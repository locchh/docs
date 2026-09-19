# AIP-C01 Learning Path

A four-day, read-it-top-to-bottom preparation path for the **AWS Certified Generative AI Developer – Professional (AIP-C01)** exam.

The path follows the exam guide's five content domains. Each domain folder holds a short README and numbered units. Every unit teaches one task statement through explanations, short paragraphs and lists, with key services and concepts highlighted.

Read each unit in this order:

- The explanations introduce each AWS service the first time it appears.
- A *Worked scenario* combines the skills in one company and one end-to-end design.
- An *Exam lens* maps question wording to answers.
- A *Knowledge check*, built from real practice questions in `../exams/`, lets you apply what you just read while it is fresh.

Each domain ends with a review unit: decision tables, the words that give answers away, a one-page summary and a mixed quiz.

Source material: the AWS exam guide (task statements and skills), the five AWS Skill Builder Domain Review courses (rewritten and expanded, not copied), the AWS documentation for every service named (facts verified against the docs as of September 2026), and the 230 questions in `../exams/` (Exam 1 with your graded results, Exams 2 and 3, and the 20 official practice questions).

## The exam in one paragraph

The exam has 65 scored questions plus 10 unscored ones, using multiple choice and multiple response. It lasts about 170 minutes, with a scaled score of 100–1,000 and 750 to pass. Scoring is compensatory: a weak domain can be carried by a strong one.

Questions are long scenarios that end in "Which solution BEST / MOST cost-effectively / with the LEAST operational overhead meets these requirements?". The correct answer is almost always the *managed, native* AWS capability that matches the requirement wording exactly. The distractors are custom builds, the wrong service for the job, or a real service used for the wrong purpose.

## Domains and where they live

| Domain | Weight | Folder | Units | Questions |
|---|---|---|---|---|
| 1. Foundation Model Integration, Data Management, and Compliance | 31% | [`01-fm-integration-data-compliance/`](01-fm-integration-data-compliance/README.md) | 6 + review | 74 |
| 2. Implementation and Integration | 26% | [`02-implementation-integration/`](02-implementation-integration/README.md) | 5 + review | 44 |
| 3. AI Safety, Security, and Governance | 20% | [`03-safety-security-governance/`](03-safety-security-governance/README.md) | 5 + review | 49 |
| 4. Operational Efficiency and Optimization for GenAI Applications | 12% | [`04-operational-efficiency-optimization/`](04-operational-efficiency-optimization/README.md) | 3 + review | 21 |
| 5. Testing, Validation, and Troubleshooting | 11% | [`05-testing-validation-troubleshooting/`](05-testing-validation-troubleshooting/README.md) | 3 + review | 35 |
| Appendix: glossary, mock exam key, out-of-scope quiz, cross-domain decision tables | | [`appendix/`](appendix/README.md) | 4 | 7 (out of scope) |

## Four-day schedule

Plan on six to eight focused hours a day. Read a unit, do its knowledge check immediately, and move on. Do not reread; the end-of-domain quiz and the day-4 mock bring everything back.

| Day | Morning | Afternoon |
|---|---|---|
| 1 | Domain 1 units 01–03 (design, model selection, data pipelines) | Domain 1 units 04–06 (vector stores, retrieval, prompts) and the Domain 1 review quiz |
| 2 | Domain 2 (agents, deployment, integration, APIs, developer tools) | Domain 2 review, then the 20 official practice questions |
| 3 | Domain 3 (**guardrails**, security, privacy, governance, responsible AI) | Domain 4 (cost, performance, monitoring) and both review quizzes |
| 4 | Domain 5 (evaluation, quality assurance, troubleshooting) and its review | Timed mock: Exam 3 graded with the appendix answer key (or the Official Pretest if you have a Skill Builder subscription), then work through every miss with the unit it points to |

## How the questions are used

Each knowledge check shows the question exactly as it appears in the source exam, with the answer hidden behind a fold. Under the fold you get the answer, a short rationale that also dismisses the distractors, the unit section that settles it, and the key's origin.

Exam 1 carries the ExamPro key you were graded against; the official practice set carries AWS's answers. Exams 2 and 3 were captured without keys, so their answers are ours. Each is marked *high* confidence when AWS documentation settles it, or *medium* when the question is ambiguous. The appendix collects all of them into one answer key for a timed mock.

Two Exam 1 questions are keyed differently from ExamPro where the official practice set contains the same question with a different answer. The folds explain why.

Questions that test model training or classical ML rather than GenAI development are out of scope for this exam and are kept in the appendix quiz so they do not eat your time.

## Service status

AWS moved several services named in the exam guide into maintenance mode in 2026. These are closed to new customers:

- **Amazon Bedrock Agents**, now **Agents Classic**.
- **Amazon Kendra**.
- **Amazon Q Business**.
- **Amazon A2I**.
- **AWS Audit Manager**.
- **CloudTrail Lake**.
- The **SageMaker** features **Model Monitor**, **Clarify** and **Ground Truth**.

**CloudWatch Evidently** was discontinued in 2025. The exam and its questions still use these names, so the units teach what the exam expects. They also note what AWS recommends today, including **AgentCore**, **Amazon Quick**, **Bedrock Evaluations** and **AppConfig**.

## Official companions

The AWS Skill Builder *Exam Prep Plan: AWS Certified Generative AI Developer – Professional* is free for its Domain Review courses and Official Practice Question Set; the Domain Practice sets, SimuLearn labs, and Official Pretest need a subscription. This path points to those items where they fit.

## About `_build/`

The `_build/` folder holds the scripts and answer-key files that generate the knowledge checks from the exam files, plus blind versions of each domain's questions used to test the path. You do not need it to study; it is kept so the checks can be regenerated if a question or key changes.
