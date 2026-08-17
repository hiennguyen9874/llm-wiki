---
type: Model System
title: DeepSeek-OCR
description: DeepSeek-OCR is an end-to-end OCR VLM whose DeepEncoder compresses high-resolution visual features before a 3B MoE decoder generates text or structured outputs.
tags: [ocr, document-parsing, vision-language-models, multilingual, context-compression]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:41:06Z }
sources:
  - id: deepseek-ocr-paper
    resource: ../raw/2510.18234_DeepSeek-OCR/main.tex
    title: "DeepSeek-OCR: Contexts Optical Compression"
  - id: deepseek-ocr-model-card
    resource: ../raw/2510.18234_DeepSeek-OCR/README.md
    title: DeepSeek-OCR model card
---

# DeepSeek-OCR

DeepSeek-OCR is an end-to-end vision-language OCR system intended to use relatively few vision tokens for document transcription and structured extraction. Its authors pair a serial high-resolution encoder with a 3B MoE decoder (570M activated parameters) and frame the model as an empirical prototype for [optical context compression](optical-context-compression.md).[^deepseek-ocr-paper]

## Architecture

DeepEncoder feeds SAM-base-style, window-attention perception features into a two-layer convolutional compressor, then feeds the reduced sequence to a CLIP-large-style global-attention component. The paper describes approximately 380M encoder parameters: 80M for the SAM-base component and 300M for the CLIP-large component. Each convolution has stride 2, producing a 16-fold reduction in vision-token count before global attention; for a 1024x1024 input, the stated path is 4,096 initial patches to 256 tokens.[^deepseek-ocr-paper]

The decoder is DeepSeek-3B-MoE. At inference, the authors state that it activates 6 of 64 routed experts plus 2 shared experts, for about 570M activated parameters.[^deepseek-ocr-paper]

## Input and task coverage

The model has four native modes: Tiny (512x512, 64 tokens), Small (640x640, 100), Base (1024x1024, 256), and Large (1280x1280, 400). The dynamic Gundam mode combines 640x640 local tiles with a 1024x1024 global view, yielding $100n+256$ vision tokens for $n$ tiles; the continued-training Gundam-M mode uses 1024x1024 local tiles and a 1280x1280 global view.[^deepseek-ocr-paper]

The authors train for text OCR, layout-conditioned OCR, charts to HTML tables, chemical-formula images to SMILES, simple plane geometry, and limited general-vision tasks. They report roughly 30M collected PDF pages spanning nearly 100 languages, plus synthetic and web-derived data; the final mix is 70% OCR, 20% general vision, and 10% text-only data. These data, their licenses, and the labeling pipeline are not included locally.[^deepseek-ocr-paper]

The model card shows Hugging Face Transformers inference with custom remote code and documents a vLLM configuration. It uses a prompt such as `Free OCR.` for plain transcription or a grounding prompt for Markdown conversion.[^deepseek-ocr-model-card]

## Reported evaluation

All figures below are author-reported, not independently reproduced:[^deepseek-ocr-paper]

- On a 100-document English Fox subset limited to 600--1,300 ground-truth tokens per page, Small mode (100 vision tokens) reported 96.8% precision for 800--900 tokens (8.5x compression) and 96.8% for 900--1,000 (9.7x); at 1,200--1,300 tokens (12.6x), it reported 87.1%. Tiny mode (64 tokens) reported 59.1% at 1,200--1,300 tokens (19.7x).
- On OmniDocBench, where lower edit distance is better, the reported English/Chinese overall edit distances are 0.386/0.361 in Tiny mode, 0.137/0.240 in Base mode (256 nominal, 182 valid tokens), 0.127/0.181 in Gundam mode (795 tokens), and 0.123/0.157 in Gundam-M mode (1,853 tokens at 200 dpi).
- The authors state that 20 nodes of eight A100-40G GPUs generated 33M pages per day in production. The abstract separately characterizes this as more than 200K pages per day for one A100-40G; neither configuration is reproducible from the local bundle.

## Trust limits

- This bundle contains an author manuscript, bibliography, source figures, and model-card instructions. It lacks model weights, training data, training and evaluation code, prompts for all tasks, and complete hardware/configuration details; performance and throughput cannot be independently reproduced here.[^deepseek-ocr-paper]
- The Fox result is an OCR reconstruction measurement on a narrow 100-page English subset. The authors note that their output format does not exactly match Fox ground truth, but do not provide a standardized reconciliation procedure; it does not establish lossless general text or conversation compression.[^deepseek-ocr-paper]
- The OmniDocBench table mixes DeepSeek-OCR modes with named baselines and gives no uncertainty. Cross-paper comparisons additionally require matched benchmark versions, page rendering, prompts, and inference setups.[^deepseek-ocr-paper]

## Relationships

- **Implements:** [Optical Context Compression](optical-context-compression.md) as an OCR-focused prototype.
- **Compared with:** [PaddleOCR-VL](paddleocr-vl.md), [PP-StructureV3](pp-structurev3.md), and [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) address document-image-to-structured-output tasks with different system decompositions; reported cross-paper ranks are not directly comparable without matched protocols.

[^deepseek-ocr-paper]: Wei, Sun, and Li, *DeepSeek-OCR: Contexts Optical Compression*, local LaTeX source at [main.tex](../raw/2510.18234_DeepSeek-OCR/main.tex), including `figures/1.pdf`, `figures/2.pdf`, `figures/3.pdf`, `figures/4.pdf`, `figures/precision_compression_chart.pdf`, and `figures/ocr_model_performance_comparison_final2.pdf` (accessed 2026-08-17).
[^deepseek-ocr-model-card]: DeepSeek-AI, *DeepSeek-OCR model card*, local [README.md](../raw/2510.18234_DeepSeek-OCR/README.md) (accessed 2026-08-17).
