# AWS Migration Hub, discovery and migration strategy

**Where it sits on the exams.** **AWS Migration Hub**, the service for organizing discovery and tracking application migration progress, connects a portfolio view with work performed by migration tools. This unit owns SAP-C02 task 4.1's assessment, asset planning, wave planning, seven migration strategies and total cost of ownership decisions, and supports task 4.2's tool selection. No SAA-C03 task statement owns this material: an Associate reader needs only the vocabulary of the seven strategies, so that a question naming rehosting or replatforming is readable. **Migration Evaluator**, the migration business-case assessment service, is explicitly outside SAA-C03 scope. The rule of thumb is to assess applications and dependencies before scheduling servers, then choose the least disruptive strategy that meets the business outcome.

## Separate discovery, planning and migration execution

Migration is a business change implemented through infrastructure and application work. A server inventory answers what exists, an assessment asks what should happen to it, a wave plan decides when dependent changes occur, and execution moves and validates the workload. These are related stages with different evidence. A dashboard reporting that replication is complete does not prove that users can sign in, that a reporting job still works or that the original data center can be closed.

Migration Hub groups discovered servers into applications and collects migration status from integrated tools. Its home Region stores discovery and migration-tracking information for the account. That Region does not constrain the workload's destination: applications can migrate to Regions supported by the actual migration tool. Choose the home Region deliberately for the location of assessment data and coordinate discovery configuration with it. A team that looks in the wrong regional console can confuse missing visibility with a failed migration.

**AWS Application Discovery Service**, the service for collecting on-premises configuration and usage information, supplies discovery data. **AWS Database Migration Service (AWS DMS)**, the database data-movement service, performs database migration tasks rather than portfolio assessment. **AWS Application Migration Service**, the server replication service now documented as **AWS Transform MGN**, supports rehosting to **Amazon Elastic Compute Cloud (Amazon EC2)**, the virtual server service. Learn the exam-era service names and their responsibilities, then verify the current service and integration documentation before implementing a new project.

As of September 2026, Migration Hub and Application Discovery Service are closed to new customers following the November 7, 2025 availability change. The Migration Hub documentation also carries this notice for **Migration Hub Strategy Recommendations**, the assessment capability for identifying migration and modernization paths, and **Migration Hub Orchestrator**, the template-based migration workflow service. **Migration Hub Refactor Spaces**, the networking and routing service for incremental refactoring, carries its own new-customer closure notice, also dated November 7, 2025. None of the four has an announced end-of-support date, and AWS answers the question directly: the service continues to operate for existing customers. These notices do not establish that every existing customer's project has stopped. When an exam scenario starts with an established deployment, reason about its documented capabilities; when designing a new customer's platform, do not recommend signing up for a closed service.

**AWS Transform**, the service for assisted migration and modernization of infrastructure and applications, is the alternative AWS points new customers toward. Its current capabilities include discovery, dependency analysis, migration planning and supported server rehosting workflows. AWS states that Transform provides equivalent capabilities and that current Migration Hub features, including Strategy Recommendations and Orchestrator, are available there, and that moving to it requires no data migration. Transform is nonetheless a different product with its own console and workflow rather than a renamed Migration Hub, so check the source platform, supported transformation path, permissions and destination before selecting it for a real portfolio.

Keep responsibility visible in the plan. Assign a business owner who can accept the migrated application, a technical owner who understands dependencies, and an execution owner who manages the move. Record which service provides evidence for each milestone. Discovery data supports an assessment; a migration tool supplies replication and task status; application tests supply functional acceptance. Combining these views is useful, but replacing one with another can produce a technically green migration that has not delivered the required business service.

## Discover assets and validate application boundaries

Start with the inventory already available: configuration records, virtualization exports, application lists, license information and infrastructure ownership. For an existing eligible customer, Application Discovery Service also supports file-based import, useful when another tool has already collected the necessary data. An import does not create information that was absent from the source file. A spreadsheet listing allocated processors cannot establish peak utilization, running processes or network dependencies unless those facts were actually collected and included.

The **AWS Application Discovery Agent**, software installed on supported hosts, captures configuration, utilization, running processes and network connections. It can serve supported physical servers and virtual machines, and gives detail from within the operating system. Installing it needs the appropriate local privileges and a permitted connection to its service endpoints. Use this route when process-level evidence matters and the organization permits host software. Discovery is observation, however, not proof that every business dependency has been exercised during the collection period.

The **Application Discovery Service Agentless Collector**, a modular appliance deployed in a VMware vCenter environment, collects information without installing the Discovery Agent on every guest. Its VMware module supplies inventory and utilization information; other modules cover database and analytics discovery and network data. Do not generalize the limitations of the VMware inventory module to the entire collector. Current documentation includes a Network Data Collection module, so the old blanket claim that agentless discovery cannot collect any network connections is no longer a safe capability statement.

