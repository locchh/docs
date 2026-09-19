# Domain 2: Implementation and Integration

**Weight: 26% of the scored exam** (roughly 17 of the 65 scored questions). Domain 1 was about choosing models and preparing knowledge. Domain 2 is about building the application around them:

- Build agents and tools.
- Deploy and serve models.
- Integrate the GenAI capability with the rest of the enterprise.
- Make the API layer work under real traffic.
- Use AWS tools to speed up development.

The domain has five task statements. Each is a unit. Units 01 and 04 carry the most questions.

| Unit | Task statement | What you will be able to do |
|---|---|---|
| [01 Agents and tools](01-agents-and-tools.md) | 2.1 Implement agentic AI solutions and tool integrations | Build agents with **Bedrock Agents**, **AgentCore**, **Strands Agents** and **Agent Squad**; give them memory, tools and **MCP servers**; orchestrate **ReAct** reasoning with **Step Functions**; add **stopping conditions**, **circuit breakers** and human review |
| [02 Model deployment strategies](02-model-deployment-strategies.md) | 2.2 Implement model deployment strategies | Pick between **Lambda** plus **Bedrock** **on-demand**, **Provisioned Throughput**, and the **SageMaker** endpoint types; deploy LLMs in GPU containers correctly; use cascading and smaller models to balance cost and quality |
| [03 Enterprise integration](03-enterprise-integration.md) | 2.3 Design and implement enterprise integration architectures | Connect legacy systems through APIs and events, federate identity, respect data residency with **Outposts** and edge zones, and ship through CI/CD and a **GenAI gateway** |
| [04 FM API integrations](04-fm-api-integrations.md) | 2.4 Implement FM API integrations | Build synchronous, asynchronous and streaming interfaces on **API Gateway**, **Lambda** and **SQS**; make them resilient with retries, **throttling**, **circuit breakers** and **X-Ray**; route requests to the right model |
| [05 Application patterns and developer tools](05-application-patterns-and-developer-tools.md) | 2.5 Implement application integration patterns and development tools | Design FM-friendly APIs, accessible interfaces with **Amplify**, **OpenAPI** and **Bedrock Flows**, business-system enhancements, **Amazon Q Developer** productivity, and troubleshooting with **Logs Insights** and **X-Ray** |
| [06 Domain review](06-domain-2-review.md) | all | Decision tables, a one-page summary, and a mixed quiz |

## How the questions are placed

The exam files hold 44 questions for this domain: 18 from Exam 1 (graded), 13 from Exam 2, 9 from Exam 3, and 4 from the official practice set. Units end with the questions that test their content; the remainder form the mixed quiz in unit 06. Exam 2 and 3 keys are ours and carry a confidence mark.

## A note on service names

Services named in the exam guide have changed status since the guide was written, and questions still use the old names:

- **Amazon Bedrock Agents** is now **Amazon Bedrock Agents Classic**, in maintenance mode and closed to new customers since 30 July 2026. AWS points new work at **Amazon Bedrock AgentCore**.
- **Amazon Augmented AI (A2I)** is also closed to new customers.
- **Amazon Q Business** is closed to new customers since 31 July 2026, with **Amazon Quick** as the successor.

The units explain both the way the exam expects and what to use today.

## Time

About four hours for the five units plus the review. This is the morning and early afternoon of day 2.
