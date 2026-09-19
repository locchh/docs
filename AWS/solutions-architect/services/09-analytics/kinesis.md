# Amazon Kinesis streaming services

**Where it sits on the exams.** **Amazon Kinesis Data Streams**, the managed real-time record stream, retains ordered records so several independent consumers can process and replay them. **Amazon Data Firehose**, formerly Amazon Kinesis Data Firehose, buffers and delivers streaming data to destinations with little consumer code. **Amazon Managed Service for Apache Flink**, formerly Kinesis Data Analytics for Apache Flink, runs stateful stream-processing applications, while **Amazon Kinesis Video Streams** ingests and stores time-indexed media. These services serve SAA-C03 task 3.5, and support SAP-C02 task 2.5, "Designing large-scale application architectures for a variety of access patterns", as a secondary owner behind DynamoDB. Rule of thumb: Data Streams is the durable replayable log, Data Firehose is managed delivery, Managed Service for Apache Flink is stateful computation, and Video Streams is time-encoded media ingestion.

## Records, shards and ordering

A Data Streams producer sends a data blob, partition key and optional explicit hash key. Kinesis computes an MD5 hash of the partition key and maps that hash to one open shard's hash-key range. The shard is the capacity and ordering unit. The service adds a sequence number that increases within the shard, and consumers receive the shard's records in sequence-number order. Ordering is not global across a stream.

Use the same partition key for records that require relative ordering, such as updates for one customer or device. Distribute keys across a large cardinality so traffic also spreads across shards. A timestamp or a constant can concentrate writes into one hot shard even when the stream has ample aggregate capacity. Random keys spread load but discard per-entity ordering. The design question is therefore which records must be ordered together, not merely how many shards exist.

A data record contains the partition key, sequence number and payload. The maximum payload before base64 encoding is currently 10 MiB. Kinesis is designed to accommodate intermittent records between 1 and 10 MiB with burst capacity; steady provisioned shard throughput remains governed by its normal write rate. Large records consume more capacity, raise retry cost and can exceed limits in downstream integrations, so splitting or storing a large object in **Amazon Simple Storage Service (Amazon S3)**, the durable object storage service, and streaming a reference is often safer.

Data Streams stores records across three Availability Zones in a Region. The default retention is 24 hours and can be increased to 365 days. Retention permits consumers to replay from an earlier position and lets a recovered consumer catch up. It is not an archive with S3 lifecycle classes, and increasing retention does not increase consumer throughput. Send records to durable analytical storage when policy requires retention beyond the stream window.

A new consumer chooses a starting position. `LATEST` begins near records arriving after it starts, `TRIM_HORIZON` begins at the oldest retained record, and timestamp or sequence-based positions support bounded replay. Checkpointing advances the application's durable progress independently of stream retention. If its checkpoint falls behind the trim horizon, the missing records are no longer recoverable from the stream, so retention must cover the maximum expected outage and catch-up time.

A sequence number identifies position within a shard, but producer retry behavior still matters. A timeout can occur after the service accepted a write, so a retry can create a duplicate application event. Include an application event ID and make consumers idempotent. `PutRecords` can partially succeed: inspect every entry in the response and retry failed records with backoff rather than replaying the whole batch blindly.

## Capacity modes, scaling and retention

Provisioned mode makes the customer choose shard count. Each shard supplies baseline write capacity of 1 MiB per second or 1,000 records per second and shared read capacity of 2 MiB per second. Size for the larger of the write requirement and read requirement, then test the partition-key distribution. More shards do not repair a key that sends most records to one hash range.

Provisioned streams scale by splitting shards to add parallel capacity and merging adjacent shards to reduce it. Resharding leaves parent shards available for their retained records while consumers discover and process child shards. The **Kinesis Client Library (KCL)** coordinates leases and assigns shard processors across a consumer fleet, including the parent-before-child processing needed around resharding. Scaling is online, but consumer code must handle the changing shard graph.

An open shard accepts writes; a closed parent shard contains its earlier retained records but no new writes. Consumers must finish the parent before relying on ordered processing from its children. Splitting one hot shard creates two hash ranges and is useful after improving key distribution, while merging two cold adjacent ranges reduces provisioned capacity. A split cannot divide traffic from one unchanged partition key between children because that key still hashes to one value.

