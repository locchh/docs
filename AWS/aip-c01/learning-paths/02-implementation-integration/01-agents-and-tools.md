# Unit 01: Agents and tools

**Task 2.1: Implement agentic AI solutions and tool integrations.** This unit is about building agents that remember, reason and call tools without running away: the managed services (**Bedrock Agents** and **AgentCore**), the open-source frameworks the exam names (**Strands Agents**, **Agent Squad** and **MCP**), **Step Functions** for deterministic reasoning and human review, and the safeguards and validation that keep an autonomous loop under control.

This is the largest unit in Domain 2 and the one most affected by product changes since the exam guide was written, so it separates what the exam expects from what AWS now recommends.

## What an agent is

A chat model answers. An **agent** acts. Given a goal, an **agent** runs a loop:

1. It reasons about what to do next.
2. It picks a **tool**, such as an API, a database query, a search or a calculation, and calls it.
3. It reads the result and reasons again. The loop continues until the goal is met or the **agent** decides to ask the user something.

This loop is called **ReAct**, short for reason and act. Each step produces a *thought*, an *action* with its parameters, and an *observation* from the **tool**. **Chain-of-thought** is the reasoning half on its own: it asks the model to work through intermediate steps before answering.

Three more concepts complete the vocabulary:

- **Memory** has two layers. **Short-term memory** is the running conversation within a session. **Long-term memory** is what the **agent** keeps across sessions, such as preferences, facts and summaries of past interactions.
- **Tool definitions** describe each **tool** to the model in a machine-readable schema. The schema supplies a name, description and typed parameters so the model can decide when to call the **tool** and with what arguments. The application, never the model, executes the call.
- **Multi-agent systems** split a big job among specialized **agents**, usually with a **supervisor** that routes work and merges results.

## Amazon Bedrock Agents: what the exam expects

The exam guide names **Amazon Bedrock Agents**, the managed agent service inside **Bedrock**, and most agent questions are written against it. You configure an agent from parts:

- A **foundation model** and **instructions** (what the agent is for, its tone, its limits).
- **Action groups**, each defined by either an **OpenAPI schema** or *function details* (name, description, parameters). When the model decides to call an action, **Bedrock** either invokes the **Lambda function** you attached to the group or, with **return of control**, hands the parameters back to your application in the `InvokeAgent` response so your code performs the call and sends the result back in the next request.
- **Knowledge bases** the agent can query for context (unit 04 of Domain 1).
- **Guardrails** applied to inputs and outputs.
- **Memory**: by default an agent remembers within a session identified by your `sessionId`; enabling memory stores summaries per user under a `memoryId` for a retention period you set, so context survives across sessions. Two request-level fields also carry state: `sessionAttributes` persist across the turns of a session and are passed to action-group **Lambda functions**, and `promptSessionAttributes` are available to the prompt for the current turn.
- A **code interpreter** action that lets the agent write and run Python in a sandbox to analyse uploaded files (up to five files, 10 MB total) and do exact calculations.
- **Advanced prompt templates** for the pre-processing, orchestration, knowledge-base response and post-processing steps, or a **custom orchestration** **Lambda function** when you want your own strategy instead of the default **ReAct** loop.

At runtime, `InvokeAgent` follows these stages:

1. **Pre-processing** validates and classifies the input.
2. **Orchestration** reasons, chooses an action or **knowledge base**, observes the result and repeats.
3. Optional **post-processing** follows **orchestration**.

Turn on the **trace** to see each rationale, action call and observation. This is how you debug why an **agent** chose a **tool**. You publish an **agent** as a **version** and point an **alias** at it; applications call the **alias**.

**Multi-agent collaboration** designates one **agent** as the **supervisor** and others as **collaborators**. The **supervisor** plans, routes each sub-question to the right **collaborator**, and combines answers. A routing mode handles simple pass-through cases.

The status change you must know: **Amazon Bedrock Agents** is now **Amazon Bedrock Agents Classic**, in maintenance mode and closed to new customers. Existing customers keep using it, exam questions still name it, and its concepts (**action groups**, **return of control**, memory, supervisor and collaborators) remain the right answers where they appear. For new work AWS points to **AgentCore**.

## Amazon Bedrock AgentCore: what AWS recommends

**Amazon Bedrock AgentCore** is a set of managed services for running agents built with *any* framework and *any* model, on or off **Bedrock**. Its pieces map to the problems this task statement lists:

