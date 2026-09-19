# Exam 3

> AWS Certified Generative AI Developer – Professional | 70 questions across 5 domains
> Source: ExamPro Practice Exam 3 (questions captured before attempting; not yet graded)

## QUESTIONS

**Q1.** A financial technology enterprise is modernizing its analytics and customer-engagement platforms. As part of this transformation, the organization is integrating Amazon Bedrock with Amazon SageMaker pipelines to support a new conversational AI system capable of processing regulated financial data. The AI system will respond to customer inquiries, summarize account-level insights, and provide guidance about financial products. The security team requires strict prevention of harmful output, elimination of unauthorized sensitive data disclosures, and automated detection and blocking of any content that could indicate potential illegal activity. The solution must require the least engineering effort while providing a fully managed compliance layer.

Which solution will meet these requirements with the MINIMAL effort?

A) Use Amazon Macie to scan model responses for sensitive information, trigger Amazon SNS alerts for possible illegal activity, and apply basic prompt constraints in Bedrock to reduce harmful output.

B) Configure generic safe-completion settings in Bedrock Guardrails to intercept harmful or restricted content, use AWS WAF rules to block prohibited content, and trigger an AWS Lambda function from CloudWatch alarms to review sensitive responses.

C) Use SageMaker Clarify reports to detect unsafe response patterns, rely on prompt-level instructions to limit exposure of sensitive data, and use CloudWatch metric filters to flag interactions indicating potential illegal content.

D) Configure content filters in Amazon Bedrock Guardrails to detect and block harmful or restricted content, define word-blocking rules for illegal or prohibited terms, and enable contextual grounding to prevent disclosure of sensitive financial information.

---

**Q2.** A global research institute is building a retrieval-augmented question-answering system on AWS. Documents are stored in Amazon S3 and indexed into a vector store that is used to augment prompts for a foundation model. Researchers need to filter results by publication date, project code, author, and confidentiality level so that the FM receives only context that is relevant to the query and appropriate for the user’s access level. The solution must improve search precision and context awareness with minimal custom logic in the application layer.

Which solution BEST meets these requirements?

A) Define a standardized metadata schema for all documents. Store publication date, project code, author, and confidentiality level as S3 object tags and user-defined metadata. Ensure the ingestion pipeline maps these attributes into structured fields in the vector store index and uses them as filters and boost signals during retrieval.

B) Derive metadata on the fly from S3 object keys by parsing folder names and file-name patterns in the application code. Pass the parsed values into the FM prompt so the model can decide which documents are relevant.

C) Embed all metadata as plain text at the beginning of each document body before generating embeddings, and rely solely on vector similarity search without separate metadata fields or filters.

D) Use Amazon CloudTrail data events on the S3 bucket to infer which documents are most frequently accessed, and treat access frequency as an implicit relevance signal for all future queries.

---

**Q3.** A global technology advisory firm is deploying a generative AI research assistant that performs semantic retrieval across hundreds of millions of embeddings derived from whitepapers, patents, interview transcripts, architecture diagrams, and internal engineering notes. The retrieval layer must support extremely fast vector similarity search, domain-specific query routing, and high availability during large-scale ingestion spikes.

The AI platform team needs a vector database architecture that optimizes semantic retrieval performance while supporting both domain specialization and distributed scaling across multiple nodes.

Which architecture BEST meets these requirements?

A) Use Amazon OpenSearch Service with the Neural plugin, implement sharding strategies to distribute large embedding sets across nodes, and create multiple specialized indexes (e.g., patents, interviews, architecture docs) to improve query routing and retrieval precision.

B) Store all embeddings in a single OpenSearch index with the minimum number of shards to simplify coordination and rely exclusively on similarity scoring for all queries.

C) Place all embeddings in a single Amazon RDS instance and run cosine similarity calculations using SQL stored procedures.

D) Use DynamoDB as the primary vector store, store embeddings as binary attributes, and perform similarity search through a custom Lambda function.

---

**Q4.** A company is developing a customer support chatbot using Amazon Bedrock. The chatbot must answer high-volume simple product inquiries as well as more complex reasoning-based questions. About 75% of all incoming queries are simple (“What is the warranty?”), while 25% require advanced reasoning (“Compare two products and recommend one based on my usage pattern”). The solution must minimize cost, reduce operational burden, and preserve high-quality responses across both query types. The company also integrates Amazon Comprehend to analyze sentiment so the bot can adjust tone and detect customer frustration.

Which approach best meets these requirements?

A) Implement a hybrid system that uses Amazon Lex to answer simple inquiries and invokes Bedrock only for complex queries. Maintain FAQ responses in Amazon S3 and use CloudWatch analytics to tune routing logic manually.

B) Deploy Bedrock using fully provisioned throughput for all queries and store frequently asked questions in Amazon ElastiCache (Redis OSS) with TTL-based caching to reduce model invocation counts.

C) Use Amazon SageMaker AI to fine-tune a Claude Sonnet model using chat logs, and integrate Amazon Kendra retrieval to improve information grounding for both simple and complex customer questions.

D) Leverage Bedrock’s intelligent prompt routing to send simple questions to Claude Haiku for low-cost inference, and automatically escalate complex reasoning queries to Claude Sonnet. This reduces cost while maintaining response quality and requires minimal operational overhead.

---

**Q5.** A fintech startup is building several domain-specific variants of a foundation model (FM) for tasks such as regulatory report drafting, fraud-case summarization, and customer-chat assistance. The team fine-tunes base models on Amazon SageMaker AI by using LoRA adapters and wants to promote only validated versions into production. They must standardize how new FM variants are registered, approved, deployed to SageMaker endpoints, and rolled back if issues are detected. They also need a repeatable mechanism to deprecate older variants and retire them without breaking clients that call the production endpoint. The team wants to minimize manual operations and ensure consistent behavior across multiple environments (dev, staging, prod).

Which combination of steps will provide a standardized and automated FM customization lifecycle? (Select TWO.)

A) Create an automated CI/CD pipeline by using SageMaker Pipelines and AWS CodePipeline that pulls the latest Approved model versions from SageMaker Model Registry, deploys them with blue/green or canary strategies to SageMaker endpoints, monitors CloudWatch alarms, and rolls back to the previous version on failures. Tag deprecated model versions for retirement and remove them on a scheduled basis.

B) Manually update SageMaker endpoint configurations whenever a new FM variant is trained. Track model versions in a shared spreadsheet and perform rollback by redeploying the previous model artifact from Amazon S3 as needed.

C) Use SageMaker Model Registry to register every fine-tuned FM variant with versioned packages, approval status (for example, Pending, Approved, Rejected), and metadata such as domain, LoRA config, and training dataset identifiers. Promote only Approved versions to production.

D) Use Amazon Bedrock provisioned throughput configurations for all domain-specific FMs and rely on manual prompt-level flags to distinguish between fraud, regulatory, and customer-chat use cases instead of maintaining separate model versions.

E) Store LoRA adapter weights exclusively in Amazon S3 with timestamped folder names. Use an AWS Lambda function that selects the adapter with the most recent timestamp at runtime and loads it into the model container without any registry or approval workflow.

---

**Q6.** A company is developing a generative AI assistant that summarizes customer interactions, composes personalized emails, and provides account recommendations. CRM data and support logs are stored in Amazon S3. The team uses Amazon Comprehend to extract sentiment and entities, and Amazon SageMaker AI to train engagement-scoring models. The pipeline must continuously ingest fresh CRM data, enrich it with Comprehend, combine it with SageMaker outputs, and feed it automatically into foundation model workflows—without ongoing manual ETL work.

Which approach offers the most scalable and reliable method for automating the CRM data processing pipeline?

A) Use Amazon EventBridge to trigger AWS Lambda functions whenever new CRM data is added to S3. Set up a Lambda function to preprocess the data, call Comprehend for sentiment analysis, and push the output to SageMaker AI for model retraining.

B) Use Amazon Bedrock Data Automation to continuously ingest CRM data from S3. Apply preprocessing, including sentiment and entity extraction with Comprehend, and automatically load the enriched data into retraining pipelines for SageMaker AI and foundation models.

C) Connect to CRM data using SageMaker Data Wrangler, perform transformations, and analyze text with Comprehend. Run SageMaker AI training jobs separately and manually trigger foundation model retraining in Amazon Bedrock.

D) Export CRM data to S3 every week, run a SageMaker Notebook to transform the data, call Comprehend, and feed the output into the foundation model retraining.

---

**Q7.** A digital media startup is building an AI-powered article-ranking engine that analyzes user reading history, sentiment scores from Amazon Comprehend, and engagement metrics stored in Amazon S3. The company has trained several Amazon SageMaker AI recommendation models and wants to evaluate which one produces the best personalization outcomes. The engineering team needs to route real-time inference traffic across multiple model variants, collect click-through metrics, compare model performance, and seamlessly shift 100% of traffic to the top-performing model—without managing custom infrastructure.

Which solution will meet these requirements with the least operational overhead?

A) Launch separate Amazon EC2 instances for each model version behind a Network Load Balancer (NLB) and manually update NLB target weights based on click-through performance.

B) Use Amazon SageMaker AI multi-variant endpoints to host all candidate models under a single endpoint, assign traffic weights for A/B testing, and update routing to direct all inference requests to the winning model.

C) Configure Amazon API Gateway to distribute inference traffic across multiple SageMaker endpoints with weighted rules, then adjust the weights as engagement metrics change.

D) Use AWS CodeDeploy blue/green deployments to alternate traffic between model versions and rely on CodeDeploy weighted routing to gradually shift traffic toward the higher-performing model.

---

**Q8.** A global software vendor is building a compliance research assistant that uses Amazon SageMaker AI to prepare domain-specific context documents and Amazon Bedrock for real-time conversational analysis. Each user query includes a long regulatory handbook that rarely changes, followed by short user questions. The handbook is included in every inference request, causing growing latency and token-processing costs. The architects want to avoid repeatedly reprocessing the static handbook text while still allowing dynamic, question-specific responses.

Which solution should the team implement to optimize performance and reduce cost?

A) Shorten the system prompt by removing the handbook entirely and move the handbook into a database that Bedrock queries dynamically at inference time.

B) Pre-encode the handbook into embeddings in SageMaker AI and send only the embeddings plus the user question into Bedrock to reduce the runtime input size.

C) Enable prompt caching in Bedrock so the static handbook section is cached as a prefix and reused across subsequent invocations, allowing only the user’s query to be processed each time.

D) Enable SageMaker AI model instance caching by using provisioned instance warm pools so the model retains the handbook context in memory across calls.

---

**Q9.** A global HR software provider is developing an internal GenAI assistant that uses Amazon Bedrock to generate policy summaries, hiring guidance, and structured HR workflows. The company wants consistent responses across departments and must ensure that the assistant always follows strict behavioral rules, such as role-specific tone, compliance-aligned phrasing, and prohibited-topic restrictions. The AI team also needs a centralized mechanism to maintain prompt templates and enforce these constraints across multiple applications built by different engineering groups.

