# Amazon EKS

**Where it sits on the exams.** **Amazon Elastic Kubernetes Service (Amazon EKS)** runs a managed Kubernetes control plane and wires Kubernetes into AWS identity, networking, storage and load balancing, leaving you to decide what compute runs the containers. Kubernetes is the open source container orchestrator behind it: a *pod* is one or more containers scheduled and addressed as a unit, a *node* is the machine a pod runs on, and the *control plane* is the API server and datastore that decide which pod runs where. EKS appears in SAA-C03 tasks 2.1 and 3.2 behind "the orchestration of containers, for example Amazon ECS, Amazon EKS", in SAP-C02 tasks 4.3 and 4.4 behind "selecting the appropriate container hosting platform", and in SAP-C02 task 1.1 under "AWS container services". The rule of thumb is narrow: choose EKS when the requirement names Kubernetes, an existing Helm chart or operator, or one control plane the team must also run outside AWS. Otherwise **Amazon Elastic Container Service (Amazon ECS)**, the AWS-native container orchestrator, is the lower-overhead answer, and [Amazon ECS and Amazon ECR](ecs-and-ecr.md) owns that comparison.

## What EKS manages, and what stays yours

A cluster is the control plane. EKS runs the Kubernetes API server and the etcd persistence layer across multiple Availability Zones, replaces unhealthy control plane nodes, patches them and scales them with load. You never see those instances: on the shared responsibility model the control plane is AWS's, and everything from the node operating system upward is yours unless you hand it back. The cluster is certified Kubernetes conformant, so standard manifests, Helm charts and operators run unchanged.

That control plane is the one charge that exists whether or not anything runs on it: a flat fee per cluster per hour, currently 0.10 USD while the cluster's Kubernetes version is in standard support, plus whatever the data plane costs. Managed node groups add nothing themselves; you pay **Amazon EC2**, the service that rents virtual servers you administer, for the instances and **Amazon EBS**, the block storage service, for their volumes. Because the fee is per cluster, 50 small clusters cost 50 times the control plane of one, which is the arithmetic behind most multi-tenancy questions.

Versions age on a published schedule and the exam likes its edges. A minor version gets 14 months of standard support from its EKS release, then 12 months of extended support, 26 in total. Extended support is on by default and costs 0.60 USD per cluster-hour in place of 0.10. At the end of it EKS automatically upgrades the control plane, and that is the trap: the upgrade covers the control plane only, leaving nodes and add-ons on the old version for you to update. Disable extended support and that automatic upgrade happens at 14 months instead. A stem saying "we cannot upgrade this quarter but must stay supported" is asking you to accept the surcharge, not to build anything.

Two more control plane settings decide security questions. The Kubernetes API endpoint is public by default; you can enable the private endpoint, restrict the public one to a list of CIDR blocks, or turn public access off so the API is reachable only from the **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network your resources run in, and networks connected to it. And since Kubernetes 1.28, EKS envelope-encrypts all Kubernetes API data before it reaches etcd using **AWS Key Management Service (AWS KMS)**, the managed key service, with an AWS owned key by default and a customer managed key when compliance demands one you control.

Control plane logging is how you see inside the part you do not run. Five log types, `api`, `audit`, `authenticator`, `controllerManager` and `scheduler`, are enabled individually, are all off by default, and stream to **Amazon CloudWatch Logs**, the log storage and query service within **Amazon CloudWatch**, the AWS monitoring service, at standard rates. The `audit` log answers "which principal deleted that namespace"; `authenticator`, unique to EKS, records the component mapping AWS identities to Kubernetes ones, so a failed `kubectl` sign-in shows up there.

## Choosing the compute: node groups, Fargate and Auto Mode

Everything above the control plane is a choice about who owns the servers. EKS schedules pods onto any mix of four things: managed node groups, self-managed nodes, **AWS Fargate**, the serverless container engine where no instance exists in your account, and **Amazon EKS Auto Mode**, in which AWS also runs the data plane. Read the table by finding the row whose selection wording matches the stem, then check the other columns against the remaining constraints.

| Option | Who patches the node | How you pay | What you can tune | Wording that selects it |
|---|---|---|---|---|
| EKS managed node groups | AWS builds the patched EKS optimized Amazon Machine Image (AMI); you choose when to roll it out, and EKS drains each node respecting pod disruption budgets | EC2 and EBS charges only | Instance types, On-Demand or Spot, labels and taints, a launch template with a custom AMI, bootstrap arguments, SSH access | "AWS should handle node lifecycle but we still need the instances", ""GPU", "Windows containers", "we own Reserved Instances" |
| Self-managed nodes | You do: build the AMI, roll the Auto Scaling group, drain the nodes | EC2 and EBS charges only | Everything, including a custom Container Network Interface (CNI) plugin and placements node groups cannot reach, such as **AWS Outposts**, the rack of AWS hardware in your data center | "a golden AMI pipeline we must keep", "a third-party CNI plugin", "nodes on Outposts" |
| AWS Fargate | AWS does. No node exists in your account, and EKS patches the pod platform by recycling pods | Per pod, by the vCPU and memory combination provisioned, per second | The pod's CPU and memory request, up to 16 vCPU and 120 GB, ephemeral storage up to 175 GiB, and which namespaces and labels a Fargate profile matches | "each pod must be isolated from every other", "no servers at all", "a short-lived job that costs nothing when idle" |
| EKS Auto Mode | AWS does, on immutable Bottlerocket-based managed instances that allow no interactive login and have a 21-day maximum node lifetime | EC2 charges plus a management fee per instance-hour that varies with instance type | NodePools and NodeClasses set instance families, Spot and ephemeral storage. Auto Mode also takes over compute autoscaling, pod networking and network policy, load balancing and block storage as built-in capabilities | "least operational overhead" for Kubernetes, "we do not want to operate the autoscaler, the CNI and the Container Storage Interface (CSI) drivers" |

