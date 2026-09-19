# Amazon ECS and Amazon ECR

**Where it sits on the exams.** **Amazon Elastic Container Service (Amazon ECS)** is the AWS container orchestrator: you describe an application as a task definition, hand it to a cluster, and ECS places, restarts, scales and replaces the containers for you. **Amazon Elastic Container Registry (Amazon ECR)** is the managed registry holding the images those tasks run, one private registry per account per Region. The pair appears in SAA-C03 tasks 2.1, 3.2 and 4.2, behind the wording "the orchestration of containers", "how to migrate applications into containers" and "optimization of compute utilization", and in SAP-C02 tasks 4.3 and 4.4, where the skill is "selecting the appropriate container hosting platform", with supporting appearances in SAP-C02 tasks 1.1 and 2.1. The rule of thumb the exam rewards is to separate the two questions it always asks together: ECS against **Amazon EKS**, the managed Kubernetes service, decides the orchestrator, and Fargate against EC2 decides who owns the servers. A stem that says "least operational overhead" and names no Kubernetes requirement is asking for ECS on Fargate.

## What Amazon ECS is and how a task runs

ECS has three layers: capacity, the infrastructure the containers run on; the controller, which is the scheduler; and provisioning, the tools you use to talk to it. AWS runs the control plane, so unlike Kubernetes there is no cluster endpoint of your own to patch or size.

A *task definition* is the blueprint: a JSON document naming one or more container definitions, each with an image URI, port mappings, environment variables, a log configuration and resource settings. Registering it produces an immutable numbered revision in a family, for example `checkout:41`, so a deployment is really a change of revision. A task definition holds at most 10 container definitions and may not exceed 64 KiB. A *cluster* groups the capacity and the work running on it. A *task* is one running instantiation of a task definition, and containers in the same task always land on the same host and share a lifecycle. A *service* keeps a desired number of identical tasks running, replaces any that die, and optionally registers them with a load balancer. On EC2 capacity a *container agent* on every instance reports utilization and starts and stops containers when ECS tells it to.

CPU and memory can be set at two levels, and the exam tests the difference. Task-level `cpu` and `memory` size the whole task and are mandatory on Fargate; container-level `cpu`, `memory` and `memoryReservation` divide that envelope among containers. Container `memory` is a hard limit and a container that exceeds it is killed, while `memoryReservation` is a soft limit that ECS reserves on the host while letting the container burst up to the hard limit or to whatever is spare. A container that normally uses 128 MiB and occasionally spikes to 256 MiB is best expressed as a `memoryReservation` of 128 with a `memory` hard limit of 300. Container `cpu` is in CPU units, 1,024 to a vCPU, and on Linux it is a share rather than a ceiling. If no task-level memory is set, every container must set at least one of `memory` or `memoryReservation`.

Containers suit workloads that are stateless and horizontally scalable, because the scheduler may stop and replace any task at any moment and a replacement starts from the image with nothing carried over. Migrating an application into containers therefore means four things: package every dependency into the image, move session and file state out to a database, a cache, an EFS file system or an EBS volume, write logs to stdout and stderr so the log driver collects them, and handle SIGTERM to shut down inside `stopTimeout`. Run one process per container and tag images with a unique version rather than `latest`. A stateful application that cannot be changed can still be containerized, but it belongs on the EC2 launch type with a rolling deployment, because running two parallel environments is exactly what its state makes difficult.

The ECS against EKS decision belongs in one paragraph, because [Amazon EKS](eks.md) owns the Kubernetes material. Choose ECS when the team wants containers orchestrated with the least moving parts: task definitions are short, IAM is the only identity system involved, and integration with **Elastic Load Balancing (ELB)**, the managed load balancing service whose Application and Network Load Balancers front ECS services, and with **Amazon CloudWatch**, the AWS monitoring service, is built in. Choose EKS when the requirement names Kubernetes, an existing Helm chart or operator, or a portable control plane the team can also run on premises. The cost shape follows: EKS bills a per-cluster hourly fee, while ECS orchestration is free and you pay only for capacity. A stem containing "existing Kubernetes manifests" or "the team already runs Kubernetes" is an EKS question; a stem that only wants containers run and scaled is an ECS question.

## Launch types, capacity providers, and Fargate

ECS runs tasks on three kinds of host: **Amazon EC2**, the service that rents virtual servers you administer; **AWS Fargate**, the serverless container engine where no instance exists in your account; and your own hardware. A launch type declares which of these a task definition is compatible with, through `requiresCompatibilities`. A capacity provider says where a task or service actually runs, through a capacity provider strategy. AWS now recommends using launch types only to declare compatibility and capacity providers to place work, because a service can move between capacity providers in place while launch type to launch type migration is not supported. A cluster may mix provider types, but a single strategy may not, and a cluster is limited to 20 capacity providers. A strategy gives each provider a `weight` and optionally one a `base`, so a service can keep four tasks on on-demand capacity and spread the rest across cheaper capacity.

Read this table by finding the row that restates the requirement in the stem, then taking the option in that column.

| Option | Who manages the host | How you pay | What you can tune | Wording that selects it |
|---|---|---|---|---|
| EC2 launch type, or an Auto Scaling group capacity provider | You do: AMI, patching, agent version, instance count | EC2 charges only, no ECS fee | Instance type, GPUs, custom AMIs, privileged containers, placement strategies, Spot | "specialized hardware", "GPU", "custom AMI", "privileged", "we already own Reserved Instances" |
| AWS Fargate, and Fargate Spot | AWS does, entirely: no instance exists in your account | Per vCPU-second and GB-second from image download until the task stops, one-minute minimum | Task size from the published vCPU and memory combinations, which run from 256 CPU units, a quarter of a vCPU, with 512 MiB of memory, up to 32,768 units, 32 vCPUs, with 244 GB, where the 8, 16 and 32 vCPU sizes need Linux platform version 1.4.0, platform version, ephemeral storage | "no servers to manage", "least operational overhead", "spiky workload", "each task must be isolated" |
| **Amazon ECS Managed Instances** | AWS provisions, patches and scales EC2 instances that still appear in your account | EC2 charges plus a per-instance management fee | Instance attributes, GPUs, accelerators, optional one task per instance | "Fargate simplicity with EC2 flexibility", "specific instance capabilities without managing instances" |
| External, with **Amazon ECS Anywhere** | You do, on your own hardware, running the ECS agent and the SSM Agent | A flat fee per registered on-premises instance-hour | Whatever the host offers; `bridge`, `host` or `none` networking only | "on-premises servers", "data residency", "one control plane for cloud and data center" |

