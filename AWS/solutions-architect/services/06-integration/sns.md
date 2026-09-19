# Amazon SNS

**Where it sits on the exams.** **Amazon Simple Notification Service (Amazon SNS)** is the managed publish and subscribe service: a publisher sends one message to a topic and Amazon SNS pushes a copy to every subscriber attached to that topic. It owns the publish/subscribe half of SAA-C03 tasks 2.1 and 3.2, and it carries SAP-C02 tasks 2.4 and 4.4 alongside **Amazon Simple Queue Service (Amazon SQS)**, the managed message queue that holds messages until a consumer polls for them. The rule of thumb the exam wants is that a topic is a one-to-many multiplier with no memory: SNS pushes each message once to each subscriber, retries on a fixed schedule, and then discards it, so anything that must survive a subscriber being down needs a queue behind the topic rather than a longer retry.

## Topics, publishers and subscribers

A topic is a Regional resource with an Amazon Resource Name (ARN) of the form `arn:aws:sns:us-east-2:123456789012:price-updates`. A publisher calls `Publish` with a topic ARN and a message, or `PublishBatch` with up to ten entries in one call; the topic looks up every confirmed subscription, evaluates each subscription's filter policy, and delivers a copy to each endpoint that matches. Nothing is stored for later collection, and there is no receive call, no visibility timeout and no deletion step, which is the structural difference from a queue.

A message body is capped at 262,144 bytes, which AWS writes as 256 KiB, and message headers at 16,384 bytes. For anything larger, the **Amazon SNS Extended Client Library**, published for Java and for Python, writes the real payload to an object in **Amazon S3**, the object storage service, and publishes only a reference to it, up to a maximum payload of 2 GB; the receiving queue uses the matching Amazon SQS extended client to dereference it. Note the asymmetry the exam can build on: an SQS queue accepts a 1 MiB message directly, but a message routed through a topic into that queue is bounded by the topic's 256 KiB, so a fan-out design with large payloads offloads to S3.

Alongside the body, a message can carry message attributes, arbitrary name, type and value triples that give subscribers something to filter on without parsing the payload.

Two quotas set the shape of a large estate. An account can hold 100,000 standard topics and 1,000 FIFO topics per Region, and a standard topic accepts up to 12,500,000 subscriptions, which is why one topic per event type with thousands of subscribers is a supported design. Publish throughput is a soft, Regional, per-account quota that varies widely, from 30,000 messages per second in US East (N. Virginia) down to 300 for standard topics in the smallest Regions, and batching counts messages rather than calls.

## Standard topics compared with FIFO topics

The topic type is chosen at creation, cannot be changed afterward, and constrains which subscribers are even legal. Read the table below row by row, because the subscriber restriction eliminates FIFO from most scenarios before ordering is discussed.

| Property | Standard topic | FIFO topic |
|---|---|---|
| Ordering | Best-effort. Subscribers may receive messages out of order | Strict, per message group, in the order published |
| Duplication | At-least-once delivery, so a subscriber may see a message more than once | Deduplicated within a five-minute interval, giving exactly-once delivery when no filter policy is attached |
| Subscribers allowed | All nine protocols, including email, SMS, HTTP/S, mobile push, Lambda and delivery streams | Amazon SQS queues only, both FIFO and standard queues |
| Subscriptions per topic | 12,500,000 | 100 |
| Message group ID | Not used | Mandatory on every publish |
| Archive and replay | Not available | Available, up to 365 days |
| **Message data protection** | Available to existing customers | Not available |
| Wording that selects it | "notify several teams", "send an email and an SMS", "trigger a function" | "in the order they were published", "no duplicate charges", "per account, in sequence" |

The subscriber restriction is the fact most often missed. AWS states plainly that customer managed endpoints such as email addresses, mobile apps, SMS numbers and HTTP/S endpoints cannot preserve strict ordering, so subscribing one to a FIFO topic returns an error. To reach **AWS Lambda**, the serverless compute service that runs code without provisioned servers, you subscribe an SQS queue to the FIFO topic and let the queue trigger the function. Subscribing a standard queue to a FIFO topic is legal and is the documented way to trade ordering for lower cost, because the guarantee ends at the queue: SNS still delivers in order, but a standard queue hands messages to its consumer out of order and possibly more than once.

Ordering on a FIFO topic is scoped to a message group, exactly as it is on a FIFO queue. Every publish must carry a message group ID, SNS preserves order within each group and processes different groups in parallel, and the group ID is passed through to a subscribed FIFO queue but not to a standard queue. SNS also assigns each message a 128-bit sequence number that it places in the message body; raw message delivery strips it along with the rest of the SNS metadata. Throughput follows the group design. The topic attribute `FifoThroughputScope` defaults to `Topic`, which caps the topic at 3,000 messages per second or 20 MB per second, whichever comes first, and deduplicates across the whole topic. A FIFO topic delivers at most 300 messages a second per message group, regardless of the throughput scope, and the scope decides the topic-wide ceiling: 3,000 messages a second or 20 MB a second under the default `Topic` scope, and higher under `MessageGroup`. That change cannot be reverted, so a topic that might ever need the throughput should be created with it.

Deduplication uses a message deduplication ID and a five-minute interval. Content-based deduplication makes SNS hash the message body to generate that ID; the hash excludes message attributes, so two publishes with identical bodies and different attributes collapse to one. Exactly-once delivery holds only when the subscribed FIFO queue permits the SNS service principal, the consumer deletes the message before the visibility timeout expires, and the subscription has no filter policy: AWS is explicit that a filter policy on a FIFO subscription downgrades the guarantee to at-most-once.

## Subscription protocols and the fan-out pattern

A subscription pairs a topic with one endpoint and one protocol, and the protocol decides the delivery format, the retry schedule and whether the subscriber must confirm. The table below lists all nine protocols SNS accepts, one of them targeting **Amazon Data Firehose**, the streaming delivery service that lands records in storage and analytics destinations. Read the raw message delivery column as the discriminating one, because filter policies are a subscription attribute and work on every protocol without exception.

