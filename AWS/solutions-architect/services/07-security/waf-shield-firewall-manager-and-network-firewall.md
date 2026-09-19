# AWS WAF, AWS Shield, AWS Firewall Manager, AWS Network Firewall and Route 53 Resolver DNS Firewall

**Where it sits on the exams.** These services address floods, injection, bad bots and unapproved outbound connections. **AWS WAF** inspects HTTP and HTTPS requests, **AWS Shield** provides distributed denial of service (DDoS) protection, **AWS Network Firewall** is a managed stateful firewall for an **Amazon VPC**, the isolated virtual network your resources run in, **Route 53 Resolver DNS Firewall** filters DNS queries, and **AWS Firewall Manager** deploys and audits protections across an organization. They appear in SAA-C03 task 1.2 for external threats and in SAP-C02 tasks 2.3 and 3.2 for managed security and attack mitigation at scale. Rule of thumb: DNS queries go to DNS Firewall, VPC packets and flows to Network Firewall, HTTP requests to WAF, volumetric floods to Shield, and organization-wide enforcement to Firewall Manager.

## The five services on one page

Keep the services apart by asking what each reads. Find the scenario's traffic in the second and third columns, then confirm it with the last column. Route 53 Resolver DNS Firewall is most often confused with Network Firewall.

| Service | Layer it operates at | What it inspects | What it can block | Wording that selects it |
|---|---|---|---|---|
| AWS WAF | Layer 7, at the CloudFront edge for a global web ACL or in the Region for a regional one | HTTP and HTTPS requests: source IP, country, URI path, query string, headers, cookies and body | Individual requests, with an allow, block, count, CAPTCHA or challenge decision each | "SQL injection", "cross-site scripting", "OWASP Top 10", "rate limit a single client", "CAPTCHA" |
| AWS Shield Standard | Layers 3 and 4, at the AWS network perimeter | All traffic arriving at AWS resources, automatically | Common infrastructure-layer floods such as SYN floods and reflection attacks | "already protected", "no additional charge", "included automatically" |
| AWS Shield Advanced | Layers 3, 4 and 7, on resources you explicitly protect | Traffic to protected resources, plus AWS WAF request data and health check state | Larger, targeted DDoS attacks, including request floods mitigated by rules it manages in your web ACL | "DDoS response team", "cost protection", "proactive engagement" |
| AWS Firewall Manager | No traffic path: a management plane over an organization | The configuration and compliance of the other four, through AWS Config | Nothing directly; it creates, enforces and remediates the protections that block | "every account in the organization", "automatically to accounts added later", "audit every security group" |
| AWS Network Firewall | Layers 3 and 4 plus application-layer inspection inside a VPC | Packets and flows routed through its endpoints: 5-tuple, TCP flags, Suricata signatures, TLS SNI and HTTP Host header | Any VPC traffic on the inspected path: internet egress, ingress from an internet gateway, east-west between VPCs, hybrid links | "intrusion prevention", "deep packet inspection", "inspect traffic leaving the VPC", "filter by domain" |
| Route 53 Resolver DNS Firewall | The DNS layer, at the VPC Resolver | Outbound DNS queries from the VPC, and on-premises queries arriving through Resolver endpoints | Resolution of a name, by returning NODATA, NXDOMAIN or a CNAME override | "prevent DNS exfiltration", "block lookups of malware domains", "only approved domains may resolve" |

Network Firewall does not see queries made through the Route 53 Resolver, so DNS exfiltration selects DNS Firewall. Conversely, DNS Firewall cannot stop a connection to a hard-coded IP address. Network Firewall controls whether a connection proceeds, reading TLS SNI and the HTTP Host header. For approved domains, use DNS Firewall for lookups and Network Firewall for traffic leaving.

## AWS WAF: web ACLs, rules and rule groups

A **web access control list (web ACL)** contains rules, sets a default allow or block action, and attaches to protected resources, which act on its verdict. The newest console calls it a protection pack. A regional web ACL protects an **Application Load Balancer**, the HTTP-aware layer 7 load balancer, an **Amazon API Gateway** REST API, the managed API front door, an **AWS AppSync** GraphQL API, an **Amazon Cognito** user pool, the managed user directory, an **AWS App Runner** container service, an **AWS Verified Access** instance, which fronts private applications, an **AWS Amplify** web application or an **Amazon Bedrock AgentCore Gateway** in the same Region. A global web ACL protects an **Amazon CloudFront** distribution, the content delivery network, and has a hard-coded Region of US East (N. Virginia). A **Network Load Balancer** cannot have a web ACL because it has no HTTP view, nor can an **Amazon EC2** instance, the virtual server service, directly. Put an Application Load Balancer or CloudFront in front instead. API Gateway support is for REST APIs only. Each resource can have one web ACL; one web ACL can protect many resources, but a CloudFront web ACL cannot protect anything else.

Inside a web ACL, a **rule** pairs a statement defining the inspection criteria with an action. Statements match an IP set of up to 10,000 addresses or ranges, a country, a string or regular expression in a named request component, the size of a component, a label added by an earlier rule, or the presence of SQL code or of a script that is likely to be malicious, and `AND`, `OR` and `NOT` combine them. A rule has no Amazon Resource Name and exists only inside the web ACL or rule group that defines it. The actions are allow, block, count, and CAPTCHA or challenge. Allow and block are terminating, refusing by default with HTTP 403; count is non-terminating, which makes it the way to test a new rule against production traffic before arming it.