On-demand Standard mode manages shards and capacity automatically. It handles traffic growth based on observed peaks and can accept an immediate increase up to roughly twice the previous peak; a faster jump can throttle until capacity adapts, so producers still need retry with exponential backoff. Uneven partition keys can also throttle an on-demand stream because one key remains concentrated. On-demand removes capacity planning, not partitioning discipline or quotas.

On-demand Advantage is a Region-level, account setting for all on-demand streams. It adds configurable warm write throughput, discounted usage dimensions and a higher enhanced-fan-out consumer allowance, but commits the account to minimum billed ingest and retrieval usage. It fits sustained aggregate throughput or many streams and consumers, not a small intermittent workload. On-demand Standard keeps per-stream pricing without that account commitment. Provisioned fits predictable volume, fine-grained shard control or purchased shard-hour economics.

Warm throughput prepares on-demand Advantage capacity for a forecast event without changing the producer API or partition scheme. It helps an aggregate surge but cannot make a single hot key parallel. Because Advantage applies at the account and Region level, evaluate the combined on-demand fleet against its usage commitment. A single low-volume stream can be cheaper and simpler on Standard even if another account with hundreds of streams benefits from Advantage.

Monitor incoming bytes and records, write and read throttles, iterator age, successful record counts and consumer lag. `IteratorAgeMilliseconds` rising means a polling consumer is falling behind even if writes succeed. Increase consumer processing, use enhanced fan-out, reduce per-record work or add stream capacity as the bottleneck requires. Scaling shards cannot accelerate a consumer that serially processes all entities in one partition.

## Producers, consumers and delivery guarantees

`PutRecord` sends one record and `PutRecords` batches up to 500 records with a 10 MiB total request limit. The **Kinesis Producer Library (KPL)**, a client-side aggregation and batching library, combines user records into Kinesis records to use requests efficiently. Aggregation improves throughput for small events but adds buffering latency and requires compatible deaggregation in consumers. Flush carefully during shutdown so locally buffered records are not abandoned.

Standard consumers poll shards with `GetRecords` and share a shard's 2 MiB-per-second read capacity. Several applications can contend, and each must manage iterators and polling. A stream supports up to 20 registered enhanced-fan-out consumers by default, so a design expecting dozens of independent readers has to plan around that ceiling. Enhanced fan-out registers a consumer and uses `SubscribeToShard` over HTTP/2, giving each registered consumer dedicated read throughput of up to 2 MiB per second per shard and push delivery with lower propagation latency. Use it when several latency-sensitive consumers must read the same stream without sharing the polling limit.

KCL is appropriate for a long-running custom application that needs checkpointing, lease coordination and rebalancing across workers. Each application name has its own lease state and checkpoints, so two independent business consumers should not accidentally share one application identity. A failed worker's leases move to another worker, which resumes after the checkpoint and may reprocess records. Idempotency turns that at-least-once processing into a safe business result.

KCL stores coordination state, including leases and checkpoints, in an **Amazon DynamoDB** table, the managed key-value and document database, and emits operational metrics to **Amazon CloudWatch**, the monitoring and observability service. Adding workers beyond the useful shard parallelism does not make one shard processor concurrent. During a scale event, allow time for lease balancing and watch lag rather than assuming every new worker immediately receives equal work.

**AWS Lambda**, the serverless function service, can poll a stream through an event source mapping. Lambda invokes the function with batches from each shard and preserves record order within that shard by default. Configure starting position, batch size and window, parallelization, retry limits, bisect-on-error and an on-failure destination according to failure policy. A poison record can block later records in its shard when retries are unbounded; bounded retries and failure capture trade strict retry for forward progress.

Partial batch response lets the function identify a failed sequence number so the mapping retries from that point instead of treating every successful item as failed. Bisecting locates a bad record by splitting failed batches, while parallelization can process several batches per shard with ordering maintained at the partition-key level. These controls reduce blast radius but do not remove the need for idempotent writes when an invocation succeeds after its acknowledgement is lost.

Encrypt Data Streams at rest with the AWS managed key for Kinesis, `aws/kinesis`, or a customer managed **AWS Key Management Service (AWS KMS)** key, the managed encryption-key service, and use TLS in transit. **AWS Identity and Access Management (IAM)**, the AWS authorization service, policies control stream operations and enhanced consumers. Interface VPC endpoints keep API traffic on private connectivity. Producers need write actions and consumers need only the read and describe actions their library actually calls.