A managed node group is an **Amazon EC2 Auto Scaling** group, the service that keeps a fleet of instances at a desired count, that EKS creates and tags in your account. "Managed" buys lifecycle: create, update and delete in one API call, draining on update and termination, the right Kubernetes labels and autoscaler tags, and node auto repair. It does not buy patching on your behalf: AWS publishes a fixed AMI and notifies you, and deploying it is your action. Capacity type is On-Demand or Spot per group, never mixed, so the usual shape is one On-Demand group for stateful work and one Spot group whose labels fault-tolerant deployments select. Quotas bind at 30 node groups per cluster and 450 nodes per group.

Fargate on EKS is selected by a Fargate profile, a cluster-level object naming namespaces and optional pod labels; a pod matching one runs on Fargate, a pod matching none stays `Pending`. The isolation is real, one pod per virtual machine with its own kernel. The restrictions are where questions live: no DaemonSets, which run one pod on every node, no privileged containers, no GPU, no `HostPort` or `HostNetwork`, no Fargate Spot, private subnets only, no EBS volumes (EFS works, static provisioning only), and no instance metadata service, so pods needing AWS permissions must use **IAM roles for service accounts (IRSA)**, the OpenID Connect mechanism taught below. Ten profiles per cluster is the default quota. AWS now states that Fargate remains an option but Auto Mode is the recommended approach going forward, because Auto Mode is fully conformant, supports service meshes, GPUs and every EC2 purchase option, and reproduces one-pod-per-instance isolation with ordinary Kubernetes scheduling.

Auto Mode is the answer when a Kubernetes question uses the exam's "least operational overhead" wording. It provisions nodes with Karpenter's logic, consolidates workloads onto fewer instances, handles Spot interruption and instance health events, and cycles every node within 21 days so patching happens by replacement. It also ships pod IP address management, network policy, DNS, GPU plugins, block storage and load balancer integration as managed capabilities, so there are no CNI, CSI or load balancer controller versions to track. The cost is control: no SSH, no custom AMI or CNI, no per-pod security groups, no Windows containers, plus a management fee on top of EC2.

## Pod networking and the Amazon VPC CNI

The most consequential design fact about EKS is that pods get real VPC addresses. The **Amazon VPC CNI plugin for Kubernetes**, the default networking plugin on every cluster, attaches elastic network interfaces (ENIs) to each node and hands their secondary IP addresses out to pods. A pod is therefore a first-class citizen of the subnet: VPC route tables, network ACLs and VPC Flow Logs see it, and anything that can route to the subnet reaches it directly with no overlay and no address translation. That is good for latency, on-premises integration and troubleshooting, and it is why EKS subnet planning differs from ECS subnet planning.

The consequence is address consumption, and the exam splits it into two problems with different answers. The first is *pod density per node*: each instance type supports a fixed number of ENIs and addresses per ENI, so a node can exhaust addresses while CPU and memory sit idle. The fix is prefix delegation, set with `ENABLE_PREFIX_DELEGATION` on the CNI add-on, which assigns a /28 prefix of 16 addresses to each ENI slot instead of a single address. The same ENI count now carries roughly 16 times the addresses, pods start faster because the plugin holds a warm pool of prefixes rather than calling EC2 per address, and the ceiling becomes the kubelet's `max-pods` value, 110 by default. Prefix delegation needs contiguous /28 blocks, so a fragmented subnet defeats it. The second problem is *subnet or VPC exhaustion*, where the VPC has run out of routable space, and prefix delegation makes that worse because it consumes addresses in larger blocks. The answers there are to associate an additional CIDR block with the VPC, typically non-routable space from 100.64.0.0/10, and use CNI custom networking so that secondary ENIs and therefore all pods come from that alternate subnet while nodes keep routable addresses, or to create the cluster with the IPv6 address family, which AWS recommends when IPv4 exhaustion is the only reason for custom networking.

Two further behaviors decide questions. Security groups for pods give an individual pod its own security group on a branch interface, which satisfies "this pod must reach the database and no other pod may", but works only on Linux nodes on supported Nitro instance types, and not on Auto Mode. And the cluster needs a path to AWS APIs: nodes in private subnets pull images from **Amazon Elastic Container Registry (Amazon ECR)**, the managed container image registry, so either a NAT gateway or interface endpoints built on **AWS PrivateLink**, the service that projects an AWS service endpoint into your subnets, must exist. Subnets must span at least two Availability Zones.

## Getting traffic to pods with the AWS Load Balancer Controller

Kubernetes describes load balancing abstractly and something must turn the abstraction into AWS resources. The **AWS Load Balancer Controller** is that something: a controller you install on the cluster that watches Kubernetes objects and creates the matching **Elastic Load Balancing (ELB)** resources, the managed load balancing family. The mapping is short enough to memorize and the exam tests it directly. A Kubernetes Service of `type: LoadBalancer` becomes a Network Load Balancer (NLB), the layer 4 load balancer with a static address per Availability Zone. A Kubernetes Ingress becomes an Application Load Balancer (ALB), the layer 7 load balancer that routes on host and path, and several Ingress objects can share one ALB through a group annotation. From controller version 2.14.0 a Kubernetes Gateway object also becomes an ALB. Certificates from **AWS Certificate Manager (ACM)**, the service that issues and renews TLS certificates, association with **AWS WAF**, the managed web application firewall, health checks and access logs are all set with annotations on the Kubernetes object.

