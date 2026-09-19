# Unit 01: Cost optimization and resource efficiency

**Task 4.1: Implement cost optimization and resource efficiency strategies.** This unit is about paying less for the same result: counting and trimming tokens, choosing the cheapest model that meets the quality bar and routing to it automatically, squeezing more throughput out of the capacity you already pay for, and not calling the model at all when a cached answer will do.

Domain 4 is 12 percent of the exam, and Task 4.1 carries most of its questions. They are recognisable by the words "reduce cost", "token usage", "underutilised", "near-duplicate queries" and "minimal operational overhead", and each maps to one of the four sections below.

## Tokens are the unit of cost

A **token** is the unit a model reads and writes: a word, part of a word or a punctuation mark. A token is roughly three-quarters of an English word on average, though every model family tokenizes differently.

**On-demand** **Bedrock** pricing is per thousand or million **input tokens** and **output tokens**. **Output tokens** cost several times more than **input tokens** because generating is more expensive than reading.

Everything counts: the system prompt, **tool definitions**, conversation history, retrieved passages and response. Cost therefore grows with prompt length times request volume plus response length. Every cost technique attacks one of those three factors.

You need three instruments: estimation before a call, tracking after it, and attribution to the application that made it.

**Estimation before the call.** The **Bedrock CountTokens API** returns, free of charge, exactly how many **input tokens** a request would consume for supported **Anthropic Claude** models. It accepts the same request formats as `InvokeModel` and `Converse`. For other models, use the provider's tokenizer. Do not rely on a characters-divided-by-four guess when accuracy matters.

**Tracking after the call.** Every `Converse` response carries a `usage` block with input, output and total tokens, plus cached-token counts when **prompt caching** applies. **Bedrock** publishes `InputTokenCount` and `OutputTokenCount` as per-model **CloudWatch metrics**. Dashboards and alarms then show which prompts, users or features consume tokens.

**Attribution.** **Application inference profiles** wrap a model in a profile that you invoke instead of the bare model ID. Add **cost-allocation tags**, such as team, application or tenant, to break **Bedrock** spend down by application. Three services analyze that spend and alert when it deviates:

- **AWS Cost Explorer** analyzes spend by service, tag and time.
- **AWS Budgets** alerts when actual or forecast spend crosses a threshold.
- **AWS Cost Anomaly Detection** uses machine learning to alert on unexpected spend.

**Model invocation logs** provide per-request detail when you need to find expensive prompts.

## Token efficiency techniques

The task statement lists six techniques; here is what each means and when it is the answer.

**Context window optimisation.** The **context window** is the maximum number of tokens the model can take in one request, and filling it is not free. Send only what the task needs:

- Keep a **sliding window** of the most recent conversation turns.
- **Summarize** older turns recursively, so a running summary replaces the transcript.
- Retrieve relevant passages with **RAG** instead of pasting whole documents.
- Chunk documents to the size the question needs.
- Place instructions and the most important content first, where models attend most reliably.

A model with a larger **context window** is not the fix for long prompts. It lets you send more tokens and pay for them.

**Context pruning.** Before assembling the prompt, remove turns, passages and boilerplate that are irrelevant to the current request. What you remove depends on the workload:

- In a conversation, drop resolved sub-threads and greetings.
- In **RAG**, use fewer, more relevant chunks and **metadata filtering**.
- In document workflows, send recent notes instead of the whole history.

**Pruning** is the most effective single technique because it cuts **input tokens**, latency and noise at once while keeping the information that matters.

**Prompt compression.** After pruning, shorten what remains:

- Tighten the instructions.
- Use fewer **few-shot examples**.
- Use structured formats, such as bullet lists or JSON, instead of prose.
- Use abbreviations the model understands.
- For very long context, use an FM or a compression library to rewrite passages more densely before sending them.

Apply **compression** to the prompt template once as engineering work. Apply it to dynamic content through a preprocessing step.

**Response size controls and response limiting.** Control generation in three ways:

- Cap output with the `maxTokens` inference parameter.
- Add **stop sequences** so the model stops at a delimiter.
- Specify length and format, such as "three bullet points", "under 100 words" or a **JSON schema**, so the model does not produce essays when a sentence will do.

Truncating the finished response afterwards saves nothing, because the tokens were already generated and billed.

