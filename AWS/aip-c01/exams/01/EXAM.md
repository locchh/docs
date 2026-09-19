# Exam 1

> AWS Certified Generative AI Developer – Professional | 70 questions across 5 domains

## QUESTIONS

**Q1.** A biomedical research company is developing an internal GenAI assistant that retrieves experiment logs, laboratory protocols, safety guidelines, and molecular datasets from multiple vector stores. The data resides in Amazon OpenSearch Service for semantic search, Aurora PostgreSQL with pgvector for structured embeddings, and an Amazon Bedrock Knowledge Base that stores scientific summaries. The engineering team wants foundation models to query all sources consistently through a single interface, without exposing the underlying storage differences. They also need a mechanism that allows FMs to invoke vector search actions programmatically during a conversation.

Which integration approach should they implement to provide a unified, consistent access mechanism for all vector retrieval operations?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Use OpenSearch cross-cluster search to unify all vector retrieval needs across the different storage systems.

B) Use Amazon Bedrock function calling to define a standardized "vectorSearch" action that routes search requests to the appropriate backend, supported by an MCP client to manage multi-store vector queries.

C) Use Step Functions to orchestrate keyword searches across OpenSearch and Aurora, then concatenate the results before sending them to the model.

D) Use Lambda functions to batch-retrieve embeddings from all vector databases simultaneously to increase retrieval speed.

---

**Q2.** A financial services company is building an autonomous AI system that assists analysts with fraud investigations. The solution must maintain evolving case context, share findings between specialized agents (for example, a transaction-pattern agent and a customer-behavior agent), and coordinate tool interactions such as querying historical case data and retrieving supporting documents. The architecture must allow agents to store intermediate reasoning, remember prior steps, and collaborate without losing state across multi-step investigations.

Which approach should the team implement to meet these requirements?

**Domain:** 2 – Implementation and Integration

A) Use Amazon EventBridge scheduling to trigger periodic recomputation of agent output and rely on S3 to store intermediate text files for each investigation step.

B) Deploy multiple stand-alone Lambda functions triggered in sequence, passing raw model output between them as JSON without a shared memory layer.

C) Use Strands Agents with AWS Agent Squad to coordinate multiple specialized agents and maintain persistent shared state, combined with MCP-based tool interaction for accessing external resources.

D) Use a single large FM prompt that instructs the model to remember all prior steps and infer how to collaborate across tasks without external state storage.

---

**Q3.** A financial analytics company is building a semantic search engine that indexes regulatory filings, compliance checklists, and legal summaries. The documents vary significantly in length, and the team observed degraded retrieval quality when using a low-dimensional embedding model. The lead AI engineer needs an embedding approach that improves semantic precision for dense, domain-specific text while supporting large-scale batch generation of embeddings.

Which solution BEST meets these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Generate embeddings during inference using a Bedrock text model instead of a dedicated embedding model.

B) Use Amazon Titan high-dimensional embeddings and batch-generate vectors with a Lambda-based parallel processing workflow.

C) Use a lightweight embedding model with reduced dimensionality to minimize storage and compute costs.

D) Use semantic chunking with a breakpoint threshold and rely on a fixed 768-dimension embedding model for all documents.

---

**Q4.** A financial services company is building an internal generative AI assistant using Amazon Bedrock to help analysts summarize regulatory filings and justify recommendations. The company must increase transparency so end users can understand how each response was produced. The governance team requires user-facing explanations of model reasoning, full visibility into retrieval steps and intermediate agent actions, confidence and uncertainty metrics with each response, and clear source attribution for extracted evidence. The engineering team wants a solution that provides all transparency features with minimal custom code and without building an external observability system.

Which approach BEST meets these requirements?

**Domain:** 3 – AI Safety, Security, and Governance

A) Enable Amazon Bedrock agent tracing to capture reasoning steps, integrate CloudWatch metrics to store confidence scores, and present model-generated reasoning displays and attributed evidence directly in the application UI.

B) Build a custom middleware layer in AWS Lambda that logs each inference, computes uncertainty scores manually, and enriches responses with structured metadata.

C) Export raw model prompts and responses to Amazon S3, build a custom analytics pipeline in AWS Glue, and surface insights with Athena and QuickSight dashboards.

D) Use Amazon SageMaker Clarify to generate model explainability reports for each FM inference call and store the results in Amazon S3 for analyst review.

---

**Q5.** A financial compliance analytics firm is deploying a foundation-model-powered document review system using Amazon Bedrock and Amazon SageMaker AI. The system processes confidential regulatory filings stored in an internal data lake. Because the documents contain sensitive information, the security team requires end-to-end environmental protection: the FM must run in an isolated environment with no public internet exposure, access to data must be fully governed, and all read/write activity must be monitored for unauthorized access attempts. The firm wants a secure architecture that enforces least privilege, prevents accidental data exfiltration, and provides continuous visibility into data-access behavior.

Which solution BEST ensures a protected AI environment for this deployment?

**Domain:** 3 – AI Safety, Security, and Governance

A) Use API Gateway with request throttling to restrict access to the model and store compliance documents in encrypted S3 buckets without additional access-control layers.

B) Deploy the FM in a public subnet with security groups that block outbound access, and store data in S3 with default bucket policies while using CloudTrail for auditing.

C) Use VPC endpoints to isolate all Bedrock and S3 traffic, enforce least-privilege access using IAM and Lake Formation for fine-grained permissions, and use CloudWatch to monitor and audit data-access patterns across the entire workflow.

D) Enable network isolation in SageMaker AI and store all documents in a private S3 bucket without configuring Lake Formation or IAM resource policies.

---

**Q6.** A media analytics company uses an Amazon Bedrock knowledge base to index research articles stored across several Amazon S3 buckets. The company wants to closely monitor ingestion operations so that the engineering team can quickly identify failures such as parsing errors, missing metadata, or documents that failed to vectorize. The debugging process must support querying logs to isolate problematic documents and analyze ingestion patterns across all S3 sources.

Which solution will provide the required visibility into knowledge base ingestion and processing?

**Domain:** 5 – Testing, Validation, and Troubleshooting

A) Use Amazon Bedrock model invocation logging to capture detailed metrics for embedding generation and use the logs to track ingestion failures.

B) Enable AWS CloudTrail to record API calls related to knowledge base operations and use CloudTrail Lake to analyze ingestion events.

C) Configure knowledge base logging with Amazon CloudWatch Logs as the destination. Use CloudWatch Logs Insights to search for ingestion failures and analyze processing behavior.

D) Enable Amazon CloudWatch Application Signals to automatically monitor ingestion performance and generate alerts for ingestion anomalies.

---

**Q7.** A healthcare analytics company is integrating a third-party clinical decision support tool with Amazon Bedrock. The company requires secure authentication that works with its existing corporate identity provider (IdP). The solution must provide temporary, short-lived access to Amazon Bedrock, remove the need for storing long-term credentials, and generate comprehensive audit logs of all authentication and Bedrock API calls. The company also wants a fully managed approach that minimizes custom authentication code.

Which solutions will meet these requirements? (Select TWO.)

**Domain:** 3 – AI Safety, Security, and Governance

A) Deploy AWS IAM Identity Center with SAML federation to the corporate IdP. Configure permission sets that grant Bedrock access for authenticated sessions.

B) Create an IAM role and configure AWS STS AssumeRole federation, storing long-term IAM user credentials in the application configuration.

C) Implement an OpenID Connect (OIDC) integration with Amazon Cognito. Configure the integration to authenticate users through the corporate IdP and exchange tokens for temporary AWS credentials that allow access to Amazon Bedrock.

D) Configure an API Gateway Lambda authorizer that validates credentials against the corporate LDAP directory and issues custom JWTs for Bedrock access.

E) Create IAM users for each analyst and rotate credentials by using AWS Secrets Manager. Assign fine-grained access through IAM policies.

---

**Q8.** A global logistics company is developing a GenAI route-planning assistant on Amazon Bedrock to help analysts generate optimized delivery summaries for large fleets. Early testing shows significant variation in output quality across different foundation models and prompt templates. Leadership requests a systematic evaluation approach that can compare multiple FM configurations, measure cost-performance tradeoffs, track latency-to-quality ratios, and identify the optimal model and prompt combination without building custom experimentation infrastructure.

Which solution will BEST meet these requirements?

**Domain:** 5 – Testing, Validation, and Troubleshooting

A) Enable CloudTrail API activity logging for all FM interactions, create EventBridge rules to detect latency spikes, and have a developer periodically review samples of model outputs to estimate overall performance trends.

B) Run Amazon Bedrock Model Evaluations to compare multiple FMs and prompt variants, analyze quality metrics and latency-to-cost ratios through the managed evaluation reports, and use the results to select the optimal configuration based on empirical performance scores and token efficiency.

C) Deploy three different Bedrock FMs into production simultaneously, collect user satisfaction survey results for each, and manually calculate quality differences and cost impacts using weekly usage data exports from the billing dashboard.

D) Stream all prompt and response data to Amazon Kinesis Data Streams, create a custom A/B testing engine on AWS Lambda, and generate periodic evaluation summaries using Athena queries and scheduled QuickSight dashboards.

---

**Q9.** A biomedical research organization is developing an AI assistant that helps scientists analyze complex gene-interaction datasets. The assistant must break down user queries into structured reasoning steps, call external analytical tools, validate intermediate results, and then continue reasoning based on those results. The engineering team wants to ensure the FM follows a deterministic sequence of thought-action-observation steps without losing track of prior reasoning.

Which approach should the team implement to meet these requirements?

**Domain:** 2 – Implementation and Integration

A) Use EventBridge pipes to chain multiple FM invocations together without enforcing structured execution or state transitions.

B) Use Amazon SQS to pass unstructured FM output between loosely connected Lambda functions that infer the sequence of steps dynamically.

