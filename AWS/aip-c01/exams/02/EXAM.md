# Exam 2

> AWS Certified Generative AI Developer – Professional | 70 questions across 5 domains
> Source: ExamPro Practice Exam 2 (questions captured before attempting; not yet graded)

## QUESTIONS

**Q1.** A global travel booking company uses Amazon Bedrock foundation models to generate itinerary summaries, hotel recommendations, and customer explanations. The engineering team is preparing to roll out a new FM version to production. Leadership requires strict deployment validation to ensure that the update does not increase hallucination rates, degrade semantic consistency, or introduce drift in how the model structures its recommendations. The validation process must run automatically before deployment, simulate real user behavior, detect output inconsistencies, and block the rollout if FM responses deviate from baseline quality metrics.

Which solution will BEST meet these requirements?

A) Enable CloudWatch anomaly detection on token usage for the new FM version and set up alerts that notify the engineering team if usage patterns diverge from historical trends.

B) Enable automated deployment validation using synthetic user workflows that run against the new FM version, evaluate hallucination and consistency metrics through an AI-specific output validation pipeline, and enforce quality gates that block rollout upon detecting semantic drift.

C) Generate human review tasks through SageMaker Ground Truth after each deployment and require a review team to approve outputs before production rollout continues.

D) Perform manual A/B testing with a subset of developers who compare model outputs in a shared spreadsheet and vote on whether the new FM version should be deployed.

---

**Q2.** A global insurance company is building a GenAI workflow on Amazon Bedrock to automate claim analysis. The workflow uses retrieval augmentation with Amazon OpenSearch Serverless and invokes an FM for summarization. During testing, the GenAI engineering team notices that latency varies significantly across requests. Profiling reveals two consistent patterns:

- Many requests use long prompts that include redundant historical context.
- Vector search queries return large result sets, slowing down the augmentation step before model invocation.

The team wants to optimize the system to reduce overall latency while maintaining consistent summarization quality. The solution must preserve accuracy, minimize reengineering, and require the least operational overhead.

Which solution BEST meets these requirements?

A) Replace the OpenSearch vector index with a high-dimensional dense index and increase the search window size to guarantee more complete retrieval.

B) Cache all retrieved documents in Amazon DynamoDB so the system always bypasses vector search, eliminating retrieval latency for most queries.

C) Increase the FM’s maximum output token limit and raise the model’s temperature to produce shorter answers that compensate for latency delays.

D) Use API call profiling to prune redundant prompt segments and optimize OpenSearch Serverless vector queries with filtered top-k scoring. This reduces both prompt token processing time and retrieval latency without changing the FM.

---

**Q3.** A robotics startup is training a high-resolution object-tracking model using Amazon SageMaker AI. The training data consists of millions of annotated frames stored in Amazon S3, generated from a labeling workflow built with SageMaker Ground Truth. Engineers notice that GPU utilization remains low because the training container must download large batches of images sequentially from S3 at startup, causing long warm-up times and slow epoch transitions.

The team wants to keep S3 as the system of record but improve throughput and reduce startup delays—without duplicating data, restructuring the dataset, or rewriting the training code. The solution must support high-performance parallel reads and integrate seamlessly with the current S3-based workflow.

Which solution will best improve training performance while meeting all requirements?

A) Create an Amazon FSx for Lustre file system linked to the existing S3 bucket and mount it into the SageMaker training job so the model can read data at high throughput with POSIX semantics.

B) Move the training data to an Amazon EFS file system and mount it to the container for improved sequential read performance.

C) Copy the training dataset to Amazon EBS volumes before every SageMaker run to reduce remote fetch overhead during training.

D) Enable S3 Transfer Acceleration to reduce latency when fetching data during training initialization.

---

**Q4.** A healthcare analytics company builds an internal GenAI assistant on Amazon Bedrock to automate interpretation of medical summaries. After deployment, clinicians report inconsistent response times and occasional drops in output quality. The CTO requests a complete observability approach that provides visibility into FM invocation performance, tracing across retrieval and orchestration steps, and business-level metrics such as clinician time saved per task. The solution must use managed AWS services, avoid building a separate monitoring system, and present insights in a unified view with minimal custom integration work.

Which solution will BEST meet these requirements?

A) Build a custom monitoring layer by exporting FM invocation logs to DynamoDB, visualizing latency, prompt-processing patterns, and business KPIs with Amazon QuickSight, and embedding additional performance panels directly into the internal clinician portal.

B) Stream all FM requests and responses into Amazon Kinesis Data Streams, use Athena to analyze latency distribution and retrieval depth, and create a custom web-based observability console to display trends, workflow traces, and clinical impact scoring.

C) Enable Amazon Bedrock invocation logging, integrate AWS X-Ray tracing across the retrieval and orchestration workflow, publish business-impact metrics to Amazon CloudWatch, and use CloudWatch dashboards to unify operational telemetry and FM interaction details in a single managed interface.

D) Use CloudTrail to capture FM invocation activity, store the event logs in Amazon S3 for periodic analysis, and configure a Lambda-based reporting process that generates operational summaries and clinician impact reports on a scheduled basis.

---

**Q5.** A healthcare analytics startup is developing a clinical triage assistant that uses Amazon Bedrock. The assistant applies multiple guardrail layers, including medical-advice blocking, PHI filtering, and prompt-injection detection. During testing, the development team notices that some benign clinical questions are blocked, and they need detailed diagnostics showing exactly which guardrail policy category caused the intervention.

The team wants to inspect guardrail activity for each invocation, differentiate which guardrail type intervened, and identify whether the issue relates to content safety, PHI detection, or topic restrictions. They want the most granular, real-time operational insight for tuning guardrail configurations.

Which configuration will provide the MOST detailed visibility into guardrail decision-making?

A) Configure guardrail tracing with {"trace": "enabled"} in guardrailConfig. Monitor Amazon CloudWatch InvocationsIntervened metrics using the GuardrailPolicyType dimensions (ContentPolicy, TopicPolicy, SensitiveInformationPolicy) to identify the specific intervention category.

B) Enable Amazon Bedrock model invocation logging and configure CloudWatch Logs Insights to query logs based on GuardrailContentSource dimensions for input vs output blocking.

C) Enable Amazon Bedrock model evaluation with automatic adversarial test sets. Review the evaluation scorecards for guardrail robustness and compare which rules blocked test prompts.

D) Configure guardrail tracing with {"trace": "enabled"} and use the GuardrailContentSource dimension to determine whether the request input or model output triggered the intervention.

---

**Q6.** A healthcare analytics company is developing a GenAI-based summarization service that uses Amazon Bedrock to generate HIPAA-compliant clinical summaries. After deployment, developers notice intermittent latency spikes and inconsistent model responses. The engineering team needs to identify whether the delays are caused by upstream validation logic, network retries in the AWS SDK, or Bedrock model invocation itself. They also need observability into prompt/response characteristics to detect possible malformed inputs.

Which approach BEST improves troubleshooting efficiency for this FM application?

A) Enable AWS X-Ray tracing for the application and analyze invocation traces, then use CloudWatch Logs Insights to query prompt/response logs for pattern anomalies.

B) Configure a CloudTrail trail to record all Bedrock API calls and search for latency anomalies in the event history.

C) Increase the Lambda function timeout and analyze the function duration metrics in CloudWatch Metrics.

D) Store every prompt and response in DynamoDB and periodically run custom scripts to detect malformed prompts.

---

**Q7.** A software engineering team at a logistics company is building a set of GenAI-powered microservices that integrate with Amazon Bedrock for text classification and summarization. Developers frequently struggle with generating correct AWS SDK code for Bedrock API calls, maintaining consistent testing patterns for model prompts, and performing safe refactoring across multiple Lambda-based services. The team also wants automated recommendations to optimize prompt performance and API usage.

Which solution MOST effectively improves developer productivity while maintaining code quality?

A) Replace the existing microservices with a monolithic containerized application on Amazon ECS and manually implement a unified prompt-testing framework.

B) Use AWS CodeCommit pre-commit hooks to block incorrect API usage and rely on CloudWatch dashboards to manually inspect prompt performance.

C) Use AWS Lambda Powertools to generate code templates for developers and rely on manual code reviews to ensure Bedrock API correctness.

D) Use Amazon Q Developer to generate and refactor Bedrock API integration code, provide inline code suggestions for AWS SDK usage, and assist in building automated test cases for GenAI components.

---

**Q8.** A cryptocurrency risk-monitoring startup uses Amazon Comprehend to extract merchant behavior signals from blockchain-linked descriptions and Amazon SageMaker AI to train a real-time fraud scoring model. The current SageMaker AI endpoint processes thousands of transactions per second, and clients integrate with it using a fixed API contract.

The data science team has produced an upgraded fraud detection model and needs to evaluate its real-world precision and latency. The firm must test the new model under live production load without changing client integrations or reducing throughput of the active model. The testing approach must require minimal operational overhead and allow gradual traffic shifting to measure performance differences.

Which solution will meet these requirements?

A) Create a second SageMaker AI endpoint for the new model and configure Amazon CloudWatch dashboards to compare prediction latency and accuracy side-by-side.

B) Deploy an Amazon API Gateway endpoint that implements a weighted traffic policy to forward some requests to the new SageMaker model.

C) Modify the existing SageMaker AI endpoint configuration to add the new model as an additional ProductionVariant and assign it a small InitialVariantWeight so only a small percentage of live traffic is routed to it.

D) Register the new model in SageMaker Model Registry and configure a Lambda function to automatically swap the live endpoint configuration after the next scheduled evaluation window.

---

**Q9.** A GenAI engineer is developing a customer-support virtual assistant using an Anthropic Claude model on Amazon Bedrock. The assistant provides multi-sentence conversational responses, but the engineer needs the model to halt generation whenever a specific phrase such as “END_OF_SECTION” appears in the output. The application must enforce this behavior consistently without modifying the model weights or relying on prompt-only approaches.

Which solution will meet these requirements?

A) Add the trigger phrase directly into the user prompt instructions to tell the model to stop when the phrase is generated.

