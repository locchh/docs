# Amazon CloudWatch

**Where it sits on the exams.** **Amazon CloudWatch** is the AWS monitoring and observability service: it stores time-series metrics, ingests logs, evaluates alarms, draws dashboards, and layers a set of application-level features on top of those four primitives to watch containers, functions, browsers and whole distributed systems. It owns SAA-C03 task 2.2, where workload visibility and choosing metrics from business requirements are named outright, and runs through SAP-C02 tasks 2.2, 2.5, 3.1 and 3.3, covering centralized monitoring, performance monitoring technologies, logging strategy, service level agreements and performance bottlenecks. The rule of thumb the exam wants is that CloudWatch records what a workload is doing, **AWS CloudTrail** records who called which API, and **AWS Config** records what a resource was configured to be: three different questions, three different services, and a stem that names one of them is never answered with another.

## What CloudWatch is and the signals it carries

CloudWatch is best understood as four stores with features built on them. Metrics hold numbers over time, logs hold text over time, traces held by **AWS X-Ray**, the distributed tracing service that follows one request across every service it touches, hold the path of a single request, and alarms watch a metric and act when it crosses a line. Everything else in the service, from canaries to container dashboards, writes into one of those stores or reads from it, which is why a question about a CloudWatch feature is almost always a question about which store the evidence lives in. The exam asks it by describing a symptom and expecting you to name the signal. Read the table by finding the sentence the scenario is really asking, then taking the feature in the third column.

| Signal | What it records | Where it lives | The question it answers |
|---|---|---|---|
| Metrics | Numeric values at a time stamp, with a namespace, a name and up to 30 dimensions | CloudWatch metrics, standard or high resolution | Is the system healthy right now, and is a threshold crossed |
| Logs | Text or JSON events from an application, an agent or an AWS service | CloudWatch Logs log groups and log streams | What exactly happened inside one component |
| Traces | The path of one request across services, as segments and subsegments | AWS X-Ray, surfaced in the CloudWatch console | Which hop in a chain of services spent the time or returned the fault |
| Real user telemetry | Page and screen load times, client-side errors, sessions, devices and geography | CloudWatch RUM | What actual browsers and mobile clients experienced |
| Synthetic checks | Scripted requests against an endpoint on a schedule, with screenshots and timings | CloudWatch Synthetics canaries | Does the endpoint still work when no customer is using it |
| Events and state changes | A JSON event when something in AWS changes state | **Amazon EventBridge**, the event bus that routes AWS and application events to targets | What just happened, so that something else can react to it |
| API call records | Who called which AWS API, from where, with which parameters, and whether it succeeded | AWS CloudTrail | Who did this, and when |
| Resource configuration | The settings of a resource at a point in time, its relationships, and its compliance with rules | AWS Config | What was this resource configured to be, and has it drifted |

The last three rows are where most of the exam's confusion lives, so learn the split precisely. CloudWatch stores numbers and text that a workload emits about its own behavior. AWS CloudTrail, the AWS service that records account activity as events, captures actions taken by a user, a role or an AWS service through the console, the CLI, the SDKs and the APIs; its Event history gives a searchable, immutable record of the past 90 days of management events at no charge, and a trail delivers the same events to **Amazon Simple Storage Service (Amazon S3)**, the object storage service, with optional delivery to CloudWatch Logs and EventBridge. AWS Config, the AWS service that records resource configuration and evaluates it against rules, captures a configuration item each time a supported resource is created, changed or deleted, keeps configuration history and relationships, and flags a resource noncompliant when it violates a rule. So "who deleted the security group rule" is CloudTrail, "which security groups had port 22 open last Tuesday" is AWS Config, and "the application returned 500 errors for nine minutes" is CloudWatch. The three chain together: CloudTrail delivers to a log group so a metric filter can alarm on a specific API call, and AWS Config notifies through EventBridge. Trails, data events and log file integrity validation are taught in [AWS CloudTrail](cloudtrail.md), and the Config recorder, rules, conformance packs and aggregators in [Detection and compliance services](../07-security/detection-and-compliance-services.md).

## Metrics, dimensions, and monitoring intervals

A metric is a time-ordered set of data points identified by three things together: a namespace, a metric name, and zero or more dimensions. A namespace is a container, and AWS services use the convention `AWS/service`, so **Amazon Elastic Compute Cloud (Amazon EC2)**, the service that rents virtual servers, publishes into `AWS/EC2`. A dimension is a name and value pair that is part of the identity of the metric, and CloudWatch treats each unique combination of dimensions as a separate metric even when the name is the same. That one sentence explains both how you slice data and how you accidentally create a very large bill: publishing `OrderLatency` with a `RequestId` dimension creates one metric per request.

Metrics live only in the Region where they are created, cannot be deleted, and expire automatically after 15 months with no new data. Retention is tiered, and the tiers decide what a post-incident review can still see: data points with a period under 60 seconds are kept for 3 hours, at 60 seconds for 15 days, at 300 seconds for 63 days, and at 3,600 seconds for 455 days. Short-period data is aggregated for long-term storage rather than discarded, so one-minute data stays at one-minute resolution for 15 days, is then retrievable only at five-minute resolution, and after 63 days only at one-hour resolution. One-minute granularity from four months ago is therefore impossible in CloudWatch metrics, which is the architectural reason to stream metrics out to a data lake.

Resolution is the other axis. Metrics produced by AWS services are standard resolution, meaning one-minute granularity. A custom metric can be published as **high-resolution metrics**, stored at one-second granularity and readable at periods of 1, 5, 10 or 30 seconds or any multiple of 60. Those are the only valid periods, the default is 60, and sub-minute periods mean anything only for metrics actually stored at one-second resolution.

The interval at which a service publishes is a separate question from resolution, and EC2 is the case the exam tests. Under **basic monitoring**, which is the default and carries no charge, EC2 status check metrics arrive in one-minute periods and every other metric arrives in five-minute periods. Under **detailed monitoring**, which you enable per instance at launch or afterward and which is charged per metric sent, all metrics arrive in one-minute periods. This decides alarm design directly: AWS states that an alarm period must be at least as long as the metric's resolution, so an alarm on a basic-monitoring EC2 metric needs a period of at least 300 seconds. Status checks are the exception that causes confusion: they publish every minute under basic monitoring, yet the console requires detailed monitoring to offer a one-minute period when you build a recover alarm, so plan for detailed monitoring whenever the recovery time objective depends on a one-minute alarm. The two-evaluation-period, one-minute recover alarm that AWS recommends for `StatusCheckFailed_System` requires detailed monitoring. Not every service behaves like EC2. **Amazon Elastic Block Store (Amazon EBS)**, the network-attached block storage service, sends one-minute metrics for every volume type at no charge, but only while the volume is attached to an instance, which is exactly why an alarm on an unattached volume drifts into `INSUFFICIENT_DATA`. **Elastic Load Balancing**, the managed service that spreads traffic across healthy targets, **AWS Lambda**, the service that runs code without servers to manage, and **Amazon DynamoDB**, the managed key-value and document database, publish without any detailed monitoring option to buy, so "enable detailed monitoring" is a distractor when the resource in the stem is not an EC2 instance.

Statistics are aggregations over a period: `Average`, `Sum`, `Minimum`, `Maximum`, `SampleCount` and percentiles. Percentiles answer a different question from an average. AWS's own framing is that an average hides anomalies and a maximum is skewed by one, so the 95th percentile shows the tail customers actually feel. Percentile statistics are available for **Amazon API Gateway**, the managed API front door, Elastic Load Balancing, EC2, **Amazon Kinesis Data Streams**, the managed streaming data service, Lambda and **Amazon Relational Database Service (Amazon RDS)**, the managed relational database service, and for any custom metric where you publish raw data points rather than a pre-aggregated statistic set. Percentiles are unavailable when any metric value is negative. Metric math lets you build expressions across metrics, which is how an error rate becomes a single series: divide a 5XX count by a request count and alarm on the ratio rather than on either raw count, so that a traffic spike does not read as an outage and a quiet hour does not hide one.

## Custom metrics, the embedded metric format, and the agent

