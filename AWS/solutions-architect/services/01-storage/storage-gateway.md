# AWS Storage Gateway

**Where it sits on the exams.** **AWS Storage Gateway** is the hybrid storage service: a small virtual appliance runs in your data center, on a hardware appliance bought from a reseller, or as an **Amazon Elastic Compute Cloud (Amazon EC2)** instance, the service that rents virtual servers by the second, and it presents a familiar on-premises storage protocol on one side while keeping the data in AWS on the other. Every gateway holds a local disk cache so recently used data is served at local speed, and uploads asynchronously over an encrypted connection, which is the point of the service: an application nobody is willing to rewrite keeps speaking NFS, SMB or iSCSI while the capacity behind it becomes **Amazon Simple Storage Service (Amazon S3)**, the object storage service. Storage Gateway owns the hybrid storage bullet in SAA-C03 task 3.1, supports tasks 3.5 and 4.1, and carries SAP-C02 task 4.3, where the guide names Volume Gateway by name. The rule of thumb the exam wants is to pick the gateway type by the protocol the application already speaks, then pick the mode by where the primary copy of the data has to live.

## What Storage Gateway is and how the four types differ

One appliance runs one gateway type. You download a virtual machine image for VMware ESXi, Microsoft Hyper-V, Linux Kernel-based Virtual Machine or Nutanix AHV, give it four virtual processors, at least 16 GiB of reserved RAM and 80 GiB of disk for the image and system data, then activate it against a Region from the console or the API. From that moment the gateway is an AWS resource you manage remotely: the local hardware only has to stay up and stay connected. AWS asks for at least 100 Mbps of bandwidth simply to download, activate and update a gateway, and the real bandwidth you need follows the write rate of the workload.

The four types split along the protocol they speak locally. **Amazon S3 File Gateway** serves Network File System (NFS) versions 3 and 4.1 and Server Message Block (SMB) versions 2 and 3, and turns files into S3 objects. **Amazon FSx File Gateway** serves SMB and caches shares that live in **Amazon FSx for Windows File Server**, the managed Windows file system. **Volume Gateway** serves Internet Small Computer System Interface (iSCSI) block volumes. **Tape Gateway** serves a virtual tape library over iSCSI so existing backup software sees tape drives and a media changer. Read the table for three things: the protocol each type presents locally, what the data becomes once it reaches AWS, and which side of the link holds the primary copy. The last column is the wording in a stem that selects the row.

| Gateway type | Local protocol | What lands in AWS | Primary copy | The wording that selects it |
|---|---|---|---|---|
| S3 File Gateway | NFS v3, v4.1; SMB v2, v3 | One S3 object per file, in your own bucket, key equals path | In AWS, hot files cached locally | "on-premises applications write files", "the data must be readable by AWS analytics as objects", "lift a file server into S3" |
| FSx File Gateway | SMB | Files in an FSx for Windows File Server file system | In AWS, hot files cached locally | "low-latency on-premises access to a Windows share already in AWS", "consolidate branch file servers" |
| Volume Gateway, cached | iSCSI block | Volume data held by the service in S3; backups as EBS snapshots | In AWS, hot blocks cached locally | "reduce the on-premises storage footprint", "keep low latency for frequently accessed data" |
| Volume Gateway, stored | iSCSI block | EBS snapshots only | On premises, the entire dataset | "the whole dataset needs local latency", "offsite backup", "recover into EC2" |
| Tape Gateway | iSCSI virtual tape library | Virtual tapes in S3, archived to S3 Glacier Flexible Retrieval or S3 Glacier Deep Archive | In AWS | "keep the existing backup application", "retire the physical tape library", "long-term retention" |

Two boundaries are worth drawing now. Storage Gateway is not a bulk migration tool: a one-time copy of a file share into AWS belongs to **AWS DataSync**, the managed transfer service for file and object data, covered in [AWS Transfer Family and AWS DataSync](transfer-family-and-datasync.md). And a gateway is not a two-way replication product. It is a cache with a write-back path, so the exam signal for Storage Gateway is always an application that must go on running on premises.

## S3 File Gateway and FSx File Gateway

