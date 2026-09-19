# AWS detection and compliance services

**Where it sits on the exams.** These services answer four questions: what threat is happening, what configuration violates policy, who can reach what, and what evidence proves control operation. **Amazon GuardDuty** detects threats from AWS activity and telemetry, **Amazon Inspector** finds software vulnerabilities and unintended network exposure, **Amazon Macie** discovers sensitive data in **Amazon Simple Storage Service (Amazon S3)**, the durable object storage service, **Amazon Detective** investigates related activity, **AWS Security Hub Cloud Security Posture Management (Security Hub CSPM)**, formerly named AWS Security Hub, aggregates findings and evaluates standards, the separate and newer **AWS Security Hub** correlates those signals into prioritized risk, **IAM Access Analyzer** reports unintended and unused access, and **AWS Config** records resource configuration and evaluates it against rules. **AWS Audit Manager**, the customer-control evidence service, and **AWS Artifact**, the AWS report and agreement portal, supply different forms of compliance evidence. The group serves SAA-C03 tasks 1.2 and 1.3 and SAP-C02 tasks 1.2 and 3.2. Rule of thumb: GuardDuty detects behavior, Inspector scans workloads, Macie classifies S3 data, Access Analyzer reasons about permissions, Config evaluates configuration, Security Hub CSPM scores posture, and Detective explains a finding.

## Select the service by the object being examined

The exam usually names an object or outcome that selects the service before any feature detail matters. Read the table from the evidence in the scenario, not from the word "security".

| Scenario evidence | Service | Output |
|---|---|---|
| Suspicious API calls, malicious addresses, unusual DNS, compromised credentials | GuardDuty | Threat finding |
| Known vulnerability in an EC2 package, ECR image or Lambda function | Inspector | Vulnerability finding with severity and remediation context |
| Personally identifiable information or credentials inside S3 objects | Macie | Sensitive data finding and classification result |
| Root cause and related entities behind a finding | Detective | Behavior graph, finding group and investigation |
| Resource shared with an external principal, or a role, key or permission unused for a tracking period | IAM Access Analyzer | External access, internal access or unused access finding |
| Findings from many products or failed security-standard controls | Security Hub CSPM | Normalized findings, controls, scores and workflow state |
| One prioritized risk correlated from several products, with an attack path | Security Hub | Exposure finding, coverage finding and unused access finding |
| Resource changed or violates a desired configuration | Config | Configuration item, history and compliance evaluation |
| Customer control evidence organized for an audit | Audit Manager for existing customers | Assessment evidence and audit report |
| AWS infrastructure certification or agreement | AWS Artifact | Downloadable AWS report or agreement |

Detection is not prevention. A GuardDuty finding does not block an address, a Config `NON_COMPLIANT` result changes nothing unless remediation was configured, and an automation rule updates finding fields in Security Hub CSPM, or those plus a Jira Cloud or ServiceNow ITSM ticket in the new Security Hub, rather than executing a repair. Use **Amazon EventBridge**, the managed event bus, to route findings to a response target, or Config remediation through **AWS Systems Manager Automation**, the managed runbook workflow. Compliance is not a service verdict either: Config can show that encryption is enabled without proving that every Payment Card Industry Data Security Standard obligation is met.

## GuardDuty, Inspector and Macie

GuardDuty continuously analyzes supported AWS data sources with threat intelligence, anomaly detection and machine learning. Foundational detection uses management activity, **Amazon Virtual Private Cloud (Amazon VPC)** network activity and DNS activity without the customer delivering copies of **AWS CloudTrail**, the AWS API activity audit service, VPC Flow Logs or DNS logs to the service. Protection plans are the optional add-ons that extend those sources and the resource types covered. As of September 2026 they are S3 Protection for S3 data events; RDS Protection for login activity on supported **Amazon Relational Database Service (Amazon RDS)** databases; Lambda Protection for network activity of **AWS Lambda**, the serverless function service; EKS Protection, which analyzes audit logs from **Amazon Elastic Kubernetes Service (Amazon EKS)**, the managed Kubernetes service, through GuardDuty's own log stream; AI Protection, which reads CloudTrail data events from **Amazon Bedrock**, the managed foundation model service, and **Amazon SageMaker AI**, the machine learning platform, for anomalous model invocation, cost harvesting and prompt injection; Runtime Monitoring for operating-system behavior on supported EC2, **Amazon Elastic Container Service (Amazon ECS)**, the managed container orchestration service, and EKS workloads; Malware Protection for EC2; Malware Protection for S3; and Malware Protection for **AWS Backup**, the managed backup service, which scans protected EBS snapshots, AMIs and S3 recovery points before a restore puts malware back. EKS audit log monitoring is a capability inside EKS Protection, not a plan of its own.

Extended Threat Detection is not a protection plan and needs no configuration. It is enabled automatically with GuardDuty in every Region at no extra charge and correlates signals across the foundational sources plus whatever plans are active into a single attack sequence finding, always rated Critical, covering credential misuse, S3 data compromise, and container or Kubernetes compromise. It works over a rolling 24-hour window and ignores archived findings, so a broad suppression rule can hide the weak signal a sequence depends on. A stem describing one finding that narrates a multi-step attack rather than an isolated event is Extended Threat Detection.

A GuardDuty finding is a lead to triage, not proof, so suppress a known acceptable pattern only after confirming its scope, and use trusted IP and threat lists for organization-specific context. Malware Protection for EC2 starts an agentless scan of attached **Amazon Elastic Block Store (Amazon EBS)** volumes, the persistent block storage for EC2, after a qualifying finding.

