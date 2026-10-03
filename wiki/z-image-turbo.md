---
type: Concept
title: Z-Image-Turbo Text-to-Image Model
description: Tongyi-MAI 6B single-stream DiT distilled checkpoint for 8-NFE text-to-image inference with bilingual rendering under Apache-2.0.
tags: [z-image, text-to-image, diffusion-transformer, turbo, bilingual, diffusers, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T12:00:00Z }
sources:
  - id: zimage-turbo-card
    resource: ../raw/Z-Image-Turbo/README.md
    scope: ../raw/Z-Image-Turbo/
    kind: documentation
    title: Z-Image-Turbo model card (Tongyi-MAI)
---

Z-Image-Turbo is the **reported** distilled release checkpoint of the Tongyi-MAI Z-Image family, described as a 6B-parameter efficient image-generation foundation model that matches or exceeds leading competitors with only 8 NFEs and sub-second inference on H800 GPUs while fitting in 16 GB VRAM consumer devices.[^zimage-turbo-card]

## Identity and model family

- **Observed** task tagging: frontmatter declares `pipeline_tag: text-to-image`, `library_name: diffusers`, `language: [en]`, and `license: apache-2.0`.[^zimage-turbo-card]
- **Reported** family: Z-Image is a 6B-parameter family with four variants named in the card — Turbo, base Z-Image, Omni-Base, and Edit.[^zimage-turbo-card]
- **Reported** Turbo: distilled version of Z-Image for fast generation; photorealistic generation, bilingual English and Chinese text rendering, and robust instruction adherence.[^zimage-turbo-card]
- **Reported** base Z-Image: foundation model behind Turbo, focused on high-quality generation, rich aesthetics, strong diversity, and controllability; suited for creative generation, fine-tuning, and downstream development, with wide artistic styles, negative prompting, and diversity across identities, poses, compositions, and layouts.[^zimage-turbo-card]
- **Reported** Omni-Base: versatile foundation model for both generation and editing, positioned as the most raw and diverse starting point for community fine-tuning and custom development.[^zimage-turbo-card]
- **Reported** Edit: variant fine-tuned on Z-Image for image editing, supporting creative image-to-image generation with instruction-following natural-language edits and bilingual editing understanding.[^zimage-turbo-card]
- **Observed** Model Zoo table status:[^zimage-turbo-card]

| Model | Pre-Training | SFT | RL | Step | CFG | Task | Visual Quality | Diversity | Fine-Tunability |
|---|---|---|---|---|---|---|---|---|---|
| Z-Image-Omni-Base | ✅ | ❌ | ❌ | 50 | ✅ | Gen. / Editing | Medium | High | Easy |
| Z-Image | ✅ | ✅ | ❌ | 50 | ✅ | Gen. | High | Medium | Easy |
| Z-Image-Turbo | ✅ | ✅ | ✅ | 8 | ❌ | Gen. | Very High | Low | N/A |
| Z-Image-Edit | ✅ | ✅ | ❌ | 50 | ✅ | Editing | High | Medium | Easy |

- **Observed** release status in the same table: Z-Image and Z-Image-Turbo link to released Hugging Face and ModelScope checkpoints and demos; Omni-Base and Edit are listed as *To be released* at capture time.[^zimage-turbo-card]
- **Synthesis:** Turbo trades the reported diversity and fine-tunability of the base/Omni variants for very-high visual quality at 8 steps without CFG; use base or Omni-Base when the task needs fine-tuning or diverse identities, poses, and layouts.

## Capabilities (reported)

- **Reported** speed: 8 NFEs, sub-second inference latency on enterprise H800 GPUs, fits in 16 GB VRAM consumer devices.[^zimage-turbo-card]
- **Reported** photorealistic quality with strong aesthetic quality.[^zimage-turbo-card]
- **Reported** accurate bilingual text rendering for complex Chinese and English text.[^zimage-turbo-card]
- **Reported** prompt enhancing and reasoning: a Prompt Enhancer gives reasoning over surface descriptions using world knowledge.[^zimage-turbo-card]
- All capability claims above are **reported** by the model card and showcase captions; no generation, latency, VRAM, rendering, or reasoning claim was reproduced here.

## Architecture (reported)

- **Reported** architecture: Scalable Single-Stream DiT (S3-DiT); text, visual semantic tokens, and image VAE tokens are concatenated at the sequence level as one unified input stream, described as maximizing parameter efficiency compared with dual-stream approaches.[^zimage-turbo-card]
- **Observed:** no code, weights, or diagram file was inspected to verify the architecture; the `assets/architecture.webp` diagram is referenced but not captured locally.[^zimage-turbo-card]

## Performance (reported)

- **Reported** evaluation: Elo-based human-preference evaluation on Alibaba AI Arena places Z-Image-Turbo as highly competitive against leading models and state-of-the-art among open-source models.[^zimage-turbo-card]
- **Observed:** no score, date range, variance, voter count, or leaderboard snapshot is captured beyond the linked arena URL and the `assets/leaderboard.png` reference.[^zimage-turbo-card]

## Diffusers use (reported)

All procedures below are **reported**; no install, download, or generation was executed for this concept.