Fargate Spot runs interruption-tolerant tasks on spare capacity at a discount, with a two-minute warning delivered as a SIGTERM and an **Amazon EventBridge**, the managed event bus, task state change event carrying stop code `SpotInterruption`. Fargate does not fall back to on-demand capacity when Spot is short, so pair a Spot provider with an on-demand `base` to keep a steady core running. A container's `stopTimeout`, 30 seconds by default and settable up to 120, is how long you get after SIGTERM.

Fargate platform versions pin the kernel and container runtime. The current `LATEST` Linux platform version is 1.4.0 and the current Windows platform version is 1.0.0, numbered independently. New tasks always start on the newest revision of the version you named, so patching happens by starting new tasks. What Fargate does not support is a reliable source of exam answers. The parameters `privileged`, `gpu`, `ipcMode`, `links`, `placementConstraints`, `maxSwap` and `swappiness` are all invalid; Docker volumes are unsupported, leaving bind mounts, **Amazon EBS**, the block storage service, and **Amazon EFS**, the managed NFS file system; the only Linux capability you may add is `CAP_SYS_PTRACE`; the network mode is always `awsvpc`; and the daemon scheduling strategy is unavailable. Managed Instances closes most of those gaps while keeping AWS responsible for patching, and it accepts existing Fargate task definitions written for platform version 1.4.0, which makes that migration straightforward.

Cluster auto scaling is how an Auto Scaling group capacity provider grows and shrinks. Managed scaling makes ECS publish a `CapacityProviderReservation` metric, the ratio of instances needed to instances running, and attach a target tracking policy against your `targetCapacity`. At the default target of 100 percent tasks queue in `PENDING` while instances launch, so a lower target buys headroom at the cost of idle instances. Managed termination protection stops scale-in from killing an instance that still has tasks, and managed instance draining, on by default, drains tasks first. Purchasing options belong to [Amazon EC2](../02-compute/ec2.md) and the group to [Amazon EC2 Auto Scaling](../02-compute/ec2-auto-scaling.md).

## Task networking and the network modes

The network mode in the task definition decides what a task looks like on the network. In `awsvpc` mode ECS allocates the task its own elastic network interface (ENI) with a private address in a subnet of an **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network your resources run in, attaches the security groups you name, and gives the task the networking properties of an EC2 instance: VPC Flow Logs see it, security group rules apply to it alone, and containers inside the task reach each other over `localhost`. That is the answer whenever a stem asks for per-task security groups or per-task flow visibility, and it is mandatory on Fargate. In `bridge` mode, the Linux default, tasks share the instance's interface through a Docker virtual network and host ports can be assigned dynamically. In `host` mode the container binds directly to the instance's interface, which means a fixed `hostPort` and therefore only one copy of that task per instance. `none` gives no external connectivity, and `default` is the Windows equivalent of bridge.

Two `awsvpc` constraints decide questions. An interface per task consumes the instance's ENI allowance, so a `c5.large` supporting three interfaces, one primary, runs roughly two such tasks; the `awsvpcTrunking` account setting raises that ceiling on supported instance types by having ECS attach a managed trunk interface. And a task's `awsVpcConfiguration` may name at most 16 subnets and 5 security groups. A Fargate task in a private subnet needs a NAT gateway to pull images, or, better, interface VPC endpoints for ECR so the pull uses the task's private address and never leaves the AWS network. Tasks on EC2 instances in `awsvpc` mode never receive public addresses. External instances cannot use `awsvpc`, which is why they also cannot use ELB target registration or ECS service discovery.

## The task execution role against the task role

This is the most reliably tested distinction in the container material, decided by one question: who needs the permission, the ECS agent or your code?

The *task execution role* is assumed by the ECS container agent and the Fargate agent to set the task up before and around your code. It pulls a private image from ECR, writes container logs to CloudWatch Logs through the `awslogs` driver, authenticates to a private third-party registry, and resolves the `secrets` block that injects values from **AWS Secrets Manager**, the managed secret store with rotation, or **AWS Systems Manager Parameter Store**, the configuration parameter store. AWS publishes the `AmazonECSTaskExecutionRolePolicy` managed policy for it, and the credentials are never exposed to your containers.

The *task role* is assumed by the application inside the container. It is what lets your code call **Amazon S3**, the object storage service, or publish to a queue, and the SDK picks it up automatically through the container credential provider. So "the task cannot pull its image from Amazon ECR" or "the logs never appear in CloudWatch Logs" is an execution role problem, and "the application gets AccessDenied calling S3" is a task role problem. A task role also overrides any instance profile on the host.

Three more roles complete the picture. The container instance role lets an EC2 or external instance register with the cluster. The ECS Anywhere role lets an on-premises instance reach AWS APIs, with **AWS Systems Manager**, the operations and hybrid management service, rotating its credentials every 30 minutes against a hardware fingerprint. The ECS infrastructure role lets ECS manage resources on your behalf: load balancer resources for native blue/green deployments, EBS volume attachment, and TLS certificates for Service Connect. Note the caveat AWS states plainly: containers are not a security boundary, and on EC2, Managed Instances and ECS Anywhere a compromised container may reach another task's credentials or the instance metadata service. Only Fargate isolates each task, which is why "strict workload isolation between tenants" selects Fargate.

