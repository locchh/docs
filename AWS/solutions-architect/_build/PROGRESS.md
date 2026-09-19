# Progress tracker

The source of truth for what is done. Update the row after every unit, then
commit. Any agent picking up this project should read `HANDOFF.md` and then this
file to find the next task.

## Handoff state, as of 2026-09-12

The tree is clean and pushed; everything below is committed. 37 of 70 service
units are done, meaning written, checked and passed by an independent review.

Three units are written but NOT done. They are the next work, in this order:

| File | What it still needs |
|---|---|
| `08-management/systems-manager.md` | Quiz quality only. The body rework is complete and both fact errors are fixed. Do NOT re-review the body. See the task list below. |
| `08-management/developer-tools-and-cicd.md` | A first independent review. Stems were fixed in a separate pass; the body has never been read by anyone. |
| `04-networking/hybrid-connectivity.md` | A first independent review. Tier L, 6,112 body words, never reviewed. |

The Systems Manager quiz tasks, all from a review that solved every question and
found no wrong key:

- Q5's stem says a task starts "so close to the end that it would still be
  running when the period closes". Cutoff does not guarantee that: it is a fixed
  hours-before-end value, no task starts after end minus Cutoff, and running
  tasks are not terminated. The body states it correctly. Fix stem and rationale.
- Q6's options A and B embed their own justification and B is self-refuting.
  Rewrite the options.
- Straw-man distractors that restate the stem's prohibition: Q4 C, Q7 A and E,
  Q8 B and D. Replace with a neighbouring capability doing what it genuinely
  does, per the three distractor shapes in STYLE_SPEC.
- The split is 6 Associate / 2 Professional; the spec wants roughly 5/3.

### Lesson learned, worth applying to every remaining unit

A unit written to the bottom of its tier range has needed a rework round roughly
half the time. Systems Manager sat 21 words above the tier M floor and the review
found two factual errors plus six coverage gaps; reworked to 4,689 words it is
sound. Kinesis and detection-and-compliance told the same story. HANDOFF.md now
tells writers to target the middle of the range, not the floor or the ceiling.
Hold them to it: it is cheaper than a rework.

### Two checks added on 2026-09-12, run both on every file

```
bash _build/check.sh <file> <TIER>              # now enforces the quiz stem register
CHECK_URLS=1 bash _build/check.sh <file> <TIER> # follows every Sources URL
```

The URL run catches retired AWS pages, which still return HTTP 200 because they
redirect to their guide root. It found a dead link in `iam.md`, a unit that had
already passed a review. The stem check found that five units had zero compliant
stems. Both classes of error were invisible before.

### One process problem worth fixing before writing more units

Three units in a row came in at or above their tier ceiling, which meant the
coordinator spent more effort trimming words than applying review findings. On
the WAF unit that cost roughly a dozen edit cycles to recover 150 words. Either
tell writers to target the middle of their tier range rather than the ceiling,
so review additions have somewhere to go, or raise the budget for multi-service
units. The five-service WAF unit is the clearest case that the tier M range may
simply be wrong for a unit of that span.

Status values:

| Value | Meaning |
|---|---|
| `todo` | Not started |
| `writing` | An agent is working on it now. Put the date so a stale claim is visible |
| `written` | File exists, writer reported done |
| `checked` | `check.sh` passes |
| `reviewed` | A reviewer returned PASS or FIX THEN PASS |
| `done` | Findings applied, committed |

A unit is only `done` after an independent review. Do not skip the review pass.

## Phase 0: coverage matrix

Do this before writing any unit. See the "Phase 0 in detail" section of
`HANDOFF.md`.

| File | Status | Notes |
|---|---|---|
| `services/README.md` | done | 379 of 379 guide bullets assigned and independently reviewed; reproducible generator in `_build/` |

## Phase 1: category READMEs

| File | Status | Notes |
|---|---|---|
| `services/01-storage/README.md` | done | 492 words; reviewed; EBS Multi-Attach and Storage Gateway wording fixed |
| `services/02-compute/README.md` | done | 496 words; reviewed; Lambda lifecycle and instance-backed scaling wording fixed |
| `services/03-containers/README.md` | done | 492 words; reviewed; task support mappings added |
| `services/04-networking/README.md` | done | 499 words; reviewed; PASS |
| `services/05-database/README.md` | done | 500 words; reviewed; PASS |
| `services/06-integration/README.md` | done | 490 words; reviewed; EventBridge relationship wording fixed |
| `services/07-security/README.md` | done | 499 words; reviewed; PASS |
| `services/08-management/README.md` | done | 491 words; reviewed; prevention controls and reading order fixed |
| `services/09-analytics/README.md` | done | 499 words; reviewed; task support mappings added |
| `services/10-migration/README.md` | done | 447 words; reviewed; SAA 2.2 mapping added |
| `services/11-ml-and-media/README.md` | done | 476 words; reviewed; SAP 3.3 mapping added |

