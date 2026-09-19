# Unit 04: Vector stores

**Task 1.4: Design and implement vector store solutions.** Five skills sit under it:

- Choose and build a vector database architecture for FM augmentation, using **Bedrock Knowledge Bases**, **OpenSearch** with the **Neural plugin**, **RDS** with **S3** documents, or **DynamoDB** with vectors.
- Design a metadata framework that sharpens retrieval, through **S3** object metadata, custom attributes and tagging taxonomies.
- Scale it, with **OpenSearch** sharding, multi-index designs and hierarchical indexing.
- Connect it to the systems that hold the content: document management systems, knowledge bases and wikis.
- Keep it current, with incremental updates, change detection, synchronisation workflows and scheduled refreshes.

Unit 05 covers what goes *into* the store, meaning chunking and embeddings, and how you *search* it. This unit is about the store itself and the plumbing around it.

## What a vector store does

An embedding model turns a piece of text, or an image, into a **vector**: a list of numbers that places it in a space where similar meanings sit close together.

A vector store holds millions of those vectors, each attached to the original chunk and to metadata, and answers one question fast: which stored vectors are nearest to this query vector. Nearness is measured with **cosine similarity**, **dot product** or **Euclidean distance**. The store must use the same metric and the same embedding model that produced the vectors.

Exact nearest-neighbour search compares the query with every vector and does not scale. Production stores use **approximate nearest neighbour (ANN)** indexes instead, most commonly:

- **HNSW**, a graph you navigate.
- **IVF**, clusters you probe.

Both trade a little **recall**, the share of the true nearest neighbours the index actually returns, for orders of magnitude in speed. Index parameters tune that trade-off: `m`, `ef_construction` and `ef_search` for **HNSW**. **Metadata filtering** narrows the candidate set before or after the vector comparison, and **hybrid search** adds a keyword score to the vector score, which unit 05 covers.

Every question in this task is a matching exercise between these properties and a scenario. How many vectors, how often queried, how fresh, how much filtering, how much operational effort the team will accept, and how tightly it must integrate with **Bedrock**.

## The AWS options

First the landscape, because vector search is one capability layered on data stores you may already know. AWS databases and stores in 2026 come in families:

- **Relational**: **Amazon RDS** for **PostgreSQL**, **MySQL** and others, and **Amazon Aurora**, the cloud-native **PostgreSQL**- and **MySQL**-compatible database. **Aurora PostgreSQL** and **RDS PostgreSQL** add vectors through the **pgvector** extension.
- **Key-value and document NoSQL**: **Amazon DynamoDB** for single-digit-millisecond key-value access, and **Amazon DocumentDB** for **MongoDB**-compatible documents.
- **In-memory**: **Amazon ElastiCache** for **Redis OSS**, **Valkey** and **Memcached** caching, and **Amazon MemoryDB** for a durable in-memory database with vector search.
- **Graph**: **Amazon Neptune**, and **Neptune Analytics** for graph analytics and **GraphRAG**.
- **Search and analytics**: **Amazon OpenSearch Service** clusters and **OpenSearch Serverless**, the engines with native **k-NN** vector search.
- **Time series**: **Amazon Timestream**.
- **Data warehouse**: **Amazon Redshift**.
- **Object storage**: **Amazon S3**, and **S3 Vectors** for vector indexes stored in **S3**.
- **File storage**: **Amazon EFS** and **FSx**.

For vectors, the exam draws on the search engines, **S3 Vectors**, **Aurora** with **pgvector**, **MemoryDB** and **Neptune Analytics**, plus the third-party stores below. **DynamoDB**, **RDS** stored procedures and plain **S3** objects are the distractors.

**Amazon Bedrock Knowledge Bases** is the managed RAG service and the default answer when the requirement says "minimal operational overhead" and "integrates natively with **Bedrock**". It ingests from a data source, chunks, embeds with a **Bedrock** embedding model, writes to a vector store, and serves `Retrieve` and `RetrieveAndGenerate`.

During creation you can let it quick-create an **Amazon OpenSearch Serverless** collection or an **Aurora PostgreSQL** cluster, or you can bring your own store. Supported stores are:

- **OpenSearch Serverless** and **OpenSearch Service** managed clusters.
- **Amazon S3 Vectors**.
- **Aurora PostgreSQL** with **pgvector**.
- **Amazon Neptune Analytics**, for **GraphRAG**, which is retrieval over a knowledge graph of entities and relationships extracted from your documents.
- **Pinecone**, **Redis Enterprise Cloud** and **MongoDB Atlas**.

A **Knowledge Base** has two more retrieval routes. It can use an **Amazon Kendra GenAI index** as a managed retriever, where **Kendra** is the managed enterprise search service. And it can query structured data in **Amazon Redshift** or the **Glue Data Catalog** by translating natural language to SQL, which is the answer when a knowledge base must answer from tables rather than documents.

Three constraints are worth knowing:

- Binary embeddings work only on the two **OpenSearch** stores.
- A managed **OpenSearch** cluster used by a **Knowledge Base** must be reachable through a public-access domain rather than a VPC-only domain.
- An **Aurora** cluster must be in the same account.

**Amazon OpenSearch Service** is the workhorse when you want control. Managed clusters run the **k-NN plugin**, with **Faiss** and **Lucene** engines, **HNSW** and **IVF** indexes, and up to 16,000 dimensions. They support exact and approximate search, filtering, and **hybrid search** that normalises and combines **BM25** keyword scores with vector scores. **BM25** is the standard keyword-scoring algorithm, and it rewards rare query terms that appear often in a document.