C) Use a single Amazon Bedrock model invocation with an expanded prompt containing all possible reasoning steps and tool instructions embedded inline.

D) Use AWS Step Functions to orchestrate a ReAct-style reasoning pipeline, where each state triggers FM reasoning, executes tool calls, captures observations, and feeds structured outputs into the next step.

---

**Q10.** A pharmaceutical research organization is building domain-specific generative AI models to summarize clinical studies, extract trial outcomes, and generate structured regulatory reports. The AI engineering team fine-tunes several Amazon Bedrock-compatible foundation models using Amazon SageMaker AI with LoRA adapters. They need a lifecycle approach that allows them to register new fine-tuned versions, deploy them safely, automatically roll back if accuracy drops, and retire outdated model variants that no longer meet compliance standards.

The lead ML engineer must implement a standardized deployment and lifecycle workflow that minimizes risk and ensures consistent version control across environments.

Which approach BEST meets these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Upload each fine-tuned model as a separate container image to Amazon ECR and switch between them by updating the endpoint configuration manually.

B) Use SageMaker Model Registry to track and version fine-tuned models, deploy them through automated CI/CD pipelines with rollback support, and manage lifecycle transitions to retire or promote model versions.

C) Store each fine-tuned model manually in Amazon S3 with timestamped folder names and deploy them by updating a Lambda function environment variable.

D) Use a single SageMaker endpoint and overwrite the model artifacts in-place whenever a new fine-tuned version is produced.

---

**Q11.** A global healthcare provider is building a GenAI assistant using Amazon Bedrock to help clinicians summarize medical case notes and draft patient communication. During evaluation, the team observes that the model sometimes generates inappropriate medical advice, speculative diagnoses, or responses that could be considered unsafe in regulated environments. The company needs a framework that can systematically prevent harmful outputs, enforce safety rules at generation time, and ensure that responses involving medical recommendations follow deterministic, approved logic.

Which solution BEST prevents unsafe or harmful model outputs?

**Domain:** 3 – AI Safety, Security, and Governance

A) Configure the application front end to block user prompts that contain medical keywords before calling the model.

B) Forward all model responses to a batch analytics job in Amazon EMR that performs nightly scans for harmful content.

C) Enable Amazon S3 Object Lock on all training and inference data to avoid accidental corruption or unsafe modifications before model use.

D) Use Amazon Bedrock guardrails to filter and constrain model responses, and integrate specialized FM-based toxicity and safety evaluations, while applying text-to-SQL transformations for deterministic output in regulated scenarios.

---

**Q12.** A global consulting firm is building an internal GenAI assistant using Amazon Bedrock to help employees generate client summaries, rewrite emails, and answer policy-related questions. During pilot testing, the engineering team discovers that most daily requests are lightweight (grammar fixes, short rewrites, quick fact checks), while only ~8% of traffic involves complex multi-step reasoning. The team wants to reduce Bedrock costs and latency while maintaining high-quality responses for the small subset of complex queries.

Which deployment approach BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Automatically route every request to a SageMaker AI endpoint hosting a fine-tuned large model to maximize accuracy for all tasks.

B) Use a single medium-sized model for all requests to avoid complexity and achieve predictable performance across all user queries.

C) Implement an API-based model cascading strategy where a smaller, low-latency Bedrock model handles routine queries, and a larger, more capable FM is selectively invoked only when the task requires deeper reasoning.

D) Deploy only the largest available Bedrock model and enable provisioned throughput to ensure consistently high performance for all query types.

---

**Q13.** A national insurance company is deploying a large FM–powered claims-assistance system in Amazon Bedrock. Because the system will be reviewed by internal auditors and external regulators, the compliance team requires:

- End-to-end data lineage for all training and inference data
- Verifiable documentation describing model behavior, limitations, and evaluation results
- Full attribution for every data source feeding the system
- A centralized log trail showing major FM decisions and inference outputs

The AI engineering team must implement a compliance framework that automates these requirements without adding significant operational burden.

Which solution BEST meets the compliance objectives?

**Domain:** 3 – AI Safety, Security, and Governance

A) Use Step Functions to orchestrate all model workflows and export execution histories to CloudTrail for compliance visibility.

B) Configure Amazon Bedrock to export all inference prompts and responses to an SQS queue, then build a custom compliance dashboard using Lambda and DynamoDB.

C) Use SageMaker AI to programmatically generate and store model cards, configure AWS Glue Data Catalog to track data lineage and apply metadata tags for source attribution, and enable CloudWatch Logs to collect detailed inference decision logs.

D) Store model documentation manually in an S3 bucket, enable S3 access logs for compliance, and rely on IAM policies to ensure analysts can review historical model activity.

---

**Q14.** A logistics technology company is building a RAG application on Amazon Bedrock to help support agents troubleshoot shipment issues. The application retrieves many relevant documents, but agents report that the most useful information often appears low in the results list. The company wants to boost semantic relevance so high-value documents appear first. The team wants a solution that avoids custom ranking algorithms and minimizes operational overhead while staying within its Bedrock-based architecture.

Which combination of steps will MOST effectively improve the relevance of retrieved results with minimal operational overhead? (Select TWO.)

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Configure an Amazon Aurora PostgreSQL cluster with pgvector to store embeddings and implement a custom weighted ranking function using metadata and cosine similarity.

B) Build a custom SageMaker inference pipeline that merges BM25 keyword scoring with embedding-based similarity for a two-stage retrieval system.

C) Use Amazon Bedrock reranker models with Amazon OpenSearch Service to reorder retrieved documents based on semantic similarity to the agent's query.

D) Use Bedrock Knowledge Bases with hybrid search and Amazon OpenSearch Serverless to combine keyword relevance with semantic vector embeddings for improved ranking.

E) Use Amazon S3 inventory reports to generate a frequency-based scoring model that prioritizes documents with higher access patterns.

---

**Q15.** A global logistics company is building a centralized GenAI gateway that routes all employee prompts through a controlled abstraction layer before invoking Amazon Bedrock models. Each update to the gateway—such as new guardrails or prompt-safety rules—must be validated through automated tests and security scans. The company also requires an auditable release process with automatic rollback if a change causes unsafe or incorrect behavior in production.

Which deployment approach BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Host the gateway on an Amazon EC2 instance and use cron jobs to restart it when new versions are uploaded.

B) Build a CI/CD pipeline using AWS CodePipeline and CodeBuild, integrate automated test suites and security scans, and deploy the GenAI gateway behind API Gateway with automatic rollbacks enabled.

C) Use a Lambda function with versioning and aliases to manually deploy updates after developers run tests locally.

D) Deploy the GenAI gateway with Amazon ECS and push container image updates manually to Amazon ECR.

---

**Q16.** A digital publishing platform uses Amazon Bedrock to generate study summaries and quiz items for its online learning portal. The system combines instructor-approved reference material with large collections of scraped public content. Before any generated summary or quiz is published, quality reviewers must verify where the information originated to ensure the accuracy and credibility of the generated educational content.

The company wants to provide reviewers with a simple way to trace each generated output back to its original data sources. The solution must introduce the least operational overhead, support automated lineage tracking, and integrate cleanly with the existing Bedrock-powered generation workflow.

Which combination of steps will meet these requirements with the LEAST operational overhead? (Select TWO.)

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Register all curated and scraped source datasets in AWS Glue Data Catalog to provide structured, searchable metadata for reviewers.

B) Configure AWS CloudTrail to track reviewer approval actions for each generated summary or quiz.

C) Tag generated outputs with metadata that identifies the specific curated or scraped sources used during content generation.

D) Use Amazon SageMaker Clarify to produce explainability reports for each generated content item.

E) Use Amazon Bedrock invocation logging to track model usage and manually cross-reference invocation events with the original data sources.

---

**Q17.** A financial analytics company is developing an internal GenAI assistant using Amazon Bedrock to help analysts generate summaries of corporate earnings reports. During testing, the assistant often produces fabricated financial ratios and cites nonexistent data points when the requested information is missing from source documents. The company needs a verification system that reduces hallucinations, forces responses to stay grounded in authoritative financial data, and guarantees that all outputs follow a strict, machine-readable structure for downstream validation.

Which solution BEST reduces hallucinations while ensuring accurate, verifiable responses?

**Domain:** 3 – AI Safety, Security, and Governance

A) Use Amazon Bedrock Knowledge Base for grounding and retrieval-augmented fact-checking, apply confidence scoring with semantic similarity verification, and enforce structured model outputs with JSON Schema.

B) Store all financial documents in S3 Glacier Deep Archive to avoid accidental model access to incomplete datasets.

C) Enable Amazon GuardDuty and Security Hub to detect anomalous behavior in the financial summarization workflow.

D) Configure the assistant to return a generic fallback message whenever users request numerical data or financial metrics.

---

**Q18.** A global logistics company is developing a conversational assistant that provides shipment troubleshooting guidance to internal support teams. The system uses Amazon Bedrock for inference and must generate reliable answers using a structured prompt that includes the conversation history, user intent, and contextual metadata such as region and shipment priority. The AI engineering team notices inconsistent responses because developers are sending varied payload structures and unformatted text directly to the Bedrock endpoint.

To ensure consistent inference behavior across all environments, the lead AI engineer must enforce a standardized input format aligned with the Bedrock model's expected schema for dialog-style requests.

Which approach BEST satisfies this requirement?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Store conversation history in DynamoDB and let the model retrieve it dynamically without requiring formatting in the API request.

B) Append all conversation turns into a single newline-separated string and pass it as a single input field to the Bedrock API.

C) Send plain text prompts directly to Bedrock and rely on the model to infer the missing structure from user input.

D) Format each request using a standardized JSON structure that includes role-based message fields, system instructions, and contextual metadata before sending it to the Bedrock API.

---

