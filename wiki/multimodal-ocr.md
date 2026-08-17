---
type: Model System
title: Multimodal OCR
description: Multimodal OCR (MOCR) is a 3B document-parsing VLM formulation that produces ordered text, table, formula, and SVG representations for information-bearing page elements.
tags: [ocr, document-parsing, vision-language-models, svg, structured-output]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:01:23Z }
sources:
  - id: multimodal-ocr-paper
    resource: ../raw/2603.13032_MultimodalOCR/main.tex
    title: "Multimodal OCR: Parse Anything from Documents"
  - id: dots-mocr-model-card
    resource: ../raw/dots.mocr.md
    title: dots.mocr model card
---

# Multimodal OCR

Multimodal OCR (MOCR) broadens document parsing from text extraction to ordered, type-specific representations of information-bearing elements. Its authors' 3B-parameter implementation, **dots.mocr**, emits text, table markup, LaTeX, or SVG as appropriate; graphics with no concise programmatic description remain raster content.[^multimodal-ocr-paper]

## Formulation and release boundary

For a page image, MOCR represents the parse as an ordered sequence of elements, each with a region, semantic category, and type-specific payload. Reading order and structural hierarchy are encoded by sequence order and delimiters rather than a separate relation module. Text regions receive transcriptions, tables receive markup, formulas receive LaTeX, and eligible charts, icons, diagrams, and UI components receive renderable SVG.[^multimodal-ocr-paper]

The paper describes MOCR as a unified formulation, but states that the current release is task-conditioned: complete page text parsing and region-level image-to-SVG decoding run in separate passes, not as one joint full-page output.[^multimodal-ocr-paper]

## Architecture and training

The stated architecture combines a 1.2B-parameter high-resolution vision encoder trained from scratch, a lightweight multimodal connector, and a Qwen2.5-1.5B base-language-model decoder. The encoder accepts inputs up to about 11 million pixels; together the components form a 3B-parameter model.[^multimodal-ocr-paper]

Training uses three pretraining stages: vision-language interface training; broad general-vision plus text-document parsing; then a mixture shifted toward MOCR and image-to-SVG targets with progressively higher input resolution. Instruction tuning uses curated data, with SVG target canonicalization, `viewBox` normalization, and complexity reduction in the data engine. The `dots.mocr-svg` checkpoint shares pretraining but increases the SVG proportion and weights harder SVG programs during supervised fine-tuning.[^multimodal-ocr-paper]

The described data engine draws on auto-labeled PDF pages, rendered webpages with HTML/DOM signals, native SVG image-code pairs, and general-purpose vision/OCR data. SVG processing uses SVGO cleanup, code- and rendered-image-level deduplication, domain balancing, and complexity-aware sampling.[^multimodal-ocr-paper]

## Release operation and output contract

The model card recommends vLLM serving and states that Dots OCR is officially integrated from vLLM 0.11.0. Its documented server commands load either `rednote-hilab/dots.mocr` or `rednote-hilab/dots.mocr-svg` with remote custom code enabled; a Transformers path likewise uses remote custom code, `qwen-vl-utils`, and a CUDA-capable bfloat16 configuration. The card warns that local model directories must temporarily avoid periods in their names pending Transformers integration.[^dots-mocr-model-card]

The bundled parser accepts a single image or PDF and supports all-layout parsing, layout-only detection, and text-only extraction; the card describes a Transformers mode as slower than its vLLM-based path. For all-layout parsing, its documented artifacts are a JSON file of bounding boxes, element categories, and extracted text; concatenated Markdown; an alternate Markdown output that removes page headers and footers; and an annotated input image. It specifies Markdown for ordinary text, LaTeX for formulas, HTML for tables, and no text field for picture regions.[^dots-mocr-model-card]

## Reported evaluation

All results below are author-reported, not independently reproduced:[^multimodal-ocr-paper]

- On olmOCR-Bench, dots.mocr reports **83.9 ± 0.9** overall, compared in the table with 82.5 for Infinity-Parser 7B, 82.4 for olmOCR v0.4.0, and 80.0 for PaddleOCR-VL. It also reports OmniDocBench v1.5 TextEdit **0.031** and ReadOrderEdit **0.029** (lower is better).
- Under the paper's [OCR Arena](ocr-arena.md) protocol, dots.mocr has mean Elo scores of **1104.4**, **1059.0**, and **1210.7** on olmOCR-Bench, OmniDocBench v1.5, and XDocParse respectively; Gemini 3 Pro is higher in each comparison table.
- For SVG reconstruction, dots.mocr-svg reports ISVGEN scores of **0.902** on UniSVG, **0.905** on ChartMimic, **0.834** on Design2Code, **0.800** on GenExam, **0.797** on SciGen, and **0.901** on ChemDraw. The paper compares these with Gemini 3 Pro and OCRVerse where scores are available.

## Trust limits

- The locally retained sources contain an author manuscript, model card, bibliography, and figures, but no weights, data, inference code, full training configuration, generated outputs, battle records, or evaluation code. The model card links to external weights and repository code, but those artifacts were not retained or inspected here; their contents and versions are therefore unverified.[^multimodal-ocr-paper][^dots-mocr-model-card]
- Benchmark and cross-model comparisons depend on rendering, prompts, metric implementations, and model versions. The OCR Arena results are additionally conditional on its judge prompt and protocol; they are not an independent general ranking.[^multimodal-ocr-paper]
- The paper's qualitative-example figures establish the authors' intended task coverage but do not quantify reliability by graphic class. This compilation visually reviewed the overview, metric, OCR-Arena prompt, and judge-example attachments; remaining qualitative figures were covered from their source captions rather than independently assessed.

## Relationships

- **Evaluated with:** [OCR Arena](ocr-arena.md), the source's pairwise LLM-judge protocol for Markdown OCR outputs.
- **Compared with:** [PaddleOCR-VL](paddleocr-vl.md) and [DeepSeek-OCR](deepseek-ocr.md) are document-parsing VLMs with different output decompositions; source-reported rankings require matched evaluation conditions for comparison.

[^multimodal-ocr-paper]: Zheng et al., *Multimodal OCR: Parse Anything from Documents*, local LaTeX source at [main.tex](../raw/2603.13032_MultimodalOCR/main.tex), including visually reviewed `Fig/Figure_main.pdf`, `Fig/Figure_metric.pdf`, `Fig/Prompt.pdf`, and `Fig/Judge-examples.pdf` (accessed 2026-08-17).
[^dots-mocr-model-card]: rednote-hilab, [dots.mocr model card](../raw/dots.mocr.md) (accessed 2026-08-17).