## Deliver with Amazon Data Firehose

Data Firehose is a delivery stream, not a replayable consumer log. It accepts direct puts and supported sources including Data Streams and **Amazon Managed Streaming for Apache Kafka (Amazon MSK)**, the managed Apache Kafka service, then buffers, optionally transforms, and delivers batches. It scales the delivery infrastructure and retries according to the destination behavior. Choose it when the outcome is reliable delivery to storage or analytics without writing and operating a consumer fleet.

When Data Streams is the source, Firehose reads as a managed consumer and delivery does not remove records from the source or change other consumers' checkpoints. Direct PUT instead makes Firehose the ingestion endpoint and provides no Data Streams retention for independent replay. Choose the former when several applications need the same log; choose direct ingestion when destination delivery is the only stream behavior required.

Destinations include S3, **Amazon Redshift**, the managed data warehouse, **Amazon OpenSearch Service**, the managed search and analytics service, Splunk and supported HTTP endpoints. Redshift delivery first places files in S3 and then issues a `COPY`; Firehose does not stream individual records directly into warehouse tables. S3 can also retain source records or failed transformed records depending on the destination and backup configuration.

Destination failure behavior belongs in the design. Firehose retries for the configured retry window, which for Amazon S3 delivery runs up to 24 hours before the data is lost and can place records that cannot reach a supported destination into an S3 error or backup prefix. Alarm on delivery freshness, failed transformation and backup growth, and rehearse replay from the retained objects. A successful producer acknowledgement means Firehose accepted the record, not that Redshift, OpenSearch or an HTTP endpoint already committed it.

Buffer size and interval are hints that trade latency for delivery efficiency. Firehose can deliver earlier when the buffer fills and some destinations use different behavior; neither hint is a strict maximum delivery time. Larger buffers generally make larger files and reduce downstream request overhead, while smaller buffers reduce latency. The service is near-real-time, not the answer for a per-event subsecond consumer reaction. Arrival frequency is itself a selector, and SAA-C03 task 3.5 names it directly. A requirement for subsecond reaction to each event maps to Data Streams, with enhanced fan-out when several consumers each need that latency. A requirement measured in minutes, such as landing records in a data lake for later query, maps to Firehose and its 60 to 900 second buffering, or to the zero-buffer hint when the destination supports it. Data that arrives on a schedule in bulk is not a streaming problem at all: that is a batch transfer and an AWS Glue job, and a stream in the answer options is the distractor.

A Lambda transformation receives buffered records and returns a result for each with success, drop or processing-failed status and encoded output. Keep the function within Firehose limits, handle retries idempotently and preserve failed input for investigation. For record format conversion, Firehose can use an **AWS Glue Data Catalog**, the shared metadata catalog, schema to convert JSON input to Apache Parquet or ORC for S3. Compression and columnar format reduce analytical scan cost.

Dynamic partitioning evaluates keys in records and writes S3 prefixes such as customer, Region or date. Good partitions match common query predicates and avoid a huge number of tiny prefixes. It applies to S3 destinations and has its own processing and cost behavior. Firehose can also invoke data transformation and format conversion, but schema validation and business-quality checks still belong in the pipeline.

## Process state with Managed Service for Apache Flink

Managed Service for Apache Flink supplies managed compute, scaling, Availability Zone recovery, checkpoints and snapshots for Apache Flink applications. Code can use Java, Scala or Python DataStream APIs and the Table API or embedded SQL. A long-running application reads streaming and static sources, maintains distributed state, applies event-time windows or joins, and writes results to sinks. This is computation, not merely delivery.

Flink checkpoints capture consistent application state to support recovery, while savepoints or service snapshots support planned updates and rollback. Give stateful operators stable identifiers across compatible application versions so state maps correctly during restore. Exactly-once state consistency does not automatically make an external sink exactly once; the connector and destination must participate in the delivery guarantee or the application must deduplicate.

Parallelism divides operators into concurrent subtasks, and parallelism per processing unit affects how those subtasks use provisioned compute. Automatic scaling can adjust application parallelism according to load, but a key with extreme skew can still concentrate state and work in one subtask. Monitor checkpoint duration and failure, backpressure, busy time, input rate and sink errors. A growing input backlog with healthy checkpoints can still mean the application is consistently slower than its source.

