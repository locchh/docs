# Unit 03: Troubleshooting GenAI applications

**Task 5.2: Troubleshoot GenAI applications.** This unit is a diagnostic manual. It takes the five problem areas the exam guide names, content that does not fit the model, integration errors, prompts that misbehave, retrieval that returns the wrong thing, and prompt templates that decay over time, and for each gives the symptoms, the likely causes, the AWS tools that reveal them and the fixes. It ends with the troubleshooting toolkit that ties Domain 4's observability to Domain 5's evaluation.

## A method for GenAI troubleshooting

Classical services fail loudly: an exception, a 5xx, a timeout. GenAI applications often fail *quietly*: the call succeeds, the logs are clean, and the answer is wrong, incomplete or oddly formatted. Troubleshoot in layers:

1. Confirm that the **request** reached the model as intended. Was the prompt assembled correctly or truncated? Which template and version were used?
2. Confirm that the **model** did what was asked. Did it stop early? Was a **guardrail** applied? What did the response contain?
3. Check the **data the model was given**. Did retrieval return the right passages? Are the embeddings consistent?
4. Only then adjust the **prompt or the parameters**.

Use the same tools throughout:

- **Bedrock model invocation logs** show the full request and response.
- **CloudWatch Logs Insights** queries those logs.
- **AWS X-Ray** shows where time and failures occur across services.
- **CloudWatch metrics** and **evaluation jobs** help measure whether a fix worked.

## Content handling: when the model does not see everything

**Symptoms.** Summaries that drop what was near the end of a long document, answers that ignore part of the input, `ValidationException` errors saying the input is too long, or responses that stop mid-sentence.

**Diagnosis.** Two different limits are involved:

- The **context window** caps the tokens the model can take in. If the input exceeds it, **Bedrock** rejects the request with a validation error or returns `stopReason = model_context_window_exceeded`. An application that pre-trims the input may instead silently lose content.
- The **maximum output tokens** setting caps the response. When the model hits that cap, the response ends with `stopReason = max_tokens`, the signature of output truncation.

**Context window overflow diagnostics** means measuring both limits:

1. Count **input tokens** before the call. Use the **Bedrock CountTokens API** for supported models and the tokenizer otherwise.
2. Log `usage.inputTokens`, `outputTokens` and the stop reason for every call.
3. Chart the distribution of **input tokens** by document type in **CloudWatch**.
4. Alarm when requests approach the limit.

Truncation-related errors are then visible rather than guessed.

**Fixes.** Choose a technique that addresses the limit you found:

- **Dynamic chunking** splits long content on token boundaries that respect sections, visit dates or paragraphs instead of fixed sizes. Each segment then fits with room for the instructions and the answer.
- A **sliding window with summarisation** processes segments in order and carries a running summary forward, so context survives between chunks.
- **Map-reduce** summarizes each chunk and then summarizes the summaries.
- **Prompt design** puts instructions and the most important content first and asks for the output structure explicitly. A final consolidation pass stitches partial summaries together so nothing is lost.
- Raise `maxTokens` when the *output* is what gets cut.

Compressing files does not reduce tokens, manual shortening does not scale, and **CloudTrail** alerts on file size are not diagnostics. When a transcript truly exceeds the window and cannot be shortened, combine **overflow diagnostics**, **dynamic chunking** and prompt adjustments that stitch the parts consistently.

A related content-handling case is document ingestion. If **Amazon Bedrock Data Automation** classifies only the first page of multi-document PDFs and skips the rest, **enable document splitting** in the **BDA project**. Each logical document within the file is then detected, processed and matched to a **blueprint** independently.

Keep **one clear blueprint per document type** so matching is unambiguous. Multiplying **blueprint** variants or bolting on **Textract** or **Rekognition OCR** does not address that configuration problem.

## FM integration issues

**Symptoms.** Intermittent failures, malformed responses, requests that "fail silently" with nothing useful in the logs, latency spikes of unclear origin.

**Know the error catalogue.** Each **Bedrock** runtime error points to a different cause:

- `AccessDeniedException` (403): the **IAM** identity lacks the action, or **model access** is not enabled.
- `ValidationException` (400): a malformed body, an unsupported parameter, an input that is too long or a wrong model identifier.
- `ResourceNotFoundException` (404): a wrong model ID, ARN or Region.
- `ThrottlingException` (429): account quotas were exceeded.
- `ModelNotReadyException` (429): the model is warming up. The SDK retries automatically.
- `ServiceQuotaExceededException` (400, on `InvokeModel`): a quota was hit.
- `ModelTimeoutException` (408): the model took too long.
- `ModelErrorException` (424): the model failed while processing.
- `InternalServerException` (500): an AWS-side error that is retryable.
- `ServiceUnavailableException` (503): an AWS-side error that is retryable.

A response that is not an error can still be a failure. Check `stopReason` for `max_tokens`, `content_filtered`, `guardrail_intervened`, `model_context_window_exceeded`, `malformed_model_output` or `malformed_tool_use`. Also check for empty content and inspect the **guardrail action field**.

**Error logging.** Log every call in a structured form with request id, model id, prompt version, parameters, token counts and latency. Include the error code and its category: client, **throttling**, model or service.

Enable **model invocation logging** to capture the exact request and response. Store malformed responses for analysis rather than discarding them. **CloudWatch Logs Insights** can then group errors by type and time and correlate them with prompt patterns.