**Q19.** A global policy research institute builds a generative AI assistant on Amazon Bedrock to help analysts produce summaries, policy briefs, and comparative country insights. After internal testing, reviewers report that some responses contain factual inconsistencies, uneven fluency, and contradictory interpretations across similar queries. Leadership requests a formal evaluation framework that can measure relevance, factual accuracy, consistency across regenerations, and linguistic fluency, while minimizing manual scoring and leveraging repeatable assessment workflows.

Which solution will BEST meet these requirements?

**Domain:** 5 – Testing, Validation, and Troubleshooting

A) Export all FM outputs to an S3 bucket and build a custom QuickSight dashboard that visualizes writing style, response length, and topic frequency trends for periodic evaluation.

B) Use CloudTrail event logs to track summary generation API activity and configure an EventBridge workflow that flags unusually long responses as potential accuracy risks, forwarding summaries to reviewers for validation.

C) Implement an automated FM evaluation framework using golden reference datasets with expected outputs, relevance scoring functions, factual-accuracy benchmarking prompts, and consistency checks performed through multi-pass output diffing to detect reasoning divergence across regenerations.

D) Require analysts to manually review a rotating sample of responses each day, document inconsistencies in a shared report, and escalate problematic outputs to the ML engineering team for follow-up investigation.

---

**Q20.** A cybersecurity analytics startup is building an internal GenAI assistant using Amazon Bedrock to help engineers summarize security reports and analyze threat intelligence data. During testing, the security team discovers that several prompts—intentionally crafted to obscure intent—are successfully bypassing existing input checks. These include disguised jailbreak attempts, indirect instructions, and adversarial phrasing designed to manipulate the model into revealing restricted information. The company needs an advanced threat detection pipeline that can identify adversarial inputs before they reach the FM, detect jailbreak behavior, and continuously evaluate the system against evolving attack patterns.

Which approach BEST provides robust protection against adversarial prompting attempts?

**Domain:** 3 – AI Safety, Security, and Governance

A) Implement multi-layer adversarial detection using input sanitization, prompt injection and jailbreak detection classifiers, and an automated adversarial testing workflow that feeds results to a continuous security evaluation pipeline.

B) Store all prompts in S3 and manually review them weekly for signs of adversarial activity.

C) Configure Amazon Bedrock with deterministic decoding by lowering temperature and disabling response streaming to prevent injection attacks.

D) Add a regex-based filter to API Gateway to block known malicious patterns before forwarding requests to the model.

---

**Q21.** A financial services company is designing an internal generative AI platform to help analysts summarize regulatory filings, classify risk disclosures, and generate compliance-ready reports. The AI engineering team plans to use multiple foundation models through Amazon Bedrock—one model for summarization, another for classification, and a third for generating structured compliance outputs. They also need an architecture that supports flexible model switching without code changes, enforces separation of concerns across services, and allows the platform to scale independently for each workload. The team must create an architecture that aligns with business requirements while handling these technical constraints.

Which architectural approach BEST satisfies these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Use AWS Step Functions to orchestrate all model calls in a single workflow with hardcoded task definitions for each model.

B) Use an Amazon EC2 instance running a custom inference server that handles routing logic across Bedrock models using local environment variables for configuration changes.

C) Use an API-based model routing layer with Amazon API Gateway and AWS Lambda to dynamically route requests to different Bedrock models, enabling modular services and configuration-based model switching.

D) Use a single monolithic Lambda function that invokes all Bedrock models based on conditional logic within the function.

---

**Q22.** A health-tech company builds a clinical-workflow assistant using an Amazon Bedrock FM to summarize patient notes and retrieve relevant medical guidelines. After deployment, physicians report inconsistent explanation quality and occasional weak citations. Leadership requests a comprehensive evaluation system that can assess outputs from multiple perspectives, including factual grounding, relevance of retrieved evidence, and clarity of reasoning. The system must use managed AWS services where possible, support LLM-as-a-Judge scoring, and allow human reviewers to provide structured feedback for continuous improvement.

Which combination of steps will BEST meet these requirements? (Select TWO.)

**Domain:** 5 – Testing, Validation, and Troubleshooting

A) Implement an LLM-as-a-Judge automated assessment method using a Bedrock model to rate clarity, reasoning quality, and citation strength, and integrate the scoring pipeline into the existing CI/CD evaluation process.

B) Embed unstructured physician feedback inside application logs and periodically search logs with Athena queries to identify "common wording patterns" that may indicate quality drift.

C) Implement RAG evaluation workflows by comparing FM outputs to retrieved ground-truth context, and use Amazon Bedrock Model Evaluations with custom metrics to score relevance, grounding, and factual alignment.

D) Use CloudWatch Logs to monitor token counts, latency spikes, and model throughput, and treat those patterns as indicators of output quality for future model evaluations.

E) Periodically export a random sample of generated summaries to S3 for manual review by the engineering manager, and approve releases whenever outputs appear subjectively acceptable.

---

**Q23.** A transportation research institute is developing a generative AI system that analyzes a combination of driver call recordings, dashcam footage, vehicle telematics logs, and written incident reports to generate comprehensive accident summaries. The system must extract speech transcripts, detect objects and road conditions from images, normalize structured tabular sensor data, and format everything into a multimodal prompt for an Amazon Bedrock model.

The AI engineering team needs a scalable workflow that can preprocess all data types, convert them into FM-ready formats, and orchestrate the multimodal pipeline efficiently.

Which approach BEST meets these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Create separate EC2 instances for each data type and have them run custom scripts, then upload the results to a shared S3 bucket for downstream model consumption.

B) Perform all preprocessing manually and upload the processed audio, images, and CSV files directly into Amazon S3 for the FM to interpret without additional orchestration.

C) Build a multimodal processing workflow using SageMaker Processing for image and tabular preprocessing, AWS Transcribe for audio-to-text conversion, and Amazon Bedrock multimodal models to consume the combined, formatted inputs.

D) Use a single Lambda function to process all audio, image, and tabular data types before sending the raw binary content directly to Amazon Bedrock.

---

**Q24.** A retail analytics company is building an interactive AI assistant that helps store managers interpret sales anomalies. The assistant uses Amazon Bedrock to generate insights, but users often submit vague messages such as "Why did yesterday look weird?" The AI engineering team wants the system to automatically detect missing intent, ask clarifying follow-up questions, and keep multi-turn conversation context available for future model calls. They also need durable storage to retrieve past conversation turns during the session.

Which architecture should the team implement to meet these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Store conversation history directly in Bedrock prompts without external storage to simplify flow management.

B) Use Amazon SQS to queue each message and process them sequentially for context preservation.

C) Use Lambda functions to rewrite vague questions before sending them to Amazon Bedrock.

D) Use Step Functions to orchestrate clarification workflows, Amazon Comprehend to detect user intent gaps, and DynamoDB to store and retrieve conversation history for context-aware responses.

---

**Q25.** A global media company is building an FM-powered summarization platform on Amazon Bedrock. To meet internal compliance policies, the solution must provide:

- End-to-end traceability of all ingested data sources
- Metadata attribution embedded in each FM-generated summary
- Auditable logs showing when each source was accessed
- A scalable, low-maintenance implementation

Which solution BEST satisfies these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Use Lambda to write data access records to Aurora and configure API Gateway to export request logs.

B) Use AWS Glue Data Catalog to register all source datasets, apply metadata tags for attribution during summary generation, and enable CloudTrail to record all data access events.

C) Store documents in S3 with folder-style prefixes, include the S3 path in summaries, and rely on S3 server access logs for traceability.

D) Create a DynamoDB table mapping document IDs to summaries and use CloudWatch Logs to track ingestion events.

---

**Q26.** A financial research company operates a retrieval-augmented generation (RAG) system that answers analyst questions using internal investment reports. The system uses Amazon Bedrock to generate embeddings and stores them in an Amazon OpenSearch Service vector index. A Lambda function runs both embedding creation and KNN search. After a recent code deployment, the system begins returning fallback responses such as "no relevant information available," even for prompts that previously produced accurate answers. CloudWatch Logs show no errors. X-Ray traces confirm successful model invocations. The OpenSearch cluster is healthy, and query performance remains normal.

What is the MOST likely cause of this issue?

**Domain:** 5 – Testing, Validation, and Troubleshooting

A) The application increased the Bedrock model temperature parameter during the update, causing inconsistent retrieval results.

B) The Lambda execution role is missing a new IAM permission required for Bedrock InvokeModel calls after the code update.

C) The document embeddings in the OpenSearch index were overwritten or deleted during deployment, requiring full re-indexing.

D) The updated Lambda function uses a different version of the embedding model, causing a mismatch between stored document embeddings and newly generated query embeddings.

---

**Q27.** A logistics technology company is building a generative AI assistant that supports multiple use cases, including shipment delay explanations, route optimization suggestions, and contract summary generation. The engineering team wants the ability to switch between different Amazon Bedrock models—such as one optimized for summarization and another for reasoning—without redeploying code. They also want the flexibility to switch model providers entirely as new FMs become available.

The lead AI engineer must design an architecture that supports dynamic model selection, configuration-driven switching, and zero code modifications during updates.

Which approach BEST meets these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Deploy all required foundation models in parallel and use an Amazon EC2 instance to manually route requests by updating environment variables on the instance.

B) Use multiple separate API Gateway endpoints, each dedicated to a single foundation model, and require clients to select the correct endpoint for their use case.

C) Create a routing layer using Amazon API Gateway and AWS Lambda, and store model selection parameters in AWS AppConfig so that model and provider choices can be switched dynamically without changing application code.

D) Hardcode the preferred foundation model into the Lambda function and update the code each time the model or provider changes.

---

**Q28.** A company is implementing new AI governance policies requiring that all foundation model (FM) interactions use Amazon Bedrock guardrails. The engineering team has configured the guardrails and must now ensure that every InvokeModel and Converse API call applies them automatically across all teams and applications. The solution must enforce compliance with minimal operational overhead and without introducing additional infrastructure.

