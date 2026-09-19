# Unit 05: Application patterns and developer tools

**Task 2.5: Implement application integration patterns and development tools.** This unit is about making GenAI applications usable and maintainable: APIs shaped for streaming and token limits, interfaces built with **Amplify**, **OpenAPI** and **Bedrock Flows**, the managed services that enhance business systems (**Q Business**, **Bedrock Data Automation**, **Kendra**, **Personalize**), **Amazon Q Developer** for productivity, agent and prompt-chaining patterns, and the troubleshooting trio of **Logs Insights**, **X-Ray** and **Q Developer**.

This unit gathers the "how do we make this usable and maintainable" questions. Several skills overlap earlier units; where they do, this unit adds the developer-facing detail and points back.

## APIs shaped for GenAI workloads

GenAI APIs differ from ordinary REST endpoints in three ways, and skill 2.5.1 wants each handled at the API layer rather than in every client.

**Responses stream.** Choose **API Gateway WebSocket APIs** for bidirectional real-time delivery and long generations. For one-way streams, use **Lambda response streaming** or **server-sent events**. Set **idle timeouts** and **keep-alive pings** to suit long generations; unit 04 has the mechanics.

**Tokens are the unit of cost and capacity.** Manage them deliberately at each stage:

- Count tokens before sending. Use the **Bedrock CountTokens API** for supported models or the model's tokenizer library.
- Cap `maxTokens` to limit generation.
- Trim or summarize conversation history to a **sliding window**.
- Compress long context.
- Validate prompt size in an **API Gateway request validator**, so oversized prompts are rejected before they cost anything.

**Models time out and throttle.** Layer the timeouts from the client through **API Gateway** and **Lambda** to the model call. Each timeout should be shorter than the one outside it.

**Retry** model timeouts and throttles with **exponential backoff and jitter**. After repeated failures, open a **circuit breaker**. Give clients progress indicators for long requests, and add content-filtering middleware through **guardrails** on input and output at the same API layer.

## Interfaces people can actually use

Skill 2.5.2 is about adoption. Three AWS pieces appear together in questions.

**AWS Amplify** builds and hosts web and mobile front ends. It generates declarative, accessible UI components wired to AWS back ends, including **Bedrock** through its AI capabilities. **Cognito** provides authentication, while skeleton states show that a model is generating and built-in error handling covers failures. This is the fastest route to a clinician-friendly or analyst-friendly interface without a custom **React** codebase.

**OpenAPI specifications** describe your FM endpoints. They define parameters, example requests and response schemas, including token usage and error cases. Publishing the specification is the heart of **API-first development**, because the same contract serves several purposes:

- Other teams integrate against it.
- **API Gateway** can import it to create the API.
- Client SDKs can be generated from it.

**Amazon Bedrock Flows**, still called **Prompt Flows** in the exam guide, is a visual, no-code builder. Non-technical users assemble prompts, **knowledge bases**, **agents**, **Lambda functions** and conditions into a workflow. An application then invokes that workflow by **alias**, as covered in Domain 1 unit 06.

"Non-technical clinicians create summaries without learning prompts, **API-first** for later integration, minimal front-end code" is answered by **Amplify** plus **OpenAPI** plus **Bedrock Flows**. **AppSync** auto-generating a UI, a hand-built **React** app on **S3**, or a Flask app on **EC2** are the distractors.

Two more managed interfaces show up. **Amazon Q Business** is a fully managed enterprise assistant that answers employees from connected data sources. It includes citations and respects their permissions. The service is in maintenance mode and closed to new customers since 31 July 2026, with **Amazon Quick** as AWS's successor, though the exam still names **Q Business**.

**Amazon Lex** is the conversational bot service, built around **intents**, **slots** and **slot types**. When users say "food spots" instead of "local dining", add **synonyms** to custom slot values. This is the quick fix when you cannot change **Lambda** code or the intent structure.

## Enhancing business systems

Skill 2.5.3 lists four patterns and questions combine them.

**Lambda for CRM enhancements.** Use a **serverless**, event-driven sequence:

1. Trigger a function on CRM events through **EventBridge** or a **webhook**.
2. Pull the interaction notes.
3. Call **Bedrock** to draft a personalized follow-up or classify sentiment.
4. Write the result back to the customer record.

This avoids polling scripts on **EC2**.

