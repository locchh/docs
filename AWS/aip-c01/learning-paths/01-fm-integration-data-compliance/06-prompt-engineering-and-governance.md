# Unit 06: Prompt engineering and governance

**Task 1.6: Implement prompt engineering strategies and governance for FM interactions.** Six skills sit under it:

- Build instruction frameworks that control model behaviour, with **Bedrock Prompt Management** for role definitions, **Bedrock Guardrails** for responsible-AI rules, and response templates.
- Build interactive systems that keep context, with **Step Functions** for clarification, **Amazon Comprehend** for intent and **DynamoDB** for history.
- Govern prompts, through parameterised templates and approval workflows in **Prompt Management**, **S3** repositories, **CloudTrail** and **CloudWatch Logs**.
- Assure prompt quality, with **Lambda** output checks, **Step Functions** edge-case tests and **CloudWatch** regression monitoring.
- Refine prompts beyond the basics, using structured inputs, output specifications, **chain-of-thought** and feedback loops.
- Build complex prompt systems, with **Bedrock Flows** for chains, branching, reusable components, and pre- and post-processing.

## What a good prompt contains

A prompt is a specification, and the exam treats it like one. A well-built prompt has five parts:

- A **role and instructions**: who the model is, what it must and must not do, and how to handle uncertainty.
- **Context**: retrieved passages, user data and business rules, clearly delimited.
- **Examples**, when format or judgement is subtle. That is **few-shot prompting**; **zero-shot** is for when the task is plain.
- The **user input**.
- An **output specification**: a JSON schema, XML tags or a fixed template, so downstream code can parse the result.

Separate sections with delimiters so the model does not confuse instructions with data. Put the most important constraints where the model will weigh them, which is typically the system prompt and the end of the user message.

**Chain-of-thought** prompting asks the model to reason step by step before answering. It improves accuracy on multi-step problems, such as financial calculations and eligibility rules, and it makes errors visible. Reasoning models do this internally, so the technique matters most with standard chat models.

**Structured output** is best enforced with tool use. Define a tool whose input schema is the JSON you want and require the model to call it, which is more reliable than asking for JSON in prose.

Inference parameters finish the picture: a low temperature for consistency, `maxTokens` to bound length and cost, and stop sequences to end at a marker.

Skill 1.6.5 is the iterative version of this. When responses vary in reasoning, format or completeness, do four things:

- Add structured input components, which means breaking the request into labelled fields.
- Specify the output format.
- Add **chain-of-thought** instructions.
- Feed user ratings and corrections back into prompt revisions.

Fine-tuning whenever users complain, or letting analysts pick prompts by hand, are the distractors.

## Instruction frameworks: prompts plus guardrails

Skill 1.6.1 pairs two **Bedrock** features, and questions almost always key the pair.

**Amazon Bedrock Prompt Management** stores prompts as versioned resources. A prompt holds a system message and user template with variables in double braces, such as `{{customer_tier}}`, the model to use and its inference parameters, optional prior turns, and optional tools. The same role definition and response template therefore apply everywhere the prompt is used. That is how you enforce "always respond as a formal compliance assistant with summary, references and disclaimer" across many applications without hard-coding text into each one.

**Amazon Bedrock Guardrails** enforces behaviour the prompt alone cannot guarantee, because a prompt is a request and a guardrail is a filter applied to inputs and outputs regardless of what the model was told. A guardrail combines six kinds of control:

- **Content filters** for hate, insults, sexual content, violence, misconduct and prompt-attack detection, for text and images, with configurable strengths.
- **Denied topics**: natural-language descriptions of subjects to refuse, such as investment advice or competitor products.
- **Word filters** for exact phrases and profanity.
- **Sensitive information filters** for PII types and regular expressions, either blocked or masked.
- **Contextual grounding checks**, which flag answers not supported by the retrieved source.
- **Automated reasoning checks**, which verify answers against formal policy rules.

You create versions, then attach a guardrail by ID and version in `guardrailConfig` on `Converse` or `InvokeModel`, on agents and **Knowledge Bases**. You can also call `ApplyGuardrail` on any text, including output from a **SageMaker**-hosted model.

Domain 3 covers guardrails in depth. Here the point is the division of labour: **Prompt Management** shapes what the model tries to do, and **Guardrails** bounds what it is allowed to do.

Response format templates round it out. A JSON schema in the prompt or as a tool definition gives consistent structure for downstream parsing.

