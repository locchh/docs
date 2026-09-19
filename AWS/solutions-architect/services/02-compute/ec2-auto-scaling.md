# Amazon EC2 Auto Scaling

**Where it sits on the exams.** **Amazon EC2 Auto Scaling** keeps a collection of **Amazon EC2** instances, the virtual servers rented by the second, at the right size: it replaces instances that fail a health check, and it adds or removes capacity on demand, on a schedule, or ahead of a forecast. It sits behind almost every "must handle traffic spikes" and "must recover automatically from failure" stem, appearing in SAA-C03 tasks 2.1, 2.2, 3.2 and 4.2 and in SAP-C02 tasks 1.3, 2.4, 2.5 and 3.4. The rule of thumb the exam rewards is to scale out rather than up, and to pick the policy type from what the requirement says the group should react to.

## What EC2 Auto Scaling is, and scaling out compared with scaling up

An **Auto Scaling group** is a set of EC2 instances managed as one unit, governed by three numbers: minimum size is the floor the group never goes below, maximum size is the ceiling it never goes above, and desired capacity is what it currently tries to maintain. Every scaling action moves desired capacity, and the group launches or terminates to match. There is no charge for the service itself; you pay for the instances, their **Amazon EBS** volumes, from the network-attached block storage service, and any **Amazon CloudWatch** alarms, from the monitoring service that also holds the metrics scaling decisions read.

This is horizontal scaling, changing how many instances run, as opposed to vertical scaling, moving to a larger instance type, which needs a stop and start and has a ceiling. The exam prefers horizontal scaling because it tolerates the loss of any single instance and lets you buy cheap interruptible capacity; vertical scaling is the answer only when work cannot be spread across machines, such as a single-writer database. Instances must therefore be stateless, with session data in a shared store, because any can disappear through scale-in, a health check failure, or reclamation of a **Spot Instance**, spare EC2 capacity sold at a discount and taken back on two minutes' notice. Purchasing options and instance family selection are decided in [Amazon EC2](ec2.md).

The group launches from a **launch template**, a versioned instance description carrying the **Amazon Machine Image (AMI)** identifier, the bootable image supplying the operating system, plus the instance type, security groups, user data and block device mappings. Its predecessor, the **launch configuration**, is immutable and unversioned, and AWS is closing it down in stages. Since January 1, 2023, new EC2 instance types are not supported in launch configurations. Accounts created on or after June 1, 2023 cannot create them in the console, and accounts created on or after October 1, 2024 cannot create them by any method, including the API, the AWS CLI and **AWS CloudFormation**, the infrastructure-as-code service. Existing launch configurations still work, and an older account can still create one, so "launch configurations no longer exist" is wrong. But several features require a launch template: multiple instance types in one group, mixing Spot and On-Demand, a parameter from **AWS Systems Manager**, the operations and configuration management service, in place of a hard-coded AMI ID, EBS volume tagging, Capacity Reservations and Dedicated Hosts.

You give the group subnets, each fixing an Availability Zone, and it launches into the enabled zone with the fewest instances and the subnet there with the most free IP addresses. When a group becomes unbalanced, Availability Zone rebalancing corrects it by launching before terminating, and may temporarily exceed maximum size by 10 percent of desired capacity or one instance, whichever is greater. Instances follow their own lifecycle: `Pending`, then `InService` once checks pass and, where a load balancer is attached, once registration completes, then `Terminating` and `Terminated`. Billing starts at launch, not at entry into service.

## Health checks and automatic instance replacement

The group continuously evaluates every `InService` instance and replaces any it finds unhealthy. Five sources can report an instance unhealthy, and knowing which are on by default decides questions.

Amazon EC2 status checks are always enabled and cannot be removed. Any state other than `running`, meaning `stopping`, `stopped`, `shutting-down` or `terminated`, or a status check result of `impaired`, makes an instance unhealthy. The service tolerates transient failures: an `impaired` result makes it wait a few minutes for AWS to fix the problem and `insufficient-data` is never unhealthy, while an instance that has left the `running` state fails immediately. A scheduled event also marks an instance unhealthy, and opt-in application status checks, configured in Amazon EC2, extend the same signal to an HTTP or HTTPS test.

**Elastic Load Balancing** health checks, from the managed service that publishes one endpoint and distributes traffic across healthy targets, are the ones candidates most often miss. Attaching a load balancer registers the instances automatically, but the group ignores the load balancer's opinion of their health until you turn these health checks on; only then is an unhealthy target marked unhealthy and replaced on the next periodic check. **VPC Lattice** health checks, from the service that connects service-to-service traffic, and Amazon EBS health checks, which watch whether attached volumes are reachable, work the same way and are likewise off by default. The fifth source is a custom health check: your own test calls `SetInstanceHealth`, for example a scheduled function in **AWS Lambda**, the event-driven function service, running `aws autoscaling set-instance-health --instance-id i-1234567890abcdef0 --health-status Unhealthy`. That call respects the health check grace period unless you add `--no-should-respect-grace-period`, and the instance is then replaced immediately.

The **health check grace period** is the minimum time a new instance stays in service before an unhealthy verdict can terminate it, because load balancer health checks start the moment an instance registers, well before a slow application finishes starting. Its default differs by interface: 300 seconds in the console, 0 seconds through the AWS CLI or an SDK, where 0 turns it off. It covers new instances, those returning from standby and those you attach, but never protects an instance that stops running. Setting it too high hides real failures, so a long start-up is better handled by a **lifecycle hook** that keeps the instance out of service until bootstrapping finishes.

