# AWS Lambda

**Where it sits on the exams.** **AWS Lambda** is the service that runs your code in response to events without any server for you to provision, patch or scale, billing only for the requests served and the time the code actually runs. It is the reference serverless compute service for SAA-C03 tasks 2.1, 3.2 and 4.2, and for SAP-C02 tasks 2.1, 4.3 and 4.4, and it is the first answer to consider whenever a stem says "least operational overhead" about work that arrives as discrete events. The rule of thumb the exam wants is simple: choose Lambda when the unit of work is an event, finishes inside 15 minutes, holds no state between invocations, and has a duty cycle low or spiky enough that paying for idle capacity would be waste.

## How Lambda runs your code

A Lambda function is a package of code plus a configuration record naming a handler, a runtime, a memory size, a timeout and a permissions role. When an event arrives, Lambda prepares an **execution environment**, a secure and isolated sandbox holding one copy of your runtime and code, and runs the handler inside it. That environment moves through three phases. Init starts any extensions, bootstraps the runtime and runs the static code outside your handler; it is limited to 10 seconds for on-demand functions, after which Lambda retries initialization at the first invocation using the configured function timeout. Invoke runs the handler, bounded by the function timeout. Shutdown gives registered extensions a last moment to clean up: 0 milliseconds with none, 500 for an internal extension and 2,000 when external extensions are registered.

Between invocations Lambda freezes the environment rather than destroying it, and thaws it for the next request to the same function. Objects declared outside the handler, such as a database client or a parsed configuration file, survive into the next invocation, which is why the standard pattern is to open connections in static initialization and reuse them, and the `/tmp` directory survives the freeze as a transient cache. None of that is a durability guarantee: AWS documents that Lambda terminates execution environments every few hours for runtime updates and maintenance, even for functions invoked continuously. Anything that must outlive an invocation belongs in **Amazon S3**, the object storage service, **Amazon DynamoDB**, the managed key-value and document database, or another external store. That is what "stateless workload" means on the exam.

When no warm environment is available, Lambda has to download the code and build a new environment before the handler runs. That preparation is the **cold start**, you are billed for it, and it adds latency to the invocation. AWS documents that cold starts typically occur in under 1 percent of invocations and that their duration varies from under 100 milliseconds to over 1 second, with development and test functions seeing more of them than production ones simply because they are invoked less often. A scenario complaining about occasional slow first requests is describing a cold start, and the two documented remedies, provisioned concurrency and SnapStart, are taught later in this unit.

Memory is the only performance dial, and it is a compound one. You configure memory from 128 MB to 10,240 MB in 1 MB increments, and Lambda allocates CPU power in proportion: at 1,769 MB a function has the equivalent of one vCPU. Doubling memory therefore roughly doubles CPU, which is why a CPU-bound function can get both faster and cheaper when you raise memory, because the duration falls further than the per-millisecond price rises. AWS recommends 128 MB, the default and the floor, only for simple functions that transform and route events. Sizing is a measurement exercise: watch the `Max Memory Used` figure that Lambda writes into the `REPORT` line of every invocation log in **Amazon CloudWatch**, the AWS monitoring, metrics and log service, watch duration, and use either the open source AWS Lambda Power Tuning tool, which runs a function at several memory settings and compares cost against speed, or the memory recommendations that **AWS Compute Optimizer**, the rightsizing service, surfaces directly in the Lambda console for x86_64 functions. Network bandwidth follows memory too: each environment gets 625 Mbps, raisable for functions outside a VPC so that bandwidth scales with memory up to 3,000 Mbps at 10,240 MB.

Two other per-function settings decide questions. The timeout can be set up to 900 seconds, which is 15 minutes, and that ceiling is the hardest boundary in the service: work that can exceed it does not belong in a single invocation. **Ephemeral storage**, the writable `/tmp` directory, is 512 MB by default and configurable to 10,240 MB in 1 MB increments, which is how a function that unzips an archive or buffers a large media file gets scratch space without a file system.

## When Lambda is the right compute platform

Both exam guides ask you to pick among serverless, containers and instances. Work through Lambda's constraints first, because they are disqualifying. Does the work finish inside 15 minutes? Does it tolerate restarting on a fresh environment with nothing in memory? Can the request and response fit in 6 MB, or be streamed? Is the language a managed runtime or something you can package as a container image? If every answer is yes, Lambda is almost always the lowest-overhead option and usually the cheapest short of continuous high utilization.

When an answer is no, the alternatives divide cleanly. **AWS Fargate**, the serverless compute engine for containers, runs long-lived containers with no instance to manage, so it is the answer when the workload is a container image, runs for hours, needs more than 10 GB of memory, or listens on a port. **Amazon Elastic Container Service (Amazon ECS)** and **Amazon Elastic Kubernetes Service (Amazon EKS)**, the AWS container orchestrators, add scheduling and service discovery on top of Fargate or of **Amazon Elastic Compute Cloud (Amazon EC2)**, the service that rents virtual servers; choose EC2 capacity for GPUs, specialized hardware, per-instance licensing or dense bin packing. **AWS Batch**, the managed batch job scheduler, handles queued jobs that run past 15 minutes. EC2 is the answer when the application cannot be modified, needs a specific kernel or driver, or carries a license bound to cores or sockets. On wording: "existing application cannot be refactored" and "runs for several hours" point away from Lambda, and "spiky, unpredictable traffic with long idle periods" points straight at it.

Cost follows the same logic, because the billing shapes differ. Lambda bills for work performed, so it wins on low or spiky duty cycles and costs nothing when idle. EC2 and Fargate bill for capacity held, so they win once utilization is high and steady. A job that runs 20 minutes a day is cheaper on Lambda even at a higher unit rate; a service pinned near full utilization all month is cheaper on committed instance capacity. A **Compute Savings Plan**, the hourly spend commitment AWS documents as applying to EC2 usage regardless of family, size, operating system, tenancy or Region, also applies to Fargate and Lambda, so a mixed estate can be covered by one commitment.

One newer option sits between the two worlds. **AWS Lambda Managed Instances** runs functions on current-generation EC2 instances in your own account through a capacity provider, with AWS still handling provisioning, patching, scaling and routing. Billing follows EC2 pricing plus a 15 percent management fee, so EC2 Savings Plans apply, one environment can serve several invocations at once, and the ceiling for asynchronous and event source mapping invocations rises to 90 minutes on every source except **Amazon MQ**, the managed message broker service, and **Amazon DocumentDB**, the managed document database. AWS positions it for high-volume predictable traffic and default Lambda for bursty traffic that benefits from scaling to zero. Treat 15 minutes as the number the exam wants and Managed Instances as the exception you can name.

Modernization questions on SAP-C02 task 4.4 are the same decision phrased as a migration. A monolith on instances becomes Lambda functions behind an API, a queue and an event bus when the operations are short, independent and event-triggered; it becomes containers on Fargate when they are long-running services listening on ports; and it stays on instances when a dependency pins it there. The strongest Professional answers split the estate rather than converting all of it, because a rewrite only pays back on the components whose traffic is spiky.

## The three invocation models

Everything that triggers a Lambda function does it in one of three ways, and the model decides who retries, where failures land and whether records arrive in batches. Getting this taxonomy right settles a large share of Lambda exam questions, because the wrong model turns a retry question into a guess.

