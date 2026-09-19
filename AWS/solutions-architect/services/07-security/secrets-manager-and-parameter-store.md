# AWS Secrets Manager and AWS Systems Manager Parameter Store

**Where it sits on the exams.** **AWS Secrets Manager** is the managed store for credentials that have to change on a schedule, and **Parameter Store**, a capability of **AWS Systems Manager**, the operations service for fleet and configuration management, is the hierarchical store for configuration data whose standard tier costs nothing. On SAA-C03 the pair appears in task 1.2, "Design secure workloads and applications", which names Secrets Manager among the services used to secure an application, and in task 2.1, "Design scalable and loosely coupled architectures". On SAP-C02 they own the secrets management bullet in task 3.2, "Determine a strategy to improve security", which names both services in the same line, and the credential management services bullet in task 2.3, "Determine security controls based on requirements". Almost every question about them is a "which one" question, and the rule of thumb is one sentence: if the stem says a credential must rotate, must be granted to another account by policy, or must exist in more than one Region, the answer is Secrets Manager, and if it is configuration read at volume with "MOST cost-effectively" in the wording, the answer is a Parameter Store standard parameter.

## What each service stores and how it is encrypted

A secret in Secrets Manager is a named, always-encrypted object with a value of up to 65,536 bytes, a set of versions, and an optional resource policy. Secrets Manager encrypts it with a symmetric key in **AWS Key Management Service (AWS KMS)**, the service that creates and controls encryption keys: either the AWS managed key `aws/secretsmanager` or a customer managed key chosen at creation. An account holds up to 500,000 secrets per Region and a secret retains 100 versions.

A parameter is a named value in a slash-delimited hierarchy such as `/myapp/prod/database/host`, in one of three types. `String` holds plain text, `StringList` a comma-separated list, and `SecureString` a value that Parameter Store encrypts with a symmetric KMS key, either `aws/ssm` or a customer managed key. Only the value is encrypted: the name, description and other metadata stay in plaintext, which is why a secret must never be hinted at in a parameter name. Parameter Store charges nothing to create a `SecureString`, although the KMS requests are billed normally.

Parameter Store has two storage tiers, chosen per parameter, and this table is the one the exam tests directly. Read it for the value size, the per-account ceiling, whether parameter policies and cross-account sharing are available, and whether it costs anything.

| | Standard parameter | Advanced parameter |
|---|---|---|
| Maximum parameters per account and Region | 10,000 | 100,000 |
| Maximum value size | 4 KB | 8 KB |
| Parameter policies | Not supported | Supported |
| Shareable across AWS accounts | Not supported | Supported |
| Tier change | Upgradeable to advanced | Not downgradeable |
| Cost | No additional charge | Charges apply |

The upgrade is one way: demoting would truncate an 8 KB value to 4 KB and strip any attached policies, so to stop the charge you delete the parameter and recreate it as a standard one.

Parameter policies are the feature that most often forces the advanced tier. `Expiration` deletes the parameter at a date or after a duration you set. `ExpirationNotification` raises an event in **Amazon EventBridge**, the event bus that routes AWS and application events to targets, before that deletion. `NoChangeNotification` raises an event when a parameter has gone unmodified for a period, which is how an approved machine image identifier gets reviewed on a cadence.

Both services version their values, but the versioning means different things. Parameter Store keeps the 100 most recent versions of a parameter and drops the oldest to make room. Secrets Manager versions carry staging labels that a rotation state machine moves for you.

## Rotation: managed, by Lambda, and the staging labels

Rotation is the largest difference between the two services and the discriminator to reach for first. The current Parameter Store documentation states its position plainly: for credential rotation, Parameter Store offers "None", and AWS recommends Secrets Manager for database passwords, API keys and tokens.

Secrets Manager rotates in one of two ways. Managed rotation is rotation the owning service configures and runs, with no function of yours involved. It covers master user credentials in **Amazon Relational Database Service (Amazon RDS)**, the managed relational database service, in **Amazon Aurora**, the AWS-built relational engine, and in **Amazon DocumentDB**, the MongoDB-compatible document database; admin passwords in **Amazon Redshift**, the data warehouse; TLS certificates issued by **AWS Private Certificate Authority**, the managed private CA, to **Amazon Elastic Container Service (Amazon ECS)** Service Connect; and partner-vended secrets. You create these through the managing service, for example by passing `--manage-master-user-password` when you create a database, and rotation typically completes within one minute.

