# Unit 03: Privacy-preserving systems

**Task 3.2: Implement data security and privacy controls (part two: privacy of the data).** Unit 02 protected the environment; this unit protects the information inside it. It covers:

- How to find sensitive data at rest with **Amazon Macie**.
- How to detect and redact personal and health information in text with **Amazon Comprehend** and **Comprehend Medical**.
- The masking and anonymisation techniques that keep data useful.
- What **Bedrock** itself guarantees.
- How to keep PII out of search indexes and model outputs.
- How to enforce retention with **S3 Lifecycle** rules.

## The privacy vocabulary

**Personally identifiable information (PII)** is any data that identifies a person: names, addresses, phone numbers, emails, account and card numbers, government identifiers, IP addresses.

**Protected health information (PHI)** is health data tied to a person, regulated in the United States by **HIPAA**, the Health Insurance Portability and Accountability Act. Several AWS services are HIPAA-eligible, including **Bedrock**, **SageMaker**, **Comprehend** and **Comprehend Medical**.

**GDPR** is the European data-protection regulation behind many "regional data-protection law" scenarios.

The principle the exam expects is **data minimisation**: send the model only what the task needs, transform what you must send, and keep it only as long as required.

A privacy design has five checkpoints, and questions usually ask for several at once:

- Discover sensitive data **at rest**.
- Detect and transform it **before it reaches the model**.
- Constrain the model **at inference**.
- Filter **outputs**.
- Enforce **retention**.

The sections below follow that order, and each checkpoint has a service:

- **Amazon Macie** for data at rest in **S3**.
- The **AWS Glue** sensitive-data transform inside ETL jobs.
- **Amazon Comprehend**, and **Comprehend Medical** for clinical text, on text before the model.
- **Bedrock Guardrails** at inference.
- **CloudWatch Logs** data protection policies in the logs afterwards.

## Discovering sensitive data at rest: Amazon Macie

**Amazon Macie** is the data-security service for **Amazon S3**. It inventories your buckets and flags posture risks, such as a bucket that becomes public or unencrypted objects. It also discovers **sensitive data** inside objects with machine learning and pattern matching, using two kinds of identifier:

- **Managed data identifiers** for names, addresses, credentials, financial and health data.
- **Custom data identifiers**, which are regular expressions with keywords, for organisation-specific identifiers such as policy numbers.

There are two ways to run it. **Automated sensitive data discovery** samples objects across the estate continuously for broad visibility. **Sensitive data discovery jobs** scan chosen buckets in depth, once or on a schedule.

Each detection becomes a **finding**, delivered to **Amazon EventBridge** and **AWS Security Hub**, so a **Lambda** function can quarantine, tag or re-encrypt the object automatically.

**Macie**'s job is to tell you *where* sensitive data sits in **S3** before a knowledge base indexes it or a training job reads it. It does not redact text, and it does not inspect prompts in flight. When a question wants PII removed from text or blocked from a live conversation, **Macie** is the wrong tool and the distractor. When it wants "scan the **S3** data lake for sensitive data" or "verify no PII remains after processing", **Macie** is right.

## Redacting inside ETL: AWS Glue

Inside an ETL pipeline, **AWS Glue** can do the detection during the transformation. **Glue Studio**'s **Detect Sensitive Data** transform finds PII entity types in the columns of a dataset. It can then redact them, mask them with a character, or replace them with a hash, before the job writes the sanitised output to a separate **S3** prefix for training.

A scheduled **Glue** job that reads the raw bucket, encrypted with **SSE-KMS**, redacts credit card numbers and writes a clean copy for **SageMaker** is the managed daily sanitisation pipeline. Masking inside the training script, manual **Data Wrangler** cleanups, and "let **PCA** obscure it", where principal component analysis is a dimensionality-reduction step that hides nothing, are not.

## Detecting PII in text: Amazon Comprehend