S3 File Gateway gives an on-premises client a mount point whose contents are an S3 bucket. Files written to the share become objects with the path as the key, one object per file, and objects already in the bucket appear as files. A file share binds to exactly one bucket, though several shares can point at one bucket as long as each uses a non-overlapping prefix, and a gateway supports up to 50 file shares. The largest individual file is 5 TiB, paths are capped at 1,024 bytes and file names at 255 bytes. All transfer is over HTTPS, the gateway sets a Content-MD5 header so S3 rejects a corrupted upload and the gateway retries, and transfers are optimized with multipart parallel uploads and byte-range downloads.

Two behaviors decide questions. First, the mapping between file operations and objects is not free. Renaming a file or folder, changing permissions or ownership, or appending to a file replaces the existing object and creates a new one, which triggers early deletion and retrieval charges on the infrequent access and archive storage classes. A file share can be created against S3 Standard, S3 Standard-Infrequent Access, S3 One Zone-Infrequent Access or S3 Intelligent-Tiering, and objects can later transition to Glacier by lifecycle policy, but S3 File Gateway does not support S3 Glacier Instant Retrieval, and AWS warns against the Intelligent-Tiering archive access tiers on a share because restoring takes hours and file access times out. Second, the gateway keeps a cached inventory of the bucket, so objects written into the bucket by something other than the gateway are invisible to the share until the cache is refreshed. You refresh it manually, through the `RefreshCache` API, or by setting a time to live so a directory resynchronizes the next time a client touches it after the interval expires. That refresh updates the inventory only, not the file data.

FSx File Gateway is the SMB-only sibling: it caches shares from an FSx for Windows File Server file system so a branch office reaches an in-cloud Windows share at local latency, joins your Microsoft Active Directory domain, and maps local shares one to one with the remote ones. It needs a private path to the file system, over a VPN or **AWS Direct Connect**, the dedicated network connection service. State its status plainly: Amazon FSx File Gateway is no longer available to new customers, existing customers can keep using it, and AWS now directs new deployments to accessing FSx for Windows File Server directly. It also never supported bandwidth rate limits, unlike the other types. On the exams, a stem about low-latency on-premises access to a Windows file share that already lives in FSx still maps to FSx File Gateway, so learn the mapping even though you could not deploy one today.

## Volume Gateway: cached compared with stored

Volume Gateway presents iSCSI block devices, and this is the type SAP-C02 task 4.3 names. The only question that matters is which side holds the primary copy, because everything else follows from it. With cached volumes the primary copy is in AWS: the service stores all the volume data in S3, and the appliance retains recently read and recently written data locally, so the on-premises array shrinks to the size of the working set. With stored volumes the primary copy is on premises: the application reads and writes local disks at local latency for the entire dataset, and the gateway asynchronously copies that data to AWS as point-in-time backups. Cached buys capacity elasticity, stored buys uniform local latency plus offsite protection.

The local disks make the difference concrete. Read this table for the capacity ceilings of each mode and for the disks the appliance requires, because the absence of a cache disk on a stored gateway is the clearest statement of where the data actually is.

| | Cached volumes | Stored volumes |
|---|---|---|
| Primary copy | Amazon S3, managed by the service | On-premises disks |
| Volume size | 1 GiB to 32 TiB | 1 GiB to 16 TiB |
| Volumes per gateway | 32 | 32 |
| Total per gateway | 1,024 TiB | 512 TiB |
| Cache disk | 150 GiB minimum, 64 TiB maximum | none |
| Upload buffer | 150 GiB minimum, 2 TiB maximum | 150 GiB minimum, 2 TiB maximum |
| Other local disks | none | one or more holding the volumes themselves |
| Backup | Snapshots of the in-cloud volume | Snapshots of the uploaded copy |

Both modes back up the same way. Snapshots are incremental and are stored as **Amazon Elastic Block Store (Amazon EBS)** snapshots, EBS being the network-attached block storage service for EC2, and you take them on demand, on a schedule managed by the gateway, or through **AWS Backup**, the central backup service, which supports both cached and stored volumes and stores the result as EBS snapshots as well. Recovery is where the two modes diverge again. A snapshot can be restored to a gateway volume, on premises or in the cloud, and it can also seed a new EBS volume attached to an EC2 instance, which is the disaster recovery path into AWS. One asymmetry decides questions: a snapshot taken from a cached volume larger than 16 TiB restores to a Storage Gateway volume but not to an EBS volume, and since stored volumes stop at 16 TiB they never hit it. If a design promises recovery into EC2, keep cached volumes at 16 TiB or less.

