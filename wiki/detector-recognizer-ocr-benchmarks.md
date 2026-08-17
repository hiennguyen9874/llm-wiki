---
type: Synthesis
title: Detector–recognizer OCR benchmarks
description: Detector–recognizer OCR benchmarks catalog the retained classical OCR model families, comparison-only baselines, datasets, metrics, and author-reported results without treating incompatible protocols as one leaderboard.
tags: [ocr, text-detection, text-recognition, benchmarks, evaluation]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T21:53:41+07:00 }
sources:
  - id: paddleocr3-report
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
  - id: pp-ocrv6-report
    resource: ../raw/2606.13108_PP-OCRv6/main.tex
    title: "PP-OCRv6: From 1.5M to 34.5M Parameters, Surpassing Billion-Scale VLMs on OCR Tasks"
  - id: nemotron-ocr-v2-card
    resource: ../raw/nemotron-ocr-v2.md
    title: Nemotron OCR v2 model card
---

# Detector–recognizer OCR benchmarks

The retained detector–recognizer family consists of [PP-OCRv5](pp-ocrv5.md), [PP-OCRv6](pp-ocrv6.md), and [Nemotron OCR v2](nemotron-ocr-v2.md). Their raw comparison tables additionally expose PP-OCRv3/v4, Nemotron OCR v1, OpenOCR, EasyOCR, and underspecified PaddleOCR variants as comparison-only members of the same broad architectural area. Results below are author or vendor reported and are grouped by exact protocol; they do not form one controlled global leaderboard.[^paddleocr3-report][^pp-ocrv6-report][^nemotron-ocr-v2-card]

## Model coverage

| Evidence level | Models or variants | Coverage decision |
|---|---|---|
| Retained wiki families | PP-OCRv5 server/mobile; PP-OCRv6 medium/small/tiny; Nemotron OCR v2 English/multilingual | Architecture and evaluation are described by dedicated concepts and raw sources. |
| Comparison-only generations | PP-OCRv3 mobile; PP-OCRv4 server/mobile; Nemotron OCR v1 | Numeric results are retained only where they occur in the three raw sources; no standalone local source was inspected. |
| Comparison-only external systems | OpenOCR server; EasyOCR; PaddleOCR base/specialized; language-specific `en_PP-OCRv5_mobile` and `latin_PP-OCRv5_mobile` | Identity or configuration is incomplete in the retained evidence, so results must not be generalized beyond the named table. |

PP-StructureV3, PaddleOCR-VL, GLM-OCR, FalconOCR, and similar systems are excluded: although they may contain a detector–recognizer stage, their primary evaluated unit is a modular document parser rather than plain text detection plus transcription.

## Metric and protocol map

| Dataset or protocol | Task | Metric | Direction | Important qualification |
|---|---|---|---|---|
| PP-OCRv5 self-built 17-scenario set | Text recognition | `1 - normalized edit distance` | Higher | Samples, category sizes, code, and uncertainty are unavailable. |
| PP-OCRv6 in-house 16-category set | Text detection | Polygon detection Hmean (%) | Higher | Private benchmark; cannot be equated with PP-OCRv5's 17-scenario set. |
| PP-OCRv6 scaled 600-image validation set | Detection robustness | Hmean, mean, standard deviation, CV | Hmean higher; std/CV lower | Seven synthetic resize factors from 0.35× to 2.83×. |
| PP-OCRv6 in-house 15-category set | Crop recognition | Accuracy and weighted average (%) | Higher | Private benchmark with undisclosed category sizes. |
| PP-OCRv6 hallucination set | Faithful transcription | Correct-output rate without hallucination (%) | Higher | Curated private set; metric is not general OCR accuracy. |
| PP-OCRv6 crop-margin set | Recognition robustness | Identical-prediction consistency (%) | Higher | Measures stability across crop margins, not correctness against ground truth. |
| PP-OCRv6 English/Latin sets | Crop recognition | Accuracy (%) | Higher | Dataset identity and composition are not supplied. |
| PP-OCRv6 200-image runtime set | End-to-end detection + recognition | Seconds/image | Lower | Includes disk I/O, preprocessing, inference, and postprocessing. |
| OmniDocBench crop mode | OCR recognition and throughput | Sample-average NED; pages/s | NED lower; throughput higher | Empty predictions are skipped; one A100; exact release and runtime configuration are incomplete. |
| Generated SynthDoG | Multilingual page OCR | Page-average NED | Lower | Synthetic generated data; configuration and generation seed are unavailable. |

