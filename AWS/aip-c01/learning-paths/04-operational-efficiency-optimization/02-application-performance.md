# Unit 02: Application performance

**Task 4.2: Optimize application performance.** Unit 01 was about spending less; this unit is about responding faster and handling more: making the user experience feel instant, making retrieval quick and relevant, pushing throughput through the model's limits, tuning **inference parameters**, allocating capacity to GenAI traffic patterns, and profiling the whole system to find where the time goes.

## Responsive systems

Users judge an assistant by how quickly something appears, so the first metric is **time to first token**, not total generation time. Five techniques trade cost against latency:

**Pre-computation.** For predictable queries, such as baggage rules, warranty terms or airport policies, generate answers ahead of time with a scheduled **Lambda function**. Serve them from a fast store:

- **Amazon ElastiCache** provides in-memory, sub-millisecond access.
- **Amazon DynamoDB** provides single-digit-millisecond access, with **DynamoDB Accelerator (DAX)** bringing reads to microseconds.
- **S3** stores larger artifacts.

During peak hours, the FM is not called at all for those questions. Pre-computing *every* possible response is impossible for open-ended questions, so pair **pre-computation** with a live path for the rest.

**Latency-optimized inference.** **Bedrock**'s **latency-optimized** option (`performanceConfig.latency = optimized`) serves supported models from faster infrastructure, sometimes at a higher token price depending on the model; use it for the time-sensitive, lightweight requests and reserve the larger, slower models for the complex ones.

**Response streaming.** `ConverseStream` and `InvokeModelWithResponseStream` deliver tokens as they are generated, so a multi-step answer starts appearing in a second instead of arriving whole after fifteen; the total time is unchanged but the perceived latency collapses. Domain 2 unit 04 covers how the stream reaches the browser.

**Parallel requests.** When a workflow needs independent model calls, such as summarizing three documents or running extraction and classification, run them concurrently and then merge the results. Choose the mechanism based on the work:

- A **Step Functions** `Parallel` state handles a fixed set of branches.
- A `Map` state handles a collection.
- Concurrent calls in application code provide another option.

**Parallelism** shortens wall-clock time for complex workflows. It does not help a single call, and sending every user query to several models "and returning the first" multiplies cost.

**Performance benchmarking.** Measure before and after in **CloudWatch**, broken down by model and configuration. Track:

- **Latency percentiles**: P50, P95 and P99.
- **Time to first token**.
- **Tokens per second**.
- Error and throttle rates.
- Cost per request.

Summarize the latency-cost trade-off as **P95 latency per dollar**. Run controlled experiments: for hosted **SageMaker** models, **production variants** split traffic by weight. For **Bedrock** applications, put the configuration behind an **AWS AppConfig feature flag**, split traffic in code and compare **CloudWatch metrics** per variant.

**CloudWatch Evidently**, the former **A/B testing** feature named in the Skill Builder course, was discontinued in October 2025.

The clinical assistant that needs instant answers for simple questions and tolerates longer computation for complex summaries is therefore served by **latency-optimized** models plus streaming for the quick path and higher-capability models for the complex path; the travel assistant is served by pre-computing predictable answers into **ElastiCache** and streaming the reasoning-heavy ones.

## Faster and better retrieval

Retrieval sits in the critical path of every **RAG** request, and it has two failure modes: slow and irrelevant.

**Index optimisation.** Use an **approximate nearest neighbour** index rather than exhaustive search, as covered in Domain 1 unit 04. **HNSW** fits most workloads. Its tuning controls apply at different stages:

- At index time, `m` controls graph connectivity and `ef_construction` controls build-time accuracy.
- At query time, `ef_search` controls how many candidates are examined.

**IVF** is an alternative, tuned through the number of clusters and probes. Higher values raise recall and latency together.

Keep the index within its resource budget:

- Compress vectors with **quantisation** to fit more in memory.
- Keep the index warm.
- Size shards so each fits its node's memory.
- On **OpenSearch Serverless**, watch the compute units the collection consumes.

**Hierarchical indices** put a coarse top-level index in front of detailed lower-level indices. A query can then narrow to a section before searching its chunks. **Filter first** with **metadata filters** and a sensible **top-k** to cut the candidate set, so large result sets do not slow augmentation.

