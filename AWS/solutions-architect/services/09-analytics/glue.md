# AWS Glue

**Where it sits on the exams.** **AWS Glue**, the serverless data integration service, discovers data, records its structure and runs extract, transform, and load (ETL) processing without requiring you to operate a cluster. It directly owns SAA-C03 task 3.5's transformation and format-conversion decisions, and supports SAP-C02 tasks 3.2 and 4.4 when an architecture optimizes or modernizes data processing. The rule of thumb is to separate metadata discovery from transformation: a crawler describes files; a job changes their contents or format.

## Catalog data before choosing a processing engine

A data lake needs both stored records and a description of how to interpret them. **Amazon Simple Storage Service (Amazon S3)**, the object storage service, holds files. The **AWS Glue Data Catalog**, the shared metadata repository, holds database and table definitions describing locations, columns, formats and partitions. Creating a catalog table over a directory of comma-separated values (CSV) files does not copy those files into Glue or convert them into a database. The table is a description that another engine can use to read the existing data.

An **AWS Glue crawler**, the discovery process that inspects supported data stores, can populate or update these definitions. Its classifiers identify formats and infer schemas. The crawler uses a role to access the source, examines the data and records discovered tables and partitions. It is appropriate when new datasets arrive with structures that need discovery. When an application already supplies a reliable schema and partition layout, explicitly creating or updating catalog metadata can avoid unnecessary discovery work. A crawler is useful automation, not a required component of every Glue architecture.

**Amazon Athena**, the serverless query service, can use catalog definitions to query S3 data with SQL. **Amazon EMR**, the managed platform for big data frameworks, can also use the catalog. Glue jobs read catalog definitions to locate and interpret their inputs. These consumers share metadata while performing different work: Athena answers queries, EMR runs chosen frameworks, and Glue runs integration jobs. Giving all three a catalog table does not give them identical execution behavior or permission to read every underlying object.

Treat crawler configuration as part of the data contract. Set source paths and exclusions deliberately so unrelated datasets do not become one confusing table. Consider whether a schema change should update an existing definition or merely be logged for review. A producer accidentally changing a numeric field to text should not silently redefine every downstream report. Keep raw and curated datasets in separate locations and catalog tables, so discovering a new raw structure does not overwrite the schema that consumers rely on.

Discovery also has an execution order. A job that reads a newly arrived partition through a catalog table needs the partition metadata to be available, unless its design reads locations directly or uses another supported discovery mechanism. Completing an upload does not prove that the catalog is current. Conversely, a successful crawler does not prove the records are correct or that a transformation ran. When troubleshooting a missing daily report, inspect the source objects, metadata and job execution separately rather than rerunning the crawler as a universal repair.

## Choose Spark, Python shell or a visual preparation tool

A Glue job combines a script, runtime version, execution role, inputs, outputs and capacity settings. Apache Spark jobs distribute processing across workers and suit joins, aggregations and large transformations. A Python shell job runs a Python script without the distributed Spark engine and suits smaller utility tasks or lightweight processing that fits its execution environment. A Python script is not automatically a Spark job merely because Glue runs it. Choose from the workload's data volume, libraries and parallelism requirements, then select compatible runtime and worker settings.

**AWS Glue Studio**, the graphical job-authoring interface, lets an engineer connect sources, transforms and targets visually, inspect generated scripts, and run and monitor Glue jobs. It is an authoring experience over the execution service. A graphical diagram still produces a job whose role, network access, runtime dependencies and output behavior need engineering. Use visual authoring when the transformations fit its supported nodes; use scripts when the application needs logic that is clearer or more controllable in code. Both paths require representative test data and an explicit publication contract.

**AWS Glue DataBrew**, the visual data preparation tool, serves users who want to explore and clean datasets without writing code. A project lets an analyst preview data and build a recipe of preparation steps. A recipe job applies the saved transformations to a dataset and writes prepared output to S3. Profiling helps reveal missing values and unusual distributions before selecting transformations. Previewing a sample is different from processing all records: a recipe that looks correct in the workspace still needs to be tested against the full data's edge cases.

Read this comparison by the work required, rather than by which interface looks easiest.

| Requirement | Starting choice | Important boundary |
|---|---|---|
| Infer schema and discover new tables | Crawler and Data Catalog | Discovery does not transform records |
| Join and transform large datasets | Glue Spark ETL job | Distributed processing still needs suitable partitioning |
| Run a small standalone Python utility | Python shell job | No Spark distribution or job-bookmark support |
| Visually author a managed integration job | Glue Studio | The generated job still needs testing and permissions |
| Let analysts clean data with reusable recipes | DataBrew | A preview is not proof of full-dataset quality |

