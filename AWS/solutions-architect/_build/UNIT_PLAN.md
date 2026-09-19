# Unit plan

Every file to be written under `aws/solutions-architect/services/`, with the
services it teaches and its depth tier. This file is authoritative. Filenames
here are the filenames on disk, and cross-unit links must match them exactly.

## How the tier was chosen

The "Lesson signal" column is the number of lessons each service has in the two
video courses the reader is working through, written as `Associate / Professional`.
"n/a" means the service does not appear in that course. "Done" means the reader
finished that module. These numbers, plus the two exam guides, set the tier.

| Tier | Body words | Quiz | Assigned when |
|---|---|---|---|
| XL | 10,000 to 13,000 | 12 | The largest modules in either course |
| L | 6,000 to 8,000 | 10 | Roughly 50 to 190 lessons in either course, or core to both exams |
| M | 3,500 to 5,000 | 8 | Roughly 25 to 49 lessons, or core to one exam |
| S | 1,800 to 3,000 | 6 | Roughly 6 to 24 lessons |
| XS group | 2,500 to 5,000 per file | 6 to 8 | Five lessons or fewer each, several services in one file |

Totals: 70 service units, roughly 296,000 words, roughly 560 questions.

Some rows give a prose signal instead of counts, such as "Exam guides, SAP task
1.1 core". That means the video courses do not have a matching module and the
tier comes from the exam guides alone. Rows with several numbers joined by plus
signs are grouped units, one number per service in listed order.

## Naming the exam guides disagree on

The SAA-C03 guide says **Amazon Quick**. The SAP-C02 guide still says **Amazon
QuickSight**. Every unit that mentions it uses the same one-sentence treatment:
"Amazon Quick, formerly Amazon QuickSight, the serverless business intelligence
service", then the current name only. Verify the current name before writing.
The same rule applies to Amazon Data Firehose, formerly Kinesis Data Firehose,
and Amazon Managed Service for Apache Flink, formerly Kinesis Data Analytics.

## Services that are in scope for only one exam

Say so in one clause where the service is taught, so a reader preparing for one
exam knows whether to spend time on it. Professional-only in the lists captured
in `_build/`: AppSync, SES, Pinpoint, Lightsail, App Runner, AppStream 2.0,
WorkSpaces, Timestream, Managed Blockchain, the whole IoT family, Kendra,
Personalize, Fraud Detector, Managed Service for Apache Flink, Proton, Service
Quotas, Elastic Disaster Recovery, Application Discovery Service, SCT, STS as a
named service, and the CodeSuite developer tools. Associate-only: VMware Cloud on
AWS, Serverless Application Repository, Client VPN, Site-to-Site VPN as separate
entries, Elastic Transcoder as an Associate media entry, Device Farm in the
Associate front-end list. QLDB and AWS Fault Injection Service are on neither
list and are context only.

## 01-storage

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `s3.md` | Amazon S3, S3 Glacier storage classes, S3 Express One Zone, Access Points, Multi-Region Access Points, Object Lambda, Storage Lens, Batch Operations, Transfer Acceleration, Requester Pays, static website hosting, event notifications, Inventory | XL | Done / 335 | Fold in `aws/solutions-architect/s3/README.md`, 12,773 words. Correct anything outdated, especially Reduced Redundancy Storage status, storage class figures, request rates per prefix |
| `ebs.md` | Amazon EBS: volume types gp3, gp2, io1, io2 Block Express, st1, sc1, snapshots, encryption, Multi-Attach, Fast Snapshot Restore, Data Lifecycle Manager, Recycle Bin, Elastic Volumes | M | 15 / 29 | |
| `efs.md` | Amazon EFS: performance modes, throughput modes including Elastic, storage classes including One Zone and Archive, lifecycle management, access points, replication, mount targets, encryption | S | 8 / 8 | |
| `fsx.md` | Amazon FSx for Windows File Server, Lustre, NetApp ONTAP, OpenZFS, plus File Cache | S | 9 / 10 | Include a four-way comparison table: protocol, use case, S3 integration, Multi-AZ, backup |
| `storage-gateway.md` | S3 File Gateway, FSx File Gateway, Volume Gateway cached and stored, Tape Gateway | S | n/a / 16 | Comparison table plus the exam's selection rules |
| `backup-and-disaster-recovery.md` | AWS Backup with plans, vaults, cross-account and cross-Region copy, logically air-gapped vaults, Backup Audit Manager. AWS Elastic Disaster Recovery. The DR strategy reference: backup and restore, pilot light, warm standby, multi-site active-active, RTO and RPO | L | 3 / 3 | This is the DR reference unit both domain guides point to. Include a strategy comparison table and how each service supports DR: S3 CRR, RDS cross-Region replicas, Aurora Global Database, DynamoDB global tables, Route 53 failover and ARC. Also owns DR testing, game days and failure scenario exercises for SAP task 3.1, including AWS Fault Injection Service, which is on neither in-scope list and so is named but not taught in depth. Raised from M because the coverage matrix assigns it the core of two SAP continuity tasks plus Associate DR and backup decisions |
| `snow-family.md` | AWS Snow Family current lineup, device selection by volume and connectivity, transfer time arithmetic against network transfer, edge compute, OpsHub, security | S | 13 / n/a | Verify Snowcone and Snowmobile status before writing either way |
| `transfer-family-and-datasync.md` | AWS Transfer Family for SFTP, FTPS, FTP, AS2 and connectors. AWS DataSync agents, locations, tasks, schedules, cross-cloud. S3 Transfer Acceleration as comparison | S | 5 and 4 / 4 and 4 | Include a "which transfer tool" table covering Transfer Family, DataSync, Snow Family, Storage Gateway, Transfer Acceleration, Direct Connect and plain CLI |

