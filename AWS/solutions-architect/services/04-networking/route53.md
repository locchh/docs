# Amazon Route 53

**Where it sits on the exams.** **Amazon Route 53** is AWS's authoritative Domain Name System (DNS) service, domain registrar and health checking service, and it is the layer that decides which endpoint a name resolves to before any packet reaches a load balancer. It carries SAA-C03 tasks 2.2 and 4.4 and SAP-C02 tasks 2.2, 2.4 and 4.2, and it turns up as a supporting service anywhere an exam scenario spans two Availability Zones, two Regions or a data center. The rule of thumb the exam wants is that the routing policy comes from the requirement in the stem, latency for speed, geolocation for compliance, failover for disaster recovery, weighted for gradual shifts, and that health checks plus alias records are what make any of them actually fail over.

## What Route 53 is and where it sits in the AWS global infrastructure

Route 53 does three jobs, and a question usually turns on exactly one of them. It registers domain names, acting as a registrar through Amazon Registrar, Inc. or its registrar associate Gandi. It answers DNS queries authoritatively for the domains you host in it. And it health checks endpoints over the internet so the answers it gives can change when something breaks. Any one job works without the other two.

Route 53 is a global service, not a Regional one. There is no Region selector for a **hosted zone**, the container that holds the records for one domain, and hosted zone data is replicated to an authoritative name server fleet spread across the world. Each public hosted zone is assigned four name servers, deliberately placed in four different top-level domains, for example `ns-2048.awsdns-64.com`, `ns-2049.awsdns-65.net`, `ns-2050.awsdns-66.org` and `ns-2051.awsdns-67.co.uk`, so that an outage affecting one top-level domain's infrastructure cannot take all four out at once. Those four names are what you give a registrar to delegate the domain. Each of the four is itself an anycast address answered by many servers in many locations, which is why DNS resolution keeps working when an individual site is impaired.

That global shape is why Route 53 appears in the exam guide bullet about AWS global infrastructure alongside Availability Zones and Regions. Zones give fault isolation inside a Region, Regions give geographic separation, and Route 53 is the mechanism that lets a client find the right Region or zone in the first place: a multi-Region design is not multi-Region until something decides which Region a user reaches. Its health checkers are distributed the same way, running from locations worldwide so that a network problem local to one checker does not look like an endpoint failure.

The split between the control plane and the data plane matters for resilience answers. The data plane is the name server fleet that answers queries, and it keeps answering during a Regional impairment. The control plane, the APIs that create hosted zones and change records, runs in the US East (N. Virginia) Region. That asymmetry is why a good failover plan does not require a record change during the disaster: it uses health checks Route 53 evaluates on its own, or routing controls, both on highly available data planes.

## Hosted zones, records, domain registration, and how changes propagate

A hosted zone holds records, each with a name, a type, a value and a time to live (TTL). Route 53 supports A, AAAA, CAA, CNAME, DS, HTTPS, MX, NAPTR, NS, PTR, SOA, SPF, SRV, SSHFP, SVCB, TLSA and TXT records, plus its own alias extension covered in the next section. AWS advises using a TXT record rather than the SPF type for sender policy data, because the SPF record type is deprecated in the relevant RFC. Every record name in a zone must end with the zone name, and a CNAME cannot coexist with any other record of the same name, which is the DNS rule that makes alias records necessary.

Two records are created for you in every public hosted zone. The NS record lists the four authoritative name servers and should not be edited. The start of authority (SOA) record carries the zone's base parameters, and its last field is the minimum TTL used for negative caching: how long a resolver may remember that a name does not exist. Route 53 caps negative caching at the lesser of that minimum TTL and the TTL on the SOA record itself, whose default is 900 seconds. Raising it reduces query charges for nonexistent names but lengthens the outage if you delete a good record by mistake, because resolvers keep serving the cached "does not exist" answer.

TTL is the single most commonly tested Route 53 behavior. When you change a record, the change reaches every Route 53 name server that manages the hosted zone within about 60 seconds, and the API reports `PENDING` until then and `INSYNC` afterward. What takes longer is the world forgetting the old answer. Resolvers on the internet cache a record for its TTL, and they cache the delegation to your four name servers for around two days. A record with a 24-hour TTL therefore continues to send some users to the old address for up to a day after the change is complete inside Route 53, and neither AWS nor you can flush a third-party resolver's cache. The practical consequences are worth memorizing. Lower the TTL to 60 seconds days before a planned migration or cutover, then raise it afterward. Never claim a DNS-based failover meets a recovery time objective shorter than the TTL plus the health check detection time. And when a scenario says clients cache DNS answers for a long time or that failover must be independent of DNS caching, the answer is a static anycast address from **AWS Global Accelerator**, the service that fronts applications with fixed IP addresses on the AWS edge network, rather than any Route 53 routing policy.

Domain registration is the third function and the least tested. Registering a domain in Route 53 creates a public hosted zone with the same name, assigns four name servers and updates the registration to use them, so the two are wired together automatically. Registration runs in whole years with auto renew on by default, privacy protection hides contact details from the public WHOIS database where the registry allows it, and domains can be transferred in or out. Registration is independent of DNS service: you can point an externally registered domain at Route 53 by editing the name server records at the current registrar. The default quota is 20 domains per account.

```bash
aws route53 change-resource-record-sets --hosted-zone-id Z123456789ABCDEFGHIJK \
  --change-batch '{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{
    "Name":"www.example.com","Type":"A","TTL":60,
    "ResourceRecords":[{"Value":"192.0.2.44"}]}}]}'
```

## Alias records compared with CNAME records

An **alias record** is a Route 53 extension to DNS that points a name at an AWS resource or at another record in the same hosted zone, and it exists because the DNS protocol forbids a CNAME at the zone apex. You cannot create a CNAME for `example.com`, only for `www.example.com`, so without alias records the bare domain could never point at a load balancer or a distribution whose address AWS controls and changes. An alias record can be created at the apex in almost every configuration, and it is declared as an A or AAAA record, so `dig example.com A` shows an A record with an IP address rather than a CNAME chain.

The supported targets are a fixed list, and the exam expects you to recognize it: an **Elastic Load Balancing** load balancer of any type, the managed service that spreads traffic across healthy targets, including Application, Network and Classic Load Balancers; an **Amazon CloudFront** distribution, the AWS content delivery network; an **Amazon API Gateway** Regional or edge-optimized custom domain, the managed API front door; an interface endpoint in **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network your resources run in, which gives private access to a service; a Global Accelerator accelerator; an **AWS Elastic Beanstalk** environment, the managed application platform; an **AWS App Runner** service, the managed container web service; an **AWS AppSync** domain name, the managed GraphQL service; an **Amazon OpenSearch Service** custom domain, the managed search and analytics service; an **Amazon Simple Storage Service (Amazon S3)** bucket configured as a static website, the object store; and another Route 53 record of the same type in the same hosted zone. Notice what is missing. There is no alias to an **Amazon Elastic Compute Cloud (Amazon EC2)** instance, the virtual server service, and no alias to an arbitrary external hostname. Those need an A record holding the address or a CNAME.

Three behaviors follow from the alias mechanism and each one decides questions. First, Route 53 tracks the target's addresses itself, so when a load balancer's node addresses change, the answers change with no action from you. Second, you cannot set a TTL on an alias to an AWS resource, because Route 53 uses the target service's own default TTL; an alias to another record in the same hosted zone uses that target record's TTL instead. Third, and this is the cost answer, Route 53 does not charge for queries to alias records that point at AWS resources, while it does charge for CNAME queries. A CNAME pointing at another name inside Route 53 is charged as two queries, because the resolver must ask again for the target name. An alias to an Application Load Balancer is therefore cheaper than a CNAME to the same load balancer, works at the apex where a CNAME cannot, and needs no TTL management. When a stem asks for the "MOST cost-effective" way to point a domain at an AWS resource, alias is the key and CNAME is the distractor.