Which solution will MOST effectively enforce consistent instructions and safe behavior across all FM interactions?

A) Embed custom instructions directly into each application’s source code so that each development team maintains its own prompt formatting logic.

B) Use Amazon Bedrock Prompt Management to define reusable system-prompt templates with role, formatting, and style requirements. Apply Amazon Bedrock Guardrails to enforce behavioral constraints and restricted-topic policies across all applications.

C) Allow each application to generate prompts dynamically based on user input and rely on model temperature settings to control output consistency.

D) Use AWS Lambda layers to store instruction text blocks and require developers to import them at runtime to standardize FM prompts.

---

**Q10.** A multinational insurance provider is building a suite of generative AI applications across multiple business units. Each team uses Amazon Bedrock for FM inference and Amazon SageMaker AI for data preparation and prompt-evaluation workflows. Leadership wants to eliminate inconsistent implementations and enforce a uniform, repeatable pattern for model invocation, retrieval-augmented generation (RAG), and shared security controls. The architecture must comply with the AWS Well-Architected Framework and the Generative AI Lens.

The cloud platform team must create standardized, reusable components that every team can adopt without rewriting integration logic. The components must enforce consistent guardrail usage, validated API patterns, and centralized logging while enabling each business unit to deploy independently.

Which approach MOST effectively provides standardized, enterprise-wide GenAI components?

A) Build a single global Amazon Bedrock prompt router and require all teams to send requests through it so the enterprise can standardize all FM outputs.

B) Create reusable Bedrock inference wrappers, prompt-evaluation modules, and RAG integration templates published in an internal AWS Service Catalog portfolio that development teams can deploy consistently across environments.

C) Require each team to independently run the AWS WA Tool Generative AI Lens and manually update their services to align with architectural best practices.

D) Deploy a central SageMaker multi-model endpoint shared across all business units to enforce consistent model invocation patterns and ensure identical architecture usage across departments.

---

**Q11.** A large compliance-monitoring firm is developing a semantic search engine that retrieves regulatory documents, legal notes, and analyst summaries. The platform uses Amazon Bedrock for FM operations and must generate high-quality embeddings that work across multiple document types. The engineering team needs an embedding solution that balances dimensionality, search latency, and accuracy. They also want a scalable method to batch-generate embeddings for millions of documents without overwhelming downstream vector indexing jobs. The solution must require minimal custom infrastructure.

Which solution will BEST meet these requirements?

A) Use Amazon Bedrock text generation FMs to produce embeddings by extracting the model’s intermediate attention values, and ingest those into OpenSearch without batching.

B) Use a custom fine-tuned embedding model deployed on Amazon SageMaker AI large GPU instances, generate embeddings synchronously inside the ingestion API, and store all vectors directly in an Aurora PostgreSQL DB instance.

C) Use AWS Glue jobs with PyTorch scripts to run custom embedding models periodically and store the vectors in DynamoDB without testing dimensional suitability.

D) Use Amazon Titan Embeddings with a dimensionality that matches domain retrieval needs, evaluate embedding model performance using Bedrock benchmarking tools, and use AWS Lambda with batching to generate embeddings at scale.

---

**Q12.** A global pharmaceutical research lab is developing an autonomous multi-agent system that assists scientists in synthesizing compound hypotheses, retrieving experiment history, and coordinating lab tooling. The system uses several specialized agents—one for literature search, one for chemical reasoning, and one for experiment planning. The engineering team needs the system to preserve long-term scientific context, maintain state across multi-step tasks, and reliably pass shared memory between agents without manually coding state synchronization for every interaction.

The solution must minimize custom infrastructure, support tool integrations, and allow agents to read/write shared memory during extended workflows.

Which solution will BEST meet these requirements?

A) Use AWS Lambda to store agent memory snapshots in Amazon DynamoDB and manually pass the memory object to each agent during invocation.

B) Use Strands Agents with built-in memory modules and integrate MCP tools for shared context access, enabling multi-agent state management without custom synchronization logic.

C) Store scientific context in Amazon S3 using versioned JSON documents and have each agent fetch and update the memory file at the start and end of every task.

D) Deploy each agent as a container in Amazon ECS and mount a shared Amazon EFS file system to store session memory that all containers read from and write to.

---

**Q13.** A multinational museum consortium is modernizing its digital archive system to support intelligent search across decades of historical photographs, recorded interviews, documentary videos, handwritten field notes, and translated manuscripts stored in Amazon S3. The machine learning engineering team uses Amazon Bedrock AgentCore for workflow orchestration, while Amazon SageMaker AI handles batch transformations for existing structured datasets.

The curation staff—who are not ML specialists—must rapidly enable automated tagging and categorization of the newly ingested multimodal content without training any custom models, building pipelines, or managing compute infrastructure. The organization needs accurate cross-modal tagging to support entity search (people, locations, objects, dates), language detection, audio transcription, and image classification. The solution must integrate cleanly with AgentCore and be immediately usable by non-technical archivists.

Which approach provides the fastest, lowest-overhead method to automatically analyze and tag all multimedia assets?

A) Leverage Amazon Comprehend, Amazon Transcribe, and Amazon Rekognition to automatically extract entities, speech transcripts, and image metadata for multimodal tagging across the media library.

B) Deploy a farm of containerized inference jobs on AWS Batch to run open-source OCR, audio feature extraction, and custom clustering algorithms across the media archive.

C) Convert the audio files with Amazon Transcribe and then train a SageMaker Neural Topic Model (NTM) and custom object-detection model to create topic and entity tags for the new media content.

D) Configure Amazon Translate, Amazon Polly, and Amazon Lex to convert recorded interviews into multilingual conversational transcripts for use in metadata generation.

---

**Q14.** A global insurance provider is developing a claims-analysis assistant using Amazon Bedrock to help employees summarize claim notes, extract key details, and generate customer responses. During testing, the team discovers that malicious users occasionally modify input text to inject harmful instructions and cause the FM to produce unauthorized financial recommendations. Additionally, compliance officers require a secondary safeguard to validate all FM outputs before they reach end users, ensuring the system cannot accidentally produce disallowed advice or internal policy violations.

The company must design a defense-in-depth safety system that prevents misuse through multiple independent safety layers. The solution must include pre-processing checks, model-based protections, and post-processing filtering, while minimizing long-term operational overhead and avoiding custom model training.

Which solution will provide the MOST comprehensive, multi-layer protection against FM misuse?

A) Use a single Lambda function that validates user input, invokes the Bedrock model directly, evaluates the output using regex-based filtering, and logs any flagged responses to CloudWatch Logs.

B) Implement an API Gateway → Lambda → Bedrock Guardrails → Lambda pipeline where API Gateway performs schema validation, a pre-processing Lambda uses Amazon Comprehend to detect harmful or adversarial content, Bedrock Guardrails filter unsafe prompts and responses, and a final Lambda runs policy-validation checks before returning output.

C) Deploy an Amazon SageMaker model to classify all prompts and responses. Route allowed requests to the FM and block requests that exceed a preset safety risk threshold.

D) Inject strict prompt instructions that prevent policy-violating outputs and configure low-temperature inference on the FM to minimize unpredictable behavior.

---

**Q15.** A global e-commerce platform is expanding its generative AI system that produces personalized shopping guidance, tailored marketing messages, and contextual order summaries. The system combines structured transaction data, customer behavior signals, and unstructured feedback from chat transcripts to generate real-time experiences. Multiple foundation model (FM) variants have been trained in Amazon SageMaker AI with different prompt strategies and tuning datasets, and the company wants to identify which model delivers the highest relevance, lowest bias, and greatest conversion impact.

The analytics pipeline uses Amazon Comprehend to classify customer intent, extract entities from feedback, and compute sentiment trends across responses. The evaluation team must compare multiple FM variants simultaneously, analyze performance differences using real user interactions, and choose the most effective model—all without disrupting the existing customer experience.

Which deployment strategy BEST supports these requirements?

A) Release each new FM variant using a Canary deployment, exposing it to 1–5% of users at first. Increase traffic allocation only if Comprehend and SageMaker AI metrics match or exceed current benchmarks.

B) Route production traffic in parallel to all candidate FM variants using an A/B testing framework, evaluate output quality using Comprehend’s sentiment and entity extraction metrics along with SageMaker AI engagement predictors, and select the top-performing model after statistical comparison.

C) Use a Linear deployment to gradually shift 10% more traffic to each FM variant at fixed intervals while monitoring output quality, sentiment patterns, and engagement signals.

D) Deploy all new FM variants using a Blue/Green strategy, run them sequentially in a staging environment, then promote the stable version to full production once Comprehend and SageMaker AI validation passes.

---

**Q16.** A media analytics company is building an internal generative AI system on Amazon Bedrock to analyze interview transcripts and generate summaries. After deployment, reviewers report inconsistent reasoning, shifts in narrative tone, and occasional hallucinations when the model processes emotionally charged content. The engineering team must implement a troubleshooting framework that can systematically detect these FM-specific failure modes and provide actionable insights. The solution must minimize manual review effort and support automated evaluation during ongoing development cycles.

Which approach will BEST meet these requirements?

A) Use CloudTrail audit logs to track summary generation events and require engineers to manually inspect each log entry for anomalies.

B) Deploy a multi-tier approval system where human reviewers must validate every model summary before it is stored, and store reviewer decisions in DynamoDB.

C) Enable Enhanced Monitoring on the compute environment and configure memory and CPU alarms to identify processing anomalies that might affect summary generation accuracy.

D) Implement an automated evaluation workflow that uses golden datasets with expected outputs, output diffing to compare reasoning variations across runs, and Bedrock Model Invocation Logs to trace intermediate reasoning paths for consistency analysis.

---

**Q17.** A global wealth-management company is deploying a regulated generative AI environment that uses Amazon SageMaker AI for training proprietary financial-risk models and Amazon Polly to generate compliance-approved voice narratives from investment summaries. To comply with strict data-sovereignty and security controls, the cloud governance office requires that all SageMaker notebook instances operate without internet access and that all traffic to AWS services must stay entirely within the corporate private network. The solution must not introduce proxies, NAT gateways, or any component that allows outbound internet connectivity.

Which configuration will ensure full compliance while maintaining SageMaker notebook functionality?

A) Deploy a Site-to-Site VPN between the notebooks and AWS service endpoints to avoid public internet usage.

B) Configure an internal proxy fleet inside the corporate VPC and route all notebook traffic through it before reaching AWS services.

C) Establish Amazon SageMaker VPC interface endpoints for all required SageMaker and AWS service APIs inside the corporate VPC to keep notebooks fully private.

D) Provision a NAT gateway inside the private subnets so the notebook instances can access AWS services without exposing public IPs.

---