Runtime selection is a compatibility decision. Pin the Glue version and test libraries, connectors and scripts together before upgrading. A newer engine can improve behavior, but changing the runtime while changing business rules makes failures harder to isolate. Keep script versions and job parameters associated with each release. Test representative schema variations, empty inputs and malformed records, not only a clean sample that exercises the happy path.

**AWS Glue for Ray**, the managed execution option for distributed Ray applications, closed to new customers on April 30, 2026. Existing customers can continue using it, with AWS focusing on security and availability rather than new features. AWS recommends Ray on **Amazon Elastic Kubernetes Service (Amazon EKS)**, the managed Kubernetes service, as an alternative. This restriction applies to Glue for Ray, not to Glue Spark or Python shell jobs. Do not infer a termination date for existing Ray jobs from a documentation page titled end of support.

## Convert CSV to Parquet and design the partition layout

CSV is convenient for interchange but stores records as text rows. Parsing types, reading unwanted columns and scanning unrelated dates can make repeated analytics inefficient. Apache Parquet is a columnar format that stores typed columns and supports compression and selective column reads. A Glue transformation can parse the CSV schema, normalize fields, select useful columns and write Parquet output to a curated S3 location. Changing a catalog table's format field or renaming a file extension does not change the bytes and is not a conversion solution.

Define the schema before optimizing it. A customer identifier containing leading zeros should not become an integer simply because a sampled file appears numeric. Decide how to handle headers, quoted delimiters, null values, timestamps and malformed rows. Normalize a business date consistently before using it as a partition column. For financial records, preserve the required decimal precision instead of casually converting every value to a floating-point number. These are application decisions: Glue supplies processing tools but cannot determine the company's intended meaning from a filename.

Partitioning divides the output by selected column values, such as `event_date=2026-09-19/region=apac/`. A query or job that filters on these columns can skip unrelated partitions. Choose keys that match common filters and produce useful amounts of data in each partition. Partitioning by a unique transaction identifier usually creates many tiny groups while providing little benefit to date-based reports. Date partitioning also requires a late-arrival policy: a record arriving today may belong to an earlier business date, so processing only today's arrival folder and writing today's business partition are not equivalent operations.

In Glue's catalog-based reads, a `push_down_predicate` filters partition metadata before the job lists and reads the selected files. This saves input work compared with loading the entire dataset and filtering afterward. It is distinct from choosing fewer columns within Parquet files. The first reduces which partitions are opened; the second reduces which column data is needed. A catalog partition index with `catalogPartitionPredicate` can additionally reduce metadata-listing work when the partition count itself becomes a bottleneck. The two predicate options use different expression syntaxes, so do not copy one expression blindly into the other.

A Spark-based Glue script can use a **DynamicFrame**, Glue's data abstraction for integration transformations, or a Spark DataFrame with an explicit schema. The following fragment illustrates writing an already validated DynamicFrame to partitioned Parquet. It assumes a configured `glue_context`, an input named `cleaned`, and an `event_date` column; it is not a complete deployable job.

```python
glue_context.write_dynamic_frame.from_options(
    frame=cleaned,
    connection_type="s3",
    connection_options={
        "path": "s3://example-curated/orders/",
        "partitionKeys": ["event_date"],
    },
    format="parquet",
)
```

Control file layout as well as format. Large numbers of small files increase listing, planning and task overhead, while poorly distributed partitions can leave one worker doing most of the work. Test the output with representative queries and measure bytes read, elapsed time and file counts. Preserve original raw inputs long enough to reproduce a transformation and validate the converted data before publishing its catalog location. A successful file write alone does not establish that a report has the expected rows or totals.

## Track incremental work and orchestrate dependencies

**Job bookmarks**, Glue's persisted processing state, help supported jobs select input that has not already been processed. For supported S3 sources, Glue uses object modification times when identifying new or changed objects. For Java Database Connectivity (JDBC) sources, bookmark keys identify progression through the source; select suitable ordered keys and verify their semantics. A bookmark is not a database change-log consumer. Arbitrary updates to older rows or deleted rows require a deliberate extraction design rather than an assumption that an increasing identifier captures every change.

Enable bookmarks for supported Spark processing and preserve the expected job initialization, transformation context and commit behavior in the script. `job.init` retrieves state and `job.commit` persists the updated state. A transformation context identifies the state associated with a particular operation. Reusing a context after pointing its source at a different dataset can apply old progress to new input and skip records. Treat changes to source location, context identifiers and job identity as changes to the incremental-processing design, not as harmless renaming.

The bookmark modes answer different operational questions. Enable advances processing state across successful runs. Disable ignores it. Pause can process data without advancing state, including controlled run ranges for a backfill. Resetting or rewinding state allows input to be processed again, but does not remove previous target files. A job that appends output can therefore duplicate records after a retry or backfill. Design idempotent publication, meaning repeating an operation produces the same intended final result, with an isolated output location, controlled replacement or a target that supports the required update semantics.

