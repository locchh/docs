# Amazon Aurora

**Where it sits on the exams.** **Amazon Aurora** is the AWS-built relational database engine that is wire-compatible with MySQL and PostgreSQL but replaces the storage layer underneath with a distributed, self-healing volume shared by every instance in the cluster. It is managed through the same console and API as **Amazon Relational Database Service (Amazon RDS)**, the managed relational database service taught in [Amazon RDS](rds.md), but the architecture, the endpoints, the failover model and the pricing are its own. It appears in SAA-C03 tasks 3.3 and 4.3, where the guide names it explicitly as a database type to choose, and in SAP-C02 tasks 2.4 and 4.4, where it carries multi-Region reliability and purpose-built database selection. The rule of thumb the exam wants is that Aurora is the answer whenever a relational workload needs more availability, more read capacity or more elasticity than a single RDS instance can give, and that everything distinctive about Aurora follows from one design decision: compute and storage are separate.

## The shared storage layer and what it buys you

An Aurora DB cluster is one or more DB instances plus a single cluster volume, an SSD-backed virtual volume that holds all user data, schema objects, system tables and internal metadata. AWS divides that volume into 10 GiB segments and replicates each segment six ways across three Availability Zones, an Availability Zone being one or more isolated data centers inside an AWS Region. The quorum is six-way with a write set of four and a read set of three: Aurora issues every write to all six copies and acknowledges it once four confirm, and it satisfies a read from any three. That is why AWS documents the cluster as transparently tolerating the loss of up to two copies without affecting write availability and up to three copies without affecting read availability. The amount of replication is fixed by the storage design and does not depend on how many DB instances you run, so a single-instance Aurora cluster is already replicated across three Availability Zones.

Three consequences of that design are tested repeatedly. First, storage is self-healing: Aurora continuously scans data blocks and disks for errors and repairs a failed segment from the surviving copies, so a disk failure does not become a restore. Second, adding a reader is cheap and fast, because Aurora does not copy any data; the new instance simply attaches to the volume that already holds it. Removing an instance removes no data, and only deleting the cluster deletes the volume. Third, crash recovery is quick, because Aurora does not replay a redo log from the last checkpoint the way a conventional engine does; it recovers asynchronously on parallel threads and is typically available again in well under a minute. The page cache also lives in a process separate from the database, so after a restart the cache is still warm and the first queries do not have to refill it.

The volume grows on its own in 10 GiB segments as data arrives, with no provisioning step and no storage autoscaling setting to configure. The maximum size depends on the engine version: 128 TiB for most versions, rising to 256 TiB on Aurora PostgreSQL 15.13, 16.9 and 17.5 and higher and on Aurora MySQL 3.10 and higher. Current versions also shrink the allocated space when you drop a table or a database, so storage charges fall again. You are billed for the space actually used and for one logical copy of it, not six, which is the single biggest reason an Aurora cluster can cost less than the equivalent self-managed replication topology on **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service. Backups are continuous to **Amazon Simple Storage Service (Amazon S3)**, the Regional object storage service, with no performance impact on the database.

## Clusters, endpoints, replicas and failover

A cluster has exactly one writer, called the primary instance, and up to 15 **Aurora Replicas**, also called reader instances, which serve read-only traffic and act as failover targets. Because every replica reads the same cluster volume rather than applying a replication stream, replica lag is usually far below 100 milliseconds and heavy writes on the primary do not push the readers behind the way engine-level replication does. This is the sharpest distinction to carry into the exam: an RDS read replica is a separate instance with its own copy of the data, promoted by hand, while an Aurora Replica shares the volume and is promoted automatically.

Four endpoint types route connections, and picking the wrong one is a common distractor. The cluster endpoint, also called the writer endpoint, always resolves to the current primary and is what write traffic and data definition language statements use; after a failover it points at the new primary with no application change. The reader endpoint balances connections across the available Aurora Replicas and is what read-only traffic should use. An instance endpoint addresses one specific DB instance and exists for diagnosis and tuning, which is exactly why it is the wrong answer in any availability scenario: it does not move during a failover. A custom endpoint addresses a named subset of instances, which is how you send reporting connections to the two large readers and application connections to the small ones inside a single cluster; the default quota is five custom endpoints per DB cluster. A global cluster adds a fifth type, covered in the Global Database section below.

Failover is automatic when the cluster has at least one replica. Aurora promotes a replica, repoints the cluster endpoint, and service is typically restored in less than 60 seconds and often in less than 30. If the cluster has no replica, Aurora creates a new primary instance instead, which typically takes under 10 minutes, so a single-instance Aurora cluster is durable but not highly available. You choose the promotion target with failover priority tiers numbered 0 for the highest priority through 15 for the lowest. Aurora promotes the healthy replica in the best tier; if two share a tier it promotes the larger instance, and if they share a tier and a size it picks one arbitrarily. Changing a priority never triggers a failover, and after five unsuccessful failover attempts Aurora stops honoring the tiers. Putting the one reader that is sized like the writer in tier 0 and the small reporting readers in tier 15 is how you keep a failover from landing on an instance too small to carry production.

**Aurora Auto Scaling** adds and removes Aurora Replicas against a target-tracking policy, driven by a predefined metric such as average CPU utilization or by a custom metric, between a minimum and maximum you set. It only ever scales readers, never the writer; new replicas take the primary's instance class and the lowest promotion priority, 15, so a manually created replica is still promoted first; and it only removes replicas it created itself. For connection pooling in front of a cluster, [Amazon RDS](rds.md) owns **Amazon RDS Proxy**, the managed connection pooler, which also cuts Aurora failover time by up to 66 percent by bypassing DNS caching.

