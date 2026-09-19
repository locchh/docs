# AWS Systems Manager

**Where it sits on the exams.** **AWS Systems Manager**, the managed operations service for AWS, on-premises and other-cloud nodes, provides secure access, fleet inventory, configuration enforcement, patching, automation and operational workflows. Its tools share managed-node registration, **AWS Identity and Access Management (IAM)** permissions, the authorization service, and the **AWS Systems Manager Agent (SSM Agent)** on the machine. Systems Manager serves SAP-C02 tasks 2.1, 2.3, 3.1 and 3.2, owning that guide's bullets on change management processes, configuration management tools, patch management strategy, patch and update process design, and remediation techniques. It owns no SAA-C03 bullet: an Associate candidate meets Systems Manager inside questions other units own, such as reaching a private instance without a bastion. Rule of thumb: **Session Manager** is interactive access, **Run Command** is one-time fleet execution, **State Manager** maintains desired state, **Patch Manager** assesses and installs patches, **Maintenance Windows** schedule disruptive work, and **Automation** runbooks orchestrate multi-step change.

## Build a managed-node fleet

A managed node is a machine configured for Systems Manager: an **Amazon Elastic Compute Cloud (Amazon EC2)** instance, the virtual server service, or a non-EC2 machine registered in a hybrid and multicloud environment. It needs a supported operating system, a current enough SSM Agent, outbound HTTPS to Systems Manager endpoints and credentials authorizing its calls. It can reach those endpoints publicly, through a NAT path or through interface VPC endpoints, and never needs an inbound management port.

SSM Agent is the moving part most often missed. AWS preinstalls it on many of its own images, including Amazon Linux 2 and 2023, the EKS-optimized and ECS-optimized images, recent Ubuntu Server LTS releases, SUSE Linux Enterprise Server 15.3 and later, and Windows Server 2016 through 2025. The preinstalled version is not necessarily the current one, and an agent can be present but not running, so check status before concluding an instance is unmanaged. Keep it current rather than pinning it, because new tools require new agent builds. The Auto update SSM Agent setting in Fleet Manager, or the equivalent option in **Quick Setup**, the guided configuration tool that applies AWS recommended settings across accounts and Regions, creates a State Manager association that checks every two weeks and installs any new version with `AWS-UpdateSSMAgent`. Use a maintenance window instead when agent upgrades must land inside an approved period.

For EC2, attach an instance profile with the `AmazonSSMManagedInstanceCore` managed policy, or use **Default Host Management Configuration**, an account and Region setting that hands eligible EC2 instances a default management role instead of requiring a profile on each one. It needs Instance Metadata Service Version 2 (IMDSv2) and SSM Agent 3.2.582.0 or later, is activated one Region at a time, and yields to an instance profile: the agent tries profile credentials first, so an existing profile allowing `ssm:UpdateInstanceInformation` suppresses the default role. Keep two authorization decisions apart: the service role an Automation runbook assumes, and the identity allowed to start it.

Registration and health are different states. A node stays listed after its agent stops responding, its credentials expire or its route disappears. Systems Manager reports connection status and last ping, while each tool reports its own execution or compliance state. Watch for offline nodes and for expected machines that never registered: an empty compliance dashboard can mean nothing was assessed, not that everything passed.

Hybrid and multicloud nodes use a hybrid activation, which covers on-premises servers, virtual machines in other clouds, and AWS IoT and other edge devices. An administrator calls `CreateActivation` with an IAM service role, then supplies the returned activation code and ID while installing SSM Agent. Two parameters bound that bundle. `RegistrationLimit` caps how many machines the activation may register, defaulting to 1 with a maximum of 1,000. `ExpirationDate` may be set up to 30 days ahead, and if omitted the code expires in 24 hours. Treat code and ID as temporary credentials, issue one activation per trust boundary, and let unused activations lapse. After registration the machine receives a managed-node identity. This is the keyed answer for managing on-premises servers without exposing SSH or Remote Desktop Protocol (RDP) to the internet.

**Fleet Manager** is the console for viewing and administering AWS and on-premises nodes from one page. Beyond node health and connection status it does the work an administrator would otherwise open a shell for: browsing the file system, viewing logs, listing and stopping processes, managing operating-system users and groups, editing the Windows registry, managing attached volumes, reading performance counters, and opening a Remote Desktop connection to a Windows Server node. It also holds the Auto update SSM Agent and Default Host Management Configuration settings. It is an operator console, not an automation engine: nothing it does repeats on a schedule.

**Inventory** collects node metadata on a schedule through a State Manager association. The collected types are fixed categories, not free-form data: applications, AWS components such as agents and drivers, files, network configuration, Windows updates, instance details, services, tags, Windows registry keys and roles, and custom inventory written as a JSON file on the node. The shortest collection interval is 30 minutes, and one node carries one inventory association, so collection is a fleet-wide standard rather than a per-team choice. To query across Regions and accounts, sync the data into a central bucket in **Amazon Simple Storage Service (Amazon S3)**, the durable object storage service, and read it with **Amazon Athena**, the serverless query service for S3 data. Inventory tells you what is installed; it is not a vulnerability scanner. Use **Amazon Inspector**, the continuous vulnerability management service, for CVE findings and Patch Manager for patch compliance.

