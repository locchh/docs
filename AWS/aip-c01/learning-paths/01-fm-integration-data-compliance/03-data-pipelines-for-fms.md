# Unit 03: Data pipelines for FM consumption

**Task 1.3: Implement data validation and processing pipelines for FM consumption.** Four skills sit under it:

- Validate data before a model sees it, with **AWS Glue Data Quality**, **SageMaker Data Wrangler**, **Lambda** and **CloudWatch**.
- Process text, image, audio and tabular data into model-ready form, with **Bedrock** multimodal models, **SageMaker Processing**, **Amazon Transcribe** and friends.
- Format requests to each model's schema: JSON for **Bedrock** APIs, payloads for **SageMaker** endpoints, and conversation formatting.
- Improve input quality so outputs improve, using **Bedrock** as a reformatter, **Amazon Comprehend** for entities and **Lambda** for normalisation.

A model is only as good as what you feed it. The questions in this task describe erratic model behaviour and trace it back to bad, inconsistent or badly formatted input, then ask for the managed pipeline that fixes it.

## Validate before you generate

Data quality has the same dimensions here as anywhere else:

- **Completeness**: no missing fields.
- **Accuracy**: values in range.
- **Consistency**: same format everywhere.
- **Timeliness**: fresh enough.
- **Conformance** to schema.

What changes is the consequence. Malformed JSON, missing fields or unexpected types make an FM produce erratic answers and make fine-tuning jobs unstable, and the model never tells you why.

**AWS Glue Data Quality** is the managed rules engine for structured and semi-structured data. You express rules in the **Data Quality Definition Language (DQDL)**, a small readable language with more than 25 rule types:

- `IsComplete "order_id"` and `IsUnique "order_id"` for presence and uniqueness.
- `ColumnValues "rating" in [1,2,3,4,5]` for allowed values.
- `ColumnLength "review_text" between 10 and 5000` for size.
- `RowCount > 1000` for volume.
- `ColumnDataType`, `ReferentialIntegrity` and `DataFreshness` for type, relationships and recency.
- `CustomSql` for anything you can express in SQL.
- `DetectAnomalies` for dynamic thresholds learned from history.

**Glue** can recommend a starter ruleset by profiling the data. Rules then run in two places:

- **Data at rest**, against tables registered in the **AWS Glue Data Catalog**. No code is needed, which suits data stewards.
- **Data in motion**, inside **Glue** ETL jobs, where a failing rule can stop the job or quarantine the bad records into a separate **S3** location, so only validated data reaches the curated bucket.

The **Glue Data Catalog** is the central metadata store of databases, tables and schemas. **Glue** crawlers populate it, and three services read it: **Athena** (serverless SQL over **S3**), **Redshift** (the data warehouse) and **Lake Formation** (fine-grained data permissions).

Each evaluation produces a **data quality score**, and results publish to **CloudWatch** metrics and **EventBridge**, so you can dashboard trends and alert on degradation. **Glue Data Quality** is built on the open source **Deequ** library.

**Amazon SageMaker Data Wrangler** is the visual, interactive counterpart, aimed at people preparing datasets for training or evaluation. You import data, build a transformation flow with built-in steps, and generate a **Data Quality and Insights report**. The report surfaces missing values, invalid values, outliers, duplicate rows, class imbalance, target leakage and a quick-model baseline.

Running the report on the entire dataset launches a **SageMaker Processing** job under the hood, which is **SageMaker**'s managed batch compute for data-processing scripts. A finished flow exports to a **SageMaker Pipelines** step or a **Processing** job, so the same validation runs every time the pipeline does. **Pipelines** is **SageMaker**'s managed ML workflow service, chaining processing, training, evaluation and registration steps.

The dividing line between the two: use **Data Wrangler** when the task is exploration and profiling of an ML dataset, and **Glue Data Quality** when the task is enforcing rules at scale on cataloged or streaming data.

**Custom Lambda validators** cover what no rules engine can express. That means domain checks, such as "the VIN matches the reported make and model" or "the procedure code is valid", and text checks such as minimum length, language detection and profanity. They are triggered by **S3** events, emit **CloudWatch** custom metrics for pass rates, and write results next to the data.

**CloudWatch** ties it together with custom metrics for validation results, alarms when quality drops below a threshold, and dashboards for trends. It also closes a feedback loop that routes failed records to human review and refines the rules based on how the model performs on them.