**Token estimation and tracking** ties the loop together: measure token use per feature, set **budgets** and alarms, and test prompt variants for token efficiency in a **Step Functions** workflow before shipping them.

For a clinical assistant whose costs climb because conversations carry long histories, send unnecessary documents and produce long answers, choose a **maximum generation token limit** and **context pruning** of irrelevant turns. **Speculative decoding** speeds generation without saving tokens, a larger **context window** costs more, and sending the whole history from **S3** every time restates the problem.

For claim summaries, combine **context-window optimisation** by pruning irrelevant historical notes, **prompt compression** for long documents and **response-size controls** in the prompt. Archiving old documents with **S3 lifecycle rules**, blanket caching across different claims and truncating outputs with a **Lambda function** do not make that request more token-efficient.

## Cost-effective model selection

The second lever is *which* model answers. Models in **Bedrock** differ by an order of magnitude in price, and a small model answers a warranty question as well as a large one.

**Cost-capability evaluation.** Measure before choosing a model:

1. Run **Amazon Bedrock Evaluations** over a representative prompt set for each candidate. Use automatic metrics for **accuracy**, **robustness** and **toxicity**, or an **LLM-as-a-judge** job for **correctness**, **completeness**, **helpfulness** and style.
2. Record cost per thousand tokens and latency.
3. Compute a **price-to-performance ratio**: quality score per dollar, or **P95 latency per dollar** for latency-sensitive work. P95 is the latency that 95 percent of requests beat.
4. Set the minimum acceptable quality for each use case and pick the cheapest model that clears it.

Repeat the comparison when new models or prices arrive.

**Tiered FM usage by query complexity.** Most traffic is easy. Route each request to the cheapest tier that can handle it, using one of two approaches:

- A **lightweight classifier** labels the query simple, medium or complex, and a router sends it to the matching model. The classifier can be a small FM with a classification prompt or a **Comprehend custom classifier**.
- **Amazon Bedrock intelligent prompt routing** provides managed routing within a model family. It predicts response quality per request and uses the small model unless the large one is needed, with a configurable quality threshold and fallback.

Store templates and metadata for the tiers in **Bedrock Prompt Management**, so the router selects the prompt as well as the model. **Model cascading** is the sequential version: try the small model first and escalate on low confidence. These routing frameworks need no **fine-tuning** and little maintenance. They are the answer whenever a scenario routes everything to a high-end model and complains about cost.

**Distillation**, covered in Domain 1 unit 02, makes the small model itself. A large **teacher model** generates responses that train a smaller, cheaper **student model** for your task.

**Efficient inference patterns.** Reduce repeated or unnecessary work:

- Generate ahead of time in a nightly **batch inference** job at half the **on-demand** price, instead of generating at page view.
- **Cache** answers to repeated questions, as explained in the next section.
- Set **stopping conditions** so agent loops and workflows cannot run away.
- Use a **fallback** to a cheaper model when the primary is throttled.
- Track it all with **cost allocation tags** on **application inference profiles**.

The three-tier logistics assistant question is therefore answered by a classifier that categorises queries and routes them to FM tiers with different price-to-performance levels, plus a two-tier pipeline whose routing templates and metadata sit in **Prompt Management**; streaming does not change billing, **speculative decoding** does not reduce cost, and a bigger **context window** is the opposite of the goal. The 75-percent-simple support bot is answered by **intelligent prompt routing** between the small and the large model of one family, not by **Provisioned Throughput** with an FAQ cache, **fine-tuning**, or hand-tuned **Lex** routing.

## Getting more out of the capacity you pay for

The third lever is utilisation: an underused GPU or an idle **Model Unit** is money spent for nothing.

**Batching.** GPUs are efficient when they process many sequences at once. **Tensor parallelism** splits each model layer across several GPUs so a large model fits, and determines how many replicas an instance can run. Domain 2 unit 02 covers this technique.

On **SageMaker**, **LMI containers** use **Deep Java Library**, or **DJL**, serving with **vLLM** or **TensorRT-LLM** back ends. Their **continuous** or **rolling batching** admits new requests into a running batch as others finish, so the GPU never waits.

At the application layer, **request batching** collects requests for a few milliseconds and submits them together. Tune it with **batch size** and **batching timeout**. When latency rises and **throttling** appears while GPU utilization stays low, enable **application-layer batching** and tune those two controls. Serial processing behind **SQS**, smaller outputs and maximum provisioned capacity for all hours do not fix that utilization problem.

