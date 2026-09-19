# AWS Organizations, AWS IAM Identity Center and AWS Control Tower

**Where it sits on the exams.** **AWS Organizations** is the service that groups many AWS accounts under one management account so you can bill them together and apply central policy to all of them, and **AWS Control Tower** is the opinionated layer on top that builds and governs a standard multi-account environment for you, while **AWS IAM Identity Center** is the workforce sign-in layer that gives one person one login to every account they are entitled to. Together they are the multi-account design that SAA-C03 task 1.1 tests at the level of "which service stops a team doing that in every account" and that SAP-C02 tasks 1.2, 1.4 and 4.2 test at the level of "design the account structure, the guardrails, the logging and the identity flow for a company of this shape". The rule of thumb the exam rewards is that the account is the isolation boundary, Organizations policy is how you put a ceiling on every account at once, Control Tower is how you get that structure without building it by hand, and Identity Center is how humans get in.

## One organization, many accounts

An organization is a collection of AWS accounts arranged in a tree. At the top is a single administrative root, created for you when you create the organization, and there is exactly one root per organization. Beneath the root you create organizational units (OUs), which are groups of accounts, and OUs can contain other OUs. Excluding the root, the hierarchy can be five levels of OUs deep. Every account sits either directly in the root or in exactly one OU, and a member account can belong to only one organization at a time.

The account that creates the organization is the management account, and you cannot change which account holds that role afterward. The management account is the payer for every charge the other accounts incur, and it is the only account that can create member accounts, invite existing accounts, remove accounts, designate delegated administrators, attach policies to roots, OUs and accounts, and turn on integration with other AWS services. Everything else is a member account. The management account does not have to sit directly under the root; you can place it anywhere in the tree.

Organizations offers two feature sets. All features, the default and the recommendation, gives you the full governance surface: policies, service integrations, delegated administration and shared billing. Consolidated billing gives you shared billing and nothing else: no service control policies, no resource control policies, no trusted access. An organization created for billing can be upgraded, but every invited member account has to accept the change, and the request to enable all features expires after 90 days. When a Professional question says an organization "has only consolidated billing enabled" and then asks how to block a service across accounts, the first move is enabling all features, and any answer that attaches an SCP without that step is wrong.

Accounts join in two ways. You create them from the management account with the `CreateAccount` API, in which case they are members immediately and a role in **AWS Identity and Access Management (IAM)**, the service that decides which principal may perform which action on which resource, named `OrganizationAccountAccessRole` is created in the new account trusting the management account. Or you invite an existing standalone account, implemented as a handshake the invited account must accept within 15 days. The default quota is 10 accounts per organization, adjustable up to 50,000. Two limits bite during a large migration: only five member accounts can be created concurrently, and a created account must exist for four days before you can remove it.

Two mechanisms let other AWS services work across the whole organization. Trusted access lets a service, such as **AWS CloudTrail**, the API activity logging service, or **AWS Config**, the configuration recording and compliance service, perform operations in every account in the organization. Delegated administration then registers a named member account as the administrator for one of those services, so that day-to-day work happens outside the management account. Most security and governance services support both, including CloudTrail, AWS Config, **AWS Service Catalog**, the curated product catalog service, **Amazon GuardDuty**, the managed threat detection service, **AWS Security Hub**, the findings aggregation and posture service, **Amazon Macie**, the S3 sensitive data discovery service, **Amazon Inspector**, the vulnerability scanner, **AWS Backup**, the centralized backup service, **AWS CloudFormation** StackSets, the multi-account deployment feature of the infrastructure-as-code service, **AWS Firewall Manager**, which applies firewall policies across an organization, **AWS Systems Manager**, the operations and configuration management service, IAM Identity Center itself and **AWS Trusted Advisor**, which checks accounts against cost, security and resilience best practices. A smaller set supports trusted access but no delegated administrator, notably **AWS Resource Access Manager (AWS RAM)**, the cross-account resource sharing service, **AWS Directory Service**, the managed Microsoft Active Directory service, and AWS Control Tower itself. When a question asks how to run a security service organization-wide without working in the management account, the two-word answer is delegated administrator, and the distractor is a cross-account role in every account.

## Organizational units, inheritance and how a policy decides a request

An OU exists so that one control applies to a subset of accounts. The structure should follow the controls you want to apply, not the company org chart, because moving an account between OUs changes which policies reach it. The default quota is 2,000 OUs per organization and a policy can be attached to an unlimited number of targets.

Policy inheritance runs down the tree, and for authorization policies the arithmetic is intersection, not union. A service control policy (SCP) sets the maximum permissions available to IAM principals in a member account. It never grants anything: "No permissions are granted by an SCP." For a permission to be allowed in an account, an explicit `Allow` for it must appear in the SCPs at every level from the root through each OU on the direct path down to the account, including the account itself. That deny-by-default model is why Organizations attaches an AWS managed SCP named `FullAWSAccess`, which allows every service and action, to the root, every OU and every account when SCPs are enabled. Remove it at any level without replacing it and everything below that level is blocked. A `Deny` behaves the other way: a deny in an SCP at any level from the root down to the account blocks that permission for every account underneath, no matter what is allowed lower down.

