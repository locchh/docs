# Unit 07: Domain 1 review

This unit closes Domain 1. It has three parts:

- The decision tables that most Domain 1 questions reduce to.
- A one-page summary you can reread the night before.
- A mixed quiz of the Domain 1 questions that did not fit an earlier unit.

## Decision tables

**Where should the knowledge live?**

| Requirement wording | Answer |
|---|---|
| Managed **RAG**, least ops, native **Bedrock**, citations | **Bedrock Knowledge Bases** (quick-created **OpenSearch Serverless**) |
| Control over index, **hybrid search**, sharding, very large scale | **Amazon OpenSearch Service**, or **OpenSearch Serverless** for no infrastructure |
| Vectors next to relational data, SQL filters, tenant isolation | **Aurora PostgreSQL** with **pgvector** |
| Tens of millions of vectors, infrequent queries, lowest cost | **Amazon S3 Vectors** |
| Lowest latency, semantic cache for near-duplicate questions | **Amazon MemoryDB** |
| Relationships between entities matter (**GraphRAG**) | **Amazon Neptune Analytics** |
| Enterprise connectors, ACL-aware search, existing investment | **Amazon Kendra** (**GenAI index** as a KB retriever) |
| Metadata, checksums, sessions | **DynamoDB** beside the vector index, never as the index |

**How should the model get its capacity?**

| Requirement wording | Answer |
|---|---|
| Variable traffic, PoC, pay as you go | **On-demand** |
| Throttled at peaks, keep the same model and API, cheapest fix | **Cross-Region inference** profile (geographic for residency, global for cost) |
| Steady high volume, predictable throughput, customised model | **Provisioned Throughput** (**Model Units**, no or 1- or 6-month commitment) |
| Bulk offline jobs, hours of delay acceptable | **Batch inference** (**JSONL** in **S3**, discounted) |
| Fastest time to first token for interactive use | **Latency-optimized inference** |
| Mixed simple and complex prompts, cut cost, keep quality, minimal ops | **Intelligent prompt routing** within a model family |

**Which chunking strategy?**

| Content | Strategy |
|---|---|
| Uniform documents, simple needs | **Fixed-size** with overlap (default about 300 tokens) |
| Long manuals with sections and sub-sections, section-level updates | **Hierarchical** (child chunks for precision, parents for context) |
| Explanations and procedures that must stay whole, fragmented today | **Semantic** |
| Already split into small files (FAQs) | No chunking |
| Structure-aware splitting the built-ins cannot do | **Custom Lambda transformation** |

**Prompt, RAG or fine-tune?**

| Symptom | Fix |
|---|---|
| Wrong or outdated facts, needs citations | **RAG** with **Knowledge Bases** |
| Inconsistent tone, style or format despite good prompts | **Fine-tuning** (**Bedrock customization** or **SageMaker** with **LoRA**) |
| Reasoning steps vary, fields missing, format drifts | Prompt engineering: structured inputs, output schema, **chain-of-thought**, feedback loops |
| Same static preamble sent every time, rising cost and latency | **Prompt caching** |
| Must never discuss a topic or leak PII | **Guardrails**, not prompt wording |

**Which orchestrator?**

| Requirement wording | Answer |
|---|---|
| Sequential prompt chains, branching on model output, reusable prompt components, pre/post-processing | **Bedrock Flows** |
| Multi-step workflow with retries, circuit breaker, human wait, many AWS integrations | **Step Functions** |
| Model decides which tools to call | **Bedrock Agents**, now **Agents Classic** (**AgentCore** for new, framework-agnostic agents) |
| Add GenAI to a legacy app without coupling | **EventBridge** rules → **Lambda** → **Bedrock** |
| Long jobs, users can wait, cost matters | **SQS** → **Lambda** → **Bedrock**, or **batch inference** |
| Real-time streamed suggestions in a browser | **API Gateway** **WebSocket API** + **Lambda** + **Bedrock** streaming |

**Which validation tool?**

| Data | Tool |
|---|---|
| Cataloged or ETL tabular data, enforce rules, quarantine, publish metrics | **AWS Glue Data Quality** (**DQDL**) |
| ML dataset profiling, outliers, leakage, reusable prep flows | **SageMaker Data Wrangler** in **SageMaker Pipelines** |
| Domain-specific business rules, unstructured text checks | **Lambda** functions with **CloudWatch** metrics |