Target type is the detail that catches people. With the `ip` target type the load balancer sends traffic straight to pod addresses, which is possible only because the VPC CNI gave pods real addresses, and is mandatory on Fargate. With the `instance` target type it sends traffic to a node port and kube-proxy forwards it, adding a hop. Subnets must carry discovery tags, `kubernetes.io/role/elb` for public and `kubernetes.io/role/internal-elb` for private, and an internet-facing load balancer needs a public subnet with spare addresses even when every node is private. One legacy behavior matters: without this controller, Kubernetes falls back to the in-tree AWS cloud provider, which creates Classic Load Balancers, so a cluster that keeps producing them needs the controller installed. Listeners, target groups and health checks belong to [Elastic Load Balancing](../02-compute/elastic-load-balancing.md).

## Cluster access and pod credentials

EKS has two identity questions that sound alike and have different answers. The first is which AWS principals may call the Kubernetes API. Kubernetes knows nothing about IAM roles, so EKS runs an authenticator on the control plane that maps **AWS Identity and Access Management (IAM)**, the service that controls who may call which AWS API, principals onto Kubernetes identities. The original mechanism was the `aws-auth` ConfigMap, a YAML object inside the cluster listing role and user ARNs against Kubernetes groups. It is awkward for the reasons the exam likes: you need cluster access to grant cluster access, a bad edit locks everyone out, and the change is invisible to **AWS CloudTrail**, the API audit log service.

**EKS access entries** replace it. An access entry is an EKS API object binding an IAM principal to Kubernetes permissions, created with the same CLI, **AWS CloudFormation**, the infrastructure as code service, or console you used to build the cluster, so access is auditable, recoverable without cluster access, and expressible in the same template. Permissions attach two ways: an AWS managed access policy, `AmazonEKSClusterAdminPolicy`, `AmazonEKSAdminPolicy`, `AmazonEKSEditPolicy` or `AmazonEKSViewPolicy`, optionally scoped to namespaces, or a Kubernetes group you bind with your own role-based access control (RBAC) rules. A cluster's authentication mode is `CONFIG_MAP`, `API_AND_CONFIG_MAP` or `API`, and the direction is one-way: you can move toward `API` but never back. Be precise about defaults, because they depend on how the cluster was made: the console defaults to `API_AND_CONFIG_MAP`, while the EKS API, an SDK or CloudFormation defaults to `CONFIG_MAP`. Access entries are the recommended mechanism and are required for Auto Mode and hybrid nodes, but they are not switched on for every new cluster. The creating principal also gets a cluster admin entry by default, which a hardened design revokes.

The second question is what a pod may call in AWS, whether that is **Amazon S3**, the object storage service, or **Amazon DynamoDB**, the managed NoSQL key-value database, and here the AWS recommendation has moved. IRSA was the long-standing answer: EKS publishes an OpenID Connect (OIDC) issuer for the cluster, you register it as an IAM OIDC identity provider, annotate a Kubernetes service account with a role ARN, and the pod's token is exchanged for credentials through `sts:AssumeRoleWithWebIdentity`. It works everywhere, but every cluster needs its own OIDC provider against a default IAM limit of 100 per account, and every role's trust policy must name each cluster using it, against a size limit that in practice allows a handful of clusters per role. **EKS Pod Identity** removes both. You install the Pod Identity Agent add-on once, trust the single service principal `pods.eks.amazonaws.com` in the role, then associate the role with a namespace and service account through the EKS API: no OIDC provider, no per-cluster trust policy edit, and credentials carrying session tags for cluster, namespace and service account so one role serves many service accounts through attribute-based access control. AWS recommends Pod Identity wherever possible, and a cluster holds up to 5,000 associations. IRSA still wins in two places: Fargate pods, because the agent is a DaemonSet and Fargate runs none, and anything outside EKS such as EKS Anywhere, self-managed Kubernetes on EC2 or Red Hat OpenShift Service on AWS. Neither is the node IAM role, which every node assumes to join the cluster and pull images, and which a pod reaches through the instance metadata service unless you block it. Policy evaluation and role design belong to [AWS IAM](../07-security/iam.md).

## Add-ons, persistent storage and cluster autoscaling

Everything the cluster needs that is not the control plane arrives as an add-on, and EKS add-ons are the managed form: AWS curates, validates and patches a version, and you install and upgrade it through the EKS API. The core four are the VPC CNI, `kube-proxy`, CoreDNS, and the Pod Identity Agent. Storage arrives the same way. The Amazon EBS CSI driver provisions Amazon EBS volumes for persistent volume claims, giving a pod a single-writer volume pinned to one Availability Zone, so a stateful set spread across zones needs one node group per zone or it will schedule a pod where its volume is not. The Amazon EFS CSI driver mounts **Amazon EFS**, the managed NFS file system, which is multi-AZ and read-write from many pods at once, and is the answer whenever several pods must share the same files. Fargate cannot mount EBS at all and supports EFS only with static provisioning; Auto Mode needs neither driver, since block storage is built in. Monitoring is add-on shaped too: CloudWatch Container Insights, **Amazon Managed Service for Prometheus**, the managed Prometheus-compatible metrics store, and the OpenTelemetry operator all install this way.

Scaling has two independent layers and conflating them is a standard distractor. Pod scaling is Kubernetes' own job: the Horizontal Pod Autoscaler changes replica counts against CPU, memory or custom metrics, and the Vertical Pod Autoscaler resizes requests. Node scaling adds and removes machines, and EKS supports two tools. The Cluster Autoscaler works through EC2 Auto Scaling groups, so it grows a node group you already defined and is bounded by the instance types in it. **Karpenter** provisions instances directly from a NodePool's constraints, picking types and sizes that fit the pending pods, launching in under a minute, then consolidating: it moves workloads that could run on cheaper or fewer nodes and terminates what is left empty. "Reduce cluster cost without capacity planning" is Karpenter wording; "we already manage node groups and only need them to grow" is Cluster Autoscaler wording. Karpenter is open source software you install and operate, which is the overhead Auto Mode removes by running the same logic as a managed capability.

## Kubernetes outside the Region: EKS Anywhere, EKS Distro and Hybrid Nodes

