# Amazon EBS

**Where it sits on the exams.** **Amazon Elastic Block Store (Amazon EBS)** is the network-attached block storage service for **Amazon Elastic Compute Cloud (Amazon EC2)**, the service that rents virtual servers by the second. It presents a raw block device that an operating system formats and mounts like a local disk, and it keeps that device alive independently of the instance using it. EBS is the block storage answer for SAA-C03 tasks 3.1 and 4.1, and it supplies the storage layer in SAP-C02 task 4.3. The rule of thumb the exam wants is that block storage means one volume attached to one instance in one Availability Zone, that the volume type follows the shape of the I/O rather than the size of the data, and that gp3 is the default answer until a stem names a number that gp3 cannot reach.

## What Amazon EBS is and where a volume lives

An EBS volume is created in a single Availability Zone and can only be attached to an instance in that same Availability Zone. Inside that zone, AWS automatically replicates the volume's data across multiple servers, so the failure of one component does not lose data. That replication is zonal, not Regional: the way a volume crosses an Availability Zone or an AWS Region boundary is through a snapshot, which is a point-in-time copy stored separately from the volume. This single fact drives a large share of EBS exam questions. A stem that asks for shared access from instances in three Availability Zones is not asking about EBS at all; it is asking about **Amazon Elastic File System (Amazon EFS)**, the managed elastic NFS file system, or **Amazon FSx**, the family of managed file systems.

Durability is published as an annual failure rate rather than the eleven nines that **Amazon Simple Storage Service (Amazon S3)**, the object storage service, quotes for objects. io2 Block Express volumes are designed for 99.999 percent durability, an annual failure rate no higher than 0.001 percent, which AWS describes as a single volume failure per 100,000 running volumes in a year. Every other volume type is designed for 99.8 to 99.9 percent durability, an annual failure rate of 0.1 to 0.2 percent, or at most two failures per 1,000 running volumes in a year. A volume is therefore not a backup of itself, and the exam expects snapshots in any answer that mentions data protection. Performance is a promise too: Provisioned IOPS volumes are designed to deliver at least 90 percent of provisioned IOPS 99.9 percent of the time in a year, the other types 99 percent of the time.

One boundary is worth drawing immediately. The local NVMe disks physically attached to some instance types are instance store, not EBS, and they are erased when the instance stops. The decision between the two belongs to [Amazon EC2](../02-compute/ec2.md); everything about the EBS side of it belongs here.

## The volume types and what selects each

Read the table for three things: the ceiling each type can reach, the size you must buy to reach it, and the wording in a question stem that selects it. Sizes are the current generation types only; the magnetic `standard` type is the only previous generation EBS volume type, and note that Amazon RDS runs a separate storage lifecycle in which gp2 and io1 are both labeled previous generation, so the answer depends on whether the question asks about an EBS volume or an RDS instance. Magnetic holds 1 GiB to 1 TiB, averages around 100 IOPS with 40 to 90 MiB/s of throughput, and AWS recommends a current type instead.

| Type | Size | Max IOPS | Max throughput | Durability | The wording that selects it |
|---|---|---|---|---|---|
| gp3, General Purpose SSD | 1 GiB to 64 TiB | 80,000 | 2,000 MiB/s | 99.8% to 99.9% | "balanced price and performance", boot volumes, "cost-effective" SSD, predictable performance without buying capacity |
| gp2, General Purpose SSD | 1 GiB to 16 TiB | 16,000 | 250 MiB/s | 99.8% to 99.9% | An existing estate to migrate off; performance scales only with size |
| io2 Block Express, Provisioned IOPS SSD | 4 GiB to 64 TiB | 256,000 | 4,000 MiB/s | 99.999% | "consistent sub-millisecond latency", "sustained IOPS", more than 80,000 IOPS, though only on Nitro instances: other instance types cap a volume at 64,000 provisioned IOPS and reach about 32,000 or 2,000 MiB/s, "highest durability", SAP HANA, Oracle, SQL Server |
| io1, Provisioned IOPS SSD | 4 GiB to 16 TiB | 64,000 | 1,000 MiB/s | 99.8% to 99.9% | An older Provisioned IOPS estate; AWS now steers these workloads to io2 |
| st1, Throughput Optimized HDD | 125 GiB to 16 TiB | 500 (1 MiB I/O) | 500 MiB/s | 99.8% to 99.9% | "big data", "log processing", data warehouse scans, large sequential I/O, cannot boot |
| sc1, Cold HDD | 125 GiB to 16 TiB | 250 (1 MiB I/O) | 250 MiB/s | 99.8% to 99.9% | "lowest storage cost", infrequently accessed throughput workloads, cannot boot |

gp3 is the type to reach for first, because it decouples performance from capacity. Every gp3 volume includes a baseline of 3,000 IOPS and 125 MiB/s in the price of the storage, and that baseline is sustained indefinitely rather than being drawn from credits. Above the baseline you provision IOPS up to 80,000 at a ratio of 500 IOPS per GiB, so the maximum is reachable on a volume of only 160 GiB, and you provision throughput up to 2,000 MiB/s at 0.25 MiB/s per provisioned IOPS, reachable once the volume has 8,000 IOPS and at least 16 GiB. AWS prices gp3 storage 20 percent below gp2 per GiB.

gp2 works the other way, and the difference is the most common sizing trap on the exam. A gp2 volume gets 3 IOPS per GiB, with a floor of 100 IOPS and a ceiling of 16,000 IOPS that is only reached at 5,334 GiB. Volumes smaller than 1 TiB can burst to 3,000 IOPS by spending I/O credits, accrued at 3 credits per GiB per second up to a cap of 5.4 million credits, which sustains a full 3,000 IOPS burst for about 30 minutes. When the credits run out the volume drops to its baseline, and the `BurstBalance` metric in **Amazon CloudWatch**, the AWS monitoring service, is where that shows up. So a workload needing a steady 10,000 IOPS on gp2 forces a 3,334 GiB volume whether or not the data needs the space, while gp3 delivers the same 10,000 IOPS on a 20 GiB volume. Throughput follows size too: gp2 gives 128 MiB/s up to 170 GiB and reaches its 250 MiB/s ceiling at 334 GiB.