## Phase 2: service units

Batch letters come from `HANDOFF.md`. Work A through H.

### 01-storage

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `s3.md` | XL | A | done | Reviewed 2026-09-12, FIX THEN PASS, no blocking findings, 28 facts verified. 7 should-fix items applied. Optional items not applied: Q7 label reads Associate; Expedited restore size nuance; Object Lock variable retention and event holds; MRAP runs on Global Accelerator; Mountpoint limits; s3:RequestPayer condition key; S3 Outposts storage class |
| `ebs.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, 30 numeric claims verified by curl fetch, no summaries. One blocking: a quiz stem asked for something no option pair delivered. 5 should-fix applied. Review settled the gp2 and io1 generation question: EBS and RDS run separate storage lifecycles and both units were right, each now names its context |
| `efs.md` | S | G | todo | |
| `fsx.md` | S | G | todo | |
| `storage-gateway.md` | S | G | todo | |
| `backup-and-disaster-recovery.md` | L | F | done | Reviewed 2026-09-12, FIX THEN PASS, 20 facts verified. Owns 40 bullets, the most in the course. Two blocking: FSx for OpenZFS has native cross-Region replication, and a quiz option was defensible as written. Reviewer confirmed the AWS Transform MGN rename, Aurora at 10 secondary Regions, and that S3 RTC is 99.9 percent |
| `snow-family.md` | S | G | todo | Verify Snowcone and Snowmobile status |
| `transfer-family-and-datasync.md` | S | G | todo | |

### 02-compute

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `ec2.md` | L | B | done | Reviewed 2026-09-12, FIX THEN PASS, 30 facts verified, all 10 keys agreed. One blocking error: z listed as a memory-optimized series letter when Z is the series and z is an option letter. 7 should-fix applied, including three quiz rationales that argued the right answer for the wrong reason |
| `ami.md` | S | G | todo | |
| `ec2-auto-scaling.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, no blocking findings, 30 facts verified, all 8 keys agreed. 3 should-fix applied. Review confirmed the hibernation contradiction with ec2.md, now reconciled in both units |
| `elastic-load-balancing.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, 31 facts verified, all 8 keys agreed under a blind second-agent audit. One blocking self-contradiction on Classic Load Balancer advantages. Review also caught an error in the already-done vpc.md, since fixed |
| `lambda.md` | L | C | done | Reviewed 2026-09-12, FIX THEN PASS, no blocking findings, 24 facts verified, all 10 keys agreed. Reviewer settled both open questions: the 1,000 per 10 seconds burst rate is authoritative and Managed Instances is stated correctly |
| `elastic-beanstalk.md` | S | G | todo | |
| `batch.md` | S | G | todo | |
| `other-compute-and-end-user.md` | XS group | H | todo | |

### 03-containers

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `ecs-and-ecr.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, no blocking findings, 30 facts verified, all 8 keys agreed. Confirmed blue/green is now a native ECS deployment strategy, recommended over the CodeDeploy controller. 4 should-fix applied |
| `eks.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, 26 facts verified, all 8 keys agreed. Two blocking: Auto Mode cannot use custom networking, and GPU was mapped to managed node groups alone when Auto Mode supports it too, which sent a least-overhead question to the wrong answer. 3 should-fix applied |

### 04-networking

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `vpc.md` | XL | A | done | Reviewed 2026-09-12, FIX THEN PASS, 32 facts verified, all 12 keys agreed. 2 blocking and 10 should-fix applied. Writer correctly dropped two unverifiable Transit Gateway security group claims. Later corrected when the ELB reviewer found a blanket claim that an internet-facing load balancer takes no Elastic IP, which is true of ALB but not NLB |
| `hybrid-connectivity.md` | L | E | checked | Uncommitted complete draft: 6112 body words, 10 questions, 33 fetched AWS sources. Check passes; independent cold review still required. Includes current large-bandwidth VPN, IPv6 Client VPN, cross-Region PrivateLink and Route 53 VPC Resolver changes while preserving exam-era mappings |
| `route53.md` | L | D | done | Reviewed 2026-09-12, FIX THEN PASS, 30 facts verified, all 10 keys agreed. Both renames confirmed: Amazon Application Recovery Controller and Route 53 VPC Resolver. One blocking fix: quota adjustability was stated backwards. 5 should-fix applied |
| `cloudfront.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, 25 facts verified, all 8 keys agreed. All seven of the writer's quota corrections against common study material confirmed. Two blocking: the regional edge cache skip is S3-specific, and origin failover on a connection failure requires 503 to be nominated. 5 should-fix applied |
| `global-accelerator.md` | S | G | todo | |
| `api-gateway.md` | L | C | done | Reviewed 2026-09-12, FIX THEN PASS, 25 facts verified, all 10 keys agreed. All four of the writer's claims that contradict common study material held up, including the integration timeout no longer being a flat 29 seconds. 1 blocking and 7 should-fix applied |