The network module uses the inventory from the VMware module and separately configured access to servers. Windows collection uses Windows Remote Management, and Linux collection uses Simple Network Management Protocol. Permissions, credentials and connectivity still matter: agentless does not mean credentialless or that a hypervisor inventory automatically includes every application conversation. Where process-level information is required, the Discovery Agent remains the clear documented fit. Check the exact collection module when a question distinguishes server metrics, network relationships and running processes.

Use observed connections to investigate application boundaries. A web tier talking to a database is one relationship; a shared identity service, batch scheduler, license server or file share can connect many applications. Validate the observed graph with application owners. A quiet system may run only at month end, and a connection may be an incidental monitoring interaction rather than a dependency that requires simultaneous cutover. Record the purpose, direction and timing of important relationships, and identify which can tolerate temporary operation across the old and new environments.

Collect representative utilization before sizing targets. Allocated capacity describes the source configuration, while measured demand shows how it is used. Include peaks, seasonal events and scheduled processing, and note gaps in the sample. Low processor usage does not mean low memory demand or low storage latency requirements. An apparently idle host may provide disaster recovery or an infrequent regulatory process. Treat a retirement candidate as a question for the owner and retention policy, not as permission to delete it based on one utilization chart.

The assessment record should attach evidence and uncertainty to each asset. Keep stable identifiers when names or addresses change, reconcile duplicates and distinguish a retired server from a failed collector. Record the collection date and scope so a later planner knows whether the information is still representative. Repeat discovery and owner validation as the portfolio evolves; a migration plan based on an old snapshot can miss a newly added dependency even if the original inventory was accurate.

## Select among the seven migration strategies

The seven Rs classify what changes during the move. They are choices per workload, not a maturity ranking that requires every application to end as microservices. This table separates the action from the business reason for choosing it.

| Strategy | What changes | Typical reason |
|---|---|---|
| Retire | Decommission an unneeded workload | Remove unused or duplicated capability |
| Retain | Keep it in the present environment for now | Unresolved dependency, restriction or weak migration value |
| Rehost | Move the application with minimal application change | Meet an exit deadline before later optimization |
| Relocate | Move an existing platform or workload placement with limited redesign | Preserve the operating model across a supported relocation path |
| Repurchase | Replace the application with another product | Adopt a suitable software-as-a-service offering |
| Replatform | Change the underlying platform with bounded application changes | Reduce operations while preserving the core design |
| Refactor or re-architect | Change application architecture substantially | Meet requirements the existing design cannot satisfy |

Rehost is often appropriate when the immediate objective is to leave a facility and the current application already satisfies functional needs. Moving server workloads to EC2 can reduce the scope of application change before cutover. It does not remove the need to validate operating-system support, licensing, network behavior and the target's performance. It also does not automatically optimize costs: reproducing every oversized server and always-on development environment can reproduce the source estate's inefficiency in a new billing model.

Replatform changes how part of the application is operated while retaining its main structure. For example, moving a supported database engine to **Amazon Relational Database Service (Amazon RDS)**, the managed relational database service, can transfer routine database infrastructure management to AWS. Verify engine features and operational requirements before assuming compatibility. Refactor is appropriate when the requirement instead calls for independently deployable components, a different data model or an architectural change that a hosting move cannot supply. Both can improve operations, but they have different testing and delivery risks.

Repurchase replaces functionality with a different product, commonly software as a service (SaaS). Moving user data, integrating identity, training users and retiring the former application are still part of the migration. Relocate preserves more of an existing platform or placement model than a redesign. Do not confuse it with repurchase just because a vendor contract changes, or assume that every historically advertised virtualization offering remains available to new customers. The strategy is a conceptual classification; the current target platform and commercial path must also be supported.

Retain and retire are legitimate decisions in a complete portfolio. Retain should have a reason and a review condition, such as resolving a specialized hardware dependency or reaching a contract renewal. Retire should include owner approval, dependency checks, data-retention handling and evidence that the service is no longer required. An application can be low usage but essential. Conversely, moving a duplicate reporting server merely to make the migration count larger adds expense without meeting a business need.

Use constraints to decide, then document why nearby alternatives fail. A fixed exit date may favor rehost now and refactor later; a mandatory feature that the old architecture cannot deliver may justify refactoring first. A supported managed database can make replatforming reasonable, but an incompatible extension can invalidate that choice. Avoid blanket rules such as every unsupported system should be replatformed or every refactor will lower total cost. A strategy recommendation is a hypothesis to validate against the actual workload, deadline and operating team.