**Step Functions for document processing.** Represent ingestion, validation, classification, extraction, generation and downstream updates as states. Use **parallel branches** to process document sections. Add **validation checkpoints**, **retries** and **human review** steps where confidence is low.

**Bedrock Data Automation** handles the extraction and classification stage. Its capabilities include:

- **Standard output**, such as summaries and transcripts.
- **Custom output** from **blueprints**, with one **blueprint** per document type.
- **Document splitting** for multi-document PDFs.
- Integration with **Knowledge Bases**, covered in Domain 1 unit 03.

**Amazon Q Business** provides internal knowledge tools. Set up the application in this order:

1. Create a **Q Business application**.
2. Add **data source connectors** for **SharePoint**, **Confluence**, **Salesforce**, **S3**, **Jira**, **ServiceNow** or dozens of other sources. The connectors sync content and its **access control lists** on a schedule.
3. Authenticate users through **IAM Identity Center** or **IAM federation**.

**Q Business** then answers with citations only from documents the user is allowed to see. **Plugins** let it take actions in other applications, while **Q Apps** let employees build small apps from prompts.

When a question wants a secure, permission-aware assistant over internal repositories with the least operational overhead, choose **Q Business connectors** plus **IAM Identity Center**. A custom proxy, custom tagging rules, or **API Gateway** with **Lambda** validators requires a different approach.

**Q Business** itself has been closed to new customers since 31 July 2026. AWS points new work at **Amazon Quick**, which offers the same connectors-plus-permissions model, but exam questions and their keys still say **Q Business**.

**Human review** for uncertain extractions uses **Amazon Augmented AI (A2I)**. When **Textract** or **Rekognition** confidence falls below a threshold, the item goes to a **human review workflow**. High-confidence items pass straight through.

**A2I** is closed to new customers but remains the keyed answer where it appears. In a new design, a **Step Functions** review step plays the same role.

**Retrieval and ranking services.** **Amazon Kendra** is the managed enterprise search service. Its **GenAI index** can serve as the retriever behind a **Bedrock Knowledge Base**. Documents indexed through **Kendra** carry **metadata attributes**, such as department, product line and intent tags, that a **Knowledge Base** can filter and rank on.

**Amazon Personalize** is the managed recommendation service. It learns from user interaction data and ranks a list of items for a given user.

When a question wants retrieval, per-customer ranking and generation "in one flow" rather than separate pipelines, use this sequence:

1. A **Knowledge Base** uses **hybrid search** over **Kendra**-enriched documents.
2. **Personalize** ranks the retrieved items for the user.
3. The FM generates the response.

**Kendra** is closed to new customers, but it remains exam vocabulary.

The archetype question, "compliance needs document enrichment, customer service needs a secure knowledge assistant, engineering needs validated upload → classification → CRM update", is answered by **Step Functions** orchestrating **Bedrock Data Automation** for enrichment and classification, with **Amazon Q Business** connected to internal sources for the assistant.

## Developer productivity with Amazon Q Developer

**Amazon Q Developer** is AWS's generative AI assistant for developers and operators. In the IDE, including **VS Code**, **JetBrains** and **Eclipse**, and at the command line, it can:

- Chat about code and give inline completions.
- Generate code, including **AWS SDK** calls for **Bedrock**.
- Refactor code and use its **transformation** capability for language and framework upgrades.
- Scan for security vulnerabilities.
- Run agentic tasks: implement a feature across files, generate unit tests, review code for quality and security, or write documentation.

In the **AWS Management Console**, it answers questions about services, explains errors and helps troubleshoot resources. It is also available in **Slack** and **Microsoft Teams**. **Free** and **Pro** tiers exist; **Pro** adds organizational customization and administration.

For the exam, **Q Developer** is the answer to "developers struggle to write correct **Bedrock** SDK code, need consistent test patterns, safe refactoring across services, and recommendations to optimise API usage". The keyed combination is to let it generate and refactor integration code with API guidance and optimization suggestions, and to integrate its test generation into **CI/CD pipelines**.

The distractors are:

- Pre-commit hooks that block API misuse.
- **Lambda Powertools** templates with manual review. **Powertools** is the AWS utility library for logging, tracing and metrics in **Lambda functions**.
- Monolith rewrites.
- Reserving optimization for periodic manual cycles.