**Q18.** A global insurance provider is building a generative AI claims assistant that summarizes adjuster notes and recommends next actions by using an FM on Amazon Bedrock. Input data comes from multiple operational systems into an Amazon S3 data lake and is later consumed by SageMaker AI fine-tuning jobs. The data engineering team has discovered issues such as missing fields, unexpected data types, and malformed JSON payloads that cause erratic FM behavior and training instability. Leadership wants a standardized validation approach that can be reused across pipelines, exposes clear quality metrics, and blocks bad data before it is used for FM training or inference. The solution must use managed AWS capabilities and minimize custom infrastructure.

Which combination of steps will create a comprehensive, reusable data validation workflow for FM consumption with minimal operational overhead? (Select TWO.)

A) Use SageMaker Data Wrangler to build reusable data preparation flows that profile input datasets, enforce schema and data-type checks, apply cleansing and outlier filters, and export only validated data to S3. Integrate the Data Wrangler flows into SageMaker Pipelines so that FM training and batch inference steps always consume the validated outputs.

B) Rely on Amazon Bedrock guardrails to automatically filter low-quality or malformed input data at inference time and depend on model-level safety controls as the primary data validation mechanism.

C) Implement AWS Glue Data Quality rulesets on datasets registered in AWS Glue Data Catalog. Integrate these rules into Glue ETL jobs that populate a curated S3 bucket for FM inputs, configure the jobs to fail or quarantine records on rule violations, and publish rule evaluation results as Amazon CloudWatch metrics and dashboards.

D) Create an Amazon S3 Lifecycle configuration that periodically moves older raw datasets to S3 Glacier and assumes that only recent data is reliable enough for FM consumption, eliminating the need for explicit validation.

E) Use a single AWS Lambda function triggered by S3 PUT events to run basic string length checks on uploaded objects. If checks pass, immediately invoke the FM; otherwise, log the errors to CloudWatch Logs without blocking downstream processing.

---

**Q19.** A financial services company uses several foundation models (FMs) in Amazon Bedrock to summarize customer account activity, generate advisory messages, and produce compliance explanations for regulatory reviews. After a recent FM version update, analysts reported inconsistencies in how the model summarized similar account histories, causing variations in tone and missing required compliance statements. The engineering team suspects regression in the new model version and wants a systematic quality assurance process that prevents these issues before deployment.

The company requires a solution that can:

- run automated regression tests against golden reference outputs
- validate response quality and consistency for every FM version
- block deployment if quality thresholds are not met
- integrate directly into the CI/CD pipeline without human review

Which approach best meets these requirements?

A) Use an A/B testing system that routes a portion of customer traffic to the new FM version, then measures quality differences between A and B before gradually shifting all traffic.

B) Use automated quality gates integrated with the CI/CD pipeline that run regression tests against golden datasets using a Bedrock-based evaluation workflow. Block deployments when response consistency or accuracy metrics fall below defined thresholds.

C) Use a manual human-review process in Amazon A2I to evaluate model outputs for compliance tone, accuracy, and consistency before each deployment.

D) Use Amazon CloudWatch Logs to track FM invocation patterns and create alerts when the response distribution deviates from historical norms.

---

**Q20.** A global telecom provider is building a GenAI-powered troubleshooting assistant for its customer-support portal. The system uses Amazon SageMaker JumpStart to generate domain-specific embeddings for historical support transcripts and Amazon Bedrock to produce real-time LLM responses. Support agents frequently submit highly similar troubleshooting questions—often differing only by a few words—which results in repetitive Bedrock invocations, increased latency, and higher operational cost.

The engineering team needs a mechanism that can detect semantically similar queries, return previously generated answers when appropriate, and only invoke the foundation model when a question is genuinely new. The solution must support fast vector similarity search and integrate efficiently with the existing embeddings pipeline.

Which approach will BEST fulfill these requirements?

A) Store embeddings and cached responses in Amazon MemoryDB with vector search enabled, and perform semantic similarity checks to return cached answers before invoking the foundation model.

B) Cache full user queries in an in-memory key-value store and return responses only when an exact string match is found to avoid unnecessary FM calls.

C) Use Amazon Kendra to index the cached questions and answers and rely on its keyword-based search to retrieve previously answered queries.

D) Save embeddings in a traditional PostgreSQL database and perform exact SQL lookup queries on the stored text before invoking the FM.

---

**Q21.** A financial services company is deploying a large language model (LLM) on Amazon SageMaker AI for real-time portfolio-risk analysis. The model requires high GPU memory, uses custom CUDA kernels, and loads several billion parameters at startup. During load testing, the team notices that model initialization takes several minutes per instance, GPU utilization remains low for many requests, and throughput drops significantly whenever concurrent requests exceed a small batch size. The deployment must reduce initialization overhead, maximize GPU efficiency, and maintain consistent performance under fluctuating traffic patterns.

Which solution will MOST effectively address the unique deployment challenges of the LLM?

A) Enable SageMaker Serverless Inference so the model loads only when needed, reducing idle GPU costs while improving peak throughput.

B) Use a standard SageMaker PyTorch inference container, increase the instance count with auto scaling, and rely on larger EBS volumes to reduce loading delays.

C) Store model weights in Amazon S3 and stream them into GPU memory per request using presigned URLs to reduce container memory footprint.

D) Use a custom SageMaker container with optimized tensor-parallel loading to spread model weights across multiple GPUs, enable continuous batching with the DJL serving stack, and preload the model on container startup to avoid repeated initialization.

---

**Q22.** A regional hospital network is building a generative decision-support assistant that suggests follow-up care plans for patients. The assistant uses Amazon SageMaker AI to train predictive models from EHR data, lab results, and demographic attributes, and uses an FM in Amazon Bedrock to generate natural language explanations of the recommended plans. The system runs in multiple Regions to comply with local healthcare regulations.

During internal review, clinicians raise concerns that recommendations may differ across patient groups (for example, older patients vs. younger patients, or different socioeconomic segments). The data science team wants a managed way to measure and monitor bias across these groups in training data and model predictions, surface metrics per Region, and minimize the amount of custom fairness code they must maintain.

Which approach best satisfies the fairness and monitoring requirements with the least operational complexity?

A) Use Amazon SageMaker Clarify to compute pre-training and post-training bias metrics, enable built-in bias monitoring on SageMaker endpoints in each Region, and publish Clarify bias metrics to Amazon CloudWatch for alerting on demographic disparities.

B) Use Amazon Comprehend Medical to annotate patient notes with entities and sentiment labels, then create custom AWS Glue jobs that periodically scan SageMaker prediction outputs and flag differences in recommendations across demographic attributes.

C) Use AWS Lambda to postprocess predictions from SageMaker endpoints, write outputs and demographic attributes to Amazon S3, and build a custom fairness dashboard in Amazon QuickSight to manually review discrepancies among patient segments.

D) Use Amazon SageMaker Model Monitor data-quality monitors to track input feature distributions, and configure Amazon SNS alerts when feature distributions for specific demographic attributes deviate from historical baselines.

---

**Q23.** A digital health platform is developing a context-aware conversational assistant that uses Amazon Bedrock to answer patient questions about wellness plans. The assistant must keep track of multi-turn conversations, recognize ambiguous user intents, and request clarification when necessary. The system must also maintain conversation history to allow the FM to provide consistent, context-rich responses during long sessions. The company wants a solution that requires minimal custom orchestration code and integrates well with downstream AI components.

Which solution will BEST meet these requirements?

A) Use AWS Step Functions to build clarification and fallback workflows, Amazon Comprehend to perform intent recognition, and DynamoDB to store conversation history for context retrieval in FM prompts.

B) Use an SQS FIFO queue to store incoming user messages, a Lambda function to parse session details, and Amazon RDS to store all conversation transcripts.

C) Use Amazon Kinesis Data Firehose to stream user messages to S3, use Athena queries to reconstruct past interactions, and provide the historical transcript to the FM when needed.

D) Use Amazon CloudWatch Logs to capture all user interactions, build context in-memory per request, and rely on the FM’s built-in reasoning to handle ambiguities without external services.

---

**Q24.** A fintech startup is building a generative AI platform that produces regulatory summaries, extracts compliance risks, and generates audit-ready narratives using multiple Amazon Bedrock foundation models. One of the selected models is available only in a single AWS Region, and the team is concerned about potential service disruptions affecting customer workloads. The business requires the system to continue operating even if a model becomes temporarily unavailable or if latency increases unexpectedly.

The lead AI engineer must design a resilient architecture that maintains functionality, handles disruptions gracefully, and automatically fails over when needed.

Which approach BEST meets these requirements?

A) Configure Amazon Bedrock Cross-Region Inference with a fallback Region and integrate AWS Step Functions circuit breaker patterns to reroute requests during failures while degrading gracefully when the primary model is unavailable.

B) Deploy all inference logic on a single Amazon EC2 instance in the Region where the model is available and rely on auto scaling to recover from outages.

C) Replace all Bedrock models with open-source models hosted in a self-managed Kubernetes cluster to avoid relying on regional model availability.

D) Add retries with exponential backoff directly inside the client application and continue sending requests to the same Region until the model becomes responsive again.

---

**Q25.** A global technology firm is expanding its internal generative-AI ecosystem by integrating services such as Amazon Comprehend for document classification and Amazon Kendra for semantic enterprise search. As part of its modernization initiative, the firm is deploying Amazon Q Business to surface insights from architecture repositories, operational runbooks, and engineering knowledge bases.

The environment must strictly enforce the company's existing enterprise role-based access controls (RBAC) so that only authorized users can view sensitive technical content. The firm also wants to minimize operational overhead and avoid maintaining custom ingestion or identity workflows.

Which of the following will satisfy these requirements with the LEAST operational overhead? (Select TWO.)

A) Deploy a custom identity proxy that uses Amazon Cognito to issue temporary access tokens and implements its own RBAC validation logic.

B) Use Amazon Q Business with scheduled reindexing jobs that pull content from all repositories and enforce access restrictions by applying document-level tagging rules during each synchronization cycle.

C) Set up a Q Business with data source connectors for the technical knowledge repositories and design repositories. Integrate authentication and RBAC using AWS IAM Identity Center.

D) Deploy Q Business data sources with automatic synchronization enabled and map enterprise access groups directly to data-source permissions.

E) Place Amazon Q Business behind Amazon API Gateway endpoints and implement SAML-based SSO using AWS IAM Identity Center, with AWS Lambda functions performing request-validation checks before allowing queries to reach the Q Business application.

---

**Q26.** A global logistics company operates a multilingual virtual-assistant platform that uses Amazon Lex and multiple foundation models (FMs) deployed through Amazon SageMaker AI. After a recent FM update, customers reported inconsistent troubleshooting guidance and mismatched responses across regions. The engineering team suspects semantic drift introduced during the model update.

They want a validation approach that:

- continuously monitors model outputs during rollout
- detects semantic shifts or degraded response quality in real time
- triggers alerts before inconsistencies affect large volumes of traffic
- integrates into their automated CI/CD process without disrupting live production

Which approach ensures reliable FM behavior and early detection of semantic drift during updates?