**Request validation.** Validate payloads before they reach **Bedrock**. Check:

- Required fields and types against a **JSON schema**.
- Parameter ranges, including **temperature** and tokens.
- Model-specific formats.
- Size limits.

Malformed requests then fail fast with a clear message instead of a cryptic validation error. **API Gateway request validators** do the same at the edge.

**Response analysis.** Validate the response against the expected schema. Look for patterns that indicate integration problems, such as repeated truncation, formatting breaks or empty answers. Retry with a **repair prompt** or fall back.

**AWS X-Ray** shows whether a latency spike comes from upstream validation, SDK retries or the model invocation itself. Retries appear as repeated **subsegments**, and **annotations** let you filter traces by model or prompt length.

When intermittent malformed or silent failures appear, combine **structured error logging** and **request validation**. Enable **invocation logging**, check payload schemas and store malformed responses for analysis. Synthetic queries to **DynamoDB** for manual inspection, **SNS** notifications on every invocation and wiki notes from staging reproductions are the distractors.

When the question is *where* the delay comes from, use **X-Ray traces** plus **Logs Insights** over prompt and response logs. **CloudTrail** event history, longer **Lambda** timeouts and custom scripts over **DynamoDB** do not locate that delay.

## Prompt engineering problems

**Symptoms.** Inconsistent tone, missing required attributes, quality that fluctuates across categories or after a prompt revision.

**Method.** Use a **prompt testing framework** to replace guessing with controlled comparison:

1. Run each prompt version against a fixed evaluation set containing real examples across product categories and edge cases.
2. Score the outputs automatically. Use a judge model or **Bedrock Evaluations** for **consistency**, **completeness** and tone, and **schema checks** for required attributes.
3. Compare versions side by side.

**Version comparison** relies on **Bedrock Prompt Management versions and variants**. The console can run them side by side on the same input, so every change is recorded, comparable and reversible.

**Systematic refinement** changes one thing at a time, such as instruction wording, examples, output format or parameters. Measure each change and keep what improves the score.

**Chain-of-thought analysis** exposes where reasoning goes wrong in complex prompts. **Prompt complexity metrics**, such as length, number of instructions and conflicting constraints, flag templates that confuse the model. **Fine-tuning** to fix a prompt, trying wordings by hand on a handful of examples, and raising **temperature** to "reveal issues" are the distractors.

## Retrieval system issues

**Symptoms.** "No relevant information found" for questions that used to work, irrelevant or outdated passages after a data refresh, recommendations that feel "off", slow retrieval.

**Model response relevance analysis.** On a sample, use a judge model or a **RAG evaluation job** to make two comparisons. Compare retrieved passages with the question to measure **context relevance**. Compare the answer with the passages to measure **faithfulness**. Falling **relevance** points at retrieval; falling **faithfulness** points at generation.

**Embedding quality diagnostics and vectorisation issues.** Consider the classic case: after a **Lambda** deployment, a **RAG** system returns fallback answers. The logs show no errors, **X-Ray** shows successful model invocations, and the **OpenSearch** cluster is healthy with normal latency.

Everything succeeds and nothing matches. The **query embeddings no longer live in the same space as the stored document embeddings** because the updated function calls a different **embedding model** or version. Two models of the same dimension fail silently with low similarity everywhere; a different dimension fails loudly at index time.

Use the same model for queries and documents, or **re-embed** the whole corpus with the new one. Deleted embeddings would show empty indexes, a missing **IAM** permission would raise `AccessDeniedException`, and **temperature** does not affect retrieval.

Other vectorization faults include:

- Chunks longer than the **embedding model**'s input limit, which get truncated before embedding.
- Inconsistent **text normalization** between ingestion and query.
- Mixed-language content used with a monolingual model.

**Drift monitoring.** Embeddings drift when the writing style or vocabulary of new documents moves away from what the index was built on. Recommendations or search quality then degrade gradually.

Detect this by comparing the distribution of live embeddings or similarity scores with a stored baseline. **SageMaker Model Monitor** with a **custom container** computes **embedding-drift statistics** against baseline vectors and exports reports to **S3**.

To test a retrained **embedding model** safely:

1. Deploy it as a **parallel endpoint** or **shadow variant** with **Data Capture** enabled. This endpoint feature writes request and response payloads to **S3** for analysis.
2. Shift a small share of traffic with `UpdateEndpointWeightsAndCapacities`.
3. Analyze the captured embeddings in **Model Monitor** before replacing the production endpoint.

Re-tagging text with a **Comprehend** classifier, nightly batch transforms with manual comparison and autoscaling do not measure drift.

**Chunking and preprocessing remediation.** If answers become irrelevant or outdated after a data refresh, validate the pipeline:

- Check for consistent **chunk boundaries**.
- Check for clean **metadata**.
- Check that the new text was segmented properly.
- Check that stale chunks were actually deleted.

Analyze **retrieved-context relevance** and **embedding drift** against historical similarity distributions. Raising **max tokens**, swapping to a larger **embedding model** without diagnostics, and reading **CloudTrail** for API sequences do not find the fault.

**Ingestion visibility.** For an **Amazon Bedrock Knowledge Base**, turn on **knowledge base logging** with **CloudWatch Logs** as the destination. **S3** and **Data Firehose** are alternative destinations. Use **Logs Insights** across all **S3** sources to find documents that failed parsing, lacked metadata or failed to vectorize.

