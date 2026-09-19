# AWS Storage Gateway

**Where it sits on the exams.** **AWS Storage Gateway** is the hybrid storage service: a virtual appliance in your data center, on a hardware appliance, or on an **Amazon Elastic Compute Cloud (Amazon EC2)** instance, the service that rents virtual servers by the second, presents a familiar on-premises storage protocol while the data lives in AWS. Every gateway caches recently used data on local disk and uploads asynchronously, so an application nobody will rewrite keeps speaking NFS, SMB or iSCSI while the capacity behind it becomes **Amazon Simple Storage Service (Amazon S3)**, the object storage service. Storage Gateway owns the hybrid storage bullet in SAA-C03 task 3.1, supports tasks 3.5 and 4.1, and carries SAP-C02 task 4.3, which names Volume Gateway. Pick the type by the protocol the application already speaks, then the mode by where the primary copy has to live.

## What Storage Gateway is and how the four types differ

One appliance runs one gateway type. You deploy a virtual machine image on VMware ESXi, Microsoft Hyper-V, Linux Kernel-based Virtual Machine or Nutanix AHV with four virtual processors, 16 GiB of reserved RAM and 80 GiB of disk, then activate it against a Region over at least 100 Mbps.

The four types split along the protocol they speak locally. **Amazon S3 File Gateway** serves Network File System (NFS) versions 3 and 4.1 and Server Message Block (SMB) versions 2 and 3, turning files into S3 objects. **Amazon FSx File Gateway** serves SMB and caches shares in **Amazon FSx for Windows File Server**, the managed Windows file system. **Volume Gateway** serves Internet Small Computer System Interface (iSCSI) block volumes. **Tape Gateway** serves a virtual tape library over iSCSI, so backup software sees tape drives and a media changer. Read the table for the local protocol, what the data becomes in AWS, which side holds the primary copy, and the stem wording that selects each row.

| Gateway type | Local protocol | What lands in AWS | Primary copy | The wording that selects it |
|---|---|---|---|---|
| S3 File Gateway | NFS, SMB | One object per file, in your own bucket | In AWS, hot files cached | "readable by analytics as objects" |
| FSx File Gateway | SMB | Files in an FSx for Windows file system | In AWS, hot files cached | "local access to a Windows share in AWS" |
| Volume Gateway, cached | iSCSI block | Volume data the service holds in S3 | In AWS, hot blocks cached | "reduce the on-premises footprint" |
| Volume Gateway, stored | iSCSI block | EBS snapshots only | On premises, all of it | "whole dataset needs local latency", "recover into EC2" |
| Tape Gateway | iSCSI tape library | Tapes archived to S3 Glacier Flexible Retrieval or Deep Archive | In AWS | "keep the existing backup software" |

Storage Gateway is not a migration tool: a one-time or scheduled copy of a file share belongs to **AWS DataSync**, the managed transfer service for file and object data, covered in [AWS Transfer Family and AWS DataSync](transfer-family-and-datasync.md), which leaves the application reading its local array. A gateway is a cache with a write-back path, so its exam signal is an application that keeps running on premises.

## S3 File Gateway and FSx File Gateway

S3 File Gateway gives an on-premises client a mount point whose contents are an S3 bucket. Files written to the share become objects with the path as the key, one per file, and objects already in the bucket appear as files. A share binds to one bucket, several shares can share a bucket if each uses a non-overlapping prefix, and a gateway supports up to 50 file shares. The largest file is 5 TiB, paths cap at 1,024 bytes and names at 255 bytes. Only the working set stays on the cache disk; a file that is not cached is downloaded from S3 when a client opens it.