**Data that lives on premises.** Often the source is a database in the company's own data centre. Two connections reach it: an **AWS Site-to-Site VPN**, an encrypted IPsec tunnel over the internet, or **AWS Direct Connect**, a dedicated private line.

Three services then move the data, and the requirement wording picks one:

- **AWS Glue** ETL jobs connect over **JDBC**, the standard Java database connection, to **SQL Server**, **Oracle** or **PostgreSQL**. They select only the columns you name, transform, and write to **S3** on a schedule. This is the answer for "a daily extract of only the non-sensitive fields".
- **AWS DMS**, the Database Migration Service, replicates whole databases or tables continuously with **change data capture**, including table mappings and column filters. It suits migrations and near-real-time copies rather than filtered daily extracts.
- **AWS DataSync** copies files and objects between on-premises file systems and **S3** or **EFS**, so it moves documents, not query results.

**Kinesis** is for streams of events, not database extracts.

The anti-patterns are consistent across questions:

- One **Lambda** per field.
- All validation in a notebook, or in **Data Wrangler** by hand.
- Validation scripts on **EC2**.
- Relying on **Bedrock** guardrails to catch malformed input. **Guardrails** filter content for safety; they do not validate data.
- Lifecycle rules that assume newer data is cleaner.

## Process every modality into model-ready form

Modern applications feed models with more than text. The exam expects you to assemble a pipeline from managed services, each doing the part it is built for, orchestrated by **AWS Step Functions**.

**Step Functions** runs the branches for each data type in parallel with a **Parallel state**, fans out over large collections with **Map** and **Distributed Map**, retries transient failures, and keeps related items intact, such as the claim form, its photos and its call recording.

**Text.** **Amazon Comprehend** detects the dominant language, and extracts entities such as people, places, dates and quantities, plus key phrases and sentiment. It detects and redacts **PII**, and can be trained for **custom classification** and **custom entity recognition**. It also offers **toxicity detection** for user-generated content.

**Amazon Textract** pulls text, forms as key-value pairs, tables, signatures and answers to natural-language queries out of scanned documents and images, with confidence scores. Low-confidence fields can therefore be routed to **Amazon Augmented AI (A2I)** human review. **Amazon Translate** handles multilingual inputs before analysis, or before a model that is stronger in English.

**Audio.** **Amazon Transcribe** converts speech to text in batch, from files in **S3**, or streaming. It offers speaker diarization, custom vocabularies, automatic language identification and **PII** redaction.

**Transcribe Call Analytics** adds call-centre features: sentiment over the call, categories, talk time and interruptions, generative call summaries, and **PII** redaction, in post-call and real-time flavours. The canonical pipeline for call recordings is **S3** → **Transcribe** → **Comprehend** for entities and sentiment → **Bedrock** for the summary. **Amazon Polly** is text to speech, the opposite direction, and appears only as a distractor in ingestion questions.

**Images and video.** **Amazon Rekognition** detects labels, objects, text in images, faces, and unsafe content, and can be trained with **Custom Labels**.

For images that need to be cropped, resized, normalised or converted into tensors, **SageMaker Processing** jobs run your own scripts in managed containers, using **scikit-learn**, **Spark**, or a custom image, at batch scale. The same jobs handle tabular feature engineering and embedding generation.

**Bedrock** multimodal models, which include **Claude**, **Nova Lite** and **Pro**, and **Pixtral**, accept images directly in the prompt, and **Nova** accepts video. So for "understand what is in this picture" you can skip preprocessing and let the FM look.

**Documents at scale.** **Amazon Bedrock Data Automation (BDA)** is the managed, generative-AI-based extraction service for documents, images, audio and video. A **BDA** project defines **standard output**, such as summaries, transcripts, scene descriptions and extracted text, and optional **custom output** through **blueprints**, which are schemas of the fields you want, chosen from a catalog or written yourself.

Keep one blueprint per document type, and turn on **document splitting** when a single PDF holds several documents or must be classified page by page. **BDA** feeds **Knowledge Bases** as a parser for multimodal content, and it is the answer whenever a question wants classification plus field extraction from messy documents without writing **Textract**-plus-**Comprehend** glue code.

