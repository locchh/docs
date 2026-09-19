# Unit 02: Select and configure FMs

**Task 1.2: Select and configure FMs.** Four skills sit under it:

- Assess and choose models with evidence, through benchmarks, capability analysis and limitation analysis.
- Build flexible architectures that switch models or providers without code changes, using **Lambda**, **API Gateway** and **AWS AppConfig**.
- Design for resilience when a model or Region misbehaves, with **cross-Region inference**, **Step Functions** circuit breakers and graceful degradation.
- Manage fine-tuned models through their lifecycle, using **SageMaker AI**, **LoRA** adapters, **Model Registry**, automated pipelines, rollback and retirement.

## The model landscape on Bedrock

**Bedrock**'s catalog groups models by provider, and each provider offers a ladder of sizes that trade capability for cost and speed.

- **Anthropic**'s **Claude** family is strong at reasoning, long documents, tool use and image understanding. **Haiku** is fast and cheap, **Sonnet** balanced, **Opus** most capable.
- **Amazon Nova** is Amazon's own family: **Micro** for text at lowest latency, **Lite** and **Pro** multimodal, **Premier** most capable. Alongside it sit **Nova Canvas** for images, **Nova Reel** for video and **Nova Sonic** for speech.
- **Amazon Titan** covers text generation, text and multimodal embeddings, and image generation.
- **Meta Llama** models are open-weight, widely fine-tuned, and available in several sizes.
- **Mistral** offers efficient open models, and **Pixtral** for vision.
- **Cohere** provides **Command** for generation, **Embed** for embeddings and **Rerank** for reranking.
- **AI21 Jamba** has a very long context window, **DeepSeek R1** is a reasoning model, and **Stability AI** supplies image generation.

Capability analysis means asking concrete questions of a candidate:

- What is its context window, which runs from a few thousand tokens to hundreds of thousands?
- Which modalities does it accept and produce?
- Does it support tool use and structured output?
- Which languages does it handle well?
- What is its knowledge cutoff?
- How fast does it produce tokens?
- What does it cost per thousand input and output tokens?

A cheaper, smaller model that meets the bar is the right answer. The exam penalises "pick the largest or newest model" as much as "pick the cheapest without testing".

## Choosing with evidence

Skill 1.2.1 is a method, and questions reward the option that follows it.

Start by mapping requirements to capabilities: reasoning depth, domain vocabulary, multilingual support, structured output, image input, latency budget.

Then benchmark. Public leaderboards and provider model cards give a first cut. They include **MMLU** for knowledge, **HELM** for holistic evaluation and the **LMArena** human-preference leaderboard. The exam, though, wants you to evaluate on your own task.

**Amazon Bedrock model evaluation** runs evaluation jobs in three styles:

- **Automatic evaluation** with built-in or custom prompt datasets, and metrics such as accuracy, robustness and toxicity.
- **LLM-as-a-judge**, where a second model scores responses against criteria you define, such as correctness, completeness, faithfulness, harmfulness and style. It scales far better than people.
- **Human evaluation** with your own workforce, for subjective qualities.

**Bedrock** also evaluates **Knowledge Bases** for retrieval and generation quality. The playground's compare mode is the quick, manual version of the same idea.

Limitation analysis follows. Probe edge cases, measure hallucination rate on questions with known answers, check behaviour on rare terminology, and note refusals and the knowledge cutoff. Finally weigh cost and performance together, across accuracy, latency, throughput and price per request, and document the rationale so the choice can be revisited when a new model appears.

Two details recur in questions. **Robustness** in **Bedrock** evaluation measures how much answers change when prompts are lightly reworded, which is exactly what you use when a model gives different advice for the same question phrased differently. And evaluation belongs before deployment: a model evaluation job is not a runtime safety control.

## Inference options

Once a model is chosen you decide how to buy its capacity. This table is worth memorising.

