# Unit 01: Evaluation frameworks and Amazon Bedrock Evaluations

**Task 5.1: Implement evaluation systems for GenAI (assessment frameworks, systematic model evaluation, comprehensive assessment, retrieval quality testing, agent performance).** This unit is about measuring generated output. It explains why classical ML metrics are not enough, what **Amazon Bedrock Evaluations** offers (automatic, **LLM-as-a-judge**, human and **RAG evaluation** jobs), how to compare models, prompts and parameters systematically and in production, how to test retrieval on its own, and how to evaluate agents. Unit 02 turns these instruments into processes; unit 03 uses them to troubleshoot.

Domain 5 is 11 percent of the exam. Its questions describe quality problems and ask for a *systematic, repeatable, managed* evaluation approach; manual review, spreadsheets and infrastructure metrics are always the distractors.

## Why GenAI evaluation is different

A classifier has one right answer per input, so **accuracy**, **precision**, **recall** and **F1** settle the matter. A generated paragraph has many acceptable answers and many ways to be wrong. Evaluation therefore needs several **dimensions** rather than a single score:

- **Relevance**: does the answer address the question?
- **Factual accuracy**, or **correctness**: is it true when checked against a reference or the world?
- **Faithfulness**, or **groundedness**: does it stay within the provided context? This addresses the **RAG** form of **hallucination**.
- **Completeness**: does it cover every part of the question?
- **Consistency**: does it give the same answer to the same or lightly reworded question, including across regenerations?
- **Fluency** and **coherence**: is it well written and logical?
- **Helpfulness**, **style and tone**: these are additional dimensions of the generated answer.
- **Harmfulness**, **toxicity**, **stereotyping** and **refusal**: these are the safety dimensions.

Two families of metrics measure these dimensions. **Reference-based metrics** compare the output with an expected answer. They require a **golden dataset** of inputs with verified expected outputs, and the metric depends on the task:

- For question answering, use exact or **F1 token overlap**.
- For summaries, use **BERTScore** or **ROUGE**. **BERTScore** computes semantic similarity between the candidate and reference with a language model. **ROUGE** measures overlap of word sequences.
- For classification, use **accuracy**.

**Reference-free metrics** judge the output on its own or against its context. Today, most are produced by an **LLM-as-a-judge**: a strong model reads the prompt and response, plus any reference or retrieved context, and scores the response against a **rubric**. It returns a number and an explanation.

Judges scale, cost little, and correlate well with humans when calibrated on a sample of human ratings. Humans remain the **ground truth** for taste, domain **correctness** and edge cases.

A policy assistant whose outputs are inconsistent, sometimes wrong and unevenly fluent needs a formal framework with four parts:

- **Golden reference datasets** with expected outputs.
- **Relevance scoring functions**.
- **Factual-accuracy benchmarking prompts** for a judge.
- **Consistency checks by multi-pass output diffing**: generate several times and compare the answers for divergence.

Automate the checks so they are repeatable. **QuickSight** trend dashboards of writing style, **CloudTrail**-triggered length alerts and daily manual review do not provide that framework.

## Amazon Bedrock Evaluations

**Amazon Bedrock Evaluations** is the managed evaluation service inside **Bedrock**. To create an **evaluation job**, choose a prompt dataset, the thing to evaluate, the metrics and an **S3** location for the report. The dataset can be JSONL in **S3** or one of the built-in datasets. Results also appear in the console with per-metric summaries.

The AWS evaluation toolbox contains several options:

- **Amazon Bedrock Evaluations** evaluates models and **RAG pipelines**.
- **AgentCore Evaluations** evaluates agents.
- **SageMaker Clarify**, with the open-source `fmeval` library, evaluates models you host.
- **RAGAS** and **DeepEval** are open-source libraries for running evaluation yourself.
- **SageMaker Ground Truth** and **Bedrock human evaluation jobs** support human review.

This unit starts with **Bedrock Evaluations** because it is the managed answer the exam expects. Four job types cover the task statement.

**Automatic (programmatic) model evaluation** runs a **generator model** over the dataset. It computes algorithmic metrics for **general text generation**, **text summarisation**, **question answering** or **text classification**. The metrics cover three areas:

- **Accuracy** uses real-world knowledge for open generation, **BERTScore** for summaries, **F1** for question answering and accuracy for classification.
- **Robustness** measures how output quality changes when prompts are lightly perturbed. The job re-runs the model with typos, case changes, whitespace changes and numbers written as words. A model whose answers swing under small surface changes scores poorly on this **semantic robustness** test. The exam treats clusters of lightly reworded prompts as the same test.
- **Toxicity** is scored by the open-source **detoxify** classifier.

