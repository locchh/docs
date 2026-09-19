# Amazon CloudFront

**Where it sits on the exams.** **Amazon CloudFront** is the AWS content delivery network (CDN): a global fleet of edge locations that terminate viewer connections close to the user, serve what they can from cache, and fetch the rest from your origin over the AWS backbone. It fronts web content, APIs and media, and it is also where AWS puts its edge security controls, so it appears in performance, cost and security scenarios alike. It carries SAA-C03 tasks 2.1, 3.4 and 4.4 and SAP-C02 tasks 2.3, 2.5 and 3.3. The rule of thumb the exam wants is that CloudFront is the answer when content is cacheable or when terminating the connection at the edge is worth something, and that the two decisions behind every CloudFront question are what goes into the cache key and how the origin is protected.

## What CloudFront is and how a request is served

A **distribution** is the configuration object: it names one or more origins, holds the rules that decide how each request is handled, and gets a domain name such as `d111111abcdef8.cloudfront.net`. CloudFront pushes that configuration, though not your content, to every point of presence. Most designs use a standard distribution, a standalone configuration for one site or application; a multi-tenant distribution, managed through CloudFront SaaS Manager, exists for software-as-a-service providers running hundreds of near-identical configurations from one template.

Content is cached in two tiers by default. An **edge location** is the point of presence that answers the viewer. Behind it sits a **regional edge cache**, a larger mid-tier cache; a miss at the edge goes there before it goes to the origin, and because that cache is bigger, objects survive in it longer. When the origin is an S3 bucket, the point of presence skips the regional edge cache in that bucket's Region. A third, optional layer, Origin Shield, is covered below.

To serve traffic on your own hostname you add alternate domain names, up to 100 per distribution, and attach a certificate that covers them. The certificate comes from **AWS Certificate Manager (ACM)**, the service that issues, stores and renews TLS certificates, and for CloudFront it must be requested in the US East (N. Virginia) Region, `us-east-1`, regardless of where anything else runs. That Region rule is tested directly. You then point **Amazon Route 53**, the AWS DNS and domain registration service, at the distribution with an alias record, which works at the zone apex where a CNAME cannot and is not charged per query. Certificates use server name indication (SNI) by default; the dedicated IP address option exists for clients too old to send SNI and carries a substantial monthly charge, so it is the wrong answer unless the stem names legacy clients.

Each cache behavior sets a viewer protocol policy of HTTP and HTTPS, redirect HTTP to HTTPS, or HTTPS only. At the distribution level you choose the supported HTTP versions. HTTP/2 needs TLS 1.2 and SNI. HTTP/3 runs over QUIC, a UDP-based transport, needs TLS 1.3 and SNI regardless of which security policy you selected, and supports connection migration so a viewer moving between Wi-Fi and cellular keeps its connection. CloudFront advertises HTTP/3 with the `Alt-Svc` header automatically, clients that cannot use it fall back, enabling it costs nothing extra, and the origin leg still uses HTTP/1.1. A default root object, normally `index.html`, is served when a viewer asks for the bare distribution URL.

Three AWS services front an application, and the exam separates them cleanly. CloudFront is for cacheable content and for HTTP and HTTPS connections that benefit from edge termination. **AWS Global Accelerator**, which fronts applications with static anycast IP addresses, is for non-HTTP protocols, clients needing fixed addresses in a firewall allowlist, and failover that must not wait on DNS caching. Route 53 decides which address a client is told to use at all. See [Amazon Route 53](route53.md) and [AWS Global Accelerator](global-accelerator.md).

## Origins, origin access control and origin failover

An origin is the definitive source for your content, and a distribution can hold up to 100 of them. An **Amazon Simple Storage Service (Amazon S3)** bucket addressed by its REST endpoint, such as `amzn-s3-demo-bucket.s3.us-west-2.amazonaws.com`, is an S3 origin; S3 is the AWS object store. Everything else is a custom origin: an **Application Load Balancer** or **Network Load Balancer**, the Layer 4 load balancer, from **Elastic Load Balancing**, the AWS load balancing service; an **Amazon Elastic Compute Cloud (Amazon EC2)** instance, the virtual server service; an **AWS Lambda** function URL, where Lambda is the serverless function service; an **Amazon API Gateway** endpoint, the managed API front door; or your own web server. An S3 bucket configured as a static website endpoint is also a custom origin, which matters because that form supports only HTTP and only port 80.

**Origin access control (OAC)** keeps an S3 bucket private while CloudFront reads from it. CloudFront signs each origin request, and a bucket policy allows the `cloudfront.amazonaws.com` service principal with an `AWS:SourceArn` condition naming the distribution, so only that distribution can read the bucket. AWS recommends OAC over the older **origin access identity (OAI)**, which AWS now documents as legacy and not recommended, because OAC supports buckets in all Regions including opt-in Regions launched after December 2022, supports server-side encryption with **AWS Key Management Service (AWS KMS)**, the managed key service, and supports `PUT` and `DELETE`. With SSE-KMS you must also allow the CloudFront service principal in the KMS key policy. Bucket Object Ownership must be bucket owner enforced, and neither OAC nor OAI works with an S3 website endpoint. Bucket policies belong to [Amazon S3](../01-storage/s3.md).