Three products carry the EKS name off the Region, they are distinct, and the SAA-C03 in-scope list names the first two. **Amazon EKS Distro** is the software: the same open source Kubernetes components AWS builds, tests and patches for EKS, published for you to install on your own hardware, virtual machines or another cloud. It is a distribution, not a service, and no AWS control plane is involved. **Amazon EKS Anywhere** is the deployment option built on EKS Distro: it creates and operates complete clusters on your own infrastructure, control plane included, with AWS support, for data residency requirements or sites that must keep running when the link to AWS is down. **Amazon EKS Hybrid Nodes** is the opposite arrangement: the control plane stays in the Region as an ordinary EKS cluster, and your on-premises machines join it as nodes over **AWS Direct Connect**, the dedicated private connection to AWS, or **AWS Site-to-Site VPN**, the encrypted tunnel over the internet. You keep one cluster and one set of add-ons, access entries and Pod Identity associations across both locations, billed per vCPU-hour. The VPC CNI does not run there, so pod networking uses Cilium, which AWS names as the supported CNI, and the EBS and EFS CSI drivers are unsupported. One control plane spanning a data center and a Region is Hybrid Nodes; clusters that must survive disconnection are EKS Anywhere.

## Professional depth

At organization scale the first Professional decision is how many clusters to run. The per-cluster hourly fee, upgrade work that multiplies with cluster count, and the IAM OIDC provider limit of 100 per account push toward fewer, larger clusters with namespaces, RBAC and network policies separating tenants. Pulling the other way are blast radius and the difficulty of giving one team cluster-admin without giving it every team's workloads. The usual answer in a multi-account landing zone is one cluster per environment per account, with **AWS Organizations**, the service that groups accounts under central policy, providing the boundary, access entries granting a role from a central identity account into each cluster, and Pod Identity making one workload role reusable. The EKS Dashboard gives the cross-account inventory, including which clusters are drifting toward extended support charges.

Version lifecycle is fleet-wide work at this level: 40 clusters need an upgrade cadence, not an upgrade project. Order matters: control plane first, then the add-ons pinned to the Kubernetes version, then the nodes. Cluster insights flags API deprecations that would break the next version, and an in-place upgrade can be rolled back within 7 days. The failure that costs money is silent: extended support is on by default, so a forgotten cluster bills at six times the standard rate without anyone choosing it.

Networking is where migration-scale designs break. A VPC sized for instances is rarely sized for pods, and the correction is expensive later because a cluster's Availability Zones are fixed at creation and subnets can be added only in those zones. Plan the pod address space first, reach for a secondary CIDR with custom networking or an IPv6 cluster before routable space is gone, and keep the cluster's service CIDR clear of any VPC it reaches through peering or a transit gateway, because service addresses win locally and the failure looks like an application bug. For very large clusters, **Amazon EKS Provisioned Control Plane** pins a control plane scaling tier so API server capacity is pre-allocated rather than scaled on demand, billed hourly on top of the cluster fee.

Two failure modes recur and neither shows up on a CPU graph. Pods stuck in `Pending` while nodes have free capacity is almost always address exhaustion, either ENI slots on the node, which prefix delegation fixes, or the subnet, which it does not. And a cluster whose `aws-auth` ConfigMap was edited badly locks out every human at once; the recovery path is access entries through the EKS API, which is the strongest argument for switching authentication mode before you need it. For zonal impairment, EKS supports **Amazon Application Recovery Controller (ARC)** zonal shift, which moves traffic away from one Availability Zone, and under Auto Mode also stops provisioning nodes there.

## Worked scenario

A media company runs a recommendation platform as 30 Kubernetes microservices with a large estate of Helm charts, the package format for Kubernetes applications, and two operators it wrote itself, controllers that automate an application's lifecycle, so the orchestrator is not in question. Traffic triples at evening peak, three services need GPUs for inference, a compliance rule says the model pod must not share a kernel with any other workload, and the platform team is four people who do not want to run cluster infrastructure. A nightly job must read a media library in the company's data center that cannot move.

The design is one EKS cluster per environment with Auto Mode enabled, which removes the CNI, CSI drivers, load balancer controller and autoscaler from the team's workload and cycles nodes every 21 days for patching. A custom NodePool selects GPU instance families for inference and another selects Spot for the batch tier; the model pod gets kernel isolation from a topology spread constraint putting one pod on each instance, not from Fargate, which cannot run GPUs. The VPC carries a secondary 100.64.0.0/16 CIDR so pod addresses never compete with routable space. Public traffic enters through an Ingress that the built-in load balancing capability turns into an ALB with `ip` targets.

Identity splits cleanly. Human access uses access entries, `AmazonEKSViewPolicy` scoped to the application namespaces for the on-call rotation and `AmazonEKSAdminPolicy` for the platform team, with the cluster creator's admin entry revoked after bootstrap. Workload access uses EKS Pod Identity, so the same roles are reused in staging with no trust policy edits. Model artifacts land on EFS because several inference pods read the same files, while the feature store uses EBS volumes with one node pool per Availability Zone. The `audit` and `authenticator` logs go to CloudWatch Logs. The nightly data center job runs on EKS Hybrid Nodes attached to the same cluster over Direct Connect, so the team keeps one control plane, one set of manifests and one identity model.

The exam asks this two ways. The Associate version asks how to run an existing Kubernetes estate with the least operational overhead while keeping GPU support, and the keyed answer is EKS with Auto Mode, not Fargate, which supports no GPUs, and not ECS, because the charts and operators are Kubernetes-specific. The Professional version adds the on-premises job, roles reused across two clusters and the pod address pressure, and the keyed answer is Hybrid Nodes for the job, Pod Identity rather than IRSA for the roles, and a secondary VPC CIDR, with NodeClass subnet selectors placing Auto Mode nodes in those subnets, since Auto Mode does not support custom networking rather than prefix delegation for the addresses.