Other logging services answer different questions:

- **Model invocation logging** covers inference, not ingestion.
- **CloudTrail** records API calls, not per-document outcomes.
- **CloudWatch Application Signals** monitors application performance, not **knowledge base** ingestion.

**Vector search performance.** When retrieval is slow rather than wrong, tune the **ANN index**, as covered in Domain 4 unit 02:

- Adjust `ef_search` and `m` for **HNSW**.
- Apply filters before search and bound the **top-k**.
- Keep indexes warm.
- Right-size shards or **OpenSearch Serverless** capacity.
- Benchmark **HNSW**, **IVF** and **product quantisation** on your own data.

## Prompt maintenance issues

**Symptoms.** After template updates: malformed JSON, missing required fields, "prompt confusion" where similar instructions get mixed up, failures that appear only for some templates or services.

**Fixes.** Use a separate check for each part of the template lifecycle:

- **Template testing frameworks** unit-test every template whenever it changes. Check that variables render, required sections are present and sample outputs satisfy the output schema.
- **CloudWatch Logs** captures all model invocations. Query the logs with **Logs Insights** to find confusion patterns and formatting failures in prompt-response pairs, grouped by template version.
- **AWS X-Ray** acts as a **prompt observability pipeline**. It traces assembly, template version, invocation and post-processing, with **annotations** for template id and version. This reveals the failing template and the stage where structure or latency breaks.
- **Schema validation** with **JSON Schema** detects output format inconsistencies as they occur and feeds them back into refinement. Disabling it to avoid false positives hides the problem.

**Systematic refinement workflows** and **prompt version management** close the loop. Longer timeouts and larger models do not fix a broken template.

## Watching tools and agents while troubleshooting

Agent workflows add tool calls to the failure surface. Problems include inconsistent tool latency, unexpected call sequences, mis-selected tools and coordination failures between agents. The managed framework combines:

- **CloudWatch metrics** for tool invocation duration, success rate, retry counts and error categories. Apply **CloudWatch anomaly detection** against historical baselines.
- **Bedrock model invocation logs** for the agent and its tools in **CloudWatch Logs**. Dashboards can then visualize call sequences and coordination behavior.
- Agent **traces**, covered in Domain 2 unit 01 and Domain 3 unit 05, and **AgentCore Observability spans**. These show the reasoning behind each call.

**Glue**-and-**Redshift** daily aggregation, **Firehose**-to-**OpenSearch** pipelines and external platforms through **CloudTrail Lake** are custom infrastructure the requirement excludes.

## The troubleshooting toolkit

Domain 2 unit 05 and Domain 4 unit 03 introduced these tools; here they are applied to diagnosis. Three tools together cover almost every troubleshooting question:

- **CloudWatch Logs Insights** centralizes and queries logs from every component with one query language. This includes application logs, **invocation logs** and **knowledge base** logs.
- **AWS X-Ray** traces requests across microservices and external integrations. It attributes cross-service error chains and slowdowns to a particular hop.
- **Amazon Q Developer** analyzes logs and code for FM-specific error signatures and suggests fixes. These signatures include context-length errors, content-policy rejections and malformed outputs.

This combination works without training a custom anomaly model or building specialized infrastructure. When a question adds **SageMaker** anomaly training, **Step Functions** error orchestration with **SNS**, or **Kinesis**-to-**OpenSearch** dashboards, it is describing the heavier alternative.

The same toolkit answers the "unified observability" questions that recur in this domain:

- Enable **Bedrock invocation logging** for request and response detail.
- Trace retrieval and orchestration steps with **X-Ray**.
- Publish business-impact and user-interaction measures to **CloudWatch** as **custom metrics**. Examples include clinician time saved, conversions and recommendation outcomes.
- Add **CloudWatch anomaly detection** on token usage and quality indicators.
- Unify operational telemetry and FM interaction details on **CloudWatch dashboards**, with **CloudTrail** supplying the request-level audit trail.

Hand-built consoles over **DynamoDB** or **S3** exports, **Kinesis**-to-**Athena** pipelines, **EMR** reports refreshed nightly and forwarding to an external **SIEM** are the custom analytics pipelines such questions exclude. **SIEM** means security information and event management system.

The FM-specific **troubleshooting frameworks** from Domain 4 unit 03 complete the kit:

- **Golden datasets** measure **hallucination**.
- **Output diffing** finds inconsistency across runs and versions.
- **Reasoning-path tracing** locates logical errors through **chain-of-thought logs**, agent **traces** and **invocation logs**.
- **Specialized observability pipelines** categorize failures and route them to remediation.

## Worked scenario

A logistics company's operations assistant has a bad Monday. Four tickets arrive: summaries of long incident reports stop before the end; the dispatch API sees intermittent **throttling** errors and occasional malformed JSON; the tone of customer notices changed after a prompt edit; and the **knowledge base** returns "no relevant information" for questions it answered last week. The on-call engineer works through them in layers.

Ticket one is content handling. **Logs Insights** over the **invocation logs** shows the stop reason is **max tokens** on the truncated summaries and a context-window error on the longest reports; the **CountTokens** API confirms the reports exceed the window. The fix is **dynamic chunking** on section boundaries with a **sliding window** and running summary, a final consolidation pass, and a higher output token limit.