The Provisioned IOPS types buy sustained, low-latency IOPS outright. As of April 30, 2025 all io2 volumes, new and previously created, are io2 Block Express volumes, so treat io2 and io2 Block Express as the same product. Block Express runs on a newer storage architecture built for instances on the **AWS Nitro System**, the AWS hypervisor and hardware platform, and is designed for average latency under 500 microseconds on 16 KiB operations. You provision up to 256,000 IOPS at a ratio of 1,000 IOPS per GiB, so the ceiling arrives at 256 GiB, and throughput scales at 0.256 MiB/s per provisioned IOPS to a maximum of 4,000 MiB/s reached at 16,000 IOPS. Instance type gates the top end: Nitro-based instances support volumes provisioned with up to 256,000 IOPS, while other instance types can attach volumes provisioned with up to 64,000 IOPS but achieve up to 32,000. io1 is the older Provisioned IOPS type, capped at 64,000 IOPS with a much tighter 50:1 ratio, so a 100 GiB io1 volume tops out at 5,000 IOPS and 64,000 IOPS needs 1,280 GiB.

The HDD types sell throughput by the terabyte and punish random I/O. An st1 volume accumulates throughput credits at 40 MiB/s per TiB and spends them at up to 250 MiB/s per TiB, so a 1 TiB volume bursts to 250 MiB/s and falls back to 40 MiB/s when the bucket empties; the 500 MiB/s cap arrives at 2 TiB for burst and 12.5 TiB for baseline. sc1 uses the same model at 12 MiB/s per TiB baseline and 80 MiB/s per TiB burst, capped at 250 MiB/s from 3.125 TiB. Neither can be a boot volume, and both merge sequential I/O into 1 MiB blocks, which is why AWS tells customers with small random I/O to use an SSD type instead. Choose st1 when a scan must finish fast or repeat several times a day, and sc1 when cost matters more than the 250 MiB/s ceiling.

Two constraints sit outside the table. The partition scheme caps what the guest can use: a master boot record supports at most 2 TiB, so a boot volume that must grow past 2 TiB needs a GUID partition table. And a volume sized for performance is still billed for the capacity you provision, not the capacity you use.

## Elastic Volumes, EBS-optimized instances and Multi-Attach

**Amazon EBS Elastic Volumes** is the feature that lets you increase the size of a volume, change its type, or change its provisioned IOPS and throughput while the volume stays attached and the instance keeps running. Current generation instances all support it. The rules that decide questions are the asymmetric ones: you can increase size but never decrease it, so shrinking means creating a smaller volume and copying the data across; at most four modifications are allowed on one volume in a rolling 24-hour period; and one modification must complete before the next begins. A modification is best-effort and can take from minutes to hours, with AWS citing up to six hours for a 1 TiB volume, though a size increase takes effect once the volume reaches the `optimizing` state. After the volume grows, the guest file system still has to be extended, which is the step candidates forget.

```bash
aws ec2 modify-volume --volume-id vol-0123456789abcdef0 \
  --volume-type gp3 --size 500 --iops 12000 --throughput 500
```

Migrating gp2 to gp3 is the canonical use. If you change the type without naming IOPS or throughput, EBS provisions whichever is higher, the gp3 baseline or the equivalent of the source gp2 volume, so a 500 GiB gp2 volume delivering 1,500 IOPS and 250 MiB/s becomes a gp3 volume with 3,000 IOPS and 250 MiB/s. A root volume cannot be changed to st1 or sc1 even when detached, and Multi-Attach volumes are restricted: io2 allows size and IOPS changes but not a type change, and io1 allows none of the three.

Performance also has an instance-side ceiling. An **EBS-optimized instance** carries dedicated bandwidth for EBS I/O so that storage traffic does not contend with the instance's other network traffic. The throughput an st1 or sc1 volume actually delivers is the smaller of the volume's limit and the instance's limit, and the same applies to IOPS: provisioning 80,000 IOPS on a volume attached to a small instance buys nothing. When a question says a database is not reaching its provisioned IOPS, the answer is usually a larger or EBS-optimized instance rather than a larger volume.

**Amazon EBS Multi-Attach** is the narrow exception to one volume per instance. It attaches a single Provisioned IOPS SSD volume, io1 or io2 only, to up to 16 instances built on the Nitro System in the same Availability Zone, each with full read and write access, at no additional charge beyond the volume itself. Linux instances support io1 and io2; Windows instances support io2 only. Multi-Attach volumes cannot be boot volumes and cannot be enabled during instance launch. The requirement that decides the exam question is the file system: XFS and ext4 are not designed for simultaneous access by multiple servers, so Multi-Attach requires a cluster-aware file system and an application that provides write ordering. io2 volumes support NVMe reservations for I/O fencing; io1 volumes do not. When a stem wants shared files across instances with no clustering software, Multi-Attach is the distractor and Amazon EFS is the answer.

## Snapshots, cross-Region copies and the archive tier

An **EBS snapshot** is a point-in-time backup of a volume held in S3-backed storage that AWS manages for you, and it persists independently of the volume. The first snapshot of a volume is always a full snapshot, and its size is the amount of data written rather than the size of the volume: the first snapshot of a 200 GiB volume holding 50 GiB of data is a 50 GiB snapshot, billed as 50 GiB. Every later snapshot is incremental and contains only the blocks that changed since the previous one, so three snapshots of a volume that held 10 GiB, then changed 4 GiB, then added 2 GiB cost 16 GiB in total. Deleting a middle snapshot does not break the chain, because AWS retains the blocks that later snapshots still reference. The incremental relationship survives a restore: a volume created from a snapshot, then snapshotted again, produces an incremental snapshot of the original, provided the same account owns it and the same KMS key encrypts it.