Two behaviors decide questions. First, renaming a file or folder, changing permissions, or appending to a file replaces the existing object with a new one, triggering early deletion and retrieval charges on the infrequent access and archive classes. A share can use S3 Standard, S3 Standard-Infrequent Access, S3 One Zone-Infrequent Access or S3 Intelligent-Tiering, and lifecycle policy can move objects to Glacier later, but S3 File Gateway does not support S3 Glacier Instant Retrieval. Second, the gateway keeps a cached inventory of the bucket, so objects written by anything other than the gateway stay invisible to the share until that inventory is refreshed: manually, through the `RefreshCache` API, or by a time to live that resynchronizes a directory the next time a client touches it. The refresh updates the inventory only, not the file data, and the size of the cache disk has no bearing on which objects the gateway knows exist.

FSx File Gateway is the SMB-only sibling: it caches shares from an FSx for Windows File Server file system so a branch office reaches an in-cloud Windows share at local latency, joins your Active Directory domain, and needs a private path over a VPN or **AWS Direct Connect**, the dedicated network connection service. Amazon FSx File Gateway is no longer available to new customers; existing customers keep using it, and AWS directs new deployments to FSx for Windows File Server directly. On the exams a stem about low-latency on-premises access to a Windows share already in FSx still maps to it.

## Volume Gateway: cached compared with stored

Volume Gateway presents iSCSI block devices, and this is the type SAP-C02 task 4.3 names. The only question that matters is which side holds the primary copy. With cached volumes it is in AWS: the service stores all volume data in S3 and the appliance keeps recently used data locally, so the on-premises array shrinks to the working set and anything outside the cache is fetched over the network. With stored volumes it is on premises: the application reads and writes local disks at local latency for the entire dataset, and the gateway asynchronously copies that data to AWS as point-in-time backups.

Read this table for each mode's ceilings and disks: the absence of a cache disk on a stored gateway states where the data actually is.

| | Cached volumes | Stored volumes |
|---|---|---|
| Primary copy | Amazon S3, managed by the service | On-premises disks |
| Volume size | 1 GiB to 32 TiB | 1 GiB to 16 TiB |
| Volumes per gateway | 32 | 32 |
| Total per gateway | 1,024 TiB | 512 TiB |
| Cache disk | 150 GiB minimum, 64 TiB maximum | none |
| Upload buffer | 150 GiB minimum, 2 TiB maximum | 150 GiB minimum, 2 TiB maximum |
| Other local disks | none | one or more holding the volumes themselves |

Both modes back up the same way. Snapshots are incremental and stored as **Amazon Elastic Block Store (Amazon EBS)** snapshots, EBS being the network-attached block storage service for EC2, taken on a gateway-managed schedule or through **AWS Backup**, the central backup service, which covers both cached and stored volumes and also produces EBS snapshots, so on-premises volumes sit in the same backup plans as in-cloud resources. A snapshot can seed a new EBS volume attached to an EC2 instance, the disaster recovery path into AWS. One asymmetry decides questions: a snapshot from a cached volume larger than 16 TiB restores to a Storage Gateway volume but not to an EBS volume, and stored volumes stop at 16 TiB so they never hit it. If a design promises recovery into EC2, keep cached volumes at 16 TiB or less.

Cached volume data lives in S3 storage the service owns, not a bucket you can read with the S3 API or console, so a stem that wants the data queryable as objects selects S3 File Gateway instead.

## Tape Gateway and the virtual tape library

Tape Gateway lets a company retire a physical tape library without replacing the backup software that drives it. Each gateway ships with one virtual tape library of ten virtual tape drives and one media changer presented as iSCSI devices, which supported backup applications drive exactly as physical hardware, with no reconfiguration. Tapes are sized between 100 GiB and 15 TiB, and one gateway holds up to 1,500 tapes or 1 PiB.

The lifecycle mirrors physical tape. The backup application writes to a tape, the gateway uploads it asynchronously, and on eject the tape moves to the archive, the virtual tape shelf. That archive is storage the service manages, not a bucket in your account you could attach a bucket policy to. The tape pool decides the storage class on eject: the Glacier pool archives to **S3 Glacier Flexible Retrieval**, typically retrieved within 3 to 5 hours, the Deep Archive pool to **S3 Glacier Deep Archive**, typically 12 hours and the cheapest archive tier. Archived tapes cannot be read in place; you retrieve one back into the library first.