## Services, scheduling strategies, and connecting them together

A service has a scheduling strategy. `REPLICA` maintains a desired count and, with no placement strategy, spreads tasks across Availability Zones. `DAEMON` runs exactly one task on every active container instance satisfying the placement constraints, needs no desired count and no scaling policy, and is what you use for a log router, metrics agent or security sidecar that must exist once per host. The exam's trap is that `DAEMON` is unavailable on Fargate and under the CodeDeploy and external deployment controllers, and that a daemon deployment must run with `maximumPercent` at 100.

On EC2 capacity you can steer placement. A placement strategy of `binpack` on `cpu` or `memory` packs tasks tightly to minimize instance count and cost, `spread` on `attribute:ecs.availability-zone` maximizes resilience, and `random` does neither. Strategies are a best effort, but placement constraints are binding: `distinctInstance` forbids two tasks of a group on one host, and a `memberOf` expression in the cluster query language selects hosts by attribute, for example `attribute:ecs.instance-type =~ g5.*`.

Service Auto Scaling changes the desired count through **Application Auto Scaling**, the service that scales targets other than EC2 instances on the `ecs:service:DesiredCount` dimension. Target tracking against `ECSServiceAverageCPUUtilization`, `ECSServiceAverageMemoryUtilization` or ALB request count per target is the default answer; step scaling reacts to alarm breach size; scheduled actions handle known peaks; predictive scaling learns daily and weekly patterns; and queue-based scaling uses a backlog-per-task custom metric from **Amazon SQS**, the managed message queue, which is right for worker fleets where CPU stays flat while the queue grows. Load balancer integration registers tasks in a target group, using the `ip` target type in `awsvpc` mode and `instance` otherwise, with five target groups allowed per service; health checks and target types are owned by [Elastic Load Balancing](../02-compute/elastic-load-balancing.md).

Two mechanisms connect services to each other. *Service discovery* registers each task in **AWS Cloud Map**, the service registry, which creates a private hosted zone in **Amazon Route 53**, the managed DNS service, so clients resolve a name like `orders.internal` to the task addresses. It is DNS only, with no load balancing or retry logic, is capped at 1,000 tasks per service by a Cloud Map quota, and its resources must be cleaned up by hand. **ECS Service Connect** is the newer answer and the one to reach for: it injects a proxy container into every task, gives each service a short name inside a Cloud Map namespace, and adds client-side round-robin load balancing, outlier detection, retries, per-connection metrics and logs, and optional TLS with certificates from **AWS Private Certificate Authority**, the managed private certificate authority service. Configuration lives in the service rather than the VPC, so one task definition runs unchanged in several namespaces, and a deployment can shift traffic through it instead of a load balancer, at no charge beyond the compute the proxy uses. Cloud Map is on the SAA-C03 out-of-scope list, so an Associate question will describe DNS-based discovery without naming it.

## Deployment strategies and detecting a bad rollout

Every ECS service has a deployment controller, and blue/green is now native. With the `ECS` controller you choose a strategy. `ROLLING` replaces tasks in place, governed by `minimumHealthyPercent`, the floor on healthy running tasks as a percentage of desired count, and `maximumPercent`, the ceiling on total tasks. At 50 and 200 with a desired count of four, the scheduler may stop two before starting two, or start four before stopping four. Setting both so nothing can start or stop stalls the deployment, and ECS emits a service event saying so. `BLUE_GREEN` stands the new service revision up beside the old one, optionally sends test traffic to it first, shifts production traffic, then keeps the blue revision running for a *bake time* so a rollback is immediate rather than a redeploy. `LINEAR` shifts traffic in equal increments over a period, and `CANARY` sends a small percentage first and the rest after an interval. All three need an Application Load Balancer, a Network Load Balancer or Service Connect, double the resources in use during the shift, and require the ECS infrastructure role for load balancers. Lifecycle hooks run a Lambda function or a pause point at named stages so automated tests gate the traffic shift.

The `CODE_DEPLOY` controller is the older blue/green path, driven by **AWS CodeDeploy**, the deployment service, with an application, a deployment group, an AppSpec file naming the task definition and container port, and predefined configurations such as `CodeDeployDefault.ECSCanary10Percent5Minutes`. Both exam guides still describe blue/green on ECS this way, but AWS now recommends the native ECS blue/green deployment and publishes migration guidance to it, so treat a question naming CodeDeploy as valid and a green-field design as native. The `EXTERNAL` controller hands control to a third-party tool through the task set APIs `CreateTaskSet`, `UpdateTaskSet` and `UpdateServicePrimaryTaskSet`, and is the answer only when a stem insists on an existing non-AWS deployment system.

Failure detection has two independent mechanisms, usable together. The deployment circuit breaker, available only on the rolling update controller, watches whether tasks reach `RUNNING` and then whether their ELB, Cloud Map or container health checks pass, marks the deployment `FAILED` at a threshold, and with rollback enabled restarts the last `COMPLETED` revision. CloudWatch alarm based detection fails a deployment on an application metric instead, catching a build that starts cleanly and then errors. Both emit `SERVICE_DEPLOYMENT_FAILED` to EventBridge. Pipelines that wrap these steps belong to [developer tools and CI/CD](../08-management/developer-tools-and-cicd.md).

## Amazon ECR: repositories, scanning, and image supply chain

Every account gets one private ECR registry per Region at `aws_account_id.dkr.ecr.region.amazonaws.com`, holding repositories of Docker and OCI images, with namespaced names so `team-a/web-app` and `team-b/web-app` coexist. Access is controlled twice over: identity-based IAM policies on the caller, and resource-based repository policies, which is how you grant another account pull access without a role. A registry permissions policy, distinct from a repository policy, governs registry-level operations such as replication. Clients authenticate with an authorization token from `GetAuthorizationToken` whose scope matches the calling principal and which is valid for 12 hours. Images are encrypted at rest with S3-managed AES-256 keys by default, or with an **AWS KMS**, the managed key service, key chosen at repository creation and never changeable afterward.

