# Unit 03: Monitoring systems for GenAI applications

**Task 4.3: Implement monitoring systems for GenAI applications.** This unit is about seeing what a GenAI application is doing: the operational metrics, traces and logs every application needs, the metrics that only GenAI needs (tokens, **prompt effectiveness**, **hallucination rate**, **response drift**, cost anomalies), dashboards that connect them to business outcomes, observability for tools and agents, the health of the **vector store**, and the troubleshooting frameworks that **catch** failure modes classical ML never had.

Few exam questions are pure monitoring, but monitoring vocabulary appears in options across every domain, and Domain 5 builds on this unit.

## The three layers of observability

Observability rests on three types of information:

- **Metrics** are numbers over time.
- **Logs** are records of events.
- **Traces** show the path of one request through many components.

On AWS, these live in **Amazon CloudWatch** and **AWS X-Ray**. A GenAI application adds a fourth layer, **model interaction records**. These capture the prompt, response, tokens, retrieved sources and guardrail decisions for each invocation.

A holistic system collects all four and joins them with a **correlation ID** carried from the user's request through every hop. One identifier then finds the trace, logs, invocation record and business event for a single conversation turn.

The tool family is small, with a clear role for each service:

- **Amazon CloudWatch** is the center for metrics, logs, **Logs Insights** queries, alarms, dashboards and **anomaly detection**. Its **Synthetics canaries** replay scripted requests, **RUM** provides real user monitoring, and **Application Signals** reports service-level health.
- **AWS X-Ray** adds distributed tracing.
- **AWS CloudTrail** records API activity.
- **AWS Cost Explorer**, **AWS Budgets** and **AWS Cost Anomaly Detection** cover spend.
- **Amazon QuickSight** turns exported data into business dashboards.

Two AWS features provide much of this out of the box. **Amazon Bedrock model invocation logging** records the full request and response for every `InvokeModel` and `Converse` call to **CloudWatch Logs**, **S3**, or both. Domain 3 unit 04 covers this logging.

**CloudWatch generative AI observability**, generally available since late 2025, gives curated views of latency, usage, tokens and errors for **Bedrock** models, **knowledge bases** and **AgentCore** agents. It includes **end-to-end prompt tracing** across models, **knowledge bases** and tools.

The feature accepts telemetry from **Strands Agents** and the open-source frameworks **LangChain** and **LangGraph** through **OpenTelemetry**. The **AgentCore tab** in the **CloudWatch** console provides an agent-curated view for monitoring many agents in one place. **AWS X-Ray** supplies the distributed traces that **CloudWatch** stitches into the service map.

## Metrics Bedrock gives you and metrics you add

**Bedrock** publishes runtime metrics in the `AWS/Bedrock` namespace with a `ModelId` dimension. Group them by what they tell you:

- Request activity and latency: `Invocations` and `InvocationLatency`.
- Errors and throttles: `InvocationClientErrors`, `InvocationServerErrors` and `InvocationThrottles`.
- Input and output volume: `InputTokenCount`, `OutputTokenCount` and `OutputImageCount`.
- Streaming responsiveness: `TimeToFirstToken`.
- Quota headroom: `EstimatedTPMQuotaUsage`.
- **Prompt caching**: `CacheReadInputTokens` and `CacheWriteInputTokens`.
- Legacy model activity: `LegacyModelInvocations`.

**Guardrails** add their own namespace, covered in Domain 3 unit 01. **Knowledge bases** and agents add invocation and latency metrics. **SageMaker endpoints** report invocations, latency, errors, GPU and memory utilization, and the concurrent-request metrics from unit 02.

These are your **operational metrics**: availability, latency percentiles, error and throttle rates, throughput, utilization and cost drivers such as tokens.

Publish the GenAI-specific measures yourself as **custom metrics** in an application namespace, never under `AWS/`. Use `PutMetricData` or the **embedded metric format**. The latter consists of structured log lines that **CloudWatch** turns into metrics with dimensions. Typical dimensions are feature, tenant, model, prompt version and cache hit.