That gives two authoring strategies. A deny list keeps `FullAWSAccess` everywhere and adds explicit `Deny` statements for what must never happen, such as leaving the organization, disabling CloudTrail, or creating resources outside approved Regions. This is the common design because it fails open toward new AWS services. An allow list replaces `FullAWSAccess` with a policy naming only the services you sanction, which means every new AWS service is blocked until someone updates the policy. AWS's own guidance warns that relying only on allow statements "can lead to unintended access, because broader or overlapping Allow statements can override more restrictive ones". A short deny-list SCP looks like this:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyLeavingTheOrganization",
      "Effect": "Deny",
      "Action": "organizations:LeaveOrganization",
      "Resource": "*"
    },
    {
      "Sid": "DenyOutsideApprovedRegions",
      "Effect": "Deny",
      "NotAction": ["iam:*", "organizations:*", "cloudfront:*", "route53:*", "support:*"],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {"aws:RequestedRegion": ["eu-west-1", "eu-central-1"]}
      }
    }
  ]
}
```

Three exemptions decide exam questions. SCPs do not affect users or roles in the management account, at all, which is the standing argument for running no workloads there; note that they do apply to member accounts designated as delegated administrators. SCPs do not affect any service-linked role. And SCPs apply to every other principal in a member account including that account's root user, so an SCP is the only way to constrain a member account root user from the outside. Because an SCP is blunt, AWS "strongly recommends that you don't attach SCPs to the root of your organization without thoroughly testing the impact", and the documented method is to move accounts into a test OU one at a time and watch IAM service last accessed data and CloudTrail for the access denied events you did not intend.

Two IAM mechanics are worth restating because questions mix them up. An SCP is a ceiling, so a principal still needs an identity-based policy: an account whose SCP allows everything and whose user has no policy has no access. And a permissions boundary, an SCP and an identity-based policy must all allow an action for it to succeed. The full evaluation order, including how a resource control policy joins in, is taught in [AWS Identity and Access Management](iam.md).

## The Organizations policy types

Organizations sorts its policies into two broad categories. Authorization policies regulate access to APIs and are evaluated as part of the IAM authorization decision. Declarative policies are enforced inside the service's own control plane rather than at the API authorization layer, which is why AWS describes them as "set once and forget": the baseline configuration "is always maintained when the service adds new features or APIs". Read the table for what each type does, whether it grants or only restricts, and what escapes it, because the exemption column is where most wrong answers live.

| Policy type | What it does | Grants or restricts | What it exempts |
|---|---|---|---|
| Service control policy (SCP) | Caps the maximum permissions available to IAM users and roles in member accounts | Restricts only, never grants | The management account entirely, all service-linked roles, and a short list of tasks such as registering for Enterprise Support as the root user |
| Resource control policy (RCP) | Caps the maximum permissions available on resources in member accounts, including access by principals outside the organization | Restricts only, never grants | Resources in the management account, service-linked roles, AWS managed KMS keys, and every service not on the supported list |
| EC2 policy (declarative) | Declares a baseline compute, network and block storage configuration that the service itself enforces on every account in scope | Enforces configuration; blocks non-compliant actions | Nothing structural: it applies to the management account and governs service-linked roles too |
| Backup policy | Pushes AWS Backup backup plans to accounts, combining partial policies down the tree into one effective plan | Configures; does not grant permissions | Applies to the management account; an incomplete effective policy simply fails to back anything up |
| Tag policy | Standardizes tag keys, case treatment and allowed values, and can enforce compliant tagging on named resource types | Configures, and restricts tagging operations only where enforcement is turned on | Untagged resources and tag keys not named in the policy are never evaluated; applies to the management account |
| Chat applications policy | Controls which chat platforms, workspaces, teams and channels can reach the organization's accounts | Restricts | Applies to the management account; validated continuously at runtime rather than at an API boundary |
| AI services opt-out policy | Opts accounts out of AWS AI services storing and using their content for service improvement | Neither: it records a data-use choice | Applies to the management account; opting out deletes historical content held only for service improvement |

The single most testable line in that table is the management account column. SCPs and RCPs do not affect the management account, and everything in the declarative category does. That asymmetry is the reason AWS recommends keeping workloads and resources out of the management account, and it is also why a Control Tower landing zone puts nothing there but the orchestration itself.

The authorization pair is taught in full in [AWS Identity and Access Management](iam.md); what matters here is the division of labor. An SCP is principal-centric and answers "what may principals in my accounts do". An RCP is resource-centric and answers "who may act on the resources in my accounts", including principals who are not in the organization at all. The classic pair is an SCP denying requests to resources outside your organization and an RCP denying requests from principals outside your organization, which together form a data perimeter. Two limits shape the design: RCPs apply only to a published list of services, currently around forty-five including **Amazon S3**, the object storage service, **AWS Key Management Service (AWS KMS)**, the managed encryption key service, **Amazon SQS**, the managed message queue, **AWS Secrets Manager**, the managed secret store, **AWS Security Token Service (AWS STS)**, the temporary credential service, **Amazon DynamoDB**, the managed NoSQL database, **Amazon EventBridge**, the managed event bus, and **Amazon CloudWatch Logs**; and an RCP named `RCPFullAWSAccess` is attached everywhere when you enable the type, cannot be detached, and counts against the quota of five RCPs per entity.

Among the declarative types, EC2 policies are what AWS originally shipped under the name "declarative policies" and they are the ones exam scenarios reach for. They cover **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual machine service, **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated network service, and **Amazon Elastic Block Store (Amazon EBS)**, the block storage service. The supported attributes are VPC Block Public Access, VPC encryption controls, EC2 serial console access, image block public access for Amazon Machine Images, allowed images settings, instance metadata defaults such as requiring IMDSv2, and block public access for EBS snapshots. The two features that go with them are the account status report, which tells you before you attach a policy whether an attribute is already uniform across accounts or inconsistent, and custom error messages, which let a denied action point the user at an internal wiki page instead of the default text. Detach a declarative policy and the attribute rolls back to its previous state.

Tag policies are the type most often mis-remembered. By default a tag policy reports compliance rather than blocking anything; you get enforcement only by turning it on for named resource types, and even then untagged resources and tag keys the policy never mentions are not evaluated. Compliance is inspected through AWS Resource Groups. Backup policies wrap AWS Backup plans in JSON and combine down the tree, so a root policy can set a default frequency that a production OU overrides; the effective plan appears in the AWS Backup console of each account as an immutable plan. Chat applications policies govern **Amazon Q Developer in chat applications**, formerly AWS Chatbot, the service that forwards AWS notifications into Slack, Microsoft Teams and Amazon Chime channels, and they take precedence over per-account role settings and channel guardrails. AI services opt-out policies are a governance answer to "our legal team says no AWS AI service may retain our content".

AWS has kept adding declarative types, and the list now also includes Security Hub policies, Amazon Inspector policies, **Amazon Bedrock**, the managed foundation model service, policies that apply Bedrock Guardrails organization-wide, upgrade rollout policies and Amazon S3 policies. Note which of these the exams know about. The SAA-C03 guide names only service control policies and AWS Control Tower, and the SAP-C02 guide names only AWS Organizations and AWS Control Tower. Neither captured guide mentions resource control policies, declarative policies, tag, backup, chat applications or AI services opt-out policies, so recognize them but expect an exam item to hinge on SCPs.

Sizes and counts occasionally decide a design. An SCP document can be 10,240 characters with 10 attached to any one entity; an RCP is capped at 5,120 characters with 5 per entity; declarative, backup and tag policies get 10,000 characters and 10 per entity; and an AI services opt-out policy gets only 2,500 characters. Policies inherited from above do not count against the per-entity maximum, only those attached directly, and every entity must have at least one SCP attached at all times, which is why you cannot remove the last one.

## AWS Control Tower: the landing zone and its controls

AWS Control Tower orchestrates AWS Organizations, AWS Service Catalog and AWS IAM Identity Center to build a landing zone, "a well-architected, multi-account environment that's based on security and compliance best practices", in less than an hour. Choosing a governance model is a three-way decision. Take Control Tower when you want the prescription and the account vending machine that comes with it; take AWS Organizations on its own when an established structure or a control Control Tower does not express must be preserved; and take Control Tower with customizations layered on when you want both. Control Tower is not only for new environments: you can register an existing organization and enroll its existing accounts, which is the migration path for a company that built its organization by hand.

Setting up a landing zone creates two OUs under the root: a Security OU and, optionally, a Sandbox OU. Into the Security OU it creates or adopts two shared accounts, the Log Archive account and the Audit account. Log Archive is the single destination for the organization CloudTrail trail and AWS Config history, so that no team can tamper with the record of what it did. Audit is the account from which security staff read across the organization and where cross-account notifications aggregate. You may rename the shared accounts or bring existing accounts in as them at launch, but not afterward. Control Tower also stands up an IAM Identity Center directory with preconfigured groups and single sign-on access, unless you self-manage identity. Under the hood, Control Tower deploys resources into accounts using CloudFormation StackSets, one stack instance per account per Region, which is why the StackSets material in [AWS CloudFormation](../08-management/cloudformation.md) is the same machinery a landing zone runs on.

A control, historically called a guardrail, is "a high-level rule that provides ongoing governance for your overall AWS environment", expressed in plain language and applied to an entire OU so that every account in that OU is affected. Controls come in three behaviors, and knowing which AWS mechanism implements each is the highest-yield Control Tower fact on either exam. Preventive controls stop the action happening and are implemented using service control policies, resource control policies and declarative policies from AWS Organizations; their status is enforced or not enabled, and they work in all Regions. Detective controls find non-compliant resources after the fact using AWS Config rules; their status is clear, in violation, or not enabled, and they apply only in Regions Control Tower supports. Proactive controls scan resources before they are provisioned and refuse non-compliant ones, using CloudFormation hooks, so they see only what CloudFormation would create; their status is PASS, FAIL or SKIP. Cutting across behavior is guidance: mandatory controls protect Control Tower's own resources, strongly recommended controls encode best practice for a well-architected multi-account environment, and elective controls lock down actions enterprises commonly restrict. Since landing zone version 4.0, mandatory controls are no longer applied by default.

The management account is exempt again, and for the same reason: "The root user and any administrators in the management account can perform work that controls would otherwise deny. This exception is intentional. It prevents the management account from entering into an unusable state." Preventive controls are not applied to it at all, though everything it does is still logged to the log archive account, so the control there is detective rather than preventive.

Regions matter more in Control Tower than anywhere else in this unit. The Region you are signed into when you create the landing zone becomes the home Region, and you cannot change it afterward. You then choose additional governed Regions. Opting out of a Region does not stop anyone deploying resources there; it only means those resources sit outside governance, which is why the Region deny control exists both as a landing zone setting and at the OU level. Extending the landing zone into a new Region updates the landing zone but not the accounts inside your OUs, so you must re-register each OU before new detective controls work there.

There is no additional charge for AWS Control Tower itself, nor for AWS Organizations or IAM Identity Center. You pay for the services the landing zone turns on: AWS Service Catalog, CloudTrail, AWS Config, **Amazon CloudWatch**, the monitoring service, **Amazon Simple Notification Service (Amazon SNS)**, the publish-and-subscribe messaging service, Amazon S3 and Amazon VPC, billed on usage. AWS Config dominates that bill, because it records a configuration item on every resource change, so an account full of short-lived instances costs far more to govern than a stable one of the same size. The Control Tower account quota is 10,000 and is not adjustable.

## Account Factory, customizations and drift

Account Factory is the account vending machine: "a configurable account template that helps to standardize the provisioning of new accounts with pre-approved account configurations". It is built as an abstraction over provisioned products in AWS Service Catalog, and it both creates and enrolls accounts, applying controls and policies automatically. Identity Center users who provision accounts must be in the `AWSAccountFactory` group or the management group. Enrolling an existing account requires the `AWSControlTowerExecution` role in it, which is the detail a migration scenario hangs on.

Three customization mechanisms sit above Account Factory and the exam expects you to tell them apart. Account Factory Customization (AFC) applies a blueprint at provisioning or enrollment time, where a blueprint is a CloudFormation or Terraform template stored as a Service Catalog product in a hub account that AWS strongly recommends should not be the management account. AFC deploys "to the home Region only, or to all Regions governed by AWS Control Tower", with nothing in between, and one blueprint per account. Customizations for AWS Control Tower (CfCT) is the pipeline approach: a CloudFormation-deployed solution that reads a manifest and deploys your own CloudFormation templates, service control policies and resource control policies to named accounts and OUs, wired into Control Tower lifecycle events so a newly vended account receives its resources automatically. Account Factory for Terraform (AFT) is the Terraform-native equivalent. All three are current, and AFT is still gaining features, such as re-applying an account's customizations when it moves to a different OU. What a Professional question wants is the selection rule. Use AFC when a single blueprint per account is enough and you want no pipeline to maintain, CfCT when you want CloudFormation and policy customizations driven from a repository, and AFT when Terraform is already the organization's tool of record.

Drift is Control Tower's word for divergence from the configuration it established, and it is a routine operations task rather than an error. Control Tower detects it automatically, scanning its managed SCPs, RCPs and declarative policies daily, and surfaces member account drift through the `aws-controltower-AggregateSecurityNotifications` topic in the audit account, with landing zone 4.0 and later sending drift notifications to Amazon EventBridge in the management account, de-duplicated so the same drift notifies once until it is remediated. Typical drift is an account moved between OUs, an account removed from the organization, a managed SCP edited, or a managed SCP detached from an OU. Four kinds must be fixed at once: deleting the Security OU, and deleting the `AWSControlTowerAdmin`, `AWSControlTowerCloudTrailRole` or `AWSControlTowerStackSetRole` roles. Both force a landing zone reset.

## IAM Identity Center: identity sources, permission sets and propagation

IAM Identity Center, renamed from AWS Single Sign-On in 2022 and still carrying the `sso` and `identitystore` API namespaces, connects a workforce to AWS accounts and to AWS managed applications. There are two instance types and the distinction matters. An organization instance is deployed in the Organizations management account and is "the only instance that enables you to manage access to AWS accounts". An account instance, which suits OIDC customer managed applications and simpler single-account scenarios as well as select AWS managed applications, is bound to a single account and exists only to support isolated deployments of select AWS managed applications. If a scenario involves signing people in to many accounts, it needs an organization instance, and an answer that proposes an account instance is wrong.

The identity source is where users and groups actually live, and there are three options. The built-in Identity Center directory is the default and needs nothing else. Active Directory connects an existing directory through AWS Directory Service, either AWS Managed Microsoft AD or an AD Connector to an on-premises domain, and is covered in [AWS Directory Service](directory-service.md). An external identity provider connects a third-party IdP such as Okta, Microsoft Entra ID or Ping over SAML 2.0. That last option is the answer to the SAP-C02 skill of integrating with third-party identity providers: Identity Center gives you "one point of federation", meaning one SAML trust and one certificate to manage for every account and every AWS managed application, instead of a SAML identity provider object and a federated role in each account. The older per-account pattern is still worth knowing because a question may present both; its mechanics live in [AWS Identity and Access Management](iam.md).

Users and groups get into Identity Center from an external IdP through SCIM 2.0 automatic provisioning. You generate a SCIM endpoint and a bearer token in Identity Center and configure them at the IdP. The details that decide questions: the access token is valid for one year, AWS starts reminding you 90 days out, and if it expires, synchronization stops silently while sign-in keeps working. Every user must have a first name, last name, user name and display name or they are not provisioned. Multi-value attributes such as a second email address fail to synchronize, and users not assigned to the IdP application cannot be provisioned at all. The attribute your IdP sends as the SAML `Subject` `NameID` must be the one you map to `Username` in SCIM, or sign-in fails. Once SCIM is configured you can no longer add or edit users in the Identity Center console, and the IdP controls the timing, so "changes are only reflected in IAM Identity Center after your identity provider sends those changes".

A permission set is the unit of AWS account access: "a template that you create and maintain that defines a collection of one or more IAM policies". Assign a permission set to a user or group in a target account and Identity Center creates an IAM role in that account, attaches the policies, and keeps the role in sync as you edit the permission set. That is the whole trick, and it is why the answer to "how do we give 60 developers the same access in 40 accounts without creating 2,400 roles" is one permission set assigned to one group across an OU. A permission set can carry AWS managed policies, customer managed policies, one inline policy and a permissions boundary. Session duration defaults to one hour and can be set up to 12 hours. The quotas that shape large deployments are 3,500 permission sets per instance, 500 provisioned permission sets per account, 100 groups per permission set per account, and 7,000 AWS accounts and 7,000 applications per instance.

Attributes for access control turn identity attributes into session tags. Select an attribute such as Department and Identity Center passes it into the target account as a session tag you reference with the `aws:PrincipalTag/{tag-key}` condition key in any IAM policy type. With an external IdP you can map attributes in Identity Center or have the IdP send them in the SAML assertion as `https://aws.amazon.com/SAML/Attributes/AccessControl:{TagKey}`; where both exist, the Identity Center mapping wins. This is how one permission set serves many teams.

