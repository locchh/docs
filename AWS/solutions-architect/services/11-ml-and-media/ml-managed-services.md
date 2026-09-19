# Managed AI services on the exams

**Where it sits on the exams.** The managed artificial intelligence (AI) services are single-purpose APIs that take an input you already have and return a result a machine learning model produced, with nothing to train and no inference infrastructure to run. Both exams test them as a selection problem rather than a machine learning problem: the question describes an input and a desired output, and the keyed answer is the service that does exactly that conversion. They appear in SAA-C03 tasks 2.1 and 2.2, where the guide names "AWS Managed Services with appropriate use cases, for example Amazon Comprehend, Amazon Polly" and "using purpose-built AWS services for workloads", and in SAP-C02 tasks 2.5 and 3.3, where the skills are developing a process methodology for selecting purpose-built services and proposing opportunities for the adoption of managed services. The rule of thumb is that an option describing a model built, trained or hosted to do something an API already does is wrong; the exam keys the training platform only when the task is specific to the company's own data and no purpose-built API covers it.

## Matching an input to an output

Find the row whose input column matches what the scenario already has and whose output column matches what it asks for. The scope column tells you whether the service is worth your study time: SAA-C03 lists Comprehend, Lex, Polly, Rekognition, SageMaker AI, Textract, Transcribe and Translate on its Machine Learning list, and SAP-C02 lists all of those plus Fraud Detector, Kendra and Personalize.

| Input the scenario has | Output it asks for | Service | Exam scope |
|---|---|---|---|
| Free-form text: reviews, emails, support tickets, social posts | Entities, key phrases, dominant language, sentiment, PII spans | **Amazon Comprehend**, the natural language processing service | Both exams |
| Text in one language | The same meaning in another language | **Amazon Translate**, the neural machine translation service | Both exams |
| Recorded or live audio | A text transcript | **Amazon Transcribe**, the automatic speech recognition service | Both exams |
| Text | Spoken audio | **Amazon Polly**, the text to speech service | Both exams |
| A photo or a video file | Labels, faces, celebrities, moderation labels, text in the picture | **Amazon Rekognition**, the image and video analysis service | Both exams |
| A scanned form, invoice, identity document or PDF | Words, key-value pairs, table cells and answers to questions about the page | **Amazon Textract**, the document text extraction service | Both exams |
| A typed or spoken user utterance | A matched intent with its slots filled, plus a fulfillment call | **Amazon Lex**, the conversational interface service | Both exams |
| A natural language question over a document repository | Ranked passages and answers with their source documents | **Amazon Kendra**, the managed intelligent search service | SAP-C02 only |
| A history of users interacting with items | Ranked recommendations, or segments of users | **Amazon Personalize**, the managed recommendation service | SAP-C02 only, named on the SAA-C03 out-of-scope list |
| An online event such as a sign-up or a payment | A fraud score and an outcome such as approve or review | **Amazon Fraud Detector**, the managed online fraud detection service | SAP-C02 only |
| Your own labeled data and your own algorithm | A trained model, plus an endpoint or a file of predictions | **Amazon SageMaker AI**, the managed platform for building, training and deploying models | Both exams |

Three of those rows carry a status note the exam has not caught up with. Amazon Kendra is no longer open to new customers, and AWS directs new work to **Amazon Bedrock Knowledge Bases**, the managed retrieval augmented generation capability of **Amazon Bedrock**, the service that serves foundation models through one API. Amazon Fraud Detector stopped accepting new customers on November 7, 2025, with Amazon SageMaker AI, AutoGluon and **AWS WAF**, the managed web application firewall named as the replacements. Amazon Comprehend kept all of its headline features but closed topic modeling, event detection and prompt safety classification to new customers, keeping access for accounts that used them in the previous twelve months. Answer the exam question with the service the guide names, and carry the status note separately as what you would tell a real customer.

Almost every one of these services reads its input from and writes its output to **Amazon Simple Storage Service (Amazon S3)**, the object storage service, and is wired into an application by **AWS Lambda**, the event-driven compute service, running on an S3 event notification. An object lands in a bucket, a function calls one AI API, and the result goes to a table, a queue or another bucket. Nothing in that path needs a server, so the "LEAST operational overhead" wording usually points at it. The distractor to recognize is the custom build: training a model on a fleet of instances, or running an open-source library in a container, to produce an output one of these APIs returns from a single call. It loses on "MOST cost-effectively" as well.

## Language services: Comprehend, Translate, Transcribe and Polly

Amazon Comprehend takes UTF-8 text and returns insights from pre-trained models you never have to train: entities such as people, places and items; key phrases; the dominant language; sentiment as positive, negative, neutral or mixed; targeted sentiment, which attaches a sentiment to each entity rather than to the document; syntax, meaning the part of speech of each word; and personally identifiable information (PII) such as addresses and account numbers, returned with the character offsets a redaction step needs. You can call it in real time for small workloads or start an asynchronous job over a large document set in Amazon S3, and that choice is often the whole question: one document now means real-time analysis, a repository of millions means a job. Amazon Comprehend Custom adds two trainable models, custom classification for your own categories and custom entity recognition for your own terms, both built by automatic machine learning from data you already have, with flywheels managing their retraining and versioning over time. The cost detail that decides a question is that a custom model used for real-time requests needs an endpoint, and you pay for it from the moment you start it until you delete it, so an idle custom endpoint is a standing charge in a way the pre-trained APIs are not. **Amazon Comprehend Medical**, a separate service with separate pricing, detects medical entities and protected health information in clinical text in US English and links them to ontologies including ICD-10-CM, RxNorm and SNOMED CT.