Note also that cached volume data is held by the service inside S3 rather than in a bucket you own, so you cannot read it with the S3 API or the S3 console. When a stem wants the on-premises data to be directly queryable as objects, the answer is S3 File Gateway, not a cached volume.

## Tape Gateway and the virtual tape library

Tape Gateway exists so a company can retire a physical tape library without replacing the backup software that drives it. Each gateway ships with one virtual tape library containing ten virtual tape drives and one media changer, all presented as iSCSI devices, and supported backup applications from vendors including Commvault, Veeam, Veritas, Dell EMC NetWorker, IBM and Micro Focus drive them exactly as they drive physical hardware. Virtual tapes are created in the console or through the API, sized between 100 GiB and 15 TiB, and a single gateway holds up to 1,500 tapes or 1 PiB of tape data at a time. The archive itself has no limit on tape count or total size.

The lifecycle mirrors physical tape. The backup application writes to a tape in the library, the gateway stores the data locally and uploads it asynchronously, and when the application ejects the tape the gateway moves it to the archive, the virtual tape shelf, in the Region where the gateway was activated. A tape pool decides the storage class on eject. The Glacier pool archives to **S3 Glacier Flexible Retrieval**, from which a tape is typically retrieved within 3 to 5 hours; the Deep Archive pool archives to **S3 Glacier Deep Archive**, typically 12 hours. A tape in Flexible Retrieval can be moved to Deep Archive later for a fee. Archived tapes cannot be read in place: you retrieve the tape back into the gateway's library first, and only then does the backup application see it.

Compliance requirements are met with a custom tape pool and **tape retention lock**, which prevents an archived tape from being deleted or moved to another pool for a fixed period of up to 100 years. Governance mode lets a principal holding `storagegateway:BypassGovernanceRetention` remove a tape; compliance mode lets nobody remove it, including the account root user, and neither the lock type nor a shortened retention period can be changed afterward. A custom pool's configuration is fixed once created, so the pool, not the tape, is where the decision is made.

> **Professional depth.** Retention lock is the tape answer to a write-once-read-many mandate, and it is worth comparing with S3 Object Lock in compliance mode on a bucket behind an S3 File Gateway. The tape lock protects the archived tape as a unit, which fits a "seven year retention of backup sets" requirement; S3 Object Lock protects individual objects, which fits a records mandate on the files themselves.

## Sizing, security, monitoring and what you pay for

Sizing is a recurring exam target because the two local disk roles do different jobs. Cache storage is the durable local store for data waiting to upload and the low-latency copy of recently accessed data; the upload buffer is the staging area from which data is sent to AWS, and it is also what makes a recovery point possible when an appliance fails. A file gateway needs only cache, from 150 GiB to 64 TiB. A cached Volume Gateway or a Tape Gateway needs both, cache from 150 GiB to 64 TiB and upload buffer from 150 GiB to 2 TiB. AWS advises allocating at least 20 percent of the existing file store size as cache and keeping cache larger than the upload buffer. Memory scales with cache: a Volume Gateway wants 16 GiB of reserved RAM up to 16 TiB of cache, 32 GiB from 16 to 32 TiB, and 48 GiB from 32 to 64 TiB. On EC2 the instance must be at least `xlarge`, or `2xlarge` in the compute-optimized family, and the Storage Gateway AMI runs only on x86 instances that support UEFI boot, not on Graviton.

Security has three layers. In transit, the gateway uses SSL/TLS to AWS. At rest, Storage Gateway encrypts what it stores in S3 with S3 managed keys by default, and a file share can instead be configured for server-side encryption with **AWS Key Management Service (AWS KMS)**, the managed key service, using a symmetric key, since asymmetric keys are not supported. For the network path, you can activate a gateway through an interface endpoint for Storage Gateway inside an **Amazon Virtual Private Cloud (Amazon VPC)**, the logically isolated network service, so activation and control traffic never crosses the public internet; an S3 File Gateway needs a second VPC endpoint for S3 to keep the data path private too, and the gateway must be activated in the same Region as the endpoints. Access to the gateway APIs is controlled by **AWS Identity and Access Management (IAM)**, the AWS permissions service, and API calls are recorded by **AWS CloudTrail**, the API audit service. SMB shares authenticate against Active Directory or, for shares that do not need it, guest access with a password.