Inspector continuously evaluates activated resource types and produces three finding classes: package vulnerability, code vulnerability and network reachability. For **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service, it correlates installed software with vulnerability intelligence, using Systems Manager inventory for agent-based scanning or inspecting eligible volumes agentlessly. For **Amazon Elastic Container Registry (Amazon ECR)**, the managed container registry, enhanced scanning rescans stored images as vulnerability intelligence changes. For Lambda, standard scanning examines package dependencies and optional code scanning looks for code vulnerabilities.

Network reachability is the seam worth memorizing. Those findings are generated for EC2 instances only, every 12 hours, by evaluating the whole path from a VPC edge inward: internet gateways, virtual private gateways, peering connections, load balancers, route tables, network access control lists, security groups and subnets. That is why "EC2 instances unintentionally reachable from the internet" selects Inspector, not GuardDuty. Inspector reasons about the configured path whether or not anyone used it; GuardDuty reports that someone did something suspicious over one.

Inspector findings carry the affected package or code, severity, fix availability and exposure context. An image passing at build time is not permanently safe, because a new common vulnerabilities and exposures (CVE) record can appear later, so prioritize exploitable internet-reachable resources and rebuild images rather than editing running containers. Inspector Classic is never the answer: the current service replaced it.

Macie is specific to S3 general purpose buckets. Enabling it maintains a bucket inventory and evaluates access posture, producing policy findings for conditions such as public exposure. Sensitive data discovery reads object content with managed data identifiers, machine learning and pattern matching; custom data identifiers add a regular expression plus optional proximity terms, and allow lists exclude known acceptable values. Automated discovery samples representative objects across the estate for broad visibility, while a discovery job is targeted, with chosen buckets, scope, sampling depth and one-time or scheduled execution. Use automated discovery to find where risk concentrates, then a job when an audit requires deliberate coverage of named data. Macie neither encrypts the object nor changes bucket access.

Two services read the bytes of an S3 object, and they answer different questions. Macie asks whether the data is sensitive: does the object hold personal, financial or credential material that changes how it must be handled. GuardDuty Malware Protection for S3 asks whether the object is malicious, scanning newly uploaded objects and optionally applying a result tag an application reads before processing. A stem about regulated content or classification selects Macie; a stem about quarantining an upload that others will download selects Malware Protection for S3.

Cost follows work performed: GuardDuty charges by analyzed data sources and enabled protection plans, Inspector by scanned resources and scanning modes, and Macie by bucket evaluation, automated object monitoring and bytes inspected. Scope expensive classification to likely data locations.

## Amazon Detective

Detective is the investigation service and its unit of work is the behavior graph. Enabling it starts an independent, duplicative ingest of CloudTrail management events and VPC flow logs, plus GuardDuty findings for enrolled accounts, and links principals, IP addresses, EC2 instances and other entities into one graph spanning the administrator account and its members. Because that ingest is its own, Detective neither depends on nor changes existing trails or flow log configuration and adds no cost to them. Two optional source packages extend the graph: EKS audit logs, and AWS security findings from Security Hub CSPM.

The number the exam cares about is the history window. Detective retains data from each source package for up to a year and shows how the type and volume of activity changed over a selected range inside it, which is why "reconstruct what this role did over the past several months" points to Detective and not to a findings console.

Finding groups collect related findings, entities and unusual behaviors into one candidate incident with an interactive visualization, the fastest route from a high-severity GuardDuty finding to the shape of the whole event. Detective Investigation runs the other direction: pointed at an **AWS Identity and Access Management (IAM)**, the AWS authorization service, user or role, it tests that principal against indicators of compromise. Integration with **Amazon Security Lake**, which centralizes security logs into a customer-owned S3 data lake in Open Cybersecurity Schema Framework (OCSF) format, lets an analyst pivot from a graph entity to the raw log records behind it. Detective explains a finding; it never produces one.

## Security Hub, Security Hub CSPM and IAM Access Analyzer

AWS now ships two live products from one user guide, and the names are the trap. AWS Security Hub CSPM is the service that was called AWS Security Hub until the rename, and it is still the posture, standards and finding-aggregation layer. The bare name AWS Security Hub now denotes a newer service, generally available since December 2, 2025, that correlates signals from Security Hub CSPM, Inspector, GuardDuty and Macie into prioritized risk. The SAP-C02 exam guide still lists "AWS Security Hub" in task 1.2 with the older meaning, so on the exams read an unqualified "Security Hub" in a stem about standards, controls, scores or ASFF aggregation as Security Hub CSPM, and reserve the new service for stems about correlated exposures, attack paths or unused access. The two are complementary: AWS recommends enabling both, CSPM findings flow into Security Hub automatically, and Security Hub without CSPM loses its posture signal.

What the new Security Hub adds is correlation. An exposure finding is one prioritized risk assembled from several signals at once, such as an Inspector package vulnerability on an instance that a control check shows is internet reachable and whose attached role is over-permissioned, and it carries an attack path graph showing how an attacker could move to downstream resources. Its findings use OCSF rather than ASFF, the schema difference to remember. It also produces unused access findings, and the mechanism matters: enabling Security Hub creates a service-linked IAM Access Analyzer analyzer that evaluates every IAM role and user against CloudTrail activity over a fixed, non-configurable 90-day lookback, re-evaluates active findings every 24 hours, and resolves one automatically when the principal becomes active again. It reports unused roles, access keys, console passwords and permissions, and for unused permissions it proposes a scoped-down replacement policy. The analyzer runs in US East (N. Virginia) because IAM is global, its findings replicate to every enabled Region, and it costs nothing extra.