- **AgentCore Runtime** hosts the **agent** code without servers to manage. It isolates every session in its own **microVM**, a lightweight virtual machine with its own kernel, so one user's session can never see another's. It starts fast for interactive use and supports long-running asynchronous work with sessions of up to eight hours.

  It works with the popular open-source frameworks **Strands Agents**, **LangGraph**, **CrewAI** and **LlamaIndex**, as well as custom code. It speaks **MCP** and **A2A**. **A2A**, short for agent-to-agent, is an open protocol that lets **agents** discover and call one another.

  Your container exposes an `/invocations` endpoint and a `/ping` health endpoint. The **AgentCore SDK** provides `BedrockAgentCoreApp` with an `@app.entrypoint` decorator that generates the HTTP server, routing and health checks for you. The **AgentCore starter toolkit**, available through the `agentcore` CLI, packages, containerizes and deploys the **agent**.

  That pair is the "least operational overhead" answer for deploying existing Python **agent** code that must handle both sub-second lookups and multi-minute streamed reports. Writing your own **FastAPI** server, or deploying to **SageMaker** endpoints or **ECS**, is the manual alternative.
- **AgentCore Memory** provides managed **short-term memory** (turn-by-turn events in a session) and **long-term memory** that extracts and stores preferences, facts and session summaries across sessions, shareable across agents.
- **AgentCore Gateway** turns **REST APIs**, **Lambda functions** and existing services into **MCP tools** behind one secured endpoint. The **REST APIs** are described by **OpenAPI** or **Smithy** specifications; **Smithy** is AWS's own interface definition language. **AgentCore Gateway** also connects to existing **MCP servers** and offers **semantic search** over **tools**, so an **agent** finds the right one as the catalog grows.
- **AgentCore Identity** handles both inbound authentication and outbound credentials. For inbound authentication, a **JWT authorizer** validates **OIDC** tokens from your identity provider, including allowed audiences and clients. **OpenID Connect** is the standard login protocol whose signed **JSON Web Tokens** prove who the caller is. For outbound access, **OAuth** flows and **API keys** in a **token vault** let **agents** call downstream systems as the user or as themselves.
- **AgentCore Code Interpreter** and **Browser** are sandboxed tools for running code and driving web applications.
- **AgentCore Observability** emits **OpenTelemetry** traces, spans and metrics into **CloudWatch**, with a **GenAI observability dashboard**. **OpenTelemetry** is the open standard for instrumentation; the metrics cover sessions, latency, tokens and errors.
- **AgentCore Evaluations** scores **task completion**, **tool** use and **reasoning quality**.
- **AgentCore Policy** enforces **Cedar** or natural-language rules on every **tool** call through the **Gateway**. **Cedar** is AWS's open-source policy language for stating which principal may perform which action on which resource under which conditions. **Amazon Verified Permissions**, the managed authorization service for application permissions covered in unit 03, also uses **Cedar**.

When a question says "**AgentCore Runtime**", "**OIDC** tokens validated by the agent platform" or "**maximum tokens** setting on the agent", the answer lives here.

## Open-source frameworks AWS names

**Strands Agents** is an open-source SDK from AWS for Python and TypeScript. It uses a **model-driven** approach: you supply a model, a system prompt and a list of **tools**. The **tools** are Python functions marked with `@tool`. The model plans and calls them itself instead of you hard-coding the flow.

The SDK has built-in session and memory managers, including **AgentCore Memory**, plus native **MCP client** and **A2A** support. Its **multi-agent patterns** include:

- **Agents as tools**: a coordinator calls specialist **agents** like **tools**.
- **Swarm**: peers hand off to each other.
- **Graph**: an explicit directed flow connects the work.

It runs on **Lambda**, **Fargate**, **EC2** or **AgentCore Runtime**, which is its natural production home. **Fargate** provides **serverless** containers on **ECS**. In questions it appears as "**Strands Agents** with built-in memory modules and **MCP tools** for shared context" and as "the **Strands API** to implement custom agent behaviors".

**Agent Squad**, formerly **Multi-Agent Orchestrator**, is an open-source **AWS Labs** framework that sits between users and a team of specialized **agents**. An LLM-based **classifier** reads each message and routes it to the best **agent**. The destinations can include a **Bedrock** model agent, a **Bedrock Agents** agent, an **Amazon Lex** bot or a **Lambda function**. **Amazon Lex** is AWS's conversational-bot service.

A **supervisor agent** mode coordinates several **agents** on one task, while conversation storage keeps unified context across **agents**. This makes **Agent Squad** the answer to "coordinate multiple specialised agents while maintaining shared state", usually alongside **Strands** and **MCP**.

Both frameworks are in scope precisely because the task statement names them; the exam does not test their code.

## MCP: how tools are exposed

