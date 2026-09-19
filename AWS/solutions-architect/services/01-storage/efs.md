# Amazon EFS

**Where it sits on the exams.** **Amazon Elastic File System (Amazon EFS)** is the managed elastic file storage service that presents a shared POSIX directory tree over the Network File System (NFS) protocol, versions 4.0 and 4.1, to Linux clients. Its defining property is that there is no capacity to provision: it grows as files arrive, shrinks as they are deleted, and thousands of clients across Availability Zones can mount it at once. It answers the file storage questions in SAA-C03 tasks 2.1, 3.1 and 4.1 and supplies the shared storage layer in SAP-C02 tasks 4.3 and 4.4. Rule of thumb: several instances, containers or functions reading and writing the same files means EFS, and a stem worrying about how storage will be sized usually points there too, because EFS removes the sizing decision.

## What Amazon EFS is, and when storage auto scaling is required

EFS is file storage, between block and object. **Amazon Elastic Block Store (Amazon EBS)**, the network-attached block storage service for **Amazon Elastic Compute Cloud (Amazon EC2)**, hands one raw disk to one instance in one Availability Zone; **Amazon Simple Storage Service (Amazon S3)** stores whole objects by key with no directory semantics. EFS gives a directory tree with POSIX ownership and permissions, advisory locking and in-place writes, reachable concurrently by many clients. It is the answer whenever an application expects a mounted path such as `/var/www/uploads` and more than one machine must see the same bytes. It is Linux only, which is the boundary with **Amazon FSx**, the managed file system family that includes FSx for Windows File Server.

Capacity is the part of EFS that decides SAA-C03 task 4.1. An EFS file system has no provisioned size, no minimum charge and no high-water mark to pay for: it scales to petabytes as data is written, releases the space when data is deleted, and bills per GB-month of what is actually stored in each class. The exam's question of when storage auto scaling is required then resolves into a comparison. An EBS volume is provisioned, can grow but never shrink, still needs the guest file system extended afterwards, and accepts a limited number of modifications per day, so a growing shared dataset there means an alarm plus a resize runbook. S3 has no capacity concept but no file system semantics either. Storage auto scaling is required exactly when the footprint is unpredictable or spiky, when a manual resize would cost an outage or a page, and, for shared files, when several writers need the space at once. That combination names EFS, and "storage that grows automatically" in a stem is close to a keyword for it.

Two file system types split the rest of the decision. A Regional file system stores data redundantly across three or more Availability Zones. A One Zone file system stores it inside a single Availability Zone and, as AWS states plainly, is not resilient to the loss of that zone. Both are designed for eleven nines of durability, so the difference is blast radius rather than design target; the availability service level agreement is 99.99 percent for Regional and 99.9 percent for One Zone. AWS enables automatic daily backup with **AWS Backup**, the centralized managed backup service, for file systems created in the console, and One Zone file systems are backed up by default for exactly this reason. Treat One Zone as the file equivalent of an S3 One Zone class: cheaper, and correct for scratch space, development environments and reproducible data.

## Performance modes and throughput modes

Two independent settings control performance. The performance mode picks the metadata engine. General Purpose is the default, has the lowest per-operation latency, supports up to 250,000 file operations per second, and is the only mode One Zone uses; watch `PercentIOLimit` in **Amazon CloudWatch**. Max I/O is a previous generation option AWS no longer recommends, supported on neither One Zone nor Elastic throughput.

The throughput mode is what the exam tests. Read the table for each mode's ceiling on a Regional file system and the stem wording that selects it.

| Throughput mode | Default IOPS ceiling | Per-file-system throughput | Billing shape | The wording that selects it |
|---|---|---|---|---|
| Elastic (default) | 250,000 read for frequently accessed data, 90,000 read for infrequently accessed data, 50,000 write | 20 to 60 GiBps read, 1 to 5 GiBps write by Region | Per GB of data and metadata read and written | "spiky", "unpredictable", "cannot forecast", drives 5 percent or less of peak on average |
| Provisioned | 55,000 read, 25,000 write | 3 to 10 GiBps read, 1 to 3.33 GiBps write by Region | Per MiBps provisioned above the baseline included with Standard storage | Known, sustained requirements, or 5 percent or more average-to-peak ratio |
| Bursting | 35,000 read, 7,000 write | 3 to 5 GiBps read, 1 to 3 GiBps write by Region | Included in storage; no separate throughput charge | "throughput should scale with the amount of data stored" |

