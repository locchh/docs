# Unit 02: Model deployment strategies

**Task 2.2: Implement model deployment strategies.** This unit is about where inference runs and why: the **Bedrock** and **SageMaker** hosting options and the traffic each fits, what makes serving a large language model different from serving a classical model, and how to cut cost with smaller models, cascading and caching.

Domain 1 covered *how you buy **Bedrock** capacity*. This unit covers *where inference runs*, including the cases where **Bedrock** is not the host.

## Deployment options and when each fits

Start with where anything runs on AWS. Each hosting option serves a different kind of workload:

- **Functions**: **AWS Lambda** runs code per request with no servers, up to fifteen minutes and ten gigabytes of memory.
- **Containers with Amazon ECS**: run containers on **serverless** **AWS Fargate** or on **EC2**.
- **Containers with Amazon EKS**: run **Kubernetes**.
- **Containers with AWS App Runner**: use the simplest way to run a web container.
- **Virtual machines**: **Amazon EC2** includes GPU and accelerator instance families.
- **Managed ML hosting**: **SageMaker AI** provides several kinds of endpoints.
- **Edge devices**: **AWS IoT Greengrass** runs on devices.
- **Hybrid infrastructure**: **AWS Outposts** runs in your data center.
- **Infrastructure near users**: **Local Zones** and **Wavelength** bring compute closer to users.

With that map in mind, there are two families of hosting for models on the exam. With **Amazon Bedrock**, AWS runs the model and you pay per token or per provisioned unit. With **Amazon SageMaker AI**, you deploy an open-weight, fine-tuned or proprietary model to an endpoint on instances you choose.

On this exam, **Lambda**, **ECS** and **App Runner** host your *application* rather than the model. Self-managed GPU containers on **ECS** or **EKS** are technically possible but appear only as distractors. The one exception, inference on edge devices, closes this unit.

| Option | What it is | Fits |
|---|---|---|
| **Lambda invoking Bedrock on-demand** | **Serverless** function calls `InvokeModel` or `Converse`; you pay per invocation and per token, nothing idles | Low or spiky traffic, event-driven and request/response apps; the default for a website with unpredictable spikes |
| **Bedrock Provisioned Throughput** | Reserved **Model Units** for guaranteed **tokens per minute**, hourly billing with optional 1- or 6-month terms | Consistently low latency at steady high volume (an internal dashboard at peak season), customised models |
| **Bedrock batch inference** | Asynchronous job over JSONL prompts in **S3** at a discount | Bulk offline generation with hours of slack |
| **SageMaker real-time endpoint** | Persistent instances (CPU or GPU) running your container behind an HTTPS endpoint with **auto scaling**, **production variants**, **shadow tests** and **deployment guardrails** | Custom or fine-tuned models that need consistent low latency and GPUs; interactive image generation; proprietary models with custom pre- and post-processing. Limits: request payload up to 6 MB and a response within 60 seconds |
| **SageMaker Serverless Inference** | Endpoint that scales to zero and up automatically; memory from 1 to 6 GB, CPU only, cold starts, optional **provisioned concurrency** (pre-warmed capacity that skips cold starts) | Intermittent traffic and small models that fit in memory (a fraud model under 5 GB serving tens of concurrent requests) |
| **SageMaker Asynchronous Inference** | Requests queued via **S3** pointers, payloads up to 1 GB, processing up to one hour, results to **S3** with **SNS** notifications, scales to zero | Large inputs or long generations where a response within minutes is acceptable (image generation with up to 15 minutes to respond) |
| **SageMaker batch transform** | Offline job over a dataset in **S3** | Scoring whole datasets, not interactive use |
| **SageMaker multi-model and multi-container endpoints** | One endpoint hosting many models of the same framework loaded on demand, or several containers in one endpoint | Many small models with uneven traffic; serial **inference pipelines** |
| **SageMaker inference components** | Independent units of compute and scaling per model on a shared endpoint; **LoRA** adapters as components on a base model | Several FMs or many adapters sharing accelerators with separate scaling policies |