The **Model Context Protocol (MCP)** is an open standard for connecting models and agents to tools and data. An **MCP server** publishes tools with typed schemas and executes them; an **MCP client** inside the agent discovers the tools and calls them the same way regardless of what sits behind them. This standardisation is why questions prefer **MCP** over prompt-embedded function-call syntax or per-service microservices the model must choose from.

Where to run **MCP servers** is a recurring question. Match the host to the work:

- **Lambda functions** host *stateless, lightweight* **tools** cheaply and with **automatic scaling**. Examples include a lookup, a calculation or a small query.
- **Amazon ECS**, on **Fargate** or **EC2**, hosts *complex or compute-intensive* **tools**. These need long-running processes, large memory or specialized runtimes, as with simulation engines, heavy data processing or image work.
- **API Gateway** can front either host with an **MCP**-compatible endpoint.
- **AgentCore Gateway** does the whole job as a managed service. It converts APIs and **Lambda functions** to **MCP tools** with authentication built in.

AWS also publishes ready-made **MCP servers** for its own services, such as a server that exposes an **Aurora** database. That is what "configure a prebuilt **MCP server** that links to **Aurora**" refers to.

The same pattern applies to data sources. An **MCP server** can wrap **Amazon Kinesis** streams for real-time event data, **CloudWatch** metrics and logs, or a **vector store**. The model then reaches those sources through one governed interface with the server's credentials rather than its own.

## Structured reasoning with Step Functions

When you are not using a managed **agent**, **AWS Step Functions** is how you make a model follow a deterministic thought-action-observation sequence. The **state machine** follows this loop:

1. A *reason* **Task** invokes the model to produce the next step.
2. An *act* **Task** uses a **Lambda function** to call the **tool**.
3. The workflow stores the observation in the state.
4. A **Choice state** loops back until the model signals completion or an **iteration counter** hits its limit.

The state carries the intermediate reasoning, so nothing is lost between steps. The execution history shows every thought and **tool** result. **Chain-of-thought** is implemented by prompting for explicit reasoning before the answer at each step.

**EventBridge Pipes** is a point-to-point connector from one event source to one target, covered in Domain 1 unit 04. It does not enforce this structure or preserve this state. Neither do **SQS** between loosely coupled functions or one giant prompt with all steps inlined.

## Safeguards on autonomous behaviour

An agent that can loop and call tools can also run away. Skill 2.1.3 lists the controls and the exam expects all of them together.

- **Stopping conditions** in **Step Functions** limit how far the workflow can run. A **Choice state** checks an **iteration counter**. Set `TimeoutSeconds` on **Tasks** and on the whole execution, and `HeartbeatSeconds` for long tasks. A long task must send a heartbeat within the interval or it fails. A **Fail** or fallback state handles limits being hit.
- **Timeouts** on the **Lambda functions** that execute **tools** prevent a hung **tool** from hanging the workflow.
- **IAM policies** give the **agent** execution role and each **tool** function only the actions and resources they need. This is **least privilege**. Where teams create their own roles, use **permission boundaries**: an **IAM policy** that caps the maximum permissions a role can ever have, whatever else is attached.
- **Circuit breakers** combine **Retry** with backoff and a **Catch** that routes to a degraded branch after repeated **tool** failures or **throttling**. A **CloudWatch alarm** on error rate can optionally drive this behavior.
- **Input validation** checks arguments before any **tool** call.

A **circuit breaker** moves through three states:

- **Closed**: calls flow normally.
- **Open**: calls are rejected for a cooling-off period. Traffic goes to a fallback model, cached responses or a human queue.
- **Half-open**: a few trial calls are let through. If they succeed, the circuit closes again.

Monitoring alone, such as reviewing logs weekly or using alarms that notify people, is not real-time control. "Approve every action" removes the automation. These are the distractors.

## Coordinating several models

No single model is best at everything. Skill 2.1.4 wants a **model selection and aggregation framework**. First, route each request to the specialized model for its intent: one FM might summarize results, another extract relationships, and another detect statistical anomalies. Then merge the outputs with custom logic suited to the task:

- **Majority vote** combines classifications.
- **Weighted averaging** uses weights derived from historical accuracy.
- **Ranked fusion** combines retrieval results by merging several ranked lists using each item's positions.

**Step Functions** or a **Lambda** router does the routing. A **Lambda** aggregator does the merging, and fallback models cover failures or low confidence. Random distribution across models, separate endpoints users must choose, or one giant-context model instead of routing are wrong.

## Humans in the loop

For decisions that carry risk, skill 2.1.5 wants the workflow to pause for a person. Examples include large production changes, high-risk loan flags and uncertainty markers in the output.

