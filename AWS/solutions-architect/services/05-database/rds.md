# Amazon RDS

**Where it sits on the exams.** **Amazon Relational Database Service (Amazon RDS)** is the managed service that runs a standard relational database engine on an instance AWS provisions, patches, backs up and fails over for you, leaving you responsible for the schema, the queries and the sizing decisions. It carries SAA-C03 tasks 2.1, 2.2, 3.3 and 4.3, and it appears in SAP-C02 tasks 2.2, 2.4, 2.5, 3.3, 3.4 and 4.3. The rule of thumb the exam wants is that RDS is the right answer whenever a workload needs joins, transactions and SQL that a team already knows, and that once RDS is chosen every remaining decision collapses into three questions: which engine, how availability is arranged, and where the reads go.

## What Amazon RDS manages, and choosing an engine

RDS runs six database engines: IBM Db2, MariaDB, Microsoft SQL Server, MySQL, Oracle Database, and PostgreSQL. **Amazon Aurora**, the AWS-built MySQL-compatible and PostgreSQL-compatible engine, is managed through the same API and console but is a different architecture with its own user guide, and it is taught in [Amazon Aurora](aurora.md). The unit of deployment is a DB instance, an isolated database environment that can hold one or more user-created databases, sized by a DB instance class and backed by an **Amazon Elastic Block Store (Amazon EBS)** volume, the durable block storage service. A DB instance lives in a subnet group inside an **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network for AWS resources, and is reached through a DNS endpoint guarded by a security group. Two pieces of AWS global infrastructure frame every RDS design: an AWS Region is a geographic area with its own isolated set of data centers, and an Availability Zone is one or more of those data centers within a Region, engineered to be isolated from failures in the others while staying close enough for low-latency replication. A DB subnet group must span at least two Availability Zones, which is what makes a same-Region standby or replica possible, and crossing Regions is what makes a design survive the loss of a whole Region.

What you get for choosing RDS is a documented split of responsibility. On **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service, AWS takes the hardware, the server maintenance and the facilities while you keep the operating system, the database software, the patching, the backups, the high availability and the scaling. On RDS, AWS takes all of those too, and what remains yours is application optimization, with query tuning named explicitly as the customer's job. That split is the answer to "reduce operational overhead" in a database scenario, and the reason a distractor that builds MySQL on EC2 with cron-driven backups loses to an RDS instance running the same engine.

Engine choice on the exams is rarely about SQL dialect and almost always about three things: what the application already runs on, what it costs to license, and which RDS features the engine supports. A homogeneous migration, meaning Oracle to RDS for Oracle or SQL Server to RDS for SQL Server, preserves the engine and keeps application code untouched, so it is the low-risk answer when the stem says the schema and stored procedures must not change. A heterogeneous migration, meaning Oracle to PostgreSQL or SQL Server to MySQL, drops commercial license cost but requires schema and code conversion, which is the work [**AWS Database Migration Service (AWS DMS)**](../10-migration/dms-and-sct.md), the managed service that moves and replicates data between databases, and the AWS Schema Conversion Tool exist to do.

The feature matrix is where a question is usually decided, because support genuinely differs by engine. **IAM database authentication**, which replaces the database password with a short-lived IAM token, works only with MariaDB, MySQL and PostgreSQL. Multi-AZ DB clusters are available only for RDS for MySQL and RDS for PostgreSQL, and AWS lists Db2, MariaDB, Oracle and SQL Server explicitly as engines where they are not offered. **Amazon RDS Blue/Green Deployments**, which stage a change in a copy of production and switch over to it, are supported only for MariaDB, MySQL and PostgreSQL. **Option groups**, the container for engine add-ons, exist for Db2, MariaDB, MySQL, Oracle and SQL Server, while PostgreSQL uses extensions and modules instead and has no option groups at all. Transparent data encryption is an Oracle and SQL Server feature. **Amazon RDS Custom**, which grants operating system access, supports only Oracle and SQL Server. RDS for Db2 does not support the gp2 storage type. Oracle and SQL Server can reach 256 TiB of storage per DB instance using additional storage volumes, while Db2, MariaDB, MySQL and PostgreSQL top out at 64 TiB.

Between the two open source engines the exam wants a tie-break rather than an argument. PostgreSQL is the engine to name when the scenario mentions complex analytical SQL, extensions such as `pgvector` for embeddings, or a target for migrating off Oracle, because its procedural language and data types map more closely. MySQL and MariaDB are the engines to name for high-volume simple read and write patterns and for lift-and-shift of an existing web application. A requirement for a serverless relational engine that scales capacity automatically is not RDS at all: it points at Aurora Serverless v2. A requirement for a specific engine version, a third-party agent on the host, or a patch AWS has not published points away from managed RDS toward RDS Custom or a self-managed instance on EC2.

## Instance classes, storage types, and storage autoscaling

Compute is chosen by DB instance class, written as `db.` plus a family, a generation, optional attributes and a size, so `db.r7g.2xlarge` is the 2xlarge size of a memory-optimized Graviton3 family. AWS groups the classes into general purpose `db.m`, memory optimized `db.z`, `db.x` and `db.r`, compute optimized `db.c`, and burstable performance `db.t`. Memory optimized classes are the default recommendation for a real database, because the working set that fits in the buffer pool is what keeps reads off disk. Burstable `db.t3` and `db.t4g` classes run at a baseline with the ability to burst to full CPU and are configured for Unlimited mode, which charges for sustained bursting, so they belong on development and test instances and are a poor answer for a production OLTP tier. Optimized Reads classes such as `db.r6gd`, `db.r8gd` and `db.m8gd` attach local NVMe-based SSD block-level storage for applications that need high-speed, low-latency local storage. A class can be changed later by modifying the instance, which is how vertical scaling works and why it costs a restart.

Storage is a separate axis, and reading this table before answering a capacity planning question saves a guess, because the deciding clause is usually either a stated IOPS figure or the words "predictable" and "sub-millisecond".

| Storage type | What you provision | Baseline and range | Maximum throughput | The requirement that selects it |
|---|---|---|---|---|
| General Purpose gp3 | Size, and IOPS and throughput independently above a size threshold | 3,000 IOPS and 125 MiB/s baseline, rising to 12,000 IOPS and 500 MiB/s at 400 GiB for most engines; up to 64,000 IOPS | 4,000 MiB/s on SQL Server and Oracle volumes under 200 GiB, and up to 16,000 MiB/s on the other engines, 1,000 MiB/s on SQL Server | The default for a new database, and "we need more IOPS without buying more storage" |
| General Purpose gp2 | Size only | 3 IOPS per GiB with a 100 IOPS floor, burst to 3,000 IOPS below 1,000 GiB | 1,000 MiB/s, 250 MiB/s on SQL Server | Previous generation for RDS, though still current for EBS volumes; recognize the burst credit trap in a stem about periodic stalls |
| Provisioned IOPS io2 Block Express | Size and IOPS, with throughput scaling from IOPS | 1,000 to 256,000 IOPS, 100 to 65,536 GiB | 4,000 MiB/s | "Sub-millisecond latency", "consistent I/O", business-critical OLTP |
| Provisioned IOPS io1 | Size and IOPS | 1,000 to 256,000 IOPS, 64,000 on SQL Server | 4,000 MiB/s | Previous generation Provisioned IOPS; io2 Block Express is the recommended replacement |

