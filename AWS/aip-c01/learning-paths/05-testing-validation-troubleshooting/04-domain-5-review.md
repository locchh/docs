# Unit 04: Domain 5 review

Decision tables for the recurring Domain 5 choices, the vocabulary that gives answers away, a one-page summary, and the mixed quiz of questions not used in units 01 to 03.

## Decision tables

**Which evaluation method?**

| Requirement wording | Answer |
|---|---|
| Compare FMs, prompts or parameters on quality, cost and latency without custom infrastructure | **Amazon Bedrock Evaluations** (managed reports) |
| Algorithmic accuracy, **robustness** or **toxicity** on a task type | Automatic evaluation job (**BERTScore**, **F1**, accuracy; **semantic robustness**; **detoxify**) |
| Stability across lightly reworded prompts | Automatic evaluation job with **robustness metrics** |
| Judge outputs for **correctness**, **completeness**, **faithfulness**, **helpfulness**, tone, **harmfulness**, **stereotyping**, **refusal**, or a **custom rubric** | **LLM-as-a-judge** evaluation job (built-in or **custom metrics**, explanations, **bring-your-own responses**) |
| Domain experts or users must rate outputs | **Human evaluation** job (own or AWS-managed team) or **Ground Truth** **annotation workflows** |
| Judge a **RAG** pipeline or **knowledge base** | **RAG evaluation** job: **retrieve-only** (**context relevance**, coverage) or **retrieve-and-generate** (**correctness**, **faithfulness**, **citation precision** and coverage) |
| **Relevance**, **factual accuracy**, **consistency** across regenerations, **fluency** | **Golden datasets**, **relevance** scoring, factual-accuracy judge prompts, **multi-pass output diffing** |
| Agent **task completion**, **tool selection**, **reasoning quality** across versions | **Amazon Bedrock Agent evaluations** (**AgentCore Evaluations**) on traces |
| Retrieval **relevance**, context alignment, latency | Labelled dataset with precision and recall at k, **MRR**, **nDCG**; vector database metrics with **CloudWatch** thresholds |

**Which testing or rollout pattern?**

| Requirement wording | Answer |
|---|---|
| Compare several variants at once on real user interactions, then choose | **A/B testing** |
| Test a new model on live traffic, same endpoint and API, gradual shift | Additional **SageMaker** **production variant** with a small initial weight |
| Route across model variants and shift 100 percent to the winner | **SageMaker** **multi-variant endpoint** |
| Copy of production traffic, no user impact | **Shadow variant** (shadow test) |
| Release one version safely with gradual exposure | **Canary** (then linear or **blue/green**) |
| Detect **semantic drift** in real time during rollout of a hosted model | **SageMaker Model Monitor** **custom metrics** on a **shadow deployment** |
| Validate a new FM version before rollout | **Synthetic user workflows**, **AI-specific validation** (**hallucination rate**, **semantic drift**, **consistency**), **quality gates** |
| Prevent regressions reaching production, automated, managed | **Bedrock Evaluations** on a **golden dataset** inside **CodePipeline** with thresholds and **quality gates** |
| Critical gate metric | **Hallucination rate** on a test set |
| Order the steps of a model replacement | Define metrics, create dataset, **A/B test**, **quality gates**, analyse and report |

**Which troubleshooting move?**

