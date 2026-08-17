---
type: Software
title: PaddleOCR 3.0
description: PaddleOCR 3.0 is an open-source document-AI toolkit that unifies model training, layered inference, heterogeneous deployment, and MCP access around three OCR and document-understanding pipelines.
tags: [ocr, document-ai, inference, deployment, mcp]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:29:24Z }
sources:
  - id: paddleocr3-report
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
---

# PaddleOCR 3.0

PaddleOCR 3.0 is an Apache-licensed toolkit for OCR and document parsing. Its three principal solutions separate text extraction, structured page parsing, and question-driven key information extraction, while a shared PaddleX-based inference library provides consistent APIs, configuration, optimization, serving, mobile deployment, and MCP integration.[^paddleocr3-report]

## Core solutions

- [PP-OCRv5](pp-ocrv5.md) performs lightweight multilingual text detection and recognition.
- [PP-StructureV3](pp-structurev3.md) composes OCR, layout analysis, specialized element recognizers, and postprocessing to emit JSON and Markdown.
- [PP-ChatOCRv4](pp-chatocrv4.md) combines parsed text retrieval and image-based VLM extraction for document key information extraction.

## Codebase architecture

The codebase separates a command-driven model training toolkit from an inference library. The inference library has three layers:[^paddleocr3-report]

1. **Interface:** a unified Python API and task-specific CLI subcommands, with selected backward compatibility.
2. **Wrapper:** model and pipeline wrappers supporting both arguments and reusable configuration files.
3. **Foundation:** PaddleX 3.0 supplies inference optimization and deployment, separating inference from training scripts.

This design addresses the report's stated PaddleOCR 2.x problems: a single expanding CLI namespace, argument-only configuration, and overlapping training/inference entry points.[^paddleocr3-report]

## Deployment surface

High-performance inference automatically selects among Paddle Inference, OpenVINO, ONNX Runtime, and TensorRT, and can apply multithreading, FP16, and on-demand Paddle-to-ONNX conversion. On a Tesla T4, the authors report latency reductions of 73.1% for `PP-OCRv5_mobile_rec` and 40.4% for `PP-OCRv5_mobile_det` when high-performance inference is enabled.[^paddleocr3-report]

Serving has two levels: a lightweight FastAPI service for validation and low concurrency, and an NVIDIA Triton-based option for multi-instance or multi-GPU operation. Paddle-Lite supports mobile deployment.[^paddleocr3-report]

The MCP server exposes OCR and PP-StructureV3 over stdio or Streamable HTTP. It can execute through a local Python library, PaddlePaddle AI Studio, or a self-hosted PaddleOCR service, allowing privacy-sensitive use to remain local while retaining cloud and managed-service paths.[^paddleocr3-report]

## Trust limits

- Performance and latency results are author-reported; this source bundle contains no executable evaluation or deployment artifacts for independent reproduction.[^paddleocr3-report]
- The abstract's statement that "these models with fewer than 100 million parameters" rival billion-parameter VLMs is too broad as written. PP-OCRv5 is reported as 0.07B, but PP-ChatOCRv4 explicitly uses PP-DocBee2-3B and an example ERNIE-4.5-300B-A47B LLM; the report also does not provide a clear total parameter count for PP-StructureV3's multi-model pipeline.[^paddleocr3-report]
- Hardware support and backend selection are described as capabilities, not a complete compatibility matrix; actual availability depends on model, runtime, and device.[^paddleocr3-report]

## Relationships

- **Includes:** [PP-OCRv5](pp-ocrv5.md), [PP-StructureV3](pp-structurev3.md), and [PP-ChatOCRv4](pp-chatocrv4.md).

[^paddleocr3-report]: Cui et al., *PaddleOCR 3.0 Technical Report*, local LaTeX source at [main.tex](../raw/2507.05595_PaddleOCR-3.0/main.tex), with referenced architecture, pipeline, deployment, and benchmark figures in the same source bundle (accessed 2026-08-17).
