# Out-of-scope quiz: classical ML questions from the practice exams

Seven questions in the practice exams test classical machine learning engineering (training infrastructure, transfer learning, class imbalance, IoT ingestion, no-code model building) rather than generative AI development. The AIP-C01 exam guide does not cover them, so they were kept out of the domain units to protect your time. They are collected here for completeness: if you have spare time on day 4, answer them once, read the folds, and move on.

Each answer is ours with a confidence mark.

## Questions

<!-- KC: E2-Q3, E2-Q30, E2-Q33, E2-Q38, E2-Q39, E3-Q46, E3-Q66 -->
<!-- KC-BEGIN -->
### 1. Exam 2, question 3

A robotics startup is training a high-resolution object-tracking model using Amazon SageMaker AI. The training data consists of millions of annotated frames stored in Amazon S3, generated from a labeling workflow built with SageMaker Ground Truth. Engineers notice that GPU utilization remains low because the training container must download large batches of images sequentially from S3 at startup, causing long warm-up times and slow epoch transitions.

The team wants to keep S3 as the system of record but improve throughput and reduce startup delays—without duplicating data, restructuring the dataset, or rewriting the training code. The solution must support high-performance parallel reads and integrate seamlessly with the current S3-based workflow.

Which solution will best improve training performance while meeting all requirements?

- **A)** Create an Amazon FSx for Lustre file system linked to the existing S3 bucket and mount it into the SageMaker training job so the model can read data at high throughput with POSIX semantics.
- **B)** Move the training data to an Amazon EFS file system and mount it to the container for improved sequential read performance.
- **C)** Copy the training dataset to Amazon EBS volumes before every SageMaker run to reduce remote fetch overhead during training.
- **D)** Enable S3 Transfer Acceleration to reduce latency when fetching data during training initialization.

<details><summary>Answer</summary>

**Answer: A.** An Amazon FSx for Lustre file system linked to the S3 bucket presents the training data as a high-throughput POSIX file system that lazily loads objects from S3 and serves parallel reads at GPU speed, so the training job starts fast and keeps GPUs busy while S3 remains the system of record and the code and dataset stay unchanged. EFS is slower and requires copying data, EBS copies before every run duplicate data, and S3 Transfer Acceleration speeds transfers over long distances rather than in-Region training reads.

*Where this is covered: Appendix, out-of-scope quiz (classical ML training, not tested by AIP-C01). Key: ours, confidence high.*

</details>

### 2. Exam 2, question 30

A global enterprise SaaS provider is building a threat-intelligence email classifier on Amazon SageMaker AI to detect malicious content across millions of internal security alerts. The ML team wants to use transfer learning by starting with a pretrained BERT model hosted in Amazon S3. They plan to fine-tune this model on a labeled dataset of “malicious” vs. “benign” security messages processed with Amazon Comprehend to extract domain entities.

To maximize accuracy and reduce training cost, the team must correctly initialize the BERT model using its pretrained weights while replacing only the components specific to the classification objective. The solution must ensure that the model starts with the full pretrained language understanding of BERT while learning a new task-specific output structure.

Which approach correctly initializes BERT for fine-tuning in this scenario?

- **A)** Load pretrained weights for all layers while keeping the original classifier frozen, and train a separate external classifier on top of the pooled output vector.
- **B)** Initialize BERT with its pretrained weights and convert the output classifier into a multi-task prediction head, then fine-tune the entire network on the labeled security dataset.
- **C)** Load the pretrained model weights and attach an additional classifier head that operates in parallel with the existing output layer, training only this new classifier.
- **D)** Apply pretrained model parameters across all transformer layers, remove the original classification layer, and add a new task-specific classifier trained using the labeled dataset.

<details><summary>Answer</summary>

**Answer: D.** Transfer learning for classification initialises every transformer layer from the pretrained weights, removes the original output layer, and adds a new task-specific classification head trained on the labelled data, so the model keeps its language understanding and learns only the new output structure. Freezing the original classifier and training an external one, converting to a multi-task head, or adding a parallel head beside the old layer all keep an output layer that does not match the new task.

*Where this is covered: Appendix, out-of-scope quiz (classical ML training, not tested by AIP-C01). Key: ours, confidence high.*

</details>

### 3. Exam 2, question 33

A large academic research consortium is building a generative AI content-analysis platform for summarizing manuscripts and generating literature insights. The organization uses Amazon Comprehend for preprocessing, along with Amazon Bedrock Agents to orchestrate retrieval, citation checks, and workflow automation across several research groups.

