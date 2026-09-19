# Amazon Cognito

**Where it sits on the exams.** **Amazon Cognito** is the identity platform for the people who use your application: a user directory, an authentication server that issues OpenID Connect (OIDC) tokens, and a credentials broker that turns proof of sign-in into temporary AWS credentials. It answers who the customer of your web or mobile application is, which is a different question from who your employees are, and the exams keep those apart deliberately. The SAA-C03 guide names Cognito in task 1.2, "Security services with appropriate use cases, for example Amazon Cognito", and the service carries the application half of task 1.1's federation work; it is in the SAP-C02 in-scope list and appears in tasks 1.2 and 2.3 wherever a question integrates a third-party identity provider or prescribes security controls for an application. The rule of thumb fits in one sentence: a user pool authenticates users and hands your application JSON Web Tokens (JWTs), an identity pool accepts proof of authentication and hands your application temporary AWS credentials, and most designs use both, in that order.

## What Amazon Cognito is: user pools compared with identity pools

Cognito has exactly two components, usable independently or together, and almost every wrong answer on this service comes from confusing them.

A **user pool** is a user directory and an OIDC identity provider. It stores profiles, runs sign-up and sign-in, enforces a password policy, verifies email addresses and phone numbers, handles forgotten passwords, and returns three tokens on a successful authentication. Users created in the directory are *local users*; users who arrived through a third-party provider are *federated users*, and Cognito creates a profile for them too, so your backend sees one token format wherever the person signed in. AWS is explicit that a user pool needs nothing else: "User pools don't require integration with an identity pool. From a user pool, you can issue authenticated JWTs directly to an app, a web server, or an API."

An **identity pool**, historically called Cognito federated identities, holds no passwords and runs no sign-in pages. It is a collection of identity records that you authorize to receive temporary AWS credentials. You present a proof of authentication, and it brokers a session from **AWS Security Token Service (AWS STS)**, the service that issues temporary credentials, taught in [AWS Identity and Access Management](iam.md). The proof can be an ID token from a user pool or any OIDC provider, a SAML 2.0 assertion, a social provider's access token, a token you mint through developer-authenticated identities, or nothing at all, which is how guest access works. Back comes an access key, secret key and session token scoped to a role in **AWS Identity and Access Management (IAM)**, the service that decides which principal may perform which action on which resource, so the client can call **Amazon S3**, the object storage service, or **Amazon DynamoDB**, the managed key-value database, with that user's own permissions.

Used together the sequence is: sign in to the user pool, receive OAuth 2.0 tokens, present the ID token to the identity pool, receive temporary AWS credentials. Read the table by finding what the scenario needs at the end of the flow, then reading left to the component that produces it.

| Component | What it produces | What it authenticates against | What the application does with the result | The wording that selects it |
|---|---|---|---|---|
| User pool | An ID token and an access token, both JWTs signed with RS256, plus a refresh token that is encrypted and opaque to everyone but the user pool | Its own user directory, or a SAML 2.0, OIDC or social provider it federates to on your behalf | Reads the ID token to know who the user is, sends the access token to an API as a bearer token, refreshes with the refresh token | "Sign up and sign in users", "add authentication to the application", "sign in with Google or the corporate SAML provider", "protect an API with a managed authorizer" |
| Identity pool | Temporary AWS credentials from AWS STS, scoped to an IAM role, valid one hour in the default flow | A token or assertion from a trusted provider, including a user pool, or nothing at all for guest access | Signs AWS API requests directly from the client, such as writing to an S3 prefix or reading a DynamoDB item | "Users must access AWS services directly", "grant temporary AWS credentials", "allow unauthenticated or guest access", "different IAM permissions for different classes of user" |

The discriminator is the phrase "AWS credentials". If the scenario ends with the client calling an AWS service API, an identity pool is in the answer. If it ends with the client calling your API or your web server, a user pool alone is enough and an identity pool is the distractor.

## Managed login, the classic hosted UI, and federation

Assigning a domain to a user pool turns on **managed login**, three things at once: an OAuth 2.0 and OIDC authorization server with `authorize`, `token`, `userInfo` and `revoke` endpoints; ready-made web pages for sign-up, sign-in, multi-factor authentication and password reset; and a service provider that talks to your SAML 2.0, OIDC and social providers so your application never has to. The domain is a Cognito prefix domain such as `https://<prefix>.auth.<region>.amazoncognito.com` or a custom domain of your own with a certificate from **AWS Certificate Manager (ACM)**, the certificate issuance and renewal service.

The naming changed and the exams have not all caught up. Managed login is the current front end, introduced in November 2024; the **classic hosted UI** is the first-generation version, still supported, with a simpler design and fewer capabilities. Passkey sign-in is not available on it, and it is the only front end offered on the Lite feature plan. Managed login adds a visual branding editor in the console on the Essentials and Plus plans; the hosted UI takes an uploaded logo and CSS file.

Two behaviors decide questions. The first is the one-hour session cookie: after a successful interactive sign-in, Cognito sets a browser cookie that lets the same user sign in again for one hour without re-entering credentials, and using that cookie does not extend it, so token lifetimes shorter than an hour do not shorten the browser session. The second is scope: managed login covers sign-up, sign-in, MFA completion, passkey registration and password management and nothing else. Self-service profile management you build yourself, and managed login does not support the custom authentication challenge triggers described below.