Copying is how a snapshot leaves its Region or account, and the rules carry real cost. A copy within the same account and Region using the same key is always incremental. A copy to a new Region is always full, as is any copy re-encrypted under a different key. Later cross-Region or cross-account copies are incremental only when four conditions hold: a copy of that snapshot reached the destination before, the most recent copy still exists there, it has not been archived, and every copy in the destination shares the same encryption state and key. Copies carry neither the source snapshot's user-defined tags nor its fast snapshot restore setting, and at most 20 copies run concurrently into one destination Region.

**Amazon EBS Snapshots Archive** is the cost lever for snapshots you must keep but almost never read. Archiving converts an incremental snapshot back into a full one and moves it to the archive tier, where AWS advertises up to 75 percent lower storage cost for snapshots kept 90 days or longer. The trade is a 90-day minimum retention, a per-GB retrieval charge, and a wait while the snapshot is restored to the standard tier before use. It suits end-of-project snapshots and monthly or yearly compliance copies, and it is the wrong answer for a chain you take every night. **Amazon EBS snapshot lock** covers the other compliance requirement: a locked snapshot cannot be deleted by any user regardless of IAM permissions, in governance mode or in write-once-read-many compliance mode, at no additional charge.

## Fast snapshot restore, Data Lifecycle Manager and the Recycle Bin

A volume restored from a snapshot is available immediately but not yet fully initialized, so the first read of each block pulls it from the snapshot and pays a latency penalty. **Amazon EBS fast snapshot restore (FSR)** removes that penalty by creating volumes that are fully initialized and deliver their provisioned performance instantly. You enable it per snapshot and per Availability Zone, on snapshots you own or that are shared with you, for snapshots of 16 TiB or less, and at most 5 snapshots per Region by default. Each snapshot and zone pair has a credit bucket that refills at `MIN(10, 1024 / snapshot size in GiB)` credits per hour, and each volume created consumes one credit; below one credit the volume is created without the benefit. FSR appears so often as a distractor because of the bill: it is charged per minute for every snapshot and zone pair with a one-hour minimum, and AWS's own worked example at 0.75 USD per hour makes one snapshot in one zone for 30 days cost 540 USD and two snapshots across three zones cost 3,240 USD.

**Amazon Data Lifecycle Manager**, the EBS-native scheduler, automates the creation, retention, copy and deletion of snapshots and EBS-backed **Amazon Machine Images (AMIs)**, the bootable images instances launch from. It carries no additional charge beyond the snapshots it creates, and the boundary to remember is that it cannot manage snapshots or AMIs created by any other means. A default policy protects every volume in a Region that lacks a recent snapshot, runs every 1 to 7 days, retains 2 to 14 days by age, and is limited to one per resource type per Region. A custom policy targets resources by tag, carries up to four schedules in one policy, retains by count up to 1,000 snapshots or by age up to 100 years, and is the only form that supports cross-account copy, snapshot archiving, fast snapshot restore and application-consistent pre and post scripts. The exam's dividing line against **AWS Backup**, the centralized backup service, is scope: Data Lifecycle Manager is EBS and EC2 only, while AWS Backup applies one plan and one vault across many services and many accounts, which is why anything organization-wide points there, as covered in [Backup and disaster recovery](backup-and-disaster-recovery.md).

**Recycle Bin** protects against the deletion itself. Retention rules, created per Region, hold deleted volumes, snapshots and EBS-backed AMIs for a period you set rather than destroying them: 1 to 7 days for volumes and 1 to 365 days for snapshots and AMIs. A rule either matches resource tags or covers every resource of that type in the Region with optional exclusion tags, and a rule can be locked so that it cannot be weakened. There is no charge for the feature, but volumes and snapshots sitting in the Recycle Bin bill at their normal rates until the retention period expires. **EBS direct APIs** answer a different need: `ListSnapshotBlocks`, `ListChangedBlocks`, `GetSnapshotBlock` and `PutSnapshotBlock` read and write snapshot blocks directly, without creating a volume or running an instance, so a backup vendor can compute the difference between two snapshots cheaply and an on-premises system can write incremental data straight into a snapshot. They are billed per request and per block.

## Encryption and access control

EBS encryption uses **AWS Key Management Service (AWS KMS)**, the managed service for creating and controlling encryption keys. EBS asks KMS for a data key, encrypts the volume with AES-256, and stores that data key encrypted under a KMS key alongside the volume metadata. Encryption happens on the servers that host the EC2 instance, so data at rest in the volume, data in transit between the instance and the volume, every snapshot from the volume, and every volume created from those snapshots are all encrypted. Every volume type and every current and previous generation instance type supports it, with no measurable IOPS cost. By default EBS uses the AWS managed key aliased `aws/ebs` in each Region; a customer managed key is what you choose when you need to control rotation, disable the key, or write a key policy, and it is the answer whenever a stem mentions key control or cross-account access.

The behavior the exam tests hardest is what you cannot do in place. You cannot encrypt an existing unencrypted volume, you cannot remove encryption from an encrypted one, and you cannot change the KMS key on an existing volume or snapshot. To encrypt an unencrypted volume, snapshot it and create a new encrypted volume from that snapshot. To encrypt an unencrypted snapshot, copy it and enable encryption on the copy, which is the one operation that changes encryption state, and the same copy operation is how you re-encrypt a snapshot under a different key. Encryption by default is an account and Region setting that makes every new volume and every snapshot copy encrypted automatically, which is the low-overhead answer to "all new volumes must be encrypted".

