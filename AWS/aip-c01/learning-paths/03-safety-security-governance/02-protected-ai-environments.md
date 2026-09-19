# Unit 02: Protected AI environments

**Task 3.2: Implement data security and privacy controls (part one: protected environments).** This unit is about the walls around a GenAI workload:

- Keeping model and data traffic off the public internet with **VPC endpoints**.
- Deciding who may call which model and read which data, with **IAM**, identity federation and **Lake Formation**.
- Encrypting everything with keys you control.
- Watching access with **CloudTrail** and **CloudWatch**.

Unit 03 continues Task 3.2 with the privacy of the data itself.

The questions here are classic AWS security questions wearing a GenAI costume. If you know how **VPC endpoints**, **IAM** roles, **KMS** and **CloudTrail** work, you already know most of the answers. This unit adds the **Bedrock**- and **SageMaker**-specific facts.

## What "protected" means for a model

Start with what AWS already guarantees, because questions test it. Under the **shared responsibility model**, AWS secures the infrastructure and you secure your configuration and data.

For **Amazon Bedrock** the platform promises are specific:

- Your prompts, completions and customisation data are **not used to train or improve** the base models, and are **not shared with model providers**.
- Each provider's model runs in a **model deployment account** owned by the **Bedrock** team that the provider cannot access.
- By default **Bedrock** keeps **zero data retention**, so prompts and responses are not stored after the response, and **zero operator access**, so no AWS operator can read model inputs or outputs.
- Data in transit uses TLS 1.2 or later, and FIPS endpoints exist for workloads that need validated cryptography.

The one nuance is abuse detection. For some third-party models AWS retains traffic for up to 30 days for automated offline abuse detection: all traffic for certain **Anthropic** models, and only classifier-flagged traffic for **OpenAI** models. It is stored by AWS in the Region that processed the request, never shared with the provider, and flagged content is subject to possible human review by AWS. Images that match known child sexual abuse material are blocked outright.

What remains yours is everything around the call: the network path the request takes, the identity that makes it, the keys that protect stored data, the permissions on the data the model reads, and the logs that prove all of it. That is the outline of this unit.

The AWS security services form five families, and this unit visits each:

- **Identity**: **IAM**, **IAM Identity Center**, **Amazon Cognito**, **AWS STS** and **Amazon Verified Permissions** decide who may do what.
- **Network**: **Amazon VPC**, **AWS PrivateLink**, **AWS WAF**, **AWS Shield** and **AWS Network Firewall** decide what can reach what.
- **Data protection**: **AWS KMS**, **AWS Secrets Manager**, **AWS Certificate Manager** and **Amazon Macie** protect keys, secrets, certificates and sensitive data.
- **Detection**: **Amazon GuardDuty**, **Amazon Inspector**, **AWS Security Hub**, **AWS Config** and **AWS CloudTrail** find threats, vulnerabilities and misconfigurations, and record activity.
- **Governance**: **AWS Organizations**, **AWS Control Tower**, **AWS Audit Manager** and **AWS Artifact** set and prove the rules.

Each is defined where it first matters below.

## Network isolation

An **Amazon VPC** is your private network in AWS: subnets, route tables, **security groups**, which are stateful allow-lists attached to network interfaces, and **network ACLs**, which are stateless subnet-level rules.

A **private subnet** has no route to an internet gateway. Resources in it reach the internet only through a **NAT gateway**, which is exactly the component a strict question tells you not to add.

**VPC endpoints** let resources in a private subnet call AWS services without any internet path. They come in two kinds.

**Gateway endpoints** exist for two services, **Amazon S3** and **DynamoDB**. A route-table entry sends traffic to the service over the AWS network at no charge. **S3** also supports a paid interface endpoint, which is useful from on premises or across VPCs, but inside a **VPC** the free gateway endpoint is the default answer.

**Interface endpoints**, powered by **AWS PrivateLink**, create an elastic network interface with a private IP address in your subnet for every other service, including **Bedrock**, **SageMaker**, **Comprehend**, **Textract**, **Rekognition**, **Polly**, **Translate** and **KMS**. Two controls attach to an interface endpoint:

- **Security groups** on its network interface decide which instances or subnets may send traffic to it.
- An **endpoint policy**, a resource-based **IAM** policy, decides which principals may perform which API actions through it.

With **private DNS** enabled, the service's normal hostname resolves to the endpoint, so applications need no code changes.

The **Bedrock** endpoints are:

- `com.amazonaws.<region>.bedrock` for the control plane.
- `bedrock-runtime` for `InvokeModel` and `Converse`.
- `bedrock-agent` for build-time agent and knowledge-base APIs.
- `bedrock-agent-runtime` for `InvokeAgent`, `Retrieve` and `RetrieveAndGenerate`.

FIPS variants exist for each. A complete private path for a RAG application therefore needs the runtime and agent-runtime endpoints for **Bedrock**, an **S3** gateway endpoint for documents, and interface endpoints for any other service in the path. **S3** bucket policies can then require the private path with the `aws:SourceVpce` or `aws:SourceVpc` condition key, so the documents are unreadable from anywhere except your endpoint.

**Amazon SageMaker AI** has its own isolation switches. **SageMaker Studio**, the web-based ML development environment, and **notebook instances** have direct internet access by default. Launching them in **VPC-only mode** inside private subnets removes it, after which they need interface endpoints for:

- The **SageMaker** API (`sagemaker.api`).
- The **SageMaker** runtime (`sagemaker.runtime`), for invoking endpoints.
- **Studio** (`sagemaker.studio`).
- Any other service they call, plus an **S3** gateway endpoint for data.

The same `VpcConfig`, meaning subnets and security groups, can be given to training jobs, processing jobs and hosted models, so their containers run inside your **VPC**.

**Network isolation** (`EnableNetworkIsolation`) goes further. The training or inference container can make **no outbound network calls at all**, not even to **S3**, and receives no AWS credentials; **SageMaker** copies the data in and the artifacts out for it. It is mandatory for AWS Marketplace algorithms and models.

