---
type: Concept
title: Qwen3.8-27B Community Variants
description: Community GGUF, MLX, AWQ, NVFP4 and speculative-decoding variants for Qwen3.8-27B curated by QwenDevs two weeks after release.
tags: [qwen3.8, gguf, mlx, awq, nvfp4, speculative-decoding, community, dspark, dflash]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T07:14:26Z }
sources:
  - id: qwen-community
    resource: ../raw/2093175583286968499/index.md
    title: 'Post by @QwenDevs on X'
---

Two weeks after release, the Qwen team curated community builds around `Qwen3.8-27B` — GGUF, MLX, AWQ and NVFP4 quantizations plus faster-inference approaches — selected for Hugging Face and ModelScope download heat, organization footprint, and technical-route representativeness[^qwen-community].

## Local-use variants

- Unsloth AI: Dynamic 3.0 GGUFs plus NVFP4 and FP8 builds, all with the MTP head intact, for running in llama.cpp, LM Studio and Unsloth Desktop[^qwen-community].
- LM Studio community: GGUF plus MLX 4–8-bit builds from the LM Studio team, for local use on Mac and PC[^qwen-community].
- cyankiwi: 21GB AWQ-INT4 built on a custom STEM plus agentic calibration set covering 10 languages[^qwen-community].
- ggml-org: GGUF conversion published by the llama.cpp team, generated with `ggml-org/convert`[^qwen-community].
- AtomicChat: imatrix GGUFs built on fully public calibration corpora[^qwen-community].
- bartowski: llama.cpp imatrix GGUF quants with multimodal (`mmproj`) and MTP support[^qwen-community].
- mlx-community: MLX builds (4/8-bit, MTP variants) for Apple Silicon[^qwen-community].

## Serving and faster-inference variants

- RadixArk: NVFP4 W4A4 quant produced with NVIDIA Model Optimizer, plus DSpark, a 1.36B speculative-decoding speculator with a reported ~3.4 mean acceptance length on SGLang[^qwen-community].
- Inferact: NVFP4 quant of Qwen3.8-27B[^qwen-community].
- incoai × z-lab: DFlash2, a block-diffusion draft model bringing lossless speculative decoding to SGLang and vLLM[^qwen-community].

Ports keep landing and Qwen3.8-27B runs on just about everything, per the source's closing note[^qwen-community].

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B base; these community GGUF/MLX/AWQ/NVFP4 builds complement the Unsloth official local path.
- Related to [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — Unsloth Dynamic 3.0 entry above is an instance of that quantization family.
- Related to [Unsloth Dynamic NVFP4 Quantization](unsloth-dynamic-nvfp4.md) — Unsloth and RadixArk NVFP4 entries are instances of the Blackwell W4A4 serving path.
- Related to [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) — detailed model-card record for the RadixArk DSpark path summarized here.
- Related to [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — serving surface for the RadixArk DSpark speculator.
- Related to [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) — parallel-drafting upgrade behind the incoai × z-lab DFlash2 entry.
- Related to [DFlash Block Diffusion Speculative Decoding](dflash-block-diffusion.md) — block-diffusion drafting design behind the DFlash2 entry.
- Related to [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — SGLang serving surface named for the DFlash2 entry.

## Contradictions

- RadixArk DSpark size: this source reports a 1.36B speculator with ~3.4 mean acceptance length[^qwen-community], while [Qwen3.8-27B DSpark Speculator](qwen3.8-dspark.md) documents 1,857,358,337 (1.86B) parameters from its model-card source; preserved as reported without reconciliation because the post gives no version or measurement protocol.

## Coverage limits

- Attached `assets/HQxyoxMb0AA6Nts.jpg` was inspected and is a decorative illustration of five Qwen3.8-27B characters with no material technical content[^qwen-community].
- Download-heat ranking, org-footprint and representativeness selection, per-variant quality, and port coverage are source-reported curation claims; linked checkpoints, calibration sets, conversion scripts, and serving engines were not inspected beyond the post text[^qwen-community].

[^qwen-community]: Post by @QwenDevs on X — `../raw/2093175583286968499/index.md`, 2026-08-28 X post curating Qwen3.8-27B community variants two weeks after release by HF/ModelScope download heat, org footprint and route representativeness: seven local-use entries (Unsloth, LM Studio, cyankiwi, ggml-org, AtomicChat, bartowski, mlx-community) and three serving entries (RadixArk NVFP4 plus DSpark, Inferact NVFP4, incoai × z-lab DFlash2), with decorative `assets/HQxyoxMb0AA6Nts.jpg`.