## Assess the portfolio and build an actionable wave plan

A portfolio assessment combines business importance, technical evidence and migration feasibility. For each application, record its owner, users, criticality, service expectations, data classification, source components, dependencies and preferred target. Add the proposed R, rationale, blockers, testing requirements and the confidence of the estimate. Asset planning then makes that choice executable. Decide the target account and Region for each application, the instance or service sizes its measured demand justifies, and the storage and network paths it needs on arrival. Resolve licensing before the wave rather than during it: some licenses are tied to physical cores or specific hosts and constrain the tenancy or instance family available. Name the owner accountable for each asset at cutover and the operational team that holds it afterwards, because an asset with no named owner reliably stalls its wave. Record which assets are shared across applications, since those force either a coordinated move or a temporary hybrid dependency. The output is a target design per application, not a list of server names beside a migration label.

Perform deeper assessment for applications approaching execution. The broad portfolio view identifies candidates and priorities; an application deep dive resolves details such as authentication, scheduled jobs, external integrations, backup restoration and cutover sequencing. Validate the proposed target with representative tests. A recommendation based only on processor utilization cannot establish whether a licensed product supports a managed database, or whether clients can tolerate the delay of a temporarily remote dependency.

Maintain one authoritative metadata store and a defined update process. Record who owns each attribute and which source supports it. A collector is a suitable source for observed utilization, while an application owner must confirm business criticality and acceptable outage. Uncontrolled copies of a wave spreadsheet quickly diverge when an owner changes a date or a test reveals a new dependency. Preserve change history and make unresolved assumptions visible so the migration team does not mistake an empty field for an approved decision.

A move group is a set of dependent servers or applications intended to move together. A migration wave contains one or more move groups scheduled within the team's delivery capacity. Group by validated dependencies and cutover constraints, then consider business priority and similarity of migration pattern. Sorting all servers alphabetically or filling a fixed server quota per week can separate a tightly coupled application from its database. Moving everything together avoids some dependencies but can create an unmanageable cutover and recovery event.

Start with a bounded pilot that exercises the migration pattern and operating process without exposing the most critical workload first. The purpose is to learn about replication, target configuration, testing, handover and recovery before expanding. A pilot that avoids every representative dependency can produce false confidence. Use its findings to improve the runbook and estimate achievable throughput. Later waves can grow in complexity as the team demonstrates reliable execution, rather than assuming that the initial schedule is a proven capacity limit.

Capacity includes people and acceptance work as well as transfer bandwidth. Database specialists, application testers, security reviewers and business approvers can each constrain the wave. Check blackout dates, reporting cycles and support availability before reserving the cutover window. Give each wave entry criteria, such as validated connectivity and completed rehearsals, and exit criteria, such as owner acceptance and operational handover. Maintain a pipeline of assessed future candidates without freezing the entire remaining portfolio into an inflexible calendar.

When dependencies cannot move together, design the interim state explicitly. Verify latency, routing, identity and data consistency across the boundary and assign an owner to each temporary arrangement. Decide what evidence permits the next wave to proceed. Reassess the plan when the source changes, an application fails a test or a business priority shifts. The migration workstream executes the wave; the portfolio workstream continually supplies validated candidates and revised sequencing. Wave planning is therefore a repeated control process, not a one-time diagram.

## Use recommendations, orchestration and incremental refactoring appropriately

Strategy Recommendations combines technical analysis with business preferences. It can inspect inventory, runtime information and supported application binaries, and use configured source and database analysis to identify incompatibilities and anti-patterns. Its value is narrowing options and exposing work needed for a target. It does not certify that every recommended path will meet the application's availability, functional or cost requirements without additional validation.

Use a recommendation as an assessment input. Investigate the reported blocker, establish whether it affects the chosen path, and test the proposed change with the application owner. A rehost recommendation may fit an urgent exit but leave a modernization goal unresolved. A refactor recommendation may fit the long-term architecture but be impossible within the current cutover window. Record the accepted strategy separately from the tool's candidate recommendation so future reviewers can see the business judgment and evidence behind the decision.

Orchestrator coordinates supported migration steps and exposes their status. A workflow consists of step groups and steps derived from a template, with supported customization. Templates can sequence activities such as prerequisite checks, target setup, migration, validation and cutover. Their scope and prerequisites differ by migration pattern. Orchestrator is not a universal replication engine that replaces the tools used by those steps, and a completed automation step is not a substitute for the business acceptance test assigned to the workload.

