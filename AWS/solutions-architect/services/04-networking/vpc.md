# Amazon VPC

**Where it sits on the exams.** **Amazon Virtual Private Cloud (Amazon VPC)**, the service that gives an AWS account a logically isolated virtual network, is where almost every other service is placed, addressed, routed, and filtered. It supplies the address space, the subnets, the routing, the packet filters, and the private paths to AWS services, so it appears in SAA-C03 tasks 1.1, 1.2, 2.1, 2.2, 3.4, 4.2, and 4.4, and in SAP-C02 tasks 1.1, 1.2, 2.3, and 3.4. The exam rule of thumb is that a VPC question is answered by four decisions in order: which Region and Availability Zones, which address ranges, which route table sends traffic where, and which filter allows it.

## What a VPC is and where it sits in the AWS global infrastructure

AWS builds its infrastructure as a hierarchy. An AWS Region is a separate geographic area with its own set of data centers, its own service endpoints, and its own pricing. An Availability Zone is one or more discrete data centers inside a Region with independent power, cooling, and physical security, connected to the other zones in the Region by high-bandwidth, low-latency, redundant links. Regions are isolated from each other by design: nothing replicates between them unless you configure replication. Zones inside a Region are close enough for synchronous replication, typically a single-digit millisecond round trip, but far enough apart that a flood, a fire, or a power event is unlikely to take two of them at once.

A VPC lives in exactly one Region and spans every Availability Zone in that Region. A subnet lives in exactly one Availability Zone and cannot be stretched across two. That single pair of facts decides a large share of exam answers. Placing an application in two subnets in two zones gives it a zonal failure boundary; placing it in one subnet gives it none, however many instances are in that subnet. Because each subnet is zonal, a highly available design needs at least one subnet per tier per zone, and the load balancer, the NAT path, and the database standby all have to follow the same pattern.

Zone names are per account. The `us-east-1a` one account sees may be different physical infrastructure from the `us-east-1a` another account sees, because AWS maps names to physical zones independently per account to spread load. The Availability Zone ID, written like `use1-az1`, is stable across accounts and is the value to compare when two accounts must place resources in the same physical zone, such as a shared VPC owner and a participant avoiding a cross-zone hop.

Region selection is a latency, compliance, feature, and cost decision at once. Latency is dominated by physical distance, so serving users in Sydney from `us-east-1` costs well over a hundred milliseconds of round trip that no instance size can recover. Compliance and data residency can require that data never leaves a jurisdiction, which pins the Region regardless of latency. Not every service or instance family is available in every Region, and prices for the same instance, the same gigabyte of storage, and the same gigabyte of data transfer differ between Regions. For a cost-optimized architecture, the Region choice is often a bigger lever than any instance rightsizing that follows it, provided latency and residency requirements still hold. The Well-Architected guidance is to choose the Region from requirements first and then optimize inside it.

When a Region is not close enough, AWS extends the network rather than the VPC. **AWS Local Zones**, extensions of a Region placed in a metropolitan area, **AWS Wavelength**, extensions inside communications service provider networks, and **AWS Outposts**, racks of AWS hardware in a customer data center, all appear as extra subnets in an existing VPC with the same route tables and security groups, so the exam treats them as placement options rather than separate networks.

Distance also has a price. Traffic between resources in the same Availability Zone using private addresses is generally free. Traffic that crosses Availability Zones inside a Region is charged per gigabyte, usually in both directions. Traffic that crosses Regions is charged at a higher per-gigabyte rate, and traffic out to the internet is charged at the internet egress rate. An architecture that spreads chatty components across zones for resilience is trading availability against a real data transfer bill, which is exactly the trade the Professional exam likes to make explicit.

Unless an account was created before default VPCs existed, or an administrator has deleted them, an account gets a default VPC in each Region, with a default subnet in each Availability Zone, an attached internet gateway, a main route table that sends `0.0.0.0/0` to that gateway, and DNS hostnames enabled. Instances launched into a default subnet therefore get a public IPv4 address and reach the internet with no further configuration. That convenience is also the reason exam scenarios about accidental public exposure so often start with a default VPC. Production designs normally create a nondefault VPC where every subnet starts private and internet reachability is added deliberately.

## IP addressing: CIDR blocks, IPv6, and the addresses you do not get

A VPC must have a primary IPv4 CIDR block, and the allowed size runs from a `/16`, which is 65,536 addresses, down to a `/28`, which is 16 addresses. AWS recommends a range from the RFC 1918 private space: `10.0.0.0/8`, `172.16.0.0/12`, or `192.168.0.0/16`. Publicly routable ranges are permitted but are never advertised to the internet from inside the VPC. Four ranges are rejected outright: `0.0.0.0/8`, the loopback range `127.0.0.0/8`, the link-local range `169.254.0.0/16`, and the multicast range `224.0.0.0/4`. Several AWS services use `172.17.0.0/16` internally, so avoiding that range prevents conflicts later.

The primary CIDR cannot be changed or removed for the life of the VPC, but up to five IPv4 CIDR blocks can be associated by default, adjustable to fifty, and each association adds a `local` route automatically. Secondary blocks obey association restrictions that exist because AWS services connect VPCs behind the scenes: once a VPC uses a range from one RFC 1918 block it cannot add a range from a different RFC 1918 block, and `198.19.0.0/16` is excluded alongside them. A secondary block may not overlap an existing block, may not be the same size as or larger than a destination already present in any VPC route table, and may not overlap a peer VPC's range while a peering connection is active or pending. Address planning is therefore close to irreversible, and an undersized VPC is usually replaced rather than resized.

Subnets take a CIDR between a `/28` and a `/16` from the VPC range, and subnets in one VPC may not overlap. Five addresses in every subnet are unusable: the network address, the VPC router at base plus one, the DNS resolver at base plus two, base plus three reserved for future use, and the broadcast address at the top. A `/28` therefore yields eleven usable addresses, not sixteen, which is why `/28` subnets are a poor fit for anything that scales. Address consumption is also larger than instance count suggests, because every load balancer node, NAT gateway, interface endpoint, managed database instance, VPC-attached serverless function, and container task with its own network interface takes at least one address per zone.

IPv6 is a separate and parallel address family, not a replacement that AWS applies for you. A VPC can carry an Amazon-provided IPv6 CIDR block, which arrives as a `/56` of your choosing only in the sense that you accept what Amazon assigns, and up to five IPv6 blocks sized `/44` through `/60` in increments of `/4`. Subnet IPv6 blocks run `/44` through `/64`, and a `/64` per subnet is the normal practice. Amazon-provided IPv6 addresses are globally unique and always advertised to the internet, so an IPv6 address is public by default and reachability is controlled by routing, security groups, and network ACLs rather than by address type. IPv6 traffic needs its own routes: a route table with `0.0.0.0/0` to an internet gateway does nothing for IPv6 until `::/0` is added as well.

Private IPv6 space also exists, but only through **Amazon VPC IP Address Manager (IPAM)**, the feature that plans, allocates, and monitors address space for an account or an organization. Unique local addresses from `fd80::/9` and, if explicitly enabled, globally unique addresses that you own can be provisioned as private ranges. AWS drops these at the internet gateway edge so they cannot leak to the internet, and there is no charge for private IPv6 addresses. They are useful when an organization wants IPv6 inside its private networks and across the private connections between them without exposing anything.

Subnets come in three IP address flavors, and the choice affects which features work. An IPv4-only subnet is the default. A dual-stack subnet has both an IPv4 and an IPv6 range and is the safe migration path, because instances keep working with IPv4-only services while gaining IPv6. An IPv6-only subnet has no IPv4 range at all, which removes IPv4 exhaustion entirely and removes the public IPv4 charge, but it also restricts you to services and instance types that support IPv6-only operation, and it changes endpoint behavior: an interface endpoint in an IPv6-only subnet must itself be an IPv6 endpoint, and a gateway endpoint in such a subnet must use the service's IPv6 prefix list. On the exam, "we are running out of RFC 1918 space across hundreds of accounts" points toward IPv6 or toward IPAM-managed planning, not toward a larger VPC.

> **Professional depth.** Address exhaustion at scale is rarely about instances. It is about a hundred accounts each grabbing a `/16` because that was the default in a template, about overlapping `10.0.0.0/16` ranges in acquired companies that now cannot be peered or attached to the same transit gateway, and about a `/24` shared subnet that runs out because a container platform assigns an address per task. The Professional answer is a governed hierarchy: a top-level pool for the organization, Regional pools beneath it, environment pools beneath those, allocation rules that force a minimum and maximum netmask, and non-overlap enforced before the VPC is created rather than discovered when the peering request fails.

## Subnets, network segmentation, and the multi-tier pattern

Segmentation in a VPC is done by putting resources in different subnets and giving those subnets different routes and different filters. A subnet is called public when its associated route table has a route for `0.0.0.0/0` pointing at an internet gateway. A subnet is called private when it has no such route. There is no checkbox named "public"; the route table is the entire difference. A third category, often called an isolated or VPN-only subnet, has neither an internet gateway route nor a NAT route, so it can reach only the VPC's own ranges and whatever private connections have been added.

The classic multi-tier design places three tiers in three sets of subnets, each set spread across at least two Availability Zones. The presentation tier holds only the load balancer nodes and lives in public subnets. The application tier holds the compute that serves requests and lives in private subnets. The data tier holds databases and caches and lives in isolated subnets with no outbound internet route at all. Internet traffic reaches the load balancer, the load balancer opens a new connection to the application tier, and the application tier opens a connection to the database. No packet from the internet ever has a route to the data tier, because the route table for those subnets has no path that leads outward.

**Elastic Load Balancing**, the managed load balancing service, is what makes this work without exposing compute. An **Application Load Balancer (ALB)**, the Layer 7 load balancer that routes on HTTP attributes, is given public subnets and receives the public address. Its targets are private instances or containers addressed by private IP address, so the targets need no public address and no internet gateway route. The **Amazon Relational Database Service (Amazon RDS)** instance behind them sits in a DB subnet group spanning the isolated subnets, reachable only from the application tier.

The filters chain the tiers together. The load balancer security group allows inbound `443` from `0.0.0.0/0`. The application security group allows inbound on the application port with the load balancer's security group as its source, not a CIDR block. The database security group allows inbound `3306` or `5432` with the application security group as its source. Nothing in that chain names an IP address, so the design keeps working as instances scale in and out, and an operator cannot accidentally widen the application tier by editing a CIDR. Chained security group references are the single most testable segmentation pattern on both exams.

Subnet sizing is a planning exercise, not an afterthought. A reasonable pattern is to give each tier in each zone a subnet of equal size, leave unallocated space between them for growth, and reserve a slice of the VPC range for future subnets such as an endpoint tier, a firewall tier, or a transit gateway attachment tier. Transit gateway attachments and network firewall endpoints both want their own small dedicated subnets, and a firewall endpoint cannot filter traffic entering or leaving the subnet it lives in, so its subnet must be used for nothing else. Planning those in from the start avoids having to carve them out of a production tier later.

