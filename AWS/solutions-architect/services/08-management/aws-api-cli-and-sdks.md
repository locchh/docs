# Working with AWS: the API, the CLI and the SDKs

**Where it sits on the exams.** Every action anyone takes in AWS is an HTTPS request to a service endpoint, signed with credentials, and the **AWS Management Console**, the **AWS Command Line Interface (AWS CLI)** and the AWS SDKs are three front ends over that single API. Be honest about scope before spending time here: the AWS CLI and the Management Console are both named in the management and governance in-scope list of the SAA-C03 and the SAP-C02 guides, while the SDKs and **AWS CloudShell**, the browser-based pre-authenticated shell, sit on the SAA-C03 out-of-scope list and are in scope for SAP-C02, whose only excluded service is **Amazon GameLift**, the managed game server hosting service. This unit owns the SAA-C03 task 2.2 knowledge item "service quotas and throttling, for example how to configure the service quotas for a workload in a standby environment". It also reinforces the "AWS service endpoints" knowledge item in SAA-C03 task 1.2 and SAP-C02 task 2.3, the SAP-C02 task 1.1 skill of using service endpoints for service integrations, and service quotas and limits in SAP-C02 tasks 2.4 and 3.4. For an Associate candidate the value is not memorizing commands. It is knowing how credentials reach a tool, what happens when a service throttles a caller, and which endpoint a request goes to. The rule of thumb the exam rewards is that quotas are per account and per Region, so a Region you have barely used has never had its quotas raised, and a failover into it fails at AWS defaults.

## The API underneath every tool

There is only one AWS API, and it speaks HTTPS. A request names an action, carries parameters, targets a service endpoint, and includes authentication information in its headers. A raw call to **Amazon CloudWatch**, the monitoring and metrics service, looks like this, with the credential and signature truncated:

```http
POST / HTTP/1.1
Host: monitoring.us-east-1.amazonaws.com
X-Amz-Target: GraniteServiceVersion20100801.GetMetricData
X-Amz-Date: 20260912T092034Z
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20260912/us-east-1/monitoring/aws4_request, SignedHeaders=host;x-amz-date;x-amz-target, Signature=...
Content-Type: application/x-amz-json-1.0
```

Almost nobody writes that by hand, and AWS says so plainly: "Unless you have a good reason not to, we recommend that you always use an SDK or the CLI." The documented reasons to hand-sign are that you are working in a language with no AWS SDK, or you need complete control over how requests are sent. Everything else goes through one of four front ends. The Management Console is the browser interface, and AWS commits that "All IaaS (infrastructure as a service) AWS administration, management, and access functions in the AWS Management Console are available in the AWS API and AWS CLI", with new IaaS features reaching full console parity in the API and CLI "at launch or within 180 days of launch". The AWS CLI runs the same API calls from a shell. The SDKs wrap the API in a language, adding request signing, error handling and automatic retries. Direct HTTPS is the fallback.

Two response details earn their keep on the job and occasionally in a question stem. Every response carries a request ID. The general case is a single identifier in the response metadata, present whether the call succeeded or failed, and it is the value to quote when you open a support case. It is also the join key between a failure you saw and the record of it: CloudTrail stores the same identifier on the matching event, so an error message and an audit log entry can be lined up exactly. For most services it is a single value; **Amazon S3**, the object storage service, is the exception that returns a pair, `x-amz-request-id` and `x-amz-id-2`. AWS documents that these "are returned in every response that Amazon S3 processes (even the erroneous ones)" and tells you to keep both when contacting **AWS Support**, the AWS technical support organization. The AWS CLI exposes them with `--debug`. The other detail is eventual consistency: some APIs, notably parts of **Amazon EC2**, the virtual server service, do not immediately reflect a change in a subsequent describe call, so scripts that create and then immediately read must tolerate a short lag rather than assume a failure.

The API is also the seam at which auditing and authorization happen. **AWS CloudTrail**, the API activity logging service, records the call, the caller identity, the source IP and the request ID. **AWS Identity and Access Management (IAM)**, the access control service, evaluates the same call against identity, resource and organization policies. Whether the call came from a console click, a `bash` loop or a Java program changes nothing about either, and that equivalence is the reason exam answers rarely turn on which tool was used.

## Service endpoints: Regional, global, dual-stack and FIPS

An endpoint is the URL of the entry point for a service, and the SDKs and CLI pick the right one automatically from the Region you configured. Most services offer a Regional endpoint that carries IPv4 traffic and uses the syntax `protocol://service-code.region-code.amazonaws.com`, so **Amazon DynamoDB**, the managed NoSQL key-value database, in US West (Oregon) is reached at `https://dynamodb.us-west-2.amazonaws.com`. Regional isolation is the point: resources in one Region are independent of similar resources elsewhere, and a call to the wrong Regional endpoint simply does not see them. A small set of services instead has a global endpoint that spans Regions, including IAM, **AWS Organizations**, the multi-account management service, **Amazon Route 53**, the managed DNS service, **Amazon CloudFront**, the content delivery network, **AWS Global Accelerator**, the anycast entry point into the AWS network, **AWS Shield Advanced**, the paid tier of the DDoS protection service, and **AWS Cloud WAN**, the managed global network service. Separately, Amazon EC2, **Amazon EC2 Auto Scaling**, the service that keeps a group of instances at the right size, and **Amazon EMR**, the managed big data framework service, accept a general endpoint with no Region in it, such as `ec2.amazonaws.com`, which AWS routes to `us-east-1`.

Two endpoint variants exist beside the standard one, and the exam likes them because each maps to a compliance or network requirement rather than a preference. Read this table for which requirement selects which variant.

| Variant | Host pattern | What it gives you | How to select it |
|---|---|---|---|
| Standard Regional | `service-code.region-code.amazonaws.com` | IPv4, the default for every tool | Nothing to do |
| Dual-stack | `service-code.region-code.api.aws`, and `service-code.dualstack.region-code.amazonaws.com` for Amazon S3 | Accepts both IPv4 and IPv6 requests | `use_dualstack_endpoint = true` in `~/.aws/config`, `AWS_USE_DUALSTACK_ENDPOINT=true`, or `--endpoint-url` |
| FIPS | Service-specific, for example `kms-fips.us-west-2.amazonaws.com` for **AWS Key Management Service (AWS KMS)**, the managed encryption key service | A TLS software library validated against FIPS 140 | `use_fips_endpoint = true`, `AWS_USE_FIPS_ENDPOINT=true`, or `--endpoint-url` |

Both settings default to `false`, and both fail loudly rather than silently falling back: if the requested variant does not exist for that service in that Region, "the AWS call may fail". FIPS endpoints require a minimum of TLS 1.2 and AWS recommends TLS 1.3. The Federal Information Processing Standards are US government security requirements, so a stem that mentions a federal agency, a FedRAMP obligation or a contract with the US government is pointing at FIPS endpoints, not at encryption at rest. A stem that says an IPv6-only client subnet must reach a service is pointing at dual-stack.

Two more endpoint ideas belong here because stems blur them. A service endpoint is a public DNS name; reaching it privately from a virtual private cloud in **Amazon VPC**, the isolated virtual network service, is the job of a VPC endpoint, either a gateway endpoint or an interface endpoint powered by **AWS PrivateLink**, the service that exposes a service through an elastic network interface inside your subnets. That is a network path decision, taught in [Amazon VPC](../04-networking/vpc.md), and it does not change the endpoint the SDK signs for. Separately, the CLI and SDKs let you override endpoints per service through `--endpoint-url`, the `endpoint_url` setting in a `services` section of the config file, or `AWS_ENDPOINT_URL_<SERVICE>` environment variables, which is how people point a client at a local test double. On the exam, `--endpoint-url` is almost always the wrong answer for a production design and the right answer only when the question explicitly asks how to reach a FIPS or dual-stack host.

## Signing a request: SigV4, and what SigV4a adds

