# Amazon API Gateway

**Where it sits on the exams.** **Amazon API Gateway** is the managed service that publishes, secures, throttles and monitors an HTTP or WebSocket front door for a backend, so that the backend never has to accept an internet connection, parse an authorization header, meter a customer, or absorb a traffic spike. It is the API layer the exams assume in every serverless and microservice design: SAA-C03 tasks 2.1 and 4.4, and SAP-C02 task 2.5, plus a supporting role wherever a question asks how a caching layer, an event-driven architecture, or a large-scale access pattern is fronted. The rule of thumb the exam wants is that API Gateway is where you put everything a client-facing API needs that is not business logic, and that the choice between its three API types is settled by which of those features the scenario actually names.

## What API Gateway is and how a request flows through it

API Gateway sits between clients and integration endpoints. An integration endpoint can be an **AWS Lambda** function, the service that runs code on demand with no server to manage, an HTTP endpoint anywhere on the internet, a private resource inside an **Amazon Virtual Private Cloud (Amazon VPC)**, the isolated virtual network in which your own resources run, or an AWS service API such as **Amazon DynamoDB**, the managed key-value and document database, or **Amazon Simple Queue Service (Amazon SQS)**, the managed message queue. API Gateway terminates TLS, authorizes the caller, meters and throttles the request, optionally transforms it, calls the backend, optionally transforms the response, and logs the whole thing. There is nothing to provision and nothing to scale.

A request passes through four stages, and knowing their names is how you read an exam question. The *method request*, called a *route* on the newer API types, is what the client sees: the path, the HTTP method, the parameters and the authorization setting. The *integration request* is what API Gateway sends to the backend, after any mapping. The *integration response* is what the backend returns. The *method response* is what the client receives, after any mapping back. With a proxy integration, the middle two stages are pass-throughs and the backend sees the raw request; with a non-proxy integration, you write the mappings yourself. Almost every configuration option in the service attaches to one of these four stages.

API Gateway builds three kinds of API, and the split is not cosmetic. A **REST API** is the original, feature-complete product, built from resources and methods, deployed through explicit deployments to stages. An **HTTP API** is the newer, deliberately smaller product, built from routes, aimed at proxying to Lambda or an HTTP endpoint at lower cost. A **WebSocket API** holds a persistent two-way connection so the backend can push messages to a connected client, which neither of the other types can do. The AWS documentation states the trade plainly: REST APIs support more features than HTTP APIs, and HTTP APIs are designed with minimal features so that they can be offered at a lower price.

Two properties are constant across all three. Every API is deployed to one or more stages, and the stage name appears in the invoke URL, so `https://a1b2c3d4e5.execute-api.us-east-2.amazonaws.com/prod` is API `a1b2c3d4e5` at stage `prod`. And throttling, metrics and logging are stage-level settings, not API-level ones, which is why "apply this to production but not to the test environment" is always a stage answer.

## Choosing between REST, HTTP and WebSocket APIs

This is the first decision in any API Gateway question, and AWS documents the feature split explicitly, so it is testable in detail rather than by feel. Several neighboring services appear by name in the rows below and are taught later in this unit: **AWS Identity and Access Management (IAM)**, the service that defines who may call what on AWS; **Amazon Cognito**, the managed user directory and sign-in service; **AWS WAF**, the web application firewall that allows, blocks or counts requests against rules you define; **AWS X-Ray**, the distributed tracing service that follows one request across the services it touches; and **AWS Cloud Map**, the service discovery registry that resolves a logical service name to healthy instances. Read the table by finding the feature the scenario names in the left column, then reading across to see which API types still offer it; the last two rows summarize what that costs and when each type is the right answer.

| Dimension | REST API | HTTP API | WebSocket API |
|---|---|---|---|
| Communication shape | Request and response over HTTPS | Request and response over HTTPS | Persistent two-way connection, backend can push to clients |
| Endpoint types | Edge-optimized, Regional, private | Regional only | Regional only |
| Authorization | IAM, resource policies, Amazon Cognito user pool authorizers, Lambda TOKEN and REQUEST authorizers | IAM, JWT authorizers including Cognito as the issuer, Lambda authorizers | IAM and Lambda REQUEST authorizers only |
| API keys, usage plans, per-client throttling | Yes | No | No |
| Request validation and request body transformation | Yes, with models and mapping templates | No; parameter mapping only, no body transformation | Mapping templates supported |
| Response caching | Yes, per stage and per method | No | No |
| AWS WAF integration | Yes | No | No |
| Canary release deployments | Yes | No, automatic deployments instead | No |
| Mock integrations and private integrations to AWS Cloud Map | Mock yes, Cloud Map no | Mock no, Cloud Map yes | Mock yes, Cloud Map no |
| Execution logs and AWS X-Ray tracing | Yes | No; access logs and metrics only | Execution logs yes, tracing no |
| Maximum integration timeout | 50 milliseconds to 29 seconds, raisable above 29 seconds for Regional and private APIs | 30 seconds, fixed | 50 milliseconds to 29 seconds, fixed |
| Latency posture | Full feature pipeline on every request | AWS names HTTP APIs for latency-sensitive workloads and workloads likely to grow very large | Connection is held open, so no per-request handshake |
| Cost shape | Tiered per million requests plus data transfer out, the highest per-request rate of the three | Tiered per million requests plus data transfer out, roughly a third of the REST per-request rate | Per million messages metered in 32 KB increments, plus per million connection-minutes |
| Correct when | The scenario names API keys, usage plans, per-client quotas, request validation, response caching, AWS WAF, canary releases, X-Ray, or a private endpoint | The scenario is a simple proxy to Lambda or an HTTP endpoint, wants OpenID Connect or OAuth 2.0 tokens, and asks for the lowest cost or lowest latency | The scenario says chat, live dashboard, notification push, collaborative editing, or "the server must send updates without the client polling" |

The exam plays this in one direction far more often than the other. A stem that says each partner must get its own request quota and rate limit rules out HTTP APIs, because API keys, usage plans and per-client throttling exist only on REST APIs. So does a requirement to cache responses at the API layer, to attach AWS WAF, or to expose a private endpoint. In the other direction, a stem describing a plain Lambda proxy with no management features and asking for the MOST cost-effective answer is pointing at an HTTP API, and choosing a REST API there pays several times as much per request for features nobody asked for.

WebSocket APIs are decided by the word "push". They route incoming JSON messages to backend integrations using a route selection expression evaluated against the message body, and they reserve three route keys: `$connect` when a client opens the connection, `$disconnect` when either side closes it, and `$default` when no custom route matches. The backend pushes messages back with the `@connections` management API, so a Lambda function holding a connection ID can send to that client at any time. The limits are firm: a connection lives at most 2 hours, closes after 10 minutes idle, frames cap at 32 KB and a message payload at 128 KB, and the default quota is 500 new connections per second per account per Region.

## Endpoint types, custom domain names, and TLS

The endpoint type is a property of a REST API and decides the hostname clients resolve. An **edge-optimized** endpoint publishes the API through a service-managed **Amazon CloudFront** distribution, the content delivery network that terminates connections at points of presence close to the viewer, so a request enters the AWS network at the nearest point of presence and travels to the API's Region over AWS's own backbone. AWS documents this as the default endpoint type for REST APIs and as the type that helps when clients are geographically distributed. Edge-optimized endpoints capitalize HTTP header names, because CloudFront normalizes them.

