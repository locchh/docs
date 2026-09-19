# Unit 04: AI governance and compliance

**Task 3.3: Implement AI governance and compliance mechanisms.** This unit is about proving to an auditor how a model behaves, where its data came from, who approved it and what it decided. The mechanisms are:

- **Model cards** for documentation.
- The **Glue Data Catalog**, **lineage tracking** and **metadata tags** for provenance.
- **CloudWatch Logs** and **CloudTrail** for decision and audit logs.
- Organisation-wide controls that keep every team inside policy.
- Continuous monitoring that detects drift, bias and misuse, and remediates automatically.

Governance questions reward the answer that produces evidence *automatically*. Manual documentation in **S3**, nightly sampling, configuration snapshots and hand-written reports are the recurring distractors. Programmatic model cards, catalogued lineage, structured logs and event-driven remediation are the recurring answers.

## What a compliance framework has to prove

A regulator, an internal auditor or a customer's due-diligence team asks four questions about an AI system:

- **What is this model and what are its limits?** That is documentation.
- **What data trained it and what data does it read?** That is lineage and attribution.
- **What did it decide, when, for whom?** Those are decision logs.
- **Who is allowed to change it, and were the rules followed?** Those are organisational controls.

A compliance framework is the set of mechanisms that answers all four continuously, and this unit maps AWS services onto them.

The external frameworks you may see named:

- The **NIST AI Risk Management Framework**, a voluntary US framework for governing, mapping, measuring and managing AI risk.
- **ISO/IEC 42001**, the international standard for an AI management system. AWS holds the certification for services including **Amazon Bedrock**.
- The **EU AI Act**, which sets risk-tiered obligations for documentation, transparency and human oversight.
- Sector rules such as **HIPAA**, **GDPR**, SEC and FINRA.
- The **OWASP Top 10 for LLM Applications** for security, covered in unit 01.

**AWS Artifact** is where you download AWS's own compliance reports, such as SOC, ISO and PCI, to cover the AWS side of shared responsibility. Your side is everything below.

**AWS Audit Manager** deserves one paragraph because Skill Builder, AWS's training platform, leans on it. It collects evidence from your AWS accounts against prebuilt or custom control frameworks and assembles audit-ready reports. Its **AWS generative AI best practices framework v2** holds 110 controls across eight domains, which are accuracy, fair, privacy, resilience, responsible, safe, secure and sustainable, for **Bedrock** and **SageMaker** workloads. **Audit Manager** is no longer open to new customers, so treat it as exam vocabulary for "automated evidence collection against a GenAI best-practices framework" rather than a service to adopt.

## Documenting models: SageMaker Model Cards

**Amazon SageMaker Model Cards** is the AWS mechanism for model documentation, and "programmatic model cards" is the exam phrase for it. A model card records:

- The model's **intended uses**, and the uses it is not meant for.
- A **risk rating** of `unknown`, `low`, `medium` or `high`.
- Training details: datasets, algorithm, hyperparameters and environment.
- **Evaluation results** supplied as JSON. **SageMaker Clarify** bias and explainability reports and **Model Monitor** reports, both described later in this unit and in unit 05, import directly.
- Observations, and free-form **additional information** such as known limitations, ethical considerations and recommendations.

Cards move through an approval status of draft, pending review, approved or archived. Every edit other than a status change creates a new **immutable version**, so the audit trail of the documentation itself is preserved, and a card can be **exported to PDF** for regulators. The APIs `CreateModelCard`, `UpdateModelCard` and `ExportModelCard` let a CI/CD pipeline generate and refresh the card from training-job metadata and evaluation outputs, which is what "minimise manual documentation effort" means.

Model cards integrate with two other features. The **SageMaker Model Registry** catalogues model versions with an approval status, `PendingManualApproval`, `Approved` or `Rejected`, that deployment pipelines check before promoting a model. The **SageMaker Model Dashboard** is the single console view of every model in the account, with its risk rating, monitoring alerts and lineage.

Model cards were built for models you train, but they document foundation-model applications equally well: the FM used, the prompt templates, the evaluation results across scenarios and demographic groups, the guardrail configuration, and the limitations users are told about.