Ticket two is integration. Structured error logs group the failures: ThrottlingException at the top of each hour when a batch job fires, and malformed JSON when the model hits its token cap mid-object. **X-Ray** traces show the delay sits in SDK retries, not in the model. The fixes are **exponential backoff with jitter** and a **concurrency limit** on the batch job, **API Gateway** per-client **throttling**, **JSON Schema** validation of requests and responses with a **repair prompt** on schema failure, and stored malformed responses for analysis.

Ticket three is prompt engineering. The new template is run against a fixed set of a hundred notices through a **prompt testing framework** that scores tone and required fields with a judge model, compared side by side with the previous **Prompt Management** version; a single instruction change is identified as the cause and reverted, and the template gains a unit test that runs on every edit.

Ticket four is retrieval. Everything is healthy and nothing matches, so the engineer checks the **embedding model** in the updated **Lambda function**: it moved to a new version while the index still holds old vectors. The corpus is re-embedded, **knowledge base logging** to **CloudWatch Logs** shows three documents that failed ingestion during the refresh, and a weekly drift check on embedding similarity distributions is added. The agent's tool metrics and anomaly baselines confirm no collateral damage. **Logs Insights**, **X-Ray** and **Amazon Q Developer**'s log analysis carried the whole day, which is the toolkit the exam expects you to name.

## Exam lens

- "Drops context at the end of long inputs, cannot shorten, prevent truncation" → **context window overflow diagnostics** plus **dynamic chunking** on token boundaries and prompt adjustments that stitch summaries.
- "Response ends abruptly" → `stopReason = max_tokens`; raise the output limit or ask for shorter output.
- "**BDA** classifies only the first page of multi-document PDFs" → enable **document splitting** in the project and keep one **blueprint** per document type.
- "Intermittent malformed or silent failures, validate requests, capture errors, analyse responses" → **structured error logging** with **invocation logging**, schema checks on payloads, stored malformed responses.
- "Is the delay in validation, SDK retries or the model? malformed inputs?" → **X-Ray** traces plus **Logs Insights** on prompt/response logs.
- "Which AWS error means what" → AccessDenied (permissions or **model access**), Validation (malformed or too long), ResourceNotFound (wrong ID or Region), **Throttling** (quotas), ModelTimeout, ModelError.
- "Inconsistent tone and missing attributes after a prompt revision, no trial and error" → a **prompt testing framework** with controlled evaluations across versions and automated scoring.
- "**RAG** returns 'no relevant information' after a code deploy; logs clean, invocations succeed, cluster healthy" → **embedding model version mismatch** between queries and stored vectors.
- "Irrelevant, outdated chunks after a data refresh" → validate chunking and preprocessing; analyse **context relevance** and **embedding drift**.
- "Recommendations feel off, suspect **embedding drift**, test safely" → **Model Monitor** custom container for drift statistics; **parallel endpoint** with **Data Capture** and gradual traffic shift.
- "Monitor **knowledge base** ingestion failures, query which documents failed" → **knowledge base logging** to **CloudWatch Logs** with **Logs Insights**.
- "Malformed JSON and prompt confusion after template updates" → **X-Ray** **prompt observability pipeline** plus **CloudWatch Logs** of all invocations for prompt-response analysis; keep **schema validation** on.
- "Tool latency, unexpected call sequences, anomalies against baselines" → **CloudWatch** tool metrics with **anomaly detection** plus **invocation logs** and dashboards.
- "Correlate logs, trace cross-service calls, detect GenAI error signatures, no custom ML" → **Logs Insights**, **X-Ray**, **Amazon Q Developer**.

## Knowledge check

<!-- KC: E2-Q40, E3-Q28, E2-Q16, E2-Q6, E2-Q64, E1-Q26, E2-Q59, E3-Q49, E1-Q6, E2-Q32, E2-Q47, E3-Q31 -->
<!-- KC-BEGIN -->
### 1. Exam 2, question 40

A media analytics company uses an Amazon Bedrock foundation model to extract insights from long interview transcripts. Recently, analysts reported that the model occasionally drops important context near the end of the transcript and produces incomplete summaries. The engineering team confirms that some requests are exceeding the model’s context window but cannot reduce transcript length due to business requirements. They need a systematic method to detect overflow conditions, ensure full content coverage, and prevent truncation-related errors during FM interactions without rewriting the summarization logic from scratch.

Which solution will BEST address these requirements?

- **A)** Enable CloudTrail logging for Bedrock API calls and configure SNS alerts when transcripts exceed a predefined size threshold.
- **B)** Require analysts to manually shorten long transcripts before submission and maintain a shared spreadsheet to track incomplete summaries.
- **C)** Implement an S3 event-triggered Lambda function that compresses transcripts before sending them to the model so they fit inside the FM’s input size limit.
- **D)** Enable context window overflow diagnostics and apply a dynamic chunking strategy that segments transcripts based on token boundaries, combined with prompt design adjustments that stitch summaries consistently without information loss.

<details><summary>Answer</summary>

**Answer: D.** Context window overflow diagnostics detect when transcripts exceed the model's limit, a dynamic chunking strategy segments them on token boundaries so every part is processed, and prompt design adjustments stitch the partial summaries consistently, which ensures full coverage without shortening transcripts or rewriting the summarisation logic. CloudTrail alerts on file size do not process the content, manual shortening violates the business requirement, and compressing files does not reduce the tokens the model must read.

