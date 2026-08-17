---
type: Model System
title: HunyuanOCR-1.5
description: HunyuanOCR-1.5 is a lightweight end-to-end OCR VLM with DFlash speculative decoding, multiple inference stacks, and an agentic data-construction workflow.
tags: [ocr, document-parsing, vision-language-models, speculative-decoding, multilingual, data-curation]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:06:36Z }
sources:
  - id: hunyuanocr-1-5-model-card
    resource: ../raw/HunyuanOCR-1.5.md
    title: "HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better"
---

# HunyuanOCR-1.5

HunyuanOCR-1.5 is a lightweight, end-to-end OCR-focused vision-language model for document parsing, text spotting, information extraction, and text-image translation. The authors retain the HunyuanOCR-1.0 backbone but report upgrades to decoding, deployment, data construction, and training for faster long structured outputs and broader long-tail coverage.[^hunyuanocr-1-5-model-card]

## Decoding and deployment

For dense documents and other long outputs, the supplied DFlash configuration uses a lightweight block-diffusion draft model to propose multiple tokens in parallel; the target model verifies them in one pass. The model card says this speculative procedure preserves the target model's output distribution while reducing decoding latency, but supplies no latency or acceptance-rate measurements.[^hunyuanocr-1-5-model-card]

The same base weights are presented for native Hugging Face Transformers, vLLM's OpenAI-compatible server, and GGUF conversion for `llama.cpp`. The DFlash draft weights occupy a `dflash/` subdirectory; the card also points to a DFlash-adapted `llama.cpp` fork. HunyuanOCR-1.0 is an archived checkpoint in `v1.0/`, rather than the root model.[^hunyuanocr-1-5-model-card]

The documented unified inference environment requires CUDA 13 and supports vLLM autoregressive decoding, vLLM DFlash decoding, and Transformers. The PC-oriented `llama.cpp` path supports CPU, consumer GPU, or laptop deployment; the standard community build is base-model-only, while the cited fork supports DFlash.[^hunyuanocr-1-5-model-card]

## Tasks and operation

The vLLM client exposes document parsing, structured parsing, two text-spotting formats, layout and layout parsing, chart, formula, and table parsing, plus Chinese/English and other-language translation task types. It uses task-specific prompts, deterministic sampling settings, and optional streaming early-stop and document-parse post-processing.[^hunyuanocr-1-5-model-card]

For document parsing, the supplied Chinese prompt requests reading-order Markdown, excludes headers and footers, represents tables as HTML, and represents formulas as LaTeX. The model card also permits task-specific natural-language instructions for spotting, extraction, and translation.[^hunyuanocr-1-5-model-card]

## Training and data construction

The authors call their data-construction process **Agentic Data Flow**: agents translate observed model weaknesses into executable data requirements, participate in material search, tool-based verification, sample cleaning, and pipeline development, and iterate with algorithm engineers. They report applying it to low-resource OCR, ancient-script OCR, and multi-image text-centric question answering.[^hunyuanocr-1-5-model-card]

The described training changes re-plan Stage-3 pretraining around the new capability data, multi-image data, and historical OCR data; raise maximum image resolution to 4K and the context window to 128K; refine SFT; and explore reinforcement learning across OCR tasks. The source does not specify datasets, model sizes, training volumes, reward definitions, or measured contributions of these changes.[^hunyuanocr-1-5-model-card]

## Scope and trust limits

This local source is a model card, not the linked paper, repository, weights, or license text. It contains no benchmark results, hardware-normalized latency figures, draft-model acceptance data, architecture specification, or independent reproduction. Its claims about output-distribution preservation, accuracy alignment across inference stacks, and capability improvements are therefore author assertions not verifiable from this bundle.[^hunyuanocr-1-5-model-card]

The card embeds a teaser image at `assets/HyOCR_1_5_teaser.png`, but that attachment is absent from the local `raw/` directory; this synthesis does not rely on its visual content.[^hunyuanocr-1-5-model-card]

## Relationships

- **Related to:** [Document-parser data flywheel](document-parser-data-flywheel.md), as both start from model weaknesses and construct targeted training data; the HunyuanOCR source does not describe the same acquisition or evaluation controls.[^hunyuanocr-1-5-model-card]

[^hunyuanocr-1-5-model-card]: Tencent Hunyuan, *HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better*, local model card at [HunyuanOCR-1.5.md](../raw/HunyuanOCR-1.5.md) (accessed 2026-08-17).