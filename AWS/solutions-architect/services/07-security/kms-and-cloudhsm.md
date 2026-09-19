# AWS Key Management Service and AWS CloudHSM

**Where it sits on the exams.** **AWS Key Management Service (AWS KMS)** is the managed service that creates, stores and controls the encryption keys nearly every other AWS service uses to encrypt data at rest, and **AWS CloudHSM** is the single-tenant hardware security module (HSM) cluster you operate yourself when the hardware and its users must be yours. KMS owns SAA-C03 task 1.3, "Determine appropriate data security controls", including the bullets on encryption and appropriate key management, encrypting data at rest, implementing access policies for encryption keys, and rotating encryption keys. On SAP-C02 it carries task 1.2, "Prescribe security controls", and task 2.3, "Determine security controls based on requirements", where the wording widens to encryption strategies for data at rest and in transit across many accounts. Both exam guides list CloudHSM as in scope, so neither reader can skip it. The rule of thumb: KMS answers every encryption-at-rest question by default, and CloudHSM answers only when the scenario names single-tenant HSMs you control, an application that speaks a cryptographic interface such as Public-Key Cryptography Standards #11 (PKCS #11) directly, or a job such as TLS offload, Oracle transparent data encryption or an issuing certificate authority private key.

## Envelope encryption and the data key pattern

A KMS key is a logical resource inside AWS KMS: a key ID, a key ARN, an alias, tags, a key policy and metadata, pointing at cryptographic key material generated inside hardware security modules validated to Federal Information Processing Standard (FIPS) 140-3 Security Level 3. That material never leaves AWS KMS in plaintext, every use of it is an API call to a Regional KMS endpoint, and every call is recorded in **AWS CloudTrail**, the API activity audit service. You never handle the top of the key hierarchy, and you get an audit trail of who asked to use it.

The consequence is that a KMS key cannot encrypt bulk data: a single `Encrypt` call against a symmetric encryption KMS key accepts at most 4,096 bytes of plaintext. Envelope encryption solves this. Your application calls `GenerateDataKey`, naming a KMS key, and AWS KMS returns a plaintext data key for immediate use plus a copy of that same data key encrypted under the KMS key. You encrypt the object locally, wipe the plaintext key from memory, and store the encrypted data key next to the ciphertext. To read the object back you send the encrypted data key to `Decrypt`, receive the plaintext key, decrypt locally and wipe it again. AWS KMS never stores, tracks or uses your data keys, and `GenerateDataKeyWithoutPlaintext` covers a process that must produce a wrapped key now and decrypt it later.

Two properties of the pattern decide exam answers. Cost and throughput follow how often you ask KMS for a data key, not how much data you encrypt, which is why data key caching and the **S3 Bucket Key**, a bucket-level data key that cuts KMS calls for objects encrypted with server-side encryption using KMS keys (SSE-KMS) in **Amazon Simple Storage Service (Amazon S3)**, the object storage service, exist. And rotating a KMS key re-encrypts nothing: it changes the wrapping key, not the data keys and not the data, so a stem about an exposed data key is not answered by rotation.

Every operation with a symmetric encryption KMS key accepts an optional encryption context, a set of non-secret key and value pairs bound to the ciphertext as additional authenticated data and required again to decrypt. It appears in plaintext in CloudTrail, so it labels which resource a decryption call was for, and it can become an authorization rule through the `kms:EncryptionContext:context-key` condition or a grant constraint. **Amazon Elastic Block Store (Amazon EBS)**, the block storage service for **Amazon Elastic Compute Cloud (Amazon EC2)** instances, uses the volume ID as the encryption context when it snapshots a volume. Asymmetric and HMAC keys do not support one.

Keep the scope of KMS clear. It protects data at rest and it signs and verifies; it does not protect data in transit. That is the job of Transport Layer Security (TLS), whose certificates come from **AWS Certificate Manager (ACM)**, the managed certificate service. A complete encryption strategy names both: KMS keys for the stored copy, ACM certificates and a condition such as `aws:SecureTransport` for the wire.

Because this unit owns the encryption strategy question for both exams, the
in-transit half deserves its own shape rather than a pointer. Decide where TLS
terminates. Terminating at an **Application Load Balancer** or at Amazon
CloudFront gives you certificate management and offloads the handshake, but the
hop from there to the target is a second connection that you must also encrypt
when the requirement says end to end. A **Network Load Balancer** can pass TLS
through untouched so it terminates on the instance, which is what a compliance
requirement for end-to-end encryption usually means. Inside a VPC, traffic to an
AWS service API over an interface endpoint stays on the AWS network and is still
TLS, so a private path is not a substitute for encryption but removes the
internet from the threat model. Enforce rather than assume: an
`aws:SecureTransport` condition in a bucket or resource policy denies any request
that did not arrive over TLS, and a security group that opens only 443 makes
plaintext impossible at the network layer. For service-to-service traffic that
must prove identity in both directions, mutual TLS with a private certificate
authority is the answer, which is why AWS Private Certificate Authority sits next
to KMS in a regulated design.

## Symmetric, asymmetric and HMAC keys

AWS KMS creates three families of key, and the exam tests which one can do which job. The symmetric encryption KMS key, key spec `SYMMETRIC_DEFAULT`, is a single 256-bit secret used for `Encrypt`, `Decrypt`, `ReEncrypt` and `GenerateDataKey`. It is the default when you create a key and it is the only type that AWS services integrated with KMS will accept for encryption at rest. It is also the only type that supports an encryption context, the only type that supports automatic key rotation, and the only type that can live in a custom key store.