For offline work, **Bedrock batch inference** and **SageMaker batch transform** process whole datasets at the best price per token.

**Right-sizing the serving configuration.** In the recurring **SageMaker** scenario, an LLM runs on 8-GPU instances with **tensor parallelism** across all eight GPUs. Its **maximum sequence length** is ten times longer than real requests. The system scales out expensively while GPUs sit idle.

Two changes fix it without touching the model:

- Set the **tensor parallelism degree to 4**, so each instance runs **two replicas** and doubles concurrency.
- **Reduce the maximum sequence length** to what requests actually need. The freed memory supports a **larger rolling batch size**.

Splitting across all eight GPUs or adding instances with smaller batches does not raise utilization. Neither does **speculative decoding**, which is a latency technique.

**Capacity planning.** Plan in the units the service meters:

- **On-demand** **Bedrock** quotas use **tokens per minute** and **requests per minute**.
- **Provisioned Throughput** uses **Model Units** in its classic purchase form.
- **SageMaker** capacity depends on GPU memory and instances.

Analyze historical token usage for peak-to-average ratios, growth trends and seasonality. Use **SageMaker Inference Recommender** load tests to pick instance types, and separate the steady base load from the spiky remainder. Buy **Provisioned Throughput** only for the base load, with a one- or six-month commitment for the discount. Let **cross-Region inference** absorb spikes on demand.

**Provisioned Throughput** comes in two purchase forms:

- **Model Units**: the classic form. The unit count cannot change after purchase, although a no-commitment purchase can be deleted and bought again at a new size.
- **By tokens**: the newer form. Set input and **output tokens** per minute, then adjust them as measured demand changes.

"Scaling **Provisioned Throughput** to prompt and completion token volume" means sizing and adjusting capacity from token metrics. A **Lambda function** driven by token-volume alarms makes the adjustment where the purchase mode allows it.

**Utilisation monitoring and auto scaling.** On **SageMaker endpoints**, watch GPU utilization, `InvocationsPerInstance` and the sub-minute `ConcurrentRequestsPerModel` and `ConcurrentRequestsPerCopy` metrics. On **Bedrock**, watch token counts and throttles.

Two hosting patterns raise utilization by sharing capacity. **Multi-model endpoints** consolidate many small models of one framework onto one endpoint and load them on demand. **Inference components** share accelerators among several models or adapters.

Then apply scaling controls:

- **Target tracking** on those metrics adds or removes **SageMaker** endpoint capacity to hold a metric at a target value.
- **Scheduled scaling** handles predictable business-hours peaks.
- Let inference-component endpoints **scale to zero** overnight.

**Lambda** scales itself, while queue-based buffering with **SQS** keeps bursts from turning into **throttling**.

## Intelligent caching

The cheapest invocation is the one you never make. Four caching layers appear in the task statement, and the wording of a question tells you which.

**Exact-match caching with deterministic request hashing.** Build the cache key in steps:

1. Normalize the request: trim whitespace, lowercase where safe and sort parameters.
2. Hash the prompt together with the model ID and **inference parameters**.
3. Use the hash as a key in **Amazon ElastiCache** or **Amazon DynamoDB**.

**ElastiCache** is in-memory with sub-millisecond access. **DynamoDB** is durable with single-digit-millisecond access. Identical requests hit the cache; anything phrased differently misses.

**Result fingerprinting** hashes the content or response, so duplicate documents or answers are recognized even when they arrive under different names. Set a **time to live** so cached answers expire, and invalidate them when source data or prompts change.

**Semantic caching.** Users ask the same thing in different words, so an **exact-match cache** misses most repeats. A **semantic cache** handles paraphrases in three steps:

1. Embed the incoming query.
2. Run an **approximate nearest neighbour** search against embeddings of previously answered queries.
3. Return the stored answer when similarity exceeds a threshold.

Tune the threshold so near-duplicates hit and genuinely different questions miss. **Amazon MemoryDB** with vector search is the lowest-latency store for this. **OpenSearch Service** and **Aurora PostgreSQL** with the **pgvector** extension also work; **pgvector** provides vector search inside PostgreSQL.

This needs no model change or new inference infrastructure. Canonicalizing prompts in **Lambda** still produces exact-match keys, raw string caching cannot match meaning, and **CloudFront** cannot judge meaning either.