| Symptom | Cause and fix |
|---|---|
| Long inputs lose content at the end; input-too-long errors | **Context window overflow**: token diagnostics, **dynamic chunking**, **sliding window** with summaries, prompt stitching |
| Output stops mid-sentence | `stopReason = max_tokens`: raise the output limit or ask for less |
| **BDA** classifies only the first page of multi-document PDFs | Enable **document splitting**; one **blueprint** per document type |
| Malformed or silent integration failures | **Structured error logging**, **invocation logging**, **schema validation** of requests, stored malformed responses |
| Where is the latency: validation, SDK retries or the model? | **X-Ray** traces plus **Logs Insights** over prompt and response logs |
| `AccessDeniedException` / `ValidationException` / `ResourceNotFoundException` / `ThrottlingException` | Permissions or **model access** / malformed or too long / wrong ID or Region / quotas |
| Inconsistent tone or missing attributes after a prompt change | **Prompt testing framework** across versions with automated scoring |
| **RAG** returns "no relevant information" after a deploy, everything healthy | **Embedding model version mismatch** between queries and index |
| Irrelevant or outdated chunks after a data refresh | Validate chunking and preprocessing; analyse **context relevance** and **embedding drift** |
| Recommendations drift, suspect **embedding drift** | **Model Monitor** custom container for drift statistics; **parallel endpoint** with **Data Capture** and gradual traffic shift |
| **Knowledge base** ingestion failures | **Knowledge base logging** to **CloudWatch Logs**, **Logs Insights** |
| Malformed JSON, prompt confusion after template updates | **X-Ray** **prompt observability pipeline** plus **CloudWatch Logs** of invocations; keep **schema validation** on |
| Tool latency, odd call sequences, coordination failures | **CloudWatch** tool metrics with **anomaly detection** plus **invocation logs** and dashboards |
| Correlate logs, trace cross-service calls, detect GenAI error signatures | **Logs Insights**, **X-Ray**, **Amazon Q Developer** |
| Unified observability with business metrics and **forensic traceability** | **Invocation logging**, **X-Ray**, **CloudWatch** **custom metrics** and dashboards, **CloudTrail** |

## Words that give the answer away

- "Without building custom experimentation infrastructure", "managed evaluation reports" → **Bedrock Evaluations**.
- "**Robustness**", "lightly reworded prompts" → **robustness metrics**.
- "Policy compliance, multilingual accuracy at scale" → **LLM-as-a-judge** with **custom metrics**.
- "Grounding, retrieved evidence, citations" → **RAG evaluation**.
- "**Task completion rate**", "**tool selection**", "**reasoning quality** across agent versions" → Agent evaluations.
- "Same API contract", "small percentage of live traffic", "InitialVariantWeight" → **SageMaker** **production variants**.
- "Compare simultaneously" → **A/B**.
- "1 to 5 percent first" → **canary**.
- "Rate, annotate, structured feedback, feed back" → in-app feedback interface into **DynamoDB**.
- "Expert annotation" → **Ground Truth**.
- "Detect regressions", "block releases", "**golden dataset**", "CI/CD" → **Bedrock Evaluations** **quality gates** in **CodePipeline**.
- "Weekly summaries", "compare models over time", "visual dashboards" → **QuickSight** on evaluation reports and **CloudWatch** metrics.
- "Simulate real users before deployment", "**semantic drift**", "block rollout" → **synthetic workflows** with **AI-specific validation** and gates.
- "Real time during rollout", "shadow" → **Model Monitor** on a **shadow deployment**.
- "Drops context near the end", "cannot shorten" → overflow diagnostics and **dynamic chunking**.
- "First page only" → **BDA** **document splitting**.
- "Fail silently", "malformed responses" → **structured error logging**, **request validation**, **invocation logging**.
- "Upstream validation, SDK retries or the model" → **X-Ray** plus **Logs Insights**.
- "No errors, invocations succeed, cluster healthy, no relevant information" → **embedding model mismatch**.
- "After a data refresh" → chunking and preprocessing validation plus drift analysis.
- "Recommendations feel off" → **Model Monitor** drift statistics and a **parallel endpoint** with **Data Capture**.
- "Ingestion failures, which documents" → **knowledge base logging** to **CloudWatch Logs**.
- "Template updates, malformed JSON" → **X-Ray** prompt pipeline and **invocation logs**.
- "Correlate logs, trace cross-service, GenAI error signatures, no custom ML" → **Logs Insights**, **X-Ray**, **Q Developer**.
- "Manual", "weekly", "spreadsheet", "wiki", "engineering manager reviews" → always wrong.

## Domain 5 on one page

Evaluate generated text on **relevance**, **factual accuracy**, **faithfulness**, **completeness**, **consistency**, **fluency**, **helpfulness**, tone and safety. Use **golden datasets**, **reference-based metrics** and calibrated **LLM-as-a-judge** scores.

**Amazon Bedrock Evaluations** supplies four types of job:

- Automatic jobs: accuracy, **robustness** and **toxicity**.
- Judge jobs: eleven **built-in metrics** plus custom rubrics, scores 0 to 1 with explanations, and **bring-your-own responses**.
- Human jobs.
- **RAG** jobs: **context relevance** and coverage; **correctness**, **faithfulness**, **citation precision** and coverage.