**Step Functions** does this with the **wait for callback** pattern. A **Task** issues a **task token**, and the execution waits until a reviewer's action calls `SendTaskSuccess` or `SendTaskFailure`. This needs a **Step Functions Standard workflow**, the durable kind that can run for up to a year and records every state transition. **Express workflows** are the cheap, high-volume kind that must finish within five minutes and suit short synchronous pipelines.

**API Gateway** endpoints collect structured reviewer feedback. Store that feedback in **DynamoDB** and later use it to refine prompts. Route only the cases that meet criteria, such as confidence below a threshold or risk flags, to review. Let the rest flow automatically.

**Amazon Augmented AI (A2I)** is the managed human-review service for low-confidence predictions from **Textract**, **Rekognition** or custom models. It includes built-in review workflows and workforces. It is the keyed answer to "route only uncertain extractions to human reviewers" even though **A2I** is now closed to new customers. Sending every output to a batch approval queue or to a Slack channel is not a controlled review process.

## Reliable tool integrations

Models produce malformed arguments: negative quantities, badly formatted dates or missing fields. Skill 2.1.6 puts a **Lambda function** between the model and every external system. The function validates and sanitizes parameters against the **tool schema**, then executes the call with **structured error handling**. When input is invalid, it returns a clear corrective message so the model can try again with fixed arguments.

Make the **tool** contract easy to use and monitor:

- Standardize **tool definitions** with **OpenAPI specifications** or **JSON Schema**.
- Keep **tools** single-purpose and **idempotent**.
- Publish metrics on invocation counts, latency and errors.

Forwarding calls unchecked through **EventBridge Pipes** does not validate them. Cleaning parameters later with **AWS Glue**, the batch ETL service, is far too slow for a live **tool** call. Simply retrying and hoping is also wrong.

## Worked scenario

A logistics company wants an agent that resolves shipment exceptions: it must look up shipments, recompute routes, check customs rules, refund customers under a threshold and ask a human above it, and coordinate with a separate returns agent, all without running away or overstepping its permissions.

The exam's vocabulary describes it with **Amazon Bedrock Agents**: an agent with instructions, **action groups** for shipment lookup and route recalculation backed by **Lambda functions**, a **knowledge base** of customs rules, memory across a customer's sessions, and traces turned on for debugging. In a new build the same design runs on **AgentCore**: the agent code (written with **Strands Agents**, tools as Python functions) deploys to **AgentCore Runtime** through the starter toolkit, **AgentCore Memory** keeps short- and long-term context, and **AgentCore Gateway** exposes the shipment and returns APIs as **MCP tools**. The lightweight lookups run as **MCP servers** on **Lambda**; the route optimiser, which needs minutes of compute and a large in-memory graph, runs as an **MCP server** on **ECS**. **Agent Squad** routes each conversation between the exceptions agent and the returns agent and keeps shared state.

When a process must be predictable, such as deciding whether to issue a refund, a **Step Functions state machine** controls the **reason-act-observe loop**.

The workflow includes:

- An **iteration limit** to prevent endless loops.
- **Task timeouts** to stop tasks that run too long.
- A **Catch** that opens a **circuit breaker** and uses a fallback path after repeated **tool** failures.
- A **wait-for-callback** step that pauses for human approval when a refund exceeds the threshold.
- **DynamoDB** to record the approval decision.

Every **tool** sits behind a **Lambda function**. The function validates the model's arguments against the **tool schema** before executing the **tool**. If the arguments are malformed, it returns a corrective message so the model can fix them.

Each role carries **least-privilege IAM permissions** and a **permission boundary** to limit what it can do.

Questions built on this scenario use the following mappings:

- **Multi-agent coordination with shared state** → **Strands**, **Agent Squad**, **MCP**.
- **Deterministic reasoning steps** → **Step Functions**.
- **Safeguards against runaway loops** → **stopping conditions**, **timeouts**, **circuit breakers**, **IAM**.
- **Human review only for risky cases** → **wait for callback**.
- **Reliable tool calls** → **Lambda** validation.
- **Lightweight tools** → **Lambda**.
- **Heavy tools** → **ECS**.

## Exam lens

