# AWS developer tools and CI/CD

**Where it sits on the exams.** The developer tools in this unit are outside the current SAA-C03 in-scope service list; they are SAP-C02 material for tasks 2.1 and 3.1. **AWS CodePipeline**, the managed continuous delivery orchestrator, moves an immutable revision through source, build, test, approval and deployment actions. **AWS CodeBuild**, the managed build service, compiles and tests it; **AWS CodeDeploy**, the managed deployment service, installs or shifts traffic to it; and **AWS CodeArtifact**, the managed package repository, supplies versioned dependencies. Rule of thumb: a pipeline coordinates stages, a build project turns source into tested artifacts, a deployment group controls rollout and rollback, and the safest strategy limits blast radius while keeping a known-good revision ready.

## Build a pipeline from immutable artifacts

A CodePipeline pipeline consists of ordered stages, and each stage contains one or more actions. A source action produces an output artifact; later actions consume named artifacts and can produce new ones. Actions in the same run order can execute in parallel, while a higher run order waits for the previous group. A stage succeeds only after its required actions and conditions succeed. The source revision and output artifacts should remain immutable so the exact version tested is the one deployed.

CodePipeline stores artifacts in **Amazon Simple Storage Service (Amazon S3)**, the durable object storage service. Its service role needs permission to call each action provider and access the artifact bucket. Artifacts can use a customer-managed **AWS Key Management Service (AWS KMS)** key, the managed encryption-key service. Cross-Region actions require an artifact store in each action Region, and cross-account actions normally add an assumable role and key and bucket policies that trust the pipeline account. These are data-path requirements, not merely console configuration.

The pipeline is orchestration, not a universal execution environment. A CodeBuild action runs commands; a CodeDeploy action deploys; a manual approval pauses for a decision; and an **AWS CloudFormation** action, the infrastructure-as-code deployment service, can create or update stacks. Give each action a narrowly scoped role instead of making the pipeline role an administrator. Separate the permission to approve production from the permission to change pipeline structure.

Stage conditions and action failure behavior implement gates. A rule can consult an alarm or another supported condition before entry, after success or on failure, and the configured result can stop, retry or roll back where supported. Rollback reruns the stage with the artifact from a previously successful pipeline execution; it does not invent an application rollback that the target service cannot perform. Preserve the old deployable revision and test rollback itself.

Pipeline execution mode decides what happens when revisions arrive faster than they finish. `SUPERSEDED` lets a newer execution overtake an older one that has not entered a later stage, which suits fast-moving delivery where only the newest revision matters. `QUEUED` preserves sequential order. `PARALLEL` permits concurrent executions but gives up some stage rollback behavior and requires targets that safely isolate revisions. Select the mode from ordering and shared-environment constraints, not from desired build speed alone.

Start executions from an explicit trigger. A connection-based source can filter branches, tags, pull-request events or file paths, while scheduled or event-driven starts fit sources without a native change trigger. Prevent duplicate starts when two mechanisms observe the same revision. Pipeline and action variables can carry commit metadata or generated values, but they are not a secret store. Record the revision identifier with the deployment so an operator can trace a running version back through approval, test and source evidence.

## Choose source control and package storage

Source code and build dependencies are different artifacts. A Git repository versions the files the team authors and branches or pull requests around them. A package repository stores built or third-party packages resolved by tools such as npm, Maven, pip and NuGet. Do not put mutable dependency downloads or generated binaries into a source repository merely because both are called artifacts.

**AWS CodeCommit**, the AWS-hosted private Git service, supports branches, pull requests, approval rule templates, notifications and IAM-based access for existing customers. It is closed to new customers; existing customers continue normally. For a new pipeline, use a supported external Git provider through **AWS CodeConnections**, the managed connection between AWS developer services and third-party repositories, or another supported source. A stale exam scenario that explicitly says an existing company uses CodeCommit can still key to its pull requests, events and CodePipeline integration.

**AWS Identity and Access Management (IAM)**, the AWS authorization service, controls CodeCommit HTTPS Git credentials, SSH keys, API calls and repository actions. Repository events can start pipelines through the current source integration rather than periodic polling. Protect the default branch with review and merge controls, and pin a pipeline to the intended branch or trigger filter. A successful source checkout proves neither code quality nor artifact provenance.