Everything else rotates through a function in **AWS Lambda**, the serverless compute service that runs code on demand. Secrets Manager calls the same function four times, once for each rotation step. `createSecret` generates a new value and stores it under the staging label `AWSPENDING`. `setSecret` changes the credential in the target to match. `testSecret` connects with the pending value to prove it works. `finishSecret` moves `AWSCURRENT` onto the new version, removing `AWSPENDING` in the same call and putting `AWSPREVIOUS` on the version that was current. Because every step keys off a staging label, a failed rotation leaves the old credential current and the application keeps working.

For database secrets, Lambda rotation offers two strategies and the exam separates them on availability. The single user strategy changes the password of one user in one secret. It is simpler and AWS recommends it for most cases, but there is a brief window between the password changing in the database and the secret being updated, during which a client can be denied, so it needs a retry. The alternating users strategy holds two users in one secret: the function clones your user on the first rotation and then alternates which password it changes, so an application reading the secret mid-rotation always gets a valid credential. The cost is that cloning needs a second secret holding superuser credentials, and **RDS Proxy**, the database connection pooler, does not support the strategy.

The schedule is a `rate()` or `cron()` expression in UTC plus a window duration. A secret can rotate as often as every four hours, the maximum period is 999 days, and Secrets Manager rotates at some moment inside the window rather than at an exact time. Windows start on the hour, can be as short as one hour, and must not run into the next one. Two cron constraints trip people up: the minutes field must be `0` and the year field must be `*`.

```bash
aws secretsmanager rotate-secret \
    --secret-id prod/payments/db \
    --rotation-rules '{"ScheduleExpression": "cron(0 16 1,15 * ? *)", "Duration": "2h"}'
```

## Sharing across accounts, replicating across Regions, and the quotas that bite

A secret has a resource policy of its own, up to 20,480 characters, and that is the structural advantage Secrets Manager has over Parameter Store. Cross-account access needs an allow in that resource policy and an allow in an identity policy in the calling account, and neither alone is enough. There is a second requirement the exam loves: the AWS managed key `aws/secretsmanager` cannot be used for cross-account access, so a shared secret must be encrypted with a customer managed key whose policy grants the external role `kms:Decrypt`.

Parameter Store has a resource policy too, but a much narrower one: it exists only to create a share, only on advanced parameters, and AWS directs you to attach it through **AWS Resource Access Manager (AWS RAM)**, the service that shares resources with named accounts, an organizational unit, or an entire organization in **AWS Organizations**, the multi-account governance service. Two restrictions follow. Only advanced parameters can be shared, so sharing configuration across accounts turns a free parameter into a charged one, and a shared `SecureString` must use a customer managed key that you share separately through AWS KMS, because AWS managed keys cannot be shared. Throughput is enforced in each consuming account, so one noisy consumer does not throttle the others.

Multi-Region differs too. Secrets Manager replicates a secret with `ReplicateSecretToRegions`. The replica keeps the same ARN except for the Region, carries the encrypted value along with tags and the resource policy, and can later be promoted to a standalone secret. Rotation runs on the primary and the new value propagates to every replica, so there is nothing to schedule in the replica Regions. A replica is billed as a distinct secret, and a primary cannot be deleted while replicas exist. Parameter Store has no replication: a parameter is Regional, and a multi-Region design creates it in each Region from the same pipeline.

Read throughput is where Parameter Store surprises people. By default all three read operations, `GetParameter`, `GetParameters` and `GetParametersByPath`, share 40 transactions per second for the whole account and Region, and `PutParameter` gets 3. The higher throughput setting raises `GetParameter` to 10,000 per second, `GetParameters` to 1,000, `GetParametersByPath` to 100 and `PutParameter` to 10, and it costs money. Secrets Manager starts far higher: `GetSecretValue` runs at 10,000 per second, while writes such as `PutSecretValue` share 50, and AWS advises against updating a secret value more often than every 10 minutes because the 100-version ceiling fills up.

Deleting is deliberately slow on the Secrets Manager side. `DeleteSecret` schedules deletion after a recovery window of at least seven days, during which the secret is inaccessible but recoverable, unless the caller passes `ForceDeleteWithoutRecovery`. A parameter is gone the moment you delete it.

## Cost and the decision rule