Federation makes the user pool a bridge. To your identity provider the user pool is a service provider; to your application it is the identity provider. For SAML 2.0 providers such as Active Directory Federation Services, Okta or Shibboleth, you register the user pool with an SP entity ID of `urn:amazon:cognito:sp:<user pool ID>` and an assertion consumer service URL of `https://<your domain>/saml2/idpresponse`, and Cognito converts the assertion into its own tokens. OIDC providers work the same way with a client ID and secret, and the supported social providers are Facebook, Google, Login with Amazon and Sign in with Apple. All third-party sign-in requires a domain, because the redirect flow runs through the managed login endpoints. Attribute mapping controls which provider claims land on which user pool attributes, a federated profile carries an `identities` claim naming the provider, and Cognito creates a group per provider named `<user pool ID>_<provider name>`. Federated users cannot sign in through API operations such as `InitiateAuth`: they go through the `authorize` or `login` endpoints. Because the external provider owns the authentication, Cognito's own MFA and threat protection do not apply to federated users.

## Tokens, scopes and groups

A successful authentication returns three tokens. The **ID token** carries claims about identity: `sub`, `email`, `cognito:username`, the `identities` claim for federated users, and `cognito:groups`. The **access token** carries the `scope` claim and also `cognito:groups`, and it is what an API inspects when the question is authorization rather than identity. The **refresh token** is encrypted and opaque; only the user pool can read it. ID and access tokens are signed with RS256 and must be verified against the public keys at the pool's `jwks_uri` endpoint before any claim is trusted, and because they are signed with different keys they are verified independently.

Lifetimes are per app client and are a recurring detail. ID and access tokens default to one hour and are configurable from 5 minutes to 1 day. Refresh tokens default to 30 days and are configurable from 60 minutes to 10 years. Optional refresh token rotation issues a new refresh token on every refresh and invalidates the old one after a grace period of up to 60 seconds; it is incompatible with the `REFRESH_TOKEN_AUTH` flow, so applications must call `GetTokensFromRefreshToken` instead. GlobalSignOut and AdminUserGlobalSignOut revoke all of a user's refresh, ID and access tokens, while RevokeToken kills only that one refresh token and the tokens issued from it. Note that a revoked JWT still verifies in a local library until it expires, so revocation is not instant to an application that checks signatures offline. Revoking a refresh token also invalidates the access tokens issued from it, which is the only way to end a session early, since a JWT cannot be recalled once handed out.

Scopes come from resource servers: you define one with an identifier such as `https://api.example.com` and custom scopes such as `orders.read`, then allow a subset on each app client. The client credentials grant issues an access token with scopes and no user at all, which is the machine-to-machine pattern.

Groups are how a user pool expresses coarse authorization and how it reaches into IAM. A group has a name, an optional precedence value and an optional IAM role ARN, and membership appears in the `cognito:groups` claim of both tokens. When roles are attached, the ID token also carries `cognito:roles`, the role ARNs available to the user, and `cognito:preferred_role`, the role from the group with the best precedence. Precedence is a non-negative number where zero is best and lower wins; if two groups tie and carry different role ARNs, `cognito:preferred_role` is not set. Nothing about a group grants AWS access on its own: the role takes effect only when an identity pool is configured to choose the role from the token. Groups cannot be nested.

Claims are not fixed: a pre token generation Lambda trigger adds, modifies and suppresses them at runtime. Customizing ID token claims works on every feature plan; customizing access token scopes and claims requires Essentials or Plus, the next-generation Cognito infrastructure, which some existing pools do not yet have and event version 2 on the trigger.

## Lambda triggers, multi-factor authentication and the feature plans

Cognito calls **AWS Lambda**, the serverless function service, at several points in a user pool's workflow, and knowing what each is for decides between a trigger and a custom build. *Pre sign-up* validates or auto-confirms a registration and can reject it, and *post confirmation* runs after the account is confirmed, typically to write a row to an application database. *Pre authentication* accepts or denies a sign-in attempt before credentials are checked, and *post authentication* logs a successful one. *Pre token generation* rewrites token claims. *Migrate user* looks the user up in an existing directory when they are not found in the pool and creates them on the spot, moving a legacy directory without asking anyone to reset a password. *Custom message* rewrites verification and invitation messages, the two *custom sender* triggers hand email and SMS delivery to a third-party provider, and *inbound federation* transforms a federated user's attributes before the profile is created. The three custom authentication challenge triggers, *define auth challenge*, *create auth challenge* and *verify auth challenge response*, together build an authentication flow of your own design.

The operational constraint matters more than the list. Except for the custom sender triggers, Cognito invokes these functions synchronously and expects a response within five seconds, and that timeout cannot be changed. A function that errors, or fails to return the request and response objects, fails the user's operation, which is why a migrate user trigger querying a slow on-premises directory is a real failure mode rather than a theoretical one. Adding a trigger in the console attaches the invoke permission to the function automatically; a cross-account function needs that resource-based policy added by hand and can only be configured through the API, the CLI or **AWS CloudFormation**, the infrastructure as code service.

Multi-factor authentication applies to local users only, because federated users are authenticated entirely by their own provider. The factors are SMS text message, email one-time code and a time-based one-time password (TOTP) from an authenticator application, and MFA is set to off, optional or required for the whole pool. When it is required, every user must register a factor and managed login prompts them to; when it is optional, managed login does not prompt and you build that flow. Passkeys backed by FIDO2 authenticators are a first factor rather than a second. SMS is delivered through **Amazon SNS**, the publish and subscribe messaging service, and email through **Amazon SES**, the managed email sending service, each billed separately.

