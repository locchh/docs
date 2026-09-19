# AWS Certificate Manager

**Where it sits on the exams.** **AWS Certificate Manager (ACM)** is the managed service that issues, stores, deploys and renews the X.509 certificates that terminate Transport Layer Security (TLS) in front of AWS applications, and **AWS Private Certificate Authority (AWS Private CA)** is the managed certificate authority (CA) that signs the ones only your own organization should trust. On SAA-C03, ACM owns the task 1.3 bullet "Encrypting data in transit, for example AWS Certificate Manager (ACM) using TLS" and the certificate half of "Rotating encryption keys and renewing certificates"; the key half of that bullet belongs to [AWS Key Management Service](kms-and-cloudhsm.md). On SAP-C02 it carries the certificate management clause of task 1.2, "Prescribe security controls", and task 2.3, "Determine security controls based on requirements", wherever the wording turns to data in transit. Two rules of thumb decide most questions. A public certificate from ACM validated by DNS is the answer for any internet-facing endpoint, because it is free for integrated services and renews itself. And a certificate is a Regional resource that must sit in the Region of the resource using it, with **Amazon CloudFront**, the AWS content delivery network, the one integration that always reads it from US East (N. Virginia).

## Public, private and imported certificates

ACM manages three kinds of certificate and the differences drive almost every answer. A public certificate is issued by Amazon Trust Services, an Amazon-operated public CA whose roots ship in every major browser and operating system, so a browser shows a padlock with no action by you. A private certificate is signed by a private CA you run in AWS Private CA; nothing trusts it until an administrator installs your root CA certificate in the client trust stores, which is why it suits internal service-to-service traffic and mutual TLS between microservices. An imported certificate is one you bought from a third-party CA and uploaded into ACM for AWS services to use.

Public certificates from ACM are domain validated: they attest to control of a domain name and nothing about the organization behind it. ACM cannot issue an organization-validated or extended-validation certificate, so a stem that insists on EV is telling you to buy one elsewhere and import it. Each certificate carries at least one fully qualified domain name and up to ten by default, raisable to 100, all listed in the Subject Alternative Name extension. A wildcard name such as `*.example.com` protects one subdomain level only: it covers `login.example.com` but neither `test.login.example.com` nor the apex `example.com`, so an apex plus its subdomains means requesting both names on one certificate.

Validity periods differ by type and have shortened. A public ACM certificate is now valid for 198 days, down from the 395 days older certificates carry, tracking the industry move to shorter lifetimes. A private certificate from AWS Private CA is valid for 13 months, that is 395 days, and the signing CA certificate must expire later than the certificate it signs or the request fails. An account holds 2,500 ACM certificates per Region, with expired and revoked ones still counting until deleted, and 200 private CAs per Region; certificates signed by a private CA do not count toward the certificate quota.

## Domain validation and managed renewal

Before Amazon Trust Services issues a public certificate, ACM must prove you control every name on it. DNS validation is the method to know. ACM hands you one CNAME record per unique name, of the form `_a79865eb.example.com` pointing at `_424c7224.acm-validations.aws`, and you publish it once. If **Amazon Route 53**, the AWS authoritative Domain Name System service, hosts the zone, the ACM console writes the record for you. The record stays useful indefinitely: while it remains in place you can reissue the same certificate, request certificates for the same name in other Regions, and let ACM revalidate at renewal without anyone doing anything. A wildcard name and its base domain share one identical CNAME pair.

Email validation is the fallback for teams that cannot edit the DNS zone. ACM mails a link to five fixed addresses at the domain, `administrator@`, `hostmaster@`, `postmaster@`, `webmaster@` and `admin@`, and someone must click it within 72 hours before the token expires. Two consequences are tested: renewal needs a human to click a link again every time, and you cannot switch an existing certificate from email to DNS validation, you delete it and request a new one. HTTP validation proves control through an HTTP redirect, but it is available only through the CloudFront distribution tenants feature and does not support wildcard names, so treat DNS as the default and email as the exception.

