# Unit 06: Domain 2 review

Decision tables for the recurring Domain 2 choices, the vocabulary that gives answers away, a one-page summary, and the mixed quiz of questions not used in units 01 to 05.

## Decision tables

**Which agent technology?**

| Requirement wording | Answer |
|---|---|
| Managed agent with **action groups**, **knowledge bases**, memory, supervisor and collaborators (exam vocabulary) | **Amazon Bedrock Agents** (now **Agents Classic**) |
| Deploy agent code from any framework, isolated sessions, long-running, no server setup | **Amazon Bedrock AgentCore Runtime** (**SDK entrypoint decorator** plus starter toolkit) |
| Shared **long-term memory** across agents and sessions | **AgentCore Memory** (or **Strands** built-in memory modules) |
| Turn APIs and **Lambda functions** into **MCP tools** centrally | **AgentCore Gateway** |
| Validate inbound **OIDC** tokens and audiences for an agent | **AgentCore Identity** |
| Model-driven single agents, tools as Python functions, **MCP client** | **Strands Agents** |
| Route conversations among specialised agents with a classifier and supervisor | **Agent Squad** |
| Lightweight stateless tools / heavy compute tools | **MCP servers** on **Lambda** / on **ECS** |

**How should the model reason and stay safe?**

| Requirement wording | Answer |
|---|---|
| Deterministic thought-action-observation steps | **Step Functions** **ReAct** pipeline |
| Stop runaway loops, halt on tool failure or latency | **Step Functions** **stopping conditions**, **iteration limits**, **Lambda** timeouts, **circuit breakers** |
| Restrict what the agent can touch | **Least-privilege** **IAM** roles for the agent and each tool |
| Malformed tool arguments | **Lambda** validation with corrective feedback to the model |
| Best model per intent, merged answer | Routing plus aggregation framework |
| Human approval for risky cases, structured feedback | **Step Functions** **wait-for-callback** review steps, **API Gateway** feedback, **DynamoDB** |
| Human review of low-confidence extractions | **Amazon A2I** |

**Where does inference run?**

| Traffic and model | Answer |
|---|---|
| Occasional or spiky, **Bedrock** model | **Lambda** invoking **Bedrock** on demand |
| Steady, latency-critical, **Bedrock** model | **Provisioned Throughput** |
| Custom model, GPUs, near-real-time | **SageMaker** **real-time endpoint** |
| Small CPU model, intermittent, no infrastructure | **SageMaker Serverless Inference** |
| Large payloads or long generations, minutes acceptable | **SageMaker Asynchronous Inference** |
| Many adapters or models sharing an endpoint | **Inference components** (adapters) or multi-model endpoint |
| Proprietary models plus general FMs | Hybrid **SageMaker** and **Bedrock** |
| 70B model, cold starts, GPU memory exhaustion | **LMI container** with **tensor parallelism**, **lazy loading**, **quantisation** |
| Mostly simple requests, few complex | **Model cascading** |
| Persistent **WebSocket** connections without servers | **ECS** on **Fargate** |
| On-site inference with unreliable connectivity | **IoT Greengrass** |

**Which interaction pattern?**

| Requirement wording | Answer |
|---|---|
| Interactive, seconds, validate requests | **API Gateway** + **Lambda** + **Bedrock** |
| Background, hours of tolerance, spikes, cost | **SQS** + **Lambda** consumer + **Bedrock** (or **Bedrock** **batch)** |
| Tokens shown as generated, bidirectional | **API Gateway** **WebSocket** + **Lambda** + **Bedrock streaming** |
| One-way live updates to HTTP clients | **Server-sent events** or **Lambda response streaming** |
| Legacy system with outbound HTTPS only, loose coupling | **EventBridge** events → **Lambda** → **Bedrock** → synchronised store |
| Real-time **webhook** from SaaS | **API Gateway** + **Lambda** handler |

**Resilience and routing**

| Requirement wording | Answer |
|---|---|
| 429s and transient failures | SDK **exponential backoff with jitter** (standard retry mode) |
| Protect downstream from bursts | **API Gateway** **throttling** and **usage plans** |
| Keep working when a model fails | **Circuit breaker** with fallback tiers (smaller model → cache → static) |
| See where time goes across services | **AWS X-Ray** |
| Route by content with evolving rules and metrics | **Step Functions** **Choice states** |
| Switch models without deployment | **AppConfig** read at runtime |
| Route by header or query parameter | **API Gateway** **mapping templates** |