- "Multiple specialised agents, shared evolving state, tool access" → **Strands Agents** with **Agent Squad** and **MCP tools** (or **Strands** with built-in memory and **MCP**).
- "Deterministic thought-action-observation steps" → **Step Functions** **ReAct** pipeline.
- "Runaway loops, tool failures, latency limits" → **Step Functions** **stopping conditions** and failure branches plus **Lambda** timeouts and **circuit breakers**.
- "Select the best model per intent and merge outputs" → a routing and aggregation framework.
- "Human review only for flagged cases, collect structured feedback" → **Step Functions** conditional review steps and **API Gateway** feedback.
- "Malformed tool parameters" → **Lambda** validation, error handling, corrective feedback to the model.
- "Simple tools fast, heavy tools scalable, one access pattern" → **Lambda** **MCP servers** and **ECS** **MCP servers** with **MCP client libraries**.
- "Expose **Kinesis**, **CloudWatch** and embeddings to the model safely" → a backend exposing them as **MCP tools**.
- "Deploy Python agent code with sub-second and multi-minute streaming, no server setup" → **AgentCore Runtime** with the **SDK entrypoint decorator** and the starter toolkit.
- "Natural-language inventory requests, **MCP** to existing systems, minimal complexity" → **AgentCore Runtime** with **Strands** and a prebuilt **MCP server**.

## Knowledge check

<!-- KC: E1-Q2, E3-Q12, E1-Q9, E1-Q50, E1-Q46, E2-Q26, E1-Q54, E1-Q38, PQ-Q15, E3-Q45 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 2

A financial services company is building an autonomous AI system that assists analysts with fraud investigations. The solution must maintain evolving case context, share findings between specialized agents (for example, a transaction-pattern agent and a customer-behavior agent), and coordinate tool interactions such as querying historical case data and retrieving supporting documents. The architecture must allow agents to store intermediate reasoning, remember prior steps, and collaborate without losing state across multi-step investigations.

Which approach should the team implement to meet these requirements?

- **A)** Use Amazon EventBridge scheduling to trigger periodic recomputation of agent output and rely on S3 to store intermediate text files for each investigation step.
- **B)** Deploy multiple stand-alone Lambda functions triggered in sequence, passing raw model output between them as JSON without a shared memory layer.
- **C)** Use Strands Agents with AWS Agent Squad to coordinate multiple specialized agents and maintain persistent shared state, combined with MCP-based tool interaction for accessing external resources.
- **D)** Use a single large FM prompt that instructs the model to remember all prior steps and infer how to collaborate across tasks without external state storage.

<details><summary>Answer</summary>

**Answer: C.** Strands Agents build the specialised agents, Agent Squad coordinates them while maintaining persistent shared state, and MCP gives them a standard way to call tools such as case-history queries and document retrieval, so intermediate reasoning and prior steps survive multi-step investigations. Scheduled recomputation with S3 files, chained Lambda functions without shared memory, and one giant prompt cannot preserve or share state.

*Where this is covered: Unit 01, Open-source frameworks AWS names. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 3, question 12

A global pharmaceutical research lab is developing an autonomous multi-agent system that assists scientists in synthesizing compound hypotheses, retrieving experiment history, and coordinating lab tooling. The system uses several specialized agents—one for literature search, one for chemical reasoning, and one for experiment planning. The engineering team needs the system to preserve long-term scientific context, maintain state across multi-step tasks, and reliably pass shared memory between agents without manually coding state synchronization for every interaction.

The solution must minimize custom infrastructure, support tool integrations, and allow agents to read/write shared memory during extended workflows.

Which solution will BEST meet these requirements?

- **A)** Use AWS Lambda to store agent memory snapshots in Amazon DynamoDB and manually pass the memory object to each agent during invocation.
- **B)** Use Strands Agents with built-in memory modules and integrate MCP tools for shared context access, enabling multi-agent state management without custom synchronization logic.
- **C)** Store scientific context in Amazon S3 using versioned JSON documents and have each agent fetch and update the memory file at the start and end of every task.
- **D)** Deploy each agent as a container in Amazon ECS and mount a shared Amazon EFS file system to store session memory that all containers read from and write to.

<details><summary>Answer</summary>

**Answer: B.** Strands Agents with built-in memory modules preserve long-term scientific context and state across multi-step tasks, and MCP tools give the specialised agents shared context access without hand-coded synchronisation. Passing memory snapshots from DynamoDB manually, versioned JSON files in S3, and a shared EFS volume between ECS containers all require custom state management.

*Where this is covered: Unit 01, Open-source frameworks AWS names. Key: ours, confidence high.*

</details>

### 3. Exam 1, question 9

A biomedical research organization is developing an AI assistant that helps scientists analyze complex gene-interaction datasets. The assistant must break down user queries into structured reasoning steps, call external analytical tools, validate intermediate results, and then continue reasoning based on those results. The engineering team wants to ensure the FM follows a deterministic sequence of thought-action-observation steps without losing track of prior reasoning.

