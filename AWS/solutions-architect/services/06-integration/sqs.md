# Amazon SQS

**Where it sits on the exams.** **Amazon Simple Queue Service (Amazon SQS)** is the managed message queue that holds messages durably until a consumer polls for them, deletes them and moves on. It is the default answer whenever a design needs one component to stop depending on another being available, fast enough or correctly sized, and it carries SAA-C03 tasks 2.1 and 3.2 and SAP-C02 tasks 2.4 and 4.4 almost single-handedly, with a supporting role in SAA-C03 task 2.2 and SAP-C02 task 2.5. The rule of thumb the exam wants is that a queue is a buffer with a memory: put one between a fast producer and a slow consumer and the producer stops failing when the consumer does, the consumer scales on backlog rather than on request rate, and work survives a restart because it is still sitting in the queue.

## How a message moves through a queue

A queue is a named, Regional resource with an Amazon Resource Name (ARN) of the form `arn:aws:sqs:us-east-2:123456789012:my_queue`. A producer calls `SendMessage` or `SendMessageBatch`; Amazon SQS stores the message redundantly across multiple Availability Zones before acknowledging the send, so no single computer, network or Availability Zone failure makes it unreachable. There is no push. A consumer calls `ReceiveMessage`, which returns up to ten messages with a receipt handle for each, processes the work, then calls `DeleteMessage` with that handle. Nothing leaves the queue until the consumer deletes it. That lifecycle of receive, process, delete is the whole model, and almost every SQS exam question is really about what happens when one of those three steps fails.

Two clocks run over it. The message retention period decides how long an undelivered message survives: four days by default, configurable from 60 seconds to 1,209,600 seconds, which is 14 days. The visibility timeout decides how long a received message stays hidden from other consumers, and has its own section below. A queue holds an unlimited number of messages, so there is no backlog ceiling to design against, only retention.

A message can carry up to 1 MiB of payload. AWS raised that ceiling from 256 KiB in August 2025 across all commercial Regions and AWS GovCloud (US), and updated the **AWS Lambda** event source mapping, where Lambda is the serverless compute service that runs code without provisioned servers, to accept the larger payloads. Older study material, and some AWS pages, still quote 256 KB. Alongside the body a message can carry up to ten message attributes, each with a name, a data type of `String`, `Number` or `Binary`, and a value, all of it counting against the 1 MiB limit, so that a consumer can triage a message without parsing the body first. Message system attributes are separate and reserved for AWS services: the only supported one is `AWSTraceHeader`, carrying a trace header for **AWS X-Ray**, the distributed tracing service, and it does not count toward the message size.

For payloads that do not fit, the **Amazon SQS Extended Client Library** stores the payload as an object in **Amazon S3**, the object storage service, and puts only a reference to that object in the queue, up to a maximum of 2 GB. AWS publishes the library for Java and for Python, and it works only through those SDKs, not through the console, the AWS CLI or the HTTP API.

## Standard queues compared with FIFO queues

Every SQS design starts by picking a queue type, and the choice cannot be changed later. The table below is the comparison the exams return to most often; read the last row first, because the stem's own wording usually decides the answer.

| Property | Standard queue | FIFO queue |
|---|---|---|
| Ordering | Best-effort ordering. Messages may occasionally arrive out of order | Strictly preserved, per message group ID. Different groups may be processed relative to each other in any order |
| Delivery guarantee | At-least-once. More than one copy of a message might be delivered | Exactly-once processing. A message is delivered once and stays unavailable until a consumer processes and deletes it |
| Throughput | Nearly unlimited API calls per second for `SendMessage`, `ReceiveMessage` and `DeleteMessage` | 300 transactions per second per API action, or 3,000 messages per second when every call carries a batch of ten. High throughput mode raises this substantially |
| Duplicate suppression | None. Consumers must be idempotent | Duplicates are not introduced into the queue within a five-minute deduplication interval |
| Parallelism | Any number of consumers on the whole queue | One in-flight message per message group at a time; groups are processed in parallel |
| Naming | Any valid queue name | The queue name must end in `.fifo` |
| Wording that selects it | "duplicates are acceptable", "order does not matter", "maximum throughput" | "must be processed in the order", "no duplicates", "exactly once", "per customer, in order" |

FIFO ordering is not queue-wide by default; it is per message group. Every message sent to a FIFO queue must carry a **message group ID**, and the action fails if one is missing. Messages sharing a group ID are processed one at a time in strict order, and no further message from that group is returned until the in-flight one is deleted or becomes visible again, while messages in different groups process concurrently. That gives the design lever the exam tests: use the customer ID, the account number or the device ID as the group ID and you get per-entity ordering with fleet-wide parallelism. Use a single constant group ID only when the whole queue must be strictly sequential, which caps you at one message in flight at a time.

Deduplication is the other half. Within a five-minute deduplication interval, two sends carrying the same **message deduplication ID** are treated as duplicates and only one copy is delivered, which is what makes a producer retry safe. You either supply the deduplication ID yourself or enable **content-based deduplication**, which makes Amazon SQS generate it as a SHA-256 hash of the message body. Note what that hash covers: the body, and not the message attributes, so two messages with identical bodies and different attributes are deduplicated to one. Amazon SQS keeps tracking a deduplication ID even after the message has been received and deleted.