Compare configurations offline on **cost-performance** and **latency-to-quality** ratios. Compare them online with production and **shadow variants** or **feature flags**: **A/B** to choose, **canary** to release.

Test retrieval separately with **labelled datasets** and ranking metrics plus latency thresholds. Test agents with **AgentCore Evaluations** on **task completion**, **tool use** and reasoning.

Turn evaluation into a process:

- Feed **golden datasets** with in-app feedback stored in **DynamoDB** and expert annotation in **Ground Truth**.
- Run **Bedrock Evaluations** continuously with **Step Functions**.
- Apply **regression thresholds** and **quality gates** in **CodePipeline**, with **hallucination rate** as the critical gate.
- Report to stakeholders with **QuickSight** dashboards and **scheduled reports**.
- Before rollout, run **synthetic user workflows** and **AI-specific validation**. During rollout, use shadow, **canary**, linear or **blue/green** exposure with **Model Monitor**. Keep rollback ready.

The model-replacement sequence is metrics, dataset, **A/B test**, **quality gates**, report.

Troubleshoot in layers with **invocation logs**, **Logs Insights**, **X-Ray** and evaluation jobs:

- Content that does not fit: overflow diagnostics and **dynamic chunking**, plus **BDA** **document splitting** for PDFs.
- Integration faults: the **Bedrock** error catalogue, structured logging, **request validation** and response analysis.
- Prompt problems: **prompt testing frameworks** across versions.
- Retrieval: embedding mismatch, drift monitoring with **Model Monitor** and shadow endpoints, chunking validation and **knowledge base logging**.
- Template decay: template tests, **invocation logs**, **X-Ray** prompt pipelines and **schema validation**.
- Agents: tool metrics with **anomaly detection**.

**Logs Insights**, **X-Ray** and **Amazon Q Developer** are the toolkit.

## Mixed quiz

<!-- KC: REVIEW -->
<!-- KC-BEGIN -->
### 1. Exam 2, question 4

A healthcare analytics company builds an internal GenAI assistant on Amazon Bedrock to automate interpretation of medical summaries. After deployment, clinicians report inconsistent response times and occasional drops in output quality. The CTO requests a complete observability approach that provides visibility into FM invocation performance, tracing across retrieval and orchestration steps, and business-level metrics such as clinician time saved per task. The solution must use managed AWS services, avoid building a separate monitoring system, and present insights in a unified view with minimal custom integration work.

Which solution will BEST meet these requirements?

- **A)** Build a custom monitoring layer by exporting FM invocation logs to DynamoDB, visualizing latency, prompt-processing patterns, and business KPIs with Amazon QuickSight, and embedding additional performance panels directly into the internal clinician portal.
- **B)** Stream all FM requests and responses into Amazon Kinesis Data Streams, use Athena to analyze latency distribution and retrieval depth, and create a custom web-based observability console to display trends, workflow traces, and clinical impact scoring.
- **C)** Enable Amazon Bedrock invocation logging, integrate AWS X-Ray tracing across the retrieval and orchestration workflow, publish business-impact metrics to Amazon CloudWatch, and use CloudWatch dashboards to unify operational telemetry and FM interaction details in a single managed interface.
- **D)** Use CloudTrail to capture FM invocation activity, store the event logs in Amazon S3 for periodic analysis, and configure a Lambda-based reporting process that generates operational summaries and clinician impact reports on a scheduled basis.

<details><summary>Answer</summary>

**Answer: C.** Enabling Bedrock invocation logging for FM interaction detail, integrating X-Ray tracing across the retrieval and orchestration workflow, publishing business-impact metrics such as clinician time saved to CloudWatch, and unifying everything on CloudWatch dashboards gives the complete observability view with managed services and minimal integration work. A DynamoDB-plus-QuickSight custom layer, a Kinesis-Athena custom console, and CloudTrail exports with scheduled Lambda reports are separate monitoring systems built by hand.

*Where this is covered: Unit 03, The troubleshooting toolkit. Key: ours, confidence high.*

</details>

### 2. Exam 2, question 37

