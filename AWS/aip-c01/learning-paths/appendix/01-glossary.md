# Glossary

One or two lines per term, in the sense the exam uses it, with the unit where it is taught (D1 U04 means Domain 1, unit 04) and, where one exists, the AWS documentation page that settles it (links verified against the docs in August and September 2026). Use it when a question names something you half remember; the unit has the detail.

## Amazon Bedrock and its features

| Term | What it is | Where | Docs |
|---|---|---|---|
| **Amazon Bedrock** | Managed service giving API access to foundation models from Amazon, **Anthropic**, Meta, Mistral, Cohere and others, plus **Knowledge Bases**, Agents, **Guardrails**, Evaluations and Flows; no servers to run | D1 U01 | [docs](https://docs.aws.amazon.com/bedrock/) |
| **Foundation model (FM)** | A large pre-trained model (text, image, embedding, multimodal) used through an API rather than trained by you | D1 U02 |  |
| **InvokeModel / InvokeModelWithResponseStream** | **Bedrock** runtime calls that send a provider-specific request body to one model, synchronously or as a token stream | D1 U02 | [docs](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html) |
| **Converse / ConverseStream** | **Bedrock** runtime calls with one provider-neutral JSON shape (role-based messages, system block, inference **config**, tool **config**) | D1 U03 |  |
| **Inference parameters** | **temperature** (randomness), **top-p** and **top-k** (candidate token set), maxTokens (length), **stop sequences** | D4 U02 |  |
| **Tool use (function calling)** | The model returns a structured request to run one of your tools, described by a **JSON Schema**; your code executes it | D1 U05 |  |
| **Structured output / JSON Schema** | Forcing a response into a fixed schema that downstream code validates | D3 U01 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) |
| **Prompt Management** | **Bedrock** feature that stores prompt templates with variables, variants and immutable versions; a prompt ARN can be passed as the model ID | D1 U06 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html) |
| **Bedrock Flows (Prompt Flows)** | Visual, no-code workflow builder chaining prompts, **knowledge bases**, agents, **Lambda functions** and conditions | D1 U06 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html) |
| **Knowledge Bases** | Managed **RAG**: ingest, chunk, embed, index, retrieve (Retrieve) and generate with citations (RetrieveAndGenerate) | D1 U04 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| **Chunking strategies** | Fixed-size, hierarchical (parent and child), semantic, none, or a custom **Lambda function** | D1 U05 |  |
| **Metadata filtering** | Restricting retrieval to chunks whose metadata match (department, date, access level) | D1 U04 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| **Hybrid search** | Vector similarity combined with keyword (**BM25**) scoring, normalised and weighted | D1 U05 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| **Reranker** | A model (**Amazon Rerank**, **Cohere Rerank**) that re-scores the top retrieved chunks for **relevance** | D1 U05 |  |
| **Embedding model** | Turns text or images into fixed-length vectors so meaning can be compared; **Titan Text Embeddings V2** (1,024, 512 or 256 dimensions), **Titan Multimodal**, **Cohere Embed** | D1 U05 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html) |
| **Cross-Region inference / inference profile** | Routes requests to Regions in a geography (or globally) with capacity, same model and API; geographic profiles keep data in the geography | D1 U02 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) |
| **Application inference profile** | A tagged wrapper around a model used for cost allocation per application or team | D4 U01 |  |
| **Provisioned Throughput** | Reserved capacity bought by **Model Units** (fixed size) or by **tokens per minute**, hourly, optionally committed for one or six months | D1 U02, D4 U01 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) |
| **Batch inference** | Asynchronous jobs over JSONL prompts in **S3** at a discount; no **tool use** | D1 U02 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html) |
| **Latency-optimized inference** | performanceConfig.latency = optimized; supported models served from faster infrastructure | D4 U02 |  |
| **Intelligent prompt routing** | Managed router that picks the smaller or larger model within a family per request by predicted quality | D1 U02 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) |
| **Prompt caching** | Cache checkpoints after a static prefix; cached tokens reused for later requests within minutes at a discount | D1 U02, D4 U01 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) |
| **CountTokens** | Free API returning the token count of a request for supported models before you send it | D4 U01 |  |
| **Custom Model Import** | Bring a fine-tuned open-weight model into **Bedrock** and serve it on demand | D1 U02 |  |
| **Model customisation** | **Fine-tuning** and **continued pre-training** jobs in **Bedrock** producing a custom model | D1 U02 |  |
| **Bedrock Data Automation (BDA)** | Extracts **structured output** from documents, images, audio and video with standard output and custom **blueprints**; **document splitting** for multi-document PDFs | D1 U03, D5 U03 |  |
| **Bedrock Agents (Agents Classic)** | Managed agents with **action groups**, **knowledge bases**, memory, traces, versions and aliases; now in maintenance mode, closed to new customers | D2 U01 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) |
| **AgentCore** | Runtime, Memory, Gateway, Identity, **Code Interpreter**, Browser, Observability, Evaluations and Policy for agents built with any framework | D2 U01 |  |
| **AgentCore Identity** | Inbound **JWT authorizer** (**OIDC** tokens, allowed audiences) and outbound credentials for agents | D2 U01, D3 U02 |  |
| **AgentCore Evaluations** | Built-in, third-party and **custom evaluators** that score agent traces on demand or online | D5 U01 |  |
| **Agent trace** | Step-by-step record of an agent run: pre-processing, orchestration (rationale, invocation input, observation), post-processing, guardrail and failure traces | D3 U05 |  |
| **Bedrock Guardrails** | Configurable policies applied to prompts and responses: **content filters**, **prompt attacks**, **denied topics**, **word filters**, **sensitive information filters**, **contextual grounding**, **Automated Reasoning checks** | D3 U01 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-components.html) |
| **ApplyGuardrail** | API that evaluates any text against a guardrail without invoking a model | D3 U01 |  |
| **Safeguard tiers** | Classic (English, French, Spanish) and Standard (more languages, code, **prompt leakage**; needs a cross-Region guardrail profile) | D3 U01 |  |
| **Automated Reasoning checks** | Formal-logic policy extracted from documents; findings such as VALID, INVALID, SATISFIABLE, IMPOSSIBLE | D3 U01 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-automated-reasoning-checks.html) |
| **bedrock:GuardrailIdentifier** | **IAM** condition key that denies model calls unless a specific guardrail is applied | D3 U01 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions-id.html) |
| **Model invocation logging** | Records full requests and responses for **InvokeModel** and **Converse** to **CloudWatch Logs** and/or **S3** | D3 U04 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) |
| **Bedrock Evaluations** | Automatic, **LLM-as-a-judge**, human and **RAG evaluation** jobs with managed reports | D5 U01 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) |
| **LLM-as-a-judge** | One model scores another model's responses against a **rubric**, returning a score and explanation | D5 U01 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-judge.html) |
| **Strands Agents** | Open-source AWS SDK for model-driven agents with tools as functions, **MCP** and multi-agent patterns | D2 U01 | [docs](https://strandsagents.com/) |
| **Agent Squad** | Open-source AWS Labs orchestrator routing conversations among specialised agents with a classifier and supervisor | D2 U01 | [repo](https://github.com/awslabs/agent-squad) |
| **Model Context Protocol (MCP)** | Open standard for exposing tools and data to models through **MCP servers** and clients | D1 U05, D2 U01 | [spec](https://modelcontextprotocol.io/) |
| **A2A** | Agent-to-agent protocol for agents to discover and call one another | D2 U01 |  |

## Amazon SageMaker AI

| Term | What it is | Where | Docs |
|---|---|---|---|
| **SageMaker AI** | Build, train and host your own models; endpoints, training jobs, Studio, **JumpStart** | D2 U02 |  |
| **Real-time endpoint** | Persistent instances behind an HTTPS endpoint; 6 MB payload, 60-second response | D2 U02 |  |
| **Serverless Inference** | Scales to zero, CPU only, 1 to 6 GB memory | D2 U02 |  |
| **Asynchronous Inference** | Queued requests, payloads to 1 GB, processing to one hour, results to **S3** | D2 U02 |  |
| **Batch transform** | Offline scoring of a dataset in **S3** | D2 U02 |  |
| **Inference components** | Independently scaled units (models or **LoRA** adapters) on a shared endpoint; **scale to zero** | D2 U02 |  |
| **Production variants / shadow variants** | Weighted traffic split between model versions on one endpoint; shadow copies traffic without serving | D5 U01 |  |
| **Deployment guardrails** | **Blue/green**, **canary** and linear traffic shifting with automatic rollback for endpoints (unrelated to **Bedrock Guardrails**) | D2 U02 |  |
| **LMI container / DJL Serving** | Large Model Inference containers with **vLLM** or **TensorRT-LLM** back ends: **tensor parallelism**, **continuous batching**, **quantisation** | D2 U02 | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-configuration.html) |
| **Tensor parallelism** | Splitting each model layer across several GPUs so a large model fits; degree 4 on 8 GPUs gives two replicas | D2 U02, D4 U01 | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-configuration.html) |
| **Continuous (rolling) batching** | New requests join the running GPU batch as others finish | D2 U02 |  |
| **Speculative decoding** | A small draft model proposes tokens the large model verifies, cutting latency | D2 U02 | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/model-optimize.html) |
| **Quantisation** | Storing weights or vectors with fewer bits to save memory | D1 U04, D2 U02 |  |
| **Network isolation** | Training or inference container may make no outbound network calls at all | D3 U02 |  |
| **VPC-only mode** | Studio and notebooks without direct internet access, reaching services through **VPC endpoints** | D3 U02 |  |
| **Inter-container traffic encryption** | Encrypts traffic between distributed training nodes | D3 U02 |  |
| **Inference Recommender** | Load tests and recommends instance types for endpoints | D4 U01 |  |
| **SageMaker Clarify** | Bias metrics. Pre-training: CI (class imbalance), DPL (difference in positive proportions of labels), KL, JS, LP, TVD, KS (divergence and distance measures between groups' label distributions), CDDL (conditional demographic disparity in labels). Post-training: DPPL (difference in positive proportions of predicted labels), DI (disparate impact, the ratio form of DPPL), DCAcc (difference in conditional acceptance), DCR (difference in conditional rejection), RD (recall difference), DAR (difference in acceptance rates), DRR (difference in rejection rates), AD (accuracy difference), TE (treatment equality, the difference in the ratio of false negatives to false positives), CDDPL (conditional demographic disparity in predicted labels), FT (flip test). Also **SHAP** explainability and FM evaluations; closed to new customers | D3 U05 | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-fairness-and-explainability.html) |
| **Model Monitor** | Data quality, model quality, bias drift and feature attribution drift monitors on endpoints; closed to new customers | D3 U04 |  |
| **Model Cards** | Documentation of intended use, risk rating, training and evaluation details; versioned, exportable to PDF | D3 U04 | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/model-cards.html) |
| **Model Registry** | Catalogue of model versions with approval status driving deployment pipelines | D3 U04 | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html) |
| **Model Dashboard** | Single console view of models, risk ratings, monitors and lineage | D3 U04 |  |
| **ML Lineage Tracking** | Graph of artifacts, actions and contexts recording how a model was produced | D3 U04 |  |
| **Feature Store** | Managed feature repository with online and offline stores and time-travel queries | D3 U04 |  |
| **Ground Truth** | Managed data labelling and annotation with human workforces; closed to new customers | D5 U02 |  |
| **Augmented AI (A2I)** | Human review of low-confidence predictions; closed to new customers | D2 U01 |  |
| **Data Wrangler** | Visual data preparation with data quality and insights reports | D1 U03 |  |
| **Canvas** | No-code model building and generative AI for analysts | Appendix quiz |  |
| **JumpStart** | Pre-trained models and solutions deployable in a few clicks, including **fine-tuning** recipes | D2 U02 |  |
| **SageMaker Processing job** | Managed batch compute for data processing and evaluation scripts | D4 U03 | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html) |