**Query preprocessing.** A **Lambda function** can prepare the query before retrieval:

1. Normalize spelling, abbreviations and punctuation.
2. Rewrite conversational phrasing into a search-friendly form.
3. Expand it with **synonyms** or related terms generated by an FM.
4. Decompose multi-part questions into sub-queries.
5. For hard cases, generate a hypothetical answer to embed instead of the raw question.

Cleaner queries mean better embeddings and fewer irrelevant hits.

**Hybrid search with custom scoring.** Combine normalized, weighted scores from vector similarity and **BM25** keyword search. Add **custom scoring functions** to boost recency, document type, popularity or source authority.

When **relevance** matters more than a few milliseconds, a **reranker model** re-scores the top candidates. Cache frequent query results in **ElastiCache** so repeated searches skip the index.

When profiling shows long prompts full of redundant history *and* vector searches returning large result sets, the answer is to profile the API calls, prune the redundant prompt segments and optimise the vector queries with filtered **top-k** scoring, all without changing the model; a denser index with a larger search window, bypassing retrieval by caching everything in **DynamoDB**, or raising **output tokens** and **temperature** make things slower or worse.

## Throughput under load

Throughput is **tokens per second** through the system, and GenAI workloads hit limits that classical APIs do not: per-model **requests-per-minute and tokens-per-minute quotas**, variable per-request processing time (a 2,000-token prompt takes far longer than a 50-token one), and GPU capacity that is wasted unless requests are batched.

**Token processing optimisation.** Shorter prompts and shorter outputs (unit 01) are throughput techniques as much as cost techniques: fewer tokens per request means more **requests per minute** inside the same quota and faster individual responses. **Prompt caching** removes the repeated prefix from the processing path, and cached reads do not count toward tokens-per-minute quotas; streaming lets clients consume output while the model is still generating.

**Batch inference strategies.** Move everything that is not interactive to **Bedrock batch inference** jobs or **SageMaker batch transform**. For similar interactive requests, use **micro-batching**: an **SQS queue** collects the requests, and a consumer submits batches whose size adapts to queue depth.

The model then processes many similar summarization requests together instead of one at a time. **Continuous batching** inside **SageMaker LMI containers** does the same on the GPU.

**Concurrent model invocation management.** Control how many invocations are in flight and what happens when the quota is reached:

- Set a **concurrency limit** sized to the quota. Use a semaphore in code, **Lambda reserved concurrency**, or a **Step Functions Map state** with `MaxConcurrency`.
- Use **SDK retries with exponential backoff and jitter** for `ThrottlingException`. **Standard mode** provides retries; **adaptive mode** also adds client-side **rate limiting**.
- Apply **API Gateway per-client throttling and usage plans** so one tenant's burst does not consume everyone's quota.
- Use **request prioritization queues** so critical requests go first.
- Provide a **fallback path** when the model is saturated.

To lift the ceiling itself, choose among these options:

- **Cross-Region inference** routes **on-demand** requests to other Regions in the geography with the same model and API.
- **Provisioned Throughput** reserves capacity.
- A requested **quota increase** raises the allowed quota.

Fixed retry intervals and **reserved concurrency** alone do not address a **Bedrock** throttle. Neither does **AWS Global Accelerator**, a network service that speeds client traffic to AWS endpoints.

For a clinical summarization service whose invocations queue at peak with widely varying token processing speed, combine **concurrent invocation management** and **batch inference**. Increase parallel invocations with retry behavior tuned for bursts, and batch similar requests with **dynamic batch sizing** based on queue depth. This raises throughput without changing the model. A smaller model changes the FM, scheduled manual **throttling** is not real-time, and truncating every document by half destroys quality.

For seasonal "Too many requests" failures on the same model and API, **cross-Region inference** is the cost-effective answer over **Provisioned Throughput**, prompt routing to other models or a hand-built **Lambda** fallback.

## Tuning the model's behaviour

**Inference parameters** shape every response, and the exam expects you to know what each does and how to test changes safely.