| Option | How it works | When it is the answer |
|---|---|---|
| **On-demand** | Pay per input and output token, no commitment, shared capacity subject to per-model quotas (requests and tokens per minute) | Default for variable workloads and PoCs |
| **Cross-Region inference** | Call an *inference profile* instead of a model ID; **Bedrock** routes each request to a Region in the profile with capacity. Geographic profiles stay inside US, EU or APAC; global profiles use any commercial Region. Same API, billed at the source Region's price. Governance: geographic profiles plus a **service control policy** (an **AWS Organizations** rule that caps what accounts may do) that denies the global profiles keep inference inside the geography, and **CloudTrail** records the Region that served each request in its `inferenceRegion` field | "Too many requests" during peaks, higher throughput, resilience to a Regional slowdown, without extra infrastructure. Choose geographic when data residency matters |
| **Provisioned Throughput** | Buy **Model Units** for guaranteed tokens-per-minute capacity, billed hourly, with no commitment or a 1- or 6-month term for a discount. Required to serve many customised models | Steady, predictable, high volume; production fine-tuned models. Cannot be combined with **inference profiles** |
| **Batch inference** | Upload **JSONL** prompts (**InvokeModel** or **Converse** format) to **S3**, run an asynchronous job, read results from **S3**, at a discount (currently half of on-demand). No tool use or structured output; quotas on records and file size per job | Large offline jobs where hours of delay are acceptable |
| **Latency-optimized inference** | Set `performanceConfig.latency` to `optimized` on a supported model; **Bedrock** serves the request from faster infrastructure through **cross-Region inference**, at a higher per-token price | Interactive use where time to first token is the requirement |
| **Prompt caching** | Mark a cache checkpoint after a long static prefix (system prompt, tool definitions, a reference document); **Bedrock** reuses the processed prefix for later requests within about five minutes, charging cached input tokens at a large discount and cutting latency. Minimum prefix lengths apply per model; on-demand only. Newer models add implicit caching without explicit checkpoints and a one-hour cache option, and writing to the cache can cost more than standard input tokens | "Same long preamble sent on every call", "rising cost and latency for repeated context" |
| **Intelligent prompt routing** | A **router endpoint** predicts which model *within one family* (**Anthropic**, **Meta** or **Nova**) will answer well enough and sends easy prompts to the smaller model, hard ones to the larger, with a configurable quality threshold and fallback model | "Simple and complex queries mixed, minimise cost, keep quality, minimal operational overhead" |

A throttling error on **Bedrock** ("Too many requests, please wait before trying again", `ThrottlingException`) has three legitimate cures:

- Retry with **exponential backoff and jitter** in the SDK.
- Move to a **cross-Region inference** profile.
- Buy **Provisioned Throughput**.

The most cost-effective fix that keeps the same model and API is **cross-Region inference**.

Two more strategies appear in the Skill Builder review and occasionally in questions.

**Model ensembling** sends the same prompt to several models and combines the answers, by majority vote for classifications or with a judge model or scoring rule for free text. It gains accuracy and resilience at a multiple of the cost.

**Fallback models** keep the application answering when the primary model is throttled or unavailable. The SDK call catches the error and retries against a second model or Region.

## Inference parameters

Every model exposes a similar set of knobs, and the `Converse` API names them consistently:

- `maxTokens` caps the response length.
- `temperature` and `topP` control randomness.
- `stopSequences` lists strings that end generation the moment the model emits them.
- **Top-k**, which means choosing among the k most likely tokens, is model specific and passed in `additionalModelRequestFields`.

**Temperature** reshapes the probability distribution. Low values, 0 to 0.3, make the model pick the most likely tokens and give consistent, factual, repeatable output. High values, 0.7 and above, flatten the distribution for creative variety. **Top-p** restricts sampling to the smallest set of tokens whose probabilities add up to p. Adjust one of the two, not both.

A temperature of 0 does not guarantee identical outputs across calls. So "set temperature to 0 for perfectly standardised output" is a distractor when the requirement is consistency with some variation. The tested answer is a lower temperature with moderate **top-p**, validated by **A/B testing** of parameter profiles.

**Stop sequences** are the tool when the requirement is "stop generating when a phrase such as END_OF_SECTION appears". Putting the instruction in the prompt is unreliable, and adjusting temperature or **top-k** does not stop anything.

## Switching models without code changes

Skill 1.2.2 is one architecture, drawn many ways in questions: **API Gateway → Lambda router → AWS AppConfig → model-specific invocation**. The router reads the active model, provider and parameters from **AppConfig** at runtime, and normalises the request and response so callers never see which model answered.

**AWS AppConfig** is the piece candidates miss. It stores feature flags and free-form configuration, and it does four more things:

- It validates a new configuration before deployment, with a JSON schema or **Lambda** validators.
- It rolls the change out gradually with a deployment strategy and bake time.
- It rolls back automatically if a **CloudWatch** alarm fires during the rollout.
- It is read through the **AppConfig Agent** or **Lambda** extension, which cache locally, so a change propagates in seconds with no redeploy.

**Feature flags** give you gradual rollout of a new model to a slice of users, **A/B tests** between models, and instant rollback.