B) Tune the top-k sampling parameter to reduce the likelihood of the trigger phrase being generated in the output.

C) Use the stop sequences parameter in the Bedrock inference request to define the trigger phrase that halts text generation.

D) Adjust the temperature parameter to decrease randomness and reduce the chance of generating the trigger phrase.

---

**Q10.** A global insurance company is rolling out a new AI assistant powered by Amazon Bedrock to support claims agents. As part of its updated AI governance program, the security team requires that all interactions with foundation models—across every internal tool and microservice—must automatically apply predefined guardrails. The solution must work across multiple teams with minimal operational overhead and without adding new infrastructure or custom code paths.

Which solution will enforce guardrail compliance for all InvokeModel and Converse API calls in the MOST operationally efficient way?

A) Create a centralized AWS Lambda proxy service that validates incoming payloads and injects guardrail identifiers before forwarding requests to Amazon Bedrock.

B) Store guardrail identifiers in AWS Systems Manager Parameter Store and require all application teams to retrieve the identifier before invoking Amazon Bedrock APIs.

C) Configure IAM policies for InvokeModel and Converse API calls that require the bedrock:GuardrailIdentifier condition key. Apply these policies to all IAM roles that interact with the FM APIs.

D) Configure IAM policies with both the bedrock:GuardrailIdentifier and bedrock:PromptRouterArn condition keys and enforce prompt router validation for all foundation model access.

---

**Q11.** A global hospitality chain operates a multilingual AI concierge built on Amazon Bedrock using the Amazon Titan Text foundation model. The concierge assists guests with booking questions, loyalty program details, and property-specific information. While Titan generates fluent responses, it cannot answer questions that depend on proprietary hotel policies, regional guidelines, or location-specific amenity data stored in Amazon S3 and an internal configuration service.

To improve answer accuracy without retraining the Titan model, an ML engineer wants to add retrieval-augmented generation (RAG) so the concierge can reference real-time private hotel data during inference. The solution must integrate directly with Bedrock, scale automatically, and support query-time grounding across multiple data sources.

Which solution will best meet these requirements?

A) Use Amazon Comprehend custom entity models to provide contextual retrieval capabilities for Titan FM.

B) Fine-tune the Amazon Titan Text model on the company’s hotel policy documents using Amazon SageMaker AI.

C) Set up an Amazon Bedrock knowledge base and connect it to the company’s private data sources to enable retrieval-augmented grounding for Titan FM.

D) Increase context window size and raise the temperature parameter to improve Titan FM’s ability to recall hotel-specific rules.

---

**Q12.** A retail technology team is upgrading its existing order-tracking web application by adding a new GenAI-powered “order explanation” feature that summarizes delays, carrier notes, and historical delivery patterns using an Amazon Bedrock FM. The legacy application calls external services only through REST endpoints and must continue using its current microservices architecture. The team wants to implement a lightweight integration pattern where the application triggers the summarization workflow via a simple API call, while a backend service handles invoking the Bedrock model and returning the generated explanation asynchronously through a webhook.

Which integration approach BEST meets these requirements?

A) Connect the order-tracking application directly to the Bedrock API and perform synchronous inference for each summarization request.

B) Build a step-based polling workflow in the application that repeatedly queries an S3 bucket for the generated summary after the model completes processing.

C) Use API Gateway to expose a REST endpoint that the order-tracking app calls, triggering a Lambda function that invokes the Bedrock model and posts the generated summary back to the application using a webhook URL.

D) Deploy an Amazon ECS service that continuously runs a long-lived container dedicated to invoking Bedrock and exposes its own custom REST API to the application.

---

**Q13.** A financial services company is developing a set of reusable foundation model (FM) prompts for regulatory reporting assistance. The AI governance team requires:

- Strict version control for prompt templates
- A mandatory approval workflow before updating any production prompt
- Centralized storage of all templates for auditing
- Full tracking of who accessed or invoked each prompt
- Logging of prompt usage for compliance reviews

The lead AI engineer must design a governance workflow that satisfies these controls while supporting scalable FM operations across multiple internal teams.

Which solution best meets these organizational requirements?

A) Use Amazon DynamoDB to store all prompts and enable Point-in-Time Recovery (PITR) for version tracking.

B) Use Amazon Bedrock Prompt Management to create parameterized templates with approval workflows, store template artifacts in Amazon S3, track template access with AWS CloudTrail, and send usage logs to Amazon CloudWatch Logs.

C) Use Lambda functions to store prompts in environment variables and rely on Amazon CloudWatch for operational monitoring.

D) Use AWS CodeCommit to store prompt text files and push updates through manual Git-based reviews.

---

**Q14.** A healthcare startup is building an internal clinical summarization tool powered by Amazon Bedrock. The product team wants a simple, accessible interface so non-technical clinicians can generate summaries without learning complex prompt formats. The engineering team also wants to adopt an API-first development approach to ensure the tool can later integrate with other hospital systems. They prefer minimal custom frontend coding but require a way to visually orchestrate prompt logic before embedding it into applications.

Which solution BEST satisfies these requirements?

A) Use AWS Amplify to build a declarative UI for clinicians, define the FM interaction contract using an OpenAPI specification, and use Amazon Bedrock Prompt Flows to visually design and manage the summarization workflow.

B) Use AppSync to automatically generate a GraphQL UI and embed Bedrock model calls directly into the resolvers.

C) Build a custom React frontend hosted on Amazon S3 and manually code all prompt orchestration logic within the browser application.

D) Deploy an EC2-hosted Flask application that exposes Bedrock inference endpoints and handles all UI development using custom HTML templates.

---

**Q15.** A fast-growing online discussion forum is building an automated safety pipeline to moderate user chat rooms and long-form posts. The company stores raw user text in Amazon S3 and uses Amazon Textract to extract text from screenshots uploaded by mobile users. Data scientists use Amazon SageMaker AI to train custom classification models, but the safety team wants an additional managed layer that can quickly detect harassment, hate speech, and other toxic behaviors.

The solution must integrate easily with the existing SageMaker inference flow, support high message throughput, and provide confidence scores so that flagged content can be routed to a human review queue.

Which AWS service provides a fully managed toxicity detection capability that can be inserted into this workflow with minimal additional infrastructure?

A) Use Amazon Bedrock to fine-tune a general-purpose FM to generate safer rewritten versions of user posts.

B) Use Amazon Translate to convert text to a neutral language before toxicity analysis to avoid bias.

C) Utilize Amazon Comprehend toxicity detection to identify abusive or harmful language in user text.

D) Utilize Amazon Comprehend sentiment analysis to detect negative tone and classify toxic messages.

---

**Q16.** A logistics optimization company integrates an Amazon Bedrock foundation model into its planning application. After deployment, developers observe intermittent failures where some requests return malformed responses, while others fail silently with no useful debugging information. The AI engineering team needs a method to diagnose and resolve these FM integration issues by validating requests, capturing detailed error logs, and analyzing problematic responses. The solution must minimize operational overhead and avoid adding unnecessary infrastructure.

Which approach will BEST help the team identify and fix these integration issues?

A) Add a periodic Lambda function that sends synthetic queries to the model and writes the responses to a DynamoDB table for manual inspection.

B) Enable CloudTrail logging for Bedrock API calls and configure an SNS topic to notify developers whenever the InvokeModel API is used.

C) Implement structured error logging and request validation for all Bedrock API calls by enabling Amazon Bedrock invocation logging, adding schema checks on request payloads, and storing malformed FM responses for automated analysis.

D) Require developers to replicate failing cases manually in a staging environment and document findings in an internal wiki.

---

**Q17.** A regional healthcare consortium is building a clinical reasoning assistant that retrieves evidence from internal policy manuals using Amazon Kendra and generates patient-safe explanations with a foundation model in Amazon Bedrock. The system supports multiple care pathways (diabetes, heart disease, oncology), each requiring standardized, reusable prompt templates and adjustable inference parameters such as temperature, top_p, and max_tokens.

The clinical engineering team needs a solution that enforces version control for prompt templates, supports dynamic insertion of retrieved Kendra results, and allows different parameter settings per workflow without modifying application code.

Which solution best satisfies these requirements?

A) Embed prompt templates inside an AWS Lambda function, storing multiple versions in environment variables so that changes only require updating Lambda configuration instead of redeploying.

B) Implement a multi-step Bedrock Prompt Flows pipeline that chains search, reasoning, and summarization prompts, and manually track prompt versions in an external Git repository.

C) Use Bedrock Prompt Management to store reusable, version-controlled prompt templates, define inference parameters within each prompt configuration, and invoke templates via the InvokeModel API after embedding Kendra search results.

D) Save prompt files to an Amazon S3 bucket and load them dynamically in the inference Lambda function, then submit each prompt to CreateModelCustomizationJob to maintain reusability.

---

**Q18.** A global retail organization needs to analyze sensitive customer feedback data using Amazon SageMaker AI notebooks and Amazon Comprehend. Customer review datasets are stored in Amazon S3, and all processing must occur inside a fully isolated VPC. The security team mandates that:

- No traffic may leave the AWS network
- No outbound internet access is allowed
- All service-to-service communication must use private connectivity
- SageMaker notebooks must not use public IPs

The company wants the simplest architecture that enforces these controls with minimal operational overhead.

Which solution meets these requirements?

A) Deploy the SageMaker AI notebook in a private subnet with a route to an internet gateway and send S3 traffic through an external proxy for monitoring.

B) Deploy the SageMaker AI notebook in a private subnet and use a NAT gateway to provide outbound internet access for S3 requests restricted to specific buckets.

C) Deploy the SageMaker AI notebook in a private subnet within a VPC and ensure that the VPC has private endpoints for both SageMaker AI and S3.

D) Deploy the SageMaker AI notebook in a private subnet and create a VPC peering connection to another VPC where S3 is accessible.

---