## Data, search and storage

| Term | What it is | Where | Docs |
|---|---|---|---|
| **Vector store** | Database indexing embeddings for nearest-neighbour search: **OpenSearch Serverless** or managed, **Aurora PostgreSQL** **pgvector**, **S3 Vectors**, **Neptune Analytics**, **MemoryDB**, **Pinecone**, **MongoDB**, **Redis** | D1 U04 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-setup.html) |
| **ANN, HNSW, IVF** | Approximate nearest-neighbour indexes; **HNSW** tuned by m, ef_construction and ef_search | D1 U04 |  |
| **Recall (retrieval)** | Share of the true nearest neighbours or relevant passages actually returned | D1 U04 |  |
| **BM25** | Classic keyword scoring algorithm used for the keyword half of **hybrid search** | D1 U05 |  |
| **Amazon OpenSearch Service / Serverless** | Search and analytics engine with k-NN vector search; **Serverless** bills by compute units | D1 U04 |  |
| **Amazon MemoryDB** | In-memory **Redis**- and **Valkey**-compatible database with vector search; **semantic caching** | D1 U04 |  |
| **Amazon S3 Vectors** | Low-cost vector storage in **S3** for infrequent queries | D1 U04 |  |
| **Amazon Kendra** | Managed enterprise search with connectors; **GenAI index** usable as a **Knowledge Base** retriever; closed to new customers | D1 U04 |  |
| **AWS Glue / Data Catalog / crawlers** | **Serverless** ETL; central metadata store of datasets populated by **crawlers** | D1 U03, D3 U04 | [docs](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html) |
| **Glue Data Quality** | Rules engine (DQDL) for data quality checks in the catalog or ETL jobs | D1 U03 |  |
| **AWS Lake Formation** | Fine-grained (column, row, cell) permissions on cataloged **S3** data, **LF-Tags**, cross-account sharing | D3 U02 | [docs](https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html) |
| **Amazon DataZone / SageMaker Unified Studio** | Data governance catalog with **OpenLineage**-compatible lineage | D3 U04 |  |
| **Amazon Athena** | **Serverless** SQL over data in **S3** | D1 U03 |  |
| **Amazon QuickSight** | **Serverless** business-intelligence dashboards and **scheduled reports** | D4 U03 |  |
| **Amazon DynamoDB / DAX** | **Serverless** key-value database; **DAX** caches reads to microseconds | D4 U02 |  |
| **Amazon ElastiCache** | In-memory cache (**Redis OSS** or **Valkey**, **Memcached**) with sub-millisecond reads | D4 U01 |  |
| **Amazon CloudFront** | Content delivery network with **edge caching** | D4 U01 |  |
| **S3 Lifecycle** | Rules that transition objects to cheaper storage classes and expire them after a set age | D3 U03 | [docs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html) |
| **S3 Object Lock** | Write-once-read-many retention (governance or compliance mode) and legal holds | D3 U03 | [docs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) |
| **S3 gateway and interface endpoints** | Private paths from a VPC to **S3** (gateway, free) and to other services through **PrivateLink** (interface) | D3 U02 |  |
| **Amazon Data Firehose** | Streaming delivery of data to **S3**, **OpenSearch** and other destinations | D4 U03 |  |
| **Amazon Kinesis Data Streams** | Real-time streaming ingestion with shards and consumers | D2 U03 |  |
| **EventBridge Pipes / Scheduler** | Point-to-point connector from a source to a target with filtering; scheduled invocations | D2 U03 | [docs](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html) |
| **AWS DMS / DataSync** | Database replication with change **data capture**; file transfer to **S3** or EFS | D1 U03 |  |
| **Amazon AppFlow** | SaaS data synchronisation (Salesforce, ServiceNow) | D2 U03 |  |