All of this is gated by the user pool's feature plan, and the plan names are new enough to be worth learning exactly. **Lite** is the low-cost plan holding the capabilities that existed before November 2024, with the classic hosted UI as its only login page. **Essentials** is the default for new user pools and adds managed login with the branding editor, email MFA, passkey and passwordless one-time-code sign-in, choice-based sign-in, and access token customization. **Plus** includes everything in Essentials and adds **threat protection**, which AWS renamed from *advanced security features*: compromised credentials detection that compares submitted passwords against public breach data, adaptive authentication that scores each sign-in on location and device and can require MFA or block it, IP always-allow and always-block lists, and export of user activity and risk logs to S3, **Amazon CloudWatch** Logs, the log store of the monitoring service, or **Amazon Data Firehose**, the streaming delivery service. It runs in audit mode, recording and publishing metrics only, or full-function mode, where it acts. The old bundle was split rather than renamed wholesale: threat protection went to Plus, while access token customization, also billed under it, now sits in Essentials. Threat protection cannot be applied to federated sign-in, and compromised credentials detection does not run in secure remote password or custom authentication flows.

## Identity pools: authenticated and guest roles, and how the role is chosen

An identity pool has two default IAM roles, one for authenticated identities and one for unauthenticated identities, and guest access can be turned off entirely. AWS is direct about the asymmetry: the guest role should be more restrictive, because anyone who can reach your application can assume it. Both roles need a trust policy of a specific shape. The principal is the federated service `cognito-identity.amazonaws.com`, the action is `sts:AssumeRoleWithWebIdentity`, and IAM refuses to save the policy without a condition on `cognito-identity.amazonaws.com:aud` naming your identity pool ID, so another account's pool cannot assume your role. A second condition on `cognito-identity.amazonaws.com:amr` restricts the role to `authenticated` or `unauthenticated` sessions.

```json
"Condition": {
  "StringEquals": {"cognito-identity.amazonaws.com:aud": "us-east-1:11111111-2222-3333-4444-555555555555"},
  "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "authenticated"}
}
```

There are two credential flows. The enhanced flow, the default, is `GetId` then `GetCredentialsForIdentity`: the identity pool decides which role to request and returns credentials valid for one hour. The basic, or classic, flow is `GetId`, `GetOpenIdToken`, then a direct `AssumeRoleWithWebIdentity` call to AWS STS, which lets the application name any role whose trust policy permits it and request a custom session duration. It must be activated explicitly on the pool.

Role resolution is the part that is tested. When several roles could apply, Cognito evaluates in a fixed order. A `CustomRoleArn` passed to `GetCredentialsForIdentity` wins if it matches a role in the `cognito:roles` claim, and the request is denied if it does not match. Otherwise, if `cognito:preferred_role` is set, that role is used. Otherwise the pool's role resolution setting decides, and it is either "use default authenticated role" or "deny the request". Two prerequisites hang off that: group roles only reach the credentials call when the identity pool's role selection is set to choose the role from the token, and a pre-token trigger or rule that never produces a preferred role leaves you relying on the fallback.

Rule-based mapping is the alternative to groups. Each rule names a claim, a match type of `Equals`, `NotEqual`, `StartsWith` or `Contains`, a value and a role; rules are evaluated in order, the first match wins, and the limit of 25 rules per provider cannot be raised. Attributes for access control is the third option: claims become principal tags on the STS session and policies use `aws:PrincipalTag` conditions, which reaches per-user isolation without a role per user. AWS attaches one warning: never map a claim the end user can set on themselves to a role with elevated permissions, because that turns an attribute update into privilege escalation.

## Putting Cognito in front of an application: ALB, API Gateway and AWS WAF

An **Application Load Balancer (ALB)**, the Layer 7 load balancer taught in [Elastic Load Balancing](../02-compute/elastic-load-balancing.md), can authenticate users before a request reaches a target. You add an `authenticate-cognito` action to a listener rule ahead of the `forward` action, and the load balancer runs the whole authorization code flow; an `authenticate-oidc` variant does the same for any OIDC provider. Both work only on HTTPS listeners. The prerequisites are a user pool, an app client with a client secret using the code grant, a user pool domain, and a callback URL of `https://<load balancer DNS name>/oauth2/idpresponse`.

Three configuration details decide answers. `OnUnauthenticatedRequest` is `authenticate` by default, which redirects anonymous users to sign in; `allow` passes them through without claims so the application can render a public view; `deny` returns HTTP 401. `SessionTimeout` defaults to 7 days and can be as short as 1 second. And the load balancer forwards the user to the target in three headers: `x-amzn-oidc-data`, a signed JWT of the claims, plus the unsigned `x-amzn-oidc-accesstoken` and `x-amzn-oidc-identity`. Only the first is signed, so a target must verify its signature and confirm the `signer` field equals the load balancer's ARN before trusting anything. The ALB does not pass the ID token, and if claims and access token together exceed 11 KB it returns HTTP 500. When **Amazon CloudFront**, the content delivery network, sits in front, forward all headers, query strings and cookies.

