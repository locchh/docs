# Amazon DynamoDB

**Where it sits on the exams.** **Amazon DynamoDB** is the fully managed key-value and document database that stores items in tables with no servers, instances or storage volumes to size, and returns single-digit millisecond responses whether the table holds a thousand items or a trillion. It is a core choice in SAA-C03 tasks 2.1, 2.2, 3.3 and 4.3, and in SAP-C02 tasks 2.5, 4.3 and 4.4. The rule of thumb the exam wants is that DynamoDB fits a workload whose access patterns are known in advance and reach items by key at high volume, and that once you have chosen it, the key schema, the secondary indexes and the capacity mode follow from those same access patterns.

## Tables, items, keys, and the request API

A table is a collection of items, and an item is a collection of attributes. Only the primary key is declared when the table is created. Every other attribute is defined per item, so two items in the same table can carry entirely different attributes, and documents can nest up to 32 levels deep. An item is limited to 400 KB, counting attribute names and values together. When a value does not fit, compress it into a binary attribute, split the record into several items under one partition key, which AWS calls vertical partitioning, or store the payload in **Amazon Simple Storage Service (Amazon S3)**, the Regional object storage service, and keep only the object identifier in the item, accepting that no transaction spans the two services.

DynamoDB supports two kinds of primary key. A simple primary key is one partition key attribute, and no two items may share a partition key value. A composite primary key is a partition key plus a sort key, and then many items may share a partition key value as long as their sort key values differ. Key attributes must be scalar, and only String, Number and Binary are allowed; non-key attributes have no such restriction. DynamoDB hashes the partition key value, and the hash decides which physical partition stores the item. Items sharing a partition key value are stored together and sorted by sort key value, which is what makes a range query on one partition cheap. That group is called an item collection, and it is the unit that several later limits act on.

The request API is deliberately narrow. `GetItem` reads one item and requires the complete primary key, not part of it. `Query` reads items that share one partition key value, optionally narrowed by a condition on the sort key, and returns them in sort key order, ascending by default or descending with `ScanIndexForward` set to false. `Scan` reads every item in the table or index. `PutItem`, `UpdateItem` and `DeleteItem` each address one item by full primary key, and `UpdateItem` is an upsert. `BatchGetItem` reads up to 100 items and 16 MB across one or more tables, and `BatchWriteItem` writes or deletes up to 25 items and 16 MB, with no update action. A batch runs its requests in parallel but is not atomic: some can fail and return as unprocessed keys while the rest succeed.

```bash
aws dynamodb query --table-name Orders \
  --key-condition-expression "CustomerId = :c AND OrderDate BETWEEN :a AND :b" \
  --expression-attribute-values '{":c":{"S":"C-4471"},":a":{"S":"2026-01"},":b":{"S":"2026-06"}}' \
  --return-consumed-capacity TOTAL
```

Two behaviors of `Query` and `Scan` decide exam questions. First, one call returns at most 1 MB of data and then hands back a `LastEvaluatedKey` for the next page, so a large read is always a paginated loop. Second, a filter expression runs after the items have been read and before they are returned, so filtering trims the response but not the cost or the time; only a key condition on the index actually reduces work. A projection expression is the same story: asking for three attributes out of thirty does not shrink the item size used to bill the read. The design conclusion is that a `Scan` with a filter is almost never the keyed answer on an exam, and the correction is a better key schema or a secondary index.

Conditional writes cover the concurrency cases. A condition expression on `PutItem`, `UpdateItem` or `DeleteItem` lets the write proceed only when the current item matches, which gives optimistic locking and prevents overwriting an existing key. A failed condition still consumes write capacity based on the existing item size and raises `ConditionalCheckFailedException`. An arithmetic update expression gives an atomic counter that never blocks but is not idempotent on retry. **PartiQL**, the SQL-compatible query language DynamoDB exposes, offers `SELECT`, `INSERT`, `UPDATE` and `DELETE` over the same engine. It adds no joins and changes no costs: a PartiQL `SELECT` without a key condition is still a scan, priced as one.

## Choosing DynamoDB from the access pattern

The selection question on both exams is almost never "relational or not" in the abstract. AWS frames the distinction as a tradeoff in where the work happens: in a relational database, data can be queried flexibly, but queries are relatively expensive and do not scale well under high traffic, while in DynamoDB data can be queried efficiently in a limited number of ways, outside of which queries become expensive and slow. In a relational design you normalize first and worry about queries later. In a DynamoDB design you must know the questions before you design the schema, then shape the data so that the most important queries are single key lookups.

Three properties settle the choice. Data size decides whether one partition can hold a query's answer, data shape decides whether the answer can be stored pre-joined rather than assembled at read time, and data velocity decides whether the request rate exceeds what a single writer node can serve. Known entity lookups, a very high request rate, unbounded growth and a tolerance for denormalized copies point at DynamoDB. Ad hoc joins, reporting queries invented after the fact, multi-row referential integrity and a moderate request rate point at [**Amazon RDS**](rds.md) or [**Amazon Aurora**](aurora.md), the managed relational engines, where a query planner earns its cost. Running the engine yourself on **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service, is correct only when a specific engine or version is a hard requirement.

Single-table design follows from that. AWS recommends maintaining as few tables as possible, because keeping related data together reduces round trips, permissions management and backup overhead. The pattern is to name the key attributes generically, `PK` and `SK`, and store several entity types in one table with prefixed values such as `CUSTOMER#4471` with `PROFILE`, `ORDER#2026-06-11` and `ADDRESS#home` as sort keys. One `Query` then returns the customer and their recent orders in a single request, the read a relational design would satisfy with a join, and access patterns that do not follow the main key get a secondary index rather than a second table. The documented exceptions are high-volume time series data and datasets with genuinely different access patterns.

The Professional exam extends this into a selection methodology across the purpose-built database family, and the method is to name the access pattern first and the product second. Key or document lookups at scale go to DynamoDB. Relational queries and transactions go to RDS or Aurora. A repeated read of a small hot result belongs in a cache, which is [**Amazon ElastiCache**](elasticache-and-memorydb.md), the managed in-memory cache, with **Amazon MemoryDB** as the durable in-memory database when the cache is also the system of record. MongoDB API compatibility points at [**Amazon DocumentDB**](documentdb.md), the MongoDB-compatible document database. Relationship traversal such as fraud rings points at [**Amazon Neptune**](neptune.md), the managed graph database. Wide-column Cassandra workloads point at [**Amazon Keyspaces**](keyspaces-qldb-and-timestream.md), the managed Apache Cassandra-compatible database, and measurements over time at [**Amazon Timestream**](keyspaces-qldb-and-timestream.md), the managed time series database, whose LiveAnalytics edition closed to new customers in June 2025, leaving Timestream for InfluxDB as the path AWS now offers. Full-text and log search points at [**Amazon OpenSearch Service**](../09-analytics/opensearch.md), the managed search and log analytics service. Aggregation over billions of rows points at [**Amazon Redshift**](redshift.md), the columnar data warehouse. A requirement for a serverless relational engine points at Aurora Serverless v2, not at DynamoDB. DynamoDB is a poor fit for every one of those last patterns, and a Professional question that pairs "analytics across the whole dataset" with DynamoDB is usually asking you to export or stream the data somewhere else rather than to scan the table.