Resource tags and **AWS Resource Groups**, the tag-based grouping service, are the scalable targeting layer: a command, association, maintenance window or automation targets a changing group rather than a static list of instance IDs. Standardize tags before relying on them in production, and restrict who can attach a tag that moves a node into a privileged target.

## Choose Session Manager, Run Command or State Manager

Session Manager provides interactive shell access and port forwarding to managed nodes. Operators connect from the console, CLI or SDK without inbound SSH or RDP ports, bastion hosts or distributed keys, and IAM policies decide who may start a session and against which nodes. Session preferences stream supported session logs to **Amazon CloudWatch Logs**, the log storage and query feature of **Amazon CloudWatch**, the AWS metrics, logs and alarms service, or to Amazon S3, and can require encryption with **AWS Key Management Service (AWS KMS)**, the managed encryption-key service.

A session document selects the session type. Shell sessions open a command channel, port sessions tunnel a local port to a node or to a host reachable from it, and interactive command sessions restrict the operator to one named command. That last option narrows capability far more effectively than a general shell.

Port forwarding and SSH over Session Manager are tunnels, so Systems Manager cannot log what runs inside those encrypted protocols, while native interactive shell sessions do support input and output logging. **AWS CloudTrail**, the AWS API activity audit service, records control-plane activity such as starting a session, but not shell commands. Choose the access mode against the audit requirement rather than assuming every path yields the same evidence.

Run Command executes a Systems Manager document on one or many managed nodes without an interactive login. Target instance IDs, tags or resource groups; set concurrency and error thresholds to bound blast radius; send output to S3 or CloudWatch Logs when the truncated console response is not enough. AWS-managed documents cover common actions and customer documents define approved commands. Run Command is the answer for an immediate, one-time command across a fleet.

State Manager creates an association between a Systems Manager document and targets, applies or checks desired configuration on a schedule and reports association compliance. Use it to keep an agent installed, enforce a configuration file or collect inventory repeatedly. New tagged nodes enter its target set automatically, but they still need SSM Agent, connectivity and permissions before State Manager can act on them.

The three are complementary: diagnose with Session Manager, repair once with Run Command, convert a stable repair into a State Manager association. Automation wins when the workflow spans AWS APIs, approvals or branches.

## Patch Manager and patch policies

Patch Manager scans managed nodes for patch compliance and installs approved operating-system updates. A patch baseline defines classification and severity filters, explicit approved or rejected patches, products and automatic approval delays. AWS supplies a predefined baseline for each supported operating system, and those cannot be edited. The Windows Server default, `AWS-DefaultPatchBaseline`, approves critical and security updates of Microsoft severity Critical or Important seven days after release. Predefined baselines also assign every patch a compliance level of `Unspecified`, so a report that needs severity requires a copied baseline. Three rules decide exam questions: a patch listed as both approved and rejected in one baseline is rejected, a node resolves to exactly one baseline, and the auto-approval delay turns "wait a week before production sees a vendor update" into configuration rather than process. A patch group, defined by the tag key `Patch Group` or `PatchGroup`, registers sets of nodes against different baselines, but it is legacy: patch policies do not use patch groups, and the console exposes them only in account and Region pairs already using them before December 22, 2022.

Scanning reports missing, installed and failed patch states without installing anything; installing changes packages and can require a reboot. The `AWS-RunPatchBaseline` document performs either operation against the applicable baseline. Patch Manager drives the operating system's own package manager, so repository reachability, disk space and package conflicts remain customer responsibilities, and a compliant scan does not prove the application still works.

A patch snapshot keeps the approved set consistent during one patching operation. Maintenance window executions supply a snapshot ID automatically, and other orchestrations should pass a stable one when an operation spans nodes. Without it, repository metadata or approval-delay boundaries can shift between invocations and give identical nodes different results. Snapshots do not freeze package binaries in a customer repository.

Reboot choice is separate from installation, and `RebootOption` is the most misread setting in the tool. Its default, `RebootIfNeeded`, does not mean what the name suggests: Patch Manager does not evaluate whether a patch requires a reboot. It reboots the node if it installed one or more patches during the operation, even when none needed a restart, and it also reboots when it finds patches in `INSTALLED_PENDING_REBOOT` state left by an earlier `NoReboot` run or by a patch installed outside Patch Manager. `NoReboot` suppresses the restart: installed patches take the status `InstalledPendingReboot` and the node is marked `Non-Compliant` until a reboot and a later scan clear it. It prevents only operating-system restarts, so a service-level restart can still interrupt a workload when a package such as Docker is updated. A scenario saying "install now but never interrupt the instance" must account for that deferred state.

Patch policies configured through Quick Setup are the current organization-scale workflow. A policy sets scan and installation schedules, baseline and reboot behavior, and targets across accounts and Regions, and Quick Setup creates the associations and supporting resources. Use a patch policy when one configuration must follow accounts added to selected organizational units, and a maintenance window when patching must sit among other ordered tasks.

Design separate scan and install cadences. Frequent scans reveal exposure without changing nodes. Install first on a canary group, verify application metrics rather than invocation status, then expand in waves under concurrency and error controls. A patch command can exit zero while a dependency, cluster quorum or latency objective fails. Patch compliance is an input to risk decisions; Amazon Inspector adds CVE severity but does not install the patch.

