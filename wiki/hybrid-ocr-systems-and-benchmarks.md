---
type: Synthesis
title: Hybrid OCR systems and benchmarks
description: Hybrid OCR systems and benchmarks catalogs retained multi-stage OCR models, their datasets, metrics, reported results, protocol boundaries, and evidence limits.
tags: [ocr, document-parsing, layout-analysis, benchmarks, evaluation, hybrid-systems]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T22:11:53+07:00 }
sources:
  - id: paddleocr3-report
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
  - id: paddleocr-vl-report
    resource: ../raw/2510.14528_PaddleOCR-VL/main.tex
    title: PaddleOCR-VL Technical Report
  - id: paddleocr-vl-1-5-report
    resource: ../raw/2601.21957_PaddleOCR-VL-1.5/main.tex
    title: PaddleOCR-VL-1.5 Technical Report
  - id: paddleocr-vl-1-6-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    title: PaddleOCR-VL-1.6 Technical Report
  - id: glm-ocr-report
    resource: ../raw/2603.10910_GLM-OCR/main.tex
    title: GLM-OCR Technical Report
  - id: falcon-perception-report
    resource: ../raw/2603.27365_FalconPerception/main.tex
    title: Falcon Perception
  - id: mineru2-5-card
    resource: ../raw/MinerU2.5-2509-1.2B.md
    title: MinerU2.5-2509-1.2B model card
  - id: mineru2-5-pro-card
    resource: ../raw/MinerU2.5-Pro-2604-1.2B.md
    title: MinerU2.5-Pro-2604-1.2B model card
  - id: mineru2-5-pro-2605-card
    resource: ../raw/MinerU2.5-Pro-2605-1.2B.md
    title: MinerU2.5-Pro-2605-1.2B model card
  - id: surya-ocr-2-card
    resource: ../raw/surya-ocr-2.md
    title: Surya OCR 2 model card
  - id: nemotron-ocr-v2-card
    resource: ../raw/nemotron-ocr-v2.md
    title: Nemotron OCR v2 model card
---

# Hybrid OCR systems and benchmarks

**Hybrid OCR is not a standardized model class in the retained sources.** This page uses an operational definition: an inference system is hybrid when it composes separately applied localization, layout or reading-order analysis, recognition, specialist parsing, or reconstruction stages. Under that definition, the core family is the same as [layout-first modular OCR](layout-first-modular-ocr-benchmarks.md); [Surya OCR 2](surya-ocr-2.md) and [Nemotron OCR v2](nemotron-ocr-v2.md) are boundary cases. The closest common full-document comparison is OmniDocBench v1.6, where the author-reproduced table reports [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) at 96.33 overall. Protocol drift and first-party evidence prevent a universal ranking.[^paddleocr-vl-1-6-report]

## Scope and complete retained model roster

| Model or release | Inference composition | Scope decision |
|---|---|---|
| [PP-StructureV3](pp-structurev3.md) | Preprocessing + PP-OCRv5 + layout/article detection + specialist table/formula/chart/seal models + reading-order reconstruction | Core hybrid pipeline[^paddleocr3-report] |
| [PaddleOCR-VL](paddleocr-vl.md) | PP-DocLayoutV2 regions/order → task-conditioned element VLM | Core; deprecated predecessor |
| [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) | PP-DocLayoutV3 polygonal regions/order → element VLM + long-document postprocessing | Core; deprecated predecessor |
| [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) | Same two-stage path as 1.5; data and CPT–SFT–GRPO changed | Core current release |
| [GLM-OCR](glm-ocr.md) | PP-DocLayoutV3 regions/order → CogViT–GLM recognizer; separate full-page KIE path | Core |
| [FalconOCR](falcon-ocr.md) | PP-DocLayoutV3 regions/order → text/formula/table recognizer | Core |
| [MinerU2.5](mineru2-5.md) | Low-resolution global layout → native-resolution text/formula/table crops | Core |
| [MinerU2.5-Pro](mineru2-5-pro.md) 2604/2605 | MinerU2.5 two-step extraction with data-centric updates | Core release family |
| [Surya OCR 2](surya-ocr-2.md) | Shared VLM for layout/OCR/tables + separate line detector; optional layout-first block mode | Boundary: hybrid operation is optional |
| [Nemotron OCR v2](nemotron-ocr-v2.md) English/multilingual | Convolutional detector → Transformer recognizer → relational grouping/reading order | Boundary: hybrid plain-text OCR, not rich document reconstruction |