Amazon Translate converts text between languages. Real-time translation accepts plain text or a single plain text, HTML or Word file, and a batch job translates a whole collection of files in Amazon S3, adding Excel, PowerPoint and XLIFF to the supported formats and returning each output in the same format as its input. Custom terminology pins how a specific term such as a brand name must be translated, and parallel data, the feature AWS also calls Active Custom Translation, adapts the output to the style, tone and word choices in example translations you supply. Do-not-translate tags protect marked spans of HTML, and profanity masking, brevity and formality settings adjust the register and length of the output. Setting the source language to `auto` makes Amazon Translate call Amazon Comprehend on your behalf to detect it, which is why a scenario with user-generated content in unknown languages needs no separate language-detection step.

Amazon Transcribe takes audio in and returns text. It runs in two modes, streaming for real time and batch over media files in an S3 bucket, and a scenario that says "as the call is happening" needs streaming while "transcribe the archive" needs batch jobs. Its features are the ones a transcription pipeline usually has to build by hand: language customization to teach it domain vocabulary, content filtering and PII redaction, multi-channel audio analysis, and partitioning the speech of individual speakers, which is what a stem means when it says the transcript must attribute each sentence to a speaker. It bills per second of transcribed audio with no minimum duration. Call Analytics is the packaged variant for contact center audio, and **Amazon Transcribe Medical** transcribes clinician dictation and physician-patient conversations in US English through either streaming or batch. Both medical services still exist and neither is closed to new customers, which matters because the pairing that decides a healthcare question is Amazon Transcribe Medical for the audio and Amazon Comprehend Medical for the entities in the resulting text.

Amazon Polly turns text into lifelike speech. It offers generative, long-form, neural and standard text-to-speech voices, and the neural engine supports a Newscaster speaking style for narration. You pay only for the text you synthesize, and you may cache the generated audio and replay it at no further charge, which is the fact behind any question about an application that reads the same fixed content to many users: synthesize once, store the audio in Amazon S3, serve it from there. The four services chain, and the exam likes the chain: Amazon Transcribe produces a transcript, Amazon Translate localizes it, Amazon Polly voices the result, and Amazon Comprehend extracts what mattered from any stage of it.

## Vision and documents: Rekognition and Textract

Amazon Rekognition analyzes images and videos without any model training. On images it detects objects, scenes and concepts as labels; detects printed and handwritten text; flags explicit, inappropriate and violent content as moderation labels; recognizes tens of thousands of celebrities; detects, analyzes and compares faces with attributes; detects personal protective equipment on people in a frame; and reports image properties such as sharpness and contrast. Facial search works through a face collection, an index of faces you own: you index faces once, then search images, stored video or streaming video against the collection, which is the pattern behind every identity verification scenario. Rekognition Face Liveness detects whether a real person is in front of the camera, defeating printed photos, replayed video and deepfakes injected into the capture path, and it is the answer whenever a stem worries about spoofing rather than matching. Rekognition Custom Labels trains a classifier on your own images for objects a general model does not know, such as your logos or your parts. On video it adds people pathing and segment detection for black frames and end credits.

The limits are set quotas that cannot be raised, and one of them decides questions. An image passed to the API as raw bytes may be no larger than 5 MB, while an image read from an Amazon S3 object may be up to 15 MB, so a scenario with large photographs must stage them in a bucket rather than inline them in the request. Only PNG and JPEG are supported, and stored video analysis accepts files up to 10 GB and six hours encoded with H. Streaming analysis reads from **Amazon Kinesis Video Streams**, the service that ingests video from devices, and writes results to **Amazon Kinesis Data Streams**, the managed streaming data service.

Amazon Textract is the document counterpart, and the distinction the exam draws is sharp: Amazon Rekognition finds text that happens to be in a picture, Amazon Textract understands the structure of a document. `DetectDocumentText` returns the words and lines. `AnalyzeDocument` returns key-value pairs from forms, cells from tables, signature locations, layout, and answers to Queries, which are plain English questions such as "what is the policy number" asked directly of the page, with Custom Queries trained on your own samples when the pretrained ones miss. `AnalyzeExpense` is specialized for invoices and receipts, `AnalyzeID` for driver's licenses and passports issued by the US government, and the Analyze Lending workflow classifies the pages of a mortgage loan package and routes each to the right operation. Synchronous operations handle single-page documents where latency matters; asynchronous operations exist because multipage documents cannot be processed in one call. The combination question is common: Amazon Textract extracts the fields, Amazon Comprehend classifies or redacts what they contain, and the pair replaces a manual data entry team and a homegrown optical character recognition (OCR) stack at once.

## Conversation and enterprise search: Lex and Kendra

Amazon Lex builds conversational interfaces over voice and text using the same automatic speech recognition and natural language understanding that sits behind Alexa. A bot supports one or more languages and one or more intents, where an intent is an action the user wants to take, described by sample utterances of how they might ask for it. An intent requires zero or more slots, the parameters the bot must collect before it can act, and each slot has a slot type, either a built-in type or an enumeration you define. Amazon Lex prompts for missing slots, keeps context across turns, and falls back to a built-in fallback intent when it cannot work out what the user meant. Fulfillment is where the conversation becomes an action, and AWS recommends a Lambda function for it, which is the integration nearly every question expects: Lex understands, Lambda does. A bot is published as a numbered version and reached through an alias, so client applications point at the alias and get the new version without changing. Bots deploy to web and mobile applications and to chat platforms, and Amazon Lex integrates with **Amazon Connect**, the managed contact center service, to put the same bot in front of a phone line.

