# Amazon FSx

**Where it sits on the exams.** **Amazon FSx** is a family of fully managed file systems that run four third-party file system engines for you: Windows File Server, NetApp ONTAP, OpenZFS and Lustre. It exists so that an application which already speaks SMB, NFS, iSCSI or the Lustre client can move to AWS without a rewrite, and so that a workload needing more throughput than a general-purpose file system can deliver has somewhere to go. FSx is a selection topic rather than a configuration topic: it appears in SAA-C03 tasks 2.1, 3.1 and 4.1, and in SAP-C02 tasks 2.5 and 4.3. The rule of thumb the exam wants is that the protocol the application already speaks, not the performance number, narrows the choice first, and the availability requirement narrows it second.

## What Amazon FSx is and the four-way choice

Every FSx file system is a managed set of file servers and storage that AWS provisions, patches, monitors and replaces inside your **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated network where your AWS resources run. You reach it over an elastic network interface with a DNS name, from **Amazon Elastic Compute Cloud (Amazon EC2)** instances, containers, or from on premises over **AWS Direct Connect**, the dedicated private network link to AWS, or a VPN. Every file system encrypts data at rest with **AWS Key Management Service (AWS KMS)**, the managed service for creating and controlling encryption keys, and encrypts data in transit when accessed from supported instances. That much is common to all four, so it never decides a question.

What decides a question is the table below. Read it in column order, left to right: the protocol column eliminates most options outright, the use case column confirms the survivor, and the last three columns break ties when a stem adds a requirement about S3, about Availability Zone failure, or about retention.

| File system | Protocols | Use case it wins | S3 integration | Multi-AZ | Backup |
|---|---|---|---|---|---|
| FSx for Windows File Server | SMB, versions 2.0 to 3.1.1 | Windows file shares, home directories, content management, SQL Server, anything needing NTFS permissions and Active Directory identities | None. Copy data in and out with **AWS DataSync**, the managed data transfer service | Yes. Single-AZ 1, Single-AZ 2 and Multi-AZ; failover typically under 30 seconds | Automatic daily and user-initiated, file-system-consistent through Volume Shadow Copy Service, incremental |
| FSx for Lustre | Lustre client on Linux only, POSIX-compliant | High performance computing, machine learning training, media rendering, financial modeling; sub-millisecond latency at multiple TBps | Native and bidirectional. Link an S3 bucket as a data repository and its objects appear as files, loaded on first read | No. Every Lustre file system takes exactly one subnet | Persistent file systems only, and only when not linked to an S3 data repository. Never on scratch |
| FSx for NetApp ONTAP | NFS, SMB, iSCSI and NVMe, with concurrent NFS and SMB on one volume | Mixed Linux and Windows estates, lift and shift of on-premises ONTAP, shared block LUNs, petabyte namespaces | S3 access points attach to a volume and serve the file data through S3 object operations | Yes. Single-AZ 1 and 2, Multi-AZ 1 and 2; failover typically under 60 seconds | Automatic daily and user-initiated volume backups, plus ONTAP snapshots and SnapMirror replication |
| FSx for OpenZFS | NFS only, versions 3, 4.0, 4.1 and 4.2 | Linux NFS shares moving off on-premises ZFS or Linux file servers, near-instant snapshots and zero-capacity clones for development and test | S3 access points attach to a volume and serve the file data through S3 object operations | Yes. Multi-AZ (HA), Single-AZ (HA) and Single-AZ (non-HA); failover typically within 60 seconds | Automatic daily and user-initiated, plus near-instant local snapshots on the file system |

Two cells in that table are where candidates lose marks. OpenZFS is reachable from Windows and macOS clients, but only over NFS, so a stem that says Windows users must keep their NTFS access control lists and their domain identities is never OpenZFS. And Lustre has no Multi-AZ deployment type at all, whatever its storage class replicates internally, so a requirement for continuous availability through the loss of an Availability Zone rules Lustre out before any performance number is read.

## The SMB answer: Windows File Server and the Active Directory requirement