**Q19.** A financial services firm wants to enhance its internal operations by introducing AI-powered automation across several existing business systems. The compliance team needs automated document enrichment for onboarding forms, while the customer service department wants a knowledge assistant that can search internal policies without exposing data externally. The engineering team also needs a workflow that automatically validates uploaded documents, sends them through an AI classification step, and updates the company’s CRM with finalized metadata.

Which architecture BEST satisfies all requirements?

A) Build a custom EC2-based application that performs AI classification, writes enriched documents to the CRM, and exposes a REST endpoint for customer service queries.

B) Use AWS Step Functions to orchestrate a multi-step AI document workflow, integrate Amazon Bedrock Data Automation for enrichment and classification, and connect Amazon Q Business to internal data sources to provide a secure knowledge assistant for customer service teams.

C) Use a single Lambda function that handles all document processing, integrates directly with Bedrock models, and stores the results in the CRM.

D) Create a Bedrock Agent with internet-enabled knowledge connectors and call it directly from the CRM for document processing and customer service queries.

---

**Q20.** A financial compliance team is building a generative AI assistant to summarize customer communications and detect potential regulatory risks. The incoming data includes long email chains, inconsistent formatting, embedded signatures, and unstructured free-text containing account numbers, dates, and names. The AI engineering team notices degraded FM output quality due to noisy text, missing extracted entities, and inconsistent input structure.

To improve the clarity and consistency of the data sent to the Amazon Bedrock model, the team needs a preprocessing workflow that standardizes text, extracts important entities, and formats inputs consistently before inference.

Which approach BEST meets these requirements?

A) Store the raw email text in Amazon S3, retrieve it using a Lambda function, and forward it unchanged to the Bedrock model.

B) Use Amazon Bedrock to reformat and clean text, Amazon Comprehend to extract key entities such as names and account IDs, and AWS Lambda to normalize and assemble the final structured input for the FM.

C) Pass all raw email text directly to Amazon Bedrock and rely on the model to extract entities and clean formatting implicitly.

D) Use only Amazon Comprehend to extract entities and ignore the formatting issues, allowing the FM to handle inconsistencies during inference.

---

**Q21.** A multinational electronics marketplace is developing a custom multilingual catalog-generation system using Amazon Titan Text on Amazon Bedrock. To improve accuracy for highly specialized product categories, the company plans to fine-tune the Titan model in Amazon SageMaker AI using proprietary product specifications stored in Amazon S3. All training data and fine-tuned artifacts must be encrypted with AWS KMS keys owned by the company.

Once deployed, the Bedrock-hosted model must support full API auditability, and the operations team needs continuous insight into latency and throughput across the company’s active regions in North America and Europe. The solution must minimize custom infrastructure and rely on managed observability wherever possible.

Which architecture meets these security, compliance, and observability requirements?

A) Fine-tune the Titan model in SageMaker AI with SSE-S3 encryption and place an API Gateway proxy in front of Bedrock to capture logs, using Amazon Macie to detect sensitive data in inference requests.

B) Fine-tune the Titan model in SageMaker AI using training data stored in Amazon S3 with KMS encryption, deploy the model through Bedrock using a customer-managed KMS key, enable AWS CloudTrail for all Bedrock API calls, and use Amazon CloudWatch metrics to monitor model latency and throughput across regions.

C) Train Titan entirely within SageMaker AI on EBS volumes encrypted with default keys, deploy the model to a custom EC2 inference cluster, and store API logs manually in Amazon DynamoDB for compliance.

D) Deploy the base Titan model directly on Bedrock without fine-tuning, restrict access through IAM conditions, and rely solely on CloudTrail logs for Bedrock usage visibility.

---

**Q22.** A digital media company is building a content-personalization engine using Amazon SageMaker AI. The ML models are trained using sensitive clickstream and user-preference data stored in Amazon S3, and real-time inference occurs through a SageMaker endpoint. The company also uses Amazon Comprehend to perform sentiment analysis on user comments to enrich the recommendation features.

For strict compliance reasons, the entire solution must operate fully inside a private VPC, prevent all outbound internet access, and allow SageMaker to communicate with Comprehend securely without using public endpoints. The engineering team wants the simplest managed approach that meets these requirements.

Which solution will satisfy the requirements with the least development effort?

A) Activate SageMaker AI network isolation mode to block all external access and create an Amazon Comprehend VPC endpoint inside the same VPC so the model can call Comprehend privately.

B) Deploy SageMaker AI in VPC-only mode and set up an internet gateway with a tightly restricted security group to limit outbound access but still reach Comprehend.

C) Configure SageMaker AI in VPC-only mode, attach a restrictive NACL to block internet access, and allow traffic to the public Comprehend endpoint.

D) Place SageMaker AI in VPC-only mode and create a VPC peering connection to another VPC hosting Comprehend, routing all inference calls through the peered network.

---

**Q23.** A global consulting firm is building an internal generative AI assistant that retrieves policy documents, audit checklists, and architectural playbooks to enhance Bedrock-based RAG responses. The data sources contain inconsistent terminology, older documents with sparse keywords, and highly structured procedure manuals. The AI engineering team reports that pure vector search misses important keyword-specific matches, while pure keyword search fails to surface semantically related content. They also need a secondary scoring step to prioritize the most contextually relevant passages before sending them to the foundation model.

Which retrieval architecture BEST satisfies these requirements?

A) Use DynamoDB queries for keyword filtering and store embeddings in a separate S3 bucket for client-side vector comparison.

B) Use Amazon Bedrock Knowledge Bases with keyword-only retrieval and increase chunk overlap to improve matching.

C) Use Amazon Aurora PostgreSQL with pgvector and rely exclusively on vector similarity scoring.

D) Use OpenSearch with hybrid search that combines BM25 keyword scoring and vector embeddings, followed by a Bedrock reranker model to rescore the top candidates.

---

**Q24.** A global education platform is building a semantic search capability to support its new AI-powered learning assistant. The platform stores millions of unstructured documents—lecture transcripts, instructor notes, solution guides, and support logs—in Amazon S3 after migrating from an aging on-premises file system. The assistant uses Amazon Bedrock for RAG-style reasoning and Amazon Comprehend for classification and entity extraction across the repository.

The company needs a retrieval layer that integrates directly with S3, scales efficiently across terabytes of text, and supports context-aware semantic search without requiring teams to manually build and maintain an embedding pipeline. The solution must return highly relevant passages by meaning—not keywords—while operating as a fully managed service.

Which AWS approach best enables scalable semantic retrieval for the learning assistant?

A) Use AWS Lambda to parse documents, generate embeddings with a custom model, store them in Amazon DynamoDB, and run search queries using DynamoDB scans.

B) Generate embeddings in SageMaker notebooks and store them in SageMaker Feature Store, then perform semantic searches using ad hoc SQL filtering.

C) Ingest S3 documents into Amazon Kendra using the S3 connector and perform semantic search through Kendra's built-in ranking engine.

D) Extract text with Amazon Textract, load it into Amazon Redshift, and use Amazon OpenSearch Service to run semantic queries on the structured tables.

---

**Q25.** A healthcare analytics startup is building a clinical-assistant application that retrieves medical guidelines, treatment protocols, and physician notes to augment foundation model responses. The AI team needs to implement a vector search layer that supports high-dimensional embeddings, real-time indexing of new documents, and fast approximate-nearest-neighbor (ANN) search across millions of vectors. The solution must also integrate cleanly with Bedrock-based RAG pipelines without requiring the team to manage custom vector retrieval logic.

Which vector search solution BEST meets these requirements?

A) Use Amazon DynamoDB with a custom Lambda-based cosine similarity search workflow.

B) Use Amazon S3 to store embeddings in JSON files and perform client-side vector search during inference.

C) Use Amazon Aurora PostgreSQL with pgvector to store all embeddings in a single table without ANN indexing.

D) Use Amazon OpenSearch Service with its vector search engine, ANN support, and Bedrock-compatible retrieval APIs.

---

**Q26.** A multinational investment firm is building an AI-powered research assistant using Amazon Bedrock to support analysts with portfolio risk assessments, market commentary, and cross-asset insights. The assistant must query diverse data sources, including real-time bond yield streams from Amazon Kinesis Data Streams, market anomaly alerts from Amazon CloudWatch, and vector-based similarity search results generated from SageMaker JumpStart embeddings.

The solution must allow the foundation model to safely access these systems without embedding credentials, SDK calls, or query syntax in prompts. The firm also requires a standardized and compliant mechanism for exposing tools that the model can call deterministically at runtime, ensuring all data interactions are auditable and consistently structured.

Which architecture best meets these requirements?

A) Rely on SageMaker JumpStart embeddings alone and depend on the model’s inherent financial reasoning to interpret current market events without direct access to streaming or alert data.

B) Build Lambda functions for each data source and instruct the model to produce the correct function-call syntax inside its prompts so the application layer can execute them.

C) Deploy a unified backend service that exposes Kinesis, CloudWatch, and embedding queries as callable tools using the Model Context Protocol (MCP), enabling secure and structured Bedrock tool use without embedding sensitive logic in prompts.

D) Create microservices for each data source and rely on prompt engineering so the foundation model can decide which service endpoint to call based solely on conversational context.

---

**Q27.** A logistics technology company is deploying a generative AI assistant powered by Amazon Bedrock to help internal teams analyze shipping exceptions. The GenAI engineering team notices that traffic patterns are highly bursty: thousands of short requests arrive during business hours, but overnight traffic drops to almost zero. The team also finds that long prompts occasionally cause slowdowns because token processing time varies significantly between queries.

The company wants to build an efficient resource allocation strategy that minimizes cost, handles spikes predictably, and prevents delays during token-heavy requests. The solution must require minimal custom infrastructure and work seamlessly with Amazon Bedrock.

Which solution BEST meets these requirements?

A) Use Amazon Bedrock invocation metrics to build token-based capacity planning. Configure auto scaling on Provisioned Throughput with target metrics based on prompt and completion token volume, ensuring capacity scales with real GenAI traffic.

B) Place an Amazon API Gateway in front of Amazon Bedrock and throttle requests to flatten traffic spikes before they reach the model.

