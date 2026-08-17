---
type: Model System
title: PP-ChatOCRv4
description: PP-ChatOCRv4 extracts key information from documents by fusing retrieval-augmented OCR text answers with direct PP-DocBee2 vision-language answers.
tags: [document-understanding, key-information-extraction, rag, vision-language-models]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:29:24Z }
sources:
  - id: paddleocr3-report
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
---

# PP-ChatOCRv4

PP-ChatOCRv4 is a document key-information-extraction pipeline with parallel text and image paths. It retrieves relevant chunks from OCR-derived structured text for an LLM while PP-DocBee2 answers directly from document images; a final stage fuses both outputs.[^paddleocr3-report]

## Architecture

- **Text path:** PP-Structure parses text, layout, and tables; a vector store retrieves question-relevant content; prompt engineering combines the retrieved text and query for an LLM. The framework is described as LLM-agnostic, with ERNIE-4.5-300B-A47B used as the report's example.
- **Image path:** the 3B-parameter PP-DocBee2 document VLM receives document images and question-derived prompts directly.
- **Fusion:** text-derived and image-derived extraction results are merged into the final answer.[^paddleocr3-report]

The split is intended to combine efficient retrieval over long or multi-page text with visual access to complex layouts, rare characters, tables, and seals.[^paddleocr3-report]

## Reported results

On an internal benchmark of 638 document images and 1,196 question-answer pairs, the authors report **85.55% Recall@1** for PP-ChatOCRv4, compared with 80.26% for Qwen2.5-VL-72B, 70.08% for PP-ChatOCRv3, and 63.47% for GPT-4o.[^paddleocr3-report]

## Trust limits

- The benchmark is custom and unreleased in this bundle. Its domains are listed, but question construction, answer matching, per-domain composition, model prompts, costs, and uncertainty are not detailed enough for independent reproduction.[^paddleocr3-report]
- The report does not explain the fusion algorithm or provide ablations separating retrieval, LLM, PP-DocBee2, and fusion contributions.[^paddleocr3-report]
- Because the example text path uses a 300B-class LLM and the image path uses a 3B VLM, PP-ChatOCRv4 should not be treated as a sub-100M standalone model despite the report's broad abstract wording.[^paddleocr3-report]

## Relationships

- **Part of:** [PaddleOCR 3.0](paddleocr-3.md).
- **Uses:** PP-Structure parsing, vector retrieval, an interchangeable LLM, and PP-DocBee2.

[^paddleocr3-report]: Cui et al., *PaddleOCR 3.0 Technical Report*, local LaTeX source at [main.tex](../raw/2507.05595_PaddleOCR-3.0/main.tex), including `images/pp_chatocrv4_pipeline2.pdf` (accessed 2026-08-17).
