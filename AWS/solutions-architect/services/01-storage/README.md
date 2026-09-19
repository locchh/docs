# Storage

Four services carry this category: **Amazon S3**, object storage addressed by
key over HTTPS; **Amazon EBS**, block volumes normally attached to one instance,
with Multi-Attach for supported io1 and io2 workloads; **Amazon EFS**, a managed
NFS file system many instances mount at once;
and **Amazon FSx**, managed file systems that speak SMB, Lustre, NetApp ONTAP
and OpenZFS. The other units move data in or protect what is already stored.

The decision the category keeps asking you to make is object against file
against block. Object when the application can fetch whole items by key over
HTTP and wants capacity that never needs sizing. File when existing code expects
a mounted path and several hosts share it. Block when one operating system needs
a raw device with a predictable IOPS floor. Settle that first, and storage
class, volume type, replication and lifecycle follow from access frequency and
cost.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [s3.md](s3.md) | Choose a storage class, write lifecycle and replication rules, and control access with bucket policies and Access Points | XL |
| [ebs.md](ebs.md) | Match a volume type to an IOPS and throughput target, and manage snapshots, encryption and resizing | M |
| [efs.md](efs.md) | Set performance and throughput modes, and cut cost with One Zone and lifecycle management | S |
| [fsx.md](fsx.md) | Match a workload's file protocol to the right FSx file system | S |
| [storage-gateway.md](storage-gateway.md) | Choose the hybrid storage interface: File, cached or stored Volume, or virtual Tape Gateway | S |
| [backup-and-disaster-recovery.md](backup-and-disaster-recovery.md) | Select a disaster recovery strategy against a stated RTO and RPO, and centralize backups with **AWS Backup** | L |
| [snow-family.md](snow-family.md) | Decide when shipping a device beats sending bytes over the network | S |
| [transfer-family-and-datasync.md](transfer-family-and-datasync.md) | Choose **AWS DataSync** for scheduled bulk copies or **AWS Transfer Family** for managed SFTP | S |

## Which exam tasks this serves

On SAA-C03 this is tasks 3.1 and 4.1 outright, both of which name object, file
and block storage, plus task 1.3 for encryption and backup, task 2.2 for
durability and disaster recovery, and task 3.5 for hybrid transfer services. On
SAP-C02 it serves tasks 1.3 and 2.2 for recovery objectives and business
continuity, 2.5 and 4.3 for selecting a storage service, 2.6 for tiering and
data transfer cost, 3.2 for backup practice, and 4.2 for the migration tool
choice.

## Reading order

Read `s3.md` first, slowly, because later units and both exams assume it. Then
`ebs.md` and `efs.md` together, since the exam often separates them inside one
question. `fsx.md` next for protocol matching, then
`backup-and-disaster-recovery.md`, which is the unit the domain guides point
back to for RTO and RPO. An Associate-only candidate can skim
`storage-gateway.md` and `snow-family.md` down to their comparison tables, and
needs only the selection rules from `transfer-family-and-datasync.md`. A
Professional candidate should reverse that order.