Compliance requirements are met with a custom tape pool and **tape retention lock**, which stops an archived tape being deleted or moved to another pool for up to 100 years. Governance mode lets a principal holding `storagegateway:BypassGovernanceRetention` remove a tape; compliance mode lets nobody remove it, including the account root user, and neither the lock type nor a shortened retention period can be changed afterward. A custom pool's configuration is fixed once created, so the pool, not the tape, is where the decision is made.

## Sizing, security, monitoring and what you pay for

The two local disk roles differ. Cache storage is the durable local store for data waiting to upload and the low-latency copy of recently accessed data; the upload buffer stages data on its way to AWS. A file gateway needs only cache, from 150 GiB to 64 TiB. A cached Volume Gateway or a Tape Gateway needs both, cache from 150 GiB to 64 TiB and upload buffer from 150 GiB to 2 TiB, with cache kept the larger of the two. Reserved memory scales with cache, 16 GiB up to 16 TiB of cache and 48 GiB at 64 TiB, and on EC2 the instance must be at least `xlarge` on x86 with UEFI boot, not Graviton.

In transit the gateway uses SSL/TLS. At rest it encrypts what it stores in S3 with S3 managed keys by default, or a file share can use a symmetric key in **AWS Key Management Service (AWS KMS)**, the managed key service; asymmetric keys are not supported. For the network path, activate the gateway through an interface endpoint for Storage Gateway inside an **Amazon Virtual Private Cloud (Amazon VPC)**, the logically isolated network service, so activation and control traffic never crosses the public internet; an S3 File Gateway needs a second VPC endpoint for S3 to keep the data path private, and both must be in the gateway's Region. Gateway API calls are authorized by **AWS Identity and Access Management (IAM)**, the AWS permissions service, and logged by **AWS CloudTrail**, the API audit service.

**Amazon CloudWatch**, the AWS monitoring service, receives cache and upload buffer metrics; `CacheHitPercent` and `CachePercentDirty` are the two to watch, a falling hit rate meaning the cache is too small and a rising dirty percentage meaning uploads are not keeping up. Bandwidth rate limits cap upload, and download on Volume and Tape Gateways, on a schedule that can differ by time of day. Pricing is a flat charge per GB written to AWS per gateway, capped monthly, nothing to read data back, plus the underlying storage, which for a file gateway is your own S3 bucket.

## Professional depth

A gateway is a Regional, single-account resource running one gateway type, so a site needing both file and tape access runs two appliances, each billed its own capped write charge. Volume backups cross accounts cleanly: because AWS Backup produces EBS snapshots, on-premises volume backups land in the same vaults, cross-account copies and audit reports as in-cloud resources, usually the keyed answer when a Professional stem asks for one backup policy across cloud and on-premises data.

Pair the Storage Gateway interface endpoint and the S3 endpoint named on a file share with Direct Connect, described in [hybrid connectivity](../04-networking/hybrid-connectivity.md), and one answer satisfies both a "no public internet" constraint and a predictable-bandwidth constraint. Without Direct Connect, bandwidth rate limit schedules keep a gateway from competing with production traffic.

The quotas that bite look generous until a migration hits them. A file gateway caches metadata for a bounded number of files, set by a gateway capacity of Small, Medium or Large for 5 million, 10 million or 20 million files; a larger share still works, but performance degrades. Thirty-two volumes per gateway, and 1,500 tapes or 1 PiB per Tape Gateway, mean that past a certain scale the answer is more appliances.

Failure modes cluster around the asynchronous upload. A write is durable locally once it reaches the cache disk but is not in AWS until it drains from the upload buffer, so a recovery point objective quoted in a stem has to account for upload lag, not just the snapshot schedule. A full upload buffer throttles writes; an undersized cache collapses the hit rate. On S3 File Gateway the rewrite-on-metadata-change behavior interacts badly with the 30 day minimum storage duration of S3 Standard-IA and with versioning, which is why AWS recommends a lifecycle rule expiring non-current versions on a gateway bucket.

