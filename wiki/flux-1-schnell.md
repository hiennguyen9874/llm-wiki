---
type: Concept
title: FLUX.1-schnell Text-to-Image Model
description: Black Forest Labs 12B rectified flow text-to-image model with latent adversarial diffusion distillation for 1-4 step inference under Apache-2.0.
tags: [flux, text-to-image, diffusion, local-inference, image-generation]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T00:00:00Z }
sources:
  - id: flux-schnell-readme
    resource: ../raw/FLUX.1-schnell/README.md
    scope: ../raw/FLUX.1-schnell/
    kind: documentation
    title: FLUX.1-schnell model card
---

FLUX.1 [schnell] is a **reported** 12 billion parameter rectified flow transformer for text-to-image generation, trained with latent adversarial diffusion distillation for high-quality output in only 1 to 4 steps and released under Apache-2.0 for personal, scientific, and commercial use.[^flux-schnell-readme]

## Identity and key features

- **Reported** identity: 12B parameter rectified flow transformer capable of generating images from text descriptions; creator Black Forest Labs via Hugging Face `black-forest-labs/FLUX.1-schnell`.[^flux-schnell-readme]
- **Reported** quality and prompt following: cutting-edge output quality and competitive prompt following, matching the performance of closed source alternatives.[^flux-schnell-readme]
- **Reported** efficiency mechanism: trained using latent adversarial diffusion distillation, enabling high-quality generation in only 1 to 4 steps.[^flux-schnell-readme]
- **Reported** openness and reuse: released under the `apache-2.0` licence; the model can be used for personal, scientific, and commercial purposes.[^flux-schnell-readme]
- **Reported** announcement pointer: model header points to the Black Forest Labs blog post for more information; the post itself was not captured locally and remains uninspected.[^flux-schnell-readme]

## Usage

- **Reported** reference implementation: sampling code and reference implementation in dedicated GitHub repository `black-forest-labs/flux`, encouraged as starting point for developers and creatives building on top; that repository was not captured locally and remains uninspected.[^flux-schnell-readme]
- **Reported** API hosts: `bfl.ml` docs (currently `FLUX.1 [pro]`), `replicate.com` Flux collection, `fal.ai` `fal-ai/flux/schnell`, and `mystic.ai` `black-forest-labs/flux1-schnell`; no endpoint was called or verified.[^flux-schnell-readme]
- **Reported** ComfyUI availability: available in Comfy UI for local inference with a node-based workflow; specific workflow or version is not pinned in this capture.[^flux-schnell-readme]
- **Reported** Diffusers procedure: install or upgrade with `pip install -U diffusers`, then run `FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16)` with `enable_model_cpu_offload()` for VRAM savings; example generation uses prompt `A cat holding a sign that says hello world`, `guidance_scale=0.0`, `num_inference_steps=4`, `max_sequence_length=256`, seeded `torch.Generator("cpu").manual_seed(0)`, saving to `flux-schnell.png`.[^flux-schnell-readme]
- **Synthesis:** treat the Diffusers snippet as a **reported** entry-point example, not a reproduced run; no install, download, or generation was executed for this concept.[^flux-schnell-readme]

## Limitations

- **Reported** factuality: model is not intended or able to provide factual information.[^flux-schnell-readme]
- **Reported** bias: as a statistical model this checkpoint might amplify existing societal biases.[^flux-schnell-readme]
- **Reported** prompt mismatch: model may fail to generate output that matches the prompts.[^flux-schnell-readme]
- **Reported** prompting sensitivity: prompt following is heavily influenced by prompting style.[^flux-schnell-readme]

## Out-of-scope prohibitions

The card lists these **reported** prohibited derivative uses; this is a disclosure boundary, not legal verification:[^flux-schnell-readme]

- Violating applicable law or regulation.
- Exploiting or harming minors, including solicitation, creation, acquisition, or dissemination of child-exploitative content.
- Generating or disseminating verifiably false information to harm others.
- Generating or disseminating personal identifiable information usable to harm an individual.
- Harassing, abusing, threatening, stalking, or bullying individuals or groups.
- Creating non-consensual nudity or illegal pornographic content.
- Fully automated decision-making that adversely impacts legal rights or creates or modifies a binding enforceable obligation.
- Generating or facilitating large-scale disinformation campaigns.

## License and disclosure boundary

- **Reported** license: `apache-2.0` per file frontmatter; no separate license file is captured in this scope.[^flux-schnell-readme]
- **Observed:** no immutable revision hash, publication date, or local capture date is present in `README.md`; freshness is unbounded beyond local capture.
- **Synthesis:** verify current license and gated terms upstream before reuse; frontmatter also declares language `en` and tags `text-to-image`, `image-generation`, `flux`.[^flux-schnell-readme]

## Relationships

- Sibling of [FLUX.1-dev Text-to-Image Model](flux-1-dev.md): schnell uses latent adversarial diffusion distillation for 1–4 steps with `guidance_scale=0.0` under Apache-2.0, while dev uses guidance distillation with a 50-step `guidance_scale=3.5` example under a non-commercial license.
- For pre-quantized schnell GGUF availability in ComfyUI, see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md); for a separate ggml-based local engine that reports FLUX.1-dev/schnell support, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md).
- Contrasts with closed-source alternatives referenced only as prompt-following comparators; no benchmark, dataset, or metric is given in this capture to support the comparison.

## Coverage limits

- **Observed:** only `../raw/FLUX.1-schnell/README.md` was statically inspected; no code was executed and no install, API, ComfyUI, Diffusers, quality, efficiency, or bias claim was reproduced.
- **Observed:** the referenced grid image `./schnell_grid.jpeg` is absent from `../raw/FLUX.1-schnell/` locally and was not inspected.
- **Observed:** uninspected material outside this scope includes the upstream `black-forest-labs/flux` repository, Black Forest Labs blog post, all four API hosts, ComfyUI project, Diffusers `flux` pipeline docs, and any license file beyond the frontmatter declaration.
- All capability, compatibility, efficiency, quality, and permission statements above are **reported** by the model card, not independently verified.
- No measurements, evaluation protocol, variance, ablations, or negative-result analysis beyond the Limitations list are present in this capture.

[^flux-schnell-readme]: Model-card capture in `../raw/FLUX.1-schnell/README.md`; 12B rectified-flow identity and blog pointer from header; quality, prompt-following, latent adversarial diffusion distillation with 1–4 steps, and Apache-2.0 personal/scientific/commercial use from Key Features; reference implementation, API hosts, ComfyUI, and Diffusers install plus `FluxPipeline` parameters from Usage; factuality, bias, mismatch, and prompting-style limits from Limitations; eight prohibitions from Out-of-Scope Use; `apache-2.0` license, language, and tags from YAML frontmatter.
