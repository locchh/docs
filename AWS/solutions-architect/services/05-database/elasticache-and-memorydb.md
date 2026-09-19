# Amazon ElastiCache and Amazon MemoryDB

**Where it sits on the exams.** **Amazon ElastiCache** is the managed in-memory data store that sits in front of a database and answers repeated reads in microseconds instead of milliseconds, and **Amazon MemoryDB** is its sibling: the same in-memory engines and APIs, but durable enough to be the database itself rather than a copy of one. ElastiCache owns SAA-C03 task 2.1 for caching strategies and tasks 3.3 and 4.3 for high-performing and cost-optimized database design, and both services carry SAP-C02 task 2.4 for replication strategies, task 2.5 for caching, buffering and replicas, and task 4.4 for purpose-built database selection. The rule of thumb the exam wants is that ElastiCache is the answer when the same small result is read over and over and losing it would only be slow, while MemoryDB is the answer when the in-memory store is the system of record and losing it would be data loss.

## What these services are and where a cache belongs

An in-memory data store keeps its working set in RAM rather than on disk. That single property produces microsecond read latency and throughput an order of magnitude above a disk-backed engine, which is why a cache in front of a relational database both cuts page load times and lets the database run on a smaller instance class. ElastiCache is fully compatible with the open source engines it runs, so existing client libraries and commands work unchanged.

The pattern that matters for the exam is cache-aside: the application asks the cache first, and only on a miss queries the database and stores the result. What lives in the cache is usually a query result, a session, a rendered fragment, a leaderboard or a rate-limit counter, not the whole table. ElastiCache fronts **Amazon Relational Database Service (Amazon RDS)**, the managed relational database service, **Amazon Aurora**, the AWS-built MySQL and PostgreSQL compatible engine, and **Amazon DynamoDB**, the managed key-value and document database, and it equally caches results that no single database produced.

Several AWS services cache, and a question separates them by where the cached copy sits. Content and whole HTTP responses at the network edge belong to **Amazon CloudFront**, the content delivery network, taught in [Amazon CloudFront](../04-networking/cloudfront.md). Responses from a REST API belong to the response cache in **Amazon API Gateway**, the managed API front door. Items read from a DynamoDB table by key belong to **Amazon DynamoDB Accelerator (DAX)**, the DynamoDB-specific write-through cache taught in [Amazon DynamoDB](dynamodb.md), which needs no cache-aside code because it speaks the DynamoDB API. Everything else, meaning values the application stores and invalidates itself, belongs to ElastiCache. SAP-C02 pairs caching with buffering in the same bullet, and the distinction is direction: a cache absorbs reads by keeping a copy, while a buffer absorbs writes by holding work until a consumer is ready, which is [**Amazon SQS**](. The distinction decides questions. A cache serves a read that would otherwise hit the database, so it helps only when the same value is read repeatedly and it may serve a stale copy. A buffer absorbs a write the downstream system cannot take yet, so it helps when arrivals are spiky rather than repetitive, and nothing is lost when the consumer catches up. A replica does neither: it adds another copy that can serve reads consistently but costs a full instance. When a stem says the database is overwhelmed, decide first whether the pressure is repeated reads, bursty writes, or steady read volume, because those three answers are a cache, a queue and a read replica respectively../06-integration/sqs.md), the managed message queue.

Knowing when a cache is the wrong answer is tested as often as knowing when it is right. Under cache-aside, every miss costs three round trips rather than one, so a workload with little repetition pays a latency penalty and gets nothing back, and a write-heavy workload whose values are read once fills memory with data nobody asks for. A read that must reflect the write it follows cannot be served from a cache at all, because a cached copy is stale by construction until it is invalidated or expires, and a cache in front of a read replica compounds that staleness. A freshly replaced node is also empty, so a design that assumes a warm cache turns one node replacement into a flood of database queries. The right response is a different tool: a larger or read-scaled database, a queue, or MemoryDB if the data must live in memory and survive.

## Engines and deployment options

ElastiCache runs three engines. **Valkey** is the open source fork of Redis OSS 7.2, created in March 2024 after the Redis license changed and now stewarded by the Linux Foundation; it keeps the same data structures and is where every new ElastiCache capability lands. **Redis OSS** is the original engine, still supported at all versions up to and including 7.1, on both node-based clusters and serverless, with paid Extended Support once a major version passes its end of standard support date. **Memcached** is the simple, multi-threaded object cache, with no complex data types, no replication and no failover.

No AWS page says "use Valkey" in those words, but the evidence points one way. Valkey is priced 20 percent lower per node than Redis OSS and 33 percent lower on serverless, where its minimum metered storage is 100 MB against 1 GB for the other engines. It gives roughly 20 percent better memory efficiency, an existing Redis OSS reservation carries over to Valkey nodes in the same family at 20 percent more value, and an in-place upgrade from any supported Redis OSS version runs without downtime. Vector and full-text search and the durability option described later exist only on Valkey. Treat Valkey as the engine for new work and Redis OSS as a migration source, while reading an exam stem written around "Redis" as describing the same feature set.

The second choice is the deployment model. **ElastiCache Serverless** creates a cache from a name in under a minute, replicates data across three Availability Zones, an Availability Zone being one or more isolated data centers inside an AWS Region, carries a 99.99 percent availability service level agreement, and scales continuously with no capacity to plan. A node-based cluster instead has you pick the node type, count and Availability Zone placement, which is what predictable traffic, cost tuning or a serverless-only gap calls for. **Data tiering** is one such gap: nodes in the r6gd family move values to local SSD once memory fills and pull them back on access, which suits workloads that regularly touch up to 20 percent of the dataset and can absorb roughly 300 extra microseconds on an SSD hit. Keys always stay in memory, so values should be larger than keys, and r6gd nodes carry close to five times the capacity of r6g for over 60 percent less at full utilization.