[PP-OCRv5](pp-ocrv5.md) and [PP-OCRv6](pp-ocrv6.md) are excluded as detector–recognizer OCR rather than hybrid document parsers; pure page-to-structure VLMs are covered by [End-to-end generative OCR VLM benchmarks](end-to-end-generative-ocr-vlm-benchmarks.md). PaddleOCR 3.0 is a toolkit, while PP-DocLayoutV2/V3 are components rather than complete OCR systems.

## Dataset and metric coverage by model

| Model | Retained evaluation datasets or protocols |
|---|---|
| PP-StructureV3 | OmniDocBench v1.0/v1.5; Real5-OmniDocBench; Paddle private chart set |
| PaddleOCR-VL | OmniDocBench v1.0/v1.5/v1.6; Real5; olmOCR-Bench; cropped OmniDoc OCR/table/formula blocks; Ocean-OCR-Handwritten; private OCR/table/formula/chart sets; throughput |
| PaddleOCR-VL-1.5 | OmniDocBench v1.5/v1.6; Falcon English-only v1.5; Real5; Falcon English-filtered olmOCR-Bench; private chart, text-spotting, and seal sets; throughput |
| PaddleOCR-VL-1.6 | OmniDocBench v1.6; Real5; private hard-table, chart, text-spotting, and seal sets |
| GLM-OCR | OmniDocBench v1.5/v1.6; Real5; OCRBench Text; UniMERNet; PubTabNet; TEDS_TEST; Nanonets-KIE; Handwritten-KIE; six private scenario sets; throughput |
| FalconOCR | English-only OmniDocBench v1.5; English-filtered olmOCR-Bench; throughput |
| MinerU2.5 | OmniDocBench v1.0/v1.5/v1.6; Real5; olmOCR-Bench; Paddle cropped OCR/table/formula and handwriting sets; GLM public comparison table; throughput |
| MinerU2.5-Pro | OmniDocBench v1.6; Real5; five unnamed table benchmarks; dense-formula and text metrics; throughput |
| Surya OCR 2 | olmOCR-Bench; internal 91-language suite; RTX 5090 and Apple Silicon throughput |
| Nemotron OCR v2 | OmniDocBench crop mode; generated SynthDoG; A100 throughput |

## Benchmark and metric map

| Dataset or protocol | Evaluated capability | Metrics | Direction and qualification |
|---|---|---|---|
| OmniDocBench v1.0 | Bilingual full-page parsing | Overall/text/formula/table/order edit distance; table TEDS | Edit ↓; TEDS ↑; 981-page evaluator is not interchangeable with later versions |
| OmniDocBench v1.5 | Full-page text, formula, table, and order | Overall; text NED; formula CDM; table TEDS/TEDS-S; order NED | Overall/CDM/TEDS ↑; NED ↓; Falcon removes Chinese pages |
| OmniDocBench v1.6 | v1.5 plus MGAM matching and hard pages | Same component schema | Closest retained common protocol; reports and release cards still conflict slightly |
| Real5-OmniDocBench | Five physical distortion conditions | Overall and scan/warp/screen-photo/illumination/skew scores | ↑; derived from v1.5 annotations |
| olmOCR-Bench | Machine-verifiable PDF extraction | Overall and eight category pass rates | ↑; filters, anchoring, HTML handling, and harness versions differ |
| OCRBench Text | Text recognition | Source-table score | ↑; exact GLM protocol is incomplete |
| UniMERNet | Formula recognition | Source-table score | ↑; metric implementation is not named in GLM's table |
| PubTabNet / TEDS_TEST | Table recognition | Source-table score | ↑; configurations are incomplete |
| Nanonets-KIE / Handwritten-KIE | Key information extraction | Source-table score | ↑; GLM uses its separate full-page path |
| Cropped OmniDocBench blocks | Element recognition with layout held out | Text NED; table TEDS/TEDS-S/edit; formula CDM | NED/edit ↓; others ↑; not end-to-end parsing |
| Ocean-OCR-Handwritten | EN/ZH handwriting | Edit, F1, precision, recall, BLEU, METEOR | Edit ↓; others ↑ |
| Private Paddle/GLM suites | OCR, tables, formulas, charts, spotting, seals, KIE | NED, TEDS, CDM, RMS-F1, accuracy, unnamed 0–100 scores | Task-dependent; datasets and executable protocols unavailable |
| Generated SynthDoG | Six-language page OCR | Page-average NED | ↓; synthetic and incompletely configured |
| Throughput protocols | Deployment performance | pages/s, images/s, tokens/s, latency | Hardware, render, batching, and output lengths differ |

