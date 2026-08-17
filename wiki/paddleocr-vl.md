---
type: Model System
title: PaddleOCR-VL
description: PaddleOCR-VL is a two-stage document parser that combines PP-DocLayoutV2 with a 0.9B dynamic-resolution VLM for multilingual text, table, formula, and chart conversion.
tags: [document-parsing, ocr, multilingual, vision-language-models, layout-analysis]
status: deprecated
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:27:43Z }
sources:
  - id: paddleocr-vl-report
    resource: ../raw/2510.14528_PaddleOCR-VL/main.tex
    title: "PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model"
  - id: paddleocr-vl-model-card
    resource: ../raw/PaddleOCR-VL.md
    title: PaddleOCR-VL model card
---

# PaddleOCR-VL

PaddleOCR-VL is a two-stage document parser: [PP-DocLayoutV2](pp-doclayoutv2.md) detects elements and their reading order, then PaddleOCR-VL-0.9B recognizes each crop as text, a table, a formula, or a chart before post-processing emits Markdown and JSON. The authors report support for 109 languages and position the decoupling as a way to avoid long page-level autoregressive layout outputs.[^paddleocr-vl-report]

## Element-recognition model

PaddleOCR-VL-0.9B follows a LLaVA-like architecture. A NaViT-style native dynamic-resolution visual encoder, initialized from Keye-VL, feeds a randomly initialized two-layer GELU MLP projector with 2×2 patch merging; ERNIE-4.5-0.3B with 3D-RoPE decodes the task-specific output. The architecture figure labels the visual encoder as NaViT-400M.[^paddleocr-vl-report]

Instruction fine-tuning teaches four output targets: OCR text, OTSL table structures, LaTeX formulas (distinguishing inline and display expressions), and chart data as Markdown tables.[^paddleocr-vl-report]

## Deployment interfaces

The model card documents the official `paddleocr doc_parser` CLI and `PaddleOCRVL(...).predict` Python pipeline, which can save results as JSON and Markdown. It also documents routing the VLM recognition backend to a locally served vLLM endpoint through `vl_rec_backend="vllm-server"` and `vl_rec_server_url`.[^paddleocr-vl-model-card]

Its direct Hugging Face Transformers example supports individual OCR, table, formula, and chart prompts, but not full document parsing. The card recommends the official pipeline for faster inference and page-level parsing; it also provides a FlashAttention 2 configuration intended to improve inference speed and reduce memory use.[^paddleocr-vl-model-card]

## Training and data construction

The VLM is trained in two all-parameter stages: alignment on 29M samples for one epoch at up to 1280×28×28 resolution, followed by two instruction-tuning epochs on 2.7M samples at up to 2048×28×28. Both stages use a 16,384-token sequence length and batch size 128; their maximum learning rates are $5×10^{-5}$ and $5×10^{-6}$, respectively.[^paddleocr-vl-report]

The report describes more than 30M total training samples from public, synthetic, publicly accessible web, and in-house sources. Its automatic-labeling workflow starts with [PP-StructureV3](pp-structurev3.md) pseudo-labels, has ERNIE-4.5-VL and Qwen2.5-VL refine them from images and prompts, then filters likely hallucinations. A type-specific evaluation engine supports hard-case mining and targeted synthetic data generation.[^paddleocr-vl-report]

## Reported results and throughput

All results below are author-reported and not independently reproduced:[^paddleocr-vl-report]

- **Page parsing:** on OmniDocBench v1.5, the reported overall score is **92.86**, with text edit distance **0.035**, formula CDM **91.22**, table TEDS **90.89**, table TEDS-S **94.76**, and reading-order edit distance **0.043**. On olmOCR-Bench, the report gives an **80.0 ± 1.0** overall pass rate.
- **Element recognition:** on the cropped OmniDocBench v1.5 subsets, it reports **0.9195** overall TEDS for tables and **0.9453** CDM for formulas. Chart performance is reported only on the authors' 1,801-sample in-house benchmark, where it gives RMS-F1 **0.8440**.
- **End-to-end efficiency:** for 981 OmniDocBench v1.0 pages batched 512 at a time on one A100, the FastDeploy configuration reports **1.6184 pages/s** and **2,486.4 output tokens/s**. The comparisons use different model backends, including vLLM for the listed baselines, so this is a system-configuration result rather than a model-only measurement.

## Trust limits

- The source bundle provides a manuscript, bibliography, source figures, and illustrative samples, but no weights, training corpus, inference implementation, or evaluation code. Its model, data, quality, and performance claims cannot be independently reproduced from this bundle.[^paddleocr-vl-report]
- Several headline comparisons rely on in-house evaluations: 107,452 OCR samples, table and formula evaluations, and the 1,801-sample chart set. Their full composition, prompts, baseline configurations, and uncertainty are not sufficiently specified for an independent ranking.[^paddleocr-vl-report]
- The public-benchmark results are still author-reported. The source credits benchmark organizers for some baseline results but reports its own and MinerU2.5 values; version and configuration differences constrain cross-paper rankings.[^paddleocr-vl-report]
- The model card contains instructions and remote links, not local model files, deployment-image contents, test inputs, or evaluated outputs; its operational claims have not been independently exercised from this source.[^paddleocr-vl-model-card]

## Supersession

[PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) is the intermediate replacement, with a new layout stage and added recognition and post-processing tasks. The current model card identifies [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) as the new version.[^paddleocr-vl-model-card]

## Relationships

- **Superseded by:** [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md), its immediate replacement, which changes the layout component and adds spotting, seal recognition, and long-document post-processing.
- **Current version:** [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), identified by this model card as the new version.[^paddleocr-vl-model-card]
- **Uses:** [PP-DocLayoutV2](pp-doclayoutv2.md) supplies element positions and reading order before VLM recognition.
- **Uses:** [PP-StructureV3](pp-structurev3.md) supplies pseudo-labels in the described automatic data-annotation pipeline.
- **Compared with:** [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) also converts pages to structured Markdown, but uses an end-to-end 7B VLM and reinforcement learning rather than detection-led element recognition.

[^paddleocr-vl-report]: Cui et al., *PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model*, local LaTeX source at [main.tex](../raw/2510.14528_PaddleOCR-VL/main.tex), including `images/PaddleOCR-VL.png`, `images/PP-DocLayoutV2.png`, `images/PaddleOCR-VL-0.9B.png`, `images/paddleocr-vl_metrics.png`, and the training-data figures (accessed 2026-08-17).
[^paddleocr-vl-model-card]: PaddlePaddle, [PaddleOCR-VL model card](../raw/PaddleOCR-VL.md) (accessed 2026-08-17).