Managed renewal is what makes ACM worth using, and its eligibility rules are the highest-value facts here. For a 198-day public certificate, ACM begins the renewal attempt 45 days before expiry; certificates still carrying the older 395-day validity renew at 60 days and come back with the new 198-day period. Private certificates issued through ACM renew 60 days before they expire. At that moment ACM checks two things for a DNS-validated public certificate: that the certificate is currently in use by an AWS service or has been exported since it was issued or last renewed, and that every validation CNAME still resolves publicly. Hence the corollary an exam question loves: a standard certificate never attached to anything expires quietly no matter how correct its DNS records are. Deleting the CNAME record, or detaching the certificate, stops automatic renewal.

The ineligibility list is short and worth memorizing. A certificate is not eligible for managed renewal if it was imported, if it has already expired, or if it is a private certificate issued by calling the AWS Private CA `IssueCertificate` API directly rather than through ACM. An imported certificate is your responsibility from the day you upload it, and reimporting a replacement preserves the same Amazon Resource Name (ARN) and therefore every association with load balancers and distributions. ACM renewal preserves the ARN too, so nothing needs reconfiguring when it succeeds.

Monitoring closes the gap. ACM publishes a `DaysToExpiry` metric per certificate twice a day to **Amazon CloudWatch**, the AWS metrics and alarms service, and emits `ACM Certificate Approaching Expiration` events to **Amazon EventBridge**, the event bus that routes AWS events to targets, starting 45 days out for private and imported certificates and 30 days out for public ones, both adjustable with `PutAccountConfiguration`. Route those events at **AWS Lambda**, the serverless function service, and nothing expires by surprise.

## Where certificates attach and the Region rules

An ACM-managed certificate attaches to an integrated service, which fetches the private key internally and never exposes it to you. The list that matters is **Elastic Load Balancing**, the managed load balancing service, covering the **Application Load Balancer (ALB)**, its HTTP-aware layer 7 member, and the **Network Load Balancer (NLB)**, its layer 4 member; CloudFront; **Amazon API Gateway**, the managed API front door, on custom domain names; **AWS Elastic Beanstalk**, the managed application platform, through the load balancer it creates; **AWS Network Firewall**, the managed VPC network firewall, for TLS inspection; and **AWS Nitro Enclaves**, the isolated execution environment on **Amazon Elastic Compute Cloud (Amazon EC2)** instances. That last entry is the exception: attaching an ACM-managed certificate directly to an EC2 instance requires a Nitro Enclave.

An ALB carries one default certificate per HTTPS listener plus a certificate list of up to 25 more, selecting among them with Server Name Indication (SNI), so one load balancer fronts many domains. The default is used only when the client sends no SNI hostname or nothing in the list matches.

Certificates are Regional resources and cannot be copied between Regions, so the same domain name served from three Regions needs three certificates, each validated in its own Region. Read the table for which Region each integration wants; these five rules are what questions are built from.

| Where the certificate is used | Region it must live in |
|---|---|
| Application, Network or Classic Load Balancer, the superseded original | The same Region as the load balancer |
| CloudFront, between viewers and the distribution | US East (N. Virginia), always |
| CloudFront to an Elastic Load Balancing origin over HTTPS | Any Region, because that certificate is the origin's |
| API Gateway edge-optimized custom domain name | US East (N. Virginia) |
| API Gateway Regional custom domain name | The same Region as the API |

The third row is the one candidates miss. The US East (N. Virginia) requirement covers the viewer-facing certificate on the distribution, not the one the origin presents to CloudFront. A distribution in front of an ALB in Sydney uses a us-east-1 certificate for the browser and an ap-southeast-2 certificate on the load balancer.

## Exporting certificates and AWS Private CA