The callers in the table below are worth naming once. **Amazon API Gateway** is the managed front door for REST, HTTP and WebSocket APIs. An **Application Load Balancer** is the Layer 7 member of **Elastic Load Balancing**, the AWS load balancing service, and can send HTTP requests to a function as a target. **Amazon CloudFront** is the content delivery network. **Amazon Simple Notification Service (Amazon SNS)** is the publish and subscribe messaging service, **Amazon EventBridge** is the event bus that routes AWS and application events to targets, and **AWS CloudFormation** is the infrastructure as code service, whose custom resources call functions during a stack operation. **AWS Step Functions** is the workflow orchestrator. On the polling side, **Amazon Simple Queue Service (Amazon SQS)** is the managed message queue, **Amazon Kinesis Data Streams** is the managed real-time streaming service, **Amazon DynamoDB Streams** is the ordered change log of a DynamoDB table, and **Amazon Managed Streaming for Apache Kafka (Amazon MSK)** is the managed Kafka service.

Read the table by the column that the scenario is really asking about: a stem about a lost message is asking about the retry and destination columns, and a stem about throughput is asking about batching.

| Invocation model | Typical callers | What the caller gets back | Retry behavior | Error destinations | Batching |
|---|---|---|---|---|---|
| Synchronous, `RequestResponse` | API Gateway, Application Load Balancer, function URLs, CloudFront edge functions, the AWS Command Line Interface (AWS CLI) and SDKs, Step Functions tasks | The response or the error, within the caller's timeout; 6 MB request and response payload, 200 MB streamed | None from Lambda. The caller decides whether to retry, and API Gateway relays the error to the client | Not supported | None. One event, one invocation |
| Asynchronous, `Event` | S3 event notifications, SNS, EventBridge rules, CloudFormation custom resources, `--invocation-type Event` | An immediate HTTP 202 with no result. Lambda queues the event and a separate process delivers it | Function errors are retried twice by default, one minute after the first attempt and two after the second. Throttles and 500-series errors return to the queue and retry for up to 6 hours, backing off from 1 second to 5 minutes | On-success and on-failure destinations, to a standard SQS queue, standard SNS topic, another function, an EventBridge bus, or an S3 bucket on failure only. A dead-letter queue is the older alternative, standard SQS or SNS only | None. One event, one invocation |
| Event source mapping | SQS, Kinesis Data Streams, DynamoDB Streams, Amazon MSK, self-managed Apache Kafka, Amazon MQ, Amazon DocumentDB | Nothing. A Lambda-managed poller reads the source and invokes the function synchronously | Stream sources retry the whole batch until it succeeds or records expire, blocking the shard, with configurable record age and retry attempts. Queue sources return the batch after the visibility timeout and rely on the queue's redrive policy | On-failure destinations only, and only for Kinesis, DynamoDB Streams and Kafka. SQS uses a dead-letter queue on the queue itself, not on the function | Yes. A batch size and optional batching window, capped at a 6 MB payload |

The synchronous path is the simplest and the least forgiving: Lambda hands the result back, so every failure is the caller's problem, and an integration timeout shorter than the function timeout produces a client error while the function keeps running and keeps billing. The asynchronous path trades the response for durability, which is what makes S3 notifications and SNS subscriptions safe to fan out to functions. Its cost is that the caller never learns the outcome, so an on-failure destination or a dead-letter queue is not optional in production. Destinations are the better of the two, because they accept more target types and the record they write includes the function's response and the reason the event was discarded, while a dead-letter queue carries only the original event body plus a few attributes.

Two async behaviors catch people out. Setting reserved concurrency to zero does not pause an async function politely: Lambda sends new events straight to the dead-letter queue or on-failure destination with no retries, which stops a runaway function but discards work if nothing catches it. And the async queue is eventually consistent, so a function can receive the same event more than once even when it never fails. Idempotency is a requirement, and it applies with more force to event source mappings, which AWS documents as processing each event at least once.

Destinations and error handling are configured on a function, a version or an alias, and the asynchronous retry settings are two knobs: the maximum age of an event in the queue, up to 6 hours, and the retry attempts, between 0 and 2. Lowering both makes a latency-sensitive async workload fail fast into a queue you can inspect rather than retrying stale work.

## Event source mappings for queues and streams

An **event source mapping** is a Lambda resource, not a setting on the source, that polls a queue or stream and invokes your function with batches of records. That matters for permissions: because Lambda does the reading, the function's execution role needs permission to read the source, and no resource policy grants the source permission to push. Lambda invokes the function when one of three conditions is met: the batching window expires, the batch size is reached, or the payload reaches 6 MB, which you cannot change.

Batching windows differ by source. For SQS, Kinesis and DynamoDB the default window is 0 seconds, so Lambda invokes as soon as records are available, and `MaximumBatchingWindowInSeconds` accepts 0 to 300 seconds. For MSK, Kafka, Amazon MQ and DocumentDB the default is 500 milliseconds, adjustable in whole seconds up to 300, and once changed you cannot recover that default without recreating the mapping.

Amazon SQS is the most common source and behaves unlike the streams. Lambda long-polls the queue and invokes the function synchronously with a batch, then deletes those messages when the function succeeds. When it fails, the whole batch becomes visible again after the queue's visibility timeout, which is why AWS tells you to set that timeout to at least six times the function timeout plus any batching window, and why the function timeout must be less than or equal to the visibility timeout or the mapping will not be created. Failed messages go to a dead-letter queue attached to the queue itself through a redrive policy, with a recommended `maxReceiveCount` of at least 5. To avoid reprocessing messages that already succeeded, enable partial batch responses by adding `ReportBatchItemFailures` to the mapping and returning the failed identifiers from the handler. Batch size reaches 10,000 records for a standard queue and 10 for a FIFO queue, and any batch size above 10 needs a batching window of at least 1 second. Scaling is automatic: Lambda starts with five concurrent batches, adds up to 300 more concurrent invocations per minute, and tops out at 1,250 for one mapping. A maximum concurrency setting between 2 and 1,000 caps one queue's share of the function's concurrency.

The two stream sources, Kinesis Data Streams and DynamoDB Streams, share a model built around shards and ordering. Lambda polls each Kinesis shard about once per second and each DynamoDB stream shard about four times per second, one batch at a time per shard, so baseline concurrency equals the number of shards. The `ParallelizationFactor` setting, from 1 to 10, runs that many concurrent batches per shard while preserving order within a partition key for Kinesis and within an item for DynamoDB, which is the documented remedy when `IteratorAge` climbs and adding shards is not an option. Kinesis mappings default to a batch size of 100 with a maximum of 10,000, and read either as a shared-throughput standard iterator or as an enhanced fan-out consumer with a dedicated HTTP/2 connection per shard. Starting position is `TRIM_HORIZON`, `LATEST` or `AT_TIMESTAMP`, and AWS recommends `TRIM_HORIZON` for DynamoDB because mapping creation is eventually consistent and `LATEST` can miss early events.

Stream failure handling decides exam questions. A function error makes Lambda retry the entire batch, and because order must be preserved, the affected shard stops advancing until the error clears or the records expire, so one poison message stalls a partition indefinitely and `IteratorAge` rises. Four settings break the deadlock. `MaximumRetryAttempts` defaults to -1, retry until the record expires, and accepts 0 to 10,000. `MaximumRecordAgeInSeconds` also defaults to -1, never discard on age, and accepts up to 604,800 seconds. `BisectBatchOnFunctionError` splits a failing batch in two and retries each half, isolating the bad record. An on-failure destination, an SQS queue or SNS topic, receives metadata about each discarded batch. Partial batch responses work here too. One more DynamoDB Streams quota: design for no more than two consumers per shard on a single-Region table, and one on a global table, or reads throttle.

Where throughput must be guaranteed rather than best-effort, SQS and the Kafka sources support provisioned mode, which allocates dedicated event pollers instead of letting Lambda autoscale them. It scales faster and to far higher concurrency, is mutually exclusive with the maximum concurrency setting, and costs extra.

## Concurrency, scaling, and start-up latency