The **hybrid pattern** appears often. Use **Bedrock** for general-purpose FMs and **SageMaker** for proprietary or custom-processed models. An orchestration layer built with **API Gateway** and **Step Functions** or **Lambda** routes between them by language, complexity or task.

A model you fine-tuned in **SageMaker** does not have to stay there. **Custom Model Import** brings supported architectures into **Bedrock** and serves them on demand without **Provisioned Throughput**.

Two matching rules decide most deployment questions. First, match the traffic. Steady, latency-critical work wants reserved or always-on capacity. Spiky, occasional work wants pay-per-use capacity that scales to zero.

Second, match the hardware and the size:

- A GPU requirement means **real-time** or **asynchronous SageMaker endpoints**. **Serverless Inference** is CPU only, while **Lambda** tops out at 10 GB of memory and 15 minutes.
- Near-real-time interactive use with requests under 6 MB and answers under 60 seconds means a **real-time endpoint**.
- Large inputs up to 1 GB, or processing that takes minutes and can run for up to an hour, mean **Asynchronous Inference**.

## What makes LLM deployment different

A classical model is megabytes; an LLM is tens or hundreds of gigabytes of weights that must sit in accelerator memory. A 70-billion-parameter model in 16-bit precision needs roughly 140 GB of GPU memory, more than any single GPU. That is before you count the **KV cache**.

The **KV cache**, or key-value cache, is the model's working memory of every token already in the context. It grows with conversation length. Loading the model takes minutes, and throughput depends on how many tokens you can process per second, not requests per second. Skill 2.2.2 covers techniques for handling these constraints on **SageMaker**.

**Containers built for LLMs.** **SageMaker**'s **Large Model Inference (LMI) containers** are the standard way to serve open LLMs. They are based on **Deep Java Library (DJL) Serving**, with back ends such as the open-source inference engine **vLLM** and NVIDIA's **TensorRT-LLM**. **Transformers-NeuronX** supports **Inferentia** and **Trainium**, AWS's own inference and training accelerator chips.

These containers implement several techniques, each addressing a different serving constraint:

- **Tensor parallelism** splits each layer across several GPUs so a model larger than one GPU fits.
- **Continuous or rolling batching** lets new requests join a running batch as others finish, keeping GPUs busy.
- **Paged attention** stores the **KV cache** in fixed-size pages so memory is not wasted on padding.
- **Quantisation** uses INT8, INT4 or FP8 weights to cut memory use and speed up loading.
- **Speculative decoding** uses a small draft model to propose several tokens. The large model verifies them in one pass.
- **Multi-adapter LoRA serving** serves multiple **LoRA** adapters.

Configure the containers with properties such as the **tensor-parallel degree** and **maximum sequence length**.

**Loading strategies.** Model loading can dominate startup time. Use these controls to make startup shorter and prevent slow loads from failing:

- Store uncompressed artifacts in **S3** so the container can stream weights instead of unpacking a tarball.
- Raise the container startup health-check and download timeouts, up to 60 minutes, so a slow load is not killed.
- **Preload** the model at container start rather than per request.
- Use **lazy or sharded loading** and **quantised weights** to shorten startup.
- Keep a **minimum instance count** or **warm capacity** so cold starts do not hit users.

**Right-sizing GPUs.** Match instance families to the model:

- `ml.g5` and `ml.g6` fit mid-size models.
- `ml.p4d` and `ml.p5` fit the largest models.
- `ml.inf2` and `ml.trn1` provide cost-efficient inference with AWS silicon.

Profiling tells you how many GPUs the weights and activations actually need. If a model fits in four of the eight GPUs on an instance, run two replicas with **tensor parallelism** of four instead of one replica across eight. Shrink the configured **maximum sequence length** to what real requests use, so more sequences fit in each batch. **SageMaker Inference Recommender** benchmarks instance types for you.