AWS Signature Version 4 (SigV4) is the signing protocol that adds authentication information to an API request. You never send the secret access key. Instead the caller builds a canonical form of the request, derives a signing key from the secret access key scoped to one date, one Region and one service, calculates an HMAC-SHA256 signature over the canonical request, and puts the result in an `Authorization` header, or in query string parameters for a presigned URL. AWS repeats the calculation on arrival and compares. The scheme delivers three things at once: it verifies who the requester is, because only the holder of the secret can produce the signature; it protects the payload in transit, because a hash of request elements is part of what gets signed, so a tampered request fails verification; and it protects against replay, because the signature covers a timestamp and "In most cases, a request must reach AWS within five minutes of the time stamp in the request", after which AWS denies it. That five-minute window is why a machine with a badly skewed clock cannot call AWS at all, and it is the real explanation behind the CLI documentation's warning that "you must ensure that your computer's date and time are set correctly". Temporary credentials add one element: the session token must be sent with every signed request alongside the access key ID.

The credential scope makes SigV4 Region-bound by construction. The `Credential` element concatenates the access key ID with the date in `YYYYMMDD` form, the Region code, the service code and the `aws4_request` termination string, so a signature computed for `us-east-1` is worthless against `eu-west-1`. That is fine until a request is meant to reach whichever Region is healthy, at which point the signer would have to know the destination in advance.

Asymmetric Signature Version 4, SigV4a, is the extension that removes that constraint, and it is worth one paragraph because the multi-Region S3 feature depends on it. SigV4a derives an Elliptic Curve Digital Signature Algorithm (ECDSA) keypair from the existing secret access key and signs with the private half, so AWS only needs to store public keys, which cannot be used to sign anything. It uses the algorithm identifier `AWS4-ECDSA-P256-SHA256` rather than `AWS4-HMAC-SHA256`, drops the Region from the credential scope, and instead carries an `X-Amz-Region-Set` header listing the Regions the signature is valid in, with wildcards allowed, for example `X-Amz-Region-Set=us-west-*`. One signature is therefore verifiable in more than one Region, which is what makes "seamless routing and failover between regions" possible. The practical exam fact is that you do not configure this: "When you supply requests to Multi-Region Access Points, SDKs and the CLI automatically switch to using Signature Version 4A without additional configuration." If a stem describes a custom-signed request failing against an S3 Multi-Region Access Point, the missing piece is SigV4a.

## Where credentials come from: the provider chain

Every SDK and the CLI look for credentials in a series of places, in a fixed order, and stop at the first source that yields a usable set. AWS calls this the credential provider chain. The exact chain "used by each SDK varies", which is why the exam tests the idea rather than a numbered list, but the standardized providers are the same everywhere: static AWS access keys, a provider for **AWS IAM Identity Center**, the workforce single sign-on service, a login provider for console credentials, an assume-role provider, a web identity provider, a container provider for tasks in **Amazon Elastic Container Service (Amazon ECS)**, the AWS-native container orchestrator, and **Amazon Elastic Kubernetes Service (Amazon EKS)**, the managed Kubernetes service, a process provider that shells out to an external program, and the instance metadata provider for EC2 instance profiles. The chain also refreshes on its own. AWS states that "the AWS SDKs always attempt to renew credentials automatically when they expire", with no code required, which is the reason a long-running process on an instance profile never needs credential rotation logic.

The AWS CLI publishes its own order explicitly, and it is worth knowing because it explains almost every "why is it using the wrong account" incident. From highest precedence to lowest, the CLI checks command line options such as `--region`, `--output` and `--profile`; environment variables; an assume-role configuration; assume role with web identity; IAM Identity Center settings in the `config` file; the `credentials` file; a custom credential process; the `config` file; container credentials; and finally Amazon EC2 instance profile credentials. Two consequences follow. First, an `AWS_ACCESS_KEY_ID` left in a shell from an hour ago beats everything in `~/.aws`, and it beats the instance profile of the machine you are on, which is how a script silently runs as the wrong principal. Second, the instance profile is last, so it is used only when nothing else answered, which is exactly the behavior you want on an EC2 instance that also has a developer's leftover files in a home directory.

The credentials themselves come in two kinds and the exam is unambiguous about the preference. Long-term access keys are a key ID and a secret belonging to an IAM user, they carry that user's full permissions, a user may hold at most two so that rotation is possible, and they never expire on their own. Temporary credentials from **AWS Security Token Service (AWS STS)**, the service that issues short-lived credentials, are an access key ID, a secret, a session token and an expiration, they are what a role assumption returns, and they cannot leak usefully for long because they expire. Role assumption, session duration, role chaining's one-hour ceiling and the STS Regional compared with global endpoint question are all taught in [AWS Identity and Access Management](../07-security/iam.md); what matters here is how those credentials reach a tool. The tooling answer is that you never paste them. You configure a source and let the chain refresh them.

One more environment-variable detail decides questions about portability. `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_SESSION_TOKEN` are read by every SDK and by the CLI. For the Region, the standardized cross-SDK setting is `AWS_REGION`, while `AWS_DEFAULT_REGION` is the older CLI-oriented name that the CLI still honors, so a script that sets only `AWS_DEFAULT_REGION` and then calls an SDK in another language may find no Region configured at all.

## Named profiles, signing in, and temporary credentials in tooling

The shared `config` and `credentials` files hold named profiles. Both are plaintext INI-format files, not TOML as some older notes have it, and AWS recommends keeping only the three secret settings, `aws_access_key_id`, `aws_secret_access_key` and `aws_session_token`, in `credentials`, so the two files can carry different filesystem permissions. Profile sections are written `[profile name]` in `config` and `[name]` in `credentials`, with `[default]` used when no profile is named. `aws configure` writes both files interactively, and `aws configure --profile finance` writes a named one.

```ini
[default]
region = us-west-2
output = json

[profile crossaccountaudit]
role_arn = arn:aws:iam::234567890123:role/AuditReader
source_profile = default
mfa_serial = arn:aws:iam::123456789012:mfa/saanvi
external_id = 123456
```

That second profile is the important shape. Rather than storing a second set of keys, it names a role and a `source_profile` whose credentials are used to call `sts:AssumeRole`, optionally requiring an MFA device and an external ID. On an EC2 instance or an ECS task, `credential_source = Ec2InstanceMetadata` or `credential_source = EcsContainer` replaces `source_profile`, so the instance profile's credentials are used to assume the target role. Setting `role_session_name` makes the resulting CloudTrail events attributable to a person rather than to an anonymous shared role session.

For human access the current answer is federation, not keys. With IAM Identity Center, `aws configure sso` writes an `sso-session` block and one or more profiles that reference it, and `aws sso login` opens a browser, authenticates the person, and caches an SSO token under `~/.aws/sso/cache`. The CLI then exchanges that token for role credentials and refreshes them automatically as long as the session is valid; when the session expires, you sign in again rather than rotating anything. One `sso-session` can back many profiles, one per account and permission set, which is what makes a 200-account organization workable from one terminal. `aws sso logout` deletes the cached credentials.

```ini
[profile prod-readonly]
sso_session = corp
sso_account_id = 111122223333
sso_role_name = ReadOnly
region = eu-west-1

[sso-session corp]
sso_region = us-east-1
sso_start_url = https://my-sso-portal.awsapps.com/start
sso_registration_scopes = sso:account:access
```

Two further sign-in paths exist and are easy to confuse with that one. `aws login`, available from AWS CLI version 2.32.0, reuses an existing Management Console sign-in: it runs a browser-based flow, then issues temporary credentials that the CLI refreshes "for up to 12 hours", capped by the session duration of the IAM principal. It is aimed at local development for accounts that do not use IAM Identity Center, and it is also the documented path for root user programmatic access, and `aws logout` clears the cache. Separately, `credential_process` points a profile at an external program that prints credentials in a documented JSON shape on standard output, which is how a tool that does not understand IAM Identity Center can still consume a refreshed session. AWS documents exactly that bridge: `credential_process = aws configure export-credentials --profile signin --format process`. One boundary is worth stating because a distractor depends on it: **AWS Secrets Manager**, the managed secret store, is the right home for an application's database passwords and third-party API keys, but it is the wrong home for the AWS credentials the caller needs to reach AWS in the first place, because retrieving them would itself require credentials. Finally, `aws sts get-caller-identity` needs no permission at all and answers the only question that matters when something behaves strangely, which is which identity the tool is actually using.

