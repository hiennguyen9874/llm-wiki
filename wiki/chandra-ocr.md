---
type: Model System
title: Chandra OCR
description: Chandra OCR is Datalab's earlier document-OCR model for converting images and PDFs to Markdown, HTML, or JSON with layout information.
tags: [ocr, document-parsing, vision-language-models, multilingual, markdown, html, json]
status: deprecated
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:00:21Z }
sources:
  - id: chandra-model-card
    resource: ../raw/chandra.md
    title: Chandra model card
---

# Chandra OCR

Chandra OCR is Datalab's earlier document-OCR model for converting images and PDFs to Markdown, HTML, or JSON with layout information. Its model card identifies [Chandra OCR 2](chandra-ocr-2.md) as the new version, so this concept is retained as deprecated predecessor history.[^chandra-model-card]

## Document parsing capabilities

The model card claims support for handwriting, form reconstruction including checkboxes, tables, mathematical content, complex layouts, image and diagram extraction with captions and structured data, and more than 40 languages.[^chandra-model-card]

The documented CLI installs as `chandra-ocr`; local inference can use `chandra_vllm` followed by `chandra input.pdf ./output`, or a Hugging Face method selected with `--method hf`. The Python examples use `InferenceManager(method="vllm")` or `generate_hf` with the `datalab-to/chandra` checkpoint.[^chandra-model-card]

## Reported evaluation

The model card reports an **83.1 ± 0.9** overall score for Datalab Chandra v0.1.0 in its olmOCR benchmark table. The table labels this as an own-benchmark result; some comparator results are attributed to their respective repositories.[^chandra-model-card]

## Supersession

Superseded by [Chandra OCR 2](chandra-ocr-2.md) on or before 2026-08-17; the source's `new_version` metadata names `datalab-to/chandra-ocr-2`.[^chandra-model-card]

## Trust limits

This local source is a vendor model card rather than an independently reviewed report. It does not locally provide model architecture, parameter count, training-data details, weights, or sufficient evaluation methodology to reproduce its claims. The referenced `bench.png` and `handwritten_form.png` files are absent from `raw/`, so their visual content was not inspected; the textual benchmark table was available.[^chandra-model-card]

[^chandra-model-card]: Datalab, *Chandra model card*, local [chandra.md](../raw/chandra.md) (accessed 2026-08-17).
