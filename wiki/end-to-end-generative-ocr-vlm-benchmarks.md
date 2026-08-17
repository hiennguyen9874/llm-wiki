---
type: Synthesis
title: End-to-end generative OCR VLM benchmarks
description: End-to-end generative OCR VLM benchmarks catalog retained models, datasets, metrics, author-reported results, protocol conflicts, and evidence gaps for systems that generate ordered document representations directly from page images.
tags: [ocr, document-parsing, vision-language-models, benchmarks, evaluation, generative-models]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T22:05:24+07:00 }
sources:
  - id: deepseek-ocr-report
    resource: ../raw/2510.18234_DeepSeek-OCR/main.tex
    title: DeepSeek-OCR Technical Report
  - id: deepseek-ocr-2-report
    resource: ../raw/2601.20552_DeepSeek-OCR-2/main.tex
    title: DeepSeek-OCR 2 Technical Report
  - id: infinity-parser-report
    resource: ../raw/2506.03197_InfinityParser/main.tex
    title: Infinity-Parser Technical Report
  - id: lightonocr-report
    resource: ../raw/2601.14251_LightOnOCR/templateArxiv.tex
    title: LightOnOCR Technical Report
  - id: typhoonocr-report
    resource: ../raw/2601.14722_TyphoonOCR/main.tex
    title: Typhoon OCR Technical Report
  - id: firered-ocr-report
    resource: ../raw/2603.01840_FireRed-OCR/fireredocr_report.tex
    title: FireRed-OCR Technical Report
  - id: qianfan-ocr-report
    resource: ../raw/2603.13398_Qianfan-OCR/qianfan_ocr_report.tex
    title: Qianfan-OCR Technical Report
  - id: unlimited-ocr-report
    resource: ../raw/2606.23050_Unlimited-OCR/main.tex
    title: Unlimited OCR Works
  - id: infinity-parser2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    title: Infinity-Parser2 Technical Report
  - id: ovisocr2-report
    resource: ../raw/2607.13639_OvisOCR2/main.tex
    title: OvisOCR2 Technical Report
  - id: chandra-card
    resource: ../raw/chandra.md
    title: Chandra model card
  - id: chandra-ocr-2-card
    resource: ../raw/chandra-ocr-2.md
    title: Chandra OCR 2 model card
  - id: dots-ocr-card
    resource: ../raw/dots.ocr.md
    title: dots.ocr model card
  - id: granite-docling-card
    resource: ../raw/granite-docling-258m.md
    title: Granite Docling 258M model card
  - id: hunyuanocr-card
    resource: ../raw/HunyuanOCR-1.5.md
    title: HunyuanOCR-1.5 model card
  - id: mineru-diffusion-card
    resource: ../raw/MinerU-Diffusion-V1-0320-2.5B.md
    title: MinerU-Diffusion model card
  - id: nanonets-ocr2-card
    resource: ../raw/Nanonets-OCR2.md
    title: Nanonets-OCR2 model card
  - id: nemotron-parse-card
    resource: ../raw/NVIDIA-Nemotron-Parse-v1.1.md
    title: NVIDIA Nemotron Parse v1.1 model card
  - id: olmocr2-card
    resource: ../raw/olmOCR-2-7B-1025.md
    title: olmOCR-2-7B-1025 model card
  - id: rolmocr-card
    resource: ../raw/RolmOCR.md
    title: RolmOCR model card
  - id: surya-ocr-2-card
    resource: ../raw/surya-ocr-2.md
    title: Surya OCR 2 model card
---

# End-to-end generative OCR VLM benchmarks

The retained core family comprises models that consume a page image and directly generate ordered text or a structured representation without requiring a separate layout detector at inference: [Chandra OCR](chandra-ocr.md), [Chandra OCR 2](chandra-ocr-2.md), [DeepSeek-OCR](deepseek-ocr.md), [DeepSeek-OCR 2](deepseek-ocr-2.md), [dots.ocr](dots-ocr.md), [FireRed-OCR](firered-ocr.md), [HunyuanOCR-1.5](hunyuanocr-1.5.md), [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md), [Infinity-Parser2](infinity-parser2.md), [LightOnOCR](lightonocr.md), [Nanonets-OCR2](nanonets-ocr2.md), [olmOCR-2-7B-1025](olmocr-2-7b-1025.md), [OvisOCR2](ovisocr2.md), [Qianfan-OCR](qianfan-ocr.md), [RolmOCR](rolmocr.md), [Typhoon OCR](typhoon-ocr.md), and [Unlimited OCR](unlimited-ocr.md). The closest retained common comparison is OmniDocBench v1.6 as transcribed by OvisOCR2: OvisOCR2 reports 96.58 overall, but all values are first-party or transcribed leaderboard results and do not establish a universal ranking.[^ovisocr2-report]