Tag immutability is the supply-chain control the exam asks about. A mutable repository lets `docker push` overwrite an existing tag, so `myapp:v1.2` can silently change under a running service. Setting the repository to `IMMUTABLE` makes a push to an existing tag fail with `ImageTagAlreadyExistsException`, which is what you want for release tags. Because a strictly immutable repository also blocks a pull through cache from refreshing a cached tag, ECR supports `IMMUTABLE_WITH_EXCLUSION` and `MUTABLE_WITH_EXCLUSION`, where wildcard filters carve out the few tags that should behave the other way, for example leaving `latest` mutable in an otherwise immutable repository.

Lifecycle policies keep repositories from growing without limit. A policy holds up to 50 rules, each with a unique `rulePriority` evaluated lowest first, a `tagStatus` of `tagged`, `untagged` or `any`, and for tagged rules either a `tagPatternList` with wildcards or a `tagPrefixList`, never both. The count type is `imageCountMoreThan` to keep only the newest N, or `sinceImagePushed`, `sinceImagePulled` or `sinceImageTransitioned` with a `countUnit` of days. The action is `expire` to delete or `transition` to move the image to the cost-optimized ECR Archive storage class, which cannot be pulled from directly and charges a per-GB retrieval fee with a 90-day minimum duration. One evaluation rule decides questions: an image is expired or archived by exactly one rule or none, so a high-priority rule protecting production tags shields them from a lower-priority catch-all. Run the preview first, and expect action within 24 hours.

Scanning comes in two grades. *Basic scanning* uses AWS native technology against more than 50 CVE data feeds to find operating system package vulnerabilities, runs on push or manually, and allows one scan per image per 24 hours. *Enhanced scanning* is an integration with **Amazon Inspector**, the automated vulnerability management service, adding programming language package vulnerabilities on top of the operating system, rescanning continuously as new CVEs are published rather than only at push time, and emitting EventBridge events when a finding is created, updated or closed. It carries Inspector charges, has no manual scan option, applies only to repositories matching its filters, and when first enabled recognizes only images pushed in the last 14 days. Any stem asking for continuous notification of newly disclosed vulnerabilities in a language dependency is enhanced scanning; a stem asking only to check images cheaply at build time is basic scanning. Findings are covered in [detection and compliance services](../07-security/detection-and-compliance-services.md).

Replication and caching move images to where they are pulled. *Replication* is a registry setting, not a repository setting: up to 25 rules with at most 25 destinations copy repositories cross-Region and cross-account, with the destination account granting `ecr:ReplicateImage` and `ecr:CreateRepository` in its registry permissions policy. Only content pushed after replication is configured is replicated, so preexisting images need a re-push; replication is single-hop, so A to B to C does not chain; names cannot change and it never deletes; and lifecycle and repository policies are not replicated. *Pull through cache* points your registry at an upstream one, so a first pull through your registry URI fetches and caches the image and later pulls are served locally, with ECR revalidating a tag upstream at most once every 24 hours. Supported upstreams are ECR Public, the Kubernetes registry and Quay without authentication; Docker Hub, Azure Container Registry, GitHub Container Registry and others with a Secrets Manager secret whose name starts with `ecr-pullthroughcache/`; and another ECR registry with an IAM role. The first pull through a rule needs a route to the internet even when ECR is otherwise reached through an interface endpoint, and **AWS Lambda**, the function service, cannot pull through one. *Repository creation templates* apply a namespace-matched set of settings, tag immutability, encryption, policies and tags, to repositories ECR creates on your behalf. ECR pricing is per GB-month of storage plus data transfer out, so lifecycle policies are the cost lever.

## Professional depth

At organization scale the registry becomes shared infrastructure. The common pattern gives one build account ownership of the images and grants every workload account pull access through a repository policy conditioned on `aws:PrincipalOrgID`, so a new account inherits access without a policy edit. Cross-Region replication then pushes the same images into every Region a workload runs in, which matters for disaster recovery: a warm standby that cannot pull its images has not been tested. Three constraints surprise people at cutover, each producing a configuration that quietly does nothing: replication only copies what is pushed after it is configured, it does not chain through a second hop, and it is authorized in the destination registry rather than the source repository.

Quotas bind before architecture does. A service supports 5,000 tasks, or 1,000 when service discovery is attached, because of the Cloud Map instance quota. A cluster supports 5,000 services and 5,000 container instances, and only 500 tasks may sit in `PROVISIONING` at once under an Auto Scaling group capacity provider. A service may launch 500 tasks per minute, dropping to 125 per minute on Fargate in newer Regions. New accounts start with a Fargate On-Demand vCPU concurrency quota of 6 that AWS raises automatically with usage, which is the quota that ruins an unrehearsed migration cutover. On ECR the request rates bind first: `PutImage` at 10 per second throttles a build farm long before the 100,000 repositories per Region does.

Hybrid and migration work is where ECS Anywhere earns its place, and its limits decide the design. An external instance runs the ECS agent and the SSM Agent, registers to exactly one cluster at a time, and is billed per registered instance-hour. It cannot use `awsvpc` networking, a load balancer, service discovery, EFS volumes or capacity providers, so you must use the `EXTERNAL` launch type directly. That makes it right for outbound and batch work near on-premises data, or a requirement that processing stay in a given building, and wrong for a public web tier. Windows support has been deprecated and the supported operating system list narrowed in 2026 to Amazon Linux 2023, recent Ubuntu and RHEL 9.