Read the table below for the engine and deployment comparison, starting with the last row: the wording in a stem usually selects the answer before any feature does.

| | Valkey on ElastiCache | Redis OSS on ElastiCache | Memcached on ElastiCache | ElastiCache Serverless | Amazon MemoryDB |
|---|---|---|---|---|---|
| Durability | Cache by default; 9.0 adds an optional Multi-AZ transactional log | Cache only | None, a replaced node comes back empty | Cache only | Durable by design, every write committed to a Multi-AZ transactional log |
| Replication | Up to 5 asynchronous read replicas per shard | Same as Valkey | None, nodes are independent | Managed by the service | Up to 5 replicas per shard, fed from the transaction log |
| Clustering | Cluster mode disabled gives 1 shard, enabled gives up to 500 | Same as Valkey | Scale out by adding nodes, client-side hashing with **Auto Discovery** | Cluster mode enabled only, shards added and removed automatically | Up to 500 shards and 500 nodes, over 100 TB |
| Multi-AZ failover | Optional when cluster mode is disabled, on by default when enabled, needs a replica | Same as Valkey | Not available | Always on across three Availability Zones | Always on and required, failover in seconds with no data loss |
| Backup and restore | Yes, to Amazon S3, retained up to 35 days | Same as Valkey | Not on node-based clusters | Yes, including serverless Memcached, no performance impact | Yes, on top of the transaction log, retained up to 35 days |
| Wording that selects it | "sorted sets", "leaderboard", "pub/sub", "vector search", new build | "existing Redis cluster", "migrate without re-ingesting data" | "simplest caching model", "multi-threaded", "cache simple objects" | "unpredictable traffic", "no capacity planning", "LEAST operational overhead" | "durable", "primary database", "one service instead of a cache and a database" |

Pricing follows the deployment model. Serverless bills two dimensions and no node-hours: data stored in gigabyte-hours and requests in **ElastiCache Processing Units (ECPUs)**, where a read or write consumes at least one ECPU per kilobyte transferred, and commands needing more vCPU time consume proportionally more, so a 3.2 KB `GET` costs 3.2 ECPUs. Minimum and maximum usage limits on both dimensions cap spend or pre-scale before a known surge, but a minimum is billed whether or not you use it. Node-based clusters bill per node-hour, discounted by reserved nodes for one or three years that are size-flexible within a node family and unavailable on serverless. Backups beyond one free snapshot, cross-Region data transfer and the 18 percent premium for synchronous durable writes are billed separately.

## Cluster mode, replication groups and endpoints

On Valkey and Redis OSS, the unit ElastiCache actually manages is a **replication group**: one or more shards, each with a single read/write primary node and up to five read-only replicas kept in step by asynchronous replication. The console calls a replication group a cluster; the API and CLI keep the older name, which is why `create-replication-group` is the command that builds what the console shows as a Valkey cluster.

Cluster mode is the choice that shapes everything else. With **cluster mode disabled**, the replication group has exactly one shard, so the whole dataset must fit in one node's memory and every write lands on one primary; you scale reads by adding up to five replicas and capacity by moving to a larger node type. With **cluster mode enabled**, data is partitioned across up to 500 shards, each with its own primary, so writes and memory scale horizontally and online resharding moves slots between shards without downtime. The default quota is 90 nodes per cluster, raised toward 500 on request for Valkey 7.2 or Redis OSS 5.0.6 and later and to 250 below those versions, and resharding also needs free IP addresses in the subnet group.

What changes for the client is the part exam questions hinge on. A cluster mode disabled group exposes a primary endpoint that always resolves to the current primary, a reader endpoint that spreads connections across the replicas in round-robin fashion, and per-node endpoints that do not move and so should not be used for availability. A cluster mode enabled group exposes a single configuration endpoint instead, and the client must be cluster-aware: it learns the slot map, computes which shard owns each key, and follows redirects when slots move. A single-node client library will not work, multi-key commands must stay within one slot, and this is why ElastiCache Serverless, which runs cluster mode enabled only, requires a cluster-capable client. Memcached has no replication and no endpoints of this kind: the client hashes keys across nodes itself, and Auto Discovery lets the client retrieve the full node list from any node so that nodes can be added or removed without redeploying configuration.

Node-based Valkey and Redis OSS clusters can also scale themselves: ElastiCache auto scaling registers shards or replicas as scalable targets and drives them with target-tracking policies on engine CPU or memory usage, or on a schedule for a known daily peak.

## Caching strategies, time to live and eviction

AWS documents two strategies for populating a cache, and a well-written question describes one of them without naming it. **Lazy loading** writes to the cache only on a miss: the application reads the cache, gets a null, queries the database, stores the result and returns it. Only requested data is ever cached, and an empty replacement node degrades gracefully because every miss simply falls through to the database. The costs are a three-trip penalty on every miss and stale data, because nothing updates the cache when the database changes underneath it.

**Write-through** writes to the cache on every database write. Data in the cache is never stale and the read path is fast, but each write costs two trips, a replaced node starts out missing everything until the underlying rows are written again, and the cache fills with values that may never be read. The two are complements, and the documented resolution is to run both and attach a **time to live (TTL)** to every write. A TTL is a number of seconds, or milliseconds on Valkey and Redis OSS, after which the key is treated as absent, so the next read refreshes it from the database. That bounds staleness without hunting down every affected key, and it clears out write-through entries nobody reads. The value is a business decision: short enough to be fresh, long enough to keep the hit rate high.