An asymmetric KMS key is a related public and private key pair. The private key is created in AWS KMS and never leaves it in plaintext, so using the private half always means calling the KMS API, while the public half can be downloaded and used by parties with no AWS credentials. Key usage is fixed at creation. RSA key specs support either encryption and decryption or signing and verification, not both; elliptic curve key specs support either signing and verification or deriving a shared secret; ML-DSA key specs sign and verify only and are the post-quantum algorithm AWS recommends for organizations moving off RSA and ECDSA. An RSA key also caps single-call plaintext well below the 4,096 bytes a symmetric key allows. The decision rule is short: choose asymmetric when someone outside AWS must encrypt to you or verify your signature without calling AWS KMS, and symmetric for everything an AWS service stores.

A hash-based message authentication code (HMAC) KMS key is a symmetric secret used only with `GenerateMac` and `VerifyMac`. It takes a message of up to 4,096 bytes and returns a fixed-length tag nobody can reproduce without the same key, which suits validating a JSON Web Token, a tokenized card reference or a callback payload. HMAC keys cannot encrypt or sign, no other key type can perform MAC operations, and an HMAC key cannot encrypt at rest for an AWS service or live in a custom key store.

> **Professional depth.** Key type also sets your throughput ceiling, because AWS KMS meters request rate per key family. Cryptographic operations on symmetric keys, HMAC keys included, share one account and Region quota that is 10,000 requests per second in most Regions, 20,000 in several and 100,000 in US East (N. Virginia), US West (Oregon) and Europe (Ireland). RSA keys share a separate 1,000 per second quota, ML-DSA keys another, and elliptic curve keys another. A design that signs every API response with an RSA KMS key hits a wall two orders of magnitude below the symmetric ceiling, and the fix is to sign locally with a downloaded key or to move the check to an HMAC key.

## Customer managed, AWS managed and AWS owned keys

Every KMS key belongs to one of three ownership classes, and questions select between them with a handful of recurring phrases. Read the table for who holds the controls, who pays, whether you can change the rotation schedule, and the wording that points at each.

| Key type | Who controls the key policy | Who pays | Rotation configurable | Wording that selects it |
|---|---|---|---|---|
| Customer managed | You, exclusively | A monthly charge for each key, prorated hourly, plus a charge for every request | Yes: automatic rotation is optional, its period is 90 to 2,560 days with a default of 365, and on-demand rotation is available | "our own key material", "audit every use of the key", "share the encrypted snapshot with another account", "revoke access immediately", "deny the key to everyone" |
| AWS managed | The AWS service that created it; you can view the policy but not change it | No monthly charge; the caller pays for API requests against it | No: AWS KMS rotates it every year and the schedule cannot be changed | "encryption managed for us", "we do not want to administer a key", any alias of the form `aws/ebs` or `aws/rds` |
| AWS owned | The owning AWS service, exclusively; you cannot view it | Nothing at all | No: the owning service decides and does not report it | "encrypted by default at no extra cost", "no key for us to manage and nothing to audit" |

A customer managed key is one you created. It is the only class with a key policy you can edit, the only one you can disable or schedule for deletion, the only one you can share across accounts, and the only one counted against the quota of 100,000 keys per Region. When a scenario asks for control, audit or cross-account sharing of encrypted data, this is the answer.

An AWS managed key lives in your account but is created and used on your behalf by a service. You can read its policy and audit its use in CloudTrail, but you cannot change any property of it or call it directly. Two limits are frequently tested: you cannot share a resource encrypted under an AWS managed key with another account, and resource control policies in **AWS Organizations**, the multi-account governance service, do not apply to it. AWS managed keys are a legacy class that AWS stopped creating for new services in 2021.

An AWS owned key lives in an account the service owns. It costs nothing, needs no administration, and lets a service encrypt by default and move data across accounts and Regions without asking you for key permissions. The trade is visibility: you cannot see its policy, audit its use or delete it. Choose a customer managed key when control matters and an AWS owned key when convenience matters.

Pricing follows the same split. Each key you create costs one dollar per month, prorated hourly, and the figure is identical for symmetric, asymmetric, HMAC, imported-material and custom key store keys, and is charged once for every key in a multi-Region set. Enabling rotation adds the same one dollar per month for the first and second rotation only; later rotations are free. Requests are billed per ten thousand, with symmetric operations cheapest and RSA and elliptic curve operations several times dearer, over a monthly free tier of twenty thousand requests. AWS managed keys carry no monthly fee but their requests are billed, AWS owned keys are free, and when one account uses another account's key, the calling account pays.

## Key policies, IAM policies, grants and cross-account use

Access to a KMS key is decided by three instruments, and the first is not optional: every KMS key has exactly one key policy, and that resource policy is the primary control. **AWS Identity and Access Management (IAM)**, the service that defines principals and their permissions across AWS, behaves differently here than anywhere else, because a key policy grants nothing to the owning account by default. No principal, not the account root user and not the key's creator, has any permission to a KMS key unless a key policy, an IAM policy or a grant explicitly allows it and nothing denies it. Delete the enabling statement and the key becomes unmanageable by anyone.

That enabling statement is the one the console and the API add by default, and it is worth memorizing because so many broken scenarios trace back to it.

```json
{
  "Sid": "Enable IAM User Permissions",
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::111122223333:root"},
  "Action": "kms:*",
  "Resource": "*"
}
```

It gives the account full access to the key and, more importantly, it is what makes IAM policies work for this key at all. Without it an IAM policy that allows `kms:Decrypt` has no effect, although one that denies `kms:Decrypt` still does. This is one of the two resource types where a same-account request needs an allow on the resource side as well as the identity side; the general evaluation order is taught in [IAM](iam.md). Key policies are Regional, controlling only the key in their own Region, and are limited to 32 KB.