Replacement is paced so a misconfigured health check cannot empty a fleet. It replaces at most 10 percent of desired capacity at a time, waiting for each batch to pass a health check and warm up. An **instance maintenance policy**, a minimum and maximum healthy percentage on the group, changes that rate and can make replacement launch before terminating, which matters for a small group where the reverse order means an outage. `Standby` suspends health checks on one instance, and suspending the `HealthCheck` and `ReplaceUnhealthy` processes stops replacement across the group, alongside `Launch`, `Terminate`, `AddToLoadBalancer`, `AlarmNotification`, `AZRebalance`, `InstanceRefresh` and `ScheduledActions`. AWS applies an administrative suspension to a group that has failed to launch any instance for over 24 hours. The deregistration delay that lets in-flight requests finish belongs to [Elastic Load Balancing](elastic-load-balancing.md).

## Choosing a scaling policy

Five mechanisms change desired capacity automatically, and one clause in the stem usually decides which. Read the table one row at a time: find the row whose trigger matches the scenario, then check its reaction speed against the requirement.

| Policy type | What it responds to | How quickly it reacts | Pacing control | Requirement wording that selects it |
|---|---|---|---|---|
| Target tracking | One metric drifting from a target value you set, such as average CPU at 50 percent | Continuously, as the alarms it creates and manages fire | Default instance warmup | "keep average utilization at", "with the LEAST operational overhead" |
| Step scaling | The size of an alarm breach, matched against bands you define | On breach, and further steps apply while an earlier one is in flight | Default instance warmup | "add 2 instances at 60 percent and 10 at 80 percent" |
| Simple scaling | A single CloudWatch alarm, applying one fixed adjustment | One adjustment, then nothing until the cooldown ends | Cooldown, 300 seconds by default | Legacy configurations only; AWS recommends against it |
| Scheduled scaling | The clock, through a cron expression and an IANA time zone | At the scheduled time, at most about two minutes late | None | "every weekday at 08:00", "a known promotion window" |
| Predictive scaling | A forecast built from historical load, not current load | Proactively, at the start of each forecast hour, or earlier with `SchedulingBufferTime` | Default instance warmup | "a recurring daily or weekly pattern" plus "long instance start-up" |

**Target tracking** is the default answer. You choose a metric and a target value, and the service creates and manages the alarms behind it. The predefined metrics are `ASGAverageCPUUtilization`, `ASGAverageNetworkIn`, `ASGAverageNetworkOut` and `ALBRequestCountPerTarget`, the last needing a `ResourceLabel` naming the target group on an **Application Load Balancer**, the Layer 7 load balancer that routes HTTP requests. Several such policies can run together if each uses a different metric, and `DisableScaleIn` turns the scale-in half off, which is how a deployment holds a floor of capacity. Three constraints decide questions: never edit the alarms the policy owns, because the service rewrites them; a metric with missing data points puts its alarm into `INSUFFICIENT_DATA` and scaling stops; and the policy can only scale out when the metric is above the target, never below it.

**Step scaling** suits a response that should depend on how badly the threshold was breached. You own the alarm, and the policy carries up to 20 step adjustments whose bounds are relative to the breach threshold, with no overlaps and no gaps. Adjustment types are `ChangeInCapacity`, `ExactCapacity` and `PercentChangeInCapacity`, the last taking a floor from `MinAdjustmentMagnitude`. **Simple scaling** is the original mechanism, one alarm and one fixed adjustment gated by a pause between actions, and AWS recommends against it in favor of target tracking or step scaling, so a scenario describing one is an invitation to replace it.

**Scheduled scaling** sets desired capacity, and optionally minimum and maximum capacity, at a given time. Recurring schedules use a five-field cron expression, `[Minute] [Hour] [Day_of_Month] [Month_of_Year] [Day_of_Week]`, so `30 6 * * 2` is every Tuesday at 06:30. The time zone defaults to UTC, and an IANA location name such as `America/New_York` adjusts for daylight saving while `Etc/UTC` does not.

**Predictive scaling** is the only proactive option. Its metric must have at least 24 hours of data before any forecast appears; it then analyzes up to the past 14 days for daily and weekly patterns, produces an hourly capacity forecast for the next 48 hours, and refreshes it every 6 hours. A new policy starts in `ForecastOnly` mode so you can compare forecast against reality, and `ForecastAndScale` lets it act. It never scales in, so pair it with a dynamic policy; when several policies are active the group takes the highest desired capacity any of them computes. By default it will not exceed the group's maximum size, though `MaxCapacityBreachBehavior` set to `IncreaseMaxCapacity` with a `MaxCapacityBuffer` allows it to, permanently raising the maximum until you lower it.

Choosing the metric is its own exam bullet. Auto Scaling group metrics such as `GroupDesiredCapacity`, `GroupInServiceInstances` and `GroupTotalInstances` live in the `AWS/AutoScaling` namespace at one-minute granularity and no extra charge, but must be enabled with `enable-metrics-collection`. Instance metrics arrive every five minutes by default; detailed monitoring gives one-minute data so a policy reacts faster. A queue-driven fleet is the classic trap: the **Amazon SQS** metric `ApproximateNumberOfMessagesVisible`, from the managed message queue service, does not work for target tracking, because queue depth does not change in proportion to group size. The documented answer is a backlog per instance metric, `ApproximateNumberOfMessages` divided by the count of `InService` instances, targeting acceptable latency divided by average processing time: 10 seconds of latency at 0.1 seconds per message gives a target of 100.

## Cooldowns, instance warmup, and which instance terminates

Two mechanisms stop a group overreacting, and the exam tests the difference. A **cooldown** is a group-level pause after a scaling activity, 300 seconds by default, during which no further activity initiated by a simple scaling policy may start. It applies to simple scaling only: target tracking and step scaling can scale out immediately, a scheduled action fires regardless, and an unhealthy instance is replaced without waiting. A scale-in policy can carry a shorter cooldown of its own.

The **default instance warmup** is the per-instance equivalent, used by target tracking, step scaling, predictive scaling and instance refresh. It is the time after an instance reaches `InService` before its data counts toward the group's aggregated metrics, so a start-up CPU spike does not look like real load. It is not enabled by default, AWS recommends turning it on, and 300 seconds is the suggested starting value. The fallback chain when it is null is what a Professional question turns on: target tracking and step scaling fall back to the default cooldown, an **instance refresh** falls back to the health check grace period, and predictive scaling has no default warmup at all, which is why a predictive policy without one can spike the aggregated metrics and trigger a dynamic policy on top of its own scale-out. While instances warm up, the group scales out only if the metric from instances that are not warming up still exceeds the threshold, and policy-driven scale-in is blocked.

