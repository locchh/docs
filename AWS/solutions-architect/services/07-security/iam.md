# AWS Identity and Access Management

**Where it sits on the exams.** **AWS Identity and Access Management (IAM)**, the global service that decides which principal may perform which action on which resource, is the authorization layer every other AWS service consults before it does anything. Every request to AWS is authenticated and then authorized against the policies that apply to it, so IAM supplies the answer to a security question in almost every scenario the two exams describe. It is the owning service for SAA-C03 tasks 1.1 and 3.5, and for SAP-C02 tasks 1.2, 2.3, 3.2 and 4.2. The rule of thumb the exam rewards is to give identities temporary credentials through roles, write the narrowest policy that satisfies the stated requirement, and remember that an explicit deny anywhere in the evaluation always wins.

## What IAM controls and the shared responsibility model

IAM is a global service. Users, groups, roles, customer managed policies and identity providers are account-wide objects that exist once and work in every Region, and the control plane answers at a single endpoint, `iam.amazonaws.com`. There is no charge for IAM itself. Because the data is replicated worldwide, IAM is eventually consistent: a policy you just attached or a role you just created can take a moment to be visible everywhere, which is why automation that creates a role and immediately assumes it should retry rather than fail.

When a principal calls an API, AWS assembles a request context that names the principal, the action such as `s3:GetObject`, the resource Amazon Resource Name (ARN), and a set of condition context keys describing the request: source IP address, whether multi-factor authentication (MFA) was used, the requested Region, the principal's tags, the time. Authentication establishes who is calling. Authorization then matches that context against every applicable policy. The default answer is no. AWS documents this as an implicit deny: "By default, all requests are implicitly denied with the exception of the AWS account root user, which has full access." Nothing is permitted until some policy explicitly allows it, and nothing stays permitted if any policy explicitly denies it.

An Amazon Resource Name is the global name for a resource and the unit a policy's `Resource` element works with. It has the shape `arn:aws:service:region:account-id:resource`, with the Region and account fields empty for global services. Policies match ARNs literally or with the `*` and `?` wildcards, so scoping a statement to `arn:aws:s3:::reports-prod/*` rather than `*` is the mechanical form that least privilege takes.

IAM is where the AWS shared responsibility model becomes concrete. AWS is responsible for security *of* the cloud: the hardware, software, networking and facilities that run AWS services, including physical security, the hypervisor and the managed service software itself. The customer is responsible for security *in* the cloud: their data, the guest operating system and its patches on an instance, application software, network and firewall configuration, encryption choices, and identity and access management. The boundary moves with the service. On **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service, the customer patches the guest operating system and configures the firewall. On an abstracted service such as **Amazon Simple Storage Service (Amazon S3)**, the object storage service, AWS operates the platform and the customer configures access, encryption and retention. What never moves is identity: in every service, on every tier, deciding who may call which API is the customer's half of the model. An exam question that says "AWS is responsible for" and lists patching an EC2 guest operating system or writing a bucket policy is testing this boundary directly.

The model divides controls three ways. Inherited controls such as physical and environmental protection pass to the customer whole, shared controls such as patch management and configuration management are implemented by both parties in their own layer, and customer-specific controls belong entirely to the customer. Compliance evidence for the AWS half comes from **AWS Artifact**, the self-service portal for AWS audit reports, rather than from inspecting the infrastructure.

## Principals: the root user, users, groups, roles and federated identities

Every AWS account is created with an account root user that owns the account's email address and password and has complete access to every service and resource, including billing. Identity-based policies cannot restrict it, because none is attached to it; the only controls that reduce what a member-account root user does are organization policies and the centralized root access feature described later. A short list of tasks genuinely requires it: changing the account name, email address or root password, closing the account, changing AWS Support plans, restoring permissions after the last administrator is locked out, and unlocking a resource policy that denies all principals.

AWS now requires MFA for the root user of every account type. The documentation states that "All AWS account types (standalone, management, and member accounts) require MFA to be configured for their root user" and that "Users must register MFA within 35 days of their first sign-in attempt to access the AWS Management Console if MFA is not already enabled." You can register up to eight MFA devices on a root user, and AWS recommends phishing-resistant factors, meaning passkeys and FIDO security keys, over time-based one-time password applications. You should not create access keys for the root user at all; for programmatic root work AWS now points at the `aws login` command, which vends temporary, automatically rotated credentials instead of a long-lived key pair.

An IAM user is a durable identity inside one account with long-term credentials: an optional console password and up to two access keys, a quota that is not adjustable and exists so that a key can be rotated by creating the second key, moving traffic, then deleting the first. A key can also be set to `Inactive` rather than deleted, which is the safer intermediate step: it stops working immediately but can be reactivated if something still depended on it. An account can hold 5,000 users, and that quota is fixed. IAM groups are containers that carry policies for a set of users; a user can belong to 10 groups, an account can have 300 groups by default, groups cannot be nested, and a group is not a principal, so it can never appear in the `Principal` element of a resource policy. Groups organize people. They do not federate, they do not receive temporary credentials, and they are not the answer when the requirement mentions applications or other accounts.

An IAM role is an identity with permissions but no long-term credentials of its own. It carries two policies: a permissions policy saying what the role may do, and a trust policy, which is a resource-based policy on the role saying which principals may assume it. Assuming a role produces temporary credentials for a session. Roles are the intended mechanism for everything except a legacy tool: a workload on EC2 uses an instance profile, a function in **AWS Lambda**, the serverless function service, uses an execution role, a human in another account switches roles, a federated employee assumes a role after their identity provider authenticates them, and a third party assumes a role you created for them. The default quota is 1,000 roles per account, automatically raisable to 10,000.

Federated identities are authenticated somewhere else and mapped to a role. IAM supports SAML 2.0 identity providers for a corporate directory reached through Active Directory Federation Services or **AWS Directory Service**, the managed directory family covered in [directory-service.md](directory-service.md), and OpenID Connect (OIDC) providers for web and continuous integration systems. For workforce sign-in across many accounts, the current answer is **AWS IAM Identity Center**, the workforce identity and single sign-on service that connects an external identity source to permission sets in every account of an organization, and it is taught in [organizations-identity-center-and-control-tower.md](organizations-identity-center-and-control-tower.md); a newer IAM feature called account access manager lets you assign existing IAM roles, with their custom trust policies and role tags, to Identity Center users and groups when a permission set is not expressive enough. The boundary that matters for the exam is short: Identity Center and IAM roles handle workforce and workload identities that call AWS APIs, while **Amazon Cognito**, the service that authenticates an application's own end users and can exchange their sign-in for scoped AWS credentials, handles customers of your application, and it is taught in [cognito.md](cognito.md).

That gives a selection rule. Employees federate and receive temporary credentials. Workloads on AWS use a role attached to the compute resource. Workloads outside AWS use **IAM Roles Anywhere**, which trades an X.509 certificate for temporary credentials, or OIDC federation. An IAM user with long-term access keys remains only for the narrow cases AWS names: a tool that cannot use temporary credentials, a third-party client that does not support Identity Center, and a few service-specific credential types. Naming an IAM user for a new application or a new employee is almost always the distractor.

## Policy documents and the six policy types