When memory fills, the `maxmemory-policy` parameter decides what happens. The ElastiCache default is `volatile-lru`, which evicts the least recently used key among those that have a TTL set. The other values evict the least recently or least frequently used key among all keys or among keys with a TTL, evict at random, evict the key closest to expiry, or, with `noeviction`, refuse further writes and return an error. Two traps follow: a cache holding only keys without a TTL under `volatile-lru` has nothing eligible to evict and starts failing writes, and a store meant to be durable needs `noeviction` explicitly, since the default deletes keys with a TTL under memory pressure.

Monitoring follows the same logic. `CacheHitRate` tells you whether the cache is earning its cost, and a rising `Evictions` figure means the working set no longer fits, so the fix is a larger node or more shards. `EngineCPUUtilization` is the metric to watch on nodes with four or more vCPUs, because Valkey and Redis OSS are single-threaded and a host-level `CPUUtilization` of 45 percent on a two-core node already saturates the engine, while multi-threaded Memcached can run near 90 percent. On serverless the two metrics that matter are `BytesUsedForCache` and `ElastiCacheProcessingUnits`, which are also the two dimensions of the bill.

## Security and the network path

An ElastiCache cache or MemoryDB cluster lives inside **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network for AWS resources, placed by a subnet group and reachable only through the security groups attached to it. There is no public endpoint and no IAM-mediated data path in the way DynamoDB has one: network reachability plus engine-level authentication is the whole model, so the first answer to "restrict access to the application tier" is a security group rule, not a policy.

Encryption in transit uses TLS. It is always on for serverless caches and for MemoryDB and optional on node-based ElastiCache clusters, where it is chosen at creation through `--transit-encryption-enabled`. It covers client connections and traffic between nodes, and mutual TLS is not supported. Encryption at rest protects the disk during synchronization, backup and swap operations, the backups written to **Amazon Simple Storage Service (Amazon S3)**, the Regional object storage service, and the transactional log on durable clusters. It is always on for serverless caches and durable clusters, optional elsewhere, settable only when the cache is created, and keyed by either an AWS managed key or a customer managed key in **AWS Key Management Service (AWS KMS)**, the managed cryptographic key service. Adding encryption to an existing node-based cluster therefore means backup, delete and restore, which is why a compliance-driven stem keys on rebuilding rather than modifying.

Client authentication has two mechanisms and the newer one wins. **Redis AUTH** requires a single shared token of 16 to 128 printable characters, is available on node-based clusters only, and requires in-transit encryption. Every client holding the token has full access to the cache, which is exactly its weakness. **Role-based access control (RBAC)** supersedes it on Valkey and on Redis OSS 6.0 and later: you create users, give each an access string naming the commands and key patterns they may touch, and attach them to a user group bound to the cache. That gives per-user passwords, fine-grained authorization and tenant isolation on a shared cache. RBAC is the only authentication method for serverless caches, passwords can rotate automatically through **AWS Secrets Manager**, the managed secret store, and users can authenticate with IAM identities instead, removing the stored credential entirely. The quotas to remember are one user group per replication group, 100 users per group and 2,000 users per Region. MemoryDB uses the same model under the name access control lists. Separately, IAM governs the control plane and **AWS CloudTrail**, the API activity audit service, records those calls.

## Multi-AZ failover, Global Datastore and backups

**Multi-AZ with automatic failover** is how a Valkey or Redis OSS cluster survives the loss of a node or an Availability Zone. It requires at least one replica in a different Availability Zone from the primary in every shard, it is optional on cluster mode disabled clusters and on by default on cluster mode enabled ones, and Memcached cannot do it at all because it has no replication. When the primary fails, ElastiCache promotes a replica and updates the DNS record behind the primary endpoint, so an application connected to that endpoint needs no change, and a healthy replacement node rejoins within about six minutes. Multi-AZ is also the condition for the 99.99 percent availability service level agreement on node-based deployments, and every serverless cache runs Multi-AZ by default. A single-node cluster is not highly available: its failure is total data loss for that shard.

Cross-Region reach is **Global Datastore**, available on node-based Valkey 7.2 and later or Redis OSS 5.0.6 and later, and not on serverless or Memcached. One primary cluster accepts writes and replicates asynchronously to secondary clusters in up to two other Regions, which serve local reads only. Replication lag is typically under one second, so the recovery point objective (RPO) is under a second, and promoting a secondary typically completes in under a minute, giving a recovery time objective (RTO) of about a minute. The promotion is manual: ElastiCache never fails a global datastore over between Regions automatically, which is the fact that most often decides a question. All member clusters must match in node type, engine version and shard count, and a secondary cannot be created from a populated cluster because adding one wipes its data.

Backup and restore write a snapshot of the cache to Amazon S3 in the Redis RDB format. They are supported on Valkey, on Redis OSS and on serverless Memcached, but not on node-based Memcached clusters, which is the classic engine-selection trap. Automatic daily backups can be retained for up to 35 days, manual backups persist until deleted and survive the cache, and a cluster can be deleted with a final backup. A restore always builds a new cache, and because Valkey and Redis OSS share the RDB format a backup moves freely between engines and between serverless and node-based deployments, which is how a Redis OSS cluster migrates to Valkey. On node-based clusters the snapshot costs real resources, so AWS recommends taking it from a replica and leaving `reserved-memory-percent` at its default of 25 percent.