**How does the store stay fresh?**

| Requirement wording | Answer |
|---|---|
| Periodic freshness, changed documents only | **Knowledge Base** sync (`StartIngestionJob`) on an **EventBridge** schedule |
| Minutes for new documents, immediate removal of deleted ones, event-driven, resilient | **S3 Event Notifications** → **SQS** → **Lambda** → `IngestKnowledgeBaseDocuments` / `DeleteKnowledgeBaseDocuments` (the ExamPro variant that says "avoid polling" keys the direct **S3** → **Lambda** path) |
| Own vector store, records change all day | **S3** events or **DynamoDB Streams** → **SQS** → **Lambda** or **SageMaker Processing** re-embeds only changed documents |
| New embedding model | Planned full re-embed of the corpus |
| Ingestion failures | **Knowledge Base** logging to **CloudWatch Logs**, query with **Logs Insights** |

**Which log answers which question?**

| Need | Source |
|---|---|
| Who called which **Bedrock** API, when (no prompt content) | **AWS CloudTrail** (runtime calls are management events; agents, KB retrieval, flows and `RenderPrompt` need data event selectors) |
| The prompts and responses themselves, with metadata | **Bedrock** model invocation logging to **CloudWatch Logs** or **S3** |
| Seven-year tamper-proof retention | Invocation logs in **S3** with **Object Lock** compliance mode |
| Why a document failed to ingest | **Knowledge Base** logging to **CloudWatch Logs** |
| Which guardrail policy intervened | **CloudWatch** `InvocationsIntervened` by `GuardrailPolicyType`, with trace enabled (guardrail metrics and traces are taught in Domain 3 unit 01) |


## Words that give the answer away

- "without code changes / redeployment" → **AWS AppConfig** read at runtime behind a **Lambda** router.
- "model available in a single Region", "continue operating" → **cross-Region inference** plus a **Step Functions** circuit breaker and graceful degradation.
- "Too many requests" → **cross-Region inference**, or **Provisioned Throughput**, or backoff with jitter.
- "stop when a phrase appears" → **stop sequences**.
- "most relevant results appear lower" → **hybrid search** plus a **Bedrock** reranker.
- "vector misses keywords, keyword misses meaning" → **hybrid search**.
- "sentences split across chunks" → **semantic chunking**. "nested manuals, section updates" → **hierarchical chunking**.
- "filter by date, author, project" → a metadata schema in **S3** tags and metadata, mapped to filterable fields.
- "trace outputs to sources" → **Glue Data Catalog** registration plus output tagging.
- "one interface over several vector stores" → function calling with a standard search tool, or **MCP**.
- "vague questions, clarify, keep context" → **Step Functions**, **Comprehend**, **DynamoDB**.
- "version control, approval, audit who used prompts" → **Prompt Management**, **S3**, **CloudTrail**, **CloudWatch Logs**.
- "reusable prompt components, conditional branching" → **Bedrock Flows**.
- "hundreds of **LoRA** adapters, one endpoint" → **SageMaker** **inference components**.
- "register, approve, roll back, retire fine-tuned models" → **Model Registry** plus a CI/CD pipeline with alarm-based rollback.
- "classify and extract from mixed documents, no custom models" → **Bedrock Data Automation**.
- "call recordings into summaries" → **Transcribe** → **Comprehend** → **Bedrock**.
- "minimal operational overhead" anywhere → the managed service, never **EC2**, never custom code that a service already does.

## Domain 1 on one page

Design starts by sorting requirements into knowledge, safety, integration and hosting, and answering each with a managed service. **Bedrock** supplies the models and most of the surrounding pieces, and **SageMaker AI** supplies custom hosting and training.

Integrate through the service that matches the interaction:

- **API Gateway** and **Lambda** for synchronous calls.
- **WebSockets** for streaming.
- **SQS** and **Step Functions** for asynchronous work.
- **EventBridge** for event-driven enrichment.
- **AppSync** and **Amplify** for typed front ends.

Prove feasibility small, in **Bedrock**, with measured quality, latency, throughput and cost. Then standardise with the **Well-Architected Generative AI Lens** and reusable templates in **Service Catalog**.

Select models by evaluating candidates on your task with **Bedrock** evaluation, which comes in automatic, **LLM-as-a-judge**, human and **robustness** forms. Then buy capacity to fit: **on-demand**, **cross-Region inference**, **Provisioned Throughput**, **batch**, **latency-optimized** or **prompt routing**.