The distractors each fall short. **Systems Manager Parameter Store** can hold the same string but has no validation, staged rollout or alarm-based rollback. Environment variables and **S3** files read at cold start need a redeploy to change. Separate API stages per model push the choice onto clients.

Two **Bedrock** features reduce how much of this you must build. The `Converse` API already normalises request and response shape across chat models, so the adapter layer shrinks to model IDs and parameters. And **intelligent prompt routing** is a managed router when the choice is between sizes within one model family.

**Step Functions** is the alternative when routing is one step in a larger workflow. A **Choice state** inspects the request type and invokes the matching model, behind a single **API Gateway** endpoint with request transformations. It suits "route by task type, add models later without changing the client API" as well as the **Lambda** router does. The difference is that **Step Functions** also gives you retries, branching and execution history.

## Designing for failure

Skill 1.2.3 asks for continuous operation when a model is throttled, slow, or unavailable in its only Region.

**Cross-Region inference** is the first answer for both capacity and Regional disruption, because the routing happens inside **Bedrock**. Choose it when a model has limited Regional availability, when a Region is degraded, or when peaks exceed on-demand quotas.

**Retries with exponential backoff and jitter** handle transient errors and throttling in the SDK. **API Gateway** per-client throttling limits stop bursts before they reach **Lambda**.

**Circuit breakers in Step Functions** protect against repeated failures. A **Task state** calling **Bedrock** has a **Retry** policy, which sets the interval, the maximum attempts and the backoff rate, and a **Catch** that routes to a fallback branch when retries are exhausted or when timeouts and throttling repeat.

The fallback branch has three options. It tries a smaller model, returns a cached or rules-based response, or sends the request to a human queue instead of failing the user. A **Choice state** can also enforce stopping conditions on output length, and **Lambda** timeouts cap downstream processing, so runaway generations do not stall the workflow.

**Graceful degradation** means capability tiers:

- The primary model.
- A cheaper fallback model.
- Cached responses for known queries.
- A deterministic rules-based answer as the last resort.

Complete shutdown, serving cached responses for everything, or routing all traffic to one generic model are the distractors.

**Multi-Region active-passive** completes the picture when the entire application stack, not just the model, must survive a Regional outage. Deploy the stack in two Regions and use **Route 53** failover records with health checks. **Cross-Region inference** alone covers the model, not your **Lambda** functions and databases.

Monitor all of it with **CloudWatch** metrics and alarms on **Bedrock** invocation errors, latency and throttles, so remediation triggers before users notice.

## Customising models and managing their lifecycle

Skill 1.2.4 is where **SageMaker AI** enters. Know both customisation paths and the operational machinery around them.

**Customising in Bedrock.** **Bedrock** offers five customisation paths:

- **Supervised fine-tuning** on labelled prompt-response pairs.
- **Reinforcement fine-tuning** that optimises against feedback.
- **Continued pre-training** on unlabelled domain text, for supported models.
- **Model distillation**, which generates responses from a large teacher model, optionally from your invocation logs, and fine-tunes a cheaper student.
- **Custom Model Import**, which brings weights you fine-tuned elsewhere from **S3** or **SageMaker** into **Bedrock** and serves them on demand. Supported architectures include **Llama**, **Mistral**, **Mixtral** and **Flan-T5** in **Hugging Face** format.

Training data is **JSONL** in **S3**, encrypted with your **KMS** key if required, and jobs run inside a **VPC** if you configure one. Customised models are served through **Provisioned Throughput**, with on-demand serving available for imported and some newer custom models, and the resulting model is private to your account.

**Customising in SageMaker AI.** When you need full control, fine-tune in **SageMaker** with parameter-efficient techniques.

**LoRA (Low-Rank Adaptation)** freezes the base weights and trains small rank-decomposition matrices. That cuts compute and memory, avoids catastrophic forgetting, and produces a small adapter file that can be swapped or combined. **QLoRA** **quantises** the base model to shrink memory further, which means storing its weights with fewer bits, such as 4-bit instead of 16-bit, trading a little precision for much less memory. Adapters are the general family.

**SageMaker JumpStart** offers fine-tuning recipes for open models, and **Hugging Face** containers and **HyperPod**, **SageMaker**'s managed cluster for large-scale training, handle larger jobs.

To serve many adapters cheaply, deploy the base model once to a **SageMaker** real-time endpoint and register each **LoRA** adapter as its own **inference component**. The endpoint loads the requested adapter in milliseconds, and callers name the adapter per request. That is the answer to "personalise per region with **LoRA** adapters without separate endpoints".