The cost shapes are not comparable, and that asymmetry is what most cost-optimization questions turn on. Secrets Manager charges a monthly fee per secret, prorated hourly, plus a fee per 10,000 API calls, and a replica is billed as another secret. Parameter Store charges nothing at all for a standard parameter at default throughput, neither for storage nor for API interactions. An advanced parameter costs $0.05 per parameter per month, prorated hourly, and its API interactions cost $0.05 per 10,000. Turning on higher throughput makes every API interaction chargeable at $0.05 per 10,000, standard parameters included, which is why it is a setting to enable for a sale weekend and turn off afterwards. An API interaction is one request against one parameter, so a `GetParameters` call returning 10 parameters bills as 10 interactions.

With that in hand, here is the decision rule, applied in order.

| If the stem says | Choose | Because |
|---|---|---|
| Rotate a database password, API key or token automatically | Secrets Manager | Parameter Store has no rotation |
| Grant another account read access to a credential | Secrets Manager | A secret's resource policy grants read directly; a parameter's only creates a RAM share |
| The same credential must be readable in several Regions | Secrets Manager | Built-in replication, with rotation driven from the primary |
| Thousands of configuration values, "MOST cost-effectively" | Parameter Store standard | No charge for storage or API interactions |
| A value over 4 KB, an expiry policy, or sharing configuration across accounts | Parameter Store advanced | Only the advanced tier offers 8 KB, parameter policies and RAM sharing |
| An application already reading Parameter Store now needs rotation | Both | Reference the secret through Parameter Store |

That last row defuses a common distractor. Parameter Store reads a Secrets Manager secret through the reserved path `/aws/reference/secretsmanager/`, so an application that already calls `GetParameter` needs no rewrite when a value graduates from configuration to a rotated secret, and a version stage such as `:AWSCURRENT` can be pinned. Only `GetParameter` and `GetParameters` work against that path.

```bash
aws ssm get-parameter \
    --name /aws/reference/secretsmanager/prod/payments/db \
    --with-decryption
```

Both stores plug into the same consumers, which is why the choice rarely changes the application. **AWS CloudFormation**, the infrastructure as code service, resolves `{{resolve:secretsmanager:secret-id:SecretString:json-key}}` and `{{resolve:ssm-secure:name:version}}` as dynamic references at deploy time, though never inside a custom resource or the user data of an **Amazon Elastic Compute Cloud (Amazon EC2)** instance. Amazon ECS injects either one as a container environment variable. The **AWS Parameters and Secrets Lambda Extension** caches both inside a Lambda execution environment, which is the standard answer to throttling before anyone pays for higher throughput.

## Professional depth

At organization scale the first question is where the value lives and who reads it. For secrets, the pattern that scales is one owning account per data domain, a customer managed KMS key in that account, and a secret resource policy conditioned on `aws:PrincipalOrgID` rather than a list of account IDs, so new accounts inherit access as they join. It needs a second allow for `kms:Decrypt` on the key policy, and the AWS managed key forecloses the pattern entirely. For configuration, the equivalent is a shared-services account holding advanced parameters shared through AWS RAM, one of the few cases where the advanced tier is worth paying for.

The quota that bites in production is the Parameter Store read quota, and Professional questions describe it as a symptom rather than a cause. Forty transactions per second shared across all three read operations for a whole account and Region means a deployment that launches fifty tasks at once, each reading a handful of parameters at startup, returns `ThrottlingException`. The fix has an order: batch with `GetParameters` instead of looping `GetParameter`, cache in the process or with the Lambda extension, stagger startup reads, and only then enable higher throughput, because that setting turns a free workload into a billed one for every interaction in the account and Region.

Rotation failures are the other recurring Professional scenario. A rotation function inside an **Amazon Virtual Private Cloud (Amazon VPC)**, the private network service, needs a network path to both the database and the Secrets Manager endpoint, which in a private subnet means a NAT gateway or an interface VPC endpoint, and the classic symptom is a rotation that times out at `setSecret` with nothing else wrong. If any step fails, Secrets Manager retries the whole rotation during the open windows, so a one-hour window on a daily schedule leaves retries almost no room. Turning rotation on also requires `iam:CreateRole` and `iam:AttachRolePolicy`, a privilege escalation risk AWS calls out explicitly.

One migration detail is worth carrying into an exam. Moving a database to RDS-managed master user credentials replaces your rotation function with managed rotation, and Amazon RDS then owns the secret. That cuts overhead but removes the alternating users option, so an application that cannot tolerate a denied connection keeps a dedicated application user with its own secret.

