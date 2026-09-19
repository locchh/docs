# AWS cost management

**Where it sits on the exams.** AWS cost management is the group of services that measure, attribute, forecast and control what an AWS environment spends: **AWS Cost Explorer** for analysis and forecasting, **AWS Budgets** for thresholds and automated responses, **AWS Cost and Usage Reports (AWS CUR)** and **AWS Data Exports** for the raw billing line items, cost allocation tags and **AWS Cost Categories** for attribution, **AWS Cost Anomaly Detection** for unpredicted change, and **Savings Plans** and **Reserved Instances** for rate discounts. Domain 4 of SAA-C03 is worth 20 percent of that exam and this unit is its reference, covering tasks 4.1, 4.2, 4.3 and 4.4; on SAP-C02 it covers tasks 1.5, 2.5, 2.6, 3.3 and 3.5. The rule of thumb the exam rewards is a fixed order of operations: measure usage, attribute it with tags, remove or resize what is idle, change the architecture where a cheaper shape exists, and only then commit to a rate for what is left.

## What an AWS bill is made of

Every line on an AWS bill is the same shape: an account, a Region, a service, a usage type, an operation, a quantity and a rate. Cost management is the practice of slicing those line items by a dimension a human cares about, and the dimensions AWS gives you are account, Region, service, usage type, charge type, cost allocation tag and cost category. Everything else in this unit is a tool for doing that slicing, a control that fires when a slice crosses a threshold, or a purchase that lowers a rate.

The quantities that drive spend fall into a few charge shapes, and recognizing the shape is usually enough to answer an exam question without knowing a price. Time-based charges accrue per second or hour for as long as a resource exists, used or not: an **Amazon Elastic Compute Cloud (Amazon EC2)** virtual server, a **NAT gateway**, an interface VPC endpoint, a managed **Amazon Relational Database Service (Amazon RDS)** database, a public IPv4 address. Capacity-based charges accrue per GB-month stored, as with **Amazon Elastic Block Store (Amazon EBS)** network block volumes and **Amazon Simple Storage Service (Amazon S3)** objects. Request-based charges accrue per operation, as with S3 requests, reads and writes on **Amazon DynamoDB**, the managed NoSQL database, and invocations of **AWS Lambda**, the serverless function service. Data processing charges accrue per GB pushed through a NAT gateway, load balancer or VPC endpoint, and data transfer charges accrue per GB moved between places. A resource carries several at once, which is why "turn it off" usually beats "make it smaller": stopping an EC2 instance ends the time-based charge but leaves the EBS charge running.

The other half of the bill is what AWS does not charge for. The **AWS Free Tier** gives every account monthly allowances, including 100 GB of data transfer out to the internet each month aggregated across all services and Regions, excluding the China Regions and AWS GovCloud (US), and data transfer from the internet into AWS is not charged at all. An ingest-heavy workload therefore has no transfer bill and an egress-heavy one has a large and growing one.

All of these tools live in the AWS Billing and Cost Management console, alongside bills, payments, credits and billing preferences. Only the management account of an organization, or a standalone account, can manage cost allocation tags, cost categories and discount sharing preferences, which is the most common reason a member account cannot do something a scenario asks for.

The cost optimization pillar of the AWS Well-Architected Framework words the discipline as five design principles: implement cloud financial management, adopt a consumption model, measure overall efficiency, stop spending money on undifferentiated heavy lifting, and analyze and attribute expenditure. The third and fifth are the ones that need tooling rather than good intentions.

## The cost tools and what each one answers

The most common exam error is reaching for the wrong tool: Cost Explorer where the question needs per-resource detail, or a budget where it needs detection of something nobody set a threshold on. Read the table by the question in the second column, then check that the granularity and latency columns satisfy the scenario's wording.

| Tool | What it answers | Granularity | Latency |
|---|---|---|---|
| AWS Cost Explorer | Where did the money go, what is the trend, what should I commit to | Monthly and daily by default, 13 months of history plus the current month, 18-month forecast; hourly and resource-level on opt-in | Data refreshed at least once every 24 hours |
| Cost and Usage Report 2.0 in Data Exports | What exactly was charged, line item by line item, with resource IDs and tags | Hourly, daily or monthly line items per unique product, usage type and operation | First delivery up to 24 hours, then updated at least once a day and up to three times a day |
| AWS Budgets | Am I about to exceed a planned amount, and what should happen when I do | Cost, usage, and reservation or Savings Plans utilization and coverage, over daily, monthly, quarterly, annual or custom periods | Updated up to three times a day, typically 8 to 12 hours apart |
| AWS Cost Anomaly Detection | Did something change that nobody set a threshold for | Per service, member account, cost allocation tag value or cost category value | Up to 24 hours to detect an anomaly after the usage, and 10 days of history required before detection starts |
| AWS Compute Optimizer | Is this resource the right size, or idle | Per EC2 instance, Auto Scaling group, EBS volume, Lambda function, Fargate service, RDS and Aurora database, NAT gateway and more | 14 days of CloudWatch metrics by default, up to 93 days with enhanced infrastructure metrics; analysis up to 24 hours |
| Amazon S3 Storage Lens | Where is object storage growing, and which buckets break cost best practice | Organization, account, Region, storage class, bucket, and prefix on the advanced tier | Metrics collected daily; queryable for 14 days on the free tier and 15 months on the advanced tier |
| AWS Trusted Advisor | Which well-known waste patterns exist right now | Per check, per resource, with an organizational view | Checks refresh on a schedule, and can be refreshed manually |
| AWS Pricing Calculator | What would this cost before I build it | Per configured service and usage assumption | Immediate, because it models future usage rather than reading history |
| Cost Optimization Hub | Of all the recommendations across accounts and Regions, which ones are worth doing first | Per recommendation, deduplicated and priced against your own discounts | Follows the underlying recommendation sources |
| AWS Billing Conductor | What should each internal team or customer be shown as their cost | Per billing group, using pricing plans, rules and custom line items | Pro forma data, reconciled to usage at the end of each month |

Cost Explorer is the default answer whenever a question says "visualize", "identify the largest cost drivers", "forecast" or "get a Savings Plans recommendation". It presents cost and usage for the current month and up to the previous 13 months at daily and monthly granularity, forecasts the next 18 months, and refreshes at least once every 24 hours. When first enabled, the current month appears in about 24 hours and the rest takes a few days longer, and it cannot be disabled afterwards. The console is free; each paginated Cost Explorer API request carries a small charge, which is why a nightly script that pages through `GetCostAndUsage` for every account becomes a line item of its own. You can save up to 300 reports per account.

Three opt-in settings extend Cost Explorer beyond its defaults, each tested by a question asking for something the default view cannot show. Resource-level data at daily granularity names individual resources rather than services. Hourly granularity covers all AWS services for the previous 14 days without resource-level detail, which answers "we need to see the spike between 02:00 and 03:00". EC2 resource-level data at hourly granularity combines the two. Granular data is charged per usage record. Separately, multi-year data raises the history to 38 months at monthly granularity for the organization, becomes available within 48 hours of being enabled, and is switched off automatically if nobody looks at it for three consecutive months. Neither feature is available to accounts in a Billing Conductor standard billing group, which see pro forma rather than chargeable data.

Cost Explorer also carries the reports the commitment sections depend on: utilization reports, answering "how much of what we bought did we use", coverage reports, answering "how much of our eligible usage was bought", and purchase recommendations that propose an hourly commitment from measured history. High utilization with low coverage means buy more; low utilization means you over-committed, which is not reversible.

## Cost and Usage Reports, CUR 2.0 and Data Exports