## Instance metadata as a credential source, and why IMDSv2 matters

On an EC2 instance with an IAM role attached through an instance profile, the CLI and SDKs "automatically and securely" retrieve temporary credentials from the instance metadata service (IMDS) at the link-local address `169.254.169.254`, or `[fd00:ec2::254]` for the IPv6 endpoint where it has been enabled. Those credentials are refreshed for you and never touch the filesystem, which is why the answer to "an application on EC2 needs to call Amazon S3" is always an instance profile and never an access key in a configuration file. The same idea appears as the container provider for Amazon ECS tasks and Amazon EKS pods, and as **IAM Roles Anywhere**, which delivers role credentials to workloads outside AWS through the process provider.

IMDS has two versions and the difference is a security control, not a feature. IMDSv1 is a plain request: anything that can make an HTTP GET to `169.254.169.254` from inside the instance gets the role's credentials back. IMDSv2 is session oriented. The caller first sends a `PUT` to `/latest/api/token` to obtain a session token valid from one second to six hours, then presents that token on subsequent `GET` requests. Three properties of that `PUT` are what make it a defense. It is a `PUT`, which a server-side request forgery through a vulnerable web application or a misconfigured reverse proxy usually cannot induce, because those flaws typically coerce a `GET`. Its response carries a hop limit, defaulting to 1 at the IP layer, so the reply cannot travel out of the instance to a container network or another host unless you deliberately raise it. And a `PUT` "is rejected if it contains an `X-Forwarded-For` header", which is the header a proxy adds when relaying someone else's request.

Defaults now lean toward IMDSv2 but do not universally require it, which is the nuance an exam question can turn on. An instance's metadata version is resolved from three levels, highest first: the value set at launch, the account-level default for that Region, then the AMI's `ImdsSupport` attribute. An AMI registered with `ImdsSupport = v2.0`, which includes Amazon Linux 2023, launches instances requiring IMDSv2 and sets the hop limit to 2 unless something with higher precedence overrides it; Amazon Linux 2023 also disables IMDSv1 by default. Where nothing is set anywhere, the resulting configuration is still "IMDSv1 or IMDSv2 (token optional)". Making IMDSv2 mandatory is therefore an explicit act with four documented levers: `modify-instance-metadata-defaults` to set the Region's account default, account-level IMDSv2 enforcement, which makes any launch with `httpTokens` set to `optional` fail outright, the IAM and service control policy condition keys `ec2:MetadataHttpTokens`, `ec2:MetadataHttpPutResponseHopLimit` and `ec2:MetadataHttpEndpoint`, and a declarative policy in AWS Organizations to set the default organization wide. A fifth control closes the loop at the other end: the condition key `ec2:RoleDelivery` with a value of `2.0` makes API calls carrying credentials that were obtained through IMDSv1 fail with `UnauthorizedOperation`, so even a leaked IMDSv1 credential cannot be used.

Migration has a documented safe path, and a question about how to find out what would break names the same tools. The CloudWatch metric `MetadataNoToken` counts IMDSv1 calls per instance, so you drive it to zero before switching; after switching, `MetadataNoTokenRejected` counts attempts that were refused, so you can find the agent nobody upgraded. Requiring IMDSv2 on a running instance "takes effect immediately without needing an instance restart", but for an Auto Scaling group, the launch template must be updated and existing instances replaced or modified individually.

## The AWS CLI in practice

Version 2 is the current AWS CLI and the only one to install today. Version 1 "is now in maintenance mode", entering that phase on 15 July 2026 and reaching end of support on 15 July 2027, after which it receives nothing. The two differ in ways that matter beyond the version number. Version 1 "is built using the SDK for Python, and therefore requires you to install a compatible version of Python"; version 2 ships as a bundled installer with its own interpreter, so the old claim that Python is a prerequisite for the AWS CLI is true only of version 1. AWS supports only its own distribution points, noting that packages found in operating system package managers "are unsupported and unofficial packages that are not produced or managed by AWS". Version 2 also changed defaults that an exam scenario could rest on, including a client-side pager and a different retry mode. `aws --version` reports which one is installed.

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update
aws --version
aws sts get-caller-identity
```

Commands follow the shape `aws <service> <operation> [parameters]`, and most operations map one to one onto an API action. Amazon S3 is the standout exception, and its three command groups are a favorite distractor set. `aws s3` is a set of "custom high-level commands made specifically for the AWS CLI that simplify performing common tasks", including `cp`, `mv`, `sync`, `rm`, `ls`, `mb` and `rb`; `sync` in particular performs a recursive multi-object copy with multipart uploads and parallelism that no single API call provides. `aws s3api` "exposes direct access to all Amazon S3 API operations", so anything not covered by the high-level verbs, such as `put-bucket-versioning` or `head-object`, lives there. `aws s3control` is a different API entirely, the S3 control plane: access points, Multi-Region Access Points, S3 Batch Operations jobs, S3 Storage Lens configurations, Access Grants and S3 on Outposts buckets. A fourth, `aws s3outposts`, manages endpoints for S3 on Outposts. The selection rule is simple: an everyday file operation is `s3`, a specific bucket or object API is `s3api`, and anything account-wide or account-level is `s3control`.

Output shaping is where the CLI stops being a wrapper and starts being a tool. `--output` accepts `json`, which is the default, `yaml`, `yaml-stream`, `text`, `table` and `off`, set per command, per profile with the `output` setting, or for a session with `AWS_DEFAULT_OUTPUT`. `--query` applies a JMESPath expression to the response after it arrives, which is client-side filtering: the whole response crosses the network first, so it is slower than a service's own `--filters` or `--filter` parameter on a large data set, and combining the two is the efficient pattern. One subtlety appears in stems about odd results: with `--output text` the output is paginated before the query runs, so the query executes once per page and can emit unexpected extra rows, while `json`, `yaml` and `yaml-stream` process the whole structure once. AWS goes further and recommends that "if you specify `text` output, you also always use the `--query` option", because text columns are ordered alphabetically by key name and that ordering changes when a service adds a field.

```bash
aws ec2 describe-instances \
  --filters Name=instance-state-name,Values=running \
  --query 'Reservations[].Instances[].{ID:InstanceId,AZ:Placement.AvailabilityZone,Type:InstanceType}' \
  --output table