Control output with **temperature** or **top-p**, max tokens and **stop sequences**. Route through **Lambda** and **AppConfig**. Survive failure with **cross-Region inference**, backoff, circuit breakers and tiered degradation. Manage fine-tuned models with **LoRA** adapters as **inference components**, **Model Registry** approval, pipeline deployments with rollback, **Model Monitor** and retirement rules.

Validate data with **Glue Data Quality**, **Data Wrangler** and **Lambda**, publishing to **CloudWatch**. Process each modality with **Transcribe**, **Comprehend**, **Textract**, **Rekognition**, **SageMaker Processing** and **Bedrock Data Automation** under **Step Functions**, and send the model a **Converse**-style structured request. Clean inputs with a cheap model, **Comprehend** entities and **Lambda** normalisation.

Pick the vector store by ops appetite and scale, design filterable metadata, and scale **OpenSearch** with shards, multiple indexes, **ANN** and **quantisation**. Connect sources through **Knowledge Bases** connectors or **Lambda** and **Glue**, and keep it fresh with incremental syncs and event-driven direct ingestion through **SQS** and **Lambda**.

Chunk to fit the content, embed with a model chosen on domain queries at the right dimensionality, search hybrid where terms matter, rerank, rewrite and decompose queries, and expose retrieval through **Knowledge Bases**, function calling or **MCP**.

Write prompts as specifications and pair **Prompt Management** with **Guardrails**. Keep conversations in **DynamoDB** with **TTL**, detect intent with **Comprehend**, and clarify with **Step Functions**. Govern with versions, **IAM**, **S3**, **CloudTrail** and invocation logging with **Object Lock**, test prompts like code, and chain them with **Bedrock Flows**.

## Mixed quiz

These are the Domain 1 questions not used in units 01 to 06. Work through them cold; every one maps to a section above.

<!-- KC: REVIEW -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 16

A digital publishing platform uses Amazon Bedrock to generate study summaries and quiz items for its online learning portal. The system combines instructor-approved reference material with large collections of scraped public content. Before any generated summary or quiz is published, quality reviewers must verify where the information originated to ensure the accuracy and credibility of the generated educational content.

The company wants to provide reviewers with a simple way to trace each generated output back to its original data sources. The solution must introduce the least operational overhead, support automated lineage tracking, and integrate cleanly with the existing Bedrock-powered generation workflow.

Which combination of steps will meet these requirements with the LEAST operational overhead? (Select TWO.)

- **A)** Register all curated and scraped source datasets in AWS Glue Data Catalog to provide structured, searchable metadata for reviewers.
- **B)** Configure AWS CloudTrail to track reviewer approval actions for each generated summary or quiz.
- **C)** Tag generated outputs with metadata that identifies the specific curated or scraped sources used during content generation.
- **D)** Use Amazon SageMaker Clarify to produce explainability reports for each generated content item.
- **E)** Use Amazon Bedrock invocation logging to track model usage and manually cross-reference invocation events with the original data sources.

<details><summary>Answer</summary>

**Answer: A, C.** Registering curated and scraped datasets in the Glue Data Catalog gives reviewers searchable source metadata, and tagging each generated output with the sources it used provides automated lineage with almost no extra infrastructure. CloudTrail tracks API calls not reviewer approvals, Clarify explains model predictions not document provenance, and manual cross-referencing of invocation logs is high overhead.

*Where this is covered: Unit 04, Metadata frameworks. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 1, question 21

A financial services company is designing an internal generative AI platform to help analysts summarize regulatory filings, classify risk disclosures, and generate compliance-ready reports. The AI engineering team plans to use multiple foundation models through Amazon Bedrock—one model for summarization, another for classification, and a third for generating structured compliance outputs. They also need an architecture that supports flexible model switching without code changes, enforces separation of concerns across services, and allows the platform to scale independently for each workload. The team must create an architecture that aligns with business requirements while handling these technical constraints.

Which architectural approach BEST satisfies these requirements?

- **A)** Use AWS Step Functions to orchestrate all model calls in a single workflow with hardcoded task definitions for each model.
- **B)** Use an Amazon EC2 instance running a custom inference server that handles routing logic across Bedrock models using local environment variables for configuration changes.
- **C)** Use an API-based model routing layer with Amazon API Gateway and AWS Lambda to dynamically route requests to different Bedrock models, enabling modular services and configuration-based model switching.
- **D)** Use a single monolithic Lambda function that invokes all Bedrock models based on conditional logic within the function.