A **Regional** endpoint publishes the API directly in its Region with no distribution in front. AWS describes it as intended for clients in the same Region and for an API serving a small number of clients with high demand, where it reduces connection overhead, and Regional endpoints pass all header names through unchanged. The same page adds the point worth carrying into an exam: even when clients are geographically dispersed, it can still make sense to use a Regional endpoint together with your own CloudFront distribution, so that the API is not associated with a service-controlled distribution. That is the pattern behind most current designs, because a distribution you own carries its own certificate, cache policies, security policy and AWS WAF web ACL. A **private** endpoint is reachable only from inside a VPC and is covered in the next section. HTTP APIs and WebSocket APIs are Regional only.

The default invoke URL is the API ID plus `execute-api`, which is unmemorable and ties the URL to one API. A custom domain name replaces it, and maps a hostname plus a base path to a specific API and stage, so `https://api.example.com/orders` can point at one API's `prod` stage and `https://api.example.com/billing` at another's. A custom domain name must be unique within a Region across all AWS accounts, and you can migrate one between edge-optimized and Regional endpoints. The default endpoint can be disabled, after which calls to the `execute-api` hostname return `403 Forbidden`, which is how you force every client through the custom domain and its protections.

Certificates come from **AWS Certificate Manager (ACM)**, the service that provisions, stores and renews TLS certificates, and the Region rule is a reliable exam question. A Regional custom domain name needs its certificate in the same Region as the API; an edge-optimized one needs it in US East (N. Virginia), `us-east-1`, because CloudFront serves it. You then point DNS at the domain, normally with an alias record in **Amazon Route 53**, the AWS DNS and domain registration service; because the same Regional custom domain name can exist in several Regions, latency-based or failover routing across Regions is built on exactly that. Multi-level API mappings require a Regional custom domain name on the TLS 1.2 security policy.

Two client-authentication features round out the front door. Mutual TLS authentication requires the client to present a certificate that API Gateway validates against a truststore you host in **Amazon Simple Storage Service (Amazon S3)**, the object storage service, holding up to 1,000 certificates and 1 MB in total. It is configured on the custom domain name, works for both REST and HTTP APIs, and is the answer when devices or partners must authenticate with client certificates rather than a token. In the other direction, a REST API can present a client certificate to the backend, so the backend can verify that a request really came from your API; HTTP APIs cannot.

## Private APIs, resource policies, and interface endpoints

A private API is a REST API callable only from inside a VPC. It has no public hostname and no route from the internet, and AWS states that traffic to a private API never leaves the Amazon network. Only REST APIs support it: there is no private HTTP API and no private WebSocket API, and a private API cannot be converted to an edge-optimized one.

Reaching it takes two pieces that must both be present, and the exam tests the combination rather than either half. The first is an interface VPC endpoint for the `execute-api` service, an elastic network interface with a private address in your subnets, powered by **AWS PrivateLink**, the technology that presents a service inside a consumer VPC through private addresses. Because it is a network interface with a security group, anything that can route to that address can call the API, including peered VPCs, transit gateway attachments, a site-to-site VPN and **AWS Direct Connect**, the dedicated network link between a data center and AWS, so on-premises clients reach a private API over a hybrid connection with no internet path. Endpoints, private DNS and endpoint policies are taught in depth in [Amazon VPC](vpc.md); what matters here is that enabling private DNS makes the standard `execute-api` hostname resolve to the endpoint's private addresses, so callers need no special headers. AWS recommends turning private DNS on and using one endpoint for many private APIs. The cost is that the VPC can then no longer resolve the public `execute-api` names of public APIs, for which the documented workarounds are a custom domain name or a private hosted zone per API.