The **Neural plugin** with **ML Commons** connectors lets the cluster call a **Bedrock** or **SageMaker** embedding model itself, so you index and query with text and **OpenSearch** generates the vectors. You choose instance types, shards and replicas, which is both the power and the cost.

**OpenSearch Serverless** vector search collections remove that choice. Capacity scales in **OpenSearch Compute Units**, indexes are compressed and built with GPU acceleration, and it is the default store **Knowledge Bases** creates for you. Serverless supports **hybrid search** when the index has a filterable text field.

**Amazon Aurora PostgreSQL and RDS for PostgreSQL with pgvector** put vectors in a relational database. You get SQL joins between vectors and business tables, transactional consistency, row-level security for multi-tenant designs, and **HNSW** or **IVFFlat** indexes; **HNSW** needs **pgvector** 0.5.0 or later.

**Knowledge Bases** connects through the **RDS Data API**, an HTTPS query interface to **Aurora** that needs no database connections. Choose this store when the vectors must live next to relational metadata, or when the team already runs **Aurora**. It is more operational work than a managed store and needs indexing to avoid full scans.

**Amazon S3 Vectors** is purpose-built, low-cost vector storage in **S3**. Vector buckets hold vector indexes, each index takes vectors of one dimension, up to 4,096, with attached metadata that is filterable by default, and you query with a dedicated API with no infrastructure.

It delivers sub-second latency for infrequent queries and is the most cost-effective choice for large collections that are queried occasionally, such as fifty million medical images searched a few times a day. It also feeds **OpenSearch** when a subset needs high query rates.

**S3 Vectors** integrates with **Knowledge Bases**, and the limits differ between the two. Used by **Knowledge Bases**, it allows up to 1 KB of custom metadata and 35 metadata keys per vector. The native **S3 Vectors** limits are larger, at 2 KB filterable and 40 KB total, but the **Knowledge Base** limit is the one that matters here, and it is why hierarchical chunking is not recommended with it.

A named hybrid pattern also appears in the exam guide: **RDS for structured metadata plus S3 for the documents**. The relational database, often **Aurora PostgreSQL** with **pgvector**, holds vectors, metadata and access rules that SQL can filter and join. The source files stay in **S3** and are fetched by key when a chunk is retrieved. It fits teams that already run **PostgreSQL** and need transactional metadata alongside vectors.

**Amazon MemoryDB** offers in-memory vector search on the **Valkey** and **Redis OSS** API, with the lowest latency and highest recall among AWS stores. That makes it the answer for **semantic caching**, which returns a previous answer when a new question is semantically similar, to avoid a model call, and for real-time recommendation lookups. **Amazon DocumentDB** also supports vector search for document-oriented workloads.

**Amazon Neptune Analytics** stores vectors alongside a graph, with one vector index per graph at a fixed dimension, and queries them with algorithms such as `topKByEmbedding`. It backs **GraphRAG** in **Knowledge Bases**, where relationships between entities improve retrieval on connected data. It is not the answer for plain semantic search.

**Amazon DynamoDB** is not a vector database. It appears in correct answers in two roles: as the metadata and embedding *store of record*, holding document IDs, chunk IDs, checksums, status and timestamps next to a real vector index, and as the session store for conversations. Computing cosine similarity in a **Lambda** function over **DynamoDB** items or **S3** JSON files is always a distractor.

**Amazon Kendra** is a managed enterprise search service with dozens of data source connectors, document-level access control, and hybrid semantic ranking, and its **GenAI Enterprise Edition** index can serve as a **Knowledge Base** retriever. It answers "fully managed semantic search over **S3** documents with no embedding pipeline to maintain" in older questions. Note that **Kendra** is no longer open to new customers. AWS points new projects at **Knowledge Bases**, but existing exam questions still use it.

| Need | Pick |
|---|---|
| Managed RAG, least ops, native **Bedrock** integration | **Knowledge Bases** (quick-create **OpenSearch Serverless**) |
| Full control of index, **hybrid search**, very large scale, custom ranking | **OpenSearch Service** (managed) or **OpenSearch Serverless** |
| Vectors next to relational data, SQL filtering, multi-tenant rows | **Aurora PostgreSQL** with **pgvector** |
| Huge collection, infrequent queries, lowest cost, no infrastructure | **S3 Vectors** |
| Lowest latency, semantic cache, real-time | **MemoryDB** |
| Graph relationships plus vectors (**GraphRAG**) | **Neptune Analytics** |
| Metadata, checksums, session state | **DynamoDB** (beside a vector index) |
| Enterprise connectors and ACL-aware search, existing investment | **Kendra** (**GenAI index** as KB retriever) |

## Metadata frameworks

Embeddings capture meaning, not provenance. A query about "return policy for damaged items" cannot tell the 2021 policy from the 2024 one, or a draft from an approved document, unless metadata says so. Skill 1.4.2 is about designing those attributes and making them filterable.

Define a standard schema for every document: publication or modification date, author or owner, document type, source system, domain classification, confidentiality or access level, version, and any business keys such as project code, product line or jurisdiction.

In **Knowledge Bases** the mechanism is a sidecar file. Next to `report.pdf` you put `report.pdf.metadata.json` containing `metadataAttributes`. Each attribute becomes a filterable field in the vector store, and queries can filter with operators such as equals, not equals, in, greater than, less than, starts with and string contains, combined with AND and OR. **Knowledge Bases** can also infer filters from the query itself, which is **implicit filtering**. For your own **OpenSearch** or **pgvector** index, the attributes become keyword, date and numeric fields alongside the vector.

**S3** helps but has limits worth knowing. User-defined object metadata is capped at 2 KB per object, and object tags at 10 per object, both versioned with the object. So use them for timestamps, type and a handful of tags, and keep richer attributes in the sidecar file or a **DynamoDB** table. Never embed metadata as prose at the top of the document and hope similarity search will respect it, and never derive it by parsing folder names in application code at query time.

