# Unit 01: Design GenAI solutions

**Task 1.1: Analyze requirements and design GenAI solutions.** Three skills sit under it:

- Create an architecture that fits the business need and its technical constraints.
- Prove feasibility with a proof of concept on **Amazon Bedrock** before scaling.
- Standardise the building blocks so every team deploys the same way, guided by the **AWS Well-Architected Framework** and its **Generative AI Lens**.

This unit is the foundation for everything that follows. It gives you the vocabulary, the map of **Amazon Bedrock**, and the way of reading a scenario that the rest of the exam relies on.

## What a generative AI application is made of

Every GenAI application on the exam has the same skeleton. A client sends a request to an **API layer**. An **orchestration layer** builds a prompt, possibly fetches extra context, calls a **foundation model** (FM), checks the answer, and returns it.

Around that core sit four supporting blocks:

- **Knowledge**: documents turned into searchable vectors.
- **Tools**: APIs the model can ask you to call.
- **Safety controls**: guardrails and redaction.
- **Operations**: logging, metrics and cost controls.

A few terms carry most of the weight in exam questions:

- A **foundation model** is a large pre-trained model you use through an API. A text foundation model is also called a **large language model**, or LLM. You never train it; you prompt it, ground it, or at most fine-tune it.
- A **prompt** is everything you send in one request: system instructions, conversation history, retrieved context, and the user's message. It is measured in **tokens**, and a token is roughly three-quarters of a word in English. The **context window** is the maximum number of tokens a model accepts in one request, and you pay per input and output token.
- **Inference** is one model call. **Streaming** returns tokens as they are generated instead of waiting for the whole answer.
- **Retrieval Augmented Generation (RAG)** fetches relevant text from your own data at request time and pastes it into the prompt, so the model answers from facts it was never trained on. **RAG** needs **embeddings**, vectors that encode meaning, stored in a **vector store**.
- An **agent** is an FM given tools and a goal. It decides which tool to call, calls it, reads the result, and continues until the task is done.
- **Hallucination** is a fluent but false answer. Grounding, guardrails and evaluation exist to detect and reduce it.

These are the general AWS building blocks the path leans on, each in one line so nothing is assumed:

- **Amazon S3**: object storage.
- **AWS Lambda**: serverless functions that run per request.
- **Amazon DynamoDB**: a key-value NoSQL database.
- **Amazon API Gateway**: managed HTTP and **WebSocket** APIs.
- **AWS Step Functions**: workflow orchestration.
- **Amazon EventBridge**: an event bus.
- **Amazon SQS**: queues.
- **Amazon SNS**: notifications.
- **IAM**: identities and permissions.
- **Amazon VPC**: private networking.
- **AWS KMS**: encryption keys.
- **Amazon CloudWatch**: metrics, logs, alarms and dashboards. **Logs Insights** is its query language over logs.
- **AWS CloudTrail**: the audit log of API calls.

An **ARN**, or Amazon Resource Name, is the unique identifier every AWS resource carries.

When you read a scenario, first decide which of these blocks the requirement is really about.

- "Answers must come from our policy documents" is a **knowledge** problem, not a model problem.
- "Must never discuss competitors" is a **safety control**.
- "Must switch providers without redeploying" is an **architecture** problem.

## The AWS AI landscape in 2026

Before choosing a service, know the map. AWS offers AI in four layers.

- **Foundation models as a service** sit at the top. **Amazon Bedrock** is where you call models from many providers through one API and get the surrounding features, such as **Knowledge Bases**, **Agents**, **Guardrails** and **Evaluations**, without running infrastructure.
- **Build and host your own** sits below it. **Amazon SageMaker AI** is where you train, fine-tune and host models on instances you choose, with notebooks, pipelines and endpoints.
- **Task-specific AI services** sit beside them, each a managed API for one job.
- **Assistants** sit at the user-facing end: **Amazon Q Developer** for developers and **Amazon Q Business**, now succeeded by **Amazon Quick**, for employees.

The task-specific services are:

