# Elastic Load Balancing

**Where it sits on the exams.** **Elastic Load Balancing (ELB)** is the managed service that publishes one endpoint, checks the health of the resources registered behind it, and distributes client traffic across only the healthy ones in several Availability Zones. It is the component that turns a set of individual servers into a tier that survives the loss of any one of them, and it is where certificate termination, request routing and inline traffic inspection usually live. It appears in SAA-C03 tasks 2.1, 2.2, 3.4, 4.2 and 4.4, and in SAP-C02 tasks 1.3 and 3.4, most often behind the phrase "load balancing concepts" or as an explicit comparison of Layer 7 against Layer 4 against Gateway. The rule of thumb the exam rewards is to choose the load balancer from what the routing decision has to see: an HTTP request selects an Application Load Balancer, a TCP or UDP connection selects a Network Load Balancer, and every IP packet on its way to a firewall appliance selects a Gateway Load Balancer.

## The four load balancer types and how to choose one

Elastic Load Balancing offers four types. An **Application Load Balancer (ALB)** operates at Layer 7 of the Open Systems Interconnection model, parses HTTP and HTTPS requests, and routes each one by rules you write. A **Network Load Balancer (NLB)** operates at Layer 4, forwards TCP, UDP and TLS flows with very low added latency, and gives each enabled subnet a static IP address. A **Gateway Load Balancer (GWLB)** is a Layer 3 gateway with Layer 4 load balancing that listens for all IP packets on all ports and exists to put a fleet of third-party virtual appliances in the traffic path. A **Classic Load Balancer (CLB)** is the previous generation, mixing Layer 4 and Layer 7 behavior with no target groups and no listener rules.

The Classic Load Balancer is not retired. AWS still sells it, still prices it by the hour plus a per-GB data processing charge, and still publishes its user guide, but every ELB page labels it the previous generation and recommends migrating, and a wizard builds an equivalent Application or Network Load Balancer from its configuration. Treat a scenario that mentions one as an invitation to migrate. AWS documents two benefits it retains over an Application Load Balancer specifically, TCP and SSL listeners and stickiness from an application-generated cookie, but neither is a reason to choose it today: a Network Load Balancer covers the first and an Application Load Balancer has since gained the second.

Read this table one row at a time: find the row that restates the requirement in the stem, then take the column whose cell satisfies it.

| Property | Application Load Balancer | Network Load Balancer | Gateway Load Balancer | Classic Load Balancer |
|---|---|---|---|---|
| Layer | 7 | 4 | Layer 3 gateway plus Layer 4 load balancing | 4 and 7 |
| Listener protocols | HTTP, HTTPS, gRPC | TCP, UDP, TLS | IP, all ports | TCP, SSL/TLS, HTTP, HTTPS |
| Target types | instance, IP, Lambda function | instance, IP, Application Load Balancer | instance, IP | EC2 instances registered directly, no target group |
| Static IP address | No, clients use the DNS name | Yes, one per enabled subnet, optionally an Elastic IP address | No, reached through a route table entry to an endpoint | No |
| TLS termination | Yes, and a certificate list with SNI | Yes on a TLS listener, pass-through on a TCP listener | No, the flow is never terminated | Yes |
| WebSockets | Yes | Yes | Yes | No |
| Routing capability | Listener rules on host, path, HTTP header, HTTP method, query string and source IP | Flow hash over protocol, source and destination address and port, and TCP sequence number | Flow stickiness to one appliance using a 5-tuple, 3-tuple or 2-tuple hash | Round robin for TCP listeners, least outstanding requests for HTTP and HTTPS |
| Use case that selects it | HTTP microservices, host and path routing, user authentication, AWS WAF inspection | Millions of flows, static or Elastic IP addresses, non-HTTP protocols, PrivateLink endpoint services | Inserting firewall, intrusion detection and deep packet inspection appliances inline | Existing deployments only, until they are migrated |

Two rows decide most questions. A fixed IP address that a partner allowlists selects a Network Load Balancer, because an Application Load Balancer publishes only a changing DNS name. Transparent third-party inspection selects a Gateway Load Balancer, the only type that never terminates the flow.

The two current generation types can also be combined. Registering an Application Load Balancer as the single target of a Network Load Balancer target group gives Layer 7 rules behind a static IP address, or behind an **AWS PrivateLink** endpoint service, the mechanism that exposes one service privately to consumers in other **Amazon Virtual Private Cloud (Amazon VPC)** networks, the isolated virtual networks in which instances and load balancers run. Both must be in one VPC and account, an Application Load Balancer can be a target of at most two Network Load Balancers, and each consumes 50 of the per-zone target allowance, or 100 with cross-zone enabled.

## Listeners, rules, target groups, and target types

A listener watches a protocol and port for connections. An Application Load Balancer listener speaks HTTP or HTTPS on any port from 1 to 65535, supports WebSockets through an HTTP connection upgrade, and supports HTTP/2 on HTTPS listeners with up to 128 parallel requests per connection. A Network Load Balancer listener speaks TCP, UDP or TLS. A Gateway Load Balancer has one listener that accepts all IP packets on all ports and cannot be configured further.

