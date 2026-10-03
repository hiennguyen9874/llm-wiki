---
type: Concept
title: Qwen-Image-2.1 Uncensored GGUF Checkpoints (Abenzerps)
description: Abenzerps GGUF and low-bit Qwen-Image-2.1 checkpoints with uncensored and base variants, encoder/VAE pairing, and ComfyUI-GGUF setup.
tags: [qwen, gguf, quantization, comfyui, image-generation, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T06:10:00Z }
sources:
  - id: abenzerps-qwen21-uc-gguf-readme
    resource: ../raw/Qwen-Image-2.1-Uncensored-Abenzerps-GGUF/README.md
    scope: ../raw/Qwen-Image-2.1-Uncensored-Abenzerps-GGUF/
    kind: documentation
    title: Qwen-Image-2.1 Uncensored GGUF
---

Abenzerps' package provides low-bit checkpoints of `Qwen/Qwen-Image-2.1` for local image generation, with an uncensored transformer set and a separate base GGUF set, plus paired text encoders and VAE for ComfyUI via the ComfyUI-GGUF custom node.[^abenzerps-qwen21-uc-gguf-readme]

## Quantization options

- **Reported** basis: GGUF quantizations of [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1) for local image generation using the original upstream base weights.[^abenzerps-qwen21-uc-gguf-readme]
- **Reported** uncensored files:[^abenzerps-qwen21-uc-gguf-readme]

| Quantization | File | Size |
|---|---|---:|
| BF16 | `qwen-image-2.1-UC-BF16.gguf` | 14.23 GB |
| FP8 | `qwen-image-2.1-UC-fp8.safetensors` | 6.63 GB |
| INT8 ConvRot | `qwen-image-2.1-UC-int8_convrot.safetensors` | 6.76 GB |
| NVFP4 | `qwen-image-2.1-UC-NVFP4.safetensors` | 4.20 GB |
| MLX 4-bit | `qwen-image-2.1-UC-MLX-4bit.safetensors` | 4.00 GB |
| MLX 6-bit | `qwen-image-2.1-UC-MLX-6bit.safetensors` | 5.78 GB |
| MLX 8-bit | `qwen-image-2.1-UC-MLX-8bit.safetensors` | 7.56 GB |
| Q8_0 | `qwen-image-2.1-UC-Q8_0.gguf` | 7.59 GB |
| Q6_K | `qwen-image-2.1-UC-Q6_K.gguf` | 5.88 GB |
| Q5_K_M | `qwen-image-2.1-UC-Q5_K_M.gguf` | 5.22 GB |
| Q4_K_M | `qwen-image-2.1-UC-Q4_K_M.gguf` | 4.60 GB |
| Q4_0 | `qwen-image-2.1-UC-Q4_0.gguf` | 4.15 GB |

- **Reported** base GGUF files on the `base` branch:[^abenzerps-qwen21-uc-gguf-readme]

| Quantization | File | Size |
|---|---:|---:|
| Q8_0 | `qwen-image-2.1-Q8_0.gguf` | 7.59 GB |
| Q6_K | `qwen-image-2.1-Q6_K.gguf` | 5.88 GB |
| Q5_K_M | `qwen-image-2.1-Q5_K_M.gguf` | 5.22 GB |
| Q4_K_M | `qwen-image-2.1-Q4_K_M.gguf` | 4.60 GB |
| Q4_0 | `qwen-image-2.1-Q4_0.gguf` | 4.05 GB |

- **Reported** recommendation: **Q4_K_M** is recommended for the best balance of size and quality; no benchmark protocol, hardware, or variance is given, so treat sizes as **reported** file facts and the recommendation as **reported** guidance, not a reproduced measurement.[^abenzerps-qwen21-uc-gguf-readme]
- **Synthesis:** the package covers two overlapping branches — a 12-file uncensored set spanning BF16, FP8/INT8/NVFP4/MLX safetensors plus GGUF quants, and a 5-file base GGUF set — with only the Q4_0 size differing between branches in the listed tables (4.15 GB versus 4.05 GB).[^abenzerps-qwen21-uc-gguf-readme]

