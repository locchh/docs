# Amazon EventBridge

**Where it sits on the exams.** **Amazon EventBridge** is the serverless event bus that receives events from AWS services, from your own applications and from software as a service (SaaS) partners, matches each event against rules you write, and delivers the matches to targets. It carries the event-driven half of SAA-C03 tasks 2.1 and 2.2 and it is the backbone of SAP-C02 tasks 3.1 and 4.4, because almost every "when this happens, automatically do that" scenario on either exam resolves to a rule on a bus. The rule of thumb the exam wants is that EventBridge decides at delivery time who should receive an event by reading the event's own contents, so adding a consumer is a rule you create on the bus rather than a change to the code that produced the event.

## Events, event buses and the CloudWatch Events inheritance

An event is a JSON document that records a change somewhere: an **Amazon EC2** instance, where EC2 is the virtual server service, moving to `running`, an **Amazon S3** object being created in the object storage service, an **AWS CloudTrail** API-call record from the service that logs API activity, or a message your own code publishes. Every event shares the same envelope, and the envelope is what a rule matches on. The fields are `version`, `id`, `detail-type`, `source`, `account`, `time`, `region`, `resources` and `detail`. The first eight are metadata that EventBridge or the producing service fills in; `detail` is the service-specific or application-specific body.

```json
{
  "version": "0",
  "id": "6a7e8feb-b491-4cf7-a9f1-bf3703467718",
  "detail-type": "EC2 Instance State-change Notification",
  "source": "aws.ec2",
  "account": "111122223333",
  "time": "2017-12-22T18:43:48Z",
  "region": "us-west-1",
  "resources": ["arn:aws:ec2:us-west-1:123456789012:instance/i-1234567890abcdef0"],
  "detail": {"instance-id": "i-1234567890abcdef0", "state": "terminated"}
}
```

An event bus is a router that receives events and delivers them to zero or more targets. Three kinds exist and the exam separates them cleanly. Every account gets a **default event bus** in every Region, and it is where AWS services automatically deliver their events; you do not create it and you cannot delete it. A **custom event bus** is one you create, and it is where your own applications should publish, because keeping application events off the default bus stops an AWS service event from accidentally matching an application rule and keeps rule counts manageable. A **partner event bus** is created when you accept a **partner event source** offered by a SaaS provider such as Datadog, Auth0 or Salesforce; the partner writes into the source, you match it to a custom bus in your account, and from then on it behaves like any other bus. You get 100 event buses per account per Region by default, and that quota is adjustable.

Your own code publishes with `PutEvents`, which accepts up to ten entries in one request with a total request size under 1 MB, and each entry must carry at least `Source`, `DetailType` and `Detail`. AWS's guidance for anything larger is to put the payload in an S3 bucket and send the object URL in the entry. Events from AWS services reach the bus either on a durable basis, meaning the service attempts delivery at least once, or on a best-effort basis, meaning that in rare cases an event might not arrive at all; the events reference names the level per service, and the difference matters when a design treats an event as the only record that something happened.

One naming point matters because both exam guides and most older material still use the old name. EventBridge was formerly called **Amazon CloudWatch Events**, and AWS describes the relationship as an evolution rather than a replacement: the default bus and the rules created under the old name appear in the EventBridge console, and EventBridge uses the same CloudWatch Events API, so existing code keeps working. That continuity shows in the spelling everywhere: the IAM namespace is still `events`, the metric namespace is still `AWS/Events`, and the CloudFormation resource is still `AWS::Events::Rule`. What changed is that new features, meaning partner events, the schema registry, Pipes and Scheduler, are added only to EventBridge. Treat "CloudWatch Events" in a question stem as a synonym for EventBridge, never as a separate service to choose between.

## Rules, event patterns and content filtering