When a question asks to investigate charges "at a granular level", to join billing data with something else, or to build a chargeback pipeline, the answer is the Cost and Usage Report and not Cost Explorer. AWS CUR contains the most comprehensive set of cost and usage data available, published to an S3 bucket you own and broken down by the hour, day or month, by product or product resource, and by the tags you define yourself, with a line item for each unique combination of product, usage type and operation. Every report carries `identity/`, `bill/` and `lineItem/` columns; other column families appear only if your usage generated them, so `savingsPlan/` columns exist only in months where you used Savings Plans.

The delivery timeline matters for scenario questions. The first delivery can take up to 24 hours, after which AWS updates the files at least once a day and up to three times a day. Each update is cumulative, holding the month to date, and mid-month figures are estimates. AWS finalizes usage charges after issuing the invoice and can still revise the report afterwards for credits, refunds and Support fees, which are calculated on final usage and appear on the sixth or seventh of the following month. A report can exceed a gigabyte and is split into several files once it passes roughly a million rows, which is why the standard consumption pattern is not a spreadsheet. You configure the report for integration with **Amazon Athena**, the serverless query service that runs SQL over data in S3, with **Amazon Redshift**, the managed data warehouse, or with **Amazon Quick**, formerly Amazon QuickSight, the serverless business intelligence service.

AWS Data Exports is the current front door for all of this and the name the exam will increasingly use. It creates recurring exports into S3 and lets you customize them with basic SQL: column selection, row filters and column aliasing. There are five export types. A standard data export offers four tables: Cost and Usage Report 2.0, cost optimization recommendations sourced from Cost Optimization Hub, FOCUS 1.0 and FOCUS 1.2 with AWS columns for the open FinOps cost specification, and carbon emissions. A cost and usage dashboard export deploys a prebuilt dashboard into Amazon Quick. A legacy data export produces the original CUR, which is still available but is reached through a different set of API actions.

AWS states plainly that CUR 2.0 is the new and recommended way to receive detailed cost and usage data, and names three improvements. CUR 2.0 has a fixed schema, where legacy CUR's columns vary month to month with your usage, tags and cost categories, which is the change that breaks fewest downstream pipelines over time. CUR 2.0 collapses `resource_tags`, `cost_category`, `product` and `discount` into nested key-value columns rather than sparse separate columns, and you can still query the nested keys as separate columns to match the old schema. It adds `bill_payer_account_name`, `line_item_usage_account_name`, `line_item_iam_principal` and `line_item_user_identifier`, the last two of which make "which principal created this spend" answerable from the bill itself. Both forms deliver to S3 in ZIP, GZIP or Parquet, and both integrate with Athena, Redshift and Amazon Quick; only CUR 2.0 supports the SQL customization and only CUR 2.0 is created through the Data Exports API and its CloudFormation resource type. When a scenario says an existing CUR pipeline must keep working while the team moves forward, the documented path is to create a CUR 2.0 export with an SQL query that reproduces the CUR schema.

The export is a delivery mechanism, so the costs attached to it are the S3 storage for the files and whatever you spend querying them, which makes Parquet output queried through Athena markedly cheaper than repeatedly scanning uncompressed CSV.

## Cost allocation tags and cost categories

Attribution is the part of cost management that cannot be retrofitted cheaply. A cost allocation tag is an ordinary resource tag that has additionally been activated for billing. AWS-generated tags are created and applied by AWS or an AWS Marketplace seller and carry the `aws:` prefix, such as `aws:createdBy`, which records who created a resource; user-defined tags are the ones you apply and appear with a `user:` prefix in billing data. Both kinds must be activated separately before they appear in Cost Explorer or a cost allocation report, and only the management account, or a standalone account, can activate them.

Two delays sit in that path and a question can turn on either. After you create and apply a user-defined tag, it can take up to 24 hours for the tag key to appear on the cost allocation tags page at all, and then up to a further 24 hours for the key to activate once you select it. Activating a key activates every value that shares it. The active cost allocation tag key quota is 500 per payer account and is adjustable through Service Quotas, and a single activate or deactivate request can carry 20 keys. The `awsApplication` tag, which is applied automatically to resources associated with an application defined in **AWS Service Catalog AppRegistry**, is activated for you and does not count against that quota.

The rule everyone misstates is retroactivity, so state it precisely. Activation is about the tag key; the tag value in a billing line item comes from the tag that was physically on the resource when the usage happened. A tag applied today does not label yesterday's usage, because yesterday's resource did not carry it, and activation does not change that. What AWS allows is a backfill: a management account user can request a backfill of cost allocation tags for up to twelve months, retroactively applying the tags' current activation status across those months. AWS is explicit that the resource tag must have been historically assigned to the resource for backfilled cost data to carry a value, so backfill recovers data for tags that existed but were never activated and recovers nothing for resources that were never tagged. It also works in reverse, removing a now-inactive tag from previous months. Only one backfill request is allowed every 24 hours, and Cost Explorer, Data Exports and CUR pick the change up on their normal refresh. The consequence for design questions is that a tagging standard must be enforced at creation time, through tag policies in **AWS Organizations**, required tags in CloudFormation or AWS Service Catalog launch constraints, or a tag-on-create condition in an IAM policy.

Cost categories solve the problem tags cannot: costs no resource tag will ever carry, such as Support charges, credits, taxes and untagged legacy resources. A cost category is a key-value pair applied to every cost line item by rules you define, and it appears as an extra dimension in Cost Explorer and Budgets, as a new column in the CUR, and as a monitor type in Cost Anomaly Detection. Rules match on account, charge type, Region, service, tag key, usage type, billing entity, or another cost category, using is, is not, is absent, contains, starts with and ends with. A regular rule assigns a fixed value; an inherited value rule takes the value from a dimension at evaluation time, so a rule inheriting from the `team` tag key generates one category value per team without listing them. You can set a default value for unmatched line items, nest categories to model teams inside business units, and add split charge rules that spread shared costs across the categories that consumed them.

The timing rules are the opposite of tags and that contrast is exam material. Cost categories are effective from the start of the current month: create or edit one on October 15 and every line item since October 1 is recategorized automatically. After a change the status shows Processing and can take up to 24 hours to become Applied across CUR, Cost Explorer and the other products. The quotas are 50 cost categories per management account, 500 rules per category through the API or 100 through the console, and 10 split charge rules per category. Only the management account or a standalone account can create and manage them.

## Budgets, budget actions and anomaly detection

AWS Budgets tracks cost and usage against a target you set and notifies you, or acts, when the target is approached or crossed. There are six budget types and the exam tests the first two against the last four. A cost budget sets a spending limit. A usage budget limits the usage amount of one or more services, which is how you stay inside a service limit rather than a dollar figure. A Reserved Instance utilization budget alerts when the proportion of reservations actually used falls below a threshold, and a coverage budget alerts when the proportion of instance hours covered by reservations does. Savings Plans utilization and coverage budgets do the same for Savings Plans. Utilization is about waste in what you bought; coverage is about opportunity in what you did not.

Budget periods can be daily, monthly, quarterly, annual or a custom period aligned to a fiscal year or project, and a target can be fixed or grow by a percentage each period. Budgets can track blended, unblended, net unblended, amortized or net amortized cost and can include or exclude discounts, refunds, Support fees and taxes, which is how a budget is made to agree with the number finance uses. Alerts fire on actual spend, after it has accrued, or on forecasted spend, before it has, and the forecasted alert is what a question asking to be warned "before" an overrun wants. Notifications go to email addresses, to an **Amazon Simple Notification Service (Amazon SNS)** topic, or both.