IAM Access Analyzer is also a service in its own right, named directly in SAP-C02 task 1.2, and its customer-managed analyzers are separate from that service-linked one. An external access analyzer applies logic-based reasoning to resource policies to report resources shared outside a chosen zone of trust, either one account or the whole organization, across supported types including S3 buckets, IAM roles, KMS keys, Lambda functions, SQS queues, Secrets Manager secrets, SNS topics, snapshots and DynamoDB tables. An internal access analyzer reports who inside that zone can reach selected business-critical resources. A customer-managed unused access analyzer is the third type, and unlike the fixed 90 days of the service-linked one its tracking period is configurable between 1 and 365 days, which is the setting a scenario naming any window other than 90 days is pointing at. Access Analyzer also validates policies against grammar and best practice, runs custom policy checks against a named security standard inside a deployment pipeline, and generates a policy from observed CloudTrail activity. The scope rule that bites: external access findings cover only the Region where that analyzer was created, so an organization needs one per Region, while unused access findings do not vary by Region.

Security Hub CSPM is the posture and finding aggregation layer. Integrations send findings in the AWS Security Finding Format (ASFF), giving different products common fields for resource, severity, workflow and compliance. It does not replace GuardDuty, Inspector or Macie; it consumes their conclusions. Enabling a security standard activates its applicable controls, runs checks and calculates a security score, but a passed score is not a legal certification.

Cross-Region aggregation replicates findings, control status and scores from linked Regions into a home Region. With **AWS Organizations**, the multi-account governance service, a delegated administrator and central configuration policies enable standards and controls across accounts and Regions. Aggregation gives a central view only where Security Hub CSPM is already enabled; it never silently activates a missing Region or member account.

Automation rules evaluate newly ingested or updated findings and change fields such as severity, workflow status and notes, which suits elevating a production-account finding or suppressing a documented informational pattern. They do not invoke Lambda or Systems Manager. For an actual response, match the finding on EventBridge and invoke a target with an IAM role limited to the required repair.

## AWS Config: recording, evaluation and remediation

Config begins with a configuration recorder, which discovers supported resource types in one account and Region and creates a configuration item, a point-in-time description of attributes, relationships and related events. Continuous recording captures changes as they occur; daily recording creates an item only when a supported type's configuration differs from the last one recorded. A service-linked or customer-managed IAM role gives Config permission to inspect the selected resources.

Choose the recording scope deliberately. Recording all current and future types reduces governance gaps, but global and high-change resources create unnecessary items and cost, and exclusions let a broad strategy omit chosen types. A delivery channel sends configuration snapshots and history files to Amazon S3 and can notify an **Amazon Simple Notification Service (Amazon SNS)** topic, the managed publish-subscribe messaging service. Neither the recorder nor the delivery channel evaluates a policy.

A Config rule evaluates resources against desired conditions and returns `COMPLIANT`, `NON_COMPLIANT`, `NOT_APPLICABLE` where the rule's logic does not apply, or `ERROR` where a parameter is invalid. Managed rules carry AWS-authored logic; custom rules use AWS Lambda or Guard custom policy.

Two independent properties of a rule decide exam questions. The trigger type says when it runs: a configuration-change trigger fires when Config records a change inside the rule's scope, which can be resource types, a type plus a resource ID, or a tag key and value; a periodic trigger runs on a chosen frequency such as every 24 hours, which is what an account-wide check needs because no single resource change signals it; a hybrid rule has both. The evaluation mode says what it looks at: a detective rule evaluates deployed resources, a proactive rule evaluates proposed properties before deployment where the rule and resource type support it. Proactive evaluation returns a verdict but neither blocks creation nor remediates, so the deployment tool must act on the result.

A conformance pack groups rules and optional remediation actions in a YAML template, deployed to one account and Region or, as an organization conformance pack, to every member account. Packs give a common baseline without turning a framework name into certification, and their rules remain ordinary Config rules, so recording the evaluated resource types still matters.

Remediation associates a noncompliant rule with a Systems Manager Automation runbook. Manual remediation hands an operator the action; automatic remediation starts it on noncompliance, with retries and a role scoped to only that repair. Automatic repair suits a deterministic, reversible change; require review when a repair could delete data or undo an intentional exception. Remediation can also start from a stale snapshot after another process already fixed the resource, so the runbook should verify current state and be idempotent.

A configuration aggregator creates a read-only, central inventory and compliance view across selected accounts and Regions, and an organization aggregator discovers member accounts without listing them. Aggregation deploys nothing and remediates nothing, so pair it with organization conformance packs when the requirement is both central visibility and consistent controls.

Advanced queries are what make an aggregator more than a dashboard. Config exposes one endpoint accepting a subset of SQL `SELECT` over current configuration item metadata, with aggregate functions, so a single statement answers "which S3 buckets have versioning disabled" without a describe call per service. Run that statement against an aggregator and it covers every account and Region in it, which is the standard Professional pattern for an inventory question answered from one account. Two limits decide whether it applies: the language has no `JOIN`, `DISTINCT` or `HAVING` and cannot unpack nested structures such as tags, and a resource type the recorder does not record is invisible to the query, so a gap in recording scope surfaces as a wrong answer rather than an error.

Config and CloudTrail answer neighboring questions. Config shows what a resource looked like and whether that state met a rule; CloudTrail shows who made an API call, when, with the request and response. Use Config to locate the configuration transition and CloudTrail to attribute the action. Config pricing follows recorded configuration items, rule evaluations and conformance pack evaluations.