- **Amazon Comprehend**: text analysis and PII.
- **Amazon Transcribe**: speech to text.
- **Amazon Polly**: text to speech.
- **Amazon Translate**.
- **Amazon Textract**: document text and forms.
- **Amazon Rekognition**: image and video analysis.
- **Amazon Lex**: conversational bots.
- **Amazon Kendra**: enterprise search.
- **Amazon Personalize**: recommendations.
- **Amazon Bedrock Data Automation**: multimodal extraction.

Underneath everything are AWS's own accelerator chips, **Trainium** for training and **Inferentia** for inference. Beside them are the data services, **S3** and the databases and search engines of unit 04, that hold what the models read.

The exam lives mostly in the first layer, uses the third as building blocks in pipelines, and reaches for the second only when a managed model will not do. Each service is defined again where the path first uses it in earnest; this map is so the names are never new.

## Amazon Bedrock is the default platform

**Amazon Bedrock** is a fully managed service that gives you many foundation models through one set of APIs, with no infrastructure to run. It hosts models from **Amazon** (**Nova**, **Titan**), **Anthropic** (**Claude**), **Meta** (**Llama**), **Mistral**, **Cohere**, **AI21 Labs** (**Jamba**), **DeepSeek**, **Stability AI** and others, plus a **Marketplace** of additional models.

Your prompts and completions carry three guarantees. They are not used to train the underlying models. They are not shared with model providers. They stay in the Region you call. That is why **Bedrock** is the answer whenever a scenario mentions sensitive data plus "minimal operational overhead".

**Bedrock** is more than a model endpoint. The exam expects you to know the whole feature map and to pick the feature that matches a requirement:

| **Bedrock** capability | What it does | Typical requirement it answers |
|---|---|---|
| **Runtime APIs** (`InvokeModel`, `Converse`, streaming variants) | Send a prompt, get a completion. **Converse** gives one request format for all chat models | "Call the model", "write code once for many models" |
| **Knowledge Bases** | Managed **RAG**: ingests documents, chunks and embeds them, stores vectors, retrieves and optionally generates | "Ground answers in company documents with minimal ops" |
| **Agents** and **AgentCore** | FMs that plan and call tools through **action groups** (the APIs or **Lambda** functions an agent is allowed to call); **AgentCore** adds runtime, memory, identity, gateway and observability for any agent framework. **Bedrock Agents** is now "**Agents Classic**" (maintenance mode, closed to new customers since July 2026); questions still say "**Bedrock Agents**", so answer as they expect, and know **AgentCore** is the current path (Domain 2 unit 01) | "Automate multi-step tasks", "call APIs on the user's behalf" |
| **Guardrails** | Content filters, denied topics, word filters, PII redaction, contextual grounding and automated reasoning checks, applied to any model or via `ApplyGuardrail` | "Block harmful content", "prevent PII leakage", "reduce hallucinations" |
| **Prompt Management** and **Flows** | Versioned, parameterised prompt templates, and a visual builder that chains prompts, knowledge bases, agents, **Lambda** and conditions | "Govern prompts", "multi-step prompt chains with branching" |
| **Model customization** | Fine-tuning, reinforcement fine-tuning, distillation, continued pre-training, and **Custom Model Import** for open-weight models | "Consistent style", "domain terminology", "bring our fine-tuned **Llama**" |
| **Evaluations** | Automatic, LLM-as-a-judge, human, and **RAG** evaluation jobs | "Compare models objectively", "measure hallucination" |
| **Inference options** | On-demand, **Provisioned Throughput**, batch inference, cross-Region inference, latency-optimized inference, intelligent prompt routing | "Throttling", "predictable throughput", "cheap bulk jobs", "lowest latency" |
| **Bedrock Data Automation** | Turns documents, images, audio and video into structured output with blueprints | "Extract fields from claim forms", "multimodal ingestion" |
| Model catalogue and access | Text, image, video, embedding and reranker models from many providers, served on demand, plus **Bedrock Marketplace** models deployed to endpoints; you enable **model access** per account before use | "Which model", "embedding model", "reranker" |
| Pricing modes | Per input and output token on demand, hourly **Model Units** or tokens per minute for **Provisioned Throughput**, a discount for batch, a discount for cached prompt tokens, and application inference profiles to allocate cost by team | "Most cost-effective", "attribute spend" |
| Security | **IAM** actions such as `bedrock:InvokeModel` on model and inference-profile ARNs, **PrivateLink** endpoints, **KMS** keys for custom models, agents and knowledge bases, and the guarantee that your data never trains the base models | "Least privilege", "private connectivity", "data not used for training" |

