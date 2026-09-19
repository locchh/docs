# Unit 03: Enterprise integration

**Task 2.3: Design and implement enterprise integration architectures.** This unit is about fitting GenAI into an enterprise that already exists: connecting to legacy systems through APIs and events, federating the identity the company already has, keeping data where regulations say it must stay, and releasing changes through a pipeline that can be audited.

Domain 1 unit 01 introduced the integration patterns; this unit goes deeper into the enterprise realities: legacy systems that cannot change, identity that already exists, data that cannot move, and release processes that must be auditable.

## Connecting to systems that already exist

Most GenAI features are added to a platform that was not built for them. Start by matching the integration job to an AWS service:

- **Amazon API Gateway** exposes HTTPS APIs.
- **AWS AppSync** serves **GraphQL** clients.
- **Amazon SQS** queues provide point-to-point buffering.
- **Amazon SNS** provides publish-subscribe notifications.
- **Amazon EventBridge** provides an **event bus** with **rules**, **Pipes** and a **Scheduler**.
- **Amazon Kinesis Data Streams** handles high-volume streams.
- **Amazon MSK**, the managed **Kafka** service, also handles high-volume streams.
- **Amazon MQ** supports existing **JMS** and **AMQP** brokers.
- **AWS Step Functions** orchestrates workflows.
- **Amazon AppFlow** synchronizes SaaS data.
- **AWS Glue** and **AWS DMS** move data between systems.

Two integration techniques built from these services cover almost every case.

**API-based integration.** Put **Amazon API Gateway** in front of the FM capability and let the legacy system call it like any other HTTPS service. This is the pattern when the legacy system can only make outbound HTTPS calls and needs a stable contract.

**API Gateway REST APIs** provide request and response **mapping templates**. These reshape payloads between the legacy format and what the model or your **Lambda** function expects. The APIs also provide **custom domain names**, per-client **usage plans** and caching.

Behind the API, **Lambda adapters** handle protocol conversion, field mapping and error translation. For example, they can convert **SOAP** or fixed-width payloads to JSON.

**Event-driven integration.** When the platform already emits business events, such as an order being created, a claim updated or a ticket opened, route them through **Amazon EventBridge**. The flow is:

1. The legacy system publishes to an **event bus**.
2. **Rules** use **event patterns** to select the events that need AI processing.
3. **Input transformers** normalize the selected events.
4. Targets such as **Lambda**, **Step Functions** or **SQS** do the work.
5. Results go to a synchronized store, such as **DynamoDB** or **S3**, that downstream consumers read.

The legacy application never learns the model exists. This is what "loose coupling" and "minimal disruption" mean in questions.

Related services cover different event requirements:

- **EventBridge Pipes** connects a single source to a target, with filtering and enrichment in between. Sources include **SQS**, **Kinesis**, **DynamoDB Streams**, **Kafka** and **Amazon MQ**.
- **EventBridge Scheduler** runs recurring or one-time jobs.
- **Amazon MQ** bridges existing **JMS** or **AMQP** brokers.
- **Amazon Kinesis Data Streams** provides real-time ingestion for continuous high-volume data, such as market ticks, telemetry and clickstreams.
- **Amazon MSK**, the managed **Kafka** service, plays the streaming role for enterprises using **Kafka**.

In **Kinesis Data Streams**, producers write records to **shards**. **Lambda** consumers or **Managed Service for Apache Flink**, the managed stream-processing service, process them within seconds. The stream retains records for replay. **Dead-letter queues** capture events that fail processing.

**Data synchronisation.** Models need current enterprise data, so pipelines keep copies fresh. Choose the service for the source and the work:

- **AWS Glue** ETL jobs use **job bookmarks** to process only new or changed records into **S3** or a **knowledge base**.
- **Amazon AppFlow** synchronizes SaaS applications, such as **Salesforce**, **ServiceNow** and **SAP**, bidirectionally with filtering and field mapping.
- **AWS DMS** replicates databases.
- **Step Functions** orchestrates multi-step syncs.

When sensitive data cannot leave a system, use an **abstraction layer**. It extracts only the non-sensitive features the model needs instead of replicating the records.

Direct synchronous calls from the legacy system to **Bedrock**, self-managed queues with periodic batch uploads, VPNs to write into cloud databases, and polling databases for changes are the distractors.

## Enhancing existing applications

Skill 2.3.2 applies the same toolkit from the application side. Expose the FM capability as a **microservice** behind **API Gateway**, with **throttling**, caching and monitoring so any application can consume it.