```

Pagination is handled for you and the three flags that change it are frequently confused. By default the CLI follows pagination tokens and makes as many calls as it takes: on a bucket with 3,500 objects and a service page size of 1,000, `aws s3api list-objects` quietly makes four calls and returns all 3,500 objects. `--page-size` changes only how many items each underlying call requests; you still get the full list, in more calls, which is the fix when a large page times out. `--max-items` limits how many items are printed and returns a `NextToken` you can feed to `--starting-token` to continue. `--no-paginate` stops the CLI following tokens at all, so you get only the first page. Mixing different `--page-size` and `--max-items` values can produce missing or duplicated items, so AWS advises setting them equal. Finally, many mutating EC2 operations accept `--dry-run`, which "checks whether you have the required permissions for the operation, without actually making the request": success is reported as the error `DryRunOperation` and failure as `UnauthorizedOperation`. It tests permissions, not correctness, and it is not a general CLI flag.

## Retries, exponential backoff with jitter, and throttling

Calls across a network fail. Some failures are transient, a reset connection or an HTTP 503; some are the service telling you to slow down. The SDKs and the CLI retry both automatically, and the three retry modes differ in how much machinery they bring.

| Mode | What it does | Where it is the default |
|---|---|---|
| `legacy` | The original per-SDK handler. Fewer retryable error codes, no standardized retry quota, timing and counts vary by language | AWS CLI version 1 |
| `standard` | A common rule set across SDKs: a wider retryable error list, exponential backoff with jitter, a retry quota | AWS CLI version 2 and the current SDKs |
| `adaptive` | Everything in standard, plus a client-side rate limiter that can delay or block even the initial request when throttling is detected | Never the default |

Standard is the answer to "which mode should we use". In AWS CLI version 2 it allows "a default value of 2 for maximum retry attempts, making a total of 3 call attempts", retries a long list of throttling codes such as `Throttling`, `ThrottlingException`, `ProvisionedThroughputExceededException`, `RequestLimitExceeded` and `SlowDown`, retries transient codes and bare HTTP 500, 502, 503 and 504, and backs off exponentially by a base factor of 2 to a maximum of 20 seconds. Legacy allowed more attempts, four retries for most services and nine for Amazon DynamoDB, but on a narrower set of errors and without a quota. Adaptive is documented as "not recommended as a general default", and AWS CLI documentation still warns that it "is an experimental mode and is subject to change"; it fits a single-resource, throttling-heavy, latency-tolerant workload such as a bulk backfill against one DynamoDB table, and fits badly where latency matters or where many clients share the endpoint. Both mode and attempt count are set the same way everywhere: `retry_mode` and `max_attempts` in `~/.aws/config`, or `AWS_RETRY_MODE` and `AWS_MAX_ATTEMPTS`.

The backoff is exponential with full jitter, not a fixed doubling. AWS documented a revised SDK retry behavior in 2026 that is opt-in during rollout, behind `AWS_NEW_RETRIES_2026=true`; without it an SDK uses the earlier behavior, which differs in backoff timing, retry quota costs and service defaults. Under the opt-in behavior the formula is `delay = random(0, 1) x min(20,000 ms, base_delay x 2^retry)`, with a base delay of 50 ms for transient errors and 1,000 ms for throttling errors, because a throttled service needs longer to recover capacity than a reset connection does. The randomization is the part older notes omit, and it is the part that matters: without it, a thousand clients that all received a 503 at the same instant would all retry at the same instant. AWS calls that the thundering herd problem, and full jitter "spreads retries uniformly across the entire backoff window so the service receives a steady trickle of requests instead of synchronized spikes". A second protection sits alongside it. Standard and adaptive modes keep a retry quota, a token bucket of 500 tokens that a transient retry draws 14 from and a throttling retry 5, refunded when a retry succeeds, with 1 token restored for a first-try success. When the budget empties the SDK stops retrying and returns the error immediately, so the client fails fast instead of prolonging an outage. During normal operation the bucket stays full and nothing changes. Note that the newest form of this behavior is opt-in while it rolls out: AWS documents that you set `AWS_NEW_RETRIES_2026=true` to get it, and that without the setting the SDK uses the earlier behavior, which "differs in backoff timing, retry quota costs, and service-specific defaults".

Throttling itself is a server-side control, and Amazon EC2 is the clearest documented example. EC2 "uses the token bucket algorithm to implement API throttling": each API is evaluated individually, per account and per Region, with a bucket capacity that allows a burst and a refill rate that sets the sustained rate. Exceeding it returns `RequestLimitExceeded` for that API while requests to other APIs are unaffected. Some actions, `RunInstances`, `StartInstances`, `StopInstances` and `TerminateInstances`, additionally consume from a separate resource token bucket that depletes with the number of resources affected, so launching 500 instances in one call is throttled differently from calling `RunInstances` 500 times. The console is bucketed separately from other non-mutating API calls, so a saturated automation loop does not by itself lock an engineer out of the console. What does hurt is several callers hammering the same API in the same account and Region, because they do share that API's bucket, and the usual root cause is a polling loop somewhere nobody remembers writing. The architectural fixes are to poll less, to cache, to move from polling to events with **Amazon EventBridge**, the event bus service, and to spread work rather than to raise `max_attempts`.

## Service quotas, and the standby Region that has none

Quotas, which older AWS documentation calls limits, are "the maximum values for the resources, actions, and items in your AWS account". **Service Quotas** is the service that shows them and requests increases from one console, CLI or API, and it is worth saying plainly that Service Quotas appears as a named service only on the SAP-C02 in-scope list, while the concept of quotas and throttling is explicitly examinable at Associate level in SAA-C03 task 2.2. Every quota has a default value set by AWS and may have an applied quota, which is the raised value after an increase. Some are adjustable and some are hard, and the console's Adjustable column is the authority. Most quotas are per account and per Region; a few are global quotas applied at the account level, and for those an increase can be requested only from US East (N. Virginia) in the standard partition. Requests go to AWS Support, which "might approve, deny, or partially approve" them, and they take time.

That last sentence is the whole of the standby-environment question in SAA-C03 task 2.2. Consider a pilot light or warm standby disaster recovery site in a second Region. It runs a handful of instances, a small database and almost nothing else, so its quotas have never been raised: the EC2 running On-Demand instance vCPU quota, the Elastic IP address quota, the VPC and NAT gateway quotas, the concurrent execution quota for **AWS Lambda**, the serverless function service, and the instance quota for **Amazon RDS**, the managed relational database service all sit at AWS defaults. The day of the failover, that Region is asked to absorb full production, and the Auto Scaling group stops mid-scale with an error nobody has seen before. The keyed answer is always the same shape: request the quota increases in the DR Region in advance, as part of building the standby environment, and verify them, rather than discovering the gap during an event. Testing the DR plan at production scale is how you find which quota you forgot. Raising the quota in the primary Region does nothing for the secondary, because quotas do not replicate.

Two features turn that from a checklist into a control. Amazon CloudWatch alarms can be created directly from a Service Quotas quota page for quotas that support them, watching utilization, which is "the percentage of a service quota in use", so an alarm at 80 percent gives you time to request an increase before a deployment fails. And a quota request template, configured in the Organization section of the Service Quotas console, holds up to ten quota increases and automatically requests them for every new account created in the organization. It requires AWS Organizations with all features enabled, it is not available with consolidated billing only, it is supported in commercial Regions but not in China Regions or opt-in Regions, and it applies to new accounts only: "Updating a request template doesn't update quota values for existing accounts." One thing to rule out: **AWS Budgets**, the cost threshold and alerting service, watches spend rather than capacity and cannot raise or read a service quota. **AWS Trusted Advisor**, the account inspection service, has service limit checks that show usage against quota as a complementary detective view, and it is taught in [AWS Config, Trusted Advisor, Health and Well-Architected](config-trusted-advisor-health-and-well-architected.md).

## SDKs, Smithy and AWS CloudShell

An AWS SDK is a library that wraps the API in a language: **AWS SDK for Python (Boto3)**, the SDKs for Java, JavaScript, .NET, Go, Ruby, PHP, C++, Kotlin, Rust and Swift, plus AWS Tools for PowerShell. What they add beyond convenience is exactly the behavior described above, and AWS summarizes it as "cryptographically signing requests, managing errors, and retrying requests automatically", along with pagination helpers, waiters that poll until a resource reaches a state, and credential chain resolution with automatic refresh. Remember the scope note: the SAA-C03 guide lists "Tools and SDKs" as out of scope, so an Associate question will not require SDK knowledge, while for SAP-C02 they are fair game. Major versions do reach end of support on a published schedule, which the AWS SDKs and Tools version lifecycle page tracks; as of September 2026 the SDK for Java 1.x, the SDK for JavaScript 2.x and the SDK for Go 1.x are all past end of support, and AWS SDK for .NET 3.x and AWS Tools for PowerShell 4.x reached end of support on 1 June 2026.

Those SDKs are not written by hand, and one paragraph explains why they are so consistent. **Smithy** is AWS's open-source interface definition language for services: a protocol-agnostic model that describes operations, inputs, outputs, errors and traits, from which AWS generates SDK clients and CLI commands in every supported language. AWS has been "generating SDK clients and CLI tools using Smithy models" since 2018, and Smithy IDL 2.0 became generally available in August 2022. The practical consequence, and the only thing worth carrying into an exam, is that a new AWS service or parameter appears in every SDK and in the CLI at roughly the same time because they all come from one model, which is why CLI syntax and SDK method names track the API reference so closely.

AWS CloudShell is a browser-based, pre-authenticated shell launched from the Management Console, with the AWS CLI and common tools already installed and the console user's credentials already in place, so there is nothing to install and no key to store. You choose Bash, PowerShell or Z shell. It provides 1 GB of persistent storage per Region at no additional cost in the home directory, which survives between sessions, and CloudShell itself is free, with normal charges for whatever you create and standard data transfer rates. Up to 10 concurrent shells per Region are allowed, each Region has a monthly usage quota, and a command cannot exceed 65,412 characters; all of those are raisable through Service Quotas. A CloudShell VPC environment, which runs inside your VPC to reach private resources, is the exception with no persistent storage: its home directory is deleted when the environment times out, which happens after 20 to 30 minutes of inactivity, or 10 minutes in AWS GovCloud (US) Regions. Scope again: CloudShell is on the SAA-C03 out-of-scope list and in scope for SAP-C02, where the right read on a stem is that CloudShell is the lowest-overhead way for an operator to run a few commands with the identity they already signed in as, and never the answer for automation, which belongs in a pipeline or a Lambda function.

## Professional depth

At organization scale, the question stops being "how do I get credentials" and becomes "how does nobody hold a long-term key". The target state is IAM Identity Center as the only human entry point, with one `sso-session` in every engineer's `config` file and one profile per account and permission set, so that access is granted and revoked centrally and every terminal session is a short-lived role session. Machine access uses instance profiles, task roles, IAM Roles Anywhere for on-premises workloads, and OIDC federation for CI systems, all through the credential provider chain. The residual access keys are then a small, enumerable list, and an SCP denying `iam:CreateAccessKey` outside a break-glass path keeps it small. The detection half of that control is the IAM credential report and last-used data, covered in [AWS Identity and Access Management](../07-security/iam.md), and the account structure it depends on is covered in [AWS Organizations, IAM Identity Center and AWS Control Tower](../07-security/organizations-identity-center-and-control-tower.md).

Quotas are the most common cause of a Professional scenario failing in a way that looks like an outage. Three patterns recur. The first is the standby Region described above, where a disaster recovery plan has an untested dependency on quotas nobody raised. The second is the newly vended account: a workload migrated into a fresh account inherits default quotas even though the source account had years of increases, which is exactly what the Service Quotas request template exists to fix, and why the template must be configured before **AWS Control Tower**, the service that sets up and governs a multi-account environment, vends the account through Account Factory rather than after. The third is the shared quota nobody owns, where several teams in one account and Region draw on the same EC2 vCPU or Lambda concurrency quota and the third team to scale is the one that breaks. The remedy for that last one is account separation, so that the quota boundary matches the team boundary, which is one of the strongest reasons to split workloads across accounts at all.

Throttling at scale is an architecture problem before it is a retry-configuration problem. A fleet of a thousand instances that each describe their own tags every minute will throttle the EC2 API for the whole account, and turning up `max_attempts` makes it worse by adding load during recovery. The durable answers are to stop polling in favor of events delivered by EventBridge, to cache descriptions that change rarely, to batch where the API supports it, to spread scheduled work with jitter so cron jobs do not all fire on the minute, and to keep control-plane calls out of the request path of a data-plane application entirely. Where a single client legitimately saturates one resource, adaptive retry mode is the narrow fit, because its client-side rate limiter throttles the caller before the service has to.

Endpoints become a design constraint rather than a detail once compliance and network isolation enter. A regulated workload may be required to use FIPS endpoints for every service it calls, which means setting `use_fips_endpoint` centrally through an environment variable baked into the AMI or task definition rather than hoping each application sets it, and verifying that each service actually offers a FIPS endpoint in that Region, because the call fails if it does not. An IPv6-only subnet requires dual-stack endpoints for every service in the path. And reaching a public service endpoint without traversing the internet requires interface endpoints, with the `aws:SourceVpce` condition key in resource policies as the enforcement that calls arrive only that way.

> **Professional depth.** A Professional question often extends an Associate throttling scenario with a second constraint. The Associate version says an application receives throttling errors and asks what to do, and the key is exponential backoff with jitter, which the SDK already implements. The Professional version adds that the workload runs in 40 accounts, that it must not regress during the fix, and that a quota increase has already been requested. The key then combines three things: request the increase per account and per Region, because neither the quota nor the increase crosses either boundary; remove the call pattern generating the load, usually by replacing polling with events; and only then tune retry behavior, choosing adaptive mode where one client saturates one resource and leaving standard mode everywhere else so that a failing service is not hammered by 40 accounts at once.

## Worked scenario

A media company runs 40 accounts in one AWS Organizations organization with all features enabled. Production for its main application lives in eu-west-1, with a warm standby in eu-central-1 that runs two application instances and a read replica. Engineers currently share IAM user access keys stored in `~/.aws/credentials`. A batch job on 200 EC2 instances describes its own instance tags every 30 seconds and has begun returning `RequestLimitExceeded`. A new government contract requires that all API traffic from one account use FIPS validated endpoints, and an internal audit found that several instances still allow IMDSv1.

The identity work comes first. IAM Identity Center becomes the only human entry point: each engineer runs `aws configure sso` once against a single `sso-session`, gets one profile per account and permission set, and signs in with `aws sso login`. The shared access keys are deleted, and an SCP blocks `iam:CreateAccessKey` outside a break-glass role. Applications keep using instance profiles, so nothing in the credential provider chain changes for them. The IMDS finding is closed by setting the account-level default to require IMDSv2 in every Region through a declarative policy in AWS Organizations, watching `MetadataNoToken` fall to zero first, then enabling account-level enforcement and adding `ec2:RoleDelivery` with value `2.0` to an SCP so IMDSv1-derived credentials cannot call any API even if one slips through.

The throttling is fixed at the source rather than at the client. The tag-polling loop is replaced by reading tags from instance metadata locally, with EventBridge notifying the fleet when something changes, which removes 400 API calls a minute from the account's EC2 token bucket. Retry configuration is left at standard mode, since the problem was load rather than retry behavior, and a CloudWatch alarm is created from the Service Quotas console on the EC2 vCPU quota's utilization at 80 percent. For the FIPS requirement, the regulated account's AMIs and task definitions set `AWS_USE_FIPS_ENDPOINT=true`, and the team confirms each service it calls publishes a FIPS endpoint in that Region before deploying.

Finally the standby Region is made real. The team lists every quota the full production footprint consumes in eu-west-1, requests matching increases in eu-central-1 while there is no incident, and adds those quotas to a Service Quotas request template so that new accounts are vended with them. A game day scales eu-central-1 to full production size to prove the numbers. When the exam asks about this scenario, the keyed answers are IAM Identity Center with `aws sso login` for human credentials, instance profiles with IMDSv2 required for workloads, removing the polling loop rather than increasing `max_attempts` for the throttling, requesting quota increases in the DR Region in advance with a request template for new accounts, and `use_fips_endpoint` for the regulated account.

## Exam lens

- "An application on an EC2 instance needs to call an AWS service securely, with no credentials stored on disk" maps to an IAM role attached through an instance profile, delivered by the instance metadata service; storing an access key in a configuration file or an environment variable is the distractor.
- "Developers must stop using long-term access keys for command line access" maps to IAM Identity Center with `aws configure sso` and `aws sso login`; rotating the keys more often is the distractor that keeps the long-term credential.
- "A script picks up the wrong account even though the profile is correct" maps to the credential precedence order: command line options beat environment variables, which beat everything in `~/.aws`, which beats the instance profile.
- "Protect instance credentials from server-side request forgery" maps to requiring IMDSv2; a security group rule does not apply, because the metadata request never leaves the instance.
- "Confirm nothing still uses IMDSv1, then watch for breakage after enforcing it" maps to the CloudWatch metric `MetadataNoToken` while IMDSv1 is still allowed, then `MetadataNoTokenRejected` once it is disabled; an instance emits one or the other, never both.
- "All API traffic must use FIPS 140 validated cryptography" maps to FIPS endpoints, set with `use_fips_endpoint` or `AWS_USE_FIPS_ENDPOINT`; enabling encryption at rest with AWS Key Management Service answers a different requirement.
- "Clients in an IPv6-only subnet must call the service" maps to dual-stack endpoints at `service-code.region-code.api.aws`, with the `dualstack` form for Amazon S3.
- "A custom-signed request to an S3 Multi-Region Access Point is rejected" maps to SigV4a and the `X-Amz-Region-Set` header; the SDKs and CLI switch to it automatically, so the fix for custom code is to use an SDK.
- "Requests are rejected with a signature error on one host only" maps to clock skew, because a request must normally reach AWS within five minutes of its timestamp.
- "The application receives throttling errors under load" maps to exponential backoff with jitter, which the SDK already applies in standard retry mode; raising `max_attempts` is the distractor that adds load during recovery.
- "One client saturates one resource and can tolerate added latency" maps to `adaptive` retry mode; it is documented as not a general default, so it is the wrong answer for a broad fleet.
- "Failover to the standby Region fails to launch enough instances" maps to service quotas being per account and per Region, and to requesting increases in the DR Region ahead of time; raising the quota in the primary Region is the distractor.
- "Every new account in the organization must start with raised quotas" maps to a Service Quotas request template, which requires AWS Organizations with all features enabled and applies only to accounts created afterward.
- "Be warned before a quota is exhausted" maps to a CloudWatch alarm on the quota's utilization, created from the Service Quotas console.
- "Copy thousands of files to Amazon S3 from a script with the least effort" maps to `aws s3 sync`; `aws s3api put-object` in a loop is the distractor that rebuilds what the high-level command already does.
- "Configure an S3 Storage Lens configuration, an access point or a Batch Operations job from the CLI" maps to `aws s3control`.
- "Return only two fields from a long list, formatted for a human" maps to `--query` with `--output table`; note that `--query` filters client-side, so a service-side `--filters` parameter is better on large data sets.
- "The list command times out on a very large bucket" maps to `--page-size`, which makes more, smaller calls and still returns everything; `--no-paginate` is the distractor because it silently returns only the first page.
- "Check whether a principal is allowed to run an EC2 operation without running it" maps to `--dry-run`, where success is reported as the `DryRunOperation` error.
- "An operator needs to run a few AWS CLI commands with no local installation" maps to AWS CloudShell, which is out of scope for SAA-C03 and in scope for SAP-C02.

## Knowledge check

### 1. A build agent that must not hold a key (Associate)

A company runs continuous integration on servers in its own data center. The build scripts call the AWS CLI to publish artifacts to Amazon S3 and to start a deployment. Security policy forbids any long-lived access key on the build servers, and the team cannot change the build scripts, which already invoke `aws` directly. The company uses AWS IAM Identity Center for workforce access.

Which solution will meet these requirements?

- **A)** Generate an access key for a dedicated IAM user and place it in `~/.aws/credentials` on each build server, rotating it every 30 days.
- **B)** Configure an IAM Identity Center profile in `~/.aws/config` on each build server and have the agent run `aws sso login` before the build, so the CLI resolves short-lived credentials from the SSO token cache.
- **C)** Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as environment variables in the build agent's configuration so nothing is written to disk.
- **D)** Attach an IAM role to the build servers so the AWS CLI can read credentials from the instance metadata service.

<details><summary>Answer</summary>

**Answer: B.** A named profile backed by IAM Identity Center lets the CLI resolve short-lived credentials from the SSO token cache, so no long-lived key exists anywhere and the scripts keep calling `aws` unchanged. A and C both place a long-lived access key on the server, and an environment variable is no better than a file for that requirement: it is still a static secret, merely one that leaks through process listings rather than through a file read. D is not available, because the instance metadata service exists only on EC2 and these servers are on premises; the equivalent for outside AWS is IAM Roles Anywhere with a certificate, which the stem does not mention.

*Where this is covered: Named profiles, signing in, and temporary credentials in tooling.*

</details>

### 2. A standby Region that will not scale (Associate)

A company keeps a warm standby environment in a second AWS Region for disaster recovery. It runs two EC2 instances and a database read replica. During a failover test, the Auto Scaling group stopped after launching 20 of the 60 instances the production workload needs, and the scaling activity reported a limit error. The primary Region has had quota increases applied over several years.

Which solution will meet these requirements?

- **A)** Increase `max_attempts` and enable adaptive retry mode on the Auto Scaling group's clients in the standby Region.
- **B)** Request an increase to the running On-Demand instance vCPU quota in the primary Region so that the standby Region inherits the higher value.
- **C)** Request increases to the affected quotas in the standby Region before the next failover, then run a scaled test to confirm the standby Region can reach production capacity.
- **D)** Replicate the primary Region's applied quota values to the standby Region with an AWS Organizations service control policy.

<details><summary>Answer</summary>

**Answer: C.** Quotas are per account and per Region, applied quotas do not replicate, and increases go through AWS Support and take time, so they must be requested and verified before the event. A treats a hard quota as a transient error; retries cannot create capacity that the quota forbids. B assumes quotas propagate between Regions, which they do not. D misuses service control policies, which restrict permissions and cannot set quota values.

*Where this is covered: Service quotas, and the standby Region that has none.*

</details>

### 3. Protecting instance credentials (Associate)

A security review finds that a web application running on EC2 instances is vulnerable to server-side request forgery, where a crafted input causes the application to issue an HTTP GET to an attacker-chosen URL. The reviewers are concerned that an attacker could retrieve the instance role's credentials. The application must keep working and must continue to obtain its credentials from the instance role. The company also wants to prevent anyone launching a new instance that allows IMDSv1.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Confirm that the `MetadataNoToken` metric is zero, then require IMDSv2 on the running instances and set the account-level default to require it in each Region.
- **B)** Add a security group rule that denies outbound traffic to 169.254.169.254.
- **C)** Attach a service control policy that denies `ec2:RunInstances` unless the `ec2:MetadataHttpTokens` condition key equals `required`.
- **D)** Add a network ACL rule on the instance subnets that denies traffic to 169.254.169.254.
- **E)** Disable the instance metadata service on the instances.

<details><summary>Answer</summary>

**Answer: A and C.** IMDSv2 requires a PUT to obtain a session token before any metadata GET succeeds, and a forged GET cannot produce that PUT; the default hop limit and the rejection of PUTs carrying `X-Forwarded-For` close the proxy variants. Driving `MetadataNoToken` to zero first proves nothing still uses IMDSv1. The `ec2:MetadataHttpTokens` condition key in a service control policy makes a launch that allows IMDSv1 fail with `UnauthorizedOperation`, which covers instances created later. B and D both fail because the metadata request never leaves the instance, so neither security groups nor network ACLs ever see it. E would stop the attack but also stops the application obtaining its role credentials, which the stem requires.

*Where this is covered: Instance metadata as a credential source, and why IMDSv2 matters.*

</details>

### 4. A list command that times out (Associate)

An operations engineer runs `aws s3api list-objects` against a bucket holding several million objects and the command fails with a timed-out error partway through. The engineer needs the complete list of objects in a single command run.

Which solution will meet these requirements?

- **A)** Add `--no-paginate` to the command.
- **B)** Add `--max-items 100` to the command.
- **C)** Add a `--query` expression that selects only the object keys.
- **D)** Add `--page-size 100` to the command.

<details><summary>Answer</summary>

**Answer: D.** `--page-size` asks the service for fewer items per underlying call, so each call is more likely to finish inside its time budget, while the CLI still follows every pagination token and returns the complete list. A does the opposite of what is needed: it stops the CLI following tokens, so only the first page is returned. B prints only 100 items and a `NextToken`, which is not the complete list in one run. C filters the response after it has already arrived, so it does nothing about a call that times out on the service side.

*Where this is covered: The AWS CLI in practice.*

</details>

### 5. Throttling from a polling fleet (Associate)

A company runs a batch application on 2,000 EC2 instances. Each instance calls `DescribeTags` every second to learn its own configuration. Every caller in the account has begun receiving `RequestLimitExceeded` on `DescribeTags`, while other EC2 API calls succeed normally. The company wants to remove the throttling without weakening the resiliWhich combination of steps will meet these requirements? (Select TWO.)

- **A)** Replace the polling loop with local reads of the instance's own metadata and an Amazon EventBridge notification when configuration changes.
- **B)** Set `AWS_MAX_ATTEMPTS` to 10 on every instance.
- **C)** Stagger the polling interval across instances with a random offset so the calls no longer arrive in lockstep.
- **D)** Switch every client to `legacy` retry mode to allow more retry attempts.
- **E)** Request an increase to the running On-Demand instance vCPU quota for the account.

<details><summary>Answer</summary>

**Answer: A and C.** EC2 throttles each API individually per account and per Region, which is why only `DescribeTags` fails while other calls succeed. Two thousand callers once a second saturate that one bucket, so the durable fix is to stop making the calls, and EventBridge replaces polling with events. Staggering the interval with a random offset addresses the other half of the problem, the synchronized arrival that turns a sustainable average rate into a burst. B increases load precisely when the service is asking for less. D moves to a mode with a narrower retryable error set and no standardized retry quota, and more attempts again means more load. E raises an unrelated capacity quota; the errors are API request-rate throttling, not a shortage of vCPUs.

*Where this is covered: Retries, exponential backoff with jitter, and throttling.*

</details>

### 6. A federal compliance requirement (Associate)

A company wins a contract with a United States government agency. The contract requires that all connections its application makes to AWS services use a TLS implementation validated against FIPS 140. The application runs on EC2 and calls AWS KMS and Amazon S3 through an AWS SDK.

Which solution will meet these requirements?

- **A)** Enable server-side encryption with AWS KMS keys on the S3 buckets and enable automatic key rotation.
- **B)** Set `AWS_USE_FIPS_ENDPOINT` to `true` in the application's environment, and confirm that each service it calls publishes a FIPS endpoint in that Region.
- **C)** Configure the SDK to use dual-stack endpoints so that requests use `service-code.region-code.api.aws`.
- **D)** Create interface VPC endpoints for AWS KMS and Amazon S3 and point the SDK at them with `--endpoint-url`.

<details><summary>Answer</summary>

**Answer: B.** FIPS endpoints are the ones whose TLS software library is validated against FIPS 140, and the SDK-level switch is `use_fips_endpoint` in the config file or the `AWS_USE_FIPS_ENDPOINT` environment variable. The confirmation step matters because the call fails if no FIPS endpoint exists for that service in that Region. A addresses encryption of stored data, which is a different requirement from the cryptography used on the connection. C selects IPv6 capability, not FIPS validation. D changes the network path so traffic stays on the AWS network, which is useful but does not make the TLS implementation FIPS validated.

*Where this is covered: Service endpoints: Regional, global, dual-stack and FIPS.*

</details>

### 7. Scripting three S3 tasks (Associate)

An engineer is writing a deployment script that must do three things with the AWS CLI: copy a local build directory to a bucket, turn on versioning for that bucket, and create an S3 Storage Lens configuration that reports across the account. Each task has to be mapped to the command group that actually provides it.

Which solution will meet these requirements?

- **A)** `aws s3 sync` for the copy, `aws s3 put-bucket-versioning` for versioning, and `aws s3 put-storage-lens-configuration` for Storage Lens.
- **B)** `aws s3 sync` for the copy, `aws s3api put-bucket-versioning` for versioning, and `aws s3api put-storage-lens-configuration` for Storage Lens.
- **C)** `aws s3 sync` for the copy, `aws s3api put-bucket-versioning` for versioning, and `aws s3control put-storage-lens-configuration` for Storage Lens.
- **D)** `aws s3api sync` for the copy, `aws s3api put-bucket-versioning` for versioning, and `aws s3outposts put-storage-lens-configuration` for Storage Lens.

<details><summary>Answer</summary>

**Answer: C.** The three groups divide the work cleanly: `s3` holds the custom high-level file commands including `sync`, `s3api` exposes the bucket and object APIs including `put-bucket-versioning`, and the account-level control plane, where Storage Lens configurations, access points and Batch Operations jobs live, is the separate `s3control` API. A puts two API-level operations in the high-level group, which offers only the simplified file verbs. B puts a control plane operation in `s3api`, which exposes the bucket and object API rather than the control plane API. D invents `aws s3api sync`, since `sync` exists only in the high-level group, and uses `s3outposts`, which manages endpoints for S3 on Outposts.

*Where this is covered: The AWS CLI in practice.*

</details>

### 8. Quotas for accounts that do not exist yet (Professional)

A platform team governs 60 accounts in an AWS Organizations organization with all features enabled. New accounts are vended monthly. Each new workload account has repeatedly hit default quotas for Lambda concurrent executions and EC2 vCPUs during its first deployment, delaying launches by days while increases are approved. The team wants new accounts to start with the higher values, and wants advance warning when an existing account approaches a quota.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Raise the two quotas in the organization's management account so that member accounts inherit the applied values.
- **B)** Configure a Service Quotas quota request template with the required increases and enable template association for the organization.
- **C)** Create Amazon CloudWatch alarms on the utilization of those quotas from the Service Quotas console in each account.
- **D)** Attach a service control policy that sets the Lambda concurrency and EC2 vCPU quota values for every account in the organizational unit.
- **E)** Create an AWS Budgets action that raises the quota automatically when spend on the service increases.

<details><summary>Answer</summary>

**Answer: B and C.** A quota request template holds up to ten quota increases and requests them automatically for every account created in the organization afterward, which is exactly the vending problem; it requires all features enabled, which this organization has. CloudWatch alarms created from a quota's page watch utilization and give warning before exhaustion. A is wrong because applied quotas belong to one account and one Region and are never inherited. D misuses service control policies, which constrain permissions and cannot set quota values. E confuses cost controls with capacity: AWS Budgets tracks spend and cannot change a service quota.

*Where this is covered: Service quotas, and the standby Region that has none.*

</details>

### 9. A build host running as the wrong identity (Professional)

A build host in a shared services account has an instance profile granting a narrowly scoped deployment role. Most builds behave correctly, but jobs started from one long-lived agent session intermittently succeed at actions the deployment role does not allow, and CloudTrail shows those calls were made by a developer's IAM user. The team must make every build run as the instance role, without changing the build scripts.

Which solution will meet these requirements?

- **A)** Remove the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_SESSION_TOKEN` variables from the agent's environment and restart the agent, so the credential chain falls through to the instance profile.
- **B)** Leave the environment as it is, because instance profile credentials take precedence over environment variables in the credential provider chain.
- **C)** Add `--profile default` to every AWS CLI invocation in the build scripts.
- **D)** Increase the maximum session duration on the deployment role so that its credentials do not expire mid-build.