Alias records also carry the `Evaluate Target Health` setting, which is the cleanest way to health check an AWS resource. Setting it to yes makes Route 53 use the health that the target service already knows about, so an alias to a load balancer is unhealthy when every target behind that load balancer is unhealthy, and an alias to a group of weighted records is healthy as long as at least one of them is. AWS explicitly recommends using `Evaluate Target Health` rather than creating a Route 53 health check against a resource you can alias to, which saves the health check charge and avoids the ambiguity of checking one node of a multi-node service.

## Routing policies

A routing policy is chosen per record, and every record in a group that shares a name and type must use the same policy. Read this table by starting from the requirement in the question stem rather than from the policy name: find the row whose "what it optimizes for" matches the stated goal, then confirm the health check column against whether the scenario needs failure detection.

| Routing policy | What it optimizes for | Health checks | Exam wording that selects it |
|---|---|---|---|
| Simple | One answer for one resource, no decision logic | No. Multiple values in one simple record are returned in random order and are never health checked | "a single web server", "a static website", "basic DNS", no mention of failure or geography |
| Weighted | A chosen proportion of traffic per endpoint | Yes, per record. Zero-weight records are used only when every nonzero-weight record is unhealthy | "send 10 percent of traffic", "blue/green", "canary", "gradually shift", "A/B test" |
| Latency | Lowest measured network latency between the user and an AWS Region | Yes, per record | "lowest latency", "best performance for global users", "resources in multiple Regions" |
| Failover | An active-passive pair: primary while healthy, secondary otherwise | Yes, and it is the point of the policy | "active-passive", "standby", "disaster recovery", "static maintenance page when the site is down" |
| Geolocation | The legal or editorial location of the user, by continent, country or US state | Yes, per record | "content licensing", "must not be served outside", "localized language", "data sovereignty" |
| Geoproximity | Distance between user and resource, adjustable with a bias | Yes, per record | "shift traffic toward a Region", "closest resource", "move a share of traffic without changing endpoints" |
| Multivalue answer | Returning several healthy addresses at once for client-side spreading | Yes, per record, and unhealthy values are withheld | "return multiple IP addresses", "improve availability without a load balancer", "randomly across servers" |
| IP-based | Routing decided by the client's source IP range, which you supply | Yes, per record | "route users from a specific ISP", "we know our clients' address ranges", "override geolocation for known networks" |

Simple routing is the default and the one whose limits get tested. A simple record cannot coexist with another record of the same name and type, and while you can put several IP addresses in one simple record, Route 53 returns them all in random order and never health checks any of them. A scenario that says "one of the servers failed and users kept being sent to it" is describing simple routing with multiple values, and the fix is multivalue answer routing with a health check per value.

Weighted routing assigns each record a weight from 0 to 255, and an endpoint receives its weight divided by the sum of all weights in the group. Weights of 1 and 255 send one 256th of traffic to the first endpoint, which is how a canary release starts. Setting a weight to 0 stops traffic to that record, with one trap: if every nonzero-weight record becomes unhealthy, Route 53 falls back to the zero-weight records, so a zero-weight endpoint must still be able to answer. Up to 100 weighted records can share a name and type.

Latency-based routing compares AWS's own latency measurements between the querying resolver and each AWS Region you have created a latency record for. Two consequences follow. Because the data describes traffic between users and AWS data centers, a latency record for an on-premises resource is meaningless, and AWS says so directly. And because latency data is collected over time and internet routing changes, the Region a given user reaches this week may change next week, so latency routing is not a way to pin a user to a Region. You create one latency record per Region, tagged with that Region, and Route 53 picks among them.

Geolocation routing answers from the location the query appears to come from, specified as a continent, a country, or a subdivision for US states. When regions overlap, the smallest one wins, so a record for Canada beats a record for North America. The failure mode the exam tests is the missing default record: some IP addresses map to no location, and if you have not created a default record, Route 53 returns a "no answer" response to those users rather than falling back to anything. Always create the default record unless denying service to unmapped users is the actual requirement.

Geoproximity routing routes on the distance between the user and the resource, where the resource is identified by an AWS Region, a Local Zone group, or a latitude and longitude for anything outside AWS. Its distinguishing feature is the bias, an integer from 1 to 99 that expands the geographic area a resource serves, or from -1 to -99 that shrinks it. Route 53 applies the formula `biased distance = actual distance * [1 - (bias/100)]`, so a bias of +50 makes a resource 150 km away look 75 km away and pull traffic from a resource that is genuinely closer. That is the mechanism behind "shift a portion of traffic from one Region to another without moving any endpoints", and it is the one policy where the distractor is latency-based routing, which optimizes measured latency rather than geography and offers no dial to turn. Only 30 geoproximity records can share a name and type, against 100 for the other multi-record policies.

Multivalue answer routing returns up to eight healthy records chosen at random, gives different answers to different resolvers, and withholds values whose health check is failing. AWS describes it as a way to use DNS to improve uptime and load sharing, and is explicit that it is not a substitute for a load balancer: there is no connection draining, no least-outstanding-requests algorithm and no TLS termination. When every record in the group is unhealthy, Route 53 returns up to eight unhealthy records rather than nothing.

IP-based routing works from data you supply. You build a CIDR collection holding named CIDR locations, each a list of CIDR blocks, then attach records to those locations. IPv4 blocks may be between `/1` and `/24` and IPv6 blocks between `/1` and `/48`, a query from a longer prefix matches a shorter block you listed, and anything unmatched falls to the default `*` location. Use it when you know your clients' address ranges and want to route a particular internet service provider's users to a particular endpoint for transit cost or performance, or to override geolocation where you know better than the geographic database. It is the one policy that cannot be used in a private hosted zone, and quotas are tight at 5 CIDR collections per account.

**Route 53 Traffic Flow** is the visual builder that composes these policies into a tree, for example latency at the top with weighted records beneath each Region and a failover branch under each. It saves the tree as a versioned traffic policy that you attach to domain names and can roll back, and it bills per policy record per month, which is why most designs build the records directly.

Finally, the decision that sits above all of these: DNS-based routing against anycast routing. Route 53 decides which address a client is told to use, and once the client caches that answer, Route 53 has no further influence until the TTL expires. Global Accelerator instead gives you two static anycast IP addresses that never change; the client always connects to the same addresses, and AWS changes which Region those packets are proxied to. AWS states that Global Accelerator detects an unhealthy endpoint and takes it out of service in less than one minute and that change propagation takes seconds, because no resolver cache is involved. Choose Route 53 routing policies when you want the answer itself to carry the decision, when endpoints are not all in AWS, or when the requirement is geographic or proportional. Choose Global Accelerator when clients cache DNS badly, when the protocol is not HTTP, such as gaming over UDP or Voice over IP, or when a firewall allowlist needs fixed addresses. Choose CloudFront when the content is cacheable or the benefit comes from terminating connections at the edge. The three are complements, and a common design uses Route 53 to resolve the name to a CloudFront distribution or to Global Accelerator's anycast addresses. The details live in [Amazon CloudFront](cloudfront.md) and [AWS Global Accelerator](global-accelerator.md).

## Health checks and DNS failover

