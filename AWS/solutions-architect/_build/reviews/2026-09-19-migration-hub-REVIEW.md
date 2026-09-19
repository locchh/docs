# Independent review: migration-hub-discovery-and-strategy.md, 2026-09-19

Reviewer: independent agent, read the unit cold, did not edit it. Coordinator
applied the findings.

Provenance note: this unit had no author record. An earlier session wrote the
file and ended before updating the tracker, so the draft arrived with no list of
verified facts and no statement of which pages were fetched. The reviewer was
dispatched with instructions to treat every claim as unverified and to weight
fact checking toward service status, which is where the blocking error was.

VERDICT: FIX THEN PASS, after one blocking finding.

## Blocking

The opening paragraph claimed the unit serves "SAA-C03 tasks 2.2, 3.3 and 4.3".
Those task statements are designing highly available architectures, determining
high-performing database solutions, and designing cost-optimized database
solutions. The unit teaches none of them, and `services/README.md` line 471
records its SAA ownership as `None`. The plan row's "3 / 3, plus SAP domain 4"
is a lesson-signal count that was misread as task numbers.

Fixed: the paragraph now states that no SAA-C03 task statement owns this
material and that an Associate reader needs only the vocabulary of the seven
strategies. The SAP-C02 4.1 ownership and 4.2 support role are unchanged.

## Should fix, all applied

| # | Finding | Applied |
|---|---|---|
| 1 | `aws.amazon.com/migration-hub/pricing/` 301-redirects to the Transform landing page, so the annotated cost detail is unreadable there | Replaced with the Refactor Spaces pricing section, which states usage hours, API requests and provisioned resources. All 22 source URLs now resolve under `CHECK_URLS=1` |
| 2 | The Refactor Spaces source was annotated "lifecycle notice", implying an end-of-support date that does not exist | Reworded to "new-customer closure notice". Coordinator confirmed on the availability-change page: closure dated November 7, 2025, no shutdown date, and the FAQ answers that the service continues to operate for existing customers |
| 3 | `move group`, `migration wave` and `Total cost of ownership (TCO)` were bolded though they are concepts, not service or feature names | Unbolded |
| 4 | Strategy Recommendations, Orchestrator and Refactor Spaces appeared unbolded and undefined at first mention, then bolded 60 lines later | Bolded and defined at first appearance, plain thereafter |
| 5 | Refactor Spaces was said to orchestrate "Elastic Load Balancing"; the docs specify a Network Load Balancer, API Gateway VPC links and Transit Gateway | Corrected to those three |
| 6 | Asset planning, an owned 4.1 bullet, was one sentence | Expanded to a paragraph covering target account and Region, sizing from measured demand, licensing constraints on tenancy and instance family, named ownership at and after cutover, and shared assets forcing coordinated moves |
| 7 | The Refactor Spaces closure date was absent from the body | Added, November 7, 2025 |

Optional finding 2 was also applied rather than left: the unit cautioned that a
Transform referral "does not imply exact feature parity", but the availability
page states Transform provides equivalent capabilities, that current Migration
Hub features including Strategy Recommendations and Orchestrator are available
there, and that no data migration is required. The caution contradicted the
source and now reports what AWS states while keeping the practical warning that
Transform is a different product with its own console and workflow.

Optional findings 1 and 3, the Transform "agentic AI" framing and the "existing
customer" question framing, were not applied.

## Verification

Twenty official pages fetched, twenty claims confirmed, including the Migration
Hub and Application Discovery Service closures of November 7, 2025, the seven Rs
names and order, home Region behavior, Discovery Agent versus Agentless
Collector capabilities, Orchestrator step-group restrictions, Refactor Spaces
concepts and charging, and Migration Evaluator still being available and
complimentary.

Quiz: the reviewer re-derived 8 of 8 keys against documentation and agreed with
every one, with no second defensible option. It states plainly that this was a
re-derivation, not a blind solve, because it had read the file top to bottom as
dispatched.

Post-fix mechanical check: 0 errors, body 4,512 words, 22 sources all resolving,
two planned-link warnings.