Sharing has its own rules. Snapshots of encrypted volumes cannot be made public; they can only be shared with named accounts, and the KMS key must be shared with those accounts as well. A user needs `kms:CreateGrant`, `kms:Decrypt`, `kms:DescribeKey`, `kms:GenerateDataKeyWithoutPlaintext` and `kms:ReEncrypt` on the key, and AWS recommends scoping the grant permission with the `kms:GrantIsForAWSResource` condition rather than allowing it outright.

```json
{
  "Effect": "Allow",
  "Action": "kms:CreateGrant",
  "Resource": "arn:aws:kms:us-east-2:123456789012:key/abcd1234-a123-456d-a12b-a123b4cd56ef",
  "Condition": { "Bool": { "kms:GrantIsForAWSResource": true } }
}
```

## Pricing shape and the limits that matter

EBS bills for what you provision, not what you use, in per-second increments with a 60-second minimum. Every type charges per GB-month of provisioned storage. What differs is the performance charge. gp2, st1 and sc1 charge nothing beyond storage, so their performance is fixed by the size you buy. gp3 includes 3,000 IOPS and 125 MB/s free and charges per provisioned IOPS-month above 3,000 and per provisioned MB/s-month above 125, which is what lets a small gp3 volume be both fast and cheap. io1 charges a flat rate per provisioned IOPS-month on top of storage. io2 charges per provisioned IOPS-month in three tiers that get cheaper as a single volume goes up, at 32,000 and again at 64,000 IOPS, applied per volume, so ten 1,000 IOPS volumes all bill at the first tier while one 60,000 IOPS volume reaches the second. Snapshots bill per GB-month of the blocks actually stored, archived snapshots bill per GB-month of the full copy plus a per-GB retrieval charge, and fast snapshot restore bills per hour per snapshot per zone. Multi-Attach, Recycle Bin, Data Lifecycle Manager and snapshot lock add no charge of their own.

Two families of limits bite. Per volume, the ratios are the limit: 500 IOPS per GiB on gp3, 3 IOPS per GiB on gp2, 1,000:1 on io2 and 50:1 on io1. Per Region, the aggregates are the limit, and the io2 ones are the tightest: 100,000 provisioned IOPS and 20 TiB of io2 storage across the whole Region by default, against 300,000 IOPS and 50 TiB for io1. Both are adjustable through Service Quotas. A Region holds 100,000 snapshots by default, an SSD volume supports 5 concurrent snapshots while st1 and sc1 support only 1, and snapshotting an HDD volume can pull its throughput down to baseline while the snapshot runs. CloudWatch is where this becomes visible: `VolumeReadOps` and `VolumeWriteOps` for IOPS, `VolumeQueueLength` for saturation, `BurstBalance` for gp2, st1 and sc1 credit exhaustion, and `VolumeIdleTime` for volumes worth deleting.

## Professional depth

At fleet scale the per-Region aggregates run out before the per-volume ratios do. The default io2 quotas are 100,000 provisioned IOPS and 20 TiB of storage across an entire Region, per account, against 300,000 IOPS and 50 TiB for io1. A single 256 GiB io2 volume at 256,000 IOPS is therefore not creatable until the quota is raised, which is a Service Quotas request per account and per Region. Plan that increase during the design of a migration wave, not on cutover night.

Snapshot copy economics decide Professional questions about cross-Region protection. The first copy of any snapshot into a new Region or account is full and is billed as one, so the cost of standing up a second Region is front-loaded. Later copies are incremental only when all four conditions hold: a previous copy reached the destination, it still exists, it has not been archived, and every copy there shares the same encryption state and key. Break one, most commonly by archiving the destination copy to save money or by rotating to a new key, and the next copy silently reverts to full. The 20 concurrent copies per destination Region is the other ceiling: a wave that snapshots 200 volumes at once will queue, so the copy schedule has to be staged.

Cross-account design turns on the key. An encrypted snapshot can be shared only with named accounts, never publicly, and the recipient needs access to the KMS key as well as the snapshot. The durable pattern is for the recipient to copy the shared snapshot immediately and re-encrypt it under a key in its own account, which breaks the dependency on the source account and survives that account being compromised or the share revoked. Data Lifecycle Manager custom policies automate the sharing side and a cross-account copy event policy in the destination account automates the copying side, which is how a central backup account collects snapshots without broad access to production.

Failure modes cluster around shared state and concurrency. A Multi-Attach volume with a problem at the EBS infrastructure layer becomes unavailable to all 16 attached instances at once, so the cluster software above it must be able to lose it; problems at the EC2 or network layer may affect only some attachments. Only one concurrent snapshot is allowed per st1 or sc1 volume against five for the SSD types, so a nightly job over a large HDD estate serializes. Elastic Volumes allows four modifications per volume in a rolling 24-hour period, which caps an automated rightsizing loop and argues for changing IOPS and throughput in one call rather than two.

The Professional extension of the Associate scenario is usually governance rather than throughput. An Associate question asks which volume type serves a database; the Professional version asks how 60 accounts prove that every volume is encrypted, backed up daily, retained for seven years and recoverable in a second Region. The answer combines encryption by default in every account and Region, a key policy that lets the backup account use the key, backup plans applied organization-wide through AWS Backup rather than per-account Data Lifecycle Manager policies, locked Recycle Bin retention rules, and snapshot lock in compliance mode where a regulator requires write-once storage.

## Worked scenario

A media analytics company runs a self-managed PostgreSQL database on a Nitro-based EC2 instance, plus a nightly batch job that scans 6 TiB of raw event logs. The database sits on a 4 TiB gp2 volume sized that large only to reach 12,000 IOPS, and during month-end close the application stalls. The log volume is a 6 TiB gp2 volume that costs more than the database volume and never needs low latency. Compliance requires daily backups retained for seven years, a copy in a second Region, and proof that backups cannot be deleted early.