## Language, vision and other AI services

| Term | What it is | Where | Docs |
|---|---|---|---|
| **Amazon Comprehend** | NLP: entities, sentiment, key phrases, **PII** detection and redaction, **toxicity** detection, custom classifiers | D3 U01, D3 U03 | [docs](https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html) |
| **Amazon Comprehend Medical** | **PHI** detection and clinical entity extraction with ICD-10-CM, RxNorm and SNOMED CT linking | D3 U03 |  |
| **Amazon Macie** | Discovers sensitive data in **S3** and monitors bucket security posture | D3 U03 | [docs](https://docs.aws.amazon.com/macie/latest/user/what-is-macie.html) |
| **Amazon Textract** | Extracts text, forms and tables from documents | D1 U03 |  |
| **Amazon Rekognition** | Image and video analysis, including content moderation labels | D3 U01 |  |
| **Amazon Transcribe** | Speech to text with **PII** redaction and **toxicity** detection | D1 U03 | [docs](https://docs.aws.amazon.com/transcribe/latest/dg/what-is.html) |
| **Amazon Translate / Amazon Polly** | Machine translation; text to speech | D1 U03 |  |
| **Amazon Lex** | Conversational bot service with **intents**, **slots** and **synonyms** | D2 U05 |  |
| **Amazon Personalize** | Managed recommendation and ranking service | D2 U05 |  |
| **Amazon Q Business** | Managed enterprise assistant over connected data sources with permissions; closed to new customers (**Amazon Quick** is the successor) | D2 U05 |  |
| **Amazon Q Developer** | AI assistant for developers in the IDE, CLI and console; IDE plugins ending in 2027 in favour of **Kiro** | D2 U05 | [docs](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/what-is.html) |

## Security, identity and governance

| Term | What it is | Where | Docs |
|---|---|---|---|
| **IAM roles, policies, condition keys** | Identity-based permissions with temporary credentials; conditions such as aws:SourceVpce, aws:PrincipalTag, **bedrock:GuardrailIdentifier** | D3 U02 |  |
| **Permission boundary / SCP** | Cap on a role's maximum permissions; organisation-wide permission guardrail on accounts | D2 U01, D3 U04 |  |
| **ABAC** | Attribute-based access control using tags on principals and resources | D3 U02 |  |
| **IAM Identity Center** | Workforce single sign-on with **SAML 2.0** identity providers, **SCIM provisioning** and **permission sets** | D2 U03, D3 U02 |  |
| **Amazon Cognito** | **User pools** (authentication, **OIDC** and **SAML federation**, JWTs) and **identity pools** (temporary AWS credentials) | D2 U03 |  |
| **AWS STS** | Issues temporary credentials (AssumeRole and federation variants) | D3 U02 | [docs](https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html) |
| **Amazon Verified Permissions / Cedar** | Fine-grained application authorization with the **Cedar** policy language | D2 U03 |  |
| **AWS KMS** | Managed encryption keys: customer managed, AWS managed and AWS owned keys; key policies, grants, rotation | D3 U02 |  |
| **SSE-KMS / SSE-S3** | **S3** server-side encryption with **KMS** keys or **S3**-managed keys | D3 U02 |  |
| **AWS PrivateLink / VPC endpoints** | Private connectivity to AWS services from a VPC | D3 U02 | [docs](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html) |
| **AWS WAF** | Web application firewall with rate-based and managed rules in front of **API Gateway**, **CloudFront** and others | D3 U01 |  |
| **AWS CloudTrail** | API audit log; management events and opt-in data events | D3 U04 |  |
| **CloudTrail Lake** | SQL queries over **CloudTrail** events; closed to new customers | D3 U02 | [docs](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html) |
| **AWS Config** | Records resource configurations and evaluates rules | D3 U02 |  |
| **AWS Security Hub / GuardDuty / Inspector** | Central security findings and standards; threat detection; vulnerability scanning | D3 U02 |  |
| **AWS Audit Manager** | Automated evidence collection against control frameworks; GenAI best practices framework; closed to new customers | D3 U04 |  |
| **AWS Artifact** | Downloads of AWS compliance reports and agreements | D3 U04 |  |
| **AWS Organizations / Control Tower** | Multi-account management with **SCPs**; landing zone with **guardrails** | D3 U04 |  |
| **AWS Outposts / Local Zones / Wavelength** | AWS infrastructure on premises; metro edge; 5G edge (**Bedrock** runs on none of them) | D2 U03 |  |
| **OWASP Top 10 for LLM Applications** | Security risk list for LLM applications (**prompt injection**, sensitive information disclosure and others) | D3 U01 |  |
| **Responsible AI dimensions** | Fairness, explainability, privacy and security, safety, controllability, veracity and **robustness**, governance, transparency | D3 U05 |  |

## Compute, integration and operations

| Term | What it is | Where | Docs |
|---|---|---|---|
| **AWS Lambda** | **Serverless** functions; 15-minute limit, 10 GB memory, 6 MB synchronous payload, **response streaming** | D2 U04 |  |
| **Lambda function URL** | Direct HTTPS endpoint for a function | D2 U04 |  |
| **Amazon API Gateway** | Managed APIs: REST, HTTP and **WebSocket**; **request validation**, **throttling**, **usage plans**, authorizers, caching | D2 U04 | [docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html) |
| **AWS Step Functions** | **Serverless** workflow orchestration; Standard and **Express workflows**; Parallel and Map states; **wait for callback** | D2 U01 | [docs](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) |
| **Amazon EventBridge** | **Event bus** with rules, targets, Pipes and **Scheduler** | D2 U03 |  |
| **Amazon SQS / SNS** | Queues with **visibility timeouts** and **dead-letter queues**; pub/sub notifications | D2 U04 |  |
| **Amazon ECS / Fargate / App Runner** | Container orchestration; **serverless** containers; simplest managed web containers | D2 U02 |  |
| **AWS CodePipeline / CodeBuild / CodeDeploy** | CI/CD pipeline, build and test, deployment with traffic shifting and rollback | D2 U03 | [docs](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html) |
| **AWS AppConfig** | **Feature flags** and configuration delivered at runtime (successor to **CloudWatch Evidently** for experiments) | D1 U02, D4 U02 | [docs](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html) |
| **AWS CDK / CloudFormation / Service Catalog** | Infrastructure as code; curated catalogue of approved products | D1 U01 |  |
| **Amazon CloudWatch** | Metrics, logs, alarms, dashboards, **anomaly detection**, **Logs Insights**, **Synthetics canaries**, **RUM** | D4 U03 |  |
| **CloudWatch generative AI observability** | Curated views and prompt tracing for **Bedrock** and **AgentCore** workloads, **OpenTelemetry**-compatible | D4 U03 |  |
| **AWS X-Ray** | Distributed tracing with segments, **subsegments** and **annotations** | D2 U04 | [docs](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html) |
| **OpenTelemetry** | Open standard for traces and metrics instrumentation | D2 U01 |  |
| **AWS Cost Explorer / Budgets / Cost Anomaly Detection** | Cost analysis by tag, spend alerts, anomaly alerts | D4 U01 |  |
| **AWS Trainium / Inferentia** | AWS accelerator chips for training (Trn instances) and inference (Inf instances) | D2 U02 |  |
| **Circuit breaker** | Pattern that stops calling a failing dependency for a cooling-off period (closed, open, half-open) | D2 U04 |  |
| **Exponential backoff with jitter** | Retry strategy with growing, randomised delays; SDK standard and adaptive retry modes | D2 U04 | [docs](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html) |

## Evaluation and quality vocabulary

| Term | What it is | Where | Docs |
|---|---|---|---|
| **Golden dataset** | Curated prompts with verified expected outputs used for **regression tests** and **hallucination** measurement | D5 U02 | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-automatic.html) |
| **Hallucination / faithfulness** | An answer not supported by any source; **faithfulness** measures how well an answer stays within its context | D3 U01, D5 U01 |  |
| **Output diffing** | Comparing responses across runs, variants or versions to detect inconsistency and drift | D4 U03 |  |
| **Semantic drift** | Gradual change in response meaning or embedding distribution relative to a baseline | D5 U02 |  |
| **Precision@k, recall@k, MRR, nDCG** | Ranking metrics for retrieval quality | D5 U01 |  |
| **BERTScore / F1 / ROUGE** | **Reference-based** text similarity and overlap metrics | D5 U01 |  |
| **Canary, A/B, blue/green, linear, shadow** | Release and testing patterns: gradual exposure, parallel comparison, fleet switch, stepped ramp, mirrored traffic | D5 U01 |  |
| **Quality gate** | Automated pipeline check that blocks a release when metrics fall below thresholds | D5 U02 |  |
| **Time to first token, P95 latency** | Streaming responsiveness metric; latency that 95 percent of requests beat | D4 U02 |  |
| **Text unit** | **Guardrails** billing unit of up to 1,000 characters | D3 U01 |  |
| **Token** | Unit a model reads and writes, about three-quarters of an English word; the unit of **Bedrock** pricing and quotas | D4 U01 |  |

## Documentation links for exam-question patterns

The rows below come from the key-term bank built while grading Exam 1. Each names a pattern or composite concept as the questions phrase it, with the AWS documentation page that settles it; the units teach the concept under its own name.

| Term as the questions phrase it | Docs |
|---|---|
| **Converse API** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) |
| **Function calling / tool use** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) |
| **Fixed-size chunking** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking-parsing.html) |
| **Hierarchical chunking** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking-parsing.html) |
| **Semantic chunking** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking-parsing.html) |
| **No chunking / custom chunking** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking-parsing.html) |
| **Embedding model** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html) |
| **Amazon Titan Text Embeddings V2** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-titan-text-embeddings-v2.html) |
| **Reranker model / Rerank API** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html) |
| **Query expansion / decomposition** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| **Incremental ingestion** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| **LoRA / PEFT** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html) |
| **Model routing layer** | [docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html) |
| **Model selection benchmarking** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) |
| **Proof of concept (POC)** | [docs](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html) |
| **AWS Well-Architected Generative AI Lens** | [docs](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html) |
| **Multimodal prompt** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) |
| **DynamoDB as conversation memory** | [docs](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html) |
| **Bedrock agent tracing** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) |
| **Amazon Bedrock AgentCore Runtime** | [docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-service-contract.html) |
| **AgentCore SDK — @app.entrypoint** | [docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-service-contract.html) |
| **AgentCore starter toolkit** | [docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-starter-toolkit.html) [new CLI](https://github.com/aws/agentcore-cli) |
| **ReAct** | [docs](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) |
| **Circuit breaker / max iterations** | [docs](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) |
| **Tool parameter validation** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) |
| **MCP server hosting: Lambda vs ECS** | [spec](https://modelcontextprotocol.io/) |
| **Amazon SQS + dead-letter queue** | [docs](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html) |
| **Human-in-the-loop (HITL)** | [docs](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) |
| **Model cascading** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) |
| **Deployment mix (provisioned / on-demand / batch)** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) |
| **Prompt attacks filter** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-components.html) |
| **Sensitive information filters** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html) |
| **Contextual grounding check** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-contextual-grounding-check.html) |
| **ApplyGuardrail API** | [docs](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ApplyGuardrail.html) |
| **bedrock:PromptRouterArn** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) |
| **Defense in depth** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) |
| **Adversarial testing / red teaming** | [docs](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html) |
| **AWS IAM Identity Center + SAML federation** | [docs](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html) |
| **Amazon Cognito + OIDC** | [docs](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html) |
| **Throttling / ThrottlingException (HTTP 429)** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) |
| **Request batching / rolling (continuous) batching** | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-configuration.html) |
| **Concurrent invocation management** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html) |
| **Max sequence length** | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-configuration.html) |
| **Semantic caching** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) |
| **Context pruning** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) |
| **Max output tokens** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) |
| **Model tiering with a query classifier** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) |
| **Serverless multimodal analysis pipeline** | [docs](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) |
| **RAG / Knowledge Base evaluation** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html) |
| **Quality gates** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html) |
| **Retrieval quality testing** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation-kb.html) |
| **Knowledge Base logging** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-bases-logging.html) |
| **CloudWatch Logs Insights** | [docs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html) |
| **User feedback loop** | [docs](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html) |
