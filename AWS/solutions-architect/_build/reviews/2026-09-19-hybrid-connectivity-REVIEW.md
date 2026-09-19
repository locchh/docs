# Independent review: hybrid-connectivity.md, 2026-09-19

Reviewer: independent agent, read the unit cold, did not edit it. This was the
unit's first review of any kind. Coordinator applied the findings.

The reviewer was dispatched with a warning that the draft sat 2 percent above
the tier L floor, which this project has recorded as correlating with rework,
and with the instruction to check each of the fourteen enumerated plan-row
sub-topics individually. That is what surfaced the Network Manager gap.

VERDICT: FIX THEN PASS, after three blocking findings.

## Blocking, all fixed

1. **Two VPN features were conflated.** The unit said large-bandwidth tunnels
   "reach up to 5 Gbps per tunnel and are managed through a Site-to-Site VPN
   Concentrator". The 5 Gbps figure is right but the attribution is wrong, and
   the error inverts a design decision. The coordinator confirmed on the
   Concentrator page: it targets 25 or more remote sites each needing under
   100 Mbps, caps a site at 100 Mbps and the attachment at 5 Gbps aggregate,
   attaches only to a Transit Gateway, and supports BGP only. A reader taking
   the original sentence at face value would reach for a Concentrator to make
   one tunnel faster and get a per-site rate twelve times lower than a standard
   tunnel. Rewritten to separate the two and to name the Concentrator as fan-in
   for many small branches.

2. **A dead source.** `direct-connect-site-link.html` is a 1,376-byte
   meta-refresh stub. Replaced with the Site-to-Site VPN Concentrator page,
   which the corrected paragraph now needs; the SiteLink VIF support table is
   already carried by the virtual interfaces source, whose annotation now says
   so. All 33 source URLs resolve under `CHECK_URLS=1`.

3. **AWS Network Manager was mentioned, not taught.** It is an enumerated
   sub-topic of the plan row's "Transit Gateway in depth" and had one sentence
   plus a clause. Now a two-paragraph treatment: the global network as a
   container for registered gateways plus the sites, devices and links model;
   topology and BGP state change events through EventBridge; Route Analyzer for
   tracing a configured path and finding asymmetry; and the boundary that
   matters for exam questions, which is that Network Manager observes without
   changing forwarding, so unifying policy is Cloud WAN and seeing or
   troubleshooting an existing topology is Network Manager.

## Should fix

| # | Finding | Applied |
|---|---|---|
| 1 | "Two VPCs whose VGWs associate with one DXGW cannot exchange traffic" was stated absolutely; a November 2021 exception exists | Yes. Coordinator confirmed the exception verbatim on the DXGW page and added it as a connectivity leak to design against, with the specific-prefix, separate-DXGW and blackhole-route controls |
| 2 | Owned SAA 4.4 bullet names VPC peering, which appeared only as a quiz distractor and one clause | Yes, covered in the new transitive routing section |
| 3 | 33 sources against a tier L ceiling of 25, with no overage note | Noted here. STYLE_SPEC is explicit that a citation is never dropped to stay under the ceiling, so the count stands |
| 4 | Transitive routing was taught but scattered across a table row, the DXGW section, peering and PrivateLink | Yes. New `## Transitive routing, and what is not transitive` section consolidates the rule: Transit Gateway transitive by design, VPC peering not and not fixable by a route, TGW peering needing explicit static routes with no third-gateway reach, VGW not a transit device, PrivateLink deliberately non-transitive |

Optional findings on the Associate labels of Q4 and Q9 were recorded and not
applied; the reviewer judged both defensible as keyed.

## Verification

Twenty-three official pages fetched. Every hard number held: dedicated
1/10/100/400 Gbps, hosted 50 Mbps to 25 Gbps, LAG limits, MACsec platform
support, the resiliency tiers, BGP path selection and the AWS community strings,
the SiteLink VIF support matrix, 1.25 Gbps standard tunnels, MTU 1,446 and
MSS 1,406, ECMP requiring dynamic routing, Transit Gateway quotas of 5,000
attachments, 20 route tables, 10,000 routes and 100 Gbps per Availability Zone,
multicast exclusions, Connect peer BGP sessions, and Cloud WAN quotas.

All four currency claims in the tracker were verified: the large-bandwidth VPN
tunnel exists but was misattributed, IPv6 Client VPN holds, cross-Region
PrivateLink holds, and the Route 53 VPC Resolver rename holds.

Quiz: solved 10 of 10 independently, no disagreement with any key, no second
defensible option on any item.

Post-fix mechanical check: 0 errors, body 6,658 words, 10 topic sections against
the tier L range of 7 to 10, 33 sources all resolving.