A **health check** is an independent Route 53 object you associate with records, and there are three kinds. An endpoint health check sends requests over the internet from Route 53's distributed checker fleet to an IP address or a domain name you specify, using HTTP, HTTPS or TCP. A calculated health check monitors other health checks and reports healthy when a number, all, or at least one of its children are healthy. A CloudWatch alarm health check watches the data stream behind an alarm in **Amazon CloudWatch**, the AWS monitoring and observability service, so that any metric can drive DNS, including metrics that no external probe could see such as queue depth, replication lag or database throttling. A fourth kind exists only for Application Recovery Controller routing controls and is covered later in this unit.

The endpoint check's numbers decide questions. The request interval is 30 seconds by default or 10 seconds at extra cost, and the failure threshold is the number of consecutive checks that must pass or fail before the status flips. Route 53 aggregates across its checkers with a documented rule: if more than 18 percent of checkers report the endpoint healthy it is healthy, and at 18 percent or fewer it is unhealthy, a threshold set so a network partition isolating a few checkers does not condemn a working endpoint. For HTTP and HTTPS, Route 53 must open a TCP connection within four seconds and receive a 2xx or 3xx status within two more; for TCP the connection must succeed within ten seconds. HTTPS checks do not validate certificates, so an expired certificate does not fail the check. String matching adds a search for a string that must appear within the first 5,120 bytes of the response body, which is how you detect an application that returns 200 while its database is down. Health checks cannot target private, link-local or other nonroutable addresses, which is why an endpoint check is useless for a resource that exists only inside a VPC.

The calculated and CloudWatch types answer the scenarios an endpoint check cannot. One parent calculated health check can monitor up to 255 child health checks and cannot monitor another calculated check. Use it to express "the Region is healthy when at least three of its five application servers are healthy". The CloudWatch alarm type is the answer whenever health is a metric rather than an HTTP response, and whenever the resource is private. Route 53 watches the alarm's data stream rather than the alarm state, so you cannot force a failover with `SetAlarmState`, and the alarm must use a standard-resolution metric with a simple statistic, must live in the same account, and cannot use metric math or "M out of N" evaluation. You also choose what the check reports when CloudWatch has insufficient data: healthy, unhealthy, or the last known status.

Failover behavior is where the exam sets traps, and there is one rule to carry into the exam: when every record in a group is unhealthy, Route 53 treats them all as healthy and answers normally. It has to return something, and it has no basis for preferring one. The corollary is that DNS failover never produces an empty answer and never produces a safe default on its own; if you want traffic to land on a maintenance page when the whole fleet is down, that page must be an explicit secondary record. A record with no health check attached is always considered healthy, which is how a single unchecked record silently becomes the answer that never rotates out. For an explicit failover pair, if the primary is unhealthy and the secondary is healthy, Route 53 returns the secondary; if both are unhealthy it returns the primary; and if you omit the health check on the secondary altogether, Route 53 returns the secondary whenever the primary is unhealthy even if the secondary is broken.

AWS separates the two failover shapes by policy. Active-active failover uses any policy other than failover, typically weighted or latency records with a health check on each, and Route 53 stops returning the records that fail. Active-passive failover uses the failover policy with one primary and one secondary, and the common pattern pairs a primary alias to an Application Load Balancer with a secondary alias to an S3 bucket serving a static "temporarily unavailable" page. You can nest them: a failover alias record whose primary target is a group of weighted or latency records, with `Evaluate Target Health` set to yes, is healthy while any member of that group is healthy and fails over to the secondary branch when none is.

Map those shapes onto the four disaster recovery strategies, because an exam question usually asks for a failover strategy rather than a record type. Backup and restore has no standing DNS answer: the record is created or repointed by hand after the environment is rebuilt, and the recovery time is measured in hours. Pilot light and warm standby both use active-passive failover records, primary pointing at the live Region and secondary at the scaled-down one, the difference being how much capacity the secondary already has when the switch happens. Multi-site active-active uses latency or weighted records with a health check on every Region, so a failed Region simply stops being returned and there is no switch to make. In every case the recovery time objective is bounded by health check detection time plus the record TTL, which is why these designs use short TTLs and why a requirement tighter than that points at Global Accelerator or a routing control from Amazon Application Recovery Controller instead, taught later in this unit,.

## Private hosted zones and split-view DNS

A private hosted zone holds records that resolve only inside the VPCs you associate with it. The VPC must have both `enableDnsSupport` and `enableDnsHostnames` set to true, and resolution happens through the VPC resolver at the VPC's base address plus two. A private hosted zone is assigned four reserved name servers that Route 53 never uses for public zones, purely because the DNS protocol requires an NS record, and querying those names from the internet returns nothing: the private zone is reachable only from an associated VPC or through an inbound Resolver endpoint. Up to 300 VPCs can be associated with one private hosted zone, and AWS recommends Route 53 Profiles above that number. A VPC can be associated with any number of private hosted zones, and association across accounts works by the zone owner creating an authorization and the VPC owner accepting it, up to 1,000 outstanding authorizations.

The routing policies allowed in a private hosted zone are simple, failover, multivalue answer, weighted, latency, geolocation and geoproximity. IP-based routing is not supported. Health checks can be attached to failover, multivalue answer, weighted, latency, geolocation and geoproximity records, but remember that Route 53 health checkers live on the internet and cannot reach private addresses, so a private zone failover is normally driven by a CloudWatch alarm health check instead of an endpoint check.

Split-view DNS, also called split-horizon DNS, is the pattern the exam names. You create a public hosted zone and a private hosted zone with the same domain name, put internal records in the private one and public records in the public one, and associate the private zone with your VPCs. Resources inside those VPCs get the internal answers, everyone else gets the public answers, and the same hostname can point at an internal load balancer inside and a CloudFront distribution outside. The public zone does not have to be in Route 53 for this to work.

Resolution order inside a VPC follows most-specific match, and the sequence is worth learning because it generates troubleshooting questions. The resolver checks whether any associated private hosted zone name is identical to, or a parent of, the queried name, and chooses the most specific one. If a matching private zone exists but contains no record of the queried name and type, the resolver returns NXDOMAIN and does not fall through to the public internet. That is the classic failure where creating a private zone for `example.com` breaks resolution of every public `example.com` name the applications also use, and the fix is to copy the public records you still need into the private zone. A Resolver forwarding rule for the same domain takes precedence over a private hosted zone, so a rule for `example.com` pointing at on-premises servers wins over a private zone of the same name associated with the same VPC.

## Route 53 VPC Resolver, hybrid DNS, and Route 53 Profiles

**Route 53 VPC Resolver**, renamed from Route 53 Resolver when **Route 53 Global Resolver**, the anycast recursive resolver for on-premises, branch and remote clients, was introduced, is the recursive resolver that every VPC gets for free. It answers three kinds of query: the internal EC2 hostnames such as `ec2-192-0-2-44.compute-1.amazonaws.com`, the records in any private hosted zone associated with the VPC, and, for everything else, it performs recursive lookups against public name servers on your behalf. It listens at the VPC base address plus two and at the link-local address `169.254.169.253`. By default it resolves only within AWS, which is the gap that hybrid designs have to close in both directions.

