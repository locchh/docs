# AWS Certified Generative AI Developer – Professional (AIP-C01)
## Official Practice Question Set — Study Notes

> Personal study notes captured from the AWS Skill Builder official practice
> question set. Source content © Amazon Web Services. Do not redistribute.

**Total questions:** 20

---

---

# Part 1 — Questions

## Question 1

A company is implementing AI governance policies. The policies require all FM interactions to be secured with guardrails. The company configures Amazon Bedrock guardrails. The company must ensure that all `InvokeModel` and `Converse` API calls to FMs apply the guardrails.

Which solution will enforce guardrail compliance for the API calls in the MOST operationally efficient way?

- **A.** Store guardrail identifiers in AWS Systems Manager Parameter Store. Create an AWS Lambda function that retrieves the guardrail identifier from Parameter Store each time before making calls to Amazon Bedrock FMs.
- **B.** Create an AWS Lambda function that validates and enforces guardrails before proxying requests to Amazon Bedrock. Use the Lambda function as the exclusive endpoint for all FM interactions.
- **C.** Configure IAM policies for the `InvokeModel` and `Converse` API calls with both `bedrock:GuardrailIdentifier` and `bedrock:PromptRouterArn` condition keys. Apply the policies to all IAM roles. Require prompt router validation before allowing access to Amazon Bedrock FMs.
- **D.** Configure IAM policies for the `InvokeModel` and `Converse` API calls with the `bedrock:GuardrailIdentifier` condition key. Apply the policies to all IAM roles that access the Amazon Bedrock FMs.

