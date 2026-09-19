# AWS Directory Service

**Where it sits on the exams.** **AWS Directory Service** is the family of managed directory options that lets AWS services and Windows or Linux workloads use Microsoft Active Directory, the directory that stores users, groups and computers and decides who may sign in to what. It is the service behind the SAA-C03 task 1.1 skill "Determining when to federate a directory service with IAM roles", and it appears in SAP-C02 task 4.2, which lists **AWS IAM Identity Center**, the workforce single sign-on service, and AWS Directory Service among the identity services a migration must plan for. The rule of thumb the exam rewards: if the directory has to live in AWS, or a Windows workload needs real Active Directory features, choose AWS Managed Microsoft AD; if it must stay on premises with nothing cached in AWS, choose AD Connector.

## The three directory options and what each one actually is

**AWS Directory Service for Microsoft Active Directory**, usually called **AWS Managed Microsoft AD**, is Microsoft Windows Server Active Directory run inside your **Amazon VPC**, the isolated virtual network service. It supports Group Policy, schema extensions, secure LDAP over TLS, Kerberos single sign-on, forest trusts, and Active Directory-aware software. A directory starts with two domain controllers across two Availability Zones, daily backups and encrypted storage; you can add controllers up to 20 per directory. AWS retains enterprise administrator rights and gives you full control over one organizational unit plus `AWS Delegated` groups, so software that demands domain administrator rights needs delegated permissions instead.

There are two editions. Standard Edition holds up to roughly 30,000 directory objects, which AWS describes as a primary directory for organizations of up to 5,000 employees; Enterprise Edition holds up to roughly 500,000. AWS calls both figures approximations, because real capacity depends on object size. Only Enterprise Edition supports multi-Region replication, and only Enterprise Edition can be shared with 500 accounts rather than 25. A third variant, AWS Managed Microsoft AD (Hybrid Edition), makes AWS domain controllers part of your existing on-premises forest, extending it into AWS with no trust at all; neither exam guide names it.

**AD Connector** is a directory gateway, not a directory. It forwards requests to your on-premises Microsoft Active Directory without caching data in AWS. You give it domain controller addresses and a service account that can read users and groups, plus join computers if you use seamless domain join or **Amazon WorkSpaces**, the managed virtual desktop service. It returns a token after your domain controller authenticates a request. Small and large sizes span two Availability Zones and have no enforced user or connection limit.

**Simple AD** is a Samba 4 Active Directory-compatible directory supporting user accounts, group memberships, Group Policy, Kerberos single sign-on and domain joins, in small (about 2,000 objects) and large (about 20,000 objects) sizes. It is no longer open to new customers, and AWS points them at AWS Managed Microsoft AD or AD Connector; existing customers keep full functionality and can still create directories, so treat it as closed rather than retired. The exams still describe the low-cost basic directory it was built for.

## Choosing between them under time pressure

One question settles almost every scenario: where does the directory live, and who answers the authentication request? Read across the row your scenario describes and the answer falls out.

| Question | AWS Managed Microsoft AD | AD Connector | Simple AD |
|---|---|---|---|
| Objects live | In AWS, real Windows Server AD | On premises, nothing cached | In AWS, Samba 4 |
| Who authenticates | AWS domain controllers, or on-premises ones over a trust | On-premises controllers, every time | AWS |
| Trust to another forest | Yes, one-way or two-way, forest or external | No, not even a transitive AD trust | No |
| MFA for AWS application sign-in | Yes, via RADIUS | Yes, via RADIUS | No |
| Schema extensions and LDAPS | Yes | Your own directory decides | No |
| Shareable with other accounts | Yes | No | No |
| If the link on premises drops | AWS directory accounts keep working | All authentication stops | No link to drop |
| Status | Current | Current | Closed to new customers |

AD Connector caches nothing, so if the **AWS Direct Connect**, the dedicated network connection service, link or the **AWS Site-to-Site VPN** tunnel, the encrypted connection over the internet, fails, dependent applications stop authenticating users. A trust also copies no users, groups or passwords. An on-premises account used across a trust still needs an on-premises domain controller, while accounts in AWS Managed Microsoft AD continue through its AWS domain controllers. A scenario requiring authentication through a network outage wants AWS Managed Microsoft AD with users in it, not AD Connector.