Two facts from that table decide questions. io2 Block Express delivers sub-millisecond average latency, provided consistently 99.9 percent of the time, against single-digit milliseconds at 99 percent for General Purpose, which is the documented basis for choosing it when a stem says latency must be consistent rather than merely low. And the instance class has its own EBS bandwidth ceiling that overrides the volume: AWS gives the example of a class limited to 40,000 IOPS that still delivers 40,000 even with 256,000 IOPS of volumes attached, which is why "we provisioned more IOPS and nothing got faster" is a class problem, not a storage problem.

Magnetic storage, the original `standard` type, is deprecated. You can no longer create DB instances on it, AWS has migrated existing magnetic volumes to gp3, and since July 1, 2026 a snapshot of a magnetic volume must be restored onto a different type. Treat any option offering magnetic storage as wrong.

**Storage autoscaling** removes the most common RDS outage, which is a database that fills its volume and goes to `storage_full`. You set a maximum storage threshold with `--max-allocated-storage`, and RDS starts a storage modification when free space is at or below 10 percent of allocated storage, the condition has lasted at least five minutes, storage optimization from the previous modification has finished, and fewer than four storage modifications have happened in the past 24 hours. The increment is the largest of 10 GiB, 10 percent of current allocated storage, or the growth predicted for the next seven hours from the `FreeStorageSpace` metric. The threshold must be at least 10 percent above current allocated storage, and AWS recommends at least 26 percent above to avoid the approaching-threshold event.

Its limits are exam material in their own right. Autoscaling only ever grows storage: allocated storage can never be reduced, and shrinking a volume means a Blue/Green deployment with a smaller green database or a migration to a new instance. It cannot keep up with a bulk load, because the four-modifications-per-24-hours rule can leave a database storage-full for hours. It is not supported on magnetic storage, on additional storage volumes, or on Multi-AZ DB clusters, and its operations are not logged in **AWS CloudTrail**, the AWS API activity log.

```bash
aws rds modify-db-instance --db-instance-identifier orders-prod \
  --storage-type gp3 --allocated-storage 500 --iops 16000 \
  --storage-throughput 600 --max-allocated-storage 2000 --apply-immediately
```

## Multi-AZ instance deployments, Multi-AZ DB clusters, and read replicas

This is the most reliably tested distinction in the whole Associate exam, and it turns on one sentence AWS puts in the documentation in bold: the high availability option is not a scaling solution for read-only scenarios, and you cannot use a standby replica to serve read traffic. Three deployment shapes exist. A **Multi-AZ DB instance deployment** has one synchronous standby in a second Availability Zone that provides failover support and serves nothing. A **Multi-AZ DB cluster deployment** has a writer and two reader DB instances in three Availability Zones, where the readers are both failover targets and readable. A **read replica** is an independent, asynchronously updated read-only copy that has no automatic failover at all. Read the table for what each one buys and, in the last column, for the stem wording that selects it.

| | Multi-AZ DB instance deployment | Multi-AZ DB cluster deployment | Read replica |
|---|---|---|---|
| What you get | One standby in a second AZ, same Region | One writer plus two readers across three AZs, same Region | Up to 15 read-only copies per source, same Region or another Region |
| Replication | Synchronous to the standby | Semisynchronous, commit needs acknowledgment from at least one reader | Asynchronous, using the engine's native replication |
| Failover | Automatic, typically 60 to 120 seconds, endpoint DNS repointed | Automatic to the reader with the most recent change record, typically under 35 seconds | None. Promotion to a standalone instance is a manual action and breaks replication |
| Standby serves reads | No, never | Yes, both readers serve read traffic | Yes, that is its only purpose |
| Engines | Db2, MariaDB, MySQL, Oracle, PostgreSQL and SQL Server | RDS for MySQL and RDS for PostgreSQL only | All six engines; Db2 standby and Oracle mounted replicas accept no connections |
| Write latency | Higher than Single-AZ because of synchronous replication | Lower than a Multi-AZ DB instance deployment | Unchanged on the source |
| Requirement wording that selects it | "high availability", "withstand the failure of an Availability Zone", "automatic failover", "minimize downtime" | "high availability and additional read capacity", "faster failover", "lower write latency", on MySQL or PostgreSQL | "offload reporting queries", "scale reads", "read-heavy", "reduce load on the primary" |

The two distractor directions are symmetrical and both appear constantly. A read replica is not a high availability answer, because replication is asynchronous, no failover is automatic, and promoting a replica is an operator action that loses whatever had not replicated. A Multi-AZ standby is not a read scaling answer, because it accepts no connections. When a stem asks for both, the keyed answer is either a Multi-AZ DB instance deployment plus read replicas, which is a supported combination and gives synchronous failover in one AZ and asynchronous read capacity in another, or a Multi-AZ DB cluster if the engine is MySQL or PostgreSQL.

Failover in a Multi-AZ DB instance deployment is triggered by a documented list of conditions: an operating system patch applied offline, an unhealthy primary host, loss of network reachability to the primary, a modification you requested, an unresponsive primary, a storage volume failure on the primary host, or a reboot with failover. The mechanism is DNS: RDS repoints the endpoint's record at the standby, so applications must reconnect, and a JVM that caches DNS lookups forever will keep talking to the dead address. AWS recommends setting `networkaddress.cache.ttl` to no more than 60 seconds. The Multi-AZ DB cluster uses the same DNS mechanism and the same advice.

The cluster's speed comes from its replication model and costs something in return. Semisynchronous commit requires acknowledgment from at least one reader but not execution on all of them, so writes are faster than fully synchronous replication, and because a reader is already applying the log, promotion is quick. Failover still resolves replica lag first, and flow control throttles writes on the writer to keep that lag bounded. Clusters also carry a real list of unsupported features: no cross-Region automated backups, no option groups, no storage autoscaling, no stopping and starting, no snapshot copy, no IPv6 connections, no Kerberos authentication, and no way to encrypt an unencrypted cluster.

## Read replicas: scaling reads, cross-Region copies, and promotion

Creating a read replica takes a snapshot of the source, builds a read-only instance from it, and then applies changes with the engine's own asynchronous replication. The default quota is 15 read replicas per primary DB instance, adjustable through Service Quotas. Replicas are billed as ordinary DB instances at the class you choose, and replication traffic within a Region is free. AWS names four use cases: scaling beyond the compute or I/O capacity of a single instance for read-heavy workloads, serving reads while the source is unavailable, running reporting and data warehousing queries away from production, and promoting a replica as a disaster recovery step.

Configuring replicas to meet a requirement is mostly a matter of matching the shape to the constraint. A replica can use a different storage type from its source, so a reporting replica can sit on gp3 while the primary uses io2 Block Express, at the cost of different performance. A replica can itself be Multi-AZ. A replica can run a larger or smaller class than the source, though AWS recommends the same or larger so that it can keep up. There is no autoscaling of read replicas: RDS never adds or removes them for you, so every scaling event is a manual `create-db-instance-read-replica` or a delete. Replication is not circular, so a replica cannot replicate back to its source; MariaDB, MySQL and some PostgreSQL versions can chain a replica from a replica, while Db2, Oracle and SQL Server cannot. Deleting a source DB instance without deleting its same-Region replicas promotes each of them to a standalone instance.

Cross-Region read replicas are the feature that makes RDS part of a multi-Region design, and the [backup and disaster recovery](../01-storage/backup-and-disaster-recovery.md) unit owns the table that places them against the other services. The mechanics are worth knowing here. RDS opens a secure channel between the Regions and adds the security group entries the channel needs. The build is a full snapshot, a cross-Region snapshot copy and a load, which can take hours for a large database. Lag is higher than in-Region because the network path is longer, and the lag is the recovery point objective (RPO) if you promote. A source can have replicas in several Regions, but because of the access control list entry limit on the source VPC, AWS does not guarantee more than five cross-Region read replica DB instances, and you may have at most 20 concurrent cross-Region replica creation requests to one destination Region per account.

