# Unit 05: Retrieval for RAG

**Task 1.5: Design retrieval mechanisms for FM augmentation.** Six skills sit under it:

- Segment documents well, with **Bedrock** chunking options, **Lambda** for custom chunking, and hierarchical chunking.
- Choose and configure embeddings: **Titan** embeddings by dimensionality and domain fit, and batch generation.
- Deploy vector search on **OpenSearch**, **Aurora** **pgvector** or **Knowledge Bases**.
- Improve relevance with semantic search, **hybrid search** and **Bedrock** reranker models.
- Handle queries intelligently: query expansion with **Bedrock**, decomposition with **Lambda**, transformation with **Step Functions**.
- Give models a consistent way to retrieve, through function calling, **MCP** clients and standard API patterns.

Unit 04 chose the store. This unit fills it and searches it.

## The two halves of RAG

Retrieval Augmented Generation has an ingestion half and a query half.

At ingestion, documents are parsed into text and split into chunks. Each chunk is embedded, and the vector plus chunk text plus metadata is written to the store.

At query time, the user's question is embedded with the same model. The store returns the nearest chunks, optionally filtered by metadata, a reranker may reorder them, and the top chunks are placed into the prompt with instructions to answer from them and cite them. The model then generates an answer grounded in your data.

In **Bedrock Knowledge Bases** there are two operations. `Retrieve` returns the chunks and their scores and sources, so your own code can build the prompt. `RetrieveAndGenerate` does the whole loop and returns an answer with citations. Both accept a `numberOfResults`, which defaults to 5, a search type, metadata filters, and optional reranking and query decomposition.

The quality of the answer depends far more on the retrieval half than on the model, which is why this task exists.

## Segmenting documents

A chunk is what gets embedded and retrieved, so it must be small enough to be specific and large enough to be understood alone. **Knowledge Bases** offers the strategies below. You set them per data source at creation, and changing them means re-ingesting.

**Default and fixed-size chunking.** The default splits content into chunks of roughly 300 tokens, respecting sentence boundaries. **Fixed-size chunking** lets you set the maximum tokens per chunk and an overlap percentage between consecutive chunks, and the overlap preserves continuity across a boundary. It is simple and predictable and works for uniform documents, but it ignores structure, so a procedure can be cut mid-step.

**Hierarchical chunking.** Content is organised into parent chunks and smaller child chunks with an overlap in tokens. Search runs over the child chunks for precision, and the response returns the parent chunk for context, so a match on one sentence brings back the whole section. This is the answer for long operational manuals, nested safety procedures and multi-level configuration guides where updates touch individual sections.

Two cautions apply. `numberOfResults` counts child chunks before parents replace them. And hierarchical chunking is not recommended with **S3 Vectors**, because parent-child relationships are stored as metadata and hit its size limit.

**Semantic chunking.** Text is split where meaning changes, using an embedding model to find natural boundaries. You configure three settings: the maximum tokens per chunk, a buffer size, which is how many neighbouring sentences are compared, and a breakpoint percentile threshold.

It keeps multi-sentence explanations and multi-step procedures together, and it is the fix when "relevant sentences are split across chunks and multi-step procedures appear fragmented". It costs more than fixed chunking because it calls the embedding model during ingestion.

**No chunking.** Each document is one chunk. Use it when you have pre-split the content yourself, one FAQ per file, or when the documents are already small. You lose page-level citations.

**Custom chunking.** Point the data source at a **Lambda** function, with an intermediate **S3** bucket, that receives the parsed documents and returns the chunks and metadata you want. This is how you implement structure-aware chunking that follows headings, tables or HTML tags, or that inserts divider strings, when the built-in strategies are not enough.

**Parsing options** sit in front of chunking:

- The default parser extracts text.
- The **Bedrock Data Automation** parser and the foundation-model parser handle scanned documents, tables and images, and cost extra.
- Multimodal content is chunked at the embedding level with **Nova** multimodal embeddings, in one- to thirty-second segments for audio and video.

Whichever strategy you use, keep metadata with each chunk: document, section, page and attributes. Filtering and citations depend on it. Storing whole manuals as single chunks, or splitting on character count regardless of content, are the distractors.

## Choosing and generating embeddings

An embedding model maps text to a vector. You must use the same model for indexing and querying, and if you change models you re-embed everything.

The **Bedrock** embedding models you need to know:

| Model | Input | Output | Notes |
|---|---|---|---|
| **Amazon Titan Text Embeddings V2** | Up to 8,192 tokens or 50,000 characters | 1,024 (default), 512 or 256 dimensions | Optional normalisation and **binary embeddings** for lower cost; optimised for English with multilingual support; the default choice for text RAG |
| **Amazon Titan Text Embeddings G1** | Up to 8,192 tokens | 1,536 dimensions | Earlier generation, still referenced in questions |
| **Amazon Titan Multimodal Embeddings G1** | Text (256 tokens) and images (up to 25 MB, 2048 × 2048) | 1,024, 384 or 256 dimensions | Text and image in one space: search images by text or by image |
| **Cohere Embed** | Text, many languages | 1,024 dimensions | Strong multilingual retrieval; compressed embedding types |
| **Amazon Nova Multimodal Embeddings** | Text, documents, images, video, audio | One shared space | Cross-modal retrieval in **Knowledge Bases** |