FSx for Windows File Server is a real Windows Server file system, which is why it is the answer whenever a stem mentions NTFS permissions, Distributed File System (DFS) namespaces, Windows shares or a domain. Joining it to a directory is not optional. You join it either to **AWS Directory Service for Microsoft Active Directory**, also called AWS Managed Microsoft AD, which is an actual Microsoft Active Directory domain run by AWS, or to a self-managed Active Directory you operate in AWS or on premises. AD Connector and Simple AD are not supported, so an option pairing the file system with either of those is wrong no matter how sensible the rest of it reads.

Sizing is three independent dials: storage capacity, storage type and throughput capacity, with SSD IOPS as a fourth on SSD file systems. SSD storage suits latency-sensitive work such as databases and media processing; HDD storage suits home directories and departmental shares and starts at 2,000 GiB against 32 GiB for SSD. A single file system holds up to 64 TiB, capacity can be increased but never decreased, and each increase must be at least 10 percent. Data Deduplication is the cost lever most often missed: it stores duplicated portions of the dataset once and compresses what remains, with AWS citing typical savings of 50 to 60 percent on general-purpose file shares and 70 to 80 percent on software development datasets. For a namespace larger than one file system can hold, DFS Namespaces stitch several file systems into a single share path.

Multi-AZ is the deployment type for production. It provisions a standby file server in a second Availability Zone, keeps the DNS name constant, and fails over in under 30 seconds, which Windows clients follow automatically. Linux clients do not follow the DNS-based failover automatically, which is a genuine constraint rather than trivia.

## The NFS answers: OpenZFS against NetApp ONTAP

Both of these serve NFS, so a stem that says only "NFS file share" does not separate them. Three things do.

The first is protocol breadth. ONTAP serves NFS, SMB, iSCSI and NVMe, and a single volume can be accessed concurrently over NFS and SMB with either UNIX or NTFS security style. OpenZFS serves NFS and nothing else. So a requirement for Windows clients with domain identities alongside Linux clients on the same data, or for a block LUN presented to a database, is ONTAP. A requirement for Linux NFS clients only is either, and cost then decides.

The second is data management. ONTAP brings the NetApp feature set: thin-provisioned volumes inside storage virtual machines, compression, compaction and deduplication that AWS says save up to 65 percent on general file shares, SnapMirror for scheduled replication to another file system or Region, FlexCache for low-latency caching of a remote volume, and SnapLock write-once-read-many retention in Compliance and Enterprise modes. Its storage model is two tiers: a provisioned SSD tier for the active data, and a fully elastic capacity pool tier that scales to petabytes, with a per-volume tiering policy and cooling period deciding what moves down. OpenZFS brings a smaller but sharper set: near-instant point-in-time snapshots held on the file system itself and data cloning that creates a writable copy consuming no capacity until it diverges, which is why it wins development and test scenarios where dozens of environments must branch from one dataset.

The third is the availability ladder. ONTAP offers Single-AZ and Multi-AZ, with active and standby servers in separate fault domains even in the Single-AZ form. OpenZFS offers three levels: Multi-AZ (HA) with a copy of the data in each Availability Zone, Single-AZ (HA) with a standby in the same zone that fails over in about 60 seconds, and Single-AZ (non-HA) that self-heals in about 30 minutes. That middle rung is useful when a stem wants protection from a server failure but explicitly rejects the cost of crossing zones.

## The throughput answers: Lustre and Amazon File Cache

FSx for Lustre is the answer whenever a stem combines a large dataset already in **Amazon Simple Storage Service (Amazon S3)**, the object storage service, with a compute fleet needing a POSIX file interface and far more aggregate throughput than a general-purpose file system gives. Linking a bucket as a data repository makes its objects appear as files immediately, contents loading on first access, with changes exportable back. That link is why Lustre appears in machine learning and HPC questions: the durable copy stays in S3 and the file system is the fast working surface over it.