## Amazon MemoryDB and the durable in-memory decision

MemoryDB keeps all data in memory like ElastiCache, but every write is committed to a distributed transaction log spread across multiple Availability Zones before the client is acknowledged. That log is what makes it a database rather than a cache. Primary nodes are strongly consistent, so a read on a primary reflects every acknowledged write and that guarantee survives a failover; replicas are eventually consistent, and sequentially consistent per replica, so a replica read may lag but never reorders. Reads take microseconds and writes single-digit milliseconds, the milliseconds being the price of durability.

Multi-AZ is not an option in MemoryDB, it is the design. Each shard must have more than one node, and failover to a replica takes seconds and loses nothing because the promoted replica catches up from the transaction log rather than from the primary. A single-node shard stops accepting writes until its primary is rebuilt from the log, which is availability lost but not data lost. A cluster holds up to 500 nodes across up to 500 shards with up to five replicas per shard, over 100 TB of data and up to 160 million transactions per second. Point-in-time snapshots to S3 with retention up to 35 days sit on top of the log, and data tiering on r6gd nodes is available here too. **MemoryDB Multi-Region** goes further than Global Datastore: active-active across up to five Regions with local reads and writes, propagation typically under a second, up to 99.999 percent availability, and automatic conflict resolution using conflict-free replicated data types with last-writer-wins semantics.

> **Professional depth.** As of Valkey 9.0, ElastiCache itself can be durable. Enabling durability attaches the same kind of Multi-AZ transactional log, with a choice between synchronous writes, which lose nothing and cost single-digit millisecond write latency, and asynchronous writes, which keep microsecond writes but risk up to 10 seconds of data and reject writes outright once the unpersisted backlog passes 10 seconds. The constraints are heavy: cluster mode enabled only, Multi-AZ with at least one replica per shard, enabled at creation and never disabled afterward, at-rest encryption forced on, no serverless, no Global Datastore, no data tiering, a ceiling of 100 MiBps of writes per primary, and an 18 percent node-hour premium for synchronous mode. AWS now positions ElastiCache with durability for single-Region durable workloads and MemoryDB for multi-Region active-active ones. Neither exam guide has caught up, so answer exam questions with the classic rule and treat this as the architecture answer in real designs.

The decision rule the exams test is short. If losing the in-memory copy means a slow rebuild from a database that still holds the truth, use ElastiCache. If losing it means losing data, use MemoryDB, and accept single-digit millisecond writes and a bill that adds a charge per gigabyte written and snapshot storage on top of node-hours. A stem saying "replace a cache and a database with one service", "durable" or "cannot lose acknowledged writes" points at MemoryDB; one saying "reduce load on the existing database" points at ElastiCache.

## Professional depth

At organization scale the first question is which account owns the cache. ElastiCache has no cross-account data path and Global Datastore forbids cross-account deployments, so a shared cache means a shared VPC or VPC peering plus security group references, not a resource policy. Handing a dataset to another account means copying a backup into an S3 bucket that account can read, which is a copy rather than a shared live store. The same rule shapes key management: at-rest encryption is chosen at creation, so a multi-account standard requiring customer managed KMS keys must be enforced before the cache exists.

The quotas that bite in a migration are worth holding together: 300 nodes per Region, 90 nodes per Valkey or Redis OSS cluster raised toward 500 on request on Valkey 7.2 or Redis OSS 5.0.6 and later, 60 nodes per Memcached cluster, 40 serverless caches per Region, 300 reserved nodes and one user group per replication group. Resharding also consumes subnet IP addresses, and an undersized subnet CIDR range is a common reason a scale-out stalls halfway.

Failure modes cluster around the difference between a cache and a store. A cluster with no replica has no failover target and comes back empty, so the database behind it must absorb a full cold start; sizing for a cache miss storm is the reliability answer. Global Datastore does not fail over by itself, so a multi-Region design needs an automation or runbook that promotes the secondary. A cache in front of an RDS read replica or a DynamoDB global table replica serves data that is stale twice over, once from replication lag and once from the TTL. And because the primary endpoint moves by DNS, a client that caches DNS answers indefinitely keeps writing to a node that is no longer primary, the same trap [Amazon RDS](rds.md) documents for Multi-AZ failover.

Cost at scale turns on three levers rather than the node price. Serverless removes capacity planning but bills every kilobyte transferred as ECPUs, so a chatty workload with small values can cost more than a modest node-based cluster, and the crossover is found by comparing measured ECPUs against node-hours. Reserved nodes discount a steady node-based bill for a one or three year commitment and apply size-flexibly within a family. Data tiering is the third, and it pays only when the regularly accessed portion of the dataset is small.

## Worked scenario

A live events company runs a product catalog and a seat-availability service on Amazon Aurora PostgreSQL. Catalog pages are read thousands of times per second and change a few times a day. Seat holds are written constantly, must never be lost, and currently sit in a self-managed Redis server that the team has twice restarted into an empty state, releasing seats customers had reserved. Traffic multiplies by twenty for two hours when a major event goes on sale, and European users should read the catalog locally.

The catalog goes into an ElastiCache for Valkey cluster with cluster mode enabled, sized so that the working set fits across several shards, with one replica per shard in a second Availability Zone and Multi-AZ with automatic failover on. The application uses lazy loading with a write-through update whenever an editor changes a product, and every write carries a five-minute TTL so that a missed invalidation self-corrects. `maxmemory-policy` stays at the default `volatile-lru`, which is correct here because every key has a TTL. A global datastore replicates the catalog cluster to a European Region for local reads, with a documented runbook for promoting it, since that promotion is never automatic.