A grant is the third instrument and adds what a policy cannot. `CreateGrant` allows access to exactly one key for exactly one grantee, can only allow and never deny, covers only a fixed list of grant operations, and is withdrawn by retiring or revoking it rather than by editing a policy document. That makes it the right shape for permission that lasts as long as a job. It can carry an encryption context constraint, on symmetric encryption keys, or a `SourceArn` constraint, on any key type. Grants are how AWS services take temporary permission on your behalf: Amazon EBS creates one for each volume it decrypts on attachment, which is why the ceiling of 50,000 grants per key matters when tens of thousands of volumes share a key. Grants are eventually consistent, so code that must use one immediately passes the returned grant token. Treat `kms:CreateGrant` as an administrative permission, because a principal holding it can extend your key to other accounts.

The `kms:ViaService` condition key narrows a permission to requests arriving through a named AWS service on the caller's behalf, using values such as `ec2.us-west-2.amazonaws.com` or `s3.eu-west-1.amazonaws.com`. It writes the rule "this role may use this key, but only when **Amazon Relational Database Service (Amazon RDS)**, the managed relational database service, is encrypting a snapshot for it, never by calling `Decrypt` directly". It applies only to KMS key resource operations and only to forward access sessions, meaning calls a service makes on behalf of a principal rather than calls that principal makes itself.

Cross-account use needs both planes, and the exam tests this constantly. The key policy in the owning account must name the external account or principal, and an IAM policy in the caller's account must allow the action on that key ARN. Neither alone works: the key policy decides who can have access, the IAM policy decides who does. Only a fixed set of operations is effective across accounts, the cryptographic operations plus `CreateGrant`, `DescribeKey`, `GetKeyRotationStatus`, `GetPublicKey`, `ListGrants`, `RetireGrant` and `RevokeGrant`, so granting a foreign principal `kms:ScheduleKeyDeletion` does nothing. When a cross-account read of an object in Amazon S3 works before encryption is enabled and fails afterward, the missing allow is almost always in the key policy; the S3 side is covered in [Amazon S3](../01-storage/s3.md).

## Rotation, imported key material and key deletion

Automatic key rotation replaces the cryptographic material behind a key while leaving the key ID, ARN, alias, policy, grants and tags untouched. AWS KMS keeps every past version of the material and picks the right one when it decrypts, so nothing you stored becomes unreadable and no application changes. Rotation is optional on customer managed keys and supported only on symmetric encryption keys whose material AWS KMS generated. The period is now configurable: the default is 365 days and any value from 90 to 2,560 days is allowed, constrained if you wish by the `kms:RotationPeriodInDays` condition key. AWS managed keys rotate every year on a schedule you cannot change, and AWS owned key rotation is the owning service's business.

On-demand rotation covers the unplanned case. `RotateKeyOnDemand` generates new material immediately, works on symmetric encryption keys with AWS KMS generated or imported material, and leaves any automatic schedule intact. It is capped at 25 rotations per key and the cap is not adjustable, so it is a break-glass tool rather than a strategy. Asymmetric keys, HMAC keys and keys in a custom key store support neither automatic nor on-demand rotation; you rotate those manually by creating a new key and repointing the alias. A disabled key or one pending deletion is not rotated at all.

Imported key material, often called bring your own key, creates a key with no material and then loads material you generated yourself, wrapped under a public key AWS KMS issues with a single-use import token. It answers requirements about the entropy source, about keeping the original copy outside AWS, and about withdrawing a key at once. You may set an expiration time on import. When the material expires, or when you call `DeleteImportedKeyMaterial`, AWS KMS deletes it, the key state becomes pending import, and the key stops working immediately. To bring it back you must reimport exactly the same material, which is why losing your copy means losing the data. That is the trade against scheduled deletion: deletion waits days and is irreversible, while removing imported material is instant and reversible.

Deletion applies only to customer managed keys. `ScheduleKeyDeletion` requires a waiting period between 7 and 30 days, with a default of 30, and the deletion can fall up to 24 hours after the scheduled moment. Throughout the wait the key state is pending deletion, the key cannot be used in any cryptographic operation, and rotation is suspended, so the period doubles as a rehearsal of life without the key. `CancelKeyDeletion` restores it before the deadline; after the deadline the key, its aliases and its metadata are gone and every ciphertext under it is unrecoverable. Watch for use during the wait with an alarm in **Amazon CloudWatch**, the metrics and alarms service, and prefer disabling the key when you are not certain.

## Multi-Region keys and custom key stores

A multi-Region key is a set of keys in different Regions of one AWS partition sharing the same key ID and key material, so ciphertext produced in one Region decrypts in another with no cross-Region call and no re-encryption. They are not global: you create a primary, choose the Regions and replicate into them, and AWS never replicates a key for you. AWS managed keys are always single-Region. You cannot convert a single-Region key into a multi-Region key or the reverse, so the decision is made at creation and a retrofit means re-encrypting data.

What replicas share and what they do not is the tested detail. Shared and synchronized from the primary are the key ID, the key material and its origin, the key spec, the key usage and the rotation configuration, with both automatic and on-demand rotation triggered only on the primary. Independent in each Region are the key policy, the grants, the aliases, the tags and the enabled state. A replica is a complete key, not a pointer: it keeps working when the primary is disabled and it can be promoted to primary. That split makes multi-Region keys useful and dangerous at once, because a permissive policy in a replica Region is invisible from the primary. Most AWS services also treat a multi-Region key as an ordinary Regional key, so S3 cross-Region replication still decrypts and re-encrypts the data key in the destination Region. The clear wins are client-side encryption libraries, disaster recovery, and active-active applications that move ciphertext across Region boundaries.

