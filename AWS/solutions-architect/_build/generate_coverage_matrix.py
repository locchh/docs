#!/usr/bin/env python3
"""Generate and validate the Solutions Architect exam coverage matrix.

The exam guides remain the source of the bullet wording. Ownership below is
explicit and keyed by exam, task, bullet kind, and position so edits to either
guide fail loudly instead of silently dropping coverage.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
BUILD = ROOT / "aws/solutions-architect/_build"
OUTPUT = ROOT / "aws/solutions-architect/services/README.md"


def unit(category: str, name: str) -> str:
    return f"{category}/{name}.md"


S3 = unit("01-storage", "s3")
EBS = unit("01-storage", "ebs")
EFS = unit("01-storage", "efs")
FSX = unit("01-storage", "fsx")
SGW = unit("01-storage", "storage-gateway")
BDR = unit("01-storage", "backup-and-disaster-recovery")
SNOW = unit("01-storage", "snow-family")
TRANSFER = unit("01-storage", "transfer-family-and-datasync")
EC2 = unit("02-compute", "ec2")
AMI = unit("02-compute", "ami")
ASG = unit("02-compute", "ec2-auto-scaling")
ELB = unit("02-compute", "elastic-load-balancing")
LAMBDA = unit("02-compute", "lambda")
BEANSTALK = unit("02-compute", "elastic-beanstalk")
BATCH = unit("02-compute", "batch")
OTHER_COMPUTE = unit("02-compute", "other-compute-and-end-user")
ECS = unit("03-containers", "ecs-and-ecr")
EKS = unit("03-containers", "eks")
VPC = unit("04-networking", "vpc")
HYBRID = unit("04-networking", "hybrid-connectivity")
ROUTE53 = unit("04-networking", "route53")
CLOUDFRONT = unit("04-networking", "cloudfront")
GLOBAL_ACCELERATOR = unit("04-networking", "global-accelerator")
API_GATEWAY = unit("04-networking", "api-gateway")
RDS = unit("05-database", "rds")
AURORA = unit("05-database", "aurora")
DYNAMODB = unit("05-database", "dynamodb")
CACHE = unit("05-database", "elasticache-and-memorydb")
DOCUMENTDB = unit("05-database", "documentdb")
NEPTUNE = unit("05-database", "neptune")
SPECIAL_DATABASES = unit("05-database", "keyspaces-qldb-and-timestream")
REDSHIFT = unit("05-database", "redshift")
SQS = unit("06-integration", "sqs")
SNS = unit("06-integration", "sns")
EVENTBRIDGE = unit("06-integration", "eventbridge")
STEP_FUNCTIONS = unit("06-integration", "step-functions")
MQ = unit("06-integration", "amazon-mq")
APP_INTEGRATION = unit("06-integration", "appflow-appsync-amplify-ses-pinpoint")
IAM = unit("07-security", "iam")
ORGANIZATIONS = unit("07-security", "organizations-identity-center-and-control-tower")
KMS = unit("07-security", "kms-and-cloudhsm")
ACM = unit("07-security", "acm")
SECRETS = unit("07-security", "secrets-manager-and-parameter-store")
COGNITO = unit("07-security", "cognito")
DIRECTORY = unit("07-security", "directory-service")
EDGE_SECURITY = unit("07-security", "waf-shield-firewall-manager-and-network-firewall")
DETECTION = unit("07-security", "detection-and-compliance-services")
API_CLI = unit("08-management", "aws-api-cli-and-sdks")
CLOUDFORMATION = unit("08-management", "cloudformation")
CLOUDWATCH = unit("08-management", "cloudwatch")
CLOUDTRAIL = unit("08-management", "cloudtrail")
SYSTEMS_MANAGER = unit("08-management", "systems-manager")
SERVICE_CATALOG = unit("08-management", "service-catalog")
GOVERNANCE_TOOLS = unit("08-management", "config-trusted-advisor-health-and-well-architected")
COST = unit("08-management", "cost-management")
DEV_TOOLS = unit("08-management", "developer-tools-and-cicd")
KINESIS = unit("09-analytics", "kinesis")
MSK = unit("09-analytics", "msk")
GLUE = unit("09-analytics", "glue")
ATHENA = unit("09-analytics", "athena")
LAKE_FORMATION = unit("09-analytics", "lake-formation")
EMR = unit("09-analytics", "emr")
OPENSEARCH = unit("09-analytics", "opensearch")
QUICK = unit("09-analytics", "data-exchange-and-quick")
MIGRATION = unit("10-migration", "migration-hub-discovery-and-strategy")
DMS = unit("10-migration", "dms-and-sct")
MGN = unit("10-migration", "application-migration-service")
ML = unit("11-ml-and-media", "ml-managed-services")
AI = unit("11-ml-and-media", "ai-dev-tools-and-generative-ai")
MEDIA = unit("11-ml-and-media", "media-iot-and-device-farm")


OWNERS: dict[str, str] = {}


def assign(exam: str, task: str, kind: str, owners: list[str]) -> None:
    for index, owner in enumerate(owners, 1):
        ref = f"{exam} {task}-{kind}{index}"
        if ref in OWNERS:
            raise ValueError(f"duplicate ownership assignment: {ref}")
        OWNERS[ref] = owner


# SAA-C03. Lists preserve the exact order of each Knowledge (K) or Skills (S)
# block in exam-guide-saa-c03.md.
assign("SAA", "1.1", "K", [ORGANIZATIONS, IAM, VPC, IAM, IAM])
assign("SAA", "1.1", "S", [IAM, IAM, IAM, ORGANIZATIONS, IAM, DIRECTORY])
assign("SAA", "1.2", "K", [SECRETS, VPC, VPC, COGNITO, DETECTION, EDGE_SECURITY])
assign("SAA", "1.2", "S", [VPC, VPC, EDGE_SECURITY, HYBRID])
assign("SAA", "1.3", "K", [LAKE_FORMATION, BDR, DETECTION, KMS])
assign("SAA", "1.3", "S", [DETECTION, KMS, ACM, KMS, BDR, S3, KMS])
assign("SAA", "2.1", "K", [API_GATEWAY, SQS, CACHE, ECS, EVENTBRIDGE, ASG,
                              CLOUDFRONT, ECS, ELB, VPC, SNS, LAMBDA, S3, ECS,
                              RDS, STEP_FUNCTIONS])
assign("SAA", "2.1", "S", [EVENTBRIDGE, ASG, SQS, ECS, LAMBDA, EC2, DYNAMODB])
assign("SAA", "2.2", "K", [ROUTE53, ML, VPC, BDR, EVENTBRIDGE, ROUTE53, AMI,
                              ELB, RDS, API_CLI, S3, CLOUDWATCH])
assign("SAA", "2.2", "S", [CLOUDFORMATION, BDR, CLOUDWATCH, ELB, BDR, BDR,
                              ELB, ML])
assign("SAA", "3.1", "K", [SGW, S3, S3])
assign("SAA", "3.1", "S", [S3, S3])
assign("SAA", "3.2", "K", [BATCH, OTHER_COMPUTE, SNS, ASG, LAMBDA, ECS])
assign("SAA", "3.2", "S", [SQS, ASG, EC2, LAMBDA])
assign("SAA", "3.3", "K", [RDS, CACHE, DYNAMODB, RDS, RDS, DMS, RDS, DYNAMODB])
assign("SAA", "3.3", "S", [RDS, RDS, RDS, DYNAMODB, CACHE])
assign("SAA", "3.4", "K", [CLOUDFRONT, VPC, ELB, HYBRID])
assign("SAA", "3.4", "S", [HYBRID, VPC, VPC, ELB])
assign("SAA", "3.5", "K", [QUICK, KINESIS, TRANSFER, GLUE, IAM, TRANSFER, KINESIS])
assign("SAA", "3.5", "S", [LAKE_FORMATION, KINESIS, TRANSFER, QUICK, EMR,
                              KINESIS, GLUE])
assign("SAA", "4.1", "K", [S3, COST, COST, S3, BDR, EBS, S3, TRANSFER, S3,
                              S3, S3])
assign("SAA", "4.1", "S", [S3, EBS, TRANSFER, EFS, S3, BDR, TRANSFER, S3,
                              S3, S3])
assign("SAA", "4.2", "K", [COST, COST, VPC, EC2, OTHER_COMPUTE, OTHER_COMPUTE,
                              EC2, ECS, ASG])
assign("SAA", "4.2", "S", [ELB, ASG, EC2, BDR, EC2, EC2])
assign("SAA", "4.3", "K", [COST, COST, CACHE, BDR, DYNAMODB, RDS, DMS, RDS,
                              DYNAMODB])
assign("SAA", "4.3", "S", [BDR, RDS, DYNAMODB, SPECIAL_DATABASES, DMS])
assign("SAA", "4.4", "K", [COST, COST, ELB, VPC, HYBRID, HYBRID, ROUTE53])
assign("SAA", "4.4", "S", [VPC, HYBRID, COST, CLOUDFRONT, COST, API_GATEWAY,
                              HYBRID])

# SAP-C02 emerging topics and Domains 1 through 4.
assign("SAP", "E", "S", [AI, AI, AI])
assign("SAP", "1.1", "K", [VPC, HYBRID, HYBRID, VPC, VPC])
assign("SAP", "1.1", "S", [HYBRID, HYBRID, VPC, VPC, VPC])
assign("SAP", "1.2", "K", [IAM, VPC, KMS, DETECTION])
assign("SAP", "1.2", "S", [IAM, ORGANIZATIONS, KMS, CLOUDTRAIL])
assign("SAP", "1.3", "K", [BDR, BDR, BDR])
assign("SAP", "1.3", "S", [BDR, ASG, ASG, BDR])
assign("SAP", "1.4", "K", [ORGANIZATIONS, ORGANIZATIONS, ORGANIZATIONS])
assign("SAP", "1.4", "S", [ORGANIZATIONS, ORGANIZATIONS, ORGANIZATIONS])
assign("SAP", "1.5", "K", [COST, EC2, COST])
assign("SAP", "1.5", "S", [COST, COST, EC2])
assign("SAP", "2.1", "K", [CLOUDFORMATION, DEV_TOOLS, SYSTEMS_MANAGER, SYSTEMS_MANAGER])
assign("SAP", "2.1", "S", [DEV_TOOLS, DEV_TOOLS, SERVICE_CATALOG, SERVICE_CATALOG])
assign("SAP", "2.2", "K", [BDR, ROUTE53, BDR, BDR, BDR])
assign("SAP", "2.2", "S", [BDR, BDR, BDR, BDR, BDR, CLOUDWATCH])
assign("SAP", "2.3", "K", [IAM, VPC, KMS, VPC, SECRETS, EDGE_SECURITY])
assign("SAP", "2.3", "S", [IAM, VPC, EDGE_SECURITY, KMS, VPC, SYSTEMS_MANAGER])
assign("SAP", "2.4", "K", [BDR, S3, BDR, ASG, SQS, GOVERNANCE_TOOLS])
assign("SAP", "2.4", "S", [BDR, BDR, SQS, BDR, BDR, ROUTE53])
assign("SAP", "2.5", "K", [CLOUDWATCH, S3, EC2, DYNAMODB])
assign("SAP", "2.5", "S", [DYNAMODB, ASG, CACHE, DYNAMODB, COST])
assign("SAP", "2.6", "K", [COST, COST, S3, COST, COST])
assign("SAP", "2.6", "S", [COST, COST, COST, COST])
assign("SAP", "3.1", "K", [EVENTBRIDGE, BDR, CLOUDWATCH, DEV_TOOLS, SYSTEMS_MANAGER])
assign("SAP", "3.1", "S", [CLOUDWATCH, DEV_TOOLS, CLOUDFORMATION, SYSTEMS_MANAGER, BDR])
assign("SAP", "3.2", "K", [DETECTION, DETECTION, SECRETS, IAM, DETECTION,
                              SYSTEMS_MANAGER, BDR])
assign("SAP", "3.2", "S", [SECRETS, IAM, DETECTION, CLOUDTRAIL, DETECTION,
                              SYSTEMS_MANAGER, BDR, SYSTEMS_MANAGER])
assign("SAP", "3.3", "K", [EC2, GLOBAL_ACCELERATOR, CLOUDWATCH, CLOUDWATCH])
assign("SAP", "3.3", "S", [CLOUDWATCH, CLOUDWATCH, GOVERNANCE_TOOLS, COST, CLOUDWATCH])
assign("SAP", "3.4", "K", [VPC, BDR, ASG, BDR, BDR, GOVERNANCE_TOOLS])
assign("SAP", "3.4", "S", [ASG, BDR, ELB, BDR])
assign("SAP", "3.5", "K", [COST, COST, COST, COST])
assign("SAP", "3.5", "S", [COST, COST, COST, COST, COST])
assign("SAP", "4.1", "K", [MIGRATION, MIGRATION, MIGRATION, MIGRATION])
assign("SAP", "4.1", "S", [MIGRATION, MIGRATION, MIGRATION])
assign("SAP", "4.2", "K", [TRANSFER, MGN, HYBRID, DIRECTORY, DMS, ORGANIZATIONS])
assign("SAP", "4.2", "S", [DMS, MGN, TRANSFER, IAM, ORGANIZATIONS])
assign("SAP", "4.3", "K", [EC2, ECS, S3, DYNAMODB])
assign("SAP", "4.3", "S", [EC2, ECS, S3, DYNAMODB])
assign("SAP", "4.4", "K", [LAMBDA, ECS, S3, DYNAMODB, SQS])
assign("SAP", "4.4", "S", [SQS, LAMBDA, ECS, DYNAMODB, EVENTBRIDGE])


def extract_bullets(path: Path, exam: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_domains = False
    emerging = False
    task = ""
    kind = ""
    counters = {"K": 0, "S": 0}

    for raw in path.read_text(encoding="utf-8").splitlines():
        if exam == "SAP" and raw == "## Emerging topics":
            emerging = True
            counters = {"K": 0, "S": 0}
            continue
        if raw.startswith("## Domain 1:"):
            emerging = False
            in_domains = True
        if raw == "## In-scope services":
            in_domains = False
        if raw.startswith("### Task "):
            task = raw.split()[2].rstrip(":")
            kind = ""
            counters = {"K": 0, "S": 0}
            continue
        if raw == "Knowledge of:":
            kind = "K"
            continue
        if raw == "Skills in:":
            kind = "S"
            continue
        if raw.startswith("- ") and emerging:
            counters["S"] += 1
            ref = f"{exam} E-S{counters['S']}"
            rows.append({"exam": exam, "task": "Emerging", "ref": ref,
                         "bullet": raw[2:]})
        elif raw.startswith("- ") and in_domains and kind:
            counters[kind] += 1
            ref = f"{exam} {task}-{kind}{counters[kind]}"
            rows.append({"exam": exam, "task": task, "ref": ref,
                         "bullet": raw[2:]})
    return rows


def extract_units() -> tuple[list[str], dict[str, str], dict[str, str]]:
    units: list[str] = []
    focus: dict[str, str] = {}
    tiers: dict[str, str] = {}
    category = ""
    for line in (BUILD / "UNIT_PLAN.md").read_text(encoding="utf-8").splitlines():
        heading = re.fullmatch(r"## (\d\d-[a-z-]+)", line)
        if heading:
            category = heading.group(1)
            continue
        if line.startswith("## ") and not heading:
            category = ""
        if not category or not line.startswith("| `"):
            continue
        fields = [field.strip() for field in line.strip("|").split("|")]
        filename = fields[0].strip("`")
        path = f"{category}/{filename}"
        units.append(path)
        summary = fields[1]
        focus[path] = summary.split(":", 1)[0].rstrip(".")
        tiers[path] = fields[2]
    return units, focus, tiers


NAMED_SUPPORTS = [
    ("Amazon S3", S3), ("S3 ", S3), ("Amazon EBS", EBS), ("Amazon EFS", EFS),
    ("Amazon FSx", FSX), ("Storage Gateway", SGW), ("AWS Backup", BDR),
    ("Elastic Disaster Recovery", BDR), ("AWS DataSync", TRANSFER),
    ("AWS Transfer Family", TRANSFER), ("Snow Family", SNOW),
    ("Amazon EC2 Auto Scaling", ASG), ("AWS Auto Scaling", ASG),
    ("Amazon EC2", EC2), ("EC2 instance", EC2), ("AWS Lambda", LAMBDA),
    ("AWS Batch", BATCH), ("Elastic Beanstalk", BEANSTALK), ("AWS Fargate", ECS),
    ("Fargate", ECS), ("Amazon ECS", ECS), ("Amazon EKS", EKS),
    ("Amazon VPC", VPC), ("AWS PrivateLink", VPC), ("VPC endpoint", VPC),
    ("NAT gateway", VPC), ("security group", VPC), ("network ACL", VPC),
    ("AWS Direct Connect", HYBRID), ("AWS VPN", HYBRID), ("Site-to-Site VPN", HYBRID),
    ("Transit Gateway", HYBRID), ("Amazon Route 53", ROUTE53),
    ("Amazon CloudFront", CLOUDFRONT), ("AWS Global Accelerator", GLOBAL_ACCELERATOR),
    ("Amazon API Gateway", API_GATEWAY), ("Application Load Balancer", ELB),
    ("Network Load Balancer", ELB), ("Gateway Load Balancer", ELB),
    ("Amazon RDS", RDS), ("RDS Proxy", RDS), ("Amazon Aurora", AURORA),
    ("Aurora Serverless", AURORA), ("Amazon DynamoDB", DYNAMODB),
    ("DynamoDB", DYNAMODB), ("Amazon ElastiCache", CACHE), ("ElastiCache", CACHE),
    ("Amazon OpenSearch Service", OPENSEARCH), ("Amazon Redshift", REDSHIFT),
    ("Amazon SQS", SQS), ("Amazon SNS", SNS), ("Amazon EventBridge", EVENTBRIDGE),
    ("AWS Step Functions", STEP_FUNCTIONS), ("AWS Secrets Manager", SECRETS),
    ("IAM Identity Center", ORGANIZATIONS), ("AWS Control Tower", ORGANIZATIONS),
    ("AWS Organizations", ORGANIZATIONS), ("AWS STS", IAM), ("IAM", IAM),
    ("AWS KMS", KMS), ("AWS Certificate Manager", ACM), ("Amazon Cognito", COGNITO),
    ("Directory Service", DIRECTORY), ("AWS Shield", EDGE_SECURITY),
    ("AWS WAF", EDGE_SECURITY), ("Amazon GuardDuty", DETECTION),
    ("Amazon Macie", DETECTION), ("AWS Security Hub", DETECTION),
    ("Amazon Inspector", DETECTION), ("AWS CloudFormation", CLOUDFORMATION),
    ("Amazon CloudWatch", CLOUDWATCH), ("CloudWatch", CLOUDWATCH),
    ("AWS CloudTrail", CLOUDTRAIL), ("AWS Systems Manager", SYSTEMS_MANAGER),
    ("Systems Manager", SYSTEMS_MANAGER), ("Service Quotas", API_CLI),
    ("AWS Trusted Advisor", GOVERNANCE_TOOLS), ("AWS Pricing Calculator", COST),
    ("AWS Cost Explorer", COST), ("AWS Budgets", COST),
    ("AWS Cost and Usage Report", COST), ("Savings Plans", COST),
    ("AWS Compute Optimizer", COST), ("S3 Storage Lens", COST),
    ("Amazon Kinesis", KINESIS), ("AWS Glue", GLUE), ("Amazon Athena", ATHENA),
    ("AWS Lake Formation", LAKE_FORMATION), ("Amazon EMR", EMR),
    ("Amazon Quick", QUICK), ("AWS Migration Hub", MIGRATION),
    ("Application Discovery Service", MIGRATION), ("Application Migration Service", MGN),
    ("AWS DMS", DMS), ("AWS SCT", DMS), ("Amazon Bedrock", AI),
    ("AgentCore Identity", AI), ("Amazon Comprehend", ML), ("Amazon Polly", ML),
]


MANUAL_SUPPORTS: dict[str, list[str]] = {
    "SAA 1.1-K3": [ROUTE53],
    "SAA 1.3-K1": [IAM, S3],
    "SAA 1.3-K2": [S3, RDS],
    "SAA 1.3-K3": [S3],
    "SAA 1.3-S7": [ACM],
    "SAA 2.1-K3": [CLOUDFRONT, API_GATEWAY],
    "SAA 2.1-K4": [LAMBDA, SQS],
    "SAA 2.1-K5": [SQS, LAMBDA],
    "SAA 2.1-K6": [EC2, LAMBDA],
    "SAA 2.1-K10": [ELB, RDS],
    "SAA 2.1-S1": [API_GATEWAY, LAMBDA],
    "SAA 2.1-S2": [LAMBDA, ECS],
    "SAA 2.1-S3": [SNS, EVENTBRIDGE],
    "SAA 2.1-S6": [VPC, S3, RDS],
    "SAA 2.1-S7": [ML, DYNAMODB],
    "SAA 2.2-K5": [SQS, DYNAMODB],
    "SAA 2.2-K6": [BDR, ELB],
    "SAA 2.2-K10": [GOVERNANCE_TOOLS],
    "SAA 2.2-S2": [ROUTE53, ELB],
    "SAA 2.2-S4": [ASG, ROUTE53],
    "SAA 2.2-S7": [ASG, BDR, MGN],
    "SAA 2.2-S8": [ML, DYNAMODB],
    "SAA 3.1-S1": [EBS, EFS, FSX],
    "SAA 3.1-S2": [EFS, FSX],
    "SAA 3.2-K2": [EC2, CLOUDFRONT, GLOBAL_ACCELERATOR],
    "SAA 3.3-K1": [AURORA, DYNAMODB],
    "SAA 3.3-S2": [AURORA, DYNAMODB],
    "SAA 3.4-S2": [HYBRID, ELB],
    "SAA 3.4-S3": [CLOUDFRONT, HYBRID],
    "SAA 3.5-K2": [GLUE, KINESIS],
    "SAA 3.5-K5": [VPC, KMS],
    "SAA 3.5-K6": [SNOW, KINESIS],
    "SAA 3.5-S6": [GLUE, TRANSFER],
    "SAA 3.5-S2": [MSK],
    "SAA 4.1-K9": [EBS, EFS],
    "SAA 4.1-K11": [EBS, EFS],
    "SAA 4.1-S2": [S3, EFS],
    "SAA 4.1-S10": [EBS, EFS, FSX],
    "SAA 4.2-K3": [COST],
    "SAA 4.2-K8": [LAMBDA, EC2],
    "SAA 4.2-S3": [ECS, LAMBDA],
    "SAA 4.2-S4": [COST, ASG],
    "SAA 4.3-K3": [DYNAMODB],
    "SAA 4.3-K4": [RDS, S3],
    "SAA 4.3-K9": [RDS, AURORA],
    "SAA 4.3-S3": [RDS, AURORA],
    "SAA 4.3-S4": [REDSHIFT, DYNAMODB],
    "SAA 4.4-S3": [VPC, GLOBAL_ACCELERATOR],
    "SAA 4.4-S5": [VPC, HYBRID],
    "SAP 1.1-K1": [ROUTE53],
    "SAP 1.1-K2": [ECS, EKS],
    "SAP 1.1-K5": [CLOUDWATCH],
    "SAP 1.1-S3": [ROUTE53],
    "SAP 1.1-S4": [CLOUDWATCH],
    "SAP 1.2-S4": [DETECTION, ORGANIZATIONS],
    "SAP 1.3-S2": [ROUTE53, ELB],
    "SAP 1.3-S3": [EC2, COST],
    "SAP 2.1-K2": [ECS, BEANSTALK],
    "SAP 2.1-S2": [BEANSTALK, ECS, LAMBDA],
    "SAP 2.1-S3": [SYSTEMS_MANAGER, BEANSTALK, ECS],
    "SAP 2.1-S4": [CLOUDFORMATION],
    "SAP 2.2-S2": [S3, RDS, DYNAMODB],
    "SAP 2.2-S5": [ROUTE53, ASG],
    "SAP 2.4-K1": [ROUTE53],
    "SAP 2.4-K2": [RDS, CACHE],
    "SAP 2.4-K3": [ROUTE53, AURORA],
    "SAP 2.4-S1": [ELB, ASG],
    "SAP 2.4-S2": [BDR, ROUTE53],
    "SAP 2.4-S4": [RDS, AURORA],
    "SAP 2.4-S5": [S3, RDS],
    "SAP 2.4-K6": [API_CLI],
    "SAP 2.5-S2": [EC2, LAMBDA],
    "SAP 2.5-S3": [SQS, RDS],
    "SAP 2.5-K4": [REDSHIFT, OPENSEARCH],
    "SAP 2.5-S1": [KINESIS, REDSHIFT, API_GATEWAY],
    "SAP 2.5-S4": [ML, ATHENA, EMR],
    "SAP 2.6-K5": [LAMBDA, RDS, SERVICE_CATALOG],
    "SAP 2.6-S1": [EC2, ASG],
    "SAP 3.1-K1": [SYSTEMS_MANAGER, CLOUDWATCH],
    "SAP 3.1-S3": [SYSTEMS_MANAGER, EVENTBRIDGE],
    "SAP 3.2-K1": [S3, BDR],
    "SAP 3.2-K5": [EDGE_SECURITY, IAM],
    "SAP 3.2-S3": [IAM, VPC],
    "SAP 3.2-S5": [SYSTEMS_MANAGER],
    "SAP 3.2-S8": [DETECTION],
    "SAP 3.3-K1": [ASG],
    "SAP 3.3-K2": [CLOUDFRONT],
    "SAP 3.3-S2": [EC2, ASG],
    "SAP 3.3-S3": [SERVICE_CATALOG, ML, LAMBDA],
    "SAP 3.3-S5": [EC2, RDS],
    "SAP 3.4-K1": [ROUTE53],
    "SAP 3.4-K2": [S3, RDS],
    "SAP 3.4-K3": [ELB],
    "SAP 3.4-K4": [ELB, ROUTE53],
    "SAP 3.4-S2": [CLOUDWATCH],
    "SAP 3.4-S4": [ASG, S3],
    "SAP 3.4-K6": [API_CLI],
    "SAP 4.2-S4": [KMS, VPC],
    "SAP 4.3-K4": [RDS, OPENSEARCH],
    "SAP 4.3-S1": [BEANSTALK, LAMBDA],
    "SAP 4.3-S3": [EBS, EFS, FSX],
    "SAP 4.3-S4": [RDS, OPENSEARCH],
    "SAP 4.4-S1": [SNS, EVENTBRIDGE],
    "SAP 4.4-S2": [ECS],
    "SAP 4.4-S4": [AURORA, CACHE],
    "SAP 4.4-S5": [SQS, SNS, STEP_FUNCTIONS],
    "SAP 3.5-K1": [EC2, ASG],
    "SAP 3.5-S1": [EC2, ASG],
    "SAP 3.5-S2": [EC2, ASG, GOVERNANCE_TOOLS],
}


def supports_for(row: dict[str, str], owner: str) -> list[str]:
    supports = [candidate for candidate in MANUAL_SUPPORTS.get(row["ref"], [])
                if candidate != owner]
    for phrase, candidate in NAMED_SUPPORTS:
        if phrase in row["bullet"] and candidate != owner and candidate not in supports:
            supports.append(candidate)
    return supports


def escape(text: str) -> str:
    return text.replace("|", "\\|")


def main() -> None:
    units, focus, tiers = extract_units()
    if len(units) != 70 or len(set(units)) != 70:
        raise ValueError(f"expected 70 unique units from UNIT_PLAN.md, got {len(units)}")

    rows = extract_bullets(BUILD / "exam-guide-saa-c03.md", "SAA")
    rows += extract_bullets(BUILD / "exam-guide-sap-c02.md", "SAP")
    refs = {row["ref"] for row in rows}
    if len(rows) != 379 or len(refs) != 379:
        raise ValueError(f"expected 379 unique guide bullets, got {len(rows)}")
    missing = refs - OWNERS.keys()
    extra = OWNERS.keys() - refs
    if missing or extra:
        raise ValueError(f"ownership mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
    unknown = set(OWNERS.values()) - set(units)
    if unknown:
        raise ValueError(f"unknown owner units: {sorted(unknown)}")

    by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    detailed: list[str] = []
    for row in rows:
        owner = OWNERS[row["ref"]]
        support = supports_for(row, owner)
        unknown_support = set(support) - set(units)
        if unknown_support:
            raise ValueError(f"unknown supporting units for {row['ref']}: {unknown_support}")
        row["owner"] = owner
        row["supports"] = ", ".join(f"`{path}`" for path in support)
        by_unit[owner].append(row)
        detailed.append(
            f"| {row['exam']}-C0{3 if row['exam'] == 'SAA' else 2} | "
            f"{row['task']} | {escape(row['bullet'])} | `{owner}` | {row['supports']} |"
        )

    unowned_units = [path for path in units if path not in by_unit]
    # Some narrow units own no cross-cutting guide bullet but still teach named
    # in-scope services. Keeping them in the unit index makes that visible.

    index: list[str] = []
    for path in units:
        owned = by_unit[path]
        saa = [row["ref"].removeprefix("SAA ") for row in owned if row["exam"] == "SAA"]
        sap = [row["ref"].removeprefix("SAP ") for row in owned if row["exam"] == "SAP"]
        index.append(
            f"| `{path}` | {escape(focus[path])} | {tiers[path]} | "
            f"{', '.join(saa) or 'None'} | {', '.join(sap) or 'None'} |"
        )

    counts = sorted(((len(by_unit[path]), path) for path in units), reverse=True)
    busiest = ", ".join(f"`{path}` ({count})" for count, path in counts[:5])
    zero_owners = ", ".join(f"`{path}`" for path in unowned_units)

    text = "\n".join([
        "# Service coverage matrix",
        "",
        "This is the ownership map for every Knowledge and Skills bullet in the",
        "SAA-C03 and SAP-C02 exam guides captured in `_build/`. Each bullet has",
        "exactly one owning service unit. An owning unit must teach the bullet",
        "well enough to answer an exam question; supporting units may reinforce it",
        "without duplicating the primary explanation.",
        "",
        "Bullet references in the unit index use `K` for Knowledge and `S` for",
        "Skills, numbered in source-guide order. `E` identifies SAP-C02's three",
        "emerging-topic skills. The detailed table preserves the source wording.",
        "",
        f"**Coverage:** {len(rows)} of {len(rows)} bullets assigned: 189 SAA-C03,",
        "187 SAP-C02 task bullets and 3 SAP-C02 emerging-topic bullets.",
        "",
        "## Bullet-by-bullet ownership",
        "",
        "| Exam | Task | Bullet | Owner | Also covered in |",
        "|---|---|---|---|---|",
        *detailed,
        "",
        "## Unit ownership index",
        "",
        "This reverse index is the writer-dispatch view. Its references use the",
        "same task, kind and source-order numbering defined above.",
        "",
        "| Unit | Service focus | Tier | Owned SAA-C03 bullets | Owned SAP-C02 bullets |",
        "|---|---|---|---|---|",
        *index,
        "",
        "Units showing `None` own no cross-cutting guide bullet. They remain in",
        "the course because their named services are in scope and their unit plan",
        "defines the service-specific material they must teach.",
        "",
        "## Ownership notes",
        "",
        "### Cross-cutting judgments",
        "",
        "A few objectives describe architectural judgment rather than a single",
        "service. SAA 2.1-S6 uses EC2 as the general-purpose baseline for the",
        "compute, storage, networking and database selection comparison. SAA",
        "2.1-S7 and 2.2-S8 use the managed ML comparison unit to teach how",
        "purpose-built managed services replace custom implementations. SAP",
        "3.3-S3 uses the Well-Architected review and improvement process to",
        "identify opportunities for adopting new managed technology.",
        "",
        "SAP 3.1-S5, engineering failure scenario activities, belongs to",
        "`01-storage/backup-and-disaster-recovery.md` by explicit project design.",
        "That unit connects game days and recovery testing to AWS Fault Injection",
        "Service without treating that out-of-scope service as a full exam topic.",
        "",
        "### Tier signals",
        "",
        f"The five busiest owners are {busiest}. Bullet count is only a signal:",
        "repeated cross-cutting objectives often share one compact explanation.",
        "The disaster recovery reference is nevertheless raised to tier L because",
        "it owns the core of two SAP continuity tasks in addition to Associate DR",
        "and backup decisions. The cost reference remains tier L and should use",
        "tight cross-links instead of repeating service-specific pricing details.",
        "",
        f"These {len(unowned_units)} units own no guide bullet directly: {zero_owners}.",
        "Their services still appear on one or both in-scope lists. Writers should",
        "treat them as selection-led units and make the scenario for choosing each",
        "service explicit.",
        "",
        "### Service homes",
        "",
        "Every service on both in-scope lists has a home in `UNIT_PLAN.md`. AWS",
        "Fargate is intentionally distributed across the ECS, EKS and Batch units.",
        "Amazon Bedrock is absent from the formal in-scope list but appears in the",
        "SAP emerging topics, so its surrounding architecture is covered in the AI",
        "unit. AWS Fault Injection Service is named only to support the failure",
        "scenario objective described above.",
        "",
    ])
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"units: {len(units)}; bullets: {len(rows)}; units without owned bullets: {len(unowned_units)}")
    if unowned_units:
        print("no direct ownership: " + ", ".join(unowned_units))


if __name__ == "__main__":
    main()
