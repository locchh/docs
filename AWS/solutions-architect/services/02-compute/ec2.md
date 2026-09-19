# Amazon EC2

**Where it sits on the exams.** **Amazon Elastic Compute Cloud (Amazon EC2)**, the service that rents virtual and bare metal servers by the second, gives you an operating system you control, attached storage, a network interface in your own network, and a bill that changes shape depending on how you buy the capacity. It is the reference compute service for SAA-C03 tasks 2.1, 3.2 and 4.2, and for SAP-C02 tasks 1.5, 2.5, 3.3 and 4.3, and it is the baseline against which containers and serverless are compared. The exam rule of thumb is to pick the instance family from the resource the workload is short of, pick the size from measured utilization, and pick the purchasing option from how predictable and how interruptible the workload is.

## What Amazon EC2 is and how the Nitro System runs it

An EC2 instance is a virtual server running on a physical host in one Availability Zone. You choose an **Amazon Machine Image (AMI)**, the bootable image that supplies the operating system and preinstalled software, an instance type that fixes the hardware, a subnet in **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network in which every instance runs, one or more security groups, and a key pair. EC2 then provisions the instance, attaches its root volume, normally an **Amazon Elastic Block Store (Amazon EBS)** volume from the network-attached block storage service, and hands it an address in the subnet. Everything above the hypervisor is yours to patch and configure; everything below it is AWS's responsibility. That split is the practical meaning of the shared responsibility model for compute, and it is why "the customer must patch the guest operating system" is a correct statement for EC2 and a wrong one for a managed database or a function service.

Current instances run on the **AWS Nitro System**, the collection of AWS-built hardware and software that offloads virtualization work from the main processors. Nitro has three parts. Nitro cards handle networking, local NVMe storage, monitoring, management and security as dedicated hardware. A Nitro security chip is integrated into the motherboard. The Nitro hypervisor is a lightweight hypervisor that manages only memory and CPU allocation and that AWS documents as delivering performance indistinguishable from bare metal for most workloads. Because the input/output paths are offloaded, almost all of the host's compute and memory goes to instances rather than to the virtualization layer.

Nitro is not trivia. It is the precondition for features the exam asks about. Nitro instances use the Elastic Network Adapter for enhanced networking and present all storage volumes as NVMe block devices. Nitro also provides bare metal types, whose `.metal` sizes give an operating system direct access to host hardware for workloads needing low-level processor features such as hardware virtualization extensions, or carrying licensing terms that require a non-virtualized environment. Bare metal instances boot slowly, because the server runs a full hardware and firmware verification: AWS documents that it can take 20 minutes or more from the running state until the instance is reachable over the network. Nitro versions also gate network capability: v3 added encryption in transit and up to 100 Gbps per network card, v4 added ENA Express and remote direct memory access on selected types, v5 raised the ceiling to 200 Gbps per network card, and v6 raises it to 400 Gbps. A question asking for the highest per-instance network throughput is asking for a current-generation Nitro type with multiple network cards.

Instances are placed in a single Availability Zone and cannot move between zones. Resilience therefore comes from running more than one instance in more than one zone behind a load balancer, not from any property of a single instance. The first question to ask about an EC2 design is how many instances it needs and where they sit, and only then which type each one is.

## Instance families, naming, and sizing

Instance type names are structured, and the exam expects you to read them. The first position is the series, the second the generation, the third any options, and everything after the period is the size. In `c7gn.xlarge`, `c` is the compute optimized series, `7` is the generation, `gn` says **AWS Graviton** processors, the AWS-designed Arm line, with extra network and EBS optimization, and `xlarge` is the size. Sizes run from `nano`, `micro`, `small` and `medium` through `large`, `xlarge` and multiples such as `2xlarge`, `4xlarge`, `8xlarge`, `16xlarge`, `24xlarge`, `48xlarge` and `96xlarge`, plus `metal` variants for bare metal. Within a family, resources scale roughly linearly with size, so an `m7i.2xlarge` has about twice the vCPUs and memory of an `m7i.xlarge` and costs about twice as much.

Read this table as a decision aid: find the resource the workload runs out of first, then take the series letters from that row. Series letters are stable across generations, so `c5`, `c7i` and `c8g` all mean compute optimized even though the processors differ.

| Category | Series letters | What it optimizes | Typical workloads | Wording that points here |
|---|---|---|---|---|
| General purpose | **M** balanced, **T** burstable, **Mac** for macOS | Even ratio of vCPU to memory | Web and application servers, small to medium databases, microservices, development environments | "balanced", "general purpose", "low average CPU with occasional spikes" for T |
| Compute optimized | **C**, **Hpc** for high performance computing | Highest CPU per dollar | Batch processing, ad serving, scientific modeling, media transcoding, dedicated gaming servers, tightly coupled HPC | "CPU-bound", "compute-intensive", "high performance computing" |
| Memory optimized | **R**, **X** memory intensive, **U** and **Z** high memory | Most RAM per vCPU | In-memory caches, large relational databases, SAP HANA, real-time analytics over large working sets | "in-memory", "memory-intensive", "large database working set" |
| Storage optimized | **I** and **Im** and **Is**, **D** dense storage | Local NVMe or HDD throughput and random IOPS | NoSQL databases, search, distributed file systems, data warehouses, log processing | "very high random IOPS", "low-latency local storage" |
| Accelerated computing | **P** and **G** for GPUs, **Trn** and **Inf** for AWS accelerators, **F** for FPGA, **VT** for video transcoding | Attached accelerators | Model training and inference, graphics workstations, video encoding, genomics, hardware-accelerated custom logic | "GPU", "model training", "inference", "rendering" |

The option letters after the generation carry most of the detail. Processor letters are `a` for AMD, `i` for Intel, `g` for Graviton, and `m` or `mpro` for Apple chips. Capability letters are `d` for attached instance store volumes, `n` for network and EBS optimization, `b` for block storage optimization, `e` for extra instance storage on storage optimized types, extra memory on memory optimized types or extra GPU memory on accelerated types, `z` for a higher CPU frequency, `q` for Qualcomm inference accelerators, and `flex` for a Flex instance. Graviton types require an Arm64 AMI and a Linux operating system, which is the one constraint that turns a cost-saving Graviton answer into a wrong answer when a scenario mentions Windows or an x86-only binary.

Two shapes inside general purpose decide questions on their own. Burstable **T instances** provide a baseline CPU level and earn CPU credits while running below it, then spend credits to burst above it. In standard mode an instance that exhausts its credits is held at the baseline. In unlimited mode it keeps bursting and you pay a flat additional rate per vCPU-hour for surplus credits. T4g, T3a and T3 launch as unlimited by default unless the account default is changed. AWS specifically recommends standard mode for T instances launched on spot capacity that run immediately and briefly, because there is no idle time to accrue credits and surplus charges follow. Flex instances, the `flex` types in the C, M and R families, take a different bargain: they deliver a 40 percent baseline CPU and can reach 100 percent CPU for 95 percent of the time over a 24-hour window, at a lower price than the full-size equivalent. Choose Flex for general purpose workloads that do not run pinned at high utilization, and choose the non-Flex type when they do.

Sizing is a measurement exercise, not a guess. Start from the resource that saturates first, pick the smallest size in the right family that leaves headroom for peaks, and verify with data. The native CloudWatch metrics for an instance cover CPU, network and disk activity but not memory or guest disk space, so any size chosen for memory needs the CloudWatch agent to justify it. Vertical resizing requires stopping an EBS-backed instance, changing the type and starting it again, so it costs downtime; horizontal scaling adds instances instead and is the preferred answer whenever the workload can be spread. **Instance store** attached types resize badly, because that local data does not survive the stop.