## 02-compute

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `ec2.md` | Amazon EC2: instance families and naming, purchasing options On-Demand, Reserved, Savings Plans, Spot, Dedicated Hosts and Instances, Capacity Reservations, placement groups, ENI, ENA and EFA, instance store compared with EBS, user data and instance metadata with IMDSv2, Nitro, hibernation, instance profiles, Spot Fleet and EC2 Fleet, EC2 Image Builder pointer | L | 61 / 61 | Purchasing options table and instance family table. Also owns the cross-category compute, storage, networking and database selection baseline in SAA task 2.1; compare and cross-link rather than reteaching the other categories |
| `ami.md` | Amazon Machine Images: lifecycle, sharing across accounts and organizations, cross-Region copy, encrypted AMIs and KMS key sharing, deprecation and deregistration, EC2 Image Builder, golden images, immutable infrastructure | S | 4 / 4 | |
| `ec2-auto-scaling.md` | EC2 Auto Scaling: launch templates, groups, health checks, scaling policies target tracking, step, simple, scheduled, predictive, warm pools, lifecycle hooks, instance refresh, mixed instances with Spot. AWS Auto Scaling scaling plans and Application Auto Scaling targets | M | 27 and 4 / 42 | Scaling policy comparison table |
| `elastic-load-balancing.md` | ALB, NLB, Gateway Load Balancer, Classic Load Balancer: listeners and rules, target groups and target types including Lambda and IP, health checks, sticky sessions, cross-zone behavior and pricing, connection draining, TLS termination and SNI, mutual TLS, access logs, WAF integration | M | 15 / 44 | Load balancer comparison table: layer, targets, static IP, TLS, WebSockets, routing, use case |
| `lambda.md` | AWS Lambda: execution model, runtimes, memory and CPU coupling, timeout, concurrency reserved and provisioned, SnapStart, event sources synchronous, asynchronous and event source mapping, destinations, dead-letter queues, layers, versions and aliases, VPC networking, Lambda@Edge compared with CloudFront Functions, pricing | L | 29 / 58 | Invocation model table and concurrency table |
| `elastic-beanstalk.md` | AWS Elastic Beanstalk: environments, platforms, deployment policies all at once, rolling, rolling with additional batch, immutable, traffic splitting, blue/green by CNAME swap, .ebextensions, worker environments | S | 13 / n/a | Deployment policy table with downtime, rollback and cost columns. The exam tests this table directly |
| `batch.md` | AWS Batch: compute environments managed and unmanaged, EC2, Spot with allocation strategies, Fargate and EKS, job queues and priorities, job definitions, array jobs, multi-node parallel jobs, retries and dependencies | S | 4 / n/a | Compare with Lambda's 15 minute limit, Step Functions and EMR |
| `other-compute-and-end-user.md` | Amazon Lightsail, AWS App Runner, Amazon AppStream 2.0, Amazon WorkSpaces, AWS Outposts, AWS Local Zones, AWS Wavelength, AWS Serverless Application Repository, VMware Cloud on AWS | XS group | 2+2+2+2 | Title: "Other compute and end-user computing services". Note per service which exam it is in scope for. Lightsail is out of scope for SAA, in scope for SAP. Verify VMware Cloud on AWS status |

