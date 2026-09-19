# Handoff: revamp of the AWS Solutions Architect course

Read this file first. It is written so that any agent or person can execute the
project without the conversation that produced it. Everything needed is in this
`_build/` folder.

**Paths.** Every path in these documents is relative to the repository root, the
directory containing the top-level `README.md` and the `aws/` folder. The course
itself lives at `aws/solutions-architect/`. Run commands from the repository root
unless a command says otherwise.

| File | What it is |
|---|---|
| `HANDOFF.md` | This file: mission, current state, execution procedure, definition of done |
| `STYLE_SPEC.md` | The authoring contract every content file must satisfy |
| `REVIEW_SPEC.md` | The contract every review pass must apply |
| `UNIT_PLAN.md` | Every file to be written, its services, its depth tier |
| `exam-guide-saa-c03.md` | The Associate exam guide, captured from AWS docs, September 2026 |
| `exam-guide-sap-c02.md` | The Professional exam guide, captured from AWS docs, September 2026 |
| `PROGRESS.md` | The tracker. Update it after every unit. It is the source of truth for what is done |
| `check.sh` | Mechanical QA script. Run it on any file before calling that file done |
| `AGENT_PROMPT.md` | A copy-paste starting prompt for handing this project to a fresh agent |

## Mission

Replace the loose per-topic notes in `aws/solutions-architect/` with a complete,
self-contained course that prepares a reader for both AWS Solutions Architect
exams at once:

- **SAA-C03**, Solutions Architect Associate
- **SAP-C02**, Solutions Architect Professional

The course is organized **by service**, not by exam domain, because the reader is
working through service-by-service video courses and wants written material that
matches. Exam domain guides sit on top and map each exam's task statements back
to the service units.

Every unit teaches the Associate level in its body and the Professional level in
a clearly marked section the Associate reader can skip. Every unit ends with its
own quiz. Full practice exams are a separate artifact and are not part of this
work.

The finished course is modeled on an existing finished path in this repository:
`aws/aip-c01/learning-paths/`. Read two of its units before writing anything.
They define the voice, the density, the section order and the quiz format:

- `aws/aip-c01/learning-paths/04-operational-efficiency-optimization/03-monitoring-genai-applications.md`
- `aws/aip-c01/learning-paths/01-fm-integration-data-compliance/04-vector-stores.md`

## Scale

This is a large project. Plan for it.

| Measure | Estimate |
|---|---|
| Service units | 70 |
| Exam domain guides | 8, plus 1 index |
| Appendix files | 2, plus 1 index |
| Category README files | 11, plus 1 services index |
| Total content files | about 94 |
| Total words | about 340,000 |
| Total original quiz questions | about 660 |

## Current state

**PROGRESS.md is the live source of truth. Read it, not this section, for what
is finished.** This section describes the shape of the work; the tracker
describes its state.

As of the last commit: 45 of 106 files complete. The coverage matrix, all eleven
category indexes, the labs refactor and the notes cleanup are done. Service units
are being written in the batch order below, each one written by one agent and
then independently reviewed by another before it counts as done.

All five original notes folders are gone. Each was folded into the unit that owns
its material and deleted only after that unit passed review, so nothing was lost:

| Notes file | Folded into | Status |
|---|---|---|
| `s3/README.md` | `services/01-storage/s3.md` | deleted |
| `api/README.md`, `api/API_request.md`, `cli/README.md` | `services/08-management/aws-api-cli-and-sdks.md` and `services/07-security/iam.md` | deleted |
| `iac/README.md` | `services/08-management/cloudformation.md` | deleted |
| `ai/README.md` | `services/11-ml-and-media/ai-dev-tools-and-generative-ai.md` and `ml-managed-services.md` | deleted |

### Picking up mid-flight

A row marked `writing` with a date means an agent was working on that file when
the session ended. Check whether the file exists on disk before starting it
again. Twice in this project an agent was stopped or hit an API error after it
had already written the file, and once it had written everything except the quiz
and closing sections. Run `check.sh` on it first: a complete unit passes, a
half-written one reports missing sections and can be finished rather than
rewritten.

## Target structure