**AWS Glue workflows**, the orchestration graphs for related Glue jobs and crawlers, express dependencies and expose progress for an entire pipeline. Scheduled triggers start time-based work; on-demand triggers start it explicitly; conditional triggers respond to specified job or crawler completion states. A sequence might discover raw data, transform it, then update curated metadata after successful processing. Conditional trigger chains rely on jobs or crawlers started through the trigger chain; manually starting one component is not equivalent to starting the workflow's intended entry point.

**Amazon EventBridge**, the event-routing service, can start event-driven Glue workflows, including batching events before starting a run. **AWS Step Functions**, the managed workflow orchestration service, is useful when the process spans Glue and other AWS services or needs broader state-machine control. Choose Glue workflows for a Glue-centered dependency graph, and consider Step Functions when the surrounding application requires richer cross-service coordination. Neither choice removes the need to handle duplicate starts, partial output and failed publication.

Limit concurrent runs according to both available compute and output safety. Two individually successful jobs can still overwrite each other's output if they publish the same partition concurrently. Glue job-run queuing can help supported jobs wait for capacity rather than fail immediately, but workflow concurrency is a separate boundary. AWS does not automatically retry workflow runs that fail because the workflow concurrency limit is exceeded. Keep a durable record of work due and a recovery path so a missed start does not silently become a missing business day. Know the structural limits before designing around them: a workflow holds at most 100 jobs, crawlers and triggers in total, a single trigger can start at most two crawlers, and an EventBridge batch window for an event-driven workflow tops out at 900 seconds. A pipeline that outgrows these needs decomposition into several workflows or Step Functions, not a quota increase request.

## Separate streaming progress from schema contracts

Glue streaming ETL processes sources such as **Amazon Kinesis Data Streams**, the managed record-stream service, and **Amazon Managed Streaming for Apache Kafka (Amazon MSK)**, the managed Apache Kafka service. Spark Structured Streaming jobs apply transformations through micro-batches rather than treating each scheduled run as an independent batch extract. Use this when incoming records need ongoing cleansing or enrichment before reaching a target. Choose the processing interval and capacity from the freshness requirement, arrival rate and transformation complexity; serverless infrastructure does not imply zero processing delay.

Streaming jobs use checkpoints to track progress, not job bookmarks. Preserve the checkpoint location across a normal stop and restart when the goal is to resume processing. Changing or removing it changes recovery behavior and can lead to reprocessing. Checkpoint recovery also depends on the source still retaining the necessary records and on a compatible processing design. A checkpoint cannot restore expired source history. Before a streaming change, consider both the application's state and whether the destination can safely receive records again after an interruption.

**AWS Glue Schema Registry**, the registry of versioned streaming-data contracts, is distinct from the table metadata in the Data Catalog. Producer and consumer integrations use registered schemas for serialization and deserialization. It supports Avro, JSON Schema and Protocol Buffers. A compatibility policy controls which new versions may be registered. Backward compatibility concerns newer consumers reading older data; forward compatibility concerns older consumers reading newer data. Full compatibility addresses both directions, while the ALL variants extend checks over the relevant version history. Choose a policy based on consumer upgrades and replay needs, then test actual producers and consumers.

Schema compatibility is structural, not a guarantee that values make business sense. A producer can keep the same numeric field type while switching its unit from dollars to cents. That change may pass structural validation and still corrupt reports. Document field meaning, coordinate semantic changes and evaluate data quality separately. Likewise, the schema registry is not a streaming queue, a data archive or a substitute for encryption. It governs the contract that applications use; records still travel through their configured stream and remain subject to its access and retention design.

Keep the three kinds of state separate during incident analysis. Catalog metadata describes where a table lives and how it is read. Registry versions describe streaming record structure and compatibility. Bookmarks or checkpoints describe processing progress for different job types. Recreating a catalog table will not rewind a streaming checkpoint, and selecting a new schema version will not remove duplicate output. Identify which state is wrong before repairing it. This distinction often separates a managed, narrow fix from a destructive rebuild of an otherwise healthy pipeline.

## Secure the data path and make quality a publication gate

**AWS Identity and Access Management (IAM)**, the authorization service, supplies the roles Glue assumes for crawlers and jobs. Scope a crawler to the datasets it needs to discover and a job to its sources, targets, scripts, temporary files and logs. The person allowed to define a job also needs appropriate permission to pass its execution role. Granting access to catalog metadata alone is not permission to read S3 objects, decrypt them or log into a database. Diagnose these boundaries separately when a job can list a table but cannot read its records.

**AWS Lake Formation**, the service for governing data-lake access, can add fine-grained permissions for supported catalog-backed access paths. Verify the job's integration and access mode instead of assuming that a table grant makes every Spark operation authorized. **AWS Key Management Service (AWS KMS)**, the managed encryption-key service, controls the keys needed for encrypted sources and outputs. Glue security configurations can cover S3 output, logs and bookmark encryption. The job still needs the relevant key permissions; encryption settings do not automatically authorize a role to decrypt an input or write under a different account's key.

