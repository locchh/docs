# Labs

Hands-on exercises to run against a real AWS account. The service units teach
what a service does and how the exam asks about it; these labs put your hands on
the API so the behavior stops being abstract.

Neither exam is hands-on, so no lab is required to pass. They exist because a
reader who has actually watched a multipart upload complete, or seen a CORS
preflight fail, answers those questions faster and with more confidence.

## Before you start

Every lab assumes the AWS CLI v2 is installed and configured, and that you are
signed in with credentials that can create and delete the resources involved.
Prefer a sandbox account. Prefer temporary credentials from IAM Identity Center
over long-lived access keys, for the reasons the
[API, CLI and SDKs unit](../services/08-management/aws-api-cli-and-sdks.md)
explains.

Each lab creates real resources that cost real money. Every one ends with a
cleanup step. Run it.

## Amazon S3

These five build on each other and are best run in order. Together they exercise
most of what the
[Amazon S3 unit](../services/01-storage/s3.md) teaches.

| Lab | What you do | What it makes concrete |
|---|---|---|
| [01 CLI common operations](s3/01-cli-common-operations.md) | Create buckets, copy, move, sync and remove objects with `aws s3` and `aws s3api` | The difference between the high-level `s3` commands and the one-to-one `s3api` mapping onto the REST API |
| [02 Bash scripting](s3/02-bash-scripting.md) | Drive S3 from a shell script, including generated files and bulk operations | How `--query` and `--output` turn API responses into something a script can consume |
| [03 PowerShell scripting](s3/03-powershell-scripting.md) | The same ground using the AWS Tools for PowerShell | That the API is the product and the language binding is just a client |
| [04 Additional checksums](s3/04-additional-checksums.md) | Upload with CRC32, CRC32C, SHA-1 and SHA-256 checksums and read them back | How S3 verifies integrity on upload, and why a multipart object's ETag is not a hash of its contents |
| [05 CORS](s3/05-cors.md) | Configure a bucket CORS policy and watch a browser preflight succeed and fail | That CORS is enforced by the browser against rules held on the bucket, which is exactly the exam's framing |

## Suggested additions

The course does not yet have labs for the areas where hands-on time pays the
most beyond S3. In rough order of value: a VPC built by hand with public and
private subnets and a NAT gateway, so the routing stops being theoretical; an
IAM exercise in assuming a role across two accounts with an external ID; and a
CloudFormation stack taken through a change set, a drift, and a deliberate
rollback. Each maps onto a unit that already exists.