Which solution will enforce guardrail compliance for the API calls in the MOST operationally efficient way?

**Domain:** 3 – AI Safety, Security, and Governance

A) Configure IAM policies for the InvokeModel and Converse API calls with the `bedrock:GuardrailIdentifier` condition key. Apply the policies to all IAM roles that access the Amazon Bedrock FMs.

B) Store guardrail identifiers in AWS Systems Manager Parameter Store. Create an AWS Lambda function that retrieves the guardrail identifier from Parameter Store each time before making calls to Amazon Bedrock FMs.

C) Configure IAM policies for the InvokeModel and Converse API calls with both `bedrock:GuardrailIdentifier` and `bedrock:PromptRouterArn` condition keys. Apply the policies to all IAM roles. Require prompt router validation before allowing access to Amazon Bedrock FMs.

D) Create an AWS Lambda function that validates and enforces guardrails before proxying requests to Amazon Bedrock. Use the Lambda function as the exclusive endpoint for all FM interactions.

---

**Q29.** A government research institute is deploying a generative AI system on Amazon Bedrock to help analysts review scientific grant proposals. Due to strict responsible AI regulations, the organization must ensure that every FM interaction complies with internal policy requirements, including content safety checks, restricted-topic filtering, and mandated disclosure of FM limitations. The governance team wants a solution that automatically enforces compliance, documents model constraints, and validates each request and response before downstream use. The engineering team must implement this without building a large custom enforcement layer.

Which approach BEST ensures policy-compliant AI behavior with minimal operational overhead?

**Domain:** 3 – AI Safety, Security, and Governance

A) Use an Amazon EC2–based microservice that performs full-text comparison of FM outputs against stored policy definitions before returning responses to analysts.

B) Use Amazon EventBridge to trigger a batch compliance workflow every night that analyzes a sample of FM responses and produces a compliance report for internal auditors.

C) Use Amazon SageMaker hosting endpoints with fully custom container validation logic and manually written policy rule scripts that run before each inference call.

D) Use Amazon Bedrock guardrails configured with the institute's policy rules, attach model cards describing FM limitations, and implement a lightweight AWS Lambda post-processing function to run automated compliance checks on each Bedrock response.

---

**Q30.** A media analytics startup wants to build an automated system that identifies emerging clothing patterns from global street-style photos and short-form runway video clips. The company wants to highlight trending color palettes, fabric types, and accessory pairings. The solution must process thousands of images and videos per day, extract visual attributes, and present aggregated insights in a business dashboard.

The engineering team wants the lowest operational overhead, minimal custom ML code, and a fully managed orchestration layer. The company prefers a serverless architecture and wants to avoid managing GPU infrastructure.

Which solution will meet these requirements with the LEAST operational overhead?

**Domain:** 4 – Operational Efficiency and Optimization for GenAI Applications

A) Use AWS Step Functions to orchestrate calls to Amazon Bedrock multimodal foundation models for image and video analysis. Store extracted attributes in Amazon S3 and use Amazon QuickSight dashboards to summarize trend patterns.

B) Deploy a containerized PyTorch model on Amazon ECS with GPU-based tasks. Stream video frames into the model, store attributes in Amazon OpenSearch Service, and build dashboards in OpenSearch Dashboards.

C) Build custom training pipelines with Amazon SageMaker to train a computer vision model for clothing classification. Use Amazon EMR to aggregate attributes and create dashboards in Amazon Managed Grafana.

D) Use Amazon Rekognition labels for all visual analysis and push results to Amazon DynamoDB. Build a custom UI that aggregates results and renders dashboards through an Amazon CloudFront distribution.

---

**Q31.** A media analytics startup uses Amazon Bedrock to power a real-time content summarization service for news and video transcripts. During peak viewing hours, the team notices rising model latency and occasional throttling. GPU utilization metrics show that the FM is underutilized during these spikes. The GenAI engineer must increase throughput and stabilize performance with minimal operational burden.

Which solution will MOST effectively improve throughput and GPU utilization?

**Domain:** 4 – Operational Efficiency and Optimization for GenAI Applications

A) Place Amazon SQS in front of the system and process requests serially to avoid throttling.

B) Reduce the max output tokens for all summaries to decrease model compute time.

C) Enable request batching in the application layer and tune batch size and batching timeout to increase FM parallelism during high traffic periods.

D) Increase the number of provisioned throughput units to the maximum supported level and keep them fixed at all times.

---

**Q32.** A global e-learning company is building an AI content-processing service that uses multiple Amazon Bedrock models for different tasks. Short user queries should be routed to a fast, low-latency LLM; long or technical queries should be routed to a larger, reasoning-optimized FM; and any requests containing code snippets should be sent to a code-specialized FM. The team requires a centralized mechanism that can run logic based on request content, apply conditional routing rules, evaluate model performance metrics over time, and easily evolve the routing logic without modifying the application code.

Which solution BEST meets these routing and maintainability requirements?

**Domain:** 2 – Implementation and Integration

A) Use AWS Step Functions with content-based branching to inspect the request payload and route it to the correct Bedrock model, combined with metric-based routing updates managed as state machine revisions.

B) Hardcode routing logic into the backend service and deploy a new version whenever routing rules or model selection criteria must be updated.

C) Store routing rules in Amazon S3 and have the application load them at runtime to decide which Bedrock model to invoke.

D) Use API Gateway request transformations to parse user requests and route them directly to different Lambda functions, each calling a different FM.

---

**Q33.** A healthcare analytics firm is integrating Amazon Bedrock into its clinical summarization workflow. During peak usage, the team notices intermittent 429 throttling errors and occasional transient network timeouts when invoking the model. The solution must automatically retry failed calls without overwhelming Bedrock, protect downstream systems from excessive traffic, and provide full request-path observability across API calls and retries.

Which approach BEST ensures a resilient and controlled FM invocation workflow?

**Domain:** 2 – Implementation and Integration

A) Deploy an EC2-based proxy that batches requests and holds them until Bedrock capacity is available, returning responses only after the full batch is processed.

B) Use the AWS SDK's exponential backoff and jitter for request retries, add API Gateway rate limiting in front of the FM invocation layer, and instrument all calls with AWS X-Ray for end-to-end tracing.

C) Increase the concurrency of the invoking Lambda function and let each function attempt retries independently without rate controls.

D) Implement a custom retry loop inside the application that retries immediately upon failure and logs errors to CloudWatch Logs.

---

**Q34.** A legal-tech startup builds a contract-analysis assistant using a retrieval-augmented generation (RAG) workflow on Amazon Bedrock. After onboarding several large document sets, attorneys report that the assistant sometimes retrieves irrelevant clauses or misses context needed for proper interpretation. The engineering team must implement a retrieval quality testing framework that evaluates relevance, verifies context alignment, and measures retrieval latency. The solution must require minimal custom infrastructure, support repeatable testing, and help optimize vector store performance.

Which combination of steps will BEST meet these requirements? (Select TWO.)

**Domain:** 5 – Testing, Validation, and Troubleshooting

A) Measure retrieval latency, index scan time, and query throughput using vector database performance metrics, and establish automated thresholds in CloudWatch to detect degradation and trigger alerts for optimization.

B) Implement a custom Lambda function that injects additional query expansion heuristics before each retrieval call and treats improved output fluency as an indicator of retrieval quality.

C) Run retrieval relevance tests by comparing retrieved passages against a labeled evaluation dataset, and track relevance and context-matching scores using Amazon Bedrock Model Evaluations or custom CloudWatch metrics to validate retrieval quality over time.

D) Use CloudTrail data events to review when retrieval APIs were called and infer retrieval quality based on the volume of requests and access frequency patterns.

E) Export all retrieved chunks to Amazon S3 and have legal teams manually review them weekly to identify mismatches and tag problematic documents for retraining.

---

**Q35.** A financial technology startup is building a GenAI-powered virtual assistant using Amazon Bedrock to help users understand loan terms and financial products. During testing, the team discovers that some users intentionally submit harmful, abusive, or manipulative prompts that could coerce the model into generating unsafe guidance. The company must enforce strict content safety checks before prompts reach the FM, and they also need a mechanism to escalate suspicious content for additional review. The solution must support real-time validation while preserving low-latency responses.

Which approach BEST implements a comprehensive content safety system for this workload?

**Domain:** 3 – AI Safety, Security, and Governance

A) Add client-side JavaScript validation that checks prompts for explicit keywords before calling the Bedrock API.

B) Enable CloudTrail data events on all Bedrock API calls and block requests that appear in the audit logs.

C) Use Amazon Bedrock guardrails for policy-based filtering and route rejected prompts through a Step Functions workflow that triggers a Lambda-based custom moderation review.

D) Implement an S3 event-driven pipeline that stores every prompt and triggers a nightly batch process to identify harmful content.

---

**Q36.** A logistics company is developing a generative AI assistant using Amazon Bedrock to automate shipment issue resolution. Each user request may require multiple reasoning steps: identifying the type of problem, checking shipment history, generating a proposed resolution, and escalating complex cases. The engineering team wants a prompt system that supports reusable prompt components, conditional branching based on FM responses (for example, escalate only if the FM detects "damaged package"), and multi-step processing that includes pre-processing of tracking IDs and post-processing of final recommendations.

Which approach should the engineering team implement?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Use Amazon EventBridge rules to route user queries to different prompt templates based solely on keyword matches.

B) Build multiple standalone prompts triggered by separate API endpoints, with logic handled manually by the client application.

C) Use Amazon Bedrock Prompt Flows to orchestrate sequential prompt chains with conditional branches, integrate reusable prompt modules, and include pre- and post-processing steps within the workflow.

D) Create a single extremely detailed monolithic prompt that embeds all possible instructions and relies on the FM to infer when to escalate or continue.