```
aws/solutions-architect/
  README.md                      track README, already written
  _build/                        this folder, planning only, not study material
  services/
    README.md                    coverage matrix: service -> unit -> SAA tasks -> SAP tasks
    01-storage/README.md         and 8 units
    02-compute/README.md         and 8 units
    03-containers/README.md      and 2 units
    04-networking/README.md      and 6 units
    05-database/README.md        and 8 units
    06-integration/README.md     and 6 units
    07-security/README.md        and 9 units
    08-management/README.md      and 9 units
    09-analytics/README.md       and 8 units
    10-migration/README.md       and 3 units
    11-ml-and-media/README.md    and 3 units
  domains/
    README.md
    saa-c03/01-design-secure-architectures.md
    saa-c03/02-design-resilient-architectures.md
    saa-c03/03-design-high-performing-architectures.md
    saa-c03/04-design-cost-optimized-architectures.md
    sap-c02/01-organizational-complexity.md
    sap-c02/02-new-solutions.md
    sap-c02/03-continuous-improvement.md
    sap-c02/04-migration-and-modernization.md
  appendix/
    README.md                    rewrite to match UNIT_PLAN
    glossary.md
    decision-tables.md
  labs/s3/                       existing hands-on labs, leave as is
```

`UNIT_PLAN.md` lists every unit file with its services and depth tier. It is
authoritative. If this file and `UNIT_PLAN.md` disagree on a filename, the plan
wins.

## Execution procedure

### Phase order

Work in this order. Later phases depend on earlier ones.

| Phase | What | Why this order |
|---|---|---|
| 0 | **The coverage matrix, `services/README.md`** | Do this first, before any unit is written. See below |
| 1 | Category READMEs, 11 files | Cheap, and they fix the cross-reference targets before units start linking to each other |
| 2 | Service units, 70 files, in the batch order below | The bulk of the work |
| 3 | Fold-in cleanup: delete `s3/`, `api/`, `cli/`, `iac/`, `ai/` once their units are reviewed and done | Cannot happen before the units that absorb them exist |
| 4 | Exam domain guides, 8 files, plus `domains/README.md` | They map task statements to units, so the units must exist and be final |
| 5 | Appendix: glossary and decision tables, plus the appendix README rewrite | Built from the finished units so every term is traceable |
| 6 | Final whole-course pass: link check, duplicate check, coverage verified against the phase 0 matrix | Last |

### Phase 0 in detail

The two exam guides contain roughly 350 "Knowledge of" and "Skills in" bullets
between them. The definition of done requires every one of them to be covered.
Deciding which unit owns which bullet **after** the units are written means
discovering gaps in work that is already reviewed and committed, and reopening it.
So assign ownership first.

Build `services/README.md` by walking both exam guides bullet by bullet and
assigning each bullet to exactly one owning unit, plus any number of supporting
units. Format:

```
| Exam | Task | Bullet | Owner | Also covered in |
|---|---|---|---|---|
| SAA-C03 | 1.1 | Designing a role-based access control strategy | 07-security/iam.md | |
| SAP-C02 | 4.2 | Selecting the appropriate database transfer mechanism | 10-migration/dms-and-sct.md | 05-database/rds.md |
```

Then add a second table, one row per unit, listing the bullets it owns. That
table is what goes into each writer's dispatch prompt.

Two things fall out of this that are cheaper to learn now than later:

- Bullets no unit owns. Assign them to the nearest unit and record the addition
  in `UNIT_PLAN.md`, or create a unit. One is already known: SAP task 3.1's
  "engineering failure scenario activities" is assigned to
  `01-storage/backup-and-disaster-recovery.md` alongside disaster recovery
  testing, since AWS Fault Injection Service appears on neither in-scope list.
- Units that own very little, which means a tier is too high, or very much, which
  means a tier is too low or the unit should split.

Phase 6 then verifies the matrix rather than building it.

### Batch order within phase 2

Write the highest-traffic units first so that if the project stalls, what exists
is what the reader needs most. Within a batch the units are independent and can
run in parallel.

| Batch | Units |
|---|---|
| A | `01-storage/s3.md`, `04-networking/vpc.md` |
| B | `07-security/iam.md`, `02-compute/ec2.md`, `05-database/rds.md` |
| C | `05-database/dynamodb.md`, `02-compute/lambda.md`, `04-networking/api-gateway.md` |
| D | `08-management/cloudformation.md`, `08-management/cloudwatch.md`, `04-networking/route53.md` |
| E | `07-security/organizations-identity-center-and-control-tower.md`, `04-networking/hybrid-connectivity.md`, `08-management/cost-management.md`, `08-management/aws-api-cli-and-sdks.md` |
| F | remaining M-tier units, in category order |
| G | remaining S-tier units, in category order |
| H | the 6 XS-group units |

### Batch size