A hospitality technology company deploys an Amazon Bedrock–powered AI concierge that handles customer inquiries, recommends services, and processes reservation requests. As usage grows, leadership wants a unified observability solution that provides actionable insights across model behavior, business impact, compliance adherence, customer interaction patterns, and forensic traceability for troubleshooting. The engineering team needs an approach that uses managed AWS services, avoids custom analytics pipelines, and supports operational metric dashboards, interaction tracking, and request-level audit trails.

Which combination of actions will BEST meet these requirements with minimal operational overhead? (Select TWO.)

- **A)** Export all interaction metadata and model inputs/outputs to S3, build an EMR-based pipeline to generate traceability reports, and visualize compliance metrics in Amazon QuickSight dashboards refreshed nightly.
- **B)** Instrument the application to push user interaction events, conversion signals, and recommendation outcomes to Amazon CloudWatch metrics. Build business impact dashboards and anomaly detection alarms directly in CloudWatch for proactive insight.
- **C)** Set up Amazon Kinesis Data Streams to capture FM invocations, build a real-time processing layer in AWS Lambda for behavior classification, and push summarized metrics into DynamoDB for downstream visualization.
- **D)** Configure AWS CloudTrail event selectors for Bedrock API calls and forward logs to an external SIEM for token usage monitoring, prompt failure analysis, and dashboarding.
- **E)** Enable Amazon Bedrock Model Invocation Logs and store them in CloudWatch Logs to capture detailed request and response traces. Use CloudWatch dashboards to visualize model behavior patterns, prompt-response correlations, and operational performance KPIs.

<details><summary>Answer</summary>

**Answer: B, E.** Pushing user interaction events, conversion signals and recommendation outcomes to CloudWatch metrics with business-impact dashboards and anomaly detection alarms covers interaction tracking and proactive insight, and Bedrock Model Invocation Logs in CloudWatch Logs with dashboards capture request and response traces for model behaviour patterns, prompt-response correlations and performance KPIs, giving forensic traceability, all managed. An EMR pipeline over S3 exports, a Kinesis-Lambda-DynamoDB layer and CloudTrail forwarding to an external SIEM are custom analytics pipelines.

*Where this is covered: Unit 03, The troubleshooting toolkit. Key: ours, confidence high.*

</details>

### 3. Exam 3, question 7

A digital media startup is building an AI-powered article-ranking engine that analyzes user reading history, sentiment scores from Amazon Comprehend, and engagement metrics stored in Amazon S3. The company has trained several Amazon SageMaker AI recommendation models and wants to evaluate which one produces the best personalization outcomes. The engineering team needs to route real-time inference traffic across multiple model variants, collect click-through metrics, compare model performance, and seamlessly shift 100% of traffic to the top-performing model—without managing custom infrastructure.

Which solution will meet these requirements with the least operational overhead?

- **A)** Launch separate Amazon EC2 instances for each model version behind a Network Load Balancer (NLB) and manually update NLB target weights based on click-through performance.
- **B)** Use Amazon SageMaker AI multi-variant endpoints to host all candidate models under a single endpoint, assign traffic weights for A/B testing, and update routing to direct all inference requests to the winning model.
- **C)** Configure Amazon API Gateway to distribute inference traffic across multiple SageMaker endpoints with weighted rules, then adjust the weights as engagement metrics change.
- **D)** Use AWS CodeDeploy blue/green deployments to alternate traffic between model versions and rely on CodeDeploy weighted routing to gradually shift traffic toward the higher-performing model.

<details><summary>Answer</summary>

**Answer: B.** A SageMaker multi-variant endpoint hosts all candidate recommendation models behind one endpoint, assigns traffic weights for A/B testing, collects the click-through metrics per variant, and shifts 100 percent of traffic to the winner by updating the weights, with no custom infrastructure. EC2 fleets behind a Network Load Balancer with manual weight changes are self-managed, API Gateway weighted rules across separate endpoints add a routing layer to maintain, and CodeDeploy blue/green alternates whole versions rather than weighting traffic among several models.

*Where this is covered: Unit 01, Comparing configurations systematically. Key: ours, confidence high.*

</details>

### 4. Exam 3, question 16

A media analytics company is building an internal generative AI system on Amazon Bedrock to analyze interview transcripts and generate summaries. After deployment, reviewers report inconsistent reasoning, shifts in narrative tone, and occasional hallucinations when the model processes emotionally charged content. The engineering team must implement a troubleshooting framework that can systematically detect these FM-specific failure modes and provide actionable insights. The solution must minimize manual review effort and support automated evaluation during ongoing development cycles.