Three cross-Region details decide questions. To create an encrypted replica in another Region the source must be encrypted, and you must supply a KMS key from the destination Region, because keys are Regional. Cross-Region replication generates data transfer charges out of the source Region for the initial snapshot and for every subsequent change, which is why For MySQL and MariaDB only, AWS documents building the second and third replicas in a Region from the first replica rather than from the source: you then pay for one cross-Region stream instead of three. And deletion behavior differs by engine: for Db2, MariaDB, SQL Server, MySQL and Oracle, deleting the source promotes the cross-Region replica, while for PostgreSQL the replica's replication status becomes `terminated` and you must promote or delete it yourself.

Promotion is the failover story for replicas, and it is deliberate rather than automatic. You promote a replica with `promote-read-replica`, the instance reboots, replication stops, and the result is an independent read-write DB instance with its own backups. Nothing repoints your application: the promoted replica has its own endpoint, so a DNS change through **Amazon Route 53**, the AWS authoritative Domain Name System service, or a configuration change, is part of the runbook. Because promotion is manual and replication is asynchronous, a design built on cross-Region replicas has an RPO of the replication lag and an RTO measured in the minutes a promotion and a reboot take, which is a pilot light or warm standby posture, not an active-active one.

## Automated backups, snapshots, and point-in-time recovery

RDS takes **automated backups** during a daily backup window, and what it captures is a storage volume snapshot of the whole DB instance rather than individual databases, plus transaction logs uploaded to **Amazon Simple Storage Service (Amazon S3)**, the Regional object storage service, every five minutes. The backup retention period is set between 0 and 35 days for a DB instance, and between 1 and 35 days for a Multi-AZ DB cluster. Setting it to 0 disables automated backups, and moving between 0 and a nonzero value causes an outage. The default is seven days when you create the instance in the console and one day through the CLI or API, which is the kind of asymmetry a Professional question uses to explain why an infrastructure-as-code deployment has less protection than the console instance beside it. Automated backups only run while the instance is `available`, so a database sitting in `storage_full` is also a database that is not being backed up.

**Point-in-time recovery (PITR)** follows from those two pieces. Because transaction logs reach S3 every five minutes, you can restore to any second within the retention period up to the latest restorable time, which trails the present by roughly that five-minute upload interval. `LatestRestorableTime` on `describe-db-instances` reports the exact boundary. A restore always creates a new DB instance rather than rewinding the existing one, so the recovery runbook includes repointing the application. The restored instance comes up on the default parameter and option groups unless you name custom ones in the CLI or API call, you cannot reduce allocated storage during a restore, and any increase must be at least 10 percent. Multi-AZ DB clusters support their own point-in-time restore to a new cluster, and a cluster snapshot can also be restored to a Single-AZ or Multi-AZ DB instance deployment.

Backups protect against a class of failure that replication cannot touch. A dropped table, a bad migration or a mistaken bulk update is copied faithfully to every read replica and every Multi-AZ standby within seconds, so the only recovery is a point-in-time restore to a moment before the damage, or a restore from a manual snapshot taken earlier. Whenever a stem describes accidental deletion, corruption or ransomware rather than a failed instance, the keyed answer is a restore, not a replica.

Manual **DB snapshots** are the other half of the picture and behave differently in exactly the ways that get tested. They are user-initiated, they persist until you delete them, and they are unaffected by deleting the DB instance, whereas automated backups are deleted with the instance unless you choose to retain them. The first snapshot of a database is full and later snapshots are incremental. The quota is 100 manual snapshots per Region, adjustable; snapshots taken by **AWS Backup**, the centralized backup service, count as manual snapshots but do not consume that quota. Snapshots can be copied to another Region or shared with another account, which is what makes them the vehicle for both cross-Region retention and handing a dataset to another team. A snapshot copy across Regions requires a KMS key in the destination Region if the snapshot is encrypted, and a snapshot encrypted with the AWS managed key cannot be shared at all.

Cross-Region automated backup replication puts point-in-time recovery in a second Region without running an instance there: RDS copies every snapshot and every transaction log to a destination Region as soon as they are ready. It works for all six engines and for Multi-AZ DB instance deployments, it is not supported for Multi-AZ DB clusters, source and destination Regions must be on the documented pairing list, and the default quota is 20 cross-Region automated backups per account. Compare it with a cross-Region read replica, which gives a live instance with minutes of lag but no independent recovery point, and with an AWS Backup copy action, where the [backup and disaster recovery](../01-storage/backup-and-disaster-recovery.md) unit records that a continuous backup copied across Regions becomes an ordinary snapshot and loses point-in-time restore.

> **Professional depth.** A Regional recovery design usually needs both replication and backups, and for different reasons. A cross-Region read replica buys a low RPO and a promotion measured in minutes. Cross-Region automated backup replication buys an independent recovery point with no standing instance and therefore a much lower bill, at an RTO of however long a restore takes. Running only the replica leaves the second Region with no way back past a logical failure, and running only the replicated backups leaves an RTO the business may not accept, so a regulated workload commonly funds both and tests each on a different schedule.

## Encryption, IAM database authentication, and the network path

RDS encryption at rest uses AES-256 and a key in **AWS Key Management Service (AWS KMS)**, the managed cryptographic key service, and it covers the underlying storage, the logs, the automated backups, the read replicas and the snapshots in one setting. You pick either the AWS managed key for RDS in your account or a customer managed key; a customer managed key is what a scenario demanding auditable, revocable, policy-controlled key material wants, because its use is logged in CloudTrail and its key policy is yours. The KMS key of an encrypted DB instance cannot be changed afterward, so changing keys means snapshotting and copying the snapshot under the new key.

The limitation that decides the most questions is that you can only encrypt an RDS DB instance when you create it, never afterward. There is no "enable encryption" modification. The documented workaround is a three-step sequence: take a snapshot of the unencrypted instance, copy that snapshot with encryption enabled and a KMS key specified, then restore a new DB instance from the encrypted copy and cut the application over. Several related rules fall out of the same design. You cannot turn encryption off once on. You cannot create an encrypted snapshot of an unencrypted instance, or restore an unencrypted snapshot into an encrypted instance. You cannot have an encrypted replica of an unencrypted instance or the reverse, and a same-Region encrypted replica must use the same key as its source, while a cross-Region replica uses a key from its own Region. Disabling the KMS key does not stop a running database immediately: after two hours the instance moves to `inaccessible-encryption-credentials-recoverable` and stays there for seven days, after which it becomes permanently inaccessible and only a backup can save it.

Transparent data encryption is a separate, engine-level mechanism available for Oracle through Oracle Advanced Security and for SQL Server, enabled through an option group. It can be combined with RDS encryption at rest, with a small performance cost and two independent key sets to manage, and it is the answer when a compliance requirement names TDE specifically rather than encryption at rest generally. Its option is permanent for Oracle and persistent for SQL Server, which means the option group carrying it can never be stripped of it, or cannot be stripped while instances are attached, so any restore has to land on an option group that still includes it.