## PP-OCRv5 report evaluation

The PaddleOCR 3.0 report evaluates 17 self-built scenarios: handwritten Chinese and English; printed Chinese and English; Pinyin; Japanese; ancient and Traditional Chinese; common, blurred, rotated, Greek, emoji, table, artistic-font, special-symbol, and deformed text. Its exact displayed aggregate is **0.804 1-EditDist** for PP-OCRv5 server at 0.07B parameters. Qwen2.5-VL-72B also displays 0.804 after rounding, so the report's prose claim that PP-OCRv5 ranks first is not established as a strict lead by the figure.[^paddleocr3-report]

The report's detailed bar chart supplies no numeric labels for the scenario-level bars. Those values are therefore not transcribed as exact measurements. It separately reports a **26% recognition-error reduction** on non-standard Chinese and English handwriting, but does not identify the exact predecessor or per-language sample counts.[^paddleocr3-report]

## PP-OCRv6 in-house detection benchmark

Hmean (%) on 16 categories; higher is better.[^pp-ocrv6-report]

| Model | Avg | HW-CN | HW-EN | Print-CN | Print-EN | TC | Ancient | JP | Blur | Emoji | Warp | Pinyin | Artistic | Table | Rotate | Industrial | General |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PP-OCRv5 server | 81.6 | 80.3 | 84.1 | 94.5 | 91.7 | 81.5 | 67.6 | 77.2 | 90.1 | 96.2 | 87.6 | 67.1 | 67.3 | 97.1 | 80.0 | 64.3 | 79.7 |
| PP-OCRv5 mobile | 75.2 | 74.4 | 77.7 | 90.5 | 91.0 | 82.3 | 58.1 | 72.7 | 87.4 | 93.6 | 82.7 | 57.5 | 52.5 | 92.8 | 64.7 | 52.8 | 72.1 |
| **PP-OCRv6 medium** | **86.2** | 83.7 | 84.0 | 95.1 | 93.7 | 86.3 | 80.2 | 84.3 | 94.1 | 99.6 | 88.6 | 74.0 | 69.0 | 96.8 | 93.8 | 73.3 | 82.8 |
| PP-OCRv6 small | 84.1 | 80.5 | 87.1 | 94.2 | 93.6 | 85.7 | 72.6 | 82.3 | 92.6 | 99.7 | 87.6 | 69.6 | 65.3 | 95.6 | 93.7 | 67.6 | 78.2 |
| PP-OCRv6 tiny | 80.6 | 79.4 | 85.9 | 93.1 | 92.3 | 83.7 | 63.0 | 76.6 | 89.3 | 99.8 | 86.1 | 59.0 | 60.1 | 94.7 | 91.0 | 62.0 | 73.8 |

### Detection robustness to resolution

Hmean at seven scales plus aggregate stability statistics.[^pp-ocrv6-report]

| Model | 0.35× | 0.50× | 0.71× | 1.00× | 1.41× | 2.00× | 2.83× | Mean ↑ | Std ↓ | CV % ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PP-OCRv4 server | 55.76 | 69.75 | 71.32 | 73.30 | 73.42 | 68.39 | 57.09 | 67.00 | 6.91 | 10.31 |
| PP-OCRv4 mobile | 48.53 | 65.51 | 68.38 | 68.56 | 69.73 | 68.56 | 64.65 | 64.84 | 6.87 | 10.60 |
| PP-OCRv5 server | 74.70 | 82.37 | 86.30 | 85.88 | 84.17 | 79.13 | 67.28 | 79.98 | 6.41 | 8.02 |
| PP-OCRv5 mobile | 66.94 | 73.59 | 79.20 | 81.50 | 80.77 | 75.39 | 65.81 | 74.74 | 5.91 | 7.90 |
| **PP-OCRv6 medium** | 76.29 | 85.00 | 89.04 | 89.72 | 89.69 | 89.04 | 87.94 | **86.67** | **4.50** | **5.19** |
| PP-OCRv6 small | 71.86 | 81.12 | 86.35 | 88.52 | 88.65 | 87.75 | 86.52 | 84.40 | 5.64 | 6.68 |
| PP-OCRv6 tiny | 69.21 | 78.12 | 83.64 | 84.74 | 84.92 | 84.24 | 81.81 | 80.95 | 5.27 | 6.52 |