- **Temperature** scales the randomness of token selection: near 0 the model almost always picks the most likely token (consistent, deterministic-feeling output for extraction, classification, code); higher values (0.7 and up) spread probability across more tokens (variety and creativity for brainstorming and marketing copy).
- **Top-p (nucleus sampling)** limits selection to the smallest set of tokens whose cumulative probability reaches *p*; **top-k** limits it to the *k* most likely tokens. Both cut off the unlikely tail; providers recommend adjusting **temperature** or **top-p**, not both aggressively.
- **Maximum tokens** caps the response length; **stop sequences** end generation at a delimiter.
- Model-specific parameters exist (**Anthropic** models expose `top_k`, **Titan** models use `topP`, some models support penalties for repetition), and prompt formats differ, so **Bedrock**'s **Converse** API normalises the common ones and passes the rest through `additionalModelRequestFields`.

When product descriptions vary too much in tone but must keep some stylistic variety, use **A/B testing several parameter profiles**. Favor a lower **temperature** with moderate **top-p**, and measure the effect before changing production. Setting **temperature** to 0 and **top-k** to 1 removes all variation. **Speculative decoding** is a latency technique, and a bigger model does not stabilize style by itself.

Run the tuning loop in a controlled sequence:

1. Store **parameter profiles** as versions in **Bedrock Prompt Management**.
2. Split traffic with a **feature flag**.
3. Score outputs with **Bedrock Evaluations** and **CloudWatch metrics**. Use **LLM-as-a-judge** for tone and **consistency**.
4. Promote the winner.

Specialized prompt templates per use case and **context-window optimisation** belong in the same tuning loop.

## Allocating resources to GenAI traffic

GenAI traffic is bursty (business-hours peaks, silent nights), heavy-tailed (a few token-heavy requests dominate processing time) and quota-bound, so classical CPU-based scaling misses it.

**Capacity planning for tokens.** Forecast **tokens per minute**, not requests:

1. Multiply expected requests by observed prompt and completion lengths.
2. Add headroom for peaks and growth.
3. Compare the result with the model's **on-demand** quota, the **Model Units** of **Provisioned Throughput**, or the tokens-per-second a **SageMaker** instance type delivers under load. **SageMaker Inference Recommender** measures that serving throughput.

Codify the resulting configuration in **CloudFormation** or **CDK** so environments are reproducible.

**Utilisation monitoring for prompt and completion patterns.** Track `InputTokenCount` and `OutputTokenCount` by hour and feature. Also track prompt-length distributions, idle periods, throttle counts and GPU utilization.

Build dashboards that show capacity used against capacity paid for. Idle windows are where you scale down or **scale to zero**. **SageMaker Model Monitor**, covered in Domain 3 unit 04, adds data-quality and drift monitoring on the same endpoints.

**Auto scaling for GenAI patterns.** On **SageMaker**, combine these controls:

- **Target tracking** on `ConcurrentRequestsPerModel` or `ConcurrentRequestsPerCopy`. These sub-minute metrics **catch** spikes far sooner than `InvocationsPerInstance`.
- **Scheduled scaling** for known peaks, such as market open or clinic hours.
- **Predictive scaling** to forecast from historical patterns and scale ahead of a peak.
- **Scale to zero** for **inference components** on quiet endpoints.
- A warm minimum where cold starts are unacceptable.

On **Bedrock**, combine committed **Provisioned Throughput** for the base load with **cross-Region inference** for spikes. Put an **SQS queue** between the application and model so bursts are smoothed rather than rejected.

**Lambda**'s own scaling handles the orchestration tier. Use **provisioned concurrency** where first-request latency matters.

## Profiling and tuning the whole system

When latency is "sometimes high", find out where. Three tools provide different views:

- **AWS X-Ray** traces each request through **API Gateway**, **Lambda**, retrieval and the **Bedrock** call. **Subsegments** identify each hop; **annotations** record prompt length, output length, model and cache hit. This shows whether time is spent in retrieval, the model or your code, and which prompt patterns are slow.
- **CloudWatch Logs Insights** queries model **invocation logs** and application logs statistically. Compare latency by prompt-length bucket, model or tenant.
- **Amazon Q Developer** reads code and errors and proposes optimizations, test cases and refactorings inside the IDE. This is what "automate performance tuning with the least operational overhead" points to when **Q Developer** is an option.