*Where this is covered: Unit 03, Content handling: when the model does not see everything. Key: ours, confidence high.*

</details>

### 2. Exam 3, question 28

A healthcare research institute processes multi-page scientific reports that include handwritten annotations, scanned lab images, and typed experiment summaries. A Generative AI engineer configures Amazon Bedrock Data Automation (BDA) to classify each page and extract structured fields used for downstream indexing. For quality assurance, the engineer uses Amazon A2I to randomly review a subset of extracted pages.

The team created multiple custom blueprints, but only the first page of each PDF is reliably classified. Subsequent pages are inconsistently categorized or skipped entirely, causing missing metadata in the clinical document archive. The team must improve BDA’s page-by-page consistency without adding new custom processing logic or increasing operational overhead.

Which combination of actions will address these issues most effectively? (Select TWO.)

- **A)** Simplify and standardize blueprint names and maintain exactly one unique blueprint per document type category.
- **B)** Use Amazon Textract asynchronous analysis to ingest full PDFs as single documents, then infer content types from detected blocks.
- **C)** Turn on PDF page-level splitting in the BDA project to ensure every page is processed independently.
- **D)** Add multiple blueprint variations per document type category to maximize potential matching.
- **E)** Enable Amazon Rekognition DetectText and run OCR first to classify pages before passing them to BDA.

<details><summary>Answer</summary>

**Answer: A, C.** Turning on document splitting in the Bedrock Data Automation project makes BDA process each page or logical document independently and match it to a blueprint, and keeping exactly one clear blueprint per document type category makes that matching unambiguous, which fixes the skipped and misclassified pages without new processing logic. Ingesting full PDFs through Textract or pre-classifying with Rekognition OCR adds custom logic, and multiplying blueprint variants makes matching more ambiguous.

*Where this is covered: Unit 03, Content handling: when the model does not see everything. Key: ours, confidence high.*

</details>

### 3. Exam 2, question 16

A logistics optimization company integrates an Amazon Bedrock foundation model into its planning application. After deployment, developers observe intermittent failures where some requests return malformed responses, while others fail silently with no useful debugging information. The AI engineering team needs a method to diagnose and resolve these FM integration issues by validating requests, capturing detailed error logs, and analyzing problematic responses. The solution must minimize operational overhead and avoid adding unnecessary infrastructure.

Which approach will BEST help the team identify and fix these integration issues?

- **A)** Add a periodic Lambda function that sends synthetic queries to the model and writes the responses to a DynamoDB table for manual inspection.
- **B)** Enable CloudTrail logging for Bedrock API calls and configure an SNS topic to notify developers whenever the InvokeModel API is used.
- **C)** Implement structured error logging and request validation for all Bedrock API calls by enabling Amazon Bedrock invocation logging, adding schema checks on request payloads, and storing malformed FM responses for automated analysis.
- **D)** Require developers to replicate failing cases manually in a staging environment and document findings in an internal wiki.

<details><summary>Answer</summary>

**Answer: C.** Structured error logging and request validation for every Bedrock call, with model invocation logging enabled to capture the exact requests and responses, schema checks on payloads before they reach the model, and malformed responses stored for automated analysis, gives the team the evidence to diagnose intermittent malformed and silent failures with minimal infrastructure. Periodic synthetic queries written to DynamoDB for manual inspection do not capture the real failures, CloudTrail with SNS on every InvokeModel is noise rather than diagnostics, and manual reproduction with wiki notes is not a method.

*Where this is covered: Unit 03, FM integration issues. Key: ours, confidence high.*

</details>

### 4. Exam 2, question 6

A healthcare analytics company is developing a GenAI-based summarization service that uses Amazon Bedrock to generate HIPAA-compliant clinical summaries. After deployment, developers notice intermittent latency spikes and inconsistent model responses. The engineering team needs to identify whether the delays are caused by upstream validation logic, network retries in the AWS SDK, or Bedrock model invocation itself. They also need observability into prompt/response characteristics to detect possible malformed inputs.

Which approach BEST improves troubleshooting efficiency for this FM application?

- **A)** Enable AWS X-Ray tracing for the application and analyze invocation traces, then use CloudWatch Logs Insights to query prompt/response logs for pattern anomalies.
- **B)** Configure a CloudTrail trail to record all Bedrock API calls and search for latency anomalies in the event history.
- **C)** Increase the Lambda function timeout and analyze the function duration metrics in CloudWatch Metrics.
- **D)** Store every prompt and response in DynamoDB and periodically run custom scripts to detect malformed prompts.

<details><summary>Answer</summary>

**Answer: A.** AWS X-Ray traces show where each request spends its time, separating upstream validation logic, AWS SDK retries and the Bedrock model invocation, and CloudWatch Logs Insights queries over the prompt and response logs reveal malformed inputs and other pattern anomalies, which together locate the latency spikes and inconsistent responses. CloudTrail records API activity rather than latency breakdowns, a longer Lambda timeout hides the symptom, and custom scripts over DynamoDB add infrastructure without tracing.

*Where this is covered: Unit 03, FM integration issues. Key: ours, confidence high.*

</details>