Elastic has been the default and recommended mode since April 2023, and it is what makes EFS behave like a serverless service: throughput scales automatically, there are no burst credits to accrue or exhaust, and you pay only for bytes moved. The IOPS figures above are defaults, and AWS will consider requests for up to ten times them. Per-client throughput is capped separately, at 1,500 MiBps on Elastic with a current EFS client or CSI driver and 500 MiBps otherwise.

Bursting is the legacy model and the source of the classic troubleshooting question. It earns a baseline of 50 KiBps per GiB held in Standard, accrues credits whenever it runs below that baseline, and spends them at up to 100 MiBps per TiB with a floor of 100 MiBps. When `BurstCreditBalance` reaches zero the file system drops to its baseline and the application appears to stall. Note the trap: the baseline derives from Standard storage only, so tiering cold data to cheaper classes shrinks a Bursting file system's throughput. Switching to Elastic or Provisioned is the documented fix once an application exceeds 80 percent of its permitted throughput or exhausts its credits. Switching mode causes no downtime, but after moving to Provisioned or raising the amount you must wait 24 hours before changing again.

## Storage classes and lifecycle management

EFS offers three storage classes inside one namespace, so a file moves between them without its path changing. Standard is SSD-backed for active data at sub-millisecond first-byte read latency. Infrequent Access (IA) suits data read a few times a quarter, at low double-digit millisecond latency and up to 95 percent lower storage cost. Archive suits data read a few times a year or less, at the same latency band, up to 50 percent below IA with a higher read charge. Two Archive constraints decide exam questions: it requires a Regional file system on Elastic throughput, and once a lifecycle policy targets Archive the file system cannot move to Bursting or Provisioned. Archive carries a 90-day minimum duration, and IA and Archive both bill a minimum of 128 KiB per file, so a directory of tiny files saves nothing by being tiered.

Lifecycle management moves the data and applies to the whole file system, not to a prefix. Transition into IA defaults to 30 days since last access; transition into Archive defaults to 90 days. Transition into Standard, which AWS markets as EFS Intelligent-Tiering, defaults to none, and its only other setting promotes a file back on first access, which is what a latency-sensitive application needs so it does not pay tens of milliseconds twice for the same file. Each policy accepts 1, 7, 14, 30, 60, 90, 180, 270 or 365 days.

Several details around that timer are exam material. The clock is an internal last-access timer, not POSIX `atime`, and listing a directory neither counts as an access nor resets it. File metadata always stays in Standard. A write to a file in IA or Archive lands in Standard first and can transition again only after 24 hours. Reads from IA and Archive carry an access charge and every transition carries a tiering charge, so an aggressive policy on data still being read can cost more than leaving it in Standard.

## Mount targets, access points and the security path

A client reaches a **mount target**, an NFSv4 endpoint with a private IP address in a subnet of an **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network service. A file system has mount targets in exactly one VPC, at most one per Availability Zone, shared by every instance in that zone; a One Zone file system has a single mount target. The DNS name resolves to the mount target in the client's own zone, and crossing zones works but adds latency and cross-zone transfer charges in both directions, so one mount target per zone is the standard design. A mount target never has a public IP, so on-premises access requires **AWS Direct Connect** or **AWS Site-to-Site VPN**, the dedicated private connection and managed IPsec tunnel services.

Security groups gate access at the mount target. The instance needs an outbound rule to TCP 2049 toward the mount target's security group, and the mount target an inbound rule on TCP 2049 from the instance's. A file system that will not mount and only times out is almost always missing one of those two rules.

**EFS access points** are application-specific entry points into one file system. An access point enforces a POSIX user ID, group ID and secondary groups on every request through it, overriding whatever the NFS client asserts, and enforces a root directory so the client sees only that subtree. A file system supports up to 10,000 of them. This is how one file system safely serves many teams, since **AWS Lambda**, **Amazon Elastic Container Service (Amazon ECS)** and **Amazon Elastic Kubernetes Service (Amazon EKS)** all attach through an access point rather than mounting the root.

**AWS Identity and Access Management (IAM)**, the AWS permissions service, supplies the NFS client actions `elasticfilesystem:ClientMount`, `ClientWrite` and `ClientRootAccess`, usable from an identity policy or from a file system policy, the resource policy on the file system. The default is frequently tested: with no file system policy, EFS grants full access to any client that can reach a mount target, so network reachability alone is the control until a policy exists. The condition keys that matter are `aws:SecureTransport`, `elasticfilesystem:AccessPointArn` and `elasticfilesystem:AccessedViaMountTarget`.

