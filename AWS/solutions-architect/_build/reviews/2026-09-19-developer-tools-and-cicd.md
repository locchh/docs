# Developer tools and CI/CD correction pass, 2026-09-19

Status: corrected and mechanically checked; independent review still required.
This is the editing agent's evidence record, not an independent PASS under
REVIEW_SPEC.md. No commit was created.

## Findings applied

- Replaced the obsolete CodeCommit new-customer restriction throughout the unit
  and Q7. The documentation history records reopening in November 2025; older
  pricing banners conflict with that newer, dated service history.
- Distinguished native ECS deployment strategies from the CodeDeploy controller.
  Constrained the worked scenario to an existing CodeDeploy workflow and an
  Application Load Balancer; documented the CodeDeploy NLB all-at-once limit.
- Distinguished EC2 load-balancer registration from ECS target-group switching;
  noted that CodeDeploy blue/green does not support on-premises targets.
- Separated CodePipeline stage conditions from automatic retry.
- Clarified secret storage versus runtime injection, and why private AWS
  endpoints do not reach required public package hosts in Q2.
- Added upgrade-path reasoning, clarified Profiler's JVM-only heap visualization,
  defined missing terms, and improved Q4/Q7/Q8 distractors.
- Clarified that Associate quiz labels indicate difficulty in this SAP-only unit.

## Documentation checks

The original 25 Sources URLs were fetched successfully. Their documentation
Markdown was read for the claims below. Two added/replacement documentation pages
were fetched as well. The final unit has 26 sources: the extra ECS controller
reference is necessary to distinguish native deployment from CodeDeploy.

| Claim | Official page (relative to `https://docs.aws.amazon.com/`) | Result |
|---|---|---|
| CodeCommit accepts new customers | `codecommit/latest/userguide/history.html` | Corrected |
| Stage-condition result types; retry conflict | `codepipeline/latest/userguide/stage-conditions.html` | Corrected |
| Pipeline stages/actions/artifacts | `codepipeline/latest/userguide/concepts.html` | Confirmed |
| Cross-account roles, bucket and KMS access | `codepipeline/latest/userguide/pipelines-create-cross-account.html` | Confirmed |
| Buildspec secret mappings | `codebuild/latest/userguide/build-spec-ref.html` | Confirmed; Q2 clarified |
| VPC builds lack public IPs and need public egress | `codebuild/latest/userguide/vpc-support.html` | Confirmed |
| EC2-only blue/green; on-premises in-place | `codedeploy/latest/userguide/welcome.html` | Clarified |
| EC2 registration versus ECS target groups | `codedeploy/latest/userguide/deployment-groups.html` | Corrected |
| AppSpec differs by compute platform | `codedeploy/latest/userguide/reference-appspec-file.html` | Confirmed |
| Canary/linear; NLB all-at-once restriction | `codedeploy/latest/userguide/deployment-configurations.html` | Clarified |
| Native ECS rolling/blue-green/canary/linear | `AmazonECS/latest/developerguide/ecs_service-options.html` | Corrected |
| AWS recommends native ECS blue/green | `AmazonECS/latest/developerguide/deployment-type-bluegreen.html` | Added |
| Package upstreams and external connections | `codeartifact/latest/ug/repos-upstream.html` | Confirmed |
| No new Reviewer associations from 2025-11-07 | `codeguru/latest/reviewer-ug/codeguru-reviewer-availability-change.html` | Confirmed |
| Profiler heap visualization excludes Python | `codeguru/latest/profiler-ug/what-is-codeguru-profiler.html` | Clarified |
| Proton ends 2026-10-07; stacks survive | `proton/latest/userguide/proton-end-of-support.html` | Confirmed |
| Beanstalk additional batch versus immutable | `elasticbeanstalk/latest/dg/using-features.deploy-existing-version.html` | Confirmed; EC2 context explicit |
| Rollback does not undo script side effects | `codedeploy/latest/userguide/deployments-rollback-and-redeploy.html` | Confirmed |

## Quiz and coverage

Editing-pass keys: 1 B; 2 A/D; 3 C; 4 B/E; 5 D; 6 A; 7 A/E; 8 B/D.
Eight questions, four multiple response, five foundational and three Professional.
Single-answer keys span A/B/C/D. This was not a blind independent quiz audit.

All plan-row services remain covered. Owned SAP bullets map to:

| Bullet | Teaching section |
|---|---|
| 2.1-K2: CI/CD | Build a pipeline from immutable artifacts |
| 2.1-S1: application/upgrade path | Select a deployment strategy and rollback |
| 2.1-S2: deployment and rollback services | Deploy to EC2 and on-premises instances; Shift Lambda and ECS traffic |
| 3.1-K4: pipelines/deployment strategies | Select a deployment strategy and rollback |
| 3.1-S2: improve deployment processes | Professional depth |

## Remaining gate

A separate reviewer must check the revised body and all eight questions before
this unit becomes done. The planned link to `elastic-beanstalk.md` remains a
warning because that unit has not been authored. Whole-course completion is not
claimed.