## Worked scenario

A geological survey company runs a 300 TB seismic archive in a leased data center. A processing cluster mounts NFS shares and reads roughly 8 TB of recent data a week, and those files must become objects an S3-based analytics pipeline can read directly. A legacy interpretation application writes to iSCSI LUNs on an aging array, holds 40 TB, and must be recoverable into AWS within four hours. Nightly backup sets must be undeletable for seven years, and nothing may cross the public internet from the Direct Connect link in place.

Three appliances cover it. An S3 File Gateway serves the NFS shares from a bucket in S3 Standard, with a lifecycle rule to S3 Standard-IA after 90 days, expiry of non-current versions, a 2 TB cache, a VPC endpoint for S3 on the share, and activation through a Storage Gateway interface endpoint. A cached Volume Gateway serves the interpretation application, with volumes kept at 16 TiB or less so their snapshots can seed EBS volumes, and AWS Backup running a daily plan. A Tape Gateway takes the nightly backup sets from the existing backup software, ejecting into a custom pool on S3 Glacier Deep Archive with compliance mode retention lock set to seven years.

The exam asks which combination meets the requirements. The keyed answer is S3 File Gateway because the data must be readable as objects, a cached Volume Gateway at 16 TiB or less because the recovery target is EC2, and a Tape Gateway with a compliance-mode retention lock pool. The distractors substitute stored volumes, which do not shrink the on-premises footprint, or a governance-mode lock, which an administrator can bypass.

## Exam lens

- "Files written on premises must be readable in AWS as S3 objects" maps to S3 File Gateway; a cached volume is the distractor, because its data is not in a bucket you can read.
- "Keep the existing backup application" or "retire the physical tape library" maps to Tape Gateway.
- "The entire dataset needs low-latency local access, with offsite backup" maps to Volume Gateway stored volumes; "reduce the on-premises footprint while keeping hot data local" maps to cached volumes.
- "Recover the on-premises volumes into EC2" maps to restoring the EBS snapshot, and caps cached volumes at 16 TiB.
- "Least operational overhead for one-time migration of a file share" maps to AWS DataSync; Storage Gateway is the distractor when no ongoing on-premises access is required.
- "Files added to the bucket by another process are not visible on the share" maps to a cache refresh, not to a larger cache disk.
- "No user, not even the root user, may delete a backup for N years" maps to a custom tape pool with compliance mode retention lock. Governance mode is the distractor.
- "Retrieve archived backups within 12 hours at the lowest cost" maps to the Deep Archive tape pool; "within 3 to 5 hours" maps to the Glacier pool.
- "No traffic over the public internet" maps to an interface VPC endpoint for Storage Gateway, plus a separate S3 endpoint named on the file share.

## Knowledge check

### 1. Seismic files that analytics must read (Associate)

A geoscience firm runs a processing application on premises that reads and writes files over NFS. The firm wants to stop expanding its local storage array, wants recently used files to stay fast for the application, and needs a new analytics job running in AWS to read the same data directly as objects.

Which solution will meet these requirements?

- **A)** Deploy a Volume Gateway in cached mode and mount the iSCSI volumes on the processing servers.
- **B)** Deploy an Amazon S3 File Gateway, create an NFS file share backed by an S3 bucket, and point the analytics job at that bucket.
- **C)** Deploy a Tape Gateway and configure the processing application to write nightly tapes into the Glacier pool.
- **D)** Deploy an AWS DataSync agent and schedule an hourly task that copies the local file system to an S3 bucket.

<details><summary>Answer</summary>