Anything CloudWatch does not publish for you, you publish yourself, and there are three ways to do it. The direct route is the `PutMetricData` API, which accepts a namespace, a metric name, dimensions, a value and an optional time stamp. A time stamp may be up to two weeks in the past and two hours in the future, and if you omit it CloudWatch uses arrival time. Alarms evaluate against the current time in UTC, so a skewed clock is the standard cause of an alarm that sits in `INSUFFICIENT_DATA` or fires late. A new metric takes up to two minutes before statistics can be retrieved. To declare one-second resolution, set the storage resolution to 1 on the call.

```bash
aws cloudwatch put-metric-data --namespace Checkout \
  --metric-name OrdersFailed --value 1 --unit Count \
  --storage-resolution 1 --dimensions Environment=prod
```

Two publishing habits decide whether the design scales. Publishing zero rather than nothing for a quiet period keeps the series continuous, because an alarm on a metric that stops reporting behaves very differently from one reporting zero. And when a process produces many observations a minute, send a statistic set with `Sum`, `Minimum`, `Maximum` and `SampleCount` in one call rather than one call per observation, which collapses the request charge. The trade is that a statistic set destroys percentiles: CloudWatch needs raw data points to compute them. If p99 latency matters, publish raw values.

The second route is the embedded metric format, the answer the exam wants whenever the scenario mentions high-cardinality context or an ephemeral compute environment. You write a structured JSON log event carrying both the metric values and the rich fields around them, and send it to CloudWatch Logs with `PutLogEvents` or through the agent. CloudWatch automatically extracts the metrics, so you get alarmable metrics and the detailed log line that explains them in one write, with no second API call and no `cloudwatch:PutMetricData` permission required, only `logs:PutLogEvents`. AWS positions it for generating actionable custom metrics from ephemeral resources such as Lambda functions and containers, where instrumenting a metrics client and flushing it before the process dies is awkward. The warning AWS attaches is a favorite exam trap: if you extract metrics on a high-cardinality dimension such as a request identifier, the embedded metric format will by design create a custom metric for every unique dimension combination, and the bill follows.

The third route is the **CloudWatch agent**, which is how anything running on a server gets into CloudWatch at all. It is a single agent for Linux, Windows Server and macOS, installed on EC2 instances and on-premises servers, that collects system-level metrics, collects logs, retrieves application metrics over the StatsD and collectd protocols, and in recent versions collects traces and enables Application Signals without a separate daemon. Its default namespace is `CWAgent`. The metrics it collects are billed as custom metrics.

What the agent sees is the point the exam tests hardest. The hypervisor can measure what it hands the instance, so EC2 natively publishes CPU utilization, disk operations against instance store volumes, network bytes and packets, and the status checks. It cannot see inside the guest operating system, so memory utilization, swap usage, free disk space, inode counts, per-process state and TCP connection counts are simply absent from the `AWS/EC2` namespace. The agent supplies exactly those: `mem_used_percent`, `swap_used_percent`, `disk_used_percent`, `disk_free`, `disk_inodes_free`, `processes_running` and `netstat_tcp_established` on Linux and macOS, and the Windows Performance Monitor counters on Windows Server. Any scenario that says "alarm when memory exceeds 80 percent" or "alert before the log volume fills the disk" is an agent answer, and "enable detailed monitoring" is the distractor, because a one-minute interval on a metric that does not exist changes nothing. The older, Linux-only CloudWatch Logs agent is deprecated and no longer supported, and the legacy Perl monitoring scripts that once filled the memory and disk gap are no longer documented: AWS's page for them now redirects to the unified agent, which is the only answer to give.

## Turning business requirements into metrics

SAA-C03 asks you to identify metrics from business requirements, and SAP-C02 asks you to translate business requirements into measurable metrics and to connect them to service level agreements and key performance indicators. The method is the same in both: name the user-visible promise, pick the one number that proves it, choose the statistic that cannot hide a failure, then decide the window over which the promise is measured.

Start from the promise, not from the dashboard. "The checkout page must respond in under 300 milliseconds for almost everyone" is a latency indicator measured as p99, not `Average`, because an average over thousands of fast requests conceals a slow tail that is somebody's abandoned cart. "The API must succeed 99.9 percent of the time" is a ratio built with metric math as faults divided by requests, not a raw 5XX count, because a count moves with traffic and a ratio does not. "No order may wait more than five minutes" is queue age rather than queue depth, because depth says how much work exists and age says how long the oldest piece has waited. "The service must survive the loss of an Availability Zone" is the count of healthy hosts per zone behind the load balancer, because that number tells you whether the redundancy you paid for still exists.

Then set the window, where an availability target becomes an alarm configuration. CloudWatch alarms take a period, a number of evaluation periods and a number of datapoints to alarm, which together express an M out of N rule: three breaching datapoints out of the last five one-minute periods is a very different promise from one out of one. A tight rule catches an outage quickly and pages on every blip; a loose rule is quiet and slow. Application Signals, the CloudWatch feature that instruments applications and tracks them against goals, formalizes the same arithmetic as a service level objective: a service level indicator such as `Latency` or `Availability`, a threshold, an attainment goal expressed as a percentage, and an interval that is either calendar-aligned or rolling. From those it derives an error budget, the amount of breaching time or the number of bad requests the interval can absorb and still meet the goal, and a burn rate, which expresses how fast the budget is being consumed relative to the baseline error rate of one hundred percent minus the goal. A burn rate above 1 means the goal is at risk; below 1 means it will be beaten. That vocabulary is how a Professional stem turns "our SLA is 99.9 percent monthly availability" into a monitoring design rather than a slogan, and it is why the right answer to "how do we know whether we are on track" is an error budget, not another dashboard.

## Alarms, missing data, and alarm actions

An alarm watches one metric, or the result of a math expression over metrics, and is always in exactly one of three states. `OK` means the metric is within the threshold, `ALARM` means it is outside, and `INSUFFICIENT_DATA` means the alarm lacks enough recent data to decide, which happens when an alarm is new, when the metric has not reported, or when the resource is idle. `INSUFFICIENT_DATA` is not an error condition and is not a breach, and treating it as one is the most common design mistake the exam punishes.

Actions fire on a state change, not on a state. An alarm sitting in `ALARM` for an hour sends one notification, not sixty, and the only exception AWS documents is an Auto Scaling action, re-invoked once per minute while the state persists. Evaluation uses three settings together: the period, the number of evaluation periods, and the number of datapoints to alarm. Setting datapoints to alarm below evaluation periods gives an M out of N alarm, so 2 out of 3 trips when two of the last three periods breach. CloudWatch deliberately retrieves more data points than the evaluation periods, a window called the evaluation range, so real data is preferred over filled-in data whenever enough exists.

Dashboards assemble these into the view an audience actually needs, and the exam distinguishes two audiences: an operational dashboard carrying latency percentiles, error rates and saturation for the on-call engineer, and a business dashboard carrying the outcome metrics leadership funds. A dashboard can be Regional or cross-Region, can be shared publicly or with named principals, and its widgets can query metric math, Logs Insights and alarm states together. A high-resolution alarm evaluates at 10 or 30 seconds, or any multiple of 60 seconds, and the sub-minute periods carry a higher per-alarm charge. Missing data is configured per alarm, with four options. `notBreaching` treats a gap as good, `breaching` treats it as bad, `ignore` keeps the current state, and `missing` transitions to `INSUFFICIENT_DATA` when every data point in the evaluation range is missing. `missing` is the default. The choice follows the metric's nature: a metric that reports continuously, where silence means something broke, deserves `breaching`; a metric that emits only on failure, such as DynamoDB's `ThrottledRequests`, deserves `notBreaching`. One namespace overrides the global default: alarms on metrics in `AWS/DynamoDB` default to `ignore` rather than to `missing`. AWS makes one recommendation explicitly: for EC2 alarms that stop, terminate, reboot or recover an instance, treat missing data as `missing` and act only on `ALARM`, because status check metrics can briefly go missing on a healthy instance and a reporting hiccup should not terminate a server.

There are three alarm shapes to choose between, and a stem usually names the one it wants by describing the threshold. Read the table by deciding first whether you can write down a number.

