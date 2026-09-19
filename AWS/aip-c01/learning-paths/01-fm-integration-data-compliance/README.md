# Domain 1: Foundation Model Integration, Data Management, and Compliance

**Weight: 31% of the scored exam** (roughly 20 of the 65 scored questions). This is the biggest domain, and the one where most questions are pure **Amazon Bedrock**: how you pick a model, get data in front of it, retrieve the right context, and keep prompts under control.

The domain has six task statements. Each one is a unit in this folder. Read them in order, because later units assume the vocabulary of earlier ones.

| Unit | Task statement | What you will be able to do |
|---|---|---|
| [01 Design GenAI solutions](01-design-genai-solutions.md) | 1.1 Analyze requirements and design GenAI solutions | Translate a business scenario into a **Bedrock**-centred architecture, choose an integration pattern, run a proof of concept, and standardise components with the **Well-Architected Generative AI Lens** |
| [02 Select and configure FMs](02-select-and-configure-fms.md) | 1.2 Select and configure FMs | Choose a model with evidence, pick the right inference option, switch models without code changes, survive Regional and throttling failures, and manage fine-tuned models through their lifecycle |
| [03 Data pipelines for FM consumption](03-data-pipelines-for-fms.md) | 1.3 Implement data validation and processing pipelines for FM consumption | Validate data with **Glue Data Quality** and **Data Wrangler**, process text, audio, image and tabular data, format requests correctly, and clean inputs before inference |
| [04 Vector stores](04-vector-stores.md) | 1.4 Design and implement vector store solutions | Pick a vector store, design metadata for filtering, scale **OpenSearch**, connect external content systems, and keep the store in sync |
| [05 Retrieval for RAG](05-retrieval-for-rag.md) | 1.5 Design retrieval mechanisms for FM augmentation | Chunk, embed, search (semantic and **hybrid**), rerank, rewrite queries, and expose retrieval to models through function calling and **MCP** |
| [06 Prompt engineering and governance](06-prompt-engineering-and-governance.md) | 1.6 Implement prompt engineering strategies and governance for FM interactions | Write instruction frameworks, keep conversation state, govern prompts with **Prompt Management**, test them, and chain them with **Bedrock Flows** |
| [07 Domain review](07-domain-1-review.md) | all | Decision tables, a one-page summary, and a mixed quiz of the questions not used in the units |

## How the questions are placed

The exam files in `../../exams/` contain 74 questions that belong to this domain: 21 from Exam 1 (graded), 20 from Exam 2, 26 from Exam 3, and 7 from the official practice set.

Each unit ends with the questions that test its content, and the rest form the mixed quiz in unit 07. Answers sit behind a fold, so decide before you open it. Exam 2 and 3 keys are ours and carry a confidence mark.

## Time

About five hours for the six units plus the review. Do units 01 to 03 in the morning of day 1, and 04 to 07 in the afternoon.