## Interactive systems that keep context

Models are stateless, so the application owns the conversation. Skill 1.6.2 names three services.

**Amazon DynamoDB** stores conversation history. The partition key is the session or user ID, the sort key is the turn number or timestamp, and the messages are the items. A **time-to-live** attribute expires sessions automatically after the retention period your policy requires, ninety days for example.

Each turn, the application loads recent history, trims or summarises it to fit the context window and token budget, and sends it with the new message as role-based messages. **DynamoDB** gives single-digit-millisecond reads at any scale, which **SQS**, **Kinesis**, **Athena** over **S3** logs and in-memory maps do not.

**Amazon Comprehend custom classification** recognises user intent from natural language, such as billing, cancellation or a technical issue. That drives routing to the right prompt or workflow, and it detects when intent is missing or ambiguous. **Amazon Lex** is the alternative for slot-filling bots with fixed intents, and **Bedrock Agents** infer intent themselves, but **Comprehend** is what the task statement names.

**AWS Step Functions** orchestrates the dialogue. A **Choice state** checks the intent confidence and, below a threshold, branches to a clarification step that asks a follow-up question and waits for the answer. The wait is a **task token callback**: the workflow pauses until an external caller returns the token, then resumes. Other branches retrieve context, call the model, validate the output and escalate to a human when needed.

The combination "**Step Functions** for clarification workflows, **Comprehend** for intent, **DynamoDB** for history" is the keyed answer for vague-question scenarios.

Managed alternatives exist. **Bedrock Agents** keep session memory, and **AgentCore Memory** provides short- and long-term memory for any agent framework. Both appear in Domain 2.

## Governance of prompts

Skill 1.6.3 turns prompts into controlled artefacts, and every scenario lists the same requirements: version control, approval before production, a central repository, tracking who used what, and logs for compliance.

**Prompt Management** provides the versioning. A prompt has a draft you edit and test, **variants** you compare side by side, and **versions**, which are immutable snapshots. Applications and **Flows** reference a specific version, so promoting a prompt means publishing a version and repointing the consumer, and rollback means pointing back.

You can invoke a prompt in three ways: by passing its ARN as the `modelId` in `Converse` or `InvokeModel` and supplying `promptVariables`, through a **Flows** prompt node, or from an agent.

The **approval workflow** the exam refers to is built from these pieces. Authors edit drafts, reviewers test variants, an administrator publishes the version, and **IAM** policies decide who may create versions and who may only invoke them. Store template exports in **Amazon S3** as the durable, versioned repository and backup.

Two services carry the audit trail:

- **AWS CloudTrail** records the management events that create, update and version prompts, guardrails and flows, and it can record `RenderPrompt` and other runtime calls as data events. That answers "track who accessed or invoked each prompt and when".
- **Amazon CloudWatch Logs**, through **Bedrock** **model invocation logging**, captures the full prompt, response and metadata of every invocation, to **CloudWatch Logs** or **S3**. That is the "log prompt usage for compliance reviews" piece.

For long retention, deliver invocation logs to **S3** with **S3 Object Lock in compliance mode** set to the required period, seven years in the usual scenario, which no one, including the root user, can shorten.

The recurring distractors are **CloudTrail Lake**, which stores **CloudTrail** events and not prompt bodies, **DynamoDB** point-in-time recovery, **Lambda** environment variables, Git repositories with manual reviews, and **Secrets Manager**.

Domain 3 adds the enforcement layer. An **IAM** condition key, `bedrock:GuardrailIdentifier`, on `InvokeModel` and `Converse` permissions forces every call to carry the approved guardrail.

## Quality assurance for prompts

Skill 1.6.4 treats prompts like code with tests. Four mechanisms do the testing:

- A **Lambda** function validates each response against expected patterns: required fields present, JSON parses against the schema, mandatory disclaimers included, numbers within range, escalation triggers respected. Deviations are flagged for review.
- **Step Functions** runs a suite of edge-case prompts against a prompt version and collects the results. The edge cases are things like angry customers, vague requests, joint accounts and international transfers.
- **CloudWatch** metrics and alarms track quality KPIs over time, such as validation pass rate, latency, error rate and escalation rate, so a regression after a prompt change is detected.
- **Regression testing** compares a new prompt version with the previous one on the same golden dataset before it is promoted, and **Bedrock** model evaluation with **LLM-as-a-judge** scores the outputs at scale.

