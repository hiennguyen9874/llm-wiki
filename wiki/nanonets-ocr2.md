---
type: Model System
title: Nanonets-OCR2
description: Nanonets-OCR2 is a Nanonets family of multilingual image-to-Markdown document OCR models with structured outputs for equations, tables, images, signatures, watermarks, checkboxes, and VQA.
tags: [ocr, document-parsing, vision-language-models, multilingual, structured-output]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:20:54Z }
sources:
  - id: nanonets-ocr2-model-card
    resource: ../raw/Nanonets-OCR2.md
    title: Nanonets-OCR2 model card
---

# Nanonets-OCR2

Nanonets-OCR2 is a Nanonets family of image-to-Markdown document OCR models intended to preserve document content as structured, LLM-consumable output. The retained model card lists hosted **Plus**, publicly linked **3B**, and experimental **1.5B** variants; its metadata identifies Qwen2.5-VL-3B-Instruct as the base model.[^nanonets-ocr2-model-card]

## Parsing and output contract

The card says the models support multilingual printed and handwritten documents, including English, Chinese, French, Spanish, Portuguese, German, Italian, Russian, Japanese, Korean, and Arabic. They can emit LaTeX equations, HTML or Markdown tables, Mermaid for flowcharts and organizational charts, and Unicode checkbox states (`☐`, `☑`, `☒`).[^nanonets-ocr2-model-card]

For non-textual or document-control elements, the documented prompt requests image descriptions or captions in `<img>` tags, signatures in `<signature>` tags, watermarks in `<watermark>` tags, and page numbers in `<page_number>` tags. The model card describes its visual-question-answering behavior as answering directly when the answer is present in the document and returning “Not mentioned” otherwise.[^nanonets-ocr2-model-card]

## Operation

The card provides a Transformers path using `AutoModelForImageTextToText`, `AutoTokenizer`, and `AutoProcessor`; its example loads the 3B model with automatic device placement and FlashAttention 2. It also documents serving the 3B model through vLLM and calling its OpenAI-compatible chat-completions endpoint with a base64 data-URL image.[^nanonets-ocr2-model-card]

A separate Docstrange API example posts a file to Nanonets' extraction endpoint with `output_type` set to `markdown`; the example uses an API-key placeholder, not a usable key. For table-heavy financial documents, the card recommends its `markdown-financial-docs` option, HTML table output, and trying `repetition_penalty=1`. It also states that greater image resolution improves performance and that optimal resolution can vary by document type.[^nanonets-ocr2-model-card]

## Reported evaluation

The following are model-card claims, not independently reproduced results:[^nanonets-ocr2-model-card]

- In its Markdown-comparison tables, Plus has a 34.35% win rate and 57.60% loss rate against Gemini 2.5 Flash (no thinking); the 3B model has 39.98% and 52.43%, respectively. The card does not define the comparison dataset, judging method, or rates' calculation.
- On the listed VQA datasets, Plus / 3B report 79.20 / 78.56 on ChartQA and 85.15 / 89.43 on DocVQA. The table compares these figures with Qwen2.5-VL-72B-Instruct and Gemini 2.5 Flash, but supplies no evaluation configuration or variance.

## Trust limits

- This synthesis covers the retained model card only. It links externally to weights, a demo, code, cookbooks, and a blog, none of which were retained or inspected; their contents, versions, licenses, and deployment behavior are unverified here.[^nanonets-ocr2-model-card]
- The card gives prompts and examples but no training data, architecture details beyond its base-model metadata, weights, inference source code, evaluation methodology, or reproducible result artifacts. Its capability and benchmark claims should therefore be treated as vendor-reported.[^nanonets-ocr2-model-card]

## Relationships

- **Related to:** [Multimodal OCR](multimodal-ocr.md) is another document-parsing VLM formulation with type-specific structured outputs; their reported capabilities and evaluations are not directly comparable without matched conditions.

[^nanonets-ocr2-model-card]: Nanonets, [Nanonets-OCR2 model card](../raw/Nanonets-OCR2.md) (accessed 2026-08-17).