## Exam lens

- "Existing Helm charts" or "a Kubernetes operator" maps to Amazon EKS; ECS is the distractor when no Kubernetes requirement is stated.
- "Run Kubernetes with the least operational overhead" maps to EKS Auto Mode; managed node groups are the distractor because they still leave AMI rollouts, add-ons and the autoscaler to you.
- "Each pod must have its own kernel" maps to Fargate, unless the stem also needs GPUs, DaemonSets, privileged containers or EBS volumes, any of which rules it out.
- "GPU" maps to managed node groups or Auto Mode, never Fargate; "Windows containers" or "custom AMI" maps to managed node groups specifically; a custom CNI plugin or an Outposts placement maps to self-managed nodes.
- "Who deleted the namespace" maps to the `audit` control plane log and a failed `kubectl` sign-in to the `authenticator` log; both are off by default.
- "Pods are Pending although nodes have spare CPU and memory" maps to address exhaustion: prefix delegation when the node is out of ENI slots, a secondary VPC CIDR with custom networking or an IPv6 cluster when the subnet is out. Prefix delegation is the distractor for a VPC-wide shortage.
- "This pod alone may reach the database" maps to security groups for pods, unavailable on Auto Mode.
- "A static Layer 4 address" maps to a Service of type LoadBalancer becoming an NLB and "route on host or path" to an Ingress becoming an ALB, both through the AWS Load Balancer Controller, whose absence is why Classic Load Balancers appear.
- "Grant a team kubectl access without editing anything inside the cluster" maps to EKS access entries with an AWS managed access policy; the `aws-auth` ConfigMap is the distractor CloudTrail cannot audit.
- "One IAM role for a workload running in twelve clusters" maps to EKS Pod Identity; IRSA is the distractor because each cluster needs its own OIDC provider and a trust policy edit.
- "A Fargate pod needs AWS permissions" maps to IAM roles for service accounts, because the Pod Identity Agent is a DaemonSet and Fargate runs none.
- "Several pods must read and write the same files" maps to the EFS CSI driver; the EBS CSI driver is the distractor because an EBS volume attaches to one node in one Availability Zone.
- "Right-size nodes to pending pods and consolidate onto fewer instances" maps to Karpenter; the Cluster Autoscaler only grows and shrinks node groups you defined.
- "We cannot upgrade Kubernetes this year but must stay supported" maps to accepting extended support at the higher hourly rate, with the control plane auto-upgraded at 26 months and nodes left behind.
- "One control plane covering the Region and our data center" maps to EKS Hybrid Nodes; "clusters that keep working when the AWS link is down" maps to EKS Anywhere, whose Kubernetes build is EKS Distro.

## Knowledge check

### 1. Kubernetes manifests with nobody to run the servers (Associate)

A retailer has spent two years building 40 microservices deployed with Helm charts and two custom Kubernetes operators. The company is moving to AWS and wants to keep the manifests unchanged. The platform team is small and does not want to patch operating systems, manage a cluster autoscaler, or maintain networking and storage drivers.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Convert the Helm charts to Amazon ECS task definitions and run the services on ECS with Fargate.
- **B)** Create an Amazon EKS cluster with self-managed node groups and install Karpenter, the Amazon VPC CNI, and the EBS CSI driver.
- **C)** Create an Amazon EKS cluster with EKS Auto Mode enabled and deploy the existing Helm charts.
- **D)** Run Kubernetes on Amazon EC2 instances using Amazon EKS Distro and manage the control plane in-house.

<details><summary>Answer</summary>

**Answer: C.** Auto Mode keeps a fully conformant Kubernetes API, so the Helm charts and operators run unchanged, while AWS provisions and patches nodes, runs compute autoscaling, and ships pod networking, load balancing and block storage as managed capabilities. A discards the Kubernetes API entirely, so the operators have nothing to run against and the charts must be rewritten. B keeps every task the requirement asked to remove: AMI patching, node draining, and add-on version management. D is the most work of all, since EKS Distro is a Kubernetes distribution you install and operate yourself, control plane included.

*Where this is covered: Choosing the compute: node groups, Fargate and Auto Mode.*

</details>

### 2. Pods stuck pending on idle nodes (Associate)

An EKS cluster runs managed node groups of `m5.large` instances. During a scale-out, pods stay in `Pending` even though CloudWatch shows the nodes at under 30 percent CPU and memory. The VPC has a single /16 CIDR block with more than 40,000 free addresses, and the node subnets are large and lightly used. The company wants more pods per node without adding instances.

Which solution will meet these requirements?

- **A)** Associate a secondary CIDR block with the VPC and enable CNI custom networking.
- **B)** Enable prefix delegation on the Amazon VPC CNI add-on and raise the kubelet `max-pods` value.
- **C)** Increase the desired capacity of the managed node group.
- **D)** Switch the node group to instances with more vCPUs and memory.

<details><summary>Answer</summary>

**Answer: B.** The symptom is address exhaustion at the node, not in the VPC: each instance type supports a fixed number of network interfaces and addresses per interface, and that ceiling is reached long before CPU is. Prefix delegation assigns /28 prefixes of 16 addresses to each interface slot, so the same node carries far more pods. A solves VPC-wide exhaustion, which the stem rules out by stating there are 40,000 free addresses. C adds instances, which the stem explicitly does not want and which wastes the idle capacity already there. D buys CPU and memory that are not the constraint, and only incidentally raises the interface limit.

*Where this is covered: Pod networking and the Amazon VPC CNI.*

</details>

### 3. Access for a new on-call rotation (Associate)