A machine learning engineer has fine-tuned a large language model (LLM) externally and stored the artifacts in an internal Amazon S3 bucket. Multiple research analysts, who share the same SageMaker AI domain as the engineer, want to experiment with text-generation capabilities using SageMaker Canvas. The engineer must make the model accessible within Canvas while ensuring it is properly registered and controlled through SageMaker AI.

Which combination of steps will enable SageMaker Canvas access to the model? (Select TWO.)

- **A)** The analysts must create a shared collaborative Canvas workspace to expose the model automatically to all users in the domain.
- **B)** The research analysts must be granted IAM permissions to access the S3 bucket that stores the model artifacts.
- **C)** The engineer must convert the LLM into a Hugging Face format before Canvas can load it.
- **D)** The engineer must deploy the model as a real-time SageMaker endpoint to enable Canvas discovery.
- **E)** The engineer must register the model in the SageMaker Model Registry so it becomes available for Canvas users within the shared SageMaker domain.

<details><summary>Answer</summary>

**Answer: D, E.** SageMaker Canvas discovers models that data scientists share through the SageMaker Model Registry within the same SageMaker domain, so the engineer registers the fine-tuned model there, and Canvas text-generation experiments run against a deployed real-time SageMaker endpoint, so the model must be deployed as well. Canvas workspaces do not expose models automatically, analysts do not need S3 access to the artifacts, and no Hugging Face conversion is required. The question is about SageMaker model governance rather than GenAI development, hence its place in the appendix.

*Where this is covered: Appendix, out-of-scope quiz (classical ML training, not tested by AIP-C01). Key: ours, confidence medium.*

</details>

### 4. Exam 2, question 38

A global entertainment studio is building a generative AI system that produces long-form narrative scripts, multilingual promotional content, and localized dialogue for international releases. The system uses Amazon SageMaker AI to fine-tune a custom 250-billion-parameter language model on decades of archived scripts, audience engagement metadata, and regional cultural datasets.

The company also uses Amazon Comprehend to analyze live social feeds and inject sentiment-aware signals into the training pipeline. Due to the size and complexity of the model, the data science team requires extremely high-throughput distributed training with optimized cost-performance characteristics. The solution must minimize training time while maintaining full scalability across multiple nodes.

Which Amazon EC2 instance type is the MOST appropriate choice for this fine-tuning workload?

- **A)** Select purpose-built Trn series EC2 instances designed for large-scale, high-performance training of massive language models.
- **B)** Use accelerated-computing G-series EC2 instances to perform lightweight pre-processing and sentiment enrichment from Comprehend.
- **C)** Use compute-optimized C-series EC2 instances inside SageMaker AI to reduce training costs across distributed nodes.
- **D)** Deploy GPU-based P-series EC2 instances for both fine-tuning and hosting the final model in SageMaker AI endpoints.

<details><summary>Answer</summary>

**Answer: A.** Trn-series instances are built on AWS Trainium, the accelerator purpose-built for large-scale, high-throughput distributed training of very large language models at the best cost-performance, which is what fine-tuning a 250-billion-parameter model across many nodes needs. G-series instances are sized for inference and lighter workloads, C-series instances have no accelerators, and P-series GPUs are a valid but more expensive training choice that the option also misuses for hosting.

*Where this is covered: Appendix, out-of-scope quiz (classical ML training, not tested by AIP-C01). Key: ours, confidence high.*

</details>

### 5. Exam 2, question 39

A renewable-energy research institute deploys hundreds of off-grid environmental sensors that record humidity, vibration signatures, and voltage stability across remote microgrid sites. Engineers plan to use Amazon SageMaker AI to train predictive models and Amazon Comprehend to extract contextual events from maintenance logs. Due to highly unreliable network connections, the sensors send compressed telemetry via MQTT whenever connectivity becomes available.

The AI engineering team must design an ingestion pipeline that reliably routes all MQTT messages into Amazon S3 with minimal operational overhead, supports scalable downstream ML processing, and integrates cleanly with other AWS analytics services.

Which solution will BEST meet these requirements?

- **A)** Route the MQTT telemetry to AWS IoT Core and configure an IoT Core rule to deliver the data to an Amazon Data Firehose stream that writes directly to Amazon S3.
- **B)** Deploy AWS IoT Greengrass components on each sensor to locally preprocess data and periodically push batches to S3 using the AWS SDK.
- **C)** Stream MQTT messages from IoT devices to AWS IoT Core, forward them into a Kinesis Data Stream, and use a Lambda consumer to upload the processed data into S3.
- **D)** Expose a public API using Amazon API Gateway for the sensors to POST telemetry, and invoke Lambda to write the incoming payloads into S3.