```json
{
  "Sid": "AllowCloudFrontServicePrincipalReadOnly",
  "Effect": "Allow",
  "Principal": { "Service": "cloudfront.amazonaws.com" },
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::amzn-s3-demo-bucket/*",
  "Condition": { "StringEquals": {
    "AWS:SourceArn": "arn:aws:cloudfront::111122223333:distribution/E1234567890ABC" } }
}
```

For a custom origin you choose the origin protocol policy, HTTP only, HTTPS only, or match viewer, plus the ports and the minimum origin SSL protocol. If CloudFront connects over HTTPS and no name in the origin's certificate matches the configured origin domain, viewers get HTTP 502. A **VPC origin** is the modern way to protect a non-S3 origin: a load balancer or EC2 instance in a private subnet of an **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network your resources run in, becomes reachable only through your distribution, with no public IP address and no shared secret to rotate. The quota is 25 VPC origins per account. For an origin that must stay public, the older pattern applies: CloudFront adds a secret custom header to every origin request and the origin rejects requests without it.

Timeouts decide how fast a broken origin is noticed: connection attempts default to 3 and range 1 to 3, the connection timeout defaults to 10 seconds and ranges 1 to 10, so CloudFront spends up to 30 seconds before giving up, and the response timeout, also called the origin read timeout, defaults to 30 seconds and can be raised to 120.

An **origin group** pairs a primary origin with a secondary and is selected by a cache behavior in place of a single origin. On a cache miss CloudFront always tries the primary; if the primary returns one of the status codes you nominated; a connection failure or a timeout counts only when 503 or 504 respectively is among them from 400, 403, 404, 416, 429, 500, 502, 503 and 504, CloudFront retries against the secondary. Two limits get tested. Failover happens only for `GET`, `HEAD` and `OPTIONS` requests, so a write path is never protected by an origin group, and every request still goes to the primary first, so the feature reduces viewer-visible errors rather than shifting load. Ten origin groups are allowed per distribution, and the classic exam pattern is an S3 bucket in one Region as primary with a replicated bucket in a second Region as secondary.

**Origin Shield** adds one more caching layer, in an AWS Region you nominate, in front of the origin. Every request from every regional edge cache passes through it, so identical requests are collapsed and the origin can see as few as one request per object. Enable it in the Region with the lowest latency to the origin. It helps when viewers span continents, when the origin does just-in-time packaging or image processing, when the origin is on premises with limited bandwidth, and when several CDNs share one origin. It is a poor fit for uncacheable content and carries its own charge, so the exam signal is duplicate origin requests for the same object.

## Cache behaviors and the precedence of path patterns

A **cache behavior** attaches a path pattern to one origin or origin group plus the caching, protocol, method and security settings for matching requests. Every distribution has a default cache behavior whose path pattern is `*` and cannot be changed. Additional behaviors form an ordered list, and the ordering is the whole trick: CloudFront compares the request path against the patterns in order and the first match wins, with the default behavior always evaluated last. Up to 75 cache behaviors are allowed per distribution.

Patterns use `*` for zero or more characters and `?` for exactly one, are at most 255 characters, and are case sensitive, so `*.jpg` does not match `LOGO.JPG`. A pattern covers subdirectories, so `images/*.jpg` matches `images/product1/a.jpg`; to treat one subdirectory differently, create a behavior for `images/product1/*` and move it above the one for `images/*`. Query strings and cookies are ignored when matching, and CloudFront normalizes the URI path per RFC 3986 before matching, so `/a/b/..?c=1` matches a behavior for `/a*` rather than `/a/b*`.

AWS flags the security consequence explicitly, and it is a good exam trap. If a request matches two behaviors and the earlier one does not require signed URLs while the later one does, the request is served without a signature, because only the first match is applied. Order restrictive behaviors above permissive ones. A second rule: each behavior points at exactly one origin, so a distribution with two origins and only the default behavior never uses the second.

Allowed HTTP methods are set per behavior. CloudFront caches responses to `GET` and `HEAD`, and optionally to `OPTIONS`, which is cached under a separate key; responses to `POST`, `PUT`, `PATCH` and `DELETE` are proxied but never cached. Allowing the write methods does not authorize them at the origin, so a bucket policy or the application must still refuse what you do not want.

## Cache policies, origin request policies, the cache key and invalidation

The **cache key** is the identifier CloudFront uses to decide whether a request is a hit. By default it is only the distribution domain name and the URL path, so two requests differing only in query string or cookie share one cached object. Fewer values in the key means a higher cache hit ratio; more values means correctness when the origin genuinely varies its response. A **cache policy** attaches to a behavior to add specific headers, cookies and query strings to the key, and it also carries the minimum, maximum and default TTL and the compression setting. An **origin request policy** is separate and controls what CloudFront forwards to the origin without keying on it. Anything in the cache key is forwarded automatically, so the origin request policy is for values the origin wants for logging or analytics but that must not fragment the cache.

The older way, forwarded values configured directly on a cache behavior, is what AWS now calls legacy cache settings, and the documentation recommends a cache policy or origin request policy instead. The reasons are worth knowing. Legacy settings conflate forwarding with caching, so the only way to give the origin a header was to key on it; they are per behavior and cannot be reused, while a policy is a named object shared across behaviors and distributions; and forwarding all headers with legacy settings disables caching for that behavior entirely, the quiet cause of a zero cache hit ratio.

Managed policies cover most cases. `CachingOptimized` excludes every query string and cookie and keys only on the normalized `Accept-Encoding` header, with a minimum TTL of 1 second, a default of 24 hours and a maximum of 365 days; it is the right default for static assets. `CachingDisabled` is for uncacheable paths and APIs, and `UseOriginCacheControlHeaders` defers to what the origin sends. Custom policies are limited to 20 per account.