---

**Q37.** A large insurance company is modernizing its legacy claims-processing platform by integrating a new Amazon Bedrock–powered claims summarization service. The legacy system runs on-premises and can only send outbound HTTPS requests. The enterprise architecture team wants to ensure loose coupling, support asynchronous processing, and maintain consistent data flow between on-prem workloads and the new FM-based service. They also need real-time synchronization so downstream systems can consume AI-generated summaries as soon as they are ready.

Which integration approach BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Use an event-driven architecture where the on-prem system publishes claim update events to Amazon EventBridge, triggering a Lambda function that invokes the Bedrock model and writes results to a synchronized data store such as DynamoDB or Amazon S3.

B) Deploy a self-managed message queue inside the on-prem environment and periodically batch-upload queued messages to S3 for Bedrock processing.

C) Create a direct synchronous API Gateway → Bedrock integration and require the on-prem system to invoke Bedrock directly for each request.

D) Build a custom VPN-based connection so the on-prem system can directly access DynamoDB tables and write the AI-generated summaries in real time.

---

**Q38.** A financial analytics firm is developing a Python-based research agent that runs on Amazon Bedrock AgentCore Runtime to support complex financial data queries. The agent must support fast lookups with sub-second response times and long-running research report generation that may stream results for several minutes. The company wants to eliminate infrastructure management tasks such as configuring HTTP servers, defining /ping or /invocations routes, and building custom health checks. The firm also wants a deployment option that packages and deploys the agent with minimal manual setup.

Which combination of approaches will meet these requirements with the least operational overhead? (Select TWO.)

**Domain:** 2 – Implementation and Integration

A) Deploy the agent by using the AgentCore starter toolkit to automate packaging, containerization, and deployment workflows.

B) Implement a custom FastAPI server that manually defines the /ping and /invoke endpoints and package it within a container for deployment.

C) Use the AgentCore SDK with the entrypoint decorator to automatically generate server configuration, routing, and health checks.

D) Deploy the agent on Amazon SageMaker AI real-time endpoints by using a custom inference container.

E) Deploy the agent on Amazon ECS on AWS Fargate by using a custom container image that runs the AgentCore SDK application.

---

**Q39.** A large consulting firm is building an enterprise-wide generative AI assistant that retrieves information from multiple internal systems, including a document management platform (over 20 TB of stored PDFs), a Confluence-based engineering wiki, and a set of legacy application knowledge bases. The AI engineering team must design an integration layer that continuously synchronizes documents, extracts metadata, and pushes cleaned and normalized content into an Amazon Bedrock Knowledge Base for RAG-style retrieval.

The team wants to ensure reliable connectivity between all external content sources and AWS, maintain consistent formatting, and support incremental ingestion as documents are updated.

Which approach BEST meets these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Store all documents in Amazon RDS and require downstream FM applications to fetch and preprocess content at inference time instead of using an ingestion pipeline.

B) Use AWS Lambda to pull updated documents from external systems, enrich metadata and normalize formatting, and send processed content to an Amazon S3 ingestion bucket that feeds an Amazon Bedrock Knowledge Base.

C) Connect Amazon Bedrock Knowledge Bases directly to the external Confluence and document management systems and rely on Bedrock to handle synchronization without preprocessing.

D) Use Amazon DynamoDB Streams to directly capture document changes from the external systems and push updates into Bedrock without additional transformation.

---

**Q40.** A robotics manufacturer is building an internal GenAI assistant to help technicians troubleshoot hundreds of machine models. The content includes long operational manuals, nested safety procedures, and multi-level configuration guides. Updates often affect only specific sections, and the team wants accurate retrieval without reprocessing full documents.

Which document segmentation approach BEST meets these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Store each manual as a single chunk to preserve full document context.

B) Use semantic chunking with no overlap so content is split solely at natural boundaries.

C) Use fixed-size chunking with a uniform 1200-token limit and 25 percent overlap across all documents.

D) Use hierarchical chunking with large parent chunks for chapter context and smaller child chunks for precise retrieval, with controlled overlap for continuity.

---

**Q41.** A publishing startup uses an Amazon Bedrock–powered content editor to help writers generate article summaries and headlines. After launch, the product team receives inconsistent reports about summary clarity and factual correctness. Leadership requests a user-centered evaluation mechanism that allows writers to rate outputs, annotate issues, and feed structured feedback back into the evaluation pipeline. The mechanism must integrate cleanly with the existing application, require minimal custom infrastructure, and support continuous improvement of FM performance over time.

Which solution will BEST meet these requirements?

**Domain:** 5 – Testing, Validation, and Troubleshooting

A) Embed a feedback interface directly into the editor UI that captures user ratings, categorical issue tags, and inline annotations, store the feedback events in Amazon DynamoDB, and periodically analyze the feedback dataset to refine prompts and model configurations for continuous FM quality improvement.

B) Create a batch job in AWS Glue that processes all model inputs and outputs daily, generates quality estimates using heuristic scoring rules, and updates a metrics dashboard in Amazon QuickSight for periodic tuning cycles.

C) Export all editor interactions to Amazon S3, manually inspect random samples each week, and adjust FM configuration parameters based on observed quality gaps and common error themes identified by the product team.

D) Use CloudTrail logging to track all FM invocation activity, generate monthly performance summaries through EventBridge and Lambda, and send the summaries to the engineering team for manual review and tuning.

---

**Q42.** A financial advisory platform is developing a generative AI assistant using an Amazon Bedrock foundation model. Customer messages often contain sensitive financial details, legal case identifiers, and personal contact information. The engineering team must design a privacy-focused GenAI workflow that ensures:

- Sensitive content is removed or transformed before being sent to the FM
- FM responses cannot reveal or reconstruct original identifying details
- Downstream analytics processes can still gain insights without accessing raw PII

Which solution BEST satisfies these requirements while maintaining FM utility?

**Domain:** 3 – AI Safety, Security, and Governance

A) Use Amazon Comprehend PII detection to identify sensitive fields, apply anonymization and data masking before forwarding the sanitized text to Bedrock, and configure Bedrock guardrails to prevent the model from generating or inferring sensitive information.

B) Use a Lambda function to remove customer names only, send partially redacted content to Bedrock, and rely on CloudWatch retention policies to ensure privacy.

C) Encrypt all requests with KMS before sending them to Bedrock, rely on the FM's internal behavior to avoid exposing PII, and mask financial data only in downstream reporting dashboards.

D) Store all FM inputs in an S3 bucket with server-side encryption, send raw data directly to Bedrock, and use IAM policies to restrict who can view inference logs.

---

**Q43.** A healthcare analytics company is building an internal generative AI assistant to help data analysts summarize clinical trial reports, extract structured findings, and generate risk assessments for research teams. The AI engineering team wants to test several Amazon Bedrock models to identify which FM provides the best accuracy when handling long biomedical texts, the lowest hallucination rate, and the strongest performance on domain-specific terminology. They must select a model that aligns with strict compliance requirements and produces reliably factual outputs.

The lead AI engineer must determine the BEST approach to select the most appropriate foundation model before finalizing the architecture.

Which approach should the engineer take?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Run performance benchmarks across multiple Amazon Bedrock foundation models by evaluating accuracy, latency, hallucination rate, and domain-specific capability to determine which model best meets the business and technical requirements.

B) Select a biomedical third-party API outside AWS to bypass internal benchmarking efforts and rely on vendor marketing claims for expected performance.

C) Select the smallest, fastest foundation model from Amazon Bedrock to reduce inference cost and maximize system responsiveness, regardless of domain performance characteristics.

D) Choose a single general-purpose model based on initial impressions and avoid extensive testing to reduce development time during the prototype phase.

---

**Q44.** A healthcare startup is building a patient-support chatbot powered by an Amazon Bedrock foundation model. The chatbot processes medical inquiries that may include sensitive personal and demographic information. To comply with internal privacy controls and regional data-protection laws, the engineering team must ensure that PII is identified before any interaction reaches the FM, that FM responses do not leak sensitive content, and that all temporary text artifacts stored in Amazon S3 are automatically deleted according to a 24-hour retention requirement.

Which approach BEST satisfies the organization's privacy-preserving requirements?

**Domain:** 3 – AI Safety, Security, and Governance

A) Store all interaction logs indefinitely in an S3 Glacier Deep Archive vault, use no guardrails, and rely exclusively on SageMaker AI's built-in model isolation for privacy control.

B) Use API Gateway request validation to block long messages, send all content directly to Bedrock without pre-processing, and rely on CloudTrail logs to monitor sensitive data access.

C) Encrypt all uploaded content using default S3 encryption, rely on the FM to ignore PII if present, and delete S3 objects manually through scheduled Lambda clean-ups.

D) Use Amazon Comprehend and Amazon Macie to detect PII before forwarding inputs to Bedrock, enable Bedrock guardrails to prevent PII exposure in FM outputs, and configure S3 Lifecycle rules to automatically delete transient data after 24 hours.

---

**Q45.** A global HR software provider is developing a GenAI assistant on Amazon Bedrock to help users draft employee performance summaries. The company must ensure strict safety controls because the assistant occasionally receives sensitive user-uploaded notes containing personal data, emotionally charged language, or prohibited content. The security team wants a defense-in-depth approach that screens inputs before they reach the FM, enforces model-level restrictions, and validates outgoing responses before they are returned to clients over their public API.

Which solution BEST provides comprehensive, layered protection against FM misuse?

**Domain:** 3 – AI Safety, Security, and Governance

A) Use Step Functions to retry prompts automatically if the initial model response contains restricted content.

B) Store all incoming requests in DynamoDB and allow the FM to decide when to reject harmful content.

C) Use Amazon Comprehend for pre-processing classification and entity detection, enforce Amazon Bedrock guardrails during model invocation, and use Lambda behind API Gateway to perform post-processing validation and filtering.