For an external provider, authorize the connection installation only for the intended organization and repositories, and restrict who can pass that connection to a pipeline. Repository permission and AWS connection permission are separate boundaries. Revoking either can stop delivery even while the other side still appears correctly configured.

CodeArtifact organizes repositories inside a domain. Repositories can have upstream repositories, forming an ordered dependency search path, and one repository can connect to a supported public package source. When a requested version is found upstream, CodeArtifact retains it so later builds can obtain the same package from the domain. Domains centralize storage and policy across repositories and can be shared across accounts with resource policies.

Clients authenticate to a CodeArtifact repository with an authorization token and the endpoint for the package format. The caller needs IAM permission to obtain the token and read or publish packages. Use separate publish and consume roles, restrict allowed package origins, and prefer exact versions plus a lock file. Upstreams improve caching and availability, but an unconstrained public fallback can import a malicious package that shadows an internal name. Package-origin controls and deliberate namespace ownership reduce dependency-confusion risk.

## Compile and test with CodeBuild

A CodeBuild project selects source, an environment image and compute size, environment variables, a service role, a build specification and output artifacts. Each build runs in a fresh environment, so files left on its local filesystem are not durable state. Use an S3 or local cache only as an optimization; the build must remain correct when the cache is empty. Store final outputs as versioned pipeline artifacts or publish packages and container images to their proper repositories.

The `buildspec.yml` file defines phases such as `install`, `pre_build`, `build` and `post_build`, plus artifacts, reports, cache paths and environment settings. Phase commands fail the build according to shell exit status and configured behavior. Test reports make unit or coverage results visible, while an artifact declaration selects what leaves the ephemeral environment. Never let a successful packaging command hide a failed test through careless shell chaining.

Use a CodeBuild service role with only the source, artifact, log, package and deployment-preparation permissions the project needs. Resolve credentials from **AWS Secrets Manager**, the managed secret lifecycle service, or **AWS Systems Manager Parameter Store**, the hierarchical configuration-value service, instead of plaintext environment variables. Masking a console display does not make a secret safe if a command prints it into logs or packages it into an artifact.

A build can attach to subnets and security groups in an **Amazon Virtual Private Cloud (Amazon VPC)**, the logically isolated network service, to reach a private database, internal package proxy or test endpoint. VPC-enabled builds do not receive a public IP address. If they also need public package sources, provide a route through a NAT device or replace internet dependencies with private endpoints and repositories. The CodeBuild role and the network path must both permit access.

Managed images reduce build-host maintenance, while a custom image supplies specialized toolchains. Pin the runtime and dependency versions required for reproducibility. Batch builds can fan out a build graph or matrix, and compute fleets can reduce start latency for sustained demand, but neither excuses tests that mutate a shared environment. Isolate test data and use unique build identifiers for concurrent execution.

Build reports and artifacts serve different readers. A report group retains structured test or coverage results for quality gates; an artifact contains the files a later stage deploys. Produce checksums, a software bill of materials or signing metadata when the supply-chain policy requires them, and keep those records tied to the source revision. A cache can accelerate compilation but must never be promoted as the authoritative application artifact.

## Deploy to EC2 and on-premises instances

For **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service, and on-premises instances, CodeDeploy uses an application, deployment group, revision and AppSpec file. The CodeDeploy agent on each target receives the revision and runs lifecycle hooks. The AppSpec file maps files to destinations and scripts to lifecycle events. A deployment group selects instances by tags or Auto Scaling groups, names its deployment configuration and can connect load balancers and alarms.

An in-place deployment updates the existing instances. Predefined configurations such as one-at-a-time, half-at-a-time and all-at-once express the minimum healthy-host behavior during the rollout. In-place is resource-efficient, but application availability falls if too many hosts are taken out of service, and rollback generally means deploying the earlier revision back onto the same fleet. It is unsuitable when the old and new runtime cannot safely share the host or when rollback must be an immediate traffic switch.