For years an ACM public certificate could not leave AWS at all. That changed: an exportable public certificate is one you mark as exportable when you request it, after which `ExportCertificate` returns the certificate, the chain and the private key encrypted under a passphrase you supply, for installation on any EC2 instance, container or on-premises host. The constraints are specific. Exportability is set at request time and cannot be added later, so an existing certificate must be replaced rather than converted, and no public certificate created before 17 June 2025 can be exported. Validity is 198 days with renewal attempted 45 days out, but ACM only produces the renewed certificate: deploying it is your job, which is what the EventBridge renewal events exist to trigger. Previously exported certificates are also the only public certificates you can revoke, because a key that has left AWS can be compromised; revocation is permanent, global and takes up to 24 hours, and non-exportable certificates are deleted rather than revoked.

Pricing follows that split. Public certificates for integrated AWS services cost nothing. Exportable ones carry a per-name charge at issuance and again at each renewal, at a higher rate for a wildcard name, plus a charge for `ExportCertificate` calls beyond a free monthly allowance. AWS Private CA charges a prorated monthly fee per CA, with the first CA in each account and Region free for 30 days; certificates issued directly from a private CA are charged once each on a volume-tiered scale, while a private certificate requested through ACM is charged only the first time you export its private key. A private certificate that stays attached to an ALB and is never exported therefore costs nothing beyond the CA fee.

AWS Private CA itself is a hierarchy of root and subordinate CAs you create and control, with revocation through a certificate revocation list (CRL), Online Certificate Status Protocol (OCSP) or both. It offers two CA modes, chosen with the `UsageMode` parameter at creation. General-purpose mode is the default and issues certificates of any validity, at 400 USD per CA per month. Short-lived certificate mode issues certificates valid for at most seven days, costs 50 USD per CA per month, and skips revocation infrastructure because the certificates expire faster than a revocation list would propagate. Two constraints make it a narrow tool: such a CA must be the last in the hierarchy, and ACM cannot issue certificates signed by one, so it is reached through the AWS Private CA API.

One more issuance path is worth knowing. ACM runs a managed server for the Automated Certificate Management Environment (ACME) protocol, so standard clients such as Certbot and cert-manager can obtain publicly trusted certificates for servers outside AWS. The client generates and keeps the private key, the certificates last 45 days, and the client renews them, so they fall outside ACM managed renewal and cannot be bound to an integrated AWS service.

## Professional depth

At organization scale the certificate question becomes a private PKI question, and the sharing model is the part Professional questions probe. An ACM certificate belongs to one account in one Region, so the thing you share is the CA, not the certificate. A CA administrator in a shared-services account attaches a resource-based policy to the private CA, either directly with `PutPolicy` or through **AWS Resource Access Manager (AWS RAM)**, the cross-account resource sharing service, naming an account, an organizational unit, or a whole organization in **AWS Organizations**, the multi-account governance service. Each member account then requests its own certificates from that CA through ACM, and each certificate lives in the requesting account. Two operational details follow. The recipient account, not the CA owner, owns autorenewal, because ACM installs a service-linked role there on first use and only a principal in that account can fix it if the role is missing. And even single-account issuance needs the CA administrator to call `CreatePermission` granting the ACM service principal rights to create, retrieve and list certificates, or renewals fail silently in an account that looks correctly configured.

The cost that bites is the per-CA monthly fee. At 400 USD per general-purpose CA per month, a CA in each of 60 workload accounts is a five-figure line item before any certificate is issued. Against that, a CA shared across an organization is a single blast radius, so the usual compromise is a root CA in a security account, subordinate CAs per environment, and RAM shares scoped to organizational units. Multi-Region designs need the same care, because nothing replicates: a standby Region needs its own certificate for the same name, and since a validation CNAME works in any Region, publish the records once and request the certificate in every Region the runbook might use, well before the event.

Know the failure modes, because Professional stems describe symptoms. A certificate that expired despite managed renewal was never attached to a service, had its validation CNAME deleted during a DNS cleanup, or was imported and untracked. An **AWS CloudFormation** stack hanging in `CREATE_IN_PROGRESS` for hours is usually an `AWS::CertificateManager::Certificate` resource waiting on an unanswered validation email. A CloudFront distribution that refuses a certificate that plainly exists is reading only us-east-1. And an application that pins a specific certificate breaks on every renewal, because a renewed certificate carries a new key pair even though the ARN is unchanged.