Amazon Kendra is in scope for SAP-C02 only, and it does semantic search over enterprise content: you connect repositories to an index, Kendra crawls and ingests the documents, and a natural language question returns ranked passages rather than a list of keyword matches. It answers factoid questions with a fact, descriptive questions with a passage, and ambiguous keyword queries by inferring which meaning was intended. Results respect your organization's security model and can be filtered by the user or group entitled to each document, which is the requirement that separates Kendra from a plain search index in a question. Two facts matter more than the features. First, pricing is per provisioned index per hour once the trial ends, charged even when the index is empty and nobody queries it, which makes Kendra expensive in exactly the way a "MOST cost-effective" stem punishes. Second, Amazon Kendra is no longer open to new customers, and AWS points new work at Amazon Bedrock Knowledge Bases, though existing Kendra GenAI indexes remain usable from there and from **Amazon Q Business**, the enterprise assistant. Where a question wants full-text and log search rather than question answering, the answer is [**Amazon OpenSearch Service**](../09-analytics/opensearch.md), the managed search and log analytics service, not Kendra.

## Recommendations, fraud and forecasting

Amazon Personalize generates item recommendations for individual users and segments of users who share an affinity, using the technology behind recommendations on Amazon's own retail site. Its primary input is interaction data, meaning records of users clicking, watching or buying items, supplied both as historical records in bulk and as real-time events, optionally enriched with item and user metadata such as genre or price. You can start from a use-case optimized recommender for a business domain, which gives you recommendation types such as "more like this" or "frequently bought together" with no configuration, or build custom resources when none matches. It serves both real-time API calls and batch jobs, and it can re-rank results that Amazon OpenSearch Service produced so that search output is personalized too. The scope note is the important part for study planning: Personalize is on the SAP-C02 Machine Learning list and is named explicitly on the SAA-C03 out-of-scope services list, so an Associate candidate should recognize the name and spend no more time on it.

Amazon Fraud Detector, also SAP-C02 only, scores online events for fraud. You supply historical event data labeled fraudulent or legitimate, the service trains a model that combines your patterns with what AWS has learned from two decades of fraud detection at Amazon, and you then write rules that turn a model score into an outcome such as approve, review or block. It is built for unauthorized transactions and fake account creation, and the giveaway wording is a decision made per event as it happens rather than a report produced later. It closed to new customers on November 7, 2025, with SageMaker AI, the AutoGluon open-source library and AWS WAF, the web application firewall, named as the paths forward.

Two more services are worth a sentence so that you can rule them out. **Amazon Forecast** is the managed time series forecasting service for predicting demand, staffing or capacity from historical measurements; it is no longer available to new customers, existing customers may keep using it, and AWS directs new work to **Amazon SageMaker Canvas**, the no-code machine learning interface. It appears on neither exam's in-scope Machine Learning list. **Amazon CodeGuru**, the machine learning code review and application profiling service, sits outside this unit despite being a machine learning service: SAP-C02 lists it under Developer Tools rather than Machine Learning, it is absent from the SAA-C03 list, and it is taught in [developer tools and CI/CD](../08-management/developer-tools-and-cicd.md). CodeGuru Reviewer stopped accepting new repository associations on November 7, 2025, and it is not DevOps Guru, which is the different service the SAA-C03 out-of-scope list names.

## Amazon SageMaker AI: build, train and deploy

Amazon SageMaker AI is the fully managed platform for the machine learning lifecycle, and it is the answer when the task genuinely needs a model of your own. On December 3, 2024, Amazon SageMaker was renamed to Amazon SageMaker AI, and the name Amazon SageMaker was reused for a unified platform for data, analytics and AI that contains SageMaker AI alongside SageMaker Lakehouse, SageMaker Unified Studio and Amazon Bedrock. The rename changed nothing operational: the `sagemaker` API namespace, the CLI commands, the `AmazonSageMaker` managed policy names and the `AWS::SageMaker` CloudFormation resource types all stayed as they were. Both exam guides already say SageMaker AI.

The loop is prepare, build, train, deploy. You prepare and label data, usually landing it in Amazon S3. You build in a managed notebook environment, choosing between SageMaker AI's built-in algorithms, a supported framework such as PyTorch or TensorFlow in a prebuilt container, your own container, or a pretrained model from **Amazon SageMaker JumpStart**, the model and solution catalog. You train by submitting a training job that SageMaker AI runs on instances it provisions and terminates for you, with distributed training when the data warrants it and automatic model tuning to search hyperparameters. You then register the model artifact and deploy it, by one of three paths that scale with the team: JumpStart in the console for a no-code deployment, the `ModelBuilder` class in the Python SDK for fine-grained control, and CloudFormation or the AWS SDK for Python for repeatable deployment at scale.

The choice a Professional question most often turns on is which of the four inference options to use, because they differ by payload size, latency and whether a persistent endpoint exists at all. Read the table for the deciding constraint in each row.

| Option | Shape of the workload | Key limits | Idle cost |
|---|---|---|---|
| Real-time endpoint | Interactive request and response, low latency | Request body up to 6 MB, container must respond within 60 seconds | Instances run continuously |
| Serverless inference | Intermittent or unpredictable traffic that tolerates a cold start | Memory 1 GB to 6 GB, up to 200 concurrent invocations per endpoint, 50 serverless endpoints per Region | Scales to zero between requests |
| Asynchronous inference | Large payloads or long inference, near real-time rather than interactive | Payload up to 1 GB, processing up to one hour, requests queued | Can autoscale instance count to zero |
| Batch transform | A whole dataset scored at once, no endpoint needed | `MaxPayloadInMB` no greater than 100 MB, and concurrency times payload also within 100 MB | Nothing runs between jobs |

Three of those rows deserve a sentence of mechanism. Asynchronous inference is not simply a slower endpoint: you put the payload in Amazon S3, pass a pointer to it on `InvokeEndpointAsync`, receive an identifier and an output location immediately, and collect the result from Amazon S3 when it appears, with optional success and error notifications through **Amazon Simple Notification Service (Amazon SNS)**, the publish-subscribe messaging service. That is what makes it right for a 900 MB medical image that takes fifteen minutes to score and wrong for a web request. Serverless inference scales to zero when idle and can keep capacity warm with provisioned concurrency, but it excludes GPUs, VPC configuration, network isolation, multi-model endpoints, data capture and Model Monitor, so a requirement for any of those forces a real-time endpoint. Batch transform starts instances, partitions the S3 input objects across them, writes one `.out` file per input file and shuts the instances down, which is why one input file plus ten instances leaves nine instances idle.

