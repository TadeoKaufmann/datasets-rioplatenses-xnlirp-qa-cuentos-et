# QA-Cuentos ET

An answer sentence selection (reading comprehension) dataset in Rioplatense Spanish, built on the **Cuentos corpus** ([Travi et al., 2026](https://doi.org/10.1038/s41597-026-06798-z)): 30 short stories, 20 of which have eye-tracking data from 113 native readers.

The task is binary classification: given a question and a candidate sentence from the story, predict whether the sentence answers the question.

## Dataset

`dataset/qa_{train,dev,test}.jsonl`: 1,788 questions and 8,940 instances (one positive and four negatives per question). Splits are assigned **by story**, so no story appears in more than one of them.

| Split | Stories | Questions | Instances | From stories with eye-tracking | Without |
|---|---|---|---|---|---|
| train | 11 | 668 | 3,340 | 1,120 | 2,220 |
| dev | 10 | 639 | 3,195 | 1,055 | 2,140 |
| test | 9 | 481 | 2,405 | 1,230 | 1,175 |

The test split is balanced between both groups of stories, to compare them directly.

| Field | Description |
|---|---|
| `id` | instance identifier |
| `story` | story title |
| `unit_idx`, `unit` | candidate sentence |
| `question` | question |
| `label` | 1 if the sentence answers the question |
| `question_type` | `factual` or `inferencial` |
| `answer_unit_idx` | index of the sentence that answers it |
| `round` | generation round |
| `is_et` | whether the story has eye-tracking data |

## Pipeline

1. **Target sentences**: sentences of 8 to 80 words from each story.
2. **Hard negatives**: random negatives made the task too easy (macro F1 around 90 to 93), so the four negatives are the sentences of the same story closest in meaning to the target, using OpenAI `text-embedding-3-small` with a cosine similarity ceiling of 0.55.
3. **Questions**: Gemini 2.5 Flash writes a question that only the target sentence answers. Half are inferential (they need synonyms or common sense) and half are literal but rephrased.
4. **Validation**: Claude Haiku, a different model from the generator, sees the question and the five unlabelled sentences. A question is valid only if it picks exactly the target. Failures go through a regeneration pass.

| File | Purpose |
|---|---|
| `prompts/generation/v1.txt` to `v3.txt` | evolution of the generation prompt |
| `prompts/hardening_v1.txt` | regenerates questions that were too easy |
| `prompts/grader_v1.txt` | validator prompt |
| `scripts/generate_batch.py` | batch question generation |
| `scripts/build_hard_negatives_embeddings.py` | negative selection with embeddings (final method) |
| `scripts/build_hard_negatives.py` | earlier TF-IDF variant, kept for reference |
| `scripts/validate_consistency.py` | validation with Claude Haiku |
| `scripts/harden_dataset.py` | regenerates questions and negatives that failed |
| `scripts/build_qa_final.py` | assembles the final dataset |

The prompts are in Spanish because they are the instructions the models actually received.

## Reproducing

The scripts are kept as I used them and expect the layout of my working repository. In particular, generation needs the story texts, which are **not included here**: get them from the [Cuentos corpus on figshare](https://doi.org/10.6084/m9.figshare.28311908).

Environment variables, read from a `.env` file that is not included: `GOOGLE_API_KEY` (Gemini), `ANTHROPIC_API_KEY` (validation) and `OPENAI_API_KEY` (embeddings).
