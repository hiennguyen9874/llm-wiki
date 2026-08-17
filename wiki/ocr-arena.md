---
type: Evaluation Method
title: OCR Arena
description: OCR Arena is a pairwise LLM-as-judge protocol for Markdown OCR that uses position-swapped comparisons, ties inconsistent judgments, and aggregates results with bootstrapped Elo ratings.
tags: [evaluation, ocr, llm-as-judge, elo, document-parsing]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:58:33Z }
sources:
  - id: multimodal-ocr-paper
    resource: ../raw/2603.13032_MultimodalOCR/main.tex
    title: "Multimodal OCR: Parse Anything from Documents"
---

# OCR Arena

OCR Arena is an author-described pairwise evaluation protocol for Markdown OCR. A high-capacity vision-language model receives the source document image and two candidate transcriptions, judges their content accuracy, and the resulting head-to-head outcomes are aggregated as Elo ratings.[^multimodal-ocr-paper]

## Protocol

The supplied prompt directs the judge to prioritize text, table, and formula content accuracy: typos, omissions, hallucinations, table-cell correctness and alignment, and formula correctness, completeness, and semantic equivalence. It directs the judge to ignore Markdown formatting, layout and typesetting differences, headers and footers, and all image/figure-processing differences. The judge returns JSON naming model 1, model 2, or a tie with an explanation.[^multimodal-ocr-paper]

Each model pair is judged twice, swapping candidate order. A win is credited only when the judge gives the same preference in both orders; a preference reversal or other contradiction becomes a tie. This is intended to reduce positional bias.[^multimodal-ocr-paper]

The paper initializes Elo ratings at $R$ and uses expected score $E_A = 1 / (1 + 10^{(R_B-R_A)/400})$, then updates with $R'_A = R_A + 32(S_A-E_A)$. To reduce ordering effects in Elo aggregation, it shuffles the full battle history in 1,000 bootstrap iterations and reports each model's mean rating.[^multimodal-ocr-paper]

## Interpretation limits

OCR Arena measures the preferences of the configured judge under this task-specific prompt, not ground-truth error rate. Its prompt intentionally excludes figure handling and de-emphasizes formatting and layout, so it should not be used as a general measure of multimodal document reconstruction.[^multimodal-ocr-paper]

The source identifies Gemini 3 Flash as the judge but does not supply battle records, sampled documents, complete model prompts and outputs, judge settings, or uncertainty intervals for ratings. The claimed positional-bias control does not establish freedom from other judge, dataset, or selection biases; independent reproduction is not possible from this bundle.[^multimodal-ocr-paper]

## Relationships

- **Evaluates:** [Multimodal OCR](multimodal-ocr.md) is assessed with this protocol alongside other OCR systems in the source's tables.

[^multimodal-ocr-paper]: Zheng et al., *Multimodal OCR: Parse Anything from Documents*, local LaTeX source at [main.tex](../raw/2603.13032_MultimodalOCR/main.tex), including visually reviewed [OCR Arena prompt](../raw/2603.13032_MultimodalOCR/Fig/Prompt.pdf) and [judge examples](../raw/2603.13032_MultimodalOCR/Fig/Judge-examples.pdf) (accessed 2026-08-17).