Seat holds go into MemoryDB rather than into the same cache, because a lost hold is lost data rather than a slow read. Every write is committed to the Multi-AZ transaction log before acknowledgment, primaries are strongly consistent so a hold is visible to the next read, and a node failure promotes a replica in seconds without losing one. Both stores sit in private subnets reachable only from the application tier, TLS is on, at-rest encryption uses a customer managed KMS key chosen at creation, and clients authenticate as RBAC users whose passwords rotate through Secrets Manager.

The exam asks how to keep seat holds through an unplanned node replacement while still cutting read load on Aurora at the lowest operational cost. The keyed answer is ElastiCache for the catalog and MemoryDB for the holds. Putting both in one ElastiCache cluster is the distractor that meets the latency requirement and breaks the durability one, and adding Aurora read replicas is the distractor that reduces read load without giving either workload microsecond latency.

## Exam lens

- "Reduce read load on the database and cut latency to microseconds" maps to ElastiCache; an RDS read replica is the distractor when the stem says microseconds or repeated reads.
- "The in-memory store is the primary database", "durable", "cannot lose acknowledged writes" maps to MemoryDB; ElastiCache is the distractor on the exams, which predate the durability option, because a cache is a copy.
- "Simplest caching model", "multi-threaded", "cache simple objects and scale out by adding nodes" maps to Memcached; anything naming replication, failover, sorted sets, pub/sub or backup rules it out.
- "Unpredictable traffic with no capacity planning" and "LEAST operational overhead" map to ElastiCache Serverless; it rules out Global Datastore, data tiering and durability, which are node-based only.
- "Dataset larger than one node" or "write throughput beyond one primary" maps to cluster mode enabled with more shards; more replicas is the distractor, because replicas scale reads only.
- "Cache must survive the loss of an Availability Zone" maps to Multi-AZ with automatic failover and at least one replica per shard; a single-node cluster fails this outright.
- "Failover without changing the connection string" maps to the primary endpoint, whose DNS record is repointed; a node endpoint never moves.
- "Low-latency reads in a second Region" maps to Global Datastore with a read-only secondary, up to two secondary Regions, RPO under a second and RTO under a minute.
- "Automatic cross-Region failover for the cache" does not exist: Global Datastore promotion is manual, and only MemoryDB Multi-Region accepts writes in more than one Region.
- "Restore the cache after deletion" maps to a final or manual backup, supported on Valkey, Redis OSS and serverless Memcached but never on node-based Memcached.
- "Only 20 percent of the data is accessed regularly and memory cost is too high" maps to data tiering on r6gd nodes, not to a larger node type.
- "Different applications share one cache and must not read each other's keys" maps to RBAC users and user groups; Redis AUTH is the distractor because one token grants full access.
- "Encrypt an existing unencrypted cluster at rest" maps to backup, delete and recreate, since at-rest encryption is set only at creation.
- "Bound the staleness of cached data without writing invalidation logic" maps to a TTL on every write, combined with lazy loading; a cluster-aware client and single-slot multi-key commands are the price of cluster mode enabled.

## Knowledge check

### 1. Product pages that repeat the same queries (Associate)

A media company serves product pages from an application tier backed by an Amazon RDS for PostgreSQL DB instance. Every page render runs the same three queries, read traffic is roughly 50 times write traffic, and product records change a few times a day. The company wants repeat reads answered in microseconds and the load on the DB instance reduced, and it accepts that a change may take a few minutes to appear on the site.

Which solution will meet these requirements?

- **A)** Create two RDS read replicas and send all page queries to them.
- **B)** Deploy an Amazon ElastiCache cluster and write query results to it only when a product record is updated, with no expiry.
- **C)** Deploy an Amazon ElastiCache cluster, read it first and fall back to the DB instance on a miss, then store the result with a five-minute time to live.
- **D)** Deploy an Amazon ElastiCache cluster and preload every product record into it at application startup, with no expiry.

<details><summary>Answer</summary>

**Answer: C.** This is lazy loading with a time to live: only data that is actually requested is cached, a replaced empty node degrades gracefully because misses fall through to the database, and the TTL bounds staleness to the few minutes the company accepts without any invalidation logic. A keeps reads at disk-backed millisecond latency and adds two instances to the bill rather than removing load from the engine. B is write-through with no TTL, so anything not recently updated is never in the cache at all and the entries that are there never refresh. D fills memory with records nobody requests and, with no expiry, serves values that go permanently stale after the first edit.

*Where this is covered: Caching strategies, time to live and eviction.*

</details>

### 2. A leaderboard that must survive a node failure (Associate)

A gaming company needs a real-time leaderboard that ranks millions of players and publishes rank changes to subscribed game servers. The data structures it needs are sorted sets and publish/subscribe channels. If a node is replaced, the leaderboard must not come back empty, and the company wants the least operational overhead.

Which solution will meet these requirements?

- **A)** Create an ElastiCache for Memcached cluster with nodes spread across three Availability Zones and use Auto Discovery in the client.
- **B)** Create an ElastiCache for Valkey cluster with at least one replica per shard in a second Availability Zone and Multi-AZ with automatic failover enabled.
- **C)** Create an ElastiCache for Memcached serverless cache and enable automatic backups.
- **D)** Create an ElastiCache for Valkey cluster mode disabled cluster with no replicas in a single Availability Zone.