## Text encoders and VAE

- **Reported** companion files packaged for ComfyUI:[^abenzerps-qwen21-uc-gguf-readme]

| Type | File | Precision | Size |
|---|---|---|---:|
| Text Encoder | `text_encoders/qwen3vl_8b_bf16.safetensors` | BF16 | 17.53 GB |
| Text Encoder | `text_encoders/qwen3vl_8b_int8_convrot.safetensors` | Int8 | 9.35 GB |
| VAE | `vae/qwen_image_2.1_vae_bf16.safetensors` | BF16 | 676 MB |

- **Reported** placement in ComfyUI:[^abenzerps-qwen21-uc-gguf-readme]

```text
ComfyUI/
└── models/
    ├── diffusion_models/
    │   └── qwen-image-2.1-UC-Q4_K_M.gguf
    ├── text_encoders/
    │   └── qwen3vl_8b_bf16.safetensors
    └── vae/
        └── qwen_image_2.1_vae_bf16.safetensors
```

- **Reported** scope note: all required companion files (GGUF transformer, text encoder, and VAE) are hosted directly in this repository.[^abenzerps-qwen21-uc-gguf-readme]

## ComfyUI setup

- **Reported** host: use with [ComfyUI](https://github.com/comfyanonymous/ComfyUI) and [ComfyUI-GGUF](https://github.com/leejet/ComfyUI-GGUF).[^abenzerps-qwen21-uc-gguf-readme]
- **Reported** custom-node install: clone the maintained fork with native Qwen-Image 2.1 support into custom nodes:[^abenzerps-qwen21-uc-gguf-readme]

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/leejet/ComfyUI-GGUF
```

- **Reported** failure mode: if the older `city96/ComfyUI-GGUF` install reports `Unknown model architecture!`, update to the `leejet` fork above or add `ModelQwenImage` to `tools/convert.py`.[^abenzerps-qwen21-uc-gguf-readme]
- **Reported** node configuration:[^abenzerps-qwen21-uc-gguf-readme]
  - Diffusion model: **`Unet Loader (GGUF)`** node with the downloaded `.gguf`.
  - Text encoder: standard **`CLIPLoader`** node with `qwen3vl_8b_bf16.safetensors` (or `int8`), setting **`type`** to **`qwen_image`**.
  - VAE: standard **`VAELoader`** node with `qwen_image_2.1_vae_bf16.safetensors`.
- **Reported** workflows: use the official Comfy-Org templates for [Text-to-Image](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_t2i.json) or [Image Edit](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_image_edit.json), replacing the default `UNETLoader` node with **`Unet Loader (GGUF)`**; neither workflow JSON was captured locally.[^abenzerps-qwen21-uc-gguf-readme]
- **Observed:** no install, download, placement, or generation step was executed for this entry.[^abenzerps-qwen21-uc-gguf-readme]

## Memory and performance notes

- **Reported** optimal setup: keep the GGUF diffusion model in GPU VRAM and let the text encoder run in or offload to system RAM/CPU; because text encoding runs once per prompt, this saves 9–17 GB of VRAM with virtually zero impact on generation speed.[^abenzerps-qwen21-uc-gguf-readme]
- **Reported** recommended configuration: diffusion `qwen-image-2.1-UC-Q4_K_M.gguf` (~4.6 GB in VRAM) plus text encoder `qwen3vl_8b_int8_convrot.safetensors` (~9.35 GB in RAM).[^abenzerps-qwen21-uc-gguf-readme]
- **Reported** low-VRAM mode: if VRAM out-of-memory errors occur, start ComfyUI with the `--lowvram` argument.[^abenzerps-qwen21-uc-gguf-readme]

## Provenance and trust boundary

- Base model is **reported** as Qwen Team `Qwen/Qwen-Image-2.1`; text-encoder and VAE source is **reported** as [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1).[^abenzerps-qwen21-uc-gguf-readme]
- **Reported** immutable references: source revision `b3179ad355be050328e483a9dfdd9e60cd62adfa` and conversion via [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) commit `1330cebae8f2ba99249df846cc0c9444fcbd4308`; checksums are pointed to `SHA256SUMS`, which was not captured locally and remains unverified.[^abenzerps-qwen21-uc-gguf-readme]
- License frontmatter states `other` / `qwen-research` with pipeline tag `text-to-image` and library `gguf`; this is a **reported** disclosure boundary, not legal verification.[^abenzerps-qwen21-uc-gguf-readme]
- Uncensored boundary: the source states this release has no built-in safety checker or content filter and describes generation of adult, NSFW, and sensitive imagery without prompt refusals or blacked-out images, with output behavior depending solely on input prompts and execution environment; this is a **reported** capability and governance limit, not a tested behavior.[^abenzerps-qwen21-uc-gguf-readme]
- Benchmark figure `assets/Qwen-Image-2.1-Benchmark.png` is referenced in the source but was not captured locally and its values are not compiled here.[^abenzerps-qwen21-uc-gguf-readme]

## Relationships

- Uses the upstream Qwen-Image-2.1 base model and Comfy-Org text-encoder and VAE weights; this concept records only the Abenzerps quantization packaging and ComfyUI setup, not the base model's own behavior.
- Uses ComfyUI with the ComfyUI-GGUF custom node as the supported host; see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) for the node pack and [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md) for the conversion engine named by this source.
- Related to [Qwen-Image-2.1 GGUF Quantized Checkpoints (Abiray)](qwen-image-2-1-gguf-abiray.md) and [Qwen-Image-2.1 GGUF Quantized Checkpoints (Unsloth)](qwen-image-2-1-gguf-unsloth.md), separate community GGUF packagings of the same base family; this source adds an uncensored branch, FP8/INT8/NVFP4/MLX artifacts, explicit source and conversion revisions, and a leejet-fork plus VRAM-offload setup, none of which the other two sources claim.

## Coverage limits

- **Observed:** only `../raw/Qwen-Image-2.1-Uncensored-Abenzerps-GGUF/README.md` was statically inspected; no code was executed and no quant, download, install, placement, workflow, checksum, or generation claim was reproduced.
- **Observed:** no package-level immutable revision or date is present in the capture; the recorded `b3179ad3` and `1330ceba` hashes identify the reported upstream source and conversion tool, not a snapshot of this GGUF repository.
- **Observed:** uninspected material outside this scope includes all weight files, `assets/Qwen-Image-2.1-Benchmark.png`, `SHA256SUMS`, the upstream base model, Comfy-Org encoder/VAE weights, both official workflow templates, and the ComfyUI, ComfyUI-GGUF, and stable-diffusion.cpp projects.

[^abenzerps-qwen21-uc-gguf-readme]: Model-card README capture in `../raw/Qwen-Image-2.1-Uncensored-Abenzerps-GGUF/README.md`; uncensored purpose and upstream-base claim from header; 12-row uncensored and 5-row base quant tables plus Q4_K_M recommendation from Uncensored GGUF Files and GGUF files sections; encoder/VAE filenames, precisions, sizes, placement tree, and hosted-in-repo claim from Text Encoders & VAE and Download & File Placement sections; leejet fork install, `Unknown model architecture` fallback, Unet Loader / CLIPLoader / VAELoader settings, and official workflow links from ComfyUI Setup section; VRAM/RAM split, 9–17 GB saving, recommended Q4_K_M plus int8 pairing, and `--lowvram` note from Memory & Performance Notes section; uncensored no-filter statement from Uncensored section; upstream, Comfy-Org, revision, conversion-commit, license, and checksum pointer from Source and build section and frontmatter; benchmark image reference from Benchmark section.