Automate extraction. **Amazon Comprehend** generates entities, key phrases, language and sentiment from unstructured content, and custom classification assigns taxonomy labels. **Lambda** functions map source-system fields into the schema.

Two structures make the metadata more useful. **Hierarchical taxonomies**, such as practice area → procedural context → jurisdiction, let the model retrieve at the right granularity. **Cross-reference attributes**, such as cites, supersedes and related-to, let it follow connections.

Metadata also carries **lineage**. Register curated and scraped source datasets in the **AWS Glue Data Catalog**, tag generated outputs with the identifiers of the sources used, and let **CloudTrail** record data access, so a reviewer can trace any generated summary back to what it was built from. This is the low-overhead lineage design the exam expects. **SageMaker Clarify** explains model predictions, not document provenance, and **CloudTrail** records API calls, not reviewer approvals.

## Performance at scale

Skill 1.4.3 is mostly about **OpenSearch**, because that is where you make the decisions.

**Sharding.** An index is split into primary shards spread across data nodes, and each shard is a full **Lucene** index with its own **HNSW** graph in memory. Aim for shard sizes of roughly 10 to 30 GiB for search workloads, size the node count so each node holds a manageable number of shards, and add replicas for read throughput and availability.

Too few shards on huge indexes create hot nodes, and too many small shards waste memory. Memory-optimised instances suit **HNSW** because the graph must fit in RAM.

**Multiple indexes.** Partition by domain, time period or data source, and route each query to the relevant index. The partitions might be patents, interviews and architecture documents, or electronics, apparel and automotive. This shrinks the search space, lets you tune similarity settings per domain, and stops a dominant category from crowding out results.

**Hierarchical indexing** goes one step further. A coarse index over sections or summaries points to fine indexes over passages, so a query first finds the right neighbourhood and then the right chunk.

**Approximate search and compression.** Use **ANN** (**HNSW**) rather than exact **k-NN** for large collections, and tune `ef_search` for the recall you need. Reduce memory with **quantisation**, storing each vector with fewer bits:

- **Scalar quantisation**: 32-bit floats become 8-bit integers.
- **Product quantisation**: sub-vectors are replaced by codebook ids.
- **FP16** and **binary vectors** on **OpenSearch**.
- The compressed indexes that **OpenSearch Serverless** builds by default.

Increasing embedding dimensionality does not improve performance. It increases memory and latency.

**Caching.** Put frequently requested results and embeddings in **Amazon ElastiCache** or **MemoryDB**, and use **semantic caching** to skip both retrieval and generation for repeat questions.

**Observability.** Use **CloudWatch** for search latency, queue rejections, JVM memory pressure and index saturation, and **AWS X-Ray** to trace a request from **API Gateway** through retrieval to the model and find the slow hop. When latency or saturation crosses a threshold, **EventBridge** and **Lambda** can trigger index optimisation, such as a merge, compaction or rebuild, automatically.

## Connecting the content systems

Skill 1.4.4 asks how the store gets its documents from where they live.

**Knowledge Bases data source connectors** handle the common cases directly:

- **Amazon S3**.
- **Atlassian Confluence**.
- **Microsoft SharePoint**.
- **Salesforce**.
- A **web crawler** for public sites.
- A **custom data source** that you feed through the API.

Multimodal content, meaning images, audio and video, is supported only through **S3** and custom sources. Connectors handle authentication, with secrets in **AWS Secrets Manager**, plus incremental crawling and deletion.

For everything else, build a thin connector:

- **Lambda functions triggered by EventBridge events or webhooks** from the document management system pull the changed document, normalise its format, extract metadata into the sidecar file, and drop it into the **S3** ingestion bucket that feeds the **Knowledge Base**. They can also call the direct ingestion API, described in the next section.
- **AWS Glue ETL jobs** transform structured knowledge, such as databases and curated tables, into documents and metadata.
- A **unified search interface** on **API Gateway** and **Lambda** can aggregate results from several stores and traditional databases for the model.

Security travels with the content. Respect the source system's permissions: index only what the connector's identity may read, carry the access level as metadata, and filter retrieval by the requesting user's entitlements. The pieces for that are **Amazon Cognito** for identity, **IAM** for service access, and metadata filters or **Kendra**'s user-context filtering for document-level control.

Exporting everything to **S3** without those controls breaks the access model, which is why "custom **Lambda** connector that respects document management system access controls" beats "bulk export to **S3**". Use **SQS** between stages for retries, and **X-Ray** for cross-system tracing.

## Keeping the store current

Skill 1.4.5 is the most heavily tested part of this unit. A vector store that lags its sources returns confident, outdated answers, so the design has to move changes into the index quickly and cheaply.

**Knowledge Bases** has two update mechanisms.

- **Sync** (`StartIngestionJob`) scans the data source and adds, updates and deletes only what changed since the last sync. Schedule it with **EventBridge Scheduler** for periodic freshness.
- **Direct ingestion** (`IngestKnowledgeBaseDocuments` and `DeleteKnowledgeBaseDocuments`) indexes or removes specific documents immediately, without a full scan. It is available for **S3** and custom data sources, and you should not run it concurrently with a sync of the same data source.

For an **S3** source, changes made through direct ingestion are not written back to **S3**, so mirror them there or the next sync will undo them.

Here is the event-driven pattern that questions love. **S3 Event Notifications** on object-created and object-removed events invoke a **Lambda** function that calls `IngestKnowledgeBaseDocuments` for new or changed objects and `DeleteKnowledgeBaseDocuments` for deleted ones. Adding an **SQS queue** between **S3** and **Lambda** buffers bursts, gives retries and a **dead-letter queue**, and is what AWS means by "resilient"; the official practice question keys that variant.