## Audit evidence, data retention and provider reports

Audit Manager, the service for continuously collecting evidence against control frameworks, maps evidence sources to controls in an assessment and lets an audit owner review evidence before producing an assessment report. Evidence comes from AWS API calls, CloudTrail activity, Config evaluations and Security Hub CSPM checks. It organizes evidence about the customer's environment without certifying it.

As of April 30, 2026, Audit Manager is in maintenance mode and closed to new customers. Existing customers continue where it was already set up, but AWS adds no new features, frameworks or Regions and directs new compliance designs toward Config conformance packs. That is not a feature-for-feature replacement: Config records configuration items rather than the broader evidence set and produces no equivalent audit report. A scenario for an existing deployment may still key to assessments; a new-customer architecture should not propose enabling the service.

Artifact, the self-service portal for AWS compliance documents and agreements, answers a different request. Artifact Reports downloads AWS or AWS Marketplace vendor documents such as SOC reports and ISO certifications; Artifact Agreements reviews, accepts and tracks eligible agreements. These demonstrate controls operated by AWS or the vendor, not whether the customer's own workloads meet the customer's controls. The distinction is clean: download the provider's report from Artifact, evaluate resource state with Config, and aggregate posture with Security Hub CSPM.

Secure the evidence path as carefully as the workloads it describes. Limit security-service administration to dedicated roles, encrypt findings and exported evidence with a customer-managed **AWS Key Management Service (AWS KMS)** key, the managed encryption-key service, restrict the S3 evidence bucket with public access blocking and least-privilege policies, and keep the response role separate from the analyst role.

Retention is where classification turns into architecture, and each mechanism answers a different obligation. **S3 Lifecycle** rules move objects between storage classes and expire them on an age schedule, a cost and hygiene control rather than a guarantee, because anyone holding delete permission can remove an object early. **S3 Object Lock** is the guarantee: write-once-read-many protection on individual object versions, requiring versioning, with a retention period in governance mode, which a principal holding `s3:BypassGovernanceRetention` can override, or compliance mode, which no principal including the account root user can shorten before the retain-until date. A legal hold gives the same protection with no expiry until an authorized principal removes it, which is what an unpredictable litigation window needs. The equivalent for the standalone **Amazon Glacier** vault service is a Vault Lock policy, written in IAM policy language and permanently unchangeable once locked, but note the status: Glacier vaults are closed to new customers, so a new architecture reaches for Object Lock. Lifecycle and lock combine, because lifecycle can transition a locked version to a colder class but cannot delete it before retention allows. [Amazon S3](../01-storage/s3.md) covers the modes in more detail.

Evidence retention is service-specific, and a central console is not automatically the system of record. Service retention periods rarely match an audit obligation, so export the required findings, configuration history and activity records into durable storage, then lock the copy that has to survive. Test that chain in every governed Region: a control that reports correctly but routes to an abandoned queue or retains less history than policy requires has not met the requirement.

## Professional depth

Build the organization around a delegated security administration account rather than the management account doing daily analysis. Enable GuardDuty, Inspector, Macie, Security Hub CSPM and Security Hub through their Organizations integrations across every governed account and required Region. Delegated administration is per service: appointing one delegated administrator does not make it administrator for the others. Keep a log archive account for durable evidence and a security tooling account for findings, investigations and response automation.

One prerequisite changed on May 27, 2026 and it retires an old mapping. Security Hub CSPM controls have always needed Config recording for the resource types they evaluate, and the classic fix for a failing control was to enable Config in that account and Region. Now, when both Security Hub and Security Hub CSPM are enabled, CSPM creates and manages a service-linked recorder named `AWSConfigurationRecorderForSecurityHubCSPM` in each such account and Region, aligns its scope with the supported controls, and ignores the customer-managed recorder. Enable CSPM without the new Security Hub and the old rule still applies: Config must be enabled manually in every Region, or controls stay unevaluated.

Centralization has two layers. Security Hub CSPM cross-Region aggregation brings normalized findings, control results and scores into a home Region, while a Config aggregator brings configuration and compliance data into a central view that advanced queries can run against. Neither enables the source service or deploys its policy. Use central configuration policies and organization conformance packs for deployment, aggregators for visibility, and Organizations service control policies for preventive permission boundaries. A service control policy caps available permissions but evaluates no resource configuration, so it is not a Config-rule substitute.

Route findings through EventBridge to a pipeline that separates enrichment, approval and repair. A high-severity GuardDuty finding can open an investigation, query Detective, isolate an instance with a narrowly scoped runbook and retain its volumes for forensics. Use dead-letter handling, idempotency and immutable evidence storage so failed or repeated events do not make an incident worse. Suppressions and exceptions are policy objects that need owners and expiry dates: an automation rule marking a finding `SUPPRESSED` changes workflow metadata without removing the risk.

## Worked scenario

A financial company has 70 AWS accounts in several organizational units and operates in four Regions. It must detect compromised credentials and vulnerable compute, locate customer identifiers in S3, enforce encryption configuration, collect evidence, and give the security operations team one triage queue. Repairs to production resources require approval, but an accidentally public development bucket may be restricted automatically.