## Capacity and cost shape: provisioned, serverless and I/O-Optimized

Each instance in a cluster is either provisioned, meaning you pick a DB instance class and pay for it by the hour, or serverless, meaning you set a capacity range and Aurora sizes the instance continuously. **Aurora Serverless v2**, which the AWS documentation now calls simply Aurora serverless after the retirement of the first version, uses the `db.serverless` instance class and measures capacity in Aurora capacity units (ACUs), each roughly 2 GiB of memory with matching CPU and networking. The supported range is 0 to 256 ACUs in increments of 0.5, and scaling happens in half-ACU steps while statements are running, with no pause and no failover. Setting the minimum to 0 turns on automatic pause: after an idle interval you choose, from 300 seconds, which is the default, to 86,400 seconds, the instance pauses and stops accruing capacity charges, then resumes when a connection arrives. Readers in promotion tiers 0 and 1 scale in step with the writer so that they can take over on failover; readers in tiers 2 through 15 scale independently, which is what lets a reporting reader grow while the writer stays small.

The original **Aurora Serverless v1** is gone. AWS set its end of life at March 31, 2025, stopped allowing new v1 clusters and instances on January 8, 2025, and the user guide no longer documents it. Treat any exam option that names Serverless v1 as wrong, and read a stem that says "serverless relational database" as Aurora Serverless v2.

Storage is billed under one of two cluster storage configurations, and the choice is pure arithmetic. **Aurora Standard** charges for storage per GB-month plus a rate per million I/O requests. **Aurora I/O-Optimized** charges nothing for read and write I/O at all, in exchange for higher instance and storage rates. AWS publishes the crossover explicitly: choose Aurora I/O-Optimized when I/O spending is 25 percent or more of total Aurora spending, and Aurora Standard when it is less. You can switch from I/O-Optimized to Standard at any time but only into I/O-Optimized once every 30 days, and the switch is non-disruptive except on NVMe-based instance classes, which need an engine restart.

The three deployment shapes a question is most likely to put side by side are provisioned, serverless and **Aurora Global Database**. Read the table for what each one is for, remembering that Global Database is a topology rather than a third capacity mode: a global cluster's instances are themselves provisioned or serverless, and the two Regions may even use different storage configurations.

| | Aurora provisioned | Aurora Serverless v2 | Aurora Global Database |
|---|---|---|---|
| What you get | Fixed-size writer and readers in one Region | Writer and readers that resize themselves in one Region | One primary cluster plus up to 10 read-only secondary Regions |
| How capacity is set | You choose a DB instance class per instance and change it with a modify and a restart | You set a cluster capacity range of 0 to 256 ACUs and Aurora moves inside it in 0.5-ACU steps | Each Region's cluster is sized independently, provisioned or serverless, and a secondary may be headless |
| Failover behavior | Automatic promotion of a replica by tier, typically under 60 seconds in-Region | Identical to provisioned, plus a resume from a paused instance | In-Region failover as usual, plus cross-Region switchover with no data loss or managed failover with an RPO in seconds |
| Cost shape | Instance-hours, plus storage and either per-I/O or I/O-Optimized rates; Reserved Instances available | ACU-seconds while running, nothing while paused; no Reserved Instance commitment | Every Region's instances and storage, plus replicated write I/Os on either configuration, and cross-Region data transfer. Standard and cross-Region data transfer |
| Requirement wording that selects it | "steady, predictable load", "MOST cost-effective for a database that runs 24 hours a day" | "unpredictable or spiky traffic", "development and test databases that sit idle", "scale automatically without provisioning" | "survive the loss of an entire Region", "low-latency reads for users on other continents", "RPO of seconds across Regions" |

## Aurora Global Database across Regions

An Aurora global database is one primary cluster that accepts writes and up to 10 read-only secondary clusters in other Regions. Replication happens in the storage layer over dedicated infrastructure rather than through the database engine, so it costs the primary almost nothing in performance and typical replication latency is under a second. A secondary cluster is read-only and can carry up to 16 read-only instances, one more than a standalone cluster, and it can be created headless, with no instances at all, which gives a Region a continuously updated copy of the data at storage cost only until the day you need it. The global writer endpoint always points at the writer of whichever cluster is currently primary, so the connection string does not encode a Region and does not change when the primary moves. Write forwarding lets applications in a secondary Region send write statements to a local endpoint; Aurora forwards them to the primary with their session and transaction context, applies them there, and replicates the result back, so the primary remains the single source of truth.

Two different operations move the primary, and the exam separates them by the word "planned". A switchover, previously called managed planned failover, is for healthy clusters and controlled events such as a Regional rotation: Aurora waits for the chosen secondary to catch up fully, makes the old primary read-only, then promotes the secondary, so the recovery point objective (RPO) is zero and no data is lost. A managed failover is for an unplanned outage in the primary Region: it does not wait for synchronization, so the RPO is a non-zero value measured in seconds, equal to the replication lag at the moment of failure. AWS documents the recovery time objective (RTO) for a global database in the order of minutes, with a secondary promoted to full read and write in under a minute, and after a managed failover it automatically re-adds the old Region as a secondary and rebuilds the other secondaries, which can take minutes to hours depending on volume size and distance. Both clusters must run the same major and minor engine version for either operation; a manual failover, meaning detach the secondary and promote it yourself, is the fallback when they do not.