<details><summary>Answer</summary>

**Answer: C.** An API Gateway and Lambda routing layer with configuration-based model selection gives modular services, independent scaling and switching without code changes. Hardcoded Step Functions tasks, an EC2 router configured by environment variables and a monolithic Lambda all require code or instance changes and couple the workloads.

*Where this is covered: Unit 02, Switching models without code changes. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 1, question 25

A global media company is building an FM-powered summarization platform on Amazon Bedrock. To meet internal compliance policies, the solution must provide:

- End-to-end traceability of all ingested data sources
- Metadata attribution embedded in each FM-generated summary
- Auditable logs showing when each source was accessed
- A scalable, low-maintenance implementation

Which solution BEST satisfies these requirements?

- **A)** Use Lambda to write data access records to Aurora and configure API Gateway to export request logs.
- **B)** Use AWS Glue Data Catalog to register all source datasets, apply metadata tags for attribution during summary generation, and enable CloudTrail to record all data access events.
- **C)** Store documents in S3 with folder-style prefixes, include the S3 path in summaries, and rely on S3 server access logs for traceability.
- **D)** Create a DynamoDB table mapping document IDs to summaries and use CloudWatch Logs to track ingestion events.

<details><summary>Answer</summary>

**Answer: B.** The Glue Data Catalog registers every source dataset for end-to-end traceability, metadata tags on summaries provide attribution, and CloudTrail records data access events, all managed and low maintenance. Aurora access records, S3 path strings with server access logs, and a DynamoDB mapping with CloudWatch Logs are custom, partial and higher effort.

*Where this is covered: Unit 04, Metadata frameworks. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 4. Exam 2, question 24

A global education platform is building a semantic search capability to support its new AI-powered learning assistant. The platform stores millions of unstructured documents—lecture transcripts, instructor notes, solution guides, and support logs—in Amazon S3 after migrating from an aging on-premises file system. The assistant uses Amazon Bedrock for RAG-style reasoning and Amazon Comprehend for classification and entity extraction across the repository.

The company needs a retrieval layer that integrates directly with S3, scales efficiently across terabytes of text, and supports context-aware semantic search without requiring teams to manually build and maintain an embedding pipeline. The solution must return highly relevant passages by meaning—not keywords—while operating as a fully managed service.

Which AWS approach best enables scalable semantic retrieval for the learning assistant?

- **A)** Use AWS Lambda to parse documents, generate embeddings with a custom model, store them in Amazon DynamoDB, and run search queries using DynamoDB scans.
- **B)** Generate embeddings in SageMaker notebooks and store them in SageMaker Feature Store, then perform semantic searches using ad hoc SQL filtering.
- **C)** Ingest S3 documents into Amazon Kendra using the S3 connector and perform semantic search through Kendra's built-in ranking engine.
- **D)** Extract text with Amazon Textract, load it into Amazon Redshift, and use Amazon OpenSearch Service to run semantic queries on the structured tables.

<details><summary>Answer</summary>

**Answer: C.** Amazon Kendra with the S3 connector is a fully managed semantic search service that indexes terabytes of documents and ranks passages by meaning without an embedding pipeline to build or maintain. Custom embeddings in DynamoDB with scans, Feature Store with SQL filtering, and Redshift tables are not semantic retrieval layers. Note that Kendra is no longer open to new customers; in a fresh design the same requirement points to Bedrock Knowledge Bases.

*Where this is covered: Unit 04, The AWS options. Key: ours, confidence high.*

</details>

### 5. Exam 2, question 25

A healthcare analytics startup is building a clinical-assistant application that retrieves medical guidelines, treatment protocols, and physician notes to augment foundation model responses. The AI team needs to implement a vector search layer that supports high-dimensional embeddings, real-time indexing of new documents, and fast approximate-nearest-neighbor (ANN) search across millions of vectors. The solution must also integrate cleanly with Bedrock-based RAG pipelines without requiring the team to manage custom vector retrieval logic.

Which vector search solution BEST meets these requirements?