**Deployment safety.** **SageMaker** offers three controls for evaluating and releasing a model:

- **Deployment guardrails** update an endpoint with **blue/green traffic shifting**, using all-at-once, **canary** or linear shifts. During a **baking period**, **CloudWatch alarms** trigger automatic rollback.
- **Shadow tests** copy production traffic to a new variant without serving its responses.
- **Production variants** split live traffic by weight for **A/B tests** and let you shift 100 percent to the winner.

The distractors are stable: **Lambda** with more memory (cannot hold the model), a classical container that loads to CPU first, many small endpoints behind a load balancer instead of parallelism, and "allocate maximum memory to everything".

## Optimising cost and performance

Skill 2.2.3 is about spending less without losing quality.

**Use the smallest model that meets the bar.** A fine-tuned small model or a task-specific model often beats a general large model on a narrow job at a fraction of the cost and latency. **Model cascading** formalises this: a small, fast model handles routine requests, and only requests it cannot handle with confidence (low confidence score, a detected complexity signal, an explicit escalation) go to the large model. When about eight percent of traffic is complex, cascading cuts cost and latency for the other ninety-two. **Bedrock**'s **intelligent prompt routing** is the managed version within a model family; a **Lambda** or **Step Functions** router is the general version.

**Cache.** Choose a cache based on what repeats:

- **Response caching** reuses answers to repeated prompts.
- **Semantic caching** reuses answers to near-duplicate questions.
- **Embedding caching** reuses embeddings for **RAG**.
- **Bedrock prompt caching** avoids re-processing a long static prefix.

The first three avoid inference; **prompt caching** avoids repeated prefix processing.

**Batch** whatever is not interactive and run it asynchronously. The options include **SQS** with **Lambda**, **Step Functions**, **SageMaker asynchronous endpoints** and **Bedrock batch inference**.

**Compress** the model when appropriate. **Quantisation** and **distillation** produce smaller models that cost less to serve.

**Scale to fit.** Match each capacity control to the load it handles:

- Use **auto scaling** on **SageMaker endpoints** and **inference components**.
- Use **provisioned concurrency** only where cold starts matter.
- Use **Provisioned Throughput** only for the steady part of the load. Let **on-demand** or **cross-Region inference** absorb spikes.

Measure latency percentiles, **tokens per second** and cost per request in **CloudWatch**. **A/B test** configurations before committing.

## Hosting the application and the edge

Two hosting questions sit beside model deployment: how to keep application connections open, and how to run inference when the cloud connection is unreliable.

Long-lived connections such as a **WebSocket** telemetry stream do not fit **Lambda**'s 15-minute limit. **Amazon ECS on AWS Fargate** runs containers without servers and holds persistent connections. **AWS App Runner** is the simplest way to run a web container with **automatic scaling**, though its request-based model suits **HTTP APIs** better than long-held sockets.

When inference must run on site with unreliable connectivity, **AWS IoT Greengrass** deploys a **SageMaker**-trained model to edge devices as a component. It runs local **Lambda functions** for millisecond decisions and syncs models from the cloud when a connection exists.

## Worked scenario

A media company runs three generative workloads and one on-premises need. Its public website summarises articles on demand with unpredictable spikes; an internal newsroom dashboard rewrites headlines all day with strict latency targets; a fine-tuned open-weight image model generates thumbnails; and a fleet of field kiosks must caption photos even when the network drops.

Match each to its host. The website calls a **Bedrock** model from **Lambda** on demand: nothing idles, spikes scale automatically, and cost follows use. The newsroom dashboard has steady daytime volume and a latency target, so it runs on a **Bedrock Provisioned Throughput** commitment for its base load. The image model is not on **Bedrock**, so it goes to **SageMaker**: a **real-time endpoint** on a GPU instance for interactive thumbnails under six megabytes and sixty seconds, and an asynchronous endpoint for the large batch renders where minutes are acceptable and inputs are big. A small CPU classifier that tags images runs on **Serverless Inference** and scales to zero overnight.