A company runs an EKS cluster created through AWS CloudFormation. A new on-call rotation of 12 engineers, who assume a shared IAM role, needs read-only `kubectl` access to two application namespaces. Security requires that every grant appear in AWS CloudTrail and that a mistaken change never lock administrators out of the cluster.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Set the cluster authentication mode to `API_AND_CONFIG_MAP`.
- **B)** Add the role ARN to the `aws-auth` ConfigMap and map it to a Kubernetes group.
- **C)** Create an access entry for the role and associate `AmazonEKSViewPolicy` scoped to the two namespaces.
- **D)** Create an IAM policy granting `eks:DescribeCluster` and attach it to the role.
- **E)** Create an IAM OIDC identity provider for the cluster and annotate a service account with the role ARN.

<details><summary>Answer</summary>

**Answer: A and C.** A cluster created through CloudFormation defaults to `CONFIG_MAP`, so the authentication mode must first be moved to `API_AND_CONFIG_MAP` before access entries exist, and an access entry with a scoped `AmazonEKSViewPolicy` then grants exactly read-only access to the two namespaces through the EKS API, which CloudTrail records and which can be repaired without cluster access. B is the mechanism the requirements rule out: ConfigMap edits are invisible to CloudTrail and a bad edit is the classic lockout. D grants an AWS API permission that lets the role fetch cluster details but confers no Kubernetes permissions at all. E describes IAM roles for service accounts, which gives pods AWS permissions and has nothing to do with human `kubectl` access.

*Where this is covered: Cluster access and pod credentials.*

</details>

### 4. Shared model files across inference pods (Associate)

Twelve inference pods spread across three Availability Zones must all read the same 200 GB of model files, and a training job must be able to write new versions into the same location while the inference pods are running.

Which solution will meet these requirements?

- **A)** Provision an Amazon EBS volume with the EBS CSI driver and mount it in every pod.
- **B)** Copy the files into each container image and rebuild the image for every model version.
- **C)** Run the inference pods on AWS Fargate and attach an EBS volume to each pod.
- **D)** Provision an Amazon EFS file system with the EFS CSI driver and mount it in every pod.

<details><summary>Answer</summary>

**Answer: D.** EFS is a multi-AZ, elastic file system that many pods can mount read-write at the same time, which is exactly the shared-files requirement, and the EFS CSI driver is available as an EKS add-on. A fails twice: an EBS volume attaches to one node and lives in one Availability Zone, so pods in the other two zones cannot mount it. B makes every model update a rebuild and redeploy of 12 pods and still gives the training job nowhere to write. C is invalid on its face, because Fargate pods cannot mount EBS volumes at all.

*Where this is covered: Add-ons, persistent storage and cluster autoscaling.*

</details>

### 5. Ingress that keeps creating the wrong load balancer (Associate)

A team deploys a Kubernetes Service of `type: LoadBalancer` on a new EKS cluster and finds that a Classic Load Balancer is created. They need a Layer 7 load balancer that routes `/api` and `/static` to different services and terminates TLS with a certificate from AWS Certificate Manager.

Which solution will meet these requirements?

- **A)** Install the AWS Load Balancer Controller and define a Kubernetes Ingress with routing and certificate annotations.
- **B)** Keep the Service of type LoadBalancer and add path rules to it with annotations.
- **C)** Create an Application Load Balancer manually and register each node's IP address as a target.
- **D)** Install the AWS Load Balancer Controller and keep the Service of type LoadBalancer.

<details><summary>Answer</summary>

**Answer: A.** The Classic Load Balancer comes from the legacy in-tree cloud provider that Kubernetes falls back to when no controller is installed. Installing the AWS Load Balancer Controller and expressing the requirement as an Ingress produces an ALB, which is the only option here that routes on path and terminates TLS. B is impossible: a Kubernetes Service is a Layer 4 object with no concept of paths. C abandons the controller, so every new pod address has to be registered by hand and the target list goes stale on the first deployment. D produces an NLB, a Layer 4 load balancer that cannot route on path.

*Where this is covered: Getting traffic to pods with the AWS Load Balancer Controller.*

</details>

### 6. One workload role for fourteen clusters (Professional)

A company runs 14 EKS clusters across four AWS accounts. A shared data-processing workload runs in every cluster and needs the same Amazon S3 and Amazon DynamoDB permissions. Today each cluster has its own IAM OIDC identity provider, and each new cluster requires an edit to the workload role's trust policy, which has grown close to its size limit. The company wants to stop editing trust policies when it builds a cluster, and wants permissions to differ per namespace using tags.

Which solution will meet these requirements?

- **A)** Attach the permissions to each cluster's node IAM role so every pod inherits them.
- **B)** Install the EKS Pod Identity Agent on each cluster, trust `pods.eks.amazonaws.com` in the role once, and create Pod Identity associations per namespace and service account.
- **C)** Create one IAM OIDC identity provider in a central account and point every cluster's service accounts at it.
- **D)** Store long-lived IAM access keys in Kubernetes Secrets and mount them into the workload pods.

<details><summary>Answer</summary>

**Answer: B.** Pod Identity trusts a single service principal, so the trust policy is written once and never touched again as clusters are added, and its credentials carry session tags for cluster, namespace and service account, which is what allows per-namespace permissions through attribute-based access control. A grants the permissions to every pod on every node, which breaks least privilege and is the classic anti-pattern the exam punishes. C is not how IRSA works: each cluster publishes its own OIDC issuer, so one shared provider cannot validate the other clusters' tokens. D reintroduces long-lived credentials that must be rotated and can be read from the cluster, which is worse than what the company has today.

*Where this is covered: Cluster access and pod credentials.*

</details>

### 7. A fleet drifting into surcharge (Professional)