**Edge caching.** **Amazon CloudFront** caches responses at edge locations near users, while **API Gateway caching** caches at the API stage. Both suit predictable, public, non-personalized answers, such as FAQ responses and pre-generated product descriptions, and remove the round trip entirely. They key on URL and headers, so they cannot recognize paraphrases or **personalize**.

**Prompt caching.** Some requests repeat a long static prefix, such as a system prompt, **tool definitions** or a regulatory handbook, followed by a short question. **Bedrock prompt caching** stores the processed prefix at a **cache checkpoint** and reuses it for later requests within a short window. That window is about five minutes and refreshes on each hit. Cached tokens are billed at a large discount, and reuse cuts latency.

Minimum prefix lengths apply per model, and the feature works with **on-demand** inference. Some models also offer a one-hour cache and **implicit caching** without explicit checkpoints. Cached reads do not count toward tokens-per-minute quotas.

This is the answer to "the same handbook is included in every request". Moving the handbook to a database the model queries does not solve this caching requirement. Neither does sending embeddings instead of text, because models cannot read embeddings. **SageMaker warm pools** keep instances ready to shorten startup, so they address a different problem.

A **tiered** design combines them: exact-match first, semantic second, model last, with hit rates, latency and savings tracked in **CloudWatch** so thresholds and **TTLs** can be tuned.

## Worked scenario

A software-as-a-service helpdesk company sees its **Bedrock** bill triple in a quarter. Conversations carry long histories, every question goes to the largest model, thousands of near-identical "how do I reset my password" queries arrive daily, the same product manual is pasted into every prompt, and a **SageMaker**-hosted **reranker** scales out while its GPUs sit idle.

Measure first. **Application inference profiles** with tenant and feature tags replace bare model identifiers so **Cost Explorer** shows spend per customer, **Budgets** alert on overruns and **Cost Anomaly Detection** flags the spikes; **CloudWatch** token metrics and the usage block in each response show that **input tokens** dominate; the **CountTokens** API confirms that the average prompt carries twelve turns of history and a forty-page manual.

Then cut tokens. A **sliding window** keeps the last four turns with a running summary of the rest, **context pruning** drops resolved sub-threads, the prompt template is compressed to half its length, and a **maximum generation token limit** with a length instruction ends the essays. The manual moves out of the prompt and into a **Knowledge Base**, and the shared instructions that remain are placed behind a **prompt-cache checkpoint** so they are processed once every few minutes rather than on every call.

Then pick the right model. **Bedrock Evaluations** on a sample of tickets show a small model answers eighty percent of them as well as the large one at a tenth of the price, so **intelligent prompt routing** sends the simple questions to the small model and escalates the rest, with the **price-to-performance ratio** tracked per tier. Nightly ticket summaries move to **batch inference**.

Then raise utilisation. The **reranker**'s container is reconfigured with **tensor parallelism** matched to its real memory footprint and a shorter **maximum sequence length**, doubling replicas per instance and enlarging the rolling batch; **auto scaling** switches to the **concurrent-requests metric** and scales to zero overnight; the steady daytime base load gets a small **Provisioned Throughput** commitment while **cross-Region inference** absorbs spikes. Finally, caching: an **exact-match cache** in **ElastiCache** keyed by a hash of the normalised prompt, a **semantic cache** in **MemoryDB** for the paraphrased password questions, and **CloudFront** for the public FAQ answers. Each step is one of the exam's cost questions, and the whole sequence is the decision order to remember.

## Exam lens