Dimensionality is a trade-off. More dimensions capture finer distinctions, which helps dense, domain-specific text such as regulatory filings, at the cost of storage, memory and query latency. Fewer dimensions are cheaper and faster, and fine for simple content. A model whose dimensionality you can choose, such as **Titan V2**, lets you test 256 against 1,024 on your own queries.

The right way to pick a model is empirical. Build a small set of domain queries with known relevant passages, embed with each candidate, and compare recall. Do not pick the smallest to save money, the newest by default, or generate several embeddings per document with different models "to be safe". And embeddings come from embedding models: extracting attention values from a text-generation model is a distractor.

Embedding models on **Bedrock** are throttled mainly by requests per minute, as the **Titan** embedding documentation describes request-based throttling, so batch generation is shaped by request count rather than token count.

**Knowledge Bases** embeds for you. If you run your own store, generate embeddings in parallel with **Lambda** functions fed from **SQS** or a **Step Functions** **Distributed Map**, with **AWS Batch**, the managed batch computing service, for very large corpora, or with **Bedrock** batch inference for embedding models. Back off on throttling and track progress in **DynamoDB**.

## Deploying vector search

The store decision is in unit 04. Here is what the query looks like on each.

With **Knowledge Bases**, retrieval configuration is declarative. You pass `numberOfResults`, `overrideSearchType` for semantic or hybrid, a metadata `filter`, an optional `rerankingConfiguration`, and an orchestration option for query decomposition, to `Retrieve` or `RetrieveAndGenerate`, or you set them on an agent's knowledge base. There is nothing to code.

With **OpenSearch**, you have two routes. You either embed the query yourself and issue a `knn` query with a filter, or you use the **Neural plugin** so **OpenSearch** embeds the text query with the connected **Bedrock** model. Hybrid queries combine a `match` clause with the `knn` clause and a search pipeline that normalises the scores. Cross-account setups, with **Bedrock** models in one account and **OpenSearch** in another, are possible through connectors and **IAM** roles.

With **Aurora PostgreSQL** and **pgvector**, the query is SQL. Order by the distance operator between the stored vector and the query vector, filter with ordinary WHERE clauses on metadata columns, and rely on an **HNSW** or **IVFFlat** index for speed. This is where multi-tenant filtering with **row-level security** is natural.

The choices map onto stems directly. A **Knowledge Base** on a managed store is the answer to "500 queries per second against 10 million documents, highly available, minimal operational overhead". **OpenSearch** is the answer to "high-dimensional embeddings, real-time indexing, fast **ANN** across millions of vectors" when the team wants the engine's controls. **pgvector** without an **ANN** index, **DynamoDB** with **Lambda** cosine similarity, and client-side search over **S3** JSON files are always wrong.

## Making results more relevant

Pure vector search finds meaning but misses exact terms: product codes, legal citations, names, rare acronyms. Pure keyword search finds terms but misses paraphrases. **Hybrid search** runs both and merges the scores, and it is the standard fix when "vector search misses keyword-specific matches while keyword search misses semantically related content".

The keyword side is usually **BM25**, the classic lexical scoring algorithm that rewards documents containing the query's terms, weighted by how rare each term is and how often it appears.

Two kinds of vector are worth naming. Embeddings are **dense** vectors, where every dimension has a value. Keyword or **sparse** vectors have a non-zero weight only for the terms present, and **OpenSearch**'s **neural sparse search** learns such sparse vectors.

In **Knowledge Bases**, **hybrid search** is available on **OpenSearch Serverless**, **Aurora** (**RDS**) and **MongoDB** stores that have a filterable text field. On **OpenSearch** clusters you build it with **BM25** plus **k-NN** and a normalisation processor.

**Reranking** is the second stage. Retrieve a generous candidate set, then let a reranker model score each candidate's relevance to the query and reorder them, so the best passage is first and only the top few go to the FM.

**Bedrock** provides reranker models, **Amazon Rerank** and **Cohere Rerank**, that you call through the `Rerank` API or configure inside `Retrieve` and `RetrieveAndGenerate`, overriding the default ranking. Reranking works on text only. It is the answer whenever "the most relevant information appears lower in the results". A custom weighted ranking function in **pgvector**, or a **SageMaker** two-stage pipeline, is the build-it-yourself distractor.

Three more relevance controls are worth knowing:

- **Metadata filtering**, covered in unit 04, removes irrelevant candidates before scoring.
- **Implicit filtering** lets **Knowledge Bases** derive filters from the query itself.
- **GraphRAG** on **Neptune Analytics** uses entity relationships to pull in connected context. **Kendra**'s **intelligent ranking** is the equivalent in the **Kendra** world.

Increasing chunk overlap, embedding every sentence separately, or raising vector dimensionality and lowering similarity thresholds do not fix relevance. They enlarge the index and add noise.

## Handling the query

Users write vague, broad or compound questions. Skill 1.5.5 transforms them before retrieval.

**Query expansion and reformulation** uses a **Bedrock** model to rewrite the question with domain terminology and synonyms, so "rules for foreign transfers" becomes "cross-border payment regulations, international wire transfer compliance requirements". That bridges the gap between how users talk and how documents are written.

**Query decomposition** splits a compound question into sub-queries, retrieves for each, and merges. **Knowledge Bases** has it built in, through the `QUERY_DECOMPOSITION` orchestration option. When you run your own pipeline, a **Lambda** function decomposes and **Step Functions** runs the sub-queries in parallel and aggregates the results.

**Query normalisation** covers punctuation, stopwords and abbreviation expansion. It makes the query embedding consistent with the index, it is cheap, and it is paired with **hybrid search** in the "slow and inconsistent retrieval" scenario.

**Semantic caching**, on **MemoryDB** or **ElastiCache** with vector search, returns a prior answer when a new query is close enough to an old one, avoiding retrieval and generation entirely for near-duplicate questions.

Recall the parts that are not query handling. Temperature does not improve retrieval, a bigger `maxTokens` does not fix missing context, and **CloudTrail** cannot analyse retrieval quality.

**Knowledge Bases** also lets you edit the prompts it uses internally. The **generation prompt template** behind `RetrieveAndGenerate` contains placeholders such as `$search_results$` for the retrieved passages and `$output_format_instructions$` for the citation and formatting rules, and editing it controls tone, citation style and answer format. The **orchestration prompt template** governs query decomposition. Changing these templates is the managed way to tune a knowledge base's answers before you reach for a custom pipeline.

## Giving models one way to retrieve

Skill 1.5.6 is about interfaces. When embeddings live in **OpenSearch**, **pgvector** and a **Knowledge Base** at once, the model should not know or care.

**Knowledge Bases as the interface.** Attach the **Knowledge Base** to a **Bedrock** agent, or call `Retrieve` and `RetrieveAndGenerate` directly. The store behind it is invisible to the caller.

**Function calling (tool use).** Define a standard tool, say `vectorSearch(query, domain, filters)`, in the `toolConfig` of a **Converse** request or as an agent **action group**. The model emits a tool call, your code routes it to the right backend, and it returns results in one standard shape of passages, sources and scores. Wrapping all backends behind an internal "retrieval gateway" API and registering that gateway as the tool is the same idea at enterprise scale.

**Model Context Protocol (MCP).** **MCP** standardises how models discover and call tools. An **MCP server** exposes each backend's search as a tool with a typed schema, and an **MCP client** in the orchestration layer lets any model or agent call it the same way.

**Bedrock AgentCore Gateway** converts existing APIs, **Lambda** functions and services into **MCP** tools behind one secure endpoint, and **Knowledge Bases** can be exposed to agents as **MCP** tools. Questions phrase this as "standardized, auditable tool access without embedding SDK calls or query syntax in prompts".

Whatever the mechanism, keep the response shape constant: passages, source identifiers, metadata and scores. Then prompts and citation logic never change when a backend does. Embedding SDK calls for each store in application code, or letting the model pick a **Lambda** by name from the prompt, are the distractors.

## Worked scenario

A heavy-equipment manufacturer builds a maintenance assistant over ten thousand service manuals. Technicians report that answers cite the right manual but the wrong procedure, that part numbers are missed, and that vague questions get inconsistent results. The retrieval half of the pipeline needs redesign.

Segmentation comes first. The manuals are long and deeply nested, with chapters, procedures and numbered steps, so the **Knowledge Base** moves from fixed-size to **hierarchical chunking**. Small child chunks give precise matches and their parent chunks supply the surrounding procedure, with overlap tuned so steps are not cut in half. The narrative troubleshooting guides use **semantic chunking** so a paragraph is not split mid-thought.

Embeddings are regenerated with **Titan Text Embeddings V2** at 1,024 dimensions, after an evaluation on a hundred technician queries shows the domain vocabulary needs the extra precision, and the corpus is embedded in parallel by **Lambda** functions fed from an **SQS** queue.

Relevance is fixed in two steps. **Hybrid search** on the **OpenSearch Serverless** store adds keyword scoring, which is what catches exact part numbers and error codes that pure vector similarity misses, and a **Bedrock** reranker re-scores the top candidates so the best procedure lands first. **Metadata filters** restrict results to the technician's equipment model and firmware version.