You can use built-in datasets such as **BoolQ**, **TriviaQA**, **Natural Questions**, **Gigaword**, **BOLD** and **RealToxicityPrompts**, or supply your own.

Suppose a fintech sees different advice for reworded prompts and has grouped prompt variants per question. An evaluation job with **robustness metrics** enabled provides the quantitative stability analysis. **Batch inference** plus **Athena** cosine similarity, a **Step Functions** paraphrasing loop with manual analysis, or a **SageMaker Processing** job with a custom drift score are the distractors.

**LLM-as-a-judge model evaluation** uses two models: the **generator** under test and the **evaluator**, or judge. They must be available in the same Region. Eleven **built-in metrics** each come with a published judge prompt:

- **Correctness**
- **Completeness**
- **Faithfulness**
- **Helpfulness**
- **Logical coherence**
- **Relevance**
- **Following instructions**
- **Professional style and tone**
- **Harmfulness**
- **Stereotyping**
- **Refusal**

Add **custom metrics** when you need your own instructions and numeric or categorical scoring schema. Examples include policy compliance, multilingual accuracy and brand voice. Scores are normalized to 0 to 1, with a natural-language **explanation** for each response, so a low score is actionable. A reference answer per prompt can sharpen **correctness** and **completeness** scoring.

You can also **bring your own inference responses**. In that mode, **Bedrock** skips generation and evaluates outputs you produced anywhere, such as a **SageMaker** endpoint, another cloud or a previous production run.

For a marketplace evaluating several models' descriptions for harmful content, regulatory violations, multilingual accuracy and policy alignment at scale, choose **LLM-as-a-judge** in **Bedrock Evaluations** with **custom metrics**. Keyword and regex counts, vector-similarity comparison in **OpenSearch**, and **RAG evaluation** of **knowledge bases** measure the wrong things.

**Human evaluation** jobs send prompts and model responses to people. Use your **own work team**, managed through the console as an **Amazon Cognito user pool**, or an **AWS managed team** whose scope you agree with AWS. The **user pool** is the user directory.

A job compares up to two models. Reviewers follow instructions you write and rate the responses using methods such as:

- A **Likert scale**, a 1-to-5 agreement scale.
- Thumbs up or down.
- **Ordinal ranking** of several responses.
- A choice between two responses.

Use humans to calibrate judge metrics, cover domain **correctness** a judge cannot verify, and give final sign-off on high-stakes releases.

**RAG evaluation** jobs evaluate a retrieval-augmented pipeline. This can be an **Amazon Bedrock Knowledge Base** or your own **RAG** system through **bring-your-own inference responses**.

A **retrieve-only** job scores the retriever with two metrics:

- **Context relevance**: do the retrieved passages address the query?
- **Context coverage**: how much of what should have been retrieved actually was? This metric requires ground-truth passages.

A **retrieve-and-generate** job scores the whole pipeline. It measures **correctness**, **completeness**, **helpfulness**, **logical coherence**, **harmfulness**, **stereotyping** and **refusal**. It also checks the link between evidence and the generated answer:

- **Faithfulness**: is the answer supported by the retrieved context?
- **Citation precision**: were the cited passages actually used?
- **Citation coverage**: is what the answer says backed by citations?

This is the managed way to compare **knowledge bases**, **chunking strategies**, **embedding models** and **generator models** on the same questions.

For models you host on **SageMaker**, **SageMaker Clarify's foundation model evaluations** (the open-source `fmeval` library) compute similar accuracy, **robustness**, **toxicity** and **stereotyping** metrics; **Clarify** is closed to new customers since July 2026, so **Bedrock Evaluations** with **bring-your-own responses** is the current route for non-**Bedrock** models.

## Comparing configurations systematically

An FM application has more knobs than a classical model: the model, the prompt template, the **inference parameters**, the retrieval settings, the guardrail. **Systematic model evaluation** means changing them under control and measuring each candidate on the same dataset with the same metrics.

**Offline comparison.** Run **Bedrock Evaluations** for every candidate, including different FMs, prompt variants and **parameter profiles**. Read the managed reports side by side. Compare quality scores per metric, latency and token usage, from which cost per response follows.

Then compute two ratios:

- **Cost-performance ratio**: quality per dollar, or tokens per acceptable answer.
- **Latency-to-quality ratio**: how much latency each increment of quality costs.

Choose the configuration that clears the quality bar at the best ratio. For a route-planning assistant with wide quality variation across models and prompts, this replaces custom experimentation infrastructure.

**Online comparison.** Offline scores do not capture real users, so test promising candidates in production on a share of traffic. On **SageMaker**, one endpoint can host several **production variants**:

1. Assign each variant an **initial variant weight**.
2. Send a small percentage of live traffic to the new model, such as a fraud model, behind the same endpoint and API contract. No client change is needed.
3. Compare its latency and precision with the incumbent's.
4. Adjust the weights with `UpdateEndpointWeightsAndCapacities`, gradually shifting traffic to 100 percent for the winner.

**Shadow variants** receive a copy of the traffic without serving responses, for risk-free comparison.

**Multi-variant endpoints** are the least-overhead answer over **EC2** fleets behind a load balancer or **API Gateway** weighted routing across endpoints. **CodeDeploy blue/green** alternates whole versions rather than splitting traffic by weight, so it is also a distractor here.

For **Bedrock** applications, **A/B tests** run through **AWS AppConfig feature flags** or **weighted Lambda aliases**, with variant tags on the metrics.

**A/B versus canary.** An **A/B test** routes traffic in parallel to two or more variants and compares them statistically on user interactions. Measures include engagement, conversion, satisfaction and judge scores. This is the right design when the goal is to *choose among several* candidates.

A **canary** exposes one new version to a small share of users, watches quality and error metrics, then ramps up or rolls back. This is the right design when the goal is to *release one* version safely. **Linear rollouts** add traffic at fixed intervals, while **blue/green** switches entire fleets.

Watch the wording: "compare multiple variants simultaneously on real user interactions and pick the best" means **A/B**; "roll out safely with gradual exposure" means **canary**.

**Business outcomes** close the loop: whichever configuration wins offline and online must also move the metric the business cares about (**task completion**, conversions, handle time), tracked in **CloudWatch** beside the quality metrics.

## Evaluating RAG and retrieval

A **RAG** answer can fail in the retriever or in the generator, so evaluate them separately before evaluating the whole.

**Retrieval quality testing** needs a **labelled evaluation dataset**: questions paired with the passages or document ids that should be retrieved. Run each question through the retriever and score the results with standard ranking metrics:

- **Precision@k**: the share of the **top-k** results that are relevant.
- **Recall@k**: the share of relevant passages that appear in the **top-k**.
- **Mean reciprocal rank**: how high the first relevant hit sits.
- **nDCG**: rank-weighted **relevance**.

**Context matching verification** checks that a retrieved passage contains the information needed for the answer, not merely similar words. A judge prompt or the **RAG evaluation** job's **context relevance** metric does this at scale.

Track the scores over time as **custom CloudWatch metrics** or through **Bedrock RAG evaluation jobs**. Then a **chunking** change, a new **embedding model** or a corpus refresh shows up as a moving line. Pair those quality scores with **retrieval latency**, index scan time and query throughput from the vector database's metrics. Set **CloudWatch thresholds** to alarm on degradation.

Query-expansion heuristics judged by output **fluency**, **CloudTrail** call volumes, and weekly manual review of exported chunks are the distractors.

**Comprehensive assessment** of the generated side combines three perspectives:

- **RAG evaluation** compares outputs with the retrieved ground-truth context. Use **Bedrock Evaluations retrieve-and-generate metrics**, including **custom metrics** for **relevance**, grounding and factual alignment.
- **LLM-as-a-judge** scores clarity, **reasoning quality** and citation strength in the **CI/CD evaluation stage**.
- **Human feedback interfaces** let clinicians, analysts or writers give structured feedback, as covered in unit 02.

Token counts, latency and throughput in **CloudWatch** are operational signals, not quality measures. Unstructured feedback buried in logs and a manager's subjective spot-check are not evaluation systems.

## Evaluating agents

An agent is judged on outcomes and on the path it took. The **agent performance framework** the exam expects measures:

- **Task completion rate**: did the multi-step task finish correctly?
- **Tool usage effectiveness**: was the right tool selected at each step, with correct parameters and without unnecessary calls?
- **Reasoning quality**: are the intermediate decisions sound and consistent across the steps?
- **Efficiency**: how many steps, how much latency and how many tokens did the task require?

Apply safety dimensions on top of these measures.

**Amazon Bedrock AgentCore Evaluations**, generally available in 2026, is the managed service for this. It scores agent **traces** with several kinds of evaluator.

**Built-in evaluators** use **LLM-as-a-judge** with fixed prompts and models. They cover:

- **Response quality**: **helpfulness**, **correctness**, **faithfulness**, **relevance** and coherence.
- **Safety**: **harmfulness**, **stereotyping** and **refusal**.
- **Task completion**: goal success.
- **Tool usage**: **tool selection** and parameter accuracy.

**Third-party evaluators** come from the **DeepEval** and **AutoEval** libraries. **Custom evaluators** can use your own judge prompt and scoring schema, or a **code-based Lambda function**. The function performs deterministic checks, such as checking an expected tool sequence.

Choose when to evaluate:

- **On-demand evaluations** run against a test set for regression testing in **CI/CD**, before an agent configuration is promoted.
- **Online evaluations** sample live production traces at a rate you configure and score them continuously.

**Ground truth** can include reference answers, behavioral assertions for session-level goals and expected tool execution sequences.

For **Bedrock Agents (Classic)**, the **trace** from `InvokeAgent` supplies the reasoning, tool selections and observations these evaluators read. Domain 2 unit 01 and Domain 3 unit 05 cover that trace. The console's test window lets you step through it by hand.

When new tools cause inconsistent reasoning paths and tool mis-selection, the structured answer is **Amazon Bedrock Agent evaluations** that run automated task-completion tests, evaluate tool-use accuracy and analyse **reasoning quality** across versions before deployment; indexing outputs in **Kendra**, reading tool call logs by hand, or comparing configuration metadata in **SageMaker Experiments** (the feature that tracks training runs and their parameters) do not measure agent behaviour.

## Worked scenario

An insurer's claims-summary assistant is about to be rebuilt on a newer model with a new prompt and a **knowledge base** of policy documents. Adjusters complained that the old version was sometimes wrong, sometimes incomplete and inconsistent between similar claims; the team must choose the new configuration on evidence.

Define the dimensions first: **correctness** against the claim file, **completeness** of required fields, **faithfulness** to the retrieved policy text, **consistency** across rephrasings, **fluency**, and the safety dimensions. Build a **golden dataset** of three hundred claims with adjuster-approved summaries and a grouped set in which each question appears in five lightly reworded forms.

Then run the jobs. An automatic **Bedrock** evaluation on the summarisation task gives **BERTScore** accuracy, **semantic robustness** (how much summaries change under perturbed prompts) and **toxicity** for each of three candidate models. An **LLM-as-a-judge** job scores **correctness**, **completeness**, **faithfulness**, **helpfulness** and professional tone with **built-in metrics** and a **custom rubric** for the insurer's mandatory compliance statement, with explanations that show which claims lose points and why. A **RAG evaluation** job in **retrieve-only** mode checks **context relevance** and coverage of the policy retrieval, and in **retrieve-and-generate** mode adds **faithfulness** and **citation precision**, comparing two **chunking strategies**. A **human evaluation** job with the adjusters as the work team rates a hundred summaries and calibrates the judge.

Compare systematically. The reports are read side by side with token usage and latency, giving quality per dollar and latency per quality point; the mid-size model with the new prompt and **hierarchical chunking** wins. The **reranker** hosted on **SageMaker** gets its new version as a **production variant** with a small weight, an **A/B test** compares precision and latency on live traffic, and the weight shifts to full when it holds. Retrieval is tested separately with a labelled query set (precision at five, recall at ten, **mean reciprocal rank**) and latency thresholds in **CloudWatch**. The claims agent that gathers documents is evaluated with **AgentCore Evaluations** on **task completion**, **tool selection accuracy** and **reasoning quality** before its new configuration is promoted. Every question the exam asks about this scenario names one of these jobs or comparisons.

## Exam lens

- "**Relevance**, **factual accuracy**, **consistency** across regenerations, **fluency**, minimal manual scoring" → **golden reference datasets**, **relevance** scoring, factual-accuracy judge prompts, **multi-pass output diffing**.
- "Compare FMs and prompt variants, **cost-performance** and **latency-to-quality**, no custom experimentation infrastructure" → **Amazon Bedrock Evaluations** reports.
- "Response stability across lightly reworded prompts, fully managed" → a **Bedrock** evaluation job with **robustness metrics**.
- "Score outputs at scale for policy compliance, safety, multilingual accuracy, **consistency**" → **LLM-as-a-judge** in **Bedrock Evaluations** (**custom metrics**).
- "Factual grounding, **relevance** of retrieved evidence, clarity of reasoning, judge scoring, human feedback" → **RAG evaluation** with **Bedrock Evaluations** **custom metrics** plus **LLM-as-a-judge** in CI/CD.
- "Evaluate retrieval **relevance**, context alignment and latency, repeatable, minimal infrastructure" → labelled dataset **relevance** tests tracked in **Bedrock Evaluations** or custom **CloudWatch** metrics, plus vector database performance metrics with **CloudWatch** thresholds.
- "Test a new model on live traffic, same API contract, gradual shift, minimal overhead" → an additional **SageMaker** **production variant** with a small initial weight; "route traffic across model variants and shift 100 percent to the winner" → **multi-variant endpoints**.
- "Compare multiple variants simultaneously on real interactions and choose" → **A/B testing**; "safe gradual release of one version" → **canary**.
- "**Task completion**, **tool selection accuracy**, **reasoning quality** across agent versions before deployment" → **Amazon Bedrock Agent evaluations** (**AgentCore Evaluations**).