C) Increase the model’s maximum context window to handle occasional large prompts and disable auto scaling to avoid unpredictable scaling events.

D) Use Amazon SQS to queue all requests and process them using a fixed number of Lambda functions that forward calls to Amazon Bedrock.

---

**Q28.** A global logistics corporation operates sorting centers in regions with limited or intermittent internet access. The company wants to automate real-time measurement of parcel dimensions using cameras deployed along conveyor belts.

The data-science team has already collected extensive video footage and will use Amazon SageMaker AI for model training. Amazon Rekognition will support initial labeling of package boundaries to accelerate dataset preparation. Because network connectivity is unreliable, the inference system must run entirely on-site, making routing decisions in milliseconds without requiring round-trip calls to the cloud.

The solution should minimize operational overhead, support continuous model updates from the cloud when connectivity is available, and allow local execution of both inference and simple post-processing logic.

Which solution best meets these requirements?

A) Train the detection model in SageMaker AI and deploy it on Amazon ECS clusters running at each facility, using containers to run batch inference on incoming video frames.

B) Use SageMaker AI to train an object-detection model and deploy it directly to AWS IoT Greengrass devices running at each site, with AWS Lambda performing local routing decisions using the model outputs.

C) Deploy the trained model on SageMaker AI real-time inference endpoints and stream video to the cloud using Amazon Kinesis Video Streams for continuous evaluation.

D) Use Rekognition Custom Labels for model training and deploy inference on local EC2 instances, sending routing results to the cloud through Amazon EventBridge.

---

**Q29.** A digital publishing platform is developing an AI-assisted editorial tool for writers. The tool must analyze draft content on demand and stream revision suggestions directly into a browser-based editor. Articles include metadata labels such as politics, entertainment, and opinion, which determine the editorial rules to apply. Editors require suggestions to begin streaming immediately when they click an “Analyze Draft” button. The company wants to use an Amazon Bedrock FM with custom style guidelines and must minimize operational overhead while supporting real-time, bidirectional communication.

Which architecture will meet these requirements with the LEAST operational overhead?

A) Create an Amazon API Gateway REST API with Lambda function URLs and enable chunked transfer encoding to deliver streaming responses to the editor.

B) Deploy an Amazon API Gateway WebSocket API integrated with an AWS Lambda function. Configure the function to read metadata labels and route requests to the corresponding Amazon Bedrock model and style guide prompts. Use Amazon Bedrock response streaming to push real-time suggestions back to the editor interface.

C) Use Amazon SQS to queue each analysis request and trigger AWS Step Functions workflows. Use Lambda functions for category routing and Bedrock invocations. Store outputs in DynamoDB and push results to clients over WebSocket connections.

D) Run custom containerized services on Amazon ECS behind an Application Load Balancer. Implement metadata-based routing and WebSocket streaming in the containers. Use Bedrock streaming for model-generated suggestions.

---

**Q30.** A global enterprise SaaS provider is building a threat-intelligence email classifier on Amazon SageMaker AI to detect malicious content across millions of internal security alerts. The ML team wants to use transfer learning by starting with a pretrained BERT model hosted in Amazon S3. They plan to fine-tune this model on a labeled dataset of “malicious” vs. “benign” security messages processed with Amazon Comprehend to extract domain entities.

To maximize accuracy and reduce training cost, the team must correctly initialize the BERT model using its pretrained weights while replacing only the components specific to the classification objective. The solution must ensure that the model starts with the full pretrained language understanding of BERT while learning a new task-specific output structure.

Which approach correctly initializes BERT for fine-tuning in this scenario?

A) Load pretrained weights for all layers while keeping the original classifier frozen, and train a separate external classifier on top of the pooled output vector.

B) Initialize BERT with its pretrained weights and convert the output classifier into a multi-task prediction head, then fine-tune the entire network on the labeled security dataset.

C) Load the pretrained model weights and attach an additional classifier head that operates in parallel with the existing output layer, training only this new classifier.

D) Apply pretrained model parameters across all transformer layers, remove the original classification layer, and add a new task-specific classifier trained using the labeled dataset.

---

**Q31.** A retail analytics company is building a generative AI system on Amazon Bedrock to generate product descriptions for thousands of new SKUs each week. The GenAI engineering team is receiving complaints that outputs vary too widely in creativity and tone across similar products. The team wants to optimize output consistency while still allowing small variations in style. They also want to evaluate the effect of several parameter configurations before making a production change.

Which approach will BEST meet these requirements with the MOST controlled performance?

A) Use speculative decoding with a draft model to reduce latency and rely on the draft model for deterministic text patterns.

B) Disable all sampling parameters by setting temperature to 0 and top-k to 1 to completely standardize outputs for all products.

C) Perform A/B testing of multiple model parameter profiles, using a lower temperature with moderate top-p sampling to constrain randomness while keeping stylistic variation.

D) Switch to a larger and more expensive FM for improved text quality, assuming the additional model capacity will inherently stabilize style.

---

**Q32.** A logistics automation company uses Amazon Bedrock to power a routing assistant that generates shipment instructions for warehouse workers. After recent updates to several prompt templates, the engineering team notices growing inconsistencies: incorrect JSON formatting, missing required fields, and occasional prompt confusion when processing similar instructions.

The team wants to troubleshoot these prompt maintenance issues by adding systematic observability, validating template structures, and detecting where specific prompts fail. The solution must minimize manual review and support ongoing refinement of multiple prompt templates across services.

Which actions will BEST help the team identify and resolve these prompt-related issues? (Select TWO.)

(Choose 2)

A) Increase the foundation model’s inference latency timeout so longer instructions are processed, reducing confusion caused by template changes.

B) Use AWS X-Ray to build a prompt observability pipeline that traces prompt flow, identifies failing templates, and surfaces latency or structure anomalies.

C) Switch to a larger foundation model variant without performing diagnostics to compensate for prompt inconsistencies.

D) Disable schema validation logic to avoid false positives during prompt template transitions.

E) Enable CloudWatch Logs for all Amazon Bedrock model invocations and analyze prompt–response pairs to detect confusion patterns and formatting failures.

---

**Q33.** A large academic research consortium is building a generative AI content-analysis platform for summarizing manuscripts and generating literature insights. The organization uses Amazon Comprehend for preprocessing, along with Amazon Bedrock Agents to orchestrate retrieval, citation checks, and workflow automation across several research groups.

A machine learning engineer has fine-tuned a large language model (LLM) externally and stored the artifacts in an internal Amazon S3 bucket. Multiple research analysts, who share the same SageMaker AI domain as the engineer, want to experiment with text-generation capabilities using SageMaker Canvas. The engineer must make the model accessible within Canvas while ensuring it is properly registered and controlled through SageMaker AI.

Which combination of steps will enable SageMaker Canvas access to the model? (Select TWO.)

(Choose 2)

A) The analysts must create a shared collaborative Canvas workspace to expose the model automatically to all users in the domain.

B) The research analysts must be granted IAM permissions to access the S3 bucket that stores the model artifacts.

C) The engineer must convert the LLM into a Hugging Face format before Canvas can load it.

D) The engineer must deploy the model as a real-time SageMaker endpoint to enable Canvas discovery.

E) The engineer must register the model in the SageMaker Model Registry so it becomes available for Canvas users within the shared SageMaker domain.

---

**Q34.** A financial-services firm is building an Amazon Bedrock–powered insights assistant that summarizes analyst notes and recommends follow-up actions. Early testing shows frequent variability in reasoning steps, inconsistent output formatting, and occasional omission of required financial metrics. The lead GenAI engineer must refine the system so the FM consistently follows the expected reasoning flow, emits structured outputs, and improves over time using user-generated feedback.

Which approach should the engineer implement to enhance FM response quality?

A) Enable JSON mode and rely solely on temperature reduction to enforce consistent response formatting.

B) Create multiple independent prompts for each department and allow analysts to manually choose which prompt to run for each query.

C) Use structured input components and output specification templates, reinforce reasoning with chain-of-thought instruction patterns, and incorporate a feedback loop that adjusts prompt parameters based on real-world user ratings.

D) Periodically fine-tune a custom model whenever users report inconsistent results, without modifying the prompting strategy.

---

**Q35.** A healthcare AI team is developing a medical-image classification pipeline using Amazon SageMaker AI. Training data is stored in one Amazon S3 bucket, while model artifacts and evaluation metrics must be written to a second S3 bucket. Due to strict compliance rules (HIPAA and internal security policies), the SageMaker notebook environment must use least-privilege access and may not rely on public access points or temporary federation mechanisms.

The team needs a secure method that allows the SageMaker notebook to read training data and write model outputs to the designated S3 buckets, while ensuring all permissions are tightly scoped and managed through AWS-native access controls.

Which approach should the team implement?

A) Use an S3 Access Point configured for open access and associate it with the SageMaker notebook to simplify bucket permissions.

B) Configure IAM identity federation for the SageMaker notebook so that it assumes an external federated role to access the S3 buckets.

C) Create an S3 bucket policy that allows unrestricted access for the SageMaker notebook ARN to retrieve and write objects.

D) Attach an IAM policy to the SageMaker execution role that grants s3:GetObject, s3:PutObject, and s3:ListBucket permissions for only the required S3 buckets.

---

**Q36.** A security-focused ML engineering team is building a controlled workflow that uses Amazon SageMaker AI for model training and Amazon Comprehend for entity extraction. The workflow is orchestrated with AWS Step Functions and triggered using Amazon EventBridge rules. Because the environment processes regulated customer data, all SageMaker API calls must remain private and must only be allowed from a small group of approved EC2 instances and IAM identities.

To meet these requirements, the team provisions a VPC interface endpoint for the SageMaker Service API in a dedicated subnet. They now need to ensure that only the approved compute instances and authorized IAM principals can send requests through this endpoint and that the endpoint cannot be accessed broadly across the VPC.

Which combination of actions will correctly enforce these access restrictions? (Select TWO.)

(Choose 2)

A) Enable private DNS on the VPC endpoint to route SageMaker traffic internally.

