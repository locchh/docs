# AWS hybrid and multi-network connectivity

**Where it sits on the exams.** **AWS Direct Connect** is the private circuit service from a customer network to AWS, **AWS Site-to-Site VPN** is the managed Internet Protocol Security (IPsec) tunnel service, and **AWS Transit Gateway** is a Regional router connecting **Amazon VPC**, the isolated virtual network service, and external networks. **AWS Client VPN** provides managed remote-user access, **AWS Cloud WAN** applies global network policy, **Amazon Route 53 VPC Resolver** provides hybrid DNS, and **AWS PrivateLink** privately publishes services without routed network access. Together they form the topology tested in SAA-C03 tasks 1.2, 3.4 and 4.4 and SAP-C02 tasks 1.1 and 4.2. The rule of thumb is to separate transport from routing: Direct Connect or a VPN supplies a path into AWS; a virtual private gateway terminates that path for one VPC; Transit Gateway or Cloud WAN distributes it across many networks.

## Choose the transport, then choose the router

A hybrid design has two independent decisions. The transport decision asks how bits cross from the customer network to AWS. Site-to-Site VPN uses the public internet and encrypts traffic end to end. Direct Connect uses a dedicated physical path through a Direct Connect location and avoids the public internet, but it does not encrypt traffic by default. The routing decision asks which AWS resource advertises and learns prefixes. A **virtual private gateway (VGW)** is the VPC-side gateway for a single VPC. A Transit Gateway is a hub for many VPCs, VPNs and Direct Connect gateways. Confusing these layers produces answers that name a circuit but never connect it to a VPC.

Read this table from the requirement in the first column. Several rows deliberately combine a transport and a routing hub because an exam answer must include both halves.

| Requirement | Primary design | Why it wins |
|---|---|---|
| Connect one VPC quickly with encryption | Site-to-Site VPN to a VGW | Deploys without waiting for a private circuit |
| Stable private bandwidth to one or a few VPCs | Direct Connect private virtual interface through a Direct Connect gateway to VGWs | Private path with reusable global gateway associations |
| Many VPCs plus on-premises networks | Transit virtual interface through a Direct Connect gateway to Transit Gateway | One regional routing hub provides transitive connectivity |
| Encrypt traffic while retaining private Direct Connect transport | Private IP Site-to-Site VPN over a transit virtual interface | IPsec supplies end-to-end encryption over Direct Connect |
| Remote individual users | AWS Client VPN | Managed OpenVPN-based client access rather than a site tunnel |
| Global policy across Regions and branches | AWS Cloud WAN core network | One global network policy and segmented core network |
| Private access to one producer service in many consumer VPCs | AWS PrivateLink | Exposes a service, not a routed network |
| Resolve on-premises names from VPCs and AWS private names on premises | Route 53 Resolver outbound and inbound endpoints | Conditional DNS forwarding in both directions |

No one transport satisfies availability by its name alone. One Direct Connect connection is one physical failure domain. One Site-to-Site VPN connection includes two tunnels, but a customer gateway using only one has thrown away the managed redundancy. For critical workloads, use independent devices and locations and make route preference intentional. A common design uses Direct Connect as the preferred route and VPN as backup by advertising the same prefixes with Border Gateway Protocol (BGP) attributes that favor Direct Connect.

Cost follows the boundaries. Direct Connect bills port-hours and data transfer out, plus the provider circuit that AWS does not sell. VPN bills per connection-hour and data transfer, with additional charges for acceleration when enabled. Transit Gateway bills attachment-hours and data processing. Cloud WAN adds core network edge and data-processing charges. PrivateLink bills endpoint-hours and processed bytes. The cheapest diagram is therefore not automatically the cheapest topology: centralizing every flow through a hub can add processing and cross-Availability Zone charges, while duplicating endpoints or gateways trades hourly cost for local paths and fault isolation.

## Direct Connect connections and virtual interfaces

A Direct Connect location is a colocation facility where the customer or a network provider cross-connects a router to an AWS device. A dedicated connection is a physical Ethernet port assigned to one customer and ordered from AWS at 1, 10, 100 or 400 Gbps. AWS supplies a Letter of Authorization and Connecting Facility Assignment (LOA-CFA), but the customer arranges the circuit from its premises to that location. The port speed cannot be changed in place. A hosted connection is provisioned by a Direct Connect Partner from its own capacity. Current hosted speeds range from 50 Mbps through 25 Gbps, availability depends on the partner and location, and a partner may support changing the hosted capacity.

The physical connection alone reaches no service. An 802.1Q VLAN and a BGP session form a **virtual interface (VIF)** on it. Direct Connect supports three types, and each has a distinct destination.

| Virtual interface | Reaches | Addressing and exam signal |
|---|---|---|
| Private VIF | A VPC through its VGW, or VGWs associated with a Direct Connect gateway | Private IP connectivity to VPC resources |
| Public VIF | AWS public service endpoints, such as the public Amazon S3 endpoint | Public prefixes over a private circuit, not private VPC addresses |
| Transit VIF | Transit Gateways through a Direct Connect gateway | Many VPCs, transitive routing and private IP VPN over Direct Connect |

**Border Gateway Protocol (BGP)** is the dynamic routing protocol on every VIF. The customer router and AWS router advertise prefixes and use an autonomous system number (ASN), with MD5 authentication on the peering session. A VIF can carry IPv4, IPv6 or one BGP session for each family. A private or transit VIF can use a 1,500-byte maximum transmission unit (MTU) or jumbo frames; every device on the path must support the selected size or large packets disappear in ways that look like application failures.

A private VIF attached directly to a VGW reaches one VPC in the same Region. Insert a Direct Connect gateway when the same private VIF must reach VGWs in other Regions or accounts. A transit VIF always uses a Direct Connect gateway before reaching Transit Gateway. A public VIF advertises AWS public prefixes globally and requires customer-owned public prefixes for the BGP advertisement; it does not turn an **Amazon S3**, the managed object storage service, public endpoint into a private address. Prefer an S3 gateway endpoint for VPC traffic that need not traverse the customer network, and use a public VIF when on-premises systems need a predictable Direct Connect path to public AWS endpoints.

Hosted VIF and hosted connection are different. A partner can allocate a hosted VIF on a connection the partner owns, while a hosted connection gives the customer a dedicated logical connection at a chosen capacity. In either case, confirm which account owns the connection, VIF and data-transfer charge. A VIF may be created for another AWS account, which must accept it before use. This is useful when a network account owns the physical connectivity and application accounts own the receiving gateway.