- **Reported** install: `pip install git+https://github.com/huggingface/diffusers`; the card notes diffusers PRs `#12703` and `#12715` added Z-Image support and states both were merged into the latest official release.[^zimage-turbo-card]
- **Reported** load: `ZImagePipeline.from_pretrained("Tongyi-MAI/Z-Image-Turbo", torch_dtype=torch.bfloat16, low_cpu_mem_usage=False)` on CUDA, with optional Flash-Attention-2 (`flash`) or Flash-Attention-3 (`_flash_3`) backends, transformer compilation, and CPU offloading.[^zimage-turbo-card]
- **Reported** Turbo generation defaults in the worked example: 1024×1024, `num_inference_steps=9` stated to produce 8 DiT forwards, `guidance_scale=0.0` for Turbo models, seeded CUDA generator, and a long Hanfu/portrait prompt saved to `example.png`.[^zimage-turbo-card]
- **Reported** weight download: `pip install -U huggingface_hub` plus `HF_XET_HIGH_PERFORMANCE=1 hf download Tongyi-MAI/Z-Image-Turbo`.[^zimage-turbo-card]

## Distillation background (reported)

- **Reported** Decoupled-DMD: core few-step distillation behind the 8-step Z-Image model, arXiv `2511.22677`; the card's insight is that CFG Augmentation drives distillation while Distribution Matching acts as a regularizer, studied separately after decoupling.[^zimage-turbo-card]
- **Reported** DMDR: post-training fusion of DMD with reinforcement learning, arXiv `2511.13649`, positioned to improve semantic alignment, aesthetic quality, structural coherence, and high-frequency detail; the card's insight is that RL unlocks DMD performance while DMD regularizes RL.[^zimage-turbo-card]
- **Reported** citations: Z-Image report `team2025zimage` arXiv `2511.22699`, Decoupled-DMD `liu2025decoupled` arXiv `2511.22677`, and DMDR `jiang2025distribution` arXiv `2511.13649` BibTeX entries.[^zimage-turbo-card]

## Endpoints and licensing

- **Observed** license: frontmatter declares `apache-2.0`.[^zimage-turbo-card]
- **Reported** endpoints: official site, GitHub `Tongyi-MAI/Z-Image` repo, Hugging Face `Tongyi-MAI/Z-Image-Turbo` checkpoint and demo Space, akhaliq mobile demo Space, ModelScope checkpoint and demo, art-gallery PDF, web art gallery, and technical report arXiv `2511.22699`.[^zimage-turbo-card]

## Relationships

- Base model packaged by [Z-Image-Turbo GGUF Quantized Checkpoints (Unsloth)](z-image-turbo-gguf-unsloth.md) for local GGUF inference; that concept records only the Unsloth packaging plus the base summary embedded in its card.
- Base checkpoint reported by [Z-Image Lookalike LoRA Collection (nphSi)](z-image-lookalike-loras.md) alongside `Tongyi-MAI/Z-Image`; neither source claims LoRA compatibility with the GGUF quant.
- For comparable few-step distilled text-to-image coverage with different licensing and step regimes, see [FLUX.1-schnell Text-to-Image Model](flux-1-schnell.md), [Krea 2 Turbo Text-to-Image Model](krea-2-turbo.md), [Qwen-Image-2.1 Viggle Turbo Few-Step LoRA](qwen-image-2-1-viggle-turbo.md), and [Pruna Qwen-Image-2.1 Few-Step LoRA Adapters](pruna-qwen-image-2-1.md).
- For GGUF hosts that may run Turbo-derived quants, see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) and [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md); this card names only the `diffusers` library and was not verified against either host in this operation.

## Coverage limits

- **Observed:** only `../raw/Z-Image-Turbo/README.md` was statically inspected; no code was executed and no install, download, generation, latency, VRAM, arena, bilingual-rendering, reasoning, or distillation claim was reproduced.
- **Observed:** no immutable revision or capture date is present; freshness is unbounded beyond the local capture.
- **Observed:** uninspected material outside this scope includes all `assets/` showcase, reasoning, architecture, decoupled-DMD, DMDR, and leaderboard images, the `assets/Z-Image-Gallery.pdf` art gallery, and linked Hugging Face, ModelScope, GitHub, blog, demo, docs, and arXiv targets.

[^zimage-turbo-card]: Official model-card capture in `../raw/Z-Image-Turbo/README.md`; `apache-2.0`, `en`, `text-to-image`, and `diffusers` tags from YAML frontmatter; 6B size, four Turbo/Base/Omni-Base/Edit variants, 8-NFE, H800 sub-second, 16 GB VRAM, photoreal, bilingual, and instruction claims from Z-Image section; training/SFT/RL, step, CFG, task, quality, diversity, tunability, and release status from Model Zoo table; photoreal, bilingual-rendering, prompt-enhancing/reasoning, and editing showcase scope from Showcase; S3-DiT unified-stream claim from Model Architecture; Alibaba AI Arena Elo and open-source SOTA claim from Performance; `pip install` diffusers, PR `#12703`/`#12715` note, `ZImagePipeline.from_pretrained("Tongyi-MAI/Z-Image-Turbo")`, bfloat16, attention/compile/offload options, 1024×1024, 9 steps for 8 forwards, and CFG 0.0 from Quick Start; Decoupled-DMD CA/DM insight and arXiv `2511.22677` plus DMDR RL/DMD insight and arXiv `2511.13649` from their sections; `hf download` command from Download; three BibTeX entries from Citation; checkpoint, demo, mobile demo, site, repo, gallery, and ModelScope endpoints from badges and Model Zoo links.