A blue/green EC2 deployment creates or identifies a replacement environment, installs the new revision there, optionally waits for validation, reroutes traffic and later terminates or retains the original instances. The original fleet remains a fast rollback target until it is terminated. Blue/green needs extra capacity and correct load-balancer health checks, but avoids partially modified hosts and supports an immutable-server pattern.

**Elastic Load Balancing**, the managed traffic distribution service, can deregister in-place targets during deployment or shift traffic between blue and green target groups. Deployment alarms can stop a bad rollout, and automatic rollback can redeploy the last known-good revision or return traffic according to the deployment type. An alarm based only on host health can miss business failures, so include request errors, latency and a deployment-specific synthetic check where appropriate.

Lifecycle hooks turn deployment into a testable state machine. A hook that exits unsuccessfully can fail the deployment before traffic reaches the revision, while validation hooks after installation or traffic shifting test the behavior users will receive. Give hook scripts timeouts, deterministic exit codes and bounded permissions. Keep diagnostics outside the replaced host when a failed blue/green environment may be terminated during cleanup.

## Shift Lambda and ECS traffic

For **AWS Lambda**, the serverless function service, CodeDeploy shifts an alias from one immutable function version to another. An all-at-once configuration moves all traffic immediately. A canary configuration moves a small percentage, waits, then moves the remainder. A linear configuration moves equal increments at intervals. Pre-traffic and post-traffic validation hooks are Lambda functions named in the AppSpec file. **Amazon CloudWatch**, the monitoring and observability service, alarms can stop and roll back the deployment by returning the alias to the previous version.

For **Amazon Elastic Container Service (Amazon ECS)**, the managed container orchestration service, CodeDeploy blue/green uses a replacement task set, two target groups and an optional test listener. It installs the new task definition in the green task set, can expose it to validation traffic, and shifts the production listener according to an all-at-once, canary or linear deployment configuration. After a successful wait period, it terminates the old task set. A rollback sends traffic back while the blue task set remains available.

The image itself belongs in **Amazon Elastic Container Registry (Amazon ECR)**, the managed container image registry. Identify it by an immutable digest or a controlled tag that resolves to the tested digest. Reusing a mutable `latest` tag can make the deployed bytes differ from the artifact the pipeline approved. Scan the image, sign or attest it where required, and carry its digest through promotion.

Lambda and ECS deployments do not use the CodeDeploy host agent. Their service control planes perform version or task-set traffic shifting. This distinguishes them from EC2 and on-premises deployments even when all three appear as CodeDeploy applications. It also explains why an EC2 one-at-a-time deployment configuration is not a valid Lambda canary answer.

## Select a deployment strategy and rollback

Choose a strategy from capacity, compatibility, validation time and rollback requirements. Read this table by what is updated and what remains available during failure.

| Strategy | How it changes capacity | Rollback shape | Strong fit |
|---|---|---|---|
| All at once | Updates or shifts all targets together | Redeploy or shift all traffic back | Dev/test or a service that tolerates a short outage and prioritizes speed |
| Rolling | Updates batches of the existing fleet | Redeploy batches; fleet may contain two versions | EC2 fleet with spare capacity and version compatibility |
| Rolling with additional batch | Adds temporary capacity before rolling | Redeploy while original capacity is preserved better | Elastic Beanstalk when full capacity must remain |
| Immutable | Launches a complete new instance set | Terminate new set and keep old environment | Elastic Beanstalk or an EC2 image change needing clean hosts |
| Blue/green | Builds a parallel environment and switches traffic | Switch traffic to the retained original | EC2 or ECS when fast rollback justifies duplicate capacity |
| Canary | Sends a small percentage first, then the remainder | Shift the canary traffic back | Lambda or ECS with sensitive production validation |
| Linear | Moves fixed increments on a schedule | Stop and return traffic to the old version | Lambda or ECS when exposure should grow gradually |