**Versioning and approval.** **SageMaker Model Registry** organises models into **model package groups**. It registers each fine-tuned version with metadata such as domain, task, dataset and **LoRA** configuration, tracks lineage from data to endpoint, and carries an approval status of `PendingManualApproval`, `Approved` or `Rejected`. Only approved versions are promoted. A custom **DynamoDB** registry or a shared spreadsheet is always the wrong answer.

**Automated deployment and rollback.** **SageMaker Pipelines** plus **CodePipeline** and **CodeBuild** pull the latest approved version, run evaluations, and deploy with blue/green, canary or linear traffic shifting to **SageMaker** endpoints, rolling back automatically when **CloudWatch** alarms fire.

Here are the release patterns once, since they recur through the path:

- **Blue/green** stands up the new version beside the old and switches traffic at once, keeping the old for rollback.
- **Canary** sends a small share of traffic to the new version first and ramps up if metrics hold.
- **Linear** adds a fixed share at fixed intervals.
- A **shadow** deployment mirrors traffic to the new version without serving its answers.
- An **A/B test** splits traffic between variants to compare them.

**Production variants** on one endpoint let you send a small weight of live traffic to a new model and shift it gradually. **Lambda aliases** with weighted routing do the same for **Lambda**-fronted models.

**Monitoring and retirement.** **SageMaker Model Monitor** watches data quality and drift on live traffic, including embedding drift with a custom container, and **Clarify** covers bias and explainability.

Lifecycle management sets evaluation schedules, update criteria and retirement rules. Tag deprecated versions, remove them on a schedule, and keep clients pointed at a stable endpoint or alias so retirement is invisible to them.

## Worked scenario

A global retailer generates product descriptions in twelve languages, answers merchandiser questions about catalogue data, and wants one platform for both. The team must pick models, buy capacity sensibly, survive Regional throttling during seasonal peaks, and manage a fine-tuned variant that writes in the house style.

Selection starts with evidence, not preference. The team assembles two hundred representative prompts per task: multilingual descriptions, and catalogue questions with known answers. It runs **Amazon Bedrock Evaluations** against three candidate models, with automatic metrics for accuracy and toxicity and an **LLM-as-a-judge** job for style and completeness, and records cost per thousand tokens and latency beside the scores.

A mid-size model wins the descriptions on quality per dollar, and a larger model wins the catalogue questions. Inference parameters follow the task: a low temperature and a stop sequence for factual catalogue answers, a higher temperature and a token cap for marketing copy.

Capacity follows the traffic shape.

- Merchandiser questions are interactive and variable, so they run on demand through a **cross-Region inference** profile scoped to the EU geography, which absorbs peaks without moving data outside Europe.
- The nightly regeneration of a million descriptions is a **batch inference** job at the discounted price.
- The steady daytime description service, whose latency matters, gets a small **Provisioned Throughput** commitment for its base load, with on-demand covering the rest.

Model identifiers, prompt versions and parameters live in **AWS AppConfig** and are read at runtime by a **Lambda** router behind **API Gateway**, so switching providers or promoting a new model version is a configuration change, not a deployment. For failure, a **Step Functions** workflow wraps the call with retries, a **circuit breaker** that opens after repeated throttling, and a fallback to a smaller model with a degraded but honest response.

The house-style variant is a **LoRA** adapter fine-tuned in **SageMaker**. It is registered in the **SageMaker Model Registry** with an approval status, promoted by a CI/CD pipeline only after the evaluation job clears the baseline, served beside the base model as an **inference component**, and rolled back automatically when production alarms fire. Retire old adapters when their metrics fall behind.

The exam's version of this scenario asks for the combination that selects with evidence, switches without code changes, keeps operating through throttling, and governs the fine-tuned lifecycle. Each of those phrases names one of the pieces above.

## Exam lens

Task 1.2 questions come in four recognisable shapes.

*Selection questions* describe requirements, such as SQL accuracy, biomedical terminology or low hallucination, and ask how to choose. The answer is always "evaluate candidates with structured benchmarks and **Bedrock** evaluation against the requirements". The distractors are newest, largest, cheapest or biggest context window by assumption.

*Switching questions* ask for model or provider changes "without code changes or redeployment". The answer contains **AppConfig** read at runtime behind an **API Gateway** and **Lambda** router.