Trusted identity propagation is the newer capability and the one most likely to be misremembered. It adds identity context to an IAM role session so that the user, not the role, is what a downstream AWS service authorizes and logs. A person signs in to **Amazon Quick**, formerly Amazon QuickSight, the serverless business intelligence service, which requests data from **Amazon Redshift**, the managed data warehouse; Redshift verifies the identity with Identity Center, compares the user's group memberships with what its own permissions require, and records the user identifier in CloudTrail and its service logs. The benefit is stated plainly: administrators "can audit who accessed what data by looking at service logs or AWS CloudTrail". For a third-party or customer-developed application, you configure a trusted token issuer so the application's own IdP tokens can be exchanged for Identity Center identity context. When a question asks how to attribute data-lake queries to named people rather than to a shared role, trusted identity propagation is the answer and a per-team IAM role is the distractor.

Changing the identity source is destructive and the exam likes the consequences. The documented warning is that the change "removes any user and group assignments that you configured in IAM Identity Center" and "will also remove permission set IAM roles from your AWS accounts", which can break KMS key policies and Amazon EKS cluster config maps that reference those role ARNs. Switching to or from Active Directory additionally deletes users and groups from the Identity Center directory and changes the Identity Store ID, which changes the AWS access portal URL your workforce has bookmarked. Switching from an external IdP back to Identity Center preserves assignments, and switching between two external IdPs preserves them as long as the new provider sends matching assertions. Multi-Region replication of an instance is supported with the Identity Center directory or an external IdP but not with Active Directory.