## 03-containers

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `ecs-and-ecr.md` | Amazon ECS: clusters, task definitions, services, launch types EC2, Fargate and External, networking modes, task roles compared with execution roles, service discovery, Service Connect, capacity providers, deployment types including blue/green with CodeDeploy, ECS Anywhere. Amazon ECR: repositories, lifecycle policies, image scanning, cross-Region replication, pull-through cache | M | 36 and 4 / 43 | |
| `eks.md` | Amazon EKS: control plane, node groups managed, self-managed and Fargate, EKS Auto Mode, VPC CNI networking, IAM roles for service accounts and EKS Pod Identity, EBS and EFS CSI drivers, AWS Load Balancer Controller, EKS Anywhere and EKS Distro, when to choose EKS over ECS | M | 27 / 28 | |

## 04-networking

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `vpc.md` | Amazon VPC: CIDR and IP addressing for IPv4 and IPv6, IPAM, BYOIP, subnets and Availability Zones, route tables, internet gateway, egress-only internet gateway, NAT gateway compared with NAT instance, security groups compared with network ACLs, VPC endpoints gateway and interface, PrivateLink and endpoint services, VPC peering, Transit Gateway introduction, VPC Flow Logs, Traffic Mirroring, Reachability Analyzer, Network Access Analyzer, DHCP option sets, Elastic IPs and public IPv4 charges, VPC sharing through RAM, VPC Lattice. Introduce AWS Network Firewall and Route 53 Resolver DNS Firewall in a paragraph each and cross-link: both are owned by `07-security/waf-shield-firewall-manager-and-network-firewall.md` | XL | 137 / 151 | The second largest unit. Transit Gateway depth belongs in `hybrid-connectivity.md`, keep only the introduction here |
| `hybrid-connectivity.md` | AWS Direct Connect dedicated and hosted, virtual interfaces, Direct Connect Gateway, link aggregation groups, resiliency models, MACsec, SiteLink. Site-to-Site VPN with virtual private gateway compared with Transit Gateway, accelerated VPN, ECMP. Client VPN. Transit Gateway in depth: attachments, route tables, peering, Connect, multicast, Network Manager. AWS Cloud WAN. Hybrid DNS with Route 53 Resolver inbound and outbound endpoints. PrivateLink at scale. Transitive routing patterns | L | Exam guides, SAP task 1.1 core | Professional-heavy unit |
| `route53.md` | Amazon Route 53: public and private hosted zones, record types, alias records, routing policies simple, weighted, latency, failover, geolocation, geoproximity, multivalue and IP-based, health checks, Route 53 Resolver, DNSSEC, domain registration, Application Recovery Controller with readiness checks, routing controls and zonal shift, Route 53 Profiles | L | 51 / 51 | Routing policy comparison table |
| `cloudfront.md` | Amazon CloudFront: distributions, origins including S3 with origin access control, ALB, custom origins and origin groups, cache behaviors and policies, TTLs and invalidation, signed URLs and signed cookies, field-level encryption, geo restriction, CloudFront Functions compared with Lambda@Edge, Origin Shield, HTTP/3, price classes, WAF and Shield integration, logging | M | 15 / 47 | |
| `global-accelerator.md` | AWS Global Accelerator: static anycast IP addresses, listeners, endpoint groups, traffic dials, health checks, custom routing accelerators, comparison with CloudFront and with Route 53 | S | 4 / 4 | |
| `api-gateway.md` | Amazon API Gateway: REST, HTTP and WebSocket APIs, endpoint types edge-optimized, Regional and private, integrations Lambda proxy, HTTP, AWS service, mock and VPC link, stages and deployments, canary releases, caching, throttling and usage plans with API keys, authorizers IAM, Cognito and Lambda, request and response mapping, CORS, custom domains, WAF, logging and X-Ray, quotas | L | 18 / 82 | |

