# AI developer tools and generative AI on the exams

**Where it sits on the exams.** **Amazon Bedrock** is the managed service that makes foundation models from several providers available through one API, and **Amazon Q** is the assistant family AWS builds on top of it. Neither appears on the in-scope service list of either exam guide. The only place generative AI is named is the SAP-C02 guide's emerging topics section, where the named area is design security and responsible AI controls, and which the guide opens by noting that the exam "may include unscored pretest questions on emerging topics". Read that framing carefully, because it decides how much time this unit deserves: a question that names Bedrock is almost always testing the in-scope services doing the work around the model. The network path is **AWS PrivateLink**, the private connectivity service behind VPC interface endpoints, in SAA-C03 task 1.2 and SAP-C02 task 2.3. The permission boundary is **AWS Identity and Access Management (IAM)**, the service that decides which principal may perform which action on which resource, in SAA-C03 task 1.1 and SAP-C02 task 2.3, extended across accounts by **AWS Organizations**, the multi-account governance service. The human approval step is **AWS Step Functions**, the managed workflow service that coordinates steps as a state machine, in SAP-C02 task 4.4. Learn those, plus enough generative AI vocabulary to recognize the scenario, and stop there.

## Amazon Q Developer and Amazon Q Business

**Amazon Q Developer**, formerly Amazon CodeWhisperer, is the generative AI assistant for building and operating on AWS. It answers questions about AWS architecture, services, documentation and the resources in your own account, and inside an integrated development environment (IDE) it chats about code, completes code inline, generates new code, scans for security vulnerabilities and performs upgrades such as language version transformations. It is built on Amazon Bedrock, with the underlying model augmented by AWS content so answers carry references. You reach it from the AWS Management Console, the AWS documentation site, Slack and Microsoft Teams, and from IDE extensions, on a Free tier or an Amazon Q Developer Pro subscription.

One status note matters. AWS will discontinue support for the Amazon Q Developer IDE plugins on April 30, 2027, and points customers at Kiro for the equivalent inline suggestions, chat and code generation. The rest of Amazon Q Developer is unaffected. Neither the plugins nor Kiro appear on an exam guide, so the fact to carry is the rename: CodeWhisperer became part of Amazon Q Developer on April 30, 2024, and is the older name a stale question stem might still use.

**Amazon Q Business** is the managed assistant that answers questions over enterprise content. It connects to sources such as **Amazon Simple Storage Service (Amazon S3)**, the object storage service, SharePoint and Salesforce, indexes them, and returns answers with citations. Its one architecturally interesting property is that responses are permissions-aware: a user sees answers built only from content they are already entitled to read, with end user access managed through **AWS IAM Identity Center**, the workforce single sign-on service, or through IAM. Amazon Q Business is no longer open to new customers. AWS continues bug fixes and security updates, considers no new feature requests, and recommends migrating to **Amazon Quick**, formerly Amazon QuickSight, the business intelligence and assistant service, whose bring your own index capability carries an existing Q Business index across. Bedrock offers models from Amazon and several third-party providers through one API. Inference runs against the `bedrock-runtime` endpoint, through the provider-neutral `Converse` API or the older `InvokeModel`, each with a streaming variant. Model providers deliver their software into Amazon Bedrock model deployment accounts that the providers themselves cannot access, so AWS states that providers have no access to Amazon Bedrock logs or to customer prompts and completions.

## Amazon Bedrock: models, Knowledge Bases, Guardrails and agents

**Amazon Bedrock** is the managed service that provides access to foundation models from Amazon and several third-party providers through one API, with no infrastructure to run.

**Amazon Bedrock Knowledge Bases** is the managed retrieval augmented generation (RAG) capability: connect data sources, and a query searches your own data for relevant passages before the model answers, with citations back to the source. There are two shapes. A managed knowledge base lets Amazon Bedrock own ingestion, embedding, indexing, storage and retrieval, and offers connectors for Amazon S3, SharePoint, Confluence, Google Drive, OneDrive and a web crawler, with document-level permission filtering from access control lists applied at retrieval time. A customer-managed knowledge base leaves you running the vector store yourself on **Amazon OpenSearch Serverless**, **Amazon Aurora** or **Amazon Neptune**, the managed search, relational and graph engines, in exchange for control of parsing, indexing and storage. The exam-relevant distinction is the one this unit turns on: retrieval either respects existing permissions or it does not, and that is an access control decision rather than a model decision.

