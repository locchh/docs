# Unit 06: Domain 3 review

Decision tables for the recurring Domain 3 choices, the vocabulary that gives answers away, a one-page summary, and the mixed quiz of questions not used in units 01 to 05.

## Decision tables

**Which guardrail policy?**

| Requirement wording | Answer |
|---|---|
| Hate, insults, sexual, violent or criminal content in prompts or responses | **Content filters** (strength per category, input and output) |
| Jailbreak, prompt injection, "ignore previous instructions", system-prompt extraction | **Prompt attack filter** (input only, input tags with `InvokeModel`; leakage needs **Standard tier**) |
| A subject the assistant must not discuss | **Denied topics** (definition plus sample phrases, up to 30) |
| Specific words, competitor names, profanity | **Word filters** (exact match, managed profanity list, 10,000 custom items) |
| PII or custom identifiers to block or mask | **Sensitive information filters** (built-in types plus regex; mask to keep utility) |
| Answer must be supported by the retrieved passages and answer the question | **Contextual grounding check** (grounding and relevance thresholds) |
| Answer must comply with written business or regulatory rules, provably | **Automated Reasoning checks** (policy from documents, detect mode, English, no streaming) |
| Multilingual, code, stronger prompt-attack accuracy | **Standard tier** with a **guardrail profile** (cross-Region) |
| Tune before enforcing | **Detect mode** (`NONE` action) with trace |
| Same policies on non-**Bedrock** text (**SageMaker** output, **Kendra** results, user input before retrieval) | `ApplyGuardrail` API |
| Which policy blocked a request, in real time | Trace enabled plus `InvocationsIntervened` by `GuardrailPolicyType` |
| Make guardrails mandatory for every caller | **IAM** `bedrock:GuardrailIdentifier` condition key on all roles |

**Which detection service?**

| Requirement wording | Answer |
|---|---|
| Toxicity in text with confidence scores, managed | **Amazon Comprehend** toxicity detection (`DetectToxicContent`) |
| PII locations (offsets) in text | **Comprehend** `DetectPiiEntities` / offsets mode |
| Which PII types a document contains (labels) | **Comprehend** `ContainsPiiEntities` / labels mode |
| Redact PII across an **S3** corpus | **Comprehend** asynchronous redaction job (mask or entity-type replacement) |
| PHI, medical entities, ICD-10-CM or RxNorm codes | Amazon **Comprehend Medical** |
| Organisation-specific sensitive terms | **Comprehend** custom entity recognition (a trained model) |
| Where sensitive data sits in **S3**, bucket posture | **Amazon Macie** |
| Redact PII inside an ETL job | **AWS Glue** sensitive-data detection transform |
| Unsafe images or video | **Amazon Rekognition** moderation labels; **Guardrails** image content filters for **Bedrock** |
| Custom threat classifier on red-team samples | **SageMaker**-hosted classifier (only when managed options are excluded) |

**Which network and identity control?**

| Requirement wording | Answer |
|---|---|
| No internet, traffic stays on the AWS network | Private subnets plus **VPC interface endpoints** (**PrivateLink**) and an **S3 gateway endpoint**; no NAT, proxy, VPN or peering |
| Restrict who uses a **VPC** endpoint | **Endpoint policy** (principals and actions) plus **security group** (sources) |
| Container may make no outbound call at all | **SageMaker** **network isolation** |
| Encrypt traffic between distributed training nodes | **Inter-container traffic encryption** |
| Least privilege for a notebook on two buckets | **IAM** policy on the execution role scoped to those bucket ARNs |
| Each user only their own notebook instance | Per-user **IAM** policy on the instance ARN |
| Workforce SSO from Entra ID or Okta, permission sets | **IAM Identity Center** (**SAML 2.0** plus **SCIM**); direct **SAML** to **IAM** roles as the alternative |
| Application or partner users, temporary AWS credentials | **Amazon Cognito** (user pool with **OIDC** federation, identity pool for credentials) |
| Agent must validate **OIDC** tokens and audience | **AgentCore Identity** inbound authorizer with allowed audience |
| Column- and row-level access to cataloged **S3** data, central audit | **AWS Lake Formation** |
| Keys the company owns and controls | **KMS** customer managed keys (SSE-**KMS**) |
| Keep FM inference in a geography | Geographic cross-Region inference profile; **SCPs** to deny other Regions |
| Regulated data may not leave the country at all | **Outposts** for local preprocessing, sanitised data to **Bedrock** in Region |