Day to day you meet **Bedrock** in four places.

**The console.** It has **model access**, where you enable the models your account may use; some providers require an end-user licence. The **playgrounds** for text, chat and image let you try prompts, compare two models side by side, and read the token counts and latency of each response. There are pages for every feature above.

**The APIs and SDKs.** **boto3**, the **AWS CLI** and the SDKs for other languages call the same features from code. `bedrock` is the control-plane client for creating resources, and `bedrock-runtime` is the data-plane client for inference.

**Monitoring.** Several sources report what the models did:

- **CloudWatch** metrics: invocations, latency, errors, throttles and token counts.
- **Model invocation logging**: full requests and responses to **CloudWatch Logs** or **S3**.
- **CloudTrail**: the API audit trail.
- **Traces**, for agents: a record of every reasoning step and tool call.
- **CloudWatch generative AI observability** and **AgentCore Observability**, which extend traces to framework-based agents.

**The open-source agent frameworks AWS publishes.** **Strands Agents** builds model-driven agents with tools as Python functions, and **Agent Squad** routes among specialised agents. The **Model Context Protocol (MCP)** connects tools. These sit beside **Bedrock** and run on **AgentCore**, and Domain 2 covers them in depth.

**Amazon SageMaker AI** is the second platform. Go to it when you need to host your own or an open-weight model on infrastructure you control, using **real-time**, **serverless**, **asynchronous** or **batch** endpoints. It is also where you fine-tune with full control or run classical ML. **SageMaker JumpStart** gives one-click deployment of hundreds of open models.

The exam's rule of thumb: **Bedrock** when a managed FM will do, **SageMaker AI** when you need custom weights, custom containers, or specific instance types.

Self-managed hosting on **EC2** or **EKS** (**Kubernetes**) is almost always a distractor. Choose it only when the question insists on a specific runtime you cannot get any other way.

## From requirements to architecture

The exam tests whether you can hear a requirement and pick the pattern. The following pairings come up again and again.

- **Knowledge that changes often, or that must be cited** points to **RAG** with **Knowledge Bases**, not fine-tuning. Fine-tuning changes how a model writes, not what it knows, and it bakes in a snapshot of the data.
- **Consistent tone, format or domain phrasing that prompts cannot reliably enforce** points to **fine-tuning**.
- **A model that must act**, such as looking up an order or opening a ticket, points to **Agents** with **action groups** or an **MCP** tool.

**MCP**, the **Model Context Protocol**, is the open standard for exposing tools and data to models. An **MCP server** publishes tools with typed schemas, and the agent's **MCP client** calls them the same way whatever sits behind them. Unit 05 and Domain 2 unit 01 go deeper.

The shape of the traffic decides the next set:

- **Interactive users** need synchronous or **streaming** responses.
- **Long-running or bulk work**, such as summarising thousands of documents where users accept a delay, needs asynchronous processing. If the delay can be hours, **Bedrock batch inference** is the cheapest route.
- **Bursty traffic with strict latency** favours on-demand with **cross-Region inference** for headroom.
- **Steady high volume** favours **Provisioned Throughput**.

Compliance and breadth decide the rest:

- **Sensitive data** points to **Bedrock** in the same Region, **VPC endpoints** (**AWS PrivateLink**) so traffic never leaves the AWS network, **KMS** encryption, and **guardrails** for PII.
- **Data residency across countries** points to Regional deployments and geographic **cross-Region inference profiles** that stay inside a geography, or **AWS Outposts** when regulated data must not leave the premises.
- **Multiple models for different tasks** points to a routing layer: **API Gateway** plus **Lambda**, with model choice held in **AWS AppConfig** so it changes without a deployment. Unit 02 covers this in depth.

