# Unit 05: Responsible AI principles

**Task 3.4: Implement responsible AI principles.** This unit is about the three things a responsible AI system owes its users and its owners:

- **Transparency**: show how an answer was produced, with evidence and a confidence signal.
- **Fairness**: measure whether outputs treat groups differently, and keep measuring.
- **Policy compliance**: turn written responsible-AI policy into enforced controls and documented limitations.

Most of the mechanisms were introduced in units 01 to 04. This unit shows how they combine for these three goals, and adds the fairness metrics and evaluation tooling.

## The dimensions AWS uses

AWS describes responsible AI along eight dimensions, and exam options often echo them:

- **Fairness**: no unjust impact on groups.
- **Explainability**: humans can understand and evaluate outputs.
- **Privacy and security**: data protected from theft and exposure.
- **Safety**: harmful output prevented.
- **Controllability**: behaviour can be monitored and steered.
- **Veracity and robustness**: correct outputs, also under unexpected or adversarial input.
- **Governance**: processes and accountability.
- **Transparency**: people know what the system does and its limits.

Units 01 to 04 covered safety, privacy, security and governance. This unit covers transparency, fairness and the policy layer that ties them together.

AWS publishes **AI Service Cards** for its own services, and model providers publish **model cards** for their FMs. Both are transparency artefacts you can cite when documenting limitations.

## Transparent systems: show the work

Transparency for an FM application has four parts, and the exam wants all four delivered with managed features rather than a custom observability platform.

**Reasoning displays.** Prompt the model to reason before it answers, using **chain-of-thought**: "think step by step, then give the recommendation and its limitations". Show the reasoning to the user, streamed as it is produced, so people see the answer being built. Structure the output into understanding, factors considered, analysis, recommendation and limitations, so the display is consistent.

Be honest about what it is. Model-written reasoning is an explanation the model generates, not a guaranteed trace of its computation, which is why it is paired with the next two parts.

**Agent traces.** For an application built on **Amazon Bedrock Agents**, `InvokeAgent` with `enableTrace` returns a **trace** of every step:

- The **pre-processing** trace: was the input valid, and how was it classified.
- The **orchestration** trace, with the agent's **rationale**, each **invocation input** naming which action group or knowledge base it called and with what parameters, and each **observation** of what came back, including the knowledge-base chunks retrieved.
- The **post-processing** trace.
- A **guardrail** trace when a guardrail intervened.
- A **failure** trace when a step failed.

That is full visibility into retrieval steps and intermediate actions at zero engineering cost, and it is the phrase "**Amazon Bedrock** agent tracing to provide reasoning traces" in the task statement.

For agents on **AgentCore**, **AgentCore Observability** emits the same kind of step-by-step spans through **OpenTelemetry** into **CloudWatch**. Knowledge base calls (`RetrieveAndGenerate`) return **citations** with the retrieved passages and their source locations for the same reason.

**Evidence presentation and source attribution.** Show the citations: which document, which passage, with a link, next to each claim, so a user can verify the answer against the source. This is RAG's built-in transparency and the reason grounded answers are preferred for regulated advice. The same references, stored with the response, become the attribution record that unit 04 asked for.

**Confidence and uncertainty metrics.** Quantify how sure the system is, and show it. A confidence signal can come from several sources:

- The **grounding and relevance scores** from a contextual grounding check.
- The **similarity score** between the answer and its sources.
- The **retrieval scores** of the chunks used.
- A **judge model's** score.
- The model's own **self-reported confidence** when asked for one. Calibrate it against measured accuracy before trusting it.
- Where a model exposes them, **token log-probabilities**: the model's own probability for each generated token, where a low value means it was unsure.

Publish these as **CloudWatch custom metrics** in an application-specific namespace, never under `AWS/Bedrock` or another `AWS/` namespace, which are reserved for AWS services. Chart them on dashboards, alarm on drops, and display a per-answer indicator to the user.

**CloudWatch** is the collection and visualisation service here. **QuickSight** builds business dashboards over stored data, **Athena** queries **S3**, and **Glue DataBrew** prepares data, none of which collects metrics from a running application.