The Application Load Balancer's listener rules are what the exam means by Layer 7 routing. Each rule has a priority, one or more conditions, and exactly one routing action that runs last. Rules are evaluated from the lowest priority number upward, and the default rule, which can have no conditions and whose priority cannot be changed, runs last if nothing else matched. The condition types are `host-header`, `http-request-method`, `path-pattern` and `source-ip`, of which a rule may carry at most one each, plus `http-header` and `query-string`, of which a rule may carry several. The routing actions are `forward` to one or more target groups, `redirect` to another URL, and `fixed-response`, which returns a status code and body without contacting any target. An HTTPS listener can additionally run `authenticate-cognito` or `authenticate-oidc` first, so the load balancer completes an OpenID Connect or **Amazon Cognito** sign-in, the managed user directory and identity service, before a request reaches the application. The default quotas are 100 rules and 100 target groups per load balancer, with five target groups per forward action.

A target group owns the health check, the routing algorithm and the stickiness setting, and its type fixes what you can register and cannot be changed afterward. The `instance` type routes to the primary private address of an instance in **Amazon EC2**, the service that rents virtual servers. The `ip` type routes to any private address in the load balancer's VPC, in RFC 1918 ranges, or in `100.64.0.0/10`, which lets one target group reach a peered VPC, a database, a container with its own interface, or an on-premises server across **AWS Direct Connect**, the dedicated private connection to AWS, or **AWS Site-to-Site VPN**, the encrypted tunnel over the internet. Publicly routable addresses can never be registered. Only an Application Load Balancer supports the `lambda` type, which invokes a function in **AWS Lambda**, the event-driven function service, directly rather than over a network connection, with a 1 MB ceiling on both request body and response and no WebSocket support. Only a Network Load Balancer supports the `alb` type.

An Application Load Balancer selects targets with `round_robin` by default, `least_outstanding_requests` when requests vary widely in cost, or `weighted_random`, the only algorithm supporting Automatic Target Weights anomaly mitigation. A Network Load Balancer instead hashes each flow, so every packet of one TCP connection reaches the same target for its lifetime. Idle timeouts differ: an Application Load Balancer defaults to 60 seconds and is configurable, a Network Load Balancer TCP flow defaults to 350 seconds and is settable from 60 to 6,000, a TLS listener is fixed at 350 seconds, and a UDP flow at 120 seconds.

## Health checks, deregistration delay, and sticky sessions

Health checks are configured per target group and take the same shape on both current generation load balancers. `HealthCheckProtocol` is HTTP or HTTPS on an Application Load Balancer and defaults to TCP on a Network Load Balancer. `HealthCheckIntervalSeconds` ranges from 5 to 300 and defaults to 30. `HealthCheckTimeoutSeconds` ranges from 2 to 120, defaulting to 5 seconds for instance and IP targets, 30 for Lambda targets, and 6 or 10 seconds on a Network Load Balancer. `HealthyThresholdCount` and `UnhealthyThresholdCount` both range from 2 to 10, defaulting to 5 consecutive successes to return a target to service and 2 consecutive failures to take it out. The `Matcher`, shown as Success codes in the console, defaults to 200 on an Application Load Balancer and to 200-399 on a Network Load Balancer. Detection time is the interval multiplied by the unhealthy threshold, 60 seconds at the defaults, and shortening both answers a stem asking for faster failure detection.

The behavior when everything is unhealthy is examined precisely because it surprises people. If a target group holds only unhealthy targets, the load balancer fails open and sends requests to all of them regardless of health, on the reasoning that a degraded response beats a guaranteed error; a Network Load Balancer also fails open on an empty target group. Target group health thresholds give finer control. A minimum healthy count or percentage for DNS failover withdraws that zone's load balancer addresses from DNS so clients resolve only to healthy zones; one for routing failover makes the node send traffic to unhealthy targets in its own zone rather than overload the few healthy ones. The DNS threshold must be greater than or equal to the routing threshold, and a withdrawal takes up to the 60-second record time to live to reach clients.

Connection draining is called deregistration delay on the current generation types, and it is the `deregistration_delay.timeout_seconds` attribute, ranging from 0 to 3,600 seconds with a default of 300. A deregistering target, whether removed by an operator or by **Amazon EC2 Auto Scaling**, the service that keeps a fleet at the right size, enters the `draining` state, stops receiving new requests, and gets that long for in-flight requests to finish before moving to `unused` and becoming eligible for termination. A target with no in-flight requests and no active connections deregisters immediately. Lower the delay when scale-in is too slow, raise it when long requests are cut off. The complement is `slow_start.duration_seconds`, 30 to 900 seconds and off by default, which ramps a newly registered target up to its full share instead of hitting a cold cache with full load.

Sticky sessions bind a client to one target, and the mechanism differs by type. An Application Load Balancer offers duration-based stickiness, `stickiness.type` set to `lb_cookie`, issuing an encrypted cookie named `AWSALB` whose duration you set from 1 second to 7 days, default 1 day. It also offers application-based stickiness, `stickiness.type` set to `app_cookie`, where the target sets a session cookie whose name you register on the target group and the load balancer issues a companion cookie named `AWSALBAPP`. Application-based stickiness is the answer when the application already has a session cookie, and the only option when several layers of load balancers each need stickiness, because `AWSALB` is a single reserved name usable at one layer. A Network Load Balancer has one option, `source_ip`, coarse enough that every client behind one NAT device lands on one target, and unsupported on TLS listeners. Two constraints decide questions: an Application Load Balancer refuses stickiness when cross-zone load balancing is off on the target group, and WebSocket connections are inherently sticky because the upgraded connection stays with the target that accepted it.

## Availability Zones, cross-zone load balancing, and resilience