<details><summary>Answer</summary>

**Answer: A.** AWS IoT Core is the managed MQTT broker for devices that connect intermittently, and an IoT Core rule that delivers messages to an Amazon Data Firehose stream writing to S3 gives a fully managed, scalable ingestion path with no code to operate and clean integration with analytics services. Greengrass components on every sensor add per-device software, a Kinesis Data Stream plus Lambda consumer adds moving parts Firehose removes, and a public API Gateway endpoint abandons MQTT and adds Lambda code.

*Where this is covered: Appendix, out-of-scope quiz (classical ML training, not tested by AIP-C01). Key: ours, confidence high.*

</details>

### 6. Exam 3, question 46

A transportation logistics company is building a predictive maintenance solution for its fleet of autonomous delivery vehicles. The engineering team uses Amazon Comprehend to extract entities such as fault codes, component descriptions, and mechanic observations from thousands of maintenance logs. These structured insights are merged with vehicle telemetry data stored in Amazon S3 to create a unified dataset for analysis.

The analytics group needs to prepare this combined dataset and build a custom predictive model to anticipate drivetrain failures. The team consists of analysts with limited coding experience, and leadership requires the process to remain integrated with downstream Amazon SageMaker AI components for future batch inference and deployment pipelines. The solution must simplify data preparation and model training while avoiding the need to build custom ML infrastructure.

Which service should the team use to prepare the dataset and train the predictive model?

- **A)** Use Amazon Bedrock to fine-tune a foundation model that predicts mechanical failures directly from the raw logs and telemetry data.
- **B)** Use SageMaker Canvas to visually prepare the dataset and train a custom predictive model using a no-code workflow integrated with SageMaker AI.
- **C)** Use SageMaker Ground Truth to label failure events and automatically create a model for drivetrain-failure predictions.
- **D)** Use Comprehend to build a predictive model end-to-end without requiring any Amazon SageMaker components.

<details><summary>Answer</summary>

**Answer: B.** SageMaker Canvas gives analysts with little coding experience a visual, no-code workflow to prepare the combined dataset and train a custom predictive model, and the resulting model integrates with SageMaker AI for batch inference and deployment pipelines. Fine-tuning a foundation model in Bedrock is the wrong tool for tabular failure prediction, Ground Truth labels data rather than training predictive models, and Comprehend extracts entities rather than building predictive models.

*Where this is covered: Appendix, out-of-scope quiz (classical ML training, not tested by AIP-C01). Key: ours, confidence high.*

</details>

### 7. Exam 3, question 66

A data science team is running an anti–financial-crime workload using Amazon SageMaker Training and SageMaker Feature Store. Transactional features are stored in the Feature Store offline store and periodically retrieved for scheduled retraining jobs. The model is a binary fraud classifier used for real-time payment screening. However, the team is seeing very high false negatives, despite overall accuracy exceeding 96%. Fraud events represent less than 0.5% of all transactions, and historical fraud examples remain extremely scarce.

The team must directly address the severe class imbalance before the next retraining cycle to increase detection performance.

Which solution will increase the fraudulent case detection performance?

- **A)** Enable early stopping in SageMaker to automatically halt training when the model’s accuracy on the validation set no longer improves.
- **B)** Enable automatic model tuning in SageMaker using Bayesian Optimization to find the best hyperparameters by running multiple training jobs. Increase the number of hyperparameter tuning jobs to explore a broader range of hyperparameter values and potentially improve model performance.
- **C)** Perform random oversampling on the non-fraudulent transactions to equalize batch sizes during training.
- **D)** Integrate a preprocessing step that applies the Synthetic Minority Oversampling Technique (SMOTE) on the minority fraudulent transaction class only before the training run begins.

<details><summary>Answer</summary>

**Answer: D.** With fraud at under half a percent of transactions, the classifier learns to predict the majority class; applying the Synthetic Minority Oversampling Technique (SMOTE) to the fraudulent class before training synthesises additional minority examples so the model learns the fraud patterns and false negatives fall. Early stopping and hyperparameter tuning optimise the wrong objective (overall accuracy), and oversampling the majority class makes the imbalance worse.

*Where this is covered: Appendix, out-of-scope quiz (classical ML training, not tested by AIP-C01). Key: ours, confidence high.*

</details>

<!-- KC-END -->