Wire the suite into CI/CD so a failing threshold blocks the release. **Amazon GuardDuty**, which is threat detection, **CodeBuild** unit tests over prompt text, and manual console review are the distractors.

## Complex prompt systems with Bedrock Flows

Skill 1.6.6 names **Amazon Bedrock Flows**, formerly **Prompt Flows**, a visual builder for multi-step generative workflows. A flow starts at an input node and ends at one or more output nodes. Between them you place nodes of several kinds:

- **Prompt nodes**, inline or from **Prompt Management**.
- **Knowledge base nodes** and **agent nodes**.
- **Lambda nodes** for custom code, and **inline code nodes** for small transformations.
- **Condition nodes** that branch on values, such as escalating only if the classifier says "damaged package".
- **Iterator and collector nodes** that loop over arrays, and a **DoWhile loop** node.
- **S3 retrieval and storage nodes**.
- An **Amazon Lex node**.

Pre-processing, such as normalising a tracking ID, and post-processing, such as adding a regulatory disclaimer or formatting the answer, are just more nodes. A prompt node is a reusable component you can drop into several flows.

You test a flow in the console, publish immutable **versions**, create **aliases** that point to a version, and invoke the alias with `InvokeFlow`, which supports streaming events, traces for debugging and multi-turn conversations. Switching a version behind an alias is the rollout and rollback mechanism, and **CloudTrail** can log `InvokeFlow` as data events.

Choosing between orchestrators is a recurring question:

- **Flows** is the answer when the requirement is sequential prompt chains, conditional branching on model output, reusable prompt components and integrated pre- and post-processing, with the least custom code.
- **Step Functions** is the answer when the workflow is broader than prompts, covering long-running tasks, human approvals, many AWS service integrations and circuit breakers, or when **Flows** is not in the options.
- **Bedrock Agents** are the answer when the model should decide which tools to call and in what order. The service is now **Agents Classic** and new work goes to **AgentCore**, but the exam still writes "**Bedrock Agents**".

**EventBridge** keyword rules, monolithic prompts, **SQS** chains and **Kafka** pipelines are not prompt systems.

## Worked scenario

A bank deploys a customer assistant that explains products, must never give investment or tax advice, must keep a professional tone, and must be auditable. Three teams write prompts for it, and after a recent prompt change the assistant started omitting required disclosures.

The instruction framework has two parts. The prompt itself carries the role, the constraints, the output format and a few examples, and is stored in **Amazon Bedrock Prompt Management** as a versioned template with variables for the customer's segment and the retrieved product facts, with inference parameters set per template. **Bedrock Guardrails** enforce what a prompt cannot: denied topics for investment and tax advice, content filters, and sensitive information masking, so the rules hold across every prompt and every team.

Conversations need state. The last turns are kept in **Amazon DynamoDB** with a **time-to-live** so history expires. **Amazon Comprehend** classifies intent, so a vague message triggers a **Step Functions** clarification step that asks a follow-up question before answering, and the assembled context is trimmed to a sliding window before each call.

Governance answers the audit question, with four pieces:

- **Prompt Management** versions, and an approval step before a version can be referenced in production.
- The template repository in **S3** with versioning.
- **AWS CloudTrail** for who changed or read what.
- **Model invocation logging** to an **S3** bucket protected by **Object Lock**, for the usage record.

Quality assurance catches the missing disclosure before deployment. A **Lambda** validator checks each response for the required fields, a **Step Functions** test suite runs edge cases against every new prompt version, and **CloudWatch** metrics on validation failures reveal regressions.

When the workflow grows to classification, retrieval, answer and a compliance post-check, **Bedrock Flows** chains the prompts with conditional branches and no orchestration code.

The exam presents this scenario in four shapes: tone-and-prohibited-topic questions (**Prompt Management** plus **Guardrails**), multi-turn context questions (**Step Functions**, **Comprehend**, **DynamoDB**), governance questions (versions, approval, **CloudTrail**, logs) and multi-step prompt questions (**Flows**).

## Exam lens