Two failure modes recur at scale and neither announces itself. A rolling deployment with `minimumHealthyPercent` and `maximumPercent` both at 100 on a cluster with no spare capacity cannot start or stop anything, and the service sits unchanged until someone reads the service events. And `awsvpc` interface exhaustion caps task density on EC2 capacity in a way no CPU or memory metric shows: tasks stay in `PROVISIONING` while cluster auto scaling launches instances that cannot help unless `awsvpcTrunking` is enabled.

## Worked scenario

A retailer runs a storefront of eight microservices in one Region plus a nightly pricing job that reads from an on-premises ERP system it cannot move. Peak traffic is five times the overnight floor, every image must be scanned continuously, release tags must be impossible to overwrite, and a failed release must be reversible in seconds.

The storefront runs on ECS with a Fargate capacity provider, because the traffic curve is spiky and nobody wants to patch instances. Each service is one task definition with task-level CPU and memory from the published combinations, `awsvpc` networking into private subnets with a per-service security group, and an interface VPC endpoint for ECR so image pulls never traverse a NAT gateway. An Application Load Balancer fronts the public services, and the eight talk to each other through Service Connect in one Cloud Map namespace, giving short names, client-side load balancing and per-connection metrics with no application change. Each service has a task role scoped to exactly the tables and buckets it touches, alongside one shared task execution role carrying `AmazonECSTaskExecutionRolePolicy` plus read access to the referenced Secrets Manager secrets. Service Auto Scaling target-tracks ALB request count per target, and a worker draining an SQS queue scales on backlog per task instead of CPU.

The pricing job runs as an `EXTERNAL` launch type task on two on-premises virtual machines registered through ECS Anywhere, in `bridge` network mode because `awsvpc` is unavailable there, scheduled by an EventBridge rule; it needs no inbound traffic, which is the shape ECS Anywhere suits. Images live in one ECR registry in a build account: repositories are `IMMUTABLE_WITH_EXCLUSION` leaving only `latest` mutable, enhanced scanning is on registry-wide, a lifecycle policy keeps the 30 newest `release-*` images and expires untagged images after 7 days, and replication copies the release repositories into the recovery Region. Deployments use the ECS blue/green strategy with a Lambda lifecycle hook running smoke tests against the test listener and a 15-minute bake time, so a rollback is a traffic shift back to the blue revision.

The exam asks this two ways. The Associate version asks how each microservice can have its own security group and its own IAM permissions with the least operational overhead, and the keyed answer is Fargate with the `awsvpc` network mode and a distinct task role per service, not one instance profile shared by the cluster. The Professional version adds the on-premises job and the "reversible in seconds" requirement, and the keyed answer is ECS Anywhere with the `EXTERNAL` launch type for the job plus an ECS blue/green deployment with a bake time for the storefront, not a rolling update with a faster circuit breaker.

## Exam lens

- "Run containers with the least operational overhead" or "no servers to manage" maps to ECS on Fargate; the EC2 launch type is the distractor that reintroduces patching.
- "Run containers on our own servers under one control plane" maps to ECS Anywhere with the `EXTERNAL` launch type; load balancing and service discovery are unavailable there.
- "GPU", "custom AMI" or "privileged container" maps to the EC2 launch type or Managed Instances; Fargate supports none of those.
- "The application keeps session state on local disk" maps to externalizing that state before containerizing, or to the EC2 launch type with a rolling deployment when the application cannot be changed.
- "Each task needs its own security group" maps to the `awsvpc` network mode; `bridge` shares the instance's interface.
- "The application code needs to read from Amazon S3" maps to the task role; "the task cannot pull its image" or "logs are not reaching CloudWatch Logs" maps to the task execution role.
- "A monitoring or logging agent on every container instance" maps to the `DAEMON` scheduling strategy, which is unavailable on Fargate.
- "Workers sit idle on CPU while the queue grows" maps to queue-based scaling on backlog per task, not CPU target tracking.
- "Services must find each other by name, with retries and per-connection metrics" maps to ECS Service Connect; DNS-only service discovery through AWS Cloud Map is the distractor.
- "Validate the new version with production traffic and roll back instantly" maps to the ECS blue/green strategy with a bake time; a rolling update with the circuit breaker rolls back in minutes, not seconds.
- "A release tag must never be overwritten" maps to ECR tag immutability, with exclusion filters when a pull through cache must still refresh a tag.
- "Notify us when a new CVE affects a language dependency in an image we already pushed" maps to ECR enhanced scanning with Amazon Inspector; basic scanning finds operating system issues only.
- "The same images must exist in a second Region and in other accounts" maps to ECR replication, configured in registry settings, with the destination registry granting permission.
- "Docker Hub rate limits are breaking our builds" maps to an ECR pull through cache rule with a Secrets Manager secret.

## Knowledge check

### 1. A spiky storefront with no patching budget (Associate)

A retailer runs six containerized microservices whose combined traffic varies between 4 and 25 times the overnight baseline over the course of a day. The platform team is three people and has no capacity to manage operating systems, AMIs or agent versions. Each service must have its own network-level isolation so that a compromise of one cannot reach another over the network.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Run the services on Amazon ECS with the EC2 launch type, using an Auto Scaling group capacity provider and the `bridge` network mode with dynamic port mapping.
- **B)** Run the services on Amazon ECS with a Fargate capacity provider, using the `awsvpc` network mode and a separate security group for each service.
- **C)** Run the services on Amazon EKS with self-managed node groups and a network policy per namespace.
- **D)** Run each service on its own Amazon EC2 Auto Scaling group behind an Application Load Balancer, with a security group per group.

<details><summary>Answer</summary>

**Answer: B.** Fargate removes every host-level task, and the `awsvpc` network mode gives each task its own elastic network interface so a distinct security group can be attached per service. A is wrong twice: the EC2 launch type keeps the team responsible for AMIs, patching and agent updates, and `bridge` mode shares the instance's interface so security groups cannot separate services. C adds a Kubernetes control plane and self-managed nodes, which is strictly more operational work than ECS on Fargate and is not justified by any stated Kubernetes requirement. D abandons containers entirely and leaves six fleets of instances to patch, which is the highest overhead option in the set.