For a private JDBC database, configure the Glue connection with the needed subnet and security groups in **Amazon Virtual Private Cloud (Amazon VPC)**, the logically isolated network service. Glue creates network interfaces with private addresses. Database rules must allow the required database traffic, and Glue workers need their documented self-referencing security-group communication rules. An internet gateway alone cannot provide internet access to interfaces without public addresses. Supply private endpoints for the AWS services used, or network address translation (NAT) for destinations that require public connectivity. Also check address capacity, name resolution and routes when jobs fail before processing begins.

**AWS Glue Data Quality**, the managed data-validation capability, evaluates rules written in **Data Quality Definition Language (DQDL)**. It can evaluate cataloged datasets or run within ETL jobs. Rules can express requirements such as completeness, uniqueness and acceptable values. Recommendations help establish a starting ruleset but do not replace business approval. A dataset may satisfy every inferred rule while violating a requirement that the sample never revealed. Version rules with the transformation and make quality thresholds explicit before a pipeline starts deciding what to publish.

Evaluation and enforcement are separate decisions. Collecting quality results is useful monitoring, but a requirement to prevent invalid records entering the curated dataset needs explicit failure or quarantine behavior before publication. ETL integration can identify failing records for supported checks; catalog-based evaluation has different capabilities. Route acceptable data to the curated destination and rejected data to a restricted location with enough context for correction. Preserve counts and reconciliation evidence so silently dropping bad records does not produce a clean-looking but incomplete report.

**Amazon CloudWatch**, the metrics and logging service, receives Glue operational information and can expose data-quality results. Monitor job failures, runtime, resource utilization and whether expected output arrived. A technically successful job that read no new records may represent normal inactivity or a broken source, depending on the business schedule. Use data freshness and reconciliation alongside infrastructure health. Keep sensitive values out of diagnostic output, and protect logs and rejected records with the same care as the original dataset.

## Match capacity and cost to the useful work

Glue compute is priced by the capacity and time used for the selected job or crawler type. A data processing unit (DPU) is the billing unit of capacity, currently 4 vCPUs and 16 GB of memory. Compute is billed by the second, with a ten-minute minimum for each crawler run and a one-minute minimum for jobs on Glue 2.0 and later. A Spark job defaults to 10 DPUs and cannot go below 2; a Python shell job runs at 1 DPU or 0.0625 DPU, which is why small coordination scripts do not belong on Spark. Catalog metadata storage and requests have their own pricing dimensions, with the first million objects stored and the first million requests each month free; DataBrew sessions and jobs have separate billing. The Schema Registry has no additional service charge, but the streams, storage and processing around it can still cost money. Treat the pricing page as the source for current regional rates and minimum billing periods instead of memorizing one hourly figure for every Glue feature.

Worker selection affects memory and execution capacity. More workers can help when the workload has enough independent partitions, but cannot make a single skewed key evenly distributed or eliminate repeated full-source scans. Inspect the Spark execution behavior before scaling. If most workers wait while one task processes a dominant customer, address skew and partition design. If reading unnecessary historical partitions dominates runtime, push down the filter. If every run lists enormous numbers of small files, improve the file layout. These changes reduce the actual work instead of purchasing more resources to repeat it.

Glue Auto Scaling can add and remove workers within the configured maximum for Spark batch and streaming jobs on Glue 3.0 and later, using the G.1X through G.16X and R-series worker types, plus G.025X for streaming jobs only. Set that maximum from the job's needs, account capacity and budget. Observe actual worker utilization and runtime rather than assuming that automatic scaling is always cheaper. A job with stable, predictable demand and a job whose parallelism varies by stage have different capacity profiles. Test an optimization against the same representative input, and compare both elapsed time and consumed capacity so a faster but much larger job is not mistaken for a cost reduction.

For nonurgent batch work, the Flex execution class trades more variable startup and execution timing for lower compute cost. Flex requires Glue 3.0 or later and the G.1X or G.2X worker type. Every other worker type is ineligible, including G.4X, G.8X, G.12X, G.16X and the memory-optimized R-series, so a job on one of those is not merely a poor fit for Flex but cannot use it at all. It suits backfills or development work without a strict completion deadline; a production report with a narrow delivery window needs a different reliability decision. Do not apply the Flex label to every job type. Long-running streaming jobs accumulate compute usage while running, so their economics differ from occasional scheduled batches even when both process similar daily volume.

Optimize the whole pipeline. Crawling unchanged datasets too frequently, retaining idle development sessions, repeating complete scans and writing excessive intermediate data all add work beyond the final transformation. Include S3 requests and storage, encryption requests, logs and network egress in the estimate. Measure cost per useful output, such as a successfully published business-day partition, and include retries in that measure. A cheap run that regularly misses the publication deadline is not an acceptable cost optimization when the requirement includes timely reporting.