| Alarm type | How the threshold is set | How it evaluates | Actions it can take | Correct when |
|---|---|---|---|---|
| Static threshold metric alarm | You supply a fixed number and a comparison operator | Compares each period's statistic to the number, over evaluation periods and datapoints to alarm, applying the missing data setting when real data is short | SNS notification, EC2 Auto Scaling policy, EC2 stop, terminate, reboot or recover, Systems Manager OpsItem or incident, Lambda function | A real limit exists: a queue depth, a disk percentage, a provisioned capacity, a documented latency budget |
| Anomaly detection alarm | You supply a band width in standard deviations; CloudWatch learns the expected range from the metric's own history | Compares the value to a model-generated band and alarms above it, below it, or either side; the model trains on up to two weeks of data and accounts for hourly, daily and weekly seasonality and for trend | The same actions as a static threshold alarm | The normal value moves with time of day or day of week, so any fixed number is either noisy at night or blind at peak |
| Composite alarm | You supply a rule expression over other alarms, using `ALARM`, `OK` and `INSUFFICIENT_DATA` functions joined by `AND`, `OR` and `NOT`, with parentheses | Goes to `ALARM` only when the whole expression is satisfied; child alarms keep their own states and may keep their own actions | SNS notification, Systems Manager OpsItem or incident, investigation. It cannot perform EC2 actions or Auto Scaling actions | Several individually noisy alarms should page only when they are true together, or notifications must be suppressed while a known parent condition is in alarm |

Three details in that table decide questions on their own. Anomaly detection applies to a metric math expression as well as a raw metric, and the model is specific to one metric and one statistic, so a model built on `Average` says nothing about `p99`. A composite alarm can notify through Amazon SNS or invoke a Lambda function, but not take the EC2 or Auto Scaling actions a metric alarm can. A composite alarm is the documented way to reduce alarm noise: create the metric alarms without notifications and notify only from the composite. And a composite alarm can carry an actions suppressor: a nominated alarm whose `ALARM` state silences the composite's actions, bounded by a wait period, the longest the composite will wait for the suppressor to enter `ALARM`, and an extension period, the longest it will wait after the suppressor leaves it. That is how a maintenance window or a known upstream failure stops a hundred downstream pages.

Alarm actions are where monitoring turns into automatic recovery, which is what SAP-C02 task 2.2 means by proactively recovering from system failures. An alarm can publish to **Amazon Simple Notification Service (Amazon SNS)**, the managed publish and subscribe messaging service, which fans out to email, to a queue, or to a Lambda function that runs a remediation. It can invoke a scaling policy on **Amazon EC2 Auto Scaling**, the service that keeps a group of instances at the right size, or invoke a Lambda function directly. It can create an OpsItem or an incident in **AWS Systems Manager**, the operations management service, which is how an alarm opens a ticket with a runbook attached. And it can act on the instance itself: stop, terminate, reboot, or recover. The recover action has rules worth memorizing. It works only with `StatusCheckFailed_System`, never with `StatusCheckFailed_Instance`, because a system status check failure means the host is impaired and AWS must move the instance. A recovered instance keeps its instance ID, private and Elastic IP addresses, public IP address and all metadata, but in-memory data is lost because it reboots onto new hardware. Reboot is the right action for an instance status check failure, and AWS warns against giving reboot and recover alarms the same number of evaluation periods, because they will race.

## CloudWatch Logs: groups, retention, and filters

CloudWatch Logs stores log events, each a timestamp plus a raw UTF-8 message. Events from one source form a log stream, and streams are grouped into a log group, which is the unit that carries retention, monitoring configuration and access control; there is no limit on streams per group. Logs arrive from the CloudWatch agent, from `PutLogEvents` calls, and automatically from many AWS services, including Lambda function output, API Gateway execution and access logs, and CloudTrail when a trail is configured to deliver there.

Retention is the setting that most often decides a cost question, because the default is that log data is stored indefinitely. Retention is set per log group from a fixed list of values in days: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288 and 3653. Clearing the retention policy returns the group to never expiring. Expired events are marked for deletion and typically removed within 72 hours, and stop accruing storage charges as soon as they are marked. An organization that has never set retention is paying to store every log line it has ever written, which is why "reduce CloudWatch Logs cost" is answered first by a retention policy and second by moving long-term copies to Amazon S3, where storage is far cheaper and lifecycle rules can tier it further.

The log class is the second cost lever. The Standard class is full-featured. The **Infrequent Access log class** costs less to ingest, keeps the same storage and query pricing, and supports managed ingestion and storage, cross-account features, encryption with **AWS Key Management Service (AWS KMS)**, the managed key service, most Logs Insights commands, export to Amazon S3 and sensitive data masking. What it does not support is the list that decides the answer: no metric filters, no subscription filters, no embedded metric format, no Live Tail, no field indexing, no Container Insights or Lambda Insights ingestion, and no `GetLogEvents` or `FilterLogEvents`. A log group's class cannot be changed after creation, so Infrequent Access is right for compliance archives you will occasionally query and wrong for anything you alarm on.

A metric filter turns text into a number. You attach a filter pattern to a log group, name a metric and namespace, give a metric value, and every matching event increments the metric, which you can then alarm on like any other. Set a default value of 0 so quiet periods report zero rather than a gap, which keeps alarm evaluation sane. Two constraints matter: filters are never retroactive, so they only publish for events that arrive after the filter is created, and adding dimensions to a metric filter both creates a separate metric per unique value extracted and makes a default value impossible. Metric filters are the standard way to alarm on a log line that no metric covers, such as a specific CloudTrail API call or an application's fatal error string.

A subscription filter turns a log group into a real-time feed. Matching events are delivered base64-encoded and gzip-compressed, usually in under three minutes, to Kinesis Data Streams, to **Amazon Data Firehose**, formerly Kinesis Data Firehose, the managed streaming delivery service, or to a Lambda function, and a built-in integration streams them to **Amazon OpenSearch Service**, the managed search and analytics service. Each log group can have up to five subscription filters, and each account can have one account-level subscription filter per Region, which is how one rule captures every log group in an account without touching each one. Cross-account delivery works through a destination created in the receiving account with an access policy naming the sending accounts, which is the classic pattern for centralizing logs into a security account. If the destination returns a retryable error, CloudWatch Logs retries for up to 24 hours; a non-retryable error such as access denied disables the filter for up to ten minutes and those logs are skipped. The choice between the two filters is the exam's real question: a metric filter counts and alarms, a subscription filter moves the data somewhere else for processing or storage, and a stem that says "stream log data to a third-party SIEM" or "process each log event as it arrives" is always a subscription filter.

## Logs Insights, data protection, and cross-account observability

**CloudWatch Logs Insights** is the query engine over log groups, and it is how a Professional question about finding a bottleneck in log data gets answered without exporting anything. It supports three query languages: a purpose-built Logs Insights query language, OpenSearch Piped Processing Language, and OpenSearch SQL, which can join across log groups. Fields are discovered automatically from AWS service logs and from any application log emitted as JSON, and every event carries `@timestamp` and `@message`. Queries time out after 60 minutes, results are kept for 7 days, and an account may run 100 concurrent Logs Insights queries plus 15 concurrent OpenSearch PPL or SQL queries. Charging is by uncompressed data scanned, so field indexes and a tight time range make a query cheap, and Live Tail streams matching events as they arrive.

```
fields @timestamp, @message, duration
| filter status >= 500
| stats count(*) as errors, pct(duration, 99) as p99 by bin(5m)
| sort errors desc
```

A **data protection policy** keeps sensitive values from the people reading logs. You select managed data identifiers covering credentials, financial data, personally identifiable information, protected health information and device identifiers, or write custom identifiers, and CloudWatch Logs audits and masks matches at every egress point, including Logs Insights, metric filters and subscription filters. Only a principal holding the `logs:Unmask` permission sees the raw value. Policies can be set for a single log group or for the whole account, and when both exist both apply. Detection happens at ingestion, so events written before the policy existed are never masked, and a `LogEventsWithFindings` metric in the `AWS/Logs` namespace lets you alarm on the discovery itself. Masking works in both the Standard and Infrequent Access classes.