Two endpoint types close it, and each is a set of elastic network interfaces you create in subnets, so each carries an hourly charge per interface. An inbound endpoint gives on-premises resolvers an address in your VPC to forward queries to, so a server in the data center can resolve a name in a private hosted zone. An outbound endpoint is the exit path for queries leaving the VPC, driven by Resolver rules: a forwarding rule names a domain and the target IP addresses to forward it to, typically the domain controllers on premises, while a system rule overrides forwarding for a subdomain so it resolves normally. Rules are associated with VPCs and can be shared across accounts with **AWS Resource Access Manager (AWS RAM)**, the cross-account resource sharing service, which is how one networking account publishes the forwarding rules every workload account uses. Put endpoints in at least two Availability Zones, because each interface is a resolution path a zone failure can remove. The quotas bite at scale: 4 endpoints per Region per account and 6 IP addresses per endpoint, each address handling up to 10,000 UDP queries per second and as few as 1,500 for an inbound endpoint reached through a Network Load Balancer. Separately, each network interface in a VPC may send only 1,024 packets per second to the link-local address, a budget DNS shares with the instance metadata service, Amazon Time Sync and Windows licensing, so the DNS share is smaller still, and that one cannot be raised. The on-premises integration design belongs to [hybrid connectivity](hybrid-connectivity.md), over **AWS Direct Connect**, the dedicated private link to AWS, or **AWS Site-to-Site VPN**, the encrypted tunnel over the internet.

Resolver query logging records queries originating in a VPC and their answers, queries arriving through an inbound endpoint, queries leaving through an outbound endpoint, and the actions taken by **Route 53 Resolver DNS Firewall** rules, the filter for outbound DNS queries. Each entry carries the VPC, the source instance and address, the queried name and type, the response code and the response data. The caveat that matters is caching: only unique queries are logged, because the resolver answers repeats from its cache without consulting the log. Destinations are a CloudWatch Logs log group, an S3 bucket, or a delivery stream in **Amazon Data Firehose**, formerly Kinesis Data Firehose, the managed streaming delivery service, with a quota of 20 configurations per Region. Query logging is the evidence trail for a DNS exfiltration investigation; the control that blocks it is DNS Firewall, owned by [WAF, Shield, Firewall Manager and Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md).

**Route 53 Profiles** solve the multiplication problem that all of this creates. A Profile is a bundle of DNS configuration that you associate with VPCs, so the settings propagate instead of being rebuilt per VPC. A Profile can carry private hosted zones, Resolver forwarding and system rules, DNS Firewall rule groups, interface VPC endpoints and query logging configurations, and it directly manages three VPC-level settings: reverse DNS lookup for Resolver rules, the DNS Firewall failure mode, and DNSSEC validation. Profiles are shared to other accounts with AWS RAM, and the sharing account's VPCs pick up the configuration on association. Exactly one Profile can be associated with a VPC. When a query matches both a Profile rule and a rule or private hosted zone attached directly to the VPC, the local setting wins at equal specificity, but the more specific name wins overall, so a Profile rule for `test.example.com` beats a local rule for `example.com`. Quotas are 5 Profiles per account per Region, 1,000 VPCs and 5,000 private hosted zones per Profile, and 2 query logging configurations per Profile.

## DNSSEC signing and DNSSEC validation

DNSSEC is two separate features in Route 53 and the exam rewards keeping them apart. DNSSEC signing is something you turn on for a public hosted zone so that resolvers elsewhere can verify your answers. DNSSEC validation is something you turn on for a VPC so that the VPC resolver verifies other people's answers. Neither one implies the other.

Signing uses two keys. The zone-signing key signs the records and is managed entirely by Route 53. The key-signing key (KSK) signs the zone-signing key and is backed by an asymmetric customer managed key in **AWS Key Management Service (AWS KMS)**, the managed key service, that you own and are responsible for rotating. Two requirements are precise enough to be tested: that key must have the `ECC_NIST_P256` key spec with sign and verify usage, and it must live in the US East (N. Virginia) Region regardless of where anything else runs. You may create at most two KSKs per hosted zone. After enabling signing you establish the chain of trust by publishing a Delegation Signer (DS) record in the parent zone, usually through the registrar; if the parent's DNS provider does not support DS records, enabling DNSSEC on the child makes it unresolvable. Enabling signing also caps every record TTL in the zone at one week, silently, and a signing failure takes the whole zone down rather than degrading it, which is why AWS tells you to alarm on the `DNSSECInternalFailure` and `DNSSECKeySigningKeysNeedingAction` metrics before you switch it on.

Validation is a checkbox on the VPC. With it on, the VPC resolver cryptographically checks signatures on public signed names during recursive resolution and refuses answers that fail, which protects instances from DNS spoofing. The risk runs the other way from signing: turning validation on can break resolution of badly maintained public domains, so AWS warns that enabling it can cause an outage. If the VPC resolver forwards a query to another resolver through an outbound endpoint, the validation happens at that resolver instead, not in AWS. A Route 53 Profile can set validation consistently across every VPC it is associated with.

## Application Recovery Controller, routing controls, and zonal shift

**Amazon Application Recovery Controller (ARC)**, formerly Route 53 Application Recovery Controller, is the service that makes recovery actions themselves highly available. Its premise is that a failover which depends on a control plane API in the Region that just failed is not a failover, so ARC puts recovery switches on a dedicated data plane. It has capabilities for two blast radii: Availability Zone recovery through zonal shift and zonal autoshift, and Region recovery through routing controls, Region switch and readiness checks.

Zonal shift is the part every Associate candidate should know, because it needs no setup. You start one to move traffic for a supported resource away from an impaired Availability Zone to the healthy zones in the same Region. Shifts are manual and temporary, with an expiration you set of up to three days and can extend. The supported resources are Application Load Balancers and Network Load Balancers, with cross-zone load balancing enabled or disabled, **Amazon EC2 Auto Scaling** groups, the service that keeps a fleet at the right size, and **Amazon Elastic Kubernetes Service (Amazon EKS)**, the managed Kubernetes service. Zonal autoshift authorizes AWS to perform the shift for you, starting one when its internal telemetry from the AWS network, EC2 and Elastic Load Balancing indicates an impairment and ending it when the indicators clear. The limitation worth remembering is that a zonal shift has no effect on a load balancer that is already failing open, because it cannot force a zone to be treated as unhealthy.

Routing controls are the multi-Region equivalent, and they are simple on and off switches whose state a Route 53 health check reads. You create a cluster, which ARC implements as a data plane of endpoints in five AWS Regions, then control panels holding routing controls, then a routing control health check per control that you attach to a failover record. Flipping a routing control to Off makes its health check unhealthy, and the DNS answer changes without anyone editing a record. Because the cluster spans five Regions and you can call any of its endpoints, the switch keeps working when a Region does not.

Safety rules stop the switches from being used dangerously, and they come in two kinds. An assertion rule enforces a condition every time you change routing control states, refusing the change if the condition would be violated; the canonical example is requiring that at least one routing control in a control panel stays On, so an operator cannot turn traffic off everywhere and fail open. A gating rule works the other way: a gating routing control acts as an overall on and off switch, and while it is Off, state changes to the target routing controls it guards are refused, which is how you freeze automated failover during a maintenance window.

Readiness checks are the one part of ARC whose status changed. A readiness check continually audits whether a standby replica is genuinely ready, comparing resource quotas, capacity and routing policy configuration between cells modeled in a recovery group, and notifying you when the standby drifts from production. AWS has closed readiness checks to new customers: existing customers can keep using them, and AWS recommends onboarding multi-Region applications to ARC Region switch instead, whose plan evaluation capability monitors readiness for the plan it will execute. Region switch, routing controls, zonal shift and zonal autoshift are unaffected. AWS also states that readiness checks were never meant to trigger failover during an event: they tell you whether you could fail over, not whether you should.

## Pricing shape and the quotas that bite