In transit, RDS supports SSL/TLS to every engine using AWS-provided server certificates, and certificate rotation appears as a `server-certificate-rotation` maintenance action. IAM database authentication removes the database password entirely for MariaDB, MySQL and PostgreSQL: the client calls `generate-db-auth-token`, receives a Signature Version 4 signed token valid for 15 minutes, and presents it as the password, so the connection is always over SSL or TLS and access is managed centrally through **AWS Identity and Access Management (IAM)**, the service that controls identities and permissions. An application on EC2 or in **AWS Lambda**, the serverless function service, then authenticates with its instance or execution role rather than a stored secret. The constraints to remember are that it needs 300 to 1,000 MiB of spare memory on the instance, that CloudWatch and CloudTrail do not log the token generation, that a custom Route 53 record cannot be used in place of the instance endpoint when generating the token, and that several global condition keys including `aws:SourceIp` and `aws:SourceVpc` are unsupported. Where the master password must still exist, RDS can generate and rotate it in **AWS Secrets Manager**, the managed secret store.

The network path is plain VPC networking. A DB instance belongs to a DB subnet group spanning at least two Availability Zones, sits in private subnets in every sane design, and is reachable only through its security group, which in the reference pattern allows the database port from the application tier's security group rather than from a CIDR range. Public accessibility is a per-instance flag and should be off. There is no RDS gateway endpoint, so private access from another VPC or from on premises comes from VPC peering or a transit gateway.

## RDS Proxy and the database connection problem

A relational database answers a fixed number of connections, set by `max_connections` on MySQL and MariaDB, `max_connections` on PostgreSQL, `processes` and `sessions` on Oracle, and `user connections` on SQL Server, and on the open source engines the default is a formula over instance memory: roughly memory in megabytes divided by 12 for MySQL. Each connection consumes memory, so raising the parameter on a small instance trades "too many connections" errors for an out-of-memory condition and an `incompatible-parameters` status. That is the problem **Amazon RDS Proxy** exists to solve, and it is the reason both exam guides list "database connections and proxies" as a knowledge item of its own.

RDS Proxy sits in your VPC between the application and the database and holds a pool of long-lived database connections that many short-lived client connections share. Each proxy performs multiplexing, running all the operations of one transaction over one underlying database connection and then returning it to the pool. When demand exceeds the pool, the proxy queues or throttles client connections rather than letting them hit the database, and beyond the limits you set it sheds load, which keeps the database predictable instead of collapsing. AWS names the candidates explicitly: instances showing "too many connections" errors, smaller burstable classes at risk of running out of memory, applications that open and close large numbers of connections without their own pooling, applications that hold many connections open for long periods, and Lambda functions, whose invocation model creates exactly the short frequent connections a pool absorbs.

Two further benefits appear in scenarios that are not obviously about connections. RDS Proxy bypasses DNS caching during a failover and reduces failover times by up to 66 percent for Multi-AZ DB instances, routing traffic to the new instance while preserving application connections. It does the same for a Blue/Green switchover and for a Multi-AZ DB cluster minor version upgrade, where AWS states the proxy can cut downtime to one second or less.

Security is part of the design rather than an add-on. Clients authenticate to the proxy with IAM credentials, and the proxy authenticates to the database either with IAM database authentication or with credentials it retrieves from Secrets Manager, so a database password never appears in application code. The proxy must be in the same VPC as the database, it cannot be publicly accessible even when the database is, and it cannot be used in a VPC whose tenancy is `dedicated`. The quotas worth knowing are 20 proxies per account per Region by default, up to 200 Secrets Manager secrets per proxy, a default endpoint spread across two Availability Zones, and up to 20 additional endpoints. For a replicated configuration you may associate a proxy only with the writer, not with a read replica, so RDS Proxy is not a read-routing layer. Pricing is per vCPU per hour of the database instance the proxy fronts, which makes it a real line item on a large instance and a common "MOST cost-effective" tie-break against simply fixing the application's own pooling.

## Parameter groups, option groups, maintenance, Blue/Green deployments, and RDS Custom

Engine configuration lives in a **DB parameter group**. An instance created without one uses a default group holding engine and RDS defaults derived from the engine, the compute class and the allocated storage, and the settings in a default group cannot be modified, so changing any engine parameter begins with creating a custom group and associating it with the instance. Association takes effect immediately, but RDS applies the parameters in a newly associated group only after the instance is rebooted; later changes to dynamic parameters in a group already attached apply immediately, while changes to static parameters wait for a manual reboot. Multi-AZ DB clusters use a DB cluster parameter group whose settings apply to every instance in the cluster, while each instance keeps the default DB parameter group. Option groups are the separate mechanism for engine add-ons that are not simple settings, such as Oracle and SQL Server transparent data encryption, Oracle time zone and Oracle Enterprise Manager. An option can be persistent, meaning it cannot be removed while instances are attached, or permanent, meaning it can never be removed, and a restore must land on a group carrying the same permanent options. Option groups are also tied to the instance's VPC, so restoring into a different VPC needs a new group. PostgreSQL has no option groups; it uses extensions.

Every DB instance has a weekly 30-minute maintenance window, chosen at random from an eight-hour block per Region if you do not pick one, and it cannot overlap the backup window. Required patching for security and reliability happens roughly once every few months and usually takes a fraction of the window. Operating system updates typically take about ten minutes and are either optional, which RDS never applies for you, or mandatory with an apply date after which RDS applies them regardless, so repeatedly moving the window does not dodge one. In a Multi-AZ deployment an operating system update is applied to the standby, the standby is promoted, and the old primary is patched as the new standby, so the disruption is one failover of typically less than a minute. An engine version upgrade is the exception: RDS upgrades both instances at once and the database is unavailable for the duration.

Blue/Green deployments are the answer when that engine upgrade window is unacceptable. RDS copies the topology of the production, blue, environment into a staging, green, environment that stays in sync through replication, including read replicas, storage configuration, backups, Performance Insights and Enhanced Monitoring, and making the blue instance Multi-AZ makes the green one Multi-AZ too. You can upgrade the major or minor engine version, change the parameter group, resize storage or change the instance class in green, test it, and then switch over. Switchover typically takes under one minute, involves no data loss because of built-in guardrails, and needs no application change, because the green instances inherit the blue names and endpoints while the old blue instances are renamed with an `-old1` suffix and kept for regression testing. The feature is supported for RDS for MariaDB, MySQL and PostgreSQL only, and the green databases are read-only by default so that writes cannot create replication conflicts. A read replica of a Multi-AZ DB cluster must sit in the same Region as the cluster, and you cannot create a second Multi-AZ DB cluster as a replica of an existing one.

Amazon RDS Custom exists for the applications that cannot live inside the managed boundary. It supports Oracle and SQL Server only, and it gives you privileged access to the database and the underlying operating system so that you can install custom patches, third-party agents and packages, and configure file systems, while RDS keeps automating lifecycle management, automated backups and point-in-time recovery. The tradeoff is a shifted responsibility model: with RDS Custom for Oracle you own operating system patching and share database patching and backups, and a change that takes the host outside the documented support perimeter puts the instance into `unsupported-configuration` until you fix it. The exam's decision rule is the one AWS writes down: fully managed database and operating system means RDS, administrative rights to both means RDS Custom, and full management responsibility with only a managed compute service underneath means self-managing the engine on EC2.

## Monitoring, pricing shape, and the limits that matter