## Worked scenario

A healthcare platform serves `www.example.com` and `api.example.com` from Application Load Balancers in Ireland and Frankfurt, fronted by a CloudFront distribution, with an API Gateway Regional custom domain in each Region for partners. Internally, 40 microservices authenticate to each other with mutual TLS, and a legacy claims appliance on EC2 instances needs a server certificate it can install in its own configuration file. Compliance requires that no certificate expire unnoticed and that internal certificates chain to a CA the company controls.

The public side is three ACM certificates and no renewals to think about. One covering both names is requested in US East (N. Virginia) for the distribution, and one in each of Ireland and Frankfurt for that Region's load balancer and Regional API Gateway domain name. All three use DNS validation, with the CNAME records published once in the Route 53 public hosted zone and left there, so ACM revalidates and renews each of them at 45 days as long as they stay attached. They are free, and validating the same names in three Regions costs nothing extra.

The internal side is AWS Private CA. A root CA sits in the security account in general-purpose mode, with a subordinate CA per Region shared to the workload organizational unit through AWS RAM, and each workload account requests its own private certificates through ACM and attaches them to internal load balancers, where they renew at 60 days with no export. The claims appliance is the one case needing a key in hand: the team requests a private certificate through ACM and exports it, paying the one-time fee at first export, and a Lambda function subscribed to the ACM renewal event in EventBridge re-exports and pushes the renewed certificate. A CloudWatch alarm on `DaysToExpiry` catches what the automation misses.

The exam asks why the distribution cannot find the certificate the team created in Ireland. The keyed answer is that a certificate used between viewers and CloudFront must be requested in US East (N. Virginia), and the Ireland certificate is the right one for the load balancer behind it.

## Exam lens

- "TLS certificate for a public website at no additional cost" maps to a public ACM certificate on the integrated service; buying from a third-party CA is the distractor.
- "the certificate must renew with no operational effort" maps to ACM with DNS validation, because email validation requires a human to click a link at every renewal.
- "CloudFront distribution and a certificate" maps to a certificate in US East (N. Virginia), no matter where the origin runs.
- "an edge-optimized API Gateway custom domain name" maps to US East (N. Virginia); a Regional custom domain name maps to the Region of the API.
- "the same domain served from load balancers in three Regions" maps to one certificate per Region; copying a certificate between Regions is impossible and a common distractor.
- "the certificate expired even though managed renewal was enabled" maps to a certificate not in use by any AWS service, or whose validation CNAME was removed.
- "we must keep using our existing commercial CA" maps to importing the certificate into ACM, with your own expiry monitoring, because ACM never renews imported certificates.
- "alert us before any certificate expires" maps to the `DaysToExpiry` CloudWatch metric or the EventBridge approaching-expiration event.
- "internal services must authenticate each other with mutual TLS" maps to private certificates from AWS Private CA, not public certificates.
- "several accounts must issue certificates from one certificate authority" maps to sharing the private CA through AWS RAM or a CA resource policy; sharing the certificate itself is the distractor.
- "install the certificate on our own servers and let AWS renew it" maps to an exportable public certificate requested with export enabled; on the exams, the older mapping that ACM certificates cannot leave AWS still drives answers that terminate TLS at an ALB or CloudFront.

## Knowledge check

### 1. A distribution in front of a Regional load balancer (Associate)

A retailer serves `shop.example.com` through an Amazon CloudFront distribution whose origin is an Application Load Balancer in the Europe (Ireland) Region. The team requested an ACM public certificate for `shop.example.com` in Europe (Ireland), attached it to the load balancer successfully, and now finds that the certificate does not appear in the list of custom SSL certificates when configuring the distribution.

Which solution will meet these requirements?