When the group scales in, a **termination policy** picks the victims. Zonal balance always comes first: the service finds the Availability Zone with the most instances that holds at least one instance not protected from scale in, and applies the policy there. Within that zone the default policy looks for outdated configurations in order, checking first for instances launched from a launch configuration, then for instances on a different launch template than the current one, then for instances on the oldest version of the current template. A remaining tie goes to the instance closest to its next billing hour, then to random choice. Unhealthy instances bypass this entirely, because they are replaced rather than chosen. A group mixing Spot and On-Demand first chooses which purchase option should go, so the group trends back toward its configured ratio.

You can replace the default with a predefined policy: `OldestInstance` when rolling onto a new instance type, `NewestInstance` when backing out a test configuration, `OldestLaunchTemplate` or `OldestLaunchConfiguration` when phasing out a configuration, `ClosestToNextInstanceHour` where hourly billing matters, and `AllocationStrategy` when preferred types or Spot pools have changed. Above all of it sits instance scale-in protection, which marks individual instances that policy-driven scale-in must not terminate: a long-running queue worker sets protection before taking a work item and clears it when the item completes. It does not protect against a health check failure or a Spot interruption.

## Lifecycle hooks, warm pools, and hibernation

A lifecycle hook pauses an instance in a wait state so something else can run first. A hook on the `autoscaling:EC2_INSTANCE_LAUNCHING` transition holds a launching instance in `Pending:Wait`, where bootstrapping happens before the instance registers with a load balancer and enters service. A hook on `autoscaling:EC2_INSTANCE_TERMINATING` holds a departing instance in `Terminating:Wait` to upload logs or drain a worker. The heartbeat timeout defaults to 3,600 seconds, one hour, and ranges from 30 to 7,200 seconds; `RecordLifecycleActionHeartbeat` restarts that clock, `CompleteLifecycleAction` ends the wait early, and a global timeout caps the whole wait at 48 hours or 100 times the heartbeat timeout, whichever is smaller. On timeout the hook applies its `DefaultResult`, `ABANDON` unless you set `CONTINUE`: on launch, `CONTINUE` puts the instance in service and `ABANDON` replaces it, while on termination both let it go but `ABANDON` skips remaining hooks. Notifications reach **Amazon EventBridge**, the event bus that routes AWS and application events to targets, and the API can also publish to an **Amazon SNS** topic, from the managed publish and subscribe service, or an Amazon SQS queue. Termination hooks are best effort.

A **warm pool** holds pre-initialized instances alongside the group for applications whose first boot is slow. Instances leave the pool on scale-out, a warm start; an empty pool means a cold start from scratch. Pool size defaults to maximum capacity minus desired capacity, `MaxGroupPreparedCapacity` replaces the maximum in that calculation for large groups, and `MinSize`, default 0, holds a floor. The pool state defaults to `Stopped`, where you pay only for EBS volumes and attached Elastic IP addresses; `Running` is supported but discouraged, because idle instances bill at full price. The third state is `Hibernated`, which uses EC2 **hibernation** to write the contents of RAM to the encrypted EBS root volume and reload it on the next start, so an instance returns with its caches and processes intact instead of repeating a long warm-up. That makes hibernation a scaling strategy in its own right, buying the responsiveness of a running instance at close to the price of a stopped one, given a root volume big enough for the memory image and an instance type meeting the prerequisites covered in [Amazon EC2](ec2.md). Four limits decide questions: the root device must be an EBS volume, weighted groups are unsupported, a warm pool cannot draw on Spot so a group that mixes purchase options must be On-Demand only, and instances are stopped or hibernated as soon as they enter the pool without waiting for user data to finish, which makes a launch lifecycle hook effectively mandatory. An instance reuse policy returns instances to the pool on scale in rather than terminating them.

## Instance refresh, maximum instance lifetime, and mixed instances with Spot

An instance refresh rolls a new configuration across a running group. Update the launch template, usually with a new AMI, then start a refresh; the default rolling strategy replaces instances in batches and adopts the new desired configuration when it succeeds. Batch size comes from two percentages. Minimum healthy percentage, 90 percent by default when no instance maintenance policy is set, is the share of desired capacity that must stay in service, so the default replaces 10 percent at a time. Maximum healthy percentage defaults to 100 percent and is how far above desired capacity the group may go while replacing; the gap between the two cannot exceed 100. Setting both to 100 percent switches to launch before terminate, one at a time, which is the answer when capacity must never dip; a minimum of 0 replaces everything at once. Between batches the refresh waits for the instance warmup.

Three options turn a refresh into a controlled deployment. Checkpoints, set with `CheckpointPercentages` and a `CheckpointDelay` that defaults to one hour, pause at chosen percentages and emit an EventBridge event at each, so `[1, 100]` is a canary. Auto rollback, off by default, returns the group to its previous configuration on failure, and an attached CloudWatch alarm can fail the refresh. Skip matching leaves instances that already match alone; it is enabled in the console and disabled through the AWS CLI and SDKs, and because it compares launch template versions and AMI IDs it cannot see a code change pulled by a user data script. A refresh has 14 days to finish and fails after retrying for an hour if instances sit in `Standby` or carry scale-in protection and the refresh is set to wait for them, which is the CLI and SDK default while the console default is to ignore them.

**Maximum instance lifetime** answers the compliance requirement to replace instances on a schedule. Set a value of at least 86,400 seconds, one day; 0 clears it. The service usually replaces one instance at a time with a pause between, but a lifetime too short for that forces it to replace up to 10 percent of current capacity at once. It honors scale-in protection and terminates before launching by default, so a single-instance group needs an instance maintenance policy to avoid an outage.

