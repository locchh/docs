# AWS CloudTrail

**Where it sits on the exams.** **AWS CloudTrail**, the AWS activity audit service, records supported user, role and service actions as events so an architect can answer who did what, where and when. Event history gives every account a recent management-event view, while a trail delivers selected events to **Amazon Simple Storage Service (Amazon S3)**, the durable object storage service, and optionally to **Amazon CloudWatch Logs**, the log storage and query feature of **Amazon CloudWatch**, the unified monitoring, log and analytics service. CloudTrail serves SAP-C02 tasks 1.2 and 3.2 directly and supports SAA-C03 security, governance and troubleshooting decisions. Rule of thumb: use Event history for a recent one-Region lookup, a multi-Region organization trail for durable centralized evidence, data events for operations inside resources, Insights for unusual API activity, and Config alongside CloudTrail when the question asks both what changed and who changed it.

## Read the event before choosing the storage path

A CloudTrail event is a JSON record of a supported action. Common fields include the event time, event source, event name, AWS Region, source IP address, user agent, request parameters, response elements and the identity that made the request. The `userIdentity` structure distinguishes an **AWS Identity and Access Management (IAM)** user, the AWS authorization service's long-lived identity, an assumed role session, an AWS service or another identity type. For temporary sessions, follow the session issuer and access-key details back to the role rather than treating the session name as proof of a human identity.

The event documents what CloudTrail observed, not necessarily the entire business transaction. Sensitive request or response fields may be omitted, read-only APIs may not modify state, and an error code means the call was attempted but did not succeed. `sourceIPAddress` might identify an AWS service or an intermediary rather than a person's device. Correlate request IDs, role-session context, application logs and network evidence before attributing intent.

Read identity and ownership separately in cross-account calls. The principal's account can differ from the account that owns the affected resource, and an assumed-role session can contain both the issuer role and session attributes. The event ID identifies the event for deduplication; a request ID helps correlate the call with service or application records. An `AccessDenied` event is valuable evidence of an attempted action, but it does not prove that another call did not later succeed. Search the surrounding time window and related identities instead of stopping at one record.

CloudTrail currently records four event categories. Read this table by the plane or anomaly the scenario asks about.

| Event category | What it records | Typical examples | Default in a new trail |
|---|---|---|---|
| Management | Control-plane operations performed on resources | Creating a trail, changing a bucket policy, describing instances | Included, read and write |
| Data | High-volume data-plane operations within a resource | S3 `GetObject`, Lambda `Invoke`, DynamoDB item operations | Not included |
| Network activity | Supported AWS API calls made through a VPC endpoint | An operation denied by an endpoint policy with `VpceAccessDenied` | Not included |
| Insights | Unusual API call rates or API error rates compared with a baseline | A spike in write calls or failed authorization calls | Not included |

Console, CLI and SDK activity converges on AWS APIs, so the same event model covers all three access paths, and CloudTrail also records supported non-API events such as console sign-in. Calls made by one AWS service on behalf of another can appear with a service identity rather than the original human principal alone. For a chain such as a deployment service assuming a role and changing a resource, reconstruct each relevant event and session instead of expecting one record to narrate the whole chain.

Management events are divided into read events that retrieve information and write events that create, modify or delete something. A security trail normally keeps both. If cost or noise requires filtering, preserve high-value write activity and document exclusions. The Event history cannot inherit those exclusions: it continues to show supported management events independently of trail configuration.

Data events are often the missing answer in an exam scenario. A management event shows that someone changed an S3 bucket policy, but only S3 object-level data events show supported `GetObject`, `PutObject` and `DeleteObject` operations. Similarly, creating an **AWS Lambda** function, the serverless function service, is a management event, while invoking it is a data event. Data events are high volume and billed, so select the resource types, prefixes, identities and operations that match the audit requirement instead of enabling everything without estimating ingestion.

Network activity events give VPC endpoint owners visibility into supported API operations that passed through their endpoints. They must be enabled explicitly and use advanced event selectors, and each selector names one `eventSource` from the supported list, which spans more than seventy services and includes `s3.amazonaws.com`, `kms.amazonaws.com`, `ec2.amazonaws.com`, `secretsmanager.amazonaws.com` and `cloudtrail.amazonaws.com`. Logging several sources takes one field selector each. Optional filters narrow further: `vpcEndpointId` restricts collection to one endpoint, and `errorCode` accepts only the value `VpceAccessDenied`, which records just the calls an endpoint policy refused. Unlike management and data events, which reach both the caller and the resource owner, network activity events are delivered only to the owner of the VPC endpoint. They are distinct from **VPC Flow Logs**, the IP traffic metadata feature: a flow log describes accepted or rejected network flows, while a CloudTrail network activity event describes a supported AWS API operation and its identity context.

This advanced event selector records only the denied Amazon S3 calls that crossed VPC endpoints in the account:

```json
[{
  "Name": "S3 VPC endpoint denials",
  "FieldSelectors": [
    { "Field": "eventCategory", "Equals": ["NetworkActivity"] },
    { "Field": "eventSource",   "Equals": ["s3.amazonaws.com"] },
    { "Field": "errorCode",     "Equals": ["VpceAccessDenied"] }
  ]
}]
```