The older mechanism is still examinable: a CloudWatch billing alarm on the `EstimatedCharges` metric in the `Billing` namespace, which requires the Receive CloudWatch Billing Alerts preference and works only in the US East (N. Virginia) Region because billing metric data is stored there and represents worldwide charges. It triggers only when current charges exceed the threshold and never on a projection, unlike a forecasted budget alert. Budget data is updated up to three times a day, typically 8 to 12 hours apart. AWS states directly that there is a delay between incurring a charge and being notified, because usage is billed after it happens, so you can exceed a threshold before the alert arrives. That disqualifies AWS Budgets from any scenario demanding near-real-time enforcement, and is the reason to reject it as an answer to "stop the spend within minutes".

Budget actions turn a threshold into enforcement. When a budget crosses a threshold, an action runs automatically or after manual approval. Three action types exist: apply a custom IAM policy to a user, group or role; apply a service control policy to an organizational unit or account; or target specific EC2 or RDS instances and stop them. Budgets assumes an IAM role you create. From the management account you can apply an SCP to another account, but you cannot target EC2 or RDS instances in another account, which is the constraint that decides multi-account questions. Several actions can share one threshold, such as a deny policy blocking new EC2 provisioning plus a stop action on a development fleet. Quotas are 10 actions per budget, 100 budget actions per account and 20,000 budgets per management account. Monitoring and notifications are free; the first two action-enabled budgets each month are free and further ones carry a small daily charge, which is why "create a budget with an alert" is always a defensible low-cost answer.

Cost Anomaly Detection covers the case budgets cannot: spend that changes in a way nobody predicted. It applies machine learning to your spending patterns and raises an anomaly with a cost impact, an impact percentage, a severity and ranked potential root causes by service, account, Region and usage type. A monitor watches one of four dimensions: AWS services, linked account, cost allocation tag or cost category. An AWS managed monitor tracks every value in its dimension automatically, up to the top 5,000 by spend, and enrolls new accounts, tag values and category values as they appear. A customer managed monitor tracks values you name, up to 10 linked accounts or tag values or a single cost category value, aggregated together. Monitors for linked accounts, tags and cost categories can only be created in the management account.

An alert subscription decides who hears about it. Individual alerts fire as soon as an anomaly is detected and require an SNS topic; daily summaries email the top 10 alerts from the previous day at 00:00 UTC; weekly summaries send one roundup. Each subscription carries an absolute or percentage threshold, and two thresholds can be combined with AND or OR. Anomalies below the threshold are still detected and still appear in the console; the threshold governs notification only. The numbers that decide questions are that an anomaly is detected up to 24 hours after the usage and that 10 days of history are required before detection works, so a new account cannot be protected this way on day one. It does not analyze every service: AWS Support, WorkSpaces, Cost Explorer, Budgets, AWS Shield, Amazon Route 53, AWS Certificate Manager and most of AWS Marketplace are excluded, and it analyzes only the Usage charge type on net unblended cost. Quotas allow 500 customer managed monitors and 100 alert subscriptions per account.

> **Professional depth.** Budgets and anomaly detection answer different halves of one question and a Professional scenario usually needs both: a forecasted-cost budget per business unit cost category with a deny SCP action on the sandbox organizational unit, plus an AWS managed monitor on the linked account dimension so new accounts join coverage automatically. Neither is fast, so a requirement for hard prevention rather than notification keys to a service control policy or a quota, not a cost tool.

## Savings Plans and Reserved Instances

A commitment lowers the rate you pay in exchange for a promise about future usage, and it does not reserve capacity unless the specific instrument says it does. The Amazon EC2 unit teaches the purchasing options in depth for compute; what matters here is the cross-service commitment model, because the exam asks which instrument covers which usage and how much freedom it leaves you. Read the table by the two questions a scenario always implies: what will this cover, and what am I forbidden to change.

| Commitment | What it covers | Flexibility | Term and payment |
|---|---|---|---|
| **Compute Savings Plans** | EC2 instance usage regardless of family, size, Region, operating system or tenancy, plus AWS Lambda usage and **AWS Fargate**, the serverless container compute engine, up to 66 percent off On-Demand | The most flexible. Move `c5` to `m5`, Ireland to London, or EC2 to ECS on Fargate and keep the discount | 1 or 3 years, All Upfront, Partial Upfront or No Upfront |
| **EC2 Instance Savings Plans** | Usage of one instance family in one Region, up to 72 percent off On-Demand | Size, operating system and tenancy are free to change inside that family and Region; family and Region are locked | 1 or 3 years, same three payment options |
| **Database Savings Plans** | Aurora, Amazon RDS, DynamoDB, ElastiCache, DocumentDB, Timestream, Neptune, Keyspaces, DMS and Amazon OpenSearch Service, up to 35 percent off | Applies to the latest provisioned instance generations regardless of engine, family, size, Availability Zone or Region, and to serverless usage; covers moves such as RDS for Oracle to Aurora PostgreSQL | 1 or 3 years, same three payment options |
| **SageMaker AI Savings Plans** | **Amazon SageMaker AI**, the managed machine learning platform, up to 64 percent off | Free across family, size, Region and component, so training usage can become inference usage | 1 or 3 years, same three payment options |
| **Standard Reserved Instances** | A specific instance configuration for EC2, RDS, ElastiCache, OpenSearch, Redshift and others, at the deepest reservation discount | Can be modified, not exchanged. Regional scope adds Availability Zone flexibility and, on Linux or Unix with default tenancy, instance size flexibility within the family | 1 or 3 years, same three payment options |
| **Convertible Reserved Instances** | The same usage, at a smaller discount than Standard | Can be exchanged for another Convertible reservation with different attributes | 1 or 3 years, same three payment options |
AWS now recommends Savings Plans over Reserved Instances for most new commitments, because the flexibility costs little discount. | **Zonal Reserved Instances** | A specific configuration in one Availability Zone | Least flexible, and the only commitment here that also reserves capacity in its Availability Zone | 1 or 3 years, same three payment options |

A Savings Plan is a commitment to spend a stated number of dollars per hour for one or three years, where one year means 365 days and three years means 1,095 days. Commitment terms cannot be changed after purchase, so a plan cannot be canceled, resized or returned; if usage grows you buy an additional plan. Each hour's commitment is usable only within that hour and does not carry over.

The order in which discounts apply decides several exam answers. EC2 Reserved Instances apply first. Savings Plans apply to what remains, with EC2 Instance Savings Plans applied before Compute Savings Plans because Compute plans have broader applicability. Within a plan, AWS computes the savings percentage of each eligible usage against its On-Demand rate and applies the commitment to the highest savings percentage first, breaking ties by the lowest Savings Plans rate, and continues until either usage or commitment runs out. Usage beyond the commitment is charged at On-Demand rates. Plans never apply to Spot Instances, and the per-Region Dedicated Instance fee is not discounted by any Savings Plan. Both Compute and EC2 Instance plans cover the EC2 instances underneath clusters of **Amazon EMR**, the managed big data platform, **Amazon Elastic Kubernetes Service (Amazon EKS)** and **Amazon Elastic Container Service (Amazon ECS)**, the managed Kubernetes and container orchestration services, but the EKS control plane charge is not covered.

Sizing a commitment is a measurement problem. Cost Explorer produces Savings Plans and Reserved Instance purchase recommendations from measured history, and the utilization and coverage reports say afterwards whether the purchase was right. Commit to the floor of usage rather than the average: a plan sized to the lowest hour of a typical week is almost always fully used, and the uncovered peak is bought at On-Demand or Spot rates. Commitment is the last step in the optimization order, because a three-year plan sized against an oversized fleet locks in the waste for three years.

## Consolidated billing, discount sharing and access control

Consolidated billing is the AWS Organizations feature that makes one management account pay the charges of every member account. It costs nothing extra and gives three things the exam asks about: one invoice per seller of record, combined cost and usage data, and combined usage for pricing purposes. The last is the substantive benefit. For tiered services, AWS treats all accounts in the organization as a single account when measuring monthly usage, so member accounts do not each climb the S3 storage tiers from zero. Member account bills are informational, because the management account may reallocate the volume, reservation and Savings Plans discounts the organization earned.