A **mixed instances policy** lets one group launch several instance types and both purchase options, which is what makes Spot practical for a production tier: spread across types and zones so one exhausted pool cannot take the tier down. List the types as launch template overrides or describe them by attribute with `InstanceRequirements`, and use instance weights so unequal types count correctly. Two settings split the purchase options, and both defaults surprise people. `OnDemandBaseCapacity`, default 0, is the first slice of capacity that is always On-Demand, where the baseline covered by Reserved Instances or Savings Plans belongs. `OnDemandPercentageAboveBaseCapacity`, default 100, governs everything above the base, so an untouched policy is entirely On-Demand; set it to 20 for 20 percent On-Demand and 80 percent Spot above the base. AWS recommends the `price-capacity-optimized` Spot allocation strategy, which picks pools combining low price with low interruption risk. `capacity-optimized` optimizes purely for available capacity and `capacity-optimized-prioritized` honors your type ordering on a best-effort basis. `lowest-price` is the API default but AWS explicitly does not recommend it, because price alone gives the highest interruption rate; it draws from `SpotInstancePools`, default 2, range 1 to 20. On-Demand capacity uses `lowest-price` or `prioritized`, the latter the default when you list types explicitly and the way to favor types your Reserved Instances cover.

**Capacity Rebalancing** makes Spot behave far better. Amazon EC2 sends a rebalance recommendation when a Spot Instance is at elevated risk of interruption, ahead of the two-minute interruption notice. With it enabled the group launches a replacement, waits for it to pass a health check, and only then terminates the at-risk instance, and it may exceed maximum size by up to 10 percent of desired capacity so a full group does not block the swap. Without it, replacement waits for the interruption and the failed health check. Pair it with a termination lifecycle hook whose action finishes inside two minutes, and do not combine it with `lowest-price`, whose replacement would come from a pool just as likely to be reclaimed.

## AWS Auto Scaling and Application Auto Scaling

Three services carry almost the same name and the exams use them loosely. Amazon EC2 Auto Scaling is everything above: Auto Scaling groups of EC2 instances, and nothing else.

**Application Auto Scaling** is a separate service that scales the capacity of other AWS services. You register a scalable target by naming a service namespace, a resource ID and a scalable dimension such as `ecs:service:DesiredCount`, then attach a policy to it, choosing target tracking, step scaling, scheduled scaling or predictive scaling. Its targets include services in **Amazon ECS**, the managed container orchestrator, tables and global secondary indexes in **Amazon DynamoDB**, the managed NoSQL key-value database, read replicas in **Amazon Aurora**, the MySQL and PostgreSQL compatible relational database, provisioned concurrency for Lambda functions, clusters in **Amazon ElastiCache**, the managed in-memory cache, and in **Amazon EMR**, the managed big data service, broker storage in **Amazon MSK**, the managed Apache Kafka service, endpoints in **Amazon SageMaker AI**, the machine learning platform, **Spot Fleet** requests, which are standalone fleets of Spot capacity, pools of **Amazon WorkSpaces**, the managed virtual desktop service, and custom resources. One detail separates it from EC2 Auto Scaling in the exam's favorite way: an Application Auto Scaling target tracking policy has `ScaleInCooldown` and `ScaleOutCooldown` settings, and an EC2 Auto Scaling target tracking policy has neither.

**AWS Auto Scaling** is the third name, and it means scaling plans. A scaling plan discovers related resources by tag or by CloudFormation stack and configures scaling for all of them at once, across Aurora read replicas, Auto Scaling groups, ECS services, DynamoDB tables and indexes, and Spot Fleets, with strategies that optimize for availability, cost, or a balance. It is still documented and still free beyond the resources it uses, with one AWS recommendation attached: if you use a scaling plan only for predictive scaling, set predictive scaling policies directly on the resources instead, because they have more features and avoid the CloudWatch `GetMetricData` charges a scaling plan incurs. For the exam, treat "AWS Auto Scaling" as the umbrella and grouping layer, and EC2 Auto Scaling as the thing that launches instances.

## Professional depth

The quotas divide into two kinds, and only one kind can be raised. Auto Scaling groups per Region, default 500, and launch configurations per Region, default 200, are adjustable through **Service Quotas**, the service that displays and raises account limits. The per-group numbers are fixed: 50 scaling policies, 125 scheduled actions, 20 step adjustments per step scaling policy, 50 lifecycle hooks, 10 SNS topics, 50 Elastic Load Balancing target groups and 5 VPC Lattice target groups. In practice the limit that stops a scale-out is somebody else's: the account's EC2 vCPU quota in the Region, free IP addresses in the subnets, or an EBS quota. A disaster recovery Region whose quotas were never raised will not absorb a failover, which is what the exam bullet about service quotas in a standby environment is testing.

At organization scale the unit of change is the launch template, not the instance. A central account hardens an AMI and shares it, along with its **AWS KMS** key from the managed encryption key service, with the organization; each workload account's launch template references it through a Systems Manager parameter, so a new AMI ID propagates without a template edit. Rolling it out is one instance refresh per group, with skip matching on, checkpoints for the first percent, and auto rollback armed against a CloudWatch alarm, and because refreshes emit EventBridge events at every checkpoint a management account can watch hundreds of groups from one bus. The same machinery serves continuity: a group whose minimum size is zero in a pilot light Region, raised by a scheduled action or a failover automation, is a warm standby that costs almost nothing while idle.

The failure modes are worth rehearsing, because Professional questions are built from them. A group that cannot launch any instance for about 24 hours receives an administrative suspension and stops trying until you resume it. Predictive scaling pointed at a brand new group has no forecast for 24 hours, so a blue/green replacement silently disables it. An instance refresh stalls and fails after an hour if instances sit in `Standby` or carry scale-in protection. And a target tracking policy whose metric stops reporting does not scale at all, because its alarm goes to `INSUFFICIENT_DATA` rather than `ALARM`. The Associate version of a question asks which policy to use; the Professional version gives a working policy, a symptom, and asks which setting explains it.