### 05-database

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `rds.md` | L | B | done | Reviewed 2026-09-12, FIX THEN PASS with NO blocking findings, the first unit to achieve that. 28 facts verified including the whole Multi-AZ comparison table, all 10 keys agreed, no cross-unit contradiction. 4 should-fix applied. Reviewer settled the cross-Region cluster replica question the writer had hedged |
| `aurora.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, 17 facts verified, all 8 keys agreed. One blocking error that invalidated a conclusion: replicated write I/Os are billed on both Aurora Standard and I/O-Optimized, not only Standard, so the claim that a global database therefore belongs on I/O-Optimized did not follow. 4 should-fix applied. Reviewer notes the Aurora FAQ still says five secondary Regions, which is stale; the user guide says ten and both units follow it |
| `dynamodb.md` | L | C | done | Reviewed 2026-09-12, FIX THEN PASS, no blocking findings, 25 facts verified, all 10 keys agreed. 4 should-fix applied, including a missing status note on Amazon Timestream, which closed to new customers in June 2025 |
| `elasticache-and-memorydb.md` | M | F | done | 4842 body words, 8 questions, 25 sources. Writer flagged a conflict: current AWS docs position ElastiCache with durability for single-Region and MemoryDB for multi-Region active-active, which neither exam guide reflects. Quizzes key the classic rule; the new positioning sits in one Professional depth blockquote. The next in-memory or DR unit will hit the same conflict |
| `documentdb.md` | S | G | todo | |
| `neptune.md` | S | G | todo | |
| `keyspaces-qldb-and-timestream.md` | XS group | H | todo | Verify QLDB status |
| `redshift.md` | S | G | todo | |

### 06-integration

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `sqs.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, no blocking findings, 23 facts verified. Confirmed the 1 MiB payload, raised from 256 KiB in August 2025. Reviewer diagnosed the WebFetch summarization problem affecting the whole project. 4 should-fix applied |
| `sns.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, 24 facts verified by curl. Two blocking: Amazon Data Firehose wrongly grouped with the AWS managed retry endpoints, and a quiz with two defensible answers. 6 should-fix applied |
| `eventbridge.md` | M | F | done | Written across two agents after the first was interrupted. Reviewed 2026-09-12, FIX THEN PASS, 24 facts verified, all 8 keys agreed, no seam found between the two halves except in Sources. One blocking error on the schema registry names. 5 should-fix applied |
| `step-functions.md` | S | G | todo | |
| `amazon-mq.md` | S | G | todo | |
| `appflow-appsync-amplify-ses-pinpoint.md` | XS group | H | todo | Verify Pinpoint status |

### 07-security

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `iam.md` | L | B | done | Reviewed 2026-09-12, FIX THEN PASS, 26 facts verified, all 10 keys agreed. One blocking error in the policy evaluation logic fixed: a missing Allow at the resource-policy step does not end evaluation in the same account. 6 should-fix applied. Corrected 5 stale claims in the folded STS notes |
| `organizations-identity-center-and-control-tower.md` | L | E | done | Reviewed 2026-09-12, FIX THEN PASS, 30 facts verified, all 10 keys agreed. Two blocking errors: a declarative policy type that does not exist, and AWS Service Catalog placed in the wrong delegated-administration group. 7 should-fix applied |
| `kms-and-cloudhsm.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, 26 facts verified, all 8 keys agreed. One blocking: SSE-KMS used undefined and first appearing inside Professional depth. Real coverage gap closed: this unit is sole owner of two SAP 2.3 encryption-in-transit rows and gave them three sentences. Body runs 4 percent over tier as a result, within tolerance. Reviewer confirmed the writer was right to teach the S3 throttling case without a number |
| `acm.md` | S | G | done | 2999 body words, 6 questions, 31 sources; review applied |
| `secrets-manager-and-parameter-store.md` | S | G | done | 2999 body words, 6 questions, 21 sources; review applied |
| `cognito.md` | M | F | done | 4982 body words, 8 questions, 28 sources; review applied |
| `directory-service.md` | S | G | done | 2812 body words, 6 questions, 27 sources; independent review applied. Restored five service rows a prior audit had wrongly deleted. |
| `waf-shield-firewall-manager-and-network-firewall.md` | M | F | done | 4905 body words, 8 questions, 37 sources; review applied and trimmed into tier. |
| `detection-and-compliance-services.md` | M | F | done | 4723 body words, 8 questions, 37 sources. Two reviews plus a dedicated quiz pass. Sources over the tier ceiling of 25, audited per citation and judged scope-driven for a ten-service unit. |