Queries are cleaned before embedding. A **Lambda** step expands abbreviations, and vague questions are decomposed into sub-queries by the **Knowledge Base**'s query decomposition or by a **Bedrock** prompt.

Finally the assistant needs one way to search two stores, the manuals and a separate parts database. A single search tool defined through function calling, backed by an **MCP client** that routes to the right **MCP server**, gives the model one consistent interface, and the model can invoke it mid-conversation. Retrieval quality is tracked with a labelled query set and **precision-at-k**, the share of the top k results that are relevant, in **CloudWatch**.

The exam asks this scenario in pieces: chunking strategy for nested manuals, embedding dimensionality, **hybrid search** with reranking, query handling, and one interface over several backends.

## Exam lens

- "Long manuals, nested procedures, section-level updates, precise retrieval" → **hierarchical chunking**, with parents for context, children for precision, and controlled overlap.
- "Sentences split across chunks, fragmented procedures, fixed-size today" → **semantic chunking**.
- "Dense domain text degraded with low-dimensional model, need large-scale batch embeddings" → higher-dimensional **Titan** embeddings, evaluated on domain queries, generated in parallel with **Lambda**.
- "Semantic vectors for documents and queries, store in existing **OpenSearch**, native **Bedrock**" → **Titan Text Embeddings** into **OpenSearch Service**.
- "Vector misses keywords, keyword misses meaning, need a second scoring step" → **hybrid search** plus a **Bedrock** reranker.
- "Most relevant results appear low" → **Knowledge Bases** **hybrid search** on **OpenSearch Serverless** and **Bedrock** reranker models.
- "Vague queries return inconsistent results" → **Bedrock** query expansion and **Lambda** decomposition, or built-in query decomposition.
- "Several vector stores, one consistent interface, model can invoke search during a conversation" → function calling with a standard search action backed by an **MCP client**, or **MCP** servers per backend with one tool schema.

## Knowledge check

<!-- KC: E1-Q40, E3-Q35, E1-Q3, E3-Q11, E2-Q45, E2-Q23, E1-Q14, PQ-Q11, E2-Q54, E3-Q41, E1-Q47, E1-Q1, E3-Q44 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 40

A robotics manufacturer is building an internal GenAI assistant to help technicians troubleshoot hundreds of machine models. The content includes long operational manuals, nested safety procedures, and multi-level configuration guides. Updates often affect only specific sections, and the team wants accurate retrieval without reprocessing full documents.

Which document segmentation approach BEST meets these requirements?

- **A)** Store each manual as a single chunk to preserve full document context.
- **B)** Use semantic chunking with no overlap so content is split solely at natural boundaries.
- **C)** Use fixed-size chunking with a uniform 1200-token limit and 25 percent overlap across all documents.
- **D)** Use hierarchical chunking with large parent chunks for chapter context and smaller child chunks for precise retrieval, with controlled overlap for continuity.

<details><summary>Answer</summary>

**Answer: D.** Hierarchical chunking keeps large parent chunks for chapter context and small child chunks for precise matches, with overlap for continuity, which suits long manuals with nested procedures and section-level updates. Single-chunk documents lose precision, semantic chunking without overlap loses continuity, and uniform fixed-size chunks ignore the document structure.

*Where this is covered: Unit 05, Segmenting documents. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 3, question 35

A biotechnology company is developing a RAG-based assistant to help researchers query internal laboratory protocols, chemical safety sheets, and experiment diagrams stored in Amazon S3. The retrieval layer uses Amazon Bedrock Knowledge Bases with embeddings stored in S3 Vectors to reduce storage and retrieval costs.

During testing, scientists report inconsistent answers: relevant sentences are split across multiple chunks, diagrams lose explanatory context, and multi-step procedures appear fragmented. The ingestion workflow currently uses a rigid fixed-size chunking strategy.

The team also preprocesses scanned lab manuals with Amazon Textract via Amazon SageMaker AI, and uses a Bedrock foundation model to answer questions based on retrieved chunks. The organization wants to improve retrieval coherence, maintain relevance for multi-sentence scientific explanations, and avoid unnecessary cost increases.

Which configuration best satisfies the requirements?

- **A)** Enable hierarchical chunking by generating both macro-level and micro-level chunks and indexing all variations for retrieval.
- **B)** Activate semantic chunking in the Bedrock Knowledge Base and adjust chunk parameters so chunks are formed based on meaning rather than fixed sizes.
- **C)** Use a larger Bedrock model with an extended context window and pre-summarize all documents using recursive summarization workflows before ingestion.
- **D)** Remove chunking and ingest each document as a single chunk, relying on the foundation model’s long-context window to interpret large inputs.

<details><summary>Answer</summary>

**Answer: B.** Semantic chunking forms chunks on meaning rather than fixed size, keeping multi-sentence explanations and multi-step procedures together, and it works within the existing Knowledge Base. Hierarchical chunking is not recommended with S3 Vectors because parent-child metadata hits its size limit, pre-summarising with a larger model adds cost, and single-chunk documents lose precision.