Encryption at rest uses AES-256 with **AWS Key Management Service (AWS KMS)**, the managed key service, holding either the AWS owned key `aws/elasticfilesystem` or a customer managed key. Two facts drive the questions. It is on by default in the console but must be requested explicitly through the CLI, API or an SDK. And it cannot be changed after creation, so the documented way to encrypt an existing unencrypted file system is to create an encrypted one and replicate or copy the data into it. Encryption in transit is the `-o tls` mount option.

## Replication, backup and the limits that bite

**EFS replication** keeps a full copy of a file system in another Region, Availability Zone or account, with no infrastructure to run. After an initial full sync it transfers incremental changes continuously, designed for a recovery point objective (RPO) of 15 minutes, though a source with more than 100 million files can fall behind; `TimeSinceLastSync` in CloudWatch proves it. The destination is read-only while replication is configured, which suits low-latency reads in a second Region as well as disaster recovery. Failing over means deleting the replication configuration, which makes the destination writable. Replication is not point-in-time consistent, and new file systems carry overwrite protection by default so one cannot accidentally become someone else's destination.

Replication is not a backup: a deletion on the source replicates. AWS Backup is the backup path. For bulk movement from on-premises NFS servers, **AWS DataSync**, the managed data transfer service, is the documented tool rather than a client-side copy.

The structural quotas worth remembering: 1,000 file systems per account per Region, 25,000 connections per file system, one mount target per Availability Zone, and a single file of up to 47.9 TiB. Costs beyond storage come from throughput, IA and Archive read and tiering charges, cross-zone and cross-Region transfer, and backup storage.

## Professional depth

The constraint shaping Professional answers is that one file system lives in one VPC with one mount target per Availability Zone. Where a shared dataset must reach several VPCs, that forces a choice: extend the network with VPC peering, **AWS Transit Gateway**, the managed connectivity hub, or a subnet shared through **AWS Resource Access Manager (AWS RAM)**, then mount by the mount target's IP address rather than the DNS name, which does not resolve outside its own VPC and account. The pattern that scales better is to give each account its own file system and use replication to distribute a read-only copy of reference data.

Cross-account replication has a permission wrinkle. Same-account replication can run on the EFS service-linked role; cross-account cannot. You must create an IAM role in the source account trusting `elasticfilesystem.amazonaws.com`, attach file system policies on both sides, and create both file systems yourself, since EFS will not create a destination in another account. A question adding "the recovery copy must live in a separate account so a compromise of production cannot reach it" is testing exactly this.

> **Professional depth.** Organization-wide enforcement is cheap here. The `elasticfilesystem:Encrypted` condition key, in a service control policy in **AWS Organizations**, the multi-account governance service, denies creation of unencrypted file systems everywhere, which matters precisely because encryption cannot be added later. EFS block public access is the companion control, stopping a file system policy granting access to an unqualified principal.

Two failure modes recur at scale. The first is silent permission loss: NFS truncates a user to 16 group IDs, so a directory identity carrying more loses access to files it should reach, and an access point with an enforced identity is the fix. The second is throughput starvation on a Bursting file system whose lifecycle policy is working well, because tiering cold data out of Standard shrinks the baseline the credits derive from. Where the access pattern is unknown, Elastic plus a 30-day IA policy is the safe default; Provisioned is the answer only once a measurement exists.

## Worked scenario

A media company runs video post-production on EC2 render nodes across three Availability Zones in eu-west-1. Every node reads and writes the same project directories, the working set runs between 20 TB and 400 TB depending on how many productions are live, and finance will not buy for the peak. Finished projects are read a handful of times the following quarter and almost never after a year, but legal requires them online for seven years in the directory structure the editors know. A second Region must resume work within an hour.

The design is a Regional file system with Elastic throughput, one mount target per Availability Zone, and security groups allowing TCP 2049 from the render node and task security groups only. Elastic removes both the capacity and the throughput decision, which the unpredictable working set demands; Bursting would have tied throughput to stored bytes and then shrunk it as tiering moved projects out of Standard. Lifecycle policies transition into IA after 30 days and Archive after 90, with transition into Standard on first access so an editor reopening an old project does not pay archive latency repeatedly. Archive is available only because the file system is Regional on Elastic throughput. Each production team gets an access point pinning a root directory and a POSIX identity, so one file system serves all of them without any team reaching another's footage. Replication to eu-west-2 gives an RPO of about 15 minutes, inside the one-hour requirement, and AWS Backup covers accidental deletion, which replication does not.