B) Attach a custom VPC endpoint policy that explicitly grants SageMaker access only to approved IAM users and roles.

C) Configure the security group associated with the endpoint’s network interface to allow inbound traffic only from the specific EC2 instances that require SageMaker access.

D) Deploy an additional VPC endpoint for SageMaker AI Runtime to isolate inference-related operations.

E) Enable VPC Flow Logs and trigger an AWS Lambda function to automatically block suspicious or unauthorized API calls.

---

**Q37.** A hospitality technology company deploys an Amazon Bedrock–powered AI concierge that handles customer inquiries, recommends services, and processes reservation requests. As usage grows, leadership wants a unified observability solution that provides actionable insights across model behavior, business impact, compliance adherence, customer interaction patterns, and forensic traceability for troubleshooting. The engineering team needs an approach that uses managed AWS services, avoids custom analytics pipelines, and supports operational metric dashboards, interaction tracking, and request-level audit trails.

Which combination of actions will BEST meet these requirements with minimal operational overhead? (Select TWO.)

(Choose 2)

A) Export all interaction metadata and model inputs/outputs to S3, build an EMR-based pipeline to generate traceability reports, and visualize compliance metrics in Amazon QuickSight dashboards refreshed nightly.

B) Instrument the application to push user interaction events, conversion signals, and recommendation outcomes to Amazon CloudWatch metrics. Build business impact dashboards and anomaly detection alarms directly in CloudWatch for proactive insight.

C) Set up Amazon Kinesis Data Streams to capture FM invocations, build a real-time processing layer in AWS Lambda for behavior classification, and push summarized metrics into DynamoDB for downstream visualization.

D) Configure AWS CloudTrail event selectors for Bedrock API calls and forward logs to an external SIEM for token usage monitoring, prompt failure analysis, and dashboarding.

E) Enable Amazon Bedrock Model Invocation Logs and store them in CloudWatch Logs to capture detailed request and response traces. Use CloudWatch dashboards to visualize model behavior patterns, prompt-response correlations, and operational performance KPIs.

---

**Q38.** A global entertainment studio is building a generative AI system that produces long-form narrative scripts, multilingual promotional content, and localized dialogue for international releases. The system uses Amazon SageMaker AI to fine-tune a custom 250-billion-parameter language model on decades of archived scripts, audience engagement metadata, and regional cultural datasets.

The company also uses Amazon Comprehend to analyze live social feeds and inject sentiment-aware signals into the training pipeline. Due to the size and complexity of the model, the data science team requires extremely high-throughput distributed training with optimized cost-performance characteristics. The solution must minimize training time while maintaining full scalability across multiple nodes.

Which Amazon EC2 instance type is the MOST appropriate choice for this fine-tuning workload?

A) Select purpose-built Trn series EC2 instances designed for large-scale, high-performance training of massive language models.

B) Use accelerated-computing G-series EC2 instances to perform lightweight pre-processing and sentiment enrichment from Comprehend.

C) Use compute-optimized C-series EC2 instances inside SageMaker AI to reduce training costs across distributed nodes.

D) Deploy GPU-based P-series EC2 instances for both fine-tuning and hosting the final model in SageMaker AI endpoints.

---

**Q39.** A renewable-energy research institute deploys hundreds of off-grid environmental sensors that record humidity, vibration signatures, and voltage stability across remote microgrid sites. Engineers plan to use Amazon SageMaker AI to train predictive models and Amazon Comprehend to extract contextual events from maintenance logs. Due to highly unreliable network connections, the sensors send compressed telemetry via MQTT whenever connectivity becomes available.

The AI engineering team must design an ingestion pipeline that reliably routes all MQTT messages into Amazon S3 with minimal operational overhead, supports scalable downstream ML processing, and integrates cleanly with other AWS analytics services.

Which solution will BEST meet these requirements?

A) Route the MQTT telemetry to AWS IoT Core and configure an IoT Core rule to deliver the data to an Amazon Data Firehose stream that writes directly to Amazon S3.

B) Deploy AWS IoT Greengrass components on each sensor to locally preprocess data and periodically push batches to S3 using the AWS SDK.

C) Stream MQTT messages from IoT devices to AWS IoT Core, forward them into a Kinesis Data Stream, and use a Lambda consumer to upload the processed data into S3.

D) Expose a public API using Amazon API Gateway for the sensors to POST telemetry, and invoke Lambda to write the incoming payloads into S3.

---

**Q40.** A media analytics company uses an Amazon Bedrock foundation model to extract insights from long interview transcripts. Recently, analysts reported that the model occasionally drops important context near the end of the transcript and produces incomplete summaries. The engineering team confirms that some requests are exceeding the model’s context window but cannot reduce transcript length due to business requirements. They need a systematic method to detect overflow conditions, ensure full content coverage, and prevent truncation-related errors during FM interactions without rewriting the summarization logic from scratch.

Which solution will BEST address these requirements?

A) Enable CloudTrail logging for Bedrock API calls and configure SNS alerts when transcripts exceed a predefined size threshold.

B) Require analysts to manually shorten long transcripts before submission and maintain a shared spreadsheet to track incomplete summaries.

C) Implement an S3 event-triggered Lambda function that compresses transcripts before sending them to the model so they fit inside the FM’s input size limit.

D) Enable context window overflow diagnostics and apply a dynamic chunking strategy that segments transcripts based on token boundaries, combined with prompt design adjustments that stitch summaries consistently without information loss.

---

**Q41.** A healthcare analytics company deploys multiple foundation models on Amazon Bedrock to generate clinical insights for internal medical review teams. Leadership wants recurring reports that clearly compare model accuracy, latency trends, cost-per-output, and quality scores from recent evaluations. Stakeholders require visual dashboards, automated weekly summaries, and the ability to compare model performance over time without building custom pipelines or maintaining bespoke reporting infrastructure. The engineering team must choose a solution that uses managed AWS services, scales automatically, and integrates seamlessly with existing Bedrock data sources.

Which solution will BEST meet these requirements?

A) Enable Amazon Bedrock Model Evaluation reports, export evaluation metrics to Amazon CloudWatch, and build automated Amazon QuickSight dashboards that visualize model quality, latency trends, and cost metrics. Schedule weekly email summaries using QuickSight’s built-in reporting capabilities.

B) Use SageMaker Studio to manually generate performance notebooks each week and upload visualizations to QuickSight dashboards for stakeholder access.

C) Export Bedrock invocation logs to Amazon S3, create an Athena query layer, and build a custom React dashboard hosted on Amazon S3 with CloudFront. Run scheduled Lambda jobs to email raw CSV reports to stakeholders.

D) Stream invocation logs to Amazon OpenSearch Service and configure custom index visualizations with Kibana. Schedule weekly exports of visualization screenshots to S3 for distribution.

---

**Q42.** A national insurance provider is developing an AI-driven claims assistant that interacts with customers through a mobile app. The assistant accepts text descriptions of incidents, voicemail transcriptions processed by Amazon Transcribe, and scanned document uploads analyzed with Amazon Rekognition. Regulatory requirements mandate that any personally identifiable information (PII)—including names, phone numbers, policy numbers, and addresses—must be identified and masked before the data is stored or forwarded to downstream analytics services.

The data engineering team wants a solution that can automatically detect and redact PII across all text-based inputs, works at scale, and requires minimal ongoing maintenance. They prefer to avoid building or training custom NLP models and want to integrate the solution with their existing AWS pipeline.

Which solution should the company implement?

A) Use Amazon SageMaker Canvas to train a custom PII detection model that processes text extracted from documents and conversations.

B) Leverage Amazon Comprehend to automatically detect and redact sensitive personal information from all text-based inputs before storage or downstream processing.

C) Configure Amazon Lex to perform real-time PII redaction during conversational interactions across all channels.

D) Deploy a custom PII-redaction pipeline using Hugging Face Transformers trained on proprietary insurance data and hosted on Amazon SageMaker.

---

**Q43.** A financial services company is building a multi-agent GenAI workflow that automates regulatory document reviews. The solution requires an “extraction agent” to summarize new documents, a “compliance agent” to classify risk levels, and a “decision agent” that determines escalation. Each agent uses separate Amazon Bedrock prompts and must pass structured results to the next stage. The orchestration must support retries, branching logic, and detailed execution traces for debugging.

Which architecture BEST supports this multi-agent orchestration pattern?

A) Use a single Lambda function that contains conditional logic to call each Bedrock agent sequentially and logs execution results to CloudWatch Logs.

B) Use Amazon SQS to trigger Bedrock requests in order and rely on DynamoDB streams to store intermediate responses for each agent.

C) Use AWS Step Functions to orchestrate the multi-agent workflow, invoking Amazon Bedrock for each agent step and passing structured outputs between agents to implement prompt chaining patterns.

D) Host the agent logic on Amazon EC2 instances and manually implement a custom orchestration framework to route prompts between agents.

---

**Q44.** A media production company is building a text-to-image generation service using a pre-trained Hugging Face diffusion model that was tested successfully in Amazon SageMaker JumpStart. The engineering team now needs to deploy the model so users can generate images on demand through an internal application. The solution must use GPU instances for inference, support text description datasets up to 50 MB in size, and return responses in near real time to support interactive creative workflows. The company wants a deployment option that minimizes latency and delivers consistent performance under variable user load.

Which deployment strategy will meet these requirements?

A) Use a SageMaker Real-Time Inference endpoint with a GPU-based instance type and invoke the endpoint directly from the application to generate images on demand.

B) Create a SageMaker batch transform job that uses a GPU-based instance type and invoke the job from a Lambda function whenever a user submits a text prompt.

C) Use a SageMaker Serverless Inference endpoint with a general-purpose instance type and invoke image generation through an AWS Lambda function.

D) Use a SageMaker Asynchronous Inference endpoint with a GPU-based instance type and trigger inference through an AWS Lambda function to handle on-demand image generation.

---

**Q45.** A global law firm is building an AI-powered knowledge assistant to help attorneys search, summarize, and cross-reference legal documents. The team already uses Amazon SageMaker Ground Truth to label case summaries and enrich document metadata.