**Data fusion.** Once each modality is text or structured data, a final step assembles them into one coherent input: the transcript, the labels from the image, the extracted fields, plus metadata that says which came from where. That assembled object is what the FM receives.

When the source is a CRM, ticketing or ERP system rather than files, enrichment is event-driven instead. **EventBridge** delivers each record event to a **Lambda** function. The function calls **Comprehend** for entities and sentiment, and a **SageMaker** endpoint or **Bedrock** model for the prediction, then writes the enriched record back to the system. **BDA** processes files, meaning documents, images, audio and video, not database records, so it is the wrong tool for a CRM pipeline.

When the extracted results, such as labels, summaries and entities, must be *reported* rather than fed back into a model, the least-overhead pattern is to land them in **S3** and point **Amazon QuickSight** at them, directly or through **Athena**. **QuickSight** is AWS's serverless business-intelligence and dashboard service. A **Step Functions** workflow that calls a multimodal **Bedrock** model over the images and videos, writes results to **S3** and feeds a **QuickSight** dashboard is the "analyse fashion-show media and show trends" answer.

## Format the request the way the model expects

**Bedrock** accepts two request styles.

**`InvokeModel`** takes a body in the model provider's own format:

- **Anthropic** models use the **Messages** format, with `anthropic_version`, `max_tokens` and a `messages` array of `role`/`content` objects.
- **Amazon Titan Text** uses `inputText` with a `textGenerationConfig`.
- **Llama** and **Mistral** have their own prompt conventions.

Getting a field wrong is a validation error, and switching models means rewriting the body.

**`Converse`**, and `ConverseStream`, accepts one format for every chat model:

- A `messages` array of alternating `user` and `assistant` turns.
- An optional `system` prompt.
- `inferenceConfig` for max tokens, temperature, top-p and stop sequences.
- `additionalModelRequestFields` for model-specific extras such as top-k.
- `toolConfig` for function definitions.
- `guardrailConfig` to apply a guardrail.

Content blocks can be text, images as bytes or an **S3** location, documents such as PDF and DOCX with optional citations, and video for models that support them.

**Converse** is the tested answer to "developers send inconsistent payloads and get inconsistent behaviour". Standardise on one structured JSON request with role-based messages, system instructions and contextual metadata, rather than concatenating everything into a string.

**Conversation formatting** matters for dialogue applications. Models do not remember, so the application resends the history each turn as alternating user and assistant messages.

That history counts against the context window and the token bill, so manage it. Keep the last N turns, summarise older turns with the model itself, and store the full transcript in **Amazon DynamoDB** keyed by session so it can be reloaded. Unit 06 covers the state-management design. The distractors are sending only the latest message, which loses context, or flattening the whole conversation into one blob, which loses the turn structure the model was trained on.

**Dynamic prompt construction** assembles the final prompt from a template: system instructions, retrieved context, the user's message, and metadata such as region or priority, in clearly delimited sections. Templates live in **Bedrock Prompt Management**, covered in unit 06, or in your code. Either way, the assembly is code, not the user's typing.

**SageMaker endpoints** have their own contract. You send a payload with a content type the container's serialiser understands, which is JSON, CSV or JSON Lines for batch transform. Batch requests where the model supports it, and shape tensors to the model's expected input for custom models. The exam does not test container internals. It tests that "structured data preparation for **SageMaker AI** endpoints" is a distinct concern from **Bedrock**'s JSON schema.

**Multimodal payloads** carry images and documents as base64 bytes or **S3** references inside the same request, subject to per-model limits on size and count, and to the model's supported formats. Encode once, in the orchestration layer, not in the client.

Inference parameters, meaning temperature, top-p, max tokens and stop sequences, belong in the request too, and unit 02 explains how to set them. A **stop sequence** is the right control for "stop generating at this phrase".

## Improve the input to improve the output

Skill 1.3.4 turns a diagnosis into a design. Output quality degrades when the input is noisy and inconsistent: long email chains with signatures, inconsistent formatting, abbreviations, mixed units. The fix is a preprocessing stage in front of the main model.

Four tools do the preprocessing:

- Use **Bedrock itself as a reformatter**. A small, cheap model with a low temperature normalises text, expands domain abbreviations, fixes grammar, strips boilerplate, and converts free text into a fixed JSON structure before the main task prompt. This is cheaper and more reliable than asking the main model to clean and answer in one pass.
- Use **Amazon Comprehend** to extract and standardise entities such as names, dates, account numbers and locations, so the same facts always appear to the model in the same form. Its **PII** detection removes what should never reach the model.
- Use **Lambda** for deterministic normalisation: terminology mapping, unit conversion, whitespace and special-character handling, date formats, and assembling the final structured input.
- Enrich with reference data, such as product specifications, repair cost benchmarks and taxonomy terms, from knowledge bases or lookup tables, so the model has the context it needs.

Close the loop by tracking input quality metrics next to output quality metrics in **CloudWatch**. When the two correlate, you know which enhancement to invest in next. The distractors are "pass the raw text and let the model cope", "use only **Comprehend** and ignore formatting", and "forward the **S3** object unchanged".

## Worked scenario

An auto insurer wants a foundation model to write a first-draft accident summary from everything a claim contains: telematics JSON from the vehicle, a recorded call with the driver, photos of the damage, and a scanned incident report. Adjusters complain that today's drafts are erratic, and the data team traces the problem to the inputs.

Validation comes first. Telematics records arrive with missing speeds, timestamps in three formats and the occasional malformed document. An **AWS Glue** ETL job applies **Glue Data Quality** rules for completeness of the required fields, value ranges and schema conformance. It quarantines failing records into a separate **S3** prefix while publishing pass rates to **CloudWatch**, so only validated records reach the curated bucket. For the training and evaluation datasets the ML team builds in **SageMaker**, a **Data Wrangler** flow profiles the data and runs inside a **SageMaker Pipeline** each time.

Then every modality is turned into model-ready text.

- **Amazon Transcribe** converts the call to a transcript with speaker labels.
- **Amazon Rekognition** labels the damage photos.
- **Amazon Bedrock Data Automation** classifies and extracts the incident report, through one blueprint per document type with document splitting on for multi-page uploads.
- **Amazon Comprehend** extracts entities and sentiment from the free text.

A **Step Functions** workflow orchestrates these calls in parallel and hands the assembled inputs to a **Bedrock** multimodal model for the summary. When a source is a CRM record rather than a file, the enrichment is triggered by an **EventBridge** event instead.

The request itself is standardised. It uses the **Converse** API with a system instruction, role-based messages, the assembled context in a fixed order, a stop sequence that ends the summary before the model starts speculating, and a normalisation **Lambda** function that cleans noisy transcript text before it is sent. Extracted fields land in **S3** for a **QuickSight** dashboard of claim trends.

When a question describes erratic outputs from bad inputs, multi-modal sources to combine, or varied payloads from many developers, it is asking for exactly these pieces: rules-based validation, managed extraction per modality, a workflow to orchestrate, and one standard request shape.

## Exam lens

Task 1.3 questions describe a data problem and ask for the managed pipeline that prevents it.

- "Missing fields, wrong types, malformed JSON causing erratic FM behaviour" → **Glue Data Quality** rulesets in ETL jobs that fail or quarantine, publishing to **CloudWatch**, plus **Data Wrangler** flows in **SageMaker Pipelines** for the ML side.
- "Call recordings / photos / telematics / incident reports into one accident summary" → **Step Functions** orchestrating **Transcribe**, **Rekognition** or **SageMaker Processing**, **Comprehend**, and a **Bedrock** multimodal model; or **SageMaker Processing** batch jobs with **Transcribe** when the requirement stresses large-scale batch.
- "Classify and extract fields from mixed documents without custom models" → **Bedrock Data Automation** with one blueprint per type and document splitting on.
- "Developers send varied payloads to **Bedrock**" → a standardised JSON request with role-based messages and system instructions, which is the **Converse** API.
- "Degraded output from noisy email text" → **Bedrock** reformatting + **Comprehend** entities + **Lambda** normalisation.
- "Stop at a phrase" → **stop sequences**, never prompt wording or temperature.

## Knowledge check

<!-- KC: E3-Q18, E1-Q23, E3-Q64, E2-Q67, E3-Q13, PQ-Q16, E1-Q18, E2-Q9, PQ-Q9, E2-Q20 -->
<!-- KC-BEGIN -->
### 1. Exam 3, question 18

