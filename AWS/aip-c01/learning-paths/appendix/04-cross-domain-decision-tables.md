# Cross-domain decision tables

Each domain review has its own tables. This page collects the choices that cut across domains, the ones the exam mixes into a single scenario, and the reading rules that decide most questions.

## How to read a question

1. Find the **constraint words** first: "least operational overhead", "most cost-effective", "minimal custom code", "no long-lived credentials", "must not leave the Region", "near real time", "hours of delay acceptable". They eliminate half the options before you read them.
2. Find the **service that already does it**. The keyed answer is almost always the managed AWS feature whose description matches the wording (**Knowledge Bases** for **RAG**, **Guardrails** for safety, **Bedrock Evaluations** for evaluation, **cross-Region inference** for **throttling**, **Identity Center** for workforce SSO).
3. Discard options that are **manual** (weekly review, spreadsheets, wiki), **custom builds** of an existing feature (a **Lambda** proxy that re-implements **guardrails**, a **Kinesis**-**Athena** **A/B** engine), or a **real service used for the wrong job** (**Macie** on live prompts, **CloudTrail** as a content filter, **Object Lock** as an output safety control).
4. For "Select TWO" or "THREE", the correct options are usually the ones that address *different* requirements in the stem; two options that solve the same requirement are a hint that one is a distractor.

## Which Bedrock feature?

| You need to | Feature |
|---|---|
| Answer from your documents with citations | **Knowledge Bases** (RetrieveAndGenerate) |
| Let the model call tools and act | Agents (Classic) or **AgentCore** with **Strands Agents**; **MCP** for tools |
| Chain prompts and conditions without code | **Bedrock Flows** |
| Version and reuse prompts | **Prompt Management** |
| Filter harmful, off-topic or sensitive content, check grounding | **Guardrails** (and **ApplyGuardrail** for any text) |
| Measure quality, bias, **robustness**, **toxicity** | **Bedrock Evaluations** (automatic, judge, human, **RAG**) |
| Survive **throttling** with the same model and API | **Cross-Region inference** |
| Guarantee steady high throughput | **Provisioned Throughput** |
| Process a large offline job cheaply | **Batch inference** |
| Cut cost when most queries are simple | **Intelligent prompt routing** or a classifier routing to tiers |
| Reuse a long static prefix | **Prompt caching** |
| Attribute cost per application | **Application inference profiles** with tags |
| Extract structure from documents, images, audio, video | **Bedrock Data Automation** |
| Fine-tune or import a model | **Model customisation**; **Custom Model Import** |

## Which compute for the application and the model?

| Situation | Answer |
|---|---|
| **Bedrock** model, spiky or low traffic | **Lambda** calling **Bedrock** on demand |
| **Bedrock** model, steady latency-critical volume | **Provisioned Throughput** |
| Your own model, GPUs, interactive | **SageMaker** **real-time endpoint** (6 MB, 60 s) |
| Your own model, large inputs or minutes of work | **SageMaker Asynchronous Inference** (1 GB, 1 hour) |
| Small CPU model, intermittent | **SageMaker Serverless Inference** |
| Many adapters or models sharing GPUs | **SageMaker** **inference components** |
| Long-lived connections, WebSockets | **ECS** on **Fargate** |
| On-site inference with poor connectivity | **IoT Greengrass** |
| Regulated data that cannot leave the country | **Outposts** for preprocessing, sanitised data to **Bedrock** |

## Which identity and access control?

| Situation | Answer |
|---|---|
| Employees, corporate IdP, **permission sets** | **IAM Identity Center** (**SAML 2.0** plus **SCIM**) |
| Application or partner users, temporary AWS credentials | **Amazon Cognito** (**OIDC** federation, **identity pools**) |
| Agent must validate inbound **OIDC** tokens | **AgentCore Identity** |
| Fine-grained application authorization | **Amazon Verified Permissions** (**Cedar**) |
| Column- and row-level data access | **Lake Formation** |
| Make a guardrail mandatory | **IAM** condition **bedrock:GuardrailIdentifier** |
| Organisation-wide limits (Regions, models) | **Service control policies** |
| Keys the company controls | **KMS** **customer managed keys** |

## Which privacy control?

| Situation | Answer |
|---|---|
| Find sensitive data in **S3** | **Macie** |
| Detect or redact **PII** in text | **Comprehend** (offsets, labels, redaction jobs) |
| **PHI** and clinical entities | **Comprehend Medical** |
| Redact during ETL | **Glue** sensitive-data transform |
| Mask **PII** on the way into and out of the model | **Guardrails** **sensitive information filters** |
| Keep **PII** out of search results | Redact before indexing |
| Delete transient data after N days | **S3 Lifecycle** expiration |
| Immutable audit records | **S3 Object Lock** |
| Mask **PII** in logs | **CloudWatch Logs** **data protection policies** |

## Which log or metric answers the question?

| Question | Answer |
|---|---|
| Who called which API, when, from where | **CloudTrail** |
| What was sent to and returned by the model | **Bedrock** **model invocation logging** |
| Why did the application decide that | Structured **CloudWatch Logs** with **Logs Insights** |
| Which guardrail policy intervened | **Guardrail trace** plus InvocationsIntervened by GuardrailPolicyType |
| Why did the agent choose that tool | **Agent trace** (or **AgentCore Observability**) |
| Which documents failed ingestion | **Knowledge base logging** to **CloudWatch Logs** |
| Where is the latency | **X-Ray** traces |
| Are tokens or spend abnormal | **CloudWatch anomaly detection**; **Cost Anomaly Detection** |
| Business impact | Custom **CloudWatch** metrics and **QuickSight** dashboards |

## Which evaluation or test?

| Goal | Answer |
|---|---|
| Compare models, prompts or parameters offline | **Bedrock Evaluations** (managed reports) |
| Judge **correctness**, **faithfulness**, tone, safety at scale | **LLM-as-a-judge** (built-in or **custom metrics**) |
| Evaluate retrieval and grounding | **RAG evaluation** jobs; labelled retrieval datasets with ranking metrics |
| Evaluate agents | **AgentCore Evaluations** on traces |
| Choose among variants on live users | **A/B testing** (**SageMaker** **production variants**, **feature flags**) |
| Release one version safely | **Canary**, then linear or **blue/green**, with rollback |
| **Catch** regressions before release | **Golden dataset** evaluations as CI/CD **quality gates** |
| Detect drift during rollout of a hosted model | **Model Monitor** on a **shadow deployment** |
| Measure fairness | **Clarify** metrics (hosted models); judge scores per group plus **CloudWatch** (FM applications) |

## Words that are almost always the distractor

Watch for an option that mismatches the requirement:

- Manual review, weekly sampling, spreadsheets or wikis.
- A nightly batch when the requirement is real time.
- A bigger model or a bigger **context window** when the requirement is cost.
- Lower **temperature** when the requirement is safety.
- **CloudTrail** as a content or quality control.
- **Macie** on live traffic.
- **Object Lock** as a safety control.
- **Global Accelerator** for **Bedrock** **throttling**.
- VPC peering, NAT gateways, proxies or internet gateways when the requirement is "no internet".
- **IAM** users with rotated keys or **Lambda** authorizers issuing custom JWTs when the requirement is federation.
- A prompt router condition when the requirement is **guardrail enforcement**.