Two choices then follow. Scratch file systems do not replicate data or replace a failed server, making them the cost-optimized choice for a job running for hours whose input can be reloaded from S3. Persistent file systems replicate data and replace failed servers automatically, which a long-running or availability-sensitive workload needs. The storage class is a separate dial: SSD gives sub-millisecond latency across the dataset; Intelligent-Tiering is elastic, bills for what you store and tiers to Infrequent Access after 30 days and Archive Instant Access after 90; HDD gives consistent single-digit-millisecond latency at lower cost. One backup rule decides exam questions on its own: backups exist only on persistent file systems not linked to an S3 data repository, because a linked bucket is the durable copy.

**Amazon File Cache** is the same Lustre engine used differently: a temporary high-speed cache, not a file system of record, presenting up to eight linked data repositories as one namespace. Those repositories are either all S3 buckets or all NFSv3 file systems, which may be on premises, so File Cache is what a stem describes when dispersed datasets across several locations must appear to a cloud fleet as one directory tree at sub-millisecond latency. Data loads on first access and is evicted as the cache fills. Capacity is 1.2 TiB, 2.4 TiB or increments of 2.4 TiB, with throughput of 1,000 MBps per TiB. The linked repository holds the durable copy, so the cache is not the thing you protect.

## What each one costs and where the family loses

All four bill provisioned storage per GB-month and separate throughput from capacity, so a small file system can still be fast. Windows File Server adds provisioned throughput capacity and SSD IOPS above the included level. ONTAP bills SSD capacity, SSD IOPS above three per GB, throughput capacity, capacity pool consumption and requests, and backup storage, which is why its elastic tier is both the cost saver and the bill surprise when access patterns change. Lustre and OpenZFS bill provisioned capacity and throughput on SSD and HDD, and data stored plus requests on their elastic tiers.

The family also loses cleanly, and knowing where is worth as much as knowing where it wins. If the application speaks NFS, runs only on Linux, needs no special features and wants least operational overhead, **Amazon Elastic File System (Amazon EFS)**, the serverless elastic NFS file system, is simpler and cheaper, because it provisions no capacity or throughput at all. If the application can address objects rather than files, S3 is cheaper by a wide margin. If one instance needs one fast disk, that is **Amazon Elastic Block Store (Amazon EBS)**. FSx earns its place when a protocol, a performance ceiling or a vendor feature set rules those three out.

## Professional depth

At organization scale the first constraint is identity rather than storage. A Windows File Server file system in a workload account can join a shared AWS Managed Microsoft AD in a central identity account, or a self-managed domain reached over Direct Connect, and the directory configuration is largely immutable: the domain name, organizational unit and administrators group cannot be changed afterwards. Changing them means restoring a backup into a new file system, which turns an apparently small governance change into a migration.

Backup is where the family converges. **AWS Backup**, the centralized backup service, supports all four file systems with cross-Region and cross-account copy, so one organization-wide plan with a copy rule into an isolated backup account replaces four per-service schedules. That is the keyed answer whenever a stem asks for centralized, auditable protection across accounts. What FSx adds beyond it is replication rather than backup: SnapMirror gives ONTAP scheduled incremental replication to another Region for a far lower recovery time objective (RTO) and recovery point objective (RPO) than a restore, and SnapLock gives write-once retention on the volume itself.

Failure modes cluster around deployment types chosen once and never changeable. An ONTAP file system's deployment type is fixed at creation, so Single-AZ to Multi-AZ means a new file system and a data move by SnapMirror, DataSync or restore; the same immutability applies to the Lustre deployment type and storage class. The second is ONTAP's tiering threshold: capacity pool reads stop being cached in the SSD tier at 90 percent SSD utilization and all tiering stops at 98 percent, so a file system that looked cheap because most data sat in the capacity pool degrades sharply as the active dataset grows.

The Professional version of an Associate question adds accounts and a second Region. The Associate form asks which file system serves a Windows share; the Professional form asks how 30 accounts keep Windows, ONTAP and Lustre file systems encrypted with customer managed keys, backed up centrally with a second-Region copy, provably retained for seven years, and reachable from on premises without the internet. The answer combines an organization backup plan with vault lock, customer managed KMS keys shared to the backup account, Direct Connect or VPN, and SnapMirror only where the RTO is too tight for a restore.