FIFO throughput is the limit that ends up in Professional scenarios. Amazon SQS stores FIFO queue data in partitions that it manages for you, and it hashes the message group ID to choose the partition, so the way to get more capacity is more distinct group IDs rather than a bigger queue. **High throughput mode** lifts the default ceiling to 70,000 transactions per second without batching, or 700,000 messages per second with batches of ten, in US East (N. Virginia), US West (Oregon) and Europe (Ireland), with lower but still substantial ceilings elsewhere. AWS recommends group IDs that take a large number of distinct values, because a workload funneling everything through a handful of groups hits a partition limit long before the Regional one.

> **Professional depth.** Standard queues now accept `MessageGroupId` too, but it means something entirely different there. **Fair queues** use it purely as a tenant identifier: Amazon SQS watches the distribution of in-flight messages, identifies a tenant monopolizing consumers, and prioritizes returning messages from the quieter tenants so their dwell time stays low. It applies automatically, needs no consumer change, and imposes no throughput limit. It does not order anything, so do not let a stem that mentions a group ID push you toward FIFO on its own.

## Visibility timeout, polling, and delaying delivery

The visibility timeout is the most misconfigured SQS setting and the one the exams probe hardest. When `ReceiveMessage` returns a message, the message stays in the queue but becomes invisible to other consumers for the duration of the timeout. The default is 30 seconds; the minimum is 0 seconds and the maximum is 12 hours. If the consumer deletes the message inside that window, the message is gone. If it does not, because the process crashed, the network failed or the work took longer than expected, the message becomes visible again and another consumer picks it up. That is the durability property that makes a queue safe, and it is also the mechanism behind every "our orders are being processed twice" scenario: the timeout was shorter than the processing time.

There are two fixes and the stem tells you which it wants. If processing time is predictable, raise the queue's timeout past it. If it varies, keep the timeout modest and have the consumer call `ChangeMessageVisibility` periodically as a heartbeat on the message it holds. AWS documents a hard bound on that: the 12-hour maximum is measured from when the message was first received, and extending does not reset it, so work that genuinely takes longer belongs in **AWS Step Functions**, the workflow service that holds the state of a multi-step process, rather than in one long-held message. Setting `VisibilityTimeout` to 0 releases a message for immediate retry. When the consumer is a Lambda function, AWS tells you to set the queue's visibility timeout to at least six times the function timeout plus any batching window; the mechanics of batching and partial batch failures belong to [AWS Lambda](../02-compute/lambda.md).

In-flight messages, meaning received but not yet deleted, are capped at approximately 120,000 per queue. The failure mode differs by polling style: with **short polling** you get an `OverLimit` error, while with **long polling** Amazon SQS returns nothing new until the in-flight count falls. The standard queue quota is adjustable through a quota increase request; the FIFO one requires a request to AWS Support.

Polling itself is worth real money. Short polling, the default, samples a weighted random subset of the servers holding your messages and answers immediately, even with nothing to return. That produces empty responses, which are billed requests, and false empty responses, where messages exist but were not on the sampled servers. Long polling queries all servers and holds the request open until a message arrives or the wait time expires, up to a maximum of 20 seconds. It is in effect whenever `WaitTimeSeconds` on the request is greater than zero, or whenever the queue attribute `ReceiveMessageWaitTimeSeconds` is greater than zero; setting either to 0 selects short polling. Long polling reduces empty and false empty responses and returns messages as soon as they are available, which is why "reduce the cost of an idle consumer fleet" maps to setting the wait time to 20 seconds rather than to a smaller fleet.

Two more timers hide messages, and the exam likes to separate them from the visibility timeout. A **delay queue** hides every new message for a queue-wide `DelaySeconds`, default and minimum 0, maximum 15 minutes. A **message timer** does the same for one message, set on `SendMessage`, with the same range, and it overrides the queue's value. The distinction that decides questions is when the hiding starts: a delay applies when the message is added to the queue, a visibility timeout only after a consumer has received it. Two footnotes: FIFO queues do not support per-message timers, and changing a queue-level delay is retroactive on a FIFO queue but not on a standard one. For anything beyond 15 minutes, AWS points you at **EventBridge Scheduler**, the scheduling feature of **Amazon EventBridge**, the event bus that routes events to targets by content.

## Dead-letter queues, redrive, and poison messages

A message that cannot be processed will be retried until it expires, consuming capacity and hiding real failures behind a stable-looking backlog. A **dead-letter queue** is the answer: an ordinary queue, created by you first, that the source queue targets through a **redrive policy** carrying a `maxReceiveCount`. When a message has been received that many times without being deleted, Amazon SQS moves it there instead of making it visible again. Valid values run from 1 to 1,000, and a value of 1 sends a message to the dead-letter queue on its first failed receive, so set it high enough to absorb transient errors, commonly five or more. Three rules decide exam questions: the dead-letter queue must be in the same AWS account and Region as the source queue, its type must match, so a FIFO queue can only use a FIFO dead-letter queue and a standard queue only a standard one, and AWS advises against pairing one with a FIFO queue where the exact order of operations must survive, because pulling a message out of the sequence changes the meaning of the rest.

Retention on the dead-letter queue behaves differently by type, and it is a quiet source of data loss. For a standard queue, expiration is always based on the original enqueue timestamp, which does not change when the message moves, so a message that spent one day in a source queue has only three days left in a dead-letter queue with four-day retention. For a FIFO queue the timestamp resets on the move. The best practice follows: always set the dead-letter queue's retention period longer than the source queue's.