**AWS Elastic Beanstalk**, the managed application platform, offers all-at-once, rolling, rolling with an additional batch, immutable and traffic-splitting policies for its environments. ECS also has a native rolling deployment controller; CodeDeploy is selected when ECS blue/green traffic shifting and its hooks are required. Lambda aliases and CodeDeploy provide all-at-once, canary and linear shifting. EC2 CodeDeploy supports in-place and blue/green, while an Auto Scaling launch-template replacement can implement other immutable or instance-refresh patterns outside CodeDeploy.

Rollback is both technical and data-dependent. Repointing traffic cannot undo an incompatible database migration, remove an emitted event or restore overwritten customer data. Prefer backward-compatible expand-and-contract schema changes, feature flags and decoupled releases. Define which metrics stop the rollout, how long to observe a canary, who may override a gate and how to recover state. A pipeline that can deploy automatically but requires an improvised rollback is incomplete.

## CodeGuru and Proton lifecycle boundaries

**Amazon CodeGuru Reviewer** uses program analysis and machine learning to recommend improvements for supported Java and Python repositories. As of November 7, 2025, customers cannot create new repository associations; only existing associations continue. For new code-review integrations, AWS points to **Amazon Q Developer**, the AI software-development assistant, for security and quality review, and Amazon Inspector Code Security for repository vulnerability scanning. Preserve Reviewer only when the scenario explicitly starts with an existing association.

**Amazon CodeGuru Profiler** remains the runtime profiling service. Its agent collects performance data from supported JVM and Python applications and produces visualizations and recommendations for expensive code paths, CPU bottlenecks and heap behavior. Reviewer analyzes source changes; Profiler analyzes a running application's resource use. Neither replaces unit tests, deployment health alarms or infrastructure metrics.

**AWS Proton** is the platform-team service for publishing environment and service templates that provision infrastructure and delivery pipelines. It stopped accepting new customers after October 7, 2025 and reaches end of support on October 7, 2026. At end of support, the Proton console and resources become inaccessible and Proton data is deleted, but deployed CloudFormation stacks and their infrastructure remain running. Existing customers must migrate before the deadline.

AWS documents CloudFormation Git sync for a GitOps-style CloudFormation workflow, CodePipeline plus CodeBuild for flexible AWS-native CI/CD, and partner developer portals as Proton alternatives. Migration means inventorying templates and environments, extracting template data, reproducing the delivery and governance path, and testing updates from the replacement. Leaving deployed stacks running is not sufficient if no supported system can safely update them after Proton disappears.

## Professional depth

Use a tools account for pipeline orchestration and separate development, test and production accounts for workloads. A cross-account deployment action assumes a dedicated role in the target account; the tools account should not hold a universal organization administrator role. Artifact bucket and KMS policies must allow the target role to read the exact artifact, and production roles should trust only the intended pipeline role with conditions that prevent confused-deputy access.

Promotion and rebuilding are different designs. Promote the same signed artifact or image digest through environments when the requirement is proof that production received what testing approved. Rebuilding per account can accommodate environment-specific compilation but weakens that guarantee and increases supply-chain exposure. Put configuration outside the binary and inject it through controlled deployment parameters or runtime configuration.

Protect the pipeline itself with branch review, least-privilege roles, isolated build credentials, artifact encryption, dependency-origin policy and audit logging. A compromised build role can modify output even if source review is perfect. Treat build images, package repositories and third-party actions as production dependencies; pin versions and validate provenance. Do not expose production secrets to pull-request builds from untrusted branches.

Improve a slow or risky process by measuring queue time, build duration, flaky tests, change-failure rate, rollback time and approval delay. Parallelize independent tests, cache only reproducible inputs, use canaries for risk reduction and remove manual gates that add no decision value. Keep a manual or automated gate where evidence, segregation of duties or destructive impact demands it.

Design pipeline recovery as well as workload recovery. Version pipeline definitions and custom build images, replicate or rebuild source connections and artifact paths according to the recovery objective, and document how a deployment can proceed if the tools Region is unavailable. A multi-Region application with a single-Region delivery control plane can keep serving during an outage yet be unable to ship an urgent fix. Test the recovery procedure with a harmless revision rather than assuming infrastructure-as-code alone proves it.

## Worked scenario