Three monitoring layers answer three different questions, and the exam tests the boundary between them. **Amazon CloudWatch**, the metrics, logs and alarm service, receives metrics from every active database every minute at no extra charge, gathered from the hypervisor: `CPUUtilization`, `FreeStorageSpace`, `DatabaseConnections`, `ReadIOPS` and `WriteIOPS`, `ReadLatency` and `WriteLatency`, `DiskQueueDepth` and `ReplicaLag`. That is the layer for alarms and capacity trends. **Enhanced Monitoring** collects operating system metrics from an agent running on the DB instance rather than from the hypervisor, at a granularity of 1, 5, 10, 15, 30 or 60 seconds, and delivers them as JSON to an `RDSOSMetrics` log group in **Amazon CloudWatch Logs**, retained 30 days by default. It needs an IAM role, usually `rds-monitoring-role`, and it is the layer that shows per-process and per-thread CPU and memory, which is exactly what CloudWatch cannot show. **Performance Insights**, which AWS now presents as Amazon CloudWatch Database Insights, measures database load in average active sessions through the `DBLoad` metric, sampled every second, and lets you slice that load by wait event, by SQL statement, by host and by user, with execution plans captured every five minutes for the heaviest queries. It includes seven days of history by default, extendable to between one and 24 months.

The distinction to carry into the exam is that Enhanced Monitoring answers "what is the operating system doing", with sub-minute granularity and per-process detail, while Performance Insights answers "what is the database waiting on and which query is causing it". A stem about a slow query, a lock, or a wait event is Performance Insights. A stem about which process is consuming CPU or swap on the host is Enhanced Monitoring. A stem about alarming on free storage or connection count is plain CloudWatch.

Pricing has six dimensions. You pay for DB instance hours; for provisioned storage per GB-month; for provisioned IOPS and storage throughput on the types that offer them, whether or not you use them; for backup storage; for data transfer, free between RDS and EC2 in the same Availability Zone and charged across Availability Zones and Regions; and for optional features such as RDS Proxy per vCPU-hour. Multi-AZ roughly doubles instance and storage cost because it runs a second instance, and a Multi-AZ DB cluster runs three. Reserved DB instances commit to a one-year or three-year term for a substantial discount, with All Upfront, Partial Upfront and No Upfront payment options. The levers a "MOST cost-effective" question wants are right-sizing the class, moving Provisioned IOPS to gp3 where latency allows, shortening backup retention, deleting replicas nobody queries, buying Reserved Instances for the steady baseline, and stopping non-production instances, remembering that a stopped instance still pays for storage.

The quotas that bite are worth holding together: 40 DB instances per Region by default across RDS, Aurora, Neptune and DocumentDB combined, with sub-limits of 10 each for license-included SQL Server editions and Oracle; 100 manual snapshots per Region; 15 read replicas per primary and no guaranteed support beyond five cross-Region replicas from one source; 20 cross-Region automated backups per account; 20 proxies per Region; and 100,000 GB of total EBS storage across all DB instances in a Region. Most are adjustable through Service Quotas, but a raise takes time, which is why a Professional migration scenario asks you to raise them before the cutover rather than during it.

## Professional depth

At organization scale the first question is where the database accounts sit and who can reach them. A common pattern is one account per workload with the databases in private subnets, a shared services account holding the KMS customer managed keys, and a central backup account receiving copies. Cross-account restore depends on two things being shared: the snapshot and the key. A snapshot encrypted with the AWS managed key for RDS cannot be shared at all, which is the single most common reason a cross-account recovery plan fails its first test, so every production instance in such a design must use a customer managed key from the start. **AWS Organizations**, the multi-account governance service, adds the guardrails: a service control policy denying `rds:CreateDBInstance` unless `rds:StorageEncrypted` is true, and another denying snapshot sharing outside the organization.

Migration at scale is where RDS meets the rest of the toolchain. A homogeneous move of an on-premises MySQL or PostgreSQL database usually runs as a full load plus change data capture through [AWS Database Migration Service](../10-migration/dms-and-sct.md); a heterogeneous move adds schema conversion first. Where the source is already RDS and the change is a version or a configuration, a Blue/Green deployment is the lower-risk instrument. Where the target must keep an agent or a patch AWS does not ship, RDS Custom is the landing zone, often as a staging step before a later move to fully managed RDS.

The failure modes that cross feature boundaries are the ones Professional questions build on. An unencrypted production database cannot be encrypted in place, so the remediation for a compliance finding is always snapshot, encrypted copy, restore and cut over, with a maintenance window attached. A Multi-AZ DB cluster cannot use cross-Region automated backups, so a design that wants both the cluster's fast failover and second-Region point-in-time recovery has to reach for AWS Backup or snapshot copy instead. Storage autoscaling cannot keep pace with a bulk load because of the four-modifications-per-day rule, so a data migration needs storage provisioned ahead of time. A read replica promoted during an incident keeps no relationship to its old source, so failing back means building replication in the other direction from scratch. And a database at its connection ceiling will throttle long before CPU looks busy, which is why "the instance is at 30 percent CPU and the application is timing out" points at connections and RDS Proxy rather than at a larger class.

> **Professional depth.** Recovery objectives choose the shape. An RPO of seconds with an RTO of minutes across Regions means a cross-Region read replica that you promote. An RPO of minutes with an RTO measured in hours, at much lower cost, means cross-Region automated backup replication with no standing instance. Zero RPO within a Region means Multi-AZ, instance deployment or cluster. Nothing in RDS gives zero RPO across Regions; a requirement for that in a relational workload points at [Aurora Global Database](aurora.md) or at a different data model entirely.

## Worked scenario

A subscription media company runs its billing and entitlement system on a self-managed PostgreSQL server in a colocation facility. The database is 4 TB, sustains about 9,000 transactions per second at peak, and is the system of record for payments. The business wants it on AWS with no schema change, an RPO of five minutes and an RTO of one hour for a Regional failure, month-end reporting that no longer slows down checkout, a hard compliance requirement that the data be encrypted with a key the security team can revoke, and no database passwords in application code.

The design starts with RDS for PostgreSQL, because the engine is unchanged and the migration is homogeneous: AWS DMS performs a full load followed by change data capture, and the cutover happens when lag reaches zero. Storage is io2 Block Express, chosen over gp3 because the requirement is consistent sub-millisecond latency on a payments path, with storage autoscaling enabled. The instance is created encrypted with a customer managed KMS key from the first moment, since encryption cannot be added later, and IAM database authentication replaces the application's stored password. RDS Proxy fronts the writer so that connection churn never reaches the engine and a failover is hidden from open connections.

Availability is arranged in two layers. Within the Region the instance runs as a Multi-AZ DB instance deployment, giving synchronous replication to a standby in a second Availability Zone and automatic failover in 60 to 120 seconds, with RDS Proxy holding connections open across that failover. Month-end reporting runs against an in-Region read replica rather than the standby, because the standby serves no reads, and the replica sits on gp3 storage since reporting tolerates single-digit millisecond latency at a lower price. For the Regional requirement a cross-Region read replica in a second Region carries asynchronous replication whose lag is the RPO, and promotion followed by a Route 53 change is the recovery action, which fits comfortably inside a one-hour RTO. Cross-Region automated backup replication runs alongside it so that a logical failure, a bad deployment that corrupts entitlements, can be recovered to a point in time in either Region, because replication would have copied the corruption faithfully.

The exam asks how to give month-end reporting its own capacity without slowing checkout, and the keyed answer is a read replica. The standby in the Multi-AZ deployment is the distractor, because it accepts no read traffic, and enlarging the writer is the distractor that meets the performance requirement while paying for peak capacity around the clock.

## Exam lens

