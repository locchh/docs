# Networking

Everything here answers one question in a different place. **Amazon VPC** is the
private network your resources sit in, and it decides what may reach them from
inside AWS. Hybrid connectivity extends that network to a data center over **AWS
Direct Connect**, a dedicated private link, or **AWS Site-to-Site VPN**, an
encrypted tunnel over the internet. **Amazon Route 53** decides which endpoint a
name resolves to. **Amazon CloudFront** and **AWS Global Accelerator** decide
where a user's traffic enters the AWS network. **Amazon API Gateway** decides
who may call an API and on what terms.

The decision the category keeps asking you to make is where the isolation
boundary sits and what is allowed to cross it. A public subnet or a private one,
a NAT gateway or a VPC endpoint, a security group or a network ACL, a peering
connection or **AWS Transit Gateway**, a hub that routes between many networks,
a public API or a private one: each is that choice at a different scale. Cost
follows the same line, because almost every network charge on either exam comes
from bytes crossing a boundary, between Availability Zones, between Regions, or
out to the internet.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [vpc.md](vpc.md) | Lay out subnets and routing, choose between security groups and network ACLs, and reach AWS services privately with VPC endpoints | XL |
| [hybrid-connectivity.md](hybrid-connectivity.md) | Design a resilient path to a data center, and connect many VPCs through a transit hub | L |
| [route53.md](route53.md) | Choose a routing policy, wire up health checks and failover, and split public from private DNS | L |
| [cloudfront.md](cloudfront.md) | Configure origins, cache behavior and signed access, and secure a distribution | M |
| [global-accelerator.md](global-accelerator.md) | Tell anycast IP addresses apart from a CDN and from DNS failover | S |
| [api-gateway.md](api-gateway.md) | Pick an API type and endpoint type, and apply authorizers, throttling and caching | L |

## Which exam tasks this serves

On SAA-C03 it is tasks 3.4 and 4.4 outright, plus task 1.2 for segmentation,
security groups and securing external connections, and tasks 2.1 and 2.2 for API
creation, edge accelerators and Route 53 failover. On SAP-C02 it is task 1.1
outright, the network connectivity task statement, plus 2.3 for route tables and
service endpoints, 2.4 for DNS routing policies, 3.3 for edge services, and 4.2
for the networking and DNS side of a migration.

## Reading order

Read `vpc.md` first: it is the second-largest unit in the course,
and every other unit here assumes it. Then `route53.md`, then `cloudfront.md`
and `global-accelerator.md` together, since the exam contrasts them. Read
`api-gateway.md` next. Leave `hybrid-connectivity.md` for last: an
Associate-only candidate needs only its Direct Connect against VPN comparison
and the idea of a transit hub, and can skim the rest, which is Professional
material. Load balancing lives in the
[compute category](../02-compute/README.md), even though AWS files it under
networking.
