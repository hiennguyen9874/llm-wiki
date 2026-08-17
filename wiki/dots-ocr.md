---
type: Model System
title: dots.ocr
description: dots.ocr is a 1.7B multilingual document-parsing vision-language model that uses prompts to produce layout detection, content recognition, and reading-order outputs.
tags: [ocr, document-parsing, vision-language-models, multilingual, layout-analysis]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:02:27Z }
sources:
  - id: dots-ocr-model-card
    resource: ../raw/dots.ocr.md
    title: "dots.ocr model card"
---

# dots.ocr

dots.ocr is an author-described multilingual document parser built on a 1.7B-parameter LLM foundation. One vision-language model performs layout detection and content recognition; task selection is prompt-driven, and its all-layout response is ordered by intended human reading order.[^dots-ocr-model-card]

## Output contract and operation

The documented all-layout prompt requests an individual bounding box, category, and source-language content for each page element. It defines eleven categories: Caption, Footnote, Formula, List-item, Page-footer, Page-header, Picture, Section-header, Table, Text, and Title. Formulas are emitted as LaTeX, tables as HTML, ordinary textual categories as Markdown, and pictures omit a text field; the complete response is one JSON object.[^dots-ocr-model-card]

The supplied parser accepts an image or PDF. It supports all-layout parsing, layout-only detection, text-only extraction that excludes headers and footers, and OCR grounding within a supplied bounding box. The documented artifacts are detected-element JSON, concatenated Markdown (with a header/footer-free variant), and a visualization with detected boxes.[^dots-ocr-model-card]

The card recommends vLLM 0.9.1 for serving and reports its evaluations on that version. Its vLLM and Transformers examples require remote custom code; the latter also uses CUDA, bfloat16, FlashAttention 2, and `qwen-vl-utils`. At the source's publication, a model-directory name without periods was a temporary workaround for Transformers integration.[^dots-ocr-model-card]

## Reported evaluation

The following values are author-reported, not independently reproduced:[^dots-ocr-model-card]

- On OmniDocBench end-to-end evaluation, dots.ocr reports overall edit scores of **0.125** (English) and **0.160** (Chinese); its table lists its text, table, and reading-order results as the lowest error values among the included systems, while other systems lead formula metrics in one or both languages.
- On the source's internal `dots.ocr-bench`—1,493 PDF images across 100 languages—it reports overall edit **0.177**, text edit **0.075**, formula edit **0.297**, table TEDS **79.2**, table edit **0.186**, and reading-order edit **0.152**.
- On olmOCR-bench, it reports **79.1 ± 1.0** overall. The source table's comparisons depend on its selected systems, preprocessing, prompts, and evaluation pipelines.

## Limitations and trust limits

The authors identify high-complexity tables and formula extraction as imperfect, state that the model does not currently parse picture contents, and do not claim high-throughput large-PDF processing is optimized. They advise increasing PDF parsing resolution to 200 DPI for a high character-to-pixel ratio while keeping images below 11,289,600 pixels for best results; long runs of ellipses or underscores can cause repetitive generation, for which the card suggests alternative task prompts.[^dots-ocr-model-card]

This local source is a model card with code snippets and author-reported tables, but it does not include weights, repository code, data, evaluation code, complete prompts beyond the example, inference outputs, or independent tests. Its linked screenshots and charts are external URLs, so they were not locally inspected. Reported performance, deployment compatibility, and limitations should therefore be treated as source claims rather than independently verified behavior.[^dots-ocr-model-card]

## Relationships

- **Compared with:** [Multimodal OCR](multimodal-ocr.md)'s dots.mocr, MonkeyOCR-pro-3B, and other OCR systems in the source's author-run benchmark tables; the different model versions, prompts, preprocessing, and benchmarks prevent a general causal ranking.[^dots-ocr-model-card]

[^dots-ocr-model-card]: rednote-hilab, [dots.ocr model card](../raw/dots.ocr.md) (accessed 2026-08-17).