**Amazon Bedrock Guardrails** applies configurable safety and privacy filters to prompts and responses, covered in its own section below. For autonomy, the current service is **Amazon Bedrock AgentCore**, the platform for building, deploying and operating agents with any framework and any model. Its component services cover identity, tool access, memory, observability and evaluation. The older **Amazon Bedrock Agents**, now named Amazon Bedrock Agents Classic, is no longer open to new customers; AWS directs new work to AgentCore. Finally, PartyRock, an Amazon Bedrock playground for building small generative AI apps in a browser, sits outside the console and was announced as needing no AWS account, though the launch post is from 2023 and the current sign-in requirements are worth checking before relying on that.

## The architecture around the model

Start with the network path. Amazon Bedrock is reached over the public AWS API endpoints by default, and a workload that must not send prompts over the internet uses an interface VPC endpoint powered by AWS PrivateLink, created from service names such as `com.amazonaws.region.bedrock-runtime` for inference and `com.amazonaws.region.bedrock` for control plane calls, with FIPS variants in a subset of Regions. Enable private DNS and no application code changes; leave it off and each client must pass the endpoint URL explicitly. An endpoint policy attached to the interface endpoint narrows what may be called through it, listing the principals, actions and resources allowed. Its default grants full access to Amazon Bedrock, so the restriction is always something you write.

Next the permission boundary. Inference permissions are ordinary IAM, and the resource element can name a single model, which is how an organization allows some models and refuses others. AWS gives this example as a deny that can also serve as a service control policy (SCP) controlling model access across an organization:

```json
{
  "Sid": "DenyInference",
  "Effect": "Deny",
  "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream",
             "bedrock:CreateModelInvocationJob"],
  "Resource": "arn:aws:bedrock:*::foundation-model/model-id"
}
```

Denying `InvokeModel` automatically blocks `Converse` and `StartAsyncInvoke`; use `*` for the model ID to deny every model.

Then the data flow. Model invocation logging is disabled by default and, once enabled, captures the full request body, response body and metadata for `Converse`, `ConverseStream`, `InvokeModel` and `InvokeModelWithResponseStream`, delivered to **Amazon CloudWatch Logs**, the log storage and query service, to Amazon S3, or to both in the same account and Region. Bodies up to 100 KB appear inline; anything larger, and binary output such as images, goes to Amazon S3 as separate objects, which is why a requirement to log image prompts forces an S3 destination. Each record carries the calling principal's ARN, so token consumption can be attributed per role without extra tagging. That is the prompt and completion record; **AWS CloudTrail**, the API activity recorder, separately records who created a guardrail or changed a logging configuration. Encrypt the destination with **AWS Key Management Service (AWS KMS)**, the managed key service.

## The three SAP-C02 emerging-topic skills

The guide names three skills, and each has a concrete mechanism.

The first is content filtering and regulatory compliance controls, which is Amazon Bedrock Guardrails. A guardrail carries six policy types. Content filters detect harmful text or image content across the predefined categories Hate, Insults, Sexual, Violence, Misconduct and Prompt Attack, with configurable strength per category. Denied topics block subjects you define, such as investment advice in a banking assistant. Word filters block exact words and phrases, including a ready-made profanity list. Sensitive information filters block or mask personally identifiable information (PII) and custom regular expression matches, the control wanted by a scenario asking to redact customer data from call transcripts. Contextual grounding checks catch responses that are not grounded in the retrieved source or are irrelevant to the question, the natural pairing with a knowledge base. Automated Reasoning checks validate a response against a set of logical rules. A guardrail has a working draft you iterate on and numbered versions you deploy. Two deployment routes matter: pass the guardrail identifier and version on an inference call, or call `ApplyGuardrail` on its own to evaluate text without invoking any model, which is how the same policy covers content that never touches Amazon Bedrock.

The second is access control for generative and agentic AI applications, which is **AgentCore Identity**, identity and credential management built for non-human callers. Each agent gets a workload identity with its own ARN in a directory, which AWS compares to a user pool in **Amazon Cognito**, the customer identity service, as a unit of governance. Inbound, a JWT authorizer validates the caller against an existing identity provider such as Amazon Cognito, Okta or Microsoft Entra ID, so the agent knows which user it is acting for. Outbound, a token vault stores OAuth 2.0 tokens, OAuth client credentials and API keys encrypted under service-managed or customer-managed AWS KMS keys, releasing them only to an agent that proves its workload identity. It supports the OAuth 2.0 client credentials grant, machine to machine with no user present, and the authorization code grant, where the end user consents explicitly to the agent reaching their data in a third-party service. The point for an exam answer is that credentials stop living in agent code or container images.