*Resilience questions* mention a model available in one Region, throttling during peaks, or "must keep operating". Look for **cross-Region inference** plus a **Step Functions** circuit breaker and graceful degradation. Reject "retry the same Region forever", "single **EC2** with auto scaling" and "replace **Bedrock** with self-hosted models".

*Lifecycle questions* mention fine-tuned variants, **LoRA**, approval, rollback and retirement. The answer combines **Model Registry** with approval status and a CI/CD pipeline with automated rollback. Multi-adapter **inference components** appear when many adapters share one base model.

## Knowledge check

<!-- KC: E1-Q43, E3-Q52, E1-Q27, E3-Q61, E2-Q62, PQ-Q12, E3-Q24, E1-Q10, E3-Q5, E2-Q48 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 43

A healthcare analytics company is building an internal generative AI assistant to help data analysts summarize clinical trial reports, extract structured findings, and generate risk assessments for research teams. The AI engineering team wants to test several Amazon Bedrock models to identify which FM provides the best accuracy when handling long biomedical texts, the lowest hallucination rate, and the strongest performance on domain-specific terminology. They must select a model that aligns with strict compliance requirements and produces reliably factual outputs.

The lead AI engineer must determine the BEST approach to select the most appropriate foundation model before finalizing the architecture.

Which approach should the engineer take?

- **A)** Run performance benchmarks across multiple Amazon Bedrock foundation models by evaluating accuracy, latency, hallucination rate, and domain-specific capability to determine which model best meets the business and technical requirements.
- **B)** Select a biomedical third-party API outside AWS to bypass internal benchmarking efforts and rely on vendor marketing claims for expected performance.
- **C)** Select the smallest, fastest foundation model from Amazon Bedrock to reduce inference cost and maximize system responsiveness, regardless of domain performance characteristics.
- **D)** Choose a single general-purpose model based on initial impressions and avoid extensive testing to reduce development time during the prototype phase.

<details><summary>Answer</summary>

**Answer: A.** Model selection is an evaluation exercise: benchmark candidate Bedrock models on accuracy, latency, hallucination rate and domain terminology against the requirements. Relying on vendor claims, picking the smallest model regardless of domain performance, or choosing on first impressions all skip the evidence.

*Where this is covered: Unit 02, Choosing with evidence. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 3, question 52

A retail analytics company is developing a generative AI assistant that interprets sales reports, summarizes trends, and generates SQL queries to help analysts explore data. The engineering team must select a foundation model (FM) for Amazon Bedrock that aligns with the company’s key requirements:

- strong performance on analytical reasoning tasks
- high accuracy in generating syntactically correct SQL
- well-documented limitations and benchmark transparency
- predictable latency for interactive use

The company wants to choose the FM based on empirical evaluation, structured capability comparisons, and alignment with the workload’s constraints.

Which approach will allow the team to choose the MOST appropriate FM for these requirements?

- **A)** Evaluate multiple Bedrock FMs by using Bedrock evaluation tools with structured benchmarks for reasoning, SQL generation accuracy, latency measurements, and failure-case analysis. Select the model that best matches the business requirements.
- **B)** Choose the latest and most expensive FM from Bedrock on the assumption that newer models always outperform earlier versions and generalize better to analytical tasks.
- **C)** Pick the FM that is cheapest per 1,000 tokens to minimize costs and assume that lower inference cost will not impact SQL correctness or reasoning ability.
- **D)** Select the FM with the largest context window to ensure that the model can handle more input tokens, assuming this will automatically improve SQL accuracy and reasoning.

<details><summary>Answer</summary>

**Answer: A.** Evaluating candidate FMs with Bedrock evaluation tools using structured benchmarks for reasoning, SQL accuracy, latency and failure cases selects the model on evidence aligned to the workload. Newest, cheapest and largest context window are assumptions the question explicitly rejects.

*Where this is covered: Unit 02, Choosing with evidence. Key: ours, confidence high.*

</details>

### 3. Exam 1, question 27

A logistics technology company is building a generative AI assistant that supports multiple use cases, including shipment delay explanations, route optimization suggestions, and contract summary generation. The engineering team wants the ability to switch between different Amazon Bedrock models—such as one optimized for summarization and another for reasoning—without redeploying code. They also want the flexibility to switch model providers entirely as new FMs become available.

The lead AI engineer must design an architecture that supports dynamic model selection, configuration-driven switching, and zero code modifications during updates.

Which approach BEST meets these requirements?