Route 53 charges on four axes, and the exam tests the shape rather than the rates. You pay a monthly charge per hosted zone, 0.50 USD for each of the first 25 zones and less beyond that, which is why a hosted zone per environment per account is a real line item at scale and why subdomain delegation into one zone is often cheaper. You pay per million queries answered, with the rate rising by routing policy: standard queries are cheapest, then latency, then geolocation and geoproximity, then IP-based. Negative NXDOMAIN and NODATA answers are billed as standard queries, the cost argument for tuning the SOA minimum TTL. You pay per health check per month, at a higher rate for endpoints outside AWS and with a further charge per optional feature such as HTTPS, string matching or fast 10-second intervals, after a free allowance covering the first 50 checks against AWS endpoints. Traffic Flow bills per policy record per month, Resolver endpoints bill per network interface per hour plus per million queries, and Profiles bill per account with an allowance of associations.

The charge that decides questions is the one that does not exist: queries answered from an alias record pointing at an AWS resource are free. A CNAME to the same load balancer is billed, and a CNAME to another Route 53 name is billed twice. Combined with apex support and automatic address tracking, that makes alias the default answer for any AWS target.

The quotas to carry in are 500 hosted zones per account, 10,000 records per hosted zone with a per-record charge above that, 100 records sharing a name and type for weighted, latency, geolocation, multivalue and IP-based routing but only 30 for geoproximity, 200 active health checks per account, 255 child health checks per calculated health check, 300 VPCs per private hosted zone, 4 Resolver endpoints per Region, and 1,024 packets per second from any single network interface to the VPC resolver. Only the 1,024 packet per second link-local limit is documented as impossible to raise. The 255 child health checks, the 300 VPCs per private hosted zone and the same-name record counts have no increase path either. The rest, including the Resolver endpoints per Region and the IP addresses per endpoint, carry a request-an-increase link.

## Professional depth

At organization scale DNS is owned centrally and consumed everywhere, and the Professional exam tests the seams. The usual landing zone puts public hosted zones and the registered domains in one networking account, delegates a subdomain per environment or business unit to hosted zones in the accounts that own the workloads, and shares the hybrid plumbing outward. Delegation keeps a single 10,000-record zone from becoming a change-control bottleneck: the parent holds only NS records for each child, and each team changes its own zone. Resolver rules, DNS Firewall rule groups and query logging configurations are shared through AWS RAM, and Profiles apply the whole bundle to every VPC in a member account with one association instead of a per-VPC script. The 300-VPC limit on a private hosted zone is what forces the move to Profiles.

The second Professional theme is that failover must not depend on the thing that failed. A design whose runbook says "update the Route 53 record" depends on the Route 53 control plane in US East (N. Virginia) and on an operator. Replacing that with health checks makes the decision automatic but couples it to whatever the check can observe; replacing it with ARC routing controls makes it a deliberate human or automated switch on a five-Region data plane, with safety rules preventing a fail-open. For teams that must retain the ability to edit public DNS records during a US East (N. Virginia) impairment, Route 53 offers accelerated recovery for public hosted zones: a copy of the zone is kept in US West (Oregon), and control plane requests fail over there within about 60 minutes. It has to be enabled before an event, it covers public zones only, and during failover only a subset of APIs works, notably `ChangeResourceRecordSets` and `GetChange`, while creating or deleting hosted zones and changing DNSSEC signing do not.

> **Professional depth.** A Professional question often extends an Associate failover scenario by adding a constraint that breaks pure DNS. If the stem says the mobile client library caches DNS for an hour, or the customer's firewall allows only fixed addresses, the DNS answer is wrong regardless of TTL and the key is Global Accelerator. If it says the failover must not be automatic because a partial failure can cause split-brain writes, the key is an ARC routing control with an assertion safety rule rather than a health check.

Migration-scale work brings its own failure modes. Cutting a domain over to Route 53 means lowering the TTL at the old provider well ahead of the change, importing the zone, querying the new name servers directly to verify answers, and only then updating the registrar, remembering that resolvers cache the delegation for roughly two days. Introducing a private hosted zone for a domain that also exists publicly is the most common self-inflicted outage, because the private zone answers NXDOMAIN for every public name it does not contain. DNSSEC has the largest blast radius of any change here: a signing failure or a stale DS record makes the zone unresolvable for everyone, so it is enabled with alarms configured first.

## Worked scenario

A media company streams licensed video to viewers in North America, Europe and Japan, with application stacks behind Application Load Balancers in three Regions and a fourth, minimal stack held as a recovery site. Licensing forbids serving certain catalogs outside their territories. A large cable partner's subscribers should be pinned to the Region with the cheapest transit for that partner, regardless of measured latency. The corporate domain is also used internally, where `api.example.com` must resolve to an internal load balancer rather than the public one.

The public hosted zone holds geolocation records at the top for catalog compliance, with a default record for unmapped addresses that serves a restricted catalog rather than nothing. Beneath each territory, latency alias records point at the Application Load Balancers with `Evaluate Target Health` set to yes, so no separate health check is billed and a Region with no healthy targets drops out automatically. The cable partner's address ranges go into a CIDR collection, and IP-based records for those locations override the geolocation answer. Records at the apex are aliases, because a CNAME is impossible there and alias queries to AWS targets are free. TTLs are 60 seconds, so recovery time is bounded by detection plus a minute.

For the recovery Region the company uses ARC. A failover record pair sits under each territory branch, primary pointing at the live Regions and secondary at the recovery stack, each attached to a routing control health check rather than an endpoint check, with an assertion safety rule guaranteeing that at least one routing control stays On. Zonal autoshift is enabled on every load balancer so single-zone impairments need no Region-level decision. Internally, a private hosted zone named `example.com` carries `api.example.com` pointing at the internal load balancer, plus copies of the public records the applications still need, since a private zone returns NXDOMAIN for names it does not hold. A Route 53 Profile pushes that zone, the forwarding rules and query logging to every VPC.

When the exam asks about this scenario, the keyed answer is geolocation at the top for licensing, latency alias records beneath it for performance, IP-based records to override for the known partner ranges, and ARC routing controls rather than endpoint health checks for the Region-level failover decision.

## Exam lens

- "Route users to the Region with the best performance" maps to latency-based routing; geolocation is the distractor, because it routes on where the user is, not on measured latency.
- "Content may be served only in certain countries" maps to geolocation routing, with a default record so unmapped addresses still get an answer.
- "Shift a percentage of traffic toward one Region without changing endpoints" maps to geoproximity routing with a positive bias from 1 to 99.
- "Send 5 percent of traffic to the new version" maps to weighted routing; a zero-weight record still answers if every nonzero-weight record is unhealthy.
- "Active-passive with a static maintenance page" maps to failover routing with a primary alias to the load balancer and a secondary alias to an S3 website bucket.
- "Return several healthy IP addresses so clients can retry" maps to multivalue answer routing, up to eight records, each with its own health check.
- "Route a named internet service provider's customers to a specific endpoint" maps to IP-based routing with a CIDR collection; it is the one policy unavailable in a private hosted zone.
- "Point the bare domain at a load balancer at the lowest cost" maps to an alias record; a CNAME cannot exist at the apex and its queries are charged.
- "Health check a resource with no public IP address" maps to a CloudWatch alarm health check; an endpoint health check cannot reach private addresses.
- "Users still reached the failed server after DNS was updated" maps to resolver caching of the old TTL; lower the TTL before a cutover.
- "Failover must not depend on DNS caching, and clients need fixed IP addresses" maps to AWS Global Accelerator, not to any routing policy.
- "The same hostname must resolve differently inside the VPC" maps to split-view DNS with a public and a private hosted zone of the same name.
- "Creating a private hosted zone broke resolution of public names in that domain" maps to the NXDOMAIN rule; add the needed public records to the private zone.
- "On-premises servers must resolve names in a private hosted zone" maps to a Route 53 Resolver inbound endpoint; an outbound endpoint with forwarding rules is the opposite direction.
- "Apply the same DNS configuration to hundreds of VPCs across accounts" maps to Route 53 Profiles shared with AWS RAM.
- "Prove which instance queried an attacker-controlled domain" maps to Resolver query logging; DNS Firewall is the control that blocks it.
- "Recover from a single impaired Availability Zone with no prior setup" maps to zonal shift, or zonal autoshift to let AWS do it.
- "A recovery switch that keeps working when the Region is down" maps to an ARC routing control on its five-Region cluster, with a safety rule preventing fail-open.
- "Resolvers must be able to verify our answers were not tampered with" maps to DNSSEC signing with a KSK backed by an ECC_NIST_P256 KMS key in US East (N. Virginia); DNSSEC validation on a VPC is the distractor, because it verifies other people's answers.