## Professional depth

The Professional selection question rarely asks which service converts audio to text. It asks which of two defensible designs to choose when the constraints conflict, and the usual conflict is between a purpose-built API and a model of your own. The methodology the exam rewards is to check, in order, whether a managed API already produces the required output, whether the accuracy gap can be closed by a customization inside that API such as Amazon Comprehend custom classification, Amazon Rekognition Custom Labels, Amazon Textract Custom Queries or Amazon Translate custom terminology, and only then to reach for SageMaker AI. Each step down that ladder adds training data, retraining cycles and an endpoint to operate, so an answer that jumps to SageMaker AI where an API-level customization would have worked is the over-engineered distractor in SAP-C02 task 2.5.

Multi-account patterns are where these services stop being one API call. The AI services are Regional and account-scoped, and access is ordinary **AWS Identity and Access Management (IAM)**, the service that decides which principal may perform which action on which resource. Cross-account invocation of a SageMaker AI endpoint is not granted with a resource policy, because SageMaker AI supports none. The caller assumes a role in the endpoint's own account, or the endpoint sits behind an API Gateway or Lambda function that fronts it, and AWS Resource Access Manager shares only the resource types that are shareable. For a workload that may not send data over the internet, these services are reachable through an interface VPC endpoint powered by **AWS PrivateLink**, the private connectivity service, and encryption of inputs, outputs and job storage volumes uses **AWS Key Management Service (AWS KMS)**, the managed key service, with a customer managed key when the company must control it.

Quotas are the failure mode at scale. Most of the AI services are throttled in transactions per second, and Amazon Rekognition's documentation is explicit that spiky traffic wastes the allotted rate: the recommended pattern is to smooth traffic through a queue and to configure retries with exponential backoff and jitter, which is exactly the answer a question about throttling on a bulk image job is looking for. SageMaker AI serverless inference likewise shares a per-Region concurrency pool across every serverless endpoint in the account, so one noisy endpoint can throttle another. A scenario that migrates a million-document backlog usually wants the asynchronous or batch form of the service plus a queue in front of it, not a higher quota.

Cost shape separates otherwise identical answers. The pre-trained AI APIs bill per unit of work processed, per page, per minute of audio, per character, per image, and cost nothing when idle. Anything with a persistent endpoint bills for time whether or not requests arrive: an Amazon Comprehend custom model endpoint, a SageMaker AI real-time endpoint, and an Amazon Kendra index, charged per provisioned index hour even when empty. That is the discriminator in a "MOST cost-effective" stem with bursty traffic. The reverse also holds: a steady high-volume workload on a per-request API can cost more than a right-sized endpoint, which is the reading behind a question that has already measured sustained throughput.

> **Professional depth.** Every one of these services emits metrics to **Amazon CloudWatch**, the metrics and log service, and job state changes can be routed with **Amazon EventBridge**, the serverless event bus, into **AWS Step Functions**, the managed workflow service, which is the standard way to orchestrate a multi-stage pipeline where Amazon Textract extracts, Amazon Comprehend classifies and a human reviews the low-confidence cases. Confidence scores are the hinge: AWS states plainly for the medical services that high-stakes results must be reviewed by a qualified human, so a design that auto-approves on a low confidence score is wrong even when the service choice is right.

## Worked scenario

A national insurer receives about 40,000 claim packets a day. Each packet is a multipage PDF of scanned forms and handwritten notes, and about a fifth arrive with a recorded voicemail from the claimant. Adjusters currently key the form fields by hand and listen to the voicemails. The company wants the fields extracted automatically, the voicemails transcribed, any Spanish-language material handled without a separate process, and personal data masked before anything reaches the analytics team. It runs a multi-account AWS organization and will not allow claim documents to traverse the public internet.

The packets land in an Amazon S3 bucket in an ingestion account. An S3 event notification invokes an AWS Lambda function that starts an asynchronous Amazon Textract job, because a multipage PDF cannot be processed synchronously, and the job uses `AnalyzeDocument` with Queries so the pipeline asks for the policy number, the incident date and the claim amount by name rather than parsing coordinates. The voicemails go to Amazon Transcribe batch jobs with speaker partitioning, and the resulting transcripts plus the free-text portions of the forms go to Amazon Comprehend. Language detection runs first, and anything detected as Spanish is passed through Amazon Translate before the rest of the analysis, so one code path serves both languages. Amazon Comprehend PII detection returns the offsets of names, addresses and account numbers, and a Lambda function masks those spans before the record is written to the analytics bucket.

The private-path requirement is met with interface VPC endpoints powered by AWS PrivateLink for each AI service the pipeline calls, so requests from the Lambda functions in private subnets never reach an internet gateway, and AWS KMS customer managed keys encrypt both buckets and the job output. AWS Step Functions orchestrates the stages, EventBridge routes the Textract and Transcribe completion events into it, and any page whose extraction confidence falls below the threshold goes to an adjuster queue rather than being auto-approved.

When the exam asks about this scenario, the keyed answer is asynchronous Amazon Textract for the multipage documents, Amazon Transcribe for the audio, Amazon Comprehend for entity and PII detection, Amazon Translate for the Spanish material, and Lambda with Step Functions to join them. The distractors are a SageMaker AI model trained on claim forms, which rebuilds `AnalyzeDocument` from scratch, and a fleet of **Amazon Elastic Compute Cloud (Amazon EC2)** virtual servers running an open-source OCR library, which adds servers to patch for an output an API already returns.

## Exam lens