Enabling an Availability Zone creates a load balancer node there, and targets registered in a zone that is not enabled receive nothing. An Application Load Balancer requires at least two zone subnets, each a `/27` or larger with at least eight free addresses, because it consumes those addresses to scale out; a subnet that runs out leaves the load balancer running with insufficient capacity and returning 5xx errors. A Network Load Balancer creates one network interface per enabled subnet and takes a static IP address from it, optionally an Elastic IP address attached at creation. Clients reach an Application Load Balancer only through its DNS name, whose records carry a 60-second time to live so Elastic Load Balancing can remap addresses as it scales.

Cross-zone load balancing decides whether a node may send traffic outside its own zone, and the default differs by type in a way the exam tests directly. On an Application Load Balancer it is always on at the load balancer level and can only be turned off per target group. On a Network Load Balancer and a Gateway Load Balancer it is off by default. On a Classic Load Balancer it is off by default through the API and the AWS CLI but selected by default in the console. The billing consequence follows the same split: AWS does not charge inter-Availability Zone data transfer for cross-zone traffic on an Application Load Balancer or a Classic Load Balancer, and does charge it on a Network Load Balancer and a Gateway Load Balancer when you enable the feature. Turning it on also changes quotas, because a Network Load Balancer's 500 targets per Availability Zone become 500 targets for the whole load balancer once cross-zone is enabled.

Cross-zone on gives even utilization across an unevenly sized fleet; off gives a tighter blast radius and no inter-zone charge. Ten targets split two in one zone and eight in another each receive 10 percent of traffic with cross-zone on, and 25 percent and 6.25 percent respectively with it off, so roughly equal target counts per zone are what make the off setting safe.

Two mechanisms handle a sick zone rather than a sick target. Zonal shift, a capability of **Amazon Application Recovery Controller (ARC)**, the service that manages recovery readiness and zonal failover, moves a load balancer's traffic away from one impaired Availability Zone in a single action and works on a Network Load Balancer whether cross-zone is on or off. For Region-level failover, an alias record in **Amazon Route 53**, the managed DNS service, with evaluate target health set, marks the record unhealthy when any attached target group is unhealthy or empty, so a failover routing policy sends clients to a load balancer in another Region.

## TLS termination, SNI, and mutual TLS

Terminating TLS at the load balancer moves handshake cost off the fleet and puts certificate renewal in one place. An HTTPS listener on an Application Load Balancer, or a TLS listener on a Network Load Balancer, needs exactly one default certificate, and AWS recommends issuing it from **AWS Certificate Manager (ACM)**, the service that provisions and renews public and private certificates, which supports RSA keys of 2048, 3072 and 4096 bits and all ECDSA key sizes. Issuance, validation and renewal belong to [AWS Certificate Manager](../07-security/acm.md); what matters here is the binding. A TCP listener on a Network Load Balancer is the opposite choice, passing encrypted bytes through untouched so the targets decrypt, which is the answer whenever a stem says the load balancer must not see plaintext or hold the private key.

Server Name Indication (SNI) is how one listener serves many domains. Beyond the default certificate you attach a certificate list, 25 additional certificates by default, and the load balancer picks one per connection from the hostname the client sends in the TLS handshake. The default certificate is used only when a client sends no SNI or nothing matches, and when several match, selection prefers ECDSA over RSA, unexpired over expired, a higher SHA variant and the larger key. The alternative is one certificate carrying a wildcard or Subject Alternative Names, remembering that `*.example.com` covers one subdomain level and not the apex.

Mutual TLS makes the client prove its identity too, which is how a business-to-business API or a device fleet authenticates without application code. An Application Load Balancer offers two modes. In passthrough mode it forwards the entire client certificate chain to the target in `X-Amzn-Mtls` headers and verifies nothing. In verify mode it performs X.509v3 client certificate authentication itself against a trust store, a batch-uploaded bundle of certificate authority certificates from a third-party authority or from **AWS Private Certificate Authority**, the managed private certificate authority, with optional revocation list checking. The quotas to know are 20 trust stores per account, 25 certificate authority certificates per trust store, and two verify-mode listeners per load balancer. Session resumption is unavailable in either mode, and mutual TLS halves the active connections a capacity unit provides.

Inspection and the edge belong to neighboring units. **AWS WAF**, the web application firewall that filters HTTP requests on rules you choose, associates with an Application Load Balancer but not with a Network or Gateway Load Balancer, and the `waf.fail_open.enabled` attribute, false by default, decides whether requests pass when the load balancer cannot reach AWS WAF; rule groups are covered in [AWS WAF, Shield, Firewall Manager and Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md). Application, Network and Classic Load Balancers carry security groups; a Gateway Load Balancer does not. Putting **Amazon CloudFront**, the content delivery network, in front of an Application Load Balancer adds caching and edge termination, and **AWS Global Accelerator**, which advertises static anycast addresses from the AWS edge, fronts either current generation type; see [Amazon CloudFront](../04-networking/cloudfront.md) and [AWS Global Accelerator](../04-networking/global-accelerator.md).

## Gateway Load Balancer, GENEVE, and inline appliance inspection

A Gateway Load Balancer exists for one job: making a fleet of virtual appliances, such as firewalls, intrusion detection and prevention systems and deep packet inspection engines, scale and fail over like any other target group without changing any of the traffic's addresses. It operates at the network layer, listens for all IP packets on all ports, and exchanges traffic with its appliances using the GENEVE encapsulation protocol on port 6081. Encapsulation is what preserves the original packet: the appliance receives the client's real source and destination addresses inside the tunnel, inspects or modifies the packet, and returns it to the load balancer to forward onward. The flow is never terminated, which is also why there is no TLS termination and no security group.