The exam asks this as a cost question, and the keyed answer is a Regional EFS file system with Elastic throughput and a lifecycle configuration transitioning to IA and then Archive. Over-sized EBS volumes, an FSx for Lustre scratch file system and S3 behind a mounted gateway are distractors that each break either the shared POSIX requirement or the no-capacity-planning requirement.

## Exam lens

- "multiple EC2 instances must access the same files" maps to a Regional file system with a mount target in each Availability Zone.
- "storage must scale automatically as data grows" maps to EFS; EBS is the distractor, because a volume is provisioned and grows only deliberately.
- "spiky or unpredictable throughput" maps to Elastic; Provisioned is the distractor once the stem has measured a steady requirement.
- "the application stalls after hours of heavy reads" maps to exhausted burst credits; the fix is Elastic or Provisioned.
- "a few times a quarter" maps to IA; "a few times a year" maps to Archive, which needs a Regional file system on Elastic throughput.
- "files must return to fast storage when reopened" maps to transition into Standard on first access.
- "scratch or test data that can be rebuilt" maps to One Zone, and is wrong whenever the stem mentions surviving an Availability Zone failure.
- "the mount times out with no error" maps to a missing TCP 2049 security group rule between client and mount target.
- "each team must see only its own directory under its own POSIX identity" maps to access points, not separate file systems.
- "an existing unencrypted file system must be encrypted" maps to creating an encrypted one and replicating into it.
- "cross-Region RPO of minutes with no infrastructure to manage" maps to EFS replication; an AWS Backup cross-Region copy is the distractor when the stem says minutes rather than daily.
- "Windows file shares" or "SMB" maps to Amazon FSx, never EFS.
- "throughput should grow with the amount of data stored" maps to Bursting.

## Knowledge check

### 1. Sizing shared storage for an unpredictable workload (Associate)

A genomics startup runs a batch pipeline on an Auto Scaling group of EC2 instances spread across three Availability Zones. Every instance must read and write the same working directory. The dataset is between 8 TB and 300 TB depending on how many studies are running, and the team cannot forecast the next quarter. They do not want to plan capacity or run a resize procedure.

Which solution will meet these requirements?

- **A)** Provision a 300 TB gp3 EBS volume, attach it to one instance, and export it over NFS to the other instances.
- **B)** Create an EBS volume per instance, size each at 100 TB, and use Amazon EBS Elastic Volumes with a CloudWatch alarm to grow them when usage passes 80 percent.
- **C)** Create a Regional Amazon EFS file system with Elastic throughput, create a mount target in each Availability Zone, and mount it on every instance.
- **D)** Create an Amazon EFS One Zone file system with Bursting throughput and mount it on every instance through its single mount target.

<details><summary>Answer</summary>

**Answer: C.** A Regional EFS file system has no provisioned capacity, grows and shrinks with the data, and is mounted concurrently from every Availability Zone through a mount target in each one, which removes both the sizing decision and the resize procedure. A buys the peak permanently and turns a single instance into a shared point of failure and a throughput bottleneck. B still requires capacity planning and a resize runbook, an EBS volume cannot shrink, and per-instance volumes do not give the instances a shared directory at all. D stores the data in a single Availability Zone, so instances in the other two pay cross-Availability-Zone charges and lose access if that zone fails, and Bursting ties throughput to stored bytes rather than to demand.

*Where this is covered: What Amazon EFS is, and when storage auto scaling is required.*

</details>

### 2. Seven years of rarely read output (Associate)

An engineering firm keeps 180 TB of simulation results on a Regional Amazon EFS file system that uses Elastic throughput. Analysts read results heavily for about a month, then a few times per quarter for a year, then almost never. Regulation requires the results stay available in the same directory tree for seven years. The firm wants the lowest storage cost without changing any application paths.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Configure an EFS lifecycle configuration that transitions into IA after 30 days and into Archive after 365 days, and leave transition into Standard set to none.
- **B)** Switch the file system to Provisioned throughput and configure a lifecycle configuration that transitions into Archive after 30 days.
- **C)** Use AWS DataSync to copy results older than 30 days into Amazon S3 Glacier Deep Archive and delete them from the file system.
- **D)** Create a One Zone EFS file system, replicate the results into it, and configure a lifecycle configuration that transitions into Archive after 90 days.