The database volume moves to io2 with Elastic Volumes, in place and with no downtime: the workload needs sustained IOPS with consistent sub-millisecond latency, and io2 provides both plus 99.999 percent durability. If the requirement were purely 12,000 steady IOPS at the lowest cost, gp3 at 500 IOPS per GiB would be the answer instead, and the choice turns on whether the stem says latency or says cost. The log volume changes type to st1, which delivers up to 500 MiB/s of sequential throughput for a fraction of the gp2 price and matches a workload that reads large blocks once a night; sc1 would be the choice if the scans were weekly. HDD types cannot boot, so the root volume stays gp3.

For protection, a Data Lifecycle Manager custom policy tagged `backup=prod` takes a nightly snapshot and copies it to the second Region, while seven-year retention with an audit trail moves to AWS Backup vaults. The monthly snapshots kept for the full seven years are archived to the EBS Snapshots Archive tier, accepting the 90-day minimum and per-GB retrieval charge in exchange for up to 75 percent lower storage cost. Encryption by default is enabled in both Regions with a customer managed key, and Recycle Bin retention rules protect against accidental deletion of the volumes themselves.

The exam asks this as a two-part question. Asked which changes improve performance and cost, the keyed answer is io2 for the database volume and st1 for the log volume, applied with Elastic Volumes without detaching. Asked how the seven-year requirement is met most cost-effectively, the keyed answer is a lifecycle that archives long-retention snapshots rather than one that keeps every nightly snapshot in the standard tier.

## Exam lens

- "Sub-millisecond latency" or "highest durability" or "mission-critical database" maps to io2 Block Express, which is the only type at 99.999 percent durability.
- "More than 80,000 IOPS" or "more than 2,000 MiB/s on one volume" maps to io2; gp3 cannot reach either number.
- "Lowest cost SSD" or "balance of price and performance" maps to gp3, which is also the answer whenever performance must rise without the volume growing.
- "Boot volume larger than 2 TiB" maps to a GUID partition table; a master boot record caps it at 2 TiB.
- "Fast at first and then slow" maps to gp2 or HDD burst credit exhaustion; check `BurstBalance`, and the fix is gp3 or a larger volume.
- "Big data", "log processing" or "sequential scans" maps to st1; "lowest storage cost" for the same access shape maps to sc1. Neither can be a boot volume.
- "Change volume size or type without downtime" maps to Elastic Volumes; the distractor is a snapshot and restore, which is unnecessary and slower. You cannot decrease size, and only four modifications are allowed per volume per 24 hours.
- "Several instances must read and write the same files" maps to Amazon EFS. Multi-Attach is the distractor unless the stem also names a cluster-aware file system, io1 or io2, one Availability Zone, and at most 16 Nitro instances.
- "Encrypt an existing unencrypted volume" maps to snapshot, then create an encrypted volume from the snapshot; "encrypt an existing snapshot" maps to an encrypted copy. Nothing encrypts in place.
- "All new volumes must be encrypted with no per-team action" maps to encryption by default, set per account and per Region.
- "Share an encrypted snapshot with another account" maps to sharing the snapshot with named accounts and sharing the KMS key; public sharing of an encrypted snapshot is impossible.
- "Automate daily snapshots of tagged volumes with the LEAST operational overhead" maps to Data Lifecycle Manager; AWS Backup is the answer when the scope crosses services or accounts, and a cron job on an instance is always wrong.
- "Retained for years and rarely read" maps to EBS Snapshots Archive and its 90-day minimum; "must not be deletable by anyone" maps to snapshot lock in compliance mode.
- "Restore many volumes from one snapshot at full performance immediately" maps to fast snapshot restore, which is the wrong answer whenever the stem says MOST cost-effectively, because it bills per snapshot per Availability Zone per hour.
- "Read the changed blocks between two snapshots without launching an instance" maps to the EBS direct APIs.

## Knowledge check

### 1. Sizing a transactional volume (Associate)

A company runs a transactional application on an Amazon EC2 instance backed by a 4 TiB General Purpose SSD (gp2) volume. The application holds only 300 GB of data; the volume was sized at 4 TiB solely to reach the IOPS the workload needs. Monitoring shows a sustained requirement of 9,000 IOPS with single-digit millisecond latency and no latency requirement below one millisecond.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Increase the gp2 volume to 5,334 GiB so that it is provisioned with the gp2 maximum of 16,000 IOPS.
- **B)** Change the volume type to Provisioned IOPS SSD (io2) and provision 9,000 IOPS.
- **C)** Change the volume type to General Purpose SSD (gp3) on a 400 GiB volume and provision 9,000 IOPS.
- **D)** Change the volume type to Throughput Optimized HDD (st1) and keep the 4 TiB size.

<details><summary>Answer</summary>

**Answer: C.** gp3 separates performance from capacity. It includes 3,000 IOPS in the storage price and scales to 80,000 at a ratio of 500 IOPS per GiB, so a 400 GiB volume can carry 9,000 IOPS while paying for only the capacity the data needs. A keeps the gp2 model, where performance is bought through capacity at 3 IOPS per GiB, so it pays for roughly 5 TiB of storage that is not needed. B meets the performance requirement but io2 costs more per GiB and adds a per-provisioned-IOPS charge, and the stem explicitly does not require sub-millisecond latency or 99.999 percent durability. D is an HDD type that tops out at 500 IOPS on 1 MiB operations and is unsuitable for random transactional I/O.

*Where this is covered: The volume types and what selects each.*

</details>

### 2. A nightly sequential scan (Associate)

A data engineering team stores 5 TiB of raw event logs on a single Amazon EBS volume attached to an EC2 instance. A nightly job reads the entire volume sequentially in large blocks and must finish within four hours. The data is never read at any other time, and the team wants the lowest possible storage cost that still meets the four-hour window.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Store the logs on a Throughput Optimized HDD (st1) volume.
- **B)** Store the logs on a Cold HDD (sc1) volume.
- **C)** Store the logs on a General Purpose SSD (gp3) volume with provisioned throughput of 500 MiB/s.
- **D)** Store the logs on a Provisioned IOPS SSD (io1) volume with 32,000 provisioned IOPS.