Watch the metric and the caveats. `AuroraGlobalDBRPOLag` reports how far behind each secondary is in milliseconds, and choosing the least-lagged secondary is how you minimize data loss in an unplanned failover. Aurora PostgreSQL adds the `rds.global_db_rpo` parameter, which enforces an upper bound on RPO by blocking commits on the primary when a secondary falls too far behind, so it trades write throughput for a guarantee. **Backtrack** is not supported on a global database, Aurora Auto Scaling does not work on secondary clusters, and the individual clusters in a global database cannot be stopped or started. Finally, a global database is replication, not backup: a bad migration propagates to every secondary in about a second, which is why [backup and disaster recovery](../01-storage/backup-and-disaster-recovery.md) insists on keeping point-in-time backups in the recovery Region as well.

> **Professional depth.** Global failover has a split-brain hazard worth naming. Aurora tries to block writes in the old primary Region but does not guarantee it, so AWS advises lowering the DNS time to live on the global writer endpoint to a low value such as five seconds, or waiting for the RDS event that confirms the endpoint's DNS change, before restarting write traffic. Configuration is not inherited either: cluster parameter groups, alarms, and integrations with **AWS Secrets Manager**, the managed secret store, and **AWS Lambda**, the serverless function service, all have to exist in the secondary Region before the day you need them.

## Backups, Backtrack and fast cloning

Automated backups are always on for Aurora and cannot be disabled. They are continuous and incremental to Amazon S3, they impose no performance penalty, and the retention period is 1 to 35 days with a default of one day however the cluster is created. Point-in-time recovery restores to any second in that window, with the latest restorable time trailing the present by about five minutes, and a restore always builds a new cluster rather than rewinding the existing one. Manual DB cluster snapshots never expire, the default quota is 100 per Region, and a snapshot can be shared with up to 20 accounts within the same Region or made public; snapshots taken through **AWS Backup**, the centralized backup service, count as manual snapshots but do not consume that quota. Encryption follows the RDS rules exactly: a key from **AWS Key Management Service (AWS KMS)**, the managed cryptographic key service, chosen at creation and never afterward, so encrypting an existing cluster means snapshot, encrypted copy, restore.

Backtrack is the Aurora-only answer to a bad write, and it exists for Aurora MySQL only. It rewinds the cluster volume in place to a chosen second, in minutes rather than the hours a restore takes, and you can move back and forth repeatedly to find the moment a change happened. The target backtrack window can be up to 72 hours, and you pay an hourly rate for the change records that make it possible; the actual window can fall short of the target under a heavy write load. The limitations decide questions: Backtrack must be enabled when the cluster is created or restored and can never be added to a running cluster, it affects the whole cluster rather than one table, it causes a brief disruption during which Aurora closes connections, it is unavailable on Aurora PostgreSQL, and it is incompatible with Aurora Global Database and with cross-Region read replicas.

Fast cloning creates a second cluster that initially shares the source cluster's data pages through a copy-on-write protocol. The clone is available in minutes regardless of volume size, and it costs almost nothing until the two diverge, because Aurora allocates new storage only for pages that either side changes. That makes it the standard answer for "give the test team a full copy of production today without doubling the storage bill" and for pre-upgrade rehearsals. You can create up to 15 copy-on-write clones from a volume; the sixteenth is a full copy. Clones can also cross accounts when the source cluster is shared through **AWS Resource Access Manager (AWS RAM)**, the resource sharing service, which is how a central production account hands an analytics account a dataset without copying it or granting database credentials.

## Beyond the standard engine: analytics, integrations and the newer Aurora services

Parallel query is an Aurora MySQL optimization that pushes row retrieval, column extraction and predicate evaluation down into the distributed storage nodes instead of dragging every scanned page back to one instance. It pays off on long analytic scans over tables with millions of rows, needs no SQL changes or hints, and Aurora decides by itself when to apply it. Two traps: it is Aurora MySQL only, and the identically named PostgreSQL feature is unrelated.

The **RDS Data API** removes the connection entirely. It exposes a secure HTTPS endpoint with AWS SDK integration, takes database credentials from AWS Secrets Manager rather than from the caller, and now works with both Aurora serverless and provisioned clusters. Its value in an exam scenario is that a Lambda function can query Aurora without being attached to the **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network for AWS resources, and without holding a pooled connection. Aurora zero-ETL integrations replicate transactional data into **Amazon Redshift**, the data warehouse, or a lakehouse in **Amazon SageMaker AI**, the managed machine learning platform, within seconds of the write, with no pipeline to build or operate, which is the keyed answer when a stem asks for near real-time analytics on operational data with the least operational overhead. **Aurora machine learning** goes the other way, letting SQL statements call **Amazon Bedrock**, the managed foundation model service, **Amazon Comprehend**, the natural language processing service, or SageMaker AI endpoints and return the result as a column.

**Babelfish for Aurora PostgreSQL** adds a second listener to an Aurora PostgreSQL cluster that speaks the SQL Server Tabular Data Stream wire protocol on port 1433 alongside the PostgreSQL protocol on 5432. Applications written for SQL Server connect with their existing drivers and mostly unchanged T-SQL, which turns a heterogeneous migration off SQL Server into something far closer to a lift and shift. Where the application code can be changed, the conventional path is instead schema and code conversion with the **AWS Schema Conversion Tool**, which converts a schema between database engines followed by a data move with **AWS Database Migration Service (AWS DMS)**, the managed service that migrates and replicates data between databases, covered in [AWS DMS and AWS SCT](../10-migration/dms-and-sct.md). **Aurora PostgreSQL Limitless Database** is the horizontal scaling option: instead of writer and reader instances, the cluster holds a DB shard group that spreads writes across shards and routers, scaling past the write ceiling of a single writer to millions of transactions per second and petabytes of data. It is Aurora PostgreSQL only, requires the Aurora I/O-Optimized configuration, takes a shard group maximum capacity between 16 and 6,144 ACUs, and is limited by default to five shard groups per Region.