A payments company deploys a Java API to ECS in three accounts. Source is hosted by an external Git provider, private Maven packages live in CodeArtifact, and images go to ECR. Production must receive the exact image tested in staging. Ten percent of traffic should reach the new task set first, with automatic rollback on payment-error or latency alarms. Production approval belongs to a team that cannot edit the pipeline.

The tools account runs CodePipeline with a CodeConnections source action. CodeBuild resolves locked dependencies from CodeArtifact, runs tests and builds one image, then records its immutable ECR digest in the artifact passed forward. Staging deploys that digest. After tests and a separately authorized manual approval, a cross-account CodeDeploy action creates an ECS green task set. A test listener exercises it, then a canary configuration moves ten percent of production traffic. CloudWatch alarms stop the deployment and return traffic to blue on failure. Roles, artifact bucket and KMS policies grant only the action-specific cross-account paths.

The exam asks for a repeatable multi-account pipeline with artifact integrity, gradual exposure and rapid rollback. The keyed answer is promote one immutable digest through CodePipeline, use least-privilege cross-account roles, and deploy ECS through CodeDeploy blue/green with canary traffic and alarms. Rebuilding the image in production or using an all-at-once update is the distractor.

## Exam lens

- "Orchestrate source, build, approval and deploy stages" maps to CodePipeline; it delegates execution to action providers.
- "Compile, test and package in disposable managed compute" maps to CodeBuild and a buildspec.
- "Private npm, Maven, pip or NuGet packages with upstream caching" maps to CodeArtifact; CodeCommit is source control.
- "Existing private Git repository hosted by AWS" maps to CodeCommit for an existing customer; a new customer must use another supported source.
- "Update the same EC2 instances in batches" maps to CodeDeploy in-place with a minimum-healthy-host configuration.
- "Provision a replacement EC2 fleet and switch traffic" maps to CodeDeploy blue/green; retain blue for fast rollback.
- "Shift ten percent of Lambda or ECS traffic before full release" maps to a CodeDeploy canary configuration.
- "Increase Lambda or ECS traffic by equal increments" maps to a linear deployment configuration.
- "Elastic Beanstalk full capacity during a batch rollout" maps to rolling with an additional batch; immutable builds an entirely new set.
- "Production must run the exact tested bytes" maps to promotion of an immutable artifact or image digest, not rebuilding per environment.
- "Rollback traffic after an incompatible database migration" is incomplete; application rollback does not reverse stateful schema or data changes.
- "New CodeGuru Reviewer association" maps to Amazon Q Developer or Inspector Code Security after November 7, 2025.
- "New Proton platform or use after October 7, 2026" maps to a supported replacement; existing deployed stacks survive but Proton management does not.
- "Build needs both private database and public packages" maps to VPC-attached CodeBuild plus a NAT path, or private endpoints and mirrored packages.

## Knowledge check

### 1. Moving a tested revision through environments (Associate)

A financial services company wants one managed workflow that carries a single source revision through a build, an integration test, a manual approval and a deployment. Each step must receive the named artifact that the previous step produced, and the exact revision that passed testing must be the one that reaches the deployment step. The company does not want to build and operate its own scheduler to sequence the steps.

Which solution will meet these requirements?

- **A)** AWS CodeArtifact
- **B)** AWS CodePipeline
- **C)** Amazon CodeGuru Profiler
- **D)** AWS CodeDeploy

<details><summary>Answer</summary>

**Answer: B.** CodePipeline coordinates ordered stages and passes artifacts between their actions. A stores versioned software packages and dependencies but does not orchestrate the delivery lifecycle. C profiles running application performance. D performs deployments for supported compute targets but does not replace the source, build, test and approval pipeline.

*Where this is covered: Build a pipeline from immutable artifacts.*

</details>

### 2. Building against a private test database (Associate)

A healthcare software team runs integration tests in an AWS CodeBuild project. The tests must reach a database that sits in private subnets and has no public endpoint, and the same build must still download approved dependencies that are only reachable outside that network. The security team requires that the database password never appear in a plaintext environment variable or in the repository, and that only the build itself be able to retrieve it.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Attach the build to suitable VPC subnets and security groups, with a NAT path or private endpoints for its other dependencies.
- **B)** Assign a public IP address directly to each VPC-enabled CodeBuild container.
- **C)** Put the database password in `buildspec.yml` so it is versioned with the tests.
- **D)** Resolve the credential from Secrets Manager or Parameter Store through a least-privilege build role.
- **E)** Grant the CodePipeline service role unrestricted database administrator permissions.