A) Implement a synthetic workflow interaction generator in SageMaker AI to simulate user behavior during CI/CD and compare new outputs with golden datasets.

B) Use SageMaker Model Monitor with custom quality metrics on a shadow deployment to detect real-time drift and generate immediate alerts during model rollout.

C) Leverage SageMaker Experiments to compare output deviations across versions and promote updated models only when performance thresholds are met.

D) Use AWS MLflow with SageMaker AI to track versioned model metadata and detect anomalies after each FM update.

---

**Q27.** A multinational insurance company operates in regions with strict data-residency requirements. Customer claim documents and policy records must remain on-premises within each jurisdiction, but the company wants to use Amazon Bedrock to generate claim summaries and policy-explanation text. The solution must allow the foundation model to operate on the data without moving regulated content outside the regional boundaries. The architecture must also support consistent inference patterns across countries while minimizing operational overhead.

Which solution will BEST satisfy these compliance and FM access requirements?

A) Set up an S3 bucket in the primary AWS Region and upload all claim documents from each country. Apply KMS multi-Region keys and use Amazon Bedrock Guardrails to ensure that the FM handles sensitive information safely.

B) Deploy AWS Outposts racks in each jurisdiction and run containerized preprocessing services locally. Route sanitized feature vectors or redacted text from Outposts to Amazon Bedrock in the nearest AWS Region for FM inference, ensuring regulated data never leaves the local environment.

C) Deploy SageMaker AI endpoints inside the corporate data centers and sync the on-premises data to Amazon Bedrock with scheduled export jobs. Perform FM inference in the cloud and return results to on-premise systems.

D) Use AWS Wavelength Zones in each country to cache on-premises data in local carrier networks and run Bedrock model inference directly inside the Wavelength Zone to ensure compliance with data-locality requirements.

---

**Q28.** A healthcare research institute processes multi-page scientific reports that include handwritten annotations, scanned lab images, and typed experiment summaries. A Generative AI engineer configures Amazon Bedrock Data Automation (BDA) to classify each page and extract structured fields used for downstream indexing. For quality assurance, the engineer uses Amazon A2I to randomly review a subset of extracted pages.

The team created multiple custom blueprints, but only the first page of each PDF is reliably classified. Subsequent pages are inconsistently categorized or skipped entirely, causing missing metadata in the clinical document archive. The team must improve BDA’s page-by-page consistency without adding new custom processing logic or increasing operational overhead.

Which combination of actions will address these issues most effectively? (Select TWO.)

A) Simplify and standardize blueprint names and maintain exactly one unique blueprint per document type category.

B) Use Amazon Textract asynchronous analysis to ingest full PDFs as single documents, then infer content types from detected blocks.

C) Turn on PDF page-level splitting in the BDA project to ensure every page is processed independently.

D) Add multiple blueprint variations per document type category to maximize potential matching.

E) Enable Amazon Rekognition DetectText and run OCR first to classify pages before passing them to BDA.

---

**Q29.** A retail company is enhancing its order-management application by integrating generative AI to generate personalized order-status summaries and customer-support responses. The existing application publishes order events (created, shipped, delayed, canceled) to an internal event stream. The engineering team wants to incorporate GenAI processing with minimal disruption to the current system while ensuring that events automatically trigger AI enrichment workflows. The solution must avoid adding tightly coupled API calls inside the legacy application.

Which solution will provide the MOST scalable and maintainable integration?

A) Expose a synchronous REST endpoint with Amazon API Gateway that the legacy application must call for each order event. The endpoint triggers a Lambda function that sends data to Amazon Bedrock.

B) Modify the legacy application to call a new GenAI microservice directly after each order update. The microservice invokes Amazon Bedrock and writes enriched results back to the database.

C) Route order events through Amazon EventBridge. Use EventBridge rules to trigger a Lambda function that formats event details, invokes the Amazon Bedrock API for summarization, and stores the AI-generated output in the application’s data store.

D) Create an S3 bucket for order snapshots. Configure the legacy application to upload order events as JSON files, and enable S3 event notifications to run a Lambda function that performs GenAI summarization.

---

**Q30.** A financial services company is building an internal AI assistant that helps compliance analysts review customer emails, chat logs, and scanned documents for regulatory risks. Amazon Textract extracts text from PDFs, and Amazon Comprehend performs downstream NLP analysis.

The compliance team requires two outputs for every detected PII entity:

- Exact character offsets showing where the PII appears in the extracted text.
- Entity labels identifying the type of sensitive data so the foundation model can generate structured compliance summaries.

The engineering team must choose Comprehend analysis modes that provide both outputs.

Which analysis modes should be selected? (Select TWO.)

A) Use Key Phrase Detection to identify important terms in the extracted text.

B) Use the Offsets analysis to return precise start and end character positions.

C) Use the Syntax Analysis feature to examine sentence structure and token-level part-of-speech data.

D) Use Sentiment Analysis to determine the emotional tone in the communication.

E) Use the Labels analysis to return classification-style entity names for compliance processing.

---

**Q31.** A global logistics company operates a real-time GenAI-enabled support platform that uses a foundation model for triaging customer cases, plus a computer-vision workflow for detecting damaged parcels. Recently, support engineers have encountered difficulty diagnosing system slowdowns, intermittent FM inference failures, and unpredictable error chains across several microservices.

The engineering leadership wants a fully integrated troubleshooting approach that allows the team to correlate logs from multiple components, trace cross-service API calls, and automatically detect GenAI-specific error signatures. The solution must accelerate debugging without introducing custom machine learning pipelines or specialized infrastructure.

Which solution meets these requirements MOST effectively?

A) Configure Amazon CloudWatch Logs Insights to centralize and query system logs, enable AWS X-Ray to trace requests flowing through the GenAI microservices and external integrations, and use Amazon Q Developer to automatically analyze logs for FM-related error patterns and operational anomalies.

B) Use Amazon CloudWatch Logs Insights to gather all logs, deploy Amazon Athena to run SQL queries on archived log data in Amazon S3, and integrate Amazon SageMaker AI to train a custom anomaly-detection model on historical error logs.

C) Aggregate logs using CloudWatch Logs Insights, deploy AWS Step Functions to orchestrate cross-service error capture, and integrate Amazon EventBridge rules to trigger SNS alerts whenever the FM service encounters errors.

D) Enable AWS X-Ray to track incoming and outgoing FM inference calls, stream application logs into Amazon Kinesis Data Streams for real-time processing, and store enriched logs in Amazon OpenSearch Service for downstream troubleshooting dashboards.

---

**Q32.** A multinational travel-booking platform is building a real-time itinerary assistant using Amazon Bedrock. The assistant must answer user questions instantly during flight searches, including airport restrictions, baggage rules, local weather, and visa requirements. Some of this information changes infrequently, while other elements require fresh, model-generated reasoning.

During testing, users complain about slow responses whenever the assistant must generate multi-step reasoning or fetch large contextual information. The company wants to improve responsiveness while reducing unnecessary FM invocations, especially for predictable or repetitive queries. The solution must be cost-efficient, require minimal operational overhead, and work reliably during peak traffic periods.

Which combination of actions will BEST meet these requirements? (Select TWO.)

A) Pre-compute FM responses for predictable queries (baggage rules, airport policies, visa basics), store them in Amazon ElastiCache, and return cached results during peak hours.

B) Migrate all inference traffic to the largest, highest-capacity FM variant to ensure faster inference, regardless of query type or complexity.

C) Use Bedrock response streaming so users can see partial model output immediately, improving perceived latency for multi-step reasoning questions.

D) Use Amazon Kendra to retrieve context for all queries and bypass the FM entirely for any user question that relates to known travel information.

E) Enable parallel FM invocations for every user query so that multiple models generate different reasoning paths, and return the first completed response.

---

**Q33.** A medical research institute is developing an AI platform that processes sensitive patient ECG scans, radiology images, and physician notes. The system uses Amazon Textract and Amazon Rekognition to extract insights before sending the data to analytics models hosted on Amazon Bedrock. All datasets are stored in Amazon S3, but researchers and AI workflows must only access the specific datasets relevant to their assigned clinical studies. Compliance officers require a unified governance layer that supports fine-grained dataset permissions, column-level restrictions, automatic encryption, and centralized auditing. The institute wants to avoid manually managing dozens of S3 bucket policies or IAM configurations for every study group.

Which solution best satisfies these requirements?

A) Configure Amazon Cognito identity pools to authenticate researchers and issue temporary credentials used for restricted S3 access.

B) Use AWS Lake Formation to define table- and column-level access controls for S3-backed datasets, centralize governance policies, and audit all access through built-in logging.

C) Apply tag-based S3 bucket policies to segregate medical datasets and rely on CloudTrail logs to audit all researcher interactions.

D) Create S3 Access Points for each clinical study and attach IAM policies to enforce dataset-level separation and researcher permissions.

---

**Q34.** A research company uses a vector database to support retrieval-augmented generation for its internal knowledge assistant. As the dataset grows, engineers notice slower similarity searches, inconsistent relevance scores, and occasional retrieval drift caused by outdated or low-quality embeddings. The company wants an operational management approach that improves vector store reliability, maintains index performance automatically, and validates embedding quality during ingestion. The solution should use managed AWS services and require minimal ongoing maintenance.

Which solution will BEST meet these requirements with the least operational overhead?

A) Use CloudWatch metrics to continuously monitor vector store latency and index saturation, and create an automated index optimization routine with EventBridge and Lambda to rebuild or compact indexes based on threshold conditions.

B) Run daily Athena queries to recalculate embedding drift across the entire dataset and rewrite low-quality segments into the vector store.

C) Create a Glue job that performs scheduled cosine similarity checks across all embeddings and removes vectors that fall below a similarity threshold.

D) Use a Step Functions pipeline that requires manual approval for embeddings before they are inserted into the vector store to maintain data quality.

---

**Q35.** A biotechnology company is developing a RAG-based assistant to help researchers query internal laboratory protocols, chemical safety sheets, and experiment diagrams stored in Amazon S3. The retrieval layer uses Amazon Bedrock Knowledge Bases with embeddings stored in S3 Vectors to reduce storage and retrieval costs.

During testing, scientists report inconsistent answers: relevant sentences are split across multiple chunks, diagrams lose explanatory context, and multi-step procedures appear fragmented. The ingestion workflow currently uses a rigid fixed-size chunking strategy.

The team also preprocesses scanned lab manuals with Amazon Textract via Amazon SageMaker AI, and uses a Bedrock foundation model to answer questions based on retrieved chunks. The organization wants to improve retrieval coherence, maintain relevance for multi-sentence scientific explanations, and avoid unnecessary cost increases.

Which configuration best satisfies the requirements?

A) Enable hierarchical chunking by generating both macro-level and micro-level chunks and indexing all variations for retrieval.

B) Activate semantic chunking in the Bedrock Knowledge Base and adjust chunk parameters so chunks are formed based on meaning rather than fixed sizes.

C) Use a larger Bedrock model with an extended context window and pre-summarize all documents using recursive summarization workflows before ingestion.