**Amazon Aurora DSQL** is easy to mistake for an Aurora deployment option and is not one. It is a separate serverless, distributed SQL service with its own user guide and API, compatible with PostgreSQL 16, with no instances or capacity to size, active-active multi-Region clusters and up to 99.999 percent availability. It has no MySQL compatibility, no cluster volume, and none of the Aurora features in this unit. Choose it when a stem asks for a relational database with active-active writes in more than one Region and no infrastructure management; choose Aurora Global Database when the stem describes one writable Region with read-only copies elsewhere.

## Professional depth

At organization scale the first Aurora questions are about who holds the data and who holds the key. Cross-account recovery depends on a snapshot and a KMS key both being shareable, so a snapshot encrypted with the AWS managed key cannot be shared at all and every production cluster in a multi-account design must use a customer managed key from creation. The same rule makes cross-account cloning through AWS RAM attractive: a clone costs storage only for divergence, so a production account can give five downstream accounts a full copy of a 40 TiB database for a fraction of five full restores.

The quotas that bite in a migration are worth memorizing together, because they are the ones a Professional question makes you raise before a cutover rather than during it. The default is 40 DB instances per Region shared across Amazon RDS, Aurora, **Amazon Neptune**, the graph database, and **Amazon DocumentDB**, the MongoDB-compatible document database, counted together; 40 Aurora DB clusters per Region; 100 manual DB cluster snapshots per Region; 15 Aurora Replicas per primary; five custom endpoints per cluster; five IAM roles per cluster; and five DB shard groups per Region for Limitless. Most are adjustable through Service Quotas, and a raise takes time.

Several failure modes only appear where features meet. Backtrack cannot coexist with a global database, so a design that wants both a 72-hour rewind and a second Region has to choose the global database and fall back on point-in-time restore for logical damage. Aurora Auto Scaling does not operate on secondary clusters, so read capacity in a secondary Region is provisioned by hand or supplied by serverless readers that scale on their own. Switching to Aurora I/O-Optimized is allowed only once every 30 days, so an experiment costs a month. A serverless instance that keeps hitting its maximum ACU value is flagged with an `incompatible-parameters` status that blocks operations such as engine upgrades until pressure falls or the ceiling rises, which makes the maximum a governance setting and not just a budget cap. And a cluster whose only instance is the writer has no failover target: Aurora recreates the primary, typically in under 10 minutes, against under 60 seconds when a replica exists.

Finally, the cost conversation at scale is usually about I/O rather than instances, and a global database is where the arithmetic is most often done backwards. Replicated write I/Os in every secondary Region are billed on both Aurora Standard and Aurora I/O-Optimized, so going global does not by itself push a cluster past the point where I/O-Optimized wins. AWS's own worked examples show Standard remaining the cheaper configuration for a global workload. Decide the configuration from the share of spend that is I/O, roughly a quarter or more favoring I/O-Optimized, and treat replicated write I/Os and cross-Region data transfer as a separate cost of being global that neither configuration removes.

## Worked scenario

A ticketing company runs its inventory and checkout database on a self-managed MySQL server that struggles at on-sale events. It wants the database on AWS with no schema change. Traffic is extremely spiky: quiet for days, then 40 times normal load for an hour when a major event goes on sale. Reporting and fraud analysis must not touch checkout. A Regional outage must be survivable with a recovery point measured in seconds and a recovery time under fifteen minutes, and the risk that keeps the operations team awake is a bad deployment that corrupts inventory rows, which last quarter took six hours to unwind from backups.

The design is an Aurora MySQL cluster. The writer and one reader in tier 0 run as Aurora Serverless v2 instances with a capacity range wide enough to cover both the quiet period and the on-sale spike, so the cluster grows in half-ACU steps within seconds instead of waiting for an instance class change, and shrinks again afterward. Two more serverless readers in tier 15 sit behind a custom endpoint that reporting and fraud analysis connect to, so their queries never touch the writer's capacity and never become the failover target. Checkout connects to the cluster endpoint and read-only pages to the reader endpoint. Because the spike drives heavy I/O against a modest amount of storage, the cluster runs Aurora I/O-Optimized once the team confirms that I/O is more than a quarter of the bill.

Regional recovery is an Aurora global database with one secondary Region, created headless so it costs storage and replication only, with instances added at failover time or kept as a small serverless reader for local reads. Replication lag under a second meets the seconds-level RPO, and a managed failover promotes the secondary to read and write in under a minute, comfortably inside a fifteen-minute RTO, with the global writer endpoint sparing the application a connection string change. The corruption risk is handled separately, because a global database would replicate the bad write faithfully: Backtrack is enabled at creation with a 24-hour target window, so a bad deployment is rewound in minutes rather than restored in hours. The cluster is created encrypted with a customer managed KMS key, since encryption cannot be added later, and nightly clones give the test team a full copy of production at the cost of the pages they change.

The exam asks how to give the company a database that absorbs a 40-fold spike without provisioning for peak all month and still recovers an accidental mass update in minutes. The keyed answer is Aurora Serverless v2 with Backtrack enabled. Provisioned instances sized for the spike are the distractor that meets the performance requirement while paying for peak capacity around the clock, and point-in-time restore is the distractor that recovers the data but rebuilds a new cluster instead of rewinding this one.

## Exam lens