- **A)** Use Amazon DynamoDB with a custom Lambda-based cosine similarity search workflow.
- **B)** Use Amazon S3 to store embeddings in JSON files and perform client-side vector search during inference.
- **C)** Use Amazon Aurora PostgreSQL with pgvector to store all embeddings in a single table without ANN indexing.
- **D)** Use Amazon OpenSearch Service with its vector search engine, ANN support, and Bedrock-compatible retrieval APIs.

<details><summary>Answer</summary>

**Answer: D.** Amazon OpenSearch Service provides high-dimensional vector storage, real-time indexing and approximate nearest-neighbour search across millions of vectors, and works with Bedrock retrieval. Lambda-computed cosine similarity over DynamoDB, client-side search over S3 JSON, and pgvector without an ANN index cannot meet the latency and scale requirements.

*Where this is covered: Unit 05, Deploying vector search. Key: ours, confidence high.*

</details>

### 6. Exam 2, question 50

A global broadcasting company wants to build an AI-powered investigation assistant that helps reporters search across years of mixed media assets, including transcripts, photographs, satellite imagery, and recorded interviews. The organization plans to use Amazon Bedrock Data Automation (BDA) to automatically extract topics, entities, timestamps, and visual attributes from all media types.

To support natural-language queries such as “Find the segment where the analyst discussed economic sanctions while showing satellite images of cargo ships”, the system must enable multimodal semantic retrieval and provide the retrieved context to a foundation model hosted on Amazon SageMaker AI for answer generation.

Which architecture will best satisfy these requirements?

- **A)** Use Bedrock Data Automation (BDA) to preprocess the media files and store extracted metadata in DynamoDB. Query DynamoDB directly from a SageMaker-hosted model for response generation.
- **B)** Process media through BDA and stream the insights to Amazon OpenSearch Service. Perform vector search directly from the model prompt and have SageMaker AI interpret raw search results.
- **C)** Leverage Bedrock Data Automation (BDA) to extract structured insights from text, images, audio, and video; index the enriched content inside Bedrock Knowledge Bases for multimodal semantic search; and pass retrieved context to a foundation model deployed on SageMaker AI for response synthesis.
- **D)** Use only BDA to extract entities and topics, skip building a retrieval index, and feed the entire structured dataset into the SageMaker AI model at inference time for complex reasoning.

<details><summary>Answer</summary>

**Answer: C.** Bedrock Data Automation extracts structured insights from text, images, audio and video, Knowledge Bases indexes that enriched content for multimodal semantic retrieval, and the retrieved context is passed to the SageMaker-hosted model for generation. Querying DynamoDB directly is not semantic search, having the model interpret raw OpenSearch results skips the retrieval layer, and feeding the whole dataset at inference time ignores context limits.

*Where this is covered: Unit 03, Process every modality into model-ready form. Key: ours, confidence high.*

</details>

### 7. Exam 2, question 51

A government-regulated medical research institute is building a hybrid AI platform to forecast patient recovery outcomes using both structured records and unstructured physician notes. Historical clinical data resides in an on-premises Microsoft SQL Server database, while non-sensitive operational metrics may be transferred to Amazon S3 for periodic retraining of models deployed in Amazon SageMaker AI. Sensitive patient-identifying data is legally restricted from leaving the on-premises facility.

All cloud-bound data transfers must occur over a secure IPsec tunnel using an existing AWS Site-to-Site VPN. The engineering team needs a daily automated process that extracts only non-sensitive fields from the SQL Server database and uploads them to Amazon S3 without exposing any restricted medical information.

Which solution meets all compliance and transfer requirements?

- **A)** Configure Amazon Kinesis Data Streams to batch-ingest SQL Server records from the on-premises environment and use AWS Lambda to remove sensitive attributes before delivery to S3.
- **B)** Deploy AWS Database Migration Service (AWS DMS) to replicate the SQL Server database to S3 and rely on table-mapping rules to exclude sensitive data during the migration process.
- **C)** Use Amazon DataSync to transfer full SQL Server database exports to S3 daily, then apply server-side filtering with AWS Lambda to remove regulated medical fields before retraining.
- **D)** Set up an AWS Glue ETL job to connect to the on-premises SQL Server using a JDBC connection, filter out sensitive columns, and securely load the sanitized dataset into Amazon S3 through the Site-to-Site VPN.

<details><summary>Answer</summary>

**Answer: D.** A Glue ETL job connects to the on-premises SQL Server over JDBC through the existing Site-to-Site VPN, selects only the non-sensitive columns, and writes the sanitised dataset to S3 on a daily schedule, so restricted fields never leave the facility. Kinesis is for streaming, DMS replicates whole tables and is meant for migration rather than a filtered daily extract, and DataSync would first export full data including restricted fields. (See the paragraph "Data that lives on premises" in that section.)