Cost shape is part of the selection. RDS and Aurora bill for instance hours whether or not requests arrive, so a spiky or low-duty workload pays for idle. DynamoDB in on-demand mode bills per request and per GB-month, and a table receiving no traffic incurs no throughput charge. That makes DynamoDB the usual answer to "MOST cost-effective" for unpredictable or intermittent traffic with simple key access, and a relational engine the better answer when the query mix is genuinely relational, because emulating joins in application code moves cost into engineering time rather than removing it.

## Consistency, capacity units, and transactions

Every read in DynamoDB is eventually consistent unless the caller asks for otherwise. An eventually consistent read might not reflect a write that has just completed, and repeating the read a moment later returns the newer item. Setting `ConsistentRead` to true on `GetItem`, `Query` or `Scan` gives a strongly consistent read that reflects every prior successful write. The restriction that decides questions is where strong consistency is available: on tables and on **local secondary indexes (LSIs)** only. Reads from a **global secondary index (GSI)** and from a stream are always eventually consistent, and there is no parameter that changes that. If a scenario says a value must be read back immediately after it is written, the answer either reads the base table with `ConsistentRead` enabled or avoids putting that read on a global secondary index.

Capacity is metered in units, and the arithmetic is worth memorizing because SAA-C03 asks for it directly. One read unit is one strongly consistent read of an item up to 4 KB, or two eventually consistent reads of it, so an eventually consistent read costs half a unit. One write unit is one write of an item up to 1 KB. Sizes round up, so a 3.5 KB item reads like a 4 KB item and a 500-byte item costs a full write unit. Transactional operations cost double, because DynamoDB prepares and then commits each item. Worked through: 80 strongly consistent reads per second of 3 KB items need 80 read units, 40 if eventually consistent and 160 if transactional; 100 writes per second of 512-byte items need 100 write units, or 200 transactionally.

Query and scan costs follow the same rounding but aggregate differently. A `Query` sums the sizes of all items it returns and rounds the total up to the next 4 KB, which is why fetching 1,500 items of 64 bytes costs far less than fetching them one at a time. A `Scan` is charged on the items it evaluates, not the items it returns after filtering. A read of an item that does not exist still consumes capacity, and a count costs the same as the values, because the engine still reads the items. `UpdateItem` is charged on the larger of the item before and after the change even when one small attribute moves.

**DynamoDB transactions** provide all-or-nothing writes across items. `TransactWriteItems` groups up to 100 actions targeting up to 100 distinct items in one or more tables within the same AWS account and Region, with an aggregate item size of no more than 4 MB. The actions are `Put`, `Update`, `Delete` and `ConditionCheck`, the last of which asserts something about an item the transaction does not modify. `TransactGetItems` is the read side, grouping up to 100 `Get` actions under the same size limit and returning an atomic snapshot. Transactions are serializable with respect to single-item operations and other transactions, and a conflict on any item cancels the whole request with `TransactionCanceledException`. A client request token makes a write transaction idempotent for 10 minutes, which matters when a network timeout leaves the caller unsure whether the transaction committed.

Three transaction facts are exam material. Enabling transactions costs nothing, but the doubled capacity is consumed even when a transaction is canceled by a failed condition check, so contention is expensive. Transactions cannot be performed using indexes, and their changes reach indexes, streams and backups gradually, so a stream consumer must not assume that one transaction's records arrive together. Atomicity holds only inside the Region where the write was issued, so another replica of a global table can observe a partial transaction. The usual distractor is `BatchWriteItem`, which groups writes without atomicity; AWS recommends it rather than transactions for bulk ingestion.

## Capacity modes, partitions, and warm throughput

A table runs in one of two throughput modes, and the mode decides both the scaling behavior and the bill. On-demand mode is the default and the option AWS recommends for most workloads: no capacity is specified, requests are billed individually, and a table with no traffic incurs no throughput charge. Provisioned mode requires a stated number of read and write capacity units per second and bills for the hourly capacity provisioned rather than the capacity consumed, which buys cost predictability and a ceiling on request rate. Read this table before choosing a mode in an exam scenario, because the deciding clause is usually either "unpredictable traffic" or "steady and forecastable".

| Dimension | On-demand mode | Provisioned mode |
|---|---|---|
| What you configure | Nothing, optionally a maximum read or write rate | Read and write capacity units, or auto scaling bounds |
| Billing basis | Read and write request units actually consumed | Capacity units provisioned per hour, used or not |
| Scaling | Instant up to double the previous peak, then allocated as traffic grows | Manual `UpdateTable`, or auto scaling toward a target utilization |
| New table instant capacity | 4,000 writes and 12,000 reads per second | Whatever you provision, within quota |
| Cost control lever | Maximum throughput setting per table or index | The provisioned number itself, plus auto scaling bounds |
| Reserved capacity | Not eligible | Eligible on the default table class only |
| Default table quota | 40,000 read and 40,000 write request units per second | 40,000 read and 40,000 write capacity units per second |
| Best fit | New, spiky, intermittent or unknown traffic | Steady, well-understood traffic with a forecastable floor |

On-demand scaling has a documented shape rather than a promise of infinite elasticity. A new on-demand table sustains up to 4,000 writes and 12,000 reads per second immediately. The table then instantly accommodates up to double its previous peak: a workload whose peak has reached 50,000 strongly consistent reads per second can jump to 100,000 with no throttling, and once it sustains that, the next ceiling becomes 200,000. Beyond double the previous peak DynamoDB allocates more capacity as traffic rises, but throttling can occur if you exceed double the previous peak within 30 minutes, so AWS advises spreading a larger increase over at least half an hour or pre-warming the table first. The default per-table quota of 40,000 read and 40,000 write request units still applies and is adjustable; there is no account-level throughput quota for on-demand tables. An optional maximum read or write throughput setting per table or per index caps consumption to protect against a runaway client or an unexpected bill.

Provisioned mode pairs with **DynamoDB auto scaling**, a target tracking policy in **AWS Application Auto Scaling**, the service that applies scaling policies to resources such as DynamoDB tables, driven by alarms in **Amazon CloudWatch**, the metrics, logs and alarm service. You set a minimum, a maximum and a target utilization, and AWS recommends 70 percent. Scaling triggers after consumed capacity breaches the target for two consecutive minutes, and the alarm adds a delay of up to a few minutes, so auto scaling absorbs a ramp but not an instant spike. Capacity can be raised as often as needed; decreases are limited to four per day per table or index, with one more each hour, up to 27 in a day. **DynamoDB reserved capacity** commits to a quantity of provisioned capacity for a one-year term, or a three-year term in selected Regions, at a discounted rate. It is capped at 1,000,000 active capacity units and is available only for provisioned tables on the default table class, not for on-demand tables, infrequent access tables or replicated writes. A table can switch from provisioned to on-demand only four times in a rolling 24 hours, though the reverse move is unrestricted.