## Event history, trails and Regions

CloudTrail is active for an AWS account without setup. Event history is a viewable, searchable, downloadable and immutable record of the last 90 days of management events in one account and one Region, at no CloudTrail charge. It does not show data, network activity or Insights events, cannot query several Regions at once and accepts only one attribute filter plus a time range. Changing or deleting a trail does not change Event history. Use it for a recent question such as who terminated an instance yesterday, not as the organization's retention design.

A trail is the durable delivery configuration. It selects event categories and sends log files to an S3 bucket. Optional delivery to CloudWatch Logs supports near-real-time searches, metrics and alarms, and an **Amazon Simple Notification Service (Amazon SNS)** topic, the managed publish-subscribe service, can notify subscribers when CloudTrail delivers log files. CloudTrail batches events into files; delivery is not a transaction log that an application should synchronously wait for.

Each compressed S3 log object holds several event records, and the key path separates account, Region and date. An SNS notification announces log-file delivery rather than one notification per API call. A trail created today does not reconstruct a durable S3 history for the months before it existed, so design the trail before the retention requirement begins.

Use a multi-Region trail for governance unless the scope is intentionally Regional. A multi-Region trail captures activity in all enabled Regions and extends to Regions enabled later. Trails created in the console are multi-Region; creating a single-Region trail requires the CLI. A single-Region trail can be useful for a bounded workload or a second specialized stream, but it is a common distractor when the requirement says an actor might operate in any Region.

The trail's home Region is where its configuration is created and updated. Copies of a multi-Region trail appear in enabled Regions, but configuration changes belong in the home Region. Distinguish the Region where an API event occurred from the central S3 bucket's Region: central delivery does not rewrite the event's own region field.

Global service events are the reason a single-Region trail can silently miss the activity an audit cares about most. For services with Regional endpoints, including **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service, events are recorded in the Region where the action occurred. For global services such as IAM, **AWS Security Token Service (AWS STS)**, the temporary-credential service, and **Amazon CloudFront**, the content delivery network, events go to any trail that includes global services. Most are logged as occurring in the US East (N. Virginia) Region, us-east-1, though some are logged in other Regions such as US East (Ohio) or US West (Oregon). The `IncludeGlobalServiceEvents` setting decides whether a trail receives them, and it must be true for a multi-Region trail. When it is true, CloudTrail delivers global service events to single-Region trails only in us-east-1. A single-Region trail in eu-west-1 therefore records no IAM or global-endpoint AWS STS activity at all, which is the usual reason an organization finds a gap in its identity evidence. Event history and `aws cloudtrail lookup-events` differ: they show these events in the Region where they occurred. AWS STS calls against a Region-specific endpoint are ordinary Regional events.

Delivery mechanics set the expectation a scenario is testing. CloudTrail publishes log files multiple times an hour, about every five minutes, and delivers nothing when no API calls were made. An event typically arrives within about five minutes of the call, but that time is not guaranteed, so a trail is not a synchronous control path. If a trail is misconfigured, for example because its S3 bucket is unreachable, CloudTrail keeps attempting redelivery for 30 days, and those attempted deliveries are still subject to standard CloudTrail charges; deleting the trail is what stops the charge. Delivery can also contain duplicate events, because CloudTrail is designed for at-least-once delivery of subscribed events. Consumers should deduplicate on the event ID, which repeats across duplicates, where their workflow cannot tolerate repeats, and should sort or correlate by event time rather than assuming S3 object arrival order is action order. These properties matter when a trail feeds an automated response or a forensic timeline.

## Organization trails and central custody

An organization trail logs events for every account in an organization in **AWS Organizations**, the multi-account governance service, and delivers them to one destination. Only the management account or a CloudTrail delegated administrator can create one, and the management account can convert an existing trail in its own account into an organization trail. Every organization trail created in the console is multi-Region and covers the enabled Regions in each member account; the CLI can create a single-Region organization trail, which logs only its home Region. To cover more than one AWS partition, create a multi-Region organization trail in each partition.

The mechanism is a replicated trail plus a service-linked role. CloudTrail creates a copy of the trail in each member account, along with the service-linked role `AWSServiceRoleForCloudTrail` that performs logging there. When an account joins the organization, the trail and the role are added and logging starts automatically, which is what makes an organization trail the answer whenever a scenario says present and future accounts. When an account leaves, the trail and role are removed from it and no further events are logged, but the log files it already produced stay in the destination bucket. Users in member accounts can see the organization trail and read its status, but they cannot delete it, stop logging, change which event types it records, or modify it in any way.

The destination layout follows the organization: log files land under a folder named with the organization ID, with a subfolder per account ID, so each member account's events sit under its own prefix in one bucket. By default only the management account can reach that bucket, which is the shape the exam wants: deliver once into a log archive account, keep workload administrators out of the evidence, and grant the security tooling account a separate read role. Write the bucket policy for the organization path, because a policy scoped to one account prefix will refuse the rest of the organization.