The exam's composite answer for "user-facing explanations, visibility into retrieval and agent actions, confidence metrics, source attribution, minimal custom code" is agent tracing plus **CloudWatch** metrics plus reasoning displays and attributed evidence in the UI. The heavier or mismatched alternatives are building middleware to compute uncertainty by hand, exporting prompts to **S3** for a **Glue** and **Athena** pipeline, or running **SageMaker Clarify** on every FM call, since **Clarify** explains feature attributions of models you host, not **Bedrock** inference calls.

## Fair systems: measure, compare, monitor

**Bias** is a systematic difference in how a system treats groups defined by a **facet**, which is a sensitive attribute such as age band, gender, ethnicity, region or socioeconomic segment. It can enter in two ways:

- Through the **data**, as **pre-training bias**: one group under-represented, or labels skewed.
- Through the **model**, as **post-training bias**: predictions or generations that differ by group even for comparable inputs.

For a classifier, the standard fairness notions are:

- **Demographic parity**: equal positive rates across groups.
- **Equal opportunity** and **equalised odds**: equal true-positive rates, or equal true- and false-positive rates.
- **Disparate impact**: the ratio of positive rates.
- **Counterfactual fairness**: the output does not change when only the facet changes.

For a generative model the same ideas apply to what it produces. Does the tone, quality, refusal rate or recommendation change with the demographic cues in the prompt?

**SageMaker Clarify** is the AWS tool for classical and hosted models. It is closed to new customers, as the domain README notes, but it is still the keyed answer wherever it appears. It does three things in one processing job: **pre-training bias metrics** on the dataset, **post-training bias metrics** on predictions, and **explainability** reports.

The pre-training metrics you should recognise are:

- **Class Imbalance (CI)**: are the groups different sizes?
- **Difference in Proportions of Labels (DPL)**: do they get positive labels at different rates?

Both are backed by several distribution-distance measures. The post-training metrics are:

- **Difference in Positive Proportions in Predicted Labels (DPPL)**.
- **Disparate Impact (DI)**: the ratio of positive prediction rates.
- **Accuracy Difference (AD)** and **Recall Difference (RD)**.
- The **Counterfactual Fliptest (FT)**: does the prediction flip when only the facet changes?

Further acceptance, rejection and conditional-disparity differences are listed in the glossary. Explainability uses **SHAP** values, which measure how much each feature pushed a prediction, with global and per-instance reports and partial dependence plots.

**Clarify** also evaluates foundation models you host on **SageMaker**, and its FM evaluation library measures toxicity, prompt stereotyping, factual knowledge, accuracy and robustness. Combined with **Model Monitor** **bias drift** and **feature attribution drift** from unit 04, **Clarify** is the answer to "detect dataset bias, evaluate model bias in production and generate explainability reports".

The alternatives fall short in specific ways. **Model Monitor** alone tracks quality and drift without fairness, **Amazon Personalize**, the managed recommendation service, and **Data Wrangler** rebalance or tune without measuring, and **Comprehend Medical** annotates text. **Clarify** is *not* the answer for evaluating **Bedrock** FM outputs at scale with no custom pipeline; that is the next section.

For FMs on **Bedrock** the low-code fairness toolkit is:

- **Amazon Bedrock Evaluations with LLM-as-a-judge.** An evaluation job sends your prompt dataset, built to represent diverse groups and edge cases, to the generator model, and has a **judge model** score each response. The built-in metrics include correctness, completeness, faithfulness, helpfulness, coherence, relevance, instruction following, professional style and tone, **harmfulness**, **stereotyping** and **refusal**, and you can add **custom metrics** written as rubrics. Scores and explanations appear in the console and in **S3**. Split the dataset by demographic group and the per-group scores become fairness metrics. **Human evaluation** jobs, with your own workforce or an AWS-managed team, calibrate the judge and cover what automation misses.
- **Systematic A/B testing with Prompt Management and Flows.** Create prompt **variants** in **Amazon Bedrock Prompt Management**, which holds versioned templates with variables, designed to reduce bias for particular groups. Then build a **Bedrock Flow**, the visual workflow builder still called **Prompt Flows** in the exam guide, that routes each test query through the variants and an evaluation step, so every prompt strategy is measured on the same controlled test sets. Control for confounders, use stratified samples across groups, and check statistical significance before declaring a winner.
- **CloudWatch fairness metrics.** Publish per-group scores, such as refusal rate, judge scores, sentiment of generated text and response length, as custom metrics. Dashboard them across model versions, and alarm when a group's metric deviates from the others beyond a threshold, which turns a one-off audit into continuous monitoring.