## Choosing the compute platform and the surrounding services

SAA-C03 task 2.1 asks you to recommend compute, storage, networking and database technologies together, and EC2 anchors that choice because it has the fewest constraints and the most operational work. The order that produces correct answers is: decide how much of the stack you want to own, then let each neighboring category follow from the workload's data shape.

On compute, the question is what you must control. Choose **AWS Lambda**, the event-driven function service that runs code without any server to manage, when work arrives as discrete events, finishes inside the function timeout, and scales to zero between invocations; you pay for invocations and duration and you never patch an operating system. Choose **AWS Fargate**, the serverless compute engine for containers, when the unit of deployment is a container image and you want per-task capacity without managing instances. Choose **Amazon Elastic Container Service (Amazon ECS)** or **Amazon Elastic Kubernetes Service (Amazon EKS)**, the AWS container orchestrators, on EC2 capacity when you need control over the host, GPU or specialized hardware, per-instance licensing, or bin packing many small tasks onto large instances. Choose **AWS Batch**, the managed batch scheduler, for queued jobs that exceed a function timeout, and **AWS Elastic Beanstalk**, the managed application platform that provisions EC2 capacity on your behalf, when a team wants a conventional application deployed without designing the stack. Choose EC2 directly when the workload needs a long-lived process, a specific kernel or driver, a license bound to cores or sockets, an unusual runtime, or a lift-and-shift migration where rewriting is out of scope. "Least operational overhead" in a stem is usually pointing away from EC2; "existing application cannot be modified" and "third-party software with a per-core license" point straight at it.

On storage, match the access pattern to the storage type. Block storage attached to one instance is Amazon EBS, the answer for boot volumes and for databases doing random reads and writes. Shared file access across many instances is **Amazon Elastic File System (Amazon EFS)**, the managed elastic Network File System, or **Amazon FSx**, the family of managed file systems for Windows, Lustre, NetApp ONTAP and OpenZFS workloads. Object storage for whole values retrieved over HTTPS is **Amazon Simple Storage Service (Amazon S3)**. Local NVMe instance store is neither of those: it is temporary scratch space belonging to the instance. A scenario that says "several instances must read and write the same files" rules out EBS for the shared layer even though EBS Multi-Attach exists for narrow clustered cases.

On networking, **Elastic Load Balancing**, the managed service that spreads incoming traffic across healthy targets, fronts the instances, and the subnet decides reachability: public subnets with an internet gateway for instances reached from the internet, private subnets with a NAT gateway for outbound access only, and VPC endpoints for private access to AWS service APIs. Distribute traffic with **Elastic Load Balancing** rather than DNS pointed at instance addresses, and put **Amazon CloudFront**, the content delivery network, in front when viewers are global and content is cacheable.

On databases, self-managing an engine on EC2 is defensible only when a specific version, extension, operating system access or licensing model is required. Otherwise **Amazon Relational Database Service (Amazon RDS)** and **Amazon Aurora**, the managed relational services, or **Amazon DynamoDB**, the managed key-value and document database, remove the patching, backup and failover work that a self-managed instance forces you to build. SAP-C02 task 4.3 lists "self-managed databases on Amazon EC2" precisely so you can recognize when the correct recommendation is to move off them.

The cost comparison across compute services follows the same logic. EC2 bills for capacity you hold, so it wins when utilization is high and steady, especially with a commitment discount. Lambda and Fargate bill for work performed, so they win when demand is spiky, low duty cycle, or unpredictable. A workload running one instance at 90 percent utilization all month is cheaper on EC2 with a **Savings Plan**, the hourly spend commitment discount covered in the next section, than on any per-request model; a workload that runs for 20 minutes a day is cheaper on Lambda even at a higher unit rate.

## Purchasing options and commitment models

EC2 usage is billed in one-second increments with a minimum of 60 seconds, and the same running instance can be billed at very different rates depending on how you bought it. Read the table by the two variables that actually vary: what you commit to, and whether capacity is reserved.

| Purchasing option | What you commit to | Discount shape | Reserves capacity | Best fit |
|---|---|---|---|---|
| **On-Demand Instances** | Nothing | None, list rate per second | No | Short, unpredictable or first-time workloads, and the baseline every other option is discounted from |
| **Compute Savings Plans** | A dollar per hour of compute spend for 1 or 3 years | Up to 66 percent off On-Demand, applied regardless of instance family, size, Region, operating system or tenancy, and also to Fargate and Lambda | No | Steady total compute spend when the shape of that spend will change |
| **EC2 Instance Savings Plans** | A dollar per hour for one instance family in one Region, for 1 or 3 years | Up to 72 percent off, flexible across size, operating system and tenancy inside that family and Region | No | Steady usage of a known family in a known Region |
| **Reserved Instances** | A specific instance configuration for 1 or 3 years | Up to 72 percent off; Standard discounts most and can only be modified, Convertible discounts less and can be exchanged | Only zonal Reserved Instances reserve capacity | Legacy commitments, Marketplace resale, and the zonal case where capacity assurance and a discount are both required |
| **Spot Instances** | Nothing | Steep discount on spare capacity, with a Spot price set by EC2 and adjusted on long-term supply and demand | No, and EC2 can reclaim the instance | Fault-tolerant, interruptible, stateless or checkpointed work |
| **On-Demand Capacity Reservations** | Nothing for immediate-use reservations; a stated duration for future-dated ones | None on their own, but they combine with Savings Plans and regional Reserved Instances | Yes, in one Availability Zone | Guaranteeing capacity for a launch event, a failover Region, or a regulatory availability requirement |
| **Capacity Blocks for ML** | A defined block of GPU capacity on a scheduled future date | Pay only for the reserved time | Yes, placed in an EC2 UltraCluster, the dense low-latency GPU fabric, rather than in a placement group you create | Short machine learning training runs and experiments on GPU instances |
| **Dedicated Instances** | Nothing beyond per-instance charges | None; a per-Region hourly fee applies | No | Compliance rules that require single-tenant hardware without needing host visibility |
| **Dedicated Hosts** | A physical server, billed per host | Dedicated Host Reservations give up to 70 percent off On-Demand host pricing | Yes, the whole host | Per-socket, per-core or per-VM licenses, and workloads that must return to the same physical server |

Savings Plans are the current recommendation, and AWS says so directly in the Reserved Instances documentation. There are four types: Compute Savings Plans, EC2 Instance Savings Plans, Database Savings Plans covering the managed database services, and SageMaker AI Savings Plans. All use a 1-year or 3-year term and All Upfront, Partial Upfront or No Upfront payment. The distinction the exam tests is coverage: a Compute Savings Plan follows a workload that moves from `c5` to `m5`, from Ireland to London, or from EC2 to Fargate, while an EC2 Instance Savings Plan gives a deeper discount but locks the family and Region. Neither reserves capacity, and neither applies to Spot Instances. The per-Region Dedicated Instance fee is not discounted by any Savings Plan.

Reserved Instances still appear in both exam guides, so know the two axes. Offering class is Standard, which can be modified but not exchanged, or Convertible, which can be exchanged for another Convertible reservation with different attributes at a smaller discount. Scope is regional or zonal, and only the zonal form reserves capacity in its Availability Zone. A regional Reserved Instance gains Availability Zone flexibility and instance size flexibility within the family, but the size flexibility applies only to Amazon Linux and Unix reservations with default tenancy. Reserved Instances cannot be canceled after purchase, though they can be modified, exchanged when Convertible, or sold on the Reserved Instance Marketplace.