Concurrency is the number of in-flight requests a function handles at one instant, and because each concurrent request needs its own execution environment, it is also the number of environments running. The arithmetic AWS gives is `Concurrency = (average requests per second) x (average request duration in seconds)`, so 100 requests per second at 500 milliseconds each is a concurrency of 50, not 100. An account gets 1,000 concurrent executions across all functions in a Region by default, a soft quota raisable into the tens of thousands, and new accounts start lower with automatic increases as usage grows.

Two limits sit on top of that pool. The concurrency scaling rate is 1,000 new execution environments every 10 seconds, per function and per Region, and it does not accrue, so an idle interval banks nothing. Network bandwidth also scales with memory, from 2,048 MB upward, to a ceiling of 3,000 Mbps. Because the rate is per function, one function ramping hard does not slow another. Separately, Lambda enforces a requests per second ceiling of 10 times the corresponding concurrency quota, so a default account tops out at 10,000 requests per second however short the functions are. That is the limit that surprises people running sub-100 millisecond functions: 20 milliseconds at 30,000 requests per second computes to a concurrency of 600, well inside the quota, and still throttles, because clearing the 10x rule needs a quota of 3,000 there.

Read this table by the requirement in the stem. "Must never be starved by other functions" points at the reserved row, "must not overwhelm a downstream database" points at the same row for the opposite reason, and "consistent low latency on the first request" points at the provisioned row.

| Concurrency setting | What it does | Effect on the rest of the account | Cold starts | Throttling behavior | Cost |
|---|---|---|---|---|---|
| Unreserved, the default | The function draws from the shared Regional pool of concurrency that no function has reserved | Competes with every other unreserved function; a runaway function can consume the whole pool | Possible on every scale-up | Throttled with a 429 only when the account pool is exhausted | No extra charge |
| Reserved concurrency | Sets both a floor and a ceiling: that many units are held exclusively for this function and it can never exceed them | Subtracted from the shared pool, so it reduces what other functions can use, and unused reserved units are wasted. Lambda always keeps at least 100 units unreserved, so an account at the default quota can reserve at most 900 | Possible on every scale-up; Lambda still terminates idle environments | Throttled once the function reaches its reserved value, even if the account has spare capacity elsewhere | No extra charge |
| Provisioned concurrency | Pre-initializes and keeps warm a set number of environments on a version or alias | Counts against the account quota like reserved concurrency does | Not incurred while requests fit inside the provisioned count; spillover invocations above it can still cold start | Spills over into unreserved concurrency if no reserved concurrency is set, and throttles at the reserved value if one is | Charged for the concurrency configured and the duration it is held |

Reserved concurrency is double-edged. Being a ceiling as well as a floor, it is the standard answer both for protecting a critical function and for protecting a fragile downstream dependency such as a relational database with a small connection pool, where **Amazon RDS Proxy**, the managed connection pooling service, is the complementary fix. Setting it to zero is the documented emergency stop. Provisioned concurrency is purely a latency tool: Lambda pre-initializes environments, starts allocating after a minute or two, provisions up to 6,000 per minute per function, and makes none usable until the allocation finishes. It attaches to a published version or an alias, never to `$LATEST`, and **Application Auto Scaling**, the service that scales non-EC2 resources, can drive it on a schedule or on utilization so you are not paying for warm capacity overnight.

**Lambda SnapStart** is the cheaper answer to the same problem for the runtimes that support it. Instead of keeping environments warm, Lambda runs the Init phase once when you publish a function version, takes an encrypted Firecracker microVM snapshot of the initialized memory and disk state, caches it, and resumes new environments from that snapshot as the function scales. SnapStart supports Java 11 and later, Python 3.12 and later, and .NET 8 and later, across both zip and container image packaging. Other managed runtimes, including Node.js and Ruby, and the OS-only runtimes are not supported. SnapStart cannot be combined with provisioned concurrency, with **Amazon Elastic File System (Amazon EFS)**, the managed elastic file system, or with ephemeral storage above 512 MB, and like provisioned concurrency it works only on published versions and aliases. For Java managed runtimes there is no additional charge; for the other supported runtimes you pay to cache the snapshot while the version is active, with a three-hour minimum, and a restoration charge each time an environment resumes from it. The trade-off the exam cares about: SnapStart gets startup latency down to as low as sub-second at little or no cost, while provisioned concurrency keeps environments already running and is the answer when the requirement is strict double-digit millisecond start times. One design caution: a single snapshot seeds many environments, so unique identifiers, secrets and random seeds must be generated after initialization, not during it.

## Packaging, layers, versions, and aliases

A function's code arrives one of two ways. A zip archive is limited to 50 MB zipped through the Lambda API, SDKs or console, larger if staged in Amazon S3, and 250 MB unzipped for the whole package including layers and custom runtimes. A container image in **Amazon Elastic Container Registry (Amazon ECR)**, the managed container registry, can reach 10 GB uncompressed, which is the answer whenever a function needs large native dependencies, a machine learning model or a language the managed runtimes do not cover. Managed runtimes cover Node.js, Python, Java, .NET and Ruby on Amazon Linux 2023, all supporting x86_64 and arm64, and Go and Rust ship as executables on the OS-only `provided.al2023` runtime. Runtimes are deprecated when the language version leaves community long-term support, with at least 180 days of notice by email, the **AWS Health Dashboard**, which reports AWS events affecting your account, and a check in **AWS Trusted Advisor**, the account inspection service, after which Lambda blocks creation and then updates.

**Lambda layers** are zip archives of shared dependencies, a custom runtime or configuration data that Lambda extracts into `/opt` in the execution environment. A function can use up to five layers, they count toward the 250 MB unzipped ceiling, and they work only for zip-packaged functions, since a container image carries its own dependencies. Each publish creates an immutable layer version with its own Amazon Resource Name (ARN) and functions reference an exact version, so a layer update is a deliberate redeploy. Layers can be shared with specific accounts, with an organization, or made public, which is how a platform team distributes one library set without every team packaging it. AWS advises against layers for Go and Rust, because loading assemblies at initialization adds to the cold start a single compiled binary avoids.

**Function versions** turn a deployment into something you can roll back. Publishing snapshots the code and most configuration, including runtime, memory, timeout, layers, environment variables, VPC settings, architecture, ephemeral storage and SnapStart, and that snapshot is immutable. The unpublished working copy is `$LATEST`, and any code deployment overwrites it, so a design that never publishes versions has no rollback target. Version numbers increase monotonically and are never reused. A qualified ARN carries the version suffix and an unqualified one invokes `$LATEST`. Operational settings such as reserved concurrency are not versioned.

**Function aliases** are mutable pointers to a version, and they are what callers should reference. An event source mapping, an API Gateway integration or a permission written against an alias keeps working across deployments while the alias moves from version 3 to version 4. An alias can carry a weighted routing configuration across exactly two versions, which is a canary deployment: both versions must be published, neither can be `$LATEST`, and both must share the same execution role and the same dead-letter queue configuration or have none. Lambda records the executed version in the `START` log line and the `x-amz-executed-version` header on synchronous invocations, so you can compare error rates per version. **AWS CodeDeploy**, the deployment service, automates the shift with configurations such as `Linear10PercentEvery2Minutes`, and the **AWS Serverless Application Model (AWS SAM)**, the serverless deployment framework, wires the alias, deployment group and rollback together through `AutoPublishAlias` and `DeploymentPreference`. That combination is the keyed answer whenever a stem asks for gradual rollout of a function with automatic rollback on a CloudWatch alarm.

## Front doors, orchestration, and event integrations