Choose a template that matches the source and target, then inspect permissions, connectivity, any required plugin and the actions the template performs. Document manual steps and approvals alongside automated ones. Recovery needs to account for steps that already changed state, not simply restart the workflow from the beginning. The service supports modifying user-added step groups and steps within its documented restrictions; do not assume every predefined step can be rewritten freely. Rehearse the customized process before applying it to a critical application.

Refactor Spaces supports a strangler-fig approach: expose an application endpoint and gradually route selected functionality to new services while legacy functionality remains. An environment supplies the shared networking context; an application contains services and routes. A service represents a reachable implementation, and routes decide which implementation receives a request. This lets teams separate the migration of individual capabilities from an immediate replacement of the entire application.

Refactor Spaces orchestrates resources including **Amazon API Gateway**, the managed application interface service, with its VPC links, a **Network Load Balancer**, the transport-layer load balancer, and **AWS Transit Gateway**, the network transit hub, with supporting access policies. New services can use supported web endpoints or **AWS Lambda**, the serverless function service. Routing requests does not rewrite application code, split a shared database or make two implementations transactionally consistent. Those design problems remain with the application team. Preserve authorization behavior and client contracts, and test routing changes before shifting business traffic.

These tools address different questions. Strategy Recommendations asks which changes may be viable; Orchestrator sequences supported migration work; Refactor Spaces supplies infrastructure for gradual routing during modernization. A status dashboard supplies visibility across the effort. Their similar product names do not make them interchangeable. For new customers, evaluate currently supported alternatives such as Transform for the required capability rather than treating a legacy service's documentation tutorial as proof that new enrollment is available.

## Compare total cost and protect the assessment data

Total cost of ownership (TCO) compares the resources required to deliver an equivalent workload over a stated period. Start with the current environment and a defined future architecture, using the same scope and comparable availability and performance. Include compute, storage, networking, licenses, support and operations as appropriate. Distinguish allocated source capacity from measured demand, and distinguish an estimate based on partial information from a validated target design. A spreadsheet with precise currency values is still uncertain if its assumptions are untested.

Migration Evaluator helps create a directional business case using inventory and utilization data, either supplied from existing records or gathered through its collection process. It models AWS costs and licensing scenarios and provides assessment outputs to inform planning. AWS describes the service as complimentary; that does not mean the migration or target resources are free. Its role is business-case analysis, not executing a cutover or guaranteeing savings. This deeper cost-assessment service is relevant to Professional preparation but explicitly outside the Associate exam's service scope.

Separate recurring cost from transition cost. During migration, both environments may run while replication, testing and acceptance occur. Include delivery labor, training, data movement, temporary infrastructure and contract exit costs where they apply. Savings from shutting down a data center do not begin merely because one application has moved if the facility contract and shared services remain. Track when each cost can actually be removed. Compare cash timing as well as the steady-state run rate so a cheaper future platform does not conceal an unaffordable transition.

Right-size from representative demand while preserving headroom and resilience. Compare licensing models only after checking the product's terms and target support; a technical migration path is not proof that a license transfers. Evaluate commitment discounts against a sufficiently understood steady-state workload rather than purchasing a long commitment for capacity that a later wave will retire. Model sensitivity to uncertain inputs such as growth, storage retention, utilization and migration duration. Show which assumptions can reverse the recommendation, and assign owners to validate the material ones.

Keep business benefits distinguishable from guaranteed cash savings. Reduced maintenance effort may free staff for other work without reducing payroll. Better recovery or faster releases can have substantial value, but should not be counted twice as both direct cost reduction and another benefit without a clear method. Compare retire, retain, rehost, replatform and repurchase options where relevant rather than presenting a single favored design as the only alternative. Revisit the case as actual migration costs and target utilization become available.

Discovery information also needs protection. Inventories, process command lines and network relationships can reveal sensitive architecture and operational details. **AWS Identity and Access Management (IAM)**, the authorization service, separates collection, assessment and execution permissions. Use the minimum access required for collectors and restrict exports to authorized teams. Discovery Agent communication uses Transport Layer Security (TLS) to protect transmission, but encryption does not replace decisions about who may view or retain the resulting data. Remove unnecessary collection credentials and access when their purpose ends.

Price the chosen tool path rather than assuming the Migration Hub name makes the entire process free. Core discovery and tracking, optional capabilities and provisioned resources have different charging boundaries. Refactor Spaces, for example, has service charges as well as charges for resources provisioned in the customer's account. Confirm the current pricing and supported enrollment for the specific component, then include target workloads and temporary coexistence in the estimate. A low assessment-tool bill says little about the total cost of delivering the migration.

## Professional depth