The number of Availability Zones is a requirement, not a preference. Two zones is the usual minimum for an application that must survive the loss of a zone, because the remaining zone has to carry full load. Three zones lets you lose one and still have two-thirds of capacity, which is why quorum-based systems and many managed services default to three. More zones spreads risk further but increases cross-zone data transfer charges and increases the number of NAT gateways, endpoint network interfaces, and firewall endpoints that a fully zone-independent design has to pay for. The Professional exam frequently asks you to justify two against three against all zones on exactly these grounds.

Placement decisions extend beyond zones. Latency-sensitive components belong close to the users or the data they serve, which may mean a Local Zone, a Wavelength zone, or an edge service rather than another subnet. Components that talk constantly to each other belong in the same zone, with cross-zone redundancy provided by a full stack in each zone rather than by a stack that is split across zones. Components that are only reached over private paths belong in subnets with no internet route, so that no future route table edit can expose them. Components subject to different regulatory scope often belong in a different VPC or a different account, because a VPC boundary is a much stronger control than a subnet boundary.

Segmentation can also be enforced above the subnet. **VPC Block Public Access (BPA)**, the account-level control that authoritatively blocks internet traffic for a Region, has a bidirectional mode that blocks all traffic through internet gateways and egress-only internet gateways, and an ingress-only mode that blocks inbound internet traffic while still allowing outbound connections initiated from inside. Named VPCs or subnets can be excluded, with an exclusion that is either bidirectional or egress-only. Because it operates independently of route tables and security groups, it answers "make sure nobody in this account can create an internet-facing resource, whatever they put in a route table".

## Route tables, internet gateways, and egress-only internet gateways

A route table is a list of routes, each with a destination expressed as a CIDR block or a prefix list and a target such as a gateway, a network interface, or a connection. Every VPC gets a main route table at creation. A subnet that is not explicitly associated with a route table implicitly uses the main table, which is a common source of accidental exposure: adding an internet gateway route to the main table makes every unassociated subnet public at once. The safer pattern is to leave the main route table with only the `local` route and associate every subnet explicitly with a purpose-built table.

The `local` route cannot be deleted and covers every CIDR block associated with the VPC. It is what makes all subnets in a VPC able to reach each other without configuration, and it is why subnet-to-subnet isolation has to be enforced with security groups and network ACLs rather than with routing. The only way to intercept traffic between two subnets in the same VPC is a gateway route table that replaces or narrows the local route, described below.

Routing uses longest prefix match: the most specific route that matches the destination wins. A route for `10.0.5.0/24` beats a route for `10.0.0.0/16`, which beats `0.0.0.0/0`. IPv4 and IPv6 routes are evaluated independently. When two routes have an identical destination, AWS applies a priority order: static routes first, then routes that reference a prefix list, then propagated routes, and within propagated routes, Border Gateway Protocol (BGP) routes learned from **AWS Direct Connect**, the dedicated private connection between a data center and AWS, then static routes from **AWS Site-to-Site VPN**, the IPsec tunnel service that connects a customer network to AWS, then VPN BGP routes. Static routes to an internet gateway, NAT gateway, network interface, instance, gateway VPC endpoint, transit gateway, VPC peering connection, or **Gateway Load Balancer** endpoint, the transparent Layer 3 load balancer that fronts a fleet of virtual appliances, therefore beat a propagated route with the same destination. This ordering decides hybrid questions where the same prefix arrives from two directions.

The default quotas frame how large a routing design can grow. A VPC gets 200 route tables and 200 subnets by default, both adjustable. A route table holds 500 non-propagated routes by default, adjustable to 1,000 with a warning about network performance, enforced separately for IPv4 and IPv6. Propagated routes are capped at 100 per route table and that cap is not adjustable, which is why the guidance for a hybrid network with more prefixes than that is to advertise a summarized or default route rather than every prefix. A managed prefix list can hold up to 1,000 entries, and referencing one consumes its maximum entry count against the referencing resource's quota, so a 20-entry prefix list counts as 20 rules in a security group even if only three entries are populated.

An internet gateway is a horizontally scaled, redundant, highly available VPC component that has no bandwidth constraint you manage and no availability risk you design around. It does two things: it provides a routing target for internet-bound traffic, and it performs one-to-one network address translation between an instance's private IPv4 address and its public IPv4 or Elastic IP address. Only one internet gateway can be attached to a VPC at a time, and the default quota is five per Region, raised automatically when the VPC quota is raised. An instance is reachable from the internet only when all four conditions hold: a public address is assigned, the subnet's route table has a route to the internet gateway, the security group allows the traffic, and the network ACL allows it in both directions.

IPv6 needs a different device for the outbound-only case. Because every Amazon-provided IPv6 address is globally unique and publicly routable, there is no IPv6 equivalent of hiding behind a shared address. An **egress-only internet gateway** is a stateful, horizontally scaled component that forwards IPv6 traffic out and returns the responses, while preventing the internet from initiating connections inward. You route `::/0` to it from a private subnet's route table. It carries no charge of its own, you cannot associate a security group with it, and it handles only IPv6. A NAT gateway is the IPv4 tool for the same job, and mixing them up is a routine distractor: "outbound-only internet access for IPv6 instances" maps to an egress-only internet gateway, never to a NAT gateway.

A route table can also be associated with a gateway rather than a subnet, which is called a **gateway route table**. An internet gateway or a virtual private gateway, the VPN and Direct Connect attachment point on the AWS side of a hybrid connection, can carry one, and its only permitted targets are the default local route, a Gateway Load Balancer endpoint, or a network interface belonging to a middlebox appliance in the same VPC. Its destinations must be inside the VPC's own ranges, either the whole VPC CIDR, replacing the local route, or one subnet's CIDR as a more specific route. This is the mechanism that forces inbound internet traffic through an inspection appliance before it reaches a workload subnet. Route propagation cannot be enabled on a gateway route table, prefix lists cannot be used as destinations, and return traffic must be routed back through the same appliance because asymmetric routing is not supported.

Two routing patterns generate most troubleshooting questions: a private subnet whose route table lacks a NAT route, so instances reach the VPC and its endpoints but time out on everything else, and a public subnet whose instances have no public address, so outbound traffic reaches the internet gateway and is dropped because there is nothing to translate.

## NAT gateways, NAT instances, and the per-Availability-Zone decision

A **NAT gateway** is a managed network address translation service that lets resources in a private subnet open outbound connections while preventing anything outside from initiating a connection inward. It comes in two connectivity types. A public NAT gateway lives in a public subnet, carries an Elastic IP address, and reaches the internet through the VPC's internet gateway. A private NAT gateway has no Elastic IP address and is used to reach other VPCs or an on-premises network through a transit gateway or a virtual private gateway; if you route its traffic to an internet gateway, the internet gateway drops it. Connections must always be initiated from inside the VPC containing the gateway.

The managed nature of the service is what the exam rewards. A NAT gateway supports 5 Gbps of bandwidth and scales automatically to 100 Gbps, processes one million packets per second and scales to ten million, and is implemented with redundancy inside its Availability Zone. It supports TCP, UDP, and ICMP, and performs NAT64 for IPv6 workloads that need to reach IPv4 destinations when paired with DNS64 on **Route 53 Resolver**, the DNS service built into every VPC. You cannot attach a security group to a NAT gateway; you control traffic with the security groups on the instances behind it and with the network ACL on the gateway's subnet, remembering that a NAT gateway uses source ports 1024 through 65535.

Two constraints bite at scale. Each IPv4 address on a NAT gateway supports up to 55,000 simultaneous connections to each unique destination, where a unique destination is a combination of destination address, destination port, and protocol. A fleet hammering one popular API endpoint therefore exhausts ports long before it exhausts bandwidth. The fix is to associate more addresses, up to eight IPv4 addresses per zonal NAT gateway, of which two Elastic IP addresses are allowed by default and up to eight with a quota increase, or to split the workload across subnets with separate gateways. The second constraint is routing: you cannot route traffic to a NAT gateway through a VPC peering connection, and you cannot reach one from Site-to-Site VPN or Direct Connect through a virtual private gateway, though you can through a transit gateway.

A NAT instance is an **Amazon Elastic Compute Cloud (Amazon EC2)** instance, one of the resizable virtual servers that most VPC traffic originates from, running NAT software, and the comparison is a standing exam table. Read it as the reason AWS recommends the gateway for nearly every case.

| Attribute | NAT gateway | NAT instance |
|---|---|---|
| Availability | Redundant within its Availability Zone; create one per zone for zone independence | You script failover between instances |
| Bandwidth | 5 Gbps, scaling to 100 Gbps | Whatever the instance type provides |
| Maintenance | Managed by AWS | You patch the operating system and software |
| Sizing | Uniform, no type or size to choose | You pick instance type and size |
| Security groups | Cannot be associated | Can be associated |
| Port forwarding | Not supported | Supported with manual configuration |
| Bastion host use | Not supported | Can double as a bastion host |
| Cost shape | Per gateway-hour plus per GB processed | Per instance-hour by type and size |
| Timeout behavior | Sends RST on timeout | Sends FIN on timeout |

A NAT instance is still the right answer in a narrow set of cases the exam signals explicitly: when port forwarding is required, when the same host must also serve as a bastion, when a security group must be attached to the translation device itself, or when the traffic volume is so low that one small burstable instance costs less than a gateway-hour. Everything else, especially "least operational overhead", points at the gateway.

The per-zone decision is an owned exam topic and it has changed. Historically the choice was between one shared NAT gateway for the whole VPC and one NAT gateway in each Availability Zone. A single shared gateway saves gateway-hours, but it creates two problems. It makes every other zone dependent on the health of one zone, so if that zone is impaired, private resources in the surviving zones lose outbound access. And it forces every byte from other zones to cross an Availability Zone boundary, which adds per-gigabyte cross-zone data transfer charges on top of the gateway's own data processing charge. For a high-volume workload the cross-zone transfer charge frequently exceeds what the extra gateway-hours would have cost, so the per-zone design can be both more available and cheaper. The rule to carry into the exam: one NAT gateway per zone, with each private subnet routing to the gateway in its own zone, unless the traffic volume is genuinely trivial and the requirement explicitly accepts a zonal dependency.

AWS has since added a third option. A regional NAT gateway is created with `--availability-mode regional` against a VPC rather than a subnet, and it automatically expands into any Availability Zone where it detects a network interface and contracts out of zones with no active workloads. It needs no public subnet, because it is a standalone resource with its own automatically created route table that already contains a route to the internet gateway, which removes a common misconfiguration where a private resource is placed in the NAT subnet. Every private subnet in every zone can point at the same NAT gateway ID, so one route entry replaces the per-zone table maintenance. It supports up to 32 IP addresses per Availability Zone against 8 for a zonal gateway, and each address adds another 55,000 concurrent connections to a popular destination. Expansion into a newly used zone can take up to 60 minutes, during which traffic from that zone is processed across zones by an existing zone's capacity. The important limitation is that regional NAT gateways do not support private NAT, so a private NAT design must still use zonal gateways, and they are not supported in constrained Availability Zones.