- "Long conversation histories, unnecessary context, overly long answers, reduce tokens" → **maximum generation token limit** plus **context pruning** (and **prompt compression** for long documents); not **speculative decoding**, bigger context windows, or truncating outputs afterwards.
- "Estimate tokens before calling", "predict cost" → the **Bedrock** **CountTokens** API or a model-specific tokeniser.
- "Attribute **Bedrock** cost by team or application" → **application inference profiles** with **cost allocation tags**, **Cost Explorer** and **Budgets**.
- "All queries go to a high-end FM, most are simple, no **fine-tuning**, minimal maintenance" → a classifier routing to FM tiers, or **intelligent prompt routing** within a family, with **Prompt Management** for templates.
- "Compare models on quality per dollar" → **Bedrock Evaluations** plus a **price-to-performance ratio** (**P95 latency per dollar** for latency-sensitive work).
- "Latency and **throttling** at peak while GPU utilisation is low" → application-layer **request batching** with tuned **batch size** and timeout.
- "8 GPUs, weights fit in 4, sequence length far larger than real requests, low concurrency" → **tensor parallelism** of 4 with two replicas per instance, and a smaller **maximum sequence length** for a larger rolling batch.
- "Bursty traffic, token-heavy requests, minimal custom infrastructure, **Bedrock**" → token-based capacity planning from invocation metrics with **Provisioned Throughput** scaled to token volume (base load committed, spikes on demand).
- "Thousands of near-duplicate queries, no model or infrastructure change" → **semantic caching** with embeddings and **ANN** similarity (**MemoryDB** vector search when the question names it).
- "Same static handbook in every request" → **Bedrock prompt caching**.
- "Predictable public answers, global users" → **CloudFront** or **API Gateway** **edge caching**.

## Knowledge check

<!-- KC: E1-Q62, E3-Q36, E1-Q58, E3-Q4, E1-Q31, PQ-Q18, E2-Q27, E1-Q65, E3-Q8 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 62

A healthcare analytics company is building a GenAI assistant with Amazon Bedrock to help clinicians summarize case notes and provide care recommendations. The engineering team notices that inference costs are rising rapidly because user conversations include long historical threads. Many requests send unnecessary document context and produce overly long responses. The company wants to reduce FM token consumption without reducing the quality of the assistant's recommendations.

Which combination of steps will MOST effectively reduce token usage with MINIMAL operational overhead? (Select TWO.)

- **A)** Apply response size controls by setting a maximum generation token limit in the inference configuration.
- **B)** Enable speculative decoding to reduce end-to-end latency for each request.
- **C)** Implement context pruning to remove irrelevant conversation turns before sending the prompt.
- **D)** Use a larger context-window FM so that longer inputs can be processed at once without manual prompt trimming.
- **E)** Store full conversation history in Amazon S3 and send the entire past thread to the model for every request to preserve accuracy.

<details><summary>Answer</summary>

**Answer: A, C.** A maximum generation token limit in the inference configuration caps the overly long responses, and context pruning removes irrelevant conversation turns and documents before the prompt is sent, cutting input tokens while keeping the information the recommendation needs; both are configuration and preprocessing changes with minimal overhead. Speculative decoding speeds generation without saving tokens, a larger context-window model lets you send and pay for more tokens, and sending the entire history from S3 on every request is the cost problem itself.

*Where this is covered: Unit 01, Token efficiency techniques. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 3, question 36

A global insurance provider is building a document-analysis assistant on Amazon Bedrock to summarize long claim forms, policy documents, and customer correspondence. The assistant uses a foundation model (FM) to generate explanations and action items for claim specialists. Recently, the monthly FM bill increased sharply due to extremely long input prompts and oversized output generations.

The architecture currently injects entire historical claim notes into every prompt, even when only the most recent details are relevant. The specialists also report that the model often produces longer-than-necessary summaries. The engineering team needs to reduce token usage without degrading the model’s ability to generate accurate summaries, and the solution must require minimal operational overhead.

Which approach BEST reduces token usage while maintaining summary quality?

- **A)** Implement context-window optimization by pruning irrelevant historical notes, apply prompt compression for long claim documents, and enforce response-size controls in the prompt itself to limit summary length.
- **B)** Use an AWS Lambda function to dynamically shorten all responses by truncating the FM output to a predefined character limit before returning the response to the user.
- **C)** Use Amazon S3 lifecycle rules to archive older claim documents and instruct the FM via system prompts to exclude archived information from analysis.
- **D)** Cache the FM responses for all claim types in Amazon ElastiCache and prevent the FM from being invoked for repeated queries even when claim details differ slightly.

<details><summary>Answer</summary>

**Answer: A.** Context-window optimisation by pruning irrelevant historical notes, prompt compression for the long claim documents, and response-size controls in the prompt attack the two causes named in the stem, oversized inputs and oversized outputs, while preserving the relevant details the summary needs. Truncating the output in Lambda after generation saves no tokens and cuts summaries mid-sentence, S3 lifecycle rules with a system prompt do not shorten what is injected into the prompt, and caching across claims whose details differ returns wrong summaries.

*Where this is covered: Unit 01, Token efficiency techniques. Key: ours, confidence high.*

</details>