The tie-break between the two shapes is the wording of the stem:

- When the stem says *resilient*, *buffer*, *retry* or *fault tolerant*, choose **S3** → **SQS** → **Lambda**.
- When it asks for the fewest components or the lowest latency and says nothing about resilience, **S3** → **Lambda** directly is enough.

Both are event-driven and neither polls **S3**. The two practice questions that share this stem are keyed differently, with the **SQS** variant in the official set and the direct variant in ExamPro's, and their folds explain why. Polling **S3** every five minutes and re-ingesting the whole bucket on a schedule are the distractors: they add latency and cost and violate "event-driven, avoid polling".

For your own **OpenSearch** or **pgvector** store the same shape applies. **S3** events or **DynamoDB Streams**, the change log of a **DynamoDB** table, feed **SQS**, and then a **Lambda** function or **SageMaker Processing** job re-chunks and re-embeds only the changed documents and upserts them.

Two managed services can replace parts of that glue:

- **Amazon OpenSearch Ingestion** pipelines are the managed streaming alternative. A serverless pipeline pulls from **S3**, **Kinesis**, **DynamoDB** or **Kafka**, can call an embedding model in flight, and writes into the **OpenSearch** vector index with no consumer code to run.
- **EventBridge Pipes** can replace the glue code. A pipe reads from **SQS**, **Kinesis** or **DynamoDB Streams**, filters and enriches events, and delivers them to the **Lambda** function or **Step Functions** workflow that updates the index.

Nightly full rebuilds from scratch are wrong when documents change all day. They are right only for planned refreshes, such as switching to a new embedding model, because every vector must be regenerated with the same model. Webhooks from wikis and document systems give real-time change detection, and **Step Functions** orchestrates the multi-step update of extract, preprocess, embed and upsert, with error handling.

Monitor the pipeline. **Knowledge Bases** can log ingestion to **CloudWatch Logs**, **S3** or **Data Firehose**, which is streaming delivery to **S3** and other destinations, and **CloudWatch Logs Insights** finds failed documents. That is how you troubleshoot ingestion, not with **CloudTrail** or model invocation logging, the record of prompts and responses covered in unit 06. Track sync latency, embedding failures and retrieval relevance, and automate remediation, such as retry, re-embed or alert through **SNS**, for missing embeddings and stale content.

## Worked scenario

A legal publisher indexes forty million documents for a research assistant: case law, statutes, internal memos with strict access rules, and a wiki edited all day. Some collections are queried constantly, others a few times a week, and the same query often repeats.

The store choice splits by workload.

- The active collections go into an **Amazon Bedrock Knowledge Base** backed by **Amazon OpenSearch Serverless**, which gives **hybrid search** and managed ingestion.
- The archive of rarely searched historical rulings goes into **Amazon S3 Vectors**, where storage is cheap and sub-second latency on infrequent queries is acceptable.
- An **Amazon MemoryDB** vector index sits in front of the assistant as a **semantic cache** for repeated questions.

A metadata framework is agreed before ingestion. Practice area, jurisdiction, decision date, document type and confidentiality level are written as **S3** object metadata and tags, then carried into filterable fields in the index, so retrieval can be narrowed by jurisdiction and users only see what their clearance allows.

Scale is planned rather than discovered. The **OpenSearch** index is split into several indexes by practice area with routing in the application, shards are sized to node memory, an **HNSW** index with tuned search parameters replaces exact search, and **quantisation** trims memory.

The internal document management system is connected through a **Lambda** connector that indexes only the documents the connector's identity may read and carries their permissions as metadata. The wiki sends webhooks on every edit instead of being crawled nightly.

Freshness is event-driven. **S3** event notifications for new and deleted objects feed an **SQS** queue whose **Lambda** consumer calls the direct ingestion and deletion APIs of the **Knowledge Base**, so a new ruling is searchable within minutes and a withdrawn memo disappears at once. For the self-managed indexes the same events drive an **OpenSearch Ingestion** pipeline, or a **Lambda** function that re-embeds only the changed documents. Ingestion logs go to **CloudWatch Logs**, where **Logs Insights** finds documents that failed to embed.

A question built on this scenario asks you to choose stores by access pattern, design metadata for filtering, scale **OpenSearch** correctly, respect source permissions, and keep everything current without polling.

## Exam lens

- "Least operational overhead, native **Bedrock**, semantic search over **S3** documents" → **Knowledge Bases** with a managed vector store. When the same question adds "hierarchical organisation plus topic-based segmentation and high-performance retrieval", the keyed answer pairs **Knowledge Bases** with **OpenSearch Service** and the **Neural plugin**.
- "Hundreds of millions of embeddings, domain routing, ingestion spikes" → **OpenSearch** with sharding across nodes and multiple specialised indexes, never one minimal-shard index, **RDS** stored procedures or **DynamoDB** binary attributes.
- "Cost-effective, infrequent similarity search over tens of millions of vectors, no infrastructure" → **S3 Vectors**.
- "Filter by date, author, project, confidentiality" → a standard metadata schema stored as **S3** tags and metadata, mapped into filterable fields in the index.
- "Reviewers must trace outputs to sources" → **Glue Data Catalog** registration plus output tagging with source identifiers.
- "New documents searchable in minutes, deleted ones gone immediately, event-driven, resilient" → **S3** events → (**SQS**) → **Lambda** → `IngestKnowledgeBaseDocuments` / `DeleteKnowledgeBaseDocuments`.
- "Embeddings not refreshed consistently as records change all day" → **S3** events → **SQS** → **Processing** job or **Lambda** that re-embeds only changed documents.
- "Wiki updated throughout the day" → webhooks for real-time change detection, not daily crawls.
- "Integrate a document management system with strict access control" → a **Lambda** connector that respects the document management system permissions and indexes only permitted documents.