The company designates a security tooling account as delegated administrator for GuardDuty, Inspector, Macie and Security Hub CSPM, enables each in every governed account and Region, and adds the new Security Hub so that exposures and unused access findings are correlated centrally. Security Hub CSPM aggregates findings in one home Region and sends actionable ones through EventBridge, where the pipeline adds account and environment context, opens an approval for production, and invokes an idempotent Systems Manager Automation runbook for permitted repairs. Detective supports investigations of GuardDuty findings. Config recorders capture governed resource types, organization conformance packs deploy encryption and public-access rules, automatic remediation handles the approved development case, and an organization aggregator answers advanced queries for the central inventory. CloudTrail records the API actor, and an S3 log archive under Object Lock retains audit data. As a new Audit Manager customer after April 30, 2026, the company relies on Config evidence and downloads AWS provider reports from Artifact.

The exam asks which combination gives organization-wide detection, central posture, configuration enforcement and defensible evidence without confusing a report portal with customer compliance. The keyed design is organization-enabled detector services plus Security Hub CSPM aggregation and EventBridge response, Config conformance packs with scoped remediation and aggregation, CloudTrail for attribution, and Artifact for provider reports.

## Exam lens

- "Suspicious API calls or credentials used from an unusual location" maps to GuardDuty; Inspector is the distractor because it finds workload vulnerabilities, not behavioral threats.
- "Continuously rescan ECR images when a new CVE is published" maps to Inspector enhanced scanning; a one-time pipeline scan misses vulnerabilities disclosed after the build.
- "EC2 instances unintentionally reachable from the internet" maps to Inspector network reachability; GuardDuty is the distractor because it reports activity that occurred, not an open path that exists.
- "Scan uploaded S3 objects before the application processes them" maps to GuardDuty Malware Protection for S3; Macie answers whether an object is sensitive, not whether it is malicious.
- "One finding that describes a multi-step attack sequence" maps to GuardDuty Extended Threat Detection, which is automatic and free and needs no protection plan.
- An unqualified "AWS Security Hub" in a stem about standards, controls, scores or ASFF maps to Security Hub CSPM; reserve the new Security Hub for exposures, attack paths and unused access.
- "Find IAM roles, access keys or permissions unused for 90 days" maps to IAM Access Analyzer unused access findings, at a fixed 90 days through the Security Hub service-linked analyzer and anywhere from 1 to 365 days through a customer-managed one; a Config rule cannot infer use from configuration, and an external access analyzer is needed once per Region for the different question of external sharing.
- "Investigate entities and activity related to a GuardDuty finding" maps to Detective; Security Hub CSPM is the aggregation layer, not the behavior graph.
- "Record how a security group changed and evaluate it against an allowed-port policy" maps to Config; add CloudTrail when the question asks who issued the API call.
- "Evaluate every account once a day even when nothing changed" maps to a periodic Config rule; a configuration-change trigger never fires without a recorded change.
- "Test a proposed resource configuration before deployment" maps to a proactive Config rule, but the deployment tool must enforce the result because evaluation alone does not block creation.
- "Query current resource state across every account from one place" maps to a Config advanced query against an organization aggregator; unrecorded resource types are invisible to it.
- "Deploy the same detective controls across an AWS organization" maps to an organization conformance pack, not to a Config aggregator, which is read-only visibility.
- "Retain records so that no administrator can delete them before a deadline" maps to S3 Object Lock compliance mode; governance mode has a bypass permission and a lifecycle rule only expires objects.
- "A finding must quarantine a resource" maps to EventBridge plus a least-privilege response target; findings do not perform that repair themselves.

## Knowledge check

### 1. Reconstructing a role's activity during an investigation (Associate)

A GuardDuty finding names an IAM role in a production account as the source of suspicious API calls. Before containment, an analyst must see the entities related to that role, including the source addresses and EC2 instances connected to it, and must see how the type and volume of that role's activity changed over the previous four months. The security team does not want to build a log analytics pipeline or change the account's existing trail and flow log configuration.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Use the GuardDuty Extended Threat Detection attack sequence finding for the role as the record of its activity.
- **B)** Review the attack path graph on the AWS Security Hub exposure finding for the affected role.
- **C)** Run an AWS Config advanced query against an organization aggregator for every resource the role changed.
- **D)** Enable Amazon Detective and review the role's entities and activity in the behavior graph.

<details><summary>Answer</summary>

**Answer: D.** Detective ingests CloudTrail management events and VPC flow logs on its own, links principals, addresses and instances into a behavior graph, and retains each source package for up to a year, so a four-month range is exactly what it shows, and the ingest neither depends on nor changes existing trails. A fails on the window: Extended Threat Detection correlates signals over a rolling 24-hour period into one attack sequence finding, not months of entity activity. B describes one correlated current risk and how an attacker could move to downstream resources, not the history of a single principal. C reads recorded configuration item metadata, so it can report what a resource looks like but not who used it or when.

*Where this is covered: Amazon Detective.*

</details>

### 2. A vulnerability disclosed after image deployment (Associate)

A company stores container images in Amazon ECR. An image passed all checks when it was built, but the security team needs the image to be reevaluated when new CVEs affecting its packages are published.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Run an AWS Config managed rule whenever the ECR repository policy changes.
- **B)** Add an image vulnerability scan step to the build pipeline and fail the build on any High severity CVE.
- **C)** Enable Amazon Inspector enhanced scanning for the ECR repository.
- **D)** Enable GuardDuty Runtime Monitoring for the build account only.

<details><summary>Answer</summary>

**Answer: C.** Inspector enhanced scanning continuously evaluates ECR images and rescans them as vulnerability intelligence changes. A evaluates configuration rather than packages inside an image, so a repository-policy rule cannot detect the new CVE. B inspects the image only at the moment it is built, which is the exact gap in the stem: a CVE published after the image is stored is never detected, and the team would still have to rebuild and rerun the pipeline to learn about it. D observes supported runtime behavior on instances and containers and does not provide the requested continuous package-vulnerability assessment of stored images.