On the API side, **Amazon API Gateway**, the managed API front door, validates user pool tokens itself. A REST API uses a Cognito user pool authorizer that checks an ID or access token against the pool and passes the claims to the integration; an HTTP API uses a JWT authorizer that checks the same tokens and can require an OAuth scope on each route. The authorizer types and their caching behavior belong to [Amazon API Gateway](../04-networking/api-gateway.md); what matters here is which token to send, which is the access token when authorization is by scope and the ID token when the backend needs attributes. If the API uses IAM authorization instead, the caller needs identity pool credentials rather than a token, and the same is true of an **AWS AppSync** GraphQL API configured for IAM. Finally, a user pool can be associated with one **AWS WAF** web ACL, the web application firewall's rule container, which inspects requests to managed login, the classic hosted UI and the user pools API endpoints, and blocked requests never reach the request rate quotas. AWS WAF cannot match on personally identifiable information here, so rules target IP addresses and requested operations rather than usernames or passwords.

## Pricing shape, the limits that bite, and choosing against IAM Identity Center

Cognito user pools bill by monthly active user (MAU). A user counts once in a calendar month if there is any identity operation on them: sign-up, administrative creation, sign-in, a challenge response, a profile read or update, or a self-service password reset. Bulk CSV import does not create MAUs. Each feature plan has its own per-MAU rate, Lite cheapest and Plus most expensive, and Essentials is the default for new pools. The free tier is 10,000 MAUs per month per account or per organization on Lite and Essentials, and there is none on Plus. Users who sign in through a SAML 2.0 or OIDC provider are metered separately at their own rate with a free tier of 50 MAUs regardless of plan, which is the number that surprises people running workforce federation through a user pool. Machine-to-machine token requests have no free tier, identity pools are free, SMS and email are billed by Amazon SNS and Amazon SES, and multi-Region replication carries an add-on charge.

The limits worth carrying into the exam are these. A user pool holds 40 million users by default, an account holds 1,000 user pools per Region, 1,000 app clients per pool and 300 identity providers per pool, and all of those are adjustable. Two are not: 50 custom attributes per user pool, and 25 role-mapping rules per provider in an identity pool. Request rates are pooled per category across every user pool in an account and Region, with `UserAuthentication` at 120 requests per second and `UserFederation` at 25, both adjustable. And Cognito's built-in email sender is capped at 50 messages per day per account, a development convenience only: any real workload configures Amazon SES.

The decision the exam asks most often about this service is not a Cognito configuration at all. It is Cognito against **AWS IAM Identity Center**, the workforce single sign-on service that connects an external identity source to permission sets across every account in an organization, taught in [AWS Organizations, IAM Identity Center and AWS Control Tower](organizations-identity-center-and-control-tower.md). The boundary is the population, not the protocol. Identity Center and IAM roles handle workforce and workload identities that call AWS APIs or open the AWS access portal; Cognito handles the customers of your application. So "employees need single sign-on to 30 AWS accounts with their corporate credentials" is Identity Center every time, and a Cognito user pool federated to the same corporate provider is the plausible distractor that costs more, scales worse and produces no account access. Conversely, "two million consumers sign in to our mobile app" is Cognito. A partner portal that is an application rather than an AWS account belongs to Cognito with SAML federation to the partner's provider, billed at the federated MAU rate.

## Professional depth

Multi-tenancy is where an Associate question becomes a Professional one. AWS documents five isolation patterns, in descending order of separation: a user pool per tenant, an app client per tenant, a group per tenant, a custom attribute per tenant, and a custom scope per tenant. A pool per tenant gives the cleanest blast radius and per-tenant branding and password policy, but it runs into the 1,000 pools per Region quota, so it suits tens of large tenants rather than thousands of small ones. Group-based and attribute-based tenancy keep one directory and push isolation into token claims and IAM conditions.

Multi-Region replication creates a secondary replica user pool in another Region that shares the primary's user pool ID, but the default issuer is Region-specific, so a replica issues tokens under its own issuer URL. AWS recommends the updated issuer for replication, and that issuer type works with neither Application Load Balancer authentication nor an API Gateway Cognito authorizer, both of which this unit teaches. The constraints define the recovery design: the pool must be on Essentials or Plus and encrypted with a multi-Region customer managed key from **AWS KMS**, the managed key service taught in [AWS KMS and AWS CloudHSM](kms-and-cloudhsm.md), the replica starts inactive, and there can be at most one secondary. In a failover the replica signs users in and issues tokens, but it cannot create users, reset passwords or update profiles, TOTP MFA is unavailable there, federated users can only sign in if they previously signed in to the primary, and lockout counters are not synchronized. The honest reading for a disaster recovery question is that this is authentication continuity for existing users, not an active-active directory, and the failover interface must hide registration and password reset.

Scale pressure shows up as throttling first. The per-category quotas are account-wide and Region-wide, so a hundred user pools share one 120 requests per second `UserAuthentication` allowance. Provisioned limits raise adjustable categories through `UpdateProvisionedLimit` after **Service Quotas**, the service that displays and raises account limits, approves a higher ceiling, with one trap: if the pool uses managed login, `UserAuthentication` and `UserFederation` must go through a Service Quotas request instead. For machine-to-machine traffic the cheaper fix is caching: front the token endpoint with an API Gateway cache keyed on the requested scopes and client credentials, so a fleet reuses one access token instead of minting thousands.

