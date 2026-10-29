---
type: Model
title: MiniCPM-OCR Jev
description: MiniCPM-OCR Jev is a 2B region-level OCR correctness model that scores candidate transcriptions for review routing or candidate selection.
tags: [ml, ocr, quality-assessment, document-parsing]
status: draft
created: 2026-10-28
generated: { by: llm-wiki-agent/1, at: 2026-10-28T16:49:13Z }
stale_after: 2027-04-28
sources:
  - id: minicpm-repo
    resource: ../raw/MiniCPM-OCR/README.md
    scope: ../raw/MiniCPM-OCR/
    kind: code
    revision: b33b474
    title: MiniCPM-OCR repository
---

# MiniCPM-OCR Jev

**Reported:** MiniCPM-OCR Jev is a 2B OCR correctness classifier trained from Qwen3.5-2B, replacing its language-model output head with a binary classification head. It scores a text, formula or table region using the original crop, OCR candidate text and a rendering of that candidate. It complements parsers such as [MiniCPM-OCR 1.0](minicpm-ocr-1-0.md), rather than generating OCR itself.[^minicpm-repo]

## Use and safeguards

A renderer-enabled service accepts the crop, candidate text and category; a service without a renderer also requires the rendered image. Scores support threshold-based review routing or best-of-N selection using the same crop and content boundaries. The vendor cautions that only `verdict: scored` indicates completed model scoring: fixed values for precheck, rendering or forward-pass failures are not low model scores. Select thresholds with application-specific labelled data and validate on an independent set; AUROC alone does not establish calibration or a universal threshold.[^minicpm-repo]

## Reported evaluation

The vendor's JevOCRBench figure reports AUROC ×100 of 93.6 overall, 94.6 text, 93.1 formula and 91.1 table. The guide reports 91.9–93.4 across four parsers on the same 200 randomly drawn samples, independently parsed and manually labelled. These are vendor-reported figures, not reproduced; small-sample cross-parser generalization and score calibration remain unestablished. [MiniCPM-OCR evaluation](minicpm-ocr-evaluation.md) records the individual cross-parser and comparator scores.[^minicpm-repo]

## Coverage and limits

The repository README, English Jev and 1.0 model guides, reproduction guide, environment manifest, benchmark JSON and two benchmark-table images were inspected; other deployment, training, API, renderer and SDK implementation, tests and remaining figures are pending. The external dataset and weights were not inspected; no code or evaluation was executed. The repository reports Apache-2.0 for code, documentation and weights. This incomplete package coverage makes the page draft; see [MiniCPM-OCR 1.0](minicpm-ocr-1-0.md) for the package-level ledger.[^minicpm-repo]

[^minicpm-repo]: [Repository README](../raw/MiniCPM-OCR/README.md), revision `b33b474`; `docs/minicpm_ocr_jev_en.md` §§ Base model and architecture, Use cases, Inference, Evaluation and License; `assets/minicpm-ocr/jev-benchmark-score-table.png`, MiniCPM-OCR Jev row.