The next phase introduces Amazon Bedrock agents, which must interpret attorney queries, summarize large legal filings, and provide context-aware recommendations. To support this, the solution must generate high-quality semantic embeddings for both queries and documents so the agent can retrieve relevant content during RAG workflows.

The firm requires a fully managed and scalable approach that integrates natively with Bedrock and supports storing embeddings in an existing OpenSearch cluster used for legal document indexing.

Which approach best satisfies these requirements?

A) Leverage Amazon Titan Text Embeddings in Bedrock to convert legal documents and queries into semantic vectors and store them in Amazon OpenSearch Service for retrieval-augmented reasoning by Bedrock agents.

B) Deploy a fine-tuned model in SageMaker JumpStart to generate document summaries and connect the model output to the Bedrock agent using Lambda integration.

C) Use Amazon Kendra to index legal documents and allow AI agents to query them directly using built-in natural-language search and ranking capabilities.

D) Use SageMaker Data Wrangler to cluster legal text into feature groups and let agents analyze similarities using the structured dataset created during preprocessing.

---

**Q46.** A national mortgage lender processes large volumes of scanned loan packets, health disclosures, and insurance attachments each day. Amazon Textract extracts the text, and Amazon Comprehend classifies financial entities such as loan numbers, debt ratios, and income indicators. Some documents contain handwritten notes, inconsistent formatting, and low-quality scans, leading to low-confidence predictions that frequently break downstream verification pipelines. Human analysts must manually review these cases, slowing loan approvals and increasing operational cost.

The lender wants to reduce manual review while maintaining strict accuracy requirements for regulated financial records. The solution must automatically route only uncertain predictions to human reviewers and allow high-confidence extractions to pass through validation without human intervention. The company wants a scalable, managed workflow with minimal custom code.

Which approach will most effectively optimize document-processing throughput while maintaining accuracy?

A) Configure Amazon Textract to send low-confidence fields to Amazon Augmented AI (A2I) so reviewers can validate the extracted content before downstream validation.

B) Reprocess low-confidence extractions with a Bedrock Claude model to predict corrected values, then send results to humans for final review.

C) Use Textract to flag uncertain text, then send documents to SageMaker Ground Truth for a full labeling job before validation.

D) Use an Amazon Titan model to predict and auto-correct low-confidence fields, eliminating human review entirely.

---

**Q47.** A logistics optimization company uses Amazon Bedrock Agents to orchestrate multiple tools that retrieve shipment data, calculate routing, and generate delivery recommendations. As tool usage increases, the engineering team notices inconsistent tool latency, unexpected call sequences, and occasional failures during multi-agent coordination. Leadership requires a tool performance framework that can track tool call patterns, measure tool execution metrics, detect anomalies against historical baselines, and provide full observability of agent-to-tool interactions. The team prefers a solution that minimizes custom infrastructure and leverages managed AWS services for insight generation.

Which combination of actions will BEST meet these requirements with the least operational overhead? (Select TWO.)

(Choose 2)

A) Export all tool input/output payloads to S3 and build a daily AWS Glue ETL job to aggregate performance metrics. Store results in Amazon Redshift and create diagnostic dashboards in QuickSight.

B) Use CloudWatch metrics to track tool invocation duration, success rate, retry counts, and error categories. Configure CloudWatch anomaly detection against historical patterns to identify unusual tool behavior.

C) Deploy a Kinesis Data Firehose stream to capture tool interactions in near real time, enrich records with Lambda, and push aggregated data into OpenSearch for custom tool usage indexing and search.

D) Forward agent and tool API activity logs to an external observability platform via CloudTrail Lake to analyze tool invocation patterns, cost trends, and correlation graphs.

E) Enable Amazon Bedrock Model Invocation Logs for the agent and tools and send them to CloudWatch Logs. Use CloudWatch dashboards to visualize tool call sequences, agent coordination behavior, and performance metrics.

---

**Q48.** A multinational retailer is building a multilingual generative support assistant using Amazon SageMaker Unified Studio and SageMaker JumpStart. The team deployed a large foundation model to a single SageMaker AI real-time endpoint and wants to personalize behavior for several regional markets using lightweight LoRA adapters. The base model must remain unchanged, and the team wants to avoid maintaining separate endpoints for each region. The solution must allow the inference call to specify which regional adapter to apply.

Which solution will meet this requirement?

A) Create a SageMaker multi-model endpoint and package each region’s LoRA adapter as a separate model, relying on container routing to select the adapter.

B) Mount an Amazon EFS volume that stores all LoRA adapters and dynamically load the correct file at runtime inside the endpoint container.

C) Use an AWS Lambda step to load the correct regional LoRA weights from Amazon S3 and inject them into the model container before the inference request.

D) Deploy the base foundation model to one SageMaker AI real-time endpoint and create separate adapter inference components for each region, each containing its LoRA artifacts, then invoke the endpoint while specifying the appropriate adapter.

---

**Q49.** A financial services company is building an internal compliance assistant powered by Amazon Bedrock. The assistant must always respond in a formal advisory tone, avoid providing personal financial recommendations, and consistently follow a strict response structure that includes a summary, regulatory references, and approved disclaimers. The AI engineering team also needs a mechanism to explicitly restrict discussions of prohibited investment topics while allowing the model to answer general compliance questions safely. They want a centralized way to manage these behavior rules and enforce them across multiple prompts and FM workflows.

Which solution should the team implement to ensure the model consistently follows required instructions and avoids restricted outputs?

A) Hardcode the assistant’s tone and policy text into every prompt template used by the application’s API calls.

B) Use Step Functions to route user messages to different prompt templates depending on the detected topic.

C) Use Amazon Bedrock Prompt Management to enforce role definitions and response templates, combined with Amazon Bedrock Guardrails to block restricted financial topics and enforce responsible AI behavior.

D) Use Lambda functions to inject a preset tone, disclaimers, and formatting rules before each model invocation.

---

**Q50.** A global broadcasting company wants to build an AI-powered investigation assistant that helps reporters search across years of mixed media assets, including transcripts, photographs, satellite imagery, and recorded interviews. The organization plans to use Amazon Bedrock Data Automation (BDA) to automatically extract topics, entities, timestamps, and visual attributes from all media types.

To support natural-language queries such as “Find the segment where the analyst discussed economic sanctions while showing satellite images of cargo ships”, the system must enable multimodal semantic retrieval and provide the retrieved context to a foundation model hosted on Amazon SageMaker AI for answer generation.

Which architecture will best satisfy these requirements?

A) Use Bedrock Data Automation (BDA) to preprocess the media files and store extracted metadata in DynamoDB. Query DynamoDB directly from a SageMaker-hosted model for response generation.

B) Process media through BDA and stream the insights to Amazon OpenSearch Service. Perform vector search directly from the model prompt and have SageMaker AI interpret raw search results.

C) Leverage Bedrock Data Automation (BDA) to extract structured insights from text, images, audio, and video; index the enriched content inside Bedrock Knowledge Bases for multimodal semantic search; and pass retrieved context to a foundation model deployed on SageMaker AI for response synthesis.

D) Use only BDA to extract entities and topics, skip building a retrieval index, and feed the entire structured dataset into the SageMaker AI model at inference time for complex reasoning.

---

**Q51.** A government-regulated medical research institute is building a hybrid AI platform to forecast patient recovery outcomes using both structured records and unstructured physician notes. Historical clinical data resides in an on-premises Microsoft SQL Server database, while non-sensitive operational metrics may be transferred to Amazon S3 for periodic retraining of models deployed in Amazon SageMaker AI. Sensitive patient-identifying data is legally restricted from leaving the on-premises facility.

All cloud-bound data transfers must occur over a secure IPsec tunnel using an existing AWS Site-to-Site VPN. The engineering team needs a daily automated process that extracts only non-sensitive fields from the SQL Server database and uploads them to Amazon S3 without exposing any restricted medical information.

Which solution meets all compliance and transfer requirements?

A) Configure Amazon Kinesis Data Streams to batch-ingest SQL Server records from the on-premises environment and use AWS Lambda to remove sensitive attributes before delivery to S3.

B) Deploy AWS Database Migration Service (AWS DMS) to replicate the SQL Server database to S3 and rely on table-mapping rules to exclude sensitive data during the migration process.

C) Use Amazon DataSync to transfer full SQL Server database exports to S3 daily, then apply server-side filtering with AWS Lambda to remove regulated medical fields before retraining.

D) Set up an AWS Glue ETL job to connect to the on-premises SQL Server using a JDBC connection, filter out sensitive columns, and securely load the sanitized dataset into Amazon S3 through the Site-to-Site VPN.

---

**Q52.** A global consulting firm is building an enterprise knowledge assistant that must retrieve information from millions of documents, including case studies, contracts, industry reports, and compliance manuals. The system must support semantic retrieval, topic-level segmentation, and hierarchical organization to surface accurate and context-rich responses for downstream FM augmentation.

The AI architecture team requires a vector database strategy that can handle large-scale embeddings, manage parent/child hierarchical document structures, and support fast semantic queries across diverse content types. Additionally, the team wants the retrieval pipeline to integrate natively with Amazon Bedrock for prompt augmentation.

Which architecture BEST meets these requirements?

A) Build a DynamoDB table with only scalar metadata fields and store raw documents in Amazon RDS, performing all vector similarity logic manually inside application code.

B) Use a single OpenSearch index with keyword analyzers and disable vector embeddings to minimize storage overhead.

C) Store all documents as raw text objects in Amazon S3 and perform keyword search using Athena SQL queries before passing results to the FM.

D) Use Amazon Bedrock Knowledge Bases for hierarchical document organization with automatic embedding generation, and integrate Amazon OpenSearch Service with the Neural plugin for topic-based segmentation and high-performance semantic retrieval.

---

**Q53.** The raw claims data contains names, phone numbers, credit card details, and other sensitive PII. The team stores the raw dataset in Amazon S3 and uses Amazon Comprehend for feature extraction on text fields.