Multi-account migration planning needs a target operating model before the first large wave. Decide which team owns account provisioning, identity, networking, logging and recovery, and make these dependencies explicit in the wave entry criteria. A source application may fit one account while its new database, security tooling or shared network belongs elsewhere. Test the application path across those boundaries with the intended workload identities. An administrator's successful connectivity test is not proof that the production role has the required access.

Separate completion milestones so progress remains meaningful. Discovered, assessed, replication-ready, tested, cut over, accepted and decommissioned describe different states. Define the evidence and responsible owner for each, and preserve exception records. A portfolio can contain many migrated servers while the data center remains indispensable because a shared service has not moved. Report the remaining business dependencies alongside server counts and reconcile tool status with owner acceptance before declaring an application complete.

Plan rollback around data ownership. Before target writes begin, rollback may be primarily a traffic and execution decision. After both environments have accepted changes, returning users to the source requires a data-reconciliation design, not just reversing a route. Specify the decision deadline, acceptable data loss, recovery time and who can authorize the change. Rehearse a failed cutover and verify that monitoring, credentials and staff are available during the actual window. The orchestration tool can sequence steps but cannot invent a safe reconciliation policy.

For incremental refactoring, define which component owns each business operation and data update during coexistence. Routing only one endpoint to a new service can still leave authentication, transaction boundaries or asynchronous processing coupled to the monolith. Validate those contracts before describing the service as independent. Keep a clear record of which paths remain on the old implementation and what evidence permits its retirement. Otherwise an incremental modernization program can accumulate permanent duplicate infrastructure without completing the intended replacement.

Treat lifecycle changes as portfolio risks. A team already using Migration Hub can assess continuity for its existing work, while a new project must evaluate supported onboarding and future operations. Preserve exportable assessment evidence, runbooks and strategy decisions so they are not understandable only inside one product. Validate Transform or another supported tool against representative workloads before committing the entire portfolio to it. The goal is repeatable, auditable migration capability, and tool selection is one part of that capability.

## Worked scenario

A manufacturer must leave a leased facility while keeping a production-ordering application available. Its inventory contains an ordering web tier, a database, a shared identity service, an apparently idle reporting server and a factory controller tied to specialized hardware. The business wants lower operating effort later, but cannot fund a complete application rewrite before the exit. The company is an existing Migration Hub customer with discovery data already collected.

The team reconciles the inventory with application owners and observes a representative operating period. It learns that the reporting server runs a required periodic process, so low average utilization is not evidence for retirement. The controller is retained with an explicit connectivity plan. The ordering tiers form a move group because their latency and consistency requirements make an untested split risky. Rehosting meets the immediate deadline; database replatforming is assessed as a later change after compatibility testing. A pilot validates the runbook and target foundation before the production wave.

Migration Hub provides the portfolio view while the execution tools perform their assigned transfers. The wave cannot proceed until connectivity, tests, recovery procedures and owners are ready. The cost case includes temporary coexistence, retained factory connectivity and the date the facility expense can actually end. The exam asks for a low-risk strategy under a fixed deadline: choose evidence-based grouping and a tested rehost wave, with later modernization and explicit retained dependencies. A full rewrite before the deadline, retiring the quiet reporting server or scheduling each server independently are distractors because they ignore the stated constraints.

## Exam lens

- "One view of application migration progress" maps to Migration Hub for an eligible existing customer.
- "Migration Hub home Region" identifies discovery and tracking storage, not a mandatory workload destination.
- "Processes and network connections on supported physical hosts" maps to the Discovery Agent.
- "Avoid an agent on every VMware guest" suggests an appropriately configured Agentless Collector.
- "Agentless network dependency information" requires checking the collector module, not assuming it is impossible.
- "A fixed exit deadline with minimal application change" often maps to rehost and later optimization.
- "Managed platform with the core application preserved" maps to replatform.
- "Replace the application with a SaaS product" maps to repurchase.
- "No longer needed" suggests retire after dependency and retention validation; low utilization alone is insufficient.
- "Cannot move yet" maps to retain with a reason and review condition.
- "Group tightly coupled components" maps to move groups and dependency-aware waves.
- "Recommend viable modernization paths" maps to Strategy Recommendations, not proof of application acceptance.
- "Sequence a supported migration workflow" maps to Orchestrator.
- "Gradually route functionality away from a monolith" maps to the strangler-fig pattern and, for existing eligible users, Refactor Spaces.
- "Compare migration economics" requires TCO and transition costs, not just target compute prices.
- "A new customer starts discovery today" requires a supported service such as Transform rather than new enrollment in closed legacy services.

## Knowledge check

### 1. Meeting an exit deadline (Associate)