**CloudWatch dashboards** are the shared view, and they are the one CloudWatch object not confined to a Region: a single dashboard can graph metrics from several Regions and, with cross-account observability, from several accounts on the same widget. **Metric streams** continuously deliver metric updates through Amazon Data Firehose to Amazon S3 or a partner endpoint, in JSON or OpenTelemetry format and filtered by namespace, which is how a company keeps one-minute data past 15 days or feeds a third-party platform.

**Cross-account observability** is the feature a multi-account question is asking for, and the mechanics are worth knowing exactly. A monitoring account holds a sink, one per Region per account. Each source account creates a link to that sink, and the link is managed by the source account, so access is removed from the source side. The shareable telemetry types are metrics, log groups, X-Ray traces, and Application Signals services and service level objectives, and both ends choose which types they share: if the source account selects more types than the monitoring account accepts, link creation fails. Setup is through the console or the Observability Access Manager API, and AWS recommends linking through **AWS Organizations**, the multi-account governance service, so accounts created later are onboarded automatically. A monitoring account can link up to 100,000 source accounts, and a source account can share with up to five monitoring accounts. From the monitoring account you graph source-account metrics, create alarms on them, and run one Logs Insights query across log groups in many accounts at once. The limits that catch people are that cross-account composite alarms are not supported and that cross-account alarms cannot use the `ANOMALY_DETECTION_BAND`, `INSIGHT_RULE` or `SERVICE_QUOTA` math functions. Sharing logs and metrics carries no extra charge.

## Application observability: Insights, canaries, and RUM

The features above this line watch infrastructure. The features below it watch applications, and the exam distinguishes them by what is being instrumented.

Container Insights collects and summarizes metrics and logs from containerized workloads on **Amazon Elastic Container Service (Amazon ECS)** and **Amazon Elastic Kubernetes Service (Amazon EKS)**, the AWS container orchestrators, and on self-managed Kubernetes on EC2, including clusters running on **AWS Fargate**, the serverless compute engine for containers. It uses a containerized CloudWatch agent to discover containers and writes performance log events in the embedded metric format, from which CloudWatch aggregates metrics at cluster, node, pod, task and service level, plus diagnostics such as container restart failures. Billing differs by version: the original Container Insights charges the metrics and logs as custom metrics and log ingestion, while Container Insights with enhanced observability for Amazon EKS charges per observation. Lambda Insights does the same job for functions through a Lambda extension layer that emits one performance log event per invocation carrying CPU time, memory, disk and network, plus cold starts and worker shutdowns.

Application Signals is the layer above both. It automatically instruments Java, Python, Node.js and .NET applications using **AWS Distro for OpenTelemetry (ADOT)**, the AWS-supported OpenTelemetry distribution, and produces standard `Latency` and `Availability` metrics, an automatically discovered application map, and the service level objectives described earlier. It is supported and tested on Amazon EKS, Amazon ECS and EC2, and can be enabled for Lambda. It absorbed the job the older ServiceLens console feature did of stitching metrics, logs and traces together: AWS has combined the X-Ray service map and the ServiceLens map into one trace map in the CloudWatch console, and the application map now replaces the service map. Do not confuse it with **CloudWatch Application Insights**, a separate and still-current feature that configures monitoring for packaged application stacks.

CloudWatch Synthetics runs canaries: scripts in Node.js, Python or Java that run on a schedule as Lambda functions in your account and exercise an endpoint the way a customer would. Node.js and Python canaries drive a headless browser through Playwright, Puppeteer or Selenium, so a canary can log in, click through a checkout, take screenshots and fail on a visual difference; Java canaries have no browser. They run as often as once per minute, publish into the `CloudWatchSynthetics` namespace with a `CanaryName` dimension, can run inside a VPC to test private endpoints, and appear on the trace map when X-Ray active tracing is on. Canaries answer "is it broken when nobody is using it", which makes them the keyed answer for an overnight availability requirement and for validating a remediation. CloudWatch RUM answers the opposite question, collecting client-side data from real sessions: page and screen load times, client errors, crashes, user journeys, and breakdowns by device, browser and geography. You create an app monitor, add the generated code snippet, and choose what percentage of sessions to sample; telemetry is retained for 30 days and can be copied to a log group to keep it longer. Note that **CloudWatch Evidently**, the feature launch and A/B experimentation feature that sat alongside RUM, reached end of support on 17 October 2025, and AWS directs feature-flag launches to **AWS AppConfig**, a feature of AWS Systems Manager.

**Contributor Insights** is the high-cardinality tool. You write a rule naming the log fields that identify a contributor, and CloudWatch analyzes matching events in real time to report the top contributors, the number of unique contributors and their usage: the busiest source IP addresses, the URLs producing the most errors, the DynamoDB partition keys taking the most capacity. Built-in rules exist for several AWS services, and charging is per matching log event. Contributor Insights answers who or what is causing a problem rather than whether there is one.

## AWS X-Ray and distributed tracing

AWS X-Ray is what SAA-C03 means by workload visibility. Metrics tell you that latency rose; traces tell you which of the eleven services in the request path caused it. The compute running your code emits a segment describing the host, the request, the response, the work done and any errors, and breaks that work into subsegments for downstream calls to AWS services, external HTTP APIs or SQL databases. Every segment carrying the same trace ID forms a trace, and X-Ray combines traces into a service graph, rendered as the trace map, with a node per service and an edge per call. For services that do not emit their own segments, such as DynamoDB, X-Ray infers a segment from the caller's subsegment so the dependency still appears.

Four details decide questions. Sampling: by default the SDK records the first request each second plus five percent of additional requests, deliberately conservative to control cost, and you override it with sampling rules that trace every state-changing call while sampling health checks at a trivial rate. Propagation: the first X-Ray-integrated service to see the request adds an `X-Amzn-Trace-Id` header carrying the root trace ID, the parent segment ID and the sampling decision, and every downstream hop passes it on, which is why one uninstrumented service in the middle breaks the chain. Annotations against metadata: annotations are key-value pairs that X-Ray indexes, up to 50 per trace, so you can filter traces by them, while metadata can hold any structure but is not searchable. Use an annotation for a customer identifier you will search on and metadata for a payload you only want to read. Retention: trace data and service graph data are kept for 30 days, so tracing is a troubleshooting tool, not an archive.

Instrumentation reaches X-Ray through the X-Ray SDKs, which send UDP segments to the X-Ray daemon for batched upload, or through OpenTelemetry with ADOT; recent CloudWatch agent versions accept traces from either and forward them, removing the separate daemon. Lambda, API Gateway REST APIs and several other services add tracing headers or run the daemon for you, which is why "enable active tracing" is often a checkbox rather than a deployment.

## Pricing shape, quotas, and the open-source options

CloudWatch pricing has a free tier covering basic monitoring metrics from AWS services at no charge, plus a small allowance of custom metrics, alarms, dashboards, API requests and log data. Beyond it, four dimensions dominate a real bill. Custom metrics are billed per metric per month on a descending tiered scale, and a metric is one unique combination of namespace, name and dimension values, so one published with an instance dimension across a thousand hosts is a thousand billable metrics. `PutMetricData` requests are billed per request beyond the free allowance, which is why statistic sets and the embedded metric format save money. Log ingestion is billed per gigabyte and is usually the largest line item, with storage per gigabyte-month and Logs Insights per gigabyte scanned. Alarms are billed per metric per alarm, with higher rates for high-resolution alarms, a flat rate for composite alarms, and an anomaly detection alarm costing three metrics because it evaluates the value and both band edges. The levers follow: cut dimension cardinality, set log retention, choose Infrequent Access for archives, use composite alarms instead of dozens of notifying alarms, and move long-term data to Amazon S3 for querying with **Amazon Athena**, the serverless query service for data in Amazon S3.

The quotas worth carrying in: a metric accepts up to 30 dimensions; alarms have no count limit but an evaluation period ceiling of seven days for periods of an hour or more and one day for shorter periods; a log group accepts five subscription filters and an account one account-level subscription filter per Region; Contributor Insights allows 100 rules per account per Region; Application Signals allows 250 service level objectives per Region; a sink accepts 100,000 links while an account may create only five links and one sink per Region; and alarm history is kept for 30 days.