*Where this is covered: Unit 05, Segmenting documents. Key: ours, confidence high.*

</details>

### 3. Exam 1, question 3

A financial analytics company is building a semantic search engine that indexes regulatory filings, compliance checklists, and legal summaries. The documents vary significantly in length, and the team observed degraded retrieval quality when using a low-dimensional embedding model. The lead AI engineer needs an embedding approach that improves semantic precision for dense, domain-specific text while supporting large-scale batch generation of embeddings.

Which solution BEST meets these requirements?

- **A)** Generate embeddings during inference using a Bedrock text model instead of a dedicated embedding model.
- **B)** Use Amazon Titan high-dimensional embeddings and batch-generate vectors with a Lambda-based parallel processing workflow.
- **C)** Use a lightweight embedding model with reduced dimensionality to minimize storage and compute costs.
- **D)** Use semantic chunking with a breakpoint threshold and rely on a fixed 768-dimension embedding model for all documents.

<details><summary>Answer</summary>

**Answer: B.** Dense domain text needs higher dimensionality for semantic precision, and Titan embeddings let you choose it; Lambda-based parallel generation handles large-scale batch embedding. A text-generation model does not produce embeddings, lower dimensionality worsens the stated problem, and semantic chunking does not fix a weak embedding model.

*Where this is covered: Unit 05, Choosing and generating embeddings. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 4. Exam 3, question 11

A large compliance-monitoring firm is developing a semantic search engine that retrieves regulatory documents, legal notes, and analyst summaries. The platform uses Amazon Bedrock for FM operations and must generate high-quality embeddings that work across multiple document types. The engineering team needs an embedding solution that balances dimensionality, search latency, and accuracy. They also want a scalable method to batch-generate embeddings for millions of documents without overwhelming downstream vector indexing jobs. The solution must require minimal custom infrastructure.

Which solution will BEST meet these requirements?

- **A)** Use Amazon Bedrock text generation FMs to produce embeddings by extracting the model’s intermediate attention values, and ingest those into OpenSearch without batching.
- **B)** Use a custom fine-tuned embedding model deployed on Amazon SageMaker AI large GPU instances, generate embeddings synchronously inside the ingestion API, and store all vectors directly in an Aurora PostgreSQL DB instance.
- **C)** Use AWS Glue jobs with PyTorch scripts to run custom embedding models periodically and store the vectors in DynamoDB without testing dimensional suitability.
- **D)** Use Amazon Titan Embeddings with a dimensionality that matches domain retrieval needs, evaluate embedding model performance using Bedrock benchmarking tools, and use AWS Lambda with batching to generate embeddings at scale.

<details><summary>Answer</summary>

**Answer: D.** Titan Embeddings with a dimensionality matched to retrieval needs, evaluated with Bedrock benchmarking, and generated at scale by Lambda with batching balances dimensionality, latency, accuracy and infrastructure. Attention values from a generation model are not embeddings, synchronous GPU endpoints inside the ingestion API do not scale, and untested Glue PyTorch jobs into DynamoDB skip suitability testing.

*Where this is covered: Unit 05, Choosing and generating embeddings. Key: ours, confidence high.*

</details>

### 5. Exam 2, question 45

A global law firm is building an AI-powered knowledge assistant to help attorneys search, summarize, and cross-reference legal documents. The team already uses Amazon SageMaker Ground Truth to label case summaries and enrich document metadata.

The next phase introduces Amazon Bedrock agents, which must interpret attorney queries, summarize large legal filings, and provide context-aware recommendations. To support this, the solution must generate high-quality semantic embeddings for both queries and documents so the agent can retrieve relevant content during RAG workflows.

The firm requires a fully managed and scalable approach that integrates natively with Bedrock and supports storing embeddings in an existing OpenSearch cluster used for legal document indexing.

Which approach best satisfies these requirements?

- **A)** Leverage Amazon Titan Text Embeddings in Bedrock to convert legal documents and queries into semantic vectors and store them in Amazon OpenSearch Service for retrieval-augmented reasoning by Bedrock agents.
- **B)** Deploy a fine-tuned model in SageMaker JumpStart to generate document summaries and connect the model output to the Bedrock agent using Lambda integration.
- **C)** Use Amazon Kendra to index legal documents and allow AI agents to query them directly using built-in natural-language search and ranking capabilities.
- **D)** Use SageMaker Data Wrangler to cluster legal text into feature groups and let agents analyze similarities using the structured dataset created during preprocessing.

<details><summary>Answer</summary>

**Answer: A.** Amazon Titan Text Embeddings in Bedrock generates semantic vectors for documents and queries in a fully managed way, and storing them in the existing OpenSearch Service cluster gives the agents their retrieval layer. A JumpStart summariser, Kendra indexing, and Data Wrangler clustering do not produce embeddings for the firm's OpenSearch index.