**Answer: B.** An S3 File Gateway presents an NFS share whose files become one S3 object each in a bucket the firm owns, so the analytics job reads them through the S3 API while the gateway's local cache keeps recent files fast and the primary copy lives in AWS. A is wrong because cached Volume Gateway data is held by the service inside S3 storage that cannot be read with the S3 API or console, so the analytics job could not reach it. C is wrong because a Tape Gateway serves a backup application through a virtual tape library, not a file system the processing application can mount. D copies data on a schedule but leaves the application reading the local array, so it neither stops the array growing nor keeps a live file interface.

*Where this is covered: S3 File Gateway and FSx File Gateway.*

</details>

### 2. Clinical images that must stay local (Associate)

A hospital stores a 40 TB medical imaging dataset on premises. The clinical application reads every part of the dataset at local disk latency and cannot tolerate a cloud round trip for any image. The hospital also needs offsite copies that can be recovered into AWS if the site is lost, and wants backup retention managed centrally alongside its AWS resources.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Deploy a Volume Gateway in stored volume mode and map the existing on-premises disks to stored volumes.
- **B)** Deploy a Volume Gateway in cached volume mode and create cached volumes totaling 40 TiB.
- **C)** Use AWS Backup with a backup plan targeting the gateway volumes, which produces Amazon EBS snapshots.
- **D)** Deploy an Amazon S3 File Gateway and have the clinical application read images over an SMB file share.
- **E)** Deploy a Tape Gateway and configure the clinical application to eject a tape into the Deep Archive pool each night.

<details><summary>Answer</summary>

**Answer: A and C.** Stored volumes keep the primary copy on the hospital's own disks, so every image is read at local latency, while the gateway asynchronously uploads the data to AWS; AWS Backup then schedules and retains backups of those volumes as EBS snapshots in the same plans that cover the hospital's AWS resources, and a snapshot can seed an EBS volume on EC2 for recovery. B is wrong because cached volumes place the primary copy in AWS and only the working set locally, so images outside the cache would be fetched over the network. D changes the protocol to a file share and still serves cold files from S3, breaking the local-latency requirement for the whole dataset. E archives backup sets for a backup application, which is not how a clinical application reads images.

*Where this is covered: Volume Gateway: cached compared with stored.*

</details>

### 3. Retiring the tape library (Associate)

A logistics company backs up its data center with a commercial backup application that writes to an LTO tape library. The library is at end of life and the company wants to remove it without changing or reconfiguring the backup application. Archived backups must be kept for several years and are read back once or twice a year, where a 12 hour wait is acceptable.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Replace the tape library with an Amazon S3 File Gateway and reconfigure the backup application to write backup files to an SMB share backed by S3 Glacier Instant Retrieval.
- **B)** Replace the tape library with a Volume Gateway in stored mode and schedule nightly snapshots of the backup volumes.
- **C)** Deploy a Tape Gateway, present its virtual tape drives and media changer to the backup application, and eject tapes into a pool that archives to S3 Glacier Deep Archive.
- **D)** Deploy an AWS DataSync agent that copies the backup application's output directory to an S3 bucket with a lifecycle rule to S3 Glacier Deep Archive.

<details><summary>Answer</summary>

**Answer: C.** A Tape Gateway presents ten virtual tape drives and a media changer as iSCSI devices, so the existing backup application keeps its configuration, and ejecting into the Deep Archive pool stores the tape in S3 Glacier Deep Archive, whose typical 12 hour retrieval matches the stated tolerance at the lowest archive price. A is wrong twice: it requires reconfiguring the backup application, and S3 File Gateway does not support the S3 Glacier Instant Retrieval storage class. B keeps the whole backup dataset on local disks, which is the capacity the company is trying to retire, and costs more than archive storage. D also requires the backup application to write to a file system first and to be reconfigured, and it discards the tape workflow the company wants to preserve.

*Where this is covered: Tape Gateway and the virtual tape library.*

</details>

### 4. Objects the share cannot see (Associate)

