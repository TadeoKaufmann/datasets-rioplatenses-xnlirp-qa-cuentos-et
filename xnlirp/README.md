# XNLIrp

An adaptation of [XNLI](https://github.com/facebookresearch/XNLI) to Rioplatense Spanish (RP). I took the 7,500 evaluation instances of XNLI (5,010 test and 2,490 validation, professionally translated into European Spanish by the original authors) and adapted them while keeping the inference label (`entailment` / `neutral` / `contradiction`) and a one to one correspondence between both versions.

This makes it possible to evaluate the same model on the same instances in two varieties of Spanish.

## Dataset

`dataset/dataset_final.jsonl`, one instance per line. Main fields:

| Field | Description |
|---|---|
| `idx` | instance index |
| `label`, `label_int` | NLI label |
| `prem_en`, `hyp_en` | English premise and hypothesis (original XNLI) |
| `prem_es`, `hyp_es` | European Spanish premise and hypothesis (original XNLI) |
| `prem_rp`, `hyp_rp` | Rioplatense adaptation |
| `type` | `A` no change, `B` vocabulary and tense, `C` grammar and *voseo*, `D` fix of an error in the Spanish translation, `E` cultural adaptation |
| `secondary_features` | other types, when an instance combines several changes |
| `changes` | description of what was changed |
| `lev_total` | character level Levenshtein distance between the ES and RP versions, premise plus hypothesis |
| `split` | `test` or `validation`, as in XNLI |
| `provenance` | automatic grader verdict and native speaker validation, where available |

**Type distribution:** A 50.8 %, B 16.1 %, C 7.0 %, D 14.9 %, E 11.2 %.

`respuestas_anotadores_anonimizado.csv` holds the 7,120 responses of the native validation campaign, with annotators replaced by IDs. Its columns are in Spanish: `anotador_id` (annotator), `respuesta` (naturalness from 1 to 5), `comentario_prem` and `comentario_hyp` (free comments), `region`, and `palabras_marcadas` (words the annotator marked as unnatural).

See [known issues](../README.md#known-issues) before using the Rioplatense text.

## Pipeline

```
Gemini 2.5 Flash adapts ES→RP (prompt v2)
    └─► Automatic grader (gpt-4o-mini, Batch API)
           ├─ ok ───────► Native validation (web app, 1 to 5)
           │                 ├─ good ──► final dataset
           │                 └─ low score or marked words ──► correction
           └─ flagged ──► correction
Correction: LLM assisted review, then a second Gemini pass with the annotators' feedback
```

| File | Purpose |
|---|---|
| `prompts/prompt_v2_cultural_inline.txt` | final adaptation prompt: typology, vocabulary rules and cultural adaptation rules |
| `prompts/grader_prompt.txt` | automatic grader prompt |
| `scripts/translate_xnli.py` | translation harness over the Gemini Batch API |
| `scripts/grade_translations.py` | automatic grading over the OpenAI Batch API |
| `scripts/evaluate_against_gold.py` | compares a run against a gold set |
| `scripts/build_dataset_final.py` | assembles the final dataset from translations and corrections |

The prompts are in Spanish because they are the instructions the models actually received.

The scripts are kept as I used them. Some expect intermediate files from my working repository that are not published, so they document the process more than they rebuild it from scratch.

## Two design decisions

- I adapted **from European Spanish, not from English**, so that both versions carry the same translation artifacts and the comparison stays controlled.
- I always adapted the **whole triple** (premise, hypothesis, label) in a single call, so that names and references stay consistent between both texts.

## Requirements

The scripts read these environment variables from a `.env` file that is not included: `GOOGLE_API_KEY` (Gemini) and `OPENAI_API_KEY` (grading).