## Professional depth

In a multi-account data platform, assign ownership for raw data, curated tables and the transformations that connect them. A central catalog makes metadata discoverable, but discovery and authorization remain separate. Coordinate IAM roles, Lake Formation grants where used, S3 access and encryption-key policies for the actual execution account. Test a consumer's intended read path with its real role. A platform can pass a metadata discovery test and still fail production because the job cannot decrypt objects or access a private source network.

Treat raw data, transformation code, catalog definitions, quality rules and progress state as separate recovery assets. An infrastructure template can recreate a job definition without recreating its previous bookmark or its output history. An S3 copy of curated files does not prove that a replacement environment has the correct metadata and permissions. Write down which assets are authoritative and how to reconstruct derived ones. Rehearse recovery with an isolated destination, then compare record counts, totals and publication completeness before directing consumers to the recovered dataset.

Backfills need a publication protocol. Keep their scope, code version and intended business dates explicit, and avoid sharing an output location with an unrelated live run unless the target's concurrency semantics make that safe. A practical file-based design writes to a separate location, validates the result, then performs a controlled change in what readers consume. Treat that publication step as its own operation with rollback and reconciliation. Glue bookmarks reduce repeated input work; they do not supply a transaction spanning every source, target and downstream consumer.

For modernization, distinguish moving data from changing its meaning. A pipeline that successfully transfers legacy CSV files has not necessarily produced a usable curated model. Compare the source application's key definitions, time zones, deletion behavior and decimal precision with the target contract. Validate representative historical periods before switching reports. Run old and new transformations against the same retained input when possible, explain discrepancies and document the acceptance criteria. The least operational overhead answer can still require custom business validation because no managed service can infer those rules reliably.

At scale, concurrency is an architectural resource shared with private subnet addresses, source-database capacity and downstream write throughput. Raising a Glue job limit can overload a database or cause overlapping publications. Establish workload classes, queue nonurgent work and reserve practical headroom for recovery. Monitor missed starts as well as failed runs, especially when workflow concurrency rejects new work without automatic retries. A durable inventory of expected partitions or processing requests lets operations distinguish a quiet business day from a pipeline that never started.

## Worked scenario

A distributor receives daily order exports as CSV objects in S3. Analysts query recent business dates and only a few columns, but reports repeatedly scan years of raw files. Exported customer identifiers can contain leading zeros, late orders belong to previous business dates, and finance requires missing identifiers to stop publication. The team wants managed processing and a repeatable way to correct a faulty transformation without duplicating report rows.

A crawler discovers the raw dataset into the Data Catalog. A Glue Spark job reads the required input, preserves identifiers as strings, normalizes business dates and writes partitioned Parquet to a separate curated location. Data Quality checks run before publication, with invalid input producing a failed gate or restricted quarantine output according to the agreed policy. A workflow sequences discovery, processing and metadata publication. The job's role can read raw data, write the intended curated and diagnostic paths, and use the required encryption keys. Athena reads the curated table for date-filtered reports.

Bookmarks reduce repeat input processing for the supported batch source, while the output design remains idempotent. A correction backfill writes to an isolated location and is reconciled before replacing what analysts read. CloudWatch monitoring covers execution and freshness, and finance compares record counts and order totals. The exam asks for format conversion and lower scan work with the least operational overhead: the keyed design is a Glue transformation into appropriately partitioned Parquet, with metadata available to Athena. A crawler alone discovers structure but cannot perform that conversion, and resetting a bookmark alone cannot clean previously published output.

## Exam lens

- "Discover file schemas and register tables" maps to crawlers and the Data Catalog.
- "Convert CSV to Parquet" maps to a transformation job, not a metadata edit.
- "Query recent dates and selected columns" maps to suitable partitions and columnar output.
- "Filter before loading historical partitions" maps to a partition pushdown predicate.
- "Large distributed joins" maps to Spark; a Python shell script is not distributed Spark.
- "Analysts clean data without code using recipes" maps to DataBrew.
- "Process only new supported batch input" maps to bookmarks plus correct state handling.
- "Replay a backfill without duplicate output" requires output reconciliation, not just bookmark reset.
- "Resume streaming progress" maps to checkpoints, not job bookmarks.
- "Control streaming schema evolution" maps to Schema Registry compatibility policies.
- "Reject invalid business records" requires quality checks and an explicit publication gate.
- "Private database access" requires the role, database authorization and a working private network path.
- "Variable Spark capacity demand" suggests evaluating Auto Scaling with a suitable maximum.
- "Nonurgent eligible batch processing" suggests Flex when variable execution timing is acceptable.
- "A new customer needs Glue for Ray" requires a supported alternative; the restriction does not close Glue Spark.

