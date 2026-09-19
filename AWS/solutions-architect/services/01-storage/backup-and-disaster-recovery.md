# AWS Backup and disaster recovery

**Where it sits on the exams.** **AWS Backup** is the managed service that centralizes backup scheduling, retention, copying and auditing across AWS services, and disaster recovery (DR) is the wider discipline of preparing for and recovering from an event that stops a workload running where it normally runs. Together they carry SAA-C03 tasks 1.3, 2.2, 4.1, 4.2 and 4.3, and SAP-C02 tasks 1.3, 2.2, 2.4, 3.1, 3.2 and 3.4, which makes this the single busiest topic in the reliability half of both exams. The rule of thumb the exam wants is that the recovery time objective and the recovery point objective in the stem choose the strategy, not the other way round: hours of downtime means backup and restore, tens of minutes means pilot light, minutes means warm standby, and near zero means multi-site active-active, and every one of them costs more than the one before it.

## Recovery objectives: RTO, RPO and workload tiers

Two numbers drive every DR decision on both exams. The recovery time objective (RTO) is, in AWS's wording, the maximum acceptable delay between the interruption of service and the restoration of service. The recovery point objective (RPO) is the maximum acceptable time after the last data recovery point, which in practice is the amount of data you are willing to lose measured as a span of time. RTO is downtime and RPO is data loss, and they are set independently: a payroll system might tolerate four hours of downtime but no more than one minute of lost transactions, while a reporting warehouse might tolerate a day of lost data but need to be readable within an hour.

Neither number is a technical choice. AWS's guidance is to build a matrix of workload tiers by business impact, for example critical, high, medium and low, assign an RTO and RPO to each tier, and assign each workload to a tier. The questions that set the tier are about impact, not architecture: how long the workload can be unavailable before the business is unacceptably harmed, how much data can be lost, whether lost data can be recreated from another source, what the objectives of the workloads this one depends on are, and whether legal or contractual penalties attach. A dependency is the trap: your RTO cannot be better than the RTO of the downstream systems you need, so an application with a fifteen minute RTO that calls a partner service with a four hour RTO does not have a fifteen minute RTO.

AWS names the anti-patterns explicitly, and exam questions are built out of them: choosing objectives arbitrarily, choosing objectives too lenient to meet the business need, choosing objectives more stringent than the business requires, and choosing unrealistic objectives such as zero downtime and zero data loss. The third is the one Associate candidates get wrong, because an over-tight objective forces a costlier and more complex implementation than the workload needs. When a stem describes a non-production or development workload and then asks for the "MOST cost-effective" answer, the key is a cheaper strategy with a looser objective, and the distractor is the multi-Region design that would be right for production. Objectives also vary by event type, so ask whether the RTO differs for an Availability Zone impairment and a full Region impairment. That is why a mature plan has one strategy for zonal failure, usually a Multi-AZ deployment that recovers automatically, and a slower one for Regional failure.

## Availability Zones, Regions and the four disaster recovery strategies

The AWS global infrastructure gives you two nested failure boundaries, and choosing between them is the first architectural decision in any DR design. An Availability Zone is one or more discrete data centers with independent power, cooling and physical security inside a Region. Spreading a workload across zones protects against fires, floods and major power outages, and because the zones are close together it can do so with synchronous replication and therefore an RPO of zero. A Region is a fully independent grouping of zones with its own control planes, deliberately isolated so that a problem in one does not propagate, which makes the Region the unit of DR when a disaster means more than the loss of a data center or when a regulator requires it.

The trade-off is that cross-Region replication is asynchronous, so a cross-Region design almost always has an RPO greater than zero. A residency constraint decides some questions outright: if data must stay inside a country that has only one AWS Region, multi-Region is unavailable and a Multi-AZ design plus cross-Region backups is the strongest answer. AWS makes one further point that Professional questions test directly. Services divide into a data plane, which serves real-time traffic, and a control plane, which configures the environment. Control planes have lower availability design goals, so a failover depending on a control plane API in the Region that just failed is not reliable. Prefer data plane operations in the recovery path.

AWS defines four multi-Region strategies, listed in increasing order of cost and complexity and decreasing order of RTO and RPO. Read the following table by starting from the objective in the question stem and working left: the band that contains the stated objective names the strategy, and the last column gives the wording that usually signals it.

| Strategy | RPO and RTO AWS documents | What runs in the recovery Region | Relative cost | Wording that selects it |
|---|---|---|---|---|
| Backup and restore | RPO in hours, RTO in 24 hours or less; point-in-time recovery can lower RPO to as little as 5 minutes | Stored backups only, plus the templates and images needed to rebuild | Lowest | "lowest cost", "we can tolerate a day", non-production or archival workloads |
| Pilot light | RPO in minutes, RTO in tens of minutes | Data stores replicated and always on; application servers defined but switched off | Low | "core infrastructure ready", "we cannot wait to restore a database", "minimize standing cost but recover quickly" |
| Warm standby | RPO in seconds, RTO in minutes | A scaled-down but fully functional copy of the workload, always running and serving traffic immediately | High | "must handle traffic immediately at reduced capacity", "scale up after failover" |
| Multi-site active-active | RPO near zero, RTO potentially zero | The full workload, serving live traffic from every Region | Highest | "no downtime", "serve users from the nearest Region", "both Regions active" |

The distinction the exam tests most often is between pilot light and warm standby, and AWS states it in one sentence: pilot light cannot process requests without additional action being taken first, whereas warm standby can handle traffic at reduced capacity immediately. Pilot light requires turning on servers, possibly deploying non-core infrastructure, then scaling up; warm standby requires only the scaling up. A warm standby deployed at full production capacity is called hot standby, which removes the dependency on scaling during recovery and is what AWS calls a statically stable configuration.

Two further points round the model out. In a multi-site active-active design there is no failover event at all; recovery means evacuating the failed Region, so DR testing asks whether traffic really moves and whether the survivors have capacity to take it. And no strategy, active-active included, protects against data corruption, accidental deletion or a malicious insider on its own, because replication faithfully copies a bad write. Only point-in-time backups, versioning and retention controls give you a recovery point before the damage, which is why every strategy in the table still needs backups underneath it.

Rerouting traffic on failover is owned by a different unit. **Amazon Route 53**, the AWS authoritative Domain Name System service, provides health checks and failover, latency and weighted routing records, and **Amazon Application Recovery Controller (ARC)**, formerly Route 53 Application Recovery Controller, provides routing controls, which are on and off switches on a dedicated multi-Region data plane, plus zonal shift for moving traffic away from an impaired Availability Zone. Both are taught in [Amazon Route 53](../04-networking/route53.md). Carry one point from here: changing a weighted record is a control plane operation and therefore less resilient than flipping an ARC routing control, which is on the data plane.

## How each data service supports cross-Region recovery

Compute is easy to recreate from an image and a template. Data is not, so the strategy you can actually achieve is bounded by the replication and copy mechanism of every data store in the workload. Read the following table by finding each data store your scenario names, then taking the weakest RPO in the list as the RPO of the whole workload. The last column names the unit that teaches the mechanism in full, because this unit deliberately does not repeat them.