*Where this is covered: Unit 03, Validate before you generate. Key: ours, confidence medium.*

</details>

### 8. Exam 3, question 6

A company is developing a generative AI assistant that summarizes customer interactions, composes personalized emails, and provides account recommendations. CRM data and support logs are stored in Amazon S3. The team uses Amazon Comprehend to extract sentiment and entities, and Amazon SageMaker AI to train engagement-scoring models. The pipeline must continuously ingest fresh CRM data, enrich it with Comprehend, combine it with SageMaker outputs, and feed it automatically into foundation model workflows—without ongoing manual ETL work.

Which approach offers the most scalable and reliable method for automating the CRM data processing pipeline?

- **A)** Use Amazon EventBridge to trigger AWS Lambda functions whenever new CRM data is added to S3. Set up a Lambda function to preprocess the data, call Comprehend for sentiment analysis, and push the output to SageMaker AI for model retraining.
- **B)** Use Amazon Bedrock Data Automation to continuously ingest CRM data from S3. Apply preprocessing, including sentiment and entity extraction with Comprehend, and automatically load the enriched data into retraining pipelines for SageMaker AI and foundation models.
- **C)** Connect to CRM data using SageMaker Data Wrangler, perform transformations, and analyze text with Comprehend. Run SageMaker AI training jobs separately and manually trigger foundation model retraining in Amazon Bedrock.
- **D)** Export CRM data to S3 every week, run a SageMaker Notebook to transform the data, call Comprehend, and feed the output into the foundation model retraining.

<details><summary>Answer</summary>

**Answer: A.** EventBridge triggering Lambda when new CRM data lands in S3, with Lambda preprocessing, calling Comprehend for sentiment and entities, and pushing enriched output to SageMaker retraining, is the scalable event-driven pipeline with no manual ETL. Bedrock Data Automation extracts insights from unstructured documents, images, audio and video; it is not a continuous ingestion and enrichment engine for CRM records, so option B misapplies it even though it reads well. Data Wrangler with manual triggers and weekly notebooks are manual.

*Where this is covered: Unit 03, Process every modality into model-ready form. Key: ours, confidence medium.*

</details>

### 9. Exam 3, question 34

A research company uses a vector database to support retrieval-augmented generation for its internal knowledge assistant. As the dataset grows, engineers notice slower similarity searches, inconsistent relevance scores, and occasional retrieval drift caused by outdated or low-quality embeddings. The company wants an operational management approach that improves vector store reliability, maintains index performance automatically, and validates embedding quality during ingestion. The solution should use managed AWS services and require minimal ongoing maintenance.

Which solution will BEST meet these requirements with the least operational overhead?

- **A)** Use CloudWatch metrics to continuously monitor vector store latency and index saturation, and create an automated index optimization routine with EventBridge and Lambda to rebuild or compact indexes based on threshold conditions.
- **B)** Run daily Athena queries to recalculate embedding drift across the entire dataset and rewrite low-quality segments into the vector store.
- **C)** Create a Glue job that performs scheduled cosine similarity checks across all embeddings and removes vectors that fall below a similarity threshold.
- **D)** Use a Step Functions pipeline that requires manual approval for embeddings before they are inserted into the vector store to maintain data quality.

<details><summary>Answer</summary>

**Answer: A.** CloudWatch metrics monitor vector store latency and index saturation, and EventBridge with Lambda automates index rebuild or compaction when thresholds are crossed, keeping the store reliable with minimal maintenance. Daily Athena recalculations, Glue similarity sweeps that delete vectors, and manual approval of every embedding are heavy or manual.

*Where this is covered: Unit 04, Performance at scale. Key: ours, confidence high.*

</details>

### 10. Exam 3, question 37

A global e-learning platform is building an AI-powered content generation system that uses multiple foundation models (FMs): one for summarization, one for question generation, and one for code explanation. The platform wants to automatically select the appropriate FM based on the user’s request type. The solution must support dynamic routing, handle large traffic volumes efficiently, and minimize the operational overhead of maintaining separate integration endpoints for each model.

The engineering team also needs the flexibility to add new specialized models in the future without modifying client-facing APIs.