## Knowledge check

### 1. Reducing report scan work (Associate)

A retailer stores daily sales exports as CSV in S3. Analysts use Athena to query a few columns for selected business dates, but each report reads large amounts of historical data. The team wants to reduce scan work without operating a processing cluster.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Run a crawler more often and retain the existing CSV file layout.
- **B)** Run a Glue Spark job that writes typed Parquet partitioned by business date, and expose the curated data through catalog metadata.
- **C)** Increase the number of workers in the job that produces the same unpartitioned CSV output.
- **D)** Create additional catalog databases that all reference the same unpartitioned CSV objects.

<details><summary>Answer</summary>

**Answer: B.** Parquet supports selective column reads, and business-date partitioning allows date-filtered queries to skip unrelated data. Glue manages the processing infrastructure. A can improve metadata freshness but does not change storage format or layout. C can affect transformation runtime but leaves the analysts' scan pattern unchanged. D creates more metadata names for the same bytes, so it does not reduce the input needed by those queries. The requirement concerns the physical output that the query engine reads.

*Where this is covered: Convert CSV to Parquet and design the partition layout.*

</details>

### 2. Preparing data without writing scripts (Associate)

A business analyst receives supplier datasets with inconsistent names and missing values. The analyst wants to explore sample data, assemble reusable cleaning steps visually, and apply those steps to each complete dataset. The analyst does not write Python or Spark code.

Which solution will meet these requirements?

- **A)** Configure a Glue crawler to discover the supplier files.
- **B)** Register producer schemas in Glue Schema Registry.
- **C)** Create a DataBrew project and recipe, then run recipe jobs on the datasets.
- **D)** Maintain custom Python shell scripts for each supplier's preparation steps.

<details><summary>Answer</summary>

**Answer: C.** DataBrew provides visual exploration and reusable preparation recipes, with jobs applying the steps to complete datasets. A discovers metadata but does not carry out the cleaning process. B governs streaming schemas rather than providing interactive dataset preparation. D can implement cleaning but requires maintaining code, which conflicts with the analyst's requirement. Previewing the recipe helps design the transformation, while running and checking the full job verifies its behavior beyond the sample.

*Where this is covered: Choose Spark, Python shell or a visual preparation tool.*

</details>

### 3. Avoiding repeated batch processing (Associate)

A logistics company adds immutable CSV objects to an S3 source and runs a supported Glue Spark job on a schedule. Every run currently reads the full source history. The team wants Glue to remember completed input processing, and it also wants recovery attempts to avoid duplicating records in the published dataset.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable job bookmarks and preserve the script's initialization, transformation contexts and state commit.
- **B)** Schedule the crawler to run immediately before every job so the catalog always lists the newest objects.
- **C)** Filter each run in the script to objects whose last modified time falls in the past 24 hours, instead of enabling bookmarks.
- **D)** Depend on job bookmarks alone to keep the published dataset free of duplicate records after a failed run is retried.
- **E)** Design controlled replacement or another idempotent output-publication process for retries and backfills.

<details><summary>Answer</summary>

**Answer: A and E.** A lets supported batch input processing use persisted progress. E handles the separate destination problem when input must be processed again. B keeps catalog metadata current, but catalog freshness is not job progress: the job still reads every listed partition. C replaces persisted progress with a hand-rolled time window, which loses an object that arrives late and skips an entire interval whenever a scheduled run is missed, while a rerun processes the same window twice. D over-extends the mechanism: bookmarks select input and never inspect the target, so a retry that republishes rows it already wrote still duplicates them. That separation is why E is needed alongside A rather than instead of it.

*Where this is covered: Track incremental work and orchestrate dependencies.*

</details>

### 4. Resuming continuous processing (Associate)

A company runs a Glue streaming ETL job against Kinesis Data Streams. It needs to stop the job for a compatible configuration change, then resume from saved progress. The source will retain the required records throughout the interruption, and the target is designed to tolerate retries.

Which solution will meet these requirements?

- **A)** Preserve the streaming checkpoint location and restart the compatible job using that checkpoint.
- **B)** Enable batch job bookmarks and use them instead of the streaming checkpoint.
- **C)** Delete the checkpoint and start again from the configured initial stream position.
- **D)** Run a crawler over the output and use its catalog table as the job's processing offset.

<details><summary>Answer</summary>

**Answer: A.** Streaming jobs use checkpoints to preserve progress, and the scenario supplies the source retention and target behavior needed for recovery. B substitutes the batch progress mechanism for the streaming mechanism. C discards the saved position and can reprocess data instead of resuming as required. D refreshes table metadata but does not record the stream position for the job. Catalog definitions and processing checkpoints solve different problems even when both belong to the same pipeline.

*Where this is covered: Separate streaming progress from schema contracts.*

</details>

### 5. Preventing invalid records from being published (Associate)