## Worked scenario

A media company runs an image processing tier on EC2 behind an Application Load Balancer, plus a worker tier reading jobs from an Amazon SQS queue. Traffic rises every weekday from 07:00 local time and falls after 19:00, with unpredictable surges when a customer uploads a large archive. Workers take nine minutes to start because each downloads a multi-gigabyte model. Jobs must not be lost, and finance wants the variable capacity on Spot.

The web tier gets a group across three Availability Zones with a target tracking policy on `ALBRequestCountPerTarget`, Elastic Load Balancing health checks turned on so a hung application is replaced rather than left in the target group, and a default instance warmup so the policy does not double-scale on start-up CPU. Because the daily pattern is regular, a predictive scaling policy runs alongside in `ForecastAndScale` mode, adding capacity before 07:00, while target tracking absorbs the surges and does the scaling in. The worker tier gets its own group with a warm pool in the `Hibernated` state, which is the one exception to the rule that Auto Scaling group instances cannot hibernate: the prohibition covers `InService` instances, while EC2 Auto Scaling itself hibernates the instances it holds in a warm pool and a launch lifecycle hook, so pre-warmed workers hold the model in memory and enter service in seconds. Its target tracking policy uses a backlog per instance custom metric rather than raw queue depth, and each worker sets instance scale-in protection while holding a job, so scale-in never kills work in progress. A termination lifecycle hook lets a departing worker return an unfinished message to the queue.

Spot arrives through a mixed instances policy with six or so instance types, `OnDemandBaseCapacity` set to the steady baseline that Savings Plans already cover, `OnDemandPercentageAboveBaseCapacity` set low, the `price-capacity-optimized` allocation strategy, and Capacity Rebalancing enabled. The exam asks why the worker tier still takes nine minutes to answer a surge, and the keyed answer is that the warm pool was created without a launch lifecycle hook, so instances were stopped before their user data finished and had to repeat the download on start.

## Exam lens

- "the instances pass EC2 status checks but the application is unresponsive" maps to turning on Elastic Load Balancing health checks for the group.
- "maintain average CPU utilization at 60 percent" with "LEAST operational overhead" maps to a target tracking policy.
- "add more capacity the further the metric goes past the threshold" maps to step scaling.
- "traffic rises predictably every weekday at 08:00" maps to scheduled scaling; predictive scaling is the distractor unless instances also start slowly.
- "recurring weekly pattern and long start-up" maps to predictive scaling paired with a dynamic policy, because predictive scaling never scales in.
- "scale on the number of messages in a queue" maps to a backlog per instance custom metric; `ApproximateNumberOfMessagesVisible` is the distractor.
- "run a configuration script before the instance receives traffic" maps to a launch lifecycle hook; raising the grace period is the distractor.
- "instances take 10 minutes to boot and scale-out is too slow" maps to a warm pool, in the `Hibernated` state when memory contents must survive.
- "deploy a new AMI with no drop in capacity" maps to an instance refresh with minimum and maximum healthy percentage both at 100, with checkpoints for a canary.
- "replace every instance every 30 days for compliance" maps to maximum instance lifetime, not a scheduled instance refresh.
- "long-running jobs must not be interrupted by scale-in" maps to instance scale-in protection; a `NewestInstance` termination policy is the distractor, because it protects no particular instance.
- "scale DynamoDB capacity and ECS tasks as well as the EC2 fleet" maps to Application Auto Scaling, with AWS Auto Scaling scaling plans as the grouping layer.

## Knowledge check

### 1. Instances that pass their checks but serve errors (Associate)

A retail company runs a web tier in an Auto Scaling group behind an Application Load Balancer. When the application process deadlocks, the load balancer marks the target unhealthy and stops sending it requests, but the Auto Scaling group leaves the instance running, so capacity stays degraded until an engineer notices. The company wants the group to replace these instances automatically without writing custom code.

Which solution will meet these requirements?

- **A)** Reduce the health check grace period on the Auto Scaling group to 0 seconds.
- **B)** Turn on Elastic Load Balancing health checks for the Auto Scaling group.
- **C)** Create a CloudWatch alarm on the load balancer's unhealthy host count and attach a step scaling policy to the group.
- **D)** Change the group's termination policy to `OldestInstance`.

<details><summary>Answer</summary>

**Answer: B.** Amazon EC2 status checks are always on but see only the instance and its hardware, not the application, so a deadlocked process passes them. Elastic Load Balancing health checks are ignored by the group until you explicitly turn them on; once enabled, a target the load balancer reports unhealthy is marked unhealthy and replaced on the next periodic check. A is wrong because the grace period only controls how long a newly launched instance is shielded from an unhealthy verdict, and it never causes a replacement. C is wrong because a step scaling policy adds capacity, which does not remove the deadlocked instance that is still counted in the group. D is wrong because a termination policy only decides which instance goes during scale-in, not whether anything is replaced.

*Where this is covered: Health checks and automatic instance replacement.*

</details>

### 2. A predictable morning ramp (Associate)

A university portal sees load climb sharply every weekday between 08:00 and 08:30 in the campus time zone, then stay flat for the rest of the day. Instances become ready in about 90 seconds. The operations team wants capacity in place before the ramp starts and wants the fleet to keep tracking demand afterward.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create a simple scaling policy on average CPU utilization with a 300-second cooldown.
- **B)** Create a step scaling policy with three step adjustments on average CPU utilization.
- **C)** Create a scheduled action that raises desired capacity at 07:45 in the campus time zone, and add a target tracking policy on average CPU utilization for the rest of the day.
- **D)** Create a predictive scaling policy and leave it in `ForecastOnly` mode.

<details><summary>Answer</summary>

