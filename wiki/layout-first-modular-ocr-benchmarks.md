---
type: Synthesis
title: Layout-first modular OCR benchmarks
description: Layout-first modular OCR benchmarks catalog retained models, datasets, metrics, author-reported results, protocol differences, and evidence limits for systems that localize document regions before specialized recognition.
tags: [ocr, document-parsing, layout-analysis, benchmarks, evaluation]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:59:12Z }
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
---

# Layout-first modular OCR benchmarks

The retained core layout-first modular family consists of [PP-StructureV3](pp-structurev3.md), [PaddleOCR-VL](paddleocr-vl.md), [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md), [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), [GLM-OCR](glm-ocr.md), [FalconOCR](falcon-ocr.md), [MinerU2.5](mineru2-5.md), and [MinerU2.5-Pro](mineru2-5-pro.md). Each localizes or classifies page regions before crop- or element-level recognition and reassembly. Across the closest common protocol retained here, the author-reported OmniDocBench v1.6 leaderboard places PaddleOCR-VL-1.6 at 96.33 overall, but version, language subset, evaluator, and reporting-source differences prevent this from establishing a universal ranking.[^paddleocr-vl-1-6-report]

## Scope and model coverage

| Model or release | Layout-first path | Parameters | Lifecycle or coverage |
|---|---|---:|---|
| [PP-StructureV3](pp-structurev3.md) | OCR + layout/article detection + specialist table/formula/chart/seal recognizers + reading-order postprocessing | Unresolved; report figure implies roughly 0.36B for the pipeline | Current retained modular pipeline |
| [PaddleOCR-VL](paddleocr-vl.md) | PP-DocLayoutV2 regions/order → one task-conditioned element VLM | 0.9B | Deprecated predecessor |
| [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) | PP-DocLayoutV3 polygonal regions/order → element VLM | 0.9B | Deprecated predecessor |
| [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) | Same two-stage architecture as 1.5; data and post-training changed | 0.9B | Current retained version |
| [GLM-OCR](glm-ocr.md) | PP-DocLayoutV3 regions/order → CogViT–GLM recognizer | 0.9B | Current retained model; full-page KIE is a separate non-layout-crop path |
| [FalconOCR](falcon-ocr.md) | PP-DocLayoutV3 regions/order → early-fusion text/formula/table recognizer | 0.3B | Current retained English-focused model |
| [MinerU2.5](mineru2-5.md) | Low-resolution global layout → native-resolution text/formula/table crops | 1.2B | Current retained baseline |
| [MinerU2.5-Pro](mineru2-5-pro.md) | MinerU2.5 two-step extraction with a data-centric update | 1.2B | 2604 and 2605 releases retained |

[Surya OCR 2](surya-ocr-2.md) is a boundary case rather than a core member: its optional block mode runs layout before region recognition, but its primary system is described as one shared VLM for full-page layout, order, OCR, and tables. [Nemotron OCR v2](nemotron-ocr-v2.md) is classified with detector–recognizer OCR, while [PP-DocLayoutV2](pp-doclayoutv2.md) and [PP-DocLayoutV3](pp-doclayoutv3.md) are layout components rather than full document parsers. End-to-end models with an optional generated layout trace, such as Qianfan-OCR, are also excluded.

## Benchmark and metric map

