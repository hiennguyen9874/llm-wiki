---
type: Concept
title: Qwen-Image-2512 GGUF Quantized Checkpoints (Unsloth)
description: Unsloth Dynamic 2.0 GGUF quants of the Qwen-Image-2512 December text-to-image model with ComfyUI and stable-diffusion.cpp guides.
tags: [qwen, gguf, quantization, unsloth, image-generation, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T11:55:00Z }
sources:
  - id: unsloth-2512-gguf-readme
    resource: ../raw/Qwen-Image-2512-GGUF/README.md
    scope: ../raw/Qwen-Image-2512-GGUF/
    kind: documentation
    title: Unsloth Qwen-Image-2512-GGUF model card
---

Unsloth's package provides Dynamic 2.0 GGUF quantized checkpoints of `Qwen/Qwen-Image-2512` for local text-to-image generation, with run guides for ComfyUI and stable-diffusion.cpp and tooling credited to ComfyUI-GGUF.[^unsloth-2512-gguf-readme]

## Quantization and packaging

- **Reported** base: GGUF quantized version of [Qwen-Image-2512](https://huggingface.co/Qwen/Qwen-Image-2512), with frontmatter `base_model: Qwen/Qwen-Image-2512`.[^unsloth-2512-gguf-readme]
- **Reported** method: Unsloth Dynamic 2.0, described as upcasting important layers to higher precision for improved performance over uniform quantization.[^unsloth-2512-gguf-readme]
- **Reported** tooling: uses tooling from [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) by city96.[^unsloth-2512-gguf-readme]
- **Reported** hosts: guides for [ComfyUI](https://unsloth.ai/docs/models/qwen-image-2512) and [stable-diffusion.cpp](https://unsloth.ai/docs/models/qwen-image-2512/stable-diffusion.cpp); the card points to the Unsloth run guide as the primary how-to entry point.[^unsloth-2512-gguf-readme]
- **Observed** component boundary: unlike the Unsloth Qwen-Image-2.1 GGUF card, this capture does not state a denoiser-only boundary nor separate VAE/text-encoder filenames; do not assume the same triple without a fuller listing.
- **Observed** task tagging: frontmatter declares `pipeline_tag: text-to-image`, `language: [en, zh]`, and `tags` including `gguf`, `quantized`, `unsloth`, and `qwen`.[^unsloth-2512-gguf-readme]

## Base-model context (reported)

- **Reported** identity: Qwen-Image-2512 is the December update of the Qwen-Image text-to-image foundation model, compared against the August Qwen-Image base release; Qwen Chat is named as a hosted try-out path.[^unsloth-2512-gguf-readme]
- **Reported** improvements over August base:[^unsloth-2512-gguf-readme]
  - Enhanced human realism with reduced AI-generated look, especially for human subjects.
  - Finer natural detail for landscapes, animal fur, and other natural elements.
  - Improved text rendering with better accuracy, layout, and multimodal text-plus-image composition.
- **Reported** evaluation: over 10,000 rounds of blind evaluations on AI Arena are claimed to place Qwen-Image-2512 as currently the strongest open-source model while remaining competitive with closed-source models; no protocol, date range, variance, or leaderboard snapshot is given, so treat as a **reported** vendor claim, not a reproduced benchmark.[^unsloth-2512-gguf-readme]
- **Reported** showcase scope: human portraits and group scenes, canyon/waterfall and lighthouse seascape landscapes, golden-retriever and argali-sheep fur/texture studies, and Chinese-language text-rich PPT, before-and-after comparison, industrial infographic, and 12-panel daily-life poster examples; prompts and remote images are summarized here rather than reproduced.[^unsloth-2512-gguf-readme]

## Diffusers defaults (reported)

- **Reported** install: `pip install git+https://github.com/huggingface/diffusers` for the latest diffusers.[^unsloth-2512-gguf-readme]
- **Reported** load: `DiffusionPipeline.from_pretrained("Qwen/Qwen-Image-2512", torch_dtype=torch.bfloat16)` on CUDA, else `torch.float32` on CPU.[^unsloth-2512-gguf-readme]
- **Reported** generation defaults in the worked example: `num_inference_steps=50`, `true_cfg_scale=4.0`, seeded generator (`manual_seed(42)`), with both `prompt` and Chinese `negative_prompt` inputs.[^unsloth-2512-gguf-readme]
- **Reported** aspect-ratio resolutions:[^unsloth-2512-gguf-readme]

| Ratio | Resolution |
|---|---|
| 1:1 | 1328 × 1328 |
| 16:9 | 1664 × 928 |
| 9:16 | 928 × 1664 |
| 4:3 | 1472 × 1104 |
| 3:4 | 1104 × 1472 |
| 3:2 | 1584 × 1056 |
| 2:3 | 1056 × 1584 |

- **Observed:** no install, download, or generation step was executed for this entry; the snippet and resolutions are **reported** usage, not reproduced behavior.
- **Reported** citation: Qwen-Image Technical Report, `wu2025qwenimagetechnicalreport`, arXiv `2508.02324`.[^unsloth-2512-gguf-readme]

## Licensing and support boundaries

- **Observed** license frontmatter states `apache-2.0`, unlike the `qwen-research` licensing recorded for Qwen-Image-2.1; this is a **reported** disclosure boundary, not legal verification.[^unsloth-2512-gguf-readme]
- **Observed** upstream endpoints named in the card: Hugging Face (`Qwen/Qwen-Image-2512`), ModelScope, Qwen Chat, tech-report PDF, blog, demo Space, GitHub repo, Discord, and WeChat; details beyond the card are delegated to those targets.[^unsloth-2512-gguf-readme]

## Relationships

- Uses the upstream `Qwen/Qwen-Image-2512` base model; this concept records only the Unsloth GGUF packaging, run-guide pointers, and base-improvement summary, not a full base-model definition.
- Related to [Qwen-Image-2.1 GGUF Quantized Checkpoints (Unsloth)](qwen-image-2-1-gguf-unsloth.md), which specifies Dynamic 2.0 per-tensor handling plus an explicit denoiser-plus-VAE-plus-Qwen3-VL-encoder triple and `sd-cli` invocation; this 2512 capture shares the Dynamic 2.0 claim but leaves the component triple unstated.
- Shares the Qwen image family with [Qwen-Image-2.1 Text-to-Image and Editing Model](qwen-image-2-1.md); the 2512 card positions itself against the August Qwen-Image base rather than against 2.1, so no supersession is recorded.
- For GGUF hosts, see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) for the ComfyUI custom-node path named as this source's tooling and [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md) for the ggml-based engine named by its second guide; neither host concept was verified against this quant in this operation.

## Coverage limits

- **Observed:** only `../raw/Qwen-Image-2512-GGUF/README.md` was statically inspected; no code was executed and no quant, download, install, generation, arena, or text-rendering claim was reproduced.
- **Observed:** no immutable revision or capture date is present; freshness is unbounded beyond the local capture.
- **Observed:** uninspected material outside this scope includes the upstream base weights, Unsloth run-guide docs, ComfyUI-GGUF code, all `assets/` sample images referenced but absent locally, and linked Hugging Face, ModelScope, Qwen Chat, tech-report, blog, demo, Discord, and WeChat targets.

[^unsloth-2512-gguf-readme]: Model-card README capture in `../raw/Qwen-Image-2512-GGUF/README.md`; GGUF identity, Dynamic 2.0 per-tensor upcasting note, ComfyUI-GGUF tooling credit, and ComfyUI plus stable-diffusion.cpp guide pointers from header; `base_model`, `apache-2.0`, `en/zh`, `text-to-image`, and `gguf/quantized/unsloth/qwen` tags from frontmatter; December-update identity, three improvements, and Qwen Chat pointer from Introduction; 10,000-round AI Arena claim from Model Performance; `pip install` diffusers, `DiffusionPipeline.from_pretrained("Qwen/Qwen-Image-2512")`, 50-step, `true_cfg_scale 4.0`, seed 42, aspect-ratio table, and negative-prompt pattern from Quick Start; showcase categories from Showcase headings and prompts; BibTeX `wu2025qwenimagetechnicalreport` arXiv 2508.02324 from Citation; upstream endpoints from header links.