For AWS's own AI services, **AWS AI Service Cards** publish intended use cases, limitations, responsible-AI design choices and deployment best practices, the same idea at the service level. **Systems Manager** documents, meaning automation runbooks, **CloudWatch** dashboards and **Config** rules do not document models.

## Tracking data lineage and source attribution

**Lineage** is the record of where data came from and what happened to it. **Attribution** links a generated output back to the sources that produced it. Four AWS mechanisms carry them.

**AWS Glue Data Catalog** is the central metadata store: databases and tables that describe datasets in **S3** and elsewhere, with location, schema, partitions and properties. **Glue crawlers** populate it, inferring schema with built-in or custom classifiers on a schedule, or you define entries manually.

Registering the curated and the scraped input datasets in the catalog is how you make sources first-class, queryable objects that reviewers and downstream jobs can reference, and it is what **Athena**, **Redshift Spectrum**, **EMR**, **Lake Formation** and **SageMaker** read.

**Glue ETL jobs** carry provenance through transformations: **job bookmarks** track what was processed, and job parameters and the catalog record source-to-target mappings. **Amazon DataZone**, AWS's data governance catalog, and **SageMaker Unified Studio**, the combined data and AI development environment, capture **OpenLineage**-compatible lineage automatically from **Glue** and **Redshift**, including column-level lineage from **Glue Spark** jobs, and visualise the graph. **OpenLineage** is the open standard for lineage events.

**Amazon SageMaker ML Lineage Tracking** records the ML workflow itself as a graph of:

- **Artifacts**: datasets, images and models.
- **Actions**: training jobs, processing jobs and deployments.
- **Contexts**: experiments and endpoints.

Those are joined by **associations**. **SageMaker** creates the entities automatically for training jobs, models and endpoints, and you add your own with `CreateArtifact`, `CreateAction`, `CreateContext` and `AddAssociation`, including across accounts, for steps it cannot see.

Querying the graph tells an auditor exactly which dataset version, container and hyperparameters produced the model behind a given endpoint, and lets you reproduce it. Dataset versioning for the same purpose comes from **S3 Versioning**, which keeps every object version with lifecycle rules to expire old ones, or from **SageMaker Feature Store**, the managed repository of ML features, with its time-travel queries that return the features as they were at a point in time.

**Metadata tagging** attaches attribution to everything else. **Resource tags** on **S3** buckets, training jobs, models, endpoints, agents and knowledge bases, such as `DataSensitivity`, `ComplianceFramework`, `Owner` and `DataSource`, and **S3 object tags** on individual files, record origin, licence and jurisdiction. **Tag policies** and **service control policies** in **AWS Organizations** can require them.

The same idea applied to generated content is the exam's "tag FM outputs with metadata from the data source". Stamp each response with the source document identifiers, which the knowledge base returns as citations, plus the prompt version, the model identifier and a timestamp, so a reviewer can trace a generated question back to the document it was drawn from.

Together with registering the datasets in the **Data Catalog**, this gives source lineage with the least operational overhead. Correlating invocation logs with sources after the fact, logging reviewer clicks in **CloudTrail**, or explaining predictions with **SageMaker Clarify** do not establish where the content came from.

## Decision logs and audit trails

Lineage covers the model and its data. **Decision logs** cover what the model did in production.

**Amazon CloudWatch Logs** is the destination, and **structured logging** is the technique: one JSON object per decision, holding the request identifier, user or session context, prompt and prompt version, model identifier, retrieved source identifiers, confidence or grounding scores, guardrail outcome, the response or a reference to it, and a timestamp. That structure is what lets **CloudWatch Logs Insights** answer compliance questions by query, **metric filters** turn log patterns into metrics, and **retention settings** per log group match the regulatory period.

**Amazon Bedrock model invocation logging** provides the raw record with no code. Every `InvokeModel` and `Converse` call's request and response metadata, inputs and outputs are delivered to **CloudWatch Logs** and/or an **S3** bucket in the same account and Region, with bodies over 100 KB and any image or embedding data stored as separate **S3** objects.

**AWS CloudTrail** is the control-plane audit trail: who called which API, from where, with what identity.

- **Bedrock**'s inference APIs, `InvokeModel`, `InvokeModelWithResponseStream`, `Converse` and `ConverseStream`, are logged as **management events**.
- `InvokeAgent`, `Retrieve`, `RetrieveAndGenerate`, `InvokeFlow` and `RenderPrompt` are **data events** that you enable with advanced event selectors on the agent alias, knowledge base, flow alias or prompt resource types. **S3** object access is a data event too.