## Sharing resources with AWS RAM

AWS RAM lets one account create a resource and let other accounts use it as though it were their own, without duplicating it and without writing a resource policy that enumerates account IDs. You create a resource share naming a Region, the resources, the principals, and a managed permission per resource type that sets the maximum the consuming accounts can be granted. Principals can be account IDs, an entire organization, specific OUs, or for some resource types named IAM roles and users. The owning account keeps ownership, and the consuming account's own IAM policies and SCPs still apply on top of the share.

Organizations changes the workflow in one important way. Sharing with an account outside your organization starts an invitation the recipient must accept. Once you turn on sharing within your organization, sharing with accounts inside it needs no invitation at all, which is why "enable resource sharing with AWS Organizations" is a step that belongs in the keyed answer of any question about sharing at organization scale. The difference from a plain resource-based policy is worth stating: with RAM you can target an OU instead of listing accounts, and the shared resource shows up natively in the consuming account's console and API results rather than having to be referenced by ARN.

The shareable list spans most of what a shared-services account exists to own. Networking dominates it: VPC subnets, which is the basis of the shared VPC pattern, security groups, transit gateways and their multicast domains, prefix lists, **Amazon VPC IP Address Manager (IPAM)** pools, **AWS Network Firewall** firewalls, policies and rule groups, and **Amazon Route 53**, the managed DNS service, Resolver rules, Resolver query logging configurations, DNS Firewall rule groups and Route 53 Profiles. Capacity follows: EC2 capacity reservations, Dedicated Hosts, placement groups and EBS volumes. The rest covers **AWS License Manager** license configurations, **AWS Private Certificate Authority** certificate authorities, **Amazon Aurora** DB clusters for cross-account cloning, **AWS Glue** catalogs, databases and tables, AWS Backup vaults, Systems Manager advanced parameters, **AWS CodeBuild** projects and **AWS Outposts**. Two mechanics to remember: a resource share holds only Regional resources from its own Region, and global resources sit only in a share created in US East (N. Virginia). There is no charge for AWS RAM itself.

## Consolidated billing and shared discounts

Consolidated billing is the half of Organizations you get even without all features. The management account is the payer and receives one bill covering every member account; member account bills exist but are informational only. Three benefits follow: one bill, easy tracking of charges and combined cost and usage data, and combined usage, which "shares the volume pricing discounts, Reserved Instance discounts, and Savings Plans" across the organization. There is no extra fee for the feature.

The pooling of commitments is the part that appears in exam scenarios. "For billing purposes, the consolidated billing feature of AWS Organizations treats all the accounts in the organization as one account. This means that all accounts in the organization can receive the hourly cost benefit of Reserved Instances that are purchased by any other account." The practical consequence is that a Reserved Instance bought in one account can cover matching usage in a sibling account it was never intended for, and the same pooling applies to **Savings Plans**, the flexible commitment pricing model. Where that is unwanted, for example when a business unit must see only the discounts it paid for, the management account turns Reserved Instance and Savings Plans discount sharing off, per account, on the Preferences page of the Billing and Cost Management console. Commitments never cross organizations: Reserved Instances and Savings Plans "apply only to the AWS Organizations where they're purchased, regardless of which account pays the bill". One more detail bites during divestitures: when a member account leaves an organization it loses access to the AWS Cost Explorer data generated while it was a member, although the management account keeps it and the member regains it if it rejoins. Cost allocation tags, cost categories, budgets and the Cost and Usage Report are taught in [Cost management](../08-management/cost-management.md).

## The recommended account structure, central logging and event notification

AWS's own multi-account guidance, in the whitepaper Organizing Your AWS Environment Using Multiple Accounts, groups the recommended OUs by purpose. The foundational OUs are Security, which "groups AWS accounts that apply security policies, governance and compliance controls across the organization", and Infrastructure, for core networking and shared infrastructure. The application OU is Workloads, holding business accounts for production and non-production, and the experimental OU is Sandbox. Four procedural OUs handle process: Exceptions for workloads that must deviate from the standard model, Transitional for accounts mid-migration, Suspended for accounts deactivated over security or policy, and Policy Staging for testing new organization policies before they reach production. Three advanced OUs cover Individual Business Users, Deployments and Business Continuity. You will not need all of them, and AWS says so. The one firm rule is to keep the Security OU clean: it should hold only the essential security accounts that Control Tower designates, and additional security-related accounts belong in a separate OU.

Inside the Security OU sit the two accounts every design assumes. The Log Archive account "is dedicated to ingesting and archiving all security-related logs and backups", and the objective for it is blunt: immutable storage, "accessed only by controlled, automated, and monitored mechanisms, and built for durability". The Security Tooling account, which Control Tower creates under the name Audit, is "dedicated to operating security services, monitoring AWS accounts, and automating security alerting and response". It is where security operators work, with read-only organization-wide roles the norm and write access tightly limited. It is the natural delegated administrator for CloudTrail, Security Hub, GuardDuty, AWS Config, Macie, Inspector, **Amazon Detective**, the security investigation service, IAM Access Analyzer and Firewall Manager. The split between the two accounts is deliberate: the Security Tooling account is the delegated administrator for CloudTrail, but the S3 bucket holding the organization trail's logs lives in the Log Archive account, "to separate the management and usage of CloudTrail log privileges". The same split applies to AWS Config snapshots and exported GuardDuty findings. In the Infrastructure OU, the Network account owns the shared network, typically an **AWS Transit Gateway**, the regional network transit hub, shared to every workload account with AWS RAM, and the Shared Services account owns things like EC2 Image Builder pipelines and directory services.