<details><summary>Answer</summary>

**Answer: A and D.** A supplies the private network path and an explicit path for required external or AWS services, while D keeps the credential outside source and limits retrieval to the build role. B is impossible because VPC-enabled builds do not receive public IP addresses. C exposes the secret in source. E gives the orchestration role excessive data-plane access and does not safely inject the credential into the build.

*Where this is covered: Compile and test with CodeBuild.*

</details>

### 3. Controlling private package dependencies (Associate)

A software company builds Java services with Maven. Its builds must resolve the company's internal libraries first and fall back to a supported public package source only for approved dependencies that are not already held internally. Once a version has been retrieved it must be retained so that later builds obtain the identical package even if the public source changes. Build accounts in several AWS accounts must share the same package storage under one policy.

Which solution will meet these requirements?

- **A)** AWS CodeCommit
- **B)** AWS CodeDeploy
- **C)** AWS CodeArtifact with a domain, repositories and an upstream or external connection
- **D)** Amazon CodeGuru Reviewer

<details><summary>Answer</summary>

**Answer: C.** CodeArtifact domains and repositories provide governed package storage, upstream search and supported public connections, with resource policies for cross-account access. A is a Git source repository, not a package registry, so it answers a different question entirely. B deploys application revisions but is not a package resolver. D analyzes supported source repositories and cannot host Maven packages.

*Where this is covered: Choose source control and package storage.*

</details>

### 4. Choosing an EC2 rollback model (Associate)

A retailer runs a web service on Amazon EC2 instances behind a load balancer. A new release must be installed only on freshly launched hosts, never on instances that already carry the previous release, and every replacement host must run the exact artifact that passed validation. If validation of the new release fails, traffic must return immediately to the unchanged previous fleet rather than wait for a redeployment onto those instances.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Use an all-at-once in-place deployment and terminate the old application files before testing.
- **B)** Use a CodeDeploy blue/green deployment with a replacement environment.
- **C)** Use CodeGuru Profiler to shift the load balancer listener after detecting CPU use.
- **D)** Rebuild the artifact independently on every replacement instance after approval.
- **E)** Retain the original environment until the green environment passes validation and the rollback period ends.

<details><summary>Answer</summary>

**Answer: B and E.** B creates clean green hosts and supports traffic rerouting, while E preserves blue as the rapid rollback target. A modifies the existing fleet and removes the unchanged target the scenario requires. C profiles code and is not a traffic deployment controller. D makes instance outputs potentially differ and violates immutable artifact promotion.

*Where this is covered: Deploy to EC2 and on-premises instances.*

</details>

### 5. Gradually deploying a Lambda version (Associate)

A media company publishes a new immutable version of an AWS Lambda function that sits behind an alias. The release team wants the alias to move an equal, fixed percentage of traffic to the new version at regular intervals rather than all at once, so that the change is observed as exposure grows. If an Amazon CloudWatch alarm on the function enters the `ALARM` state during the shift, all traffic must return to the previous version automatically.

Which solution will meet these requirements?

- **A)** An EC2 one-at-a-time deployment configuration
- **B)** A CodeBuild batch build with a shared cache
- **C)** A CodeArtifact upstream repository
- **D)** A CodeDeploy linear Lambda deployment configuration with automatic rollback alarms

<details><summary>Answer</summary>

**Answer: D.** A linear Lambda configuration moves equal traffic increments on a schedule, and CodeDeploy can use alarms to stop and restore the alias to the previous version. A applies to host deployments, not Lambda aliases. B changes build parallelism rather than production traffic. C resolves packages and has no deployment control.

*Where this is covered: Shift Lambda and ECS traffic.*

</details>

### 6. Preserving capacity during an Elastic Beanstalk rollout (Associate)