The standard key store, where every ordinary KMS key lives, is a fleet of AWS-operated HSMs validated to FIPS 140-3 Security Level 3, backed by a 99.999 percent availability commitment. A custom key store replaces that storage layer with hardware you control, in one of two kinds. An AWS CloudHSM key store forwards KMS requests into a CloudHSM cluster in your own account, where the material is generated, stored and used; the cluster must hold at least two active HSMs in different Availability Zones before you can create keys in it, and AWS KMS logs in as a dedicated crypto user account named `kmsuser` whose password it rotates and holds. An external key store, or XKS, keeps the material in a key manager outside AWS and reaches it through an XKS proxy you run, over a public endpoint or an endpoint service in **Amazon Virtual Private Cloud (Amazon VPC)**, the private network service.

Custom key stores of both kinds support symmetric encryption keys only. Asymmetric keys, HMAC keys, automatic rotation, multi-Region keys and imported key material are unavailable in them, an account is limited to 10 custom key stores per Region, and throughput is capped by a per-key-store quota of 1,800 requests per second on top of the account quota. AWS is direct that a custom key store is not more secure than the standard key store, that one should be created only when a regulation explicitly mandates single-tenant or off-AWS key material, and that external key stores are not recommended because availability and latency then depend on infrastructure AWS does not run. When the requirement is only that you control the key material, imported key material in the standard key store is the lower-overhead answer and keeps the availability commitment.

## AWS CloudHSM clusters and when to choose them over KMS

AWS CloudHSM gives you HSMs of your own, attached to a VPC. A cluster is a collection of HSMs the service keeps synchronized, so a user or key created on one appears on all of them. A cluster can hold 1 to 28 HSMs, and the default quotas are 4 clusters and 6 HSMs per account per Region, both adjustable, while the 28 HSMs per cluster ceiling is not. More than one HSM in a cluster gives client-side load balancing automatically, and HSMs in different Availability Zones give high availability, which is why AWS recommends a minimum of two HSMs in separate Availability Zones. The service backs a cluster up at least every 24 hours and also when you activate a cluster or add or remove an HSM, and backups can be copied to another Region or shared with another account.

Clusters run in FIPS mode or non-FIPS mode, chosen at creation and unchangeable afterwards. The current HSM type, `hsm2m.medium`, is validated to FIPS 140-3 Level 3 and supports both modes; the older `hsm1.medium`, validated to FIPS 140-2 Level 3, was closed to new clusters in April 2025 and reached end of support on 31 March 2026, with existing clusters migrated automatically. Non-FIPS mode exists for workloads needing algorithms outside FIPS approval.

What you manage in CloudHSM that you do not manage in KMS is the heart of the comparison. Access inside the cluster does not use IAM: you create HSM users, crypto officers, crypto users and appliance users, on the HSMs themselves, with credentials you set. The data plane is end to end encrypted and invisible to AWS, so AWS cannot read your keys, cannot recover them if you lose the credentials, and has limited ability to diagnose key access problems. You own key durability, cluster scaling and client SDK upgrades, inside hard system quotas such as 16,666 keys per cluster on `hsm2m.medium`, of which at most 3,333 may be asymmetric, and 900 concurrent client connections. Billing is hourly per HSM with no upfront commitment, so a two-HSM cluster charges continuously whether or not anyone uses it, a different cost class from a KMS key.

The decision rule fits in one line. Choose AWS KMS unless the scenario names single-tenant HSMs under your control, an application that must speak PKCS #11, the Java Cryptography Extension, Cryptography API: Next Generation or a Key Storage Provider directly, TLS offload, an Oracle transparent data encryption master key, an issuing certificate authority private key, or an algorithm KMS does not offer. If the only stated requirement is FIPS 140-3 Level 3 validated hardware, KMS already meets it and CloudHSM is the distractor. If the requirement is single-tenant hardware but AWS services must still do the encrypting, the answer is a KMS custom key store backed by CloudHSM.

## Professional depth

At organization scale the first decision is where keys live. A key in each workload account keeps blast radius small and needs no cross-account policy, but multiplies rotation, audit and deletion work; a few keys in a security or shared-services account give one place to audit and one place to revoke. Because a key policy is a resource policy, the scalable sharing statement conditions on `aws:PrincipalOrgID` rather than listing account IDs, so new accounts inherit access as they join. Each member account still needs its own IAM policy allowing the action on the key ARN. Resource control policies can cap what principals do with keys in member accounts, but they do not apply to AWS managed keys, which is one reason organization-wide standards specify customer managed keys.

The quotas that bite are request quotas, not key counts. Cryptographic operations share one account and Region rate, so a fleet reading SSE-KMS objects from Amazon S3 competes with snapshot traffic and any application calling `Decrypt` directly. Most KMS request quotas are adjustable, but both custom key store quotas, CloudHSM-backed and external, are fixed through Service Quotas, and the cheaper first move is the S3 Bucket Key. The ceiling of 50,000 grants per key is reached by mass volume attachment when a fleet shares one key, and a custom key store adds a ceiling of 1,800 requests per second, which is why AWS restricts custom key stores to low-throughput work.

Migration and sharing scenarios are where key type decides the answer. A snapshot or image encrypted with an AWS managed key cannot be shared at all: copy it under a customer managed key whose policy admits the target account, then let that account copy it again under its own key. Cross-Region copy always re-encrypts under a key in the destination Region, and multi-Region keys do not change that for most services.