## Knowledge check

<!-- KC: E1-Q19, E1-Q8, E3-Q69, E3-Q54, E2-Q8, E3-Q15, E1-Q34, E1-Q22, E3-Q70 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 19

A global policy research institute builds a generative AI assistant on Amazon Bedrock to help analysts produce summaries, policy briefs, and comparative country insights. After internal testing, reviewers report that some responses contain factual inconsistencies, uneven fluency, and contradictory interpretations across similar queries. Leadership requests a formal evaluation framework that can measure relevance, factual accuracy, consistency across regenerations, and linguistic fluency, while minimizing manual scoring and leveraging repeatable assessment workflows.

Which solution will BEST meet these requirements?

- **A)** Export all FM outputs to an S3 bucket and build a custom QuickSight dashboard that visualizes writing style, response length, and topic frequency trends for periodic evaluation.
- **B)** Use CloudTrail event logs to track summary generation API activity and configure an EventBridge workflow that flags unusually long responses as potential accuracy risks, forwarding summaries to reviewers for validation.
- **C)** Implement an automated FM evaluation framework using golden reference datasets with expected outputs, relevance scoring functions, factual-accuracy benchmarking prompts, and consistency checks performed through multi-pass output diffing to detect reasoning divergence across regenerations.
- **D)** Require analysts to manually review a rotating sample of responses each day, document inconsistencies in a shared report, and escalate problematic outputs to the ML engineering team for follow-up investigation.

<details><summary>Answer</summary>

**Answer: C.** An automated evaluation framework built on golden reference datasets with expected outputs, relevance scoring functions, factual-accuracy benchmarking prompts for a judge model, and consistency checks through multi-pass output diffing measures relevance, factual accuracy, consistency across regenerations and fluency repeatably with almost no manual scoring. A QuickSight dashboard of writing style and length trends measures nothing about correctness, CloudTrail-driven alerts on long responses are not an accuracy signal, and daily manual review is the manual scoring the institute wants to minimise.

*Where this is covered: Unit 01, Why GenAI evaluation is different. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 1, question 8

A global logistics company is developing a GenAI route-planning assistant on Amazon Bedrock to help analysts generate optimized delivery summaries for large fleets. Early testing shows significant variation in output quality across different foundation models and prompt templates. Leadership requests a systematic evaluation approach that can compare multiple FM configurations, measure cost-performance tradeoffs, track latency-to-quality ratios, and identify the optimal model and prompt combination without building custom experimentation infrastructure.

Which solution will BEST meet these requirements?

- **A)** Enable CloudTrail API activity logging for all FM interactions, create EventBridge rules to detect latency spikes, and have a developer periodically review samples of model outputs to estimate overall performance trends.
- **B)** Run Amazon Bedrock Model Evaluations to compare multiple FMs and prompt variants, analyze quality metrics and latency-to-cost ratios through the managed evaluation reports, and use the results to select the optimal configuration based on empirical performance scores and token efficiency.
- **C)** Deploy three different Bedrock FMs into production simultaneously, collect user satisfaction survey results for each, and manually calculate quality differences and cost impacts using weekly usage data exports from the billing dashboard.
- **D)** Stream all prompt and response data to Amazon Kinesis Data Streams, create a custom A/B testing engine on AWS Lambda, and generate periodic evaluation summaries using Athena queries and scheduled QuickSight dashboards.

<details><summary>Answer</summary>

**Answer: B.** Amazon Bedrock Model Evaluations runs the candidate FMs and prompt variants against the same dataset and produces managed reports with quality metrics, latency and token usage, from which cost-performance and latency-to-quality ratios follow, so the team picks the best model and prompt combination without building experimentation infrastructure. CloudTrail with EventBridge and periodic sampling does not measure quality, three models in production with surveys and billing exports is slow and manual, and a Kinesis-Lambda-Athena A/B engine is exactly the custom infrastructure the requirement excludes.

*Where this is covered: Unit 01, Amazon Bedrock Evaluations. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 3, question 69

A fintech startup is developing a generative AI advisor that assists customers with investment planning. During controlled testing, the engineering team observes that the FM produces noticeably different recommendations when prompts are rephrased with small wording adjustments. To diagnose the issue, the team prepares a grouped evaluation dataset where each investment question includes multiple lightly reworded prompt variants. The team wants a fully managed method to measure the FM’s response stability and identify statistical differences across prompt clusters, without building custom evaluation pipelines.

Which solution will provide the required quantitative robustness analysis?