Which approach should the team implement to meet these requirements?

- **A)** Use EventBridge pipes to chain multiple FM invocations together without enforcing structured execution or state transitions.
- **B)** Use Amazon SQS to pass unstructured FM output between loosely connected Lambda functions that infer the sequence of steps dynamically.
- **C)** Use a single Amazon Bedrock model invocation with an expanded prompt containing all possible reasoning steps and tool instructions embedded inline.
- **D)** Use AWS Step Functions to orchestrate a ReAct-style reasoning pipeline, where each state triggers FM reasoning, executes tool calls, captures observations, and feeds structured outputs into the next step.

<details><summary>Answer</summary>

**Answer: D.** A Step Functions state machine that alternates FM reasoning, tool execution and observation capture, feeding structured output into the next state, is the ReAct pattern with deterministic sequencing and preserved state. EventBridge Pipes and SQS chains enforce no structure, and a single expanded prompt cannot call tools and validate intermediate results.

*Where this is covered: Unit 01, Structured reasoning with Step Functions. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 4. Exam 1, question 50

A financial analytics company is building an FM-powered system that generates multi-step investment risk assessments. Some model queries can escalate into long reasoning chains, repeatedly calling external risk-analysis tools. The engineering team must ensure that the FM behaves safely by enforcing strict stopping conditions, preventing runaway loops, and ensuring the workflow halts immediately if any tool call fails or exceeds its expected latency.

Which approach will BEST ensure controlled and safeguarded FM behavior?

- **A)** Use CloudWatch Logs alone to detect abnormal FM behavior and manually terminate workflows if excessive tool calls are identified.
- **B)** Use AWS Step Functions to implement explicit stopping conditions, failure branches, and maximum iteration limits, with Lambda functions enforcing timeouts and circuit breakers for external tool calls.
- **C)** Use a large, instruction-heavy Bedrock prompt that instructs the FM to stop after a certain number of reasoning steps and avoid unnecessary tool calls.
- **D)** Use Amazon SQS with dead-letter queues to hold messages when FM tool calls fail, allowing engineers to investigate failures later.

<details><summary>Answer</summary>

**Answer: B.** Step Functions provides explicit stopping conditions, failure branches and maximum iteration limits, and Lambda functions enforce timeouts and circuit breakers on external tool calls, so the workflow halts on failure or excessive latency. CloudWatch Logs alone requires manual termination, prompt instructions are not enforceable, and SQS dead-letter queues only park failures for later investigation.

*Where this is covered: Unit 01, Safeguards on autonomous behaviour. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 5. Exam 1, question 46

A logistics automation company is building an FM-driven operations assistant using Amazon Bedrock. The assistant uses the Strands API to trigger route optimization tools, inventory lookup functions, and shipment-delay diagnostics. During testing, engineers observe that the FM sometimes produces malformed function parameter values (such as negative quantities or improperly formatted timestamps), causing downstream tool failures. The AI engineer must design a solution that ensures safe execution of tool calls, validates all parameters before invoking external systems, and provides corrective feedback to the FM when invalid inputs are detected.

Which solution BEST meets these requirements?

- **A)** Use Amazon EventBridge Pipes to forward all FM tool calls directly to downstream services without parameter checks to reduce latency.
- **B)** Store the FM output in Amazon S3 and run periodic AWS Glue jobs to clean malformed parameters before tool execution.
- **C)** Use AWS Lambda functions to validate and sanitize all FM-generated tool parameters, implement structured error handling, and return corrective messages to the FM when inputs are invalid.
- **D)** Configure the FM to retry failed tool calls automatically, assuming that repeated attempts will eventually produce valid parameters.

<details><summary>Answer</summary>

**Answer: C.** Lambda functions between the model and each tool validate and sanitise the generated parameters, handle errors in a structured way, and return corrective messages so the FM can retry with valid inputs, which keeps tool execution safe. Forwarding calls unchecked through EventBridge Pipes, cleaning parameters later with Glue, and blind retries do not prevent bad calls.

*Where this is covered: Unit 01, Reliable tool integrations. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 6. Exam 2, question 26

A multinational investment firm is building an AI-powered research assistant using Amazon Bedrock to support analysts with portfolio risk assessments, market commentary, and cross-asset insights. The assistant must query diverse data sources, including real-time bond yield streams from Amazon Kinesis Data Streams, market anomaly alerts from Amazon CloudWatch, and vector-based similarity search results generated from SageMaker JumpStart embeddings.