**Amazon Comprehend** is the managed natural-language-processing service, and its **PII detection** is the exam's default answer for finding personal data in text without training a model. It works in two modes, and a question that asks for "both character offsets and entity labels" is asking you to name them:

- **Offsets** (`DetectPiiEntities` in real time, or an asynchronous job with `Mode = ONLY_OFFSETS`) returns each PII entity with its **type**, a confidence **score**, and the **begin and end character offsets** where it appears, so your code can mask or replace exactly that span.
- **Labels** (`ContainsPiiEntities`) returns only the **entity types present** in the document, for example `NAME`, `CREDIT_DEBIT_NUMBER` or `ADDRESS`, with a confidence each, without locations. That is enough to classify or route a document.

Real-time calls accept up to 100 KB of text, and PII detection is documented for English and Spanish.

The **asynchronous redaction job** (`StartPiiEntitiesDetectionJob` with `Mode = ONLY_REDACTION`) processes whole **S3** prefixes and writes a redacted copy. Its `RedactionConfig` lists which entity types to redact and a **mask mode**:

- `MASK` replaces each character with a mask character such as `*`.
- `REPLACE_WITH_PII_ENTITY_TYPE` substitutes the type name, so "Paulo Santos" becomes `[NAME]`.

The universal entity types include `NAME`, `ADDRESS`, `AGE`, `EMAIL`, `PHONE`, `USERNAME`, `PASSWORD`, `DATE_TIME`, `URL`, `IP_ADDRESS`, `MAC_ADDRESS`, `CREDIT_DEBIT_NUMBER`, `CREDIT_DEBIT_CVV`, `CREDIT_DEBIT_EXPIRY`, `PIN`, `INTERNATIONAL_BANK_ACCOUNT_NUMBER`, `SWIFT_CODE`, `DRIVER_ID`, `LICENSE_PLATE`, `VEHICLE_IDENTIFICATION_NUMBER`, `AWS_ACCESS_KEY` and `AWS_SECRET_KEY`. There are also country-specific types such as `BANK_ACCOUNT_NUMBER`, `BANK_ROUTING`, `SSN`, `PASSPORT_NUMBER`, `US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER`, `CA_HEALTH_NUMBER` and `UK_NATIONAL_INSURANCE_NUMBER`.

When the organisation's sensitive terms are not in that list, such as internal project codes or claim numbers, two managed alternatives exist. **Custom entity recognition** trains a **Comprehend** recogniser from your annotated examples, and **custom classification** trains a document classifier. Both are managed, but they are "train a model" answers, so they lose to built-in PII detection when the question says "avoid training custom models".

**Comprehend**'s other analyses are the recurring distractors. Key phrases, sentiment, syntax and entity recognition find important terms, tone, parts of speech and general entities, not personal data.

The other services around it divide up as follows:

- **Amazon Lex**, the conversational bot service, and **Amazon SageMaker Canvas**, no-code model building, do not provide managed PII redaction across arbitrary text.
- **Amazon Textract** extracts text from documents, and **Amazon Rekognition** analyses images and can locate faces for blurring. Both feed text or findings into **Comprehend** rather than replacing it.
- **Amazon Transcribe** does offer PII redaction within transcripts of audio.
- Text from **Amazon Textract** is what **Comprehend** redacts for scanned documents.

**Amazon Comprehend Medical** is the separate, HIPAA-eligible service for clinical text, and it has three groups of operations:

- `DetectPHI` finds protected health information, covering names, ages, dates, IDs, addresses and contact details, for redaction.
- `DetectEntitiesV2` extracts medical conditions, medications with dosage and frequency, tests, treatments, procedures and anatomy, with relationships and traits such as negation.
- The ontology-linking operations map entities to standard codes: `InferICD10CM` for diagnoses, `InferRxNorm` for medications and `InferSNOMEDCT` for clinical concepts.