Direct Connect is private transport, not encryption. Workloads that require end-to-end encryption can run application-layer Transport Layer Security (TLS), build an ordinary public IP VPN over a public VIF, or use private IP Site-to-Site VPN over a transit VIF and Transit Gateway. MAC Security protects only the local Ethernet hop to the Direct Connect device and is a different control, covered with physical resilience below.

## Direct Connect gateways and route control

A **Direct Connect gateway (DXGW)** is a global BGP route-reflector resource that links VIFs to VGWs, Transit Gateways or an AWS Cloud WAN core network. It is not a packet-processing appliance and does not create a throughput bottleneck. A private VIF associates with VGWs through the DXGW; a transit VIF associates with Transit Gateways. The same gateway can be owned by a central network account while accepting association proposals from gateways in other accounts.

The DXGW removes the same-Region restriction of a private VIF, but it is not a global transit router. Two VPCs whose VGWs associate with one DXGW cannot use it to exchange traffic with each other. Likewise, a DXGW association does not make VPC CIDRs transitive through an on-premises router unless the route advertisements and security policy deliberately support that path. Use Transit Gateway peering or Cloud WAN when VPC-to-VPC connectivity is the requirement.

Allowed prefixes on a DXGW association are route filters, not routes installed into a VPC. For a VGW association, AWS advertises only VPC prefixes that fall within the allowed-prefix list toward on premises. For a Transit Gateway association, the allowed prefixes are advertised from the DXGW toward the transit VIF, while the Transit Gateway route table still decides which attachments can reach them. An overly broad filter can expose more networks than intended; an overly narrow one produces an established BGP session with missing reachability.

Routing preference is a design input, not a side effect to discover during failure. For traffic from on premises to AWS, use longer-prefix matching first, then BGP attributes supported by Direct Connect. For traffic from AWS toward on premises, AWS evaluates the route source and BGP attributes documented for the gateway type. Advertise identical prefixes over redundant paths only after deciding active-active or active-passive behavior. AS-path prepending can make a backup less preferred, and Direct Connect BGP communities can influence local preference on supported VIFs.

For private and transit VIFs, AWS evaluates longest prefix first, then local preference, AS-path length and Multi-Exit Discriminator (MED) in that order for outbound path selection. AWS recommends its local-preference communities when equal-length advertisements must form an active-passive design: `7224:7300` is high, `7224:7200` medium and `7224:7100` low. Equal prefix lengths and equal attributes can instead form active-active ECMP paths. A common mistake is prepending the AS path on a backup while assigning it a higher local-preference community; local preference wins before the prepend is considered. Control the customer-to-AWS direction separately on the customer routers, because a community influencing AWS return traffic does not choose the path packets take into AWS.

A Direct Connect gateway does not terminate a Site-to-Site VPN by itself. A public IP VPN terminates at a VGW or Transit Gateway and may traverse a public VIF. A private IP VPN requires Transit Gateway, a transit VIF and a DXGW. This distinction is a frequent Professional-level discriminator: the answer that says "attach the VPN to the Direct Connect gateway" is incomplete because the VPN terminates on Transit Gateway.

## Physical resilience, LAGs, MACsec and SiteLink

The **Direct Connect Resiliency Toolkit** is the connection wizard and failover-test workflow for building known failure domains. Its current models make the topology explicit. Maximum resiliency targets the 99.99 percent service level agreement (SLA) requirements with connections on separate devices in more than one Direct Connect location. High resiliency targets the 99.9 percent SLA with two single connections across multiple locations. Development and test uses separate devices in one location, protecting against a device failure but not a location failure. The failover test temporarily takes down selected BGP sessions so the team can prove traffic uses the surviving VIF instead of trusting a diagram.

A **link aggregation group (LAG)** uses Link Aggregation Control Protocol (LACP) to operate several dedicated connections as one logical interface. Every member has the same bandwidth and terminates on the same AWS device at the same Direct Connect location. Connections are active-active. A minimum-links setting can take the whole LAG down when too few members remain, preventing the surviving links from becoming overloaded. A LAG increases bandwidth and protects against a member-link failure, but because its members share a device and location it does not replace the second location required for site resilience. AWS does not support multi-chassis LAG.

LAG membership has current hard shapes worth recognizing: dedicated connections only, up to four members below 100 Gbps, or up to two members at 100 or 400 Gbps. A design requiring four 100-Gbps circuits therefore needs more than one LAG. Each physical member still counts against the connection quota and incurs its own port-hour charge.

**MAC Security (MACsec)** provides layer 2 encryption, integrity and origin authentication between the customer edge router and the Direct Connect device. It is not end-to-end encryption across the AWS network or the provider path before that cross-connect. MACsec is supported on selected 10, 100 and 400 Gbps dedicated connections and on qualifying LAGs, not on customer hosted connections. The `must_encrypt` mode stops traffic if encryption cannot be established; `should_encrypt`, the default for a newly MACsec-enabled connection, can fall back to unencrypted traffic. Choose the former when plaintext is prohibited and design a separate redundant path so a key or negotiation fault does not become an outage.

**Direct Connect SiteLink** carries traffic between Direct Connect points of presence over the AWS global network without detouring through an AWS Region. Enable it on supported private or transit VIFs when branches connected at different Direct Connect locations need private any-to-any transport. It adds a SiteLink data-processing charge and uses BGP path selection between locations. Public VIFs and private VIFs attached directly to a VGW do not support it. SiteLink solves branch-to-branch transport; it does not replace a Transit Gateway for routing among VPC attachments or Cloud WAN for global segmentation policy.

## Site-to-Site VPN, acceleration and bandwidth

A Site-to-Site VPN connection joins a customer gateway device to either a VGW, Transit Gateway or Cloud WAN. The **customer gateway** resource in AWS describes the on-premises router, including its outside address and BGP ASN; it is not the physical device itself. AWS creates two IPsec tunnels to distinct AWS endpoints. Configure and monitor both. If the customer router establishes only the first tunnel, routine AWS maintenance on that endpoint becomes an outage even though the service delivered two paths.