## 05-database

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `rds.md` | Amazon RDS: engines, instance classes, storage types including gp3 and Provisioned IOPS, storage autoscaling, Multi-AZ instance deployment compared with Multi-AZ DB cluster, read replicas including cross-Region, automated backups, manual snapshots, cross-Region copy, point-in-time recovery, encryption with KMS and transparent data encryption, IAM database authentication, RDS Proxy, Blue/Green deployments, Performance Insights, Enhanced Monitoring, parameter and option groups, RDS Custom, maintenance windows, pricing | L | 76 / 73 | |
| `aurora.md` | Amazon Aurora: shared storage architecture with six copies across three Availability Zones, cluster endpoints writer, reader and custom, replicas and failover tiers, Aurora Serverless v2 and the v1 retirement, Global Database with write forwarding, managed failover and switchover, Backtrack, fast cloning, parallel query, Aurora machine learning, the Data API, zero-ETL integrations, Aurora Limitless, Aurora DSQL, I/O-Optimized, Babelfish | M | 31 / 31 | |
| `dynamodb.md` | Amazon DynamoDB, the largest database module in the Professional course at 110 lessons, so write to the top of the L range: tables, items, partition and sort keys, capacity modes on-demand and provisioned with auto scaling, reserved capacity, warm throughput, local and global secondary indexes, consistency eventual, strong and transactional, DynamoDB Streams and Kinesis Data Streams for DynamoDB, time to live, DAX, global tables including multi-Region strong consistency, backups and point-in-time recovery, export to S3, Standard-IA table class, partitions and hot keys, single-table design basics, PartiQL, encryption, VPC endpoints, pricing | L | 33 / 110 | |
| `elasticache-and-memorydb.md` | Amazon ElastiCache with Valkey, Redis OSS and Memcached engines, cluster mode, Multi-AZ with automatic failover, Global Datastore, ElastiCache Serverless, caching strategies lazy loading, write-through and TTL. Amazon MemoryDB as a durable in-memory database | M | 13 and 3 / n/a | |
| `documentdb.md` | Amazon DocumentDB with MongoDB compatibility: clusters, replicas, global clusters, elastic clusters, when to choose it over DynamoDB | S | 10 / 10 | |
| `neptune.md` | Amazon Neptune: property graph with Gremlin and openCypher, RDF with SPARQL, clusters and replicas, Neptune Serverless, global database, Neptune Analytics, use cases | S | 16 / 16 | |
| `keyspaces-qldb-and-timestream.md` | Amazon Keyspaces for Apache Cassandra. Amazon QLDB, which is on neither exam's in-scope list: one paragraph of legacy context and its end of support status, no depth. Amazon Timestream for LiveAnalytics and for InfluxDB, SAP-only | XS group | 2 and 3 / 2 and 3 | |
| `redshift.md` | Amazon Redshift: provisioned with RA3 node types compared with Redshift Serverless, distribution styles and sort keys, Redshift Spectrum, concurrency scaling, snapshots and cross-Region copy, data sharing, zero-ETL, Redshift ML, when to choose it over Athena, EMR or RDS | S | 4 / n/a | The Associate exam tests columnar and data warehouse selection |

## 06-integration

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `sqs.md` | Amazon SQS: standard compared with FIFO including ordering, deduplication and high-throughput FIFO, visibility timeout, short and long polling, dead-letter queues and redrive, delay queues, message size and the extended client library, batching, Lambda event source mapping, access policies, encryption, when to choose it over SNS, EventBridge or Kinesis | M | 38 / 38 | |
| `sns.md` | Amazon SNS: standard and FIFO topics, subscriptions and protocols, fan-out to SQS, filter policies on attributes and payload, message data protection, delivery policies and retries, dead-letter queues, mobile push and SMS, cross-account and cross-Region delivery, encryption | M | 40 / 40 | |
| `eventbridge.md` | Amazon EventBridge: default, custom and partner event buses, rules and event patterns, targets, input transformers, EventBridge Scheduler, EventBridge Pipes, schema registry, archive and replay, cross-account and cross-Region buses, API destinations, when to choose it over SNS or SQS | M | Exam guides, both | |
| `step-functions.md` | AWS Step Functions: Standard compared with Express workflows, state types Task, Choice, Parallel, Map including Distributed Map, Wait, Pass, Fail and Succeed, service integrations optimized and SDK, integration patterns request-response, run a job with .sync, and wait for callback with task token, error handling with Retry and Catch, Workflow Studio, pricing | S | 13 / n/a | Push toward the upper end of the S range. SAP task 4.4 and the emerging AI topics both name it |
| `amazon-mq.md` | Amazon MQ: ActiveMQ and RabbitMQ brokers, single-instance compared with active/standby compared with cluster deployments, protocol compatibility AMQP, MQTT, OpenWire and STOMP, when to choose it over SQS and SNS | S | 13 / 13 | |
| `appflow-appsync-amplify-ses-pinpoint.md` | Amazon AppFlow. AWS AppSync with GraphQL, resolvers, subscriptions and the Events API. AWS Amplify hosting and backend. Amazon SES. Amazon Pinpoint, verify end of support status | XS group | 3+7+4 / 3 | AppSync and SES are Professional-only in scope terms. Note that per service |