**Identity and residency**

| Requirement wording | Answer |
|---|---|
| Workforce access through the corporate IdP, **least privilege**, no long-lived credentials | **IAM Identity Center** with **SAML federation** and **permission sets** |
| Application users through an **OIDC** IdP, temporary credentials | **Amazon Cognito** |
| Data must stay on premises | **Outposts** for local processing, sanitised data to **Bedrock** |
| Ultra-low latency for mobile users | **AWS Wavelength** |
| Auditable gateway releases with tests, scans and rollback | **CodePipeline** and **CodeBuild** behind **API Gateway** |

**Developer tools**

| Requirement wording | Answer |
|---|---|
| Generate and refactor SDK code, tests, optimisation suggestions | **Amazon Q Developer** |
| Non-technical users assemble workflows, front end with little code, **API-first** | **Bedrock Flows**, **Amplify**, **OpenAPI** |
| Permission-aware assistant over internal repositories | **Amazon Q Business** with connectors and **IAM Identity Center** |
| Classify and extract from mixed documents in a workflow | **Step Functions** with **Bedrock Data Automation** |
| **Lex** bot misses paraphrases | **Slot type** **synonyms** |
| Correlate logs, trace calls, detect GenAI error signatures | **CloudWatch Logs Insights**, **X-Ray**, **Q Developer** |

## Words that give the answer away

- "maintain persistent shared state across specialised agents" → **Strands Agents** plus **Agent Squad** plus **MCP**.
- "thought-action-observation" → **Step Functions** **ReAct**.
- "runaway loops", "halt immediately if a tool call fails" → **Step Functions** **stopping conditions** and failure branches, **Lambda** timeouts, **circuit breakers**.
- "malformed parameter values" → **Lambda** validation and corrective feedback.
- "no HTTP server, no /ping or /invocations, minimal manual setup" → **AgentCore SDK** entrypoint decorator plus starter toolkit.
- "prebuilt **MCP server** that links to **Aurora**" → **AgentCore Runtime** with **Strands**.
- "8% complex, rest lightweight" → **model cascading**.
- "cold starts, GPU memory exhaustion, uneven token throughput" → LLM-optimised container with **tensor parallelism**.
- "respond within 15 minutes, GPUs, 50 MB input" → **Asynchronous Inference**; "near real time" → **real-time endpoint**.
- "under 5 GB, 40 to 60 concurrent, no infrastructure" → **Serverless Inference**.
- "outbound HTTPS only, loose coupling, downstream consumes as soon as ready" → **EventBridge** and **Lambda** with a synchronised store.
- "enterprise IdP, **least privilege**, no long-lived credentials" → **IAM Identity Center** with **SAML**.
- "must remain on premises" → **Outposts**.
- "automated tests, security scans, auditable, automatic rollback" → **CodePipeline** and **CodeBuild**.
- "tokens as soon as generated, bidirectional, browser" → **WebSocket API** with **Bedrock streaming**.
- "wait up to 24 hours, unpredictable spikes, cost-effective" → **SQS** and **Lambda**.
- "route by content, rules evolve, evaluate metrics" → **Step Functions** branching.
- "generate and refactor **Bedrock** SDK code" → **Amazon Q Developer**.
- "non-technical clinicians, **API-first**, visual orchestration" → **Amplify**, **OpenAPI**, **Bedrock Flows**.

## Domain 2 on one page

Agents reason, act and observe over tools with memory. Keep the platform and orchestration roles distinct:

- **Bedrock Agents** is the exam vocabulary for **action groups**, **return of control**, **knowledge bases**, **guardrails**, **memory**, a **code interpreter**, and **supervisor** and **collaborator** agents.
- **AgentCore** is the current platform for agents built with **Strands Agents**, **Agent Squad** or any framework. Its components include **Runtime**, **Memory**, **Gateway**, **Identity**, **Observability**, **Evaluations** and **Policy**.
- **MCP** is the tool protocol. Host light tools on **Lambda**, heavy ones on **ECS**, or use managed **AgentCore Gateway**.
- **Step Functions** implements **ReAct** when you orchestrate yourself. It supplies **stopping conditions**, **timeouts**, **circuit breakers** and human-review pauses. **IAM least privilege** and **Lambda** validation surround every tool.