## PP-OCRv6 in-house recognition benchmark

Accuracy (%) on 15 categories and weighted average; higher is better.[^pp-ocrv6-report]

| Model | W-Avg | HW-CN | HW-EN | Print-CN | Print-EN | TC | Ancient | JP | Confusable | Special | General | Pinyin | Artistic | Industrial | Screen | Card |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PP-OCRv5 server | 78.1 | 58.0 | 59.6 | 90.1 | 85.1 | 74.7 | 60.4 | 73.7 | 59.4 | 56.8 | 86.5 | 74.4 | 64.0 | 70.2 | 68.1 | 87.6 |
| PP-OCRv5 mobile | 73.7 | 41.7 | 50.9 | 86.0 | 86.0 | 72.0 | 57.8 | 75.8 | 55.7 | 54.8 | 80.7 | 72.5 | 54.0 | 59.3 | 57.6 | 81.7 |
| **PP-OCRv6 medium** | **83.2** | 62.1 | 67.8 | 91.5 | 94.1 | 78.6 | 72.4 | 90.5 | 64.9 | 61.7 | 87.5 | 78.1 | 71.2 | 77.4 | 82.5 | 88.1 |
| PP-OCRv6 small | 81.3 | 57.6 | 61.1 | 90.5 | 93.3 | 77.0 | 71.1 | 88.2 | 64.1 | 60.2 | 85.7 | 75.9 | 68.4 | 76.4 | 79.7 | 86.9 |
| PP-OCRv6 tiny | 73.5 | 40.1 | 39.3 | 86.7 | 88.4 | 65.0 | 68.4 | 89.8 | 52.3 | 57.1 | 78.0 | 65.4 | 54.7 | 62.1 | 71.2 | 80.5 |

### Hallucination and crop-margin robustness

These are distinct private protocols and should not be mixed with ground-truth recognition accuracy.[^pp-ocrv6-report]

| Protocol | Model | Metric | Result (%) |
|---|---|---|---:|
| Hallucination set | PP-OCRv6 medium | Correct output without hallucinated content | 93.20 |
| Hallucination set | PP-OCRv6 small | Same | 88.20 |
| Hallucination set | PP-OCRv6 tiny | Same | 86.80 |
| Crop-margin set | PP-OCRv3 mobile | Identical prediction across margins | 31.05 |
| Crop-margin set | PP-OCRv4 server | Same | 45.69 |
| Crop-margin set | PP-OCRv4 mobile | Same | 43.41 |
| Crop-margin set | PP-OCRv5 server | Same | 54.82 |
| Crop-margin set | PP-OCRv5 mobile | Same | 57.74 |
| Crop-margin set | PP-OCRv6 medium | Same | 75.32 |
| Crop-margin set | PP-OCRv6 small | Same | 67.80 |
| Crop-margin set | PP-OCRv6 tiny | Same | 44.80 |

### English and Latin-script recognition

Accuracy (%); PP-OCRv6 uses one unified recognizer, whereas the named PP-OCRv5 language models are specialized checkpoints.[^pp-ocrv6-report]

| Model | English | Latin |
|---|---:|---:|
| PP-OCRv5 server | 79.5 | — |
| PP-OCRv5 mobile | 78.3 | — |
| `en_PP-OCRv5_mobile` | 86.0 | — |
| `latin_PP-OCRv5_mobile` | 77.8 | 81.4 |
| **PP-OCRv6 medium** | **88.4** | **88.0** |
| PP-OCRv6 small | 86.3 | 84.0 |
| PP-OCRv6 tiny | 77.3 | 63.8 |