<details><summary>Answer</summary>

**Answer: B.** Sorted sets and publish/subscribe exist only on Valkey and Redis OSS, and Multi-AZ with automatic failover promotes a replica and repoints the primary endpoint so the data survives the loss of the node holding it. A fails on the data structures: Memcached stores simple objects only, and Auto Discovery finds nodes, it does not replicate data. C also fails on data structures, and a backup restores into a new cache rather than keeping the running one populated. D has the right engine but no replica, so a node failure loses everything in that shard and Multi-AZ cannot even be enabled.

*Where this is covered: Engines and deployment options.*

</details>

### 3. A cache that emptied during a node replacement (Associate)

A retailer runs a Valkey cluster mode disabled cluster consisting of a single node in one Availability Zone. During a maintenance node replacement the cache came back empty and the resulting query storm overloaded the database. The company needs the cache to survive the loss of a node or an Availability Zone, and the application must keep using the same connection string.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Add a read replica to the replication group in a second Availability Zone.
- **B)** Enable Multi-AZ with automatic failover on the replication group.
- **C)** Create a global datastore with a secondary cluster in the same AWS Region.
- **D)** Change the application to connect to each node endpoint in turn until one responds.
- **E)** Schedule automatic daily backups and restore the most recent one after a failure.

<details><summary>Answer</summary>

**Answer: A and B.** Multi-AZ with automatic failover requires at least one replica in a different Availability Zone from the primary, so the two steps are halves of the same fix; ElastiCache then promotes the replica and repoints the DNS record behind the primary endpoint, leaving the connection string unchanged. C is invalid as written, because a global datastore secondary cluster must be in a different Region, and cross-Region promotion is manual in any case. D replaces one endpoint with a list of endpoints that do not move during a failover, which is the opposite of what the primary endpoint provides. E rebuilds the cache into a new cluster after the outage rather than preventing the outage, and it changes the endpoint.

*Where this is covered: Multi-AZ failover, Global Datastore and backups.*

</details>

### 4. A dataset that has outgrown one node (Associate)

A retailer's Valkey cluster mode disabled cluster runs on the largest node type available in its family and is at 95 percent memory use. Write latency is rising because every write lands on the single primary node, and the dataset is forecast to triple in the next year. The company needs both memory and write throughput to grow.

Which solution will meet these requirements?

- **A)** Add five read replicas to the existing replication group.
- **B)** Recreate the cluster on r6gd nodes so that data tiering extends capacity onto local SSD.
- **C)** Change `maxmemory-policy` to `allkeys-lru` so that older keys are evicted automatically.
- **D)** Move to a cluster mode enabled replication group with several shards and add shards with online resharding as the data grows.

<details><summary>Answer</summary>

**Answer: D.** Cluster mode enabled partitions data across up to 500 shards, each with its own primary, so memory and write throughput both scale horizontally, and online resharding moves slots between shards without downtime. A adds read capacity only: replicas are read-only and every write still goes to the one primary. B is the tempting half-answer, because data tiering does relieve the memory ceiling, but the cluster still has a single shard and therefore a single primary, so rising write latency is untouched. C keeps the data inside one node by throwing keys away, which turns a capacity problem into a cache miss problem and still leaves one write endpoint.

*Where this is covered: Cluster mode, replication groups and endpoints.*

</details>

### 5. European users reading a US cache (Associate)

A company runs a node-based ElastiCache for Valkey catalog cache in us-east-1, where all writes originate. European users report slow catalog pages because every read crosses the Atlantic. The company also wants a copy of the cache in Europe that it can promote if us-east-1 becomes degraded, and it will accept a recovery point measured in seconds.

Which solution will meet these requirements with the LEAST latency?

- **A)** Create a global datastore with a secondary cluster in eu-west-1 and point European readers at the secondary cluster.
- **B)** Add a read replica in eu-west-1 to the existing replication group and point European readers at the reader endpoint.
- **C)** Create an ElastiCache Serverless cache in eu-west-1 and add it to a global datastore with the us-east-1 cluster.
- **D)** Export a backup of the us-east-1 cluster to Amazon S3 each night and restore it into a new eu-west-1 cluster each morning.

<details><summary>Answer</summary>

**Answer: A.** A global datastore replicates a node-based Valkey cluster to a read-only secondary in another Region with lag typically under one second, which serves local reads and can be promoted to primary in about a minute. B is impossible: an ElastiCache read replica must be in the same Region as its primary, which is precisely why Global Datastore exists. C fails because Global Datastore is not supported on ElastiCache Serverless. D leaves European data up to 24 hours stale and gives a recovery point measured in hours rather than seconds.

*Where this is covered: Multi-AZ failover, Global Datastore and backups.*

</details>

### 6. Retiring a dual-write architecture (Professional)

A payments company holds in-flight authorization state in an ElastiCache for Valkey cluster using sorted sets and hashes, and writes the same state to an Amazon Aurora cluster so that it is durable. Reconciliation jobs regularly find records in one store and not the other after failures, and each mismatch requires manual investigation. The company wants a single store that keeps microsecond read latency, never loses an acknowledged write, and does not require the data access layer to be rewritten.

Which solution will meet these requirements?

- **A)** Move the cache to ElastiCache Serverless and take automatic backups every hour.
- **B)** Move the state to an Amazon MemoryDB cluster with at least one replica in each shard and retire the Aurora copy.
- **C)** Keep the ElastiCache cluster and add a global datastore with a secondary cluster in another Region.
- **D)** Move the state to Amazon DynamoDB and put a DynamoDB Accelerator cluster in front of it.

