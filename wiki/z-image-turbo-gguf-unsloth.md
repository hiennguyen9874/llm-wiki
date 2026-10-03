---
type: Concept
title: Z-Image-Turbo GGUF Quantized Checkpoints (Unsloth)
description: Unsloth Dynamic 2.0 GGUF quants of the Z-Image-Turbo 6B single-stream DiT model with 8-NFE Turbo inference and diffusers use.
tags: [z-image, gguf, quantization, unsloth, image-generation, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T12:00:00Z }
sources:
  - id: zimage-turbo-gguf-card
    resource: ../raw/Z-Image-Turbo-GGUF/README.md
    scope: ../raw/Z-Image-Turbo-GGUF/
    kind: documentation
    title: Unsloth Z-Image-Turbo-GGUF model card
---

Unsloth's package provides GGUF quantized checkpoints of `Tongyi-MAI/Z-Image-Turbo` for local text-to-image generation, using Unsloth Dynamic 2.0 with important layers upcast to higher precision; the card embeds the upstream Z-Image-Turbo summary of a 6B single-stream DiT model with 8-NFE distilled Turbo inference, bilingual rendering, and `diffusers` use.[^zimage-turbo-gguf-card]

## Quantization and packaging

- **Observed** base declaration: card frontmatter states `base_model: Tongyi-MAI/Z-Image-Turbo`.[^zimage-turbo-gguf-card]
- **Reported** method: Unsloth Dynamic 2.0 methodology for SOTA performance, with important layers upcasted to higher precision; the card links the Unsloth Dynamic 2.0 documentation as the method reference.[^zimage-turbo-gguf-card]
- **Observed** task tagging: frontmatter declares `pipeline_tag: text-to-image`, `library_name: ggml`, `language: [en]`, `license: apache-2.0`, and `tags` including `gguf`, `quantized`, and `unsloth`.[^zimage-turbo-gguf-card]
- **Observed** sample widgets: frontmatter widget prompt `cute sloth in starry night style` points to `assets/sloth_gogh.png`, and the Samples table references four `assets/sloth_*` images; none of these asset files is captured locally.[^zimage-turbo-gguf-card]
- **Observed:** the capture does not list quant filenames, sizes, VRAM targets, component boundaries such as a separate VAE or text encoder, or a named GGUF host; do not assume the denoiser-plus-VAE-plus-encoder triple recorded for Unsloth Qwen-Image-2.1 GGUF applies here.[^zimage-turbo-gguf-card]

## Base-model identity and variants (reported)

- **Reported** identity: Z-Image is a 6B-parameter image generation model, with the card title framing it as an efficient foundation model with single-stream diffusion transformer; three variants are named.[^zimage-turbo-gguf-card]
- **Reported** Turbo: distilled version matching or exceeding leading competitors with only 8 NFEs, sub-second inference on H800 GPUs, fits in 16 GB VRAM consumer devices, with photorealistic generation, bilingual English and Chinese text rendering, and robust instruction adherence.[^zimage-turbo-gguf-card]
- **Reported** Base: non-distilled foundation model for community fine-tuning and custom development; listed as to be released in the Model Zoo table at capture time.[^zimage-turbo-gguf-card]
- **Reported** Edit: variant fine-tuned on Z-Image for image editing with instruction-following image-to-image generation; listed as to be released in the Model Zoo table at capture time.[^zimage-turbo-gguf-card]
- **Reported** endpoints: Hugging Face checkpoint and demo Space for `Tongyi-MAI/Z-Image-Turbo`, ModelScope checkpoint and demo, official site, GitHub repo, art-gallery PDF and web gallery, and technical report arXiv `2511.22699`.[^zimage-turbo-gguf-card]

## Architecture and performance (reported)

- **Reported** architecture: Scalable Single-Stream DiT (S3-DiT), concatenating text, visual semantic tokens, and image VAE tokens at the sequence level as one unified input stream, described as maximizing parameter efficiency over dual-stream approaches.[^zimage-turbo-gguf-card]
- **Reported** evaluation: Elo-based human-preference evaluation on Alibaba AI Arena places Z-Image-Turbo as highly competitive against leading models and state-of-the-art among open-source models; no score, date range, variance, or leaderboard snapshot is captured beyond the linked arena and `assets/leaderboard.png` reference.[^zimage-turbo-gguf-card]
- **Reported** showcase scope: photorealistic quality, bilingual text rendering, prompt-enhancing and reasoning, and creative image editing; remote showcase images are summarized here rather than reproduced.[^zimage-turbo-gguf-card]

## Diffusers use (reported)