Cost work on NAT rarely starts with the gateway itself. The largest reduction is usually to stop sending traffic through it. Traffic to **Amazon Simple Storage Service (Amazon S3)**, the Regional object storage service, and **Amazon DynamoDB**, the managed key-value and document database, should use a gateway endpoint, which has no hourly or data processing charge; other AWS services should use interface endpoints, which cost endpoint-hours but remove both NAT processing and internet egress charges. Only once the remaining NAT traffic is genuinely external does the gateway count and placement matter.

## Elastic IP addresses, public IPv4 charges, IPAM, and BYOIP

A public IPv4 address assigned automatically at launch comes from an Amazon pool, is not associated with the account, and is released when the instance stops or the address is disassociated. An **Elastic IP address** is a public IPv4 address allocated to the account, which can be associated with and moved between resources on demand and survives an instance stop or replacement. The default quota is five Elastic IP addresses per Region, adjustable, and that low default is deliberate: a design that needs dozens of static public addresses usually wants a load balancer, **AWS Global Accelerator**, the service that fronts an application with static anycast addresses on the AWS network, or a NAT gateway instead.

The charging model changed on February 1, 2024, and this is one of the items most likely to be out of date in older study material. AWS charges an hourly rate for every public IPv4 address, whether it is attached to a running resource or sitting idle, and the charge applies across services including EC2 instances, RDS database instances, **Amazon Elastic Kubernetes Service (Amazon EKS)** nodes, the managed Kubernetes service's worker instances, load balancers, and NAT gateways. The old distinction where an attached Elastic IP was free and only an unattached one was charged no longer exists. The EC2 free tier includes 750 hours of public IPv4 address usage per month for the first twelve months. Addresses that you own and bring to AWS through BYOIP are not charged this fee, and IPv6 addresses are not charged at all.

Three consequences follow for architecture and for exam answers. First, a fleet of a thousand instances each with a public address now carries a five-figure annual charge purely for addressing, so instances that only need outbound access should sit in private subnets behind NAT and instances that need inbound access should sit behind a load balancer that holds the small number of public addresses. Second, unused Elastic IP addresses are pure waste and are a standard finding in a cost review. Third, IPv6-only and dual-stack subnets become a cost lever, not just an address-exhaustion lever, because IPv6 carries no per-address charge.

IPAM is the tool for managing all of this at organization scale. When you create an IPAM it automatically creates two scopes. The private scope holds address space that is never advertised to the internet, and the public scope holds space that is. Scopes let the same range be reused in two unconnected networks without conflict. Inside a scope you create pools, which are collections of contiguous ranges, and pools nest: a top-level pool for the organization, Regional pools beneath it, and environment or business-unit pools beneath those. An allocation is a CIDR handed from a pool to a VPC, a subnet, or another pool. Allocation rules on a pool can require a minimum and maximum netmask, require particular tags on the requesting resource, and restrict which Regions or accounts may draw from it, so a team creating a VPC gets a correctly sized, non-overlapping range automatically instead of inventing one.

IPAM integrates with **AWS Organizations**, the multi-account governance service, through a delegated administrator account, giving one team a view of every CIDR in every account and Region with utilization metrics and a history of allocations. It can also discover resources that are using address space outside its pools, which is how a migration finds the overlapping ranges before a peering attempt fails. IPAM is billed in two tiers: a free tier that covers management within a single Region at no charge, and an advanced tier billed per active IP address per hour for management that spans Regions and accounts. **Public IP Insights**, the IPAM view of every public IPv4 address in use, is the tool for finding the addresses now costing money.

Bring your own IP addresses, or BYOIP, moves an organization's own public IPv4 or IPv6 range into AWS. You keep ownership, AWS advertises the range for you, and the addresses appear as a pool from which Elastic IP addresses or VPC IPv6 CIDR blocks are drawn. It is the answer when a partner allowlist, a hardcoded client configuration, or a reputation-bound mail service makes the actual addresses part of the requirement, and it avoids the public IPv4 hourly charge. For the reverse case, IPAM can provision a contiguous AWS-owned public IPv4 block and allocate sequential Elastic IP addresses from it.

One more quota deserves attention because it is invisible until it stops you. **Network Address Usage (NAU)**, a metric that counts IP addresses, network interfaces, and prefix list CIDRs in a VPC, has a default limit of 64,000 units per VPC, adjustable to 256,000, and 128,000 units across a VPC and all of its intra-Region peered VPCs, adjustable to 512,000. Inter-Region peered VPCs do not count toward the peered total. NAU is the ceiling that a very large flat VPC hits first, and it is the technical argument for segmenting a large estate into several VPCs joined by a transit gateway rather than growing one.

## Security groups compared with network ACLs

A VPC has two packet filters and the exam tests the difference constantly. A **security group** is a virtual firewall attached to a network interface, so it protects individual resources. A **network ACL** is a filter attached to a subnet, so it protects everything in that subnet including resources launched later by someone who forgot the right security group. The table is the comparison AWS publishes and the one worth memorizing.

| Characteristic | Security group | Network ACL |
|---|---|---|
| Level of operation | Instance, more precisely network interface, level | Subnet level |
| Scope | Applies to every resource associated with the group | Applies to every resource in the associated subnets |
| Rule type | Allow rules only | Allow and deny rules |
| Rule evaluation | Evaluates all rules before deciding | Evaluates rules in ascending number order until a match is found |
| Return traffic | Automatically allowed, stateful | Must be explicitly allowed, stateless |

Statefulness is the difference that generates the most wrong answers. A security group that allows inbound TCP 443 automatically allows the response out, whatever the outbound rules say, because it tracks the connection. A network ACL does not track anything, so allowing inbound TCP 443 without an outbound rule for the ephemeral port range leaves every response dropped. The range AWS documents is 32768 to 61000 for Linux kernels using the Amazon Linux defaults, 49152 to 65535 for requests through a NAT gateway, and 1025 to 5000 for Windows versions through Server 2003. Open the widest range the traffic requires rather than guessing one. Linux clients typically use ephemeral ports 32768 through 60999, Windows uses 49152 through 65535, a NAT gateway uses 1024 through 65535, and an Elastic Load Balancing node uses 1024 through 65535, so a restrictive network ACL usually has to allow 1024 through 65535 outbound to be usable at all. That is a large part of why AWS recommends security groups as the primary control and network ACLs as a coarse secondary guardrail.

Security group rules specify a protocol, a port range, and a source for inbound or a destination for outbound. The source can be a CIDR block, a managed prefix list, or another security group. Referencing another security group is the feature that makes the multi-tier pattern maintainable: the rule follows membership rather than addresses, so instances can be replaced, scaled, or renumbered without touching a rule. A new security group starts with no inbound rules and an outbound rule allowing all traffic. The default security group of a VPC is different: it allows all inbound traffic from resources assigned to the same group and all outbound traffic, which is why relying on the default group is a recognized anti-pattern.

A **managed prefix list** is a named, versioned set of CIDR blocks that can be referenced in both security group rules and route tables. Customer-managed prefix lists let a network team maintain the corporate address ranges in one place and have every security group inherit the change. AWS-managed prefix lists cover the address ranges of services such as Amazon S3, DynamoDB, and **Amazon CloudFront**, the content delivery network, which is how a security group can allow outbound traffic to S3 without listing IP ranges that change. The cost is quota: a prefix list consumes its maximum entry count, not its current entry count, against the referencing resource, so a prefix list with a maximum of 60 entries fills an entire default security group.

The quotas that shape a security group design are worth knowing exactly. A Region allows 2,500 VPC security groups by default, adjustable. A security group allows 60 inbound and 60 outbound rules by default, adjustable, counted separately for inbound and outbound and separately for IPv4 and IPv6, so the default really means 60 IPv4 inbound plus 60 IPv6 inbound plus the same outbound. A network interface can carry 5 security groups by default, adjustable up to 16. The hard constraint is that rules per security group multiplied by security groups per network interface cannot exceed 1,000, so 16 groups per interface forces a maximum of 62 rules per group. A network ACL allows 20 rules by default in each direction, adjustable to 40 inbound and 40 outbound with a warning about network performance, and a VPC allows 200 network ACLs. Those numbers explain why a design that tries to express per-customer allowlists in network ACL rules fails and why prefix lists and security group references exist.

Cross-VPC references have precise rules that separate two right-looking exam options. Over a VPC peering connection, a security group rule can reference a security group in the peer VPC only when the peering connection is active and both VPCs are in the same Region; for a peer in another account but the same Region you write the rule as `123456789012/sg-1a2b3c4d`. For a peer in a different Region you cannot reference the group at all and must use the peer VPC's CIDR block. When a peering connection is deleted or the referenced group is removed, the rule becomes stale and is not cleaned up automatically; `describe-stale-security-groups` finds them and they must be removed by hand.

Over **AWS Transit Gateway**, the Regional hub that interconnects VPCs and on-premises networks, security group referencing became generally available in September 2024 and works differently in several respects. It must be enabled on the transit gateway and on the VPC attachment, and it works only when both are enabled, so a half-configured pair silently does nothing. It applies to inbound rules only; outbound rules cannot reference a remote security group. Both VPCs must be attached to the same transit gateway, because referencing does not work across a transit gateway peering connection. AWS also documents that it is unavailable in the `use1-az3` Availability Zone and on Outposts, Wavelength and some Local Zones, and that an Amazon EFS mount target needs an allow-all egress rule for it to work. It is not supported for PrivateLink endpoints, where CIDR-based rules are the documented alternative, and it does not work across a Gateway Load Balancer or AWS Network Firewall in an inspection VPC. There is no additional charge. For the exam, remember that neither peering nor transit gateway referencing crosses a Region boundary, so any inter-Region requirement falls back to CIDR blocks or prefix lists.

A security group can also be shared. The shared security group feature lets an account share a non-default security group in a non-default VPC with other accounts in the same organization and Region through **AWS Resource Access Manager (AWS RAM)**, the service that shares resources across accounts. Participants then attach the owner's group to their own network interfaces, and any rule change the owner makes applies everywhere immediately, which is how a central security team enforces a baseline inside a shared VPC. Participants cannot share security groups they created, default groups cannot be shared, and when an owned and a shared group are mixed on one interface the lower of the two accounts' per-interface quotas applies.

Writing the rules is where the "specify inbound and outbound network flows" skill is tested. The pattern is to describe each flow as a source, a destination, a protocol, and a port, then decide which side the rule belongs on. A web tier reachable from anywhere gets inbound `443` from `0.0.0.0/0` and `::/0`. An application tier gets inbound on its port from the web tier's security group. A database gets inbound `5432` from the application tier's security group. Administrative access gets inbound `22` or `3389` from a bastion's security group or, better, no inbound rule at all because **AWS Systems Manager** Session Manager, the agent-based shell service that connects through an interface endpoint, needs none. Outbound rules are left permissive on most tiers and tightened, usually with a prefix list, where egress control is a stated requirement.