TTL settings and origin headers interact by a rule the exam likes. When the origin sends `Cache-Control: max-age` and the minimum TTL is 0, CloudFront caches for the lesser of `max-age` and the maximum TTL. When the origin sends nothing, CloudFront caches for the default TTL, 86,400 seconds unless you change it. A minimum TTL above 0 clamps everything upward, and AWS warns that it overrides `no-cache`, `no-store` and `private` from the origin, so a nonzero minimum TTL on an authenticated path is a real leak risk. For CloudFront `s-maxage` takes precedence over `max-age` while browsers still honor `max-age`, which is how you cache longer at the edge than in the browser. CloudFront also honors `stale-while-revalidate` and `stale-if-error`, serving stale content while refreshing or while the origin returns a 5xx, both capped by the maximum TTL.

An **invalidation** removes objects from the cache before they expire. The first 1,000 invalidation paths per month are free per AWS account across all distributions, and you pay per path beyond that; a wildcard path such as `/*` counts as one path no matter how many files it clears, and cache tag invalidations draw on the same allowance. AWS recommends versioned file names over invalidation, because versioning also defeats browser and corporate proxy caches, makes access logs interpretable, and costs nothing. Custom error pages let you return your own body for a given status code and set how long that error is cached.

## Protecting the content and the origin

Exam questions about CloudFront security are usually decided by one phrase in the stem. Five of the six controls below are CloudFront's own; **AWS WAF** is the separate managed web application firewall that attaches to a distribution. Read the table by matching that phrase in the last column, then check the middle column to confirm the control actually addresses the threat described.

| Control | What it protects against | Wording that selects it |
|---|---|---|
| Origin access control (OAC) | Viewers reaching the S3 bucket directly and bypassing CloudFront and its controls | "the bucket must not be publicly accessible", "reachable only through the distribution", "private S3 origin with HTTPS" |
| Signed URLs | Access to one file by anyone without a valid, time-limited link | "a single file", "one download link per purchase", "clients that do not support cookies" |
| Signed cookies | Access to a whole set of restricted files, without changing any of their URLs | "an entire subscription library", "all premium videos", "we cannot change the existing URLs" |
| Geo restriction | Viewers in countries where you have no right to serve the content at all | "licensing prohibits", "must not be available in these countries", "block an entire country" |
| AWS WAF | Malicious or abusive HTTP requests: injection, bad bots, floods from one client, and country blocking finer than a whole distribution | "SQL injection", "OWASP Top 10", "rate limit one client", "block a country for part of the site" |
| VPC origins | The load balancer or instances behind the distribution being reachable from the internet | "origin must have no public IP address", "CloudFront must be the only ingress" |

A **signed URL** and a **signed cookie** use the same cryptography and differ only in packaging. A signed URL carries the policy and signature in the query string of one URL, which suits a single file and clients that cannot store cookies. Signed cookies set `Set-Cookie` headers once and then authorize every later request matching the policy, which suits many files and keeps URLs unchanged. Either can use a canned policy, which supports only an expiry time and cannot be reused across files, or a custom policy, which adds an optional start time, an optional source IP address or CIDR range, and a wildcard resource covering many files.

Whoever signs must be registered on the distribution as a signer, and there are two kinds. A **key group** is the recommended kind: you upload a public key to CloudFront, put it in a key group, and associate up to 4 key groups with a cache behavior, each holding up to 5 public keys. Key groups are managed through the CloudFront API, so creation and rotation can be automated and restricted with identity-based permissions. The legacy alternative is a trusted signer, an AWS account holding a CloudFront key pair that only the account root user can manage through the console, with at most 2 active key pairs per account. Any stem mentioning root user key pairs or automated key rotation is pointing at key groups. Keys must be SSH-2 RSA 2048 or ECDSA 256 in PEM format, and adding a signer to a behavior immediately requires signatures for everything that behavior matches.

**Geo restriction** is configured once for the whole distribution as an allowlist or a denylist of countries, and blocked viewers get HTTP 403 with an optional custom error page. CloudFront resolves country from a third-party IP database that AWS states is about 99.8 percent accurate overall, and serves the content normally when it cannot determine a location. Because it is distribution-wide and country-level only, anything finer needs an AWS WAF geographic match rule or a third-party geolocation service. AWS WAF attaches as a global web ACL evaluated at the edge before the request reaches the origin, bringing managed rule groups for common vulnerabilities, rate-based rules that throttle one client IP address, and bot control. **AWS Shield**, the AWS DDoS protection service, comes in two forms: Shield Standard is included automatically at no extra charge and covers network and transport layer attacks, while Shield Advanced is the paid subscription adding response team access, cost protection and automatic application-layer mitigation. Both are taught in [AWS WAF, AWS Shield, AWS Firewall Manager and AWS Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md).

**Field-level encryption** keeps one or two fields secret from your own systems. You give CloudFront an RSA 2048 public key, define a profile naming up to 10 fields in a `POST` body, wrap it in a configuration, and link that configuration to a cache behavior. CloudFront encrypts those fields at the edge, and only the component holding the private key can read them, so a card number stays ciphertext through the load balancer, the application tier and the logs. The origin must support chunked encoding, and nothing else is encrypted beyond the usual TLS, so this complements HTTPS rather than replacing it.