Deliver the trail to an **S3** bucket protected with **Object Lock**, query it with **Athena**, and build the compliance report in **Amazon QuickSight**.

The three sources answer different questions. **CloudTrail** tells you *that* a call happened and by whom, invocation logging tells you *what* was said, and **CloudWatch Logs** tells you *why* the application decided what it did. A complete audit needs all three, which is why "**CloudWatch Logs** to collect comprehensive decision logs" sits beside model cards and lineage in the keyed answers.

## Organisational governance systems

Governance at scale is about making the right thing the only thing teams can do.

**AWS Organizations** groups accounts and applies **service control policies (SCPs)** that cap permissions across whole organisational units. They can deny **Bedrock** actions outside approved Regions, deny model-customisation jobs without an approved tag, or deny `InvokeModel` on model ARNs that legal has not cleared. **AWS Control Tower** layers preventive and detective controls on a **landing zone**, a pre-built multi-account environment with baseline security settings.

Inside accounts, **IAM** policies with condition keys enforce the details. The pattern from unit 01, an **IAM** policy with the `bedrock:GuardrailIdentifier` condition on every role that calls the FM APIs, is the way to make an AI governance rule, "every interaction uses the approved guardrail", self-enforcing across teams. It needs no proxy service, no **Parameter Store** lookup and no new infrastructure.

Three more mechanisms watch the configuration. **Tag policies** standardise the governance tags, **AWS Config** rules detect drift from approved configurations, such as an endpoint without data capture or a notebook with internet access, and **AWS Security Hub** collects the findings.

Process controls are workflows.

**Approval gates** for promoting a model or a prompt from development to production run as **Step Functions** state machines. They check governance metrics such as evaluation scores, bias metrics and red-team results, wait for a human approver, record the decision in **DynamoDB**, and only then update the **Model Registry** status or the **Bedrock** prompt or agent alias. Deployment pipelines roll back on alarms, whether through **CodePipeline** and **CodeDeploy** or **SageMaker deployment guardrails**, the endpoint feature that shifts traffic blue/green or canary-style and rolls back on alarms, which is unrelated to **Bedrock Guardrails**.

**Role separation** keeps the people who build models, evaluate them, deploy them and monitor them in different roles with different permissions, through **IAM Identity Center** permission sets. The **SageMaker Model Dashboard** gives the governance team one view of every model's risk rating, monitor status and lineage, and the **SageMaker Model Registry** is the catalogue of approved versions.

Governance also decides **where** data and inference may happen. Data residency is enforced by four things: Region choice, **SCPs** that deny other Regions, **geographic cross-Region inference profiles** that keep **Bedrock** inference within a geography, and, when regulated data may not leave a country at all, **AWS Outposts**.

**Outposts** is AWS infrastructure installed in the customer's data centre and connected to a parent Region. It runs the preprocessing and redaction locally, so that only sanitised text or feature vectors travel to **Bedrock** in the nearest Region. Note the limits: **Bedrock** does not run on **Outposts**, **SageMaker** endpoints do not run in your data centre, and **AWS Wavelength**, which is compute inside 5G carrier networks for mobile latency, does not host **Bedrock** either. Any option that uploads the regulated documents to a central **S3** bucket first, however well encrypted, fails the residency requirement.

## Continuous monitoring and automated remediation

Compliance is not a launch gate; it is a running state. The task statement asks for detection of misuse, drift and policy violations, bias-drift monitoring, automated alerting and remediation, token-level redaction, response logging and output policy filters. Here are the AWS pieces.

**Amazon SageMaker Model Monitor** watches models deployed on **SageMaker** endpoints, and, on a schedule, batch transform jobs. **Model Monitor**, **Clarify** and **Ground Truth** are closed to new customers, as the domain README notes, but the mechanics below are what the exam tests.

The setup has three steps. You enable **data capture** on the endpoint, create a **baseline** from the training data that computes statistics and suggests **constraints**, then schedule monitoring jobs that compare live traffic with the baseline and report **violations** to **CloudWatch**, where alarms notify or trigger remediation.

It has four monitor types:

- **Data quality**: input feature drift, missing values and type changes.
- **Model quality**: accuracy, precision, recall, F1 or regression metrics, which needs ground-truth labels merged in later.
- **Bias drift**.
- **Feature attribution drift**.

The last two use **SageMaker Clarify**. **Bias drift** recomputes bias metrics such as **DPPL**, the difference in positive proportions in predicted labels, over each monitoring window, and alarms when a metric leaves the allowed range you set, for example when DPPL must stay within (-0.1, 0.1). Confidence intervals reduce false alarms. **Feature attribution drift** compares the **SHAP** feature-importance ranking of live predictions with the baseline, where SHAP values measure each feature's contribution to a prediction.

Bias drift monitoring is therefore the answer to "detect and alert on potential bias drift in model outputs over time". **Clarify**'s **pre-training** metrics, on the dataset, and **post-training** metrics, on predictions, published to **CloudWatch** per Region, are the low-code way to measure and monitor bias across patient or customer groups. Unit 05 covers the metrics themselves.

For FM applications on **Bedrock** the equivalents are:

- **CloudWatch** metrics and alarms on invocation volume, token counts, latency and error rates, with **anomaly detection** for unusual patterns that may indicate misuse or a runaway agent.
- Guardrail metrics on intervention rates by policy type.
- **Scheduled evaluation jobs**, whether **Bedrock Evaluations** or your own **LLM-as-a-judge** pipeline, that re-score a sample of production prompts for quality, bias and safety.
- **Amazon GuardDuty** and **Security Hub** for account-level threats.

**Remediation** is event-driven. A **CloudWatch** alarm or **Model Monitor** violation publishes to **Amazon EventBridge**, and a rule invokes a **Lambda** function or **Step Functions** workflow. That workflow shifts endpoint traffic back to the previous production variant or rolls back through **CodeDeploy** or **SageMaker deployment guardrails**, disables an agent alias or tightens a guardrail version, opens a ticket and notifies through **SNS**, and pauses for the human review that regulated decisions require.

Three terms from the task statement map onto pieces you have already seen:

- **Token-level redaction** means pre- and post-processing handlers around the model, using **Comprehend** PII detection or named-entity recognition, regular expressions, or guardrail sensitive-information filters, that remove identifiers from prompts and responses at the token level, so logs and outputs are compliant by construction.
- **Response logging** is the structured decision log above.
- **AI output policy filters** are **Bedrock Guardrails**, or a custom **Lambda** filter, that enforce content policy on every response.

Running compliance tests continuously, with adversarial prompts, policy test suites and evaluation datasets, against each new model or prompt version keeps the system audit-ready rather than audit-surprised.

## Worked scenario

A multinational bank runs foundation models in **Bedrock** and its own models on **SageMaker** across three Regions. Regulators ask for documentation of every model, lineage of the data it uses, a record of each decision it influenced, proof that only approved versions reach production, and evidence that the bank watches for bias and misuse.

Documentation is generated, not written by hand. The training and evaluation pipeline creates and updates a **SageMaker Model Card** for every model version, with its intended use, risk rating, training data references and the JSON evaluation results from **Clarify** and **Bedrock Evaluations**. It exports the card as PDF for the regulator, and links it to the **Model Registry** entry whose approval status the deployment pipeline checks. For the **Bedrock** applications the same card documents the FM, the prompt version, the guardrail version and the evaluation results.

Lineage and attribution use the data services.

- Every dataset is registered in the **Glue Data Catalog** by crawlers.
- **DataZone** captures lineage from the **Glue** jobs that transform it.
- **SageMaker Lineage Tracking** records which dataset version and container produced each model.
- **S3 Versioning** keeps the training snapshots.
- Generated outputs are stamped with the source document identifiers, prompt version and model identifier.

Decisions are logged as structured **CloudWatch Logs** events with a correlation identifier, **Bedrock** invocation logging keeps the full requests and responses, and **CloudTrail** records the API calls with data events enabled for agents and knowledge bases. **Athena** over the trail bucket and **QuickSight** produce the compliance reports.

Organisational control is preventive. **Service control policies** deny **Bedrock** outside the approved Regions and deny model customisation without an approved tag, **Control Tower** supplies the landing zone, the guardrail-identifier **IAM** condition makes the bank's guardrail mandatory for every role, and a **Step Functions** approval workflow gates promotion. The country with strict residency runs preprocessing on **Outposts** and sends only sanitised text to **Bedrock**.