- "MySQL or PostgreSQL compatible, but more available and more scalable than a single instance" maps to Aurora; plain RDS is the distractor when the stem also asks for sub-second replica lag or 15 readers.
- "Survive the failure of an Availability Zone with no data loss" maps to the cluster volume's six copies across three Availability Zones, which exist even with one instance; but add a replica, because a single-instance cluster has no fast failover.
- "Failover in under a minute" maps to promoting an Aurora Replica; "under 10 minutes" is what you get when the cluster has no replica and Aurora must build a new primary.
- "Control which instance is promoted" maps to failover priority tiers 0 through 15, with the larger instance winning a tie inside a tier.
- "Send reporting to specific instances in the same cluster" maps to a custom endpoint; the reader endpoint is the distractor because it balances across all replicas, and the instance endpoint is the distractor because it does not move during a failover.
- "Unpredictable or intermittent traffic", "scale to zero when idle" maps to Aurora Serverless v2 with a minimum of 0 ACUs and automatic pause; anything naming Aurora Serverless v1 is wrong, since it reached end of life on March 31, 2025.
- "I/O charges dominate the bill" maps to Aurora I/O-Optimized, and AWS's threshold is I/O at 25 percent or more of total Aurora spend.
- "Planned Regional rotation with no data loss" maps to a global database switchover, RPO zero; "recover from an unplanned Regional outage" maps to managed failover, RPO non-zero and measured in seconds.
- "Writes from a secondary Region without managing a second endpoint" maps to write forwarding, not to a second writable cluster.
- "Low-latency reads on three continents from one database" maps to Aurora Global Database with read-only secondaries; "writes accepted in more than one Region" maps to Amazon Aurora DSQL instead.
- "Undo a bad bulk update in minutes" maps to Backtrack on Aurora MySQL, up to a 72-hour window, enabled at creation only; point-in-time restore is the distractor because it creates a new cluster.
- "A full copy of production for testing without doubling storage cost" maps to fast cloning with copy-on-write; a snapshot restore is the distractor because it copies everything and costs full storage.
- "Long analytic scans over a very large Aurora MySQL table" maps to parallel query; on Aurora PostgreSQL the same wording points at a reader or at Amazon Redshift.
- "Query Aurora from Lambda without VPC configuration or connection pooling" maps to the RDS Data API.
- "Near real-time analytics on transactional data with no pipeline to maintain" maps to a zero-ETL integration with Amazon Redshift or the SageMaker AI lakehouse.
- "SQL Server application must keep its drivers and most of its T-SQL" maps to Babelfish for Aurora PostgreSQL; a heterogeneous migration with schema conversion is the distractor when the stem says the application code cannot change.
- "Write throughput beyond a single writer, sharded automatically" maps to Aurora PostgreSQL Limitless Database, which requires Aurora I/O-Optimized.

## Knowledge check

### 1. Reporting queries competing with checkout (Associate)

A retailer runs an Amazon Aurora MySQL DB cluster with a writer and three Aurora Replicas of different sizes. The two largest replicas are meant to serve a nightly reporting tool, and the smallest exists only to absorb overflow read traffic from the website. Today the reporting tool connects to the cluster's reader endpoint and its queries sometimes land on the small replica, where they time out. The company wants reporting to use only the two large replicas, without creating another cluster.

Which solution will meet these requirements?

- **A)** Create a custom endpoint that includes only the two large Aurora Replicas and point the reporting tool at it.
- **B)** Point the reporting tool at the instance endpoint of the largest Aurora Replica.
- **C)** Point the reporting tool at the cluster endpoint so that queries run on the writer.
- **D)** Set the failover priority of the two large Aurora Replicas to tier 0 so that the reader endpoint prefers them.

<details><summary>Answer</summary>

**Answer: A.** A custom endpoint addresses a named subset of the DB instances in a cluster, which is exactly the case AWS describes for clusters whose instances have different capacities, and the default quota of five per cluster leaves plenty of room. B sends all reporting to one instance and, because an instance endpoint never moves, leaves reporting broken if that instance is replaced or promoted. C puts analytic queries on the writer, which is the contention the company is trying to remove. D misreads promotion tiers: they decide which replica is promoted during a failover and have no effect on how the reader endpoint balances connections.

*Where this is covered: Clusters, endpoints, replicas and failover.*

</details>

### 2. A database that is idle most of the week (Associate)

A university runs a course registration application on an Amazon Aurora PostgreSQL DB cluster provisioned on a db.r6g.4xlarge instance. The database is idle for weeks at a time and then handles very heavy traffic during two registration windows each year. Finance has asked for the lowest possible cost for a database that is unused most of the year, while keeping the ability to handle the registration peak.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Convert the DB instances to Aurora Serverless v1 so that the cluster pauses when idle.
- **B)** Convert the DB instances to Aurora Serverless v2 with a minimum capacity of 0 ACUs and a maximum high enough to cover the registration peak.
- **C)** Keep the provisioned instance and buy a three-year Reserved Instance to lower its hourly rate.
- **D)** Keep the provisioned instance and stop the DB cluster between registration windows, starting it before each window.

<details><summary>Answer</summary>

**Answer: B.** Aurora Serverless v2 scales between 0 and 256 ACUs in half-ACU increments, and a minimum of 0 ACUs turns on automatic pause, so an idle cluster stops accruing capacity charges and resumes when a connection arrives, while the maximum setting covers the peak. A is wrong because Aurora Serverless v1 reached end of life on March 31, 2025, and new v1 clusters could not be created after January 8, 2025. C commits to three years of an instance that is idle most of the year, which lowers the rate but not the waste. D looks close but an Aurora DB cluster that is stopped is automatically started again after seven days, and it still pays for storage while adding a manual step twice a year.