It also means a network-isolated container cannot call **Comprehend** or any other API itself. When a question pairs network isolation with "the model calls **Comprehend** privately", read the intent as VPC-private access rather than a literal call from the isolated container. It is still the best option when the alternatives are internet gateways, public endpoints or **VPC** peering that leads nowhere.

For **distributed training** across several instances, **inter-container traffic encryption** encrypts the traffic between the training nodes, at some cost in training time. That, together with a **VPC** without internet access and **S3** access through a **VPC endpoint**, answers "encrypt data in transit between nodes, never traverse the public internet".

The pattern the exam rewards is always the same: private subnets, **VPC endpoints** for every AWS service touched, security groups and endpoint policies to narrow who uses them, and **no** NAT gateway, proxy fleet, internet gateway, Site-to-Site VPN "to AWS services" or **VPC** peering. Peering connects two VPCs, and AWS services are not in a **VPC** you can peer with.

## Identity: who may call the model and read the data

**AWS Identity and Access Management (IAM)** decides what a principal may do. The rules the exam repeats:

- **Roles, not users.** Workloads run under **IAM roles** with temporary credentials. A **SageMaker** notebook, **Studio** user or training job acts through its **execution role**. Giving that role `s3:GetObject`, `s3:PutObject` and `s3:ListBucket` on exactly the required buckets is the least-privilege way to let a notebook read training data and write artifacts. Long-lived **IAM** user access keys stored in configuration, rotated or not, are always wrong. **S3 Access Points** are named entry points to a bucket with their own policies, useful for giving many teams different views of one shared dataset, but an access point "configured for open access" is a distractor, and a bucket policy that allows a principal unrestricted access is not least privilege.
- **Scope by resource ARN.** When each data scientist has a personal notebook instance, write an **IAM** policy per developer that allows the **SageMaker** notebook actions only on the ARN of their own instance, while allowing shared access to **Rekognition** and the central **S3** data lake. That prevents anyone from starting, stopping or opening another person's notebook. Lifecycle configurations, security groups and shared notebooks cannot express "whose notebook this is".
- **Conditions and tags.** Condition keys refine an allow or deny. Use `aws:SourceVpce` for "only through our endpoint", and `aws:PrincipalTag` and `aws:ResourceTag` for **attribute-based access control**, which is a single policy that allows access when the caller's project tag matches the resource's. **Bedrock** has its own keys too, such as `bedrock:GuardrailIdentifier` from unit 01. **Service control policies (SCPs)** in **AWS Organizations** set the maximum permissions for whole accounts, for example denying **Bedrock** in Regions outside the approved geography; they grant nothing themselves. **Permission boundaries** cap what a role can ever be granted.

**Federation** answers every question that says "existing identity provider", "no long-lived credentials" and "audit logs". There are two managed front doors, and the wording tells you which.

**AWS IAM Identity Center** is for **workforce** users, meaning employees, across AWS accounts and applications. You connect the corporate IdP, whether **Microsoft Entra ID**, **Okta** or any **SAML 2.0** provider, which is the XML-based single sign-on standard. You turn on **SCIM** provisioning, the standard that pushes users and groups from the IdP automatically, and assign **permission sets**, which become **IAM** roles in each account, to groups.

**Identity Center** does not accept an external IdP over **OIDC**, so "**Identity Center** with an OIDC provider for Entra ID" is a distractor. Direct **SAML federation to IAM roles**, mapping IdP groups to roles, is the older but valid alternative when **Identity Center** is not in the option.

**Amazon Cognito** is for **application** users, including partners and customers. A **user pool** authenticates them, natively or by federating to an external IdP over **OIDC** or SAML, and issues **JSON Web Tokens (JWTs)**. An **identity pool** exchanges those tokens for **temporary AWS credentials** scoped by an **IAM** role, so the application can call **Bedrock** directly with short-lived keys. A **pre token generation Lambda trigger** can add enterprise claims to the token.

Behind both sits **AWS STS**, the Security Token Service, which mints the temporary credentials through `AssumeRole`, `AssumeRoleWithSAML` and `AssumeRoleWithWebIdentity`. **CloudTrail** records every sign-in and every API call for the audit requirement.

The recurring wrong answers are:

- A **Lambda** authorizer that checks an LDAP directory and issues its own **JWTs**. It is custom, unaudited, and **JWTs** it mints cannot call **Bedrock**.
- **IAM** users per employee with **Secrets Manager** rotation.
- `AssumeRole` federation seeded with stored user credentials.
- **AWS Organizations** cross-account roles presented as an identity solution.

Two more identity services appear at the edges.

**Amazon Bedrock AgentCore Identity** authenticates callers of an agent. Configure the corporate **OIDC** provider as the **inbound** authorizer and list the application's client ID as an **allowed audience**, and the runtime rejects any token whose audience does not match. The same agent configuration also carries model settings, such as the maximum tokens for a response.

**Amazon Verified Permissions** evaluates fine-grained application authorization, such as "this user may run this operation on data of this classification", with **Cedar** policies once the user is authenticated.

## Fine-grained data access with Lake Formation

**IAM** and bucket policies work at the level of buckets and objects. Regulated datasets need "this study team may read these tables, but not these columns, and only these rows", and managing that with dozens of bucket policies does not scale.

**AWS Lake Formation** is the governance layer for data in **S3** that is registered in the **AWS Glue Data Catalog**, the central metadata store of databases, tables and columns that **Glue** crawlers populate. **Lake Formation** adds its own grant-and-revoke permission model on top of **IAM**:

- **Database, table, column, row and cell-level** permissions.
- **Data filters** for row and cell security.
- **LF-Tags** for tag-based access control. Grant "clinical-study = A" once, and every table or column carrying that tag follows.

Permissions are enforced by the analytics and ML services that read through the catalog: **Amazon Athena** (serverless SQL over **S3**), **Amazon Redshift Spectrum** (**Redshift** queries over **S3** data), **Amazon EMR** (managed **Spark** and **Hadoop** clusters), **AWS Glue** ETL and **QuickSight**, and by **SageMaker** when it reads through those paths. Every access is logged through **CloudTrail**.