D) Configure the Bedrock model with a low temperature setting to reduce risky generations and enforce API throttling at API Gateway.

---

**Q46.** A logistics automation company is building an FM-driven operations assistant using Amazon Bedrock. The assistant uses the Strands API to trigger route optimization tools, inventory lookup functions, and shipment-delay diagnostics. During testing, engineers observe that the FM sometimes produces malformed function parameter values (such as negative quantities or improperly formatted timestamps), causing downstream tool failures. The AI engineer must design a solution that ensures safe execution of tool calls, validates all parameters before invoking external systems, and provides corrective feedback to the FM when invalid inputs are detected.

Which solution BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Use Amazon EventBridge Pipes to forward all FM tool calls directly to downstream services without parameter checks to reduce latency.

B) Store the FM output in Amazon S3 and run periodic AWS Glue jobs to clean malformed parameters before tool execution.

C) Use AWS Lambda functions to validate and sanitize all FM-generated tool parameters, implement structured error handling, and return corrective messages to the FM when inputs are invalid.

D) Configure the FM to retry failed tool calls automatically, assuming that repeated attempts will eventually produce valid parameters.

---

**Q47.** A machine learning team at a financial analytics firm is building a GenAI assistant that retrieves regulatory guidance, compliance summaries, and historical interpretations from a large vector store. Users often submit vague or incomplete queries such as "rules for foreign transfers", which return inconsistent results across departments. The team needs a retrieval workflow that can automatically expand ambiguous queries, break them into structured components, and transform them into domain-aligned search intents before performing vector search.

Which retrieval enhancement approach should the team implement to meet these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Use Amazon Aurora with pgvector and rely on a larger embedding chunk overlap to compensate for vague user queries.

B) Use Step Functions to run multiple sequential keyword searches against Amazon S3 and merge the results before embedding generation.

C) Use Amazon Bedrock to perform query expansion and generate domain-specific reformulations, then use a Lambda function to decompose the expanded query into sub-queries before passing them to the vector search engine.

D) Use OpenSearch with a larger vector dimensionality and lower similarity threshold to increase recall for ambiguous queries.

---

**Q48.** A social media analytics company deployed a customized transformer model to an Amazon SageMaker AI endpoint using DJL Serving. The endpoint runs on GPU instances with 8 GPUs each. As usage increases, the AI engineer notices high costs because the endpoint scales out frequently, even though GPU utilization per instance remains low.

Log analysis shows that the model was configured for a maximum sequence length far larger than what real production queries require. Profiling also reveals that the model's weights and activation memory fit within 4 GPUs, but DJL is currently configured to spread the model across all 8 GPUs. The engineering team wants to improve utilization and reduce cost without refactoring the model.

Which combination of steps will improve resource efficiency with minimal operational overhead? (Select TWO.)

**Domain:** 4 – Operational Efficiency and Optimization for GenAI Applications

A) Use a tensor parallelism degree of 4, allowing two full model replicas per instance and increasing concurrency.

B) Increase the number of SageMaker AI instances while lowering the batch size to reduce contention across GPUs.

C) Reduce the model's maximum sequence length so that DJL can allocate more memory to larger rolling batch sizes and increase throughput.

D) Split the model evenly across all 8 GPUs to guarantee that GPU memory is fully utilized by a single replica.

E) Enable speculative decoding to accelerate token generation across all GPUs and reduce per-request latency.

---

**Q49.** A financial analytics company is building an FM-powered research assistant using Amazon Bedrock. The assistant needs access to several tools via MCP, including a lightweight exchange-rate lookup tool and a more complex market-sentiment analysis service. The engineering team wants to ensure that the FM can call simple tools with minimal latency while reserving more scalable compute resources for tools that require heavy data processing or model execution. They also need a consistent access pattern so all tools are discoverable and invoked in a standardized way by the FM.

Which architecture BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Store all tool definitions in Amazon S3 and let the FM retrieve and execute tool logic directly from the stored files without MCP-level orchestration.

B) Host all MCP servers on Amazon ECS to standardize compute environments and avoid the operational overhead of managing two tool-hosting mechanisms.

C) Deploy all MCP servers on Lambda regardless of complexity, using environment variables to simulate persistent state and reduce deployment overhead.

D) Use AWS Lambda functions to implement stateless MCP servers for lightweight tools and Amazon ECS to host MCP servers that handle complex or compute-intensive tools, while relying on MCP client libraries to maintain consistent access patterns.

---

**Q50.** A financial analytics company is building an FM-powered system that generates multi-step investment risk assessments. Some model queries can escalate into long reasoning chains, repeatedly calling external risk-analysis tools. The engineering team must ensure that the FM behaves safely by enforcing strict stopping conditions, preventing runaway loops, and ensuring the workflow halts immediately if any tool call fails or exceeds its expected latency.

Which approach will BEST ensure controlled and safeguarded FM behavior?

**Domain:** 2 – Implementation and Integration

A) Use CloudWatch Logs alone to detect abnormal FM behavior and manually terminate workflows if excessive tool calls are identified.

B) Use AWS Step Functions to implement explicit stopping conditions, failure branches, and maximum iteration limits, with Lambda functions enforcing timeouts and circuit breakers for external tool calls.

C) Use a large, instruction-heavy Bedrock prompt that instructs the FM to stop after a certain number of reasoning steps and avoid unnecessary tool calls.

D) Use Amazon SQS with dead-letter queues to hold messages when FM tool calls fail, allowing engineers to investigate failures later.

---

**Q51.** An ecommerce company operates a generative AI service that uses Amazon Bedrock to produce product descriptions and personalized recommendations. The application currently runs in a single AWS Region. During high-traffic periods such as seasonal sales, requests to the foundation model begin failing with the message "Too many requests, please wait before trying again."

The company must increase throughput during peak periods without adding operational overhead. The solution must remain compatible with the current Amazon Bedrock API and must continue using the same foundation model.

Which solution will meet these requirements in the MOST cost-effective way?

**Domain:** 4 – Operational Efficiency and Optimization for GenAI Applications

A) Purchase provisioned throughput for the foundation model in the primary Region to guarantee higher request capacity.

B) Use prompt routing to distribute traffic across multiple foundation models within the same family to increase capacity.

C) Create an AWS Lambda wrapper function that attempts inference in the primary Region and falls back to a secondary Region upon throttling errors.

D) Use cross-Region inference to distribute model invocations across multiple AWS Regions while still using the same foundation model and API structure.

---

**Q52.** A biotechnology startup is building an FM-powered research assistant that analyzes complex lab reports. The system uses three specialized models deployed through Amazon Bedrock: one FM optimized for summarizing experimental results, another FM tuned for extracting chemical relationships, and a third FM trained for identifying statistical anomalies. The solution architect needs a coordination layer that can dynamically select the best model based on query intent and aggregate outputs using custom logic before returning a unified response to researchers.

Which approach will BEST support this multi-capability coordination?

**Domain:** 2 – Implementation and Integration

A) Build a model selection and aggregation framework that routes requests to specialized FMs and merges outputs using custom logic, enabling optimized performance across multiple capabilities.

B) Create separate API endpoints for each FM and instruct researchers to manually choose which endpoint to use for each type of analysis.

C) Increase the context window of a single general-purpose FM so that all tasks are handled by one model without requiring routing logic or aggregation.

D) Use AWS Lambda to randomly distribute requests among the three FMs to balance load and avoid overloading any single model.

---

**Q53.** A media analytics startup is developing a real-time script-evaluation assistant that must display generated text to users as soon as the FM begins producing tokens. The engineering team wants to minimize perceived latency, support incremental output delivery to browser clients, and avoid long-running synchronous requests. They also require a standards-based mechanism for maintaining persistent bidirectional connections.

Which solution BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Use an ALB in front of a containerized Bedrock proxy service that waits for full responses before returning them to users.

B) Use Amazon SQS long polling to retrieve incremental FM output and push updates to the UI.

C) Use a Lambda function that polls Bedrock until the full response is ready, then returns the complete text to the browser.

D) Use Amazon Bedrock streaming APIs and deliver partial tokens to clients through a WebSocket-based API Gateway endpoint.

---

**Q54.** A financial services company is developing an FM-powered document analysis assistant on Amazon Bedrock to help analysts review complex loan applications. The system generates risk summaries, extracts financial ratios, and identifies anomalies. Compliance officers require a multi-stage human review process when the FM output includes uncertainty markers or high-risk flags. The AI engineer must design a workflow that automatically routes these cases for human validation and also collects structured feedback that will later be used to refine prompt strategies.

Which solution BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Use AWS Step Functions to orchestrate conditional human-review steps, and integrate Amazon API Gateway to collect structured reviewer feedback for future refinement.

B) Implement an Amazon SQS queue that sends every FM output to a batch process for manual approval, regardless of whether uncertainty markers are detected.

C) Deploy the FM behind an Amazon CloudFront distribution and instruct analysts to manually review outputs through a web form before approval.

D) Configure Amazon EventBridge to forward all FM responses to a Slack channel so that reviewers can leave comments that the system parses asynchronously.

---

**Q55.** A retail analytics company wants to evaluate whether generative AI can improve internal reporting workflows by automatically generating weekly sales summaries, identifying anomalies, and drafting executive insights. Before committing to a full production deployment, the lead AI engineer is asked to validate feasibility, model performance, and expected ROI. The engineer needs to quickly test multiple Amazon Bedrock foundation models, compare latency and output quality, and gather stakeholder feedback with minimal engineering overhead.

Which approach is the MOST appropriate for conducting this proof-of-concept (POC) phase?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Use a single chosen foundation model and skip comparative testing to reduce initial development effort and accelerate the move to full-scale deployment.

B) Develop a custom container-based inference server on Amazon EC2 to manually manage model selection, caching, and benchmarking across different Bedrock models.

