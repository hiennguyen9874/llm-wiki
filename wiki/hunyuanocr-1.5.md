---
type: Model System
title: HunyuanOCR-1.5
description: HunyuanOCR-1.5 is a lightweight end-to-end OCR VLM with DFlash speculative decoding, multiple inference stacks, and an agentic data-construction workflow.
tags: [ocr, document-parsing, vision-language-models, speculative-decoding, multilingual, data-curation]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:24:26Z }
sources:
  - id: hunyuanocr-1-5-model-card
    resource: ../raw/HunyuanOCR-1.5.md
    title: "HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better"
  - id: hunyuanocr-repo-readme
    resource: ../raw/HunyuanOCR-github.md
    kind: code
    title: "HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better (GitHub repository README)"
---

# HunyuanOCR-1.5

HunyuanOCR-1.5 is a lightweight, end-to-end OCR-focused vision-language model for document parsing, text spotting, information extraction, and text-image translation. The authors retain the HunyuanOCR-1.0 backbone but report upgrades to decoding, deployment, data construction, and training for faster long structured outputs and broader long-tail coverage.[^hunyuanocr-1-5-model-card]

## Decoding and deployment

For dense documents and other long outputs, the supplied DFlash configuration uses a lightweight block-diffusion draft model to propose multiple tokens in parallel; the target model verifies them in one pass. The model card says this speculative procedure preserves the target model's output distribution while reducing decoding latency, but supplies no latency or acceptance-rate measurements.[^hunyuanocr-1-5-model-card]

The same base weights are presented for native Hugging Face Transformers, vLLM's OpenAI-compatible server, and GGUF conversion for `llama.cpp`. The DFlash draft weights occupy a `dflash/` subdirectory; the card also points to a DFlash-adapted `llama.cpp` fork. HunyuanOCR-1.0 is an archived checkpoint in `v1.0/`, rather than the root model.[^hunyuanocr-1-5-model-card]

The documented unified inference environment requires CUDA 13 and supports vLLM autoregressive decoding, vLLM DFlash decoding, and Transformers. The PC-oriented `llama.cpp` path supports CPU, consumer GPU, or laptop deployment; the model card describes a DFlash-adapted `llama.cpp` fork alongside the standard build, while the later repository README reports that fork support has since been absorbed upstream.[^hunyuanocr-1-5-model-card][^hunyuanocr-repo-readme]

## Tasks and operation

The vLLM client exposes document parsing, structured parsing, two text-spotting formats, layout and layout parsing, chart, formula, and table parsing, plus Chinese/English and other-language translation task types. It uses task-specific prompts, deterministic sampling settings, and optional streaming early-stop and document-parse post-processing.[^hunyuanocr-1-5-model-card]

For document parsing, the supplied Chinese prompt requests reading-order Markdown, excludes headers and footers, represents tables as HTML, and represents formulas as LaTeX. The model card also permits task-specific natural-language instructions for spotting, extraction, and translation.[^hunyuanocr-1-5-model-card]

## Training and data construction

The authors call their data-construction process **Agentic Data Flow**: agents translate observed model weaknesses into executable data requirements, participate in material search, tool-based verification, sample cleaning, and pipeline development, and iterate with algorithm engineers. They report applying it to low-resource OCR, ancient-script OCR, and multi-image text-centric question answering.[^hunyuanocr-1-5-model-card]

The described training changes re-plan Stage-3 pretraining around the new capability data, multi-image data, and historical OCR data; raise maximum image resolution to 4K and the context window to 128K; refine SFT; and explore reinforcement learning across OCR tasks. The source does not specify datasets, model sizes, training volumes, reward definitions, or measured contributions of these changes.[^hunyuanocr-1-5-model-card]

## Release history and team artefacts

The repository README's `News` section dates the 1.5 release to 2026/07/07 and attributes it to four changes: DFlash speculative decoding, PC-side `llama.cpp` deployment, Agentic Data Flow, and an upgraded training recipe. It then records three later releases: **CHAOS-Bench** on 2026/07/13, described as a character-level hallucination benchmark that probes "seeing-is-believing" behavior by injecting character-level corruptions into academic-paper images; and, on 2026/07/24, the unified inference environment and a verl-based reinforcement-learning stack. The 2026/04–06 entries instead announce team papers and benchmarks accepted or released at CVPR 2026 and ECCV 2026 — document parsing, text-image machine translation, StrucTab for table parsing, Chronicles-OCR for historical scripts, ChartArena for charts, Wild-OmniDocBench, and MMTIT-Bench. These are related team artefacts rather than HunyuanOCR-1.5 model results, and none of them is present locally.[^hunyuanocr-repo-readme]

The README's `License` section states that HunyuanOCR-1.5 carries the same Tencent Hunyuan Community License Agreement as HunyuanOCR-1.0, with terms in `LICENSE`. That file is not in the local bundle, so redistribution and commercial-use conditions remain unverified here.[^hunyuanocr-repo-readme]

## Deployment status update

The model card and the repository README describe the same `llama.cpp` situation at different dates. The card offers a DFlash-adapted fork because the standard community build was base-model-only. The README's 2026/07/24 news and its `PC-side deployment via llama.cpp` section then state that HunyuanOCR DFlash speculative decoding was merged into upstream `llama.cpp` (PR #28890, build `b11103` and later) and that "no fork is needed", since upstream `master` serves both the base model and the draft. Read as a dated update, the later author statement replaces the fork arrangement rather than contradicting it; neither statement is independently verified here, and the cited PR and build notes are external to the bundle.[^hunyuanocr-1-5-model-card][^hunyuanocr-repo-readme]

## Scope and trust limits

This local source is a model card, not the linked paper, repository, weights, or license text. It contains no benchmark results, hardware-normalized latency figures, draft-model acceptance data, architecture specification, or independent reproduction. Its claims about output-distribution preservation, accuracy alignment across inference stacks, and capability improvements are therefore author assertions not verifiable from this bundle.[^hunyuanocr-1-5-model-card]

The card embeds a teaser image at `assets/HyOCR_1_5_teaser.png`, but that attachment is absent from the local `raw/` directory; this synthesis does not rely on its visual content.[^hunyuanocr-1-5-model-card]

The second local source, the GitHub repository README, is largely the same introduction and model description as the card, plus operation and maintenance material. It likewise carries no benchmark table, latency measurement, draft acceptance rate, architecture specification, or independent reproduction, and the pages it defers to for those details are not in the bundle. Its release dates and its upstream-merge claim are therefore single-source author assertions.[^hunyuanocr-repo-readme]

## Relationships

- **Uses:** [HunyuanOCR-1.5 training and inference stack](hunyuanocr-training-and-inference-stack.md) for the documented packing, SFT, DFlash draft training, and deployment procedures.[^hunyuanocr-repo-readme]
- **Related to:** [Document-parser data flywheel](document-parser-data-flywheel.md), as both start from model weaknesses and construct targeted training data; the HunyuanOCR source does not describe the same acquisition or evaluation controls.[^hunyuanocr-1-5-model-card]

[^hunyuanocr-1-5-model-card]: Tencent Hunyuan, *HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better*, local model card at [HunyuanOCR-1.5.md](../raw/HunyuanOCR-1.5.md), locators are the `Introduction`, `Model layout` note, and inference paragraphs (accessed 2026-08-17).
[^hunyuanocr-repo-readme]: Tencent Hunyuan, *HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better* (GitHub repository README), local capture at [HunyuanOCR-github.md](../raw/HunyuanOCR-github.md), locators are the README sections `News`, `Introduction`, `Inference`, `PC-side deployment via llama.cpp`, and `License` (accessed 2026-10-25).