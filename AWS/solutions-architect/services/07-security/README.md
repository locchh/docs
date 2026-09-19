# Security

Security is the largest single block on SAA-C03, where domain 1 is 30 percent of
the scored exam, and it runs through every domain of SAP-C02. The category
starts with **AWS IAM**, the service that decides which principal may call which
API on which resource, and extends outward: **AWS Organizations** for guardrails
across many accounts, **AWS KMS** for the keys that encrypt data at rest, **AWS
Certificate Manager** for the certificates that protect data in transit,
**Amazon Cognito** for application end users rather than AWS principals, and a
set of detective services that tell you what actually happened.

The decision the category keeps asking you to make is which layer owns the
control. The same requirement can be met by an identity policy, a resource
policy, a network rule, or an organization-wide guardrail, and the exam usually
accepts only one of them. "Only this account may read the bucket" is a resource
policy or a condition key, not a security group. "No account in the organization
may leave this Region" is a service control policy, not an IAM policy. "The
database must not be reachable from the internet" is subnet and security group
design, not encryption. Read for the layer, then pick the service.

| Unit | What you will be able to do after reading it | Tier |
|---|---|---|
| [iam.md](iam.md) | Write and evaluate policies, design cross-account role assumption, and apply least privilege | L |
| [organizations-identity-center-and-control-tower.md](organizations-identity-center-and-control-tower.md) | Design an account structure with guardrails, federated sign-in and shared resources | L |
| [kms-and-cloudhsm.md](kms-and-cloudhsm.md) | Choose a key type, write key policies, and design cross-account and multi-Region key use | M |
| [acm.md](acm.md) | Issue, validate and renew certificates, and place them correctly for each service | S |
| [secrets-manager-and-parameter-store.md](secrets-manager-and-parameter-store.md) | Choose between the two stores and design rotation | S |
| [cognito.md](cognito.md) | Separate user pools from identity pools and attach them to an API or a load balancer | M |
| [directory-service.md](directory-service.md) | Connect workloads to Active Directory with the right directory type | S |
| [waf-shield-firewall-manager-and-network-firewall.md](waf-shield-firewall-manager-and-network-firewall.md) | Build layered protection against web and volumetric attacks, centrally | M |
| [detection-and-compliance-services.md](detection-and-compliance-services.md) | Choose a detective service by the signal it reads, and aggregate findings | M |

## Which exam tasks this serves

On SAA-C03 it is all of domain 1: tasks 1.1, 1.2 and 1.3. On SAP-C02 it is tasks
1.2 and 1.4, 2.3, 3.2, and 4.2 for the identity and governance side of a
migration.

## Reading order

Read `iam.md` first. Nothing else here makes sense without it. Then
`kms-and-cloudhsm.md` and `acm.md` for the encryption pair,
`secrets-manager-and-parameter-store.md`, and `cognito.md`. Read the detective
units next, then `waf-shield-firewall-manager-and-network-firewall.md`. Leave
`organizations-identity-center-and-control-tower.md` until last on a first pass:
an Associate-only candidate needs service control policies, **AWS Control
Tower**, which sets up a governed multi-account landing zone, and consolidated
billing from it, and can skim the rest, and can also skim `directory-service.md`
down to the three directory types.