- "Extract the fields from scanned forms and invoices" maps to Amazon Textract; Amazon Rekognition text detection is the distractor, because it finds text in a picture without understanding forms or tables.
- "Read the text aloud to the user" maps to Amazon Polly, and "the same audio is played to every user" adds caching the synthesized file in Amazon S3.
- "Convert recorded calls to text" maps to Amazon Transcribe batch; "as the call is in progress" maps to Amazon Transcribe streaming.
- "Detect inappropriate images uploaded by users" maps to Amazon Rekognition content moderation; a human moderation team is the operational-overhead distractor.
- "Confirm the person in front of the camera is real, not a photograph" maps to Amazon Rekognition Face Liveness, not to face comparison, which only proves a match.
- "Build a chatbot that books appointments over voice and chat" maps to Amazon Lex with an AWS Lambda fulfillment function.
- "Detect medical conditions and medications in clinician notes" maps to Amazon Comprehend Medical, paired with Amazon Transcribe Medical when the source is dictation.
- "Natural language search across SharePoint, Amazon S3 and a wiki, respecting who may read each document" maps to Amazon Kendra on SAP-C02; on SAA-C03 the equivalent is Amazon OpenSearch Service, because Kendra is not on that guide's list.
- "Recommend products based on what similar users bought" maps to Amazon Personalize on SAP-C02 only, since Personalize is named on the SAA-C03 out-of-scope list.
- "Score each new account sign-up for fraud at the moment it is created" maps to Amazon Fraud Detector on SAP-C02.
- "Score an entire dataset overnight with no endpoint running between runs" maps to SageMaker AI batch transform; a real-time endpoint bills for idle instances.
- "The payload is several hundred megabytes and inference takes twenty minutes" maps to SageMaker AI asynchronous inference; a real-time endpoint breaks the 6 MB payload and 60 second response limits.
- "Traffic is unpredictable with long idle periods and a cold start is acceptable" maps to SageMaker AI serverless inference; "a GPU is required" or "the endpoint must be in a VPC" rules serverless out and forces a real-time endpoint.
- "No machine learning expertise on the team" is the phrase that points away from SageMaker AI and toward whichever purpose-built API matches the output.

Recognizing when to replace something already running is its own skill, and the Professional exam asks for it. Three shapes recur: a self-run optical character recognition, natural language or speech stack on EC2 instances that a team patches and scales itself, a per-minute transcription or translation vendor contract renewing against usage that has grown, and a hand-built recommender whose model nobody has retrained in two years. In each case the argument is not that the managed service is more capable. It is that the undifferentiated work disappears, the cost moves from fixed capacity to per-request, and the accuracy improves without a project, because AWS retrains the model. Weigh against that the switching cost and any accuracy regression on the specific corpus, and propose a measured comparison on real samples rather than a wholesale swap.

## Knowledge check

### 1. Turning scanned claim forms into data (Associate)

An insurance company receives thousands of scanned claim forms as single-page images each day. Employees currently retype the values of named fields, such as the policy number and the claim amount, into an internal system. The company wants to extract those field values automatically and has no machine learning staff.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Use Amazon Rekognition text detection to read the characters on each image and write custom parsing logic to locate the fields.
- **B)** Use Amazon Textract with the `AnalyzeDocument` operation and the Queries feature to request each named field.
- **C)** Train a custom object detection model in Amazon SageMaker AI on a labeled sample of the forms and deploy it to a real-time endpoint.
- **D)** Use Amazon Comprehend custom entity recognition on the images to detect the field values.

<details><summary>Answer</summary>

**Answer: B.** Amazon Textract is the purpose-built document service, and the Queries feature lets the application ask for a field by name rather than reasoning about coordinates, so nothing has to be trained or parsed. A returns detected words with no structural understanding of the form, leaving the company to write and maintain the parsing logic the requirement is trying to avoid. C rebuilds a capability that an existing API already provides, and it needs labeled training data, a training job and an endpoint to operate, which is the opposite of least operational overhead. D targets the wrong stage: Amazon Comprehend analyzes text for entities and sentiment, and it is a natural follow-on step after extraction, but it does not extract key-value pairs from a scanned form.

*Where this is covered: Vision and documents: Rekognition and Textract.*

</details>

### 2. A bilingual support inbox (Associate)

A retailer receives support emails in English and Spanish into one inbox. The company wants every message stored in English, wants the overall sentiment of each message recorded, and wants to add no servers. Messages arrive as objects in an Amazon S3 bucket.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Call Amazon Translate with the source language set to `auto` from an AWS Lambda function triggered by an S3 event notification.
- **B)** Deploy an open-source translation model on Amazon EC2 instances behind an **Application Load Balancer**, the Layer 7 load balancer, the layer 7 load balancer, and call it from the application.
- **C)** Call Amazon Comprehend `DetectSentiment` on the translated text from the same Lambda function and store the result.
- **D)** Call Amazon Polly on each message and store the resulting audio alongside the text.
- **E)** Train an Amazon Comprehend custom classification model to label each message as English or Spanish before translating it.

<details><summary>Answer</summary>

**Answer: A and C.** Setting the source language to `auto` makes Amazon Translate detect the language by calling Amazon Comprehend on your behalf, so one code path handles both languages, and Amazon Comprehend sentiment analysis then returns positive, negative, neutral or mixed with no model to train. A Lambda function on an S3 event notification adds no servers. B introduces instances to patch, scale and pay for in order to reproduce a managed API. D produces speech, which nothing in the requirements asks for. E trains a custom model to do language detection, which both Amazon Comprehend and Amazon Translate already perform with a pre-trained model.

*Where this is covered: Language services: Comprehend, Translate, Transcribe and Polly.*

</details>

### 3. Scoring a nightly file of records (Associate)

