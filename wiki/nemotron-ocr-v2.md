---
type: Model System
title: Nemotron OCR v2
description: Nemotron OCR v2 is NVIDIA's detector–recognizer OCR system with a relational layout model, offered in English word-level and six-language line-level variants.
tags: [ocr, multilingual, text-detection, text-recognition, layout-analysis, reading-order]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T21:53:41+07:00 }
sources:
  - id: nemotron-ocr-v2-model-card
    resource: ../raw/nemotron-ocr-v2.md
    title: Nemotron OCR v2 model card
---

# Nemotron OCR v2

Nemotron OCR v2 is NVIDIA's three-stage OCR system: a RegNetX-8GF text detector localizes regions, a Transformer recognizer transcribes them, and a relational model predicts layout groupings and reading order. The released English variant operates on word-level regions; the multilingual variant operates on line-level regions and supports English, Simplified and Traditional Chinese, Japanese, Korean, and Russian.[^nemotron-ocr-v2-model-card]

## Variants and operation

| Variant | Recognizer | Maximum sequence length | Character set | Total parameters |
|---|---:|---:|---:|---:|
| `v2_english` | 3-layer, 256-dimensional Transformer | 32 | 855 | 53.8M |
| `v2_multilingual` | 6-layer, 512-dimensional Transformer | 128 | 14,244 | 83.9M |

Both variants use the same 45.4M-parameter detector and broadly similar approximately 2.3M-parameter relational model; their parameter difference is primarily in the recognizer.[^nemotron-ocr-v2-model-card]

The PyTorch API accepts RGB PNG or JPEG images as single images or batches, automatically resizes at multiple scales, and returns text, confidence, and bounding-box coordinates. With default construction it downloads the multilingual v2 checkpoint; `lang="en"` selects the English checkpoint, while a complete local checkpoint directory takes precedence over `lang`.[^nemotron-ocr-v2-model-card]

A detector-only mode returns regions without transcription. The source claims this loads only the detector and uses approximately 37% less GPU memory and runs approximately 20% faster; skipping the relational model is claimed to use approximately 35% less GPU memory and run approximately 8% faster, at the cost of reading-order grouping.[^nemotron-ocr-v2-model-card]

## Training and deployment

The model card describes approximately 12 million training images: about 680,000 real-world images spanning scenes, charts, tables, infographics, and handwriting, plus more than 11 million synthetic multilingual document and historical-document images. It does not identify the component datasets, their licenses, or sampling proportions beyond these aggregates.[^nemotron-ocr-v2-model-card]

The documented package requires Linux amd64, Python 3.12, an NVIDIA GPU, a CUDA toolkit compatible with the installed PyTorch build, and C++17/OpenMP tooling because installation compiles a C++ CUDA extension. NVIDIA also documents a Docker workflow. The card lists Ampere, Lovelace, Hopper, and Blackwell as supported microarchitectures.[^nemotron-ocr-v2-model-card]

## Reported evaluation

All metrics are NVIDIA reference results and have not been independently reproduced:[^nemotron-ocr-v2-model-card]

- On OmniDocBench crop-mode evaluation on one A100, the multilingual variant is reported at **34.7 pages/s** and normalized edit distance (lower is better) of **0.048** for English, **0.072** for Chinese, and **0.142** for mixed English/Chinese samples. The English variant is reported at **40.7 pages/s** and **0.038** English NED, but performs poorly on the non-English subsets shown in the table.
- On generated SynthDoG data, the multilingual variant is reported between **0.035** and **0.069** NED across English, Japanese, Korean, Russian, Simplified Chinese, and Traditional Chinese.

## Trust limits

- The local source is a model card, not a technical report. It contains no weights, source code, evaluation scripts, model outputs, dataset manifests, or benchmark configurations, so its architectural, training, throughput, and accuracy claims cannot be reproduced from this bundle.[^nemotron-ocr-v2-model-card]
- The OmniDocBench table states crop mode and a single A100, but does not fully specify batch size, image preprocessing, runtime versions, or exact benchmark release. Its cross-model comparisons are therefore not controlled evidence for deployment selection.[^nemotron-ocr-v2-model-card]
- The source calls the model commercially usable and names both the NVIDIA Open Model License Agreement and Apache 2.0 as additional information, but does not make the scope of each term clear in this local artifact. Confirm applicable terms from the linked license materials before use.[^nemotron-ocr-v2-model-card]

## Relationships

- **Benchmarked by:** [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md), which retains the full reported OmniDocBench crop-mode and generated SynthDoG tables alongside the comparison-only baselines.

[^nemotron-ocr-v2-model-card]: NVIDIA, *Nemotron OCR v2 model card*, local [nemotron-ocr-v2.md](../raw/nemotron-ocr-v2.md) (accessed 2026-08-17).