Traffic reaches it through a Gateway Load Balancer endpoint, a VPC endpoint powered by AWS PrivateLink connecting the consumer VPC holding the application to the provider VPC holding the appliances. You do not point clients at the Gateway Load Balancer; you point route tables at the endpoint. A route entry naming the endpoint as next hop sends a subnet's traffic through inspection and back, which is why the endpoint and the application servers must sit in different subnets, and a gateway route table on the internet gateway does the same inbound.

Flow stickiness keeps a connection on one appliance, which stateful inspection requires. The default hash is a 5-tuple of protocol, source and destination address and source and destination port, with 3-tuple and 2-tuple options. If an appliance fails, existing flows continue to it while new flows are rerouted to healthy appliances, unlike the fail-open behavior of the other types. Cross-zone load balancing is off by default and, as with a Network Load Balancer, enabling it adds inter-Availability Zone data transfer charges.

## Monitoring, logs, and the pricing shape

Every load balancer publishes metrics to **Amazon CloudWatch**, the AWS monitoring service, at no extra charge. The ones that answer questions are `HealthyHostCount` and `UnHealthyHostCount` per target group, `TargetResponseTime`, the `HTTPCode_ELB_5XX_Count` and `HTTPCode_Target_5XX_Count` pair that separates a load balancer fault from an application fault, `ActiveFlowCount` on a Network Load Balancer, and `ConsumedLCUs`. A separate `PeakLCUs` metric reports the peak across all scaling dimensions rather than only the billed ones, and AWS recommends it when sizing a capacity reservation.

Three optional log types write to **Amazon S3**, the object storage service, and all three are off by default. Access logs record one entry per request, with client address, latencies, request path and response code. Connection logs, on an Application Load Balancer, record one entry per connection with client address and port, TLS protocol and cipher, handshake latency, connection status and client certificate details, which is what you enable when handshakes fail or when auditing mutual TLS clients. Health check logs capture the load balancer's own probes. Two limits matter here: Network Load Balancer access logs exist only when the load balancer has a TLS listener and cover TLS connections only, and AWS charges for the S3 storage but not the delivery bandwidth. Newer delivery paths send the same logs to CloudWatch Logs or to **Amazon Data Firehose**, the managed streaming delivery service, instead.

Pricing has two parts for every type: an hourly charge, with a partial hour billed as a full hour, plus a per-minute capacity charge. That capacity charge is the Load Balancer Capacity Unit, or LCU, a composite unit measured on several dimensions at once where you are billed only on the dimension with the highest usage. For an Application Load Balancer the four dimensions are new connections, active connections, processed bytes and rule evaluations, and one LCU covers 25 new connections per second, 3,000 active connections per minute, 1 GB per hour of processed bytes for instance, container and IP targets, and 1,000 rule evaluations per second. The variations surprise people: Lambda targets get only 0.4 GB per hour per LCU, mutual TLS halves active connections to 1,500, and the first 10 processed rules are free, with the rule dimension ignored entirely below 11 rules. A Network Load Balancer capacity unit (NLCU) has three dimensions whose contents vary by protocol, notably 800 new TCP connections per second against only 50 new TLS connections per second, which makes terminating TLS there a real cost decision. A Gateway Load Balancer capacity unit (GLCU) covers 600 new connections per second, 60,000 active connections per minute and 1 GB per hour. A Classic Load Balancer has no LCU and is billed per hour plus per GB processed.

A Load Balancer Capacity Unit Reservation is the other half of the term, and it is a capacity feature rather than a billing dimension. It holds a static minimum capacity so a load balancer starts a known-spiky event already scaled instead of waiting for automatic scaling, with a minimum of 100 LCUs, reserved LCU-hours billed whether used or not, and usage above the reservation billed as ordinary LCU-hours.

## Professional depth

At organization scale a load balancer stops being one tier's front door and becomes shared infrastructure. The common landing zone pattern puts the appliances and a Gateway Load Balancer in a central inspection VPC owned by a network account and shares its endpoints into workload VPCs, so every account's traffic is inspected without any team running a firewall. The ingress side has the same shape: a provider account fronts a service with a Network Load Balancer, publishes it as a PrivateLink endpoint service, and consumer accounts create interface endpoints against the service name, which works even when the two VPCs have overlapping address ranges. Subnets shared through **AWS Resource Access Manager (AWS RAM)**, the cross-account resource sharing service, let a load balancer live in a network account's subnets while its targets belong to workload accounts.

Quotas bind before architecture does. The defaults that bite are 1,000 targets and 100 listener rules per Application Load Balancer, 500 targets per Availability Zone and 3,000 per Network Load Balancer, the collapse of that per-zone allowance to 500 for the whole load balancer once cross-zone is enabled, the 50 or 100 targets each registered Application Load Balancer consumes, 1,200 Network Load Balancer network interfaces per VPC, and two verify-mode mutual TLS listeners per load balancer. Most are adjustable, but a migration registering a few thousand instances needs the increase approved before cutover, not during it.

Migration-scale designs lean on the `ip` target type. Registering on-premises servers by private address across Direct Connect lets one Application Load Balancer serve a hybrid fleet, so traffic shifts to AWS by changing target group weights in a forward action rather than by changing DNS, which gives a controllable blue/green or canary cutover. A partner firewall that allowlists addresses is the usual reason to put a Network Load Balancer in front of that Application Load Balancer instead of publishing a DNS name.