| Protocol | Delivers to | Raw message delivery | Filter policy | Selected by |
|---|---|---|---|---|
| `sqs` | An Amazon SQS queue, by ARN | Yes | Yes | Durable fan-out where each consumer needs its own buffer |
| `lambda` | A Lambda function, by ARN | No | Yes | Serverless reaction with no queue in between |
| `firehose` | A delivery stream, by ARN, using a subscription role | Yes | Yes | Archiving every published message for storage and analytics |
| `http` / `https` | A public URL, by JSON POST | Yes | Yes | A webhook into a third-party or on-premises system |
| `email` | An email address, as plain text | No | Yes | Human operational alerts, standard topics only |
| `email-json` | An email address, as JSON | No | Yes | A mailbox parsed by a script rather than read |
| `sms` | A phone number, through **AWS End User Messaging SMS** | No | Yes | Application-to-person alerts to a handset |
| `application` | A mobile app device endpoint, by endpoint ARN | No | Yes | Push notifications to iOS, Android or Kindle devices |

HTTP/S endpoints, email addresses and any endpoint in a different AWS account must confirm the subscription before they receive anything, and the confirmation token is valid for two days. Email subscriptions are standard topics only, cannot have their body customized, and are throttled at ten messages per second per subscription as a hard limit that cannot be raised. A Firehose subscription requires a `SubscriptionRoleArn` naming an IAM role that can write to the delivery stream, and an owner may attach at most five delivery streams to one topic.

Fan-out is the pattern the exams test most: several SQS queues subscribe to one topic so that each downstream system gets its own private copy of every message. The direction matters, since the queue subscribes to the topic, never the reverse. Amazon SNS is a push service with no polling API of its own, and Amazon SQS is a pull service with no way to reach out to a topic, so the only mechanism that exists is an SNS subscription whose endpoint is a queue ARN. The payoff is what the exam rewards. A direct subscription gets a fixed number of retry attempts and then the message is gone; a queue in the same position accepts the delivery in milliseconds, stores it durably across Availability Zones, and lets its consumer be offline for hours with its own retention, visibility timeout and dead-letter queue. Adding a consumer later is a new queue and subscription, with no publisher change.

One permissions detail makes or breaks the pattern: the queue's own access policy must allow the `sns.amazonaws.com` service principal to call `sqs:SendMessage`, conditioned on `aws:SourceArn` matching the topic ARN, because a subscription is not itself a grant. Across accounts, have the queue owner create the subscription, since a subscription created by the resource owner is confirmed automatically; if someone else creates it, the subscription sits in pending confirmation until a reader of the queue retrieves the `SubscribeURL` and confirms it.

## Message filtering and raw message delivery

By default every subscriber receives every message published to the topic, and a filter policy is how a subscriber narrows that down. The policy is a JSON object set as a subscription attribute, and the attribute `FilterPolicyScope` decides what it is matched against: `MessageAttributes`, the default, compares it against the message attributes, and `MessageBody` compares it against the payload, which must be well-formed JSON. Filtering happens at the topic before delivery, so a filtered-out message is never sent and never billed as a delivery, and routing logic lives with the subscriber rather than the publisher.

```json
{
  "store": ["example_corp"],
  "event": [{"anything-but": "order_cancelled"}],
  "price_usd": [{"numeric": [">=", 100]}]
}
```

The two scopes are not equivalent, and the differences decide questions. Attribute-based filtering compares only attributes of type `String` and `String.Array`, with `Number` supported for numeric values, ignores `Binary` attributes entirely, and does not accept a nested policy. Payload-based filtering does accept nesting, and for a nested policy only leaf keys count toward the key limit. Both share the same constraints: at most five keys, a total combination of values not exceeding 150, computed by multiplying the number of values in each array, a policy no larger than 256 KB, numeric matching from negative one billion to one billion, and case-sensitive string matching. An account may hold 200 filter policies per topic and 10,000 per account. Cost differs too, which is the reason not to reach for payload filtering by default: attribute-based filtering is free, while payload-based filtering is billed per GB of outbound payload scanned, counting filtered-out messages as well as delivered ones.

Raw message delivery is the other subscription attribute that changes what arrives. Left off, SNS wraps the message in a JSON envelope carrying `Type`, `MessageId`, `TopicArn`, `Subject`, `Timestamp`, `Signature` and `UnsubscribeURL`, and the subscriber has to parse that envelope to find the payload in the `Message` field. Setting `RawMessageDelivery` to true on an `sqs`, `http`, `https` or `firehose` subscription strips the envelope and delivers the published body as is. For HTTP/S endpoints SNS adds an `x-amz-sns-rawdelivery: true` header, and for both HTTP/S and Firehose, message attributes are not sent at all under raw delivery. For SQS subscriptions with raw delivery enabled, at most ten message attributes can be sent, and SNS discards a message carrying more as a client-side error. The exam cares because of migration: a consumer written against a queue expects the bare payload, so subscribing it to a topic without raw message delivery silently breaks its parser.

## Delivery retries, dead-letter queues, and archive and replay

Amazon SNS defines a delivery policy per protocol, and it retries only server-side errors: all 5XX responses and HTTP 429 are retryable, and everything else is a permanent failure. Client-side errors, which happen when SNS holds stale subscription metadata because the endpoint was deleted or its resource policy was changed to block the SNS service principal, are never retried at all. The two schedules that matter are far apart. For AWS managed endpoints, meaning AWS Lambda and Amazon SQS. Amazon Data Firehose sits between the two categories: its throttling errors follow the customer managed policy, SNS retries three times with no delay, twice one second apart, ten times with exponential backoff from one to twenty seconds, and then 100,000 times at twenty-second intervals, for 100,015 attempts over 23 days. For customer managed endpoints, meaning SMTP email, SMS and mobile push, it makes 50 attempts over six hours: two ten seconds apart, ten with exponential backoff from ten seconds to ten minutes, then 38 at ten-minute intervals. Only HTTP/S accepts a custom delivery policy, a JSON `healthyRetryPolicy` at the topic or subscription level with `minDelayTarget`, `maxDelayTarget`, `numRetries` up to 100 and a `backoffFunction`, and its total retry time is hard-capped at 3,600 seconds. The companion `throttlePolicy` with `maxReceivesPerSecond` protects a fragile HTTP server.