Underneath both modes sit partitions, and their limits explain most throttling. Every partition is designed to deliver at most 3,000 read units and 1,000 write units per second. Item size interacts with that ceiling: on a table of 20 KB items one strongly consistent read costs five read units, so a partition sustains about 600 such reads per second. Uneven traffic therefore throttles long before the table's total capacity is exhausted, which is what a hot partition means. **Adaptive capacity** is the automatic mitigation, enabled for every table in both capacity modes at no cost. It instantly raises throughput for partitions receiving more traffic and rebalances data so that frequently accessed items do not share a partition, and it can isolate one consistently hot item on its own partition, served up to the partition maximum but not beyond. It will not split an item collection when the table has a local secondary index. Burst capacity separately retains up to five minutes of unused capacity for short spikes, some of which DynamoDB may use for background work.

The durable fix is key design rather than capacity. A good partition key has high cardinality and spreads requests evenly; a status flag or a current date makes a poor one. Where a low-cardinality key is unavoidable, write sharding appends a calculated suffix such as `2026-09-12#7` so one logical day spreads across many partitions, and the reader queries every shard and merges. **Warm throughput** reports the read and write rate a table or index can instantly support. It is available by default for all tables and global secondary indexes and rises automatically with usage, and before a launch that will multiply traffic tenfold you can pre-warm the table to raise that baseline without changing capacity mode or provisioned settings. Pre-warm requests are billable, warm throughput can never be decreased once raised, and for a global table it applies to every replica.

## Local and global secondary indexes

A secondary index lets an application query the same data by an alternate key. DynamoDB maintains indexes itself; applications never write to one directly. A global secondary index has its own partition key and optional sort key, which may be any top-level String, Number or Binary attributes and need not resemble the table's key at all. A local secondary index keeps the table's partition key and substitutes a different sort key, so it reorders an item collection rather than reorganizing the table. The default quotas are 20 global secondary indexes and 5 local secondary indexes per table, and across all of a table's indexes you may name at most 100 attributes in `INCLUDE` projections. A GSI key can also be composed from several attributes, up to four in the partition key and four in the sort key, removing the old habit of concatenating synthetic keys by hand.

The differences below are what exam questions turn on, and the first row is usually decisive on its own.

| Property | Local secondary index | Global secondary index |
|---|---|---|
| When it can be created | Only when the table is created, and deleted only with the table | Added to or removed from an existing table at any time |
| Partition key | Same as the base table | Any attribute, independent of the table |
| Read consistency | Eventually or strongly consistent | Eventually consistent only |
| Throughput | Shares the base table's capacity | Its own capacity in provisioned mode, inherits the table's capacity mode |
| Non-projected attributes | Fetched from the base table automatically, at extra read cost | Not available, the query cannot reach back to the table |
| Key uniqueness | Sort key values need not be unique | Key values need not be unique |
| Size constraint | Item collection for one partition key value limited to 10 GB | No item collection size limit |
| Typical use | An extra sort order on the same partition, with strong consistency | A new access pattern on an existing table, at any scale |

The 10 GB rule is the most commonly missed limit in the service. In a table that has at least one local secondary index, all the items sharing a partition key value, in the table and in every LSI, form an item collection stored on a single partition, and that collection may not exceed 10 GB. Exceed it and writes that grow the collection fail with `ItemCollectionSizeLimitExceededException`, while reads and shrinking writes still work. Tables with no local secondary index have no such limit. AWS recommends requesting `ReturnItemCollectionMetrics` on writes and alarming well below the ceiling, for example at 8 GB, and choosing a global secondary index instead whenever an item collection could grow without bound.

Throughput coupling is the second trap. A query against a global secondary index consumes read units from the index, and a write to the base table consumes write units from both the table and every affected index. If a global secondary index has less write capacity than the base table needs, writes to the base table are throttled, not just the index update. AWS therefore advises provisioning at least as much write capacity on a global secondary index as on the table. Index writes are conditional on the data: defining an indexed attribute costs one index write, changing an indexed key value costs two because the old entry is deleted and a new one written, and changing an attribute that is neither an index key nor projected costs nothing on the index. Storage is billed for the index too, at the size of the projected attributes plus the keys plus 100 bytes of overhead per index item.

Projection choice is a cost decision with a latency consequence. `KEYS_ONLY` gives the smallest index and cheapest writes, `INCLUDE` adds named attributes, and `ALL` duplicates the item. A local secondary index query that needs an unprojected attribute makes DynamoDB fetch the whole item from the base table, charging for the full item; a global secondary index cannot fetch at all, so an omitted attribute is simply unavailable. Sparse indexes exploit the propagation rule deliberately: an item lacking the index key is never written to the index, so setting a `PendingReview` attribute only on items needing review produces an index that is exactly the work queue, far cheaper to read than a table scan.

## Streams, change data capture, and time to live

**DynamoDB Streams** turns a table into an event source. When enabled, it captures a time-ordered sequence of item-level modifications and keeps them in a log for 24 hours, with no performance impact on the table because the capture is asynchronous. The stream view type decides what each record carries: keys only, the new image, the old image, or both images. It is fixed for the life of the stream, so changing it means disabling the stream and creating a new one. Two guarantees matter: each stream record appears exactly once, and for any single item the records appear in the order the modifications happened. Ordering is per item, not across a partition or table. Shards map one to one onto table partitions, so the stream scales with the table, and no more than two processes should read one shard at once.

The common consumer is **AWS Lambda**, the serverless function service, attached through an event source mapping. Lambda reads each open shard in sequence-number order with one function instance, follows shard lineage automatically, and can run up to ten concurrent instances per shard with `ParallelizationFactor` while preserving per-item order. That is the standard answer to "react to every change without polling the table": maintain an aggregate, push a notification, write an audit record or fan a change out. A write that changes nothing produces no stream record.

The alternative is **Kinesis Data Streams for DynamoDB**, which sends the same item-level changes to a stream in **Amazon Kinesis Data Streams**, the managed streaming data service, in the same account and Region. One table can feed exactly one Kinesis data stream. It is the answer whenever the DynamoDB Streams model runs out: Kinesis retains data far longer than 24 hours, enhanced fan-out lets two or more consumers read the same data independently, and the stream connects directly to **Amazon Data Firehose**, formerly Kinesis Data Firehose, for delivery to S3 or a data warehouse, and to **Amazon Managed Service for Apache Flink**, formerly Kinesis Data Analytics, for stream processing. The tradeoff is the delivery model: records may arrive out of order and the same change may appear more than once, so consumers deduplicate and order on the `ApproximateCreationDateTime` attribute. Changes are billed in change data capture units of one kilobyte, plus ordinary Kinesis charges. A scenario saying "exactly once and in order for each item, with a simple trigger" is DynamoDB Streams; one saying "retain for seven days, feed three teams, land in a data lake" is Kinesis Data Streams for DynamoDB.