When CloudWatch is not the answer, two managed services take over. **Amazon Managed Grafana** is a fully managed Grafana that you run as workspaces, with built-in connectors to CloudWatch, X-Ray, Amazon OpenSearch Service and Amazon Managed Service for Prometheus as well as many open-source, third-party and other-cloud sources, and authentication through AWS IAM Identity Center or any SAML 2.0 provider. It is priced per active user in a workspace. Choose it when teams already have Grafana dashboards, when panels must combine AWS data with on-premises or another cloud's data, or when a single pane must span data sources CloudWatch dashboards cannot reach. Amazon Managed Service for Prometheus is a serverless, Prometheus-compatible metric store for container environments, replicated across three Availability Zones in a Region, ingesting through Prometheus remote write or managed scrapers, queried with PromQL, and retaining metrics for 150 days by default and up to 1,095 days by configuration. Choose it when a team already runs Prometheus exporters and PromQL alerting rules on Amazon EKS or self-managed Kubernetes and does not want to rewrite them as CloudWatch metrics; the common pairing is Managed Service for Prometheus for storage and Managed Grafana for display, with CloudWatch still carrying the logs and alarms.

## Professional depth

At organization scale there are two different centralization problems and they have two different answers. If the requirement is that an operations team can see and query telemetry that stays where it is produced, the answer is cross-account observability: one monitoring account, a sink, links created from every source account through an Organizations-wide template so new accounts onboard themselves, and shared telemetry types agreed at both ends. Nothing is copied, there is no extra charge for logs and metrics, and Logs Insights queries span accounts. If instead the requirement is that log data must physically land in a security or archive account, under that account's retention and key policies, the answer is subscription filters delivering to a cross-account destination, or an account-level subscription filter so no team can create a log group that escapes the pipeline. The two are complementary, and a Professional stem that says "without moving the data" or "without changing each workload account" is pointing at the first while "must be retained in the audit account for seven years" is pointing at the second.

Cardinality is the failure mode that arrives with scale rather than with a mistake. A dimension that looked harmless in one account becomes thousands of billable metrics across fifty, and because metrics cannot be deleted the only remedy is to stop publishing and wait 15 months. The same trap sits inside the embedded metric format and inside metric filters with dimensions. Design the dimension set deliberately: keep identifiers you alarm on as dimensions, and push identifiers you investigate into log fields, where Contributor Insights and Logs Insights reach them without creating a metric each.

Alarm noise is the other scale problem, and composite alarms are the documented cure. Build the metric alarms without notification actions, express the real operational condition as a rule over them, and notify only from the composite; then attach an actions suppressor driven by a maintenance or upstream-dependency alarm so a planned change does not page anyone. Remember the boundaries: a composite alarm's underlying alarms must be in the same account and Region as the composite, so in a monitoring account you build the composite over alarms created there that watch source-account metrics, and a composite alarm cannot take EC2 or Auto Scaling actions, so automatic remediation stays on the metric alarm in the workload account. Remember too that Auto Scaling actions are re-invoked every minute while the state persists, unlike every other action which fires once per state change.

Hybrid and migration scenarios turn on three facts. The CloudWatch agent installs on on-premises servers as well as EC2, so a data center fleet can publish the same in-guest metrics and logs during a migration and be compared against its cloud target on one dashboard. Metric retention rolls up as it ages, so comparing one-minute data across a migration window longer than 15 days needs a metric stream into Amazon S3. And a team arriving with a Prometheus and Grafana estate should usually keep it: Amazon Managed Service for Prometheus takes the remote write and PromQL rules unchanged and Amazon Managed Grafana takes the dashboards, which is a far smaller rewrite than re-expressing every exporter as a custom metric.

Testing a remediation is its own discipline, and the Professional exam asks for it directly. Establish the baseline before the change: a canary on the affected user journey gives a controlled, continuous measurement that real traffic cannot, because it runs on a fixed schedule from fixed locations whether or not customers are active. Express the regression as an alarm with an M out of N evaluation so that a single noisy data point neither declares victory nor raises a false alarm. Apply the change to one Availability Zone, one Region or one weighted target group first, and compare the canary and service metrics against the untouched remainder rather than against yesterday. Metric math over the two populations makes that comparison explicit, and CloudWatch retains one-minute data for fifteen days and alarm history for thirty days, so a before-and-after comparison at that resolution has to be taken while the window is open or exported first. Recommend the change only when the canary, the service metric and the business metric all move the right way, because a fix that improves latency while lowering conversion is not a fix.

## Worked scenario

A retailer runs a storefront across three AWS accounts in one Region: a web account with containers on Amazon ECS behind a load balancer, a services account with Lambda functions and a DynamoDB table, and a security account. The business contract is 99.9 percent monthly availability and a 300 millisecond p99 page latency. Overnight traffic is almost nil, a previous outage went unnoticed for 40 minutes, and log retention has never been set.

The design starts with signals. The ECS cluster gets Container Insights, the functions get Lambda Insights, and both tiers use Application Signals through ADOT, producing `Latency` and `Availability` per service and an application map. A service level objective is created on the storefront operation with a 300 millisecond threshold, a 99.9 percent attainment goal and a rolling 30-day interval, with burn rate alarms so the team hears when the error budget is being consumed faster than the baseline. Because overnight traffic is near zero, a static threshold on request count would be either noisy or blind, so the traffic-drop alarm uses anomaly detection, and the availability alarm is a metric math ratio of faults to requests rather than a raw fault count. A Synthetics canary runs the login and checkout journey every minute, which closes the 40-minute gap because it fails whether or not a customer is there, and CloudWatch RUM supplies the real client-side view alongside it.

The alarms are wired for action rather than for email. The canary failure alarm, the availability ratio alarm and the ECS task-restart alarm carry no notifications; a composite alarm over them, with an `AND` between the canary and the availability condition, is the only thing that pages, and an actions suppressor tied to the deployment window keeps releases quiet. The composite alarm creates a Systems Manager OpsItem with the runbook attached, while the Auto Scaling policy stays on the underlying metric alarm, because composite alarms cannot perform scaling actions. Logs are brought under control with 30-day retention on the application log groups, the Infrequent Access class for compliance archives, and an account-level data protection policy so card numbers are masked at ingestion. The security account becomes the monitoring account for cross-account observability, linked through AWS Organizations, and a subscription filter ships security-relevant log groups to it for long-term retention in Amazon S3.

The exam asks this scenario two ways. The Associate version asks how to detect an overnight outage when there is no traffic to measure, and the keyed answer is a Synthetics canary on a one-minute schedule, not a static threshold alarm on request count. The Professional version asks how the operations team can query logs and alarm on metrics across all three accounts without copying data or modifying each workload, and the keyed answer is cross-account observability with a sink in the security account and Organizations-managed links, not a subscription filter pipeline.

## Exam lens

- "Alert when memory or disk space crosses a threshold on an EC2 instance" maps to the CloudWatch agent; enabling detailed monitoring is the distractor, because the hypervisor never sees those values.
- "Custom metrics with rich context from Lambda functions or containers" maps to the embedded metric format; a high-cardinality dimension there is what makes the bill explode.
- "The alarm keeps flipping to INSUFFICIENT_DATA on an idle resource" maps to treating missing data as `notBreaching` or `ignore`, because `missing`, the default, is what produces that state. Separately, AWS recommends `missing` for EC2 stop, terminate, reboot and recover alarms, so that a gap in reporting never triggers the action.
- "Normal usage varies by time of day so no fixed threshold works" maps to an anomaly detection alarm, trained on up to two weeks of history.
- "Page only when several conditions are true together, and stop the noise during maintenance" maps to a composite alarm with an actions suppressor; a composite alarm cannot take EC2 or Auto Scaling actions.
- "Automatically move an impaired instance to healthy hardware" maps to a recover action on a `StatusCheckFailed_System` alarm; `StatusCheckFailed_Instance` with a reboot action is the distractor.
- "Alarm on a string or API call appearing in logs" maps to a metric filter plus an alarm; filters are not retroactive.
- "Stream log events in near real time to a third-party platform or a custom processor" maps to a subscription filter to Kinesis Data Streams, Amazon Data Firehose, Lambda or OpenSearch Service, five per log group.
- "Reduce CloudWatch Logs cost" maps first to a retention policy, because the default is never expire, then to the Infrequent Access class, which supports no metric filters, subscription filters or embedded metric format.
- "One team must query metrics and logs in 200 accounts without copying data" maps to cross-account observability with a sink, links and AWS Organizations; a subscription filter pipeline is the distractor when the stem forbids moving data.
- "Find which client, key or URL is causing the load" maps to Contributor Insights; a metric dimension is the distractor, because it bills per value.
- "Detect an outage when there is no customer traffic" maps to a CloudWatch Synthetics canary, which can run as often as once per minute and can run inside a VPC.
- "Find which service in a chain of microservices is adding the latency" maps to AWS X-Ray traces and the trace map; traces are kept for 30 days and the default sampling is one request per second plus five percent.
- "Keep one-minute metric data beyond 15 days" maps to a metric stream into Amazon S3, because CloudWatch rolls it up to five-minute after 15 days and one-hour after 63 days.
- "The team already has Prometheus exporters and Grafana dashboards" maps to Amazon Managed Service for Prometheus with Amazon Managed Grafana, not to rewriting the metrics as custom CloudWatch metrics.

