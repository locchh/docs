# Unit 02: Quality assurance, feedback, reporting and deployment validation

**Task 5.1 (continued): user-centered evaluation, quality assurance processes, reporting systems and deployment validation.** Unit 01 built the measuring instruments. This unit puts them to work over the life of an application: collecting what users think, running evaluations continuously so regressions are caught before release, reporting results to people who do not read JSON, and validating a new model or prompt version before and during rollout.

The questions here share one shape: the company already has an FM application, quality has wobbled after a change, and leadership wants a *systematic*, *automated*, *managed* process. The distractors are always manual review, spreadsheets, weekly spot-checks, or infrastructure metrics standing in for quality.

## Learning from users

Automated metrics tell you what a judge model thinks; users tell you what actually helped. A **user-centered evaluation mechanism** has three parts.

**A feedback interface** belongs in the application itself. Give users several ways to describe a problem:

- A **rating** on each response. Thumbs up or down supports feedback at volume; a 1-to-5 scale adds nuance.
- **Categorical issue tags**, such as wrong fact, missing information, wrong tone or too long. These make feedback analyzable.
- **Inline annotations**, so a writer or clinician can mark the exact sentence that was wrong.

**Multi-dimensional feedback** with free-text comments beats a binary thumbs signal because it says *what* to fix. Implicit signals, such as session duration, follow-up rephrasings and API call counts, are weak proxies.

**A feedback pipeline** connects the interface to storage. The interface posts events through **Amazon API Gateway** to a **Lambda function**, which writes them to **Amazon DynamoDB**. **DynamoDB** is a **serverless** key-value database suited to high-volume event records keyed by response id.

Attach the response id, prompt version, model id and user context so feedback can be joined to the invocation record. High-volume streams can go through **Kinesis Data Streams**. **Amazon Comprehend** uses **sentiment analysis** and **key-phrase analysis** to turn free-text comments into trends.

**A loop back into evaluation** turns feedback into improvements:

1. Periodically analyze the dataset with **Athena** and **QuickSight**, or a **Lambda** summary.
2. Turn recurring failures into new **golden-dataset cases**.
3. Refine prompts and parameters.
4. Calibrate judge models against the human ratings.

Experts use **annotation workflows** in **SageMaker Ground Truth**, the managed labeling service. A private or vendor workforce scores or corrects outputs against a **rubric**. **Ground Truth**, like **Amazon A2I**, is closed to new customers, as explained in the domain README, but remains the exam's name for expert annotation.

For a content editor whose writers must rate, annotate and feed back, choose an in-UI feedback interface that writes to **DynamoDB** and is analyzed periodically. A daily **Glue** heuristic job, weekly manual inspection of **S3** exports, or **CloudTrail**-driven monthly summaries do not provide that feedback mechanism.

## Continuous evaluation and quality gates

A **systematic quality assurance process** treats every prompt, model or configuration change like a software release.

**Golden datasets and regression tests.** Maintain a curated set of prompts with expected outputs and, for **RAG**, the retrieved context. Cover important use cases, edge cases and past failures.

Run every candidate configuration against the dataset and compare its scores with the baseline. A drop in **accuracy**, **consistency**, **faithfulness** or **fluency** beyond a tolerance is a **regression**. Version-control the prompts and datasets so tests are reproducible.

**Continuous evaluation workflows.** **AWS Step Functions** orchestrates the evaluation:

1. Start an **Amazon Bedrock Evaluations** job against the **golden dataset**, using **LLM-as-a-judge** or **automatic evaluation**.
2. Wait for the job to finish.
3. Read the report from **S3**.
4. Compare each metric with its threshold.
5. Publish the results as **CloudWatch metrics**.

Schedule the workflow with **EventBridge** for nightly checks on the production configuration. Also trigger it from the pipeline for every change.

**Automated quality gates.** In **AWS CodePipeline**, the evaluation stage sits between build and deploy, with **CodeBuild** running the scripts. If **hallucination rate**, **accuracy**, **consistency** or **fluency** falls below the predefined baseline, the pipeline fails and the release is blocked. If it passes, a manual approval step or automatic promotion follows.

