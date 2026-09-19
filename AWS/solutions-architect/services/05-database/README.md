# Database

AWS sells a different database for each shape of query, and both exams test
whether you can tell them apart. **Amazon RDS** runs the familiar relational
engines as a managed service. **Amazon Aurora** is a MySQL and PostgreSQL
compatible engine rebuilt on a shared storage layer. **Amazon DynamoDB** is a
key-value and document store with no instances to size. **Amazon ElastiCache**
puts an in-memory layer in front of any of them. Around them sit purpose-built
stores for documents, graphs, wide-column data, time series and columnar
analytics.

The decision the category keeps asking you to make is the access pattern. Not
the data, the access: how the application reads and writes, how often, with what
consistency, and whether the query shape is known in advance. Known keys and
high-volume single-item access point at DynamoDB. Ad hoc joins across normalized
tables point at RDS or Aurora. Repeated reads of one small result point at a
cache. Scans across billions of rows point at a columnar warehouse. Answer that
first and engine, instance class, capacity mode and replica layout follow.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [rds.md](rds.md) | Choose storage and instance sizing, and design Multi-AZ, read replicas, backups and encryption | L |
| [aurora.md](aurora.md) | Use cluster endpoints, replica tiers, Serverless v2 and Global Database, and say when Aurora beats RDS | M |
| [dynamodb.md](dynamodb.md) | Design keys and indexes, choose a capacity mode, and use streams, global tables and in-memory acceleration | L |
| [elasticache-and-memorydb.md](elasticache-and-memorydb.md) | Pick an engine and a caching strategy, and tell a cache from a durable in-memory database | M |
| [documentdb.md](documentdb.md) | Decide between **Amazon DocumentDB**, MongoDB-compatible storage, and DynamoDB | S |
| [neptune.md](neptune.md) | Recognize the relationship queries that justify a graph database | S |
| [keyspaces-qldb-and-timestream.md](keyspaces-qldb-and-timestream.md) | Place wide-column and time series workloads on the right service | XS group |
| [redshift.md](redshift.md) | Choose a warehouse over a query engine or RDS, and design distribution and sort keys | S |

## Which exam tasks this serves

On SAA-C03 it is tasks 3.3 and 4.3 outright, plus 2.1 for read replicas and
caching, 2.2 for failover and RDS Proxy, and 1.3 for encryption at rest and
backup policy. On SAP-C02 it is tasks 2.5 and 4.4 for purpose-built selection,
4.3 for the database platform in a migration, and 2.4 and 3.4 for replication
and failover.

## Reading order

Read `rds.md`, then `aurora.md`, then `dynamodb.md`. Those three carry most of
the question weight on both exams, and the relational pair comes first because
Aurora is defined against RDS. Then `elasticache-and-memorydb.md`, then
`redshift.md`. An Associate-only candidate can skim `documentdb.md`,
`neptune.md` and `keyspaces-qldb-and-timestream.md` down to their selection
rules: SAA-C03 tests recognizing when a purpose-built store is the answer, not
running one. Note that **Amazon Timestream**, the time series database, is in
scope for SAP-C02 only, and **Amazon QLDB**, the ledger database, appears on
neither in-scope list.