## Edge functions, observability and the pricing shape

CloudFront can run your own code on four events: viewer request, origin request, origin response and viewer response. **CloudFront Functions** is the native, JavaScript-only runtime that executes at the edge location itself with submillisecond duration and scales to millions of requests per second, and it runs on viewer request and viewer response only. **Lambda@Edge** is Lambda replicated to CloudFront's infrastructure, runs on all four events, and has network access, file system access and access to the request body. The rule is that cache key normalization, header rewrites, redirects and token validation belong in CloudFront Functions, while anything needing a network call, a library or an origin-side trigger belongs in Lambda@Edge. The full comparison and the Lambda@Edge restrictions live in [AWS Lambda](../02-compute/lambda.md).

**Amazon CloudWatch**, the AWS metrics, logs and alarm service, receives distribution metrics including requests, bytes transferred and 4xx and 5xx error rates at no extra charge, with additional metrics such as cache hit rate available for a fee. Standard logs record one line per request. Standard logging v2 delivers them to CloudWatch Logs, to **Amazon Data Firehose**, formerly Kinesis Data Firehose, the managed streaming delivery service, or to Amazon S3, and lets you select fields, partition the output and deliver across accounts; standard logging legacy writes to S3 only. Either way delivery is best effort and a line can arrive long after the request or not at all, so logs are for analysis, not billing reconciliation. Real-time logs are the alternative when seconds matter: they reach **Amazon Kinesis Data Streams**, the managed real-time streaming service, within seconds, and you choose a sampling rate, a field list and which cache behaviors they cover, at a charge per log line on top of the Kinesis charge. Edge function logs go to CloudWatch Logs, and API calls to **AWS CloudTrail**, the service that records AWS API activity.

Pay-as-you-go pricing has two main axes: data transfer out from edge locations to viewers, and HTTP and HTTPS requests, both priced by the geography that served the request. The fact that decides cost questions is the one that costs nothing: data transfer from an AWS origin to CloudFront is always free when the origin is an AWS service such as S3, Elastic Load Balancing or API Gateway, so putting CloudFront in front of a bucket or a load balancer converts Regional egress charges into CloudFront delivery charges rather than adding to them. A free tier of 1 TB of data transfer out and 10 million requests per month applies to pay-as-you-go usage. Origin Shield, real-time logs, dedicated IP custom SSL and invalidation paths beyond the free 1,000 are separate line items. AWS has since added flat-rate pricing plans, a monthly price per distribution across Free, Pro, Business, Premium and custom tiers, each bundling the CDN with AWS WAF, DDoS protection, Route 53, logging and edge compute under a usage allowance with no overage charges; they are an alternative to pay-as-you-go, and both exams are written against the pay-as-you-go model.

A **price class** is the cost lever inside a distribution. Price Class All uses every edge location, Price Class 200 excludes the most expensive ones, and Price Class 100 is the smallest and cheapest set. Viewers in an excluded geography are still served, from the nearest included location, so the trade is latency for rate, not availability for rate. The other levers are structural: a higher cache hit ratio means fewer origin fetches and less origin compute, Origin Shield collapses duplicate origin requests, and a cache key that excludes values the origin does not vary on is usually worth more than any pricing option. That is the strategic case for a CDN, and what a cost-optimization question about edge caching is testing.

## Professional depth

At organization scale the distribution is rarely in the same account as the origin. A common landing zone puts public-facing distributions in a shared perimeter account while workloads stay in their own accounts, which works because OAC is an identity on the distribution: the bucket policy in the workload account allows the `cloudfront.amazonaws.com` service principal with an `AWS:SourceArn` condition naming the distribution ARN, which carries the perimeter account ID. The same split drives logging, since standard logging v2 supports cross-account delivery into a log archive account, and security, since **AWS Firewall Manager**, which applies security policies across accounts, can enforce a baseline web ACL on every distribution in an **AWS Organizations** organization, the service that groups AWS accounts under central governance.

> **Professional depth.** When a question adds "the configuration change must be tested with real traffic before it reaches all viewers", the answer is CloudFront continuous deployment: a staging distribution carries the new configuration and you send it either a fixed percentage of traffic or only requests carrying a specific header, then promote it. The quota is 20 staging distributions per account.

The quotas that bite at scale are per distribution rather than per account. One distribution is limited by default to 150 Gbps of data transfer and 250,000 requests per second, both increasable on request, and a launch that will exceed either needs the increase filed in advance rather than discovered during the event. Elsewhere the defaults are 500 distributions per account, 100 alternate domain names, 100 origins and 75 cache behaviors per distribution, and 20 custom cache policies and 20 custom origin request policies per account. AWS also caps a chain of requests to an origin at 2 distributions and advises against putting one distribution in front of another.

Multi-Region and multi-CDN designs combine several features. An origin group gives automatic failover between two Regional origins for read traffic, but only for `GET`, `HEAD` and `OPTIONS`, so a design with writes still needs Route 53 failover for the write path. Origin Shield in front of a shared origin is the standard answer when a second CDN generates duplicate origin fetches. And a SaaS provider onboarding thousands of customer domains hits the 100 alternate domain names per distribution limit long before any other, which is what multi-tenant distributions exist to solve.

The last Professional theme is failure modes that look like something else. A cache hit ratio near zero usually means the cache key includes a value that varies per viewer, a cookie or a tracking query string, or that a legacy behavior forwards all headers. Viewers seeing another user's personalized page usually means a nonzero minimum TTL overriding `Cache-Control: private`, or an authenticated path sharing a cache behavior with a static one. Intermittent 502 responses from a custom origin usually mean the origin certificate does not match the configured origin domain name.