### 3. Exam 1, question 58

A logistics automation company is building a GenAI routing assistant on Amazon Bedrock. The assistant must handle three categories of queries: simple shipment lookups, medium-complexity route validation, and complex multi-stop optimization questions. The company notices that all queries are currently routed to a high-end FM, causing unnecessary inference costs for common low-complexity requests.

A GenAI developer is tasked with implementing a framework that reduces FM cost while keeping answer quality high for complex queries. The solution must require minimal ongoing maintenance and no custom fine-tuning.

Which combination of steps will meet these requirements MOST effectively? (Select TWO.)

- **A)** Use a single large FM for all requests but enable response streaming to reduce billing costs based on output tokens.
- **B)** Enable speculative decoding on the large FM to reduce compute time for the most complex requests.
- **C)** Implement a lightweight classifier model to categorize incoming queries as simple, medium, or complex, and route each category to a corresponding FM tier with different price-to-performance levels.
- **D)** Route all queries to a high-context-window FM to reduce the chance of missing relevant details.
- **E)** Create a two-tier FM pipeline where simple lookups use a small FM and complex optimization queries use a larger FM. Use Bedrock Prompt Management to store routing templates and metadata.

<details><summary>Answer</summary>

**Answer: C, E.** A lightweight classifier that labels each query simple, medium or complex and routes it to an FM tier with the matching price-to-performance level stops paying high-end prices for shipment lookups, and a two-tier pipeline with routing templates and metadata stored in Bedrock Prompt Management keeps the framework maintainable without fine-tuning. Streaming does not change token billing, speculative decoding reduces compute time rather than cost, and a high-context-window model for everything is the opposite of the goal.

*Where this is covered: Unit 01, Cost-effective model selection. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 4. Exam 3, question 4

A company is developing a customer support chatbot using Amazon Bedrock. The chatbot must answer high-volume simple product inquiries as well as more complex reasoning-based questions. About 75% of all incoming queries are simple (“What is the warranty?”), while 25% require advanced reasoning (“Compare two products and recommend one based on my usage pattern”). The solution must minimize cost, reduce operational burden, and preserve high-quality responses across both query types. The company also integrates Amazon Comprehend to analyze sentiment so the bot can adjust tone and detect customer frustration.

Which approach best meets these requirements?

- **A)** Implement a hybrid system that uses Amazon Lex to answer simple inquiries and invokes Bedrock only for complex queries. Maintain FAQ responses in Amazon S3 and use CloudWatch analytics to tune routing logic manually.
- **B)** Deploy Bedrock using fully provisioned throughput for all queries and store frequently asked questions in Amazon ElastiCache (Redis OSS) with TTL-based caching to reduce model invocation counts.
- **C)** Use Amazon SageMaker AI to fine-tune a Claude Sonnet model using chat logs, and integrate Amazon Kendra retrieval to improve information grounding for both simple and complex customer questions.
- **D)** Leverage Bedrock’s intelligent prompt routing to send simple questions to Claude Haiku for low-cost inference, and automatically escalate complex reasoning queries to Claude Sonnet. This reduces cost while maintaining response quality and requires minimal operational overhead.

<details><summary>Answer</summary>

**Answer: D.** Bedrock intelligent prompt routing predicts per request whether the smaller model in a family will answer well enough and sends the simple 75 percent to it, escalating complex reasoning to the larger model, which minimises cost and operational burden while preserving quality, and Comprehend sentiment analysis sits alongside for tone. Provisioned Throughput for all queries with an FAQ cache pays for capacity the simple queries do not need, fine-tuning with Kendra adds training and retrieval work the question does not ask for, and a Lex-plus-manual-routing hybrid is more operations, not less.

*Where this is covered: Unit 01, Cost-effective model selection. Key: ours, confidence high.*

</details>

### 5. Exam 1, question 31

A media analytics startup uses Amazon Bedrock to power a real-time content summarization service for news and video transcripts. During peak viewing hours, the team notices rising model latency and occasional throttling. GPU utilization metrics show that the FM is underutilized during these spikes. The GenAI engineer must increase throughput and stabilize performance with minimal operational burden.

Which solution will MOST effectively improve throughput and GPU utilization?