Know the failure modes, because Professional questions describe symptoms rather than causes. Disabling a key, scheduling its deletion or deleting imported material does not break a running resource immediately; it breaks the next operation that needs the data key decrypted, hours later, and looks like an unrelated outage. An explicit deny in a key policy overrides every allow and can lock administrators out of their own key. A `kms:ViaService` condition that was correct when the data was written blocks a direct `Decrypt` during an incident. And cross-account access fails the moment either plane changes, because both must allow every request.

## Worked scenario

A payments company runs a card-authorization platform in three accounts: security, production and analytics. Regulators require that the private key of the company's issuing certificate authority live in single-tenant hardware the company controls, that card data at rest be encrypted under keys the company can revoke within minutes, and that key material rotate at least every 90 days. The analytics team, in its own account, must read encrypted objects from the production S3 bucket.

The issuing CA key goes into an AWS CloudHSM cluster with two `hsm2m.medium` HSMs in different Availability Zones, in FIPS mode, reached through PKCS #11 from the CA software. Nothing else goes there, because CloudHSM offers no AWS service integration and no IAM-based access control. Everything an AWS service encrypts uses customer managed KMS keys in the security account, one per data domain, with automatic rotation enabled and the period set to 90 days. Each key policy admits the production application role and the analytics reader role, with a `kms:ViaService` condition limiting the application role to requests arriving through Amazon S3 and Amazon RDS, and both member accounts carry IAM policies allowing `kms:Decrypt` and `kms:GenerateDataKey` on those key ARNs. Bucket Keys keep the SSE-KMS request rate under the account quota, and the claims API terminates TLS with an ACM certificate while the bucket policy denies any request where `aws:SecureTransport` is false, so the strategy covers data in transit as well as at rest. To meet the revoke-in-minutes rule the company imports its own material into the card-data key, so one `DeleteImportedKeyMaterial` call stops every decryption at once and the material can be reimported later, instead of waiting 7 to 30 days for scheduled deletion.

The exam asks why the analytics team gets access denied after the bucket policy is corrected. The keyed answer is that the key policy in the security account must also allow the analytics role, because a KMS key policy must explicitly allow the principal and cross-account key use requires an allow in both the key policy and the caller's IAM policy.

## Exam lens

- "control the encryption key and audit its use" maps to a customer managed KMS key.
- "we do not want to manage a key" or "encrypted by default at no additional cost" maps to an AWS owned or AWS managed key.
- "share the encrypted snapshot with another account" maps to a customer managed key; an AWS managed key is the distractor because it can never be shared.
- "rotate key material every 90 days automatically" maps to automatic rotation with `RotationPeriodInDays` set to 90; creating a new key each quarter is the unnecessary-operational-overhead distractor.
- "revoke access to the data immediately" maps to imported key material deleted with `DeleteImportedKeyMaterial`, or to disabling the key; scheduled deletion is the distractor because it waits 7 to 30 days.
- "encrypt data in an AWS service" maps to a symmetric encryption KMS key; an asymmetric key is the distractor whenever an integrated service must do the encrypting.
- "a partner outside AWS must encrypt data for us without AWS credentials" maps to an asymmetric KMS key and a downloaded public key.
- "validate that a token was not tampered with" maps to an HMAC KMS key with `GenerateMac` and `VerifyMac`, not to signing.
- "this role may use the key only through Amazon EBS" maps to a `kms:ViaService` condition in the key policy.
- "grant a service temporary permission for the life of a job" maps to a grant.
- "decrypt in the failover Region without re-encrypting" maps to a multi-Region key, where your own code moves the ciphertext.
- "key material must never exist outside hardware we control" maps to a custom key store; when the requirement is only FIPS 140-3 Level 3, the standard KMS key store already meets it and CloudHSM is the distractor.
- "TLS offload, Oracle transparent data encryption, or an issuing CA private key" maps to AWS CloudHSM used directly.
- "reduce the cost of SSE-KMS on millions of objects" maps to an S3 Bucket Key.

## Knowledge check

### 1. Sharing an encrypted snapshot (Associate)

A media company stores rendered assets on Amazon EBS volumes in a production account and snapshots them nightly. The volumes are encrypted with the default Amazon EBS encryption key, which is the AWS managed key for the service. A newly created archive account must be able to restore these snapshots into volumes of its own. The company wants the smallest change that makes the snapshots shareable.

Which solution will meet these requirements?

- **A)** Share the existing snapshots with the archive account and grant that account `kms:Decrypt` on the AWS managed key in an IAM policy.
- **B)** Copy the snapshots, re-encrypting them with a different AWS managed key, then share the copies with the archive account.
- **C)** Copy the snapshots, re-encrypting them with a customer managed KMS key whose key policy allows the archive account, then share the copies.
- **D)** Turn off encryption on the source volumes, take unencrypted snapshots, and share those.

<details><summary>Answer</summary>

**Answer: C.** A resource encrypted under an AWS managed key can never be shared with another account, so the only path is to copy the snapshot and re-encrypt it under a customer managed key whose key policy admits the archive account. A fails because no policy edit is possible on an AWS managed key: its policy is controlled by the service and cannot be changed to admit an external account. B fails for the same reason, since re-encrypting under another AWS managed key leaves the snapshot unshareable. D is not possible, because encryption cannot be turned off on an existing encrypted Amazon EBS volume, and it would discard the encryption-at-rest control in any case.

*Where this is covered: Customer managed, AWS managed and AWS owned keys.*

</details>

### 2. A 90-day rotation requirement (Associate)

A bank's security standard requires that the key material protecting an Amazon RDS database rotate at least every 90 days. Applications must not change, stored data must not be re-encrypted, and every existing backup must stay readable.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Enable automatic key rotation on the customer managed KMS key and set the rotation period to 90 days.
- **B)** Create a new customer managed KMS key every 90 days and point the database at it.
- **C)** Run a scheduled job that calls `RotateKeyOnDemand` on the key every 90 days.
- **D)** Enable automatic key rotation on the AWS managed key for Amazon RDS and set its rotation period to 90 days.