AWS has announced end of support for the **Q Developer IDE plugins** in April 2027 in favor of **Kiro**, AWS's agentic IDE. The exam still uses the **Q Developer** name.

## Advanced application patterns

Skill 2.5.5 restates the agent material from unit 01 in application terms. Match each framework or service to its role:

- **Strands Agents** builds individual agents with tools and memory.
- **Agent Squad** orchestrates specialized agents with a **classifier** and **supervisor**.
- **Step Functions** orchestrates agent handoffs, with validation between steps and recovery when an agent fails.

The recurring example passes work from an extraction agent to a compliance agent and then to a decision agent. **Step Functions** invokes **Bedrock** for each agent step and passes structured outputs along. With retries, branching and execution traces, this is a **prompt chaining** pattern.

When the chain is prompts rather than agents, **Bedrock Flows** or **Converse**-based chaining does the same job. Between steps, keep context within token limits by compressing it, summarizing it, or passing only what the next step needs.

Combine declarative workflows in **Step Functions** with event processing in **EventBridge** for agents that **react** to changing conditions. A single **Lambda** with conditional logic, **SQS** ordering with **DynamoDB Streams**, and **custom orchestration** on **EC2** are the distractors.

## Troubleshooting FM applications

Skill 2.5.6 previews Domain 5. Give each troubleshooting tool a distinct job:

- **CloudWatch Logs Insights** finds problematic prompt-response pairs. Enable **Bedrock model invocation logging** to **CloudWatch Logs**, then query for high latency, errors, unexpected token counts or malformed outputs.
- **AWS X-Ray** shows where time and failures occur across microservices. Instrument the stack to trace requests from **API Gateway** through **Lambda**, retrieval and the **Bedrock** call, with **annotations** for model and token counts.
- **Amazon Q Developer** analyzes logs in the console, recognizes GenAI-specific error patterns and suggests fixes. Examples include context-length errors and content-policy rejections.

Add **synthetic monitoring** with **CloudWatch Synthetics canaries** that send representative prompts on a schedule. A **central prompt registry** lets you tie a regression to a prompt version.

**CloudWatch Logs Insights** plus **X-Ray** plus **Q Developer** is the keyed trio for "correlate logs across components, trace cross-service calls, detect GenAI-specific error signatures without custom ML".

## Worked scenario

A healthcare provider wants three things at once: clinicians who cannot write prompts must produce visit summaries through a simple interface, the compliance team needs documents enriched and routed into the records system, and a growing engineering team must ship reliable **Bedrock** code faster.

The clinician interface is built **API-first**. An **OpenAPI** specification describes the summarisation endpoint (parameters, token usage in the response, error cases) and is imported into **API Gateway**; **AWS Amplify** generates the accessible front end, with **Cognito** authentication and skeleton states while the model streams; and **Amazon Bedrock Flows** lets a clinical informatics lead assemble the prompt chain (classify the note, retrieve guidelines, summarise, check disclosures) visually and publish it by alias, with no front-end code for each change. The API layer streams responses over a **WebSocket**, caps tokens, layers timeouts and retries model timeouts with backoff, and applies **guardrails** on input and output.

Document enrichment runs as a **Step Functions** workflow: uploaded referrals are validated, classified and extracted by **Bedrock Data Automation** with a **blueprint** per document type, low-confidence extractions pause for human review, and the results update the records system through a **Lambda** step. For internal knowledge the exam names **Amazon Q Business** with connectors to the intranet and SharePoint and **IAM Identity Center** for permission-aware answers; a new build would use **Amazon Quick**, but the pattern is the same. Search and ranking use **Kendra** as a **Knowledge Base** retriever and **Personalize** where per-clinician ranking matters.

Engineering adopts **Amazon Q Developer** in the IDE and the pipeline: it generates and refactors **Bedrock** SDK code, proposes tests that CI runs, flags defects and suggests optimisations, and in the console helps read errors. Multi-step automation uses **Strands Agents** for individual agents and **Step Functions** for **prompt chaining** with validation between steps. When something breaks, **CloudWatch Logs Insights** over **invocation logs**, **X-Ray** traces across the microservices and **Q Developer**'s log analysis form the troubleshooting trio. The exam asks for exactly this bundle: **Amplify** plus **OpenAPI** plus Flows for the interface, **Step Functions** plus **BDA** plus **Q Business** for the business systems, **Q Developer** for productivity, and **Logs Insights** plus **X-Ray** plus **Q Developer** for diagnosis.

