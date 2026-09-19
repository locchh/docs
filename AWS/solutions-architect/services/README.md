# Service coverage matrix

This is the ownership map for every Knowledge and Skills bullet in the
SAA-C03 and SAP-C02 exam guides captured in `_build/`. Each bullet has
exactly one owning service unit. An owning unit must teach the bullet
well enough to answer an exam question; supporting units may reinforce it
without duplicating the primary explanation.

Bullet references in the unit index use `K` for Knowledge and `S` for
Skills, numbered in source-guide order. `E` identifies SAP-C02's three
emerging-topic skills. The detailed table preserves the source wording.

**Coverage:** 379 of 379 bullets assigned: 189 SAA-C03,
187 SAP-C02 task bullets and 3 SAP-C02 emerging-topic bullets.

## Bullet-by-bullet ownership

| Exam | Task | Bullet | Owner | Also covered in |
|---|---|---|---|---|
| SAA-C03 | 1.1 | Access controls and management across multiple accounts | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAA-C03 | 1.1 | AWS federated access and identity services, for example IAM, AWS IAM Identity Center | `07-security/iam.md` | `07-security/organizations-identity-center-and-control-tower.md` |
| SAA-C03 | 1.1 | AWS global infrastructure, for example Availability Zones, AWS Regions | `04-networking/vpc.md` | `04-networking/route53.md` |
| SAA-C03 | 1.1 | AWS security best practices, for example the principle of least privilege | `07-security/iam.md` |  |
| SAA-C03 | 1.1 | The AWS shared responsibility model | `07-security/iam.md` |  |
| SAA-C03 | 1.1 | Applying AWS security best practices to IAM users and root users, for example multi-factor authentication (MFA) | `07-security/iam.md` |  |
| SAA-C03 | 1.1 | Designing a flexible authorization model that includes IAM users, groups, roles and policies | `07-security/iam.md` |  |
| SAA-C03 | 1.1 | Designing a role-based access control strategy, for example AWS STS, role switching, cross-account access | `07-security/iam.md` |  |
| SAA-C03 | 1.1 | Designing a security strategy for multiple AWS accounts, for example AWS Control Tower, service control policies (SCPs) | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAA-C03 | 1.1 | Determining the appropriate use of resource policies for AWS services | `07-security/iam.md` |  |
| SAA-C03 | 1.1 | Determining when to federate a directory service with IAM roles | `07-security/directory-service.md` | `07-security/iam.md` |
| SAA-C03 | 1.2 | Application configuration and credentials security | `07-security/secrets-manager-and-parameter-store.md` |  |
| SAA-C03 | 1.2 | AWS service endpoints | `04-networking/vpc.md` |  |
| SAA-C03 | 1.2 | Control ports, protocols and network traffic on AWS | `04-networking/vpc.md` |  |
| SAA-C03 | 1.2 | Secure application access | `07-security/cognito.md` |  |
| SAA-C03 | 1.2 | Security services with appropriate use cases, for example Amazon Cognito, Amazon GuardDuty, Amazon Macie | `07-security/detection-and-compliance-services.md` | `07-security/cognito.md` |
| SAA-C03 | 1.2 | Threat vectors external to AWS, for example DDoS, SQL injection | `07-security/waf-shield-firewall-manager-and-network-firewall.md` |  |
| SAA-C03 | 1.2 | Designing VPC architectures with security components, for example security groups, route tables, network ACLs, NAT gateways | `04-networking/vpc.md` |  |
| SAA-C03 | 1.2 | Determining network segmentation strategies, for example using public subnets and private subnets | `04-networking/vpc.md` |  |
| SAA-C03 | 1.2 | Integrating AWS services to secure applications, for example AWS Shield, AWS WAF, IAM Identity Center, AWS Secrets Manager | `07-security/waf-shield-firewall-manager-and-network-firewall.md` | `07-security/secrets-manager-and-parameter-store.md`, `07-security/organizations-identity-center-and-control-tower.md`, `07-security/iam.md` |
| SAA-C03 | 1.2 | Securing external network connections to and from the AWS Cloud, for example VPN, AWS Direct Connect | `04-networking/hybrid-connectivity.md` |  |
| SAA-C03 | 1.3 | Data access and governance | `09-analytics/lake-formation.md` | `07-security/iam.md`, `01-storage/s3.md` |
| SAA-C03 | 1.3 | Data recovery | `01-storage/backup-and-disaster-recovery.md` | `01-storage/s3.md`, `05-database/rds.md` |
| SAA-C03 | 1.3 | Data retention and classification | `07-security/detection-and-compliance-services.md` | `01-storage/s3.md` |
| SAA-C03 | 1.3 | Encryption and appropriate key management | `07-security/kms-and-cloudhsm.md` |  |
| SAA-C03 | 1.3 | Aligning AWS technologies to meet compliance requirements | `07-security/detection-and-compliance-services.md` |  |
| SAA-C03 | 1.3 | Encrypting data at rest, for example AWS KMS | `07-security/kms-and-cloudhsm.md` |  |
| SAA-C03 | 1.3 | Encrypting data in transit, for example AWS Certificate Manager (ACM) using TLS | `07-security/acm.md` |  |
| SAA-C03 | 1.3 | Implementing access policies for encryption keys | `07-security/kms-and-cloudhsm.md` |  |
| SAA-C03 | 1.3 | Implementing data backups and replications | `01-storage/backup-and-disaster-recovery.md` |  |
| SAA-C03 | 1.3 | Implementing policies for data access, lifecycle and protection | `01-storage/s3.md` |  |
| SAA-C03 | 1.3 | Rotating encryption keys and renewing certificates | `07-security/kms-and-cloudhsm.md` | `07-security/acm.md` |
| SAA-C03 | 2.1 | API creation and management, for example Amazon API Gateway, REST API | `04-networking/api-gateway.md` |  |
| SAA-C03 | 2.1 | AWS managed services with appropriate use cases, for example AWS Transfer Family, Amazon SQS, AWS Secrets Manager | `06-integration/sqs.md` | `01-storage/transfer-family-and-datasync.md`, `07-security/secrets-manager-and-parameter-store.md` |
| SAA-C03 | 2.1 | Caching strategies | `05-database/elasticache-and-memorydb.md` | `04-networking/cloudfront.md`, `04-networking/api-gateway.md` |
| SAA-C03 | 2.1 | Design principles for microservices, for example stateless workloads compared with stateful workloads | `03-containers/ecs-and-ecr.md` | `02-compute/lambda.md`, `06-integration/sqs.md` |
| SAA-C03 | 2.1 | Event-driven architectures | `06-integration/eventbridge.md` | `06-integration/sqs.md`, `02-compute/lambda.md` |
| SAA-C03 | 2.1 | Horizontal scaling and vertical scaling | `02-compute/ec2-auto-scaling.md` | `02-compute/ec2.md`, `02-compute/lambda.md` |
| SAA-C03 | 2.1 | How to appropriately use edge accelerators, for example content delivery network (CDN) | `04-networking/cloudfront.md` |  |
| SAA-C03 | 2.1 | How to migrate applications into containers | `03-containers/ecs-and-ecr.md` |  |
| SAA-C03 | 2.1 | Load balancing concepts, for example Application Load Balancer (ALB) | `02-compute/elastic-load-balancing.md` |  |
| SAA-C03 | 2.1 | Multi-tier architectures | `04-networking/vpc.md` | `02-compute/elastic-load-balancing.md`, `05-database/rds.md` |
| SAA-C03 | 2.1 | Queuing and messaging concepts, for example publish/subscribe | `06-integration/sns.md` |  |
| SAA-C03 | 2.1 | Serverless technologies and patterns, for example AWS Fargate, AWS Lambda | `02-compute/lambda.md` | `03-containers/ecs-and-ecr.md` |
| SAA-C03 | 2.1 | Storage types with associated characteristics, for example object, file, block | `01-storage/s3.md` |  |
| SAA-C03 | 2.1 | The orchestration of containers, for example Amazon ECS, Amazon EKS | `03-containers/ecs-and-ecr.md` | `03-containers/eks.md` |
| SAA-C03 | 2.1 | When to use read replicas | `05-database/rds.md` |  |
| SAA-C03 | 2.1 | Workflow orchestration, for example AWS Step Functions | `06-integration/step-functions.md` |  |
| SAA-C03 | 2.1 | Designing event-driven, microservice and multi-tier architectures based on requirements | `06-integration/eventbridge.md` | `04-networking/api-gateway.md`, `02-compute/lambda.md` |
| SAA-C03 | 2.1 | Determining scaling strategies for components used in an architecture design | `02-compute/ec2-auto-scaling.md` | `02-compute/lambda.md`, `03-containers/ecs-and-ecr.md` |
| SAA-C03 | 2.1 | Determining the AWS services required to achieve loose coupling based on requirements | `06-integration/sqs.md` | `06-integration/sns.md`, `06-integration/eventbridge.md` |
| SAA-C03 | 2.1 | Determining when to use containers | `03-containers/ecs-and-ecr.md` |  |
| SAA-C03 | 2.1 | Determining when to use serverless technologies and patterns | `02-compute/lambda.md` |  |
| SAA-C03 | 2.1 | Recommending appropriate compute, storage, networking and database technologies based on requirements | `02-compute/ec2.md` | `04-networking/vpc.md`, `01-storage/s3.md`, `05-database/rds.md` |
| SAA-C03 | 2.1 | Using purpose-built AWS services for workloads | `05-database/dynamodb.md` | `11-ml-and-media/ml-managed-services.md` |
| SAA-C03 | 2.2 | AWS global infrastructure, for example Availability Zones, AWS Regions, Amazon Route 53 | `04-networking/route53.md` |  |
| SAA-C03 | 2.2 | AWS Managed Services with appropriate use cases, for example Amazon Comprehend, Amazon Polly | `11-ml-and-media/ml-managed-services.md` |  |
| SAA-C03 | 2.2 | Basic networking concepts, for example route tables | `04-networking/vpc.md` |  |
| SAA-C03 | 2.2 | Disaster recovery (DR) strategies, for example backup and restore, pilot light, warm standby, active-active failover, recovery point objective (RPO), recovery time objective (RTO) | `01-storage/backup-and-disaster-recovery.md` |  |
| SAA-C03 | 2.2 | Distributed design patterns | `06-integration/eventbridge.md` | `06-integration/sqs.md`, `05-database/dynamodb.md` |
| SAA-C03 | 2.2 | Failover strategies | `04-networking/route53.md` | `01-storage/backup-and-disaster-recovery.md`, `02-compute/elastic-load-balancing.md` |
| SAA-C03 | 2.2 | Immutable infrastructure | `02-compute/ami.md` |  |
| SAA-C03 | 2.2 | Load balancing concepts, for example ALB | `02-compute/elastic-load-balancing.md` |  |
| SAA-C03 | 2.2 | Proxy concepts, for example Amazon RDS Proxy | `05-database/rds.md` |  |
| SAA-C03 | 2.2 | Service quotas and throttling, for example how to configure the service quotas for a workload in a standby environment | `08-management/aws-api-cli-and-sdks.md` | `08-management/config-trusted-advisor-health-and-well-architected.md` |
| SAA-C03 | 2.2 | Storage options and characteristics, for example durability, replication | `01-storage/s3.md` |  |
| SAA-C03 | 2.2 | Workload visibility, for example AWS X-Ray | `08-management/cloudwatch.md` |  |
| SAA-C03 | 2.2 | Determining automation strategies to ensure infrastructure integrity | `08-management/cloudformation.md` |  |
| SAA-C03 | 2.2 | Determining the AWS services required to provide a highly available and/or fault-tolerant architecture across AWS Regions or Availability Zones | `01-storage/backup-and-disaster-recovery.md` | `04-networking/route53.md`, `02-compute/elastic-load-balancing.md` |
| SAA-C03 | 2.2 | Identifying metrics based on business requirements to deliver a highly available solution | `08-management/cloudwatch.md` |  |
| SAA-C03 | 2.2 | Implementing designs to mitigate single points of failure | `02-compute/elastic-load-balancing.md` | `02-compute/ec2-auto-scaling.md`, `04-networking/route53.md` |
| SAA-C03 | 2.2 | Implementing strategies to ensure the durability and availability of data, for example backups | `01-storage/backup-and-disaster-recovery.md` |  |
| SAA-C03 | 2.2 | Selecting an appropriate DR strategy to meet business requirements | `01-storage/backup-and-disaster-recovery.md` |  |
| SAA-C03 | 2.2 | Using AWS services that improve the reliability of legacy applications and applications not built for the cloud, for example when application changes are not possible | `02-compute/elastic-load-balancing.md` | `02-compute/ec2-auto-scaling.md`, `01-storage/backup-and-disaster-recovery.md`, `10-migration/application-migration-service.md` |
| SAA-C03 | 2.2 | Using purpose-built AWS services for workloads | `11-ml-and-media/ml-managed-services.md` | `05-database/dynamodb.md` |
| SAA-C03 | 3.1 | Hybrid storage solutions to meet business requirements | `01-storage/storage-gateway.md` |  |
| SAA-C03 | 3.1 | Storage services with appropriate use cases, for example Amazon S3, Amazon EFS, Amazon EBS | `01-storage/s3.md` | `01-storage/ebs.md`, `01-storage/efs.md` |
| SAA-C03 | 3.1 | Storage types with associated characteristics, for example object, file, block | `01-storage/s3.md` |  |
| SAA-C03 | 3.1 | Determining storage services and configurations that meet performance demands | `01-storage/s3.md` | `01-storage/ebs.md`, `01-storage/efs.md`, `01-storage/fsx.md` |
| SAA-C03 | 3.1 | Determining storage services that can scale to accommodate future needs | `01-storage/s3.md` | `01-storage/efs.md`, `01-storage/fsx.md` |
| SAA-C03 | 3.2 | AWS compute services with appropriate use cases, for example AWS Batch, Amazon EMR, AWS Fargate | `02-compute/batch.md` | `03-containers/ecs-and-ecr.md`, `09-analytics/emr.md` |
| SAA-C03 | 3.2 | Distributed computing concepts supported by AWS global infrastructure and edge services | `02-compute/other-compute-and-end-user.md` | `02-compute/ec2.md`, `04-networking/cloudfront.md`, `04-networking/global-accelerator.md` |
| SAA-C03 | 3.2 | Queuing and messaging concepts, for example publish/subscribe | `06-integration/sns.md` |  |
| SAA-C03 | 3.2 | Scalability capabilities with appropriate use cases, for example Amazon EC2 Auto Scaling, AWS Auto Scaling | `02-compute/ec2-auto-scaling.md` | `02-compute/ec2.md` |
| SAA-C03 | 3.2 | Serverless technologies and patterns, for example AWS Lambda, Fargate | `02-compute/lambda.md` | `03-containers/ecs-and-ecr.md` |
| SAA-C03 | 3.2 | The orchestration of containers, for example Amazon ECS, Amazon EKS | `03-containers/ecs-and-ecr.md` | `03-containers/eks.md` |
| SAA-C03 | 3.2 | Decoupling workloads so that components can scale independently | `06-integration/sqs.md` |  |
| SAA-C03 | 3.2 | Identifying metrics and conditions to perform scaling actions | `02-compute/ec2-auto-scaling.md` |  |
| SAA-C03 | 3.2 | Selecting the appropriate compute options and features, for example EC2 instance types, to meet business requirements | `02-compute/ec2.md` |  |
| SAA-C03 | 3.2 | Selecting the appropriate resource type and size, for example the amount of Lambda memory, to meet business requirements | `02-compute/lambda.md` |  |
| SAA-C03 | 3.3 | AWS global infrastructure, for example Availability Zones, AWS Regions | `05-database/rds.md` | `05-database/aurora.md`, `05-database/dynamodb.md` |
| SAA-C03 | 3.3 | Caching strategies and services, for example Amazon ElastiCache | `05-database/elasticache-and-memorydb.md` |  |
| SAA-C03 | 3.3 | Data access patterns, for example read-intensive compared with write-intensive | `05-database/dynamodb.md` |  |
| SAA-C03 | 3.3 | Database capacity planning, for example capacity units, instance types, Provisioned IOPS | `05-database/rds.md` |  |
| SAA-C03 | 3.3 | Database connections and proxies | `05-database/rds.md` |  |
| SAA-C03 | 3.3 | Database engines with appropriate use cases, for example heterogeneous migrations, homogeneous migrations | `10-migration/dms-and-sct.md` |  |
| SAA-C03 | 3.3 | Database replication, for example read replicas | `05-database/rds.md` |  |
| SAA-C03 | 3.3 | Database types and services, for example serverless, relational compared with non-relational, in-memory | `05-database/dynamodb.md` |  |
| SAA-C03 | 3.3 | Configuring read replicas to meet business requirements | `05-database/rds.md` |  |
| SAA-C03 | 3.3 | Designing database architectures | `05-database/rds.md` | `05-database/aurora.md`, `05-database/dynamodb.md` |
| SAA-C03 | 3.3 | Determining an appropriate database engine, for example MySQL compared with PostgreSQL | `05-database/rds.md` |  |
| SAA-C03 | 3.3 | Determining an appropriate database type, for example Amazon Aurora, Amazon DynamoDB | `05-database/dynamodb.md` | `05-database/aurora.md` |
| SAA-C03 | 3.3 | Integrating caching to meet business requirements | `05-database/elasticache-and-memorydb.md` |  |
| SAA-C03 | 3.4 | Edge networking services with appropriate use cases, for example Amazon CloudFront, AWS Global Accelerator | `04-networking/cloudfront.md` | `04-networking/global-accelerator.md` |
| SAA-C03 | 3.4 | How to design network architecture, for example subnet tiers, routing, IP addressing | `04-networking/vpc.md` |  |
| SAA-C03 | 3.4 | Load balancing concepts, for example Application Load Balancer (ALB) | `02-compute/elastic-load-balancing.md` |  |
| SAA-C03 | 3.4 | Network connection options, for example AWS VPN, AWS Direct Connect, AWS PrivateLink | `04-networking/hybrid-connectivity.md` | `04-networking/vpc.md` |
| SAA-C03 | 3.4 | Creating a network topology for various architectures, for example global, hybrid, multi-tier | `04-networking/hybrid-connectivity.md` |  |
| SAA-C03 | 3.4 | Determining network configurations that can scale to accommodate future needs | `04-networking/vpc.md` | `04-networking/hybrid-connectivity.md`, `02-compute/elastic-load-balancing.md` |
| SAA-C03 | 3.4 | Determining the appropriate placement of resources to meet business requirements | `04-networking/vpc.md` | `04-networking/cloudfront.md`, `04-networking/hybrid-connectivity.md` |
| SAA-C03 | 3.4 | Selecting the appropriate load balancing strategy | `02-compute/elastic-load-balancing.md` |  |
| SAA-C03 | 3.5 | Data analytics and visualization services with appropriate use cases, for example Amazon Athena, AWS Lake Formation, Amazon Quick | `09-analytics/data-exchange-and-quick.md` | `09-analytics/athena.md`, `09-analytics/lake-formation.md` |
| SAA-C03 | 3.5 | Data ingestion patterns, for example frequency | `09-analytics/kinesis.md` | `09-analytics/glue.md` |
| SAA-C03 | 3.5 | Data transfer services with appropriate use cases, for example AWS DataSync, AWS Storage Gateway | `01-storage/transfer-family-and-datasync.md` | `01-storage/storage-gateway.md` |
| SAA-C03 | 3.5 | Data transformation services with appropriate use cases, for example AWS Glue | `09-analytics/glue.md` |  |
| SAA-C03 | 3.5 | Secure access to ingestion access points | `07-security/iam.md` | `04-networking/vpc.md`, `07-security/kms-and-cloudhsm.md` |
| SAA-C03 | 3.5 | Sizes and speeds needed to meet business requirements | `01-storage/transfer-family-and-datasync.md` | `01-storage/snow-family.md`, `09-analytics/kinesis.md` |
| SAA-C03 | 3.5 | Streaming data services with appropriate use cases, for example Amazon Kinesis | `09-analytics/kinesis.md` |  |
| SAA-C03 | 3.5 | Building and securing data lakes | `09-analytics/lake-formation.md` |  |
| SAA-C03 | 3.5 | Designing data streaming architectures | `09-analytics/kinesis.md` | `09-analytics/msk.md` |
| SAA-C03 | 3.5 | Designing data transfer solutions | `01-storage/transfer-family-and-datasync.md` |  |
| SAA-C03 | 3.5 | Implementing visualization strategies | `09-analytics/data-exchange-and-quick.md` |  |
| SAA-C03 | 3.5 | Selecting appropriate compute options for data processing, for example Amazon EMR | `09-analytics/emr.md` |  |
| SAA-C03 | 3.5 | Selecting appropriate configurations for ingestion | `09-analytics/kinesis.md` | `09-analytics/glue.md`, `01-storage/transfer-family-and-datasync.md` |
| SAA-C03 | 3.5 | Transforming data between formats, for example .csv to .parquet | `09-analytics/glue.md` |  |
| SAA-C03 | 4.1 | Access options, for example an S3 bucket with Requester Pays object storage | `01-storage/s3.md` |  |
| SAA-C03 | 4.1 | AWS cost management service features, for example cost allocation tags, multi-account billing | `08-management/cost-management.md` |  |
| SAA-C03 | 4.1 | AWS cost management tools with appropriate use cases, for example AWS Cost Explorer, AWS Budgets, AWS Cost and Usage Report | `08-management/cost-management.md` |  |
| SAA-C03 | 4.1 | AWS storage services with appropriate use cases, for example Amazon FSx, Amazon EFS, Amazon S3, Amazon EBS | `01-storage/s3.md` | `01-storage/ebs.md`, `01-storage/efs.md`, `01-storage/fsx.md` |
| SAA-C03 | 4.1 | Backup strategies | `01-storage/backup-and-disaster-recovery.md` |  |
| SAA-C03 | 4.1 | Block storage options, for example hard disk drive (HDD) volume types, solid state drive (SSD) volume types | `01-storage/ebs.md` |  |
| SAA-C03 | 4.1 | Data lifecycles | `01-storage/s3.md` |  |
| SAA-C03 | 4.1 | Hybrid storage options, for example AWS DataSync, AWS Transfer Family, AWS Storage Gateway | `01-storage/transfer-family-and-datasync.md` | `01-storage/storage-gateway.md` |
| SAA-C03 | 4.1 | Storage access patterns | `01-storage/s3.md` | `01-storage/ebs.md`, `01-storage/efs.md` |
| SAA-C03 | 4.1 | Storage tiering, for example cold tiering for object storage | `01-storage/s3.md` |  |
| SAA-C03 | 4.1 | Storage types with associated characteristics, for example object, file, block | `01-storage/s3.md` | `01-storage/ebs.md`, `01-storage/efs.md` |
| SAA-C03 | 4.1 | Designing appropriate storage strategies, for example batch uploads to Amazon S3 compared with individual uploads | `01-storage/s3.md` |  |
| SAA-C03 | 4.1 | Determining the correct storage size for a workload | `01-storage/ebs.md` | `01-storage/s3.md`, `01-storage/efs.md` |
| SAA-C03 | 4.1 | Determining the lowest cost method of transferring data for a workload to AWS storage | `01-storage/transfer-family-and-datasync.md` |  |
| SAA-C03 | 4.1 | Determining when storage auto scaling is required | `01-storage/efs.md` |  |
| SAA-C03 | 4.1 | Managing S3 object lifecycles | `01-storage/s3.md` |  |
| SAA-C03 | 4.1 | Selecting the appropriate backup and/or archival solution | `01-storage/backup-and-disaster-recovery.md` |  |
| SAA-C03 | 4.1 | Selecting the appropriate service for data migration to storage services | `01-storage/transfer-family-and-datasync.md` |  |
| SAA-C03 | 4.1 | Selecting the appropriate storage tier | `01-storage/s3.md` |  |
| SAA-C03 | 4.1 | Selecting the correct data lifecycle for storage | `01-storage/s3.md` |  |
| SAA-C03 | 4.1 | Selecting the most cost-effective storage service for a workload | `01-storage/s3.md` | `01-storage/ebs.md`, `01-storage/efs.md`, `01-storage/fsx.md` |
| SAA-C03 | 4.2 | AWS cost management service features, for example cost allocation tags, multi-account billing | `08-management/cost-management.md` |  |
| SAA-C03 | 4.2 | AWS cost management tools with appropriate use cases, for example AWS Cost Explorer, AWS Budgets, AWS Cost and Usage Report | `08-management/cost-management.md` |  |
| SAA-C03 | 4.2 | AWS global infrastructure, for example Availability Zones, AWS Regions | `04-networking/vpc.md` | `08-management/cost-management.md` |
| SAA-C03 | 4.2 | AWS purchasing options, for example Spot Instances, Reserved Instances, Savings Plans | `02-compute/ec2.md` | `08-management/cost-management.md` |
| SAA-C03 | 4.2 | Distributed compute strategies, for example edge processing | `02-compute/other-compute-and-end-user.md` |  |
| SAA-C03 | 4.2 | Hybrid compute options, for example AWS Outposts | `02-compute/other-compute-and-end-user.md` |  |
| SAA-C03 | 4.2 | Instance types, families and sizes, for example memory optimized, compute optimized, virtualization | `02-compute/ec2.md` |  |
| SAA-C03 | 4.2 | Optimization of compute utilization, for example containers, serverless computing, microservices | `03-containers/ecs-and-ecr.md` | `02-compute/lambda.md`, `02-compute/ec2.md` |
| SAA-C03 | 4.2 | Scaling strategies, for example auto scaling, hibernation | `02-compute/ec2-auto-scaling.md` |  |
| SAA-C03 | 4.2 | Determining an appropriate load balancing strategy, for example Application Load Balancer (Layer 7) compared with Network Load Balancer (Layer 4) compared with Gateway Load Balancer | `02-compute/elastic-load-balancing.md` |  |
| SAA-C03 | 4.2 | Determining appropriate scaling methods and strategies for elastic workloads, for example horizontal compared with vertical, EC2 hibernation | `02-compute/ec2-auto-scaling.md` |  |
| SAA-C03 | 4.2 | Determining cost-effective AWS compute services with appropriate use cases, for example AWS Lambda, Amazon EC2, AWS Fargate | `02-compute/ec2.md` | `03-containers/ecs-and-ecr.md`, `02-compute/lambda.md` |
| SAA-C03 | 4.2 | Determining the required availability for different classes of workloads, for example production workloads, non-production workloads | `01-storage/backup-and-disaster-recovery.md` | `08-management/cost-management.md`, `02-compute/ec2-auto-scaling.md` |
| SAA-C03 | 4.2 | Selecting the appropriate instance family for a workload | `02-compute/ec2.md` |  |
| SAA-C03 | 4.2 | Selecting the appropriate instance size for a workload | `02-compute/ec2.md` |  |
| SAA-C03 | 4.3 | AWS cost management service features, for example cost allocation tags, multi-account billing | `08-management/cost-management.md` |  |
| SAA-C03 | 4.3 | AWS cost management tools with appropriate use cases, for example AWS Cost Explorer, AWS Budgets, AWS Cost and Usage Report | `08-management/cost-management.md` |  |
| SAA-C03 | 4.3 | Caching strategies | `05-database/elasticache-and-memorydb.md` | `05-database/dynamodb.md` |
| SAA-C03 | 4.3 | Data retention policies | `01-storage/backup-and-disaster-recovery.md` | `05-database/rds.md`, `01-storage/s3.md` |
| SAA-C03 | 4.3 | Database capacity planning, for example capacity units | `05-database/dynamodb.md` |  |
| SAA-C03 | 4.3 | Database connections and proxies | `05-database/rds.md` |  |
| SAA-C03 | 4.3 | Database engines with appropriate use cases, for example heterogeneous migrations, homogeneous migrations | `10-migration/dms-and-sct.md` |  |
| SAA-C03 | 4.3 | Database replication, for example read replicas | `05-database/rds.md` |  |
| SAA-C03 | 4.3 | Database types and services, for example relational compared with non-relational, Amazon Aurora, Amazon DynamoDB | `05-database/dynamodb.md` | `05-database/rds.md`, `05-database/aurora.md` |
| SAA-C03 | 4.3 | Designing appropriate backup and retention policies, for example snapshot frequency | `01-storage/backup-and-disaster-recovery.md` |  |
| SAA-C03 | 4.3 | Determining an appropriate database engine, for example MySQL compared with PostgreSQL | `05-database/rds.md` |  |
| SAA-C03 | 4.3 | Determining cost-effective AWS database services with appropriate use cases, for example DynamoDB compared with Amazon RDS, serverless | `05-database/dynamodb.md` | `05-database/rds.md`, `05-database/aurora.md` |
| SAA-C03 | 4.3 | Determining cost-effective AWS database types, for example time series format, columnar format | `05-database/keyspaces-qldb-and-timestream.md` | `05-database/redshift.md`, `05-database/dynamodb.md` |
| SAA-C03 | 4.3 | Migrating database schemas and data to different locations and/or different database engines | `10-migration/dms-and-sct.md` |  |
| SAA-C03 | 4.4 | AWS cost management service features, for example cost allocation tags, multi-account billing | `08-management/cost-management.md` |  |
| SAA-C03 | 4.4 | AWS cost management tools with appropriate use cases, for example AWS Cost Explorer, AWS Budgets, AWS Cost and Usage Report | `08-management/cost-management.md` |  |
| SAA-C03 | 4.4 | Load balancing concepts, for example Application Load Balancer (ALB) | `02-compute/elastic-load-balancing.md` |  |
| SAA-C03 | 4.4 | NAT gateways, for example NAT instance costs compared with NAT gateway costs | `04-networking/vpc.md` |  |
| SAA-C03 | 4.4 | Network connectivity, for example private lines, dedicated lines, VPNs | `04-networking/hybrid-connectivity.md` |  |
| SAA-C03 | 4.4 | Network routing, topology and peering, for example AWS Transit Gateway, VPC peering | `04-networking/hybrid-connectivity.md` |  |
| SAA-C03 | 4.4 | Network services with appropriate use cases, for example DNS | `04-networking/route53.md` |  |
| SAA-C03 | 4.4 | Configuring appropriate NAT gateway types for a network, for example a single shared NAT gateway compared with NAT gateways for each Availability Zone | `04-networking/vpc.md` |  |
| SAA-C03 | 4.4 | Configuring appropriate network connections, for example AWS Direct Connect compared with VPN compared with internet | `04-networking/hybrid-connectivity.md` |  |
| SAA-C03 | 4.4 | Configuring appropriate network routes to minimize network transfer costs, for example Region to Region, Availability Zone to Availability Zone, private to public, AWS Global Accelerator, VPC endpoints | `08-management/cost-management.md` | `04-networking/vpc.md`, `04-networking/global-accelerator.md` |
| SAA-C03 | 4.4 | Determining strategic needs for content delivery networks (CDNs) and edge caching | `04-networking/cloudfront.md` |  |
| SAA-C03 | 4.4 | Reviewing existing workloads for network optimizations | `08-management/cost-management.md` | `04-networking/vpc.md`, `04-networking/hybrid-connectivity.md` |
| SAA-C03 | 4.4 | Selecting an appropriate throttling strategy | `04-networking/api-gateway.md` |  |
| SAA-C03 | 4.4 | Selecting the appropriate bandwidth allocation for a network device, for example a single VPN compared with multiple VPNs, Direct Connect speed | `04-networking/hybrid-connectivity.md` |  |
| SAP-C02 | Emerging | Implementing content filtering and regulatory compliance controls for generative AI services, for example by using Amazon Bedrock Guardrails | `11-ml-and-media/ai-dev-tools-and-generative-ai.md` |  |
| SAP-C02 | Emerging | Implementing access controls for generative and agentic AI applications, for example by using AgentCore Identity | `11-ml-and-media/ai-dev-tools-and-generative-ai.md` |  |
| SAP-C02 | Emerging | Designing human oversight workflows that include approval mechanisms for AI operations, for example by using AWS Step Functions | `11-ml-and-media/ai-dev-tools-and-generative-ai.md` | `06-integration/step-functions.md` |
| SAP-C02 | 1.1 | AWS Global Infrastructure | `04-networking/vpc.md` | `04-networking/route53.md` |
| SAP-C02 | 1.1 | AWS networking concepts, for example Amazon VPC, AWS Direct Connect, AWS VPN, transitive routing, AWS container services | `04-networking/hybrid-connectivity.md` | `03-containers/ecs-and-ecr.md`, `03-containers/eks.md`, `04-networking/vpc.md` |
| SAP-C02 | 1.1 | Hybrid DNS concepts, for example Amazon Route 53 Resolver, on-premises DNS integration | `04-networking/hybrid-connectivity.md` | `04-networking/route53.md` |
| SAP-C02 | 1.1 | Network segmentation, for example subnetting, IP addressing, connectivity among VPCs | `04-networking/vpc.md` |  |
| SAP-C02 | 1.1 | Network traffic monitoring | `04-networking/vpc.md` | `08-management/cloudwatch.md` |
| SAP-C02 | 1.1 | Evaluating connectivity options for multiple VPCs | `04-networking/hybrid-connectivity.md` |  |
| SAP-C02 | 1.1 | Evaluating connectivity options for on-premises, co-location and cloud integration | `04-networking/hybrid-connectivity.md` |  |
| SAP-C02 | 1.1 | Selecting AWS Regions and Availability Zones based on network and latency requirements | `04-networking/vpc.md` | `04-networking/route53.md` |
| SAP-C02 | 1.1 | Troubleshooting traffic flows by using AWS tools | `04-networking/vpc.md` | `08-management/cloudwatch.md` |
| SAP-C02 | 1.1 | Using service endpoints for service integrations | `04-networking/vpc.md` |  |
| SAP-C02 | 1.2 | AWS Identity and Access Management (IAM) and AWS IAM Identity Center | `07-security/iam.md` | `07-security/organizations-identity-center-and-control-tower.md` |
| SAP-C02 | 1.2 | Route tables, security groups and network ACLs | `04-networking/vpc.md` |  |
| SAP-C02 | 1.2 | Encryption keys and certificate management, for example AWS KMS, AWS Certificate Manager (ACM) | `07-security/kms-and-cloudhsm.md` | `07-security/acm.md` |
| SAP-C02 | 1.2 | AWS security, identity and compliance tools, for example AWS CloudTrail, IAM Access Analyzer, AWS Security Hub, Amazon Inspector | `07-security/detection-and-compliance-services.md` | `07-security/iam.md`, `08-management/cloudtrail.md` |
| SAP-C02 | 1.2 | Evaluating cross-account access management | `07-security/iam.md` |  |
| SAP-C02 | 1.2 | Integrating with third-party identity providers | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAP-C02 | 1.2 | Deploying encryption strategies for data at rest and data in transit | `07-security/kms-and-cloudhsm.md` |  |
| SAP-C02 | 1.2 | Developing a strategy for centralized security event notifications and auditing | `08-management/cloudtrail.md` | `07-security/detection-and-compliance-services.md`, `07-security/organizations-identity-center-and-control-tower.md` |
| SAP-C02 | 1.3 | Recovery time objectives (RTOs) and recovery point objectives (RPOs) | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 1.3 | Disaster recovery strategies, for example using AWS Elastic Disaster Recovery, pilot light, warm standby and multi-site | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 1.3 | Data backup and restoration | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 1.3 | Designing disaster recovery solutions based on RTO and RPO requirements | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 1.3 | Implementing architectures to automatically recover from failure | `02-compute/ec2-auto-scaling.md` | `04-networking/route53.md`, `02-compute/elastic-load-balancing.md` |
| SAP-C02 | 1.3 | Developing the optimal architecture by considering scale-up and scale-out options | `02-compute/ec2-auto-scaling.md` | `02-compute/ec2.md`, `08-management/cost-management.md` |
| SAP-C02 | 1.3 | Designing an effective backup and restoration strategy | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 1.4 | AWS Organizations and AWS Control Tower | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAP-C02 | 1.4 | Multi-account event notifications | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAP-C02 | 1.4 | AWS resource sharing across environments | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAP-C02 | 1.4 | Evaluating the most appropriate account structure for organizational requirements | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAP-C02 | 1.4 | Recommending a strategy for central logging and event notifications | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAP-C02 | 1.4 | Developing a multi-account governance model | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAP-C02 | 1.5 | AWS cost and usage monitoring tools, for example AWS Trusted Advisor, AWS Pricing Calculator, AWS Cost Explorer, AWS Budgets | `08-management/cost-management.md` | `08-management/config-trusted-advisor-health-and-well-architected.md` |
| SAP-C02 | 1.5 | AWS purchasing options, for example Reserved Instances, Savings Plans, Spot Instances | `02-compute/ec2.md` | `08-management/cost-management.md` |
| SAP-C02 | 1.5 | AWS rightsizing visibility tools, for example AWS Compute Optimizer, Amazon S3 Storage Lens | `08-management/cost-management.md` | `01-storage/s3.md` |
| SAP-C02 | 1.5 | Monitoring cost and usage with AWS tools | `08-management/cost-management.md` |  |
| SAP-C02 | 1.5 | Developing an effective tagging strategy that maps costs to business units | `08-management/cost-management.md` |  |
| SAP-C02 | 1.5 | Understanding how purchasing options affect cost and performance | `02-compute/ec2.md` |  |
| SAP-C02 | 2.1 | Infrastructure as code (IaC), for example AWS CloudFormation | `08-management/cloudformation.md` |  |
| SAP-C02 | 2.1 | Continuous integration and continuous delivery (CI/CD) | `08-management/developer-tools-and-cicd.md` | `03-containers/ecs-and-ecr.md`, `02-compute/elastic-beanstalk.md` |
| SAP-C02 | 2.1 | Change management processes | `08-management/systems-manager.md` |  |
| SAP-C02 | 2.1 | Configuration management tools, for example AWS Systems Manager | `08-management/systems-manager.md` |  |
| SAP-C02 | 2.1 | Determining an application or upgrade path for new services and features | `08-management/developer-tools-and-cicd.md` |  |
| SAP-C02 | 2.1 | Selecting services to develop deployment strategies and implement appropriate rollback mechanisms | `08-management/developer-tools-and-cicd.md` | `02-compute/elastic-beanstalk.md`, `03-containers/ecs-and-ecr.md`, `02-compute/lambda.md` |
| SAP-C02 | 2.1 | Adopting managed services as needed to reduce infrastructure provisioning and patching overhead | `08-management/service-catalog.md` | `08-management/systems-manager.md`, `02-compute/elastic-beanstalk.md`, `03-containers/ecs-and-ecr.md` |
| SAP-C02 | 2.1 | Making advanced technologies accessible by delegating complex development and deployment tasks to AWS | `08-management/service-catalog.md` | `08-management/cloudformation.md` |
| SAP-C02 | 2.2 | AWS Global Infrastructure | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 2.2 | AWS networking concepts, for example Amazon Route 53, routing methods | `04-networking/route53.md` |  |
| SAP-C02 | 2.2 | RTOs and RPOs | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 2.2 | Disaster recovery scenarios, for example backup and restore, pilot light, warm standby, multi-site | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 2.2 | Disaster recovery solutions on AWS | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 2.2 | Configuring disaster recovery solutions | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 2.2 | Configuring data and database replication | `01-storage/backup-and-disaster-recovery.md` | `01-storage/s3.md`, `05-database/rds.md`, `05-database/dynamodb.md` |
| SAP-C02 | 2.2 | Performing disaster recovery testing | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 2.2 | Architecting a backup solution that is automated, is cost-effective, and supports business continuity across multiple Availability Zones or AWS Regions | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 2.2 | Designing an architecture that provides application and infrastructure availability in the event of a disruption | `01-storage/backup-and-disaster-recovery.md` | `04-networking/route53.md`, `02-compute/ec2-auto-scaling.md` |
| SAP-C02 | 2.2 | Using processes and components for centralized monitoring to proactively recover from system failures | `08-management/cloudwatch.md` |  |
| SAP-C02 | 2.3 | IAM | `07-security/iam.md` |  |
| SAP-C02 | 2.3 | Route tables, security groups and network ACLs | `04-networking/vpc.md` |  |
| SAP-C02 | 2.3 | Encryption options for data at rest and data in transit | `07-security/kms-and-cloudhsm.md` | `07-security/acm.md` |
| SAP-C02 | 2.3 | AWS service endpoints | `04-networking/vpc.md` |  |
| SAP-C02 | 2.3 | Credential management services | `07-security/secrets-manager-and-parameter-store.md` |  |
| SAP-C02 | 2.3 | AWS managed security services, for example AWS Shield, AWS WAF, Amazon GuardDuty, AWS Security Hub | `07-security/waf-shield-firewall-manager-and-network-firewall.md` | `07-security/detection-and-compliance-services.md` |
| SAP-C02 | 2.3 | Specifying IAM users and IAM roles that adhere to the principle of least privilege access | `07-security/iam.md` |  |
| SAP-C02 | 2.3 | Specifying inbound and outbound network flows by using security group rules and network ACL rules | `04-networking/vpc.md` |  |
| SAP-C02 | 2.3 | Developing attack mitigation strategies for large-scale web applications | `07-security/waf-shield-firewall-manager-and-network-firewall.md` |  |
| SAP-C02 | 2.3 | Developing encryption strategies for data at rest and data in transit | `07-security/kms-and-cloudhsm.md` | `07-security/acm.md` |
| SAP-C02 | 2.3 | Specifying service endpoints for service integrations | `04-networking/vpc.md` |  |
| SAP-C02 | 2.3 | Developing strategies for patch management to remain compliant with organizational standards | `08-management/systems-manager.md` |  |
| SAP-C02 | 2.4 | AWS Global Infrastructure | `01-storage/backup-and-disaster-recovery.md` | `04-networking/route53.md` |
| SAP-C02 | 2.4 | AWS storage services and replication strategies, for example Amazon S3, Amazon RDS, Amazon ElastiCache | `01-storage/s3.md` | `05-database/rds.md`, `05-database/elasticache-and-memorydb.md` |
| SAP-C02 | 2.4 | Multi-AZ and multi-Region architectures | `01-storage/backup-and-disaster-recovery.md` | `04-networking/route53.md`, `05-database/aurora.md` |
| SAP-C02 | 2.4 | Auto scaling policies and events | `02-compute/ec2-auto-scaling.md` |  |
| SAP-C02 | 2.4 | Application integration, for example Amazon SNS, Amazon SQS, AWS Step Functions | `06-integration/sqs.md` | `06-integration/sns.md`, `06-integration/step-functions.md` |
| SAP-C02 | 2.4 | Service quotas and limits | `08-management/config-trusted-advisor-health-and-well-architected.md` | `08-management/aws-api-cli-and-sdks.md` |
| SAP-C02 | 2.4 | Designing highly available application environments based on business requirements | `01-storage/backup-and-disaster-recovery.md` | `02-compute/elastic-load-balancing.md`, `02-compute/ec2-auto-scaling.md` |
| SAP-C02 | 2.4 | Using advanced techniques to design for failure and ensure seamless system recoverability | `01-storage/backup-and-disaster-recovery.md` | `04-networking/route53.md` |
| SAP-C02 | 2.4 | Implementing loosely coupled dependencies | `06-integration/sqs.md` |  |
| SAP-C02 | 2.4 | Operating and maintaining high-availability architectures, for example application failovers, database failovers | `01-storage/backup-and-disaster-recovery.md` | `05-database/rds.md`, `05-database/aurora.md` |
| SAP-C02 | 2.4 | Using AWS managed services for high availability | `01-storage/backup-and-disaster-recovery.md` | `01-storage/s3.md`, `05-database/rds.md` |
| SAP-C02 | 2.4 | Implementing DNS routing policies, for example Route 53 latency-based routing, geolocation routing, simple routing | `04-networking/route53.md` |  |
| SAP-C02 | 2.5 | Performance monitoring technologies | `08-management/cloudwatch.md` |  |
| SAP-C02 | 2.5 | Storage options on AWS | `01-storage/s3.md` |  |
| SAP-C02 | 2.5 | Instance families and use cases | `02-compute/ec2.md` |  |
| SAP-C02 | 2.5 | Purpose-built databases | `05-database/dynamodb.md` | `05-database/redshift.md`, `09-analytics/opensearch.md` |
| SAP-C02 | 2.5 | Designing large-scale application architectures for a variety of access patterns | `05-database/dynamodb.md` | `09-analytics/kinesis.md`, `05-database/redshift.md`, `04-networking/api-gateway.md` |
| SAP-C02 | 2.5 | Designing an elastic architecture based on business objectives | `02-compute/ec2-auto-scaling.md` | `02-compute/ec2.md`, `02-compute/lambda.md` |
| SAP-C02 | 2.5 | Applying design patterns to meet performance objectives with caching, buffering and replicas | `05-database/elasticache-and-memorydb.md` | `06-integration/sqs.md`, `05-database/rds.md` |
| SAP-C02 | 2.5 | Developing a process methodology for selecting purpose-built services for required tasks | `05-database/dynamodb.md` | `11-ml-and-media/ml-managed-services.md`, `09-analytics/athena.md`, `09-analytics/emr.md` |
| SAP-C02 | 2.5 | Designing a rightsizing strategy | `08-management/cost-management.md` |  |
| SAP-C02 | 2.6 | AWS cost and usage monitoring tools, for example AWS Cost Explorer, AWS Trusted Advisor, AWS Pricing Calculator | `08-management/cost-management.md` | `08-management/config-trusted-advisor-health-and-well-architected.md` |
| SAP-C02 | 2.6 | Pricing models, for example Reserved Instances, AWS Savings Plans | `08-management/cost-management.md` |  |
| SAP-C02 | 2.6 | Storage tiering | `01-storage/s3.md` |  |
| SAP-C02 | 2.6 | Data transfer costs | `08-management/cost-management.md` |  |
| SAP-C02 | 2.6 | AWS managed service offerings | `08-management/cost-management.md` | `02-compute/lambda.md`, `05-database/rds.md`, `08-management/service-catalog.md` |
| SAP-C02 | 2.6 | Identifying opportunities to select and rightsize infrastructure for cost-effective resources | `08-management/cost-management.md` | `02-compute/ec2.md`, `02-compute/ec2-auto-scaling.md` |
| SAP-C02 | 2.6 | Identifying appropriate pricing models | `08-management/cost-management.md` |  |
| SAP-C02 | 2.6 | Performing data transfer modeling and selecting services to reduce data transfer costs | `08-management/cost-management.md` |  |
| SAP-C02 | 2.6 | Developing a strategy and implementing controls for expenditure and usage awareness | `08-management/cost-management.md` |  |
| SAP-C02 | 3.1 | Alerting and automatic remediation strategies | `06-integration/eventbridge.md` | `08-management/systems-manager.md`, `08-management/cloudwatch.md` |
| SAP-C02 | 3.1 | Disaster recovery planning | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 3.1 | Monitoring and logging solutions, for example Amazon CloudWatch | `08-management/cloudwatch.md` |  |
| SAP-C02 | 3.1 | CI/CD pipelines and deployment strategies, for example blue/green, all-at-once, rolling | `08-management/developer-tools-and-cicd.md` |  |
| SAP-C02 | 3.1 | Configuration management tools, for example AWS Systems Manager | `08-management/systems-manager.md` |  |
| SAP-C02 | 3.1 | Determining the most appropriate logging and monitoring strategy | `08-management/cloudwatch.md` |  |
| SAP-C02 | 3.1 | Evaluating current deployment processes for improvement opportunities | `08-management/developer-tools-and-cicd.md` |  |
| SAP-C02 | 3.1 | Prioritizing opportunities for automation within a solution stack | `08-management/cloudformation.md` | `08-management/systems-manager.md`, `06-integration/eventbridge.md` |
| SAP-C02 | 3.1 | Recommending the appropriate AWS solution to enable configuration management automation | `08-management/systems-manager.md` |  |
| SAP-C02 | 3.1 | Engineering failure scenario activities to support and exercise an understanding of recovery actions | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 3.2 | Data retention, data sensitivity and data regulatory requirements | `07-security/detection-and-compliance-services.md` | `01-storage/s3.md`, `01-storage/backup-and-disaster-recovery.md` |
| SAP-C02 | 3.2 | Automated monitoring and remediation strategies, for example AWS Config rules | `07-security/detection-and-compliance-services.md` |  |
| SAP-C02 | 3.2 | Secrets management, for example Systems Manager, AWS Secrets Manager | `07-security/secrets-manager-and-parameter-store.md` | `08-management/systems-manager.md` |
| SAP-C02 | 3.2 | Principle of least privilege access | `07-security/iam.md` |  |
| SAP-C02 | 3.2 | Security-specific AWS solutions | `07-security/detection-and-compliance-services.md` | `07-security/waf-shield-firewall-manager-and-network-firewall.md`, `07-security/iam.md` |
| SAP-C02 | 3.2 | Patching practices | `08-management/systems-manager.md` |  |
| SAP-C02 | 3.2 | Backup practices and methods | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 3.2 | Evaluating a strategy for the secure management of secrets and credentials | `07-security/secrets-manager-and-parameter-store.md` |  |
| SAP-C02 | 3.2 | Auditing an environment for least privilege access | `07-security/iam.md` |  |
| SAP-C02 | 3.2 | Reviewing implemented solutions to ensure security at every layer | `07-security/detection-and-compliance-services.md` | `07-security/iam.md`, `04-networking/vpc.md` |
| SAP-C02 | 3.2 | Reviewing comprehensive traceability of users and services | `08-management/cloudtrail.md` |  |
| SAP-C02 | 3.2 | Prioritizing automated responses to the detection of vulnerabilities | `07-security/detection-and-compliance-services.md` | `08-management/systems-manager.md` |
| SAP-C02 | 3.2 | Designing and implementing a patch and update process | `08-management/systems-manager.md` |  |
| SAP-C02 | 3.2 | Designing and implementing a backup process | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 3.2 | Employing remediation techniques | `08-management/systems-manager.md` | `07-security/detection-and-compliance-services.md` |
| SAP-C02 | 3.3 | High-performing systems architectures, for example auto scaling, instance fleets, placement groups | `02-compute/ec2.md` | `02-compute/ec2-auto-scaling.md` |
| SAP-C02 | 3.3 | Global service offerings, for example AWS Global Accelerator, Amazon CloudFront, edge computing services | `04-networking/global-accelerator.md` | `04-networking/cloudfront.md` |
| SAP-C02 | 3.3 | Monitoring tool sets and services, for example CloudWatch | `08-management/cloudwatch.md` |  |
| SAP-C02 | 3.3 | Service level agreements (SLAs) and key performance indicators (KPIs) | `08-management/cloudwatch.md` |  |
| SAP-C02 | 3.3 | Translating business requirements to measurable metrics | `08-management/cloudwatch.md` |  |
| SAP-C02 | 3.3 | Testing potential remediation solutions and making recommendations | `08-management/cloudwatch.md` | `02-compute/ec2.md`, `02-compute/ec2-auto-scaling.md` |
| SAP-C02 | 3.3 | Proposing opportunities for the adoption of new technologies and managed services | `08-management/config-trusted-advisor-health-and-well-architected.md` | `08-management/service-catalog.md`, `11-ml-and-media/ml-managed-services.md`, `02-compute/lambda.md` |
| SAP-C02 | 3.3 | Assessing solutions and applying rightsizing based on requirements | `08-management/cost-management.md` |  |
| SAP-C02 | 3.3 | Identifying and examining performance bottlenecks | `08-management/cloudwatch.md` | `02-compute/ec2.md`, `05-database/rds.md` |
| SAP-C02 | 3.4 | AWS Global Infrastructure | `04-networking/vpc.md` | `04-networking/route53.md` |
| SAP-C02 | 3.4 | Data replication methods | `01-storage/backup-and-disaster-recovery.md` | `01-storage/s3.md`, `05-database/rds.md` |
| SAP-C02 | 3.4 | Scaling methodologies, for example load balancing, auto scaling | `02-compute/ec2-auto-scaling.md` | `02-compute/elastic-load-balancing.md` |
| SAP-C02 | 3.4 | High availability and resiliency | `01-storage/backup-and-disaster-recovery.md` | `02-compute/elastic-load-balancing.md`, `04-networking/route53.md` |
| SAP-C02 | 3.4 | Disaster recovery methods and tools | `01-storage/backup-and-disaster-recovery.md` |  |
| SAP-C02 | 3.4 | Service quotas and limits | `08-management/config-trusted-advisor-health-and-well-architected.md` | `08-management/aws-api-cli-and-sdks.md` |
| SAP-C02 | 3.4 | Understanding application growth and usage trends | `02-compute/ec2-auto-scaling.md` |  |
| SAP-C02 | 3.4 | Evaluating existing architecture to determine areas that are not sufficiently reliable | `01-storage/backup-and-disaster-recovery.md` | `08-management/cloudwatch.md` |
| SAP-C02 | 3.4 | Remediating single points of failure | `02-compute/elastic-load-balancing.md` |  |
| SAP-C02 | 3.4 | Enabling data replication, self-healing and elastic features and services | `01-storage/backup-and-disaster-recovery.md` | `02-compute/ec2-auto-scaling.md`, `01-storage/s3.md` |
| SAP-C02 | 3.5 | Cost-conscious architecture choices, for example using Spot Instances, scaling policies and rightsizing resources | `08-management/cost-management.md` | `02-compute/ec2.md`, `02-compute/ec2-auto-scaling.md` |
| SAP-C02 | 3.5 | Price model adoptions, for example Reserved Instances, AWS Savings Plans | `08-management/cost-management.md` |  |
| SAP-C02 | 3.5 | Networking and data transfer costs | `08-management/cost-management.md` |  |
| SAP-C02 | 3.5 | Cost management, alerting and reporting | `08-management/cost-management.md` |  |
| SAP-C02 | 3.5 | Analyzing usage reports to identify underutilized and overutilized resources | `08-management/cost-management.md` | `02-compute/ec2.md`, `02-compute/ec2-auto-scaling.md` |
| SAP-C02 | 3.5 | Using AWS solutions to identify unused resources | `08-management/cost-management.md` | `02-compute/ec2.md`, `02-compute/ec2-auto-scaling.md`, `08-management/config-trusted-advisor-health-and-well-architected.md` |
| SAP-C02 | 3.5 | Designing billing alarms based on expected usage patterns | `08-management/cost-management.md` |  |
| SAP-C02 | 3.5 | Investigating AWS Cost and Usage Reports at a granular level | `08-management/cost-management.md` |  |
| SAP-C02 | 3.5 | Using tagging for cost allocation and reporting | `08-management/cost-management.md` |  |
| SAP-C02 | 4.1 | Migration assessment and tracking tools, for example AWS Migration Hub | `10-migration/migration-hub-discovery-and-strategy.md` |  |
| SAP-C02 | 4.1 | Portfolio assessment | `10-migration/migration-hub-discovery-and-strategy.md` |  |
| SAP-C02 | 4.1 | Asset planning | `10-migration/migration-hub-discovery-and-strategy.md` |  |
| SAP-C02 | 4.1 | Prioritization and migration of workloads, for example wave planning | `10-migration/migration-hub-discovery-and-strategy.md` |  |
| SAP-C02 | 4.1 | Completing an application migration assessment | `10-migration/migration-hub-discovery-and-strategy.md` |  |
| SAP-C02 | 4.1 | Evaluating applications according to the seven common migration strategies (7Rs) | `10-migration/migration-hub-discovery-and-strategy.md` |  |
| SAP-C02 | 4.1 | Evaluating total cost of ownership (TCO) | `10-migration/migration-hub-discovery-and-strategy.md` |  |
| SAP-C02 | 4.2 | Data migration options and tools, for example AWS DataSync, AWS Transfer Family, AWS Snow Family, Amazon S3 Transfer Acceleration | `01-storage/transfer-family-and-datasync.md` | `01-storage/s3.md`, `01-storage/snow-family.md` |
| SAP-C02 | 4.2 | Application migration tools, for example AWS Application Discovery Service, AWS Application Migration Service | `10-migration/application-migration-service.md` | `10-migration/migration-hub-discovery-and-strategy.md` |
| SAP-C02 | 4.2 | AWS networking services and DNS, for example AWS Direct Connect, AWS Site-to-Site VPN, Amazon Route 53 | `04-networking/hybrid-connectivity.md` | `04-networking/route53.md` |
| SAP-C02 | 4.2 | Identity services, for example AWS IAM Identity Center, AWS Directory Service | `07-security/directory-service.md` | `07-security/organizations-identity-center-and-control-tower.md`, `07-security/iam.md` |
| SAP-C02 | 4.2 | Database migration tools, for example AWS DMS, AWS SCT | `10-migration/dms-and-sct.md` |  |
| SAP-C02 | 4.2 | Governance tools, for example AWS Control Tower, AWS Organizations | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAP-C02 | 4.2 | Selecting the appropriate database transfer mechanism | `10-migration/dms-and-sct.md` |  |
| SAP-C02 | 4.2 | Selecting the appropriate application transfer mechanism | `10-migration/application-migration-service.md` |  |
| SAP-C02 | 4.2 | Selecting the appropriate data transfer service and migration strategy | `01-storage/transfer-family-and-datasync.md` |  |
| SAP-C02 | 4.2 | Applying the appropriate security methods to migration tools | `07-security/iam.md` | `07-security/kms-and-cloudhsm.md`, `04-networking/vpc.md` |
| SAP-C02 | 4.2 | Selecting the appropriate governance model | `07-security/organizations-identity-center-and-control-tower.md` |  |
| SAP-C02 | 4.3 | Compute services, for example Amazon EC2, AWS Elastic Beanstalk | `02-compute/ec2.md` | `02-compute/elastic-beanstalk.md` |
| SAP-C02 | 4.3 | Containers, for example Amazon ECS, Amazon EKS, AWS Fargate, Amazon ECR | `03-containers/ecs-and-ecr.md` | `03-containers/eks.md` |
| SAP-C02 | 4.3 | AWS storage services, for example Amazon EBS, Amazon EFS, Amazon FSx, Amazon S3, AWS Storage Gateway Volume Gateway | `01-storage/s3.md` | `01-storage/ebs.md`, `01-storage/efs.md`, `01-storage/fsx.md`, `01-storage/storage-gateway.md` |
| SAP-C02 | 4.3 | Databases, for example Amazon DynamoDB, Amazon OpenSearch Service, Amazon RDS, self-managed databases on Amazon EC2 | `05-database/dynamodb.md` | `05-database/rds.md`, `09-analytics/opensearch.md`, `02-compute/ec2.md` |
| SAP-C02 | 4.3 | Selecting the appropriate compute platform | `02-compute/ec2.md` | `02-compute/elastic-beanstalk.md`, `02-compute/lambda.md` |
| SAP-C02 | 4.3 | Selecting the appropriate container hosting platform | `03-containers/ecs-and-ecr.md` |  |
| SAP-C02 | 4.3 | Selecting the appropriate storage service | `01-storage/s3.md` | `01-storage/ebs.md`, `01-storage/efs.md`, `01-storage/fsx.md` |
| SAP-C02 | 4.3 | Selecting the appropriate database platform | `05-database/dynamodb.md` | `05-database/rds.md`, `09-analytics/opensearch.md` |
| SAP-C02 | 4.4 | Serverless compute offerings, for example AWS Lambda | `02-compute/lambda.md` |  |
| SAP-C02 | 4.4 | Containers, for example Amazon ECS, Amazon EKS, Fargate | `03-containers/ecs-and-ecr.md` | `03-containers/eks.md` |
| SAP-C02 | 4.4 | AWS storage services, for example Amazon S3, Amazon EFS | `01-storage/s3.md` | `01-storage/efs.md` |
| SAP-C02 | 4.4 | Purpose-built databases, for example DynamoDB, Amazon Aurora Serverless, Amazon ElastiCache | `05-database/dynamodb.md` | `05-database/aurora.md`, `05-database/elasticache-and-memorydb.md` |
| SAP-C02 | 4.4 | Integration services, for example Amazon SQS, Amazon SNS, Amazon EventBridge, AWS Step Functions | `06-integration/sqs.md` | `06-integration/sns.md`, `06-integration/eventbridge.md`, `06-integration/step-functions.md` |
| SAP-C02 | 4.4 | Identifying opportunities to decouple application components | `06-integration/sqs.md` | `06-integration/sns.md`, `06-integration/eventbridge.md` |
| SAP-C02 | 4.4 | Identifying opportunities for serverless solutions | `02-compute/lambda.md` | `03-containers/ecs-and-ecr.md` |
| SAP-C02 | 4.4 | Selecting the appropriate service for containers | `03-containers/ecs-and-ecr.md` |  |
| SAP-C02 | 4.4 | Identifying opportunities for purpose-built databases | `05-database/dynamodb.md` | `05-database/aurora.md`, `05-database/elasticache-and-memorydb.md` |
| SAP-C02 | 4.4 | Selecting the appropriate application integration service | `06-integration/eventbridge.md` | `06-integration/sqs.md`, `06-integration/sns.md`, `06-integration/step-functions.md` |

