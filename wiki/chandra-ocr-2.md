---
type: Model System
title: Chandra OCR 2
description: Chandra OCR 2 is a Datalab document-OCR model that converts images and PDFs to Markdown, HTML, or JSON with layout information.
tags: [ocr, document-parsing, vision-language-models, multilingual, markdown, html, json]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-10-30T03:30:00Z }
sources:
  - id: chandra-ocr-2-model-card
    resource: ../raw/chandra-ocr-2.md
    title: Chandra OCR 2 model card
  - id: chandra-model-card
    resource: ../raw/chandra.md
    title: Chandra model card
  - id: chandra-bench-img
    resource: ../raw/ocr-benchmark-assets-2026-10-30/chandra-bench.png
    kind: figure
    title: Chandra OCR 2 olmOCR benchmark chart
  - id: chandra-full-bench
    resource: ../raw/ocr-benchmark-assets-2026-10-30/chandra-full-benchmarks.md
    kind: article
    title: Chandra 2 full 90-language benchmark
---

# Chandra OCR 2

Chandra OCR 2 is Datalab's document-OCR model for converting images and PDFs to Markdown, HTML, or JSON with layout information. The supplied model card presents vLLM as the recommended local inference path and also documents Hugging Face Transformers inference.[^chandra-ocr-2-model-card]

## Document parsing capabilities

The model card claims support for handwriting, form reconstruction including checkboxes, tables, mathematical content, complex layouts, image and diagram extraction with captions and structured data, and more than 90 languages.[^chandra-ocr-2-model-card]

The documented CLI installs as `chandra-ocr`; local inference can use `chandra_vllm` followed by `chandra input.pdf ./output`, or a Hugging Face method selected with `--method hf`. The Python examples use `InferenceManager(method="vllm")` or the `datalab-to/chandra-ocr-2` checkpoint with `AutoModelForImageTextToText` and `AutoProcessor`.[^chandra-ocr-2-model-card]

## Reported evaluation and throughput

All results in this section are vendor-reported and have not been independently reproduced:[^chandra-ocr-2-model-card]

- In the model card's olmOCR benchmark table, Chandra 2 scores **85.8 ± 0.8** overall. The table labels this as the authors' own benchmark result and lists Datalab API at 86.7 ± 0.8, dots.ocr 1.5 at 83.9, and Chandra 1 at 83.1.
- In a 43-language multilingual table, it averages **77.8%**, compared with 69.4% for Chandra 1. A separate 90-language comparison reports 72.7% for Chandra 2 and 60.8% for Gemini 2.5 Flash; the source does not provide the full methodology. The per-language 90-language table, downloaded on 2026-10-30, shows Chandra 2 ahead of Gemini 2.5 Flash on most Indic languages and on Khmer, Lao, and Burmese, but behind on Arabic (68.4% vs 84.4%), Hindi (78.4% vs 82.7%), Thai (62.6% vs 66.7%), Vietnamese (82.6% vs 89.5%), and Urdu (44.1% vs 57.6%).[^chandra-full-bench]
- A single-H100 80 GB vLLM configuration at 96 concurrent sequences reports **1.44 pages/s**, 60-second average latency, 156-second P95 latency, and no failures on the source's diverse olmOCR-benchmark document mix. The card characterizes that mix as slower than real-world usage and estimates 2 pages/s for real-world documents.

## Cross-project benchmark results

Other projects report Chandra OCR 2 on benchmarks its card omits, including OmniParseBench 90.1 (highest open-weight headline in Datalab's dataset card), MDPBench 79.7, ParseBench 70.1, and OmniDocBench v1.6 92.27 as run by MiniCPM. These are collected per dataset in [Document OCR model benchmark comparison](document-ocr-model-benchmark-comparison.md), with the Infinity-Parser2 report's conflicting 83.1 olmOCR transcription.

## Supersession

Supersedes [Chandra OCR](chandra-ocr.md) on or before 2026-08-17. The predecessor's model card identifies `datalab-to/chandra-ocr-2` as its new version.[^chandra-model-card]

## Licensing and trust limits

The source says the code is Apache 2.0 and the model weights use a modified OpenRAIL-M license. It permits research, personal use, and startups below $2M in funding or revenue, prohibits competitive use against Datalab's API, and directs broader commercial users to Datalab licensing.[^chandra-ocr-2-model-card]

This local source is a vendor model card, not an independently reviewed report. It contains no model architecture, parameter count, training-data description, weights, evaluation code, prompts, or inference configuration sufficient to reproduce the claims. Four locally referenced images—the Datalab logo, a handwriting/form example, and the benchmark figures—are absent beside the card. The two benchmark figures were later downloaded to `raw/ocr-benchmark-assets-2026-10-30/`; the olmOCR chart matches the textual table (85.8%).[^chandra-bench-img] The logo and form example remain uninspected, and the textual tables remain the basis for the reported numerical claims.[^chandra-ocr-2-model-card]

## Relationships

- **Compared in:** [Document OCR model benchmark comparison](document-ocr-model-benchmark-comparison.md), per dataset with nine other parsers.

[^chandra-ocr-2-model-card]: Datalab, *Chandra OCR 2 model card*, local [chandra-ocr-2.md](../raw/chandra-ocr-2.md) (accessed 2026-08-17).
[^chandra-bench-img]: [chandra-bench.png](../raw/ocr-benchmark-assets-2026-10-30/chandra-bench.png), olmOCR Benchmark bar chart (fetched 2026-10-30 per `manifest.json`).
[^chandra-full-bench]: Datalab, [Full 90-Language Benchmark](../raw/ocr-benchmark-assets-2026-10-30/chandra-full-benchmarks.md), § Results by Language rows `ar`, `hi`, `th`, `vi`, `ur`, `km`, `lo`, `my` and Indic-language rows (fetched 2026-10-30).
[^chandra-model-card]: Datalab, *Chandra model card*, local [chandra.md](../raw/chandra.md) (accessed 2026-08-17).