The solution must allow the foundation model to safely access these systems without embedding credentials, SDK calls, or query syntax in prompts. The firm also requires a standardized and compliant mechanism for exposing tools that the model can call deterministically at runtime, ensuring all data interactions are auditable and consistently structured.

Which architecture best meets these requirements?

- **A)** Rely on SageMaker JumpStart embeddings alone and depend on the model’s inherent financial reasoning to interpret current market events without direct access to streaming or alert data.
- **B)** Build Lambda functions for each data source and instruct the model to produce the correct function-call syntax inside its prompts so the application layer can execute them.
- **C)** Deploy a unified backend service that exposes Kinesis, CloudWatch, and embedding queries as callable tools using the Model Context Protocol (MCP), enabling secure and structured Bedrock tool use without embedding sensitive logic in prompts.
- **D)** Create microservices for each data source and rely on prompt engineering so the foundation model can decide which service endpoint to call based solely on conversational context.

<details><summary>Answer</summary>

**Answer: C.** Exposing Kinesis streams, CloudWatch alerts and embedding queries as MCP tools through a unified backend gives the model deterministic, auditable, consistently structured tool access without credentials, SDK calls or query syntax in prompts. Relying on embeddings alone loses live data, making the model emit function-call syntax in prompts is fragile, and letting the model pick microservice endpoints from conversational context is neither standardised nor auditable.

*Where this is covered: Unit 01, MCP: how tools are exposed. Key: ours, confidence high.*

</details>

### 7. Exam 1, question 54

A financial services company is developing an FM-powered document analysis assistant on Amazon Bedrock to help analysts review complex loan applications. The system generates risk summaries, extracts financial ratios, and identifies anomalies. Compliance officers require a multi-stage human review process when the FM output includes uncertainty markers or high-risk flags. The AI engineer must design a workflow that automatically routes these cases for human validation and also collects structured feedback that will later be used to refine prompt strategies.

Which solution BEST meets these requirements?

- **A)** Use AWS Step Functions to orchestrate conditional human-review steps, and integrate Amazon API Gateway to collect structured reviewer feedback for future refinement.
- **B)** Implement an Amazon SQS queue that sends every FM output to a batch process for manual approval, regardless of whether uncertainty markers are detected.
- **C)** Deploy the FM behind an Amazon CloudFront distribution and instruct analysts to manually review outputs through a web form before approval.
- **D)** Configure Amazon EventBridge to forward all FM responses to a Slack channel so that reviewers can leave comments that the system parses asynchronously.

<details><summary>Answer</summary>

**Answer: A.** Step Functions orchestrates conditional human-review steps that trigger only when outputs carry uncertainty markers or high-risk flags, and API Gateway endpoints collect structured reviewer feedback for later prompt refinement. Sending every output to batch approval ignores the conditions, a CloudFront web form is not a workflow, and parsing Slack comments is unstructured and unreliable.

*Where this is covered: Unit 01, Humans in the loop. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 8. Exam 1, question 38

A financial analytics firm is developing a Python-based research agent that runs on Amazon Bedrock AgentCore Runtime to support complex financial data queries. The agent must support fast lookups with sub-second response times and long-running research report generation that may stream results for several minutes. The company wants to eliminate infrastructure management tasks such as configuring HTTP servers, defining /ping or /invocations routes, and building custom health checks. The firm also wants a deployment option that packages and deploys the agent with minimal manual setup.

Which combination of approaches will meet these requirements with the least operational overhead? (Select TWO.)

- **A)** Deploy the agent by using the AgentCore starter toolkit to automate packaging, containerization, and deployment workflows.
- **B)** Implement a custom FastAPI server that manually defines the /ping and /invoke endpoints and package it within a container for deployment.
- **C)** Use the AgentCore SDK with the entrypoint decorator to automatically generate server configuration, routing, and health checks.
- **D)** Deploy the agent on Amazon SageMaker AI real-time endpoints by using a custom inference container.
- **E)** Deploy the agent on Amazon ECS on AWS Fargate by using a custom container image that runs the AgentCore SDK application.

<details><summary>Answer</summary>

**Answer: A, C.** The AgentCore SDK entrypoint decorator generates the HTTP server, routing and health checks, and the AgentCore starter toolkit automates packaging, containerisation and deployment to AgentCore Runtime, which supports both sub-second responses and multi-minute streaming with no infrastructure management. A custom FastAPI server, SageMaker real-time endpoints and ECS on Fargate all require the manual server and infrastructure work the question excludes.

*Where this is covered: Unit 01, Amazon Bedrock AgentCore: what AWS recommends. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 9. Official practice question set, question 15