## Knowledge check

<!-- KC: E2-Q11, E3-Q43, PQ-Q5, E1-Q69, E3-Q2, E3-Q3, E2-Q52, E1-Q39, E1-Q64, PQ-Q13, E2-Q69, E3-Q38 -->
<!-- KC-BEGIN -->
### 1. Exam 2, question 11

A global hospitality chain operates a multilingual AI concierge built on Amazon Bedrock using the Amazon Titan Text foundation model. The concierge assists guests with booking questions, loyalty program details, and property-specific information. While Titan generates fluent responses, it cannot answer questions that depend on proprietary hotel policies, regional guidelines, or location-specific amenity data stored in Amazon S3 and an internal configuration service.

To improve answer accuracy without retraining the Titan model, an ML engineer wants to add retrieval-augmented generation (RAG) so the concierge can reference real-time private hotel data during inference. The solution must integrate directly with Bedrock, scale automatically, and support query-time grounding across multiple data sources.

Which solution will best meet these requirements?

- **A)** Use Amazon Comprehend custom entity models to provide contextual retrieval capabilities for Titan FM.
- **B)** Fine-tune the Amazon Titan Text model on the company’s hotel policy documents using Amazon SageMaker AI.
- **C)** Set up an Amazon Bedrock knowledge base and connect it to the company’s private data sources to enable retrieval-augmented grounding for Titan FM.
- **D)** Increase context window size and raise the temperature parameter to improve Titan FM’s ability to recall hotel-specific rules.

<details><summary>Answer</summary>

**Answer: C.** A Bedrock Knowledge Base connected to the private data sources adds retrieval-augmented grounding at query time, integrates directly with Bedrock, scales automatically and needs no retraining. Comprehend entity models do not retrieve, fine-tuning changes style not facts and would require repeating for every policy change, and context window or temperature settings cannot supply data the model never saw.

*Where this is covered: Unit 04, The AWS options. Key: ours, confidence high.*

</details>

### 2. Exam 3, question 43

A global HR software company is building an AI assistant that answers employee policy questions by using retrieval-augmented generation (RAG) with Amazon Bedrock. The assistant must perform semantic search over handbooks, benefits guides, and jurisdiction-specific policies stored in Amazon S3. The team wants to minimize operational overhead for vector index management while still supporting FM augmentation with context-aware retrieval. They prefer not to manage OpenSearch clusters or implement custom vector indexing logic but need scalable performance as more documents and regions are added.

Which solution will BEST meet these requirements?

- **A)** Create an Amazon Aurora PostgreSQL cluster with the pgvector extension. Write custom application logic to compute embeddings, insert vectors, and perform similarity search queries for each request.
- **B)** Deploy an Amazon OpenSearch Service domain with vector search enabled. Build custom ingestion jobs on AWS Lambda to compute embeddings and manage index sharding, mappings, and lifecycle policies.
- **C)** Use Amazon Bedrock Knowledge Bases with a managed vector store. Connect the S3 document repository, enable vector search, and integrate the knowledge base with the Bedrock FM for retrieval-augmented prompts.
- **D)** Store documents and precomputed embeddings in Amazon DynamoDB as JSON items. Implement custom cosine similarity logic in the application layer to filter and rank results before calling the FM.

<details><summary>Answer</summary>

**Answer: C.** Bedrock Knowledge Bases with a managed vector store connected to the S3 repository handles chunking, embedding, vector search and integration with the FM, scaling as documents and regions grow without OpenSearch clusters or custom indexing logic. Aurora pgvector and OpenSearch with Lambda ingestion require the index management the team wants to avoid, and DynamoDB with application-layer cosine similarity does not scale.

*Where this is covered: Unit 04, The AWS options. Key: ours, confidence high.*

</details>

### 3. Official practice question set, question 5

A company is building a diagnostic imaging application. The application needs to perform similarity searches across 50 million images to assist with diagnosing and treating patients. The application must process new images daily. The application will perform similarity searches infrequently when users need to find similar cases for reference. The company wants a cost-effective solution that provides responsive search performance without requiring infrastructure management.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Create an Amazon S3 vector bucket with vector indexes to store image embeddings and perform similarity searches.
- **B)** Store image vectors in Amazon RDS for PostgreSQL. Use the pgvector extension to perform similarity searches using indexed vector embeddings.
- **C)** Store image vectors in Amazon OpenSearch Serverless. Use vector search capabilities for similarity searches.
- **D)** Use Amazon DynamoDB to store image vectors. Implement custom similarity search logic by using AWS Lambda functions.

<details><summary>Answer</summary>

**Answer: A.** An S3 vector bucket with vector indexes stores fifty million image embeddings at the lowest cost with no infrastructure, and its sub-second query latency is fine for infrequent similarity searches. RDS pgvector and OpenSearch Serverless cost more for a rarely queried index, and DynamoDB with Lambda similarity is not a vector search solution.

*Where this is covered: Unit 04, The AWS options. Key: AWS official answer.*

</details>

### 4. Exam 1, question 69

A media research company is building a generative AI assistant that retrieves insights from thousands of articles, interviews, video transcripts, and industry reports. Users often request information filtered by publication date, content category, author credibility, and source type (e.g., transcript vs. article). However, retrieval results are inconsistent because embeddings alone do not capture contextual attributes such as authorship, timestamps, or domain classification.