Multi-factor authentication (MFA) here means a second factor for AWS application sign-in, not IAM MFA or Identity Center MFA. AWS Managed Microsoft AD and AD Connector act as Remote Authentication Dial-In User Service (RADIUS) clients against your server, using UDP port 1812 by default. Simple AD cannot do this.

Pricing follows the deployment rather than usage. AWS Managed Microsoft AD is billed per domain controller hour, by edition, with two controllers included and each extra one at the same rate. Directory sharing adds an hourly charge per additional account shared to, with no charge for extra VPCs or the owning account, and multi-Region replication adds the controllers in each Region plus per-GB data transfer between them. AD Connector and Simple AD are billed hourly by size.

## Trusts, seamless domain join and directory sharing

AWS Managed Microsoft AD supports both forest trusts and external trusts, in all three directions: incoming, outgoing and two-way. You can trust a self-managed domain on premises or on **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service, or another AWS Managed Microsoft AD directory. The prerequisites are what exam questions hide in the stem: connectivity to the on-premises network with the Active Directory ports open, Kerberos pre-authentication enabled on the user accounts, conditional DNS forwarders and the same trust password on both sides, and unique NetBIOS and domain names. Single-label domains are not supported, and IP routes must be added when the on-premises network uses public, non-RFC 1918 address space.

Direction matters. IAM Identity Center, WorkSpaces, **Amazon Quick**, the business intelligence service formerly called Amazon QuickSight, and the AWS Management Console require a two-way trust, because the AWS directory must query users and groups in yours. Amazon EC2, **Amazon Relational Database Service (Amazon RDS)**, the managed relational database service, and **Amazon FSx**, the managed file system family, work with a one-way or two-way trust. Selective authentication narrows a trust to named service accounts.

Seamless domain join puts Windows and supported Linux EC2 instances in the domain at launch through the agent of **AWS Systems Manager**, the operations and configuration management service; EC2 Mac instances require a manual join. It needs an instance profile with the `AmazonSSMManagedInstanceCore` and `AmazonSSMDirectoryServiceAccess` policies from **AWS Identity and Access Management (IAM)**, the service that authorizes actions; `ds:DescribeDirectories` and `ds:CreateComputer` for the launcher; access to the directory and the `ssm`, `ssmmessages`, `ec2messages` and `ds` endpoints; and working domain DNS. Linux also uses a service account in **AWS Secrets Manager**, the managed secret storage service.

Directory sharing lets one directory serve many accounts. Each consumer receives a shared directory object used for seamless domain join. With **AWS Organizations**, the multi-account governance service, all features enabled and the directory in the management account, consumers need not accept; outside Organizations, each accepts a handshake. VPC connectivity is still required, and the consumer pays the sharing fee. AD Connector cannot be shared or span VPCs, so each account and VPC needs its own, with WorkSpaces in the same VPC.

## Which AWS services can consume which directory

This is the discriminator that decides more questions than any other detail in the unit. Read the table for the row that matches the service in the stem; a "no" eliminates a directory type outright. Four of its rows name services this unit does not otherwise teach: **AWS Client VPN**, the managed remote access VPN, **Amazon Quick**, the business intelligence service formerly called Amazon QuickSight, **AWS License Manager**, which tracks software licences, **AWS Private CA**, the managed private certificate authority, and **Amazon WorkMail**, the managed email service, which is closed to new customers and ends support on 31 March 2027.

| AWS service | AWS Managed Microsoft AD | AD Connector | Simple AD |
|---|---|---|---|
| WorkSpaces | Yes | Yes | Yes |
| AWS Management Console sign-in | Yes | Yes | Yes |
| Amazon EC2 domain join | Yes | Yes, to your own domain | Yes |
| IAM Identity Center identity source | Yes | Yes | No |
| Amazon RDS Windows or Kerberos auth | Yes | No | No |
| FSx for Windows File Server | Yes | No | No |
| AWS Client VPN, Amazon Quick | Yes | Yes | No |
| AWS License Manager, AWS Private CA | Yes | Not listed | No |
| Amazon WorkMail | Yes | Yes | Yes |
| Third-party AD-aware software | Yes | No, AWS applications only | Samba 4-compatible only |