**Hybrid access mode** lets you adopt **Lake Formation** table by table while **IAM** policies keep working elsewhere, and cross-account sharing grants another account or organisation access to specific catalog resources.

When a question describes many groups needing different column-level views of **S3**-backed datasets, automatic encryption, centralised auditing and "no manual management of bucket policies per group", **Lake Formation** is the answer. **Cognito** identity pools, tag-based bucket policies with **CloudTrail**, and one **S3 Access Point** per study are the manual alternatives.

## Encryption and key management

**AWS Key Management Service (KMS)** creates and controls the keys that encrypt data at rest, backed by FIPS 140-3 validated hardware. Three kinds of key appear in questions.

- **AWS owned keys** belong to the service and cost nothing. You see nothing and control nothing.
- **AWS managed keys** (`aws/s3`, `aws/sagemaker`) live in your account, are used only by that service, and rotate automatically. You can audit their use but not change their policy.
- **Customer managed keys** are yours. You write the **key policy**, which sets who may use and administer the key, enable annual **automatic rotation** or rotate manually, create **grants** so a service can use the key on your behalf, and can disable or delete them. That is why "keys owned by the company" or "customer-controlled encryption" means a customer managed key.

**Multi-Region keys** replicate a key across Regions, so data encrypted in one Region can be decrypted in another.

**Bedrock** resources you can encrypt with a customer managed key include:

- **Custom models** produced by customisation jobs.
- **Agents**.
- **Knowledge-base data ingestion**, meaning the transient data during indexing, and the **S3** data sources themselves through **SSE-KMS**.
- **Model evaluation jobs**.
- **Guardrails**.
- The vector store: **OpenSearch** collections with **KMS**, or the **AWS Secrets Manager** secret that holds credentials for a third-party store.

**SageMaker** encrypts notebook and training volumes, model artifacts and endpoint storage with **KMS** keys you name.

**S3** buckets should default to **SSE-KMS**, which is server-side encryption with **KMS** keys, using a customer managed key when a question stresses ownership. Use **SSE-S3**, server-side encryption with keys **S3** manages, when it only says "encrypted at rest with AWS-managed keys". **AWS Certificate Manager** issues the TLS certificates for encryption in transit at load balancers, **API Gateway** and **CloudFront**, the content delivery network.

## Monitoring access

Protection you cannot see is not protection. **AWS CloudTrail** records API calls in two categories.

- **Management events** are control-plane actions such as `CreateModelCustomizationJob` and `CreateAgent`, and, for **Bedrock**, the inference calls `InvokeModel`, `InvokeModelWithResponseStream`, `Converse` and `ConverseStream`.
- **Data events** are high-volume data-plane actions, off by default, that you enable with event selectors: **S3** object reads and writes, and for **Bedrock** `InvokeAgent`, `Retrieve`, `RetrieveAndGenerate`, `InvokeFlow` and `RenderPrompt`.

A multi-Region trail delivered to a locked-down **S3** bucket is the audit record. **CloudTrail Lake** adds SQL queries over events and long retention, but it has been closed to new customers since May 2026, so **Amazon Athena** over the trail bucket is the durable pattern.

**Amazon CloudWatch** holds the metrics and logs:

- Metrics for **Bedrock** invocation counts, latency, throttles and token counts, guardrail interventions, and **SageMaker** endpoint metrics.
- **CloudWatch Logs Insights** queries the logs, answering who accessed which dataset and which prompts were blocked.
- **Metric filters** turn log patterns into metrics.
- **Alarms** and **anomaly detection**, a model of each metric's normal band that alarms on deviations, flag unusual access patterns.
- **Dashboards** give the compliance view.

**VPC Flow Logs** record network flows for the network layer.

Around them sit the security services you should be able to name in one line each:

- **Amazon GuardDuty** is threat detection over **CloudTrail**, **VPC Flow Logs**, DNS logs and **S3** events, catching compromised credentials, exfiltration and malware.
- **AWS Security Hub** aggregates findings from **GuardDuty**, **Macie**, **Inspector**, **Config** and partners, and scores accounts against standards.
- **AWS Config** records resource configurations and evaluates rules, for example that **SageMaker** notebooks have no direct internet access or that buckets block public access.
- **Amazon Inspector** scans **EC2**, **Lambda** and container images for vulnerabilities.
- **Amazon Macie** discovers sensitive data in **S3**, covered in unit 03.

None of these replaces the three basics a **Bedrock** deployment needs: **IAM** for access control, **CloudTrail** for the audit trail, and **CloudWatch** for monitoring and alerting.

The composite answer for "isolated environment, governed data access, monitored read and write activity, least privilege, no exfiltration" is therefore **VPC endpoints** for **Bedrock** and **S3** traffic, **IAM** plus **Lake Formation** for fine-grained permissions, and **CloudWatch**, with **CloudTrail** behind it, for monitoring and auditing across the workflow. A public subnet with restrictive security groups, **API Gateway** throttling as an access control, or network isolation without any permission model each leaves a wall missing.

## Worked scenario

A hospital network builds an analytics platform where data scientists train models in **SageMaker** and clinicians query a **Bedrock** assistant over de-identified notes. The security office requires no internet exposure, least privilege everywhere, per-study data access, company-owned encryption keys, and a complete audit trail. Two partner clinics will use the assistant through their own applications.

The network is closed first. **SageMaker Studio** runs in **VPC-only mode** in private subnets, with interface endpoints for the **SageMaker** API, runtime and **Studio**, a gateway endpoint for **S3**, and interface endpoints for **Bedrock** runtime, **Comprehend** and **KMS**. There is no NAT gateway. Training jobs run with **network isolation**, distributed jobs enable **inter-container traffic encryption**, and endpoint policies plus security groups restrict who may use each endpoint. **S3** bucket policies accept requests only through the **VPC endpoint**.

Identity follows the roles-not-users rule.