A rule belongs to exactly one event bus and does two things: it says which events it wants, using an event pattern, and it names the targets that receive the matches. An event pattern is JSON with the same shape as the event it matches, and the values are always arrays of candidate matches. A pattern either matches an event or it does not, and one event can match many rules, each of which fires independently.

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {"state": ["terminated", "stopped"]}
}
```

The important property is that a pattern can match on the envelope and on the body at the same time: `source` and `detail-type` select the class of event, and fields inside `detail` narrow it to the instances you actually care about. Any field present in the event is fair game, which is why the routing decision can be as specific as a customer tier or an order value without the producer knowing anything about it. Omitting a field means the pattern does not constrain it, and a pattern of `{}` is invalid, so there is no way to write a rule that matches nothing by accident through emptiness.

Content filtering is where a plain equality pattern becomes a routing language, and the operators are worth memorizing because a stem often quotes one of them in English. `prefix` matches the start of a string value, `suffix` matches the end, and both accept an `equals-ignore-case` wrapper to make the comparison case-insensitive. `numeric` compares JSON numbers with `=`, `>`, `>=`, `<` and `<=`, and takes a pair of comparisons for a range, so `{"numeric": [">", 0, "<=", 5]}` is a half-open interval; numeric matching is limited to values between -5.0e9 and +5.0e9 inclusive with 15 digits of precision. `anything-but` inverts a match and can itself take a `prefix`, `suffix`, `equals-ignore-case` or `wildcard`. `exists` tests only for presence or absence of a field, and the documented trap is that it works on leaf nodes only, so `{"detail": {"state": [{"exists": true}]}}` is valid while testing whether `detail` itself exists is not. Beyond those five the same syntax gives you `equals-ignore-case`, `wildcard` with `*`, `cidr` for IPv4 and IPv6 ranges, `null`, the empty string, and `$or` for matching across several fields at once. Comparison operators work on leaf nodes, with `$or` and `anything-but` the exceptions. Listing several values in one array is an implicit OR, and listing several fields is an implicit AND.

Three quotas shape rule design. An event pattern is capped at 2,048 characters by default, an account gets 300 rules per event bus in most Regions, and only 30 rules per bus may contain wildcards, which is not adjustable. AWS also warns about recursion: a rule that reacts to a change by making the same kind of change fires itself again, and the resulting loop is billable, so patterns should be written tightly enough to exclude the actor's own writes. Finally, some AWS services create **managed rules** in your account for their own features. You can force-delete one, but the feature that depends on it stops working, so an unexplained rule on the default bus is usually not something to clean up.

## Targets, input transformers and API destinations

A target is whatever the rule invokes, and the number that decides questions is five: a rule can have at most five targets, and that quota cannot be raised. When a scenario needs a matched event to reach more than five places, the documented moves are to create several rules with the same event pattern, or to target one **Amazon SNS** topic, the publish and subscribe service that pushes a message to many subscribers at once, and fan out from there. The target list includes **AWS Lambda** functions, where Lambda is the serverless compute service that runs code without provisioned servers, **Amazon SQS** standard and FIFO queues, where SQS is the managed queue that holds messages until a consumer polls for them, **AWS Step Functions** state machines from the workflow service, **Amazon Kinesis Data Streams**, the managed streaming data service streams, **Amazon ECS** tasks in the container service, **Amazon API Gateway**, the managed API front door endpoints, another event bus, and the **AWS Systems Manager** automation, OpsItem and Run Command actions behind the remediation pattern. To call any of these, EventBridge assumes an IAM execution role you supply as the `RoleArn` on the target; the console creates it for you, the API does not.

By default the target receives the whole event. An **input transformer** changes that. You define an input path, which is a map of variable names to JSON paths into the original event, and an input template, which is the text actually sent, with `<variable>` placeholders filled in. Up to 100 variables are allowed, and five predefined ones are available without a path: `aws.events.rule-arn`, `aws.events.rule-name`, `aws.events.event.ingestion-time`, `aws.events.event` and `aws.events.event.json`. The transformer is what makes a target that expects a specific shape usable, which is why API destinations and API Gateway targets almost always need one, and it is also how you turn a machine event into a human sentence for a chat or paging endpoint.

Delivery is not guaranteed on the first attempt, so every target carries a retry policy and optionally a dead-letter queue, and both sit on the target rather than on the bus. By default EventBridge retries a failed delivery for 24 hours and up to 185 times with exponential backoff and jitter; you can set `MaximumEventAgeInSeconds` anywhere from 60 to 86,400 and `MaximumRetryAttempts` from 0 to 185. When both are exhausted the event is dropped, permanently, unless a dead-letter queue is attached. That queue must be a standard SQS queue, never a FIFO one, and it must be in the same Region as the rule. Some errors skip retries entirely and go straight to the queue: missing permissions, a target that no longer exists, or a DNS failure. Each dead-lettered message carries `RULE_ARN`, `TARGET_ARN`, `ERROR_CODE`, `ERROR_MESSAGE`, `EXHAUSTED_RETRY_CONDITION` and `RETRY_ATTEMPTS` as message attributes, which is enough to tell a permissions problem from a throttle without opening the payload.

**API destinations** extend the target list to anything that speaks HTTPS, including third-party SaaS APIs and private APIs of your own. A destination pairs an HTTPS endpoint and HTTP method with a **connection**, which holds the authorization method, one of basic, OAuth or API key, and stores the credentials as a secret in **AWS Secrets Manager**, the service that stores and rotates credentials, through a service-linked role. Connections can also reach private endpoints inside a VPC through **Amazon VPC Lattice**, the application networking service for connecting services across VPCs and accounts resource configurations. Two numbers matter operationally: each request must complete within five seconds or EventBridge times it out and retries it, and each destination has an invocation rate limit, 300 invocations per second by default and adjustable, which throttles rather than drops. AWS's own warning is that setting that rate far below the event rate builds a backlog that can exceed the 24-hour retry window, so an API destination in front of a slow partner belongs with a dead-letter queue.

## EventBridge Scheduler, scheduled rules and EventBridge Pipes

EventBridge can start work on a clock as well as on an event, and there are two ways to do it that a question will make you separate. The older one is a **scheduled rule**: a rule whose trigger is a `cron()` or `rate()` expression instead of an event pattern. Three limits define it. It can only be created on the default event bus, every expression is evaluated in UTC with no time zone support, and the finest resolution is one minute. AWS now labels scheduled rules a legacy feature and recommends the newer service for new work.

That newer service is **EventBridge Scheduler**, a separate, serverless scheduler with its own API and its own quotas. It adds everything the scheduled rule lacks: cron and rate expressions evaluated in any IANA time zone with automatic daylight saving adjustment, one-time invocations through an `at(yyyy-mm-ddThh:mm:ss)` expression, a flexible time window that spreads invocations over a period instead of firing them all on the minute, a per-schedule retry limit and event age, and a per-schedule IAM role. It also reaches further: templated targets cover the common SQS, SNS, Lambda and EventBridge calls, and a universal target parameter calls more than 270 AWS services and over 6,000 API operations directly. Scale is the other separation. A bus allows 300 rules, while Scheduler allows 10,000,000 schedules per Region by default, so "one schedule per customer" or "one reminder per order" is a Scheduler design and never a rule design, and one-time schedules keep counting until deleted. This is also where a delay longer than the 15 minutes an SQS delay queue allows belongs.

**Amazon EventBridge Pipes** solves a different problem from the bus. A bus is many-to-many: many sources in, many rules and targets out. A pipe is strictly point to point, one source to one target, with four stages: source, optional filter, optional enrichment, target. Its reason to exist is that it polls sources a bus cannot receive from. The supported sources are an **Amazon DynamoDB** stream from the NoSQL database service, a Kinesis Data Streams stream, an **Amazon MQ** broker from the managed ActiveMQ and RabbitMQ service, an **Amazon MSK** stream from the managed Kafka service, a self-managed or third-party Apache Kafka stream, and an SQS queue. The filter stage uses the same event pattern syntax as a rule, and you are billed only for events that pass it. The enrichment stage is a synchronous call out to a Lambda function, an API destination, API Gateway or a Step Functions Express workflow, and only Express, because the pipe waits for the response; the response is capped at 6 MB. If the source enforces order, the pipe preserves it end to end. The common composition is a pipe whose target is an event bus, which turns a stream or queue into bus events without any polling code of your own.

The **EventBridge Schema Registry** rounds out the developer side. It holds schemas in OpenAPI 3 or JSON Schema Draft 4 form across three default registries, all schemas, AWS event schemas and discovered schemas, alongside any custom registries you create for your own uploads, and it generates code bindings so a consumer can deserialize an event into a typed object. **Schema discovery** is the feature to know by name: turn it on for a bus and EventBridge infers a schema from the events flowing through it, versioning the schema when the shape changes. Two constraints appear in scenarios: discovery is not supported on a bus encrypted with a customer managed KMS key, and it ignores events larger than 1,000 KiB without raising an error.

## Archive and replay, and delivery across accounts and Regions

An **archive** is a durable copy of the events a bus received, and it exists so that they can be replayed later, either to recover from a bug that dropped work or to feed newly written consumers with real history. Each archive draws from exactly one source bus, which cannot be changed afterward, and you can create several archives per bus. An archive accepts an event pattern, so you can keep only the event types worth keeping, and a retention period in days, with the default being to keep events indefinitely. EventBridge encrypts archived events with AES-256 under an AWS owned key unless you choose otherwise.

A **replay** selects a time window from an archive and re-sends those events to the bus they came from, optionally restricted to specific rules. Four behaviors decide questions. Events can only be replayed to the source bus, never to a different bus or Region. A replayed event gains a `replay-name` metadata field, which a target can use to tell history from live traffic, and which EventBridge itself uses through an automatically created managed rule to stop replayed events from being archived again. Replays are not ordered: EventBridge works through the window one minute at a time, so a 20-minute window replays the first minute before the second, but nothing guarantees the order within. And you are limited to ten concurrent replays per account per Region, with replay records deleted after 90 days. AWS also advises waiting ten minutes before replaying recent events, because there is a lag between a bus receiving an event and the archive holding it.

Cross-account delivery is a resource policy on the receiving side and a role on the sending side. The receiving account attaches a resource-based policy to its event bus allowing `events:PutEvents` from a specific account, or from a whole organization through an `aws:PrincipalOrgID` condition using **AWS Organizations**, the multi-account governance service; the policy is capped at 10,240 characters by default, which is the reason an organization condition beats listing accounts. The sending account creates an ordinary rule whose target is the other account's bus ARN, and here is the requirement the exam keys on: every cross-account event bus target created since March 2, 2023 must specify an IAM role, and the console creates one automatically while the CLI and CloudFormation do not. Two more behaviors bound the design. Events do not hop twice: if a receiving account forwards events it received from a sender on to a third account, or a third bus in the same account, they are not delivered. And the sending account pays, as custom events, while the receiving account pays nothing.

Cross-Region works the same way, a rule in one Region targeting a bus ARN in another, with the caveat that the destination must be a supported cross-Region destination Region rather than any Region at all. For Regional resilience rather than routing, EventBridge offers **global endpoints**: you pair a bus of the same name in a primary and a secondary Region with an **Amazon Route 53** health check, Route 53 being the DNS and health-checking service, publish to the endpoint instead of to a bus, and custom events shift to the secondary Region within minutes of the health check turning unhealthy. With the alarm configuration AWS prescribes, both recovery time objective (RTO) and recovery point objective (RPO) land at 360 seconds with a maximum of 420. Enabling event replication, which sends every custom event to both Regions, costs more but is required for automatic failback.

## Choosing EventBridge against SNS and SQS

The full four-way comparison against SQS, SNS, Kinesis Data Streams and Amazon MQ belongs to the [Amazon SQS](sqs.md) unit, and nothing here contradicts it. The table below sharpens the three-way choice among the services that look most alike on the page, along the axes that actually decide an EventBridge question. Read the first row and the last row together, because what a service routes on is what its selecting wording describes.

| Property | Amazon SQS | Amazon SNS | Amazon EventBridge |
|---|---|---|---|
| What routes on | Nothing. The producer names the queue, and one consumer group drains it | The subscription list. Every confirmed subscriber gets a copy unless its filter policy excludes it | The content of the event. Rules on the bus evaluate every event and pick the targets |
| Filtering power | None. A consumer receives whatever is next | Filter policy on message attributes or the JSON payload, up to five keys and 150 value combinations | Event patterns on any envelope or `detail` field, with prefix, suffix, numeric, anything-but, exists, wildcard, cidr and `$or` |
| Delivery guarantee | At-least-once on a standard queue, exactly-once processing on a FIFO queue | At-least-once, retried for up to 23 days to AWS managed endpoints, then discarded or dead-lettered | At-least-once. A rule can rarely fire twice for one event. Retried 24 hours and 185 times by default, then dropped unless a target dead-letter queue exists |
| Ordering | Best-effort on standard, strict per message group ID on FIFO | Best-effort on standard, strict per message group ID on FIFO | None on a bus. There is no group ID, and a replay is not returned in archive order. Only Pipes preserves a source's order |
| Replay | None. A deleted message is gone; dead-letter queue redrive recovers failures only | FIFO topics only, archived up to 365 days and replayed per subscription | Any bus. An archive filtered by event pattern, retained indefinitely by default, replayed to the source bus |
| Wording that selects it | "must not lose work while the consumer is down", "buffer a burst", "process in order" | "notify several teams", "send an email and an SMS", "fan out the same message" | "route different event types to different targets", "react when an AWS service does X", "SaaS partner", "run on a schedule", "another account" |

Two follow-on rules cover most stems. First, these services compose rather than compete: EventBridge decides who cares, an SNS topic multiplies the message when the answer is many teams, and an SQS queue in front of each consumer keeps a slow or broken consumer from losing work, because a target dead-letter queue protects the last hop and not the consumer. Second, the exam's own coupling language sorts them. "Decouple" with "must survive the consumer being down" is a queue, "notify" several named recipients is a topic, and "react to" or "route based on" something inside the payload, or anything involving an AWS service's own events, a partner, a schedule or another account, is EventBridge. That last group is also the answer to the distributed design pattern question, because the producer never learns who consumes it and adding a consumer is a rule rather than a deployment.

## Pricing, monitoring and the limits that matter

EventBridge pricing has an unusual shape and the free part drives cost questions. AWS management events, meaning the control plane events that over 250 AWS services publish automatically to the default bus, are ingested for free, and there is no per-rule or per-bus charge, so an account that reacts only to AWS service events pays nothing for ingestion. What is billed per million events is everything else you put on a bus: custom events published with `PutEvents`, partner events, and AWS opt-in data events such as the S3 object-level events a bucket sends once you enable EventBridge notifications on it. On the delivery side, delivery to a service in the same account is free, while delivery to another event bus or to a service in a different account is billed per million. Payload size is counted in 64 KB chunks, so one 256 KB event bills as four. Around the bus, Scheduler bills per million invocations after 14,000,000 free each month, Pipes bills per million requests counted after filtering, API destinations bill per million invocations, archive bills per GB processed plus per GB-month stored with replayed events billed again as custom events, and the schema registry is free while schema discovery includes five million ingested events a month and bills per million after that.

Monitoring lives in the `AWS/Events` namespace with `EventBusName`, `RuleName` and `EventSourceName` as dimensions. Four metrics carry the diagnosis. `TriggeredRules` and `MatchedEvents` tell you a rule is matching at all, and a flat zero on a rule you expect to fire means the event pattern is wrong, which is far more common than a delivery problem. `FailedInvocations` counts invocations that failed permanently rather than ones being retried. `InvocationsSentToDlq` and `InvocationsFailedToBeSentToDlq` separate a target that is failing safely from one whose failures are being lost, usually because the dead-letter queue policy is wrong. `ThrottledRules` says you are hitting the Regional invocations ceiling, which ranges from 750 per second in smaller Regions to 18,750 in US East (N. Virginia), US West (Oregon) and Europe (Ireland) and is adjustable. `PutEvents` has its own, lower ceiling in each Region and its own throttle metric.

Encryption at rest uses an AWS owned key by default, with a customer managed key in **AWS Key Management Service (AWS KMS)**, the managed key service, as the alternative when a scenario asks for auditable key control. Choosing one turns off schema discovery on that bus and makes a bus-level dead-letter queue worth configuring, so that events failing to decrypt are not lost.

## Professional depth

Alerting and automatic remediation is the pattern SAP-C02 returns to, and EventBridge is its spine. A detective control emits an event, **AWS Config** reporting a resource as noncompliant, **Amazon GuardDuty** raising a threat finding, **AWS Health** announcing a scheduled retirement, or CloudTrail recording a specific API call; a rule matches the finding type and severity in `detail`; and the target is a Systems Manager Automation runbook that fixes the resource, or a Lambda function when no runbook fits. The input transformer maps the finding's resource ID into the runbook's parameter, and the rule's IAM role is what bounds the blast radius, so it should allow only the runbook and only on tagged resources. A dead-letter queue on the target is the difference between a remediation that silently stopped working and one that leaves evidence.

At organization scale that pattern becomes a hub. Each member account keeps a rule on its default bus whose target is the security tooling account's custom bus, carrying the required IAM role; the hub bus has a resource policy allowing `events:PutEvents` from the organization through `aws:PrincipalOrgID`, which is both shorter than an account list and self-maintaining as accounts join. Rules in the hub then fan the events to ticketing, a data lake and a paging endpoint. Remember the no-second-hop rule when designing this: the hub cannot forward what it received to a third account, so anything a third account needs must be republished there rather than routed through. Remember too that senders pay and the hub does not, which makes a chatty member account visible on its own bill.

Three quotas bite at scale. Five targets per rule cannot be raised, so a hub that grows past five consumers per event type needs duplicate rules or an SNS topic. Three hundred rules per bus sounds generous until every team writes its own; the way out is a smaller number of broader rules feeding per-team queues, not a quota increase. And the Regional invocations ceiling throttles rather than drops, so a burst of thousands of matching events per second in a smaller Region delays delivery in a way that looks like a broken target.

Two failure modes are worth recognizing on sight. A rule that matches nothing usually has a pattern written against the transformed event rather than the original, or an `exists` test placed on an intermediate node. And a bus encrypted with a customer managed key quietly disables schema discovery, which is what a bus-level dead-letter queue exists to catch.

## Worked scenario

A logistics company runs order intake on Lambda in a workload account, with fulfillment, billing and analytics owned by three other teams in three other accounts. Today the intake function calls all three synchronously and a slow billing API stalls order acceptance. The company also wants automatic remediation when a shipment tracker EC2 instance fails an instance status check, and it wants to replay a day of orders after a bug in the fulfillment consumer.

The redesign publishes one `OrderAccepted` event per order to a custom bus in the workload account with `PutEvents`, carrying the order value and the destination country in `detail`. Three rules on that bus match different patterns: fulfillment takes every order, billing takes only orders above a threshold using a `numeric` comparison, and analytics takes everything. Each rule targets the consuming account's own bus with the required IAM role, and each consuming bus has a resource policy scoped by `aws:PrincipalOrgID`. In each consuming account the rule's target is an SQS queue rather than the consumer itself, so a consumer outage buffers rather than dead-letters, and each cross-account target carries a dead-letter queue for the delivery itself. An archive on the workload bus keeps `OrderAccepted` events for 30 days, which is what makes the replay possible.

Separately, a rule on the default bus matches `aws.ec2` instance status events and targets a Systems Manager Automation runbook that reboots the tracker, with an SNS topic as a second target to page the on-call engineer.

The exam asks this as a question about adding a fourth consumer in a fifth account without touching the producer, and the keyed answer is a new rule on the existing bus targeting that account's bus with an IAM role, plus a statement or organization condition on the receiving bus policy. The distractor that looks right is adding a fifth target to the existing rule, which breaks at the five-target ceiling and also delivers the wrong events.

## Exam lens

- "Route different event types to different consumers based on the contents of the message" maps to EventBridge rules with event patterns; an SNS filter policy is the distractor when the stem never mentions event content beyond attributes.
- "React automatically when an AWS service does something" maps to a rule on the default event bus, because AWS service events arrive there with no configuration.
- "Ingest events from a third-party SaaS application" maps to a partner event source and its partner event bus; an API destination is the distractor, because it points outward.
- "Call a third-party REST API when an event occurs" maps to an API destination with a connection; a Lambda function written to call the API is the distractor that adds code AWS manages.
- "Run a task on a schedule, in local time, millions of times" maps to EventBridge Scheduler; a scheduled rule is the distractor because it is default-bus only, UTC only and capped at 300 rules.
- "Delay a message by more than 15 minutes" maps to EventBridge Scheduler, because an SQS delay queue stops at 15 minutes.
- "Enrich records from a DynamoDB stream before delivering them to one target" maps to EventBridge Pipes; a bus is the distractor, because it cannot poll a stream.
- "Reprocess the events from last Tuesday against a fixed consumer" maps to an archive and a replay to the source bus; a dead-letter queue is the distractor that holds only the failures.
- "Send events to a central security account" maps to a resource policy on the receiving bus plus an IAM role on the sending rule's target; the resource policy alone is the distractor since March 2023.
- "Events are matching but never arriving" maps to a target dead-letter queue and `InvocationsSentToDlq`; a longer retry policy is the distractor when the error is a permissions failure that skips retries.
- "One event must reach eight consumers" maps to several rules or an SNS topic as a target, because a rule allows five targets and that quota is fixed.
- "Must be processed strictly in order" never maps to EventBridge; it maps to a FIFO queue or a FIFO topic, because a bus has no message group ID.

## Knowledge check

### 1. Routing orders to the right consumers (Associate)

An online retailer publishes a JSON order document for every order it accepts. Three internal teams consume orders today and more teams are expected. Fulfillment wants every order, billing wants only orders above a currency threshold, and an export team wants only orders whose destination country is outside the domestic market. Both the order value and the destination country are fields inside the order JSON. The retailer must be able to add a fourth consumer later without changing the code that publishes orders.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Publish each order to an Amazon SNS topic and have each team subscribe with a filter policy that reads message attributes the publisher sets on every order.
- **B)** Write every order to one Amazon SQS standard queue and have each team's consumer read the queue and discard the orders it does not want.
- **C)** Publish each order to a custom Amazon EventBridge event bus and create one rule per team whose event pattern matches on fields inside `detail`.
- **D)** Write every order to an Amazon Kinesis Data Streams stream and have each team run a consumer application that filters the records it reads.

<details><summary>Answer</summary>

**Answer: C.** EventBridge picks targets by reading the event itself, so a rule can match a numeric comparison on the order value or a string in the destination country without the producer knowing who is listening, and a fourth consumer is a new rule rather than a producer change. A pushes the filtering decision back onto the publisher, which must set a message attribute for every field a future subscriber might want, and that is exactly the producer change the stem forbids. B fails the fan-out requirement outright: one queue is drained by one consumer group, so three teams cannot each receive every order. D gives every team the whole stream and makes each one write and operate filtering code, which is more overhead, not less.

*Where this is covered: Choosing EventBridge against SNS and SQS.*

</details>

### 2. Nightly reports in local time (Associate)

A retailer operates 4,000 stores spread across many time zones. Each store needs a summary report generated at 6:00 AM local time every day by invoking one AWS Lambda function with the store identifier as input. Daylight saving changes must be handled without anyone editing configuration twice a year. The company has no servers it wants to maintain for this.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create one Amazon EventBridge Scheduler schedule per store with a cron expression set to 6:00 AM in that store's IANA time zone, targeting the Lambda function.
- **B)** Create one EventBridge scheduled rule per store on the default event bus, with a cron expression adjusted to that store's offset from UTC.
- **C)** Create one EventBridge scheduled rule that runs every hour and invokes a Lambda function that works out which stores are due and invokes the report function for each.
- **D)** Run an Amazon EC2 instance in each Region with a cron daemon that invokes the Lambda function for the stores in its area.

<details><summary>Answer</summary>

**Answer: A.** EventBridge Scheduler evaluates cron expressions in any IANA time zone and adjusts for daylight saving automatically, and the default quota is 10,000,000 schedules per Region, so 4,000 schedules is unremarkable. B breaks twice: a scheduled rule is evaluated in UTC with no time zone support, so a fixed offset drifts every time a store's clocks change, and an event bus allows only 300 rules, far short of 4,000. C replaces a managed scheduler with dispatch logic the company has to write, test and maintain, and it still has to hold the time zone table somewhere. D adds servers to patch and scale for a job that needs no servers at all.

*Where this is covered: EventBridge Scheduler, scheduled rules and EventBridge Pipes.*

</details>

### 3. Eight consumers and a target that fails (Associate)

A company publishes `InvoiceIssued` events to a custom Amazon EventBridge event bus. Eight AWS Lambda functions, all in the same account and Region, must each receive every `InvoiceIssued` event. Separately, when EventBridge cannot deliver an event to one of those functions, the company needs the event kept along with the reason the delivery failed, so an engineer can inspect it the next morning.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Add all eight Lambda functions as targets of a single rule on the event bus.
- **B)** Create two rules on the event bus with the same event pattern and spread the eight Lambda functions across them.
- **C)** Configure an Amazon SQS standard queue in the same Region as the dead-letter queue on each target.
- **D)** Configure an Amazon SQS FIFO queue as the dead-letter queue on each target.
- **E)** Set `MaximumEventAgeInSeconds` to 86,400 on each target so that undelivered events are retained for a day.

<details><summary>Answer</summary>

**Answer: B and C.** A rule can carry at most five targets and that quota cannot be raised, so eight functions need at least two rules with the same event pattern, and each matching event fires both rules independently. A target dead-letter queue keeps what could not be delivered, and every dead-lettered message carries `ERROR_CODE`, `ERROR_MESSAGE`, `EXHAUSTED_RETRY_CONDITION` and `RETRY_ATTEMPTS`, which is the failure reason the team wants. A exceeds the five-target ceiling and cannot be created. D is not a valid configuration, because EventBridge dead-letter queues must be standard SQS queues. E only extends how long EventBridge keeps retrying; when that window closes the event is dropped and nothing is retained.

*Where this is covered: Targets, input transformers and API destinations.*

</details>

### 4. Replaying a day of dropped orders (Associate)

A company routes `OrderAccepted` events through a custom Amazon EventBridge event bus, with separate rules for fulfillment, billing and analytics. An archive on that bus keeps every `OrderAccepted` event for 30 days. A bug caused the fulfillment consumer to acknowledge Tuesday's events and then silently discard them. EventBridge delivered every one of those events successfully, so the fulfillment target's dead-letter queue is empty. The bug is fixed, and Tuesday's orders must be processed again by fulfillment only, without billing or analytics seeing them a second time.

Which solution will meet these requirements?

- **A)** Start a dead-letter queue redrive on the fulfillment target's dead-letter queue back to the event bus.
- **B)** Create a second event bus, replay the archive to that bus, and point the fulfillment rule at it.
- **C)** Write a script that reads Tuesday's events out of the archive and re-sends them with `PutEvents`.
- **D)** Start a replay from the archive for Tuesday's time window, restricted to the fulfillment rule.

<details><summary>Answer</summary>

**Answer: D.** A replay selects a time window from an archive and can be restricted to specific rules, which is exactly how you re-send Tuesday's orders to fulfillment without touching billing or analytics, and each replayed event carries a `replay-name` field so the consumer can tell history from live traffic. A has nothing to work with, because the deliveries succeeded and the dead-letter queue holds only delivery failures. B is not possible: archived events can only be replayed to the bus that originally received them, never to a different bus or Region. C rebuilds replay by hand and cannot be built anyway, since there is no API that reads individual events back out of an archive.

*Where this is covered: Archive and replay, and delivery across accounts and Regions.*

</details>

### 5. Enriching stream records before one target (Associate)

A manufacturer stores device records in an Amazon DynamoDB table with a stream enabled. Every change where the record's status becomes `faulted` must start one AWS Step Functions state machine. The state machine needs the device owner's contact details, which are not in the table and are only available from an internal REST API. Records with any other status must not start the state machine, and the company wants to write and operate as little code as possible.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create a rule on the default event bus whose event pattern matches the DynamoDB stream, with the state machine as the target and an input transformer that adds the contact details.
- **B)** Create an EventBridge pipe with the DynamoDB stream as the source, a filter that matches `faulted` records, an AWS Lambda function that calls the REST API as the enrichment, and the state machine as the target.
- **C)** Subscribe a Lambda function to the DynamoDB stream and have it filter the records, call the REST API and start the state machine.
- **D)** Turn on EventBridge schema discovery for the default event bus so that stream records become events, then create a rule that targets the state machine.

<details><summary>Answer</summary>

**Answer: B.** A pipe is the point-to-point path with exactly these four stages, a DynamoDB stream is a supported pipe source, the filter uses the same event pattern syntax as a rule and you are billed only for the events that pass it, and the enrichment stage makes a synchronous call to a Lambda function before the target is invoked. A cannot work on two counts: an event bus cannot poll a DynamoDB stream, and an input transformer only reshapes fields that are already in the event, so it cannot fetch contact details. C is the custom build of all three stages, which is the operational overhead the stem rules out. D misuses a real feature: schema discovery infers schemas from events already flowing through a bus and ingests nothing.

*Where this is covered: EventBridge Scheduler, scheduled rules and EventBridge Pipes.*

</details>

### 6. Findings from 300 accounts (Professional)

A company runs 300 AWS accounts in AWS Organizations and adds several more every month. Amazon GuardDuty findings raised in any member account must arrive on a custom Amazon EventBridge event bus in a central security account, where rules fan them out to ticketing and a data lake. Every resource is deployed with **AWS CloudFormation**, the infrastructure as code service and nobody uses the console. The design must keep working as new accounts join, without an engineer editing a policy each time.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Attach a resource-based policy to the security account's event bus that allows `events:PutEvents` with a condition on `aws:PrincipalOrgID`.
- **B)** Attach a resource-based policy to the security account's event bus that names all 300 member account IDs as principals.
- **C)** In each member account, create a rule on the default event bus that targets the security account's event bus, relying on the member account's identity-based policies for permission.
- **D)** In each member account, create a rule on the default event bus that targets the security account's event bus, and specify an IAM role on that target.
- **E)** In each member account, create an archive on the default event bus and replay it into the security account's event bus.

<details><summary>Answer</summary>

**Answer: A and D.** Cross-account delivery needs a resource-based policy on the receiving bus and a role on the sending target, and an organization condition covers every account that joins without an edit. The role matters here specifically: every cross-account event bus target created since March 2, 2023 must specify an IAM role, and the console creates one automatically while CloudFormation and the CLI do not, so a template that omits it produces a target that never delivers. B grants the same access today but must be edited for each new account, and the bus policy is capped at 10,240 characters, which an account list will eventually exceed. C omits the required role. E is impossible, because archived events can only be replayed to the bus they came from.

*Where this is covered: Archive and replay, and delivery across accounts and Regions.*

</details>

### 7. The hub that will not forward (Professional)

The same company acquires a subsidiary whose audit account belongs to a different AWS organization. That audit account must also receive the GuardDuty findings. An engineer created a rule on the security account's central event bus that targets the audit account's event bus, gave that target an IAM role, and added a statement to the audit account's bus policy allowing the security account. No events arrive. Messages in the security account's dead-letter queue carry an `ERROR_CODE` of `THIRD_ACCOUNT_HOP_DETECTED`.

Which solution will meet these requirements?

- **A)** Increase `MaximumRetryAttempts` and `MaximumEventAgeInSeconds` on the security account's target so the deliveries are retried for longer.
- **B)** Add the audit account as a principal on the security account's event bus resource policy so that it is allowed to receive the events.
- **C)** In each member account, add the audit account's event bus as a second target on the existing rule, with an IAM role on that target, and allow `events:PutEvents` on the audit account's bus for those member accounts.
- **D)** Create an archive on the security account's event bus and replay it into the audit account's event bus.

<details><summary>Answer</summary>

**Answer: C.** Events do not hop twice. A receiving account cannot forward events it received from a sender on to a third account, which is precisely what the error code reports, so anything the audit account needs has to be sent from where the events originate. Each member rule allows five targets and is using one, so adding a second target with its own role is the smallest change that works. A treats a structural rejection as a transient failure; no amount of retrying will deliver a blocked hop. B grants the wrong direction, since that policy controls who may put events onto the security bus, not where the security bus may send them. D cannot help, because a replay goes only to the source bus.

*Where this is covered: Professional depth.*

</details>

### 8. Targets that lag but never fail (Professional)

A company runs a custom Amazon EventBridge event bus in a Region whose default invocations quota is 750 per second. A nightly batch job produces several thousand matching events per second for about ten minutes. During that burst, targets run minutes behind the bus; afterwards they catch up and every event is eventually processed. No dead-letter queue receives anything, `FailedInvocations` stays at zero, and `ThrottledRules` is elevated for the length of the burst. The company needs the targets to keep up during the burst and must not lose any events.

Which solution will meet these requirements?

- **A)** Request an increase to the invocations per second quota for EventBridge in that Region through Service Quotas.
- **B)** Attach a standard Amazon SQS dead-letter queue to every target so that throttled events are captured rather than delayed.
- **C)** Split the rules across two additional custom event buses in the same account and Region so the burst is spread across three buses.
- **D)** Reduce `MaximumEventAgeInSeconds` on every target to 60 seconds so that backlogged events are not delivered late.

<details><summary>Answer</summary>

**Answer: A.** An invocation is an event matching a rule and being sent on to that rule's targets, and when the Regional ceiling is reached invocations are throttled rather than dropped, meaning they still happen but are delayed. That is exactly the reported symptom: nothing fails, nothing is dead-lettered, and `ThrottledRules` rises for the duration. The ceiling is adjustable, so a quota increase is the fix. B captures deliveries that failed permanently, and nothing here is failing, so the queue would stay empty. C does not help because the invocations quota applies per account per Region rather than per event bus. D discards work to make the lag disappear from the metrics, which breaks the requirement that no events are lost.

*Where this is covered: Pricing, monitoring and the limits that matter.*

</details>

## Summary

EventBridge is a sequence of routing decisions. Choose the bus first: the default bus for AWS service events, a custom bus for your own applications so their rules stay separate, and a partner event bus when a SaaS provider is the source. Then write the rule, because the event pattern is where the design lives: match the envelope to select a class of event and match inside `detail` with prefix, numeric, anything-but, exists or wildcard operators to narrow it to the instances that matter. Attach at most five targets per rule, add an input transformer where the target expects a particular shape, and give every target a retry policy and a standard SQS dead-letter queue, because a rule that matches is not a rule that delivered. Pick the right sibling for the job: Pipes when the source is a stream or queue that a bus cannot poll, Scheduler rather than a legacy scheduled rule whenever a schedule needs a time zone, a one-time run, or more than 300 of anything. Add an archive before you need a replay, and remember that cross-account delivery needs a resource policy on the receiver and a role on the sender.

## Related units

- [Amazon SQS](sqs.md): the four-way comparison against SNS, Kinesis and Amazon MQ, and the queue that buffers each consumer behind a rule
- [Amazon SNS](sns.md): the fan-out target when one event has to reach more than the five targets a rule allows
- [AWS Lambda](../02-compute/lambda.md): the most common EventBridge target, and the pipe enrichment that calls an API before delivery
- [AWS Step Functions](step-functions.md): Express workflows as pipe enrichments, and state machines as rule and pipe targets
- [Amazon Kinesis](../09-analytics/kinesis.md): the stream source a bus cannot poll and a pipe can
- [AWS Systems Manager](../08-management/systems-manager.md): Automation runbooks as the remediation target behind a detective control
- [Detection and compliance services](../07-security/detection-and-compliance-services.md): AWS Config and Amazon GuardDuty findings as the events most remediation rules match on
- [AWS Organizations, IAM Identity Center and Control Tower](../07-security/organizations-identity-center-and-control-tower.md): the `aws:PrincipalOrgID` condition that keeps a hub bus policy self-maintaining

## Sources

- [PutEvents API reference](https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_PutEvents.html): the 10 entry and under 1 MB limits on a single call
- [Schema discovery](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-schemas-infer.html): that discovery silently ignores events larger than 1,000 KiB
- [EventBridge schemas](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-schema.html): OpenAPI 3 and JSONSchema Draft 4 support and generated code bindings
- [Event delivery levels](https://docs.aws.amazon.com/eventbridge/latest/userguide/ref/event-delivery-level.html): which AWS services deliver durably and which are best effort

- [What Is Amazon EventBridge?](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html): event buses and pipes as the two ways to process events, and Scheduler alongside them
- [EventBridge is the evolution of Amazon CloudWatch Events](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cwe-now-eb.html): EventBridge was formerly called CloudWatch Events, uses the same API, and receives all new features
- [Creating Amazon EventBridge event patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html): a pattern has the same structure as the event, matches envelope and body fields together, and the recursive rule warning
- [Comparison operators for use in event patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-pattern-operators.html): the operator list, and that operators work on leaf nodes only, with `$or` and `anything-but` the exceptions
- [Amazon EventBridge quotas](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-quota.html): five targets per rule and not adjustable, 300 rules per event bus, 30 wildcard rules, 2,048 character patterns, 100 buses, the 10,240 character bus policy, and the per-Region invocations and PutEvents ceilings
- [Amazon EventBridge input transformation](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-transform-target-input.html): up to 100 variables, the input path and input template, and the five predefined `aws.events` variables
- [Using dead-letter queues to process undelivered events](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rule-dlq.html): standard SQS queues only, same Region as the rule, the message attributes including `ERROR_CODE` and `THIRD_ACCOUNT_HOP_DETECTED`, and the errors that skip retries
- [RetryPolicy](https://docs.aws.amazon.com/eventbridge/latest/APIReference/API_RetryPolicy.html): `MaximumEventAgeInSeconds` from 60 to 86,400 and `MaximumRetryAttempts` from 0 to 185
- [Troubleshooting Amazon EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-troubleshooting.html): EventBridge attempts delivery to a target for up to 24 hours
- [API destinations](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-api-destinations.html): the five second endpoint timeout, the 300 invocations per second default rate, credentials held in Secrets Manager, and the backlog warning when the rate is set too low
- [Creating a scheduled rule (legacy)](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html): scheduled rules are legacy, run on the default bus only, use UTC with no time zone support, and resolve to one minute
- [What is Amazon EventBridge Scheduler?](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html): templated and universal targets covering more than 270 services and over 6,000 API operations, flexible time windows and per-schedule retries
- [Quotas for Amazon EventBridge Scheduler](https://docs.aws.amazon.com/scheduler/latest/UserGuide/scheduler-quotas.html): 10,000,000 schedules per Region by default, adjustable, plus the request rate and invocation ceilings
- [Amazon EventBridge Pipes](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes.html): point-to-point source, filter, enrichment and target, and billing only for events that pass the filter
- [Amazon EventBridge Pipes sources](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-event-source.html): the six supported sources and the guarantee that a source's order is maintained end to end
- [Event enrichment in Amazon EventBridge Pipes](https://docs.aws.amazon.com/eventbridge/latest/userguide/pipes-enrichment.html): the four enrichment types, Express workflows only, synchronous invocation and the 6 MB response cap
- [Archiving and replaying events](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-archive.html): one source bus per archive, event pattern and retention, replay to the source bus only, ten concurrent replays, the `replay-name` field, one-minute replay intervals and the 90 day replay record life
- [Sending and receiving events between AWS accounts](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cross-account.html): the receiver's resource policy, the IAM role required on cross-account targets created after March 2, 2023, the no-second-hop rule, and that the sender pays
- [Making applications Regional-fault tolerant with global endpoints](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-global-endpoints.html): the Route 53 health check pairing, RTO and RPO of 360 seconds with a maximum of 420, and event replication as the requirement for automatic failback
- [Monitoring Amazon EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-monitoring.html): the `AWS/Events` namespace, the metric list including `ThrottledRules` and `InvocationsSentToDlq`, and the dimensions
- [Data protection in Amazon EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-data-protection.html): encryption at rest with an AWS owned key by default and a customer managed key as the alternative
- [Encrypting event bus events with a customer managed key](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-encryption-event-bus-cmkey.html): schema discovery is not supported on a bus encrypted with a customer managed key, and the bus-level dead-letter queue that catches decryption failures
- [Schema registries in Amazon EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-schema-registry.html): the three default registries for AWS, custom and discovered schemas
- [Amazon EventBridge pricing](https://aws.amazon.com/eventbridge/pricing/): AWS management events ingested free, custom, partner and opt-in data events billed per million, free delivery within an account, 64 KB payload chunks, the 14,000,000 free Scheduler invocations, and the archive and schema discovery charges