A lender has trained a credit risk model and deployed it to an Amazon SageMaker AI real-time endpoint. The model is used only once a day, when a file of roughly two million applications is scored in a single overnight run. The endpoint sits idle the rest of the day. The company wants to reduce cost without changing the model.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Keep the real-time endpoint and reduce its instance count to one outside the nightly window.
- **B)** Replace the endpoint with a SageMaker AI batch transform job scheduled to run each night against the input file in Amazon S3.
- **C)** Replace the endpoint with SageMaker AI asynchronous inference and submit each application as a separate request.
- **D)** Keep the real-time endpoint and add an **Amazon Simple Queue Service (Amazon SQS)** queue, the managed message queue, so that the application sends records at a steady rate.


<details><summary>Answer</summary>

**Answer: B.** Batch transform starts instances, scores the whole file from Amazon S3, writes the predictions back to Amazon S3 and shuts the instances down, so nothing runs between nightly runs and there is no endpoint to pay for. A still pays for an instance every hour of the day for a job that runs once. C is the wrong asynchronous option: asynchronous inference keeps an endpoint configuration and is built for large individual payloads with long inference times, not for scoring two million small records, and submitting each record separately adds two million requests. D smooths traffic against an endpoint whose problem is that it exists at all, and the workload has no latency requirement that an endpoint satisfies.

*Where this is covered: Amazon SageMaker AI: build, train and deploy.*

</details>

### 4. Stopping photographs of photographs (Associate)

A bank verifies new customers in a mobile app by having them take a selfie, which the app compares with the photo on their identity document. The fraud team finds that attackers are passing the check by holding up printed photos and by injecting pre-recorded video into the camera feed. The bank needs to confirm that a real person is physically present during the capture.

Which solution will meet these requirements?

- **A)** Raise the similarity threshold on the Amazon Rekognition `CompareFaces` operation.
- **B)** Index every selfie in an Amazon Rekognition face collection and use `SearchFacesByImage` to reject duplicates.
- **C)** Add Amazon Rekognition Face Liveness to the capture step before comparing the two faces.
- **D)** Use Amazon Textract `AnalyzeID` on the identity document and reject any submission whose name does not match the account.

<details><summary>Answer</summary>

**Answer: C.** Face Liveness is the feature built for this exact attack class: it checks that a live user is in front of the camera and detects spoofs presented to the camera, such as printed or digital photos, as well as spoofs injected past the camera, such as pre-recorded or deepfake video. A tightens a similarity score, but a printed photo of the right person matches the document photo perfectly, so the threshold never helps. B detects the same face appearing twice, which is a different fraud pattern and does nothing about presentation attacks. D reads the document's fields and says nothing about whether the person submitting it is present.

*Where this is covered: Vision and documents: Rekognition and Textract.*

</details>

### 5. Narrating a fixed course catalog (Associate)

An e-learning company has 8,000 lesson pages of static text and wants an audio narration of each one available to learners worldwide. The text changes only a few times a year. The company has no machine learning staff and wants the lowest ongoing cost.

Which solution will meet these requirements MOST cost-effectively?

- **A)** Synthesize each lesson once with Amazon Polly, store the resulting audio files in Amazon S3, and serve those files to learners.
- **B)** Call Amazon Polly from the application on every page view so that the narration always matches the current text.
- **C)** Hire voice actors to record all 8,000 lessons and store the recordings in Amazon S3.
- **D)** Use Amazon Transcribe to generate narration audio from the lesson text and store it in Amazon S3.

<details><summary>Answer</summary>

**Answer: A.** Amazon Polly bills for the text you synthesize, and AWS permits caching and replaying the generated speech at no additional charge, so synthesizing static content once and serving the stored audio turns a per-playback cost into a one-time cost plus storage. B pays to synthesize the same unchanged text on every view, which is the expensive version of the same design. C produces the same output at far higher cost and needs the actors back whenever a lesson changes. D reverses the direction of the service: Amazon Transcribe converts audio to text, and Amazon Polly is the text to speech service.

*Where this is covered: Language services: Comprehend, Translate, Transcribe and Polly.*

</details>

### 6. Serving a large, slow imaging model (Professional)

A medical imaging company hosts a segmentation model on Amazon SageMaker AI. Each study is a single file of roughly 600 MB, and inference takes between 8 and 25 minutes on a GPU instance. Radiologists submit studies throughout the working day and review results later, so no interactive response is required, but a study must begin processing as soon as it is submitted rather than waiting for a scheduled run. Overnight, no studies are submitted, and the company wants no inference capacity running then. The model container cannot be modified.

Which solution will meet these requirements?

- **A)** Deploy the model to a real-time endpoint with target tracking auto scaling on invocations per instance.
- **B)** Deploy the model to a serverless inference endpoint with provisioned concurrency disabled.
- **C)** Run an Amazon SageMaker AI batch transform job every hour against the studies submitted in the previous hour.
- **D)** Deploy the model to an asynchronous inference endpoint, place each study in Amazon S3, invoke it with a pointer to the object, and let auto scaling reduce the instance count to zero when the queue is empty.

<details><summary>Answer</summary>

**Answer: D.** Asynchronous inference is designed for payloads up to 1 GB and processing times up to one hour, it queues each request and returns an identifier immediately, it reads the payload from Amazon S3 and writes the result back there with optional Amazon SNS notification, and it can autoscale the instance count to zero so nothing runs overnight. A breaks two hard limits: a real-time invocation body may not exceed 6 MB and the container must respond within 60 seconds. B fails on several counts, because serverless inference offers no GPUs, caps memory at 6 GB, and is still a synchronous request path. C meets the cost requirement but breaks the requirement that processing start on submission, and batch transform caps `MaxPayloadInMB` at 100 MB, well below a 600 MB study.

*Where this is covered: Amazon SageMaker AI: build, train and deploy.*

</details>

### 7. Moderating a backlog without leaving the VPC (Professional)