**Business impact metrics** connect the model to outcomes:

- **Task completion** or **containment rate**, meaning conversations resolved without a human.
- Conversion rate.
- Customer satisfaction and thumbs-up ratio.
- Handle time saved.
- Cost per conversation.
- Revenue influenced.

**Custom dashboards** show technical and business metrics side by side. A latency regression can then be seen next to the drop in completion it caused.

## Monitoring what is specific to GenAI

The task statement lists the signals a classical monitoring stack does not have, and each has an AWS mechanism.

**Token usage.** Alarm on `InputTokenCount` and `OutputTokenCount` per model, and per application through **application inference profiles**. Use **CloudWatch anomaly detection**, which learns a metric's normal band from history and alarms when values leave it, to **catch** **token burst patterns** (a runaway agent loop, a prompt-injection campaign, a tenant abusing the service) without guessing static thresholds.

**Prompt effectiveness.** Measure whether prompts produce useful responses through several signals:

- Explicit user feedback: thumbs up or down, or ratings.
- Implicit signals: follow-up rephrasings, abandonment and time spent.
- **Task completion rates**.
- Judge-model scores on a sample.

Track every signal per prompt version so a prompt change can be evaluated. Token counts and API call rates measure efficiency, not effectiveness.

**Hallucination rates and response quality.** Keep a **golden dataset** of questions with verified answers. Run it on a schedule through **Amazon Bedrock Evaluations**, using a **SageMaker Processing** job or a **Lambda function**. **SageMaker Processing** provides managed batch compute for data and evaluation scripts.

Publish **LLM-as-a-judge** scores such as **correctness**, **completeness** and **faithfulness** as metrics. In production, track **contextual grounding scores**, **citation coverage** and **refusal rates** as continuous quality proxies.

**Response drift.** Store embeddings or judge scores of responses to a fixed set of benchmark prompts over time, and alarm when they move. **Semantic drift** appears as falling similarity to baseline answers. It can happen when a model version, prompt or retrieved corpus changes.

For hosted models, **SageMaker Model Monitor** provides data-quality and drift monitors for the same role. Its **custom metrics** can drive automated **output-diffing checks** triggered through **EventBridge**.

**Detailed request and response analysis.** Query model **invocation logs** with **CloudWatch Logs Insights** (or **Amazon Athena**, **serverless** SQL over **S3**, on the **S3** copy) to find slow, failed, malformed or unusually long interactions, to reconstruct a specific conversation, and to compare prompt patterns.

**Performance benchmarks.** Record the P50, P95 and P99 latency, **time to first token** and throughput of each model and configuration as a baseline and alarm on degradation.

**Cost anomalies.** Each cost service answers a different question:

- **AWS Cost Anomaly Detection** learns spending patterns per service, account or cost allocation tag and alerts on unexpected increases.
- **AWS Budgets** alerts when forecast or actual spend crosses thresholds.
- **Cost Explorer**, filtered by **application inference profile tags**, shows which application drove the change.

## From dashboards to decisions

An integrated observability solution turns signals into action. Give each audience the view it needs:

- **Operational dashboards** in **CloudWatch** support the on-call engineer.
- **Business impact visualisations** in **Amazon QuickSight** show stakeholders trends and outcomes from results and metrics exported to **S3**. **QuickSight** is the **serverless** business-intelligence service.
- **Compliance monitoring dashboards** show guardrail intervention counts, **PII detections** and policy-check failures.
- **Forensic traceability** uses **AWS CloudTrail** joined with **invocation logs** and **correlation IDs**. It supplies the audit record regulators ask for: who called which API, when and from where.
- **User interaction tracking** uses **CloudWatch RUM**, or real user monitoring. Its JavaScript agent records page loads, errors and user journeys in the web application, so a slow model call can be tied to the user experience.
- **Model behaviour pattern tracking** watches response-length distributions, **refusal** rates, topic mix and response sentiment to notice change before users complain.