Reserved Instance and Savings Plans discounts are shared across the organization by default, and the rule has a consistent shape: the commitment benefits the owning account first, and only surplus flows elsewhere. AWS assigns reservation hours starting with the purchasing account and then to other accounts running identical usage types in the same Availability Zone, applying a regional reservation to the smallest instance in the family first and upward by normalization factor. Savings Plans behave the same way, and only if sharing is enabled. Both the purchasing and the receiving account must have sharing activated, and if a Savings Plans owner account leaves the organization the plan stops applying to the consolidated bill.

Turning sharing off is a management account action, taken in Billing preferences under the Reserved Instances and Savings Plans discount sharing preference by selecting accounts and choosing Deactivate, with a Deactivate All option for the whole organization. Three sharing modes exist. Organization-wide sharing maximizes the overall discount rate by letting surplus flow anywhere. Prioritized group sharing serves defined account groups after the owner and then lets the remainder flow organization-wide. Restricted group sharing confines surplus to defined groups even when that leaves commitment unused. Groups are defined with cost categories on the Accounts dimension, each account belongs to at most one group, and the payer account cannot be in a group. The final monthly bill uses the preferences in force at 23:59:59 UTC on the last day of the month. The tradeoff to state is exact: deactivating sharing makes each team's bill reflect its own purchases and can raise the organization total, because surplus commitment goes unused.

Blended and unblended rates fall out of this. The unblended rate is the rate actually applied to a line item and is what member accounts see; a reservation line item has an unblended cost of zero because the reservation charge sits with the purchasing account. The blended rate is the organization's average rate for a usage type, total cost divided by total usage, and allocating it back shows each account a fair share of a shared discount rather than an accidental windfall. Budgets can track either.

**AWS Billing Conductor** exists when that is not enough. It is a custom billing service for AWS channel partners and for organizations with chargeback requirements, producing a second version of the cost data called pro forma cost from billing groups, pricing plans, pricing rules and custom line items. You can apply global or per-service markups and discounts, control free tier access, and add flat or percentage charges and credits. Accounts in a billing group see pro forma costs in Cost Explorer, their CUR and their budgets, and a designated primary account sees the whole group. The sentence to remember is that Billing Conductor does not change the actual AWS invoice or the underlying sharing of credits and commitment discounts; it changes what a billing group is shown.

Access is off by default. IAM users and roles cannot open the Billing and Cost Management console even when their policies grant billing actions, until the account root user turns on the Activate IAM Access setting once per account, which is on by default for newly created member accounts. That setting gates the Bills, Budgets, CUR, cost categories, cost allocation tags, billing preferences, Cost Explorer and reservation report pages, but not Cost Anomaly Detection, the Billing and Cost Management SDK APIs or the in-console Pricing Calculator. Activating it grants nothing on its own, so you still attach policies carrying the fine-grained billing actions. Billing views give finer control still, exposing cost management data as a resource with an ARN that identity-based and resource-based policies can reference.

## Rightsizing, idle resources and managed services

Rightsizing is the move with the largest verified return in most environments. **AWS Compute Optimizer** analyzes resource configuration and CloudWatch utilization metrics and returns rightsizing recommendations plus idle resource findings for EC2 instances, EC2 Auto Scaling groups, EBS volumes, Lambda functions, ECS services on Fargate, commercial software licenses, Aurora and RDS databases, NAT gateways, DynamoDB, ElastiCache, MemoryDB, DocumentDB, WorkSpaces and SageMaker. You must opt in, and a management account can opt in for the organization and see findings across accounts and Regions. It analyzes the last 14 days of metrics by default, using the maximum utilization point in each five-minute interval, and analysis can take up to 24 hours. The enhanced infrastructure metrics preference extends the lookback to 93 days for a charge, which is what a scenario with monthly or quarterly peaks needs.

What Compute Optimizer cannot see is the detail exam questions turn on. **Amazon CloudWatch**, the AWS monitoring service, does not collect guest memory utilization from an EC2 instance, so Compute Optimizer analyzes `MemoryUtilization` only for instances running the CloudWatch agent or ingesting memory metrics from a supported external observability product, and GPU metrics have the same requirement. Without the agent, recommendations come from CPU, network and disk alone, which systematically under-detects memory-bound instances.

**Cost Optimization Hub** consolidates all of it, aggregating rightsizing, idle resource, Savings Plans and Reserved Instance recommendations across accounts and Regions into one prioritized list, deduplicating overlaps and pricing the savings against your own commercial terms rather than list rates. It is the answer when a central team must rank opportunities across an organization instead of reading each service console.

**AWS Trusted Advisor** is the checklist view and is taught in full in its own unit. Its cost optimization category finds the classic waste patterns: low-utilization EC2 instances, long-stopped instances, unassociated Elastic IP addresses, underutilized or unattached EBS volumes, idle load balancers, idle NAT gateways and interface endpoints, buckets without lifecycle policies, and reservation and Savings Plans purchase opportunities. Its cost optimization category is available with Business Support Plus, Enterprise Support or AWS Unified Operations, so Developer Support, although paid, does not unlock it. AWS has announced that Developer Support, Business Support and Enterprise On-Ramp end on January 1, 2027, leaving Business Support+ and Enterprise Support, so plan names in older material may not match the console.

**Amazon S3 Storage Lens** is the equivalent for object storage and the tool SAP-C02 names alongside Compute Optimizer for rightsizing visibility. Its free tier gives daily metrics across summary, cost optimization, data protection, access management, performance and event categories, at organization, account, Region, storage class and bucket level, queryable for 14 days. The advanced tier adds activity and detailed status code metrics, advanced cost optimization and data protection metrics, prefix-level aggregation, contextual recommendations, publishing to CloudWatch and a 15-month query window, for a charge based on objects monitored. Prefix-level activity metrics identify the cold prefixes that justify a lifecycle transition, and exist only on the advanced tier.

Two decisions sit above the tooling. The first is whether to run a managed service at all. A managed offering charges more per unit of raw capacity and removes the patching, failover engineering and staffing behind it, which is why SAP-C02 treats "AWS managed service offerings" as a cost topic. Aurora Serverless instead of a fleet sized for peak, Fargate instead of a partly idle EC2 cluster, DynamoDB on-demand instead of provisioned capacity nobody tunes: each trades a higher unit rate for the elimination of idle capacity and of labor, and the exam keys the managed option when the stem says "least operational overhead" and the self-managed one only when the workload is steady, large and already staffed. The second decision is to model before building, which is what **AWS Pricing Calculator** is for: a free web tool that estimates cost for configured services, groups estimates to match an architecture, shows the calculation behind each price, exports to CSV or PDF, and takes its prices from the AWS Price List API. It models future usage, so it answers "estimate the cost before migration" and never "analyze what we spent".

## Data transfer costs

Data transfer is the cost category that architecture decides and that no purchasing option discounts, which is why both exam guides name it separately. Five rules cover almost every question. First, traffic between Availability Zones in the same Region is metered as the usage type `{Region}-DataTransfer-Regional-Bytes`, and AWS charges a given resource for both inbound and outbound traffic, so a single cross-zone transfer produces two line items. The usage type exists only for traffic that crosses a zone boundary. Traffic that stays inside one Availability Zone over private IPv4 addresses is not charged, which the VPC pricing page states directly in its NAT gateway worked example: there is no charge for the transfer between the NAT gateway and the instance because the traffic stays in the same Availability Zone using private addresses. Co-locating chatty components therefore removes the charge entirely, and some services provide in-Region traffic at no cost, which the service's own pricing page states. Data sent over a VPC peering connection that crosses an Availability Zone in the same Region is charged in both the in and out directions. The design tension is explicit: multi-Availability-Zone deployment buys resilience and costs cross-zone transfer, so "reduce cost without reducing availability" means keeping chatter inside a zone, not collapsing to one zone.