The most common Lambda architecture on the exams is an HTTP front door invoking a function synchronously. [Amazon API Gateway](../04-networking/api-gateway.md) is the general answer, because it adds authorizers, throttling and usage plans, request validation, caching, custom domains, canary stage deployments and WAF integration, and because a proxy integration hands the function the whole request and takes back a structured response. Its integration timeout is far shorter than Lambda's 15 minutes, so work that might run long must be made asynchronous behind the API rather than held open, and API Gateway relays a function error to the caller instead of retrying. An Application Load Balancer is the cheaper alternative when you need only path and host routing and none of the API management features.

A **function URL** is the third option: a dedicated HTTPS endpoint of the form `https://<url-id>.lambda-url.<region>.on.aws` attached to `$LATEST` or to an alias, with an auth type of either `AWS_IAM`, which requires SigV4-signed requests, or `NONE`, which makes the function publicly callable through a resource-based policy. Function URLs support cross-origin resource sharing (CORS), are reachable only over the public internet with no PrivateLink support, and are throttled by reserved concurrency at 10 requests per second per unit reserved. They suit webhooks and single-purpose endpoints, and are the wrong answer when a scenario asks for API keys, request validation, multiple routes or a private endpoint.

**Response streaming** changes the payload economics of the synchronous path. A buffered response caps at 6 MB; a streamed response reaches 200 MB, and the client receives bytes as the function produces them, improving time to first byte. It works through function URLs, the `InvokeWithResponseStream` API, and the API Gateway proxy integration, which calls that same API. Bandwidth is uncapped for the first 6 MB and then capped at 2 MBps. Lambda supports it natively on the Node.js managed runtimes; other languages need a custom runtime integration. Two cautions: function URLs do not stream from inside a VPC, where you invoke through an interface endpoint instead, and a broken client connection does not stop the function, so you are billed for the full duration.

For work that spans several steps, [AWS Step Functions](../06-integration/step-functions.md) is the orchestrator and the standard answer for anything that outgrows one function. A workflow that calls a sequence of short functions, waits for a human approval with a task token, retries individual steps with backoff and branches on results replaces both the 15 minute limit and a pile of hand-written retry logic. Express workflows suit high-volume short-lived orchestration and Standard workflows suit long-running durable ones. Chaining functions by having one invoke the next is a design smell; a state machine is the managed alternative.

For decoupling, [Amazon SQS](../06-integration/sqs.md) and [Amazon EventBridge](../06-integration/eventbridge.md) do different jobs in front of a function. A queue absorbs a burst and lets the consumer set its own pace, which is what you want when the downstream system is rate-limited, and it gives you a dead-letter queue and a redrive path for poison messages. An event bus routes by content: rules with event patterns pick out the events a function should see, input transformers reshape them, and one event can fan out to several targets in several accounts. EventBridge invokes Lambda asynchronously, so Lambda's own retry and destination settings apply on top of the bus's delivery retries. Amazon SNS is the third pattern, publish and subscribe with message filtering, also invoking asynchronously. Amazon S3 event notifications and EventBridge both deliver object-created events, the canonical file-ingest design. A function that writes back into the bucket that triggers it creates a loop; Lambda's recursive loop detection stops a chain after roughly 16 invocations, but the fix is a separate prefix or bucket, not the safety net.

## VPC networking, IAM, and encryption

By default a Lambda function runs inside a VPC that Lambda owns and manages, invisible to you, with outbound access to the public internet. Attaching it to your own **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network you control, is what lets it reach private resources such as an **Amazon Relational Database Service (Amazon RDS)** instance, and the trade is absolute: once attached, the function reaches only what that VPC can reach. It loses internet access unless the subnets route through a NAT gateway, and a public subnet does not help, because a function never gets a public IP address. Private access to AWS service APIs goes through interface or gateway VPC endpoints, which also keeps that traffic off the internet for compliance.

The networking model behind this changed in a way that removed the old objection to VPC-attached functions: Lambda no longer creates one elastic network interface per concurrent execution environment. It creates **Hyperplane elastic network interfaces**, managed interfaces shared by every function in the account that uses the same combination of subnets and security groups. The first function to use a combination pays for the interface creation, during which it sits in the `Pending` state and cannot be invoked, which AWS documents as taking several minutes. After that, other functions with the same combination reuse it, each interface supports up to 65,000 connections, and Lambda adds more interfaces automatically as traffic and concurrency require. Interfaces are not permanent: Lambda may recreate them for load balancing or health, a function idle for 14 days has its unused interfaces reclaimed and goes `Inactive` until the next invocation, and removing a VPC configuration can take up to 20 minutes to clean up. So standardize on a small number of subnet and security group combinations rather than a unique one per function, keep the execution role's interface permissions in place until cleanup finishes, and count against the default quota of 500 network interfaces per VPC, which Lambda shares with services such as Amazon EFS.

Permissions come in two halves and the exam tests the distinction. The **execution role** is an **AWS Identity and Access Management (IAM)** role that Lambda assumes when it invokes the function, so it governs what the code can do: its trust policy must name the `lambda.amazonaws.com` service principal, and the `AWSLambdaBasicExecutionRole` managed policy grants only the CloudWatch Logs permissions every function needs. Reading an event source, writing to a destination, decrypting with a customer managed key and creating network interfaces are additional grants on this role. The other half is the function's resource-based policy, capped at 20 KB, which says who may invoke the function: an S3 bucket, an SNS topic, an EventBridge rule or another account, and it is also how a function URL with auth type `NONE` is made public. Attaching a VPC configuration grants the code EC2 network interface permissions implicitly, so AWS recommends a deny statement scoped with the `lambda:SourceFunctionArn` condition key. The `lambda:VpcIds`, `lambda:SubnetIds` and `lambda:SecurityGroupIds` condition keys let an organization require VPC attachment or restrict which networks a function may join.

Environment variables are encrypted at rest with **AWS Key Management Service (AWS KMS)**, the managed key service, using an AWS managed key by default and a customer managed key when you need key policy control or an audit trail, and they cap at 4 KB in aggregate. Zip deployment packages can also be encrypted with a customer managed key. Secrets do not belong in environment variables at all: read them at initialization from a secrets store through the execution role. Code signing requires that a package was signed by a trusted publisher before Lambda will deploy it, which is how a Professional answer enforces artifact integrity across an organization.

## Lambda@Edge compared with CloudFront Functions

CloudFront can run your code at its edge in two different ways, and picking the wrong one is a common exam trap. **CloudFront Functions** is a native CloudFront feature that runs small JavaScript functions with submillisecond duration, scales to millions of requests per second, and executes only on viewer request and viewer response events. It gives 2 MB of memory and 10 KB for code and libraries, has no network access, no file system access and no access to the request body, but does see geolocation and device data, and you can build and test it entirely inside CloudFront. Its jobs are cache key normalization, header manipulation, URL rewrites and redirects, and validating a signed token such as a JSON web token (JWT).

**Lambda@Edge** is Lambda itself, replicated to CloudFront's infrastructure. It runs Node.js or Python, executes on all four CloudFront events including origin request and origin response, and scales to about 10,000 requests per second per Region. Viewer-facing triggers allow up to 128 MB of memory and origin-facing triggers up to 10,240 MB, with 50 MB of code and libraries either way and up to 30 seconds of execution. It has network access, file system access and access to the request body, which is exactly why you reach for it.

The restrictions get tested. The function must be created in the US East (N. Virginia) Region and associated by a numbered version, never `$LATEST` and never an alias, and its execution role must trust both `lambda.amazonaws.com` and `edgelambda.amazonaws.com`. Lambda@Edge does not support VPC access, environment variables other than the reserved ones, layers, dead-letter queues, tracing, provisioned concurrency, container images, the arm64 architecture, or ephemeral storage above 512 MB. Logs land in the CloudWatch Region nearest the edge location that ran it, not in your home Region. The decision rule: if the work is a header, a cookie, a cache key or a URL and must be as cheap and fast as possible, use CloudFront Functions; if it needs a network call, a library, the request body or an origin-side trigger, use Lambda@Edge.