## Worked scenario

A streaming company sells regional subscriptions. Video segments and images sit in an S3 bucket replicated to a second Region, the catalog and playback APIs run behind an Application Load Balancer in private subnets, and licensing forbids serving some catalogs outside their territories. Subscribers must not be able to share playback URLs, the marketing site must stay fast worldwide, and finance wants the origin bill to fall.

One distribution fronts all of it. The default cache behavior points at the marketing site with the `CachingOptimized` managed cache policy. A behavior for `/api/*`, ordered above the default, points at the Application Load Balancer configured as a VPC origin so it has no public address, and uses `CachingDisabled` with an origin request policy that forwards the headers and cookies the API needs without keying on them. A behavior for `/media/*`, ordered above both, points at an origin group whose primary is the S3 bucket with origin access control and whose secondary is the replicated bucket, with 500, 502, 503 and 504 as failover codes. That behavior requires signed cookies from a key group, because a subscriber gets a whole library rather than one file and the existing URLs cannot change.

Geo restriction is not the right tool for the licensing rule, because it applies to the whole distribution and the marketing site must stay global; an AWS WAF geographic match rule scoped to `/media/*` does the job, alongside managed rule groups and a rate-based rule on `/api/*`. Origin Shield in the Region holding the primary bucket collapses the duplicate segment requests arriving from regional edge caches on three continents. Content is deployed with versioned object names rather than invalidations, standard logging v2 delivers to a central log archive account, and real-time logs sample the playback paths into Kinesis Data Streams for a live quality dashboard.

When the exam asks about this scenario, the keyed answer is signed cookies with a key group for the library, origin access control with a private bucket, an origin group for cross-Region read failover, AWS WAF rather than geo restriction for the per-path licensing rule, and Origin Shield for the duplicate origin fetches.

## Exam lens

- "Fail over to a second Region automatically when the origin returns 5xx" maps to an origin group; it covers only `GET`, `HEAD` and `OPTIONS`.
- "A directory needs a different origin or different caching" maps to an extra cache behavior placed above the broader pattern, because the first matching path pattern wins.
- "Serve a static site over HTTPS from a private S3 bucket" maps to origin access control with a bucket policy naming the distribution; an S3 website endpoint is the distractor, because it is HTTP only and needs public objects.
- "Cache hit ratio is very low" maps to trimming the cache key with a cache policy and moving values the origin only wants for analytics into an origin request policy; forwarding all headers with legacy settings disables caching outright.
- "Push a content change to viewers immediately" maps to an invalidation, with 1,000 free paths per month per account and a wildcard counting as one path; versioned file names are the answer when the stem says "frequently".
- "One download link per purchase, and it must expire" maps to a signed URL; signed cookies are the answer instead when a whole library is granted without changing existing URLs.
- "The load balancer must not be reachable from the internet" maps to a VPC origin; a secret custom header is the older answer and the distractor when the origin can move to a private subnet.
- "Reduce duplicate requests reaching an origin that does just-in-time packaging" maps to Origin Shield.
- "Rotate signing keys automatically and avoid the root user" maps to a trusted key group; the legacy trusted signer with a CloudFront key pair is the distractor.
- "Block an entire country for licensing reasons" maps to geo restriction; when only part of the content is restricted, the answer is an AWS WAF geographic match rule, because geo restriction is distribution-wide.
- "Credit card numbers must stay encrypted through the application tier" maps to field-level encryption on up to 10 `POST` fields, not to HTTPS alone.
- "Reduce delivery cost and we accept higher latency in some geographies" maps to a price class; viewers are still served, from the nearest included location.
- "Reduce the origin's data transfer bill" maps to CloudFront itself, because data transfer from AWS origins to CloudFront is free.

## Knowledge check

### 1. Serving a private bucket over HTTPS (Associate)

A company hosts a marketing website as static files in an Amazon S3 bucket. Security requires that the bucket allow no public access and that all viewer traffic use HTTPS on the company's own domain name. The site must load quickly for viewers on three continents.

Which solution will meet these requirements?

- **A)** Enable S3 static website hosting, attach an ACM certificate to the bucket, and point the domain at the website endpoint.
- **B)** Create a CloudFront distribution with the S3 REST endpoint as the origin, configure origin access control, and update the bucket policy to allow only that distribution.
- **C)** Create a CloudFront distribution with the S3 static website endpoint as the origin and enable origin access control on it.
- **D)** Make the objects publicly readable and create a CloudFront distribution with a viewer protocol policy of HTTPS only.

<details><summary>Answer</summary>

**Answer: B.** Origin access control lets CloudFront sign requests to the bucket so the bucket policy can allow only that distribution, which keeps the bucket private while CloudFront supplies HTTPS, a custom domain and global caching. A is not possible: an S3 static website endpoint serves HTTP only and cannot have a certificate attached, and it requires public objects. C cannot be built, because a bucket configured as a website endpoint is a custom origin and neither origin access control nor origin access identity works with it. D meets the HTTPS and performance requirements but leaves the objects publicly readable, so viewers can bypass the distribution entirely, which the stem forbids.

*Where this is covered: Origins, origin access control and origin failover.*

</details>

### 2. Two behaviors, one request (Associate)