A finance team requires every published order to have a customer identifier and an acceptable order total. A Glue job currently writes all rows to curated storage, and an overnight report lists invalid values after analysts have already used them. The team wants managed validation before the curated dataset is released.

Which solution will meet these requirements?

- **A)** Update the crawler's schema-change policy and keep the current publication order.
- **B)** Register the field types in Schema Registry and rely on schema compatibility to validate all business values.
- **C)** Alarm only on Spark memory utilization before allowing the job to run.
- **D)** Add Data Quality rules to the ETL job and explicitly fail or quarantine invalid data before publication.

<details><summary>Answer</summary>

**Answer: D.** Data Quality evaluates the rules, while the explicit gate controls whether bad data reaches consumers. A changes metadata handling rather than validating each required business condition. B can enforce structural contracts but does not prove that every customer identifier or total is acceptable. C monitors processing resources rather than data validity. Reporting failed checks after publication is too late for this requirement, so rule evaluation must be connected to the output-release decision.

*Where this is covered: Secure the data path and make quality a publication gate.*

</details>

### 6. Reading an encrypted private source (Professional)

A company runs Glue jobs in an analytics account and reads encrypted S3 objects owned by another account. The same jobs must query a private JDBC database reachable through the company's private network. An engineer can browse the catalog, but production jobs fail when accessing the actual inputs.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Grant access to the catalog database and rely on that grant to authorize S3 decryption and JDBC login.
- **B)** Configure the job's VPC connection, subnet, security groups and routes for the private database and required AWS endpoints.
- **C)** Increase the Spark worker count so failed data-access requests run concurrently.
- **D)** Authorize the execution role for the required objects and encryption keys, and configure the database's required authentication and access.
- **E)** Put the Glue network interfaces in a public subnet with an internet-gateway route as the only connectivity change.

<details><summary>Answer</summary>

**Answer: B and D.** B establishes the required network path; D establishes the separate authorization and authentication boundaries for actual data access. A confuses metadata visibility with access to objects, keys and the database. C adds compute but cannot repair a missing route or denied permission. E does not give Glue's private-address interfaces a public address and does not establish the specified private database path. Check the role used by the job, not only the engineer's console permissions.

*Where this is covered: Secure the data path and make quality a publication gate.*

</details>

### 7. Correcting a published historical partition (Professional)

A data platform appends daily Glue output to curated S3 storage used by several reporting accounts. A transformation defect affected one historical month, while the current pipeline must keep running. The team can reprocess retained raw input but must validate the correction before consumers see it and must avoid counting the old and corrected rows together.

Which solution will meet these requirements?

- **A)** Reset the production job's bookmark and append the corrected month to the existing curated location.
- **B)** Recrawl the curated location and treat the refreshed schema as correction of the stored records.
- **C)** Process the affected month into an isolated output location, reconcile it, and perform a controlled replacement of the affected published data.
- **D)** Increase workflow concurrency and run the backfill and current job against the same output without coordinating publication.

<details><summary>Answer</summary>

**Answer: C.** Isolating the correction permits validation before publication and provides a deliberate replacement step that avoids exposing both versions together. A reprocesses input but leaves the previous target records present. B changes metadata, not incorrect values already stored. D increases execution overlap without defining safe output semantics and can introduce races. The key requirement is controlled publication of a validated correction while live processing continues, not simply the ability to rerun the transformation.

*Where this is covered: Professional depth.*

</details>

### 8. Handling variable batch demand (Professional)

An analytics platform has eligible Spark backfills with flexible completion times and separate reporting jobs with strict deadlines. Worker demand varies across backfill stages, and some event-driven workflow starts are missed when the workflow concurrency limit is reached. The team wants to reduce unnecessary compute use while ensuring missed work can be recovered.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Evaluate Flex and bounded Auto Scaling for the eligible backfills while preserving appropriate execution settings for deadline-sensitive reports.
- **B)** Rely on Glue job-run queuing to re-run the workflow starts that the concurrency limit rejected.
- **C)** Request higher worker and workflow concurrency quotas so that no start is rejected.
- **D)** Provision each backfill at a fixed worker count sized for its heaviest stage.
- **E)** Track expected work durably and reconcile missed workflow starts, with concurrency aligned to downstream capacity.

<details><summary>Answer</summary>

**Answer: A and E.** A applies cost-oriented execution choices to work that tolerates their timing tradeoffs and bounds automatic capacity growth. E handles the separate risk of work that never started. B applies a job-level mechanism to a workflow-level boundary: queuing makes an individual job run wait for capacity, and Glue does not automatically retry a workflow run rejected by the concurrency limit. C raises the ceiling but still loses any start rejected before the increase, and it can push load onto sources and destinations that were never sized for it. D pays for the heaviest stage throughout the run, including stages with little parallelism, and still does not recover a missed start. Cost and completeness require separate controls.