## Unit ownership index

This reverse index is the writer-dispatch view. Its references use the
same task, kind and source-order numbering defined above.

| Unit | Service focus | Tier | Owned SAA-C03 bullets | Owned SAP-C02 bullets |
|---|---|---|---|---|
| `01-storage/s3.md` | Amazon S3, S3 Glacier storage classes, S3 Express One Zone, Access Points, Multi-Region Access Points, Object Lambda, Storage Lens, Batch Operations, Transfer Acceleration, Requester Pays, static website hosting, event notifications, Inventory | XL | 1.3-S6, 2.1-K13, 2.2-K11, 3.1-K2, 3.1-K3, 3.1-S1, 3.1-S2, 4.1-K1, 4.1-K4, 4.1-K7, 4.1-K9, 4.1-K10, 4.1-K11, 4.1-S1, 4.1-S5, 4.1-S8, 4.1-S9, 4.1-S10 | 2.4-K2, 2.5-K2, 2.6-K3, 4.3-K3, 4.3-S3, 4.4-K3 |
| `01-storage/ebs.md` | Amazon EBS | M | 4.1-K6, 4.1-S2 | None |
| `01-storage/efs.md` | Amazon EFS | S | 4.1-S4 | None |
| `01-storage/fsx.md` | Amazon FSx for Windows File Server, Lustre, NetApp ONTAP, OpenZFS, plus File Cache | S | None | None |
| `01-storage/storage-gateway.md` | S3 File Gateway, FSx File Gateway, Volume Gateway cached and stored, Tape Gateway | S | 3.1-K1 | None |
| `01-storage/backup-and-disaster-recovery.md` | AWS Backup with plans, vaults, cross-account and cross-Region copy, logically air-gapped vaults, Backup Audit Manager. AWS Elastic Disaster Recovery. The DR strategy reference | L | 1.3-K2, 1.3-S5, 2.2-K4, 2.2-S2, 2.2-S5, 2.2-S6, 4.1-K5, 4.1-S6, 4.2-S4, 4.3-K4, 4.3-S1 | 1.3-K1, 1.3-K2, 1.3-K3, 1.3-S1, 1.3-S4, 2.2-K1, 2.2-K3, 2.2-K4, 2.2-K5, 2.2-S1, 2.2-S2, 2.2-S3, 2.2-S4, 2.2-S5, 2.4-K1, 2.4-K3, 2.4-S1, 2.4-S2, 2.4-S4, 2.4-S5, 3.1-K2, 3.1-S5, 3.2-K7, 3.2-S7, 3.4-K2, 3.4-K4, 3.4-K5, 3.4-S2, 3.4-S4 |
| `01-storage/snow-family.md` | AWS Snow Family current lineup, device selection by volume and connectivity, transfer time arithmetic against network transfer, edge compute, OpsHub, security | S | None | None |
| `01-storage/transfer-family-and-datasync.md` | AWS Transfer Family for SFTP, FTPS, FTP, AS2 and connectors. AWS DataSync agents, locations, tasks, schedules, cross-cloud. S3 Transfer Acceleration as comparison | S | 3.5-K3, 3.5-K6, 3.5-S3, 4.1-K8, 4.1-S3, 4.1-S7 | 4.2-K1, 4.2-S3 |
| `02-compute/ec2.md` | Amazon EC2 | L | 2.1-S6, 3.2-S3, 4.2-K4, 4.2-K7, 4.2-S3, 4.2-S5, 4.2-S6 | 1.5-K2, 1.5-S3, 2.5-K3, 3.3-K1, 4.3-K1, 4.3-S1 |
| `02-compute/ami.md` | Amazon Machine Images | S | 2.2-K7 | None |
| `02-compute/ec2-auto-scaling.md` | EC2 Auto Scaling | M | 2.1-K6, 2.1-S2, 3.2-K4, 3.2-S2, 4.2-K9, 4.2-S2 | 1.3-S2, 1.3-S3, 2.4-K4, 2.5-S2, 3.4-K3, 3.4-S1 |
| `02-compute/elastic-load-balancing.md` | ALB, NLB, Gateway Load Balancer, Classic Load Balancer | M | 2.1-K9, 2.2-K8, 2.2-S4, 2.2-S7, 3.4-K3, 3.4-S4, 4.2-S1, 4.4-K3 | 3.4-S3 |
| `02-compute/lambda.md` | AWS Lambda | L | 2.1-K12, 2.1-S5, 3.2-K5, 3.2-S4 | 4.4-K1, 4.4-S2 |
| `02-compute/elastic-beanstalk.md` | AWS Elastic Beanstalk | S | None | None |
| `02-compute/batch.md` | AWS Batch | S | 3.2-K1 | None |
| `02-compute/other-compute-and-end-user.md` | Amazon Lightsail, AWS App Runner, Amazon AppStream 2.0, Amazon WorkSpaces, AWS Outposts, AWS Local Zones, AWS Wavelength, AWS Serverless Application Repository, VMware Cloud on AWS | XS group | 3.2-K2, 4.2-K5, 4.2-K6 | None |
| `03-containers/ecs-and-ecr.md` | Amazon ECS | M | 2.1-K4, 2.1-K8, 2.1-K14, 2.1-S4, 3.2-K6, 4.2-K8 | 4.3-K2, 4.3-S2, 4.4-K2, 4.4-S3 |
| `03-containers/eks.md` | Amazon EKS | M | None | None |
| `04-networking/vpc.md` | Amazon VPC | XL | 1.1-K3, 1.2-K2, 1.2-K3, 1.2-S1, 1.2-S2, 2.1-K10, 2.2-K3, 3.4-K2, 3.4-S2, 3.4-S3, 4.2-K3, 4.4-K4, 4.4-S1 | 1.1-K1, 1.1-K4, 1.1-K5, 1.1-S3, 1.1-S4, 1.1-S5, 1.2-K2, 2.3-K2, 2.3-K4, 2.3-S2, 2.3-S5, 3.4-K1 |
| `04-networking/hybrid-connectivity.md` | AWS Direct Connect dedicated and hosted, virtual interfaces, Direct Connect Gateway, link aggregation groups, resiliency models, MACsec, SiteLink. Site-to-Site VPN with virtual private gateway compared with Transit Gateway, accelerated VPN, ECMP. Client VPN. Transit Gateway in depth | L | 1.2-S4, 3.4-K4, 3.4-S1, 4.4-K5, 4.4-K6, 4.4-S2, 4.4-S7 | 1.1-K2, 1.1-K3, 1.1-S1, 1.1-S2, 4.2-K3 |
| `04-networking/route53.md` | Amazon Route 53 | L | 2.2-K1, 2.2-K6, 4.4-K7 | 2.2-K2, 2.4-S6 |
| `04-networking/cloudfront.md` | Amazon CloudFront | M | 2.1-K7, 3.4-K1, 4.4-S4 | None |
| `04-networking/global-accelerator.md` | AWS Global Accelerator | S | None | 3.3-K2 |
| `04-networking/api-gateway.md` | Amazon API Gateway | L | 2.1-K1, 4.4-S6 | None |
| `05-database/rds.md` | Amazon RDS | L | 2.1-K15, 2.2-K9, 3.3-K1, 3.3-K4, 3.3-K5, 3.3-K7, 3.3-S1, 3.3-S2, 3.3-S3, 4.3-K6, 4.3-K8, 4.3-S2 | None |
| `05-database/aurora.md` | Amazon Aurora | M | None | None |
| `05-database/dynamodb.md` | Amazon DynamoDB, the largest database module in the Professional course at 110 lessons, so write to the top of the L range | L | 2.1-S7, 3.3-K3, 3.3-K8, 3.3-S4, 4.3-K5, 4.3-K9, 4.3-S3 | 2.5-K4, 2.5-S1, 2.5-S4, 4.3-K4, 4.3-S4, 4.4-K4, 4.4-S4 |
| `05-database/elasticache-and-memorydb.md` | Amazon ElastiCache with Valkey, Redis OSS and Memcached engines, cluster mode, Multi-AZ with automatic failover, Global Datastore, ElastiCache Serverless, caching strategies lazy loading, write-through and TTL. Amazon MemoryDB as a durable in-memory database | M | 2.1-K3, 3.3-K2, 3.3-S5, 4.3-K3 | 2.5-S3 |
| `05-database/documentdb.md` | Amazon DocumentDB with MongoDB compatibility | S | None | None |
| `05-database/neptune.md` | Amazon Neptune | S | None | None |
| `05-database/keyspaces-qldb-and-timestream.md` | Amazon Keyspaces for Apache Cassandra. Amazon QLDB, verify end of support status. Amazon Timestream for LiveAnalytics and for InfluxDB | XS group | 4.3-S4 | None |
| `05-database/redshift.md` | Amazon Redshift | S | None | None |
| `06-integration/sqs.md` | Amazon SQS | M | 2.1-K2, 2.1-S3, 3.2-S1 | 2.4-K5, 2.4-S3, 4.4-K5, 4.4-S1 |
| `06-integration/sns.md` | Amazon SNS | M | 2.1-K11, 3.2-K3 | None |
| `06-integration/eventbridge.md` | Amazon EventBridge | M | 2.1-K5, 2.1-S1, 2.2-K5 | 3.1-K1, 4.4-S5 |
| `06-integration/step-functions.md` | AWS Step Functions | S | 2.1-K16 | None |
| `06-integration/amazon-mq.md` | Amazon MQ | S | None | None |
| `06-integration/appflow-appsync-amplify-ses-pinpoint.md` | Amazon AppFlow. AWS AppSync with GraphQL, resolvers, subscriptions and the Events API. AWS Amplify hosting and backend. Amazon SES. Amazon Pinpoint, verify end of support status | XS group | None | None |
| `07-security/iam.md` | IAM | L | 1.1-K2, 1.1-K4, 1.1-K5, 1.1-S1, 1.1-S2, 1.1-S3, 1.1-S5, 3.5-K5 | 1.2-K1, 1.2-S1, 2.3-K1, 2.3-S1, 3.2-K4, 3.2-S2, 4.2-S4 |
| `07-security/organizations-identity-center-and-control-tower.md` | AWS Organizations | L | 1.1-K1, 1.1-S4 | 1.2-S2, 1.4-K1, 1.4-K2, 1.4-K3, 1.4-S1, 1.4-S2, 1.4-S3, 4.2-K6, 4.2-S5 |
| `07-security/kms-and-cloudhsm.md` | AWS KMS | M | 1.3-K4, 1.3-S2, 1.3-S4, 1.3-S7 | 1.2-K3, 1.2-S3, 2.3-K3, 2.3-S4 |
| `07-security/acm.md` | AWS Certificate Manager | S | 1.3-S3 | None |
| `07-security/secrets-manager-and-parameter-store.md` | AWS Secrets Manager | S | 1.2-K1 | 2.3-K5, 3.2-K3, 3.2-S1 |
| `07-security/cognito.md` | Amazon Cognito | M | 1.2-K4 | None |
| `07-security/directory-service.md` | AWS Directory Service | S | 1.1-S6 | 4.2-K4 |
| `07-security/waf-shield-firewall-manager-and-network-firewall.md` | AWS WAF | M | 1.2-K6, 1.2-S3 | 2.3-K6, 2.3-S3 |
| `07-security/detection-and-compliance-services.md` | Amazon GuardDuty findings and protection plans including malware protection. Amazon Inspector for EC2, ECR and Lambda. Amazon Macie for S3 sensitive data discovery. Amazon Detective. AWS Security Hub with standards, finding aggregation and automation rules. AWS Audit Manager, verify status. AWS Artifact. AWS Config with rules, conformance packs, remediation and aggregators | M | 1.2-K5, 1.3-K3, 1.3-S1 | 1.2-K4, 3.2-K1, 3.2-K2, 3.2-K5, 3.2-S3, 3.2-S5 |
| `08-management/aws-api-cli-and-sdks.md` | The AWS API | L | 2.2-K10 | None |
| `08-management/cloudformation.md` | AWS CloudFormation | L | 2.2-S1 | 2.1-K1, 3.1-S3 |
| `08-management/cloudwatch.md` | Amazon CloudWatch | L | 2.2-K12, 2.2-S3 | 2.2-S6, 2.5-K1, 3.1-K3, 3.1-S1, 3.3-K3, 3.3-K4, 3.3-S1, 3.3-S2, 3.3-S5 |
| `08-management/cloudtrail.md` | AWS CloudTrail | M | None | 1.2-S4, 3.2-S4 |
| `08-management/systems-manager.md` | AWS Systems Manager | M | None | 2.1-K3, 2.1-K4, 2.3-S6, 3.1-K5, 3.1-S4, 3.2-K6, 3.2-S6, 3.2-S8 |
| `08-management/service-catalog.md` | AWS Service Catalog | S | None | 2.1-S3, 2.1-S4 |
| `08-management/config-trusted-advisor-health-and-well-architected.md` | AWS Config recorder, aggregators and conformance packs, with rules covered in the security detection unit. AWS Trusted Advisor checks, priority and organizational view. AWS Health Dashboard account and organizational views with EventBridge integration. AWS License Manager. AWS Well-Architected Tool. Service Quotas | XS group | None | 2.4-K6, 3.3-S3, 3.4-K6 |
| `08-management/cost-management.md` | AWS Cost Explorer. AWS Budgets and budget actions. AWS Cost and Usage Report including CUR 2.0 and Data Exports. Cost allocation tags and cost categories. Consolidated billing with Reserved Instance and Savings Plans sharing. Savings Plans types. AWS Compute Optimizer. AWS Pricing Calculator. S3 Storage Lens. AWS Cost Anomaly Detection. AWS Billing Conductor. The data transfer cost rules | L | 4.1-K2, 4.1-K3, 4.2-K1, 4.2-K2, 4.3-K1, 4.3-K2, 4.4-K1, 4.4-K2, 4.4-S3, 4.4-S5 | 1.5-K1, 1.5-K3, 1.5-S1, 1.5-S2, 2.5-S5, 2.6-K1, 2.6-K2, 2.6-K4, 2.6-K5, 2.6-S1, 2.6-S2, 2.6-S3, 2.6-S4, 3.3-S4, 3.5-K1, 3.5-K2, 3.5-K3, 3.5-K4, 3.5-S1, 3.5-S2, 3.5-S3, 3.5-S4, 3.5-S5 |
| `08-management/developer-tools-and-cicd.md` | AWS CodePipeline. AWS CodeBuild. AWS CodeDeploy with deployment configurations for EC2, Lambda and ECS, blue/green, canary and linear. AWS CodeArtifact. Amazon CodeGuru. CodeCommit status. AWS Proton status. Deployment strategies all-at-once, rolling, blue/green, canary and immutable, compared across Elastic Beanstalk, ECS, Lambda and EC2 | M | None | 2.1-K2, 2.1-S1, 2.1-S2, 3.1-K4, 3.1-S2 |
| `09-analytics/kinesis.md` | Amazon Kinesis Data Streams | M | 3.5-K2, 3.5-K7, 3.5-S2, 3.5-S6 | None |
| `09-analytics/msk.md` | Amazon MSK | S | None | None |
| `09-analytics/glue.md` | AWS Glue | M | 3.5-K4, 3.5-S7 | None |
| `09-analytics/athena.md` | Amazon Athena | S | None | None |
| `09-analytics/lake-formation.md` | AWS Lake Formation | S | 1.3-K1, 3.5-S1 | None |
| `09-analytics/emr.md` | Amazon EMR | S | 3.5-S5 | None |
| `09-analytics/opensearch.md` | Amazon OpenSearch Service | S | None | None |
| `09-analytics/data-exchange-and-quick.md` | AWS Data Exchange. Amazon Quick, formerly Amazon QuickSight | XS group | 3.5-K1, 3.5-S4 | None |
| `10-migration/migration-hub-discovery-and-strategy.md` | AWS Migration Hub with tracking, Strategy Recommendations, Refactor Spaces and Orchestrator. AWS Application Discovery Service agent-based and agentless. The seven common migration strategies. Portfolio assessment, asset planning, wave planning, total cost of ownership. Migration Evaluator, noting it is out of scope for SAA | M | None | 4.1-K1, 4.1-K2, 4.1-K3, 4.1-K4, 4.1-S1, 4.1-S2, 4.1-S3 |
| `10-migration/dms-and-sct.md` | AWS DMS | S | 3.3-K6, 4.3-K7, 4.3-S5 | 4.2-K5, 4.2-S1 |
| `10-migration/application-migration-service.md` | AWS Application Migration Service | S | None | 4.2-K2, 4.2-S2 |
| `11-ml-and-media/ml-managed-services.md` | Amazon Comprehend, Lex, Polly, Rekognition, Textract, Transcribe, Translate, Kendra, Personalize, Fraud Detector, and Amazon SageMaker AI in two paragraphs covering build, train, deploy and endpoint types | M | 2.2-K2, 2.2-S8 | None |
| `11-ml-and-media/ai-dev-tools-and-generative-ai.md` | Amazon Q Developer, formerly CodeWhisperer. Amazon Q Business. Amazon Bedrock | S | None | E-S1, E-S2, E-S3 |
| `11-ml-and-media/media-iot-and-device-farm.md` | Amazon Elastic Transcoder, verify status. AWS Elemental MediaConvert, out of scope for SAA. Kinesis Video Streams pointer. AWS Device Farm. AWS IoT Core and the IoT family in one page, in scope for SAP and out of scope for SAA. Amazon Managed Blockchain in one paragraph | XS group | None | None |