## Selectors, Insights and cost boundaries

A new trail logs management events by default and excludes data, network activity and Insights events. Basic event selectors cover read or write management activity and data events for S3 objects, Lambda functions and **Amazon DynamoDB**, the managed key-value and document database. Advanced event selectors reach the broader set of supported data resources and filter on fields such as event category, event name, resource type, resource ARN, event source and read-only status. A trail uses basic or advanced selectors, not both; applying advanced selectors replaces its basic selectors, so preserve existing coverage during a conversion.

Selectors are both a security and a cost design. Log object reads for a regulated bucket without paying for every object read in an unrelated content-delivery bucket, and keep write management events even when high-volume read events go to another analysis path. Excluding high-volume encryption-key or relational-database Data API events reduces cost, but an exclusion can remove evidence an investigation needs.

Test selectors with real resource ARNs before treating coverage as complete. For S3 object events the object ARN prefix differs from the bucket ARN, so a selector aimed only at the bucket resource can miss the data events the auditor requested. When converting from basic to advanced selectors, reproduce the existing intent first, then add filters.

CloudTrail Insights continuously builds a baseline and emits an Insights event when supported activity deviates. API call rate Insights for management events evaluates unusual write-management call volume, so the trail must log write management events. API error rate Insights analyzes management calls that returned an error code, so the trail must log read or write management events. CloudTrail also supports Insights on data-event call and error rates, but only on trails, not on event data stores, and only when the underlying data events are logged.

Know the delivery path and the charge shape, because both decide questions. When Insights is enabled on a trail, CloudTrail analyzes the past 28 days of collected events to form the baseline and recalculates it daily on a trailing 28 days; the baseline analysis is free. Detected Insights events go to a separate `/CloudTrail-Insight` folder in the same destination bucket, are published to EventBridge, and reach the CloudWatch Logs group when the trail has one. After Insights is first enabled, or re-enabled after a stop, delivery can take up to 36 hours to begin even if unusual activity occurs meanwhile, which rules Insights out of any near-real-time requirement. Charges follow the number of events analyzed, not the number of Insights events produced, and enabling both Insights types means write management events are analyzed twice. Insights finds a statistical deviation, not a known-malicious signature, and it does not replace GuardDuty.

The pricing shape explains many selector questions. Viewing Event history is free. Delivery of the first copy of ongoing management events to S3 is free, while additional copies of management events and logging data, network activity and Insights events incur CloudTrail charges. S3 storage and requests, CloudWatch Logs ingestion and retention, encryption-key API calls and downstream analytics have their own charges. The least-cost valid design captures the required evidence once, filters high-volume categories deliberately and applies an S3 lifecycle that matches policy.

## Protect and validate trail evidence

Centralize logs in a dedicated security or log archive account and allow CloudTrail to write through a narrowly scoped S3 bucket policy, so workload administrators cannot delete or rewrite the evidence that records their actions. S3 encrypts new objects by default; CloudTrail can use server-side encryption with a customer-managed **AWS Key Management Service (AWS KMS)** key, the managed encryption-key service, when the key policy permits CloudTrail to generate data keys and authorized readers to decrypt. Separate write, read and key-administration permissions.

The destination policy is a frequent failure point. Grant the CloudTrail service only the bucket check and object-write permissions it needs, constrain the statement to the expected trail ARN, and require the bucket-owner-full-control object ACL on delivery. The KMS key policy is separate from the bucket policy, and success in one does not compensate for denial in the other.

CloudTrail log file integrity validation detects modification or deletion after delivery. When enabled, CloudTrail hashes each delivered log file and delivers a signed digest file every hour. The chain uses SHA-256 hashing and SHA-256 with RSA signatures; each digest also references the previous digest when one exists. Digest files go to the same bucket as the log files but into a separate `CloudTrail-Digest` folder, so you can apply a stricter access policy to them without disturbing existing log processing, and CloudTrail uses a different key pair for each Region. The `aws cloudtrail validate-logs` command checks the digest signature and file hashes. Validation starts only after it is enabled, supplies detection rather than prevention and cannot prove integrity for earlier files.

Layer storage controls around validation. S3 Versioning retains overwritten versions, S3 Object Lock enforces write-once-read-many retention in a versioned bucket, and lifecycle rules move older evidence to a suitable archive class. An attacker who can stop a trail creates a gap even if existing files remain intact, so protect `StopLogging`, `DeleteTrail`, bucket-policy and key-policy operations with least privilege and organization guardrails.

Delivery status is part of monitoring: a bad bucket policy, inaccessible KMS key or incorrect CloudWatch Logs role prevents delivery silently. Alert on delivery errors and on configuration changes. CloudTrail records calls that change CloudTrail, but one trail cannot be the only independent evidence for unrestricted administrators who can disable it and its storage path.

## Search, alert and correlate