## Worked scenario

A genomics company runs three workloads. Research runs sequencing pipelines on several hundred EC2 instances, reading a 60 TB reference dataset already in S3 and writing results back; runs last six to ten hours and only speed matters. A Windows estate serves 400 staff with home directories and departmental shares, against an on-premises Active Directory already extended into AWS, and records rules require shares to survive losing an Availability Zone. A third group runs a Linux analytics application over NFS on an aging on-premises ZFS server, and wants a business intelligence tool speaking the S3 API to read the same files without a copy.

The pipeline gets an FSx for Lustre scratch file system linked to the S3 bucket as a data repository. Objects appear as files and load on first read, the fleet mounts them with the Lustre client, and results export back to S3 before the file system is deleted. Scratch is correct precisely because the data is not at risk: S3 holds the durable copy, and a persistent file system would buy replication this workload does not need. Backups are unavailable here anyway, because the file system is linked to an S3 data repository.

The Windows estate gets a Multi-AZ FSx for Windows File Server joined to the existing self-managed Active Directory, with HDD storage and Data Deduplication, the profile those two are priced for. Multi-AZ meets the Availability Zone requirement with failover behind an unchanged DNS name. The analytics group gets a Multi-AZ FSx for OpenZFS file system mounted over NFS, with an S3 access point on the volume so the business intelligence tool reads the same files through S3 object operations while the data stays on the file system. One AWS Backup plan with a cross-Region copy rule covers all three.

The exam asks this two ways. For the pipeline most cost-effectively, the key is a Lustre scratch file system linked to the bucket; the distractor is a persistent file system, which meets the requirement but pays for durability S3 already provides. For the analytics files reaching an S3-API tool with least overhead, the key is an S3 access point on the OpenZFS volume; the distractor is a scheduled DataSync copy, which creates a second copy that immediately drifts.

## Exam lens

- "SMB", "NTFS permissions" or "joined to a domain" maps to FSx for Windows File Server; only ONTAP also serves SMB.
- "Both Windows and Linux clients need the same data" or "iSCSI LUN" maps to FSx for NetApp ONTAP, the only member with concurrent multiprotocol access.
- "NFS only, replacing an on-premises ZFS server", "instant snapshots" or "zero-capacity clones" maps to FSx for OpenZFS.
- "High performance computing", "machine learning training" or "a dataset already in S3 must be processed as files" maps to FSx for Lustre.
- "Temporary, data can be reloaded from S3" maps to a Lustre scratch file system; persistent is the distractor that over-buys durability.
- "The file system must be backed up" rules out Lustre scratch and any Lustre file system linked to an S3 data repository.
- "Continuous availability if an Availability Zone fails" rules out Lustre and selects a Multi-AZ Windows File Server, ONTAP or OpenZFS.
- "Several on-premises NFS servers and S3 must appear as one namespace to cloud compute" maps to Amazon File Cache, not a file system.
- "Lowest cost for a Windows share of home directories" maps to HDD with Data Deduplication, not a smaller SSD file system.
- "Simple NFS, least operational overhead, no capacity planning" maps to Amazon EFS; OpenZFS is the distractor when the stem names no OpenZFS-specific feature.
- "Recovery time objective in minutes for an ONTAP file system in another Region" maps to SnapMirror replication, not restoring a backup.
- "AD Connector" or "Simple AD" in a Windows File Server option is always wrong; only AWS Managed Microsoft AD and self-managed Active Directory are supported.

## Knowledge check

### 1. Lifting a Windows file estate into AWS (Associate)

A manufacturing company is closing its data center and must move 12 TB of Windows file shares to AWS. The shares are used by 600 employees whose identities live in a self-managed Active Directory domain that already extends into AWS over AWS Direct Connect. Users must keep their existing NTFS permissions, and the shares must remain available if a single Availability Zone fails.