## Scope and model coverage

| Model or release | Direct output path | Size | Coverage decision |
|---|---|---:|---|
| [Chandra OCR](chandra-ocr.md) / [Chandra OCR 2](chandra-ocr-2.md) | Page/PDF → Markdown, HTML, or layout-bearing JSON | 9B / 5.3B only in comparison tables | Core; Chandra 1 is deprecated predecessor |
| [DeepSeek-OCR](deepseek-ocr.md) / [DeepSeek-OCR 2](deepseek-ocr-2.md) | Compressed page tokens → text or structured output | 3B MoE, about 0.5B active | Core; versioned family |
| [dots.ocr](dots-ocr.md) | Prompted page → ordered layout JSON or text-only output | Source identity conflicts between 1.7B LLM foundation and 3B comparison label | Core |
| [FireRed-OCR](firered-ocr.md) | Page → Markdown | 2B | Core |
| [HunyuanOCR-1.5](hunyuanocr-1.5.md) | Prompted page → Markdown or task-specific structure | Unspecified locally; comparison tables call the family 1B | Core, but its own retained card has no scores |
| [Infinity-Parser](layout-rl-and-infinity-parser.md) | Page → Markdown | 7B | Core predecessor |
| [Infinity-Parser2](infinity-parser2.md) | Page + task → JSON, Markdown, HTML, LaTeX, SMILES, or answers | Flash 2B; Pro 35B-A3B | Core current family |
| [LightOnOCR](lightonocr.md) | Page → ordered Markdown-like text; optional image boxes | 1B | Core; multiple checkpoints and a modified olmOCR protocol |
| [Nanonets-OCR2](nanonets-ocr2.md) | Page → Markdown/HTML/LaTeX/Mermaid and VQA | Plus, 3B, experimental 1.5B | Core |
| [olmOCR-2-7B-1025](olmocr-2-7b-1025.md) | Rendered page plus PDF-derived metadata → YAML/text | 7B | Core; uses metadata anchoring rather than image-only input |
| [OvisOCR2](ovisocr2.md) | Page → ordered Markdown | 0.8B | Core |
| [Qianfan-OCR](qianfan-ocr.md) | Page + prompt → final output, optionally preceded by layout reasoning | 4B | Core |
| [RolmOCR](rolmocr.md) | Image-only page → natural-reading text | 7B | Core; no retained numeric benchmark |
| [Typhoon OCR](typhoon-ocr.md) | Page → Markdown, HTML tables, LaTeX, figure descriptions, page markers | V1 3B/7B; V1.5 2B | Core multilingual/domain family |
| [Unlimited OCR](unlimited-ocr.md) | One or multiple pages → continuous structured OCR output | 3B MoE, 0.5B active | Core long-horizon variant |

Three retained systems are boundary cases and are not merged into the core leaderboard: [Granite Docling 258M](granite-docling-258m.md) directly generates DocTags but is positioned as a Docling component; [NVIDIA Nemotron Parse v1.1](nemotron-parse-v1-1.md) is a direct vision-encoder–decoder parser but its card contains no results; [Surya OCR 2](surya-ocr-2.md) performs full-page generation with a shared VLM but also has a separate line detector and optional layout-first block mode. [MinerU-Diffusion](mineru-diffusion.md) directly decodes page text, but its retained card does not establish ordered structured-document output, so it is cataloged only as an adjacent generative decoder. [Multimodal OCR](multimodal-ocr.md) is kept under the separate unified-multimodal-reconstruction family defined by [Current OCR approaches](current-ocr-approaches.md).