## Exam lens

- "Non-technical users, simple interface, **API-first**, visual prompt orchestration, minimal front-end code" → **Amplify UI**, an **OpenAPI** spec, **Bedrock Flows**.
- "Developers need correct SDK code, consistent tests, safe refactoring, optimisation suggestions" → **Amazon Q Developer** generating and refactoring code and generating tests in CI/CD.
- "Document enrichment plus internal knowledge assistant plus validated document workflow into the CRM" → **Step Functions** with **Bedrock Data Automation** and **Amazon Q Business**.
- "Low-confidence **Textract** fields to humans, high-confidence straight through" → **Amazon A2I**.
- "Extraction agent, compliance agent, decision agent with retries, branching, traces" → **Step Functions** orchestrating **Bedrock** steps with **prompt chaining**.
- "**Lex** bot misses phrases like 'pamper session', no **Lambda** or intent changes" → **slot type** **synonyms**.
- "Correlate logs, trace cross-service calls, detect GenAI error signatures" → **CloudWatch Logs Insights**, **X-Ray**, **Amazon Q Developer**.
- "**Kendra** retrieval plus **Personalize** ranking plus **Bedrock** generation in one flow" → a **Knowledge Base** with **hybrid search** enriched with **Kendra** metadata, **Personalize** to rank, then the LLM.

## Knowledge check

<!-- KC: E2-Q14, E3-Q48, E2-Q7, PQ-Q4, E2-Q19, E3-Q25, E2-Q46, E2-Q43, E3-Q65 -->
<!-- KC-BEGIN -->
### 1. Exam 2, question 14

A healthcare startup is building an internal clinical summarization tool powered by Amazon Bedrock. The product team wants a simple, accessible interface so non-technical clinicians can generate summaries without learning complex prompt formats. The engineering team also wants to adopt an API-first development approach to ensure the tool can later integrate with other hospital systems. They prefer minimal custom frontend coding but require a way to visually orchestrate prompt logic before embedding it into applications.

Which solution BEST satisfies these requirements?

- **A)** Use AWS Amplify to build a declarative UI for clinicians, define the FM interaction contract using an OpenAPI specification, and use Amazon Bedrock Prompt Flows to visually design and manage the summarization workflow.
- **B)** Use AppSync to automatically generate a GraphQL UI and embed Bedrock model calls directly into the resolvers.
- **C)** Build a custom React frontend hosted on Amazon S3 and manually code all prompt orchestration logic within the browser application.
- **D)** Deploy an EC2-hosted Flask application that exposes Bedrock inference endpoints and handles all UI development using custom HTML templates.

<details><summary>Answer</summary>

**Answer: A.** Amplify supplies a declarative UI for clinicians with minimal front-end code, an OpenAPI specification defines the FM interaction contract for API-first integration with hospital systems, and Bedrock Prompt Flows lets the team visually orchestrate the summarisation logic before embedding it. AppSync does not auto-generate a UI, a custom React app with browser-side orchestration is heavy custom code, and a Flask app on EC2 is unmanaged.

*Where this is covered: Unit 05, Interfaces people can actually use. Key: ours, confidence high.*

</details>

### 2. Exam 3, question 48

A healthcare analytics company is building a GenAI assistant that allows clinicians to summarize patient case files, generate follow-up recommendations, and interact with medical knowledge bases. The system uses Amazon Bedrock FMs for generation and Amazon API Gateway for backend access. The company wants to accelerate adoption across multiple internal teams, many of which have minimal experience integrating with FM-based APIs.

The solution must provide an easy interface for developers, support API-first integration, and enable non-technical teams to create simple GenAI workflows without writing custom code.

Which solution will BEST meet these requirements?

- **A)** Build custom React components for each FM interaction, distribute them internally, and require all teams to manually integrate with Bedrock using AWS SDK calls.
- **B)** Use AWS Amplify to generate declarative UI components that interact with Bedrock APIs, publish an OpenAPI specification for the FM endpoints, and provide Bedrock Prompt Flows so non-technical users can assemble no-code GenAI workflows.
- **C)** Use Amazon SageMaker Studio to build and publish notebooks that demonstrate FM usage. Require teams to copy notebook examples into their own applications for integration.
- **D)** Deploy a Lambda-backed API Gateway endpoint that abstracts FM calls, and require all internal teams to write their own middleware to integrate with the Lambda function.