Second, traffic between Regions produces two line items, one for data in at the destination and one for data out at the source, and only the outbound item at the source Region carries a charge. A cross-Region read replica, a cross-Region S3 replication rule and a multi-Region active-active design therefore all cost in proportion to the bytes leaving the source.

Third, data transfer out to the internet is charged per GB as `{Region}-DataTransfer-Out-Bytes` after the free allowance, while transfer in is free. Egress is the dimension that grows with a successful public-facing product, and it is the one **Amazon CloudFront**, the AWS content delivery network, exists to reduce. CloudFront charges for data transfer out to viewers and for requests, but transfer between CloudFront and your AWS origins is waived when you serve traffic through CloudFront, and Amazon S3 lists data transferred out to CloudFront at no charge. Putting CloudFront in front of an S3 bucket or a load balancer replaces per-GB origin egress with cached delivery at CDN rates, which is why "reduce data transfer costs for a global audience" keys to CloudFront and not to more Regions.

Fourth, the endpoint decision. A NAT gateway is billed per NAT gateway-hour that it is provisioned plus a data processing charge for every GB that passes through it, and traffic reaching Amazon S3 through a NAT gateway pays that processing charge on top of the S3 request. A gateway VPC endpoint for S3 or DynamoDB has no hourly and no data processing charge at all, so routing private subnet traffic to those two services through a gateway endpoint is strictly cheaper than routing it through a NAT gateway, as well as keeping the traffic off the internet. An interface VPC endpoint, powered by **AWS PrivateLink**, is billed for each hour the endpoint is provisioned in each Availability Zone plus a per-GB data processing charge regardless of the traffic's source or destination, so for other services the comparison is real arithmetic: an interface endpoint wins on high, steady volume and a NAT gateway can win for a small VPC with occasional outbound traffic, because the endpoint's hourly charge multiplies by the number of zones. Trusted Advisor's inactive NAT gateway and inactive interface endpoint checks exist because both keep billing when nothing flows through them.

Fifth, addresses and links. **Amazon Virtual Private Cloud (Amazon VPC)** charges an hourly rate for every public IPv4 address, at the same rate whether it is in use or idle, covering addresses on EC2 instances, Elastic Load Balancing, RDS databases, Elastic IP addresses, **AWS Global Accelerator**, the anycast network entry point, and AWS Site-to-Site VPN endpoints; BYOIP addresses are not charged. That turns an unused Elastic IP into a recurring line item and makes IPv6 and private-only subnets a cost decision. **AWS Direct Connect**, the dedicated network connection to AWS, charges port hours plus data transfer out at rates lower than internet egress, which is the comparison behind any question weighing a dedicated line against a VPN for sustained high volume.

## Professional depth

At organization scale, cost management becomes an operating model rather than a set of consoles. The management account is the only place cost allocation tags, cost categories and discount sharing preferences can be set, so a Professional design centralizes those and pushes everything else outward: a dedicated billing account receives the CUR 2.0 export into S3, Athena and Amazon Quick sit on top of it, and teams get a billing view or a cost category filter rather than management account access. Tag enforcement moves to creation time through Organizations tag policies, Service Catalog launch constraints and IAM conditions on `aws:RequestTag`, because backfill recovers only tags that were physically present on the resource. An AWS managed anomaly monitor on the linked account dimension is the one control that keeps pace with account creation.

Migration-scale work fails in a predictable order. Commitments bought from pre-migration estimates are the most expensive mistake available, because a Savings Plan cannot be canceled, resized or returned, so the sequence is to migrate on On-Demand, rightsize with Compute Optimizer after at least 14 days of metrics and preferably 93 with enhanced infrastructure metrics, and only then commit to the measured floor. The Pricing Calculator is the planning instrument before the move and Cost Explorer recommendations the instrument after it. Where peaks are monthly or quarterly, the 14-day default lookback recommends an instance too small, which is why enhanced infrastructure metrics exists.

The quotas that bite appear in scenarios as hidden constraints: 500 active cost allocation tag keys per payer account, 50 cost categories with 500 rules and 10 split charge rules each, 20,000 budgets per management account but only two free action-enabled budgets per month, 10 actions per budget, one tag backfill request every 24 hours, and a charge on every paginated Cost Explorer API request that makes a per-account polling loop a real cost. Latency is the other hidden constraint: budgets refresh up to three times a day, anomaly detection can take 24 hours and needs 10 days of history first, and CUR data is an estimate until the invoice closes. None of these enforces a ceiling in minutes; a service control policy, a service quota or a budget action attaching a deny policy is what stops provisioning.

A Professional question usually extends an Associate cost scenario by adding accountability. The Associate version asks which team is spending the money and keys to cost allocation tags plus Cost Explorer. The Professional version adds that one business unit bought a three-year commitment and objects to subsidizing another, which turns the answer into restricted or prioritized group sharing defined by a cost category on the Accounts dimension, with the tradeoff stated plainly: restricting sharing protects the buyer's bill and can raise the organization total. Where the requirement is only to show a different number, Billing Conductor's pro forma costs are the answer, because they never alter the AWS invoice.

## Worked scenario

A media company runs 60 AWS accounts under one organization: three production accounts, a batch transcoding account, a shared services account holding NAT gateways and inspection, and a long tail of team sandboxes. The bill has grown 40 percent in two quarters, nobody can say which product line drives it, and finance wants each of four business units charged for what it uses without capping engineering. Egress to viewers is the largest line item.

Attribution comes first. The management account activates a `product`, `env` and `cost-center` tag set, an Organizations tag policy plus IAM `aws:RequestTag` conditions stop untagged resources being created, and a twelve-month backfill recovers history for resources that already carried the tags. Four cost categories map accounts and tag values to business units, with a split charge rule spreading the shared services account across them, and a CUR 2.0 export lands in a dedicated billing account for Athena and Amazon Quick. Each business unit gets a forecasted-cost budget on its cost category, an AWS managed anomaly monitor watches the linked account dimension, and the sandbox organizational unit gets a budget action attaching a deny service control policy at 100 percent of plan.

Then the cost work. Compute Optimizer, with the CloudWatch agent installed so memory is visible and enhanced infrastructure metrics enabled for the quarterly peak, resizes the production fleet, and Cost Optimization Hub ranks the findings across all 60 accounts. CloudFront goes in front of the viewer-facing origins, removing per-GB origin egress because transfer from AWS origins into CloudFront is waived. Gateway VPC endpoints replace NAT gateway paths to S3 and DynamoDB at no hourly or processing charge, and idle Elastic IPs are released because public IPv4 addresses bill whether used or not. Only after two months of stable, resized usage does the organization buy Compute Savings Plans sized to the floor of hourly usage, leaving the transcoding peak on Spot. Sharing stays organization-wide except for the business unit that funded its own commitment, which goes into a restricted sharing group defined by a cost category.

When the exam asks about this scenario, it usually asks how to charge each business unit accurately while keeping one AWS invoice. The keyed answer is cost allocation tags plus cost categories with a split charge rule, reported from Cost Explorer and the CUR, under consolidated billing. Billing Conductor is the distractor unless the teams must see marked-up or contractual prices.

## Exam lens