To comply with strict data governance rules, the company must meet two requirements before training the model:

1. All data at rest must be encrypted using AWS-managed keys. 2, All PII—especially credit card numbers—must be removed or masked before any data is accessed by SageMaker AI.

The data engineering team wants a managed service that can automatically process and sanitize the dataset each day before training.

Which solution will best satisfy these requirements?

A) Use Data Wrangler to manually remove PII and reupload the cleaned dataset to S3. Enable client-side encryption using a custom encryption library.

B) Encrypt all datasets with AWS KMS in S3 and use AWS Glue ETL jobs to scan the claims dataset, redact credit card details, and write sanitized outputs to a separate S3 location for SageMaker AI training.

C) Use Comprehend to detect PII inside SageMaker AI, then apply a masking step inside the training script before loading the data into the model.

D) Train the model on encrypted raw data and rely on algorithm-level preprocessing (such as PCA or feature scaling) to obscure or eliminate sensitive information before model ingestion.

---

**Q54.** A global research firm is building a retrieval-augmented generation (RAG) system on Amazon Bedrock to support analysts who query large volumes of scientific papers. Analysts report that retrieval is sometimes slow and the relevance of returned passages is inconsistent. A GenAI engineer must enhance both retrieval speed and the quality of retrieved context before it is sent to the foundation model.

Which combination of steps will MOST effectively meet these requirements?

(Choose 2)

A) Increase the number of vectors stored in the index by embedding every sentence separately, regardless of semantic similarity.

B) Preprocess incoming queries by normalizing punctuation, removing stopwords, and expanding abbreviations to improve embedding consistency before vector retrieval.

C) Use CloudTrail Lake queries to analyze retrieval timing and manually adjust index shards each week to maintain performance.

D) Route all retrieval queries directly to the foundation model and rely on FM reasoning to determine the most relevant documents.

E) Implement a hybrid search pipeline in Amazon OpenSearch Serverless that combines vector search with BM25 keyword scoring, and apply custom ranking weights based on document type.

---

**Q55.** A fintech startup is building a conversational compliance assistant that interacts with Amazon Bedrock models through a custom API layer. The assistant must provide real-time streamed responses to users, enforce token limits to prevent oversized prompts, and handle occasional model timeouts through controlled retries. The engineering team wants a managed interface that supports request validation, incremental response delivery, and retry-safe error handling without placing this burden on the application servers.

Which solution BEST meets these requirements?

A) Call Bedrock models directly from the application server and implement retry, chunking, and token validation manually in the backend logic.

B) Use Amazon SQS to pass FM requests to a worker fleet of EC2 instances that stream results back to users over long-lived connections.

C) Use Amazon API Gateway to expose a custom FM API with request validation, chunked transfer encoding for streaming Bedrock responses, and an AWS SDK–based retry strategy in integrated Lambda functions.

D) Use AWS AppSync to handle streaming requests and enforce token limits before invoking the Bedrock model directly.

---

**Q56.** A global e-commerce enterprise is building an intelligent natural language processing (NLP) system to enhance its customer engagement platform, TD-Assistance. The company uses Amazon Bedrock to access a foundation model for generative conversational responses and Amazon SageMaker AI to fine-tune a BERT-based model on proprietary chat transcripts for sentiment and intent analysis.

The training dataset, which contains sensitive customer messages, is stored in an Amazon S3 bucket. To improve performance, the SageMaker training job is configured for distributed training across five compute instances.

The data science team must encrypt the dataset, model checkpoints, and intermediate artifacts both at rest and in transit. Additionally, all node communications must be secure, and data transfers should never traverse the public internet.

Which combination of actions will meet these security and compliance requirements for the distributed training workload? (Select THREE.)

(Choose 3)

A) Deploy the distributed training jobs in a restricted VPC environment with inter-container traffic encryption enabled.

B) Provision an S3 VPC endpoint to isolate network traffic and apply fine-grained endpoint and S3 bucket access policies.

C) Deploy an AWS Network Firewall in the VPC to inspect and filter traffic between SageMaker containers during training.

D) Create AWS PrivateLink interface VPC endpoints to route training data and model checkpoints to S3 and internal services.

E) Attach a SageMaker execution role with read-only access rights to required resources in the training environment.

F) Configure the network security group (NSG) to accept inbound communication originating from peer training containers.

---

**Q57.** A global music-streaming provider is building a personalization engine using Amazon SageMaker AI to recommend playlists to millions of listeners worldwide. The ML team trains a neural network that predicts music preferences based on listening history, skipped tracks, mood-tagged playlists, and regional genre trends. After deployment, the compliance team observes that certain musical genres are recommended significantly more or less frequently in specific geographic markets, raising concerns about unintended demographic bias.

To meet internal fairness mandates and regulatory transparency requirements, the organization must analyze whether bias exists in the training dataset, determine whether the deployed model is amplifying bias in predictions, and automatically generate explainability reports showing which features most strongly influence playlist recommendations.

Which solution should the company implement to identify, measure, and explain potential bias across both the dataset and the model outputs?

A) Use SageMaker Model Monitor to track error rates, latency, and data drift without evaluating fairness or explaining feature influence.

B) Use SageMaker Clarify to detect dataset bias, evaluate model bias during inference, and generate feature attribution explainability reports for compliance and transparency.

C) Use Amazon Personalize with automatic weight balancing to reduce region-specific recommendation skew without performing explicit fairness analysis.

D) Use SageMaker Data Wrangler to manually rebalance the listening-history dataset before retraining the personalization model.

---

**Q58.** A retail analytics startup uses an Amazon Bedrock foundation model to generate weekly market-insight summaries for its clients. After several prompt updates, the team notices inconsistent tone, missing numerical breakdowns, and occasional hallucinated recommendations. The lead AI engineer must implement an automated quality assurance workflow that validates expected structure, checks edge-case responses, and monitors for prompt regressions before new versions are deployed to production.

Which approach should the engineer implement to ensure reliable and consistent prompt behavior?

A) Use CodeBuild with a scheduled pipeline that runs unit tests against the prompt text stored in an S3 bucket.

B) Enable Amazon GuardDuty to scan all prompt output for anomalies and escalate findings to the security team.

C) Store sample prompts in DynamoDB and manually review generated outputs from the model console before each deployment.

D) Build a QA workflow using Lambda functions to validate expected output fields, Step Functions to orchestrate edge-case prompt tests, and Amazon CloudWatch Logs to detect regression patterns across prompt versions.

---

**Q59.** A healthcare analytics company uses a Retrieval-Augmented Generation (RAG) workflow on Amazon Bedrock to help clinical researchers summarize medical guidelines. After a recent data refresh, the AI engineering team notices that responses are increasingly irrelevant, missing key medical details, and referencing outdated chunks. The team must diagnose and resolve issues affecting retrieval quality. The solution must focus on identifying retrieval-specific failures, detecting embedding or vector drift, and validating that preprocessing and chunking remain effective.

Which combination of actions will BEST help the team identify and resolve the retrieval issues? (Select TWO.)

(Choose 2)

A) Increase the FM model’s max tokens to ensure that more retrieved context fits within the generation window and reduces missing detail issues.

B) Review and validate the chunking and preprocessing pipeline to ensure consistent boundaries, clean metadata, and proper segmentation of updated guideline text.

C) Switch to a larger embedding model without diagnostics to boost similarity scores and reduce the likelihood of retrieval mismatches.

D) Use CloudTrail logs to track which API calls were made during ingestion to identify incorrect retrieval sequences.

E) Analyze retrieved context relevance compared to the user query and evaluate embedding vectors for drift using historical similarity distributions.

---

**Q60.** A healthcare research startup is building an application that processes large clinical reports and generates AI-powered summaries. Users upload documents through an API backed by AWS Lambda. The API stores each uploaded document in an Amazon S3 bucket.

The company wants to use a pre-trained foundation model (FM) in Amazon Bedrock to summarize each report. Summaries must be written back to Amazon S3, and users will retrieve them through the same API. Users are willing to wait up to 24 hours to receive results. The workload will experience unpredictable spikes in traffic, and the solution must remain scalable, fault tolerant, and cost-efficient.

Which approach will meet these requirements in the MOST cost-effective way?

A) Use the ingestion Lambda function to invoke an AWS Step Functions workflow with multiple parallel Lambda tasks. Configure each task to call the Amazon Bedrock API and write the summary to Amazon S3 with workflow-managed retries.

B) Use the ingestion Lambda function to call the Amazon Bedrock InvokeModel API synchronously for each document upload. Return the summary directly to the user and store the result in Amazon S3.

C) Use the ingestion Lambda function to publish a message to an Amazon SQS queue. Configure another Lambda function to poll the queue, call the Amazon Bedrock InvokeModel API to summarize each document, and store the results in Amazon S3 with retries enabled.

D) Modify the ingestion Lambda function to batch uploaded documents into an Amazon SQS queue. Use a batch window to send batched requests to a custom Bedrock batch inference workflow.

---

**Q61.** A regional telemedicine provider is building a secure clinical document-processing pipeline to handle uploaded patient materials, including handwritten prescriptions, clinician summaries, and scanned referral letters. The organization uses Amazon Textract to extract text from the documents and Amazon Rekognition to blur patient faces in diagnostic images.

Before storing the processed content in Amazon S3 for downstream model training, the compliance team must automatically detect and redact both PII and PHI while preserving medically relevant details such as dosage instructions, diagnoses, allergies, and treatment recommendations. The solution must minimize manual review, support HIPAA compliance, and integrate into the existing automated workflow.

Which combination of AWS services will meet these requirements with the LEAST operational overhead? (Select TWO.)

(Choose 2)

A) Use Amazon Polly to generate spoken summaries so reviewers can identify audio-level disclosures of sensitive information.

B) Use Amazon Comprehend to detect and redact personally identifiable information (PII) from extracted clinical text.

C) Use Amazon Comprehend Medical to identify and redact protected health information (PHI) and extract clinically important entities such as conditions, medications, and procedures.