A **rule group** is a reusable set of rules that a web ACL references. Rule groups cannot nest, have no default action, and are never attached to a resource directly. **AWS Managed Rules** are rule groups AWS writes, versions and updates for you. The baseline groups are `AWSManagedRulesCommonRuleSet`, the core rule set covering much of the OWASP Top 10 at 700 capacity units, `AWSManagedRulesAdminProtectionRuleSet` at 100 and `AWSManagedRulesKnownBadInputsRuleSet` at 200. Use-case groups target a stack: `AWSManagedRulesSQLiRuleSet` at 200 for databases, plus Linux, POSIX, Windows, PHP and WordPress groups; two IP reputation groups cover known bad sources at 25 and anonymizing proxies at 50. Those are free beyond the basic AWS WAF charges; only the intelligent threat groups cost extra, meaning Bot Control, the two Fraud Control groups and the anti-DDoS group. You cannot read the rules inside a managed group, so tuning means overriding a named rule to count rather than editing it.

The **web ACL capacity unit (WCU)** is how AWS WAF budgets processing, at a base cost per rule type that rises with complexity. A rule group's capacity is fixed at creation, and using it always costs that number however many rules are inside. The ceiling is 5,000 WCUs per web ACL and per rule group, but the number that decides cost questions is the 1,500 included in the basic web ACL price, beyond which a tiered surcharge applies.

## Rate-based rules, Bot Control, CAPTCHA and logging

A **rate-based rule** counts requests and applies its action once an aggregation instance exceeds a limit. Its settings are an evaluation window of 60, 120, 300 or 600 seconds with 300 as the default, a rate limit of at least 10 requests in that window, an aggregation key, an action that can be anything except allow, and an optional scope-down statement narrowing which requests the rule tracks. The window is how far back AWS WAF looks each time it checks, not how often it checks. The aggregation key is the part candidates miss. The default is the source IP address, but you can aggregate on a forwarded IP address from a header such as `X-Forwarded-For`, on the autonomous system number derived from the address, on `Count all` with a required scope-down statement, or on custom keys: a header, a cookie, a query argument, the query string, the URI path, the HTTP method, a label namespace, and JA3 or JA4 TLS fingerprints, several of which can be combined. That is what lets one rule enforce a per-tenant limit rather than a per-address limit, the distinction a scenario about one noisy customer behind a shared NAT gateway is testing. Against an HTTP request flood the choice between this and Shield Advanced turns on whether the flood has a shape you can name: a rate-based rule is the answer when a key such as an address, a tenant or a path identifies the abuse, and Shield Advanced with `AWSManagedRulesAntiDDoSRuleSet` is the answer when the flood is distributed widely enough that no single key isolates it and the requirement mentions automatic response or a baseline of normal traffic.

**AWS WAF Bot Control** is a managed rule group, `AWSManagedRulesBotControlRuleSet`, at 50 WCUs, with two protection levels. The common level detects bots that identify themselves, such as scrapers, scanners and search engines, using static request analysis, then labels them and blocks the ones it cannot verify. The targeted level includes common and adds detection for sophisticated bots that do not self-identify, using browser interrogation, fingerprinting, behavior heuristics and optional machine learning; its rules carry a `TGT_` prefix and the machine learning ones `TGT_ML_`, and it brings its own rate limiting. Pricing is ten US dollars per month per web ACL plus a per-million-requests inspection fee, with the first 10 million requests a month free at common and the first 1 million at targeted. Bot Control labels carry the bot category and name, and your own rules match those labels, which is how you allow a verified search engine crawler while challenging the rest.

The **CAPTCHA** and **Challenge** actions are the middle ground between allow and block. CAPTCHA presents a puzzle in a JavaScript interstitial that a human solves; Challenge runs a silent browser verification with no user involvement. Both issue a token and both are conditional: a valid, unexpired token within the configured immunity time makes the action behave like count, and only a missing, invalid or expired token serves the interstitial. Both require HTTPS and a browser in a secure context, and both carry extra charges. The exam signal is a stem saying blocking would turn away too many real customers.

Logging has exactly three destinations, and naming them is a frequent question: an **Amazon CloudWatch Logs** log group, an **Amazon S3** bucket in the object storage service, or an **Amazon Data Firehose**, formerly Kinesis Data Firehose, delivery stream. Named fields can be redacted, and request sampling shows a live sample of evaluated requests with no logging enabled at all.

## AWS Shield Standard compared with Shield Advanced

**AWS Shield Standard** is on for every AWS customer automatically, at no extra charge, and cannot be turned off or configured. It defends against the most common network and transport layer attacks, and AWS states that hosted zones in **Amazon Route 53**, the managed DNS service, along with CloudFront distributions and **AWS Global Accelerator** standard accelerators, receive comprehensive availability protection against all known layer 3 and layer 4 attacks. That is the architectural point: putting CloudFront or Global Accelerator in front of an origin moves the perimeter from your VPC to the AWS edge and improves DDoS resilience before any paid service is involved.

**AWS Shield Advanced** is a paid subscription that you must then apply to individual resources; subscribing an account protects nothing on its own. The eligible types are CloudFront distributions, Route 53 hosted zones, Global Accelerator standard accelerators, EC2 Elastic IP addresses, Application Load Balancers and Classic Load Balancers, with Network Load Balancers and EC2 instances covered through an associated Elastic IP address. That is the mirror image of the AWS WAF list: Shield Advanced reaches a Network Load Balancer through an Elastic IP address, while AWS WAF cannot reach one at all.

What the subscription adds falls into four groups. First, mitigation: automatic application layer DDoS mitigation, where Shield Advanced maintains a rule group inside your web ACL, rate limits known DDoS sources, compares live traffic against a baseline it needs between 24 hours and 30 days to learn, and deploys custom rules in count or block mode as attacks appear. That rule group consumes 150 WCUs. The anti-DDoS managed rule group, `AWSManagedRulesAntiDDoSRuleSet`, became the default for HTTP request flood protection on 26 March 2026 and supersedes that older layer 7 auto mitigation feature, which existing customers may keep; both exams still describe automatic application layer mitigation. Second, visibility: real-time attack metrics, health-based detection that uses a health check to cut false positives, and protection groups that treat a set of resources as one detection unit. Third, people: the **Shield Response Team (SRT)**, which older material and both exam guides still call the DDoS Response Team, is reachable during an attack and can build custom mitigations, but only if you are also on the Business or Enterprise Support plan. Proactive engagement goes further and has the SRT contact you first when a protected resource's health check goes unhealthy during a detected event; it needs the same support plan, a health check on the resource, and at least one of up to ten registered contacts. Fourth, money: cost protection issues service credits for attack-driven spikes in data transfer out, CloudFront requests, Route 53 queries, load balancer capacity units, and EC2 instances that scaling policies launched during the attack.