*Where this is covered: Launch types, capacity providers, and Fargate.*

</details>

### 2. Two failures with one cause each (Associate)

A team deploys a task on AWS Fargate. The task fails to start, and the event says the image could not be pulled from a private Amazon ECR repository. After that is fixed, the application starts but every call it makes to an Amazon S3 bucket returns an AccessDenied error. The task definition currently references a single IAM role.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Grant the task execution role permission to call `ecr:GetAuthorizationToken`, `ecr:BatchGetImage` and `ecr:GetDownloadUrlForLayer`, for example through the `AmazonECSTaskExecutionRolePolicy` managed policy.
- **B)** Grant the task role permission to call `ecr:BatchGetImage` and `ecr:GetDownloadUrlForLayer`.
- **C)** Attach an instance profile with Amazon S3 permissions to the container instances that host the task.
- **D)** Specify a task role in the task definition and grant it `s3:GetObject` on the bucket.
- **E)** Add the S3 permissions to the task execution role.

<details><summary>Answer</summary>

**Answer: A and D.** The image pull is performed by the Fargate agent using the task execution role, so the ECR permissions belong there, and the managed policy exists for exactly this case. The application's own S3 calls use the task role, which the SDK picks up through the container credential provider. B puts the pull permissions on the wrong role, since the task role is never consulted for image pulls. C is impossible on Fargate, where there is no instance in your account and no instance profile, and would be poor practice on EC2 because it grants the permission to every task on the host. E confuses the two roles in the other direction: the execution role's credentials are held by the agent and are never exposed to your application code.

*Where this is covered: The task execution role against the task role.*

</details>

### 3. A logging agent on every host (Associate)

A company runs Amazon ECS services on a cluster of Amazon EC2 instances managed by an Auto Scaling group capacity provider. Compliance requires a vendor log-forwarding container on every container instance in the cluster, including instances added later by a scale-out event, and it must start before the application tasks on a new instance.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create a service with the `DAEMON` scheduling strategy for the log-forwarding task definition.
- **B)** Create a service with the `REPLICA` scheduling strategy and set the desired count equal to the Auto Scaling group's desired capacity.
- **C)** Add the log-forwarding container to every application task definition as a sidecar.
- **D)** Use an Amazon EC2 Auto Scaling lifecycle hook to run a script that starts the container with the Docker CLI on each new instance.

<details><summary>Answer</summary>

**Answer: A.** The daemon scheduling strategy places exactly one task on every active container instance that meets the placement constraints, tracks instances as they join and leave the cluster, and ECS prioritizes daemon tasks so they are first to launch on a new instance and last to stop. B breaks every time the group scales, because a replica count is a fixed number that has no relationship to which instances exist or how tasks are distributed. C multiplies the agent by the number of tasks rather than the number of hosts, wasting resources and duplicating logs. D bypasses ECS entirely, leaving containers the scheduler does not know about, does not restart and does not account for in capacity calculations.

*Where this is covered: Services, scheduling strategies, and connecting them together.*

</details>

### 4. Release tags that keep changing (Associate)

An audit found that a container image tagged `release-2024-11` in Amazon ECR no longer matches the artifact that was reviewed, because a later build pushed the same tag. The company must make it impossible to overwrite release tags, while a separate pull through cache rule in the same repository must keep refreshing a `latest` tag from an upstream registry.

Which solution will meet these requirements?

- **A)** Set the repository to `IMMUTABLE` and disable the pull through cache rule.
- **B)** Set the repository to `IMMUTABLE_WITH_EXCLUSION` with a wildcard exclusion filter for `latest`.
- **C)** Add a lifecycle policy rule with `tagPatternList` set to `release-*` and an `expire` action.
- **D)** Enable enhanced scanning on the repository so that changed images are detected.

<details><summary>Answer</summary>

**Answer: B.** Tag immutability is a repository setting, and the exclusion filters exist for exactly this conflict: an immutable repository blocks pull through cache from updating a cached tag, so naming `latest` as an exclusion keeps that one tag mutable while every release tag is protected. A protects the tags but sacrifices the caching requirement stated in the stem. C deletes the release images rather than protecting them, which is the opposite of the requirement. D detects vulnerabilities in images, not tag overwrites, and does nothing to prevent a push.

*Where this is covered: Amazon ECR: repositories, scanning, and image supply chain.*

</details>

### 5. A deployment that must be reversible in seconds (Associate)

A payments service runs on Amazon ECS behind an Application Load Balancer. A recent release passed its health checks but returned errors for 20 minutes while a rolling update finished and a second rolling update restored the previous version. The team wants the next release validated against production traffic before it is fully adopted, and wants any rollback to take effect immediately rather than requiring tasks to be replaced again.

Which solution will meet these requirements?

- **A)** Keep the rolling update strategy and set `minimumHealthyPercent` to 100 and `maximumPercent` to 200.
- **B)** Keep the rolling update strategy and enable the deployment circuit breaker with rollback.
- **C)** Change the service to the ECS blue/green deployment strategy with a test listener, a lifecycle hook and a bake time.
- **D)** Change the service to the external deployment controller and manage task sets from a custom pipeline.

<details><summary>Answer</summary>

**Answer: C.** The native ECS blue/green strategy stands the new revision up alongside the old one, can send test traffic to it through a test listener, gates the production shift on a lifecycle hook, and keeps the blue revision running for the bake time so rolling back is a traffic shift rather than another task replacement. A only changes how fast tasks are swapped; the old revision is still gone once it completes. B stops a deployment whose tasks fail health checks, but this release passed its health checks, and its rollback works by replacing tasks, which is the minutes-long path the stem rejects. D achieves the outcome only by building and operating the whole blue/green mechanism yourself, which is the most operational overhead of the four.