Which solution will meet these requirements MOST effectively?

- **A)** Create static routing tables inside an AWS Lambda function that maps request types to specific FM ARNs. Update the Lambda function manually whenever new models are added.
- **B)** Implement routing logic directly inside front-end applications by embedding FM identifiers inside each request. Call the appropriate Bedrock model directly based on request type.
- **C)** Use Amazon CloudFront Functions to inspect request metadata and forward traffic to multiple backend API Gateway endpoints, each dedicated to a different FM.
- **D)** Use Step Functions to orchestrate model routing by inspecting the request type and invoking the appropriate FM. Expose a single API Gateway endpoint with request transformations to route traffic to the Step Functions workflow.

<details><summary>Answer</summary>

**Answer: D.** Step Functions inspects the request type and invokes the matching FM behind a single API Gateway endpoint with request transformations, so new specialised models are added to the workflow without changing the client-facing API. Static Lambda routing tables need manual code updates, front-end routing embeds model identifiers in clients, and CloudFront Functions forwarding to per-model API Gateways multiplies endpoints.

*Where this is covered: Unit 02, Switching models without code changes. Key: ours, confidence high.*

</details>

### 11. Exam 3, question 51

A global ecommerce company is building a semantic product-search system that supports millions of items across multiple specialized categories such as electronics, apparel, home goods, and automotive. The company uses Amazon OpenSearch Service with the neural search plugin to store embeddings generated by an Amazon Bedrock model. As traffic grows, search latency increases and some queries return incomplete results because certain categories dominate the primary index. The architecture must be optimized to improve retrieval performance at scale while keeping the operational burden low.

Which solution will MOST effectively optimize vector search performance for this workload?

- **A)** Create a single index but add category labels to each vector document so that queries can filter results based on the user’s category. Rely on vector scoring alone for retrieval performance.
- **B)** Store all embeddings in a single large OpenSearch index and increase the number of replicas to improve search speed across all categories.
- **C)** Use Amazon RDS with the pgvector extension to store all product embeddings in a single table and scale vertically by increasing the database instance size.
- **D)** Partition the data by domain and create multiple specialized vector indices in OpenSearch (for example, electronics, apparel, automotive). Use category routing to query only the relevant index and apply sharding within each index to reduce search load and improve recall.

<details><summary>Answer</summary>

**Answer: D.** Partitioning by domain into specialised vector indexes with category routing searches only the relevant index, and sharding within each index spreads load, which fixes both latency and the dominant-category recall problem. A single filtered index still scans everything, more replicas do not shrink the search space, and pgvector scaled vertically is a worse fit at this scale.

*Where this is covered: Unit 04, Performance at scale. Key: ours, confidence high.*

</details>

### 12. Exam 3, question 56

A global logistics intelligence platform uses an FM in Amazon Bedrock to generate anomaly explanations and delivery-delay summaries for operations teams. The system runs primarily in a single Region and uses AWS Step Functions to orchestrate inference workflows. During seasonal demand spikes, the team notices intermittent Bedrock throttling and occasional Regional degradation. The platform must continue operating even when the primary Region has limited availability. It must also fall back gracefully to a lightweight rules-based summary generator when FM capacity is severely constrained. The architects want the solution to require minimal code changes and avoid manual failover procedures.

Which combination of steps will ensure a resilient and continuously available FM workflow? (Select TWO.)

- **A)** Wrap FM calls in an AWS Step Functions workflow that implements a circuit breaker pattern. Detect repeated timeouts or throttling from Bedrock and route failed invocations to a graceful degradation branch that uses a smaller FM or cached responses instead of failing user requests.
- **B)** Increase the provisioned throughput allocation for the FM in the primary Region and rely on automatic retries from the AWS SDK to handle transient errors, without changing any Regional configuration.
- **C)** Configure Amazon Bedrock Cross-Region Inference to use a primary FM in the existing Region and a secondary FM in a nearby Region. Point the application to the Bedrock cross-Region endpoint so traffic automatically shifts to the secondary Region when the primary has limited availability.
- **D)** Deploy a duplicate copy of the RAG pipeline in a second AWS account and require operators to flip a feature flag and redeploy the application when the primary Region experiences issues.
- **E)** Use Amazon API Gateway and AWS Lambda as a proxy in front of the Bedrock endpoint and configure Amazon Route 53 weighted routing across two API Gateway endpoints in the same Region to spread traffic and reduce throttling.