Capacity Reservations solve the opposite problem from Savings Plans. They give no discount by themselves and are billed at the On-Demand rate for the reserved capacity whether or not instances occupy it, but they hold capacity in a named Availability Zone with matching instance type, platform and tenancy. An open reservation automatically matches any running or new instance with those attributes, including instances launched on your behalf by **Amazon EC2 Auto Scaling**, the service that keeps a group of instances at the right size, and by ECS, EKS, **Amazon EMR**, the managed big data platform, AWS Batch and Elastic Beanstalk; a targeted reservation is used only by instances that explicitly request it. Active and unused reservations count against your On-Demand Instance limits. They can be created inside a cluster **placement group**, the instance placement control taught later in this unit, but not a spread or partition placement group, cannot be used with Dedicated Hosts, and do not guarantee that a hibernated instance can resume. Capacity Blocks for ML extend the idea to GPU fleets: you can reserve a start time up to eight weeks in the future, each block holds up to 64 instances with up to 256 instances across all your blocks, cancellations are not allowed, and blocks do not support placement groups.

Dedicated Hosts and Dedicated Instances both give single-tenant hardware and AWS documents no performance, security or physical difference between them. The difference is visibility and licensing. A Dedicated Host is billed per host, exposes the number of sockets and physical cores, supports host affinity so an instance returns to the same physical server, allows targeted placement, can be shared with other accounts, and gives comprehensive bring-your-own-license support for per-socket, per-core and per-VM licenses. A Dedicated Instance is billed per instance, shows no socket or core detail, has no affinity or targeted placement, and supports bring-your-own-license only partially, for cases such as Microsoft SQL Server with License Mobility. Dedicated Hosts cannot be launched into placement groups and do not support Capacity Reservations; Dedicated Instances do support Capacity Reservations. When a question mentions a per-core Windows Server or SQL Server license that must be brought to AWS, the answer is a Dedicated Host.

## Spot capacity, fleets, and interruption handling

A Spot Instance runs on spare EC2 capacity at a price EC2 sets and adjusts gradually according to long-term supply and demand for each Spot capacity pool, where a pool is one instance type in one Availability Zone. The bargain is explicit: you take a steep discount and accept that EC2 can reclaim the instance. AWS documents three reasons for an interruption. Capacity is the main one, because EC2 needs the hardware back, though host maintenance and hardware decommissioning also occur. Price is a reason only if you set a maximum price and the Spot price rises above it, which is why setting a maximum price makes interruptions more frequent than leaving it unset. Constraints are the third: a request with a launch group or an Availability Zone group is terminated as a group when the constraint can no longer be met.

The warning signals are the part exam questions hang on. A Spot Instance interruption notice is issued two minutes before EC2 stops or terminates the instance. It arrives both as an `EC2 Spot Instance Interruption Warning` event in **Amazon EventBridge**, the event bus that routes AWS and application events to targets, and as an `instance-action` item in instance metadata at `/latest/meta-data/spot/instance-action`, which names the action and the approximate time. AWS recommends polling that item every five seconds and states that notices are emitted on a best effort basis, so an application must tolerate a missing notice. The hibernate interruption behavior is the documented exception: you receive the notice but not two minutes of warning, because hibernation begins immediately. Separately, an EC2 instance rebalance recommendation is emitted when an instance is at elevated risk of interruption, which gives a longer and earlier signal than the two-minute notice and is the right trigger for draining connections or launching a replacement.

Interruption behavior defaults to terminate. Stop and hibernate are available only when the Spot Instance request type is `persistent`, or the fleet request type is `maintain`, and neither works with a launch group. While an interrupted Spot Instance is stopped you pay only for its EBS volumes, and only EC2 can restart it, which it does when capacity returns in the same Availability Zone for the same instance type. You cannot launch a Spot Instance configured to stop or hibernate on interruption into a placement group.

**EC2 Fleet** and **Spot Fleet** launch tens to thousands of instances in one request from a launch template, across several instance types, several Availability Zones and both purchasing models at once. Spot Fleet is the older API and is Spot-centric; EC2 Fleet is the current one, takes a launch template, and expresses On-Demand and Spot target capacity together, so new designs should use it. Mixing types and zones is the single most effective way to reduce interruptions, because it multiplies the pools the fleet can draw from. The allocation strategy decides which pools get used. AWS recommends `price-capacity-optimized`, which finds the pools with the highest capacity availability and then picks the lowest priced among them; it is the documented best choice for most Spot workloads. Use `capacity-optimized` when interruption cost dominates price, such as long continuous integration runs, rendering and deep learning, and `capacity-optimized-prioritized` when you also want instance types honored in a preference order on a best-effort basis. `diversified` spreads instances across all pools and suits large or long-running fleets. `lowest-price` exists but AWS explicitly does not recommend it, because considering only price and not capacity gives the highest interruption rate. For On-Demand capacity the strategies are `lowest-price`, the default, and `prioritized`, which is how you make a fleet fill On-Demand demand with a family you already hold Reserved Instances for. A `maintain` fleet replaces interrupted instances automatically and, with **Capacity Rebalancing**, proactively replaces instances flagged by a rebalance recommendation.

Spot Instances are not covered by Savings Plans, and Spot spend does not draw down a Compute Savings Plan commitment. The design pattern the exam rewards is a mixed fleet: a baseline of On-Demand or committed capacity sized to the minimum the service must always have, with Spot supplying the elastic remainder, plus checkpointing so that reclaimed work restarts rather than restarts from zero.

## Instance store compared with Amazon EBS, and the instance lifecycle

Every instance has exactly one root volume, and the AMI decides its type. An EBS-backed instance boots from an Amazon EBS volume, whose lifecycle is independent of the instance. An instance store-backed instance boots from disks physically attached to the host. AWS recommends EBS-backed AMIs, and only a short list of older instance types still supports an instance store root volume at all. The practical consequence is the one the exam tests: an instance store-backed instance cannot be stopped, only terminated, and it cannot be recovered after failure, while an EBS-backed instance can be stopped, resized, moved to a new host by a stop and start, and restored from snapshots.

Instance store is temporary block storage for data that changes constantly and can be recreated: buffers, caches, scratch space, temporary files, and replicas of data held durably elsewhere. It is included in the instance price at no extra charge, which is why storage optimized families with a `d` in the name are the cheapest way to get very high random IOPS. The lifetime rule is absolute. Instance store volumes attach only at launch and cannot be attached, detached or reattached afterward. Data persists across a reboot and across an operating system restart. It does not persist when the instance is stopped, hibernated, terminated or resized, and every block is cryptographically erased in those cases. It does not persist through an underlying disk failure, an AWS instance retirement, or an automatic recovery action. A design that puts a database's only copy on instance store fails on the first stop.

Amazon EBS is the answer whenever data must outlive the instance. EBS volumes persist independently, can be snapshotted to Amazon S3, can be encrypted with **AWS Key Management Service (AWS KMS)**, the managed key service, and can be detached from one instance and attached to another in the same Availability Zone. The root EBS volume has `DeleteOnTermination` set to true by default while additional volumes default to false, which is how a terminated instance can silently take its boot disk with it and leave its data volumes behind. Volume type selection, gp3 against io2 against st1 and the rest, along with snapshots, Multi-Attach and Fast Snapshot Restore, belongs to [Amazon EBS](../01-storage/ebs.md) rather than here. The decision that belongs here is instance store against EBS: choose instance store for speed on replaceable data, EBS for anything you would be unhappy to lose.

