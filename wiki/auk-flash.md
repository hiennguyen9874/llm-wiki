---
type: Concept
title: AuK-Flash
description: Distilled 4-step variant of Tencent's 1.5B AuK speech generation and editing foundation model with 16 instruction-driven tasks and MIT-licensed weights.
tags: [tts, voice-cloning, speech-editing, diffusion]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:04:37Z }
sources:
  - id: auk-flash-card
    resource: ../raw/AuK-Flash.md
    kind: documentation
    title: AuK-Flash model card
---

AuK-Flash is the distilled variant of Tencent Hunyuan's 1.5B AuK speech generation and editing foundation model, performing fast 4-step inference over 16 instruction-driven tasks spanning zero-shot and instruct TTS, content, acoustic, and paralinguistic editing, plus enhancement and separation, with weights distributed for Hugging Face and ModelScope alongside a Qwen2.5-Omni-3B MLLM encoder (**Reported**).[^auk-flash-card]

## Model identity and release

- Card title is "AuK-Flash: Fast 4-Step Speech Generation and Editing"; the base model is `tencent/AuK` and the foundation model is described as a 1.5B model trained on millions of hours of diverse audio data (**Reported**).[^auk-flash-card]
- Two variants are named: AuK (base model for high-quality generation) and AuK-Flash (distilled model for fast 4-step inference); this card's repository contains the official AuK-Flash weights (**Reported**).[^auk-flash-card]
- Frontmatter declares `license: mit`, languages `zh` and `en`, `pipeline_tag: text-to-speech`, and tags including zero-shot TTS, voice cloning, speech generation, speech editing, enhancement, separation, source separation, instruction-guided, diffusion, distillation, and few-step inference (**Reported**).[^auk-flash-card]
- News entry dated 2026/09/09 announces AuK as open-source with code and weights public and links to Hugging Face and ModelScope demo spaces (**Reported**).[^auk-flash-card]
- Canonical upstream entry points are the [AuK-Flash Hugging Face repo](https://huggingface.co/tencent/AuK-Flash) and the [AuK-Flash ModelScope repo](https://modelscope.cn/models/Tencent-Hunyuan/AuK-Flash); the card also links the AuK base repos, the Qwen2.5-Omni-3B encoder, the Tencent-Hunyuan/AuK GitHub repo, the cookbook, the project website, the demo spaces, and arXiv paper 2609.08936 (**Reported**).[^auk-flash-card]
- Research use cites the AuK technical report (Ma et al., 2026, arXiv:2609.08936, `cs.SD`) via the card's BibTeX entry; the model is released under the MIT License with full terms in the referenced `LICENSE` (**Reported**).[^auk-flash-card]

## Task taxonomy

- All tasks are exposed through the same natural-language instruction interface; the card groups 16 tasks into five categories and points each to a cookbook section with instruction templates plus CLI and Python examples (**Reported**).[^auk-flash-card]

| Category | Task | Card description |
| --- | --- | --- |
| Speech Generation | Zero-shot TTS | Speak the target text in the voice of the reference audio. |
| Speech Generation | Instruct TTS | Generate speech from a voice description alone — no reference audio. |
| Content Editing | Speech Content Editing | Rewrite what is said — replace, insert, or remove text. |
| Content Editing | Lyric Editing | Rewrite lyrics in a singing recording while preserving melody and voice. |
| Acoustic Editing | Pitch Editing | Raise or lower the pitch by semitones. |
| Acoustic Editing | Speed Editing | Adjust the speaking rate; output length scales with the speed factor. |
| Acoustic Editing | Volume Editing | Raise or lower the volume by decibels. |
| Paralinguistic Editing | Emotion | Change the emotion while preserving content and voice. |
| Paralinguistic Editing | Timbre | Change the timbre to a description while keeping content unchanged. |
| Paralinguistic Editing | De-accent | Remove a regional accent while preserving speaker voice and content. |
| Paralinguistic Editing | Nonverbal Editing | Remove or add nonverbal sounds such as breaths, laughs, or coughs. |
| Paralinguistic Editing | Whisper Conversion | Convert between normal speech and whisper while preserving speaker and content. |
| Enhancement & Separation | Speech Enhancement | Denoise, dereverberate, or restore natural, clear speech. |
| Enhancement & Separation | Speech Separation | Keep one speaker by talking order and remove the others. |
| Enhancement & Separation | Music Separation | Extract the singing voice from a mix, or keep all human voices. |
| Enhancement & Separation | Target Speaker Extraction | Keep the target speaker identified by what they say. |

Table content reproduces the card's Supported Tasks table without its external cookbook links (**Reported**).[^auk-flash-card]

## Weights and runtime layout

- Hugging Face download commands fetch `tencent/AuK` into `./ckpts/AuK`, `tencent/AuK-Flash` into `./ckpts/AuK-Flash`, and `Qwen/Qwen2.5-Omni-3B` into `./ckpts/Qwen2.5-Omni-3B`; ModelScope commands fetch the corresponding `Tencent-Hunyuan/AuK`, `Tencent-Hunyuan/AuK-Flash`, and `Qwen/Qwen2.5-Omni-3B` models into the same layout (**Reported**).[^auk-flash-card]
- The model checkpoint contains the diffusion transformer and layer-fusion weights; the MLLM encoder and VAE load from separate files at runtime, so missing `text_encoder.*` keys during checkpoint loading are expected (**Reported**).[^auk-flash-card]
- Installation, inference, Gradio, ComfyUI, and fine-tuning are delegated to the linked GitHub README quick-start and cookbook rather than documented in the card (**Reported**).[^auk-flash-card]

## Coverage and limits

- Source inspected statically only; no commands executed, no weights downloaded, and no inference reproduced (**Synthesis**).[^auk-flash-card]
- The performance figure (`assets/performance.png`) and architecture figure (`assets/arch.png`) are referenced by image tags but absent from `raw/`, so no benchmark numbers or architectural detail beyond the captions were extracted (**Synthesis**).[^auk-flash-card]
- Linked external guides, cookbook, upstream model pages, demo assets, paper text, and the `LICENSE` file were not fetched and are not covered (**Synthesis**).[^auk-flash-card]
- All capability, training-data, variant, and download claims are source assertions without independent verification in this wiki (**Synthesis**).[^auk-flash-card]

## Relationships

- Base model described in [AuK](auk.md), which covers the official 1.5B base weights, the shared 16-task instruction interface, and SGLang-Omni serving (**Synthesis**).[^auk-flash-card]
- Packaged for local execution by [AuK Base and Flash GGUF](auk-base-and-flash-gguf.md), which converts the upstream AuK and AuK-Flash weights into audio.cpp GGUF components with variant-selection flags and a 16-task C++/Python parity report (**Synthesis**).[^auk-flash-card]

[^auk-flash-card]: [AuK-Flash model card](../raw/AuK-Flash.md) — locators: frontmatter (`license`, `language`, `pipeline_tag`, `tags`, `base_model`); `div` title block; section `News` (2026/09/09 open-source entry); section `Introduction` (1.5B, millions of hours, capability list, two-row variant table, Flash-weights scope sentence); section `Performance` (image tag `assets/performance.png`, no extractable numbers); section `Model Architecture` (image tag `assets/arch.png`); section `Supported Tasks` (5-category, 16-row HTML table with task descriptions and cookbook links); section `Download the weights` (Hugging Face and ModelScope code fences, `ckpts/` tree, diffusion-transformer plus layer-fusion note, `text_encoder.*` note, README/cookbook pointer); section `Citation` (BibTeX `ma2026auktechnicalreportopensource`); section `License` (MIT, `LICENSE` reference). Referenced `assets/` images and `LICENSE` have no locator available in `raw/` (files absent).
