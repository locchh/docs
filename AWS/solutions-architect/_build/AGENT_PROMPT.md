# Starting prompt for a fresh agent

Paste the block below into Codex, a new Claude Code session, or any other coding
agent to continue this project. It is deliberately short: everything else lives
in `HANDOFF.md`, which the prompt tells the agent to read first.

---

```
Continue building the AWS Solutions Architect course in this repository.

Repo: /home/locch/Works/certex
Course: aws/solutions-architect/

Read these three files before doing anything else, in this order:
  aws/solutions-architect/_build/HANDOFF.md    mission, phases, execution loop
  aws/solutions-architect/_build/PROGRESS.md   what is done, what is next
  aws/solutions-architect/_build/UNIT_PLAN.md  every file, its services, its tier

HANDOFF.md is the specification. Follow it rather than re-planning. The
structure, the depth tiers and the phase order were already decided and approved.
If something in the plan looks wrong, say so before changing it.

Pick up at the first row in PROGRESS.md that is not `done`, working phases in
order. Mark a row `writing` with today's date before you start it and update the
row when you finish, so a second agent does not duplicate your work.

For every content file, run this loop:

  1. Write it. The authoring contract is _build/STYLE_SPEC.md. Read it in full,
     plus the two exemplar units it names. Verify every fact, number and service
     status against official AWS documentation by fetching the page. Do not write
     a number you did not read. State facts as of September 2026: AWS renamed and
     retired a lot recently, and STYLE_SPEC.md lists the specific items to check
     rather than assume. Target the middle of the assigned tier's body-word range,
     not its ceiling, so review findings can be added without a destructive trim.

     Fetching: do NOT rely on WebFetch. It returns a composed summary instead of
     the page for many AWS docs URLs, which cost five writers real facts before
     the cause was found. Use curl and extract the text locally, or the Tavily
     extract tool, or append .md to a docs URL. Some pricing pages render their
     rate tables in JavaScript and cannot be read at all; describe the charge
     shape instead of quoting a rate.

  2. Check it:
       bash aws/solutions-architect/_build/check.sh <path> <TIER>
     Fix everything it reports before moving on.

  3. Review it. The contract is _build/REVIEW_SPEC.md, including the dispatch
     prompt to use. The review must be independent: a subagent if you can spawn
     one, otherwise a separate pass that reads the file cold against the spec.
     The reviewer fact-checks at least twelve claims against AWS docs and solves
     every quiz question before reading its key. Do not skip this step. A unit is
     not done until a review passes it.

  4. Apply the findings, update PROGRESS.md, and commit:
       docs(sa): add <service> unit to the solutions architect course
     Commit per unit or small batch, never one large commit at the end.

Constraints that matter:
  - Run at most 3 writer agents at once, 1 for an XL unit. A larger batch has
    already been lost entirely to an API rate limit.
  - No em dash, U+2014, in course content. The en dash, U+2013, in
    "Solutions Architect - Associate" is correct and stays.
  - Every unit teaches the Associate exam in its body and the Professional exam
    in a Professional depth section the Associate reader can skip. Nothing the
    Associate exam tests may live only in that section.
  - Quizzes are original, written from the exam guides, never copied from a
    practice exam.

Report progress as you go: which file, its word count, what the review found.
```

---

## If the agent has no web access

The fact-verification step is the core of the quality bar, so an agent that
cannot fetch `docs.aws.amazon.com` should not write units. Give it one of the
non-research tasks instead: the category READMEs in phase 1, or the final link
and structure pass in phase 6.

## If you want it to do just one unit

Append to the prompt:

```
Do only this one file, then stop and report: aws/solutions-architect/services/<category>/<file>
```

That is the safest way to try a new agent on this project. Check the result
against STYLE_SPEC.md yourself before letting it loose on a batch.
