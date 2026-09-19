# Unit 04: Domain 4 review

Decision tables for the recurring Domain 4 choices, the vocabulary that gives answers away, a one-page summary, and the mixed quiz of questions not used in units 01 to 03.

## Decision tables

**Which cost technique?**

| Requirement wording | Answer |
|---|---|
| Long histories, unnecessary context sent every time | **Context pruning** (drop irrelevant turns and documents) and **context-window optimisation** (**sliding window**, summaries, retrieval) |
| Responses longer than needed | **Response-size controls**: `maxTokens`, **stop sequences**, length instructions; never truncate after generation |
| Long documents in prompts | **Prompt compression** |
| Know the cost before calling | **CountTokens** API or a model-specific tokeniser |
| Attribute spend by team or application | **Application inference profiles** with **cost allocation tags**, **Cost Explorer**, **Budgets**, **Cost Anomaly Detection** |
| Same static prefix in every request | **Bedrock prompt caching** |
| Same question in different words, many times | **Semantic caching** (embeddings plus **ANN** similarity, **MemoryDB** or **OpenSearch**) |
| Identical requests | **Exact-match cache** with **deterministic request hashing** (**ElastiCache** or **DynamoDB**) |
| Predictable public answers for global users | **CloudFront** or **API Gateway** **edge caching** |
| Work that is not interactive | **Bedrock batch inference** (discounted) or **batch transform** |

**Which model and routing?**

| Requirement wording | Answer |
|---|---|
| Most queries simple, some complex, one high-end FM today | Classifier routing to FM tiers, or **intelligent prompt routing** within a family; **Prompt Management** holds the templates |
| Compare candidates on quality versus cost | **Bedrock Evaluations** plus price-to-performance (quality per dollar, **P95 latency per dollar**) |
| Escalate only on low confidence | **Model cascading** |
| Primary throttled or down | Fallback to a cheaper model or another Region |
| Time-sensitive simple requests | **Latency-optimized inference** for those, larger models for the rest |

**How do I get more throughput and utilisation?**