The pairing the exam likes: **Comprehend** redacts general PII, and **Comprehend Medical** redacts PHI **and** keeps the dosage instructions, diagnoses and allergies that make the record medically useful. **Polly** (text to speech), **Transcribe** reviews by compliance officers, and **SageMaker Ground Truth** (the managed data-labelling service) workforces are manual or irrelevant by comparison.

## Masking and anonymisation that keep the data useful

Detection finds the sensitive spans. A transformation step, usually a **Lambda** function in the pipeline, decides what to do with them. The techniques form a ladder from most to least destructive:

- **Redaction** removes the value entirely (`***`). It is safest, and least useful downstream.
- **Masking** hides part of a value (`****-1234`), keeping enough for recognition.
- **Tokenisation** replaces the value with a random token and keeps the mapping in a secure vault, so authorised systems can reverse it and the model never sees the original.
- **Pseudonymisation** replaces identifiers with consistent stand-ins (`Customer_4471`) through a secure mapping table, so records about the same person still link together for analytics without revealing who they are.
- **Format-preserving encryption** encrypts a value into another of the same shape, turning a 16-digit card number into a different 16-digit number, so systems that validate formats keep working.
- **Generalisation** widens values, turning an exact age into an age band or a street address into a city. **Perturbation** adds small noise to numbers.
- **k-anonymity** ensures every combination of quasi-identifiers, such as age band, postcode and gender, matches at least *k* records, so no one is unique in the dataset.
- **Differential privacy** adds calibrated statistical noise to aggregate results, so the presence or absence of any single person cannot be inferred. It is managed through a **privacy budget** that limits how many queries can be answered before the noise must grow.
- **Synthetic data** generates artificial records with the statistical properties of the real ones, for training and testing without any real person in the data.

The design goal is utility with privacy, and it has three parts:

- Mask before the model, so the FM works on `{NAME}` and `{ACCOUNT}` placeholders and cannot reproduce the originals.
- Keep the mapping outside the model, so downstream analytics can re-join results without ever holding raw PII.
- Choose the technique by sensitivity and need: tokenise identifiers you must recover, pseudonymise for analytics, and redact what nothing downstream needs.

## Privacy at the model

Three controls sit at the inference call.

**First, Bedrock's native guarantees** from unit 02: no training on your data, no sharing with providers, no retention by default, encryption, private connectivity, and processing within the Region or geography.

**Second, Bedrock Guardrails sensitive information filters** applied to **both input and output**. Mask PII in prompts so the model never sees it, and block or mask PII in responses so the model cannot reveal or reconstruct identifying details from context, whatever model is behind the call.

**Third, prompt discipline.** System prompts that instruct the model not to repeat identifiers are worth having, but they are not a control, because a model can be talked out of an instruction. The exam consistently rejects "rely on the FM to ignore PII" or "use a system prompt to remove PII during query processing".

So the privacy-focused workflow for customer messages full of financial details and contact information runs in four steps: **Comprehend** PII detection to find the sensitive fields, anonymisation and masking (tokenise or pseudonymise) before the text is forwarded to **Bedrock**, guardrails on the **Bedrock** call to stop the model generating or inferring sensitive information, and analytics running on the pseudonymised outputs.

Encrypting the request with **KMS** protects it in transit and at rest but does nothing about what the model reads. Storing raw prompts in an encrypted bucket and relying on **IAM** to limit who views logs protects the logs, not the conversation.

## Privacy for search and retrieval

Anything indexed for search will be surfaced by search. When a knowledge base or an enterprise search index is built from support emails, transcripts or documents that contain PII, the redaction has to happen **before indexing**. A **Comprehend** redaction job over the **S3** corpus produces a clean copy, and the clean copy is what the index ingests.

For the search layer the exam names **Amazon Kendra**, the managed enterprise search service with natural-language queries and connectors to **S3** and other repositories, integrated with **Bedrock** as a retriever. **Kendra** is now closed to new customers, but in the official practice question "**Comprehend** redacts PII in **S3**, then **Kendra** indexes the processed data" is the keyed answer, and a **Bedrock Knowledge Base** over the redacted copy is the current equivalent.