D) Remove chunking and ingest each document as a single chunk, relying on the foundation model’s long-context window to interpret large inputs.

---

**Q36.** A global insurance provider is building a document-analysis assistant on Amazon Bedrock to summarize long claim forms, policy documents, and customer correspondence. The assistant uses a foundation model (FM) to generate explanations and action items for claim specialists. Recently, the monthly FM bill increased sharply due to extremely long input prompts and oversized output generations.

The architecture currently injects entire historical claim notes into every prompt, even when only the most recent details are relevant. The specialists also report that the model often produces longer-than-necessary summaries. The engineering team needs to reduce token usage without degrading the model’s ability to generate accurate summaries, and the solution must require minimal operational overhead.

Which approach BEST reduces token usage while maintaining summary quality?

A) Implement context-window optimization by pruning irrelevant historical notes, apply prompt compression for long claim documents, and enforce response-size controls in the prompt itself to limit summary length.

B) Use an AWS Lambda function to dynamically shorten all responses by truncating the FM output to a predefined character limit before returning the response to the user.

C) Use Amazon S3 lifecycle rules to archive older claim documents and instruct the FM via system prompts to exclude archived information from analysis.

D) Cache the FM responses for all claim types in Amazon ElastiCache and prevent the FM from being invoked for repeated queries even when claim details differ slightly.

---

**Q37.** A global e-learning platform is building an AI-powered content generation system that uses multiple foundation models (FMs): one for summarization, one for question generation, and one for code explanation. The platform wants to automatically select the appropriate FM based on the user’s request type. The solution must support dynamic routing, handle large traffic volumes efficiently, and minimize the operational overhead of maintaining separate integration endpoints for each model.

The engineering team also needs the flexibility to add new specialized models in the future without modifying client-facing APIs.

Which solution will meet these requirements MOST effectively?

A) Create static routing tables inside an AWS Lambda function that maps request types to specific FM ARNs. Update the Lambda function manually whenever new models are added.

B) Implement routing logic directly inside front-end applications by embedding FM identifiers inside each request. Call the appropriate Bedrock model directly based on request type.

C) Use Amazon CloudFront Functions to inspect request metadata and forward traffic to multiple backend API Gateway endpoints, each dedicated to a different FM.

D) Use Step Functions to orchestrate model routing by inspecting the request type and invoking the appropriate FM. Expose a single API Gateway endpoint with request transformations to route traffic to the Step Functions workflow.

---

**Q38.** A global logistics company operates a retrieval-augmented assistant used by warehouse planners to query shipment histories, routing constraints, and delivery forecasts. The system stores document embeddings in Amazon OpenSearch Service and uses an Amazon Bedrock FM for generation. As warehouse activities occur throughout the day, shipment records in Amazon S3 change frequently. Users report that the assistant occasionally returns outdated information because vector embeddings are not being refreshed consistently. The company needs a scalable, low-overhead mechanism to keep embeddings accurate and synchronized with upstream data updates.

Which solution will MOST effectively maintain current and accurate embeddings in the vector store?

A) Run a nightly batch job that reprocesses all documents, regenerates embeddings for the entire corpus, and recreates the OpenSearch index from scratch.

B) Use Amazon S3 event notifications to send object-created and object-updated events to an Amazon SQS queue. A SageMaker Processing job polls the queue, regenerates embeddings only for changed documents, and updates the OpenSearch index.

C) Manually trigger a SageMaker Processing job whenever a warehouse planner identifies incorrect or outdated search results in the FM assistant.

D) Store all shipment records in Amazon DynamoDB and configure DynamoDB Streams to capture modification events. Use AWS Glue to rebuild the entire embedding store whenever any record changes.

---

**Q39.** A global automotive platform is building a GenAI assistant on Amazon Bedrock to help users troubleshoot vehicle issues. Users can upload descriptions, error logs, and chat messages to interact with the assistant. During early testing, the security team discovers that some users attempt to submit harmful content, including self-harm statements, violent instructions, and attempts to bypass the safety mechanisms of the foundation model (FM).

To reduce risk, the platform must implement a comprehensive input-safety pipeline that filters, validates, and blocks unsafe content before the FM receives the prompt. The solution must integrate with existing AWS services, support custom business rules, generate detailed moderation logs, and require minimal ongoing operational maintenance.

Which solution will meet these requirements with the least operational overhead?

A) Use an AWS Step Functions workflow that invokes Amazon Bedrock Guardrails for initial filtering, followed by a Lambda function that applies custom moderation logic. Send all blocked inputs and violation metadata to CloudWatch Logs for auditing.

B) Expose all user prompts directly to Amazon Bedrock Guardrails, then use API Gateway request validation to block unsupported data formats before invoking the FM.

C) Deploy an Amazon SageMaker endpoint that classifies input prompts for toxicity. For any high-risk prompt, use an SNS topic to notify administrators and route the message to a manual review queue.

D) Create a Lambda function that scans user prompts using Amazon Comprehend sentiment analysis and Amazon Comprehend PII detection. Block any prompts with negative sentiment or PII indicators before forwarding to the FM.

---

**Q40.** A digital branding firm uses Amazon Bedrock and Amazon SageMaker AI to generate marketing copy for hundreds of ecommerce clients. The firm wants to standardize output quality using Bedrock Prompt Management by creating reusable, parameterized prompt templates that support client-specific variables such as product tone, regional phrasing, and brand guidelines. The templates must also enforce strict style rules—such as banned phrases, tone consistency, and formatting constraints—across all generated content.

For compliance, the governance team requires full versioning and a mandatory review step before any updated prompt template can be activated. The organization must also track all template changes and usage activity for audit purposes with minimal manual effort.

Which solution meets these requirements?

A) Use Lambda-based preprocessing scripts to validate tone and keyword restrictions before invoking a model, maintain prompt templates in AWS Systems Manager Parameter Store with versioning, and enable CloudTrail only for model invocation events.

B) Use Bedrock Guardrails to validate stylistic rules at runtime, store template definitions in Amazon S3 with object versioning enabled, and configure Amazon CloudWatch Logs to capture template access events.

C) Develop prompt templates in Bedrock Prompt Management, use Amazon Comprehend to classify tone and detect restricted phrases, and configure Amazon SNS to send notifications whenever templates are updated or used.

D) Configure reusable templates with client-specific parameters and versioning, enforce a mandatory approval workflow for template changes, apply Bedrock Guardrails to enforce stylistic rules, and use AWS CloudTrail to record template modifications and usage events for compliance.

---

**Q41.** A global consulting firm is building an AI-powered knowledge analytics platform. The platform must process large volumes of internal reports, extract insights, and answer employee questions with conversational responses. The solution must use a foundation model (FM) from Amazon Bedrock for inference and Amazon SageMaker AI for preprocessing tasks such as document chunking, embedding generation, and metadata extraction.

The compliance team requires that no model training or fine-tuning occur in the architecture. In addition, the system must support hybrid retrieval (semantic + keyword search), run fully within a private VPC environment, and scale automatically with increasing employee traffic. The architecture must minimize operational overhead while ensuring consistent latency for inference requests.

Which architectural approach BEST meets these requirements?

A) Use Amazon SageMaker AI to host the FM in a custom inference container and integrate with Amazon Kendra for hybrid search. Configure autoscaling by adding additional GPU-based SageMaker endpoints as traffic increases.

B) Use Amazon Bedrock Knowledge Bases with a vector store in Amazon OpenSearch Serverless for hybrid search. Run SageMaker preprocessing jobs in a private VPC, and expose a single Bedrock inference endpoint for employee queries routed through an API Gateway in the VPC.

C) Deploy a multi-model SageMaker endpoint hosting several fine-tuned versions of an FM. Use Route 53 latency-based routing to direct employee queries to the lowest-latency model endpoint in each Region.

D) Use Amazon Bedrock for both preprocessing and inference. Replace SageMaker entirely to reduce architectural complexity and use managed Bedrock pipelines for chunking and metadata extraction.

---

**Q42.** A transportation company is developing an Amazon Bedrock agent that provides dispatch recommendations based on live vehicle data. The agent uses Amazon SageMaker AI for ETA prediction and Amazon Comprehend to interpret driver feedback. The company must integrate a custom telemetry component that maintains a long-lived WebSocket connection to stream continuous GPS data into the agent.

The development team attempted serverless designs but encountered connection timeouts because the WebSocket stream requires a persistent network session. The company needs a fully managed deployment option that supports long-running connections without managing servers.

Which solution will meet these requirements?

A) Deploy the telemetry tool on Amazon EC2 with a custom script to maintain the WebSocket session.

B) Expose the telemetry component as a containerized application running on Amazon ECS with the AWS Fargate launch type to maintain persistent WebSocket connections.

C) Deploy the telemetry component on Amazon App Runner as a containerized service with automatic scaling based on concurrent WebSocket sessions.

D) Run the telemetry tool in AWS Lambda and periodically refresh the WebSocket session through scheduled invocations.

---

**Q43.** A global HR software company is building an AI assistant that answers employee policy questions by using retrieval-augmented generation (RAG) with Amazon Bedrock. The assistant must perform semantic search over handbooks, benefits guides, and jurisdiction-specific policies stored in Amazon S3. The team wants to minimize operational overhead for vector index management while still supporting FM augmentation with context-aware retrieval. They prefer not to manage OpenSearch clusters or implement custom vector indexing logic but need scalable performance as more documents and regions are added.

Which solution will BEST meet these requirements?

A) Create an Amazon Aurora PostgreSQL cluster with the pgvector extension. Write custom application logic to compute embeddings, insert vectors, and perform similarity search queries for each request.

B) Deploy an Amazon OpenSearch Service domain with vector search enabled. Build custom ingestion jobs on AWS Lambda to compute embeddings and manage index sharding, mappings, and lifecycle policies.

C) Use Amazon Bedrock Knowledge Bases with a managed vector store. Connect the S3 document repository, enable vector search, and integrate the knowledge base with the Bedrock FM for retrieval-augmented prompts.

D) Store documents and precomputed embeddings in Amazon DynamoDB as JSON items. Implement custom cosine similarity logic in the application layer to filter and rank results before calling the FM.

---

**Q44.** A global logistics company is building a retrieval-augmented assistant that answers questions about shipment status, contracts, and warehouse procedures. The data science team uses multiple vector backends (Amazon OpenSearch Service, Amazon Aurora with pgvector, and a managed Bedrock Knowledge Base) across different business units. The GenAI lead wants a consistent way for foundation models to perform vector search regardless of which backend stores the embeddings. The solution must provide a stable access pattern for the FM, support future backend changes with minimal code impact, and integrate cleanly with existing Bedrock-based agents.

Which combination of approaches will BEST provide consistent access mechanisms for FM retrieval augmentation?

A) Embed direct OpenSearch, Aurora pgvector, and Bedrock Knowledge Base SDK calls into the FM application code. Use conditional logic to select the correct SDK based on the tenant and region.