**Time to live (TTL)** is the built-in expiry mechanism, and it is a cost control as much as a data-lifecycle feature. You nominate one attribute that holds a Unix epoch expiration timestamp in seconds as a Number, and DynamoDB deletes expired items automatically, typically within a few days of expiration and without consuming write throughput. Items whose TTL attribute is not a Number are ignored. Three behaviors surprise people. Expired items remain readable until the background process removes them, so queries and scans must use a filter expression on the TTL attribute if the application must never see expired data. An item can be rescued by updating its TTL attribute to a future value before the deletion happens. And TTL deletions appear in DynamoDB Streams marked as service deletions rather than user deletes, which is exactly what makes the archive pattern work: let TTL expire the hot copy, catch the deletion in the stream, and have a Lambda function write the item to S3 for long-term retention. TTL also removes the item from every local and global secondary index, and in a global table using multi-Region eventual consistency the deletion is replicated to the other replicas, where it does consume replicated write capacity even though the original deletion was free.

## Read acceleration with DAX

**Amazon DynamoDB Accelerator (DAX)** is a write-through, in-memory cache that fronts DynamoDB and cuts eventually consistent read response times from single-digit milliseconds to microseconds. It is API compatible with DynamoDB, so an application adopts it by pointing the DAX client at a cluster endpoint instead of writing cache logic. A cluster runs inside **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network for AWS resources, controlled by security groups. One node is the primary and the others are read replicas; AWS recommends at least three nodes across Availability Zones, and replication among them is eventually consistent, usually within a second. DAX supports encryption at rest and TLS in transit.

DAX keeps two independent caches. The item cache stores `GetItem` and `BatchGetItem` results by primary key with a time to live of five minutes by default, plus a least recently used eviction policy that is always on. The query cache stores whole `Query` and `Scan` result sets keyed by their parameters. They do not interact: a write updates the item cache but never invalidates a cached result set, so a query repeated after an update returns the old result set until its own TTL expires. Writes go through DAX to DynamoDB first and are cached only after DynamoDB confirms them, which means a throttled or failed write never pollutes the cache. A bulk load is usually better sent around DAX directly to the table, because writing megabytes through the cache evicts the items that reads actually want.

The consistency caveats are what exams test. DAX serves eventually consistent data. A request with `ConsistentRead` set to true, and every `TransactGetItems` call, is passed straight through to DynamoDB and the result is not cached, so DAX never accelerates a strongly consistent read. Any write that reaches the table without going through DAX leaves the cache stale until the TTL expires, and that includes replicated writes arriving at a global table replica. DAX also caches misses: a read for an item that does not exist stores an empty entry and returns it until the TTL expires or the item is written through DAX. AWS lists the poor fits explicitly: applications that need strongly consistent reads, applications that are write intensive, and applications without many repeated reads, since DAX performs best above a 90 percent cache hit rate.

Choosing between DAX and a general purpose cache is a recurring question. DAX is specific to DynamoDB, needs no cache-aside code, and is billed per node-hour regardless of hit rate, which makes it the answer when a read-heavy DynamoDB workload needs microsecond reads or when a hot key is exhausting a partition's read capacity. [Amazon ElastiCache](elasticache-and-memorydb.md) caches anything, including query results assembled from several sources or from a relational database, but the application must implement lazy loading, write-through and invalidation itself. If the scenario says "reduce DynamoDB read costs and latency with minimal application change", the answer is DAX; if it says "cache a computed result or a relational query", the answer is ElastiCache.

## Global tables and multi-Region designs

**DynamoDB global tables** replicate a table across AWS Regions. A global table is two or more replica tables in different Regions, one replica per Region, sharing a table name, key schema and item data, and a write to any replica is propagated to the others. Replicas are readable and writable, which is what "multi-active" means and what separates global tables from a relational read replica. Each replica offers the same durability as a single-Region table, and AWS publishes a 99.999 percent availability service level agreement for global tables against 99.99 percent for a single-Region table. Version 2019.11.21 is the current version and the one to use; the 2017.11.29 version is legacy. The consistency mode is chosen when the global table is created and cannot be changed afterward, and every replica in one global table shares it.

Multi-Region eventual consistency (MREC) is the default. Changes replicate asynchronously, typically within a second, and when one item is modified in two Regions at once DynamoDB keeps the write with the latest internal timestamp, a last writer wins rule applied per item. The subtlety that decides questions is that a strongly consistent read on an MREC replica returns the latest version only if the item was last written in that Region; otherwise it can still be stale, and conditional writes evaluate the local copy. MREC replicates by reading a stream on each replica, so streams cannot be turned off there. Replicas can be added or removed at any time, and the recovery point objective (RPO) equals the replication delay.

Multi-Region strong consistency (MRSC) is the newer mode and it is far more constrained. Writes are replicated synchronously to at least one other Region before the write returns, a strongly consistent read on any replica always returns the latest item, and the recovery point objective is zero. An MRSC global table must be deployed in exactly three Regions, either as three replicas or as two replicas plus a witness. A witness stores the replicated data and supports the availability architecture but cannot serve reads or writes, and it is owned and managed by DynamoDB rather than appearing in your account. MRSC is offered only within a US, EU or AP Region set and cannot span sets. It must be configured at creation from a table that contains no data, replicas cannot be added later, and time to live, local secondary indexes and transactions are all unsupported on MRSC tables. A write that collides with an in-flight write to the same item in another Region fails with `ReplicatedWriteConflictException` and can be retried. The exam trade is plain: MRSC buys global read correctness and an RPO of zero at the cost of higher write latency and unsupported features, while MREC buys lower latency and flexibility at the cost of a nonzero RPO and last writer wins conflicts.

The cost shape of a global table is a common oversight. Every replicated write is billed again in each receiving Region, as a replicated write capacity unit or replicated write request unit, on top of storage in every Region and cross-Region data transfer, so a three-Region table multiplies write cost roughly by the number of replicas. Settings behave in a specific way too: capacity mode, table write capacity, index definitions, encryption type, time to live and warm throughput are synchronized across replicas, read capacity and table class can be overridden per replica, and continuous backups, deletion protection, tags and the Kinesis streaming destination are never synchronized, so each replica needs its own backup configuration. Replicated writes bypass DAX, so a cache in front of a replica stays stale until its TTL expires.

## Security, backup, and data movement

All user data in DynamoDB is encrypted at rest and that cannot be turned off. The choice is which key in **AWS Key Management Service (AWS KMS)**, the managed cryptographic key service, protects the table: an AWS owned key, the default and free; an AWS managed key in your account; or a customer managed key you create, control and can audit or disable. You can switch between the three at any time, and encryption covers the table, its indexes, streams, global tables, backups and DAX clusters. A question asking for auditable, revocable key control points at a customer managed key; one asking only for encryption at rest is already satisfied by the default.

Authorization is pure **AWS Identity and Access Management (IAM)**, the service that controls identities and permissions: DynamoDB has no database users or passwords, and every request is signed and evaluated against identity policies, table resource-based policies and any VPC endpoint policy. Fine-grained access control narrows permission below the table. The `dynamodb:LeadingKeys` condition key restricts a principal to items whose partition key value matches an identity variable, which is how one shared table serves many tenants safely, and `dynamodb:Attributes` with `dynamodb:Select` and `dynamodb:ReturnValues` restricts which attributes a request may read or write. Note that `Scan` is deliberately left out of such policies, because a scan returns items regardless of the leading key.

```json
{"Effect": "Allow",
 "Action": ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:UpdateItem"],
 "Resource": "arn:aws:dynamodb:us-west-2:111122223333:table/GameScores",
 "Condition": {"ForAllValues:StringEquals": {
   "dynamodb:LeadingKeys": ["${www.amazon.com:user_id}"]}}}
```