When the delivery policy is exhausted, or when the failure was a client-side error, SNS discards the message unless the subscription has a dead-letter queue. That attachment point separates this from the queue-level mechanism: an SNS dead-letter queue hangs off a subscription rather than the topic, so a topic with five subscribers can have five of them and you can tell from the queue alone which endpoint the message failed to reach. There is no `maxReceiveCount` here, because SNS is not counting receives; the trigger is a failed delivery. The queue must be an ordinary Amazon SQS queue in the same AWS account and Region as the subscription, its type must match the topic type, and an encrypted one must use a customer managed key whose policy grants the SNS service principal the KMS actions. Attach it with a `RedrivePolicy` subscription attribute naming the queue ARN, set the queue's retention to the 14-day maximum, and alarm on `ApproximateNumberOfMessagesVisible` rather than `NumberOfMessagesSent`, which does not count messages that arrive through a failure path.

FIFO topics add a second recovery tool that standard topics do not have. Setting an `ArchivePolicy` with a `MessageRetentionPeriod` of one to 365 days makes the topic keep a single copy of every published message in place, with no code and no second destination. A subscriber then sets a `ReplayPolicy` with `PointType` of `Timestamp`, a `StartingPoint` and an optional `EndingPoint`, and SNS redelivers the archived messages to that subscription; omitting the ending point replays forward until it catches up with live traffic. A replayed message keeps its original `MessageId` and `Timestamp` and gains a `Replayed` attribute, and a filter policy still applies. One caution: deactivating the archive policy deletes every archived message, which is why a topic with an active one cannot be deleted until it is turned off.

## Security, encryption and cross-account delivery

Access to a topic is granted by an identity-based policy on the caller in **AWS Identity and Access Management (IAM)**, the service that decides which principal may call which API, by a resource-based topic access policy, or by both. Within one account an identity policy is usually enough. Across accounts the topic policy must name the external principal, which is what makes cross-account fan-out work: the topic owner grants the other account `sns:Subscribe` on the topic, and the queue owner creates the subscription so that it confirms automatically. The security best practice AWS calls out first is to keep topics from being publicly accessible, meaning no `Principal` of `*` without a condition that scopes it, with a `Deny` on `sns:Publish` when `aws:SecureTransport` is false on top, forcing publishers onto HTTPS.

Server-side encryption protects messages at rest using **AWS Key Management Service (AWS KMS)**, the managed key service, and accepts symmetric keys only. Set `KmsMasterKeyId` on the topic to either the AWS managed key `alias/aws/sns` or a customer managed key. SNS reuses a data key for up to five minutes, which keeps KMS cost proportional to publishing principals rather than to message volume. Encryption covers the message body only, and not topic metadata, message metadata including the subject and the message attributes, or per-topic metrics, so sensitive values do not belong in attributes. A message is encrypted only if it was published after encryption was enabled, every request to an encrypted topic must use HTTPS and Signature Version 4, and a publisher needs `kms:GenerateDataKey*` and `kms:Decrypt` on the key.

Two key policy requirements catch people from the other direction. When an AWS service is the publisher, for example **Amazon CloudWatch**, the metrics, logs and alarms service, sending an alarm notification, the topic must use a customer managed key whose policy grants that service principal `kms:GenerateDataKey*` and `kms:Decrypt`; the AWS managed key cannot be used this way, and AWS recommends `aws:SourceAccount` and `aws:SourceArn` conditions against confused deputy attacks. And when SNS is the publisher into an encrypted Amazon SQS queue, the queue's customer managed key must grant `sns.amazonaws.com` those same two actions. Miss that one and the fan-out looks correctly configured while every delivery fails.

```json
{
  "Sid": "AllowSNSToUseThisKey",
  "Effect": "Allow",
  "Principal": {"Service": "sns.amazonaws.com"},
  "Action": ["kms:Decrypt", "kms:GenerateDataKey*"],
  "Resource": "*"
}
```

For the network path, an interface VPC endpoint powered by **AWS PrivateLink**, which exposes AWS services as private addresses inside **Amazon VPC**, the isolated virtual network service, lets an application in a private subnet publish to a topic without an internet gateway, NAT device or VPN. It covers publishing only: a VPC endpoint does not let you subscribe a private IP address. Cross-Region delivery is supported, but only to Amazon SQS queues and Lambda functions, and the `Subscribe` call must be made in the account and Region that hosts the topic. When either side is an opt-in Region, the subscribed resource's policy must name a regionalized service principal such as `sns.af-south-1.amazonaws.com` instead of the plain `sns.amazonaws.com`, and forgetting that is the most common cause of a cross-Region fan-out that silently delivers nothing.

One feature is closing. Message data protection, which scans messages in motion for personally identifiable information (PII) and protected health information (PHI) using managed or custom data identifiers, is no longer available to new customers as of April 30, 2026. Existing accounts with policies configured may keep using it, it works on standard topics only, and AWS now recommends a Lambda function subscribed ahead of the destination topic that calls **Amazon Bedrock** Guardrails, Bedrock being the managed service for foundation models, instead. Know what it does, because older exam scenarios describe it: an audit statement samples up to 99 percent of published data and writes findings to CloudWatch, S3 or Firehose, a de-identify statement masks or redacts without interrupting delivery, and a deny statement blocks the publish.

## Mobile push, SMS, pricing and the limits that matter

Application-to-person messaging is the half of SNS that talks to people rather than systems. For mobile push you register a platform application holding your credentials for one push service, and SNS supports Amazon Device Messaging, Apple Push Notification Service, Baidu Cloud Push, Firebase Cloud Messaging and the two Microsoft Windows push services. Each registered device returns a device token, from which SNS creates a platform endpoint, and you publish either directly to that endpoint ARN or to a topic the endpoints subscribe to with the `application` protocol.

SMS has changed and the current wiring matters. Amazon SNS SMS messages are now delivered by AWS End User Messaging SMS, the dedicated SMS and push channel service, and all origination identity work, meaning long codes, 10-digit long codes, toll-free numbers, short codes and alphabetic sender IDs, along with company registration and SMS billing, happens in that service rather than in SNS. Registration is not universally required, but it is required for some countries and some identity types, and several major markets including the United States, Canada and China do not support sender IDs at all, so a design that assumes an unregistered sender ID works worldwide is wrong. New accounts start in the SMS sandbox, which allows sending only to as many as ten verified destination phone numbers until you request production access. The default account spend threshold is 1.00 USD per month, and `SMSMonthToDateSpentUSD` is the metric to alarm on, because SNS stops publishing SMS within minutes of that quota being reached.