<details><summary>Answer</summary>

**Answer: B.** Amplify generates declarative UI components that call the Bedrock-backed APIs, an OpenAPI specification enables API-first integration for developer teams, and Bedrock Prompt Flows lets non-technical teams assemble GenAI workflows without code. Custom React components with SDK calls, copied SageMaker notebooks, and a Lambda-backed endpoint that every team wraps with its own middleware all require custom development.

*Where this is covered: Unit 05, Interfaces people can actually use. Key: ours, confidence high.*

</details>

### 3. Exam 2, question 7

A software engineering team at a logistics company is building a set of GenAI-powered microservices that integrate with Amazon Bedrock for text classification and summarization. Developers frequently struggle with generating correct AWS SDK code for Bedrock API calls, maintaining consistent testing patterns for model prompts, and performing safe refactoring across multiple Lambda-based services. The team also wants automated recommendations to optimize prompt performance and API usage.

Which solution MOST effectively improves developer productivity while maintaining code quality?

- **A)** Replace the existing microservices with a monolithic containerized application on Amazon ECS and manually implement a unified prompt-testing framework.
- **B)** Use AWS CodeCommit pre-commit hooks to block incorrect API usage and rely on CloudWatch dashboards to manually inspect prompt performance.
- **C)** Use AWS Lambda Powertools to generate code templates for developers and rely on manual code reviews to ensure Bedrock API correctness.
- **D)** Use Amazon Q Developer to generate and refactor Bedrock API integration code, provide inline code suggestions for AWS SDK usage, and assist in building automated test cases for GenAI components.

<details><summary>Answer</summary>

**Answer: D.** Amazon Q Developer generates and refactors Bedrock API integration code, provides inline AWS SDK suggestions, and helps build automated tests for GenAI components, which addresses SDK correctness, consistent testing and safe refactoring directly. A monolith rewrite, pre-commit hooks with manual dashboard inspection, and Powertools templates with manual reviews do not improve productivity while keeping quality.

*Where this is covered: Unit 05, Developer productivity with Amazon Q Developer. Key: ours, confidence high.*

</details>

### 4. Official practice question set, question 4

A cross-functional team is developing a generative AI (GenAI) application by using AWS services. The team needs to optimize developer productivity and enforce consistent integration patterns. The team needs to automate performance tuning and accelerate AI testing across multiple business units.

The team wants to use Amazon Q Developer. The team must accelerate development workflows and maintain application quality.

Which combination of steps will meet these requirements? **(Select TWO)**

- **A)** Integrate the Amazon Q Developer automated unit and integration test generation features into the team's CI/CD pipelines.
- **B)** Configure Amazon Q Developer to automatically generate and refactor integration code snippets, provide targeted API usage guidance, and suggest performance optimizations for AI components. Apply the changes across the modular code base.
- **C)** Incorporate Amazon Q Developer to resolve coding issues that are identified during merge requests. Reserve most refactoring and optimization tasks for periodic manual review cycles.
- **D)** Use Amazon Q Developer to retrospectively analyze and document common integration patterns that are found across different business units' code bases.
- **E)** Use Amazon Q Developer to analyze code for security best practices and suggest compliance improvements. Implement a mandatory review process where all code changes must be manually approved by security teams before integration.

<details><summary>Answer</summary>

**Answer: A, B.** Integrating Amazon Q Developer's automated unit and integration test generation into CI/CD pipelines accelerates testing, and configuring it to generate and refactor integration code with API guidance and performance suggestions enforces consistent patterns and tuning across the codebase. Reserving refactoring for manual cycles, only documenting patterns retrospectively, and mandatory manual security approvals slow development rather than accelerate it.

*Where this is covered: Unit 05, Developer productivity with Amazon Q Developer. Key: AWS official answer.*

</details>

### 5. Exam 2, question 19

A financial services firm wants to enhance its internal operations by introducing AI-powered automation across several existing business systems. The compliance team needs automated document enrichment for onboarding forms, while the customer service department wants a knowledge assistant that can search internal policies without exposing data externally. The engineering team also needs a workflow that automatically validates uploaded documents, sends them through an AI classification step, and updates the company’s CRM with finalized metadata.

Which architecture BEST satisfies all requirements?