Monitoring closes the loop: **Model Monitor** with **Clarify** bias drift on the **SageMaker** endpoints, **CloudWatch** anomaly detection on token usage, scheduled evaluations of production prompts, and **EventBridge** rules that trigger rollback or traffic shifting when a threshold is crossed.

The exam's questions on this scenario ask for the framework that documents, tracks, logs and remediates automatically. The answer is model cards, **Glue** and lineage, tags, **CloudWatch Logs**, and event-driven remediation.

## Exam lens

- "Document model behaviour and limitations, track all data sources, attribute every source, central decision logs, minimal manual effort" → programmatic **SageMaker Model Cards**, **Glue** (**Data Catalog** and ETL) for lineage, metadata tags for attribution, and **CloudWatch Logs** for decision logs.
- "Reviewers need source lineage for generated content, least overhead" → tag FM outputs with source metadata, and register the input datasets in the **Glue Data Catalog**.
- "Track model provenance" → **SageMaker ML Lineage Tracking**. "Reproduce training data" → **S3 Versioning** or **Feature Store** time travel.
- "Detect and alert on bias drift over time" → **SageMaker Model Monitor** with **Clarify** bias drift. "Measure bias in training data and predictions per Region, low code" → **Clarify** pre- and post-training bias metrics plus endpoint bias monitoring publishing to **CloudWatch**.
- "Every team's FM calls must apply the guardrail, no new infrastructure" → the **IAM** `bedrock:GuardrailIdentifier` condition on all roles, which is an organisational control, not a proxy.
- "Regulated documents must stay in the jurisdiction but use **Bedrock**" → **Outposts** for local preprocessing and redaction, with sanitised data to **Bedrock** in Region.
- "Auditable record of who called which API" → **CloudTrail**, with data events for agents, knowledge bases and flows. "What was sent and returned" → **Bedrock** model invocation logging. "Why the application decided" → structured **CloudWatch Logs**.
- "Automated evidence collection against a GenAI best-practices framework" → **AWS Audit Manager**, now closed to new customers.
- "Governance violation detected, remediate without a person" → an **EventBridge** rule to **Lambda** or **Step Functions**: rollback, traffic shift, disable, notify.

## Knowledge check

<!-- KC: E1-Q13, PQ-Q3, E2-Q10, E3-Q27, E3-Q22 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 13

A national insurance company is deploying a large FM–powered claims-assistance system in Amazon Bedrock. Because the system will be reviewed by internal auditors and external regulators, the compliance team requires:

- End-to-end data lineage for all training and inference data
- Verifiable documentation describing model behavior, limitations, and evaluation results
- Full attribution for every data source feeding the system
- A centralized log trail showing major FM decisions and inference outputs

The AI engineering team must implement a compliance framework that automates these requirements without adding significant operational burden.

Which solution BEST meets the compliance objectives?

- **A)** Use Step Functions to orchestrate all model workflows and export execution histories to CloudTrail for compliance visibility.
- **B)** Configure Amazon Bedrock to export all inference prompts and responses to an SQS queue, then build a custom compliance dashboard using Lambda and DynamoDB.
- **C)** Use SageMaker AI to programmatically generate and store model cards, configure AWS Glue Data Catalog to track data lineage and apply metadata tags for source attribution, and enable CloudWatch Logs to collect detailed inference decision logs.
- **D)** Store model documentation manually in an S3 bucket, enable S3 access logs for compliance, and rely on IAM policies to ensure analysts can review historical model activity.

<details><summary>Answer</summary>

**Answer: C.** SageMaker programmatic model cards produce verifiable documentation of behaviour, limitations and evaluation results, the AWS Glue Data Catalog with metadata tags tracks data lineage and attributes every source, and CloudWatch Logs collects the detailed inference decision logs, all generated automatically. Step Functions histories exported to CloudTrail are not lineage or documentation, an SQS-and-DynamoDB dashboard is custom and covers only inference, and manual documentation in S3 with access logs is exactly the operational burden the team must avoid.

*Where this is covered: Unit 04, Tracking data lineage and source attribution. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Official practice question set, question 3