- "Professional tone, accurate product facts, never discuss competitors / prohibited topics, centrally managed across prompts" → **Prompt Management** for role definitions and templates, plus **Guardrails** for denied topics and behaviour.
- "Vague messages, ask clarifying questions, keep multi-turn context, durable history" → a **Step Functions** clarification workflow, **Comprehend** intent detection, and **DynamoDB** history with **TTL**.
- "Version control, mandatory approval, central storage, who accessed, usage logs" → **Prompt Management** with versions and approval, **S3** for the template repository, **CloudTrail** for access tracking, **CloudWatch Logs** for usage. Add invocation logging to **S3** with **Object Lock** compliance mode when a retention period, seven years, is stated.
- "Inconsistent tone, missing fields, hallucinated numbers after prompt updates; validate before deploying" → **Lambda** validators, **Step Functions** edge-case tests, **CloudWatch** regression detection.
- "Variable reasoning, inconsistent formatting, omitted metrics, improve from user feedback" → structured inputs, output specifications, **chain-of-thought**, feedback loops.
- "Reusable prompt components, conditional branching on FM output, pre- and post-processing, multi-step" → **Bedrock Flows**.
- "Version-controlled templates with per-workflow inference parameters and dynamic insertion of retrieved results, no code changes" → **Prompt Management** with variables and inference configuration per prompt.

## Knowledge check

<!-- KC: E2-Q49, E3-Q9, E1-Q24, E3-Q23, E2-Q13, E3-Q40, E1-Q63, PQ-Q6, E2-Q58, E2-Q34, E1-Q36, E2-Q17 -->
<!-- KC-BEGIN -->
### 1. Exam 2, question 49

A financial services company is building an internal compliance assistant powered by Amazon Bedrock. The assistant must always respond in a formal advisory tone, avoid providing personal financial recommendations, and consistently follow a strict response structure that includes a summary, regulatory references, and approved disclaimers. The AI engineering team also needs a mechanism to explicitly restrict discussions of prohibited investment topics while allowing the model to answer general compliance questions safely. They want a centralized way to manage these behavior rules and enforce them across multiple prompts and FM workflows.

Which solution should the team implement to ensure the model consistently follows required instructions and avoids restricted outputs?

- **A)** Hardcode the assistant’s tone and policy text into every prompt template used by the application’s API calls.
- **B)** Use Step Functions to route user messages to different prompt templates depending on the detected topic.
- **C)** Use Amazon Bedrock Prompt Management to enforce role definitions and response templates, combined with Amazon Bedrock Guardrails to block restricted financial topics and enforce responsible AI behavior.
- **D)** Use Lambda functions to inject a preset tone, disclaimers, and formatting rules before each model invocation.

<details><summary>Answer</summary>

**Answer: C.** Prompt Management enforces the advisory role, response structure and disclaimers centrally across prompts, and Bedrock Guardrails denied topics block prohibited investment discussions while content policies enforce responsible behaviour. Hardcoding text in every template, routing by topic in Step Functions, and injecting text in Lambda are neither centralised nor enforceable.

*Where this is covered: Unit 06, Instruction frameworks: prompts plus guardrails. Key: ours, confidence high.*

</details>

### 2. Exam 3, question 9

A global HR software provider is developing an internal GenAI assistant that uses Amazon Bedrock to generate policy summaries, hiring guidance, and structured HR workflows. The company wants consistent responses across departments and must ensure that the assistant always follows strict behavioral rules, such as role-specific tone, compliance-aligned phrasing, and prohibited-topic restrictions. The AI team also needs a centralized mechanism to maintain prompt templates and enforce these constraints across multiple applications built by different engineering groups.

Which solution will MOST effectively enforce consistent instructions and safe behavior across all FM interactions?

- **A)** Embed custom instructions directly into each application’s source code so that each development team maintains its own prompt formatting logic.
- **B)** Use Amazon Bedrock Prompt Management to define reusable system-prompt templates with role, formatting, and style requirements. Apply Amazon Bedrock Guardrails to enforce behavioral constraints and restricted-topic policies across all applications.
- **C)** Allow each application to generate prompts dynamically based on user input and rely on model temperature settings to control output consistency.
- **D)** Use AWS Lambda layers to store instruction text blocks and require developers to import them at runtime to standardize FM prompts.

<details><summary>Answer</summary>

**Answer: B.** Prompt Management defines reusable system-prompt templates with role, formatting and style requirements, and Guardrails enforces behavioural constraints and restricted topics across every application. Instructions in each application's code, dynamic prompts controlled by temperature, and Lambda layers of text are not centrally enforceable.

*Where this is covered: Unit 06, Instruction frameworks: prompts plus guardrails. Key: ours, confidence high.*