An online retailer runs its application in an AWS Elastic Beanstalk environment that is sized for peak traffic. During a release the environment must keep its full serving capacity while its instances are updated in batches, so no request is lost while a batch is out of service. The retailer can fund one extra batch of instances for the duration of the update but cannot fund a second complete environment.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Rolling with an additional batch
- **B)** All at once
- **C)** Immutable
- **D)** A Lambda canary deployment

<details><summary>Answer</summary>

**Answer: A.** Rolling with an additional batch adds temporary capacity before updating batches, preserving serving capacity without building a complete parallel fleet. B updates all existing instances together and can cause an outage. C creates a complete new instance set, exceeding the stated capacity budget. D applies to Lambda alias traffic and not an Elastic Beanstalk EC2 environment.

*Where this is covered: Select a deployment strategy and rollback.*

</details>

### 7. Replacing lifecycle-constrained developer services (Professional)

A company with no prior AWS footprint is designing its developer platform in September 2026. The draft design creates a new AWS CodeCommit repository as the source of record, associates that repository with Amazon CodeGuru Reviewer for automated code review, and standardizes on AWS Proton as the long-term portal for service templates. The company has no existing CodeCommit repository and no existing CodeGuru Reviewer association. The platform must use a source provider that accepts new customers, a code-review path that can still be enabled today, and a templating path that remains supported after October 2026.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** CodeCommit accepts all new customers, so no source-provider change is needed.
- **B)** New CodeGuru Reviewer associations remain the recommended code-quality path.
- **C)** Choose another supported Git provider because CodeCommit is closed to new customers.
- **D)** Keep Proton as the long-term control plane because support has no announced end date.
- **E)** Use current code-review alternatives and migrate the Proton design before its October 7, 2026 end of support.

<details><summary>Answer</summary>

**Answer: C and E.** C reflects CodeCommit's new-customer restriction. E combines the Reviewer association closure with Proton's imminent end of support and therefore replaces both constrained paths. A contradicts the CodeCommit banner, B contradicts the November 7, 2025 Reviewer restriction, and D contradicts Proton's announced end date.

*Where this is covered: CodeGuru and Proton lifecycle boundaries.*

</details>

### 8. Securing a multi-account production pipeline (Professional)

A payments company runs AWS CodePipeline in a central tools account and deploys one container image into separate staging and production accounts. Auditors must be able to prove that the bytes running in production are the same bytes that were tested in staging and then approved, with no rebuild taking place after that approval. The security team also requires that the pipeline never be able to assume administrator roles unrelated to the deployment action it is performing.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Rebuild the image in each production account from whatever dependency versions are current.
- **B)** Promote the same ECR image digest and signed pipeline artifact through every environment.
- **C)** Give the tools-account root principal full access to every production account.
- **D)** Use action-specific target roles whose trust, artifact bucket and KMS policies allow only the intended pipeline path.
- **E)** Store production credentials in the source repository so CodeBuild can assume any role.

<details><summary>Answer</summary>

**Answer: B and D.** B preserves artifact identity across testing and production, and D bounds cross-account access to the intended action and data path. A can produce different bytes and introduces fresh supply-chain risk after approval. C grants unrelated administrative authority rather than a deployment role. E exposes long-lived credentials and bypasses the controlled trust design.

*Where this is covered: Professional depth.*

</details>

## Summary

Use CodePipeline to coordinate immutable artifacts through source, build, test, approval and deployment actions. CodeBuild provides disposable build compute driven by a buildspec; keep secrets outside source and give VPC builds an explicit route to every dependency. CodeArtifact stores governed packages with upstream resolution, while CodeCommit remains usable only by existing customers. CodeDeploy updates EC2 or on-premises hosts in place or through blue/green replacement, shifts Lambda alias traffic, and creates ECS blue/green task sets. Choose all-at-once for speed and accepted interruption, rolling for bounded existing-fleet change, immutable or blue/green for clean replacement, canary for small initial exposure and linear for gradual increments. Preserve a known-good artifact and design stateful rollback separately. CodeGuru Reviewer accepts no new associations, though Profiler remains available. Proton stops on October 7, 2026, so existing users must migrate its management workflow even though deployed CloudFormation stacks remain. Across accounts, promote the same digest and use action-specific roles, artifact policies and monitored rollback gates.