Indexing the raw data and asking the FM to hide PII at query time, routing through **DocumentDB** for "search", or scanning with **Macie** and indexing anyway, all leave the PII in the index.

Retrieval also needs **access control**. **Knowledge Base** **metadata filtering**, covered in Domain 1, restricts retrieved chunks to what the user may see, and **Q Business** or **Kendra** carry document permissions from the source, so a user cannot pull another department's records through the model.

## Retention and disposal

Privacy law and internal policy set how long data may live, and the exam wants the retention enforced by configuration, not by scheduled cleanup scripts.

**S3 Lifecycle configuration** is a set of rules on a bucket, optionally scoped by prefix or tag. It has two kinds of action:

- **Expiration actions** delete objects a set number of days after creation. A 24-hour retention requirement is an expiration rule of one day. They can also expire **noncurrent versions** in versioned buckets.
- **Transition actions** move objects to cheaper storage classes after set ages: **S3 Standard-IA**, **Glacier Instant Retrieval**, **Glacier Flexible Retrieval** and **Glacier Deep Archive**.

Rules apply to existing objects as well as new ones, and a bucket policy cannot stop them. Different prefixes get different rules, so transient inference artifacts expire in a day while regulatory records are retained for years. Two related mechanisms: **DynamoDB TTL** expires items by a timestamp attribute, and **CloudWatch Logs retention settings** expire log events per log group.

The opposite requirement, "must not be deleted or altered", is **S3 Object Lock**. It is a write-once-read-many (WORM) model on a versioned bucket, with two mechanisms:

- **Retention periods**. In **governance mode**, privileged users with a special permission can shorten or remove the lock. In **compliance mode** nobody, not even the root user, can, until the period ends.
- **Legal holds**, which last until explicitly removed.

**Object Lock** protects audit logs and evidence from tampering. It does not make outputs safe or delete anything, so it is a distractor in safety questions.

Logs deserve their own attention because they outlive the conversation. **Bedrock** **model invocation logging** records full prompts and responses, with any blocked content in plain text, to **CloudWatch Logs** or **S3**. Three things protect that destination: **KMS** and **IAM** on the bucket, lifecycle rules or log-group retention to expire it, and **CloudWatch Logs data protection policies**, which detect sensitive data in log events with managed data identifiers and mask it for anyone without the `logs:Unmask` permission, keeping PII out of the eyes of operators.

## Worked scenario

A telecom company wants a support assistant grounded in ten years of chat transcripts and call summaries stored in **S3**. The transcripts are full of names, phone numbers, account identifiers and payment details. Privacy rules say none of it may appear in search results or model answers, analysts still need usage insights, and transient files must vanish within a day.

Discovery comes first. **Amazon Macie** runs a sensitive data discovery job over the transcript buckets, confirms the PII types present with managed data identifiers and a custom identifier for the account number format, and flags one bucket that is publicly readable. The findings go to **Security Hub** and an **EventBridge** rule that tags the offending objects.

Redaction happens before anything is indexed.

- An **Amazon Comprehend** asynchronous PII redaction job processes the corpus with entity-type replacement, so "call from Maria Alvarez about 0412..." becomes "call from [NAME] about [PHONE]".
- A **Glue** job applies the sensitive-data transform to the structured billing extracts and writes clean copies to a curated prefix.
- A **Lambda** step pseudonymises account identifiers through a mapping table held in a separate encrypted store, so analysts can still count interactions per customer without holding the real identifier.

The clean corpus is what the **Bedrock Knowledge Base** ingests. At inference, **Bedrock Guardrails** sensitive information filters mask any personal data a customer types and block it in responses, and the system prompt tells the model not to repeat identifiers, understood as a courtesy rather than a control.

Retention is configuration. The transient transcripts and intermediate files sit under a prefix with an **S3 Lifecycle** expiration rule of one day, the curated corpus follows the legal retention schedule, and the invocation logs go to a bucket with **Object Lock** in compliance mode for the audit period, with **CloudWatch Logs data protection policies** masking any PII that reaches the application logs.