The keyed pattern for "measure fairness over time, compare controlled test groups, automatically score responses for equity violations, minimal engineering" is **Bedrock Flows** running controlled A/B tests on demographic test sets, fairness metrics published to **CloudWatch**, and an **LLM-as-a-judge** evaluation scoring bias. Sentiment analysis, image analysis and transcript redaction are not bias evaluations.

## Policy-compliant systems: policy into controls

A responsible-AI policy is a document; compliance is behaviour. The translation has four steps, and the exam expects them together.

1. **Encode the policy in guardrails.** Each policy clause becomes a guardrail configuration. Prohibited subjects become **denied topics**, harmful-content rules become content-filter strengths, privacy rules become **sensitive-information filters**, accuracy rules become **contextual grounding** thresholds, and business or regulatory rules written in a policy document become an **Automated Reasoning** policy that checks every response against them. Different guardrail versions serve different contexts, such as a clinical workflow versus a marketing assistant, and the `bedrock:GuardrailIdentifier` **IAM** condition makes the approved version mandatory.
2. **Document limitations in model cards.** Record what the FM must not be used for, the known failure modes found in evaluation, the demographic groups where performance was weaker, and the disclosures users receive. Keep them in **SageMaker Model Cards**, or an equivalent card for the application, regenerated by the pipeline whenever evaluations change.
3. **Automate compliance checks in Lambda.** A post-processing function evaluates each response against rules the guardrail cannot express: required disclaimers present, forbidden recommendations absent, numbers within policy limits, citations attached, tone acceptable. It blocks, rewrites or flags, and logs the check. The same rule engine runs in CI/CD on evaluation datasets before a prompt or model change ships.
4. **Monitor and prove it.** Use **CloudWatch** metrics and alarms on guardrail interventions, compliance-check failures and fairness metrics, structured logs and **CloudTrail** as the audit trail from unit 04, guardrail, prompt and policy configurations under version control released through a pipeline with approvals, and automated reports that assemble the evidence.

For a government or regulated deployment that must "enforce content safety and restricted topics, disclose FM limitations, validate each request and response, with minimal custom enforcement", the answer is **Bedrock Guardrails** configured to the policy, model cards for the limitations, and a lightweight **Lambda** post-processing check. It is not an **EC2** microservice comparing text to policy documents, a nightly **EventBridge** batch that samples responses, or **SageMaker** endpoints with hand-written validation containers.

And when a company simply wants outputs that adhere to its policy against harmful content, the feature is **Bedrock Guardrails**, not **Inspector** (vulnerability scanning), **Shield** (DDoS protection) or **Macie** (**S3** data discovery).

## Human oversight and feedback

Responsible systems keep a person in the loop where stakes are high. Four practices do that:

- Route low-confidence, high-risk or flagged responses to human review, with **Step Functions** wait-for-callback steps, or **Amazon A2I** for existing customers.
- Collect structured feedback from users and reviewers, and feed it into prompt revisions, guardrail tuning and evaluation datasets.
- Give users a way to contest an automated outcome.
- Tell users they are interacting with AI and what it cannot do.

These are the controllability and transparency dimensions in practice, and they are what "continuous improvement" means in the scenario transcripts.

## Worked scenario

A public agency builds an assistant that helps citizens understand benefit eligibility. Advocacy groups ask how answers are produced, whether people from different backgrounds get equally good guidance, and how the agency guarantees the assistant follows its published policy.