### 08-management

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `aws-api-cli-and-sdks.md` | L | E | done | Reviewed 2026-09-12, FIX THEN PASS, 27 facts verified. Two blocking errors: EC2 throttling described as one account-wide bucket when it is per-API with the console bucketed separately, which invalidated a question premise; and an opt-in 2026 SDK retry behavior taught as the current default. 9 should-fix applied, including a question that duplicated one in iam.md. Folds in `api/` and `cli/` |
| `cloudformation.md` | L | D | done | Reviewed 2026-09-12, FIX THEN PASS, 23 facts verified. One blocking error: a quiz key required rollback triggers on a StackSet operation, which CloudFormation does not support; question rewritten as multiple choice. 5 should-fix applied. Reviewer verified 3 of the 8 claimed corrections to the folded notes and could not itemize the rest |
| `cloudwatch.md` | L | D | done | Reviewed 2026-09-12, FIX THEN PASS, 29 facts verified, all 10 keys agreed. One blocking coverage gap: SAP 3.3-S2 on testing a remediation had a single clause; a full passage added. 11 should-fix applied. Body runs 4.5 percent over the L ceiling, within the review spec tolerance, because the coverage gap required new material |
| `cloudtrail.md` | M | F | done | 4693 body words, 8 questions, 27 sources. Two reviews; the second returned FIX THEN PASS with no blocking finding and verified 33 claims. Sources at 27 over the tier ceiling of 25, judged justified. |
| `systems-manager.md` | M | F | done | 4689 body words, 8 questions, 25 sources; body reworked and reviewed, quiz distractors fixed and rekeyed. |
| `service-catalog.md` | S | G | todo | Verify Proton status |
| `config-trusted-advisor-health-and-well-architected.md` | XS group | H | todo | |
| `cost-management.md` | L | E | done | Reviewed 2026-09-12, FIX THEN PASS, no blocking findings, 22 facts verified, all 10 keys agreed. 5 should-fix applied. Reviewer confirmed the same-zone data transfer citation the coordinator added |
| `developer-tools-and-cicd.md` | M | F | checked | Committed draft, unreviewed; 3512 body words, 8 questions, 25 fetched AWS sources; check passes with one planned-link warning and all source URLs return success. Explicitly SAP-only. CodeCommit is closed to new customers, CodeGuru Reviewer accepts no new repository associations, and Proton ends support 2026-10-07. Still requires an independent cold review. |

### 09-analytics

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `kinesis.md` | M | F | done | 3718 body words, 8 questions, 25 sources; stems rewritten and review applied. |
| `msk.md` | S | G | todo | |
| `glue.md` | M | F | todo | A writer claimed this row on 2026-09-12 and was stopped before writing anything. No file exists. Verify Glue for Ray status. |
| `athena.md` | S | G | todo | |
| `lake-formation.md` | S | G | todo | |
| `emr.md` | S | G | todo | |
| `opensearch.md` | S | G | todo | |
| `data-exchange-and-quick.md` | XS group | H | todo | Verify the Amazon Quick name |

### 10-migration

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `migration-hub-discovery-and-strategy.md` | M | F | todo | |
| `dms-and-sct.md` | S | G | todo | |
| `application-migration-service.md` | S | G | todo | |

### 11-ml-and-media