**Which governance artefact?**

| Requirement wording | Answer |
|---|---|
| Document intended use, limitations, risk rating, evaluation results | **SageMaker Model Cards** (programmatic, versioned, PDF export) |
| Approve or reject model versions before deployment | **SageMaker Model Registry** status |
| Register datasets, schema and metadata | **AWS Glue Data Catalog** (crawlers) |
| Lineage of datasets, jobs, models and endpoints | **SageMaker ML Lineage Tracking**; **DataZone** or **Unified Studio** lineage for **Glue** and Redshift |
| Attribute generated content to its sources | Tag outputs with source, prompt version and model metadata; keep knowledge-base citations |
| Reproduce training data as it was | **S3 Versioning** or **Feature Store** time travel |
| Who called which API | **CloudTrail** (data events for agents, knowledge bases, flows, prompts) |
| What was sent and returned to the model | **Bedrock** model invocation logging |
| Why the application decided | Structured **CloudWatch Logs** decision logs with **Logs Insights** |
| Evidence against a GenAI best-practices framework | **AWS Audit Manager** (closed to new customers) |
| AWS's own compliance reports | **AWS Artifact** |
| Organisation-wide guardrails on accounts | **SCPs** and **Control Tower**; tag policies |

**Which monitoring and remediation tool?**

| Requirement wording | Answer |
|---|---|
| Bias drift in a deployed **SageMaker** model | **Model Monitor** bias drift (**Clarify**), **CloudWatch** alarms |
| Dataset bias, model bias, feature attributions | **SageMaker** **Clarify** pre- and post-training metrics and **SHAP** |
| Bias in FM outputs at scale, low code | **Bedrock** **LLM-as-a-judge** evaluations, **Prompt Management** variants and **Flows** for A/B tests, **CloudWatch** fairness metrics |
| Confidence or uncertainty metrics collected and charted | **CloudWatch** custom metrics in an application namespace |
| Reasoning steps and retrieval visibility for an agent | **Bedrock** agent tracing (**AgentCore** Observability for new agents) |
| Unusual usage patterns, possible misuse | **CloudWatch** anomaly detection, guardrail intervention rates, **GuardDuty** |
| Violation detected, fix without a person | **EventBridge** rule to **Lambda** or **Step Functions**: rollback, traffic shift, disable, notify |


## Words that give the answer away

- "Prohibited topics", "must not discuss" → **denied topics**. "Specific terms", "competitor names" → **word filters**. "PII", "mask", "anonymise" → **sensitive information filters**. "Grounded", "hallucination", "supported by sources" → **contextual grounding**. "Provably", "policy rules", "logical" → **Automated Reasoning**.
- "Which guardrail policy", "granular", "real time" → trace plus `GuardrailPolicyType`. "Input or output triggered" → `GuardrailContentSource`.
- "All InvokeModel and Converse calls", "every team", "no new infrastructure" → the **IAM** condition `bedrock:GuardrailIdentifier`. A `PromptRouterArn` condition in the same option is the distractor.
- "Custom business rules", "escalate for review", "moderation workflow" → **Step Functions** plus **Lambda** around the guardrail.
- "Toxicity", "harassment", "confidence scores", "managed" → **Comprehend** toxicity detection. "Sentiment" is never the toxicity answer.
- "Character offsets" → offsets mode. "Entity labels" → labels mode.
- "PHI", "dosage", "diagnoses", "HIPAA" → **Comprehend Medical** beside **Comprehend**.
- "Must not appear in search results" → redact before indexing with **Comprehend**, then the search or knowledge base.
- "Deleted after N hours or days", "retention" → **S3 Lifecycle** expiration. "Immutable", "WORM", "cannot be deleted" → **S3 Object Lock**.
- "No internet", "no public IPs", "stay within the AWS network", "no NAT or proxy" → **VPC endpoints**. "Peering", "internet gateway", "NAT gateway", "proxy fleet" → wrong.
- "Existing identity provider", "no long-lived credentials", "audit logs" → **Identity Center** for workforce, or **Cognito** for applications. "**IAM** users", "Secrets Manager rotation", "**Lambda** authorizer against LDAP", "custom JWTs" → wrong.
- "Column-level", "per study team", "no per-group bucket policies" → **Lake Formation**.
- "Company-owned keys" → customer managed **KMS** keys.
- "Cannot leave the jurisdiction" → **Outposts** preprocessing. Anything that uploads first is wrong.
- "Model cards", "lineage", "attribution", "decision logs", "minimal manual effort" → programmatic **Model Cards**, **Glue**, tags, **CloudWatch Logs**.
- "Source lineage for reviewers, least overhead" → tag outputs with source metadata and register datasets in the **Data Catalog**.
- "Bias drift" → **Model Monitor** with **Clarify**. "Explainability reports" → **Clarify** **SHAP**.
- "Reasoning traces", "retrieval steps", "confidence metrics", "source attribution", "minimal custom code" → agent tracing plus **CloudWatch** plus UI displays.
- "Fairness over time", "controlled test groups", "automatically score" → **Flows** A/B tests, **CloudWatch** metrics, **LLM-as-a-judge**.
- "Nightly batch", "weekly manual review", "sample of responses", "EC2 microservice", "custom validation containers" → always the distractor.