## Knowledge check

### 1. Alerting before an instance runs out of memory (Associate)

A company runs a Java application on Amazon EC2 instances. Twice this month the application has failed after the Java virtual machine exhausted the instance's memory, and the operations team saw nothing in CloudWatch beforehand. The team wants an alarm that notifies them when memory utilization on any instance stays above 85 percent for five minutes.

Which solution will meet these requirements?

- **A)** Enable detailed monitoring on the instances and create an alarm on the `MemoryUtilization` metric in the `AWS/EC2` namespace.
- **B)** Create a CloudWatch Logs metric filter on the application log group that matches out-of-memory messages, and alarm on the resulting metric.
- **C)** Install the CloudWatch agent on the instances, configure it to collect `mem_used_percent`, and create an alarm on that metric in the `CWAgent` namespace.
- **D)** Create an anomaly detection alarm on the `CPUUtilization` metric, because memory pressure raises CPU usage.

<details><summary>Answer</summary>

**Answer: C.** Memory lives inside the guest operating system, which the hypervisor cannot see, so EC2 never publishes a memory metric. The CloudWatch agent collects `mem_used_percent` and publishes it under the `CWAgent` namespace, where an ordinary threshold alarm works. A is not possible, because there is no `MemoryUtilization` metric in `AWS/EC2` and detailed monitoring only changes the interval of metrics that already exist. B alarms after the failure has already been logged, which is too late for the stated requirement to alert before the application fails. D substitutes a proxy signal for the real one and would fire on any CPU-heavy workload while missing a slow memory leak on an idle instance.

*Where this is covered: Custom metrics, the embedded metric format, and the agent.*

</details>

### 2. An outage nobody noticed overnight (Associate)

A retailer's checkout page failed at 02:00 and was not noticed until staff arrived at 08:00. Between midnight and 06:00 there is almost no customer traffic, so request-count and error-rate alarms stayed quiet. The company wants to learn within a few minutes that the checkout journey has stopped working, at any hour, and wants screenshots of the failure.

Which solution will meet these requirements?

- **A)** Create a CloudWatch alarm on the load balancer's request count with a static threshold of zero requests over five minutes.
- **B)** Create a CloudWatch Synthetics canary that runs the checkout journey in a headless browser every minute and alarm on its `SuccessPercent` metric.
- **C)** Enable CloudWatch RUM on the checkout page and alarm on the client-side error rate.
- **D)** Enable AWS X-Ray active tracing on the checkout service and alarm on the trace fault rate.

<details><summary>Answer</summary>

**Answer: B.** A canary generates its own traffic, so it detects a broken endpoint whether or not customers are present, can drive a full browser journey including login and checkout, stores screenshots, and runs as often as once per minute. A depends on real traffic that the stem says does not exist overnight, and a threshold of zero requests would fire every quiet night. C is real user monitoring, which also depends on real users, so it reports nothing when nobody is on the site. D traces requests that are actually made, so with no requests there are no traces and no fault rate to alarm on.

*Where this is covered: Application observability: Insights, canaries, and RUM.*

</details>

### 3. An automatic recovery that keeps terminating healthy servers (Associate)

A company created a CloudWatch alarm on the `StatusCheckFailed_System` metric with a terminate action so that impaired instances are replaced. The alarm treats missing data as `breaching`. Over the past month several healthy instances were terminated after brief gaps in metric reporting. The company still wants automatic action on genuine host impairment, but must stop acting on reporting gaps, and must preserve the instance ID and its Elastic IP address.

Which solution will meet these requirements?

- **A)** Change the alarm to treat missing data as `breaching` and keep the terminate action.
- **B)** Change the alarm to treat missing data as `notBreaching` and keep the terminate action.
- **C)** Replace the alarm with one on `StatusCheckFailed_Instance` configured with a reboot action.
- **D)** Change the alarm action to recover, and configure the alarm to treat missing data as `missing`.

<details><summary>Answer</summary>

**Answer: D.** AWS recommends treating missing data as `missing` for EC2 alarms that stop, terminate, reboot or recover, precisely because status check metrics can briefly disappear on a healthy instance, and the recover action migrates the instance to new hardware while keeping its instance ID, private addresses, Elastic IP address and metadata, which termination destroys. A makes the problem worse by converting every reporting gap into a breach. B silences genuine failures whenever the metric stops reporting, which is exactly what an impaired host does. C changes the failure being watched: an instance status check failure is an operating system problem, while the stem describes host impairment detected by the system status check.

*Where this is covered: Alarms, missing data, and alarm actions.*

</details>

### 4. A log bill that grew without anyone noticing (Associate)

A company's CloudWatch Logs charges have tripled in a year. Investigation shows that no log group has a retention setting, and that a set of compliance log groups holding 40 TB is queried perhaps twice a quarter but must be kept for seven years. Application log groups feed metric filters and alarms and must keep every current feature.

Which combination of steps will meet these requirements MOST cost-effectively? (Select TWO.)

- **A)** Set a 30-day retention policy on every log group in the account, including the compliance log groups.
- **B)** Set a retention policy appropriate to each application log group, because the default is that log data never expires.
- **C)** Move the application log groups to the Infrequent Access log class to reduce ingestion cost.
- **D)** Create new log groups in the Infrequent Access log class for future compliance logs, and export the existing data to Amazon S3 for the seven-year requirement.
- **E)** Enable a data protection policy on all log groups so that masked data is stored more cheaply.

<details><summary>Answer</summary>

**Answer: B and D.** CloudWatch Logs stores data indefinitely unless a retention policy is set, so setting retention per log group is the first and largest saving, and the Infrequent Access class ingests at a lower price while keeping cross-account access and Logs Insights, which suits archives that are queried rarely. A breaks the seven-year compliance requirement by deleting the archive after 30 days. C breaks the application groups, because the Infrequent Access class supports no metric filters, no subscription filters and no embedded metric format, so the alarms would stop working. E confuses two features: data protection masks sensitive values and changes nothing about storage price.

*Where this is covered: CloudWatch Logs: groups, retention, and filters.*

</details>

### 5. Turning a log line into an alert (Associate)

An application writes a line containing the string `FATAL` to a CloudWatch Logs log group whenever a background job aborts. Operations must be paged within a few minutes of the third such line in five minutes. The team does not want to run any additional compute and does not want to change the application.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create a metric filter on the log group that matches `FATAL`, publish it as a metric with a default value of 0, and create an alarm with a threshold of 3 over a five-minute period that notifies an Amazon SNS topic.
- **B)** Create a subscription filter on the log group that sends matching events to an AWS Lambda function which counts them and calls Amazon SNS.
- **C)** Schedule a CloudWatch Logs Insights query every five minutes from a Lambda function and notify Amazon SNS when the count exceeds three.
- **D)** Export the log group to Amazon S3 on a schedule and query it with Amazon Athena.

<details><summary>Answer</summary>