Dynamic routing uses BGP and adapts when a tunnel or advertised route disappears. Static routing requires the operator to enter remote prefixes and is appropriate only for devices that cannot run BGP or for very simple fixed networks. A VGW connects the VPN to one VPC and supports IPv4 traffic inside the tunnels. A Transit Gateway attachment connects the VPN transitively to many VPCs and supports IPv4 or IPv6 inner traffic; current Transit Gateway and Cloud WAN VPNs can also use IPv6 outer tunnel addresses. This is an example of a capability claim that has moved beyond older exam material: when an exam stem is generic, the classic IPv4 design remains sufficient, but a present-day requirement for IPv6 selects Transit Gateway or Cloud WAN rather than a VGW.

Each standard VPN tunnel supports up to 1.25 Gbps under ideal conditions, not a guaranteed application rate. Packet size, protocol, internet conditions and the customer device all affect realized throughput. The VPN path does not support jumbo frames or Path MTU Discovery; its current maximum transmission unit is 1,446 bytes with a 1,406-byte maximum segment size. Clamp TCP MSS and test large packets when small probes work but application sessions stall.

Current AWS documentation also defines large-bandwidth VPN tunnels, which reach up to 5 Gbps per tunnel and are managed through a Site-to-Site VPN Concentrator. The SAA-C03 and SAP-C02 guides predate this capability, so an exam question that contrasts one standard VPN with several connections still expects the established bandwidth-scaling rule unless it explicitly names the newer tunnel type. Architecturally, do not claim that every VPN tunnel is permanently capped at 1.25 Gbps.

Transit Gateway can use equal-cost multipath (ECMP) across dynamic-routing VPN tunnels. Several tunnels advertising equal prefixes can therefore aggregate bandwidth and distribute flows, while a VGW chooses one preferred path and cannot provide this horizontal scaling pattern. ECMP requires BGP; static VPN routes do not qualify. Because hashing operates per flow, one long-lived flow remains limited by one tunnel even when aggregate throughput rises. Use independent customer devices and VPN connections when the design also needs protection from an on-premises appliance failure.

An **accelerated Site-to-Site VPN** uses **AWS Global Accelerator**, the edge routing service, to enter the AWS global network near the customer gateway, avoiding more of the public internet. AWS manages two accelerators, one per tunnel. Acceleration is available only for new VPN attachments to Transit Gateway, not VGW connections, cannot be enabled or disabled in place, and cannot run over a Direct Connect public VIF. It adds hourly and data-processing charges. Choose it for internet-based sites whose long-distance public path is unstable or high latency; it adds little value when the customer is already near the destination Region.

Private IP VPN over Direct Connect combines the services differently. A transit VIF connects through a DXGW to Transit Gateway, and the VPN terminates between private addresses on that Transit Gateway and the customer device. Traffic remains on private connectivity while IPsec encrypts it end to end. This design requires a private CIDR on Transit Gateway for the tunnel addresses and distinct route-table associations for the underlying Direct Connect attachment and overlaid VPN when segmentation demands it. It does not use acceleration because the path already uses Direct Connect.

For resilient hybrid access, advertise the same application prefixes through Direct Connect and an internet VPN, prefer Direct Connect with BGP policy, and verify failover in both directions. Route propagation alone is not proof: stateful firewalls may reject the returning path if failover creates asymmetry, DNS may still hand out an unreachable private endpoint, and customer routers may retain a stale route. Monitor both VPN tunnel states, BGP status and bytes, and test during a maintenance window before the backup path is needed.

## Transit Gateway attachments and route tables

Transit Gateway is a Regional, highly available router rather than an appliance placed in one subnet. Attachments connect VPCs, Site-to-Site VPNs, Direct Connect gateways, other Transit Gateways, Client VPN endpoints, Cloud WAN core network edges, and supported network appliances. A VPC attachment selects one subnet per Availability Zone that needs to send traffic to the gateway. A workload subnet still needs a VPC route pointing to the Transit Gateway, and the attachment subnet's network controls and return routes must permit the flow.

Transit Gateway route tables provide both forwarding and segmentation. Each attachment associates with exactly one route table, which decides where traffic arriving from that attachment may go. The same attachment can propagate its prefixes into several route tables, which decides which other attachments learn a route back to it. Association answers "where do packets from this attachment look"; propagation answers "which tables learn how to reach this attachment". Keeping those questions separate makes hub-and-spoke isolation straightforward.

For example, associate production and development VPCs with separate spoke route tables, propagate both into a shared-services table, and propagate the shared-services attachment back into both spoke tables. Do not propagate production into the development table or development into production. Both can reach shared services without reaching each other. A blackhole route can explicitly discard a sensitive prefix, and longest-prefix matching lets a narrow inspection route override a broad propagated route.

Peering attachments connect Transit Gateways in the same or different Regions and accounts. The accepter must approve the attachment, and both sides need static Transit Gateway routes pointing at it because peering routes do not propagate dynamically. Inter-Region traffic travels over the AWS global network and is encrypted at the virtual network layer. Peering creates transitive reachability only for prefixes represented in both gateways' route tables; it does not merge the tables, and Route 53 Resolver cannot resolve private names across an inter-Region Transit Gateway peer by default.

An appliance VPC needs symmetric routing because a stateful firewall must see both directions of a flow. Enabling appliance mode on its VPC attachment keeps a flow pinned to the same Availability Zone for its lifetime instead of allowing return traffic to select another zone. Route spoke traffic to an inspection attachment, then from the inspection route table to the destination. A single default route to an appliance is not enough if the return table bypasses it.

**Transit Gateway Connect** integrates software-defined wide area network (SD-WAN) appliances through Generic Routing Encapsulation (GRE) tunnels and BGP. A Connect attachment rides on an existing VPC or Direct Connect attachment called the transport attachment. Each Connect peer supplies two AWS-side BGP sessions for control-plane resilience; configure both. Connect routes propagate dynamically and do not support static routes. ECMP across peers can scale aggregate throughput when they advertise equal prefixes with matching AS paths.

Transit Gateway also supplies a multicast router for attached VPC subnets. A multicast domain separates memberships, and receivers join through static elastic network interface registration or Internet Group Management Protocol version 2 (IGMPv2). This is VPC-only multicast: it does not traverse Direct Connect, VPN, peering or Connect attachments. It is suitable for discovery and one-to-many enterprise applications, not an assumption that an on-premises multicast domain can simply extend through the gateway.