Pricing has two shapes, one per topic type, and both reward filtering early. A standard topic is billed on API requests, where every 64 KB chunk of a published payload counts as one request, so a single 256 KB publish is billed as four, with the first million requests each month free. Deliveries are then priced by endpoint type: mobile push, email, HTTP/S and Firehose each carry a per-notification price, while deliveries to Amazon SQS and Lambda carry only data transfer. A FIFO topic is billed on published messages plus subscription messages, where subscription messages are the number published multiplied by the number of subscriptions and filtered-out messages still count, plus a charge per GB of payload with every message rounded up to a minimum of 1 KB. Attribute-based filtering is free; payload-based filtering is billed per GB scanned. Archive and replay adds a per-GB processing charge and per-GB-month storage.

Monitoring is thin but pointed. In the `AWS/SNS` namespace, which is free, `NumberOfMessagesPublished` is the ingress signal, `NumberOfNotificationsDelivered` counts messages a subscription accepted, `NumberOfNotificationsFailed` counts those SNS gave up on, and `NumberOfNotificationsFilteredOut` tells you whether a filter policy is working as designed or quietly discarding everything.

## Professional depth

The multi-account shape of SNS is a central topic in a platform account with producers and consumers scattered across an organization. The topic access policy is the control point: grant `sns:Publish` to producing accounts and `sns:Subscribe` to consuming accounts, tightened with an `aws:PrincipalOrgID` condition so a mistyped account number cannot open the topic to the internet. Service control policies in **AWS Organizations**, the multi-account governance service, can then deny `sns:SetTopicAttributes` and `sns:AddPermission` outside a pipeline role so that topic policies cannot drift. The subtlety worth planning for is that a consumer account that subscribes its own queue gets an automatically confirmed subscription, while a central team that subscribes on the consumer's behalf leaves it pending until someone in the consumer account reads the queue and confirms it. Pending subscriptions are quota-bearing at 5,000 per account, and unconfirmed subscriptions are deleted after 48 hours, so a stalled bulk onboarding quietly loses its work.

Encryption multiplies across accounts rather than adding. A cross-account, encrypted fan-out has three policies that must agree: the topic policy admitting the publisher, the topic's KMS key policy granting the publisher `kms:GenerateDataKey*` and `kms:Decrypt`, and each subscribed queue's KMS key policy granting `sns.amazonaws.com` the same two actions. Those failures present differently. A missing topic policy statement fails the publish with an authorization error the publisher sees; a missing queue-side key grant fails the delivery, which the publisher never sees, because a successful `Publish` only means SNS accepted the message. That asymmetry is why `NumberOfNotificationsFailed` and a subscription-level dead-letter queue belong in every production fan-out.

Multi-Region and scale designs run into four hard edges. A topic is Regional with no global endpoint, so an active-active design deploys the same topic in each Region behind **Amazon Route 53**, the DNS service, health-based routing. Cross-Region delivery reaches only SQS and Lambda, and the opt-in Region service principal rule bites during expansions. AWS documents that a FIFO topic can see reduced throughput within a message group on cross-Region deliveries, because maintaining strict order across the added latency serializes the group, so a global ordered pipeline performs better as one FIFO topic per Region with an aggregation step. And the FIFO subscription limit of 100 per topic surprises teams migrating a broadcast workload, because the standard-topic answer of adding subscribers stops working two orders of magnitude earlier.

A Professional question extends the Associate one by adding a constraint that invalidates the obvious answer: three teams need the same event, so the Associate answer is fan-out to three SQS queues, and the Professional version puts the teams in three accounts with encrypted queues, making the answer that same topology plus the topic policy grant, the queue-side KMS key policy for the SNS service principal, and the queue owners creating their own subscriptions.

## Worked scenario

A logistics company publishes package status updates from a tracking service. Four systems need them: a billing service that must apply each status change to an invoice exactly once and in the order the events occurred per shipment, an analytics pipeline that wants everything landed in Amazon S3, a partner integration that consumes a webhook and only wants exception events, and an operations mailbox that should receive an email when a shipment is declared lost. Volume peaks at 4,000 events per second, and the payload carries a customer name, so the topics must be encrypted with a key the security team controls.

Ordering and the email requirement pull in opposite directions, so the design uses two topics. A FIFO topic with `FifoThroughputScope` set to `MessageGroup` carries the ordered path, with the shipment ID as the message group ID so that per-shipment sequence is preserved while thousands of shipments process in parallel and no single group approaches the 300 messages per second ceiling. A FIFO SQS queue subscribes for billing, with no filter policy so that exactly-once delivery holds, and a standard SQS queue subscribes for analytics, trading ordering for a cheaper queue and feeding a Lambda function that writes to S3. Both subscriptions carry a dead-letter queue of the matching type, with 14-day retention.

The partner webhook and the mailbox hang off a standard topic that the billing consumer publishes to after applying each change, because neither endpoint type is legal on a FIFO topic. The webhook subscription is `https` with a filter policy of `{"status": ["exception", "damaged", "lost"]}` on the default `MessageAttributes` scope, and raw message delivery is enabled so the partner's existing parser sees the bare JSON payload. A custom `healthyRetryPolicy` with a `maxReceivesPerSecond` throttle protects the partner's server, and a dead-letter queue catches anything left after the 3,600-second retry ceiling. The mailbox is an `email` subscription filtered to `{"status": ["lost"]}`, which keeps it inside the ten-messages-per-second hard limit. Both topics use a customer managed KMS key whose policy grants the tracking service's role `kms:GenerateDataKey*` and `kms:Decrypt`, and each subscribed queue's own key policy grants `sns.amazonaws.com` the same two actions, without which every delivery would fail while every publish succeeded.

The exam asks this scenario as a question about how to give the billing service exact ordering while still emailing the operations team, and the keyed answer is a FIFO topic with FIFO queue subscriptions for the ordered consumers plus a separate standard topic for the email. The two distractors that look right are one FIFO topic with an email subscription, which cannot be created at all, and one standard topic with an application-side sequence number, which meets the notification requirements and breaks the ordering one.

## Exam lens