Send selected trail events to CloudWatch Logs when operations teams need log queries, metric filters, alarms or correlation with application logs. The log group is not a target CloudTrail writes to on its own authority: you supply an IAM role, and CloudTrail assumes it to create the log stream and put events into it, so the role should carry only `CreateLogStream` and `PutLogEvents` on the intended log group. Reusing an existing role for an organization trail means updating its policy by hand. The trail sends only what its own settings select, and events larger than the 256 KB that CloudWatch Logs and EventBridge accept are not sent to either destination. A metric filter can count a stable event pattern such as console sign-in failures or changes to a sensitive policy, and a CloudWatch alarm can notify or initiate a response. Set an explicit log-group retention period; indefinite retention by accident is not a compliance strategy.

Choose the consumer by latency and query style: S3 is the durable evidence destination, CloudWatch Logs the operational search and metric path, EventBridge the routing path for one event pattern, and Athena the pay-per-scan historical SQL path. A design can use several without duplicating the trail itself.

**Amazon EventBridge**, the managed event bus, receives CloudTrail activity on the default event bus and nowhere else; to handle it on a custom bus, match it on the default bus and forward it. The detail type names the category: `AWS API Call via CloudTrail`, `AWS Console Signin via CloudTrail`, `AWS Console Action via CloudTrail`, `AWS Service Event via CloudTrail`, `AWS Insight via CloudTrail` and `AWS Network Activity Event via CloudTrail`. An event pattern matches the source, detail type, API name, account, Region or detail fields and routes the event to a function, queue, notification or workflow. One pattern that alarms on a disabled encryption key looks like this:

```json
{
  "source": ["aws.kms"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": { "eventSource": ["kms.amazonaws.com"],
              "eventName": ["DisableKey", "ScheduleKeyDeletion"] }
}
```

One trap is worth knowing: a rule in the ordinary `ENABLED` state does not match read-only management events, so a rule written for a `Describe` or `Get` call appears to do nothing. Only the `ENABLED_WITH_ALL_CLOUDTRAIL_MANAGEMENT_EVENTS` state matches those. Write calls such as the key operation above match under plain `ENABLED`. Use EventBridge for event-driven response and CloudWatch Logs for retained search and metric extraction. Neither destination replaces the S3 trail when the requirement is durable audit evidence.

**Amazon Athena**, the serverless SQL query service for data in S3, queries CloudTrail JSON logs through an external table whose location and partition layout must match the trail prefix. Partition projection is the cheapest form: Athena computes partition values from table properties instead of reading a partition list, so a query filtered to a date range scans only those days.

```sql
CREATE EXTERNAL TABLE cloudtrail_logs (
  -- column list per the Athena guide
)
PARTITIONED BY (`timestamp` string)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
STORED AS INPUTFORMAT 'com.amazon.emr.cloudtrail.CloudTrailInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://bucket/AWSLogs/account-id/CloudTrail/region'
TBLPROPERTIES (
  'projection.enabled'='true',
  'projection.timestamp.type'='date',
  'projection.timestamp.format'='yyyy/MM/dd',
  'projection.timestamp.range'='2020/01/01,NOW',
  'storage.location.template'=
    's3://bucket/AWSLogs/account-id/CloudTrail/region/${timestamp}')
```

For an organization trail the path carries the organization ID before the account ID, so the location and the template must include it. Athena is a strong answer when logs already live in S3 and investigations are occasional.

Pair CloudTrail with AWS Config rather than choosing one for both jobs. CloudTrail identifies the actor and API request; **AWS Config**, the resource configuration history and compliance service, shows the resource's recorded state, relationships and rule evaluation before or after the change. **Amazon GuardDuty**, the managed threat detection service, adds threat context, and **AWS Security Hub CSPM**, the security posture and finding aggregation service, centralizes the finding. The forensic chain is detection, CloudTrail attribution, Config state comparison, protected raw evidence and a reviewed response.

## CloudTrail Lake availability change

CloudTrail Lake is the managed CloudTrail feature that stores selected events in immutable event data stores, converts event JSON to columnar Apache ORC and supports SQL queries and dashboards. Existing customers can still use account or organization event data stores and their configured retention. It remains a valid answer when a scenario says the company already uses CloudTrail Lake and needs managed SQL over long-lived audit events.

As of May 31, 2026, CloudTrail Lake is closed to new customers. Core CloudTrail remains fully supported: trails, Event history, Insights and aggregated events are not affected. Existing Lake customers continue, but the feature receives critical bug fixes and security updates rather than normal feature development. AWS recommends Amazon CloudWatch for comparable new-customer capture and analysis capabilities.

Do not key a new-customer design to creating a Lake event data store after that date. For durable raw audit logs and occasional SQL, use a multi-Region or organization trail to S3 and query it with Athena. For centralized ingestion, queries, dashboards and alerting, AWS directs Lake customers to migrate their data to CloudWatch, starting with CloudWatch pipelines. Note the scope: CloudWatch ingestion covers CloudTrail events except network activity and Insights events, so those two categories still need a trail. Existing organization event data stores continue to include new member accounts, while existing account-level stores do not extend ingestion to accounts added later, which matters in a growing estate.

## Professional depth