**Answer: C.** The ramp happens at a known clock time, which is exactly what scheduled scaling is for, and a scheduled action can carry an IANA time zone so it follows daylight saving. Pairing it with a target tracking policy keeps the group following demand for the rest of the day. A is wrong because simple scaling is reactive, AWS recommends against it, and its cooldown blocks further scaling for five minutes after each action. B is wrong for the same reactive reason: step scaling responds only after utilization has already risen. D is wrong because `ForecastOnly` generates a forecast but never changes capacity; only `ForecastAndScale` acts.

*Where this is covered: Choosing a scaling policy.*

</details>

### 3. Renders lost during scale-in (Associate)

An image rendering fleet runs in an Auto Scaling group. Each instance picks up one job that can take up to 40 minutes to finish. During scale-in, renders are being lost because instances are terminated part way through, and the company cannot change how jobs are distributed.

Which solution will meet these requirements?

- **A)** Have each worker call `SetInstanceProtection` on itself before starting a job and clear the protection when the job finishes.
- **B)** Change the group's termination policy to `OldestInstance`.
- **C)** Increase the group's default cooldown to 2,400 seconds.
- **D)** Enable Capacity Rebalancing on the Auto Scaling group.

<details><summary>Answer</summary>

**Answer: A.** Instance scale-in protection is the only control that tells the group which specific instance must not be terminated, and toggling it around each unit of work is the documented pattern for long-running queue workers. B is wrong because age has no relationship to whether an instance is busy, so an old idle instance and an old busy instance are equally likely to be chosen. C is wrong because a cooldown only paces further activity from simple scaling policies; it delays scale-in without protecting any particular instance. D is wrong because Capacity Rebalancing reacts to Spot rebalance recommendations and does nothing about policy-driven scale-in.

*Where this is covered: Cooldowns, instance warmup, and which instance terminates.*

</details>

### 4. Servers that take eleven minutes to start (Associate)

A game studio runs matchmaking servers that take 11 minutes to start, because each one loads a 30 GB map cache into memory before it can accept players. Scale-out is far too slow during evening peaks, but the studio does not want to pay for peak capacity to sit idle all day.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Set the group's desired capacity to the evening peak and leave it there all day.
- **B)** Create a step scaling policy that adds instances at a much lower CPU threshold.
- **C)** Add a warm pool in the `Running` state with a launch lifecycle hook.
- **D)** Add a warm pool in the `Hibernated` state with a launch lifecycle hook.

<details><summary>Answer</summary>

**Answer: D.** A hibernated warm pool instance has already loaded its cache; hibernation writes the contents of RAM to the encrypted EBS root volume and reloads it on start, so the server returns warm in seconds, and while it waits you pay only for EBS storage and any attached Elastic IP address. The launch lifecycle hook is required so the instance is not stopped before its user data finishes loading the cache. A is wrong because it pays full price for idle capacity all day. B is wrong because a lower threshold starts the same 11-minute boot earlier without shortening it. C is wrong on cost: instances kept `Running` in a warm pool bill at the full instance rate, which AWS explicitly discourages.

*Where this is covered: Lifecycle hooks, warm pools, and hibernation.*

</details>

### 5. Rolling out a patched image (Associate)

A company must deploy a patched AMI across a 200-instance Auto Scaling group that fronts a payment API. Capacity must never fall below the group's current desired capacity at any point during the rollout, and the release team wants to inspect a small sample of replaced instances before the remaining instances are rolled.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Start an instance refresh with a minimum healthy percentage of 0.
- **B)** Start an instance refresh with both the minimum and the maximum healthy percentage set to 100.
- **C)** Set the group's maximum instance lifetime to 86,400 seconds.
- **D)** Configure checkpoint percentages of 1 and 100, with a checkpoint delay long enough to inspect the canary.
- **E)** Suspend the `AZRebalance` process for the duration of the rollout.

<details><summary>Answer</summary>

**Answer: B and D.** Setting both the minimum and maximum healthy percentage to 100 switches an instance refresh to launch before terminate, one instance at a time, which is what guarantees capacity never dips. Checkpoints pause the refresh at the percentages you choose and emit an EventBridge event at each, so `[1, 100]` replaces one instance, waits, and continues only after inspection. A is wrong because a minimum of 0 replaces every instance at once, which is the opposite of the requirement. C is wrong because maximum instance lifetime replaces instances on an age schedule and offers no canary or ordering control. E is wrong because Availability Zone rebalancing already launches before terminating and suspending it does not affect the AMI rollout.

*Where this is covered: Instance refresh, maximum instance lifetime, and mixed instances with Spot.*

</details>

### 6. A Spot fleet that keeps losing capacity (Professional)

A data processing platform runs a 400-instance Auto Scaling group across three Availability Zones with a mixed instances policy. `OnDemandBaseCapacity` is 40, `OnDemandPercentageAboveBaseCapacity` is 0, the launch template lists two instance types, and the Spot allocation strategy is `lowest-price` across two Spot pools. Interruptions arrive in bursts, capacity drops for several minutes at a time, and in-flight work is lost with no chance to check point. The platform must keep its Spot savings.

Which solution will meet these requirements?

- **A)** Set `OnDemandPercentageAboveBaseCapacity` to 100 so that only the base capacity remains on Spot.
- **B)** Keep `lowest-price`, raise the number of Spot pools to 20, and set a `SpotMaxPrice` above the current On-Demand rate.
- **C)** Change the Spot allocation strategy to `price-capacity-optimized`, add more instance types to the launch template overrides, enable Capacity Rebalancing, and add a termination lifecycle hook that checkpoints work.
- **D)** Replace the mixed instances policy with a predictive scaling policy in `ForecastAndScale` mode and raise the group's maximum size.


<details><summary>Answer</summary>

**Answer: C.** `price-capacity-optimized` is the strategy AWS recommends because it selects pools that are both cheap and least likely to be interrupted, more instance types mean more pools to draw from, Capacity Rebalancing launches a replacement on the rebalance recommendation and waits for it to pass a health check before terminating the at-risk instance, and a termination lifecycle hook provides the window to checkpoint. A is wrong because it moves essentially the whole fleet to On-Demand, breaking the requirement to keep Spot savings. B is wrong because `lowest-price` ignores available capacity by design and carries the highest interruption rate, and AWS states that setting a maximum price increases interruptions rather than reducing them. D is wrong because predictive scaling forecasts demand and does nothing about Spot reclamation.

