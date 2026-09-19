# Unit 04: FM API integrations

**Task 2.4: Implement FM API integrations.** This unit is about the API layer between users and models: synchronous, asynchronous and streaming interaction patterns, the **API Gateway** features that protect the model, the resilience stack (retries, **rate limiting**, **circuit breakers**, tracing), and how requests get routed to the right model.

This is the API layer between your users and **Bedrock**. Questions here describe traffic problems (spikes, **throttling**, slow responses, timeouts) and ask for the managed shape that handles them.

## Three interaction patterns

Every FM integration is synchronous, asynchronous or streaming, and the scenario usually tells you which by describing the user's patience.

**Synchronous.** The client waits for the complete answer. The managed shape is **Amazon API Gateway** → **AWS Lambda** → **Bedrock**, using `InvokeModel` or `Converse`. This suits interactive requests that finish in seconds.

Each part has a distinct job:

- **API Gateway** gives you a stable HTTPS endpoint, authentication, **request validation**, **throttling**, caching and metrics.
- **Lambda** scales per request.
- The **AWS SDK** makes the **Bedrock** call from **Lambda**. It can also run on **ECS**, **EKS** or **EC2**, provided that compute can hold an SDK client with sensible timeouts and **connection pooling**.

The time limits determine whether a synchronous call fits:

- **API Gateway** has an **integration timeout** of 29 seconds by default. For Regional and private **REST APIs**, you can request an increase above 29 seconds, which may lower the Region-level throttle quota.
- Edge-optimized **REST APIs** cannot have that timeout raised. **HTTP APIs** are capped at 30 seconds, so a generation that long is better streamed.
- **Lambda** has a 15-minute maximum.

Long generations therefore push you toward **streaming** or **asynchronous** designs.

**Asynchronous.** The client submits work and collects the result later. The managed shape is **API Gateway** or **Lambda** → **Amazon SQS** → **Lambda** consumer → **Bedrock** → **S3** or **DynamoDB**. The client receives a notification through **SNS**, a **webhook** or an **EventBridge** event, or uses a polling endpoint to collect the result.

**SQS** absorbs spikes and retries failed messages. After `maxReceiveCount` attempts, it moves poison messages to a **dead-letter queue**. Set the **visibility timeout** longer than the worst-case processing time so a message is not redelivered while a slow model call is still running.

**Step Functions** replaces the queue when the work has several steps. **Bedrock batch inference** replaces it when the job is bulk and can wait hours. Choose **asynchronous** processing when users tolerate delay, such as up to 24 hours for report summaries, when unpredictable traffic must not be dropped, or when cost matters more than latency.

**Streaming.** Tokens are delivered as generated. **Bedrock** provides `InvokeModelWithResponseStream` and `ConverseStream`; the challenge is getting the stream to the client. The delivery options are:

- **API Gateway WebSocket APIs** keep a two-way connection. The `$connect`, `$disconnect` and custom routes map to **Lambda**. Store connection IDs in **DynamoDB** so a **Lambda function** can push chunks back through the `@connections` callback URL. Idle connections close after 10 minutes, and no connection lives past two hours.
- **Lambda response streaming** sends a progressive response through a **function URL**. This is a dedicated HTTPS endpoint attached directly to a **Lambda function**, with no **API Gateway** required. Streamed payloads can reach 200 MB instead of 6 MB. **API Gateway** or **CloudFront**, the content delivery network, can front it.
- **Server-sent events** deliver a one-way `text/event-stream` response. They and **chunked transfer encoding** work for HTTP clients that only need server-to-client updates.

For a browser editor that must start showing suggestions the moment the user clicks, **WebSocket API** plus **Lambda** plus **Bedrock streaming** is the keyed answer. **SQS** long polling, **Lambda** polling until completion, or containers that wait for the full response defeat the purpose.

The distinction these questions turn on is how the response reaches the client. **REST** and **HTTP APIs** return a **Lambda** response only when it is complete. Token-by-token delivery to a browser therefore needs the **WebSocket API** or **Lambda response streaming** through a **function URL**. **Chunked transfer encoding** serves HTTP clients that read a stream from a container or a **function URL**.

Read the wording:

- "real-time bidirectional" → **WebSocket**.
- "incremental delivery" → **Bedrock streaming**.
- "background", "hours", "unpredictable spikes" and "cost-effective" → **SQS** and **Lambda**.
- "validate requests" → **API Gateway**.

## API Gateway features you will be tested on

**API Gateway** has two HTTP API styles plus **WebSocket**. Choose the style according to the features needed:

- **REST APIs** carry the full feature set: **request validators**, **mapping templates**, **usage plans** and **API keys**, caching, **WAF** integration, and **per-method throttling**.
- **HTTP APIs** are cheaper and faster, with **JWT authorizers** but fewer features.
- **WebSocket APIs** handle persistent connections.

**Request validation** checks that a request has the required parameters and that the body matches a **JSON Schema** model before it reaches your integration. Failures return 400 immediately and never consume **Lambda** or model capacity. Use it to enforce required fields, prompt size limits and token caps.

**Throttling** applies at account level, with a default of 10,000 requests per second and burst capacity. It also applies per stage, per method and per client. Per-client limits use **usage plans** with **API keys**. This stops one tenant's burst from starving others and protects **Bedrock** quotas.

**Mapping templates** transform requests and responses, which also makes them a lightweight place for **header-based routing**. **API keys** meter and throttle clients; they are not user authentication.

## Calling Bedrock: identity, quotas and errors

Three practical concerns sit under every integration: **identity**, **quotas** and **errors**.

**Identity.** A caller needs **IAM** permission for `bedrock:InvokeModel` on the resource it calls. Streaming also needs `bedrock:InvokeModelWithResponseStream`; the **Converse** operations are governed by the same permissions. The resource is identified by the ARN of a foundation model, an **inference profile**, a **provisioned model**, a **custom model deployment** or a prompt. The account must have **model access** enabled for that model. **Least privilege** means naming those ARNs, not `*`.

**Quotas.** **On-demand** capacity is metered per model per Region in **requests per minute** and **tokens per minute**. You can see the values in **Service Quotas**, and some can be raised on request. **Cross-Region inference** or **Provisioned Throughput** lifts the ceiling.

**Lambda** has its own limits and capacity controls that shape the API layer:

- A six-megabyte **synchronous payload** limit constrains request size.
- **Reserved concurrency** caps how many instances of a function may run. That cap also protects the **Bedrock** quota.
- **Provisioned concurrency** supplies pre-warmed instances for latency-sensitive paths.

**Errors.** Recognize the meaning of each error before choosing a response:

- `AccessDeniedException` (403): a permission or model-access problem.
- `ValidationException` (400): a malformed request or an input too long for the model.
- `ResourceNotFoundException` (404): a wrong model identifier or Region.
- `ThrottlingException` (429): a quota hit.
- `ModelTimeoutException` (408): a slow generation.
- `ModelNotReadyException` (429): a model still warming up. The SDK retries this automatically.

Domain 5 unit 03 has the full catalog and what to do about each error.

## Resilience

**Bedrock** is a shared service with quotas, and networks **fail**. Skill 2.4.3 stacks four layers.

**Retries with exponential backoff and jitter.** The **AWS SDKs** do this by default in **standard retry mode**. Delays grow exponentially and include random **jitter**, with longer waits for **throttling** than for transient network errors. A **retry quota** prevents a failing dependency from triggering retry storms. **Adaptive mode** adds client-side **rate limiting** when a service keeps **throttling**.

**Retry** `ThrottlingException` (429) and 5xx errors; do not retry 4xx client errors. Constant intervals, immediate synchronous retries and fixed linear patterns are the distractors because they synchronize clients and **amplify** load.

**Rate limiting at the edge.** **API Gateway** **throttling** and **usage plans** smooth bursts before they reach **Lambda** and **Bedrock**, protecting downstream systems.

**Circuit breakers and fallbacks.** When a dependency keeps failing, stop calling it for a cooling-off period and serve a fallback. That can be a smaller model, a cached response, a static message or a human queue.

The **circuit breaker** moves through three states:

- **Closed**: calls succeed and continue to flow.
- **Open**: calls are rejected during the cooling-off period.
- **Half-open**: a few trial calls test whether the dependency has recovered before the breaker closes again.