<details><summary>Answer</summary>

**Answer: A.** st1 is designed for large sequential I/O, bursts to 250 MiB/s per TiB up to a 500 MiB/s cap, and AWS documents a full scan of a 5 TiB st1 volume completing in 2.91 to 3.27 hours, inside the window. B is cheaper per GB but caps at 250 MiB/s, and AWS documents the same 5 TiB scan taking 5.83 to 6.54 hours on sc1, which breaks the four-hour requirement in the stem. C meets the window but pays SSD storage prices plus a provisioned throughput charge for a workload that needs neither low latency nor random I/O. D is the most expensive option of the four and buys IOPS that a purely sequential scan does not use.

*Where this is covered: The volume types and what selects each.*

</details>

### 3. Encrypting what already exists (Associate)

An audit finds that a production EC2 instance has an unencrypted 500 GiB data volume and that 60 existing snapshots of that volume are also unencrypted. Security requires that the volume and all retained snapshots be encrypted with a specific customer managed AWS KMS key.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable EBS encryption by default in the Region, which encrypts the existing volume and its existing snapshots in place.
- **B)** Create a snapshot of the unencrypted volume, create a new volume from that snapshot with encryption enabled and the customer managed key, then attach the new volume in place of the old one.
- **C)** Use an Elastic Volumes modification on the attached volume to set the KMS key without detaching it.
- **D)** Copy each existing snapshot, enabling encryption with the customer managed key on the copy, and delete the unencrypted originals.
- **E)** Call the AWS KMS `ReEncrypt` operation against the volume ID to re-wrap the volume's data key.

<details><summary>Answer</summary>

**Answer: B and D.** Nothing in EBS encrypts in place. The only route for a volume is snapshot, then create an encrypted volume from that snapshot, and the only route for a snapshot is an encrypted copy, which is also how a snapshot is re-encrypted under a different key. A is half right and half wrong: encryption by default does prevent future unencrypted volumes, which the stem also asks for, but it does not touch existing resources, and the option states that it does. C is not a capability of Elastic Volumes, which changes size, type, IOPS and throughput only. E addresses KMS key material rather than EBS resources; there is no API that re-encrypts an attached volume.

*Where this is covered: Encryption and access control.*

</details>

### 4. Shared access from three Availability Zones (Associate)

A content management application runs on six EC2 instances spread across three Availability Zones behind a load balancer. Every instance must read and write the same set of files, and a file written by one instance must be visible to the others immediately. The company does not want to install or operate clustering software.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create a Provisioned IOPS SSD (io2) volume with Multi-Attach enabled and attach it to all six instances.
- **B)** Create a Provisioned IOPS SSD (io1) volume with Multi-Attach enabled, attach it to all six instances, and format it with a cluster-aware file system.
- **C)** Attach a separate gp3 volume to each instance and synchronize them on a schedule using snapshots.
- **D)** Create an Amazon EFS file system and mount it on all six instances.

<details><summary>Answer</summary>

**Answer: D.** Amazon EFS is a managed NFS file system that mounts from every Availability Zone in the Region and gives all instances a consistent shared view with nothing to install. A fails on two counts: a Multi-Attach volume lives in one Availability Zone and cannot serve instances in three, and standard file systems such as XFS and ext4 are not safe for simultaneous access, so a cluster-aware file system would still be required. B names the file system but keeps the single Availability Zone limitation and adds the clustering software the stem rules out. C does not give immediate visibility of a written file and adds a synchronization job to operate.

*Where this is covered: Elastic Volumes, EBS-optimized instances and Multi-Attach.*

</details>

### 5. The highest tier of block performance (Associate)

A trading platform runs on a single Nitro-based EC2 instance. Its database requires a sustained 120,000 IOPS from one volume, an average write latency consistently below one millisecond, and the highest volume durability that Amazon EBS offers. Cost is a secondary concern.

Which solution will meet these requirements?

- **A)** Provision a General Purpose SSD (gp3) volume with 80,000 IOPS and 2,000 MiB/s of throughput.
- **B)** Provision a Provisioned IOPS SSD (io2) Block Express volume of 256 GiB or larger with 120,000 provisioned IOPS.
- **C)** Provision a Provisioned IOPS SSD (io1) volume with 64,000 provisioned IOPS.
- **D)** Build a RAID 0 array from four General Purpose SSD (gp2) volumes of 5,334 GiB each.

<details><summary>Answer</summary>

**Answer: B.** io2 Block Express is the only type that reaches 256,000 IOPS, the only one designed for an average latency under 500 microseconds on 16 KiB operations, and the only one rated at 99.999 percent durability with an annual failure rate of 0.001 percent. The 1,000:1 IOPS-to-GiB ratio means 120,000 IOPS needs at least 120 GiB, and a Nitro instance is required to exceed 64,000 IOPS. A cannot reach 120,000 IOPS, since gp3 stops at 80,000, and gp3 is rated at 99.8 to 99.9 percent durability. C stops at 64,000 IOPS and carries the same lower durability rating. D reaches 64,000 IOPS in aggregate, still short, and RAID 0 lowers effective durability because losing one volume loses the array.

*Where this is covered: The volume types and what selects each.*

</details>

### 6. A cross-Region copy bill that doubled (Professional)

A company protects 400 EBS volumes in eu-west-1 with a nightly snapshot that is copied to eu-central-1 for disaster recovery. To reduce cost, an engineer added a step that archives the most recent copy in eu-central-1 to the EBS Snapshots Archive tier each morning. Snapshot storage cost in eu-central-1 rose sharply the following week rather than falling. All snapshots use the same customer managed key in both Regions.