- **Reported** install: `pip install git+https://github.com/huggingface/diffusers` for the latest diffusers; the card notes PRs `#12703` and `#12715` added Z-Image support and states both were merged into the latest official release.[^zimage-turbo-gguf-card]
- **Reported** load: `ZImagePipeline.from_pretrained("Tongyi-MAI/Z-Image-Turbo", torch_dtype=torch.bfloat16, low_cpu_mem_usage=False)` on CUDA, with optional Flash-Attention backends, transformer compilation, and CPU offloading.[^zimage-turbo-gguf-card]
- **Reported** Turbo generation defaults in the worked example: 1024x1024, `num_inference_steps=9` stated to produce 8 DiT forwards, `guidance_scale=0.0` for Turbo models, seeded generator, and a long Hanfu/portrait prompt saved to `example.png`.[^zimage-turbo-gguf-card]
- **Observed:** no install, download, or generation step was executed for this entry; the snippet and defaults are **reported** usage, not reproduced behavior.[^zimage-turbo-gguf-card]
- **Reported** weight download: `pip install -U huggingface_hub` plus `HF_XET_HIGH_PERFORMANCE=1 hf download Tongyi-MAI/Z-Image-Turbo`.[^zimage-turbo-gguf-card]

## Distillation background (reported)

- **Reported** Decoupled-DMD: core few-step distillation behind the 8-step Z-Image model, arXiv `2511.22677`; the card's insight is that CFG Augmentation drives distillation while Distribution Matching acts as a regularizer, studied separately after decoupling.[^zimage-turbo-gguf-card]
- **Reported** DMDR: post-training fusion of DMD with reinforcement learning, arXiv `2511.13649`, positioned to improve semantic alignment, aesthetic quality, structural coherence, and high-frequency detail; the card's insight is that RL unlocks DMD performance while DMD regularizes RL.[^zimage-turbo-gguf-card]
- **Reported** citations: Z-Image report `team2025zimage` arXiv `2511.22699`, Decoupled-DMD `liu2025decoupled` arXiv `2511.22677`, and DMDR `jiang2025distribution` arXiv `2511.13649` BibTeX entries.[^zimage-turbo-gguf-card]

## Relationships

- Uses the upstream [Z-Image-Turbo Text-to-Image Model](z-image-turbo.md) (`Tongyi-MAI/Z-Image-Turbo`) as its base model; this concept records only the Unsloth GGUF packaging plus the base summary embedded in its card, while the canonical base definition now lives in the linked concept.
- Related to [Z-Image Lookalike LoRA Collection (nphSi)](z-image-lookalike-loras.md), community LoRA adapters reported for `Tongyi-MAI/Z-Image` and `Tongyi-MAI/Z-Image-Turbo`; neither source claims LoRA compatibility with this GGUF quant.
- Shares the Unsloth Dynamic 2.0 method with [Qwen-Image-2.1 GGUF Quantized Checkpoints (Unsloth)](qwen-image-2-1-gguf-unsloth.md) and [Qwen-Image-2512 GGUF Quantized Checkpoints (Unsloth)](qwen-image-2512-gguf-unsloth.md); unlike the 2.1 card, this capture gives no denoiser-only boundary, VAE/encoder filenames, or `sd-cli` invocation.
- For GGUF hosts, see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) and [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md); this card names only the `ggml` library tag and was not verified against either host in this operation.

## Coverage limits

- **Observed:** only `../raw/Z-Image-Turbo-GGUF/README.md` was statically inspected; no code was executed and no quant, download, install, generation, latency, VRAM, arena, bilingual-rendering, or distillation claim was reproduced.
- **Observed:** no immutable revision or capture date is present; freshness is unbounded beyond the local capture.
- **Observed:** uninspected material outside this scope includes all `assets/` sample, showcase, architecture, decoupled-DMD, DMDR, and leaderboard images, the art-gallery PDF, and linked Hugging Face, ModelScope, GitHub, blog, demo, docs, Discord, and arXiv targets.
- **Observed:** a separate local capture `../raw/Z-Image-Turbo/` existed uninspected at the time of this concept's creation and is now compiled as [Z-Image-Turbo Text-to-Image Model](z-image-turbo.md); do not treat the base-model summary recorded here as a substitute for that canonical base concept.

[^zimage-turbo-gguf-card]: Model-card README capture in `../raw/Z-Image-Turbo-GGUF/README.md`; GGUF identity, Dynamic 2.0 upcasting note, and Unsloth/docs links from header note; `base_model`, `apache-2.0`, `en`, `text-to-image`, `ggml`, and `gguf/quantized/unsloth` tags plus sloth widget from frontmatter; four `assets/sloth_*` samples from Samples table; 6B size, three Turbo/Base/Edit variants, 8-NFE, H800 sub-second, 16 GB VRAM, photoreal, bilingual, and instruction claims from Z-Image section; Model Zoo release status from Model Zoo table; S3-DiT unified-stream claim from Model Architecture; Alibaba AI Arena Elo and open-source SOTA claim from Performance; `pip install` diffusers, PR `#12703`/`#12715` note, `ZImagePipeline.from_pretrained("Tongyi-MAI/Z-Image-Turbo")`, bfloat16, attention/compile/offload options, 1024x1024, 9 steps for 8 forwards, CFG 0.0, and seed 42 from Quick Start; Decoupled-DMD CA/DM insight and arXiv `2511.22677` plus DMDR RL/DMD insight and arXiv `2511.13649` from their sections; `hf download` command from Download; three BibTeX entries from Citation; checkpoint, demo, site, repo, gallery, and ModelScope endpoints from badges.