- **A)** Deploy all required foundation models in parallel and use an Amazon EC2 instance to manually route requests by updating environment variables on the instance.
- **B)** Use multiple separate API Gateway endpoints, each dedicated to a single foundation model, and require clients to select the correct endpoint for their use case.
- **C)** Create a routing layer using Amazon API Gateway and AWS Lambda, and store model selection parameters in AWS AppConfig so that model and provider choices can be switched dynamically without changing application code.
- **D)** Hardcode the preferred foundation model into the Lambda function and update the code each time the model or provider changes.

<details><summary>Answer</summary>

**Answer: C.** API Gateway and Lambda form the routing layer and AWS AppConfig holds the model and provider selection, so a configuration change switches models with zero code modification and no redeploy. EC2 environment variables, one endpoint per model that clients must choose, and hardcoded model IDs all require manual or code changes.

*Where this is covered: Unit 02, Switching models without code changes. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 4. Exam 3, question 61

A media intelligence platform uses multiple foundation models (FMs) from Amazon Bedrock for tasks such as summarization, classification, and content rewriting. The engineering team wants to switch between different FMs and even different providers without deploying new code. The platform currently routes all inference requests through a shared AWS Lambda function that is invoked by an Amazon API Gateway endpoint. The company wants to introduce a mechanism that allows product teams to adjust FM selection in real time during experimentation, failover, or regional capacity constraints. The solution must avoid code changes, deployments, or service interruptions while allowing controlled configuration updates.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Use Amazon DynamoDB to store multiple FM routing rules. Require the engineering team to manually update environment variables and redeploy the Lambda function after each FM change.
- **B)** Use Amazon S3 to store a JSON configuration file that contains the active FM name. Configure the Lambda function to download and cache the file on cold start, updating only when the function is redeployed.
- **C)** Create multiple API Gateway stages, each mapped to a different FM provider. Instruct clients to switch between stages based on which model they want to use.
- **D)** Use AWS AppConfig to store the active FM and provider configuration. Have the Lambda function read the AppConfig value at runtime to determine which model to invoke, enabling dynamic FM switching without code changes.

<details><summary>Answer</summary>

**Answer: D.** AWS AppConfig stores the active FM and provider, and the Lambda function reads it at runtime, so product teams switch models dynamically for experiments, failover or capacity constraints with no code change, deployment or interruption. DynamoDB plus redeploys, an S3 file read only at cold start, and per-model API Gateway stages all require redeployment or client changes.

*Where this is covered: Unit 02, Switching models without code changes. Key: ours, confidence high.*

</details>

### 5. Exam 2, question 62

A multinational logistics intelligence company operates a generative AI routing assistant on Amazon Bedrock to optimize fleet movement and provide real-time delivery guidance. During peak shipping seasons, the assistant receives unpredictable surges of inference traffic from users in South America and Southeast Asia. The company must maintain consistently low-latency responses while ensuring all inference requests remain compliant with strict regional data residency requirements.

The engineering team wants a solution that minimizes operational overhead, avoids deploying and managing separate FM instances in every region, and automatically uses available compute capacity across regions when demand spikes.

Which solution will best meet these requirements?

- **A)** Use the Bedrock cross-region inference profile so that inference calls from one region are automatically routed to another region with available compute capacity.
- **B)** Use SageMaker AI multi-region inference endpoints and manage routing with Amazon Route 53 latency-based rules.
- **C)** Deploy separate Bedrock foundation model instances in each active region and route callers using a custom latency-aware client SDK.
- **D)** Pre-copy all interaction logs and prompts to multiple regions and perform FM inference in the nearest region to the end user.

<details><summary>Answer</summary>

**Answer: A.** A Bedrock cross-Region inference profile automatically routes requests to Regions with available capacity during surges, with no separate model instances to manage, and geographic profiles keep data within the required geography for residency. SageMaker multi-Region endpoints with Route 53, separate Bedrock deployments with a custom SDK, and pre-copying logs all add infrastructure and operations.

*Where this is covered: Unit 02, Inference options. Key: ours, confidence high.*

</details>

### 6. Official practice question set, question 12

An ecommerce company has an application that uses Amazon Bedrock to generate product descriptions and recommendations. Currently, the application resides in a single AWS Region. When invoking a model in Amazon Bedrock during peak periods, the application receives an error. The error message says, "Too many requests, please wait before trying again."

The company must increase the throughput for invocations during peak periods without introducing additional operational overhead. The company must maintain compatibility with the existing Amazon Bedrock API. The company must use the same FM.

Which solution will meet these requirements in the MOST cost-effective way?