A media company serves free trailers under `/media/trailers/` and paid films under `/media/films/` from the same CloudFront distribution. The team created a cache behavior for `/media/*` with no viewer restrictions, then added a behavior for `/media/films/*` that requires signed cookies and placed it below the first one in the list. Testing shows that paid films are downloadable without any cookie.

Which solution will meet these requirements?

- **A)** Move the `/media/films/*` cache behavior above the `/media/*` cache behavior.
- **B)** Change the path pattern of the paid behavior to `*films*` so that it matches more requests.
- **C)** Enable geo restriction on the distribution so that only subscriber countries can reach the films.
- **D)** Add the signed cookie requirement to the default cache behavior as well.

<details><summary>Answer</summary>

**Answer: A.** CloudFront compares a request path against cache behaviors in the order they are listed and applies the first match, so the permissive `/media/*` behavior is answering every request under `/media/` and the restricted behavior is never reached. Moving the more specific, restrictive behavior above the broader one is the documented fix. B changes the pattern but not the ordering, so the first match is still the permissive behavior. C blocks whole countries rather than distinguishing paying subscribers from everyone else, and it applies to the entire distribution. D adds a requirement to a behavior that this request never reaches, because `*` is always evaluated last.

*Where this is covered: Cache behaviors and the precedence of path patterns.*

</details>

### 3. A cache that never hits (Associate)

A retailer put CloudFront in front of an Application Load Balancer for its product catalog. The origin returns identical HTML for a given product regardless of the dozens of marketing and session cookies the browser sends. The cache hit ratio is near zero and origin load has not fallen. The team wants a high cache hit ratio while still letting the origin read the cookies for analytics.

Which solution will meet these requirements?

- **A)** Attach a cache policy that includes all cookies in the cache key.
- **B)** Attach the `CachingDisabled` managed cache policy and raise the origin's instance size.
- **C)** Attach a cache policy that includes no cookies in the cache key, and attach an origin request policy that forwards the cookies to the origin.
- **D)** Set the minimum TTL to 86,400 seconds on the existing cache behavior.

<details><summary>Answer</summary>

**Answer: C.** The cache policy decides the cache key and the origin request policy decides what is forwarded, and everything in the key is forwarded automatically, so excluding the cookies from the key collapses the many per-viewer variants into one cached object while the origin still receives the cookies it wants. A is what is already happening in effect and guarantees a unique object per viewer. B removes caching entirely and treats the symptom by scaling the origin. D forces objects to stay cached for a day but does nothing about the key, so the cache still holds a separate object per cookie combination, and a high minimum TTL would also override any `no-cache` directive the origin sends.

*Where this is covered: Cache policies, origin request policies, the cache key and invalidation.*

</details>

### 4. Access to a whole library (Associate)

A publisher gives paying subscribers access to roughly 40,000 files served through CloudFront. Access must expire when a subscription lapses, the existing file URLs are printed in a mobile app and cannot change, and the team does not want to generate a link per file.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Generate a CloudFront signed URL for every file and have the app request a fresh list at startup.
- **B)** Set signed cookies after the subscriber authenticates, with a trusted key group associated with the cache behavior that serves the library.
- **C)** Enable geo restriction so that only countries with active subscribers can reach the content.
- **D)** Put an AWS WAF web ACL on the distribution with a rule that allows only authenticated subscriber IP addresses.

<details><summary>Answer</summary>

**Answer: B.** Signed cookies authorize a set of files matching one policy without altering any URL, which is exactly the constraint in the stem, and a key group is the recommended signer because keys can be created and rotated through the CloudFront API. A would work cryptographically but requires generating and distributing 40,000 signed URLs, and signed URLs change the URL, which the stem forbids. C restricts by country, which has no relationship to whether a particular subscriber has paid. D would require maintaining an IP allowlist for every subscriber's changing address, which is unmanageable and not what AWS WAF is for.

*Where this is covered: Protecting the content and the origin.*

</details>

### 5. Cutting the origin bill (Associate)

A company serves 80 TB per month of images from an Amazon S3 bucket directly to viewers over the internet. Finance wants to reduce the data transfer bill without changing the storage location or the object keys, and is willing to accept slightly higher latency for viewers in the most expensive geographies.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create a CloudFront distribution with the bucket as the origin and serve viewers through the distribution.
- **B)** Enable S3 Transfer Acceleration on the bucket and publish the acceleration endpoint to viewers.
- **C)** Set the distribution's price class to Price Class 100.
- **D)** Set the cache policy minimum TTL to 0 seconds so that CloudFront revalidates every request with S3.
- **E)** Enable S3 Requester Pays on the bucket so that viewers are charged for their own downloads.

<details><summary>Answer</summary>

**Answer: A and C.** Data transfer from an AWS origin such as S3 to CloudFront is always free, so moving delivery behind a distribution replaces S3 internet egress with CloudFront delivery charges and, because the images are cacheable, most requests never reach S3 at all. A price class excludes the most expensive edge locations; viewers in those geographies are still served from the nearest included location, which is the latency trade the stem accepts. B accelerates individual long-distance transfers, adds its own charge, and builds no reusable cache. D forces a revalidation request to the origin for every viewer request, which defeats the saving. E requires authenticated requesters and does not work for anonymous website viewers.

*Where this is covered: Edge functions, observability and the pricing shape.*

</details>

### 6. Origin protection across two accounts (Professional)