Getting messages back out is **dead-letter queue redrive**, driven by `StartMessageMoveTask`, with `ListMessageMoveTasks` and `CancelMessageMoveTask` alongside it. By default it moves messages back to their source queue, and it can target any other queue of the same type instead. You can cap the rate: the console offers system-optimized velocity or a custom maximum topping out at 500 messages per second, and starting low protects a source queue that is still fragile. A redrive task runs for a maximum of 36 hours and an account can have at most 100 active tasks. Two behaviors catch people out: redrive cannot filter or modify messages on the way through, and it resets the retention period, assigning a new message ID and enqueue time.

The **redrive allow policy** sits on the dead-letter queue and controls the other direction, namely which source queues may use it. The default allows all source queues, `byQueue` names up to ten specific source queue ARNs, and `denyAll` stops the queue being used as a dead-letter queue at all. In a shared platform account this is the control that stops one team pointing its failures at another team's dead-letter queue. One monitoring trap goes with it: messages that Amazon SQS moves automatically are not counted by `NumberOfMessagesSent`, which counts only manual sends, so the metric to alarm on is `ApproximateNumberOfMessagesVisible` on the dead-letter queue.

## Choosing SQS against SNS, EventBridge, Kinesis and Amazon MQ

An exam question hides this comparison inside a paragraph of business context, and each of the four alternatives is a real service used for a real job. **Amazon Simple Notification Service (Amazon SNS)** is the publish and subscribe service that pushes one message to many subscribers at once, with filter policies so each subscriber sees only the messages it cares about; it does not store messages for a slow consumer, which is why the canonical durable fan-out is SNS to several SQS queues, one per consumer, so each consumer keeps its own buffer and its own dead-letter queue. Amazon EventBridge routes on the content of an event using rules and event patterns and delivers across accounts and Regions, which is what you want when the set of targets keeps changing and the routing decision depends on fields inside the event. **Amazon Kinesis Data Streams**, the managed real-time streaming service, keeps an ordered, replayable log that several independent consumers read at their own positions, so a stem asking to reprocess the last 24 hours of records, or to feed both a dashboard and a batch job from the same data, is a stream rather than a queue, because an SQS message is destroyed the moment one consumer deletes it. **Amazon MQ** is a managed broker for ActiveMQ and RabbitMQ, and it wins exactly one argument: an existing application already speaks AMQP, MQTT, OpenWire or STOMP and is not being rewritten.

The rule of thumb is what each one does to coupling. SQS buffers work so a producer does not need the consumer to be up, SNS duplicates one message to many subscribers, EventBridge decides at delivery time who should get it, Kinesis keeps the sequence so it can be read again, and Amazon MQ preserves a protocol so code does not change. A question that pairs "decouple" with "must not lose work while the downstream service is down" is SQS; pair it with "notify several teams" and it is SNS; with "route different event types to different targets" and it is EventBridge; with "replay" or "ordered stream consumed by multiple applications" and it is Kinesis.

Inside AWS, SQS is wired into most of the services you would expect. Lambda polls a queue through an event source mapping and deletes the batch on success; that unit owns the batching, scaling and partial-failure behavior, and the piece that belongs here is the queue-side setting, namely a generous visibility timeout and a redrive policy on the queue, because a Lambda dead-letter queue catches only asynchronous invocations and never an SQS source. **Amazon EC2 Auto Scaling**, which adds and removes **Amazon EC2** virtual server instances to match demand, scales a worker fleet on queue depth, but AWS warns against target-tracking on `ApproximateNumberOfMessagesVisible` directly, because backlog does not move in proportion to fleet size. The documented approach is a backlog per instance metric, messages available divided by `InService` instances, with a target of acceptable latency divided by average processing time per message. Their example: 1,500 messages, ten instances, 0.1 second processing and a ten-second latency budget gives a target of 100 against a current 150, so the group scales out. Pair it with instance scale-in protection when tasks are long. Finally, a short list of AWS features cannot target a FIFO queue at all: S3 Event Notifications, Auto Scaling lifecycle hooks, IoT rule actions and Lambda dead-letter queues.

## Security, monitoring, pricing and the limits that matter