The four lifecycle actions differ in ways worth memorizing. A reboot keeps the instance on the same host, keeps its public IPv4 address, keeps instance store data, and does not start a new billing period. A stop and start moves the instance to a new host in most cases, keeps the private IPv4 and IPv6 addresses and any **Elastic IP address**, the static public IPv4 address you allocate and control, releases the public IPv4 address and assigns a new one on start, erases instance store data, preserves EBS volumes, and starts a new billing period with a one-minute minimum. Hibernation is a stop that first writes the contents of memory to the encrypted EBS root volume, so processes resume where they left off, and it is the right answer for instances that take a long time to warm a cache or build a memory footprint. Termination deletes the root volume by default, releases everything, and cannot be undone unless termination protection was enabled beforehand.

Hibernation has prerequisites that the exam turns into distractors. It must be enabled at launch and cannot be added to an existing instance. The root volume must be an EBS volume, must be encrypted, and must be large enough to hold the RAM contents, which are written to it. The supported EBS volume types are gp2, gp3, io1 and io2. Linux instances must have less than 150 GiB of RAM and Windows instances 16 GiB or less. Bare metal instances are not supported, instance store data is lost across hibernation, and instances in an EC2 Auto Scaling group or used by Amazon ECS cannot be hibernated while they are in service, because Auto Scaling marks the stopped instance unhealthy and replaces it. The one exception is a warm pool, where EC2 Auto Scaling itself puts instances into a Hibernated state, covered in the Auto Scaling unit. You are not charged for instance usage while hibernated, but you are charged during the stopping state and for the EBS storage that holds the memory image. AWS does not support keeping an instance hibernated for more than 60 days; past that you must start it, stop it and start it again.

## Instance networking, placement groups, and addressing

Every instance reaches the network through one or more **elastic network interfaces**, the virtual network cards that carry a primary private IPv4 address, optional secondary private addresses, IPv6 addresses, one Elastic IP address per private IPv4 address, one public IPv4 address, security groups, a MAC address and a source and destination check flag. Interface attributes travel with the interface, so moving a secondary interface from a failed instance to a standby instance redirects traffic to the standby without changing addresses. The primary interface cannot be detached. The number of interfaces and addresses an instance supports is fixed by its instance type, which is a quiet capacity limit on designs that assign many addresses per host. The source and destination check must be disabled on any instance acting as a NAT device, router or firewall, because by default an instance may only send and receive traffic addressed to itself.

Enhanced networking with the **Elastic Network Adapter (ENA)** is the standard data path on Nitro instances and costs nothing extra. It provides higher packets-per-second, lower and more consistent latency, and bandwidth up to the instance type's ceiling. The **Elastic Fabric Adapter (EFA)** goes further for tightly coupled work. An EFA adds a device with built-in operating system bypass through the Libfabric API and the Scalable Reliable Datagram protocol, so machine learning collectives and Message Passing Interface jobs talk to the network without going through the kernel TCP stack. EFA costs nothing extra on supported instance types, but its constraints matter: EFA traffic cannot cross Availability Zones or VPCs and is not routable, EFA is unsupported on **AWS Outposts**, the AWS-managed racks that run AWS infrastructure on premises, and most types allow one EFA per instance, or one per network card. Ordinary IP traffic on an EFA-with-ENA interface remains routable.

Placement groups tell EC2 how to place interdependent instances, cost nothing, and come in four strategies. A cluster placement group packs instances close together inside one Availability Zone for low latency and high throughput; it cannot span Availability Zones, gives 10 Gbps of single-flow bandwidth between members against 5 Gbps outside a cluster group, and limits internet and Direct Connect traffic to 5 Gbps. AWS recommends launching all of its instances in a single request with the same instance type, because adding instances later raises the chance of an insufficient capacity error, and recommends reserving capacity with an On-Demand Capacity Reservation created inside the group. Burstable instances, Mac1 and M7i-flex are not supported. A partition placement group splits instances into partitions that share no racks, with a maximum of seven partitions per Availability Zone and no limit on instances beyond your account quotas, and it exposes which instance is in which partition so that topology-aware software such as HDFS, HBase and Cassandra can place replicas intelligently; a partition group using Dedicated Instances is limited to two partitions. A spread placement group puts every instance on distinct hardware and is capped at seven running instances per Availability Zone per group, so a three-zone Region allows 21; it is not supported for Dedicated Instances. A precision time placement group places instances on hardware with direct access to high-precision time sources for microsecond clock synchronization. Capacity Reservations reserve capacity in cluster placement groups only, not in spread or partition groups, and Dedicated Hosts cannot be launched into any placement group.

Addressing has a cost consequence worth knowing. Public IPv4 addresses carry an hourly charge, and AWS charges the same rate whether the address is in use on a running instance or sitting idle and unassociated in your account. There is a narrow free tier: accounts created before 15 July 2025 get 750 hours a month of in-use public IPv4 for their first twelve months, never covering idle addresses, and newer accounts receive credits instead. On a fleet of hundreds of instances that is a real line item, and it is why current designs put instances in private subnets behind a load balancer or NAT gateway, use IPv6 where the workload allows, and release unused Elastic IP addresses. An instance loses its public IPv4 address on stop or hibernate and gets a new one on start, so anything needing a stable address wants an Elastic IP address or a DNS record pointed at a load balancer. Security groups, network access control lists, routing and VPC endpoints are taught in the networking category.

## Bootstrapping, images, instance metadata, and instance profiles

An AMI supplies the software required to boot an instance plus a block device mapping that says which volumes to attach, and it is tied to one Region, one operating system, one processor architecture and one root volume type, so an image must be copied to another Region before it can launch instances there. The standard practice is a golden image: bake the operating system, agents, runtime and application into an AMI so that launches are fast and identical, then replace instances rather than patching in place. **EC2 Image Builder**, the managed pipeline service, automates that build, test, security-scan and distribution cycle on a schedule and shares the result across accounts and Regions. Image lifecycle, cross-account and cross-organization sharing, encrypted images and KMS key sharing, deprecation and deregistration are covered in the Amazon Machine Images unit, linked below.

**User data** is the other half of bootstrapping. It is passed at launch as a shell script or cloud-init directives on Linux, or a script handled by the launch agent on Windows, is base64-encoded in transit, and is limited to 16 KB in raw form. Scripts run as root, run only during the first boot cycle by default, and can be made to run on every start with additional configuration. User data is an instance attribute rather than part of the AMI, and it can be viewed or changed only while the instance is stopped. Because it is retrievable from the metadata service by anything on the instance, user data is the wrong place for secrets; a parameter store or secrets service read through an instance role is the right place.

The **Instance Metadata Service (IMDS)** runs on every instance at `169.254.169.254` and serves instance identity, network configuration, user data and role credentials. Version 2 requires a session token obtained with a `PUT` before any `GET`, which defeats the server-side request forgery attacks that made IMDSv1 dangerous, because a tricked application making a plain `GET` through a proxy cannot mint the token. Whether IMDSv2 is required on a given instance is decided by a three-level precedence and not by a single global default. Settings on the instance at launch win, then the account-level default for that Region, then the AMI: an AMI registered with `imds-support` set to `v2.0` launches instances with `HttpTokens` set to `required` and a hop limit of 2. When nothing is set at launch, the account has no preference and the AMI carries no setting, the instance still allows IMDSv1. The durable controls are therefore the account-level default per Region, the account-level IMDSv2 enforcement setting, which blocks any launch not configured to require IMDSv2, a declarative policy in **AWS Organizations**, the multi-account governance service, and IAM condition keys that refuse launches without it. The hop limit defaults to 1 unless the AMI sets `v2.0`; containers need 2 because the request crosses an extra network hop.