*Where this is covered: Instance refresh, maximum instance lifetime, and mixed instances with Spot.*

</details>

### 7. A predictive policy that stopped forecasting (Professional)

An insurance company replaced an Auto Scaling group during a blue/green cutover, creating a new group from the same launch template and deleting the old one. The predictive scaling policy was recreated on the new group with the same metric and target and left in `ForecastAndScale` mode. A day later the console still shows no forecast, no proactive scale-out happened before the morning peak, and the target tracking policy on average CPU utilization is working normally. The company wants proactive scaling restored and wants it to survive the next cutover.

Which solution will meet these requirements?

- **A)** Allow the new group to accumulate 24 hours of metric data, and configure the predictive scaling policy with a custom metric that aggregates load across the old and new Auto Scaling groups so future cutovers keep their history.
- **B)** Set `MaxCapacityBreachBehavior` to `IncreaseMaxCapacity` with a `MaxCapacityBuffer` of 10.
- **C)** Increase `SchedulingBufferTime` so that instances launch earlier within each forecast hour.
- **D)** Enable the default instance warmup on the group and raise the health check grace period to 300 seconds.

<details><summary>Answer</summary>

**Answer: A.** Predictive scaling needs at least 24 hours of data on its metric before it produces any forecast, and metric history does not follow a group that has been deleted and recreated, so a blue/green replacement silently disables it; a custom metric that aggregates across both groups is the documented way to carry history through the next cutover. B is wrong because the maximum capacity behavior only decides what happens when a forecast approaches the group's ceiling, and there is no forecast yet. C is wrong for the same reason: the scheduling buffer shifts the launch time of capacity the forecast asked for. D is wrong because warmup and grace period affect how metrics are counted and how quickly a new instance can be failed, not whether a forecast exists.

*Where this is covered: Choosing a scaling policy.*

</details>

### 8. Scaling more than the instance fleet (Professional)

A SaaS provider runs a three-tier platform in one account: an EC2 web tier in an Auto Scaling group, an Amazon ECS service that processes background jobs, and an Amazon DynamoDB table in provisioned capacity mode. All three saturate during the same daily peak. The platform team wants each tier to scale on its own utilization metric, wants to avoid writing and maintaining custom automation, and wants the configuration to be visible in the console for each service.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create a target tracking scaling policy on the Auto Scaling group using the `ASGAverageCPUUtilization` predefined metric.
- **B)** Register the Auto Scaling group as a scalable target in Application Auto Scaling and attach a target tracking policy to it.
- **C)** Register the ECS service and the DynamoDB table as scalable targets in Application Auto Scaling and attach a target tracking policy to each.
- **D)** Create a scheduled action on the Auto Scaling group and an AWS Lambda function that adjusts the ECS desired count and the DynamoDB provisioned capacity at the same time.
- **E)** Create an AWS Auto Scaling scaling plan and rely on it to apply predictive scaling to the DynamoDB table.

<details><summary>Answer</summary>

**Answer: A and C.** EC2 instances in an Auto Scaling group are scaled by Amazon EC2 Auto Scaling, which supports the `ASGAverageCPUUtilization` predefined metric directly. Everything that is not an Auto Scaling group, including ECS services and DynamoDB tables, is scaled by Application Auto Scaling, which requires registering a scalable target and then attaching a policy. B is wrong because an Auto Scaling group is not a valid Application Auto Scaling scalable target. D is wrong because it is exactly the custom automation the team wants to avoid, and a schedule cannot follow utilization. E is wrong because scaling plans support predictive scaling only for Auto Scaling groups, and AWS recommends setting predictive scaling policies directly on the resource rather than through a plan.

*Where this is covered: AWS Auto Scaling and Application Auto Scaling.*

</details>

## Summary

An EC2 Auto Scaling question is a short chain of decisions. Decide the shape first: scale out across several Availability Zones rather than up, keep instances stateless, and build from a launch template, because launch configurations block multiple instance types and Spot and cannot be created in accounts made on or after October 1, 2024. Decide what "unhealthy" means, remembering that EC2 status checks are always on while Elastic Load Balancing, VPC Lattice and EBS health checks are not, and set the grace period from application start-up time. Decide the policy from the trigger: a metric and a target choose target tracking, a graded response chooses step scaling, a clock chooses scheduled scaling, a repeating pattern with slow instances chooses predictive scaling, and simple scaling means a legacy design. Set the default instance warmup rather than relying on the cooldown fallback. Then take the feature that matches the requirement: a lifecycle hook to run something before or after, a warm pool with hibernation for long boots, an instance refresh for a rollout, maximum instance lifetime for compliance, a mixed instances policy with Capacity Rebalancing for Spot, and Application Auto Scaling for what is not an instance.

## Related units

- [Amazon EC2](ec2.md): purchasing options, instance families, hibernation prerequisites and status checks behind every group
- [Elastic Load Balancing](elastic-load-balancing.md): target groups, health check settings and the deregistration delay that protects requests during scale-in
- [Amazon Machine Images](ami.md): building, sharing and deprecating the images a launch template points at
- [AWS Lambda](lambda.md): the compute model that scales itself, and the function behind a custom health check or lifecycle hook action
- [Amazon CloudWatch](../08-management/cloudwatch.md): alarms, metric math and detailed monitoring that drive every dynamic scaling policy
- [Amazon ECS and Amazon ECR](../03-containers/ecs-and-ecr.md): capacity providers and service auto scaling for container workloads on the same instances
- [Amazon SQS](../06-integration/sqs.md): the queue whose backlog per instance metric drives worker fleets
- [Cost management](../08-management/cost-management.md): Savings Plans coverage, rightsizing and the reports that show an oversized group