- **A)** Use cross-Region inference to distribute traffic across multiple Regions within a geographic area.
- **B)** Create an AWS Lambda function to invoke the model in Amazon Bedrock with the original Region as the default. Configure the Lambda function to fall back to Amazon Bedrock in a secondary Region.
- **C)** Use provisioned throughput to provision a higher level of throughput for the FM.
- **D)** Use prompt routing to distribute traffic across multiple FMs from the same family.

<details><summary>Answer</summary>

**Answer: A.** Cross-Region inference distributes requests across Regions in the geography with the same model and API, removing peak-time throttling at on-demand prices with no extra infrastructure. A Lambda fallback adds custom code, Provisioned Throughput costs more, and prompt routing changes the model.

*Where this is covered: Unit 02, Inference options. Key: AWS official answer.*

</details>

### 7. Exam 3, question 24

A fintech startup is building a generative AI platform that produces regulatory summaries, extracts compliance risks, and generates audit-ready narratives using multiple Amazon Bedrock foundation models. One of the selected models is available only in a single AWS Region, and the team is concerned about potential service disruptions affecting customer workloads. The business requires the system to continue operating even if a model becomes temporarily unavailable or if latency increases unexpectedly.

The lead AI engineer must design a resilient architecture that maintains functionality, handles disruptions gracefully, and automatically fails over when needed.

Which approach BEST meets these requirements?

- **A)** Configure Amazon Bedrock Cross-Region Inference with a fallback Region and integrate AWS Step Functions circuit breaker patterns to reroute requests during failures while degrading gracefully when the primary model is unavailable.
- **B)** Deploy all inference logic on a single Amazon EC2 instance in the Region where the model is available and rely on auto scaling to recover from outages.
- **C)** Replace all Bedrock models with open-source models hosted in a self-managed Kubernetes cluster to avoid relying on regional model availability.
- **D)** Add retries with exponential backoff directly inside the client application and continue sending requests to the same Region until the model becomes responsive again.

<details><summary>Answer</summary>

**Answer: A.** Cross-Region inference with a fallback Region covers a model available in one Region, and Step Functions circuit breaker patterns reroute during failures and degrade gracefully when the primary model is unavailable. A single EC2 instance, self-managed Kubernetes replacing Bedrock, and endless retries against the same Region do not provide failover.

*Where this is covered: Unit 02, Designing for failure. Key: ours, confidence high.*

</details>

### 8. Exam 1, question 10

A pharmaceutical research organization is building domain-specific generative AI models to summarize clinical studies, extract trial outcomes, and generate structured regulatory reports. The AI engineering team fine-tunes several Amazon Bedrock-compatible foundation models using Amazon SageMaker AI with LoRA adapters. They need a lifecycle approach that allows them to register new fine-tuned versions, deploy them safely, automatically roll back if accuracy drops, and retire outdated model variants that no longer meet compliance standards.

The lead ML engineer must implement a standardized deployment and lifecycle workflow that minimizes risk and ensures consistent version control across environments.

Which approach BEST meets these requirements?

- **A)** Upload each fine-tuned model as a separate container image to Amazon ECR and switch between them by updating the endpoint configuration manually.
- **B)** Use SageMaker Model Registry to track and version fine-tuned models, deploy them through automated CI/CD pipelines with rollback support, and manage lifecycle transitions to retire or promote model versions.
- **C)** Store each fine-tuned model manually in Amazon S3 with timestamped folder names and deploy them by updating a Lambda function environment variable.
- **D)** Use a single SageMaker endpoint and overwrite the model artifacts in-place whenever a new fine-tuned version is produced.

<details><summary>Answer</summary>

**Answer: B.** SageMaker Model Registry versions the fine-tuned models with approval status and lineage, CI/CD pipelines deploy approved versions with rollback, and lifecycle rules retire old variants. Manual ECR image switching, timestamped S3 folders with Lambda environment variables, and overwriting artifacts in place have no versioning, approval or safe rollback.

*Where this is covered: Unit 02, Customising models and managing their lifecycle. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 9. Exam 3, question 5

A fintech startup is building several domain-specific variants of a foundation model (FM) for tasks such as regulatory report drafting, fraud-case summarization, and customer-chat assistance. The team fine-tunes base models on Amazon SageMaker AI by using LoRA adapters and wants to promote only validated versions into production. They must standardize how new FM variants are registered, approved, deployed to SageMaker endpoints, and rolled back if issues are detected. They also need a repeatable mechanism to deprecate older variants and retire them without breaking clients that call the production endpoint. The team wants to minimize manual operations and ensure consistent behavior across multiple environments (dev, staging, prod).

