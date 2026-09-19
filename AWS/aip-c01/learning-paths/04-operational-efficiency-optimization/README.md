# Domain 4: Operational Efficiency and Optimization for GenAI Applications

**Weight: 12% of the scored exam** (roughly 8 of the 65 scored questions). Domains 1 to 3 built and secured the application; Domain 4 makes it cheap enough to run and fast enough to use, and puts the instruments in place to know both. The questions are about tokens, model tiers, batching, caching, latency, throughput, capacity and the metrics that watch them.

The domain has three task statements, each a unit, plus a review.

| Unit | Task statement | What you will be able to do |
|---|---|---|
| [01 Cost optimization and resource efficiency](01-cost-and-resource-efficiency.md) | 4.1 Implement cost optimization and resource efficiency strategies | Count and cut tokens, choose and route to the cheapest adequate model, raise throughput and utilisation with batching, right-sizing and capacity planning, and avoid invocations with exact-match, semantic, edge and **prompt caching** |
| [02 Application performance](02-application-performance.md) | 4.2 Optimize application performance | Reduce perceived latency with **pre-computation**, **latency-optimized inference**, streaming and parallelism; tune retrieval indexes and queries; lift throughput within quotas; tune **inference parameters** with **A/B tests**; allocate capacity to GenAI traffic; profile the system |
| [03 Monitoring systems for GenAI applications](03-monitoring-genai-applications.md) | 4.3 Implement monitoring systems for GenAI applications | Build observability from **Bedrock** metrics, **invocation logs**, **X-Ray** and **CloudWatch generative AI observability**; monitor tokens, **prompt effectiveness**, **hallucination** rates, drift and cost anomalies; watch tools, agents and the **vector store**; apply FM troubleshooting frameworks |
| [04 Domain review](04-domain-4-review.md) | all | Decision tables, the words that give answers away, a one-page summary, and a mixed quiz |

## How the questions are placed

The exam files hold 21 questions for this domain: 9 from Exam 1 (graded), 4 from Exam 2, 7 from Exam 3, and 1 from the official practice set. Units end with the questions that test their content; three questions that overlap earlier units form the mixed quiz in unit 04. Exam 2 and 3 keys are ours and carry a confidence mark. Task 4.3 has almost no dedicated exam questions in these files (monitoring questions are tagged to Domain 5), so unit 03 is shorter and points forward.

## A note on service status

**Amazon CloudWatch Evidently**, which the Skill Builder course names for **A/B testing**, was discontinued in October 2025; the units use **AWS AppConfig** **feature flags** with **CloudWatch** metrics (and **SageMaker** **production variants** for hosted models) instead. **CloudWatch generative AI observability** became generally available in late 2025 and is the current way to monitor **Bedrock** and **AgentCore** workloads together.

## Time

About two and a half hours for the three units plus the review. This is the afternoon of day 3, followed by the Domain 3 and Domain 4 review quizzes.