When a question describes this scenario, the pieces are **Macie** to find, **Comprehend** and **Glue** to redact, tokenisation or pseudonymisation to keep utility, guardrails on both directions, redaction before indexing, and lifecycle rules to delete.

## Exam lens

- "Detect PII in **S3** at rest, discover where sensitive data lives" → **Amazon Macie**. "Redact PII in text" → **Amazon Comprehend**. "PHI and clinical entities" → **Amazon Comprehend Medical**.
- "Both exact character offsets and entity-type labels" → **Comprehend** PII offsets analysis (`DetectPiiEntities`) and labels analysis (`ContainsPiiEntities`).
- "Redact PII across all text inputs at scale, no custom models" → **Comprehend** PII detection and redaction.
- "Daily managed job that encrypts and sanitises a claims dataset before training" → **SSE-KMS** on **S3** plus a **Glue** ETL job that redacts and writes a clean copy.
- "PII must not appear in search results" → **Comprehend** redaction before indexing, then **Kendra** or a **Knowledge Base**. Never a system prompt at query time.
- "Sensitive fields transformed before the FM, responses cannot reconstruct them, analytics still works" → **Comprehend** detection, anonymisation and masking (tokenise or pseudonymise), and guardrails on input and output.
- "PII identified before the FM, no leakage in outputs, temporary **S3** files deleted after 24 hours" → **Comprehend** and **Macie**, **Bedrock Guardrails**, and **S3 Lifecycle** expiration.
- "Logs must be immutable" → **S3 Object Lock**. "Logs must not expose PII" → **CloudWatch Logs data protection policies** and KMS-protected destinations.
- "Differential privacy", "k-anonymity", "tokenisation" → anonymisation techniques implemented in the pipeline with **Lambda**, chosen by sensitivity and downstream need.

## Knowledge check

<!-- KC: E3-Q30, E2-Q42, E2-Q61, E2-Q53, E1-Q42, PQ-Q14, E1-Q44 -->
<!-- KC-BEGIN -->
### 1. Exam 3, question 30

A financial services company is building an internal AI assistant that helps compliance analysts review customer emails, chat logs, and scanned documents for regulatory risks. Amazon Textract extracts text from PDFs, and Amazon Comprehend performs downstream NLP analysis.

The compliance team requires two outputs for every detected PII entity:

- Exact character offsets showing where the PII appears in the extracted text.
- Entity labels identifying the type of sensitive data so the foundation model can generate structured compliance summaries.

The engineering team must choose Comprehend analysis modes that provide both outputs.

Which analysis modes should be selected? (Select TWO.)

- **A)** Use Key Phrase Detection to identify important terms in the extracted text.
- **B)** Use the Offsets analysis to return precise start and end character positions.
- **C)** Use the Syntax Analysis feature to examine sentence structure and token-level part-of-speech data.
- **D)** Use Sentiment Analysis to determine the emotional tone in the communication.
- **E)** Use the Labels analysis to return classification-style entity names for compliance processing.

<details><summary>Answer</summary>

**Answer: B, E.** Comprehend PII detection has two analysis modes: the offsets analysis returns the begin and end character positions of each PII entity in the text, and the labels analysis returns the entity-type labels present in the document, so selecting both gives the exact positions and the classification-style names the compliance team needs. Key phrases, syntax and sentiment analysis describe terms, grammar and tone, none of which identifies PII.

*Where this is covered: Unit 03, Detecting PII in text: Amazon Comprehend. Key: ours, confidence high.*

</details>

### 2. Exam 2, question 42

A national insurance provider is developing an AI-driven claims assistant that interacts with customers through a mobile app. The assistant accepts text descriptions of incidents, voicemail transcriptions processed by Amazon Transcribe, and scanned document uploads analyzed with Amazon Rekognition. Regulatory requirements mandate that any personally identifiable information (PII)—including names, phone numbers, policy numbers, and addresses—must be identified and masked before the data is stored or forwarded to downstream analytics services.