## Domain 3 on one page

**Safety is layered.** Reading from the client inward:

- **WAF** and **API Gateway** validation at the edge.
- A **Comprehend** pre-filter and **Lambda** sanitisation.
- **Bedrock Guardrails** at the model, with content, prompt-attack, topic, word, sensitive-information, grounding and **Automated Reasoning** policies, in block, mask or detect mode, **Classic** or **Standard** tier, versioned and applied through `guardrailConfig` or `ApplyGuardrail`.
- **Lambda** post-processing and **API Gateway** response filtering.
- **CloudWatch** metrics by policy type, and traces to explain interventions.
- **IAM**'s guardrail-identifier condition to make it all mandatory.

Three problems have their own answers. Hallucinations are reduced by grounding in a knowledge base with citations, grounding checks or similarity-based confidence scores, and **JSON Schema** structure. Adversarial prompts are met with sanitisation, prompt-attack and classifier detection, least agency and automated adversarial testing. Toxicity is caught by **Comprehend** toxicity detection, and **Rekognition** for images.

**Security is the classic AWS stack.**

- Network: private subnets with interface endpoints for **Bedrock**, **SageMaker** and friends and a gateway endpoint for **S3**, endpoint policies and security groups, **SageMaker** **VPC-only mode**, **network isolation** and inter-container encryption.
- Identity: **IAM** roles scoped to ARNs and conditions, **Identity Center** for workforce SSO and **Cognito** for application users, **AgentCore Identity** for agents, and **Lake Formation** for fine-grained data access.
- Keys: customer managed **KMS** keys on data, models, agents, knowledge bases and guardrails.
- Visibility: **CloudTrail**, **CloudWatch** and the security services.

**Bedrock** itself never trains on your data, never shares it with providers, and retains nothing by default.

**Privacy runs through the pipeline.** **Macie** finds sensitive data in **S3**, **Glue** redacts it in ETL, **Comprehend** detects PII as offsets or labels and redacts it, and **Comprehend Medical** handles PHI while keeping clinical meaning. **Lambda** applies masking, tokenisation, pseudonymisation, generalisation, **k-anonymity** or **differential privacy**, and guardrails mask PII on input and output. Redaction happens before anything is indexed for search, **S3 Lifecycle** rules expire transient data, **Object Lock** makes audit records immutable, and data protection policies keep PII out of logs.

**Governance produces evidence automatically.**

- Documentation: **SageMaker Model Cards**.
- Provenance: the **Glue Data Catalog**, **DataZone** lineage and **SageMaker Lineage Tracking**.
- Attribution: tags on resources, objects and generated outputs.
- Audit trail: structured **CloudWatch Logs**, invocation logging and **CloudTrail**.
- Organisational control: **SCPs**, **Control Tower**, **IAM** conditions, approval workflows and the **Model Registry**.
- Residency: **Outposts** and geographic profiles.
- Remediation: **Model Monitor** with **Clarify**, **CloudWatch** anomaly detection and scheduled evaluations, feeding **EventBridge**-driven remediation.