A publisher runs an Amazon S3 File Gateway whose SMB share is backed by an S3 bucket. A separate AWS data pipeline writes newly rendered assets directly into the same bucket under the same prefix. On-premises editors report that the new assets never appear in the mounted share, although they are present in the bucket. The publisher wants the assets to appear without building a custom synchronization process.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Increase the size of the gateway's local cache disk so it can hold the additional assets.
- **B)** Enable S3 Versioning on the bucket so the gateway detects the new object versions.
- **C)** Create a second file share on the same gateway pointing at the same bucket and prefix.
- **D)** Configure an automated cache refresh on the file share with a time to live suited to the pipeline's write rate.

<details><summary>Answer</summary>

**Answer: D.** The gateway keeps a cached inventory of the bucket, and objects written by anything other than the gateway are invisible to the share until that inventory is refreshed; a time to live setting resynchronizes a directory the next time a client accesses it after the interval expires, which is a console setting rather than a custom process. A is wrong because cache size governs how much file data is held locally for low latency, not which objects the gateway knows exist. B is wrong because versioning records object versions in S3 and does not notify the gateway; AWS in fact recommends expiring non-current versions on a gateway bucket. C is wrong because a second share inherits the same inventory behavior and AWS requires shares on one bucket to use non-overlapping prefixes.

*Where this is covered: S3 File Gateway and FSx File Gateway.*

</details>

### 5. Shrinking an array without losing the failover path (Professional)

A manufacturer runs an application that uses iSCSI LUNs on an aging 120 TB storage array in a colocation facility. The company wants to stop buying array capacity while keeping frequently accessed blocks local. Its disaster recovery plan requires that, within hours of a site failure, the application's volumes be brought up on Amazon EC2 instances and tested twice a year. Corporate policy forbids any data path over the public internet, and an AWS Direct Connect connection is already in place.

Which solution will meet these requirements?

- **A)** Deploy a cached Volume Gateway, create volumes of 16 TiB or less, activate the gateway through an interface VPC endpoint for Storage Gateway reached over Direct Connect, and schedule snapshots of the volumes.
- **B)** Deploy a cached Volume Gateway, create 32 TiB volumes to reduce the number of volumes to manage, activate the gateway through an interface VPC endpoint for Storage Gateway reached over Direct Connect, and schedule snapshots of the volumes.
- **C)** Deploy a stored Volume Gateway against the existing array disks, activate it through an interface VPC endpoint for Storage Gateway reached over Direct Connect, and schedule snapshots of the volumes.
- **D)** Deploy an Amazon S3 File Gateway with an SMB share over Direct Connect and migrate the application to read its data from the share.

<details><summary>Answer</summary>

**Answer: A.** Cached volumes move the primary copy to AWS so the array stops growing while the working set stays local, the interface VPC endpoint keeps activation and control traffic off the internet over the existing Direct Connect link, and volumes kept at 16 TiB or less produce snapshots that can be restored as EBS volumes and attached to EC2 instances for the failover test. B meets every requirement except the last: a snapshot from a cached volume larger than 16 TiB can be restored only to a Storage Gateway volume, not to an EBS volume, so the EC2 recovery test fails. C keeps the entire 120 TB on the array, which is exactly the capacity spending the company wants to end. D replaces block storage with a file share and requires rewriting the application, which the stem does not permit.

*Where this is covered: Volume Gateway: cached compared with stored.*

</details>

### 6. Seven years of untouchable backup sets (Professional)

A regulated insurer uses a Tape Gateway for nightly backups written by its existing backup software. A new mandate requires that every archived backup set be impossible to delete or relocate for seven years, including by an administrator holding full permissions and by the account root user. Auditors read back one or two backup sets a year and accept a retrieval wait of up to half a day. The insurer wants the lowest storage cost that satisfies the mandate.

Which combination of steps will meet these requirements MOST cost-effectively? (Select TWO.)

- **A)** Continue ejecting tapes into the default Glacier pool and attach an S3 bucket policy denying the delete actions.
- **B)** Create a custom tape pool with tape retention lock in compliance mode and a retention period of seven years, and eject tapes into it.
- **C)** Create a custom tape pool with tape retention lock in governance mode and a retention period of seven years, and eject tapes into it.
- **D)** Configure the custom tape pool to archive to S3 Glacier Flexible Retrieval.
- **E)** Configure the custom tape pool to archive to S3 Glacier Deep Archive.