<details><summary>Answer</summary>

**Answer: A.** Automatic rotation on a customer managed symmetric encryption key now takes a configurable period from 90 to 2,560 days, AWS KMS retains all previous key material so older backups still decrypt, and the key ID, ARN and alias do not change, so no application is touched. B is manual work every quarter and forces a change on the database. C does rotate the material but needs a scheduler, and on-demand rotation is capped at 25 per key with no way to raise the cap, so it eventually runs out. D is not possible: AWS managed keys rotate every year on a schedule that cannot be configured.

*Where this is covered: Rotation, imported key material and key deletion.*

</details>

### 3. Encryption by a partner with no AWS account (Associate)

A healthcare provider must let a laboratory partner encrypt small result files before transmitting them. The partner has no AWS account and cannot call AWS APIs. The provider must be the only party able to decrypt the files, and the private key material must never leave AWS.

Which solution will meet these requirements?

- **A)** Create a symmetric encryption KMS key and send the key material to the partner over a secure channel.
- **B)** Create an HMAC KMS key and give the partner the key so it can generate a MAC tag over each file.
- **C)** Create a customer managed key and let the partner assume a cross-account role in order to call `Encrypt`.
- **D)** Create an asymmetric KMS key with encrypt and decrypt key usage, download the public key, and give it to the partner.

<details><summary>Answer</summary>

**Answer: D.** An asymmetric KMS key keeps the private half inside AWS KMS while the public half can be downloaded and used by anyone, including a party with no AWS credentials, which is exactly the stated shape. A is impossible, because symmetric KMS key material cannot be exported from AWS KMS. B solves a different problem: an HMAC key authenticates a message and cannot encrypt anything, and sharing it would let the partner verify as well as generate. C requires the partner to hold AWS credentials and call the KMS API, which the scenario rules out.

*Where this is covered: Symmetric, asymmetric and HMAC keys.*

</details>

### 4. Cross-account access to SSE-KMS objects (Associate)

A retailer keeps nightly reports in an Amazon S3 bucket in its data account, encrypted with SSE-KMS under a customer managed key in that same account. A reporting role in a separate analytics account is named in the bucket policy and already has `s3:GetObject` in its identity policy, yet every download fails with an access denied error. Unencrypted objects in the same bucket download normally.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable an S3 Bucket Key on the bucket.
- **B)** Add a statement to the KMS key policy that allows the analytics reporting role to call `kms:Decrypt`.
- **C)** Replace the customer managed key with the AWS managed key for Amazon S3.
- **D)** Add `kms:Decrypt` on the key ARN to the reporting role's identity policy in the analytics account.
- **E)** Create a grant on the S3 bucket that allows the analytics account to read objects.

<details><summary>Answer</summary>

**Answer: B and D.** Cross-account use of a KMS key requires an allow in the key policy of the owning account and an allow in an IAM policy in the caller's account, and neither side is sufficient alone. The symptom, unencrypted objects working and encrypted objects failing, points squarely at the key plane. A only reduces KMS request cost and changes nothing about authorization. C would make the problem permanent, because a resource encrypted under an AWS managed key cannot be read from another account at all. E is not a real operation: grants are created on a KMS key, not on an S3 bucket.

*Where this is covered: Key policies, IAM policies, grants and cross-account use.*

</details>

### 5. Revoking access to encrypted data in minutes (Associate)

A defense contractor must be able to make an encrypted Amazon S3 dataset unreadable within minutes of declaring a security incident, and must be able to restore readability once the incident is closed. The data must stay where it is, and the control must apply no matter which principal or service tries to read it.

Which solution will meet these requirements?

- **A)** Schedule deletion of the KMS key with the minimum waiting period of 7 days.
- **B)** Import your own key material into the KMS key, call `DeleteImportedKeyMaterial` during an incident, and reimport the same material afterwards.
- **C)** Remove the statement in the bucket policy that allows the application role to read objects.
- **D)** Perform on-demand rotation of the KMS key at the start of the incident.

<details><summary>Answer</summary>

**Answer: B.** Deleting imported key material takes effect immediately, puts the key into a pending import state where no cryptographic operation succeeds for anyone, and is reversible by reimporting exactly the same material. A breaks the timing requirement, because the shortest waiting period is 7 days, and it is irreversible once the period ends. C removes one access path but leaves the data decryptable by any other principal that can reach the key, so it does not satisfy "no matter which principal". D generates new key material but leaves every previous version in place, so existing ciphertext keeps decrypting and nothing is revoked.

*Where this is covered: Rotation, imported key material and key deletion.*

</details>

### 6. A FIPS 140-3 Level 3 mandate across many accounts (Professional)

A systems integrator runs workloads in 60 accounts in one AWS Organizations organization. A new control requires that all key material protecting data at rest be generated and used inside hardware security modules validated to FIPS 140-3 Level 3, that every use of a key be auditable from the account that owns the data, and that Amazon S3, Amazon EBS and Amazon RDS keep encrypting at rest with no application changes. Several workloads read tens of thousands of objects per second.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Use customer managed KMS keys in the standard key store, with automatic rotation enabled and AWS CloudTrail recording in every account.
- **B)** Create an AWS CloudHSM cluster in each account and integrate every application through PKCS #11.
- **C)** Create a KMS custom key store backed by an AWS CloudHSM cluster in each account and create the keys there.
- **D)** Create a KMS external key store in each account, backed by the integrator's on-premises key manager.

<details><summary>Answer</summary>