Which approach will BEST meet these requirements?

- **A)** Use CloudTrail audit logs to track summary generation events and require engineers to manually inspect each log entry for anomalies.
- **B)** Deploy a multi-tier approval system where human reviewers must validate every model summary before it is stored, and store reviewer decisions in DynamoDB.
- **C)** Enable Enhanced Monitoring on the compute environment and configure memory and CPU alarms to identify processing anomalies that might affect summary generation accuracy.
- **D)** Implement an automated evaluation workflow that uses golden datasets with expected outputs, output diffing to compare reasoning variations across runs, and Bedrock Model Invocation Logs to trace intermediate reasoning paths for consistency analysis.

<details><summary>Answer</summary>

**Answer: D.** An automated evaluation workflow that uses golden datasets with expected outputs to measure hallucinations, output diffing to compare reasoning variations across runs, and Bedrock model invocation logs to trace intermediate reasoning paths gives systematic detection of inconsistent reasoning, tone shifts and hallucinations with minimal manual review during development. Manual inspection of CloudTrail logs and human approval of every summary are manual, and CPU or memory alarms on the compute environment cannot see reasoning quality.

*Where this is covered: Unit 03, The troubleshooting toolkit. Key: ours, confidence high.*

</details>

### 5. Exam 3, question 19

A financial services company uses several foundation models (FMs) in Amazon Bedrock to summarize customer account activity, generate advisory messages, and produce compliance explanations for regulatory reviews. After a recent FM version update, analysts reported inconsistencies in how the model summarized similar account histories, causing variations in tone and missing required compliance statements. The engineering team suspects regression in the new model version and wants a systematic quality assurance process that prevents these issues before deployment.

The company requires a solution that can:

- run automated regression tests against golden reference outputs
- validate response quality and consistency for every FM version
- block deployment if quality thresholds are not met
- integrate directly into the CI/CD pipeline without human review

Which approach best meets these requirements?

- **A)** Use an A/B testing system that routes a portion of customer traffic to the new FM version, then measures quality differences between A and B before gradually shifting all traffic.
- **B)** Use automated quality gates integrated with the CI/CD pipeline that run regression tests against golden datasets using a Bedrock-based evaluation workflow. Block deployments when response consistency or accuracy metrics fall below defined thresholds.
- **C)** Use a manual human-review process in Amazon A2I to evaluate model outputs for compliance tone, accuracy, and consistency before each deployment.
- **D)** Use Amazon CloudWatch Logs to track FM invocation patterns and create alerts when the response distribution deviates from historical norms.

<details><summary>Answer</summary>

**Answer: B.** Automated quality gates integrated with the CI/CD pipeline run regression tests against golden datasets through a Bedrock-based evaluation workflow for every FM version, validate response quality and consistency, and block deployment when metrics fall below thresholds, all without human review. A/B testing on customer traffic exposes customers to the regression, Amazon A2I is a manual human-review process, and CloudWatch alerts on invocation distributions detect problems after deployment rather than preventing them.

*Where this is covered: Unit 02, Continuous evaluation and quality gates. Key: ours, confidence high.*

</details>

### 6. Exam 3, question 60

A financial research firm deploys a GenAI summarization engine on Amazon Bedrock to assist analysts with real-time market briefings. After several weeks in production, the engineering lead notices irregular spikes in token usage, subtle degradation in summary accuracy, and occasional hallucinated numerical values. Leadership requests a comprehensive monitoring approach that can proactively identify anomalies, evaluate hallucination rates, analyze prompt effectiveness, and correlate performance with token consumption trends. The solution must rely on managed AWS services, avoid building a custom analytics pipeline, and allow teams to investigate detailed request/response behavior.

Which solution will BEST meet these requirements?