An organization trail is a deployment mechanism, not proof that delivery works. CloudTrail creates the trail copy in every member account even when resource validation fails, including an incorrect bucket policy, an incorrect SNS topic policy, an inability to write to the CloudWatch Logs log group, or insufficient permission to encrypt with the KMS key. The trail looks present and logs nothing. Member accounts can see those failures on the trail's detail page or through `get-trail-status`, so monitor status centrally rather than trusting the configuration, and run a controlled test event in each required partition first.

Opt-in Regions are the second trap at scale. If the home Region of a multi-Region organization trail is itself an opt-in Region, member accounts send no activity to the trail unless they have opted into that Region, so a trail homed in a newly launched Region can cover far fewer accounts than the console suggests. A trail homed in a default-enabled Region behaves as expected and extends into each member's opt-in Regions once they activate. Attaching a CloudWatch Logs group is also asymmetric: the management account can do it in the console, while a delegated administrator must use the CLI or API.

Separate the baseline trail from high-volume or specialized evidence when ownership, selectors, retention or access differ. The baseline organization trail should preserve broad management activity. A workload-specific trail can capture selected object reads or network activity events for a regulated application, with its own lifecycle and analyst boundary. Avoid recording a paid category repeatedly merely because several teams want access; deliver once and grant governed read or query paths where possible.

Response automation must tolerate duplicate and delayed events. Match a narrow EventBridge pattern, enrich the event with account and resource ownership, verify current state, and make the repair idempotent. Preserve the original event and workflow decision. Require approval for destructive containment, because CloudTrail proves that an API call occurred but does not by itself prove malicious intent.

## Worked scenario

A healthcare company operates 45 accounts in an organization and uses six Regions, including two opt-in Regions. Auditors require seven years of protected API evidence. Security operations needs an alarm when anyone changes a production bucket policy, object-level records for reads from one regulated bucket, and a SQL path for occasional investigations. The company has never used CloudTrail Lake.

The management account creates a multi-Region organization trail that delivers read and write management events to an encrypted, versioned and Object-Locked S3 bucket in the log archive account. The KMS and bucket policies allow CloudTrail delivery but keep workload administrators from deleting evidence. Advanced selectors add S3 object data events only for the regulated prefix. The trail also sends events to a centrally retained CloudWatch Logs group, where a metric filter and alarm detect the bucket-policy API, while EventBridge routes the same change to an approval workflow. Athena queries the partitioned S3 history. Operations verifies the trail in every enabled Region, monitors delivery status and schedules integrity validation.

The exam asks for centralized, tamper-evident, organization-wide traceability with targeted high-volume logging and no unavailable service. The keyed answer is the multi-Region organization trail, scoped data-event selectors, protected S3 storage with log validation, CloudWatch Logs or EventBridge for the alert path, and Athena for historical SQL. A new CloudTrail Lake event data store is the outdated distractor after May 31, 2026.

## Exam lens

- "Who terminated this instance yesterday" maps to Event history in the event's Region; it needs no trail and covers 90 days of management events.
- "Retain activity longer than 90 days" maps to a trail with S3 delivery; Event history is not configurable long-term storage.
- "IAM or AWS STS activity is missing from our logs" maps to a single-Region trail outside us-east-1; only a multi-Region trail, or a single-Region trail in us-east-1, receives global service events.
- "Record reads and writes to objects inside one S3 bucket" maps to data events with a resource-scoped selector; bucket configuration changes are management events.
- "Record a denied AWS API call through a VPC endpoint" maps to a network activity event; VPC Flow Logs lack the same API identity record.
- "Unusual spike in write API calls" maps to CloudTrail Insights API call rate analysis; GuardDuty is the behavioral threat detector distractor.
- "All present and future organization accounts" maps to a multi-Region organization trail created by the management account or delegated administrator.
- "Prove delivered log files were not changed" maps to log file integrity validation; use S3 Object Lock when prevention of deletion or overwrite is also required.
- "Alarm on a sensitive API call" maps to CloudWatch Logs with a metric filter and alarm, or EventBridge for direct event routing.
- "Run occasional SQL across years of trail files already in S3" maps to Athena with partitions or partition projection.
- "Show the resource state before and after the API call" maps to Config alongside CloudTrail; CloudTrail alone supplies the actor and request.
- "New customer wants CloudTrail Lake after May 31, 2026" maps to a current CloudWatch architecture or S3 plus Athena, not a new Lake event data store.
- "Existing CloudTrail Lake customer needs managed SQL" can still map to its event data store; closure to new customers did not delete existing stores.
- "Reduce cost without losing change evidence" maps to one broad management-event copy plus narrowly selected paid data or network categories, not disabling the baseline trail.

## Knowledge check

### 1. Looking up a recent administrative action (Associate)

A media company's operations engineer must identify who changed an Amazon EC2 security group 12 days ago. No CloudTrail trail was configured at the time of the change, and none exists today. The engineer knows which Region contains the security group and needs the answer this afternoon. The company does not want to stand up new logging infrastructure for a single lookup.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Search CloudTrail Event history in that Region.
- **B)** Create a trail now and search its new S3 objects for the earlier event.
- **C)** Enable S3 object-level data events for the account and search the delivered files.
- **D)** Create a CloudTrail Lake event data store and wait for it to backfill the event automatically.