Operationally, **Amazon CloudWatch**, the AWS monitoring service, receives metrics for cache use, upload buffer use and bytes uploaded, and `CacheHitPercent` and `CachePercentDirty` are the two to watch: a falling hit rate means the cache is too small for the working set, and a rising dirty percentage means the upload path is not keeping up with writes. Bandwidth rate limits cap upload, and on Volume and Tape Gateways download as well, on a schedule that can differ by time of day, which is how a gateway is kept from saturating a shared link during business hours. Pricing has a shape worth memorizing rather than a number: you pay a flat charge per GB of data written to AWS by each gateway, capped per gateway per month, with no charge for reading data back, plus the underlying storage. For a file gateway that storage is your own S3 bucket at ordinary S3 rates; for Volume and Tape Gateways you pay for the volume and tape data stored, prorated daily on the capacity actually used rather than the provisioned size, and the gateway compresses that data before sending it. EBS snapshots of gateway volumes are billed by EBS.

## Professional depth

A gateway is a Regional, single-account resource, so an estate of them is managed as a fleet. Each appliance runs one gateway type, which means a site needing both file and tape access runs two appliances. Tag every gateway for cost allocation, because the per-gateway write charge and its monthly cap make the per-gateway boundary the unit of cost. Volume backups are the piece that crosses accounts cleanly: because AWS Backup produces EBS snapshots, on-premises volume backups land in the same backup plans, vaults, cross-account copies and Backup Audit Manager reports as in-cloud resources, which is usually the keyed answer when a Professional stem asks for one backup policy over cloud and on-premises data.

The private network path deserves design attention at scale. Activating through an interface VPC endpoint keeps control traffic off the internet, but for S3 File Gateway the bucket traffic follows a separate endpoint that must be specified on the file share, and both must be in the Region where the gateway was activated. Pair that with Direct Connect, described in [hybrid connectivity](../04-networking/hybrid-connectivity.md), and the design satisfies both a "no public internet" constraint and a predictable-bandwidth constraint in one answer. Without Direct Connect, bandwidth rate limit schedules are the lever that keeps a gateway from competing with production traffic.

The quotas that bite are the ones that look generous until a migration hits them. A file gateway caches metadata for a bounded number of files, set by a gateway capacity of Small, Medium or Large for 5 million, 10 million or 20 million files; a share with more files than that will still work, because S3 has no folder limit, but performance degrades as the gateway churns metadata. Fifty file shares per gateway sounds ample until a consolidation project maps one share per department. Thirty-two volumes per gateway caps a cached deployment at 1,024 TiB and a stored one at 512 TiB, so past that the answer is more gateways. And 1,500 tapes or 1 PiB per Tape Gateway is a live constraint for a nightly full backup policy, which is one reason retention policy design belongs in the migration plan.

Failure modes cluster around the asynchronous upload. A write acknowledged to the application is durable locally once it reaches the cache disk, but it is not in AWS until it has drained from the upload buffer, so a recovery point objective quoted in a stem has to account for the upload lag, not just the snapshot schedule. If the upload buffer fills, the gateway throttles writes. If the cache disk is undersized, the hit rate collapses and every read becomes a download. On S3 File Gateway, the rewrite-on-metadata-change behavior interacts badly with the 30 day minimum storage duration of S3 Standard-IA and with versioning, which is why AWS recommends a lifecycle rule expiring non-current versions on a bucket behind a gateway.

> **Professional depth.** A Professional stem often extends the Associate scenario by adding a second requirement that disqualifies the obvious mode. "Reduce the on-premises footprint" alone selects cached volumes; add "and restore into an EC2 instance during a failover test" and the design must also keep each volume at 16 TiB or less, because a snapshot of a larger cached volume cannot become an EBS volume. Similarly, "keep the existing backup software" selects Tape Gateway, but adding "and no user, including an administrator, may delete a backup for seven years" forces a custom tape pool with compliance mode retention lock rather than the default Glacier pool.