Automated reports summarize the week. Alarms route through **SNS** and **EventBridge** to on-call teams and remediation workflows.

For a pipeline that analyses thousands of images and videos and must present aggregated trends with the least operational overhead, the managed shape is a **Step Functions** workflow calling **Bedrock** multimodal models, results stored in **S3**, and a **QuickSight** dashboard on top; GPU containers, custom training pipelines and hand-built UIs are the operational overhead the question excludes.

## Watching tools and agents

Agents add a layer that needs its own telemetry: which tools were called, how often, how long they took, how often they failed and whether the agent used them well. Instrument tools at three levels:

- **Call metrics** record call count, latency, error rate and success rate.
- **X-Ray subsegments** or **AgentCore Observability spans** trace sessions, steps, tool invocations and tokens per step.
- **Usage baselines** with **CloudWatch anomaly detection** raise an alarm when a tool is suddenly called ten times per request, or never.

Add **effectiveness metrics** to ask whether the task completed, how many steps it took and how often a human intervened.

For **multi-agent systems**, track handoffs, supervisor routing decisions and end-to-end task latency. This makes coordination failures, such as loops or ping-pong between agents, visible. The agent-curated view in the **CloudWatch** console shows all agents and their tool usage in one place. Automated tests validate tool behavior under load before release.

## Operating the vector store

A **RAG** application is only as good as its index, so the **vector store** needs operational management of its own.

**Performance monitoring.** Choose metrics for the store you operate:

- **Amazon OpenSearch Service**: search and indexing latency, request rates, `JVMMemoryPressure`, CPU, free storage and k-NN graph memory. **JVM memory pressure** is the share of Java heap in use; sustained high values mean the index no longer fits.
- **OpenSearch Serverless**: search and indexing compute units consumed, plus query latency.
- **Aurora pgvector**: the usual database metrics plus query latency.

Alarm on latency percentiles and error rates. Display them alongside **retrieval quality metrics**, including **relevance** scores and the share of queries with no good match.

**Automated index optimisation routines.** Use scheduled **Lambda functions** or **Step Functions workflows** for maintenance:

- **Force merge** the index's segments, its internal storage files, after bulk loads.
- Lengthen the **refresh interval** during heavy ingestion. This interval determines how often new documents become searchable.
- Warm the k-NN index into memory.
- Delete stale or duplicate vectors.
- Monitor index size and fragmentation.
- When the **embedding model** changes, **re-embed and re-index** the whole corpus. Every vector must come from the same model.

**Knowledge Bases** logs each ingestion job to **CloudWatch Logs**, **S3** or **Amazon Data Firehose**, the streaming delivery service. Failed documents and embedding errors are then visible and can trigger retries.

**Data quality validation.** Check the data before indexing and test retrieval periodically:

- **AWS Glue Data Quality** applies rules to structured metadata.
- **SageMaker Data Wrangler** supplies dataset reports.
- **Lambda** checks for empty or truncated chunks, encoding problems and missing metadata.
- Periodic retrieval tests against a **golden query set** **catch** silent **relevance** regressions.

Back up the store with **OpenSearch snapshots** or database backups, and test restores. Track **index freshness**, the time since the last successful sync, as a metric.

The most useful monitoring trio for a **knowledge base** is query latency, retrieval **relevance** score and update frequency. Infrastructure metrics alone miss the quality dimension.

## Troubleshooting frameworks (a preview of Domain 5)

GenAI systems fail in ways classical ML systems do not: outputs that are fluent but wrong (hallucinations), answers that change between identical or near-identical requests (inconsistency), reasoning that reaches a conclusion through a flawed chain, and outputs that shift as prompts, models or corpora change. The task statement names four techniques, each of which Domain 5 develops:

- **Golden datasets** with verified answers, run on a schedule, to measure **hallucination** and accuracy rates, with a judge model scoring factual **consistency**.
- **Output diffing**: generate systematic variations of the same question, compare responses with semantic similarity, and compare today's answers to historical baselines for the same prompts to detect divergence and temporal drift.
- **Reasoning path tracing**: **chain-of-thought** prompting and agent traces logged so the intermediate steps can be checked for logical errors, circular reasoning and unsupported conclusions.
- **Specialised observability pipelines**: **CloudWatch Logs**, **Lambda** and **S3** collecting multi-dimensional quality signals (factuality, **consistency**, reasoning, **toxicity**), an automated triage that categorises failures and routes them to remediation, and a feedback loop into prompts, **guardrails** and **golden datasets**.

## Worked scenario

A retailer's shopping assistant runs on **Bedrock** with an agent that calls inventory and pricing tools. Leadership wants one view of whether it works, costs what it should, and helps sales, and the on-call team wants to know about problems before customers do.

The foundation is the built-in telemetry. **Bedrock**'s **CloudWatch** metrics (invocations, latency, errors, throttles, input and **output tokens**, **time to first token**) are charted per model, **model invocation logging** captures every request and response to **CloudWatch Logs**, **X-Ray** traces each request through **API Gateway**, **Lambda**, retrieval and the model call with a correlation identifier, and **CloudWatch generative AI observability** shows the agent's sessions, tool calls and token use in one curated view. The application adds **custom metrics** in its own namespace through the **embedded metric format**: conversion after an assistant interaction, **containment rate**, thumbs-up ratio and cost per conversation.

The GenAI-specific signals follow. **CloudWatch anomaly detection** on token counts catches a runaway agent loop before the bill does; explicit user ratings and rephrasing rates, tracked per prompt version, measure **prompt effectiveness**; a **golden dataset** of two hundred product questions runs nightly through a **Bedrock** evaluation job and publishes **hallucination** and **correctness** scores as metrics; embeddings of the answers to a fixed benchmark set are compared with a baseline weekly to detect **semantic drift**; **Logs Insights** over the **invocation logs** reconstructs any conversation a customer complains about; and **Cost Anomaly Detection** watches spend by **application inference profile** tag.

Dashboards serve two audiences: a **CloudWatch** dashboard with operational and quality metrics for on-call, alarms routed through **SNS** and **EventBridge** to remediation, and a **QuickSight** dashboard over exported metrics for leadership, with **CloudWatch RUM** tying slow model calls to what shoppers experienced. The tools get their own metrics (duration, success rate, retries, error category) with anomaly baselines, so a pricing tool suddenly called ten times per request is noticed. The **OpenSearch** **vector store** is watched for search latency, memory pressure and **index freshness**, with a scheduled **Lambda** job merging segments and re-embedding when the model changes, and **Glue Data Quality** validating catalogue data before ingestion. When the exam describes this scenario it asks for complete visibility with managed services and no separate monitoring system; the answer is **invocation logging**, **X-Ray**, **CloudWatch** metrics and dashboards, **anomaly detection**, and **QuickSight** for the business view.

## Exam lens

- "Complete visibility into FM application performance" → **CloudWatch** metrics and dashboards, **X-Ray** tracing, model **invocation logs**, custom business metrics; **CloudWatch generative AI observability** for **Bedrock** and **AgentCore**.
- "**Token burst patterns**", "anomalies in consumption" → **CloudWatch anomaly detection** on token metrics.
- "Detailed request and response analysis" → **Bedrock** model **invocation logs** with **Logs Insights**.
- "**Forensic traceability**", "who called which API" → **AWS CloudTrail**.
- "Cost anomalies for GenAI services" → **AWS Cost Anomaly Detection** and **Budgets**, with **application inference profile** tags.
- "**Business impact metrics**" → user engagement, conversion, satisfaction, containment, cost per conversation; not CPU, tokens or API counts.
- "**Prompt effectiveness**" → user engagement and feedback with responses, per prompt version.
- "Monitor many agents and their tool usage in one place" → the **AgentCore** tab in the **CloudWatch** console; tool call patterns with baselines and **anomaly detection**.
- "**Knowledge base** monitoring" → query latency, retrieval **relevance** score, update frequency.
- "Detect hallucinations over time" → **golden datasets** with scheduled evaluations; "logical errors in reasoning" → **reasoning path tracing**; "**response consistency**" → **output diffing**.
- "Aggregate visual insights with least overhead" → **Step Functions**, **Bedrock** multimodal models, **S3**, **QuickSight**.

