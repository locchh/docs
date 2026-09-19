# Build tooling for the learning path

These scripts insert the practice questions from `../../exams/` into the *Knowledge check* sections of the unit files, and guard the prose of the units when it is rewritten. They are only needed when writing, regenerating or reworking a domain.

| File | Purpose |
|---|---|
| `parse_questions.py` | Parses `exams/01/EXAM.md`, `exams/02/EXAM.md`, `exams/03/EXAM.md` and `exams/practice-questions.md` into `questions.json` (id, stem, options, answer key where the source has one, Exam 1 domain). Run from `aws/aip-c01/exams/`: `python3 ../learning-paths/_build/parse_questions.py ../learning-paths/_build/questions.json` |
| `questions.json` | All 230 questions in one structure. Question ids are `E1-Q12`, `E2-Q5`, `E3-Q70`, `PQ-Q3`. |
| `tags.json` | Domain tag for every Exam 2, Exam 3 and official question (`D1-1.4`, `D3`, `OOS`). Exam 1 questions carry their domain inside `questions.json`. `OOS` marks questions about model training or classical ML that are out of scope for AIP-C01. |
| `rationales_d1.json` | Answer, confidence and rationale for every Domain 1 question. `graded` = ExamPro key from Exam 1, `official` = AWS key from the practice set, `high` / `medium` = our key. One file per domain. |
| `build_kc.py` | Replaces `<!-- KC: E1-Q55, E3-Q10 -->` markers in unit files with the rendered questions and folded answers; `<!-- KC: REVIEW -->` receives every question of the domain not used elsewhere. Re-running it replaces the previously inserted blocks. |
| `READABILITY_SPEC.md` | The rules for the readability rewrite of the units: bold every key term, break walls of parallel items into lists, write explanations as narrative, and leave every fact, heading and generated block untouched. Read it before reworking a unit's prose. |
| `readability_check.py` | Mechanical guard for that rewrite. Compares a reworked unit with its committed version and fails if a heading, the generated *Knowledge check* block, a number, a code span, a link or a table cell changed, if the word count moved outside tolerance, or if an em dash appeared. Run `python3 readability_check.py --git <path>` from the repository root, one or more paths at a time. |

Rebuild Domain 1:

```
python3 build_kc.py 1 ../01-fm-integration-data-compliance rationales_d1.json
```

To add a domain: tag its questions in `tags.json` if not already tagged, write `rationales_dN.json`, put `<!-- KC: ... -->` markers in the new unit files, and run `build_kc.py N <units_dir> rationales_dN.json`.