<details><summary>Answer</summary>

**Answer: B.** MemoryDB commits every write to a Multi-AZ transaction log before acknowledging it, so an acknowledged write survives node and Availability Zone failure, primaries are strongly consistent across failovers, and reads stay in microseconds. It speaks the same Valkey API and data structures, so the dual write and the Aurora copy both disappear with no rewrite. A leaves the cluster a cache: a backup is a point-in-time copy, so writes since the last snapshot are still lost. C replicates the same non-durable data to a second Region and does nothing about losing acknowledged writes. D is durable but abandons sorted sets and hashes for the DynamoDB API, which is exactly the rewrite the company ruled out.

*Where this is covered: Amazon MemoryDB and the durable in-memory decision.*

</details>

### 7. An audit of a shared cache (Professional)

Three application teams share one node-based ElastiCache for Valkey cluster that was created two years ago without encryption at rest, and all three authenticate with the same AUTH token. An audit requires that each team have its own credential restricted to its own key prefix, that credentials rotate automatically, and that stored data be encrypted with a customer managed key in AWS KMS. Downtime of a few minutes during a maintenance window is acceptable.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Modify the existing cluster to enable encryption at rest with a customer managed AWS KMS key.
- **B)** Rotate the shared AUTH token every 30 days with a scheduled automation.
- **C)** Back up the cluster, create a replacement cluster with encryption at rest enabled and a customer managed AWS KMS key, and restore the backup into it.
- **D)** Add the cluster to a global datastore so that replication traffic is encrypted in transit.
- **E)** Create RBAC users with per-team access strings, attach them to a user group bound to the cluster, and rotate their passwords with AWS Secrets Manager.

<details><summary>Answer</summary>

**Answer: C and E.** At-rest encryption can only be set when a cache is created, so the documented path on an existing node-based cluster is backup, recreate with the key, and restore, which the maintenance window allows. RBAC gives each team a separate user whose access string limits the commands and key patterns it may touch, and ElastiCache integrates with Secrets Manager to rotate those user passwords. A is not possible: the modify operation cannot turn on at-rest encryption. B keeps a single shared credential that grants full access to the whole cache, which is the finding the audit raised. D encrypts cross-Region traffic and does nothing for per-team authorization or for data at rest.

*Where this is covered: Security and the network path.*

</details>

### 8. A large dataset with a small hot set (Professional)

A company stores a 500 GB dataset in a node-based ElastiCache for Valkey cluster on memory-only r7g nodes, and the node bill is the largest line in its database spend. Telemetry shows that about 15 percent of keys are read on any given day and the remainder are read rarely. The company can tolerate slightly higher latency the first time a rarely used key is read, wants no application change, and wants to stay in one Region.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Move the workload to ElastiCache Serverless so that capacity tracks demand.
- **B)** Halve the number of nodes and set `maxmemory-policy` to `allkeys-lru`.
- **C)** Recreate the cluster on r6gd nodes so that data tiering moves the least recently used values to local SSD.
- **D)** Create a global datastore and serve the rarely used keys from the secondary cluster.

<details><summary>Answer</summary>

**Answer: C.** Data tiering on the r6gd node family keeps keys in memory and moves least recently used values to local SSD, bringing them back on access with roughly 300 extra microseconds of latency. AWS scopes it at workloads that regularly access up to 20 percent of the dataset, which 15 percent comfortably satisfies, and r6gd nodes carry close to five times the capacity of memory-only nodes for over 60 percent less at full utilization, with no client change. A changes the billing dimensions to stored gigabytes and ECPUs but still keeps all 500 GB in memory, and serverless does not support data tiering. B evicts 250 GB of data, turning cold reads into database queries rather than SSD reads. D pays for a second full cluster in another Region and adds cross-Region latency to exactly the reads the company wants cheaper.

*Where this is covered: Engines and deployment options.*

</details>

## Summary

Start by deciding whether the in-memory copy is expendable. If it is, the answer is ElastiCache, and the remaining decisions follow in order: Valkey for anything new, Memcached only when the requirement is a simple multi-threaded object cache with no replication and no backup, serverless when traffic is unpredictable and operational overhead must be minimal, node-based when you need predictable cost or a feature serverless lacks. Then choose cluster mode disabled for a single shard scaled by replicas, or cluster mode enabled for up to 500 shards, a configuration endpoint and a cluster-aware client. Add at least one replica per shard and Multi-AZ so a failure promotes rather than empties, add a global datastore for read latency in up to two other Regions while remembering that its promotion is manual, and add backups where the engine supports them. Populate the cache with lazy loading plus write-through and put a TTL on every write, watch hit rate and evictions, and keep the network path private with TLS, a KMS key chosen at creation and RBAC users rather than a shared AUTH token. If the copy is not expendable, use MemoryDB, whose Multi-AZ transaction log makes it a database.

## Related units

- [Amazon RDS](rds.md): the relational engine a cache usually sits in front of, and its read replica alternative
- [Amazon Aurora](aurora.md): reader endpoints and Global Database, the replication answer when the workload is relational
- [Amazon DynamoDB](dynamodb.md): DAX, the DynamoDB-specific cache, and the rule for choosing it over ElastiCache
- [Amazon CloudFront](../04-networking/cloudfront.md): edge caching of content and whole responses, the other half of task 2.1
- [Amazon API Gateway](../04-networking/api-gateway.md): response caching at the API tier
- [Amazon SQS](../06-integration/sqs.md): buffering writes, the counterpart to caching reads in SAP-C02 task 2.5
- [Amazon VPC](../04-networking/vpc.md): subnet groups, security groups and the private network path to a cache
- [AWS KMS](../07-security/kms-and-cloudhsm.md): customer managed keys for at-rest encryption chosen at creation