Migration has two shapes and they are not interchangeable. A CSV import job moves profiles in bulk but cannot move passwords, so every imported user must reset; the migrate user trigger moves people one at a time as they sign in and keeps their passwords. When a question says "users must not have to reset their passwords", the trigger is the answer and the import job is the distractor.

Finally, treat threat protection logs as a security data source rather than a console feature. Exporting user activity and risk evaluations to S3, CloudWatch Logs or Amazon Data Firehose puts sign-in risk next to the rest of the organization's findings in a security account, which is what a centralized detection question asks for.

## Worked scenario

A retailer runs a mobile app and a website for four million shoppers, a partner portal used by staff at 60 supplier companies, and an internal operations console. Shoppers sign in with an email address or with Google, suppliers must use their own corporate directories, and shoppers upload review photos that the team wants going straight to S3 rather than through application servers. Compliance has asked for credential stuffing detection, and internal staff already reach AWS accounts through IAM Identity Center.

One user pool serves shoppers and suppliers, on the Plus feature plan so that compromised credentials detection and adaptive authentication are available, with managed login on a custom domain and an ACM certificate. Google is added as a social provider and each supplier's SAML 2.0 provider is registered separately. Application groups named `shopper`, `supplier` and `supplier-admin` carry precedence values and IAM role ARNs. MFA is required, with TOTP and email one-time codes; because federated suppliers authenticate at their own provider, their MFA is their employer's responsibility. A pre sign-up trigger rejects disposable email domains and a pre token generation trigger adds the loyalty tier as a claim. An AWS WAF web ACL on the user pool rate-limits the sign-in endpoints, and threat protection logs are exported to the security account.

For the photo uploads an identity pool trusts the user pool, with role selection set to choose the role from the token so that `cognito:preferred_role` decides, and with attributes for access control mapping the `sub` claim to a principal tag. The shopper role allows `s3:PutObject` only on `arn:aws:s3:::reviews-bucket/${aws:PrincipalTag/sub}/*`, so each shopper writes only under their own prefix and no role proliferates. Guest access is off. The shopping API is a REST API with a Cognito user pool authorizer reading the access token and resource server scopes separating read from write. The operations console sits behind an ALB with an `authenticate-cognito` listener rule, and its targets verify the `x-amzn-oidc-data` signature. Nothing about AWS account access goes near Cognito: that stays with IAM Identity Center.

When the exam builds a question on this scenario it asks how shoppers write to their own S3 prefix with the least operational overhead. The keyed answer is a user pool for sign-in plus an identity pool that exchanges the ID token for temporary AWS credentials, with a group role or principal tags scoping the prefix. Long-term IAM user keys in the app, proxying every upload through a Lambda function, and one shared role for all shoppers are the distractors, and they break least privilege, add overhead, or both.

## Exam lens

- "Add sign-up and sign-in to a web or mobile application" maps to a Cognito user pool; an IAM user per customer is never the answer.
- "Users must access AWS services such as S3 or DynamoDB directly" maps to an identity pool exchanging a token for temporary AWS credentials.
- "Employees need single sign-on to multiple AWS accounts" maps to IAM Identity Center; a Cognito user pool is the distractor for workforce access to AWS.
- "Allow unauthenticated or guest users limited access" maps to an identity pool's unauthenticated role, scoped more tightly than the authenticated role.
- "Different permissions for different classes of user" maps to user pool groups with IAM roles and an identity pool set to choose the role from the token, or to rule-based mapping on a claim.
- "Authenticate users before the request reaches the application, with no application code" maps to an ALB `authenticate-cognito` listener rule on an HTTPS listener.
- "Validate the token at the API with no custom code" maps to a Cognito user pool authorizer on a REST API or a JWT authorizer on an HTTP API; a Lambda authorizer is the distractor when no custom logic is required.
- "Detect compromised passwords and risky sign-ins" maps to threat protection on the Plus feature plan, formerly advanced security features.
- "Migrate an existing directory without forcing password resets" maps to the migrate user Lambda trigger; the CSV import job cannot carry passwords.
- "Add a custom claim to the token" maps to the pre token generation trigger; access token customization needs Essentials or Plus.
- "Keep users signing in when a Region is impaired" maps to multi-Region replication, remembering that the replica cannot create users or reset passwords.

## Knowledge check

### 1. Photo uploads from a mobile app (Associate)

A company is building a mobile app whose users sign in with an email address and password. After signing in, each user uploads images from the device. The company wants the uploads to go directly to an Amazon S3 bucket instead of passing through the application servers, and each user must be able to write only to their own prefix. No long-term credentials may be stored on the device.

Which solution will meet these requirements?

- **A)** Create an IAM user for each app user and embed its access keys in the app after sign-in.
- **B)** Create a Cognito user pool and send the ID token to Amazon S3 as the authorization header on each `PutObject` request.
- **C)** Create a Cognito user pool for sign-in and a Cognito identity pool that trusts it, and have the app exchange the ID token for temporary AWS credentials scoped by an IAM role.
- **D)** Create a Cognito identity pool with guest access enabled and attach a role that allows `s3:PutObject` on the bucket.

<details><summary>Answer</summary>

