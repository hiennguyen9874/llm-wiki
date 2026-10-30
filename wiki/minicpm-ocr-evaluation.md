---
type: Benchmark
title: MiniCPM-OCR evaluation
description: MiniCPM-OCR evaluation records the project's reported OCR quality, throughput, and Jev correctness-assessment results with protocol and reproducibility limits.
tags: [ml, ocr, benchmarks, document-parsing, evaluation]
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

# MiniCPM-OCR evaluation

The MiniCPM-OCR project reports document parsing scores, RTX 5090 throughput and [MiniCPM-OCR Jev](minicpm-ocr-jev.md) correctness-assessment AUROC. These are **vendor-reported**, not independently verified; benchmark-specific protocols, incomplete reproduction materials and conflicts between repository artifacts constrain comparison.[^minicpm-repo]

## Document parsing comparison

The project figure reports the following overall scores (higher is better), with each column on its own benchmark scale. They are not a single cross-benchmark leaderboard.[^minicpm-repo]

| Model | OmniDocBench v1.6 | Real5 | Wild | olmOCR | CHAOS | OCRBench v2 |
|---|---:|---:|---:|---:|---:|---:|
| MiniCPM-OCR 1.0 | 96.51 | 93.68 | 92.39 | 82.7 | 29.78* | 54.7 |
| Xiaomi-OCR-0 | 96.83 | 92.73 | 92.06 | 82.1 | 17.84 | 47.0 |
| PaddleOCR-VL-1.6 | 96.34 | 93.19 | 91.49 | 80.2 | 9.32 | 35.2 |
| GLM-OCR | 95.22 | 90.32 | 90.40 | 75.2 | 8.62 | 45.5 |
| MinerU2.5-Pro | 95.75 | 88.94 | 90.06 | 79.5 | 13.90 | 29.1 |
| TeleOCR | 96.91 | 90.72 | 90.71 | 77.1 | 21.28 | 23.3 |
| Ovis-OCR2 | 96.58 | 92.29 | 89.91 | 80.3 | 6.38 | 33.3 |
| HunyuanOCR-1.5 | 94.74 | 88.70 | 87.01 | 78.6 | 14.88 | 45.0 |
| LightOnOCR-3-1B | 89.87 | 83.62 | 84.36 | 84.5 | 7.73 | 12.7 |
| chandra-ocr-2 | 92.27 | 88.74 | 89.08 | 85.8 | 2.87 | 32.9 |

*The image shows 29.78 for MiniCPM CHAOS, while `benchmark-data.json` leaves that value null and marks the model row `pending_confirmation`. The same figure contains six further models; those comparison-only rows remain available in the cited image. Its HunyuanOCR Real5 value 88.70 differs from the JSON's 88.542; no reconciliation is supplied.[^minicpm-repo]

**Reported protocol:** OmniDocBench v1.6 uses `quick_match`. For OmniDocBench, Real5 and Wild, Overall is the equal mean of `(1 − TextEdit) × 100`, Formula CDM and Table TEDS; reading order is reported separately and excluded from Overall. Real5 averages five 1,355-page scenario scores using v1.5 annotations. Wild uses v1.6 scoring with the corresponding v1.5 ground truth and SDK rotation correction. olmOCR averages eight category scores equally. CHAOS searches altered words in full-page output and averages page-level hit rates without aligning them to ground-truth boxes, so it is not equivalent to cropped-region recognition.[^minicpm-repo]

## Throughput

On the full 1,651-image OmniDocBench v1.6 set, an RTX 5090, image concurrency 1 and each system's accelerated configuration, the guide reports these values. P95 and P99 are time per sample; the table does not specify their unit.[^minicpm-repo]

| System | Pages/s | P95 | P99 |
|---|---:|---:|---:|
| MiniCPM-OCR 1.0 | 1.217 | 2.1 | 3.8 |
| GLM-OCR | 1.179 | 2.0 | 4.7 |
| PaddleOCR-VL-1.6 | 0.818 | 2.8 | 6.0 |
| Xiaomi-OCR-0 | 0.724 | 4.0 | 7.9 |
| MinerU2.5-Pro | 0.336 | 10.0 | 15.4 |

MiniCPM's reported throughput at image concurrency 1, 2, 4, 6 and 8 is respectively 1.217, 1.613, 1.888, 2.031 and 2.133 pages/s. Regions within each page may run concurrently even at image concurrency 1. The 55% DSpark end-to-end efficiency improvement is a vendor claim; the guide says complete comparison commands and logs remain to be added.[^minicpm-repo]

## JevOCRBench

JevOCRBench evaluates human-labelled correct/incorrect region candidates. The figure reports **AUROC ×100**: Jev overall/text/formula/table = 93.6/94.6/93.1/91.1; JEV 35B-A3B = 90.1/91.6/88.9/89.6; Qwen3.5 397B-A17B = 93.8/95.4/91.8/91.4. In the project's 200-sample cross-parser test, Jev scores 92.7, 91.9, 93.4 and 93.1 against MiniCPM, GLM-OCR, PaddleOCR-VL-1.6 and Xiaomi candidates respectively. AUROC does not establish calibrated probabilities or a safe automatic-acceptance threshold.[^minicpm-repo]

## Contradictions and limits

- The guide and reproduction document give **1.217 pages/s** for MiniCPM at concurrency 1; `benchmark-data.json` gives **1.213 pages/s** under its stated conditions. Both are source-reported; the difference is unresolved.[^minicpm-repo]
- The HunyuanOCR Real5 figure and JSON values differ, and MiniCPM's CHAOS number is printed in the image but missing from the JSON pending-confirmation row. These are not resolved by choosing one artifact as ground truth.[^minicpm-repo]
- Complete evaluation scripts, exact versions, timing boundaries and DSpark comparison logs are explicitly pending in the reproduction guide; benchmark datasets, predictions and external scorers were not inspected or executed. The figures and guides were inspected, but other repository figures and implementation remain pending; see the [package coverage ledger](minicpm-ocr-1-0.md#coverage-and-trust). The page is draft.[^minicpm-repo]

## Relationships

- **Compared in:** [Document OCR model benchmark comparison](document-ocr-model-benchmark-comparison.md), which places this model's reported results beside nine other document parsers per dataset.
- **Evaluates:** [MiniCPM-OCR 1.0](minicpm-ocr-1-0.md) and [MiniCPM-OCR Jev](minicpm-ocr-jev.md).[^minicpm-repo]
- **Complements:** [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md); keep these vendor-run figures separate from its other evaluation protocols.[^minicpm-repo]

[^minicpm-repo]: [MiniCPM-OCR repository README](../raw/MiniCPM-OCR/README.md), revision `b33b474`; [OCR benchmark figure](../raw/MiniCPM-OCR/assets/minicpm-ocr/ocr-benchmarks.png), all indicated model rows; [benchmark-data JSON](../raw/MiniCPM-OCR/assets/minicpm-ocr/benchmark-data.json), `benchmarks.models` and `throughput`; [1.0 guide](../raw/MiniCPM-OCR/docs/minicpm_ocr_1dot0_en.md), §§ Evaluation and Throughput; [reproduction guide](../raw/MiniCPM-OCR/docs/benchmark_reproduction_en.md), §§ Evaluation Settings, Scoring and Aggregation Rules, Parsing Efficiency Test; [Jev figure](../raw/MiniCPM-OCR/assets/minicpm-ocr/jev-benchmark-score-table.png), comparison rows; [Jev guide](../raw/MiniCPM-OCR/docs/minicpm_ocr_jev_en.md), § Evaluation.