The image model is a large transformer, so its container is a **SageMaker** **LMI container** with **tensor parallelism** set to the number of GPUs the weights actually need (two replicas per instance rather than one spread across all eight), a **maximum sequence length** matched to real requests so rolling batches are larger, weights **preloaded at container start** from uncompressed **S3** artefacts, and **auto scaling** on the **concurrent-requests metric**. A **shadow variant** receives copied traffic when a new model version is tested, and **deployment guardrails** roll back on alarms.

Cost is then trimmed: a small model handles the routine summaries and cascades to the large one on low confidence, semantic and **prompt caching** cut repeated work, and the batch renders move to off-peak. The kiosks get the captioning model through **AWS IoT Greengrass** with a local **Lambda function**, syncing new model versions when connectivity returns. The exam asks this scenario as "which deployment option fits each workload", "why is the GPU underutilised", and "how do we cut cost without losing quality"; the answers are the matches above.

## Exam lens

- "About 100 requests a day, only sometimes needs AI" → **Lambda** invoking **Bedrock** on demand.
- "Internal tool needs consistently low latency in peak season, public site spikes unpredictably, batch jobs need long processing" → **Provisioned Throughput** for the internal tool, **Lambda** **on-demand** for the site, a **SageMaker** endpoint (or **batch)** for scheduled jobs.
- "Proprietary models with custom pre- and post-processing plus general FMs" → hybrid **SageMaker** plus **Bedrock**.
- "70B model, slow cold starts, GPU memory exhaustion, uneven token throughput" → LLM-optimised containers with **tensor parallelism**, **lazy loading** and GPU-aware partitioning (**LMI**).
- "Weights fit in 4 of 8 GPUs, sequence lengths 10× smaller than configured, low concurrency" → **tensor parallelism** of 4 with two replicas per instance and a smaller **maximum sequence length**.
- "Image generation on GPUs, 50 MB text inputs, respond within 15 minutes" → **SageMaker Asynchronous Inference**; "near real time" for the same workload → real-time GPU endpoint.
- "Model under 5 GB, 40 to 60 concurrent real-time requests, no infrastructure to manage" → **SageMaker Serverless Inference**.
- "Most requests lightweight, few need deep reasoning, reduce cost and latency" → API-based **model cascading**.
- "Persistent **WebSocket** stream, **serverless** designs time out, no servers" → containers on **ECS** with **Fargate**.
- "On-site inference with intermittent connectivity, model updates from the cloud" → **IoT Greengrass** with **SageMaker**-trained models and local **Lambda**.

## Knowledge check

<!-- KC: E1-Q61, E1-Q12, E1-Q59, E2-Q44, PQ-Q19, E3-Q42, E2-Q28 -->
<!-- KC-BEGIN -->
### 1. Exam 1, question 61

A global hospitality company is building an FM-powered itinerary generator that serves both a public-facing website and an internal concierge dashboard. The concierge dashboard must support consistently low-latency responses during peak travel seasons, while the public website experiences unpredictable traffic spikes. The engineering team wants to optimize cost efficiency while ensuring high performance for the internal tool. They also need a fallback option for batch itinerary generation jobs that require longer processing times.

Which deployment strategy BEST meets these requirements?

- **A)** Use Amazon Bedrock serverless mode for the concierge dashboard and the public website, while using Lambda functions to run batch jobs that invoke the model through the Bedrock API.
- **B)** Use Amazon Bedrock provisioned throughput for the concierge dashboard, Lambda-based on-demand model invocation for the public website, and a SageMaker AI endpoint for scheduled batch itinerary generation.
- **C)** Deploy all inference through Lambda so both the dashboard and website automatically scale during traffic bursts, and use Lambda reserved concurrency to guarantee low-latency performance for the concierge tool.
- **D)** Use a single SageMaker AI endpoint for all traffic and scale it with automatic instance warm pools to handle seasonal spikes and batch workloads.