<details><summary>Answer</summary>

**Answer: A.** Event history is available without configuring a trail and retains 90 days of management events in each Region, so a 12-day-old security-group change is in scope and needs no new infrastructure. B starts durable delivery going forward and does not retroactively place the old event in its S3 prefix. C records operations inside selected S3 resources, not EC2 security-group management calls, and it adds a billed event category for no benefit here. D is unavailable to a new Lake customer after May 31, 2026, and a new store would not backfill prior Event history in any case.

*Where this is covered: Event history, trails and Regions.*

</details>

### 2. Auditing reads of regulated objects (Associate)

A financial services company already operates a trail that records all management events in every Region. An external auditor now requires the identity, event time and source IP address for every `GetObject` call made against one regulated prefix in an S3 bucket. Reads of the company's other buckets must stay out of scope so that logging charges do not rise across the estate. The security team wants to change as little of the existing trail as possible.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Enable CloudTrail Insights for write management events on the existing trail.
- **B)** Create a second trail that delivers another copy of all management events in every Region.
- **C)** Add an S3 object-level data event selector scoped to the regulated prefix.
- **D)** Enable network activity events for every supported event source in the account.

<details><summary>Answer</summary>

**Answer: C.** `GetObject` is a data-plane operation, and an advanced data-event selector can scope collection to the regulated prefix, so the auditor gets the identity, time and source address without paying for object reads elsewhere. A detects deviations in API call rates rather than recording each object read. B duplicates control-plane events, adds a charged second copy of management events, and still omits object-level reads. D records API calls that crossed VPC endpoints, would miss access that did not use an endpoint, and enabling every supported event source is the opposite of a scoped, cost-effective selection.

*Where this is covered: Read the event before choosing the storage path.*

</details>

### 3. Capturing the right event categories (Associate)

A software company's security team must record three things in one account. First, every change to IAM policies. Second, every invocation of the one Lambda function that processes payment files. Third, the supported AWS API calls that a named VPC endpoint denied. The team already has a trail that logs read and write management events and wants to add only what these requirements need.

Which combination of steps will meet these requirements? (Select THREE.)

- **A)** Keep logging management events, which already record the IAM policy changes.
- **B)** Enable CloudTrail Insights and treat its events as the complete record of every invocation of the payment function.
- **C)** Rely only on management events, because they already include Lambda invocations and VPC endpoint denials.
- **D)** Add a Lambda data event selector scoped to the payment-processing function.
- **E)** Add a network activity event selector scoped to the supported event source and the named VPC endpoint.

<details><summary>Answer</summary>

**Answer: A, D and E.** A keeps the IAM control-plane changes the existing trail already captures. D adds the function's data-plane invocations, which management events never contain. E adds the endpoint activity, including the `VpceAccessDenied` records the third requirement asks for, scoped to one event source and one endpoint. B is wrong because Insights reports statistical deviations from a baseline rather than an entry per invocation, and it can take up to 36 hours to start. C is wrong for the same reason as B in reverse: management events are control-plane only, so they cover neither Lambda invocation nor VPC endpoint denials.

*Where this is covered: Read the event before choosing the storage path.*

</details>

### 4. Detecting changes to delivered evidence (Associate)

A regulated insurer delivers its CloudTrail log files to an S3 bucket in a separate log archive account. During the annual audit, the auditor must be able to determine whether any delivered log file was modified or deleted after CloudTrail wrote it to that bucket. The insurer wants cryptographic evidence rather than a procedural assurance, and it does not want to build and operate its own hashing and signing pipeline.

Which solution will meet these requirements?

- **A)** Enable CloudTrail Insights on the trail and review the Insights events.
- **B)** Enable CloudTrail log file integrity validation and verify the delivered digest files.
- **C)** Create an EventBridge archive of the account's CloudTrail events.
- **D)** Deploy an AWS Config conformance pack for logging controls.

<details><summary>Answer</summary>

**Answer: B.** Integrity validation hashes every delivered log file with SHA-256 and delivers hourly digest files signed with SHA-256 with RSA, each chained to the previous digest, so the auditor can detect modification or deletion without the insurer building anything. A detects unusual API call or error rates and says nothing about file contents. C stores events that matched a rule on the event bus and does not validate the trail's S3 objects. D evaluates resource configuration against rules and produces no cryptographic signature over CloudTrail log files.

*Where this is covered: Protect and validate trail evidence.*

</details>

### 5. Alerting on one sensitive API operation (Associate)

A payments company keeps its authoritative CloudTrail log files in S3 and queries them occasionally. Security operations now needs a containment workflow to start as soon as any principal disables a production encryption key. The gap between the API call and the start of the workflow must be as short as the services allow. The existing S3 evidence path must stay exactly as it is.

Which solution will meet these requirements with the LEAST latency?