- **A)** Place Amazon SQS in front of the system and process requests serially to avoid throttling.
- **B)** Reduce the max output tokens for all summaries to decrease model compute time.
- **C)** Enable request batching in the application layer and tune batch size and batching timeout to increase FM parallelism during high traffic periods.
- **D)** Increase the number of provisioned throughput units to the maximum supported level and keep them fixed at all times.

<details><summary>Answer</summary>

**Answer: C.** Low GPU utilisation during latency spikes means requests are being processed one at a time; enabling request batching in the application layer and tuning batch size and batching timeout lets the FM process many requests in parallel, raising throughput and utilisation with minimal operational burden. Serial processing behind SQS lowers throughput further, cutting output tokens reduces quality without using the idle GPU capacity, and maximum fixed Provisioned Throughput pays for peak capacity all day.

*Where this is covered: Unit 01, Getting more out of the capacity you pay for. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 6. Official practice question set, question 18

A GenAI developer deployed a fine-tuned LLM to an Amazon SageMaker AI endpoint. The GenAI developer used the default serving configuration for continuous batching with the AMI including the Deep Java Library (DJL). The model is being served on GPU-based Amazon EC2 instances, each with 8 GPUs. As the model scales to production, the GenAI developer discovers that many instances are needed to meet traffic demands. The GenAI developer wants to avoid increased costs from the overutilization.

The GenAI developer analyzes logs. The GenAI developer discovers that the maximum I/O sequence length in real requests is 10 times smaller than what the model was originally configured to handle. Additionally, the current concurrency for each instance is low. Profiling shows that the model's weights and activations can fit entirely within 4 GPUs.

Which combination of steps can the GenAI developer take to improve resource utilization? **(Select TWO)**

- **A)** Split the model across all 8 GPUs by using a tensor parallelism degree of 8 to improve memory efficiency.
- **B)** Enable speculative decoding to reduce response latency for each request.
- **C)** Use tensor parallelism with a degree of 4 to deploy two model replicas for each instance.
- **D)** Reduce the model's maximum sequence length to provide a higher rolling batch size for each GPU.
- **E)** Increase the number of SageMaker AI instances and spread requests more evenly to reduce the load for each instance.

<details><summary>Answer</summary>

**Answer: C, D.** Because the weights and activations fit in four GPUs, a tensor parallelism degree of 4 lets each 8-GPU instance run two model replicas and double its concurrency, and because real sequences are ten times shorter than the configured maximum, reducing the maximum sequence length frees memory for a larger rolling batch per GPU; together they raise utilisation so fewer instances are needed. Spreading one replica across all eight GPUs wastes half of them, speculative decoding targets latency rather than utilisation, and adding instances is the cost the developer wants to avoid.

*Where this is covered: Unit 01, Getting more out of the capacity you pay for. Key: AWS official answer.*

</details>

### 7. Exam 2, question 27

A logistics technology company is deploying a generative AI assistant powered by Amazon Bedrock to help internal teams analyze shipping exceptions. The GenAI engineering team notices that traffic patterns are highly bursty: thousands of short requests arrive during business hours, but overnight traffic drops to almost zero. The team also finds that long prompts occasionally cause slowdowns because token processing time varies significantly between queries.

The company wants to build an efficient resource allocation strategy that minimizes cost, handles spikes predictably, and prevents delays during token-heavy requests. The solution must require minimal custom infrastructure and work seamlessly with Amazon Bedrock.

Which solution BEST meets these requirements?

- **A)** Use Amazon Bedrock invocation metrics to build token-based capacity planning. Configure auto scaling on Provisioned Throughput with target metrics based on prompt and completion token volume, ensuring capacity scales with real GenAI traffic.
- **B)** Place an Amazon API Gateway in front of Amazon Bedrock and throttle requests to flatten traffic spikes before they reach the model.
- **C)** Increase the model’s maximum context window to handle occasional large prompts and disable auto scaling to avoid unpredictable scaling events.
- **D)** Use Amazon SQS to queue all requests and process them using a fixed number of Lambda functions that forward calls to Amazon Bedrock.

<details><summary>Answer</summary>