- Each data scientist's notebook is reachable only by their own **IAM** policy scoped to that notebook's ARN, and execution roles get read on the study buckets and write on the artefact bucket, nothing else.
- Clinicians sign in through **IAM Identity Center**, federated to the hospital's **SAML** identity provider with **SCIM** provisioning and permission sets per role.
- The partner clinics' applications authenticate through **Amazon Cognito** with **OIDC** federation to their identity providers, exchanging tokens for temporary credentials.
- Study-level access to the de-identified datasets is governed by **AWS Lake Formation**: tables registered in the **Glue Data Catalog**, column-level permissions per study group, **LF-Tags** for the sensitivity class, and no per-group bucket policies to maintain.

Encryption uses customer managed **KMS** keys on the **S3** buckets, the **SageMaker** volumes and artefacts, the **Bedrock** knowledge base ingestion and the guardrail configuration, with key policies limiting administration to the security team.

**CloudTrail** records every API call, with data events enabled for **S3** objects and for the knowledge base and agent calls. **CloudWatch** alarms and anomaly detection watch access patterns, and **GuardDuty**, **Macie** and **Config** findings roll up in **Security Hub**.

A question built on this scenario asks for the combination that isolates, governs and monitors with least privilege. The answer names **VPC endpoints**, **IAM** and **Lake Formation**, and **CloudWatch** with **CloudTrail** behind it.

## Exam lens

- "No traffic leaves the AWS network, no internet, no public IPs, simplest" → **SageMaker** in private subnets with **VPC** interface endpoints for **SageMaker** and other services, and a gateway endpoint for **S3**. Never a NAT gateway, proxy, internet gateway or peering.
- "Studio accesses **S3** over public endpoints" → **Studio** in **VPC-only mode** plus an **S3** gateway endpoint.
- "Only approved instances and principals may use the **SageMaker** **VPC** endpoint" → an **endpoint policy** for the principals, and a **security group** on the endpoint for the instances.
- "Distributed training, encrypt at rest and in transit, node traffic secure, never the public internet" → a **VPC** with **inter-container traffic encryption**, an **S3 VPC endpoint** with endpoint and bucket policies, and **PrivateLink** interface endpoints for other services.
- "Notebook reads one bucket, writes another, least privilege, AWS-native" → an **IAM** policy on the **SageMaker** execution role scoped to those buckets.
- "Each developer only their own notebook, shared **Rekognition** and data lake" → a per-developer **IAM** policy on the notebook instance ARN.
- "Corporate IdP, temporary access, audit logs, no long-lived credentials" → **IAM Identity Center** with **SAML** federation and permission sets for the workforce, and **Cognito** with **OIDC** federation exchanging tokens for temporary credentials for applications. **Entra ID** with **Identity Center** means **SAML** plus **SCIM**, not **OIDC**.
- "Agent must validate inbound OIDC tokens and audience" → **AgentCore Identity** with an inbound **OIDC** provider and the application ID as allowed audience.
- "Column-level, per-study access to **S3** datasets, central governance and audit, no per-group bucket policies" → **Lake Formation**.
- "Training data and fine-tuned artifacts encrypted with company-owned keys, full API auditability, latency and throughput visibility" → **SSE-KMS** customer managed keys, a **Bedrock** custom model with a customer managed key, **CloudTrail**, and **CloudWatch** metrics.
- "Isolated, governed, monitored end to end" → **VPC endpoints** plus **IAM** and **Lake Formation** plus **CloudWatch**.

## Knowledge check

<!-- KC: E2-Q18, E2-Q22, E2-Q63, E2-Q36, E2-Q56, E2-Q21, E2-Q35, E3-Q47, E1-Q7, PQ-Q20, E3-Q55, E3-Q50, E3-Q33, E1-Q5 -->
<!-- KC-BEGIN -->
### 1. Exam 2, question 18

A global retail organization needs to analyze sensitive customer feedback data using Amazon SageMaker AI notebooks and Amazon Comprehend. Customer review datasets are stored in Amazon S3, and all processing must occur inside a fully isolated VPC. The security team mandates that:

- No traffic may leave the AWS network
- No outbound internet access is allowed
- All service-to-service communication must use private connectivity
- SageMaker notebooks must not use public IPs

The company wants the simplest architecture that enforces these controls with minimal operational overhead.

Which solution meets these requirements?

- **A)** Deploy the SageMaker AI notebook in a private subnet with a route to an internet gateway and send S3 traffic through an external proxy for monitoring.
- **B)** Deploy the SageMaker AI notebook in a private subnet and use a NAT gateway to provide outbound internet access for S3 requests restricted to specific buckets.
- **C)** Deploy the SageMaker AI notebook in a private subnet within a VPC and ensure that the VPC has private endpoints for both SageMaker AI and S3.
- **D)** Deploy the SageMaker AI notebook in a private subnet and create a VPC peering connection to another VPC where S3 is accessible.

<details><summary>Answer</summary>

**Answer: C.** A SageMaker notebook in a private subnet with VPC interface endpoints for SageMaker and a gateway endpoint for S3 keeps every request on the AWS network with no public IPs and no internet path, and it is the simplest configuration to operate. An internet gateway route or a NAT gateway provides outbound internet access the mandate forbids, an external proxy is more infrastructure and still an internet path, and VPC peering cannot reach S3, which does not live in a VPC.

*Where this is covered: Unit 02, Network isolation. Key: ours, confidence high.*

</details>

### 2. Exam 2, question 22

A digital media company is building a content-personalization engine using Amazon SageMaker AI. The ML models are trained using sensitive clickstream and user-preference data stored in Amazon S3, and real-time inference occurs through a SageMaker endpoint. The company also uses Amazon Comprehend to perform sentiment analysis on user comments to enrich the recommendation features.

For strict compliance reasons, the entire solution must operate fully inside a private VPC, prevent all outbound internet access, and allow SageMaker to communicate with Comprehend securely without using public endpoints. The engineering team wants the simplest managed approach that meets these requirements.

Which solution will satisfy the requirements with the least development effort?