*Where this is covered: Capacity and cost shape: provisioned, serverless and I/O-Optimized.*

</details>

### 3. Recovering from a bad deployment (Associate)

A gaming company runs an Amazon Aurora MySQL DB cluster. A release contained a faulty migration script that overwrote several million rows with incorrect values, and the error was noticed 40 minutes later. The company needs the data as it was just before the script ran, on the same cluster and the same endpoint, as quickly as possible. The cluster was created with Backtrack enabled and a 24-hour target window.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Restore the cluster to a point in time 45 minutes ago, then repoint the application at the restored cluster's endpoint.
- **B)** Fail over to an Aurora Replica, which still holds the data as it was before the script ran.
- **C)** Create a clone of the cluster from before the migration and switch the application to the clone.
- **D)** Backtrack the DB cluster to a time just before the migration script ran.

<details><summary>Answer</summary>

**Answer: D.** Backtrack rewinds the cluster volume in place to a chosen second, completes in minutes, and keeps the same cluster and the same endpoints, which is exactly what the requirement asks for; the 24-hour window easily covers 40 minutes. A works but creates a new cluster, takes far longer, and forces an endpoint change. B misunderstands the architecture: Aurora Replicas read the same cluster volume as the writer, so they show the same incorrect rows within milliseconds. C is impossible as written, because a clone is created from the current state of the volume, not from a past point in time.

*Where this is covered: Backups, Backtrack and fast cloning.*

</details>

### 4. Surviving the loss of a Region (Associate)

A payments company runs an Amazon Aurora PostgreSQL DB cluster in eu-west-1. Regulators now require the service to keep operating if the entire Region becomes unavailable, with a recovery point objective measured in seconds and a recovery time objective of 15 minutes. The company does not want to pay for idle database instances running in the second Region while the primary is healthy.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create an Aurora global database with a secondary cluster in eu-central-1.
- **B)** Create a cross-Region Aurora Replica in eu-central-1 and configure Amazon RDS to promote it automatically when eu-west-1 fails.
- **C)** Create the secondary cluster as a headless cluster and add DB instances as part of the recovery runbook.
- **D)** Copy an automated DB cluster snapshot to eu-central-1 every hour and restore it when eu-west-1 fails.
- **E)** Enable Backtrack on the primary cluster with a 72-hour target window.

<details><summary>Answer</summary>

**Answer: A and C.** An Aurora global database replicates through the storage layer with typical latency under a second, which meets an RPO measured in seconds, and a managed failover promotes a secondary to read and write in under a minute, well inside a 15-minute RTO. Creating the secondary headless means the Region holds a live copy of the data at storage cost only, with instances added during recovery. B invents a feature: Aurora has no automatic cross-Region promotion of a replica, and cross-Region failover is a switchover or a managed failover on a global database. D gives an RPO of up to an hour plus restore time, which fails both objectives. E addresses logical corruption, not a Regional outage, and Backtrack is not supported on a global database at all.

*Where this is covered: Aurora Global Database across Regions.*

</details>

### 5. Choosing a storage configuration (Associate)

A media company runs an Amazon Aurora MySQL DB cluster on the Aurora Standard storage configuration, and its monthly bill is unpredictable. Reviewing the last six months of billing data, the team finds that charges for I/O operations are consistently about 40 percent of total Aurora spending and swing widely month to month. The company wants a more predictable bill without reducing throughput.

Which solution will meet these requirements?

- **A)** Switch the DB cluster to the Aurora Standard cluster storage configuration.
- **B)** Move the cluster to Aurora Serverless v2 so that capacity tracks demand.
- **C)** Switch the DB cluster to the Aurora I/O-Optimized cluster storage configuration.
- **D)** Add three Aurora Replicas so that read I/O is spread across more instances.

<details><summary>Answer</summary>

**Answer: C.** Aurora I/O-Optimized removes per-request read and write I/O charges entirely in exchange for higher instance and storage rates, and AWS states plainly that it is the better choice when I/O spending is 25 percent or more of total Aurora spending, which 40 percent clearly is. A is the configuration the cluster already effectively has, and it is the one that bills per million I/O requests. B changes how compute is sized and billed but leaves I/O charges untouched on Aurora Standard. D adds instances and therefore cost, and reads served by replicas still generate I/O against the cluster volume.

*Where this is covered: Capacity and cost shape: provisioned, serverless and I/O-Optimized.*

</details>

### 6. A planned move between Regions (Professional)

A logistics company runs an Aurora global database with a primary cluster in us-east-1 and secondary clusters in eu-west-1 and ap-southeast-2. Its head office is moving to Europe, and it has scheduled a two-hour window to make eu-west-1 the write Region. All clusters are healthy and run identical engine versions. The business will not accept the loss of a single committed transaction, and the application connects through the global writer endpoint.

Which solution will meet these requirements?

- **A)** Perform a managed failover of the global database to the eu-west-1 cluster.
- **B)** Perform a switchover of the global database to the eu-west-1 cluster.
- **C)** Detach the eu-west-1 cluster from the global database, promote it to a standalone cluster, and add us-east-1 back as a secondary afterward.
- **D)** Take a snapshot of the us-east-1 cluster, copy it to eu-west-1, restore it as a new cluster, and repoint the application.

<details><summary>Answer</summary>