**Responsible AI ties them together.** Transparency comes through agent traces, citations, reasoning displays and **CloudWatch** confidence metrics. Fairness comes through **Clarify** metrics for hosted models, and **LLM-as-a-judge**, **Prompt Management** and **Flows** A/B tests and **CloudWatch** fairness metrics for FM applications. Policy compliance comes through guardrails encoded from policy, model cards for limitations, **Lambda** compliance checks and continuous monitoring. And humans stay in the loop where the stakes are high.

## Mixed quiz

<!-- KC: REVIEW -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 28

A company is implementing new AI governance policies requiring that all foundation model (FM) interactions use Amazon Bedrock guardrails. The engineering team has configured the guardrails and must now ensure that every InvokeModel and Converse API call applies them automatically across all teams and applications. The solution must enforce compliance with minimal operational overhead and without introducing additional infrastructure.

Which solution will enforce guardrail compliance for the API calls in the MOST operationally efficient way?

- **A)** Configure IAM policies for the InvokeModel and Converse API calls with the `bedrock:GuardrailIdentifier` condition key. Apply the policies to all IAM roles that access the Amazon Bedrock FMs.
- **B)** Store guardrail identifiers in AWS Systems Manager Parameter Store. Create an AWS Lambda function that retrieves the guardrail identifier from Parameter Store each time before making calls to Amazon Bedrock FMs.
- **C)** Configure IAM policies for the InvokeModel and Converse API calls with both `bedrock:GuardrailIdentifier` and `bedrock:PromptRouterArn` condition keys. Apply the policies to all IAM roles. Require prompt router validation before allowing access to Amazon Bedrock FMs.
- **D)** Create an AWS Lambda function that validates and enforces guardrails before proxying requests to Amazon Bedrock. Use the Lambda function as the exclusive endpoint for all FM interactions.

<details><summary>Answer</summary>

**Answer: A.** IAM policies with the bedrock:GuardrailIdentifier condition key on InvokeModel and Converse, applied to all roles that access Bedrock FMs, deny any call that does not name the required guardrail and enforce compliance with no additional infrastructure. The ExamPro key chooses the option that also requires the bedrock:PromptRouterArn condition, but requiring a prompt router is unrelated to guardrail compliance and would break callers that do not use routing; the official AWS practice question with the same wording keys the guardrail-identifier-only option. Parameter Store lookups and a Lambda proxy add infrastructure and can be bypassed.

*Where this is covered: Unit 01, Amazon Bedrock Guardrails: the managed safety layer. Key: ours, confidence high. (Source file key: C.)*

</details>

### 2. Exam 2, question 65

A regional insurance provider is building a customer-support chatbot that uses Amazon Bedrock to answer questions based on historical communication records. The company has thousands of customer-service transcripts stored in Amazon S3. These transcripts contain sensitive PII—including policy numbers, addresses, and phone numbers—that must never appear in search results or downstream model responses. The company needs an automated and scalable solution to preprocess all records before they are indexed for retrieval. The solution must support natural language search and integrate easily with Bedrock-powered applications.

Which solution will meet these requirements with the most secure and scalable design?

- **A)** Use Amazon Textract to extract text from transcript files and Amazon Macie to identify PII. Integrate the text output directly into Amazon OpenSearch Service for retrieval.
- **B)** Use an Amazon Bedrock FM and a system prompt to instruct the model to avoid exposing PII at query time while performing search over the full transcripts.
- **C)** Use Amazon Comprehend to detect and redact PII from the transcripts stored in Amazon S3. Integrate the processed data with Amazon Kendra to provide enterprise search and natural language support.
- **D)** Use AWS Lambda to retrieve raw transcripts, manually parse them for common PII patterns with regex, and index the cleaned text into an Amazon RDS database for keyword search.

<details><summary>Answer</summary>

**Answer: C.** Running Amazon Comprehend PII detection and redaction over the transcripts in S3 removes policy numbers, addresses and phone numbers before indexing, and Amazon Kendra then provides natural-language enterprise search over the redacted data that integrates with Bedrock applications, so PII cannot surface in results or responses. Macie identifies PII but does not redact it before OpenSearch indexes the raw text, a system prompt at query time is not a reliable control and leaves the PII searchable, and hand-written regex in Lambda with RDS keyword search is fragile and loses natural-language search.