- **A)** Activate SageMaker AI network isolation mode to block all external access and create an Amazon Comprehend VPC endpoint inside the same VPC so the model can call Comprehend privately.
- **B)** Deploy SageMaker AI in VPC-only mode and set up an internet gateway with a tightly restricted security group to limit outbound access but still reach Comprehend.
- **C)** Configure SageMaker AI in VPC-only mode, attach a restrictive NACL to block internet access, and allow traffic to the public Comprehend endpoint.
- **D)** Place SageMaker AI in VPC-only mode and create a VPC peering connection to another VPC hosting Comprehend, routing all inference calls through the peered network.

<details><summary>Answer</summary>

**Answer: A.** SageMaker network isolation blocks all external access from the training and inference containers, and a Comprehend interface VPC endpoint in the same VPC gives a private path to Comprehend without public endpoints, which is the managed way to meet the no-internet requirement. Strictly, a network-isolated container cannot make any outbound call itself, so the Comprehend call would come from the surrounding application over the endpoint, but the other options are clearly wrong: an internet gateway and a public Comprehend endpoint violate the no-internet rule, and Comprehend is a regional service that cannot be hosted in a peered VPC.

*Where this is covered: Unit 02, Network isolation. Key: ours, confidence medium.*

</details>

### 3. Exam 2, question 63

A financial analytics company uses Amazon SageMaker Studio notebooks and SageMaker Autopilot to train models on sensitive customer data stored in Amazon S3. Compliance policies require that all data transfers between SageMaker and S3 stay entirely within the AWS private network.

During an audit, the security team finds that the Studio domain is accessing S3 over public endpoints. The engineering team must update the architecture so that Studio notebooks, Autopilot jobs, and processing workloads all communicate with S3 only through private connectivity, without affecting existing workflows.

Which configuration should the team implement?

- **A)** Enable AWS PrivateLink for S3 using an interface endpoint and update the Studio domain to route traffic privately.
- **B)** Create a restricted public S3 Access Point that only allows requests from the SageMaker execution role.
- **C)** Configure SageMaker Studio to run inside a private VPC and create a VPC Gateway Endpoint for S3 so all SageMaker–S3 traffic stays on the AWS private network.
- **D)** Enable internet access for SageMaker Studio and use AWS Key Management Service (KMS) to encrypt all SageMaker–S3 transfers.

<details><summary>Answer</summary>

**Answer: C.** Running SageMaker Studio in VPC-only mode inside a private VPC and adding a VPC gateway endpoint for S3 routes all Studio, Autopilot and processing traffic to S3 over the AWS private network without changing the workflows. An S3 interface endpoint also works but is the costlier choice where a gateway endpoint exists, a public S3 Access Point still uses public endpoints, and enabling internet access with KMS encryption leaves the transfers on the public path.

*Where this is covered: Unit 02, Network isolation. Key: ours, confidence high.*

</details>

### 4. Exam 2, question 36

A security-focused ML engineering team is building a controlled workflow that uses Amazon SageMaker AI for model training and Amazon Comprehend for entity extraction. The workflow is orchestrated with AWS Step Functions and triggered using Amazon EventBridge rules. Because the environment processes regulated customer data, all SageMaker API calls must remain private and must only be allowed from a small group of approved EC2 instances and IAM identities.

To meet these requirements, the team provisions a VPC interface endpoint for the SageMaker Service API in a dedicated subnet. They now need to ensure that only the approved compute instances and authorized IAM principals can send requests through this endpoint and that the endpoint cannot be accessed broadly across the VPC.

Which combination of actions will correctly enforce these access restrictions? (Select TWO.)

- **A)** Enable private DNS on the VPC endpoint to route SageMaker traffic internally.
- **B)** Attach a custom VPC endpoint policy that explicitly grants SageMaker access only to approved IAM users and roles.
- **C)** Configure the security group associated with the endpoint’s network interface to allow inbound traffic only from the specific EC2 instances that require SageMaker access.
- **D)** Deploy an additional VPC endpoint for SageMaker AI Runtime to isolate inference-related operations.
- **E)** Enable VPC Flow Logs and trigger an AWS Lambda function to automatically block suspicious or unauthorized API calls.

<details><summary>Answer</summary>

**Answer: B, C.** A custom VPC endpoint policy restricts which IAM principals may call SageMaker through the endpoint, and the security group on the endpoint's network interface restricts which EC2 instances can send traffic to it, which together limit the endpoint to approved compute and identities. Private DNS only changes name resolution, a second endpoint for the runtime does not restrict access, and Flow Logs with a Lambda function react after the fact rather than enforcing.

*Where this is covered: Unit 02, Network isolation. Key: ours, confidence high.*

</details>

### 5. Exam 2, question 56

A global e-commerce enterprise is building an intelligent natural language processing (NLP) system to enhance its customer engagement platform, TD-Assistance. The company uses Amazon Bedrock to access a foundation model for generative conversational responses and Amazon SageMaker AI to fine-tune a BERT-based model on proprietary chat transcripts for sentiment and intent analysis.

The training dataset, which contains sensitive customer messages, is stored in an Amazon S3 bucket. To improve performance, the SageMaker training job is configured for distributed training across five compute instances.

The data science team must encrypt the dataset, model checkpoints, and intermediate artifacts both at rest and in transit. Additionally, all node communications must be secure, and data transfers should never traverse the public internet.

Which combination of actions will meet these security and compliance requirements for the distributed training workload? (Select THREE.)

- **A)** Deploy the distributed training jobs in a restricted VPC environment with inter-container traffic encryption enabled.
- **B)** Provision an S3 VPC endpoint to isolate network traffic and apply fine-grained endpoint and S3 bucket access policies.
- **C)** Deploy an AWS Network Firewall in the VPC to inspect and filter traffic between SageMaker containers during training.
- **D)** Create AWS PrivateLink interface VPC endpoints to route training data and model checkpoints to S3 and internal services.
- **E)** Attach a SageMaker execution role with read-only access rights to required resources in the training environment.
- **F)** Configure the network security group (NSG) to accept inbound communication originating from peer training containers.

<details><summary>Answer</summary>