### 5. Exam 2, question 64

A retail technology company is using an Amazon Bedrock foundation model to generate personalized product descriptions. After a new prompt revision, the AI engineering team notices inconsistent tone, missing required attributes, and fluctuating output quality across different product categories. The team wants to troubleshoot these prompt engineering issues using a structured method that compares prompt versions, analyzes differences in model behavior, and validates improvements before deployment. The solution must avoid trial-and-error prompting and require minimal manual inspection.

Which approach will BEST help the team improve response quality and diagnose prompt issues?

- **A)** Use a prompt testing framework that runs controlled evaluations across multiple prompt versions, compares output consistency, and measures quality changes using automated scoring to guide systematic refinement.
- **B)** Tune the foundation model with additional product data to reduce tone variation and regenerate product descriptions from scratch.
- **C)** Manually run the updated prompt against a small batch of example products and adjust wording until the responses look more consistent.
- **D)** Increase the model’s temperature parameter during generation to improve creativity and reveal hidden issues in the prompt design.

<details><summary>Answer</summary>

**Answer: A.** A prompt testing framework that runs controlled evaluations across prompt versions on a fixed set of products, compares output consistency and measures quality changes with automated scoring gives a structured, low-manual method to diagnose the revision and validate improvements before deployment. Fine-tuning the model to fix a prompt problem is expensive and indirect, manual wording adjustments on a small batch are trial and error, and raising temperature increases variation rather than diagnosing it.

*Where this is covered: Unit 03, Prompt engineering problems. Key: ours, confidence high.*

</details>

### 6. Exam 1, question 26

A financial research company operates a retrieval-augmented generation (RAG) system that answers analyst questions using internal investment reports. The system uses Amazon Bedrock to generate embeddings and stores them in an Amazon OpenSearch Service vector index. A Lambda function runs both embedding creation and KNN search. After a recent code deployment, the system begins returning fallback responses such as "no relevant information available," even for prompts that previously produced accurate answers. CloudWatch Logs show no errors. X-Ray traces confirm successful model invocations. The OpenSearch cluster is healthy, and query performance remains normal.

What is the MOST likely cause of this issue?

- **A)** The application increased the Bedrock model temperature parameter during the update, causing inconsistent retrieval results.
- **B)** The Lambda execution role is missing a new IAM permission required for Bedrock InvokeModel calls after the code update.
- **C)** The document embeddings in the OpenSearch index were overwritten or deleted during deployment, requiring full re-indexing.
- **D)** The updated Lambda function uses a different version of the embedding model, causing a mismatch between stored document embeddings and newly generated query embeddings.

<details><summary>Answer</summary>

**Answer: D.** Every component succeeds yet nothing matches, which is the signature of query embeddings that no longer share a vector space with the stored document embeddings: the updated Lambda function uses a different embedding model or version, so similarity scores collapse and the system falls back to 'no relevant information'. A temperature change affects generation rather than retrieval, a missing IAM permission would produce access errors in the logs and traces, and deleted embeddings would show an empty index rather than a healthy cluster with normal query performance.

*Where this is covered: Unit 03, Retrieval system issues. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 7. Exam 2, question 59

A healthcare analytics company uses a Retrieval-Augmented Generation (RAG) workflow on Amazon Bedrock to help clinical researchers summarize medical guidelines. After a recent data refresh, the AI engineering team notices that responses are increasingly irrelevant, missing key medical details, and referencing outdated chunks. The team must diagnose and resolve issues affecting retrieval quality. The solution must focus on identifying retrieval-specific failures, detecting embedding or vector drift, and validating that preprocessing and chunking remain effective.

Which combination of actions will BEST help the team identify and resolve the retrieval issues? (Select TWO.)

- **A)** Increase the FM model’s max tokens to ensure that more retrieved context fits within the generation window and reduces missing detail issues.
- **B)** Review and validate the chunking and preprocessing pipeline to ensure consistent boundaries, clean metadata, and proper segmentation of updated guideline text.
- **C)** Switch to a larger embedding model without diagnostics to boost similarity scores and reduce the likelihood of retrieval mismatches.
- **D)** Use CloudTrail logs to track which API calls were made during ingestion to identify incorrect retrieval sequences.
- **E)** Analyze retrieved context relevance compared to the user query and evaluate embedding vectors for drift using historical similarity distributions.

<details><summary>Answer</summary>

**Answer: B, E.** Reviewing and validating the chunking and preprocessing pipeline (consistent boundaries, clean metadata, proper segmentation of the refreshed guideline text) addresses the retrieval-specific failures introduced by the data refresh, and analysing retrieved-context relevance against the queries while evaluating embedding vectors for drift against historical similarity distributions detects embedding or vector drift. Raising max tokens changes generation rather than retrieval, switching embedding models without diagnostics guesses, and CloudTrail records API calls rather than retrieval quality.

*Where this is covered: Unit 03, Retrieval system issues. Key: ours, confidence high.*

</details>

### 8. Exam 3, question 49

A global financial analytics firm uses an FM embedding endpoint on Amazon SageMaker AI to generate embeddings for market reports, regulatory filings, and real-time analyst commentary. These embeddings feed multiple vector search indexes that power downstream recommendation engines for portfolio managers. The system also uses Amazon Comprehend for topic extraction and sentiment analysis to understand how market tone shifts across sectors.