Deploy on **Bedrock** through **Lambda** on demand, **Provisioned Throughput** or **batch inference**. Choose **SageMaker** for real-time GPU, **serverless** CPU, asynchronous, **batch transform**, multi-model or **inference components** hosting. Use a hybrid when proprietary models need custom processing.

Serve LLMs in **LMI containers** with **tensor parallelism**, **continuous batching**, **quantisation** and tuned loading. Cut cost with smaller models, cascading and caching.

For enterprise integration, match each responsibility to its services:

- Connect legacy systems through **API Gateway** and **Lambda adapters**, or through **EventBridge** events.
- Keep data in sync with **Glue**, **AppFlow** and **DMS**.
- Federate identity with **IAM Identity Center** or **Cognito**.
- Respect residency with **Outposts**, **Local Zones** and **Wavelength**.
- Release through **CodePipeline** and **CodeBuild**, with rollback behind a **GenAI gateway**.

Build the API around its interaction pattern:

- Synchronous: **API Gateway** and **Lambda** with validation and **throttling**.
- Asynchronous: **SQS** with **dead-letter queues**.
- Streaming: **WebSocket APIs** with **Bedrock streaming**.

**Retry** with backoff and jitter, break circuits into fallback tiers, and trace with **X-Ray**. Route with configuration, **Step Functions Choice states**, metrics or **mapping templates**.

For applications and developer tools, remember these combinations:

- Interfaces: **Amplify**, **OpenAPI** and **Bedrock Flows**; **Q Business** for internal knowledge; **Lex synonyms** for bots.
- Business systems: **Lambda** enrichment, **Step Functions** document workflows, **Bedrock Data Automation** and **A2I**.
- Developer productivity: **Amazon Q Developer**.
- Troubleshooting: **Logs Insights**, **X-Ray** and **Q Developer**.

## Mixed quiz

<!-- KC: REVIEW -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 49

A financial analytics company is building an FM-powered research assistant using Amazon Bedrock. The assistant needs access to several tools via MCP, including a lightweight exchange-rate lookup tool and a more complex market-sentiment analysis service. The engineering team wants to ensure that the FM can call simple tools with minimal latency while reserving more scalable compute resources for tools that require heavy data processing or model execution. They also need a consistent access pattern so all tools are discoverable and invoked in a standardized way by the FM.

Which architecture BEST meets these requirements?

- **A)** Store all tool definitions in Amazon S3 and let the FM retrieve and execute tool logic directly from the stored files without MCP-level orchestration.
- **B)** Host all MCP servers on Amazon ECS to standardize compute environments and avoid the operational overhead of managing two tool-hosting mechanisms.
- **C)** Deploy all MCP servers on Lambda regardless of complexity, using environment variables to simulate persistent state and reduce deployment overhead.
- **D)** Use AWS Lambda functions to implement stateless MCP servers for lightweight tools and Amazon ECS to host MCP servers that handle complex or compute-intensive tools, while relying on MCP client libraries to maintain consistent access patterns.

<details><summary>Answer</summary>

**Answer: D.** Stateless MCP servers on Lambda serve lightweight tools such as exchange-rate lookups with minimal latency, ECS hosts the compute-intensive sentiment analysis tools, and MCP client libraries give the FM one consistent discovery and invocation pattern across both. Tool logic in S3 files bypasses MCP, and forcing everything onto ECS or everything onto Lambda mismatches compute to tool needs.

*Where this is covered: Unit 01, MCP: how tools are exposed. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 1, question 52

A biotechnology startup is building an FM-powered research assistant that analyzes complex lab reports. The system uses three specialized models deployed through Amazon Bedrock: one FM optimized for summarizing experimental results, another FM tuned for extracting chemical relationships, and a third FM trained for identifying statistical anomalies. The solution architect needs a coordination layer that can dynamically select the best model based on query intent and aggregate outputs using custom logic before returning a unified response to researchers.