Central logging has one canonical mechanism. An organization trail, created by the management account or the CloudTrail delegated administrator, "logs all events for all AWS accounts in that organization" into one S3 bucket, with a folder per organization ID and a subfolder per account ID. A copy appears in every member account, where users can see it but "do not have sufficient permissions to delete organization trails, turn logging on or off, change what types of events are logged, or otherwise change an organization trail in any way". New accounts are added automatically through the `AWSServiceRoleForCloudTrail` service-linked role; accounts that leave stop logging, and their existing log files remain. Two behaviors surprise people: Event history in the console still shows only the signed-in account's own events, and console-created organization trails are multi-Region, so a member must have opted into a Region for its activity to appear. Configuration data follows the same shape through an AWS Config aggregator in the delegated administrator account. Both are developed in [AWS CloudTrail](../08-management/cloudtrail.md) and [Detection and compliance services](detection-and-compliance-services.md).

Organization-wide event notification runs on Amazon EventBridge. On the receiving account, usually Security Tooling, you attach a resource policy to an event bus granting `events:PutEvents` to the whole organization by organization ID rather than to a list of accounts, and on each sending account you create a rule whose target is that central bus. Four constraints decide the answers. A cross-account event bus target created after March 2, 2023 requires an IAM role on the sending side, which the console creates for you and the CLI does not. Events are billed to the sending account as custom events; the receiver pays nothing. Forwarding does not chain: a receiver that sends events on to a third account does not deliver them. And unless a rule's event pattern names the `account` field, it also matches events arriving from other accounts, which is why AWS recommends adding `account` to every rule in an account that accepts organization-wide events.

## Professional depth

Rolling out organization policy is a release process, not a configuration change, and Professional questions test whether you treat it that way. AWS says you should not attach an SCP or an RCP to the organization root "without thoroughly testing the impact", and the documented method is to move one test account into a staging OU, then a low OU, then upward, reading CloudTrail for access denied events at each step. Two asymmetries make that harder than it sounds. Organizations lets you view the effective policy for an OU or account for every declarative type but not for SCPs or RCPs, so the effect of an authorization policy has to be inferred from IAM service last accessed data and from failures rather than read off a screen. And the management account is exempt from SCPs and RCPs but not from declarative policies, so a control validated in the management account may behave differently everywhere else. This is what the Policy Staging OU exists for.

Delegation is how a large organization stops working in the management account. There are two distinct kinds and mixing them up costs marks. A delegated administrator for an AWS service is registered per service, and each service then treats that member account as its organization-wide administrator: Security Tooling for GuardDuty, Security Hub, Macie and Inspector, a networking account for IPAM, a platform account for StackSets. A delegated administrator for Organizations itself is different: you attach a resource-based delegation policy, up to 40,000 characters, to the organization so that a named member account may perform policy actions that are otherwise reserved for the management account, scoped as narrowly as you like. Note the trap in both cases: SCPs and RCPs still apply to a delegated administrator account, because it is a member account. The example AWS gives is worth remembering, an SCP on the Identity Center delegated administrator denying `identitystore:Create*`, `identitystore:Update*` and `identitystore:Delete*` so that nobody can bypass the external identity provider by mutating the identity store directly, with the caveat that the same SCP does nothing in the management account.

Scale runs into quotas in three predictable places. The Organizations control plane throttles per API: `ListAccounts` allows 8 requests per second with a burst of 12 and `CreateAccount` allows 0.1 per second, and Control Tower's own daily scan of managed policies runs with the management account's credentials against the same budget, so automation that enumerates every account on every operation eventually collides with the platform itself. IAM Identity Center tops out at 7,000 AWS accounts per instance, well below the 50,000 accounts Organizations will grant, and provisioning a permission set to all accounts caps at 3,500 accounts per call with three concurrent calls, so a 6,000-account rollout must be batched. And because each assigned permission set becomes an IAM role, the IAM quota of 10 managed policies per role, not the Identity Center quota of 25 per permission set, is the number that bites, and it must be raised in each target account.

Account lifecycle has its own arithmetic, and it appears in divestiture and consolidation scenarios. Within any 30-day window you can close at most 250 member accounts or 20% of your members, whichever is higher, capped at 1,000, with only three closures in progress at a time, and a closed account keeps counting against the organization quota until it is permanently closed. On acquisition, you cannot change which account is the management account, so absorbing another company's organization means removing its members and inviting them into yours, and Reserved Instances and Savings Plans "apply only to the AWS Organizations where they're purchased", so commitments do not survive the move.

Finally, the failure modes worth recognizing on sight. Removing `FullAWSAccess` at any level without a replacement allow blocks everything beneath it, and an allow-list SCP at the root silently blocks every AWS service launched after it was written. Moving an account between OUs in a landing zone is drift, and controls it inherited from the old OU are not removed when they are SCPs or AWS Config rules; only hook-based controls are replaced. While the landing zone is in drift, Account Factory enrollment stops working and you fall back to provisioning through Service Catalog.

## Worked scenario

A European insurer runs 140 AWS accounts that grew organically, one per project, with no organization above them and IAM users in every account. It must now show an auditor that no account can disable logging, that all activity is recorded somewhere no project team can reach, that data stays in two approved Regions, and that staff sign in with the corporate identity provider rather than with local credentials. It also wants the networking team to run one shared transit network instead of 140 VPCs with their own connectivity.

The design starts with an organization in all features mode, because consolidated billing alone would give no policies and no trusted access. AWS Control Tower builds the landing zone: a Security OU holding a Log Archive account and an Audit account, a Sandbox OU, and Workloads OUs for production and non-production, with the 140 accounts invited and then enrolled once each has the `AWSControlTowerExecution` role. Controls go on at the OU level, and the Region deny control restricts activity to the two approved Regions. An SCP denies `cloudtrail:StopLogging` and `organizations:LeaveOrganization`, while an RCP on the Workloads OUs denies access to S3 and KMS resources by principals outside the organization. An organization trail created from the Audit account, registered as the CloudTrail delegated administrator, writes every account's events to a bucket in the Log Archive account where no project team has a role at all.

Identity moves to IAM Identity Center as an organization instance, with the corporate identity provider connected over SAML 2.0 and users and groups arriving through SCIM. Four permission sets, ReadOnly, Developer, Deploy and Break-glass, are assigned to groups across OUs, so all 140 accounts get the right IAM roles created and maintained for them without anyone writing a role. The networking team puts a transit gateway in a Network account in the Infrastructure OU and shares it organization-wide with AWS RAM, which needs no invitations once organization sharing is on. GuardDuty, Security Hub and AWS Config are delegated to the Audit account, which also receives every member account's findings on an event bus whose resource policy trusts the organization ID.

The exam asks this scenario as "which combination of actions meets the audit requirement with the least operational overhead". The keyed answer is to enable all features, deploy a Control Tower landing zone, and create an organization trail delivering to the Log Archive account, with an SCP preventing members from stopping logging or leaving the organization. The attractive wrong answer is deploying a CloudTrail trail and a bucket policy in each of the 140 accounts, which meets the letter of the requirement, costs 140 times the effort, and leaves each project team able to turn its own trail off.

## Exam lens