**Step Functions Retry and Catch** implement this declaratively. Application code or a **Lambda** function that tracks error rates implements it programmatically. Define the **degradation path** explicitly: primary model → smaller model → cached responses → static responses.

**Observability.** **AWS X-Ray** traces a request from **API Gateway** through **Lambda** to the **Bedrock** call and back. **Segments** and **subsegments** identify each hop, while **annotations** record model name, token counts and prompt size. Together, they show where time goes and which retries happened.

**CloudWatch** supplies **Bedrock** metrics and alarms. The metrics cover invocations, latency, throttles, and input and **output tokens**. For a Regional outage, **active-passive deployments** with **Route 53 health checks** complete the picture. The first response to **throttling**, however, is **backoff**, **rate limiting** and **cross-Region inference**, not multi-Region redeployment.

**Typical values.** Questions and AWS guidance use these round numbers:

- **SQS visibility timeout**: 5 to 15 minutes for FM tasks, longer than the slowest model call.
- **Dead-letter queue**: move messages after 3 to 5 receives.
- **SDK retry attempts**: 3 to 5.
- **WebSocket keep-alive pings**: every 30 to 60 seconds.
- **Cascade confidence threshold**: around 0.7 to 0.9 before escalating to the large model.
- **A/B candidate**: 5 to 10 percent of traffic.

## Routing requests to the right model

Skill 2.4.4 ranks routing mechanisms by how dynamic they need to be.

**Static routing** keeps a mapping from request type to model in configuration, using **AWS AppConfig feature flags** or **Parameter Store**. The application reads it at runtime, so the mapping changes without code deployment. The rules themselves remain simple. Domain 1 unit 02 covers the **AppConfig** pattern.

**Content-based routing in Step Functions.** A **Choice state** inspects the request payload, using its length, language, presence of code or classification result. It then invokes the matching specialized model.

Add new rules and models as **state machine revisions**, without application code changes. The same workflow can record performance metrics for later tuning. This is the answer when the requirement combines conditional rules on request content, evolving logic and metric evaluation.

**Metric-based routing.** Store per-model latency, cost and quality in **DynamoDB** or **Amazon Timestream**, the **serverless** time-series database. The router uses those metrics to pick a model by objective. Run **A/B tests** by sending a small share of traffic to a candidate and comparing the results.

**API Gateway request transformations.** **Mapping templates** route to different integrations using a header or query parameter, such as `x-model-preference`. This is simple, but the logic lives in templates and the client must send the selector.

**Managed routing.** **Bedrock intelligent prompt routing** picks between sizes within a model family by predicted response quality. **Model cascading** escalates from a small model when confidence is low.

Routing can also select the *prompt*, not just the model. **Bedrock Prompt Management**, covered in Domain 1 unit 06, stores **versioned prompt templates**. A router that reads a document's category can therefore pick both the model and the category's style-guide prompt by name.

## Worked scenario

A customer-support platform exposes three FM features to its clients: an interactive chat, a bulk document-classification upload, and a live "suggest a reply" editor. During load tests the team sees **throttling** errors, slow responses on long generations, and one tenant's bursts starving the others.

Each feature gets the interaction pattern its user can tolerate. The chat is synchronous: **API Gateway** with **request validation** (a **JSON Schema** that rejects oversized prompts before they cost anything) invokes a **Lambda function** that calls **Converse** and returns within seconds. The bulk upload is asynchronous: **API Gateway** drops jobs onto an **SQS** queue, a **Lambda** consumer calls **Bedrock** and writes results to **S3**, a **dead-letter queue** catches poison messages after five receives, and the **visibility timeout** exceeds the slowest model call; the client polls a status endpoint or receives an **SNS** notification. The editor streams: an **API Gateway** **WebSocket API** holds the connection, connection IDs sit in **DynamoDB**, and the **Lambda function** pushes tokens from **ConverseStream** back as they arrive.

Resilience is layered. The SDK's standard retry mode applies **exponential backoff with jitter** to **throttling** errors, and adaptive mode adds client-side **rate limiting** for the bulk consumer. **API Gateway** **usage plans** give each tenant its own throttle so bursts stay contained. A **circuit breaker** in the consumer opens after repeated failures and serves a smaller fallback model, then half-opens to test recovery. **X-Ray** traces every request through **API Gateway**, **Lambda** and the **Bedrock** call with **annotations** for prompt length and model, which is how the team finds that long generations, not the network, cause the slow responses; the fix is streaming plus a token cap.