Cost protection is the most conditional benefit on either exam, and every condition must have been in place before the attack: the resource already protected, a CloudFront or Application Load Balancer resource already carrying a web ACL with a rate-based rule in block mode, and the AWS DDoS resiliency best practices already followed. The claim is a billing case with "DDoS Concession" in the subject, filed within 15 days of the end of the billing month.

Shield Advanced is 3,000 US dollars a month billed against the payer account, covering every subscribed account in the consolidated billing family, plus per-GB data transfer out fees on protected resources; the benefits are subject to a one-year subscription commitment, and the subscription auto-renews annually. It also absorbs standard AWS WAF charges on protected resources, meaning the web ACL fee, the per-rule fee and the base request fee, up to 1,500 WCUs and up to the default body size, but not Bot Control, Fraud Control, CAPTCHA, capacity above 1,500 WCUs or inspection of a request body beyond that default size. Separately, the subscription includes up to 50 billion requests a month against the Layer 7 Anti-DDoS managed rule group.

## AWS Firewall Manager across an organization

AWS Firewall Manager exists because per-account configuration does not scale and does not survive new accounts. It applies protections once and keeps them applied across every account and resource in scope, including those that appear later. It inspects no traffic; every block credited to it is performed by one of the other services.

The prerequisites are graded material. Your organization in **AWS Organizations** must be enabled for all features, not consolidated billing only. The management account onboards the organization and creates a Firewall Manager default administrator, which Firewall Manager registers as a delegated administrator in Organizations so day-to-day policy work leaves the management account; up to ten administrators are allowed, each optionally restricted to specific accounts, Regions, or policy types. **AWS Config** must be enabled in every member account and protected Region with recording set to continuous, because Config is how Firewall Manager sees resource state and detects drift, and **AWS Resource Access Manager (AWS RAM)**, the service that shares resources between accounts, must be enabled for Network Firewall and DNS Firewall policies. It charges a monthly fee per policy per Region, roughly 100 US dollars, on top of the underlying service and Config charges; Shield Advanced policies are free for subscribers.

Seven policy types matter. An AWS WAF policy pushes a set of rule groups to run first in the web ACL and a set to run last, leaving the middle open so the account owner can add rules without bypassing the mandated ones. A Shield Advanced policy applies protections to named resource types and can subscribe every member account, including those that join later. A security group policy comes in three flavors: common, which replicates baseline groups into every account; content audit, which checks existing groups against allowed rules and can remediate them; and usage audit, which finds unused and redundant groups. A network ACL policy enforces first and last rules on subnets. A Network Firewall policy stands up a firewall in each in-scope VPC, and a DNS Firewall policy attaches rule groups to every in-scope VPC. Third-party policies deploy Palo Alto Networks Cloud NGFW or Fortigate CNF. Scope is set by organizational unit, account list, or resource tag, and every policy runs either in audit-only mode or in automatic remediation mode.

What Firewall Manager does that per-account configuration cannot is the answer to a family of Professional questions: protect all resources of a type rather than a list you maintain; protect resources created after the policy was written; guarantee a mandated rule group runs first and cannot be reordered away; subscribe a whole organization to Shield Advanced including future members; and produce one compliance view, exportable to **AWS Security Hub CSPM**, the security finding aggregator.

## AWS Network Firewall and Route 53 Resolver DNS Firewall

AWS Network Firewall is built on **Suricata**, the open source intrusion prevention engine, and accepts Suricata-compatible rules directly. A firewall names a VPC and one subnet per Availability Zone for its endpoints, a policy holds the settings, and rule groups hold the rules. A **stateless rule group** evaluates one packet in isolation on 5-tuple criteria plus optional TCP flag masks, with a unique numeric priority per rule and actions of pass, drop, or forward to stateful rules; packets reach the stateful engine only if forwarded. A **stateful rule group** tracks flows in the state table and comes in three forms: standard rules built from a form, domain list rules, and raw Suricata rule strings. Stateful actions are pass, drop, alert and reject, where reject returns a TCP reset for TCP only. Managed rule groups each count as one group against the 20 stateful rule groups a policy allows.

Stateful evaluation order is a policy-level choice made once: `RuleOrder` cannot be edited after the firewall policy or rule group is created. Under the default action order, Suricata evaluates all pass rules first, then drop, then reject, then alert, and the `priority` keyword only orders rules within one action group. Under strict order, rule groups run in the priority order you assign and rules in the order written, which AWS recommends because it is the only mode where the policy reads the way it executes.

Domain list filtering is the feature most often confused with DNS Firewall. A domain list rule group takes explicit names or a leading-dot wildcard such as `.example.com` that also matches every subdomain, inspects HTTP, HTTPS or both, and acts with allow, deny, reject or alert; allow makes it a strict allowlist and denies everything else on that protocol. Network Firewall reads the TLS Server Name Indication for HTTPS and the HTTP `Host` header for plain HTTP, never pausing for an out-of-band DNS lookup, so a manipulated header needs separate address-based rules. By default the `HOME_NET` variable is the CIDR range of the VPC hosting the firewall, so a centralized inspection VPC receiving traffic over a transit gateway silently inspects nothing until `HOME_NET` is set manually to cover the spoke ranges.