- **A)** Copy the existing certificate from Europe (Ireland) to US East (N. Virginia) using the ACM console.
- **B)** Change the distribution's origin protocol policy to HTTP only so that no certificate is required.
- **C)** Request a second ACM public certificate for `shop.example.com` in the US East (N. Virginia) Region and select it as the distribution's custom SSL certificate.
- **D)** Move the Application Load Balancer to the US East (N. Virginia) Region so that it shares a Region with the distribution.

<details><summary>Answer</summary>

**Answer: C.** A certificate used between viewers and a CloudFront distribution must be requested or imported in US East (N. Virginia), regardless of where the origin runs, and the certificate already on the load balancer is the correct one for the origin leg. A is not possible: ACM certificates are Regional resources and cannot be copied between Regions. B removes encryption between CloudFront and the origin, which fails the reason the load balancer has a certificate at all. D solves nothing, because the viewer-facing certificate would still have to be in US East (N. Virginia) and the move adds latency for European customers.

*Where this is covered: Where certificates attach and the Region rules.*

</details>

### 2. A certificate that expired with renewal enabled (Associate)

A company requested an ACM public certificate for `reports.example.com` using DNS validation and published the validation CNAME record in Amazon Route 53. The certificate was issued, but the launch slipped and it was never attached to any AWS resource. Roughly six months later the certificate expired. The company wants certificates for planned endpoints to stay valid until they are used.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Request the certificate with email validation instead, because email-validated certificates renew without being attached.
- **B)** Attach each certificate to the resource that will use it, such as a load balancer listener, and leave the validation CNAME record in place.
- **C)** Create an EventBridge rule that calls the ACM `RenewCertificate` API every 90 days for every certificate in the account.
- **D)** Import the certificate into ACM a second time so that it is tracked as an imported certificate.

<details><summary>Answer</summary>

**Answer: B.** ACM renews a DNS-validated public certificate at the 45-day mark only when the validation CNAME records still resolve and the certificate is either in use by an AWS service or has been exported since it was issued or last renewed. A standard certificate that was never attached to anything satisfies neither branch of that second test and expires silently, so attaching it is the fix and it needs no automation. A makes the problem worse, because email-validated certificates require a person to click a renewal link and are subject to the same in-use requirement. C is unnecessary work, and forced renewal is intended for private certificates rather than as a substitute for the managed path. D removes managed renewal entirely, since imported certificates are explicitly not eligible for it.

*Where this is covered: Domain validation and managed renewal.*

</details>

### 3. Choosing a validation method for an unattended pipeline (Associate)

A platform team creates short-lived test environments many times a day with AWS CloudFormation. Each environment provisions an Application Load Balancer with an HTTPS listener and an ACM public certificate for a subdomain of a domain the team hosts in Amazon Route 53. Stack creation currently stalls for hours and eventually times out. No human should have to take an action for a stack to finish.

Which solution will meet these requirements?

- **A)** Use DNS validation for the certificate and let ACM create the validation CNAME records in the Route 53 hosted zone.
- **B)** Use email validation and configure a shared mailbox rule that automatically forwards the ACM validation messages.
- **C)** Import a wildcard certificate purchased from a third-party CA into ACM in every Region the pipeline uses.
- **D)** Increase the CloudFormation stack creation timeout so the certificate has more time to be issued.

<details><summary>Answer</summary>

**Answer: A.** A CloudFormation stack containing an ACM certificate resource stays in `CREATE_IN_PROGRESS` until validation completes, and the stall described is the signature of email validation waiting on a click. DNS validation is fully automated, and because Route 53 hosts the zone, ACM can write the CNAME records itself, so no person is involved at issuance or at renewal. B still depends on someone or something following a link within the 72 hours before the token expires, and forwarding the mail does not approve the request. C would work technically but discards managed renewal, since ACM never renews imported certificates, and it adds a purchase and an import per Region. D does not address the cause: nothing issues the certificate no matter how long the stack waits.

*Where this is covered: Domain validation and managed renewal.*

</details>

### 4. Keeping a purchased certificate alive (Associate)