C) Immediately deploy a fully scalable multi-Region architecture using Amazon ECS, provisioned throughput for Bedrock, and an automated CI/CD pipeline to simulate production traffic patterns.

D) Build a small-scale proof-of-concept using Amazon Bedrock by testing multiple foundation models behind a simple API Gateway and Lambda architecture to evaluate performance, latency, and output quality before investing in a production deployment.

---

**Q56.** A global media company is developing multiple generative AI applications, including automated captioning, editorial assistance, and conversational search. Several teams are building their own Amazon Bedrock-based prototypes using API Gateway and Lambda, but leadership is concerned that each team is implementing different security controls, logging approaches, and model invocation patterns.

The principal AI architect must ensure all teams follow consistent, repeatable architecture patterns and adopt validated best practices across environments.

Which approach BEST meets these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Require teams to store all model invocation code in a shared Git repository to encourage consistent implementation patterns.

B) Develop reusable architecture blueprints and service templates using the AWS Well-Architected Framework and the AWS WA Tool Generative AI Lens to enforce standardized best practices across all GenAI projects.

C) Allow teams to continue building independently but require monthly architectural review meetings to surface inconsistencies and recommend improvements.

D) Build a single centralized generative AI platform that all teams must integrate with, regardless of workload differences.

---

**Q57.** A healthcare analytics company is developing a generative AI system on Amazon Bedrock to help clinicians interpret patient risk summaries. During initial testing, the governance team discovers variation in outputs when patient profiles from different demographic groups are analyzed, raising concerns about fairness and potential bias. The organization needs a systematic, low-code approach to measure fairness metrics over time, compare model behavior across controlled test groups, and automatically score responses for equity violations. The solution should avoid building custom evaluation pipelines and must run evaluations at scale with minimal engineering effort.

Which approach BEST satisfies these requirements?

**Domain:** 3 – AI Safety, Security, and Governance

A) Use a custom container in Amazon ECS that runs Python-based fairness scripts and pushes evaluation metrics to Amazon QuickSight dashboards.

B) Use Amazon SageMaker Clarify to run bias detection on all FM outputs and require manual labeling by analysts before each model release.

C) Use Amazon Bedrock Prompt Flows to run controlled A/B tests on demographic test sets, publish fairness metrics to Amazon CloudWatch for ongoing monitoring, and evaluate responses using an LLM-as-a-judge pattern in Amazon Bedrock to automatically score potential bias.

D) Use Amazon Athena queries against S3 logs to manually compare responses from different demographic groups and export CSV reports for fairness audits.

---

**Q58.** A logistics automation company is building a GenAI routing assistant on Amazon Bedrock. The assistant must handle three categories of queries: simple shipment lookups, medium-complexity route validation, and complex multi-stop optimization questions. The company notices that all queries are currently routed to a high-end FM, causing unnecessary inference costs for common low-complexity requests.

A GenAI developer is tasked with implementing a framework that reduces FM cost while keeping answer quality high for complex queries. The solution must require minimal ongoing maintenance and no custom fine-tuning.

Which combination of steps will meet these requirements MOST effectively? (Select TWO.)

**Domain:** 4 – Operational Efficiency and Optimization for GenAI Applications

A) Use a single large FM for all requests but enable response streaming to reduce billing costs based on output tokens.

B) Enable speculative decoding on the large FM to reduce compute time for the most complex requests.

C) Implement a lightweight classifier model to categorize incoming queries as simple, medium, or complex, and route each category to a corresponding FM tier with different price-to-performance levels.

D) Route all queries to a high-context-window FM to reduce the chance of missing relevant details.

E) Create a two-tier FM pipeline where simple lookups use a small FM and complex optimization queries use a larger FM. Use Bedrock Prompt Management to store routing templates and metadata.

---

**Q59.** A biotech research company is deploying a large 70-billion-parameter language model on Amazon SageMaker AI to summarize genomic experiment logs and generate structured reports. During testing, the team observes extremely slow cold-start times, GPU memory exhaustion, and uneven throughput under variable token workloads. The engineering lead wants a deployment strategy that ensures optimal GPU utilization, predictable token processing performance, and minimal startup delays while maintaining container flexibility for future model upgrades.

Which deployment strategy BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Use a container-based deployment pattern optimized for LLMs with tensor parallelism, lazy weight loading, and GPU-aware model partitioning to maximize memory efficiency and token throughput.

B) Use Lambda-based invocation with increased memory allocation to accelerate model loading and reduce cold-start latency.

C) Use a traditional ML container that loads the entire model into CPU memory first, then transfers it to the available GPUs during inference initialization.

D) Use multiple smaller SageMaker endpoints behind an Application Load Balancer to distribute requests and avoid GPU memory pressure.

---

**Q60.** A multinational retail company is building a generative AI platform on AWS to support product analytics, code generation for microservices, and automated test creation across multiple engineering teams. Leadership wants to standardize development workflows, enforce consistent integration patterns, and accelerate experimentation while maintaining high application quality. The company decides to adopt Amazon Q Developer to streamline coding tasks, automate troubleshooting, and improve test coverage for GenAI features.

The engineering organization must select the combination of steps that will maximize developer productivity and automate performance tuning with the least operational overhead.

Which combination of steps will meet these requirements? (Select TWO.)

**Domain:** 4 – Operational Efficiency and Optimization for GenAI Applications

A) Use Amazon Q Developer to create custom vector store indexing logic for all microservices and deploy the logic with a centralized CI/CD pipeline.

B) Configure Amazon Q Developer to manage schema migrations for all service databases and auto-deploy them with AWS CodeDeploy.

C) Use Amazon Q Developer to automatically generate test cases, identify code defects, and propose optimizations directly within developer IDEs.

D) Deploy Amazon Q Developer as a standalone inference endpoint on Amazon EC2 to run nightly batch validations against all GenAI components.

E) Use Amazon Q Developer to perform workload-aware refactoring, accelerate application troubleshooting, and auto-suggest integration patterns aligned with company standards.

---

**Q61.** A global hospitality company is building an FM-powered itinerary generator that serves both a public-facing website and an internal concierge dashboard. The concierge dashboard must support consistently low-latency responses during peak travel seasons, while the public website experiences unpredictable traffic spikes. The engineering team wants to optimize cost efficiency while ensuring high performance for the internal tool. They also need a fallback option for batch itinerary generation jobs that require longer processing times.

Which deployment strategy BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Use Amazon Bedrock serverless mode for the concierge dashboard and the public website, while using Lambda functions to run batch jobs that invoke the model through the Bedrock API.

B) Use Amazon Bedrock provisioned throughput for the concierge dashboard, Lambda-based on-demand model invocation for the public website, and a SageMaker AI endpoint for scheduled batch itinerary generation.

C) Deploy all inference through Lambda so both the dashboard and website automatically scale during traffic bursts, and use Lambda reserved concurrency to guarantee low-latency performance for the concierge tool.

D) Use a single SageMaker AI endpoint for all traffic and scale it with automatic instance warm pools to handle seasonal spikes and batch workloads.

---

**Q62.** A healthcare analytics company is building a GenAI assistant with Amazon Bedrock to help clinicians summarize case notes and provide care recommendations. The engineering team notices that inference costs are rising rapidly because user conversations include long historical threads. Many requests send unnecessary document context and produce overly long responses. The company wants to reduce FM token consumption without reducing the quality of the assistant's recommendations.

Which combination of steps will MOST effectively reduce token usage with MINIMAL operational overhead? (Select TWO.)

**Domain:** 4 – Operational Efficiency and Optimization for GenAI Applications

A) Apply response size controls by setting a maximum generation token limit in the inference configuration.

B) Enable speculative decoding to reduce end-to-end latency for each request.

C) Implement context pruning to remove irrelevant conversation turns before sending the prompt.

D) Use a larger context-window FM so that longer inputs can be processed at once without manual prompt trimming.

E) Store full conversation history in Amazon S3 and send the entire past thread to the model for every request to preserve accuracy.

---

**Q63.** A global insurance provider is building an internal Amazon Bedrock–powered assistant for underwriting, claims, and customer operations. Each business division maintains its own prompt templates and requires a formal approval workflow before templates can be used in production. The company also must retain full invocation records—including prompts, parameters, and FM outputs—for at least 7 years to satisfy auditing and regulatory inquiries.

The AI engineering team wants a solution that provides built-in governance and long-term, tamper-proof logging without developing custom workflow engines, storage systems, or archival processes.

Which combination of steps will meet these requirements with MINIMAL operational overhead? (Select TWO.)

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Enable Amazon Bedrock model invocation logging to Amazon S3, and apply S3 Object Lock in compliance mode with a 7-year retention period.

B) Configure AWS CloudTrail Lake to store all Bedrock events, including prompt bodies and FM responses, with custom retention settings.

C) Use Amazon Bedrock Prompt Management with approval workflows and role-based access control to centrally manage, version, and approve prompt templates across divisions.

D) Send Bedrock invocation events to Amazon EventBridge and archive them in Amazon Redshift tables configured with 7-year retention policies.

E) Store prompt templates in AWS Secrets Manager with resource policies that require MFA for approvals and updates.

---

**Q64.** A global logistics company is building a real-time generative AI assistant that relies on a vector database to retrieve shipment procedures, customs compliance rules, and regional operations updates across 40+ countries. These documents are stored in multiple internal systems and regularly updated throughout the day.

The AI engineering team must ensure that the organization's Amazon Bedrock-powered RAG pipeline always uses fresh, accurate embeddings. They need a solution that can detect document changes, re-chunk and re-embed only modified content, and automatically refresh the vector store without reprocessing the entire dataset. The solution must scale to thousands of document changes per hour.

Which approach BEST meets these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Trigger manual refresh workflows that require engineers to upload updated content to S3 whenever document editors finish revisions in internal systems.