## Integration patterns

A GenAI capability is usually bolted onto an existing system, so the integration pattern is part of the design. The integration services themselves are a small family:

- **API Gateway** for synchronous HTTPS APIs.
- **SQS** queues for buffering.
- **SNS** for fan-out notifications.
- **EventBridge** as the event bus.
- **Kinesis** for high-volume streams.
- **Step Functions** for multi-step workflows.
- **AppFlow** and **Glue** for moving data.

Domain 2 unit 03 returns to each.

**Synchronous request and response.** Put **Amazon API Gateway** in front of a **Lambda** function that calls **Bedrock**. It is simple, serverless, and fine when a response fits in a few seconds.

Two limits matter. **API Gateway** REST integrations time out at about 29 seconds by default, and **Lambda** runs at most 15 minutes. Long answers from large models can exceed the first limit, which is why streaming exists.

**Streaming to the browser.** Use `ConverseStream` or `InvokeModelWithResponseStream` and push tokens to the client. The managed pattern is an **API Gateway** **WebSocket API** backed by **Lambda**, which keeps a two-way connection open so partial results appear as they are generated.

**Lambda response streaming** through a **function URL**, a direct HTTPS endpoint on a **Lambda** function, is the alternative when you do not need bidirectional messages. Streaming does not make the model faster; it improves perceived latency.

**Asynchronous work.** Put the request on an **Amazon SQS** queue and let a **Lambda** consumer call **Bedrock** and write results to **S3** or **DynamoDB**. The consumer can instead deliver them back through a **webhook** URL the caller supplied.

This decouples the caller from model latency, absorbs traffic spikes, and gives you retries and **dead-letter queues**, which are holding queues for messages that failed repeatedly, for free.

When the work has several steps, **AWS Step Functions** orchestrates them with built-in retries, error handling and a visual execution history. It has an **optimized integration** that calls **Bedrock** `InvokeModel` directly from a state, with request bodies up to 256 KiB and **S3** references for larger payloads.

**Event-driven enrichment.** When an application already publishes events, such as an order created or a document uploaded, route them through **Amazon EventBridge** rules or **S3 Event Notifications** to a **Lambda** function that calls the model and writes the enrichment back.

This is the pattern for "add GenAI without touching the legacy application": the legacy system keeps emitting events and never learns that a model exists. **Kafka** and other pub/sub systems play the same role in non-AWS estates.

**GraphQL and front ends.** **AWS AppSync** provides a managed **GraphQL** API with declarative data fetching, caching, fine-grained authorization and a direct integration with **Bedrock** runtime from its resolvers. A mobile or web client can therefore call a model through a typed schema.

**AWS Amplify** generates front-end UI and connects it to **Bedrock**-backed APIs. Publishing an **OpenAPI specification**, a machine-readable description of a REST API, for your FM endpoints is how you make an "API-first" integration consumable by other teams.

**Ready-made scaffolding.** The **Generative AI Application Builder on AWS** is an AWS Solution. It is a dashboard deployed with the **AWS CDK**, the Cloud Development Kit, which is infrastructure as code written in Python or TypeScript that compiles to **CloudFormation**.

From a no-code wizard it stands up chat, text-generation and agent use cases on **Bedrock** or **SageMaker** models, with optional **Knowledge Bases**, **Guardrails**, **Agents**, **AgentCore** and **MCP servers**, the tool servers the agent can call. It exists to accelerate experimentation, which is exactly the proof-of-concept skill.

## Proving feasibility before scaling

Skill 1.1.2 is about not overbuilding. The right PoC is small, measurable and disposable.

Start in the **Bedrock** console. The **playground** lets you send prompts to several models side by side, adjust parameters, and see token counts and latency without writing code. For a slightly more realistic test, put a thin **API Gateway** and **Lambda** layer in front of two or three candidate models and run a fixed set of representative prompts through each. If the use case needs your data, create a **Knowledge Base** pointed at a sample of documents in **S3** rather than the full corpus.

