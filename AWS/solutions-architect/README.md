# AWS Solutions Architect

A service-by-service course covering both AWS Solutions Architect exams from one
body of material.

| Exam | Code | Format | Pass |
|---|---|---|---|
| Solutions Architect – Associate | SAA-C03 | 65 questions, 50 scored, 130 minutes | 720 of 1,000 |
| Solutions Architect – Professional | SAP-C02 | 75 questions, 65 scored, 180 minutes | 750 of 1,000 |

## How the course is arranged

The material is organized by service, not by exam domain, because that is how the
underlying knowledge is actually shaped and how most video courses teach it. Each
service unit teaches the Associate level in its body, adds a `Professional depth`
section that an Associate candidate can skip, and ends with its own quiz.

On top of the service units sit eight exam domain guides, four per exam. Each one
maps that domain's task statements back to the service units and adds the
cross-cutting decision tables that no single service owns.

| Folder | What it holds |
|---|---|
| `services/` | 70 service units in 11 categories: storage, compute, containers, networking, database, integration, security, management, analytics, migration, machine learning and media |
| `domains/` | Exam domain guides: 4 for SAA-C03, 4 for SAP-C02 |
| `appendix/` | Glossary and cross-cutting decision tables |
| [`labs/`](labs/README.md) | Hands-on exercises against a real account. Five for Amazon S3 today, covering the CLI, Bash and PowerShell scripting, additional checksums and CORS |
| `_build/` | Planning and quality control for the course itself. Not study material |

## Status

Under construction. `_build/PROGRESS.md` tracks every file. `_build/HANDOFF.md`
explains how to continue the work.

The older per-topic notes are gone. Every one was folded into the service unit
that owns its material, and each fold was checked by an independent review
before the notes were deleted.

## Official resources

**Associate**

- [Certification page](https://aws.amazon.com/certification/certified-solutions-architect-associate/) - Official SAA-C03 certification page: exam overview, cost, scheduling and recertification
- [SAA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html) - The authoritative scope document: four domains with their weightings, every task statement, and the in-scope service list
- [Skill Builder exam prep plan](https://skillbuilder.aws/learning-plan/UYRXS2DF85/exam-prep-plan-aws-certified-solutions-architect--associate-saac03--english/U991QUF9C3) - Official AWS Skill Builder learning plan for SAA-C03, a sequenced set of courses and labs
- [Official practice question set, 20 questions, free](https://skillbuilder.aws/learn/6NV91XYP1P/official-practice-question-set-aws-certified-solutions-architect--associate-saac03--english/N1HSPV1K17) - Twenty AWS-written questions with answer explanations; the closest free sample of real exam wording
- [Official practice exam, subscription](https://skillbuilder.aws/learn/R3KVD4BBJY/official-practice-exam-aws-certified-solutions-architect--associate-saac03--english/W7GU3R1HCT) - Full-length timed practice exam from AWS, behind a Skill Builder subscription

**Professional**

- [Certification page](https://aws.amazon.com/certification/certified-solutions-architect-professional/) - Official SAP-C02 certification page: exam overview, recommended experience, cost and scheduling
- [SAP-C02 exam guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02.html) - The authoritative scope document: four domains with their weightings, every task statement, and the in-scope service list
- [Skill Builder exam prep](https://skillbuilder.aws/category/exam-prep/solutions-architect-professional-SAP-C02) - Official AWS Skill Builder exam-prep category for SAP-C02, collecting its courses, question sets and practice exam

**Both**

- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) - The six pillars both exams reason from; most "which option is best" answers trace back to one of them
- [AWS Architecture Center](https://aws.amazon.com/architecture/) - AWS reference architectures, diagrams and whitepapers; useful for seeing whole designs rather than single services
- [ExamProCo AWS Examples](https://github.com/ExamProCo/AWS-Examples) - A codebase of all the AWS examples used through AWS Certification Study Courses

Slide decks and cheatsheets live in the repository-root [assets/](../../assets)
directory: the SAA-C03 cheatsheet plus `PDF_Oct_16_2025/`, a per-service deck set
covering S3, VPC, IAM, EC2, RDS, Lambda and about 70 more.