```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-app \
  --protocol tcp --port 8080 --source-group sg-alb
```

## VPC endpoints: gateway, interface, and AWS PrivateLink

An AWS service endpoint is the URL an SDK or CLI call is sent to, normally a public Regional name such as `s3.us-east-2.amazonaws.com`. Traffic from a VPC to such an endpoint stays on the AWS network but still needs a route out of the VPC through an internet gateway or a NAT gateway. A VPC endpoint removes that requirement by giving the service a presence inside the VPC. There are two mechanisms and several endpoint types, and the difference decides both the network design and the bill.

A **gateway endpoint** is a route table entry, not a device. It exists only for Amazon S3 and Amazon DynamoDB. You select the route tables to associate, and AWS adds a route whose destination is the service's AWS-managed prefix list and whose target is the endpoint. Every instance in a subnet using that route table then reaches the service privately, with no internet gateway and no NAT. There is no hourly charge and no data processing charge, which makes a gateway endpoint the cheapest private path to S3 or DynamoDB and a standard cost-optimization answer. Because it is routing, three limits follow: a route table can hold only one endpoint route per service, traffic to the same service in a different Region still goes to the internet gateway because prefix lists are Regional, and the endpoint is unreachable from outside the VPC, so it cannot be used over peering, a transit gateway, Site-to-Site VPN, or Direct Connect. Security still applies at both ends: instance security groups need an outbound rule to the service's prefix list, and network ACLs need the service's CIDR ranges because they cannot reference prefix lists.

An **interface endpoint** is an elastic network interface with a private IP address, placed in one subnet per Availability Zone that you select, and it is powered by **AWS PrivateLink**, the technology that presents a service inside a consumer VPC through private addresses. Because it is a network interface, it has a security group, it can be reached from anywhere that can reach that address including peered VPCs, transit gateway attachments, Site-to-Site VPN, and Direct Connect, and it supports far more services than the two with gateway endpoints. It is billed per endpoint-hour in each Availability Zone plus per GB of data processed, so a design with twenty endpoints across three zones carries a real fixed cost that has to be weighed against the NAT processing and egress charges it removes.

Private DNS is what makes an interface endpoint transparent. Creating one produces a Regional DNS name and one zonal name per Availability Zone. Enabling private DNS, which requires the VPC attributes `enableDnsSupport` and `enableDnsHostnames`, creates a hidden AWS-managed private hosted zone that resolves the service's normal public name to the endpoint's private addresses, so existing applications and SDKs need no change. AWS recommends enabling private DNS, configuring at least two Availability Zones, and calling the Regional name, at which point requests are distributed round robin across healthy endpoint network interfaces. If you would rather avoid the cross-zone hop and its transfer charge, call the zonal name for the endpoint interface in the same zone as the caller. An endpoint with an interface in only one zone is a single point of failure for the whole VPC: resources in other zones lose access to that service if the zone is impaired.

A **VPC endpoint policy** is a resource policy in **AWS Identity and Access Management (IAM)**, the service that controls identities and permissions, attached to the endpoint that determines which principals may use it and for what. The default allows all actions by all principals, so it is a control you have to write. Two patterns matter on the exam. The endpoint policy can restrict the endpoint to specific buckets, tables, or actions, which stops an instance from using the private path to reach a personal bucket. From the other direction, a resource policy on the bucket or table can require that requests arrive through a named endpoint using the `aws:SourceVpce` condition key, or from a named VPC using `aws:SourceVpc`. Together they express "this data is only reachable from this network, and this network can only reach this data". As with any deny that names a network path, keep an administrative route in place, because a bucket policy that denies everything not arriving through an endpoint can lock a console user out.

Two newer endpoint types extend the same model beyond AWS services. A resource endpoint connects to a resource that another account shared with you, such as an RDS database, an EC2 instance, an application endpoint, a domain-name target, or an IP address, without a load balancer in the path. The provider creates a resource gateway as the point of ingress into its VPC, defines a resource configuration describing what is being shared, and shares it through AWS RAM. A service-network endpoint connects to a whole service network in one endpoint, which is how on-premises networks reach many services and resources through a single private door, and is covered in the next section. There are also Gateway Load Balancer endpoints, which are routing targets used to steer traffic to an appliance fleet rather than to consume a service.

Choosing between the mechanisms is short. For S3 or DynamoDB from inside this VPC only, use a gateway endpoint, because it is free. For S3 or DynamoDB reached from on-premises or another VPC, use an interface endpoint. For any other AWS service, an interface endpoint is the only option. The recurring distractor is an interface endpoint when the requirement says "lowest network cost" and every client is inside the VPC, and the mirror image is a gateway endpoint when the clients are on-premises.

## PrivateLink endpoint services and Amazon VPC Lattice

PrivateLink has a provider side as well as a consumer side. A provider creates a **VPC endpoint service** by putting a **Network Load Balancer (NLB)**, the Layer 4 load balancer that preserves connection semantics and supports static addresses, or a Gateway Load Balancer in front of its application and publishing it under a service name. Consumers create interface endpoints against that name. By default nobody may connect: the provider adds explicit permissions for named AWS principals, and each consumer connection arrives in a `PendingAcceptance` state that the provider accepts or rejects, unless automatic acceptance is configured. Traffic flows one way only, from consumer to provider; the provider cannot initiate connections back through the endpoint.

The model solves problems that peering cannot. Consumer and provider CIDR ranges may overlap, because the consumer only ever addresses the endpoint's own private address. Only the published service is exposed, not the provider's whole VPC, so it is a far smaller blast radius than a peering connection. And the relationship scales to thousands of consumers without any routing coordination, which is why software-as-a-service vendors and internal platform teams both use it. The provider can also enable split-horizon DNS so that the same hostname resolves to private endpoint addresses inside a consumer VPC and to public addresses elsewhere.

**Amazon VPC Lattice** is the application networking service that takes the same idea further up the stack. Instead of connecting networks, it connects services. A service in Lattice is a unit of application function with its own listeners, rules, and target groups, where targets can be EC2 instances, IP addresses, **AWS Lambda** functions, the serverless function service, Application Load Balancers, **Amazon Elastic Container Service (Amazon ECS)** tasks, the managed container orchestrator's units of work, or Kubernetes pods. A service network is a logical boundary that collects services and resource configurations; VPCs are associated with the service network, and any client in an associated VPC can reach any service in it that authorizes the call. Lattice supports overlapping CIDR blocks between client and service VPCs because clients address services by DNS name through the Route 53 Resolver rather than by network route.

Three features distinguish it on the exam. Authorization is expressed as auth policies, IAM-style documents attached to the service network or to an individual service, so service-to-service access control is a policy decision rather than a security group edit; auth policies do not apply to resource configurations. Observability is built in, with per-request metrics and access logs published to **Amazon CloudWatch**, the metrics, logs, and alarms service, to **Amazon Data Firehose** delivery streams, the managed streaming delivery service, or to S3 buckets. And routing has Availability Zone affinity: Lattice returns an address in the client's own zone when one is available, and there are no inter-Availability-Zone data transfer charges within Lattice. Pricing is per service-hour, per GB processed, and per request, with resource configurations billed hourly to the service network owner.

The selection rule is worth stating plainly. PrivateLink exposes one service to many consumers with minimal exposure and tolerates overlapping ranges. VPC Lattice applies when the unit of connectivity is an application service rather than a network, teams own separate accounts and VPCs, and per-request authorization and observability matter more than IP reachability.

## Connecting VPCs: peering, Transit Gateway, and VPC sharing

A **VPC peering connection** is a one-to-one networking connection between two VPCs that lets resources address each other by private IPv4 or IPv6 address. It is not a gateway and not a VPN, has no single point of failure and no bandwidth bottleneck, and costs nothing to create. VPCs can be in different accounts and different Regions. Inter-Region peering traffic is encrypted before it leaves an AWS facility and stays on the AWS global backbone. Setup is a request from the requester VPC owner, an acceptance from the accepter VPC owner, then a route in each side's route tables pointing at the peer's CIDR, then security group rules on both sides.

The limitations are the exam content. The two VPCs may not have matching or overlapping IPv4 or IPv6 CIDR blocks, and if either has multiple CIDR blocks, any overlap blocks the whole connection. Peering is not transitive: if A peers with B and A peers with C, B cannot reach C through A, and a third connection is required. Because a full mesh of n VPCs needs n times n minus one, divided by two connections, peering stops scaling somewhere around a dozen VPCs. Edge-to-edge routing is not supported in any form: a peer cannot use your internet gateway, your NAT device, your Site-to-Site VPN, your Direct Connect connection, or your gateway endpoint. Jumbo frames are 9001 bytes within a Region and 8500 bytes inter-Region. DNS resolution of the peer's private hostnames requires explicitly enabling DNS resolution support on the connection, which is mandatory for inter-Region peering. Data transfer within an Availability Zone over peering is free even across accounts, while cross-zone and cross-Region transfer is charged.

AWS Transit Gateway is the answer when the mesh becomes unmanageable. It is a Regional virtual router. Attachments include VPCs, Site-to-Site VPN connections, a Direct Connect gateway, Transit Gateway Connect attachments for software-defined wide area network appliances, **AWS Client VPN** endpoints, the managed remote-access VPN service, and peering connections to transit gateways in other Regions. Each attachment associates with exactly one transit gateway route table, and one route table can serve many attachments, which is how isolation domains are built: a production route table and a development route table on the same transit gateway can share an egress VPC without seeing each other. Pricing is per attachment-hour plus per GB processed. This unit introduces the transit gateway only; attachment types in detail, static compared with propagated routes, maximum transmission unit sizes, route table strategy, appliance mode, multicast, Network Manager, Cloud WAN, and the hybrid DNS patterns that go with them are taught in the `04-networking/hybrid-connectivity.md` unit.

**VPC sharing** solves a different problem: instead of connecting many VPCs, it removes the need for them. An owner account shares one or more subnets, through AWS RAM, with participant accounts in the same organization. Participants launch their own EC2 instances, RDS databases, **Amazon Redshift** clusters, the managed data warehouse, and Lambda functions directly into those subnets and get implicit VPC routing between them with no peering, no transit gateway attachment, and no inter-VPC data transfer charge. Each account keeps its own billing, its own IAM boundary, and its own resource quotas, because participant resources count against participant quotas.

The division of responsibility is precise, and it is exactly what a Professional question tests. The owner creates and controls subnets, route tables, network ACLs, internet gateways, NAT gateways, gateway and interface endpoints, Route 53 Resolver endpoints, peering connections, and transit gateway attachments. Participants can create network interfaces and their own security groups, can enable flow logs for network interfaces they own, and can reference other accounts' security groups in their rules using `account-number/security-group-id`. Participants cannot create or modify subnets, route tables, network ACLs, NAT gateways, or peering connections, cannot enable flow logs on the shared subnet itself, and cannot launch instances with the VPC's default security group because it belongs to the owner. Owners can see participant network interfaces and security groups but cannot use or modify them. Default VPC subnets cannot be shared at all. The default quotas are 100 participant accounts per VPC and 100 subnets shared with any one account, both adjustable.