A company must leave a leased data center before its contract expires. Its application already meets current functional requirements, and there is insufficient time to redesign and retest its architecture before the exit. The team wants to preserve the option of modernizing after the move.

Which solution will meet these requirements?

- **A)** Refactor every component into independently deployable services before migrating any production traffic.
- **B)** Rehost the supported application stack, validate it in AWS, and schedule modernization separately.
- **C)** Retain the entire stack in the leased facility until the team completes a redesign.
- **D)** Repurchase a replacement application that requires redesigning the company's core business workflows before adoption.

<details><summary>Answer</summary>

**Answer: B.** Rehosting limits application change before the fixed exit while leaving later optimization possible. It still requires compatibility checks and application testing. A adds an architectural change that the scenario says cannot be completed in time. C misses the required facility exit. D could be appropriate for a different business objective, but its mandatory workflow redesign introduces work the current schedule cannot accommodate. The decisive constraint is the deadline combined with an already adequate application.

*Where this is covered: Select among the seven migration strategies.*

</details>

### 2. Investigating physical-server dependencies (Associate)

An existing Application Discovery Service customer is assessing supported physical Windows and Linux servers. The team needs operating-system process information as well as performance and network connections. Installing approved discovery software on those hosts is permitted.

Which solution will meet these requirements?

- **A)** Import a spreadsheet containing only hostnames and allocated processor counts.
- **B)** Use the VMware inventory module without access to the physical hosts.
- **C)** Deploy the Discovery Agent on the supported servers and validate the resulting dependency evidence with owners.
- **D)** Use migration task completion reports as the sole source of process and dependency information.

<details><summary>Answer</summary>

**Answer: C.** The Discovery Agent collects the required host-level information, including running processes, on supported physical systems. Owner validation adds the business meaning that technical observations alone cannot establish. A imports only the supplied fields and cannot infer missing observations. B targets a VMware inventory and does not provide the requested process view of these physical servers. D describes execution progress rather than the source workload's observed processes and connections. Existing-customer eligibility is explicit in the scenario.

*Where this is covered: Discover assets and validate application boundaries.*

</details>

### 3. Distinguishing platform change from replacement (Associate)

A team wants to move a supported database to a managed service while preserving the application's core structure. Compatibility testing confirms that the required database features are supported by Amazon RDS. The team wants to reduce database infrastructure maintenance without replacing the business application.

Which solution will meet these requirements?

- **A)** Replatform the database to RDS and validate the existing application's behavior against the managed target.
- **B)** Rehost the same self-managed database configuration on EC2 as the final design.
- **C)** Repurchase a different business application and migrate the users to its workflows.
- **D)** Retire the application and archive its database.

<details><summary>Answer</summary>

**Answer: A.** Replatforming changes the operating platform while preserving the main application design, and the scenario has already established the required compatibility. B can move the workload but keeps the database infrastructure maintenance that the team wants to reduce. C replaces the application rather than preserving it. D removes the active business capability entirely. The classification follows the change being made, not merely the fact that a database is moving to AWS.

*Where this is covered: Select among the seven migration strategies.*

</details>

### 4. Handling a quiet but potentially important workload (Associate)

Discovery shows low average activity on a reporting server. Its business owner has not yet confirmed whether it performs a periodic regulatory process, and a downstream application's relationship to it is unclear. The migration team wants to avoid unnecessary migration expense without interrupting required reporting.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Retire the server immediately because its average utilization is low.
- **B)** Refactor the reporting application before establishing whether the business still needs it.
- **C)** Use allocated processor capacity alone to decide whether the reporting function is required.
- **D)** Validate business usage, dependency timing and retention obligations with the responsible owners.
- **E)** Record the unresolved dependency and retain the workload pending an evidence-based retire or migrate decision.

<details><summary>Answer</summary>

**Answer: D and E.** D establishes whether the workload is required, while E prevents an irreversible decision based on incomplete evidence. Retain should have a review condition rather than become an unexplained permanent exception. A equates a low average with no business value. B spends modernization effort before confirming the need. C measures provisioned hardware, not business usage or required reporting. None of those three alternatives resolves the uncertainty that matters to the stated continuity requirement.

*Where this is covered: Discover assets and validate application boundaries.*

</details>

### 5. Separating tracking location from deployment location (Associate)

An existing Migration Hub customer stores portfolio tracking data in its chosen home Region. Business requirements place one application in a different Region that the selected migration tool supports. The team needs a consolidated portfolio view throughout the move.

Which solution will meet these requirements?

- **A)** Move the application to the home Region regardless of the business requirement.
- **B)** Create an unrelated tracking process solely because the target differs from the home Region.
- **C)** Change the home Region before every application cutover.
- **D)** Keep the portfolio tracking in the home Region and migrate the application to the supported destination Region.