- **A)** Run a weekly Athena query over the trail files and start the workflow from the results.
- **B)** Enable log file integrity validation and start the workflow when the next hourly digest arrives.
- **C)** Have an engineer search Event history after an application reports a key failure.
- **D)** Create an EventBridge rule that matches the CloudTrail API event for the key operation and targets the workflow.

<details><summary>Answer</summary>

**Answer: D.** CloudTrail publishes API activity to the default EventBridge event bus, so a rule on the `DisableKey` event can invoke the workflow within the delivery window while the trail keeps writing to S3 unchanged. The operation is a write management event, so an ordinary enabled rule matches it. A is bounded by a weekly schedule and is designed for historical SQL. B waits for an hourly digest and validates files rather than routing the event. C is manual and starts only after a failure is noticed, which is the slowest option of the four.

*Where this is covered: Search, alert and correlate.*

</details>

### 6. Organization-wide immutable evidence (Professional)

A healthcare company runs 60 accounts in AWS Organizations and expects to add more each quarter. Management activity from every present and future account, in every enabled Region, must reach a central log archive account. Workload administrators must not be able to modify the trail or overwrite retained evidence. The company does not want to onboard each new account by hand.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Have every member account create and own its own single-Region trail.
- **B)** Create a multi-Region organization trail from the management account or a CloudTrail delegated administrator.
- **C)** Grant member-account administrators permission to stop organization logging during maintenance windows.
- **D)** Keep the only copy of each account's events in that account's own CloudWatch Logs log group.
- **E)** Deliver to a tightly controlled, versioned S3 bucket in the log archive account and apply retention controls that prevent overwrite.

<details><summary>Answer</summary>

**Answer: B and E.** B covers the management account and every member account, adds the trail and its service-linked role automatically when an account joins, extends to each enabled Region, and cannot be modified or deleted from a member account. E separates evidence custody from workload administration and supplies the overwrite protection the stem requires. A fragments coverage, leaves each trail under workload control, and onboards nothing automatically. C deliberately opens the gap the stem forbids. D leaves evidence inside the accounts being audited and provides neither the central archive nor the retention controls.

*Where this is covered: Organization trails and central custody.*

</details>

### 7. A new customer's audit analytics platform (Associate)

In September 2026, a company that has never used CloudTrail Lake wants managed ingestion, queries and dashboards over its CloudTrail activity. It wants a path that continues to receive new features rather than only critical fixes. Its audit team separately needs durable raw log files that it can query with SQL a few times a year. An architect must recommend a design that reflects the current status of each service.

Which solution will meet these requirements?

- **A)** Create an account-level CloudTrail Lake event data store, because new customers retain access to Lake.
- **B)** Stop using CloudTrail trails, because the whole CloudTrail service is in maintenance mode.
- **C)** Keep CloudTrail collection, use the current Amazon CloudWatch data architecture for ingestion and dashboards, and query a trail's S3 files with Athena for the occasional SQL.
- **D)** Replace CloudTrail with AWS Config as a lossless record of every API event.

<details><summary>Answer</summary>

**Answer: C.** CloudTrail Lake closed to new customers on May 31, 2026, and AWS directs comparable new work to CloudWatch, while a trail to S3 queried with Athena remains the durable, low-cost path for occasional SQL. A contradicts the closure, which applies to account and organization event data stores alike. B is false: only Lake is closed, and trails, Event history, Insights and aggregated events are fully supported. D confuses resource configuration history with API activity; Config records what a resource looked like, not the identity and parameters of every call.

*Where this is covered: CloudTrail Lake availability change.*

</details>

### 8. Building a trustworthy automated timeline (Professional)

A response pipeline in a security tooling account receives CloudTrail events from 30 member accounts and can quarantine a resource automatically. During testing the team found that the same containment action ran twice for a single API call. Auditors also require the pipeline's case record to show both who changed a resource and what the resource's configuration became after the change. The team must fix both problems without reducing the evidence the baseline organization trail collects.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Make the containment action idempotent and deduplicate incoming events by event ID.
- **B)** Order the case timeline by S3 object arrival time, on the assumption that it matches API execution order.
- **C)** Treat the source IP address in each event as conclusive proof of the human actor.
- **D)** Correlate the CloudTrail identity and request data with AWS Config configuration history.
- **E)** Turn off management event logging on the baseline trail after the first response to reduce noise.

<details><summary>Answer</summary>

**Answer: A and D.** CloudTrail is designed for at-least-once delivery, and duplicates carry the same event ID, so A fixes the repeated containment exactly. D supplies the second requirement: CloudTrail names the actor and the request, and Config supplies the resource state that resulted. B is unsafe because log files are not an ordered stack trace and object arrival order is not an action timeline. C ignores assumed-role sessions, service principals and intermediaries, so it misattributes rather than proves. E removes baseline evidence and creates an audit gap, which the stem explicitly rules out.

*Where this is covered: Professional depth.*

</details>

## Summary