Comparison tables additionally name end-to-end systems without standalone retained sources: OCRFlux, Mistral OCR, POINTS-Reader, MinerU2-VLM, Nanonets-OCR-S, OCRVerse, OpenDoc/UniRec, ABot-OCR, Logics-Parsing-v2, FD-RL, HunyuanOCR 1.0, GOT-OCR, Nougat, SmolDocling, and general VLMs such as GPT, Gemini, InternVL, Qwen-VL, Kimi, and Ovis2.6. Their scores below are retained only when needed to define the protocol; this page does not promote them to locally verified model concepts.

## Benchmark and metric map

| Dataset or protocol | Scope | Metrics | Direction | Qualification |
|---|---|---|---|---|
| OmniDocBench v1.0 | EN/ZH full-page parsing | Overall/text/formula/table/order edit; table TEDS | Edit lower; TEDS higher | Older 981-page protocol; not interchangeable with v1.5/v1.6 |
| OmniDocBench v1.5 | 1,355 bilingual pages | Overall; text NED; formula CDM; table TEDS/TEDS-S; reading-order NED | Overall/CDM/TEDS higher; NED lower | Different reports give conflicting values for nominally identical models |
| OmniDocBench v1.6 | 1,651 pages including a hard subset | Same component schema with refined matching | Same | Closest current common table; values are transcribed, not locally rerun |
| PureDocBench | 1,475 source-traceable pages rendered into Clean, Digital, and Real tracks; 4,425 images | Per-track overall and Avg3 | Higher | OvisOCR2 report is the only retained source for the table |
| olmOCR-Bench | About 1,400 PDF pages and over 7,000 unit tests | Overall pass rate and eight category pass rates | Higher | Anchoring, omitted categories, toolkit versions, output normalization, and retries differ |
| ParseBench | About 2,000 enterprise pages | Overall across structure, faithfulness, semantic formatting, and grounding | Higher | Infinity-Parser2's internal pipeline mixes own reruns and cited results |
| FireRedBench | Distorted and non-standard layouts | OmniDoc-style overall and component metrics | Task-dependent | Private and unreproducible |
| dots.ocr-bench | 1,493 PDF images, 100 languages | Overall/text/formula/order edit; table TEDS and edit | Edit lower; TEDS higher | Private multilingual set |
| Typhoon internal Thai suite | Six Thai document categories | BLEU, ROUGE-L, Levenshtein distance | BLEU/ROUGE higher; distance lower | Sizes and test artifacts unavailable |
| Layout datasets | DocLayNet, D4LA, OmniDocBench layout subset | mIoU under five-category remapping | Higher | Infinity-Parser2 protocol differs from original mAP evaluations |
| Element datasets | OmniDoc text blocks, PubTabNet, FinTabNet, UniMERNet | EDS, TEDS, CDM | Higher | Crop-level tasks do not measure full-page layout/order errors |
| Charts and chemistry | ChartQA, ChartX-SE, ChartMimic, CoSyn-Chemical, ChemDraw-Bench | RMS-F1, AP, execution/similarity, InChI, Tanimoto, valid-SMILES | Higher | Several are internal reruns or private sets |
| OCR/understanding/KIE | OCRBench/v2, CCOCR, DocVQA, InfoVQA, TextVQA, CharXiv, ChartQA/Pro, ChartBench, Nanonets KIE | Benchmark-specific scores, ANLS, F1 | Higher | Metric scales differ and must not be merged |
| Model-specific robustness | Fox compression, LightOn bbox, Chandra/Surya multilingual, Unlimited multi-page | Precision; F1/IoU/count; pass rate; edit and Distinct-n | Task-dependent | Usually author-constructed or modified protocols |

## OmniDocBench v1.5

The following retained end-to-end values use the v1.5 overall schema. Rows come from different first-party reports; conflicts are preserved rather than averaged.[^deepseek-ocr-2-report][^firered-ocr-report][^qianfan-ocr-report][^unlimited-ocr-report]