**Answer: A.** Building capacity planning on Bedrock invocation metrics measured in tokens, and sizing Provisioned Throughput to prompt and completion token volume (committed capacity for the daytime base load, adjusted from token-based alarms where the purchase mode allows it, with on-demand or cross-Region inference for the remainder), matches capacity to real GenAI traffic and keeps token-heavy requests from starving others with minimal custom infrastructure. Bedrock does not auto scale Provisioned Throughput natively: Model Unit purchases cannot be resized (only deleted and re-bought), while the tokens-based purchase mode lets you change tokens per minute, so the option describes token-driven capacity management rather than a checkbox, but it is the only option that plans in the right unit. API Gateway throttling rejects requests rather than serving them, raising the context window and disabling scaling ignores the bursts, and a fixed number of Lambda consumers on SQS adds delay and custom plumbing.

*Where this is covered: Unit 01, Getting more out of the capacity you pay for. Key: ours, confidence medium.*

</details>

### 8. Exam 1, question 65

A global logistics company is building an AI assistant on Amazon Bedrock to help internal teams analyze shipment exceptions. The system receives thousands of near-duplicate queries each day, such as slight variations of "summarize the delay reason for package 12345." A GenAI engineer needs to reduce FM invocation costs and improve response latency without modifying the underlying foundation model or deploying additional inference infrastructure. The solution must avoid recomputing responses for semantically identical requests.

Which solution will MOST effectively meet these requirements with the least operational overhead?

- **A)** Create a Lambda function that rewrites prompts into a canonical form before sending them to the model, then cache based on the canonicalized string.
- **B)** Use Amazon CloudFront to cache model responses at the edge to reduce round trips to the Bedrock endpoint.
- **C)** Cache the raw prompt strings in an in-memory store and return cached responses only when an exact string match occurs.
- **D)** Implement a semantic caching layer by generating vector embeddings for incoming queries, performing similarity search with an approximate nearest neighbor index, and returning cached results when similarity exceeds a defined threshold.

<details><summary>Answer</summary>

**Answer: D.** A semantic caching layer embeds each incoming query, searches an approximate nearest neighbour index of previously answered queries and returns the cached result when similarity exceeds a threshold, so the thousands of paraphrased shipment questions stop invoking the model, with no change to the FM and no new inference infrastructure. Canonicalising prompts in Lambda is still exact-match caching that misses most paraphrases, raw string caching misses even more, and CloudFront caches by URL and headers and cannot judge that two differently worded prompts mean the same thing.

*Where this is covered: Unit 01, Intelligent caching. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 9. Exam 3, question 8

A global software vendor is building a compliance research assistant that uses Amazon SageMaker AI to prepare domain-specific context documents and Amazon Bedrock for real-time conversational analysis. Each user query includes a long regulatory handbook that rarely changes, followed by short user questions. The handbook is included in every inference request, causing growing latency and token-processing costs. The architects want to avoid repeatedly reprocessing the static handbook text while still allowing dynamic, question-specific responses.

Which solution should the team implement to optimize performance and reduce cost?

- **A)** Shorten the system prompt by removing the handbook entirely and move the handbook into a database that Bedrock queries dynamically at inference time.
- **B)** Pre-encode the handbook into embeddings in SageMaker AI and send only the embeddings plus the user question into Bedrock to reduce the runtime input size.
- **C)** Enable prompt caching in Bedrock so the static handbook section is cached as a prefix and reused across subsequent invocations, allowing only the user’s query to be processed each time.
- **D)** Enable SageMaker AI model instance caching by using provisioned instance warm pools so the model retains the handbook context in memory across calls.

<details><summary>Answer</summary>

**Answer: C.** Bedrock prompt caching stores the processed static handbook as a cached prefix at a checkpoint and reuses it across subsequent invocations, so only the short user question is processed each time, cutting both latency and token cost. Moving the handbook into a database the model queries at inference changes the design and still sends retrieved text every time, models cannot consume raw embeddings in place of text, and SageMaker warm pools keep instances warm rather than caching Bedrock prompt context.

*Where this is covered: Unit 01, Intelligent caching. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

Cost is tokens times requests: count them (**CountTokens**, `usage`, **CloudWatch** token metrics, **application inference profiles** for attribution), then cut them with **context-window optimisation**, pruning, compression and **response-size controls**. Pick the cheapest model that meets a measured quality bar, route by complexity with a classifier or **intelligent prompt routing**, and generate offline in batch where you can.

Raise utilisation with continuous and **application-layer batching**, right-sized **tensor parallelism** and sequence lengths, token-based capacity planning, committed **Provisioned Throughput** for the base load and **auto scaling** on the right metrics. And avoid the call altogether with exact-match, semantic, edge and **prompt caching**.