A global insurance provider is building a generative AI claims assistant that summarizes adjuster notes and recommends next actions by using an FM on Amazon Bedrock. Input data comes from multiple operational systems into an Amazon S3 data lake and is later consumed by SageMaker AI fine-tuning jobs. The data engineering team has discovered issues such as missing fields, unexpected data types, and malformed JSON payloads that cause erratic FM behavior and training instability. Leadership wants a standardized validation approach that can be reused across pipelines, exposes clear quality metrics, and blocks bad data before it is used for FM training or inference. The solution must use managed AWS capabilities and minimize custom infrastructure.

Which combination of steps will create a comprehensive, reusable data validation workflow for FM consumption with minimal operational overhead? (Select TWO.)

- **A)** Use SageMaker Data Wrangler to build reusable data preparation flows that profile input datasets, enforce schema and data-type checks, apply cleansing and outlier filters, and export only validated data to S3. Integrate the Data Wrangler flows into SageMaker Pipelines so that FM training and batch inference steps always consume the validated outputs.
- **B)** Rely on Amazon Bedrock guardrails to automatically filter low-quality or malformed input data at inference time and depend on model-level safety controls as the primary data validation mechanism.
- **C)** Implement AWS Glue Data Quality rulesets on datasets registered in AWS Glue Data Catalog. Integrate these rules into Glue ETL jobs that populate a curated S3 bucket for FM inputs, configure the jobs to fail or quarantine records on rule violations, and publish rule evaluation results as Amazon CloudWatch metrics and dashboards.
- **D)** Create an Amazon S3 Lifecycle configuration that periodically moves older raw datasets to S3 Glacier and assumes that only recent data is reliable enough for FM consumption, eliminating the need for explicit validation.
- **E)** Use a single AWS Lambda function triggered by S3 PUT events to run basic string length checks on uploaded objects. If checks pass, immediately invoke the FM; otherwise, log the errors to CloudWatch Logs without blocking downstream processing.

<details><summary>Answer</summary>

**Answer: A, C.** Glue Data Quality rulesets on Data Catalog datasets, embedded in Glue ETL jobs that fail or quarantine bad records and publish results to CloudWatch, enforce reusable rules for FM inputs; Data Wrangler flows in SageMaker Pipelines profile and validate the training and batch inference datasets. Guardrails filter content not data quality, S3 lifecycle rules do not validate, and a Lambda string-length check that never blocks is not validation.

*Where this is covered: Unit 03, Validate before you generate. Key: ours, confidence high.*

</details>

### 2. Exam 1, question 23

A transportation research institute is developing a generative AI system that analyzes a combination of driver call recordings, dashcam footage, vehicle telematics logs, and written incident reports to generate comprehensive accident summaries. The system must extract speech transcripts, detect objects and road conditions from images, normalize structured tabular sensor data, and format everything into a multimodal prompt for an Amazon Bedrock model.

The AI engineering team needs a scalable workflow that can preprocess all data types, convert them into FM-ready formats, and orchestrate the multimodal pipeline efficiently.

Which approach BEST meets these requirements?

- **A)** Create separate EC2 instances for each data type and have them run custom scripts, then upload the results to a shared S3 bucket for downstream model consumption.
- **B)** Perform all preprocessing manually and upload the processed audio, images, and CSV files directly into Amazon S3 for the FM to interpret without additional orchestration.
- **C)** Build a multimodal processing workflow using SageMaker Processing for image and tabular preprocessing, AWS Transcribe for audio-to-text conversion, and Amazon Bedrock multimodal models to consume the combined, formatted inputs.
- **D)** Use a single Lambda function to process all audio, image, and tabular data types before sending the raw binary content directly to Amazon Bedrock.

<details><summary>Answer</summary>

**Answer: C.** SageMaker Processing preprocesses images and tabular sensor data at scale, Amazon Transcribe converts the call audio to text, and a Bedrock multimodal model consumes the assembled inputs; that is the managed, orchestrated multimodal pipeline. Per-type EC2 scripts, manual preprocessing and a single Lambda pushing raw binaries do not scale or match model input requirements.

*Where this is covered: Unit 03, Process every modality into model-ready form. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 3. Exam 3, question 64

A global media analysis company is developing a multimodal generative AI pipeline that ingests customer-support phone recordings, product images, and troubleshooting notes. The goal is to build an FM-powered assistant that can summarize interactions, detect product defects, and extract structured issue categories. The data engineering team needs a standardized workflow to preprocess audio, images, and text before feeding them into a multimodal foundation model. The solution must support large-scale batch processing, avoid custom infrastructure, and ensure that each data type is transformed into FM-ready formats.