The choice among the three is a sizing question. VPC sharing suits many teams on one network inside one trust boundary and conserves address space. Peering suits a few durable, non-overlapping point-to-point relationships. A transit gateway suits a growing estate, hybrid connectivity, and centralized inspection or egress. They compose, and commonly do.

## DNS in a VPC, DHCP option sets, and DNS Firewall

Every VPC has a DNS resolver, Route 53 Resolver, reachable at the VPC base address plus two in each subnet and at the link-local address `169.254.169.253`. Two VPC attributes control it. `enableDnsSupport` decides whether the resolver answers at all, and `enableDnsHostnames` decides whether instances with public addresses receive public DNS hostnames. Both must be on for private DNS on an interface endpoint and for a Route 53 private hosted zone to resolve inside the VPC. The resolver has one quota that surprises people: each network interface can send 1,024 packets per second to the resolver, and that limit cannot be raised. A DNS-heavy application that resolves a name on every request has to cache locally or run a caching resolver inside the VPC.

A **DHCP option set** carries the network settings the Amazon DHCP server hands to instances: domain name servers, domain name, NTP servers, NetBIOS name servers, NetBIOS node type, and an IPv6 preferred lease time. Each Region has a default option set whose domain name server value is `AmazonProvidedDNS`. A VPC can have exactly one associated option set, though one option set can be associated with many VPCs. Option sets cannot be edited after creation: to change a value you create a new set and associate it, and instances pick up the change as each one renews its DHCP lease, so no restart or relaunch is needed, though the change does not land on every instance at the same moment. The exam case for a custom set is a workload joined to an on-premises Active Directory domain, where the domain controllers must be the name servers; the common failure is listing only the on-premises servers and losing the ability to resolve AWS service names, which is why a hybrid design usually points at Route 53 Resolver inbound and outbound endpoints instead.

Hybrid name resolution belongs elsewhere, but the shape is worth a sentence. Resolver inbound endpoints let on-premises systems resolve names in AWS private hosted zones, and outbound endpoints with forwarding rules let VPC resources resolve on-premises names. Both are network interfaces in subnets, both belong in at least two Availability Zones, and both are shareable across accounts. The details are taught in [hybrid connectivity](hybrid-connectivity.md) and [Amazon Route 53](route53.md).

**Route 53 Resolver DNS Firewall** filters outbound DNS queries that pass through the VPC resolver. You build rule groups containing ordered rules, each matching a domain list and taking an action of ALLOW, BLOCK, or ALERT, then associate the rule groups with VPCs. BLOCK can return NODATA, NXDOMAIN, or a custom override response. AWS publishes managed domain lists covering known malware and botnet command-and-control domains, and a rule group can also use your own lists to implement either a denylist or a strict allowlist. Its primary purpose is preventing DNS exfiltration, where a compromised instance encodes data into lookups against a domain the attacker controls, and it can also block resolution of private hosted zone names and VPC endpoint names. It is a feature of the VPC resolver and needs no other setup, and Firewall Manager can attach rule groups automatically to every VPC that comes into scope of a policy. DNS Firewall is owned by the `07-security/waf-shield-firewall-manager-and-network-firewall.md` unit; treat this as the paragraph that tells you when to reach for it.

## Traffic visibility, inspection, and troubleshooting

**VPC Flow Logs** capture metadata about IP traffic to and from network interfaces. A flow log can be created at three levels: one network interface, a whole subnet, or a whole VPC, where the subnet and VPC levels automatically include interfaces created later. Records can be published to CloudWatch Logs, to Amazon S3, or to a Data Firehose delivery stream, and S3 with **Amazon Athena**, the serverless SQL query service for data in S3, is the usual choice for cost-effective analysis at volume. The default record format carries source and destination address and port, protocol, packet and byte counts, start and end time, and an action of ACCEPT or REJECT. A custom format adds fields worth knowing: `pkt-srcaddr` and `pkt-dstaddr` for the original addresses when an intermediate device rewrote them, `traffic-path` for the route taken out of the VPC, `flow-direction`, and the transit gateway, ECS, and instance tag fields available in later versions. Collection happens outside the traffic path, so enabling flow logs does not affect throughput or latency.

The limitations matter because they turn up as wrong answers. Flow logs record metadata, never packet contents, so they cannot answer "what was in the request". A flow log configuration cannot be edited after creation; you delete it and make a new one. Several traffic types are never logged: queries to the Amazon DNS server, DHCP traffic, traffic to and from `169.254.169.254` for instance metadata and `169.254.169.123` for the Amazon Time Sync Service, Windows license activation, ARP, traffic to the reserved VPC router address, traffic between an endpoint network interface and a Network Load Balancer interface, and mirrored source traffic. On a Nitro-based instance the aggregation interval is always one minute or less regardless of the configured maximum. In a shared VPC, participants can create flow logs only for interfaces they own, and the owner cannot see or delete participant flow logs.

**Traffic Mirroring** answers the question flow logs cannot, by copying actual packets from an `interface`-type elastic network interface and sending them to a target for out-of-band inspection. A mirror session ties a source, a filter, and a target together; the filter selects the traffic of interest by protocol, port range, and CIDR, and packet truncation limits how much of each packet is copied. Targets are a network interface, a Network Load Balancer with a UDP listener, or a Gateway Load Balancer endpoint, so appliance fleets can sit behind a load balancer. Sources must be supported instance types, and only Nitro v2 bare metal instances are supported among bare metal types. Billing is per active mirror session-hour and continues until the session is deleted, even if the source instance is stopped, plus data transfer and load balancer processing. Use flow logs for "who talked to whom, and was it allowed"; use Traffic Mirroring for "show me the packets" in threat hunting, deep inspection, and application troubleshooting.

**AWS Network Firewall** is the managed stateful firewall and intrusion detection and prevention service for a VPC. It creates firewall endpoints in dedicated subnets, one per Availability Zone, and you edit route tables to steer traffic through them, typically between an internet gateway and workload subnets, or between a transit gateway and an egress VPC. **AWS Firewall Manager**, the service that applies and audits firewall policies across an organization, can deploy and enforce Network Firewall, AWS WAF and security group policies centrally from the Organizations management or delegated administrator account. A firewall policy references stateless rule groups, which examine one packet at a time on 5-tuple criteria, and stateful rule groups, which track flows and support Suricata-compatible rules, domain list filtering, and protocol detection independent of port. A firewall endpoint cannot filter traffic entering or leaving its own subnet, which is why the firewall subnet must be used for nothing else, and using an endpoint in one zone to filter another zone's traffic incurs cross-zone charges. Firewall Manager can deploy and maintain firewalls across an organization. The depth belongs to `07-security/waf-shield-firewall-manager-and-network-firewall.md`; here it is enough to know that Network Firewall inspects network and application layer traffic while DNS Firewall inspects resolver queries, and that the two cover different paths.

**Reachability Analyzer** is the first tool to reach for when connectivity is broken. It builds a model of the network configuration and checks reachability against it; it does not send packets and does not touch the data plane. You specify a source, a destination, a protocol, and optionally a destination port. When the path is reachable it returns the hop-by-hop virtual path; when it is not, it names the blocking component, which is typically a security group, a network ACL, a route table, or a load balancer. Source and destination must be in the same Region and either in the same VPC or in VPCs connected by a peering connection or a transit gateway, and they may be in different accounts in the same organization when trusted access and a delegated administrator are configured. Supported endpoints include EC2 instances, network interfaces, internet gateways, transit gateways and their attachments, virtual private gateways, VPC endpoints and endpoint services, and peering connections, plus a plain IP address as a destination. It analyzes IPv4 only, does not consider target health, and does not report paths created by traffic mirroring. Billing is per analysis.

**Network Access Analyzer** asks the opposite question: not "can A reach B" but "what can reach anything it should not". You define a Network Access Scope with `MatchPaths` describing the network paths you consider a violation and `ExcludePaths` describing legitimate exceptions, expressed by resource ID, resource type, resource tag, address range, port range, or protocol. Findings are the paths that match a `MatchPaths` entry and no `ExcludePaths` entry. Typical scopes verify that production and development VPCs are isolated, that only intended resources are reachable from an internet gateway, that every path to the internet passes through a firewall or NAT gateway, and that resources accept traffic only from trusted ranges on specific ports. Billing is per network interface analyzed. The pairing to remember is that Reachability Analyzer troubleshoots a broken path and Network Access Analyzer audits an unwanted one, and neither sends traffic, so both can be run safely in production and in a pipeline after a configuration change.

Beyond these, CloudWatch publishes NAT gateway metrics such as `ErrorPortAllocation` and `PacketsDropCount` alongside transit gateway and endpoint metrics, and **AWS CloudTrail**, the API activity audit service, records who changed a route table or a security group rule. A complete network monitoring story combines flow logs for traffic, CloudWatch for device health, CloudTrail for configuration change, and the two analyzers for intent.

## Cost shape and the quotas that bite

A VPC itself is free, as are subnets, route tables, internet gateways, egress-only internet gateways, security groups, network ACLs, peering connections, and gateway endpoints. What costs money is address occupancy, managed devices, data movement, and analysis. Every public IPv4 address is billed per hour whether attached or idle. NAT gateways bill per gateway-hour and per GB processed, the regional variant per hour for each zone it has expanded into. Interface endpoints bill per endpoint-hour in each zone and per GB processed. Transit gateways bill per attachment-hour and per GB processed. Traffic Mirroring bills per session-hour, Reachability Analyzer per analysis, Network Access Analyzer per interface analyzed, IPAM's advanced tier per active IP address per hour, and flow logs at vended-log rates.

Data transfer is the dimension that dominates a large network bill, and it is layered on top of the device charges above. Same-zone private traffic is generally free. Cross-zone traffic inside a Region is charged per GB, usually both ways. Cross-Region and internet egress are charged at higher rates. The important point is that these charges stack: a byte sent from a private subnet in one zone through a NAT gateway in another zone to the internet pays cross-zone transfer, NAT data processing, and internet egress. Moving that byte to a gateway endpoint removes all three.

The optimization sequence is therefore consistent. Put a gateway endpoint in front of S3 and DynamoDB traffic first, because it is free. Add interface endpoints for the services that carry meaningful volume, and compare their endpoint-hours against the NAT processing and egress they replace. Keep each zone's traffic inside its own zone by putting a NAT gateway, an endpoint interface, and a firewall endpoint in every zone that has workloads, or by using a regional NAT gateway. Release unused Elastic IP addresses and move instances that do not need inbound reachability out of public subnets. Consider IPv6-only subnets where the workload supports them, because IPv6 addresses are free. Then look at CloudFront or Global Accelerator for content that leaves the Region repeatedly.