Access to a queue can be granted two ways, and knowing which one a scenario needs is a recurring question. An **AWS Identity and Access Management (IAM)** identity-based policy, attached to a user or role, says what that principal may do. A queue access policy, the resource-based policy on the queue itself, says which principals may act on the queue. Within one account either is usually enough. Across accounts you need both: AWS states plainly that IAM identity-based policies alone are not sufficient for cross-account access to SQS queues, so the queue's access policy must name the external principal. A second trap is that cross-account permissions do not apply to the management actions at all, including `CreateQueue`, `DeleteQueue`, `ListQueues`, `SetQueueAttributes` and `TagQueue`; for those the caller must be in the account that owns the queue. A queue policy is bounded at 8,192 bytes, 20 statements, 50 principals and 10 conditions.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::111122223333:role/OrderProducer"},
    "Action": "sqs:SendMessage",
    "Resource": "arn:aws:sqs:us-east-2:444455556666:orders"
  }]
}
```

For the network path, an interface VPC endpoint powered by **AWS PrivateLink**, which exposes AWS services as private addresses inside **Amazon VPC**, the isolated virtual network service, lets instances in private subnets reach SQS without an internet gateway, NAT device or VPN. It works only with HTTPS endpoints, needs private DNS enabled, and does not support legacy `queue.amazonaws.com` style endpoints. The matching control is a queue policy denying any request whose `aws:SourceVpc` is not yours, with one caveat: redrive runs outside your VPC, so such a policy needs an exception on `aws:CalledViaLast` or `aws:ViaAWSService` or redrive will fail.

Encryption at rest has two options and the difference is about key control, not strength. Server-side encryption with SQS-managed keys (SSE-SQS) uses AES-256, requires no configuration and costs nothing extra, and it is the default for a queue created over HTTPS without encryption attributes. Server-side encryption with **AWS Key Management Service (AWS KMS)**, the managed key service, uses either the AWS managed key `alias/aws/sqs` or a customer managed key, and it is what a stem asking for key rotation control, key policies or an audit trail of key use is describing. With SSE-KMS, the data key reuse period controls how long SQS may reuse a data key before calling KMS again: 60 to 86,400 seconds with a default of 300, so a longer period means fewer KMS requests and lower KMS cost. Encryption covers the message body only; queue metadata, message metadata including message attributes, and per-queue metrics are not encrypted, which is a reason to keep anything sensitive out of attributes. One cross-account gotcha: a queue encrypted with the default AWS managed KMS key cannot invoke a Lambda function in a different account.

**Amazon CloudWatch**, the metrics and logs service, receives SQS metrics automatically in the `AWS/SQS` namespace with a single dimension, `QueueName`. Four carry most of the diagnostic weight. `ApproximateNumberOfMessagesVisible` is the backlog, the thing to alarm on and to scale from. `ApproximateAgeOfOldestMessage` is the latency signal, and a rising value with a flat backlog means consumers are stuck rather than outnumbered. `ApproximateNumberOfMessagesNotVisible` counts in-flight work, and a value near 120,000 means consumers hold messages they never delete. `NumberOfEmptyReceives` is the evidence that a fleet is still on short polling. FIFO queues add `ApproximateNumberOfGroupsWithInflightMessages`, which shows whether your group IDs are spread widely enough for the throughput you expect.

Pricing has one shape worth memorizing because it drives cost questions. Every SQS action counts as a request, and each 64 KB chunk of payload is billed as one request, so a single action carrying a 1 MiB payload is billed as 16 requests. Two consequences follow: batching ten messages into one `SendMessageBatch` is one action rather than ten, and long polling eliminates the empty `ReceiveMessage` calls otherwise billed for finding nothing. The first million requests each month are free, FIFO requests are priced on their own schedule, and there is no data transfer charge in-Region. Storage is not billed separately, so long retention costs nothing by itself.

Batching is the lever that changes the bill. `SendMessageBatch`, `DeleteMessageBatch` and `ChangeMessageVisibilityBatch` each carry up to ten messages, and the batch counts as one request, so a consumer that deletes one message at a time pays ten times what a batching consumer pays for the same work. The whole batch shares the 1 MiB per-request payload ceiling, so ten messages of 200 KiB will not fit in one call. Batching also interacts with ordering: in a FIFO queue the messages in one batch may carry different message group IDs, and ordering is still guaranteed only within a group.

## Professional depth

Cross-account queues are the most common Professional shape. A producer in a workload account writes to a queue owned by a platform account: the queue's access policy names the producer's role, the producer's IAM role allows `sqs:SendMessage` on the queue ARN, and if the queue is encrypted with a customer managed KMS key that key's policy must allow the producer `kms:GenerateDataKey` and `kms:Decrypt`. Miss the key policy and the send fails with an access denied error pointing at KMS rather than SQS, which is exactly the distractor a question builds on. A dead-letter queue cannot span accounts, so a central failure-triage queue in a separate account has to be fed by a consumer, not by a redrive policy.

Multi-Region is the constraint people forget. A queue is a Regional resource with no cross-Region replication and no global endpoint, so an active-active or pilot-light design deploys the same queue into each Region and lets the producer choose, usually behind **Amazon Route 53** health-based routing, Route 53 being the DNS service. Anything in flight in a failed Region stays there until that Region returns, which makes the retention period a recovery point objective (RPO) decision rather than a housekeeping one.

Quotas bite in three places at scale. The 120,000 in-flight ceiling is per queue, not per consumer, so a fleet holding messages for minutes at a time reaches it long before any throughput limit, and the fix is shorter processing or more queues rather than a bigger fleet. FIFO throughput is bounded by partitions chosen from the hash of the message group ID, so a migration that used a single constant group ID to be safe stays stuck near the unbatched per-action rate whether or not high throughput mode is enabled; the remediation is redesigning the group ID, which is a code change rather than a console setting. And the redrive ceiling of 100 active tasks per account, each capped at 36 hours and 500 messages per second, sets a real floor on how quickly an estate recovers from a large incident.

For organization-wide governance, treat queue policies the way you treat bucket policies. **AWS Organizations**, the multi-account governance service service control policies can deny `sqs:SetQueueAttributes` outside a pipeline role so queue configuration cannot drift, a redrive allow policy of `denyAll` keeps a shared dead-letter queue from being co-opted, and an `aws:SourceOrgID` condition on every queue policy prevents an accidental public grant from becoming a real one.

A Professional question usually extends the Associate one by adding a constraint that invalidates the obvious answer. The Associate version says duplicate processing is occurring and the answer is a longer visibility timeout; the Professional version adds that processing time varies from seconds to an hour, so the answer becomes a heartbeat with `ChangeMessageVisibility` plus idempotent consumers, and if the work can run for a day the answer moves out of SQS into Step Functions because of the 12-hour ceiling. Or the Associate version says messages must be processed in order and the answer is FIFO; the Professional version adds a throughput figure above the unbatched ceiling, so the answer becomes high throughput mode with the tenant identifier as the message group ID.

## Worked scenario

A ticketing company sells event seats through a web tier on EC2 behind a load balancer and a worker tier that reserves seats, charges a card and emails a confirmation. At an on-sale moment traffic rises by two orders of magnitude in under a minute, and today the web tier calls the worker tier synchronously and times out. Two requirements shape the redesign: reservations for a single event must be applied in the order they arrive, because seats are allocated first come first served, and a payment must never be charged twice.

The web tier writes a reservation message to a FIFO queue with the event ID as the message group ID and a client-generated reservation token as the message deduplication ID. Per-event ordering is preserved while thousands of concurrent events process in parallel, and a retry from a web server that lost its connection inside the five-minute deduplication interval creates no second charge. The worker tier is an Auto Scaling group that long-polls with a 20-second wait, holds a visibility timeout of five minutes against a payment call that usually takes eight seconds, and extends it by heartbeat when the provider is slow. Scaling uses a backlog per instance target rather than raw queue depth, with instance scale-in protection so a worker is never terminated mid-payment. A redrive policy with `maxReceiveCount` set to 5 sends broken reservations to a FIFO dead-letter queue whose retention is 14 days against the source queue's 4, and a CloudWatch alarm on `ApproximateNumberOfMessagesVisible` there pages the on-call engineer.

Confirmation email is a second consumer, so it hangs off an SNS topic that the worker publishes to, with a standard queue subscribed for the email service and another for the analytics pipeline. The reservation queue is encrypted with a customer managed KMS key because card tokens pass through it, workers reach it over an interface VPC endpoint from private subnets, and the queue policy denies anything not arriving from that VPC, with the `aws:CalledViaLast` exception so redrive still works.

The exam asks this scenario as a question about which queue type and which identifier, and the keyed answer is a FIFO queue using the event ID as the message group ID and the reservation token as the message deduplication ID. The two distractors that look right are a standard queue with an idempotency table, which meets the duplicate requirement but not the ordering one, and a FIFO queue with a single fixed message group ID, which meets both requirements and then fails the throughput one.

## Exam lens

- "Must be processed in the order they were sent" and "no duplicates" map to a FIFO queue; a standard queue with an application-side sequence number is the distractor that adds work and still cannot order.
- "Order matters only within each customer" maps to a FIFO queue with the customer ID as the message group ID; a single group ID is the distractor that serializes the whole queue.
- "The application processes messages twice" maps to a visibility timeout shorter than the processing time, fixed by raising it or adding a `ChangeMessageVisibility` heartbeat, bounded by 12 hours from first receipt; increasing consumer count is the distractor that makes it worse.
- "Reduce the cost of polling an often-empty queue" maps to long polling with a wait time of up to 20 seconds; a smaller consumer fleet is the distractor that raises latency instead.
- "A few messages fail repeatedly and block the backlog" maps to a dead-letter queue with a `maxReceiveCount` in the redrive policy, not to a longer retention period.
- "Failed messages disappear before anyone investigates" maps to setting the dead-letter queue's retention period longer than the source queue's, because a standard queue keeps the original enqueue timestamp on the move.
- "Reprocess the messages that failed during the outage" maps to dead-letter queue redrive with `StartMessageMoveTask`, rate-capped to protect the source queue.
- "Hide new messages for a few minutes so a downstream system can catch up" maps to a delay queue or a per-message timer, both capped at 15 minutes; anything longer maps to EventBridge Scheduler.
- "Several independent teams need the same event" maps to SNS fan-out into one SQS queue per team, not to several consumers on one queue.
- "Records must be replayable and read by more than one application" maps to Kinesis Data Streams, because deleting an SQS message destroys it.
- "An account in another organizational unit must send to our queue" maps to the queue access policy naming that principal, plus the KMS key policy when the queue is encrypted; an IAM policy alone is the distractor.
- "Scale the worker fleet on the queue" maps to a backlog per instance target tracking metric; target tracking directly on `ApproximateNumberOfMessagesVisible` is the documented wrong answer.

## Knowledge check

### 1. Buffering an image pipeline (Associate)

A media company lets users upload photos through a web tier that runs on Amazon EC2 instances. Each upload triggers a resize and a watermark job that takes about 40 seconds. During promotions the upload rate rises tenfold for a few minutes and the web tier begins returning errors because the processing tier cannot keep up. Occasionally processing the same photo twice is acceptable, and the order of processing does not matter. The company wants the highest possible throughput.

Which solution will meet these requirements?

- **A)** Publish each upload to an Amazon SNS topic and subscribe the processing tier with an HTTP endpoint.
- **B)** Write each upload to an Amazon SQS FIFO queue with a single message group ID and poll it from the processing tier.
- **C)** Write each upload to an Amazon SQS standard queue and poll it from an Auto Scaling group of processing instances.
- **D)** Write each upload to an Amazon Kinesis Data Streams stream and process it with instances that read from the shards.

<details><summary>Answer</summary>

**Answer: C.** The stem gives the three signals that select a standard queue: duplicates are acceptable, order does not matter, and throughput should be as high as possible. Standard queues support a nearly unlimited number of API calls per second per action, and a queue in front of an Auto Scaling group absorbs the burst so the web tier stops failing. A pushes to a subscriber rather than storing work, so an overwhelmed endpoint still fails and the burst is not buffered. B works but caps throughput at 300 transactions per second per action, and a single message group ID allows only one in-flight message at a time, which is the opposite of the stated goal. D adds a replayable ordered log the scenario does not need, and shard capacity must be managed.

*Where this is covered: Standard queues compared with FIFO queues.*

</details>

### 2. Per-account transaction ordering (Associate)

A bank posts ledger transactions to a processing service. Transactions for the same account number must be applied in the order they were submitted, and a retried submission must never post twice. Transactions for different account numbers are independent of each other, and the service must process many accounts concurrently.

Which solution will meet these requirements?

- **A)** Use an Amazon SQS standard queue and have consumers sort messages by a timestamp attribute before processing.
- **B)** Use an Amazon SQS FIFO queue with the account number as the message group ID and a submission token as the message deduplication ID.
- **C)** Use an Amazon SQS FIFO queue with a constant message group ID and content-based deduplication enabled.
- **D)** Use an Amazon SNS FIFO topic with a filter policy for each account number.

<details><summary>Answer</summary>

**Answer: B.** FIFO ordering applies per message group, so using the account number as the group ID gives strict order within each account while different accounts process in parallel. A submission token as the message deduplication ID makes a producer retry inside the five-minute deduplication interval safe. A cannot work: a standard queue makes only a best-effort attempt at order, and a consumer that holds ten messages cannot sort messages it has not received yet. C orders correctly but serializes every account behind one group, allowing a single in-flight message at a time, which breaks the concurrency requirement. D is a topic rather than a queue, so it does not hold work for a consumer, and a filter policy selects subscribers rather than ordering messages.

*Where this is covered: Standard queues compared with FIFO queues.*

</details>

### 3. Orders processed more than once (Associate)

A retailer's worker fleet reads order messages from an Amazon SQS standard queue. Each order calls an external fulfillment API that usually responds in 20 seconds but sometimes takes up to four minutes. The queue uses default settings. Operators report that some orders are fulfilled twice, and that duplicate work begins while the first worker is still running.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable content-based deduplication on the queue.
- **B)** Increase the queue's visibility timeout so that it comfortably exceeds the longest expected processing time.
- **C)** Reduce the message retention period from 4 days to 1 hour.
- **D)** Have each worker call `ChangeMessageVisibility` periodically while it is still processing a message.
- **E)** Configure a dead-letter queue with a `maxReceiveCount` of 1.

<details><summary>Answer</summary>

**Answer: B and D.** The default visibility timeout is 30 seconds, so a message being processed for four minutes becomes visible again long before the worker deletes it and a second worker picks it up. Raising the timeout past the worst case fixes the common path, and a heartbeat with `ChangeMessageVisibility` covers the variable tail without setting the queue-wide value to the worst case for every message. A is not available here: content-based deduplication is a FIFO-only setting and cannot be enabled on a standard queue. C changes only how long an undelivered message survives and does nothing about redelivery during processing. E would move a message to the dead-letter queue on its first failed receive, discarding valid orders rather than preventing duplicate work.

*Where this is covered: Visibility timeout, polling, and delaying delivery.*

</details>

### 4. An expensive idle fleet (Associate)

A company runs 60 consumer instances that read from an Amazon SQS queue. The queue is empty most of the day. The finance team notices a large number of billable Amazon SQS requests even when no messages are being processed, and the CloudWatch metric `NumberOfEmptyReceives` is very high. The company wants to lower the SQS request cost without increasing the time it takes to pick up a new message.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Reduce the consumer fleet to 10 instances and accept the longer processing time.
- **B)** Increase the queue's message retention period to 14 days.
- **C)** Set the queue's delay period to 15 minutes so consumers poll less often.
- **D)** Set the queue attribute `ReceiveMessageWaitTimeSeconds` to 20 seconds to enable long polling.

<details><summary>Answer</summary>

**Answer: D.** Short polling answers immediately even when it finds nothing, and every one of those empty responses is a billed request. Long polling holds the request open until a message arrives or the wait time expires, up to a maximum of 20 seconds, which removes both empty responses and false empty responses, and it returns messages as soon as they become available, so pickup latency does not increase. A cuts request volume but directly increases processing time, which the stem forbids. B changes how long an undelivered message is kept and has no effect on polling cost. C hides new messages for 15 minutes after they are sent, which delays every message rather than reducing empty receives.

*Where this is covered: Visibility timeout, polling, and delaying delivery.*

</details>

### 5. A message that will never succeed (Associate)

A logistics application consumes shipment events from an Amazon SQS standard queue. A small number of malformed events cause the consumer to throw an exception every time. Those events return to the queue, are retried indefinitely, and keep the backlog metric elevated so the team cannot tell whether real work is queued. The team wants the bad events isolated for investigation without losing them.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create a second standard queue, configure it as the dead-letter queue of the source queue with a redrive policy whose `maxReceiveCount` is 5, and alarm on `ApproximateNumberOfMessagesVisible` on that queue.
- **B)** Reduce the source queue's message retention period to 1 hour so malformed events expire quickly.
- **C)** Have the consumer catch the exception and call `DeleteMessage` on any event it cannot parse.
- **D)** Create a second FIFO queue and configure it as the dead-letter queue of the standard source queue.

<details><summary>Answer</summary>

**Answer: A.** A redrive policy moves a message to a dead-letter queue once it has been received `maxReceiveCount` times without being deleted, which isolates the malformed events after five honest attempts and leaves the backlog metric meaningful. Alarming on `ApproximateNumberOfMessagesVisible` is the documented way to watch a dead-letter queue, because messages moved there automatically are not counted by `NumberOfMessagesSent`. B discards the events entirely and shortens the safety margin for every other message. C also discards them, and it loses exactly the payloads the team wants to investigate. D is not a valid configuration: the dead-letter queue type must match the source queue type, so a standard queue can only use a standard dead-letter queue.

*Where this is covered: Dead-letter queues, redrive, and poison messages.*

</details>

### 6. A queue shared across accounts (Professional)

A platform team owns an encrypted Amazon SQS queue in a central account. An application running in a separate workload account must send messages to it. The queue is encrypted with a customer managed AWS KMS key that the platform account owns. The application's task role has been granted `sqs:SendMessage` on the queue ARN through an identity-based policy, but every send fails with an access denied error.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Add a statement to the queue's access policy allowing the workload account's task role to call `sqs:SendMessage` on the queue.
- **B)** Create a dead-letter queue in the workload account and attach it to the central queue with a redrive policy.
- **C)** Add a statement to the KMS key policy allowing the workload account's task role to call `kms:GenerateDataKey` and `kms:Decrypt`.
- **D)** Recreate the queue as a FIFO queue so that cross-account sends are deduplicated.
- **E)** Attach a VPC endpoint policy in the central account that allows `sqs:SendMessage` from the workload account.

<details><summary>Answer</summary>

**Answer: A and C.** AWS states that identity-based policies alone are not sufficient for cross-account access to an SQS queue, so the queue's own resource-based access policy must name the external principal. Because the queue is encrypted with a customer managed key, the sender also needs key permissions, and a send requires `kms:GenerateDataKey` as well as `kms:Decrypt`. B is impossible, since a dead-letter queue must be in the same account and Region as its source queue, and it would not address an access denied error on send. D changes the delivery semantics of the queue and has nothing to do with authorization. E controls traffic entering through an endpoint in a VPC; it cannot grant permissions across accounts on its own, and the application is not sending through the central account's VPC.

*Where this is covered: Security, monitoring, pricing and the limits that matter.*

</details>

### 7. A FIFO queue that will not go faster (Professional)

A payments platform migrated from a self-managed broker to an Amazon SQS FIFO queue. Every message is sent with the same message group ID because the original design processed one message at a time. Volume has grown to roughly 9,000 messages per second at peak in the US East (N. Virginia) Region, and the platform is now throttled. Ordering must still be preserved for all messages belonging to the same merchant, but messages for different merchants are independent.

Which solution will meet these requirements?

- **A)** Enable high throughput mode on the existing queue and leave the message group ID unchanged.
- **B)** Replace the FIFO queue with a standard queue and set `MessageGroupId` to the merchant ID so that fair queues preserve order per merchant.
- **C)** Enable high throughput mode and change the producer to set the message group ID to the merchant ID, sending messages in batches of ten.
- **D)** Request a Service Quotas increase for in-flight messages on the FIFO queue.

<details><summary>Answer</summary>

**Answer: C.** Amazon SQS hashes the message group ID to choose the partition that stores a message, and each partition has its own transaction ceiling, so a single constant group ID cannot use more than one partition's worth of capacity no matter what mode the queue is in. Distributing across merchant IDs spreads messages across partitions, high throughput mode raises the Regional ceiling to 70,000 transactions per second unbatched in this Region, and batching ten messages per call multiplies the message rate further. A alone leaves everything hashing to one group and therefore one partition. B breaks the ordering requirement: on a standard queue `MessageGroupId` is only a tenant identifier for fair queues and enforces no ordering. D addresses the in-flight ceiling, which is not what is throttling sends.

*Where this is covered: Standard queues compared with FIFO queues.*

</details>

### 8. Recovering from a regional outage (Professional)

A company processes insurance claims through an Amazon SQS standard queue consumed by an Auto Scaling group. A downstream API was unavailable for 30 hours, during which roughly 400,000 claims exceeded the queue's `maxReceiveCount` and were moved to the dead-letter queue. The source queue's retention period is 4 days and the dead-letter queue's is also 4 days. The API is healthy again. The company must reprocess all affected claims, must not overwhelm the recovered API, and wants the least operational overhead.

Which solution will meet these requirements?

- **A)** Write a script that receives messages from the dead-letter queue and re-sends them to the source queue at a fixed rate.
- **B)** Start a dead-letter queue redrive to the source queue with a custom maximum velocity, and raise the dead-letter queue's retention period above the source queue's.
- **C)** Increase the source queue's `maxReceiveCount` to 1,000 and wait for the messages to be retried automatically.
- **D)** Create a new FIFO queue, redrive the dead-letter queue into it, and point the consumers at the new queue.

<details><summary>Answer</summary>

**Answer: B.** Dead-letter queue redrive moves messages back to the source queue through a managed task, and custom velocity caps the rate, with a maximum of 500 messages per second, so the recovered API is not flooded. Raising the dead-letter queue's retention matters because a standard queue keeps the original enqueue timestamp when a message moves, so claims that already spent time in the source queue have less than four days left where they now sit. A rebuilds a managed feature by hand, which is the operational overhead the stem rules out. C has no effect on messages that have already been moved, since `maxReceiveCount` governs future receives on the source queue only. D changes the queue type, and a standard dead-letter queue cannot be redriven into a FIFO queue because the destination must be the same type.

*Where this is covered: Dead-letter queues, redrive, and poison messages.*

</details>

## Summary

Amazon SQS is a short chain of decisions, and each one has a number behind it. Choose the queue type first, because it cannot be changed: standard for nearly unlimited throughput with at-least-once delivery and best-effort ordering, FIFO for strict per-group ordering and no duplicates inside a five-minute deduplication interval, with the message group ID chosen so ordering is scoped to the entity that needs it rather than to the whole queue. Set the visibility timeout above the real processing time and add a `ChangeMessageVisibility` heartbeat when that time varies, remembering the 12-hour ceiling. Turn on long polling with a wait time of up to 20 seconds, because short polling bills you for finding nothing. Attach a dead-letter queue with a sensible `maxReceiveCount`, give it a longer retention period than the source, and keep redrive in reserve for recovering after an outage. Secure the queue with an access policy as well as IAM, since cross-account access needs both, and remember the KMS key policy when the queue is encrypted. Then scale consumers on backlog per instance, and watch message age rather than message count to tell a stuck consumer from a busy one.

## Related units

- [AWS Lambda](../02-compute/lambda.md): event source mappings, batching and the six times visibility timeout rule for SQS-triggered functions
- [Amazon SNS](sns.md): fan-out to several queues, message filtering, and FIFO topics paired with FIFO queues
- [Amazon EventBridge](eventbridge.md): content-based routing, cross-account buses and EventBridge Scheduler for delays beyond 15 minutes
- [Amazon MQ](amazon-mq.md): the managed broker option when an application already speaks AMQP, MQTT, OpenWire or STOMP
- [Amazon Kinesis](../09-analytics/kinesis.md): ordered, replayable streams read by several independent consumers
- [AWS Step Functions](step-functions.md): where work moves when it outlives the 12-hour visibility timeout ceiling
- [Amazon EC2 Auto Scaling](../02-compute/ec2-auto-scaling.md): backlog per instance target tracking and instance scale-in protection for queue workers
- [AWS KMS](../07-security/kms-and-cloudhsm.md): customer managed keys, key policies and the data key reuse period

## Sources

- [Amazon SQS endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/sqs-service.html): the 120,000 in-flight message quota for standard queues and the FIFO figure. Note that this table still gives the message size as 256 KB, which the quotas page supersedes at 1 MiB

- [Amazon SQS standard queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html): at-least-once delivery, best-effort ordering and nearly unlimited API calls per second
- [Amazon SQS FIFO queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-fifo-queues.html): FIFO delivery and exactly-once processing, message groups and the high throughput note
- [FIFO queue delivery logic in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-understanding-logic.html): per-group ordering, the required message group ID and parallel processing across groups
- [Exactly-once processing in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-exactly-once-processing.html): the five-minute deduplication interval and content-based deduplication hashing the body only
- [Amazon SQS FIFO queue key terms](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-key-terms.html): deduplication ID tracking after deletion, and the AWS features not compatible with FIFO queues
- [High throughput for FIFO queues in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/high-throughput-fifo.html): partitions, hashing the message group ID and the advice to use many distinct group IDs
- [Amazon SQS message quotas](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/quotas-messages.html): 1 MiB message size, 4 day default retention, 300 and 3,000 FIFO rates, high throughput ceilings and policy quotas
- [Amazon SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html): 30 second default, 12 hour maximum, ChangeMessageVisibility and the 120,000 in-flight limit
- [Amazon SQS short and long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html): the 20 second maximum wait, WaitTimeSeconds and ReceiveMessageWaitTimeSeconds
- [Amazon SQS delay queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html): the 15 minute maximum, retroactivity on FIFO queues and EventBridge Scheduler for longer delays
- [Amazon SQS message timers](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-timers.html): per-message delays, the override of the queue value and the FIFO limitation
- [Using dead-letter queues in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html): the redrive policy, the redrive allow policy options and retention timestamp behavior
- [Configure a dead-letter queue using the Amazon SQS console](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-dead-letter-queue.html): the queue type must match, and the console's documented maxReceiveCount input range of 1 to 1,000
- [Learn how to configure a dead-letter queue redrive in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-dead-letter-queue-redrive.html): StartMessageMoveTask, 500 messages per second, 36 hours and 100 active tasks
- [Message metadata for Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-metadata.html): ten attributes, the data types and the AWSTraceHeader system attribute
- [Managing large Amazon SQS messages using Java and Amazon S3](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-s3-messages.html): the extended client mechanism, the 2 GB maximum and the SDK-only restriction
- [Amazon SQS increases maximum message payload size to 1 MiB](https://aws.amazon.com/about-aws/whats-new/2025/08/amazon-sqs-max-payload-size-1mib/): the August 2025 change from 256 KiB and the Lambda event source mapping update
- [Encryption at rest in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-server-side-encryption.html): SSE-SQS against SSE-KMS, the data key reuse period and what is not encrypted
- [Configuring server-side encryption using SQS-managed keys](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-sqs-sse-queue.html): AES-256, no additional charge and the default on queues created without encryption attributes
- [Overview of managing access in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-overview-of-managing-access.html): queue access policies against IAM policies and the actions cross-account permissions exclude
- [Internetwork traffic privacy in Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-internetwork-traffic-privacy.html): interface VPC endpoints, HTTPS only and private DNS requirements
- [Available CloudWatch metrics for Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-available-cloudwatch-metrics.html): the metric list, the QueueName dimension and how to monitor a dead-letter queue
- [Amazon SQS fair queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-fair-queues.html): MessageGroupId as a tenant identifier on standard queues with no ordering guarantee
- [Scaling policy based on Amazon SQS](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-using-sqs-queue.html): the backlog per instance metric, the worked calculation and instance scale-in protection
- [Amazon SQS pricing](https://aws.amazon.com/sqs/pricing/): every action counts as a request, the 64 KB chunk rule and the one million free requests per month