Which solution will meet these requirements?

- **A)** Create an Amazon EFS file system with Standard storage and mount it from the Windows servers over NFS.
- **B)** Create an Amazon FSx for OpenZFS Multi-AZ file system and share the volumes to the Windows clients.
- **C)** Create an Amazon FSx for Windows File Server Multi-AZ file system and join it to the self-managed Active Directory domain.
- **D)** Create an Amazon FSx for Lustre persistent file system and mount it from the Windows clients.

<details><summary>Answer</summary>

**Answer: C.** Only FSx for Windows File Server serves SMB with NTFS access control lists and Active Directory authentication, and it can be joined to a self-managed domain as well as to AWS Managed Microsoft AD. Its Multi-AZ deployment type places a standby file server in a second Availability Zone and fails over behind an unchanged DNS name. A is wrong because Amazon EFS serves NFS and carries no NTFS permissions or domain identities. B is wrong because FSx for OpenZFS serves NFS only, so the Windows permission model is lost even though Windows clients can mount it. D is wrong because FSx for Lustre needs the Linux Lustre client and has no Multi-AZ deployment type.

*Where this is covered: The SMB answer: Windows File Server and the Active Directory requirement.*

</details>

### 2. Feeding a training fleet from an S3 dataset (Associate)

A research team trains models on a 40 TB dataset stored in Amazon S3. Each training run uses 300 Amazon EC2 instances for about eight hours, needs a POSIX file interface with sub-millisecond latency, and writes checkpoints that are copied back to S3 when the run ends. Between runs no compute is active. The team wants the lowest cost for the file storage layer.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Create an Amazon FSx for Lustre scratch file system linked to the S3 bucket as a data repository, and delete it when the run ends.
- **B)** Create an Amazon FSx for Lustre Persistent 2 file system linked to the S3 bucket and keep it running between training runs.
- **C)** Create an Amazon FSx for OpenZFS Single-AZ (HA) file system and copy the dataset into it with AWS DataSync before each run.
- **D)** Create an Amazon FSx for Windows File Server Single-AZ file system and copy the dataset into it before each run.

<details><summary>Answer</summary>

**Answer: A.** A scratch file system does not replicate data or replace failed file servers, which makes it the cost-optimized Lustre choice when the durable copy of the data is already in S3 and a failed run can be restarted. Linking the bucket as a data repository presents the objects as files immediately and loads contents on first access, so no separate copy step is needed. B meets the requirement but pays for replication and for idle capacity between runs. C adds a full copy of 40 TB before every run and provisions an NFS file system with no Lustre throughput profile. D is wrong twice: FSx for Windows File Server serves SMB, not a Linux POSIX interface, and it also requires a copy step.

*Where this is covered: The throughput answers: Lustre and Amazon File Cache.*

</details>

### 3. One dataset, two client families, plus a block volume (Associate)

An engineering firm is migrating an on-premises NetApp estate. Linux build servers must read and write a shared dataset over NFS, Windows workstations must access the same dataset with domain identities, and a reporting database needs a shared block device presented over iSCSI. The solution must stay available if an Availability Zone becomes unavailable.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create an Amazon FSx for NetApp ONTAP Multi-AZ file system.
- **B)** Create an Amazon FSx for OpenZFS Multi-AZ file system.
- **C)** Create a storage virtual machine with a volume configured for concurrent NFS and SMB access, and create an iSCSI LUN on the file system.
- **D)** Create one Amazon FSx for Windows File Server file system and one Amazon EFS file system, and keep them synchronized with AWS DataSync.
- **E)** Create an Amazon FSx for Lustre Persistent 2 file system and export it to the Windows workstations over SMB.

<details><summary>Answer</summary>

**Answer: A and C.** FSx for NetApp ONTAP is the only member of the family that serves NFS, SMB and iSCSI, and a single ONTAP volume supports concurrent NFS and SMB access, so one file system satisfies all three client requirements. Its Multi-AZ deployment type places the standby file server in a second Availability Zone. B is wrong because FSx for OpenZFS serves NFS only and cannot present an iSCSI LUN. D creates two copies of the dataset that drift between synchronizations and still provides no block device. E is wrong because FSx for Lustre neither serves SMB nor offers a Multi-AZ deployment type.