Which solution will meet these requirements with the least operational overhead?

- **A)** Use a single AWS Lambda function to perform audio transcription, image resizing, and text normalization for all file types as they arrive in S3.
- **B)** Depend on Amazon Bedrock alone to automatically convert raw audio, images, and tabular data into usable embeddings without any preprocessing workflows.
- **C)** Use SageMaker Processing jobs to run batch preprocessing scripts for all data types. Integrate Amazon Transcribe to convert audio to text, apply image preprocessing inside the Processing container, and output normalized text, image tensors, and metadata for downstream multimodal FM consumption.
- **D)** Create an AWS Glue ETL pipeline to extract, clean, and normalize all multimodal data into Parquet files, then pass the Parquet dataset directly into a multimodal FM.

<details><summary>Answer</summary>

**Answer: C.** SageMaker Processing jobs run batch preprocessing scripts for all modalities, with Amazon Transcribe converting audio to text and image preprocessing inside the container, producing normalised text, image tensors and metadata for the multimodal FM with no custom infrastructure. One Lambda for everything hits size and time limits, Bedrock alone does not preprocess raw media, and Glue to Parquet is not an FM input format for images and audio.

*Where this is covered: Unit 03, Process every modality into model-ready form. Key: ours, confidence high.*

</details>

### 4. Exam 2, question 67

A multinational logistics company operates customer support centers across Latin America, Europe, and Southeast Asia. The business needs to process support calls, field-inspection videos, and training recordings into English summaries so global teams can review incidents efficiently. The company already uses Amazon Kendra and Amazon Textract, but these do not address multilingual audio or video content.

The company needs the fastest-to-deploy solution that can convert audio/video to text, translate it into English, and generate concise summaries with a large language model—without building custom infrastructure and while scaling automatically across regions.

Which approach best meets these requirements?

- **A)** Deploy a custom generative model in Amazon SageMaker AI that performs transcription, translation, and summarization in a single end-to-end pipeline.
- **B)** Run all audio and video through a pre-trained embedding model in SageMaker AI, translate extracted entities with Amazon Translate, and use a Bedrock-connected Lambda function for summarization.
- **C)** Use AWS Glue to clean the multimedia data, run translation with Amazon Translate, and generate summaries using Amazon Lex.
- **D)** Utilize Amazon Transcribe for speech-to-text, Amazon Translate for English translation, and Amazon Bedrock with an LLM such as Jamba or Claude for summarization.

<details><summary>Answer</summary>

**Answer: D.** Amazon Transcribe converts the multilingual audio and video to text, Amazon Translate produces English, and a Bedrock LLM such as Claude or Jamba summarises, all managed and auto-scaling with nothing to build. A custom end-to-end SageMaker model, an embedding model for transcription, and Glue plus Lex misuse the services.

*Where this is covered: Unit 03, Process every modality into model-ready form. Key: ours, confidence high.*

</details>

### 5. Exam 3, question 13

A multinational museum consortium is modernizing its digital archive system to support intelligent search across decades of historical photographs, recorded interviews, documentary videos, handwritten field notes, and translated manuscripts stored in Amazon S3. The machine learning engineering team uses Amazon Bedrock AgentCore for workflow orchestration, while Amazon SageMaker AI handles batch transformations for existing structured datasets.

The curation staff—who are not ML specialists—must rapidly enable automated tagging and categorization of the newly ingested multimodal content without training any custom models, building pipelines, or managing compute infrastructure. The organization needs accurate cross-modal tagging to support entity search (people, locations, objects, dates), language detection, audio transcription, and image classification. The solution must integrate cleanly with AgentCore and be immediately usable by non-technical archivists.

Which approach provides the fastest, lowest-overhead method to automatically analyze and tag all multimedia assets?

- **A)** Leverage Amazon Comprehend, Amazon Transcribe, and Amazon Rekognition to automatically extract entities, speech transcripts, and image metadata for multimodal tagging across the media library.
- **B)** Deploy a farm of containerized inference jobs on AWS Batch to run open-source OCR, audio feature extraction, and custom clustering algorithms across the media archive.
- **C)** Convert the audio files with Amazon Transcribe and then train a SageMaker Neural Topic Model (NTM) and custom object-detection model to create topic and entity tags for the new media content.
- **D)** Configure Amazon Translate, Amazon Polly, and Amazon Lex to convert recorded interviews into multilingual conversational transcripts for use in metadata generation.