| Data service | Cross-Region mechanism | What it gives you | Taught in |
|---|---|---|---|
| **Amazon S3**, the object storage service | S3 Replication in its Cross-Region form, asynchronous and continuous, with S3 Replication Time Control for a time-bound service level agreement and S3 Batch Replication for existing objects | Near-continuous RPO for new writes; delete markers replicate only if you opt in, and a permanent version delete never replicates | [Amazon S3](s3.md) |
| **Amazon RDS**, the managed relational database service | Cross-Region read replicas, cross-Region automated backup replication of snapshots and transaction logs, and cross-Region snapshot copy | Replicas give minutes of RPO and a promotion taking a few minutes including a reboot; replicated automated backups give point-in-time restore in the second Region | [Amazon RDS](../05-database/rds.md) |
| **Amazon Aurora**, the MySQL and PostgreSQL compatible database with a distributed storage layer | Aurora Global Database, one primary cluster and up to 10 read-only secondary Regions replicated through dedicated storage-layer infrastructure | Typical replication latency under a second; switchover for planned moves with no data loss, managed failover for an outage, and write forwarding from secondaries | [Amazon Aurora](../05-database/aurora.md) |
| **Amazon DynamoDB**, the managed key-value and document database | Global tables, in multi-Region eventual consistency mode across any number of Regions in the partition, or multi-Region strong consistency mode across exactly three | Eventual mode replicates typically within a second with last-writer-wins conflict resolution and an RPO equal to the lag; strong mode supports an RPO of zero | [Amazon DynamoDB](../05-database/dynamodb.md) |
| **Amazon EBS**, the block storage service for EC2 instances | Snapshot copy to another Region or account, scheduled through AWS Backup or Data Lifecycle Manager | Point-in-time copies only, so RPO equals the snapshot interval; the first copy into a Region is full, and later copies are incremental only if an earlier copy survives and uses the same key | [Amazon EBS](ebs.md) |
| **Amazon EFS**, the elastic NFS file system | EFS replication to a destination file system in the same or another Region, plus AWS Backup copy | A documented RPO of 15 minutes for most file systems, with a read-only destination you fail over to and can later fail back from | [Amazon EFS](efs.md) |
| **Amazon FSx**, the family of managed file systems | For FSx for NetApp ONTAP, NetApp SnapMirror volume replication in Region or across Regions, schedulable as often as every 5 minutes. For FSx for OpenZFS, native snapshot replication across Regions and accounts on demand or on a schedule. For FSx for Windows File Server and Lustre, AWS Backup cross-Region and cross-account copy | SnapMirror gives a live second file system with an RPO set by the schedule; backup copy gives point-in-time copies, so RPO equals the backup interval | [Amazon FSx](fsx.md) |

Two readings decide questions. First, snapshot copying gives an RPO no better than the interval between snapshots, while continuous replication gives an RPO in seconds, so a stem demanding a five minute RPO for an EC2-backed database on EBS volumes cannot be answered with hourly snapshot copies. Second, a live replica is not a backup: Aurora Global Database, DynamoDB global tables and S3 Cross-Region Replication all propagate a bad write, so AWS's guidance for pilot light, warm standby and active-active alike is to keep point-in-time backups in the recovery Region as well.

The compute half of the recovery is simpler but is where RTO is usually lost. AWS's position is that infrastructure should be redeployed from infrastructure as code, using **AWS CloudFormation**, the AWS templating and stack service, so the recovery Region rebuilds quickly and identically; without it the RTO in the plan will not be the RTO you achieve. Back up the Amazon Machine Images that **Amazon EC2**, the AWS virtual server service, launches from and copy them to the recovery Region, and use **Amazon EC2 Auto Scaling**, the service that keeps a fleet at the right size, to scale a pilot light or warm standby up to production capacity, remembering that auto scaling is a control plane activity and therefore a dependency in the recovery path. Confirm that service quotas in the recovery Region allow the scale-up before you need it.

## AWS Backup: plans, rules, vaults and the resources it protects

AWS Backup replaces per-service scripting with one console, one set of APIs and one policy model. You define a backup plan, a container for one or more backup rules; each rule names a schedule, a backup window, a lifecycle, a destination vault and optional copy actions; and you assign resources by listing their ARNs or, far more commonly, by tag. Tag-based assignment is the answer whenever a question asks how newly created resources get protected without anybody remembering to add them, because a resource joins the plan the moment it is tagged.

The schedule is the RPO control. The console offers hourly, every 12 hours, daily, weekly or monthly, and a cron expression or the CLI can schedule as often as hourly. For resources that support it you can instead tick continuous backups, which enables point-in-time restore rather than discrete snapshots and cannot take a cron expression because it records changes continuously. The backup window has two parts that trip people up: a start window, within which the job must begin, and a completion window, within which it must finish, defaulting in the console to 12:30 AM local time, start within 8 hours and complete within 7 days. A job sits in `CREATED` status until it starts or the start window expires, at which point it becomes `EXPIRED`. If two rules have overlapping start windows, AWS Backup takes one backup and keeps it under the rule with the longer retention.

Retention is the lifecycle. Snapshot retention runs from 1 day to 100 years, or is left unset to retain indefinitely; continuous backup retention is limited to 1 to 35 days. Every backup is created in warm storage, and supported resource types can transition to a lower-cost cold tier. The rule to memorize is that a backup moved to cold storage must stay there for a minimum of 90 days on top of its time in warm storage, which is why AWS Backup requires the total retention period to be at least 90 days greater than the transition setting, and why the transition setting cannot be changed after a backup has moved. AWS recommends at least 8 days in warm storage first, because incremental backups need a warm full backup to reference. Cold storage covers a short list of types including Amazon EFS, Amazon EBS through EBS Snapshot Archive, CloudFormation stacks, SAP HANA on EC2, **Amazon Timestream** for LiveAnalytics, the time series database, and VMware virtual machines.

A backup vault is the container backups land in, and it is more than a folder. The vault sets the **AWS Key Management Service (AWS KMS)** key, the managed service for creating and controlling encryption keys, that encrypts the backups it holds, and it carries a resource-based access policy naming which principals may act on them. That separation is the point: the vault retains EC2 and EBS backups according to their lifecycle even after the source instance and volumes are deleted, and a least-privilege vault policy means the identity that can delete a production database is not the identity that can delete its backups. Resource types under what AWS calls full AWS Backup management go further, encrypting with the vault's own key rather than the source resource's key and carrying an `arn:aws:backup` ARN you can write policies against independently.

Knowing what AWS Backup can protect is worth a question on its own. It covers Amazon EC2 instances backed by EBS volumes, Amazon EBS volumes, Amazon S3 data, Amazon DynamoDB tables, Amazon RDS instances including Multi-AZ instance deployments and Multi-AZ DB clusters, though point-in-time recovery excludes the clusters, Amazon Aurora and Aurora DSQL clusters, Amazon EFS file systems, all four Amazon FSx file system types, Volume Gateway volumes from **AWS Storage Gateway**, the hybrid storage service, clusters from **Amazon DocumentDB** and **Amazon Neptune**, the managed document and graph databases, clusters and Serverless namespaces from **Amazon Redshift**, the data warehouse, Amazon Timestream for LiveAnalytics tables, AWS CloudFormation stacks, SAP HANA on EC2, clusters and their persistent storage from **Amazon Elastic Kubernetes Service (Amazon EKS)**, the managed Kubernetes service, and VMware virtual machines. The boundary that matters is the other direction: AWS Backup does not govern backups taken outside AWS Backup, so a question asking how to get one auditable view of protection across an estate of per-service snapshot scripts is asking you to move those workloads onto backup plans.

## Vault Lock and logically air-gapped vaults

A backup that a compromised administrator can delete is not protection against ransomware, and AWS Backup has two features aimed squarely at that. The first is **AWS Backup Vault Lock**, an optional configuration on a vault that enforces a write-once-read-many model: while a lock is in force, any attempt to delete a recovery point or change its lifecycle properties is denied, including attempts by the account root user. A vault can carry one lock, and the lock can optionally set a minimum retention period and a maximum retention period, from 1 day up to 36,500 days. Those two values are admission controls rather than retroactive changes: new backup and copy jobs whose retention falls outside the range fail, while recovery points already in the vault keep the lifecycle they were created with.