Measure four things:

- Output quality against a small labelled set, or against reviewer ratings.
- Latency and time to first token.
- Throughput at the expected load.
- Cost per request, from token counts.

Those four numbers, plus stakeholder feedback, are what justify or kill the project.

What you do not do in a PoC is build multi-Region deployments, buy **Provisioned Throughput**, fine-tune a model, or write a custom inference server. Every distractor in PoC questions is one of those.

The PoC also sets the baseline you will later evaluate against, so keep the prompt set and the results.

## Standardising the building blocks

Skill 1.1.3 is about repeatability across many teams and deployments. The reference is the **AWS Well-Architected Framework** and its **Generative AI Lens**, which adds generative-AI-specific guidance under all six pillars:

- **Operational excellence**: consistent output quality, traceability, automated lifecycle.
- **Security**: protect endpoints, prompt injection, model poisoning.
- **Reliability**: throughput, graceful failure.
- **Performance efficiency**: model performance, retrieval performance.
- **Cost optimization**: model selection, prompt engineering for cost, vector store and agent cost.
- **Sustainability**: minimise compute for customisation, hosting and storage.

The lens is organised around the lifecycle stages of scoping, model selection, customization, development, deployment, integration and continuous improvement, and you can run it as a review in the **AWS Well-Architected Tool**.

Standardisation in practice means reusable infrastructure as code. Package these as **CloudFormation** or **CDK** constructs:

- A **Bedrock** inference wrapper, which applies the guardrail, the logging and the retry policy.
- A **RAG** integration template.
- A prompt-evaluation module.

Publish them in an **AWS Service Catalog** portfolio, a curated catalogue of approved **CloudFormation** products that teams launch self-service, so each business unit deploys the approved pattern independently.

Add shared security components: **Amazon Cognito** for authentication, which is the managed sign-in service for application users and issues tokens and temporary AWS credentials; **AWS KMS** for encryption; and least-privilege **IAM** roles. Add shared observability with **CloudWatch** dashboards and **AWS X-Ray** tracing.

The distractors are a shared Git repository (no enforcement), monthly review meetings (no automation), a single central platform everyone must use (ignores workload differences), or asking each team to run the lens themselves.

**GenAIOps** extends this to the model side. **SageMaker Pipelines** and **MLflow on SageMaker** give experiment tracking and repeatable evaluation and deployment. CI/CD pipelines built with **CodePipeline** and **CodeBuild** re-run evaluations whenever a prompt, model or index changes.

## Where the application runs

Deployment strategy is the last design decision. **Bedrock** removes hosting for the model, but the application still needs a home, and AWS compute comes in a short list, from most to least managed:

- **AWS Lambda** runs functions per request with a 15-minute limit.
- **AWS App Runner** runs a web container with nothing to manage.
- **Amazon ECS** orchestrates containers on **AWS Fargate** (serverless capacity) or on **EC2**, and **Amazon EKS** does the same with **Kubernetes**.
- **Amazon EC2** gives you virtual machines, including GPU instances.
- **SageMaker AI endpoints** host models, and **AgentCore Runtime** hosts agents.

The rule of thumb:

- **Lambda** for event-driven and request/response logic.
- **ECS** on **Fargate** or **App Runner** for containers that must hold long-lived connections, a **WebSocket** telemetry feed for example, which **Lambda**'s 15-minute limit cannot.
- **SageMaker AI endpoints** when the model itself is yours.

Geography adds three more cases. For global users, deploy per Region and route with **Amazon Route 53** or **AWS Global Accelerator**, keeping each Region's data inside it. For edge sites with unreliable connectivity, **AWS IoT Greengrass** runs **SageMaker**-trained models and **Lambda** functions locally. For data that legally cannot leave a facility, **AWS Outposts** runs preprocessing on premises and sends only sanitised text to **Bedrock**.

## Worked scenario

A regional insurer wants an assistant that helps claims handlers answer policy questions. The requirements arrive as a list:

- Answers must cite the policy documents.
- Protected health information must never leave the company.
- The assistant must read claim status from a twenty-year-old claims system.
- A working prototype is due in four weeks.
- Two other business units want the same thing next quarter.