*Where this is covered: Match capacity and cost to the useful work.*

</details>

## Summary

Start by deciding whether the requirement concerns metadata, transformation or processing progress. The Data Catalog describes datasets and crawlers discover their structure; Spark jobs perform distributed transformations, while Python shell jobs suit smaller scripts. Glue Studio provides visual job authoring and DataBrew provides reusable visual preparation recipes. Convert CSV into typed Parquet and choose partitions from real query filters, then validate both correctness and scan savings. Use bookmarks for supported batch input and checkpoints for streaming, with an independent design for retries, backfills and output publication. Schema Registry governs streaming contracts; Data Quality evaluates business rules that must be connected to an explicit gate when invalid data must be withheld. Secure the execution role, underlying storage, encryption keys and private network path separately. Orchestrate dependencies, track missed work and choose capacity from observed utilization. Evaluate Flex for eligible nonurgent work and Auto Scaling for variable demand while preserving deadline and recovery requirements. New customers must choose an alternative to Glue for Ray.

## Related units

- [Amazon S3](../01-storage/s3.md): raw and curated object storage, encryption and access policies
- [Kinesis and streaming delivery](kinesis.md): stream retention, replay and ingestion choices
- [Amazon Athena](athena.md): SQL access and query-scan optimization for curated data
- [AWS Lake Formation](lake-formation.md): governed catalog access across accounts
- [Amazon EMR](emr.md): choosing managed frameworks when processing needs differ from Glue jobs
- [Amazon VPC](../04-networking/vpc.md): private routes, endpoints and security-group behavior
- [Amazon CloudWatch](../08-management/cloudwatch.md): operational metrics, alarms and logs

## Sources

- [What is AWS Glue?](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html): integration service and Glue Studio authoring
- [Data discovery and cataloging](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html): metadata, consumers and explicit table definitions
- [Defining crawlers](https://docs.aws.amazon.com/glue/latest/dg/add-crawler.html): classifiers, sources and crawler behavior
- [Spark job properties](https://docs.aws.amazon.com/glue/latest/dg/add-job.html): runtimes, workers, execution class and queuing
- [Python shell jobs](https://docs.aws.amazon.com/glue/latest/dg/add-job-python.html): script execution and bookmark limitation
- [What is DataBrew?](https://docs.aws.amazon.com/databrew/latest/dg/what-is.html): visual preparation, recipes and output
- [Glue for Ray availability change](https://docs.aws.amazon.com/glue/latest/dg/awsglue-ray-jobs-availability-change.html): new-customer closure and EKS alternative
- [CSV format support](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-format-csv-home.html): CSV parsing and format options
- [Parquet format support](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-format-parquet-home.html): columnar reads and writes
- [Managing partitions](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-partitions.html): partition pruning, indexes and partitioned output
- [Job bookmarks](https://docs.aws.amazon.com/glue/latest/dg/monitor-continuations.html): modes, source state, reset and target limitations
- [JDBC connections](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-connect-jdbc-home.html): relational sources and connection options
- [Orchestrating workflows](https://docs.aws.amazon.com/glue/latest/dg/orchestrate-using-workflows.html): Glue-centered workflow orchestration
- [Workflow overview](https://docs.aws.amazon.com/glue/latest/dg/workflows_overview.html): event starts and concurrency rejection behavior
- [Glue triggers](https://docs.aws.amazon.com/glue/latest/dg/about-triggers.html): schedules, conditions and dependency-chain restrictions
- [Streaming ETL jobs](https://docs.aws.amazon.com/glue/latest/dg/add-job-streaming.html): stream sources, micro-batches and checkpoints
- [Schema Registry](https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html): supported contracts and compatibility modes
- [Execution roles](https://docs.aws.amazon.com/glue/latest/dg/create-an-iam-role.html): source, target, key and role permissions
- [Private JDBC connectivity](https://docs.aws.amazon.com/glue/latest/dg/connection-JDBC-VPC.html): interfaces, security groups and public-egress constraints
- [Security configurations](https://docs.aws.amazon.com/glue/latest/dg/encryption-security-configuration.html): encryption of output, logs and bookmarks
- [Glue Data Quality](https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html): rules, evaluation contexts and integration differences
- [Glue Auto Scaling](https://docs.aws.amazon.com/glue/latest/dg/auto-scaling.html): variable worker capacity and utilization monitoring
- [AWS Glue pricing](https://aws.amazon.com/glue/pricing/): compute, metadata, DataBrew and registry pricing dimensions
- [Step Functions integration](https://docs.aws.amazon.com/step-functions/latest/dg/connect-glue.html): starting Glue jobs and waiting for completion
- [Lake Formation access in Glue](https://docs.aws.amazon.com/glue/latest/dg/security-lf-enable.html): runtime-dependent fine-grained access and IAM requirements