## PP-OCR end-to-end runtime benchmark

Seconds/image on 200 general-scene and document images; lower is better. The source includes disk I/O and all pipeline stages.[^pp-ocrv6-report]

| Hardware | Backend | v6 medium | v6 small | v6 tiny | v5 server | v5 mobile | v4 mobile |
|---|---|---:|---:|---:|---:|---:|---:|
| NVIDIA A100 | PaddlePaddle | 0.29 | 0.25 | 0.13 | 0.32 | 0.25 | 0.14 |
| NVIDIA A100 | TensorRT | — | 0.32 | 0.16 | — | 0.33 | 0.16 |
| NVIDIA V100 | PaddlePaddle | 0.72 | 0.49 | 0.21 | 0.66 | 0.50 | 0.25 |
| NVIDIA V100 | ONNX Runtime | 0.67 | 0.53 | 0.29 | 0.77 | 0.46 | 0.27 |
| NVIDIA V100 | TensorRT | 0.77 | 0.60 | 0.23 | 0.73 | 0.59 | 0.27 |
| Intel Xeon 8350C | PaddlePaddle | 2.05 | 0.79 | 0.32 | 2.04 | 0.80 | 0.62 |
| Intel Xeon 8350C | OpenVINO | 1.40 | 0.59 | 0.20 | 7.30 | 0.78 | 0.60 |
| Intel Xeon 8350C | ONNX Runtime | 3.31 | 0.61 | 0.22 | 6.36 | 0.61 | 0.49 |
| Apple M4 | PaddlePaddle | 8.82 | 3.07 | 0.96 | >10 | 5.82 | 5.65 |
| Apple M4 | ONNX Runtime | 5.55 | 1.29 | 0.35 | 7.20 | 1.10 | 1.02 |

A separate detector-only benchmark uses batch size 1, 15 warm-ups, and 30 measured iterations on a V100 or Xeon Gold 6271C over 512–2048-pixel square inputs. Exact values supplied in prose at 2048 pixels are: v6 medium **106.89 ms GPU / 2327.23 ms CPU ONNX**, v5 server **253.52 / 3034.93**, v6 small **42.70 / 654.25**, and v5 mobile **37.36 / 687.98**; v6 tiny CPU ONNX is **317.06 ms**. Other curve points have no numeric labels in the source figure and are not treated as exact data.[^pp-ocrv6-report]

## Nemotron OCR v2: OmniDocBench crop mode

Sample-average NED (lower is better), with throughput on one A100. Empty predictions are skipped.[^nemotron-ocr-v2-card]

| Model | pages/s ↑ | EN | ZH | Mixed | White | Single | Multi | Normal | Rotate90 | Rotate270 | Horizontal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PaddleOCR v5 server | 1.2 | 0.027 | 0.037 | 0.041 | 0.031 | 0.035 | 0.064 | 0.031 | 0.116 | 0.897 | 0.027 |
| OpenOCR server | 1.5 | 0.024 | 0.033 | 0.049 | 0.027 | 0.034 | 0.061 | 0.028 | 0.042 | 0.761 | 0.034 |
| **Nemotron OCR v2 multilingual** | **34.7** | 0.048 | 0.072 | 0.142 | 0.061 | 0.049 | 0.117 | 0.062 | 0.109 | 0.332 | 0.372 |
| Nemotron OCR v2 English | 40.7 | 0.038 | 0.830 | 0.437 | 0.348 | 0.282 | 0.572 | 0.353 | 0.232 | 0.827 | 0.893 |
| EasyOCR | 0.4 | 0.095 | 0.117 | 0.326 | 0.095 | 0.179 | 0.322 | 0.110 | 0.987 | 0.979 | 0.809 |
| Nemotron OCR v1 | 39.3 | 0.038 | 0.876 | 0.436 | 0.472 | 0.434 | 0.715 | 0.482 | 0.358 | 0.871 | 0.979 |