The third is human oversight with approval mechanisms, which is Step Functions, through the wait for callback integration pattern. Append `.waitForTaskToken` to a task's resource ARN and pass `"TaskToken.$": "$$.Task.Token"` from the context object into the message the task sends. The execution pauses. An approver receives the notification, and an external process calls `SendTaskSuccess` or `SendTaskFailure` with that token to resume or fail the branch. Three details decide questions. A paused callback task waits until the execution hits the one-year service quota, so a `HeartbeatSeconds` timeout is how you avoid a stuck approval, failing the task with `States.Timeout`. The pattern is supported only on Standard workflows, never on Express, which support Request Response integrations only. And the token must be returned by a principal in the same AWS account. The services commonly used to reach the human, **Amazon Simple Notification Service (Amazon SNS)** and **Amazon Simple Queue Service (Amazon SQS)**, the publish-subscribe and message queue services, both support the pattern, as do Lambda and the Amazon Bedrock optimized integration.

## Professional depth

At organization scale, guardrails stop being an application setting and become a policy. Guardrails enforcements apply a guardrail to every model invocation across an organizational unit, a set of accounts, or the whole organization, using Amazon Bedrock policies in AWS Organizations. The sequence matters: create the guardrail in the management account in every Region where it must apply, create a numbered version so member accounts cannot modify it, attach a resource-based policy granting `bedrock:ApplyGuardrail` to the organization, grant that permission in member account roles, enable the `BEDROCK_POLICY` type in AWS Organizations, then attach a policy naming the guardrail ARN and version. Account-level enforcement does the same for one account through `PutEnforcedGuardrailConfiguration`, per Region.

Layering is the part a Professional question exploits. An organization-enforced guardrail, an account-enforced guardrail and a guardrail named in the request all apply at once, and the effective control is the union of all three with the most restrictive setting winning, so a team cannot weaken the organization's policy by passing a laxer guardrail of their own. Three operational facts come with it. Automated Reasoning checks are not supported in an enforcement configuration and cause runtime failures if included, so the organization policy uses the other five policy types. A guardrail referenced by an enforcement configuration cannot be deleted. And consumption counts against the calling member account's Guardrails service quotas, so review those before switching enforcement on, or inference starts throttling in accounts that configured nothing.

Naming the wrong ARN in the policy is the failure mode with the worst blast radius. AWS warns that an incorrect or invalid guardrail ARN results in policy violations, non-enforcement of the safeguards, and the inability to use models in Amazon Bedrock for inference at all. It silently turns off protection and loudly turns off the workload, so it belongs behind a staged rollout: one organizational unit, then one Region, then the estate.

> **Professional depth.** The Associate version of the approval question is "pause the workflow until a person approves", answered by a Standard workflow with `.waitForTaskToken`. The Professional version adds accounts and time. The token must come back from a principal in the same account as the state machine, so an approver working in a separate security or operations account approves through an API in the workflow's account rather than by calling `SendTaskSuccess` directly. The heartbeat timeout stops an abandoned approval from holding an execution for a year.

## Worked scenario

An insurer runs 60 accounts in one AWS organization with all features enabled. A claims team wants an assistant that drafts claim adjustment letters from policy documents and adjuster notes. Three constraints bind: prompts and completions must never traverse the internet, no letter may be sent without a named adjuster approving it, and a compliance group must be able to prove months later what the model was asked and what it produced.

The application runs in a private subnet and calls Amazon Bedrock through an interface VPC endpoint for `com.amazonaws.region.bedrock-runtime` with private DNS enabled, so no code changes and no internet gateway. An endpoint policy allows only `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream`, and the application role's IAM policy names the single approved foundation model ARN in its resource element, so a developer cannot quietly switch models. Policy documents live in a managed knowledge base over Amazon S3 with document-level permission filtering, so retrieval cannot surface a policy the requesting adjuster is not entitled to read.

Safety is two layers. The organization enforces a versioned guardrail from the management account through an Amazon Bedrock policy in AWS Organizations, carrying sensitive information filters to mask PII and denied topics covering legal and medical advice. The application adds its own guardrail with a contextual grounding check, so a letter that drifts from the retrieved policy text is blocked. The two combine as a union with the more restrictive control winning.