**Hallucination rate on a test set** is the canonical gate metric, because a factual error is the failure users forgive least. Alerts on unusual response lengths, **Glue** heuristic scores reviewed by a manager, and weekly spot-checks are not gates.

**Rollback and versioning.** Keep the previous prompt version in **Bedrock Prompt Management**, along with a deployable **guardrail version** and model configuration. Roll back automatically when production alarms fire after a release. Domain 3 unit 04 and Domain 4 unit 03 cover this pattern.

When new prompt templates and a model version produce inconsistent quality across deployments, use a **continuous evaluation workflow**. Run **Bedrock Evaluations** against the **golden dataset** on every deployment, with **regression thresholds** in the **CI/CD pipeline** and **automated quality gates** that block releases.

The same design fits a regulated firm that wants **regression tests** against golden reference outputs, validation of every FM version, blocking on thresholds and no human review. **A/B testing** on customer traffic, **A2I** human review and **CloudWatch** distribution alerts after the fact do not meet that requirement.

## Reporting to stakeholders

Evaluation produces numbers; stakeholders need pictures and trends. Build a **comprehensive reporting system** from managed pieces:

- **Bedrock Evaluations reports**, stored as JSON in **S3**, and **CloudWatch metrics** supply the data.
- **Amazon QuickSight**, the **serverless** business-intelligence service, reads the data through **Athena** or **S3 datasets**. Its **dashboards** compare model accuracy, latency trends, cost per output and quality scores across models and over time.
- **QuickSight scheduled reports** email weekly summaries to stakeholders.
- **Stakeholder-specific views** provide an executive summary in business terms and a drill-down for engineers.

**Model comparison visualisations** make release decisions legible through side-by-side scores per metric and trend lines per version. **Alert-based reports** notify people of significant changes between **scheduled reports**.

Manual weekly notebooks, custom **React** dashboards on **S3** and **CloudFront** with CSV emails, and **OpenSearch Dashboards** screenshots are the bespoke infrastructure the requirement excludes.

## Validating a deployment

Rolling out a new FM version is the moment quality regresses most often, so **deployment validation** runs before and during the rollout.

**Before rollout**, **synthetic user workflows** simulate real usage against the candidate version. Use **Lambda** or **Step Functions** to generate scripted conversations and multi-step journeys, or **CloudWatch Synthetics canaries** to replay representative prompts on a schedule.

An **AI-specific output validation pipeline** scores the results:

- **Hallucination rate** checks outputs against the **golden dataset**.
- **Semantic drift** compares embeddings of new answers and baseline answers to the same prompts. Alarm when similarity falls.
- **Structural drift** checks whether the model still formats recommendations the same way.
- **Response consistency** repeats prompts and diffs the outputs.

**Quality gates** block the rollout when metrics deviate from the baseline. Token-usage **anomaly detection** alone, **Ground Truth** review after each deployment, and developers voting in a spreadsheet do not validate quality before release.

**During rollout**, expose the new version gradually. For models hosted on **SageMaker**, choose among these patterns:

- **Shadow variants** receive a copy of production traffic without serving responses.
- **Production variants** with small weights run a **canary**: a few percent of traffic at first, ramping up as metrics hold.
- **Linear rollouts** add a fixed share of traffic at intervals.
- **Blue/green deployments** keep the old fleet ready to take traffic back.

**SageMaker deployment guardrails** and **CodeDeploy** automate traffic shifting with automatic rollback on **CloudWatch alarms**. For **Bedrock** applications, the same patterns run through **AWS AppConfig feature flags** and **Lambda aliases** with **weighted routing**.

To detect **semantic drift in real time** during a hosted-model rollout, use **SageMaker Model Monitor with custom quality metrics on a shadow deployment**. It scores the **shadow variant** outputs continuously and alerts before inconsistencies reach large volumes of traffic.

Offline comparison in **SageMaker Experiments**, **MLflow** metadata tracking and synthetic tests alone do not watch live traffic in that way. **MLflow** is the open-source experiment-tracking tool that **SageMaker** hosts as a managed service.