- "Several independent teams need every message" maps to an SNS topic fanning out to one SQS queue per team; several consumers polling one shared queue is the distractor, because each message is consumed once, and the queues are what keep the work when a consumer is down, since the topic discards a message once its retries run out.
- "Messages must be processed in the order published and never duplicated" maps to a FIFO topic with FIFO queue subscriptions; a standard topic with deduplication logic in the consumer is the distractor that adds work and still cannot order.
- "The notification must also go to an email address or a phone number" rules out a FIFO topic entirely, because a FIFO topic delivers only to Amazon SQS queues.
- "Each subscriber should receive only the events it cares about" maps to a subscription filter policy, not to one topic per event type; attribute-based filtering is free, and payload-based filtering, selected by `FilterPolicyScope` of `MessageBody`, is the distractor that adds a per-GB scanning charge.
- "The consumer cannot parse the extra JSON wrapper" maps to enabling raw message delivery, available on SQS, HTTP/S and Firehose subscriptions only.
- "Capture the notifications that could not be delivered" maps to a dead-letter queue on the subscription with a `RedrivePolicy`; an SQS queue's own `maxReceiveCount` redrive policy is the distractor, because it governs consumption failures, not delivery failures.
- "Replay the last two days of events after a downstream bug" maps to a FIFO topic archive policy with a subscriber `ReplayPolicy`; a standard topic has no archive, and subscribing an Amazon Data Firehose delivery stream, which is the right answer for "store every message in S3 for compliance", is the distractor here because it cannot redeliver.
- "A topic in one account must deliver to a queue in another" maps to the topic policy granting `sns:Subscribe`, the queue policy allowing `sns.amazonaws.com` to `sqs:SendMessage`, and the queue owner creating the subscription so no confirmation is needed.
- "Publishes succeed but nothing reaches the encrypted queue" maps to the queue's customer managed KMS key policy missing `kms:Decrypt` and `kms:GenerateDataKey*` for the SNS service principal.

## Knowledge check

### 1. One event, four consumers (Associate)

A retailer publishes an order-placed event from its checkout service. An inventory service, a fraud service, a shipping service and an analytics pipeline each need every event. The services process at different speeds, and one of them is regularly offline for up to an hour during nightly maintenance. No event may be lost during that window, and the checkout service must not be changed when a fifth consumer is added later.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Publish each event to an Amazon SNS topic and subscribe a separate Amazon SQS queue for each service.
- **B)** Publish each event to an Amazon SNS topic and subscribe each of the four services as an HTTPS endpoint.
- **C)** Publish each event to an Amazon SQS queue and have all four services poll that queue.
- **D)** Have the checkout service write each event to four Amazon SQS queues in a single transaction.

<details><summary>Answer</summary>

**Answer: A.** A topic delivers a copy of every message to every subscription, and a queue per consumer gives each service its own durable buffer, so the service that is offline for an hour finds its events waiting. Adding a fifth consumer is a new queue and a new subscription with no publisher change. B loses events during the outage: an HTTP/S subscription's delivery policy defaults to three retries, and even a customized policy cannot retry for more than 3,600 seconds in total, after which SNS discards the message unless a dead-letter queue is attached. C fails because an SQS message is consumed once: four pollers on one queue split the events rather than each receiving all of them. D makes the publisher responsible for the subscriber list, which the stem forbids, and SQS has no cross-queue transaction.

*Where this is covered: Subscription protocols and the fan-out pattern.*

</details>

### 2. Ordered updates with an email alert (Associate)

A payments team publishes account balance changes. A settlement service must receive the changes for a given account in the exact order they were published and must not process a change twice. A second requirement was added late: the operations team wants an email whenever a balance goes negative. The team is designing the messaging layer now.

Which solution will meet these requirements?

- **A)** Create one Amazon SNS FIFO topic with an Amazon SQS FIFO queue subscription for settlement and an email subscription for the operations team.
- **B)** Create an Amazon SNS FIFO topic with an Amazon SQS FIFO queue subscription for settlement, and have the settlement service publish negative-balance alerts to a separate Amazon SNS standard topic that carries an email subscription with a filter policy.
- **C)** Create an Amazon SNS standard topic with an Amazon SQS FIFO queue subscription for settlement and an email subscription for the operations team.
- **D)** Create one Amazon SNS FIFO topic for each subscriber, each with its own Amazon SQS FIFO queue, and drain the second queue with an AWS Lambda function that sends the email.

<details><summary>Answer</summary>

**Answer: B.** A FIFO topic delivers only to Amazon SQS queues, both FIFO and standard, because AWS states that customer managed endpoints such as email addresses, phone numbers, mobile apps and HTTP/S endpoints cannot preserve strict ordering. Keeping the ordered path on a FIFO topic and routing the human alert through a separate standard topic satisfies both requirements. A cannot be created at all: the email subscription on a FIFO topic is rejected with an error. C loses the ordering and deduplication guarantees, because a standard topic makes only a best-effort attempt at order and delivers at least once. D would work, but it runs two FIFO topics and adds a Lambda function purely to send an email that a standard topic sends by itself, which is more to build and more to operate.

*Where this is covered: Standard topics compared with FIFO topics.*

</details>

### 3. A subscriber drowning in messages (Associate)

A company publishes about 30 million device telemetry messages per month to an Amazon SNS topic. A partner subscribes an HTTPS endpoint, but the partner only needs the roughly 200,000 messages per month whose `alarm_state` message attribute is `critical`. Today the partner receives every message and discards the rest, and both sides want to reduce cost and load.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Create a second Amazon SNS topic for critical messages and have the publisher decide which topic to use.
- **B)** Subscribe an AWS Lambda function that inspects each message and forwards the critical ones to the partner.
- **C)** Add a subscription filter policy of `{"alarm_state": ["critical"]}` and set the subscription's filter policy scope to `MessageBody`.
- **D)** Add a subscription filter policy of `{"alarm_state": ["critical"]}` to the partner's subscription, leaving the filter policy scope at the default.

<details><summary>Answer</summary>

**Answer: D.** The value being tested is already a message attribute, so the default `MessageAttributes` scope matches it, SNS evaluates the policy at the topic before delivery, and the 29.8 million non-matching messages are never delivered and never billed as HTTP/S notifications. Attribute-based filtering carries no charge. A pushes routing logic back into the publisher, which is the coupling SNS filtering exists to remove. B adds a Lambda invocation for every one of the 30 million messages, which is both the most expensive option and the most operational overhead. C reaches the same routing outcome but switches to payload-based filtering, which is billed per GB of outbound payload scanned, counting filtered-out messages too, so it costs more for no benefit.