Approval is a Standard Step Functions workflow. The draft task invokes the model, the next task is an Amazon SNS publish with `.waitForTaskToken` notifying the assigned adjuster, and `HeartbeatSeconds` fails the branch if nobody responds in two business days. The decision returns through an internal API that calls `SendTaskSuccess` from the workflow's own account, and only the success branch sends the letter. Model invocation logging writes prompts and completions to Amazon S3 under an AWS KMS key, and CloudTrail records the API activity around it. When the exam asks about this scenario, the keyed answer is an interface VPC endpoint for the private path, an organization-level enforced guardrail for the mandatory filtering, a Standard workflow with a task token callback for the human approval, and model invocation logging for the record.

## Exam lens

- "Prompts must not leave the VPC or traverse the internet" maps to an interface VPC endpoint for `bedrock-runtime` with AWS PrivateLink; a NAT gateway is the distractor, because it still sends traffic over the public internet.
- "Allow only one approved model and block the rest" maps to an IAM policy, or an SCP, naming the foundation model ARN in the resource element of an `InvokeModel` statement; denying `InvokeModel` also blocks `Converse`.
- "Record exactly what was sent to the model and what came back" maps to model invocation logging to Amazon S3 or CloudWatch Logs; CloudTrail is the distractor, because it records API activity rather than prompt and completion bodies.
- "Redact customer PII from model input and output" maps to a Guardrails sensitive information filter, not to **Amazon Macie**, the S3 data discovery service, which inspects stored objects rather than an inference request.
- "Block responses that are not supported by the retrieved documents" maps to a Guardrails contextual grounding check.
- "Retrieval must not surface a document the asking user cannot already read" maps to a managed knowledge base with document-level permission filtering.
- "Apply the same content policy to every account in the organization" maps to a versioned guardrail plus an Amazon Bedrock policy in AWS Organizations. An SCP is the distractor: the `bedrock:GuardrailIdentifier` condition key can require, and even name, a guardrail on an invocation, but requiring one is not the same as configuring one, and pinning a single identifier blocks teams from adding stricter checks of their own.
- "Evaluate text against our safety policy without calling a model" maps to the `ApplyGuardrail` API.
- "A person must approve before the action is taken, and the workflow must not hang forever" maps to a Standard Step Functions workflow with `.waitForTaskToken`, `SendTaskSuccess` and a `HeartbeatSeconds` timeout; an Express workflow is the distractor, because Express supports Request Response integrations only.
- "An agent must call a third-party SaaS API as the signed-in user, with no secrets in the code" maps to an AgentCore Identity OAuth 2.0 authorization code grant credential provider and the token vault; **AWS Secrets Manager**, the managed secret store, is the near miss, because it holds a secret but performs no user consent flow.

## Knowledge check

### 1. Keeping inference off the internet (Associate)

A healthcare company runs an application on virtual servers in the private subnets of a VPC. The application calls Amazon Bedrock to summarize clinical notes. A security review requires that the request and response traffic between the application and Amazon Bedrock never traverse the public internet. The company wants to avoid changing application code.

Which solution will meet these requirements?

- **A)** Route the traffic through a NAT gateway in a public subnet and restrict the route table to the Amazon Bedrock IP ranges.
- **B)** Deploy an AWS Site-to-Site VPN connection between the VPC and the Amazon Bedrock service endpoint.
- **C)** Create an interface VPC endpoint for `com.amazonaws.region.bedrock-runtime` with private DNS enabled, and attach an endpoint policy allowing only the inference actions.
- **D)** Create a gateway VPC endpoint for Amazon Bedrock and add a route to it in the private subnet route tables.

<details><summary>Answer</summary>

**Answer: C.** An interface VPC endpoint powered by AWS PrivateLink places an endpoint network interface in the subnet, so calls reach Amazon Bedrock without an internet gateway, NAT device or public IP address. Enabling private DNS means the application keeps using the standard Regional DNS name with no code change, and an endpoint policy narrows what can be called through it. A still sends the traffic over the public internet, which is exactly what the review forbids. B is not an available connection: a VPN terminates against a customer gateway or a transit gateway, not against an AWS service endpoint. D names the wrong endpoint type; gateway endpoints exist only for Amazon S3 and DynamoDB, and Amazon Bedrock is reached through an interface endpoint.