An organization runs 60 EKS clusters across 12 accounts. Finance reports that the EKS line item has risen sharply although no clusters were added. Investigation shows that 22 clusters are running Kubernetes versions released more than 14 months ago. The platform team wants to stop the overspend, keep every cluster supported, and be warned before this happens again.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Disable extended support on the 22 clusters and take no other action.
- **B)** Upgrade the 22 clusters to a Kubernetes version that is in standard support, then update the add-ons and nodes.
- **C)** Reduce the number of clusters by consolidating workloads into shared namespaces across all 12 accounts.
- **D)** Use the EKS Dashboard to track version and support status across accounts and Regions, and act on the cluster insights findings before each version reaches 14 months.
- **E)** Set every cluster's cluster upgrade policy to `EXTENDED` so upgrades never happen unexpectedly.

<details><summary>Answer</summary>

**Answer: B and D.** The surcharge is extended support, six times the standard hourly rate, and the only way to stop paying it while remaining supported is to upgrade onto a version still in standard support, remembering that the control plane upgrade leaves add-ons and nodes for you to update. The EKS Dashboard supplies the cross-account inventory and forecast that would have caught the drift, and cluster insights flags the API deprecations that block an upgrade. A is dangerous on its own: disabling extended support does not upgrade anything, it just moves the automatic control plane upgrade forward to the end of standard support with no preparation. C collapses account boundaries that exist for isolation and does not address the versions, which are the actual cost driver. E is what the clusters already have, since extended support is on by default, and it is what produced the bill.

*Where this is covered: What EKS manages, and what stays yours.*

</details>

### 8. Kubernetes in a factory that loses its link (Professional)

A manufacturer runs three factories. Each factory must run containerized quality-control workloads that keep operating for days if the connection to AWS is lost, and local regulations require the image data to stay in the building. A fourth workload, a nightly aggregation job, runs on servers in the corporate data center that has a 10 Gbps AWS Direct Connect link, and the company wants that job managed by the same cluster, manifests and IAM roles as its cloud workloads.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Deploy Amazon EKS Anywhere clusters in each factory.
- **B)** Deploy Amazon EKS Hybrid Nodes in each factory, attached to a cluster in the nearest Region.
- **C)** Run the factory workloads on AWS Outposts racks with managed node groups.
- **D)** Run the aggregation job on an EKS cluster with a Fargate profile and connect to the data center over the Direct Connect link.
- **E)** Attach the corporate data center servers to an EKS cluster as EKS Hybrid Nodes over the Direct Connect link.

<details><summary>Answer</summary>

**Answer: A and E.** EKS Anywhere creates complete clusters, control plane included, on the factory's own infrastructure, so each site survives a disconnection from AWS and the image data never leaves the building. Hybrid Nodes is the right shape for the data center job, because the control plane stays in the Region and the on-premises servers join the existing cluster over Direct Connect, giving one cluster, one set of manifests and reusable access entries and Pod Identity associations. B breaks the first requirement: a hybrid node depends on a control plane in the Region, so losing the link stops cluster operations at that site. C puts AWS-managed hardware in the factories, which addresses residency but not disconnection, and managed node groups cannot be deployed on Outposts in any case. D runs the job in the cloud rather than on the data center servers the stem specifies.

*Where this is covered: Kubernetes outside the Region: EKS Anywhere, EKS Distro and Hybrid Nodes.*

</details>

## Summary

Amazon EKS is a sequence of decisions that starts before Kubernetes. Choose EKS only when the requirement names Kubernetes, a Helm chart, an operator or a control plane that must also run outside AWS; otherwise ECS costs less. Having chosen it, accept that AWS runs the control plane across Availability Zones for a flat fee per cluster-hour, and plan the version cadence around 14 months of standard support, 12 more at a sixfold surcharge, and a forced control plane upgrade at 26 that leaves nodes behind. Choose the compute next: Auto Mode for least operational overhead, managed node groups for Windows or a custom AMI, either managed node groups or Auto Mode for GPUs, self-managed nodes for a custom CNI, Fargate only when per-pod kernel isolation outweighs its exclusions. Size the VPC for pods, not instances, and know that prefix delegation fixes node density while a secondary CIDR or IPv6 fixes VPC exhaustion. Turn Kubernetes objects into AWS resources deliberately: Service to NLB and Ingress to ALB through the AWS Load Balancer Controller, claims to EBS for single-writer volumes and EFS for shared files. Grant human access with access entries and workload access with EKS Pod Identity, keeping IRSA for Fargate and clusters outside EKS.

## Related units

- [Amazon ECS and Amazon ECR](ecs-and-ecr.md): the other half of the container platform decision, and the registry both services pull from
- [Amazon EC2](../02-compute/ec2.md): instance families, Spot behavior and purchasing options for node capacity
- [Amazon EC2 Auto Scaling](../02-compute/ec2-auto-scaling.md): the Auto Scaling group behind a managed node group
- [Elastic Load Balancing](../02-compute/elastic-load-balancing.md): ALB and NLB target groups, target types and health checks
- [Amazon VPC](../04-networking/vpc.md): CIDR planning, secondary CIDRs, NAT gateways and interface endpoints for a cluster
- [AWS IAM](../07-security/iam.md): policy evaluation, trust policies and the role design behind Pod Identity and IRSA
- [Amazon EFS](../01-storage/efs.md): the shared file system behind the EFS CSI driver
- [Amazon CloudWatch](../08-management/cloudwatch.md): control plane logs, Container Insights and metric-based alarms

## Sources