## 07-security

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `iam.md` | IAM: principals, root user protection, users, groups, roles, policy types identity-based, resource-based, managed compared with inline, permission boundaries, session policies, and how SCPs and RCPs interact, policy evaluation logic, condition keys including aws:PrincipalOrgID, aws:SourceIp and aws:PrincipalTag, MFA conditions, ABAC compared with RBAC, AWS STS with AssumeRole, AssumeRoleWithSAML, AssumeRoleWithWebIdentity, external ID and role chaining, instance profiles, service roles and service-linked roles, IAM Access Analyzer external and unused access findings and policy validation, credential reports, Access Advisor, the shared responsibility model | L | 45 / core to both | Fold in the STS material from `aws/solutions-architect/api/README.md` |
| `organizations-identity-center-and-control-tower.md` | AWS Organizations: organizational units, service control policies, resource control policies, declarative policies, tag policies, backup policies, delegated administrator, consolidated billing. AWS Control Tower: landing zone, controls, Account Factory, customizations. IAM Identity Center: permission sets, SAML 2.0 and SCIM, trusted identity propagation. AWS RAM. Multi-account patterns: log archive, security tooling and shared services accounts, central logging, organization-wide event notification | L | Exam guides, SAP tasks 1.2 and 1.4 core | Professional-heavy unit |
| `kms-and-cloudhsm.md` | AWS KMS: key types symmetric, asymmetric and HMAC, customer managed compared with AWS managed compared with AWS owned keys, key policies and grants, envelope encryption, automatic and manual rotation, multi-Region keys, imported key material, custom key stores backed by CloudHSM or external HSMs, cross-account key use, the kms:ViaService condition, key deletion and waiting periods. AWS CloudHSM: clusters, FIPS validation, when to choose it over KMS | M | 9 and Done / n/a | |
| `acm.md` | AWS Certificate Manager: public compared with private certificates, AWS Private CA, DNS and email validation, managed renewal, integrations with ALB, CloudFront and API Gateway, exportable public certificates, importing third-party certificates, the Regional nature of certificates and the us-east-1 requirement for CloudFront | S | 7 / 7 | |
| `secrets-manager-and-parameter-store.md` | AWS Secrets Manager: rotation with Lambda and managed rotation, cross-account access, multi-Region replication, pricing. AWS Systems Manager Parameter Store: standard compared with advanced parameters, SecureString, pricing. The decision rule between them | S | 12 / 12 | |
| `cognito.md` | Amazon Cognito: user pools for authentication with hosted UI, federation, MFA, Lambda triggers, groups and advanced security, compared with identity pools for temporary AWS credentials, roles and unauthenticated access, integration with ALB and API Gateway, when to choose it over IAM Identity Center | M | 4 / 33 | |
| `directory-service.md` | AWS Directory Service: AWS Managed Microsoft AD with trusts, seamless domain join and directory sharing, AD Connector, Simple AD, integration with IAM Identity Center, RDS, FSx and WorkSpaces | S | 9 / 1 | |
| `waf-shield-firewall-manager-and-network-firewall.md` | AWS WAF: web ACLs, rules, managed rule groups, rate-based rules, Bot Control, CAPTCHA, logging. AWS Shield Standard compared with Shield Advanced including the DDoS Response Team, cost protection and proactive engagement. AWS Firewall Manager for organization-wide policies. **AWS Network Firewall**, owned here: stateful and stateless rule groups, rule evaluation order, deployment models, and Route 53 Resolver DNS Firewall | M | Done, Done and 4 / n/a | |
| `detection-and-compliance-services.md` | Amazon GuardDuty findings and protection plans including malware protection. Amazon Inspector for EC2, ECR and Lambda. Amazon Macie for S3 sensitive data discovery. Amazon Detective. AWS Security Hub with standards, finding aggregation and automation rules. AWS Audit Manager, verify status. AWS Artifact. **AWS Config in full**: recorder, delivery channel, rules, conformance packs, remediation and aggregators. Config is owned here and only here | M | 2+3+2+5+4+5 | |