- "Prevent any account from disabling CloudTrail, even the account administrator" maps to an SCP with an explicit `Deny`. An IAM policy in each account is the distractor, because a local administrator can remove it.
- "The restriction must also apply to the root user of the member account" maps to an SCP. It is the only control that reaches a member account's root user from outside.
- "Our controls do not seem to apply to one account" maps to that account being the management account, which SCPs and RCPs never affect.
- "Set up a compliant multi-account environment quickly, following best practices" maps to AWS Control Tower. Building the organization and SCPs by hand is the distractor when the stem says "least operational overhead".
- "Stop a non-compliant resource from being created by CloudFormation" maps to a proactive control, a CloudFormation hook. A detective control is the distractor, because it reports after the fact.
- "Alert us when a resource drifts out of compliance" maps to a detective control, an AWS Config rule; "block the action outright, in every Region" maps to a preventive control, an SCP, RCP or declarative policy.
- "Restrict access to our S3 buckets to principals in our organization" maps to a resource control policy. An SCP is the distractor, because it constrains your principals, not your resources.
- "One sign-in to many accounts with our existing corporate identity provider" maps to IAM Identity Center with an external IdP over SAML 2.0 and SCIM. An IAM SAML provider and roles in every account is the distractor.
- "Give 200 engineers the same access in 50 accounts" maps to one permission set assigned to a group across an OU.
- "Attribute data warehouse queries to the individual user, not a shared role" maps to trusted identity propagation.
- "Share the transit gateway with every account without inviting each one" maps to AWS RAM with sharing enabled for AWS Organizations.
- "Route all findings to one security account" maps to an EventBridge bus whose resource policy trusts the organization ID, plus a delegated administrator.
- "Share the Reserved Instance benefit with some accounts but not others" maps to turning discount sharing off per account in Billing preferences.
- "Standardize tags across the organization" maps to a tag policy, which only reports unless enforcement is enabled for the resource type.
- "Automatically deploy a baseline stack into every new account" maps to a service-managed StackSet with automatic deployment targeting an OU.

## Knowledge check

### 1. Logging that a project team cannot switch off (Associate)

A media company runs 30 AWS accounts in one organization with all features enabled. Each account has a local administrator who holds the `AdministratorAccess` IAM policy. The compliance team requires that no one in any member account, including that account's root user, can stop CloudTrail logging.

Which solution will meet these requirements?

- **A)** Attach an IAM policy to every user in every member account that denies `cloudtrail:StopLogging`.
- **B)** Attach a permissions boundary that denies `cloudtrail:StopLogging` to every role in every member account.
- **C)** Attach a service control policy to the organization root that denies `cloudtrail:StopLogging`.
- **D)** Enable an AWS Config rule in every member account that detects when a trail is stopped.

<details><summary>Answer</summary>

**Answer: C.** An SCP sets the maximum permissions for every principal in a member account, including that account's root user, and a local administrator cannot remove it because only the management account can detach it. A is wrong because a local administrator can delete or edit any IAM policy in their own account, and it misses the root user. B is wrong for the same reason and because a boundary attaches to a single user or role, so a new role escapes it. D is a detective control: it reports that logging stopped but does not prevent it, and the requirement is that nobody can stop it.

*Where this is covered: Organizational units, inheritance and how a policy decides a request.*

</details>

### 2. A new multi-account environment in a week (Associate)

A retailer has one AWS account and plans to move to roughly 40 accounts over the next year. It wants a standard account structure, a centralized log destination, guardrails applied consistently to every account, and a self-service way for teams to request new accounts. The platform team is small.

Which combination of steps will meet these requirements with the LEAST operational overhead? (Select TWO.)

- **A)** Deploy an AWS Control Tower landing zone and enable the mandatory and strongly recommended controls on the OUs.
- **B)** Provision new member accounts with AWS Control Tower Account Factory.
- **C)** Create an organization in AWS Organizations and write a service control policy for each OU by hand.
- **D)** Create 40 standalone accounts and connect them with cross-account IAM roles.
- **E)** Publish an account request product in AWS Service Catalog backed by a custom AWS Lambda function that calls `CreateAccount`.

<details><summary>Answer</summary>

**Answer: A and B.** Control Tower builds the organization, the Security OU with its Log Archive and Audit accounts, and the control set in one operation, and Account Factory is the self-service account vending machine that applies those controls to each new account automatically. C reaches a similar end state but leaves a small team authoring and maintaining every policy itself. D abandons central governance entirely: no SCPs, no organization trail, no consolidated billing, and 40 sets of credentials. E is a custom build of exactly what Account Factory already manages, and it would still need the landing zone underneath it.

*Where this is covered: AWS Control Tower: the landing zone and its controls.*

</details>

### 3. One place to read every account's API activity (Associate)

A bank with 60 accounts in an organization must deliver every account's CloudTrail events to a single immutable location that no workload team can modify, and it wants new accounts to be covered automatically as they are created.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create a separate CloudTrail trail in each member account and configure each one to write to a shared S3 bucket.
- **B)** Create an organization trail from the management account or the CloudTrail delegated administrator.
- **C)** Enable CloudTrail Event history in the management account and query it for member account events.
- **D)** Deliver the trail's log files to an S3 bucket in a dedicated Log Archive account in the Security OU.
- **E)** Grant every workload account write and delete access to the log bucket so their agents can manage retention.

<details><summary>Answer</summary>

**Answer: B and D.** An organization trail logs all events for all accounts in the organization, adds new accounts automatically through a service-linked role, and cannot be turned off or modified by member accounts. Delivering it to a dedicated Log Archive account separates the management of logging from the storage of logs. A requires 60 trails to configure and leaves each team able to stop its own. C is wrong because Event history shows only the signed-in account's own events, never member account events. E defeats immutability by granting the teams being audited the ability to delete the evidence.

*Where this is covered: The recommended account structure, central logging and event notification.*

</details>

### 4. Corporate credentials for 30 accounts (Associate)

A company authenticates its staff with a third-party SAML 2.0 identity provider. Engineers need console and CLI access to 30 AWS accounts in an organization, with access levels that differ by team. The company does not want to manage credentials in AWS and wants the least operational overhead.

Which solution will meet these requirements?

- **A)** Create IAM users in each account and synchronize passwords from the identity provider nightly.
- **B)** Create an Amazon Cognito user pool federated to the identity provider and issue AWS credentials from an identity pool.
- **C)** Create a SAML identity provider object and a set of federated IAM roles in each of the 30 accounts.
- **D)** Enable IAM Identity Center as an organization instance, connect the identity provider over SAML 2.0 with SCIM provisioning, and assign permission sets to groups.

<details><summary>Answer</summary>

**Answer: D.** Identity Center gives one point of federation, meaning one SAML trust and one certificate, and each permission set assigned to a group creates and maintains the matching IAM role in every target account automatically. A creates long-term credentials in 30 places, which is the opposite of the requirement. B is a real service used for the wrong job: Cognito is for application end users, not workforce access to AWS accounts. C works but means 30 identity provider objects and 30 sets of roles to keep in step, which fails the "least operational overhead" test.

*Where this is covered: IAM Identity Center: identity sources, permission sets and propagation.*

</details>

### 5. A guardrail that one account ignores (Professional)

A company has an SCP attached to the organization root that denies the creation of internet gateways. Every account complies except one, where an administrator continues to create them successfully. That account is the account from which the organization was originally created, and it also runs a legacy reporting application. Audit logs confirm the SCP is attached to the root and has not been modified.

Which explanation and remediation will meet these requirements?