## Knowledge check

Only one question in the exam files is pure Domain 4 monitoring. Five more that test this unit's content sit in Domain 5 (Exam 2 questions 4, 37 and 47, Exam 3 questions 16 and 60), so treat them as this unit's practice too.

<!-- KC: E1-Q30 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 30

A media analytics startup wants to build an automated system that identifies emerging clothing patterns from global street-style photos and short-form runway video clips. The company wants to highlight trending color palettes, fabric types, and accessory pairings. The solution must process thousands of images and videos per day, extract visual attributes, and present aggregated insights in a business dashboard.

The engineering team wants the lowest operational overhead, minimal custom ML code, and a fully managed orchestration layer. The company prefers a serverless architecture and wants to avoid managing GPU infrastructure.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Use AWS Step Functions to orchestrate calls to Amazon Bedrock multimodal foundation models for image and video analysis. Store extracted attributes in Amazon S3 and use Amazon QuickSight dashboards to summarize trend patterns.
- **B)** Deploy a containerized PyTorch model on Amazon ECS with GPU-based tasks. Stream video frames into the model, store attributes in Amazon OpenSearch Service, and build dashboards in OpenSearch Dashboards.
- **C)** Build custom training pipelines with Amazon SageMaker to train a computer vision model for clothing classification. Use Amazon EMR to aggregate attributes and create dashboards in Amazon Managed Grafana.
- **D)** Use Amazon Rekognition labels for all visual analysis and push results to Amazon DynamoDB. Build a custom UI that aggregates results and renders dashboards through an Amazon CloudFront distribution.

<details><summary>Answer</summary>

**Answer: A.** Step Functions provides the fully managed orchestration, Bedrock multimodal foundation models analyse the images and video clips with no custom ML code or GPU infrastructure, S3 stores the extracted attributes, and QuickSight dashboards summarise the trends, giving a serverless pipeline with the least operational overhead. GPU tasks on ECS, custom SageMaker training with EMR aggregation, and Rekognition labels with a hand-built CloudFront UI all add infrastructure or custom code the company wants to avoid.

*Where this is covered: Unit 03, From dashboards to decisions. Key: ExamPro answer key (Exam 1 graded).*

</details>

<!-- KC-END -->

## Summary

Collect metrics, logs, traces and **model interaction records** with a **correlation ID**, using **Bedrock**'s **CloudWatch** metrics (invocations, latency, errors, throttles, token counts), **invocation logging**, **X-Ray** and **CloudWatch generative AI observability**, and add custom application and business metrics.

Watch the GenAI-specific signals: token bursts with **anomaly detection**, **prompt effectiveness** through user feedback, **hallucination** rates with **golden datasets** and **Bedrock Evaluations**, **response drift** with semantic baselines, and cost anomalies with **Cost Anomaly Detection** and **Budgets**. Turn them into dashboards (**CloudWatch**, **QuickSight**), compliance views, **CloudTrail** forensics and **RUM**-based user tracking.

Instrument tools and agents with call metrics, spans and baselines, operate the **vector store** with performance metrics, automated index maintenance and data quality checks, and preview Domain 5's troubleshooting frameworks: **golden datasets**, **output diffing**, **reasoning path tracing** and specialised pipelines.