*Where this is covered: GuardDuty, Inspector and Macie.*

</details>

### 3. Locating regulated data in object storage (Associate)

A company has hundreds of S3 buckets and does not know which objects contain national identification numbers. It wants broad visibility first, followed by a deliberately scoped scan of the buckets most likely to contain regulated data.

Which solution will meet these requirements?

- **A)** Enable GuardDuty Malware Protection for S3 on the buckets and review the result tags it applies to new objects.
- **B)** Enable Macie automated sensitive data discovery, then run targeted sensitive data discovery jobs.
- **C)** Enable Macie and use the policy findings it produces for publicly exposed buckets to locate the regulated data.
- **D)** Build a Lambda function that reads every object, matches national identification numbers with a regular expression, and writes the matches to a report.

<details><summary>Answer</summary>

**Answer: B.** Macie automated discovery samples the S3 estate for broad visibility, and targeted discovery jobs then provide deliberate coverage of selected buckets, scope and sampling depth. A answers whether an object is malicious rather than whether it is sensitive, so its result tags say nothing about which objects hold national identification numbers. C reports bucket access posture such as public exposure, which locates risky permissions rather than regulated content, and a private bucket full of identifiers produces no policy finding. D rebuilds by hand what Macie already manages, since a custom data identifier is a regular expression plus optional proximity terms with allow lists for known acceptable values.

*Where this is covered: GuardDuty, Inspector and Macie.*

</details>

### 4. Enforcing an encryption baseline (Associate)

A company needs to evaluate whether supported resources use an approved encryption configuration and automatically correct a simple noncompliant setting. It also needs configuration history delivered to durable storage.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Configure an AWS Config recorder and delivery channel for the required resource types.
- **B)** Enable a proactive Config rule and rely on it to block deployment of the noncompliant setting.
- **C)** Create a Config aggregator and rely on it to deploy rules and modify source resources.
- **D)** Deploy a Config rule with automatic remediation that invokes an approved Systems Manager Automation runbook.
- **E)** Download an AWS encryption certification from Artifact and use it as proof of each resource's configuration.

<details><summary>Answer</summary>

**Answer: A and D.** A records the selected resources and delivers configuration history, while D evaluates the desired state and associates noncompliance with an actual repair workflow. B fails because a proactive rule returns a verdict on proposed properties but neither blocks creation nor remediates, so the setting already deployed is never corrected. C fails because an aggregator is a read-only central view and neither deploys controls nor remediates sources. E provides AWS-operated-control documentation, not evidence or enforcement of the customer's individual resource configurations.

*Where this is covered: AWS Config: recording, evaluation and remediation.*

</details>

### 5. Reporting IAM principals that stopped being used (Professional)

A company runs workloads in three Regions under one AWS Organizations organization and has enabled the new AWS Security Hub in its delegated administrator account. An internal standard requires that any IAM role, access key or console password unused for 45 consecutive days be reported so that the owning team can remove it, and the security team must report against that 45-day threshold rather than a longer one. The team also wants to avoid creating and paying for a separate analyzer in every Region.

Which solution will meet these requirements?

- **A)** Create a customer-managed IAM Access Analyzer unused access analyzer with the organization as its zone of trust and a tracking period of 45 days.
- **B)** Use the unused access findings from the service-linked IAM Access Analyzer that enabling AWS Security Hub creates.
- **C)** Create an IAM Access Analyzer external access analyzer in each of the three Regions with the organization as its zone of trust.
- **D)** Enable Amazon Detective in the delegated administrator account and review each role's activity in the behavior graph for the previous 45 days.

<details><summary>Answer</summary>

**Answer: A.** A customer-managed unused access analyzer reports unused roles, access keys, console passwords and permissions, its tracking period is configurable anywhere between 1 and 365 days, and unused access findings do not vary by Region, so one analyzer covers the organization. B produces the same finding types but on a fixed, non-configurable 90-day lookback, so it never reports a principal at the 45-day mark the standard requires. C answers the different question of which resources are shared outside the zone of trust, and external access findings cover only the Region where the analyzer was created, so it needs one per Region. D can show what a principal did, but the behavior graph is an investigation view rather than an inventory of unused roles, keys and passwords.

*Where this is covered: Security Hub, Security Hub CSPM and IAM Access Analyzer.*

</details>

### 6. Central controls and visibility across an organization (Professional)

A company must apply one set of configuration controls to every governed AWS account and Region, then query compliance centrally. New accounts must receive the controls without an administrator adding each account manually.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Apply an AWS Organizations service control policy that denies the noncompliant configurations in every member account.
- **B)** Deploy an AWS Config organization conformance pack containing the required rules and remediation definitions.
- **C)** Create one customer-managed AWS Config rule in the management account and give it cross-account permission to evaluate resources in every member account.
- **D)** Deploy an AWS Config conformance pack containing the required rules in each member account individually.
- **E)** Create an AWS Config organization aggregator and query it for configuration and compliance across the accounts and Regions.

<details><summary>Answer</summary>

**Answer: B and E.** B distributes the common Config control set to every member account that the organization discovers, and E collects configuration and compliance into a central read-only view that advanced queries can run against. A caps the permissions available in each account but evaluates no resource configuration, so it is not a Config-rule substitute and leaves nothing to query centrally. C misreads the account boundary of a Config rule, which evaluates only resources recorded in the account and Region where it exists, so every member account stays without controls. D deploys the same rules but repeats the deployment account by account, which is the manual step for each new account that the stem rules out.