</details>

### 3. Exam 1, question 24

A retail analytics company is building an interactive AI assistant that helps store managers interpret sales anomalies. The assistant uses Amazon Bedrock to generate insights, but users often submit vague messages such as "Why did yesterday look weird?" The AI engineering team wants the system to automatically detect missing intent, ask clarifying follow-up questions, and keep multi-turn conversation context available for future model calls. They also need durable storage to retrieve past conversation turns during the session.

Which architecture should the team implement to meet these requirements?

- **A)** Store conversation history directly in Bedrock prompts without external storage to simplify flow management.
- **B)** Use Amazon SQS to queue each message and process them sequentially for context preservation.
- **C)** Use Lambda functions to rewrite vague questions before sending them to Amazon Bedrock.
- **D)** Use Step Functions to orchestrate clarification workflows, Amazon Comprehend to detect user intent gaps, and DynamoDB to store and retrieve conversation history for context-aware responses.

<details><summary>Answer</summary>

**Answer: D.** Step Functions orchestrates clarification loops, Comprehend detects missing or ambiguous intent, and DynamoDB durably stores conversation turns for context-aware follow-ups, the exact trio named in the task statement. Prompts alone are not durable storage, SQS is a queue not a session store, and rewriting questions in Lambda does not ask the user for clarification.

*Where this is covered: Unit 06, Interactive systems that keep context. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 4. Exam 3, question 23

A digital health platform is developing a context-aware conversational assistant that uses Amazon Bedrock to answer patient questions about wellness plans. The assistant must keep track of multi-turn conversations, recognize ambiguous user intents, and request clarification when necessary. The system must also maintain conversation history to allow the FM to provide consistent, context-rich responses during long sessions. The company wants a solution that requires minimal custom orchestration code and integrates well with downstream AI components.

Which solution will BEST meet these requirements?

- **A)** Use AWS Step Functions to build clarification and fallback workflows, Amazon Comprehend to perform intent recognition, and DynamoDB to store conversation history for context retrieval in FM prompts.
- **B)** Use an SQS FIFO queue to store incoming user messages, a Lambda function to parse session details, and Amazon RDS to store all conversation transcripts.
- **C)** Use Amazon Kinesis Data Firehose to stream user messages to S3, use Athena queries to reconstruct past interactions, and provide the historical transcript to the FM when needed.
- **D)** Use Amazon CloudWatch Logs to capture all user interactions, build context in-memory per request, and rely on the FM’s built-in reasoning to handle ambiguities without external services.

<details><summary>Answer</summary>

**Answer: A.** Step Functions builds the clarification and fallback workflows, Comprehend performs intent recognition, and DynamoDB stores conversation history for retrieval into prompts, with minimal custom orchestration code. SQS FIFO with RDS, Kinesis to S3 with Athena reconstruction, and CloudWatch Logs with in-memory context are not conversation-state designs.

*Where this is covered: Unit 06, Interactive systems that keep context. Key: ours, confidence high.*

</details>

### 5. Exam 2, question 13

A financial services company is developing a set of reusable foundation model (FM) prompts for regulatory reporting assistance. The AI governance team requires:

- Strict version control for prompt templates
- A mandatory approval workflow before updating any production prompt
- Centralized storage of all templates for auditing
- Full tracking of who accessed or invoked each prompt
- Logging of prompt usage for compliance reviews

The lead AI engineer must design a governance workflow that satisfies these controls while supporting scalable FM operations across multiple internal teams.

Which solution best meets these organizational requirements?

- **A)** Use Amazon DynamoDB to store all prompts and enable Point-in-Time Recovery (PITR) for version tracking.
- **B)** Use Amazon Bedrock Prompt Management to create parameterized templates with approval workflows, store template artifacts in Amazon S3, track template access with AWS CloudTrail, and send usage logs to Amazon CloudWatch Logs.
- **C)** Use Lambda functions to store prompts in environment variables and rely on Amazon CloudWatch for operational monitoring.
- **D)** Use AWS CodeCommit to store prompt text files and push updates through manual Git-based reviews.

<details><summary>Answer</summary>

**Answer: B.** Prompt Management supplies parameterised, versioned templates with an approval process, S3 provides the central template repository, CloudTrail tracks who accessed or invoked prompts, and CloudWatch Logs records usage, satisfying every control. DynamoDB point-in-time recovery is not version control, environment variables are not governance, and CodeCommit with manual reviews lacks the audit trail of invocations.