```bash
aws ec2 run-instances --image-id ami-0abcdef1234567890 \
  --instance-type c7i.large \
  --iam-instance-profile Name=app-server-profile \
  --metadata-options "HttpEndpoint=enabled,HttpTokens=required,HttpPutResponseHopLimit=2"
```

Applications on an instance should never hold long-term access keys. Attach an **instance profile**, the container that carries one **AWS Identity and Access Management (IAM)** role to an instance, and the metadata service delivers rotating temporary credentials that the AWS SDKs and the **AWS Command Line Interface (AWS CLI)** find automatically. An instance profile holds exactly one role, one role can appear in many profiles, and a role can be attached or replaced on a running instance. AWS recommends replacing the instance profile rather than removing a role from one, because removal can take up to an hour to take effect. Policy changes on the role propagate to every instance using it immediately. For administrative access, prefer **Session Manager** in **AWS Systems Manager**, the operations and management service, over inbound SSH or RDP: it needs no open port, no bastion host and no key distribution, and it records sessions for audit.

## Scaling, resilience, monitoring, and cost optimization

A single instance is a single point of failure, so EC2 designs reach availability by running several instances across Availability Zones and replacing failed ones automatically. Two services own that work. Amazon EC2 Auto Scaling maintains a group of instances from a launch template, replaces instances that fail a health check, and adds or removes capacity on demand, schedule or forecast; its launch templates, scaling policies, warm pools, lifecycle hooks and instance refresh are taught in the EC2 Auto Scaling unit. Elastic Load Balancing distributes traffic across those instances, performs its own health checks, and terminates TLS; the choice between the Application, Network and Gateway load balancers is taught in the Elastic Load Balancing unit. The pairing is what makes horizontal scaling work: the load balancer is the stable endpoint, the Auto Scaling group is the elastic capacity behind it, and no instance address ever appears in a client configuration. Vertical scaling, moving to a larger instance type, remains the answer when a workload cannot be distributed, such as a single-writer database, but it needs a stop and start and has a ceiling.

EC2 runs four status checks, each every minute. A system status check monitors the AWS infrastructure the instance runs on and fails on lost network connectivity, lost power, or host software and hardware problems; the fix is AWS's, but stopping and starting an EBS-backed instance usually moves it to a healthy host immediately. An instance status check monitors the instance's own software and network configuration and fails on an exhausted memory condition, a corrupted file system, an incompatible kernel or bad startup configuration; the fix is yours. An attached EBS status check, available on Nitro instances, fails when attached volumes cannot complete input and output. Application status checks are opt-in and test an HTTP or HTTPS path on the instance. Each failure increments a metric in **Amazon CloudWatch**, the AWS monitoring and observability service, so a CloudWatch alarm on `StatusCheckFailed_System` with the recover action, or automatic instance recovery, restores an impaired instance on new hardware while keeping its instance ID, private address and EBS volumes.

CloudWatch collects EC2 metrics every five minutes by default and every minute with detailed monitoring enabled, at extra cost. Native metrics cover CPU utilization, network in and out, instance store disk activity, and the status checks. Memory utilization and guest disk space are not native metrics and need the CloudWatch agent, which is why a memory-bound instance can look healthy on a default dashboard.

Cost work on EC2 is a loop of four moves. Rightsize with **AWS Compute Optimizer**, which analyzes resource configuration and CloudWatch utilization and returns instance and Auto Scaling group recommendations plus idle resource findings. Turn off what is not needed, using schedules for development and test fleets and hibernation for instances that must return warm. Commit to the steady baseline with Savings Plans, sized from the recommendations in **AWS Cost Explorer**, the cost analysis and forecasting tool. Move the interruptible remainder to Spot. Do them in that order: committing to an oversized fleet locks in waste for three years.

## Professional depth

At organization scale the purchasing decision moves up a level. Savings Plans and Reserved Instances purchased in an Organizations management account are shared across member accounts by default, so an unused commitment in one account covers usage in another. That is efficient, but it hides accountability, and Professional scenarios often turn on turning discount sharing off for specific accounts so that a team's bill reflects its own behavior, or on centralizing purchases so that a single blended commitment covers a fleet no individual account could justify. Cost allocation tags and a consistent tagging standard are what make either model auditable, and a tag applied after the fact does not retroactively label past usage.

Capacity is the other organization-scale concern. Capacity Reservations can be shared with other accounts through **AWS Resource Access Manager (AWS RAM)**, the cross-account resource sharing service, which lets a platform team hold capacity in a shared services account and let workload accounts consume it. Placement groups can be shared the same way. A disaster recovery design that promises a Region failover with a stated recovery time objective needs Capacity Reservations in the recovery Region, because a Region-wide event is precisely when uncommitted On-Demand capacity for a large instance type may not be available; the reservation is billed at the On-Demand rate continuously, which is the price of the guarantee. Regional Reserved Instance and Savings Plan discounts apply on top of a reservation, so the combination gives both capacity and a discount.

Licensing is where Dedicated Hosts earn their complexity. **AWS License Manager**, the service that tracks and enforces license entitlements, defines a host resource group whose rules allocate and release hosts automatically, so an Auto Scaling group whose launch template names that group scales on dedicated hardware without an operator allocating hosts. Host affinity keeps an instance returning to the same physical server across stops, which some license terms require. The sharp edges: Dedicated Hosts cannot join placement groups, cannot use Capacity Reservations, and cannot switch between virtualized and `.metal` types after allocation.

Migration-scale EC2 work fails on quotas more often than on architecture. On-Demand Instance limits are expressed in vCPUs per instance family group per Region, and active unused Capacity Reservations count against them. Spread placement groups stop at seven instances per Availability Zone and partition groups at seven partitions per zone, Dedicated Hosts have a running-host quota per family per Region, and network interfaces per instance are fixed by instance type. Raise the ones that bind before the cutover, not during it.

Failure modes at scale are usually correlated. A fleet concentrated in one instance type and one Availability Zone shares a Spot pool, a rack and a power domain. Spread and partition placement groups break that correlation but cap group size, so large fleets need several groups. A cluster placement group does the opposite on purpose, trading blast radius for latency, so it belongs to a recomputable HPC job and not a stateful tier. Instance retirement and scheduled maintenance events arrive through the **AWS Health Dashboard**, which reports AWS events affecting your account, and through EventBridge, and should be automated rather than read as email.

> **Professional depth.** A Professional question often extends an Associate Spot scenario by adding a hard deadline. The Associate answer is "use Spot for the batch fleet". The Professional answer keeps a committed On-Demand baseline sized to meet the deadline in the worst case, adds Spot capacity through a `maintain` fleet with the `price-capacity-optimized` strategy across many instance types and zones, enables Capacity Rebalancing, and checkpoints intermediate state to Amazon S3 so that a reclaimed instance costs minutes of work rather than the whole run.

## Worked scenario

A genomics company runs three workloads in one Region. A customer-facing portal serves steady traffic all day. A nightly alignment pipeline processes thousands of independent samples and must finish before an 08:00 reporting deadline. A licensed commercial variant caller is sold per physical core and must run on hardware the vendor recognizes. The finance team wants the compute bill down without missing the deadline or breaking the license.