An education company built a content generation system on Amazon Bedrock. The system generates practice questions to quiz end users on a topic to test their knowledge. The system consumes a mix of curated data and scraped data in the topic domain. Reviewers must approve of the generated question-response sets before end users can access the sets. The company wants to improve the system by adding source lineage for the reviewers to verify the credibility of the content.

Which combination of steps will meet these requirements with the LEAST operational overhead? **(Select TWO)**

- **A)** Enable Amazon Bedrock invocation logging and correlate the logs with the data source.
- **B)** Tag FM outputs with metadata from the data source.
- **C)** Use AWS CloudTrail to log reviewer feedback actions.
- **D)** Use Amazon SageMaker Clarify to explain model predictions.
- **E)** Register the curated and scraped input datasets with AWS Glue Data Catalog.

<details><summary>Answer</summary>

**Answer: B, E.** Tagging each generated question-response set with metadata from the data source it was drawn from gives reviewers direct source lineage, and registering the curated and scraped datasets in the AWS Glue Data Catalog makes those sources first-class, documented objects the tags can point to, both with minimal ongoing work. Correlating invocation logs with sources after the fact is heavy and indirect, CloudTrail logging of reviewer actions records approvals rather than lineage, and SageMaker Clarify explains model predictions rather than tracing content to sources.

*Where this is covered: Unit 04, Tracking data lineage and source attribution. Key: AWS official answer.*

</details>

### 3. Exam 2, question 10

A global insurance company is rolling out a new AI assistant powered by Amazon Bedrock to support claims agents. As part of its updated AI governance program, the security team requires that all interactions with foundation models—across every internal tool and microservice—must automatically apply predefined guardrails. The solution must work across multiple teams with minimal operational overhead and without adding new infrastructure or custom code paths.

Which solution will enforce guardrail compliance for all InvokeModel and Converse API calls in the MOST operationally efficient way?

- **A)** Create a centralized AWS Lambda proxy service that validates incoming payloads and injects guardrail identifiers before forwarding requests to Amazon Bedrock.
- **B)** Store guardrail identifiers in AWS Systems Manager Parameter Store and require all application teams to retrieve the identifier before invoking Amazon Bedrock APIs.
- **C)** Configure IAM policies for InvokeModel and Converse API calls that require the bedrock:GuardrailIdentifier condition key. Apply these policies to all IAM roles that interact with the FM APIs.
- **D)** Configure IAM policies with both the bedrock:GuardrailIdentifier and bedrock:PromptRouterArn condition keys and enforce prompt router validation for all foundation model access.

<details><summary>Answer</summary>

**Answer: C.** IAM policies that require the bedrock:GuardrailIdentifier condition key on InvokeModel and Converse, applied to every role that calls the FM APIs, make the approved guardrail mandatory across all teams and microservices with no new infrastructure or code paths. A central Lambda proxy is new infrastructure that can be bypassed, Parameter Store relies on every team remembering to look up the identifier, and adding a PromptRouterArn condition imposes prompt routing that has nothing to do with guardrail compliance.

*Where this is covered: Unit 04, Organisational governance systems. Key: ours, confidence high.*

</details>

### 4. Exam 3, question 27

A multinational insurance company operates in regions with strict data-residency requirements. Customer claim documents and policy records must remain on-premises within each jurisdiction, but the company wants to use Amazon Bedrock to generate claim summaries and policy-explanation text. The solution must allow the foundation model to operate on the data without moving regulated content outside the regional boundaries. The architecture must also support consistent inference patterns across countries while minimizing operational overhead.

Which solution will BEST satisfy these compliance and FM access requirements?

- **A)** Set up an S3 bucket in the primary AWS Region and upload all claim documents from each country. Apply KMS multi-Region keys and use Amazon Bedrock Guardrails to ensure that the FM handles sensitive information safely.
- **B)** Deploy AWS Outposts racks in each jurisdiction and run containerized preprocessing services locally. Route sanitized feature vectors or redacted text from Outposts to Amazon Bedrock in the nearest AWS Region for FM inference, ensuring regulated data never leaves the local environment.
- **C)** Deploy SageMaker AI endpoints inside the corporate data centers and sync the on-premises data to Amazon Bedrock with scheduled export jobs. Perform FM inference in the cloud and return results to on-premise systems.
- **D)** Use AWS Wavelength Zones in each country to cache on-premises data in local carrier networks and run Bedrock model inference directly inside the Wavelength Zone to ensure compliance with data-locality requirements.