## Knowledge check

### 1. Serving a global audience from three Regions (Associate)

A company runs identical copies of its web application behind Application Load Balancers in three AWS Regions. Users are spread across every continent, and the company wants each user's request handled by the Region that gives that user the fastest network response. The three copies serve identical content and there are no licensing or regulatory restrictions on where a user is served from.

Which solution will meet these requirements with the LEAST latency?

- **A)** Create a simple record that contains the IP addresses of all three load balancers.
- **B)** Create geolocation records that map each continent to one of the three Regions.
- **C)** Create latency alias records, one for each Region, that point at that Region's Application Load Balancer.
- **D)** Create weighted records with equal weights for the three load balancers.

<details><summary>Answer</summary>

**Answer: C.** Latency-based routing compares AWS's measured latency between the querying resolver and each Region you have created a latency record for, and returns the record for the Region with the lowest latency, which is exactly the stated requirement. Alias records are the correct form for a load balancer target. A returns all three values in random order with no latency awareness and no health checking. B routes on the user's geographic location, which is a proxy for latency and often a poor one, and the stem says there are no geographic restrictions to enforce. D distributes traffic in fixed proportions regardless of where the user is, which guarantees that roughly two thirds of users are sent to a distant Region.

*Where this is covered: Routing policies.*

</details>

### 2. Pointing a bare domain at a load balancer (Associate)

A company owns `example.com` and wants that exact name, with no `www` prefix, to resolve to an Application Load Balancer in its account. The load balancer's IP addresses change over time. The company wants to avoid unnecessary DNS query charges.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Create an alias A record for `example.com` that targets the Application Load Balancer.
- **B)** Create a CNAME record for `example.com` that points at the load balancer's DNS name.
- **C)** Create an A record for `example.com` containing the load balancer's current IP addresses and a script that updates them.
- **D)** Create a CNAME record for `www.example.com` and redirect `example.com` to it at the registrar.

<details><summary>Answer</summary>

**Answer: A.** An alias record can be created at the zone apex, resolves to the load balancer's current addresses automatically as they change, and Route 53 does not charge for queries to alias records that target AWS resources. B is impossible: the DNS protocol forbids a CNAME at the zone apex, and CNAME queries are charged. C would work briefly but breaks whenever the load balancer's addresses change, and it adds the operational burden the managed alias removes. D does not make `example.com` itself resolve to the application, and registrar-level redirection is not a DNS record type Route 53 provides.

*Where this is covered: Alias records compared with CNAME records.*

</details>

### 3. Serving a maintenance page during an outage (Associate)

An ecommerce company runs its storefront behind an Application Load Balancer. When the storefront is completely unavailable, the company wants visitors to see a static "we will be back shortly" page instead of a browser error, with no servers running to serve that page.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create a multivalue answer record containing the load balancer and a second load balancer that serves the static page.
- **B)** Create a simple record with two values, the storefront load balancer and an Amazon S3 website endpoint.
- **C)** Create weighted records with a weight of 255 for the storefront and a weight of 1 for a second Application Load Balancer serving the page.
- **D)** Create a failover alias record pair: a primary alias to the load balancer with Evaluate Target Health enabled, and a secondary alias to an Amazon S3 bucket configured as a static website.

<details><summary>Answer</summary>

**Answer: D.** Failover routing is the active-passive policy, and AWS documents the pattern of a primary resource with an S3 website bucket as the secondary holding a temporarily unavailable message. Evaluate Target Health lets Route 53 use the load balancer's own health rather than a separate billed health check, and the S3 bucket needs no running servers. A cannot be built, because a multivalue answer record cannot be an alias to a load balancer. B cannot be built either, because a simple record accepts only one alias target, and even as plain values a simple record is never health checked, so the failed storefront would keep being returned. C sends about one in 256 visitors to the maintenance page at all times and requires a second load balancer, which is both wrong and not the least overhead.

*Where this is covered: Health checks and DNS failover.*

</details>

### 4. Spreading traffic across servers without a load balancer (Associate)

A company runs six identical application servers on Amazon EC2 instances, each with its own public IP address. The application client retries a different address if the first one refuses a connection. The company wants DNS to spread requests across the servers and to stop returning the address of any server that fails a health check. It does not want to introduce a load balancer.

Which solution will meet these requirements?

- **A)** Create one simple record containing all six IP addresses.
- **B)** Create six multivalue answer records, one per IP address, each associated with its own Route 53 health check.
- **C)** Create six weighted records with equal weights and no health checks.
- **D)** Create six latency records, one per IP address.

<details><summary>Answer</summary>

**Answer: B.** Multivalue answer routing returns up to eight healthy records chosen at random, gives different answers to different resolvers, and withholds the value of any record whose health check is unhealthy, which is exactly the described behavior. A returns all six values in random order but simple records are never health checked, so a failed server keeps being returned. C spreads traffic but, with no health checks attached, Route 53 treats every record as healthy and never removes the failed server. D is meaningless here: latency records are tagged with an AWS Region and compare latency between users and AWS data centers, and all six servers would have to be in different Regions for the policy to express anything.

*Where this is covered: Routing policies.*

</details>

### 5. Internal and external names for one domain (Associate)

A company uses `example.com` for its public website, served from a CloudFront distribution. It now wants `api.example.com` to resolve to an internal Network Load Balancer for applications running inside its VPCs, while external users continue to reach the public website normally. After a first attempt, applications inside the VPC could no longer resolve `www.example.com`.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Delete the public hosted zone for `example.com` and use only the private hosted zone.
- **B)** Create a private hosted zone named `example.com`, associate it with the VPCs, and add an `api.example.com` record pointing at the internal Network Load Balancer.
- **C)** Create a Route 53 Resolver outbound endpoint with a forwarding rule for `example.com`.
- **D)** Turn off `enableDnsSupport` on the VPCs so that queries bypass the private hosted zone.
- **E)** Add records for the public names that VPC resources still need, such as `www.example.com`, to the private hosted zone.

<details><summary>Answer</summary>

**Answer: B and E.** B is the split-view DNS pattern: a private hosted zone with the same name as the public zone gives VPC resources different answers from everyone else. E fixes the failure described in the stem, because when a matching private hosted zone exists but holds no record for the queried name and type, the VPC resolver returns NXDOMAIN and does not fall through to a public resolver. A removes public resolution for every internet user. C forwards queries to an on-premises or external resolver, which is not where these names live and would not restore public resolution inside the VPC. D disables the VPC resolver entirely, breaking all name resolution including AWS service endpoints, and private hosted zones require that attribute to be true.

*Where this is covered: Private hosted zones and split-view DNS.*

</details>

### 6. Moving a share of traffic toward one Region (Associate)