<details><summary>Answer</summary>

**Answer: D.** The home Region holds discovery and tracking information; it does not force all migrated workloads into that Region. A imposes a restriction that the service does not require and violates the destination requirement. B fragments the requested portfolio view without a technical need. C adds repeated tracking reconfiguration without changing the migration tool's supported destinations. The architect must distinguish the location of assessment metadata from the location where the application will run.

*Where this is covered: Separate discovery, planning and migration execution.*

</details>

### 6. Planning a production wave (Professional)

A migration program has several application tiers sharing a database and identity services. A pilot has exposed a limited number of available testers and a monthly business blackout period. Leadership wants a predictable production wave without separating components whose cross-environment behavior has not been validated.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Assign every server to a week based only on the alphabetical order of its hostname.
- **B)** Define move groups from validated application dependencies and design any necessary interim connections.
- **C)** Schedule the entire remaining portfolio in the same cutover window to eliminate all temporary dependencies.
- **D)** Size and schedule waves against delivery and acceptance capacity, blackout dates and explicit readiness criteria.
- **E)** Treat successful replication as sufficient evidence for business acceptance and remove application testing from the wave plan.

<details><summary>Answer</summary>

**Answer: B and D.** B preserves the dependency reasoning needed to avoid an untested application split. D includes the human and business constraints that determine whether the wave can finish safely. A ignores application relationships. C turns all remaining work into one large event and exceeds the demonstrated acceptance capacity. E confuses data-transfer progress with application functionality. A useful wave plan must be executable by the available team and must establish what evidence permits cutover and completion.

*Where this is covered: Assess the portfolio and build an actionable wave plan.*

</details>

### 7. Modernizing incrementally (Professional)

An existing Refactor Spaces customer wants to replace selected capabilities in a monolith while preserving its external application endpoint. New implementations are being built in separate accounts, and the legacy application must continue handling functionality that has not yet moved. The application team remains responsible for data consistency and business logic.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Use Strategy Recommendations as the runtime request router for the application.
- **B)** Use Orchestrator completion status to determine where every incoming client request is forwarded.
- **C)** Use a Refactor Spaces environment, application, services and routes to shift selected functionality incrementally.
- **D)** Build and operate a custom cross-account proxy and networking control system with equivalent routing behavior.

<details><summary>Answer</summary>

**Answer: C.** Refactor Spaces supplies the networking and routing foundation for the stated incremental refactoring pattern, and the scenario establishes existing eligibility. A is an assessment capability, not a runtime routing system. B sequences migration work rather than serving client traffic. D could implement routing but requires operating a custom version of infrastructure the service manages. The managed routing does not remove the team's responsibility for code, authorization contracts or consistency between old and new implementations.

*Where this is covered: Use recommendations, orchestration and incremental refactoring appropriately.*

</details>

### 8. Evaluating the migration business case (Professional)

A company compares its current estate with a proposed AWS deployment. The initial estimate copies all allocated server capacity, counts facility savings from the first migrated application and excludes the period when both environments will run. Finance needs a defensible comparison before approving the migration program.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Use representative demand and comparable service requirements to model target capacity and test sensitivity to uncertain assumptions.
- **B)** Compare only the advertised target compute rate with the current hardware purchase price.
- **C)** Treat a complimentary Migration Evaluator assessment as evidence that migration execution has no cost.
- **D)** Count all freed staff time as immediate payroll reduction without confirming an actual cost change.
- **E)** Include transition and coexistence costs and remove current expenses only when contracts and retained dependencies permit them to end.

<details><summary>Answer</summary>

**Answer: A and E.** A makes the target estimate reflect measured needs and equivalent service expectations rather than blindly copied allocations. E corrects the timing and scope of migration costs and savings. B compares incomplete and differently timed cost categories. C confuses the assessment service's price with implementation and resource costs. D turns a potential productivity benefit into an unsupported cash-saving claim. A defensible business case exposes assumptions and distinguishes steady-state economics from the cost of reaching that state.

*Where this is covered: Compare total cost and protect the assessment data.*

</details>

## Summary

Assess an application as a business capability with owners, dependencies and acceptance criteria, rather than treating it as an isolated server. Discovery agents, collector modules and imports provide different evidence, and the collection method must match the required detail. Choose among the seven Rs from the deadline, compatibility, business value and desired operating model. Translate the chosen strategy into asset requirements, move groups and waves sized for both technical delivery and business acceptance. Migration Hub supplies tracking, Strategy Recommendations informs viable paths, Orchestrator sequences supported work, and Refactor Spaces supports incremental routing for eligible existing customers. New customers must evaluate supported alternatives such as AWS Transform because the legacy services have enrollment restrictions. Compare equivalent workloads using representative utilization, transition costs and realistic timing for savings. Keep assessment data protected and decisions exportable. Rehearse cutover and recovery, and distinguish replication completion from application acceptance and eventual source decommissioning before claiming that the migration has delivered its intended outcome.