*Where this is covered: Message filtering and raw message delivery.*

</details>

### 4. Deliveries that vanish (Associate)

An operations team subscribes an AWS Lambda function to an Amazon SNS topic. During a deployment the function was deleted and recreated with a new ARN, and the old subscription remained. Messages published during that window never arrived and were not recoverable. The team wants any future undeliverable message preserved for inspection, and wants to be alerted when it happens.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Configure a `RedrivePolicy` on the subscription that names an Amazon SQS queue in the same account and Region as the subscription.
- **B)** Increase the topic's delivery retry policy so that Lambda deliveries are retried for 30 days.
- **C)** Create a CloudWatch alarm on the dead-letter queue's `ApproximateNumberOfMessagesVisible` metric.
- **D)** Create a CloudWatch alarm on the dead-letter queue's `NumberOfMessagesSent` metric.
- **E)** Configure a redrive policy with a `maxReceiveCount` of 5 on the Amazon SNS topic.

<details><summary>Answer</summary>

**Answer: A and C.** A dead-letter queue attaches to an SNS subscription through a `RedrivePolicy` naming an ordinary SQS queue in the same account and Region, and it catches client-side errors such as a deleted endpoint as well as messages whose retry policy has been exhausted. Alarming on `ApproximateNumberOfMessagesVisible` is the documented approach because it reflects everything sitting in the queue. B does not help: a deleted function is a client-side error, which SNS never retries no matter how long the policy runs, and the Lambda delivery policy is AWS-defined and not customizable anyway. D is the trap: `NumberOfMessagesSent` counts only messages sent to the queue by a normal send, not messages that arrive through a failure path. E puts the setting in the wrong place and invents a parameter: `maxReceiveCount` belongs to an SQS queue's redrive policy and counts receive attempts, and an SNS dead-letter queue is attached to a subscription with no such counter.

*Where this is covered: Delivery retries, dead-letter queues, and archive and replay.*

</details>

### 5. Publishes succeed, nothing arrives (Professional)

A central events account owns an Amazon SNS topic encrypted with a customer managed AWS KMS key. A workload account owns an Amazon SQS queue encrypted with its own customer managed key. The queue owner has created the subscription, the topic policy grants the workload account `sns:Subscribe`, and the queue access policy allows the `sns.amazonaws.com` service principal to call `sqs:SendMessage` with an `aws:SourceArn` condition on the topic. Publishes return a message ID and succeed, but the queue stays empty and `NumberOfNotificationsFailed` is climbing.

Which solution will meet these requirements?

- **A)** Add a statement to the topic's KMS key policy allowing the `sqs.amazonaws.com` service principal to call `kms:Decrypt`.
- **B)** Re-create the subscription from the central events account so that the topic owner controls it.
- **C)** Add a statement to the queue's KMS key policy allowing the `sns.amazonaws.com` service principal to call `kms:Decrypt` and `kms:GenerateDataKey*`.
- **D)** Enable raw message delivery on the subscription so that the queue does not have to decrypt the SNS envelope.

<details><summary>Answer</summary>

**Answer: C.** To deliver into an encrypted queue, SNS must be able to generate and use a data key from the key that protects that queue, so the queue's customer managed key policy must grant the SNS service principal `kms:Decrypt` and `kms:GenerateDataKey*`. A successful `Publish` only means SNS accepted the message, which is why the failure shows up in `NumberOfNotificationsFailed` rather than in the publisher's response. A grants the wrong service on the wrong key; the queue never reads the topic's key. B makes matters worse: a subscription created by someone other than the queue owner sits in pending confirmation, which is why the queue owner creating it is the recommended pattern. D changes the message format only; the SNS envelope has nothing to do with encryption at rest on the queue.

*Where this is covered: Security, encryption and cross-account delivery.*

</details>

### 6. A FIFO migration that will not scale (Professional)

A trading platform migrated a broadcast feed to an Amazon SNS FIFO topic in US East (N. Virginia) with two Amazon SQS FIFO queues subscribed. Every publish uses a single constant message group ID because the original broker processed one message at a time. Volume has reached 2,500 messages per second at peak and publishers are being throttled. Ordering must still be preserved for messages about the same instrument, but messages about different instruments are independent.

Which solution will meet these requirements?

- **A)** Set `FifoThroughputScope` to `MessageGroup` on the topic and leave the message group ID unchanged.
- **B)** Set `FifoThroughputScope` to `MessageGroup` on the topic and change the publisher to use the instrument ID as the message group ID.
- **C)** Request a Service Quotas increase for subscriptions per FIFO topic.
- **D)** Replace the FIFO topic with a standard topic and have each consumer sort messages by the sequence number.

<details><summary>Answer</summary>

**Answer: B.** A FIFO topic caps throughput within any single message group at 300 messages per second, and high throughput mode spreads messages across partitions by hashing the message group ID, so a constant group ID cannot exceed one group's worth of capacity regardless of the topic setting. Distributing across instrument IDs both raises throughput and scopes ordering exactly as the stem requires. A leaves every message in one group and therefore one hash bucket, so the throttling continues. C addresses the wrong quota: two subscriptions is nowhere near the 100-subscription FIFO limit, and subscriptions are not what is throttling publishes. D discards the ordering guarantee, and a standard topic does not assign the 128-bit sequence number that FIFO topics place in the message body.

*Where this is covered: Standard topics compared with FIFO topics.*

</details>

### 7. Reaching an opt-in Region (Professional)

A company runs an Amazon SNS topic in Europe (Ireland), a Region that is enabled by default, and is expanding into Africa (Cape Town), an opt-in Region. A new Amazon SQS queue in Africa (Cape Town) must receive every message published to the Ireland topic. An engineer created the queue and added a queue access policy allowing the `sns.amazonaws.com` service principal to call `sqs:SendMessage`, and ran the `subscribe` command from the Africa (Cape Town) Region. The subscription appears in the console but no messages arrive.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Change the queue policy's principal to `sns.eu-west-1.amazonaws.com`.
- **B)** Change the queue policy's principal to `sns.af-south-1.amazonaws.com`.
- **C)** Run the `subscribe` command from the account and Region that hosts the topic, Europe (Ireland).
- **D)** Create a replica of the topic in Africa (Cape Town) and subscribe the queue to that replica instead.
- **E)** Enable raw message delivery on the subscription so that the queue accepts messages from another Region.