## 08-management

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `aws-api-cli-and-sdks.md` | The AWS API: Regional service endpoints, SigV4 request signing, request IDs. The AWS CLI: installation, configure, named profiles, `aws sso login`, `--query` and `--output`, pagination, `aws s3` compared with `s3api` compared with `s3control`. SDKs: the credential provider chain, retries with exponential backoff and jitter, adaptive retry mode. Temporary credentials in tooling. Service quotas and throttling. Smithy in one paragraph. AWS CloudShell. The Management Console | L | 49 / 189 | Fold in `api/README.md`, `api/API_request.md` and `cli/README.md`. Note that the SDKs and CloudShell are out of scope for SAA but in scope for SAP |
| `cloudformation.md` | AWS CloudFormation: template anatomy with parameters, mappings, conditions, resources, outputs and intrinsic functions, stacks, change sets, StackSets self-managed and service-managed, nested stacks, cross-stack references, drift detection, stack policies, deletion and update replace policies, custom resources, macros, the registry and modules, Hooks, Git sync, the IaC generator. A comparison table covering CDK, Terraform and Pulumi | L | n/a / 80 | Fold in `iac/README.md`. State plainly that CDK is out of scope for SAA and that Terraform and Pulumi are third-party context, not exam material |
| `cloudwatch.md` | Amazon CloudWatch: metrics standard, detailed, custom and high-resolution, the embedded metric format, alarms including composite alarms, anomaly detection and missing data treatment, dashboards, CloudWatch Logs with log groups, streams, retention, Logs Insights, metric filters, subscription filters, data protection policies and cross-account observability, Synthetics, RUM, Application Signals, Container Insights, Lambda Insights, the CloudWatch agent, Contributor Insights. Amazon Managed Grafana and Amazon Managed Service for Prometheus in brief. AWS X-Ray | L | 83 / n/a | |
| `cloudtrail.md` | AWS CloudTrail: management, data and Insights events, trails single-Region, multi-Region and organization trails, log file integrity validation, delivery to S3 and CloudWatch Logs, CloudTrail Lake status, Event history, integration with Athena and EventBridge | M | 27 / n/a | |
| `systems-manager.md` | AWS Systems Manager: Fleet Manager, Session Manager, Run Command, Patch Manager with baselines, maintenance windows and patch policies, State Manager, Automation runbooks, Inventory, OpsCenter, Incident Manager, Change Manager, Application Manager, hybrid activations, the SSM Agent and its IAM requirements. Parameter Store pointer to the security unit | M | Exam guides, SAP tasks 2.1, 3.1 and 3.2 core | |
| `service-catalog.md` | AWS Service Catalog: portfolios, products, constraints launch, template and tag update, provisioned products, sharing across accounts, AppRegistry, compared with Control Tower Account Factory and with AWS Proton | S | 23 / n/a | Verify Proton status |
| `config-trusted-advisor-health-and-well-architected.md` | AWS Config is **not** taught here, it is owned by `07-security/detection-and-compliance-services.md`: give it one paragraph and a cross-link. AWS Trusted Advisor checks, priority and organizational view. AWS Health Dashboard account and organizational views with EventBridge integration. AWS License Manager. AWS Well-Architected Tool. Service Quotas | XS group | Done / n/a | |
| `cost-management.md` | AWS Cost Explorer. AWS Budgets and budget actions. AWS Cost and Usage Report including CUR 2.0 and Data Exports. Cost allocation tags and cost categories. Consolidated billing with Reserved Instance and Savings Plans sharing. Savings Plans types. AWS Compute Optimizer. AWS Pricing Calculator. S3 Storage Lens. AWS Cost Anomaly Detection. AWS Billing Conductor. The data transfer cost rules: cross-AZ, cross-Region, internet egress, VPC endpoints and NAT | L | 4 / 4, plus exam guides | The cost reference unit both domain guides point to. Include the cost tradeoffs of managed service offerings without duplicating each service unit's pricing details |
| `developer-tools-and-cicd.md` | AWS CodePipeline. AWS CodeBuild. AWS CodeDeploy with deployment configurations for EC2, Lambda and ECS, blue/green, canary and linear. AWS CodeArtifact. Amazon CodeGuru. CodeCommit status. AWS Proton status. Deployment strategies all-at-once, rolling, blue/green, canary and immutable, compared across Elastic Beanstalk, ECS, Lambda and EC2 | M | Exam guides, SAP tasks 2.1 and 3.1 | Out of scope for SAA. Say so at the top |