Recently, analysts report that the recommendations feel “off” and no longer align with current market themes. The engineering team suspects drift in both the embedding distribution and the underlying writing style of analyst reports. They need to evaluate embedding drift using live endpoint traffic, compare it to baseline training data, and prepare the system for safe retraining—without impacting the production workload.

Which actions should the team take? (Select TWO.)

- **A)** Use SageMaker Model Monitor with a custom container to compute embedding-drift statistics, compare production data with stored baseline vectors, and export all drift reports to Amazon S3 for inspection.
- **B)** Enable a Comprehend custom classifier to re-evaluate the tone of incoming analyst text and automatically update vector database entries without using baseline comparisons.
- **C)** Set up a parallel SageMaker embedding endpoint with Data Capture enabled, gradually shift traffic using UpdateEndpointWeights, and analyze captured embeddings in SageMaker Model Monitor to identify drift before replacing the production endpoint.
- **D)** Run all incoming analyst reports through SageMaker Batch Transform jobs nightly and manually compare embedding vectors with old training data to detect distribution changes.
- **E)** Enable autoscaling on the embedding endpoint to handle higher traffic volumes and reduce latency issues during drift analysis.

<details><summary>Answer</summary>

**Answer: A, C.** SageMaker Model Monitor with a custom container computes embedding-drift statistics by comparing production embeddings with stored baseline vectors and exports the reports to S3, and a parallel embedding endpoint with Data Capture enabled, receiving a gradually shifted share of traffic through UpdateEndpointWeights, lets the team analyse captured embeddings in Model Monitor and validate a retrained model before replacing production. A Comprehend classifier rewriting vector entries without baselines measures nothing, nightly batch transforms with manual comparison are not monitoring, and autoscaling addresses capacity rather than drift.

*Where this is covered: Unit 03, Retrieval system issues. Key: ours, confidence high.*

</details>

### 9. Exam 1, question 6

A media analytics company uses an Amazon Bedrock knowledge base to index research articles stored across several Amazon S3 buckets. The company wants to closely monitor ingestion operations so that the engineering team can quickly identify failures such as parsing errors, missing metadata, or documents that failed to vectorize. The debugging process must support querying logs to isolate problematic documents and analyze ingestion patterns across all S3 sources.

Which solution will provide the required visibility into knowledge base ingestion and processing?

- **A)** Use Amazon Bedrock model invocation logging to capture detailed metrics for embedding generation and use the logs to track ingestion failures.
- **B)** Enable AWS CloudTrail to record API calls related to knowledge base operations and use CloudTrail Lake to analyze ingestion events.
- **C)** Configure knowledge base logging with Amazon CloudWatch Logs as the destination. Use CloudWatch Logs Insights to search for ingestion failures and analyze processing behavior.
- **D)** Enable Amazon CloudWatch Application Signals to automatically monitor ingestion performance and generate alerts for ingestion anomalies.

<details><summary>Answer</summary>

**Answer: C.** Knowledge base logging with CloudWatch Logs as the destination records the outcome of every ingested document, so CloudWatch Logs Insights can search for parsing errors, missing metadata and vectorisation failures and analyse ingestion patterns across all S3 sources. Model invocation logging covers inference calls rather than ingestion, CloudTrail records knowledge base API calls rather than per-document processing results, and CloudWatch Application Signals monitors application performance rather than knowledge base ingestion.

*Where this is covered: Unit 03, Retrieval system issues. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 10. Exam 2, question 32

A logistics automation company uses Amazon Bedrock to power a routing assistant that generates shipment instructions for warehouse workers. After recent updates to several prompt templates, the engineering team notices growing inconsistencies: incorrect JSON formatting, missing required fields, and occasional prompt confusion when processing similar instructions.

The team wants to troubleshoot these prompt maintenance issues by adding systematic observability, validating template structures, and detecting where specific prompts fail. The solution must minimize manual review and support ongoing refinement of multiple prompt templates across services.

Which actions will BEST help the team identify and resolve these prompt-related issues? (Select TWO.)

- **A)** Increase the foundation model’s inference latency timeout so longer instructions are processed, reducing confusion caused by template changes.
- **B)** Use AWS X-Ray to build a prompt observability pipeline that traces prompt flow, identifies failing templates, and surfaces latency or structure anomalies.
- **C)** Switch to a larger foundation model variant without performing diagnostics to compensate for prompt inconsistencies.
- **D)** Disable schema validation logic to avoid false positives during prompt template transitions.
- **E)** Enable CloudWatch Logs for all Amazon Bedrock model invocations and analyze prompt–response pairs to detect confusion patterns and formatting failures.

<details><summary>Answer</summary>

**Answer: B, E.** An X-Ray prompt observability pipeline traces each prompt's path, identifies which templates fail and surfaces latency or structure anomalies, and CloudWatch Logs for all Bedrock invocations let the team analyse prompt-response pairs to detect confusion patterns and formatting failures per template, which together give systematic observability with minimal manual review. Raising the inference timeout, switching to a larger model without diagnostics and disabling schema validation all hide the problem instead of finding it.

*Where this is covered: Unit 03, Prompt maintenance issues. Key: ours, confidence high.*

</details>

### 11. Exam 2, question 47