For the network path, DynamoDB supports both endpoint types. A gateway endpoint is a route table entry, is not billed, and serves resources inside the VPC only. An interface endpoint using **AWS PrivateLink**, the feature that exposes services on private IP addresses in your subnets, is billed, accepts traffic from on-premises networks and from peered or transit-attached VPCs in other Regions, and supports 50,000 requests per second per endpoint. Both accept an endpoint policy limiting access to named tables, and AWS documents keeping the gateway endpoint for in-VPC callers while adding an interface endpoint only for on-premises ones.

Backups come in two forms. **Point-in-time recovery (PITR)** keeps continuous backups with a recovery period you choose between 1 and 35 days, and restores to any second between the earliest restorable time and the latest restorable time, which is typically five minutes before now. On-demand backups are full backups taken with a single call, retained until deleted, with zero impact on table performance, and they suit long-term or compliance retention. Every restore creates a new table, so cutover is an application change rather than an in-place rollback. Deleting a table with PITR enabled leaves a free system backup for 35 days, and **AWS Backup**, the centralized backup service, can run DynamoDB backups on a schedule and a policy.

Data movement uses S3 in both directions and neither direction consumes table capacity. Export to S3 requires PITR to be enabled, runs asynchronously, consumes no read units, has no effect on table performance, and writes DynamoDB JSON or Amazon Ion to a bucket that may belong to another account or Region. A full export captures any point inside the PITR window; incremental exports cover a window of between 15 minutes and 24 hours. The exported data is then queried with **Amazon Athena**, the serverless SQL query service for S3, which is how you run analytics on DynamoDB data without scanning the live table. Import from S3 reads CSV, DynamoDB JSON or Amazon Ion, optionally GZIP or ZSTD compressed, consumes no write capacity, and is priced on the uncompressed source size. It always creates a new table, can build global secondary indexes but not local ones, and is the cheapest bulk load, because the equivalent `BatchWriteItem` job is billed as writes.

## Monitoring, table classes, and pricing shape

CloudWatch receives consumed and provisioned capacity, latency, throttling and error metrics per table and per index, and alarms on those are the routine operational control. Two DynamoDB-specific signals matter more on the exam. `ReplicationLatency` is published for each source and destination pair of an MREC global table and is the metric to alarm on when a multi-Region recovery point objective is at stake; MRSC tables do not publish it. CloudWatch Contributor Insights for DynamoDB identifies the most accessed and most throttled partition keys in a table or index, which is the direct way to find the hot key behind a throttling incident. It is enabled per table or index, does not show DAX cache hits, and publishes key values to CloudWatch, so it is unsuitable when the key itself is sensitive. **AWS CloudTrail**, the API activity audit service, records control plane actions and, where enabled, item-level data events.

Every table has a table class. **DynamoDB Standard** is the default and the right choice for most workloads. **DynamoDB Standard-Infrequent Access (Standard-IA)** lowers storage cost and raises read and write cost, with identical performance, durability and availability, and AWS gives a clean rule for switching: when storage exceeds 50 percent of the throughput cost of a Standard table, Standard-IA reduces the total. Application code does not change, because the API and endpoints are the same. All of a table's secondary indexes inherit its class, and no more than two table class updates are allowed in a 30-day trailing period. Typical candidates are logs, order history and other data that must stay online but is rarely read.

The rest of the bill follows the same pattern of paying for what the table actually does. In on-demand mode you pay per read request unit and write request unit; in provisioned mode you pay per hour for the capacity configured, discounted by reserved capacity when the table uses the Standard table class and you commit to a term. Storage is billed per GB-month for the table and for every index, so a wide `ALL` projection on three global secondary indexes can cost more than the table. Reading a DynamoDB stream is billed in read request units, with an important exception: records read through a Lambda trigger are not charged, which is why the Lambda pattern is usually the cost-effective one. Kinesis Data Streams for DynamoDB is billed in change data capture units of one kilobyte of change, plus the Kinesis stream itself. Global tables add a replicated write request unit in every receiving Region plus cross-Region data transfer. PITR is priced on table size and the chosen recovery period does not change it, on-demand backups and restores are priced by size, exports and imports are priced per GB, and DAX is priced per node-hour whether or not the cache is hit. The cost-optimization answer for a DynamoDB scenario is therefore usually one of five moves: switch a spiky table to on-demand, buy reserved capacity for a steady one, remove or narrow an index, move cold data out with TTL or the Standard-IA class, or stop a scan that should have been a query.

## Professional depth

At organization scale the first decision is whether a dataset gets its own table or its own account. A shared multi-tenant table with fine-grained access control keeps operations and cost low, but every tenant then shares one table's quotas, backup schedule and blast radius. A table per tenant inverts that, and the initial quota of 2,500 tables per Region, extendable to 10,000, becomes the ceiling; beyond it AWS recommends spreading tenants across accounts. Cross-account access comes from a resource-based policy on the table or an assumed role in the owning account, and **AWS Organizations**, the multi-account governance service, can stop member accounts from weakening encryption or creating replicas in unapproved Regions. One trap: fine-grained access control must not be applied to the service-linked roles that perform global table replication, or replication breaks.

Migration questions rarely reduce to schema translation. Moving a relational workload to DynamoDB means enumerating access patterns, folding joined entities into item collections and designing keys and indexes for them, which is why the safe answer to "migrate this normalized schema without redesign" is usually that the workload belongs on [Amazon RDS](rds.md) or Aurora instead. When the redesign is genuine, bulk load into a new table with import from S3, which consumes no write capacity and is priced on source bytes, then capture changes from the source during cutover.

The quotas that bite at scale are worth listing together: 40,000 read and write units per table by default in both capacity modes, 80,000 per account for provisioned tables, four capacity decreases per day plus one per hour, two table class updates per 30 days, 10 GB per item collection on any table carrying a local secondary index, 3,000 read and 1,000 write units per partition, two concurrent readers per stream shard, 100 projected attributes across all of a table's indexes, and 10 TB of replica backfill per Region per day when adding a global table replica. Most are adjustable, but adjustment takes a support case, so raise them and pre-warm the table before the traffic arrives rather than after the first throttling incident.

Failure modes cross feature boundaries. An under-provisioned global secondary index throttles writes to the base table, not merely queries on the index. A DAX cluster in front of a global table replica serves stale items because replicated writes never touch the cache. Point-in-time recovery is not synchronized across replicas, so a global table can have backups in one Region and none in another. And a table keyed on a date or a status value throttles at a fraction of its configured capacity in either capacity mode, because adaptive capacity can raise a partition only to the partition maximum.

> **Professional depth.** Recovery objectives decide the multi-Region design. A requirement for a recovery point objective of zero with strongly consistent reads in every Region can only be met by an MRSC global table, which costs three fixed Regions, no transactions, no time to live and no local secondary indexes. A requirement for low write latency with a few seconds of acceptable data loss is MREC with last writer wins. A requirement for recovery from logical corruption rather than Regional failure is PITR or an on-demand backup, because replication faithfully copies bad data to every replica.