Which approach will BEST support this multi-capability coordination?

- **A)** Build a model selection and aggregation framework that routes requests to specialized FMs and merges outputs using custom logic, enabling optimized performance across multiple capabilities.
- **B)** Create separate API endpoints for each FM and instruct researchers to manually choose which endpoint to use for each type of analysis.
- **C)** Increase the context window of a single general-purpose FM so that all tasks are handled by one model without requiring routing logic or aggregation.
- **D)** Use AWS Lambda to randomly distribute requests among the three FMs to balance load and avoid overloading any single model.

<details><summary>Answer</summary>

**Answer: A.** A model selection and aggregation framework routes each request to the specialised FM for its intent and merges the outputs with custom logic into one unified response, which is exactly multi-capability coordination. Separate endpoints chosen by researchers, one general model with a bigger context window, and random distribution across models do not select by intent or aggregate.

*Where this is covered: Unit 01, Coordinating several models. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 2, question 70

A global fintech startup is migrating its proprietary fraud-scoring model to AWS. The model is under 5 GB, evaluates transactions in real time, and typically handles between 40 and 60 concurrent inference requests during peak hours. The team wants to avoid managing underlying compute infrastructure, autoscaling policies, or complex deployment pipelines.

They currently use Amazon Rekognition for image verification and Amazon Textract for document extraction, and now need a low-overhead solution to host their fraud model in the cloud. The company requires an environment that scales automatically with variable traffic while keeping operational maintenance to a minimum.

Which approach best meets these requirements?

- **A)** Configure a SageMaker asynchronous inference endpoint to handle fraud requests and rely on batched queueing during peak traffic.
- **B)** Create a model configuration within Amazon SageMaker AI and deploy the fraud model on a serverless SageMaker endpoint to automatically scale for real-time inference without provisioning infrastructure.
- **C)** Deploy the fraud model on a managed EC2 instance inside an Auto Scaling group and use an Application Load Balancer to distribute inference requests across the instances.
- **D)** Optimize the model with Amazon SageMaker Neo and deploy it on a real-time SageMaker endpoint with manual autoscaling configuration.

<details><summary>Answer</summary>

**Answer: B.** SageMaker Serverless Inference suits a model under 5 GB that serves real-time requests at tens of concurrent invocations with variable traffic: it provisions nothing, scales automatically and needs no autoscaling policies. Asynchronous inference queues requests instead of answering in real time, EC2 with Auto Scaling means managing infrastructure, and a real-time endpoint with manual autoscaling is the configuration overhead the team wants to avoid.

*Where this is covered: Unit 02, Deployment options and when each fits. Key: ours, confidence high.*

</details>

### 4. Exam 3, question 29

A retail company is enhancing its order-management application by integrating generative AI to generate personalized order-status summaries and customer-support responses. The existing application publishes order events (created, shipped, delayed, canceled) to an internal event stream. The engineering team wants to incorporate GenAI processing with minimal disruption to the current system while ensuring that events automatically trigger AI enrichment workflows. The solution must avoid adding tightly coupled API calls inside the legacy application.

Which solution will provide the MOST scalable and maintainable integration?

- **A)** Expose a synchronous REST endpoint with Amazon API Gateway that the legacy application must call for each order event. The endpoint triggers a Lambda function that sends data to Amazon Bedrock.
- **B)** Modify the legacy application to call a new GenAI microservice directly after each order update. The microservice invokes Amazon Bedrock and writes enriched results back to the database.
- **C)** Route order events through Amazon EventBridge. Use EventBridge rules to trigger a Lambda function that formats event details, invokes the Amazon Bedrock API for summarization, and stores the AI-generated output in the application’s data store.
- **D)** Create an S3 bucket for order snapshots. Configure the legacy application to upload order events as JSON files, and enable S3 event notifications to run a Lambda function that performs GenAI summarization.

<details><summary>Answer</summary>

**Answer: C.** Routing the existing order events through EventBridge and triggering a Lambda function that formats the event, invokes Bedrock and stores the enrichment keeps the legacy application untouched and loosely coupled while every event automatically drives AI processing. A synchronous REST call or a direct microservice call adds coupled API calls to the legacy code, and uploading JSON snapshots to S3 is an indirect workaround.