| Reporting source / model | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| FireRed table: DeepSeek-OCR | 87.36 | 0.073 | 84.14 | 85.25 | 89.01 | 0.085 |
| FireRed table: dots.ocr | 88.41 | 0.048 | 83.22 | 86.78 | 90.62 | 0.053 |
| FireRed/DeepSeek/Qianfan table: DeepSeek-OCR 2 | 91.09 | 0.048 | 90.31 | 87.75 | 92.06 | 0.057 |
| FireRed-OCR | 92.94 | **0.032** | 91.71 | 90.31 | 93.81 | **0.041** |
| Qianfan-OCR | 93.12 | 0.041 | **92.43** | **91.02** | 93.85 | 0.049 |
| Qianfan-OCR with Layout-as-Thought | 92.64 | 0.052 | 91.92 | 91.21 | **94.03** | 0.051 |
| Unlimited table: DeepSeek-OCR 2 | 89.17 | 0.049 | 86.85 | 85.60 | 90.06 | 0.060 |
| Unlimited-OCR | **93.23** | 0.038 | 92.61 | 90.93 | **94.07** | 0.045 |

The 1.6-style overall score must not be confused with the older EN/ZH edit-distance aggregate. Under the older OmniDocBench protocol, Infinity-Parser-7B reports EN/ZH overall edit **0.141/0.197**, text edit 0.076/0.117, formula edit 0.314/0.434, table TEDS 85.3/81.4, table edit 0.098/0.142, and order edit 0.076/0.095.[^infinity-parser-report] DeepSeek-OCR also reports mode-dependent EN/ZH overall edit: Tiny 0.386/0.361, Base 0.137/0.240, Gundam 0.127/0.181, and Gundam-M 0.123/0.157.[^deepseek-ocr-report]

## OmniDocBench v1.6

One OvisOCR2 table supplies the closest retained common comparison below. OvisOCR2 says leaderboard rows come from OpenDataLab and several technical reports; model versions and evaluator configurations remain incompletely matched.[^ovisocr2-report]

| End-to-end model | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| Nanonets-OCR-S | 83.61 | 0.108 | 81.46 | 80.18 | 84.51 | 0.213 |
| olmOCR | 85.74 | 0.139 | 88.10 | 83.00 | 87.17 | 0.216 |
| HunyuanOCR | 89.95 | 0.088 | 87.68 | 91.01 | 93.23 | 0.171 |
| DeepSeek-OCR 2 | 90.25 | 0.050 | 91.84 | 83.89 | 87.75 | 0.144 |
| dots.ocr | 90.77 | 0.048 | 89.95 | 87.18 | 90.58 | 0.138 |
| FireRed-OCR | 93.26 | 0.037 | 95.44 | 88.04 | 91.06 | 0.131 |
| Qianfan-OCR | 93.90 | 0.040 | 95.08 | 90.53 | 93.31 | 0.130 |
| Unlimited-OCR | 93.92 | 0.042 | 95.79 | 90.16 | 93.32 | 0.129 |
| HunyuanOCR-1.5 | 94.74 | 0.039 | 94.50 | 93.67 | 94.71 | 0.129 |
| **OvisOCR2** | **96.58** | **0.025** | **97.53** | **94.76** | **97.16** | **0.111** |

Infinity-Parser2 uses a separate table/protocol and reports Flash **91.98** and Pro **93.95** overall; its table reports DeepSeek-OCR 2 at 90.17 and dots.ocr at 90.50, illustrating cross-source drift even within the v1.6 name.[^infinity-parser2-report]

## PureDocBench

PureDocBench distinguishes clean source renders, digital degradation, and physical/screen-mediated recapture. The following rows are the retained end-to-end models in OvisOCR2's table.[^ovisocr2-report]

| Model | Clean ↑ | Digital ↑ | Real ↑ | Avg3 ↑ |
|---|---:|---:|---:|---:|
| DeepSeek-OCR | 53.50 | 46.95 | 40.48 | 46.98 |
| DeepSeek-OCR 2 | 55.53 | 49.41 | 43.60 | 49.51 |
| Qianfan-OCR | 57.22 | 50.85 | 45.06 | 51.04 |
| olmOCR | 62.56 | 57.84 | 47.30 | 55.90 |
| Nanonets-OCR2 | 64.83 | 61.23 | 49.03 | 58.36 |
| olmOCR-2-7B | 69.36 | 65.87 | 56.10 | 63.78 |
| dots.ocr | 72.01 | 65.95 | 55.68 | 64.55 |
| FireRed-OCR | 70.81 | 68.49 | 57.42 | 65.57 |
| OCRVerse | 73.18 | 71.36 | 63.66 | 69.40 |
| Logics-Parsing-v2 | 76.35 | 73.85 | **67.64** | 72.61 |
| FD-RL | 78.38 | 76.33 | 67.04 | 73.92 |
| **OvisOCR2** | **81.55** | **77.09** | 66.56 | **75.06** |