At scale, quotas shape topology before packet limits do. A gateway supports 5,000 attachments by default and 20 route tables, with 10,000 combined dynamic and static routes across its tables. VPC and Direct Connect gateway attachments can reach up to 100 Gbps per Availability Zone under current quotas, while standard VPN tunnels retain their lower per-tunnel ceiling. **AWS Network Manager** provides topology, events and monitoring for Transit Gateway-centered global networks; it observes and organizes the network but does not replace route-table policy.

## Cloud WAN for a global policy

AWS Cloud WAN connects VPCs, data centers and branches through one declarative global policy. A global network is the inventory and visualization container. Its core network is the AWS-managed routing system. The core network policy declares Regions, segments, attachment mapping and segment actions; applying a policy version creates or changes the underlying routing configuration. One policy is live at a time, and previous versions can be restored.

Each declared Region receives a core network edge, a Regional connection point derived from Transit Gateway technology. The edges form a managed full mesh over the AWS global network. VPC, VPN, Connect and Transit Gateway route-table attachments connect at an edge. The core network owner can share the network through **AWS Resource Access Manager (AWS RAM)**, the cross-account resource-sharing service; attachment owners can add permitted attachments without controlling the global policy.

A segment is a global routing domain comparable to a virtual routing and forwarding table. Attachments in the same segment can communicate by default, while separate segments are isolated until a segment action shares routes. Attachment policies can assign a tagged VPC or branch automatically to `production`, `development` or `shared-services`. Segment actions can share the shared-services routes with both application segments without sharing production and development with each other, or steer inter-segment traffic through a network-function group containing firewalls.

Choose Cloud WAN when the requirement is one global segmentation and routing policy spanning several Regions and branches. Choose separate Transit Gateways when teams need direct control of a smaller number of Regional hubs and can manage peering and route tables themselves. Network Manager can visualize either design, but only Cloud WAN turns intent in one policy into consistent multi-Region routing. Cloud WAN does not supply last-mile connectivity: branches still attach through VPN, Direct Connect or Connect appliances.

Current scale defaults include 40 segments, 5,000 attachments and 10,000 routes across the core network. These are planning ceilings, not reasons to build one enormous failure domain. Stage a policy change, inspect its change set for unexpected route sharing, and apply it only after checking overlapping prefixes. A global policy distributes a mistake globally as efficiently as it distributes the intended configuration.

## Client VPN and PrivateLink at scale

AWS Client VPN is OpenVPN-based remote access for individual devices. It differs from Site-to-Site VPN, which connects networks. A Client VPN endpoint terminates TLS sessions and associates with VPC subnets or directly with Transit Gateway. Every endpoint needs a server certificate from **AWS Certificate Manager (ACM)**, the managed certificate service, and one or more authentication methods: mutual certificate authentication, Microsoft Active Directory authentication, or Security Assertion Markup Language (SAML) federation. Mutual certificates can be combined with either user-based method for two factors.

Authentication decides who may connect; authorization rules decide which destination networks an authenticated identity may reach. With Active Directory or SAML, rules can name groups. The endpoint route table must also contain the destination, and VPC or Transit Gateway route tables need a return path. These are three separate gates. A user can authenticate successfully yet reach nothing because an authorization rule is absent, or see an authorization rule but have no endpoint route.

In full-tunnel mode, the client sends all traffic through the endpoint. In split-tunnel mode, AWS pushes only endpoint routes to the client, leaving other traffic on the local connection. Split tunneling reduces AWS data processing and preserves local internet performance, but it permits a device to touch the local network and protected AWS network simultaneously. Added routes reach already-connected split-tunnel clients only after their sessions reset. Associate subnets in at least two Availability Zones and keep identical endpoint routes for each association to avoid intermittent reachability.

For IPv4, the client CIDR must not overlap the VPC, target networks or endpoint routes, is fixed after endpoint creation, and must be between /22 and /12. Client traffic is source-NATed to the endpoint network interface for VPC access. Current endpoints can instead carry IPv6 or dual-stack traffic; AWS assigns the client IPv6 range and does not source-NAT IPv6, improving source visibility. Client VPN is billed for each endpoint-subnet association hour and each active connection hour, so it is rarely the right answer for permanent site connectivity.

AWS PrivateLink provides private, one-way access to a service or resource without routing the consumer into the provider VPC. For a classic endpoint service, the provider places applications behind a **Network Load Balancer**, the layer 4 load balancer, grants named principals permission to request connections and optionally requires manual acceptance. Consumers create interface endpoints, which place private endpoint network interfaces in selected subnets and use security groups and endpoint policies. The provider exposes a service, not its VPC CIDR, so overlapping consumer addresses and transitive-route concerns disappear.

PrivateLink is useful at organization scale when hundreds of VPCs need one API but must not become mutually routable. Central DNS can map a verified private service name to each consumer's endpoint. Traffic stays on the AWS network, but endpoint-hours and per-byte processing apply in every consumer. Current endpoint services can enable cross-Region access, which removes the old absolute rule that provider and consumer must share a Region; use it only when the provider opted in and include inter-Region charges and failure behavior in the design. Transit Gateway remains the answer when consumers need many bidirectional network prefixes rather than one published service.

## Hybrid DNS with Route 53 VPC Resolver

Amazon Route 53 VPC Resolver, formerly Route 53 Resolver, is available at the VPC-plus-two address. It answers VPC hostnames, private hosted-zone records and public names. Resolver endpoints extend that behavior across hybrid connectivity. They carry DNS queries, not application traffic, so Direct Connect, VPN or another routed path must already connect the endpoint subnets to the other DNS servers.

An inbound endpoint gives on-premises resolvers private IP addresses to which they forward queries for AWS namespaces such as `aws.corp.example.com`. Resolver then answers from associated private hosted zones or its recursive view. An outbound endpoint gives queries originating in VPCs source addresses in AWS; forwarding rules send a named suffix such as `corp.example.com` to specified on-premises DNS server addresses. "Inbound" and "outbound" describe the direction relative to VPC Resolver, not who initiated the business transaction.

Build endpoints across at least two Availability Zones and permit TCP and UDP port 53 in security groups, network ACLs and on-premises firewalls. DNS commonly appears healthy for small UDP responses and fails for larger or retried TCP responses when only UDP was allowed. Each rule is Regional and applies only after association with a VPC. Share centrally managed forwarding rules to accounts or organizational units through AWS RAM; consumers can associate a shared rule but cannot modify it.