## Related units

- [Application Migration Service](application-migration-service.md): replication, testing and server cutover
- [DMS and Schema Conversion Tool](dms-and-sct.md): database transfer and engine conversion decisions
- [Hybrid connectivity](../04-networking/hybrid-connectivity.md): interim connections and hybrid dependencies
- [Cost management](../08-management/cost-management.md): cost allocation, commitment and optimization decisions
- [Backup and disaster recovery](../01-storage/backup-and-disaster-recovery.md): recovery objectives and rehearsal
- [Organizations, Identity Center and Control Tower](../07-security/organizations-identity-center-and-control-tower.md): the target account and governance foundation
- [Amazon RDS](../05-database/rds.md): managed database platform capabilities and constraints

## Sources

- [What is Migration Hub?](https://docs.aws.amazon.com/migrationhub/latest/ug/whatishub.html): tracking, integrations and new-customer notice
- [Migration Hub home Region](https://docs.aws.amazon.com/migrationhub/latest/ug/home-region.html): metadata location versus workload destination
- [Application Discovery Service overview](https://docs.aws.amazon.com/application-discovery/latest/userguide/what-is-appdiscovery.html): agents, collectors and imports
- [Discovery Agent](https://docs.aws.amazon.com/application-discovery/latest/userguide/discovery-agent.html): host detail, local privileges and encrypted transmission
- [Agentless Collector](https://docs.aws.amazon.com/application-discovery/latest/userguide/agentless-collector.html): modular collection and VMware deployment
- [Network Data Collection module](https://docs.aws.amazon.com/application-discovery/latest/userguide/network-data-module-setup.html): separate network module and access requirements
- [Application Discovery Service availability change](https://docs.aws.amazon.com/application-discovery/latest/userguide/application-discovery-service-availability-change.html): new-customer closure and Transform transition
- [What is AWS Transform?](https://docs.aws.amazon.com/transform/latest/userguide/what-is-service.html): current migration and modernization capabilities
- [Migration strategies](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html): the seven Rs and current Transform MGN terminology
- [Application portfolio assessment guide](https://docs.aws.amazon.com/prescriptive-guidance/latest/application-portfolio-assessment-guide/introduction.html): iterative discovery, assessment and planning
- [Initial assessment data requirements](https://docs.aws.amazon.com/prescriptive-guidance/latest/application-portfolio-assessment-guide/understanding-initial-assessment-data-requirements.html): evidence for application assessment and cost modeling
- [Metadata processes](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-portfolio-playbook/metadata.html): attribute ownership, sources and a shared metadata store
- [Wave planning process](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-portfolio-playbook/wave-planning.html): move groups, constraints and iterative wave planning
- [Strategy Recommendations](https://docs.aws.amazon.com/migrationhub-strategy/latest/userguide/what-is-mhub-strategy.html): technical assessment and candidate strategies
- [Migration Hub Orchestrator](https://docs.aws.amazon.com/migrationhub-orchestrator/latest/userguide/what-is-migrationhub-orchestrator.html): supported template-based migration roles
- [Orchestrator workflows](https://docs.aws.amazon.com/migrationhub-orchestrator/latest/userguide/migration-workflows.html): step groups, customization and restrictions
- [Refactor Spaces](https://docs.aws.amazon.com/migrationhub-refactor-spaces/latest/userguide/what-is-mhub-refactor-spaces.html): incremental modernization, new-customer closure notice and charging boundaries
- [Refactor Spaces concepts](https://docs.aws.amazon.com/migrationhub-refactor-spaces/latest/userguide/welcome-concepts.html): environments, applications, services and routes
- [Directional business case](https://docs.aws.amazon.com/prescriptive-guidance/latest/application-portfolio-assessment-guide/directional-business-case.html): comparable workloads, transition costs and assessment uncertainty
- [Migration Evaluator features](https://aws.amazon.com/migration-evaluator/features/): inventory, utilization and business-case outputs
- [Migration Evaluator pricing](https://aws.amazon.com/migration-evaluator/pricing/): complimentary assessment scope
- [Refactor Spaces pricing](https://docs.aws.amazon.com/migrationhub-refactor-spaces/latest/userguide/what-is-mhub-refactor-spaces.html#what-is-pricing): usage hours, API requests and provisioned-resource charges