<details><summary>Answer</summary>

**Answer: B and E.** Compliance mode retention lock on a custom tape pool prevents deletion or movement of an archived tape by any principal, including the root user, for the configured period of up to 100 years, and the Deep Archive storage class is the cheapest archive tier while its typical 12 hour retrieval fits the auditors' stated tolerance. A is wrong because tapes are held in service-managed storage rather than a bucket the insurer can attach a policy to, and a policy can be changed by an administrator anyway. C is wrong because governance mode is explicitly bypassable by a principal with the `storagegateway:BypassGovernanceRetention` permission, which the mandate forbids. D meets the retrieval requirement with time to spare but costs more than Deep Archive, so it loses on the stated cost constraint.

*Where this is covered: Tape Gateway and the virtual tape library.*

</details>

## Summary

Storage Gateway answers one question: an application that must keep running on premises needs storage that actually lives in AWS. Choose the type by the protocol the application already speaks. NFS or SMB with the data needed as S3 objects selects S3 File Gateway, which maps one file to one object, caches the working set, and needs a cache refresh when something else writes into the bucket. SMB against a Windows file system already in AWS selects FSx File Gateway, which is closed to new customers but remains the keyed answer on the exams. iSCSI block selects Volume Gateway, and there the second decision is where the primary copy lives: cached puts it in S3 and shrinks the on-premises array, stored keeps the whole dataset on local disks and ships EBS snapshots offsite, and only the stored mode dispenses with a cache disk entirely. Both back up as EBS snapshots through the gateway or AWS Backup, and a cached volume over 16 TiB cannot be restored to EBS. A virtual tape library selects Tape Gateway, with the pool choosing Glacier Flexible Retrieval or Deep Archive and compliance mode retention lock covering a write-once mandate. Size cache and upload buffer from 150 GiB up, keep the path private with VPC endpoints, and remember that you pay per GB written to AWS plus the storage underneath.

## Related units

- [Amazon S3](s3.md): the object store behind S3 File Gateway, its storage classes and lifecycle rules
- [Amazon EBS](ebs.md): snapshots are the format every Volume Gateway backup takes
- [AWS Transfer Family and AWS DataSync](transfer-family-and-datasync.md): the transfer tool comparison and when a gateway is the wrong answer
- [Amazon FSx](fsx.md): FSx for Windows File Server, the file system FSx File Gateway caches
- [AWS Backup and disaster recovery](backup-and-disaster-recovery.md): backup plans, vaults and the DR strategies a gateway supports
- [AWS Snow Family](snow-family.md): offline transfer when the network cannot carry the initial load
- [Hybrid connectivity](../04-networking/hybrid-connectivity.md): Direct Connect and VPN for the gateway's network path
- [AWS KMS and AWS CloudHSM](../07-security/kms-and-cloudhsm.md): the symmetric keys a file share can use for server-side encryption

## Sources