For inbound **webhooks** from a SaaS platform, such as a support platform sending conversation events, use **API Gateway** with a **Lambda** handler. The handler follows a short sequence:

1. Validate the payload.
2. Deduplicate it with **idempotency keys**.
3. Invoke the model.
4. Return or post the result in real time.

**EC2** web servers, always-on containers and batching **webhooks** through **SQS** are wrong for a real-time **webhook**.

Other application needs use the same services in different ways:

- **EventBridge rules** trigger AI enrichment on application events, such as recommendations when a customer views a product.
- Caching at **API Gateway**, application and database layers cuts model calls. Client libraries or SDKs help teams consume the capability consistently.
- **Amazon SQS FIFO queues** preserve ordering when related requests must be processed in sequence.
- **AWS AppSync resolvers** can call **Lambda** or **Bedrock** directly for **GraphQL** clients.

## Securing access

Skill 2.3.3 is where Domain 2 overlaps Domain 3, and the exam repeats a small set of principles.

**Federate identity; do not create IAM users.** Choose the federation service according to who needs access.

For workforce access, **AWS IAM Identity Center** connects to the corporate identity provider through **SAML federation**. The provider can be **Microsoft Entra ID**, **Okta** or any provider that speaks **SAML 2.0**, the XML-based single sign-on standard. **SCIM provisioning** automatically synchronizes users and groups from the identity provider.

Map **permission sets** to groups. Analysts, auditors and risk officers then receive **least-privilege IAM roles** that allow only the **Bedrock** or **SageMaker** actions their group needs.

For application and customer users, **Amazon Cognito user pools** authenticate users, including through **OIDC** to an external identity provider. **Identity pools** exchange tokens for **temporary AWS credentials** scoped by role.

A **Cognito pre token generation Lambda trigger** can enrich the issued **JWT** with **enterprise claims** looked up from the identity provider or a directory. These claims can include department, clearance level or customer tier. Downstream authorizers can then make role decisions from the token itself.

Both approaches give short-lived credentials, central lifecycle management and **CloudTrail audit trails**. The recurring wrong answers are:

- **IAM users** with long-lived keys.
- **API keys** used as identities.
- **LDAP**-checking **Lambda authorizers** that mint their own tokens.
- Access keys stored in configuration.

**Least privilege with conditions.** **IAM policies** on the roles that call **Bedrock** name specific model ARNs and actions. Add **condition keys** when the permission must depend on context:

- `bedrock:GuardrailIdentifier` forces a **guardrail** on every invocation.
- Source VPC or IP conditions restrict where calls originate.
- Tags or time-of-day conditions further constrain access.

**Permission boundaries** cap what delegated administrators can grant. When **IAM** alone is too coarse, **Amazon Verified Permissions** adds fine-grained application authorization with **Cedar policies**. These policies specify which users may run which operations on which data classification.

**Network and encryption.** Apply a separate control to each boundary:

- **AWS PrivateLink interface endpoints** keep **Bedrock** and **SageMaker** traffic on the AWS network. **Endpoint policies** restrict which operations can be called from the VPC.
- **AWS KMS customer managed keys** encrypt data at rest. Use **multi-Region keys** where data is processed in several geographies.
- **AWS Certificate Manager** handles TLS.
- **AWS WAF rate-based rules** and **geographic matching** protect public API endpoints.
- **CloudTrail** logs activity for audit.
- **AWS Security Hub** centralizes security findings. Its dashboard aggregates findings from AWS services and checks accounts against security standards.

**Amazon Q Business**, the managed enterprise assistant taught in unit 05, plugs into the same **Identity Center** identities so its answers respect each user's document permissions. **Q Business** is closed to new customers since 31 July 2026, with **Amazon Quick** as the successor, but it remains the exam's vocabulary.

## Operating across environments and jurisdictions

Skill 2.3.4 answers "the data cannot leave" and "the users are far away".

**AWS Outposts** is AWS-managed infrastructure installed as racks or servers in your data center and connected to a parent Region. It runs **EC2**, **EBS**, **ECS**, **EKS**, **RDS** and other services locally.

**Bedrock** itself does not run on **Outposts**. For the compliant pattern, run preprocessing, redaction or feature extraction on **Outposts**, then send only sanitized text or feature vectors to **Bedrock** in the nearest Region. Alternatively, host a **SageMaker**-trained model on local compute.

Two other infrastructure options address proximity to users:

- **AWS Local Zones** place compute and storage in metropolitan areas for single-digit-millisecond latency to users there.
- **AWS Wavelength** embeds AWS compute at the edge of 5G carrier networks for mobile applications that need the lowest latency.

Connect and control these environments with the following services:

- **AWS Direct Connect** supplies dedicated private links.
- **AWS Site-to-Site VPN** supplies encrypted tunnels over the internet.
- **AWS Transit Gateway** acts as a hub that routes between VPCs and on-premises networks.
- **AWS Network Firewall** inspects traffic.
- **AWS Control Tower controls** block resources in non-compliant Regions.

**Geographic cross-Region inference profiles**, covered in Domain 1, keep **Bedrock** inference within a geography.

The trap in these questions is any option that moves the regulated data to the cloud first: uploading to a central **S3** bucket with encryption, syncing on-premises data to **Bedrock** on a schedule, or caching it in **Wavelength** Zones all violate the residency requirement.

## Shipping safely: CI/CD and the GenAI gateway

Skill 2.3.5 treats GenAI components like software. This includes prompts, **guardrail configurations**, routing rules and the gateway code itself. The AWS developer toolchain assigns each job to a service:

- **CodePipeline** manages the pipeline.
- **CodeBuild** builds and tests.
- **CodeDeploy** deploys with traffic shifting.
- **CloudFormation** and the **CDK** define **infrastructure as code**.
- **Service Catalog** publishes approved products.
- **Amplify** provides front ends.
- **Amazon Q Developer** and **Kiro** are AI assistants for developers.

A **CodePipeline** pipeline moves a change through these stages:

1. Pull the change from source control.
2. Build and test in **CodeBuild**. Checks include unit tests, prompt **regression tests** against **golden datasets**, model evaluations, and dependency and static security scans.
3. Pause at a **manual approval gate** for production.
4. Deploy with **CodeDeploy**, using **canary** or **linear traffic shifting** for **Lambda** and **ECS**. For endpoints, use **SageMaker deployment guardrails**.
5. Roll back automatically when **CloudWatch alarms** fire.

Define infrastructure in **CloudFormation** or **CDK**. Publish approved patterns through **AWS Service Catalog**, a curated catalog of approved **CloudFormation** products that teams launch through self-service.

The distractors are **EC2** with cron restarts, manual **Lambda** deployments after local tests, and manual image pushes to **ECR**, the container image registry.

A **GenAI gateway** is the centralized abstraction layer many enterprises put between every application and the models. It consists of an **API Gateway** and **Lambda** or container tier that handles shared responsibilities:

- Authenticate callers.
- Apply **guardrails** and **prompt-safety rules**.
- Enforce quotas and cost allocation per team.
- Route to the right model or provider.
- Log every request for audit.
- Emit metrics and traces.

Because every team goes through it, a change to the gateway is high-risk. That is why the pipeline above, with automated tests, security scans and rollback, is the keyed answer for "auditable release of gateway updates".

## Worked scenario

A bank adds generative AI to a thirty-year-old order-management platform. The mainframe can only make outbound HTTPS calls, business events already flow through an internal bus, employees sign in through **Microsoft Entra ID**, customers use a mobile app, one country's data may not leave its borders, and every release must be auditable.

Integration uses the two patterns. For the mainframe, **API Gateway** fronts the FM capability with **mapping templates** that reshape its fixed-width payloads, and **Lambda adapters** do the protocol conversion, so the mainframe calls one stable HTTPS contract. For the rest, the platform's order events are published to Amazon **EventBridge**; rules select the events that need enrichment, **Lambda functions** call **Bedrock** and write results to **DynamoDB**, and downstream consumers read them, never knowing a model exists. High-volume trade ticks arrive through **Kinesis Data Streams**, and **AWS Glue** jobs with **bookmarks** keep the **knowledge base**'s reference data in sync.

Identity is federated, never re-created. Employees reach the tools through **IAM Identity Center** connected to **Entra ID** over **SAML 2.0** with **SCIM provisioning** and **permission sets** per role; the mobile app authenticates customers through an **Amazon Cognito** **user pool**, with a **pre token generation trigger** adding their service tier to the token and an **identity pool** issuing temporary credentials. **IAM policies** name the allowed model ARNs and require the approved guardrail; **PrivateLink** endpoints keep **Bedrock** traffic private; **KMS** **customer managed keys** encrypt everything at rest.