## Automation, maintenance windows and change control

Systems Manager Automation runs multi-step runbooks that call AWS APIs, run commands, branch on values, wait, pause for approval and invoke other automations. AWS-managed runbooks cover common operations; custom YAML or JSON documents encode an organization's own procedure. The execution role needs the actions in the runbook, and the initiating identity needs permission to start the automation and to pass that role.

The approval gate is a step, not a separate product. An `aws:approve` action pauses the automation until named approvers supply `MinRequiredApprovals` decisions, optionally notified through an **Amazon Simple Notification Service (Amazon SNS)** topic, the managed publish and subscribe service. It times out after seven days by default, up to 30 with `timeoutSeconds`. One constraint decides Professional questions: `aws:approve` is not supported in multi-account and multi-Region automations, so a design that fans out across accounts and needs a human decision must gate before the fan-out.

Maintenance Windows schedule tasks against registered targets during an approved period. Task types are Run Command, Automation, **AWS Lambda**, the serverless function service, and **AWS Step Functions**, the managed workflow service. A window defines its schedule, duration and cutoff; tasks add priority, concurrency and error thresholds. Duration is a whole number of hours from 1 to 24 and fixes the end time. Cutoff is a required whole number of hours from 0 to 23, read as a deadline measured backward from that end: no new task starts after the end time minus the cutoff, so a window beginning at 15:00 with a duration of three hours and a cutoff of one hour starts no task after 17:00. Cutoff says nothing about how long a task runs. It does not estimate duration, refuse a task that will overrun, or terminate a task already running when the window closes.

Treat runbook parameters as an interface: declare types and allowed patterns, and prefer a bounded choice to an arbitrary command string. Application-level rollback is the author's problem, so an `onFailure` path that captures diagnostics or calls a recovery runbook beats one that stops halfway through changing resources.

**Change Calendar** stores open and closed states that Automation can check before changing resources. A calendar entry is a Systems Manager document of type `ChangeCalendar` holding iCalendar 2.0 data, so events can be imported from a third-party calendar. The exam fact is the entry type, which inverts the meaning of every event on it. A `DEFAULT_OPEN` calendar permits all actions except during its events: the shape of a release freeze. A `DEFAULT_CLOSED` calendar blocks all actions except during its events: the shape of an approved change window, where nothing runs unless an event says it may. Automation, Maintenance Windows and State Manager can each check a calendar. The calendar does not itself execute a change, approve a request or remediate a node.

**Change Manager** is the Systems Manager framework for change templates, requests, approvals, calendars and Automation runbooks. It can coordinate changes across accounts and Regions from a delegated administrator for existing customers. However, it closed to new customers on November 7, 2025. Existing customers continue to use it; a new-customer design should evaluate an AWS Partner Network enterprise change-management solution. On an exam question that explicitly describes an established Change Manager environment, map approval templates and controlled runbook execution to Change Manager. Do not propose enabling it for a new customer in 2026.

## Event-driven remediation and multi-account automation

SAP-C02 asks how a detection becomes a fix with no human in the path. Systems Manager supplies the fix, wired two ways the exam keeps distinct.