Managed Service for Apache Flink Studio provides notebook-based interactive development using SQL, Python and Scala, with the option to promote work into a long-running application. Use Studio for exploration and dashboards; use a versioned Flink application and CI/CD when testing, repeatable deployment and fine-grained state control matter. Capacity is measured in Kinesis Processing Units, and parallelism controls how operator work is distributed.

The former Amazon Kinesis Data Analytics for SQL applications is discontinued. New SQL applications stopped in October 2025, existing applications were deleted starting January 27, 2026, and they can no longer be started or operated. Do not confuse that retired service with Managed Service for Apache Flink or its Studio SQL capability. The current answer for managed stateful stream processing is Managed Service for Apache Flink.

## Video streams and service selection

Kinesis Video Streams ingests video, audio and other time-encoded data from devices and stores it with timestamps for playback and processing. Producer SDKs fragment and send media; consumers can use parsers, playback protocols or integrate with video-analysis workflows. The stream handles media ordering and retention differently from JSON business events. Do not choose Data Streams merely because a camera emits data continuously.

Kinesis Video Streams with WebRTC supports real-time peer communication and low-latency media exchange, while the persisted video-stream APIs support ingestion, retention and later playback or analysis. A video call and an archival camera feed can therefore use different parts of the service. For derived detections such as "vehicle entered zone," publish a compact business event to Data Streams or EventBridge rather than forcing every downstream system to parse the original media.

Select among the neighboring messaging services by consumer model. This table separates replay, routing and protocol requirements.

| Requirement | Service | Why |
|---|---|---|
| Ordered event log with several independent replaying consumers | Kinesis Data Streams | Shards, retention, checkpoints and fan-out |
| Managed batching into S3, Redshift, OpenSearch or HTTP | Amazon Data Firehose | Destination delivery without consumer infrastructure |
| Stateful windows, joins and event-time computation | Managed Service for Apache Flink | Stateful distributed stream processing |
| Time-indexed video or audio from devices | Kinesis Video Streams | Media fragments, playback and video consumers |
| Work queue where one worker handles each message | **Amazon Simple Queue Service (Amazon SQS)**, the managed message queue | Per-message acknowledgement and visibility timeout |
| Existing Apache Kafka clients, protocols and ecosystem | Amazon MSK | Managed Kafka brokers or serverless Kafka |
| Route discrete application events by content to targets | **Amazon EventBridge**, the managed event bus | Rules and target routing rather than shard consumption |

Data Streams and SQS are frequent distractors. A Data Streams record can be read independently by many applications and replayed during retention; adding consumers does not remove it. An SQS FIFO queue preserves order within a message group but still hands each message to one consumer that deletes it, so an ordering requirement alone does not select Kinesis: choose Data Streams when several independent applications must each read and replay the same ordered records. An SQS message is normally processed by one competing consumer and deleted after acknowledgement. EventBridge routes matching events to targets and supports archive and replay as a separate feature, but it is not a continuously sharded analytics log. MSK is preferred when Kafka API compatibility, Kafka tooling or control over Kafka semantics decides the migration.

## Professional depth

For multi-account ingestion, centralize the stream only when producer network paths, IAM policies, encryption keys and regional latency permit it. A resource policy can grant cross-account data-plane access, but the producer still needs identity permission and KMS access where applicable. Regional streams do not become multi-Region because accounts share an organization. Replicate or independently ingest when regional continuity is required, and define how duplicates are reconciled.

Partition design becomes a schema contract at scale. Choose a stable business key that provides the ordering consumers require, measure its skew, and include an application event ID and schema version. A future reshard changes shard IDs but not the business ordering rule for a consistent partition key. A producer that changes partition-key derivation during migration can interleave one entity across shards and break consumers that assumed serial updates.

Deploy stateful Flink changes with snapshots and compatibility testing. Changing serializer schemas, operator identifiers or parallelism can affect whether old state restores. Run a canary application or shadow consumer against the same input when output comparison is possible, and keep the previous artifact and snapshot until new checkpoints and sink health are stable.

Treat schema evolution as a producer-consumer contract. Add compatible fields before consumers require them, carry an explicit schema version, and reject or quarantine records whose shape cannot be interpreted. A stream retains bytes, not semantic compatibility. During a producer migration, replay representative old and new records through every critical consumer and verify that Firehose conversion and Flink state serializers agree with the transition.