## Worked scenario

A payments company runs an order service on Amazon ECS in two Regions, active in both. Each task reads about 30 configuration values at startup, including endpoint URLs and feature toggles, and connects to an Aurora cluster whose credentials a regulator requires to rotate every 30 days. A reporting account in the same organization must read that credential. During a deployment, ECS replaces roughly 60 tasks at once, and the team is seeing `ThrottlingException` from Systems Manager.

The 30 configuration values become standard parameters under `/orders/prod/`, created in both Regions by the same pipeline, at no charge. The database credential becomes a secret in the production account encrypted with a customer managed KMS key, with Lambda rotation on the alternating users strategy so a task reading the secret mid-rotation still gets a working credential, scheduled with `cron(0 2 1 * ? *)` and a two-hour window. The secret is replicated to the second Region, so both Regions read locally while rotation runs only on the primary. The reporting account is granted `secretsmanager:GetSecretValue` in the secret's resource policy and `kms:Decrypt` in the key policy, plus the same action on the secret ARN in its own identity policy. For the throttling, the team replaces 30 `GetParameter` calls per task with four `GetParameters` calls and caches the results for the life of the task, dropping the burst under 40 transactions per second without paying for higher throughput.

The exam asks why the reporting account still gets access denied after the secret's resource policy is corrected. The keyed answer is that the KMS key policy does not yet allow the reporting role to call `kms:Decrypt`, and that `aws/secretsmanager` could not have been used here at all because it does not support cross-account access.

## Exam lens

- "rotate the database password automatically every 30 days" maps to Secrets Manager rotation; a `SecureString` parameter plus a scheduled script is the custom-build distractor.
- "the application must never receive an invalid credential during rotation" maps to the alternating users strategy; single user is the distractor.
- "rotate on the first and fifteenth of the month at 4 PM" maps to a `cron()` rotation schedule with a window duration; "rotation cannot be scheduled" is wrong.
- "share the configuration value with every account in the organization" maps to an advanced parameter shared through AWS RAM; a standard parameter cannot be shared at all.
- "store 8,000 endpoint URLs and AMI IDs, MOST cost-effectively" maps to Parameter Store standard parameters, which carry no charge; Secrets Manager bills per item per month.
- "another account must read the credential" maps to a secret resource policy plus an identity policy plus a customer managed KMS key; `aws/secretsmanager` is the distractor because it cannot be used cross-account.
- "the credential must be readable in three Regions with the same name" maps to Secrets Manager multi-Region replication; recreating the parameter per Region is the answer only for configuration.
- "ThrottlingException from GetParameter when many tasks start" maps first to batching and caching, and only then to the higher throughput setting, which makes every API interaction chargeable.
- "we already read configuration from Parameter Store but now need rotation" maps to the `/aws/reference/secretsmanager/` path, not to rewriting the application.

## Knowledge check

### 1. Credentials for an application on Amazon EC2 (Associate)

A retailer runs a web application on Amazon EC2 instances that connects to an Amazon RDS for PostgreSQL database using a dedicated application user. A new security standard requires the database password to change every 30 days without any application downtime and without a person touching it. The team does not want to build or operate a scheduler.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Store the password as a Parameter Store `SecureString` parameter and run a cron job on one instance that generates a new password, updates the database and updates the parameter.
- **B)** Store the password in an AWS Secrets Manager secret, turn on automatic rotation with a 30-day schedule, and have the application retrieve the secret from Secrets Manager when it opens a connection.
- **C)** Store the password as an advanced parameter with an `Expiration` policy set to 30 days so the parameter is replaced on schedule.
- **D)** Store the password in an AWS Secrets Manager secret and have an operator call `PutSecretValue` each month after changing the password in the database.

<details><summary>Answer</summary>

**Answer: B.** Secrets Manager rotation is the only option that changes the credential in both the database and the store on a schedule with nothing for the team to run. A is a custom build of something AWS already manages, and it adds an instance that must hold privileged database credentials. C misreads the `Expiration` policy: it deletes the parameter when the time is up, it does not generate a new value or update the database, so the application would lose its credential entirely. D meets the 30-day interval only through manual work, which is exactly the operational overhead the stem rules out.

*Where this is covered: Rotation: managed, by Lambda, and the staging labels.*

</details>

### 2. Configuration data for a large fleet (Associate)