**Answer: A.** The standard KMS key store already generates and uses key material in HSMs validated to FIPS 140-3 Security Level 3, records every call in AWS CloudTrail, and integrates with all three storage services without code changes, so the control is met with nothing extra to run. B removes AWS service integration entirely, since CloudHSM has no IAM-based access control and no native encryption at rest for S3, EBS or RDS. C meets the letter of the control but adds a cluster per account and caps each key store at 1,800 requests per second, far below the stated read rate. D has the same throughput problem, adds an XKS proxy to operate, and is explicitly not recommended by AWS.

*Where this is covered: AWS CloudHSM clusters and when to choose them over KMS.*

</details>

### 7. Throttling on a high-volume SSE-KMS workload (Professional)

A streaming analytics platform writes and reads millions of small objects per hour in a single Region, all in Amazon S3 with SSE-KMS under one customer managed key. During peak hours the application logs `ThrottlingException` responses from AWS KMS and read latency climbs. The encryption control and the audit trail must stay exactly as they are.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable an S3 Bucket Key on the buckets and rewrite existing objects so they adopt it.
- **B)** Create ten additional customer managed KMS keys and spread new objects evenly across them.
- **C)** Move the key into an AWS CloudHSM key store so the workload gets its own throughput pool.
- **D)** Request an increase to the cryptographic operations request rate quota for the account and Region.
- **E)** Switch the buckets to server-side encryption with customer-provided keys.

<details><summary>Answer</summary>

**Answer: A and D.** A Bucket Key derives a short-lived bucket-level key and can cut calls from S3 to KMS by up to 99 percent, and because existing objects do not adopt it automatically they must be rewritten. The shared cryptographic operations request rate is an account and Region quota and it is adjustable, so raising it addresses the remaining volume. B does not help, because the quota is per account and Region rather than per key. C makes the problem worse: a custom key store adds its own ceiling of 1,800 requests per second on top of the account quota. E changes the encryption control and removes the KMS audit trail the scenario requires to stay in place.

*Where this is covered: Professional depth.*

</details>

### 8. Customer-generated key material at scale (Professional)

An insurer's regulator requires that the key material protecting policy documents be generated on the insurer's own equipment, that the insurer keep the only other copy, and that the insurer be able to withdraw the material from AWS on demand. The documents live in Amazon S3 and are read by a claims service at high request rates. The insurer also wants an availability commitment from AWS covering the key itself.

Which solution will meet these requirements?

- **A)** Create a KMS external key store fronted by an XKS proxy in the insurer's data center.
- **B)** Create a KMS custom key store backed by an AWS CloudHSM cluster with two HSMs in different Availability Zones.
- **C)** Create a customer managed KMS key with imported key material in the standard key store, and set an expiration time on the material.
- **D)** Run an AWS CloudHSM cluster and have the claims service call it directly through PKCS #11.

<details><summary>Answer</summary>

**Answer: C.** Imported key material gives the insurer control of generation, a copy held outside AWS, and immediate withdrawal through `DeleteImportedKeyMaterial` or an expiration time, while the key still lives in the standard key store and therefore keeps full AWS service integration, the highest request rates and the AWS availability commitment. A and B both move the material into a custom key store, which caps throughput at 1,800 requests per second, carries no availability commitment, and makes the insurer responsible for the availability of the key path. D removes S3 server-side encryption integration altogether, since CloudHSM cannot act as the key store for SSE-KMS unless it is wired up as a KMS custom key store.

*Where this is covered: Multi-Region keys and custom key stores.*

</details>

## Summary

AWS KMS is a chain of decisions, and the exam walks it in order. Decide what the key must do: symmetric for anything an AWS service encrypts, asymmetric when a party outside AWS must encrypt to you or verify your signature, HMAC when you are authenticating a token. Decide who owns it: a customer managed key when you need to edit the policy, audit use, share across accounts or revoke, an AWS managed or AWS owned key when you want encryption with no administration and no bill. Decide who may use it, remembering that a key policy is always required, that an IAM allow does nothing without it, that a cross-account call needs an allow on both sides, and that grants and `kms:ViaService` narrow permission without rewriting the policy. Decide the lifecycle: automatic rotation with a period from 90 to 2,560 days, on-demand rotation for the unplanned case, imported material when you must withdraw the key in seconds, and a 7 to 30 day wait when you really are deleting it. Finally decide where the material lives: a custom key store or AWS CloudHSM only when a regulation demands single-tenant hardware you control, the standard key store every other time.

## Related units

- [AWS Identity and Access Management](iam.md): policy evaluation order, explicit deny, and cross-account role assumption
- [Amazon S3](../01-storage/s3.md): SSE-S3, SSE-KMS, DSSE-KMS, SSE-C, Bucket Keys and client-side encryption
- [AWS Certificate Manager](acm.md): the certificates that protect data in transit and their renewal
- [Amazon EBS](../01-storage/ebs.md): volume and snapshot encryption, and cross-account snapshot copy
- [AWS Secrets Manager and Parameter Store](secrets-manager-and-parameter-store.md): secrets encrypted with KMS keys, and rotation of the secret rather than the key
- [AWS Organizations, IAM Identity Center and Control Tower](organizations-identity-center-and-control-tower.md): service control and resource control policies that constrain key use organization-wide
- [AWS CloudTrail](../08-management/cloudtrail.md): where every KMS API call and encryption context lands
- [Amazon RDS](../05-database/rds.md): database encryption at rest and encrypted snapshot copy

## Sources

