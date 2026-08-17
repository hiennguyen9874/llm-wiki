---
type: Model System
title: DeepSeek-OCR 2
description: DeepSeek-OCR 2 is an end-to-end document OCR VLM that uses DeepEncoder V2 to causally reorder compressed visual tokens before a 3B MoE decoder.
tags: [ocr, document-parsing, vision-language-models, visual-token-compression, reading-order]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:48:19Z }
sources:
  - id: deepseek-ocr-2-report
    resource: ../raw/2601.20552_DeepSeek-OCR-2/main.tex
    title: "DeepSeek-OCR 2: Visual Causal Flow"
  - id: deepseek-ocr-2-model-card
    resource: ../raw/2601.20552_DeepSeek-OCR-2/README.md
    title: DeepSeek-OCR 2 model card
---

# DeepSeek-OCR 2

DeepSeek-OCR 2 is an end-to-end document OCR VLM built on DeepSeek-OCR's image-compression approach. Its DeepEncoder V2 replaces the prior CLIP-like global module with an LLM-style encoder that emits causally ordered query tokens for a DeepSeek 3B MoE decoder; the authors position this as a way to improve document reading order without increasing the visual-token budget.[^deepseek-ocr-2-report]

## Architecture

An 80M SAM-base-style vision tokenizer followed by two convolutional layers reduces image-token count 16-fold and produces 896-dimensional features. DeepEncoder V2 then combines these visual tokens with an equal number of learned causal-flow queries in a Qwen2-0.5B-based encoder. Visual tokens attend bidirectionally; a query can attend to every visual token and preceding queries, but not subsequent queries. Only the query outputs reach the decoder.[^deepseek-ocr-2-report]

The model uses a 1024x1024 global view with 256 queries and zero to six 768x768 local views with 144 queries each, for 256--1,120 decoder-input visual tokens per image. The decoder remains DeepSeek-3B-A500M, a 3B-parameter MoE decoder with about 500M active parameters according to the report.[^deepseek-ocr-2-report]

## Training

The report describes three stages: encoder pretraining, query enhancement with the encoder and decoder jointly optimized, and decoder-only continued training with the encoder frozen. It says the training mix is 80% OCR data and differs from DeepSeek-OCR through a 3:1:1 text/formula/table sampling scheme for OCR 1.0 data and merged semantically similar layout labels.[^deepseek-ocr-2-report]

## Reported evaluation

All results are author-reported and have not been independently reproduced:[^deepseek-ocr-2-report]

- On OmniDocBench v1.5, the report gives an overall score of **91.09**, text edit distance **0.048**, formula CDM **90.31**, table TEDS **87.75**, table TEDS-S **92.06**, and reading-order edit distance **0.057**, using at most 1,120 visual tokens. Its DeepSeek-OCR baseline result is 87.36 overall with a 0.085 reading-order edit distance at 1,156 tokens.
- On the report's document-element edit-distance table, DeepSeek-OCR 2 has **0.100** overall edit distance, compared with **0.129** for DeepSeek-OCR. The report lists a 0.115 result for Gemini-3 Pro at the same 1,120-token limit, but gives neither its configuration nor the component-level Gemini scores.
- The authors' production-quality proxy is output repetition rate: 4.17% versus 6.25% for online user-log images and 2.88% versus 3.69% for PDF pretraining data, for DeepSeek-OCR 2 versus DeepSeek-OCR respectively. They state that ground truth was unavailable in those production settings.

## Trust limits

- The local bundle contains the report, bibliography, five source figures, and a model card. It does not contain weights, code, training data, prompts beyond two model-card examples, or evaluation scripts; its performance and training claims cannot be reproduced from this bundle.[^deepseek-ocr-2-report][^deepseek-ocr-2-model-card]
- The manuscript labels the comparison values in its main OmniDocBench table as either its own results or values sourced from the benchmark repository. Version, rendering, prompts, and inference settings are not fully specified here, limiting cross-system ranking.[^deepseek-ocr-2-report]
- The causal-flow interpretation is the authors' architectural rationale. The source measures document outputs and reading-order edit distance, not directly whether the learned queries correspond to human visual scan paths.[^deepseek-ocr-2-report]

## Relationships

- **Builds on:** [DeepSeek-OCR](deepseek-ocr.md), retaining its compressed vision tokenizer and 3B MoE decoder while replacing the CLIP-like encoder component.[^deepseek-ocr-2-report]
- **Related to:** [Optical Context Compression](optical-context-compression.md), the earlier DeepSeek-OCR proposal; this source evaluates document OCR rather than end-to-end long-context retrieval.[^deepseek-ocr-2-report]
- **Compared with:** [PaddleOCR-VL](paddleocr-vl.md), which reports a higher OmniDocBench v1.5 overall score in a distinct two-stage system. The author-reported cross-paper results are not a controlled comparison.[^deepseek-ocr-2-report]

[^deepseek-ocr-2-report]: Wei, Sun, and Li, *DeepSeek-OCR 2: Visual Causal Flow*, local LaTeX source at [main.tex](../raw/2601.20552_DeepSeek-OCR-2/main.tex), including [1_1.pdf](../raw/2601.20552_DeepSeek-OCR-2/fig/1_1.pdf), [2.pdf](../raw/2601.20552_DeepSeek-OCR-2/fig/2.pdf), [22.pdf](../raw/2601.20552_DeepSeek-OCR-2/fig/22.pdf), [3.pdf](../raw/2601.20552_DeepSeek-OCR-2/fig/3.pdf), and [5.pdf](../raw/2601.20552_DeepSeek-OCR-2/fig/5.pdf) (accessed 2026-08-17).
[^deepseek-ocr-2-model-card]: DeepSeek-AI, *DeepSeek-OCR 2 model card*, local [README.md](../raw/2601.20552_DeepSeek-OCR-2/README.md) (accessed 2026-08-17).