- **A)** The SCP is not inherited by accounts placed directly under the root, so the account must be moved into an OU.
- **B)** SCPs never apply to the management account, so the reporting workload should be migrated to a member account.
- **C)** The account is a delegated administrator, and delegated administrators are exempt from SCPs, so the delegation should be removed.
- **D)** The `FullAWSAccess` policy attached to that account overrides the deny, so it should be detached from the account.

<details><summary>Answer</summary>

**Answer: B.** SCPs affect only member accounts and have no effect on users or roles in the management account, which is precisely why AWS recommends running no workloads there. A is wrong because accounts directly under the root do inherit root-attached SCPs. C is a plausible-sounding inversion of a real fact: SCPs do apply to member accounts designated as delegated administrators. D is wrong because an explicit `Deny` always wins over any `Allow`, so `FullAWSAccess` cannot override it, and detaching the last SCP from an entity is not permitted anyway.

*Where this is covered: The Organizations policy types.*

</details>

### 6. One transit network for the whole organization (Associate)

A networking team owns a transit gateway in a dedicated Network account. Application teams in 80 member accounts of the same organization need to attach their VPCs to it. The team does not want to approve a request for each account.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Enable resource sharing with AWS Organizations, then create an AWS RAM resource share for the transit gateway targeting the organization.
- **B)** Create an AWS RAM resource share for the transit gateway listing all 80 account IDs and accept each invitation.
- **C)** Create a transit gateway in each member account and peer them to the Network account's transit gateway.
- **D)** Attach a resource-based policy to the transit gateway granting `ec2:*` to the organization ID.

<details><summary>Answer</summary>

**Answer: A.** Once sharing within the organization is enabled, a resource share targeting the organization or an OU reaches every member account without invitations, and new accounts in a targeted OU are covered as they appear. B works but requires enumerating 80 accounts and accepting 80 invitations, which is the overhead the stem rules out; invitations are only needed for accounts outside the organization. C multiplies cost and complexity for no benefit. D is wrong because a transit gateway is shared through AWS RAM, not through a resource-based policy on the gateway.

*Where this is covered: Sharing resources with AWS RAM.*

</details>

### 7. A perimeter around company data (Professional)

A pharmaceutical company must ensure two things across its organization. First, principals in its accounts must not be able to copy data to S3 buckets or KMS keys owned by accounts outside the organization. Second, the S3 buckets and KMS keys it owns must not be readable by any principal outside the organization, even if a bucket policy is misconfigured by a team.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Attach a service control policy that denies S3 and KMS actions when `aws:ResourceOrgID` does not match the organization.
- **B)** Attach a permissions boundary to every role in every member account denying cross-account S3 and KMS access.
- **C)** Attach a resource control policy that denies S3 and KMS actions when `aws:PrincipalOrgID` does not match the organization.
- **D)** Enable Amazon Macie in every account to report on buckets shared outside the organization.
- **E)** Attach an AWS Config rule that flags bucket policies granting access to external principals.

<details><summary>Answer</summary>

**Answer: A and C.** The SCP is the principal-centric half, capping what your identities may reach; the RCP is the resource-centric half, capping who may reach your resources, and it applies even when a team writes a permissive bucket policy. Both S3 and KMS are on the list of services that support RCPs. B is wrong because a boundary attaches to one user or role at a time, so a newly created role escapes it, and it cannot constrain access to a resource. D and E are detective: they report exposure after it exists, while the requirement is that it cannot exist.

*Where this is covered: The Organizations policy types.*

</details>

### 8. Stopping a non-compliant resource before it exists (Associate)

A company deploys all infrastructure through AWS CloudFormation in a Control Tower landing zone. It requires that a stack containing an unencrypted Amazon EBS volume fails to deploy rather than being reported afterward.

Which solution will meet these requirements?

- **A)** Enable a detective control on the OU that checks EBS volume encryption.
- **B)** Enable an AWS Config rule with automatic remediation that encrypts the volume after creation.
- **C)** Enable a preventive control implemented as a tag policy on the OU.
- **D)** Enable a proactive control on the OU.

<details><summary>Answer</summary>

**Answer: D.** Proactive controls are implemented as CloudFormation hooks: they scan resources before provisioning and non-compliant resources are not provisioned, which is exactly the stated requirement. A reports after the fact, since a detective control is an AWS Config rule whose status is clear or in violation. B also acts after creation, and an EBS volume cannot be encrypted in place by remediation anyway. C confuses two things: preventive controls are real, but they are implemented with SCPs, RCPs and declarative policies, and a tag policy standardizes tags rather than blocking unencrypted volumes.

*Where this is covered: AWS Control Tower: the landing zone and its controls.*

</details>

### 9. A business unit that wants its own discounts (Associate)

A holding company consolidates billing for four business units in one organization. One unit buys Reserved Instances for its own steady workloads and complains that the discount is being consumed by other units' accounts. The company wants the unit's Reserved Instance benefit to apply only to its own accounts, without splitting the organization.

Which solution will meet these requirements?

- **A)** Move the unit's accounts into their own OU and attach an SCP that denies other accounts from using the Reserved Instances.
- **B)** Turn off Reserved Instance and Savings Plans discount sharing for the other accounts on the Preferences page in the Billing and Cost Management console.
- **C)** Convert the Reserved Instances to Savings Plans, which are not shared across accounts.
- **D)** Create a second organization for the unit and invite its accounts into it.

<details><summary>Answer</summary>

**Answer: B.** Discount sharing is a billing preference the management account sets per account, and turning it off is the supported way to stop a commitment pooling across the organization. A is wrong because Reserved Instance application is a billing behavior, not an API action, so no SCP can influence it. C is wrong because Savings Plans are shared by consolidated billing in exactly the same way as Reserved Instances. D would work but splits the organization, which the stem rules out, and commitments do not cross organizations, so the unit would also lose the rest of the shared benefit.

*Where this is covered: Consolidated billing and shared discounts.*

</details>

### 10. Naming the person behind a query (Professional)

A company's analysts use Amazon Quick to query data held in Amazon Redshift. Auditors require that every query in the data warehouse be attributable to the named individual who ran it, not to a shared role, and that the analyst's group memberships in the corporate identity provider decide which tables they can read. Workforce identities are already federated to IAM Identity Center.

Which solution will meet these requirements?

- **A)** Create one IAM role per analyst team, assume it from Quick, and record the role ARN in CloudTrail.
- **B)** Map each analyst to a distinct IAM user and pass the user's access keys to Redshift.
- **C)** Configure trusted identity propagation between IAM Identity Center, Quick and Redshift.
- **D)** Enable attributes for access control in IAM Identity Center and tag every Redshift table with the analyst's user name.

<details><summary>Answer</summary>

**Answer: C.** Trusted identity propagation adds identity context to the role session so Redshift authorizes on the user's own identity and group memberships and logs the user identifier in its service logs and CloudTrail, which is exactly what the auditors asked for. A gives attribution only to a team role, so individual queries remain anonymous. B reintroduces long-term credentials and still does not carry group context into Redshift. D is a real feature used for the wrong job: session tags can express group-based access, but tagging tables per user name does not scale and does not put the user's identity in the Redshift logs.

*Where this is covered: IAM Identity Center: identity sources, permission sets and propagation.*

</details>

## Summary