## Worked scenario

A ticketing company sells seats for events worldwide. The catalog and the seat inventory live in one DynamoDB table with a generic key schema: the partition key holds `EVENT#<id>` and the sort key holds `META`, `SEAT#<row>#<number>` or `HOLD#<id>`, so one query returns an event and its seat map. A global secondary index keyed on customer ID and order timestamp serves the "my orders" screen, which the base key schema cannot answer. The table runs in on-demand mode because traffic is flat until an on-sale, and the team pre-warms it before each major on-sale so that the first minute does not exceed double the previous peak.

Seat holds expire after ten minutes of inactivity. The application writes an absolute expiry timestamp and lets time to live delete the hold items, and because TTL deletions arrive in DynamoDB Streams as service deletions, a Lambda function releases the seat and writes an audit record. Checkout itself is a `TransactWriteItems` call that marks the seats sold, decrements the remaining inventory item and writes the order, all with condition expressions, so a double sale is impossible. The seat map for the single hottest event is served through DAX, which absorbs the repeated reads that would otherwise exhaust one partition's 3,000 read units.

Customers are in three Regions, so the table is a global table using multi-Region eventual consistency, a per-Region write cost accepted in exchange for local read latency. Because last writer wins would be unacceptable for inventory, the application routes every write for an event to its home Region and reads from the other replicas. Point-in-time recovery is enabled on each replica separately, and a nightly incremental export to S3 feeds Athena for revenue reporting so that analysts never scan the live table.

The exam asks how to add a revenue-by-city report without affecting checkout latency, and the keyed answer is the export to S3 queried with Athena rather than a scan, a new global secondary index or a read replica.

## Exam lens

- "Key-value access at any scale with single-digit millisecond latency" maps to DynamoDB; a relational engine is the distractor when the scenario has no joins.
- "Unpredictable or spiky traffic, MOST cost-effective" maps to on-demand capacity mode; provisioned with auto scaling is the distractor because scaling lags a spike by minutes.
- "Read the item immediately after writing it" maps to a strongly consistent read on the table; a global secondary index cannot serve one.
- "Query by an attribute that is not the table key, on an existing table" maps to a global secondary index; a local secondary index is the distractor because it can only be created with the table.
- "Throttling on one table while total capacity is unused" maps to a hot partition; fix the key design or shard writes, because more capacity will not help past 3,000 read and 1,000 write units per partition.
- "All-or-nothing update of several items" maps to `TransactWriteItems` at double the write cost; `BatchWriteItem` is the distractor because it is not atomic.
- "Microsecond reads for a read-heavy DynamoDB workload with no code rewrite" maps to DAX; ElastiCache is the distractor when the cached data is not DynamoDB items.
- "React to every item change exactly once and in order per item" maps to DynamoDB Streams with a Lambda trigger.
- "Retain change records beyond 24 hours or feed several independent consumers" maps to Kinesis Data Streams for DynamoDB, accepting possible duplicates and reordering.
- "Delete expired records without paying for the deletes" maps to time to live; a scheduled `DeleteItem` job is the distractor because it consumes write capacity.
- "Active-active reads and writes in several Regions with the LEAST operational overhead" maps to global tables; multi-Region strong consistency only when the requirement is an RPO of zero with strongly consistent cross-Region reads.
- "Run SQL analytics over table data without affecting production" maps to export to S3 and query with Athena, not a scan.
- "Storage dominates the bill for rarely read data" maps to the DynamoDB Standard-Infrequent Access table class.
- "Restrict each mobile user to their own items in a shared table" maps to fine-grained access control with the `dynamodb:LeadingKeys` condition key.
- "Private access to DynamoDB from on-premises servers" maps to a PrivateLink interface endpoint; a gateway endpoint is the distractor because it serves only resources inside the VPC.

- "Query the table with SQL-like syntax" maps to PartiQL, which is a query language over the same API and the same capacity, not a second engine and not a way to avoid designing keys.
- "Read-intensive" points at eventually consistent reads, a global secondary index, DAX or a read-scaled design; "write-intensive" points at capacity mode, partition spread and write sharding. Name the axis before choosing the feature, because the same table can be both on different access patterns.

## Knowledge check

### 1. Storing player profiles for a mobile game (Associate)

A studio is launching a mobile game that stores one profile document per player. The application always reads and writes a profile by player ID, the document shape differs between players, the player count could grow from thousands to tens of millions, and the team has no database administrators.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Run Amazon RDS for MySQL in a Multi-AZ deployment with a normalized player schema.
- **B)** Store each profile as an item in an Amazon DynamoDB table with the player ID as the partition key.
- **C)** Load the profiles into an Amazon Redshift cluster and query them by player ID.
- **D)** Run a self-managed Apache Cassandra cluster on Amazon EC2 instances and shard it manually.

<details><summary>Answer</summary>

**Answer: B.** The access pattern is a single key lookup of a schemaless document with unbounded growth, which is exactly what DynamoDB is built for, and there is nothing to size or patch. A adds a relational engine, a fixed instance size and a schema the workload does not need. C is a columnar warehouse designed for aggregation over many rows, not single-item lookups. D delivers similar data-model behavior but pushes cluster sizing, patching, repair and scaling back onto a team with no database administrators.

*Where this is covered: Choosing DynamoDB from the access pattern.*

</details>

### 2. Capacity for scheduled flash sales (Associate)

A retailer runs flash sales twice a month. Between sales the table receives almost no traffic; during a sale, request rates rise to roughly 40 times the normal level within a minute. The company wants to avoid throttling during sales without paying for idle capacity between them.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Use on-demand capacity mode and pre-warm the table before each sale.
- **B)** Use provisioned capacity mode with auto scaling and a 70 percent target utilization.
- **C)** Use provisioned capacity mode fixed at the peak capacity observed in the last sale.
- **D)** Use provisioned capacity mode at the baseline level and rely on burst capacity during sales.

<details><summary>Answer</summary>

**Answer: A.** On-demand charges only for requests, so the quiet periods cost nothing, and pre-warming raises the instantly available throughput above double the previous peak before the sale begins. B scales only after consumed capacity breaches the target for two consecutive minutes plus alarm delay, which a one-minute ramp outruns. C removes throttling but pays peak capacity around the clock, which the cost requirement rules out. D fails because burst capacity retains only about five minutes of unused capacity and cannot cover a 40-fold increase.

*Where this is covered: Capacity modes, partitions, and warm throughput.*

</details>

### 3. A new query on an existing table (Associate)

An order table with billions of items uses the order ID as its partition key. A new fulfillment screen must list orders by warehouse and by order date. The table cannot be recreated, and the query must stay efficient as the table grows.

Which solution will meet these requirements?

- **A)** Create a local secondary index with the warehouse as the partition key and the date as the sort key.
- **B)** Run a `Scan` with a filter expression on warehouse and date each time the screen loads.
- **C)** Create a global secondary index with the warehouse as the partition key and the order date as the sort key.
- **D)** Create a second table of warehouse orders and keep it in step from application code.

<details><summary>Answer</summary>