A media company needs a central store for roughly 7,000 configuration values: approved machine image identifiers, service endpoint URLs, and feature toggles. None of the values are credentials, each is well under 1 KB, and all are read by applications inside a single account and Region. The company wants the lowest possible cost.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Store each value as an AWS Secrets Manager secret and read it with `GetSecretValue`.
- **B)** Store each value as a Parameter Store advanced parameter so the company can attach policies later.
- **C)** Store each value as a Parameter Store standard parameter in a hierarchy such as `/app/prod/`.
- **D)** Store the values as a JSON object in a single AWS Secrets Manager secret and parse it in the application.

<details><summary>Answer</summary>

**Answer: C.** Standard parameters carry no additional charge for storage and no charge for API interactions at default throughput, the account limit of 10,000 standard parameters comfortably covers 7,000 values, and 1 KB is well inside the 4 KB ceiling. A pays a monthly fee for every one of 7,000 items plus a fee per 10,000 API calls, for data that is not secret. B pays $0.05 per parameter per month plus API interaction charges for capabilities the stem does not ask for. D is not workable at this scale: a secret value caps at 65,536 bytes, well short of 7,000 values of up to 1 KB each, and it would still bill per API call while giving up the hierarchy.

*Where this is covered: Cost and the decision rule.*

</details>

### 3. Reading a secret from another account (Associate)

A company stores an API key for a payment provider in an AWS Secrets Manager secret in its production account, encrypted with the AWS managed key `aws/secretsmanager`. A role in a separate analytics account must read the secret. The analytics role already has `secretsmanager:GetSecretValue` on the secret ARN in its identity policy, but every call fails with an access denied error.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Re-encrypt the secret with a customer managed KMS key in the production account and allow the analytics role `kms:Decrypt` in that key's policy.
- **B)** Attach a resource policy to the secret in the production account that allows the analytics role to call `secretsmanager:GetSecretValue`.
- **C)** Replicate the secret to the Region used by the analytics account.
- **D)** Share the secret with the analytics account through AWS Resource Access Manager.
- **E)** Grant the analytics role `kms:Decrypt` on `aws/secretsmanager` in the production account.

<details><summary>Answer</summary>

**Answer: A and B.** Cross-account access to a secret requires an allow in the secret's resource policy and an allow in the caller's identity policy, and the identity side is already in place, so the resource policy is the first gap. The second is the key: the AWS managed key `aws/secretsmanager` cannot be used for cross-account access, so the secret must be encrypted with a customer managed key whose policy admits the analytics role. C solves a latency and availability problem, not an authorization one, and a replica inherits the same policy gap. D is not how Secrets Manager shares: AWS RAM shares advanced Parameter Store parameters, not secrets. E cannot be done, because the key policy of an AWS managed key is controlled by the service and cannot be edited to admit another account.

*Where this is covered: Sharing across accounts, replicating across Regions, and the quotas that bite.*

</details>

### 4. A configuration value that must expire (Associate)

A bank stores a 6 KB allow list of partner network ranges as configuration for an internal service. Compliance requires that the value be removed automatically 90 days after it is written, and that an event be raised 15 days beforehand so an engineer can refresh it.

Which solution will meet these requirements?

- **A)** Store the value as a Parameter Store standard parameter and write an Amazon EventBridge scheduled rule that deletes it after 90 days.
- **B)** Store the value in an AWS Secrets Manager secret and set the rotation schedule to `rate(90 days)`.
- **C)** Store the value as a Parameter Store standard parameter and attach `Expiration` and `ExpirationNotification` policies.
- **D)** Store the value as a Parameter Store advanced parameter and attach `Expiration` and `ExpirationNotification` policies.

<details><summary>Answer</summary>

**Answer: D.** A 6 KB value exceeds the 4 KB standard parameter ceiling and so needs the advanced tier anyway, and parameter policies, which are the feature that expires a parameter and notifies through Amazon EventBridge before it does, are available only on advanced parameters. A fails twice: a standard parameter cannot hold 6 KB, and it builds a scheduler for something Parameter Store already does. B is the wrong service for a non-credential value and misreads rotation, which replaces a value rather than deleting it. C attaches policies to a tier that does not support them, and still breaks the size limit.

*Where this is covered: What each service stores and how it is encrypted.*

</details>

### 5. Throttling during a container deployment (Professional)