Two rows carry most of the weight. Amazon RDS is explicit: "Amazon RDS supports using only AWS Managed Microsoft AD for Windows Authentication. RDS doesn't support using AD Connector." That covers SQL Server Windows Authentication and the Kerberos options on RDS for Oracle and PostgreSQL. **Amazon FSx for Windows File Server**, the managed Windows file share service, is equally explicit that it "does not support Active Directory Connector and Simple Active Directory"; its options are AWS Managed Microsoft AD or a self-managed Active Directory the file system joins directly, a different mechanism from AD Connector. Any question pairing an on-premises directory with RDS for SQL Server or FSx is steering you to AWS Managed Microsoft AD, usually with a trust.

WorkSpaces is the opposite case, accepting everything: AD Connector to an on-premises domain, AWS Managed Microsoft AD standalone or with a cross trust, or Simple AD. When WorkSpaces appears with "existing corporate credentials and nothing stored in AWS", AD Connector is the keyed answer.

IAM Identity Center accepts AWS Managed Microsoft AD or AD Connector as its identity source and performs pass-through authentication, synchronizing users, groups and memberships but never passwords. The directory must be in the Organizations management account, or the Identity Center delegated administrator account when one exists, and in the same Region. Only one directory connects at a time, so several forests require AWS Managed Microsoft AD with trusts. Simple AD is unsupported.

Directory federation with IAM roles separates authentication from authorization. For direct AWS Management Console federation, map directory users or groups to IAM roles; a successful directory sign-in yields temporary role credentials instead of long-lived IAM user keys. Choose this when an existing workforce directory must control who assumes a bounded AWS role. For centrally assigning access across many accounts, use Identity Center permission sets with the directory as its identity source. SAML or OpenID Connect federation covers external identity providers without Directory Service, as explained in [AWS Identity and Access Management](iam.md); **Amazon Cognito** authenticates an application's end users instead.

## Professional depth

At organization scale, use one AWS Managed Microsoft AD resource forest for computer objects, service accounts and AWS integrations, with a trust to the corporate forest. Share it so instances across accounts and VPCs join one domain. The quotas are 25 shared accounts per Standard directory, 500 per Enterprise, 20 domain controllers and 20 directories per Region.

Multi-Region replication is Enterprise Edition only and answers a global Active Directory requirement. Adding a Region deploys two domain controllers there in the same account, builds the inter-Region networking, creates an Active Directory site named after the Region, and replicates users, groups, Group Policy Objects, trusts and schema. The directory ID stays the same, and Amazon EC2, FSx for Windows File Server and RDS for SQL Server connect to the local instance. One directory spans at most five Regions, one primary plus four additional, and trusts are a global feature configured only in the primary Region.

Two things bite. AD Connector has a one-to-one relationship with a domain, so a forest with several child domains needs one per domain, each a hard dependency on the hybrid link. And a migration that moves a domain rather than trusting it uses the Active Directory Migration Toolkit with the Password Export Service, the keyed answer when a SAP-C02 stem says the on-premises domain controllers are being decommissioned.

## Worked scenario

A manufacturer runs one on-premises Active Directory forest, `corp.example.com`, and is migrating to AWS. It has a management account and eight workload accounts in one organization, connected to the data center by AWS Direct Connect. Three things move first: 400 WorkSpaces desktops, a SQL Server estate going to Amazon RDS for SQL Server with Windows Authentication, and a Windows file share going to FSx for Windows File Server. Employees must keep one password, and Windows servers in every workload account must join the domain automatically when an Auto Scaling group launches them.

The design puts an AWS Managed Microsoft AD Enterprise Edition directory in the management account and creates a two-way forest trust to `corp.example.com`, with conditional forwarders on both sides and the Active Directory ports open across Direct Connect. Two-way is required rather than optional, because WorkSpaces is one of the AWS enterprise applications that must query the corporate directory. RDS for SQL Server and FSx for Windows File Server join the AWS directory, the only option either accepts, and corporate users authenticate across the trust. The directory is shared with all eight workload accounts through the Organizations method, needing no acceptance step, and each launch template attaches an instance profile with `AmazonSSMManagedInstanceCore` and `AmazonSSMDirectoryServiceAccess` so new instances seamlessly join. IAM Identity Center, enabled in the same Region, uses that directory as its identity source, so the same accounts get console and CLI access through permission sets.