**Answer: A.** A metric filter converts matching log events into a CloudWatch metric that any alarm can watch, which is the native path from a log line to a notification with no code and no compute; the default value of 0 keeps the series continuous so the alarm evaluates cleanly. B works but adds a function to write, deploy and operate for counting that CloudWatch already does. C also adds a function plus a scheduler and pays per gigabyte scanned on every run. D is a batch analytics path with a delay measured in hours, which cannot meet a few-minute paging requirement.

*Where this is covered: CloudWatch Logs: groups, retention, and filters.*

</details>

### 6. A threshold that is wrong at both ends of the day (Associate)

A media company's API serves 50 requests per second at 03:00 and 5,000 at 20:00, with a repeatable daily and weekly shape. A static alarm at 500 requests per second pages every evening and never fires when overnight traffic collapses to zero. The company wants to be alerted when traffic is abnormal for the time of day, without maintaining a schedule of thresholds.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create several alarms with different thresholds and use a composite alarm to combine them.
- **B)** Publish the request count as a high-resolution custom metric and alarm on a one-second period.
- **C)** Enable anomaly detection on the request count metric and create an anomaly detection alarm that fires when the value falls outside the expected band.
- **D)** Create a Contributor Insights rule on the access logs and alarm on the number of unique contributors.

<details><summary>Answer</summary>

**Answer: C.** Anomaly detection trains a model on up to two weeks of the metric's own history, accounts for hourly, daily and weekly seasonality and for trend, and produces a band of expected values, so one alarm covers both the quiet night and the busy evening with no thresholds to maintain. A still requires somebody to choose and revise every static threshold, and a composite alarm combines alarm states rather than adapting them. B changes the resolution of the data, not the fact that a fixed threshold cannot fit a curve. D reports which clients are generating load, which is a different question from whether total load is abnormal.

*Where this is covered: Alarms, missing data, and alarm actions.*

</details>

### 7. Finding the slow hop in a chain of services (Associate)

A customer-facing request passes through an API layer, three internal microservices and a database. End-to-end latency has risen from 400 milliseconds to 2 seconds, but every service's own CloudWatch latency metric looks normal. The team must identify which call in the chain is responsible, including calls to AWS services that do not emit their own telemetry.

Which solution will meet these requirements?

- **A)** Enable detailed monitoring on the instances hosting each microservice and compare the CPU graphs.
- **B)** Create a CloudWatch dashboard with every service's latency metric on one graph.
- **C)** Enable Container Insights on the cluster and review the pod-level performance log events.
- **D)** Instrument the services with AWS X-Ray, enable active tracing, and use the trace map and trace timelines to compare segment and subsegment durations.

<details><summary>Answer</summary>

**Answer: D.** X-Ray correlates the segments emitted by every service that handled the same request into one trace, breaks each segment into subsegments for downstream calls, and infers segments for services such as DynamoDB that emit none, so the timeline shows exactly which hop consumed the time. A measures host resources, which are normal in the stem, and says nothing about the call path. B places independent averages side by side; each service can look healthy while the time is lost between them or in a dependency nobody graphed. C gives container-level resource metrics for one cluster, not the cross-service path of a single request.

*Where this is covered: AWS X-Ray and distributed tracing.*

</details>

### 8. One operations team, 180 accounts (Professional)

A company runs 180 AWS accounts in one organization and one Region. A central operations team must graph metrics from every account on shared dashboards, create alarms in its own account that watch metrics in workload accounts, and run a single CloudWatch Logs Insights query across log groups in many accounts. Data must stay in the accounts that produce it, workload teams must keep the ability to revoke sharing, and new accounts must be onboarded without manual work.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** In the operations account, create a CloudWatch cross-account observability sink and select metrics, log groups and traces as the shared telemetry types.
- **B)** In each workload account, create a subscription filter that streams every log group to a Kinesis data stream in the operations account.
- **C)** Use an AWS Organizations-based link configuration so that every current and future member account creates an observability link to the sink.
- **D)** Grant the operations team an IAM role in every workload account and have engineers switch roles to view each account's console.
- **E)** Create a composite alarm in the operations account that references metric alarms in each workload account.

<details><summary>Answer</summary>

**Answer: A and C.** A sink in the monitoring account plus links from the source accounts is exactly the cross-account observability model: nothing is copied, the monitoring account can graph and alarm on source metrics and query many accounts' log groups in one Logs Insights query, links are managed by the source account so workload teams can revoke them, and linking through AWS Organizations onboards accounts created later automatically. B physically copies log data, which the stem forbids, and covers only logs. D gives access one account at a time and cannot produce a single dashboard or a single cross-account query. E is not possible: a composite alarm's underlying alarms must live in the same account and Region as the composite, and cross-account composite alarms are not supported.

*Where this is covered: Logs Insights, data protection, and cross-account observability.*

</details>

### 9. Two hundred pages for one network failure (Professional)

A platform team has 140 metric alarms, each notifying an on-call Amazon SNS topic. When a shared network dependency failed, 90 alarms fired within two minutes and the on-call engineer missed the one that mattered. Planned maintenance produces the same flood. The team wants one page per real incident, wants no pages during declared maintenance windows, and must keep the Auto Scaling policy that a CPU alarm currently triggers.

Which solution will meet these requirements?

- **A)** Increase the evaluation periods on all 140 alarms so that they take longer to fire.
- **B)** Remove the notification actions from the metric alarms, build composite alarms whose rule expressions express the real incident conditions, notify only from the composite alarms, attach an actions suppressor driven by a maintenance alarm, and leave the Auto Scaling action on the CPU metric alarm.
- **C)** Replace the metric alarms with a single composite alarm that also performs the Auto Scaling action, and delete the CPU metric alarm.
- **D)** Disable alarm actions on all alarms during maintenance using the DisableAlarmActions API, and otherwise leave the design unchanged.

<details><summary>Answer</summary>

**Answer: B.** AWS documents composite alarms as the way to reduce alarm noise: keep the detailed metric alarms as signals without notifications, express the operational condition as a rule over them, and page only from the composite, with an actions suppressor silencing it for a declared maintenance or upstream condition. Keeping the Auto Scaling action on the metric alarm is required, because a composite alarm cannot perform EC2 or Auto Scaling actions. A delays every page without reducing their number and slows real detection. C is not possible for the same reason as the Auto Scaling constraint in B, and it also discards the detail needed to diagnose. D requires a manual API call at the start and end of every window and does nothing about the 90 simultaneous pages during an unplanned failure.

*Where this is covered: Alarms, missing data, and alarm actions.*

</details>

### 10. A custom metric bill that outgrew the workload (Professional)

A company instrumented a fleet of containerized services to publish a `RequestLatency` custom metric with dimensions for service, Availability Zone, customer identifier and request identifier. The CloudWatch bill is now dominated by custom metrics. The company still needs per-service and per-Availability-Zone alarms, still needs to investigate which individual customers see slow requests, and needs p99 latency rather than an average.

Which combination of steps will meet these requirements MOST cost-effectively? (Select TWO.)

- **A)** Keep all four dimensions but publish the metric at one-second storage resolution to reduce the number of data points.
- **B)** Delete the existing high-cardinality metrics through the CloudWatch console so the charges stop immediately.
- **C)** Publish `RequestLatency` with only the service and Availability Zone dimensions, using raw data points so percentile statistics remain available.
- **D)** Replace the alarms with an anomaly detection alarm on each customer's metric.
- **E)** Emit the customer identifier and request identifier as fields in embedded metric format log events, and use CloudWatch Logs Insights and a Contributor Insights rule to investigate individual customers.

<details><summary>Answer</summary>

**Answer: C and E.** A metric is one unique combination of namespace, name and dimension values, so removing the customer and request dimensions collapses thousands of billable metrics into a handful while keeping the per-service and per-Availability-Zone alarms, and publishing raw values rather than statistic sets keeps p99 available. The identifiers belong in log fields, where Logs Insights and Contributor Insights can answer the per-customer question without creating a metric for each value. A raises cost rather than lowering it, because high-resolution publishing means more `PutMetricData` calls. B is not possible: CloudWatch metrics cannot be deleted and expire only after 15 months without new data. D multiplies the problem, adding an anomaly detection model that bills as three metrics for every customer.

*Where this is covered: Metrics, dimensions, and monitoring intervals.*

</details>

## Summary