Which combination of steps will provide a standardized and automated FM customization lifecycle? (Select TWO.)

- **A)** Create an automated CI/CD pipeline by using SageMaker Pipelines and AWS CodePipeline that pulls the latest Approved model versions from SageMaker Model Registry, deploys them with blue/green or canary strategies to SageMaker endpoints, monitors CloudWatch alarms, and rolls back to the previous version on failures. Tag deprecated model versions for retirement and remove them on a scheduled basis.
- **B)** Manually update SageMaker endpoint configurations whenever a new FM variant is trained. Track model versions in a shared spreadsheet and perform rollback by redeploying the previous model artifact from Amazon S3 as needed.
- **C)** Use SageMaker Model Registry to register every fine-tuned FM variant with versioned packages, approval status (for example, Pending, Approved, Rejected), and metadata such as domain, LoRA config, and training dataset identifiers. Promote only Approved versions to production.
- **D)** Use Amazon Bedrock provisioned throughput configurations for all domain-specific FMs and rely on manual prompt-level flags to distinguish between fraud, regulatory, and customer-chat use cases instead of maintaining separate model versions.
- **E)** Store LoRA adapter weights exclusively in Amazon S3 with timestamped folder names. Use an AWS Lambda function that selects the adapter with the most recent timestamp at runtime and loads it into the model container without any registry or approval workflow.

<details><summary>Answer</summary>

**Answer: A, C.** Model Registry registers every LoRA-tuned variant with versions, approval status and metadata so only Approved versions are promoted, and a SageMaker Pipelines and CodePipeline CI/CD pipeline deploys them with blue/green or canary strategies, rolls back on alarms, and retires deprecated versions on a schedule. Spreadsheets, prompt-level flags on Provisioned Throughput, and timestamp-based adapter loading have no approval or rollback.

*Where this is covered: Unit 02, Customising models and managing their lifecycle. Key: ours, confidence high.*

</details>

### 10. Exam 2, question 48

A multinational retailer is building a multilingual generative support assistant using Amazon SageMaker Unified Studio and SageMaker JumpStart. The team deployed a large foundation model to a single SageMaker AI real-time endpoint and wants to personalize behavior for several regional markets using lightweight LoRA adapters. The base model must remain unchanged, and the team wants to avoid maintaining separate endpoints for each region. The solution must allow the inference call to specify which regional adapter to apply.

Which solution will meet this requirement?

- **A)** Create a SageMaker multi-model endpoint and package each region’s LoRA adapter as a separate model, relying on container routing to select the adapter.
- **B)** Mount an Amazon EFS volume that stores all LoRA adapters and dynamically load the correct file at runtime inside the endpoint container.
- **C)** Use an AWS Lambda step to load the correct regional LoRA weights from Amazon S3 and inject them into the model container before the inference request.
- **D)** Deploy the base foundation model to one SageMaker AI real-time endpoint and create separate adapter inference components for each region, each containing its LoRA artifacts, then invoke the endpoint while specifying the appropriate adapter.

<details><summary>Answer</summary>

**Answer: D.** SageMaker multi-adapter inference deploys the base model once and registers each regional LoRA adapter as its own inference component on the same endpoint, and the invocation names the adapter to apply. Multi-model endpoints treat each as a full model, EFS mounting and Lambda weight injection are custom hacks that do not select adapters per request.

*Where this is covered: Unit 02, Customising models and managing their lifecycle. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

Choose a model by mapping requirements to capabilities and then measuring candidates with **Bedrock** evaluation, including **LLM-as-a-judge** and **robustness** metrics, before weighing cost and latency.

Buy capacity to fit the traffic: **on-demand** by default, **cross-Region inference** for peaks and Regional resilience, **Provisioned Throughput** for steady volume and customised models, **batch inference** for offline bulk work, and **latency-optimized inference** and **intelligent prompt routing** for interactive cost and speed.

Control output with **temperature** or **top-p**, max tokens and **stop sequences**. Switch models through an **API Gateway** and **Lambda** router that reads **AppConfig** at runtime. Survive failure with **cross-Region inference**, backoff and jitter, **Step Functions** circuit breakers and tiered degradation.

Manage fine-tuned models with **LoRA** adapters served as **inference components**, **Model Registry** approval statuses, pipeline-driven blue/green or canary deployment with alarm-based rollback, and explicit retirement.