The quotas that shape designs are collected here for review: 5 VPCs per Region, 200 subnets per VPC, 5 IPv4 and 5 IPv6 CIDR blocks per VPC adjustable to 50, 200 route tables per VPC, 500 non-propagated routes per route table adjustable to 1,000, 100 propagated routes per route table which is not adjustable, 2,500 security groups per Region, 60 inbound and 60 outbound rules per security group, 5 security groups per network interface adjustable to 16 with the product capped at 1,000, 200 network ACLs per VPC with 20 rules each way adjustable to 40, 5 Elastic IP addresses per Region, 5 internet gateways and 5 egress-only internet gateways per Region, 5 NAT gateways per Availability Zone, 5,000 network interfaces per Availability Zone, 100 prefix lists per Region with up to 1,000 entries each, 100 participant accounts per shared VPC, and 64,000 Network Address Usage units per VPC. All are adjustable except propagated routes per route table and the Route 53 Resolver rate of 1,024 packets per second per network interface.

## Professional depth

At organization scale the network is designed once, centrally, and consumed by everyone else. The common landing zone shape puts a network account at the center holding a transit gateway, an inspection VPC with Network Firewall or a third-party appliance fleet behind a Gateway Load Balancer, an egress VPC with NAT gateways, and a shared services VPC with Route 53 Resolver endpoints and the interface endpoints that every account uses. Workload accounts attach to the transit gateway, or use subnets shared to them from a small number of large VPCs, and their route tables send `0.0.0.0/0` to the transit gateway rather than to their own internet gateway. Transit gateway route tables provide the isolation domains, and VPC Block Public Access in every workload account makes an accidental internet gateway route ineffective.

Centralization has to be paid for and the Professional exam asks you to notice. A centralized egress VPC adds transit gateway attachment-hours and per-GB processing to every internet-bound byte, plus NAT processing and egress. For a small number of accounts with modest egress, per-account NAT gateways are cheaper and simpler; centralized egress wins when you need uniform inspection, a small set of static source addresses for partner allowlists, or when the fleet is large enough that gateway-hours dominate. Interface endpoints centralize much better: one set in a shared services VPC, reached from every attached VPC, with private DNS handled by a Route 53 private hosted zone shared across accounts, replaces one set of endpoint-hours per account per zone.

Sharing changes who can do what, and the boundaries are exam material. In a shared VPC the owner controls all routing and all subnet-level constructs, so a participant cannot create a NAT gateway, cannot modify a network ACL, and cannot attach a transit gateway. Participants can create and manage their own security groups and can reference the owner's or another participant's group as `account-number/security-group-id`, and the owner can push a baseline group to everyone with shared security groups through AWS RAM. Resource quotas count against the participant, not the owner, so one noisy account cannot exhaust another's network interface quota, but the VPC-level quotas such as subnets and Network Address Usage are shared and are the ones that run out.

Migration-scale work almost always begins with addresses. An acquisition brings VPCs that overlap your `10.0.0.0/16`, and overlapping ranges cannot be peered, cannot be attached to the same transit gateway route domain, and cannot be associated with the same Direct Connect gateway. The options are renumbering, which is slow but permanent; a private NAT gateway so that traffic leaving the overlapping VPC is translated into a non-overlapping range before it reaches the hub; or PrivateLink and VPC Lattice, which do not care about overlap because the consumer only addresses a local endpoint or a DNS name. IPAM is how you avoid creating the problem again: pools with allocation rules, non-overlap enforced at creation, and Public IP Insights to show what the public IPv4 charge is actually being paid for.

Failure modes cross layers. A path can be blocked by a missing route, an asymmetric route through a middlebox, a stale peer security group reference, a network ACL missing an ephemeral port range, an endpoint or bucket policy that denies a source VPC, a NAT gateway exhausting ports to one popular destination, an interface endpoint in only one Availability Zone, private DNS left disabled so calls still go out over NAT, or a DNS Firewall rule blocking the name first. Reachability Analyzer collapses the configuration half of that list into one call, and Network Access Analyzer proves the negative case an auditor asks about.

> **Professional depth.** A question that offers both VPC peering and a transit gateway usually hides the discriminator in one clause. "Must not be transitive" or "only these two VPCs, lowest cost" favors peering, which has no hourly charge. "Dozens of VPCs", "on-premises must reach all of them", "centralized inspection", or "add new VPCs without touching existing ones" favors a transit gateway. "The CIDR ranges overlap" rules out both and points to PrivateLink or VPC Lattice. "Different accounts, same network, conserve addresses" points to VPC sharing.

## Worked scenario

A payments company runs a customer-facing API in one Region and is expanding to a second. Regulators require that cardholder data never traverses the public internet, that every outbound flow is inspected, and that auditors can be shown evidence of isolation. Twelve product teams each have their own AWS account. The company has already used most of its `10.0.0.0/8` space and two recently acquired subsidiaries use overlapping ranges.

The network account owns a transit gateway per Region, peered across Regions, with three transit gateway route tables: production, non-production, and shared. An inspection VPC holds AWS Network Firewall endpoints in three Availability Zones with dedicated firewall subnets, and an egress VPC holds a regional NAT gateway so that outbound capacity follows workloads into new zones without route table edits. A shared services VPC holds interface endpoints for the services every account calls and Route 53 Resolver inbound and outbound endpoints for the on-premises domain. IPAM runs from a delegated administrator account with a top-level pool, Regional pools, and per-environment pools carrying allocation rules that force a `/20` maximum and non-overlap, and Public IP Insights reports the remaining public IPv4 addresses so the team can retire them.

Each product account uses subnets shared to it from two large VPCs per Region rather than owning a VPC. Its tiers follow the standard pattern: Application Load Balancers in public subnets, compute in private subnets, databases in isolated subnets, and chained security group references between them so no rule names an address. Cardholder data flows only to S3 and DynamoDB through gateway endpoints and to other services through the shared interface endpoints, with bucket policies that deny any request whose `aws:SourceVpce` is not one of those endpoints. Workload route tables send `0.0.0.0/0` to the transit gateway, VPC Block Public Access runs in bidirectional mode with exclusions only for the two load balancer subnets, and DNS Firewall blocks all domains outside an approved list to stop exfiltration by lookup. The two overlapping subsidiaries are not peered; their services are published through PrivateLink endpoint services instead, so overlap never matters. Flow logs from every VPC land in a central S3 bucket queried with Athena, Traffic Mirroring is enabled on demand for incident response, and a Network Access Analyzer scope runs nightly to prove that no path exists from an internet gateway to a database subnet.

The exam asks this scenario in two ways. The Associate version asks how instances in private subnets should reach Amazon S3 without a NAT gateway, and the keyed answer is a gateway VPC endpoint with an endpoint policy, not an interface endpoint and not a NAT gateway. The Professional version asks how to connect the two overlapping subsidiaries with the least operational overhead, and the keyed answer is to publish the needed services through PrivateLink endpoint services rather than renumbering, peering, or attaching them to the transit gateway.

## Exam lens

- "Instances in a private subnet need outbound internet access" maps to a NAT gateway with a route from the private subnet; an internet gateway alone is the distractor because a private subnet has no route to it.
- "Outbound-only internet access for IPv6 instances" maps to an egress-only internet gateway; a NAT gateway is the distractor because it is the IPv4 tool.
- "Highly available outbound access, avoid cross-zone charges" maps to one NAT gateway per Availability Zone with per-zone routing, or a regional NAT gateway; one shared NAT gateway is the distractor that creates a zonal dependency.
- "Lowest cost private access to Amazon S3 or DynamoDB from this VPC" maps to a gateway endpoint, which has no hourly or data processing charge.
- "Private access to S3 from on-premises over Direct Connect" maps to an interface endpoint, because a gateway endpoint cannot be reached from outside the VPC.
- "Private access to any other AWS service" maps to an interface endpoint with private DNS enabled in at least two Availability Zones.
- "Only requests from our network may reach this bucket" maps to a bucket policy condition on `aws:SourceVpce` or `aws:SourceVpc`, backed by an endpoint policy.
- "Allow return traffic automatically" maps to security groups; a network ACL is the distractor because it is stateless and needs an ephemeral port rule.
- "Deny one specific IP address for a whole subnet" maps to a network ACL, because security groups have no deny rules.
- "Rules that keep working as instances scale" maps to security group references rather than CIDR blocks, and across VPCs those references work over peering or a transit gateway only within one Region; a different Region is the distractor and requires a CIDR block.
- "Connect two VPCs with non-overlapping ranges at the lowest cost" maps to a VPC peering connection, which has no hourly charge.
- "Connect dozens of VPCs plus on-premises, add more without reconfiguring" maps to AWS Transit Gateway; peering is the distractor because it is not transitive.
- "VPCs have overlapping CIDR blocks" rules out peering and transit gateway attachment and maps to AWS PrivateLink or VPC Lattice.
- "Many accounts, one network, conserve address space" maps to VPC sharing through AWS RAM; the participant cannot modify subnets or route tables.
- "Plan and enforce non-overlapping CIDR blocks across an organization" maps to IPAM pools with allocation rules; a spreadsheet or tagging convention is the distractor.
- "Find why one instance cannot reach another" maps to Reachability Analyzer, which analyzes configuration without sending packets.
- "Prove no path exists from the internet to the database tier" maps to Network Access Analyzer scopes, not to flow logs.
- "Record which flows were accepted and rejected" maps to VPC Flow Logs; Traffic Mirroring is the distractor unless packet contents are required.
- "Prevent data exfiltration through DNS lookups" maps to Route 53 Resolver DNS Firewall; AWS Network Firewall is the distractor because it does not see resolver queries.
- "Reduce the cost of public IPv4 addresses" maps to releasing unused Elastic IP addresses, moving instances behind load balancers and NAT, or adopting IPv6, because every public IPv4 address is billed hourly.

## Knowledge check

### 1. Reaching object storage from a private subnet (Associate)

An application runs on EC2 instances in private subnets in a single VPC and writes several terabytes a month to an Amazon S3 bucket in the same Region. The instances currently reach S3 through a NAT gateway. The security team requires that the traffic never traverse the internet, and the finance team wants the network cost of this traffic reduced.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Create an interface VPC endpoint for Amazon S3 in each Availability Zone and enable private DNS.
- **B)** Create a gateway VPC endpoint for Amazon S3 and associate it with the private subnets' route tables.
- **C)** Assign Elastic IP addresses to the instances and route `0.0.0.0/0` to the internet gateway.
- **D)** Create a second NAT gateway in each Availability Zone and split the instances between them.

<details><summary>Answer</summary>

**Answer: B.** A gateway endpoint adds a route for the S3 prefix list, keeps the traffic on the AWS network, and has no hourly or data processing charge, so it removes both the NAT processing charge and the egress charge. A works and is private, but an interface endpoint bills per endpoint-hour in each Availability Zone plus per GB, so it is more expensive than the free gateway endpoint when every client is inside the VPC. C makes the instances publicly addressable, adds a per-hour charge for every public IPv4 address, and sends traffic out through the internet gateway. D increases NAT capacity and cost without removing either the data processing charge or the path out of the VPC.

*Where this is covered: VPC endpoints: gateway, interface, and AWS PrivateLink.*

</details>

### 2. Outbound access that survives a zone failure (Associate)