**After**: production monitoring (Domain 4 unit 03) keeps watching **hallucination** indicators, drift and user feedback, and the rollback path stays ready.

## The sequence the exam expects

The official practice set includes an ordering question about replacing a production model through a sequential, approved validation process. The official answer uses this order:

1. **Define the evaluation metrics**, such as **relevance**, **factual accuracy** and **fluency**.
2. **Create the test dataset**, covering diverse scenarios and edge cases.
3. **Conduct A/B testing** of the new model against the current one.
4. **Implement automated quality gates** with **Step Functions**.
5. **Analyze the results and produce the evaluation report**.

The official explanation is that each step needs the previous one. Metrics define what the dataset must cover; the dataset is what the **A/B test** runs on. The gates enforce the thresholds the test produced, and the report is written once everything has passed. You could argue that gates belong before the test; on the exam, reproduce the official order.

## Worked scenario

The same insurer's assistant now goes to production, and the team must keep it good through every change. Adjusters need a way to say what is wrong, releases must not regress, leadership wants a weekly view, and the next model version must be validated before and during rollout.

Feedback starts in the interface. Each summary shows a rating control, issue tags (wrong figure, missing field, wrong tone) and inline annotation; the events flow through **API Gateway** and a **Lambda function** into **DynamoDB** keyed by response identifier with the prompt version attached. Recurring failures become new golden-dataset cases, senior adjusters annotate a monthly sample in a **Ground Truth** workflow, and the judge model is recalibrated against their ratings.

Quality assurance becomes a pipeline. A **Step Functions** workflow runs the golden-dataset evaluation nightly and on every change, publishing scores to **CloudWatch**; in **CodePipeline**, the evaluation stage blocks a release when **hallucination rate**, **completeness** or **consistency** falls below the baseline, and a manual approval follows a pass. Prompt versions in **Prompt Management** and the evaluation datasets are version-controlled, and the previous configuration stays deployable for rollback.

Reporting is managed: evaluation reports in **S3** and **CloudWatch** metrics feed a **QuickSight** dashboard that compares model versions on accuracy, latency, cost per summary and judge scores over time, with a scheduled weekly summary emailed to leadership.

Deployment validation runs in two phases. Before rollout, synthetic adjuster workflows exercise the new version, and an **AI-specific validation** pipeline compares **hallucination rate**, **semantic drift** (embedding similarity to baseline answers) and repeat-run **consistency** against thresholds that block the rollout. During rollout, the **SageMaker**-hosted components go out as shadow and then **canary** variants with **Model Monitor** custom quality metrics alerting on drift, the **Bedrock** configuration moves behind an **AppConfig** flag from five percent to full traffic, and **CloudWatch alarms** trigger automatic rollback. The order the team followed, and the one the exam asks for, is define metrics, build the dataset, **A/B test**, gate with **Step Functions**, then analyse and report.

## Exam lens

- "Writers rate outputs, annotate issues, feed structured feedback back, minimal infrastructure" → in-app feedback interface storing events in **DynamoDB**, analysed periodically to refine prompts.
- "Detailed, actionable user feedback" → multi-dimensional ratings with free-text comments; "expert annotation" → **SageMaker Ground Truth** workflows.
- "Detect regressions, prevent low-quality configurations from reaching production, managed, automated" → **Bedrock Evaluations** on a **golden dataset** in the CI/CD pipeline with **regression thresholds** and **quality gates**.
- "Critical **quality gate** metric" → **hallucination rate** on a test set.
- "**Regression tests** against golden outputs for every FM version, block deployment, no human review" → **automated quality gates** with a **Bedrock**-based evaluation workflow in CI/CD.
- "Recurring visual reports comparing models, weekly summaries, no custom pipelines" → **Bedrock** evaluation reports plus **CloudWatch** metrics into **QuickSight** dashboards with **scheduled reports**.
- "Validate a new FM version before rollout: simulate users, **hallucination** and **consistency** metrics, block on drift" → **synthetic user workflows** with an **AI-specific validation** pipeline and **quality gates**.
- "Detect **semantic drift** in real time during rollout, alert before large traffic is affected" → **SageMaker Model Monitor** **custom metrics** on a **shadow deployment**.
- "Order the steps" → metrics, dataset, **A/B test**, **quality gates**, report.