**Run at most 3 writer agents concurrently.** An XL or L unit does heavy
documentation fetching and long writes; four or more at once has already
exhausted the account rate limit and lost all work in flight. For XL units, run
one at a time.

Recommended concurrency by tier: XL, 1. L, 2. M, 3. S or XS, 3.

### The write and review loop

For each unit, repeat until the reviewer returns no blocking findings:

1. **Write.** Dispatch one writer agent. Its prompt must be exactly:

   > Read, in this order and in full:
   > `aws/solutions-architect/_build/STYLE_SPEC.md`, then `UNIT_PLAN.md`,
   > `exam-guide-saa-c03.md` and `exam-guide-sap-c02.md` in the same folder, then
   > the exemplar units the spec names.
   >
   > Assignment: write the unit in the `UNIT_PLAN.md` row **`<category>/<file>`**,
   > tier **`<TIER>`**, to `aws/solutions-architect/services/<category>/<file>`.
   > `<any fold-in instruction from the plan's Notes column>`
   >
   > This unit owns these exam guide bullets, and each must be taught well enough
   > that a reader could answer an exam question on it:
   > `<paste the unit's rows from the phase 0 coverage matrix>`
   >
   > Follow every rule in the spec, verify every fact against official AWS
   > documentation with web fetches, and report per the finish checklist. Target
   > the middle of the tier's body-word range, not its ceiling, so review fixes
   > can be added without forcing a destructive trim pass.

   For XL and L units add: *Write the file in several appends, one or two
   sections per write, rather than one enormous write.*

2. **Check mechanically.** Run `_build/check.sh <path>`. Fix anything it flags
   before spending a reviewer on the file.

3. **Review.** Dispatch one reviewer agent with the prompt in `REVIEW_SPEC.md`.
   The reviewer is a different agent from the writer and reads the unit cold.

4. **Fix.** Apply every blocking finding. Either send the findings back to the
   writer agent, which still holds its context, or fix directly for small edits.

5. **Record.** Update the row in `PROGRESS.md`. Commit.

A unit is not done until a reviewer has passed it. The user asked specifically
for subagent review of every piece of work, so do not skip step 3 even when the
unit looks clean.

### Committing

Commit after each unit or each small batch, never one giant commit at the end.
Message form:

```
docs(sa): add <service> unit to the solutions architect course
```

Attribution trailer for commits in this repository:

```
Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
```

## Definition of done

The project is complete when all of the following hold.

1. Every file in `UNIT_PLAN.md` exists, and `PROGRESS.md` shows it written,
   checked, reviewed and fixed.
2. `bash aws/solutions-architect/_build/check.sh` passes on every content file.
3. Every "Knowledge of" and "Skills in" bullet in both exam guides has an owner in
   the `services/README.md` matrix built in phase 0, and the final pass confirms
   that each owning unit actually teaches its bullets.
4. Every in-scope service in both exam guides is taught somewhere. Services
   in-scope for SAP but not SAA are taught with a note saying so, and the
   reverse.
5. Every internal link resolves. No unit links to a file that does not exist.
6. The six source notes files listed above are deleted, their content having been
   folded in.
7. The glossary contains every service and term the course uses, each with the
   unit that teaches it and an official documentation link.
8. `appendix/README.md`, `services/README.md` and `domains/README.md` describe
   the structure that actually exists.

## Constraints and gotchas already learned

- **Rate limits are the binding constraint.** Three concurrent writers maximum.
  A failed agent writes nothing, so a dead batch is pure loss.
- **Em dash, U+2014, is banned** in course content. The en dash, U+2013, is
  required in official exam names such as "Solutions Architect – Associate" and
  is fine. `check.sh` distinguishes them. Do not let a reviewer flag the en dash.
- **AWS renamed and retired a lot in 2024 to 2026.** Both exam guides still use
  older names in places. The spec lists the specific items to verify rather than
  assume. Teach the guide's name and the current name in one sentence.
- **The scratchpad is not durable.** Everything the project needs lives in this
  `_build/` folder inside the repository.
- **The AIP path is the model, not a source to copy from.** Its subject matter is
  generative AI and is irrelevant here. Copy its shape only.
- The reader's own course progress, which set the depth tiers, is recorded in
  `UNIT_PLAN.md` as the "Lesson signal" column. It is the number of lessons each
  service has in the Associate and Professional video courses the reader is
  taking. It is why S3, VPC, DynamoDB, API Gateway and CloudFormation are deep
  and Lightsail is a paragraph.