## Monitoring, pricing, and the quotas that matter

Every function writes to CloudWatch Logs through its execution role, and each `REPORT` line carries duration, billed duration, memory size and maximum memory used, the cheapest rightsizing signal you have. The metrics worth alarming on are `Errors` and `Throttles`, since throttling means a concurrency or requests-per-second ceiling rather than a code defect; `Duration` at the p95 or p99 statistic so cold starts do not hide in an average; `ConcurrentExecutions` and `ClaimedAccountConcurrency` against the Regional quota; `IteratorAge` for Kinesis and DynamoDB mappings, the early warning that a shard is stalled behind a failing batch; `AsyncEventAge` and `AsyncEventsDropped` for the asynchronous queue; and `DeadLetterErrors` and `DestinationDeliveryFailures`, which mean the safety net is itself failing. **AWS X-Ray**, the distributed tracing service, stitches a request together across API Gateway, the function and its downstream calls, and is the answer when a stem asks where latency is being spent.

Pricing has two dimensions for a standard function: requests served, and duration measured in GB-seconds at 1 millisecond granularity, which is why memory and speed are the same lever. There is still a free tier: one million requests and 400,000 GB-seconds per month. Provisioned concurrency charges for the concurrency configured and how long you keep it, at a lower duration rate for invocations that land on it. SnapStart is free on Java managed runtimes and otherwise charges for snapshot caching, with a three-hour minimum, plus a restoration charge per environment resumed. Ephemeral storage above 512 MB, streamed response bytes beyond the first 6 MB, and provisioned mode on event source mappings each carry their own charges, and Lambda@Edge is priced separately per million requests plus compute. Data transfer, the downstream service calls the function makes, and CloudWatch Logs ingestion are usually the quiet majority of a serverless bill, so cost reviews should look past the Lambda line item. The levers, in order: right-size memory, cut duration by moving initialization outside the handler and trimming dependencies, move to arm64 where the runtime allows, batch harder on event source mappings, reduce log volume, and cover a steady baseline with a Compute Savings Plan.

The quotas that decide designs are worth memorizing as a set: memory 128 MB to 10,240 MB; timeout 900 seconds; ephemeral storage 512 MB to 10,240 MB; five layers; 4 KB of environment variables; a 20 KB resource-based policy; a 6 MB synchronous payload each way, 1 MB asynchronous and 200 MB streamed; zip packages of 50 MB zipped and 250 MB unzipped including layers, against 10 GB for a container image; 1,000 concurrent executions per account per Region; 1,000 new environments per 10 seconds per function; and 500 network interfaces per VPC. The concurrency and storage numbers are soft; the timeout, payload sizes and unzipped package size are not.

## Professional depth

Concurrency is an account-level and Region-level resource, and that fact reshapes serverless designs at organization scale. Every function in an account competes for the same 1,000 units by default, so a batch job that scales to 900 environments can throttle the customer-facing API beside it. Professional questions usually want two remedies together: separate accounts per workload or environment through **AWS Organizations**, the multi-account governance service, so blast radius is an account boundary; reserved concurrency as a ceiling on noisy jobs and a floor under critical ones, remembering the 100 units Lambda always holds back; and an increase requested through **Service Quotas**, the console for viewing and raising limits, ahead of a launch, sized for the ten-times-concurrency requests-per-second rule rather than for concurrency alone.

Cross-account patterns run through the two permission halves. To let another account invoke a function, add a statement to its resource-based policy naming that principal, preferably on an alias so the caller is insulated from version churn. To read a queue in another account the grant goes the other way: the execution role needs the SQS permissions and the queue's access policy must allow that role. Layers and container base images are the shared-artifact path, published once in a platform account and shared with the organization, with code signing enforcing that only signed artifacts deploy. Functions do not span Regions, so a multi-Region design deploys the same template into each Region and leaves replication to the data layer.

The quotas that bite at scale are rarely the concurrency limit. Network interfaces cap at 500 per VPC and are shared with Amazon EFS and other services, so a large estate of VPC-attached functions with many distinct subnet and security group combinations exhausts them long before it exhausts concurrency; consolidating those combinations is the fix. The Lambda control plane allows only 15 requests per second across all management APIs, which makes a mass redeployment across hundreds of functions throttle-prone. An SQS event source mapping tops out at 1,250 concurrent invocations regardless of an increased account quota. And a provisioned concurrency pre-warm has to start minutes early, because none of the allocation is usable until all of it completes.

Failure modes at scale are about backpressure rather than the function. A poison record stalls a Kinesis or DynamoDB shard indefinitely because ordering must be preserved, and the symptom is a climbing `IteratorAge` with no error spike; bisect-on-error, a maximum record age and an on-failure destination turn that outage into a quarantined record. A function scaling to hundreds of environments in front of a relational database exhausts its connection pool, and the answer is reserved concurrency plus RDS Proxy, not a larger database. Asynchronous backlogs are invisible in `Duration` and show only in `AsyncEventAge`, and an event that ages past six hours is gone unless a destination catches it.

A Professional question extends the Associate version by adding a constraint that breaks the obvious answer. The Associate scenario says a function is slow on first invocation and the answer is provisioned concurrency; the Professional version adds that the workload is Java, runs in 30 Regions and has a fixed budget, so the answer becomes SnapStart on published versions, free on Java managed runtimes, with provisioned concurrency kept for the one endpoint whose latency is contractual. Or the Associate scenario says messages are being lost and the answer is a dead-letter queue; the Professional version adds that the source is SQS, making the answer a redrive policy on the queue itself, because a Lambda dead-letter queue catches only asynchronous invocations.

## Worked scenario

A media company ingests customer video uploads and must publish a transcoded preview, a thumbnail set and a search index entry within minutes. Uploads arrive in an S3 bucket at an unpredictable rate, from a handful an hour overnight to several thousand when a partner syncs a catalog. Transcoding can take up to 40 minutes. A customer-facing API returns job status and must answer in under 200 milliseconds at the 99th percentile, and the platform team owns a shared library that every function must use.

Object creation in S3 sends an event to EventBridge, and a rule starts a Step Functions Standard workflow. The workflow, not a function, owns the long path: a Lambda function validates and fingerprints the file, a container job does the transcode because 40 minutes exceeds the 15 minute limit, and short functions generate thumbnails and write the index entry. Failures retry inside the state machine with backoff, and a failed execution lands in an SQS queue an operator can inspect. The thumbnail function is memory-bound, so tuning sets its memory where the shorter duration more than pays for the larger allocation, and its ephemeral storage is raised above 512 MB to hold frames on `/tmp`.

The status API runs on API Gateway with a proxy integration behind an alias. The function is Java, so SnapStart is enabled on each published version, cutting startup latency without the standing cost of provisioned concurrency; the one endpoint with a contractual latency target carries a small provisioned concurrency allocation on a separate function, because the two features cannot coexist on one version. That function reads DynamoDB, so there is no connection pool to exhaust and no reason to attach it to a VPC. The ingest functions do attach to a VPC to reach a private metadata store, all sharing one subnet and security group combination so they share Hyperplane network interfaces. Reserved concurrency caps them at a value the metadata store can absorb and reserves a floor for the status function so a catalog sync cannot starve the API. Deployments publish a version, shift traffic on the alias with CodeDeploy at 10 percent every two minutes, and roll back on a CloudWatch alarm. The shared library is a layer published in the platform account and shared with the organization.