## Common full-document results

### OmniDocBench v1.0

Edit columns are lower-is-better; table TEDS is higher-is-better.[^paddleocr-vl-report]

| Model | Avg overall edit | Overall EN / ZH | Text edit EN / ZH | Formula edit EN / ZH | Table TEDS EN / ZH | Order edit EN / ZH |
|---|---:|---:|---:|---:|---:|---:|
| PP-StructureV3 | 0.176 | 0.145 / 0.206 | 0.058 / 0.088 | 0.295 / 0.535 | 77.2 / 83.9 | 0.069 / 0.091 |
| MinerU2.5 | 0.143 | 0.111 / 0.174 | 0.050 / 0.074 | 0.258 / 0.473 | 88.3 / 89.2 | 0.045 / 0.068 |
| PaddleOCR-VL | **0.115** | **0.105 / 0.126** | 0.041 / **0.062** | **0.241 / 0.316** | 88.0 / **92.1** | 0.045 / **0.063** |

### OmniDocBench v1.5 bilingual protocol

[^paddleocr-vl-report][^paddleocr-vl-1-5-report][^glm-ocr-report]

| Model | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| PP-StructureV3 | 86.73 | 0.073 | 85.79 | 81.68 | 89.48 | 0.073 |
| MinerU2.5 | 90.67 | 0.047 | 88.46 | 88.22 | 92.38 | 0.044 |
| PaddleOCR-VL | 92.86 | **0.035** | 91.22 | 90.89 | 94.76 | 0.043 |
| PaddleOCR-VL-1.5 | 94.50 | **0.035** | **94.21** | 92.76 | 95.79 | **0.042** |
| GLM-OCR | **94.62** | 0.040 | 93.90 | **93.96** | **96.39** | 0.044 |

FalconOCR uses an incompatible English-only subset: FalconOCR 88.64 overall, 0.055 text edit, 86.8 formula CDM, and 84.6 table TEDS; its source reports PaddleOCR-VL-1.5 at 94.37 on that subset.[^falcon-perception-report]

### OmniDocBench v1.6

The first table is reproduced by the PaddleOCR-VL-1.6 report; all values remain author- or leaderboard-reported.[^paddleocr-vl-1-6-report]

| Model | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| MinerU2.5 | 93.04 | 0.045 | 95.77 | 87.88 | 91.47 | 0.130 |
| PaddleOCR-VL | 94.18 | 0.040 | 95.91 | 90.65 | 93.74 | 0.135 |
| PaddleOCR-VL-1.5 | 94.93 | 0.038 | 96.89 | 91.67 | 94.37 | 0.130 |
| GLM-OCR | 95.22 | 0.044 | 97.18 | 92.83 | 95.39 | 0.133 |
| MinerU2.5-Pro | 95.75 | 0.036 | 97.45 | 93.42 | 95.92 | **0.120** |
| PaddleOCR-VL-1.6 | **96.33** | **0.033** | **97.49** | **94.76** | **97.11** | 0.127 |

MinerU's own cards instead report 92.98 for MinerU2.5, 95.69 for Pro-2604, and 95.72 for Pro-2605. The 2605 vector is text edit 0.036, formula CDM 97.15, table TEDS/TEDS-S 93.62/96.01, and order edit 0.123; the 2604 vector is 0.036, 97.29, 93.42/95.92, and 0.120. The bundle cannot reconcile these small differences.[^mineru2-5-pro-card][^mineru2-5-pro-2605-card]

### Real5-OmniDocBench

[^paddleocr-vl-1-6-report]