- [What is Amazon EKS?](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html): EKS standard against EKS Auto Mode, the managed control plane, and the pricing shape including data transfer on the node side
- [Understand the Kubernetes version lifecycle on EKS](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html): 14 months standard, 12 months extended, 26 total, the default EXTENDED upgrade policy and what the automatic upgrade covers
- [Amazon EKS pricing](https://aws.amazon.com/eks/pricing/): 0.10 USD per cluster-hour standard, 0.60 extended, the Auto Mode management fee and hybrid node vCPU-hour tiers
- [Amazon EKS Provisioned Control Plane](https://docs.aws.amazon.com/eks/latest/userguide/eks-provisioned-control-plane.html): standard against provisioned mode and the scaling tiers
- [Manage compute resources by using nodes](https://docs.aws.amazon.com/eks/latest/userguide/eks-compute.html): the compute comparison table across managed node groups, Auto Mode and hybrid nodes
- [Simplify node lifecycle with managed node groups](https://docs.aws.amazon.com/eks/latest/userguide/managed-node-groups.html): Auto Scaling group behavior, On-Demand against Spot capacity types, draining, node auto repair and the AMI patching responsibility split
- [Maintain nodes yourself with self-managed nodes](https://docs.aws.amazon.com/eks/latest/userguide/worker.html): EKS optimized AMIs, the node IAM role and the cluster tag
- [Automate cluster infrastructure with EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html): managed components, Bottlerocket immutable AMIs, the 21-day node lifetime and the shared responsibility shift
- [Simplify compute management with AWS Fargate](https://docs.aws.amazon.com/eks/latest/userguide/fargate.html): per-pod kernel isolation, private subnets only, no DaemonSets, GPUs, EBS or Fargate Spot, and the IMDS restriction
- [Understand Fargate Pod configuration details](https://docs.aws.amazon.com/eks/latest/userguide/fargate-pod-configuration.html): the vCPU and memory combinations up to 16 vCPU and 120 GB, and ephemeral storage up to 175 GiB
- [Migrate from EKS Fargate to EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/auto-migrate-fargate.html): the statement that Auto Mode is the recommended approach going forward and how to reproduce Fargate isolation
- [Assign more IP addresses to Amazon EKS nodes with prefixes](https://docs.aws.amazon.com/eks/latest/userguide/cni-increase-ip-addresses.html): prefix delegation, the default max-pods of 110 and the transition guidance
- [Prefix Mode for Linux](https://docs.aws.amazon.com/eks/latest/best-practices/prefix-mode-linux.html): /28 prefixes per interface slot, warm prefix targets and when fragmentation defeats prefix mode
- [Deploy Pods in alternate subnets with custom networking](https://docs.aws.amazon.com/eks/latest/userguide/cni-custom-network.html): secondary interfaces in alternate subnets, and the IPv6 recommendation for IPv4 exhaustion
- [View Amazon EKS networking requirements for VPC and subnets](https://docs.aws.amazon.com/eks/latest/userguide/network-reqs.html): two Availability Zones, cluster network interfaces, subnet load balancer tags, secondary CIDRs and service CIDR conflicts
- [Assign security groups to individual Pods](https://docs.aws.amazon.com/eks/latest/userguide/security-groups-for-pods.html): branch interfaces, supported Nitro instance types and the Auto Mode exclusion
- [Cluster API server endpoint](https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html): public, private and restricted endpoint access
- [Route internet traffic with AWS Load Balancer Controller](https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html): Ingress to ALB, Service to NLB, Gateway to ALB, and the legacy cloud provider that creates Classic Load Balancers
- [Grant IAM users and roles access to Kubernetes APIs](https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html): the three authentication modes and the aws-auth ConfigMap comparison
- [CreateAccessConfigRequest](https://docs.aws.amazon.com/eks/latest/APIReference/API_CreateAccessConfigRequest.html): the default authentication mode is CONFIG_MAP through the API and API_AND_CONFIG_MAP through the console
- [Grant IAM users access to Kubernetes with EKS access entries](https://docs.aws.amazon.com/eks/latest/userguide/access-entries.html): access policies against Kubernetes groups, and legacy cluster behavior
- [Learn how EKS Pod Identity grants pods access to AWS services](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html): the pods.eks.amazonaws.com principal, the agent DaemonSet and the 5,000 association limit
- [Grant Kubernetes workloads access to AWS using Kubernetes Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html): the AWS recommendation for Pod Identity and the OIDC provider and trust policy limits behind it
- [IAM roles for service accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html): the cluster OIDC issuer, AssumeRoleWithWebIdentity and where IRSA still applies
- [Amazon EKS add-ons](https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html): curated add-ons, field management and the default VPC CNI, kube-proxy and CoreDNS installs
- [Use Kubernetes volume storage with Amazon EBS](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html): the EBS CSI driver, the Fargate exclusion and the Auto Mode provisioner
- [Use elastic file system storage with Amazon EFS](https://docs.aws.amazon.com/eks/latest/userguide/efs-csi.html): the EFS CSI driver and static provisioning on Fargate
- [Scale cluster compute with Karpenter and Cluster Autoscaler](https://docs.aws.amazon.com/eks/latest/userguide/autoscaling.html): Karpenter against the Cluster Autoscaler, and the support statement for each
- [Send control plane logs to CloudWatch Logs](https://docs.aws.amazon.com/eks/latest/userguide/control-plane-logs.html): the five log types and that all are disabled by default
- [Default envelope encryption for all Kubernetes API Data](https://docs.aws.amazon.com/eks/latest/userguide/envelope-encryption.html): KMS v2 envelope encryption from Kubernetes 1.28 with an AWS owned or customer managed key
- [Amazon EKS Hybrid Nodes overview](https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-overview.html): on-premises nodes on a Region-hosted control plane, vCPU-hour billing and the CNI and CSI exclusions
- [Amazon EKS Anywhere](https://aws.amazon.com/eks/eks-anywhere/): clusters created and operated on your own infrastructure
- [Amazon EKS Distro](https://aws.amazon.com/eks/eks-distro/): the open source Kubernetes distribution that EKS and EKS Anywhere are built from
- [Amazon EKS endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/eks.html): 100 clusters per Region, 30 managed node groups per cluster, 450 nodes per group, 10 Fargate profiles and 3,000 access entries
- [Amazon EKS FAQs](https://aws.amazon.com/eks/faqs/): control plane across multiple Availability Zones, automatic replacement of unhealthy control plane nodes, and the EKS Dashboard