## Knowledge check

<!-- KC: E1-Q41, E1-Q67, E2-Q41, E2-Q1, E3-Q26, PQ-Q17 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 41

A publishing startup uses an Amazon Bedrock–powered content editor to help writers generate article summaries and headlines. After launch, the product team receives inconsistent reports about summary clarity and factual correctness. Leadership requests a user-centered evaluation mechanism that allows writers to rate outputs, annotate issues, and feed structured feedback back into the evaluation pipeline. The mechanism must integrate cleanly with the existing application, require minimal custom infrastructure, and support continuous improvement of FM performance over time.

Which solution will BEST meet these requirements?

- **A)** Embed a feedback interface directly into the editor UI that captures user ratings, categorical issue tags, and inline annotations, store the feedback events in Amazon DynamoDB, and periodically analyze the feedback dataset to refine prompts and model configurations for continuous FM quality improvement.
- **B)** Create a batch job in AWS Glue that processes all model inputs and outputs daily, generates quality estimates using heuristic scoring rules, and updates a metrics dashboard in Amazon QuickSight for periodic tuning cycles.
- **C)** Export all editor interactions to Amazon S3, manually inspect random samples each week, and adjust FM configuration parameters based on observed quality gaps and common error themes identified by the product team.
- **D)** Use CloudTrail logging to track all FM invocation activity, generate monthly performance summaries through EventBridge and Lambda, and send the summaries to the engineering team for manual review and tuning.

<details><summary>Answer</summary>

**Answer: A.** A feedback interface embedded in the editor that captures ratings, categorical issue tags and inline annotations, stores the events in DynamoDB and is analysed periodically to refine prompts and configurations gives writers a direct, structured channel that integrates with the existing application with minimal infrastructure and drives continuous improvement. A daily Glue heuristic job and QuickSight dashboard measure without user input, weekly manual inspection of S3 exports is neither structured nor scalable, and CloudTrail invocation summaries contain no quality feedback.

*Where this is covered: Unit 02, Learning from users. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 1, question 67

A logistics software company uses an Amazon Bedrock FM to generate route summaries and exception reports for its dispatch system. After adding new prompt templates and switching to a newer model version, the team notices inconsistent quality across deployments. Leadership asks for a systematic quality assurance process that can automatically detect regressions, evaluate output consistency, and prevent low-quality model configurations from being promoted to production. The solution must use managed AWS services, require minimal custom infrastructure, and provide automated quality gating before deployments.

Which solution will BEST meet these requirements?

- **A)** Use CloudWatch Logs to track FM invocations, create a Lambda function that checks for unusual response lengths, and trigger SNS alerts when anomalies occur before deployment.
- **B)** Export FM outputs to Amazon S3 and use an AWS Glue job to compute heuristic quality scores, then have the engineering manager manually review a QuickSight dashboard before approving releases.
- **C)** Implement a continuous evaluation workflow using Amazon Bedrock Model Evaluations to test the FM against a golden dataset on every deployment, integrate regression thresholds into the CI/CD pipeline, and enforce automated quality gates that block releases when accuracy, consistency, or fluency metrics fall below predefined baselines.
- **D)** Run manual spot-checks on generated summaries each week, compare outputs with historical examples, and approve deployments only after the product team reviews a small sample set.

<details><summary>Answer</summary>

**Answer: C.** A continuous evaluation workflow that runs Amazon Bedrock Model Evaluations against a golden dataset on every deployment, with regression thresholds in the CI/CD pipeline and automated quality gates that block releases when accuracy, consistency or fluency fall below baselines, detects regressions and prevents low-quality configurations from being promoted using managed services. Lambda checks on response length are not quality measures, a Glue heuristic score reviewed by a manager is manual, and weekly spot-checks provide no automated gating.