*Where this is covered: The architecture around the model.*

</details>

### 2. Proving what the model was asked (Associate)

A financial services company uses Amazon Bedrock to draft customer correspondence. Auditors require a record of the complete prompt text and the complete model response for every invocation, retained for later analysis. The security team separately requires a record of which principal created or modified guardrail configurations in the account.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Enable model invocation logging in Amazon Bedrock and configure an Amazon S3 bucket as the destination.
- **B)** Enable AWS Config rules for Amazon Bedrock resource types.
- **C)** Enable VPC Flow Logs on the subnets that host the application.
- **D)** Enable an AWS CloudTrail trail in the account and deliver it to Amazon S3.
- **E)** Enable AWS X-Ray tracing on the application that calls Amazon Bedrock.

<details><summary>Answer</summary>

**Answer: A and D.** Model invocation logging is the only mechanism that captures the request body and response body of `InvokeModel` and `Converse` calls; it is disabled by default, and an Amazon S3 destination handles bodies larger than 100 KB as separate objects. CloudTrail records the API activity around Amazon Bedrock, including who created or changed a guardrail. B records configuration item history for resources and never captures prompt content. C records packet metadata such as source, destination and ports, not payloads. E records latency and call graph segments for troubleshooting, not the text sent to a model.

*Where this is covered: The architecture around the model.*

</details>

### 3. Restricting which model a team may call (Associate)

A company allows one business unit to use Amazon Bedrock but has approved only a single foundation model for that unit after a legal review. The company must prevent the unit's application role from running inference on any other foundation model, while leaving the approved model available.

Which solution will meet these requirements?

- **A)** Attach an IAM policy to the role that allows `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` with the resource element set to the approved foundation model ARN only.
- **B)** Create a guardrail with a denied topic for each unapproved model and enforce it at the account level.
- **C)** Remove the `AmazonBedrockFullAccess` managed policy from the role and rely on the Amazon Bedrock console's model access page.
- **D)** Configure an endpoint policy on the VPC interface endpoint that allows all Amazon Bedrock actions on all resources.

<details><summary>Answer</summary>

**Answer: A.** Amazon Bedrock inference permissions are ordinary IAM, and the resource element accepts a foundation model ARN of the form `arn:aws:bedrock:*::foundation-model/model-id`, so scoping the allow to one ARN permits that model and implicitly denies the rest. B misuses the mechanism: denied topics filter subject matter in prompts and responses and have nothing to do with which model is invoked. C leaves no permission boundary in place at the API level, and a console page is not an access control for programmatic calls. D allows everything on every resource, which is the opposite of the requirement.

*Where this is covered: The architecture around the model.*

</details>

### 4. Pausing for a human decision (Associate)

A company builds a workflow that uses a foundation model to draft refund decisions. Each draft must be reviewed by a support manager, and the workflow must not continue until the manager approves or rejects it. Reviews normally take a few hours but must not hold the workflow indefinitely. The company wants the least operational overhead.

Which solution will meet these requirements?

- **A)** Use an Express workflow in AWS Step Functions with a Wait state set to four hours, then read an approval flag from Amazon DynamoDB.
- **B)** Poll an Amazon SQS queue from an AWS Lambda function on an Amazon EventBridge schedule until an approval message appears.
- **C)** Store the draft in Amazon S3 and use an S3 event notification to resume processing when the manager uploads an approval file.
- **D)** Use a Standard workflow in AWS Step Functions with an Amazon SNS publish task using `.waitForTaskToken`, and set `HeartbeatSeconds` so the task fails if no response arrives in time.

<details><summary>Answer</summary>

**Answer: D.** The wait for callback pattern is built for exactly this: the task passes `$$.Task.Token` in the notification, the execution pauses, and `SendTaskSuccess` or `SendTaskFailure` resumes it. `HeartbeatSeconds` bounds the wait and fails the task with `States.Timeout` rather than letting it run to the one-year execution quota. A fails twice: Express workflows do not support callback integrations at all, and a fixed Wait state guesses at a review time instead of waiting for the decision. B rebuilds the callback mechanism with a polling loop the service already provides, adding a schedule, a function and a queue to operate. C makes an approval depend on a manager uploading a file to a bucket, which is both fragile and unauditable compared with a recorded task token response.

*Where this is covered: The three SAP-C02 emerging-topic skills.*

</details>

### 5. One content policy across 60 accounts (Professional)