*Where this is covered: Unit 06, Governance of prompts. Key: ours, confidence high.*

</details>

### 6. Exam 3, question 40

A digital branding firm uses Amazon Bedrock and Amazon SageMaker AI to generate marketing copy for hundreds of ecommerce clients. The firm wants to standardize output quality using Bedrock Prompt Management by creating reusable, parameterized prompt templates that support client-specific variables such as product tone, regional phrasing, and brand guidelines. The templates must also enforce strict style rules—such as banned phrases, tone consistency, and formatting constraints—across all generated content.

For compliance, the governance team requires full versioning and a mandatory review step before any updated prompt template can be activated. The organization must also track all template changes and usage activity for audit purposes with minimal manual effort.

Which solution meets these requirements?

- **A)** Use Lambda-based preprocessing scripts to validate tone and keyword restrictions before invoking a model, maintain prompt templates in AWS Systems Manager Parameter Store with versioning, and enable CloudTrail only for model invocation events.
- **B)** Use Bedrock Guardrails to validate stylistic rules at runtime, store template definitions in Amazon S3 with object versioning enabled, and configure Amazon CloudWatch Logs to capture template access events.
- **C)** Develop prompt templates in Bedrock Prompt Management, use Amazon Comprehend to classify tone and detect restricted phrases, and configure Amazon SNS to send notifications whenever templates are updated or used.
- **D)** Configure reusable templates with client-specific parameters and versioning, enforce a mandatory approval workflow for template changes, apply Bedrock Guardrails to enforce stylistic rules, and use AWS CloudTrail to record template modifications and usage events for compliance.

<details><summary>Answer</summary>

**Answer: D.** Prompt Management templates with client-specific parameters and versioning, a mandatory approval workflow before activation, Guardrails enforcing banned phrases and style rules at runtime, and CloudTrail recording template modifications and usage meet every requirement with minimal manual effort. Parameter Store lacks approval workflows, S3 versioning with CloudWatch Logs lacks the review step, and Comprehend classification with SNS notifications is not governance.

*Where this is covered: Unit 06, Governance of prompts. Key: ours, confidence high.*

</details>

### 7. Exam 1, question 63

A global insurance provider is building an internal Amazon Bedrock–powered assistant for underwriting, claims, and customer operations. Each business division maintains its own prompt templates and requires a formal approval workflow before templates can be used in production. The company also must retain full invocation records—including prompts, parameters, and FM outputs—for at least 7 years to satisfy auditing and regulatory inquiries.

The AI engineering team wants a solution that provides built-in governance and long-term, tamper-proof logging without developing custom workflow engines, storage systems, or archival processes.

Which combination of steps will meet these requirements with MINIMAL operational overhead? (Select TWO.)

- **A)** Enable Amazon Bedrock model invocation logging to Amazon S3, and apply S3 Object Lock in compliance mode with a 7-year retention period.
- **B)** Configure AWS CloudTrail Lake to store all Bedrock events, including prompt bodies and FM responses, with custom retention settings.
- **C)** Use Amazon Bedrock Prompt Management with approval workflows and role-based access control to centrally manage, version, and approve prompt templates across divisions.
- **D)** Send Bedrock invocation events to Amazon EventBridge and archive them in Amazon Redshift tables configured with 7-year retention policies.
- **E)** Store prompt templates in AWS Secrets Manager with resource policies that require MFA for approvals and updates.

<details><summary>Answer</summary>

**Answer: A, C.** Model invocation logging to S3 captures prompts, parameters and outputs, and S3 Object Lock in compliance mode makes the seven-year retention tamper-proof; Prompt Management with versioning, approval and role-based access governs the templates centrally. CloudTrail Lake does not store prompt bodies, Redshift retention is custom archival, and Secrets Manager is not a template store.

*Where this is covered: Unit 06, Governance of prompts. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 8. Official practice question set, question 6

A financial services company needs to use Amazon Bedrock to create an AI assistant that will help customer support representatives across multiple business units. A GenAI developer must ensure that prompt templates are properly governed through approval workflows. Additionally, the company requires comprehensive logging of all model invocations with a 7-year retention period for regulatory compliance.

Which combination of steps will meet these requirements with MINIMAL operational overhead? **(Select TWO)**