When the exam asks about this scenario, the keyed answer is the split: Step Functions for the orchestration that outgrows a function, a container job for the 40 minute transcode, short Lambda functions for the event-shaped steps, SnapStart for Java cold starts at no extra cost, and reserved concurrency as the guardrail that keeps a burst of uploads from taking the API down with it.

## Exam lens

- "Run code in response to events with the least operational overhead" maps to Lambda; an EC2 Auto Scaling group is the distractor that reintroduces patching and idle capacity.
- "The job takes about 30 minutes" rules Lambda out at the 15 minute timeout and maps to AWS Batch, Fargate or a Step Functions workflow.
- "Reduce the latency of the first request after a quiet period" maps to provisioned concurrency, or to SnapStart when the runtime is Java 11 or later, Python 3.12 or later, or .NET 8 or later.
- "A function must never be starved by other functions in the account" maps to reserved concurrency, which is a floor as well as a ceiling.
- "Protect a relational database from function scaling" maps to reserved concurrency plus RDS Proxy; raising the account quota is the distractor that makes it worse.
- "Messages must not be lost when the function fails" maps to a dead-letter queue or on-failure destination for asynchronous invocation, and to the source queue's redrive policy when the source is SQS.
- "One bad record has stopped stream processing and IteratorAge is climbing" maps to bisect batch on function error, a maximum record age or retry attempts, and an on-failure destination.
- "Messages are redelivered while still being processed" maps to setting the queue's visibility timeout to at least six times the function timeout.
- "More Kinesis throughput without adding shards" maps to raising the parallelization factor, up to 10 concurrent batches per shard.
- "The function must reach a private database and also call a public API" maps to VPC attachment plus a NAT gateway; a public subnet is the distractor, because a function never gets a public IP address.
- "Manipulate headers or rewrite a URL at the edge as cheaply as possible" maps to CloudFront Functions; Lambda@Edge is the distractor unless network access, the request body or an origin trigger is required.
- "Shift traffic gradually to a new function version and roll back automatically" maps to a weighted alias driven by CodeDeploy.
- "Return a response larger than 6 MB or improve time to first byte" maps to response streaming through a function URL or the `InvokeWithResponseStream` API.
- "A public HTTPS endpoint for a webhook, no API management needed" maps to a function URL; API Gateway is the distractor when the stem mentions API keys, usage plans or request validation.
- "Sub-100 millisecond function throttles well below 1,000 concurrency" maps to the synchronous requests-per-second ceiling of ten times the concurrency quota; asynchronous invocation is bounded by concurrency alone.

## Knowledge check

### 1. Nightly report generation (Associate)

A company generates a set of PDF reports once a night. The job reads about 2 GB from Amazon S3, takes roughly 45 minutes of processing on a single machine, and runs on a schedule with no traffic in between. The company wants to stop paying for an always-on server and wants the least operational overhead.

Which solution will meet these requirements?

- **A)** Run the job in a single AWS Lambda function invoked on a schedule, with memory set to 10,240 MB.
- **B)** Run the job on an Amazon EC2 instance started and stopped by a scheduled Lambda function.
- **C)** Run the job as an AWS Batch job on Fargate, submitted on a schedule.
- **D)** Split the job into 10 Lambda functions that each invoke the next one.

<details><summary>Answer</summary>

**Answer: C.** The job runs for about 45 minutes, which exceeds Lambda's 900 second maximum timeout, so a function cannot complete it regardless of memory. AWS Batch on Fargate runs the containerized job on managed capacity with no instance to patch and nothing running between executions. A breaks the 15 minute timeout. B works but reintroduces the operating system patching and instance lifecycle the company is trying to shed. D is a chain of function invocations that still has to move state between functions, has no orchestration, retry or rollback, and is the design smell a state machine exists to replace.

*Where this is covered: When Lambda is the right compute platform.*

</details>

### 2. Sizing a CPU-bound function (Associate)

A Lambda function resizes images and currently runs at the 128 MB default. Duration averages 8 seconds, the `REPORT` line shows maximum memory used around 90 MB, and the team wants faster responses without increasing cost significantly.

Which solution will meet these requirements?

- **A)** Leave memory at 128 MB and enable provisioned concurrency.
- **B)** Increase the memory setting and measure the resulting duration and cost at several values.
- **C)** Increase the function timeout so the function has more time to complete.
- **D)** Attach an Amazon EFS file system so the function has more working space.

<details><summary>Answer</summary>

**Answer: B.** Lambda allocates CPU in proportion to memory, reaching one vCPU at 1,769 MB, so raising memory on a CPU-bound function shortens duration and can lower total cost, because billing is memory multiplied by duration. Measuring at several settings is exactly what the Power Tuning tool and Compute Optimizer recommendations are for. A addresses cold start latency, not the 8 second steady-state duration. C changes only the point at which Lambda gives up; it makes nothing faster. D adds shared file storage, which the function does not need, and does not add CPU.

*Where this is covered: How Lambda runs your code.*

</details>

### 3. Losing events from an Amazon S3 trigger (Associate)

An Amazon S3 bucket invokes a Lambda function when objects are created. During a recent downstream outage the function failed for two hours, and the team discovered afterward that some object events had been processed and others had disappeared with no record of them. The team needs every failed event preserved with enough detail to diagnose the failure, without changing how S3 triggers the function.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Configure an on-failure destination on the function that points to an Amazon SQS standard queue.
- **B)** Increase the function timeout to 15 minutes.
- **C)** Set the maximum age of event and the retry attempts on the function's asynchronous invocation configuration to values that fit the operations process.
- **D)** Create an Amazon SQS FIFO queue and configure it as the function's dead-letter queue.
- **E)** Enable provisioned concurrency on the function.

<details><summary>Answer</summary>

**Answer: A and C.** S3 invokes Lambda asynchronously, so Lambda queues the event, retries a function error twice, and then discards it unless somewhere is configured to catch it. An on-failure destination captures the request, the function's response and the reason the event was discarded, which is what "enough detail to diagnose" requires. Tuning the maximum event age, up to six hours, and the retry attempts, between 0 and 2, controls how long Lambda keeps trying before handing the event to that destination. B does not help, because the failure was a downstream outage rather than a timeout. D is not possible: Lambda dead-letter queues accept only standard SQS queues and standard SNS topics, and a dead-letter queue carries only the event body, not the response. E reduces cold start latency and has no effect on failed events.

*Where this is covered: The three invocation models.*

</details>

### 4. Duplicate processing from a queue (Associate)

A Lambda function processes orders from an Amazon SQS standard queue with a batch size of 10. Occasionally one message in a batch fails validation, and the team sees the other nine orders processed a second time. The function's timeout is 60 seconds and the queue's visibility timeout is 60 seconds, and operators also report messages being delivered again while a batch is still running.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Configure a dead-letter queue on the Lambda function.
- **B)** Enable partial batch responses by adding `ReportBatchItemFailures` to the event source mapping and returning the failed message identifiers.
- **C)** Reduce the batch size to 1.
- **D)** Increase the queue's visibility timeout to at least six times the function timeout.
- **E)** Enable provisioned concurrency on the function.

<details><summary>Answer</summary>

**Answer: B and D.** Without partial batch responses, one failure returns the whole batch to the queue, so the nine successful orders are redelivered; reporting only the failed identifiers leaves the rest deleted. A visibility timeout equal to the function timeout leaves no margin for retries after a throttle, which is why AWS documents at least six times the function timeout, plus any batching window. A does not apply, because a Lambda dead-letter queue catches asynchronous invocations only; an SQS source needs a redrive policy on the queue itself. C would stop the duplicate processing but multiplies invocations and cost and does nothing about the redelivery during processing. E affects cold starts, not batch failure semantics.