**Answer: B.** A switchover, previously called managed planned failover, is the operation AWS documents for planned Regional rotation on a healthy global database: it synchronizes the target secondary with the primary first, makes the old primary read-only, then promotes the secondary, so the RPO is zero. It also preserves the replication topology, leaving ap-southeast-2 in place, and the global writer endpoint follows the new primary with no application change. A is the unplanned-outage operation and explicitly does not wait for synchronization, so it can lose transactions the business will not give up. C is the manual failover procedure, which is meant for cases where managed operations are unavailable, and it destroys and rebuilds the topology by hand. D takes far longer than the window, loses everything written after the snapshot, and abandons the global writer endpoint.

*Where this is covered: Aurora Global Database across Regions.*

</details>

### 7. Standing up test environments across accounts (Professional)

A financial services company runs a 30 TiB Amazon Aurora PostgreSQL DB cluster in a production account. Four development accounts in the same organization each need a full, writable copy of production at the start of every sprint. Copies are discarded after two weeks, and during that time each team changes roughly 2 percent of the data. Restoring snapshots into each account currently takes most of a day and quadruples the storage bill. The company wants the fastest and cheapest repeatable process.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Copy an encrypted DB cluster snapshot to each development account every sprint and restore a cluster from it.
- **B)** Add four cross-Region Aurora Replicas, one reachable from each development account, and promote each to a standalone cluster.
- **C)** Create an Aurora global database with four secondary clusters and give each development team a secondary Region.
- **D)** Share the production DB cluster through AWS Resource Access Manager and have each development account create a clone of it.

<details><summary>Answer</summary>

**Answer: D.** Aurora cloning uses a copy-on-write protocol at the storage layer, so a clone of a 30 TiB volume is ready in minutes and allocates new storage only for pages that diverge; at 2 percent divergence each account pays for a fraction of a full copy. Cross-account cloning is supported through AWS RAM, which is what lets development accounts clone a cluster the production account owns. A is the slow, expensive process the company already has. B is wrong twice: Aurora Replicas are read-only members of a cluster rather than per-account copies, and promotion is not how you hand a dataset to another account. C provides read-only secondaries in other Regions, not writable development copies, and it pays for full storage and replication in each one.

*Where this is covered: Backups, Backtrack and fast cloning.*

</details>

### 8. Modernizing a SQL Server estate (Professional)

A company is moving 60 applications off self-managed Microsoft SQL Server to reduce license cost. Twenty of them are third-party applications whose source code cannot be modified and which use SQL Server drivers and T-SQL stored procedures. The remaining forty are in-house applications that the development teams can change. The company wants to eliminate SQL Server licensing wherever possible and to minimize the code changes required.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Migrate the twenty unmodifiable applications to Aurora PostgreSQL with Babelfish enabled and point them at the TDS listener port.
- **B)** Migrate the twenty unmodifiable applications to Amazon RDS for SQL Server with the license-included model.
- **C)** Migrate the forty in-house applications to Aurora PostgreSQL, converting schemas and code with the AWS Schema Conversion Tool and moving data with AWS Database Migration Service.
- **D)** Migrate all sixty applications to Aurora MySQL with Babelfish enabled.
- **E)** Migrate all sixty applications to Amazon Aurora DSQL, which is PostgreSQL compatible and serverless.

<details><summary>Answer</summary>

**Answer: A and C.** Babelfish gives an Aurora PostgreSQL cluster a second listener that speaks the SQL Server Tabular Data Stream protocol on port 1433, so applications keep their existing SQL Server drivers and most of their T-SQL, which is the only option that removes the SQL Server license for code that cannot be changed. For the applications the teams can change, a conventional heterogeneous migration with schema conversion and AWS DMS is the documented path. B keeps paying SQL Server licenses, which is the cost the company is trying to remove. D is wrong because Babelfish is a feature of Aurora PostgreSQL only and does not exist for Aurora MySQL. E misapplies Aurora DSQL: it is a separate distributed SQL service with no SQL Server compatibility, and moving sixty applications to it would require more change, not less.

*Where this is covered: Beyond the standard engine: analytics, integrations and the newer Aurora services.*

</details>

## Summary

Aurora starts from one decision, separating compute from storage, and every exam-relevant behavior follows from it. The cluster volume keeps six copies of every 10 GiB segment across three Availability Zones, needs four for a write and three for a read, repairs itself, and grows on its own toward 128 TiB or 256 TiB on the newest engine versions, so durability is free of instance count and adding a reader copies nothing. From there the decisions are: how many Aurora Replicas and in which promotion tiers, which endpoint each workload uses, whether instances are provisioned or Aurora Serverless v2 with a 0 to 256 ACU range and automatic pause, whether storage is billed per I/O on Aurora Standard or flat on Aurora I/O-Optimized above the 25 percent threshold, and whether the cluster stretches into other Regions as a global database, where a planned switchover loses nothing and an unplanned managed failover costs seconds of data. Around that core sit the tools that answer specific stems: Backtrack for rewinding Aurora MySQL in minutes, cloning for cheap full copies, parallel query, the Data API, zero-ETL, Babelfish, Limitless for sharded write scale, and Aurora DSQL when writes must be accepted in several Regions at once.

## Related units

- [Amazon RDS](rds.md): the engines, the Multi-AZ comparison, RDS Proxy and the backup rules Aurora inherits
- [Amazon DynamoDB](dynamodb.md): the non-relational alternative and the access-pattern test that decides between them
- [Amazon ElastiCache and Amazon MemoryDB](elasticache-and-memorydb.md): caching in front of Aurora to cut read load and latency
- [Amazon Redshift](redshift.md): the zero-ETL destination and the line between operational and analytic stores
- [Backup and disaster recovery](../01-storage/backup-and-disaster-recovery.md): the cross-Region recovery table, AWS Backup plans and the DR strategy bands
- [AWS DMS and AWS SCT](../10-migration/dms-and-sct.md): homogeneous and heterogeneous migrations into Aurora
- [AWS KMS](../07-security/kms-and-cloudhsm.md): customer managed keys and cross-account grants for shared snapshots and clones
- [Amazon VPC](../04-networking/vpc.md): subnet groups, security groups and the private network path to a cluster