*Where this is covered: Deployment strategies and detecting a bad rollout.*

</details>

### 6. A nightly job that cannot leave the data center (Professional)

A manufacturer must keep a nightly reconciliation job inside its own data center for regulatory reasons, but wants it containerized and managed from the same control plane, task definitions and CloudWatch log groups as the rest of its workloads, which run on Amazon ECS in two AWS accounts. The job makes only outbound calls, takes about 40 minutes, and must be scheduled centrally.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Register the on-premises virtual machines as external instances with Amazon ECS Anywhere and run the job as a service with the `awsvpc` network mode behind a Network Load Balancer.
- **B)** Deploy **AWS Outposts**, the AWS-managed racks installed in your own data center, and run the job on Amazon ECS with the EC2 launch type.
- **C)** Run the job on AWS Fargate and reach the on-premises systems over **AWS Site-to-Site VPN**, the encrypted tunnel between a VPC and a data center.
- **D)** Register the on-premises virtual machines as external instances with Amazon ECS Anywhere, run the job with the `EXTERNAL` launch type in `bridge` network mode, and trigger it with an Amazon EventBridge Scheduler rule.

<details><summary>Answer</summary>

**Answer: D.** ECS Anywhere registers an on-premises server or virtual machine as an external instance, which keeps task definitions, scheduling and logging in ECS while the work runs on your hardware, and outbound-only batch work is precisely the shape AWS says external instances suit. A breaks on two documented limits: external instances do not support the `awsvpc` network mode and cannot be registered with an Elastic Load Balancing target group. B meets the requirement but installs and operates physical racks to run one 40-minute nightly job, far more overhead than registering a virtual machine. C moves the processing into AWS, which the regulatory constraint in the stem forbids regardless of how the network is built.

*Where this is covered: Launch types, capacity providers, and Fargate.*

</details>

### 7. Images missing in the recovery Region (Professional)

A company runs Amazon ECS services in us-east-1 and maintains a warm standby in eu-west-1 in a different AWS account. It enabled cross-Region, cross-account Amazon ECR replication from the production registry last week. During a failover test, services in eu-west-1 failed to start because the images they reference were not present, although images built since last week did replicate. The team also found that a third Region configured to replicate from eu-west-1 received nothing.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Push the existing images again in the source Region so that replication copies them.
- **B)** Add a repository policy in the source account granting the destination account `ecr:ReplicateImage`.
- **C)** Configure a replication rule in the source registry that targets the third Region directly, rather than relying on replication from eu-west-1.
- **D)** Enable a lifecycle policy in the destination account so that replicated images are retained.
- **E)** Increase the images per repository quota in the destination Region.

<details><summary>Answer</summary>

**Answer: A and C.** ECR replicates only content pushed or restored after replication is configured, so images that already existed must be pushed again, and a replication action happens once per push, so replication does not chain from a first destination to a second one. B targets the wrong account and the wrong policy type: cross-account replication is authorized by a registry permissions policy in the destination account granting `ecr:ReplicateImage` and `ecr:CreateRepository`, and source repositories need no policy at all. D would if anything delete images rather than create them, since lifecycle policies expire and archive, and they are not replicated in any case. E is a quota with a default of 100,000 images per repository, far above anything implied here, and a quota breach would not produce this selective pattern.

*Where this is covered: Amazon ECR: repositories, scanning, and image supply chain.*

</details>

### 8. A cutover that stalls at half capacity (Professional)

During a large migration, a company moves 40 services onto one Amazon ECS cluster backed by an Auto Scaling group capacity provider with managed scaling and the `awsvpc` network mode. Under load, new tasks sit in the `PROVISIONING` state for long periods even though CloudWatch shows the container instances have ample free CPU and memory, and the Auto Scaling group keeps launching instances that do not relieve the backlog. The instance type is not GPU-backed and the images are small.

Which solution will meet these requirements?

- **A)** Lower the capacity provider's `targetCapacity` so that the cluster keeps more spare headroom.
- **B)** Turn on the `awsvpcTrunking` account setting and use supported instance types so that more elastic network interfaces can be attached per instance.
- **C)** Switch the services to the `host` network mode so that each task binds directly to the instance interface.
- **D)** Increase the `maximumPercent` value on each service's deployment configuration.

<details><summary>Answer</summary>

**Answer: B.** In `awsvpc` mode each task consumes an elastic network interface on its host, and the per-instance ENI limit, not CPU or memory, caps task density, which is why the free-capacity metrics look healthy while tasks stall and newly launched instances cannot help. The `awsvpcTrunking` account setting raises that limit on supported instance types by having ECS attach a managed trunk interface. A adds more instances that hit the same per-instance interface ceiling, so the symptom persists. C would relieve the interface pressure but forces a fixed host port per task, so only one copy of each task could run per instance and the per-task security group isolation is lost. D governs how many tasks may exist during a deployment and has no bearing on why a task cannot be provisioned.

*Where this is covered: Task networking and the network modes.*

</details>

## Summary

Amazon ECS is a sequence of decisions. Choose the orchestrator first: ECS unless the requirement names Kubernetes, in which case Amazon EKS. Choose the capacity next, preferring a capacity provider to a bare launch type: Fargate for no servers and strict per-task isolation, Fargate Spot for interruption-tolerant work, the EC2 launch type or Managed Instances when GPUs, custom AMIs, privileged containers or existing commitments are in play, and ECS Anywhere when processing must stay in your data center. Size the task with task-level CPU and memory, and divide it with container-level hard and soft limits. Pick `awsvpc` unless something forbids it, remembering it costs a network interface per task. Split permissions correctly: the execution role pulls images and writes logs, the task role is what your code uses. Pick a scheduling strategy, replica or daemon, then a placement strategy, binpack for density or spread for resilience. Deploy with the native blue/green, linear or canary strategy when instant rollback matters, and rolling with the circuit breaker when it does not. On the registry side, make release tags immutable, scan continuously with Inspector, expire images with a lifecycle policy, and replicate to every Region and account that must pull.