Transparency is designed in.

- The assistant runs as an agent whose trace is enabled, so every retrieval, tool call and rationale is recorded and can be shown.
- Answers carry citations to the eligibility rules they rest on.
- The prompt asks the model to state its reasoning steps and the conditions it assumed.
- Each answer is accompanied by a confidence indicator derived from the grounding score, the retrieval scores and a judge model's assessment, published as **CloudWatch** custom metrics in the agency's namespace, so uncertainty trends are visible on a dashboard.

Users are told they are talking to an AI and how to reach a caseworker.

Fairness is measured, not assumed. The team builds evaluation sets in which the same eligibility question is asked with different demographic cues, covering age, language and household type. It runs them through **Bedrock Evaluations** with **LLM-as-a-judge** metrics for correctness, completeness, helpfulness and stereotyping, plus a custom equity rubric, and splits the scores by group.

**Prompt Management** variants designed to reduce the gaps are routed through a **Bedrock Flow** for controlled A/B comparison, and per-group scores are published to **CloudWatch** with alarms on divergence. The eligibility classifier that pre-screens applications is evaluated with **SageMaker Clarify** pre- and post-training bias metrics, and monitored for bias drift in production. Human reviewers score a sample each month to calibrate the judge.

Policy compliance is encoded. The agency's published policy becomes a guardrail: denied topics for legal advice, content filters, sensitive information masking, a grounding threshold, and an **Automated Reasoning** policy built from the eligibility handbook, so every answer is checked against the written rules. A model card documents the FM's limitations and the disclosures users receive, a **Lambda** post-processing function confirms the mandatory referral text is present and logs the check, **CloudWatch** alarms track violations, and every prompt, guardrail and policy version is under version control with an approval step.

A question built on this scenario asks for three things: transparency with minimal custom code (traces, **CloudWatch** metrics, reasoning displays), fairness evaluation at scale (**Flows** A/B tests, **CloudWatch** fairness metrics, **LLM-as-a-judge**), and policy compliance without a large enforcement layer (guardrails, model cards, **Lambda** checks).

## Exam lens

- "User-facing explanations, visibility into retrieval and agent steps, confidence metrics, source attribution, minimal custom code" → **Bedrock** agent tracing, **CloudWatch** custom metrics for confidence, and reasoning displays with attributed evidence in the UI.
- "Collect and visualise confidence or uncertainty metrics" → **Amazon CloudWatch** custom metrics in an application namespace, not `AWS/Bedrock`, and not **QuickSight**, **Athena** or **DataBrew**.
- "Measure fairness over time, controlled demographic test groups, automatic equity scoring, no custom pipeline" → **Bedrock Flows** A/B tests plus **CloudWatch** fairness metrics plus **LLM-as-a-judge**.
- "Dataset bias, model bias in production, explainability reports", for a **SageMaker** model → **SageMaker Clarify**, with **Model Monitor** bias drift.
- "Automated bias evaluation of FM outputs" → **Bedrock** with **LLM-as-a-judge**, not sentiment analysis.
- "Enforce policy, document limitations, validate every request and response, minimal enforcement layer" → **Bedrock Guardrails** from policy rules, model cards, and **Lambda** compliance checks.
- "Outputs must adhere to a policy against harmful content" → **Bedrock Guardrails**, not **Inspector**, **Shield** or **Macie**.
- "Which fairness metric?" → **DPL** for labels in data, **DPPL** for predicted labels, **DI** for the ratio, **AD** or **RD** for accuracy or recall gaps, **CI** for group sizes, and **FT** for counterfactual flips.

## Knowledge check

<!-- KC: E1-Q4, E1-Q57, E2-Q57, E1-Q29 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 4

A financial services company is building an internal generative AI assistant using Amazon Bedrock to help analysts summarize regulatory filings and justify recommendations. The company must increase transparency so end users can understand how each response was produced. The governance team requires user-facing explanations of model reasoning, full visibility into retrieval steps and intermediate agent actions, confidence and uncertainty metrics with each response, and clear source attribution for extracted evidence. The engineering team wants a solution that provides all transparency features with minimal custom code and without building an external observability system.