<details><summary>Answer</summary>

**Answer: B.** Provisioned Throughput gives the concierge dashboard consistently low latency at peak, Lambda-based on-demand invocation lets the public website scale with unpredictable spikes at pay-per-use cost, and a SageMaker endpoint handles scheduled batch itinerary jobs with longer processing. All-serverless with Lambda batch jobs lacks guaranteed low latency, reserved concurrency does not reserve Bedrock capacity, and one SageMaker endpoint for everything wastes cost and ignores Bedrock.

*Where this is covered: Unit 02, Deployment options and when each fits. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 2. Exam 1, question 12

A global consulting firm is building an internal GenAI assistant using Amazon Bedrock to help employees generate client summaries, rewrite emails, and answer policy-related questions. During pilot testing, the engineering team discovers that most daily requests are lightweight (grammar fixes, short rewrites, quick fact checks), while only ~8% of traffic involves complex multi-step reasoning. The team wants to reduce Bedrock costs and latency while maintaining high-quality responses for the small subset of complex queries.

Which deployment approach BEST meets these requirements?

- **A)** Automatically route every request to a SageMaker AI endpoint hosting a fine-tuned large model to maximize accuracy for all tasks.
- **B)** Use a single medium-sized model for all requests to avoid complexity and achieve predictable performance across all user queries.
- **C)** Implement an API-based model cascading strategy where a smaller, low-latency Bedrock model handles routine queries, and a larger, more capable FM is selectively invoked only when the task requires deeper reasoning.
- **D)** Deploy only the largest available Bedrock model and enable provisioned throughput to ensure consistently high performance for all query types.

<details><summary>Answer</summary>

**Answer: C.** API-based model cascading sends the lightweight majority of requests to a small, low-latency Bedrock model and escalates only the roughly eight percent that need deeper reasoning to a larger FM, cutting cost and latency while preserving quality where it matters. Routing everything to a fine-tuned large model, one medium model for all, or the largest model with Provisioned Throughput all pay premium prices for routine work.

*Where this is covered: Unit 02, Optimising cost and performance. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 1, question 59

A biotech research company is deploying a large 70-billion-parameter language model on Amazon SageMaker AI to summarize genomic experiment logs and generate structured reports. During testing, the team observes extremely slow cold-start times, GPU memory exhaustion, and uneven throughput under variable token workloads. The engineering lead wants a deployment strategy that ensures optimal GPU utilization, predictable token processing performance, and minimal startup delays while maintaining container flexibility for future model upgrades.

Which deployment strategy BEST meets these requirements?

- **A)** Use a container-based deployment pattern optimized for LLMs with tensor parallelism, lazy weight loading, and GPU-aware model partitioning to maximize memory efficiency and token throughput.
- **B)** Use Lambda-based invocation with increased memory allocation to accelerate model loading and reduce cold-start latency.
- **C)** Use a traditional ML container that loads the entire model into CPU memory first, then transfers it to the available GPUs during inference initialization.
- **D)** Use multiple smaller SageMaker endpoints behind an Application Load Balancer to distribute requests and avoid GPU memory pressure.

<details><summary>Answer</summary>

**Answer: A.** A container pattern optimised for LLMs uses tensor parallelism to spread a 70B model across GPUs, lazy weight loading to cut startup delay, and GPU-aware partitioning to maximise memory efficiency and token throughput while keeping the container flexible for upgrades. Lambda cannot hold the model, a classical container loading through CPU memory is slow and wasteful, and many small endpoints behind a load balancer do not solve per-request GPU memory needs.

*Where this is covered: Unit 02, What makes LLM deployment different. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 4. Exam 2, question 44