**Answer: C.** A global secondary index can be added to an existing table, can use a partition key unrelated to the table's key, and is maintained by DynamoDB. A is impossible twice over: a local secondary index must be created with the table and must keep the table's partition key. B reads every item and is charged on items evaluated, so it gets slower and more expensive as the table grows. D reproduces what a global secondary index already does while adding dual-write consistency bugs.

*Where this is covered: Local and global secondary indexes.*

</details>

### 4. Throttling on a table that has spare capacity (Associate)

A telemetry table uses the current date as its partition key and the device ID as its sort key. Requests are throttled during the day even though consumed capacity stays far below the table's configured capacity. The company wants the throttling to stop.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Raise the table's provisioned capacity to four times the current setting.
- **B)** Add a calculated suffix to the partition key so that each day's writes spread across many values.
- **C)** Put a DAX cluster in front of the table to absorb the write traffic.
- **D)** Create a new table whose partition key is the device ID with the date in the sort key, then migrate the items into it.
- **E)** Change the table class to DynamoDB Standard-Infrequent Access.

<details><summary>Answer</summary>

**Answer: B and D.** All traffic lands on one partition key value, and a partition serves at most 3,000 read and 1,000 write units per second, so both fixes spread the traffic across partition key values. A cannot help, because adaptive capacity already raises the hot partition only to the partition maximum. C is a read cache and does nothing for writes. E changes only the price of storage and throughput, not the distribution of requests.

*Where this is covered: Capacity modes, partitions, and warm throughput.*

</details>

### 5. Reading a value immediately after writing it (Associate)

An application writes an inventory item and then immediately reads it through a global secondary index whose partition key is the stock keeping unit. The read sometimes returns the previous value. The company needs the read to reflect the write every time.

Which solution will meet these requirements?

- **A)** Add a DAX cluster and read the item through DAX.
- **B)** Repeat the index query with `ConsistentRead` set to true.
- **C)** Replace the global secondary index with a local secondary index on the same attributes.
- **D)** Read the item from the base table by its primary key with `ConsistentRead` set to true.

<details><summary>Answer</summary>

**Answer: D.** Strongly consistent reads are supported on tables and local secondary indexes only, so reading the base table by key is the one option that always reflects the write. A makes the problem worse, since DAX serves eventually consistent cached items and passes strongly consistent reads through uncached. B is invalid, because a global secondary index rejects the parameter and is always eventually consistent. C cannot be done on an existing table, and a local secondary index must keep the table's partition key, which the stock keeping unit is not.

*Where this is covered: Consistency, capacity units, and transactions.*

</details>

### 6. Expiring sessions and keeping an archive (Associate)

A session table must keep each session for 30 days and then remove it from the table, but every removed session must be archived to Amazon S3 for compliance. The team wants to avoid paying for the deletions and to avoid running a scheduled cleanup job.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable time to live on the table and store an expiration timestamp in Unix epoch seconds on each session item.
- **B)** Schedule a nightly job that scans the table and issues `DeleteItem` for sessions older than 30 days.
- **C)** Enable DynamoDB Streams and use an AWS Lambda function to write the expired item to Amazon S3 when the deletion record appears.
- **D)** Enable point-in-time recovery and restore the table to Amazon S3 every night.
- **E)** Enable DynamoDB Standard-Infrequent Access so that expired sessions cost less to keep.

<details><summary>Answer</summary>

**Answer: A and C.** Time to live deletes expired items automatically and consumes no write throughput, and the deletion appears in the stream as a service deletion, which gives the Lambda function the full item to archive. B consumes read capacity for the scan and write capacity for every delete, and it is the scheduled job the team wants to avoid. D is a recovery feature that restores into a new table, not an archival export of individual expired items. E lowers storage price but never removes anything.

*Where this is covered: Streams, change data capture, and time to live.*

</details>

### 7. Microsecond reads for a hot catalog (Associate)

A product catalog in DynamoDB is read constantly and updated rarely. During promotions a handful of products are read far more than the rest, and read costs are rising. The company needs microsecond response times for these repeated reads, can tolerate eventually consistent data, and wants to change as little application code as possible.

Which solution will meet these requirements with the LEAST latency?

- **A)** Deploy an Amazon ElastiCache cluster and implement lazy loading and invalidation in the application.
- **B)** Increase the table's provisioned read capacity and enable auto scaling.
- **C)** Create a DynamoDB Accelerator cluster and point the application's DAX client at it.
- **D)** Convert the table to a global table and read from the nearest replica.

<details><summary>Answer</summary>

**Answer: C.** DAX is API compatible with DynamoDB, serves eventually consistent reads in microseconds, and absorbs repeated reads of hot items without cache-aside code. A can also cache, but it requires the application to implement loading, invalidation and serialization itself. B reduces throttling but leaves reads at single-digit milliseconds and raises cost rather than lowering it. D reduces network distance for remote users but not the service response time, and it adds replicated write charges.

*Where this is covered: Read acceleration with DAX.*

</details>

### 8. A ledger that must be correct in every Region (Professional)

A payments company runs active stacks in three United States Regions and is building its ledger table now; the table exists in one Region and contains no data yet. Balance items must be readable at their latest value from any of the three Regions, and a Regional failure must not lose a committed write. The team has confirmed that the workload uses no local secondary indexes, no transactions and no time to live.

Which solution will meet these requirements?

- **A)** Create a global table with multi-Region eventual consistency and issue strongly consistent reads in each Region.
- **B)** Create a global table configured for multi-Region strong consistency across the three Regions in one Region set.
- **C)** Keep a single-Region table and, on failure, restore the latest point-in-time recovery backup into another Region.
- **D)** Keep a single-Region table and place a DAX cluster in each of the other two Regions.

<details><summary>Answer</summary>

**Answer: B.** Multi-Region strong consistency replicates each write synchronously before it returns, gives a recovery point objective of zero, and returns the latest item from strongly consistent reads on any replica; the workload has already given up the features it does not support. A fails because a strongly consistent read on an eventually consistent replica returns stale data when the item was last written elsewhere, and its recovery point objective is the replication delay. C loses writes made since the restore point and takes a restore to a new table. D caches eventually consistent copies and adds no durability in another Region.

*Where this is covered: Global tables and multi-Region designs.*

</details>

### 9. Tenant isolation and analytics on one table (Professional)

A software company keeps all tenants in one DynamoDB table, partitioned by tenant ID. Each tenant's application credentials must be unable to read another tenant's items. Separately, the analytics team needs SQL access to the entire dataset for monthly reporting, with no effect on production latency. The company wants to keep the single-table design.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Attach an IAM policy that uses the `dynamodb:LeadingKeys` condition key to restrict each tenant role to items whose partition key matches its tenant ID.
- **B)** Create one table for each tenant and grant each role access to its own table.
- **C)** Run a monthly parallel `Scan` of the table into Amazon S3 and query the output with Amazon Athena.
- **D)** Enable point-in-time recovery, export the table to Amazon S3, and have the analytics team query the export with Amazon Athena.
- **E)** Grant the analytics team read access to the production table and let them run `Scan` operations directly.

<details><summary>Answer</summary>