Control cost at every stage: provisioned shard-hours or on-demand ingest and retrieval, enhanced fan-out, extended retention, Firehose processing and format conversion, Flink capacity, Lambda invocations, KMS calls and destination storage. Small files multiply query and request cost, while over-buffering raises freshness latency. Optimize the complete path rather than the cheapest ingestion service in isolation.

## Worked scenario

A logistics company receives location updates from 300,000 vehicles. Each vehicle's updates must remain ordered, fraud detection and customer tracking consume the same events within seconds, raw data must reach S3 as partitioned Parquet, and five-minute route windows require stateful joins. Traffic is uneven and can double during storms.

Producers write to an on-demand Data Streams stream using vehicle ID as the partition key and a unique event ID for deduplication. Fraud and tracking use separate enhanced-fan-out consumers so they do not share read throughput. A third path feeds Data Firehose, which transforms records, uses the Glue schema to convert them to Parquet and dynamically partitions S3 by date and Region. Managed Service for Apache Flink reads the stream, checkpoints route state and writes windowed alerts. Iterator age, write throttling, Firehose delivery failures and Flink checkpoint health drive alarms. Large bursts use retry with jitter, while key-skew metrics identify fleets whose IDs concentrate unexpectedly.

The exam asks which combination preserves per-vehicle order, supports several low-latency consumers, delivers query-efficient history and computes stateful windows. The keyed answer is Data Streams with vehicle partition keys and enhanced fan-out, Data Firehose for Parquet delivery, and Managed Service for Apache Flink for stateful processing.

## Exam lens

- "Several applications independently consume and replay the same ordered events" maps to Kinesis Data Streams.
- "All updates for one customer must remain ordered" maps to the customer ID as partition key; global ordering across shards is not promised.
- "One partition throttles while the stream has spare aggregate capacity" maps to a hot key and skew, not automatically to too few total shards.
- "Unpredictable traffic with no shard planning" maps to on-demand; producers still retry sharp jumps and hot-key throttles.
- "Predictable throughput and direct capacity control" maps to provisioned shards sized for both records and bytes.
- "Several latency-sensitive consumers need independent read bandwidth" maps to enhanced fan-out.
- "A poison record blocks a Lambda stream consumer" maps to bounded retries, bisect-on-error and an on-failure destination, chosen against ordering needs.
- "Deliver buffered records to S3 with no custom consumer fleet" maps to Amazon Data Firehose.
- "Convert JSON to Parquet during delivery" maps to Firehose format conversion with a Glue Data Catalog schema.
- "Five-minute event-time windows and stateful joins" maps to Managed Service for Apache Flink.
- "Kinesis Data Analytics SQL application in 2026" is a retired-service distractor; use current Flink or another supported analytics path.
- "Stream camera video for time-based playback" maps to Kinesis Video Streams.
- "One worker should process and acknowledge each task" maps to SQS, not a replayable Kinesis log.
- "Existing Kafka producers must migrate without protocol changes" maps to Amazon MSK.

## Knowledge check

### 1. Preserving order for each device (Associate)

A utility company streams status changes from 50,000 field sensors into a Kinesis data stream that has several shards. Every update from a single sensor must be processed in the order it was produced, because a later update can cancel an earlier one. Updates from different sensors are independent of each other and should be processed in parallel so the consumers keep up. The company is deciding how its producer application should write each record.

Which solution will meet these requirements?

- **A)** Use the sensor ID as the partition key for all of that sensor's records.
- **B)** Generate a random partition key for every update.
- **C)** Use the event timestamp as a partition key across all sensors.
- **D)** Ask each consumer to globally sort all shards by sequence number.

<details><summary>Answer</summary>

**Answer: A.** A stable sensor key maps that sensor's updates to one shard, where sequence-number order is defined, while other keys can spread across shards. B can place consecutive updates on different shards. C can concentrate unrelated simultaneous events and does not keep one sensor stable. D is impossible because sequence numbers order records only within a shard, not globally across shards.

*Where this is covered: Records, shards and ordering.*

</details>

### 2. Absorbing unpredictable traffic (Associate)

A gaming company is launching an event pipeline whose volume cannot be forecast: traffic sits near zero for hours and then jumps many times over within a minute. Several independent applications must read the same records, and the company must be able to replay those records for a later reprocessing run. The team does not want to plan, monitor or resize shard counts and accepts usage-based pricing in exchange. Its producers already retry with backoff when a sudden burst is throttled.

