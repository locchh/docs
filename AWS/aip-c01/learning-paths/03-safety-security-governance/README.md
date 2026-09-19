# Domain 3: AI Safety, Security, and Governance

**Weight: 20% of the scored exam** (roughly 13 of the 65 scored questions). Domains 1 and 2 built the application. Domain 3 makes it safe to run in a regulated company:

- Filtering what goes into and comes out of the model.
- Isolating and governing the environment and its data.
- Protecting personal information.
- Proving compliance to auditors.
- Behaving responsibly toward users.

The domain has four task statements. Task 3.2 is split across two units because it covers two different things, the environment around the data and the data itself. The other tasks map one to one.

| Unit | Task statement | What you will be able to do |
|---|---|---|
| [01 Input and output safety controls](01-input-and-output-safety-controls.md) | 3.1 Implement input and output safety controls | Configure every **Bedrock Guardrails** policy, tier and action, apply guardrails to any call or text, read the metrics and traces, enforce them with **IAM**, build custom moderation workflows, use **Comprehend** toxicity detection, reduce hallucinations, assemble defense in depth, and detect prompt injection and jailbreaks |
| [02 Protected AI environments](02-protected-ai-environments.md) | 3.2 Implement data security and privacy controls (environment) | Keep **Bedrock** and **SageMaker** traffic private with **VPC endpoints** and isolation modes, scope **IAM** roles, federate identity through **IAM Identity Center** and **Cognito**, govern data with **Lake Formation**, encrypt with **KMS**, and audit with **CloudTrail** and **CloudWatch** |
| [03 Privacy-preserving systems](03-privacy-preserving-systems.md) | 3.2 Implement data security and privacy controls (data) | Discover sensitive data with **Macie**, detect and redact PII and PHI with **Comprehend** and **Comprehend Medical**, apply masking and anonymisation, use **Bedrock**'s privacy guarantees and guardrails, redact before indexing, and enforce retention with **S3 Lifecycle** and **Object Lock** |
| [04 AI governance and compliance](04-governance-and-compliance.md) | 3.3 Implement AI governance and compliance mechanisms | Generate **model cards**, track lineage and attribution with the **Glue Data Catalog**, lineage tracking and tags, keep decision and audit logs, apply organisation-wide controls and residency patterns, and monitor and remediate drift, bias and misuse |
| [05 Responsible AI principles](05-responsible-ai.md) | 3.4 Implement responsible AI principles | Make systems transparent with agent traces, citations and confidence metrics, evaluate fairness with **Clarify** and **LLM-as-a-judge**, run controlled A/B tests, and turn policy into guardrails, model cards and automated checks |
| [06 Domain review](06-domain-3-review.md) | all | Decision tables, the words that give answers away, a one-page summary, and a mixed quiz |

## How the questions are placed

The exam files hold 49 questions for this domain: 14 from Exam 1 (graded), 16 from Exam 2, 14 from Exam 3, and 5 from the official practice set. Units end with the questions that test their content, and six near-duplicates form the mixed quiz in unit 06.

Exam 2 and 3 keys are ours and carry a confidence mark. One Exam 1 question (question 28) is keyed differently from the ExamPro key, because the official practice set contains the same question with a different answer; the fold explains why.

## A note on service status

Several services named in questions have changed status since the exam guide was written. These are closed to new customers:

- **Amazon Kendra**, **Amazon Q Business** and **Amazon Augmented AI (A2I)**.
- **AWS Audit Manager** and **CloudTrail Lake**.
- The **Comprehend** **prompt safety classifier**.
- The **SageMaker** features **Model Monitor**, **Clarify** and **Ground Truth**.

**Amazon Bedrock Agents** is now **Agents Classic**, with **AgentCore** as the recommended path. The units say what the exam expects and what to use today.

## Time

About four hours for the five units plus the review. This is the morning of day 3.