A platform team owns a perimeter account that holds every public CloudFront distribution. Content lives in Amazon S3 buckets inside separate workload accounts. Security requires that each bucket stay private, that it be readable only by the one distribution that serves it, and that objects encrypted with a customer managed KMS key remain readable. Auditors also want every distribution's access logs in a central log archive account.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Configure origin access control on each distribution, and in each workload account write a bucket policy allowing the `cloudfront.amazonaws.com` service principal with an `AWS:SourceArn` condition naming that distribution, plus a KMS key policy statement for the same principal.
- **B)** Create an origin access identity in the perimeter account and grant it `s3:GetObject` through a bucket ACL in each workload account.
- **C)** Make each bucket public and rely on an AWS WAF rule that blocks requests whose `User-Agent` is not CloudFront.
- **D)** Configure standard logging (v2) on each distribution with cross-account delivery to a bucket or log group in the log archive account.
- **E)** Copy log files nightly from each perimeter account bucket to the log archive account with a scheduled script.

<details><summary>Answer</summary>

**Answer: A and D.** Origin access control is an identity on the distribution, so the bucket policy in another account can name the distribution's ARN in an `AWS:SourceArn` condition, and SSE-KMS additionally requires a statement in the key policy for the CloudFront service principal; origin access identity supports neither SSE-KMS nor this pattern cleanly, which is why AWS recommends origin access control. D uses the cross-account delivery that standard logging v2 supports natively. B relies on a legacy mechanism that AWS no longer recommends and on bucket ACLs, which are disabled under the bucket owner enforced setting that origin access control requires. C leaves the buckets public and depends on a header any client can forge. E adds a custom job to do what the logging feature already does, which is the opposite of least operational overhead.

*Where this is covered: Professional depth.*

</details>

### 7. Regional failover for reads and writes (Professional)

An insurer serves policy documents and an upload API through one CloudFront distribution. Documents come from an Amazon S3 bucket replicated to a second Region; uploads go to an Application Load Balancer in the primary Region with a warm standby in the second. During a rehearsal, the team confirmed that document downloads survived the loss of the primary Region but that uploads returned errors for the whole exercise.

Which solution will meet these requirements?

- **A)** Add the upload origin to the same origin group as the document origins and add 500 and 504 to the failover status codes.
- **B)** Reduce the origin connection timeout to 1 second and the connection attempts to 1 on the upload origin.
- **C)** Enable Origin Shield in the standby Region so that upload requests are served from there during an outage.
- **D)** Keep the origin group for the document cache behavior and, for the upload cache behavior, point at a Route 53 failover record with health checks that resolves to the standby load balancer when the primary is unhealthy.

<details><summary>Answer</summary>

**Answer: D.** CloudFront origin failover applies only to `GET`, `HEAD` and `OPTIONS` requests, so an upload path using `POST` or `PUT` is never failed over by an origin group no matter how it is configured; moving that decision into DNS with a Route 53 failover record and health checks is the standard way to redirect a write path to a standby Region. A is precisely the configuration that does not work, for the reason above. B makes CloudFront give up on the primary faster but it still never retries a write against the secondary. C adds a caching layer in front of the origin and does not change which origin receives an uncacheable write.

*Where this is covered: Origins, origin access control and origin failover.*

</details>

### 8. A release that leaked private pages (Professional)

After a release, a company found that CloudFront had served a personalized account page belonging to one customer to several other customers. The origin sets `Cache-Control: private, no-store` on that page. The account page is served by the same cache behavior as the company's static assets, whose cache policy was recently given a minimum TTL of 3,600 seconds to improve the cache hit ratio. The company needs the leak stopped and the static assets to keep their high hit ratio.

Which solution will meet these requirements?

- **A)** Create a separate cache behavior for the account page path, above the existing one, attached to the `CachingDisabled` managed cache policy, and leave the assets behavior unchanged.
- **B)** Set the minimum TTL on the existing cache behavior to 0 and rely on the origin's `Cache-Control` headers for every path.
- **C)** Submit an invalidation for `/*` and add the `Authorization` header to the existing cache policy's cache key.
- **D)** Enable field-level encryption on the account page so that personal data is unreadable in the cache.

<details><summary>Answer</summary>

**Answer: A.** A minimum TTL greater than zero makes CloudFront cache a response for at least that long even when the origin sends `no-cache`, `no-store` or `private`, which is exactly the documented behavior that produced the leak. Splitting the account page into its own cache behavior ordered above the assets behavior, with caching disabled, removes the private page from the cache without touching the static asset settings the stem wants preserved. B stops the leak but also gives up the higher hit ratio on the assets, which the stem requires keeping. C clears the cache once and then caches a separate copy per `Authorization` value, which still stores private responses and still ignores `no-store` because the minimum TTL is unchanged. D encrypts named fields in a `POST` request body on the way to the origin and does nothing to responses returned to viewers.

*Where this is covered: Cache policies, origin request policies, the cache key and invalidation.*

</details>

## Summary

CloudFront is a series of decisions layered on one distribution. First, what the origin is and how it is protected: an S3 bucket kept private with origin access control, which AWS recommends over the legacy origin access identity; a load balancer or instance kept off the internet as a VPC origin; a pair of origins in an origin group for automatic read failover. Second, which cache behavior handles a request, decided by the first matching path pattern in an ordered list, with the default `*` behavior always last and the consequence that a permissive behavior above a restrictive one wins. Third, what goes into the cache key, controlled by a cache policy rather than the legacy forwarded values, with an origin request policy carrying what the origin wants but must not be keyed on. Fourth, who may view the content: signed URLs for one file, signed cookies for a set, a key group rather than a root-user key pair, geo restriction for whole countries and AWS WAF for anything finer. Finally the cost shape, where origin fetches from AWS services are free, the cache hit ratio is the real lever, and the price class trades latency for rate.