## olmOCR-Bench

These overall pass rates are intentionally separated by reporting source. Exact subcategory vectors are available for Chandra, olmOCR-2, Surya, Qianfan, and Infinity-Parser; LightOnOCR excludes headers/footers from its aggregate.[^chandra-card][^chandra-ocr-2-card][^dots-ocr-card][^infinity-parser-report][^infinity-parser2-report][^lightonocr-report][^olmocr2-card][^qianfan-ocr-report][^surya-ocr-2-card]

| Model / protocol | Overall ↑ | Important qualification |
|---|---:|---|
| DeepSeek-OCR, Chandra's own run | 75.4 ± 1.0 | Qianfan reports 77.2 under another environment |
| dots.ocr original | 79.1 ± 1.0 | Category vector: 82.1/64.2/88.3/40.9/94.1/82.4/81.2/99.5 |
| Qianfan-OCR | 79.8 | Category vector: 80.1/73.1/81.6/42.0/92.2/80.4/89.1/99.6 |
| olmOCR-2 BF16 / FP8 | 82.3 ± 1.1 / 82.4 ± 1.1 | Toolkit v0.4.0 with rendering, rotation, and retry behavior |
| Infinity-Parser-7B | 82.5 ± 1.0 | Category vector: 84.4/83.8/85.0/47.9/88.7/84.2/86.4/99.8 |
| Chandra OCR | 83.1 ± 0.9 | Vendor's own run |
| LightOnOCR-2-1B | 83.2 ± 0.9 | Excludes headers/footers; not directly comparable |
| Surya OCR 2 | 83.3 | `default` preset, 8,413 tests; adjusts for HTML output |
| dots.ocr 1.5 / dots.mocr | 83.9 | Version naming differs across cards/reports |
| Chandra OCR 2 | 85.8 ± 0.8 | Infinity-Parser2 instead transcribes 83.1 ± 0.9 |
| Infinity-Parser2-Flash | 86.0 ± 0.8 | Author evaluation pipeline |
| **Infinity-Parser2-Pro** | **87.6 ± 0.8** | Author evaluation pipeline |

## Model-specific and task-specific evaluations