Routing completes the design: a **Step Functions** **Choice state** sends short queries to a fast model, technical ones to a reasoning model and code to a code model, with the rules changed as state machine revisions and the per-category prompt templates pulled from **Prompt Management**. When the questions describe **throttling** at peak, users who will wait, tokens that must appear as typed, or rules that must evolve without code changes, they are describing these pieces.

## Exam lens

- "429 **throttling** and transient timeouts at peak, protect downstream, full request-path visibility" → SDK **exponential backoff with jitter**, **API Gateway** **rate limiting**, **X-Ray** tracing.
- "Both real-time clients and background processing of large PDFs, **request validation**, reliable messaging" → **API Gateway** with validation for synchronous calls, **SQS** with **Lambda** workers for asynchronous ones.
- "Display tokens as they are produced, browser clients, persistent bidirectional connection" → **Bedrock streaming** through an **API Gateway** **WebSocket** endpoint.
- "Analyze button, suggestions stream immediately, category metadata picks the model and style guide, least operational overhead" → **WebSocket API** plus **Lambda** that routes by metadata and uses **Bedrock streaming** (with **Prompt Management** for the style rules).
- "Streamed responses, enforce token limits, controlled retries on model timeouts, **request validation**, keep it off the app servers" → **API Gateway** custom FM API with **request validation**, chunked streaming, and SDK-based retries in **Lambda**.
- "Users wait up to 24 hours, unpredictable spikes, fault tolerant, cost-efficient" → **Lambda** publishes to **SQS**, a consumer **Lambda** calls **Bedrock** with retries and writes to **S3**.
- "Route short queries to a fast model, technical ones to a reasoning model, code to a code model, evolve rules without app changes, evaluate metrics" → **Step Functions** content-based branching.
- "Synchronous endpoint plus asynchronous batch submissions, decoupled, independently scalable" → **API Gateway** and **Lambda** for synchronous, SDK clients on **ECS** publishing to **SQS** with a **Lambda** consumer for asynchronous.

## Knowledge check

<!-- KC: E1-Q33, E1-Q66, E1-Q53, E2-Q29, PQ-Q8, E2-Q55, E2-Q60, E1-Q32 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 33

A healthcare analytics firm is integrating Amazon Bedrock into its clinical summarization workflow. During peak usage, the team notices intermittent 429 throttling errors and occasional transient network timeouts when invoking the model. The solution must automatically retry failed calls without overwhelming Bedrock, protect downstream systems from excessive traffic, and provide full request-path observability across API calls and retries.

Which approach BEST ensures a resilient and controlled FM invocation workflow?

- **A)** Deploy an EC2-based proxy that batches requests and holds them until Bedrock capacity is available, returning responses only after the full batch is processed.
- **B)** Use the AWS SDK's exponential backoff and jitter for request retries, add API Gateway rate limiting in front of the FM invocation layer, and instrument all calls with AWS X-Ray for end-to-end tracing.
- **C)** Increase the concurrency of the invoking Lambda function and let each function attempt retries independently without rate controls.
- **D)** Implement a custom retry loop inside the application that retries immediately upon failure and logs errors to CloudWatch Logs.

<details><summary>Answer</summary>

**Answer: B.** The SDK's exponential backoff with jitter retries 429s and transient timeouts without flooding Bedrock, API Gateway rate limiting protects downstream systems from excess traffic, and X-Ray traces every call and retry end to end. An EC2 batching proxy adds latency and infrastructure, higher Lambda concurrency with uncontrolled retries amplifies load, and immediate retry loops make throttling worse.

*Where this is covered: Unit 04, Resilience. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 1, question 66

A financial analytics company is building a GenAI-powered summarization service that processes thousands of large PDF reports per hour. Some workloads require synchronous responses from Amazon Bedrock, while others must be processed asynchronously due to long document sizes and unpredictable latency. The solution must support both real-time API clients and background batch processing, enforce request validation, and provide reliable message handling.

Which architecture BEST meets these requirements?