Start from the account as the isolation boundary, then decide the tree. An organization in all features mode gives you OUs, policies, trusted access and delegated administration; consolidated billing alone gives you none of that. Group accounts into OUs by the controls they need, not the org chart, and remember that an SCP intersects down the path while a deny anywhere wins. Choose the policy type by the job: SCP for what your principals may do, RCP for who may touch your resources, declarative types for configuration you want held regardless of new APIs, and remember that SCPs and RCPs skip the management account while every declarative type does not. Let AWS Control Tower build and hold the structure, with preventive controls from Organizations policy, detective controls from AWS Config and proactive controls from CloudFormation hooks, and Account Factory vending accounts into it. Put logs in a Log Archive account, security tooling in an Audit account, shared networking in an Infrastructure account shared out with AWS RAM, and workforce sign-in in IAM Identity Center with permission sets assigned to groups.

## Related units

- [AWS Identity and Access Management](iam.md): policy evaluation logic, permissions boundaries, and the IAM mechanics of SCPs and RCPs
- [AWS CloudFormation](../08-management/cloudformation.md): service-managed StackSets, automatic deployment to OUs, and the machinery Control Tower runs on
- [AWS CloudTrail](../08-management/cloudtrail.md): organization trails, log file integrity validation and delivery to a central bucket
- [Detection and compliance services](detection-and-compliance-services.md): AWS Config aggregators, Security Hub, GuardDuty and their delegated administrators
- [AWS Directory Service](directory-service.md): AWS Managed Microsoft AD and AD Connector as an IAM Identity Center identity source
- [Amazon Cognito](cognito.md): application end user identity, and when it is the wrong answer for workforce access
- [Cost management](../08-management/cost-management.md): cost allocation tags, cost categories, budgets and the Cost and Usage Report across accounts
- [Hybrid connectivity](../04-networking/hybrid-connectivity.md): the transit gateway a Network account shares to the organization with AWS RAM
- [Amazon EventBridge](../06-integration/eventbridge.md): event buses, rules and cross-account delivery in depth

## Sources

- [Account Factory for Terraform account provisioning](https://docs.aws.amazon.com/controltower/latest/userguide/taf-account-provisioning.html): how AFT provisions and customizes accounts

- [Terminology and concepts for AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html): root, OU, management and member accounts, feature sets, handshakes, five levels of OU nesting
- [Managing organization policies with AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html): the full policy type list and the table of which types affect the management account
- [Service control policies (SCPs)](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html): no permissions are granted, the management account and service-linked role exemptions, and the testing warning
- [SCP evaluation](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_evaluation.html): allow at every level, deny anywhere, `FullAWSAccess` and the allow-list warning
- [Resource control policies (RCPs)](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html): the supported service list, `RCPFullAWSAccess`, and what RCPs cannot restrict
- [Declarative policies in AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_declarative_policies.html): control plane enforcement, the comparison with SCPs and RCPs, and rollback on detach
- [EC2 policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_ec2.html): the supported attributes, the account status report and custom error messages
- [Tag policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_tag-policies.html): what enforcement means and what is never evaluated
- [Backup policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_backup.html): inheritance into an effective plan and the complete-policy requirement
- [Chat applications policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_chatbot.html): the platforms and settings a policy can enforce
- [AI services opt-out policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_ai-opt-out.html): what opting out does to stored content
- [Delegated administrator for AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_delegate_policies.html): delegating policy management to a member account
- [AWS services that you can use with AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html): which services support trusted access and which support a delegated administrator
- [Quotas and service limits for AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_reference_limits.html): accounts, OUs, policy sizes, attachment maximums, closure limits and API throttle rates
- [Consolidating billing for AWS Organizations](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/consolidated-billing.html): one bill, combined usage, and the Cost Explorer consequence of leaving
- [Reserved Instances](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ri-behavior.html): discount pooling across the organization and turning sharing off
- [What Is AWS Control Tower?](https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html): landing zone, controls, Account Factory and the services it orchestrates
- [How AWS Control Tower works](https://docs.aws.amazon.com/controltower/latest/userguide/how-control-tower-works.html): the Security and Sandbox OUs, the shared accounts, and what setup does
- [Control behavior and guidance](https://docs.aws.amazon.com/controltower/latest/controlreference/control-behavior.html): preventive, detective and proactive behavior, their implementations and statuses, and the guidance levels
- [About controls in AWS Control Tower](https://docs.aws.amazon.com/controltower/latest/controlreference/controls.html): the management account exception to controls
- [How AWS Regions work with AWS Control Tower](https://docs.aws.amazon.com/controltower/latest/userguide/region-how.html): the home Region, governed Regions and re-registering OUs
- [Provision and manage accounts with Account Factory](https://docs.aws.amazon.com/controltower/latest/userguide/account-factory.html): provisioning permissions and the `AWSControlTowerExecution` role
- [Customize accounts with Account Factory Customization (AFC)](https://docs.aws.amazon.com/controltower/latest/userguide/af-customization-page.html): blueprints, the hub account, one blueprint per account and the Region options
- [Customizations for AWS Control Tower (CfCT) overview](https://docs.aws.amazon.com/controltower/latest/userguide/cfct-overview.html): CloudFormation templates, SCPs and RCPs driven by lifecycle events
- [Detect and resolve drift in AWS Control Tower](https://docs.aws.amazon.com/controltower/latest/userguide/drift.html): drift types, the daily policy scan, notifications and what must be fixed at once
- [What is IAM Identity Center?](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html): organization and account instances, one point of federation, and the rename
- [Manage AWS accounts with permission sets](https://docs.aws.amazon.com/singlesignon/latest/userguide/permissionsetsconcept.html): permission sets as IAM roles, policy types and session duration
- [Considerations for changing your identity source](https://docs.aws.amazon.com/singlesignon/latest/userguide/manage-your-identity-source-considerations.html): what is deleted, the Identity Store ID change and the access portal URL
- [Provision users and groups from an external identity provider using SCIM](https://docs.aws.amazon.com/singlesignon/latest/userguide/provision-automatically.html): required attributes, token expiry, and the SCP on the delegated administrator
- [Trusted identity propagation overview](https://docs.aws.amazon.com/singlesignon/latest/userguide/trustedidentitypropagation.html): identity context, the workflow and the auditing benefit
- [Attributes for access control](https://docs.aws.amazon.com/singlesignon/latest/userguide/attributesforaccesscontrol.html): session tags, `aws:PrincipalTag` and SAML assertion precedence
- [Quotas and limits in IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/limits.html): permission sets, accounts, groups per permission set and provisioning limits
- [What is AWS Resource Access Manager?](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html): resource shares, managed permissions, organization sharing without invitations, and no charge
- [Shareable AWS resources](https://docs.aws.amazon.com/ram/latest/userguide/shareable.html): the resource types that can be shared, by service
- [Recommended OUs and accounts](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/recommended-ous-and-accounts.html): the foundational, application, experimental, procedural and advanced OUs
- [Security OU - Log Archive account](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/log-archive.html): what the log archive account stores and the controls on it
- [Security OU - Security Tooling account](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/security-tooling.html): the audit account's role and the separation from log storage
- [Creating a trail for an organization](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html): organization trails, member account visibility, the service-linked role and Event history
- [Sending and receiving events between AWS accounts in Amazon EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cross-account.html): organization-wide bus policies, the IAM role requirement, billing and the no-chaining rule
- [AWS Control Tower pricing](https://docs.aws.amazon.com/controltower/latest/userguide/pricing.html): no additional charge for Control Tower, and the AWS Config cost of ephemeral workloads