## Worked scenario

A geological survey company runs a 300 TB seismic archive in a leased data center. Two workloads touch it. A processing cluster mounts NFS shares and reads roughly 8 TB of recent survey data in any given week, and the company wants those files to become objects that an S3-based analytics pipeline can read directly. Separately, a legacy interpretation application writes to iSCSI LUNs on an aging storage array, holds about 40 TB, and must be recoverable into AWS within four hours if the data center is lost. Compliance requires that nightly backup sets be undeletable for seven years. The link to AWS is a Direct Connect connection, and no data may traverse the public internet.

The design uses three appliances. An S3 File Gateway serves the NFS shares, backed by an S3 bucket in S3 Standard with a lifecycle rule moving objects to S3 Standard-IA after 90 days and expiring non-current versions; its cache is sized at roughly 2 TB, comfortably above the 150 GiB minimum and enough for the weekly working set, and the share is created against a VPC endpoint for S3 while the gateway itself is activated through a Storage Gateway interface endpoint. A cached Volume Gateway serves the interpretation application, with volumes kept at 16 TiB or less so their snapshots can seed EBS volumes, cache and upload buffer both provisioned above 150 GiB, and AWS Backup running a daily plan that produces EBS snapshots. A Tape Gateway takes the nightly backup sets from the existing backup software, ejecting into a custom tape pool configured for S3 Glacier Deep Archive with retention lock in compliance mode set to seven years.

Failover is rehearsed rather than assumed. During a test, the team restores the latest volume snapshots to EBS volumes, attaches them to EC2 instances running the interpretation application, and confirms the recovery time. The seismic data needs no failover step, because it is already in S3. Bandwidth rate limit schedules throttle the gateways during working hours so the processing cluster keeps the Direct Connect link.

When the exam describes this scenario it asks which combination meets the requirements, and the keyed answer is an S3 File Gateway for the file workload because the data must be readable as S3 objects, a cached Volume Gateway with volumes at or under 16 TiB for the block workload because the recovery target is an EC2 instance, and a Tape Gateway with a compliance-mode retention lock pool for the backup sets. The distractors substitute stored volumes, which do not reduce the on-premises footprint, or a governance-mode lock, which an administrator can bypass.

## Exam lens

- "On-premises application writes files that must be available as S3 objects" maps to S3 File Gateway with an NFS or SMB share.
- "Keep the existing backup application" or "retire the physical tape library" maps to Tape Gateway.
- "The entire dataset needs low-latency local access, with offsite backup" maps to Volume Gateway stored volumes.
- "Reduce the on-premises storage footprint while keeping hot data local" maps to Volume Gateway cached volumes.
- "Recover the on-premises volumes into EC2" maps to restoring the EBS snapshot, and constrains cached volumes to 16 TiB or less.
- "Low-latency on-premises access to a Windows file share hosted in AWS" maps to FSx File Gateway, which is closed to new customers but still the keyed answer on the exams.
- "Least operational overhead for one-time migration of a file share" maps to AWS DataSync, not a gateway. Storage Gateway is the distractor when the stem does not require ongoing on-premises access.
- "Files added to the bucket by another process are not visible on the share" maps to a cache refresh, manual or on a time to live, not to a larger cache disk.
- "No user, not even the root user, may delete a backup for N years" maps to a custom tape pool with retention lock in compliance mode. Governance mode is the distractor.
- "Retrieve archived backups within 12 hours at the lowest cost" maps to the Deep Archive tape pool; "within 3 to 5 hours" maps to the Glacier pool.
- "No traffic over the public internet" maps to an interface VPC endpoint for Storage Gateway, plus a separate S3 endpoint named on the file share for an S3 File Gateway.
- "Cache hit rate is falling and reads are slow" maps to adding cache disk; "uploads are lagging" maps to upload buffer and bandwidth.
- "One backup policy across cloud and on-premises data" maps to AWS Backup, which protects both cached and stored Volume Gateway volumes as EBS snapshots.
- Cached volume data is the distractor whenever a stem wants the stored data readable through the S3 API, because the service holds it in S3 storage you cannot browse.

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