Resolver chooses the most specific matching rule. Private hosted zones and forwarding rules with overlapping suffixes therefore require deliberate ownership. A forwarding rule for `example.com` can send a query away from a private hosted zone if the queried name matches the rule's namespace, while a more specific rule can override a broader one. Test both forward and reverse lookups, because Active Directory and SSH environments often depend on pointer records under `in-addr.arpa` as well as forward names.

Transit Gateway connectivity does not automatically make private DNS names resolvable across every attached VPC, and inter-Region Transit Gateway peering does not provide cross-peer private hostname resolution through another Region's Resolver. Associate private hosted zones with the intended VPCs, share forwarding rules centrally, and deploy Regional endpoints and rules for multi-Region hybrid DNS. The exam signal "on premises must resolve private hosted-zone records" selects an inbound endpoint; "VPC workloads must resolve on-premises names" selects an outbound endpoint plus a forwarding rule.

## Professional depth

Separate ownership is the first change at enterprise scale. Put Direct Connect connections, DXGWs, Transit Gateways, Cloud WAN policy and Resolver rules in a network account. Share Transit Gateway and Cloud WAN attachments or route tables through AWS RAM, but leave workload teams responsible for their VPC routes and security groups. A central resource being shared does not create routes inside a participant VPC, and a propagated Transit Gateway route does not authorize traffic at the workload interface.

Overlapping CIDRs constrain every routed merger. Transit Gateway does not route between two identical prefixes merely because both VPCs attach, and route advertisements from acquired networks can silently collide. Renumber where possible. During a staged merger, publish individual services through PrivateLink, place a translating firewall or proxy at an explicit boundary, or keep networks in separate Cloud WAN segments. Do not solve overlap by adding more propagation to an ambiguous route table.

Design failure domains across organizations as well as links. Two Direct Connect connections on one AWS device and in one building protect only against a port failure. Maximum resilience requires separate devices and locations, customer routers, provider paths and power domains. Add an internet VPN whose customer device is not dependent on the same carrier. Then test a full location loss, not only a BGP session loss. If DNS endpoints, identity servers or firewalls remain in the failed site, a surviving data path can still be unusable.

Route scale and convergence become migration risks. A DXGW can carry prefixes globally, but Transit Gateway has a combined route ceiling and a peering attachment needs static routes. Summarize prefixes without advertising unused or overlapping space. During a data-center migration, announce a more specific prefix from AWS after each wave so longest-prefix matching moves only that workload, retain the aggregate from on premises as rollback, and remove stale specifics after cutover. Check both directions because an asymmetric migration route through a stateful inspection VPC will fail.

Central inspection creates an availability and cost tradeoff. An appliance-mode attachment preserves flow symmetry, but routing every inter-VPC and internet flow through one VPC adds Transit Gateway processing and may add cross-Availability Zone transfer. Deploy firewall endpoints per Availability Zone, keep each workload on the same-zone path where possible, and use separate route tables for pre-inspection and post-inspection traffic. A default route from every table to the firewall can form a loop rather than a security boundary.

Quotas are architecture inputs: Direct Connect VIF and gateway association limits, Transit Gateway attachments and total routes, Cloud WAN segments and routes, Client VPN endpoint routes, and Resolver queries per endpoint IP. Treat documented defaults as the start of capacity planning, request adjustable increases before migration, and scale across independent hubs when a hard ceiling or blast-radius requirement demands it. Monitoring must cover physical connection state, VIF and BGP state, VPN tunnels, Transit Gateway bytes and drops, and Resolver query logs.

Troubleshoot from the path outward rather than changing several control planes at once. First prove the source has a route to its local gateway and that the destination has a return route. Then check the VPC route table, Transit Gateway association, propagated or static prefix, DXGW allowed prefix and BGP advertisement in order. Reachability Analyzer can model the AWS portion but cannot prove that an on-premises router accepted a route. Flow logs show accepted or rejected IP flows but not a missing route before an interface; Transit Gateway Flow Logs and Network Manager events narrow the hub; Resolver query logs distinguish a DNS answer from a transport failure. Preserve timestamps and request correlation because a routing flap may vanish before an operator opens the console.

Security boundaries should match ownership. Restrict which accounts may create PrivateLink endpoints or Cloud WAN attachments, require acceptance for endpoint-service consumers that are not fully trusted, and use attachment policies that map only approved tags. A Transit Gateway route table is not a firewall, and route isolation does not replace security groups, network ACLs or inspection. Conversely, an organization-wide deny policy cannot make an unreachable route work. Professional questions often present both faults and ask for the pair of changes: one establishes reachability, and the other authorizes the resulting traffic.

## Worked scenario

A manufacturer has two data centers, 70 AWS accounts and production VPCs in three Regions. It needs predictable private capacity for factory systems, encrypted connectivity for regulated traffic, internet backup, isolated production and development networks, shared identity services, and bidirectional DNS. An acquired business overlaps one production CIDR, and engineers need remote access without exposing the VPCs publicly.

The network account orders dedicated Direct Connect connections at two locations on independent customer routers and builds transit VIFs through a DXGW to Regional Transit Gateways. Private IP VPN over Direct Connect encrypts regulated flows, while ordinary Site-to-Site VPN attachments on separate internet devices provide backup. Production, development, shared services and inspection use separate Transit Gateway route tables. Appliance mode keeps firewall flows symmetric. The three Regional hubs peer with explicit static routes; if the global policy and branch count keep growing, Cloud WAN replaces manual peering with tagged attachment policies and global segments.

Resolver inbound endpoints let the data centers resolve AWS private zones, and outbound endpoints plus shared rules forward corporate suffixes to on-premises DNS. Client VPN uses SAML authentication and group authorization, with routes only to administration networks. The overlapping acquisition cannot join the routed core yet, so its applications consume selected central APIs through PrivateLink endpoints. The exam asks which components provide the circuit, encryption, transitive routing, segmentation and DNS. The keyed design is redundant Direct Connect plus VPN transport, Transit Gateway or Cloud WAN for routing, separate route tables or segments for isolation, and the correctly directed Resolver endpoints.

## Exam lens