<details><summary>Answer</summary>

**Answer: B and C.** When cross-Region delivery involves an opt-in Region, the subscribed resource's policy must name a regionalized SNS service principal rather than the plain `sns.amazonaws.com`. AWS documents the direction explicitly: delivering from a Region that is enabled by default into an opt-in Region uses `sns.queue-region.amazonaws.com`, which for a queue in Africa (Cape Town) is `sns.af-south-1.amazonaws.com`. AWS also documents that the `subscribe` call must be made in the account and Region that host the topic. A applies the topic's Region, which is the principal for the opposite direction, an opt-in Region delivering to a default-enabled one. D is unnecessary work: SNS supports cross-Region delivery to SQS queues and Lambda functions directly, and there is no topic replication feature to build it with. E changes only the message format and grants nothing.

*Where this is covered: Security, encryption and cross-account delivery.*

</details>

### 8. Recovering from a downstream bug (Associate)

An insurer publishes policy change events to an Amazon SNS FIFO topic consumed by an Amazon SQS FIFO queue. A bug in the consumer silently mis-applied every event for a 40-hour window three days ago, and the queue has already been drained. The team has fixed the consumer and must reprocess exactly the events from that window, in order, without asking publishers to resend and without changing the other subscribers' behavior.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Subscribe an Amazon Data Firehose delivery stream to the topic so that future events land in Amazon S3, then replay from S3.
- **B)** Set an archive policy on the topic now and ask publishers to resend the affected events.
- **C)** Increase the source queue's message retention period to 14 days and use SQS dead-letter queue redrive to move the events back.
- **D)** Confirm that the topic has an archive policy covering that period, then set a `ReplayPolicy` on the consumer's subscription with `PointType` of `Timestamp` and starting and ending points bounding the window.

<details><summary>Answer</summary>

**Answer: D.** A FIFO topic with an archive policy keeps a copy of every published message in place for up to 365 days, and a subscriber replays a bounded window by setting a `ReplayPolicy` with a `Timestamp` starting point and an optional ending point. The replay targets one subscription, so the other subscribers are untouched, and no code is written. A only helps future events and still leaves the work of re-injecting them. B cannot recover the past: an archive policy set now captures nothing published before it, and the stem rules out asking publishers to resend. C confuses two mechanisms. SQS redrive moves messages from a dead-letter queue, and these events were processed and deleted rather than dead-lettered, so there is nothing to move, and retention does not resurrect deleted messages.

*Where this is covered: Delivery retries, dead-letter queues, and archive and replay.*

</details>

## Summary

Amazon SNS is a sequence of decisions that each close off options downstream. Pick the topic type first, because it cannot be changed and because a FIFO topic delivers only to Amazon SQS queues, which rules it out the moment a human endpoint appears; if you choose FIFO, pick a message group ID with many distinct values and set `FifoThroughputScope` to `MessageGroup` at creation, since that switch is one way and a single group caps at 300 messages per second. Then decide what sits behind the topic: a queue per consumer whenever work must survive a subscriber being down, because the topic retries and then discards. Push routing into subscription filter policies rather than the publisher, preferring attribute-based filtering, which is free, over payload-based, which is billed per GB scanned. Attach a dead-letter queue to every subscription that matters, remembering that it hangs off the subscription rather than the topic and has no `maxReceiveCount`. Finally, get the policies right in pairs: the topic policy with the topic's KMS key policy for publishers, and the queue policy with the queue's KMS key policy for the SNS service principal, because a publish that succeeds says nothing about a delivery that failed.

## Related units

- [Amazon SQS](sqs.md): the queue that sits behind a topic in fan-out, and the full comparison of SQS against SNS, EventBridge, Kinesis and Amazon MQ
- [Amazon EventBridge](eventbridge.md): content-based routing when the target set changes and the decision depends on fields inside the event
- [AWS Lambda](../02-compute/lambda.md): direct topic subscriptions, asynchronous invocation and the queue-triggered alternative for FIFO topics
- [AWS KMS](../07-security/kms-and-cloudhsm.md): symmetric customer managed keys, key policies and the service principal grants that encrypted fan-out depends on
- [Amazon Kinesis](../09-analytics/kinesis.md): Amazon Data Firehose as a topic subscriber for archiving and analytics
- [Amazon CloudWatch](../08-management/cloudwatch.md): alarm actions that publish to a topic, and the metrics and alarms that monitor delivery failures
- [Amazon VPC](../04-networking/vpc.md): interface endpoints and PrivateLink for publishing from private subnets
- [AppFlow, AppSync, Amplify, SES and Pinpoint](appflow-appsync-amplify-ses-pinpoint.md): where customer-facing email and campaign messaging belongs instead of SNS email subscriptions

## Sources

