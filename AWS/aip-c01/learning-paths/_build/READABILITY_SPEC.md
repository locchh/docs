# Readability rewrite spec

A pass over every unit in `learning-paths/` to make the prose easier to read.
The information does not change. Not one fact, number, service name, limit,
exam mapping or recommendation may be added, removed or altered. This is a
presentation rewrite only.

## What is wrong today

Three complaints from the reader, in priority order.

1. **Key terms are not highlighted.** AWS service names, components, features,
   API operations and exam-relevant concepts sit in plain text, so the eye
   cannot find them. Bold is used inconsistently: a service is bold in one
   paragraph and plain in the next.
2. **Paragraphs are walls.** A single paragraph lists five services, or three
   categories each with three items, or six error codes, in one unbroken run of
   sentences. The reader cannot tell where one item ends and the next begins.
3. **Sentences are compressed to the point of meaninglessness.** Clauses are
   stacked with commas and parentheses to save words, so a sentence carries six
   ideas and none of them lands. Explanations should read as narrative: one idea
   per sentence, in an order a person can follow.

## Rule 1: bold every key term

Bold, at **every** appearance, not only the first:

- AWS service and product names: **Amazon Bedrock**, **AWS Lambda**,
  **Amazon SageMaker AI**, **Amazon API Gateway**, **AWS Step Functions**.
  Short forms count too: **Lambda**, **Bedrock**, **SQS**, **S3**.
- Named features and components of a service: **Bedrock Guardrails**,
  **Knowledge Bases**, **Provisioned Throughput**, **usage plans**,
  **dead-letter queue**, **visibility timeout**, **reserved concurrency**,
  **WebSocket API**, **function URL**, **Choice state**.
- Named patterns and concepts the exam tests: **RAG**, **circuit breaker**,
  **exponential backoff with jitter**, **least privilege**, **model cascading**,
  **intelligent prompt routing**.
- Named third-party tools and frameworks when they are the point of the
  sentence: **Strands Agents**, **LangChain**, **MCP**.

Do NOT bold:

- Code: API operations, parameters, error codes, ARNs, CLI flags stay in
  backticks and are not bolded: `InvokeModel`, `ThrottlingException`,
  `maxReceiveCount`. Backticks are their highlight.
- Generic words: "model", "prompt", "token", "request", "endpoint" when used
  generically. Bold them only when they are part of a proper name.
- Whole sentences or phrases for emphasis. Bold marks terms, not importance.
- Anything inside a heading. Headings are already prominent.
- Anything inside the generated Knowledge check block (see Rule 5).

If a service is bolded in one paragraph, it is bolded in every paragraph. Search
the file for each service name after rewriting and check.

## Rule 2: break walls into lists and short paragraphs

Convert to a bulleted list whenever a paragraph enumerates three or more
parallel items, each of which a reader might want to find on its own. The
signature is a sentence pattern such as "X: description. Y: description. Z:
description." or "A, B and C, where A does ..., B does ... and C does ...".

Before:

> Start with where anything runs on AWS. Functions: AWS Lambda runs code per
> request with no servers, up to fifteen minutes and ten gigabytes of memory.
> Containers: Amazon ECS runs containers on AWS Fargate (serverless) or EC2,
> Amazon EKS runs Kubernetes, and AWS App Runner is the simplest way to run a
> web container. Virtual machines: Amazon EC2, including GPU and accelerator
> instance families.

After:

> Start with where anything runs on AWS.
>
> - **Functions.** **AWS Lambda** runs code per request with no servers, up to
>   fifteen minutes and ten gigabytes of memory.
> - **Containers.** **Amazon ECS** runs containers on **AWS Fargate**
>   (serverless) or **EC2**. **Amazon EKS** runs Kubernetes. **AWS App Runner**
>   is the simplest way to run a web container.
> - **Virtual machines.** **Amazon EC2**, including GPU and accelerator instance
>   families.

Other list triggers:

- A run of error codes, each with a meaning: one bullet per code.
- A run of "if the stem says X, the answer is Y" mappings: one bullet per
  mapping, in the form `**stem wording** → **answer**`.
- Steps of a process or workflow: a numbered list.
- Three or more services compared on the same axis: a list, or a table if
  there are two or more axes.

Keep as prose when the items are not parallel, when there are only two, or
when the sentence is genuinely making one connected argument that a list would
chop up.

Paragraph length: aim for two to five sentences. A paragraph longer than
roughly 120 words almost always contains two ideas; split it at the seam. Put a
blank line before and after every list.

## Rule 3: rewrite compressed explanations as narrative

This rule applies to the explanatory sections: the lead paragraphs and every
`##` topic section before the Worked scenario. It applies more lightly to the
Worked scenario. It does not apply to the Exam lens bullets (already terse by
design), the Knowledge check (generated) or the Summary (a recap).

Signs a sentence needs rewriting:

- More than one parenthetical aside.
- Three or more clauses joined by commas or semicolons, each introducing a
  different idea.
- A term defined inside the sentence that uses it, in a parenthesis.
- The reader has to hold four things in memory to reach the verb.

How to rewrite:

- One idea per sentence. If a sentence contains a definition and a usage,
  split them: define first, then use.
- Move parenthetical definitions into their own sentence or into a list item.
- Where a sentence lists what something contains or does, and the list has
  three or more items, make it a list (Rule 2).
- Keep the connective tissue. "so", "because", "which means" are what make
  prose readable; do not strip them to save words.
- Write it the way you would say it to a colleague who asked you to explain,
  not the way you would compress it into a cheat sheet.

Before (one paragraph from a Worked scenario):

> Where determinism matters (the refund decision), a Step Functions state
> machine implements the reason-act-observe loop with an iteration limit, task
> timeouts, a Catch that opens a circuit to a fallback path after repeated tool
> failures, and a wait-for-callback step that pauses for a human approver when
> the refund exceeds the threshold, recording the decision in DynamoDB. Every
> tool sits behind a Lambda function that validates the model's arguments
> against the tool schema and returns a corrective message when they are
> malformed, and each role carries least-privilege IAM permissions with a
> permission boundary.

After:

> When a process must be predictable, such as deciding whether to issue a
> refund, **AWS Step Functions** controls the reason-act-observe workflow.
>
> The Step Functions workflow includes:
>
> - An **iteration limit** to prevent endless loops.
> - **Task timeouts** to stop tasks that run too long.
> - **Catch and circuit-breaker logic** to use a fallback path after repeated
>   tool failures.
> - **Wait for callback** to pause the workflow and request human approval when
>   a refund is above the allowed threshold.
> - **DynamoDB** to store the approval decision.
>
> Every tool is placed behind a **Lambda function**. Lambda checks the model's
> arguments against the tool schema before executing the tool. If the arguments
> are invalid, it returns a clear message so the model can correct them and try
> again.
>
> Each agent or service uses **least-privilege IAM permissions** and a
> **permission boundary** so it cannot perform actions outside its authorized
> scope.

Notice that every fact in the before appears in the after. Nothing was added
except connective words; nothing was dropped.

## Rule 4: what stays exactly as it is

- **Every fact.** Numbers, limits, dates, prices, service names, API names,
  error codes, quotas, defaults, exam question mappings. If you are unsure
  whether a rewording changes a fact, keep the original wording for that
  clause.
- **Every heading**, character for character, in the same order.
- **The Exam lens bullets' meaning and mappings.** You may bold terms inside
  them and split a bullet that carries two mappings into two bullets. Do not
  reword the stem phrases in quotes; they are the exam's language.
- **Code spans** and code blocks, byte for byte.
- **Links**, targets and link text.
- **Tables**: content unchanged. You may bold service names inside cells.
- The word "Summary" section keeps its content; you may bold and split
  paragraphs but do not expand it.

## Rule 5: the Knowledge check block is off limits

Everything from the line `## Knowledge check` down to the line before
`## Summary` is generated by `_build/build_kc.py` from the `<!-- KC: ... -->`
marker and the exam files. Do not edit one character of it, including bold,
line breaks or spacing. A rebuild would overwrite your work, and the reader
asked for exam text to stay as it is.

The mechanical check (`_build/readability_check.py`) fails the file if this
block changed.

## Rule 6: the usual prose rules still hold

- No em dash, U+2014, in rewritten prose. Preserve any in the untouched
  generated questions under Rule 5. Use a comma, a colon, or a new sentence. The
  en dash in "Solutions Architect - Associate" style names is fine.
- No emoji, no exclamation marks, no marketing adjectives.
- US spelling (the source is mostly US; do not introduce British spellings).
- Arrows (→) are fine inside Exam lens style mappings and are already in use.

## Procedure per file

1. Read the whole file first. Note every service name that appears, so your
   bolding is consistent.
2. Rewrite section by section, top to bottom, stopping at `## Knowledge check`.
   Resume at `## Summary`.
3. Run the check:

   ```
   python3 aws/aip-c01/learning-paths/_build/readability_check.py <old-file-from-git> <new-file>
   ```

   or, from the repository root, letting the script fetch the committed
   version itself:

   ```
   python3 aws/aip-c01/learning-paths/_build/readability_check.py --git <path>
   ```

   It fails if headings changed, if the Knowledge check block changed, if the
   multiset of numbers or code spans changed, if the word count moved outside
   the allowed band, or if an em dash appeared. Fix every failure before
   reporting.

   The checker also protects generated mixed quizzes using their `KC` markers,
   complete links, fenced code blocks and table content apart from bold markup.
   Numeric comparisons ignore trailing punctuation and digits embedded in
   identifiers such as S3 or A2A; repeating a service name is not a numeric
   content change. Passing this check protects structure and selected content,
   but does not replace a manual review for meaning and readability.
4. Re-read the result once as a reader. If a list has one item, it is a
   paragraph. If a paragraph still has two parentheticals, split it.

## Definition of done for one file

- `readability_check.py` passes.
- Every AWS service and named component is bold at every appearance outside
  headings, code and the Knowledge check block.
- No paragraph outside the Knowledge check block enumerates three or more
  parallel items in running prose.
- No explanatory sentence carries more than one parenthetical aside.
- A reader who knew the old file would find every fact in the new one.