## Sources

- [What is Amazon EC2 Auto Scaling?](https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html): minimum, maximum and desired capacity, the feature list and the no-additional-charge statement
- [Auto Scaling benefits for application architecture](https://docs.aws.amazon.com/autoscaling/ec2/userguide/auto-scaling-benefits.html): instance distribution across zones and the 10 percent margin during Availability Zone rebalancing
- [Amazon EC2 Auto Scaling instance lifecycle](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-lifecycle.html): the Pending, InService, Terminating and Standby states and billing from launch
- [Auto Scaling launch templates](https://docs.aws.amazon.com/autoscaling/ec2/userguide/launch-templates.html): versioning and the features that require a launch template
- [Auto Scaling launch configurations](https://docs.aws.amazon.com/autoscaling/ec2/userguide/launch-configurations.html): the January 2023, June 2023 and October 2024 restrictions by account creation date
- [Health checks for instances in an Auto Scaling group](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-health-checks.html): the five health check sources
- [About the health checks for your Auto Scaling group](https://docs.aws.amazon.com/autoscaling/ec2/userguide/health-checks-overview.html): which checks are on by default, the unhealthy EC2 states, and the 10 percent replacement pacing
- [Set the health check grace period for an Auto Scaling group](https://docs.aws.amazon.com/autoscaling/ec2/userguide/health-check-grace-period.html): 300 seconds in the console, 0 seconds through the CLI and SDKs
- [Set up a custom health check for your Auto Scaling group](https://docs.aws.amazon.com/autoscaling/ec2/userguide/set-up-a-custom-health-check.html): the set-instance-health command and the grace period override
- [Instance maintenance policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-instance-maintenance-policy.html): minimum and maximum healthy percentage during replacement events
- [Suspend and resume Amazon EC2 Auto Scaling processes](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-suspend-resume-processes.html): the suspendable process list and administrative suspension
- [Target tracking scaling policies for Amazon EC2 Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html): predefined metrics, managed alarms, DisableScaleIn and the INSUFFICIENT_DATA behavior
- [Step and simple scaling policies for Amazon EC2 Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-simple-step.html): step adjustments, adjustment types and MinAdjustmentMagnitude
- [Scaling cooldowns for Amazon EC2 Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-scaling-cooldowns.html): the 300-second default and which policy types ignore it
- [Set the default instance warmup for an Auto Scaling group](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-default-instance-warmup.html): the warmup fallback chain and the 300-second starting recommendation
- [Scheduled scaling for Amazon EC2 Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-scheduled-scaling.html): cron format, IANA time zones and the 125 scheduled actions limit
- [How predictive scaling works](https://docs.aws.amazon.com/autoscaling/ec2/userguide/predictive-scaling-policy-overview.html): the 24-hour minimum, 14-day analysis, 48-hour forecast, 6-hour refresh and max capacity behavior
- [Configure termination policies for Amazon EC2 Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-termination-policies.html): the default termination order and every predefined policy
- [Amazon EC2 Auto Scaling lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html): the global timeout of 48 hours or 100 heartbeats, and best-effort termination hooks
- [How lifecycle hooks work in Auto Scaling groups](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks-overview.html): the Pending:Wait and Terminating:Wait transitions
- [PutLifecycleHook](https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_PutLifecycleHook.html): the 3,600-second heartbeat default, the 30 to 7,200 range and the ABANDON default result
- [Decrease latency for applications with long boot times using warm pools](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-warm-pools.html): pool sizing, the three pool states, instance reuse policy and the warm pool limitations
- [PutWarmPool](https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_PutWarmPool.html): the Stopped default pool state and the MinSize and MaxGroupPreparedCapacity defaults
- [How an instance refresh works in an Auto Scaling group](https://docs.aws.amazon.com/autoscaling/ec2/userguide/instance-refresh-overview.html): minimum and maximum healthy percentage, checkpoints, skip matching and the 14-day and one-hour limits
- [Understand the default values for an instance refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/understand-instance-refresh-default-values.html): the 90 percent minimum, 100 percent maximum, one-hour checkpoint delay and per-interface skip matching default
- [Replace Auto Scaling instances based on maximum instance lifetime](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-max-instance-lifetime.html): the 86,400-second minimum and the 10 percent replacement rate
- [Allocation strategies for multiple instance types](https://docs.aws.amazon.com/autoscaling/ec2/userguide/allocation-strategies.html): every Spot and On-Demand allocation strategy and the AWS recommendation
- [InstancesDistribution](https://docs.aws.amazon.com/autoscaling/ec2/APIReference/API_InstancesDistribution.html): the OnDemandBaseCapacity, OnDemandPercentageAboveBaseCapacity, SpotAllocationStrategy and SpotInstancePools defaults
- [Capacity Rebalancing in Auto Scaling to replace at-risk Spot Instances](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-capacity-rebalancing.html): launch before terminate, the 10 percent overshoot and the lowest-price warning
- [Quotas for Auto Scaling resources and groups](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-quotas.html): the adjustable Region quotas and the fixed per-group and per-operation limits
- [Amazon CloudWatch metrics for Amazon EC2 Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-metrics.html): the group metrics, their one-minute granularity and the requirement to enable collection
- [Scaling policy based on Amazon SQS](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-using-sqs-queue.html): why queue depth fails for target tracking and how to compute backlog per instance
- [What is Application Auto Scaling?](https://docs.aws.amazon.com/autoscaling/application/userguide/what-is-application-auto-scaling.html): the scalable target list and the four supported policy types
- [What is a scaling plan?](https://docs.aws.amazon.com/autoscaling/plans/userguide/what-is-a-scaling-plan.html): the five scaling plan resource types and the recommendation to set predictive scaling policies directly
- [Migrate your scaling plan](https://docs.aws.amazon.com/autoscaling/plans/userguide/migrate-scaling-plan.html): the documented migration path and the cooldown settings Application Auto Scaling exposes but EC2 Auto Scaling does not