*Where this is covered: The NFS answers: OpenZFS against NetApp ONTAP.*

</details>

### 4. A Lustre file system that must be backed up (Associate)

A media company renders animation frames on a Linux compute fleet against an Amazon FSx for Lustre file system. New source assets are created directly on the file system and exist nowhere else. A compliance rule requires a daily backup of the file system retained for 35 days, restorable without restoring the whole render farm.

Which solution will meet these requirements?

- **A)** Use a Lustre scratch file system and enable automatic daily backups on it.
- **B)** Use a Lustre Persistent 2 file system linked to an Amazon S3 bucket as a data repository, and enable automatic daily backups on the file system.
- **C)** Use a Lustre Persistent 2 file system with the Intelligent-Tiering storage class linked to an Amazon S3 bucket, and rely on S3 versioning.
- **D)** Use a Lustre Persistent 2 file system with no linked data repository, and enable automatic daily backups with a 35-day retention period.

<details><summary>Answer</summary>

**Answer: D.** FSx for Lustre supports automatic daily and user-initiated backups only on persistent file systems that are not linked to an S3 data repository, so removing the link is what makes the backup requirement satisfiable. A is wrong because backups are never supported on scratch file systems. B is wrong because a file system linked to an S3 bucket cannot be backed up: AWS treats the bucket as the durable data repository. C compounds the error, since Intelligent-Tiering file systems cannot link to an S3 data repository at all, and S3 versioning would in any case protect only objects that reached the bucket.

*Where this is covered: The throughput answers: Lustre and Amazon File Cache.*

</details>

### 5. Protecting file systems across 30 accounts (Professional)

A financial services group runs FSx for Windows File Server, FSx for NetApp ONTAP and FSx for Lustre persistent file systems across 30 accounts in an AWS Organizations organization. Auditors require one provable backup schedule for every file system, copies held in a separate account in a second AWS Region, and evidence that no administrator can shorten retention. One ONTAP file system holds a trading application with a recovery time objective of 15 minutes in the second Region, which a restore from backup cannot meet.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Configure automatic daily backups on each file system individually and copy them with a scheduled script in each account.
- **B)** Create an AWS Backup organization backup plan with a cross-Region, cross-account copy rule into a locked backup vault in the isolated account.
- **C)** Enable Data Deduplication on every file system so that backup storage consumption falls below the audit threshold.
- **D)** Replace the trading application's file system with an FSx for Lustre Persistent 2 file system in the second Region.
- **E)** Configure NetApp SnapMirror scheduled replication from the trading application's ONTAP file system to an ONTAP file system in the second Region.

<details><summary>Answer</summary>

**Answer: B and E.** AWS Backup supports all four FSx file systems and supports cross-Region and cross-account copy for each, so one organization backup plan with a locked vault gives a single provable schedule and retention that administrators cannot shorten. SnapMirror is the only option that gives incremental, scheduled ONTAP replication to a second Region, which is what a 15-minute recovery time objective needs. A recreates the same schedule 30 times with no central proof and no lock. C reduces storage consumption but provides no schedule, no copy and no retention control. D moves a multiprotocol trading workload onto a Lustre file system that serves neither SMB nor iSCSI and has no Multi-AZ option.

*Where this is covered: Professional depth.*

</details>

### 6. Serving file data to an S3-API analytics tool (Professional)

