# Management and governance

This category builds, watches, controls and pays for everything in the other
ten. **AWS CloudFormation** declares infrastructure as code, so a stack can be
rebuilt or rolled back. **Amazon CloudWatch** collects the metrics, logs and
alarms that tell you a system is healthy. **AWS CloudTrail** records who called
which API. **AWS Systems Manager** patches, configures and runs commands on
fleets without opening SSH. **AWS Config** records resource configuration and
evaluates it against rules. The cost tools turn all of it into a bill you can
explain.

The decision the category keeps asking you to make is whether the answer
detects, prevents, or corrects. Detection is CloudWatch, CloudTrail, Config and
**AWS Trusted Advisor**, which checks an account against best practices: they
report a problem after it is true. Prevention comes from **AWS Service Catalog**
constraints, CloudFormation Hooks and policy guardrails: the wrong thing cannot
be created. Correction is Systems
Manager Automation, Config remediation and event-triggered functions: the wrong
thing is fixed without a human. An exam question asking for "no manual
intervention" wants correction, and one asking to "ensure compliance" usually
wants prevention.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [aws-api-cli-and-sdks.md](aws-api-cli-and-sdks.md) | Sign and send API requests, use profiles and temporary credentials, and reason about retries and quotas | L |
| [cloudformation.md](cloudformation.md) | Write and update templates, use StackSets and nested stacks, and control deletion and drift | L |
| [cloudwatch.md](cloudwatch.md) | Design metrics, alarms, logs and traces, including across accounts | L |
| [cloudtrail.md](cloudtrail.md) | Set up organization trails and query events for an audit answer | M |
| [systems-manager.md](systems-manager.md) | Patch, configure and access fleets, and automate a runbook | M |
| [service-catalog.md](service-catalog.md) | Publish approved products with launch constraints | S |
| [config-trusted-advisor-health-and-well-architected.md](config-trusted-advisor-health-and-well-architected.md) | Record configuration, read advisory findings, and track quotas and events | XS group |
| [cost-management.md](cost-management.md) | Attribute, forecast and reduce spend, including data transfer charges | L |
| [developer-tools-and-cicd.md](developer-tools-and-cicd.md) | Build a pipeline and choose a deployment strategy with a rollback path | M |

## Which exam tasks this serves

On SAA-C03 it is task 2.2 for automation, workload visibility and service
quotas, and all four tasks of domain 4, where the cost management tools are
named in each. On SAP-C02 it is tasks 1.5, 2.6 and 3.5 for cost, 2.1 and 3.1 for
deployment and operational excellence, 3.2 for patching and automated
remediation, and 3.3 for monitoring.

## Reading order

Read `cloudwatch.md`, then `cloudtrail.md`, then `cloudformation.md`. Those
three appear in scenarios throughout the course. Then `systems-manager.md`,
`service-catalog.md`, `cost-management.md`, which the domain guides reference, and
`config-trusted-advisor-health-and-well-architected.md`. An Associate-only
candidate should skip `developer-tools-and-cicd.md` entirely, since the SAA-C03
guide names its build, deployment and artifact services as out of scope, and can
read only the CLI and console half of `aws-api-cli-and-sdks.md`, because the
SDKs and the browser shell are out of scope too.
