# Integration

These services sit between application components so that the components do not
have to know about each other. **Amazon SQS** is a queue that holds messages
until a consumer is ready. **Amazon SNS** is a topic that pushes one message to
many subscribers. **Amazon EventBridge** is an event bus that routes on the
content of the event. **AWS Step Functions** is a state machine that holds the
progress of a multi-step process. **Amazon MQ** is a managed broker for
applications that already speak a standard messaging protocol and are not being
rewritten.

The decision the category keeps asking you to make is what kind of coupling the
scenario needs. A buffer, when a fast producer would otherwise overwhelm a slow
consumer or a failure would lose work: that is SQS. Fan-out, when one event has
several independent consumers: that is SNS, usually to SQS queues. Content-based
routing, when different events go to different targets and the set of targets
keeps changing: that is EventBridge. Durable state, when the process has ordered
steps, branches, retries and possibly a human approval: that is Step Functions.
Existing protocol, when the application speaks AMQP, MQTT, OpenWire or STOMP and
cannot be changed: that is Amazon MQ.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [sqs.md](sqs.md) | Choose standard against FIFO, set visibility timeout and polling, and handle failures with dead-letter queues | M |
| [sns.md](sns.md) | Build fan-out, filter subscriptions, and handle delivery failure | M |
| [eventbridge.md](eventbridge.md) | Write event patterns, route across accounts and Regions, and schedule with Scheduler and Pipes | M |
| [step-functions.md](step-functions.md) | Choose Standard against Express, use the service integration patterns, and handle errors | S |
| [amazon-mq.md](amazon-mq.md) | Decide when a managed broker beats a rewrite onto SQS and SNS | S |
| [appflow-appsync-amplify-ses-pinpoint.md](appflow-appsync-amplify-ses-pinpoint.md) | Recognize the SaaS, GraphQL, hosting and messaging services and what each replaces | XS group |

## Which exam tasks this serves

On SAA-C03 it is task 2.1 above all, which names queuing, publish/subscribe,
event-driven architecture and workflow orchestration in one task statement, plus
task 3.2 for decoupling so components scale independently. On SAP-C02 it is task
4.4 outright, which asks you to identify decoupling opportunities and select an
integration service, plus task 2.4 for loosely coupled dependencies. Step
Functions also carries the emerging-topics skill on human approval workflows for
AI operations.

## Reading order

Read `sqs.md` and `sns.md` first and in that order, because every later
comparison is written against them, then `eventbridge.md`, which is commonly
tested as an alternative to both. Then
`step-functions.md`, which is short but weighted above its length on SAP-C02.
Read `amazon-mq.md` last of the single-service units. An Associate-only
candidate can skim `appflow-appsync-amplify-ses-pinpoint.md`: its GraphQL, email
and mobile messaging services are in scope for SAP-C02 only, while its SaaS data
transfer and web hosting services appear on both in-scope lists.