A bank must keep using extended-validation certificates from its existing commercial certificate authority, because its regulator requires the organization name in the certificate. The certificates are imported into ACM and attached to Application Load Balancers. The bank wants the smallest possible chance that one expires unnoticed and wants the replacement to take effect without reconfiguring any load balancer.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable managed renewal on each imported certificate in the ACM console.
- **B)** Create an EventBridge rule for the `ACM Certificate Approaching Expiration` event that notifies the operations team, or alarm on the `DaysToExpiry` CloudWatch metric.
- **C)** Obtain the replacement certificate from the commercial CA and reimport it into ACM over the existing certificate.
- **D)** Delete the expiring certificate from ACM and import the replacement as a new certificate.
- **E)** Request an ACM public certificate for the same domain names and replace the imported certificate with it.

<details><summary>Answer</summary>

**Answer: B and C.** ACM never renews an imported certificate, so the bank owns the clock, and ACM gives it two instruments for that: the approaching-expiration event in EventBridge and the twice-daily `DaysToExpiry` metric in CloudWatch. Reimporting the replacement over the existing certificate preserves its ARN, which means every load balancer listener that references it picks up the new certificate with no reconfiguration. A is not possible: managed renewal cannot be turned on for imported certificates under any setting. D produces a new ARN, so every listener referencing the old one must be edited. E abandons the extended-validation requirement, because ACM issues domain-validated certificates only.

*Where this is covered: Domain validation and managed renewal.*

</details>

### 5. One certificate authority for sixty accounts (Professional)

A manufacturer runs 60 accounts in one AWS Organizations organization. Internal services in every account must present certificates that chain to a single corporate root that the company controls, and workload teams must be able to issue certificates for their own services without contacting the security team. The security team must keep exclusive control of the CA itself, and certificates must renew without manual work. Cost per CA is a concern.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create a private CA in the security account and share it with the workloads organizational unit using AWS Resource Access Manager, so each account requests its own certificates from it through ACM.
- **B)** Create a private CA in every workload account and configure each one as a subordinate of the corporate root.
- **C)** Issue every certificate in the security account and share each certificate with the owning workload account using AWS Resource Access Manager.
- **D)** Ensure each recipient account allows ACM to create its service-linked role, because the recipient account owns automatic renewal of certificates it issues from a shared CA.
- **E)** Create the shared CA in short-lived certificate mode so that certificate renewal is unnecessary.

<details><summary>Answer</summary>

**Answer: A and D.** Sharing the private CA rather than the certificates is the supported pattern: a resource-based policy, attached through AWS RAM, lets principals in named accounts or organizational units request certificates from the CA, and each certificate is created in and owned by the requesting account. D is the operational catch that Professional questions test, because ACM installs a service-linked role in the recipient account on first use of a shared CA, and if that role cannot be created the recipient's certificates stop renewing and only a principal in that account can fix it. B multiplies the monthly per-CA charge by 60 for no benefit, which the cost constraint rules out. C does not work, since an ACM certificate belongs to the account and Region that requested it and is not a shareable resource. E does not work at all, because ACM cannot issue certificates signed by a private CA in short-lived mode, and even setting that aside the seven-day validity cap would force constant reissuance.

*Where this is covered: Professional depth.*

</details>

### 6. A certificate for an appliance that AWS cannot manage (Professional)

An insurer runs a licensed claims appliance on Amazon EC2 instances that reads its server certificate and private key from a local configuration file and cannot be placed behind a load balancer for regulatory reasons. The certificate must be publicly trusted, must be issued and renewed centrally with the rest of the company's certificates, and the team wants AWS to signal when a renewed certificate is ready so an existing automation pipeline can push it to the instances.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Request a standard ACM public certificate, attach it to a Network Load Balancer in front of the appliance, and point clients at the load balancer.
- **B)** Buy a certificate from a commercial CA each year, import it into ACM for inventory, and copy the files onto the instances by hand.
- **C)** Create a private CA in AWS Private CA, issue a certificate from it through ACM, export it, and install the company root in every client's trust store.
- **D)** Request an ACM public certificate with export enabled, export the certificate and private key to the instances, and trigger the deployment pipeline from the ACM renewal event in Amazon EventBridge.