A retailer runs a Linux analytics application that mounts an NFS file system holding 8 TB of transaction extracts, and the file system must survive the loss of an Availability Zone. A new business intelligence product can only read data through Amazon S3 object operations. The retailer must not maintain a second copy of the extracts, must not modify the analytics application, and wants the least operational overhead.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create an Amazon FSx for Lustre Persistent 2 file system linked to an S3 bucket, and point both the analytics application and the business intelligence product at the bucket.
- **B)** Create an Amazon FSx for OpenZFS Multi-AZ file system, mount it from the analytics application over NFS, and attach an Amazon S3 access point to the volume for the business intelligence product.
- **C)** Create an Amazon FSx for OpenZFS Single-AZ (non-HA) file system and run a scheduled AWS DataSync task that copies the extracts into an S3 bucket for the business intelligence product.
- **D)** Deploy an Amazon FSx File Gateway in front of an Amazon FSx for Windows File Server file system and expose its cache to the business intelligence product.

<details><summary>Answer</summary>

**Answer: B.** An S3 access point attached to an FSx for OpenZFS volume serves the file data through S3 object operations while the data continues to live on the file system, so there is no second copy, no application change, and NFS access continues alongside. The Multi-AZ (HA) deployment type meets the Availability Zone requirement. A is wrong because a Lustre data repository link makes S3 the source of truth and the file system a working copy, and Lustre has no Multi-AZ deployment type. C creates exactly the second, drifting copy the stem forbids and uses a deployment type with no Availability Zone protection. D adds a gateway and switches the protocol to SMB, which the Linux analytics application does not speak.

*Where this is covered: The NFS answers: OpenZFS against NetApp ONTAP.*

</details>

## Summary

Amazon FSx is a selection decision made in a fixed order. Start with the protocol: SMB with Active Directory identities means FSx for Windows File Server; NFS, SMB, iSCSI or NVMe together means FSx for NetApp ONTAP; NFS alone with snapshots and instant clones means FSx for OpenZFS; the Linux Lustre client at HPC throughput means FSx for Lustre. Then apply the availability requirement, which removes Lustre from any scenario naming Availability Zone failure and picks a Multi-AZ deployment type for the other three. Then apply the data requirement: Lustre pulls an S3 bucket into the file system as a data repository, while ONTAP and OpenZFS push file data outward through S3 access points, and Windows File Server does neither. Then apply retention, remembering that Lustre backups exist only on persistent file systems with no S3 link. Amazon File Cache is the separate answer for presenting up to eight dispersed S3 or NFSv3 repositories as one high-speed namespace. Finally, check that FSx is needed at all, because Amazon EFS, Amazon S3 and Amazon EBS are cheaper when no protocol or feature forces the choice.

## Related units

- [Amazon EFS](efs.md): the serverless NFS alternative that wins when no FSx-specific feature is required
- [Amazon S3](s3.md): the data repository Lustre links to and the object API that FSx access points serve
- [Amazon EBS](ebs.md): single-instance block storage, the other half of the storage type decision
- [AWS Storage Gateway](storage-gateway.md): Amazon FSx File Gateway for cached on-premises access to Windows file systems
- [Transfer Family and DataSync](transfer-family-and-datasync.md): moving data into and out of FSx file systems
- [Backup and disaster recovery](backup-and-disaster-recovery.md): AWS Backup plans, vaults and cross-Region copy for all four file systems
- [AWS Directory Service](../07-security/directory-service.md): AWS Managed Microsoft AD and the self-managed domain options FSx for Windows File Server requires
- [Hybrid connectivity](../04-networking/hybrid-connectivity.md): the Direct Connect and VPN paths that reach a file system from on premises

## Sources