| Dataset or protocol | Scope | Metrics | Direction | Qualification |
|---|---|---|---|---|
| OmniDocBench v1.0 | 981 pages; EN/ZH page parsing | Overall, text, formula, table, reading-order edit distance; table TEDS | Edit lower; TEDS higher | Older evaluator; not numerically interchangeable with v1.5/v1.6 |
| OmniDocBench v1.5 | 1,355 pages; page parsing | Overall; text NED; formula CDM; table TEDS/TEDS-S; reading-order NED | Overall/CDM/TEDS higher; NED lower | Falcon uses English-only pages and a distinct result table |
| OmniDocBench v1.6 | v1.5 plus MGAM matching and a 296-page Hard subset | Same task metrics with adaptive matching | Same | Leaderboard values conflict slightly with MinerU release-card values |
| Real5-OmniDocBench | Physical reconstructions under scanning, warping, screen photography, illumination, and skew | Overall score and five condition scores | Higher | Derived from OmniDocBench v1.5 annotations; not comprehensive in-the-wild coverage |
| olmOCR-Bench | Machine-verifiable PDF extraction checks | Overall and eight category unit-test pass rates | Higher | Paddle's report evaluates the full retained protocol; Falcon drops non-English documents |
| OCRBench Text | Text recognition | Source table score | Higher | GLM report does not provide protocol details |
| UniMERNet | Formula recognition | Source table score | Higher | Metric naming is not explicit in the GLM comparison table |
| PubTabNet and TEDS_TEST | Table recognition | Source table score | Higher | GLM comparison table supplies values but incomplete configurations |
| Nanonets-KIE and Handwritten-KIE | Key information extraction | Source table score | Higher | GLM's KIE path is full-page prompting, not layout-first cropping |
| Cropped OmniDocBench blocks | Text, table, or formula recognition with layout held out | NED, TEDS/TEDS-S, CDM | NED lower; others higher | Measures recognizer quality, not full pipeline quality |
| Private Paddle sets | OCR, hard tables, formulas, charts, spotting, seals | NED, TEDS, CDM, RMS-F1, accuracy/F1 | Task-dependent | Samples and executable protocols are unavailable |
| GLM in-house scenarios | Code, tables, handwriting, multilingual text, seals, receipt KIE | Unnamed 0–100 task scores | Higher | Dataset sizes and exact metrics are not disclosed |

## OmniDocBench v1.0

The exact in-scope rows retained in the PaddleOCR-VL report are below. All edit-distance columns are lower-is-better; table TEDS is higher-is-better.[^paddleocr-vl-report]

| Model | Avg overall edit | Overall EN / ZH | Text edit EN / ZH | Formula edit EN / ZH | Table TEDS EN / ZH | Table edit EN / ZH | Order edit EN / ZH |
|---|---:|---:|---:|---:|---:|---:|---:|
| PP-StructureV3 | 0.176 | 0.145 / 0.206 | 0.058 / 0.088 | 0.295 / 0.535 | 77.2 / 83.9 | 0.159 / 0.109 | 0.069 / 0.091 |
| MinerU2.5 | 0.143 | 0.111 / 0.174 | 0.050 / 0.074 | 0.258 / 0.473 | 88.3 / 89.2 | 0.089 / 0.083 | 0.045 / 0.068 |
| PaddleOCR-VL | **0.115** | **0.105 / 0.126** | 0.041 / **0.062** | **0.241 / 0.316** | 88.0 / **92.1** | 0.093 / **0.062** | 0.045 / **0.063** |

## OmniDocBench v1.5

### Full bilingual protocol

These rows share the v1.5 metric schema and are printed in the Paddle or GLM reports. The sources say most comparison values come from the official leaderboard, but the bundle has no preserved leaderboard snapshot.[^paddleocr-vl-report][^paddleocr-vl-1-5-report][^glm-ocr-report]

| Model | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | Table TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| PP-StructureV3 | 86.73 | 0.073 | 85.79 | 81.68 | 89.48 | 0.073 |
| MinerU2.5 | 90.67 | 0.047 | 88.46 | 88.22 | 92.38 | 0.044 |
| PaddleOCR-VL | 92.86 | **0.035** | 91.22 | 90.89 | 94.76 | 0.043 |
| PaddleOCR-VL-1.5 | 94.50 | **0.035** | **94.21** | 92.76 | 95.79 | **0.042** |
| GLM-OCR | **94.62** | 0.040 | 93.90 | **93.96** | **96.39** | 0.044 |

### Falcon English-only protocol

FalconOCR explicitly removes Chinese pages. Its comparison rows differ from the bilingual table and must not be merged with it.[^falcon-perception-report]