- [What is Amazon S3 File Gateway](https://docs.aws.amazon.com/filegateway/latest/files3/what-is-file-s3.html): protocols, deployment targets and integrations
- [How Amazon S3 File Gateway works](https://docs.aws.amazon.com/filegateway/latest/files3/file-gateway-concepts.html): file to object mapping, HTTPS with Content-MD5, metadata rewrite behavior and versioning guidance
- [Using storage classes](https://docs.aws.amazon.com/filegateway/latest/files3/storage-classes.html): supported classes and the absence of S3 Glacier Instant Retrieval support
- [Limits and quotas for Amazon S3 File Gateway](https://docs.aws.amazon.com/filegateway/latest/files3/fgw-quotas.html): 50 file shares, gateway capacity file counts, 5 TiB file, path and name lengths, cache disk sizes
- [File Gateway setup requirements](https://docs.aws.amazon.com/filegateway/latest/files3/Requirements.html): CPU, RAM, 80 GiB system disk, 100 Mbps, EC2 instance requirements, cache 150 GiB to 64 TiB
- [Refreshing Amazon S3 bucket object cache](https://docs.aws.amazon.com/filegateway/latest/files3/refresh-cache.html): manual, API and time to live refresh, and that it updates inventory only
- [What is Amazon FSx File Gateway](https://docs.aws.amazon.com/filegateway/latest/filefsxw/what-is-file-fsxw.html): closed to new customers, SMB caching of FSx for Windows File Server, VPN or Direct Connect requirement
- [What is Volume Gateway](https://docs.aws.amazon.com/storagegateway/latest/vgw/WhatIsStorageGateway.html): the four-type lineup and the cached compared with stored definitions
- [How Volume Gateway works](https://docs.aws.amazon.com/storagegateway/latest/vgw/StorageGatewayConcepts.html): volume sizes and counts, cache and upload buffer roles, EBS snapshots, the 16 TiB restore limit, and that cached data is not readable with the S3 API
- [Requirements for setting up Volume Gateway](https://docs.aws.amazon.com/storagegateway/latest/vgw/Requirements.html): per-mode local disk table, RAM by cache size, UEFI and x86 instance requirements
- [AWS Storage Gateway quotas, Volume Gateway](https://docs.aws.amazon.com/storagegateway/latest/vgw/resource-gateway-limits.html): 32 TiB and 16 TiB volume ceilings, 32 volumes, 1,024 TiB and 512 TiB totals
- [Backing up your volumes](https://docs.aws.amazon.com/storagegateway/latest/vgw/backing-up-volumes.html): native snapshot scheduler and AWS Backup support for cached and stored volumes
- [What is Tape Gateway](https://docs.aws.amazon.com/storagegateway/latest/tgw/WhatIsStorageGateway.html): virtual tape archive to S3 Glacier Flexible Retrieval and S3 Glacier Deep Archive
- [How Tape Gateway works](https://docs.aws.amazon.com/storagegateway/latest/tgw/StorageGatewayConcepts.html): ten tape drives, one media changer, tape sizes, virtual tape shelf, retrieval times, cache and upload buffer roles
- [AWS Storage Gateway quotas, Tape Gateway](https://docs.aws.amazon.com/storagegateway/latest/tgw/resource-gateway-limits.html): 100 GiB to 15 TiB tapes, 1,500 tapes or 1 PiB per gateway, no archive limit
- [Creating a custom tape pool](https://docs.aws.amazon.com/storagegateway/latest/tgw/CreatingCustomTapePool.html): Glacier and Deep Archive pools, retention lock governance and compliance modes, 100 year maximum
- [Data encryption using AWS KMS](https://docs.aws.amazon.com/filegateway/latest/files3/encryption.html): SSL/TLS in transit, SSE-S3 by default, symmetric KMS keys only
- [Activating a gateway in a virtual private cloud](https://docs.aws.amazon.com/filegateway/latest/files3/gateway-private-link.html): the Storage Gateway endpoint and the separate S3 endpoint for the file share
- [Managing bandwidth for your Volume Gateway](https://docs.aws.amazon.com/storagegateway/latest/vgw/MaintenanceUpdateBandwidth-common.html): upload and download rate limits, schedules, and no support on FSx File Gateway
- [AWS Storage Gateway pricing](https://aws.amazon.com/storagegateway/pricing/): per-gateway write charge with a monthly cap, and where storage charges fall
- [AWS Storage Gateway FAQs](https://aws.amazon.com/storagegateway/faqs/): no charge to read, prorated volume and tape storage on used capacity, compression, EBS snapshot billing
- [What is AWS Backup](https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html): Storage Gateway volumes as a supported resource type
- [What is AWS DataSync](https://docs.aws.amazon.com/datasync/latest/userguide/what-is-datasync.html): the transfer service a one-time migration question wants instead of a gateway