- **A)** Build a custom EC2-based application that performs AI classification, writes enriched documents to the CRM, and exposes a REST endpoint for customer service queries.
- **B)** Use AWS Step Functions to orchestrate a multi-step AI document workflow, integrate Amazon Bedrock Data Automation for enrichment and classification, and connect Amazon Q Business to internal data sources to provide a secure knowledge assistant for customer service teams.
- **C)** Use a single Lambda function that handles all document processing, integrates directly with Bedrock models, and stores the results in the CRM.
- **D)** Create a Bedrock Agent with internet-enabled knowledge connectors and call it directly from the CRM for document processing and customer service queries.

<details><summary>Answer</summary>

**Answer: B.** Step Functions orchestrates the validate, classify and update-CRM document workflow, Bedrock Data Automation performs enrichment and classification, and Amazon Q Business connected to internal data sources gives customer service a secure knowledge assistant, covering all three teams with managed services. A custom EC2 application and a single Lambda function are unmanaged monoliths, and an internet-enabled Bedrock agent called from the CRM exposes data and mismatches the requirements.

*Where this is covered: Unit 05, Enhancing business systems. Key: ours, confidence high.*

</details>

### 6. Exam 3, question 25

A global technology firm is expanding its internal generative-AI ecosystem by integrating services such as Amazon Comprehend for document classification and Amazon Kendra for semantic enterprise search. As part of its modernization initiative, the firm is deploying Amazon Q Business to surface insights from architecture repositories, operational runbooks, and engineering knowledge bases.

The environment must strictly enforce the company's existing enterprise role-based access controls (RBAC) so that only authorized users can view sensitive technical content. The firm also wants to minimize operational overhead and avoid maintaining custom ingestion or identity workflows.

Which of the following will satisfy these requirements with the LEAST operational overhead? (Select TWO.)

- **A)** Deploy a custom identity proxy that uses Amazon Cognito to issue temporary access tokens and implements its own RBAC validation logic.
- **B)** Use Amazon Q Business with scheduled reindexing jobs that pull content from all repositories and enforce access restrictions by applying document-level tagging rules during each synchronization cycle.
- **C)** Set up a Q Business with data source connectors for the technical knowledge repositories and design repositories. Integrate authentication and RBAC using AWS IAM Identity Center.
- **D)** Deploy Q Business data sources with automatic synchronization enabled and map enterprise access groups directly to data-source permissions.
- **E)** Place Amazon Q Business behind Amazon API Gateway endpoints and implement SAML-based SSO using AWS IAM Identity Center, with AWS Lambda functions performing request-validation checks before allowing queries to reach the Q Business application.

<details><summary>Answer</summary>

**Answer: C, D.** Amazon Q Business data source connectors index the knowledge and design repositories, IAM Identity Center provides authentication and enterprise RBAC, and connector synchronisation carries document permissions so enterprise access groups map onto what each user may see, all managed. A custom Cognito proxy with its own RBAC, scheduled reindexing with tagging rules, and API Gateway with Lambda validators add custom identity and ingestion work the question excludes.

*Where this is covered: Unit 05, Enhancing business systems. Key: ours, confidence medium.*

</details>

### 7. Exam 2, question 46

A national mortgage lender processes large volumes of scanned loan packets, health disclosures, and insurance attachments each day. Amazon Textract extracts the text, and Amazon Comprehend classifies financial entities such as loan numbers, debt ratios, and income indicators. Some documents contain handwritten notes, inconsistent formatting, and low-quality scans, leading to low-confidence predictions that frequently break downstream verification pipelines. Human analysts must manually review these cases, slowing loan approvals and increasing operational cost.

The lender wants to reduce manual review while maintaining strict accuracy requirements for regulated financial records. The solution must automatically route only uncertain predictions to human reviewers and allow high-confidence extractions to pass through validation without human intervention. The company wants a scalable, managed workflow with minimal custom code.

Which approach will most effectively optimize document-processing throughput while maintaining accuracy?

- **A)** Configure Amazon Textract to send low-confidence fields to Amazon Augmented AI (A2I) so reviewers can validate the extracted content before downstream validation.
- **B)** Reprocess low-confidence extractions with a Bedrock Claude model to predict corrected values, then send results to humans for final review.
- **C)** Use Textract to flag uncertain text, then send documents to SageMaker Ground Truth for a full labeling job before validation.
- **D)** Use an Amazon Titan model to predict and auto-correct low-confidence fields, eliminating human review entirely.