The data engineering team wants a solution that can automatically detect and redact PII across all text-based inputs, works at scale, and requires minimal ongoing maintenance. They prefer to avoid building or training custom NLP models and want to integrate the solution with their existing AWS pipeline.

Which solution should the company implement?

- **A)** Use Amazon SageMaker Canvas to train a custom PII detection model that processes text extracted from documents and conversations.
- **B)** Leverage Amazon Comprehend to automatically detect and redact sensitive personal information from all text-based inputs before storage or downstream processing.
- **C)** Configure Amazon Lex to perform real-time PII redaction during conversational interactions across all channels.
- **D)** Deploy a custom PII-redaction pipeline using Hugging Face Transformers trained on proprietary insurance data and hosted on Amazon SageMaker.

<details><summary>Answer</summary>

**Answer: B.** Amazon Comprehend's built-in PII detection and redaction identifies names, phone numbers, addresses and account-style identifiers across text from any source (typed descriptions, Transcribe output, text from documents) at scale, with no model to train or maintain, and its asynchronous redaction jobs mask the entities before storage or downstream processing. SageMaker Canvas and Hugging Face models mean training and hosting custom PII models, and Amazon Lex is a conversational bot service, not a redaction engine for all channels.

*Where this is covered: Unit 03, Detecting PII in text: Amazon Comprehend. Key: ours, confidence high.*

</details>

### 3. Exam 2, question 61

A regional telemedicine provider is building a secure clinical document-processing pipeline to handle uploaded patient materials, including handwritten prescriptions, clinician summaries, and scanned referral letters. The organization uses Amazon Textract to extract text from the documents and Amazon Rekognition to blur patient faces in diagnostic images.

Before storing the processed content in Amazon S3 for downstream model training, the compliance team must automatically detect and redact both PII and PHI while preserving medically relevant details such as dosage instructions, diagnoses, allergies, and treatment recommendations. The solution must minimize manual review, support HIPAA compliance, and integrate into the existing automated workflow.

Which combination of AWS services will meet these requirements with the LEAST operational overhead? (Select TWO.)

- **A)** Use Amazon Polly to generate spoken summaries so reviewers can identify audio-level disclosures of sensitive information.
- **B)** Use Amazon Comprehend to detect and redact personally identifiable information (PII) from extracted clinical text.
- **C)** Use Amazon Comprehend Medical to identify and redact protected health information (PHI) and extract clinically important entities such as conditions, medications, and procedures.
- **D)** Use Amazon Transcribe to create audio transcripts that can be manually reviewed by compliance officers for sensitive content.
- **E)** Use Amazon SageMaker Ground Truth to create a human-labeling workforce to annotate PII/PHI entities and manually remove sensitive content before ingestion.

<details><summary>Answer</summary>

**Answer: B, C.** Amazon Comprehend detects and redacts general PII in the text Textract extracted, and Amazon Comprehend Medical detects and redacts protected health information while extracting the clinically important entities (conditions, medications with dosage, procedures) that must be preserved, both as managed, HIPAA-eligible APIs that slot into the existing automated pipeline. Polly narrations, Transcribe transcripts for manual compliance review and a Ground Truth labelling workforce all add manual effort and do not automate redaction.

*Where this is covered: Unit 03, Detecting PII in text: Amazon Comprehend. Key: ours, confidence high.*

</details>

### 4. Exam 2, question 53

The raw claims data contains names, phone numbers, credit card details, and other sensitive PII. The team stores the raw dataset in Amazon S3 and uses Amazon Comprehend for feature extraction on text fields.

To comply with strict data governance rules, the company must meet two requirements before training the model:

1. All data at rest must be encrypted using AWS-managed keys. 2, All PII—especially credit card numbers—must be removed or masked before any data is accessed by SageMaker AI.