## Sources

- [What is Amazon ElastiCache?](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/WhatIs.html): the three supported engines and the two deployment formats
- [Choosing between deployment options](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/WhatIs.deployment.html): the serverless compared with node-based table, three Availability Zones and the 99.99 percent SLA, cluster mode enabled only on serverless, and which features are node-based only
- [Comparing node-based Valkey, Memcached, and Redis OSS clusters](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/SelectEngine.html): when to choose each engine, the feature matrix including backup, automatic failover and durability, and Memcached being multi-threaded
- [Replication: Valkey and Redis OSS Cluster Mode Disabled vs. Enabled](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Replication.Redis-RedisCluster.html) and [Understanding Valkey and Redis OSS replication](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Replication.Redis.Groups.html): one shard compared with up to 500, five replicas per shard, the 90-node default and the 500-node ceiling
- [Finding replication group endpoints](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Replication.Endpoints.html): primary, reader, node and configuration endpoints and what each one does
- [Automatically identify nodes in your cluster (Memcached)](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/AutoDiscovery.html): Auto Discovery, and that it does not exist for Valkey or Redis OSS
- [Minimizing downtime in ElastiCache by using Multi-AZ](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/AutoFailover.html): the replica requirement, DNS propagation of the promoted replica, and that Multi-AZ is on by default for cluster mode enabled
- [Replication across AWS Regions using global datastores](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Redis-Global-Datastore.html) and [Prerequisites and limitations](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Redis-Global-Datastores-Getting-Started.html): node-based only, up to two secondary Regions, matching cluster configuration, manual promotion, no cross-account and no durability
- [Snapshot and restore](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/backups.html): which engines support backups, the manual backup limits, and taking a backup from a replica
- [Data tiering in ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/data-tiering.html): the r6gd requirement, the 20 percent access pattern, roughly 300 microseconds of extra latency, keys staying in memory, and the supported eviction policies
- [Caching strategies for Memcached](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Strategies.html): lazy loading, write-through, their advantages and disadvantages, and adding a time to live
- [Engine specific parameters](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/ParameterGroups.Engine.html): the permitted `maxmemory-policy` values and the `volatile-lru` default
- [Managing reserved memory for Valkey and Redis OSS](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/redis-memory-management.html): the 25 percent `reserved-memory-percent` default and what it protects
- [Which Metrics Should I Monitor?](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/CacheMetrics.WhichShouldIMonitor.html): the single-threaded CPU threshold arithmetic, `EngineCPUUtilization`, evictions and memory pressure
- [ElastiCache in-transit encryption (TLS)](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/in-transit-encryption.html) and [At-Rest Encryption in ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/at-rest-encryption.html): always on for serverless, no mutual TLS, what at-rest encryption covers, and that it can only be enabled at creation
- [Authenticating with the Valkey and Redis OSS AUTH command](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/auth.html) and [Role-Based Access Control (RBAC)](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Clusters.RBAC.html): token constraints, AUTH being superseded, access strings, user groups and Secrets Manager rotation
- [Quotas for ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/quota-limits.html): nodes per Region and per cluster, serverless caches per Region, and the user and user group limits
- [Scaling ElastiCache Serverless clusters](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Scaling-serverless.html): automatic scale-out, usage limits, pre-scaling and what happens at a storage maximum
- [Durability in ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/durability.html) and [Limitations](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Durability.Limitations.html): synchronous and asynchronous writes, the 10-second buffer, and the cluster mode, Multi-AZ, encryption and feature restrictions
- [Engine versions and upgrading in ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/engine-versions.html) and [ElastiCache Extended Support](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/extended-support.html): the Valkey 9.0 feature list and the Redis OSS end of standard support and automatic upgrade dates
- [Related services](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/related-services-choose-between-memorydb-and-redis.html): AWS's current positioning of ElastiCache with durability against MemoryDB
- [Amazon ElastiCache pricing](https://aws.amazon.com/elasticache/pricing/) and [Amazon ElastiCache FAQs](https://aws.amazon.com/elasticache/faqs/): ECPUs and GB-hours, the Valkey price difference and 100 MB minimum, reserved nodes, the 18 percent synchronous durability premium, Global Datastore RPO and RTO, and backup retention
- [What is MemoryDB](https://docs.aws.amazon.com/memorydb/latest/devguide/what-is-memorydb.html) and [Features of MemoryDB](https://docs.aws.amazon.com/memorydb/latest/devguide/servicename-feature-overview.html): the Multi-AZ transactional log, latency figures, cluster ceilings and snapshot retention
- [Understanding MemoryDB replication](https://docs.aws.amazon.com/memorydb/latest/devguide/replication.html), [Consistency](https://docs.aws.amazon.com/memorydb/latest/devguide/consistency.html) and [Minimizing downtime in MemoryDB with Multi-AZ](https://docs.aws.amazon.com/memorydb/latest/devguide/autofailover.html): strong consistency on primaries, shard and replica limits, and failover from the transaction log
- [MemoryDB Multi-Region](https://docs.aws.amazon.com/memorydb/latest/devguide/multi-region.html) and [Amazon MemoryDB pricing](https://aws.amazon.com/memorydb/pricing/): active-active across up to five Regions, CRDT conflict resolution, and the node-hour, data written and snapshot storage billing dimensions