The table indicates a throughput–accuracy trade-off rather than an unqualified Nemotron accuracy lead: PaddleOCR v5 and OpenOCR have lower NED in many content columns, while Nemotron v2 multilingual is far faster under the vendor's reported setup and is much less degraded than English-only Nemotron variants on non-English samples.[^nemotron-ocr-v2-card]

## Nemotron OCR v2: generated SynthDoG

Page-average NED by language; lower is better.[^nemotron-ocr-v2-card]

| Language | PaddleOCR base | PaddleOCR specialized | OpenOCR server | Nemotron v1 | Nemotron v2 English | **Nemotron v2 multilingual** |
|---|---:|---:|---:|---:|---:|---:|
| English | 0.117 | 0.096 | 0.105 | 0.078 | 0.079 | **0.069** |
| Japanese | 0.201 | 0.201 | 0.586 | 0.723 | 0.765 | **0.046** |
| Korean | 0.943 | 0.133 | 0.837 | 0.923 | 0.924 | **0.047** |
| Russian | 0.959 | 0.163 | 0.950 | 0.564 | 0.632 | **0.043** |
| Chinese, Simplified | 0.054 | 0.054 | 0.061 | 0.784 | 0.819 | **0.035** |
| Chinese, Traditional | 0.094 | 0.094 | 0.127 | 0.700 | 0.756 | **0.065** |

## Interpretation

- **Accuracy depends on task:** PP-OCRv6 medium leads the retained PP-OCR rows on its private detection and recognition sets, but OmniDocBench crop-mode reports lower NED for PaddleOCR v5 or OpenOCR than Nemotron v2 in many columns.
- **Throughput is protocol-bound:** Nemotron's pages/s and PP-OCR's seconds/image use different images, software, and measurement boundaries and cannot be converted into a fair cross-source speed ranking.
- **Synthetic multilingual strength is not real-world proof:** Nemotron v2 multilingual is best in every listed SynthDoG language, but SynthDoG is generated data and the retained artifact lacks reproducible scripts.
- **No global winner is supported:** all three sources are first-party, most datasets are private or incompletely configured, and no retained evaluation runs every model under one disclosed protocol.

## Trust limits

The PaddleOCR reports provide neither evaluation samples nor executable benchmark configurations. The Nemotron model card provides no evaluated outputs, exact OmniDocBench release, SynthDoG generation configuration, or complete runtime settings. PP-OCRv5's scenario bars and PP-OCRv6's detector-speed curves include unlabeled graphical values; only explicitly printed values are recorded here. No result in this page has been independently reproduced from the retained bundle.[^paddleocr3-report][^pp-ocrv6-report][^nemotron-ocr-v2-card]

## Relationships

- **Benchmarks:** [PP-OCRv5](pp-ocrv5.md), [PP-OCRv6](pp-ocrv6.md), and [Nemotron OCR v2](nemotron-ocr-v2.md).
- **Refines:** the detector–recognizer family described in [Current OCR approaches](current-ocr-approaches.md) with model-, dataset-, metric-, and protocol-level evidence.

[^paddleocr3-report]: Cui et al., *PaddleOCR 3.0 Technical Report*, local source at [main.tex](../raw/2507.05595_PaddleOCR-3.0/main.tex), including visually reviewed [aggregate benchmark](../raw/2507.05595_PaddleOCR-3.0/images/pp_ocrv5_benchmark.pdf) and [scenario chart](../raw/2507.05595_PaddleOCR-3.0/images/ocr_res_final.png) (accessed 2026-08-17).
[^pp-ocrv6-report]: Zhang et al., *PP-OCRv6*, local source at [main.tex](../raw/2606.13108_PP-OCRv6/main.tex), including its detection, recognition, robustness, hallucination, multilingual, and latency tables and visually reviewed speed figures (accessed 2026-08-17).
[^nemotron-ocr-v2-card]: NVIDIA, *Nemotron OCR v2 model card*, local [model card](../raw/nemotron-ocr-v2.md), including its OmniDocBench and generated SynthDoG reference tables (accessed 2026-08-17).