| Model | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ |
|---|---:|---:|---:|---:|
| PaddleOCR-VL | 91.76 | **0.024** | 91.7 | 85.9 |
| PaddleOCR-VL-1.5 | **94.37** | 0.075 | **94.4** | **91.1** |
| FalconOCR | 88.64 | 0.055 | 86.8 | 84.6 |

## OmniDocBench v1.6

### Leaderboard table retained in PaddleOCR-VL-1.6

All rows below occur in one author-reproduced leaderboard table using MGAM. They are the closest available cross-model comparison, but remain unreproduced locally.[^paddleocr-vl-1-6-report]

| Model | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | Table TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| MinerU2.5 | 93.04 | 0.045 | 95.77 | 87.88 | 91.47 | 0.130 |
| PaddleOCR-VL | 94.18 | 0.040 | 95.91 | 90.65 | 93.74 | 0.135 |
| PaddleOCR-VL-1.5 | 94.93 | 0.038 | 96.89 | 91.67 | 94.37 | 0.130 |
| GLM-OCR | 95.22 | 0.044 | 97.18 | 92.83 | 95.39 | 0.133 |
| MinerU2.5-Pro | 95.75 | 0.036 | 97.45 | 93.42 | 95.92 | **0.120** |
| PaddleOCR-VL-1.6 | **96.33** | **0.033** | **97.49** | **94.76** | **97.11** | 0.127 |

### MinerU release-card values

The MinerU cards instead report 92.98 for the original baseline and 95.69 for Pro-2604. The 2605 card labels its table `v1.6_full` and reports 95.72. The source bundle cannot reconcile these small differences with the leaderboard row.[^mineru2-5-pro-card][^mineru2-5-pro-2605-card]

| Release | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | Table TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| MinerU2.5 baseline | 92.98 | — | — | — | — | — |
| MinerU2.5-Pro-2604 | 95.69 | 0.036 | **97.29** | 93.42 | 95.92 | **0.120** |
| MinerU2.5-Pro-2605 | **95.72** | 0.036 | 97.15 | **93.62** | **96.01** | 0.123 |

## Real5-OmniDocBench

One PaddleOCR-VL-1.6 table reports all retained in-scope rows below under the same five physical-distortion categories.[^paddleocr-vl-1-6-report]

| Model | Overall ↑ | Scan | Warp | Screen photo | Illumination | Skew |
|---|---:|---:|---:|---:|---:|---:|
| PP-StructureV3 | 64.45 | 84.68 | 59.34 | 66.89 | 73.38 | 37.98 |
| PaddleOCR-VL | 85.54 | 92.11 | 85.97 | 82.54 | 89.61 | 77.47 |
| MinerU2.5 | 85.61 | 90.06 | 83.76 | 89.41 | 89.57 | 75.24 |
| MinerU2.5-Pro | 88.96 | 92.11 | 88.72 | 91.29 | 91.42 | 81.26 |
| GLM-OCR | 90.32 | 92.67 | 90.68 | 91.75 | 91.12 | 85.39 |
| PaddleOCR-VL-1.5 | 92.05 | 93.43 | 91.25 | 91.76 | 92.16 | 91.66 |
| PaddleOCR-VL-1.6 | **93.19** | **94.74** | **92.48** | **92.78** | **93.28** | **92.66** |

## olmOCR-Bench

### Full retained Paddle protocol

Unit-test pass rate (%); the report describes 1,402 PDFs and 7,010 checks.[^paddleocr-vl-report]

| Model | Overall | ArXiv | Old math | Tables | Old scans | Header/footer | Multi-column | Tiny text | Base |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MinerU2.5 | 77.5 ± 1.0 | 81.1 | 74.0 | **85.1** | 33.8 | 96.3 | 65.5 | **89.8** | 94.4 |
| PaddleOCR-VL | **80.0 ± 1.0** | **85.7** | 71.0 | 84.1 | **37.8** | **97.0** | **79.9** | 85.7 | **98.5** |

### Falcon English-filtered protocol

The Falcon source drops non-English cases, so its values and its Paddle comparison values are a separate protocol.[^falcon-perception-report]