- "Consistent private bandwidth" maps to Direct Connect; "set up quickly with encryption" maps to Site-to-Site VPN.
- "Direct Connect is private, therefore encrypted" is false; use TLS, IPsec or supported MACsec according to the required boundary.
- "One VPC" maps to a VGW, while "many VPCs with transitive routing" maps to Transit Gateway.
- "Public AWS service endpoint from on premises" maps to a public VIF; private VPC addresses map to a private or transit VIF.
- "Several Transit Gateways over one connection" maps to a transit VIF through a DXGW.
- "Branch-to-branch over the AWS backbone without a Region detour" maps to Direct Connect SiteLink.
- "99.99 percent Direct Connect SLA design" maps to separate devices in more than one Direct Connect location.
- "Aggregate VPN throughput" maps to BGP VPNs on Transit Gateway with ECMP; a VGW or static routes are distractors.
- "Improve a long-distance internet VPN path" maps to accelerated VPN on Transit Gateway, not a VGW.
- "Encrypt Direct Connect without public addresses" maps to private IP VPN over a transit VIF, DXGW and Transit Gateway.
- "Attachment can reach shared services but not another spoke" maps to Transit Gateway association and propagation in separate route tables.
- "SD-WAN appliance with GRE and dynamic routes" maps to Transit Gateway Connect.
- "One global segmentation policy" maps to Cloud WAN; Network Manager alone only observes a Transit Gateway topology.
- "Remote employees" maps to Client VPN, not Site-to-Site VPN.
- "Expose one service without routing between overlapping VPCs" maps to PrivateLink.
- "On premises resolves an AWS private zone" maps to a Resolver inbound endpoint.
- "A VPC resolves an on-premises zone" maps to a Resolver outbound endpoint and forwarding rule.
- "BGP is up but a prefix is unreachable" maps to checking VPC routes, Transit Gateway association and propagation, DXGW allowed prefixes, security controls and the return path.

## Knowledge check

### 1. Predictable capacity for a factory link (Associate)

A manufacturer transfers a steady stream of production telemetry from a factory to one AWS Region. The public internet has caused variable latency and packet loss. The company needs a private path with predictable capacity and can wait several weeks for provisioning. Encryption is handled by TLS in the application.

Which solution will meet these requirements?

- **A)** Create an accelerated Site-to-Site VPN connection to a virtual private gateway.
- **B)** Order an AWS Direct Connect connection and create the appropriate private virtual interface.
- **C)** Create an AWS Client VPN endpoint and install a client on the factory router.
- **D)** Publish the telemetry collector through AWS PrivateLink.

<details><summary>Answer</summary>

**Answer: B.** Direct Connect supplies the private physical path and provisioned port capacity the requirement describes; a private VIF reaches private addresses in the VPC. A is wrong because accelerated VPN requires Transit Gateway, not a VGW, and still begins over the public internet. C is remote-user access rather than site connectivity. D privately exposes a service within the AWS network but provides no path from the factory to AWS.

*Where this is covered: Direct Connect connections and virtual interfaces.*

</details>

### 2. Connecting Direct Connect locations directly (Associate)

A retailer has private VIFs on Direct Connect connections in Singapore and Frankfurt. Its offices need private branch-to-branch communication over the AWS global network, and traffic must not detour through a workload Region. No VPC connectivity is required for this flow.

Which solution will meet these requirements?

- **A)** Peer the VPCs nearest each office and route office traffic through the peering connection.
- **B)** Create a public VIF at each location and advertise the office prefixes publicly.
- **C)** Enable Direct Connect SiteLink on supported VIFs at both locations.
- **D)** Combine the connections in one Direct Connect LAG.

<details><summary>Answer</summary>

**Answer: C.** SiteLink carries traffic between Direct Connect points of presence over the AWS network without routing through a Region, which exactly matches the branch-to-branch requirement. A introduces VPCs and a Regional detour the stem excludes. B exposes the wrong interface type and public VIFs do not support SiteLink. D is impossible because LAG members must terminate on the same AWS device at the same Direct Connect location.

*Where this is covered: Physical resilience, LAGs, MACsec and SiteLink.*

</details>

### 3. An authenticated remote user with no route (Associate)

Engineers can authenticate successfully to a Client VPN endpoint and establish sessions, but they cannot reach an on-premises administration subnet through the VPC's existing hybrid connection. The VPC and on-premises route tables already have return routes, and security groups allow the traffic. Only members of the `NetworkAdmins` identity-provider group should receive access.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Add the administration subnet to the Client VPN endpoint route table for every associated target subnet.
- **B)** Change the endpoint from split-tunnel to full-tunnel mode.
- **C)** Add a Client VPN authorization rule for the administration subnet and the `NetworkAdmins` group.
- **D)** Replace Client VPN with a second Site-to-Site VPN connection for each engineer.
- **E)** Add the administration subnet to the endpoint's client CIDR range.

<details><summary>Answer</summary>

**Answer: A and C.** Client VPN needs both a route for the destination and an authorization rule granting the intended group access. The stem already supplies return routing and security controls. B changes which traffic clients send into the tunnel but does not create either missing gate. D is network-to-network connectivity and cannot scale per user. E confuses assigned client addresses with destination routes, and the client CIDR cannot overlap target networks.

*Where this is covered: Client VPN and PrivateLink at scale.*

</details>

### 4. Publishing one service across overlapping networks (Associate)

After an acquisition, 60 consumer VPCs use CIDR ranges that overlap the provider VPC. Every consumer needs private access to one TCP licensing service, but none should receive routed access to the provider network or to another consumer. The provider wants to grant access per AWS account.

Which solution will meet these requirements?

- **A)** Attach all VPCs to one Transit Gateway and propagate every VPC route.
- **B)** Put the service behind a Network Load Balancer, create a PrivateLink endpoint service, and allow approved consumer principals to create interface endpoints.
- **C)** Create full-mesh VPC peering and add the provider CIDR to every route table.
- **D)** Create one Site-to-Site VPN from every consumer VPC to the provider VPC.

<details><summary>Answer</summary>

**Answer: B.** PrivateLink exposes the TCP service through consumer-local endpoint interfaces without routing the provider CIDR, so overlapping addresses do not conflict and consumers gain no transitive connectivity. A cannot route ambiguous overlapping prefixes and creates broader reachability. C has the same overlap problem and VPC peering is not transitive. D treats VPCs as external sites, still depends on unique routed addresses and creates heavy operational work.

*Where this is covered: Client VPN and PrivateLink at scale.*

</details>

### 5. Bidirectional hybrid name resolution (Associate)

