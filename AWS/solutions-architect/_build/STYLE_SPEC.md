# Authoring spec for service units

This is the contract every content file in `aws/solutions-architect/services/`
must satisfy. A reviewer will check the file against it line by line.

Before writing anything, read:

1. This file, in full.
2. `UNIT_PLAN.md` in this folder, at least the row you were assigned and the full
   file map, because you will link to other units.
3. `exam-guide-saa-c03.md` and `exam-guide-sap-c02.md` in this folder. Your
   dispatch prompt lists the specific exam guide bullets your unit owns. Those
   are a hard requirement: each must be taught well enough that a reader could
   answer an exam question on it.
4. The two exemplar units, in full. They define voice, density, section order and
   quiz format. Their subject matter is generative AI and is irrelevant. Copy the
   shape, not the content.
   - `aws/aip-c01/learning-paths/04-operational-efficiency-optimization/03-monitoring-genai-applications.md`
   - `aws/aip-c01/learning-paths/01-fm-integration-data-compliance/04-vector-stores.md`

Write only the file you were assigned. Create its category directory if needed.

## The two readers

Every unit serves two readers at once.

The **Associate reader** is preparing for SAA-C03 and may be meeting the service
for the first time. Define the service, and every other AWS service you mention,
in one clause at first appearance, in bold: "**Amazon SQS**, the managed message
queue". This applies even to famous services. The Associate reader must be able
to answer every Associate question in the unit using only the unit.

The **Professional reader** has passed the Associate exam and is preparing for
SAP-C02. They want the multi-account view, the organization-wide view, the
migration-scale view, the quotas that bite, and the way a Professional question
extends the same scenario. Serve them in a dedicated `## Professional depth`
section and, where a topic naturally extends, in at most three inline
blockquotes beginning `> **Professional depth.**`.

An Associate reader must be able to skip everything marked Professional depth and
still be fully prepared for SAA-C03. Nothing that SAA-C03 tests may live only in
a Professional depth section.

## Depth tiers

Your assignment names a tier. Body words are counted from the top of the file to
the `## Knowledge check` heading.

| Tier | Body words | Topic sections | Quiz questions |
|---|---|---|---|
| XL | 10,000 to 13,000 | 10 to 14 | 12 |
| L | 6,000 to 8,000 | 7 to 10 | 10 |
| M | 3,500 to 5,000 | 5 to 7 | 8 |
| S | 1,800 to 3,000 | 3 to 5 | 6 |
| XS group | 2,500 to 5,000 for the file, 500 to 1,200 per service | one `##` per service | 6 to 8 |

For XL and L units, write the file in several appends of one or two sections
each. A single enormous write tends to get truncated or to lose structure.

## Section order

The order is fixed. Do not add, remove or reorder top-level sections.

````
# <Service name exactly as AWS writes it, for example Amazon DynamoDB>

**Where it sits on the exams.** One paragraph. What the service is, in two
sentences. Which SAA-C03 tasks and which SAP-C02 tasks it appears in, cited by
number from the exam guides, for example "SAA-C03 tasks 3.3 and 4.3, SAP-C02
tasks 2.5 and 4.4". The one-sentence rule of thumb the exam wants you to know.

## <Topic section>
...between 3 and 14 of these, per the tier. Continuous prose. Use `##` only. Do
not use `###` inside a topic section, except in XS group files, where each
service is a `##` and its parts may be `###`.

Cover topics in this order where they apply: what it is and how it works, the
configuration choices that decide exam questions, integrations with neighboring
services, security including IAM, encryption and network path, resilience and
scaling, monitoring, pricing shape, the limits that matter.

## Professional depth
3 to 8 paragraphs, scaled to tier. Multi-account and organization-wide use.
Hybrid and migration-scale patterns. Quotas that bite. Failure modes. What
changes at scale. How a Professional question extends the Associate scenario.

## Worked scenario
One company, one end-to-end design that exercises most of the unit. Two to four
paragraphs. End by saying what the exam asks about this scenario and what the
keyed answer is.

## Exam lens
8 to 20 bullets, scaled to tier, each of the form: "quoted question wording"
maps to answer. Include distractor patterns, for example "X is the distractor
when the requirement says Y".

## Knowledge check
See the quiz rules below.

## Summary
One paragraph, 120 to 200 words, restating the unit as a series of decisions.

## Related units
3 to 8 bullets linking neighboring units by relative path with one clause of
reason:
- [Amazon VPC](../04-networking/vpc.md): endpoints and security groups for private access
Link only to files that appear in UNIT_PLAN.md. Most of those files do not exist
yet, and that is fine: write the real markdown link anyway. `check.sh` reports a
link to a planned file as a warning, not an error, and the link resolves as soon
as that unit lands. Never degrade a link to plain text or a backticked path to
silence the checker.