Which solution will meet these requirements?

- **A)** Provision one shard permanently and disable throttling retries.
- **B)** Use Amazon SQS because Kinesis has no managed capacity mode.
- **C)** Use Kinesis Data Streams on-demand mode with well-distributed partition keys.
- **D)** Use enhanced fan-out as the write-capacity mode.

<details><summary>Answer</summary>

**Answer: C.** On-demand manages stream capacity for variable traffic, while distributed keys and retries handle per-partition pressure and fast jumps. A has no basis in the unknown peak and retries are still required. B discards the replaying multi-consumer stream requirement merely to avoid shard planning. D is a consumer read method, not a producer capacity mode.

*Where this is covered: Capacity modes, scaling and retention.*

</details>

### 3. Isolating consumer throughput (Associate)

A payments company has three separate applications that all read the same Kinesis data stream. Each application must see new records with low propagation delay, and each must have its own read throughput on every shard. One of the three slows down periodically while it writes to a downstream database, and that application must not be able to consume read capacity the other two depend on. The stream already has enough shards for the write volume.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Give all applications one KCL application name and one shared checkpoint.
- **B)** Register each application as an enhanced-fan-out consumer.
- **C)** Keep all three applications on standard consumers and raise their `GetRecords` polling frequency.
- **D)** Replace each partition key with a constant.
- **E)** Consume with `SubscribeToShard` so each registered consumer receives dedicated per-shard throughput.

<details><summary>Answer</summary>

**Answer: B and E.** Registering distinct enhanced consumers and using `SubscribeToShard` gives each dedicated per-shard read throughput and push delivery. A makes the workers cooperate as one logical application rather than three independent consumers. C leaves the three applications contending for the same 2 MiB per second of shared read capacity, and polling harder makes the contention and the throttling worse rather than better. D creates a hot shard and does not isolate consumers.

*Where this is covered: Producers, consumers and delivery guarantees.*

</details>

### 4. Creating query-efficient S3 files (Associate)

An advertising company receives a continuous feed of JSON click events and wants them buffered and written to Amazon S3 as large, query-efficient objects. Each record must pass through an AWS Lambda function that enriches it before delivery, and the JSON must be converted to Parquet using a schema held in the AWS Glue Data Catalog. The company does not need the delivery layer itself to retain records for consumers to replay.

Which solution will meet these requirements?

- **A)** Amazon EventBridge
- **B)** Amazon Kinesis Video Streams
- **C)** Amazon SQS
- **D)** Amazon Data Firehose

<details><summary>Answer</summary>

**Answer: D.** Data Firehose provides managed buffering, Lambda transformation, Glue-schema format conversion and S3 delivery. A routes discrete matching events rather than building partitioned Parquet delivery batches. B ingests time-encoded media. C is a work queue and does not natively perform the requested format-conversion delivery pipeline.

*Where this is covered: Deliver with Amazon Data Firehose.*

</details>

### 5. Computing stateful event-time windows (Associate)

A ride-hailing company must combine two continuous streams, one of driver location updates and one of ride requests, and emit a match result for each window based on the time an event actually occurred rather than the time it arrived. The application has to keep per-key state across those windows. After a failure it must restore that state from a checkpoint rather than reprocessing days of history. The company wants a managed runtime that handles the checkpointing and recovery for it.

Which solution will meet these requirements?

- **A)** Amazon Data Firehose dynamic partitioning
- **B)** Amazon Managed Service for Apache Flink
- **C)** Amazon S3 event notifications
- **D)** Amazon CodeBuild batch builds

<details><summary>Answer</summary>

**Answer: B.** Managed Service for Apache Flink runs stateful streaming operators, windows and joins with managed checkpoints and recovery. A determines S3 delivery prefixes but is not a general stateful compute engine. C emits storage events and maintains no window state. D is disposable build compute rather than a long-running stream processor.

*Where this is covered: Process state with Managed Service for Apache Flink.*

</details>

### 6. Ingesting time-indexed camera media (Associate)

A manufacturer is installing cameras above 40 assembly lines and must ingest their live video into AWS. The footage has to be retained and indexed by timestamp so an engineer can play back the minutes around a reported defect. The same footage must also be readable by a computer-vision application that inspects individual frames. The company does not want to build its own media fragmentation, timestamp indexing, retention or playback layer.