- **A)** Use API Gateway for request validation and synchronous Bedrock invocations, and use Amazon SQS with Lambda workers to process asynchronous requests that call Bedrock in the background.
- **B)** Use Amazon EventBridge to route all traffic to a monolithic container running on Amazon ECS that synchronously invokes Bedrock for every request.
- **C)** Use a single AWS Lambda function to directly invoke Amazon Bedrock for all workloads and store the results in Amazon S3.
- **D)** Use an Amazon EC2 instance to poll PDF files from S3 and directly call Amazon Bedrock through the AWS CLI.

<details><summary>Answer</summary>

**Answer: A.** API Gateway validates requests and fronts the synchronous Bedrock calls for real-time clients, while SQS with Lambda workers processes the long, unpredictable asynchronous requests reliably in the background. A monolithic ECS container behind EventBridge, a single Lambda for everything, and an EC2 poller with the CLI provide neither validation nor reliable asynchronous handling.

*Where this is covered: Unit 04, Three interaction patterns. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 1, question 53

A media analytics startup is developing a real-time script-evaluation assistant that must display generated text to users as soon as the FM begins producing tokens. The engineering team wants to minimize perceived latency, support incremental output delivery to browser clients, and avoid long-running synchronous requests. They also require a standards-based mechanism for maintaining persistent bidirectional connections.

Which solution BEST meets these requirements?

- **A)** Use an ALB in front of a containerized Bedrock proxy service that waits for full responses before returning them to users.
- **B)** Use Amazon SQS long polling to retrieve incremental FM output and push updates to the UI.
- **C)** Use a Lambda function that polls Bedrock until the full response is ready, then returns the complete text to the browser.
- **D)** Use Amazon Bedrock streaming APIs and deliver partial tokens to clients through a WebSocket-based API Gateway endpoint.

<details><summary>Answer</summary>

**Answer: D.** Bedrock streaming APIs return tokens as they are generated, and an API Gateway WebSocket endpoint delivers them to browser clients over a standards-based persistent bidirectional connection with no long-running synchronous request. An ALB-fronted proxy that waits for full responses, SQS long polling, and Lambda polling for the complete text all defeat incremental delivery.

*Where this is covered: Unit 04, Three interaction patterns. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 4. Exam 2, question 29

A digital publishing platform is developing an AI-assisted editorial tool for writers. The tool must analyze draft content on demand and stream revision suggestions directly into a browser-based editor. Articles include metadata labels such as politics, entertainment, and opinion, which determine the editorial rules to apply. Editors require suggestions to begin streaming immediately when they click an “Analyze Draft” button. The company wants to use an Amazon Bedrock FM with custom style guidelines and must minimize operational overhead while supporting real-time, bidirectional communication.

Which architecture will meet these requirements with the LEAST operational overhead?

- **A)** Create an Amazon API Gateway REST API with Lambda function URLs and enable chunked transfer encoding to deliver streaming responses to the editor.
- **B)** Deploy an Amazon API Gateway WebSocket API integrated with an AWS Lambda function. Configure the function to read metadata labels and route requests to the corresponding Amazon Bedrock model and style guide prompts. Use Amazon Bedrock response streaming to push real-time suggestions back to the editor interface.
- **C)** Use Amazon SQS to queue each analysis request and trigger AWS Step Functions workflows. Use Lambda functions for category routing and Bedrock invocations. Store outputs in DynamoDB and push results to clients over WebSocket connections.
- **D)** Run custom containerized services on Amazon ECS behind an Application Load Balancer. Implement metadata-based routing and WebSocket streaming in the containers. Use Bedrock streaming for model-generated suggestions.

<details><summary>Answer</summary>

**Answer: B.** An API Gateway WebSocket API with a Lambda function gives real-time bidirectional communication with the least operational overhead; the function reads the metadata label to select the model and style prompts and uses Bedrock response streaming to push suggestions as they are generated. REST with chunked encoding is one-way and awkward, SQS plus Step Functions plus DynamoDB adds latency and components, and ECS containers behind an ALB mean managing infrastructure.

*Where this is covered: Unit 04, Three interaction patterns. Key: ours, confidence high.*

</details>

### 5. Official practice question set, question 8