To increase search precision and improve FM-augmented responses, the AI engineering team must implement a metadata framework that enriches embeddings with structured contextual information for filtering, ranking, and relevance scoring.

Which approach BEST meets these requirements?

- **A)** Use DynamoDB to store only document titles and perform string-matching searches before sending results to the FM.
- **B)** Add metadata fields directly into the embedding vectors by appending text descriptions of authorship and timestamps before embedding.
- **C)** Use S3 object metadata to store timestamps and document types, apply custom metadata attributes for authorship and domain tags, and make these fields available for metadata filtering in the vector database during semantic retrieval.
- **D)** Store all documents in Amazon S3 without metadata and rely solely on embedding similarity to determine which documents are relevant.

<details><summary>Answer</summary>

**Answer: C.** Storing timestamps and document types as S3 object metadata, adding custom attributes for authorship and domain, and exposing them as filterable fields in the vector store lets retrieval filter and rank on context that embeddings do not capture. Title-only string matching, appending metadata as text into the embedding, and relying purely on similarity ignore the attributes.

*Where this is covered: Unit 04, Metadata frameworks. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 5. Exam 3, question 2

A global research institute is building a retrieval-augmented question-answering system on AWS. Documents are stored in Amazon S3 and indexed into a vector store that is used to augment prompts for a foundation model. Researchers need to filter results by publication date, project code, author, and confidentiality level so that the FM receives only context that is relevant to the query and appropriate for the user’s access level. The solution must improve search precision and context awareness with minimal custom logic in the application layer.

Which solution BEST meets these requirements?

- **A)** Define a standardized metadata schema for all documents. Store publication date, project code, author, and confidentiality level as S3 object tags and user-defined metadata. Ensure the ingestion pipeline maps these attributes into structured fields in the vector store index and uses them as filters and boost signals during retrieval.
- **B)** Derive metadata on the fly from S3 object keys by parsing folder names and file-name patterns in the application code. Pass the parsed values into the FM prompt so the model can decide which documents are relevant.
- **C)** Embed all metadata as plain text at the beginning of each document body before generating embeddings, and rely solely on vector similarity search without separate metadata fields or filters.
- **D)** Use Amazon CloudTrail data events on the S3 bucket to infer which documents are most frequently accessed, and treat access frequency as an implicit relevance signal for all future queries.

<details><summary>Answer</summary>

**Answer: A.** A standard metadata schema stored as S3 object tags and user-defined metadata, mapped by the ingestion pipeline into structured fields in the vector index and used as filters and boosts, improves precision and enforces access level with minimal application logic. Parsing folder names in code, embedding metadata as text, and inferring relevance from CloudTrail access frequency are fragile substitutes.

*Where this is covered: Unit 04, Metadata frameworks. Key: ours, confidence high.*

</details>

### 6. Exam 3, question 3

A global technology advisory firm is deploying a generative AI research assistant that performs semantic retrieval across hundreds of millions of embeddings derived from whitepapers, patents, interview transcripts, architecture diagrams, and internal engineering notes. The retrieval layer must support extremely fast vector similarity search, domain-specific query routing, and high availability during large-scale ingestion spikes.

The AI platform team needs a vector database architecture that optimizes semantic retrieval performance while supporting both domain specialization and distributed scaling across multiple nodes.

Which architecture BEST meets these requirements?

- **A)** Use Amazon OpenSearch Service with the Neural plugin, implement sharding strategies to distribute large embedding sets across nodes, and create multiple specialized indexes (e.g., patents, interviews, architecture docs) to improve query routing and retrieval precision.
- **B)** Store all embeddings in a single OpenSearch index with the minimum number of shards to simplify coordination and rely exclusively on similarity scoring for all queries.
- **C)** Place all embeddings in a single Amazon RDS instance and run cosine similarity calculations using SQL stored procedures.
- **D)** Use DynamoDB as the primary vector store, store embeddings as binary attributes, and perform similarity search through a custom Lambda function.

<details><summary>Answer</summary>

**Answer: A.** OpenSearch Service with the Neural plugin, sharding across nodes for distributed scale, and multiple specialised indexes for domain routing meets fast similarity search, domain specialisation and availability under ingestion spikes. A single minimally sharded index, SQL cosine similarity in RDS, and DynamoDB binary attributes with Lambda cannot scale to hundreds of millions of embeddings.

*Where this is covered: Unit 04, Performance at scale. Key: ours, confidence high.*

</details>

### 7. Exam 2, question 52

A global consulting firm is building an enterprise knowledge assistant that must retrieve information from millions of documents, including case studies, contracts, industry reports, and compliance manuals. The system must support semantic retrieval, topic-level segmentation, and hierarchical organization to surface accurate and context-rich responses for downstream FM augmentation.

The AI architecture team requires a vector database strategy that can handle large-scale embeddings, manage parent/child hierarchical document structures, and support fast semantic queries across diverse content types. Additionally, the team wants the retrieval pipeline to integrate natively with Amazon Bedrock for prompt augmentation.

Which architecture BEST meets these requirements?

- **A)** Build a DynamoDB table with only scalar metadata fields and store raw documents in Amazon RDS, performing all vector similarity logic manually inside application code.
- **B)** Use a single OpenSearch index with keyword analyzers and disable vector embeddings to minimize storage overhead.
- **C)** Store all documents as raw text objects in Amazon S3 and perform keyword search using Athena SQL queries before passing results to the FM.
- **D)** Use Amazon Bedrock Knowledge Bases for hierarchical document organization with automatic embedding generation, and integrate Amazon OpenSearch Service with the Neural plugin for topic-based segmentation and high-performance semantic retrieval.

<details><summary>Answer</summary>