*Where this is covered: Professional depth.*

</details>

### 7. Supplying a provider compliance report (Associate)

In September 2026, an auditor asks a new AWS customer for AWS's current SOC report and for the customer's own evidence that production resources meet its encryption rule. The customer has never enabled Audit Manager and needs both artifacts without building a custom evidence store.

Which solution will meet these requirements?

- **A)** Enable Audit Manager for the new customer and use it both to download the AWS SOC report and to evaluate resource configuration.
- **B)** Download the AWS SOC report from Artifact and present the Security Hub CSPM security score for the AWS Foundational Security Best Practices standard as the encryption evidence.
- **C)** Download the AWS SOC report from Artifact and use AWS Config rules and retained configuration items for the resource-state evidence.
- **D)** Download the AWS SOC report from Artifact and use CloudTrail Event history as the record of each resource's encryption state.

<details><summary>Answer</summary>

**Answer: C.** Artifact provides AWS compliance reports, while Config rules and configuration items supply point-in-time evidence about supported customer resource state. A is unavailable because Audit Manager closed to new customers on April 30, 2026, and it was never the portal for AWS provider reports. B supplies a posture score that informs risk but is not per-resource evidence and is not a certification. D produces the right report but the wrong customer evidence, because CloudTrail records the API calls that changed a resource rather than the resource's configuration at a point in time.

*Where this is covered: Audit evidence, data retention and provider reports.*

</details>

### 8. Designing a safe response pipeline (Professional)

A security team wants organization-wide threat detection and automated containment. A repeated high-severity GuardDuty finding must be enriched centrally, but production isolation requires human approval and duplicate events must not repeat a completed change.

Which combination of steps will meet these requirements? (Select THREE.)

- **A)** Send normalized findings from Security Hub CSPM through EventBridge to an idempotent response workflow.
- **B)** Configure a Security Hub CSPM automation rule to invoke the containment runbook as soon as the finding is ingested.
- **C)** Insert an approval step before the production Systems Manager Automation runbook changes the resource.
- **D)** Add a GuardDuty suppression rule for the repeated finding type so that duplicate events never reach the response workflow.
- **E)** Enable the detector services through their Organizations integrations in every governed account and required Region.

<details><summary>Answer</summary>

**Answer: A, C and E.** A provides central routing and makes repeated delivery safe, C preserves the required production approval boundary, and E supplies broad detector coverage rather than relying on a single account or Region. B fails because an automation rule can only update finding fields such as severity, workflow status and notes; it has no Lambda or Systems Manager action, so no runbook would ever start. D suppresses the duplicates but also suppresses the finding itself, losing the enrichment the stem requires and removing an archived signal from Extended Threat Detection correlation.

*Where this is covered: Professional depth.*

</details>

## Summary

Choose these services by the evidence object. GuardDuty detects suspicious behavior and, through Extended Threat Detection, narrates a multi-step attack in one Critical finding at no extra cost. Inspector finds vulnerabilities in supported compute and images and reports which EC2 instances are reachable from a VPC edge. Macie discovers sensitive data in S3, while GuardDuty Malware Protection for S3 answers the different question of whether an object is malicious. Detective connects entities and up to a year of activity during an investigation. Security Hub CSPM, the service formerly named AWS Security Hub, normalizes findings in ASFF, evaluates standards and updates finding fields; the newer AWS Security Hub correlates those signals into OCSF exposure findings with an attack path graph and surfaces unused access findings from a service-linked IAM Access Analyzer on a 90-day lookback. EventBridge and a response target perform actual containment. Config records resource state, evaluates rules by trigger type and evaluation mode, packages controls in conformance packs, remediates through Systems Manager Automation, and answers advanced queries against an organization aggregator. Artifact supplies AWS provider reports, Audit Manager organizes customer-control evidence for existing customers only, and S3 Object Lock or a legal hold makes the retained evidence immutable.

## Related units

- [AWS CloudTrail](../08-management/cloudtrail.md): API attribution and durable activity evidence alongside Config history
- [AWS Systems Manager](../08-management/systems-manager.md): Automation runbooks used by Config and incident response workflows
- [Amazon EventBridge](../06-integration/eventbridge.md): event routing from findings to enrichment, approval and remediation targets
- [AWS Organizations, IAM Identity Center and AWS Control Tower](organizations-identity-center-and-control-tower.md): delegated administration and organization-wide policy deployment
- [AWS Identity and Access Management](iam.md): least-privilege analyst, recorder and remediation roles, and the policies Access Analyzer reasons about
- [AWS Key Management Service and CloudHSM](kms-and-cloudhsm.md): customer-managed keys for supported evidence and finding stores
- [Amazon S3](../01-storage/s3.md): Object Lock retention modes, lifecycle and encryption for evidence buckets
- [AWS Backup and disaster recovery](../01-storage/backup-and-disaster-recovery.md): backup vaults scanned by Malware Protection for Backup and retained under policy

## Sources