Try the LLM-specific latency-reduction techniques in this order:

1. Stream the response.
2. Shorten prompts and outputs.
3. Cache prompts, responses and retrieval results.
4. Pick a **latency-optimized** or smaller model for the simple path.
5. For models you host, tune the serving stack for cheaper throughput.

That hosted serving stack can use **quantisation**, **speculative decoding**, **continuous batching**, right-sized **tensor parallelism** and **AWS Inferentia** instances. **Speculative decoding** uses a small draft model to propose tokens that the large model verifies. **Inferentia** is AWS's own inference accelerator chip. Keep the model **preloaded at container start** so initialization is not paid per request.

A custom **SageMaker** container with tensor-parallel loading across GPUs, **continuous batching** in the **DJL** serving stack and **preloading** is the answer to "several minutes of initialisation, low GPU utilisation and throughput collapse beyond a small batch". **Serverless Inference** has no GPUs, a standard container with bigger volumes and more instances does not fix loading, and streaming weights per request would be slower still.

**Efficient service communication** closes the list:

- Reuse connections through **keep-alive** and **SDK client reuse** across **Lambda** invocations.
- Call Regional and **VPC endpoints**.
- Avoid chains of synchronous hops where an **EventBridge** event or **SQS** message would do.
- Keep payloads small.
- Place compute in the same Region as the model and **vector store**.

## Worked scenario

A travel platform's itinerary assistant is slow at peak: baggage-rule questions take as long as complex multi-city planning, retrieval returns hundreds of chunks, **throttling** appears during evening bursts, and product managers want to test whether a lower **temperature** makes recommendations more consistent without breaking anything.

Responsiveness is split by query type. Baggage rules, visa basics and airport policies are pre-computed by a nightly **Lambda** job into **ElastiCache** and served without a model call; simple live questions run on **latency-optimized inference**; every generation streams so the first tokens appear within a second; and the multi-city planner fans out its independent sub-tasks (flights, hotels, local rules) as parallel **Step Functions** branches and merges the results. Benchmarks in **CloudWatch** track P95 latency and **time to first token** per configuration, and the P95-per-dollar figure decides the trade-offs.

Retrieval is tightened. The **OpenSearch** **HNSW** index is tuned, **metadata filters** restrict results to the traveller's destination and dates before the vector search, **top-k** drops from fifty to eight, a **hierarchical index** narrows to a destination before searching its documents, queries are normalised and expanded by a **Lambda** step, and **hybrid search** with a recency boost surfaces the current rules over outdated ones.

Throughput is protected. Prompts are shorter, **prompt caching** removes the repeated instructions from the processing path and its cached reads stay outside the token quota, non-interactive work moves to batch, a **concurrency limit** and the SDK's adaptive retry mode keep bursts inside the quota, **API Gateway** **usage plans** throttle per partner, and **cross-Region inference** raises the ceiling for evening peaks.

The **temperature** question becomes an experiment: two **parameter profiles** are stored as **Prompt Management** versions, an **AppConfig** feature flag splits traffic, **Bedrock Evaluations** and **CloudWatch** metrics score **consistency** and satisfaction per variant, and the winner is promoted. Capacity is planned in **tokens per minute** from observed prompt and completion lengths, **SageMaker** endpoints scale on the **concurrent-requests metric** with **scheduled scaling** for the evening peak, and **X-Ray** traces with **Logs Insights** show where remaining latency hides. A question built on this scenario asks for the latency, retrieval, throughput, tuning or profiling piece; the answers are the ones above.

## Exam lens