- **A)** Enable Amazon Bedrock Model Invocation Logs for detailed request and response analysis, configure Amazon CloudWatch metrics to track token usage, hallucination indicators, and prompt-effectiveness KPIs, and use CloudWatch anomaly detection and dashboards to proactively identify drift and correlate performance with token patterns in a unified managed interface.
- **B)** Export all Bedrock FM inputs and outputs to Amazon S3, build a custom prompt-evaluation engine on AWS Lambda, visualize hallucination and drift statistics in Amazon QuickSight, and generate weekly analyst performance reports via scheduled Athena queries.
- **C)** Enable AWS CloudTrail data event logging for Bedrock API calls, configure an EventBridge rule to trigger alerts on elevated request activity, and create a Lambda function that summarizes prompt trends and token anomalies into a daily email digest.
- **D)** Stream FM invocation data into Amazon Kinesis Data Firehose, create a feature-drift detection workflow in SageMaker Model Monitor, and deliver corrective performance recommendations to the engineering team through SNS notifications.

<details><summary>Answer</summary>

**Answer: A.** Bedrock Model Invocation Logs give detailed request and response analysis, CloudWatch metrics track token usage, hallucination indicators and prompt-effectiveness KPIs, and CloudWatch anomaly detection with dashboards proactively flags irregular token spikes and drift while correlating quality with token consumption in one managed interface. Exporting to S3 with a Lambda evaluation engine and QuickSight is a custom pipeline, CloudTrail data events with EventBridge and daily digests do not evaluate hallucinations, and Firehose into Model Monitor is built for feature drift on hosted models rather than FM invocation quality.

*Where this is covered: Unit 03, The troubleshooting toolkit. Key: ours, confidence high.*

</details>

### 7. Official practice question set, question 7

A company runs a question-answering application. The application uses an Amazon Bedrock knowledge base that ingests documents from multiple Amazon S3 buckets. The company needs to monitor the data ingestion process to identify and troubleshoot any issues with document processing.

Which solution will meet these requirements to monitor knowledge base operations?

- **A)** Enable AWS CloudTrail to track all API calls that relate to knowledge base operations and document ingestion activities.
- **B)** Implement Amazon Bedrock model invocation logging to capture detailed metrics about document processing and embedding generation.
- **C)** Enable Amazon CloudWatch Application Signals to automatically detect and alert on knowledge base performance issues.
- **D)** Configure knowledge base logging with Amazon CloudWatch Logs as the destination. Use CloudWatch Logs Insights to query for failed document processing.

<details><summary>Answer</summary>

**Answer: D.** Knowledge base logging with CloudWatch Logs as the destination captures per-document ingestion results, and CloudWatch Logs Insights queries find the documents that failed processing across the S3 buckets. CloudTrail records the API calls rather than document outcomes, model invocation logging covers inference rather than ingestion, and CloudWatch Application Signals monitors application performance rather than knowledge base ingestion.

*Where this is covered: Unit 03, Retrieval system issues. Key: AWS official answer.*

</details>

### 8. Official practice question set, question 10

A financial services company operates RAG for an application that answers user questions by using internal market analysis reports. The application uses Amazon Bedrock for the embedding model. The application uses an Amazon OpenSearch Service cluster as the vector store. An AWS Lambda function performs the embedding and search logic.

After a recent code update to the Lambda function, the application starts returning generic responses. For example, the application returns "no relevant information found" even for questions that previously returned accurate answers. Amazon CloudWatch Logs shows no errors. AWS X-Ray confirms successful FM invocation. The OpenSearch Service cluster is healthy. Query latency remains normal.

What is the cause of this issue?

- **A)** The Lambda function's IAM role is missing the permission for `bedrock:InvokeModel`.
- **B)** The Amazon Bedrock FM temperature parameter was increased.
- **C)** The updated Lambda function uses a different version of the embedding model.
- **D)** The document embeddings in OpenSearch Service were deleted during the application update and have not been re-indexed.

<details><summary>Answer</summary>

**Answer: C.** With no errors, successful FM invocations, a healthy cluster and normal latency, the only failure that produces generic 'no relevant information' answers is a mismatch between the embedding model used for queries and the one used for the stored documents: the updated Lambda function calls a different embedding model version, so similarities collapse. A missing IAM permission would raise access errors, temperature affects generation rather than retrieval, and deleted embeddings would leave an empty index.

*Where this is covered: Unit 03, Retrieval system issues. Key: AWS official answer.*

</details>

<!-- KC-END -->

## What to do next

You have finished the five domains. Use day 4 for the full mixed practice in the appendix (`../appendix/`), rereading the review units of Domains 1 to 3 (the heaviest weights) and the decision tables of Domains 4 and 5. Then sit the official practice question set again under exam conditions.