**Answer: C.** Only an identity pool produces AWS credentials, and it does so by exchanging the user pool's ID token for a temporary session from AWS STS, which the app uses to sign the `PutObject` call with the role's permissions. A creates one long-term credential per user, which is unmanageable and violates the no-long-term-credentials requirement. B is not how Amazon S3 authorizes: it expects SigV4-signed requests from an AWS principal, not a user pool JWT. D gives every anonymous caller the same write permissions with no way to separate one user's prefix from another's.

*Where this is covered: What Amazon Cognito is: user pools compared with identity pools.*

</details>

### 2. Branded sign-in pages with social sign-in (Associate)

A retailer wants to add sign-up and sign-in to a new web application. Customers must be able to register with an email address or sign in with their Google account. The sign-in pages must carry the retailer's logo and colors and be reached at `login.example.com`. The development team has no capacity to build authentication screens.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create a Cognito user pool on the Essentials feature plan, add Google as a social identity provider, assign a custom domain with an AWS Certificate Manager certificate, and style the pages in the managed login branding editor.
- **B)** Create a Cognito identity pool with Google as an authentication provider and build sign-in screens in the application.
- **C)** Run an open-source identity server on Amazon EC2 instances behind an Application Load Balancer and configure Google as an upstream provider.
- **D)** Create a Cognito user pool on the Lite feature plan and use the managed login branding editor to apply the retailer's logo and colors.

<details><summary>Answer</summary>

**Answer: A.** Managed login supplies hosted sign-up, sign-in and password pages, a custom domain gives the `login.example.com` address, and the visual branding editor applies the logo and colors without any front-end code. B skips the directory entirely: an identity pool has no sign-in pages and no user profiles, so the team would still build the screens. C is a custom build of something AWS already manages. D never adds Google as a provider and never assigns a custom domain, so it fails two stated requirements outright; the branding editor is also unavailable on Lite, which only offers the classic hosted UI with file-based branding.

*Where this is covered: Managed login, the classic hosted UI, and federation.*

</details>

### 3. Authorizing an API by role (Associate)

A company exposes a REST API through Amazon API Gateway. End users sign in to a Cognito user pool. Editors may call the write methods and readers may call only the read methods. The company wants the API to enforce this without writing custom authorization code, and does not want to give end users AWS credentials.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create a Cognito identity pool and give each user temporary AWS credentials, then enable IAM authorization on the API methods.
- **B)** Create user pool groups for editors and readers and place each user in the group that matches their job.
- **C)** Issue an API key to each user and place the editors in a usage plan with a higher quota.
- **D)** Configure a Cognito user pool authorizer on the API and have the application send the user's token in the `Authorization` header.
- **E)** Store the user's role in a DynamoDB table and look it up in the integration function on every request.

<details><summary>Answer</summary>

**Answer: B and D.** Group membership travels in the `cognito:groups` claim of both the ID token and the access token, and a Cognito user pool authorizer validates the token against the pool and passes those claims to the integration, so the API enforces the split with no custom authorization code. A contradicts the stated requirement that end users must not receive AWS credentials. C misuses API keys, which AWS states are not an authentication or authorization mechanism and which meter rather than secure. E is custom authorization code on every request, which the requirement excludes.

*Where this is covered: Tokens, scopes and groups.*

</details>

### 4. Corporate sign-in to many AWS accounts (Professional)

An enterprise runs 45 AWS accounts under one organization. Employees authenticate against a corporate SAML 2.0 identity provider. The security team wants employees to sign in once with their corporate credentials and then assume job-function roles in any account they are entitled to, with one federation trust and one certificate to maintain. A separate customer-facing application in the same organization already uses a Cognito user pool.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Extend the existing Cognito user pool with the corporate SAML provider and create an identity pool in each account that exchanges the user pool token for account credentials.
- **B)** Create a SAML identity provider object and a set of IAM roles in each of the 45 accounts, and point the corporate provider at all of them.
- **C)** Create a second Cognito user pool for employees, put them in groups, and map each group to an IAM role through an identity pool.
- **D)** Enable AWS IAM Identity Center in the organization, connect the corporate SAML provider as the identity source, and assign permission sets to groups across the accounts.

<details><summary>Answer</summary>

**Answer: D.** Identity Center is the workforce service: one federation trust and one certificate, with permission sets that create and maintain the matching IAM role in every assigned account. A and C are the same mistake in two costumes, using Cognito for workforce access to AWS accounts; both add a user directory that duplicates the corporate one, and an identity pool per account multiplies the objects to maintain rather than reducing them. B works but leaves 45 identity provider objects and 45 sets of roles in step with each other, which is exactly the overhead the requirement excludes.

*Where this is covered: Pricing shape, the limits that bite, and choosing against IAM Identity Center.*

</details>

### 5. Moving an existing directory (Associate)

A company is replacing a self-managed LDAP directory of 900,000 customers with a Cognito user pool. The directory stores password hashes that cannot be exported in a usable form. Customers must not be asked to reset their passwords, and the company wants to decommission the old directory once most customers have signed in at least once.

Which solution will meet these requirements?

- **A)** Export the customer records to a CSV file and run a user import job into the user pool.
- **B)** Configure a migrate user Lambda trigger on the user pool that validates the submitted credentials against the LDAP directory and creates the Cognito profile at first sign-in.
- **C)** Configure a pre sign-up Lambda trigger that reads the LDAP directory and auto-confirms each new registration.
- **D)** Register the LDAP directory as a SAML 2.0 identity provider in the user pool.

<details><summary>Answer</summary>