**Answer: D.** Bedrock Knowledge Bases handles hierarchical (parent-child) document organisation with automatic embedding generation and native prompt augmentation, and OpenSearch Service with the Neural plugin adds topic-based segmentation and high-performance semantic retrieval, matching skill 1.4.1 word for word. Manual similarity in application code, keyword-only OpenSearch without vectors, and Athena keyword search are not semantic retrieval.

*Where this is covered: Unit 04, The AWS options. Key: ours, confidence high.*

</details>

### 8. Exam 1, question 39

A large consulting firm is building an enterprise-wide generative AI assistant that retrieves information from multiple internal systems, including a document management platform (over 20 TB of stored PDFs), a Confluence-based engineering wiki, and a set of legacy application knowledge bases. The AI engineering team must design an integration layer that continuously synchronizes documents, extracts metadata, and pushes cleaned and normalized content into an Amazon Bedrock Knowledge Base for RAG-style retrieval.

The team wants to ensure reliable connectivity between all external content sources and AWS, maintain consistent formatting, and support incremental ingestion as documents are updated.

Which approach BEST meets these requirements?

- **A)** Store all documents in Amazon RDS and require downstream FM applications to fetch and preprocess content at inference time instead of using an ingestion pipeline.
- **B)** Use AWS Lambda to pull updated documents from external systems, enrich metadata and normalize formatting, and send processed content to an Amazon S3 ingestion bucket that feeds an Amazon Bedrock Knowledge Base.
- **C)** Connect Amazon Bedrock Knowledge Bases directly to the external Confluence and document management systems and rely on Bedrock to handle synchronization without preprocessing.
- **D)** Use Amazon DynamoDB Streams to directly capture document changes from the external systems and push updates into Bedrock without additional transformation.

<details><summary>Answer</summary>

**Answer: B.** Lambda connectors pull updated documents from the document management system, the wiki and the legacy systems, normalise formatting and enrich metadata, and land the content in the S3 bucket the Knowledge Base ingests from, supporting incremental updates. Fetching at inference time from RDS skips ingestion, direct Knowledge Base connectors do not cover every system or the required preprocessing, and DynamoDB Streams cannot capture changes in external systems.

*Where this is covered: Unit 04, Connecting the content systems. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 9. Exam 1, question 64

A global logistics company is building a real-time generative AI assistant that relies on a vector database to retrieve shipment procedures, customs compliance rules, and regional operations updates across 40+ countries. These documents are stored in multiple internal systems and regularly updated throughout the day.

The AI engineering team must ensure that the organization's Amazon Bedrock-powered RAG pipeline always uses fresh, accurate embeddings. They need a solution that can detect document changes, re-chunk and re-embed only modified content, and automatically refresh the vector store without reprocessing the entire dataset. The solution must scale to thousands of document changes per hour.

Which approach BEST meets these requirements?

- **A)** Trigger manual refresh workflows that require engineers to upload updated content to S3 whenever document editors finish revisions in internal systems.
- **B)** Run a nightly batch job using Amazon SageMaker Processing to rebuild the vector index from scratch and replace the existing embeddings each morning.
- **C)** Use event-driven AWS Lambda functions triggered by document change notifications to reprocess only updated files, generate new embeddings, and synchronize them with the vector store through a Bedrock Knowledge Base ingestion S3 bucket.
- **D)** Schedule a full vector store rebuild every hour using AWS Glue crawlers to scan all documents and regenerate embeddings for the entire dataset regardless of whether content changed.

<details><summary>Answer</summary>

**Answer: C.** Event-driven Lambda functions triggered by document change notifications reprocess only the modified files, regenerate their embeddings and synchronise through the Knowledge Base ingestion bucket, scaling to thousands of changes an hour. Manual uploads, nightly full rebuilds and hourly Glue crawls all reprocess unchanged content or lag the updates.

*Where this is covered: Unit 04, Keeping the store current. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 10. Official practice question set, question 13

A company uses an AI assistant to answer customer questions based on internal company documents. The company wants to include new documents in the assistant's responses as soon as possible. The company wants to exclude deleted documents from the AI assistant's responses as soon as possible.

The documents are stored in Amazon S3. The AI assistant uses Amazon Bedrock Knowledge Bases. Amazon S3 is the data source of the vector store that the company uses for RAG. A GenAI developer must create a scalable, event-driven, and resilient solution.

Which solution will meet these requirements?

- **A)** Configure Amazon EventBridge Scheduler to schedule a rule that runs every 5 minutes and invokes an AWS Lambda function. Configure the Lambda function to track changes in Amazon S3 and invoke `IngestKnowledgeBaseDocuments` for new objects and `DeleteKnowledgeBaseDocuments` for deleted objects.
- **B)** Configure Amazon EventBridge Scheduler to schedule a rule that runs every 5 minutes and invokes an AWS Lambda function. Configure the Lambda function to sync the documents in Amazon S3 with the knowledge base by invoking `StartIngestionJob`.
- **C)** Configure S3 Event Notifications to send object-created and object-deleted events to an Amazon SQS queue. Create an AWS Lambda function to poll the queue and invoke `IngestKnowledgeBaseDocuments` for new objects and `DeleteKnowledgeBaseDocuments` for deleted objects.
- **D)** Configure S3 Event Notifications to invoke an AWS Lambda function on object-created and object-deleted events. Configure the Lambda function to invoke `IngestKnowledgeBaseDocuments` for new objects and `DeleteKnowledgeBaseDocuments` for deleted objects.

<details><summary>Answer</summary>