<details><summary>Answer</summary>

**Answer: A.** Amazon Augmented AI integrates with Textract so only low-confidence fields are routed to human reviewers while high-confidence extractions pass straight to validation, which is a managed workflow with minimal custom code. Sending results to a Claude model then to humans still reviews everything, a full Ground Truth labelling job is not a review workflow, and eliminating human review violates the accuracy requirement. A2I is now closed to new customers, but it remains the keyed answer where it appears.

*Where this is covered: Unit 05, Enhancing business systems. Key: ours, confidence high.*

</details>

### 8. Exam 2, question 43

A financial services company is building a multi-agent GenAI workflow that automates regulatory document reviews. The solution requires an “extraction agent” to summarize new documents, a “compliance agent” to classify risk levels, and a “decision agent” that determines escalation. Each agent uses separate Amazon Bedrock prompts and must pass structured results to the next stage. The orchestration must support retries, branching logic, and detailed execution traces for debugging.

Which architecture BEST supports this multi-agent orchestration pattern?

- **A)** Use a single Lambda function that contains conditional logic to call each Bedrock agent sequentially and logs execution results to CloudWatch Logs.
- **B)** Use Amazon SQS to trigger Bedrock requests in order and rely on DynamoDB streams to store intermediate responses for each agent.
- **C)** Use AWS Step Functions to orchestrate the multi-agent workflow, invoking Amazon Bedrock for each agent step and passing structured outputs between agents to implement prompt chaining patterns.
- **D)** Host the agent logic on Amazon EC2 instances and manually implement a custom orchestration framework to route prompts between agents.

<details><summary>Answer</summary>

**Answer: C.** Step Functions orchestrates the extraction, compliance and decision agents as sequential Bedrock invocations, passes structured outputs between them in a prompt chaining pattern, and provides retries, branching and detailed execution traces natively. A single Lambda with conditional logic, SQS with DynamoDB Streams, and a custom orchestration framework on EC2 lack managed retries, branching and traceability.

*Where this is covered: Unit 05, Advanced application patterns. Key: ours, confidence high.*

</details>

### 9. Exam 3, question 65

A global hospitality company is enhancing its Amazon Lex–based concierge assistant that helps customers request services such as “spa,” “guided tours,” and “local dining.” The Lex bot uses a Lambda function to query an Amazon DynamoDB table for package options based on the detected category.

During validation, the Generative AI Developer notices that user phrases such as “pamper session,” “food spots,” and “city walk” are not being matched, even though these map to existing service categories. The company plans to explore Amazon Titan embeddings later, but it needs a quick fix without modifying Lambda code, the DynamoDB schema, or intent structures.

Which action should the developer take to improve recognition of these user inputs?

- **A)** Define the unrecognized words as synonyms linked to the correct enumeration values in the custom slot type.
- **B)** Add runtime hints to the slot values so Lex can resolve similar user inputs more effectively.
- **C)** Expand the slot enumeration list by manually adding each of the unrecognized words as separate values.
- **D)** Create additional intents that include the new phrases as sample utterances for improved matching.

<details><summary>Answer</summary>

**Answer: A.** Defining the unrecognised phrases as synonyms of the existing slot values in the custom slot type makes Lex resolve 'pamper session' to the spa value without changing Lambda code, the DynamoDB schema or the intents. Runtime hints and new enumeration values change what the Lambda receives, and new intents alter the intent structure.

*Where this is covered: Unit 05, Interfaces people can actually use. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

Shape FM APIs for streaming, token **budgets** and timeouts at the API layer. Make GenAI usable with **Amplify** front ends, **OpenAPI** contracts, **Bedrock Flows** for no-code workflows, **Q Business** for permission-aware internal assistants, and **Lex** slot **synonyms** for conversational bots. Enhance business systems with event-driven **Lambda** enrichment, **Step Functions** document workflows, **Bedrock Data Automation** extraction and **A2I** review.

Speed developers up with **Amazon Q Developer** for generation, refactoring, tests and security scans. Build advanced applications with **Strands Agents**, **Agent Squad** and **Step Functions** **prompt chaining**. Troubleshoot with **invocation logs** in **CloudWatch Logs Insights**, **X-Ray** traces and **Q Developer**'s error-pattern analysis.