| Model | Overall ↑ | Scan | Warp | Screen photo | Illumination | Skew |
|---|---:|---:|---:|---:|---:|---:|
| PP-StructureV3 | 64.45 | 84.68 | 59.34 | 66.89 | 73.38 | 37.98 |
| PaddleOCR-VL | 85.54 | 92.11 | 85.97 | 82.54 | 89.61 | 77.47 |
| MinerU2.5 | 85.61 | 90.06 | 83.76 | 89.41 | 89.57 | 75.24 |
| MinerU2.5-Pro | 88.96 | 92.11 | 88.72 | 91.29 | 91.42 | 81.26 |
| GLM-OCR | 90.32 | 92.67 | 90.68 | 91.75 | 91.12 | 85.39 |
| PaddleOCR-VL-1.5 | 92.05 | 93.43 | 91.25 | 91.76 | 92.16 | 91.66 |
| PaddleOCR-VL-1.6 | **93.19** | **94.74** | **92.48** | **92.78** | **93.28** | **92.66** |

## Document-extraction and specialist results

### olmOCR-Bench

Under Paddle's full 1,402-PDF/7,010-check protocol, PaddleOCR-VL reports **80.0 ± 1.0** overall versus MinerU2.5 **77.5 ± 1.0**. Under Falcon's English-filtered protocol, FalconOCR reports **80.3**, PaddleOCR-VL-1.5 **79.3**, and PaddleOCR-VL **79.2**; these values must not be merged with Paddle's full protocol.[^paddleocr-vl-report][^falcon-perception-report]

Surya OCR 2 reports **83.3** over 8,413 tests after adjustments for HTML output. Its category pass rates are ArXiv 88.3, Base 99.7, headers/footers 92.5, tiny text 93.7, multi-column 82.4, old scans 41.8, old math 81.4, and tables 86.6.[^surya-ocr-2-card]

### Public element and KIE benchmarks

| Model | Dataset | Reported result |
|---|---|---:|
| GLM-OCR | OCRBench Text | 94.0 |
| GLM-OCR | UniMERNet | 96.5 |
| GLM-OCR | PubTabNet | 85.2 |
| GLM-OCR | TEDS_TEST | 86.0 |
| GLM-OCR | Nanonets-KIE | 93.7 |
| GLM-OCR | Handwritten-KIE | 86.1 |
| MinerU2.5 | OCRBench Text / UniMERNet / PubTabNet / TEDS_TEST | 75.3 / 96.4 / 88.4 / 85.4 |
| PaddleOCR-VL-1.5 | OCRBench Text / UniMERNet / PubTabNet / TEDS_TEST | 75.3 / 96.1 / 84.6 / 83.3 |

The GLM table does not fully specify metric implementations or model configurations; KIE uses GLM-OCR's separate full-page prompted path.[^glm-ocr-report]

### Cropped and private specialist sets

| Dataset | Model | Metrics and reported result |
|---|---|---|
| OmniDocBench-Table-block, 512 crops | PaddleOCR-VL | TEDS 0.9195; TEDS-S 0.9543; edit 0.0561 |
| OmniDocBench-Formula-block, 1,050 crops | PaddleOCR-VL | CDM overall/EN/ZH 0.9453/0.9677/0.9228 |
| Ocean-OCR-Handwritten, 400 EN/ZH | PaddleOCR-VL | Edit 0.118/0.034; F1 0.750/0.957; precision 0.748/0.959; recall 0.753/0.957; BLEU 0.551/0.856; METEOR 0.787/0.936 |
| Same three sets | MinerU2.5 | Table TEDS/TEDS-S/edit 0.9005/0.9539/0.0693; formula CDM 0.9187/0.9751/0.8623; handwriting edit 0.238/0.356 |
| Paddle private chart, 1,801 samples | PP-StructureV3 / PaddleOCR-VL / VL-1.5 / VL-1.6 | RMS-F1 80.60 / 84.40 / 80.37 / 91.74 |
| Paddle private text spotting | VL-1.5 / VL-1.6 | Average accuracy 86.21 / 87.47 |
| Paddle private seal, 300 images | VL-1.5 / VL-1.6 | NED 0.138 / 0.119 |
| Paddle hard table, 1,258 samples | VL-1.6 | TEDS 91.71; structural TEDS 94.67 |
| GLM six private scenarios | GLM-OCR | Code 84.7; table 91.5; handwriting 87.0; multilingual 69.3; seal 90.5; receipt KIE 94.5 |