**Answer: A, B, D.** Running the distributed training job in a restricted VPC with inter-container traffic encryption protects data in transit between the five instances, an S3 VPC endpoint with endpoint and bucket policies keeps dataset and checkpoint traffic off the public internet and scoped, and PrivateLink interface endpoints give the same private path to S3 and the other AWS services the job calls. Network Firewall inspection between containers is unnecessary, a read-only role cannot write checkpoints, and hand-editing security-group rules for peer containers is not the AWS-native control (SageMaker requires the training security group to allow traffic between its own members, but that is configuration, not the encryption and isolation the question asks for).

*Where this is covered: Unit 02, Network isolation. Key: ours, confidence medium.*

</details>

### 6. Exam 2, question 21

A multinational electronics marketplace is developing a custom multilingual catalog-generation system using Amazon Titan Text on Amazon Bedrock. To improve accuracy for highly specialized product categories, the company plans to fine-tune the Titan model in Amazon SageMaker AI using proprietary product specifications stored in Amazon S3. All training data and fine-tuned artifacts must be encrypted with AWS KMS keys owned by the company.

Once deployed, the Bedrock-hosted model must support full API auditability, and the operations team needs continuous insight into latency and throughput across the company’s active regions in North America and Europe. The solution must minimize custom infrastructure and rely on managed observability wherever possible.

Which architecture meets these security, compliance, and observability requirements?

- **A)** Fine-tune the Titan model in SageMaker AI with SSE-S3 encryption and place an API Gateway proxy in front of Bedrock to capture logs, using Amazon Macie to detect sensitive data in inference requests.
- **B)** Fine-tune the Titan model in SageMaker AI using training data stored in Amazon S3 with KMS encryption, deploy the model through Bedrock using a customer-managed KMS key, enable AWS CloudTrail for all Bedrock API calls, and use Amazon CloudWatch metrics to monitor model latency and throughput across regions.
- **C)** Train Titan entirely within SageMaker AI on EBS volumes encrypted with default keys, deploy the model to a custom EC2 inference cluster, and store API logs manually in Amazon DynamoDB for compliance.
- **D)** Deploy the base Titan model directly on Bedrock without fine-tuning, restrict access through IAM conditions, and rely solely on CloudTrail logs for Bedrock usage visibility.

<details><summary>Answer</summary>

**Answer: B.** Fine-tuning in SageMaker on S3 data encrypted with the company's KMS keys, deploying the resulting model through Bedrock with a customer managed KMS key, enabling CloudTrail for every Bedrock API call and using CloudWatch metrics for latency and throughput per Region meets the ownership, auditability and observability requirements with managed services only. SSE-S3 uses AWS-owned keys, an API Gateway proxy with Macie adds infrastructure and misuses Macie, an EC2 inference cluster with DynamoDB logs is custom everything, and skipping fine-tuning ignores the accuracy requirement.

*Where this is covered: Unit 02, Encryption and key management. Key: ours, confidence high.*

</details>

### 7. Exam 2, question 35

A healthcare AI team is developing a medical-image classification pipeline using Amazon SageMaker AI. Training data is stored in one Amazon S3 bucket, while model artifacts and evaluation metrics must be written to a second S3 bucket. Due to strict compliance rules (HIPAA and internal security policies), the SageMaker notebook environment must use least-privilege access and may not rely on public access points or temporary federation mechanisms.

The team needs a secure method that allows the SageMaker notebook to read training data and write model outputs to the designated S3 buckets, while ensuring all permissions are tightly scoped and managed through AWS-native access controls.

Which approach should the team implement?

- **A)** Use an S3 Access Point configured for open access and associate it with the SageMaker notebook to simplify bucket permissions.
- **B)** Configure IAM identity federation for the SageMaker notebook so that it assumes an external federated role to access the S3 buckets.
- **C)** Create an S3 bucket policy that allows unrestricted access for the SageMaker notebook ARN to retrieve and write objects.
- **D)** Attach an IAM policy to the SageMaker execution role that grants s3:GetObject, s3:PutObject, and s3:ListBucket permissions for only the required S3 buckets.

<details><summary>Answer</summary>

**Answer: D.** Attaching an IAM policy to the SageMaker execution role that grants s3:GetObject, s3:PutObject and s3:ListBucket only on the two required buckets is least privilege through AWS-native access control with no public access points or federation. An open-access S3 Access Point and an unrestricted bucket policy violate least privilege, and identity federation for a notebook is both unnecessary and excluded by the requirements.

*Where this is covered: Unit 02, Identity: who may call the model and read the data. Key: ours, confidence high.*

</details>

### 8. Exam 3, question 47

A global insurance provider runs a fraud-analytics platform using Amazon SageMaker AI for feature engineering and model development, and Amazon Rekognition to validate customer identity documents submitted during claims processing. Each data scientist is assigned their own isolated SageMaker notebook instance to comply with internal compliance and audit requirements. All developers must share access to Amazon Rekognition and a centralized Amazon S3 data lake, but no developer should be able to start, stop, or connect to a notebook instance assigned to another user.

The security engineering team must enforce strict least-privilege access, prevent cross-notebook access, and avoid introducing any custom authorization service or additional infrastructure. Which approach provides the correct enforcement model?

- **A)** Configure SageMaker lifecycle configurations to prevent users from attaching to notebook instances owned by other developers.
- **B)** Use a shared SageMaker notebook instance for all developers and control access by configuring JupyterLab workspace-level permissions.
- **C)** Enable VPC Security Group isolation around each notebook instance to implicitly restrict which developer can connect to each instance.
- **D)** Create an IAM policy for each developer that grants SageMaker permissions only on the ARN of their assigned notebook instance while allowing shared access to Rekognition APIs and the central S3 data lake.

<details><summary>Answer</summary>

**Answer: D.** An IAM policy per developer that allows SageMaker notebook actions only on the ARN of that developer's notebook instance, while granting shared access to Rekognition and the central S3 data lake, enforces least privilege and prevents cross-notebook access with no extra service. Lifecycle configurations run scripts on the instance rather than authorising users, a shared instance with workspace permissions violates the isolation requirement, and security groups control network reachability rather than which IAM identity may start or open a notebook.

*Where this is covered: Unit 02, Identity: who may call the model and read the data. Key: ours, confidence high.*

</details>

### 9. Exam 1, question 7