- "Highly available, survive the loss of an Availability Zone, automatic failover" maps to a Multi-AZ deployment; a read replica is the distractor because its replication is asynchronous and its promotion is manual.
- "Offload reporting, scale reads, reduce load on the primary" maps to read replicas; a Multi-AZ standby is the distractor because it serves no read traffic.
- "High availability and extra read capacity, with faster failover" maps to a Multi-AZ DB cluster, but only on RDS for MySQL or RDS for PostgreSQL.
- "Failover must complete in well under a minute" maps to a Multi-AZ DB cluster at typically under 35 seconds, against 60 to 120 seconds for a Multi-AZ DB instance deployment.
- "Read scaling in another Region, or a Regional recovery option with an RPO of minutes" maps to a cross-Region read replica that you promote.
- "Point-in-time recovery in a second Region with no standing instance" maps to cross-Region automated backup replication, which is unavailable for Multi-AZ DB clusters.
- "Restore to any second in the last N days" maps to automated backups with a retention period of 0 to 35 days, restoring to a new DB instance; "keep a copy after the database is deleted" maps to a manual DB snapshot.
- "Encrypt an existing unencrypted database" maps to snapshot, encrypted snapshot copy, restore; there is no in-place option.
- "Auditable, revocable key control" and "share an encrypted snapshot with another account" both map to a customer managed KMS key, because the AWS managed key cannot be shared.
- "No database passwords in the application" maps to IAM database authentication on MariaDB, MySQL or PostgreSQL, or to Secrets Manager where the engine has no support.
- "Too many connections, or a Lambda function exhausting the database" maps to RDS Proxy; raising `max_connections` is the distractor because connections consume memory.
- "Upgrade the major engine version with minimal downtime" maps to a Blue/Green deployment, switchover typically under a minute, on MariaDB, MySQL or PostgreSQL.
- "Which query is causing the load and what is it waiting on" maps to Performance Insights; "which operating system process is consuming CPU" maps to Enhanced Monitoring.
- "Consistent sub-millisecond I/O" maps to io2 Block Express; gp3 is the MOST cost-effective answer whenever the stem asks only for more IOPS or throughput.
- "Needs operating system access, a custom agent or a specific patch" maps to RDS Custom on Oracle or SQL Server, or to self-managing the engine on EC2; both are the wrong answer when the stem says least operational overhead.

## Knowledge check

### 1. Reporting queries slowing down an order system (Associate)

An online retailer runs its order system on an Amazon RDS for MySQL DB instance in a Multi-AZ deployment. Every night the finance team runs long analytical queries against the same database, and order processing slows noticeably while they run. The company wants the reports to stop affecting order processing without changing the reporting queries.

Which solution will meet these requirements?

- **A)** Point the reporting tool at the standby instance in the second Availability Zone.
- **B)** Increase the DB instance class so that the database has enough capacity for both workloads.
- **C)** Create a read replica of the DB instance and point the reporting tool at the replica endpoint.
- **D)** Enable RDS Proxy and configure the reporting tool to connect through the proxy endpoint.

<details><summary>Answer</summary>

**Answer: C.** A read replica is an asynchronously updated read-only copy created specifically to take read-heavy traffic such as business reporting off the source instance, and pointing the reporting tool at its endpoint needs no query changes. A is wrong because the standby in a Multi-AZ DB instance deployment provides failover support only and cannot serve read traffic; AWS states this explicitly. B would work but pays for peak capacity 24 hours a day to serve a nightly job, and it still lets the reports compete with orders for the same buffer pool. D solves connection pressure, not query contention, and RDS Proxy may only be associated with the writer in a replicated configuration, so it cannot route the reports anywhere else.

*Where this is covered: Multi-AZ instance deployments, Multi-AZ DB clusters, and read replicas.*

</details>

### 2. Surviving the loss of an Availability Zone (Associate)

A company runs a customer-facing application on an Amazon RDS for PostgreSQL DB instance in a single Availability Zone. An internal audit requires that the database survive the failure of one Availability Zone with automatic failover and no data loss at the moment of failure. The team wants the least operational overhead.

Which solution will meet these requirements?

- **A)** Create a read replica in a second Availability Zone and write a Lambda function that promotes it when health checks fail.
- **B)** Modify the DB instance to a Multi-AZ DB instance deployment.
- **C)** Take automated backups with a 35-day retention period and restore to a second Availability Zone if the first fails.
- **D)** Create a cross-Region read replica and fail over to the second Region by changing an Amazon Route 53 record.

<details><summary>Answer</summary>

**Answer: B.** A Multi-AZ DB instance deployment maintains a synchronous standby in a second Availability Zone and fails over automatically, typically in 60 to 120 seconds, with no data loss because the replication is synchronous, and it is a single modification to the instance. A replicates asynchronously, so a promotion can lose in-flight transactions, and it adds custom failover code to maintain. C is a recovery mechanism whose RTO is however long a restore takes and whose RPO is up to five minutes, which is not automatic failover. D protects against a Regional failure rather than the stated Availability Zone failure, replicates asynchronously, and requires a manual promotion.

*Where this is covered: Multi-AZ instance deployments, Multi-AZ DB clusters, and read replicas.*

</details>

### 3. A compliance finding on an unencrypted database (Associate)

An auditor finds that a production Amazon RDS for MariaDB DB instance was created without encryption at rest. The company must encrypt the data at rest using a key that its security team can audit and disable, and it wants to keep the existing data.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Modify the DB instance and set the storage encryption option to enabled, specifying a customer managed key.
- **B)** Create a DB snapshot of the existing DB instance, then copy the snapshot and enable encryption with a customer managed AWS KMS key during the copy.
- **C)** Enable transparent data encryption through an option group associated with the DB instance.
- **D)** Restore a new DB instance from the encrypted snapshot copy and repoint the application to the new endpoint.
- **E)** Create an encrypted read replica of the DB instance with a customer managed key, then promote the replica.

<details><summary>Answer</summary>

**Answer: B and D.** RDS documents that a DB instance can only be encrypted at creation time, and that the supported way to add encryption to existing data is to snapshot the instance, create an encrypted copy of that snapshot, and restore a new DB instance from the copy. A customer managed key gives the security team the auditability and the ability to disable it. A is the trap: no such modification exists. C is wrong because transparent data encryption in RDS is an Oracle and SQL Server feature and MariaDB has no option groups entry for it. E is impossible, because you cannot have an encrypted read replica of an unencrypted DB instance.

*Where this is covered: Encryption, IAM database authentication, and the network path.*

</details>

### 4. Serverless functions exhausting a database (Associate)

A company migrated an API to AWS Lambda backed by an Amazon RDS for PostgreSQL DB instance on a db.t4g.medium class. During traffic spikes the functions fail with "too many connections" errors, although Amazon CloudWatch shows CPU utilization on the database below 30 percent. The company wants to fix the errors without rewriting the functions.

Which solution will meet these requirements?

- **A)** Increase the `max_connections` parameter in a custom DB parameter group and reboot the instance.
- **B)** Create two read replicas and distribute Lambda connections across them.
- **C)** Convert the DB instance to a Multi-AZ DB cluster so that the readers absorb the connections.
- **D)** Create an RDS Proxy for the DB instance and have the Lambda functions connect to the proxy endpoint.

<details><summary>Answer</summary>

**Answer: D.** RDS Proxy pools and multiplexes connections so that many short-lived Lambda connections share a small number of long-lived database connections, and AWS names Lambda functions as a primary candidate for exactly this reason. A raises the ceiling but each connection consumes memory, and on a burstable class this risks an out-of-memory condition and the `incompatible-parameters` status. B sends writes nowhere useful and multiplies the connection problem across more instances rather than solving it. C changes the availability shape and adds two instances of cost, and the writer still receives every write connection.

*Where this is covered: RDS Proxy and the database connection problem.*

</details>