- **A)** Use Amazon Bedrock Prompt Management with multi-stage approval workflows. Use IAM policies that require multi-party authorization.
- **B)** Set up Amazon EventBridge rules to capture Amazon Bedrock model invocation events. Route events to Amazon CloudWatch Logs groups that are organized by business unit. Export the logs to Amazon S3. Enable S3 Object Lock with compliance retention mode set to 7 years.
- **C)** Enable AWS CloudTrail data events for all Amazon Bedrock APIs. Deliver the logs to CloudTrail Lake with a 7-year retention setting. Tag each event with the business unit ID. Run CloudTrail Lake queries to monitor prompt activity.
- **D)** Store prompt templates in Amazon DynamoDB tables with composite keys partitioned by business units. Implement IAM policies that grant role-based access to business units for template approval. Use DynamoDB item-level permissions to control prompt template modifications and approvals.
- **E)** Enable Amazon Bedrock model invocation logging with Amazon S3 as the destination. Enable S3 Object Lock with compliance retention mode set to 7 years. Create separate prefixes for each business unit.

<details><summary>Answer</summary>

**Answer: A, E.** Prompt Management with multi-stage approval and IAM multi-party authorization governs the templates, and model invocation logging to S3 with Object Lock compliance mode set to seven years gives comprehensive, tamper-proof invocation records with per-unit prefixes. EventBridge does not capture invocation payloads, CloudTrail records API calls without prompt bodies, and DynamoDB templates need custom approval logic.

*Where this is covered: Unit 06, Governance of prompts. Key: AWS official answer.*

</details>

### 9. Exam 2, question 58

A retail analytics startup uses an Amazon Bedrock foundation model to generate weekly market-insight summaries for its clients. After several prompt updates, the team notices inconsistent tone, missing numerical breakdowns, and occasional hallucinated recommendations. The lead AI engineer must implement an automated quality assurance workflow that validates expected structure, checks edge-case responses, and monitors for prompt regressions before new versions are deployed to production.

Which approach should the engineer implement to ensure reliable and consistent prompt behavior?

- **A)** Use CodeBuild with a scheduled pipeline that runs unit tests against the prompt text stored in an S3 bucket.
- **B)** Enable Amazon GuardDuty to scan all prompt output for anomalies and escalate findings to the security team.
- **C)** Store sample prompts in DynamoDB and manually review generated outputs from the model console before each deployment.
- **D)** Build a QA workflow using Lambda functions to validate expected output fields, Step Functions to orchestrate edge-case prompt tests, and Amazon CloudWatch Logs to detect regression patterns across prompt versions.

<details><summary>Answer</summary>

**Answer: D.** Lambda functions validate expected output fields, Step Functions orchestrates edge-case prompt tests, and CloudWatch Logs detects regression patterns across prompt versions, which is the QA system in skill 1.6.4. CodeBuild unit tests on prompt text do not test model behaviour, GuardDuty is a threat detector, and manual console review does not scale or automate.

*Where this is covered: Unit 06, Quality assurance for prompts. Key: ours, confidence high.*

</details>

### 10. Exam 2, question 34

A financial-services firm is building an Amazon Bedrock–powered insights assistant that summarizes analyst notes and recommends follow-up actions. Early testing shows frequent variability in reasoning steps, inconsistent output formatting, and occasional omission of required financial metrics. The lead GenAI engineer must refine the system so the FM consistently follows the expected reasoning flow, emits structured outputs, and improves over time using user-generated feedback.

Which approach should the engineer implement to enhance FM response quality?

- **A)** Enable JSON mode and rely solely on temperature reduction to enforce consistent response formatting.
- **B)** Create multiple independent prompts for each department and allow analysts to manually choose which prompt to run for each query.
- **C)** Use structured input components and output specification templates, reinforce reasoning with chain-of-thought instruction patterns, and incorporate a feedback loop that adjusts prompt parameters based on real-world user ratings.
- **D)** Periodically fine-tune a custom model whenever users report inconsistent results, without modifying the prompting strategy.

<details><summary>Answer</summary>

**Answer: C.** Structured input components, output specification templates, chain-of-thought instruction patterns and a feedback loop from user ratings are the prompt-refinement techniques for inconsistent reasoning, formatting and omissions. JSON mode with temperature alone does not fix reasoning, manual prompt selection by analysts is not systematic, and fine-tuning on complaints without changing the prompting strategy is slow and expensive.