<details><summary>Answer</summary>

**Answer: A.** The documented CLI precedence puts command line options first, environment variables second and Amazon EC2 instance profile credentials last, so a stale exported key in a long-lived agent session overrides the instance profile for every command that session runs. Clearing the variables lets the chain reach the instance profile. B states the precedence backwards. C changes the build scripts, which the stem forbids, and the stem forbids changing the build scripts, which is where a profile would have to be named. D addresses expiry, which is not the symptom: the calls are succeeding, just as the wrong principal.

*Where this is covered: Where credentials come from: the provider chain.*

</details>

### 10. Signing requests for a multi-Region bucket (Professional)

A company serves a global application from two Regions and fronts its object storage with an Amazon S3 Multi-Region Access Point so that requests route to the nearest healthy Region and fail over automatically. One legacy component is written in a language with no AWS SDK and builds its own signed HTTPS requests with SigV4. Requests from that component to the Multi-Region Access Point are rejected, while requests from components using AWS SDKs succeed.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Have the legacy component request presigned URLs from a service that uses an AWS SDK, and fetch each object through the presigned URL.
- **B)** Configure the legacy component to sign with SigV4 for `us-east-1` and rely on the Multi-Region Access Point to route the request.
- **C)** Replace the Multi-Region Access Point with Regional bucket endpoints and an Amazon Route 53 latency routing policy in front of them.
- **D)** Rewrite the legacy component's AWS calls to use an AWS SDK, which switches to SigV4a and the `X-Amz-Region-Set` header for Multi-Region Access Point requests automatically.