Deployment is done with route tables, and this is where the exam probes. A firewall endpoint is a VPC endpoint that can be a route table target, so it appears in a route as a `vpce-` identifier. In the simplest internet gateway design, the workload subnet's default route points at the firewall endpoint, the firewall subnet's default route points at the internet gateway, and an ingress route table on the internet gateway routes each workload subnet's CIDR back to the firewall endpoint so return traffic is symmetric. Without it, replies bypass inspection and stateful rules break. A firewall endpoint cannot inspect traffic entering or leaving its own subnet, so firewall subnets hold nothing else, and one endpoint per Availability Zone is the pattern because crossing zones adds charges. AWS documents three deployment models: distributed, with a firewall in each VPC; centralized, with an inspection VPC behind **AWS Transit Gateway**, the Regional hub that interconnects VPCs and on-premises networks; and combined, where a central inspection VPC handles east-west and on-premises traffic while VPCs needing local internet ingress keep their own firewall. VPC peering traffic, Global Accelerator traffic and Amazon-provided DNS queries cannot be inspected. Stateful logging goes to S3, CloudWatch Logs or Data Firehose, and pricing is per endpoint hour plus per GB processed.

Route 53 Resolver DNS Firewall works on a different plane. You build rule groups holding ordered rules, each with a unique numeric priority, and associate them with VPCs, again with a priority per association; DNS Firewall evaluates rule groups from the lowest priority upward and rules within a group the same way, stopping at the first match. A foundational rule names one domain list and an action of ALLOW, ALERT or BLOCK, and a blocked query returns NODATA, NXDOMAIN or an OVERRIDE with a custom CNAME. A rule can restrict itself to one query type, so you can block A records while letting MX queries through. AWS publishes four managed domain lists, free and continuously updated: malware, botnet command and control, an aggregate list that includes the others, and one drawn from **Amazon GuardDuty**, the managed threat detection service. DNS Firewall Advanced rules replace the domain list with a threat signature detector for domain generation algorithms, DNS tunneling and dictionary DGAs at a chosen confidence threshold, and can only block or alert, never allow. One VPC-level setting is easy to get wrong: the failure mode is closed by default, so if DNS Firewall does not answer, the Resolver blocks the query and returns `SERVFAIL`. Rule groups are Regional and can be shared with AWS RAM or pushed by a Firewall Manager policy.

## Professional depth

At organization scale the first decision is where the mandated rules live. A Firewall Manager AWS WAF policy pushes a first and a last set of rule groups into every in-scope web ACL and leaves the middle to the application team, the only arrangement that guarantees a baseline and still permits tuning. The corollary is capacity: mandated groups consume WCUs from the 5,000 ceiling and from the 1,500 included in the base price, so mandating the core rule set, known bad inputs, the SQL database group and both IP reputation lists spends 1,175 WCUs before any application rule exists. Firewall Manager's own quotas bite too: 50 policies per organization per Region, 20 organizational units per policy, and 2,500 accounts in scope unless you explicitly include or exclude individual accounts, which drops the ceiling to 200.

Shield Advanced across an organization is a subscription question before a protection question. The 3,000 US dollars a month is billed to the payer account and covers every subscribed account in that consolidated billing family, so each account owning a protected resource still subscribes, so the marginal cost of protecting the hundredth account is zero, and a Shield Advanced policy subscribes member accounts and applies protections automatically at no extra policy charge. The mistake to look for is protecting the load balancer but not the CloudFront distribution in front of it: when the load balancer receives all of its traffic from CloudFront, protecting CloudFront is what matters.

> **Professional depth.** Where AWS WAF is evaluated changes the blast radius. A global web ACL runs at the CloudFront edge before the request reaches the origin, so a blocked request never consumes origin capacity or Regional data transfer, while a regional web ACL on a load balancer runs after the request has crossed into your Region. The ordering AWS recommends at scale is CloudFront with a global web ACL at the front, Shield Advanced on the distribution, and the origin reachable only from CloudFront.

Inspection designs fail in characteristic ways. Asymmetric routing breaks stateful inspection, which is why the internet gateway ingress route matters, and a NAT gateway or load balancer ahead of the firewall loses the workload's source address. Network Firewall cannot inspect VPC peering traffic, so inspection between two VPCs means routing them through a transit gateway. Quotas to carry: 5 firewalls and 50 stateful rule groups per account per Region by default, 20 stateful and 20 stateless rule groups per firewall policy as hard limits, and 30,000 stateful rules per policy. On the DNS side, because the default failure mode is closed, an organization-wide rollout is also an availability decision.

## Worked scenario

A retail company runs a storefront on CloudFront in front of an Application Load Balancer, a partner API on an API Gateway REST API, and batch processors in private subnets that must reach a short list of supplier endpoints and nothing else. It has 90 accounts in an organization with all features enabled, and has been hit twice in a quarter by a volumetric flood combined with slow credential stuffing against the login page. Compliance requires evidence that every internet-facing resource carries the same baseline, including in accounts opened later.

The storefront gets a global web ACL with the core rule set, known bad inputs and the Amazon IP reputation list, a rate-based rule on the login path aggregated on a forwarded IP address with a challenge action rather than a block, so customers behind a corporate proxy are not turned away, and Bot Control at the targeted level for credential stuffing that does not self-identify. The partner API gets a regional web ACL with a rate-based rule aggregated on the partner's API key header. Shield Advanced is subscribed in each account owning a protected resource, one price for the payer family, and applied to the distribution, the load balancer and the hosted zone, with a health check on the distribution and Business Support so the SRT and proactive engagement are usable; the storefront's rate-based rule in block mode is what makes the resource eligible for cost protection.

Firewall Manager runs from a delegated administrator in the security account with AWS Config recording continuously in all 90 accounts. One AWS WAF policy pushes the mandated rule groups as the first set into every in-scope web ACL, one Shield Advanced policy subscribes and protects new accounts automatically, one DNS Firewall policy attaches the aggregate threat list plus a company allowlist to every VPC, and one Network Firewall policy serves the batch processors. Those get a stateful domain list rule group in allow mode naming the supplier domains over HTTPS, chosen over DNS Firewall because the requirement is that traffic not leave rather than that names not resolve, `HOME_NET` set explicitly because the firewalls sit in a central inspection VPC behind a transit gateway, and routes sending each workload subnet to the `vpce-` endpoint with a matching ingress route on the internet gateway.