**Answer: A and D.** Fine-grained access control with `dynamodb:LeadingKeys` enforces per-tenant isolation inside the shared table, and an export to S3 consumes no read capacity and does not touch table performance, leaving Athena to do the SQL. B abandons the single-table design the company wants to keep. C and E both consume read capacity from the production table, which breaks the requirement that reporting must not affect production latency, and E additionally gives analysts access to every tenant's live data.

*Where this is covered: Security, backup, and data movement.*

</details>

### 10. Cutting the cost of a cold audit table (Professional)

A platform team owns an audit table of 6 TB that grows steadily and is read a few thousand times a day at a predictable rate. Storage is more than 80 percent of the table's monthly cost. Records must remain queryable by key for seven years, and the access pattern is not expected to change.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Switch the table to on-demand capacity mode and enable warm throughput.
- **B)** Keep the DynamoDB Standard table class and buy reserved capacity for the provisioned throughput.
- **C)** Enable time to live with a seven-year expiration and export the table to Amazon S3 every night.
- **D)** Change the table class to DynamoDB Standard-Infrequent Access.

<details><summary>Answer</summary>

**Answer: D.** Standard-IA lowers storage cost with identical performance, durability and availability, and it is the documented choice when storage exceeds 50 percent of a table's throughput cost, which it does here at more than 80 percent. A raises the per-request price for a predictable workload and does nothing about storage. B discounts the smaller part of the bill, and reserved capacity is in any case unavailable once the table moves to Standard-IA, so it is the wrong lever for a storage-dominated table. C deletes nothing for seven years and adds export cost while the records must still be queryable by key.

*Where this is covered: Monitoring, table classes, and pricing shape.*

</details>

## Summary

DynamoDB is chosen from the access pattern, not from the data. Decide first whether the application reaches items by known keys at high volume and can live without joins; if it cannot, the answer is a relational or purpose-built engine instead. Then design the partition key for even distribution, use a sort key to group an item collection, and add a global secondary index for every query the table key cannot answer, remembering that a local secondary index must be planned at table creation and caps its item collection at 10 GB. Pick on-demand for spiky or unknown traffic and provisioned with auto scaling and reserved capacity for steady traffic, and pre-warm before a known surge. Choose eventual consistency unless a read must reflect the write, and pay double for transactions only where partial application would be wrong. Add DAX for repeated reads, streams or Kinesis for change capture, time to live for expiry, global tables for multi-Region reach, and PITR plus export to S3 for recovery and analytics. Cost follows the same decisions: requests, storage, indexes, replicas and caches.

## Related units

- [Amazon RDS](rds.md): the relational alternative when queries are ad hoc and joins matter
- [Amazon Aurora](aurora.md): relational scale-out, Serverless v2 and Global Database compared with DynamoDB global tables
- [Amazon ElastiCache and Amazon MemoryDB](elasticache-and-memorydb.md): general purpose caching when DAX is not the right cache
- [Amazon DocumentDB](documentdb.md): the choice when MongoDB API compatibility is a requirement
- [AWS Lambda](../02-compute/lambda.md): stream triggers, event source mappings and serverless data access
- [Amazon Kinesis](../09-analytics/kinesis.md): the streaming service behind Kinesis Data Streams for DynamoDB
- [Amazon Athena](../09-analytics/athena.md): SQL over table exports in Amazon S3
- [Amazon S3](../01-storage/s3.md): the destination for exports, archives and large attribute payloads

## Sources

- [Core components of Amazon DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html): tables, items, key types, nesting depth and index definitions
- [Working with items and attributes in DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html): batch limits, conditional writes and the 400 KB item size
- [Best practices for storing large items and attributes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-use-s3-too.html): compression, vertical partitioning and the S3 pointer pattern
- [NoSQL design for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-general-nosql-design.html): relational compared with NoSQL design and the single-table recommendation
- [Quotas in Amazon DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html): throughput quotas, index counts, tables per Region, reserved capacity and export limits
- [DynamoDB on-demand capacity mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/on-demand-capacity-mode.html): instant capacity, double the previous peak, the 30-minute rule and maximum throughput settings
- [DynamoDB provisioned capacity mode](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/provisioned-capacity-mode.html): capacity units, auto scaling targets and mode switching
- [DynamoDB reserved capacity](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/reserved-capacity.html): term lengths, the Standard table class restriction and the purchase cap
- [Understanding DynamoDB warm throughput](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/warm-throughput.html): default warm throughput, pre-warming and its one-way nature
- [DynamoDB burst and adaptive capacity](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/burst-adaptive-capacity.html): five minutes of burst, adaptive capacity and per-partition limits
- [DynamoDB read and write operations](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/read-write-operations.html): capacity unit arithmetic for reads, writes and transactions
- [DynamoDB read consistency](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html): eventual and strong consistency and where each is available
- [Best practices for designing and using partition keys](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html): per-partition throughput and item size interaction
- [Amazon DynamoDB Transactions: how it works](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html): 100 actions, 4 MB, isolation, idempotency and doubled capacity
- [Local secondary indexes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/LSI.html): creation timing, shared throughput, fetches and the 10 GB item collection limit
- [Using global secondary indexes in DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html): separate throughput, eventual consistency, projections and multi-attribute keys
- [Change data capture for DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html): 24-hour retention, view types, ordering and Lambda consumption
- [Using Kinesis Data Streams to capture changes to DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/kds.html): retention, duplicates, ordering and change data capture units
- [Using time to live (TTL) in DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/howitworks-ttl.html): timestamp format, deletion timing, free deletes and stream behavior
- [In-memory acceleration with DynamoDB Accelerator (DAX)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.html): use cases, poor fits and encryption support
- [DAX: how it works](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.concepts.html): item and query caches and the five-minute default TTL
- [DAX and DynamoDB consistency models](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.consistency.html): write-through behavior, pass-through strong reads and staleness
- [How DynamoDB global tables work](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html): MREC and MRSC, witnesses, Region sets, restrictions and settings synchronization
- [Enable point-in-time recovery in DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery_Howitworks.html): 1 to 35 day recovery period, restore window and system backups
- [Using on-demand DynamoDB backup and restore](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/backuprestore_HowItWorks.html): full backups with no impact on table performance
- [DynamoDB data export to Amazon S3: how it works](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataExport.HowItWorks.html): PITR requirement, formats, incremental windows and analytics tools
- [DynamoDB data import from Amazon S3: how it works](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/S3DataImport.HowItWorks.html): new-table-only import, formats and pricing basis
- [Considerations when choosing a table class](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithTables.tableclasses.html): the 50 percent storage rule and two updates per 30 days
- [DynamoDB encryption at rest](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/EncryptionAtRest.html): always-on encryption and the three KMS key types
- [Using IAM policy conditions for fine-grained access control](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/specifying-conditions.html): `dynamodb:LeadingKeys` and attribute conditions
- [AWS PrivateLink for DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/privatelink-interface-endpoints.html): gateway compared with interface endpoints and endpoint policies
- [CloudWatch contributor insights for DynamoDB: how it works](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/contributorinsights_HowItWorks.html): most accessed and most throttled keys
- [Amazon DynamoDB on-demand pricing](https://aws.amazon.com/dynamodb/pricing/on-demand/): request units, storage, streams, replicated writes and change data capture units