An enterprise runs 60 AWS accounts in one AWS organization with all features enabled. Several teams build applications on Amazon Bedrock in their own accounts. Compliance requires that every model invocation anywhere in the organization masks personally identifiable information and blocks a defined list of prohibited topics, that application teams cannot weaken the policy, and that individual teams may still add stricter checks of their own.

Which solution will meet these requirements?

- **A)** Distribute a guardrail template to each team with a written standard requiring them to attach it to every inference call.
- **B)** Create a versioned guardrail in the management account, attach a resource-based policy granting `bedrock:ApplyGuardrail` to the organization, enable the `BEDROCK_POLICY` policy type in AWS Organizations, and attach a policy naming that guardrail ARN and version to the organization root.
- **C)** Attach a service control policy to the organization root that denies `bedrock:InvokeModel` unless the request includes a guardrail identifier.
- **D)** Enable account-level guardrail enforcement in each of the 60 accounts and ask account owners to keep the configuration current.

<details><summary>Answer</summary>

**Answer: B.** Guardrails enforcements apply a guardrail to every model invocation across the organization through an Amazon Bedrock policy in AWS Organizations, the numbered version makes the configuration immutable to member accounts, and an application guardrail supplied on the request combines with it as a union in which the most restrictive control wins, so teams can add strictness but not remove it. A depends on every team complying every time, which is a standard rather than a control. C is closer than it looks, because the `bedrock:GuardrailIdentifier` condition key can pin a specific guardrail ARN and version. It still fails the requirement: a policy tight enough to name one guardrail forbids the stricter guardrails the stem says teams may add, and one loose enough to allow them lets a team pass an empty guardrail instead. D is the right mechanism at the wrong scope: account-level enforcement must be configured per account and per Region, and nothing stops an account owner from removing it.

*Where this is covered: Professional depth.*

</details>

### 6. An agent acting for a signed-in user (Professional)

A company deploys an agent on Amazon Bedrock AgentCore that must read a user's records from a third-party SaaS application. The agent must act as the individual signed-in user rather than under one shared service account, the user must explicitly consent to that access, and no long-lived credential may be stored in the agent's container image or source code. Requests reaching the agent must be attributable to a verified corporate identity.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Configure an inbound JWT authorizer in AgentCore Identity that validates the caller's token against the corporate identity provider.
- **B)** Store a shared SaaS API key in AWS Secrets Manager and have the agent retrieve it at startup.
- **C)** Configure an outbound OAuth 2.0 authorization code grant credential provider in AgentCore Identity so the user consents and the resulting token is held in the token vault.
- **D)** Embed a long-lived SaaS refresh token in the agent's container image and rotate the image weekly.
- **E)** Grant the agent's execution role `bedrock:InvokeModel` on all foundation models.

<details><summary>Answer</summary>

**Answer: A and C.** The inbound JWT authorizer verifies who is calling the agent against an existing provider such as Amazon Cognito, Okta or Microsoft Entra ID, which is what makes the request attributable to a corporate identity. The authorization code grant, the three-legged OAuth flow, is the one that asks the end user for explicit consent and produces a user-scoped token, and AgentCore Identity keeps that token in its encrypted token vault, released only to an agent that proves its workload identity, so nothing is stored in the image. B gives every user the same shared identity and no consent step, breaking two stated requirements. D is the anti-pattern the requirement rules out, and a weekly rotation does not change that the credential lives in the image. E is an inference permission and says nothing about SaaS access or user identity.

*Where this is covered: The three SAP-C02 emerging-topic skills.*

</details>

## Summary

Generative AI on these exams is a short list of decisions taken around a service that is not itself examinable. Decide first whether the question is about the model at all: Amazon Bedrock, Amazon Q and AgentCore appear on neither in-scope list, so the graded content is the in-scope architecture. Decide the network path: public endpoint, or an interface VPC endpoint with AWS PrivateLink and an endpoint policy when prompts must not leave the VPC. Decide the permission boundary: which principals may call inference, and which foundation model ARN their policy names. Decide what is recorded: model invocation logging for prompt and completion bodies, with an Amazon S3 destination for payloads over 100 KB, and CloudTrail for the API activity around it. Decide the content policy: which guardrail policy types apply, whether the guardrail rides on the inference call or on `ApplyGuardrail`, and whether it is enforced organization-wide through an Amazon Bedrock policy in AWS Organizations. Decide how identity reaches an agent: AgentCore Identity for inbound verification and outbound tokens in a vault. And decide where a person signs off: a Standard Step Functions workflow with `.waitForTaskToken` and a heartbeat timeout.