- "Visualize spend trends and identify the largest cost drivers over the last year" maps to Cost Explorer; the CUR is the distractor when no line-item detail is required.
- "Investigate charges at the individual resource level" maps to the Cost and Usage Report or Cost Explorer resource-level granularity; default views name services, not resources.
- "Alert me before we exceed the monthly budget" maps to a cost budget with a forecasted-spend alert; an actual-spend alert fires after the money is gone.
- "Stop new provisioning automatically when spend hits a threshold" maps to a budget action attaching a deny IAM policy or SCP; a notification enforces nothing.
- "Detect unexpected spend nobody set a threshold for" maps to Cost Anomaly Detection; a budget only fires on a number you predicted.
- "Attribute costs to teams, including last quarter's resources" maps to cost allocation tags plus a backfill, which recovers values only where the resource carried the tag.
- "Steady compute spend that may move between families, Regions or to Fargate and Lambda" maps to a Compute Savings Plan; an EC2 Instance Savings Plan locks family and Region.
- "Reduce spend across Aurora, RDS and DynamoDB with one commitment" maps to a Database Savings Plan.
- "Guarantee capacity in an Availability Zone as well as a discount" maps to a zonal Reserved Instance or a Capacity Reservation; Savings Plans reserve no capacity.
- "One business unit must not subsidize another's reservations" maps to deactivating discount sharing for those accounts, or to restricted group sharing, and raises the organization's total bill.
- "Show a marked-up bill without changing the AWS invoice" maps to AWS Billing Conductor pro forma costs.
- "Identify oversized or idle instances across many accounts" maps to Compute Optimizer, ranked by Cost Optimization Hub; memory-bound instances need the CloudWatch agent first.
- "Find the buckets and prefixes driving storage growth" maps to S3 Storage Lens, prefix-level metrics being advanced tier only.
- "Estimate cost before the workload exists" maps to the Pricing Calculator; Cost Explorer forecasts only from history you have.
- "Cut the cost of private subnet access to Amazon S3" maps to a gateway VPC endpoint, which has no hourly or data processing charge, not a NAT gateway.
- "Reduce egress cost for a global audience" maps to CloudFront, since transfer from AWS origins is waived.
- "Reduce in-Region transfer cost without losing availability" maps to keeping chatty traffic inside one Availability Zone, since cross-zone transfer is charged both ways.

- "Reduce data transfer cost for a global audience" maps to Amazon CloudFront, whose egress is cheaper than direct S3 or EC2 egress and which charges nothing for the origin fetch from AWS. AWS Global Accelerator is the distractor here: it adds an hourly accelerator charge and a per-GB premium on top of standard egress, because it buys latency and fast failover rather than lower cost.

## Knowledge check

### 1. Finding the instances behind a spike (Associate)

A company's monthly AWS bill rose sharply last week. The finance team needs to see which individual Amazon EC2 instances drove the increase, broken down hour by hour, for the previous seven days. The company does not want to build or run any data pipeline.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create an AWS Budgets usage budget for Amazon EC2 and review the alert history.
- **B)** Model the affected instances in the AWS Pricing Calculator and compare the estimate with the invoice.
- **C)** Enable hourly granularity and EC2 resource-level data in Cost Explorer and review the last seven days.
- **D)** Create a CUR 2.0 export to Amazon S3, configure Amazon Athena, and query the line items.

<details><summary>Answer</summary>

**Answer: C.** Cost Explorer's opt-in granular data covers hourly cost for the previous 14 days and resource-level detail for EC2, which is exactly the window and the granularity the stem asks for, and it is a console setting rather than a pipeline. A is wrong because a usage budget tracks an amount against a threshold and never names a resource. B is wrong because the Pricing Calculator models future usage from assumptions and reads no historical data at all. D would produce the right answer but requires creating an export, a bucket and an Athena workgroup, which is more operational overhead than the stem allows.

*Where this is covered: The cost tools and what each one answers.*

</details>

### 2. Tagging after the fact (Associate)

A company applied a `cost-center` tag to all of its resources three months ago but only activated the tag key in the Billing console yesterday. Finance now wants cost reported by cost center for the previous six months.

Which solution will meet these requirements?

- **A)** From the management account, request a cost allocation tag backfill covering the previous six months, and accept that only the months in which resources already carried the tag will show values.
- **B)** Activate the tag key in each member account so that AWS regenerates the historical billing data for those accounts.
- **C)** Create a cost category with an inherited value rule on the `cost-center` tag key, because cost categories are applied to all historical data.
- **D)** Delete and re-create the Cost and Usage Report with a start date six months in the past.

<details><summary>Answer</summary>

**Answer: A.** A management account user can request a backfill of cost allocation tags for up to twelve months, which retroactively applies the tags' activation status, and AWS states that the tag must have been historically assigned to the resource for the backfilled data to carry a value. B is wrong because only the management account or a standalone account can activate cost allocation tags, and activation does not regenerate history. C is wrong because cost categories are effective from the start of the current month, not across all history. D is wrong because a new report carries data from its creation forward and cannot recover unlabeled past usage.

*Where this is covered: Cost allocation tags and cost categories.*

</details>

### 3. Trimming a transfer bill (Associate)

An application runs on EC2 instances in private subnets that write large objects to Amazon S3 through a NAT gateway. The same application serves large media files to a worldwide audience through an Application Load Balancer, and internet egress is now the largest line on the bill.

Which combination of steps will meet these requirements MOST cost-effectively? (Select TWO.)

- **A)** Create a gateway VPC endpoint for Amazon S3 and route the private subnets to it.
- **B)** Replace the NAT gateway with a self-managed NAT instance in each Availability Zone.
- **C)** Move the EC2 instances into public subnets and give each one a public IPv4 address.
- **D)** Create an Amazon CloudFront distribution in front of the Application Load Balancer.
- **E)** Create an interface VPC endpoint for Amazon S3 in each Availability Zone.

<details><summary>Answer</summary>

**Answer: A and D.** A gateway VPC endpoint for S3 has no hourly and no data processing charge, so it removes both the NAT gateway processing charge and the internet path for that traffic. CloudFront charges for delivery to viewers but data transfer from AWS origins into CloudFront is waived, so caching in front of the load balancer replaces per-GB origin egress. B is a custom build of something AWS manages and adds instance, patching and availability work without removing per-GB cost. C removes the NAT charge but adds a per-hour public IPv4 charge for every instance and exposes them directly. E would work but an interface endpoint bills per endpoint per Availability Zone per hour plus per GB processed, so it is strictly more expensive than the free gateway endpoint for S3.

*Where this is covered: Data transfer costs.*

</details>

### 4. Stopping a sandbox from growing (Associate)

A company gives each engineering team a sandbox account inside its AWS organization. When a sandbox is forecast to exceed its monthly allowance, no new resources may be created in it until the next month, without an administrator intervening.

Which solution will meet these requirements?

- **A)** Create an AWS Budgets cost budget with an Amazon SNS notification at 100 percent of the forecasted amount.
- **B)** Create an AWS Cost Anomaly Detection monitor for the sandbox accounts with individual alerts.
- **C)** Create an AWS Budgets usage budget with an email alert to the team and to the administrator.
- **D)** Create an AWS Budgets cost budget with a budget action that attaches a deny service control policy to the sandbox organizational unit at the threshold.

<details><summary>Answer</summary>

**Answer: D.** A budget action can apply a service control policy from the management account when a threshold is crossed, and running it automatically rather than with manual approval is what removes the administrator from the loop. A notifies but enforces nothing. B detects unexpected spend rather than planned overrun and also only notifies. C tracks usage rather than cost and still only sends email. Note that budget data refreshes up to three times a day, so this control is a boundary, not a real-time stop.

*Where this is covered: Budgets, budget actions and anomaly detection.*

</details>

### 5. Committing during a migration (Professional)