<details><summary>Answer</summary>

**Answer: D.** A Multi-Region Access Point request needs an asymmetric SigV4a signature that is verifiable in more than one Region, carrying the set of valid Regions in `X-Amz-Region-Set` rather than a single Region in the credential scope, and AWS documents that the SDKs and CLI switch to SigV4a for these requests with no configuration. B fails because a symmetric SigV4 signature is bound to the Region in its credential scope. A shifts object access to a URL-based workaround and does not fix the component's own signed calls, adding a service in the request path for every object. C meets the routing requirement but removes the Multi-Region Access Point the stem says the company uses, and DNS failover does not give the same single global endpoint behavior.

*Where this is covered: Signing a request: SigV4, and what SigV4a adds.*

</details>

## Summary

Working with AWS is a chain of decisions about one HTTPS API. Decide which endpoint a call goes to: the standard Regional one by default, a dual-stack host when clients speak IPv6, a FIPS host when a government requirement names FIPS 140, and a VPC endpoint when the requirement is about the network path rather than the URL. Decide how the request is signed, which is SigV4 for everything and SigV4a automatically when a Multi-Region Access Point is involved, and remember that a clock more than five minutes out stops signing working at all. Decide where credentials come from by choosing a link in the provider chain: IAM Identity Center with `aws sso login` for people, an instance profile or task role for workloads, `role_arn` with `source_profile` for cross-account hops, and `credential_process` when a tool cannot do any of those. Require IMDSv2 so a forged GET cannot lift those credentials. Decide what happens when a call fails: standard retry mode, with adaptive reserved for a single saturated resource. Then decide what happens before failure: raise quotas in every Region you plan to fail over into, alarm on utilization, and template the increases for accounts that do not exist yet.