- "Low latency for simple queries, complex ones may take longer, smooth at peak" → **latency-optimized** models plus **response streaming**, larger models reserved for complex requests.
- "Predictable repetitive queries slow at peak, multi-step reasoning feels slow" → pre-compute into **ElastiCache** (or **DynamoDB** with **DAX**) and stream the rest.
- "Orchestrate parallel FM calls in a workflow" → **Step Functions** Parallel or Map states.
- "Latency-cost trade-off metric" → **P95 latency per dollar**. "Lowest-latency store for pre-computed answers" → **DynamoDB** with **DAX** or **ElastiCache**.
- "Redundant prompt context and large vector result sets" → API call profiling, prompt pruning, filtered **top-k** vector queries.
- "Improve vector query speed" → **ANN** indexes (**HNSW** or **IVF**) with tuned parameters, filters and **top-k**; **hierarchical indices**.
- "Invocations queue at peak, token speed varies, same FM" → **concurrent invocation management** with tuned retries plus **batch inference** with **dynamic batch sizing**.
- "ThrottlingException from **Lambda** at high concurrency" → SDK **exponential backoff with jitter** plus **API Gateway** per-client **throttling**.
- "Too many requests at seasonal peaks, same model and API, cost-effective" → **cross-Region inference**.
- "Outputs vary too much but need some style variety, evaluate before production" → **A/B test** **parameter profiles** with lower **temperature** and moderate **top-p**.
- "Which parameter controls randomness" → **temperature**; "limit the candidate token set" → **top-k** or **top-p**; "limit length" → **max tokens** and **stop sequences**.
- "Estimate future capacity" → historical token usage patterns and growth trends; "scale **SageMaker** for GenAI traffic" → **target tracking** on concurrent-request metrics, scheduled and **predictive scaling**, **scale to zero**.
- "Minutes of initialisation, low GPU utilisation, throughput collapses beyond a small batch" → custom container with tensor-parallel loading, **continuous batching** (**DJL**/**LMI**) and model **preloading**.
- "Maximise developer productivity and automate performance tuning" → **Amazon Q Developer** generating tests, finding defects and proposing optimisations and refactorings in the IDE.

## Knowledge check

<!-- KC: E2-Q68, E3-Q32, E2-Q2, E1-Q70, E2-Q31, E3-Q21, E3-Q53, E1-Q60 -->
<!-- KC-BEGIN -->
### 1. Exam 2, question 68

A healthcare analytics company is building a clinical query assistant using Amazon Bedrock. Clinicians need answers with extremely low latency during live patient consultations. Some requests require fast, lightweight reasoning, while others involve complex medical summaries and take longer to compute. A GenAI engineer must design the system to optimize responsiveness and control model invocation costs while keeping user experience smooth during peak clinic hours.

Which solution will MOST effectively meet these requirements?

- **A)** Use latency-optimized Bedrock models for simple, time-sensitive queries and enable response streaming to return partial outputs immediately, while reserving higher-capability models for complex medical summaries.
- **B)** Route every request to the most powerful available Bedrock model to minimize the chance of inaccurate responses.
- **C)** Precompute all potential responses in advance and store them in a database to eliminate Bedrock calls during consultations.
- **D)** Break each request into multiple sub-queries and send them in parallel to the same Bedrock model to reduce end-to-end latency.

<details><summary>Answer</summary>

**Answer: A.** Latency-optimized Bedrock models serve the simple, time-sensitive clinical questions from faster infrastructure, response streaming shows partial output immediately so the experience feels instant even for longer answers, and reserving higher-capability models for complex medical summaries controls cost. Routing everything to the most powerful model maximises latency and cost, pre-computing all possible responses is impossible for open clinical questions, and splitting each request into parallel sub-queries multiplies invocations without helping single-answer latency.

*Where this is covered: Unit 02, Responsive systems. Key: ours, confidence high.*

</details>

### 2. Exam 3, question 32

A multinational travel-booking platform is building a real-time itinerary assistant using Amazon Bedrock. The assistant must answer user questions instantly during flight searches, including airport restrictions, baggage rules, local weather, and visa requirements. Some of this information changes infrequently, while other elements require fresh, model-generated reasoning.

During testing, users complain about slow responses whenever the assistant must generate multi-step reasoning or fetch large contextual information. The company wants to improve responsiveness while reducing unnecessary FM invocations, especially for predictable or repetitive queries. The solution must be cost-efficient, require minimal operational overhead, and work reliably during peak traffic periods.

Which combination of actions will BEST meet these requirements? (Select TWO.)

- **A)** Pre-compute FM responses for predictable queries (baggage rules, airport policies, visa basics), store them in Amazon ElastiCache, and return cached results during peak hours.
- **B)** Migrate all inference traffic to the largest, highest-capacity FM variant to ensure faster inference, regardless of query type or complexity.
- **C)** Use Bedrock response streaming so users can see partial model output immediately, improving perceived latency for multi-step reasoning questions.
- **D)** Use Amazon Kendra to retrieve context for all queries and bypass the FM entirely for any user question that relates to known travel information.
- **E)** Enable parallel FM invocations for every user query so that multiple models generate different reasoning paths, and return the first completed response.

<details><summary>Answer</summary>

**Answer: A, C.** Pre-computing the FM answers for predictable queries such as baggage rules and visa basics into Amazon ElastiCache removes those invocations entirely and serves them in sub-millisecond time at peak, and Bedrock response streaming makes multi-step reasoning answers appear immediately, improving perceived latency for the questions that still need the model. Moving all traffic to the largest model is slower and costlier, bypassing the FM with Kendra for all known topics loses the reasoning the assistant exists for, and parallel invocations of several models per query multiplies cost.

*Where this is covered: Unit 02, Responsive systems. Key: ours, confidence high.*

</details>

### 3. Exam 2, question 2

A global insurance company is building a GenAI workflow on Amazon Bedrock to automate claim analysis. The workflow uses retrieval augmentation with Amazon OpenSearch Serverless and invokes an FM for summarization. During testing, the GenAI engineering team notices that latency varies significantly across requests. Profiling reveals two consistent patterns:

- Many requests use long prompts that include redundant historical context.
- Vector search queries return large result sets, slowing down the augmentation step before model invocation.

The team wants to optimize the system to reduce overall latency while maintaining consistent summarization quality. The solution must preserve accuracy, minimize reengineering, and require the least operational overhead.

Which solution BEST meets these requirements?

- **A)** Replace the OpenSearch vector index with a high-dimensional dense index and increase the search window size to guarantee more complete retrieval.
- **B)** Cache all retrieved documents in Amazon DynamoDB so the system always bypasses vector search, eliminating retrieval latency for most queries.
- **C)** Increase the FM’s maximum output token limit and raise the model’s temperature to produce shorter answers that compensate for latency delays.
- **D)** Use API call profiling to prune redundant prompt segments and optimize OpenSearch Serverless vector queries with filtered top-k scoring. This reduces both prompt token processing time and retrieval latency without changing the FM.

<details><summary>Answer</summary>

**Answer: D.** Profiling the API calls shows where the time goes, pruning redundant historical context from prompts cuts token processing time, and optimising the OpenSearch Serverless vector queries with metadata filters and a bounded top-k shrinks the result sets that slow the augmentation step, all without changing the FM or re-engineering the pipeline. A denser index with a larger search window returns more, not fewer, results, caching every document in DynamoDB abandons retrieval accuracy, and raising output tokens and temperature makes answers longer and less consistent.

*Where this is covered: Unit 02, Faster and better retrieval. Key: ours, confidence high.*

</details>

### 4. Exam 1, question 70

A health analytics company deploys a large foundation model on Amazon Bedrock to summarize clinical documents. As usage increases, the GenAI platform team notices throughput bottlenecks: model invocations queue during peak hours, and token processing speed varies widely based on request patterns. The team must improve throughput without increasing model size or changing the FM.

Which combination of steps will MOST effectively improve throughput for this workload? (Select TWO.)

- **A)** Use concurrent model invocation management by increasing the maximum parallel invocations per endpoint and tuning retry behavior for bursts.
- **B)** Replace the summarization model with a smaller FM even if accuracy decreases, to reduce token generation time.
- **C)** Enable batch inference for highly similar summarization requests and configure dynamic batch sizing based on real-time queue depth.
- **D)** Capture all Bedrock invocation events with EventBridge and run scheduled jobs to manually throttle or unthrottle request traffic.
- **E)** Reduce all prompt lengths by 50% regardless of content by truncating input documents to the first portion of each text.

<details><summary>Answer</summary>

**Answer: A, C.** Concurrent model invocation management, raising the maximum parallel invocations toward the quota and tuning retry behaviour for bursts, keeps the pipeline full during peaks, and batch inference for highly similar summarisation requests with dynamic batch sizing from queue depth processes many documents per invocation, both without changing the model. Swapping in a smaller FM changes the model and loses accuracy, scheduled manual throttling through EventBridge is neither real-time nor a throughput gain, and truncating every document by half destroys summary quality.

*Where this is covered: Unit 02, Throughput under load. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 5. Exam 2, question 31

A retail analytics company is building a generative AI system on Amazon Bedrock to generate product descriptions for thousands of new SKUs each week. The GenAI engineering team is receiving complaints that outputs vary too widely in creativity and tone across similar products. The team wants to optimize output consistency while still allowing small variations in style. They also want to evaluate the effect of several parameter configurations before making a production change.

Which approach will BEST meet these requirements with the MOST controlled performance?

- **A)** Use speculative decoding with a draft model to reduce latency and rely on the draft model for deterministic text patterns.
- **B)** Disable all sampling parameters by setting temperature to 0 and top-k to 1 to completely standardize outputs for all products.
- **C)** Perform A/B testing of multiple model parameter profiles, using a lower temperature with moderate top-p sampling to constrain randomness while keeping stylistic variation.
- **D)** Switch to a larger and more expensive FM for improved text quality, assuming the additional model capacity will inherently stabilize style.

<details><summary>Answer</summary>

**Answer: C.** A/B testing several parameter profiles, favouring a lower temperature with moderate top-p sampling, constrains randomness enough for consistent tone while leaving small stylistic variation, and measuring each profile before the production change is the controlled approach the team asked for. Temperature 0 with top-k 1 removes all variation and contradicts the requirement, speculative decoding is a latency technique whose draft model does not govern style, and a larger model does not stabilise tone by itself and raises cost.

*Where this is covered: Unit 02, Tuning the model's behaviour. Key: ours, confidence high.*

</details>

### 6. Exam 3, question 21

A financial services company is deploying a large language model (LLM) on Amazon SageMaker AI for real-time portfolio-risk analysis. The model requires high GPU memory, uses custom CUDA kernels, and loads several billion parameters at startup. During load testing, the team notices that model initialization takes several minutes per instance, GPU utilization remains low for many requests, and throughput drops significantly whenever concurrent requests exceed a small batch size. The deployment must reduce initialization overhead, maximize GPU efficiency, and maintain consistent performance under fluctuating traffic patterns.

Which solution will MOST effectively address the unique deployment challenges of the LLM?

- **A)** Enable SageMaker Serverless Inference so the model loads only when needed, reducing idle GPU costs while improving peak throughput.
- **B)** Use a standard SageMaker PyTorch inference container, increase the instance count with auto scaling, and rely on larger EBS volumes to reduce loading delays.
- **C)** Store model weights in Amazon S3 and stream them into GPU memory per request using presigned URLs to reduce container memory footprint.
- **D)** Use a custom SageMaker container with optimized tensor-parallel loading to spread model weights across multiple GPUs, enable continuous batching with the DJL serving stack, and preload the model on container startup to avoid repeated initialization.

<details><summary>Answer</summary>

**Answer: D.** A custom SageMaker container with tensor-parallel loading spreads the billions of parameters across the GPUs so the model fits and loads efficiently, continuous batching in the DJL serving stack keeps GPUs busy as concurrency rises, and preloading the model at container startup removes the minutes of per-instance initialisation, which together address every symptom in the stem. Serverless inference offers no GPUs and cannot host such a model, a standard PyTorch container with more instances and larger volumes does not fix slow loading or batching, and streaming weights from S3 per request would make every request pay the load time.

*Where this is covered: Unit 02, Profiling and tuning the whole system. Key: ours, confidence high.*

</details>

### 7. Exam 3, question 53

A company is developing a customer support platform that uses Amazon Comprehend for NLP and Amazon Bedrock to generate conversational responses. The front end communicates through Amazon API Gateway, which invokes an AWS Lambda function to send requests to the Bedrock API.

During load testing, the engineering team observes intermittent latency spikes and recurring ThrottlingException errors when the Lambda function calls the Bedrock API. The issues occur during high concurrency periods and degrade real-time response performance. The team must reduce throttling events and improve response resilience during peak traffic.

Which solution should be implemented to address these requirements?

- **A)** Initialize exponential backoff with jitter in the AWS SDK to smooth retry behavior, and configure API Gateway per-client throttling limits to regulate request bursts before they reach Lambda.
- **B)** Use AWS Step Functions to orchestrate each Bedrock API call and apply fixed retry intervals to reduce throttling during peak times.
- **C)** Configure Lambda reserved concurrency so a fixed number of execution environments remain available to handle peak API call volume.
- **D)** Enable AWS Global Accelerator to optimize latency when the Bedrock API is invoked from the Lambda function.

<details><summary>Answer</summary>

**Answer: A.** Exponential backoff with jitter in the AWS SDK spreads retries so throttled Bedrock calls succeed without synchronised retry storms, and API Gateway per-client throttling limits regulate bursts before they reach Lambda and the model, reducing ThrottlingException errors and smoothing latency at peak. Fixed retry intervals in Step Functions synchronise retries and add orchestration overhead, Lambda reserved concurrency guarantees Lambda capacity but does nothing about Bedrock's quota, and Global Accelerator optimises network paths for client traffic, not Bedrock throttling.

*Where this is covered: Unit 02, Throughput under load. Key: ours, confidence high.*

</details>

### 8. Exam 1, question 60

A multinational retail company is building a generative AI platform on AWS to support product analytics, code generation for microservices, and automated test creation across multiple engineering teams. Leadership wants to standardize development workflows, enforce consistent integration patterns, and accelerate experimentation while maintaining high application quality. The company decides to adopt Amazon Q Developer to streamline coding tasks, automate troubleshooting, and improve test coverage for GenAI features.

The engineering organization must select the combination of steps that will maximize developer productivity and automate performance tuning with the least operational overhead.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Use Amazon Q Developer to create custom vector store indexing logic for all microservices and deploy the logic with a centralized CI/CD pipeline.
- **B)** Configure Amazon Q Developer to manage schema migrations for all service databases and auto-deploy them with AWS CodeDeploy.
- **C)** Use Amazon Q Developer to automatically generate test cases, identify code defects, and propose optimizations directly within developer IDEs.
- **D)** Deploy Amazon Q Developer as a standalone inference endpoint on Amazon EC2 to run nightly batch validations against all GenAI components.
- **E)** Use Amazon Q Developer to perform workload-aware refactoring, accelerate application troubleshooting, and auto-suggest integration patterns aligned with company standards.

<details><summary>Answer</summary>

**Answer: C, E.** Amazon Q Developer generates test cases, finds code defects and proposes optimisations inside the developer IDE, and it performs workload-aware refactoring, accelerates troubleshooting and suggests integration patterns aligned with company standards, which is how it raises productivity and automates performance tuning with the least operational overhead. It is not a vector-indexing code generator to deploy through CI/CD, not a schema-migration manager, and not something you deploy as an EC2 inference endpoint for nightly validations.

*Where this is covered: Unit 02, Profiling and tuning the whole system. Key: ExamPro answer key (Exam 1 graded).*

</details>

<!-- KC-END -->

## Summary

Make it feel fast with **pre-computation** into **ElastiCache** or **DynamoDB** with **DAX**, **latency-optimized** models for the simple path, streaming, parallel **Step Functions** branches, and benchmarks in P95-latency-per-dollar terms tested through feature-flag **A/B** experiments. Make retrieval fast and relevant with tuned **ANN** indexes, filters and **top-k**, **hierarchical indices**, **query preprocessing** and **hybrid search** with custom scoring.

Push throughput with shorter tokens, **batch inference** and **micro-batching**, concurrency limits with backoff and **API Gateway** **throttling**, and **cross-Region inference** or **Provisioned Throughput** to lift the ceiling. Tune **temperature**, **top-p**, **top-k**, **max tokens** and **stop sequences** through controlled **A/B tests**.

Plan capacity in tokens, scale on concurrent-request metrics with scheduled and predictive rules, and profile with **X-Ray** and **Logs Insights** to apply LLM-specific latency fixes, from streaming and caching to tensor-parallel preloaded containers with **continuous batching**.