A logistics platform runs 40 services on Amazon ECS across three accounts. Each task reads 25 Parameter Store standard parameters at startup by calling `GetParameter` once per value. During a rolling deployment, ECS replaces up to 80 tasks at a time, and the deployment now fails intermittently with `ThrottlingException` from Systems Manager. The platform team must fix the failures without introducing a new monthly charge for the thousands of parameters that are currently free.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable the Parameter Store higher throughput setting in each account and Region.
- **B)** Change each task to make one `GetParameters` call for its 25 named parameters instead of 25 `GetParameter` calls.
- **C)** Convert the parameters to the advanced tier so they get a separate throughput pool.
- **D)** Move all 25 values into a single AWS Secrets Manager secret and read it once per task.
- **E)** Cache the retrieved values in the task for its lifetime and stagger startup reads so they do not all land in the same second.

<details><summary>Answer</summary>

**Answer: B and E.** The default quota of 40 transactions per second is shared across `GetParameter`, `GetParameters` and `GetParametersByPath` for the whole account and Region, so collapsing 25 calls into one and spreading the remaining bursts across seconds brings the deployment under the ceiling with no change to the bill. A does fix the throttling, but enabling higher throughput makes every API interaction chargeable at $0.05 per 10,000, including interactions with standard parameters, which is the new charge the stem forbids. C confuses tiers with throughput: tiers control storage size and features, not request rate, and advanced parameters bill per parameter per month. D replaces a free store with one that charges per secret per month and per API call, for values that are configuration rather than credentials.

*Where this is covered: Professional depth.*

</details>

### 6. An active-active design with a rotated credential (Professional)

An insurer runs an application in eu-west-1 and us-east-1, serving traffic from both. Both Regions connect to an Aurora global database and must read the same application database credential from within their own Region, with no cross-Region API call on the read path. The credential must rotate every seven days, the rotation must be configured in exactly one place, and a regional outage must not stop the other Region from reading the credential.

Which solution will meet these requirements?

- **A)** Create the secret in eu-west-1, turn on rotation with a `rate(7 days)` schedule, and replicate the secret to us-east-1 with `ReplicateSecretToRegions`.
- **B)** Create the secret in eu-west-1 with a `rate(7 days)` rotation schedule and have the us-east-1 application call the eu-west-1 Secrets Manager endpoint.
- **C)** Create a separate secret in each Region, each with its own rotation function and a `rate(7 days)` schedule against the same database user.
- **D)** Store the credential as a Parameter Store advanced parameter in each Region and share both through AWS Resource Access Manager.

<details><summary>Answer</summary>

**Answer: A.** A replicated secret keeps the same name and ARN apart from the Region, so each application reads locally, and rotation runs on the primary with the new value propagating to every replica, which satisfies "configured in exactly one place". B keeps a single configuration point but puts a cross-Region call on the read path and makes the eu-west-1 endpoint a dependency for us-east-1, breaking both the latency and the isolation requirements. C configures rotation twice and has two functions rotating the same database user, which will race and leave one secret holding a stale password. D has no rotation at all, since Parameter Store does not rotate credentials, and RAM sharing addresses cross-account access rather than cross-Region reads.

*Where this is covered: Sharing across accounts, replicating across Regions, and the quotas that bite.*

</details>

## Summary

The choice between these two services is a short chain of decisions. Start with rotation, the one capability Secrets Manager has and Parameter Store does not: if the value is a credential that must change on a schedule it is a secret, and if a database service can own that secret, managed rotation beats writing a Lambda rotation function. Next ask who reads it. A secret carries its own resource policy, so cross-account access is a policy edit plus a customer managed KMS key, while a parameter's own policy only creates a share, through AWS RAM and only in the advanced tier. Then ask where it is read: Secrets Manager replicates across Regions with rotation on the primary, while a parameter is Regional and must be recreated per Region. Then count and price. Standard parameters are free to store and free to read, which makes them the default for configuration and the answer to almost every "MOST cost-effectively" stem, while advanced parameters buy 8 KB values, expiry policies and RAM sharing for a monthly fee. Finally, the two are not exclusive: an application already reading Parameter Store can reach a rotated secret through `/aws/reference/secretsmanager/` without a rewrite.

## Related units