<details><summary>Answer</summary>

**Answer: A, C.** A Step Functions circuit breaker detects repeated timeouts or throttling and routes to a graceful degradation branch (smaller FM or cached responses), and cross-Region inference shifts traffic to a secondary Region automatically when the primary is constrained, both without manual failover. Only raising Provisioned Throughput ignores Regional degradation, a duplicate pipeline needing a feature-flag flip is manual, and Route 53 weighting between two API Gateways in one Region does not escape that Region.

*Where this is covered: Unit 02, Designing for failure. Key: ours, confidence high.*

</details>

### 13. Exam 3, question 57

A global insurance company is building an internal generative AI platform that uses Amazon Bedrock across multiple business units. To ensure consistent FM behavior, leadership requires strict governance over prompts, including version control, approval workflows, and operational visibility. The platform must support parameterized prompt templates for different departments, maintain a central repository for approved templates, and track all prompt usage for compliance reviews. The solution must minimize custom governance code and rely on managed AWS services.

Which solution will MOST effectively meet these requirements?

- **A)** Use Amazon Bedrock Prompt Management for parameterized templates and approval workflows, store approved templates in Amazon S3, enable AWS CloudTrail to track Bedrock API usage, and configure Amazon CloudWatch Logs for prompt access logging.
- **B)** Use Amazon DynamoDB to store prompt templates, use Step Functions to create approval workflows, use AWS X-Ray to trace prompt calls, and use EventBridge to notify teams of changes.
- **C)** Use Amazon API Gateway with usage plans to enforce prompt access control, store templates in AWS CodeCommit, and use CloudWatch Alarms to track abnormal usage patterns.
- **D)** Use AWS Lambda functions to manage template versioning, store templates in Amazon S3, use Athena queries for access tracking, and require manual approval steps through email notifications.

<details><summary>Answer</summary>

**Answer: A.** Prompt Management for parameterised templates and approval, S3 for the approved template repository, CloudTrail for Bedrock API usage tracking and CloudWatch Logs for prompt access logging is the managed governance stack named in skill 1.6.3. DynamoDB with Step Functions approvals and X-Ray, API Gateway usage plans with CodeCommit, and Lambda versioning with email approvals are custom governance code.

*Where this is covered: Unit 06, Governance of prompts. Key: ours, confidence high.*

</details>

### 14. Exam 3, question 62

A healthcare analytics company is developing a generative AI workflow that summarizes patient case files and produces structured diagnostic reports. The workflow uses an Amazon Bedrock FM for summarization, AWS Lambda functions for data preprocessing, and a multi-step orchestration built with AWS Step Functions.

During testing, the engineering team notices that occasionally the FM produces extremely long or repetitive responses, causing downstream Lambda tasks to time out. There are also intermittent FM API failures that cause the entire workflow to retry excessively and exceed SLA limits. The solution must prevent runaway FM behavior, enforce strict execution boundaries, and gracefully degrade when repeated failures occur—without requiring manual operator intervention.

Which solution will meet these requirements?

- **A)** Use AWS Step Functions with a built-in circuit breaker to halt the workflow after repeated Bedrock API failures, implement a Step Functions choice state to enforce FM output length stopping conditions, and add Lambda timeouts to cap downstream processing.
- **B)** Use an SQS queue between Step Functions states so that FM responses exceeding the token limit are placed back into the queue for delayed reprocessing until they meet output constraints.
- **C)** Set a global maximum concurrency limit on the Lambda functions so that excessive FM retries are throttled automatically without making changes to Step Functions logic.
- **D)** Configure Amazon CloudWatch Alarms to stop the workflow whenever the Bedrock invocation count exceeds a threshold and send an SNS notification for operators to manually restart the workflow.

<details><summary>Answer</summary>

**Answer: A.** A Step Functions circuit breaker halts the workflow after repeated Bedrock failures, a Choice state enforces output-length stopping conditions, and Lambda timeouts cap downstream processing, preventing runaway generations and excessive retries without operators. Requeuing oversized responses, Lambda concurrency limits, and CloudWatch alarms with manual restarts do not enforce execution boundaries automatically.

*Where this is covered: Unit 02, Designing for failure. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## What to do next

Move to Domain 2. If more than a quarter of the mixed quiz went wrong, reread the *Exam lens* sections of units 02, 04 and 05 first. They carry most of the Domain 1 weight.