A company runs application servers in private subnets across three Availability Zones in one Region. All three subnets currently route `0.0.0.0/0` to a single NAT gateway in the first zone. During a recent zone impairment, servers in the other two zones lost internet access, and the monthly bill shows a large cross-Availability-Zone data transfer line.

Which solution will meet these requirements?

- **A)** Increase the size of the existing NAT gateway and add a second Elastic IP address to it.
- **B)** Replace the NAT gateway with a NAT instance in the first zone and enable detailed monitoring.
- **C)** Create a NAT gateway in each Availability Zone and point each private subnet's route table at the NAT gateway in its own zone.
- **D)** Route `0.0.0.0/0` from all three private subnets to the internet gateway.

<details><summary>Answer</summary>

**Answer: C.** A NAT gateway is redundant only inside its own Availability Zone, so zone independence requires one per zone with per-zone routing, which also keeps the traffic from crossing a zone boundary and removes the cross-zone charge. A is impossible because a NAT gateway has no size to choose, and extra addresses raise the connection limit, not availability. B replaces a managed device with one you must patch and fail over yourself and leaves the single-zone dependency in place. D makes the subnets public and still fails, because instances without public addresses have nothing for the internet gateway to translate.

*Where this is covered: NAT gateways, NAT instances, and the per-Availability-Zone decision.*

</details>

### 3. Outbound-only access for IPv6 workloads (Associate)

A company has added an Amazon-provided IPv6 CIDR block to a VPC and assigned IPv6 addresses to instances in private subnets. The instances must download operating system patches from the internet over IPv6, but nothing on the internet may initiate a connection to them.

Which solution will meet these requirements?

- **A)** Create an egress-only internet gateway and add a route for `::/0` in the private subnets' route tables.
- **B)** Create a public NAT gateway and add a route for `::/0` to it in the private subnets' route tables.
- **C)** Attach an internet gateway and add a route for `::/0` to it, then block inbound traffic with a network ACL.
- **D)** Create an interface VPC endpoint and enable private DNS for the patch repository.

<details><summary>Answer</summary>

**Answer: A.** An egress-only internet gateway is the stateful, IPv6-only device that allows outbound connections and their responses while preventing the internet from initiating a connection inward. B is wrong because a NAT gateway performs IPv4 translation and NAT64, and is not the outbound-only device for native IPv6 traffic. C exposes the instances at the routing layer and relies entirely on a stateless filter that must also be maintained for ephemeral ports, which is what the egress-only gateway exists to avoid. D provides a private path to supported AWS services, not to a public patch repository.

*Where this is covered: Route tables, internet gateways, and egress-only internet gateways.*

</details>

### 4. A subnet filter that drops responses (Associate)

A team associates a custom network ACL with a web subnet. Rule 50 outbound denies all traffic to `0.0.0.0/0`, rule 100 inbound allows TCP 443 from `0.0.0.0/0`, and rule 100 outbound allows TCP 443 to `0.0.0.0/0`. Team convention is to add every new rule at a number above 200. Instance security groups allow inbound TCP 443 from the load balancer. Users report that every HTTPS request times out, although the instances are healthy.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Add an inbound network ACL rule allowing TCP 1024 through 65535 from `0.0.0.0/0`.
- **B)** Add an outbound network ACL rule allowing TCP 1024 through 65535 to `0.0.0.0/0`.
- **C)** Add an outbound rule to the instance security group allowing TCP 1024 through 65535.
- **D)** Renumber the outbound deny-all rule from 50 to 400 so that lower-numbered allow rules are evaluated first.
- **E)** Replace the network ACL with a security group associated with the subnet.

<details><summary>Answer</summary>

**Answer: B and D.** Two separate edits are needed. A network ACL is stateless, so the response to an inbound request leaves on an ephemeral port and needs an explicit outbound allow rule. Rules are also evaluated in ascending number order until one matches, so while the deny-all sits at 50 and team convention numbers new rules above 200, that new allow rule would never be reached; moving the deny to 400 lets the allow rules evaluate first. A allows inbound ephemeral traffic, which is not the direction that is failing. C is unnecessary because a security group is stateful and already permits the response, and because the default outbound rule allows all traffic anyway. E is impossible: security groups attach to network interfaces, not to subnets.

*Where this is covered: Security groups compared with network ACLs.*

</details>

### 5. Segmenting a three-tier application (Associate)

A company is designing a public web application with an Application Load Balancer, a fleet of EC2 instances that scales in and out, and an Amazon RDS database. The database must not be reachable from the internet under any circumstance, and the rules must keep working as instances are replaced by scaling events.

Which solution will meet these requirements?

- **A)** Place all three tiers in public subnets and restrict the database security group to the VPC CIDR block.
- **B)** Place the load balancer and instances in public subnets and the database in a private subnet, allowing the database security group to accept traffic from the VPC CIDR block.
- **C)** Place all three tiers in private subnets and give the load balancer an Elastic IP address.
- **D)** Place the load balancer in public subnets, the instances in private subnets, and the database in subnets with no internet route, and have each tier's security group reference the security group of the tier in front of it.

<details><summary>Answer</summary>

**Answer: D.** Routing provides the isolation, because the database subnets have no path outward, and chained security group references follow group membership rather than addresses, so scaling events change nothing. A leaves every tier on a subnet with an internet gateway route, which is exactly what the requirement forbids. B still places the instances in public subnets unnecessarily and uses a CIDR block that grants access to everything in the VPC rather than to the application tier. C cannot work, because an internet-facing load balancer must be placed in subnets with an internet gateway route, and an Application Load Balancer does not take an Elastic IP address.

*Where this is covered: Subnets, network segmentation, and the multi-tier pattern.*

</details>

### 6. An unexpected addressing charge (Associate)

A cost review finds a large recurring line item for public IPv4 addresses. The environment has 400 EC2 instances, each launched into a public subnet with an automatically assigned public IPv4 address, although only a load-balanced subset serves inbound traffic. It also holds 60 allocated Elastic IP addresses that are not associated with any resource.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Move all instances to a larger instance family to reduce the instance count.
- **B)** Convert the Elastic IP addresses to automatically assigned public IPv4 addresses.
- **C)** Release the unassociated Elastic IP addresses and move instances that need only outbound access into private subnets behind a NAT gateway.
- **D)** Request a quota increase for Elastic IP addresses per Region.

<details><summary>Answer</summary>

**Answer: C.** Since February 1, 2024 every public IPv4 address is billed hourly whether it is attached or idle, so the fix is to stop holding addresses that nothing uses and to stop assigning addresses to instances that only make outbound connections. A changes compute cost and does not address the charge, which is per address rather than per instance. B is wrong because automatically assigned public addresses carry the same hourly charge as Elastic IP addresses. D raises a limit rather than reducing usage and would increase the bill.

*Where this is covered: Elastic IP addresses, public IPv4 charges, IPAM, and BYOIP.*

</details>

### 7. Finding out why a connection fails (Associate)

An operations team cannot connect from an EC2 instance in one subnet to a database instance in another subnet of the same VPC. They need to identify the specific component that is blocking the path without generating traffic against the production database and without installing agents.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Run VPC Reachability Analyzer between the source network interface and the destination, specifying the protocol and destination port.
- **B)** Enable VPC Flow Logs on both subnets and query the records in Amazon Athena.
- **C)** Create a Traffic Mirroring session from the source instance to a packet analyzer behind a Network Load Balancer.
- **D)** Create a Network Access Analyzer scope that matches paths from the source to the destination.

<details><summary>Answer</summary>

**Answer: A.** Reachability Analyzer models the configuration without sending packets and, when a path is unreachable, names the blocking security group, network ACL, route table, or load balancer directly. B records only traffic that is actually attempted and shows a REJECT without saying which construct caused it, and it produces nothing until traffic flows. C copies real packets to an appliance, which is heavier, adds session-hour charges, and still requires traffic to exist. D audits which paths exist against a stated intent and is the wrong tool for diagnosing one broken connection.

*Where this is covered: Traffic visibility, inspection, and troubleshooting.*

</details>

### 8. Connecting an acquisition with overlapping addresses (Professional)

A company acquires two businesses whose VPCs both use `10.0.0.0/16`, the same range as the company's production VPC. Three internal HTTPS APIs in the production VPC must be reachable from workloads in both acquired VPCs within two weeks. Renumbering either acquired network is not possible in that time, and the company will not expose the production VPC's full address space to either party.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create inter-Region VPC peering connections between the production VPC and each acquired VPC and add routes for the API subnets.
- **B)** Attach all three VPCs to a transit gateway and use separate transit gateway route tables for isolation.
- **C)** Deploy a private NAT gateway in each acquired VPC and peer the VPCs through it.
- **D)** Publish each API behind a Network Load Balancer as a PrivateLink endpoint service and have each acquired VPC create an interface endpoint.

<details><summary>Answer</summary>

**Answer: D.** PrivateLink exposes only the named services, works when consumer and provider ranges overlap because the consumer addresses a local endpoint interface, and scales to more consumers without routing coordination. A cannot be created at all, because VPC peering rejects overlapping CIDR blocks regardless of Region. B fails for the same reason: a transit gateway cannot route between attachments with overlapping ranges in one route domain, and route table separation does not solve address overlap. C is a real technique for overlapping networks but requires a transit gateway or virtual private gateway path rather than peering, needs address planning for the translated range, and exposes more than the three APIs.

*Where this is covered: PrivateLink endpoint services and Amazon VPC Lattice.*

</details>

### 9. One network for twelve teams (Professional)

A company with twelve AWS accounts in one organization is running short of RFC 1918 address space and is paying significant inter-VPC data transfer charges because every account has its own VPC connected through a transit gateway. The teams' workloads are inside the same trust boundary and communicate constantly. A central network team must keep exclusive control of routing, NAT, and network ACLs, while each team keeps its own billing and its own IAM boundary.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Create VPC peering connections in a full mesh between the twelve VPCs and delete the transit gateway.
- **B)** Have the network account own two large VPCs per Region and share subnets with the twelve accounts through AWS Resource Access Manager.
- **C)** Consolidate all twelve accounts into one account and one VPC.
- **D)** Create a VPC Lattice service network and associate all twelve VPCs with it.

<details><summary>Answer</summary>

**Answer: B.** VPC sharing places every team's resources in one owner-controlled VPC, so traffic between them uses the implicit local route with no attachment-hours and no inter-VPC processing charge, address space is numbered once, participants keep their own billing and IAM boundary, and only the owner can touch subnets, route tables, NAT gateways, and network ACLs. A replaces one hub with 66 peering connections, does not conserve address space, and still charges cross-zone transfer. C destroys the per-team billing and IAM separation the requirement keeps. D connects services rather than networks, which suits loosely coupled microservices but neither conserves address space nor gives the network team control of routing.

*Where this is covered: Connecting VPCs: peering, Transit Gateway, and VPC sharing.*

</details>

### 10. Rules that survive scaling and a peering connection (Associate)