*Where this is covered: Unit 03, Privacy for search and retrieval. Key: ours, confidence high.*

</details>

### 3. Exam 3, question 14

A global insurance provider is developing a claims-analysis assistant using Amazon Bedrock to help employees summarize claim notes, extract key details, and generate customer responses. During testing, the team discovers that malicious users occasionally modify input text to inject harmful instructions and cause the FM to produce unauthorized financial recommendations. Additionally, compliance officers require a secondary safeguard to validate all FM outputs before they reach end users, ensuring the system cannot accidentally produce disallowed advice or internal policy violations.

The company must design a defense-in-depth safety system that prevents misuse through multiple independent safety layers. The solution must include pre-processing checks, model-based protections, and post-processing filtering, while minimizing long-term operational overhead and avoiding custom model training.

Which solution will provide the MOST comprehensive, multi-layer protection against FM misuse?

- **A)** Use a single Lambda function that validates user input, invokes the Bedrock model directly, evaluates the output using regex-based filtering, and logs any flagged responses to CloudWatch Logs.
- **B)** Implement an API Gateway → Lambda → Bedrock Guardrails → Lambda pipeline where API Gateway performs schema validation, a pre-processing Lambda uses Amazon Comprehend to detect harmful or adversarial content, Bedrock Guardrails filter unsafe prompts and responses, and a final Lambda runs policy-validation checks before returning output.
- **C)** Deploy an Amazon SageMaker model to classify all prompts and responses. Route allowed requests to the FM and block requests that exceed a preset safety risk threshold.
- **D)** Inject strict prompt instructions that prevent policy-violating outputs and configure low-temperature inference on the FM to minimize unpredictable behavior.

<details><summary>Answer</summary>

**Answer: B.** An API Gateway to Lambda to Bedrock Guardrails to Lambda pipeline gives independent layers: schema validation at API Gateway, a pre-processing Lambda function using Amazon Comprehend to detect harmful or adversarial content, Bedrock Guardrails filtering unsafe prompts and responses, and a final Lambda function running policy validation before output, all managed and without custom model training. A single Lambda with regex filtering is one layer, a SageMaker classifier requires custom training and is also one layer, and strict prompt instructions with low temperature are not safety controls.

*Where this is covered: Unit 01, Defense in depth, assembled. Key: ours, confidence high.*

</details>

### 4. Exam 3, question 17

A global wealth-management company is deploying a regulated generative AI environment that uses Amazon SageMaker AI for training proprietary financial-risk models and Amazon Polly to generate compliance-approved voice narratives from investment summaries. To comply with strict data-sovereignty and security controls, the cloud governance office requires that all SageMaker notebook instances operate without internet access and that all traffic to AWS services must stay entirely within the corporate private network. The solution must not introduce proxies, NAT gateways, or any component that allows outbound internet connectivity.

Which configuration will ensure full compliance while maintaining SageMaker notebook functionality?

- **A)** Deploy a Site-to-Site VPN between the notebooks and AWS service endpoints to avoid public internet usage.
- **B)** Configure an internal proxy fleet inside the corporate VPC and route all notebook traffic through it before reaching AWS services.
- **C)** Establish Amazon SageMaker VPC interface endpoints for all required SageMaker and AWS service APIs inside the corporate VPC to keep notebooks fully private.
- **D)** Provision a NAT gateway inside the private subnets so the notebook instances can access AWS services without exposing public IPs.

<details><summary>Answer</summary>

**Answer: C.** SageMaker notebook instances in the corporate VPC with interface VPC endpoints for the SageMaker APIs and every other AWS service they call (Polly, S3 through a gateway endpoint) keep all traffic on the private AWS network with no internet access and full notebook functionality. A Site-to-Site VPN connects networks rather than reaching AWS service endpoints privately, an internal proxy fleet is explicitly excluded and still needs an internet path, and a NAT gateway provides exactly the outbound internet connectivity the governance office forbids.

*Where this is covered: Unit 02, Network isolation. Key: ours, confidence high.*

</details>

### 5. Exam 3, question 58