A media production company is building a text-to-image generation service using a pre-trained Hugging Face diffusion model that was tested successfully in Amazon SageMaker JumpStart. The engineering team now needs to deploy the model so users can generate images on demand through an internal application. The solution must use GPU instances for inference, support text description datasets up to 50 MB in size, and return responses in near real time to support interactive creative workflows. The company wants a deployment option that minimizes latency and delivers consistent performance under variable user load.

Which deployment strategy will meet these requirements?

- **A)** Use a SageMaker Real-Time Inference endpoint with a GPU-based instance type and invoke the endpoint directly from the application to generate images on demand.
- **B)** Create a SageMaker batch transform job that uses a GPU-based instance type and invoke the job from a Lambda function whenever a user submits a text prompt.
- **C)** Use a SageMaker Serverless Inference endpoint with a general-purpose instance type and invoke image generation through an AWS Lambda function.
- **D)** Use a SageMaker Asynchronous Inference endpoint with a GPU-based instance type and trigger inference through an AWS Lambda function to handle on-demand image generation.

<details><summary>Answer</summary>

**Answer: A.** A SageMaker real-time inference endpoint on a GPU instance returns image generations in near real time with consistent performance under variable load through auto scaling, and the application invokes it directly. The 50 MB figure describes the text-description dataset the service must support, not a single request: individual prompts are small, so the real-time endpoint's 6 MB payload and 60-second response limits are not the constraint here. Batch transform is offline, serverless inference is CPU only, and asynchronous inference trades interactivity for queued processing, which the near-real-time creative workflow rules out. Compare the official practice question in this unit, where inputs of 50 MB per request and a 15-minute tolerance make asynchronous inference the answer; the discriminator is per-request size and how long the user will wait.

*Where this is covered: Unit 02, Deployment options and when each fits. Key: ours, confidence medium.*

</details>

### 5. Official practice question set, question 19

A GenAI developer is implementing a solution to create images from text descriptions. The GenAI developer successfully tested a pre-trained Hugging Face model by using Amazon SageMaker JumpStart. Now, the GenAI developer needs to deploy the model so that users can generate images on demand.

The solution must use GPUs for inference. The solution must be able to handle text datasets up to 50 MB with image descriptions. The solution requires responses within 15 minutes.

Which deployment strategy will meet these requirements?

- **A)** Deploy a SageMaker Real-Time Inference endpoint that uses an accelerated computing SageMaker AI instance type. Create an AWS Lambda function for on-demand invocation of the SageMaker AI endpoint to manage image generation.
- **B)** Deploy a SageMaker Serverless Inference endpoint that uses a general purpose SageMaker AI instance type. Create an AWS Lambda function for on-demand invocation of the SageMaker AI endpoint to manage image generation.
- **C)** Deploy a SageMaker Asynchronous Inference endpoint that uses an accelerated computing SageMaker AI instance type. Create an AWS Lambda function for on-demand invocation of the SageMaker AI endpoint to manage image generation.
- **D)** Create a SageMaker AI batch transform job that uses an accelerated computing SageMaker AI instance type to manage image generation. Create an AWS Lambda function to start the batch transform job.

<details><summary>Answer</summary>

**Answer: C.** SageMaker Asynchronous Inference on an accelerated computing instance handles GPU-based image generation with inputs up to 50 MB and returns results within the 15-minute window, queuing requests and scaling to zero when idle. Real-time endpoints cap payloads at 6 MB and must answer within 60 seconds, serverless inference offers no GPUs, and batch transform is for offline datasets rather than on-demand requests.

*Where this is covered: Unit 02, Deployment options and when each fits. Key: AWS official answer.*

</details>

### 6. Exam 3, question 42

A transportation company is developing an Amazon Bedrock agent that provides dispatch recommendations based on live vehicle data. The agent uses Amazon SageMaker AI for ETA prediction and Amazon Comprehend to interpret driver feedback. The company must integrate a custom telemetry component that maintains a long-lived WebSocket connection to stream continuous GPS data into the agent.