A company runs a steady compute floor across three AWS Regions. Over the next twelve months it will move roughly half of that workload from EC2 instances to AWS Fargate, and it expects to change instance families as it modernizes. Finance wants a commitment discount now but refuses any purchase that could be stranded by the migration.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Purchase EC2 Instance Savings Plans for each instance family and Region currently in use.
- **B)** Purchase a Compute Savings Plan sized to the floor of hourly compute spend and leave the variable remainder on On-Demand.
- **C)** Purchase Convertible Reserved Instances for the current instance types and exchange them after each migration wave.
- **D)** Purchase zonal Reserved Instances in every Availability Zone in use so that capacity is also reserved.

<details><summary>Answer</summary>

**Answer: B.** A Compute Savings Plan applies regardless of instance family, size, Region, operating system or tenancy and also covers Fargate and Lambda, so it follows the workload through exactly the changes described, and sizing to the floor rather than the average avoids buying commitment that will go unused. A is wrong because an EC2 Instance Savings Plan locks family and Region, which is precisely what will change. C is wrong because Convertible Reserved Instances do not cover Fargate at all, so half the workload would leave the commitment behind. D is wrong because zonal reservations are the least flexible instrument and the stem asks for no capacity guarantee.

*Where this is covered: Savings Plans and Reserved Instances.*

</details>

### 6. Rightsizing a memory-bound fleet (Associate)

A company suspects that many of the EC2 instances across its twelve AWS accounts are oversized, and that the binding resource is memory rather than CPU. It wants AWS to produce rightsizing recommendations that take memory into account, viewed centrally.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable EC2 detailed monitoring on every instance.
- **B)** Install the Amazon CloudWatch agent on the instances so that memory utilization is published.
- **C)** Enable hourly granularity in Cost Explorer for the twelve accounts.
- **D)** Create an AWS Budgets usage budget for Amazon EC2 in each account.
- **E)** Opt in to AWS Compute Optimizer from the organization's management account.

<details><summary>Answer</summary>

**Answer: B and E.** CloudWatch does not collect guest memory utilization, so Compute Optimizer analyzes the memory metric only for instances running the CloudWatch agent or ingesting memory from a supported external product; without it, recommendations come from CPU, network and disk alone. Opting in from the management account is what gives findings across all accounts and Regions in one view. A only raises the EC2 metric frequency from five minutes to one minute and still publishes no memory metric. C shows spend by hour but measures no utilization headroom. D tracks a usage threshold and produces no recommendation.

*Where this is covered: Rightsizing, idle resources and managed services.*

</details>

### 7. A business unit that funded its own commitment (Professional)

An organization has 30 member accounts. One business unit purchased a three-year Compute Savings Plan in its own account, sized to its own usage. Another business unit's usage is now absorbing part of that discount, and the first business unit wants its own invoice to reflect only its own purchases. Leadership wants the tradeoff stated before the change is made.

Which solution will meet these requirements?

- **A)** Move the Savings Plan purchase into the organization's management account so that the discount is centrally owned.
- **B)** Create a cost category that allocates the full Savings Plan cost to the purchasing business unit.
- **C)** In the management account's billing preferences, place the purchasing business unit's accounts in a restricted sharing group, accepting that unused commitment may raise the organization's total bill.
- **D)** Enable AWS Billing Conductor and create a billing group for the purchasing business unit.

<details><summary>Answer</summary>

**Answer: C.** Reserved Instance and Savings Plans discount sharing is controlled from the management account's billing preferences, and restricted group sharing confines surplus benefit to a defined group of accounts even when that leaves commitment unused, which is exactly the requirement and exactly the tradeoff. A is wrong because a management account purchase shares more widely, not less. B is wrong because a cost category relabels how costs are grouped and cannot change which account's usage a discount is applied to. D is wrong because Billing Conductor produces pro forma costs for display and explicitly does not change the actual invoice or the underlying commitment discount sharing.

*Where this is covered: Consolidated billing, discount sharing and access control.*

</details>

### 8. Spend nobody predicted (Associate)

A misconfigured nightly job quadrupled one service's cost for four days before anyone noticed. The company wants to be told automatically when spending departs from its normal pattern, for any service, including services it does not use today.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create an AWS managed Cost Anomaly Detection monitor on the AWS services dimension with an alert subscription that sends individual alerts to an Amazon SNS topic.
- **B)** Create an AWS Budgets cost budget for every AWS service with a forecasted-spend alert at 110 percent.
- **C)** Schedule an AWS Lambda function to query the Cost and Usage Report in Amazon Athena each hour and compare the result with the previous week.
- **D)** Enable hourly granularity in Cost Explorer and have an engineer review the dashboard each morning.

<details><summary>Answer</summary>

**Answer: A.** An AWS managed monitor on the AWS services dimension evaluates every service automatically and begins evaluating new services as they are used, which is what covers services not in use today, and machine learning detection is what finds a change nobody set a threshold for. B requires a budget per service, needs a predicted number for each, and never covers a service that did not exist in the plan. C is a custom build of a managed capability. D is manual review, not automatic notification. Detection can take up to 24 hours and needs 10 days of history, which the four-day window in the stem tolerates.

*Where this is covered: Budgets, budget actions and anomaly detection.*

</details>

### 9. Chargeback across 40 accounts (Professional)

A company has 40 accounts in one AWS organization, including a shared services account that runs NAT gateways, inspection and logging for everyone. Finance must charge four business units for what they use, including a fair share of the shared services account, must keep a single AWS invoice, and requires that the numbers teams see are the real AWS prices.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable AWS Billing Conductor and create one billing group per business unit with a pricing plan.
- **B)** Deactivate Reserved Instance and Savings Plans discount sharing for all member accounts.
- **C)** Create cost categories that map accounts and cost allocation tag values to the four business units.
- **D)** Create a separate AWS organization for each business unit and consolidate the invoices manually.
- **E)** Add a split charge rule to the cost category that allocates the shared services account's costs across the four business units.

<details><summary>Answer</summary>

**Answer: C and E.** Cost categories group line items by account and tag value into business units and appear as a dimension in Cost Explorer, Budgets and the CUR, and a split charge rule is the documented mechanism for spreading a shared account's costs across the categories that consumed them. A is wrong because Billing Conductor exists to show marked-up or contractual pro forma prices, which the stem explicitly rules out. B changes who benefits from commitments and does nothing to allocate shared costs. D breaks the single-invoice requirement and discards the consolidated volume and commitment benefits.

*Where this is covered: Cost allocation tags and cost categories.*

</details>

### 10. A billing feed that does not break (Associate)

A platform team needs the most granular billing data AWS publishes, delivered to Amazon S3 on a schedule, with a schema that does not change from month to month, and containing only the columns its pipeline uses.

Which solution will meet these requirements?

- **A)** Save a Cost Explorer report and export it to CSV each month.
- **B)** Create a legacy Cost and Usage Report with resource IDs enabled.
- **C)** Configure an AWS Budgets report delivered by email daily.
- **D)** Create a CUR 2.0 standard data export in AWS Data Exports with a column selection.

<details><summary>Answer</summary>

**Answer: D.** CUR 2.0 has a fixed schema, where legacy CUR's columns vary month to month with your usage, tags and cost categories, and Data Exports lets you select columns, filter rows and rename columns with basic SQL before delivery to S3. A produces an aggregated console view, not line items, and is a manual step. B delivers line items but has the varying schema the stem is trying to avoid and cannot restrict columns. C emails a summary of budget status and contains no line items at all.

*Where this is covered: Cost and Usage Reports, CUR 2.0 and Data Exports.*

</details>

## Summary