The exam asks which service stops the credential stuffing and which stops the flood. The keyed answer is AWS WAF with Bot Control and a rate-based rule for the application layer, Shield Advanced for the volumetric attack and the cost exposure, and Firewall Manager for the organization-wide guarantee.

## Exam lens

- "SQL injection" or "OWASP Top 10" maps to a web ACL with the core rule set and the SQL database rule group; a network ACL is the distractor, because it has no view of request content.
- "Protect a Network Load Balancer with a web application firewall" maps to putting CloudFront or an Application Load Balancer in front; AWS WAF cannot associate with an NLB at all.
- "Limit each tenant or each API key" maps to a rate-based rule with a custom aggregation key on a header; source IP aggregation is the distractor when users share a NAT address.
- "Bots that do not identify themselves" maps to Bot Control at the targeted level; the common level is the distractor, because it only handles self-identifying bots.
- "Blocking would reject too many real users" maps to the CAPTCHA or Challenge action, not to block.
- "No extra charge, already in place" maps to Shield Standard, and "access to DDoS experts during an attack" to Shield Advanced plus Business or Enterprise Support.
- "Credit for the bill spike caused by the attack" maps to Shield Advanced cost protection; adding protection during or after the attack is the distractor.
- "AWS should contact us before we notice" maps to proactive engagement, which needs a Route 53 health check and Business or Enterprise Support.
- "Every account, including accounts added later" maps to Firewall Manager with a delegated administrator, Organizations with all features, and AWS Config recording continuously.
- "Intrusion prevention" or "allow only these domains over HTTPS from the VPC" maps to Network Firewall stateful rule groups, which read Suricata signatures and the TLS SNI; a security group is the distractor, because it is allow-only and has no signatures.
- "Prevent data exfiltration through DNS lookups" maps to Route 53 Resolver DNS Firewall; Network Firewall is the distractor, because it never sees Resolver queries.
- "Traffic must pass through the firewall" maps to routes pointing at the `vpce-` firewall endpoint plus an internet gateway ingress route back to it.

## Knowledge check

### 1. Injection attacks against a public storefront (Associate)

A retailer runs a storefront on Amazon EC2 instances behind an Application Load Balancer. A penetration test reports that the application is vulnerable to SQL injection and cross-site scripting, and the development team cannot ship code fixes for several weeks. The security team needs to stop the attacks reaching the application in the meantime with as little ongoing maintenance as possible.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Add inbound deny rules to the network ACL on the application subnets for the source addresses seen in the penetration test.
- **B)** Subscribe to AWS Shield Advanced and enable automatic application layer DDoS mitigation on the Application Load Balancer.
- **C)** Create an AWS WAF web ACL with the AWS Managed Rules core rule set and SQL database rule group, and associate it with the Application Load Balancer.
- **D)** Deploy AWS Network Firewall in the VPC with a stateful rule group that drops requests containing SQL keywords.

<details><summary>Answer</summary>

**Answer: C.** A web ACL with AWS Managed Rules inspects HTTP request content for injection and scripting patterns, attaches directly to an Application Load Balancer, and is updated by AWS as new signatures appear, which is the least ongoing work. A blocks addresses rather than payloads, and attackers change addresses; network ACLs cannot read request content at all. B addresses denial of service, not injection, and its automatic mitigation writes rate and reputation rules rather than injection signatures. D is the wrong layer and the wrong tool: Network Firewall inspects VPC traffic paths and would require you to write and maintain Suricata signatures for a job AWS already manages, and it does not attach to a load balancer.

*Where this is covered: AWS WAF: web ACLs, rules and rule groups.*

</details>

### 2. Rate limiting a single noisy tenant (Associate)

A software company exposes a multi-tenant API through an Amazon API Gateway REST API. Each tenant sends a unique value in a custom `X-Tenant-Id` header. One tenant's misbehaving client recently generated enough traffic to degrade the API for everyone. All tenants reach the API through a small number of shared corporate NAT addresses. The company wants to cap requests per tenant without capping legitimate tenants that share an address.

Which solution will meet these requirements?

- **A)** Create an AWS WAF rate-based rule that aggregates on the source IP address and associate the web ACL with the REST API.
- **B)** Enable AWS Shield Advanced on the REST API and rely on automatic application layer DDoS mitigation.
- **C)** Create an AWS WAF IP set rule that blocks the corporate NAT addresses used by the offending tenant.
- **D)** Create an AWS WAF rate-based rule that uses a custom aggregation key on the `X-Tenant-Id` header and associate the web ACL with the REST API.

<details><summary>Answer</summary>

**Answer: D.** A rate-based rule can aggregate on custom keys including a named header, so each distinct tenant identifier becomes its own aggregation instance with its own limit. A aggregates on the address, which is exactly what the stem rules out: tenants share NAT addresses, so one tenant's traffic would rate limit the others. B does not apply, because API Gateway is not a Shield Advanced protected resource type, and automatic mitigation targets DDoS patterns rather than per-tenant quotas. C blocks addresses that legitimate tenants also use, breaking the same requirement.

*Where this is covered: Rate-based rules, Bot Control, CAPTCHA and logging.*

</details>

### 3. Stopping data leaving through name lookups (Associate)

A healthcare company runs processing instances in private subnets that reach the internet through a NAT gateway. An incident review found that a compromised instance had encoded patient identifiers into subdomain labels and sent them out as lookups against a domain the attacker controlled. The company wants to stop that specific technique and to block queries for domains AWS already knows to be malicious.

Which solution will meet these requirements?