The exam asks this as "which directory option supports WorkSpaces, RDS for SQL Server Windows Authentication and FSx while letting employees keep their existing credentials, with the LEAST operational overhead". The keyed answer is AWS Managed Microsoft AD with a two-way trust, shared to the workload accounts. AD Connector is the distractor and fails twice: RDS and FSx do not accept it, and it cannot be shared.

## Exam lens

- "Users must sign in with existing on-premises credentials and no directory data may be stored in AWS" maps to AD Connector; AWS Managed Microsoft AD is the distractor because it holds objects in the cloud.
- "RDS for SQL Server needs Windows Authentication" maps to AWS Managed Microsoft AD, with a trust if the accounts are on premises; AD Connector and Simple AD are unsupported.
- "FSx for Windows File Server with an existing corporate directory" maps to AWS Managed Microsoft AD with a trust, or a direct join to a self-managed AD; AD Connector is never the answer for FSx.
- "Authentication must survive an outage of the link to the data center" maps to AWS Managed Microsoft AD with users in the AWS directory; AD Connector stops authenticating entirely.
- "Join EC2 instances in 20 accounts to one domain" maps to AWS Managed Microsoft AD shared through AWS Organizations; one AD Connector per account is the distractor, and it is not even possible.
- "The seamless domain join silently fails" maps to a missing `AmazonSSMDirectoryServiceAccess` policy on the instance profile, or DNS that does not resolve the domain.
- "A low-cost directory with only basic Active Directory features" maps, on the exams, to Simple AD; in practice it is closed to new customers.
- "Add MFA to AWS application sign-in for directory users" maps to a RADIUS server with AWS Managed Microsoft AD or AD Connector; Simple AD supports no MFA.
- "Use Active Directory as the identity source for IAM Identity Center" maps to AWS Managed Microsoft AD or AD Connector in the management account, in the same Region; Simple AD is unsupported, and only one directory connects at a time, so several forests means trusts.
- "Which trust direction" maps to two-way for IAM Identity Center, WorkSpaces, Amazon Quick and the AWS Management Console; one-way or two-way works for EC2, RDS and FSx.
- "One directory serving users in several Regions with low authentication latency" maps to multi-Region replication, which requires Enterprise Edition.
- "Who pays for a shared directory" maps to the consumer account, not the owner.
- "Decommission the on-premises domain controllers entirely" maps to migrating objects with the Active Directory Migration Toolkit and Password Export Service, not to a trust.

## Knowledge check

### 1. Virtual desktops for an existing workforce (Associate)

A company is deploying Amazon WorkSpaces for 600 employees. The security team requires that user accounts, passwords and group memberships remain only in the company's on-premises Active Directory, and that no directory information is stored in AWS. The company already has an AWS Direct Connect connection to the data center.

Which solution will meet these requirements?

- **A)** Create an AWS Managed Microsoft AD directory and use the Active Directory Migration Toolkit to copy the user accounts into it.
- **B)** Create an AD Connector that points to the on-premises domain controllers and register it with WorkSpaces.
- **C)** Create a Simple AD directory and create matching user accounts in it.
- **D)** Create an AWS Managed Microsoft AD directory and configure a one-way trust to the on-premises domain.

<details><summary>Answer</summary>

**Answer: B.** AD Connector is a proxy that redirects directory requests to the on-premises domain controllers without caching any information in the cloud, and WorkSpaces is one of the AWS applications it supports. A copies the accounts into AWS, which is exactly what the requirement forbids. C creates a second set of credentials in a Samba 4 directory in AWS, failing both the single-source and no-storage requirements. D stores computer objects and service accounts in AWS and, because WorkSpaces is an AWS enterprise application that must query the corporate directory, a one-way trust in that direction would not work anyway.

*Where this is covered: Choosing between them under time pressure.*

</details>

### 2. Windows Authentication for a migrated database (Associate)

A company is migrating Microsoft SQL Server databases to Amazon RDS for SQL Server. Applications must continue to connect using Windows Authentication with the accounts that already exist in the company's on-premises Active Directory forest. The company does not want to duplicate user accounts.