A company serves users in Europe from Regions in Ireland and Frankfurt. Capacity was recently added in Ireland, and the company wants a larger share of European users, including some who are physically closer to Frankfurt, to be served from Ireland. It wants to make the change gradually and to reverse it easily, without changing any endpoint or creating new records for each country.

Which solution will meet these requirements?

- **A)** Change the latency records so that Ireland is listed first.
- **B)** Create geolocation records for every European country and map more of them to Ireland.
- **C)** Use geoproximity routing and apply a positive bias to the Ireland record, increasing it in small steps.
- **D)** Use weighted routing with a higher weight on Ireland and remove the Frankfurt record.

<details><summary>Answer</summary>

**Answer: C.** Geoproximity routing applies a bias between 1 and 99 that expands the geographic area a resource serves, using the formula that treats the biased distance as the actual distance multiplied by one minus the bias divided by 100, so a positive bias pulls in users who are physically closer to the other Region. AWS recommends changing the bias in small steps, and lowering it reverses the change. A does nothing: latency records have no ordering, and Route 53 picks the Region with the lowest measured latency. B would work but requires a record per country and a manual reassignment each time the balance changes, which is the opposite of a gradual adjustable shift. D ignores geography entirely and removing the Frankfurt record sends all European traffic to Ireland rather than a share of it.

*Where this is covered: Routing policies.*

</details>

### 7. Failing over on a metric rather than an HTTP response (Associate)

A company runs a data processing service on EC2 instances in private subnets in two Regions. The instances have no public IP addresses and are not reachable from the internet. The company wants Route 53 to stop sending traffic to a Region when that Region's processing backlog, published as a custom Amazon CloudWatch metric, exceeds a threshold.

Which solution will meet these requirements?

- **A)** Create an endpoint health check against each instance's private IP address and attach it to the records.
- **B)** Create a calculated health check that monitors the instances' status checks.
- **C)** Create an endpoint health check with string matching against a health page on each instance.
- **D)** Create a CloudWatch alarm on the backlog metric in each Region, create a Route 53 health check that monitors that alarm, and associate each health check with that Region's record.

<details><summary>Answer</summary>

**Answer: D.** A CloudWatch alarm health check lets any metric drive DNS, which is the only way to health check on a value that no external probe can observe, and it is also the standard way to health check resources that Route 53's internet-based checkers cannot reach. A is not possible: Route 53 cannot create health checks for private, nonroutable addresses. B would require child health checks that can reach the instances, which is the same problem, and a calculated check only aggregates other Route 53 health checks. C still requires the checkers to reach the instances over the internet, and the stem says they have no public addresses.

*Where this is covered: Health checks and DNS failover.*

</details>

### 8. Two-way name resolution with a data center (Professional)

A company connects its data center to several VPCs across multiple accounts over AWS Direct Connect. Applications in the VPCs must resolve names in the on-premises Active Directory domain `corp.internal`, and servers in the data center must resolve names in a Route 53 private hosted zone named `aws.example.com`. The company wants the resolution paths to survive the loss of one Availability Zone and wants every account to use the same configuration.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create a Route 53 Resolver outbound endpoint with interfaces in at least two Availability Zones and a forwarding rule for `corp.internal` that targets the on-premises DNS servers, and share the rule with the other accounts using AWS Resource Access Manager.
- **B)** Change the VPC DHCP option set in every account to list only the on-premises domain controllers as domain name servers.
- **C)** Create a public hosted zone for `aws.example.com` and let the on-premises servers resolve it over the internet.
- **D)** Create a Route 53 Resolver inbound endpoint with interfaces in at least two Availability Zones, and configure the on-premises DNS servers to forward `aws.example.com` to those endpoint IP addresses.
- **E)** Enable DNSSEC validation on every VPC so that queries for `corp.internal` are forwarded correctly.

<details><summary>Answer</summary>

**Answer: A and D.** A is the outbound direction: a forwarding rule sends queries for the named domain out through the endpoint to the on-premises resolvers, and sharing the rule through AWS RAM gives every account the same configuration without rebuilding it. D is the inbound direction, giving the data center addresses inside the VPC to forward to. Placing endpoint interfaces in at least two Availability Zones satisfies the resilience requirement. B replaces the VPC resolver with the on-premises servers for everything, which breaks resolution of private hosted zones and AWS service endpoint names. C exposes internal names publicly and still does not give VPC resources a path to `corp.internal`. E verifies signatures on public names and has nothing to do with forwarding.

*Where this is covered: Route 53 VPC Resolver, hybrid DNS, and Route 53 Profiles.*

</details>

### 9. A failover switch that survives the Region it is failing away from (Professional)

A payments company runs an active-standby architecture in two Regions. Its runbook requires an operator to decide when to fail over, because an automated switch during a partial failure could cause duplicate settlement. The previous design used an Amazon Route 53 record change, but a rehearsal showed that the operator could not reliably make the change while the primary Region was impaired, and a second rehearsal ended with an operator turning both Regions off.

Which solution will meet these requirements?

- **A)** Attach endpoint health checks to failover records and let Route 53 switch automatically when the primary fails.
- **B)** Create an Amazon Application Recovery Controller cluster with routing controls and routing control health checks attached to the failover records, and add an assertion safety rule requiring at least one routing control to remain On.
- **C)** Attach CloudWatch alarm health checks to the failover records, with the insufficient data status set to unhealthy.
- **D)** Reduce the record TTL to 10 seconds and document a faster manual record change procedure.

<details><summary>Answer</summary>

**Answer: B.** An ARC routing control is a deliberate on and off switch whose state a Route 53 health check reads, so the operator keeps the decision, and the cluster is a data plane of endpoints in five AWS Regions, so the switch remains usable when one Region is impaired. An assertion safety rule enforces a condition on every state change and is the documented way to prevent the fail-open case where every routing control is turned Off. A removes the human decision the stem requires. C also removes the human decision and, with insufficient data treated as unhealthy, is more likely to fire during exactly the partial failure the company is trying to avoid acting on. D leaves the failover dependent on the Route 53 control plane and on an operator making a change during an event, which the rehearsal already showed does not work.

*Where this is covered: Application Recovery Controller, routing controls, and zonal shift.*

</details>

### 10. DNS standards across 200 accounts, and a client that caches (Professional)

A platform team manages 200 accounts with more than 400 VPCs. Every VPC must use the same on-premises forwarding rules, the same DNS Firewall rule groups and the same query logging configuration, and new VPCs must pick these up without a per-VPC script. Separately, a mobile client library used by the company's customers caches DNS answers for up to an hour, and product owners require that a Regional failover take effect for those clients within one minute.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Associate a single private hosted zone with all 400 VPCs and rely on its records for forwarding.
- **B)** Reduce the TTL on the public records to 30 seconds and rely on Route 53 failover routing for the mobile clients.
- **C)** Create a Route 53 Profile containing the Resolver rules, DNS Firewall rule groups and query logging configuration, share it with the member accounts using AWS Resource Access Manager, and associate it with each VPC.
- **D)** Create a Resolver outbound endpoint in each of the 400 VPCs and replicate the forwarding rules into each account with CloudFormation.
- **E)** Put the application behind AWS Global Accelerator and let its static anycast IP addresses absorb the Regional failover.

<details><summary>Answer</summary>

**Answer: C and E.** C is what Profiles exist for: one bundle of DNS configuration, shared through AWS RAM, associated with a VPC so the settings propagate, and a private hosted zone tops out at 300 VPC associations, which 400 VPCs exceed. E solves the caching problem, because Global Accelerator's IP addresses never change, so the client's cached answer stays valid while AWS redirects the packets, and AWS documents that an unhealthy endpoint is taken out of service in less than one minute. A does not carry forwarding rules, firewall rule groups or logging configuration and hits the 300-VPC quota. B cannot work: the client caches for an hour regardless of the TTL the company publishes, so no record change reaches it inside one minute. D produces the right behavior but multiplies endpoint charges by 400 and is the per-account replication the stem rules out.

