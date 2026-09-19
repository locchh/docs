# Review spec

Every content file gets an independent review before it counts as done. The
reviewer is a different agent from the writer and reads the file cold.

## Dispatch prompt

Give the reviewer exactly this, with the placeholders filled:

> You are reviewing one unit of an AWS Solutions Architect course. You did not
> write it. Be skeptical.
>
> Read, in full: `aws/solutions-architect/_build/STYLE_SPEC.md`, the row for
> **`<category>/<file>`** in `aws/solutions-architect/_build/UNIT_PLAN.md`,
> `aws/solutions-architect/_build/REVIEW_SPEC.md`, and the rows naming this unit
> as owner in `aws/solutions-architect/services/README.md`. Then read the unit
> under review: `aws/solutions-architect/services/<category>/<file>`.
>
> Apply the review procedure in the review spec. Verify at least twelve factual
> claims against official AWS documentation by fetching the pages yourself, and
> weight your sampling toward numbers, limits, service status claims and anything
> that decides a quiz answer. Independently solve every quiz question before
> reading its answer, and report any question where you disagree with the key or
> where you can defend a second option.
>
> Report findings in the format the review spec requires. Do not edit the file.

The reviewer reports. The coordinator or the original writer applies fixes. A
reviewer that edits the file it is reviewing loses the independence that makes
the review worth doing.

## Review procedure

Work through these in order and take notes as you go.

### 1. Mechanical conformance

Run `bash aws/solutions-architect/_build/check.sh <file> <TIER>` from the
repository root and read its output. The tier argument makes the script check the
body word count for you. Then check what the script cannot:

- Top-level sections are exactly those in the style spec, in order, none missing,
  none added. For a domain guide, the sections are those in the domain guide
  template at the end of `UNIT_PLAN.md`.
- Topic section count matches the tier.
- No `###` headings inside topic sections, except in XS group files.

### 2. Coverage against the plan

Every service and topic named in the unit's `UNIT_PLAN.md` row is actually
taught, not merely mentioned in passing. List any that are missing or that get
less than a sentence. This is the most common real failure.

### 3. Coverage against the exam guides

Open `aws/solutions-architect/services/README.md`, the coverage matrix, and find
the rows where this unit is the owner. Every bullet it owns must be taught well
enough that a reader could answer an exam question on it. A passing mention is
not coverage. List every owned bullet that is thin or absent.

Then read the task statements the unit claims in its opening paragraph and flag
any it does not really serve.

### 4. Fact check

Fetch official AWS documentation and verify at least twelve claims. Choose them
by risk, not at random:

- Every hard number: limits, sizes, durations, IOPS, throughput ceilings,
  retention periods, quota values.
- Every service status claim: deprecated, closed to new customers, end of
  support, renamed, generally available.
- Every claim that decides a quiz answer.
- Anything that contradicts your own knowledge.

For each, record the claim, the page you checked, and whether it holds.

Watch for the failure mode where a writer states a plausible number it never
verified. If a number has no matching page in the unit's Sources list, treat it
as suspect.

### 5. Quiz audit

For every question:

- Solve it yourself before reading the answer.
- Confirm exactly one option is defensible for a multiple choice question, and
  that the stated count is right for a multiple response question.
- Confirm the rationale dismisses every other option by letter, and that each
  dismissal is accurate rather than hand-waved.
- Confirm the "Where this is covered" line names a real section in this unit.
- Confirm the Associate or Professional label fits the question's difficulty.
- Confirm the question is original rather than a lightly reworded classic from a
  well-known practice set.

Check the set as a whole: count matches the tier, at least a quarter multiple
response, roughly two thirds Associate, and keys spread across letters rather
than clustered. Read the "key spread, multiple choice only" line from
`check.sh`, not the aggregate: multiple response keys pad the totals and can hide
a unit whose single-answer keys are all B and C.

### 6. Two-reader test

- Could a reader who has never used this service answer the Associate questions
  using only this unit? Name anything assumed but never defined.
- Is every AWS service bolded and defined at first mention?
- Does anything the Associate exam tests live only inside a Professional depth
  section? That is a blocking error.
- Does the Professional depth section actually add Professional-level material,
  or does it restate the body at greater length?

### 7. Prose and links

- Em dash, U+2014, anywhere: blocking. The en dash, U+2013, in an official exam
  name is correct and must not be flagged.
- Emoji, exclamation marks, marketing adjectives, first-person asides.
- US spelling.
- Every table has a lead-in sentence saying what to read from it.
- Every `Related units` link resolves to a file listed in the unit plan, with a
  correct relative path.
- Every `Sources` entry is on an allowed host and is a real page. Spot-check at
  least three by fetching them.

## Severity

Classify every finding.

**Blocking.** The unit cannot be marked done. Any of: a wrong fact, an
unverifiable number, a wrong or ambiguous quiz key, a missing service from the
plan row, an owned coverage matrix bullet that is absent, a missing or
out-of-order section, an em dash, a broken link, an Associate topic hidden in
Professional depth, a fabricated source.

**Should fix.** Real but not disqualifying: thin coverage of a listed topic, a
weak distractor, keys clustered on one letter, a missing table lead-in, body word
count outside the tier range by less than fifteen percent.

**Optional.** Style preferences and suggestions.

## Report format

Report in under 600 words.

```
VERDICT: PASS | FIX THEN PASS | REWRITE

Blocking findings
1. <section>: <what is wrong> -> <what it should be, with the source URL if factual>
...

Should fix
1. ...

Optional
1. ...

Fact checks performed
| Claim | Source checked | Holds |
|---|---|---|
... at least twelve rows ...

Quiz audit
Questions solved independently: N of N. Disagreements: <list, or none>.
Counts: total N, multiple response N, Associate N, Professional N, key spread A/B/C/D.

Coverage
Plan row items missing: <list, or none>.
Owned matrix bullets thin or absent: <list, or none>.
```

`PASS` means done. `FIX THEN PASS` means the findings are mechanical and the unit
is done once they are applied, with no second review needed. `REWRITE` means send
it back to the writer and review again from the top.

## After the review

The coordinator applies blocking and should-fix findings, then updates the unit's
row in `PROGRESS.md`. A `REWRITE` verdict means the loop runs again: fix, then a
fresh review.

Optional findings are recorded in `PROGRESS.md` notes and not necessarily
applied.
