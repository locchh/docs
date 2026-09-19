# Analytics

This category moves data from where it is produced into storage, then
makes it queryable. **Amazon Kinesis Data Streams** and **Amazon MSK** carry
records while they are still in motion. **Amazon Data Firehose**, formerly
Kinesis Data Firehose, delivers those records into storage without code. **AWS
Glue** catalogs and transforms what lands. **Amazon Athena** queries it in place
with SQL, **Amazon EMR** runs open-source big data frameworks over it, and
**Amazon OpenSearch Service** indexes it for search and log analysis. **AWS Lake
Formation** decides who is allowed to see which rows and columns.

The decision the category keeps asking you to make is whether the data is in
motion or at rest, and then who runs the query. In motion with multiple
independent consumers and replay means a stream. In motion with a single
destination and no code means Firehose. At rest and queried occasionally with
SQL means Athena over partitioned columnar files. At rest and queried constantly
by many analysts means a warehouse, covered in the
[database category](../05-database/README.md). At rest and needing custom Spark
or Hive means EMR. Converting .csv to .parquet, which the exam names directly,
is Glue.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [kinesis.md](kinesis.md) | Size shards, choose consumers, and tell streams, Firehose and Flink apart | M |
| [msk.md](msk.md) | Decide when managed Kafka beats Kinesis, and secure a cluster | S |
| [glue.md](glue.md) | Crawl a catalog, run ETL jobs, and convert and partition formats | M |
| [athena.md](athena.md) | Cut scan cost with partitioning and columnar formats, and control spend with workgroups | S |
| [lake-formation.md](lake-formation.md) | Grant row, column and cell-level access across accounts | S |
| [emr.md](emr.md) | Compose a cluster, use Spot for task nodes, and choose EMR over Glue or Athena | S |
| [opensearch.md](opensearch.md) | Choose managed domains or Serverless, and size storage tiers | S |
| [data-exchange-and-quick.md](data-exchange-and-quick.md) | Subscribe to third-party data and build dashboards with row-level security | XS group |

## Which exam tasks this serves

This category is weighted toward the Associate exam. On SAA-C03 it is task 3.5
outright, which names Athena, Lake Formation, **Amazon Quick**, formerly Amazon
QuickSight, Glue, Kinesis and EMR in one task statement, down to converting .csv
to .parquet and securing ingestion access points. On SAP-C02 the coverage is
genuinely thinner: task 2.5 for selecting a purpose-built service, and task 4.3,
which names Amazon OpenSearch Service directly in its database list.

## Reading order

Read `kinesis.md` first, since streaming vocabulary carries into everything
else, then `glue.md` and `athena.md` together, because the catalog Glue builds
is what Athena queries. Then `lake-formation.md`, `emr.md` and `opensearch.md`.
An Associate-only candidate can skim `msk.md` and `data-exchange-and-quick.md`
down to their selection rules, but should skip nothing else here: everything in
this category is on the SAA-C03 in-scope list except **Amazon Managed Service
for Apache Flink**, the stream processing service inside `kinesis.md`, which is
SAP-C02 only.