Which solution will meet these requirements?

- **A)** Amazon Kinesis Video Streams
- **B)** Amazon Kinesis Data Streams with one JSON record per video
- **C)** Amazon Data Firehose with a Redshift destination
- **D)** Amazon EventBridge archive

<details><summary>Answer</summary>

**Answer: A.** Kinesis Video Streams is designed for time-encoded video, audio and related media with producer and consumer tooling. B would require the company to build its own media fragmentation, timestamp, retention and playback layer over a business-record stream. C is a buffered analytics delivery path, not media playback ingestion. D archives routed application events and provides none of the required media stream behavior.

*Where this is covered: Video streams and service selection.*

</details>

### 7. Correcting a hot-shard design (Professional)

A SaaS provider ingests device events from many tenants into a provisioned Kinesis data stream with 40 shards. Writes are throttled during business hours even though aggregate capacity looks sufficient, because about half of all events come from one large tenant and the producer uses the tenant ID as the partition key. Those events land on a single shard while the other shards stay lightly used. The application requires ordering only within each individual device belonging to a tenant, not across the whole tenant. The team must remove the throttling at its source rather than mask it, and wants to confirm the key distribution before it pays for more capacity.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Merge the lightly used shards to reduce aggregate capacity.
- **B)** Increase retention from one day to one year.
- **C)** Change the partition key to include the device ID so the tenant's traffic can spread while each device remains ordered.
- **D)** Add more polling consumers without changing the producer key.
- **E)** Measure key distribution and split overloaded hash ranges or add capacity after correcting the key design.

<details><summary>Answer</summary>

**Answer: C and E.** C aligns the ordering boundary with the real device requirement and increases key cardinality, while E verifies distribution and adds capacity where it can be used. A removes capacity and worsens the imbalance. B changes replay duration, not write placement. D changes reads and cannot remove producer throttling on the hot shard.

*Where this is covered: Professional depth.*

</details>

### 8. Designing a multi-consumer analytics path (Professional)

A logistics platform is designing one ingestion path for its structured shipment events. Two independent applications must each receive every event with low latency and must each track their own position in the data. A third workload joins those events with a second stream over five-minute windows and needs keyed state that survives a restart. The same events must also land in Amazon S3 as hourly Parquet objects for the finance team to query. Because delivery is at least once, a record can arrive twice, and every consumer must be able to recognize a duplicate and discard it.

Which combination of steps will meet these requirements? (Select THREE.)

- **A)** Kinesis Data Streams with stable business partition keys and application event IDs
- **B)** One SQS standard queue shared by all consumers so each receives every message
- **C)** Kinesis Video Streams for the JSON business events
- **D)** Managed Service for Apache Flink for the stateful joins
- **E)** Data Firehose for buffered Parquet delivery to S3

<details><summary>Answer</summary>

**Answer: A, D and E.** A supplies ordered replay and IDs for idempotency, D supplies stateful windows and joins, and E supplies managed Parquet delivery. B distributes each queue message among competing workers rather than giving every application an independent copy. C is optimized for time-encoded media, not this structured business-event pipeline.

*Where this is covered: Worked scenario.*

</details>

## Summary

Use Kinesis Data Streams when several applications need an ordered, replayable event log. A partition key maps related records to one shard, so it defines both ordering and load distribution. Provisioned mode gives direct shard control; on-demand manages capacity but still needs distributed keys and producer retries. Standard consumers share read throughput, enhanced fan-out gives registered consumers dedicated throughput, KCL coordinates custom workers, and Lambda event source mappings provide managed polling. Data Firehose is the delivery answer for buffered transformation, format conversion and destinations such as S3, Redshift and OpenSearch. Managed Service for Apache Flink performs stateful windows, joins and event-time computation; the old Kinesis Data Analytics SQL application service is gone. Kinesis Video Streams handles time-indexed media. Design consumers for retry and duplicates, monitor iterator age and throttling, protect streams with IAM and encryption, and calculate cost across retention, retrieval, processing and destination storage rather than ingestion alone.

## Related units