| Requirement wording | Answer |
|---|---|
| Latency and **throttling** at peak, GPU underutilised | Application-layer **request batching** (**batch size** and timeout); **continuous batching** in **LMI containers** |
| 8 GPUs, weights fit in 4, sequence length far too large | **Tensor parallelism** of 4 with two replicas; smaller **maximum sequence length** for a larger rolling batch |
| Invocations queue at peak, same FM | **Concurrent invocation management** with tuned retries plus **batch inference** with **dynamic batch sizing** |
| "Too many requests" at seasonal peaks, same model and API | **Cross-Region inference** |
| ThrottlingException from **Lambda** under concurrency | SDK **exponential backoff with jitter** plus **API Gateway** per-client **throttling** |
| Bursty traffic, token-heavy requests, **Bedrock** | Token-based capacity planning from invocation metrics; **Provisioned Throughput** sized to token volume for the base, **on-demand** for spikes |
| Minutes of model initialisation, low GPU use, throughput collapses | Custom container with tensor-parallel loading, **continuous batching** (**DJL**/**LMI**), **preloading** at startup |
| Scale **SageMaker** for GenAI traffic | **Target tracking** on `ConcurrentRequestsPerModel` / `ConcurrentRequestsPerCopy`, scheduled and **predictive scaling**, **scale to zero** for **inference components** |

**How do I make it faster?**

| Requirement wording | Answer |
|---|---|
| Predictable repetitive queries | Pre-compute into **ElastiCache** or **DynamoDB** (**DAX** for microseconds) |
| Multi-step reasoning feels slow | **Response streaming** |
| Several independent model calls per request | **Step Functions** Parallel or Map |
| Slow retrieval with large result sets | **ANN index** tuning (**HNSW** `m`, `ef_construction`, `ef_search`; **IVF**), **metadata filters**, filtered **top-k**, **hierarchical indices**, **query preprocessing** |
| Vector search misses exact terms | **Hybrid search** with custom scoring and reranking |
| Where does the time go | **X-Ray** profiling of prompt-completion patterns, **Logs Insights** over **invocation logs** |
| Outputs vary too much, keep some variety, test first | **A/B test** **parameter profiles**: lower **temperature**, moderate **top-p** |

**Which monitoring signal or tool?**

| Requirement wording | Answer |
|---|---|
| Token bursts, unusual consumption | **CloudWatch anomaly detection** on `InputTokenCount` / `OutputTokenCount` |
| Detailed request and response analysis | **Bedrock** model **invocation logs** with **Logs Insights** |
| Who called which API | **CloudTrail** |
| Spend deviates | **AWS Cost Anomaly Detection**, **Budgets**, **Cost Explorer** by inference-profile tag |
| Business impact | Engagement, conversion, satisfaction, containment, cost per conversation |
| **Prompt effectiveness** | User engagement and feedback per prompt version |
| **Hallucination rate** over time | **Golden dataset** with scheduled **Bedrock Evaluations** |
| **Response consistency** or drift | **Output diffing**, **semantic drift** against baselines |
| Logical errors in reasoning | **Reasoning path tracing** (**chain-of-thought** logs, agent traces) |
| Many agents and their tools in one view | **CloudWatch generative AI observability**, **AgentCore** tab |
| **Knowledge base** health | Query latency, retrieval **relevance** score, update frequency |
| Aggregate insights with least overhead | **Step Functions**, **Bedrock** multimodal models, **S3**, **QuickSight** |

## Words that give the answer away

- "Reduce token usage", "long conversation history", "overly long responses" → pruning plus `maxTokens`; "long documents" adds **prompt compression**. "**Speculative decoding**" in a cost question is the distractor (it is a latency technique).
- "Same handbook in every request" → **prompt caching**.
- "Near-duplicate", "semantically similar", "different wording" → **semantic caching**; "exact match" and "canonical string" are the weaker options.
- "All queries go to the high-end model", "75 percent simple" → tiered routing or **intelligent prompt routing**; "no **fine-tuning**" confirms it.
- "GPU utilisation low", "scales out frequently" → batching or right-sized **tensor parallelism** and sequence length.
- "Too many requests", "same model and API", "cost-effective" → **cross-Region inference**.
- "guaranteed capacity, steady high volume" → **Provisioned Throughput**.
- "Instantly", "time-sensitive", "partial output immediately" → **latency-optimized inference** and streaming.
- "Predictable queries" → **pre-computation**.
- "Complex workflows" → **Step Functions** parallel branches.
- "Large result sets", "redundant context", "profiling" → filtered **top-k** queries and prompt pruning.
- "**Consistency** with some variation", "evaluate before production" → **A/B test** **parameter profiles**; "**temperature** 0 and **top-k** 1" removes all variety.
- "Minutes to initialise", "custom CUDA kernels" (custom GPU code), "billions of parameters" → tensor-parallel loading, **continuous batching**, **preloading** in a custom container; "**serverless inference**" has no GPUs.
- "Token burst", "anomalies" → **CloudWatch anomaly detection**.
- "Forensic", "audit of API calls" → **CloudTrail**.
- "Business impact" → engagement and conversion, never CPU.
- "Least operational overhead" plus "dashboard" → managed orchestration (**Step Functions**), managed models (**Bedrock**), **S3** and **QuickSight**.

## Domain 4 on one page

Cost is tokens times requests times price. Work through the controls in order:

1. Measure tokens with **CountTokens**, `usage` and **CloudWatch** token metrics. Use **application inference profiles** for attribution.
2. Reduce tokens with **context pruning**, **context-window optimisation**, **prompt compression** and **response-size controls**.
3. Choose the cheapest model that clears a measured quality bar. Route by complexity with a classifier or **intelligent prompt routing**, and generate offline in batch.
4. Cache at four levels: exact-match hashing, semantic similarity, edge and **Bedrock prompt caching**.

Raise utilisation with continuous and **application-layer batching**, right-sized **tensor parallelism** and sequence lengths, and token-based capacity planning. Use committed **Provisioned Throughput** for the base load and **cross-Region inference** for spikes. Auto scale on concurrent-request metrics with scheduled rules and **scale to zero**.

Performance is perceived first. Match each technique to the part of the request it improves:

- Responsiveness: pre-compute predictable answers into **ElastiCache** or **DynamoDB** with **DAX**, use **latency-optimized inference** for the quick path, stream long responses and parallelize independent calls with **Step Functions**. Benchmark in P95-latency-per-dollar terms through feature-flag **A/B tests**.
- Retrieval: tune **ANN** indexes, filters and **top-k**. Use **hierarchical indices**, **query preprocessing** and **hybrid search** with custom scoring.
- Throughput: reduce tokens, batch requests, set concurrency limits with backoff and **API Gateway** **throttling**, and use **cross-Region inference** or **Provisioned Throughput**.

Tune **temperature**, **top-p**, **top-k**, **max tokens** and **stop sequences** through controlled experiments, and plan capacity in tokens. **X-Ray** and **Logs Insights** show where the time goes. Apply the LLM-specific fix that fits: streaming, caching, smaller models, **quantisation**, **speculative decoding** or preloaded tensor-parallel containers.

Monitoring adds the GenAI layer to metrics, logs and traces:

- Collect **Bedrock**'s **CloudWatch** metrics and **invocation logs**, **CloudWatch generative AI observability** for models and **AgentCore** agents, **X-Ray** traces, and custom and business metrics.
- Watch token anomalies with **anomaly detection**, **hallucination** and quality with **golden datasets** and **Bedrock Evaluations**, and **semantic drift** against baselines.
- Monitor spend with **Cost Anomaly Detection** and **Budgets**.
- Present dashboards in **CloudWatch** and **QuickSight**, use **CloudTrail** for forensics and **RUM** for users.
- Track tool and agent telemetry against baselines.
- Maintain **vector store** health through automated index maintenance and data quality checks.

Domain 5 develops the troubleshooting frameworks: **golden datasets**, **output diffing**, **reasoning path tracing** and specialized pipelines.

## Mixed quiz

<!-- KC: REVIEW -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 48

A social media analytics company deployed a customized transformer model to an Amazon SageMaker AI endpoint using DJL Serving. The endpoint runs on GPU instances with 8 GPUs each. As usage increases, the AI engineer notices high costs because the endpoint scales out frequently, even though GPU utilization per instance remains low.

Log analysis shows that the model was configured for a maximum sequence length far larger than what real production queries require. Profiling also reveals that the model's weights and activation memory fit within 4 GPUs, but DJL is currently configured to spread the model across all 8 GPUs. The engineering team wants to improve utilization and reduce cost without refactoring the model.

Which combination of steps will improve resource efficiency with minimal operational overhead? (Select TWO.)

- **A)** Use a tensor parallelism degree of 4, allowing two full model replicas per instance and increasing concurrency.
- **B)** Increase the number of SageMaker AI instances while lowering the batch size to reduce contention across GPUs.
- **C)** Reduce the model's maximum sequence length so that DJL can allocate more memory to larger rolling batch sizes and increase throughput.
- **D)** Split the model evenly across all 8 GPUs to guarantee that GPU memory is fully utilized by a single replica.
- **E)** Enable speculative decoding to accelerate token generation across all GPUs and reduce per-request latency.

<details><summary>Answer</summary>

**Answer: A, C.** Because the model fits in four GPUs, a tensor parallelism degree of 4 runs two full replicas per 8-GPU instance and doubles concurrency, and reducing the oversized maximum sequence length frees GPU memory for larger rolling batches and higher throughput, so the endpoint stops scaling out with idle GPUs; neither change refactors the model. More instances with smaller batches increases cost, spreading one replica across all eight GPUs is the current waste, and speculative decoding targets per-request latency rather than utilisation.

*Where this is covered: Unit 01, Getting more out of the capacity you pay for. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 1, question 51

An ecommerce company operates a generative AI service that uses Amazon Bedrock to produce product descriptions and personalized recommendations. The application currently runs in a single AWS Region. During high-traffic periods such as seasonal sales, requests to the foundation model begin failing with the message "Too many requests, please wait before trying again."

The company must increase throughput during peak periods without adding operational overhead. The solution must remain compatible with the current Amazon Bedrock API and must continue using the same foundation model.

Which solution will meet these requirements in the MOST cost-effective way?

- **A)** Purchase provisioned throughput for the foundation model in the primary Region to guarantee higher request capacity.
- **B)** Use prompt routing to distribute traffic across multiple foundation models within the same family to increase capacity.
- **C)** Create an AWS Lambda wrapper function that attempts inference in the primary Region and falls back to a secondary Region upon throttling errors.
- **D)** Use cross-Region inference to distribute model invocations across multiple AWS Regions while still using the same foundation model and API structure.

<details><summary>Answer</summary>

**Answer: D.** Cross-Region inference routes model invocations to other Regions in the geography that have capacity while keeping the same foundation model and API structure, so throttling at seasonal peaks disappears without new infrastructure and at on-demand prices. Provisioned Throughput reserves capacity you pay for all year, prompt routing changes the model used, and a Lambda wrapper with a manual fallback Region is custom infrastructure that reinvents what cross-Region inference already does.

*Where this is covered: Unit 02, Throughput under load. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 3, question 20

A global telecom provider is building a GenAI-powered troubleshooting assistant for its customer-support portal. The system uses Amazon SageMaker JumpStart to generate domain-specific embeddings for historical support transcripts and Amazon Bedrock to produce real-time LLM responses. Support agents frequently submit highly similar troubleshooting questions—often differing only by a few words—which results in repetitive Bedrock invocations, increased latency, and higher operational cost.

The engineering team needs a mechanism that can detect semantically similar queries, return previously generated answers when appropriate, and only invoke the foundation model when a question is genuinely new. The solution must support fast vector similarity search and integrate efficiently with the existing embeddings pipeline.

Which approach will BEST fulfill these requirements?

- **A)** Store embeddings and cached responses in Amazon MemoryDB with vector search enabled, and perform semantic similarity checks to return cached answers before invoking the foundation model.
- **B)** Cache full user queries in an in-memory key-value store and return responses only when an exact string match is found to avoid unnecessary FM calls.
- **C)** Use Amazon Kendra to index the cached questions and answers and rely on its keyword-based search to retrieve previously answered queries.
- **D)** Save embeddings in a traditional PostgreSQL database and perform exact SQL lookup queries on the stored text before invoking the FM.

<details><summary>Answer</summary>

**Answer: A.** Amazon MemoryDB with vector search stores the query embeddings and their cached responses in memory and performs a fast semantic similarity check, returning a previous answer when a new troubleshooting question is close enough and invoking the FM only for genuinely new questions, which integrates directly with the existing SageMaker JumpStart embeddings pipeline. Exact string matching misses questions that differ by a few words, Kendra's keyword search is not a vector similarity cache, and exact SQL lookups on stored text in PostgreSQL ignore the embeddings entirely.

*Where this is covered: Unit 01, Intelligent caching. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## What to do next

Move to Domain 5 (`../05-testing-validation-troubleshooting/`), which turns the monitoring signals from this domain into evaluation methods, test suites and troubleshooting procedures for GenAI applications.