## Sources

- [Amazon Aurora storage](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.StorageReliability.html) and [Amazon Aurora reliability](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.Reliability.html): the cluster volume and what it contains, the two storage configurations and the 25 percent I/O threshold, storage auto-repair, the survivable page cache and recovery from unplanned restarts
- [Availability and Durability (Aurora extended content)](https://docs.aws.amazon.com/rds/latest/auroraextendedcontent/aurora-faq-availability-and-durability.html): 10 GiB segments replicated six ways across three Availability Zones, the two-copy and three-copy loss tolerances, promotion tiers, and promotion of a secondary Region in under a minute
- [High availability for Amazon Aurora](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html): six storage nodes per write, up to 15 Aurora Replicas, failover times, promotion tiers 0 to 15 and the tie-break rules
- [Amazon Aurora connection management](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.Endpoints.html): cluster, reader, instance, custom and global writer endpoints
- [Replication with Amazon Aurora](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Replication.html): shared-storage replication and replica lag under 100 milliseconds
- [Amazon Aurora Auto Scaling with Aurora Replicas](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Integrating.AutoScaling.html): readers only, instance class inheritance and promotion tier 15
- [Quotas and constraints for Amazon Aurora](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_Limits.html): 40 instances and clusters per Region, 100 manual cluster snapshots, five custom endpoints, five shard groups, and the 128 TiB and 256 TiB volume maximums by engine version
- [Using Aurora serverless](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html) and [Requirements and limitations for Aurora serverless](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.requirements.html): use cases, the advantages over provisioned instances, the capacity range in 0.5 ACU increments and the db.serverless instance class
- [How Aurora serverless works](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.how-it-works.html): ACU definition, the 0 to 256 ACU range, six copies of data, and reader scaling by promotion tier
- [Scaling to Zero ACUs with automatic pause and resume for Aurora serverless](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2-auto-pause.html): the 300 to 86,400 second interval, the default, and what resumes an instance
- [Document history for Amazon Aurora](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/WhatsNew.html): the Aurora Serverless v1 end-of-life date of March 31, 2025 and the January 8, 2025 stop on new v1 clusters
- [Using Amazon Aurora Global Database](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html) and [Using write forwarding in an Amazon Aurora global database](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-write-forwarding.html): up to 10 secondary Regions, storage-layer replication under a second, 16 readers per secondary, the global limitations including Backtrack and Auto Scaling, and how secondaries forward writes with session and transaction context
- [Using switchover or failover in Amazon Aurora Global Database](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html): RTO in minutes, RPO in seconds, switchover with RPO zero, managed compared with manual failover, AuroraGlobalDBRPOLag and the DNS time-to-live guidance
- [Overview of backing up and restoring an Aurora DB cluster](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Managing.Backups.html): continuous incremental backups, the 1 to 35 day retention range, the one-day default and the fact that backups cannot be disabled
- [Backtracking an Aurora DB cluster](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Managing.Backtrack.html): Aurora MySQL only, the 72-hour window limit, enablement at creation only, and the cross-Region replica restriction
- [Cloning a volume for an Amazon Aurora DB cluster](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Managing.Clone.html): the copy-on-write protocol, storage billing for diverged pages, the 15-clone limit and cross-account cloning with AWS RAM
- [Parallel query for Amazon Aurora MySQL](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-mysql-parallel-query.html): pushdown to storage nodes, the workloads it suits, and the warning that PostgreSQL parallel query is unrelated
- [Using the Amazon RDS Data API](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html) and [Supported Regions and Aurora DB engines for RDS Data API](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.Aurora_Fea_Regions_DB-eng.Feature.Data_API.html): the HTTP endpoint, Secrets Manager credentials, and support for serverless and provisioned clusters
- [Aurora zero-ETL integrations](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/zero-etl.html): near real-time replication into Amazon Redshift and the Amazon SageMaker AI lakehouse
- [Using Babelfish for Aurora PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/babelfish.html): the TDS listener on port 1433 alongside PostgreSQL on 5432
- [Using Amazon Aurora machine learning](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-ml.html): SQL access to Amazon Bedrock, Amazon Comprehend and SageMaker AI
- [Aurora PostgreSQL Limitless Database requirements and considerations](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/limitless-reqs-limits.html): I/O-Optimized requirement, shard group capacity of 16 to 6,144 ACUs and five shard groups per Region
- [What is Amazon Aurora DSQL?](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/what-is-aurora-dsql.html): a separate serverless distributed SQL service, PostgreSQL 16 compatible, multi-Region with up to 99.999 percent availability
- [Stopping and starting an Amazon Aurora DB cluster](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-cluster-stop-start.html): the seven-day stop limit and automatic restart
- [Amazon Aurora pricing](https://aws.amazon.com/rds/aurora/pricing/): the billing dimensions, ACU-hour charging, and replicated write I/Os in secondary Regions, billed on both Standard and I/O-Optimized
- [Amazon Aurora under the hood: quorum and correlated failure](https://aws.amazon.com/blogs/database/amazon-aurora-under-the-hood-quorum-and-correlated-failure): the six-way quorum with a write set of four and a read set of three