| Model | Average | ArXiv math | Base | Header/footer | Tiny text | Multi-column | Old scan | Old math | Tables |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PaddleOCR-VL | 79.2 | 85.4 | 98.6 | 96.9 | 80.8 | 82.5 | 38.8 | 66.4 | 83.9 |
| PaddleOCR-VL-1.5 | 79.3 | **85.4** | 98.8 | **96.9** | **80.8** | 82.6 | 39.2 | 66.4 | 84.1 |
| FalconOCR | **80.3** | 80.5 | **99.5** | 94.0 | 78.5 | **87.1** | **43.5** | **69.2** | **90.3** |

## Element-level and specialist benchmarks

These results evaluate recognizers or specialist tasks, not necessarily the end-to-end layout-first pipeline.

### PaddleOCR-VL public or derived sets

| Dataset | Size | Model | Metric and reported result |
|---|---:|---|---|
| OmniDocBench-OCR-block | 17,148 text crops | PaddleOCR-VL | Average NED by page type: PPT 0.049; academic 0.021; book 0.045; textbook 0.081; exam 0.115; magazine 0.020; newspaper 0.034; note 0.081; report 0.033 |
| Ocean-OCR-Handwritten | 400 EN/ZH samples | PaddleOCR-VL | EN/ZH: edit 0.118/0.034; F1 0.750/0.957; precision 0.748/0.959; recall 0.753/0.957; BLEU 0.551/0.856; METEOR 0.787/0.936 |
| OmniDocBench-Table-block | 512 table crops | PaddleOCR-VL | TEDS 0.9195; structural TEDS 0.9543; edit distance 0.0561 |
| OmniDocBench-Formula-block | 1,050 formula crops | PaddleOCR-VL | CDM overall/EN/ZH 0.9453/0.9677/0.9228 |

The same Paddle report evaluates MinerU2.5 on these recognizer-only sets: its nine OCR-block NED values are 0.195/0.089/0.111/0.234/0.194/0.147/0.056/0.142/0.094; Ocean handwriting EN/ZH edit is 0.238/0.356; table-block TEDS/TEDS-S/edit is 0.9005/0.9539/0.0693; and formula-block CDM overall/EN/ZH is 0.9187/0.9751/0.8623.[^paddleocr-vl-report]

### Private Paddle benchmarks

| Dataset | Model | Metrics and reported result |
|---|---|---|
| In-house OCR, 107,452 lines | PaddleOCR-VL | Table NED by script: Arabic .122, Korean .052, Tamil .043, Greek .135, Thai .081, Telugu .011, Devanagari .097, Cyrillic .109, Latin .013, Japanese .086; 13 text-type NEDs range from .001 rare characters to .198 ancient text |
| In-house Table, 20 categories | PaddleOCR-VL | TEDS .8699; structural TEDS .9066; reported edit-similarity columns .9066/.9339 |
| In-house Formula, 34,816 samples | PaddleOCR-VL | CDM overall/EN/ZH .9882/.9914/.9849 |
| In-house Chart, 1,801 samples | PP-StructureV3 | RMS-F1 overall/EN/ZH 80.60/79.63/81.09 |
| In-house Chart, 1,801 samples | PaddleOCR-VL | RMS-F1 84.40/82.22/85.49 |
| In-house Chart, 1,801 samples | PaddleOCR-VL-1.5 | RMS-F1 80.37/76.15/84.58, reported later by the 1.6 source |
| In-house Text Spotting, nine dimensions | PaddleOCR-VL-1.5 | Average accuracy 86.21; category values 85.23/84.22/77.13/89.52/91.63/86.69/86.89/89.93/84.61 |
| In-house Seal, 300 images | PaddleOCR-VL-1.5 | NED 0.138 |
| Hard Table, 1,258 samples | PaddleOCR-VL-1.6 | TEDS 91.71; structural TEDS 94.67 |
| In-house Chart, 1,801 samples | PaddleOCR-VL-1.6 | RMS-F1 overall/EN/ZH 91.74/90.11/93.37 |
| In-house Text Spotting, nine dimensions | PaddleOCR-VL-1.6 | Average accuracy 87.47; category values 85.98/90.59/77.28/85.90/92.60/91.26/86.51/92.32/84.76 |
| In-house Seal, 300 images | PaddleOCR-VL-1.6 | NED 0.119 |