<details><summary>Answer</summary>

**Answer: A.** Lifecycle transitions move files between Standard, IA and Archive inside one namespace, so no application path changes, and the 30-day and 365-day steps match the described access pattern. B is wrong twice: Archive requires Elastic throughput, so a file system with an Archive policy cannot move to Provisioned, and a 30-day Archive transition would hit data still being read each quarter, paying tiering and access charges repeatedly. C moves the data out of the file system, so the directory tree the regulation names no longer holds it. D breaks the requirement in two ways, because a One Zone file system does not support the Archive storage class and moving the data there reduces durability without being asked to.

*Where this is covered: Storage classes and lifecycle management.*

</details>

### 3. A file system that will not mount (Associate)

A company launches EC2 instances in two private subnets in different Availability Zones and mounts a new Regional Amazon EFS file system using its DNS name. The instances in the first Availability Zone mount successfully. The instances in the second Availability Zone hang and eventually time out with no specific error. The company wants both Availability Zones working.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Attach an Elastic IP address to the mount target in the second Availability Zone.
- **B)** Create a mount target in a subnet of the second Availability Zone.
- **C)** Enable Max I/O performance mode on the file system.
- **D)** Add an inbound rule allowing TCP port 2049 from the instance security group to the mount target security group.
- **E)** Create a second EFS file system in the second Availability Zone and replicate to it.

<details><summary>Answer</summary>

**Answer: B and D.** A Regional file system needs a mount target in each Availability Zone it serves, and the DNS name resolves to the mount target in the client's own zone, so a missing mount target produces exactly this timeout. The mount target security group must also allow inbound TCP 2049 from the client security group, which is the other cause of a silent hang. A is impossible, because mount targets never carry public IP addresses. C changes the metadata engine, not reachability, and AWS recommends General Purpose mode in any case. E builds a separate file system whose contents lag the original and does not give the second zone access to the shared data.

*Where this is covered: Mount targets, access points and the security path.*

</details>

### 4. Encrypting a file system that already exists (Associate)

An audit finds that a production Amazon EFS file system created through the AWS CLI two years ago is not encrypted at rest. It holds 12 TB of data and is mounted by an application that can tolerate a short maintenance window. The company must encrypt the data with a customer managed AWS KMS key and wants the least operational overhead.

Which solution will meet these requirements?

- **A)** Attach a file system policy that requires `aws:SecureTransport`, and remount all clients with the `tls` option.
- **B)** Modify the file system to enable encryption at rest and select the customer managed key.
- **C)** Create an AWS Backup plan for the file system and enable encryption on the backup vault with the customer managed key.
- **D)** Create a new EFS file system encrypted with the customer managed key, use EFS replication to copy the data into it, then repoint the clients during the maintenance window.

<details><summary>Answer</summary>

**Answer: D.** Encryption at rest is fixed when a file system is created and cannot be changed afterward, so the documented remedy is a new encrypted file system with the data copied across, and replication does that copy with no infrastructure to manage. A encrypts data in transit only, which does not address the audit finding about data at rest. B describes an operation EFS does not offer. C encrypts the backup copy, while the 12 TB in the live file system remains unencrypted.

*Where this is covered: Mount targets, access points and the security path.*

</details>

### 5. A cross-Region recovery target measured in minutes (Professional)

A publisher runs a content management application on ECS tasks in us-east-1 that share a Regional Amazon EFS file system holding 40 TB of assets. Business continuity requires a recovery point objective of 15 minutes and the ability to resume writes in us-west-2 within an hour. The team also wants editors in us-west-2 to read assets locally in normal operation, and refuses to run replication servers.

Which solution will meet these requirements?

- **A)** Create a daily AWS Backup plan with a cross-Region copy to us-west-2 and restore the most recent recovery point during a failover.
- **B)** Configure EFS replication from the us-east-1 file system to a destination file system in us-west-2, have us-west-2 editors mount the destination read-only, and delete the replication configuration to fail over.
- **C)** Run AWS DataSync on a 15-minute schedule from the us-east-1 file system to a file system in us-west-2 and mount the destination read-write in both Regions.
- **D)** Create a One Zone file system in us-west-2 and use an hourly AWS Backup copy job, then restore into it when a failover is declared.

<details><summary>Answer</summary>