*Where this is covered: Unit 05, Choosing and generating embeddings. Key: ours, confidence high.*

</details>

### 6. Exam 2, question 23

A global consulting firm is building an internal generative AI assistant that retrieves policy documents, audit checklists, and architectural playbooks to enhance Bedrock-based RAG responses. The data sources contain inconsistent terminology, older documents with sparse keywords, and highly structured procedure manuals. The AI engineering team reports that pure vector search misses important keyword-specific matches, while pure keyword search fails to surface semantically related content. They also need a secondary scoring step to prioritize the most contextually relevant passages before sending them to the foundation model.

Which retrieval architecture BEST satisfies these requirements?

- **A)** Use DynamoDB queries for keyword filtering and store embeddings in a separate S3 bucket for client-side vector comparison.
- **B)** Use Amazon Bedrock Knowledge Bases with keyword-only retrieval and increase chunk overlap to improve matching.
- **C)** Use Amazon Aurora PostgreSQL with pgvector and rely exclusively on vector similarity scoring.
- **D)** Use OpenSearch with hybrid search that combines BM25 keyword scoring and vector embeddings, followed by a Bedrock reranker model to rescore the top candidates.

<details><summary>Answer</summary>

**Answer: D.** Hybrid search in OpenSearch combines BM25 keyword scoring with vector similarity so both exact terms and semantic matches surface, and a Bedrock reranker rescoring the top candidates supplies the required secondary relevance step. DynamoDB keyword filtering with client-side vectors, keyword-only Knowledge Base retrieval, and vector-only pgvector each miss one side of the requirement.

*Where this is covered: Unit 05, Making results more relevant. Key: ours, confidence high.*

</details>

### 7. Exam 1, question 14

A logistics technology company is building a RAG application on Amazon Bedrock to help support agents troubleshoot shipment issues. The application retrieves many relevant documents, but agents report that the most useful information often appears low in the results list. The company wants to boost semantic relevance so high-value documents appear first. The team wants a solution that avoids custom ranking algorithms and minimizes operational overhead while staying within its Bedrock-based architecture.

Which combination of steps will MOST effectively improve the relevance of retrieved results with minimal operational overhead? (Select TWO.)

- **A)** Configure an Amazon Aurora PostgreSQL cluster with pgvector to store embeddings and implement a custom weighted ranking function using metadata and cosine similarity.
- **B)** Build a custom SageMaker inference pipeline that merges BM25 keyword scoring with embedding-based similarity for a two-stage retrieval system.
- **C)** Use Amazon Bedrock reranker models with Amazon OpenSearch Service to reorder retrieved documents based on semantic similarity to the agent's query.
- **D)** Use Bedrock Knowledge Bases with hybrid search and Amazon OpenSearch Serverless to combine keyword relevance with semantic vector embeddings for improved ranking.
- **E)** Use Amazon S3 inventory reports to generate a frequency-based scoring model that prioritizes documents with higher access patterns.

<details><summary>Answer</summary>

**Answer: C, D.** Bedrock reranker models reorder retrieved chunks by semantic relevance, and Knowledge Bases hybrid search on OpenSearch Serverless blends keyword and vector scores; both are managed and stay in the Bedrock architecture. Custom pgvector ranking and a SageMaker BM25 pipeline are custom ranking algorithms the question excludes; S3 inventory access frequency is not relevance.

*Where this is covered: Unit 05, Making results more relevant. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 8. Official practice question set, question 11

A company is developing a RAG application by using Amazon Bedrock. The application processes customer support documents. Initially, the application retrieves many relevant documents. However, users report that the most relevant information often appears lower in the results. The company wants to improve the relevance ranking of retrieved results to ensure that the most useful information appears first.

Which combination of steps will improve the relevance of retrieved results with MINIMAL operational overhead? **(Select TWO)**

- **A)** Use Amazon SageMaker JumpStart FMs with Amazon Kendra Intelligent Ranking to create custom relevancy scoring algorithms.
- **B)** Use Knowledge Bases with hybrid search capabilities and Amazon OpenSearch Serverless to combine vector embeddings with keyword matching.
- **C)** Create an Amazon Aurora PostgreSQL database with the pgvector extension to store document embeddings. Create a similarity scoring algorithm that combines vector distances with document metadata to rank results.
- **D)** Use Amazon Bedrock reranker models with Amazon OpenSearch Service to reorder retrieved results based on semantic relevance to the query.
- **E)** Configure Amazon OpenSearch Serverless with the Amazon Bedrock Knowledge Bases plugin. Use OpenSearch's Learning to Rank feature for relevance scoring. Integrate relevance scoring with Knowledge Bases for result reranking.

<details><summary>Answer</summary>

**Answer: B, D.** Knowledge Bases hybrid search on OpenSearch Serverless combines vector similarity with keyword matching, and Bedrock reranker models with OpenSearch reorder results by semantic relevance, both managed and low overhead. Kendra Intelligent Ranking with JumpStart, a custom pgvector scoring algorithm, and a Learning-to-Rank integration are custom or higher-overhead paths.