**Answer: B.** The migrate user trigger runs when a user is not found in the pool, checks the password against the old directory, and creates the Cognito profile on the spot, so nobody resets anything and the old directory can be retired as the tail shrinks. A moves profiles but cannot carry passwords, so every imported customer would have to reset. C fires during sign-up, not sign-in, so it never sees an existing customer's credentials. D is a real feature used for the wrong job: LDAP is not a SAML 2.0 identity provider, and federating would leave authentication permanently on the old system rather than migrating off it.

*Where this is covered: Lambda triggers, multi-factor authentication and the feature plans.*

</details>

### 6. Credential stuffing against a consumer application (Professional)

A media company's consumer application has 3 million monthly active users in a Cognito user pool currently on the Essentials feature plan. Attackers are replaying credentials leaked from other sites. The security team wants Cognito to block sign-ins that use known-breached passwords, to require MFA automatically when a sign-in looks risky, and to deliver the per-session risk records into the organization's central security account for correlation. Existing federated users authenticate at a partner's OIDC provider and are out of scope.

Which solution will meet these requirements?

- **A)** Keep the Essentials plan and attach an AWS WAF web ACL with the account takeover prevention managed rule group to the user pool.
- **B)** Keep the Essentials plan, set MFA to required for every user, and enable Amazon CloudWatch alarms on failed sign-in metrics.
- **C)** Switch the user pool to the Plus feature plan, turn on threat protection in full-function mode with compromised credentials blocking and adaptive authentication, and export the user activity logs to the security account.
- **D)** Switch the user pool to the Lite feature plan and add a pre authentication Lambda trigger that calls a third-party breach API before every sign-in.

<details><summary>Answer</summary>

**Answer: C.** Threat protection, formerly advanced security features, is the Plus plan, and full-function mode is what actually blocks compromised credentials and raises an MFA requirement on a risky session; its user activity and risk logs export to Amazon S3, CloudWatch Logs or Amazon Data Firehose for central analysis. A is not possible: a web ACL that uses the account takeover prevention rule group cannot be associated with a user pool. B makes every user do MFA on every sign-in, which is not risk-based and does not detect breached passwords. D moves to a less capable plan and rebuilds part of a managed feature in a function that must answer within five seconds.

*Where this is covered: Lambda triggers, multi-factor authentication and the feature plans.*

</details>

### 7. Browsing before signing in (Associate)

A news publisher wants anonymous visitors to read a catalog of headlines stored in an Amazon DynamoDB table directly from the browser, with no sign-in. Visitors who create an account must additionally be able to write comments to a second table. Anonymous visitors must never be able to write.

Which solution will meet these requirements?

- **A)** Create a Cognito user pool with a shared guest account and give the credentials to the front-end code.
- **B)** Make the DynamoDB table publicly readable and restrict writes with a condition on the caller's IP address.
- **C)** Create a Cognito user pool and use its access token as the credential for DynamoDB read requests.
- **D)** Create a Cognito identity pool with guest access activated, attach an unauthenticated role that allows only read on the catalog table, and attach an authenticated role that also allows write on the comments table.

<details><summary>Answer</summary>

**Answer: D.** Identity pools issue credentials to unauthenticated identities as well as authenticated ones, and the two default roles are exactly the mechanism for giving guests a narrower policy than signed-in users. A shares one credential with every visitor and puts it in client-side code. B is not a DynamoDB capability: table data is not publicly readable, and IP conditions do not separate anonymous readers from signed-in writers. C confuses the two components: a user pool access token authorizes calls to your API, not to the DynamoDB API, which requires AWS credentials.

*Where this is covered: Identity pools: authenticated and guest roles, and how the role is chosen.*

</details>

### 8. Two roles for one signed-in user (Professional)

A software company runs a multi-tenant application on a single Cognito user pool. Users belong to a `tenant-admin` group and an `analyst` group, each mapped to a different IAM role. Administrators must always receive the `tenant-admin` role when the application requests AWS credentials, and the request must be denied outright if no role can be determined rather than falling back to a broad default.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Assign the `tenant-admin` group a lower precedence value than the `analyst` group so that its role becomes the `cognito:preferred_role` claim.
- **B)** Give both groups the same precedence value so the identity pool can choose between them.
- **C)** Set the identity pool's authenticated role selection to choose the role from the token, and set role resolution to deny the request.
- **D)** Set the identity pool's authenticated role selection to use the default authenticated role, and attach both permission sets to it.
- **E)** Pass the `analyst` role ARN in the `CustomRoleArn` parameter on every `GetCredentialsForIdentity` call.

<details><summary>Answer</summary>

**Answer: A and C.** Precedence is a non-negative number where lower wins, so giving `tenant-admin` the better precedence puts its role in `cognito:preferred_role`, and the identity pool only reads that claim when role selection is set to choose the role from the token; setting role resolution to deny removes the broad fallback the requirement forbids. B produces the opposite outcome: equal precedence with different role ARNs leaves `cognito:preferred_role` unset. D collapses two privilege levels into one role, which breaks the separation the scenario describes. E forces every session into the analyst role, which is wrong for administrators.

*Where this is covered: Identity pools: authenticated and guest roles, and how the role is chosen.*

</details>

## Summary