The data engineering team wants a managed service that can automatically process and sanitize the dataset each day before training.

Which solution will best satisfy these requirements?

- **A)** Use Data Wrangler to manually remove PII and reupload the cleaned dataset to S3. Enable client-side encryption using a custom encryption library.
- **B)** Encrypt all datasets with AWS KMS in S3 and use AWS Glue ETL jobs to scan the claims dataset, redact credit card details, and write sanitized outputs to a separate S3 location for SageMaker AI training.
- **C)** Use Comprehend to detect PII inside SageMaker AI, then apply a masking step inside the training script before loading the data into the model.
- **D)** Train the model on encrypted raw data and rely on algorithm-level preprocessing (such as PCA or feature scaling) to obscure or eliminate sensitive information before model ingestion.

<details><summary>Answer</summary>

**Answer: B.** Encrypting the S3 datasets with AWS KMS satisfies encryption at rest with AWS-managed keys, and a scheduled AWS Glue ETL job that scans the claims data, redacts credit card numbers and other PII with its sensitive-data detection transform, and writes the sanitised output to a separate S3 location gives SageMaker a clean dataset every day with no manual step. Manual Data Wrangler cleanups and a custom encryption library are not automated, masking inside the training script means SageMaker already has the raw PII, and algorithmic preprocessing such as PCA does not remove sensitive data.

*Where this is covered: Unit 03, Redacting inside ETL: AWS Glue. Key: ours, confidence high.*

</details>

### 5. Exam 1, question 42

A financial advisory platform is developing a generative AI assistant using an Amazon Bedrock foundation model. Customer messages often contain sensitive financial details, legal case identifiers, and personal contact information. The engineering team must design a privacy-focused GenAI workflow that ensures:

- Sensitive content is removed or transformed before being sent to the FM
- FM responses cannot reveal or reconstruct original identifying details
- Downstream analytics processes can still gain insights without accessing raw PII

Which solution BEST satisfies these requirements while maintaining FM utility?

- **A)** Use Amazon Comprehend PII detection to identify sensitive fields, apply anonymization and data masking before forwarding the sanitized text to Bedrock, and configure Bedrock guardrails to prevent the model from generating or inferring sensitive information.
- **B)** Use a Lambda function to remove customer names only, send partially redacted content to Bedrock, and rely on CloudWatch retention policies to ensure privacy.
- **C)** Encrypt all requests with KMS before sending them to Bedrock, rely on the FM's internal behavior to avoid exposing PII, and mask financial data only in downstream reporting dashboards.
- **D)** Store all FM inputs in an S3 bucket with server-side encryption, send raw data directly to Bedrock, and use IAM policies to restrict who can view inference logs.

<details><summary>Answer</summary>

**Answer: A.** Comprehend PII detection identifies the sensitive fields, anonymisation and data masking (tokenisation or pseudonymisation) transform them before the text reaches Bedrock so the model works on placeholders, and Bedrock Guardrails sensitive-information filters stop responses from generating or inferring identifying details, while pseudonymised outputs still support analytics. Removing only names is incomplete and CloudWatch retention is not a privacy control, KMS encryption protects data in transit and at rest but the model still reads the PII, and IAM on inference logs protects the logs rather than the conversation.

*Where this is covered: Unit 03, Privacy at the model. Key: ExamPro answer key (Exam 1 graded).*

</details>

### 6. Official practice question set, question 14

A financial services company wants to develop a mobile app that will help users with account inquiries and general account information. The company has a large amount of email exchange data between customers and support staff to use as source material. The data is stored in an Amazon S3 bucket and contains personally identifiable information (PII) that should not appear in search results.

Which solution will meet these requirements?