B) Expose all vector backends through an internal “retrieval gateway” service that offers a single standardized HTTP API. Register this gateway as a tool for the FM by using function calling, so the model always invokes the same retrieval interface.

C) Use separate Lambda functions for each vector backend, each with its own custom request/response shape. Allow the FM to select which Lambda function to call by passing the function name in the user prompt.

D) Implement Model Context Protocol (MCP) servers for each vector backend and use an MCP client in the FM orchestration layer. Standardize retrieval tool schemas so the FM always issues the same query structure, regardless of backend.

---

**Q45.** A global logistics company is building an automated system to optimize its inventory replenishment workflow. Employees will submit restocking requests and check inventory levels through natural language interactions, and the solution must autonomously trigger supply chain processes with minimal ongoing maintenance. The company uses Amazon Textract to extract key fields from scanned inventory documents and stores all operational and inventory data in Amazon Aurora. The system must support Model Context Protocol (MCP) to enable seamless communication with the company’s existing inventory systems.

Which solution will minimize operational complexity while meeting these requirements?

A) Create an intelligent assistant with Amazon Lex and Amazon Polly, using AWS Lambda to process natural language inventory requests and store results in Amazon DynamoDB. Use Amazon SNS to notify supply chain teams for restocking actions.

B) Implement an AI-powered chat assistant with Amazon Lex, using AWS Lambda to process inventory requests. Push requests to an Amazon SQS queue, which triggers backend supply chain processes on Amazon ECS with AWS Fargate.

C) Set up an agent using Amazon Bedrock AgentCore Runtime and Strands Agents, and configure a prebuilt MCP server that links to Aurora for inventory data. Store and expose the data as MCP tools, connecting with the company’s chat interface.

D) Deploy an MCP server using FastMCP with LangGraph on an Amazon EC2 instance, connect it to Aurora for inventory data, and expose the data as MCP tools. Integrate with the company’s chat interface using a custom agent built with Amazon SageMaker.

---

**Q46.** A transportation logistics company is building a predictive maintenance solution for its fleet of autonomous delivery vehicles. The engineering team uses Amazon Comprehend to extract entities such as fault codes, component descriptions, and mechanic observations from thousands of maintenance logs. These structured insights are merged with vehicle telemetry data stored in Amazon S3 to create a unified dataset for analysis.

The analytics group needs to prepare this combined dataset and build a custom predictive model to anticipate drivetrain failures. The team consists of analysts with limited coding experience, and leadership requires the process to remain integrated with downstream Amazon SageMaker AI components for future batch inference and deployment pipelines. The solution must simplify data preparation and model training while avoiding the need to build custom ML infrastructure.

Which service should the team use to prepare the dataset and train the predictive model?

A) Use Amazon Bedrock to fine-tune a foundation model that predicts mechanical failures directly from the raw logs and telemetry data.

B) Use SageMaker Canvas to visually prepare the dataset and train a custom predictive model using a no-code workflow integrated with SageMaker AI.

C) Use SageMaker Ground Truth to label failure events and automatically create a model for drivetrain-failure predictions.

D) Use Comprehend to build a predictive model end-to-end without requiring any Amazon SageMaker components.

---

**Q47.** A global insurance provider runs a fraud-analytics platform using Amazon SageMaker AI for feature engineering and model development, and Amazon Rekognition to validate customer identity documents submitted during claims processing. Each data scientist is assigned their own isolated SageMaker notebook instance to comply with internal compliance and audit requirements. All developers must share access to Amazon Rekognition and a centralized Amazon S3 data lake, but no developer should be able to start, stop, or connect to a notebook instance assigned to another user.

The security engineering team must enforce strict least-privilege access, prevent cross-notebook access, and avoid introducing any custom authorization service or additional infrastructure. Which approach provides the correct enforcement model?

A) Configure SageMaker lifecycle configurations to prevent users from attaching to notebook instances owned by other developers.

B) Use a shared SageMaker notebook instance for all developers and control access by configuring JupyterLab workspace-level permissions.

C) Enable VPC Security Group isolation around each notebook instance to implicitly restrict which developer can connect to each instance.

D) Create an IAM policy for each developer that grants SageMaker permissions only on the ARN of their assigned notebook instance while allowing shared access to Rekognition APIs and the central S3 data lake.

---

**Q48.** A healthcare analytics company is building a GenAI assistant that allows clinicians to summarize patient case files, generate follow-up recommendations, and interact with medical knowledge bases. The system uses Amazon Bedrock FMs for generation and Amazon API Gateway for backend access. The company wants to accelerate adoption across multiple internal teams, many of which have minimal experience integrating with FM-based APIs.

The solution must provide an easy interface for developers, support API-first integration, and enable non-technical teams to create simple GenAI workflows without writing custom code.

Which solution will BEST meet these requirements?

A) Build custom React components for each FM interaction, distribute them internally, and require all teams to manually integrate with Bedrock using AWS SDK calls.

B) Use AWS Amplify to generate declarative UI components that interact with Bedrock APIs, publish an OpenAPI specification for the FM endpoints, and provide Bedrock Prompt Flows so non-technical users can assemble no-code GenAI workflows.

C) Use Amazon SageMaker Studio to build and publish notebooks that demonstrate FM usage. Require teams to copy notebook examples into their own applications for integration.

D) Deploy a Lambda-backed API Gateway endpoint that abstracts FM calls, and require all internal teams to write their own middleware to integrate with the Lambda function.

---

**Q49.** A global financial analytics firm uses an FM embedding endpoint on Amazon SageMaker AI to generate embeddings for market reports, regulatory filings, and real-time analyst commentary. These embeddings feed multiple vector search indexes that power downstream recommendation engines for portfolio managers. The system also uses Amazon Comprehend for topic extraction and sentiment analysis to understand how market tone shifts across sectors.

Recently, analysts report that the recommendations feel “off” and no longer align with current market themes. The engineering team suspects drift in both the embedding distribution and the underlying writing style of analyst reports. They need to evaluate embedding drift using live endpoint traffic, compare it to baseline training data, and prepare the system for safe retraining—without impacting the production workload.

Which actions should the team take? (Select TWO.)

A) Use SageMaker Model Monitor with a custom container to compute embedding-drift statistics, compare production data with stored baseline vectors, and export all drift reports to Amazon S3 for inspection.

B) Enable a Comprehend custom classifier to re-evaluate the tone of incoming analyst text and automatically update vector database entries without using baseline comparisons.

C) Set up a parallel SageMaker embedding endpoint with Data Capture enabled, gradually shift traffic using UpdateEndpointWeights, and analyze captured embeddings in SageMaker Model Monitor to identify drift before replacing the production endpoint.

D) Run all incoming analyst reports through SageMaker Batch Transform jobs nightly and manually compare embedding vectors with old training data to detect distribution changes.

E) Enable autoscaling on the embedding endpoint to handle higher traffic volumes and reduce latency issues during drift analysis.

---

**Q50.** A global insurance provider is deploying an internal GenAI assistant using Amazon Bedrock AgentCore Runtime to help policy specialists summarize claim files, validate coverage rules, and generate multilingual customer explanations using Amazon Translate and Amazon SageMaker AI. The company requires strict access control: only employees authenticated through the corporate OIDC identity provider may use the agent. Security teams mandate that AgentCore must validate inbound OIDC tokens and allow requests only when the token’s audience matches the registered internal application ID. The engineering team also wants to reduce generation costs by configuring the agent’s maximum tokens setting to limit output length and prevent overly long responses.

Which configuration satisfies these requirements MOST effectively?

A) Use Amazon Cognito user pools as a proxy identity provider and map the application ID for audience enforcement while leaving the maximum tokens setting unmanaged.

B) Integrate the OIDC IdP only for outbound authentication from AgentCore, and rely on IAM permissions to validate inbound requests.

C) Configure AgentCore Identity as an inbound OIDC provider, specify the internal application ID as an allowed audience, and set a maximum tokens value to enforce response length limits.

D) Use SigV4-only request signing for all AgentCore Runtime calls and disable external identity providers to simplify authentication.

---

**Q51.** A global ecommerce company is building a semantic product-search system that supports millions of items across multiple specialized categories such as electronics, apparel, home goods, and automotive. The company uses Amazon OpenSearch Service with the neural search plugin to store embeddings generated by an Amazon Bedrock model. As traffic grows, search latency increases and some queries return incomplete results because certain categories dominate the primary index. The architecture must be optimized to improve retrieval performance at scale while keeping the operational burden low.

Which solution will MOST effectively optimize vector search performance for this workload?

A) Create a single index but add category labels to each vector document so that queries can filter results based on the user’s category. Rely on vector scoring alone for retrieval performance.

B) Store all embeddings in a single large OpenSearch index and increase the number of replicas to improve search speed across all categories.

C) Use Amazon RDS with the pgvector extension to store all product embeddings in a single table and scale vertically by increasing the database instance size.

D) Partition the data by domain and create multiple specialized vector indices in OpenSearch (for example, electronics, apparel, automotive). Use category routing to query only the relevant index and apply sharding within each index to reduce search load and improve recall.

---

**Q52.** A retail analytics company is developing a generative AI assistant that interprets sales reports, summarizes trends, and generates SQL queries to help analysts explore data. The engineering team must select a foundation model (FM) for Amazon Bedrock that aligns with the company’s key requirements:

- strong performance on analytical reasoning tasks
- high accuracy in generating syntactically correct SQL
- well-documented limitations and benchmark transparency
- predictable latency for interactive use

The company wants to choose the FM based on empirical evaluation, structured capability comparisons, and alignment with the workload’s constraints.

Which approach will allow the team to choose the MOST appropriate FM for these requirements?

A) Evaluate multiple Bedrock FMs by using Bedrock evaluation tools with structured benchmarks for reasoning, SQL generation accuracy, latency measurements, and failure-case analysis. Select the model that best matches the business requirements.

B) Choose the latest and most expensive FM from Bedrock on the assumption that newer models always outperform earlier versions and generalize better to analytical tasks.

C) Pick the FM that is cheapest per 1,000 tokens to minimize costs and assume that lower inference cost will not impact SQL correctness or reasoning ability.

D) Select the FM with the largest context window to ensure that the model can handle more input tokens, assuming this will automatically improve SQL accuracy and reasoning.

---

**Q53.** A company is developing a customer support platform that uses Amazon Comprehend for NLP and Amazon Bedrock to generate conversational responses. The front end communicates through Amazon API Gateway, which invokes an AWS Lambda function to send requests to the Bedrock API.

During load testing, the engineering team observes intermittent latency spikes and recurring ThrottlingException errors when the Lambda function calls the Bedrock API. The issues occur during high concurrency periods and degrade real-time response performance. The team must reduce throttling events and improve response resilience during peak traffic.

Which solution should be implemented to address these requirements?

A) Initialize exponential backoff with jitter in the AWS SDK to smooth retry behavior, and configure API Gateway per-client throttling limits to regulate request bursts before they reach Lambda.