**Answer: B.** EFS replication is continuous, managed, designed for an RPO of 15 minutes, keeps the destination readable while replication runs, and is failed over by deleting the replication configuration, which makes the destination writable in minutes. A cannot meet a 15-minute RPO from a daily backup, and restoring 40 TB is unlikely to finish within an hour. C requires DataSync task scheduling and agent management the team refused, the minimum schedule granularity works against a 15-minute RPO on a large file system, and a destination mounted read-write invites conflicting writes. D combines a backup cadence that misses the RPO with a single-Availability-Zone target that weakens the recovery site.

*Where this is covered: Replication, backup and the limits that bite.*

</details>

### 6. One file system, many teams, many accounts (Professional)

A platform team owns a Regional Amazon EFS file system in a shared services account. Twelve application teams, each running Lambda functions and ECS tasks from their own accounts, must use it. Each team must see only its own subtree, must write files owned by a per-team POSIX identity regardless of what the client asserts, and must not be able to reach the file system except over TLS. The platform team wants central enforcement rather than instructions to each team.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create one EFS access point per team with an enforced root directory and an enforced POSIX user ID and group ID, and grant each team's role access only to its own access point.
- **B)** Create one file system per team in the shared services account and use EFS replication to keep the twelve copies synchronized.
- **C)** Give each team a dedicated mount target and apply a per-team security group to it.
- **D)** Ask each team to mount with the `tls` option and to set `umask` values that produce the correct file ownership.
- **E)** Attach a file system policy that denies `elasticfilesystem:ClientMount` and `ClientWrite` when `aws:SecureTransport` is false, and that requires access through a named access point ARN.

<details><summary>Answer</summary>

**Answer: A and E.** Access points enforce both the root directory and the POSIX identity server-side, overriding whatever the client claims, and a file system policy is the central control that rejects non-TLS connections and any path that does not go through an approved access point. B creates twelve divergent copies of what is meant to be one shared dataset and multiplies cost and sync lag. C cannot work, because EFS allows only one mount target per Availability Zone and security groups gate network reachability rather than directory scope or file ownership. D relies on every team configuring its own clients correctly, which is exactly the delegation the platform team rejected, and `umask` does not enforce ownership.

*Where this is covered: Mount targets, access points and the security path.*

</details>

## Summary

Amazon EFS is the service to reach for when more than one Linux client must share a POSIX directory tree, and the reason it answers cost and scaling questions at the same time is that it has no capacity to provision. The first decision is the file system type: Regional across three or more Availability Zones for anything that must survive a zone failure, One Zone for reproducible or already-backed-up data. The second is throughput mode, where Elastic is the default and the right answer for spiky or unforecastable demand, Provisioned suits a measured steady requirement, and Bursting ties throughput to the bytes held in Standard storage and eventually runs out of credits. The third is the lifecycle configuration, which moves cold files to IA after a month and to Archive after a quarter without moving them in the namespace, subject to Archive requiring a Regional file system on Elastic throughput. The fourth is the access path: a mount target per Availability Zone inside one VPC, security groups on TCP 2049, access points for per-team root directories and POSIX identities, a file system policy for TLS and IAM authorization, and encryption at rest chosen at creation because it cannot be added later. Replication covers the Region, and AWS Backup covers the mistake.

## Related units

- [Amazon EBS](ebs.md): the block storage alternative, and the provisioned capacity model EFS is contrasted with
- [Amazon S3](s3.md): object storage, storage classes and the lifecycle model EFS lifecycle policies echo
- [Amazon FSx](fsx.md): the answer whenever the stem says SMB, Windows, Lustre or NetApp ONTAP
- [Backup and disaster recovery](backup-and-disaster-recovery.md): AWS Backup plans and vaults, and where EFS replication sits among the DR strategies
- [AWS Transfer Family and AWS DataSync](transfer-family-and-datasync.md): moving on-premises NFS data into an EFS file system
- [Amazon VPC](../04-networking/vpc.md): subnets, security groups and the peering or Transit Gateway path a cross-VPC mount needs
- [AWS KMS and AWS CloudHSM](../07-security/kms-and-cloudhsm.md): customer managed keys, key policies and the `kms:ViaService` condition for encrypted file systems
- [Amazon EKS](../03-containers/eks.md): the EFS CSI driver and persistent shared volumes for pods
- [AWS Lambda](../02-compute/lambda.md): attaching an EFS access point to a function for shared state beyond the deployment package

