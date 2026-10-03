---
type: Concept
title: Qwen-Image-2.1 GGUF Quantized Checkpoints (Unsloth)
description: Unsloth Dynamic 2.0 GGUF quants of the Qwen-Image-2.1 denoiser with VAE and Qwen3-VL encoder pairing and sd-cli use.
tags: [qwen, gguf, quantization, unsloth, image-generation, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T04:50:53Z }
sources:
  - id: unsloth-qwen21-gguf-readme
    resource: ../raw/Qwen-Image-2.1-GGUF/README.md
    scope: ../raw/Qwen-Image-2.1-GGUF/
    kind: documentation
    title: Unsloth Qwen-Image-2.1-GGUF model card
---

Unsloth's package provides Dynamic 2.0 GGUF quantized checkpoints of the `Qwen/Qwen-Image-2.1` denoiser for local text-to-image generation, paired with a separate VAE and Qwen3-VL text encoder and run through Unsloth Desktop, stable-diffusion.cpp, or other GGUF hosts.[^unsloth-qwen21-gguf-readme]

## Quantization and packaging

- **Reported** base: GGUF quantized version of [Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1), with `base_model: Qwen/Qwen-Image-2.1` and `base_model_relation: quantized` in frontmatter.[^unsloth-qwen21-gguf-readme]
- **Reported** method: Unsloth Dynamic 2.0, described as upcasting important layers to higher precision per tensor based on a measured sensitivity scan for improved performance over uniform quantization.[^unsloth-qwen21-gguf-readme]
- **Reported** component boundary: the GGUF file is the denoiser only, so a VAE and the Qwen3-VL text encoder are required alongside it.[^unsloth-qwen21-gguf-readme]
- **Reported** hosts: Unsloth Desktop, stable-diffusion.cpp, and more; a pointer to the Unsloth Qwen-Image-2.1 run guide is given as the primary how-to entry point.[^unsloth-qwen21-gguf-readme]

## Required components and encoder comparison

- **Reported** VAE: `unsloth/Qwen-Image-2.1-FP8` file `vae/qwen_image_2.1_vae_bf16.safetensors`.[^unsloth-qwen21-gguf-readme]
- **Reported** text encoder: `unsloth/Qwen3-VL-8B-Instruct-GGUF` file `Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf`, explicitly recommended as the Dynamic 2.0 4-bit rung rather than the uniform `Q4_K_M` encoder.[^unsloth-qwen21-gguf-readme]
- **Reported** encoder measurement, holding denoiser and VAE fixed at a shared seed: UD-Q4_K_XL versus Q4_K_M gives LPIPS 0.029, SSIM 0.959, 5.15 GB versus 5.03 GB, and 36.5 s versus 39.0 s; no fuller protocol, hardware, image count, or variance is stated, so treat as a **reported** paired comparison, not a reproduced benchmark.[^unsloth-qwen21-gguf-readme]
- **Synthesis:** the size/time direction favors the UD rung as slightly larger but faster in this one reported comparison, while LPIPS/SSIM closeness is positioned as near-equivalence; without protocol detail this is a selection signal, not a quality proof.[^unsloth-qwen21-gguf-readme]

## Local run

- **Reported** `sd-cli` invocation:[^unsloth-qwen21-gguf-readme]

```bash
sd-cli --diffusion-model qwen-image-2.1-Q4_K_M.gguf \
  --vae qwen_image_2.1_vae_bf16.safetensors \
  --llm Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf \
  -p "a cartoon sloth mascot waving, flat vector illustration, bright colours" \
  --steps 20 --cfg-scale 6.0 --sampling-method euler -W 1024 -H 1024 --diffusion-fa \
  -o out.png
```

- **Reported** sample conditions: Q4_K_M denoiser with Q4_K_M text encoder, 1024x1024, 20 steps, CFG 6.0, euler; four widget/sample images (`cafe`, `spaces`, `cinema`, `cardesert`) are referenced but no image files were captured locally.[^unsloth-qwen21-gguf-readme]
- **Observed:** no run, download, or generation step was executed for this entry; the command and sample claims are **reported** usage, not reproduced behavior.[^unsloth-qwen21-gguf-readme]