Map each requirement to a block.

- Citations from policy documents is the *knowledge* block: an **Amazon Bedrock Knowledge Base** over the policy PDFs in **S3**, returning passages with source references, rather than fine-tuning a model on the documents.
- PHI control is the *safety* block: **Bedrock Guardrails** with sensitive information filters on input and output, plus **Amazon Comprehend Medical**, **Comprehend**'s healthcare variant, which detects protected health information, to redact records before they are indexed.
- Claim status is the *integration* block: the legacy system cannot change, so an **API Gateway** endpoint with a **Lambda** adapter exposes the status lookup, and the model calls it as a tool.
- Hosting is the *runtime* block: traffic is spiky and modest, so use **Lambda** invoking **Bedrock** on demand behind **API Gateway**, with no servers to size.

The four-week deadline is the proof-of-concept skill. Start in the **Bedrock** playground with two or three candidate models on twenty real handler questions. Score them with a **Bedrock** evaluation job against the policy passages, and fix the success criteria, citation accuracy and handler time saved, before building. Use the **Generative AI Application Builder on AWS** or a small **CDK** stack to stand the pilot up in days. Only when the pilot clears the criteria does the design add throughput reservations or a second Region; doing that first is the classic wrong answer.

The other business units are the standardisation skill. Package what worked as **CDK** constructs in an **AWS Service Catalog** portfolio: the inference wrapper with guardrail and logging, the **Knowledge Base** template, and the evaluation module. Review each deployment against the **Well-Architected Generative AI Lens**, and run prompts and evaluations through a **GenAIOps** pipeline, so the next unit deploys the approved pattern instead of reinventing it.

A question built on this scenario will ask which option meets every requirement with the least overhead. The answer is the one that names a managed service for each block and validates before scaling.

## Exam lens

Task 1.1 questions are the "architect" questions of the exam. They describe a company, a set of requirements (usually one of them is compliance-flavoured), and ask for the architecture that meets all of them with the least overhead. Three habits win them:

1. Match each requirement to a block: **knowledge**, **safety**, **integration**, **hosting**. The correct option names a managed service for each; the wrong ones leave a requirement unmet or build it by hand.
2. Reject answers that skip validation. In PoC questions, "deploy a fully scalable multi-Region architecture immediately" and "pick one model without comparison" are always wrong.
3. Recognise the standardisation vocabulary: **Well-Architected Generative AI Lens**, reusable templates, **Service Catalog**, **GenAIOps**. Anything that relies on people remembering to do the right thing loses to a template.

## Knowledge check

<!-- KC: E1-Q55, E1-Q56, E3-Q10 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 55

A retail analytics company wants to evaluate whether generative AI can improve internal reporting workflows by automatically generating weekly sales summaries, identifying anomalies, and drafting executive insights. Before committing to a full production deployment, the lead AI engineer is asked to validate feasibility, model performance, and expected ROI. The engineer needs to quickly test multiple Amazon Bedrock foundation models, compare latency and output quality, and gather stakeholder feedback with minimal engineering overhead.

Which approach is the MOST appropriate for conducting this proof-of-concept (POC) phase?

- **A)** Use a single chosen foundation model and skip comparative testing to reduce initial development effort and accelerate the move to full-scale deployment.
- **B)** Develop a custom container-based inference server on Amazon EC2 to manually manage model selection, caching, and benchmarking across different Bedrock models.
- **C)** Immediately deploy a fully scalable multi-Region architecture using Amazon ECS, provisioned throughput for Bedrock, and an automated CI/CD pipeline to simulate production traffic patterns.
- **D)** Build a small-scale proof-of-concept using Amazon Bedrock by testing multiple foundation models behind a simple API Gateway and Lambda architecture to evaluate performance, latency, and output quality before investing in a production deployment.

<details><summary>Answer</summary>

**Answer: D.** A PoC should be small and comparative: several Bedrock models behind a thin API Gateway and Lambda layer, measured for performance, latency and quality before production investment. Skipping comparison, building a custom EC2 inference server, or deploying a multi-Region production architecture first are the opposite of validating feasibility.