- **A)** Launch an Amazon Bedrock model evaluation job using the grouped prompt dataset and enable robustness metrics to assess statistical variation across closely related prompts.
- **B)** Use Bedrock batch inference to generate responses for each prompt variant and compute cosine similarity scores in Amazon Athena to identify output differences.
- **C)** Create a Step Functions pipeline that repeatedly invokes the FM with random paraphrasing injected into the system prompts, then perform manual analysis of the response patterns.
- **D)** Run a SageMaker Processing job that invokes the FM with all prompt variants and applies a custom semantic-drift scoring algorithm to measure divergence.

<details><summary>Answer</summary>

**Answer: A.** A Bedrock model evaluation job over the grouped prompt dataset with robustness metrics enabled measures semantic robustness, how much the responses change across closely related prompt variants, as a managed quantitative analysis. Batch inference plus cosine similarity in Athena, a Step Functions paraphrasing loop with manual analysis, and a SageMaker Processing job with a custom drift score are all custom evaluation pipelines the team wants to avoid.

*Where this is covered: Unit 01, Amazon Bedrock Evaluations. Key: ours, confidence high.*

</details>

### 4. Exam 3, question 54

A global e-commerce marketplace is developing an AI moderation pipeline to validate product listings before publication. The system generates refined product descriptions, policy-aligned safety disclaimers, and multilingual variants using several foundation models hosted on Amazon Bedrock. Amazon Rekognition classifies product images for restricted categories, and Amazon Translate generates multilingual baseline references to verify cross-language consistency.

To comply with international marketplace rules and safety standards, the compliance team must evaluate multiple models at scale. The evaluation must analyze outputs for harmful content, regulatory violations, accuracy of multilingual generations, and overall policy alignment. Manual review and regex-based filters are insufficient due to volume and linguistic diversity. The solution must automate evaluation with minimal operational overhead.

Which solution will best meet these requirements?

- **A)** Use AWS Lambda with keyword lists and regex filters to count unsafe terms, then compare violation counts across candidate models.
- **B)** Index generated descriptions in Amazon OpenSearch and compare vector similarity scores to identify which model produces more consistent outputs.
- **C)** Use LLM-as-a-judge within Amazon Bedrock Model Evaluation to automatically score generated descriptions for policy compliance, contextual safety, multilingual accuracy, and consistency.
- **D)** Perform RAG evaluation using Amazon Bedrock Knowledge Bases to validate retrieval and content grounding across product categories.

<details><summary>Answer</summary>

**Answer: C.** LLM-as-a-judge in Amazon Bedrock Model Evaluation scores each model's generated descriptions at scale against built-in and custom metrics for policy compliance, contextual safety, multilingual accuracy and consistency, with explanations, which handles the volume and linguistic diversity that manual review and regex cannot. Keyword and regex counts in Lambda miss meaning and languages, vector similarity in OpenSearch measures consistency but not safety or compliance, and RAG evaluation of knowledge bases assesses retrieval grounding rather than generated listing quality.

*Where this is covered: Unit 01, Amazon Bedrock Evaluations. Key: ours, confidence high.*

</details>

### 5. Exam 2, question 8

A cryptocurrency risk-monitoring startup uses Amazon Comprehend to extract merchant behavior signals from blockchain-linked descriptions and Amazon SageMaker AI to train a real-time fraud scoring model. The current SageMaker AI endpoint processes thousands of transactions per second, and clients integrate with it using a fixed API contract.

The data science team has produced an upgraded fraud detection model and needs to evaluate its real-world precision and latency. The firm must test the new model under live production load without changing client integrations or reducing throughput of the active model. The testing approach must require minimal operational overhead and allow gradual traffic shifting to measure performance differences.

Which solution will meet these requirements?

- **A)** Create a second SageMaker AI endpoint for the new model and configure Amazon CloudWatch dashboards to compare prediction latency and accuracy side-by-side.
- **B)** Deploy an Amazon API Gateway endpoint that implements a weighted traffic policy to forward some requests to the new SageMaker model.
- **C)** Modify the existing SageMaker AI endpoint configuration to add the new model as an additional ProductionVariant and assign it a small InitialVariantWeight so only a small percentage of live traffic is routed to it.
- **D)** Register the new model in SageMaker Model Registry and configure a Lambda function to automatically swap the live endpoint configuration after the next scheduled evaluation window.

<details><summary>Answer</summary>

**Answer: C.** Adding the upgraded model to the existing SageMaker endpoint as an additional production variant with a small initial variant weight routes a small share of live traffic to it behind the same endpoint and API contract, so precision and latency can be compared under real load and the weight shifted gradually with no client change and no extra infrastructure. A second endpoint with dashboards forces client or routing changes, API Gateway weighted forwarding adds a routing hop and a second endpoint to maintain, and a Lambda that swaps the endpoint configuration after a window is a cutover rather than gradual testing.