*Where this is covered: Unit 06, What a good prompt contains. Key: ours, confidence high.*

</details>

### 11. Exam 1, question 36

A logistics company is developing a generative AI assistant using Amazon Bedrock to automate shipment issue resolution. Each user request may require multiple reasoning steps: identifying the type of problem, checking shipment history, generating a proposed resolution, and escalating complex cases. The engineering team wants a prompt system that supports reusable prompt components, conditional branching based on FM responses (for example, escalate only if the FM detects "damaged package"), and multi-step processing that includes pre-processing of tracking IDs and post-processing of final recommendations.

Which approach should the engineering team implement?

- **A)** Use Amazon EventBridge rules to route user queries to different prompt templates based solely on keyword matches.
- **B)** Build multiple standalone prompts triggered by separate API endpoints, with logic handled manually by the client application.
- **C)** Use Amazon Bedrock Prompt Flows to orchestrate sequential prompt chains with conditional branches, integrate reusable prompt modules, and include pre- and post-processing steps within the workflow.
- **D)** Create a single extremely detailed monolithic prompt that embeds all possible instructions and relies on the FM to infer when to escalate or continue.

<details><summary>Answer</summary>

**Answer: C.** Bedrock Flows is built for sequential prompt chains with condition nodes that branch on model output, reusable prompt nodes, and Lambda or inline code nodes for pre- and post-processing. EventBridge keyword rules, client-side logic across standalone prompts, and one monolithic prompt cannot express conditional multi-step processing.

*Where this is covered: Unit 06, Complex prompt systems with Bedrock Flows. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 12. Exam 2, question 17

A regional healthcare consortium is building a clinical reasoning assistant that retrieves evidence from internal policy manuals using Amazon Kendra and generates patient-safe explanations with a foundation model in Amazon Bedrock. The system supports multiple care pathways (diabetes, heart disease, oncology), each requiring standardized, reusable prompt templates and adjustable inference parameters such as temperature, top_p, and max_tokens.

The clinical engineering team needs a solution that enforces version control for prompt templates, supports dynamic insertion of retrieved Kendra results, and allows different parameter settings per workflow without modifying application code.

Which solution best satisfies these requirements?

- **A)** Embed prompt templates inside an AWS Lambda function, storing multiple versions in environment variables so that changes only require updating Lambda configuration instead of redeploying.
- **B)** Implement a multi-step Bedrock Prompt Flows pipeline that chains search, reasoning, and summarization prompts, and manually track prompt versions in an external Git repository.
- **C)** Use Bedrock Prompt Management to store reusable, version-controlled prompt templates, define inference parameters within each prompt configuration, and invoke templates via the InvokeModel API after embedding Kendra search results.
- **D)** Save prompt files to an Amazon S3 bucket and load them dynamically in the inference Lambda function, then submit each prompt to CreateModelCustomizationJob to maintain reusability.

<details><summary>Answer</summary>

**Answer: C.** Prompt Management stores reusable, version-controlled templates with variables for the retrieved Kendra results and per-prompt inference parameters such as temperature and max tokens, so each care pathway gets its own settings without application changes. Lambda environment variables are not version control, tracking versions in Git outside Flows is manual, and CreateModelCustomizationJob is fine-tuning, not prompt reuse.

*Where this is covered: Unit 06, Governance of prompts. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

A prompt is a specification: role, instructions, delimited context, examples, the user's input and an output schema, tuned with **chain-of-thought** and low temperature where consistency matters.

**Prompt Management** holds the templates with variables, models, parameters, variants and immutable versions. **Guardrails** bounds behaviour with content filters, denied topics, word and PII filters, contextual grounding and automated reasoning, applied through `guardrailConfig` or `ApplyGuardrail`.

Conversations live in **DynamoDB** with **TTL**, intents come from **Comprehend** custom classification, and **Step Functions** runs clarification and escalation.

Govern with versions and **IAM**-controlled publishing, **S3** as the repository, **CloudTrail** for who and when, invocation logging to **CloudWatch Logs** or **S3** for what, and **Object Lock** for retention. Test prompts with **Lambda** validators, **Step Functions** edge-case suites, golden-dataset regression and **CloudWatch** alarms.

Chain prompts with **Bedrock Flows**, using prompt, knowledge base, agent, **Lambda**, condition and iterator nodes, plus versions and aliases, when the problem is a multi-step prompt system.