<details><summary>Answer</summary>

**Answer: B.** AWS Outposts racks in each jurisdiction run the preprocessing and redaction on premises, so only sanitised text or feature vectors travel to Amazon Bedrock in the nearest Region and the regulated documents never leave the local boundary, with a consistent inference pattern everywhere. Uploading all documents to a primary-Region bucket violates residency however it is encrypted, SageMaker endpoints do not run in corporate data centres and syncing the data to Bedrock moves it anyway, and Wavelength Zones neither host Bedrock nor keep data on premises.

*Where this is covered: Unit 04, Organisational governance systems. Key: ours, confidence high.*

</details>

### 5. Exam 3, question 22

A regional hospital network is building a generative decision-support assistant that suggests follow-up care plans for patients. The assistant uses Amazon SageMaker AI to train predictive models from EHR data, lab results, and demographic attributes, and uses an FM in Amazon Bedrock to generate natural language explanations of the recommended plans. The system runs in multiple Regions to comply with local healthcare regulations.

During internal review, clinicians raise concerns that recommendations may differ across patient groups (for example, older patients vs. younger patients, or different socioeconomic segments). The data science team wants a managed way to measure and monitor bias across these groups in training data and model predictions, surface metrics per Region, and minimize the amount of custom fairness code they must maintain.

Which approach best satisfies the fairness and monitoring requirements with the least operational complexity?

- **A)** Use Amazon SageMaker Clarify to compute pre-training and post-training bias metrics, enable built-in bias monitoring on SageMaker endpoints in each Region, and publish Clarify bias metrics to Amazon CloudWatch for alerting on demographic disparities.
- **B)** Use Amazon Comprehend Medical to annotate patient notes with entities and sentiment labels, then create custom AWS Glue jobs that periodically scan SageMaker prediction outputs and flag differences in recommendations across demographic attributes.
- **C)** Use AWS Lambda to postprocess predictions from SageMaker endpoints, write outputs and demographic attributes to Amazon S3, and build a custom fairness dashboard in Amazon QuickSight to manually review discrepancies among patient segments.
- **D)** Use Amazon SageMaker Model Monitor data-quality monitors to track input feature distributions, and configure Amazon SNS alerts when feature distributions for specific demographic attributes deviate from historical baselines.

<details><summary>Answer</summary>

**Answer: A.** SageMaker Clarify computes pre-training bias metrics on the EHR training data and post-training metrics on predictions across the age and socioeconomic groups, Model Monitor's built-in bias drift monitoring on the endpoints in each Region keeps measuring in production, and publishing the metrics to CloudWatch gives per-Region alerting with almost no custom fairness code. Comprehend Medical annotations with custom Glue scans, Lambda post-processing with a QuickSight dashboard, and data-quality monitors on feature distributions are either custom code or do not measure bias.

*Where this is covered: Unit 04, Continuous monitoring and automated remediation. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

A compliance framework does three things.

It **documents the model** with **SageMaker Model Cards**, which carry intended uses, risk rating, evaluation results, immutable versions and PDF export, generated from pipelines and tied to the **Model Registry** and **Model Dashboard**.

It **tracks the data** with the **Glue Data Catalog** and ETL, **DataZone** lineage, **SageMaker ML Lineage Tracking**, **S3 Versioning** and **Feature Store**, and metadata tags on resources, objects and generated outputs.

It **logs the decisions** with structured **CloudWatch Logs**, **Bedrock** invocation logging, and **CloudTrail** management and data events.

Organisation-wide controls keep every team inside policy: **SCPs**, **Control Tower**, **IAM** conditions such as the guardrail identifier, tag policies, **Config**, approval workflows in **Step Functions**, **Model Registry** status, role separation, and residency through Regions, geographic profiles and **Outposts**.

Continuous monitoring feeds **EventBridge**-driven remediation. That monitoring is **Model Monitor**'s data quality, model quality, bias drift and feature attribution drift, plus **CloudWatch** metrics and anomaly detection and scheduled evaluations. Token-level redaction, response logging and output policy filters keep the running system compliant.