A media company runs a 30-account AWS organization. A workload account holds 12 million user-submitted images in Amazon S3 that must be screened for explicit content, and roughly 200,000 new images arrive each day. Security requires that image data never traverse the public internet. During an earlier attempt, the bulk run failed repeatedly with throttling errors because the application called the moderation API as fast as it could read objects. The company wants the least operational overhead.

Which combination of steps will meet these requirements? (Select TWO.)

- **A)** Create an interface VPC endpoint for Amazon Rekognition and call the moderation API from AWS Lambda functions attached to private subnets.
- **B)** Route the moderation calls through a NAT gateway in a public subnet and restrict the route table to the Amazon Rekognition public IP ranges.
- **C)** Place the backlog on an Amazon SQS queue, drive the moderation calls from the queue at a controlled rate, and configure retries with exponential backoff and jitter.
- **D)** Request a transactions per second quota increase and call the moderation API in a tight loop from an **Amazon EC2 Auto Scaling**, the service that adds and removes instances to match demand group.
- **E)** Train an Amazon Rekognition Custom Labels model on a sample of the backlog so that fewer API calls are needed.

<details><summary>Answer</summary>

**Answer: A and C.** An interface VPC endpoint puts the Amazon Rekognition API on a private network path, so Lambda functions in private subnets reach it without an internet gateway or a NAT device. Queueing the backlog and retrying with exponential backoff and jitter is the pattern AWS documents for getting maximum throughput from a transactions per second quota, because spiky traffic wastes the allotted rate. B still sends the traffic over the public internet, which the security requirement forbids. D removes the smoothing that makes a quota usable and adds an instance fleet to operate; a quota increase without backoff reproduces the same throttling at a higher number. E adds a training and retraining burden to replace a pre-trained moderation model and does not reduce the number of images that must be screened.

*Where this is covered: Professional depth.*

</details>

### 8. Question answering across four repositories (Professional)

A pharmaceutical company keeps standard operating procedures in Amazon S3, meeting notes in SharePoint, project pages in Confluence and policy documents on a file share. Staff must be able to ask questions in plain English and get an answer with the source document, and each person may only see results drawn from documents they are already entitled to read. The company already runs an Amazon Kendra index for two of these repositories, provisioned before Kendra closed to new customers, and has no search engineering team.

Which solution will meet these requirements with the LEAST operational overhead?

- **A)** Create an Amazon Kendra index, attach the built-in connectors for each repository, and rely on Kendra's user and group access filtering to scope results per user.
- **B)** Load the documents into an Amazon OpenSearch Service cluster and write an application layer that rewrites each query with the requesting user's group memberships.
- **C)** Run Amazon Comprehend key phrase detection over every document and store the key phrases in **Amazon DynamoDB**, the managed key-value database, for keyword lookup.
- **D)** Build an Amazon Lex bot with one intent per document category and have an AWS Lambda fulfillment function return the matching file.

<details><summary>Answer</summary>

**Answer: A.** Amazon Kendra is the managed intelligent search service, it ships connectors for these repositories, it answers factoid and descriptive questions rather than matching keywords, and its results reflect the organization's security model so a user sees only what they may read. Note that Kendra is closed to new customers and AWS now points new work at Amazon Bedrock Knowledge Bases, but Kendra is what the SAP-C02 guide lists. B produces a comparable result only after the company builds and maintains the semantic ranking and the access filtering itself, which is the operational overhead the stem excludes. C reduces documents to keywords and answers nothing in plain English. D forces every question into a predefined intent, which is what a conversational bot does well and open-ended enterprise search does not.

*Where this is covered: Conversation and enterprise search: Lex and Kendra.*

</details>

## Summary

These services are decided by matching an input to an output. Text in, insights out, is Amazon Comprehend; text in, other-language text out, is Amazon Translate; audio in, text out, is Amazon Transcribe; text in, audio out, is Amazon Polly; a picture in, labels or faces out, is Amazon Rekognition; a document in, fields and tables out, is Amazon Textract; an utterance in, an intent and a fulfillment call out, is Amazon Lex. Three more belong to SAP-C02 only: Amazon Kendra for question answering over repositories, Amazon Personalize for recommendations, which the SAA-C03 guide names as out of scope, and Amazon Fraud Detector for scoring an event. Decide next whether the work is one item now or a repository at once, because most of these services split into a real-time call and an asynchronous job, and the cost and the keyed answer follow that split. Reach for Amazon SageMaker AI only when the output is specific to the company's own data and no purpose-built API covers it, then decide the inference option from payload size, latency tolerance and whether anything may run while idle: real-time within 6 MB and 60 seconds, serverless when traffic is intermittent, asynchronous for large slow payloads, batch transform when no endpoint should exist at all.

## Related units

- [AI developer tools and generative AI](ai-dev-tools-and-generative-ai.md): Amazon Bedrock, Knowledge Bases and Guardrails, and when a foundation model replaces one of these purpose-built APIs
- [Developer tools and CI/CD](../08-management/developer-tools-and-cicd.md): Amazon CodeGuru, the machine learning developer tool SAP-C02 lists outside its Machine Learning group
- [Amazon OpenSearch Service](../09-analytics/opensearch.md): the full-text and log search alternative when the scenario is not question answering, and the Associate-scope answer where Kendra is not listed
- [AWS Lambda](../02-compute/lambda.md): the event-driven glue that calls these APIs from an S3 event notification and fulfills an Amazon Lex intent
- [Amazon S3](../01-storage/s3.md): event notifications and the buckets nearly every one of these services reads from and writes to
- [AWS Step Functions](../06-integration/step-functions.md): orchestrating multi-stage document and media pipelines with human review branches
- [Amazon Kinesis](../09-analytics/kinesis.md): Kinesis Video Streams and Kinesis Data Streams, the input and output of Amazon Rekognition streaming video analysis
- [Media services, IoT and Device Farm](media-iot-and-device-farm.md): the media processing neighbors in this category