*Where this is covered: Unit 03, Connecting to systems that already exist. Key: ours, confidence high.*

</details>

### 5. Exam 3, question 59

A media analytics company is designing a flexible model interaction layer for its GenAI summarization and categorization services. The system must support both real-time synchronous requests for interactive applications and asynchronous batch submissions for large video-processing workloads. The company uses Amazon Bedrock for inference and wants a design that supports multiple compute environments, standardized request validation, and a decoupled architecture that can scale independently for each workload type.

Which combination of solutions will meet these requirements? (Select TWO.)

- **A)** Use language-specific AWS SDKs running on ECS tasks to submit asynchronous summarization jobs to an Amazon SQS queue. Process the queue with a Lambda consumer that invokes Amazon Bedrock and stores results in S3.
- **B)** Route all summary generation requests directly from clients to the Bedrock runtime API to avoid middleware and reduce latency.
- **C)** Use Amazon API Gateway to expose a synchronous inference endpoint backed by AWS Lambda. Validate request payloads at the API layer before calling the Bedrock InvokeModel API.
- **D)** Use Amazon EventBridge Pipes to automatically throttle synchronous client traffic and buffer requests before fan-out to the Bedrock API.
- **E)** Deploy a single monolithic EC2 instance hosting a custom REST endpoint that handles all synchronous and asynchronous inference workflows in one place.

<details><summary>Answer</summary>

**Answer: A, C.** API Gateway with Lambda gives a synchronous inference endpoint that validates payloads before calling InvokeModel, and SDK clients on ECS submitting jobs to an SQS queue consumed by Lambda give a decoupled asynchronous path for large video workloads, each scaling independently. Direct client calls to the runtime API skip validation and middleware, EventBridge Pipes does not throttle synchronous traffic, and one monolithic EC2 endpoint is neither decoupled nor managed.

*Where this is covered: Unit 04, Three interaction patterns. Key: ours, confidence high.*

</details>

### 6. Exam 3, question 68

An enterprise is designing a generative AI customer-support assistant that must deliver highly relevant, personalized answers in real time. The system processes large amounts of structured and unstructured content, including troubleshooting guides, device manuals, support transcripts, and diagnostic notes. To provide accurate results at scale, the architecture must combine semantic document retrieval with customer-specific personalization.

The engineering team has selected Amazon Kendra to retrieve intent-aligned documents and Amazon Personalize to tailor recommendations based on each customer’s historical interactions. The team must integrate these services with a Bedrock-powered LLM so that retrieval, ranking, personalization, and generation operate in a single, cohesive workflow without maintaining separate data pipelines.

Which solution best meets these requirements?

- **A)** Use Bedrock Prompt Flows as an orchestration layer where Kendra retrieval and Personalize signals are invoked separately, and store outputs in external systems without using a unified knowledge store.
- **B)** Continuously ingest support documents through Bedrock Data Automation and run Kendra and Personalize independently, merging results manually before generating a final answer.
- **C)** Precompute document embeddings with Bedrock Customizations and process Kendra retrieval results in a standalone pipeline, then call Personalize in a separate workflow to rank articles.
- **D)** Use an Amazon Bedrock Knowledge Base with hybrid search and enrich documents with Kendra metadata, then integrate Amazon Personalize to rank and personalize retrieved content before passing it to the LLM.

<details><summary>Answer</summary>

**Answer: D.** Amazon Kendra's GenAI index can act as the retriever behind a Bedrock Knowledge Base, so hybrid-search retrieval and Kendra's document metadata (intent and product attributes) live in one store; Amazon Personalize, the managed recommendation service, then ranks the retrieved items for the customer, and the LLM generates from that ranked context, giving retrieval, ranking and generation in a single flow. Invoking the three services separately without a unified store, merging results manually, and running Personalize as a separate pipeline all keep the separate data flows the question forbids.

*Where this is covered: Unit 05, Enhancing business systems. Key: ours, confidence medium.*

</details>

<!-- KC-END -->

## What to do next

Continue to Domain 3. If the agent questions felt uncertain, reread the *Exam lens* of unit 01; it carries most of this domain's weight.