- [Resource control policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html): that resource control policies do not apply to AWS managed keys
- [AWS CloudHSM pricing](https://docs.aws.amazon.com/cloudhsm/latest/userguide/pricing.html): hourly billing per HSM in a cluster

- [AWS KMS keys](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html): customer managed, AWS managed and AWS owned key comparison, and the 2021 status of AWS managed keys
- [AWS Key Management Service](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html): FIPS 140-3 Security Level 3 validation and the key hierarchy
- [Generate data keys](https://docs.aws.amazon.com/kms/latest/developerguide/data-keys.html): the envelope encryption pattern and GenerateDataKeyWithoutPlaintext
- [Encryption context](https://docs.aws.amazon.com/kms/latest/developerguide/encrypt_context.html): additional authenticated data, CloudTrail visibility, and the asymmetric and HMAC exclusion
- [Asymmetric keys in AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/symmetric-asymmetric.html): RSA, ECC and ML-DSA key usage rules
- [Choosing a KMS key spec](https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-choose-key-spec.html): the 4,096-byte symmetric Encrypt limit and RSA plaintext limits
- [HMAC keys in AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/hmac.html): GenerateMac and VerifyMac, and what HMAC keys cannot do
- [Key policies in AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html): every key must have exactly one key policy, and IAM policies need the key policy to enable them
- [Default key policy](https://docs.aws.amazon.com/kms/latest/developerguide/key-policy-default.html): the Enable IAM User Permissions statement
- [Creating a key policy](https://docs.aws.amazon.com/kms/latest/developerguide/key-policy-overview.html): the 32 KB policy document limit
- [KMS key access and permissions](https://docs.aws.amazon.com/kms/latest/developerguide/control-access.html): the three access mechanisms and the cross-account rule
- [Grants in AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/grants.html): grant operations, constraints, grant tokens and eventual consistency
- [Allowing users in other accounts to use a KMS key](https://docs.aws.amazon.com/kms/latest/developerguide/key-policy-modifying-external-accounts.html): the operations that work cross-account and the two-policy requirement
- [AWS KMS condition keys](https://docs.aws.amazon.com/kms/latest/developerguide/conditions-kms.html): kms:ViaService semantics and examples
- [Rotate AWS KMS keys](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html): what rotation does and does not change, and which key types cannot rotate
- [Enable automatic key rotation](https://docs.aws.amazon.com/kms/latest/developerguide/rotating-keys-enable.html): the 90 to 2,560 day rotation period and the 365 day default
- [Perform on-demand key rotation](https://docs.aws.amazon.com/kms/latest/developerguide/rotating-keys-on-demand.html): the limit of 25 on-demand rotations per key
- [Importing key material for AWS KMS keys](https://docs.aws.amazon.com/kms/latest/developerguide/importing-keys.html): supported key types and the reasons to import
- [Delete imported key material](https://docs.aws.amazon.com/kms/latest/developerguide/importing-keys-delete-key-material.html): expiration, the pending import state and reimport
- [Delete an AWS KMS key](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html): the 7 to 30 day waiting period and the 30 day default
- [Multi-Region keys in AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html): shared and independent properties, and how services treat replicas
- [Key stores](https://docs.aws.amazon.com/kms/latest/developerguide/key-store-overview.html): standard, imported material, CloudHSM key store and external key store trade-offs
- [AWS CloudHSM key stores](https://docs.aws.amazon.com/kms/latest/developerguide/keystore-cloudhsm.html): the two-HSM requirement and the kmsuser crypto user
- [Resource quotas](https://docs.aws.amazon.com/kms/latest/developerguide/resource-limits.html): 100,000 keys, 50,000 grants per key, 10 custom key stores, 25 on-demand rotations
- [Request quotas](https://docs.aws.amazon.com/kms/latest/developerguide/requests-per-second.html): shared cryptographic request rates, the 1,800 per second custom key store quota, and which request quotas are adjustable
- [AWS Key Management Service pricing](https://aws.amazon.com/kms/pricing/): monthly key charge, rotation charge cap, request pricing and free tier
- [What is AWS CloudHSM?](https://docs.aws.amazon.com/cloudhsm/latest/userguide/introduction.html): FIPS and non-FIPS clusters, single tenancy and the AWS KMS comparison note
- [External key stores](https://docs.aws.amazon.com/kms/latest/developerguide/keystore-external.html): the XKS proxy, public endpoint and VPC endpoint service connectivity
- [AWS CloudHSM clusters](https://docs.aws.amazon.com/cloudhsm/latest/userguide/clusters.html): 1 to 28 HSMs and Availability Zone placement
- [AWS CloudHSM cluster modes](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cluster-hsm-types.html): FIPS and non-FIPS mode fixed at cluster creation
- [AWS CloudHSM cluster high availability and load balancing](https://docs.aws.amazon.com/cloudhsm/latest/userguide/cluster-high-availability-load-balancing.html): automatic client-side load balancing and the two-HSM recommendation
- [Users in AWS CloudHSM](https://docs.aws.amazon.com/cloudhsm/latest/userguide/hsm-users.html): HSM users are not IAM principals
- [Cluster backups in AWS CloudHSM](https://docs.aws.amazon.com/cloudhsm/latest/userguide/manage-backups.html): the 24-hour backup cadence and cross-Region copy
- [Compliance validation for AWS CloudHSM](https://docs.aws.amazon.com/cloudhsm/latest/userguide/fips-validation.html): hsm2m.medium FIPS 140-3 Level 3 and hsm1.medium FIPS 140-2 Level 3
- [Deprecation notifications](https://docs.aws.amazon.com/cloudhsm/latest/userguide/compliance-dep-notif.html): hsm1.medium end of support on 31 March 2026
- [AWS CloudHSM quotas](https://docs.aws.amazon.com/cloudhsm/latest/userguide/limits.html): clusters, HSMs, keys per cluster and client connections