- **A)** Attach a Route 53 Resolver DNS Firewall rule group to the VPCs with the AWS managed aggregate threat list and an allowlist rule for approved domains.
- **B)** Deploy AWS Network Firewall with a stateful domain list rule group in deny mode for the attacker's domain.
- **C)** Enable VPC Flow Logs on the private subnets and create a CloudWatch Logs metric filter for unusual query volumes.
- **D)** Replace the NAT gateway with a proxy fleet that terminates TLS and inspects the Host header of every outbound connection.

<details><summary>Answer</summary>

**Answer: A.** DNS Firewall filters queries passing through the Route 53 Resolver, which is the exact path DNS exfiltration uses, and AWS managed domain lists cover malware and botnet command-and-control names at no extra charge. B is the standard distractor: Network Firewall does not see Resolver queries, so a domain list rule group there would never match the lookup. C detects after the fact and flow logs do not record queries to the Amazon-provided DNS server. D inspects TLS connections but the exfiltration happens in the DNS lookup itself, before any connection, and building a proxy fleet is a custom solution for something AWS manages.

*Where this is covered: AWS Network Firewall and Route 53 Resolver DNS Firewall.*

</details>

### 4. Choosing what Shield Advanced actually buys (Associate)

A media company streams live events from Amazon CloudFront with an Application Load Balancer origin. Management wants assurance that during a large DDoS attack the company can reach AWS DDoS specialists within minutes, that AWS will contact the company before its own operations team notices, and that the company will not pay for the scaling caused by the attack. The company is currently on the Developer Support plan.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Subscribe to AWS Shield Advanced, add protection to the CloudFront distribution, associate an Amazon Route 53 health check with it, and enable proactive engagement.
- **B)** Upgrade to the Business Support plan or the Enterprise Support plan.
- **C)** Rely on AWS Shield Standard, which already includes response team engagement for CloudFront distributions.
- **D)** Create an AWS WAF web ACL with the anonymous IP list rule group and enable AWS WAF logging to Amazon S3.
- **E)** Open a billing case in advance so that any attack-related charges are automatically credited.

<details><summary>Answer</summary>

**Answer: A and B.** Shield Advanced with a protected resource, an associated Route 53 health check and proactive engagement enabled is what allows the Shield Response Team to contact the customer first, and Shield Advanced is what makes cost protection credits available for attack-driven scaling. Both SRT access and proactive engagement additionally require the Business or Enterprise Support plan, which the Developer plan does not satisfy. C is wrong because Shield Standard includes no response team access. D improves request filtering and visibility but grants no expert access and no cost protection. E is not how cost protection works: the claim is filed after the attack, within 15 days of the end of the billing month, and only for resources protected beforehand.

*Where this is covered: AWS Shield Standard compared with Shield Advanced.*

</details>

### 5. Bots that do not announce themselves (Associate)

An online ticketing site finds that automated clients are buying inventory within seconds of release. The clients rotate addresses, present ordinary browser user agents and do not identify themselves as bots. Blocking outright has already turned away real customers during previous attempts. The site is served through CloudFront and uses HTTPS everywhere.

Which solution will meet these requirements?

- **A)** Add the AWS WAF Bot Control managed rule group at the targeted protection level and use the Challenge action on requests it labels as unverified bots.
- **B)** Add the AWS WAF Bot Control managed rule group at the common protection level and set all of its rules to block.
- **C)** Add the AWS WAF anonymous IP list managed rule group and block every match.
- **D)** Enable CloudFront geo restriction for the countries the automated traffic originates from.

<details><summary>Answer</summary>

**Answer: A.** The targeted protection level exists specifically for sophisticated bots that do not self-identify, using browser interrogation, fingerprinting and behavior heuristics, and the Challenge action verifies a real browser silently so genuine customers are not asked to solve anything. B only detects self-identifying bots, which the stem rules out, and blocking everything it matches repeats the mistake the company already made. C blocks proxies and anonymizing services, which is a different population from browser-imitating bots and would catch legitimate users on VPNs. D applies to whole countries and to the whole distribution, and the stem gives no country signal.

*Where this is covered: Rate-based rules, Bot Control, CAPTCHA and logging.*

</details>

### 6. One baseline across ninety accounts (Professional)

A financial services group has 90 accounts in AWS Organizations with all features enabled. Security requires that every internet-facing Application Load Balancer and CloudFront distribution carry the same three AWS Managed Rules rule groups, that application teams may still add their own rules, that the mandated rules cannot be removed or reordered by those teams, and that any account created next quarter is covered automatically with no manual step.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Publish a CloudFormation StackSet that creates a web ACL in every account, and run a weekly script that reports accounts whose web ACL has drifted.
- **B)** Attach a service control policy that denies `wafv2:DeleteWebACL` and `wafv2:UpdateWebACL` in every member account.
- **C)** Onboard the organization to AWS Firewall Manager from a delegated administrator account, enable AWS Config with continuous recording in every account and Region, and create an AWS WAF policy whose first rule group set contains the three mandated rule groups.
- **D)** Subscribe every account to AWS Shield Advanced and use a Shield Advanced policy to apply the three rule groups to all protected resources.

<details><summary>Answer</summary>

**Answer: C.** A Firewall Manager AWS WAF policy applies a first and a last set of rule groups to every in-scope web ACL, leaves the middle open for application teams, and automatically covers accounts and resources that come into scope later; it requires Organizations with all features, a delegated administrator and AWS Config recording continuously, all of which the stem allows. A creates the web ACLs but does not stop a team from editing them, and a weekly script is manual drift detection rather than enforcement. B blocks the API calls teams need in order to add their own rules, breaking a stated requirement, and an SCP cannot guarantee rule ordering. D subscribes to a DDoS service at 3,000 US dollars a month for a requirement that is about managed rule groups, and a Shield Advanced policy does not push AWS WAF rule groups as its first set.

*Where this is covered: AWS Firewall Manager across an organization.*

</details>

### 7. Centralized inspection that inspects nothing (Professional)