| Model | Dataset or protocol | Metrics and author-reported result |
|---|---|---|
| DeepSeek-OCR | 100-page English Fox subset | Precision falls with compression: Small reports 96.8% around 8.5–9.7× and 87.1% at 12.6×; Tiny reports 59.1% at 19.7×.[^deepseek-ocr-report] |
| DeepSeek-OCR 2 | Element edit table and production logs | Overall element edit 0.100 vs. DeepSeek-OCR 0.129; repetition 4.17% vs. 6.25% on online images and 2.88% vs. 3.69% on PDF data.[^deepseek-ocr-2-report] |
| dots.ocr | dots.ocr-bench | Overall/text/formula/order edit 0.177/0.075/0.297/0.152; table TEDS 79.2; table edit 0.186.[^dots-ocr-card] |
| FireRed-OCR | FireRedBench | Overall 74.62; text edit 0.248; formula CDM 83.02; table TEDS/TEDS-S 65.63/72.30; order edit 0.430.[^firered-ocr-report] |
| FireRed-OCR | OCRBench Text, TEDS_TEST, PubTabNet | 93.5, 80.6, and 77.0 respectively.[^firered-ocr-report] |
| Infinity-Parser2-Pro | ParseBench | 74.3 overall; Flash 72.2.[^infinity-parser2-report] |
| Infinity-Parser2 Pro / Flash | Layout mIoU: DocLayNet / OmniDocBench v1.5 / D4LA | Pro 64.93/74.56/52.41; Flash 64.97/73.07/46.05.[^infinity-parser2-report] |
| Infinity-Parser2 Pro / Flash | Omni text EDS; PubTabNet/FinTabNet TEDS; UniMER formula CDM avg. | Pro 95.05; 94.76/98.88; 97.7. Flash 94.31; 92.41/98.51; 96.5.[^infinity-parser2-report] |
| Infinity-Parser2 Pro / Flash | ChartQA RMS-F1; ChartX-SE AP strict/slight/high; ChartMimic exec/low/high | Pro 86.5; 61.7/68.9/73.7; 87.1/70.1/79.6. Flash 80.5; 53.4/62.0/67.7; 62.1/45.2/60.3.[^infinity-parser2-report] |
| Infinity-Parser2 Pro / Flash | CoSyn-Chemical InChI/Tanimoto/valid; ChemDraw-Bench same | Pro 53.91/73.19/86.72 and 49.95/72.35/77.28; Flash 39.06/63.34/83.59 and 34.30/66.21/74.69.[^infinity-parser2-report] |
| Infinity-Parser2-Pro | DocVQA / InfoVQA ANLS; OCRBench | 96.43 / 86.26; OCRBench 86.2.[^infinity-parser2-report] |
| LightOnOCR bbox | 290 olmOCR-derived + 565 arXiv pages | F1@0.5 0.78/0.83; mean IoU 0.70/0.77; exact-count accuracy 83.8/85.0.[^lightonocr-report] |
| Nanonets-OCR2 Plus / 3B | ChartQA and DocVQA | ChartQA 79.20/78.56; DocVQA 85.15/89.43. The card gives no evaluator configuration.[^nanonets-ocr2-card] |
| Nanonets-OCR2 3B | Pairwise Markdown comparison | Against Gemini 2.5 Flash: table labeled win 39.98%, lose 52.43%, both correct 7.58%; dataset and judge are undefined.[^nanonets-ocr2-card] |
| OvisOCR2 | In-house >1,000 pages | Overall 85.54; handwriting 72.28; complex-table overall 83.97 and table-missing rate 0.0796.[^ovisocr2-report] |
| Qianfan-OCR | General OCR | OCRBench 880; OCRBenchv2 EN/ZH 56.0/60.77; CCOCR multilingual/overall 76.7/79.3.[^qianfan-ocr-report] |
| Qianfan-OCR | Understanding | OCRVQA 66.8; TextVQA 80.0; DocVQA 92.8; CharXiv DQ/RQ 94.0/85.2; ChartQA/Pro 88.1/42.9; ChartBench 85.9.[^qianfan-ocr-report] |
| Qianfan-OCR | Five KIE benchmarks | Mean 87.9; OCRBench KIE 95.0; OCRBenchv2 EN/ZH 82.8/82.3; CCOCR KIE 92.8; Nanonets KIE F1 86.5.[^qianfan-ocr-report] |
| Typhoon OCR V1.5 2B | Six-category Thai internal suite | Average BLEU 0.644, ROUGE-L 0.774, Levenshtein 0.251; V1 7B reports 0.558/0.686/0.332.[^typhoonocr-report] |
| Unlimited OCR | Multi-page in-house set | For 2/5/10/15/20/40+ pages, edit 0.0362/0.0452/0.0526/0.0787/0.0572/0.1069; Distinct-35 99.87/99.98/99.83/99.99/99.89/96.90%.[^unlimited-ocr-report] |

## Boundary-case evaluations

- **Granite Docling 258M:** layout mAP/F1/precision/recall 0.27/0.86/0.92/0.88; full-page OCR edit/F1/precision/recall/BLEU/METEOR 0.45/0.84/0.91/0.83/0.65/0.72; code recognition 0.013/0.988/0.990/0.988/0.983/0.986; equation recognition 0.073/0.968/0.968/0.969/0.893/0.927; FinTabNet structural/content TEDS 0.97/0.96; MMStar 0.30; OCRBench 500.[^granite-docling-card]
- **Surya OCR 2:** olmOCR-Bench 83.3; category pass rates ArXiv/Base/header-footer/tiny-text/multi-column/old-scan/old-math/tables are 88.3/99.7/92.5/93.7/82.4/41.8/81.4/86.6; internal 91-language overall pass rate is 87.2%.[^surya-ocr-2-card]
- **MinerU-Diffusion:** no named accuracy benchmark is retained. Its card reports relative operating points versus MinerU2.5: 2.12× speed at 99.9% relative accuracy and 3.01× at 98.8%, with up to 3.26× throughput.[^mineru-diffusion-card]
- **NVIDIA Nemotron Parse v1.1:** the retained card names public and internal evaluation data but provides no benchmark, metric, or numeric result.[^nemotron-parse-card]
- **HunyuanOCR-1.5:** its own retained card provides no benchmark or latency values; its OmniDocBench v1.6 row above is a comparison transcribed by OvisOCR2 rather than direct evidence in the Hunyuan card.[^hunyuanocr-card][^ovisocr2-report]
- **RolmOCR:** the retained card claims speed and memory advantages but contains no benchmark score, throughput, hardware configuration, or numeric comparison.[^rolmocr-card]