B) Use AWS Step Functions to orchestrate each Bedrock API call and apply fixed retry intervals to reduce throttling during peak times.

C) Configure Lambda reserved concurrency so a fixed number of execution environments remain available to handle peak API call volume.

D) Enable AWS Global Accelerator to optimize latency when the Bedrock API is invoked from the Lambda function.

---

**Q54.** A global e-commerce marketplace is developing an AI moderation pipeline to validate product listings before publication. The system generates refined product descriptions, policy-aligned safety disclaimers, and multilingual variants using several foundation models hosted on Amazon Bedrock. Amazon Rekognition classifies product images for restricted categories, and Amazon Translate generates multilingual baseline references to verify cross-language consistency.

To comply with international marketplace rules and safety standards, the compliance team must evaluate multiple models at scale. The evaluation must analyze outputs for harmful content, regulatory violations, accuracy of multilingual generations, and overall policy alignment. Manual review and regex-based filters are insufficient due to volume and linguistic diversity. The solution must automate evaluation with minimal operational overhead.

Which solution will best meet these requirements?

A) Use AWS Lambda with keyword lists and regex filters to count unsafe terms, then compare violation counts across candidate models.

B) Index generated descriptions in Amazon OpenSearch and compare vector similarity scores to identify which model produces more consistent outputs.

C) Use LLM-as-a-judge within Amazon Bedrock Model Evaluation to automatically score generated descriptions for policy compliance, contextual safety, multilingual accuracy, and consistency.

D) Perform RAG evaluation using Amazon Bedrock Knowledge Bases to validate retrieval and content grounding across product categories.

---

**Q55.** A global insurance provider is modernizing its GenAI platform that combines Amazon Bedrock for LLM inference and Amazon SageMaker AI for model customization. The company mandates strict role-based access control so only authorized data scientists, analysts, and operations engineers can use these services.

The enterprise already uses Microsoft Entra ID as its centralized identity provider and wants AWS access to be federated through Entra ID without creating IAM users. The solution must provide centralized identity lifecycle management and enforce fine-grained permissions for Bedrock and SageMaker AI.

Which combination of steps will meet these requirements? (Select TWO.)

A) Create IAM users for all employees and manage password policies through Entra ID pass-through authentication. Attach Bedrock and SageMaker policies directly to each IAM user.

B) Implement SAML 2.0 federation between Entra ID and AWS IAM by mapping Entra ID security groups to IAM roles that contain scoped permissions for Bedrock and SageMaker AI.

C) Set up AWS IAM Identity Center with Microsoft Entra ID as an external identity provider. Use SCIM provisioning and IAM Identity Center permission sets to grant role-based access to Bedrock and SageMaker AI.

D) Use AWS IAM Identity Center with an OpenID Connect (OIDC) provider configuration for Entra ID authentication and assign permission sets for Bedrock and SageMaker access.

E) Develop a custom identity proxy service that authenticates to Entra ID, exchanges tokens through a Lambda authorizer, and injects AWS temporary credentials for Bedrock and SageMaker operations.

---

**Q56.** A global logistics intelligence platform uses an FM in Amazon Bedrock to generate anomaly explanations and delivery-delay summaries for operations teams. The system runs primarily in a single Region and uses AWS Step Functions to orchestrate inference workflows. During seasonal demand spikes, the team notices intermittent Bedrock throttling and occasional Regional degradation. The platform must continue operating even when the primary Region has limited availability. It must also fall back gracefully to a lightweight rules-based summary generator when FM capacity is severely constrained. The architects want the solution to require minimal code changes and avoid manual failover procedures.

Which combination of steps will ensure a resilient and continuously available FM workflow? (Select TWO.)

A) Wrap FM calls in an AWS Step Functions workflow that implements a circuit breaker pattern. Detect repeated timeouts or throttling from Bedrock and route failed invocations to a graceful degradation branch that uses a smaller FM or cached responses instead of failing user requests.

B) Increase the provisioned throughput allocation for the FM in the primary Region and rely on automatic retries from the AWS SDK to handle transient errors, without changing any Regional configuration.

C) Configure Amazon Bedrock Cross-Region Inference to use a primary FM in the existing Region and a secondary FM in a nearby Region. Point the application to the Bedrock cross-Region endpoint so traffic automatically shifts to the secondary Region when the primary has limited availability.

D) Deploy a duplicate copy of the RAG pipeline in a second AWS account and require operators to flip a feature flag and redeploy the application when the primary Region experiences issues.

E) Use Amazon API Gateway and AWS Lambda as a proxy in front of the Bedrock endpoint and configure Amazon Route 53 weighted routing across two API Gateway endpoints in the same Region to spread traffic and reduce throttling.

---

**Q57.** A global insurance company is building an internal generative AI platform that uses Amazon Bedrock across multiple business units. To ensure consistent FM behavior, leadership requires strict governance over prompts, including version control, approval workflows, and operational visibility. The platform must support parameterized prompt templates for different departments, maintain a central repository for approved templates, and track all prompt usage for compliance reviews. The solution must minimize custom governance code and rely on managed AWS services.

Which solution will MOST effectively meet these requirements?

A) Use Amazon Bedrock Prompt Management for parameterized templates and approval workflows, store approved templates in Amazon S3, enable AWS CloudTrail to track Bedrock API usage, and configure Amazon CloudWatch Logs for prompt access logging.

B) Use Amazon DynamoDB to store prompt templates, use Step Functions to create approval workflows, use AWS X-Ray to trace prompt calls, and use EventBridge to notify teams of changes.

C) Use Amazon API Gateway with usage plans to enforce prompt access control, store templates in AWS CodeCommit, and use CloudWatch Alarms to track abnormal usage patterns.

D) Use AWS Lambda functions to manage template versioning, store templates in Amazon S3, use Athena queries for access tracking, and require manual approval steps through email notifications.

---

**Q58.** A GenAI developer is building a generative AI platform using Amazon Bedrock and Amazon SageMaker AI to enable both internal teams and external partners to access and utilize large language models and AI services. The goal is to integrate the solution with the current identity provider (IdP) to enable secure user authentication. Additionally, it must provide temporary access to users for Bedrock and SageMaker AI, eliminating the need for long-lived credentials, while maintaining detailed audit logs of user activity to meet compliance requirements.

Which of the following should be implemented? (Select TWO.)

A) Utilize AWS IAM Identity Center with SAML-based federation to integrate the IdP, and configure it to grant users access to Bedrock and SageMaker AI using customized permission sets.

B) Set up an API Gateway with an AWS Lambda authorizer that verifies user credentials against the Lightweight Directory Access Protocol (LDAP) system and issues JSON Web Tokens (JWTs) for accessing Bedrock and SageMaker AI.

C) Configure AWS Lambda to authenticate users directly against the IdP and then issue temporary access tokens for Bedrock and SageMaker AI.

D) Configure Amazon Cognito to integrate with the current IdP via OpenID Connect (OIDC) and enable it to authenticate users, exchange tokens for temporary AWS credentials, and provide access to Bedrock and SageMaker AI.

E) Use AWS Organizations to set up cross-account access and manage permissions for users accessing Bedrock and SageMaker AI through IAM roles.

---

**Q59.** A media analytics company is designing a flexible model interaction layer for its GenAI summarization and categorization services. The system must support both real-time synchronous requests for interactive applications and asynchronous batch submissions for large video-processing workloads. The company uses Amazon Bedrock for inference and wants a design that supports multiple compute environments, standardized request validation, and a decoupled architecture that can scale independently for each workload type.

Which combination of solutions will meet these requirements? (Select TWO.)

A) Use language-specific AWS SDKs running on ECS tasks to submit asynchronous summarization jobs to an Amazon SQS queue. Process the queue with a Lambda consumer that invokes Amazon Bedrock and stores results in S3.

B) Route all summary generation requests directly from clients to the Bedrock runtime API to avoid middleware and reduce latency.

C) Use Amazon API Gateway to expose a synchronous inference endpoint backed by AWS Lambda. Validate request payloads at the API layer before calling the Bedrock InvokeModel API.

D) Use Amazon EventBridge Pipes to automatically throttle synchronous client traffic and buffer requests before fan-out to the Bedrock API.

E) Deploy a single monolithic EC2 instance hosting a custom REST endpoint that handles all synchronous and asynchronous inference workflows in one place.

---

**Q60.** A financial research firm deploys a GenAI summarization engine on Amazon Bedrock to assist analysts with real-time market briefings. After several weeks in production, the engineering lead notices irregular spikes in token usage, subtle degradation in summary accuracy, and occasional hallucinated numerical values. Leadership requests a comprehensive monitoring approach that can proactively identify anomalies, evaluate hallucination rates, analyze prompt effectiveness, and correlate performance with token consumption trends. The solution must rely on managed AWS services, avoid building a custom analytics pipeline, and allow teams to investigate detailed request/response behavior.

Which solution will BEST meet these requirements?

A) Enable Amazon Bedrock Model Invocation Logs for detailed request and response analysis, configure Amazon CloudWatch metrics to track token usage, hallucination indicators, and prompt-effectiveness KPIs, and use CloudWatch anomaly detection and dashboards to proactively identify drift and correlate performance with token patterns in a unified managed interface.

B) Export all Bedrock FM inputs and outputs to Amazon S3, build a custom prompt-evaluation engine on AWS Lambda, visualize hallucination and drift statistics in Amazon QuickSight, and generate weekly analyst performance reports via scheduled Athena queries.

C) Enable AWS CloudTrail data event logging for Bedrock API calls, configure an EventBridge rule to trigger alerts on elevated request activity, and create a Lambda function that summarizes prompt trends and token anomalies into a daily email digest.

D) Stream FM invocation data into Amazon Kinesis Data Firehose, create a feature-drift detection workflow in SageMaker Model Monitor, and deliver corrective performance recommendations to the engineering team through SNS notifications.

---

**Q61.** A media intelligence platform uses multiple foundation models (FMs) from Amazon Bedrock for tasks such as summarization, classification, and content rewriting. The engineering team wants to switch between different FMs and even different providers without deploying new code. The platform currently routes all inference requests through a shared AWS Lambda function that is invoked by an Amazon API Gateway endpoint. The company wants to introduce a mechanism that allows product teams to adjust FM selection in real time during experimentation, failover, or regional capacity constraints. The solution must avoid code changes, deployments, or service interruptions while allowing controlled configuration updates.

Which solution will meet these requirements with the LEAST operational overhead?

A) Use Amazon DynamoDB to store multiple FM routing rules. Require the engineering team to manually update environment variables and redeploy the Lambda function after each FM change.

B) Use Amazon S3 to store a JSON configuration file that contains the active FM name. Configure the Lambda function to download and cache the file on cold start, updating only when the function is redeployed.

C) Create multiple API Gateway stages, each mapped to a different FM provider. Instruct clients to switch between stages based on which model they want to use.