### 5. A database that keeps running out of space (Associate)

A gaming company's Amazon RDS for MySQL DB instance has twice entered the `storage_full` state during rapid user growth, each time requiring an operator to enlarge the volume manually. The company wants the database to grow on its own up to a ceiling it controls, with no downtime when it grows.

Which solution will meet these requirements?

- **A)** Enable storage autoscaling on the DB instance and set a maximum storage threshold above the expected growth.
- **B)** Switch the DB instance from gp3 to io2 Block Express storage and provision the maximum IOPS.
- **C)** Create an Amazon CloudWatch alarm on `FreeStorageSpace` that invokes a Lambda function to call `modify-db-instance`.
- **D)** Enable automated backups with a 35-day retention period so that old data is offloaded to Amazon S3.

<details><summary>Answer</summary>

**Answer: A.** Storage autoscaling starts a storage modification when free space falls to 10 percent or less of allocated storage for at least five minutes, grows the volume by the larger of 10 GiB, 10 percent, or the predicted seven-hour need, and stops at the maximum storage threshold you set. Enabling it requires no reboot and causes no downtime. B changes the storage type and performance but not its size, so the volume still fills. C rebuilds what RDS already provides, including the throttling rules that keep modifications safe, and adds code to maintain. D is unrelated: backups copy data to Amazon S3 but remove nothing from the database volume.

*Where this is covered: Instance classes, storage types, and storage autoscaling.*

</details>

### 6. Faster failover with room for reads (Associate)

A payments company runs Amazon RDS for PostgreSQL in a Multi-AZ DB instance deployment. Failovers take around 90 seconds, which exceeds the new service level target, and a growing read workload is starting to compete with writes. The company wants both problems addressed inside one Region with the least operational overhead.

Which solution will meet these requirements?

- **A)** Add two read replicas in other Availability Zones and configure Amazon Route 53 failover records over their endpoints.
- **B)** Move the database to a larger memory optimized instance class and enable Enhanced Monitoring at one-second granularity.
- **C)** Convert the deployment to a Multi-AZ DB cluster with a writer and two readable standby DB instances.
- **D)** Enable cross-Region automated backup replication and promote a restored instance when a failover is needed.

<details><summary>Answer</summary>

**Answer: C.** A Multi-AZ DB cluster runs a writer and two reader DB instances across three Availability Zones, the readers both serve read traffic and act as automatic failover targets, and failover times are typically under 35 seconds, so one change addresses both requirements. It is available for RDS for PostgreSQL. A gives read capacity but no automatic failover, since a replica must be promoted by hand. B may shorten queries but does nothing to failover time, and Enhanced Monitoring is a diagnostic tool, not a remedy. D is a cross-Region recovery mechanism with an RTO measured in the time a restore takes, which is far worse than 90 seconds.

*Where this is covered: Multi-AZ instance deployments, Multi-AZ DB clusters, and read replicas.*

</details>

### 7. Regional recovery for a regulated workload (Professional)

A financial services company runs an Amazon RDS for Oracle DB instance in eu-west-1 as a Multi-AZ DB instance deployment. Regulators require that the company be able to recover the database in eu-central-1 to any point in the previous 14 days, and separately that a Regional outage be survivable with a recovery point objective of minutes. The company does not want to pay for a full standby environment that is never used for anything.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable cross-Region automated backup replication from eu-west-1 to eu-central-1 with a 14-day retention period.
- **B)** Configure AWS Backup to copy continuous backups to eu-central-1 and rely on point-in-time restore from the copy.
- **C)** Create a cross-Region read replica of the DB instance in eu-central-1 and promote it if the primary Region fails.
- **D)** Convert the DB instance to a Multi-AZ DB cluster and enable cross-Region automated backup replication on the cluster.
- **E)** Copy a manual DB snapshot to eu-central-1 once every 14 days.

<details><summary>Answer</summary>

**Answer: A and C.** Cross-Region automated backup replication copies both snapshots and transaction logs to the destination Region as soon as they are ready, which is what makes a point-in-time restore possible there, and it is supported for Multi-AZ DB instance deployments across all six engines including Oracle. A cross-Region read replica gives a live copy whose lag is the recovery point objective and which can be promoted in minutes, without a full standby application stack. B fails because a continuous backup copied across Regions becomes an ordinary snapshot and loses point-in-time restore. D fails because cross-Region automated backup replication is explicitly unsupported for Multi-AZ DB clusters, and Oracle cannot use Multi-AZ DB clusters at all. E gives a recovery point 14 days old, which is the opposite of the requirement.

*Where this is covered: Automated backups, snapshots, and point-in-time recovery.*

</details>

### 8. A major version upgrade the business will not approve (Professional)

A company must upgrade 30 Amazon RDS for MySQL DB instances from an engine version approaching end of standard support. Each instance is a Multi-AZ DB instance deployment with one read replica. A previous upgrade caused 25 minutes of downtime because RDS upgraded the primary and standby together, and the business will not approve another window of that length. The team also wants to validate the new version against production-like traffic before committing.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Restore the latest snapshot of each instance into a new instance, upgrade it, run tests, then use AWS DMS to synchronize and cut over.
- **B)** Create a blue/green deployment for each DB instance, upgrade the engine version in the green environment, test it, then switch over.
- **C)** Create a cross-Region read replica of each instance on the new engine version and promote it during a maintenance window.
- **D)** Modify each DB instance to the new engine version during its maintenance window and accept the downtime.

<details><summary>Answer</summary>

**Answer: B.** A blue/green deployment copies the full topology, including the Multi-AZ configuration and the read replica, keeps the green environment in sync through replication, lets you upgrade and test there without touching production, and switches over in typically under one minute with no data loss and no application change, because the green instances inherit the blue names and endpoints. It is supported for RDS for MySQL. A rebuilds by hand what the feature automates and adds a migration service to operate for 30 databases. C adds cross-Region replication cost and lag to 30 databases, and every cutover is still a manual promotion plus an endpoint change, which is more operational overhead than a managed switchover. D reproduces the 25-minute outage the business rejected.

*Where this is covered: Parameter groups, option groups, maintenance, Blue/Green deployments, and RDS Custom.*

</details>

### 9. Diagnosing a slow application (Associate)

Users report that an application backed by Amazon RDS for PostgreSQL is slow at unpredictable times. Amazon CloudWatch shows CPU utilization around 45 percent and no storage or connection pressure. The team needs to find which SQL statements are responsible and what the database sessions are waiting on.

Which solution will meet these requirements?

- **A)** Enable Enhanced Monitoring at one-second granularity and review the per-process CPU metrics in CloudWatch Logs.
- **B)** Create a CloudWatch alarm on `DiskQueueDepth` and `ReadLatency` and notify the team when either crosses a threshold.
- **C)** Enable RDS Proxy and review its connection metrics to identify the slow client.
- **D)** Review the Performance Insights dashboard, sorting database load by wait event and by top SQL.

<details><summary>Answer</summary>

**Answer: D.** Performance Insights measures database load in average active sessions and lets you break that load down by wait event, SQL statement, host and user, capturing execution plans for the heaviest queries, which is precisely the "which query and what is it waiting on" question. A gives operating system process and thread detail from an agent on the host, which answers what the operating system is doing rather than what the database is waiting on. B produces an alert rather than a diagnosis, and the stem already says there is no storage pressure. C addresses connection management and reports nothing about query execution.

*Where this is covered: Monitoring, pricing shape, and the limits that matter.*

</details>

### 10. Recovering a database into a separate account (Professional)

