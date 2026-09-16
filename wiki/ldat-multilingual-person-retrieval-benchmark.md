---
type: Concept
title: LDAT multilingual person-retrieval benchmark
description: LDAT translates four English person-retrieval datasets into Chinese, French, and German by filtering LLM translations and rewriting suspected errors with domain-adapted multimodal models.
tags: [datasets, multilingual, data-curation, machine-translation, person-reidentification]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:19:16Z }
sources:
  - id: arxiv-2510.17685v1
    resource: ../raw/papers/arXiv-2510.17685v1/main.tex
    title: Multilingual Text-to-Image Person Retrieval via Bidirectional Relation Reasoning and Aligning
---

# LDAT multilingual person-retrieval benchmark

LMs-driven Domain Adaptive Translation (LDAT) constructs multilingual counterparts of CUHK-PEDES, ICFG-PEDES, RSTPReid, and UFineBench. It translates each English person description into Chinese, French, and German, filters translations using a reference-free quality score, and rewrites suspected errors with a multimodal model fine-tuned on cleaner image-source-target triples. The resulting datasets retain English and add the three generated languages; only their test sets are reported as manually inspected and revised.[^arxiv-2510.17685v1]

## Pipeline

1. **Translate:** Qwen generates Chinese descriptions; LLaMA 3 generates French and German descriptions from fixed translation prompts.[^arxiv-2510.17685v1]
2. **Filter:** COMETKiwi scores each English/translation pair. Noise is defined as $1-\Phi(T^s,\widetilde T^t)$, and examples above a threshold are considered noisy. The threshold is the rounded mean noise score for the corpus; the Chinese CUHK-PEDES study reports the best downstream retrieval at $\theta=0.15$.[^arxiv-2510.17685v1]
3. **Adapt and rewrite:** Qwen-VL for Chinese and Phi for French/German are LoRA-fine-tuned for one epoch on the clean triples. Their prompts include the person image and English source, and they regenerate only translations classified as noisy.[^arxiv-2510.17685v1]
4. **Evaluate:** the authors manually inspect and revise the test sets, then train and evaluate retrieval systems on the multilingual corpora.[^arxiv-2510.17685v1]

**Synthesis:** LDAT is a weak-supervision loop rather than a conventional benchmark-translation protocol. An automatic cross-lingual scorer decides which generated examples become trusted supervision, while visual context is introduced only for rewriting. This scales curation, but scorer errors can propagate because the “clean” training set is not reported as manually validated.

## Dataset scope

| Dataset | Images | Descriptions per language | Identities | Notable split detail |
|---|---:|---:|---:|---|
| CUHK-PEDES(M) | 40,206 | 80,440 | 13,003 | 34,054 train and 3,074 test images reported |
| ICFG-PEDES(M) | 54,522 | 54,522 | 4,102 | 34,674 train and 19,848 test images |
| RSTPReid(M) | 20,505 | 41,010 | 4,101 | 3,701/200/200 train/validation/test identities |
| UFineBench(M) | 26,206 | 52,412 | 6,926 | 18,577 train and 7,629 test images |

Each image retains its original English description(s) and receives Chinese, French, and German counterparts. The manuscript links data and code at <https://github.com/Flame-Chasers/Bi-IRRA>.[^arxiv-2510.17685v1]

## Reported evidence and trust limits

On CUHK-PEDES(M), Bi-IRRA trained with full LDAT data reports English/Chinese Rank-1 of 78.82/76.43. Direct LLM translation gives 78.09/75.89; direct multimodal translation gives 78.61/76.19; and rewriting with a text-only LLM gives 78.22/76.02. Full LDAT is best on Rank-1 and mAP, but gains over direct multimodal translation are small: 0.21 English Rank-1 and 0.24 Chinese Rank-1.[^arxiv-2510.17685v1]

- Translation quality is primarily validated through downstream retrieval and selected qualitative examples. The paper reports no human adequacy/fluency scores, inter-annotator agreement, error taxonomy frequencies, or comparison against professional translation.[^arxiv-2510.17685v1]
- COMETKiwi is applied without references, but the manuscript describes similarity between extracted source/target representations rather than enough implementation detail to reproduce the exact score. Thresholding at the corpus mean is heuristic and is tuned analytically on Chinese CUHK-PEDES.[^arxiv-2510.17685v1]
- Manual review is stated only for test sets. Training translations may retain hallucinations, mistranslations, or errors inherited from English source captions; the examples explicitly show misspellings and malformed source descriptions.[^arxiv-2510.17685v1]
- These are translated benchmark extensions, not independently collected native-language corpora. Results may reflect translation style and parallel-caption structure rather than natural multilingual query behavior.[^arxiv-2510.17685v1]
- The paper does not document release licensing, per-language annotation provenance beyond the pipeline, or whether every revised test translation is distributed; these must be checked in the released dataset before reuse.

## Relationships

- **Used by:** [Bi-IRRA multilingual text-to-image person retrieval](bi-irra-multilingual-person-retrieval.md) is trained and evaluated on the four LDAT-generated datasets.[^arxiv-2510.17685v1]

[^arxiv-2510.17685v1]: Min Cao, Xinyu Zhou, Ding Jiang, Bo Du, Mang Ye, and Min Zhang, “Multilingual Text-to-Image Person Retrieval via Bidirectional Relation Reasoning and Aligning,” arXiv:2510.17685v1, 2025, [`main.tex`](../raw/papers/arXiv-2510.17685v1/main.tex). Included LDAT ablations and the pipeline and translation-rewrite figures in the same source bundle were also inspected.