A news media company wants to develop a content conformance tool that automatically reviews and adjusts articles to ensure compliance with a style guide. Journalists need a web-based article editor that provides real-time analysis of content upon request.

When journalists click an "analyze" button, the system should immediately begin providing suggested revisions through the editor interface. Articles are tagged with content categories in the metadata. Examples of categories include news, sports, and editorial. The company wants to use an Amazon Bedrock FM to analyze content and provide immediate feedback through the web-based article editor interface.

Which architecture will meet these requirements with the LEAST operational overhead?

- **A)** Create an Amazon API Gateway REST API with AWS Lambda function URLs to enable response streaming. Configure the Lambda function to process articles and stream suggestions using chunked transfer encoding.
- **B)** Deploy an Amazon API Gateway WebSocket API linked to an AWS Lambda function. Configure the function to read the content category from metadata and route content to the appropriate Amazon Bedrock model based on the category tag. Configure the function to use Amazon Bedrock Prompt Management to enforce style guide rules. Use the Amazon Bedrock streaming API to return suggestions in real time.
- **C)** Implement an Amazon SQS queue for article ingestion. Create AWS Step Functions workflows to process content. Use AWS Lambda functions to determine the content category from metadata and invoke appropriate Amazon Bedrock models with style guide prompts. Store results in Amazon DynamoDB. Use an Amazon API Gateway WebSocket API for real-time streaming of suggestions to the journalists.
- **D)** Configure an Application Load Balancer with Amazon ECS tasks that run custom containers. Implement content category routing logic and style guide checking within the containers. Use Amazon Bedrock with streaming support to generate suggestions. Use WebSocket connections to stream results to the journalists in real time.

<details><summary>Answer</summary>

**Answer: B.** An API Gateway WebSocket API linked to a Lambda function streams suggestions in real time with the least operational overhead; the function reads the category tag to route to the right model, enforces the style guide through Bedrock Prompt Management, and uses the Bedrock streaming API. REST with function URLs and chunked encoding lacks the bidirectional real-time channel, SQS plus Step Functions plus DynamoDB adds latency and components, and ECS behind an ALB means managing containers.

*Where this is covered: Unit 04, Three interaction patterns. Key: AWS official answer.*

</details>

### 6. Exam 2, question 55

A fintech startup is building a conversational compliance assistant that interacts with Amazon Bedrock models through a custom API layer. The assistant must provide real-time streamed responses to users, enforce token limits to prevent oversized prompts, and handle occasional model timeouts through controlled retries. The engineering team wants a managed interface that supports request validation, incremental response delivery, and retry-safe error handling without placing this burden on the application servers.

Which solution BEST meets these requirements?

- **A)** Call Bedrock models directly from the application server and implement retry, chunking, and token validation manually in the backend logic.
- **B)** Use Amazon SQS to pass FM requests to a worker fleet of EC2 instances that stream results back to users over long-lived connections.
- **C)** Use Amazon API Gateway to expose a custom FM API with request validation, chunked transfer encoding for streaming Bedrock responses, and an AWS SDK–based retry strategy in integrated Lambda functions.
- **D)** Use AWS AppSync to handle streaming requests and enforce token limits before invoking the Bedrock model directly.

<details><summary>Answer</summary>

**Answer: C.** API Gateway exposes a custom FM API with request validation for token limits, chunked transfer encoding to stream Bedrock responses incrementally, and integrated Lambda functions that apply the SDK's retry strategy for model timeouts, keeping the burden off application servers. Direct calls with manual logic in the backend, an EC2 worker fleet behind SQS, and AppSync invoking Bedrock directly do not provide that managed validation, streaming and retry layer.

*Where this is covered: Unit 04, API Gateway features you will be tested on. Key: ours, confidence high.*

</details>

### 7. Exam 2, question 60

A healthcare research startup is building an application that processes large clinical reports and generates AI-powered summaries. Users upload documents through an API backed by AWS Lambda. The API stores each uploaded document in an Amazon S3 bucket.

The company wants to use a pre-trained foundation model (FM) in Amazon Bedrock to summarize each report. Summaries must be written back to Amazon S3, and users will retrieve them through the same API. Users are willing to wait up to 24 hours to receive results. The workload will experience unpredictable spikes in traffic, and the solution must remain scalable, fault tolerant, and cost-efficient.