The second piece is a **resource policy**, a JSON policy document attached to the API itself that says which principals, source IP ranges, VPCs or VPC endpoints may invoke it. This is not optional for a private API: AWS documents that a newly created private API is inaccessible to all VPCs and cannot be deployed until a resource policy is attached. The policy should carry an `aws:SourceVpc` or `aws:SourceVpce` condition naming specific VPCs or endpoints rather than allowing all of them, and a VPC endpoint in any account can be granted access, which is how one team publishes an API that another account consumes privately.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": "execute-api:Invoke",
    "Resource": "arn:aws:execute-api:us-east-2:111122223333:a1b2c3d4e5/*",
    "Condition": { "StringEquals": { "aws:SourceVpce": "vpce-1a2b3c4d" } }
  }]
}
```

A VPC endpoint policy is the mirror control, attached to the endpoint rather than the API. The resource policy says which principals may reach this API; the endpoint policy says which APIs may be called through this endpoint, and it is evaluated first. AWS states the division directly: a private API needs a resource policy, but a custom endpoint policy is optional. Together they express a data perimeter, which is why a Professional scenario about proving an internal API is unreachable from outside an approved network is answered with both. Associating the VPC endpoint with the private API adds a Route 53 alias record, so the API is invoked like a public one without a `Host` override or an `x-apigw-api-id` header.

Private custom domain names extend the same model to friendly hostnames. Unlike public ones they need not be unique across accounts, so two accounts can each run `api.internal.example.com`, each identified by a domain name ARN carrying a domain name ID. A provider account creates and shares the name through API Gateway or **AWS Resource Access Manager (AWS RAM)**, the cross-account resource sharing service, and a consumer account creates a domain name access association between its VPC endpoint and that name. Two further constraints matter: private APIs support only TLS 1.2, and an HTTP/2 request is served as HTTP/1.1.

## Integration types, Lambda proxy compared with non-proxy, and VPC links

An integration is what API Gateway calls when a method or route matches, and REST APIs support five types. The `AWS_PROXY` type, universally called the **Lambda proxy integration**, hands the whole request to a Lambda function as a single JSON event carrying the path, method, headers, query string parameters, path parameters and body, and expects the function to return a JSON object containing `statusCode`, `headers` and `body`. Nothing is configured on the integration request or the integration response. AWS calls this the preferred way to call a Lambda function through API Gateway, because the contract lives in the function and the API does not have to be torn down when the backend changes. The price is that the function must build a correctly shaped response; a function returning a bare string produces a `502 Bad Gateway`, which is the classic troubleshooting question on this feature.

The `AWS` type is the non-proxy integration, also called the Lambda custom integration when the target is a function. Here you write an integration request mapping and an integration response mapping, so the function receives exactly the payload you compose and the client receives exactly the payload you compose back. The same type is what lets API Gateway call any AWS service action directly with no function at all: put a message on an SQS queue, write an item to a DynamoDB table, start an **AWS Step Functions** execution, where Step Functions is the managed workflow orchestrator, or put a record on a stream. That service proxy pattern is a recurring "LEAST operational overhead" answer, because it removes a Lambda function whose only job was to forward a request, and API Gateway signs the call with an IAM role you give it.

`HTTP` and `HTTP_PROXY` are the same pair for a backend reached over HTTP. `HTTP_PROXY` passes the request through untouched; `HTTP` lets you map. `MOCK` returns a response from API Gateway itself without calling any backend, which is how teams stub an endpoint another team has not built yet, and is also what the console generates behind the `OPTIONS` method when you enable cross-origin resource sharing on a non-proxy integration. HTTP APIs support the Lambda proxy, HTTP proxy and AWS service integrations but not mock integrations, and their Lambda integrations take a payload format version: `2.0` is the current shape, with lower-cased header names, a `cookies` array and no multi-value fields, while `1.0` matches the REST API event and is what you choose when a function must serve both.

A **VPC link** is how an API reaches a backend that has no public address. API Gateway creates and manages elastic network interfaces in your subnets, and the integration targets a load balancer or a registered service through them. There are two generations, and the current state is worth stating carefully because it changed. VPC links V2 are now supported for both HTTP APIs and REST APIs, are created with subnets and security groups, are immutable once created, and can target an **Application Load Balancer** or a **Network Load Balancer**, the Layer 7 and Layer 4 members of the **Elastic Load Balancing** family, and on HTTP APIs also a service registered in AWS Cloud Map, which is how a request reaches **Amazon Elastic Container Service (Amazon ECS)** tasks, the managed container orchestrator's units of work, by service name rather than by address. VPC links V1 are the legacy REST-only form that required a Network Load Balancer, and AWS now labels them legacy and recommends not creating new ones.

Three operational details follow VPC links into questions. Every resource in the path, the load balancer or Cloud Map service, the link and the API, must be owned by the same account. Private integration traffic uses HTTP by default, so TLS to the backend means specifying a secure server name. And API Gateway includes the stage name in the path it sends to the backend, so a call to the `test` stage arrives as `test/orders` unless you override the path with parameter mapping. A V2 link that carries no traffic for 60 days goes inactive and its network interfaces are deleted, so the first request after the gap fails while the link is reprovisioned.

## Mapping, validation, and cross-origin resource sharing

Non-proxy integrations exist for the cases where the client contract and the backend contract are not the same. Parameter mapping changes path parameters, query string parameters and header values without scripting; it works in the integration request for both proxy and non-proxy integrations, but mapping an integration *response* requires a non-proxy integration. A **mapping template** goes further: a script in Velocity Template Language applied to the body according to the `Content-Type` header, capped at 300 KB, and it is how a REST API reshapes a client's JSON into the exact payload a DynamoDB `PutItem` call or a legacy backend expects, and reshapes the answer back. HTTP APIs support parameter mapping only: they can append, overwrite or remove headers and query strings and overwrite the path, but cannot transform a request body at all, which is one concrete requirement that forces a REST API.

Request validation is the other REST-only feature in this area and is a cheap way to protect a backend. You define a model, a JSON Schema document describing the expected body, attach a request validator to a method, and API Gateway rejects a request that omits a required query string parameter or header, or whose body does not match the schema, returning `400` and logging the result without ever calling the integration. AWS is explicit that this reduces unnecessary calls to the backend, and the exam uses that framing: "reduce invocations caused by malformed requests with the least code" is request validation, not a check inside the Lambda function. The two halves differ in strength: parameter validation checks only that required query string parameters and headers are present and non-blank, while body validation applies the full JSON Schema, including types and formats.

Cross-origin resource sharing is a browser rule, not a security control, and it decides whether a script served from one origin may read a response from another. For a non-simple request the browser first sends an `OPTIONS` preflight that the API must answer with `Access-Control-Allow-Origin`, `Access-Control-Allow-Headers` and `Access-Control-Allow-Methods`. On a REST API with a non-proxy integration the console builds that preflight as a mock integration; on a proxy integration API Gateway cannot compose it, so the function must return the headers on every response. HTTP APIs have CORS as a configuration object on the API, which removes the problem entirely.

## Authorizers, IAM authorization, and AWS WAF

Authorization is set per method on a REST API and per route on an HTTP API, and the choice of mechanism is one of the two or three things an API Gateway question is most likely to turn on. Read this table by starting from what the scenario says the caller already has, a signed AWS request, a user pool token, a third-party token, or something stranger, and take the row that matches.

| Authorizer type | API types | What the client presents | How the decision is made | Result caching | Correct when |
|---|---|---|---|---|---|
| IAM authorization | REST, HTTP, WebSocket | A request signed with AWS credentials using Signature Version 4 | API Gateway checks the caller's `execute-api:Invoke` permission on the method or route, combined with any resource policy | None | The callers are AWS principals: other services, other accounts, instances or containers carrying roles, or a cross-account internal API |
| Resource policy | REST only | Nothing extra; the policy inspects the request's source | A JSON policy on the API allows or denies by account, source IP range, VPC or VPC endpoint, evaluated before and alongside the authorizer | None | Restricting an API to named IP ranges, VPCs or VPC endpoints, and mandatory for every private API |
| Amazon Cognito user pool authorizer | REST only | A user pool identity token or access token, normally in the `Authorization` header | API Gateway validates the token against the configured user pool and passes the claims to the integration | Configurable, 300 seconds by default and 3600 maximum | End users sign in to a Cognito user pool and the API should not carry any custom authorization code |
| JWT authorizer | HTTP only | A JSON Web Token from an OpenID Connect or OAuth 2.0 provider | API Gateway fetches the issuer's public key from its `jwks_uri`, checks the signature, then the `kid`, `iss`, `aud` or `client_id`, `exp`, `nbf` and `iat` claims, and any scopes required on the route | The issuer's public key is cached for up to two hours | An HTTP API is fronted by any standards-compliant identity provider, Cognito included, and you want scope-based authorization with no code |
| Lambda TOKEN authorizer | REST, WebSocket via REQUEST only | A bearer token in one named header | A Lambda function receives the token, returns a principal identifier and an IAM policy document that API Gateway evaluates | Default 300 seconds, maximum 3600, keyed on the token header | A bearer token must be validated by custom logic, for example against a third-party OAuth or SAML provider |
| Lambda REQUEST authorizer | REST, HTTP, WebSocket | Any combination of headers, query string parameters, stage variables and context values | The same function contract, but the function sees the whole request context, so policies can depend on path, method or source | Default 300 seconds, maximum 3600, keyed on all named identity sources in order | Authorization depends on more than one input, which is why AWS recommends REQUEST over TOKEN |

Three behaviors in that table decide questions on their own. A Lambda authorizer returns an IAM policy document rather than a yes or no, so one authorizer can allow a caller for `GET /orders` and deny the same caller for `DELETE /orders`. Authorizer caching is the difference between one Lambda invocation per request and one per cache period per identity, so "reduce the cost and latency of authorization" maps to raising the authorizer result time to live, and the trade is that a revoked token stays valid until the entry expires. And only REST APIs have resource policies; the HTTP API documentation states that resource policies are not currently supported, so restricting an API to a CIDR range without writing code is a REST API requirement.

IAM authorization is the one that is easy to underrate. Setting a method's authorization type to `AWS_IAM` means the caller must sign the request with Signature Version 4, and API Gateway invokes the method only if the principal has `execute-api:Invoke` on the resource ARN. That is the right answer whenever the caller is itself an AWS workload, because it needs no token store, no identity provider and no rotation, and it composes with a resource policy: on a private API you can require both an allowed VPC endpoint and an allowed IAM principal. The resource ARN carries the method, so a policy can be as fine-grained as one HTTP method on one path.

AWS WAF attaches to a REST API stage as a Regional web ACL and is evaluated before every other access control on the API. AWS states the precedence explicitly: if AWS WAF blocks a CIDR block that a resource policy allows, AWS WAF wins and the resource policy is never evaluated. It brings rate-based rules that count requests per client IP over a rolling five-minute window, managed rule groups for SQL injection and cross-site scripting, geographic match rules, and body inspection limited to the first 64 KB. AWS WAF is not available for HTTP APIs, so protecting one from a Layer 7 attack means putting CloudFront with a web ACL in front of it. And a rate-based rule is the answer for "block an abusive client", where a usage plan is the answer for "give a paying customer a quota". Rules, managed rule groups and DDoS protection are taught in [AWS WAF, AWS Shield, AWS Firewall Manager and AWS Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md), and user pools, identity pools and token types in [Amazon Cognito](../07-security/cognito.md).

## Usage plans, API keys, and choosing a throttling strategy

A **usage plan** names the API stages and methods a group of clients may call, the rate and burst at which they may call them, and an optional quota, a maximum number of requests over a day, week or month. Clients are identified by an **API key**, an alphanumeric string of 20 to 128 characters that the client sends in the `X-API-Key` header, or that a Lambda authorizer returns as part of its response when the API's key source is set to `AUTHORIZER`. A key can belong to several usage plans and a plan can cover several stages, but a given key can map to only one plan per stage. This whole mechanism exists only on REST APIs.

What usage plans and API keys do is meter and differentiate customers: a free tier at 10 requests per second with a 10,000 request daily quota, a paid tier at 200 requests per second, each partner's consumption visible per key. What they do not do is secure anything, and AWS says so twice. API keys must not be used for authentication or authorization, because a caller with a valid key for one API in a usage plan can call every API in that plan, and because clients send keys in headers that get logged. Usage plan throttling and quotas are best-effort rather than hard limits, so clients can exceed them, and AWS states you should not rely on them to control costs or block access; **AWS Budgets**, the cost monitoring and alerting service, is named for cost control and AWS WAF for blocking. The keyed answer to "how do you secure this API" is therefore always an IAM role, a Lambda authorizer or a Cognito user pool, with the API key alongside for metering.

Throttling itself applies at four levels, and API Gateway evaluates them in a fixed order, from most specific to least. Per-client and per-method limits set for a stage inside a usage plan are checked first. Per-method limits set directly on a stage are checked next. The account-level limit for the Region comes third. AWS's own Regional limits are last and are not visible to customers. Every level uses a token bucket, where the rate is how fast tokens refill and the burst is the bucket's capacity, so burst is the number of concurrent submissions that can be absorbed before requests are rejected with `429 Too Many Requests`. The account default is 10,000 requests per second per Region across HTTP, REST, WebSocket and WebSocket callback APIs, with a burst bucket capacity of 5,000; in thirteen newer Regions the defaults are 2,500 requests per second and a burst of 1,250. The rate is adjustable on request, and AWS notes that higher limits are easier to obtain for APIs with shorter timeouts and smaller payloads. The burst quota is set by the service team from the rate and cannot be requested directly. HTTP APIs have the same account level plus route-level throttling on a stage, and no usage plan layer at all.

Choosing a throttling strategy, which SAA-C03 task 4.4 names directly, is a matter of matching the level to the reason for throttling. If the concern is one expensive operation swamping a shared backend, set a method-level or route-level limit on that method only, leaving the rest of the API at the stage default. If the concern is protecting the whole backend, set stage-level limits below what the backend can survive, and remember that a limit above the account level is meaningless. If the concern is fairness or monetization between named consumers, that is a usage plan with per-key rate, burst and quota, and it is the only level that can tell two callers apart. If the concern is an unauthenticated flood or an abusive source, throttling is the wrong tool and an AWS WAF rate-based rule is the right one. And whichever level you use, throttling protects the backend by shedding load at the edge: the request that returns `429` never reaches the integration, never invokes a Lambda function, and never consumes a database connection, which is why "protect the downstream relational database from traffic spikes without changing the application" is an API Gateway throttling answer as often as it is a queue answer.

## Stages, deployments, canary releases, and caching

A **deployment** is a snapshot of a REST API's configuration, and a **stage** is a named pointer to one deployment. Nothing a client calls changes until you create a new deployment and associate it with a stage, and AWS is specific that every change to routes, methods, integrations, authorizers or resource policies requires a redeploy, while stage settings take effect on their own. HTTP APIs invert this with automatic deployments on the `$default` stage, which is convenient for a simple proxy and is exactly the control a regulated change process does not want. **Stage variables** are name-value pairs available to mapping templates and to integration configuration, so one API definition can point at a development Lambda alias in the `dev` stage and a production alias in `prod`, or at different VPC link identifiers, without any code change. The default quota is 10 stages per API and 100 stage variables per stage.

A **canary release deployment** puts a new deployment on the same stage as the current one and sends it a chosen percentage of traffic, between 0.0 and 100.0, selected at random per request. Canary settings can override stage variables, so the canary can point at a new backend version while production keeps the old one, and can be told whether to use the stage cache. Execution and access logs go to a separate log group ending in `/Canary`, which is how you compare error rates and latency before promoting. Promotion makes the canary deployment the stage's deployment; discarding it just removes the settings. This is the API Gateway answer to "deploy to a small share of live traffic and roll back quickly", and it is REST-only.

Caching is provisioned per stage on a REST API by choosing a dedicated cache size from 0.5, 1.6, 6.1, 13.5, 28.4, 58.2, 118 or 237 GB. Creating or deleting a cache takes about four minutes, and changing the size destroys and rebuilds it, so every entry is lost. The default time to live is 300 seconds and the maximum is 3600; a time to live of 0 disables caching, and the largest cacheable response is 1,048,576 bytes. Two behaviors matter more than the numbers. Only `GET` methods are cached when you turn on the stage's default method-level caching, and AWS recommends leaving it that way; caching other methods requires a deliberate per-method override. And cache keys are built from the method or integration parameters you nominate, so `GET /users?type=admin` and `GET /users?type=regular` share one entry unless `type` is part of the key, which is the quiet cause of one customer seeing another's data. Invalidation is open by default: unless you attach a policy requiring `execute-api:InvalidateCache`, any client can flush an entry by sending `Cache-Control: max-age=0`. Caching is billed hourly by size, is not free-tier eligible, and HTTP APIs have no cache at all, so an HTTP API that needs caching needs CloudFront in front of it or an application-side cache such as **Amazon ElastiCache**, the managed in-memory caching service.

## Monitoring, pricing shape, and the quotas that bite

**Amazon CloudWatch**, the AWS metrics, logs and alarms service, receives API Gateway metric data every minute in the `AWS/ApiGateway` namespace. Seven metrics carry almost all the diagnostic value. `Count` is request volume. `4XXError` and `5XXError` separate client faults from server faults, and their `Average` statistic gives an error rate rather than a count. `CacheHitCount` and `CacheMissCount` size the cache. The pair that decides troubleshooting questions is `IntegrationLatency`, the time between API Gateway relaying the request to the backend and receiving the response, and `Latency`, the whole time from receiving the client's request to returning a response, which includes integration latency plus API Gateway's own overhead. A rising `Latency` with a flat `IntegrationLatency` points at the API layer, most often at an uncached Lambda authorizer; the two rising together point at the backend. By default these metrics are aggregated by API name and stage, and per-method metrics require enabling detailed metrics on the stage, which costs extra.

Logging comes in two kinds on a REST API. Execution logs record what API Gateway did internally with each request, at an `ERROR` or `INFO` level set per stage or per method, and are the only place you see why a mapping template failed or an authorizer denied a call. Access logs are a per-request line whose format you define from `$context` variables, delivered to CloudWatch Logs or to **Amazon Data Firehose**, formerly Kinesis Data Firehose, the managed streaming delivery service. HTTP APIs have access logs and metrics but no execution logs. AWS X-Ray traces requests end to end for REST APIs on every endpoint type, including private, but is not available for HTTP APIs.

Pricing follows the API type. REST APIs bill per million requests on a tiered, descending scale plus data transfer out; private REST APIs use the same request pricing and carry no data transfer out charge, but their interface endpoints are billed by PrivateLink. HTTP APIs bill the same way at roughly a third of the REST per-request rate, which is why an HTTP API is the default cost answer for a plain proxy. WebSocket APIs bill on two dimensions at once, messages metered in 32 KB increments and connection-minutes, so an application with many idle connections pays mostly for time. Caching is billed hourly for the size you provision whether or not it is used, and is not free-tier eligible.

The quotas worth carrying into an exam are the ones that shape a design. The integration timeout for REST APIs runs from 50 milliseconds to 29 seconds, and this is the number that changed: for Regional and private APIs it can now be raised above 29 seconds through **Service Quotas**, the service that shows and raises AWS quotas, though AWS warns that doing so might require reducing the Region-level throttle quota for the account, while edge-optimized APIs remain fixed at 29 seconds. HTTP APIs cap at 30 seconds and WebSocket APIs at 29 seconds, neither increasable. Any operation that cannot finish inside that ceiling belongs off the synchronous path: return `202 Accepted` with a job identifier, do the work behind a queue, and let the client poll a second method for the result. Payload size is 10 MB for both REST and HTTP APIs, so large uploads belong in S3 through a presigned URL. Other defaults that bind are 300 resources or routes per API, 10 stages per API, 10 authorizers per API, 10,000 API keys and 300 usage plans per account per Region, 10 usage plans per API key, 20 method-level throttle settings per stage in a usage plan, 8,192 characters of resource policy, and a 20,480 byte total header size that drops to 8,000 bytes on a private API.

## Professional depth

At organization scale the API layer is usually split across accounts, and the seams are where Professional questions live. A common shape puts each API in its workload account and centralizes only what has to be shared: private custom domain names in a provider account shared through AWS RAM, one `execute-api` interface endpoint per consumer VPC serving many private APIs, and AWS WAF web ACLs managed from one place. Cross-account invocation has three forms that are not interchangeable: IAM authorization with a role assumed from the calling account, a resource policy naming the other account or its VPC endpoint, and a Cognito authorizer whose user pool lives elsewhere. Only the first two work without a token, which is why service-to-service traffic between accounts is almost always IAM plus a resource policy.

Multi-Region designs use a Regional endpoint in each Region, the same custom domain name in both, and Route 53 latency-based or failover routing across them with health checks, because an edge-optimized endpoint pins the API to the Region that owns its distribution. The subtleties are that ACM certificates must exist in each Region, that a canary release is per stage and therefore per Region, and that usage plan quotas are per Region, so a customer with a monthly quota effectively gets that quota twice across two Regions unless the counting moves somewhere else.

Quotas bite hardest during a migration. The account-level 10,000 requests per second is shared across every API type in the Region, so a new high-volume API can throttle an existing one that was never touched; stage-level limits on each API are how you partition the account budget deliberately rather than by accident. Raising the account rate is possible, and AWS notes it is easier for APIs with short timeouts and small payloads, which is one practical reason not to raise integration timeouts past 29 seconds casually: the trade is explicitly documented as possibly requiring a reduced Region-level throttle quota.

Failure modes cluster in a few places. A Lambda authorizer with caching off becomes the most-invoked function in the account and the largest contributor to latency. A VPC link that has carried no traffic for 60 days goes inactive and the first request after the gap fails. A cache key that omits a tenant identifier serves one customer's response to another. A private API deployed without a resource policy cannot be deployed at all, and one whose VPC has private DNS enabled loses the ability to resolve public `execute-api` names. And a 29-second ceiling turns any long backend operation into a `504`, which is the architectural signal to return `202 Accepted` with a job identifier and do the work asynchronously behind SQS or Step Functions.

> **Professional depth.** A question that offers both a REST API and an HTTP API usually hides the discriminator in one clause. "Per-customer quotas", "request validation", "response caching", "AWS WAF", "canary deployment", "X-Ray" or "private endpoint" each force a REST API on their own. "Lowest cost", "lowest latency", "simple proxy to Lambda", "OpenID Connect" or "very large scale" with no management feature named favors an HTTP API. When both appear, the management requirement wins, because an HTTP API cannot be made to do it.

## Worked scenario

A logistics company exposes a shipment tracking API to 400 carrier partners and to its own mobile app. Partners are on contracts with different rate limits and monthly call allowances. The mobile app signs users in through a Cognito user pool. An internal reconciliation service in a separate AWS account calls the same backend and must never traverse the internet. Tracking responses change at most once a minute, the backend is a set of ECS tasks behind an Application Load Balancer in private subnets, and one report endpoint takes up to 45 seconds to build.

The public API is a REST API with a Regional endpoint behind the custom domain name `api.example.com`, with an ACM certificate in the same Region, a Route 53 alias record, and the company's own CloudFront distribution in front carrying an AWS WAF web ACL with managed rule groups and a rate-based rule. The default `execute-api` endpoint is disabled so nothing bypasses that path. Partner methods require an API key and belong to one usage plan per contract tier, each with its own rate, burst and monthly quota, while a Lambda REQUEST authorizer with a 300-second result cache validates the partner's token and returns a policy scoped to the paths that partner bought. Mobile app methods use a Cognito user pool authorizer instead. The backend is reached through a VPC link V2 to the Application Load Balancer, so no ECS task has a public address, and stage caching is provisioned at 1.6 GB with a 60-second time to live on the `GET` tracking method only, with the carrier identifier in the cache key.

The internal account calls a second, private REST API in the same account as the backend. Its resource policy allows `execute-api:Invoke` only when `aws:SourceVpce` matches the reconciliation account's interface endpoint, the methods use IAM authorization so the calling role is checked as well, and an endpoint policy on the consumer side limits that endpoint to this one API. The 45-second report endpoint fits no integration timeout an edge-optimized API allows, so it is restructured: the method integrates directly with SQS, returns `202 Accepted` with a job identifier, and the client polls a second endpoint for the result. Releases go out as canary deployments at 10 percent for an hour.

The exam asks this scenario two ways. The Associate version asks how to give each partner its own rate limit and monthly allowance with the least operational overhead, and the keyed answer is API keys with per-tier usage plans on a REST API, not a custom counter and not an HTTP API. The Professional version asks how the internal account should call the API without internet exposure, and the keyed answer is a private API with an interface endpoint, a resource policy conditioned on `aws:SourceVpce`, and IAM authorization on the methods, not a public API restricted by source IP.

## Exam lens

- "Each customer needs its own rate limit and monthly quota" maps to API keys with usage plans on a REST API; an HTTP API is the distractor because it has neither.
- "Secure the API" never maps to API keys; AWS states they are not an authentication or authorization mechanism, so the answer is IAM, a Lambda authorizer or a Cognito user pool authorizer.
- "Simple proxy to a Lambda function at the lowest cost" maps to an HTTP API; a REST API is the distractor that pays several times the per-request rate for unused features.
- "Users sign in to a Cognito user pool" maps to a Cognito user pool authorizer on a REST API, or a JWT authorizer on an HTTP API.
- "Validate a third-party token or apply custom logic" maps to a Lambda authorizer, using REQUEST when more than one input decides the outcome.
- "Reduce the number of authorizer invocations" maps to raising the authorizer result time to live, default 300 seconds and maximum 3600.
- "Another AWS service or account calls the API" maps to IAM authorization with Signature Version 4, optionally with a resource policy.
- "Only callers inside our network may reach the API" maps to a private REST API with an interface VPC endpoint plus a resource policy conditioned on `aws:SourceVpce`; a security group alone is the distractor, because it does not authorize the API call.
- "Restrict the API to specific IP ranges without writing code" maps to a resource policy on a REST API; HTTP APIs do not support resource policies.
- "Block SQL injection, bad bots or an abusive client IP" maps to an AWS WAF web ACL on the REST API stage, evaluated before resource policies and authorizers.
- "Reduce backend calls for repeated identical reads" maps to stage caching with the varying parameter in the cache key; an HTTP API is the distractor, because it cannot cache.
- "Reject malformed requests before they reach the function" maps to request validation with a model on a REST API, not a check inside the function.
- "The backend is in private subnets with no public address" maps to a VPC link V2 to an Application Load Balancer or Network Load Balancer; VPC link V1 is the legacy NLB-only form.
- "Push updates to connected clients without polling" maps to a WebSocket API with the `@connections` API; long polling on a REST API is the distractor.
- "Send a small share of live traffic to a new version and roll back fast" maps to a canary release deployment, which is REST-only.
- "The backend takes longer than 30 seconds" maps to returning `202 Accepted` with a job identifier; raising the integration timeout past 29 seconds is possible only on Regional and private REST APIs and may cost Region-level throttle quota.
- "Latency rose but the backend is unchanged" maps to `Latency` climbing while `IntegrationLatency` stays flat, which points at the API layer, most often an uncached authorizer.

## Knowledge check

### 1. Selling an API to partners on tiered contracts (Associate)

A company publishes a product catalog API to 200 retail partners. Each partner signs one of three contracts that differ in requests per second and in the number of calls allowed per month, and the company must be able to see how many calls each partner made. Partners already authenticate with bearer tokens that a custom function validates. The company wants to meter and limit partners without writing any metering code.

Which solution will meet these requirements?

- **A)** Build the API as a REST API, issue each partner an API key, and place the keys in three usage plans with per-tier rate, burst and quota settings.
- **B)** Build the API as an HTTP API and configure route-level throttling for each partner.
- **C)** Build the API as a REST API and have the Lambda authorizer count each partner's calls in an Amazon DynamoDB table, rejecting calls above the contract limit.
- **D)** Build the API as an HTTP API and attach an AWS WAF rate-based rule per partner.

<details><summary>Answer</summary>

**Answer: A.** Usage plans are the only feature that applies a rate, a burst and a periodic quota per identified client, and API keys are how API Gateway identifies that client; usage data per key is reported without any code. B fails because HTTP APIs support neither API keys nor per-client throttling, and route-level throttling applies to every caller of the route, not to one partner. C is a custom build of something AWS already manages and adds a read and a write to the hot path of every request. D fails twice: AWS WAF is not available for HTTP APIs, and a rate-based rule counts per client IP address rather than per partner identity, so it cannot express a monthly call allowance.

*Where this is covered: Usage plans, API keys, and choosing a throttling strategy.*

</details>

### 2. Fronting a function at the lowest cost (Associate)

A startup exposes a single Lambda function as a public JSON API. There is no need for per-client quotas, response caching, request validation, or a web application firewall. Clients present tokens issued by a standards-compliant OpenID Connect provider. Traffic is expected to grow to several billion requests a month and the team wants the lowest possible per-request cost.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Create a REST API with a Lambda proxy integration and an Amazon Cognito user pool authorizer.
- **B)** Create a REST API with a Lambda proxy integration and a Lambda TOKEN authorizer that validates the token.
- **C)** Create an HTTP API with a Lambda proxy integration and a JWT authorizer configured with the provider as issuer.
- **D)** Create a WebSocket API with a Lambda integration on the `$default` route.

<details><summary>Answer</summary>

**Answer: C.** An HTTP API bills at roughly a third of the REST API per-request rate, its built-in JWT authorizer validates tokens from any OpenID Connect or OAuth 2.0 provider with no code, and AWS names HTTP APIs as the choice for latency-sensitive workloads and for workloads likely to grow very large. A and B both use a REST API whose extra features the stem explicitly does not need, and B additionally adds a Lambda invocation on the authorization path. D is the wrong communication model: the clients make ordinary request and response calls, and a WebSocket API bills for connection-minutes as well as messages.

*Where this is covered: Choosing between REST, HTTP and WebSocket APIs.*

</details>

### 3. Letting one account call another account's internal API (Professional)

A bank runs a settlement API in a services account. A reporting workload in a separate account must call it. Auditors require that the call never traverse the public internet and that the design can prove which network path and which identity are permitted. Both accounts belong to the same company and run in the same Region.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create a Regional REST API in the services account and attach a resource policy that allows the reporting account's AWS account ID.
- **B)** Create a private REST API in the services account and attach a resource policy that allows `execute-api:Invoke` only when `aws:SourceVpce` equals the reporting account's interface VPC endpoint ID.
- **C)** Create an HTTP API in the services account and attach a resource policy scoped to the reporting account's VPC.
- **D)** Create an interface VPC endpoint for `execute-api` in the reporting account's VPC, enable private DNS, and set the settlement API's methods to IAM authorization so the calling role is checked.
- **E)** Place the settlement API behind a public custom domain name and restrict access with an AWS WAF IP set containing the reporting account's NAT gateway addresses.

<details><summary>Answer</summary>

**Answer: B and D.** A private REST API has no public hostname, and its resource policy conditioned on `aws:SourceVpce` names the exact network path; the interface endpoint in the consumer VPC is the other half of that path, and IAM authorization on the methods adds the identity check the auditors want, so both the network and the principal are provable. A leaves the API on a Regional public endpoint reachable from the internet, which the stem forbids. C is not possible, because HTTP APIs do not support resource policies and cannot be private. E routes the call over the internet to reach the public endpoint and controls it only by source address, which is neither private nor an identity control.

*Where this is covered: Private APIs, resource policies, and interface endpoints.*

</details>

### 4. Cutting repeated reads to a relational backend (Associate)

A news site exposes an article API through an API Gateway REST API backed by a relational database. The same few hundred article identifiers are requested thousands of times a minute, article content changes at most once every few minutes, and the database is close to its connection limit. The team wants to cut database load without changing the application or the database.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Move the API to an HTTP API and enable its response cache.
- **B)** Add a read replica to the database and point the API at it.
- **C)** Add an ElastiCache cluster and change the application to read from it first.
- **D)** Enable stage caching on the REST API, set a time to live of 120 seconds on the `GET` article method, and include the article identifier in the cache key.

<details><summary>Answer</summary>

**Answer: D.** API Gateway stage caching serves repeat reads without reaching the backend at all, is a stage setting rather than a code change, and including the article identifier in the cache key keeps each article's response separate. A is not possible: HTTP APIs have no response cache. B spreads reads across another instance but still serves every request from the database, so the repeated identical reads remain and the site gains a replica to operate. C would work but requires changing the application, which the stem rules out, and it adds a cluster to operate.

*Where this is covered: Stages, deployments, canary releases, and caching.*

</details>

### 5. Reaching containers that have no public address (Associate)

A company runs a containerized service on Amazon ECS tasks behind an Application Load Balancer in private subnets. It wants to expose a subset of the service's paths as a public API through API Gateway. No task and no load balancer may have a public address.

Which solution will meet these requirements?

- **A)** Create an HTTP proxy integration whose URI is the load balancer's DNS name and add a NAT gateway to the private subnets.
- **B)** Create a VPC link V2 in the subnets holding the load balancer and create an HTTP proxy integration that targets the Application Load Balancer through that link.
- **C)** Create a VPC link V1 and target the Application Load Balancer through it.
- **D)** Create an interface VPC endpoint for `execute-api` and route API Gateway traffic to the load balancer through it.

<details><summary>Answer</summary>

**Answer: B.** A VPC link V2 places API Gateway-managed network interfaces in your subnets and lets a private integration target an Application Load Balancer directly, which is exactly the path this design needs and keeps every address private. A requires an internet-facing load balancer for API Gateway to resolve and reach, and a NAT gateway provides outbound access from the VPC rather than inbound access into it. C is not possible: VPC links V1 are the legacy form and support only a Network Load Balancer. D inverts the direction; an `execute-api` interface endpoint lets clients inside a VPC call API Gateway, not the other way round.

*Where this is covered: Integration types, Lambda proxy compared with non-proxy, and VPC links.*

</details>

### 6. An operation that outlives the integration timeout (Associate)

A REST API with an edge-optimized endpoint exposes a report endpoint whose backend takes between 40 and 90 seconds to complete. Clients currently receive `504 Gateway Timeout` errors. The company wants clients to get a successful response immediately and to collect the report when it is ready, without abandoning API Gateway.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Request a quota increase to raise the integration timeout above 29 seconds for the edge-optimized API.
- **B)** Change the report method to an AWS service integration that places a job message on an Amazon SQS queue and returns `202 Accepted` with a job identifier.
- **C)** Enable stage caching on the report method with a 3600 second time to live.
- **D)** Increase the Lambda function timeout to 15 minutes.
- **E)** Add a second method that returns the finished report, and have the client poll it with the job identifier.

<details><summary>Answer</summary>

**Answer: B and E.** Decoupling the request from the work is the only design that fits inside any API Gateway integration timeout: the first call enqueues and returns immediately, and a second call retrieves the result. A is not possible, because the documented increase above 29 seconds applies to Regional and private REST APIs only, never to edge-optimized ones, and it would also risk a reduction in the account's Region-level throttle quota. C caches a response that does not exist yet and does nothing for the first caller. D changes how long the backend may run but not how long API Gateway will wait, so the `504` is unchanged.

*Where this is covered: Monitoring, pricing shape, and the quotas that bite.*

</details>

### 7. Pushing live updates to a dashboard (Associate)

A logistics operator shows vehicle positions on a browser dashboard. Positions arrive from vehicles every few seconds and every open dashboard must see an update within a second of arrival. The current design has each browser poll a REST API once per second, which costs far more than expected and still lags. The team wants the server to send updates as they arrive.

Which solution will meet these requirements?

- **A)** Replace the polling API with a WebSocket API, store each connection ID on `$connect`, and have the backend push updates with the `@connections` API.
- **B)** Keep the REST API and enable stage caching with a one second time to live.
- **C)** Keep the REST API and raise the account-level throttle quota so polling is never rejected.
- **D)** Replace the REST API with an HTTP API and enable automatic deployments.

<details><summary>Answer</summary>

**Answer: A.** A WebSocket API holds a persistent two-way connection, so the backend pushes each update to the connection IDs it recorded on the `$connect` route and no client polls at all. B caches responses but still requires one request per second per browser, so neither the cost nor the lag changes. C removes a symptom of the polling design while keeping the request volume that caused it. D changes the API type and the deployment model but leaves the communication pattern as request and response, which cannot push.

*Where this is covered: Choosing between REST, HTTP and WebSocket APIs.*

</details>

### 8. Releasing a new version to a small share of traffic (Associate)

A payments team must release a new version of an API method to 5 percent of live traffic on the production stage, compare its error rate and latency against the current version in separate logs, and be able to revert within seconds if the new version misbehaves. Clients must keep calling the same URL throughout.

Which solution will meet these requirements?

- **A)** Deploy the new version to a second stage and ask clients to switch to the new stage URL for testing.
- **B)** Create a second API, put both behind Amazon Route 53 weighted records, and set the new API's weight to 5.
- **C)** Deploy the new version to the production stage and roll back by redeploying the previous deployment if errors rise.
- **D)** Create a canary release deployment on the production stage with a traffic percentage of 5.0 and stage variable overrides pointing at the new backend version.

<details><summary>Answer</summary>

**Answer: D.** A canary release splits traffic on the same stage at a percentage you choose, overrides stage variables so the canary reaches a different backend, writes its execution and access logs to a separate log group ending in `/Canary`, and is disabled or promoted in one call. A changes the URL, which the stem forbids, and tests with volunteers rather than a random share of live traffic. B works at the DNS layer, where cached resolver answers make a fast revert unreliable, and it duplicates the whole API. C exposes every user to the new version at once, which is the risk the requirement exists to avoid.

*Where this is covered: Stages, deployments, canary releases, and caching.*

</details>

### 9. An authorizer that became the biggest line item (Professional)

A platform team runs 40 REST APIs across 12 accounts, each with a Lambda REQUEST authorizer that validates a bearer token against an identity provider. Authorizer invocations now exceed the number of business Lambda invocations, latency has risen, and the `Latency` metric is climbing while `IntegrationLatency` is flat. Tokens are valid for one hour. The team must cut authorizer cost and latency while keeping the ability to revoke access within roughly five minutes.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Set the authorizer result time to live to 300 seconds so a validated identity is reused for five minutes.
- **B)** Set the authorizer result time to live to 3600 seconds to match the token lifetime.
- **C)** Ensure each authorizer's identity sources include every request attribute the returned policy depends on, so cached policies are not reused across different callers or paths.
- **D)** Turn authorization caching off and increase the authorizer function's provisioned concurrency.
- **E)** Replace the authorizers with API keys in a usage plan shared across the 40 APIs.

<details><summary>Answer</summary>

**Answer: A and C.** A 300 second result cache removes the great majority of authorizer invocations while keeping the revocation window inside the stated five minutes, and a rising `Latency` with a flat `IntegrationLatency` is the signature of exactly this problem. C is the safety condition on caching: the cache key is derived from the named identity sources, so a policy that varies by path or method must have those attributes among the identity sources or one caller's cached decision will be applied to another's request. B caches for an hour and breaks the revocation requirement. D increases cost rather than reducing it. E is wrong twice: API keys are not an authorization mechanism, and AWS documents that a caller with a valid key for one API in a usage plan can call every API in that plan.

*Where this is covered: Authorizers, IAM authorization, and AWS WAF.*

</details>

### 10. One noisy API throttling everything else (Professional)

A company runs a revenue-critical checkout API and a new internal analytics API in the same account and Region. After the analytics API launched, checkout clients began receiving `429 Too Many Requests` during business hours even though checkout traffic did not change. The company must protect checkout, keep analytics working at a reduced rate, and avoid moving either API to another account.

Which solution will meet these requirements?

- **A)** Attach an AWS WAF rate-based rule to the analytics API stage at 500 requests per five minutes.
- **B)** Set stage-level throttling on the analytics API well below the account limit, set stage-level throttling on the checkout API to reserve the remainder, and request an increase to the account-level rate quota if the total still does not fit.
- **C)** Create a usage plan containing both APIs and issue one API key per internal team.
- **D)** Enable stage caching on the analytics API with a 3600 second time to live.

<details><summary>Answer</summary>

**Answer: B.** The account-level throttle quota of 10,000 requests per second is shared across every API of every type in the Region, so one API can consume the budget another one needs; stage-level limits are how that budget is partitioned deliberately, and the account rate itself can be raised through a request. A limits per client IP address rather than in aggregate, so many analytics clients still add up to the same account-level pressure, and it does nothing to reserve capacity for checkout. C meters internal callers but usage plan limits are best-effort and, more importantly, they do not reserve account capacity for the checkout API. D may reduce analytics backend calls, but cached responses are still requests counted against the account throttle, so checkout is no better protected.

*Where this is covered: Usage plans, API keys, and choosing a throttling strategy.*

</details>

## Summary

Amazon API Gateway is a sequence of decisions, and the exam tests them one at a time. Decide the API type first, because it silently decides everything after it: REST APIs when the scenario names API keys, usage plans, request validation, response caching, AWS WAF, canary releases, X-Ray or a private endpoint, HTTP APIs when it describes a plain proxy and asks for the lowest cost or lowest latency, and WebSocket APIs when the server must push. Decide the endpoint type from where the callers are, remembering that private is REST-only. Decide authorization from what the caller already holds: IAM for AWS principals, a Cognito user pool or JWT authorizer for signed-in users, a Lambda REQUEST authorizer for anything custom, and a resource policy when the constraint is a network rather than an identity. Use API keys and usage plans to meter customers, never to secure them. Throttle at the level that matches the reason, per method, per stage, per client or per account, and remember that the account quota is shared across every API in the Region. Then wire the backend through a proxy integration, a service integration or a VPC link V2, and keep any operation longer than 29 seconds off the synchronous path.

## Related units

- [AWS Lambda](../02-compute/lambda.md): the function service behind most proxy integrations, its timeout, concurrency and event shapes
- [Amazon Cognito](../07-security/cognito.md): user pools, tokens and scopes behind user pool and JWT authorizers
- [AWS WAF, AWS Shield, AWS Firewall Manager and AWS Network Firewall](../07-security/waf-shield-firewall-manager-and-network-firewall.md): web ACLs, managed rules and rate-based rules attached to an API stage
- [Amazon VPC](vpc.md): interface endpoints, PrivateLink, private DNS and endpoint policies that make a private API reachable
- [Amazon CloudFront](cloudfront.md): the distribution you own in front of a Regional endpoint, for caching, TLS policy and edge protection
- [Amazon Route 53](route53.md): alias records, latency-based routing and failover across Regional custom domain names
- [AWS Identity and Access Management](../07-security/iam.md): identity policies, resource policies and Signature Version 4 for IAM authorization
- [Amazon SQS](../06-integration/sqs.md): the queue behind the asynchronous pattern for work that outlives an integration timeout

## Sources

- [Choose between REST APIs and HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html): the feature-by-feature split behind the comparison table, including endpoint types, authorizers, caching, AWS WAF, canary releases, tracing and integrations
- [Amazon API Gateway quotas](https://docs.aws.amazon.com/apigateway/latest/developerguide/limits.html): the 10,000 requests per second account quota, the 5,000 burst bucket, and the 2,500 and 1,250 defaults in thirteen Regions
- [Quotas for configuring and running a REST API](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-execution-service-limits-table.html): integration timeouts and the note that Regional and private APIs can exceed 29 seconds, payload size, cache TTL and response size, stages, resources, usage plans, truststore size and header sizes
- [Quotas for configuring and running an HTTP API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-quotas.html): the fixed 30 second integration timeout, 10 MB payload, route and VPC link quotas
- [Quotas for configuring and running a WebSocket API](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-execution-service-websocket-limits-table.html): 2 hour connection lifetime, 10 minute idle timeout, 32 KB frames, 128 KB messages and 500 new connections per second
- [Overview of WebSocket APIs in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-overview.html): route selection expressions, the `$connect`, `$disconnect` and `$default` route keys, and the `@connections` API
- [API endpoint types for REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-api-endpoint-types.html): edge-optimized as the default type, Regional behavior, and the note about using your own CloudFront distribution
- [Custom domain name for public REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-custom-domains.html): base path mappings, per-Region uniqueness, disabling the default endpoint and the multi-level mapping requirement
- [Get certificates ready in AWS Certificate Manager](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-specify-certificate-for-custom-domain-name.html): the us-east-1 rule for edge-optimized domains and the same-Region rule for Regional domains
- [Private REST APIs in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-apis.html): best practices, private DNS behavior, and the REST-only, TLS 1.2 and HTTP/1.1 considerations
- [Create a private API](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-api-create.html): that a private API cannot be deployed until a resource policy is attached, and the VPC endpoint association that creates a Route 53 alias record
- [Control access to a REST API with API Gateway resource policies](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-resource-policies.html): what a resource policy can allow and that it applies to any REST endpoint type
- [Use VPC endpoint policies for private APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-vpc-endpoint-policies.html): the division of work between resource policy and endpoint policy, and the evaluation order
- [Custom domain names for private APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-custom-domains.html): provider and consumer roles, domain name access associations and per-account uniqueness
- [Choose an API Gateway API integration type](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-api-integration-types.html): AWS, AWS_PROXY, HTTP, HTTP_PROXY and MOCK, and why proxy is preferred for Lambda
- [Set up Lambda proxy integrations for REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html): the event the function receives and the `statusCode`, `headers` and `body` response contract
- [Create AWS Lambda proxy integrations for HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html): payload format versions 1.0 and 2.0 and their differences
- [Private integrations for REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/private-integration.html): VPC links V2 for REST APIs, V1 as legacy, same-account ownership and the stage name in the backend path
- [Set up VPC links V2](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-vpc-links-v2.html): subnets and security groups, immutability and the 60 day inactivity behavior
- [Create private integrations for HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-private.html): Application Load Balancer, Network Load Balancer and AWS Cloud Map targets
- [Data transformations for REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/rest-api-data-transformations.html): parameter mapping compared with Velocity Template Language mapping templates, and which works on a proxy integration
- [Transform API requests and responses for HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html): the append, overwrite and remove keys for headers, query strings and path
- [Request validation for REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-method-request-validation.html): models, validators, the 400 response and the reduction in backend calls
- [CORS for REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html): simple compared with non-simple requests and the preflight response a proxy integration must return itself
- [Use API Gateway Lambda authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html): TOKEN compared with REQUEST, the returned policy document, caching behavior and the AWS recommendation
- [CreateAuthorizer API reference](https://docs.aws.amazon.com/apigateway/latest/api/API_CreateAuthorizer.html): the authorizer result time to live default of 300 seconds and maximum of 3600
- [Control access to HTTP APIs with JWT authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html): the claims validated and the two hour public key cache
- [Control access to REST APIs using Amazon Cognito user pools as an authorizer](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html): identity compared with access tokens and the COGNITO_USER_POOLS authorizer
- [Control access to HTTP APIs with IAM authorization](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control-iam.html): Signature Version 4 and the statement that resource policies are not currently supported for HTTP APIs
- [Control and manage access to WebSocket APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api-control-access.html): IAM and Lambda REQUEST authorizers only, and the `$connect` recommendation
- [Use AWS WAF to protect your REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-aws-waf.html): that AWS WAF is evaluated before resource policies and authorizers, rate-based rules and the 64 KB body inspection limit
- [Usage plans and API keys for REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-api-usage-plans.html): key length and uniqueness rules, and the warnings against using API keys for authorization or usage plans for cost control
- [Choose an API key source](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-api-key-source.html): the `X-API-Key` header and the AUTHORIZER key source
- [Throttle requests to your REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-request-throttling.html): the four throttling levels, the order they are applied in and the token bucket behavior
- [Throttle requests to your HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-throttling.html): account-level and route-level throttling for HTTP APIs
- [Deploy REST APIs in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-deploy-api.html): deployments compared with stages, the redeploy requirement and the invoke URL shape
- [Cache settings for REST APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-caching.html): default and maximum TTL, the 1,048,576 byte response limit, the GET-only default and cache keys
- [CreateStage API reference](https://docs.aws.amazon.com/apigateway/latest/api/API_CreateStage.html): the valid cache cluster sizes from 0.5 to 237 GB and the canary settings fields
- [Set up an API Gateway canary release deployment](https://docs.aws.amazon.com/apigateway/latest/developerguide/canary-release.html): traffic percentage, stage variable overrides and the separate canary log group
- [Amazon API Gateway dimensions and metrics](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-metrics-and-dimensions.html): Latency compared with IntegrationLatency, cache metrics and detailed metrics
- [Trace user requests to REST APIs using X-Ray](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-xray.html): X-Ray support on all REST endpoint types including private, and trace pass-through
- [Amazon API Gateway pricing](https://aws.amazon.com/api-gateway/pricing/): the per-request tiers for REST and HTTP APIs, WebSocket message and connection-minute pricing, and hourly cache pricing
- [Amazon API Gateway FAQs](https://aws.amazon.com/api-gateway/faqs/): the statement that HTTP APIs are ideal for latency-sensitive workloads and workloads likely to grow very large