A company routes all egress traffic from 30 spoke VPCs through AWS Transit Gateway into a central inspection VPC running AWS Network Firewall, with firewall endpoints in three Availability Zones. A stateful domain list rule group in allow mode names the approved supplier domains over HTTPS. After cutover, traffic from the spokes reaches the suppliers as expected, but traffic to unapproved domains is also passing, and the alert logs are empty for spoke traffic while showing matches for test traffic generated inside the inspection VPC itself.

Which solution will meet these requirements?

- **A)** Change the firewall policy stateful rule order from action order to strict order and set the stateful default action to drop established.
- **B)** Set the `HOME_NET` policy or rule group variable to include the CIDR ranges of the spoke VPCs.
- **C)** Move the firewall endpoints into the transit gateway attachment subnets so that they see the traffic before it is routed.
- **D)** Add a stateless rule group that forwards all traffic to the stateful engine and set the stateless default action to drop.

<details><summary>Answer</summary>

**Answer: B.** Domain list inspection uses `HOME_NET`, which defaults to the CIDR range of the VPC hosting the firewall endpoints, so in a centralized design only traffic sourced from the inspection VPC is eligible. Setting `HOME_NET` to cover the spoke ranges is the documented fix and exactly matches the symptom that local test traffic matches while spoke traffic does not. A changes evaluation ordering and would not make ineligible traffic eligible. C breaks the design, because a firewall endpoint cannot inspect traffic entering or leaving its own subnet, so firewall subnets must be dedicated. D would send more traffic to the stateful engine but the domain rules still would not consider it, and a stateless default of drop would break the paths that currently work.

*Where this is covered: AWS Network Firewall and Route 53 Resolver DNS Firewall.*

</details>

### 8. Budget and blast radius for a global attack surface (Professional)

A global retailer is designing DDoS protection for a storefront served by CloudFront over an Application Load Balancer origin, plus a partner portal on a second Application Load Balancer with no CDN. The organization has 40 accounts under one payer account. Finance objects to paying a Shield Advanced subscription in each account, and the security team wants blocked traffic to stop before it consumes origin capacity or Regional data transfer.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Subscribe each account that owns a protected resource, relying on the fact that one subscription price covers all subscribed accounts in the payer family.
- **B)** Split the business units into separate AWS organizations so that each one negotiates its own Shield Advanced commitment.
- **C)** Put the storefront's web ACL on the CloudFront distribution rather than on the origin load balancer, so that blocking happens at the edge before the request reaches the origin.
- **D)** Move the storefront web ACL to the origin Application Load Balancer so that CloudFront caching is unaffected by rule evaluation.
- **E)** Use AWS Network Firewall in the origin VPC as the primary layer 7 control for both applications.

<details><summary>Answer</summary>

**Answer: A and C.** Every account owning a protected resource has to subscribe, but one subscription price covers all subscribed accounts in the same consolidated billing family, so the finance objection is answered without leaving any account unprotected. A global web ACL on a CloudFront distribution is evaluated at the edge before the request reaches the origin, which is what keeps blocked traffic off origin capacity and out of Regional data transfer. B breaks the single consolidated billing family that makes one subscription price possible, so each new organization pays its own 3,000 US dollars a month. D does the opposite of the stated requirement by letting attack traffic traverse the network to the origin before it is evaluated. E is the wrong layer: Network Firewall inspects VPC traffic and has no web ACL semantics, and it cannot protect the CloudFront path at all.

*Where this is covered: AWS Shield Standard compared with Shield Advanced.*

</details>

## Summary

This unit is a sequence of layer decisions. First, what does the threat touch: a DNS query answers to Route 53 Resolver DNS Firewall, a packet or flow inside a VPC to AWS Network Firewall, an HTTP request to AWS WAF, a volumetric flood to AWS Shield. Second, which resource can even carry a web ACL, remembering that CloudFront, Application Load Balancers, API Gateway REST APIs, AppSync, Cognito user pools, App Runner, Verified Access and Amplify can, while a Network Load Balancer cannot. Third, which rule shape fits: a managed rule group for known vulnerability classes, a rate-based rule with the right aggregation key for a flood you can key on, Bot Control at the level matching whether the bots self-identify, and CAPTCHA when blocking would cost real customers. Fourth, whether Shield Advanced earns its 3,000 US dollars a month, which turns on the response team, proactive engagement and cost protection, each with preconditions that must exist before an attack. Fifth, whether the requirement says "every account" and "automatically", which is always AWS Firewall Manager. Finally, for Network Firewall, whether the route tables really steer traffic symmetrically through the `vpce-` endpoint, because a firewall nothing routes to inspects nothing.

## Related units

- [Amazon VPC](../04-networking/vpc.md): the route tables, subnets and security group layers that Network Firewall and DNS Firewall sit alongside
- [Amazon CloudFront](../04-networking/cloudfront.md): the distribution a global web ACL attaches to, and the edge controls that overlap with AWS WAF
- [Amazon API Gateway](../04-networking/api-gateway.md): which API types accept a web ACL, and throttling compared with rate-based rules
- [Elastic Load Balancing](../02-compute/elastic-load-balancing.md): why an Application Load Balancer accepts a web ACL and a Network Load Balancer does not
- [Amazon Route 53](../04-networking/route53.md): hosted zones as Shield Advanced protected resources and health checks for proactive engagement
- [AWS Global Accelerator](../04-networking/global-accelerator.md): standard accelerators as a Shield Advanced protected resource type at the edge
- [AWS Organizations, IAM Identity Center and AWS Control Tower](organizations-identity-center-and-control-tower.md): all features, delegated administrators and the accounts Firewall Manager acts on
- [Detection and compliance services](detection-and-compliance-services.md): AWS Config, which Firewall Manager requires, plus GuardDuty and Security Hub

## Sources