*Where this is covered: Unit 01, Proving feasibility before scaling. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 1, question 56

A global media company is developing multiple generative AI applications, including automated captioning, editorial assistance, and conversational search. Several teams are building their own Amazon Bedrock-based prototypes using API Gateway and Lambda, but leadership is concerned that each team is implementing different security controls, logging approaches, and model invocation patterns.

The principal AI architect must ensure all teams follow consistent, repeatable architecture patterns and adopt validated best practices across environments.

Which approach BEST meets these requirements?

- **A)** Require teams to store all model invocation code in a shared Git repository to encourage consistent implementation patterns.
- **B)** Develop reusable architecture blueprints and service templates using the AWS Well-Architected Framework and the AWS WA Tool Generative AI Lens to enforce standardized best practices across all GenAI projects.
- **C)** Allow teams to continue building independently but require monthly architectural review meetings to surface inconsistencies and recommend improvements.
- **D)** Build a single centralized generative AI platform that all teams must integrate with, regardless of workload differences.

<details><summary>Answer</summary>

**Answer: B.** Reusable architecture blueprints and service templates built on the Well-Architected Framework and the Generative AI Lens enforce consistent security, logging and invocation patterns across teams. A shared repository and monthly meetings do not enforce anything, and a single mandatory platform ignores workload differences.

*Where this is covered: Unit 01, Standardising the building blocks. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 3, question 10

A multinational insurance provider is building a suite of generative AI applications across multiple business units. Each team uses Amazon Bedrock for FM inference and Amazon SageMaker AI for data preparation and prompt-evaluation workflows. Leadership wants to eliminate inconsistent implementations and enforce a uniform, repeatable pattern for model invocation, retrieval-augmented generation (RAG), and shared security controls. The architecture must comply with the AWS Well-Architected Framework and the Generative AI Lens.

The cloud platform team must create standardized, reusable components that every team can adopt without rewriting integration logic. The components must enforce consistent guardrail usage, validated API patterns, and centralized logging while enabling each business unit to deploy independently.

Which approach MOST effectively provides standardized, enterprise-wide GenAI components?

- **A)** Build a single global Amazon Bedrock prompt router and require all teams to send requests through it so the enterprise can standardize all FM outputs.
- **B)** Create reusable Bedrock inference wrappers, prompt-evaluation modules, and RAG integration templates published in an internal AWS Service Catalog portfolio that development teams can deploy consistently across environments.
- **C)** Require each team to independently run the AWS WA Tool Generative AI Lens and manually update their services to align with architectural best practices.
- **D)** Deploy a central SageMaker multi-model endpoint shared across all business units to enforce consistent model invocation patterns and ensure identical architecture usage across departments.

<details><summary>Answer</summary>

**Answer: B.** Reusable Bedrock inference wrappers, prompt-evaluation modules and RAG templates published in an AWS Service Catalog portfolio give every business unit consistent guardrails, validated API patterns and centralised logging while deploying independently, in line with the Generative AI Lens. A single global prompt router centralises traffic not patterns, asking teams to run the lens themselves enforces nothing, and a shared multi-model endpoint is not an architecture standard.

*Where this is covered: Unit 01, Standardising the building blocks. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

A GenAI application is an **API layer**, an **orchestration layer**, a model, and the **knowledge**, **tools** and **safety controls** around it. **Amazon Bedrock** is the managed platform for models and for most of those surrounding pieces, while **SageMaker AI** is for models you host yourself.

Read requirements as knowledge, safety, integration or hosting problems, and answer each with the native managed service. Integrate through **API Gateway** and **Lambda** for synchronous calls, **WebSocket APIs** for streaming, **SQS** or **Step Functions** for asynchronous work, **EventBridge** for event-driven enrichment, and **AppSync** or **Amplify** for typed front ends.

Prove feasibility with a small, measured PoC in **Bedrock** before spending on scale, and standardise what works with the **Well-Architected Generative AI Lens** and reusable infrastructure as code.