Start with the question and time window. Event history answers recent, one-Region management-event lookups for 90 days without a trail. A multi-Region trail delivers durable evidence to S3; make it an organization trail for present and future accounts. A single-Region trail outside us-east-1 receives no global service events, so IAM, AWS STS and CloudFront activity is missing from it. Management events describe control-plane calls, data events describe operations inside resources, network activity events describe supported API calls through VPC endpoints, and Insights identifies unusual call or error rates. Scope paid, high-volume categories with selectors while preserving baseline management activity. Protect the destination with cross-account custody, least privilege, encryption, retention controls and log file integrity validation. Use CloudWatch Logs for searches and metric alarms, EventBridge for event-driven response, Athena for SQL over S3, and Config beside CloudTrail when the resource state matters. CloudTrail Lake remains usable by existing customers, but it closed to new customers on May 31, 2026; new designs should use current CloudWatch capabilities or trails with S3 and Athena.

## Related units

- [Amazon CloudWatch](cloudwatch.md): log retention, metric filters, alarms and centralized analysis
- [AWS Config and detection services](../07-security/detection-and-compliance-services.md): resource-state history, compliance and finding correlation
- [AWS Organizations, IAM Identity Center and AWS Control Tower](../07-security/organizations-identity-center-and-control-tower.md): delegated administration and the log archive account pattern
- [AWS Identity and Access Management](../07-security/iam.md): interpreting principals, role sessions and least-privilege audit access
- [Amazon EventBridge](../06-integration/eventbridge.md): event patterns and response routing for CloudTrail API activity
- [Amazon S3](../01-storage/s3.md): versioning, Object Lock, lifecycle and protected log storage
- [Amazon Athena](../09-analytics/athena.md): partitioned SQL queries over historical CloudTrail files

## Sources

- [CloudTrail concepts](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html): events, Event history, trails, global service events and the `IncludeGlobalServiceEvents` rule
- [CloudTrail event history](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html): 90-day, one-account, one-Region management-event limits
- [CloudTrail event record contents](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html): identity, request, response, source and event fields
- [CloudTrail user identity element](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html): IAM users, role sessions and service identities
- [Logging management events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-management-events-with-cloudtrail.html): defaults, read and write selection and exclusions
- [Logging data events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html): data-plane resources, basic and advanced selectors and charges
- [Logging network activity events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-network-events-with-cloudtrail.html): supported `eventSource` values, `vpcEndpointId` and `errorCode` filters and `VpceAccessDenied`
- [Working with CloudTrail Insights](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-insights-events-with-cloudtrail.html): call-rate and error-rate baselines and prerequisites
- [Delivery of Insights events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/insights-events-understanding.html): the `/CloudTrail-Insight` folder and the 36-hour start delay
- [Costs for Insights events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/insights-events-costs.html): the free 28-day baseline and charging per event analyzed
- [Creating a trail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-create-and-update-a-trail.html): multi-Region console behavior and trail destinations
- [How CloudTrail works](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/how-cloudtrail-works.html): publishing about every 5 minutes, the 30-day redelivery window and its charges
- [Receiving CloudTrail log files from multiple Regions](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/receive-cloudtrail-log-files-from-multiple-regions.html): multi-Region coverage and new Regions
- [Creating a trail for an organization](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html): delegated administration, `AWSServiceRoleForCloudTrail`, opt-in Region behavior, validation failures and the organization bucket layout
- [CloudTrail log file integrity validation](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html): hourly digests, SHA-256 hashing and signing, the separate digest folder and per-Region key pairs
- [Encrypting CloudTrail log files with AWS KMS](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/encrypting-cloudtrail-log-files-with-aws-kms.html): customer-managed key configuration and policy needs
- [CloudTrail S3 bucket policy](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/create-s3-bucket-policy-for-cloudtrail.html): permissions required for centralized delivery
- [Sending events to CloudWatch Logs](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/send-cloudtrail-events-to-cloudwatch-logs.html): the IAM role CloudTrail assumes, organization-trail restrictions and the 256 KB event limit
- [Creating CloudWatch alarms for CloudTrail events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudwatch-alarms-for-cloudtrail.html): metric filters and alarms
- [Understanding CloudTrail events](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-events.html): event categories, record fields and non-API events
- [AWS service events delivered via AWS CloudTrail](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-service-event-cloudtrail.html): default-bus-only delivery, detail types and the read-only management event rule state
- [Query CloudTrail logs with Athena](https://docs.aws.amazon.com/athena/latest/ug/cloudtrail-logs.html): external tables and SQL over S3 trail files
- [Create a CloudTrail table using partition projection](https://docs.aws.amazon.com/athena/latest/ug/create-cloudtrail-table-partition-projection.html): the table DDL and projection properties
- [CloudTrail Lake availability change](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake-service-availability-change.html): May 31, 2026 closure, CloudWatch pipelines as the migration start and the network activity and Insights exclusions
- [Working with CloudTrail Lake](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html): event data stores, ORC, SQL and existing-customer capabilities
- [AWS CloudTrail pricing](https://aws.amazon.com/cloudtrail/pricing/): Event history, trail event copies and downstream cost dimensions
- [AWS CloudTrail FAQs](https://aws.amazon.com/cloudtrail/faqs/): at-least-once delivery and duplicate event IDs, the assumed role for CloudWatch Logs delivery, and the separate digest folder