- [What is Amazon FSx for Windows File Server?](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/what-is.html): SMB 2.0 to 3.1.1, SSD and HDD storage types, automatic daily backups, Single-AZ and Multi-AZ availability
- [Availability and durability: Single-AZ and Multi-AZ file systems](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/high-availability-multiAZ.html): deployment type feature matrix, sub-30-second failover, Linux client failover behavior, subnet and network interface counts
- [Working with Microsoft Active Directory](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/aws-ad-integration-fsxW.html): AWS Managed Microsoft AD and self-managed AD only, AD Connector and Simple AD unsupported, immutable directory properties
- [Managing storage on FSx for Windows File Server](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/managing-storage-capacity.html): Data Deduplication savings ranges, 10 percent minimum capacity increase, 65,536 GiB maximum
- [Quotas for FSx for Windows File Server](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/limits.html): 32 GiB SSD and 2,000 GiB HDD minimums, 64 TiB maximum per file system
- [What is Amazon FSx for Lustre?](https://docs.aws.amazon.com/fsx/latest/LustreGuide/what-is.html): POSIX compliance, SSD, Intelligent-Tiering and HDD storage classes, S3 data repository integration
- [Deployment and storage class options for FSx for Lustre](https://docs.aws.amazon.com/fsx/latest/LustreGuide/using-fsx-lustre.html): scratch compared with Persistent 1 and Persistent 2, Intelligent-Tiering tier transitions at 30 and 90 days
- [Performance characteristics of the Intelligent-Tiering storage class](https://docs.aws.amazon.com/fsx/latest/LustreGuide/intelligent-tiering-file-systems.html): elastic regional storage and the optional SSD read cache
- [Using data repositories with Amazon FSx for Lustre](https://docs.aws.amazon.com/fsx/latest/LustreGuide/fsx-data-repositories.html): S3 link behavior, and that Intelligent-Tiering file systems cannot link to S3
- [Protecting your data with backups, FSx for Lustre](https://docs.aws.amazon.com/fsx/latest/LustreGuide/using-backups-fsx.html): backups on persistent file systems only, and never when linked to an S3 data repository
- [What is Amazon FSx for NetApp ONTAP?](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/what-is-fsx-ontap.html): NFS, SMB, iSCSI and NVMe support, Multi-AZ and Single-AZ options, SnapMirror, FlexCache and SnapLock
- [Availability and durability for FSx for ONTAP](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/high-availability-AZ.html): Single-AZ and Multi-AZ generations, sub-60-second failover, immutable deployment type
- [Managing storage capacity for FSx for ONTAP](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/managing-storage-capacity.html): SSD tier and capacity pool tier, tiering thresholds at 90 and 98 percent, storage efficiency savings
- [Managing FSx for ONTAP volumes](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/managing-volumes.html): thin provisioning, concurrent NFS and SMB access, iSCSI LUNs, tiering policies and security styles
- [Accessing your data via Amazon S3 access points, FSx for ONTAP](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/accessing-data-via-s3-access-points.html): S3 object operations against ONTAP volumes alongside NFS and SMB
- [What is Amazon FSx for OpenZFS?](https://docs.aws.amazon.com/fsx/latest/OpenZFSGuide/what-is-fsx.html): NFS v3 through v4.2 only, the three availability levels, snapshots and cloning, storage classes
- [Accessing your data using Amazon S3 access points, FSx for OpenZFS](https://docs.aws.amazon.com/fsx/latest/OpenZFSGuide/s3accesspoints-for-FSx.html): read and write S3 object operations against an OpenZFS volume
- [What is Amazon File Cache?](https://docs.aws.amazon.com/fsx/latest/FileCacheGuide/what-is.html): up to eight linked S3 or NFSv3 repositories of one type, CACHE_1 deployment, Lustre client access
- [Cache eviction in Amazon File Cache](https://docs.aws.amazon.com/fsx/latest/FileCacheGuide/cache-eviction.html): automatic eviction and the requirement to export before release
- [Step 1: Create your cache](https://docs.aws.amazon.com/fsx/latest/FileCacheGuide/getting-started-step1.html): 1.2 TiB, 2.4 TiB and 2.4 TiB increments, throughput of 1,000 MBps per TiB
- [CreateFileSystem API reference](https://docs.aws.amazon.com/fsx/latest/APIReference/API_CreateFileSystem.html): exactly two subnets for Windows and ONTAP Multi-AZ, exactly one subnet for all Lustre deployment types
- [AWS Backup feature availability](https://docs.aws.amazon.com/aws-backup/latest/devguide/backup-feature-availability.html): cross-Region and cross-account backup copy support for all four FSx file systems
- [Amazon FSx product page](https://aws.amazon.com/fsx/): the four file systems in the family and the selection framing AWS uses