## Related units

- [Amazon EKS](eks.md): Kubernetes on AWS, and the other half of the container platform decision
- [Amazon EC2](../02-compute/ec2.md): instance families, purchasing options and Spot behavior for EC2 capacity
- [AWS Lambda](../02-compute/lambda.md): the serverless comparison, and when a function beats a container
- [Elastic Load Balancing](../02-compute/elastic-load-balancing.md): target groups, target types and health checks for ECS services
- [Amazon EC2 Auto Scaling](../02-compute/ec2-auto-scaling.md): the Auto Scaling group behind an EC2 capacity provider
- [Amazon VPC](../04-networking/vpc.md): subnets, NAT gateways, security groups and interface endpoints for ECR and ECS
- [Detection and compliance services](../07-security/detection-and-compliance-services.md): Amazon Inspector findings from ECR enhanced scanning
- [Developer tools and CI/CD](../08-management/developer-tools-and-cicd.md): AWS CodeDeploy, pipelines and deployment strategies across services

## Sources

- [Architect your solution for Amazon ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_types.html): the three layers, cluster, task definition, task, service and agent, when to choose each capacity type, and the container image principles
- [Amazon ECS launch types and capacity providers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/capacity-launch-type-comparison.html): launch types declare compatibility, capacity providers place work, and which migrations are supported
- [Architect for Amazon ECS Managed Instances](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ManagedInstances.html): attribute-based instance selection, consolidation and Fargate task definition compatibility
- [Fargate platform versions for Amazon ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform-fargate.html): Linux LATEST is 1.4.0, Windows is 1.0.0, and how revisions are patched
- [Amazon ECS task definition differences for Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-tasks-services.html): the unsupported parameters and the valid task CPU and memory combinations
- [Amazon ECS clusters for Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html): Fargate Spot, the two-minute warning, and the weight, base and 20 provider strategy rules
- [Automatically manage Amazon ECS capacity with cluster auto scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cluster-auto-scaling.html): CapacityProviderReservation, targetCapacity and managed termination protection
- [Amazon ECS task networking options for EC2](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-networking.html): awsvpc, bridge, host, none and default
- [Allocate a network interface for an Amazon ECS task](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-networking-awsvpc.html): ENI per task, awsvpcTrunking, and the 16 subnet and 5 security group limits
- [IAM roles for Amazon ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-iam-role-overview.html): every role ECS uses and when each is required
- [Amazon ECS task execution IAM role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html): image pulls, log delivery, secrets and AmazonECSTaskExecutionRolePolicy
- [Amazon ECS task IAM role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html): credentials for application code, and the isolation caveat for EC2 capacity
- [Amazon ECS service deployment controllers and strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_service-options.html): replica and daemon scheduling, and the ECS, CodeDeploy and external controllers
- [Amazon ECS blue/green deployments](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-blue-green.html): bake time, lifecycle hooks and the load balancer requirement
- [Deploy Amazon ECS services by replacing tasks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html): minimumHealthyPercent and maximumPercent arithmetic
- [CodeDeploy blue/green deployments for Amazon ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-bluegreen.html): the AWS recommendation to use native ECS blue/green, and the predefined configurations
- [How the Amazon ECS deployment circuit breaker detects failures](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html): the two stages, rollback behavior and the rolling update restriction
- [Use Service Connect to connect Amazon ECS services with short names](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect.html): proxy, namespaces, TLS and pricing
- [Use service discovery to connect Amazon ECS services with DNS names](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html): Cloud Map registration, record types and the 1,000 task limit
- [Automatically scale your Amazon ECS service](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html): target tracking, step, scheduled, predictive and queue-based scaling
- [Use strategies to define Amazon ECS task placement](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-placement-strategies.html): binpack, random and spread
- [Amazon ECS clusters for external instances](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-anywhere.html): ECS Anywhere limits, supported operating systems and required endpoints
- [Amazon ECS endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/ecs-service.html): tasks per service, container instances per cluster, launch rates and Fargate vCPU quotas
- [Amazon ECS pricing](https://aws.amazon.com/ecs/pricing/): no orchestration fee, the Managed Instances management fee and the ECS Anywhere per-instance-hour fee
- [AWS Fargate pricing](https://aws.amazon.com/fargate/pricing/): per-second billing from image download, one-minute minimum and the free 20 GB of ephemeral storage
- [Amazon ECR private registry and repositories](https://docs.aws.amazon.com/AmazonECR/latest/userguide/Registries.html): the registry URI, namespaces and repository policies
- [Preventing image tags from being overwritten in Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html): IMMUTABLE, MUTABLE and the exclusion filter modes
- [Automate the cleanup of images by using lifecycle policies in Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html): rule priority, one-rule matching and the 24-hour action window
- [Lifecycle policy properties in Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/lifecycle_policy_parameters.html): tagStatus, tagPatternList, countType and the expire and transition actions
- [Scan images for software vulnerabilities in Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html): basic against enhanced scanning and their scan frequencies
- [Scan images for OS and programming language package vulnerabilities](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning-enhanced.html): the Amazon Inspector integration, continuous rescanning and the 14-day eligibility window
- [Private image replication in Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/replication.html): destination registry permissions, no backfill, no chaining and the rule limits
- [Sync an upstream registry with an Amazon ECR private registry](https://docs.aws.amazon.com/AmazonECR/latest/userguide/pull-through-cache.html): supported upstreams, the 24-hour revalidation and the first-pull internet requirement
- [Amazon ECR pricing](https://aws.amazon.com/ecr/pricing/): storage per GB-month, data transfer out and the ECR Archive storage class