- [AWS Key Management Service and AWS CloudHSM](kms-and-cloudhsm.md): the keys that encrypt secrets and `SecureString` parameters, and why an AWS managed key blocks cross-account use
- [AWS Identity and Access Management](iam.md): the identity policy half of every cross-account grant, and `aws:PrincipalOrgID` conditions
- [AWS Systems Manager](../08-management/systems-manager.md): the rest of Systems Manager, including Session Manager, Run Command and Patch Manager
- [Amazon RDS](../05-database/rds.md): managed master user passwords, RDS Proxy and IAM database authentication
- [AWS Lambda](../02-compute/lambda.md): the execution role, VPC networking and extensions that rotation functions depend on
- [Amazon ECS and Amazon ECR](../03-containers/ecs-and-ecr.md): injecting secrets and parameters as container environment variables
- [AWS CloudFormation](../08-management/cloudformation.md): dynamic references that resolve secrets and parameters at deploy time
- [AWS Organizations, IAM Identity Center and Control Tower](organizations-identity-center-and-control-tower.md): AWS RAM sharing and organization-wide policy conditions

## Sources

- [AWS Secrets Manager quotas](https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_limits.html): 65,536-byte secret value, 500,000 secrets per Region, 100 versions, 20 staging labels, 20,480-character resource policy, and the read and write request rates
- [Managed rotation for AWS Secrets Manager secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_managed.html): which services offer managed rotation and that it typically completes within one minute
- [Rotation by Lambda function](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_lambda.html): the four rotation steps, the request structure and the retry behavior
- [Lambda rotation functions](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_lambda-functions.html): `createSecret`, `setSecret`, `testSecret` and `finishSecret`, and the `AWSCURRENT`, `AWSPENDING` and `AWSPREVIOUS` staging labels
- [Lambda function rotation strategies](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotation-strategy.html): single user compared with alternating users
- [Set up automatic rotation for a database secret](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_turn-on-for-db.html): that RDS Proxy does not support the alternating users strategy
- [Rotation schedules](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_schedule.html): `rate()` and `cron()` expressions, the four-hour minimum, the 999-day maximum and the rotation window rules
- [Access AWS Secrets Manager secrets from a different account](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_examples_cross.html): the two-policy requirement and that `aws/secretsmanager` cannot be used cross-account
- [Replicate AWS Secrets Manager secrets across Regions](https://docs.aws.amazon.com/secretsmanager/latest/userguide/create-manage-multi-region-secrets.html): replica ARNs, rotation on the primary, promotion to standalone and partition restrictions
- [Delete an AWS Secrets Manager secret](https://docs.aws.amazon.com/secretsmanager/latest/userguide/manage_delete-secret.html): the minimum seven-day recovery window and the replica deletion order
- [AWS Secrets Manager pricing](https://aws.amazon.com/secrets-manager/pricing/): per-secret monthly charge prorated hourly, replicas billed as distinct secrets, and a per-10,000 API call charge
- [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html): the parameter tier table, the 100-version retention and the comparison stating that Parameter Store offers no credential rotation
- [Choosing parameter tiers in Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-advanced-parameters.html): 10,000 against 100,000 parameters, 4 KB against 8 KB, and why an advanced parameter cannot be downgraded
- [Parameter Store reference](https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-a-parameter.html): `String`, `StringList` and `SecureString`, symmetric KMS keys only, and that only the value is encrypted
- [Assigning parameter policies in Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-policies.html): `Expiration`, `ExpirationNotification` and `NoChangeNotification`, and that policies require the advanced tier
- [Managing Parameter Store throughput](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-throughput.html): the 40 TPS shared default, the higher throughput figures, and that higher throughput bills every API interaction
- [Working with shared parameters in Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-shared-parameters.html): AWS RAM sharing, the advanced tier prerequisite, and the customer managed key requirement for `SecureString`
- [AWS Systems Manager pricing](https://aws.amazon.com/systems-manager/pricing/): standard parameters at no additional charge, $0.05 per advanced parameter per month, and $0.05 per 10,000 API interactions
- [Referencing AWS Secrets Manager secrets from Parameter Store parameters](https://docs.aws.amazon.com/systems-manager/latest/userguide/integration-ps-secretsmanager.html): the `/aws/reference/secretsmanager/` path and the `GetParameter` and `GetParameters` restriction
- [Using dynamic references to specify template values](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html): the 60-reference ceiling and where secure dynamic references are not supported
- [Password management with Amazon RDS and AWS Secrets Manager](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-secrets-manager.html): `--manage-master-user-password`, automatic generation, storage and regular rotation