D) Use AWS AppConfig to store the active FM and provider configuration. Have the Lambda function read the AppConfig value at runtime to determine which model to invoke, enabling dynamic FM switching without code changes.

---

**Q62.** A healthcare analytics company is developing a generative AI workflow that summarizes patient case files and produces structured diagnostic reports. The workflow uses an Amazon Bedrock FM for summarization, AWS Lambda functions for data preprocessing, and a multi-step orchestration built with AWS Step Functions.

During testing, the engineering team notices that occasionally the FM produces extremely long or repetitive responses, causing downstream Lambda tasks to time out. There are also intermittent FM API failures that cause the entire workflow to retry excessively and exceed SLA limits. The solution must prevent runaway FM behavior, enforce strict execution boundaries, and gracefully degrade when repeated failures occur—without requiring manual operator intervention.

Which solution will meet these requirements?

A) Use AWS Step Functions with a built-in circuit breaker to halt the workflow after repeated Bedrock API failures, implement a Step Functions choice state to enforce FM output length stopping conditions, and add Lambda timeouts to cap downstream processing.

B) Use an SQS queue between Step Functions states so that FM responses exceeding the token limit are placed back into the queue for delayed reprocessing until they meet output constraints.

C) Set a global maximum concurrency limit on the Lambda functions so that excessive FM retries are throttled automatically without making changes to Step Functions logic.

D) Configure Amazon CloudWatch Alarms to stop the workflow whenever the Bedrock invocation count exceeds a threshold and send an SNS notification for operators to manually restart the workflow.

---

**Q63.** A global cybersecurity consultancy is developing an internal GenAI system to assist analysts in reviewing incident reports, generating threat summaries, and drafting customer notifications. The system uses Amazon Bedrock for text generation and Amazon Comprehend for entity extraction. During testing, red-team testers successfully bypass safety prompts by embedding malicious instructions within long narrative inputs, causing the FM to output unauthorized remediation steps. The security team must implement an advanced threat detection approach that identifies and mitigates prompt injection attempts, encoded jailbreaks, and adversarial manipulation of both the input text and FM outputs.

The solution must support automated evaluation during development and provide real-time protection in production. It should require minimal custom model training while providing layered detection mechanisms.

Which solution BEST satisfies these requirements?

A) Configure IAM policies to restrict access to sensitive APIs and require all inputs to follow a fixed schema enforced by API Gateway, relying on static prompt constraints within the FM to block adversarial behavior.

B) Use a multi-stage input validation workflow where a Lambda function sanitizes incoming text, a threat classifier detects prompt injection attempts, Bedrock Guardrails filter unsafe segments, and an automated adversarial testing pipeline continuously evaluates new attack patterns.

C) Use CloudWatch metric filters to detect anomalies in FM response length or token usage, triggering alerts when unusual generation patterns appear.

D) Deploy an Amazon SageMaker model trained on internal red-team attack samples to classify threats, and block any input classified as high-risk before the FM is invoked.

---

**Q64.** A global media analysis company is developing a multimodal generative AI pipeline that ingests customer-support phone recordings, product images, and troubleshooting notes. The goal is to build an FM-powered assistant that can summarize interactions, detect product defects, and extract structured issue categories. The data engineering team needs a standardized workflow to preprocess audio, images, and text before feeding them into a multimodal foundation model. The solution must support large-scale batch processing, avoid custom infrastructure, and ensure that each data type is transformed into FM-ready formats.

Which solution will meet these requirements with the least operational overhead?

A) Use a single AWS Lambda function to perform audio transcription, image resizing, and text normalization for all file types as they arrive in S3.

B) Depend on Amazon Bedrock alone to automatically convert raw audio, images, and tabular data into usable embeddings without any preprocessing workflows.

C) Use SageMaker Processing jobs to run batch preprocessing scripts for all data types. Integrate Amazon Transcribe to convert audio to text, apply image preprocessing inside the Processing container, and output normalized text, image tensors, and metadata for downstream multimodal FM consumption.

D) Create an AWS Glue ETL pipeline to extract, clean, and normalize all multimodal data into Parquet files, then pass the Parquet dataset directly into a multimodal FM.

---

**Q65.** A global hospitality company is enhancing its Amazon Lex–based concierge assistant that helps customers request services such as “spa,” “guided tours,” and “local dining.” The Lex bot uses a Lambda function to query an Amazon DynamoDB table for package options based on the detected category.

During validation, the Generative AI Developer notices that user phrases such as “pamper session,” “food spots,” and “city walk” are not being matched, even though these map to existing service categories. The company plans to explore Amazon Titan embeddings later, but it needs a quick fix without modifying Lambda code, the DynamoDB schema, or intent structures.

Which action should the developer take to improve recognition of these user inputs?

A) Define the unrecognized words as synonyms linked to the correct enumeration values in the custom slot type.

B) Add runtime hints to the slot values so Lex can resolve similar user inputs more effectively.

C) Expand the slot enumeration list by manually adding each of the unrecognized words as separate values.

D) Create additional intents that include the new phrases as sample utterances for improved matching.

---

**Q66.** A data science team is running an anti–financial-crime workload using Amazon SageMaker Training and SageMaker Feature Store. Transactional features are stored in the Feature Store offline store and periodically retrieved for scheduled retraining jobs. The model is a binary fraud classifier used for real-time payment screening. However, the team is seeing very high false negatives, despite overall accuracy exceeding 96%. Fraud events represent less than 0.5% of all transactions, and historical fraud examples remain extremely scarce.

The team must directly address the severe class imbalance before the next retraining cycle to increase detection performance.

Which solution will increase the fraudulent case detection performance?

A) Enable early stopping in SageMaker to automatically halt training when the model’s accuracy on the validation set no longer improves.

B) Enable automatic model tuning in SageMaker using Bayesian Optimization to find the best hyperparameters by running multiple training jobs. Increase the number of hyperparameter tuning jobs to explore a broader range of hyperparameter values and potentially improve model performance.

C) Perform random oversampling on the non-fraudulent transactions to equalize batch sizes during training.

D) Integrate a preprocessing step that applies the Synthetic Minority Oversampling Technique (SMOTE) on the minority fraudulent transaction class only before the training run begins.

---

**Q67.** A multinational insurance provider is deploying an enterprise-wide generative AI platform built on Amazon Bedrock and Amazon SageMaker AI. The platform generates policy summaries, assists with claim reviews, and provides underwriting insights. Because the system processes regulated financial and personal data, the compliance office requires a framework that documents model behavior, tracks all data sources used during training, and provides auditable reasoning traces for every generated output. Additionally, auditors must be able to review historical versions of the models, including the datasets, parameters, and decision logs associated with each output.

The engineering team needs a solution that minimizes manual documentation effort, automatically captures data lineage, and ensures end-to-end traceability across all AI workflows.

Which solution BEST meets these requirements?

A) Use Amazon Bedrock Guardrails to create compliance summaries, store model version metadata in Amazon S3, and configure VPC Flow Logs to capture model interaction history.

B) Generate programmatic model cards with SageMaker AI, use AWS Glue to capture and track data lineage for all training sources, apply metadata tags for source attribution, and stream detailed decision logs to CloudWatch Logs for compliance review.

C) Configure AWS Config rules to detect changes to AI resources and export configuration snapshots to an audit S3 bucket, using these snapshots to document model provenance.

D) Store all training datasets and model artifacts in Amazon S3 with versioning enabled, and use Amazon Athena queries to manually reconstruct model lineage for compliance audits.

---

**Q68.** An enterprise is designing a generative AI customer-support assistant that must deliver highly relevant, personalized answers in real time. The system processes large amounts of structured and unstructured content, including troubleshooting guides, device manuals, support transcripts, and diagnostic notes. To provide accurate results at scale, the architecture must combine semantic document retrieval with customer-specific personalization.

The engineering team has selected Amazon Kendra to retrieve intent-aligned documents and Amazon Personalize to tailor recommendations based on each customer’s historical interactions. The team must integrate these services with a Bedrock-powered LLM so that retrieval, ranking, personalization, and generation operate in a single, cohesive workflow without maintaining separate data pipelines.

Which solution best meets these requirements?

A) Use Bedrock Prompt Flows as an orchestration layer where Kendra retrieval and Personalize signals are invoked separately, and store outputs in external systems without using a unified knowledge store.

B) Continuously ingest support documents through Bedrock Data Automation and run Kendra and Personalize independently, merging results manually before generating a final answer.

C) Precompute document embeddings with Bedrock Customizations and process Kendra retrieval results in a standalone pipeline, then call Personalize in a separate workflow to rank articles.

D) Use an Amazon Bedrock Knowledge Base with hybrid search and enrich documents with Kendra metadata, then integrate Amazon Personalize to rank and personalize retrieved content before passing it to the LLM.

---

**Q69.** A fintech startup is developing a generative AI advisor that assists customers with investment planning. During controlled testing, the engineering team observes that the FM produces noticeably different recommendations when prompts are rephrased with small wording adjustments. To diagnose the issue, the team prepares a grouped evaluation dataset where each investment question includes multiple lightly reworded prompt variants. The team wants a fully managed method to measure the FM’s response stability and identify statistical differences across prompt clusters, without building custom evaluation pipelines.

Which solution will provide the required quantitative robustness analysis?

A) Launch an Amazon Bedrock model evaluation job using the grouped prompt dataset and enable robustness metrics to assess statistical variation across closely related prompts.

B) Use Bedrock batch inference to generate responses for each prompt variant and compute cosine similarity scores in Amazon Athena to identify output differences.

C) Create a Step Functions pipeline that repeatedly invokes the FM with random paraphrasing injected into the system prompts, then perform manual analysis of the response patterns.

D) Run a SageMaker Processing job that invokes the FM with all prompt variants and applies a custom semantic-drift scoring algorithm to measure divergence.

---

**Q70.** A logistics company is building an AI operations agent using Amazon Bedrock Agents. The agent performs tasks such as computing optimized shipment routes, summarizing delivery exceptions, and triggering warehouse automation tools through chained API calls. After introducing several new tools, the engineering team noticed inconsistent reasoning paths and frequent tool mis-selections that caused incomplete workflows and incorrect outputs. The company needs a structured evaluation strategy that can measure how effectively the agent completes multi-step tasks, verify that it selects the correct tools at each step, assess reasoning quality across different agent versions, and automatically identify weak points before the updated agent configuration is deployed to production.

Which solution best meets these requirements?

A) Use Amazon Kendra to index historical agent outputs and compare them with new agent responses to detect reasoning inconsistencies.

B) Use CloudWatch Logs to monitor API calls for each tool and manually review whether the agent chose the correct tool based on call patterns.

C) Use Amazon Bedrock Agent Evaluations to run automated task-completion tests, evaluate tool-use accuracy, and analyze reasoning quality across multi-step workflows before deployment.

D) Use SageMaker Experiments to track agent configuration metadata and compare different versions to determine which configuration performs best.

---

## ANSWERS

_Not yet attempted. Answer key, per-question domain tags, and domain distribution will be added after grading._