*Where this is covered: Unit 01, Comparing configurations systematically. Key: ours, confidence high.*

</details>

### 6. Exam 3, question 15

A global e-commerce platform is expanding its generative AI system that produces personalized shopping guidance, tailored marketing messages, and contextual order summaries. The system combines structured transaction data, customer behavior signals, and unstructured feedback from chat transcripts to generate real-time experiences. Multiple foundation model (FM) variants have been trained in Amazon SageMaker AI with different prompt strategies and tuning datasets, and the company wants to identify which model delivers the highest relevance, lowest bias, and greatest conversion impact.

The analytics pipeline uses Amazon Comprehend to classify customer intent, extract entities from feedback, and compute sentiment trends across responses. The evaluation team must compare multiple FM variants simultaneously, analyze performance differences using real user interactions, and choose the most effective model—all without disrupting the existing customer experience.

Which deployment strategy BEST supports these requirements?

- **A)** Release each new FM variant using a Canary deployment, exposing it to 1–5% of users at first. Increase traffic allocation only if Comprehend and SageMaker AI metrics match or exceed current benchmarks.
- **B)** Route production traffic in parallel to all candidate FM variants using an A/B testing framework, evaluate output quality using Comprehend’s sentiment and entity extraction metrics along with SageMaker AI engagement predictors, and select the top-performing model after statistical comparison.
- **C)** Use a Linear deployment to gradually shift 10% more traffic to each FM variant at fixed intervals while monitoring output quality, sentiment patterns, and engagement signals.
- **D)** Deploy all new FM variants using a Blue/Green strategy, run them sequentially in a staging environment, then promote the stable version to full production once Comprehend and SageMaker AI validation passes.

<details><summary>Answer</summary>

**Answer: B.** The requirement is to compare several FM variants simultaneously on real user interactions and choose the best, which is an A/B testing framework: production traffic is split in parallel across the candidates, outputs are scored with Comprehend sentiment and entity signals plus SageMaker engagement predictors, and the winner is selected after statistical comparison, without removing the current experience for anyone. A canary exposes one version at a time to a small slice for safe release rather than comparing many, a linear rollout likewise promotes one version, and blue/green runs variants sequentially in staging, so none compares all variants at once on live interactions.

*Where this is covered: Unit 01, Comparing configurations systematically. Key: ours, confidence medium.*

</details>

### 7. Exam 1, question 34

A legal-tech startup builds a contract-analysis assistant using a retrieval-augmented generation (RAG) workflow on Amazon Bedrock. After onboarding several large document sets, attorneys report that the assistant sometimes retrieves irrelevant clauses or misses context needed for proper interpretation. The engineering team must implement a retrieval quality testing framework that evaluates relevance, verifies context alignment, and measures retrieval latency. The solution must require minimal custom infrastructure, support repeatable testing, and help optimize vector store performance.

Which combination of steps will BEST meet these requirements? (Select TWO.)

- **A)** Measure retrieval latency, index scan time, and query throughput using vector database performance metrics, and establish automated thresholds in CloudWatch to detect degradation and trigger alerts for optimization.
- **B)** Implement a custom Lambda function that injects additional query expansion heuristics before each retrieval call and treats improved output fluency as an indicator of retrieval quality.
- **C)** Run retrieval relevance tests by comparing retrieved passages against a labeled evaluation dataset, and track relevance and context-matching scores using Amazon Bedrock Model Evaluations or custom CloudWatch metrics to validate retrieval quality over time.
- **D)** Use CloudTrail data events to review when retrieval APIs were called and infer retrieval quality based on the volume of requests and access frequency patterns.
- **E)** Export all retrieved chunks to Amazon S3 and have legal teams manually review them weekly to identify mismatches and tag problematic documents for retraining.

<details><summary>Answer</summary>

**Answer: A, C.** Retrieval relevance tests that compare retrieved passages against a labelled evaluation dataset, with relevance and context-matching scores tracked in Bedrock Model Evaluations or custom CloudWatch metrics, validate retrieval quality repeatably, and vector database performance metrics for retrieval latency, index scan time and throughput with CloudWatch thresholds detect degradation and drive optimisation. Query-expansion heuristics judged by output fluency measure the wrong thing, CloudTrail call volumes say nothing about relevance, and weekly manual review of exported chunks is neither repeatable nor low-overhead.

*Where this is covered: Unit 01, Evaluating RAG and retrieval. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 8. Exam 1, question 22

A health-tech company builds a clinical-workflow assistant using an Amazon Bedrock FM to summarize patient notes and retrieve relevant medical guidelines. After deployment, physicians report inconsistent explanation quality and occasional weak citations. Leadership requests a comprehensive evaluation system that can assess outputs from multiple perspectives, including factual grounding, relevance of retrieved evidence, and clarity of reasoning. The system must use managed AWS services where possible, support LLM-as-a-Judge scoring, and allow human reviewers to provide structured feedback for continuous improvement.