<details><summary>Answer</summary>

**Answer: A.** Comprehend (entities, language), Transcribe (audio transcripts) and Rekognition (image labels and metadata) tag the multimodal archive with no model training, pipelines or infrastructure, and their outputs feed AgentCore workflows. AWS Batch with open-source OCR, SageMaker topic and detection models, and Translate plus Polly plus Lex all require building or misuse the services.

*Where this is covered: Unit 03, Process every modality into model-ready form. Key: ours, confidence high.*

</details>

### 6. Official practice question set, question 16

A company wants to create an application to analyze fashion trends. The application must analyze videos and photos from public fashion shows to understand style elements and trends. The solution must store the extracted information and provide a dashboard that summarizes the fashion trends.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Use Amazon EventBridge to trigger AWS Lambda functions that use Amazon Quick Suite to analyze videos and photos from fashion shows. Store analysis results in Amazon S3. Deploy an Amazon Quick Sight dashboard with ML-powered trend analysis.
- **B)** Use Amazon Rekognition Custom Labels to train a custom model for fashion trend analysis. Store results in Amazon DynamoDB. Create a dashboard using Amazon Managed Grafana with custom plugins for fashion trend analytics.
- **C)** Use AWS Step Functions to process videos and photos from fashion shows by using Amazon Bedrock multimodal FMs. Store analysis results in Amazon S3. Use an Amazon Quick Sight dashboard to visualize trends in the data.
- **D)** Use an Anthropic Claude model in Amazon Bedrock to analyze text descriptions from fashion show videos and photos. Use Stable Diffusion for image analysis. Store results in Amazon OpenSearch Service. Create a dashboard by using Amazon Managed Grafana with OpenSearch visualizations.

<details><summary>Answer</summary>

**Answer: C.** Step Functions orchestrates Bedrock multimodal FMs to analyse the videos and photos, results land in S3, and a QuickSight dashboard summarises trends, all managed with the least overhead. Training Rekognition Custom Labels is unnecessary effort, Claude on text descriptions plus Stable Diffusion misuses an image generator for analysis, and Quick Suite in Lambda is not the analysis engine.

*Where this is covered: Unit 03, Process every modality into model-ready form. Key: AWS official answer.*

</details>

### 7. Exam 1, question 18

A global logistics company is developing a conversational assistant that provides shipment troubleshooting guidance to internal support teams. The system uses Amazon Bedrock for inference and must generate reliable answers using a structured prompt that includes the conversation history, user intent, and contextual metadata such as region and shipment priority. The AI engineering team notices inconsistent responses because developers are sending varied payload structures and unformatted text directly to the Bedrock endpoint.

To ensure consistent inference behavior across all environments, the lead AI engineer must enforce a standardized input format aligned with the Bedrock model's expected schema for dialog-style requests.

Which approach BEST satisfies this requirement?

- **A)** Store conversation history in DynamoDB and let the model retrieve it dynamically without requiring formatting in the API request.
- **B)** Append all conversation turns into a single newline-separated string and pass it as a single input field to the Bedrock API.
- **C)** Send plain text prompts directly to Bedrock and rely on the model to infer the missing structure from user input.
- **D)** Format each request using a standardized JSON structure that includes role-based message fields, system instructions, and contextual metadata before sending it to the Bedrock API.

<details><summary>Answer</summary>

**Answer: D.** Dialog-style Bedrock requests expect a structured JSON body with role-based messages, system instructions and context, which is what the Converse API standardises; enforcing that schema in the orchestration layer removes the payload variance causing inconsistent responses. Newline-joined strings, plain text and hoping the model fetches history from DynamoDB all ignore the model's schema.

*Where this is covered: Unit 03, Format the request the way the model expects. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 8. Exam 2, question 9

A GenAI engineer is developing a customer-support virtual assistant using an Anthropic Claude model on Amazon Bedrock. The assistant provides multi-sentence conversational responses, but the engineer needs the model to halt generation whenever a specific phrase such as “END_OF_SECTION” appears in the output. The application must enforce this behavior consistently without modifying the model weights or relying on prompt-only approaches.