## Sources

- [Amazon Rekognition and interface VPC endpoints](https://docs.aws.amazon.com/rekognition/latest/dg/vpc.html): that Rekognition is reachable privately through AWS PrivateLink

- [What is Amazon Comprehend?](https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html): the pre-trained insights, real-time compared with asynchronous jobs, Amazon Comprehend Custom, flywheels, and the endpoint charge for custom real-time requests
- [Amazon Comprehend feature availability change](https://docs.aws.amazon.com/comprehend/latest/dg/comprehend-availability-change.html): topic modeling, event detection and prompt safety classification closed to new customers, the twelve-month grandfathering, and the Amazon Bedrock alternatives
- [What is Amazon Comprehend Medical?](https://docs.aws.amazon.com/comprehend-medical/latest/dev/comprehendmedical-welcome.html): medical entity and PHI detection, ICD-10-CM, RxNorm and SNOMED CT linking, US English only, HIPAA eligibility and the human review caution
- [What is Amazon Translate?](https://docs.aws.amazon.com/translate/latest/dg/what-is.html): what the service does and its integrations with Amazon Comprehend, Amazon Transcribe and Amazon Polly
- [How Amazon Translate works](https://docs.aws.amazon.com/translate/latest/dg/how-it-works.html): real-time compared with batch input formats, custom terminology, parallel data, do-not-translate tags, brevity, profanity, formality, and `auto` source language detection
- [What is Amazon Transcribe?](https://docs.aws.amazon.com/transcribe/latest/dg/what-is.html): streaming compared with batch, speaker partitioning, language customization, content filtering, and per-second billing in one-second increments
- [Amazon Transcribe Medical](https://docs.aws.amazon.com/transcribe/latest/dg/transcribe-medical.html): that the service still exists, its streaming and batch modes, US English only, the supported specialties and the separate Region lists
- [What is Amazon Polly?](https://docs.aws.amazon.com/polly/latest/dg/what-is.html): generative, long-form, neural and standard voices, the Newscaster style, paying only for synthesized text, caching and replay at no additional cost, HIPAA and PCI DSS
- [What is Amazon Rekognition?](https://docs.aws.amazon.com/rekognition/latest/dg/what-is.html): the image and video capability lists, face collections, Face Liveness, PPE detection, Custom Labels and moderation adapters
- [Guidelines and quotas in Amazon Rekognition](https://docs.aws.amazon.com/rekognition/latest/dg/limits.html): the 5 MB raw bytes and 15 MB S3 object image limits, PNG and JPEG only, minimum dimensions, 10 GB and six-hour stored video limits, 20 concurrent jobs, and the queue plus backoff guidance for TPS quotas
- [What is Amazon Textract?](https://docs.aws.amazon.com/textract/latest/dg/what-is.html): `DetectDocumentText`, `AnalyzeDocument` with forms, tables and Queries, `AnalyzeExpense`, `AnalyzeID` for US government documents, Analyze Lending, Custom Queries, and synchronous single-page compared with asynchronous multipage processing
- [What is Amazon Lex V2?](https://docs.aws.amazon.com/lexv2/latest/dg/what-is.html): voice and text conversational interfaces, ASR and NLU, AWS Lambda integration, the Amazon Connect, Amazon Comprehend and Amazon Kendra integrations, and Multi-Region Replication
- [Amazon Lex V2 core concepts](https://docs.aws.amazon.com/lexv2/latest/dg/how-it-works.html): bot, language, intent, sample utterances, slot, slot type, fallback intent, version and alias, and the recommendation to fulfill an intent with a Lambda function
- [What is Amazon Kendra?](https://docs.aws.amazon.com/kendra/latest/dg/what-is-kendra.html): the closed to new customers notice and the Amazon Bedrock Knowledge Bases recommendation
- [What is Amazon Personalize?](https://docs.aws.amazon.com/personalize/latest/dg/what-is-personalize.html): that Personalize carries no closure notice and remains current
- [What is Amazon Fraud Detector?](https://docs.aws.amazon.com/frauddetector/latest/ug/what-is-frauddetector.html): the November 7, 2025 close to new customers with Amazon SageMaker, AutoGluon and AWS WAF as alternatives, and the model, rules and outcomes workflow
- [What is Amazon Forecast?](https://docs.aws.amazon.com/forecast/latest/dg/what-is-forecast.html): the no longer available to new customers notice, that existing customers continue, and the transition to Amazon SageMaker Canvas
- [What is Amazon CodeGuru Reviewer?](https://docs.aws.amazon.com/codeguru/latest/reviewer-ug/welcome.html): that new repository associations stopped on November 7, 2025
- [What is Amazon SageMaker AI?](https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html): the December 3, 2024 rename, the unchanged API namespaces and CloudFormation prefixes, and the next-generation Amazon SageMaker platform that contains SageMaker AI
- [Deploy models for inference](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html): the JumpStart, `ModelBuilder` and CloudFormation deployment paths, and the four inference options with their intended workloads
- [Real-time inference](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html): fully managed endpoints for interactive low latency workloads with auto scaling
- [InvokeEndpoint API reference](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html): the 6,291,456 byte request and response body limit and the 60 second container response requirement
- [Deploy models with Amazon SageMaker Serverless Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html): memory sizes from 1024 MB to 6144 MB, scale to zero, cold starts, provisioned concurrency, 200 maximum concurrency per endpoint, 50 endpoints per Region and the excluded features
- [Asynchronous inference](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html): payloads up to 1 GB, processing up to one hour, the queued `InvokeEndpointAsync` flow through Amazon S3, optional Amazon SNS notifications and autoscaling to zero
- [Batch transform for inference with Amazon SageMaker AI](https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html): when to use batch transform, the per-file output objects, and the 100 MB ceiling on `MaxPayloadInMB` and on concurrency times payload