A GenAI developer is building a generative AI platform using Amazon Bedrock and Amazon SageMaker AI to enable both internal teams and external partners to access and utilize large language models and AI services. The goal is to integrate the solution with the current identity provider (IdP) to enable secure user authentication. Additionally, it must provide temporary access to users for Bedrock and SageMaker AI, eliminating the need for long-lived credentials, while maintaining detailed audit logs of user activity to meet compliance requirements.

Which of the following should be implemented? (Select TWO.)

- **A)** Utilize AWS IAM Identity Center with SAML-based federation to integrate the IdP, and configure it to grant users access to Bedrock and SageMaker AI using customized permission sets.
- **B)** Set up an API Gateway with an AWS Lambda authorizer that verifies user credentials against the Lightweight Directory Access Protocol (LDAP) system and issues JSON Web Tokens (JWTs) for accessing Bedrock and SageMaker AI.
- **C)** Configure AWS Lambda to authenticate users directly against the IdP and then issue temporary access tokens for Bedrock and SageMaker AI.
- **D)** Configure Amazon Cognito to integrate with the current IdP via OpenID Connect (OIDC) and enable it to authenticate users, exchange tokens for temporary AWS credentials, and provide access to Bedrock and SageMaker AI.
- **E)** Use AWS Organizations to set up cross-account access and manage permissions for users accessing Bedrock and SageMaker AI through IAM roles.

<details><summary>Answer</summary>

**Answer: A, D.** IAM Identity Center with SAML-based federation to the IdP and customised permission sets gives internal users temporary, role-based access to Bedrock and SageMaker with CloudTrail auditing, and Amazon Cognito federating to the IdP over OIDC exchanges tokens for temporary AWS credentials for external partners and application users. A Lambda authorizer validating LDAP credentials and issuing JWTs is custom, unaudited code whose tokens cannot call AWS APIs, a Lambda function issuing its own access tokens is the same problem, and Organizations cross-account roles address account structure rather than identity provider integration.

*Where this is covered: Unit 02, Identity: who may call the model and read the data. Key: ours, confidence high.*

</details>

### 6. Exam 3, question 67

A multinational insurance provider is deploying an enterprise-wide generative AI platform built on Amazon Bedrock and Amazon SageMaker AI. The platform generates policy summaries, assists with claim reviews, and provides underwriting insights. Because the system processes regulated financial and personal data, the compliance office requires a framework that documents model behavior, tracks all data sources used during training, and provides auditable reasoning traces for every generated output. Additionally, auditors must be able to review historical versions of the models, including the datasets, parameters, and decision logs associated with each output.

The engineering team needs a solution that minimizes manual documentation effort, automatically captures data lineage, and ensures end-to-end traceability across all AI workflows.

Which solution BEST meets these requirements?

- **A)** Use Amazon Bedrock Guardrails to create compliance summaries, store model version metadata in Amazon S3, and configure VPC Flow Logs to capture model interaction history.
- **B)** Generate programmatic model cards with SageMaker AI, use AWS Glue to capture and track data lineage for all training sources, apply metadata tags for source attribution, and stream detailed decision logs to CloudWatch Logs for compliance review.
- **C)** Configure AWS Config rules to detect changes to AI resources and export configuration snapshots to an audit S3 bucket, using these snapshots to document model provenance.
- **D)** Store all training datasets and model artifacts in Amazon S3 with versioning enabled, and use Amazon Athena queries to manually reconstruct model lineage for compliance audits.

<details><summary>Answer</summary>

**Answer: B.** Programmatic SageMaker model cards document model behaviour and versions with minimal manual effort, AWS Glue captures and tracks data lineage for all training sources, metadata tags attribute every source, and streaming detailed decision logs to CloudWatch Logs gives auditors the reasoning trail for each output, together delivering automated end-to-end traceability. Guardrails do not create compliance summaries and VPC Flow Logs record network flows rather than model interactions, Config snapshots track resource configuration rather than model provenance, and S3 versioning with manual Athena reconstruction is the manual effort the team must avoid.

*Where this is covered: Unit 04, Tracking data lineage and source attribution. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## What to do next

Move to Domain 4 (`../04-operational-efficiency-optimization/`), which turns from protecting the system to running it well: cost, latency, throughput and the monitoring that keeps them in bounds. The safety and governance vocabulary from this domain reappears there as the constraints that optimisation must respect.