Which approach BEST meets these requirements?

- **A)** Enable Amazon Bedrock agent tracing to capture reasoning steps, integrate CloudWatch metrics to store confidence scores, and present model-generated reasoning displays and attributed evidence directly in the application UI.
- **B)** Build a custom middleware layer in AWS Lambda that logs each inference, computes uncertainty scores manually, and enriches responses with structured metadata.
- **C)** Export raw model prompts and responses to Amazon S3, build a custom analytics pipeline in AWS Glue, and surface insights with Athena and QuickSight dashboards.
- **D)** Use Amazon SageMaker Clarify to generate model explainability reports for each FM inference call and store the results in Amazon S3 for analyst review.

<details><summary>Answer</summary>

**Answer: A.** Bedrock agent tracing exposes every reasoning step, knowledge-base retrieval and intermediate action, CloudWatch custom metrics store the confidence and uncertainty scores, and presenting the model's reasoning displays and attributed evidence in the application UI gives users the explanations and source attribution, all with minimal custom code and no external observability system. A custom Lambda middleware computes uncertainty by hand, a Glue, Athena and QuickSight pipeline over raw prompts is an external analytics system, and SageMaker Clarify explains feature attributions of hosted models rather than FM inference calls.

*Where this is covered: Unit 05, Transparent systems: show the work. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 1, question 57

A healthcare analytics company is developing a generative AI system on Amazon Bedrock to help clinicians interpret patient risk summaries. During initial testing, the governance team discovers variation in outputs when patient profiles from different demographic groups are analyzed, raising concerns about fairness and potential bias. The organization needs a systematic, low-code approach to measure fairness metrics over time, compare model behavior across controlled test groups, and automatically score responses for equity violations. The solution should avoid building custom evaluation pipelines and must run evaluations at scale with minimal engineering effort.

Which approach BEST satisfies these requirements?

- **A)** Use a custom container in Amazon ECS that runs Python-based fairness scripts and pushes evaluation metrics to Amazon QuickSight dashboards.
- **B)** Use Amazon SageMaker Clarify to run bias detection on all FM outputs and require manual labeling by analysts before each model release.
- **C)** Use Amazon Bedrock Prompt Flows to run controlled A/B tests on demographic test sets, publish fairness metrics to Amazon CloudWatch for ongoing monitoring, and evaluate responses using an LLM-as-a-judge pattern in Amazon Bedrock to automatically score potential bias.
- **D)** Use Amazon Athena queries against S3 logs to manually compare responses from different demographic groups and export CSV reports for fairness audits.

<details><summary>Answer</summary>

**Answer: C.** Bedrock Prompt Flows run controlled A/B tests over demographic test sets, publishing fairness metrics to CloudWatch tracks them over time, and an LLM-as-a-judge evaluation in Bedrock automatically scores responses for bias, which is systematic, low-code and scales without a custom pipeline. Custom fairness scripts in ECS and Athena-plus-CSV audits are manual pipelines, and SageMaker Clarify with mandatory manual labelling before each release evaluates hosted models and adds human effort.

*Where this is covered: Unit 05, Fair systems: measure, compare, monitor. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 2, question 57

A global music-streaming provider is building a personalization engine using Amazon SageMaker AI to recommend playlists to millions of listeners worldwide. The ML team trains a neural network that predicts music preferences based on listening history, skipped tracks, mood-tagged playlists, and regional genre trends. After deployment, the compliance team observes that certain musical genres are recommended significantly more or less frequently in specific geographic markets, raising concerns about unintended demographic bias.

To meet internal fairness mandates and regulatory transparency requirements, the organization must analyze whether bias exists in the training dataset, determine whether the deployed model is amplifying bias in predictions, and automatically generate explainability reports showing which features most strongly influence playlist recommendations.

Which solution should the company implement to identify, measure, and explain potential bias across both the dataset and the model outputs?

