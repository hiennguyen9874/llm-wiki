---
type: Concept
title: stable-diffusion.cpp Local Diffusion Inference
description: ggml-based C/C++ engine for local SD, FLUX, Qwen-Image, Wan and related image/video model inference.
tags: [diffusion, local-inference, ggml, image-generation, video-generation]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T05:14:15Z }
sources:
  - id: sdcpp-readme
    resource: ../raw/stable-diffusion.cpp.md
    kind: documentation
    title: stable-diffusion.cpp README
---

stable-diffusion.cpp is a lightweight plain C/C++ diffusion-model inference engine built on ggml, following the llama.cpp pattern with no external dependencies, supporting local image and video generation across SD, FLUX, Qwen-Image and Wan-class families with portable CPU/GPU backends and GGUF/Safetensors/PyTorch weight handling.[^sdcpp-readme]

## Implementation and portability

- **Reported** architecture: plain C/C++ on [ggml](https://github.com/ggml-org/ggml), working the same way as llama.cpp; described as super lightweight without external dependencies.[^sdcpp-readme]
- **Reported** backends: CPU with AVX/AVX2/AVX512 on x86, plus CUDA, Vulkan, Metal, OpenCL and SYCL.[^sdcpp-readme]
- **Reported** platforms: Linux, macOS, Windows, and Android via Termux and Local Diffusion.[^sdcpp-readme]
- **Reported** weight formats: PyTorch checkpoint (`.ckpt`/`.pth`/`.pt`), Safetensors (`.safetensors`), and GGUF (`.gguf`); convert mode converts weights to `.gguf` or `.safetensors`.[^sdcpp-readme]
- **Reported** efficiency controls: Flash Attention for memory optimization, VAE tiling to reduce memory use, faster memory-efficient latent decoding via TAESD, and ESRGAN upscaling; see performance and backend-selection guides for tuning and backend placement.[^sdcpp-readme]

## Capabilities

- **Reported** image-model breadth: SD1.x, SD2.x, SD-Turbo, SDXL, SDXL-Turbo, selected distilled SD1.x/SDXL models, SD3/SD3.5, FLUX.1-dev/schnell, FLUX.2-dev/klein, plus Lens, Chroma/Chroma1-Radiance, Qwen-Image/Qwen-Image-2.1, PiD, LongCat-Image, Z-Image, MiniT2I, SenseNova-U1.5, Ovis-Image, Anima, ERNIE-Image, Boogu-Image, Krea2, Mage-Flow, SeFi-Image, HiDream-O1-Image, Ideogram4, LLaDA-Image, Ming-Image-Design and PixArt.[^sdcpp-readme]
- **Reported** image-edit support: FLUX.1-Kontext-dev, Qwen-Image-Edit series, LongCat-Image-Edit, Boogu-Image-Edit, Mage-Flow-Edit and LLaDA-Image-Edit.[^sdcpp-readme]
- **Reported** video-model support: Wan2.1/Wan2.2 including Vace, MiniMax-H3, LTX-2.3/LTX-2.5, HunyuanVideo-1.5 and LingBot-Video.[^sdcpp-readme]
- **Reported** conditioning and adaptation: PhotoMaker, IP-Adapter for SD1.5 and SDXL including Plus, ControlNet with SD1.5, ADetailer, LoRA compatible with stable-diffusion-webui behavior, and LCM/LCM-LoRA support.[^sdcpp-readme]
- **Reported** generation controls: negative prompt, webui-style tokenizer limited to token weighting, embedded webui-compatible generation parameters in PNG output, and cross-platform reproducibility via `--rng cuda` by default consistent with webui GPU RNG versus `--rng cpu` consistent with ComfyUI RNG.[^sdcpp-readme]
- **Reported** samplers: Euler A, Euler, Heun, DPM2, DPM++ 2M, DPM++ 2M v2, DPM++ 2S a, ER-SDE and LCM.[^sdcpp-readme]

## Operation

- **Reported** acquisition: download prebuilt `sd` binaries from releases or build from source via the build guide.[^sdcpp-readme]
- **Reported** minimal run: download weights such as `v1-5-pruned-emaonly.safetensors`, then run `./bin/sd-cli -m ../models/v1-5-pruned-emaonly.safetensors -p "a lovely cat"`; detailed flags live in the CLI example README.[^sdcpp-readme]
- **Reported** guides: troubleshooting, backend selection, RPC, LoRA, LCM/LCM-LoRA, Docker, quantization and GGUF, INT8 convrot Safetensors, and inference acceleration via caching.[^sdcpp-readme]
- **Synthesis:** treat the dated “Important News” entries as freshness signals rather than stable coverage; the snapshot advertises day-0 support for Qwen-Image-2.1 on 2026/09/20 and day-1 support for MiniMax-H3 on 2026/08/04, with an explicit warning that the project is under active development and API/CLI options may change frequently.[^sdcpp-readme]

## Relationships

- **Synthesis:** [Image Model, Library, and Workflow Roles](image-inference-tool-roles.md) places this engine alongside Diffusers and ComfyUI without implying they share an execution stack; [Latent Image Generation Pipeline](latent-image-generation.md) explains the conceptual components an engine executes.

## Ecosystem

- **Reported** language bindings: non-cgo and cgo Go projects, C#, Python, Rust, and Flutter/Dart wrappers listed as external projects.[^sdcpp-readme]
- **Reported** downstream UIs and hosts: GIMP plugins, Jellybox, Stable Diffusion GUI and CLI-GUI variants, Local Diffusion, sd.cpp-webui, LocalAI, Neural-Pixel and KoboldCpp.[^sdcpp-readme]

## Coverage limits

- **Observed:** only `raw/stable-diffusion.cpp.md` was statically inspected; linked `./assets/logo.png`, `./docs/*.md`, `./examples/cli/README.md`, release binaries and Hugging Face weights were not captured locally and remain uninspected.
- **Observed:** no immutable revision hash was present in the capture; freshness is bounded by news entries through 2026/09/20.
- No code was executed and no implementation, command, quantization, backend-placement or benchmark claim was independently reproduced; engine behavior above is **reported** by the project README.
- Consequential limits for reuse: tokenizer support is only token weighting rather than full webui behavior; ControlNet is stated for SD1.5; IP-Adapter is stated for SD1.5 and SDXL including Plus.

[^sdcpp-readme]: stable-diffusion.cpp README capture in `../raw/stable-diffusion.cpp.md`; Features and Supported models/backends/weight-formats sections for capabilities and portability; Quick Start for acquisition and `sd-cli` invocation; Sampling method and reproducibility notes for samplers and `--rng`; Bindings and UIs sections for ecosystem; Important News plus active-development note for freshness and API instability.