Which solution will meet these requirements?

- **A)** Create an AD Connector to the on-premises forest and enable Windows Authentication on the RDS DB instance.
- **B)** Create a Simple AD directory and recreate the required accounts in it.
- **C)** Create an AWS Managed Microsoft AD directory, establish a trust with the on-premises forest, and join the RDS DB instance to the AWS directory.
- **D)** Use IAM database authentication and map each Active Directory user to an IAM user.

<details><summary>Answer</summary>

**Answer: C.** AWS documents that Amazon RDS supports only AWS Managed Microsoft AD for Windows Authentication, and a trust lets the existing on-premises accounts authenticate without being copied. A fails on the documented statement that RDS does not support AD Connector. B duplicates the accounts, which the scenario rules out, and Simple AD is not compatible with RDS for SQL Server either. D replaces Windows Authentication with a different mechanism and would require an IAM user per person, which is neither what the applications use nor a scalable identity design.

*Where this is covered: Which AWS services can consume which directory.*

</details>

### 3. Domain-joining instances across accounts (Associate)

A company runs one AWS Managed Microsoft AD directory in its AWS Organizations management account. Windows EC2 instances launched by Auto Scaling groups in six workload accounts must join that domain automatically at launch, with no manual steps and no scripts holding domain credentials. The VPCs are already connected through a transit gateway.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Share the AWS Managed Microsoft AD directory with the six workload accounts using the AWS Organizations sharing method.
- **B)** Create an AD Connector in each workload account that points to the shared directory.
- **C)** Attach an instance profile to the instances that includes the `AmazonSSMManagedInstanceCore` and `AmazonSSMDirectoryServiceAccess` managed policies.
- **D)** Store the domain administrator password in user data and run a domain join command at boot.
- **E)** Create a separate AWS Managed Microsoft AD directory in each workload account and replicate objects between them.

<details><summary>Answer</summary>

**Answer: A and C.** Directory sharing gives each consumer account the shared directory object that seamless domain join needs, and the two managed policies are the documented IAM prerequisite for the Systems Manager agent to perform the join. B misuses AD Connector, which proxies to a self-managed directory rather than to a shared AWS Managed Microsoft AD, and cannot be shared. D puts a privileged credential in user data, which the scenario forbids and which is poor practice regardless. E multiplies cost and administration and is not how AWS Managed Microsoft AD replicates, since replication is a Region feature of one directory rather than a way to link separate directories.

*Where this is covered: Trusts, seamless domain join and directory sharing.*

</details>

### 4. A second factor for directory sign-in (Associate)

A company uses an on-premises Active Directory and an existing RADIUS-based one-time passcode system. It is adopting Amazon WorkSpaces and AWS Management Console access and requires a second authentication factor when users sign in from the internet. Directory data must stay on premises.

Which solution will meet these requirements?

- **A)** Create an AD Connector to the on-premises directory and enable multi-factor authentication on it, pointing at the existing RADIUS servers.
- **B)** Create a Simple AD directory and enable multi-factor authentication on it.
- **C)** Enable IAM multi-factor authentication on each user's IAM user account.
- **D)** Create an AWS Managed Microsoft AD directory and copy the user accounts into it so that MFA can be enabled.

<details><summary>Answer</summary>

**Answer: A.** AD Connector keeps the directory on premises and can act as a RADIUS client against existing MFA infrastructure for WorkSpaces and AWS Management Console sign-in. B is impossible because Simple AD does not support MFA. C applies only to IAM-user sign-in and leaves WorkSpaces unprotected. D can support MFA but copies directory data into AWS, breaking the stated constraint and adding an unnecessary migration.

*Where this is covered: Choosing between them under time pressure.*

</details>

### 5. A global directory for a multi-Region estate (Professional)

A company runs Active Directory-aware applications, Amazon FSx for Windows File Server file systems and Amazon RDS for SQL Server instances in three AWS Regions. It currently operates an AWS Managed Microsoft AD Standard Edition directory in one Region, and remote users report slow authentication. The company wants one directory whose users, groups, Group Policy Objects and schema are identical in every Region, with authentication served locally, and the least ongoing administration.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Replace the Standard Edition directory with an Enterprise Edition directory and migrate its objects.
- **B)** Create an additional AWS Managed Microsoft AD directory in each Region and build two-way trusts between them.
- **C)** Configure multi-Region replication on the Enterprise Edition directory and add the two additional Regions.
- **D)** Deploy an AD Connector in each additional Region pointing at the original directory.
- **E)** Add domain controllers to the original directory and expose them through a Network Load Balancer in each Region.