The lock has two modes, and the difference between them is the exam question. Governance mode can be removed by any principal with sufficient IAM permissions, so it stops accidents and unauthorized users but keeps an administrative escape hatch. Compliance mode cannot. When you create a compliance mode lock you set a cooling-off period, called grace time, of at least 3 days, expressed through the `ChangeableForDays` parameter; during grace time you can still change or delete the lock, and after it expires the vault and its lock are immutable and cannot be altered or deleted by any user or by AWS while the vault holds recovery points. The API behavior is a clean way to remember it: `PutBackupVaultLockConfiguration` creates a governance mode lock if you omit `ChangeableForDays` and a compliance mode lock if you include it.

```bash
aws backup put-backup-vault-lock-configuration \
  --backup-vault-name finance-vault \
  --changeable-for-days 3 \
  --min-retention-days 2557 \
  --max-retention-days 2557
```

Compliance mode has a cost consequence AWS warns about directly: backups in a locked vault cannot be deleted until their lifecycle completes, so a recovery point created with a retention of "always" before the grace time expired is retained and charged forever. One narrow escape remains, in that closing the AWS account suspends it for 90 days with backups intact and then deletes the vault contents even though the lock was in place. Note also that AWS Backup Vault Lock is not the same feature as S3 Glacier Vault Lock, and that it has been assessed by a third party for use under SEC 17a-4, CFTC and FINRA regulations, which is why a stem quoting one of those points at compliance mode.

The second feature is the **logically air-gapped vault**, a distinct vault type rather than a setting on an ordinary one. Four properties define it. It is always locked with Vault Lock in compliance mode, with a minimum retention period of at least 7 days, so there is no unlocked variant. It is encrypted by default with an AWS owned key managed by AWS Backup, optionally a customer managed key, rather than a key from the source account. Its backups are stored in an AWS Backup service-owned account, which is what makes the isolation logical rather than a matter of account boundaries you administer. And it can be shared with other accounts, including accounts in other organizations, through **AWS Resource Access Manager (AWS RAM)**, the service for sharing resources across accounts, so a backup can be restored directly by an account that did not create it. Ordinary vaults are not compatible with AWS RAM and are shared through vault policies instead.

That sharing property is the reason to choose it, and it is a recovery time argument as much as a security one. If the account owning the production data is compromised or closed, an ordinary cross-account copy still has to be copied back before it can be restored, whereas a shared logically air-gapped vault can be restored from directly. AWS recommends holding these copies cross-Region and pairs the vault with multi-party approval so backups stay reachable even when the owning account is not. A third protection sits alongside both: a legal hold, which prevents deletion of the recovery points it covers regardless of their lifecycle, capped at 50 per account, and which is the answer when retention must be suspended for litigation without changing the backup plan.

## Cross-Region copy, cross-account copy and backup policies

A copy action inside a backup rule is what turns a local backup into a disaster recovery asset, and AWS Backup supports copying to another Region, to another account, or to both in one action. The first copy into a new Region or account is always full; subsequent copies are incremental for resource types that support incremental backup, provided they go to the same vault with the same key. AWS Backup re-encrypts each copy with the destination vault's key, which is the fact most often tested, and it is also why Amazon EBS is called out as an exception: copying an EBS snapshot into a vault with a different key produces a full copy rather than an incremental one. Two other constraints decide questions. AWS Backup does not support cross-Region or cross-account copies of backups that are already in a cold tier, and when a continuous backup is copied across Regions or accounts the copy becomes an ordinary snapshot, so point-in-time restore is not available from the copy.