## Related units

- [Amazon S3](../01-storage/s3.md): the most common origin, and the owner of bucket policies, encryption and static website hosting
- [Amazon Route 53](route53.md): alias records that point a domain at a distribution, and the DNS against anycast decision
- [AWS Global Accelerator](global-accelerator.md): static anycast addresses when the protocol is not HTTP or clients need fixed IP addresses
- [AWS Lambda](../02-compute/lambda.md): the full CloudFront Functions against Lambda@Edge comparison and the Lambda@Edge restrictions
- [Amazon API Gateway](api-gateway.md): Regional endpoints fronted by your own distribution instead of a service-managed one
- [Elastic Load Balancing](../02-compute/elastic-load-balancing.md): the load balancer that sits behind most custom and VPC origins
- [AWS WAF, AWS Shield, AWS Firewall Manager and AWS Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md): web ACLs, rate-based rules and DDoS protection at the edge
- [Backup and disaster recovery](../01-storage/backup-and-disaster-recovery.md): where origin failover fits among the DR strategies

## Sources

- [What is Amazon CloudFront?](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html): edge locations, standard against multi-tenant distributions, and free data transfer from AWS origins
- [Origin settings](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesOrigin.html): origin protocol policy, origin path, custom headers, connection attempts and the timeout defaults
- [Restrict access to an Amazon S3 origin](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html): why AWS recommends OAC over OAI, the bucket policy, the SSE-KMS key policy and the website endpoint exclusion
- [Optimize high availability with CloudFront origin failover](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/high_availability_origin_failover.html): origin groups, the nine failover status codes and the GET, HEAD and OPTIONS restriction
- [Use Amazon CloudFront Origin Shield](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html): request collapsing, Region selection and when Origin Shield is a poor fit
- [Cache behavior settings](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesCacheBehavior.html): path pattern precedence, wildcards, normalization, allowed methods and the minimum, maximum and default TTL fields
- [Distribution settings](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistValuesGeneral.html): price class, alternate domain names, SNI against dedicated IP, security policies, HTTP/3 and the two standard logging options
- [Understand the cache key](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-the-cache-key.html): the default cache key and the separate OPTIONS entry
- [Control origin requests with a policy](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-origin-requests.html): how origin request policies and cache policies divide the work
- [Use managed cache policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html): CachingOptimized, CachingDisabled and their TTL settings
- [Manage how long content stays in the cache (expiration)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Expiration.html): the TTL and Cache-Control interaction table, and the stale-while-revalidate and stale-if-error directives
- [Invalidate files to remove content](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Invalidation.html): why AWS recommends versioned file names over invalidation
- [Pay for file invalidation](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/PayingForInvalidation.html): the 1,000 free paths per month per account and the wildcard and tag counting rules
- [Use signed URLs](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-signed-urls.html): the canned against custom policy comparison
- [Specify signers that can create signed URLs and signed cookies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-trusted-signers.html): trusted key groups against legacy AWS account signers, key limits and key formats
- [Restrict the geographic distribution of your content](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/georestrictions.html): country-level allowlists and denylists, the 403 response and the third-party service alternative
- [Use field-level encryption to help protect sensitive data](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/field-level-encryption.html): up to 10 POST fields, the RSA 2048 key pair and the chunked encoding requirement
- [Differences between CloudFront Functions and Lambda@Edge](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/edge-functions-choosing.html): the event types each supports and where each runs
- [How AWS Shield and Shield Advanced work](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-overview.html): Shield Standard included at no extra charge, and what Shield Advanced adds
- [Monitor CloudFront metrics with Amazon CloudWatch](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/viewing-cloudfront-metrics.html): the free default metrics and the additional metrics, including cache hit rate, that cost extra
- [Configure standard logging (v2)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/standard-logging.html): CloudWatch Logs, Firehose and S3 destinations, field selection and cross-account delivery
- [Use real-time access logs](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/real-time-logs.html): Kinesis Data Streams delivery, sampling rate and per-behavior scope
- [Access logs (standard logs)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/AccessLogs.html): best-effort delivery and the v2 against legacy split
- [Learn how continuous deployment works](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-continuous-deployment.html): weight-based and header-based routing to a staging distribution
- [AWS Firewall Manager](https://docs.aws.amazon.com/waf/latest/developerguide/fms-chapter.html): protecting all resources of a type, such as every CloudFront distribution in an organization, including newly added ones
- [Quotas](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cloudfront-limits.html): distributions, origins, cache behaviors, policies, key groups, VPC origins, invalidation rates and the per-distribution throughput ceilings
- [Amazon CloudFront pricing](https://aws.amazon.com/cloudfront/pricing/): the flat-rate plan tiers and the waiver of data transfer between AWS origins and CloudFront
- [Amazon CloudFront FAQs](https://aws.amazon.com/cloudfront/faqs/): price classes, regional edge caches, HTTP/3 over QUIC, VPC origins and the 1 TB and 10 million request free tier
- [DistributionConfig](https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_DistributionConfig.html): the PriceClass_100, PriceClass_200 and PriceClass_All values