<details><summary>Answer</summary>

**Answer: D.** An exportable public certificate is requested with export enabled at creation, returns the certificate, chain and passphrase-protected private key through `ExportCertificate`, stays publicly trusted because it comes from Amazon Trust Services, and is renewed by ACM 45 days before its 198-day expiry, with an EventBridge event announcing that the renewed certificate is available for the pipeline to deploy. A contradicts the stem, which says the appliance cannot sit behind a load balancer. B keeps a manual purchase and a manual install every cycle, and ACM never renews an imported certificate, so it is the highest-overhead option. C produces a certificate that is not publicly trusted, and installing a corporate root in every external client's trust store is exactly the work a public certificate avoids.

*Where this is covered: Exporting certificates and AWS Private CA.*

</details>

## Summary

ACM turns certificate management into a short chain of decisions. Decide the trust model first: a public certificate from Amazon Trust Services when browsers or partners must trust it, a private certificate from AWS Private CA when only your own services must, and an imported certificate only when a requirement such as extended validation rules ACM out. Decide the validation method next, and prefer DNS, because it validates and revalidates without a person while email validation needs a click at every renewal and cannot be changed later. Then place the certificate: same Region as a load balancer or a Regional API Gateway domain, US East (N. Virginia) for CloudFront viewers and edge-optimized API domains, and one certificate per Region because none of them copy. Then check that renewal will actually happen, remembering that ACM renews only certificates that are in use, that are not imported, that have not expired, and whose validation records are still published. Finally decide whether the key must leave AWS: it can now, through an exportable public certificate or an exported private one, at a per-certificate charge and with deployment of the renewed copy left to you.

## Related units

- [AWS Key Management Service and AWS CloudHSM](kms-and-cloudhsm.md): the keys protecting data at rest, next to the certificates protecting data in transit
- [Elastic Load Balancing](../02-compute/elastic-load-balancing.md): HTTPS listeners, the certificate list with SNI, and mutual TLS trust stores
- [Amazon CloudFront](../04-networking/cloudfront.md): the distribution that reads its viewer certificate from US East (N. Virginia)
- [Amazon API Gateway](../04-networking/api-gateway.md): edge-optimized and Regional custom domain names and the certificate each one needs
- [Amazon Route 53](../04-networking/route53.md): the hosted zone that holds the validation CNAME records and the alias records pointing at the endpoints
- [WAF, Shield, Firewall Manager and Network Firewall](waf-shield-firewall-manager-and-network-firewall.md): Network Firewall TLS inspection, which requires an ACM certificate
- [AWS Organizations, IAM Identity Center and Control Tower](organizations-identity-center-and-control-tower.md): the RAM shares and organizational units that scope a private CA
- [Amazon CloudWatch](../08-management/cloudwatch.md): the DaysToExpiry metric and the alarms built on it

## Sources