Cross-account copy has a specific setup. All accounts involved must belong to the same organization in **AWS Organizations**, the service for centrally managing multiple AWS accounts, and the management account must first enable the cross-account backup feature. The destination vault cannot be the default vault, whose key cannot be shared across accounts, and it needs a resource-based policy allowing `backup:CopyIntoBackupVault`; any other cross-account action is rejected. If the source resources use a customer managed KMS key, that key must be shared with the destination account. For resource types under full AWS Backup management the destination may use either a customer managed key or the AWS managed `aws/backup` key; every other type requires a customer managed key, because AWS managed key policies are immutable and cannot be shared across accounts.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowOrgCopyIntoBackupVault",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "backup:CopyIntoBackupVault",
      "Resource": "*",
      "Condition": { "StringEquals": { "aws:PrincipalOrgID": "o-a1b2c3d4e5" } }
    }
  ]
}
```

The pattern this enables is the one Professional questions describe: a dedicated backup account, isolated from production, that every workload account fans its backups into and can fan them back out of for recovery. One rule is easy to get wrong: you cannot restore a backup from account A directly into account B, you copy it into account B first and restore it there. Two security details finish the pattern. A destination account that later leaves the organization keeps the backups it holds, so AWS recommends denying `organizations:LeaveOrganization` on it through a service control policy, and because any member account can nominate itself as a destination once the feature is on, policies using `backup:CopyTargets`, `backup:CopyTargetOrgPaths` or a required destination-vault tag are how you restrict where copies may go.

Backup policies in AWS Organizations are the layer above backup plans. A backup policy is a JSON document containing everything a backup plan needs, attached to the organization root, an organizational unit or an account, and Organizations applies inheritance rules to combine every policy reaching an account into one effective backup policy. That effective policy appears in the member account's AWS Backup console as an immutable plan the account can view but not change, which is how a central team enforces a retention standard a workload team cannot weaken. A policy carries the same tag-based resource selection a plan does, and inheritance lets you set a default at the root, for example that all DynamoDB tables are backed up, then override the frequency in child policies so the Developers organizational unit backs up weekly and Production daily. The trap is completeness: AWS Backup runs a policy only when the effective policy contains every required element, so partial policies relying on inheritance leave resources silently unprotected if the combination is incomplete. AWS recommends making every policy complete on its own and using child control operators to override.

## Backup Audit Manager and organization-wide reporting

Having a plan is not the same as it covering everything, and **AWS Backup Audit Manager** closes that gap. It answers questions of the form "am I backing up all my resources", "are all of my backups encrypted" and "are my backups taking place daily" by evaluating your environment against controls, each auditing one backup requirement such as frequency, retention, encryption, whether a resource is in a plan that uses a locked vault, whether a backup exists in at least one logically air-gapped vault, and whether restore time met a target. You group controls into a framework, view it to see which resources are compliant, and create report plans that publish results to Amazon S3. A report is generated automatically every 24 hours, on demand reports are available, and findings can be imported into **AWS Audit Manager**, the separate compliance evidence service, not to be confused with Backup Audit Manager.

One prerequisite catches people out: before creating your first compliance framework you must turn on resource tracking, which means enabling **AWS Config**, the configuration recording and rules service, to record your AWS Backup resources, and charges apply to that recording. Only active resources are evaluated, so a stopped EC2 instance is excluded from the compliance count while a running one is included. The quotas are small enough to plan around: 15 frameworks and 50 controls per account per Region, and 20 report plans per account. Combined with cross-account management, Audit Manager is what lets an organization's management account or delegated administrator report on backup compliance for every member account in one place, which is the keyed answer whenever a Professional stem asks for evidence of backup compliance across dozens of accounts with the least operational overhead.

## AWS Elastic Disaster Recovery

**AWS Elastic Disaster Recovery (AWS DRS)** replicates whole servers, block by block, into AWS so they can be launched there when the place they normally run stops working. It is in scope for SAP-C02 and not for SAA-C03, so Associate candidates can read this section for context and move on. Its source can be a physical server, a virtual machine, a server in another cloud, or an EC2 instance, and it is the answer whenever a scenario involves recovering a server-hosted application or a self-managed database with no native cross-Region replication. For AWS-hosted workloads its documented boundary is applications and databases on EC2, not managed services such as Amazon RDS.

The replication model is what distinguishes it. You install the AWS Replication Agent on each source server; it sits in memory, captures blocks continuously as they are written to disk, compresses and encrypts them, and sends them to a staging area subnet in your account in the Region you choose. That staging area holds low-cost storage and minimal compute, which is the whole cost argument: you pay to keep data current without paying for a duplicate fleet. AWS documents a crash-consistent RPO in the sub-second to seconds range, bounded by whether the networks and staging resources absorb writes as fast as the source produces them, and an RTO typically between 5 and 20 minutes dominated by boot time, with an average Linux server booting in about 5 minutes and an average Windows server in about 20. Crash consistent means the recovery point holds everything written to disk, not data still in memory.

Recovery is not limited to the latest state. AWS DRS keeps point-in-time snapshots on a fixed schedule of one every 10 minutes for the previous hour, one per hour for the previous 24 hours, and one per day for the previous 7 days, and only that last retention value is adjustable, from 1 to 365 days. That makes DRS an answer to ransomware as well as to infrastructure failure, because you can launch a recovery instance from a point before the encryption started. On launch DRS converts the volumes so a server that originated outside AWS boots natively on EC2, and after the primary site recovers it orchestrates failback.

Place it correctly against the four strategies. AWS describes DRS as using the pilot light approach, keeping data and switched-off resources in a staging VPC and building a full-capacity deployment on failover, while offering recovery objectives comparable to warm standby. That combination, warm standby objectives at close to pilot light cost, is what the Well-Architected guidance suggests considering when cost is a concern and the objectives look like warm standby.

> **Professional depth.** Two comparisons come up. AWS DRS and **AWS Transform MGN**, which both exam guides still call AWS Application Migration Service, share almost all their replication and launch technology; MGN is the lift-and-shift migration service that moves servers to AWS with a short cutover, DRS is the disaster recovery service, and the capability MGN lacks is failback to the source environment. The two agents cannot coexist on one server, so an MGN agent must be removed before DRS can protect it. Detail on the migration side lives in [AWS Application Migration Service](../10-migration/application-migration-service.md). The second comparison is against AWS Backup: DRS replicates continuously and its unit is the server, while AWS Backup is scheduled and point-in-time and its unit is the resource, so a stem naming RDS databases, DynamoDB tables or S3 buckets wants AWS Backup, and a stem naming a fleet of data center virtual machines with an RPO in seconds wants DRS.

## Testing the plan: restore testing, game days and fault injection

AWS's position on untested plans is unusually blunt, and it is the heart of SAP-C02 task 3.1's bullet on engineering failure scenario activities. The pattern to avoid is developing recovery paths that are rarely exercised, because the only error recovery that works is the path you test frequently. AWS's example is a secondary data store you intend to promote on failure: if the promotion is never tested, you discover during the real event that the secondary's capacity no longer carries the load, or that a service quota in the recovery Region is too low. A small number of well-exercised recovery paths therefore beats a large number of documented ones, and AWS lists "never exercise failovers in production" as the anti-pattern for this best practice.

Testing a backup is a different activity from testing a failover, and both exams expect both. AWS's stated backup anti-patterns are assuming a backup exists, assuming it is operational, assuming the restore finishes inside the RTO, assuming its data falls inside the RPO, and restoring without then querying any data to confirm the restoration is usable. The remedy is a periodic recovery test that restores to a new location, validates content against criteria defined in advance such as a checksum or record count, measures how long restore and validation took against the RTO, and notifies stakeholders when either fails.

AWS Backup restore testing automates that loop. A restore testing plan has a name, a frequency, a target start time and a start window of 1 to 168 hours, then a recovery point selection: which vaults to draw from, how far back eligible points may come, from 1 to 365 days, whether to take the latest eligible point or one at random, and whether continuous backup points count. A random point gauges the health of the whole retention window, not just last night's job. You assign resources by type and tag, name the IAM role the restore runs under, and set a cleanup delay of 1 to 168 hours if you want to validate the restored resource yourself. AWS Backup infers the restore metadata each type needs, such as subnet, instance class and security group, and lets you override it. When the plan runs it starts a real restore job, visible in **AWS CloudTrail**, the AWS API activity log, as `StartRestoreJob` and shown with restore type `Test`, restores at most one recovery point per protected resource, records the completion time, then deletes the resource by finding the `awsbackup-restore-test` tag it applied. Supported types are Aurora, Amazon DocumentDB, Amazon DynamoDB, Amazon EBS, Amazon EC2, Amazon EFS, all four FSx file systems, Amazon Neptune, Amazon RDS and Amazon S3. Pair it with the Audit Manager control that checks restore time against a target and you have repeated evidence that the RTO is achievable.

A game day is the organizational equivalent: a simulation of an event in a production-like environment, involving the same teams who would handle the real scenario, in which participants perform the actions they would actually perform and observe how people, processes and technology respond. Game days run on a schedule so response becomes habit, everyone is told in advance, and the exercise ends with a retrospective whose findings are tracked to completion. AWS lists the failure modes: documenting procedures but never exercising them, excluding business decision makers, focusing only on technical failure, not feeding lessons back, and blaming teams for what the exercise uncovers. If impact appears, the team rolls the test back and fixes what it found.

Separate two things people call testing. A tabletop exercise is a discussion: the team walks through the runbook against a hypothetical scenario, in a room, touching nothing. It is cheap, it surfaces gaps in documentation, ownership and escalation, and it is the right first step for a new plan, but it cannot tell you whether the failover works because nothing failed over. A real failover exercise moves traffic, promotes the replica, scales the standby and measures elapsed time, and it is the only thing that validates an RTO. Mature programs use both, updating the runbook after each. What a real exercise confirms is what drift quietly breaks, and AWS names it: current Amazon Machine Images in the recovery Region, service quotas high enough for full production capacity, and configuration that has not drifted, which AWS Config and CloudFormation drift detection watch continuously. **AWS Fault Injection Service** runs controlled fault experiments, such as terminating instances or injecting latency, against a defined stop condition. It is on neither exam's in-scope list, so recognize the name and move on. It is on neither exam's in-scope list, so no question will turn on its parameters; recognize it as the AWS answer to "how do we inject failure safely" and move on.

## Pricing shape, monitoring and the limits that matter

AWS Backup bills on five axes and the exam tests the shape, not the rates: backup storage per GB-month with a cheaper cold tier, data restored, restore testing per test plus the restore jobs it runs, cross-Region data transfer for copies, and AWS Backup Audit Manager including the AWS Config resource tracking it depends on. Vault Lock is free; what it costs is the storage it prevents you deleting early. Where the charge appears depends on the resource: types under full AWS Backup management bill under Backup, others under their own service, so EBS backups show under Amazon EBS while S3 backups and everything in a logically air-gapped vault show under AWS Backup. The two levers that reduce the bill are lifecycle, moving long-retention backups to cold storage while respecting the 90-day minimum, and retention itself.

Monitoring sits in the same place as the plans. AWS Backup publishes metrics to Amazon CloudWatch so you can alarm on failed jobs, emits events to **Amazon EventBridge**, the serverless event bus, logs API calls to AWS CloudTrail, and notifies through **Amazon SNS**, the pub/sub messaging service, when a backup succeeds or a restore begins. The console dashboard shows recent backup, copy and restore jobs, and with cross-account management and trusted access enabled the management account sees job status and errors for every member account. An alarm on failed backup jobs is the minimum viable control, because a plan that has been quietly failing for a month is indistinguishable from no plan at all until you need it.

The quotas worth carrying in are these. An account gets 300 vaults per Region, counting backup and logically air-gapped vaults together, 300 backup plans per Region, both adjustable, and 1,000,000 recovery points per vault. A plan holds 10 backup rules and 100 resource assignments, and an assignment may use 30 tags; neither of those last two can be raised, so at scale you split across plans. A rule may carry 5 copy actions, and only one backup or copy job runs per resource at a time. Copy throughput is capped at 100 concurrent copy jobs per account in a destination Region, after which a vault with fewer than 5 running copies can still start up to 5, which is the quota that bites when a large estate fans every nightly backup into one recovery Region at once. Restore testing allows 100 plans with 30 selections each, and legal holds are capped at 50 per account. One timing behavior surprises people: expired backups are deleted at a random point over the following 8 hours, so expiry is approximate by design.

## Professional depth

At organization scale the unit of design stops being the backup plan and becomes the account topology. The reference shape is a dedicated backup account no workload team can log into, holding vaults every production account copies into, with cross-account backup enabled from the management account and each destination vault allowing `backup:CopyIntoBackupVault` and nothing else. Standards are pushed down as backup policies rather than per-account plans, so each account's effective policy is immutable to it, and a delegated administrator runs the program without daily use of management account credentials. Service control policies close the rest: one restricting copy destinations by `backup:CopyTargetOrgPaths` or a required destination-vault tag, and one denying `organizations:LeaveOrganization` on the backup account.

The quotas that bite are concurrency quotas rather than capacity quotas. One hundred concurrent copy jobs per account into a destination Region, with only five more per vault once that ceiling is hit, turns a nightly fan-in from hundreds of accounts into a queue, and the fix is staggering backup windows and spreading copies across several destination vaults, because the per-vault allowance cannot be raised. A plan takes 100 resource assignments and a selection takes 30 tag conditions, neither adjustable, so a large estate is organized as many plans keyed on a few standard tags rather than one plan with a long list. Only one backup or copy job runs per resource at a time, so overlapping hourly and daily rules on the same volume will not double up.

The failure mode Professional questions probe most is a recovery path that depends on the Region it is recovering from. Scaling a standby with EC2 Auto Scaling, creating resources from a CloudFormation stack, restoring from a backup and editing a weighted DNS record are all control plane operations, each lengthening the RTO and adding a dependency that may be unavailable during a Regional event. The mitigations are to pre-provision enough capacity that the recovery Region is statically stable, to hold On-Demand Capacity Reservations or provisioned concurrency so the scale-up cannot be refused, and to move the traffic switch onto a data plane with an ARC routing control. AWS also suggests restoring backups into the recovery Region on a schedule, so operable data stores exist even if the restore control plane does not.

Failback is the half of the plan most designs omit, and it is where consistency is hardest, because the recovery Region now holds the authoritative data. Some services handle it: an Aurora global database failed over with a managed operation keeps its replication topology, so the former primary becomes a replica and catches up, and DynamoDB global tables resume propagating pending writes when the impaired Region returns. Everywhere else you rebuild the original primary as a replica of the recovery Region, and AWS DRS provides an explicit failback flow for servers. Because failback is expensive, some organizations promote the recovery Region to be the new primary, and a few rotate the two on a schedule, which also proves the plan works.

Hybrid estates add two pieces. Data center and other-cloud servers are protected with AWS DRS agents replicating into a staging subnet, while VMware virtual machines come under AWS Backup through the backup gateway, so one set of plans and one Audit Manager framework cover both. The compliance overlay is the last piece: a regulator's name in the stem points at Vault Lock in compliance mode, and protection from a compromised administrator plus fast restore into a clean account points at a logically air-gapped vault shared through AWS RAM.

## Worked scenario

A claims processor runs a three-tier application in us-east-1 across 40 accounts in one organization: EC2 instances in Auto Scaling groups behind a load balancer, an Aurora PostgreSQL claims database, scanned documents in S3, and a legacy rules engine on two Windows servers in a colocation facility. The business has set a four hour RTO and a fifteen minute RPO for the claims path, plus a regulatory requirement that claim documents and database backups be retained for seven years in a form nobody, including the cloud team, can delete early. Reporting and development environments are excluded and protected as cheaply as possible.

Four hours and fifteen minutes sits in the pilot light band, so us-west-2 gets an Aurora global database secondary cluster, S3 Cross-Region Replication on the documents bucket, and CloudFormation stacks defining the web and application tiers with a desired capacity of zero, scaled up on failover. The rules engine is protected with AWS DRS agents replicating from the colocation facility into a staging subnet, bringing its RPO to seconds and its RTO to minutes rather than the days a bare-metal rebuild would take. Traffic moves on an ARC routing control attached to Route 53 failover records, not on a manual record edit, so the switch does not depend on a control plane in the failing Region.

Backups are separate from replication, because replication would copy a bad write. A backup policy on the Production organizational unit creates a plan whose daily rule selects resources by a `Backup=prod` tag, retains them 30 days locally and copies into a logically air-gapped vault in a dedicated backup account in us-west-2. A second rule handles the seven-year copy, transitioning to cold storage after 30 days with a total retention of 2,557 days, into a vault locked in compliance mode with a three day grace time. The Development organizational unit inherits a weekly rule with 14 day retention and no copy. A Backup Audit Manager framework checks coverage, encryption and restore time daily; a restore testing plan restores a random recovery point weekly into the backup account and deletes it after a four hour validation window; and a quarterly game day flips the routing control, scales the standby, launches DRS drill instances and measures elapsed time against the four hour objective.

The exam asks this two ways. At Associate level it asks which strategy meets a four hour RTO and fifteen minute RPO at the lowest cost, and the key is pilot light with a replicated database and switched-off compute, not warm standby and not backup and restore. At Professional level it asks how to guarantee seven years of backups cannot be deleted by a compromised administrator while keeping recovery fast, and the key is cross-account copy into a compliance mode locked vault, with the operational copy in a logically air-gapped vault shared to the recovery account so a restore needs no copy back first.

## Exam lens

- "RPO of 15 minutes and RTO of 4 hours, lowest cost" maps to pilot light: data replicated and always on, compute defined but not running.
- "Must serve traffic immediately at reduced capacity after failover" maps to warm standby. Pilot light is the distractor, because it cannot process requests until resources are turned on.
- "RTO near zero and users served from the closest Region" maps to multi-site active-active; warm standby is the distractor when both Regions already serve production traffic.
- "We can tolerate a day of downtime, non-production" maps to backup and restore with cross-Region copies; any standing standby loses a "MOST cost-effective" question.
- "Protect against accidental deletion and ransomware" maps to point-in-time backups plus Vault Lock; cross-Region replication is the distractor, because replication copies the bad write.
- "No one, including the root user, may delete backups early", or a stem naming SEC 17a-4, FINRA or CFTC, maps to Vault Lock in compliance mode with a grace time of at least 3 days; governance mode is the distractor, because a privileged user can remove it.
- "Restore into a separate account even if the production account is compromised" maps to a logically air-gapped vault shared through AWS RAM. An ordinary cross-account copy is the distractor, because it must be copied back first.
- "Enforce one retention standard across 200 accounts that local teams cannot weaken" maps to backup policies in AWS Organizations, which produce an immutable effective plan per account.
- "New resources must be protected automatically" maps to tag-based resource assignment, not a list of ARNs.
- "Prove to auditors that every resource is backed up and encrypted" maps to AWS Backup Audit Manager frameworks, controls and daily reports, which need AWS Config resource tracking turned on first.
- "Confirm the restore works and finishes inside the RTO" maps to AWS Backup restore testing plans, with the Audit Manager control that checks restore time against a target.
- "Replicate data center servers with an RPO of seconds and recover to a point before the ransomware" maps to AWS Elastic Disaster Recovery; AWS Backup is the distractor when the RPO is seconds, and AWS Transform MGN, formerly Application Migration Service, is the distractor because MGN cannot fail back.
- "Move backups to a cheaper tier after 30 days" maps to a cold storage transition, with total retention set at least 90 days beyond the transition.
- "Point-in-time restore of the copy in the second Region" is a trap: a continuous backup copied cross-Region or cross-account becomes a snapshot, so PITR is unavailable from the copy.
- "Exercise the recovery procedure with the teams who would run it" maps to a game day; a tabletop validates the runbook but not the RTO, and only a real failover measures recovery time.
- "Failover must work when the primary Region's APIs do not" maps to an ARC routing control, a data plane mechanism, not a control plane call.
- "Data must not leave the country and there is only one Region here" rules out multi-Region entirely; the answer is Multi-AZ plus backups.

## Knowledge check

### 1. Choosing a strategy from the objectives (Associate)

A media company runs a web application and a PostgreSQL database in one AWS Region. After a business impact review, the company sets a recovery time objective of 2 hours and a recovery point objective of 10 minutes for a Regional failure. The company wants to spend as little as possible on standing recovery capacity.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Take daily database snapshots, copy them to a second Region, and rebuild the environment from a CloudFormation template after an event.
- **B)** Replicate the database continuously to a second Region, define the application tier in a CloudFormation template that is not deployed there, and launch and scale that tier on failover.
- **C)** Run a scaled-down but fully functional copy of the application and database in a second Region at all times.
- **D)** Run the full application and database in both Regions and route users with latency records.

<details><summary>Answer</summary>

**Answer: B.** This is pilot light: data stores replicated and always on, compute defined but switched off. AWS documents pilot light as reaching an RPO in minutes and an RTO in tens of minutes, which satisfies 10 minutes and 2 hours, and it holds no idle application capacity. A fails because daily snapshots give an RPO of up to 24 hours, far outside 10 minutes. C is warm standby, which meets the objectives but pays continuously for a running application tier that the stated RTO does not require, so it loses a "MOST cost-effective" question. D is multi-site active-active, the most expensive and most complex option, and nothing in the stem asks for near-zero recovery time or multi-Region reads.

*Where this is covered: Availability Zones, Regions and the four disaster recovery strategies.*

</details>

### 2. Backups a privileged user cannot delete (Associate)

A financial services firm must retain database backups for seven years to satisfy a regulator that cites SEC 17a-4. An internal audit requires that no principal, including the account root user, can delete a backup or shorten its retention before the seven years elapse.

Which solution will meet these requirements?

- **A)** Store the backups in an S3 bucket with **S3 Object Lock**, the write-once-read-many control on objects in governance mode and a seven year retention period.
- **B)** Apply AWS Backup Vault Lock in governance mode to the vault, with a minimum retention period of 2,557 days.
- **C)** Apply AWS Backup Vault Lock in compliance mode to the vault, with a grace time of 3 days and a minimum retention period of 2,557 days.
- **D)** Attach a vault access policy that denies `backup:DeleteRecoveryPoint` to every principal in the account.

<details><summary>Answer</summary>

**Answer: C.** Only compliance mode makes the vault and its lock immutable once the grace time expires, so that neither a user, nor the root user, nor AWS can delete a recovery point or change its lifecycle before retention completes. AWS Backup Vault Lock has been assessed for use under SEC 17a-4, CFTC and FINRA regulations, which is why the regulator's name points here. B fails because a governance mode lock can be removed by anyone holding sufficient IAM permissions, which is exactly the principal the audit is worried about. A uses the wrong control surface, since the backups live in AWS Backup vaults rather than in a bucket you manage, and governance mode there is likewise removable. D fails because an identity policy or vault policy can be edited by a principal with policy permissions, including the root user.

*Where this is covered: Vault Lock and logically air-gapped vaults.*

</details>

### 3. One backup standard across 40 accounts (Associate)

A company runs 40 AWS accounts in one organization. Teams create new Amazon EBS volumes and Amazon RDS instances every week. A central platform team must guarantee that every production resource is backed up daily and retained for 35 days, and that workload teams cannot weaken the schedule or the retention in their own accounts.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Assign resources to the backup plan with a tag condition rather than by listing resource ARNs.
- **B)** Create an identical backup plan by hand in each of the 40 accounts and review them monthly.
- **C)** Grant each account's administrators full access to their backup vault so they can correct failed jobs quickly.
- **D)** Define the backup plan as a backup policy in AWS Organizations and attach it to the Production organizational unit.
- **E)** Create an AWS Config rule that notifies the platform team whenever an untagged EBS volume is created.

<details><summary>Answer</summary>

**Answer: A and D.** A tag-based resource assignment brings a new volume or database into the plan the moment it is tagged, with nobody remembering to add it, and a backup policy attached to an organizational unit produces an effective plan that appears in each member account as an immutable plan the account can view but not change. B is a custom build of something AWS Organizations already manages, and hand-maintained copies drift. C breaks the stated requirement directly, because full vault access lets a workload team delete backups and alter lifecycles. E provides useful visibility but protects nothing on its own; a notification does not cause a backup to be taken.

*Where this is covered: Cross-Region copy, cross-account copy and backup policies.*

</details>

### 4. Retention with a cold tier (Associate)

A company backs up an Amazon EFS file system with AWS Backup and must keep each backup for 365 days. To reduce cost, the company wants each backup to move to cold storage after 30 days in warm storage.

Which solution will meet these requirements?

- **A)** Set the transition to cold storage at 30 days and the total retention period at 90 days.
- **B)** Set the transition to cold storage at 30 days and the total retention period at 100 days.
- **C)** Keep every backup in warm storage for the full 365 days and delete it on day 365.
- **D)** Set the transition to cold storage at 30 days and the total retention period at 365 days.

<details><summary>Answer</summary>

**Answer: D.** A backup transitioned to cold storage must remain in cold storage for a minimum of 90 days on top of its time in warm storage, so AWS Backup requires the total retention period to be at least 90 days greater than the transition setting. With a 30 day transition, the minimum valid total retention is 120 days, and 365 days satisfies both that rule and the stated retention requirement. A and B are rejected by AWS Backup because 90 and 100 days are less than 30 plus 90. C meets the retention requirement but keeps every backup in the more expensive warm tier for a year, which is the outcome the company is trying to avoid.

*Where this is covered: AWS Backup: plans, rules, vaults and the resources it protects.*

</details>

### 5. Restoring when the source account is compromised (Professional)

A company copies AWS Backup recovery points from 60 production accounts into a standard backup vault in a dedicated backup account. A tabletop exercise raised a scenario in which an attacker gains administrative credentials in a production account. The company wants to restore the affected workloads into a separate, clean recovery account within a few hours, without a copy step during the incident.

Which solution will meet these requirements?

- **A)** Copy the backups into a logically air-gapped vault in the backup account, share that vault with the recovery account through AWS Resource Access Manager, and restore directly from the shared vault.
- **B)** Copy the backups into a standard vault in the dedicated backup account and apply AWS Backup Vault Lock in governance mode.
- **C)** Enable S3 Cross-Region Replication from the production accounts to a bucket in the recovery account.
- **D)** Grant the recovery account `backup:CopyIntoBackupVault` on each production account's vault so it can pull backups when an incident occurs.

<details><summary>Answer</summary>

**Answer: A.** A logically air-gapped vault is always locked in compliance mode, stores its backups in an AWS Backup service-owned account, and is the only vault type that can be shared through AWS RAM, which lets an account other than the vault owner restore from it directly. That removes the copy step the stem forbids. B does not, because a backup in a standard vault can only be restored by the account that owns the vault, and a governance mode lock can be removed by a sufficiently privileged principal. C replicates objects rather than protecting backups, and replication faithfully copies encrypted or deleted data from a compromised account. D is the wrong permission in the wrong direction: `backup:CopyIntoBackupVault` authorizes writing into a destination vault, and even a successful copy would still have to finish before a restore could start.

*Where this is covered: Vault Lock and logically air-gapped vaults.*

</details>

### 6. Evidence that the restore works (Associate)

Auditors have asked a company to demonstrate, on a recurring basis, that its Amazon RDS backups can actually be restored and that a restore completes inside the four hour recovery time objective. The company wants the least operational overhead.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Restore one backup manually each quarter and record the elapsed time in a spreadsheet.
- **B)** Create an AWS Backup restore testing plan that restores a recovery point on a schedule and deletes it afterward, and enable the AWS Backup Audit Manager control that checks whether restore time meets a target.
- **C)** Build an AWS Lambda function invoked on a schedule by Amazon EventBridge that calls `StartRestoreJob`, polls for completion, writes timings to Amazon DynamoDB, and deletes the restored instance.
- **D)** Create AWS Config rules that check whether every RDS instance is assigned to a backup plan.

<details><summary>Answer</summary>

**Answer: B.** Restore testing runs real restore jobs on a schedule, selects recovery points by a latest-or-random algorithm from the vaults and window you specify, records completion times, and deletes the restored resource after the validation window, and the Audit Manager control turns the recorded time into a compliance result the auditors can read. A is manual, infrequent, and produces evidence no stronger than the spreadsheet. C rebuilds exactly what AWS Backup already manages, including the cleanup logic, and adds code to maintain. D verifies that backups are being taken, not that they can be restored or how long a restore takes, which is the specific thing the auditors asked for.

*Where this is covered: Testing the plan: restore testing, game days and fault injection.*

</details>

### 7. A failover that keeps failing (Professional)

A company runs a warm standby in a second Region. The documented failover procedure is to edit the weights on Amazon Route 53 records so that all traffic goes to the standby, then increase the desired capacity of the Auto Scaling groups there. During the last two Regional impairments the operations team could not complete either step in time, and the standby was overwhelmed by the traffic it did receive.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Increase the time to live on the Route 53 records so that clients cache the recovery endpoint for longer.
- **B)** Replace the weight edit with an Amazon Application Recovery Controller routing control, whose state is changed through a multi-Region data plane.
- **C)** Reduce the standby to a pilot light configuration so that fewer resources need to be managed during an event.
- **D)** Hold a weekly tabletop review of the failover runbook with the operations team.
- **E)** Pre-provision the standby at full production capacity and run a quarterly game day that actually shifts production traffic to it.

<details><summary>Answer</summary>

**Answer: B and E.** Editing a weighted record is a control plane operation, so it is the least reliable step to depend on during the impairment it is meant to escape; a routing control flips a Route 53 health check through a dedicated multi-Region data plane designed to work when a Region does not. Pre-provisioning to full capacity makes the recovery Region statically stable, removing the Auto Scaling control plane dependency, and a game day that really moves traffic is what proves both changes work. A makes failover slower, because a longer time to live means clients keep the old answer for longer. C reduces the standby's readiness and makes the RTO worse. D is worth doing, but a tabletop discussion touches nothing and cannot validate a recovery time objective.

*Where this is covered: Testing the plan: restore testing, game days and fault injection.*

</details>

### 8. Protecting a colocation estate (Professional)

A company runs 120 Windows and Linux servers in a colocation facility, including a self-managed SQL Server cluster. After a ransomware incident at a peer, the company needs a recovery point objective measured in seconds, a recovery time objective under 30 minutes, and the ability to recover a server to a state from before an encryption event. The company wants the least operational overhead.

Which solution will meet these requirements?

- **A)** Install the AWS Transform MGN agent, formerly AWS Application Migration Service, on each server and launch test instances weekly.
- **B)** Use AWS DataSync to copy the file systems to Amazon S3 every hour and restore them with AWS Backup after an event.
- **C)** Install AWS Elastic Disaster Recovery agents on each server to replicate continuously into a staging area subnet, and recover from a point-in-time snapshot taken before the event.
- **D)** Use AWS Backup with the backup gateway to take hourly backups of the servers and copy them to a second Region.

<details><summary>Answer</summary>

**Answer: C.** AWS Elastic Disaster Recovery performs continuous block-level replication from any source into a low-cost staging area, giving a crash-consistent RPO in seconds and an RTO typically between 5 and 20 minutes, and it retains point-in-time snapshots on a fixed schedule so a server can be launched from a state before the encryption started. A is the migration service: it shares the replication technology but is built for a one-way cutover and cannot fail back, so it is the wrong product for an ongoing DR posture. B and D both give an RPO bounded by the copy interval, which is an hour, an order of magnitude outside the stated requirement, and B additionally leaves the operating system and application state to be rebuilt by hand.

*Where this is covered: AWS Elastic Disaster Recovery.*

</details>

### 9. Serving traffic the moment failover completes (Associate)

A company's DR design replicates its database to a second Region and keeps the application tier defined in an AWS CloudFormation template that is not deployed there. A new requirement states that after a failover the recovery Region must begin serving requests immediately at roughly 25 percent of production capacity while the fleet scales up.

Which solution will meet these requirements?

- **A)** Deploy the application tier in the recovery Region at 25 percent of production capacity and leave it running, converting the design to warm standby.
- **B)** Keep the current design and reduce the time to live on the DNS records so that clients move faster.
- **C)** Convert the design to multi-site active-active so that both Regions serve production traffic at all times.
- **D)** Increase the frequency of database snapshots taken in the recovery Region.

<details><summary>Answer</summary>

**Answer: A.** The current design is pilot light, and AWS defines the difference precisely: pilot light cannot process requests until additional action is taken, whereas warm standby can handle traffic at reduced capacity immediately. Leaving a scaled-down application tier running is exactly that change. B addresses how quickly clients learn the new answer, not whether anything is listening when they arrive, so requests would still fail while instances launched. C satisfies the requirement but goes far beyond it, adding the cost and the write-conflict complexity of running both Regions active when the stem only asks for immediate reduced capacity after failover. D improves the recovery point, which the stem does not mention, and does nothing for the time to serve the first request.

*Where this is covered: Availability Zones, Regions and the four disaster recovery strategies.*

</details>

### 10. What survives a cross-Region copy (Associate)

A team copies AWS Backup recovery points from us-east-1 to eu-west-1 for disaster recovery. Continuous backups are enabled on the source Amazon RDS instance, and the team wants the smallest practical recovery point objective in the recovery Region while limiting cross-Region data transfer charges.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** A continuous backup copied to eu-west-1 keeps point-in-time restore in that Region.
- **B)** Backups that have already transitioned to cold storage can be copied to another Region.
- **C)** A continuous backup copied cross-Region becomes a snapshot, so point-in-time restore is not available from the copy.
- **D)** The first copy into a new Region is a full copy, and later copies are incremental when they go to the same vault using the same KMS key.
- **E)** AWS Backup encrypts the copy with the source vault's KMS key, so the destination vault needs no key of its own.

<details><summary>Answer</summary>

**Answer: C and D.** AWS documents that when a continuous backup is copied across Regions or accounts the copied recovery point becomes a snapshot, so the team must plan for snapshot-granularity recovery in eu-west-1 rather than point-in-time restore, and it documents that the first copy into a Region is full while subsequent copies are incremental for resource types that support incremental backup, which is the behavior that controls the transfer bill. A states the opposite of C and is false. B is false, because AWS Backup does not support cross-Region or cross-account copies of backups held in cold tiers. E is false and inverts the rule: AWS Backup re-encrypts each copy with the destination vault's key, which is why a destination vault key must exist and, for cross-account copies of most resource types, must be a customer managed key.

*Where this is covered: Cross-Region copy, cross-account copy and backup policies.*

</details>

## Summary

Disaster recovery is a sequence of decisions that begins outside the architecture. The business sets an RTO and an RPO per workload tier, and those two numbers select one of four strategies: backup and restore for hours of downtime, pilot light for tens of minutes, warm standby for minutes, and multi-site active-active for near zero, each costing more than the last. The weakest data store in the workload caps the achievable RPO, so you check each one against its own replication mechanism and cross-link to the unit that owns it. Underneath every strategy sits AWS Backup, where a plan of rules sets frequency, window, lifecycle and copies, vaults set the key and the access policy, Vault Lock in compliance mode makes retention unbreakable, logically air-gapped vaults let another account restore directly, and backup policies in AWS Organizations push one standard across every account. AWS Elastic Disaster Recovery covers servers no managed service replicates. Finally, none of it counts until it is exercised: restore testing proves the backup, and a game day proves the failover.

## Related units

- [Amazon S3](s3.md): Cross-Region Replication, versioning and Object Lock, which this unit references rather than reteaches
- [Amazon EBS](ebs.md): snapshots, snapshot copy and Data Lifecycle Manager behind the block storage row in the recovery table
- [Amazon Route 53](../04-networking/route53.md): failover routing, health checks and Application Recovery Controller, which move the traffic during a failover
- [Amazon RDS](../05-database/rds.md): cross-Region read replicas, automated backup replication and point-in-time recovery
- [Amazon Aurora](../05-database/aurora.md): Aurora Global Database, switchover and managed failover
- [Amazon DynamoDB](../05-database/dynamodb.md): global tables and their two consistency modes
- [AWS Application Migration Service](../10-migration/application-migration-service.md): the migration counterpart to Elastic Disaster Recovery
- [AWS Organizations, IAM Identity Center and Control Tower](../07-security/organizations-identity-center-and-control-tower.md): backup policies, delegated administrator and the service control policies that fence copy destinations

## Sources

- [Disaster recovery options in the cloud](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html): the four strategies, what runs in the recovery Region, and the data plane compared with control plane rule
- [REL13-BP01 Define recovery objectives for downtime and data loss](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_planning_for_recovery_objective_defined_recovery.html): AWS's definitions of RTO and RPO, the workload tier matrix, and the anti-patterns
- [REL13-BP02 Use defined recovery strategies to meet the recovery objectives](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_planning_for_recovery_disaster_recovery.html): the documented RPO and RTO band for each strategy, and where Elastic Disaster Recovery sits
- [REL13-BP03 Test disaster recovery implementation to validate the implementation](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_planning_for_recovery_dr_tested.html): why rarely exercised recovery paths fail
- [REL09-BP04 Perform periodic recovery of the data to verify backup integrity and processes](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_backing_up_data_periodic_recovery_testing_data.html): the backup testing anti-patterns and the validate, measure, notify loop
- [REL12-BP05 Conduct game days regularly](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_testing_resiliency_game_days_resiliency.html): the definition of a game day, its failure modes, and the retrospective
- [Testing disaster recovery](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/testing-disaster-recovery.html): managing configuration drift, AMIs and service quotas in the recovery Region
- [What is AWS Fault Injection Service?](https://docs.aws.amazon.com/fis/latest/userguide/what-is.html): the current service name, experiment templates, actions, targets, stop conditions and billing
- [What is AWS Backup?](https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html): the feature set, full AWS Backup management, and the supported resource list
- [Backup plan options and configuration](https://docs.aws.amazon.com/aws-backup/latest/devguide/plan-options-and-configuration.html): rules, frequency, backup window defaults, retention ranges and the 90-day cold storage rule
- [Logically air-gapped vault](https://docs.aws.amazon.com/aws-backup/latest/devguide/logicallyairgappedvault.html): the vault type's encryption, compliance mode lock, 7 day minimum retention and AWS RAM sharing
- [AWS Backup Vault Lock](https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html): governance compared with compliance mode, grace time, and the retention parameters
- [Creating backup copies across AWS Regions](https://docs.aws.amazon.com/aws-backup/latest/devguide/cross-region-backup.html): re-encryption with the destination key, incremental behavior and the cold tier exclusion
- [Creating backup copies across AWS accounts](https://docs.aws.amazon.com/aws-backup/latest/devguide/create-cross-account-backup.html): the Organizations prerequisite, vault policy, KMS requirements and restore ordering
- [Backup policies in AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_backup.html): inheritance, the effective policy and the completeness trap
- [AWS Backup Audit Manager](https://docs.aws.amazon.com/aws-backup/latest/devguide/aws-backup-audit-manager.html): frameworks, controls, daily reports and the AWS Config prerequisite
- [Restore testing](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html): plan structure, recovery point selection, validation window, cleanup and supported resource types
- [AWS Backup feature availability](https://docs.aws.amazon.com/aws-backup/latest/devguide/backup-feature-availability.html): which resources support cross-Region copy, cold storage, PITR and logically air-gapped vaults
- [AWS Backup quotas](https://docs.aws.amazon.com/aws-backup/latest/devguide/aws-backup-limits.html): vault, plan, rule, assignment, copy concurrency, legal hold and restore testing limits
- [What is Elastic Disaster Recovery?](https://docs.aws.amazon.com/drs/latest/userguide/what-is-drs.html): the staging area model, drills and failback
- [Elastic Disaster Recovery Concepts](https://docs.aws.amazon.com/drs/latest/userguide/CloudEndure-Concepts.html): the documented RPO and RTO, and the point-in-time snapshot schedule and retention
- [What Is AWS Transform MGN?](https://docs.aws.amazon.com/mgn/latest/ug/what-is-application-migration-service.html): the current name of AWS Application Migration Service and its migration purpose
- [Using Amazon Aurora Global Database](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html): up to 10 secondary Regions, sub-second replication, switchover and failover
- [How DynamoDB global tables work](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html): multi-Region eventual and strong consistency, the three-Region MRSC rule and the RPO of each
- [Creating a read replica in a different AWS Region](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.XRgn.html): cross-Region replica creation, lag and promotion behavior
- [Replicating automated backups to another AWS Region](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReplicateBackups.html): cross-Region snapshot and transaction log replication, and its Multi-AZ cluster limitation
- [Replicating EFS file systems](https://docs.aws.amazon.com/efs/latest/ug/efs-replication.html): the documented 15 minute RPO, read-only destination and failback
- [Copy an Amazon EBS snapshot](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-copy-snapshot.html): cross-Region and cross-account copy, encryption outcomes and when a copy is incremental
- [Replicating your data using NetApp SnapMirror](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/scheduled-replication.html): in-Region and cross-Region FSx for ONTAP replication as often as every 5 minutes
- [Replicating objects within and across Regions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html): Cross-Region Replication, Same-Region Replication, Batch Replication and S3 Replication Time Control