## Related units

- [AWS Step Functions](../06-integration/step-functions.md): the callback integration pattern, Standard compared with Express workflows, and the state types behind an approval workflow
- [AWS Identity and Access Management](../07-security/iam.md): identity-based policies, resource ARNs and the service control policies that scope model access
- [Managed machine learning services](ml-managed-services.md): the purpose-built AI services that are in scope on both exams, and when one of them replaces a generative AI build
- [AWS Organizations, IAM Identity Center and AWS Control Tower](../07-security/organizations-identity-center-and-control-tower.md): the organization policy types and delegated administration that guardrail enforcement depends on
- [Amazon VPC](../04-networking/vpc.md): interface endpoints, AWS PrivateLink and endpoint policies for a private path to an AWS API
- [Amazon CloudWatch](../08-management/cloudwatch.md): log groups, Logs Insights queries and the metrics guardrail interventions publish
- [AWS CloudTrail](../08-management/cloudtrail.md): management and data events for Amazon Bedrock API activity
- [AWS KMS and AWS CloudHSM](../07-security/kms-and-cloudhsm.md): customer managed keys for log destinations and for the AgentCore Identity token vault

## Sources

- [What is Amazon Q Developer?](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/what-is.html): what Amazon Q Developer does, that it is built on Amazon Bedrock, where it runs, and the Free and Pro tiers
- [Amazon Q Developer rename, summary of changes](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/service-rename.html): the April 30, 2024 date on which Amazon CodeWhisperer became part of Amazon Q Developer
- [Amazon Q Developer IDE plugins end of support](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/q-developer-ide-end-of-support.html): the April 30, 2027 date and the recommendation to move to Kiro
- [What is Amazon Q Business?](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/what-is.html): permissions-aware responses, connectors, and IAM Identity Center or IAM for end user access
- [Amazon Q Business availability change](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/qbusiness-availability-change.html): closed to new customers, continued bug fixes, and Amazon Quick with bring your own index as the path
- [Amazon Bedrock overview](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html): 100 or more foundation models, the providers, the `bedrock-runtime` endpoint and the Converse and Invoke APIs
- [Retrieve data and generate AI responses with Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html): managed compared with customer-managed knowledge bases, connectors, vector stores and document-level permission filtering
- [Detect and filter harmful content by using Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html): the six policy types, the content filter categories, working draft and versions, and the `ApplyGuardrail` API
- [Apply cross-account safeguards with Amazon Bedrock Guardrails enforcements](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-enforcements.html): organization and account-level enforcement, the `BEDROCK_POLICY` type, the union rule, the Automated Reasoning exclusion, undeletable enforced guardrails and member account quota consumption
- [Automate tasks in your application using AI agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html): Amazon Bedrock Agents Classic closed to new customers, with AgentCore named as the path forward
- [What is Amazon Bedrock AgentCore?](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html): the modular services including Runtime, Memory, Gateway, Identity, Code Interpreter, Browser, Observability and Policy
- [Provide identity and credential management for agent applications with Amazon Bedrock AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html): the current name and what the service manages
- [Features of AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/key-features-and-benefits.html): workload identity directory, the token vault and AWS KMS encryption, and the client credentials and authorization code grants
- [Use interface VPC endpoints (AWS PrivateLink) to create a private connection between your VPC and Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html): the endpoint service names, private DNS behavior and the endpoint policy example
- [Identity-based policy examples for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_id-based-policy-examples.html): the foundation model ARN in the resource element, the SCP note, and that denying `InvokeModel` blocks `Converse`
- [Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html): disabled by default, the logged operations, the destinations, the 100 KB inline limit and the calling principal ARN
- [Data protection in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html): model deployment accounts and the statement that providers have no access to logs, prompts or completions
- [Discover service integration patterns in Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/connect-to-resource.html): `.waitForTaskToken`, `$$.Task.Token`, `SendTaskSuccess` and `SendTaskFailure`, `HeartbeatSeconds`, the one-year quota, the same-account rule and the Standard-only support table
- [Announcing PartyRock, an Amazon Bedrock Playground](https://aws.amazon.com/about-aws/whats-new/2023/11/partyrock-amazon-bedrock-playground/): the no-code playground, its web UI separate from the console, and that no AWS account is required