The failure modes at scale are economic or silent. Enabling cross-zone load balancing on a large Network Load Balancer adds an inter-Availability Zone transfer bill that no metric alarms on. A deregistration delay left at 300 seconds makes every scale-in take five minutes, capping how fast a fleet can shrink. And fail-open means a bad deployment that fails health checks everywhere produces application errors rather than a clean 503, so only a synthetic check outside the load balancer detects it.

## Worked scenario

A payments company runs a public API for merchants and a partner API for a small number of banks, both in one Region, under a rule that all traffic entering or leaving the production VPC must pass through a vendor firewall appliance.

The public API sits behind an Application Load Balancer in three Availability Zones, with an HTTPS listener holding an ACM certificate, rules routing `/v1/payments/*` and `/v1/refunds/*` to separate target groups, and AWS WAF associated for rate limiting and injection rules. Targets are registered by IP address because the services run as container tasks, deregistration delay is lowered to 60 seconds because requests are short and scale-in was too slow, and cross-zone load balancing stays on so uneven task placement does not create hot zones. The partner API needs a fixed address for bank firewalls and client certificate authentication, so it is a Network Load Balancer with an Elastic IP address per subnet forwarding to an Application Load Balancer target group, whose HTTPS listener runs mutual TLS in verify mode against a trust store holding each bank's certificate authority. Cross-zone stays off on the Network Load Balancer, for the inter-zone charge and because that fleet is evenly sized.

Inspection is a Gateway Load Balancer in an inspection VPC with the vendor appliances as targets, exchanging traffic over GENEVE on port 6081. Production route tables send `0.0.0.0/0` to a Gateway Load Balancer endpoint, and a gateway route table on the internet gateway sends inbound traffic the same way, so both directions are inspected while addresses stay intact. Access and connection logs land in Amazon S3, and CloudWatch alarms on `UnHealthyHostCount` and on `HTTPCode_Target_5XX_Count` against `HTTPCode_ELB_5XX_Count` separate application faults from load balancer faults. Before a large onboarding the team sets a Load Balancer Capacity Unit Reservation sized from `PeakLCUs`.

The exam asks this two ways. The Associate version asks how to give the partner API a static IP address while keeping path-based routing, and the keyed answer is a Network Load Balancer with Elastic IP addresses forwarding to an Application Load Balancer target group. The Professional version adds the inspection requirement and asks for the least operational overhead, and the keyed answer is a Gateway Load Balancer reached from route tables through its endpoints, not appliances placed as NAT-style routing targets.

## Exam lens

- "Route to different services based on URL path or hostname" maps to an Application Load Balancer with listener rules; a Network Load Balancer cannot see the request.
- "Static IP address", "the client firewall allowlists IP addresses", "UDP traffic" or "millions of flows at the lowest latency" maps to a Network Load Balancer; an Application Load Balancer publishes only a DNS name.
- "Third-party firewall or intrusion detection appliances inline, transparently" maps to a Gateway Load Balancer, GENEVE on port 6081, endpoints in route tables.
- "Static IP address and path-based routing together" maps to an Application Load Balancer registered as the target of a Network Load Balancer.
- "Expose the service privately to many consumer VPCs with overlapping CIDR blocks" maps to a PrivateLink endpoint service fronted by a Network Load Balancer.
- "Invoke a serverless function from the load balancer" maps to an Application Load Balancer with a `lambda` target group; a Network Load Balancer cannot.
- "Targets are on premises or in a peered VPC" maps to the `ip` target type.
- "Requests from one user must reach the same server" maps to sticky sessions: the duration-based `AWSALB` cookie when the application has none of its own, application-based when it does.
- "In-flight requests must finish before an instance is terminated" maps to deregistration delay, default 300 seconds; a lifecycle hook is the distractor, managing the instance rather than the connections.
- "Detect a failed target faster" maps to lowering the health check interval and the unhealthy threshold; the defaults take 60 seconds.
- "A newly launched target is slow until a cache warms" maps to slow start on the target group.
- "The load balancer must not decrypt the traffic" maps to a Network Load Balancer with a TCP listener; a TLS listener is the distractor that terminates.
- "Authenticate the client with a certificate" maps to mutual TLS on an Application Load Balancer, verify mode when the load balancer itself validates against a trust store.
- "Serve many domains from one HTTPS listener" maps to a certificate list with SNI; a wildcard certificate is the distractor when the domains are unrelated.
- "Even distribution across unevenly sized Availability Zones" maps to enabling cross-zone load balancing, which costs inter-zone data transfer on a Network or Gateway Load Balancer.
- "Filter malicious HTTP requests before they reach the targets" maps to AWS WAF on an Application Load Balancer; it cannot associate with a Network Load Balancer.

Several of these features exist because an application cannot be changed. Duration-based stickiness keeps a user on the instance holding their in-memory session when moving that session to a shared store is not an option. Mutual TLS in verify mode authenticates clients by certificate without the application parsing one. An `ip` target group reaches servers that still run in a data center, so a load balancer can front them during a migration. When a question says the application cannot be modified, these are the levers.

## Knowledge check

### 1. One endpoint for several microservices (Associate)

A company runs four microservices on Amazon EC2 instances. All of them must be reachable through a single HTTPS hostname, with requests to `/orders/*` going to one service, `/inventory/*` to another, and requests for a retired path returning a static 410 response without reaching any instance. The company wants the least operational overhead.

Which solution will meet these requirements?

- **A)** Deploy a Network Load Balancer with a TLS listener and one target group per service.
- **B)** Deploy an Application Load Balancer with an HTTPS listener, path-pattern rules forwarding to one target group per service, and a fixed-response rule for the retired path.
- **C)** Deploy a Classic Load Balancer with an HTTPS listener and register all instances with it.
- **D)** Deploy four Network Load Balancers and use Amazon Route 53 weighted records to select among them.