## Related units

- [AWS CloudFormation](cloudformation.md): stack deployment actions, Git sync and infrastructure rollback behavior
- [Amazon CloudWatch](cloudwatch.md): deployment alarms, application health and pipeline metrics
- [AWS Systems Manager](systems-manager.md): controlled operational changes outside application delivery pipelines
- [Amazon ECS and Amazon ECR](../03-containers/ecs-and-ecr.md): task definitions, deployment controllers and image storage
- [AWS Lambda](../02-compute/lambda.md): versions, aliases and concurrency behind traffic shifting
- [AWS Elastic Beanstalk](../02-compute/elastic-beanstalk.md): platform-specific deployment policies and environment updates
- [AWS Identity and Access Management](../07-security/iam.md): cross-account roles, `iam:PassRole` and least privilege

## Sources

- [What is AWS CodePipeline?](https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html): pipeline orchestration and action providers
- [CodePipeline concepts](https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts.html): stages, actions, artifacts, executions and modes
- [CodePipeline pipeline structure](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipeline-requirements.html): run order and artifact stores
- [Stage conditions](https://docs.aws.amazon.com/codepipeline/latest/userguide/stage-conditions.html): entry, success and failure gates and results
- [CodePipeline cross-account actions](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-create-cross-account.html): target roles, artifact access and KMS policies
- [What is AWS CodeBuild?](https://docs.aws.amazon.com/codebuild/latest/userguide/welcome.html): managed build projects and environments
- [Build specification reference](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html): phases, artifacts, reports and parameter-store integration
- [CodeBuild VPC support](https://docs.aws.amazon.com/codebuild/latest/userguide/vpc-support.html): private resource access and internet routing
- [Build environment reference](https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref.html): managed and custom images and environment behavior
- [What is CodeDeploy?](https://docs.aws.amazon.com/codedeploy/latest/userguide/welcome.html): supported compute platforms and deployment objects
- [CodeDeploy deployment configurations](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html): EC2, Lambda and ECS rollout options
- [CodeDeploy deployment groups](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-groups.html): targets, load balancers, alarms and rollback
- [CodeDeploy AppSpec reference](https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file.html): files, hooks and platform-specific resources
- [Blue/green deployments with ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-bluegreen.html): task sets, target groups and listeners
- [Deploying Lambda applications](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-steps-lambda.html): aliases, traffic shifting and hooks
- [What is AWS CodeArtifact?](https://docs.aws.amazon.com/codeartifact/latest/ug/welcome.html): domains, repositories, formats and public sources
- [CodeArtifact upstream repositories](https://docs.aws.amazon.com/codeartifact/latest/ug/repos-upstream.html): dependency search order and retained packages
- [Package origin controls](https://docs.aws.amazon.com/codeartifact/latest/ug/package-origin-controls.html): controlling publishing and upstream ingestion
- [What is AWS CodeCommit?](https://docs.aws.amazon.com/codecommit/latest/userguide/welcome.html): private Git repositories, pull requests and IAM integration
- [AWS CodeCommit product page](https://aws.amazon.com/codecommit/): current closed-to-new-customers notice
- [CodeGuru Reviewer availability change](https://docs.aws.amazon.com/codeguru/latest/reviewer-ug/codeguru-reviewer-availability-change.html): November 7, 2025 association restriction and alternatives
- [What is CodeGuru Profiler?](https://docs.aws.amazon.com/codeguru/latest/profiler-ug/what-is-codeguru-profiler.html): runtime profiling and supported languages
- [AWS Proton deprecation and migration](https://docs.aws.amazon.com/proton/latest/userguide/proton-end-of-support.html): signup closure, October 7, 2026 end and alternatives
- [Elastic Beanstalk deployment policies](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.deploy-existing-version.html): all-at-once, rolling, additional batch, immutable and traffic splitting
- [CodeDeploy rollback and redeployment](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployments-rollback-and-redeploy.html): automatic rollback and prior revisions