| File | Tier | Batch | Status | Notes |
|---|---|---|---|---|
| `ml-managed-services.md` | M | F | done | Reviewed 2026-09-12, FIX THEN PASS, 26 facts verified, all 8 keys agreed, all 7 service status claims confirmed. One blocking error: cross-account SageMaker AI invocation described with a resource policy, which SageMaker AI does not support. 5 should-fix applied. Body runs 1.7 percent over tier, within tolerance |
| `ai-dev-tools-and-generative-ai.md` | S | G | done | Reviewed 2026-09-12, FIX THEN PASS, 22 facts verified, all 6 keys agreed, framing judged correct. One blocking error: a quiz rationale said an SCP cannot name a specific guardrail, but bedrock:GuardrailIdentifier can. 5 should-fix applied. Folds part of `ai/README.md`; the rest belongs to ml-managed-services.md, so the notes stay until that lands |
| `media-iot-and-device-farm.md` | XS group | H | todo | |

## Phase 3: fold-in cleanup

Delete each notes file only after the unit that absorbs it is `done`.

| Notes file | Absorbed by | Status |
|---|---|---|
| `s3/README.md` | `services/01-storage/s3.md` | done | 
| `api/README.md` | `services/08-management/aws-api-cli-and-sdks.md` and `services/07-security/iam.md` | done | 
| `api/API_request.md` | same | done | 
| `cli/README.md` | same | done | 
| `iac/README.md` | `services/08-management/cloudformation.md` | done | 
| `ai/README.md` | `services/11-ml-and-media/ai-dev-tools-and-generative-ai.md` and `services/11-ml-and-media/ml-managed-services.md` | done | 

## Phase 4: exam domain guides

| File | Status | Notes |
|---|---|---|
| `domains/README.md` | todo | |
| `domains/saa-c03/01-design-secure-architectures.md` | todo | |
| `domains/saa-c03/02-design-resilient-architectures.md` | todo | |
| `domains/saa-c03/03-design-high-performing-architectures.md` | todo | |
| `domains/saa-c03/04-design-cost-optimized-architectures.md` | todo | |
| `domains/sap-c02/01-organizational-complexity.md` | todo | |
| `domains/sap-c02/02-new-solutions.md` | todo | |
| `domains/sap-c02/03-continuous-improvement.md` | todo | |
| `domains/sap-c02/04-migration-and-modernization.md` | todo | |

## Phase 5: appendix

| File | Status | Notes |
|---|---|---|
| `appendix/glossary.md` | todo | |
| `appendix/decision-tables.md` | todo | |
| `appendix/README.md` | todo | Currently a stub, rewrite when the two files above exist |

## Phase 6: final pass

| Check | Status | Notes |
|---|---|---|
| `bash aws/solutions-architect/_build/check.sh` passes on every file | todo | |
| Every owner in the phase 0 matrix actually teaches its bullets | todo | Verify, do not build. The matrix exists from phase 0 |
| Every in-scope service from both guides taught somewhere | todo | |
| All internal links resolve | todo | |
| No duplicated teaching across units, cross-links used instead | todo | |
| Track README, `services/README.md`, `domains/README.md`, `appendix/README.md` describe what exists | todo | |

## Log

Append one line per working session: date, what was completed, what broke.

- 2026-09-12: S3 unit reviewed and passed, first unit done. Review found no
  blocking errors in 28 fact checks and agreed with all 12 quiz keys. It caught
  four corrections the writer had already made to the old notes, including the
  max object size, which AWS raised from 5 TB to 50 TB. Seven should-fix items
  applied: request styles, CLI examples, append on directory buckets,
  If-None-Match conditional writes, archived objects not replicated, and two
  source citations. VPC unit started.
- 2026-09-11: Planning documents written to `_build/`. Folder renamed to
  `solutions-architect`, parent READMEs updated, exam guides captured, QA script
  written and smoke tested. No content units written yet. A first attempt at 16
  concurrent writer agents failed entirely on an account rate limit, which is why
  `HANDOFF.md` caps concurrency at three.
- 2026-09-11: Phase 0 coverage matrix completed. All 379 SAA-C03, SAP-C02 and
  SAP emerging-topic Knowledge and Skills bullets have exactly one owning unit.
  Independent review corrected nine weak owners, strengthened supporting-unit
  mappings and raised the disaster recovery reference unit from M to L.
- 2026-09-11: Phase 1 completed. All 11 category indexes are 250 to 500 words,
  pass the checker and include every planned unit. Independent review found nine
  blocking wording or coverage-map issues across seven files; all were fixed.