<details><summary>Answer</summary>

**Answer: B.** Only an Application Load Balancer can read the request path, and its listener rules support both a `forward` action per path pattern and a `fixed-response` action that returns a status code and body without contacting a target. A cannot inspect paths at all, because a Network Load Balancer routes at Layer 4 by flow hash. C has no listener rules or target groups, so it cannot route on path, and AWS labels it the previous generation. D needs four endpoints, cannot express path routing in DNS, and multiplies the operational work the stem asks to minimize.

*Where this is covered: Listeners, rules, target groups, and target types.*

</details>

### 2. A fixed address for a partner firewall (Associate)

A bank must connect to a company's API. The bank's firewall allowlists destination IP addresses and cannot be changed to allow a hostname. The API itself routes requests to different backend services based on the URL path, and that routing must be preserved.

Which solution will meet these requirements?

- **A)** Create an Application Load Balancer and allocate Elastic IP addresses for each of its subnets.
- **B)** Create an Application Load Balancer and give the bank the current IP addresses resolved from its DNS name.
- **C)** Create a Gateway Load Balancer in front of the Application Load Balancer and give the bank the endpoint addresses.
- **D)** Create a Network Load Balancer with an Elastic IP address in each subnet, and register the Application Load Balancer in a target group of type `alb`.

<details><summary>Answer</summary>

**Answer: D.** A Network Load Balancer takes a static IP address in each enabled subnet and accepts an Elastic IP address, and a target group of type `alb` lets it forward to an Application Load Balancer that keeps the path-based rules. A is not possible, because an Application Load Balancer does not support Elastic IP addresses. B fails because the addresses behind an Application Load Balancer's DNS name change as it scales, and the records carry a 60-second time to live. C misuses a Gateway Load Balancer, which exists to insert inspection appliances in a traffic path and is reached through route table entries, not by external clients.

*Where this is covered: The four load balancer types and how to choose one.*

</details>

### 3. A legacy application that keeps session state locally (Associate)

A company is moving a purchased application to Amazon EC2 behind an Application Load Balancer. The vendor stores shopping cart state in memory on whichever server handled the first request, and the source code cannot be modified. The application sets its own session cookie named `JSESSIONID`. Users are reporting emptied carts.

Which solution will meet these requirements?

- **A)** Enable application-based stickiness on the target group and configure `JSESSIONID` as the application cookie name.
- **B)** Enable duration-based stickiness on the target group with a one-second cookie duration.
- **C)** Change the target group routing algorithm to least outstanding requests.
- **D)** Replace the Application Load Balancer with a Network Load Balancer and enable `source_ip` stickiness.

<details><summary>Answer</summary>

**Answer: A.** Application-based stickiness makes the load balancer issue an `AWSALBAPP` companion cookie keyed to the session cookie the application already sets, so every request in a session returns to the same target without any application change. B would work mechanically but a one-second duration expires the binding almost immediately, which is the same broken behavior. C changes only which target is chosen for a new request and provides no affinity at all. D would give affinity but discards the Layer 7 features, and source IP stickiness sends every user behind a shared NAT device to the same target.

*Where this is covered: Health checks, deregistration delay, and sticky sessions.*

</details>

### 4. Hot targets in one zone and dropped requests on scale-in (Associate)

A TCP service runs behind a Network Load Balancer in three Availability Zones. Because of capacity constraints, one zone holds 3 instances while the other two hold 12 each, and the 3 instances are saturated while the others are lightly loaded. Separately, during scale-in users occasionally receive errors on connections that were already in progress on the instance being removed. The company accepts a small increase in data transfer cost.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable cross-zone load balancing on the Network Load Balancer.
- **B)** Set the target group deregistration delay long enough to cover the slowest in-flight request.
- **C)** Set the target group deregistration delay to 0 seconds.
- **D)** Enable `source_ip` stickiness on the target group.
- **E)** Add an Amazon Route 53 weighted record for each Availability Zone.

<details><summary>Answer</summary>

**Answer: A and B.** Cross-zone load balancing is off by default on a Network Load Balancer, so each node serves only its own zone and the 3 instances absorb a full third of the traffic; enabling it lets every node reach all 27 targets, at the cost of inter-Availability Zone data transfer, which the stem accepts. Deregistration delay holds a target in the `draining` state so in-flight work finishes before the instance is terminated, with a range of 0 to 3,600 seconds and a default of 300. C does the opposite and cuts connections immediately. D pins clients to targets, which worsens rather than fixes an uneven distribution. E cannot help, because clients resolve one load balancer DNS name whose records already cover every enabled zone, and weighting them would not change which targets a node may reach.

*Where this is covered: Availability Zones, cross-zone load balancing, and resilience.*

</details>

### 5. Encryption that the load balancer must not break (Associate)

A healthcare application requires that traffic remain encrypted all the way to the application servers and that the private key never be installed on any AWS-managed component. The clients are a fixed set of hospital systems whose firewalls allowlist destination IP addresses.

Which solution will meet these requirements?

- **A)** Use an Application Load Balancer with an HTTPS listener and an ACM certificate, and re-encrypt to the targets.
- **B)** Use an Application Load Balancer with mutual TLS in passthrough mode.
- **C)** Use a Network Load Balancer with a TCP listener on port 443 and register the application servers as targets.
- **D)** Use a Network Load Balancer with a TLS listener and an ACM certificate.

<details><summary>Answer</summary>