## Related units

- [AWS Identity and Access Management](../07-security/iam.md): AWS STS, role assumption, session duration and the one-hour role chaining ceiling behind every temporary credential
- [AWS Organizations, IAM Identity Center and AWS Control Tower](../07-security/organizations-identity-center-and-control-tower.md): the federation and account structure that `aws sso login` and quota request templates depend on
- [AWS CloudFormation](cloudformation.md): declarative provisioning where a script of CLI calls would otherwise accumulate
- [AWS Config, Trusted Advisor, Health and Well-Architected](config-trusted-advisor-health-and-well-architected.md): Trusted Advisor service limit checks as the detective view of quota usage
- [Amazon CloudWatch](cloudwatch.md): the alarms on quota utilization and the `MetadataNoToken` metric used to retire IMDSv1
- [AWS CloudTrail](cloudtrail.md): the record of every API call, its caller and its request ID
- [Amazon VPC](../04-networking/vpc.md): interface and gateway endpoints for reaching service endpoints privately
- [Amazon EC2](../02-compute/ec2.md): instance profiles, launch templates and the instance metadata options set at launch

## Sources

- [AWS SDKs and Tools environment variable list](https://docs.aws.amazon.com/sdkref/latest/guide/environment-variables.html): AWS_REGION as the cross-SDK setting and AWS_DEFAULT_REGION as the CLI-era name

- [AWS service endpoints](https://docs.aws.amazon.com/general/latest/gr/rande.html): Regional, general and global endpoint syntax, plus the FIPS and dual-stack host patterns and the TLS minimum
- [Dual-stack and FIPS endpoints](https://docs.aws.amazon.com/sdkref/latest/guide/feature-endpoints.html): `use_dualstack_endpoint`, `use_fips_endpoint`, their defaults and the failure behavior when a variant does not exist
- [AWS Signature Version 4 for API requests](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_sigv.html): what SigV4 does, how SigV4a differs, and the automatic switch for Multi-Region Access Points
- [Elements of an AWS API request signature](https://docs.aws.amazon.com/general/latest/gr/sigv4_elements.html): the algorithm identifiers, credential scope contents and the `X-Amz-Region-Set` header
- [AWS SDKs and Tools standardized credential providers](https://docs.aws.amazon.com/sdkref/latest/guide/standardized-credentials.html): the provider list and the automatic credential renewal statement
- [Configuring settings for the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html): the full credentials and configuration precedence order and the clock accuracy warning
- [Using shared config and credentials files](https://docs.aws.amazon.com/sdkref/latest/guide/file-format.html): INI format, profile section syntax and which settings belong in the credentials file
- [Using an IAM role in the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-role.html): `role_arn`, `source_profile`, `credential_source`, `mfa_serial` and `external_id`
- [Configuring IAM Identity Center authentication with the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html): `aws configure sso`, the `sso-session` block, `aws sso login` and the token cache
- [Login for AWS local development using console credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html): `aws login`, the 2.32.0 minimum version, the 12-hour refresh and the `credential_process` bridge
- [Using Amazon EC2 instance metadata as credentials in the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-metadata.html): instance profile credentials and `credential_source = Ec2InstanceMetadata`
- [Use the Instance Metadata Service to access instance metadata](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html): IMDSv2 session tokens, the default hop limit of 1 and the `X-Forwarded-For` rejection
- [Configure the Instance Metadata Service options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html): the metadata version options, the order of precedence and account-level enforcement
- [Transition to using Instance Metadata Service Version 2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-metadata-transition-to-version-2.html): `MetadataNoToken`, `MetadataNoTokenRejected`, the condition keys and `ec2:RoleDelivery`
- [What is the AWS Command Line Interface?](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html): AWS CLI version 2 as the current version, the bundled installer and console parity in the API and CLI
- [What is the AWS Command Line Interface version 1?](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-welcome.html): version 1 in maintenance mode and its dependency on Python
- [CLI v1 maintenance mode announcement](https://aws.amazon.com/blogs/developer/cli-v1-maintenance-mode-announcement/): the 15 July 2026 maintenance date and the 15 July 2027 end of support date
- [AWS SDKs and Tools version lifecycle](https://docs.aws.amazon.com/sdkref/latest/guide/version-support-matrix.html): which SDK major versions are generally available, in maintenance or past end of support
- [Using Amazon S3 in the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-services-s3.html): the high-level `s3` commands compared with API-level `s3api`
- [`s3control` command reference](https://docs.aws.amazon.com/cli/latest/reference/s3control/index.html): the control plane operations for access points, Batch Operations jobs and Storage Lens
- [Setting the output format in the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-output-format.html): the six output formats and how `--output text` interacts with `--query`
- [Filtering output in the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-filter.html): JMESPath client-side filtering compared with server-side filter parameters
- [Using the pagination options in the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-pagination.html): `--no-paginate`, `--page-size`, `--max-items` and `--starting-token`
- [RunInstances](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_RunInstances.html): the `DryRun` parameter and the `DryRunOperation` and `UnauthorizedOperation` responses
- [AWS CLI retries](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-retries.html): legacy, standard and adaptive modes, the version 2 default, attempt counts and the retryable error lists
- [Retry behavior](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html): the full jitter backoff formula, base delays, the 20 second cap, the retry quota token bucket and the opt-in setting
- [Request throttling for the Amazon EC2 API](https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-throttling.html): the token bucket model, request and resource rate limiting and `RequestLimitExceeded`
- [What is Service Quotas?](https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html): default and applied quotas, adjustable values, global quotas and utilization
- [Using Service Quotas request templates](https://docs.aws.amazon.com/servicequotas/latest/userguide/organization-templates.html): the all-features requirement, the ten-quota limit and the new-accounts-only behavior
- [Service Quotas and Amazon CloudWatch alarms](https://docs.aws.amazon.com/servicequotas/latest/userguide/configure-cloudwatch.html): creating a utilization alarm from a quota page
- [What is AWS CloudShell?](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html): the pre-authenticated browser shell, 1 GB of persistent storage per Region and no additional charge
- [Service quotas and restrictions for AWS CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/limits.html): concurrent shells, monthly usage, command size and VPC environment timeouts
- [Getting Amazon S3 request IDs for AWS Support](https://docs.aws.amazon.com/AmazonS3/latest/userguide/get-request-ids.html): `x-amz-request-id` and `x-amz-id-2` and retrieving them with `--debug`
- [Introducing AWS API models and publicly available resources for AWS API definitions](https://aws.amazon.com/blogs/aws/introducing-aws-api-models-and-publicly-available-resources-for-aws-api-definitions/): that AWS has generated its SDK clients and CLI tools from Smithy models since 2018
