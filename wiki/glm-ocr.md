---
type: Model System
title: GLM-OCR
description: GLM-OCR is a 0.9B two-stage document OCR system that combines PP-DocLayoutV3 region parsing with a CogViT-GLM recognizer using shared-parameter multi-token prediction.
tags: [ocr, document-parsing, vision-language-models, layout-analysis, multi-token-prediction, key-information-extraction]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:00:00Z }
sources:
  - id: glm-ocr-report
    resource: ../raw/2603.10910_GLM-OCR/main.tex
    title: GLM-OCR Technical Report
  - id: glm-ocr-model-card
    resource: ../raw/2603.10910_GLM-OCR/README.md
    title: GLM-OCR model card
---

# GLM-OCR

GLM-OCR is a 0.9B two-stage document OCR system: PP-DocLayoutV3 detects and crops text, formula, and table regions for parallel recognition by a 0.4B CogViT encoder and 0.5B GLM decoder; a separate prompted path performs full-page key-information extraction (KIE) as JSON.[^glm-ocr-report]

## Architecture and tasks

For document parsing, [PP-DocLayoutV3](pp-doclayoutv3.md) supplies layout regions, then GLM-OCR recognizes each crop and merges the results into Markdown or JSON in recovered reading order. The report motivates this decomposition as reducing small-model hallucination and repetition on complex pages while enabling parallel region recognition.[^glm-ocr-report]

The recognizer projects CogViT visual features into the decoder's embedding space as prefix tokens. Shared-parameter multi-token-prediction (MTP) heads predict future token offsets alongside the main head; the authors say this improves structural consistency and reduces decoding steps. They train with ten-token prediction and report 5.2 generated tokens per decoding step, or about 50% higher throughput.[^glm-ocr-report]

For KIE, GLM-OCR directly processes the entire document image and a task-specific prompt that specifies the required JSON schema; unlike parsing, this mode does not use layout crops.[^glm-ocr-report][^glm-ocr-model-card]

## Training

The reported training recipe has four stages: CogViT pretraining on image-text and grounding/retrieval data with MIM, CLIP, and distillation objectives; joint vision-language pretraining; MTP-enabled supervised fine-tuning for text, formula, table, and KIE tasks; then GRPO reinforcement learning. The RL rewards pair task metrics with structural constraints, including repetition penalties for text, structure validity for formulas, tag closure for tables, and JSON parse plus field penalties for KIE.[^glm-ocr-report]

## Reported results and deployment

All results below are author-reported and not independently reproduced:[^glm-ocr-report]

- **OmniDocBench v1.5:** 94.62 overall; text edit distance 0.040; formula CDM 93.90; table TEDS 93.96; table TEDS-S 96.39; and reading-order edit distance 0.044. The report's cross-system table lists [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) at 94.50 overall under its reported evaluation.
- **Other public benchmarks:** OCRBench text 94.0, UniMERNet 96.5, PubTabNet 85.2, TEDS_TEST 86.0, Nanonets-KIE 93.7, and Handwritten-KIE 86.1.
- **Throughput:** under the authors' single-replica, single-concurrency configuration, 0.67 image pages/s and 1.86 PDF pages/s for parsing and Markdown export. The report lists different systems and configurations for its comparisons, so this is a system-configuration result rather than a model-only measurement.[^glm-ocr-report]

The model card documents vLLM, SGLang, Ollama, and Transformers inference. It recommends the official SDK for layout-aware document parsing and limits direct prompts to text, formula, and table recognition plus schema-constrained KIE.[^glm-ocr-model-card]

## Limitations and trust limits

- The two-stage design can propagate layout-detection errors; cross-page dependencies, irregular multi-column layouts, and reading-order reconstruction remain failure points.[^glm-ocr-report]
- The report identifies degradation risks for very low-resolution or distorted documents, complex formulas, dense or irregular tables, and underrepresented languages. Generative formatting may vary in whitespace and line breaks, and KIE depends on prompt and schema clarity.[^glm-ocr-report]
- The local bundle contains the report source, model card, tables, and architecture, benchmark, and illustrative PDF figures, but not weights, local inference or training code, datasets, prompts beyond the model-card examples, or evaluation scripts. Its training, quality, and throughput claims cannot be reproduced from this bundle.[^glm-ocr-report][^glm-ocr-model-card]
- The report includes custom in-house benchmarks but does not supply their composition, protocols, or uncertainty. Public benchmark values are also author-reported; cross-paper ranking and throughput comparisons require matched versions and configurations.[^glm-ocr-report]

## Relationships

- **Uses:** [PP-DocLayoutV3](pp-doclayoutv3.md) for layout detection, region cropping, and reading order before document-region recognition.[^glm-ocr-report]
- **Compared with:** [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md), another 0.9B two-stage parser that uses the same layout model. The source's reported scores are not a controlled comparison.[^glm-ocr-report]
- **Compared with:** [DeepSeek-OCR 2](deepseek-ocr-2.md), an end-to-end OCR VLM listed in the report's evaluation tables; their cross-source evaluation conditions are not established as equivalent.[^glm-ocr-report]

[^glm-ocr-report]: Duan et al., *GLM-OCR Technical Report*, local LaTeX source at [main.tex](../raw/2603.10910_GLM-OCR/main.tex), including the [architecture figure](../raw/2603.10910_GLM-OCR/assets/model.pdf), [benchmark visualization](../raw/2603.10910_GLM-OCR/assets/omnidocbench_vis.pdf), and [result tables](../raw/2603.10910_GLM-OCR/tables/docparse.tex), [OmniDocBench](../raw/2603.10910_GLM-OCR/tables/omnidocbench.tex), and [in-house results](../raw/2603.10910_GLM-OCR/tables/self_eval.tex) (accessed 2026-08-17).
[^glm-ocr-model-card]: Zhipu AI, [GLM-OCR model card](../raw/2603.10910_GLM-OCR/README.md) (accessed 2026-08-17).