- [What is Amazon GuardDuty?](https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html): foundational data sources, findings and managed threat detection
- [Configuring protection plans](https://docs.aws.amazon.com/guardduty/latest/ug/protection-plans.html): the current protection plan lineup and where each is configured
- [Extended Threat Detection](https://docs.aws.amazon.com/guardduty/latest/ug/guardduty-extended-threat-detection.html): automatic enablement, no extra cost, attack sequence findings, 24-hour window, archived findings excluded
- [AI Protection](https://docs.aws.amazon.com/guardduty/latest/ug/ai-protection.html): Bedrock and SageMaker AI data events, anomalous invocation, cost harvesting and prompt injection
- [EKS Protection](https://docs.aws.amazon.com/guardduty/latest/ug/kubernetes-protection.html): EKS audit log monitoring as a capability inside the plan
- [Malware Protection for AWS Backup](https://docs.aws.amazon.com/guardduty/latest/ug/malware-protection-backup.html): scanning EBS snapshots, AMIs and S3 recovery points before restore
- [Malware Protection for S3](https://docs.aws.amazon.com/guardduty/latest/ug/gdu-malware-protection-s3.html): scanning newly uploaded objects and publishing scan results
- [Amazon Inspector finding types](https://docs.aws.amazon.com/inspector/latest/user/findings-types.html): package, code and network reachability findings, 12-hour scans, evaluated network path
- [Scanning resources with Amazon Inspector](https://docs.aws.amazon.com/inspector/latest/user/scanning-resources.html): agent-based and agentless EC2 scanning and supported resource modes
- [What is Amazon Macie?](https://docs.aws.amazon.com/macie/latest/user/what-is-macie.html): S3 inventory, policy findings and sensitive data discovery
- [Performing automated sensitive data discovery](https://docs.aws.amazon.com/macie/latest/user/discovery-asdd.html): estate-wide sampling and classification behavior
- [Discovering sensitive data with jobs](https://docs.aws.amazon.com/macie/latest/user/discovery-jobs.html): targeted one-time and scheduled discovery
- [What is Amazon Detective?](https://docs.aws.amazon.com/detective/latest/userguide/what-is-detective.html): behavior graph, finding groups, Detective Investigation and Security Lake integration
- [Source data used in a Detective behavior graph](https://docs.aws.amazon.com/detective/latest/userguide/detective-source-data-about.html): independent ingest, one year of retention and optional source packages
- [What is Amazon Security Lake?](https://docs.aws.amazon.com/security-lake/latest/userguide/what-is-security-lake.html): customer-owned OCSF data lake in Amazon S3
- [What are Security Hub and Security Hub CSPM?](https://docs.aws.amazon.com/securityhub/latest/userguide/what-are-securityhub-services.html): the two services, how they complement each other and what breaks when only one is enabled
- [Introduction to AWS Security Hub](https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub-v2.html): correlation, OCSF findings, attack path graph and the service-linked unused access analyzer
- [Understanding unused access findings in Security Hub](https://docs.aws.amazon.com/securityhub/latest/userguide/unused-access-findings.html): 90-day lookback, four finding types, service-linked analyzer and no extra cost
- [Security Hub document history](https://docs.aws.amazon.com/securityhub/latest/userguide/doc-history.html): Security Hub general availability on December 2, 2025 and the May 27, 2026 CSPM recorder change
- [What is IAM Access Analyzer?](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html): external, internal and unused access analyzers, zone of trust, supported resources and Regional scope
- [Enabling and configuring AWS Config for Security Hub CSPM](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-setup-prereqs.html): the service-linked configuration recorder and when manual Config setup is still required
- [Security standards and controls](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-standards.html): standards, controls and security scores
- [Automation rules](https://docs.aws.amazon.com/securityhub/latest/userguide/automation-rules.html): finding-field updates and evaluation behavior
- [Cross-Region aggregation](https://docs.aws.amazon.com/securityhub/latest/userguide/finding-aggregation.html): home and linked Regions and replicated data
- [Security Hub CSPM findings in EventBridge](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-cloudwatch-events.html): routing finding events to response targets
- [Recording frequency](https://docs.aws.amazon.com/config/latest/developerguide/select-resources.html): continuous and daily recording behavior and resource selection
- [Components of an AWS Config rule](https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_components.html): evaluation results, configuration-change, periodic and hybrid triggers, detective and proactive modes
- [Querying the current configuration state of AWS resources](https://docs.aws.amazon.com/config/latest/developerguide/querying-AWS-resources.html): advanced query SQL subset, aggregate functions, aggregator scope and limitations
- [Conformance packs](https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html): grouped rules and remediation actions in YAML
- [Remediating noncompliant resources](https://docs.aws.amazon.com/config/latest/developerguide/remediation.html): manual and automatic Systems Manager Automation remediation
- [Aggregating data](https://docs.aws.amazon.com/config/latest/developerguide/aggregate-data.html): central multi-account, multi-Region read-only views
- [AWS Config pricing](https://aws.amazon.com/config/pricing/): configuration item, rule and conformance pack evaluation billing dimensions
- [AWS Audit Manager availability change](https://docs.aws.amazon.com/audit-manager/latest/userguide/audit-manager-availability-change.html): April 30, 2026 closure, maintenance mode and Config gaps
- [What is AWS Audit Manager?](https://docs.aws.amazon.com/audit-manager/latest/userguide/what-is.html): assessments, controls, evidence sources and reports
- [What is AWS Artifact?](https://docs.aws.amazon.com/artifact/latest/ug/what-is-aws-artifact.html): AWS and vendor reports, agreements, customer responsibility and pricing
- [How S3 Object Lock works](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html): WORM protection, retention periods, governance and compliance modes, legal holds
- [Amazon Glacier Vault Lock](https://docs.aws.amazon.com/amazonglacier/latest/dev/vault-lock.html): lockable vault policies, and the standalone vault service closed to new customers