## 09-analytics

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `kinesis.md` | Amazon Kinesis Data Streams: shards, on-demand compared with provisioned, producers, consumers, enhanced fan-out, retention. Amazon Data Firehose, formerly Kinesis Data Firehose: sources, destinations, buffering hints, Lambda transformation, format conversion. Amazon Managed Service for Apache Flink, formerly Kinesis Data Analytics. Amazon Kinesis Video Streams. When to choose Kinesis over SQS, MSK or EventBridge | M | 21 / 25 | |
| `msk.md` | Amazon MSK: provisioned compared with Serverless, brokers and storage, MSK Connect, MSK Replicator, tiered storage, security with IAM, TLS and SASL/SCRAM, when to choose it over Kinesis | S | 13 / 13 | |
| `glue.md` | AWS Glue: Data Catalog and crawlers, ETL jobs in Spark, Python shell and streaming, Glue Studio, DataBrew, Glue Data Quality, workflows and triggers, job bookmarks, the schema registry, format conversion from CSV to Parquet, partitioning, pricing | M | 16 / 31 | Verify Glue for Ray status |
| `athena.md` | Amazon Athena: SQL over S3, Data Catalog integration, partitioning and partition projection, columnar formats and compression, workgroups and cost controls, federated query, CREATE TABLE AS SELECT, Athena for Spark, Lake Formation permissions, pricing | S | 15 / 15 | |
| `lake-formation.md` | AWS Lake Formation: building a data lake on S3, permissions by named resource and by LF-Tags, row, column and cell-level security, blueprints, governed tables status, cross-account sharing, integration with Athena, Redshift, EMR and Glue | S | 6 / n/a | |
| `emr.md` | Amazon EMR: cluster composition with primary, core and task nodes, EMR on EC2 compared with EMR on EKS compared with EMR Serverless, instance fleets and Spot, EMRFS and S3 compared with HDFS, steps, auto scaling, when to choose it over Glue, Athena or Redshift | S | Exam guides | |
| `opensearch.md` | Amazon OpenSearch Service: managed domains compared with Serverless, use cases for log analytics, search and vector search, UltraWarm and cold storage, cross-cluster search and replication, ingestion through OpenSearch Ingestion and Data Firehose, fine-grained access control and VPC access, when to choose it over Athena or CloudWatch Logs | S | 4 / 4 | |
| `data-exchange-and-quick.md` | AWS Data Exchange. Amazon Quick, formerly Amazon QuickSight: SPICE, datasets, dashboards, embedding, row-level security, natural language query | XS group | 4 / 4 | Verify the current name and what it covers |

## 10-migration

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `migration-hub-discovery-and-strategy.md` | AWS Migration Hub with tracking, Strategy Recommendations, Refactor Spaces and Orchestrator. AWS Application Discovery Service agent-based and agentless. The seven common migration strategies. Portfolio assessment, asset planning, wave planning, total cost of ownership. Migration Evaluator, noting it is out of scope for SAA | M | 3 / 3, plus SAP domain 4 | |
| `dms-and-sct.md` | AWS DMS: replication instances compared with DMS Serverless, endpoints, task types full load, change data capture, and both, homogeneous compared with heterogeneous migration, AWS Schema Conversion Tool, DMS Schema Conversion, Fleet Advisor, common source and target pairs, migrating to Aurora, DynamoDB, Redshift and S3 | S | 7 / 7 | Push to the upper end of the S range |
| `application-migration-service.md` | AWS Application Migration Service, now renamed **AWS Transform MGN**, which both exam guides predate, so teach both names: replication agents, launch templates, test and cutover instances. Its relationship to AWS Elastic Disaster Recovery. VM Import/Export. The CloudEndure lineage and the retirement of Server Migration Service | S | Exam guides | |

## 11-ml-and-media