The portal runs on `m7i` instances in an Auto Scaling group across three Availability Zones behind an Application Load Balancer, with a target tracking policy on request count. Compute Optimizer shows the instances at 25 percent CPU, so the group moves down two sizes and the saved baseline is covered by an EC2 Instance Savings Plan for the `m7i` family in that Region, which preserves the freedom to change size and operating system. The pipeline runs on an EC2 Fleet of type `maintain` that mixes `c7i`, `c7a`, `c6i` and `m7i` across all three zones with the `price-capacity-optimized` allocation strategy, a small On-Demand baseline sized so the deadline is met even if every Spot pool empties, Capacity Rebalancing enabled, and each sample checkpointed to Amazon S3 so a two-minute interruption notice costs one sample rather than the run. The variant caller runs on a Dedicated Host allocated through a License Manager host resource group, with host affinity so it returns to the same server, and a Dedicated Host Reservation for the discount.

Storage follows the same logic. Reference genomes sit in S3, intermediate alignment output goes to local NVMe instance store because it is regenerated on retry, and results are written back to S3. Metadata lives in RDS rather than on a self-managed instance. Every instance carries an instance profile rather than keys, requires IMDSv2, and is reached through Session Manager with no inbound SSH port open.

When the exam asks about this scenario, the keyed answer pairs each workload with its purchasing option: a Savings Plan for the predictable portal, a diversified Spot fleet with an On-Demand baseline and checkpointing for the deadline-bound batch work, and a Dedicated Host for the per-core license.

## Exam lens

- "Lowest cost for a fault-tolerant, interruptible batch workload" maps to Spot Instances in a diversified fleet; On-Demand is the distractor that ignores interruptibility.
- "Must finish by a deadline but should be cheap" maps to an On-Demand or committed baseline plus Spot; pure Spot is the distractor that breaks the deadline requirement.
- "Steady usage and the workload may move between families or Regions" maps to a Compute Savings Plan; an EC2 Instance Savings Plan is the distractor because it locks the family and Region.
- "Steady usage of one known family in one Region at the deepest discount" maps to an EC2 Instance Savings Plan.
- "Must guarantee capacity is available in a specific Availability Zone" maps to an On-Demand Capacity Reservation, or a zonal Reserved Instance; a regional Reserved Instance and a Savings Plan reserve no capacity.
- "Bring an existing per-socket or per-core license" maps to Dedicated Hosts; Dedicated Instances give single tenancy without socket and core visibility or host affinity.
- "Reserve GPU capacity for a training run on a future date" maps to Capacity Blocks for ML, reservable up to eight weeks ahead and not cancellable.
- "Lowest network latency between tightly coupled nodes" maps to a cluster placement group with an EFA-capable instance type.
- "Reduce correlated hardware failure for a replicated data store such as Cassandra" maps to a partition placement group, with a maximum of seven partitions per Availability Zone.
- "A small number of critical instances that must not share hardware" maps to a spread placement group, capped at seven running instances per Availability Zone.
- "Resume quickly with the in-memory state intact" maps to hibernation, which needs an encrypted EBS root volume and under 150 GiB of RAM on Linux, and cannot be used on an in-service Auto Scaling group instance, only on one held in a warm pool.
- "Data must survive a stop" rules out instance store; instance store data is erased on stop, hibernate, terminate and resize.
- "Low average CPU with occasional spikes at the lowest cost" maps to a T instance; a fixed-performance M instance is the distractor that overprovisions.
- "Protect instance credentials from a server-side request forgery" maps to requiring IMDSv2, enforced at the account level per Region or through a declarative policy.
- "Applications on the instance must call AWS APIs securely" maps to an instance profile carrying an IAM role; storing access keys in user data is the distractor.
- "Memory utilization must trigger scaling" maps to the CloudWatch agent, because memory is not a native EC2 metric.
- "Recover automatically from a failed system status check" maps to a CloudWatch alarm with the recover action or automatic instance recovery; instance store data does not survive either path.
- "Identify oversized instances across many accounts" maps to Compute Optimizer; Cost Explorer shows spend but does not itself measure utilization headroom.

## Knowledge check

### 1. Sizing an in-memory analytics job (Associate)

A data science team runs a graph analytics job that loads a 480 GiB working set entirely into memory. CPU utilization during the run averages 35 percent, and the job reads its input once from Amazon S3 and writes a small result file at the end. The team wants the instance type that fits the workload without paying for resources it does not use.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Launch a compute optimized `c7i` instance sized to provide 480 GiB of memory.
- **B)** Launch a storage optimized `i7i` instance with large local NVMe volumes.
- **C)** Launch a memory optimized `r7i` instance sized for the 480 GiB working set.
- **D)** Launch a burstable `t3` instance and enable unlimited mode.

<details><summary>Answer</summary>

**Answer: C.** The workload is bound by memory, so a memory optimized family delivers the required RAM at the lowest vCPU count and therefore the lowest price. A cannot meet the requirement at any size, because the largest compute optimized instance in that family tops out at 384 GiB of memory. B optimizes for local disk throughput and IOPS, which this job does not use once the data is in memory. D provides a fraction of the needed memory in any size and is designed for low average CPU with occasional bursts, not for a sustained multi-hundred-gigabyte working set.

*Where this is covered: Instance families, naming, and sizing.*

</details>

### 2. Committing to compute spend during a migration (Associate)

A company spends a predictable amount on compute every month. Over the next year it plans to move several services from `c5` instances to `m7g` instances, move one workload from Amazon EC2 to AWS Fargate, and shift a Region. It wants the largest discount that will survive all of those changes without repurchasing.

Which solution will meet these requirements?

- **A)** Purchase a three-year Compute Savings Plan sized to the steady hourly spend.
- **B)** Purchase a three-year EC2 Instance Savings Plan for the `c5` family in the current Region.
- **C)** Purchase three-year Standard Reserved Instances for the current instance types.
- **D)** Run everything on Spot Instances with a `price-capacity-optimized` fleet.

<details><summary>Answer</summary>

**Answer: A.** A Compute Savings Plan applies regardless of instance family, size, Region, operating system or tenancy, and also covers Fargate and Lambda, so every planned change stays covered. B locks the discount to the `c5` family in one Region and would stop applying after the move to `m7g` or to another Region. C commits to a specific instance configuration and Standard Reserved Instances cannot be exchanged, only modified. D gives a discount but no commitment coverage, provides no capacity guarantee, and is not appropriate for steady production services that cannot tolerate interruption.

*Where this is covered: Purchasing options and commitment models.*

</details>

### 3. Guaranteeing capacity for a three-day sales event (Associate)

A retailer already has a Compute Savings Plan that covers its baseline spend. For a three-day sales event it must be certain that 300 additional instances of a specific type can launch in one Availability Zone. After the event the extra capacity is not needed and the company does not want a long commitment.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Purchase three-year regional Convertible Reserved Instances for 300 instances.
- **B)** Purchase one-year zonal Standard Reserved Instances for 300 instances.
- **C)** Launch a Spot Fleet with the `capacity-optimized` allocation strategy.
- **D)** Create On-Demand Capacity Reservations in that Availability Zone before the event and cancel them afterward.

<details><summary>Answer</summary>

**Answer: D.** An immediate-use Capacity Reservation has no term commitment, can be created and canceled at will, and reserves capacity in a named Availability Zone. The existing Savings Plan already covers the baseline, so the reservation secures the additional capacity while that commitment keeps discounting the steady-state usage underneath it. A reserves no capacity at all, because only zonal Reserved Instances do, and locks three years of spend. B does reserve zonal capacity but forces a one-year commitment for three days of need. C offers no capacity guarantee and EC2 can reclaim the instances during the event, which is the requirement the stem rules out.

*Where this is covered: Purchasing options and commitment models.*

</details>

### 4. Running a batch pipeline on interruptible capacity (Associate)