Which explanation and remedy will meet the company's cost requirements?

- **A)** A cross-Region copy is incremental only while an unarchived previous copy of that snapshot still exists in the destination. Archiving it forces every later copy to be a full copy, so keep the most recent copy in the standard tier and archive only older copies.
- **B)** Cross-Region snapshot copies are always full copies, so the cost increase is unrelated to archiving; reduce the copy frequency instead.
- **C)** Snapshots copied across Regions are re-encrypted with the destination Region's default key, which forces a full copy; specify the same key in the destination to restore incremental copies.
- **D)** Archived snapshots continue to bill at the standard tier rate until they are restored; disable archiving and enable fast snapshot restore on the destination copies instead.

<details><summary>Answer</summary>

**Answer: A.** A cross-Region copy is incremental only when a previous copy of the same snapshot reached the destination, still exists there, has not been archived, and shares the encryption key with the other copies there. Archiving the most recent copy removes the reference the next copy would have been measured against, so each night produces a full copy of every volume. B is wrong because only the first copy into a Region is necessarily full; later copies are incremental when the four conditions hold. C describes a real cause of full copies, a change of key, but the stem states the same customer managed key is used in both Regions. D misstates archive billing, which charges the lower archive rate for the full copy, and fast snapshot restore is a restore-performance feature charged per snapshot per Availability Zone per hour, which would add cost.

*Where this is covered: Snapshots, cross-Region copies and the archive tier.*

</details>

### 7. A fast snapshot restore bill (Professional)

A platform team refreshes eight development environments from a single 128 GiB snapshot. The refresh runs once a week, takes about 90 minutes, and creates all eight volumes in the same Availability Zone. To avoid slow first reads the team enabled fast snapshot restore on the snapshot in three Availability Zones and left it enabled in all three. Finance reports a large recurring charge. The weekly refresh must still produce volumes that deliver full performance immediately.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Copy the snapshot into each Availability Zone so that fast snapshot restore is no longer required.
- **B)** Change the development volumes from gp3 to io2 so that they initialize faster.
- **C)** Disable fast snapshot restore in the two Availability Zones the refresh does not use, and leave it enabled only in the zone where the volumes are created.
- **D)** Create a Data Lifecycle Manager policy that takes a new snapshot every hour so that a recent snapshot is always available.

<details><summary>Answer</summary>

**Answer: C.** Fast snapshot restore is billed for every minute that a snapshot and Availability Zone pair is enabled, so enabling three zones when volumes are created in one charges three times over. Keeping the single zone enabled preserves the benefit and cuts the charge by two thirds, and the credit bucket for a 128 GiB snapshot fills at `MIN(10, 1024 / 128)`, or 8 credits per hour to a maximum of 8, which covers the eight volumes created each week. A is not possible: snapshots are Regional resources, not zonal, so there is nothing to copy per Availability Zone. B changes the volume type but not the fact that a volume restored from a snapshot loads blocks lazily on first read. D creates more snapshots and more storage cost without making any restored volume fully initialized.

*Where this is covered: Fast snapshot restore, Data Lifecycle Manager and the Recycle Bin.*

</details>

### 8. Guarding block storage across 60 accounts (Professional)

A company runs 60 AWS accounts in one organization. A central security team must guarantee two outcomes. First, no new EBS volume in any account can be created unencrypted. Second, if an engineer deletes a production volume by mistake, the team must be able to recover that exact volume for up to a week afterward without restoring from a backup. Engineers must keep the ability to delete volumes as part of normal work.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable EBS encryption by default in every account and in every Region the company uses.
- **B)** Apply a service control policy that denies `ec2:DeleteVolume` to all principals in the organization.
- **C)** Enable fast snapshot restore on the snapshots of every production volume.
- **D)** Create Region-level Recycle Bin retention rules for EBS volumes with a 7-day retention period, and lock the rules.
- **E)** Create an AWS Backup plan that copies every EBS snapshot to a second Region every hour.

<details><summary>Answer</summary>

**Answer: A and D.** Encryption by default is an account and Region setting, so applying it everywhere makes every new volume encrypted with no per-team action. Recycle Bin retention rules hold deleted volumes for a period you choose, 1 to 7 days for volumes, and a locked rule cannot be weakened by a workload team; a restored volume is the same volume rather than a rebuild from a snapshot. B meets the recovery goal by preventing deletion entirely, which the stem forbids. C changes how quickly volumes restored from snapshots reach full performance and protects nothing. E improves disaster recovery and costs cross-Region transfer, but restoring from a backup is exactly what the stem rules out, and hourly copies still leave a gap.

*Where this is covered: Fast snapshot restore, Data Lifecycle Manager and the Recycle Bin.*

</details>

## Summary

Amazon EBS is a sequence of decisions about one volume attached to one instance in one Availability Zone. Decide first whether block storage is even the right shape: shared file access across instances is Amazon EFS or Amazon FSx, and scratch data that can be recreated belongs on instance store. Then pick the volume type from the shape of the I/O rather than the size of the data: gp3 by default because it provisions 3,000 IOPS and 125 MiB/s free and scales to 80,000 IOPS without buying capacity, io2 Block Express when a stem says sub-millisecond latency, sustained IOPS beyond 80,000 or 99.999 percent durability, st1 for large sequential scans, sc1 when the scan is rare and cost rules, and gp2 only as something to migrate away from. Size for performance using each type's ratio, then change type, size, IOPS and throughput live with Elastic Volumes rather than rebuilding. Protect the data with incremental snapshots, automated by Data Lifecycle Manager inside EBS or by AWS Backup across services and accounts, copied cross-Region with the four incremental conditions in mind, archived when retention is long and reads are rare. Encrypt with AWS KMS, remembering that nothing encrypts in place and that the copy operation is the only path from unencrypted to encrypted.