The nine spotting-category values are ordered as Ancient, Blur, Common, handwritten Chinese, handwritten English, printed Chinese, printed English, Table, and Japanese.[^paddleocr-vl-report][^paddleocr-vl-1-5-report][^paddleocr-vl-1-6-report]

### GLM-OCR public and private suites

The GLM report gives the following public rows; metric implementations are not fully specified in the retained bundle.[^glm-ocr-report]

| Dataset | Result |
|---|---:|
| OCRBench Text | 94.0 |
| UniMERNet | 96.5 |
| PubTabNet | 85.2 |
| TEDS_TEST | 86.0 |
| Nanonets-KIE | 93.7 |
| Handwritten-KIE | 86.1 |

Its private suite reports: Code Document 84.7, Real-world Table 91.5, Handwritten Text 87.0, Multilingual Text 69.3, Seal Recognition 90.5, and Receipt KIE 94.5. Dataset sizes, formulas, and uncertainty are absent; Receipt KIE uses GLM-OCR's separate full-page KIE path.[^glm-ocr-report]

### MinerU2.5-Pro claims without retained numeric tables

The 2604 card says Pro was evaluated across five unnamed table benchmarks, leading the next model by 1.39 points and original MinerU by 3.06 points; it also reports Dense Formula CDM 97.29 and text edit distance 0.036. The referenced performance plots are remote and not retained, so the five table-dataset names and complete score vectors cannot be recovered from the local evidence.[^mineru2-5-pro-card]

## Throughput and system metrics

These measurements use different datasets, servers, backends, batching, and concurrency and are not a controlled speed ranking.

| Model | Reported setup | Result |
|---|---|---|
| PaddleOCR-VL | 981 OmniDocBench v1.0 pages, one A100, FastDeploy 2.3, batch 512 | 1.6184 pages/s; 2,486.4 output tokens/s |
| PaddleOCR-VL-1.5 | 1,355 OmniDocBench v1.5 pages, one A100, FastDeploy 2.3, batch 512 | 1.4335 pages/s; 2,016.6 tokens/s |
| FalconOCR | Layout + OCR, one A100-80GB; source conditions conflict | 2.8–2.9 images/s and 5,825–about 6,000 tokens/s; another report location says about 3,000 tokens/s |
| MinerU2.5 / Pro | One A100, concurrent asynchronous vLLM; workload unspecified | 2.12 fps |
| GLM-OCR | Single replica and concurrency; hardware/configuration not fully matched | 0.67 image pages/s; 1.86 PDF pages/s |

[^paddleocr-vl-report][^paddleocr-vl-1-5-report][^falcon-perception-report][^mineru2-5-card][^mineru2-5-pro-card][^glm-ocr-report]

## Interpretation

- **Closest retained common comparison:** on the single OmniDocBench v1.6 leaderboard table, PaddleOCR-VL-1.6 has the highest overall, text, formula, and table results; MinerU2.5-Pro has the best reading-order edit distance. This is author-reproduced leaderboard evidence, not a local rerun.[^paddleocr-vl-1-6-report]
- **Robustness differs more than clean-page scores:** Real5 exposes a large PP-StructureV3 drop, while PaddleOCR-VL-1.5/1.6 retain scores above 92; this supports distortion-aware layout localization as consequential within that protocol, not as proof of universal robustness.[^paddleocr-vl-1-6-report]
- **Layout errors remain coupled to recognition:** cropped-block benchmarks can be much stronger than page-level results because they remove missed regions, category errors, and reading-order mistakes.
- **Data improvements dominate the latest retained gains:** MinerU2.5-Pro and PaddleOCR-VL-1.6 attribute improvement primarily to data coverage, label correction, and staged post-training rather than larger architectures.[^mineru2-5-pro-card][^paddleocr-vl-1-6-report]
- **No global winner is supported:** benchmark versions, language filters, matching rules, prompts, rendering, postprocessing, and private datasets differ. Even nominally identical OmniDocBench releases produce conflicting values across retained reports and cards.