- [Amazon SQS](../06-integration/sqs.md): competing-consumer work queues and visibility timeouts
- [Amazon EventBridge](../06-integration/eventbridge.md): event routing, filtering, archives and replay
- [Amazon MSK](msk.md): Kafka compatibility, brokers, replication and connector ecosystems
- [AWS Lambda](../02-compute/lambda.md): event source mappings, concurrency and failure handling
- [AWS Glue](glue.md): Data Catalog schemas, streaming ETL and format conversion
- [Amazon S3](../01-storage/s3.md): durable stream archives, partitions and lifecycle
- [Amazon OpenSearch Service](opensearch.md): search and analytics destinations for streaming data

## Sources

- [What is Amazon Kinesis Data Streams?](https://docs.aws.amazon.com/streams/latest/dev/introduction.html): stream, shard, producer and consumer model
- [Kinesis Data Streams terminology](https://docs.aws.amazon.com/streams/latest/dev/key-concepts.html): records, partition keys and sequence numbers
- [Kinesis Data Streams quotas](https://docs.aws.amazon.com/streams/latest/dev/service-sizes-and-limits.html): record, request, shard and consumer limits
- [Choose a stream capacity mode](https://docs.aws.amazon.com/streams/latest/dev/how-do-i-size-a-stream.html): provisioned, on-demand Standard and on-demand Advantage behavior
- [Change data retention](https://docs.aws.amazon.com/streams/latest/dev/kinesis-extended-retention.html): 24-hour default and 365-day maximum
- [Reshard a stream](https://docs.aws.amazon.com/streams/latest/dev/kinesis-using-sdk-java-resharding.html): shard splitting, merging and child processing
- [Write data to a stream](https://docs.aws.amazon.com/streams/latest/dev/developing-producers-with-sdk.html): `PutRecord`, `PutRecords` and retry behavior
- [Kinesis Producer Library](https://docs.aws.amazon.com/streams/latest/dev/developing-producers-with-kpl.html): aggregation, batching and producer efficiency
- [Enhanced fan-out consumers](https://docs.aws.amazon.com/streams/latest/dev/enhanced-consumers.html): registered consumers and dedicated throughput
- [Kinesis Client Library concepts](https://docs.aws.amazon.com/streams/latest/dev/kcl-concepts.html): leases, checkpoints, workers and resharding
- [Lambda with Kinesis Data Streams](https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html): managed polling, order, batching and failure controls
- [Monitor Kinesis Data Streams](https://docs.aws.amazon.com/streams/latest/dev/monitoring-with-cloudwatch.html): throughput and iterator-age metrics
- [Data protection in Kinesis Data Streams](https://docs.aws.amazon.com/streams/latest/dev/server-side-encryption.html): KMS encryption and producer or consumer access
- [What is Amazon Data Firehose?](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html): current name, sources, processing and delivery
- [Data Firehose destinations](https://docs.aws.amazon.com/firehose/latest/dev/create-destination.html): supported delivery destinations
- [Understand Firehose delivery](https://docs.aws.amazon.com/firehose/latest/dev/basic-deliver.html): buffering, retry and destination behavior
- [Transform Firehose source data](https://docs.aws.amazon.com/firehose/latest/dev/data-transformation.html): Lambda transformation contract and results
- [Convert Firehose record formats](https://docs.aws.amazon.com/firehose/latest/dev/record-format-conversion.html): Glue schema, Parquet and ORC conversion
- [Firehose dynamic partitioning](https://docs.aws.amazon.com/firehose/latest/dev/dynamic-partitioning.html): record-derived S3 prefixes and processing
- [What is Managed Service for Apache Flink?](https://docs.aws.amazon.com/managed-flink/latest/java/what-is.html): languages, APIs, Studio and managed runtime
- [Flink fault tolerance](https://docs.aws.amazon.com/managed-flink/latest/java/how-fault.html): checkpoints, snapshots and recovery
- [Kinesis Data Analytics SQL discontinuation](https://docs.aws.amazon.com/kinesisanalytics/latest/dev/what-is.html): October 2025 creation stop and January 2026 deletion
- [What is Kinesis Video Streams?](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/what-is-kinesis-video.html): time-indexed media ingestion, retention and playback
- [Amazon Kinesis Data Streams pricing](https://aws.amazon.com/kinesis/data-streams/pricing/): capacity-mode, retention and retrieval cost dimensions
- [Amazon Data Firehose pricing](https://aws.amazon.com/firehose/pricing/): ingestion, processing, format conversion and delivery cost dimensions