**Answer: C.** S3 Event Notifications to an SQS queue, consumed by a Lambda function that calls IngestKnowledgeBaseDocuments for new objects and DeleteKnowledgeBaseDocuments for deleted ones, is event-driven and resilient because the queue buffers bursts and retries failures. Scheduled Lambda polling adds delay, re-running StartIngestionJob every five minutes rescans everything, and invoking Lambda directly from S3 lacks the queue's buffering.

*Where this is covered: Unit 04, Keeping the store current. Key: AWS official answer.*

</details>

### 11. Exam 2, question 69

A publishing company uses an AI assistant powered by Amazon Bedrock Knowledge Bases to answer internal research questions. The assistant retrieves context from documents stored in Amazon S3, which serves as the data source for the vector store. The company wants newly uploaded documents to be searchable within minutes and deleted documents to be removed from responses immediately. A GenAI developer must design a scalable, resilient, event-driven solution that updates the knowledge base as document changes occur in S3. The solution must minimize operational overhead and avoid polling or scheduled jobs.

Which solution will meet these requirements?

- **A)** Configure S3 Event Notifications to publish events to an Amazon SQS queue. Use a Lambda function to poll the queue and invoke the knowledge base ingestion APIs.
- **B)** Configure S3 Event Notifications to invoke an AWS Lambda function on object-created and object-deleted events. Configure the Lambda function to invoke IngestKnowledgeBaseDocuments for new objects and DeleteKnowledgeBaseDocuments for deleted objects.
- **C)** Configure Amazon EventBridge Scheduler to invoke a Lambda function every 5 minutes to query S3 for changes and call IngestKnowledgeBaseDocuments and DeleteKnowledgeBaseDocuments.
- **D)** Use Amazon EventBridge Scheduler to run a Lambda function every 5 minutes that calls StartIngestionJob to re-ingest the entire S3 bucket into the knowledge base.

<details><summary>Answer</summary>

**Answer: B.** S3 Event Notifications invoking a Lambda function on object-created and object-deleted events, which calls IngestKnowledgeBaseDocuments and DeleteKnowledgeBaseDocuments, is event-driven and near-immediate with no schedules, which is what the stem demands. Option A is the SQS-buffered variant that the official practice question (PQ-Q13) keys as the resilient design; here the option describes the Lambda function as polling the queue while the stem says to avoid polling, and the ExamPro key follows that wording. Technically an SQS event source mapping does poll the queue on Lambda's behalf, so the two designs differ in wording more than architecture: when a stem stresses resilience and buffering, choose the SQS variant; when it stresses avoiding polling and the option itself says "poll", choose the direct path. The two scheduled options poll S3 or rescan the whole bucket and are wrong either way.

*Where this is covered: Unit 04, Keeping the store current. Key: ours, confidence medium.*

</details>

### 12. Exam 3, question 38

A global logistics company operates a retrieval-augmented assistant used by warehouse planners to query shipment histories, routing constraints, and delivery forecasts. The system stores document embeddings in Amazon OpenSearch Service and uses an Amazon Bedrock FM for generation. As warehouse activities occur throughout the day, shipment records in Amazon S3 change frequently. Users report that the assistant occasionally returns outdated information because vector embeddings are not being refreshed consistently. The company needs a scalable, low-overhead mechanism to keep embeddings accurate and synchronized with upstream data updates.

Which solution will MOST effectively maintain current and accurate embeddings in the vector store?

- **A)** Run a nightly batch job that reprocesses all documents, regenerates embeddings for the entire corpus, and recreates the OpenSearch index from scratch.
- **B)** Use Amazon S3 event notifications to send object-created and object-updated events to an Amazon SQS queue. A SageMaker Processing job polls the queue, regenerates embeddings only for changed documents, and updates the OpenSearch index.
- **C)** Manually trigger a SageMaker Processing job whenever a warehouse planner identifies incorrect or outdated search results in the FM assistant.
- **D)** Store all shipment records in Amazon DynamoDB and configure DynamoDB Streams to capture modification events. Use AWS Glue to rebuild the entire embedding store whenever any record changes.

<details><summary>Answer</summary>

**Answer: B.** S3 event notifications for created and updated objects go to an SQS queue, and a SageMaker Processing job consumes it to regenerate embeddings only for the changed documents and update the OpenSearch index, keeping embeddings current with low overhead. Nightly full rebuilds lag and waste compute, manual triggers depend on users noticing, and DynamoDB Streams with Glue rebuilding everything on any change is wasteful.

*Where this is covered: Unit 04, Keeping the store current. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

A vector store answers nearest-neighbour queries over embeddings with **ANN** indexes such as **HNSW**, filtered by metadata.

**Knowledge Bases** is the managed default, and it can sit on **OpenSearch Serverless**, **OpenSearch** clusters, **Aurora** **pgvector**, **S3 Vectors**, **Neptune Analytics** or third-party stores. Beyond it:

- **OpenSearch** is the choice for control, **hybrid search** and scale.
- **pgvector** is for vectors beside relational data.
- **S3 Vectors** is for cheap, large, infrequently queried collections.
- **MemoryDB** is for the lowest latency and **semantic caching**.
- **DynamoDB** is only for metadata and state.

Design a metadata schema, store it as sidecar attributes and filterable fields, extract it automatically, and use the **Glue Data Catalog** and output tags for lineage. Scale **OpenSearch** with right-sized shards, replicas, multiple domain indexes, **ANN**, **quantisation** and caching.

Connect sources through **Knowledge Bases** connectors, or **Lambda** and **Glue** connectors that honour source permissions. Keep the store fresh with incremental syncs and direct ingestion APIs driven by **S3** events through **SQS** and **Lambda**, re-embedding only changed content, with full rebuilds only when the embedding model changes, and **CloudWatch** logging of ingestion.
