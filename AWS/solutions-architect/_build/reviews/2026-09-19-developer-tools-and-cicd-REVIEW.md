# Independent review: developer-tools-and-cicd.md, 2026-09-19

Reviewer: independent agent, read the unit cold, did not edit it. Coordinator
applied the findings. This is the review that REVIEW_SPEC.md requires; the
earlier `2026-09-19-developer-tools-and-cicd.md` in this folder is the editing
agent's own record and is not a review.

VERDICT: FIX THEN PASS. No blocking findings.

## Findings and disposition

| # | Severity | Finding | Applied |
|---|---|---|---|
| 1 | Should fix | Network Load Balancer and Application Load Balancer defined but not bolded at first mention | Yes, both bolded |
| 2 | Should fix | Amazon EC2 Auto Scaling used twice, never bolded or defined | Yes, bolded and defined at first use |
| 3 | Should fix | Q3 labeled Professional but single-service recall; options A, B and D eliminable without the stem | Yes, stem gained a "no repository servers" requirement; A and D replaced by an S3-as-Maven-repo near-miss and a no-shared-domain CodeArtifact topology; rationale rewritten |
| 4 | Should fix | Weak distractors: Q1 option C (CodeGuru Profiler) and Q6 option D (a Lambda canary for a Beanstalk EC2 environment) are cross-service non-sequiturs | Yes, Q1 C became a single-buildspec CodeBuild near-miss; Q6 D became plain Rolling, which differs from the key by exactly the capacity requirement |
| 5 | Optional | Lambda AppSpec hooks named "pre-traffic and post-traffic" rather than `BeforeAllowTraffic` and `AfterAllowTraffic` | Yes, actual hook names used |
| 6 | Optional | 26 sources against a tier M ceiling of 25 | Not applied; permitted overage, the extra ECS controller reference is load-bearing |
| 7 | Optional | QUEUED execution mode requires pipeline type V2, unstated | Not applied; below the exam's resolution |
| 8 | Optional | Q4's B+E pair is close to one design | Not applied; reviewer agreed option D keeps the choice load-bearing |

No quiz key changed. Keys remain 1 B, 2 A+D, 3 C, 4 B+E, 5 D, 6 A, 7 A+E, 8 B+D.

## Verification

The reviewer fetched fifteen official pages and confirmed every high-risk claim,
including all six the editing agent flagged: the CodeDeploy ECS NLB all-at-once
restriction, blue/green being EC2-only with on-premises excluded, the native ECS
controller's four strategies, the AWS recommendation of native ECS blue/green,
automatic stage retry being incompatible with on-failure conditions, and
Profiler heap visualization being JVM-only. All 26 source URLs return 200.

The coordinator separately confirmed the CodeCommit reversal: the CodeCommit
documentation history records "AWS CodeCommit is now available to new customers"
dated November 25, 2025, and the welcome page carries no restriction banner.

Quiz: solved 8 of 8 independently before reading the keys, no disagreements, no
second defensible option on any item.

Post-fix mechanical check: 0 errors, body 3,888 words, one planned-link warning
for the unwritten `elastic-beanstalk.md`.

## Limit of this review

The reviewer solved the quiz as it stood before the fixes. The replacement
options in Q1, Q3 and Q6 were written by the coordinator afterwards and have not
been independently solved by anyone. No key changed, and Q3's and Q6's new
options were each built to differ from the key by exactly one stated
requirement, but a future pass over this unit should treat those three questions
as coordinator-written rather than review-confirmed.
