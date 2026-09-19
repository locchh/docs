# Domain 5: Testing, Validation, and Troubleshooting

**Weight: 11% of the scored exam** (roughly 7 of the 65 scored questions). Domain 4 put monitoring in place; Domain 5 asks how you *prove* a GenAI application is good, keep it good through every change, and find out why when it is not: evaluation frameworks and **Amazon Bedrock Evaluations**, user feedback and **quality gates**, reporting, deployment validation, and a diagnostic manual for the failure modes that only GenAI has.

The domain has two task statements. Task 5.1 has nine skills and is split across two units; Task 5.2 is one unit.

| Unit | Task statement | What you will be able to do |
|---|---|---|
| [01 Evaluation frameworks and Amazon Bedrock Evaluations](01-evaluation-frameworks.md) | 5.1 Implement evaluation systems (assessment frameworks, systematic model evaluation, comprehensive assessment, **retrieval quality testing**, agent performance) | Evaluate generated text on the right dimensions, run automatic, **LLM-as-a-judge**, human and **RAG evaluation** jobs, compare models and configurations offline and online with **production variants** and **A/B** or **canary** tests, test retrieval with **labelled datasets**, and evaluate agents |
| [02 Quality assurance, feedback, reporting and deployment validation](02-quality-assurance-and-deployment-validation.md) | 5.1 Implement evaluation systems (user-centered evaluation, quality assurance, reporting, deployment validation) | Collect and use user feedback, run **continuous evaluation** with **regression tests** and **quality gates** in CI/CD, report to stakeholders with **QuickSight**, validate releases with **synthetic workflows** and shadow or **canary** rollouts, and order a model-replacement workflow |
| [03 Troubleshooting GenAI applications](03-troubleshooting-genai-applications.md) | 5.2 Troubleshoot GenAI applications | Diagnose content-handling, integration, prompt, retrieval and prompt-maintenance problems with **invocation logs**, **Logs Insights**, **X-Ray**, evaluation jobs and the **Bedrock** error catalogue, and apply the fixes |
| [04 Domain review](04-domain-5-review.md) | all | Decision tables, the words that give answers away, a one-page summary, and a mixed quiz |

## How the questions are placed

The exam files hold 35 questions for this domain: 8 from Exam 1 (graded), 12 from Exam 2, 12 from Exam 3, and 3 from the official practice set (one of them an ordering question). Units end with the questions that test their content; eight near-duplicates and monitoring-flavoured items form the mixed quiz in unit 04. Exam 2 and 3 keys are ours and carry a confidence mark.

## A note on service status

Since 30 July 2026, these **SageMaker** services are closed to new customers, while existing customers continue:

- **SageMaker Model Monitor**
- **SageMaker Clarify**
- **SageMaker Ground Truth**

**Amazon A2I** is likewise closed to new customers. These services remain the exam's vocabulary and keyed answers. The units explain replacements for new work, including **Bedrock Evaluations**, **CloudWatch custom metrics** and in-app feedback pipelines.

**Amazon Bedrock AgentCore Evaluations** became generally available in 2026 and is the current form of "**Amazon Bedrock Agent evaluations**".

## Time

About two and a half hours for the three units plus the review. This is the morning of day 4, before the final mixed practice.