Which solution will meet these requirements?

- **A)** Add the trigger phrase directly into the user prompt instructions to tell the model to stop when the phrase is generated.
- **B)** Tune the top-k sampling parameter to reduce the likelihood of the trigger phrase being generated in the output.
- **C)** Use the stop sequences parameter in the Bedrock inference request to define the trigger phrase that halts text generation.
- **D)** Adjust the temperature parameter to decrease randomness and reduce the chance of generating the trigger phrase.

<details><summary>Answer</summary>

**Answer: C.** The stop sequences parameter tells Bedrock to halt generation the moment the model emits the specified string, enforced by the API rather than by the prompt. Prompt instructions are unreliable, and top-k or temperature change randomness but never stop generation.

*Where this is covered: Unit 02, Inference parameters. Key: ours, confidence high.*

</details>

### 9. Official practice question set, question 9

A GenAI developer is building a virtual assistant application by using an Anthropic Claude model on Amazon Bedrock. The application sends user queries and expects conversational responses. The GenAI developer wants to configure the application to stop generating output after a specific phrase is generated in the response.

Which solution will meet these requirements?

- **A)** Add the trigger phrase "stop at this phrase" in the user prompt.
- **B)** Use the top-k parameter to control the diversity of tokens in the model's output.
- **C)** Use the temperature parameter in the inference call to control the likelihood of the phrase appearing.
- **D)** Use the stop sequences parameter in the inference call to specify a trigger phrase.

<details><summary>Answer</summary>

**Answer: D.** The stop sequences parameter in the inference call makes the model stop generating when the specified phrase appears. Prompt text is advisory, and top-k or temperature adjust sampling randomness rather than stopping output.

*Where this is covered: Unit 02, Inference parameters. Key: AWS official answer.*

</details>

### 10. Exam 2, question 20

A financial compliance team is building a generative AI assistant to summarize customer communications and detect potential regulatory risks. The incoming data includes long email chains, inconsistent formatting, embedded signatures, and unstructured free-text containing account numbers, dates, and names. The AI engineering team notices degraded FM output quality due to noisy text, missing extracted entities, and inconsistent input structure.

To improve the clarity and consistency of the data sent to the Amazon Bedrock model, the team needs a preprocessing workflow that standardizes text, extracts important entities, and formats inputs consistently before inference.

Which approach BEST meets these requirements?

- **A)** Store the raw email text in Amazon S3, retrieve it using a Lambda function, and forward it unchanged to the Bedrock model.
- **B)** Use Amazon Bedrock to reformat and clean text, Amazon Comprehend to extract key entities such as names and account IDs, and AWS Lambda to normalize and assemble the final structured input for the FM.
- **C)** Pass all raw email text directly to Amazon Bedrock and rely on the model to extract entities and clean formatting implicitly.
- **D)** Use only Amazon Comprehend to extract entities and ignore the formatting issues, allowing the FM to handle inconsistencies during inference.

<details><summary>Answer</summary>

**Answer: B.** Using Bedrock to reformat and clean the text, Comprehend to extract entities such as names and account identifiers, and Lambda to normalise and assemble a consistent structured input is the input-enhancement pipeline the task statement describes. Forwarding raw text unchanged, relying on the model to clean implicitly, or extracting entities while ignoring formatting leaves the noise that degrades output quality.

*Where this is covered: Unit 03, Improve the input to improve the output. Key: ours, confidence high.*

</details>

<!-- KC-END -->

## Summary

Validate structured data with **Glue Data Quality** rules, which fail or quarantine records and publish to **CloudWatch**. Profile ML datasets with **Data Wrangler**'s insights report inside **SageMaker Pipelines**, and cover domain rules with **Lambda**.

Convert each modality with the managed service built for it, under a **Step Functions** workflow, then fuse the results:

- **Transcribe** and **Call Analytics** for audio.
- **Textract** and **Bedrock Data Automation** for documents.
- **Rekognition** and **SageMaker Processing** for images.
- **Comprehend** for text.

Send requests in the model's schema, preferably the **Converse** API's unified messages format with a system prompt, role-based history and inference parameters, and manage conversation history deliberately.

When output quality suffers from noisy input, clean it first with a cheap **Bedrock** model, **Comprehend** entity extraction and **Lambda** normalisation, and enrich it with reference data.