<details><summary>Answer</summary>

**Answer: A and C.** Multi-Region replication requires Enterprise Edition, so the Standard directory must be replaced. It deploys two domain controllers per added Region, builds inter-Region networking and replicates users, groups, Group Policy Objects, trusts and schema under one directory ID. B creates separate directories that must be maintained separately. D is only a proxy to a self-managed directory, not replication. E neither places controllers in other Regions nor replicates directory data.

*Where this is covered: Professional depth.*

</details>

### 6. Single sign-on across several forests (Professional)

A holding company has three separate Active Directory forests on premises, one per subsidiary, and an AWS organization with 40 accounts. It wants employees from all three forests to sign in once and receive access to AWS accounts through IAM Identity Center permission sets, without deploying a third-party identity provider, and with one place to manage the connection.

Which solution will meet these requirements?

- **A)** Create one AD Connector per forest in the management account and connect all three to IAM Identity Center.
- **B)** Create a Simple AD directory in the management account, synchronize all three forests into it, and connect it to IAM Identity Center.
- **C)** Create an AWS Managed Microsoft AD directory in an ordinary workload account that is not the delegated administrator, establish two-way trusts to the three forests, and connect it to IAM Identity Center.
- **D)** Create an AWS Managed Microsoft AD directory in the Organizations management account, establish two-way trusts to the three forests, enable IAM Identity Center in the same Region as the directory, and connect the directory as the identity source.

<details><summary>Answer</summary>

**Answer: D.** IAM Identity Center can connect only one AD Connector or one AWS Managed Microsoft AD directory at a time, it can work with users from the connected directory or from any domain reached through a trust, and the directory must reside in the management account or the Identity Center delegated administrator account and be in the same Region as Identity Center. A breaks the one-directory rule and AD Connector supports no AD trusts and maps one-to-one to a single domain, so it cannot reach the other forests. B fails twice: Simple AD is not supported as an Identity Center connected directory, and it supports no trusts or synchronization from other forests. C places the directory in the wrong account, which the documented prerequisite rules out.

*Where this is covered: Which AWS services can consume which directory.*

</details>

## Summary

AWS Directory Service is a short sequence of decisions. First ask where the directory has to live. If it must stay on premises with nothing cached in AWS, AD Connector is the proxy that forwards every authentication to your own domain controllers, at the price of a hard dependency on the hybrid link, no trusts, no sharing across accounts, and no support from Amazon RDS or FSx for Windows File Server. If the directory can live in AWS, AWS Managed Microsoft AD is real Windows Server Active Directory with Group Policy, schema extensions, LDAPS, RADIUS-backed MFA and forest or external trusts in any direction, shareable to other accounts so one domain serves a whole organization. Choose Enterprise Edition when you need 500,000 objects, 500 shared accounts or multi-Region replication. Simple AD remains the exams' low-cost basic directory, closed to new customers, with no MFA, no trusts and no support from RDS, FSx or IAM Identity Center. Then check the consuming service: two-way trust for WorkSpaces and IAM Identity Center, one-way is enough for EC2, RDS and FSx, and the sharing fee lands on the consumer account.

## Related units

- [AWS Organizations, IAM Identity Center and AWS Control Tower](organizations-identity-center-and-control-tower.md): permission sets, identity sources and the management account placement rule this unit depends on
- [AWS Identity and Access Management](iam.md): SAML and OIDC federation with IAM roles when a directory service is not involved
- [Amazon Cognito](cognito.md): application end user identity, the wrong answer for workforce directory scenarios
- [Amazon FSx](../01-storage/fsx.md): FSx for Windows File Server and its Active Directory join options
- [Amazon RDS](../05-database/rds.md): Windows and Kerberos authentication on RDS DB instances
- [AWS Systems Manager](../08-management/systems-manager.md): the agent and IAM permissions that make seamless domain join work
- [Other compute and end-user computing services](../02-compute/other-compute-and-end-user.md): Amazon WorkSpaces and the directory it registers against
- [Hybrid connectivity](../04-networking/hybrid-connectivity.md): the Direct Connect or VPN path a trust and an AD Connector both depend on