For the country with residency rules, an **AWS Outposts** rack runs the preprocessing and redaction locally, and only sanitised text reaches **Bedrock** in the nearest Region through a **geographic inference profile**. Releases of the shared **GenAI gateway** (the **API Gateway** and **Lambda** tier that applies **guardrails**, quotas and logging for every team) flow through **CodePipeline** with **CodeBuild** tests and security scans, a manual approval, and **CodeDeploy** **canary** shifting with automatic rollback. The exam splits this scenario into its parts: legacy integration, event-driven enhancement, federated access, residency, and auditable CI/CD.

## Exam lens

- "On-premises legacy system, outbound HTTPS only, loose coupling, asynchronous, downstream consumers need results as soon as ready" → **EventBridge** events → **Lambda** → **Bedrock** → synchronised store (**DynamoDB** or **S3**).
- "Add GenAI to an order-management app without tightly coupled API calls" → route existing events through **EventBridge** rules to **Lambda**.
- "Real-time **webhook** from a SaaS platform" → **API Gateway** plus **Lambda** handler.
- "Centralised authentication through the enterprise IdP, **least privilege**, role-based, no long-lived credentials" → **IAM Identity Center** with **SAML federation** and **permission sets** (or **Cognito** with **OIDC** for application users).
- "Sensitive data must stay on premises but use **Bedrock**" → **Outposts** for local processing, sanitised data to **Bedrock** in Region.
- "Gateway updates need automated tests, security scans, auditable release, automatic rollback" → **CodePipeline** and **CodeBuild** deploying behind **API Gateway** with rollback.
- "**Q Business** over internal repositories with enterprise RBAC and least effort" → **Q Business** **data source connectors** with **IAM Identity Center** for authentication and access control (unit 05 teaches **Q Business**; the question sits there).

## Knowledge check

<!-- KC: E1-Q37, E2-Q12, E1-Q68, E1-Q15 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 37

A large insurance company is modernizing its legacy claims-processing platform by integrating a new Amazon Bedrock–powered claims summarization service. The legacy system runs on-premises and can only send outbound HTTPS requests. The enterprise architecture team wants to ensure loose coupling, support asynchronous processing, and maintain consistent data flow between on-prem workloads and the new FM-based service. They also need real-time synchronization so downstream systems can consume AI-generated summaries as soon as they are ready.

Which integration approach BEST meets these requirements?

- **A)** Use an event-driven architecture where the on-prem system publishes claim update events to Amazon EventBridge, triggering a Lambda function that invokes the Bedrock model and writes results to a synchronized data store such as DynamoDB or Amazon S3.
- **B)** Deploy a self-managed message queue inside the on-prem environment and periodically batch-upload queued messages to S3 for Bedrock processing.
- **C)** Create a direct synchronous API Gateway → Bedrock integration and require the on-prem system to invoke Bedrock directly for each request.
- **D)** Build a custom VPN-based connection so the on-prem system can directly access DynamoDB tables and write the AI-generated summaries in real time.

<details><summary>Answer</summary>

**Answer: A.** Publishing claim events from the on-premises system to EventBridge over HTTPS decouples it from the model, a Lambda target invokes Bedrock asynchronously, and writing results to a synchronised store such as DynamoDB or S3 lets downstream systems consume summaries as soon as they are ready. A self-managed queue with batch uploads adds delay, a synchronous API Gateway to Bedrock call couples the systems, and a VPN for direct DynamoDB writes is neither loosely coupled nor an integration pattern.

*Where this is covered: Unit 03, Connecting to systems that already exist. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 2, question 12

A retail technology team is upgrading its existing order-tracking web application by adding a new GenAI-powered “order explanation” feature that summarizes delays, carrier notes, and historical delivery patterns using an Amazon Bedrock FM. The legacy application calls external services only through REST endpoints and must continue using its current microservices architecture. The team wants to implement a lightweight integration pattern where the application triggers the summarization workflow via a simple API call, while a backend service handles invoking the Bedrock model and returning the generated explanation asynchronously through a webhook.

Which integration approach BEST meets these requirements?

- **A)** Connect the order-tracking application directly to the Bedrock API and perform synchronous inference for each summarization request.
- **B)** Build a step-based polling workflow in the application that repeatedly queries an S3 bucket for the generated summary after the model completes processing.
- **C)** Use API Gateway to expose a REST endpoint that the order-tracking app calls, triggering a Lambda function that invokes the Bedrock model and posts the generated summary back to the application using a webhook URL.
- **D)** Deploy an Amazon ECS service that continuously runs a long-lived container dedicated to invoking Bedrock and exposes its own custom REST API to the application.