*Where this is covered: Unit 02, Continuous evaluation and quality gates. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 2, question 41

A healthcare analytics company deploys multiple foundation models on Amazon Bedrock to generate clinical insights for internal medical review teams. Leadership wants recurring reports that clearly compare model accuracy, latency trends, cost-per-output, and quality scores from recent evaluations. Stakeholders require visual dashboards, automated weekly summaries, and the ability to compare model performance over time without building custom pipelines or maintaining bespoke reporting infrastructure. The engineering team must choose a solution that uses managed AWS services, scales automatically, and integrates seamlessly with existing Bedrock data sources.

Which solution will BEST meet these requirements?

- **A)** Enable Amazon Bedrock Model Evaluation reports, export evaluation metrics to Amazon CloudWatch, and build automated Amazon QuickSight dashboards that visualize model quality, latency trends, and cost metrics. Schedule weekly email summaries using QuickSight’s built-in reporting capabilities.
- **B)** Use SageMaker Studio to manually generate performance notebooks each week and upload visualizations to QuickSight dashboards for stakeholder access.
- **C)** Export Bedrock invocation logs to Amazon S3, create an Athena query layer, and build a custom React dashboard hosted on Amazon S3 with CloudFront. Run scheduled Lambda jobs to email raw CSV reports to stakeholders.
- **D)** Stream invocation logs to Amazon OpenSearch Service and configure custom index visualizations with Kibana. Schedule weekly exports of visualization screenshots to S3 for distribution.

<details><summary>Answer</summary>

**Answer: A.** Bedrock Model Evaluation reports supply the quality scores, CloudWatch holds latency and cost metrics, QuickSight builds the visual dashboards that compare model accuracy, latency trends, cost per output and quality over time, and QuickSight's scheduled reports email weekly summaries, all managed and scaling automatically. Manual weekly SageMaker notebooks, a custom React dashboard with Lambda-emailed CSVs, and OpenSearch visualisations exported as screenshots are the bespoke reporting infrastructure the team must avoid.

*Where this is covered: Unit 02, Reporting to stakeholders. Key: ours, confidence high.*

</details>

### 4. Exam 2, question 1

A global travel booking company uses Amazon Bedrock foundation models to generate itinerary summaries, hotel recommendations, and customer explanations. The engineering team is preparing to roll out a new FM version to production. Leadership requires strict deployment validation to ensure that the update does not increase hallucination rates, degrade semantic consistency, or introduce drift in how the model structures its recommendations. The validation process must run automatically before deployment, simulate real user behavior, detect output inconsistencies, and block the rollout if FM responses deviate from baseline quality metrics.

Which solution will BEST meet these requirements?

- **A)** Enable CloudWatch anomaly detection on token usage for the new FM version and set up alerts that notify the engineering team if usage patterns diverge from historical trends.
- **B)** Enable automated deployment validation using synthetic user workflows that run against the new FM version, evaluate hallucination and consistency metrics through an AI-specific output validation pipeline, and enforce quality gates that block rollout upon detecting semantic drift.
- **C)** Generate human review tasks through SageMaker Ground Truth after each deployment and require a review team to approve outputs before production rollout continues.
- **D)** Perform manual A/B testing with a subset of developers who compare model outputs in a shared spreadsheet and vote on whether the new FM version should be deployed.

<details><summary>Answer</summary>

**Answer: B.** Automated deployment validation with synthetic user workflows against the new FM version, an AI-specific output validation pipeline that scores hallucination and consistency metrics, and quality gates that block rollout when semantic drift from baseline is detected runs automatically before deployment and simulates real user behaviour, as required. Token-usage anomaly detection says nothing about hallucinations or structure, Ground Truth human review after each deployment is manual and too late, and developers voting in a spreadsheet is neither automated nor rigorous.

*Where this is covered: Unit 02, Validating a deployment. Key: ours, confidence high.*

</details>

### 5. Exam 3, question 26