- [Subscribe API reference](https://docs.aws.amazon.com/sns/latest/api/API_Subscribe.html): the nine protocol values, the subscription attributes and the two-day confirmation token validity
- [Publishing large messages with Amazon SNS and Amazon S3](https://docs.aws.amazon.com/sns/latest/dg/large-message-payloads.html): the 256 KB maximum, the 2 GB extended payload and the Java and Python libraries
- [Amazon SNS message delivery for FIFO topics](https://docs.aws.amazon.com/sns/latest/dg/fifo-message-delivery.html): FIFO topics deliver only to SQS queues, and customer managed endpoints are rejected
- [Amazon SNS message ordering details for FIFO topics](https://docs.aws.amazon.com/sns/latest/dg/fifo-topic-message-ordering.html): per-subscriber ordering, the 128-bit sequence number and what raw delivery strips
- [Amazon SNS message grouping for FIFO topics](https://docs.aws.amazon.com/sns/latest/dg/fifo-message-grouping.html): the mandatory group ID, 300 messages per second per group and the advice to use many groups
- [Amazon SNS message deduplication for FIFO topics](https://docs.aws.amazon.com/sns/latest/dg/fifo-message-dedup.html): the five-minute interval, content-based deduplication excluding attributes and the at-most-once effect of filtering
- [High throughput FIFO topics in Amazon SNS](https://docs.aws.amazon.com/sns/latest/dg/fifo-high-throughput.html): `FifoThroughputScope`, automatic partitions and the one-way nature of the change
- [Amazon SNS subscription filter policy scope](https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering-scope.html): `MessageAttributes` as the default and `MessageBody` for payload filtering
- [Amazon SNS example filter policies](https://docs.aws.amazon.com/sns/latest/dg/example-filter-policies.html): the policy syntax, including `anything-but` and `numeric` operators, and the same policy against attributes or body
- [Filter policy constraints in Amazon SNS](https://docs.aws.amazon.com/sns/latest/dg/subscription-filter-policy-constraints.html): five keys, 150 combinations, 256 KB, 200 per topic, and the String and String.Array restriction
- [Amazon SNS raw message delivery](https://docs.aws.amazon.com/sns/latest/dg/sns-large-payload-raw-message-delivery.html): which protocols support it, the `x-amz-sns-rawdelivery` header and the ten-attribute limit on SQS
- [Amazon SNS message delivery retries](https://docs.aws.amazon.com/sns/latest/dg/sns-message-delivery-retries.html): the per-protocol retry table, the HTTP/S custom delivery policy and the 3,600-second ceiling
- [Amazon SNS dead-letter queues](https://docs.aws.amazon.com/sns/latest/dg/sns-dead-letter-queues.html): attachment at the subscription, same account and Region, and alarming on `ApproximateNumberOfMessagesVisible`
- [Configuring an Amazon SNS dead-letter queue for a subscription](https://docs.aws.amazon.com/sns/latest/dg/sns-configure-dead-letter-queue.html): the `RedrivePolicy` attribute and the queue policy for the SNS service principal
- [Amazon SNS message archiving for FIFO topic owners](https://docs.aws.amazon.com/sns/latest/dg/message-archiving-and-replay-topic-owner.html): the `ArchivePolicy`, one to 365 days, and deactivation deleting the archive
- [Amazon SNS message replay for FIFO topic subscribers](https://docs.aws.amazon.com/sns/latest/dg/message-archiving-and-replay-subscriber.html): `ReplayPolicy`, `PointType` of Timestamp and the `Replayed` attribute
- [Fanout Amazon SNS notifications to Amazon SQS queues](https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html): the push against poll contrast and the JSON envelope delivered to a queue
- [Sending Amazon SNS messages to an Amazon SQS queue in a different account](https://docs.aws.amazon.com/sns/latest/dg/sns-send-message-to-sqs-cross-account.html): automatic confirmation when the queue owner subscribes, and the `sns:Subscribe` grant
- [Sending Amazon SNS messages to an Amazon SQS queue or AWS Lambda function in a different Region](https://docs.aws.amazon.com/sns/latest/dg/sns-cross-region-delivery.html): SQS and Lambda only, opt-in Region service principals and where to run the subscribe call
- [Securing Amazon SNS data with server-side encryption](https://docs.aws.amazon.com/sns/latest/dg/sns-server-side-encryption.html): symmetric keys only, HTTPS and SigV4, and exactly what SSE does not encrypt
- [Managing Amazon SNS encryption keys and costs](https://docs.aws.amazon.com/sns/latest/dg/sns-key-management.html): the five-minute data key reuse, publisher permissions and event source service principals
- [Setting up Amazon SNS topic encryption with encrypted Amazon SQS queue subscription](https://docs.aws.amazon.com/sns/latest/dg/sns-enable-encryption-for-topic-sqs-queue-subscriptions.html): the queue key policy statement granting `sns.amazonaws.com`
- [Amazon SNS message data protection availability change](https://docs.aws.amazon.com/sns/latest/dg/sns-message-data-protection-availability-change.html): closed to new customers on April 30, 2026 and the recommended Lambda with Bedrock Guardrails alternative
- [Message data protection in Amazon SNS](https://docs.aws.amazon.com/sns/latest/dg/message-data-protection.html): audit, de-identify and deny operations, and standard topics only
- [Mobile text messaging with Amazon SNS](https://docs.aws.amazon.com/sns/latest/dg/sns-mobile-phone-number-as-subscriber.html): delivery through AWS End User Messaging SMS and where origination identity work now happens
- [Origination identities for Amazon SNS SMS messages](https://docs.aws.amazon.com/sns/latest/dg/channels-sms-originating-identities.html): long codes, 10DLC, toll-free numbers, short codes, sender IDs and where registration is required
- [Using the Amazon SNS SMS sandbox](https://docs.aws.amazon.com/sns/latest/dg/sns-sms-sandbox.html): ten verified destination numbers and the steps out of the sandbox
- [Sending mobile push notifications with Amazon SNS](https://docs.aws.amazon.com/sns/latest/dg/sns-mobile-application-as-subscriber.html): the supported push services, platform applications and device tokens
- [Amazon SNS endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/sns.html): topic, subscription, filter policy and message size quotas, and the Regional publish throughput table
- [Monitoring Amazon SNS topics using CloudWatch](https://docs.aws.amazon.com/sns/latest/dg/sns-monitoring-using-cloudwatch.html): the `AWS/SNS` metric list, one-minute intervals and the six-hour active window
- [Amazon SNS pricing](https://aws.amazon.com/sns/pricing/): the 64 KB request rule, per-endpoint delivery pricing, FIFO subscription messages and the payload filtering charge
- [Securing Amazon SNS traffic with VPC endpoints](https://docs.aws.amazon.com/sns/latest/dg/sns-internetwork-traffic-privacy.html): interface endpoints for publishing and the inability to subscribe a private IP address
- [Amazon SNS security best practices](https://docs.aws.amazon.com/sns/latest/dg/sns-security-best-practices.html): public access, least privilege and the `aws:SecureTransport` condition
- [Amazon SNS email subscription setup and management](https://docs.aws.amazon.com/sns/latest/dg/sns-email-notifications.html): standard topics only, the ten per second hard limit and bounce suppression
- [Fanout to Firehose delivery streams](https://docs.aws.amazon.com/sns/latest/dg/sns-firehose-as-subscriber.html): five delivery streams per topic per subscription owner and the backlog risk
