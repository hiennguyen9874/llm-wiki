---
type: Concept
title: Qwen-Image-2.1 Text Encoder (Heretic)
description: Refusal-ablated Qwen3-VL text encoder for Qwen-Image-2.1 with GGUF, FP8, and bf16 builds and ComfyUI setup.
tags: [qwen, text-encoder, gguf, quantization, comfyui, image-generation, ablation]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T06:00:00Z }
sources:
  - id: heretic-te-gguf-readme
    resource: ../raw/Qwen-Image-2.1-Text-Encoder-Heretic-GGUF/README.md
    scope: ../raw/Qwen-Image-2.1-Text-Encoder-Heretic-GGUF/
    kind: documentation
    title: Qwen-Image-2.1 Text Encoder Heretic GGUF README
---

Qwen-Image-2.1 Text Encoder (Heretic) is a community refusal-ablated packaging of the Qwen3-VL-8B-Instruct text encoder that Qwen-Image-2.1 uses unmodified, distributed as GGUF, FP8, and bf16 builds with a ComfyUI GGUF loading patch and sampler guidance.[^heretic-te-gguf-readme]

## Identity and provenance

- **Observed** frontmatter: `base_model: pottokao/Qwen-Image-2.1-Text-Encoder-Heretic`; tags include `quantized`, `fp8`, `gguf`, `comfyui`, `qwen-image`, `abliterated`, and `text-encoder`.[^heretic-te-gguf-readme]
- **Reported** derivation: refusal-ablated derivative of `Qwen/Qwen3-VL-8B-Instruct`, which Qwen-Image-2.1 uses as its text encoder; redistributed under Apache-2.0 with `LICENSE` and `NOTICE` references.[^heretic-te-gguf-readme]
- **Reported** non-affiliation: not affiliated with or endorsed by Alibaba / Qwen.[^heretic-te-gguf-readme]
- **Reported** ablation method: Heretic directional ablation on `o_proj` plus `down_proj`, 200 trials / 60 startup trials, knee point of the Pareto front.[^heretic-te-gguf-readme]

## File options

- **Reported** builds in this repo:[^heretic-te-gguf-readme]

| File | Size | Loader |
|---|---:|---|
| `qwen3vl_8b_heretic-Q4_K_M.gguf` + `mmproj-qwen3vl_8b_heretic-f16.gguf` | 5.03 + 1.16 GB | `CLIPLoaderGGUF` + patch node |
| `qwen3vl_8b_heretic-Q6_K.gguf` + mmproj | 6.88 + 1.16 GB | same GGUF loader path |
| `qwen3vl_8b_heretic-Q8_0.gguf` + mmproj | 8.71 + 1.16 GB | same GGUF loader path |
| `qwen3vl_8b_fp8_heretic.safetensors` | 9.34 GB | stock `CLIPLoader`, NVIDIA GPU |
| `qwen3vl_8b_bf16_heretic.safetensors` | 17.53 GB | stock `CLIPLoader`, any device incl. Mac |

- **Reported** loader convention: every build uses type `qwen_image` and feeds `TextEncodeQwenImage21`.[^heretic-te-gguf-readme]
- **Reported** other formats of the same ablated encoder outside this repo: bf16 HF shards, INT8 convrot 9.35 GB, W4A8 6.31 GB, and NVFP4 6.31 GB for Blackwell GPUs.[^heretic-te-gguf-readme]

## ComfyUI GGUF setup

- **Reported** 3-step procedure: install `city96/ComfyUI-GGUF` plus `pottokao-dotcom/ComfyUI-GGUF-Qwen3VL-TE` under `ComfyUI/custom_nodes/`, place both the GGUF and the f16 mmproj in `ComfyUI/models/text_encoders/` without renaming, restart ComfyUI, then `CLIPLoaderGGUF` with type `qwen_image`.[^heretic-te-gguf-readme]
- **Reported** mmproj requirement: the vision tower file is required even for text-only use and is also used for reference-image editing; a missing tower stops loading with a `Missing vision tower` error naming the expected file.[^heretic-te-gguf-readme]
- **Reported** success signal: console shows `[GGUF-Qwen3VL-TE] added 351 Qwen3-VL vision tensors from mmproj`.[^heretic-te-gguf-readme]
- **Reported** patch root cause 1 — text encoder `[1, 512, 12288]`: stock ComfyUI-GGUF loads the mmproj vision tower only for `qwen2vl`, not `qwen3vl`, so the encoder is misbuilt with 12288-wide hidden states instead of 4096; the patch loads the matching `mmproj-*.gguf` and renames tensors to ComfyUI's Qwen3-VL `model.visual.*` layout.[^heretic-te-gguf-readme]
- **Reported** patch root cause 2 — DiT `Unknown model architecture!`: DiT GGUFs without `general.architecture` metadata are identified by tensor names, and ComfyUI-GGUF lacks a Qwen-Image entry; the patch recognizes `img_in`, `txt_in.in_layer`, and `txt_in.text_norm` as `qwen_image` and stands down once upstream handles either case.[^heretic-te-gguf-readme]
- **Reported** verification: 2026-09-23 on ComfyUI 0.36.0 plus ComfyUI-GGUF `6ea2651` on NVIDIA GPU, text-to-image and reference-image editing match the bf16 encoder for the same seed up to Q4 quantization noise; Mac build not tested.[^heretic-te-gguf-readme]

## Sampler guidance