## Sources

- [Amazon EFS performance specifications](https://docs.aws.amazon.com/efs/latest/ug/performance.html): the performance table by file system type and throughput mode, latency figures, the default and increasable IOPS numbers, Max I/O restrictions, burst credit arithmetic and the 24-hour Provisioned throughput rule
- [Features of Amazon EFS](https://docs.aws.amazon.com/efs/latest/ug/features.html): Regional and One Zone durability and availability, the storage class comparison table, the 128 KiB minimum billable file, the 90-day Archive minimum and the storage class billing rules
- [How Amazon EFS works](https://docs.aws.amazon.com/efs/latest/ug/how-it-works.html): NFSv4.0 and 4.1 support, one mount target per Availability Zone, DNS resolution to the local zone, and on-premises access over Direct Connect and Site-to-Site VPN
- [Managing mount targets](https://docs.aws.amazon.com/efs/latest/ug/accessing-fs.html): mount targets per Availability Zone, the single mount target on One Zone file systems, and the cross-Availability-Zone data access charge
- [Managing file system throughput](https://docs.aws.amazon.com/efs/latest/ug/managing-throughput.html): Elastic as the console default, that changing mode causes no downtime, and the 24-hour wait after moving to Provisioned
- [Managing storage lifecycle](https://docs.aws.amazon.com/efs/latest/ug/lifecycle-management-efs.html): the three lifecycle policies, the internal last-access timer, metadata staying in Standard, and writes landing in Standard for 24 hours
- [Configuring lifecycle policies](https://docs.aws.amazon.com/efs/latest/ug/enable-lifecycle-management.html): the 30-day IA and 90-day Archive defaults and the `put-lifecycle-configuration` syntax
- [EFS LifecyclePolicy API reference](https://docs.aws.amazon.com/efs/latest/ug/API_LifecyclePolicy.html): the valid transition values and `AFTER_1_ACCESS` for transition into Standard
- [Working with access points](https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html): access points requiring a mount target, security groups applying at the mount target, and the `AccessedViaMountTarget` condition key
- [Enforcing a root directory with an access point](https://docs.aws.amazon.com/efs/latest/ug/enforce-root-directory-access-point.html): the 100-character path limit, four subdirectory levels, and automatic root directory creation
- [Using IAM to control access to file systems](https://docs.aws.amazon.com/efs/latest/ug/iam-access-control-nfs-efs.html): the three client actions, the condition keys, and the default policy granting full access to any client that reaches a mount target
- [Encrypting data at rest](https://docs.aws.amazon.com/efs/latest/ug/encryption-at-rest.html): console default compared with CLI and API, that encryption cannot be changed after creation, AES-256, and the `elasticfilesystem:Encrypted` condition key
- [Blocking public access to EFS file systems](https://docs.aws.amazon.com/efs/latest/ug/access-control-block-public-access.html): what makes a file system policy non-public
- [Replicating EFS file systems](https://docs.aws.amazon.com/efs/latest/ug/efs-replication.html): the 15-minute RPO and its exceptions, the non-point-in-time model, and `TimeSinceLastSync`
- [Replicating EFS file systems across AWS accounts](https://docs.aws.amazon.com/efs/latest/ug/cross-account-replication.html): the customer IAM role requirement and that the service-linked role is not permitted
- [Using the replica](https://docs.aws.amazon.com/efs/latest/ug/replication-fail-over.html): failing over by deleting the replication configuration, and failback in either direction
- [Amazon EFS quotas](https://docs.aws.amazon.com/efs/latest/ug/limits.html): file systems per account, access points per file system, connections, mount targets per VPC, the per-client throughput caps, maximum file size and the 16 group ID NFS truncation
- [Amazon EFS document history](https://docs.aws.amazon.com/efs/latest/ug/document-history.html): Elastic replacing Bursting as the default in April 2023, the Archive storage class in November 2023, and cross-account replication in November 2024
- [Amazon EFS FAQs](https://aws.amazon.com/efs/faq/): Archive being supported on Regional file systems using Elastic throughput, the IA and Archive cost comparisons, EFS Intelligent-Tiering, and the read-only replica
- [Amazon EFS pricing](https://aws.amazon.com/efs/pricing/): the billing shape per storage class, Elastic billed on data read and written, Provisioned billed above the Standard baseline, tiering and access charges, and cross-Availability-Zone and cross-Region transfer