## Throughput and decoding metrics

These measurements use different page renders, output lengths, hardware, concurrency, precision, and software, so they are deployment observations rather than a fair speed ranking.

| Model | Reported setup | Result |
|---|---|---|
| Chandra OCR 2 | H100 80GB, vLLM, concurrency 96, olmOCR mix | 1.44 pages/s; mean/P95 latency 60/156 s |
| Infinity-Parser2-Flash | H100, TP2, concurrency 8, longer `doc2json` | 1,624 tokens/s; 0.95 s/page |
| Infinity-Parser2-Pro | H100, TP2, concurrency 8 | 704 tokens/s; 2.13 s/page |
| LightOnOCR-2 | One H100 80GB, BF16, 1,403 olmOCR pages | 5.71 pages/s |
| Qianfan-OCR | One A100, vLLM 0.10.2, batch/query 512 | 0.503 pages/s W16A16; 1.024 W8A8 |
| Surya OCR 2 | RTX 5090, vLLM, concurrency 128, 96 DPI | 5.35 pages/s; 12,884 tokens/s |
| Unlimited OCR | Base mode, concurrency 512 | 5,580 tokens/s vs. DeepSeek-OCR 4,951; theoretical TPS remains 7,848 at 6,144 output tokens vs. 5,823 for DeepSeek-OCR |

[^chandra-ocr-2-card][^infinity-parser2-report][^lightonocr-report][^qianfan-ocr-report][^surya-ocr-2-card][^unlimited-ocr-report]

## Interpretation

- **Closest current comparison:** OvisOCR2 leads the retained Ovis-transcribed OmniDocBench v1.6 end-to-end table on every listed component, while its PureDocBench Real score trails Logics-Parsing-v2 and FD-RL. This is stronger evidence for clean/digital parsing than for universal in-the-wild superiority.[^ovisocr2-report]
- **Results evolve rapidly and conflict:** DeepSeek-OCR 2 is 91.09 in one v1.5 table and 89.17 in Unlimited OCR's; Chandra OCR 2 is 85.8 in its own olmOCR card and 83.1 in Infinity-Parser2's table. Version labels alone are insufficient to merge scores.
- **Task breadth changes the apparent winner:** Qianfan and Infinity-Parser2 expose OCR, layout, VQA, chart, KIE, and chemistry results, while Chandra, dots, and LightOn emphasize page transcription. Missing tasks are missing evidence, not zero capability.
- **Small end-to-end models can be competitive:** OvisOCR2 reports 0.8B and the top v1.6 value; LightOnOCR, Surya, and Granite report useful size–quality points. Their protocols remain first-party and not hardware- or evaluator-normalized.
- **No global winner is supported:** dataset versions, prompts, PDF metadata anchoring, page rendering, output schemas, retry behavior, excluded categories, evaluator implementations, and private data differ.

## Trust limits

Every numeric result is author-, vendor-, leaderboard-, or report-transcribed. The repository does not contain complete evaluated outputs, model weights for local reruns, benchmark snapshots, prompt/configuration manifests, or executable evaluation environments for the full family. Several cards reference absent local images or external artifacts; those were not used for values. The page records explicit results and conflicts, but it cannot verify leaderboard freshness, contamination controls, private benchmark composition, or causal claims about architecture and training.

## Relationships