## Sources

- [What is AWS Directory Service?](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/what_is.html): the three options, Standard and Enterprise object counts, and the which-to-choose table
- [AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_microsoft_ad.html): what the managed directory provides and the edition split
- [What gets created with your AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_getting_started_what_gets_created.html): two domain controllers across two Availability Zones, the ENIs, the security group and the delegated OU model
- [AD Connector](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_ad_connector.html): proxy with no caching, small and large sizes, no transitive trusts, one per domain, not shareable, not multi-VPC aware
- [What gets created with your AD Connector](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/create_details_ad_connector.html): the authentication forwarding path and two-Availability-Zone deployment
- [Getting started with AD Connector](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ad_connector_getting_started.html): the service account privileges and size choice
- [Simple AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_simple_ad.html): closed to new customers, small and large sizes, and the unsupported feature list including MFA, trusts and IAM Identity Center
- [Simple AD availability changes](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/simple-ad-availability-change.html): existing customers retain functionality, and the recommended alternatives
- [Creating a trust relationship between your AWS Managed Microsoft AD and self-managed AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_setup_trust.html): forest and external trusts, all three directions, the two-way requirement for AWS enterprise applications, and the prerequisites
- [Share your AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_directory_sharing.html): the Organizations and handshake methods and which account is charged
- [Joining an Amazon EC2 Windows instance to your AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/launching_instance.html): seamless domain join prerequisites, IAM policies and endpoints
- [Seamlessly joining an Amazon EC2 Linux instance](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/seamlessly_join_linux_instance.html): supported Linux join flow, SSM Agent and the Secrets Manager service account
- [Joining an Amazon EC2 Mac instance](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/join_mac_instance.html): the manual macOS join procedure
- [Application compatibility for AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_app_compatibility.html): the compatible AWS service list and the domain administrator and schema guidelines
- [Application compatibility policy for AD Connector](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ad_connector_app_compatibility.html): the AD Connector service list and the note that Amazon RDS is not compatible
- [Configure Multi-Region replication for AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_configure_multi_region_replication.html): Enterprise Edition only, what gets deployed per Region, and the supported services
- [AWS Managed Microsoft AD quotas](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_limits.html): directories per Region, domain controllers, shared domains per edition and the five-Region ceiling
- [AWS::DirectoryService::MicrosoftAD](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-directoryservice-microsoftad.html): changing the directory edition requires replacement
- [Enabling multi-factor authentication for AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_mfa.html): the RADIUS client model, port 1812 and the Simple AD exclusion
- [Use Case 5: Extend your on-premises Active Directory to the AWS Cloud](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/usecase5.html): trusts avoid synchronizing users, groups or passwords, and the ADMT migration path
- [Microsoft AD directory as an IAM Identity Center identity source](https://docs.aws.amazon.com/singlesignon/latest/userguide/manage-your-identity-source-ad.html): management account placement, same-Region requirement, one directory at a time and the Simple AD exclusion
- [Enabling AWS Management Console access](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_management_console_access.html): assigning directory users and groups to IAM roles
- [Working with AWS Managed Active Directory with RDS for SQL Server](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_SQLServerWinAuth.html): RDS supports only AWS Managed Microsoft AD for Windows Authentication
- [Working with Microsoft Active Directory in FSx for Windows File Server](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/aws-ad-integration-fsxW.html): AWS Managed Microsoft AD or self-managed AD only, with AD Connector and Simple AD unsupported
- [Manage directories for WorkSpaces Personal](https://docs.aws.amazon.com/workspaces/latest/adminguide/manage-workspaces-directory.html): the directory options WorkSpaces accepts, including cross trust
- [AWS Directory Service pricing](https://aws.amazon.com/directoryservice/pricing/): hourly domain controller billing, additional controllers, the per-account sharing charge and cross-Region data transfer
- [AWS Directory Service FAQs](https://aws.amazon.com/directoryservice/faqs/): the resource forest pattern and multi-Region replication behavior