→ [Show answer](#answer-1)

---

## Question 2

A company is developing an AI assistant that processes customer data by using Amazon Bedrock. The AI assistant has multiple guardrails. The guardrails include prompt injection detection, sensitive information filtering, and denied topic blocking.

When a customer query is blocked, a GenAI developer needs a detailed analysis of which specific guardrail rule was invoked and why the content was flagged. Then, the GenAI developer must fine-tune guardrail configurations and distinguish between legitimate customer queries and actual security threats.

Which configuration provides the MOST detailed analysis of guardrail decision-making for content filtering?

- **A.** Configure guardrail tracing with `{"trace": "enabled"}` in `guardrailConfig`. Monitor `InvocationsIntervened` metrics filtered by the `GuardrailContentSource` dimension to identify whether input prompts or output responses triggered interventions.
- **B.** Configure guardrail tracing with `{"trace": "enabled"}` in `guardrailConfig`. Monitor `InvocationsIntervened` metrics filtered by the `GuardrailPolicyType` dimensions: `ContentPolicy`, `TopicPolicy`, and `SensitiveInformationPolicy`.
- **C.** Enable Amazon Bedrock model evaluation with automated evaluation jobs that include guardrail assessment metrics. Configure the evaluation framework to test prompt injection resistance by using company-specific test cases. Use the evaluation dashboard to analyze which guardrail policies are most effective at blocking malicious content while preserving legitimate queries.
- **D.** Enable Amazon Bedrock model invocation logging to capture full request and response data. Configure Amazon CloudWatch alarms on `InvocationsIntervened` metrics filtered by `GuardrailContentSource` dimensions. Analyze patterns by using CloudWatch Insights queries to identify which content source triggered interventions.

→ [Show answer](#answer-2)

---

## Question 3

An education company built a content generation system on Amazon Bedrock. The system generates practice questions to quiz end users on a topic to test their knowledge. The system consumes a mix of curated data and scraped data in the topic domain. Reviewers must approve of the generated question-response sets before end users can access the sets. The company wants to improve the system by adding source lineage for the reviewers to verify the credibility of the content.

Which combination of steps will meet these requirements with the LEAST operational overhead? **(Select TWO)**

- **A.** Enable Amazon Bedrock invocation logging and correlate the logs with the data source.
- **B.** Tag FM outputs with metadata from the data source.
- **C.** Use AWS CloudTrail to log reviewer feedback actions.
- **D.** Use Amazon SageMaker Clarify to explain model predictions.
- **E.** Register the curated and scraped input datasets with AWS Glue Data Catalog.

→ [Show answer](#answer-3)

---

## Question 4

A cross-functional team is developing a generative AI (GenAI) application by using AWS services. The team needs to optimize developer productivity and enforce consistent integration patterns. The team needs to automate performance tuning and accelerate AI testing across multiple business units.

The team wants to use Amazon Q Developer. The team must accelerate development workflows and maintain application quality.

Which combination of steps will meet these requirements? **(Select TWO)**

- **A.** Integrate the Amazon Q Developer automated unit and integration test generation features into the team's CI/CD pipelines.
- **B.** Configure Amazon Q Developer to automatically generate and refactor integration code snippets, provide targeted API usage guidance, and suggest performance optimizations for AI components. Apply the changes across the modular code base.
- **C.** Incorporate Amazon Q Developer to resolve coding issues that are identified during merge requests. Reserve most refactoring and optimization tasks for periodic manual review cycles.
- **D.** Use Amazon Q Developer to retrospectively analyze and document common integration patterns that are found across different business units' code bases.
- **E.** Use Amazon Q Developer to analyze code for security best practices and suggest compliance improvements. Implement a mandatory review process where all code changes must be manually approved by security teams before integration.

→ [Show answer](#answer-4)

---

## Question 5

A company is building a diagnostic imaging application. The application needs to perform similarity searches across 50 million images to assist with diagnosing and treating patients. The application must process new images daily. The application will perform similarity searches infrequently when users need to find similar cases for reference. The company wants a cost-effective solution that provides responsive search performance without requiring infrastructure management.

Which solution will meet these requirements MOST cost-effectively?

- **A.** Create an Amazon S3 vector bucket with vector indexes to store image embeddings and perform similarity searches.
- **B.** Store image vectors in Amazon RDS for PostgreSQL. Use the pgvector extension to perform similarity searches using indexed vector embeddings.
- **C.** Store image vectors in Amazon OpenSearch Serverless. Use vector search capabilities for similarity searches.
- **D.** Use Amazon DynamoDB to store image vectors. Implement custom similarity search logic by using AWS Lambda functions.

→ [Show answer](#answer-5)

---

## Question 6

A financial services company needs to use Amazon Bedrock to create an AI assistant that will help customer support representatives across multiple business units. A GenAI developer must ensure that prompt templates are properly governed through approval workflows. Additionally, the company requires comprehensive logging of all model invocations with a 7-year retention period for regulatory compliance.

Which combination of steps will meet these requirements with MINIMAL operational overhead? **(Select TWO)**

- **A.** Use Amazon Bedrock Prompt Management with multi-stage approval workflows. Use IAM policies that require multi-party authorization.
- **B.** Set up Amazon EventBridge rules to capture Amazon Bedrock model invocation events. Route events to Amazon CloudWatch Logs groups that are organized by business unit. Export the logs to Amazon S3. Enable S3 Object Lock with compliance retention mode set to 7 years.
- **C.** Enable AWS CloudTrail data events for all Amazon Bedrock APIs. Deliver the logs to CloudTrail Lake with a 7-year retention setting. Tag each event with the business unit ID. Run CloudTrail Lake queries to monitor prompt activity.
- **D.** Store prompt templates in Amazon DynamoDB tables with composite keys partitioned by business units. Implement IAM policies that grant role-based access to business units for template approval. Use DynamoDB item-level permissions to control prompt template modifications and approvals.
- **E.** Enable Amazon Bedrock model invocation logging with Amazon S3 as the destination. Enable S3 Object Lock with compliance retention mode set to 7 years. Create separate prefixes for each business unit.

→ [Show answer](#answer-6)

---

## Question 7

A company runs a question-answering application. The application uses an Amazon Bedrock knowledge base that ingests documents from multiple Amazon S3 buckets. The company needs to monitor the data ingestion process to identify and troubleshoot any issues with document processing.

Which solution will meet these requirements to monitor knowledge base operations?

- **A.** Enable AWS CloudTrail to track all API calls that relate to knowledge base operations and document ingestion activities.
- **B.** Implement Amazon Bedrock model invocation logging to capture detailed metrics about document processing and embedding generation.
- **C.** Enable Amazon CloudWatch Application Signals to automatically detect and alert on knowledge base performance issues.
- **D.** Configure knowledge base logging with Amazon CloudWatch Logs as the destination. Use CloudWatch Logs Insights to query for failed document processing.

→ [Show answer](#answer-7)

---

## Question 8

A news media company wants to develop a content conformance tool that automatically reviews and adjusts articles to ensure compliance with a style guide. Journalists need a web-based article editor that provides real-time analysis of content upon request.

When journalists click an "analyze" button, the system should immediately begin providing suggested revisions through the editor interface. Articles are tagged with content categories in the metadata. Examples of categories include news, sports, and editorial. The company wants to use an Amazon Bedrock FM to analyze content and provide immediate feedback through the web-based article editor interface.

Which architecture will meet these requirements with the LEAST operational overhead?

- **A.** Create an Amazon API Gateway REST API with AWS Lambda function URLs to enable response streaming. Configure the Lambda function to process articles and stream suggestions using chunked transfer encoding.
- **B.** Deploy an Amazon API Gateway WebSocket API linked to an AWS Lambda function. Configure the function to read the content category from metadata and route content to the appropriate Amazon Bedrock model based on the category tag. Configure the function to use Amazon Bedrock Prompt Management to enforce style guide rules. Use the Amazon Bedrock streaming API to return suggestions in real time.
- **C.** Implement an Amazon SQS queue for article ingestion. Create AWS Step Functions workflows to process content. Use AWS Lambda functions to determine the content category from metadata and invoke appropriate Amazon Bedrock models with style guide prompts. Store results in Amazon DynamoDB. Use an Amazon API Gateway WebSocket API for real-time streaming of suggestions to the journalists.
- **D.** Configure an Application Load Balancer with Amazon ECS tasks that run custom containers. Implement content category routing logic and style guide checking within the containers. Use Amazon Bedrock with streaming support to generate suggestions. Use WebSocket connections to stream results to the journalists in real time.

→ [Show answer](#answer-8)

---

## Question 9

A GenAI developer is building a virtual assistant application by using an Anthropic Claude model on Amazon Bedrock. The application sends user queries and expects conversational responses. The GenAI developer wants to configure the application to stop generating output after a specific phrase is generated in the response.

Which solution will meet these requirements?

- **A.** Add the trigger phrase "stop at this phrase" in the user prompt.
- **B.** Use the top-k parameter to control the diversity of tokens in the model's output.
- **C.** Use the temperature parameter in the inference call to control the likelihood of the phrase appearing.
- **D.** Use the stop sequences parameter in the inference call to specify a trigger phrase.

→ [Show answer](#answer-9)

---

## Question 10

A financial services company operates RAG for an application that answers user questions by using internal market analysis reports. The application uses Amazon Bedrock for the embedding model. The application uses an Amazon OpenSearch Service cluster as the vector store. An AWS Lambda function performs the embedding and search logic.

After a recent code update to the Lambda function, the application starts returning generic responses. For example, the application returns "no relevant information found" even for questions that previously returned accurate answers. Amazon CloudWatch Logs shows no errors. AWS X-Ray confirms successful FM invocation. The OpenSearch Service cluster is healthy. Query latency remains normal.

What is the cause of this issue?

- **A.** The Lambda function's IAM role is missing the permission for `bedrock:InvokeModel`.
- **B.** The Amazon Bedrock FM temperature parameter was increased.
- **C.** The updated Lambda function uses a different version of the embedding model.
- **D.** The document embeddings in OpenSearch Service were deleted during the application update and have not been re-indexed.

→ [Show answer](#answer-10)

---

## Question 11

A company is developing a RAG application by using Amazon Bedrock. The application processes customer support documents. Initially, the application retrieves many relevant documents. However, users report that the most relevant information often appears lower in the results. The company wants to improve the relevance ranking of retrieved results to ensure that the most useful information appears first.

Which combination of steps will improve the relevance of retrieved results with MINIMAL operational overhead? **(Select TWO)**

- **A.** Use Amazon SageMaker JumpStart FMs with Amazon Kendra Intelligent Ranking to create custom relevancy scoring algorithms.
- **B.** Use Knowledge Bases with hybrid search capabilities and Amazon OpenSearch Serverless to combine vector embeddings with keyword matching.
- **C.** Create an Amazon Aurora PostgreSQL database with the pgvector extension to store document embeddings. Create a similarity scoring algorithm that combines vector distances with document metadata to rank results.
- **D.** Use Amazon Bedrock reranker models with Amazon OpenSearch Service to reorder retrieved results based on semantic relevance to the query.
- **E.** Configure Amazon OpenSearch Serverless with the Amazon Bedrock Knowledge Bases plugin. Use OpenSearch's Learning to Rank feature for relevance scoring. Integrate relevance scoring with Knowledge Bases for result reranking.

→ [Show answer](#answer-11)

---

## Question 12

An ecommerce company has an application that uses Amazon Bedrock to generate product descriptions and recommendations. Currently, the application resides in a single AWS Region. When invoking a model in Amazon Bedrock during peak periods, the application receives an error. The error message says, "Too many requests, please wait before trying again."

The company must increase the throughput for invocations during peak periods without introducing additional operational overhead. The company must maintain compatibility with the existing Amazon Bedrock API. The company must use the same FM.

Which solution will meet these requirements in the MOST cost-effective way?

- **A.** Use cross-Region inference to distribute traffic across multiple Regions within a geographic area.
- **B.** Create an AWS Lambda function to invoke the model in Amazon Bedrock with the original Region as the default. Configure the Lambda function to fall back to Amazon Bedrock in a secondary Region.
- **C.** Use provisioned throughput to provision a higher level of throughput for the FM.
- **D.** Use prompt routing to distribute traffic across multiple FMs from the same family.

→ [Show answer](#answer-12)

---

## Question 13

A company uses an AI assistant to answer customer questions based on internal company documents. The company wants to include new documents in the assistant's responses as soon as possible. The company wants to exclude deleted documents from the AI assistant's responses as soon as possible.

The documents are stored in Amazon S3. The AI assistant uses Amazon Bedrock Knowledge Bases. Amazon S3 is the data source of the vector store that the company uses for RAG. A GenAI developer must create a scalable, event-driven, and resilient solution.

Which solution will meet these requirements?

- **A.** Configure Amazon EventBridge Scheduler to schedule a rule that runs every 5 minutes and invokes an AWS Lambda function. Configure the Lambda function to track changes in Amazon S3 and invoke `IngestKnowledgeBaseDocuments` for new objects and `DeleteKnowledgeBaseDocuments` for deleted objects.
- **B.** Configure Amazon EventBridge Scheduler to schedule a rule that runs every 5 minutes and invokes an AWS Lambda function. Configure the Lambda function to sync the documents in Amazon S3 with the knowledge base by invoking `StartIngestionJob`.
- **C.** Configure S3 Event Notifications to send object-created and object-deleted events to an Amazon SQS queue. Create an AWS Lambda function to poll the queue and invoke `IngestKnowledgeBaseDocuments` for new objects and `DeleteKnowledgeBaseDocuments` for deleted objects.
- **D.** Configure S3 Event Notifications to invoke an AWS Lambda function on object-created and object-deleted events. Configure the Lambda function to invoke `IngestKnowledgeBaseDocuments` for new objects and `DeleteKnowledgeBaseDocuments` for deleted objects.

→ [Show answer](#answer-13)

---

## Question 14

A financial services company wants to develop a mobile app that will help users with account inquiries and general account information. The company has a large amount of email exchange data between customers and support staff to use as source material. The data is stored in an Amazon S3 bucket and contains personally identifiable information (PII) that should not appear in search results.

Which solution will meet these requirements?

- **A.** Use Amazon Comprehend to detect and redact PII from the email data that is stored in Amazon S3. Integrate Amazon Comprehend with Amazon Kendra to enable enterprise search of the processed data.
- **B.** Use Amazon Kendra to enable enterprise search of the email data that is stored in Amazon S3. Integrate Amazon Kendra with an Amazon Bedrock FM. Use a system prompt to identify and remove PII during query processing.
- **C.** Use Amazon Comprehend to detect and redact PII from the email data that is stored in Amazon S3. Integrate Amazon Comprehend with Amazon DocumentDB to enable database queries for enterprise search.
- **D.** Use Amazon Textract to extract text from the email data. Use Amazon Macie to scan for PII in Amazon S3. Integrate Amazon Textract and Amazon S3 with Amazon Kendra to enable enterprise search of the processed data.

→ [Show answer](#answer-14)

---

## Question 15

A financial services company is developing a research agent that processes complex financial data queries. The company must deploy existing Python agent code to Amazon Bedrock AgentCore Runtime. The company wants to reduce infrastructure management overhead and operational complexity.

The agent must be able to handle quick data lookups that require sub-second responses. The agent must be able to handle comprehensive research report generation. For example, streaming responses over several minutes. The solution must automatically manage HTTP server configuration, endpoint routing, and health monitoring.

Which deployment approaches will meet these requirements with MINIMAL operational overhead? **(Select TWO)**

- **A.** Deploy the agent on Amazon ECS on AWS Fargate by using a custom container image that runs the AgentCore SDK application.
- **B.** Deploy the agent on Amazon SageMaker AI real-time endpoints by using a custom inference container.
- **C.** Implement the AgentCore SDK with the `@app.entrypoint` decorator to automatically handle server setup and endpoint management.
- **D.** Deploy the agent by using the AgentCore starter toolkit for automated packaging, containerization, and deployment workflows.
- **E.** Implement a FastAPI server with a configuration of `/invocations` and `/ping` endpoints and container orchestration.

→ [Show answer](#answer-15)

---

## Question 16

A company wants to create an application to analyze fashion trends. The application must analyze videos and photos from public fashion shows to understand style elements and trends. The solution must store the extracted information and provide a dashboard that summarizes the fashion trends.

Which solution will meet these requirements with the LEAST operational overhead?

- **A.** Use Amazon EventBridge to trigger AWS Lambda functions that use Amazon Quick Suite to analyze videos and photos from fashion shows. Store analysis results in Amazon S3. Deploy an Amazon Quick Sight dashboard with ML-powered trend analysis.
- **B.** Use Amazon Rekognition Custom Labels to train a custom model for fashion trend analysis. Store results in Amazon DynamoDB. Create a dashboard using Amazon Managed Grafana with custom plugins for fashion trend analytics.
- **C.** Use AWS Step Functions to process videos and photos from fashion shows by using Amazon Bedrock multimodal FMs. Store analysis results in Amazon S3. Use an Amazon Quick Sight dashboard to visualize trends in the data.
- **D.** Use an Anthropic Claude model in Amazon Bedrock to analyze text descriptions from fashion show videos and photos. Use Stable Diffusion for image analysis. Store results in Amazon OpenSearch Service. Create a dashboard by using Amazon Managed Grafana with OpenSearch visualizations.

→ [Show answer](#answer-16)

---

## Question 17

*Ordering question.*

A company is implementing a systematic evaluation process for a newly deployed FM in Amazon Bedrock. The company wants to replace an existing model in production with a new model. The change to the new model is dependent on the new model demonstrating better performance than the existing model. The company must follow a sequential validation process. To ensure evaluation rigor, each step must be reviewed and approved before proceeding to the next step.

Select and order each step from the following list to implement the evaluation workflow. Select each step one time.

Steps to order:

- Conduct A/B testing to compare the new model against the existing production model.
- Create a test dataset with diverse scenarios and edge cases.
- Define evaluation metrics for relevance, factual accuracy, and fluency.
- Implement automated quality gates by using AWS Step Functions.
- Analyze the results and generate a comprehensive evaluation report.

→ [Show answer](#answer-17)

---

## Question 18

A GenAI developer deployed a fine-tuned LLM to an Amazon SageMaker AI endpoint. The GenAI developer used the default serving configuration for continuous batching with the AMI including the Deep Java Library (DJL). The model is being served on GPU-based Amazon EC2 instances, each with 8 GPUs. As the model scales to production, the GenAI developer discovers that many instances are needed to meet traffic demands. The GenAI developer wants to avoid increased costs from the overutilization.

The GenAI developer analyzes logs. The GenAI developer discovers that the maximum I/O sequence length in real requests is 10 times smaller than what the model was originally configured to handle. Additionally, the current concurrency for each instance is low. Profiling shows that the model's weights and activations can fit entirely within 4 GPUs.

Which combination of steps can the GenAI developer take to improve resource utilization? **(Select TWO)**

- **A.** Split the model across all 8 GPUs by using a tensor parallelism degree of 8 to improve memory efficiency.
- **B.** Enable speculative decoding to reduce response latency for each request.
- **C.** Use tensor parallelism with a degree of 4 to deploy two model replicas for each instance.
- **D.** Reduce the model's maximum sequence length to provide a higher rolling batch size for each GPU.
- **E.** Increase the number of SageMaker AI instances and spread requests more evenly to reduce the load for each instance.

→ [Show answer](#answer-18)

---

## Question 19

A GenAI developer is implementing a solution to create images from text descriptions. The GenAI developer successfully tested a pre-trained Hugging Face model by using Amazon SageMaker JumpStart. Now, the GenAI developer needs to deploy the model so that users can generate images on demand.

The solution must use GPUs for inference. The solution must be able to handle text datasets up to 50 MB with image descriptions. The solution requires responses within 15 minutes.

Which deployment strategy will meet these requirements?

- **A.** Deploy a SageMaker Real-Time Inference endpoint that uses an accelerated computing SageMaker AI instance type. Create an AWS Lambda function for on-demand invocation of the SageMaker AI endpoint to manage image generation.
- **B.** Deploy a SageMaker Serverless Inference endpoint that uses a general purpose SageMaker AI instance type. Create an AWS Lambda function for on-demand invocation of the SageMaker AI endpoint to manage image generation.
- **C.** Deploy a SageMaker Asynchronous Inference endpoint that uses an accelerated computing SageMaker AI instance type. Create an AWS Lambda function for on-demand invocation of the SageMaker AI endpoint to manage image generation.
- **D.** Create a SageMaker AI batch transform job that uses an accelerated computing SageMaker AI instance type to manage image generation. Create an AWS Lambda function to start the batch transform job.

→ [Show answer](#answer-19)

---

## Question 20

A company needs secure authentication for a third-party application that uses Amazon Bedrock. The solution must integrate with the company's existing identity provider (IdP). The solution must maintain comprehensive audit logs of authentication and API calls. The solution must eliminate long-lived credentials and provide temporary access to Amazon Bedrock.

Which solutions will meet these requirements? **(Select TWO)**

- **A.** Implement an OpenID Connect (OIDC) integration with Amazon Cognito. Configure the integration to authenticate users through the IdP and exchange tokens for temporary AWS credentials. Configure the integration to allow the application to access Amazon Bedrock.
- **B.** Create IAM users for each employee that needs access to the application. Assign permissions through IAM policies. Implement credential rotation by using AWS Secrets Manager.
- **C.** Configure an Amazon API Gateway Lambda authorizer. Configure the authorizer to validate credentials against the company's LDAP server and then issue signed JSON Web Tokens (JWTs) for Amazon Bedrock access.
- **D.** Create an IAM role and configure federation by using AWS STS `AssumeRole` API calls. Store the application's IAM user credentials in the application configuration.
- **E.** Deploy AWS IAM Identity Center with SAML federation to the IdP. Configure custom permission sets that grant access to Amazon Bedrock.

→ [Show answer](#answer-20)


---

# Part 2 — Answers and explanations

## Answer 1

**Correct answer: D**

**Why D is correct**

This solution uses IAM policies with the `bedrock:GuardrailIdentifier` condition key to enforce guardrail compliance for `InvokeModel` and `Converse` API calls. IAM policies are a centralized and efficient way to control access to AWS resources. You can apply the policies to roles that access Amazon Bedrock FMs. This solution ensures that guardrails are consistently applied across all relevant API calls in the most operationally efficient way.

**Why the others are incorrect**

- **A.** Parameter Store provides a centralized location to store guardrail identifiers. However, using a Lambda function to retrieve the identifier for each API call adds additional operational overhead and latency. You must create and maintain the Lambda function. This solution requires the retrieval of the guardrail identifier each time before making a call to the model.
- **B.** Creating a Lambda function to proxy and validate all requests introduces an additional point of failure and a potential performance bottleneck. You must maintain custom code for guardrail enforcement. Therefore, this solution is less operationally efficient and more error-prone than using built-in capabilities.
- **C.** The `PromptRouterArn` condition key is designed to filter access by the specified prompt router. The prompt router manages prompt templates and configurations. This condition key is unrelated to guardrail enforcement. Using both conditions creates more complex IAM policies to maintain without providing additional security benefits.

**Read more**

- [Guardrail enforcement during inference](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions-id.html)
- [Using IAM policies with Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_service-with-iam.html)
- [Amazon Bedrock condition keys](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonbedrock.html#amazonbedrock-bedrock_PromptRouterArn)
- [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [Amazon API Gateway Lambda authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)

<sub>[↑ back to question 1](#question-1)</sub>

---

## Answer 2

**Correct answer: B**

**Why B is correct**

`GuardrailPolicyType` provides detailed information on which policy intervened in the guardrail. The GenAI developer can use this configuration to make an informed decision based on specific metrics.

**Why the others are incorrect**

- **A.** The `GuardrailContentSource` dimension can distinguish between input and output. However, this dimension does not indicate the layer of the guardrail that intervened.
- **C.** Amazon Bedrock model evaluation provides analysis based on measurable tests. Model evaluation can create a report about correctness, toxicity, accuracy, and other parameters during evaluation. However, you would not use Amazon Bedrock model evaluation during inference.
- **D.** Amazon Bedrock model invocation logging can log the input, output, and metadata of invocations. However, model invocation logging does not provide details about guardrail interventions.

**Read more**

- [CloudWatch metrics to monitor Amazon Bedrock guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-guardrails-cw-metrics.html)
- [The Converse API and setting up guardrailConfig](https://docs.aws.amazon.com/cli/latest/reference/bedrock-runtime/converse.html)
- [Converse and guardrailConfig (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html)
- [Amazon Bedrock model evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html)
- [How to monitor model invocations](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html)

<sub>[↑ back to question 2](#question-2)</sub>

---

## Answer 3

**Correct answers: B and E**

**Why B is correct**

You can tag the outputs with metadata about the data sources. The generated questions are the outputs. The curated data and scraped data are the data sources. This step provides direct traceability between generated content and the content's origins. This step provides reviewers with immediate access to source information. This step helps reviewers verify credibility in an operationally efficient way. This step is a direct and automated way to track sources. This step injects metadata during processing and attaches the metadata to the output.

**Why E is correct**

You can register input datasets by using Data Catalog to create a searchable inventory of data sources. Reviewers can use this step to verify the origin and credibility of source material. This step uses the built-in features of a managed service. Therefore, this step provides structured metadata management with minimal operational overhead.

**Why the others are incorrect**

- **A.** Amazon Bedrock invocation logging can track model interactions. However, correlating logs with data sources would require additional operational overhead. You must manually correlate logs with data sources, or you must build an automated method. This step would capture usage data. However, this step would not help reviewers verify content credibility.
- **C.** CloudTrail logs AWS API calls. API calls can track actions that are taken by reviewers, such as approval or rejection. However, this step does not meet the requirement to verify the source lineage of the generated content. Using CloudTrail to log reviewer feedback actions focuses on tracking reviewer activity rather than providing source lineage information.
- **D.** SageMaker Clarify is designed for model explainability and bias detection. Clarify is not designed to track source lineage. This step does not meet the requirement for source credibility verification.

**Read more**

- [Knowledge base metadata attributes](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-metadata.html)
- [AWS Glue Data Catalog](https://docs.aws.amazon.com/prescriptive-guidance/latest/serverless-etl-aws-glue/aws-glue-data-catalog.html)
- [How to log Amazon Bedrock model invocations](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html)
- [AWS CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)
- [Amazon SageMaker Clarify](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-processing-job-run.html)

<sub>[↑ back to question 3](#question-3)</sub>

---

## Answer 4

**Correct answers: A and B**

**Why A is correct**

By embedding Amazon Q Developer automated test generation into CI/CD workflows, the team continuously validates both new and existing AI components. This step ensures high velocity, ongoing code quality, and early defect detection. These qualities are critical in large-scale ML deployments.

**Why B is correct**

Amazon Q Developer provides automatic code generation, refactoring, targeted API recommendations, and performance optimization. Comprehensive use of these features can increase productivity and reduce integration errors across business units.

**Why the others are incorrect**

- **C.** This step uses Amazon Q Developer primarily at merge or review stages. This step reserves most code improvements for infrequent manual cycles. Therefore, this step does not optimize the core benefits of Amazon Q Developer. This step can slow down the resolution of code quality and integration issues.
- **D.** Using Amazon Q Developer for retrospective analysis and documentation of patterns does not meet the requirements to optimize developer productivity and accelerate development workflows. This reactive approach fails to use the tool's real-time assistance capabilities for code generation, refactoring, and testing.
- **E.** Amazon Q Developer can help identify security issues and suggest improvements. However, implementing a mandatory manual approval process for all code changes would create a bottleneck. This approach does not meet the requirements to optimize developer productivity and accelerate development workflows. This approach does not automate performance tuning or accelerate AI testing. This approach could slow down integration across business units.

**Read more**

- [Generate unit tests by using Amazon Q Developer](https://aws.amazon.com/q/developer/features/#test-and-secure)
- [Amazon Q Developer features](https://aws.amazon.com/q/developer/features/)
- [Best practices for code generation in Amazon Q Developer](https://docs.aws.amazon.com/prescriptive-guidance/latest/best-practices-code-generation/code-generation.html)
- [How to review code in Amazon Q Developer](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/code-reviews.html)

<sub>[↑ back to question 4](#question-4)</sub>

---

## Answer 5

**Correct answer: A**

**Why A is correct**

S3 Vectors is a fully managed, serverless feature of Amazon S3 that provides scalable vector search capabilities. S3 Vectors can store and search vector data. S3 Vectors can support up to billions of vectors. This solution is suitable for workloads with infrequent searches. You need to pay for only what you use. You do not need to provision infrastructure. Therefore, this solution is cost-effective for storing 50 million image vectors. S3 Vectors automatically optimizes vector data for low-cost performance as datasets scale.

**Why the others are incorrect**

- **B.** RDS for PostgreSQL supports the pgvector extension. The pgvector extension provides similarity search on vector embeddings by using SQL queries. This approach is useful for hybrid workloads when you need to combine metadata and vectors. However, Amazon RDS requires you to provision and manage database instances. Therefore, this solution does not meet the requirement to avoid infrastructure management. Additionally, this solution is not cost-effective for infrequent workloads. You must pay for provisioned capacity that remains underutilized.
- **C.** OpenSearch Serverless is optimized for high-throughput, low-latency workloads with frequent searches. OpenSearch Service supports vector similarity search through k-nearest neighbors (k-NN) indexes. However, OpenSearch Service is less cost-effective because of compute unit processing. The company performs similarity searches infrequently. Therefore, the company would pay for provisioned capacity that remains underutilized. This solution would not be the most cost-effective.
- **D.** DynamoDB is a scalable NoSQL database that is optimized for key-value and document access patterns. DynamoDB does not provide built-in support for vector similarity search. You would need to integrate DynamoDB with a vector search engine such as OpenSearch Service. Then, you would need to enable similarity search for the data that you store in DynamoDB. Implementing custom similarity search logic by using Lambda functions would introduce latency and add compute costs.

**Read more**

- [S3 Vectors for similarity searches](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html)
- [Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html)
- [OpenSearch Serverless pricing](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-overview.html#serverless-pricing)
- [DynamoDB use cases](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)

<sub>[↑ back to question 5](#question-5)</sub>

---

## Answer 6

**Correct answers: A and E**

**Why A is correct**

You can use Amazon Bedrock Prompt Management to securely create, parameterize, version, and approve prompt templates within the Amazon Bedrock managed environment. This solution provides multi-stage approvals, access roles, version control, and collaboration features that are suitable for diverse business units and complex governance requirements.

**Why E is correct**

Amazon Bedrock provides a built-in model invocation logging feature. You can enable Amazon Bedrock model invocation logging with Amazon S3 as the destination. This approach provides comprehensive logging with minimal setup. S3 Object Lock in compliance mode provides immutable storage that enforces the 7-year retention period for regulatory compliance. This approach ensures that you cannot delete logs before the retention period expires. This approach provides built-in business unit segregation through S3 prefixes. Therefore, this solution requires minimal operational overhead.

**Why the others are incorrect**

- **B.** You can use EventBridge rules to capture and route events. However, this approach requires more operational overhead and creates potential points of failure. This approach requires custom configuration and maintenance of rules. This approach does not provide the comprehensive audit trail that you need for regulatory compliance.
- **C.** CloudTrail Lake provides logging capabilities. However, CloudTrail captures only API metadata. For example, CloudTrail captures who called `bedrock:InvokeModel` and when. CloudTrail does not capture the actual prompt content and model responses that you need for regulatory reconstruction.
- **D.** DynamoDB is a NoSQL database that can store prompt templates. However, this approach requires custom development for approval workflows and access control. Building and maintaining custom solutions for template management increases operational overhead.

**Read more**

- [Amazon Bedrock Prompt Management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html)
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html)
- [Amazon EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html)
- [Monitor Amazon Bedrock API calls by using CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html)
- [Amazon DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)

<sub>[↑ back to question 6](#question-6)</sub>

---

## Answer 7

**Correct answer: D**

**Why D is correct**

Amazon Bedrock knowledge bases support a built-in logging system that you can configure to send logs to CloudWatch Logs. The logs track the status of files during data ingestion jobs. The jobs show whether the files were successfully ingested, ignored, or failed. You can use CloudWatch Logs Insights to create queries that help identify specific issues. For example, you can query for documents that have the status `RESOURCE_IGNORED`, `EMBEDDING_FAILED`, or `INDEXING_FAILED`.

**Why the others are incorrect**

- **A.** CloudTrail can track API calls that are made to Amazon Bedrock. However, CloudTrail does not provide the detailed document-level processing information that you need to troubleshoot ingestion issues. CloudTrail focuses on API activity auditing rather than the status of individual documents being processed.
- **B.** Amazon Bedrock model invocation logging captures information about model API calls and inference requests. Model invocation logging does not capture knowledge base document ingestion processes. The logging in this solution would help monitor model usage patterns. However, this solution would not provide visibility into document processing failures during knowledge base creation.
- **C.** CloudWatch Application Signals is designed to monitor the performance and health of applications, not knowledge bases. CloudWatch Application Signals does not integrate with Amazon Bedrock knowledge base monitoring. You can use CloudWatch for monitoring. However, CloudWatch Application Signals is not the appropriate feature for the knowledge base ingestion monitoring in this scenario.

**Read more**

- [How to monitor knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-bases-logging.html)
- [Monitor Amazon Bedrock API calls by using CloudTrail](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html)
- [How to monitor invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html)
- [CloudWatch Application Signals](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Monitoring-Sections.html)

<sub>[↑ back to question 7](#question-7)</sub>

---

## Answer 8

**Correct answer: B**

**Why B is correct**

This architecture uses managed services to minimize operational overhead. An API Gateway WebSocket API provides real-time, bidirectional communication. Therefore, this solution is suitable for streaming suggestions in the web-based article editor interface. The Lambda function efficiently reads metadata tags for routing. Amazon Bedrock Prompt Management provides a managed way to implement and maintain style guide rules across different content types. The Amazon Bedrock streaming API capability provides immediate delivery of suggestions when journalists click the "analyze" button. Therefore, this architecture creates a responsive editing experience. This architecture requires minimal infrastructure management and meets the requirements for real-time content analysis and feedback.

**Why the others are incorrect**

- **A.** Lambda function URLs with chunked transfer encoding through API Gateway would not provide real-time streaming to the web-based article editor interface. API Gateway has dataset size limits and would not provide the immediate, responsive experience that you need. REST APIs are not suitable for the long-lived connections that you need for real-time streaming. This architecture could lead to connection timeouts and a poor user experience.
- **C.** Amazon SQS and Lambda provide reliable processing capabilities. Amazon SQS is a queuing service where messages must be polled for processing. Therefore, this architecture does not meet the requirement for immediate feedback through the web-based article editor interface. This queuing and polling approach introduces additional latency. This architecture does not provide real-time feedback when journalists click the "analyze" button.
- **D.** To run custom containers on Amazon ECS, you must manage container infrastructure, scaling, and deployment. Implementing content routing and style guide checking within containers creates additional development and maintenance overhead. This architecture does not use managed services effectively. This approach requires more operational effort than using serverless alternatives.

**Read more**

- [API Gateway WebSocket APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html)
- [Invoke an Amazon Bedrock model with response streaming](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-invoke.html)
- [Lambda function URLs](https://docs.aws.amazon.com/lambda/latest/dg/urls-configuration.html)
- [Lambda streaming responses](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html)
- [Amazon ECS containers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-container-image.html)

<sub>[↑ back to question 8](#question-8)</sub>

---

## Answer 9

**Correct answer: D**

**Why D is correct**

You can use the stop sequences parameter to stop the model from generating a response. You can use the stop sequences parameter to stop the model after generating certain key phrases. This solution provides a built-in mechanism in the model's API to directly control output generation.

**Why the others are incorrect**

- **A.** Amazon Bedrock processes prompts and generates completions based on the input and the model parameters. Adding a "stop at this phrase" instruction in the prompt relies on the model following instructions. However, the model might not follow instructions. This solution does not reliably control output termination.
- **B.** The top-k parameter controls token sampling diversity during generation. This parameter could affect the likelihood of certain tokens being selected. However, this parameter cannot stop generation at specific phrases.
- **C.** This parameter value controls the randomness of the model's output. Adjusting temperature influences creativity and variation. Temperature does not influence the stopping point of output generation. This solution does not reliably control output termination.

**Read more**

- [The stop sequences parameter (Anthropic Claude Messages API)](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-request-response.html)
- [Inference parameters — randomness and diversity (top-k)](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-parameters.html#inference-randomness)
- [Designing prompts](https://docs.aws.amazon.com/bedrock/latest/userguide/design-a-prompt.html)

<sub>[↑ back to question 9](#question-9)</sub>

---

## Answer 10

**Correct answer: C**

**Why C is correct**

Embedding drift occurs when query embeddings are generated with a different model than the model used to index documents. This issue causes a mismatch in vector space and makes retrieval ineffective. In this scenario, the update to the Lambda function likely introduced a new embedding model version or configuration.

**Why the others are incorrect**

- **A.** The scenario states that the model is being invoked successfully. If the IAM permission were missing, then the Lambda function would throw an access error and fail before generating a response.
- **B.** A high temperature setting can degrade the quality of generation. However, a high temperature setting would not prevent the model from finding relevant context. The reported issue relates to a retrieval failure, not generation randomness.
- **D.** If the embeddings had been deleted, the issue would appear in logs or cause failed OpenSearch queries. The scenario states that there are no errors or unusual query latency. Therefore, the documents are still being retrieved.

**Read more**

- [Embeddings in machine learning](https://aws.amazon.com/what-is/embeddings-in-machine-learning/)
- [Embedding drift — lessons from building real-world RAGs](https://aws.amazon.com/blogs/machine-learning/from-rag-to-fabric-lessons-learned-from-building-real-world-rags-at-genaiic-part-1/)
- [Amazon Bedrock and IAM](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)
- [Amazon Bedrock generation parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html)
- [OpenSearch Service vector search and embeddings](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector-search.html)

<sub>[↑ back to question 10](#question-10)</sub>

---

## Answer 11

**Correct answers: B and D**

**Why B is correct**

Knowledge Bases with hybrid search capabilities combines vector embeddings for semantic understanding with traditional keyword matching. This step improves retrieval relevance. You can use OpenSearch Serverless as the vector store. This step enhances the quality of retrieved results by using semantic similarity and exact keyword matches to find the most relevant documents.

**Why D is correct**

Amazon Bedrock reranker models are specifically designed to improve the relevance of retrieved results. The reranker models calculate relevance scores between queries and documents. Then, the reranker models reorder the results based on the scores. You can perform this step with the OpenSearch Service reordering step to enhance retrieval relevance in RAG applications. This combination of steps ensures that the most relevant information appears first in search results.

**Why the others are incorrect**

- **A.** SageMaker JumpStart provides access to FMs. Amazon Kendra Intelligent Ranking can improve search results. However, Amazon Bedrock already provides built-in reranking capabilities that are optimized for FM integration. Therefore, this approach is more complex and less integrated with the existing Amazon Bedrock environment.
- **C.** Aurora with the pgvector extension supports vector operations. However, this approach requires custom development to implement a similarity scoring algorithm and maintain the vector database. You must manage document embeddings and metadata in Aurora. You must implement ranking logic. Therefore, this approach requires more operational overhead than using the built-in features of Amazon Bedrock.
- **E.** OpenSearch Service provides vector search capabilities. Learning to Rank is an open source plugin that you can use to tune the relevance of documents. For this approach, you must create custom relevance scoring. You must train and maintain custom models. Therefore, this approach requires more operational overhead than using the built-in features of Amazon Bedrock.

**Read more**

- [Improve relevance with reranker models in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html)
- [Knowledge base vector search configurations](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_KnowledgeBaseVectorSearchConfiguration.html)
- [Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)
- [Amazon OpenSearch Service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html)
- [SageMaker JumpStart FMs](https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-foundation-models.html)
- [Amazon Kendra Intelligent Ranking](https://docs.aws.amazon.com/kendra/latest/dg/intelligent-rerank.html)
- [Use the pgvector extension with Aurora PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.VectorDB.html)
- [OpenSearch Learning to Rank](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/learning-to-rank.html)

<sub>[↑ back to question 11](#question-11)</sub>

---

## Answer 12

**Correct answer: A**

**Why A is correct**

Cross-Region inference automatically distributes traffic across multiple Regions within your geographic area to process your inference request.

**Why the others are incorrect**

- **B.** You can create a Lambda function to invoke an Amazon Bedrock model. The Lambda function is an intermediary that you must manage and maintain. Therefore, this solution increases cost and operational overhead compared to using a built-in feature of Amazon Bedrock.
- **C.** Provisioned throughput will provide higher throughput for the number of I/O rates that a model can process. However, the application needs a solution for peak periods, not for consistent usage.
- **D.** Amazon Bedrock intelligent prompt routing provides a single endpoint to efficiently route requests between different FMs within the same model family. This solution requires at least two different models from the same family. The models cannot be exactly the same. However, the company in the scenario must use the same FM.

**Read more**

- [Cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)
- [Provisioned throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)
- [Intelligent prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html)

<sub>[↑ back to question 12](#question-12)</sub>

---

## Answer 13

**Correct answer: C**

**Why C is correct**

This solution provides a scalable and resilient architecture to meet the requirements. You can use Amazon SQS as a buffer between S3 events and Lambda processing. The queue handles traffic spikes, provides automatic retries, and ensures that no updates are missed. This event-driven approach meets the requirements and maintains system reliability under varying loads.

**Why the others are incorrect**

- **A.** EventBridge Scheduler provides time-based actions for different AWS services. Running the sync action every 5 minutes is not suitable for near real-time updates to the knowledge base. This solution introduces delays in including new documents in the knowledge base. Additionally, tracking changes to the documents in Amazon S3 within the Lambda function is not operationally efficient. The Lambda function would need to maintain some form of change tracking to identify which documents have been added or deleted.
- **B.** EventBridge Scheduler provides time-based actions for different AWS services. Syncing every 5 minutes is inefficient and causes unnecessary scanning. This solution can introduce delays. This solution cannot support the immediacy required for near real-time updates. This solution is not an event-driven architecture.
- **D.** You can use S3 Event Notifications to send notifications when an event occurs in an S3 bucket. This solution does not provide buffering and retry support. Amazon S3 directly invoking Lambda can fail under high load because of synchronous invocation limits.

**Read more**

- [Ingest changes directly into a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-direct-ingestion.html)
- [How to sync a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html)
- [Amazon EventBridge Scheduler](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html)
- [Amazon S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html)

<sub>[↑ back to question 13](#question-13)</sub>

---

## Answer 14

**Correct answer: A**

**Why A is correct**

Amazon Comprehend detects and redacts sensitive information from text data in Amazon S3. Amazon Kendra provides a managed enterprise search of the processed data for conversational AI integration.

**Why the others are incorrect**

- **B.** Amazon Kendra provides enterprise search capabilities and can integrate with Amazon Bedrock FMs. However, using system prompts to handle PII during query processing is not a reliable or secure approach for sensitive financial data. A system prompt cannot ensure the consistent identification and removal of PII. A system prompt risks potential exposure of sensitive information. Additionally, prompts can be circumvented or jailbroken. Therefore, this solution is not suitable to protect sensitive financial data. This solution lacks the systematic and secure PII detection and redaction capabilities that you need for financial services applications.
- **C.** Amazon Comprehend provides PII detection and redaction capabilities. However, using Amazon DocumentDB for enterprise search requires custom development for search indexing and querying. This solution lacks the natural language processing capabilities that you need for user interactions in a mobile app. Users would need to construct specific database queries rather than using natural language. Therefore, this solution is not suitable for a customer-facing financial services application. Additionally, Amazon DocumentDB is not designed for enterprise search scenarios.
- **D.** Amazon Textract can extract text from documents. Macie can detect sensitive data in S3 buckets. However, this solution is not the most suitable for processing email data. Macie is designed for data discovery and security assessment, not for the redaction of PII in preparation for GenAI applications. Additionally, Amazon Textract is optimized for scanned documents, not raw email text.

**Read more**

- [Amazon Comprehend PII detection](https://docs.aws.amazon.com/comprehend/latest/dg/how-pii.html)
- [Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/what-is-kendra.html)
- [Amazon Comprehend](https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html)
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [Amazon DocumentDB](https://docs.aws.amazon.com/documentdb/latest/developerguide/what-is.html)
- [Querying in Amazon DocumentDB](https://docs.aws.amazon.com/documentdb/latest/developerguide/querying.html)
- [Amazon Textract](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)
- [PII discovery in Amazon Macie](https://docs.aws.amazon.com/macie/latest/user/data-classification.html)

<sub>[↑ back to question 14](#question-14)</sub>

---

## Answer 15

**Correct answers: C and D**

**Why C is correct**

The AgentCore SDK with the `@app.entrypoint` decorator provides minimal operational overhead. This approach automatically creates an HTTP server on port 8080 and implements the required `/invocations` and `/ping` endpoints. This approach handles proper content types and response formats. This approach supports both JSON responses for quick lookups and streaming responses for long-running report generation. This approach does not require manual server configuration or endpoint management.

**Why D is correct**

The AgentCore starter toolkit provides automated packaging, containerization, and deployment workflows. This approach requires minimal operational overhead. This approach automatically generates container images based on provided Dockerfiles. This approach automatically handles ARM64 container builds and manages ECR repository creation and image pushing. This approach automatically deploys agents by using the `CreateAgentRuntime` operation. This approach is specifically designed for users that want to focus on agent logic rather than infrastructure management.

**Why the others are incorrect**

- **A.** Running the agent on ECS on Fargate with a custom container image increases operational overhead. You must build and maintain Dockerfiles, manage container images, and define task definitions. Fargate eliminates the need to manage servers. However, this deployment approach still requires container configuration and does not provide automatic HTTP server setup and health monitoring.
- **B.** You can deploy the Python agent on a SageMaker AI real-time endpoint by using a custom inference container. This approach can host a long-running workload. However, this approach increases operational overhead for infrastructure management. You must build and maintain Docker images. You must configure an inference server and set up auto scaling policies. You must monitor container health and manage deployment workflows.
- **E.** A FastAPI server can meet the technical requirements for AgentCore Runtime. However, a FastAPI server requires manual configuration. You must implement `/invocations` and `/ping` endpoints. You must handle JSON and streaming responses. You must create Dockerfiles and manage container builds. You must orchestrate deployment processes. Therefore, this approach increases operational overhead.

**Read more**

- [AgentCore Runtime — getting started with the starter toolkit](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-starter-toolkit.html)
- [Create an AgentCore Runtime agent without the starter toolkit](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-custom.html)
- [Amazon ECS on AWS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [SageMaker custom inference containers](https://docs.aws.amazon.com/sagemaker/latest/dg/adapt-inference-container.html)

<sub>[↑ back to question 15](#question-15)</sub>

---

## Answer 16

**Correct answer: C**

**Why C is correct**

Amazon Bedrock supports multimodal FMs including Amazon Nova Pro and Claude Sonnet. Multimodal FMs can directly analyze videos and photos from fashion shows. Multimodal FMs can extract style elements and fashion trend information without custom model development. Step Functions provides a managed way to coordinate the analysis workflow. You can use Quick Sight to build and deploy dashboards without managing any servers or infrastructure. Therefore, this solution requires the least operational overhead.

**Why the others are incorrect**

- **A.** You can use Quick Suite to create topics and ask questions about a specific topic inside a Quick Sight dashboard. Quick Suite helps users ask questions about data that is already located within a Quick Sight dashboard. However, Quick Suite cannot perform the required analysis of videos and photos from fashion shows.
- **B.** This solution requires additional operational overhead. This solution requires custom model development and ongoing maintenance. You must continuously train and update the custom labels model to keep up with changing fashion trends. Additionally, developing and maintaining custom plugins for Grafana requires dedicated development resources.
- **D.** This solution requires additional operational overhead. You must manage an OpenSearch cluster and coordinate multiple FMs. Managing and scaling OpenSearch clusters requires ongoing operational overhead. The integration between the Claude and Stable Diffusion FMs would require custom development and maintenance. Additionally, you must create custom visualizations for OpenSearch. This solution requires cluster management, model coordination, and custom visualization development. Additionally, the requirement is to directly analyze the visual content of videos and photos, not textual descriptions.

**Read more**

- [Step Functions and Amazon Bedrock](https://docs.aws.amazon.com/step-functions/latest/dg/connect-bedrock.html)
- [Amazon Quick Sight](https://docs.aws.amazon.com/quicksuite/latest/userguide/quick-bi.html)
- [Amazon Quick Suite terminology](https://docs.aws.amazon.com/quicksuite/latest/userguide/quicksight-terminology.html)
- [Quick Sight ML capabilities](https://docs.aws.amazon.com/quicksuite/latest/userguide/making-data-driven-decisions-with-ml-in-quicksight.html)
- [EventBridge and Lambda](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-run-lambda-schedule.html)
- [Amazon Rekognition Custom Labels](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/what-is.html)
- [Grafana plugins](https://docs.aws.amazon.com/grafana/latest/userguide/grafana-plugins.html)
- [Amazon OpenSearch Service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html)
- [Amazon Managed Grafana and OpenSearch](https://docs.aws.amazon.com/grafana/latest/userguide/using-opensearch-in-AMG.html)

<sub>[↑ back to question 16](#question-16)</sub>

---

## Answer 17

**Correct order**

1. Define evaluation metrics for relevance, factual accuracy, and fluency.
2. Create a test dataset with diverse scenarios and edge cases.
3. Conduct A/B testing to compare the new model against the existing production model.
4. Implement automated quality gates by using AWS Step Functions.
5. Analyze the results and generate a comprehensive evaluation report.

**Explanation**

Sequential validation and approval provides a rigorous evaluation process where each step builds upon validated components of the previous steps. This sequential workflow is essential to maintain evaluation rigor. You can use this approach to make an informed decision about model replacement.

**First**, you must define evaluation metrics. This step establishes the specific criteria to measure model performance. Important metrics include relevance, factual accuracy, and fluency. These metrics provide a quantifiable way to assess model outputs. You need to review and approve the metrics before proceeding. The metrics determine what constitutes success in all subsequent testing steps.

**Second**, you must create a test dataset with diverse scenarios and edge cases. This step provides the controlled data that you need for systematic evaluation. The dataset must include carefully selected examples that cover various use cases, potential edge cases, and challenging scenarios. The test dataset must align with the approved evaluation metrics and ensure comprehensive coverage of test cases.

**Third**, you must conduct A/B testing. A/B testing systematically compares the performance of the new model against the existing model using the test dataset. A/B testing runs both models on the same inputs and measures the outputs against the defined metrics. A/B testing provides direct performance comparisons. The testing can only proceed after both the metrics and the test dataset are validated.

**Fourth**, you must implement automated quality gates by using Step Functions. This step establishes automated checkpoints in the evaluation workflow. The gates enforce the approval requirements between stages. The gates automatically verify the results against predefined thresholds. The gates ensure that all necessary validations are completed before proceeding.

**Finally**, you must analyze the results and generate a comprehensive evaluation report. This step must be the final step because first you must complete all the previous steps and approve the results. This analysis provides the evidence that you need to make an informed decision about replacing the existing model. You can make a decision based on performance measurements, established metrics, and a validated testing framework.

**Read more**

- [Amazon Bedrock evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html)
- [Step Functions for ML workflows](https://docs.aws.amazon.com/step-functions/latest/dg/use-cases.html#use-cases-machine-learning)
- [A/B testing](https://docs.aws.amazon.com/sagemaker/latest/dg/model-ab-testing.html)

<sub>[↑ back to question 17](#question-17)</sub>

---

## Answer 18

**Correct answers: C and D**

**Why C is correct**

DJL is an open source, high-level deep learning framework. You can use DJL to streamline the process of building and deploying deep learning models. You can deploy models on SageMaker AI with DJL Serving. If the weights and activations fit within the memory limits on the available GPUs, then you can change the tensor parallel configuration. This solution creates multiple model copies in the same instance.

**Why D is correct**

You can use DJL to overwrite the maximum number of requests or sequences that a model can process at a time. You can reduce maximum sequence length to free up memory to use for larger batch sizes. This step increases throughput and concurrency for each instance.

**Why the others are incorrect**

- **A.** You can indicate the tensor parallelism degree to use. Using a tensor parallelism degree of 8 would restrict the instance to serving only one model replica across all 8 GPUs. The GenAI developer determined that the model fits within 4 GPUs. Therefore, spreading the model across 8 GPUs would leave half of the instance's GPU capacity underutilized.
- **B.** SageMaker AI supports inference optimization through speculative decoding. This technique can speed up the decoding process of large LLMs by using draft models. Speculative decoding improves latency, not resource utilization. Therefore, this step would not improve the issue in this scenario. Instead, you can explore the serving properties used with DJL to serve the model.
- **E.** SageMaker AI supports auto scaling based on user demand. However, increasing the number of instances does not improve concurrency or decrease the GPU memory footprint. The model is being served with DJL. Therefore, you can explore changing serving property configurations to improve utilization.

**Read more**

- [Deploy deep learning models on SageMaker AI with DJL Serving](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-models-frameworks-djl-serving.html)
- [Inference optimization for SageMaker AI](https://docs.aws.amazon.com/sagemaker/latest/dg/model-optimize.html)

<sub>[↑ back to question 18](#question-18)</sub>

---

## Answer 19

**Correct answer: C**

**Why C is correct**

SageMaker asynchronous endpoints provide long-running inference workloads with processing times up to 15 minutes. Asynchronous endpoints efficiently manage compute resources. This deployment strategy supports GPU instances for efficient processing, handles large datasets (up to 1 GB), and provides scaling based on actual usage.

**Why the others are incorrect**

- **A.** SageMaker real-time endpoints provide continuous, low-latency inference with sub-millisecond processing times. Real-time endpoints have dataset size limits up to 25 MB. Therefore, this deployment strategy does not meet the requirement for datasets up to 50 MB.
- **B.** SageMaker serverless inference automatically provisions and scales compute capacity based on the number of inference requests. However, this deployment strategy does not support the GPU-powered instances that you need for efficient image generation.
- **D.** SageMaker AI batch transform is designed for offline processing of large datasets in batches. Batch transform does not support on-demand individual requests. Batch transform is not suitable for on-demand image generation. Additionally, batch transform does not support responses within 15 minutes.

**Read more**

- [SageMaker asynchronous endpoints](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html)
- [SageMaker AI endpoint deployment options](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model-options.html)
- [SageMaker real-time endpoints](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html)
- [SageMaker serverless inference](https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html)
- [SageMaker AI batch transform](https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html)

<sub>[↑ back to question 19](#question-19)</sub>

---

## Answer 20

**Correct answers: A and E**

**Why A is correct**

Amazon Cognito with OIDC integration provides a secure way to authenticate users through the company's existing IdP. This solution can exchange identity tokens for temporary AWS credentials. Therefore, this solution eliminates long-lived credentials. This solution allows the application to access Amazon Bedrock using short-term credentials and to integrate with an existing IdP. This solution provides comprehensive logging through AWS CloudTrail.

**Why E is correct**

IAM Identity Center with SAML federation can provide secure authentication and integration with the IdP. IAM Identity Center provides federation with IdPs. IAM Identity Center eliminates long-lived credentials by providing temporary security credentials. This solution provides audit logging through AWS CloudTrail. This solution meets all the requirements by integrating with the existing IdP while maintaining secure access control.

**Why the others are incorrect**

- **B.** Creating IAM users for each employee does not meet the requirement to eliminate long-lived credentials. Secrets Manager can assist with credential rotation. However, this solution relies on persistent access keys. This solution does not integrate with the existing IdP. This solution does not provide temporary access.
- **C.** API Gateway Lambda authorizers can provide authentication. However, this solution does not meet the requirement for temporary AWS credentials. This solution requires custom development to manage credential exchange. This solution does not use built-in integration capabilities for identity federation.
- **D.** AWS STS `AssumeRole` allows applications to acquire temporary credentials. However, storing the application's IAM user credentials in the configuration violates the requirement to eliminate long-lived credentials. This solution does not properly integrate with the existing IdP.

**Read more**

- [Amazon Cognito and OIDC](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-oidc-idp.html)
- [AWS IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html)
- [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [API Gateway Lambda authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- [AWS STS temporary credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html)

<sub>[↑ back to question 20](#question-20)</sub>


---

## Answer key

| # | Answer | Topic |
|---|--------|-------|
| 1 | D | Guardrail enforcement via IAM condition keys |
| 2 | B | Guardrail observability (`GuardrailPolicyType`) |
| 3 | B, E | Source lineage — metadata tagging + Glue Data Catalog |
| 4 | A, B | Amazon Q Developer in CI/CD |
| 5 | A | S3 Vectors for infrequent similarity search |
| 6 | A, E | Prompt Management + invocation logging with S3 Object Lock |
| 7 | D | Knowledge base logging to CloudWatch Logs |
| 8 | B | API Gateway WebSocket + Bedrock streaming |
| 9 | D | Stop sequences parameter |
| 10 | C | Embedding drift |
| 11 | B, D | Hybrid search + reranker models |
| 12 | A | Cross-Region inference |
| 13 | C | S3 events → SQS → Lambda direct ingestion |
| 14 | A | Comprehend PII redaction + Kendra |
| 15 | C, D | AgentCore SDK `@app.entrypoint` + starter toolkit |
| 16 | C | Step Functions + Bedrock multimodal FMs + Quick Sight |
| 17 | ordering | FM evaluation workflow sequence |
| 18 | C, D | DJL tensor parallelism + max sequence length |
| 19 | C | SageMaker Asynchronous Inference |
| 20 | A, E | Cognito OIDC + IAM Identity Center |

### Themes worth reviewing

- **Bedrock guardrails** — IAM `bedrock:GuardrailIdentifier`, `GuardrailPolicyType` vs `GuardrailContentSource` metrics
- **Logging** — model invocation logging (content) vs CloudTrail (API metadata only) vs knowledge base logging (ingestion status)
- **Knowledge Bases** — hybrid search, rerankers, direct ingestion APIs, metadata attributes
- **Vector stores** — S3 Vectors (serverless/infrequent) vs OpenSearch Serverless (frequent/low latency) vs pgvector (managed instances)
- **Throughput** — cross-Region inference vs provisioned throughput vs prompt routing
- **Deployment** — SageMaker real-time (25 MB) vs async (1 GB, 15 min) vs serverless (no GPU) vs batch transform
- **AgentCore Runtime** — SDK decorator and starter toolkit over hand-rolled containers
- **Auth** — federation for temporary credentials; never long-lived IAM user keys