- **Benchmarks:** the retained core models listed under **Scope and model coverage**.
- **Refines:** the end-to-end generative document-VLM family in [Current OCR approaches](current-ocr-approaches.md).
- **Complements:** [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md) and [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md).

[^deepseek-ocr-report]: Wei, Sun, and Li, *DeepSeek-OCR*, local source at [main.tex](../raw/2510.18234_DeepSeek-OCR/main.tex) (accessed 2026-08-17).
[^deepseek-ocr-2-report]: Wei, Sun, and Li, *DeepSeek-OCR 2*, local source at [main.tex](../raw/2601.20552_DeepSeek-OCR-2/main.tex) (accessed 2026-08-17).
[^infinity-parser-report]: Wang et al., *Infinity-Parser*, local source at [main.tex](../raw/2506.03197_InfinityParser/main.tex), especially `sections/experiments.tex` (accessed 2026-08-17).
[^lightonocr-report]: Taghadouini, Cavaillès, and Aubertin, *LightOnOCR*, local source at [templateArxiv.tex](../raw/2601.14251_LightOnOCR/templateArxiv.tex) (accessed 2026-08-17).
[^typhoonocr-report]: Nonesung et al., *Typhoon OCR*, local source at [main.tex](../raw/2601.14722_TyphoonOCR/main.tex) (accessed 2026-08-17).
[^firered-ocr-report]: Super Intelligence Team, *FireRed-OCR*, local source at [fireredocr_report.tex](../raw/2603.01840_FireRed-OCR/fireredocr_report.tex), especially `section/5_experiments.tex` (accessed 2026-08-17).
[^qianfan-ocr-report]: Baidu Qianfan Team, *Qianfan-OCR*, local source at [qianfan_ocr_report.tex](../raw/2603.13398_Qianfan-OCR/qianfan_ocr_report.tex) (accessed 2026-08-17).
[^unlimited-ocr-report]: Yin et al., *Unlimited OCR Works*, local source at [main.tex](../raw/2606.23050_Unlimited-OCR/main.tex) (accessed 2026-08-17).
[^infinity-parser2-report]: INF Team, *Infinity-Parser2*, local source at [arxiv_latex.tex](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex), especially `latex/experiments.tex` and `latex/appendix.tex` (accessed 2026-08-17).
[^ovisocr2-report]: Lu et al., *OvisOCR2*, local source at [main.tex](../raw/2607.13639_OvisOCR2/main.tex), especially `content/evaluation.tex` (accessed 2026-08-17).
[^chandra-card]: Datalab, local [Chandra model card](../raw/chandra.md) (accessed 2026-08-17).
[^chandra-ocr-2-card]: Datalab, local [Chandra OCR 2 model card](../raw/chandra-ocr-2.md) (accessed 2026-08-17).
[^dots-ocr-card]: rednote-hilab, local [dots.ocr model card](../raw/dots.ocr.md) (accessed 2026-08-17).
[^granite-docling-card]: IBM, local [Granite Docling 258M model card](../raw/granite-docling-258m.md) (accessed 2026-08-17).
[^hunyuanocr-card]: Tencent Hunyuan, local [HunyuanOCR-1.5 model card](../raw/HunyuanOCR-1.5.md) (accessed 2026-08-17).
[^mineru-diffusion-card]: MinerU-Diffusion authors, local [model card](../raw/MinerU-Diffusion-V1-0320-2.5B.md) (accessed 2026-08-17).
[^nanonets-ocr2-card]: Nanonets, local [Nanonets-OCR2 model card](../raw/Nanonets-OCR2.md) (accessed 2026-08-17).
[^nemotron-parse-card]: NVIDIA, local [Nemotron Parse v1.1 model card](../raw/NVIDIA-Nemotron-Parse-v1.1.md) (accessed 2026-08-17).
[^olmocr2-card]: Ai2, local [olmOCR-2-7B-1025 model card](../raw/olmOCR-2-7B-1025.md) (accessed 2026-08-17).
[^rolmocr-card]: Reducto AI, local [RolmOCR model card](../raw/RolmOCR.md) (accessed 2026-08-17).
[^surya-ocr-2-card]: Datalab, local [Surya OCR 2 model card](../raw/surya-ocr-2.md) (accessed 2026-08-17).