A company keeps production databases in one AWS account and requires that a copy of every production Amazon RDS snapshot be restorable in a separate, locked-down backup account in another Region. During a recovery exercise the backup account could not restore any of the snapshots. All production DB instances were created with encryption enabled using the default key offered by the console.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Grant the backup account `rds:RestoreDBInstanceFromDBSnapshot` in a resource policy on each snapshot.
- **B)** Increase the manual DB snapshot quota in the production account from 100 to 500.
- **C)** Re-create the production DB instances so that they use a customer managed AWS KMS key rather than the AWS managed key for RDS.
- **D)** Enable cross-Region automated backup replication into the backup account.
- **E)** Share the customer managed key with the backup account and specify a key in the destination Region when copying each snapshot.

<details><summary>Answer</summary>

**Answer: C and E.** A snapshot encrypted with the AWS managed key for RDS cannot be shared with another account at all, which is why the exercise failed, so the databases must be rebuilt on a customer managed key, the mechanism being a snapshot, an encrypted copy under the new key, and a restore. The receiving account then also needs access to that key, and because KMS keys are Regional, a cross-Region copy must name a key in the destination Region. A is wrong because snapshot sharing is a change to a snapshot attribute rather than an IAM resource policy, and no permission grant overcomes the AWS managed key restriction. B addresses a quota that is not the failure. D replicates backups to another Region within the same account; it does not cross an account boundary.

*Where this is covered: Encryption, IAM database authentication, and the network path.*

</details>

## Summary

Amazon RDS is a sequence of decisions rather than a single product. Choose the engine from what the application already runs, what the license costs, and which RDS features that engine supports, remembering that Multi-AZ DB clusters, Blue/Green deployments and IAM database authentication are not available everywhere. Size the instance class for memory and the storage type for latency, taking gp3 by default and io2 Block Express when the requirement says consistent and sub-millisecond, and turn on storage autoscaling so the volume never fills. Then separate availability from read capacity: a Multi-AZ deployment fails over automatically and serves no reads, a read replica serves reads and fails over never, and a Multi-AZ DB cluster on MySQL or PostgreSQL does both at under 35 seconds. Protect the data with automated backups for point-in-time recovery, manual snapshots for anything that must outlive the instance, and cross-Region replication of backups or replicas for a Regional recovery. Encrypt at creation, because there is no way back, and use a customer managed key wherever sharing or revocation matters. Finally, put RDS Proxy in front of connection-heavy clients, use Blue/Green deployments for version changes, and read Performance Insights for queries and Enhanced Monitoring for the host.

## Related units

- [Amazon Aurora](aurora.md): the shared-storage relational engine, its cluster endpoints, Serverless v2 and Global Database
- [Amazon DynamoDB](dynamodb.md): the non-relational alternative, and the access-pattern test that decides between them
- [Amazon ElastiCache and Amazon MemoryDB](elasticache-and-memorydb.md): caching in front of RDS to cut read load and latency
- [Backup and disaster recovery](../01-storage/backup-and-disaster-recovery.md): the cross-Region recovery table, AWS Backup plans and the DR strategy bands
- [AWS DMS and AWS SCT](../10-migration/dms-and-sct.md): homogeneous and heterogeneous migrations into RDS
- [Amazon VPC](../04-networking/vpc.md): subnet groups, security groups and the private network path to a DB instance
- [AWS KMS](../07-security/kms-and-cloudhsm.md): customer managed keys, key policies and cross-account grants for encrypted snapshots
- [Amazon CloudWatch](../08-management/cloudwatch.md): metrics, alarms and the log groups that Enhanced Monitoring writes to

## Sources

- [What is Amazon Relational Database Service (Amazon RDS)?](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html): the six engines, the responsibility comparison with EC2 and on premises, DB instance concepts and the free tier
- [Configuring and managing a Multi-AZ deployment for Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html) and [Multi-AZ DB instance deployments for Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html): the one-standby and two-standby definitions, synchronous replication, and the statement that a standby cannot serve read traffic
- [Failing over a Multi-AZ DB instance for Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.Failover.html): 60 to 120 second failover, the failover reason list and the DNS TTL guidance
- [Multi-AZ DB cluster deployments for Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html) and [Failing over a Multi-AZ DB cluster](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts-failover.html): semisynchronous replication, readable standbys, flow control, and failover typically under 35 seconds
- [Limitations of Multi-AZ DB clusters](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.Limitations.html) and [Supported Regions and DB engines for Multi-AZ DB clusters](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RDS_Fea_Regions_DB-eng.Feature.MultiAZDBClusters.html): MySQL and PostgreSQL only, and the unsupported feature list
- [Working with DB instance read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html) and [Working with Multi-AZ DB cluster read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_MultiAZDBCluster_ReadRepl.html): use cases, asynchronous replication, no autoscaling, the no-circular-replication rule, and DB instance replicas from a cluster
- [Creating a read replica in a different AWS Region](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.XRgn.html): the five-replica guidance, encryption rules, data transfer cost and per-engine deletion behavior
- [Amazon RDS DB instance storage](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html): gp2, gp3, io1 and io2 Block Express ranges, latency figures, striping and the magnetic deprecation
- [Managing capacity automatically with Amazon RDS storage autoscaling](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.Autoscaling.html): trigger conditions, increment sizing and limitations
- [DB instance classes](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.html) and [DB instance class types](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.DBInstanceClass.Types.html): the class families and the Optimized Reads classes
- [Introduction to backups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html) and [Backup retention period](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.BackupRetention.html): incremental snapshots, the 100 manual snapshot limit, 0 to 35 days of retention and the console and CLI defaults
- [Restoring a DB instance to a specified time for Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html): five-minute log uploads, latest restorable time and restore constraints
- [Replicating automated backups to another AWS Region](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReplicateBackups.html): supported engines, Multi-AZ support and the 20-backup quota
- [Encrypting Amazon RDS resources](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html): the encrypt-at-creation limitation, the snapshot copy workaround and the replica and sharing rules
- [IAM database authentication for MariaDB, MySQL, and PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.html): 15-minute tokens, supported engines and limitations
- [Amazon RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html) and [Planning where to use RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-planning.html): multiplexing, quotas, the writer-only association rule, candidate workloads and the up-to-66-percent failover improvement
- [Overview of Amazon RDS Blue/Green Deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/blue-green-deployments-overview.html): supported engines, what is copied and the sub-minute switchover
- [Overview of parameter groups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/parameter-groups-overview.html): default groups that cannot be modified, static and dynamic parameters, and the reboot rules
- [Working with option groups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithOptionGroups.html): persistent and permanent options, and PostgreSQL using extensions instead
- [Maintaining a DB instance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.Maintenance.html): the 30-minute window, Multi-AZ patching order and mandatory operating system updates
- [Amazon RDS Custom](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-custom.html): Oracle and SQL Server only, and the shared responsibility table
- [Monitoring OS metrics with Enhanced Monitoring](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html) and [Setting up and enabling Enhanced Monitoring](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.Enabling.html): agent-based collection, granularity values and CloudWatch Logs delivery
- [Database load](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.Overview.ActiveSessions.html) and [Pricing and data retention for Database Insights](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.Overview.cost.html): average active sessions, dimensions and retention
- [Quotas and constraints for Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html): instance, snapshot, replica, proxy and storage quotas, and the maximum connection formulas
- [Amazon RDS pricing](https://aws.amazon.com/rds/pricing/) and [Amazon RDS Proxy pricing](https://aws.amazon.com/rds/proxy/pricing/): the billing dimensions, Reserved Instance terms and the per-vCPU proxy charge