The first is event-driven. An **Amazon EventBridge** rule, on the managed event bus, names an Automation runbook directly as its target, so a matched event starts an execution with parameters drawn from the event. The rule needs an IAM role allowing `ssm:StartAutomationExecution` and `iam:PassRole` for the runbook's execution role. Nothing sits in between: no function to maintain, no queue to drain.

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": { "state": ["running"] }
}
```

The second is compliance-driven. **AWS Config**, the service that records resource configurations and evaluates them against rules, attaches a remediation action to a rule, and that action is an SSM Automation document, either one AWS ships or a custom runbook. Remediation is manual, where an operator selects noncompliant resources and triggers it, or automatic, where Config runs the document as soon as a resource is evaluated noncompliant. Use Config when the requirement is continuous evaluation with a recorded compliance state per resource, and EventBridge when it is reaction to a discrete event. Where a human must decide first, route the finding to an OpsItem with the runbook attached.

Automation also runs across accounts and Regions in one execution, the pattern behind organization-wide remediation. Nominate a central account, ideally a delegated administrator registered for the `ssm.amazonaws.com` service principal in **AWS Organizations**, the multi-account management service, so it can enumerate organizational units. The central account holds `AWS-SystemsManager-AutomationAdministrationRole`; every target account holds `AWS-SystemsManager-AutomationExecutionRole` under that same name, because the automation assumes it by name in each location. Target locations name accounts or organizational units plus Regions, and `TargetLocationMaxConcurrency` and `TargetLocationMaxErrors` throttle how many run at once and how many may fail.

## OpsCenter, Application Manager and Incident Manager

**OpsCenter** centralizes operational work items called OpsItems. A CloudWatch alarm, an EventBridge rule or another integrated source creates an OpsItem carrying the affected resource, related events, runbooks and context. OpsCenter organizes diagnosis and remediation; it does not enforce configuration like State Manager, nor replace a service desk unless its workflow meets the business need.

An OpsItem has a lifecycle, ownership, priority, related resources and operational data, and a responder can run an associated Automation runbook and keep the result with the issue. Use a stable deduplication string so a repeating alarm updates one work item instead of flooding the queue, but keep items separate when one alarm name covers unrelated resources.

**Application Manager** groups and displays resources in an application context, using resource groups and application tags to surface operations, cost and monitoring information. It entered maintenance mode and closed to accounts that had not previously used it on July 30, 2026. Existing customers can continue, but AWS is adding neither features nor Regions. AWS recommends tags plus Resource Groups for organization, **AWS Resource Explorer**, the resource search service, for cross-Region and cross-account discovery, and **Amazon CloudWatch Application Signals**, the application performance and dependency monitoring feature, for application observability.

**AWS Systems Manager Incident Manager** coordinates response plans, contacts, escalation plans, timelines, chat channels and runbooks for an incident. A response plan standardizes who is engaged and what automation starts when an incident is created. Incident Manager closed to new customers on November 7, 2025 and receives no new features, while existing enabled accounts continue. AWS directs new customers to the documented migration alternatives and recommends exporting existing incident data during a move. Keep the exam mapping for an established customer, but do not present Incident Manager as a new 2026 deployment.

For an existing customer, design contacts and escalation plans around several reachable channels and test the complete response plan. Starting an incident can create collaboration resources and invoke a runbook, but the response still needs current ownership, least-privilege automation and retained evidence. For a migration, export the incident history before removing resources; a replacement that pages people but loses timelines, action records or service-management integration is not functionally equivalent.

These tools represent three different objects. An OpsItem is an operational issue to investigate and remediate. An application is a resource grouping and health context. An incident is a coordinated response with engagement and escalation. A scenario asking for paging responders and following a response plan is not solved merely by creating an OpsItem; a scenario asking which resources comprise an application does not need an incident platform.

## Security, observability and cost boundaries

Use IAM conditions on resource tags, document names and session ownership to limit operators to approved nodes and actions, and prevent ordinary users from editing the document they are then allowed to execute. Keep custom documents under change control, pin a reviewed version where it matters and restrict `iam:PassRole` to the exact automation roles. An operator who can start an unrestricted shell holds full operating-system access whatever the policy says, so authorization must track the node's data sensitivity.

The private network path is a list of endpoint names. A node in a private subnet with no internet route needs three interface VPC endpoints: `com.amazonaws.region.ssm` for the service API, `com.amazonaws.region.ssmmessages` for the agent data channel that Session Manager and Run Command ride on, and `com.amazonaws.region.ec2messages`, the older delivery path still used by agents before version 3.3.40.0. It also needs a path to S3, either `com.amazonaws.region.s3` or the S3 gateway endpoint, because the agent updates itself over S3, patch operations read AWS managed patch buckets, and command output, scripts and session transcripts land in buckets. Add `com.amazonaws.region.logs` for CloudWatch Logs destinations, `com.amazonaws.region.kms` when those use a customer managed key, and `com.amazonaws.region.ec2` for VSS-enabled snapshots. Endpoint security groups allow inbound HTTPS on 443 from the node subnets; the node still initiates every connection. Session Manager removes inbound administration ports, not the outbound connectivity, agent health, DNS and IAM dependencies.

Monitor command, association, patch and automation status rather than treating API acceptance as successful execution. Route failures through EventBridge or CloudWatch and use CloudTrail for control-plane attribution. Watch for secrets in command text, document parameters and output, which several observability paths retain: use **AWS Secrets Manager**, the managed secret lifecycle service, or Parameter Store references instead of embedded credentials.

Output access is its own permission boundary. An operator who cannot start a privileged document can still read credentials or customer data out of command output, session logs or an automation execution, so apply least privilege to the S3 prefix, log group, execution history and encryption key.

**Parameter Store** is Systems Manager's hierarchical store for configuration values and secrets, with versioning, advanced-parameter policies and optional KMS encryption for `SecureString` values. It is taught fully in the Secrets Manager unit; here, remember the integration boundary: a runbook or command resolves a parameter at execution, while Secrets Manager is the answer when the requirement includes managed rotation.

Systems Manager pricing varies by capability, and the shape changed in 2026. On EC2 instances, Session Manager, Run Command, State Manager and Patch Manager carry no additional Systems Manager charge. Hybrid and multicloud nodes no longer need a paid tier: the advanced-instances tier was removed effective June 30, 2026, the 1,000-instance account limit on hybrid nodes is gone, and registration costs nothing per node. In exchange, from September 30, 2026 Session Manager and Run Command on those nodes are billed per use, at $0.05 per session and $0.002 per invocation; the June to September window is explicitly unbilled. Automation carries no free allowance: every step is charged from the first, at $0.002 per step per resource, and each `aws:executeScript` step adds $0.00003 per second of runtime. OpsCenter costs $2.97 per 1,000 OpsItems plus $0.039 per 1,000 read and update API requests. Parameter Store standard parameters are free and advanced ones cost $0.05 each per month, and CloudWatch Logs, S3, KMS and endpoints add their own costs.

## Professional depth

At organization scale, configure Systems Manager through Quick Setup from a delegated administration account, using organization or organizational-unit targets for patch policies and host management, then verifying the generated associations and compliance in each Region. Account membership does not fix an unhealthy SSM Agent or a missing network path, so keep unmanaged and offline nodes as an explicit exception queue.

Separate platform documents from workload targeting. A central team owns hardened session preferences, patch baselines and reviewed Automation runbooks, while application teams select approved maintenance groups through controlled tags. Protect target-tag mutation with IAM conditions and, where necessary, service control policies, and standardize keys and values with tag policies. Changing a target tag can be equivalent to enrolling a production database host in an install wave.

For hybrid fleets, create activations per trust and lifecycle boundary and let unused ones expire rather than sharing one registration bundle broadly. Decide how nodes reach Systems Manager and patch repositories during a data-center link failure: a private Direct Connect path with interface endpoints may be preferred, but recovery needs an alternate management path when that connection is the incident.

## Worked scenario

A retailer operates 1,800 Linux and Windows EC2 instances across 30 accounts and 12 on-premises servers. No node may expose SSH or RDP. Security wants daily compliance scans, production installation during a Sunday window after a canary wave, central evidence and approval before emergency database-host changes. The retailer is a new customer in September 2026.

The platform team enables Default Host Management Configuration for EC2, registers the on-premises machines with scoped hybrid activations, and supplies private connectivity through the ssm, ssmmessages and ec2messages endpoints plus an S3 path. Session Manager provides interactive access with native-shell logs sent to encrypted CloudWatch Logs. A Quick Setup patch policy targets organizational units for daily scans, and production installation uses approved baselines, canary tags and a maintenance window with conservative concurrency and cutoff. Automation runbooks verify state and perform the change; an EventBridge rule starts a recovery runbook when a patch task fails, and a Config rule with automatic remediation reverts any security group that reopens RDP. Because Change Manager and Incident Manager are closed to new customers, the retailer integrates an approved current change and incident platform rather than enabling those tools. Parameter Store holds non-rotating configuration and Secrets Manager supplies rotating credentials.

The exam asks which design removes inbound administration, patches new accounts consistently, limits blast radius and preserves operational evidence. The keyed answer is the managed-node prerequisites plus Session Manager, an organization-targeted patch policy, canary and maintenance-window execution, and least-privilege Automation runbooks with monitored output.

## Exam lens

- "Interactive shell without port 22, a bastion or SSH keys" maps to Session Manager; the node still needs SSM Agent, permissions and outbound connectivity.
- "Run one approved command now across tagged instances" maps to Run Command with concurrency and error thresholds.
- "Keep a required configuration present over time" maps to a State Manager association; Run Command is the one-time distractor.
- "Collect installed application and operating-system metadata" maps to Inventory; Inspector is the vulnerability-finding service.
- "Define which operating-system patches are approved" maps to a patch baseline; a maintenance window defines when work may start.
- "Apply one patch configuration across accounts and Regions" maps to a Quick Setup patch policy.
- "Coordinate patching with other ordered tasks in a Sunday period" maps to a maintenance window.
- "No task may begin during the last hour of the window" maps to a cutoff of 1; cutoff never stops a task already running.
- "Install the patch but do not restart the host" maps to `NoReboot`, which leaves the patch `InstalledPendingReboot` and the node `Non-Compliant`.
- "Multi-step workflow with API calls, branches and approval" maps to Automation; keep the execution role distinct from permission to start it.
- "Nothing may run unless it falls inside an approved change event" maps to a `DEFAULT_CLOSED` Change Calendar; a release freeze is `DEFAULT_OPEN` with blackout events.
- "Automatically fix a resource as soon as it is evaluated noncompliant" maps to an AWS Config rule with an automatic remediation action running an SSM Automation document.
- "Start a runbook when a specific AWS event occurs" maps to an EventBridge rule with the runbook as its target; a Lambda function calling `StartAutomationExecution` is the custom-build distractor.
- "Run one remediation across every account in an organizational unit" maps to a multi-account, multi-Region automation from a delegated administrator, with the execution role present under the same name in every target account.
- "Operational issue with related resources and a remediation runbook" maps to an OpsCenter OpsItem.
- "New customer requests Change Manager or Incident Manager" maps to a supported partner or documented alternative because both closed on November 7, 2025.
- "New account requests Application Manager" maps to tags and Resource Groups, Resource Explorer or CloudWatch Application Signals because access closed July 30, 2026.
- "Manage an on-premises server" maps to a hybrid activation plus SSM Agent, permissions and reachability.
- "Private subnet with no internet route and no NAT gateway" maps to the `ssm`, `ssmmessages` and `ec2messages` interface endpoints plus an S3 path.
- "Automatically rotate a database password" maps to Secrets Manager, not Parameter Store.

## Knowledge check

### 1. Removing inbound administrative access (Associate)

A financial services company runs its application servers on Amazon EC2 instances in private subnets. Administrators need to open interactive shells on those instances to troubleshoot incidents. The security team will not approve any inbound SSH rule in the security groups and will not approve bastion hosts in the account. Every administrative session must be attributable to a named principal through AWS CloudTrail.

Which solution will meet these requirements?

- **A)** Run a State Manager association every time an administrator needs a shell.
- **B)** Configure the instances as managed nodes and grant scoped Session Manager access.
- **C)** Use Inventory to collect each administrator's terminal input.
- **D)** Create a maintenance window that opens port 22 temporarily.

<details><summary>Answer</summary>

**Answer: B.** Session Manager provides interactive access over the managed-node outbound path without an inbound port or bastion, and CloudTrail records its control-plane session APIs. A enforces scheduled desired state and is not an interactive shell. C collects node metadata and does not provide access or terminal auditing. D introduces the forbidden inbound SSH exposure and a maintenance window does not modify a security group unless a task is built to do so.

*Where this is covered: Choose Session Manager, Run Command or State Manager.*

</details>

### 2. Running a fleet repair safely (Associate)

A retail company must run an approved diagnostic command one time on every web node tagged `Environment=Production`. All of those nodes are already registered as Systems Manager managed nodes. The rollout must stop expanding automatically once failures cross the threshold the operations team sets, so that a bad command cannot reach the whole fleet. The complete output of every invocation must be retained for a later review, because the truncated console response is not enough evidence.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Use Run Command with the tag as its target and configure concurrency and an error threshold.
- **B)** Use Session Manager and ask each administrator to run the command manually.
- **C)** Create an Inventory association and treat collected package names as command output.
- **D)** Send Run Command output to S3 or CloudWatch Logs with appropriate retention.
- **E)** Use Application Manager to install the diagnostic command on every resource it displays.

<details><summary>Answer</summary>

**Answer: A and D.** A provides one-time, tag-targeted fleet execution with blast-radius controls, and D retains output beyond the bounded console response. B is manual and loses consistent fleet control. C collects metadata rather than executing and retaining the diagnostic. E is an application view, is not a command executor and is closed to new customers.

*Where this is covered: Choose Session Manager, Run Command or State Manager.*

</details>

### 3. Maintaining an agent configuration (Associate)

A media company requires a monitoring agent to stay installed and correctly configured on every EC2 instance that carries its workload tag. The fleet changes every week, and instances launched next month must be covered without an engineer remembering to act on them. The compliance team wants a scheduled report showing which nodes currently match the desired configuration and which have drifted. The company does not want to build and operate its own scheduler or maintain a list of instance IDs.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Open Fleet Manager and preview the agent's configuration file on each instance.
- **B)** Run the installation command once with Run Command against today's instance IDs.
- **C)** Create a State Manager association that targets the workload tag and applies the configuration document on a schedule.
- **D)** Create an Incident Manager response plan that engages an on-call engineer whenever the agent drifts.

<details><summary>Answer</summary>

**Answer: C.** A State Manager association binds a document to dynamic tag targets, reapplies or checks the desired state on a schedule, and reports association compliance, which is the drift report the stem asks for. A shows one file on one node and enforces nothing. B covers today's instance IDs only, so next month's launches are missed, and it does not reapply the configuration. D engages people after the fact instead of maintaining the configuration, and it adds the on-call overhead the stem wants avoided.

*Where this is covered: Choose Session Manager, Run Command or State Manager.*

</details>

### 4. Patching a growing organization (Professional)

A company runs managed nodes in 25 workload accounts in one AWS Organizations organization and expects to add more accounts every quarter. Security requires a patch-compliance scan every day in every workload account, while installation on production nodes may happen only during the Sunday maintenance period. The platform team must control which updates are approved and which are rejected rather than accepting whatever a vendor publishes. Installation must reach a tagged canary group first, and a wave that starts failing must not propagate to the rest of the fleet.

Which combination of steps will meet these requirements? (Select THREE.)

- **A)** Use Amazon Inspector findings as the mechanism that installs each approved operating-system update.
- **B)** Create a patch policy in Quick Setup that targets the required organizational units and Regions.
- **C)** Use Run Command to run `AWS-RunPatchBaseline` as an install operation in each account every day.
- **D)** Create custom patch baselines that define the approved and rejected updates for each operating system.
- **E)** Target a tagged canary group first and schedule installation with concurrency and error thresholds.

<details><summary>Answer</summary>

**Answer: B, D and E.** B distributes the scan and install configuration to organizational units so accounts added next quarter inherit it, D gives the platform team control over approvals and rejections, and E stages the rollout and stops a failing wave. A adds CVE severity and exposure context but Amazon Inspector does not install operating-system patches. C uses a real document for the wrong job: Run Command is a one-time invocation against the targets of one account at the moment it runs, so all 25 accounts and every account added next quarter need their own invocation, and a daily install ignores the rule that production nodes may be patched only during the Sunday period.

*Where this is covered: Patch Manager and patch policies.*

</details>

### 5. Scheduling a multi-step operational change (Associate)

A healthcare company has a documented runbook that stops an application, calls an AWS API to take its nodes out of service, patches those nodes, waits for a health check to pass and then starts the application again. The team wants this runbook to run on a recurring schedule inside an approved four-hour change period every month. No task may start during the final hour of that period, although a task already running when the period ends is allowed to finish. The company wants Systems Manager to enforce both the sequence and the schedule.

Which solution will meet these requirements?

- **A)** Store the steps in Inventory and query their compliance.
- **B)** Use Session Manager port forwarding as the workflow engine.
- **C)** Put the commands in a Parameter Store `SecureString` and schedule the parameter.
- **D)** Use an Automation runbook as a Maintenance Window task and configure the window cutoff.

<details><summary>Answer</summary>

**Answer: D.** Automation represents the multi-step API and node workflow, and the maintenance window supplies the monthly schedule plus a cutoff of 1, which stops any new task from starting after the end time minus one hour. Cutoff never terminates a task already running, which is exactly the behavior the stem asks for. A collects metadata and cannot execute the workflow. B is an interactive tunnel, not an orchestrator. C stores a value but neither schedules nor executes operational steps.

*Where this is covered: Automation, maintenance windows and change control.*

</details>

### 6. Change approval for a new customer (Associate)

It is September 2026. A manufacturing company has just opened its first AWS accounts and has never used any AWS Systems Manager capability. It wants an enterprise change-management system that handles change requests, approver workflows, reporting and integration with its existing service-management process. An architect must recommend what the company should adopt now.

Which solution will meet these requirements?

- **A)** Adopt an AWS Partner Network enterprise change-management product and keep using Systems Manager Automation runbooks to perform the approved changes.
- **B)** Enable Change Manager from a delegated administrator account and build change templates and approval workflows there.
- **C)** Create a `DEFAULT_CLOSED` Change Calendar and record each change request as a calendar event.
- **D)** Create a State Manager association for each change request and use its compliance report as the approval record.

<details><summary>Answer</summary>

**Answer: A.** A capability that is closed to new customers is simply unavailable to a company opening its first accounts, however well it fits the requirement, so the enterprise change-management system has to come from a partner product while Automation still performs the approved changes inside AWS. B is the near miss: a delegated administrator is how an established customer coordinates Change Manager across accounts and Regions, but a company that has never used it cannot enable it. C gives an open or closed state that Automation, Maintenance Windows and State Manager can check before acting, which gates execution but supplies no change requests, approver workflow or reporting. D keeps node configuration at a desired state and reports association compliance, which is drift evidence rather than an approval record.

*Where this is covered: Automation, maintenance windows and change control.*

</details>

### 7. Governing operations across accounts (Professional)

A platform team manages nodes in 40 accounts in one AWS Organizations organization. It wants patch configuration defined centrally and applied to organizational units so that new accounts inherit it as they join, while application teams keep the ability to run a bounded set of approved runbooks in their own accounts. A review found two gaps: an application engineer could add a tag to a production database node and pull it into a target group whose automation restarts services, and engineers could pass any IAM role to an Automation execution. The team must close both gaps without taking automation away from the application teams. It also needs to know which nodes are genuinely reachable and managed rather than merely present in an account.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Configure the patch scan and install settings separately in each of the 40 accounts with Quick Setup.
- **B)** Deploy patch policies to organization or organizational-unit targets through Quick Setup.
- **C)** Use one shared hybrid activation code with no expiration for all current and future machines.
- **D)** Restrict document versions, `iam:PassRole` and target-tag mutation through IAM and governance policies.
- **E)** Open a Session Manager session to each node in turn to confirm that it is reachable and managed.

<details><summary>Answer</summary>

**Answer: B and D.** B centrally deploys the patch configuration to changing organization targets, and D keeps approved automation and enrollment boundaries from being bypassed. A applies the same tool one account at a time, which covers the 40 accounts that exist today but leaves every account joining later with no patch configuration until someone repeats the work by hand. C creates a long-lived credential and trust-boundary problem. E proves that one node answered at one moment and is 40 accounts of manual effort, while connection status and last ping already report offline nodes and the expected machines that never registered at all.

*Where this is covered: Professional depth.*

</details>

### 8. Operating a hybrid production fleet (Professional)

A logistics company is bringing 300 on-premises servers in its own data centers under Systems Manager management and will use Automation to make production changes on them. Its security standard forbids management traffic over the public internet and forbids opening inbound ports on those servers, so all traffic must use the existing private network path to the Systems Manager endpoints and to the protected log destinations. Every execution must leave retained, reviewable output. Registration credentials must be scoped and must expire rather than being reused indefinitely across current and future machines. When the first canary reports an application-health failure, the change must stop and move to controlled recovery instead of continuing.

Which combination of steps will meet these requirements? (Select THREE.)

- **A)** Register the servers with scoped, expiring hybrid activations and install SSM Agent.
- **B)** Use Patch Manager scan operations to confirm that each production change succeeded and to roll it back when it did not.
- **C)** Provide outbound access to Systems Manager endpoints and protected log destinations through the approved private network path.
- **D)** Create an OpsCenter OpsItem when a canary reports an application-health failure and treat that OpsItem as the mechanism that halts the remaining waves.
- **E)** Use reviewed, idempotent Automation documents with conservative concurrency, error thresholds and retained output.

<details><summary>Answer</summary>

**Answer: A, C and E.** A establishes managed-node identity without reusing an unlimited activation, C supplies the node-initiated private service and evidence paths, and E makes the change controlled, repeat-safe and auditable. B reports missing, installed and failed operating-system patch states, which is not evidence that an application-level change succeeded, and Patch Manager has no rollback of any kind: application-level recovery belongs to the runbook author. D collects the failure as a work item with its affected resource and an attached runbook, which organizes the diagnosis but stops nothing already in flight; the error threshold on the automation is what ends the remaining waves.

*Where this is covered: Professional depth.*

</details>

## Summary

Start by making each machine a managed node with SSM Agent, IAM permissions and outbound endpoint connectivity; hybrid machines add an activation. Use Fleet Manager to view nodes and Inventory to collect metadata. Session Manager supplies interactive access without inbound administration ports, Run Command executes a one-time fleet action, and State Manager maintains desired configuration. Patch baselines decide which updates are approved, patch policies distribute recurring scan and install configuration, and maintenance windows coordinate timed work. Automation handles multi-step runbooks, while Change Calendar gates execution around business events. OpsCenter organizes operational issues. Change Manager and Incident Manager remain exam answers for established customers but closed to new customers on November 7, 2025; Application Manager closed on July 30, 2026. At scale, target organizational units and controlled tags, protect document and `iam:PassRole` permissions, canary every disruptive operation, monitor application health as well as command status, and retain output without exposing secrets. Parameter Store supplies hierarchical configuration; use Secrets Manager when managed rotation decides the answer.

## Related units

- [Amazon CloudWatch](cloudwatch.md): alarms, log retention and application health gates for operations
- [AWS CloudTrail](cloudtrail.md): attribution for session, command, automation and configuration APIs
- [AWS Config and detection services](../07-security/detection-and-compliance-services.md): configuration compliance and Systems Manager remediation runbooks
- [AWS Secrets Manager and Parameter Store](../07-security/secrets-manager-and-parameter-store.md): full selection rules for configuration and rotating secrets
- [AWS Organizations, IAM Identity Center and AWS Control Tower](../07-security/organizations-identity-center-and-control-tower.md): delegated administration and organization targeting
- [Hybrid connectivity](../04-networking/hybrid-connectivity.md): Direct Connect and VPN paths for managed on-premises nodes
- [Amazon EventBridge](../06-integration/eventbridge.md): routing operational failures and changes to workflows

## Sources

- [What is AWS Systems Manager?](https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html): managed nodes and the Systems Manager tool groups
- [Setting up managed nodes](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-setting-up-nodes.html): agent, permission and connectivity prerequisites
- [Default Host Management Configuration](https://docs.aws.amazon.com/systems-manager/latest/userguide/managed-instances-default-host-management.html): account and Region default instance permissions
- [Creating a hybrid activation](https://docs.aws.amazon.com/systems-manager/latest/userguide/activations.html): activation code, ID, role, expiry and registration
- [AWS Systems Manager Fleet Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/fleet.html): fleet console and supported node administration
- [AWS Systems Manager Inventory](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-inventory.html): collected metadata and associations
- [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html): interactive access without inbound ports or bastions
- [Logging session activity](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-logging.html): CloudWatch Logs, S3 and encrypted-tunnel limitations
- [AWS Systems Manager Run Command](https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command.html): documents, fleet targets, concurrency and output
- [AWS Systems Manager State Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-state.html): associations, schedules and compliance
- [AWS Systems Manager Patch Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager.html): scanning, installation and managed-node patching
- [Patch baselines](https://docs.aws.amazon.com/systems-manager/latest/userguide/about-patch-baselines.html): approval rules, rejected patches and patch groups
- [Patch policies in Quick Setup](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager-policies.html): multi-account and multi-Region patch configuration
- [AWS-RunPatchBaseline](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager-aws-runpatchbaseline.html): scan and install operation behavior
- [Systems Manager Automation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html): multi-step runbooks, actions and service roles
- [Systems Manager Maintenance Windows](https://docs.aws.amazon.com/systems-manager/latest/userguide/maintenance-windows.html): schedules, duration, cutoff, targets and task types
- [Systems Manager Change Calendar](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-change-calendar.html): open and closed calendar states for automation
- [Change Manager availability change](https://docs.aws.amazon.com/systems-manager/latest/userguide/change-manager-availability-change.html): November 7, 2025 closure and partner guidance
- [AWS Systems Manager OpsCenter](https://docs.aws.amazon.com/systems-manager/latest/userguide/OpsCenter.html): OpsItems, operational data and remediation
- [Application Manager availability change](https://docs.aws.amazon.com/systems-manager/latest/userguide/application-manager-availability-change.html): July 30, 2026 closure, maintenance mode and alternatives
- [What is Incident Manager?](https://docs.aws.amazon.com/incident-manager/latest/userguide/what-is-incident-manager.html): response plans, contacts, escalation and incidents
- [Incident Manager availability change](https://docs.aws.amazon.com/incident-manager/latest/userguide/incident-manager-availability-change.html): November 7, 2025 closure and existing-customer support
- [VPC endpoints for Systems Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-create-vpc.html): private node-to-service connectivity
- [Restricting Session Manager access](https://docs.aws.amazon.com/systems-manager/latest/userguide/getting-started-restrict-access-quickstart.html): tag, document and session IAM controls
- [AWS Systems Manager pricing](https://aws.amazon.com/systems-manager/pricing/): capability-specific and connected-service billing dimensions
