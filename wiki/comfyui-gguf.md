---
type: Concept
title: ComfyUI-GGUF Quantized Model Support
description: Custom nodes for running GGUF-quantized UNET/DiT and T5 models in ComfyUI.
tags: [comfyui, gguf, quantization, diffusion, local-inference, image-generation]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T05:14:15Z }
sources:
  - id: comfyui-gguf-readme
    resource: ../raw/ComfyUI-GGUF.md
    kind: documentation
    title: ComfyUI-GGUF README
---

ComfyUI-GGUF is a **reported** work-in-progress custom-node pack that adds GGUF-quantized model loading to native ComfyUI, targeting transformer/DiT diffusion models and a quantized T5 text encoder for lower VRAM use on low-end GPUs.[^comfyui-gguf-readme]

## Rationale and scope

- **Reported** purpose: support model files stored in the GGUF format popularized by llama.cpp inside native ComfyUI models.[^comfyui-gguf-readme]
- **Reported** qualification: quantization was not feasible for regular UNET conv2d models, while transformer/DiT models such as FLUX are described as less affected by quantization, enabling lower bits-per-weight variable-bitrate quants.[^comfyui-gguf-readme]
- **Reported** status: explicitly described as very much WIP.[^comfyui-gguf-readme]

## UNET loader usage

- **Reported** procedure: use the GGUF Unet loader under the `bootleg` category, place `.gguf` model files in `ComfyUI/models/unet`, and replace the stock Load Diffusion Model node with the Unet Loader (GGUF) node; there is no need to copy an example workflow verbatim.[^comfyui-gguf-readme]
- **Reported** prerequisite: ComfyUI must be recent enough to support custom ops when loading UNET-only models.[^comfyui-gguf-readme]
- **Reported** LoRA handling: LoRA loading is experimental but should work with the built-in LoRA loader node(s).[^comfyui-gguf-readme]
- **Reported** boundary: Force/Set CLIP Device is not part of this node pack; the source warns single-GPU users against setting it to `cuda:0` and then reporting OOM errors.[^comfyui-gguf-readme]

## Text-encoder loader usage

- **Reported** purpose: a quantized T5 text-encoder loader provides further VRAM savings.[^comfyui-gguf-readme]
- **Reported** procedure: use the various `*CLIPLoader (gguf)` nodes in place of the regular CLIP loaders; for the CLIP model, keep whatever model was used before.[^comfyui-gguf-readme]
- **Reported** compatibility: the loader handles both `gguf` and regular `safetensors`/`bin` CLIP files.[^comfyui-gguf-readme]

## Installation

- **Reported** normal install: clone `https://github.com/city96/ComfyUI-GGUF` into `ComfyUI/custom_nodes` and install inference dependency via `pip install --upgrade gguf`.[^comfyui-gguf-readme]
- **Reported** portable Windows install: from the `ComfyUI_windows_portable` folder run `git clone https://github.com/city96/ComfyUI-GGUF ComfyUI/custom_nodes/ComfyUI-GGUF` then `.\python_embeded\python.exe -s -m pip install -r .\ComfyUI\custom_nodes\ComfyUI-GGUF\requirements.txt`.[^comfyui-gguf-readme]
- **Reported** macOS constraint: on macOS Sequoia, torch 2.4.1 appears required because 2.6.X nightly versions cause a "M1 buffer is not large enough" error; workarounds are **reported** in upstream issue 107.[^comfyui-gguf-readme]

## Available pre-quantized models

The source lists these **reported** city96 Hugging Face quants without pinning revisions:[^comfyui-gguf-readme]

- FLUX.1-dev GGUF.
- FLUX.1-schnell GGUF.
- Stable Diffusion 3.5 Large GGUF.
- Stable Diffusion 3.5 Large Turbo GGUF.
- T5 v1.1-XXL encoder GGUF.

- **Reported** path for custom quants: see instructions in the upstream `tools` folder for creating new quants; that folder was not captured locally.[^comfyui-gguf-readme]

## Relationships

- **Synthesis:** [Image Model, Library, and Workflow Roles](image-inference-tool-roles.md) provides the host/library/engine distinction behind this custom-node integration; GGUF loading here is not evidence that ComfyUI runs through stable-diffusion.cpp.

- Uses the GGUF format popularized by llama.cpp and the `gguf` Python package; depends on a ComfyUI version with custom-ops support for UNET-only loading.
- Used by [Qwen-Image-2.1 GGUF Quantized Checkpoints (Abiray)](qwen-image-2-1-gguf-abiray.md) as its supported ComfyUI host via the Unet Loader (GGUF) node.
- Referenced by [Qwen-Image-2.1 GGUF Quantized Checkpoints (Leejet)](qwen-image-2-1-gguf-leejet.md), which recommends the `leejet/ComfyUI-GGUF` fork over the `city96` install documented here; the maintenance claim is reported by that source and unverified here.
- Extended by [Qwen-Image-2.1 Text Encoder (Heretic)](qwen-image-2-1-text-encoder-heretic.md) for the Qwen3-VL encoder path: stock loading misses the `qwen3vl` vision tower and DiT GGUFs without architecture metadata, addressed there by the `ComfyUI-GGUF-Qwen3VL-TE` patch.
- Contrasts with [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md), a separate ggml-based local engine rather than a ComfyUI integration.

## Coverage limits

- **Observed:** only `../raw/ComfyUI-GGUF.md` was statically inspected; no code was executed and no install, loading, quantization-quality, VRAM, or LoRA-compatibility claim was reproduced.
- **Observed:** no immutable revision, date, or license is present in the capture; freshness is unbounded beyond local capture.
- **Observed:** uninspected linked material outside this scope includes the example workflow screenshot, upstream llama.cpp project, all five Hugging Face quant repositories, the upstream `tools` quantization instructions, and macOS issue 107.
- All capability, compatibility, and model-availability statements above are **reported** by the project README, not independently verified.

[^comfyui-gguf-readme]: ComfyUI-GGUF README capture in `../raw/ComfyUI-GGUF.md`; WIP status and GGUF/UNET/DiT rationale from intro; Unet loader category, model folder, node-replacement guidance, LoRA note, and CLIP-device warning from Usage and intro screenshot note; T5/CLIPLoader behavior from Usage; normal, portable, and macOS install commands plus custom-ops prerequisite from Installation; pre-quantized FLUX/SD3.5/T5 links and tools-folder pointer from Usage.