**Answer: C.** A TCP listener on a Network Load Balancer forwards encrypted bytes without decrypting them, so the targets terminate TLS and hold the only copy of the private key, and the Network Load Balancer supplies the static addresses the hospital firewalls need. A terminates TLS at the load balancer, which requires installing the certificate there, and re-encryption does not change that. B still terminates the server side of the TLS connection at the load balancer; passthrough refers only to the client certificate chain. D explicitly terminates TLS at the load balancer with a certificate deployed on it.

*Where this is covered: TLS termination, SNI, and mutual TLS.*

</details>

### 6. Central inspection for every workload account (Professional)

A company runs 60 workload accounts. Security requires that all traffic leaving any workload VPC for the internet be inspected by a licensed third-party firewall appliance, that the appliance see the original source and destination IP addresses, and that workload teams not operate any firewall themselves.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Deploy the appliances behind a Gateway Load Balancer in a central inspection VPC, and point workload subnet route tables at Gateway Load Balancer endpoints as the next hop for outbound traffic.
- **B)** Deploy a pair of appliance instances in each workload VPC and set them as the default route target, with source and destination checks disabled.
- **C)** Deploy the appliances behind an internal Network Load Balancer in a central inspection VPC and route workload traffic to the load balancer's addresses.
- **D)** Associate AWS WAF with an Application Load Balancer in each workload VPC.

<details><summary>Answer</summary>

**Answer: A.** A Gateway Load Balancer is the only load balancer that inserts appliances transparently: it never terminates the flow, encapsulates packets in GENEVE on port 6081 so the appliance sees the original addresses, and is reached from route tables through its endpoints, so a central team owns the fleet and workload accounts change only a route. B meets the inspection requirement but puts 60 appliance pairs and 60 licenses under workload teams, which is the overhead the stem rules out. C rewrites the destination address and terminates the flow, so the appliance does not see the original packet, and a Network Load Balancer cannot be a transparent bump in the wire. D inspects only inbound HTTP traffic to an Application Load Balancer and does nothing for outbound traffic.

*Where this is covered: Gateway Load Balancer, GENEVE, and inline appliance inspection.*

</details>

### 7. Publishing a service to acquired companies (Professional)

After three acquisitions, a platform team must expose one internal HTTP API to VPCs in six other accounts. Two of those VPCs use CIDR blocks that overlap the platform VPC. The consumers must not gain any other network reachability into the platform VPC, and the team does not want to renumber anything.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Put a Network Load Balancer in front of the API and create a VPC endpoint service so consumers create interface endpoints against the service name.
- **B)** Create VPC peering connections from the platform VPC to each consumer VPC.
- **C)** Attach every VPC to a transit gateway and add routes for the API subnet.
- **D)** Register the existing Application Load Balancer in a Network Load Balancer target group of type `alb` so the API keeps its path-based routing behind the endpoint service.
- **E)** Assign Elastic IP addresses to the Application Load Balancer and share them with the consumer accounts.

<details><summary>Answer</summary>

**Answer: A and D.** A VPC endpoint service built on a Network Load Balancer exposes exactly one service through AWS PrivateLink, works across accounts, and tolerates overlapping address ranges because each consumer addresses a local endpoint rather than the provider's range. Registering the Application Load Balancer as an `alb` target keeps the Layer 7 routing the API already uses behind that endpoint service. B cannot be created between VPCs with overlapping CIDR blocks. C has the same overlap problem and would grant broad network reachability rather than a single service. E is not possible, because an Application Load Balancer does not support Elastic IP addresses.

*Where this is covered: Professional depth.*

</details>

### 8. Authenticating partner clients by certificate (Professional)

A company exposes an API to 40 partner organizations. Each partner presents a client certificate issued by its own certificate authority. The company must reject any request whose certificate is expired or has been revoked, must not add authentication code to the application, and wants the application to know which organization sent each request.

Which solution will meet these requirements?

- **A)** Configure mutual TLS in passthrough mode on the Application Load Balancer and validate certificates in the application.
- **B)** Configure the Application Load Balancer HTTPS listener with `authenticate-oidc` and register each partner as an OpenID Connect provider.
- **C)** Configure mutual TLS in verify mode on the Application Load Balancer, with a trust store containing each partner's certificate authority bundle and the corresponding certificate revocation lists.
- **D)** Terminate TLS on a Network Load Balancer TLS listener and enable client certificate authentication on it.

<details><summary>Answer</summary>

**Answer: C.** Verify mode makes the Application Load Balancer perform X.509 client certificate authentication itself against a trust store of certificate authority bundles, with optional revocation list checking, and it passes the certificate details to the target in `X-Amzn-Mtls` headers so the application can identify the organization without validating anything. A does the opposite: passthrough forwards the whole chain and verifies nothing, so the application must implement validation, which the stem forbids. B authenticates human users through an identity provider, not machine clients presenting certificates, and would require 40 provider integrations. D is not possible, because mutual TLS is an Application Load Balancer feature and a Network Load Balancer TLS listener does not authenticate clients.

*Where this is covered: TLS termination, SNI, and mutual TLS.*

</details>

## Summary