A global logistics company operates a multilingual virtual-assistant platform that uses Amazon Lex and multiple foundation models (FMs) deployed through Amazon SageMaker AI. After a recent FM update, customers reported inconsistent troubleshooting guidance and mismatched responses across regions. The engineering team suspects semantic drift introduced during the model update.

They want a validation approach that:

- continuously monitors model outputs during rollout
- detects semantic shifts or degraded response quality in real time
- triggers alerts before inconsistencies affect large volumes of traffic
- integrates into their automated CI/CD process without disrupting live production

Which approach ensures reliable FM behavior and early detection of semantic drift during updates?

- **A)** Implement a synthetic workflow interaction generator in SageMaker AI to simulate user behavior during CI/CD and compare new outputs with golden datasets.
- **B)** Use SageMaker Model Monitor with custom quality metrics on a shadow deployment to detect real-time drift and generate immediate alerts during model rollout.
- **C)** Leverage SageMaker Experiments to compare output deviations across versions and promote updated models only when performance thresholds are met.
- **D)** Use AWS MLflow with SageMaker AI to track versioned model metadata and detect anomalies after each FM update.

<details><summary>Answer</summary>

**Answer: B.** SageMaker Model Monitor with custom quality metrics on a shadow deployment scores the new model's outputs on a copy of live traffic during rollout, detects semantic shifts or degraded quality in real time and raises alerts before inconsistencies affect large volumes of traffic, and it plugs into the CI/CD process without disturbing production. A synthetic workflow generator with golden datasets tests before release but does not watch live rollout traffic, SageMaker Experiments compares versions offline, and MLflow tracks metadata and detects anomalies only after the fact.

*Where this is covered: Unit 02, Validating a deployment. Key: ours, confidence high.*

</details>

### 6. Official practice question set, question 17

*Ordering question.*

A company is implementing a systematic evaluation process for a newly deployed FM in Amazon Bedrock. The company wants to replace an existing model in production with a new model. The change to the new model is dependent on the new model demonstrating better performance than the existing model. The company must follow a sequential validation process. To ensure evaluation rigor, each step must be reviewed and approved before proceeding to the next step.

Select and order each step from the following list to implement the evaluation workflow. Select each step one time.

Steps to order:

- Conduct A/B testing to compare the new model against the existing production model.
- Create a test dataset with diverse scenarios and edge cases.
- Define evaluation metrics for relevance, factual accuracy, and fluency.
- Implement automated quality gates by using AWS Step Functions.
- Analyze the results and generate a comprehensive evaluation report.

(#answer-17)

---


<details><summary>Answer</summary>

**Answer: Define metrics → create test dataset → A/B testing → quality gates → analyse and report.** The sequential validation order is: define the evaluation metrics for relevance, factual accuracy and fluency; create the test dataset with diverse scenarios and edge cases; conduct A/B testing of the new model against the production model; implement automated quality gates with Step Functions; and finally analyse the results and generate the comprehensive evaluation report. Each step depends on the approved output of the previous one: the metrics decide what the dataset must cover, the dataset is what the A/B test runs on, the gates enforce the thresholds the test defines, and the report is written once every stage has passed.

*Where this is covered: Unit 02, The sequence the exam expects. Key: AWS official answer.*

</details>

<!-- KC-END -->

## Summary

Collect user feedback in the application (ratings, issue tags, **annotations** through **API Gateway** into **DynamoDB**, expert annotation in **Ground Truth**) and feed it into prompts and **golden datasets**. Run **continuous evaluation** with **Step Functions** and **Bedrock Evaluations** against **golden datasets**, wire **regression thresholds** and **quality gates** (**hallucination rate** first) into **CodePipeline**, and keep versions ready to roll back. Report through **QuickSight** dashboards and scheduled summaries that compare models over time.

Validate releases with **synthetic user workflows** and AI-specific checks for **hallucination**, **semantic drift** and **consistency** before rollout, then shadow, **canary**, linear or **blue/green** exposure with **Model Monitor** on a **shadow deployment** during rollout. And remember the order: metrics, dataset, **A/B test**, gates, report.