## Base-model context (reported)

- **Reported** identity: Qwen-Image-2.1 is a unified text-to-image generation and image-editing model with 7B parameters in the visual generation component across 32 Single-Stream DiT layers, balancing quality, efficiency, and versatility.[^unsloth-qwen21-gguf-readme]
- **Reported** improvements: compact efficient architecture with mixed-granularity attention and prefix KV cache reuse; native transparency with unified creation/editing including RGBA generation, transparent-layer editing, and subject extraction; versatile editing with up to 10 reference images, circle/painted-annotation/separate-mask local edits, and identity preservation for people and products; improved textures, typography, portrait lighting, and fine detail.[^unsloth-qwen21-gguf-readme]
- **Reported** Diffusers use: `pip install torch>=2.4.0 transformers>=5.17 accelerate pillow` plus `diffusers` from git; `QwenImage21Pipeline.from_pretrained("Qwen/Qwen-Image-2.1", torch_dtype=torch.bfloat16)` on CUDA for text-to-image at 2048x2048 and 40 steps, image editing from an input image, and RGBA generation via a transparency prompt prefix; `enable_model_cpu_offload()` is given for memory optimization.[^unsloth-qwen21-gguf-readme]
- **Reported** aspect-ratio defaults: 1:1 2048x2048, 4:3 2400x1792, 3:4 1792x2400, 3:2 2528x1696, 2:3 1696x2528, 16:9 2752x1536, 9:16 1536x2752.[^unsloth-qwen21-gguf-readme]
- License frontmatter states `other` / `qwen-research` with a link to the upstream `Qwen-Image-2.1` LICENSE, and the body points to the Qwen Research License Agreement; this is a **reported** disclosure boundary, not legal verification.[^unsloth-qwen21-gguf-readme]

## Relationships

- Uses the upstream `Qwen/Qwen-Image-2.1` base model; this concept records only the Unsloth GGUF denoiser packaging, component pairing, and local-run notes, not a full base-model definition.
- Related to [Qwen-Image-2.1 GGUF Quantized Checkpoints (Abiray)](qwen-image-2-1-gguf-abiray.md), a separate community GGUF packaging with six size/VRAM options and a ComfyUI setup; Unsloth specifies Dynamic 2.0 per-tensor handling and a denoiser-plus-VAE-plus-Qwen3-VL-encoder triple, a distinct packaging claim neither source makes about the other.
- For GGUF hosts, see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) for the ComfyUI custom-node path and [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md) for the ggml-based `sd-cli` engine named by this source; neither host concept was verified against this quant in this operation.
- Related to [Pruna Qwen-Image-2.1 Few-Step LoRA Adapters](pruna-qwen-image-2-1.md), which targets fewer-step inference on the same base family, and [Qwen-Image-2.1-Fun ControlNet-Union Branch](qwen-image-2-1-fun-controlnet-union.md), which adds structural control; this source makes no claim about LoRA or ControlNet compatibility.

## Coverage limits

- **Observed:** only `../raw/Qwen-Image-2.1-GGUF/README.md` was statically inspected; no code was executed and no quant, download, install, or generation claim was reproduced.
- **Observed:** no immutable revision or capture date is present; freshness is unbounded beyond the local capture.
- **Observed:** uninspected material outside this scope includes the upstream base model, Unsloth run-guide docs, Unsloth Desktop, the VAE and text-encoder weights, all `assets/` sample images, and linked Hugging Face, ModelScope, GitHub, blog, demo, Discord, and WeChat targets.

[^unsloth-qwen21-gguf-readme]: Model-card README capture in `../raw/Qwen-Image-2.1-GGUF/README.md`; base-model, Dynamic 2.0 per-tensor, denoiser-only boundary, host, VAE path, encoder filename, UD-vs-Q4_K_M LPIPS/SSIM/size/time figures, `sd-cli` command, and Q4_K_M sample conditions from header and top sections; base-model parameter count, DiT layers, four improvements, install, T2I/edit/RGBA snippets, aspect-ratio table, and CPU-offload note from Introduction and Quick Start sections; `qwen-research` license, pipeline tag, languages, and upstream links from frontmatter and License section.
