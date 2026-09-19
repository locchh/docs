# Independent review: glue.md, 2026-09-19

Two agents were used. The first applied REVIEW_SPEC.md in full but disclosed
that its opening action had been a whole-file `cat`, which put every answer fold
in front of it before it could solve anything, so its quiz verdict was a
re-derivation rather than a blind solve. A second agent was therefore dispatched
with an extraction procedure that strips the folds before reading, to supply the
blind quiz audit the spec requires. Neither agent edited the file.

VERDICT: FIX THEN PASS. No blocking findings from either pass.

## Reviewer 1, content and coverage

| # | Finding | Applied |
|---|---|---|
| 1 | The pricing section named no billable dimension at all and defined a DPU only as "provisioned processing capacity" | Yes. DPU defined as 4 vCPUs and 16 GB; per-second billing, ten-minute crawler minimum, one-minute job minimum on Glue 2.0 and later, Spark default 10 DPUs with a floor of 2, Python shell at 1 or 0.0625 DPU, first million catalog objects and requests free |
| 2 | "Eligible" and "supported" were load-bearing hedges that the reader was never able to cash. The Exam lens bullet on Flex and the Q8 key both turn on them | Yes. Flex and Auto Scaling eligibility now stated explicitly |
| 3 | No quota anywhere in the body or Professional depth | Yes. 100 jobs, crawlers and triggers per workflow; at most two crawlers per trigger; 900-second EventBridge batch window |
| 4 | The opening claimed SAP-C02 task 2.1, which nothing in the unit serves | Yes, claim dropped; 3.2 and 4.4 retained |
| 5 | Q8 options B and D, and Q3 option B, were misconceptions or attitudes rather than alternative solutions | Yes, all rewritten as actions a competent engineer might propose |

Optional findings on the `push_down_predicate` sequencing, the `DynamicFrame`
and DPU bolding, the one-sided Q6 rationale and the thin Glue Studio paragraph
were recorded and not applied.

Nineteen official pages fetched; every sampled claim held, including the Ray
new-customer closure of April 30 2026, Python shell and streaming jobs having no
bookmark support, streaming checkpoints, bookmark reset not deleting target
files, workflow concurrency rejections not being retried, and Glue ENIs having
no public address.

## Reviewer 2, blind quiz audit

Solved 8 of 8 with the answer folds stripped, writing its answers to disk before
opening the key. Agreement on all eight: 1 B, 2 C, 3 A+E, 4 A, 5 D, 6 B+D,
7 C, 8 A+E. No disagreement. The closest call is Q8 option C, a quota increase,
which is a real engineering response and fails only on the stem's recovery
requirement; it remains correctly keyed.

It also re-verified all nine facts added under reviewer 1's findings against
official documentation. All nine hold. Two were worded imprecisely and were
corrected:

- Flex's allow-list is G.1X and G.2X only, so G.4X and G.8X are ineligible too.
  The text had named only G.12X, G.16X and the R-series as excluded, inviting
  the inference that G.4X and G.8X qualify. The unit now states the allow-list
  positively and lists every excluded type.
- Auto Scaling does include G.025X, restricted to streaming. The text had placed
  it outside the supported list. Corrected.

Its remaining finding, that Q3 options C and D were still eliminable without
reasoning, was applied: C is now a hand-rolled 24-hour last-modified window and
D is the classic over-extension of bookmarks to output deduplication, which is
the misconception the section exists to correct.

Post-fix mechanical check: 0 errors, body within tier M, 25 sources, three
planned-link warnings for the unwritten Athena, Lake Formation and EMR units.

## Limit of this review

The blind audit solved Q3 in its pre-fix form. Its own finding that Q3 options C
and D were eliminable without reasoning was applied after it reported, so the
current C and D are coordinator-written and have not been independently solved.
The key is unchanged at A and E. Option D, "Depend on job bookmarks alone to
keep the published dataset free of duplicate records", still signals itself
somewhat through the word "alone"; it is a real misconception rather than an
attitude, but it is not claimed here to be a fully plausible-shaped distractor.
Q1 option D and Q4 option D were also flagged as implausible rather than
misconception-shaped and were left unchanged.