<details><summary>Answer</summary>

**Answer: C.** The application calls a REST endpoint on API Gateway, a Lambda function invokes Bedrock, and the summary is posted back asynchronously to the application's webhook URL, keeping the legacy microservices architecture intact with a lightweight integration. Direct synchronous Bedrock calls block the application, S3 polling adds latency and complexity, and a long-lived ECS container with its own API is heavier than needed.

*Where this is covered: Unit 03, Enhancing existing applications. Key: ours, confidence high.*

</details>

### 3. Exam 1, question 68

A financial services company is integrating Amazon Bedrock into its existing loan-processing platform to generate automated explanations for loan approval decisions. The platform relies on an internal identity provider (IdP) that manages user permissions for analysts, auditors, and risk officers. The security team requires a framework that ensures:

- centralized authentication through the enterprise IdP,
- least-privilege access to Bedrock model APIs,
- role-based controls so that only a small group of analysts can invoke the FM, and
- no long-lived credentials stored in the application environment.

Which solution BEST satisfies these requirements?

- **A)** Use API Gateway API keys to control who can invoke the Bedrock model, mapping each analyst's identity to a unique API key.
- **B)** Configure each analyst with separate IAM user accounts and attach Bedrock invocation policies directly to their user credentials.
- **C)** Allow the application to store AWS access keys for analysts in an encrypted configuration store and validate their permissions on each request.
- **D)** Use IAM Identity Center with SAML federation to the company's IdP and assign fine-grained, least-privilege IAM roles that permit Bedrock model invocation only for authorized analyst groups.

<details><summary>Answer</summary>

**Answer: D.** IAM Identity Center with SAML federation to the enterprise IdP centralises authentication, and fine-grained IAM roles assigned to authorised analyst groups give least-privilege Bedrock invocation with temporary credentials only. API keys are not user identities, per-analyst IAM users and stored access keys are long-lived credentials, and none of them integrate the enterprise IdP.

*Where this is covered: Unit 03, Securing access. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 4. Exam 1, question 15

A global logistics company is building a centralized GenAI gateway that routes all employee prompts through a controlled abstraction layer before invoking Amazon Bedrock models. Each update to the gateway—such as new guardrails or prompt-safety rules—must be validated through automated tests and security scans. The company also requires an auditable release process with automatic rollback if a change causes unsafe or incorrect behavior in production.

Which deployment approach BEST meets these requirements?

- **A)** Host the gateway on an Amazon EC2 instance and use cron jobs to restart it when new versions are uploaded.
- **B)** Build a CI/CD pipeline using AWS CodePipeline and CodeBuild, integrate automated test suites and security scans, and deploy the GenAI gateway behind API Gateway with automatic rollbacks enabled.
- **C)** Use a Lambda function with versioning and aliases to manually deploy updates after developers run tests locally.
- **D)** Deploy the GenAI gateway with Amazon ECS and push container image updates manually to Amazon ECR.

<details><summary>Answer</summary>

**Answer: B.** A CodePipeline and CodeBuild pipeline runs automated tests and security scans on every gateway change, produces an auditable release history, and deploys behind API Gateway with automatic rollback when production behaviour degrades. EC2 with cron restarts, manual Lambda alias deployments after local tests, and manual image pushes to ECR provide neither validation nor rollback.

*Where this is covered: Unit 03, Shipping safely: CI/CD and the GenAI gateway. Key: ExamPro answer key (Exam 1 graded).*

</details>

<!-- KC-END -->

## Summary

Integrate through **API Gateway** and **Lambda adapters** when the legacy system must call you, and through **EventBridge** rules, Pipes and queues when it already emits events; keep data current with **Glue**, **AppFlow** and **DMS**, or expose only non-sensitive features. Enhance applications as microservices, **webhook** handlers and event-driven enrichers with caching and client libraries.

Secure access with **IAM Identity Center** or **Cognito** federation, **least-privilege** roles with condition keys, Verified Permissions for fine-grained rules, **PrivateLink**, **KMS** and **WAF**. Respect residency with **Outposts**, **Local Zones** and **Wavelength** connected by **Direct Connect**, VPN and **Transit Gateway**, never by moving the regulated data. Release through **CodePipeline** and **CodeBuild** with tests, scans, approvals and automatic rollback, fronted by a **GenAI gateway** that centralises auth, **guardrails**, quotas, routing and logging.