An Elastic Load Balancing question is a short chain of decisions. Choose the type from what the routing decision must see: HTTP requests choose an Application Load Balancer, TCP and UDP flows with a static address choose a Network Load Balancer, transparent appliance inspection chooses a Gateway Load Balancer, and a Classic Load Balancer, still sold but labeled previous generation, means migrate. Choose the target type from where the targets are, remembering that `ip` reaches peered VPCs and on-premises servers, `lambda` exists only on an Application Load Balancer, and `alb` exists only on a Network Load Balancer. Set the health check interval and unhealthy threshold from how fast failure must be noticed, and know that a fully unhealthy target group fails open. Set deregistration delay from the longest request and slow start from the warm-up time. Decide stickiness from whether the application already has a session cookie. Decide cross-zone load balancing from whether even utilization is worth the inter-zone charge, which applies on a Network or Gateway Load Balancer but not an Application or Classic one. Then terminate TLS where the certificate belongs, and read the bill as an hourly charge plus the highest LCU dimension.

## Related units

- [Amazon EC2](ec2.md): the instances that make up an `instance` target group and the status checks behind them
- [Amazon EC2 Auto Scaling](ec2-auto-scaling.md): the elastic capacity behind the load balancer, and the scale-in that deregistration delay protects
- [Amazon VPC](../04-networking/vpc.md): subnets, security groups, route tables and PrivateLink endpoints the load balancer depends on
- [Amazon Route 53](../04-networking/route53.md): alias records, evaluate target health, and failover routing across Regions
- [Amazon CloudFront](../04-networking/cloudfront.md): caching and edge TLS termination in front of an Application Load Balancer
- [AWS Global Accelerator](../04-networking/global-accelerator.md): static anycast addresses and Region failover in front of either current generation load balancer
- [AWS Certificate Manager](../07-security/acm.md): issuing, validating and renewing the certificates bound to an HTTPS or TLS listener
- [AWS WAF, Shield, Firewall Manager and Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md): request filtering on an Application Load Balancer and the alternatives for other layers

## Sources

- [Application Load Balancer CloudWatch metrics](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html): the metric names this unit names
- [Network Load Balancer CloudWatch metrics](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-cloudwatch-metrics.html): the same for a Network Load Balancer

- [What is Elastic Load Balancing?](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html): the four load balancer types and the current generation statement
- [What is a Classic Load Balancer?](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/introduction.html): previous generation status and the two remaining Classic advantages
- [Migrate your Classic Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/migrate-classic-load-balancer.html): the migration wizard and the per-type benefits of moving
- [Elastic Load Balancing features](https://aws.amazon.com/elasticloadbalancing/features/): the product comparison table covering layer, target types, listeners, static IP, SNI, WebSockets and security groups
- [How Elastic Load Balancing works](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/how-elastic-load-balancing-works.html): cross-zone defaults per type, routing algorithms, the 60-second DNS time to live, zonal shift and GENEVE port 6081
- [Elastic Load Balancing FAQs](https://aws.amazon.com/elasticloadbalancing/faqs/): which types charge inter-Availability Zone data transfer when cross-zone load balancing is enabled
- [Elastic Load Balancing pricing](https://aws.amazon.com/elasticloadbalancing/pricing/): LCU, NLCU and GLCU dimensions and contents, Classic per-GB billing, and LCU reservation billing
- [Listeners for your Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html): protocols and ports, WebSockets, HTTP/2 and listener attributes
- [Listener rules for your Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-rules.html): priority order, the default rule and the one-routing-action constraint
- [Condition types for listener rules](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/rule-condition-types.html): host-header, http-header, http-request-method, path-pattern, query-string and source-ip
- [Action types for listener rules](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/rule-action-types.html): forward, redirect, fixed-response and the authentication actions
- [Target groups for your Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html): instance, ip and lambda target types, target group attributes and target group health thresholds
- [Target groups for your Network Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-target-groups.html): target group attributes, deregistration delay and stickiness on a Network Load Balancer
- [Use an Application Load Balancer as a target of a Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/application-load-balancer-target.html): same VPC and account, two Network Load Balancers maximum, and the 50-target cost
- [Use Lambda functions as targets of an Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html): the 1 MB request and response limits and the WebSocket exclusion
- [Health checks for Application Load Balancer target groups](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html): every health check setting and the fail-open behavior when all targets are unhealthy
- [Health checks for Network Load Balancer target groups](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/target-group-health-checks.html): TCP default protocol, per-protocol timeouts and fail-open on an empty target group
- [Edit target group attributes](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-target-group-attributes.html): deregistration delay, slow start, routing algorithms, and duration-based and application-based stickiness
- [Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html): the two-zone minimum, the /27 and eight-address subnet rule, idle timeout and the WAF fail-open attribute
- [Network Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/network-load-balancers.html): TCP, TLS and UDP idle timeout behavior
- [SSL certificates for your Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/https-listener-certificates.html): default certificate, certificate list, SNI selection order and wildcard scope
- [Mutual authentication with TLS in Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/mutual-authentication.html): passthrough compared with verify mode, trust stores and the X-Amzn-Mtls headers
- [What is a Gateway Load Balancer?](https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/introduction.html): GENEVE on port 6081, endpoints, flow stickiness tuples and the route table path
- [Access logs for your Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-access-logs.html): disabled by default, S3 delivery and the newer CloudWatch Logs path
- [Connection logs for your Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-connection-logs.html): the TLS handshake and client certificate fields
- [Access logs for your Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-access-logs.html): the TLS listener requirement and best-effort delivery
- [Capacity reservations for your Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/capacity-unit-reservation.html): the 100 LCU minimum and the PeakLCUs sizing metric
- [Quotas for your Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-limits.html): rules, target groups, targets, certificates and trust store limits
- [Quotas for your Network Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-limits.html): targets per Availability Zone, targets per load balancer and network interfaces per VPC
- [AWS WAF](https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html): the resource types AWS WAF can protect, including the Application Load Balancer