The development team attempted serverless designs but encountered connection timeouts because the WebSocket stream requires a persistent network session. The company needs a fully managed deployment option that supports long-running connections without managing servers.

Which solution will meet these requirements?

- **A)** Deploy the telemetry tool on Amazon EC2 with a custom script to maintain the WebSocket session.
- **B)** Expose the telemetry component as a containerized application running on Amazon ECS with the AWS Fargate launch type to maintain persistent WebSocket connections.
- **C)** Deploy the telemetry component on Amazon App Runner as a containerized service with automatic scaling based on concurrent WebSocket sessions.
- **D)** Run the telemetry tool in AWS Lambda and periodically refresh the WebSocket session through scheduled invocations.

<details><summary>Answer</summary>

**Answer: B.** Amazon ECS with the Fargate launch type runs the telemetry component as a container without managing servers and holds persistent WebSocket sessions for as long as the task runs, which serverless functions cannot. EC2 means managing servers and Lambda cannot keep a persistent session. App Runner is the other defensible answer as a fully managed container service, but its request-driven scaling and HTTP service model suit request/response APIs better than long-held sockets; if the exam offers only App Runner as the managed container option, choose it.

*Where this is covered: Unit 02, Hosting the application and the edge. Key: ours, confidence medium.*

</details>

### 7. Exam 2, question 28

A global logistics corporation operates sorting centers in regions with limited or intermittent internet access. The company wants to automate real-time measurement of parcel dimensions using cameras deployed along conveyor belts.

The data-science team has already collected extensive video footage and will use Amazon SageMaker AI for model training. Amazon Rekognition will support initial labeling of package boundaries to accelerate dataset preparation. Because network connectivity is unreliable, the inference system must run entirely on-site, making routing decisions in milliseconds without requiring round-trip calls to the cloud.

The solution should minimize operational overhead, support continuous model updates from the cloud when connectivity is available, and allow local execution of both inference and simple post-processing logic.

Which solution best meets these requirements?

- **A)** Train the detection model in SageMaker AI and deploy it on Amazon ECS clusters running at each facility, using containers to run batch inference on incoming video frames.
- **B)** Use SageMaker AI to train an object-detection model and deploy it directly to AWS IoT Greengrass devices running at each site, with AWS Lambda performing local routing decisions using the model outputs.
- **C)** Deploy the trained model on SageMaker AI real-time inference endpoints and stream video to the cloud using Amazon Kinesis Video Streams for continuous evaluation.
- **D)** Use Rekognition Custom Labels for model training and deploy inference on local EC2 instances, sending routing results to the cloud through Amazon EventBridge.

<details><summary>Answer</summary>

**Answer: B.** Training in SageMaker and deploying the model to AWS IoT Greengrass devices at each site runs inference entirely on premises with millisecond routing decisions in local Lambda functions, and Greengrass pulls model updates from the cloud when connectivity is available. ECS clusters per facility and local EC2 add operational overhead, and cloud endpoints with Kinesis Video Streams need the network the sites lack.

*Where this is covered: Unit 02, Hosting the application and the edge. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

Deploy on **Bedrock** when a managed FM will do (**Lambda** for **on-demand**, **Provisioned Throughput** for steady low latency, batch for offline) and on **SageMaker** when you host the weights: real-time endpoints for GPU-backed low latency, **serverless** for small CPU models with idle periods, asynchronous for large payloads and long generations, **batch transform** for datasets, multi-model and **inference components** to share instances, and **Custom Model Import** to bring **SageMaker**-tuned models back into **Bedrock**.

LLMs need **LMI**-style containers with **tensor parallelism**, **continuous batching**, **quantisation** and tuned loading, on GPU families sized by profiling, updated with **deployment guardrails** and **production variants**. Cut cost with smaller task-specific models, cascading, caching, batching and right-sized scaling. Host long-lived application connections on **Fargate**, and edge inference on **Greengrass**.