Amazon Cognito is two services and one recurring decision. Decide first which component the scenario needs: a user pool when the requirement is to sign users up and in and hand the application JSON Web Tokens, an identity pool when the requirement is temporary AWS credentials so a client can call an AWS service directly, and both together when a signed-in user must reach S3 or DynamoDB. Decide the front end next: managed login with a domain, a custom domain and the branding editor on Essentials or Plus, the classic hosted UI only on Lite. Add federation through SAML 2.0, OIDC or a social provider so the application still sees one token format. Shape the tokens with lifetimes, scopes from resource servers, groups with precedence, and a pre token generation trigger, and shape the flow with the other Lambda triggers, remembering the five-second budget. Choose the feature plan from the security requirement, since threat protection lives only in Plus. Then check the population: workforce access to AWS accounts is IAM Identity Center, not Cognito.

## Related units

- [AWS Identity and Access Management](iam.md): roles, trust policies and the AWS STS calls that identity pool credentials come from
- [AWS Organizations, IAM Identity Center and AWS Control Tower](organizations-identity-center-and-control-tower.md): workforce identity, and why it is the answer when the users are employees
- [Amazon API Gateway](../04-networking/api-gateway.md): user pool authorizers, JWT authorizers and the rest of the authorization choices for an API
- [Elastic Load Balancing](../02-compute/elastic-load-balancing.md): the `authenticate-cognito` listener rule and the headers an ALB passes to targets
- [AWS WAF, AWS Shield, AWS Firewall Manager and AWS Network Firewall](waf-shield-firewall-manager-and-network-firewall.md): web ACLs and rate-based rules in front of sign-in endpoints
- [AWS KMS and AWS CloudHSM](kms-and-cloudhsm.md): the multi-Region customer managed key that user pool replication requires
- [AWS Directory Service](directory-service.md): Active Directory as the source behind a SAML provider
- [AWS Lambda](../02-compute/lambda.md): the execution model and timeouts behind every Cognito trigger

## Sources

- [What is Amazon Cognito?](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html): the user pool and identity pool feature comparison table and the combined flow
- [Common Amazon Cognito scenarios](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-scenarios.html): the six documented patterns, including user pool with identity pool and API Gateway
- [User pool feature plans](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-sign-in-feature-plans.html): Lite, Essentials and Plus, the default plan, and the features-by-plan table
- [User pool managed login](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-managed-login.html): managed login compared with the classic hosted UI, branding, the one-hour session cookie and scope of operations
- [User pool sign-in with third party identity providers](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-identity-federation.html): the service provider and identity provider roles, per-provider groups, and the federated sign-in constraints
- [Using SAML identity providers with a user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-saml-idp.html): the SP entity ID and assertion consumer service URL
- [Understanding user pool JSON web tokens (JWTs)](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html): the three token types and what each carries
- [Understanding the identity (ID) token](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-id-token.html): the ID token payload and the 5 minute to 1 day range
- [Understanding the access token](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html): scope claims and separate signing keys
- [Refresh tokens](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-refresh-token.html): the 30 day default, the 60 minute to 10 year range, and refresh token rotation
- [CreateUserPoolClient](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_CreateUserPoolClient.html): the one-hour default for ID and access tokens and the 30 day refresh default
- [Adding groups to a user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-user-groups.html): group IAM roles, precedence, the preferred role claim and group limitations
- [Customizing user pool workflows with Lambda triggers](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-working-with-lambda-triggers.html): the trigger list, the five-second synchronous budget and cross-account triggers
- [Adding MFA to a user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-mfa.html): SMS, email and TOTP factors, optional compared with required, and passkey interaction
- [Advanced security with threat protection](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pool-settings-threat-protection.html): the rename from advanced security features, the Plus requirement and log export
- [Importing users into a user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-import-users.html): CSV import compared with just-in-time migration and passwords
- [Multi-Region replication for user pools](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-multi-region.html): the shared user pool ID, prerequisites and failover limitations
- [Associate an AWS WAF web ACL with a user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-waf.html): what AWS WAF inspects and the account takeover prevention exclusion
- [Amazon Cognito identity pools](https://docs.aws.amazon.com/cognito/latest/developerguide/identity-pools.html): authenticated and unauthenticated identities and guest access
- [Identity pools authentication flow](https://docs.aws.amazon.com/cognito/latest/developerguide/authentication-flow.html): the enhanced and basic flows and the artifacts each provider supplies
- [IAM roles](https://docs.aws.amazon.com/cognito/latest/developerguide/iam-roles.html): the required aud condition and the amr condition for authenticated compared with guest
- [Using role-based access control](https://docs.aws.amazon.com/cognito/latest/developerguide/role-based-access-control.html): the role resolution order, rule-based mapping and the 25 rule limit
- [Accessing resources with API Gateway after sign-in](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-accessing-resources-api-gateway-and-lambda.html): which token to send to which authorizer
- [Authenticate users using an Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html): the authenticate-cognito action, session timeout and the x-amzn-oidc headers
- [Quotas in Amazon Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/quotas.html): monthly active user definition, per-category request rates and resource quotas
- [Amazon Cognito pricing](https://aws.amazon.com/cognito/pricing/): the MAU model, the three tiers, the free tiers and the separate federated rate
- [Multi-tenancy best practices](https://docs.aws.amazon.com/cognito/latest/developerguide/multi-tenant-application-best-practices.html): the five tenant isolation patterns
- [What is IAM Identity Center?](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html): the workforce scope that sets the boundary against Cognito
