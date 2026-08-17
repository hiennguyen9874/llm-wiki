---
type: Model System
title: NVIDIA Nemotron Parse v1.1
description: NVIDIA Nemotron Parse v1.1 is a sub-1B vision-encoder–decoder document parser that emits reading-order text, element classes, and bounding boxes from an image.
tags: [ocr, document-parsing, vision-language-models, layout-analysis, table-extraction, spatial-grounding]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:29:48Z }
sources:
  - id: nemotron-parse-v1-1-model-card
    resource: ../raw/NVIDIA-Nemotron-Parse-v1.1.md
    title: NVIDIA Nemotron Parse v1.1 model card
---

# NVIDIA Nemotron Parse v1.1

NVIDIA Nemotron Parse v1.1 is a Transformer vision-encoder–decoder model for document-image parsing. Given an RGB image and a task prompt, it produces a reading-order string that encodes text, semantic element classes, and bounding boxes; the documented default renders text as Markdown, equations as LaTeX or Markdown, and tables as LaTeX.[^nemotron-parse-v1-1-model-card]

## Architecture and interface

The card describes a ViT-H vision encoder initialized from NVIDIA C-RADIO, followed by a 1D-convolution-and-normalization adapter that reduces the latent sequence from 13,184 to 3,201 tokens, then a 10-block mBART decoder. It reports fewer than 1 billion parameters.[^nemotron-parse-v1-1-model-card]

The documented input is an RGB image plus a string prompt. Supported image dimensions are stated as 1,024–1,648 pixels wide and 1,280–2,048 pixels high. The default prompt, `</s><s><predict_bbox><predict_classes><output_markdown>`, requests text, classes, and boxes; `output_no_text` omits transcription. The reported classes are title, section, caption, index, footnote, lists, tables, bibliography, and image.[^nemotron-parse-v1-1-model-card]

The provided postprocessing API separates generated classes, boxes, and text; maps boxes back to original image coordinates; and converts table and text output to configurable LaTeX, HTML, Markdown, or plain-text forms.[^nemotron-parse-v1-1-model-card]

## Deployment

The card documents Transformers inference with `trust_remote_code=True` and BF16 on CUDA, naming Transformers 4.51.3 as the pinned reference environment and stating that its remote code was tested through Transformers 5.6.2 with golden-output compatibility. It also documents TensorRT-LLM and vLLM operation, including vLLM 0.20.1 validation, the `vllm/vllm-openai:v0.14.1` image, and a Triton-attention recommendation for A100 and A10 hardware.[^nemotron-parse-v1-1-model-card]

The listed target operating system is Linux and listed GPU microarchitectures are Turing, Ampere, and Hopper. The card describes a NIM container, while the model itself is governed by the NVIDIA Open Model License and its tokenizer by CC-BY-4.0; it states the container has separate NVIDIA software and product-specific terms. Confirm the applicable terms from the linked agreements before use.[^nemotron-parse-v1-1-model-card]

## Training and reported compute

The source says pretraining used internal human, synthetic, and automated text-and-image datasets, and evaluation used public and internal datasets, but does not identify their contents, licenses, sizes, splits, or results. It reports cumulative training compute of $2.2\times10^{22}$, 7,827.46 kWh estimated energy consumption, and 3.21 tCO2e estimated carbon emissions.[^nemotron-parse-v1-1-model-card]

## Scope and trust limits

The card positions the model for PDF and PowerPoint text extraction, layout classification, spatial grounding, retriever and curator applications, and LLM/VLM training-data generation. These are vendor claims, not independently validated capability or quality evidence.[^nemotron-parse-v1-1-model-card]

The local source is a model card rather than the cited technical report. It provides no weights, source code, datasets, benchmark configurations, evaluation metrics, or reproducible results. Its locally referenced `layout.png`, `tables.png`, and `equations.png` example images are absent, and the referenced `chat_template.jinja` is also absent; none were inspected. The card's frontmatter identifies `nvidia/NVIDIA-Nemotron-Parse-v1.2` as a newer version, but that version's source is not present in this bundle, so no supersession or capability comparison is established here.[^nemotron-parse-v1-1-model-card]

[^nemotron-parse-v1-1-model-card]: NVIDIA, [*NVIDIA Nemotron Parse v1.1 model card*](../raw/NVIDIA-Nemotron-Parse-v1.1.md) (accessed 2026-08-17). Referenced local `layout.png`, `tables.png`, `equations.png`, and `chat_template.jinja` are absent and were not inspected.