*Where this is covered: Event source mappings for queues and streams.*

</details>

### 5. A stalled stream across two Regions (Professional)

A payments company processes an Amazon Kinesis data stream of 60 shards in each of two Regions, fed by producers in several accounts. After a partner began sending a new message format, the consuming Lambda function throws on those records and processing on the affected shards stops advancing. The `IteratorAge` metric climbs steadily while the error rate stays flat and downstream settlement falls behind. The company must restore processing without pausing the producers, must keep ordering per partition key, and must retain the rejected records for a compliance review.

Which solution will meet these requirements?

- **A)** Increase the batch size on the event source mapping.
- **B)** Increase the number of shards in the stream.
- **C)** Switch the event source mapping to an enhanced fan-out consumer.
- **D)** Set a maximum retry attempts value, enable bisect batch on function error, and configure an on-failure destination.

<details><summary>Answer</summary>

**Answer: D.** Stream event source mappings retry the whole batch and block the shard to preserve order, so a poison record stalls that partition until the records expire. Capping retry attempts lets the batch be discarded, bisecting on function error isolates the single bad record so the good records in the batch still process, and the on-failure destination retains metadata for every discarded batch, which is what the compliance review needs. All three preserve per-partition-key ordering and none of them touch the producers. A sends more records per invocation and makes the stalled batch larger. B adds shards, but the existing shards holding the bad records still stall. C changes the read path to a dedicated HTTP/2 connection for lower latency and has no effect on failure handling.

*Where this is covered: Event source mappings for queues and streams.*

</details>

### 6. Cold starts on a large Java estate (Professional)

A financial services company runs 400 Java Lambda functions behind API Gateway across 12 Regions. Users report slow responses on the first request after quiet periods. Finance has refused an increase to the serverless budget. One checkout endpoint has a contractual 100 millisecond response requirement at the 99th percentile.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Enable SnapStart on published versions of the other 399 Java functions, and configure provisioned concurrency on the checkout function alone.
- **B)** Configure provisioned concurrency on all 400 functions in all 12 Regions.
- **C)** Increase the memory setting on all 400 functions to 10,240 MB.
- **D)** Enable SnapStart on all 400 functions including the checkout function, and set its memory to the maximum.

<details><summary>Answer</summary>

**Answer: A.** AWS documents no additional charge for SnapStart on Java managed runtimes, so it removes most of the initialization latency across the rest of the estate for free, while the one endpoint whose latency is contractual gets provisioned concurrency instead, the two being mutually exclusive on a single version, because it keeps environments already running and answers in double-digit milliseconds. B meets the latency goal and blows the budget across 4,800 function-Region combinations. C raises cost on every invocation without addressing initialization, which is the part of a cold start that dominates for Java. D fails the contractual requirement in the only place it matters, because SnapStart targets sub-second rather than double-digit millisecond starts, and SnapStart and provisioned concurrency cannot both be enabled on the same version anyway.

*Where this is covered: Concurrency, scaling, and start-up latency.*

</details>

### 7. Protecting a database from a burst (Associate)

A Lambda function writes to an Amazon RDS for PostgreSQL database. During traffic spikes the function scales to hundreds of concurrent environments and the database runs out of connections, which also affects an unrelated reporting application on the same instance. The company needs the function to keep working at a rate the database can absorb.

Which solution will meet these requirements?

- **A)** Request an increase to the account concurrency quota.
- **B)** Enable provisioned concurrency on the function.
- **C)** Configure reserved concurrency on the function at a level the database can sustain, and route the function's connections through Amazon RDS Proxy.
- **D)** Move the function into the same VPC subnet as the database.

<details><summary>Answer</summary>

**Answer: C.** Reserved concurrency is a ceiling as well as a floor, so it caps how many environments can exist and therefore how many connections the function can open, and RDS Proxy pools and reuses those connections so short invocations stop opening new ones. A raises the ceiling the function is already hitting and makes the database failure worse. B pre-warms environments to reduce latency and does nothing to limit concurrency. D changes network placement; the function likely already reaches the database, and subnet choice has no effect on connection count.

*Where this is covered: Concurrency, scaling, and start-up latency.*

</details>

### 8. Normalizing a cache key at the edge (Associate)

A company serves a catalog through Amazon CloudFront. Viewers send a dozen tracking query strings that vary per user, which fragments the cache. The team wants to strip those parameters and lowercase the path on every viewer request, at the lowest possible cost and latency, with no calls to other services.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Associate a Lambda@Edge function with the origin request event.
- **B)** Associate a CloudFront Function with the viewer request event.
- **C)** Associate a Lambda@Edge function with the viewer request event.
- **D)** Invoke a Lambda function through a function URL from the origin.

<details><summary>Answer</summary>

**Answer: B.** CloudFront Functions run in submillisecond durations, scale to millions of requests per second, and are the lightweight option AWS positions for high-scale, latency-sensitive CDN customizations, with cache key normalization the use case AWS names first for them. They run on viewer request, which is where the cache key is decided. A attaches to the origin request event, which is on the origin-facing side of the cache and therefore cannot shape the key that decides whether a request is served from cache. C runs on the right event but costs more and adds milliseconds for logic that needs no network access, file system access or request body. D adds a full network round trip to a separate endpoint for a string operation.

*Where this is covered: Lambda@Edge compared with CloudFront Functions.*

</details>

### 9. Releasing a risky change (Associate)

A team deploys a Lambda function behind API Gateway several times a week. A recent change raised the error rate and was noticed only after all traffic had moved to it. The team wants new code to receive a small share of traffic first and to roll back automatically when errors rise.

Which solution will meet these requirements?

- **A)** Deploy the new code to `$LATEST` and point the API Gateway integration at the unqualified function ARN.
- **B)** Publish a new function version and change the API Gateway integration to the new version's qualified ARN.
- **C)** Publish a new version, keep the API Gateway integration pointed at an alias, and use AWS CodeDeploy to shift alias traffic gradually with a CloudWatch alarm as the rollback trigger.
- **D)** Create a second function with the new code and split traffic with weighted DNS records.

<details><summary>Answer</summary>

**Answer: C.** An alias is a mutable pointer that callers reference, weighted alias routing splits traffic between exactly two published versions, and CodeDeploy automates the shift and the rollback when a CloudWatch alarm fires. A sends all traffic to the new code immediately and leaves nothing to roll back to, because deploying code overwrites `$LATEST`. B is an all-at-once cutover that also couples the API configuration to a version number. D duplicates the function and its configuration and puts DNS caching between the team and a rollback, when the alias mechanism already exists.

*Where this is covered: Packaging, layers, versions, and aliases.*

</details>

### 10. Running out of network interfaces (Professional)

A platform team supports 600 VPC-attached Lambda functions in one shared account and VPC. Each team created its own security group and used a different pair of subnets, and new function deployments now fail with a network interface error. Some functions also take several minutes to become invokable after their first deployment. The team must restore deployments and reduce the chance of recurrence.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Standardize functions on a small set of shared subnet and security group combinations so they reuse the same Hyperplane elastic network interfaces.
- **B)** Detach every function from the VPC and give each one a public IP address.
- **C)** Increase the account's Lambda concurrent executions quota.
- **D)** Give each function its own dedicated security group so interfaces are not shared.
- **E)** Request an increase to the elastic network interfaces per VPC quota, and move workloads into separate accounts and VPCs so the limit is not shared estate-wide.

<details><summary>Answer</summary>