A company has private hosted-zone records under `aws.example.com` and on-premises records under `corp.example.com`. VPC workloads must resolve the corporate names, and on-premises clients must resolve the AWS private names. Direct Connect routing between the networks already works.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create a Resolver outbound endpoint and associate a forwarding rule for `corp.example.com` with the VPCs.
- **B)** Create a Resolver inbound endpoint and configure it to forward `corp.example.com` to the VPC-plus-two address.
- **C)** Associate the private hosted zone directly with the on-premises network.
- **D)** Create a Resolver inbound endpoint and configure the on-premises resolver to forward `aws.example.com` to its addresses.
- **E)** Create public records for both namespaces so each side uses internet DNS.

<details><summary>Answer</summary>

**Answer: A and D.** VPC-originated queries leave Resolver through an outbound endpoint under a forwarding rule, while queries entering from on premises target an inbound endpoint that can answer from the private hosted zone. B reverses the endpoint direction and names the wrong suffix. C is impossible because hosted-zone associations target VPCs, not an on-premises network. E exposes internal names and ignores the private-resolution requirement.

*Where this is covered: Hybrid DNS with Route 53 VPC Resolver.*

</details>

### 6. Replacing hand-built global routing policy (Professional)

A multinational company operates Transit Gateways in eight Regions and connects 140 branches through VPN and SD-WAN appliances. Engineers manually maintain peering routes and separate production, development and shared-services tables in every Region. Configuration drift is common. The company wants one declarative policy that assigns tagged attachments to global segments and consistently shares only the shared-services routes.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Register every Transit Gateway in Network Manager and continue updating each route table independently.
- **B)** Create one global Direct Connect gateway and associate every VPC directly with it.
- **C)** Build an AWS Cloud WAN core network whose attachment policies map tags to segments and whose segment actions share the shared-services routes.
- **D)** Replace all Transit Gateway peerings with full-mesh inter-Region VPC peering.

<details><summary>Answer</summary>

**Answer: C.** Cloud WAN applies one core network policy across Regional edges, maps tagged attachments to global segments and controls route sharing through segment actions. A improves visibility but Network Manager does not turn the separate route tables into one policy. B cannot associate VPCs directly, does not provide global segmentation and is not a VPC transit router. D multiplies point-to-point relationships and has no central segment policy.

*Where this is covered: Cloud WAN for a global policy.*

</details>

### 7. Choosing the virtual interface (Associate)

A company has one Direct Connect connection. Its data center must reach ten VPCs attached to a Transit Gateway, including VPCs in accounts owned by different business units. The company wants to exchange private routes through one BGP-based attachment.

Which solution will meet these requirements?

- **A)** Create a public VIF and associate it directly with the Transit Gateway.
- **B)** Create one private VIF per VPC and attach each VIF to the Transit Gateway.
- **C)** Create a private VIF and associate it directly with every VPC attachment.
- **D)** Create a transit VIF, connect it to a Direct Connect gateway, and associate the Direct Connect gateway with the Transit Gateway.

<details><summary>Answer</summary>

**Answer: D.** A transit VIF is the Direct Connect interface type for reaching one or more Transit Gateways, and the DXGW sits between the VIF and Transit Gateway. A reaches public AWS endpoints and cannot associate directly with Transit Gateway. B is unnecessary and structurally wrong because private VIFs target VGWs or a DXGW rather than VPC attachments. C gives a private VIF destinations it cannot directly associate with.

*Where this is covered: Direct Connect connections and virtual interfaces.*

</details>

### 8. Direct Connect location failure (Professional)

A payment company needs its hybrid connection to satisfy the Direct Connect maximum-resiliency model. It currently has two dedicated connections in one colocation facility, terminated on the same AWS device and combined in one LAG. A facility power failure must not disconnect the company from AWS.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Provision connections at a second Direct Connect location.
- **B)** Add two more members to the existing LAG in the original location.
- **C)** Terminate redundant connections on separate AWS devices and independent customer equipment.
- **D)** Raise the LAG minimum-links setting to the total number of members.
- **E)** Replace the dedicated connections with hosted VIFs on the same partner connection.

<details><summary>Answer</summary>

**Answer: A and C.** Maximum resilience separates connections across devices and more than one Direct Connect location, with independent customer-side equipment completing the failure-domain separation. B adds bandwidth but all LAG members remain on the same AWS device and location. D deliberately takes the LAG down when any member fails and adds no location. E retains shared physical infrastructure and does not meet the maximum-resiliency placement model.

*Where this is covered: Physical resilience, LAGs, MACsec and SiteLink.*

</details>

### 9. Scaling encrypted site connectivity (Associate)

A media company uses two BGP Site-to-Site VPN connections attached to a Transit Gateway. Aggregate traffic exceeds the capacity of one standard tunnel, but no single flow exceeds it. The company wants to use the existing tunnels concurrently with the least operational overhead.

Which solution will meet these requirements?

- **A)** Enable equal-cost multipath routing and advertise equal prefixes with matching BGP path attributes over the tunnels.
- **B)** Move both VPN connections to a virtual private gateway and enable route propagation.
- **C)** Replace BGP with static routes of equal prefix length on the Transit Gateway.
- **D)** Create a link aggregation group containing the VPN tunnels.

<details><summary>Answer</summary>

**Answer: A.** Transit Gateway supports ECMP across dynamic-routing VPN tunnels and can distribute separate flows over equal paths, increasing aggregate bandwidth. B loses this scaling behavior because a VGW does not provide VPN ECMP. C fails because static-routing VPN connections do not qualify for ECMP. D is a Direct Connect feature that aggregates dedicated physical Ethernet connections, not IPsec tunnels.

*Where this is covered: Site-to-Site VPN, acceleration and bandwidth.*

</details>

### 10. Isolated spokes with shared services (Professional)

A company attaches production, development and shared-services VPCs to one Transit Gateway. Production and development must each reach shared services, but must never route directly to each other. Security groups already allow the intended application ports.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Associate all three attachments with the default Transit Gateway route table and enable all propagation.
- **B)** Associate production and development attachments with separate spoke route tables that contain routes only to shared services.
- **C)** Add a peering attachment between the production and development VPCs.
- **D)** Propagate the production and development prefixes into the shared-services route table, and propagate the shared-services prefix into both spoke tables.
- **E)** Enable appliance mode on all three VPC attachments.

<details><summary>Answer</summary>

**Answer: B and D.** Separate association tables control where traffic arriving from each spoke can go, while selective propagation gives shared services return routes to both and gives each spoke only the shared-services route. A creates full mesh reachability. C directly violates the isolation requirement. E preserves Availability Zone affinity for stateful appliances but neither creates the required routes nor separates the spokes.