B) Run a nightly batch job using Amazon SageMaker Processing to rebuild the vector index from scratch and replace the existing embeddings each morning.

C) Use event-driven AWS Lambda functions triggered by document change notifications to reprocess only updated files, generate new embeddings, and synchronize them with the vector store through a Bedrock Knowledge Base ingestion S3 bucket.

D) Schedule a full vector store rebuild every hour using AWS Glue crawlers to scan all documents and regenerate embeddings for the entire dataset regardless of whether content changed.

---

**Q65.** A global logistics company is building an AI assistant on Amazon Bedrock to help internal teams analyze shipment exceptions. The system receives thousands of near-duplicate queries each day, such as slight variations of "summarize the delay reason for package 12345." A GenAI engineer needs to reduce FM invocation costs and improve response latency without modifying the underlying foundation model or deploying additional inference infrastructure. The solution must avoid recomputing responses for semantically identical requests.

Which solution will MOST effectively meet these requirements with the least operational overhead?

**Domain:** 4 – Operational Efficiency and Optimization for GenAI Applications

A) Create a Lambda function that rewrites prompts into a canonical form before sending them to the model, then cache based on the canonicalized string.

B) Use Amazon CloudFront to cache model responses at the edge to reduce round trips to the Bedrock endpoint.

C) Cache the raw prompt strings in an in-memory store and return cached responses only when an exact string match occurs.

D) Implement a semantic caching layer by generating vector embeddings for incoming queries, performing similarity search with an approximate nearest neighbor index, and returning cached results when similarity exceeds a defined threshold.

---

**Q66.** A financial analytics company is building a GenAI-powered summarization service that processes thousands of large PDF reports per hour. Some workloads require synchronous responses from Amazon Bedrock, while others must be processed asynchronously due to long document sizes and unpredictable latency. The solution must support both real-time API clients and background batch processing, enforce request validation, and provide reliable message handling.

Which architecture BEST meets these requirements?

**Domain:** 2 – Implementation and Integration

A) Use API Gateway for request validation and synchronous Bedrock invocations, and use Amazon SQS with Lambda workers to process asynchronous requests that call Bedrock in the background.

B) Use Amazon EventBridge to route all traffic to a monolithic container running on Amazon ECS that synchronously invokes Bedrock for every request.

C) Use a single AWS Lambda function to directly invoke Amazon Bedrock for all workloads and store the results in Amazon S3.

D) Use an Amazon EC2 instance to poll PDF files from S3 and directly call Amazon Bedrock through the AWS CLI.

---

**Q67.** A logistics software company uses an Amazon Bedrock FM to generate route summaries and exception reports for its dispatch system. After adding new prompt templates and switching to a newer model version, the team notices inconsistent quality across deployments. Leadership asks for a systematic quality assurance process that can automatically detect regressions, evaluate output consistency, and prevent low-quality model configurations from being promoted to production. The solution must use managed AWS services, require minimal custom infrastructure, and provide automated quality gating before deployments.

Which solution will BEST meet these requirements?

**Domain:** 5 – Testing, Validation, and Troubleshooting

A) Use CloudWatch Logs to track FM invocations, create a Lambda function that checks for unusual response lengths, and trigger SNS alerts when anomalies occur before deployment.

B) Export FM outputs to Amazon S3 and use an AWS Glue job to compute heuristic quality scores, then have the engineering manager manually review a QuickSight dashboard before approving releases.

C) Implement a continuous evaluation workflow using Amazon Bedrock Model Evaluations to test the FM against a golden dataset on every deployment, integrate regression thresholds into the CI/CD pipeline, and enforce automated quality gates that block releases when accuracy, consistency, or fluency metrics fall below predefined baselines.

D) Run manual spot-checks on generated summaries each week, compare outputs with historical examples, and approve deployments only after the product team reviews a small sample set.

---

**Q68.** A financial services company is integrating Amazon Bedrock into its existing loan-processing platform to generate automated explanations for loan approval decisions. The platform relies on an internal identity provider (IdP) that manages user permissions for analysts, auditors, and risk officers. The security team requires a framework that ensures:

- centralized authentication through the enterprise IdP,
- least-privilege access to Bedrock model APIs,
- role-based controls so that only a small group of analysts can invoke the FM, and
- no long-lived credentials stored in the application environment.

Which solution BEST satisfies these requirements?

**Domain:** 2 – Implementation and Integration

A) Use API Gateway API keys to control who can invoke the Bedrock model, mapping each analyst's identity to a unique API key.

B) Configure each analyst with separate IAM user accounts and attach Bedrock invocation policies directly to their user credentials.

C) Allow the application to store AWS access keys for analysts in an encrypted configuration store and validate their permissions on each request.

D) Use IAM Identity Center with SAML federation to the company's IdP and assign fine-grained, least-privilege IAM roles that permit Bedrock model invocation only for authorized analyst groups.

---

**Q69.** A media research company is building a generative AI assistant that retrieves insights from thousands of articles, interviews, video transcripts, and industry reports. Users often request information filtered by publication date, content category, author credibility, and source type (e.g., transcript vs. article). However, retrieval results are inconsistent because embeddings alone do not capture contextual attributes such as authorship, timestamps, or domain classification.

To increase search precision and improve FM-augmented responses, the AI engineering team must implement a metadata framework that enriches embeddings with structured contextual information for filtering, ranking, and relevance scoring.

Which approach BEST meets these requirements?

**Domain:** 1 – Foundation Model Integration, Data Management, and Compliance

A) Use DynamoDB to store only document titles and perform string-matching searches before sending results to the FM.

B) Add metadata fields directly into the embedding vectors by appending text descriptions of authorship and timestamps before embedding.

C) Use S3 object metadata to store timestamps and document types, apply custom metadata attributes for authorship and domain tags, and make these fields available for metadata filtering in the vector database during semantic retrieval.

D) Store all documents in Amazon S3 without metadata and rely solely on embedding similarity to determine which documents are relevant.

---

**Q70.** A health analytics company deploys a large foundation model on Amazon Bedrock to summarize clinical documents. As usage increases, the GenAI platform team notices throughput bottlenecks: model invocations queue during peak hours, and token processing speed varies widely based on request patterns. The team must improve throughput without increasing model size or changing the FM.

Which combination of steps will MOST effectively improve throughput for this workload? (Select TWO.)

**Domain:** 4 – Operational Efficiency and Optimization for GenAI Applications

A) Use concurrent model invocation management by increasing the maximum parallel invocations per endpoint and tuning retry behavior for bursts.

B) Replace the summarization model with a smaller FM even if accuracy decreases, to reduce token generation time.

C) Enable batch inference for highly similar summarization requests and configure dynamic batch sizing based on real-time queue depth.

D) Capture all Bedrock invocation events with EventBridge and run scheduled jobs to manually throttle or unthrottle request traffic.

E) Reduce all prompt lengths by 50% regardless of content by truncating input documents to the first portion of each text.

---

## ANSWERS

| Q | Answer | | Q | Answer | | Q | Answer | | Q | Answer |
|---|--------|-|---|--------|-|---|--------|-|---|--------|
| 1 | B | | 19 | C | | 37 | A | | 55 | D |
| 2 | C | | 20 | A | | 38 | A, C | | 56 | B |
| 3 | B | | 21 | C | | 39 | B | | 57 | C |
| 4 | A | | 22 | A, C | | 40 | D | | 58 | C, E |
| 5 | C | | 23 | C | | 41 | A | | 59 | A |
| 6 | C | | 24 | D | | 42 | A | | 60 | C, E |
| 7 | A, C | | 25 | B | | 43 | A | | 61 | B |
| 8 | B | | 26 | D | | 44 | D | | 62 | A, C |
| 9 | D | | 27 | C | | 45 | C | | 63 | A, C |
| 10 | B | | 28 | C* | | 46 | C | | 64 | C |
| 11 | D | | 29 | D | | 47 | C | | 65 | D |
| 12 | C | | 30 | A | | 48 | A, C | | 66 | A |
| 13 | C | | 31 | C | | 49 | D | | 67 | C |
| 14 | C, D | | 32 | A | | 50 | B | | 68 | D |
| 15 | B | | 33 | B | | 51 | D | | 69 | C |
| 16 | A, C | | 34 | A, C | | 52 | A | | 70 | A, C |
| 17 | A | | 35 | C | | 53 | D | | | |
| 18 | D | | 36 | C | | 54 | A | | | |

### Notes

- **Q28 (\*)** — The source exam keys **C**, but its explanation blocks are misaligned: the "Correct" rationale describes enforcing only `bedrock:GuardrailIdentifier` (option A), and a separate rationale explicitly rejects `bedrock:PromptRouterArn` as "not guardrails... provides no benefit for guardrail compliance." Technically, **A** is the defensible answer — `PromptRouterArn` gates prompt-router access, not guardrail enforcement.

### Domain distribution

| Domain | Questions | Count |
|---|---|---|
| 1 – Foundation Model Integration, Data Management, and Compliance | 1, 3, 10, 14, 16, 18, 21, 23, 24, 25, 27, 36, 39, 40, 43, 47, 55, 56, 63, 64, 69 | 21 |
| 2 – Implementation and Integration | 2, 9, 12, 15, 32, 33, 37, 38, 46, 49, 50, 52, 53, 54, 59, 61, 66, 68 | 18 |
| 3 – AI Safety, Security, and Governance | 4, 5, 7, 11, 13, 17, 20, 28, 29, 35, 42, 44, 45, 57 | 14 |
| 4 – Operational Efficiency and Optimization for GenAI Applications | 30, 31, 48, 51, 58, 60, 62, 65, 70 | 9 |
| 5 – Testing, Validation, and Troubleshooting | 6, 8, 19, 22, 26, 34, 41, 67 | 8 |