## Sources
Scaled to tier: 8 to 15 for S and XS, 15 to 25 for M and L, up to 30 for XL.
Official AWS pages you actually fetched while writing this unit, one line each.
Never drop a citation to stay under the ceiling: if a claim needs a source, list
it and note the overage in your report.
- [Page title](URL): what it settles
````

## Facts and sources

Verify every capability, limit, number, price shape and service status claim
against official AWS documentation before writing it. Fetch the page. Do not
write a number you did not read.

Allowed source hosts, in order of preference:

1. `docs.aws.amazon.com`, including the Well-Architected framework pages
2. `aws.amazon.com` for FAQs, pricing pages, feature pages, What's New posts and
   the Architecture Center
3. `aws.amazon.com/blogs` for architecture patterns only

No third-party sites. No videos. No training vendors.

One failure mode to watch: a fetch can return a composed summary of a page rather
than the page itself. If what comes back reads like prose written about the
documentation instead of the documentation, or if it lacks the tables, headings
and parameter names the page should have, do not build a claim on it.

The cause is known. `WebFetch` is what produces those summaries. Two workarounds
both work, and the second is the most reliable:

1. The Tavily extract tool returns the raw page for URLs that `WebFetch` only
   summarizes, including the SQS FIFO fundamentals page and the AWS pricing pages.
2. Better still, fetch the page with `curl` and extract the text locally. The EBS
   writer did this for every source and read the tables and footnotes directly,
   so no summary entered the unit at all. For any page whose content is a table,
   a footnote or a quota list, prefer this.

Failing both, find the API reference for the same fact.

If a number changes often, describe the shape rather than the figure: "billed per
GB-month and per thousand requests" rather than a price.

**Capability claims against exam mappings.** These two kinds of sentence follow
different rules, and the distinction resolves most conflicts between current AWS
documentation and the older exam guides. A capability claim says what a service
can do; it must be true today, without exception. An exam mapping says which
answer a question wants; it may follow the guide even where the service has moved
on. Write a mapping as a mapping, so the reader can tell: "on the exams, X maps to
Y" rather than "X cannot do Y". Where the two diverge, key the quiz to the mapping
and put the current capability in a Professional depth note. A reviewer will test
every sentence this way.

State facts as of September 2026. AWS renamed and retired a lot between 2024 and
2026, and both exam guides still use older names in places. When the guide's name
and the current name differ, teach both in one sentence: "**Amazon Quick**,
formerly Amazon QuickSight, the serverless business intelligence service". When a
service is in maintenance mode, closed to new customers, or scheduled for end of
support, say so in one sentence, name what AWS recommends instead, and still
teach what the exam expects.

Verify these before stating anything about them in either direction. Each one
changed recently enough that training data is unreliable:

Amazon Quick and QuickSight. Amazon Data Firehose. Amazon Managed Service for
Apache Flink. Snow Family lineup, especially Snowcone and Snowmobile. Elastic
Transcoder. Aurora Serverless v1. Amazon Inspector Classic. CodeCommit. QLDB.
Pinpoint. Proton. Audit Manager. CloudTrail Lake. CloudWatch Evidently. The S3
storage class lineup. The EBS volume type lineup. ElastiCache engines including
Valkey, and ElastiCache Serverless. DynamoDB global tables multi-Region strong
consistency, and warm throughput. RDS Multi-AZ DB clusters and Blue/Green
deployments. Resource control policies and declarative policies in Organizations.
Public IPv4 address charges. NAT gateway pricing shape. Route 53 Application
Recovery Controller and zonal shift. AWS Backup logically air-gapped vaults. EKS
Auto Mode. ECS Service Connect. Lambda SnapStart runtime support. CloudFront
Functions compared with Lambda@Edge. API Gateway quotas. Direct Connect port
speeds and MACsec. Transit Gateway features. Control Tower controls. IAM Identity
Center trusted identity propagation. Aurora DSQL and Aurora Limitless. Amazon
Timestream editions. Redshift Serverless. Glue for Ray. Lake Formation governed
tables. Migration Hub features. DMS Serverless. Kendra and Personalize status.
VMware Cloud on AWS status.

Never invent question statistics, exam percentages beyond the published domain
weights, or "AWS says" claims you did not read.

## Quiz rules

The `## Knowledge check` section holds original questions written by you. They
are not copied from any practice exam, so they will not spoil a later mock.

Count is set by the tier. At least a quarter must be multiple response.

Label every question with its exam level in the heading:

```
### 3. Cross-Region read scaling (Associate)
### 7. Consolidating logs across 40 accounts (Professional)
```

Roughly two thirds Associate, one third Professional. Professional questions are
longer, involve several accounts, Regions or competing constraints, and often
have two right-looking options separated by a single requirement.