PaddleOCR-VL also has nine page-type text-block NEDs, a 107,452-line private OCR suite, and private table/formula sets; their full vectors remain cataloged in [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md). The raw sources do not supply reproducible dataset manifests.[^paddleocr-vl-report][^paddleocr-vl-1-5-report][^paddleocr-vl-1-6-report][^glm-ocr-report]

## Boundary-case evaluations

### Nemotron OCR v2

OmniDocBench crop mode uses sample-average NED (lower is better) and one A100. This tests crop transcription rather than full layout reconstruction.[^nemotron-ocr-v2-card]

| Variant | pages/s ↑ | EN | ZH | Mixed | White | Single | Multi | Normal | Rotate90 | Rotate270 | Horizontal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Multilingual | 34.7 | 0.048 | 0.072 | 0.142 | 0.061 | 0.049 | 0.117 | 0.062 | 0.109 | 0.332 | 0.372 |
| English | 40.7 | 0.038 | 0.830 | 0.437 | 0.348 | 0.282 | 0.572 | 0.353 | 0.232 | 0.827 | 0.893 |

On generated SynthDoG, multilingual page-average NED is English 0.069, Japanese 0.046, Korean 0.047, Russian 0.043, Simplified Chinese 0.035, and Traditional Chinese 0.065.[^nemotron-ocr-v2-card]

### Surya OCR 2

Beyond olmOCR-Bench, Surya reports an internal **87.2%** pass rate across 91 languages; 38 languages reach at least 90% and 76 reach at least 80%. The retained card exposes 15 language scores, including English 92.3%, Vietnamese 73.2%, Chinese 82.5%, Japanese 86.2%, and Arabic 72.7%. This is vendor-internal rather than an independent multilingual benchmark.[^surya-ocr-2-card]

## Throughput and system metrics

These are deployment observations, not a controlled speed leaderboard.[^paddleocr-vl-report][^paddleocr-vl-1-5-report][^glm-ocr-report][^falcon-perception-report][^mineru2-5-card][^mineru2-5-pro-card][^surya-ocr-2-card][^nemotron-ocr-v2-card]

| Model | Reported setup | Result |
|---|---|---|
| PaddleOCR-VL | 981 pages, one A100, FastDeploy 2.3, batch 512 | 1.6184 pages/s; 2,486.4 tokens/s |
| PaddleOCR-VL-1.5 | 1,355 pages, one A100, FastDeploy 2.3, batch 512 | 1.4335 pages/s; 2,016.6 tokens/s |
| GLM-OCR | Single replica/concurrency; hardware incompletely matched | 0.67 image pages/s; 1.86 PDF pages/s |
| FalconOCR | Layout + OCR, A100-80GB; source statements conflict | 2.8–2.9 images/s; about 5,825–6,000 tokens/s, with another location saying about 3,000 |
| MinerU2.5 / Pro | One A100, asynchronous vLLM; workload unspecified | 2.12 fps |
| Surya OCR 2 | RTX 5090, vLLM, concurrency 128, 96 DPI | 5.35 pages/s; 12,884 tokens/s; p50/p95 18,915/42,538 ms |
| Surya OCR 2 | Apple Silicon, llama.cpp Metal, parallelism 8 | 0.108 pages/s; 254 tokens/s; about 30 W |
| Nemotron OCR v2 | One A100, crop mode | 34.7 pages/s multilingual; 40.7 English |

## Interpretation

- **Best retained common full-document result:** PaddleOCR-VL-1.6 leads the author-reproduced OmniDocBench v1.6 table overall and on text, formula, and table metrics; MinerU2.5-Pro has the lowest reading-order edit. This is not an independent rerun.
- **Robustness separates models more than clean-page scores:** on Real5, PP-StructureV3 falls to 64.45 while PaddleOCR-VL-1.6 reports 93.19, supporting distortion-aware localization within that protocol.
- **Boundary systems answer different questions:** Surya's main common result is PDF unit-test pass rate; Nemotron's is crop transcription NED and throughput. Neither can be inserted into the OmniDocBench v1.6 full-document table.
- **Latest gains are data-centric:** MinerU2.5-Pro and PaddleOCR-VL-1.6 attribute gains primarily to coverage, label refinement, and post-training rather than parameter scaling.
- **No global winner is supported:** benchmark versions, language filters, matching, prompts, output normalization, private data, and hardware differ.