- **Reported** step budget: Qwen-Image-2.1 is a full non-distilled model; use 25 steps because more steps do not sharpen text and start to burn highlights.[^heretic-te-gguf-readme]
- **Reported** no-text case: plain `KSampler` at cfg 1.0 is fastest with the softest look, and the negative prompt is ignored at cfg 1.[^heretic-te-gguf-readme]
- **Reported** with-text case: split cfg partway — first 1/2 to 2/3 of steps at cfg 1 to lock composition and materials, remainder at cfg 3 with a negative prompt such as `oversaturated, overexposed, gibberish text` to redraw lettering; implemented as two chained `KSamplerAdvanced` nodes with shared model, seed, and 25 steps, first `add_noise` enabled from step 0 to 12–17 with leftover noise returned, second from 12–17 to 25 without added noise.[^heretic-te-gguf-readme]
- **Synthesis:** splitting later at step 17 preserves more of the cfg-1 look while splitting earlier at step 12 favors crisper text.[^heretic-te-gguf-readme]

## Ablation and format details

- **Reported** refusal/KL table inherited from the bf16 source: stock encoder 100/100 refusals and KL 0.0 by definition; this family 5/100 refusals and KL 0.0220; independently rechecked as 0/20 refusals with 4/4 benign questions answered correctly.[^heretic-te-gguf-readme]
- **Reported** GGUF layout: Q4_K_M language model with the vision tower kept as a separate f16 mmproj.[^heretic-te-gguf-readme]
- **Reported** FP8 layout: self-quantized `float8_e4m3fn` covering 254 two-dimensional FFN, attention, embed, and lm_head weights; 351 vision-tower tensors left in bf16; norms and biases left in bf16; remapped to ComfyUI `model.layers.…` keys without the `language_model.` prefix; requires a ComfyUI build with `QwenImage21` support, 0.36.0 or newer.[^heretic-te-gguf-readme]

## Pipeline context

- **Reported** all-GGUF Qwen-Image-2.1 layout: optional PE-T2I rewriter via llama.cpp, this text encoder via `CLIPLoaderGGUF` plus patch, DiT GGUF via stock `UnetLoaderGGUF`, and official `qwen_image_2.1_vae_bf16.safetensors` via `VAELoader`.[^heretic-te-gguf-readme]
- **Reported** prompt rewriters: PE-T2I expands one short multilingual line into a detailed English prompt plus aspect ratio; PE-I2I turns a vague edit instruction plus input images into a precise editing prompt; both ship refusal-ablated with GGUF builds that run anywhere llama.cpp runs.[^heretic-te-gguf-readme]
- **Reported** showcase basis: the page's Q4_K_M gallery was made with PE-T2I Q4_K_M, this encoder Q4_K_M plus f16 mmproj, DiT Q4_K_M, and the official bf16 VAE.[^heretic-te-gguf-readme]

## Relationships

- Encodes prompts for [Qwen-Image-2.1 Text-to-Image and Editing Model](qwen-image-2-1.md); this concept records only the Heretic encoder packaging, not the base model's generation behavior.
- Uses [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) plus the `ComfyUI-GGUF-Qwen3VL-TE` patch for the GGUF path; the FP8 and bf16 safetensors paths use the stock `CLIPLoader` instead.
- Complements DiT-side GGUF packages such as [Qwen-Image-2.1 GGUF Quantized Checkpoints (Abiray)](qwen-image-2-1-gguf-abiray.md), [Qwen-Image-2.1 GGUF Quantized Checkpoints (Leejet)](qwen-image-2-1-gguf-leejet.md), and [Qwen-Image-2.1 GGUF Quantized Checkpoints (Unsloth)](qwen-image-2-1-gguf-unsloth.md); those pages cover the denoiser, while this page covers the encoder.

## Coverage limits

- **Observed:** only `../raw/Qwen-Image-2.1-Text-Encoder-Heretic-GGUF/README.md` was statically inspected; no weights were downloaded and no install, load, generation, editing, sampler, quantization-noise, or ablation claim was executed or reproduced.
- **Observed:** uninspected or unavailable material includes all six weight files, `LICENSE` and `NOTICE`, both ComfyUI custom-node repos, the linked PE-T2I and PE-I2I repos, the DiT GGUF and VAE targets, the PhotoStyles node, and all remote showcase images.
- No immutable revision or snapshot date is present in the capture; future weight or card updates would be a new revision.

[^heretic-te-gguf-readme]: Model-card README capture in `../raw/Qwen-Image-2.1-Text-Encoder-Heretic-GGUF/README.md`; Heretic/Qwen3-VL identity, file-size and loader table, `qwen_image` type, and patch-node fix notice from header and Which-file sections; sampler steps, cfg split, KSamplerAdvanced table, and negative prompt from Recommended-sampler section; all-GGUF pipeline, FP8/bf16 details, and ComfyUI 0.36.0 requirement from All-GGUF, Format-details, and Files sections; ablation 5/100, KL 0.0220, Heretic `o_proj`/`down_proj` settings, and 0/20 recheck from Ablation section; mmproj naming rule, vision-tensor count, verification date/commit, and both patch root causes from GGUF-in-ComfyUI and What-the-patch-handles sections; rewriter behavior, outside-repo formats, showcase basis, Apache-2.0 derivation, and non-affiliation disclaimer from Also-for, Files, Showcase, and footer sections; frontmatter `base_model` and tags from file header.