- **A)** Use Amazon Comprehend to detect and redact PII from the email data that is stored in Amazon S3. Integrate Amazon Comprehend with Amazon Kendra to enable enterprise search of the processed data.
- **B)** Use Amazon Kendra to enable enterprise search of the email data that is stored in Amazon S3. Integrate Amazon Kendra with an Amazon Bedrock FM. Use a system prompt to identify and remove PII during query processing.
- **C)** Use Amazon Comprehend to detect and redact PII from the email data that is stored in Amazon S3. Integrate Amazon Comprehend with Amazon DocumentDB to enable database queries for enterprise search.
- **D)** Use Amazon Textract to extract text from the email data. Use Amazon Macie to scan for PII in Amazon S3. Integrate Amazon Textract and Amazon S3 with Amazon Kendra to enable enterprise search of the processed data.

<details><summary>Answer</summary>

**Answer: A.** Running Amazon Comprehend PII detection and redaction over the email data in S3 removes personal information before indexing, and Amazon Kendra then provides enterprise search over the processed data so PII can never appear in results. Asking a Bedrock FM to remove PII through a system prompt at query time leaves the PII in the index and is not a reliable control, DocumentDB is a database rather than a search service, and Macie only reports where PII sits in S3 without redacting it.

*Where this is covered: Unit 03, Privacy for search and retrieval. Key: AWS official answer.*

</details>

### 7. Exam 1, question 44

A healthcare startup is building a patient-support chatbot powered by an Amazon Bedrock foundation model. The chatbot processes medical inquiries that may include sensitive personal and demographic information. To comply with internal privacy controls and regional data-protection laws, the engineering team must ensure that PII is identified before any interaction reaches the FM, that FM responses do not leak sensitive content, and that all temporary text artifacts stored in Amazon S3 are automatically deleted according to a 24-hour retention requirement.

Which approach BEST satisfies the organization's privacy-preserving requirements?

- **A)** Store all interaction logs indefinitely in an S3 Glacier Deep Archive vault, use no guardrails, and rely exclusively on SageMaker AI's built-in model isolation for privacy control.
- **B)** Use API Gateway request validation to block long messages, send all content directly to Bedrock without pre-processing, and rely on CloudTrail logs to monitor sensitive data access.
- **C)** Encrypt all uploaded content using default S3 encryption, rely on the FM to ignore PII if present, and delete S3 objects manually through scheduled Lambda clean-ups.
- **D)** Use Amazon Comprehend and Amazon Macie to detect PII before forwarding inputs to Bedrock, enable Bedrock guardrails to prevent PII exposure in FM outputs, and configure S3 Lifecycle rules to automatically delete transient data after 24 hours.

<details><summary>Answer</summary>

**Answer: D.** Amazon Comprehend and Amazon Macie detect PII before inputs are forwarded to Bedrock, Bedrock Guardrails prevent PII from appearing in responses, and an S3 Lifecycle expiration rule deletes the transient text artifacts automatically after one day, meeting all three requirements with configuration rather than scripts. Indefinite Glacier storage with no guardrails ignores the requirements, API Gateway length validation and CloudTrail monitoring do not detect PII, and manual or scheduled Lambda deletions are not an enforced retention policy.

*Where this is covered: Unit 03, Retention and disposal. Key: ExamPro answer key (Exam 1 graded).*

</details>

<!-- KC-END -->

## Summary

Find sensitive data at rest with **Macie**, and with **Glue**'s sensitive-data transform inside ETL. Detect it in text with **Comprehend** PII, using offsets for locations, labels for types and asynchronous jobs for redaction with mask or entity-type replacement, and detect PHI with **Comprehend Medical**.

Then transform it before the model with redaction, masking, tokenisation, pseudonymisation, generalisation, **k-anonymity** or **differential privacy**, so the data stays useful.

**Bedrock** adds its own guarantees of no training on your data, no retention and no provider access, and **guardrails** mask or block PII on input and output. System prompts are not a privacy control.

Redact before you index anything for search, restrict retrieval with metadata filters, expire transient data with **S3 Lifecycle** rules, lock what must be immutable with **Object Lock**, and keep PII out of logs with data protection policies.