- [What is AWS Certificate Manager?](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html): certificates as Regional resources, the no-copy-between-Regions rule and the CloudFront us-east-1 requirement
- [Types of certificates in AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/certificate-types.html): public, private and imported certificates
- [Choosing how to issue certificates with AWS](https://docs.aws.amazon.com/acm/latest/userguide/service-options.html): ACM, ACME and direct AWS Private CA issuance compared
- [AWS Certificate Manager public certificate characteristics and limitations](https://docs.aws.amazon.com/acm/latest/userguide/acm-certificate-characteristics.html): Amazon Trust Services, domain validation, the 198-day validity, wildcard rules and supported key algorithms
- [Request a public certificate in AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/acm-public-certificates.html): the Enable export option at request time and the pre-17 June 2025 exclusion
- [Validate domain ownership for AWS Certificate Manager public certificates](https://docs.aws.amazon.com/acm/latest/userguide/domain-ownership-validation.html): DNS, email and HTTP validation, and the one-way email-to-DNS restriction
- [AWS Certificate Manager DNS validation](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html): the CNAME record format, reuse across Regions and deleting the record to stop renewal
- [AWS Certificate Manager email validation](https://docs.aws.amazon.com/acm/latest/userguide/email-validation.html): the five administrative addresses, the 72-hour token and the end of WHOIS validation
- [Managed certificate renewal in AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/managed-renewal.html): the eligibility and ineligibility list and the unchanged ARN
- [Renewal for domains validated by DNS](https://docs.aws.amazon.com/acm/latest/userguide/dns-renewal-validation.html): the 45-day check, the in-use requirement and the 395-to-198 day transition
- [Private certificate renewal in AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/renew-private-cert.html): renewal at 60 days and the exclusion of certificates issued with IssueCertificate
- [AWS Certificate Manager exportable public certificates](https://docs.aws.amazon.com/acm/latest/userguide/acm-exportable-certificates.html): 198-day validity, renewal at 45 days, the additional charge and deployment responsibility
- [Revoke an AWS Certificate Manager public certificate](https://docs.aws.amazon.com/acm/latest/userguide/revoke-certificate.html): revocation limited to exported certificates, permanence and the 24-hour propagation
- [Import certificates into AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/import-certificate.html): no managed renewal, reimport preserving the ARN and the per-Region import rule
- [Private certificates in AWS Certificate Manager](https://docs.aws.amazon.com/acm/latest/userguide/private-certificates.title.html): the 13-month validity, the algorithm rules and the absence of validation
- [Conditions for using AWS Private CA to sign ACM private certificates](https://docs.aws.amazon.com/acm/latest/userguide/ca-access.html): CreatePermission for single-account issuance and PutPolicy for cross-account
- [Managed automation with integrated services](https://docs.aws.amazon.com/acm/latest/userguide/acm-services.html): the integrated service list, the CloudFront Region note and the Nitro Enclaves requirement for EC2
- [ACME certificate automation](https://docs.aws.amazon.com/acm/latest/userguide/acm-acme.html): the managed ACME server, client-held private keys, 45-day validity and no binding to integrated services
- [Amazon EventBridge support for ACM](https://docs.aws.amazon.com/acm/latest/userguide/supported-events.html): approaching-expiration events at 45 and 30 days and PutAccountConfiguration
- [Supported CloudWatch metrics](https://docs.aws.amazon.com/acm/latest/userguide/cloudwatch-metrics.html): the DaysToExpiry metric published twice a day
- [Quotas](https://docs.aws.amazon.com/acm/latest/userguide/acm-limits.html): 2,500 certificates, 5,000 per year, 10 domain names by default and 200 private CAs
- [What is AWS Private CA?](https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html): root and subordinate hierarchies, Regional CAs and supported algorithms
- [Understand AWS Private CA CA modes](https://docs.aws.amazon.com/privateca/latest/userguide/short-lived-certificates.html): general-purpose and short-lived modes, the seven-day cap and the ACM exclusion
- [Attach a policy for cross-account access](https://docs.aws.amazon.com/privateca/latest/userguide/pca-ram.html): RAM sharing of a CA and the recipient's responsibility for autorenewal
- [AWS Private CA pricing](https://aws.amazon.com/private-ca/pricing/): 400 USD and 50 USD per CA per month, the 30-day trial and the charge on first export
- [AWS Certificate Manager pricing](https://aws.amazon.com/certificate-manager/pricing/): no charge for public certificates on integrated services and the per-name charge for exportable certificates
- [SSL certificates for your Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/https-listener-certificates.html): the default certificate, the certificate list and SNI selection
- [Quotas for your Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-limits.html): 25 certificates per load balancer excluding the default
- [Requirements for using alternate domain names and HTTPS](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html): the us-east-1 rule for viewers and the any-Region rule for an Elastic Load Balancing origin
- [Set up an edge-optimized custom domain name in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-edge-optimized-custom-domain-name.html): the us-east-1 certificate requirement
- [Set up a Regional custom domain name in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-regional-api-custom-domain-create.html): the certificate must be in the same Region as the API