A healthcare analytics company is integrating a third-party clinical decision support tool with Amazon Bedrock. The company requires secure authentication that works with its existing corporate identity provider (IdP). The solution must provide temporary, short-lived access to Amazon Bedrock, remove the need for storing long-term credentials, and generate comprehensive audit logs of all authentication and Bedrock API calls. The company also wants a fully managed approach that minimizes custom authentication code.

Which solutions will meet these requirements? (Select TWO.)

- **A)** Deploy AWS IAM Identity Center with SAML federation to the corporate IdP. Configure permission sets that grant Bedrock access for authenticated sessions.
- **B)** Create an IAM role and configure AWS STS AssumeRole federation, storing long-term IAM user credentials in the application configuration.
- **C)** Implement an OpenID Connect (OIDC) integration with Amazon Cognito. Configure the integration to authenticate users through the corporate IdP and exchange tokens for temporary AWS credentials that allow access to Amazon Bedrock.
- **D)** Configure an API Gateway Lambda authorizer that validates credentials against the corporate LDAP directory and issues custom JWTs for Bedrock access.
- **E)** Create IAM users for each analyst and rotate credentials by using AWS Secrets Manager. Assign fine-grained access through IAM policies.

<details><summary>Answer</summary>

**Answer: A, C.** IAM Identity Center with SAML federation to the corporate IdP and permission sets gives workforce users temporary, role-based Bedrock access with CloudTrail audit and no custom code, and Amazon Cognito with OIDC federation to the IdP exchanges tokens for temporary AWS credentials for application users. Storing long-term IAM user credentials, an LDAP-checking Lambda authorizer issuing custom JWTs, and IAM users with rotated keys all keep long-lived secrets or custom authentication code.

*Where this is covered: Unit 02, Identity: who may call the model and read the data. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 10. Official practice question set, question 20

A company needs secure authentication for a third-party application that uses Amazon Bedrock. The solution must integrate with the company's existing identity provider (IdP). The solution must maintain comprehensive audit logs of authentication and API calls. The solution must eliminate long-lived credentials and provide temporary access to Amazon Bedrock.

Which solutions will meet these requirements? **(Select TWO)**

- **A)** Implement an OpenID Connect (OIDC) integration with Amazon Cognito. Configure the integration to authenticate users through the IdP and exchange tokens for temporary AWS credentials. Configure the integration to allow the application to access Amazon Bedrock.
- **B)** Create IAM users for each employee that needs access to the application. Assign permissions through IAM policies. Implement credential rotation by using AWS Secrets Manager.
- **C)** Configure an Amazon API Gateway Lambda authorizer. Configure the authorizer to validate credentials against the company's LDAP server and then issue signed JSON Web Tokens (JWTs) for Amazon Bedrock access.
- **D)** Create an IAM role and configure federation by using AWS STS `AssumeRole` API calls. Store the application's IAM user credentials in the application configuration.
- **E)** Deploy AWS IAM Identity Center with SAML federation to the IdP. Configure custom permission sets that grant access to Amazon Bedrock.

<details><summary>Answer</summary>

**Answer: A, E.** Cognito with OIDC integration authenticates users through the existing IdP and exchanges tokens for temporary AWS credentials that the third-party application uses for Bedrock, and IAM Identity Center with SAML federation and custom permission sets does the same for federated workforce access; both remove long-lived credentials and are logged by CloudTrail. IAM users with rotated secrets are still long-lived credentials, a Lambda authorizer issuing its own JWTs cannot grant Bedrock access and is unaudited custom code, and AssumeRole seeded with stored IAM user credentials keeps a permanent secret in the configuration.

*Where this is covered: Unit 02, Identity: who may call the model and read the data. Key: AWS official answer.*

</details>

### 11. Exam 3, question 55

A global insurance provider is modernizing its GenAI platform that combines Amazon Bedrock for LLM inference and Amazon SageMaker AI for model customization. The company mandates strict role-based access control so only authorized data scientists, analysts, and operations engineers can use these services.

The enterprise already uses Microsoft Entra ID as its centralized identity provider and wants AWS access to be federated through Entra ID without creating IAM users. The solution must provide centralized identity lifecycle management and enforce fine-grained permissions for Bedrock and SageMaker AI.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create IAM users for all employees and manage password policies through Entra ID pass-through authentication. Attach Bedrock and SageMaker policies directly to each IAM user.
- **B)** Implement SAML 2.0 federation between Entra ID and AWS IAM by mapping Entra ID security groups to IAM roles that contain scoped permissions for Bedrock and SageMaker AI.
- **C)** Set up AWS IAM Identity Center with Microsoft Entra ID as an external identity provider. Use SCIM provisioning and IAM Identity Center permission sets to grant role-based access to Bedrock and SageMaker AI.
- **D)** Use AWS IAM Identity Center with an OpenID Connect (OIDC) provider configuration for Entra ID authentication and assign permission sets for Bedrock and SageMaker access.
- **E)** Develop a custom identity proxy service that authenticates to Entra ID, exchanges tokens through a Lambda authorizer, and injects AWS temporary credentials for Bedrock and SageMaker operations.

<details><summary>Answer</summary>

**Answer: B, C.** IAM Identity Center with Microsoft Entra ID as the external identity provider, SCIM provisioning for user and group lifecycle and permission sets for role-based Bedrock and SageMaker access is the recommended design, and direct SAML 2.0 federation from Entra ID to IAM roles mapped from security groups is the valid alternative that also avoids IAM users. Identity Center accepts external identity providers over SAML 2.0 with SCIM, not OIDC, so the OIDC option is wrong; IAM users with pass-through passwords and a custom identity proxy contradict the centralised, managed requirement.

*Where this is covered: Unit 02, Identity: who may call the model and read the data. Key: ours, confidence medium.*

</details>

### 12. Exam 3, question 50