## Related units

- [Amazon EC2](../02-compute/ec2.md): the instance store against EBS decision, EBS-optimized instance types and the instance lifecycle
- [Backup and disaster recovery](backup-and-disaster-recovery.md): AWS Backup plans and vaults, and the cross-Region recovery table that EBS snapshots appear in
- [Amazon EFS](efs.md): the answer whenever several instances must share the same files
- [Amazon FSx](fsx.md): managed Windows, Lustre, ONTAP and OpenZFS file systems for shared and high-performance file workloads
- [Amazon S3](s3.md): object storage, and where snapshot data ultimately lives
- [AWS KMS and AWS CloudHSM](../07-security/kms-and-cloudhsm.md): key policies, customer managed keys and cross-account key sharing for encrypted volumes and snapshots
- [Amazon RDS](../05-database/rds.md): the same gp3 and Provisioned IOPS storage choices made inside a managed database
- [Amazon CloudWatch](../08-management/cloudwatch.md): the volume metrics and alarms that show burst exhaustion and queue depth

## Sources

- [Amazon EBS volume types](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html): the comparison tables for SSD, HDD and previous generation volumes, with size, IOPS, throughput and durability
- [Amazon EBS General Purpose SSD volumes](https://docs.aws.amazon.com/ebs/latest/userguide/general-purpose.html): gp3 baseline and provisioning ratios, gp2 I/O credits and throughput by size
- [Amazon EBS Provisioned IOPS SSD volumes](https://docs.aws.amazon.com/ebs/latest/userguide/provisioned-iops.html): io2 Block Express ratios, latency and the April 30, 2025 statement that all io2 volumes are Block Express; io1 limits
- [Amazon EBS Throughput Optimized HDD and Cold HDD volumes](https://docs.aws.amazon.com/ebs/latest/userguide/hdd-vols.html): st1 and sc1 burst bucket rates, caps and documented scan times
- [What is Amazon Elastic Block Store?](https://docs.aws.amazon.com/ebs/latest/userguide/what-is-ebs.html): zonal replication and the durability figures for each volume class
- [Amazon EBS volume constraints](https://docs.aws.amazon.com/ebs/latest/userguide/volume_constraints.html): the 2 TiB master boot record ceiling and the 64 TiB EBS maximum
- [Modify an Amazon EBS volume using Elastic Volumes operations](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-modify-volume.html): what can change live, the four modifications per 24 hours, and the gp2 to gp3 conversion behavior
- [Requirements for Amazon EBS volume modifications](https://docs.aws.amazon.com/ebs/latest/userguide/modify-volume-requirements.html): supported instance types and the boot volume partitioning requirement
- [Amazon EBS optimization](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-optimization.html): dedicated EBS bandwidth and the per-type performance delivery percentages
- [Attach an EBS volume to multiple EC2 instances using Multi-Attach](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volumes-multi.html): 16 Nitro instances, io1 and io2 only, the file system requirement and NVMe reservations
- [How Amazon EBS snapshots work](https://docs.aws.amazon.com/ebs/latest/userguide/how_snapshots_work.html): full first snapshot, incremental behavior and the worked storage arithmetic
- [Copy an Amazon EBS snapshot](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-copy-snapshot.html): cross-Region and cross-account copy, the four incremental conditions and the 20 concurrent copies limit
- [Archive Amazon EBS snapshots](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-archive.html): conversion to a full snapshot, the 75 percent saving claim and the archive quotas
- [Amazon EBS snapshot lock](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-snapshot-lock.html): governance and compliance lock modes
- [Amazon EBS fast snapshot restore](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-fast-snapshot-restore.html): per snapshot and per Availability Zone enablement, the 5 per Region quota and the billing example
- [Amazon EBS fast snapshot restore volume creation credits](https://docs.aws.amazon.com/ebs/latest/userguide/volume-creation-credits.html): the credit bucket fill rate formula
- [Automate backups with Amazon Data Lifecycle Manager](https://docs.aws.amazon.com/ebs/latest/userguide/snapshot-lifecycle.html): no additional charge, the policy quotas and the limit to resources it created
- [Amazon Data Lifecycle Manager default policies vs custom policies](https://docs.aws.amazon.com/ebs/latest/userguide/policy-differences.html): frequency, retention and feature differences between the two policy forms
- [Recover deleted EBS volumes, EBS snapshots, and EBS-backed AMIs with Recycle Bin](https://docs.aws.amazon.com/ebs/latest/userguide/recycle-bin.html): supported resources, quotas and billing while in the bin
- [How does Recycle Bin work?](https://docs.aws.amazon.com/ebs/latest/userguide/recycle-bin-concepts.html): tag-level and Region-level rules and the retention periods per resource type
- [Amazon EBS encryption](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-encryption.html): what cannot be encrypted in place and how to encrypt existing volumes and snapshots
- [How Amazon EBS encryption works](https://docs.aws.amazon.com/ebs/latest/userguide/how-ebs-encryption-works.html): the data key flow, AES-256 and the `aws/ebs` managed key
- [Requirements for Amazon EBS encryption](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-encryption-requirements.html): supported volume and instance types and the required AWS KMS permissions
- [Use EBS direct APIs to access the contents of an EBS snapshot](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-accessing-snapshot.html): reading and writing snapshot blocks without a volume or instance
- [Pricing for EBS direct APIs](https://docs.aws.amazon.com/ebs/latest/userguide/ebsapi-pricing.html): per request and per block charging
- [Quotas for Amazon EBS](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-resource-quotas.html): per-Region io1 and io2 IOPS and storage aggregates, snapshots per Region and concurrent snapshots per volume type
- [Amazon EBS pricing](https://aws.amazon.com/ebs/pricing/): the per-type billing shape, the gp3 free baseline, io2 IOPS tiering and per-second billing with a 60-second minimum