Amazon CloudWatch is a sequence of choices, and the exam asks them one at a time. Choose the signal first: a metric when a number crosses a line, a log when you need the detail, a trace when the question is which service in a chain is slow, a canary when there is no traffic to observe, and real user monitoring when the browser's experience is the requirement. Then choose the source: AWS services publish their own metrics, EC2 needs detailed monitoring for one-minute data, and anything inside the guest operating system needs the CloudWatch agent. Then choose the alarm shape: a static threshold when a real limit exists, anomaly detection when normal moves with the clock, a composite alarm when several conditions must hold together, always with a deliberate treat-missing-data setting. Then choose the action, from a notification through a scaling policy to an instance recovery. Then control the cost, which is dimension cardinality and log retention far more often than anything else. And keep CloudWatch, AWS CloudTrail and AWS Config separate in your head: behavior, API activity, and configuration state.

## Related units

- [AWS CloudTrail](cloudtrail.md): the API activity record that answers who called what, and the trail that feeds a log group
- [Detection and compliance services](../07-security/detection-and-compliance-services.md): AWS Config recording configuration state, rules and aggregators
- [AWS Systems Manager](systems-manager.md): OpsItems, Incident Manager and the automation runbooks an alarm can open
- [Amazon EventBridge](../06-integration/eventbridge.md): the event bus that routes state changes to remediation targets
- [Amazon EC2](../02-compute/ec2.md): status checks, instance recovery and the metrics the hypervisor can and cannot see
- [Amazon EC2 Auto Scaling](../02-compute/ec2-auto-scaling.md): the scaling policies that CloudWatch alarms invoke
- [AWS Lambda](../02-compute/lambda.md): function metrics, log groups and the extension behind Lambda Insights
- [Cost management](cost-management.md): where CloudWatch charges sit in the overall bill and how to attribute them

## Sources

- [Viewing the X-Ray service map](https://docs.aws.amazon.com/xray/latest/devguide/xray-console-servicemap.html): the trace map that absorbed the ServiceLens view
- [CloudWatch cross-account observability](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Unified-Cross-Account.html): the telemetry types a monitoring account can see

- [CloudWatch metrics concepts](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html): namespaces, dimension combinations, the 15-month expiry, the retention tiers and roll-up, resolution, periods and percentiles
- [Publish custom metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/publishingMetrics.html): high-resolution metrics, statistic sets, publishing zero, and the delay before a new metric is retrievable
- [Embedding metrics within logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format.html): metric extraction from structured logs, the `logs:PutLogEvents` permission, and the high-cardinality warning
- [Collect metrics, logs, and traces using the CloudWatch agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html): in-guest metrics, StatsD and collectd, trace collection, the `CWAgent` namespace and custom-metric billing
- [Metrics collected by the CloudWatch agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/metrics-collected-by-CloudWatch-agent.html): the memory, swap, disk, process and netstat metric names on Linux and the Windows counters
- [Manage detailed monitoring for your EC2 instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/manage-detailed-monitoring.html): one-minute status checks under basic monitoring, one-minute everything under detailed monitoring, and the per-metric charge
- [Amazon CloudWatch metrics for Amazon EBS](https://docs.aws.amazon.com/ebs/latest/userguide/using_cloudwatch_ebs.html): one-minute metrics for all volume types at no charge, only while attached
- [Using Amazon CloudWatch alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html): metric and composite alarms, actions on state change, the Auto Scaling exception, evaluation period ceilings, and that composite alarms cannot take EC2 or Auto Scaling actions
- [Configuring how CloudWatch alarms treat missing data](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarms-and-missing-data.html): the four options, `missing` as the default, the evaluation range, and the EC2 action recommendation
- [PutCompositeAlarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/APIReference/API_PutCompositeAlarm.html): rule expression syntax with `ALARM`, `OK`, `INSUFFICIENT_DATA`, `AND`, `OR` and `NOT`, the four permitted actions, the 100-child limit, and the `ActionsSuppressor` wait and extension periods
- [Using CloudWatch anomaly detection](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Anomaly_Detection.html): training on up to two weeks of data, seasonality and trend, per-statistic models, and anomaly detection on metric math
- [Create alarms that stop, terminate, reboot, or recover an instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/UsingAlarmActions.html): the recover action's `StatusCheckFailed_System` restriction, what a recovered instance keeps, and the reboot and recover race warning
- [Working with log groups and log streams](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html): that log data is stored indefinitely by default and the 72-hour deletion behavior
- [PutRetentionPolicy](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutRetentionPolicy.html): the exact list of valid retention values in days
- [Log classes](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatch_Logs_Log_Classes.html): the Standard and Infrequent Access feature matrix, the immutable class, and the two-day `Delivery` class
- [Creating metrics from log events using filters](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/MonitoringLogData.html): default value, dimensions, Standard-class-only support and the non-retroactive rule
- [Real-time processing of log data with subscriptions](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Subscriptions.html): destinations, five filters per log group, one account-level filter per Region, and the retry behavior
- [Analyzing log data with CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html): the three query languages, 60-minute timeout, seven-day results, concurrency limits and per-gigabyte-scanned charging
- [Help protect sensitive log data with masking](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/mask-sensitive-log-data.html): managed and custom data identifiers, masking at egress points, `logs:Unmask`, and account-level policies
- [CloudWatch cross-account observability](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Unified-Cross-Account.html): sinks and links, shareable telemetry types, the Organizations recommendation, the 100,000 and five limits, and the no-extra-cost statement
- [Using Amazon CloudWatch dashboards](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Dashboards.html): cross-Region and cross-account dashboards and what a monitoring account can do
- [Use metric streams](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Metric-Streams.html): Firehose and partner destinations, JSON and OpenTelemetry formats, and namespace filters
- [Container Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html): supported platforms, performance log events in embedded metric format, and the per-observation billing for enhanced observability
- [Lambda Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Lambda-Insights.html): the extension layer, the per-invocation performance log event and the metrics collected
- [Application Signals](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Monitoring-Sections.html): supported languages and platforms, the application map, and cross-account requirements
- [Service level objectives](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-ServiceLevelObjectives.html): SLI, attainment goal, calendar and rolling intervals, error budget and burn rate
- [Synthetic monitoring (canaries)](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries.html): runtimes and browsers, the one-minute minimum schedule, the `CloudWatchSynthetics` namespace and VPC support
- [CloudWatch RUM](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-RUM.html): app monitors, the code snippet, session sampling and 30-day retention
- [Use Contributor Insights to analyze high-cardinality data](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContributorInsights.html): rules, top-N contributors, built-in rules and per-matching-event charging
- [Support for Amazon CloudWatch Evidently ending soon](https://aws.amazon.com/blogs/mt/support-for-amazon-cloudwatch-evidently-ending-soon/): the 17 October 2025 end of support and the AWS AppConfig recommendation
- [AWS X-Ray concepts](https://docs.aws.amazon.com/xray/latest/devguide/xray-concepts.html): segments and subsegments, inferred segments, the service graph, default sampling of one request per second plus five percent, the tracing header, annotations against metadata, and 30-day retention
- [CloudWatch service quotas](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_limits.html): Contributor Insights rules, canary limits, Application Signals SLO limits, and Observability Access Manager sinks and links
- [Amazon CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/): the free tier and the charge dimensions for custom metrics, API requests, alarms, logs ingestion, storage and query
- [What is AWS CloudTrail?](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html): Event history for 90 days of management events, trails delivering to Amazon S3, CloudWatch Logs and EventBridge
- [What is AWS Config?](https://docs.aws.amazon.com/config/latest/developerguide/WhatIsConfig.html): configuration items, history, relationships, rules, conformance packs and aggregators
- [What is Amazon Managed Grafana?](https://docs.aws.amazon.com/grafana/latest/userguide/what-is-Amazon-Managed-Service-Grafana.html): workspaces, AWS and third-party data sources, IAM Identity Center and SAML, and per-active-user pricing
- [What is Amazon Managed Service for Prometheus?](https://docs.aws.amazon.com/prometheus/latest/userguide/what-is-Amazon-Managed-Service-Prometheus.html): workspaces, three-Availability-Zone replication, PromQL, and 150-day default retention up to 1,095 days