A media company renders video segments in a batch pipeline. Each segment takes about 20 minutes, segments are independent, and the company wants the lowest possible compute cost while losing as little work as possible when capacity is reclaimed.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Set a maximum Spot price at half the On-Demand rate for every instance type.
- **B)** Run an EC2 Fleet of type `maintain` with the `price-capacity-optimized` allocation strategy across several instance types and Availability Zones.
- **C)** Run all Spot Instances as one large instance type in a single Availability Zone to simplify operations.
- **D)** Handle the two-minute interruption notice from instance metadata or Amazon EventBridge and write completed segments to Amazon S3 as they finish.
- **E)** Purchase zonal Reserved Instances to cover the Spot capacity.

<details><summary>Answer</summary>

**Answer: B and D.** B draws from the pools with the highest capacity availability and then the lowest price among them, which AWS documents as the best choice for most Spot workloads, and a `maintain` fleet replaces reclaimed instances automatically. D turns a reclaim into the loss of one in-flight segment instead of the whole run. A increases interruptions, because AWS documents that specifying a maximum price makes instances interrupted more frequently. C concentrates the fleet in one capacity pool, which is the opposite of what reduces interruptions. E does not apply to Spot Instances, which are never covered by Reserved Instance or Savings Plan discounts.

*Where this is covered: Spot capacity, fleets, and interruption handling.*

</details>

### 5. Pausing a long-warming simulation overnight (Associate)

An engineering team runs a simulation on a Linux `m7i` instance with 64 GiB of RAM. The application takes 25 minutes to load a large dataset into memory before it becomes useful. Engineers want to pause work at the end of each day and resume the next morning with the loaded dataset still in memory, without paying for the instance overnight.

Which solution will meet these requirements?

- **A)** Stop the instance each evening and start it each morning.
- **B)** Create an AMI from the instance each evening and launch a new instance from it each morning.
- **C)** Launch the instance with hibernation enabled and an encrypted EBS root volume large enough to hold the RAM contents, then hibernate it each evening.
- **D)** Place the instance in an Auto Scaling group with a scheduled action that scales to zero overnight.

<details><summary>Answer</summary>

**Answer: C.** Hibernation writes memory contents to the encrypted EBS root volume, so processes resume where they stopped, and instance usage is not billed while the instance sits in the stopped state. The 64 GiB of RAM is under the documented 150 GiB Linux limit. A erases RAM, so the 25-minute load repeats every morning. B captures disk state, not memory, and produces the same reload. D terminates the instance on scale-in and loses memory entirely, and AWS documents that instances in an Auto Scaling group cannot be hibernated because the group marks a stopped instance unhealthy.

*Where this is covered: Instance store compared with Amazon EBS, and the instance lifecycle.*

</details>

### 6. Isolating a small set of critical servers (Associate)

A company runs six license servers in one Availability Zone. A single rack or host failure must not be able to take down more than one of them. The servers do not communicate with each other and have no latency requirement between them.

Which solution will meet these requirements?

- **A)** Launch the six instances into a spread placement group.
- **B)** Launch the six instances into a cluster placement group.
- **C)** Launch the six instances into a partition placement group with six partitions.
- **D)** Launch the six instances on Dedicated Hosts inside a spread placement group.

<details><summary>Answer</summary>

**Answer: A.** A spread placement group puts each instance on distinct underlying hardware and supports up to seven running instances per Availability Zone, which covers six exactly. B packs instances close together in one segment of the network, which increases rather than reduces correlated failure. C would work for a much larger replicated fleet, but AWS does not guarantee an even distribution of instances across partitions, so six instances in a partition group can still land two to a partition and share a rack, which is exactly the correlated failure the requirement rules out; it is the answer for topology-aware distributed stores. D is not possible, because AWS documents that Dedicated Hosts cannot be launched into placement groups.

*Where this is covered: Instance networking, placement groups, and addressing.*

</details>

### 7. Enforcing IMDSv2 across an organization (Professional)

A security team manages 200 accounts in AWS Organizations. An audit found application servers that still allow IMDSv1, and a recent incident showed that a vulnerable application could be tricked into reading instance role credentials. The team must ensure that no new instance in any account or Region can launch allowing IMDSv1, and must keep the control from being turned off by individual account administrators.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Use a declarative policy in AWS Organizations to set the account-level instance metadata default to IMDSv2 required and enable account-level IMDSv2 enforcement in every Region.
- **B)** Register every AMI with `imds-support` set to `v2.0` and rely on that alone to force IMDSv2.
- **C)** Attach a service control policy that denies `ec2:RunInstances` unless the request sets `HttpTokens` to `required`, and restrict the APIs that change metadata options and account defaults.
- **D)** Disable the instance metadata endpoint on every instance.
- **E)** Set the metadata response hop limit to 1 on every instance.

<details><summary>Answer</summary>

**Answer: A and C.** A sets the account default and turns on enforcement, which blocks any launch not configured to require IMDSv2 regardless of AMI or launch parameters, and a declarative policy applies it across accounts and Regions without a local administrator being able to change it. C adds a preventive guardrail on the launch call itself and protects the settings by restricting the modify APIs. B is the weakest level of precedence, so a launch parameter or account setting overrides it. D breaks role credentials, user data and SSH key retrieval. E limits how far a metadata response travels but does nothing about token requirements, and it breaks container workloads that need a hop limit of 2.

*Where this is covered: Bootstrapping, images, instance metadata, and instance profiles.*

</details>

### 8. Bringing a per-core license to AWS (Associate)

A company is migrating an enterprise resource planning system whose license is bound to physical processor cores and must be reported per socket for audit. The vendor requires that the software run on identifiable hardware, and the operations team must be able to stop an instance and have it return to the same physical server.

Which solution will meet these requirements?

- **A)** Launch the instances as Dedicated Instances.
- **B)** Allocate Dedicated Hosts, use host affinity, and manage allocation through an AWS License Manager host resource group.
- **C)** Launch bare metal instances into a cluster placement group.
- **D)** Create On-Demand Capacity Reservations targeted to one Availability Zone.

<details><summary>Answer</summary>

**Answer: B.** Dedicated Hosts expose the number of sockets and physical cores, support comprehensive bring-your-own-license for per-socket and per-core terms, and support host affinity so an instance returns to the same physical server. License Manager host resource groups automate allocation and release. A gives single-tenant hardware but no socket or core visibility, no host affinity, and only partial bring-your-own-license support. C gives dedicated hardware access but not per-host billing, affinity, or the socket and core reporting the audit requires. D reserves capacity and provides no tenancy, licensing or affinity control at all.

*Where this is covered: Purchasing options and commitment models.*

</details>

### 9. Guaranteeing recovery capacity in a second Region (Professional)

A financial services company runs its production workload in one Region across three accounts. A regulator requires that the company be able to bring 200 memory optimized instances online in a second Region within 30 minutes of a Region-wide failure. The company already holds a Compute Savings Plan that covers its steady spend, and it wants to avoid paying twice for the same discount.

Which solution will meet these requirements?

- **A)** Purchase three-year zonal Standard Reserved Instances in the recovery Region for 200 instances in each account.
- **B)** Launch On-Demand Instances in the recovery Region only when the failover is declared.
- **C)** Purchase a second Compute Savings Plan sized to the recovery fleet.
- **D)** Create On-Demand Capacity Reservations in the recovery Region's target Availability Zones, share them with the workload accounts using AWS Resource Access Manager, and let the existing Compute Savings Plan discount apply to the reserved capacity.

<details><summary>Answer</summary>