*Where this is covered: Transit Gateway attachments and route tables.*

</details>

## Summary

Hybrid networking is a sequence of boundary decisions. Choose Direct Connect for private, predictable capacity and Site-to-Site VPN for fast IPsec connectivity; combine them for encrypted private transport and independent internet failover. Select the VIF by destination: public AWS endpoints use public, VGWs use private, and Transit Gateways use transit through a Direct Connect gateway. A VGW serves one VPC, Transit Gateway routes among many Regional attachments, and Cloud WAN applies global segment policy. Separate Transit Gateway association from propagation, preserve symmetry through stateful appliances, and use BGP plus ECMP when aggregate VPN bandwidth matters. Client VPN connects individual users, while PrivateLink publishes one service without routed network access, even across overlapping CIDRs. For hybrid DNS, inbound Resolver endpoints accept on-premises queries for AWS names; outbound endpoints and forwarding rules send VPC queries to on-premises DNS. Resilience requires independent devices and locations, intentional route preference, working return paths and tested failure, not merely two lines on a diagram.

## Related units

- [Amazon VPC](vpc.md): subnet routes, gateway endpoints, peering and security controls beneath every hybrid attachment
- [Amazon Route 53](route53.md): hosted zones, records, routing policies and Resolver behavior beyond hybrid forwarding
- [AWS Global Accelerator](global-accelerator.md): the edge network used by accelerated Site-to-Site VPN
- [AWS WAF, Shield, Firewall Manager and Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md): centralized inspection and DNS filtering along routed paths
- [AWS Organizations, IAM Identity Center and Control Tower](../07-security/organizations-identity-center-and-control-tower.md): multi-account ownership and resource sharing boundaries
- [Cost management](../08-management/cost-management.md): cross-AZ, cross-Region and network-processing charges that alter topology decisions

## Sources

- [What is AWS Direct Connect?](https://docs.aws.amazon.com/directconnect/latest/UserGuide/Welcome.html): components, VIF types, network requirements and billing shape
- [Dedicated connections](https://docs.aws.amazon.com/directconnect/latest/UserGuide/dedicated_connection.html): current dedicated port speeds and immutable capacity
- [Hosted connections](https://docs.aws.amazon.com/directconnect/latest/UserGuide/hosted_connection.html): current hosted speeds and partner provisioning
- [Direct Connect virtual interfaces](https://docs.aws.amazon.com/directconnect/latest/UserGuide/WorkingWithVirtualInterfaces.html): private, public and transit destinations, BGP and SiteLink support
- [Direct Connect gateways](https://docs.aws.amazon.com/directconnect/latest/UserGuide/direct-connect-gateways-intro.html): global gateway associations and routing role
- [Direct Connect routing policies](https://docs.aws.amazon.com/directconnect/latest/UserGuide/routing-and-bgp.html): path-selection order, ECMP and local-preference communities
- [Direct Connect Resiliency Toolkit](https://docs.aws.amazon.com/directconnect/latest/UserGuide/resiliency_toolkit.html): maximum, high, and development and test resilience models
- [Direct Connect link aggregation groups](https://docs.aws.amazon.com/directconnect/latest/UserGuide/lags.html): LACP, member placement, limits and minimum links
- [MAC Security in Direct Connect](https://docs.aws.amazon.com/directconnect/latest/UserGuide/MACsec.html): encryption boundary, modes, supported speeds and connection types
- [Direct Connect SiteLink](https://docs.aws.amazon.com/directconnect/latest/UserGuide/direct-connect-site-link.html): point-of-presence connectivity and supported VIFs
- [How Site-to-Site VPN works](https://docs.aws.amazon.com/vpn/latest/s2svpn/how_it_works.html): gateways, two tunnels, routing and IPv6 combinations
- [Site-to-Site VPN quotas](https://docs.aws.amazon.com/vpn/latest/s2svpn/vpn-limits.html): standard and large-bandwidth throughput, MTU and ECMP conditions
- [Accelerated Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/accelerated-vpn.html): Global Accelerator path and Transit Gateway restrictions
- [Private IP VPN with Direct Connect](https://docs.aws.amazon.com/vpn/latest/s2svpn/private-ip-dx.html): transit VIF, DXGW and Transit Gateway overlay design
- [What is Transit Gateway?](https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html): attachment, association and propagation concepts
- [Transit Gateway route tables](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-route-tables.html): associations, multi-table propagation and static routes
- [Transit Gateway peering](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-peering.html): acceptance, static routes and inter-Region encryption
- [Transit Gateway Connect](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-connect.html): GRE, BGP, transport attachments and ECMP
- [Transit Gateway multicast](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-multicast-overview.html): domains, IGMPv2 and unsupported hybrid attachments
- [Transit Gateway quotas](https://docs.aws.amazon.com/vpc/latest/tgw/transit-gateway-quotas.html): attachments, route tables, routes and bandwidth
- [What is AWS Cloud WAN?](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html): core networks, edges, segments, policies and sharing
- [Cloud WAN policy parameters](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policies-json.html): attachment policies, segment actions and routing controls
- [Cloud WAN quotas](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-quotas.html): segment, attachment, route and bandwidth limits
- [What is AWS Client VPN?](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/what-is.html): endpoint components, target networks, IPv6 and billing shape
- [Client VPN authentication](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authentication.html): certificate, Active Directory and SAML options
- [Client VPN routes](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-routes.html): route and authorization gates and split-tunnel updates
- [Create a Client VPN endpoint](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-endpoint-create.html): CIDR constraints, certificates and tunnel modes
- [AWS PrivateLink concepts](https://docs.aws.amazon.com/vpc/latest/privatelink/concepts.html): providers, consumers, endpoints, policies and private connectivity
- [Create a PrivateLink endpoint service](https://docs.aws.amazon.com/vpc/latest/privatelink/create-endpoint-service.html): load balancer, permissions, acceptance, DNS and cross-Region access
- [What is Route 53 VPC Resolver?](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html): current name, recursive behavior and hybrid DNS flow
- [Forwarding inbound DNS queries](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-forwarding-inbound-queries.html): inbound endpoint addresses and on-premises delegation
- [Forwarding outbound DNS queries](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-forwarding-outbound-queries.html): outbound endpoints and suffix rules
- [Managing Resolver forwarding rules](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-rules-managing.html): VPC associations, reverse lookup and AWS RAM sharing