Two VPCs in the same Region and the same account are joined by a VPC peering connection that was created some time ago. Instances in VPC A must reach a database fleet in VPC B on TCP 5432. The fleet scales in and out several times a day, and the team does not want to edit rules when addresses change. Both route tables already contain routes to the peer CIDR blocks.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** In the VPC B database security group, add an inbound rule for TCP 5432 whose source is the VPC A application security group ID.
- **B)** In the VPC B database security group, add an inbound rule for TCP 5432 whose source is the VPC A CIDR block, and update it whenever instances change.
- **C)** Confirm that the peering connection is in the `active` state, since a security group reference requires it and becomes stale if the connection is deleted.
- **D)** Enable security group referencing on the transit gateway and on both VPC attachments.
- **E)** Create an interface VPC endpoint in VPC A for the database in VPC B.

<details><summary>Answer</summary>

**Answer: A and C.** Across a peering connection in the same Region, a security group rule can name the peer security group directly, so the rule follows membership instead of addresses, and that reference is valid only while the peering connection is active, becoming a stale rule that must be removed manually if the connection is deleted. B works but requires exactly the manual edits the requirement rules out and grants access to everything in VPC A. D describes the transit gateway feature, and there is no transit gateway in this design. E would provide a private path but replaces a working peering connection with a load balancer and endpoint service that nobody has built.

*Where this is covered: Security groups compared with network ACLs.*

</details>

### 11. Address planning across an organization (Professional)

A company with 180 AWS accounts across five Regions has repeatedly discovered overlapping CIDR blocks only when a transit gateway attachment or a Direct Connect gateway association fails. A central team must allocate non-overlapping ranges automatically, enforce a maximum subnet size per environment, report utilization per account and Region, and see which public IPv4 addresses are in use so they can be retired.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Maintain a spreadsheet of allocations and require a change ticket before any VPC is created.
- **B)** Apply a tagging standard for CIDR blocks and write an AWS Config rule that flags overlaps after creation.
- **C)** Deploy Amazon VPC IP Address Manager with a delegated administrator account, a nested pool hierarchy with allocation rules, and Public IP Insights on the advanced tier.
- **D)** Give each account a `/16` from a different RFC 1918 range and forbid secondary CIDR blocks.

<details><summary>Answer</summary>

**Answer: C.** IPAM allocates CIDR blocks from governed pools at creation time so overlap cannot happen, allocation rules enforce minimum and maximum netmasks per pool, the delegated administrator sees utilization for every account and Region, and Public IP Insights lists the public IPv4 addresses that are now billed hourly. A is manual and is the process that already failed. B detects the problem after the VPC exists, which is too late because a primary CIDR cannot be changed. D exhausts RFC 1918 space long before 180 accounts across five Regions are covered and cannot enforce environment-level sizing or report public address usage.

*Where this is covered: Elastic IP addresses, public IPv4 charges, IPAM, and BYOIP.*

</details>

### 12. Proving isolation and stopping exfiltration (Professional)

An auditor asks a regulated company to demonstrate, on a recurring schedule, that no network path exists from any internet gateway to the subnets holding cardholder data. A separate incident review found that a compromised instance in a private subnet had encoded data into DNS lookups against an attacker-controlled domain, and that traffic left through the shared NAT gateway.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable VPC Flow Logs on the cardholder subnets and have the auditor review the ACCEPT and REJECT records each quarter.
- **B)** Create a Network Access Analyzer scope with `MatchPaths` from resource type `AWS::EC2::InternetGateway` to the cardholder subnets, and run the analysis on a schedule.
- **C)** Create a Traffic Mirroring session from every instance in the cardholder subnets to a packet analyzer.
- **D)** Replace the shared NAT gateway with one NAT gateway per Availability Zone.
- **E)** Associate a Route 53 Resolver DNS Firewall rule group with the VPCs that blocks all domains outside an approved allowlist.

<details><summary>Answer</summary>

**Answer: B and E.** A Network Access Analyzer scope states the intent as a matched path and produces findings only when such a path exists, which is exactly the recurring evidence an auditor wants, and DNS Firewall filters outbound queries at the VPC resolver, which is where DNS exfiltration is stopped. A proves only that observed traffic was rejected, not that no path exists, and flow logs never record queries to the Amazon DNS server. C copies packets for inspection at a per-session-hour charge and still proves nothing about paths that were never used. D improves availability and cross-zone cost but does nothing for either requirement, and AWS Network Firewall would not see resolver queries either.

*Where this is covered: Traffic visibility, inspection, and troubleshooting.*

</details>

## Summary

A VPC question is a sequence of decisions. Choose the Region for latency, residency, features, and price, then spread subnets across at least two Availability Zones, because a subnet is zonal while a VPC is Regional. Choose address space that will not need to change, because a primary CIDR is permanent and overlapping ranges block peering, transit gateway routing, and Direct Connect gateway association. Make subnets public, private, or isolated through route tables alone, where longest prefix match decides every routing question. Provide outbound access with NAT gateways per zone or a regional NAT gateway, and an egress-only internet gateway for IPv6. Filter with stateful security groups that reference other security groups, adding network ACLs only as a coarse guardrail. Reach AWS services privately with a free gateway endpoint for S3 and DynamoDB and interface endpoints for the rest, and expose your own with PrivateLink or VPC Lattice when ranges overlap. Connect VPCs with peering when there are few, a transit gateway when many, and VPC sharing when they should have been one network. Watch it with flow logs and the two analyzers, and remember that public IPv4 addresses, NAT processing, endpoint-hours, and cross-zone transfer are where the money goes.

## Related units

- [Hybrid connectivity](hybrid-connectivity.md): Direct Connect, Site-to-Site VPN, Transit Gateway in depth, Cloud WAN, and hybrid DNS
- [Amazon Route 53](route53.md): private hosted zones, Resolver endpoints, routing policies, and health checks
- [Amazon CloudFront](cloudfront.md): edge delivery and private origins that reduce egress from the VPC
- [AWS Global Accelerator](global-accelerator.md): static anycast entry points compared with DNS-based routing
- [Amazon API Gateway](api-gateway.md): private REST APIs reached through interface endpoints and endpoint policies
- [Amazon S3](../01-storage/s3.md): the gateway endpoint target and bucket policy conditions on source VPC and endpoint
- [AWS WAF, Shield, Firewall Manager and Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md): the inspection services this unit introduces and defers to

## Sources

- [Network ACLs and ephemeral ports](https://docs.aws.amazon.com/vpc/latest/userguide/custom-network-acl.html): the documented ephemeral port ranges per client type
- [DHCP option sets](https://docs.aws.amazon.com/vpc/latest/userguide/DHCPOptionSet.html): immutability, one set per VPC, and that no restart is needed
- [Traffic mirroring targets](https://docs.aws.amazon.com/vpc/latest/mirroring/traffic-mirroring-targets.html): supported target types
- [Amazon VPC pricing](https://aws.amazon.com/vpc/pricing/): the IPAM tier split, NAT gateway and public IPv4 charge shapes
- [Security group sharing](https://docs.aws.amazon.com/vpc/latest/userguide/security-group-sharing.html): sharing security groups through AWS RAM and its restrictions

- [IP addressing for your VPCs and subnets](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-ip-addressing.html): private and public IPv4, the public IPv4 charge, public and private IPv6, and BYOIP
- [VPC CIDR blocks](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html): /16 to /28 sizing, secondary CIDR association restrictions, and IPv6 block sizes
- [Subnet CIDR blocks](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html): subnet netmask range and the five reserved addresses in every subnet
- [Amazon VPC quotas](https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html): every default quota and whether it is adjustable, including Network Address Usage and shared subnet limits
- [How route priority works](https://docs.aws.amazon.com/vpc/latest/userguide/route-tables-priority.html): longest prefix match and the static, prefix list, propagated ordering
- [What is Network Access Analyzer?](https://docs.aws.amazon.com/vpc/latest/network-access-analyzer/what-is-network-access-analyzer.html): Network Access Scopes, MatchPaths and ExcludePaths, and findings
- [Enable outbound IPv6 traffic using an egress-only internet gateway](https://docs.aws.amazon.com/vpc/latest/userguide/egress-only-internet-gateway.html): IPv6-only stateful behavior and `::/0` routing
- [NAT gateway basics](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-basics.html): bandwidth, packet rate, 55,000 connections per address, ports, and per-zone guidance
- [Regional NAT gateways for automatic multi-AZ expansion](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateways-regional.html): automatic zone expansion, 32 addresses per zone, and the private NAT limitation
- [Compare NAT gateways and NAT instances](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-comparison.html): the full attribute-by-attribute comparison table
- [AWS Free Tier now includes 750 hours of free Public IPv4 addresses](https://aws.amazon.com/about-aws/whats-new/2024/02/aws-free-tier-750-hours-free-public-ipv4-addresses/): the February 1, 2024 charge start and the free tier allowance
- [How IPAM works](https://docs.aws.amazon.com/vpc/latest/ipam/how-it-works-ipam.html): public and private scopes, nested pools, and allocations
- [Infrastructure security in Amazon VPC](https://docs.aws.amazon.com/vpc/latest/userguide/infrastructure-security.html): the security group and network ACL comparison table and which to use first
- [Update your security groups to reference peer security groups](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-security-groups.html): same-Region requirement, cross-account syntax, and stale rules
- [General availability for Security Group Referencing on AWS Transit Gateway](https://aws.amazon.com/about-aws/whats-new/2024/09/general-availability-security-group-referencing-aws-transit-gateway/): inbound-only referencing across a transit gateway and its cost
- [Amazon VPC attachments in AWS Transit Gateway](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-vpc-attachments.html): security group referencing limits across a transit gateway, and appliance mode
- [Block public access to VPCs and subnets](https://docs.aws.amazon.com/vpc/latest/userguide/security-vpc-bpa.html): bidirectional and ingress-only modes and exclusion modes
- [Gateway endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html): Amazon S3 and DynamoDB only, prefix list routing, no charge, and route precedence
- [Access AWS services through AWS PrivateLink](https://docs.aws.amazon.com/vpc/latest/privatelink/privatelink-access-aws-services.html): interface endpoint pricing shape, private DNS, and Availability Zone guidance
- [What is Amazon VPC Lattice?](https://docs.aws.amazon.com/vpc-lattice/latest/ug/what-is-vpc-lattice.html): service networks, auth policies, zone affinity, and pricing dimensions
- [How VPC peering connections work](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-basics.html): overlapping CIDR, transitive peering, edge-to-edge routing, and inter-Region limits
- [Responsibilities and permissions for owners and participants](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-share-limitations.html): exactly what a shared VPC participant can and cannot do
- [Using DNS Firewall to filter outbound DNS traffic](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall.html): rule groups, exfiltration prevention, and how it differs from Network Firewall
- [Flow log limitations](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html): immutable configuration and the full list of traffic that is never logged
- [How Reachability Analyzer works](https://docs.aws.amazon.com/vpc/latest/reachability/how-reachability-analyzer-works.html): configuration-only analysis, supported resources, and the same-Region limit