**Answer: A and E.** Lambda creates one Hyperplane elastic network interface per distinct subnet and security group combination and shares it across every function using that combination, so consolidating combinations collapses hundreds of interfaces into a handful and also removes most of the multi-minute `Pending` waits, since the interface already exists. The 500 interfaces per VPC quota is shared with services such as Amazon EFS, so raising it and splitting the estate across accounts and VPCs removes the shared ceiling. B abandons private access to VPC resources, and a Lambda function never receives a public IP address. C addresses a different quota entirely. D is the behavior that caused the exhaustion and would multiply the interface count further.

*Where this is covered: VPC networking, IAM, and encryption.*

</details>

## Summary

AWS Lambda is a sequence of decisions, and each one has a number attached. Decide first whether the work fits: under 15 minutes, stateless between invocations, and expressible as a handler in a supported runtime or a container image, or else it belongs on Fargate, AWS Batch or EC2. Size the function by memory, because CPU scales with it and reaches one vCPU at 1,769 MB, and measure rather than guess. Identify the invocation model, because it decides who retries and where failures land: synchronous callers own their own retries, asynchronous invocation retries twice and needs a destination or dead-letter queue, and event source mappings batch, block on ordering for streams, and defer to the source queue's redrive policy for Amazon SQS. Control concurrency deliberately, reserving it to protect a critical function or a fragile database and provisioning or SnapStarting it to remove cold starts. Publish versions and point callers at aliases so a canary and a rollback are available. Attach a VPC only when private resources demand it, and standardize subnet and security group pairs so Hyperplane interfaces are shared. Then watch throttles, iterator age and async event age, because those are where a serverless design fails quietly.

## Related units

- [Amazon EC2](ec2.md): the instance baseline Lambda is compared against, and the home of purchasing options and instance sizing
- [AWS Batch](batch.md): managed job queues for work that outgrows the 15 minute function timeout
- [Amazon ECS and Amazon ECR](../03-containers/ecs-and-ecr.md): Fargate and container orchestration for long-running workloads and large images
- [Amazon API Gateway](../04-networking/api-gateway.md): the HTTP front door that invokes functions synchronously, with authorizers, throttling and stage deployments
- [Amazon SQS](../06-integration/sqs.md): visibility timeout, dead-letter queues and redrive for the most common event source mapping
- [Amazon EventBridge](../06-integration/eventbridge.md): buses, rules and event patterns that route events to functions across accounts
- [AWS Step Functions](../06-integration/step-functions.md): the orchestrator for multi-step work that exceeds one function
- [Amazon CloudFront](../04-networking/cloudfront.md): distributions and cache behaviors that CloudFront Functions and Lambda@Edge attach to

## Sources

- [Recursive loop detection](https://docs.aws.amazon.com/lambda/latest/dg/invocation-recursion.html): the roughly 16 invocation chain limit and which event sources it covers
- [Lambda@Edge CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-edge-logs.html): that logs land in the Region nearest the edge location that ran the function

- [Lambda quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html): memory, timeout, payload, package, layer, ephemeral storage and network interface limits
- [Understanding Lambda function scaling](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html): the concurrency formula, reserved compared with provisioned concurrency, the 100 unreserved units and the 10x requests per second rule
- [Lambda scaling behavior](https://docs.aws.amazon.com/lambda/latest/dg/scaling-behavior.html): the 1,000 environments per 10 seconds per function scaling rate
- [Understanding the Lambda execution environment lifecycle](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html): Init, Invoke and Shutdown phases, environment reuse, `/tmp` persistence and cold start frequency
- [Configure Lambda function memory](https://docs.aws.amazon.com/lambda/latest/dg/configuration-memory.html): the 128 MB to 10,240 MB range and one vCPU at 1,769 MB
- [Improving startup performance with Lambda SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html): supported runtimes, the provisioned concurrency and EFS exclusions, and SnapStart pricing
- [Invoking a Lambda function asynchronously](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html): the internal queue and the 202 response
- [How Lambda handles errors and retries with asynchronous invocation](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-error-handling.html): two retries at one and two minutes, and six hours of retries for throttles and system errors
- [Configuring error handling settings for Lambda asynchronous invocations](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-configuring.html): maximum event age up to 6 hours and retry attempts between 0 and 2
- [Capturing records of Lambda asynchronous invocations](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-retain-records.html): the five destination types, the dead-letter queue comparison and the reserved concurrency zero behavior
- [Understanding retry behavior in Lambda](https://docs.aws.amazon.com/lambda/latest/dg/invocation-retries.html): who retries for direct, asynchronous and event source mapping invocations
- [How Lambda processes records from stream and queue-based event sources](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html): the source list, batching windows, the 6 MB payload rule and provisioned mode
- [Using Lambda with Amazon SQS](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html): polling and batching behavior, provisioned mode poller ranges and partial batch responses
- [Creating and configuring an Amazon SQS event source mapping](https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html): the six times visibility timeout rule, batch sizes for standard and FIFO queues and the redrive recommendation
- [Configuring scaling behavior for SQS event source mappings](https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-scaling.html): five initial batches, 300 more per minute, the 1,250 ceiling and the maximum concurrency range
- [Using Lambda to process records from Amazon Kinesis Data Streams](https://docs.aws.amazon.com/lambda/latest/dg/with-kinesis.html): shard polling rate, parallelization factor and enhanced fan-out
- [Lambda parameters for Amazon Kinesis Data Streams event source mappings](https://docs.aws.amazon.com/lambda/latest/dg/services-kinesis-parameters.html): batch size, record age, retry attempts, bisect and starting position values
- [Using AWS Lambda with Amazon DynamoDB](https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html): stream polling rate, the TRIM_HORIZON recommendation and the simultaneous reader guidance
- [Giving Lambda functions access to resources in an Amazon VPC](https://docs.aws.amazon.com/lambda/latest/dg/foundation-networking.html): Hyperplane elastic network interfaces, sharing by subnet and security group, the 14 day reclaim and the VPC condition keys
- [Defining Lambda function permissions with an execution role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html): the service principal trust policy and AWSLambdaBasicExecutionRole
- [Managing Lambda dependencies with layers](https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html): five layers, extraction into /opt, zip-only support and layer version immutability
- [Manage Lambda function versions](https://docs.aws.amazon.com/lambda/latest/dg/configuration-versions.html): what a published version freezes, qualified compared with unqualified ARNs
- [Implement Lambda canary deployments using a weighted alias](https://docs.aws.amazon.com/lambda/latest/dg/configuring-alias-routing.html): the two-version limit, the shared role and dead-letter queue rules and the CodeDeploy rolling deployment
- [Creating and managing Lambda function URLs](https://docs.aws.amazon.com/lambda/latest/dg/urls-configuration.html): the endpoint format, AWS_IAM and NONE auth types, CORS and reserved concurrency throttling
- [Response streaming for Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html): the 200 MB limit, the 6 MB uncapped burst and 2 MBps cap, and runtime support
- [Lambda runtimes](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html): supported runtimes, both architectures and the deprecation policy and notice periods
- [Lambda Managed Instances](https://docs.aws.amazon.com/lambda/latest/dg/lambda-managed-instances.html): capacity providers, multi-concurrent invocations and EC2-based pricing with a management fee
- [Types of metrics for Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics-types.html): invocation, performance, concurrency, asynchronous and event source mapping metrics
- [Differences between CloudFront Functions and Lambda@Edge](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/edge-functions-choosing.html): the full capability comparison including events, memory, size and network access
- [Restrictions on Lambda@Edge](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-at-edge-function-restrictions.html): the us-east-1 requirement, numbered versions only and the unsupported Lambda features
- [AWS Lambda pricing](https://aws.amazon.com/lambda/pricing/): request and GB-second billing, the free tier, and provisioned concurrency, SnapStart and streaming charges
- [What are Savings Plans?](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html): Compute Savings Plans applying to Fargate and Lambda usage