## Trust limits

Every numeric result is author-, vendor-, or leaderboard-reported. The retained bundle lacks a common executable evaluation environment, evaluated outputs, complete prompts/configurations, benchmark snapshots, and uncertainty for most metrics. MinerU's remote figures and Surya's referenced image assets are absent locally; private Paddle, GLM, and Surya datasets cannot be audited. “All” in this page means all models and benchmark evidence retained in this repository under the operational hybrid definition, not all OCR systems published externally.

## Relationships

- **Specializes:** the production-hybrid recommendation in [Current OCR approaches](current-ocr-approaches.md).
- **Consolidates:** [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md) for the core family and selected boundary evidence from [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md) and [End-to-end generative OCR VLM benchmarks](end-to-end-generative-ocr-vlm-benchmarks.md).
- **Benchmarks:** [PP-StructureV3](pp-structurev3.md), [PaddleOCR-VL](paddleocr-vl.md), [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md), [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), [GLM-OCR](glm-ocr.md), [FalconOCR](falcon-ocr.md), [MinerU2.5](mineru2-5.md), [MinerU2.5-Pro](mineru2-5-pro.md), [Surya OCR 2](surya-ocr-2.md), and [Nemotron OCR v2](nemotron-ocr-v2.md).

[^paddleocr3-report]: Cui et al., *PaddleOCR 3.0 Technical Report*, local source at [main.tex](../raw/2507.05595_PaddleOCR-3.0/main.tex), including PP-StructureV3 benchmark figures (accessed 2026-08-17).
[^paddleocr-vl-report]: Cui et al., *PaddleOCR-VL*, local source at [main.tex](../raw/2510.14528_PaddleOCR-VL/main.tex), including page-, element-, private-benchmark, and throughput tables (accessed 2026-08-17).
[^paddleocr-vl-1-5-report]: Cui et al., *PaddleOCR-VL-1.5*, local source at [main.tex](../raw/2601.21957_PaddleOCR-VL-1.5/main.tex), including OmniDocBench, Real5, spotting, seal, and throughput tables (accessed 2026-08-17).
[^paddleocr-vl-1-6-report]: Zhang et al., *PaddleOCR-VL-1.6*, local source at [main.tex](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex), including OmniDocBench v1.6, Real5, hard-table, chart, spotting, seal, and ablation tables (accessed 2026-08-17).
[^glm-ocr-report]: Duan et al., *GLM-OCR Technical Report*, local source at [main.tex](../raw/2603.10910_GLM-OCR/main.tex) and its `tables/` result files (accessed 2026-08-17).
[^falcon-perception-report]: Falcon Vision Team, *Falcon Perception*, local source at [main.tex](../raw/2603.27365_FalconPerception/main.tex), especially `sections/ocr.tex` (accessed 2026-08-17).
[^mineru2-5-card]: OpenDataLab, local [MinerU2.5 model card](../raw/MinerU2.5-2509-1.2B.md); remote benchmark figures were unavailable locally (accessed 2026-08-17).
[^mineru2-5-pro-card]: OpenDataLab, local [MinerU2.5-Pro-2604 model card](../raw/MinerU2.5-Pro-2604-1.2B.md); remote benchmark figures were unavailable locally (accessed 2026-08-17).
[^mineru2-5-pro-2605-card]: OpenDataLab, local [MinerU2.5-Pro-2605 model card](../raw/MinerU2.5-Pro-2605-1.2B.md) (accessed 2026-08-17).
[^surya-ocr-2-card]: Datalab, local [Surya OCR 2 model card](../raw/surya-ocr-2.md); its 29 referenced image assets are absent locally (accessed 2026-08-17).
[^nemotron-ocr-v2-card]: NVIDIA, local [Nemotron OCR v2 model card](../raw/nemotron-ocr-v2.md), including OmniDocBench crop-mode and generated SynthDoG tables (accessed 2026-08-17).