## Trust limits

Every numeric result is author- or vendor-reported. The local bundle does not contain a complete reproducible evaluation package, evaluated outputs, training corpora, uncertainty for most metrics, or a preserved official leaderboard snapshot. Private Paddle and GLM suites cannot be audited; MinerU's remote benchmark images are absent; Falcon's throughput statements conflict; and PP-StructureV3's total parameter count is unresolved. PaddleOCR-VL's in-house OCR prose also states Telugu/Japanese NED as 0.114/0.096 while its table prints 0.011/0.086; the table values are transcribed above without resolving the conflict. This page records exact printed values where available and marks missing score vectors rather than inferring them.[^paddleocr3-report][^paddleocr-vl-report][^paddleocr-vl-1-5-report][^paddleocr-vl-1-6-report][^glm-ocr-report][^falcon-perception-report][^mineru2-5-card][^mineru2-5-pro-card][^mineru2-5-pro-2605-card]

## Relationships

- **Benchmarks:** [PP-StructureV3](pp-structurev3.md), [PaddleOCR-VL](paddleocr-vl.md), [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md), [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), [GLM-OCR](glm-ocr.md), [FalconOCR](falcon-ocr.md), [MinerU2.5](mineru2-5.md), and [MinerU2.5-Pro](mineru2-5-pro.md).
- **Refines:** the modular layout-first family and evaluation limits in [Current OCR approaches](current-ocr-approaches.md).
- **Complements:** [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md), which covers plain text detection and recognition rather than document reconstruction.

[^paddleocr3-report]: Cui et al., *PaddleOCR 3.0 Technical Report*, local source at [main.tex](../raw/2507.05595_PaddleOCR-3.0/main.tex), including its PP-StructureV3 OmniDocBench figure (accessed 2026-08-17).
[^paddleocr-vl-report]: Cui et al., *PaddleOCR-VL*, local source at [main.tex](../raw/2510.14528_PaddleOCR-VL/main.tex), including page-, element-, private-benchmark, and throughput tables (accessed 2026-08-17).
[^paddleocr-vl-1-5-report]: Cui et al., *PaddleOCR-VL-1.5*, local source at [main.tex](../raw/2601.21957_PaddleOCR-VL-1.5/main.tex), including OmniDocBench, Real5, spotting, seal, and throughput tables (accessed 2026-08-17).
[^paddleocr-vl-1-6-report]: Zhang et al., *PaddleOCR-VL-1.6*, local source at [main.tex](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex), including OmniDocBench v1.6, Real5, hard-table, chart, spotting, seal, and ablation tables (accessed 2026-08-17).
[^glm-ocr-report]: Duan et al., *GLM-OCR Technical Report*, local source at [main.tex](../raw/2603.10910_GLM-OCR/main.tex) and its `tables/` result files (accessed 2026-08-17).
[^falcon-perception-report]: Falcon Vision Team, *Falcon Perception*, local source at [main.tex](../raw/2603.27365_FalconPerception/main.tex), especially `sections/ocr.tex` (accessed 2026-08-17).
[^mineru2-5-card]: OpenDataLab, local [MinerU2.5 model card](../raw/MinerU2.5-2509-1.2B.md); remote benchmark figures were unavailable locally (accessed 2026-08-17).
[^mineru2-5-pro-card]: OpenDataLab, local [MinerU2.5-Pro-2604 model card](../raw/MinerU2.5-Pro-2604-1.2B.md); remote benchmark figures were unavailable locally (accessed 2026-08-17).
[^mineru2-5-pro-2605-card]: OpenDataLab, local [MinerU2.5-Pro-2605 model card](../raw/MinerU2.5-Pro-2605-1.2B.md) (accessed 2026-08-17).