Register: a two to six sentence business scenario ending in one of

- "Which solution will meet these requirements?"
- "Which solution will meet these requirements MOST cost-effectively?"
- "Which solution will meet these requirements with the LEAST operational overhead?"
- "Which solution will meet these requirements with the LEAST latency?"
- "Which combination of steps will meet these requirements? (Select TWO.)"

Either opening may carry either qualifier, so "Which combination of steps
will meet these requirements MOST cost-effectively? (Select TWO.)" is also
correct. `check.sh` enforces this set; a stem outside it is an error.

Four options A to D for multiple choice. Five options A to E for multiple
response, and state the number to select.

Distractors must be plausible. Use one of these three shapes: a real service used
for the wrong job, a custom build of something AWS already manages, or a solution
that meets some stated requirements while breaking another one in the same stem.
Never write a joke option.

Exactly one defensible key per multiple choice question. Never write an ambiguous
question. Spread correct letters across A to D across the unit.

Format exactly as follows:

````
### 1. Short title (Associate)

A logistics company stores 40 TB of shipment scans in Amazon S3. Auditors request
individual documents about twice a year, and each request must be served within
12 hours. The company wants the lowest possible storage cost.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Store the scans in S3 Standard-IA.
- **B)** Store the scans in S3 Glacier Flexible Retrieval and use standard retrievals.
- **C)** Store the scans in S3 Glacier Deep Archive and use standard retrievals.
- **D)** Store the scans in S3 Intelligent-Tiering with the Deep Archive Access tier enabled.

<details><summary>Answer</summary>

**Answer: B.** ...60 to 160 words. Say why the key is right, then dismiss every
other option by letter, naming the requirement each one breaks...

*Where this is covered: Storage classes and retrieval times.*

</details>
````

The italic line must name a real `##` section heading in the same unit.

No confidence marks, no source attributions. These questions are yours.

Use real numbers only where a real limit or price rule decides the answer, and
only where you verified that number.

## Prose rules

Continuous prose in topic sections. Bullets are for the Exam lens, Related units
and Sources sections only, plus anywhere the exemplar uses them.

Tables are welcome for comparisons: storage classes, volume types, load balancer
types, routing policies, DR strategies, capacity modes. Every table needs a
sentence before it saying what to read from it.

Plain sentences. No em dash, U+2014. Use a comma, a colon, or a new sentence. The
en dash, U+2013, is required in official exam names such as "Solutions Architect –
Associate" and is allowed only there. No emoji. No exclamation marks. No
marketing adjectives. No "In this section we will".

US spelling, to match AWS documentation: optimize, center, behavior.

Bold a service or feature name on its first appearance in the unit and never
again. Bold nothing else except the `**Where it sits on the exams.**` lead, the
`**Professional depth.**` blockquote lead, and the `**Answer: X.**` line.

Expand acronyms on first use: recovery time objective (RTO).

Quote the exam's own constraint wording when mapping wording to a service:
"least operational overhead", "MOST cost-effective".

Code is welcome where it teaches: a CLI command, an IAM policy document, a
CloudFormation snippet, an EventBridge event pattern. Keep each block short and
fenced with a language tag.

Keep the unit self-contained. A reader with only this unit must be able to answer
its questions.

## Folding in existing notes

If your assignment says to fold in a notes file, read that file in full first.
Keep every substantive fact that is still correct, rewritten into this voice.
Correct anything wrong or outdated and list every correction in your report. Drop
lecture-transcript phrasing, first-person asides and duplicated sections. Keep
useful CLI examples, trimmed.

Do not delete the notes file. The coordinator removes it after review.

## Finish checklist

Run all of this before reporting.

1. `wc -w` on the file. Body, meaning everything before `## Knowledge check`, is
   within the tier range.
2. Every service and feature listed in your `UNIT_PLAN.md` row is taught, and
   every exam guide bullet your dispatch prompt assigned you is taught.
3. Every template section is present, in order, with no extras.
4. Every AWS service is bolded once and defined at first mention.
5. Quiz count matches the tier. At least a quarter multiple response. Keys spread
   across letters. Every distractor dismissed by letter in the rationale. Every
   "Where this is covered" line names a real section in this unit. Every question
   labeled Associate or Professional.
6. `bash aws/solutions-architect/_build/check.sh <your file> <TIER>` passes, run
   from the repository root.
7. Related units link only to files in `UNIT_PLAN.md`, with correct relative
   paths.
8. Sources are only official AWS pages you actually fetched.

## Report format

Report in under 300 words:

- File path
- Body word count and total word count
- Section list
- Service status notes you included, for example "noted Aurora Serverless v1 end
  of support"
- Corrections made to folded notes, if any
- Anything you could not verify, named explicitly
- Each assigned exam guide bullet with the section that teaches it, one line each