- [How AWS WAF works](https://docs.aws.amazon.com/waf/latest/developerguide/how-aws-waf-works.html): web ACLs, rules, rule groups and WCUs as components, the protected resource types, and the protection pack relabeling
- [Associating or disassociating protection with an AWS resource](https://docs.aws.amazon.com/waf/latest/developerguide/web-acl-associating-aws-resource.html): regional compared with global scope, one web ACL per resource, CloudFront exclusivity
- [Using rule actions in AWS WAF](https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-action.html): terminating compared with non-terminating actions, token-conditional CAPTCHA and Challenge behavior, and the HTTPS requirement
- [Baseline rule groups](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-baseline.html): the rule group names and WCU costs quoted in this unit
- [Web ACL capacity units (WCUs) in AWS WAF](https://docs.aws.amazon.com/waf/latest/developerguide/aws-waf-capacity-units.html): how capacity is calculated, the 1,500 WCU inclusion and the 5,000 ceiling
- [Rate-based rule high-level settings](https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based-high-level-settings.html): evaluation windows, the minimum limit of 10 and the action restriction
- [Aggregating rate-based rules in AWS WAF](https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based-aggregation-options.html): every aggregation key option including custom keys and fingerprints
- [AWS WAF Bot Control rule group](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-bot.html): the common and targeted protection levels, WCU cost and the TGT rule naming
- [Logging AWS WAF web ACL traffic](https://docs.aws.amazon.com/waf/latest/developerguide/logging.html): the three logging destinations and request sampling
- [AWS WAF Pricing](https://aws.amazon.com/waf/pricing/): per rule and rule group monthly fee, WCU surcharge above 1,500 and Bot Control free tiers
- [AWS Shield Standard overview](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-standard-summary.html): what is included automatically and which edge services get comprehensive protection
- [AWS Shield Advanced capabilities and options](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-advanced-summary-capabilities.html): automatic mitigation, protection groups, the SRT, cost protection and the AWS WAF charges the subscription absorbs
- [List of AWS resources that AWS Shield Advanced protects](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-advanced-summary-protected-resources.html): the protected resource types, including NLB through an Elastic IP address
- [Setting up proactive engagement](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-srt-proactive-engagement.html): health check, support plan and contact prerequisites
- [Requesting a credit in AWS Shield Advanced after an attack](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-request-service-credit.html): eligible charges, preconditions and the 15 day claim window
- [Automating application layer DDoS mitigation with Shield Advanced](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-automatic-app-layer-response.html): the 150 WCU rule group, the baseline learning period and the March 2026 supersession
- [AWS Shield Pricing](https://aws.amazon.com/shield/pricing/): the 3,000 US dollars monthly fee, payer account billing and the one-year commitment
- [Joining and configuring AWS Organizations for using Firewall Manager](https://docs.aws.amazon.com/waf/latest/developerguide/join-aws-orgs.html): the all-features requirement
- [Using AWS Firewall Manager administrators](https://docs.aws.amazon.com/waf/latest/developerguide/fms-administrators.html): default and delegated administrators and administrative scope
- [Enabling AWS Config for using Firewall Manager](https://docs.aws.amazon.com/waf/latest/developerguide/enable-config.html): continuous recording and the resource types each policy type needs
- [Using AWS Firewall Manager policies](https://docs.aws.amazon.com/waf/latest/developerguide/working-with-policies.html): every policy type and the first and last rule group behavior
- [AWS Firewall Manager quotas](https://docs.aws.amazon.com/waf/latest/developerguide/fms-limits.html): policies per organization, accounts in scope and the 5,000 WCU policy limit
- [AWS Firewall Manager Pricing](https://aws.amazon.com/firewall-manager/pricing/): per policy per Region charges and the Shield Advanced inclusion
- [What is AWS Network Firewall?](https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html): Suricata, firewall subnets, stateless and stateful rule groups, the state table and the pricing shape
- [Firewall policy settings in AWS Network Firewall](https://docs.aws.amazon.com/network-firewall/latest/developerguide/firewall-policy-settings.html): default actions, immutable rule order and HOME_NET policy variables
- [Defining rule actions in AWS Network Firewall](https://docs.aws.amazon.com/network-firewall/latest/developerguide/rule-action.html): pass, drop, reject and alert, and the domain list allow and deny semantics
- [Managing evaluation order for Suricata compatible rules](https://docs.aws.amazon.com/network-firewall/latest/developerguide/suricata-rule-evaluation-order.html): action order compared with strict order
- [Stateful domain list rule groups](https://docs.aws.amazon.com/network-firewall/latest/developerguide/stateful-rule-groups-domain-names.html): wildcards, SNI and host header matching and HOME_NET for central deployments
- [Simple single zone architecture with an internet gateway](https://docs.aws.amazon.com/network-firewall/latest/developerguide/arch-single-zone-igw.html): the route table edits including the internet gateway ingress route
- [Deployment models for AWS Network Firewall](https://aws.amazon.com/blogs/networking-and-content-delivery/deployment-models-for-aws-network-firewall/): the distributed, centralized and combined models
- [AWS Network Firewall quotas](https://docs.aws.amazon.com/network-firewall/latest/developerguide/quotas.html): firewalls per account, rule groups per policy and stateful rule limits
- [AWS Network Firewall example architectures with routing](https://docs.aws.amazon.com/network-firewall/latest/developerguide/architectures.html): the unsupported paths, including VPC peering and Global Accelerator
- [How Resolver DNS Firewall works](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall-overview.html): rule group and rule priority ordering and per-VPC associations
- [Rule actions in DNS Firewall](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall-rule-actions.html): ALLOW, ALERT and BLOCK with NODATA, NXDOMAIN and OVERRIDE responses
- [Managed Domain Lists](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall-managed-domain-lists.html): the four AWS managed lists and their coverage
- [DNS Firewall VPC configuration](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall-vpc-configuration.html): the fail closed default and the SERVFAIL response
- [Using DNS Firewall to filter outbound DNS traffic](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall.html): why Network Firewall cannot see Resolver queries