A policy is a JSON document. The `Version` element should always be `2012-10-17`, because the older version does not support policy variables. Each statement carries an optional `Sid`, an `Effect` of `Allow` or `Deny`, an `Action` list naming `service:Operation` pairs, a `Resource` list of ARNs, an optional `Principal` when the policy is attached to a resource, and an optional `Condition` block. `NotAction` and `NotResource` invert a list and are easy to get wrong: `"NotAction": "iam:*"` in an `Allow` grants every action in AWS except IAM, which is far broader than most authors intend.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ReadOneProductionPrefix",
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::reports-prod",
      "arn:aws:s3:::reports-prod/quarterly/*"
    ],
    "Condition": {"Bool": {"aws:SecureTransport": "true"}}
  }]
}
```

Six kinds of policy participate in an authorization decision, and knowing which one a scenario is asking for is most of the work. The table lists them in the order they are introduced below; read it as "what attaches where, and does it grant or only limit".

| Policy type | Attached to | Grants access | Typical use |
|---|---|---|---|
| Identity-based | User, group, role | Yes | The normal way to give a principal permissions |
| Resource-based | The resource itself | Yes | Cross-account sharing and service access to one resource |
| Permissions boundary | One user or role | No, limits only | Delegating role creation safely inside an account |
| Session policy | Passed at `AssumeRole` time | No, limits only | Narrowing one session below the role's own permissions |
| Service control policy (SCP) | Organization root, OU, account | No, limits only | Maximum permissions for principals in member accounts |
| Resource control policy (RCP) | Organization root, OU, account | No, limits only | Maximum permissions on resources in member accounts |

Identity-based policies come in three forms. AWS managed policies are written and updated by AWS, are the fastest start, and are deliberately broad, so `AdministratorAccess` or `ReadOnlyAccess` is a starting point rather than a least-privilege answer. Customer managed policies are yours, are versioned with up to five stored versions and one default, can be attached to many principals, and are the recommended form. An inline policy is embedded in one user, group or role, is deleted when that entity is deleted, and cannot be reused, so it fits a strict one-to-one relationship and nothing else. Size limits differ and occasionally decide a design: a managed policy holds 6,144 characters, and the aggregate inline policy size is 2,048 characters for a user, 5,120 for a group and 10,240 for a role, with whitespace excluded.

A resource-based policy hangs off the resource, always names a `Principal`, and is the only way for an account to grant something to a principal in another account without that principal first assuming a local role. The familiar examples are an S3 bucket policy, an **AWS Key Management Service (AWS KMS)** key policy, where AWS KMS is the managed key service, an **Amazon Simple Queue Service (Amazon SQS)** queue policy, where Amazon SQS is the managed message queue, an **Amazon Simple Notification Service (Amazon SNS)** topic policy, where Amazon SNS is the publish-and-subscribe service, a Lambda function policy, an **AWS Secrets Manager**, the managed secret store, resource policy, and an IAM role's trust policy. Most services do not support them; when a question asks how one account grants another direct access to a specific queue, bucket or key, the resource policy is the mechanism, and when it asks how a principal gets broad access to many resources in another account, the role is.

A permissions boundary is a managed policy attached to a user or role that caps what that entity's identity-based policies can grant. It never grants anything itself. The classic use is delegation: give developers `iam:CreateRole` but require through the `iam:PermissionsBoundary` condition key that any role they create carries a specified boundary, so they can move quickly without being able to manufacture an administrator. A session policy is passed as a parameter at the moment a session is created and narrows that one session; the effective permissions are the intersection of the role's policies and the session policy, and a session policy can never add a permission the role does not already have.

Role assumption throughout this unit runs through **AWS Security Token Service (AWS STS)**, the service that issues temporary security credentials, which the section on STS develops in full. Service control policies and resource control policies come from **AWS Organizations**, the multi-account governance service, and are taught alongside **AWS Control Tower**, which sets up and governs a multi-account landing zone, in [organizations-identity-center-and-control-tower.md](organizations-identity-center-and-control-tower.md). Their IAM mechanics belong here. An SCP bounds what principals in a member account may do. An RCP bounds what may be done to resources in a member account, including by principals outside the organization. Neither grants anything: "No permissions are granted by SCPs and RCPs." Two details decide exam questions. RCPs apply only to a specific, short list of services, currently including Amazon S3, AWS KMS, Amazon SQS, AWS Secrets Manager, AWS STS, **Amazon DynamoDB**, the managed NoSQL database, **Amazon Elastic Container Registry (Amazon ECR)**, the container image registry, and roughly forty others, so "an RCP will stop that for every service" is a wrong answer. And neither SCPs nor RCPs affect the organization's management account, which is the standing argument for running no workloads there.

Access control lists are the legacy seventh mechanism: cross-account grants attached to a resource, with no conditions and no explicit deny, and disabled by default for new S3 buckets. Treat an answer that reaches for an ACL as a distractor unless the scenario explicitly depends on legacy behavior.

## How a request is authorized: the policy evaluation logic

This is the single most directly tested mechanism in the unit. AWS evaluates every applicable policy in a fixed order, and the first step that returns a final decision ends the evaluation.

The evaluation begins with deny. AWS gathers every policy that applies, across all six types, and looks for a `Deny` statement matching the request. "If the enforcement code finds even one explicit deny that applies, the enforcement code returns a final decision of Deny." There is no appeal and no precedence argument: an explicit deny in an SCP, an RCP, a bucket policy, an identity policy, a boundary or a session policy ends the request. This is why a deny statement is the right tool for a non-negotiable rule such as "no unencrypted transport" or "never outside these Regions", and why a misplaced deny can lock administrators out of their own account.

If no explicit deny applies, AWS evaluates in this order. First resource control policies: if none of the RCPs that apply to the resource contains a matching `Allow`, the request is denied. In practice the AWS managed `RCPFullAWSAccess` policy is attached automatically to every root, organizational unit and account when RCPs are enabled and cannot be detached, so an `Allow` always exists unless someone has written a restrictive RCP. Second service control policies: with no matching `Allow` in the SCPs that apply to the calling principal's account, the request is denied. Third resource-based policies, then identity-based policies, then permissions boundaries, then session policies. At the last three steps, the absence of a matching `Allow` is an implicit deny that ends the evaluation. The resource-based policy step behaves differently: within a single account, no matching resource policy simply means evaluation continues to the identity-based policies, which is why a same-account request can succeed on an identity policy alone, except for the resource-policy special cases below.

Within a single account, the usual rule is that one `Allow` is enough. "For most resources, you only need an explicit Allow for the principal in either an identity-based policy or a resource-based policy to grant access." The permissions are the union of the two. Two exceptions matter: IAM role trust policies and KMS key policies must explicitly allow the principal, so granting a user `kms:Decrypt` in an identity policy achieves nothing if the key policy does not admit them, and granting `sts:AssumeRole` achieves nothing if the role's trust policy does not name the caller. A subtlety on top of that is that a same-account resource policy naming an IAM user or a specific role session ARN grants that session directly, unreduced by an implicit deny elsewhere, while one naming a role ARN is still limited by a boundary or session policy.

Cross-account access follows a different and simpler rule that questions test constantly. AWS performs two complete evaluations, one in the trusted account that holds the principal and one in the trusting account that holds the resource, and "the request is allowed only if both evaluations return a decision of Allow." The identity-based policy in the caller's account must allow the action on the target ARN, and the resource-based policy in the resource's account must allow that principal. Neither side can grant on its own. An answer that fixes only the bucket policy, or only the caller's IAM policy, when the scenario spans two accounts is incomplete by construction. The same two-sided requirement is why an explicit deny in either account is fatal: in the AWS example, a developer whose own identity policy denies any bucket whose name contains `log` cannot write to a log bucket in another account no matter what that bucket's policy says.

Two practical corollaries follow. A principal in another account can be admitted either by naming it in a resource policy or by having it assume a role in the resource's account; assuming the role converts the request into a local identity and usually produces a smaller, more auditable policy surface. And a permissions boundary or session policy applies only in the account that holds the principal, while SCPs apply in the principal's account and RCPs in the resource's account, which is how an organization can constrain both ends of a cross-account call.

## Conditions, ABAC and the shape of least privilege

The `Condition` block is where a policy stops being a list of actions and starts expressing a security requirement. A condition names an operator, a context key and a value: `"Condition": {"StringEquals": {"aws:PrincipalOrgID": "o-abc123"}}`. Operators cover strings, numbers, dates, Booleans, IP addresses, ARNs and null checks, and appending `IfExists` makes a condition pass when the key is absent from the request rather than fail. Several operators in one block are combined with AND, several values for one key with OR. A key that is not present in the request context is a mismatch, so `Null` checks and `IfExists` are how you avoid accidentally denying a service principal that does not send the key.

A handful of global keys answer most exam scenarios. `aws:PrincipalOrgID` admits every account in an organization without enumerating account IDs, which is the standard way to write a bucket or key policy that stays correct as accounts are added. `aws:PrincipalOrgPaths` narrows that to an organizational unit. `aws:SourceIp` restricts to a public address range and does not match traffic arriving through a VPC endpoint, where `aws:SourceVpce` or `aws:SourceVpc` is the key that works. `aws:SecureTransport` denies plain HTTP. `aws:RequestedRegion` implements a data residency rule. `aws:MultiFactorAuthPresent` and `aws:MultiFactorAuthAge` require MFA, and the age variant is how "re-authenticate within the last hour before deleting anything" is written. `aws:PrincipalArn` and `aws:PrincipalAccount` identify the caller in a resource policy. For service-to-service calls, `aws:SourceAccount` and `aws:SourceArn` pin which account and which resource may cause a service to act on your behalf, which is the standard defense against the confused deputy problem when SNS, S3 or CloudWatch invokes something.

```json
{
  "Effect": "Deny",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::research-data", "arn:aws:s3:::research-data/*"],
  "Principal": "*",
  "Condition": {"StringNotEquals": {"aws:PrincipalOrgID": "o-abc123def4"}}
}
```

Two keys handle tags. `aws:ResourceTag/key` reads a tag on the resource being touched; `aws:PrincipalTag/key` reads a tag on the calling identity. Putting them together produces attribute-based access control (ABAC), where one policy allows an action when the principal's tag value equals the resource's tag value. AWS contrasts this with role-based access control (RBAC), the traditional model of one policy per job function that lists specific resources. The disadvantage of RBAC that the exam wants you to name is that "when you or your users add new resources to your environment, you have to update the policies to allow access to those resources". ABAC does not need that edit: tag the new instance `project = Heart` and everyone whose principal carries the same tag can already use it.

ABAC scales with headcount and project count, needs far fewer policies, and reaches directly into the corporate directory, because a SAML or OIDC provider can pass session tags that become the principal's tags for the session. Its cost is tag discipline. If anyone can set a tag, anyone can grant themselves access, so an ABAC design pairs the permission policy with controls on tagging itself: `aws:TagKeys` to enforce a naming convention, `aws:RequestTag/key` to constrain what values may be applied, and a deny on `tag` actions for the tags that drive authorization. The exam signal is the wording. "Permissions must apply automatically to new projects and resources without editing policies" is ABAC. "Each job function needs a defined set of permissions" is RBAC, and the two coexist in real designs.

Least privilege is the goal these mechanisms serve. AWS recommends starting from a managed policy while you learn the workload, replacing it with a customer managed policy scoped to specific actions, resource ARNs and conditions, then verifying with the auditing tools covered later. Wildcards are the measurable failure: `"Action": "*"` with `"Resource": "*"` in a production role is the finding every reviewer looks for first.

## AWS STS, role assumption and session duration

AWS STS is the engine behind every role. A successful call returns four values: an `AccessKeyId`, a `SecretAccessKey`, a `SessionToken` that must accompany every signed request, and an `Expiration`. Temporary credentials cannot be revoked by deleting them, because there is nothing stored to delete; they simply expire, which is why an emergency response revokes access by attaching a deny policy or by changing the role's trust policy rather than by rotating a key. Note that STS is named in the SAA-C03 task 1.1 skills and appears in the SAP-C02 in-scope service list, though its mechanics are examinable on both.

Five operations produce credentials, and the exam distinguishes them by who calls and what is presented.

| Operation | Who calls it | Duration: min, max, default |
|---|---|---|
| `AssumeRole` | An IAM user or a role with existing temporary credentials | 15 minutes, the role's maximum session duration, 1 hour |
| `AssumeRoleWithSAML` | Any user presenting a SAML 2.0 assertion from a registered provider | 15 minutes, the role's maximum session duration, 1 hour |
| `AssumeRoleWithWebIdentity` | Any user presenting an OIDC-compliant JSON Web Token | 15 minutes, the role's maximum session duration, 1 hour |
| `GetFederationToken` | An IAM user or root user, for a custom identity broker | IAM user 15 minutes to 36 hours, default 12 hours; root user 15 minutes to 1 hour |
| `GetSessionToken` | An IAM user or root user, usually to attach MFA state | IAM user 15 minutes to 36 hours, default 12 hours; root user 15 minutes to 1 hour |

The role's maximum session duration setting ranges from 1 to 12 hours and caps what `DurationSeconds` may request. Two exceptions matter. Credentials that EC2 delivers through an instance profile are not subject to that setting, and sessions assumed by AWS services are not either. And when you use the credentials from one role to assume a second role, called role chaining, "the role's session duration is limited to one hour", regardless of the maximum session duration configured on the target role. That one-hour ceiling applies to console role switching, the AWS CLI and the API alike, and it does not apply to the first assumption from user credentials or to an EC2 instance profile. A pipeline that hops through three accounts therefore needs refresh logic, not a 12-hour session.

`AssumeRoleWithSAML` and `AssumeRoleWithWebIdentity` are unsigned calls: the caller has no AWS credentials, only an assertion or token, which AWS validates against the registered provider. `GetSessionToken` requires no permission to call, because its job is to authenticate rather than authorize, and its credentials cannot call IAM APIs unless MFA information was included. `GetFederationToken` produces a federated user session whose permissions are the intersection of the calling user's policy and the passed session policy. Three read-only operations round out the service: `GetCallerIdentity`, which needs no permission and answers "which identity am I", `DecodeAuthorizationMessage`, which expands the encoded message in an authorization failure, and `GetAccessKeyInfo`.

STS also has an endpoint question that older notes get wrong. AWS recommends Regional endpoints such as `https://sts.eu-west-1.amazonaws.com` over the legacy global endpoint `https://sts.amazonaws.com`, "to reduce latency, build in redundancy, and increase session token validity". Validity here means which Regions will accept the token, not how long it lasts: a version 1 token from the global endpoint is rejected by Regions that are disabled by default, while a token from a Regional endpoint, or a version 2 token, is accepted everywhere. The lifetime is set by the duration parameter and is unaffected. The global endpoint is hosted only in US East (N. Virginia) and does not fail over. Tokens from Regional endpoints are valid in all Regions; tokens from the global endpoint are valid only in Regions enabled by default unless the account sets version 2 tokens with `SetSecurityTokenServicePreferences`. Some newer operations, including the root session call described later, refuse the global endpoint entirely. The default STS request quota is 600 requests per second per account per Region, shared across the credential operations, and calls AWS service principals make on your behalf do not consume it.

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::222222222222:role/AuditReader \
  --role-session-name audit-2026-09 \
  --external-id 7f3c1a9b \
  --duration-seconds 3600
```

## Cross-account access patterns

There are two ways to let a principal in account A reach a resource in account B, and choosing between them is a recurring question. The resource-policy path names the external principal directly in the resource's own policy, so account B's bucket policy lists `arn:aws:iam::111111111111:role/Analytics` and account A's identity policy allows `s3:GetObject` on that bucket. It is the right shape when the sharing is narrow: one bucket, one key, one queue, one topic. The role path creates a role in account B whose trust policy names account A, gives that role the permissions it needs, and lets account A's principals call `sts:AssumeRole`. It is the right shape when the external party needs several resources or when account B wants one auditable place to review and revoke the grant.

A trust policy is short and specific. Naming the whole account as the principal delegates the decision to account A's administrators, who must still grant `sts:AssumeRole` in an identity policy; naming a specific role ARN keeps both ends explicit.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::111111111111:role/Analytics"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "Bool": {"aws:MultiFactorAuthPresent": "true"},
      "StringEquals": {"sts:ExternalId": "7f3c1a9b"}
    }
  }]
}
```

When the other party is a third-party vendor rather than an account you own, the trust policy should require an external ID. Its purpose is to prevent the confused deputy problem: a vendor that holds role ARNs for many customers could be tricked into using its privileged position against the wrong one. The vendor generates a unique value per customer, you put it in the trust policy, and the vendor sends it with every `AssumeRole` call. AWS is explicit that the external ID is not a secret, that it "must be generated by Example Corp and not their customers", and that a vendor should test whether a customer's role can be assumed without it and refuse to onboard until the condition is in place. Values run from 2 to 1,224 characters.

Two mechanisms improve accountability once a session exists. Session tags, passed at assumption time, carry attributes such as department into the session and drive ABAC decisions; up to 50 may be passed. Source identity, set with `sts:SourceIdentity`, records the original human behind a chained set of roles, cannot be changed by the session, and appears in **AWS CloudTrail**, the API activity audit service, which is how a pipeline answers "which person did this" after three role hops.

Remember the exceptions from the evaluation logic when the shared resource is encrypted. An S3 object encrypted with a customer managed KMS key needs an allow in three places: the bucket policy, the reader's identity policy, and the KMS key policy, because a key policy must explicitly allow the principal. A cross-account grant that works for unencrypted objects and fails after encryption is enabled is nearly always the missing key policy. For workforce access across many accounts, the scalable alternative to hand-written trust policies is IAM Identity Center permission sets, cross-linked above.

## Roles for services, ingestion paths and migration tools

Most AWS workloads never see a credential. An instance profile is a container that holds one IAM role and attaches it to an EC2 instance; the instance metadata service vends and refreshes the role's temporary credentials, and the AWS SDKs and AWS CLI find them automatically. Require Instance Metadata Service Version 2, whose session-oriented design, in which a `PUT` request obtains a token that every later `GET` must carry and whose response hop limit defaults to 1, adds defense in depth against open firewalls, reverse proxies and server-side request forgery. The equivalents elsewhere are the Lambda execution role, the task role in **Amazon Elastic Container Service (Amazon ECS)**, the managed container orchestrator, and the service account role in **Amazon Elastic Kubernetes Service (Amazon EKS)**, the managed Kubernetes service. None of them should be replaced by an access key stored in an environment variable or a configuration file.

A service role is a role your account creates and hands to an AWS service so the service can act for you, and handing it over requires a distinct permission: `iam:PassRole`. AWS is direct about why. "To pass a role (and its permissions) to an AWS service, a user must have permissions to pass the role to the service. This helps administrators ensure that only approved users can configure a service with a role that grants permissions." Without it, a user who cannot touch S3 could still create a Lambda function with an administrative role and reach S3 through it. Scope `iam:PassRole` to specific role ARNs and add the `iam:PassedToService` condition key to pin which service may receive them. Two facts catch people out: `PassRole` is a permission and not an API call, so it never appears in CloudTrail on its own, and it works only within one account.

```json
{
  "Effect": "Allow",
  "Action": ["iam:GetRole", "iam:PassRole"],
  "Resource": "arn:aws:iam::111122223333:role/dms-*",
  "Condition": {"StringEquals": {"iam:PassedToService": "dms.amazonaws.com"}}
}
```

A service-linked role is different again. It is predefined by the service, linked to it, and carries exactly the permissions that service needs; you cannot edit its policies, and you can usually delete it only after the service's resources are gone. It is also exempt from both service control policies and resource control policies, so an organization cannot use either to constrain what a service does through its service-linked role.

Securing an ingestion endpoint is the same toolkit applied to a data path. A producer writing to **Amazon Kinesis Data Streams**, the managed streaming data service, to **Amazon Data Firehose**, formerly Kinesis Data Firehose, the managed delivery stream service, or to an S3 landing prefix should use a role rather than a key, scoped to that one stream or prefix. The receiving resource adds a resource policy or, for a stream, a key policy on its encryption key. Network path and identity are then combined: route the traffic through an interface or gateway VPC endpoint in **Amazon VPC**, the isolated virtual network service, and add `aws:SourceVpce` or `aws:SourceVpc` conditions so the resource refuses requests that arrive any other way, with `aws:SecureTransport` enforcing TLS. The delivery stream itself needs a service role to write to its destination bucket and to any KMS key involved. That combination, a narrow producer role, a resource policy, an endpoint condition and a service role on the delivery path, is what "secure access to ingestion access points" means on the exam.

Migration tooling follows the same pattern with an extra wrinkle: it usually spans two accounts and an on-premises network. **AWS Database Migration Service (AWS DMS)**, the managed database replication service, **AWS DataSync**, the managed online data transfer service, and **AWS Application Migration Service**, which replicates whole servers into AWS, each run under service roles you pass to them, and each needs KMS permissions when the source or target is encrypted. Agents running on-premises should not hold IAM user keys. The supported mechanism is IAM Roles Anywhere, which exchanges a certificate issued by a certificate authority you register as a trust anchor for ordinary temporary credentials, so the same roles and policies work outside AWS; **AWS Private Certificate Authority (AWS Private CA)**, the managed private CA service, can issue those certificates. Devices in the **AWS Snow Family**, the physical data transfer appliances, are treated the same way. The rule for any migration question is that the tool needs an allow in both accounts plus the key policy, and that a long-lived access key on a migration agent is the wrong answer.

## Auditing least privilege: Access Analyzer, credential reports and last accessed

**IAM Access Analyzer** is the service that answers "who can actually reach this", and it now has three kinds of analyzer plus three authoring aids. An external access analyzer applies automated reasoning to resource policies inside a zone of trust, which is either one account or an organization, and reports every resource reachable by a principal outside it. External access analysis, policy validation and policy generation carry no charge; internal access analyzers, unused access analyzers and custom policy checks are billed. It covers S3 buckets, IAM roles, KMS keys, Lambda functions, SQS queues, Secrets Manager secrets, SNS topics, snapshots from **Amazon Elastic Block Store (Amazon EBS)**, the block storage service, and **Amazon Relational Database Service (Amazon RDS)**, the managed relational database service, ECR repositories, file systems in **Amazon Elastic File System (Amazon EFS)**, the managed shared file service, and DynamoDB tables and streams. External access findings are Regional, so create the analyzer in each Region you use. An internal access analyzer answers the opposite question for selected business-critical resources: which principals inside the organization can reach them, and by what path. An unused access analyzer continuously reviews last accessed data for every role and user in the organization and reports unused roles, unused access keys, unused passwords, and unused services and actions on identities that are still active; its findings are not Regional, so one analyzer is enough. Charging follows the same split: unused access is billed per role and user analyzed per analyzer per month, internal access per resource monitored, and custom policy checks per API request.

The authoring aids sit in the policy editor and in automation. Policy validation runs more than 100 checks against policy grammar and AWS best practices and returns four categories of finding: errors, security warnings, general warnings and suggestions. Custom policy checks let a pipeline enforce a written standard with three API operations: `CheckNoNewAccess` compares a proposed policy with the current one and fails if it grants anything new, `CheckAccessNotGranted` fails if a named critical action is allowed, and `CheckNoPublicAccess` fails if a resource policy would make a resource public. Running these in a pull request is how an organization stops privilege creep before deployment rather than detecting it afterward. Policy generation reads CloudTrail for a chosen window and writes a fine-grained policy from the activity it finds, which is the standard way to replace an over-broad starting policy with a real one.

Two older reports remain examinable. The credential report is an account-wide CSV listing every user with the state of their passwords, access keys, MFA devices and signing certificates, including `password_last_used`, `access_key_1_last_rotated` and `access_key_1_last_used_date`. It can be regenerated once every four hours, and a request inside that window returns the existing report. Last accessed information, shown in the console as Access Advisor, reports which services and which management actions an identity or policy has actually reached and when, with a tracking period of at least 400 days for services. The management account can run the same report against an organizational unit or account to see what an SCP is really permitting. Its limits matter: it includes attempts rather than only successes, it reflects only identity-based policies and SCPs, it does not track `iam:PassRole`, and it covers management events rather than data plane events. CloudTrail remains the authoritative record of who called what.

## Credential hygiene, root access management and the limits that bite

Long-lived access keys are the credential AWS now steers away from. The guidance is explicit that "Where possible, we recommend relying on temporary credentials instead of creating long-term credentials such as access keys", and the remaining sanctioned uses are narrow: a workload that genuinely cannot assume a role, such as a plugin in third-party software, a third-party client that does not support IAM Identity Center, and a few service-specific credential types. Where keys must exist, each user may hold two, rotation means creating the second key, moving every caller, verifying through last-used data, then deleting the first, and the practical discipline is to never commit a key, never share one, and let the unused access analyzer find the ones nobody retired. A key belongs to a user and carries that user's full permissions, so a leaked key is a leaked identity.

In an organization, the root user of every member account is a standing risk that centralized root access is designed to remove. With trusted access enabled for IAM in AWS Organizations, the feature has two halves. Root credentials management lets the management account or a delegated administrator delete a member account's root password, access keys and signing certificates and deactivate its MFA; after that "Member accounts can't sign in to their root user or perform password recovery for their root user", and new accounts created in the organization have no root credentials at all. Privileged root actions let the same accounts perform the few tasks that still need root, through short sessions created with `sts:AssumeRoot`. Those sessions run at most 900 seconds, must go to a Regional STS endpoint, and must carry exactly one of five AWS managed task policies: `IAMAuditRootUserCredentials`, `IAMCreateRootUserPassword`, `IAMDeleteRootUserCredentials`, `S3UnlockBucketPolicy` and `SQSUnlockQueuePolicy`. That last pair is the answer to the classic lockout, a bucket or queue policy that denies everyone including its owner. Every root session is recorded in CloudTrail. Where root credentials still exist in member accounts, an SCP denying root actions is the preventive control, and **AWS Config**, the resource configuration and compliance service, has managed rules for root MFA and root access keys.

A few quotas change designs rather than just failing a call. A managed policy holds 6,144 characters and inline role policies 10,240, and only 20 managed policies may attach to a role and 10 to a user, both raisable on request to 25 and 20, and 10 to a group, so a growing permission set eventually has to be split. A role trust policy holds 2,048 characters by default, raisable to 8,192, which constrains how many principals one role can name before `aws:PrincipalOrgID` becomes necessary. A session may carry one JSON session policy plus up to 10 managed policy ARNs within 2,048 combined characters. The defaults of 1,000 roles, 1,500 customer managed policies and 300 groups per account are adjustable; the 5,000 users, 2 access keys, 10 groups per user and 8 MFA devices per user are not.

## Professional depth

Delegation is the first thing that changes at scale. A platform team cannot review every role a hundred product teams need, so it delegates role creation and caps the result with permissions boundaries. The pattern is a policy that allows `iam:CreateRole` and `iam:AttachRolePolicy` only when the `iam:PermissionsBoundary` condition key equals a specified boundary ARN, plus a deny on `iam:DeleteRolePermissionsBoundary` and on modifying the boundary policy itself. Developers then create whatever roles their workloads need and cannot exceed the ceiling. The same policy usually pins a role path, so boundary-constrained roles are distinguishable from platform roles in later audits.

Auditing scales the same way. Create the external and unused access analyzers with the organization as the zone of trust, register a security account as the delegated administrator for IAM Access Analyzer, and treat findings as a work queue rather than a dashboard: archive rules suppress known-good external grants such as an approved partner account, and everything else becomes a ticket. Feed the findings into **AWS Security Hub**, the findings aggregation and posture service, alongside the other detective controls. Then push the checks left: `CheckNoNewAccess` and `CheckAccessNotGranted` in the deployment pipeline stop a policy that would grant new or forbidden access before it reaches an account, which is a far cheaper control than detecting the same grant afterward.

Organization policies need testing discipline because they are blunt. AWS warns against attaching an RCP to the organization root "without thoroughly testing the impact", and the recommended path is one test account, then a low organizational unit, then upward, watching CloudTrail for access-denied events at each step. Two exemptions shape designs. RCPs never apply to the management account or to service-linked roles, so a management account running workloads is outside your own guardrails and a service that acts through a service-linked role cannot be constrained this way. Together SCPs and RCPs implement a data perimeter: an SCP saying principals in my accounts may only reach my resources, an RCP saying my resources may only be reached by my principals, and VPC endpoint policies saying my networks may only carry traffic to both.

Multi-hop automation runs into STS behavior. A deployment pipeline that assumes a hub role and then a spoke role in each target account is role chaining and gets one hour per session no matter how the target role is configured, so long-running jobs must refresh rather than hold. Set `sts:SourceIdentity` on the first hop and require it in downstream trust policies, so CloudTrail attributes the final action to a person rather than to a nameless session. Point clients at Regional STS endpoints so a hub Region incident does not stop credential issuance elsewhere, and watch the 600 requests per second per account per Region quota when a fan-out job assumes thousands of roles; only the calling account's quota is consumed for a cross-account `AssumeRole`.

Quotas and consistency also cause failures that look like permission bugs. A policy that grew past 6,144 characters must be split rather than extended, and a trust policy listing dozens of account principals should become one `aws:PrincipalOrgID` condition. Eventual consistency means a newly created role can fail its first `AssumeRole`, so provisioning code needs retries.

## Worked scenario

A financial services company runs 60 accounts under one organization: a security account, a shared services account, and production and non-production accounts per business unit. Employees sign in through the corporate identity provider. A data platform team ingests transaction files from branch systems into a landing bucket, and a partner analytics vendor needs read access to a curated prefix. A migration is underway that moves three on-premises databases into Amazon RDS. Auditors require evidence that no identity holds permissions it does not use.

Workforce access goes through IAM Identity Center federated to the corporate directory, with permission sets for the common job functions and account access manager used for the two teams that need custom trust policies and ABAC role tags. No human has an IAM user. Each application uses a role attached to its compute: instance profiles with Instance Metadata Service Version 2 for EC2, execution roles for Lambda. Branch systems write to the landing bucket through a role obtained with IAM Roles Anywhere from certificates issued by AWS Private CA, and the bucket policy requires `aws:PrincipalOrgID`, denies `aws:SecureTransport` false, and restricts in-cloud readers to the VPC endpoint with `aws:SourceVpce`. Migration agents use service roles passed with `iam:PassRole` scoped by `iam:PassedToService` to `dms.amazonaws.com`, with matching grants on the KMS key in the target account.

The vendor assumes a role in the data account whose trust policy names the vendor's account, requires the external ID the vendor generated, and whose permissions policy allows only `s3:GetObject` on the curated prefix; the curated bucket's KMS key policy allows that role to decrypt. An SCP denies Regions outside the approved list and denies member-account root actions, an RCP on the data organizational unit denies S3 and KMS access from any principal outside the organization other than the vendor's account, and centralized root access has removed root credentials from every member account, leaving `sts:AssumeRoot` from the security account for the two unlock task policies. Organization-wide external, internal and unused access analyzers run from the security account, `CheckNoNewAccess` runs in the policy pipeline, and CloudTrail with source identity ties every action back to a person. When the exam asks about this scenario, the keyed answer is federated temporary credentials through Identity Center, roles rather than keys for every workload, a role plus external ID for the third party, resource policies and KMS key policies on both sides of every cross-account path, organization policies as the guardrail, and IAM Access Analyzer unused access findings as the least-privilege evidence.

## Exam lens

- "Applications on EC2 need credentials to call AWS" maps to an instance profile with a role; storing access keys on the instance or in user data is the distractor.
- "Grant an application in another account access to one S3 bucket" maps to a bucket policy naming the external principal plus an identity policy in the caller's account; either alone fails the two-account rule.
- "A third-party vendor will manage resources in our account" maps to a role whose trust policy requires an external ID, not an IAM user with access keys.
- "No user, including an administrator, may ever do X" maps to an explicit deny, in an SCP when the scope is organization-wide; removing the allow leaves the action reachable by another policy.
- "Restrict a bucket to every account in our organization without listing them" maps to an `aws:PrincipalOrgID` condition; enumerating account IDs is the operationally worse distractor.
- "Permissions must apply automatically to new projects without editing policies" maps to ABAC with `aws:PrincipalTag` and `aws:ResourceTag`; a role for each project is the RBAC distractor.
- "Let developers create roles but never exceed a ceiling" maps to a permissions boundary enforced by the `iam:PermissionsBoundary` condition key; an SCP is the distractor because it applies to the whole account, not to the roles developers create.
- "Identify resources shared outside the organization" maps to an IAM Access Analyzer external access analyzer; the credential report and Access Advisor do not read resource policies.
- "Find permissions and identities that have never been used" maps to an unused access analyzer or last accessed information; external access findings answer a different question.
- "Block a policy change that would grant new access, before deployment" maps to the `CheckNoNewAccess` custom policy check in the pipeline; policy validation only checks grammar and best practices.
- "A bucket policy denies everyone and the owner is locked out" maps to a privileged root session with the `S3UnlockBucketPolicy` task policy, or root sign-in where credentials still exist.
- "Workloads outside AWS need AWS credentials without long-lived keys" maps to IAM Roles Anywhere with a certificate trust anchor, or OIDC federation for a CI system.
- "Deny any request that does not arrive through our VPC endpoint" maps to `aws:SourceVpce` in the resource policy; `aws:SourceIp` does not match endpoint traffic.

## Knowledge check

### 1. Credentials for an application on EC2 (Associate)

A company runs a reporting application on Amazon EC2 instances in an Auto Scaling group. The application reads objects from an Amazon S3 bucket in the same account. The security team requires that no long-term credentials exist on the instances and that credentials rotate automatically.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create an IAM role with a policy allowing `s3:GetObject` on the bucket and attach it to the instances through an instance profile.
- **B)** Create an IAM user with `s3:GetObject` permissions and place its access keys in a file baked into the instance image.
- **C)** Create an IAM user, store its access keys in AWS Secrets Manager, and have the application read the keys at startup.
- **D)** Add a bucket policy that allows `s3:GetObject` from the instances' public IP address range.

<details><summary>Answer</summary>

**Answer: A.** An instance profile delivers the role's temporary credentials through the instance metadata service and refreshes them automatically, so nothing long-lived exists on disk. B embeds a long-term access key in the image, which is the practice the requirement forbids and which spreads with every scaled instance. C still creates and stores long-term keys; Secrets Manager protects them but does not remove them or rotate them into temporary credentials. D authorizes by network address rather than identity, breaks whenever an instance is replaced, and leaves the request with no principal permitted to call the action.

*Where this is covered: Roles for services, ingestion paths and migration tools.*

</details>

### 2. Reading a bucket in another account (Associate)

An analytics application runs under an IAM role in account A. It must read objects from an S3 bucket in account B. The bucket is encrypted with a customer managed AWS KMS key owned by account B. The company does not want to copy the data.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Attach a policy to the role in account A that allows `s3:GetObject` on the bucket, and take no action in account B.
- **B)** Add a bucket policy in account B that allows `s3:GetObject` for the role ARN in account A.
- **C)** Create an IAM user in account B, and give its access keys to the application in account A.
- **D)** Add a statement to the KMS key policy in account B that allows the role in account A to call `kms:Decrypt`.
- **E)** Enable an S3 access control list granting public read on the bucket.

<details><summary>Answer</summary>

**Answer: B and D.** A cross-account request is evaluated twice and must be allowed in both accounts, so account B's bucket policy has to name the role, and because a KMS key policy must explicitly allow a principal, the key policy has to grant decrypt as well. A is only half the requirement and fails in account B. C replaces temporary credentials with long-term keys and hands a credential across an account boundary. E makes the data public, which the scenario never asks for and which S3 blocks by default.

*Where this is covered: How a request is authorized: the policy evaluation logic.*

</details>

### 3. Protecting the account root user (Associate)

A startup has one AWS account. The root user currently has a password and one access key pair used by a nightly script. The security team wants to follow AWS guidance for root user protection while keeping the nightly script running.

Which solution will meet these requirements?

- **A)** Attach a deny-all IAM policy to the root user and keep the access key.
- **B)** Rotate the root access key every 30 days and record the rotation in a runbook.
- **C)** Register MFA for the root user, create an IAM role with only the permissions the script needs, run the script under that role, and delete the root access key.
- **D)** Add the root user to an IAM group that has a restrictive policy attached.

<details><summary>Answer</summary>

**Answer: C.** AWS requires MFA on the root user, recommends that no root access key exist, and directs programmatic work to a role with scoped permissions. A is impossible: no identity-based policy can be attached to the root user, so it cannot be restricted that way inside its own account. B keeps a full-privilege long-term credential in circulation, which rotation does not fix. D is also impossible, because the root user is not an IAM user and cannot be placed in a group.

*Where this is covered: Principals: the root user, users, groups, roles and federated identities.*

</details>

### 4. Letting developers create their own roles (Professional)

A platform team supports 80 product teams in separate accounts. Developers must be able to create IAM roles for their own workloads without raising a ticket, but no role they create may grant permissions outside an approved set, and developers must not be able to escalate their own access. The platform team wants one reusable control.

Which solution will meet these requirements?

- **A)** Grant developers `iam:CreateRole` and review every new role weekly with an IAM Access Analyzer external access analyzer.
- **B)** Attach a service control policy to each account that denies `iam:CreateRole`, and have the platform team create roles on request.
- **C)** Give developers a session policy that limits their permissions when they sign in.
- **D)** Allow `iam:CreateRole` and `iam:AttachRolePolicy` only when the `iam:PermissionsBoundary` condition key matches an approved boundary policy, and deny changes to that boundary.

<details><summary>Answer</summary>

**Answer: D.** A permissions boundary caps what any identity-based policy attached to the new role can grant, and conditioning role creation on the boundary makes the cap mandatory rather than advisory. A is detective rather than preventive and an external access analyzer reports cross-account and public exposure, not over-broad internal permissions. B removes the self-service the scenario requires. C narrows one developer session but places no limit on the roles that developer creates, which is where the escalation path is.

*Where this is covered: Policy documents and the six policy types.*

</details>

### 5. Granting a monitoring vendor access (Associate)

A company hires a cost optimization vendor that will read resource metadata in the company's AWS account. The vendor serves hundreds of customers from its own AWS account. The security team wants to prevent the vendor from being tricked into using the company's access on behalf of another customer.

Which solution will meet these requirements?

- **A)** Create an IAM user for the vendor and send the access keys over an encrypted channel.
- **B)** Create an IAM role with read-only permissions whose trust policy names the vendor's account and requires the `sts:ExternalId` value the vendor issued for this company.
- **C)** Create an IAM role whose trust policy allows any principal, and rely on the permissions policy to limit access.
- **D)** Add the vendor's account to a bucket policy with `aws:PrincipalOrgID` set to the company's organization.

<details><summary>Answer</summary>

**Answer: B.** The external ID is the documented defense against the confused deputy problem, and it must be generated by the vendor and asserted on every `AssumeRole` call. A hands out a long-term credential and gives the vendor a durable identity inside the account. C trusts every principal in AWS, so anyone who learns the role ARN can assume it. D is the wrong direction entirely: `aws:PrincipalOrgID` admits members of the company's own organization, and the vendor is outside it.

*Where this is covered: Cross-account access patterns.*

</details>

### 6. Permissions that follow new projects (Associate)

An engineering organization starts new projects every few weeks. Each project has its own EC2 instances and S3 prefixes, and members must access only their own project's resources. Administrators currently edit a policy every time a project or resource is added, and they want that work to stop.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create one IAM group per project and add each engineer to the correct group.
- **B)** Create one IAM role per project and list each project's resource ARNs in its permissions policy.
- **C)** Tag principals and resources with a project key, and write one policy that allows the action when `aws:PrincipalTag/project` matches `aws:ResourceTag/project`.
- **D)** Give every engineer a permissions boundary that names the project's resources.

<details><summary>Answer</summary>

**Answer: C.** This is attribute-based access control: permissions follow the tags, so a new project or a new resource needs a tag rather than a policy edit. A and B are both role-based designs whose policies must be rewritten every time a resource or project appears, which is the cost the scenario asks to remove. D uses a boundary as if it granted access; a boundary only caps permissions and would still have to be edited for every new resource.

*Where this is covered: Conditions, ABAC and the shape of least privilege.*

</details>

### 7. A deployment pipeline that loses its session (Professional)

A deployment tool runs in a tooling account. It assumes a hub role in a security account, then from that session assumes a deployment role in each of 40 target accounts. Some deployments run for three hours and fail partway through with expired credentials. Each deployment role already has its maximum session duration set to 12 hours, and the company must keep the two-hop design for auditability.

Which solution will meet these requirements?

- **A)** Have the tool refresh its credentials during long deployments, because the second assumption is role chaining and is capped at a one-hour session regardless of the role setting.
- **B)** Raise the maximum session duration on the hub role to 12 hours so that it applies to the chained session.
- **C)** Switch the tool from the AWS STS global endpoint to a Regional endpoint, which issues longer-lived tokens.
- **D)** Remove the session policies the tool passes, because a session policy shortens the session lifetime.

<details><summary>Answer</summary>

**Answer: A.** AWS states that when you use credentials from one role to assume another, "the role's session duration is limited to one hour", and that limit applies to the console, the AWS CLI and the API alike, so long jobs must refresh rather than hold one session. B misstates the mechanism: the cap comes from chaining, not from the hub role's setting, and raising it changes nothing. C confuses endpoints with duration; Regional endpoints improve latency, resilience and the Regions a token is valid in, but do not alter session length. D is wrong because a session policy narrows permissions, not lifetime.

*Where this is covered: AWS STS, role assumption and session duration.*

</details>

### 8. Securing a data ingestion endpoint (Associate)

Branch application servers running on EC2 in a private subnet upload transaction files to an S3 landing bucket. Security requires that the upload path never traverse the internet, that only the branch application's identity can write to the landing prefix, and that requests arriving by any other network path are refused.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create an IAM user for the branch application and distribute its access keys to each server.
- **B)** Make the landing bucket public and restrict uploads with a cross-origin resource sharing configuration.
- **C)** Attach a role to the branch servers that allows `s3:PutObject` only on the landing prefix.
- **D)** Allow all principals in the bucket policy and rely on the security group to block other traffic.
- **E)** Create an S3 gateway VPC endpoint and add a bucket policy condition denying requests whose `aws:SourceVpce` is not that endpoint.

<details><summary>Answer</summary>

**Answer: C and E.** The role supplies the identity control scoped to one prefix, and the endpoint condition supplies the network control, keeping traffic off the internet and refusing requests that arrive another way. A distributes long-term keys the scenario's identity requirement rules out. B makes the data public, and cross-origin resource sharing is a browser rule rather than an authorization control. D removes the identity requirement altogether, and a security group filters traffic leaving the instances rather than constraining who may call the S3 API.

*Where this is covered: Roles for services, ingestion paths and migration tools.*

</details>

### 9. Evidence that permissions are not over-granted (Associate)

An auditor asks a company to show which IAM roles and users hold permissions they have not exercised, and which access keys have gone unused. The company wants continuous evidence rather than a one-time review, and wants the least custom work.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Query AWS CloudTrail logs every month and compare the results with attached policies by hand.
- **B)** Run IAM Access Analyzer policy validation on every policy and record the warnings.
- **C)** Generate a credential report every four hours and archive the CSV files.
- **D)** Create an IAM Access Analyzer unused access analyzer for the account and review its findings for unused roles, keys, passwords, services and actions.

<details><summary>Answer</summary>

**Answer: D.** An unused access analyzer continuously reads last accessed data and reports unused roles, unused access keys, unused passwords, and unused services and actions, which is exactly the evidence requested. A rebuilds that analysis manually from raw logs. B checks policy grammar and best practices, which says nothing about whether a permission was used. C reports credential state and last-used dates for users only, missing roles and unused actions entirely.

*Where this is covered: Auditing least privilege: Access Analyzer, credential reports and last accessed.*

</details>

### 10. A perimeter around regulated data (Professional)

A regulated business unit occupies one organizational unit in an AWS organization. Its S3 buckets and AWS KMS keys must never be readable by a principal outside the organization, even if someone in a member account writes a permissive bucket policy. Separately, no principal in those member accounts may call AWS services in Regions outside an approved list. The management account runs no workloads.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Attach a resource control policy to the organizational unit that denies S3 and AWS KMS actions when `aws:PrincipalOrgID` does not match the organization.
- **B)** Attach a resource control policy that denies every AWS service outside the approved Regions.
- **C)** Attach a service control policy to the organizational unit that denies all actions when `aws:RequestedRegion` is not in the approved list.
- **D)** Ask each account owner to add a deny statement to every bucket policy.
- **E)** Enable IAM Access Analyzer external access analyzers and delete any bucket policy that generates a finding.

<details><summary>Answer</summary>

**Answer: A and C.** An RCP bounds what may be done to resources in member accounts, including by principals outside the organization, and S3 and AWS KMS are both on the list of services RCPs support, so a permissive bucket policy cannot override it. An SCP bounds what principals in those accounts may do, which is the right instrument for a Region restriction. B fails because RCPs apply only to a specific subset of services, so they cannot express an all-services Region rule. D depends on every account owner acting correctly forever, which is the condition the scenario says must not be trusted. E is detective, arrives after exposure, and deleting policies automatically would break legitimate access.

*Where this is covered: Policy documents and the six policy types.*

</details>

## Summary

IAM is a sequence of decisions. Decide what kind of principal the scenario has: a workforce human federates through IAM Identity Center, an application end user belongs to Amazon Cognito, a workload on AWS gets a role through an instance profile or execution role, a workload outside AWS gets one through IAM Roles Anywhere or OIDC federation, and an IAM user with access keys survives only where nothing else works. Decide which policy type expresses the requirement: an identity policy for what a principal may do, a resource policy for who may touch one resource, a permissions boundary for delegation, a session policy for one session, and an SCP or RCP for an organization-wide maximum. Then evaluate: an explicit deny anywhere ends the request, RCPs and SCPs must allow, one allow from an identity or resource policy suffices within an account except for role trust and KMS key policies, and a cross-account call needs an allow in both accounts. Scope with conditions, use tags for ABAC where projects change often, keep sessions short and remember the one-hour chaining cap, and prove least privilege with IAM Access Analyzer, credential reports and last accessed data.

## Related units

- [AWS Organizations, IAM Identity Center and AWS Control Tower](organizations-identity-center-and-control-tower.md): account structure, SCP and RCP design, workforce single sign-on and resource sharing
- [AWS KMS and AWS CloudHSM](kms-and-cloudhsm.md): key policies and grants, the second authorization plane for encrypted data
- [Amazon Cognito](cognito.md): authentication for an application's own end users rather than AWS principals
- [AWS Directory Service](directory-service.md): Active Directory integration and when to federate a directory with IAM roles
- [Detection and compliance services](detection-and-compliance-services.md): GuardDuty, Security Hub and Config for detecting and remediating identity risk
- [AWS Secrets Manager and Parameter Store](secrets-manager-and-parameter-store.md): where the credentials that cannot become roles should live
- [Amazon VPC](../04-networking/vpc.md): endpoints, endpoint policies and the network half of a data perimeter
- [Amazon S3](../01-storage/s3.md): bucket policies, access points and Block Public Access in practice

## Sources

- [Centrally manage root access](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html): root credentials management and privileged root actions for member accounts
- [IAM Access Analyzer pricing](https://aws.amazon.com/iam/access-analyzer/pricing/): which analyzer types and authoring aids carry a charge

- [Policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html): how identity, resource, boundary, session, SCP and RCP policies combine
- [How AWS enforcement code logic evaluates requests](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic_policy-eval-denyallow.html): the ordered evaluation and the resource-policy special cases
- [Cross-account policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic-cross-account.html): the two evaluations and the allow-in-both-accounts rule
- [Resource control policies (RCPs)](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html): supported services, RCPFullAWSAccess, and the management account and service-linked role exemptions
- [Security best practices in IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html): temporary credentials, the access key guidance, boundaries and guardrails
- [Root user best practices for your AWS account](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html): root MFA requirement, the 35-day window and no root access keys
- [Centralize root access for member accounts](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-enable-root-access.html): root credentials management and privileged root actions
- [AssumeRoot](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoot.html): the 900 second limit, the five task policies and the Regional endpoint requirement
- [Compare AWS STS credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_sts-comparison.html): caller, duration and restriction table for each STS operation
- [Methods to assume a role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html): role chaining's one-hour cap and the maximum session duration setting
- [Request temporary security credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_request.html): what each STS operation returns and how sessions are created
- [Manage AWS STS in an AWS Region](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_enable-regions.html): Regional endpoints, the global endpoint and version 1 compared with version 2 tokens
- [Access to AWS accounts owned by third parties](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_third-party.html): external IDs and the confused deputy problem
- [Grant a user permissions to pass a role to an AWS service](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html): iam:PassRole, iam:PassedToService and service-linked roles
- [Define permissions based on attributes with ABAC authorization](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction_attribute-based-access-control.html): ABAC compared with RBAC and session tags from an identity provider
- [IAM JSON policy elements: Condition](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition.html): condition operators, the request context and missing-key behavior
- [Using IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html): external, internal and unused access analyzers, policy validation, generation and pricing
- [Delegated administrator for IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-settings.html): who can create organization-wide analyzers and what happens when the delegation changes
- [Validate policies with IAM Access Analyzer custom policy checks](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-custom-policy-checks.html): CheckNoNewAccess, CheckAccessNotGranted and CheckNoPublicAccess
- [Refine permissions in AWS using last accessed information](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_last-accessed.html): Access Advisor tracking period, policy types covered and the PassRole exclusion
- [Generate credential reports for your AWS account](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_getting-report.html): report contents and the four-hour regeneration rule
- [IAM and AWS STS quotas](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html): policy sizes, session policy limits and the STS request quota
- [IAM user groups](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_groups.html): groups cannot nest and cannot be named as a Principal
- [Use the Instance Metadata Service to access instance metadata](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-metadata-v2-how-it-works.html): IMDSv2 session tokens and the defense-in-depth rationale
- [AWS Identity and Access Management endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/iam-service.html): users, groups, roles, access keys and MFA device quotas
- [What is AWS Identity and Access Management Roles Anywhere?](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/introduction.html): trust anchors, profiles and credentials for workloads outside AWS
- [Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/): security of the cloud compared with security in the cloud, and the three control categories