A financial services company is developing a research agent that processes complex financial data queries. The company must deploy existing Python agent code to Amazon Bedrock AgentCore Runtime. The company wants to reduce infrastructure management overhead and operational complexity.

The agent must be able to handle quick data lookups that require sub-second responses. The agent must be able to handle comprehensive research report generation. For example, streaming responses over several minutes. The solution must automatically manage HTTP server configuration, endpoint routing, and health monitoring.

Which deployment approaches will meet these requirements with MINIMAL operational overhead? **(Select TWO)**

- **A)** Deploy the agent on Amazon ECS on AWS Fargate by using a custom container image that runs the AgentCore SDK application.
- **B)** Deploy the agent on Amazon SageMaker AI real-time endpoints by using a custom inference container.
- **C)** Implement the AgentCore SDK with the `@app.entrypoint` decorator to automatically handle server setup and endpoint management.
- **D)** Deploy the agent by using the AgentCore starter toolkit for automated packaging, containerization, and deployment workflows.
- **E)** Implement a FastAPI server with a configuration of `/invocations` and `/ping` endpoints and container orchestration.

<details><summary>Answer</summary>

**Answer: C, D.** The AgentCore SDK's entrypoint decorator automatically handles HTTP server setup, endpoint routing and health monitoring, and the AgentCore starter toolkit automates packaging, containerisation and deployment, so existing Python agent code runs on AgentCore Runtime with sub-second and long streaming responses and minimal operations. ECS on Fargate, SageMaker real-time endpoints and a hand-written FastAPI server with /invocations and /ping all reintroduce infrastructure and server management.

*Where this is covered: Unit 01, Amazon Bedrock AgentCore: what AWS recommends. Key: AWS official answer.*

</details>

### 10. Exam 3, question 45

A global logistics company is building an automated system to optimize its inventory replenishment workflow. Employees will submit restocking requests and check inventory levels through natural language interactions, and the solution must autonomously trigger supply chain processes with minimal ongoing maintenance. The company uses Amazon Textract to extract key fields from scanned inventory documents and stores all operational and inventory data in Amazon Aurora. The system must support Model Context Protocol (MCP) to enable seamless communication with the company’s existing inventory systems.

Which solution will minimize operational complexity while meeting these requirements?

- **A)** Create an intelligent assistant with Amazon Lex and Amazon Polly, using AWS Lambda to process natural language inventory requests and store results in Amazon DynamoDB. Use Amazon SNS to notify supply chain teams for restocking actions.
- **B)** Implement an AI-powered chat assistant with Amazon Lex, using AWS Lambda to process inventory requests. Push requests to an Amazon SQS queue, which triggers backend supply chain processes on Amazon ECS with AWS Fargate.
- **C)** Set up an agent using Amazon Bedrock AgentCore Runtime and Strands Agents, and configure a prebuilt MCP server that links to Aurora for inventory data. Store and expose the data as MCP tools, connecting with the company’s chat interface.
- **D)** Deploy an MCP server using FastMCP with LangGraph on an Amazon EC2 instance, connect it to Aurora for inventory data, and expose the data as MCP tools. Integrate with the company’s chat interface using a custom agent built with Amazon SageMaker.

<details><summary>Answer</summary>

**Answer: C.** AgentCore Runtime hosts a Strands agent without infrastructure, a prebuilt MCP server for Aurora exposes inventory data as MCP tools, and the chat interface connects to the agent, meeting the MCP requirement with the least operational complexity. Lex with Lambda and SNS or SQS to Fargate does not use MCP or an agent, and FastMCP with LangGraph on EC2 plus a custom SageMaker agent means managing servers and custom code.

*Where this is covered: Unit 01, MCP: how tools are exposed. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

Agents run a **reason-act-observe loop** over tools with short- and **long-term memory**. **Bedrock Agents** (now **Agents Classic**) packages that loop with **action groups**, **return of control**, **knowledge bases**, **guardrails**, memory, **code interpretation** and **supervisor-collaborator teams**; **AgentCore** is the current platform, with Runtime, Memory, Gateway, Identity, tools, Observability, Evaluations and Policy for agents built on any framework.

**Strands Agents** is AWS's model-driven SDK, **Agent Squad** the open-source **multi-agent orchestrator**, and **MCP** the protocol that standardises tools, hosted on **Lambda** for light work, **ECS** for heavy work, or **AgentCore Gateway** as a managed service. **Step Functions** implements **ReAct** when you orchestrate yourself and supplies the safeguards: **stopping conditions**, timeouts, **circuit breakers** and human-review pauses, with **IAM** **least privilege** and **Lambda** validation around every tool.