Cost management is a sequence of decisions, not a dashboard. Decide what question you are asking, because Cost Explorer answers trends over 13 months and forecasts 18 forward, the Cost and Usage Report answers line items with resource IDs, and only its opt-in granular settings or a CUR 2.0 export answer both at once. Decide how costs will be attributed before you need the answer, because a tag labels usage only from the moment the resource carries it, and cost categories, which apply from the start of the current month, are what cover the charges no tag can reach. Decide what should happen when a number moves: a budget for a threshold you predicted, with a budget action when notification is not enough, and Cost Anomaly Detection for the ones you did not. Decide what to fix before deciding what to buy, because rightsizing with Compute Optimizer and removing idle resources shrinks the commitment you then size from measured history. Decide how discounts are shared across the organization, knowing that restricting sharing protects a team's bill and can raise the total. Finally, decide the network path, because cross-zone, cross-Region and internet egress charges are set by architecture and no purchase discounts them.

## Related units

- [Amazon EC2](../02-compute/ec2.md): purchasing options, Spot, Capacity Reservations and Dedicated Hosts in depth
- [Amazon S3](../01-storage/s3.md): storage classes, lifecycle policies and Storage Lens as a storage feature
- [Amazon VPC](../04-networking/vpc.md): NAT gateways, gateway and interface endpoints and the traffic paths that generate transfer charges
- [Amazon CloudFront](../04-networking/cloudfront.md): caching and origin behavior behind the egress savings described here
- [AWS Config, Trusted Advisor, Health and Well-Architected](./config-trusted-advisor-health-and-well-architected.md): the full Trusted Advisor check catalog and the Well-Architected Tool
- [AWS Organizations, IAM Identity Center and Control Tower](../07-security/organizations-identity-center-and-control-tower.md): organizational units, service control policies and tag policies
- [EC2 Auto Scaling](../02-compute/ec2-auto-scaling.md): scheduled and predictive scaling that removes idle capacity
- [Amazon CloudWatch](./cloudwatch.md): the agent, metrics and alarms that rightsizing recommendations depend on

## Sources

- [Amazon VPC pricing](https://aws.amazon.com/vpc/pricing/): the NAT gateway worked example stating that traffic staying in one Availability Zone over private addresses is not charged, the public IPv4 hourly charge in use and idle, NAT gateway hours and processing, free gateway endpoints, and the cross-zone VPC peering charge in both directions

- [Analyzing your costs and usage with AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html): 13 months of history, 18-month forecast, 24-hour refresh, API request charge
- [Exploring more data for advanced cost analysis](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-advanced-cost-analysis.html): default daily and monthly granularity, opt-in granular and multi-year data
- [Granular data](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-granular-data.html): the three granular data features and the Billing Conductor exclusion
- [Multi-year data at monthly granularity](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-multi-year-data.html): 38 months, 48-hour availability, automatic disablement
- [AWS Cost Explorer pricing](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/pricing/): console free, per-request API charge, per-record granular data charge
- [What are AWS Cost and Usage Reports?](https://docs.aws.amazon.com/cur/latest/userguide/what-is-cur.html): hourly, daily and monthly line items, delivery timeline, up to three updates a day
- [What is AWS Data Exports?](https://docs.aws.amazon.com/cur/latest/userguide/what-is-data-exports.html): the five export types and the CUR 2.0 recommendation
- [Migrating from CUR to Data Exports CUR 2.0](https://docs.aws.amazon.com/cur/latest/userguide/dataexports-migrate.html): fixed schema, nested columns, added columns, legacy comparison
- [Understanding data transfer charges](https://docs.aws.amazon.com/cur/latest/userguide/cur-data-transfers-charges.html): cross-zone, cross-Region and internet egress usage types and which direction is charged
- [Organizing and tracking costs using AWS cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html): AWS-generated and user-defined tags, management account restriction
- [Activating user-defined cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/activating-tags.html): the two 24-hour delays and the awsApplication tag
- [Backfill cost allocation tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-allocation-backfill.html): twelve-month backfill and the historical-tag requirement
- [Organizing costs using AWS Cost Categories](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/manage-cost-categories.html): dimensions, rule types, split charges, current-month effect, 24-hour processing
- [Quotas and restrictions, AWS Billing](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-limits.html): 500 tag keys, 50 cost categories, rule and split charge limits
- [Managing your costs with AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html): the six budget types, custom periods, three updates a day, notification delay
- [Configuring budget actions](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-controls.html): IAM policy, SCP and instance actions, and the cross-account restriction
- [AWS Budgets pricing](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/): free monitoring, two free action-enabled budgets, report charge
- [Getting started with AWS Cost Anomaly Detection](https://docs.aws.amazon.com/cost-management/latest/userguide/getting-started-ad.html): monitor types, managed and customer managed monitors, alert frequencies
- [Quotas and restrictions, AWS Cost Management](https://docs.aws.amazon.com/cost-management/latest/userguide/management-limits.html): budget, monitor and subscription quotas, 24-hour detection, 10-day history
- [What are Savings Plans?](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html): term definitions and payment options
- [Savings Plans types](https://docs.aws.amazon.com/savingsplans/latest/userguide/plan-types.html): Compute, Database, EC2 Instance and SageMaker AI plans, coverage and discount ceilings
- [Understanding how Savings Plans apply to your usage](https://docs.aws.amazon.com/savingsplans/latest/userguide/sp-applying.html): application order, owner account first, unused commitment does not carry over
- [Consolidating billing for AWS Organizations](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/consolidated-billing.html): one bill, combined usage, no extra fee
- [Understanding Consolidated Bills](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/con-bill-blended-rates.html): pricing tiers across accounts, reservation allocation order, blended and unblended rates
- [Reserved Instances and Savings Plans discount sharing](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ri-turn-off.html): the three sharing modes, deactivation procedure, end-of-month preference rule
- [Overview of managing access permissions](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/control-access-billing.html): Activate IAM Access and the pages it does and does not gate
- [What is AWS Billing Conductor?](https://docs.aws.amazon.com/billingconductor/latest/userguide/what-is-billingconductor.html): billing groups, pricing plans, pro forma costs, no change to the invoice
- [What is AWS Compute Optimizer?](https://docs.aws.amazon.com/compute-optimizer/latest/ug/what-is-compute-optimizer.html): supported resources, opt-in, 14-day lookback, enhanced infrastructure metrics
- [EC2 instance metrics](https://docs.aws.amazon.com/compute-optimizer/latest/ug/ec2-metrics-analyzed.html): memory and GPU metrics require the CloudWatch agent
- [Identifying opportunities with Cost Optimization Hub](https://docs.aws.amazon.com/cost-management/latest/userguide/cost-optimization-hub.html): aggregation, deduplication and pricing against your own discounts
- [Understanding Amazon S3 Storage Lens](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage_lens_basics_metrics_recommendations.html): free and advanced tiers, 14-day and 15-month query windows, prefix aggregation
- [AWS Trusted Advisor](https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor.html): which support plans get which checks and the 2027 support plan changes
- [Cost optimization checks](https://docs.aws.amazon.com/awssupport/latest/user/cost-optimization-checks.html): the named cost optimization checks in the Trusted Advisor catalog
- [What is AWS Pricing Calculator?](https://docs.aws.amazon.com/pricing-calculator/latest/userguide/what-is-pricing-calculator.html): free tool, groups, export, Price List API
- [AWS PrivateLink pricing](https://aws.amazon.com/privatelink/pricing/): per endpoint per Availability Zone per hour plus per GB processed
- [Amazon S3 pricing](https://aws.amazon.com/s3/pricing/): data transfer out to CloudFront at no charge, Storage Lens advanced tier charge
- [Amazon CloudFront pricing](https://aws.amazon.com/cloudfront/pricing/): origin transfer from AWS origins waived
- [Amazon EC2 On-Demand pricing](https://aws.amazon.com/ec2/pricing/on-demand/): 100 GB monthly free data transfer out allowance
- [Cost optimization pillar design principles](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/design-principles.html): the five Well-Architected cost principles
- [Create a billing alarm to monitor your estimated AWS charges](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html): the EstimatedCharges metric, the us-east-1 requirement and the billing alerts preference