A global insurance provider is deploying an internal GenAI assistant using Amazon Bedrock AgentCore Runtime to help policy specialists summarize claim files, validate coverage rules, and generate multilingual customer explanations using Amazon Translate and Amazon SageMaker AI. The company requires strict access control: only employees authenticated through the corporate OIDC identity provider may use the agent. Security teams mandate that AgentCore must validate inbound OIDC tokens and allow requests only when the token’s audience matches the registered internal application ID. The engineering team also wants to reduce generation costs by configuring the agent’s maximum tokens setting to limit output length and prevent overly long responses.

Which configuration satisfies these requirements MOST effectively?

- **A)** Use Amazon Cognito user pools as a proxy identity provider and map the application ID for audience enforcement while leaving the maximum tokens setting unmanaged.
- **B)** Integrate the OIDC IdP only for outbound authentication from AgentCore, and rely on IAM permissions to validate inbound requests.
- **C)** Configure AgentCore Identity as an inbound OIDC provider, specify the internal application ID as an allowed audience, and set a maximum tokens value to enforce response length limits.
- **D)** Use SigV4-only request signing for all AgentCore Runtime calls and disable external identity providers to simplify authentication.

<details><summary>Answer</summary>

**Answer: C.** Configuring AgentCore Identity with the corporate OIDC provider as the inbound authorizer and the internal application ID as an allowed audience makes the runtime reject tokens whose audience does not match, and setting a maximum tokens value on the agent caps response length and cost. Cognito as a proxy identity provider adds a hop and leaves the token setting unmanaged, outbound-only integration does not validate inbound requests, and SigV4-only signing disables the external identity provider the requirement mandates.

*Where this is covered: Unit 02, Identity: who may call the model and read the data. Key: ours, confidence high.*

</details>

### 13. Exam 3, question 33

A medical research institute is developing an AI platform that processes sensitive patient ECG scans, radiology images, and physician notes. The system uses Amazon Textract and Amazon Rekognition to extract insights before sending the data to analytics models hosted on Amazon Bedrock. All datasets are stored in Amazon S3, but researchers and AI workflows must only access the specific datasets relevant to their assigned clinical studies. Compliance officers require a unified governance layer that supports fine-grained dataset permissions, column-level restrictions, automatic encryption, and centralized auditing. The institute wants to avoid manually managing dozens of S3 bucket policies or IAM configurations for every study group.

Which solution best satisfies these requirements?

- **A)** Configure Amazon Cognito identity pools to authenticate researchers and issue temporary credentials used for restricted S3 access.
- **B)** Use AWS Lake Formation to define table- and column-level access controls for S3-backed datasets, centralize governance policies, and audit all access through built-in logging.
- **C)** Apply tag-based S3 bucket policies to segregate medical datasets and rely on CloudTrail logs to audit all researcher interactions.
- **D)** Create S3 Access Points for each clinical study and attach IAM policies to enforce dataset-level separation and researcher permissions.

<details><summary>Answer</summary>

**Answer: B.** AWS Lake Formation provides table- and column-level (and row- and cell-level) permissions on S3-backed datasets registered in the Glue Data Catalog, centralises the governance policies for every study group, works with encrypted data and logs all access through CloudTrail, which removes the need to manage bucket policies or IAM configurations per group. Cognito identity pools only issue credentials, tag-based bucket policies with CloudTrail are exactly the manual approach the institute wants to avoid, and one S3 Access Point per study still means dozens of policies and no column-level control.

*Where this is covered: Unit 02, Fine-grained data access with Lake Formation. Key: ours, confidence high.*

</details>

### 14. Exam 1, question 5

A financial compliance analytics firm is deploying a foundation-model-powered document review system using Amazon Bedrock and Amazon SageMaker AI. The system processes confidential regulatory filings stored in an internal data lake. Because the documents contain sensitive information, the security team requires end-to-end environmental protection: the FM must run in an isolated environment with no public internet exposure, access to data must be fully governed, and all read/write activity must be monitored for unauthorized access attempts. The firm wants a secure architecture that enforces least privilege, prevents accidental data exfiltration, and provides continuous visibility into data-access behavior.

Which solution BEST ensures a protected AI environment for this deployment?

- **A)** Use API Gateway with request throttling to restrict access to the model and store compliance documents in encrypted S3 buckets without additional access-control layers.
- **B)** Deploy the FM in a public subnet with security groups that block outbound access, and store data in S3 with default bucket policies while using CloudTrail for auditing.
- **C)** Use VPC endpoints to isolate all Bedrock and S3 traffic, enforce least-privilege access using IAM and Lake Formation for fine-grained permissions, and use CloudWatch to monitor and audit data-access patterns across the entire workflow.
- **D)** Enable network isolation in SageMaker AI and store all documents in a private S3 bucket without configuring Lake Formation or IAM resource policies.

<details><summary>Answer</summary>

**Answer: C.** VPC endpoints keep all Bedrock and S3 traffic off the public internet, IAM together with Lake Formation enforces least privilege down to column and row level, and CloudWatch (with CloudTrail behind it) monitors and audits data-access patterns across the workflow, which covers isolation, governance and continuous visibility. API Gateway throttling is not access control, a public subnet is not isolation and default bucket policies are not governance, and network isolation without Lake Formation or resource policies leaves data access ungoverned.

*Where this is covered: Unit 02, Monitoring access. Key: ExamPro answer key (Exam 1 graded).*

</details>

<!-- KC-END -->

## Summary

**Bedrock** never trains on your data or shares it with providers, keeps zero retention and zero operator access by default, and encrypts in transit. The rest is yours.

Keep traffic private with interface endpoints for **Bedrock**, **SageMaker** and the other services, and a gateway endpoint for **S3**, narrowed by endpoint policies and security groups. Put **SageMaker** in **VPC-only mode**, or use **network isolation** and inter-container encryption for distributed training, and never a NAT, proxy or peering shortcut.

Grant access through roles scoped to resource ARNs and conditions. Federate workforce users through **IAM Identity Center**, with **SAML** plus **SCIM** and permission sets, and application users through **Cognito**, with **OIDC** and temporary credentials. Use **Lake Formation** for column- and row-level control over cataloged **S3** data.

Encrypt with customer managed **KMS** keys where ownership matters, and prove it all with **CloudTrail** management and data events, **CloudWatch** metrics, **Logs Insights** and alarms.