Which approach will meet these requirements in the MOST cost-effective way?

- **A)** Use the ingestion Lambda function to invoke an AWS Step Functions workflow with multiple parallel Lambda tasks. Configure each task to call the Amazon Bedrock API and write the summary to Amazon S3 with workflow-managed retries.
- **B)** Use the ingestion Lambda function to call the Amazon Bedrock InvokeModel API synchronously for each document upload. Return the summary directly to the user and store the result in Amazon S3.
- **C)** Use the ingestion Lambda function to publish a message to an Amazon SQS queue. Configure another Lambda function to poll the queue, call the Amazon Bedrock InvokeModel API to summarize each document, and store the results in Amazon S3 with retries enabled.
- **D)** Modify the ingestion Lambda function to batch uploaded documents into an Amazon SQS queue. Use a batch window to send batched requests to a custom Bedrock batch inference workflow.

<details><summary>Answer</summary>

**Answer: C.** Publishing each upload to an SQS queue and letting a consumer Lambda function call Bedrock and write to S3 with retries decouples ingestion from model latency, absorbs unpredictable spikes, tolerates failures through the queue and dead-letter handling, and costs only per use. Synchronous invocation blocks users and fails under spikes, a Step Functions fan-out is heavier than a queue for independent documents, and the SQS-batched 'custom Bedrock batch inference workflow' adds custom orchestration. Note that a plain Bedrock batch inference job would be the cheapest path when users truly accept a 24-hour delay; the option here describes a custom workflow, which is why the queue-based design is keyed.

*Where this is covered: Unit 04, Three interaction patterns. Key: ours, confidence medium.*

</details>

### 8. Exam 1, question 32

A global e-learning company is building an AI content-processing service that uses multiple Amazon Bedrock models for different tasks. Short user queries should be routed to a fast, low-latency LLM; long or technical queries should be routed to a larger, reasoning-optimized FM; and any requests containing code snippets should be sent to a code-specialized FM. The team requires a centralized mechanism that can run logic based on request content, apply conditional routing rules, evaluate model performance metrics over time, and easily evolve the routing logic without modifying the application code.

Which solution BEST meets these routing and maintainability requirements?

- **A)** Use AWS Step Functions with content-based branching to inspect the request payload and route it to the correct Bedrock model, combined with metric-based routing updates managed as state machine revisions.
- **B)** Hardcode routing logic into the backend service and deploy a new version whenever routing rules or model selection criteria must be updated.
- **C)** Store routing rules in Amazon S3 and have the application load them at runtime to decide which Bedrock model to invoke.
- **D)** Use API Gateway request transformations to parse user requests and route them directly to different Lambda functions, each calling a different FM.

<details><summary>Answer</summary>

**Answer: A.** Step Functions content-based branching inspects each request (length, technical content, code snippets) and routes it to the matching Bedrock model, and routing rules evolve as state machine revisions with performance metrics feeding updates, all without touching application code. Hardcoded backend logic needs redeployment, rules in S3 still require application logic to interpret them, and API Gateway transformations to per-model Lambda functions cannot evaluate metrics or evolve easily.

*Where this is covered: Unit 04, Routing requests to the right model. Key: ExamPro answer key (Exam 1 graded).*

</details>

<!-- KC-END -->

## Summary

Choose the interaction pattern from the user's patience: **API Gateway** and **Lambda** to **Bedrock** for synchronous requests with validation and **throttling**, **SQS** with **Lambda** consumers (**visibility timeouts**, **dead-letter queues**) or **Step Functions** for asynchronous work, and **Bedrock streaming** delivered over **API Gateway WebSocket APIs**, **Lambda response streaming** or **server-sent events** for real-time output.

Make it resilient with the SDK's **exponential backoff and jitter**, **API Gateway** **rate limiting**, **circuit breakers** with explicit fallback tiers, and **X-Ray** tracing across every hop. Route with configuration for static rules, **Step Functions** **Choice states** for content-based and evolving rules, stored metrics for objective-driven selection, **API Gateway** transformations for header-based selection, and **intelligent prompt routing** or cascading when a managed router fits.