**Answer: D.** Capacity Reservations are the only mechanism here that holds capacity in a named Availability Zone with no term commitment, sharing them through AWS RAM lets one account hold capacity that the workload accounts consume, and AWS documents that Capacity Reservations combine with Savings Plans and regional Reserved Instances for the discount. A reserves capacity but buys a three-year commitment per account and cannot be shared the way a reservation can. B is the failure the regulator is guarding against, because a Region-wide event is exactly when uncommitted On-Demand capacity for a large instance type may be unavailable. C adds a second commitment discount but reserves no capacity at all.

*Where this is covered: Professional depth.*

</details>

### 10. Protecting data on local NVMe storage (Professional)

A company runs a self-managed NoSQL cluster on storage optimized instances with local NVMe volumes, chosen for their random IOPS. An operator stopped one node to change its instance type and the node's data was gone when it started again. The company must keep local NVMe performance for the live data path while ensuring that no single node's loss destroys data or requires a manual rebuild.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable termination protection on every node so the data cannot be lost.
- **B)** Configure the cluster's replication factor so that every shard has replicas on nodes in other Availability Zones, and let a replacement node rebuild from its peers.
- **C)** Schedule Amazon EBS snapshots of the instance store volumes.
- **D)** Move to a larger instance size so that the entire dataset fits in memory.
- **E)** Stream a periodic backup of each shard to Amazon S3 and restore from it when a replacement node joins.

<details><summary>Answer</summary>

**Answer: B and E.** B puts a durable copy of every shard on independent hardware in another Availability Zone, which is the design instance store assumes, and makes node replacement routine. E adds an off-cluster copy so that a correlated loss or a logical error is still recoverable. A does not help, because termination protection does not prevent a stop, and instance store data is cryptographically erased on stop, hibernate, terminate and instance type change alike. C is not possible: EBS snapshots apply to EBS volumes, and instance store volumes cannot be snapshotted or detached. D changes nothing about durability and loses the instance store contents during the resize that causes it.

*Where this is covered: Instance store compared with Amazon EBS, and the instance lifecycle.*

</details>

## Summary

Amazon EC2 is a series of decisions, and the exam tests them one at a time. Decide first whether you need an instance at all, because Lambda, Fargate and the managed database services remove work that EC2 leaves to you, and "least operational overhead" usually points away from an instance. If you do, pick the family from the resource the workload runs out of first, read the generation and option letters to get the processor and the attached storage or network capability, and pick the size from measured utilization rather than intuition. Pick the purchasing option from predictability and interruptibility: On-Demand to start, a Compute or EC2 Instance Savings Plan for the steady baseline, Spot in a diversified fleet for interruptible work, Capacity Reservations when capacity itself must be guaranteed, and Dedicated Hosts when a license is bound to cores or sockets. Put durable data on Amazon EBS and scratch data on instance store, knowing that instance store is erased on stop. Bootstrap from an AMI plus user data, carry permissions in an instance profile, require IMDSv2, and place instances across Availability Zones behind a load balancer with an Auto Scaling group doing the replacing.

## Related units

- [Amazon EC2 Auto Scaling](ec2-auto-scaling.md): launch templates, scaling policies, warm pools and instance refresh for the elastic capacity in front of EC2
- [Elastic Load Balancing](elastic-load-balancing.md): choosing between the Application, Network and Gateway load balancers that front an instance fleet
- [Amazon Machine Images](ami.md): image lifecycle, cross-account and cross-Region sharing, encryption and EC2 Image Builder pipelines
- [AWS Lambda](lambda.md): the event-driven alternative when work is short, spiky and stateless
- [AWS Batch](batch.md): managed job queues and compute environments for work that outgrows a function timeout
- [Amazon EBS](../01-storage/ebs.md): volume types, snapshots, encryption and Multi-Attach for the block storage attached to an instance
- [Amazon S3](../01-storage/s3.md): the durable object store for checkpoints, artifacts and instance backups
- [Amazon VPC](../04-networking/vpc.md): subnets, security groups, NAT and endpoints that decide what an instance can reach

## Sources

- [Placement groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/placement-groups.html): the general placement group rules, including that Dedicated Hosts cannot be launched into one
- [Declarative policies syntax for Amazon EC2](https://docs.aws.amazon.com/organizations/latest/userguide/declarative_policy_ec2-syntax.html): the instance metadata defaults an organization can enforce

- [Amazon EC2 instance type naming conventions](https://docs.aws.amazon.com/ec2/latest/instancetypes/instance-type-names.html): series letters, generation, option letters and size qualifiers
- [Amazon EC2 instance types](https://docs.aws.amazon.com/ec2/latest/instancetypes/instance-types.html): current families by category, fixed compared with burstable, and Flex instance behavior
- [Instances built on the AWS Nitro System](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-nitro-instances.html): Nitro components, bare metal boot time and per-version network capability
- [Unlimited mode for burstable performance instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-performance-instances-unlimited-mode.html): which T generations default to unlimited and when surplus credits are charged
- [Savings Plans types](https://docs.aws.amazon.com/savingsplans/latest/userguide/plan-types.html): the four plan types, their coverage and the stated discount ceilings
- [Reserved Instances for Amazon EC2 overview](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-reserved-instances.html): the recommendation to prefer Savings Plans, offering classes and payment options
- [Regional and zonal Reserved Instances (scope)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/reserved-instances-scope.html): which scope reserves capacity and the conditions on instance size flexibility
- [Spot Instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html): Spot pricing behavior, capacity pools, request types and the Savings Plan exclusion
- [Spot Instance interruption notices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html): the two-minute notice, the EventBridge event and the metadata path
- [Behavior of Spot Instance interruptions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/interruption-behavior.html): terminate, stop and hibernate behaviors and their request-type requirements
- [Use allocation strategies to determine how EC2 Fleet or Spot Fleet fulfills capacity](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-fleet-allocation-strategy.html): every Spot and On-Demand allocation strategy and the AWS recommendation
- [Reserve compute capacity with EC2 On-Demand Capacity Reservations](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-reservations.html): billing, matching attributes, the comparison with Reserved Instances and Savings Plans, and the limitations
- [Capacity Blocks for ML](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html): the eight-week horizon, the 64 and 256 instance limits and the no-cancellation rule
- [Amazon EC2 Dedicated Hosts](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/dedicated-hosts-overview.html): the Dedicated Host compared with Dedicated Instance table and host restrictions
- [Placement strategies for your placement groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/placement-strategies.html): seven partitions per Availability Zone, seven spread instances per zone, and per-strategy limits
- [Data persistence for Amazon EC2 instance store volumes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-store-lifetime.html): the event-by-event persistence table and instance store pricing
- [Amazon EC2 instance state changes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html): per-second billing, the one-minute minimum, and the reboot, stop, hibernate and terminate comparison
- [Prerequisites for EC2 instance hibernation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/hibernating-prerequisites.html): RAM ceilings, root volume encryption and supported EBS volume types
- [How Amazon EC2 instance hibernation works](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-hibernate-overview.html): the 60-day limit and the Auto Scaling and bare metal exclusions
- [Elastic network interfaces](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html): interface attributes, primary and secondary interfaces, and network cards
- [Elastic Fabric Adapter for AI/ML and HPC workloads](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html): operating system bypass, interface types, limitations and pricing
- [Configure the Instance Metadata Service options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html): the order of precedence and account-level enforcement that decide whether IMDSv2 is required
- [Run commands when you launch an EC2 instance with user data input](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html): the 16 KB limit and the first-boot-only default
- [IAM roles for Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html): instance profiles, one role per profile and the replacement recommendation
- [Status checks for Amazon EC2 instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-system-instance-status-check.html): the four status check types and what each detects
- [Amazon VPC pricing](https://aws.amazon.com/vpc/pricing/): the public IPv4 address charge for in-use and idle addresses