| File | Services and topics | Tier | Lesson signal | Notes |
|---|---|---|---|---|
| `ml-managed-services.md` | Amazon Comprehend, Lex, Polly, Rekognition, Textract, Transcribe, Translate, Kendra, Personalize, Fraud Detector, and Amazon SageMaker AI in two paragraphs covering build, train, deploy and endpoint types | M | 37 / 35 | One comparison table mapping the exam's wording to the service, including how purpose-built managed services replace custom implementations. Kendra, Personalize and Fraud Detector are Professional-only in scope terms, and Personalize is explicitly out of scope for SAA. Say so |
| `ai-dev-tools-and-generative-ai.md` | Amazon Q Developer, formerly CodeWhisperer. Amazon Q Business. Amazon Bedrock: models, Knowledge Bases, Guardrails, Agents and AgentCore. PartyRock. The SAP-C02 emerging topics: Bedrock Guardrails, AgentCore Identity, human approval workflows with Step Functions | S | 7 / n/a | Fold in `aws/solutions-architect/ai/README.md`. State plainly that Bedrock is not in either in-scope list, so a question naming it is testing the surrounding architecture |
| `media-iot-and-device-farm.md` | Amazon Elastic Transcoder, verify status. AWS Elemental MediaConvert, out of scope for SAA. Kinesis Video Streams pointer. AWS Device Farm. AWS IoT Core and the IoT family in one page, in scope for SAP and out of scope for SAA. Amazon Managed Blockchain in one paragraph | XS group | 4+4+4 / 4+4 | |

## Category READMEs

Each of the eleven category folders gets a `README.md` of 250 to 500 words: what
the category covers, a table of its units with a one-line description of each,
which exam tasks the category serves, and a suggested reading order.

`services/README.md` is the coverage matrix. One row per unit, with columns for
the unit, the services it teaches, the SAA-C03 tasks it serves and the SAP-C02
tasks it serves. This is the file the final pass uses to prove that every task
statement bullet is covered.

## Domain guides

Written after all service units are done. Each maps one exam domain's task
statements to the service units that teach them, then adds the cross-cutting
material that no single service unit owns.

| File | Covers | Words | Quiz |
|---|---|---|---|
| `domains/README.md` | Both exam formats, how the domain guides relate to the service units, a suggested study order for each exam | 600 to 900 | none |
| `domains/saa-c03/01-design-secure-architectures.md` | Tasks 1.1 to 1.3 | 2,500 to 4,000 | 12 |
| `domains/saa-c03/02-design-resilient-architectures.md` | Tasks 2.1 to 2.2 | 2,500 to 4,000 | 12 |
| `domains/saa-c03/03-design-high-performing-architectures.md` | Tasks 3.1 to 3.5 | 2,500 to 4,000 | 12 |
| `domains/saa-c03/04-design-cost-optimized-architectures.md` | Tasks 4.1 to 4.4 | 2,500 to 4,000 | 12 |
| `domains/sap-c02/01-organizational-complexity.md` | Tasks 1.1 to 1.5 | 3,000 to 4,500 | 12 |
| `domains/sap-c02/02-new-solutions.md` | Tasks 2.1 to 2.6 | 3,000 to 4,500 | 12 |
| `domains/sap-c02/03-continuous-improvement.md` | Tasks 3.1 to 3.5 | 3,000 to 4,500 | 12 |
| `domains/sap-c02/04-migration-and-modernization.md` | Tasks 4.1 to 4.4, plus the emerging topics note | 3,000 to 4,500 | 12 |

Domain guide section order differs from a service unit:

```
# <Domain name>
**Weight and shape.** Paragraph on the weight, question count and what the domain
feels like.
## Task X.Y: <verbatim task statement>     one per task statement
   Prose mapping each Knowledge and Skills bullet to the unit that teaches it,
   with the decisions the exam actually tests.
## Decision tables                          the cross-cutting choices
## Words that give the answer away          wording to service mappings
## The domain on one page                   a compressed summary
## Mixed quiz                               12 questions spanning the domain
## Where to read more                       links to the service units
```

Domain guide quizzes must not repeat questions from the service units.

## Appendix

Written last, from the finished units.

| File | Content |
|---|---|
| `appendix/glossary.md` | Every service and term the course uses. One or two lines each, the unit that teaches it, and the official documentation link |
| `appendix/decision-tables.md` | The cross-cutting choices: which storage, which compute, which database, which load balancer, which connectivity, which DR strategy, which security control, which messaging service. Plus the reading rules for exam questions and the distractor words |
| `appendix/README.md` | Rewrite the existing file to describe these two files and nothing else |