- **A)** Use SageMaker Model Monitor to track error rates, latency, and data drift without evaluating fairness or explaining feature influence.
- **B)** Use SageMaker Clarify to detect dataset bias, evaluate model bias during inference, and generate feature attribution explainability reports for compliance and transparency.
- **C)** Use Amazon Personalize with automatic weight balancing to reduce region-specific recommendation skew without performing explicit fairness analysis.
- **D)** Use SageMaker Data Wrangler to manually rebalance the listening-history dataset before retraining the personalization model.

<details><summary>Answer</summary>

**Answer: B.** SageMaker Clarify detects bias in the training dataset with pre-training metrics, evaluates whether the deployed model amplifies bias with post-training metrics and bias-drift monitoring, and generates feature-attribution explainability reports showing which listening features drive recommendations, covering dataset, model and explanation in one tool. Model Monitor alone tracks quality and drift without fairness or explanations, Personalize weight balancing changes outputs without analysing bias, and Data Wrangler rebalancing is a manual data fix that measures nothing.

*Where this is covered: Unit 05, Fair systems: measure, compare, monitor. Key: ours, confidence high.*

</details>

### 4. Exam 1, question 29

A government research institute is deploying a generative AI system on Amazon Bedrock to help analysts review scientific grant proposals. Due to strict responsible AI regulations, the organization must ensure that every FM interaction complies with internal policy requirements, including content safety checks, restricted-topic filtering, and mandated disclosure of FM limitations. The governance team wants a solution that automatically enforces compliance, documents model constraints, and validates each request and response before downstream use. The engineering team must implement this without building a large custom enforcement layer.

Which approach BEST ensures policy-compliant AI behavior with minimal operational overhead?

- **A)** Use an Amazon EC2–based microservice that performs full-text comparison of FM outputs against stored policy definitions before returning responses to analysts.
- **B)** Use Amazon EventBridge to trigger a batch compliance workflow every night that analyzes a sample of FM responses and produces a compliance report for internal auditors.
- **C)** Use Amazon SageMaker hosting endpoints with fully custom container validation logic and manually written policy rule scripts that run before each inference call.
- **D)** Use Amazon Bedrock guardrails configured with the institute's policy rules, attach model cards describing FM limitations, and implement a lightweight AWS Lambda post-processing function to run automated compliance checks on each Bedrock response.

<details><summary>Answer</summary>

**Answer: D.** Bedrock Guardrails configured with the institute's policy rules enforce content safety and restricted topics on every request and response, model cards document the FM's limitations for the mandated disclosure, and a lightweight Lambda post-processing function runs the automated compliance checks, giving policy compliance without a large custom enforcement layer. An EC2 microservice comparing text to policy documents, a nightly EventBridge batch over a sample, and SageMaker endpoints with hand-written validation containers are all heavy custom enforcement.

*Where this is covered: Unit 05, Policy-compliant systems: policy into controls. Key: ExamPro answer key (Exam 1 graded).*

</details>

<!-- KC-END -->

## Summary

**Transparency** means showing the work: **chain-of-thought** reasoning displays, **Bedrock** agent traces with rationale, invocation inputs, observations, guardrail and failure traces, or **AgentCore Observability**, citations as evidence, and confidence signals published as **CloudWatch** custom metrics.

**Fairness** means measuring. For hosted models, **SageMaker Clarify** gives pre-training bias metrics, which are class imbalance and label-proportion difference, and post-training metrics, which are predicted-label difference, disparate impact, accuracy and recall differences, and the rest listed in the glossary, plus **SHAP** explainability, with **Model Monitor** bias drift in production. For FM applications, use **Bedrock Evaluations** with **LLM-as-a-judge**, **Prompt Management** variants and **Flows** for controlled A/B tests, and **CloudWatch** fairness metrics.

**Policy compliance** means encoding policy in guardrails, including **Automated Reasoning** from policy documents, documenting limitations in model cards, automating checks in **Lambda**, and monitoring and versioning everything, with humans reviewing what matters most.