A logistics optimization company uses Amazon Bedrock Agents to orchestrate multiple tools that retrieve shipment data, calculate routing, and generate delivery recommendations. As tool usage increases, the engineering team notices inconsistent tool latency, unexpected call sequences, and occasional failures during multi-agent coordination. Leadership requires a tool performance framework that can track tool call patterns, measure tool execution metrics, detect anomalies against historical baselines, and provide full observability of agent-to-tool interactions. The team prefers a solution that minimizes custom infrastructure and leverages managed AWS services for insight generation.

Which combination of actions will BEST meet these requirements with the least operational overhead? (Select TWO.)

- **A)** Export all tool input/output payloads to S3 and build a daily AWS Glue ETL job to aggregate performance metrics. Store results in Amazon Redshift and create diagnostic dashboards in QuickSight.
- **B)** Use CloudWatch metrics to track tool invocation duration, success rate, retry counts, and error categories. Configure CloudWatch anomaly detection against historical patterns to identify unusual tool behavior.
- **C)** Deploy a Kinesis Data Firehose stream to capture tool interactions in near real time, enrich records with Lambda, and push aggregated data into OpenSearch for custom tool usage indexing and search.
- **D)** Forward agent and tool API activity logs to an external observability platform via CloudTrail Lake to analyze tool invocation patterns, cost trends, and correlation graphs.
- **E)** Enable Amazon Bedrock Model Invocation Logs for the agent and tools and send them to CloudWatch Logs. Use CloudWatch dashboards to visualize tool call sequences, agent coordination behavior, and performance metrics.

<details><summary>Answer</summary>

**Answer: B, E.** CloudWatch metrics for tool invocation duration, success rate, retry counts and error categories with anomaly detection against historical patterns track tool call patterns and flag unusual behaviour, and Bedrock model invocation logs for the agent and its tools in CloudWatch Logs with dashboards visualise call sequences, coordination behaviour and performance, all managed with the least overhead. A Glue-to-Redshift daily pipeline, a Firehose-Lambda-OpenSearch stream and an external platform fed through CloudTrail Lake are custom infrastructure.

*Where this is covered: Unit 03, Watching tools and agents while troubleshooting. Key: ours, confidence high.*

</details>

### 12. Exam 3, question 31

A global logistics company operates a real-time GenAI-enabled support platform that uses a foundation model for triaging customer cases, plus a computer-vision workflow for detecting damaged parcels. Recently, support engineers have encountered difficulty diagnosing system slowdowns, intermittent FM inference failures, and unpredictable error chains across several microservices.

The engineering leadership wants a fully integrated troubleshooting approach that allows the team to correlate logs from multiple components, trace cross-service API calls, and automatically detect GenAI-specific error signatures. The solution must accelerate debugging without introducing custom machine learning pipelines or specialized infrastructure.

Which solution meets these requirements MOST effectively?

- **A)** Configure Amazon CloudWatch Logs Insights to centralize and query system logs, enable AWS X-Ray to trace requests flowing through the GenAI microservices and external integrations, and use Amazon Q Developer to automatically analyze logs for FM-related error patterns and operational anomalies.
- **B)** Use Amazon CloudWatch Logs Insights to gather all logs, deploy Amazon Athena to run SQL queries on archived log data in Amazon S3, and integrate Amazon SageMaker AI to train a custom anomaly-detection model on historical error logs.
- **C)** Aggregate logs using CloudWatch Logs Insights, deploy AWS Step Functions to orchestrate cross-service error capture, and integrate Amazon EventBridge rules to trigger SNS alerts whenever the FM service encounters errors.
- **D)** Enable AWS X-Ray to track incoming and outgoing FM inference calls, stream application logs into Amazon Kinesis Data Streams for real-time processing, and store enriched logs in Amazon OpenSearch Service for downstream troubleshooting dashboards.

<details><summary>Answer</summary>

**Answer: A.** CloudWatch Logs Insights centralises and queries logs from every component, AWS X-Ray traces requests through the GenAI microservices and external integrations so cross-service error chains and slowdowns are attributable, and Amazon Q Developer analyses the logs for FM-related error patterns and anomalies, accelerating debugging without custom ML or specialised infrastructure. Training a SageMaker anomaly model, orchestrating error capture with Step Functions and SNS, and streaming logs through Kinesis into OpenSearch dashboards are the heavier alternatives.

*Where this is covered: Unit 03, The troubleshooting toolkit. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

Troubleshoot in layers: request, model, data, then prompt. For content that does not fit, diagnose with token counts and stop reasons and fix with **dynamic chunking**, sliding windows with summaries and prompt design (and **BDA** **document splitting** for multi-document PDFs).

For integration faults, know the **Bedrock** error catalogue, log every call in a structured form with **invocation logging**, validate requests against schemas, analyse responses and use **X-Ray** to place the delay. For prompt problems, test versions systematically with automated scoring and refine one change at a time.

For retrieval, check **relevance** and **faithfulness**, suspect an **embedding model mismatch** when everything succeeds and nothing matches, monitor **embedding drift** with **Model Monitor** and shadow endpoints, validate chunking after data refreshes, watch **knowledge base** ingestion in **CloudWatch Logs**, and tune the index for speed. For template decay, test templates, query **invocation logs**, trace prompts with **X-Ray** and keep **schema validation** on.

**Logs Insights**, **X-Ray** and **Amazon Q Developer** are the toolkit that ties it together.