*Where this is covered: Unit 05, Making results more relevant. Key: AWS official answer.*

</details>

### 9. Exam 2, question 54

A global research firm is building a retrieval-augmented generation (RAG) system on Amazon Bedrock to support analysts who query large volumes of scientific papers. Analysts report that retrieval is sometimes slow and the relevance of returned passages is inconsistent. A GenAI engineer must enhance both retrieval speed and the quality of retrieved context before it is sent to the foundation model.

Which combination of steps will MOST effectively meet these requirements?

- **A)** Increase the number of vectors stored in the index by embedding every sentence separately, regardless of semantic similarity.
- **B)** Preprocess incoming queries by normalizing punctuation, removing stopwords, and expanding abbreviations to improve embedding consistency before vector retrieval.
- **C)** Use CloudTrail Lake queries to analyze retrieval timing and manually adjust index shards each week to maintain performance.
- **D)** Route all retrieval queries directly to the foundation model and rely on FM reasoning to determine the most relevant documents.
- **E)** Implement a hybrid search pipeline in Amazon OpenSearch Serverless that combines vector search with BM25 keyword scoring, and apply custom ranking weights based on document type.

<details><summary>Answer</summary>

**Answer: B, E.** Normalising queries (punctuation, stopwords, abbreviations) produces consistent embeddings, and a hybrid pipeline in OpenSearch Serverless that combines vector search with BM25 and document-type weights improves both relevance and speed. Embedding every sentence bloats the index, CloudTrail Lake cannot tune shards, and routing all queries to the FM removes retrieval entirely.

*Where this is covered: Unit 05, Handling the query. Key: ours, confidence high.*

</details>

### 10. Exam 3, question 41

A global consulting firm is building an AI-powered knowledge analytics platform. The platform must process large volumes of internal reports, extract insights, and answer employee questions with conversational responses. The solution must use a foundation model (FM) from Amazon Bedrock for inference and Amazon SageMaker AI for preprocessing tasks such as document chunking, embedding generation, and metadata extraction.

The compliance team requires that no model training or fine-tuning occur in the architecture. In addition, the system must support hybrid retrieval (semantic + keyword search), run fully within a private VPC environment, and scale automatically with increasing employee traffic. The architecture must minimize operational overhead while ensuring consistent latency for inference requests.

Which architectural approach BEST meets these requirements?

- **A)** Use Amazon SageMaker AI to host the FM in a custom inference container and integrate with Amazon Kendra for hybrid search. Configure autoscaling by adding additional GPU-based SageMaker endpoints as traffic increases.
- **B)** Use Amazon Bedrock Knowledge Bases with a vector store in Amazon OpenSearch Serverless for hybrid search. Run SageMaker preprocessing jobs in a private VPC, and expose a single Bedrock inference endpoint for employee queries routed through an API Gateway in the VPC.
- **C)** Deploy a multi-model SageMaker endpoint hosting several fine-tuned versions of an FM. Use Route 53 latency-based routing to direct employee queries to the lowest-latency model endpoint in each Region.
- **D)** Use Amazon Bedrock for both preprocessing and inference. Replace SageMaker entirely to reduce architectural complexity and use managed Bedrock pipelines for chunking and metadata extraction.

<details><summary>Answer</summary>

**Answer: B.** Knowledge Bases with an OpenSearch Serverless vector store provides hybrid semantic and keyword search with no training, SageMaker preprocessing jobs run in the private VPC, and a single Bedrock inference path behind API Gateway scales automatically with consistent latency and minimal operations. Hosting the FM on SageMaker with Kendra adds GPU management, multi-model fine-tuned endpoints violate the no-fine-tuning rule, and Bedrock does not replace SageMaker preprocessing jobs.

*Where this is covered: Unit 05, Making results more relevant. Key: ours, confidence high.*

</details>

### 11. Exam 1, question 47

A machine learning team at a financial analytics firm is building a GenAI assistant that retrieves regulatory guidance, compliance summaries, and historical interpretations from a large vector store. Users often submit vague or incomplete queries such as "rules for foreign transfers", which return inconsistent results across departments. The team needs a retrieval workflow that can automatically expand ambiguous queries, break them into structured components, and transform them into domain-aligned search intents before performing vector search.

Which retrieval enhancement approach should the team implement to meet these requirements?

- **A)** Use Amazon Aurora with pgvector and rely on a larger embedding chunk overlap to compensate for vague user queries.
- **B)** Use Step Functions to run multiple sequential keyword searches against Amazon S3 and merge the results before embedding generation.
- **C)** Use Amazon Bedrock to perform query expansion and generate domain-specific reformulations, then use a Lambda function to decompose the expanded query into sub-queries before passing them to the vector search engine.
- **D)** Use OpenSearch with a larger vector dimensionality and lower similarity threshold to increase recall for ambiguous queries.