Which combination of steps will BEST meet these requirements? (Select TWO.)

- **A)** Implement an LLM-as-a-Judge automated assessment method using a Bedrock model to rate clarity, reasoning quality, and citation strength, and integrate the scoring pipeline into the existing CI/CD evaluation process.
- **B)** Embed unstructured physician feedback inside application logs and periodically search logs with Athena queries to identify "common wording patterns" that may indicate quality drift.
- **C)** Implement RAG evaluation workflows by comparing FM outputs to retrieved ground-truth context, and use Amazon Bedrock Model Evaluations with custom metrics to score relevance, grounding, and factual alignment.
- **D)** Use CloudWatch Logs to monitor token counts, latency spikes, and model throughput, and treat those patterns as indicators of output quality for future model evaluations.
- **E)** Periodically export a random sample of generated summaries to S3 for manual review by the engineering manager, and approve releases whenever outputs appear subjectively acceptable.

<details><summary>Answer</summary>

**Answer: A, C.** An LLM-as-a-Judge assessment with a Bedrock model rating clarity, reasoning quality and citation strength, integrated into the CI/CD evaluation stage, and RAG evaluation workflows that compare outputs with the retrieved ground-truth context using Bedrock Model Evaluations with custom metrics for relevance, grounding and factual alignment, together assess the outputs from multiple perspectives with managed services and leave room for structured human feedback. Unstructured feedback mined from logs, CloudWatch token and latency patterns treated as quality, and a manager's subjective spot-check of S3 samples are not evaluation systems.

*Where this is covered: Unit 01, Evaluating RAG and retrieval. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 9. Exam 3, question 70

A logistics company is building an AI operations agent using Amazon Bedrock Agents. The agent performs tasks such as computing optimized shipment routes, summarizing delivery exceptions, and triggering warehouse automation tools through chained API calls. After introducing several new tools, the engineering team noticed inconsistent reasoning paths and frequent tool mis-selections that caused incomplete workflows and incorrect outputs. The company needs a structured evaluation strategy that can measure how effectively the agent completes multi-step tasks, verify that it selects the correct tools at each step, assess reasoning quality across different agent versions, and automatically identify weak points before the updated agent configuration is deployed to production.

Which solution best meets these requirements?

- **A)** Use Amazon Kendra to index historical agent outputs and compare them with new agent responses to detect reasoning inconsistencies.
- **B)** Use CloudWatch Logs to monitor API calls for each tool and manually review whether the agent chose the correct tool based on call patterns.
- **C)** Use Amazon Bedrock Agent Evaluations to run automated task-completion tests, evaluate tool-use accuracy, and analyze reasoning quality across multi-step workflows before deployment.
- **D)** Use SageMaker Experiments to track agent configuration metadata and compare different versions to determine which configuration performs best.

<details><summary>Answer</summary>

**Answer: C.** Amazon Bedrock Agent evaluations run automated task-completion tests, score tool-use accuracy at each step and analyse reasoning quality across multi-step workflows, so weak points in a new agent configuration are found and compared across versions before deployment. Indexing historical outputs in Kendra compares text rather than behaviour, manual review of tool call logs in CloudWatch does not scale or measure reasoning, and SageMaker Experiments tracks configuration metadata rather than evaluating agent tasks.

*Where this is covered: Unit 01, Evaluating agents. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

Generated text is evaluated on dimensions (**relevance**, **factual accuracy**, **faithfulness**, **completeness**, **consistency**, **fluency**, **helpfulness**, tone, safety) with **reference-based metrics** against **golden datasets** and **reference-free** **LLM-as-a-judge** scores calibrated by humans.

**Amazon Bedrock Evaluations** provides automatic jobs (accuracy, **robustness**, **toxicity** by task type), **LLM-as-a-judge** jobs (eleven **built-in metrics** plus custom ones, scores 0 to 1 with explanations, **bring-your-own responses**), **human evaluation** jobs, and **RAG evaluation** jobs (**context relevance** and coverage; **correctness**, **faithfulness**, **citation precision** and coverage).

Compare configurations offline on **cost-performance** and **latency-to-quality** ratios, then online with **SageMaker** production and **shadow variants** or **feature flags**, using **A/B tests** to choose and canaries to release. Test retrieval separately with **labelled datasets** (precision and recall at k, **MRR**, **nDCG**, **context matching**) and latency metrics, and evaluate agents on **task completion**, **tool use** and **reasoning quality** with **AgentCore Evaluations** on their traces.