D) Use Amazon Transcribe to create audio transcripts that can be manually reviewed by compliance officers for sensitive content.

E) Use Amazon SageMaker Ground Truth to create a human-labeling workforce to annotate PII/PHI entities and manually remove sensitive content before ingestion.

---

**Q62.** A multinational logistics intelligence company operates a generative AI routing assistant on Amazon Bedrock to optimize fleet movement and provide real-time delivery guidance. During peak shipping seasons, the assistant receives unpredictable surges of inference traffic from users in South America and Southeast Asia. The company must maintain consistently low-latency responses while ensuring all inference requests remain compliant with strict regional data residency requirements.

The engineering team wants a solution that minimizes operational overhead, avoids deploying and managing separate FM instances in every region, and automatically uses available compute capacity across regions when demand spikes.

Which solution will best meet these requirements?

A) Use the Bedrock cross-region inference profile so that inference calls from one region are automatically routed to another region with available compute capacity.

B) Use SageMaker AI multi-region inference endpoints and manage routing with Amazon Route 53 latency-based rules.

C) Deploy separate Bedrock foundation model instances in each active region and route callers using a custom latency-aware client SDK.

D) Pre-copy all interaction logs and prompts to multiple regions and perform FM inference in the nearest region to the end user.

---

**Q63.** A financial analytics company uses Amazon SageMaker Studio notebooks and SageMaker Autopilot to train models on sensitive customer data stored in Amazon S3. Compliance policies require that all data transfers between SageMaker and S3 stay entirely within the AWS private network.

During an audit, the security team finds that the Studio domain is accessing S3 over public endpoints. The engineering team must update the architecture so that Studio notebooks, Autopilot jobs, and processing workloads all communicate with S3 only through private connectivity, without affecting existing workflows.

Which configuration should the team implement?

A) Enable AWS PrivateLink for S3 using an interface endpoint and update the Studio domain to route traffic privately.

B) Create a restricted public S3 Access Point that only allows requests from the SageMaker execution role.

C) Configure SageMaker Studio to run inside a private VPC and create a VPC Gateway Endpoint for S3 so all SageMaker–S3 traffic stays on the AWS private network.

D) Enable internet access for SageMaker Studio and use AWS Key Management Service (KMS) to encrypt all SageMaker–S3 transfers.

---

**Q64.** A retail technology company is using an Amazon Bedrock foundation model to generate personalized product descriptions. After a new prompt revision, the AI engineering team notices inconsistent tone, missing required attributes, and fluctuating output quality across different product categories. The team wants to troubleshoot these prompt engineering issues using a structured method that compares prompt versions, analyzes differences in model behavior, and validates improvements before deployment. The solution must avoid trial-and-error prompting and require minimal manual inspection.

Which approach will BEST help the team improve response quality and diagnose prompt issues?

A) Use a prompt testing framework that runs controlled evaluations across multiple prompt versions, compares output consistency, and measures quality changes using automated scoring to guide systematic refinement.

B) Tune the foundation model with additional product data to reduce tone variation and regenerate product descriptions from scratch.

C) Manually run the updated prompt against a small batch of example products and adjust wording until the responses look more consistent.

D) Increase the model’s temperature parameter during generation to improve creativity and reveal hidden issues in the prompt design.

---

**Q65.** A regional insurance provider is building a customer-support chatbot that uses Amazon Bedrock to answer questions based on historical communication records. The company has thousands of customer-service transcripts stored in Amazon S3. These transcripts contain sensitive PII—including policy numbers, addresses, and phone numbers—that must never appear in search results or downstream model responses. The company needs an automated and scalable solution to preprocess all records before they are indexed for retrieval. The solution must support natural language search and integrate easily with Bedrock-powered applications.

Which solution will meet these requirements with the most secure and scalable design?

A) Use Amazon Textract to extract text from transcript files and Amazon Macie to identify PII. Integrate the text output directly into Amazon OpenSearch Service for retrieval.

B) Use an Amazon Bedrock FM and a system prompt to instruct the model to avoid exposing PII at query time while performing search over the full transcripts.

C) Use Amazon Comprehend to detect and redact PII from the transcripts stored in Amazon S3. Integrate the processed data with Amazon Kendra to provide enterprise search and natural language support.

D) Use AWS Lambda to retrieve raw transcripts, manually parse them for common PII patterns with regex, and index the cleaned text into an Amazon RDS database for keyword search.

---

**Q66.** A global wealth-management firm is building an internal generative AI advisory assistant. The system uses Amazon Kendra to retrieve regulatory guidance and investment policy documents, and fine-tuned domain models running on Amazon SageMaker AI to generate tailored responses for financial advisors. Because the model interacts with highly sensitive investor information and strictly governed compliance rules, the firm must prevent the assistant from producing misleading financial advice, exposing confidential data, or being manipulated through adversarial prompts.

The solution must apply consistent safety policies across both the retrieval stage and the model-generation stage, enforce PII redaction, block investment-advice topics, and detect possible hallucinations in model output.

Which solution best satisfies these requirements?

A) Enable Amazon Kendra query filters and metadata-based access control, then allow the SageMaker model to generate output without additional safety layers.

B) Use AWS WAF to block harmful input patterns at the API level and apply IAM policies to restrict SageMaker model access during inference calls.

C) Restrict Kendra to return only regulatory documents and rely on SageMaker post-processing scripts to sanitize responses and remove sensitive information.

D) Configure Amazon Bedrock Guardrails with content filters, denied-topic rules, sensitive-information redaction, and automated reasoning checks, and apply them to both Kendra retrieval results and SageMaker model output.

---

**Q67.** A multinational logistics company operates customer support centers across Latin America, Europe, and Southeast Asia. The business needs to process support calls, field-inspection videos, and training recordings into English summaries so global teams can review incidents efficiently. The company already uses Amazon Kendra and Amazon Textract, but these do not address multilingual audio or video content.

The company needs the fastest-to-deploy solution that can convert audio/video to text, translate it into English, and generate concise summaries with a large language model—without building custom infrastructure and while scaling automatically across regions.

Which approach best meets these requirements?

A) Deploy a custom generative model in Amazon SageMaker AI that performs transcription, translation, and summarization in a single end-to-end pipeline.

B) Run all audio and video through a pre-trained embedding model in SageMaker AI, translate extracted entities with Amazon Translate, and use a Bedrock-connected Lambda function for summarization.

C) Use AWS Glue to clean the multimedia data, run translation with Amazon Translate, and generate summaries using Amazon Lex.

D) Utilize Amazon Transcribe for speech-to-text, Amazon Translate for English translation, and Amazon Bedrock with an LLM such as Jamba or Claude for summarization.

---

**Q68.** A healthcare analytics company is building a clinical query assistant using Amazon Bedrock. Clinicians need answers with extremely low latency during live patient consultations. Some requests require fast, lightweight reasoning, while others involve complex medical summaries and take longer to compute. A GenAI engineer must design the system to optimize responsiveness and control model invocation costs while keeping user experience smooth during peak clinic hours.

Which solution will MOST effectively meet these requirements?

A) Use latency-optimized Bedrock models for simple, time-sensitive queries and enable response streaming to return partial outputs immediately, while reserving higher-capability models for complex medical summaries.

B) Route every request to the most powerful available Bedrock model to minimize the chance of inaccurate responses.

C) Precompute all potential responses in advance and store them in a database to eliminate Bedrock calls during consultations.

D) Break each request into multiple sub-queries and send them in parallel to the same Bedrock model to reduce end-to-end latency.

---

**Q69.** A publishing company uses an AI assistant powered by Amazon Bedrock Knowledge Bases to answer internal research questions. The assistant retrieves context from documents stored in Amazon S3, which serves as the data source for the vector store. The company wants newly uploaded documents to be searchable within minutes and deleted documents to be removed from responses immediately. A GenAI developer must design a scalable, resilient, event-driven solution that updates the knowledge base as document changes occur in S3. The solution must minimize operational overhead and avoid polling or scheduled jobs.

Which solution will meet these requirements?

A) Configure S3 Event Notifications to publish events to an Amazon SQS queue. Use a Lambda function to poll the queue and invoke the knowledge base ingestion APIs.

B) Configure S3 Event Notifications to invoke an AWS Lambda function on object-created and object-deleted events. Configure the Lambda function to invoke IngestKnowledgeBaseDocuments for new objects and DeleteKnowledgeBaseDocuments for deleted objects.

C) Configure Amazon EventBridge Scheduler to invoke a Lambda function every 5 minutes to query S3 for changes and call IngestKnowledgeBaseDocuments and DeleteKnowledgeBaseDocuments.

D) Use Amazon EventBridge Scheduler to run a Lambda function every 5 minutes that calls StartIngestionJob to re-ingest the entire S3 bucket into the knowledge base.

---

**Q70.** A global fintech startup is migrating its proprietary fraud-scoring model to AWS. The model is under 5 GB, evaluates transactions in real time, and typically handles between 40 and 60 concurrent inference requests during peak hours. The team wants to avoid managing underlying compute infrastructure, autoscaling policies, or complex deployment pipelines.

They currently use Amazon Rekognition for image verification and Amazon Textract for document extraction, and now need a low-overhead solution to host their fraud model in the cloud. The company requires an environment that scales automatically with variable traffic while keeping operational maintenance to a minimum.

Which approach best meets these requirements?

A) Configure a SageMaker asynchronous inference endpoint to handle fraud requests and rely on batched queueing during peak traffic.

B) Create a model configuration within Amazon SageMaker AI and deploy the fraud model on a serverless SageMaker endpoint to automatically scale for real-time inference without provisioning infrastructure.

C) Deploy the fraud model on a managed EC2 instance inside an Auto Scaling group and use an Application Load Balancer to distribute inference requests across the instances.

D) Optimize the model with Amazon SageMaker Neo and deploy it on a real-time SageMaker endpoint with manual autoscaling configuration.

---

## ANSWERS

_Not yet attempted. Answer key, per-question domain tags, and domain distribution will be added after grading._