*Where this is covered: Route 53 VPC Resolver, hybrid DNS, and Route 53 Profiles.*

</details>

## Summary

Route 53 is a sequence of decisions, and the exam asks them one at a time. Decide first whether the name is public or private, because a private hosted zone answers only inside associated VPCs and returns NXDOMAIN for names it does not hold, and a public and private zone of the same name is how split-view DNS is built. Decide next how to express the target: an alias record for anything in the supported AWS list, because it works at the zone apex, tracks the target's addresses, and costs nothing per query, and a CNAME only for external names below the apex. Then pick the routing policy from the requirement in the stem: latency for speed, geolocation for licensing and sovereignty, geoproximity with bias to shift a share of traffic, weighted for canaries, failover for active-passive, multivalue answer for health-checked client-side spreading, and IP-based when you know the client address ranges. Attach health checks, choosing endpoint, calculated or CloudWatch alarm by what can be observed, and remember that when everything is unhealthy Route 53 answers as if everything is healthy. Finally, bound recovery time by the TTL, and when a client caches worse than that, move the decision off DNS to Global Accelerator or an ARC routing control.

## Related units

- [Amazon VPC](vpc.md): the VPC resolver, DNS attributes, DHCP option sets and the endpoints that private records point at
- [Hybrid connectivity](hybrid-connectivity.md): the on-premises integration design that Resolver inbound and outbound endpoints serve
- [Amazon CloudFront](cloudfront.md): the edge cache that alias records most often target, and the alternative to Regional routing
- [AWS Global Accelerator](global-accelerator.md): static anycast addresses when DNS caching or fixed IP addresses rule out a routing policy
- [Elastic Load Balancing](../02-compute/elastic-load-balancing.md): the alias target behind most records, and the source of Evaluate Target Health
- [Backup and disaster recovery](../01-storage/backup-and-disaster-recovery.md): the DR strategy reference that Route 53 failover and ARC implement
- [WAF, Shield, Firewall Manager and Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md): Route 53 Resolver DNS Firewall and the rest of the edge protection set
- [Amazon API Gateway](api-gateway.md): custom domain names that alias records point at

## Sources

- [What is Amazon Route 53?](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html): the three functions, and the feature list including VPC Resolver, Traffic Flow and Profiles
- [How internet traffic is routed to your website or web application](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/welcome-dns-service.html): the resolution path and the two-day caching of name server delegation
- [How domain registration works](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/welcome-domain-registration.html): Amazon Registrar and Gandi, and the hosted zone created at registration
- [NS and SOA records that Amazon Route 53 creates for a public hosted zone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/SOA-NSrecords.html): the four name servers in four top-level domains and the negative caching rule
- [Supported DNS record types](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/ResourceRecordTypes.html): the record type list, the CNAME apex restriction and the SPF deprecation
- [ChangeResourceRecordSets](https://docs.aws.amazon.com/Route53/latest/APIReference/API_ChangeResourceRecordSets.html): transactional change batches and the 60-second PENDING to INSYNC propagation
- [Choosing between alias and non-alias records](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resource-record-sets-choosing-alias-non-alias.html): the alias target list, apex support, TTL rules and the free alias query rule
- [Choosing a routing policy](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html): the eight routing policies and which work in a private hosted zone
- [Simple routing](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-simple.html): multiple values in one record and the absence of health checking
- [Weighted routing](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-weighted.html): the weight share formula and the zero-weight fallback behavior
- [Latency-based routing](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-latency.html): AWS latency data, one record per Region and the warning about non-AWS resources
- [Geolocation routing](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-geo.html): continent, country and subdivision, smallest region wins, and the default record
- [Geoproximity routing](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-geoproximity.html): the bias range from -99 to 99 and the biased distance formula
- [IP-based routing](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-ipbased.html): CIDR collections and locations, prefix length limits and the private hosted zone exclusion
- [Multivalue answer routing](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-multivalue.html): up to eight healthy records and the all-unhealthy behavior
- [Types of Amazon Route 53 health checks](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/health-checks-types.html): endpoint, calculated, CloudWatch alarm and ARC routing control health checks
- [How Amazon Route 53 determines whether a health check is healthy](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover-determining-health-of-endpoints.html): the 18 percent rule, response time limits and 255 child health checks
- [Values that you specify when you create or update health checks](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/health-checks-creating-values.html): intervals, failure threshold, string matching and the insufficient data options
- [How Amazon Route 53 chooses records when health checking is configured](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/health-checks-how-route-53-chooses-records.html): the all-unhealthy rule and the failover record behavior
- [Active-active and active-passive failover](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover-types.html): the two failover shapes and the S3 maintenance page pattern
- [Working with private hosted zones](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zones-private.html): the reserved name servers and how private zones are reached
- [Considerations when working with a private hosted zone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zone-private-considerations.html): VPC attributes, supported policies, split-view DNS and the NXDOMAIN rule
- [What is Route 53 VPC Resolver?](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html): the rename from Route 53 Resolver, inbound and outbound endpoints and forwarding rules
- [Resolver query logging](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-query-logs.html): what is logged, the cache caveat and the three destinations
- [Enabling DNSSEC validation in Amazon Route 53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dnssec-validation.html): per-VPC validation and the forwarding caveat
- [What are Amazon Route 53 Profiles?](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/profiles.html): the resources a Profile carries, RAM sharing and the precedence table
- [Configuring DNSSEC signing in Amazon Route 53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring-dnssec.html): KSK and ZSK responsibilities, the one-week TTL cap and the DS record warning
- [Working with customer managed keys for DNSSEC](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring-dnssec-cmk-requirements.html): the ECC_NIST_P256 key spec and the US East (N. Virginia) requirement
- [Enabling accelerated recovery for managing public DNS records](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/accelerated-recovery.html): the 60-minute control plane failover to US West (Oregon) and its restrictions
- [Quotas](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/DNSLimitations.html): hosted zone, record, health check, Resolver endpoint and Profile quotas
- [What is ARC?](https://docs.aws.amazon.com/r53recovery/latest/dg/what-is-route53-recovery.html): the rename to Amazon Application Recovery Controller and its five capabilities
- [Routing control in ARC](https://docs.aws.amazon.com/r53recovery/latest/dg/routing-control.html): clusters as a data plane of endpoints in five AWS Regions
- [Creating safety rules for routing control](https://docs.aws.amazon.com/r53recovery/latest/dg/routing-control.safety-rules.html): assertion rules and gating rules
- [Readiness check in ARC](https://docs.aws.amazon.com/r53recovery/latest/dg/recovery-readiness.html): what readiness checks audit and why they are not a failover trigger
- [ARC readiness check availability change](https://docs.aws.amazon.com/r53recovery/latest/dg/arc-readiness-availability-change.html): closed to new customers, with Region switch as the recommended alternative
- [Supported resources for zonal shift](https://docs.aws.amazon.com/r53recovery/latest/dg/arc-zonal-shift.resource-types.html): the four resource types and the fail-open load balancer caveat
- [Amazon Route 53 pricing](https://aws.amazon.com/route53/pricing/): hosted zone, query, health check, Resolver endpoint, Traffic Flow and Profile charges
- [AWS Global Accelerator FAQs](https://aws.amazon.com/global-accelerator/faqs/): the DNS caching comparison, sub-minute endpoint failover and the CloudFront distinction