<details><summary>Answer</summary>

**Answer: C.** Using a Bedrock model to expand and reformulate vague queries into domain-aligned intents, then decomposing them into sub-queries in Lambda before vector search, is the query-handling pattern in the task statement. Larger chunk overlap, keyword searches against S3, and lower similarity thresholds add noise rather than understanding the query.

*Where this is covered: Unit 05, Handling the query. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 12. Exam 1, question 1

A biomedical research company is developing an internal GenAI assistant that retrieves experiment logs, laboratory protocols, safety guidelines, and molecular datasets from multiple vector stores. The data resides in Amazon OpenSearch Service for semantic search, Aurora PostgreSQL with pgvector for structured embeddings, and an Amazon Bedrock Knowledge Base that stores scientific summaries. The engineering team wants foundation models to query all sources consistently through a single interface, without exposing the underlying storage differences. They also need a mechanism that allows FMs to invoke vector search actions programmatically during a conversation.

Which integration approach should they implement to provide a unified, consistent access mechanism for all vector retrieval operations?

- **A)** Use OpenSearch cross-cluster search to unify all vector retrieval needs across the different storage systems.
- **B)** Use Amazon Bedrock function calling to define a standardized "vectorSearch" action that routes search requests to the appropriate backend, supported by an MCP client to manage multi-store vector queries.
- **C)** Use Step Functions to orchestrate keyword searches across OpenSearch and Aurora, then concatenate the results before sending them to the model.
- **D)** Use Lambda functions to batch-retrieve embeddings from all vector databases simultaneously to increase retrieval speed.

<details><summary>Answer</summary>

**Answer: B.** A standard function-calling action such as vectorSearch gives every model one interface, and an MCP client behind it routes to OpenSearch, pgvector or the Knowledge Base without exposing storage differences; the model can invoke it mid-conversation. Cross-cluster search only spans OpenSearch clusters, Step Functions keyword searches and Lambda batch retrieval are not model-callable interfaces.

*Where this is covered: Unit 05, Giving models one way to retrieve. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 13. Exam 3, question 44

A global logistics company is building a retrieval-augmented assistant that answers questions about shipment status, contracts, and warehouse procedures. The data science team uses multiple vector backends (Amazon OpenSearch Service, Amazon Aurora with pgvector, and a managed Bedrock Knowledge Base) across different business units. The GenAI lead wants a consistent way for foundation models to perform vector search regardless of which backend stores the embeddings. The solution must provide a stable access pattern for the FM, support future backend changes with minimal code impact, and integrate cleanly with existing Bedrock-based agents.

Which combination of approaches will BEST provide consistent access mechanisms for FM retrieval augmentation?

- **A)** Embed direct OpenSearch, Aurora pgvector, and Bedrock Knowledge Base SDK calls into the FM application code. Use conditional logic to select the correct SDK based on the tenant and region.
- **B)** Expose all vector backends through an internal “retrieval gateway” service that offers a single standardized HTTP API. Register this gateway as a tool for the FM by using function calling, so the model always invokes the same retrieval interface.
- **C)** Use separate Lambda functions for each vector backend, each with its own custom request/response shape. Allow the FM to select which Lambda function to call by passing the function name in the user prompt.
- **D)** Implement Model Context Protocol (MCP) servers for each vector backend and use an MCP client in the FM orchestration layer. Standardize retrieval tool schemas so the FM always issues the same query structure, regardless of backend.

<details><summary>Answer</summary>

**Answer: B, D.** The question asks for a combination, and two options describe consistent access mechanisms: a retrieval gateway with one standardised API registered as a function-calling tool, and MCP servers per backend with a standardised tool schema and an MCP client in the orchestration layer. Both hide the backend from the model and survive backend changes. Direct SDK calls with conditional logic and per-backend Lambda functions chosen from the prompt couple the model to storage. If forced to pick one, the MCP design is the most standardised.

*Where this is covered: Unit 05, Giving models one way to retrieve. Key: ours, confidence medium.*

</details>

<!-- KC-END -->

## Summary

Retrieval quality decides RAG quality.

Chunk to fit the content: **fixed-size** for uniform text, **hierarchical** for structured manuals, **semantic** for explanations that must stay whole, and **custom Lambda chunking** for anything structure-aware. Keep metadata on every chunk.

Embed with a model chosen on domain test queries, with the dimensionality your accuracy needs, using the same model for index and query, generated in parallel or by **Knowledge Bases**.

Query the store you chose in unit 04, using **hybrid search** when exact terms matter and a **Bedrock** reranker to put the best passage first. Rewrite queries with an FM, decompose compound ones, normalise them, and cache semantically similar ones.

Expose retrieval through **Knowledge Bases**, a standard function-calling tool, or **MCP**, so models see one interface no matter where the vectors live.