Units showing `None` own no cross-cutting guide bullet. They remain in
the course because their named services are in scope and their unit plan
defines the service-specific material they must teach.

## Ownership notes

### Cross-cutting judgments

A few objectives describe architectural judgment rather than a single
service. SAA 2.1-S6 uses EC2 as the general-purpose baseline for the
compute, storage, networking and database selection comparison. SAA
2.1-S7 and 2.2-S8 use the managed ML comparison unit to teach how
purpose-built managed services replace custom implementations. SAP
3.3-S3 uses the Well-Architected review and improvement process to
identify opportunities for adopting new managed technology.

SAP 3.1-S5, engineering failure scenario activities, belongs to
`01-storage/backup-and-disaster-recovery.md` by explicit project design.
That unit connects game days and recovery testing to AWS Fault Injection
Service without treating that out-of-scope service as a full exam topic.

### Tier signals

The five busiest owners are `01-storage/backup-and-disaster-recovery.md` (40), `08-management/cost-management.md` (33), `04-networking/vpc.md` (25), `01-storage/s3.md` (24), `07-security/iam.md` (15). Bullet count is only a signal:
repeated cross-cutting objectives often share one compact explanation.
The disaster recovery reference is nevertheless raised to tier L because
it owns the core of two SAP continuity tasks in addition to Associate DR
and backup decisions. The cost reference remains tier L and should use
tight cross-links instead of repeating service-specific pricing details.

These 14 units own no guide bullet directly: `01-storage/fsx.md`, `01-storage/snow-family.md`, `02-compute/elastic-beanstalk.md`, `03-containers/eks.md`, `05-database/aurora.md`, `05-database/documentdb.md`, `05-database/neptune.md`, `05-database/redshift.md`, `06-integration/amazon-mq.md`, `06-integration/appflow-appsync-amplify-ses-pinpoint.md`, `09-analytics/msk.md`, `09-analytics/athena.md`, `09-analytics/opensearch.md`, `11-ml-and-media/media-iot-and-device-farm.md`.
Their services still appear on one or both in-scope lists. Writers should
treat them as selection-led units and make the scenario for choosing each
service explicit.

### Service homes

Every service on both in-scope lists has a home in `UNIT_PLAN.md`. AWS
Fargate is intentionally distributed across the ECS, EKS and Batch units.
Amazon Bedrock is absent from the formal in-scope list but appears in the
SAP emerging topics, so its surrounding architecture is covered in the AI
unit. AWS Fault Injection Service is named only to support the failure
scenario objective described above.
