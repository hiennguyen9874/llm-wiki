---
type: Concept
title: FLUX.1-dev Text-to-Image Model
description: Black Forest Labs 12B rectified flow text-to-image model with guidance distillation and non-commercial licensing.
tags: [flux, text-to-image, diffusion, local-inference, image-generation]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T00:00:00Z }
sources:
  - id: flux-dev-readme
    resource: ../raw/FLUX.1-dev/README.md
    scope: ../raw/FLUX.1-dev/
    kind: documentation
    title: FLUX.1-dev model card
---

FLUX.1 [dev] is a **reported** 12 billion parameter rectified flow transformer for text-to-image generation, positioned second only to FLUX.1 [pro] on output quality with competitive prompt following and guidance-distilled efficiency under a non-commercial license.[^flux-dev-readme]

## Identity and key features

- **Reported** identity: 12B parameter rectified flow transformer capable of generating images from text descriptions; creator Black Forest Labs via Hugging Face `black-forest-labs/FLUX.1-dev`.[^flux-dev-readme]
- **Reported** quality rank: cutting-edge output quality, second only to state-of-the-art `FLUX.1 [pro]`.[^flux-dev-readme]
- **Reported** prompt following: competitive with closed-source alternatives, heavily influenced by prompting style.[^flux-dev-readme]
- **Reported** efficiency mechanism: trained using guidance distillation, making `FLUX.1 [dev]` more efficient.[^flux-dev-readme]
- **Reported** openness rationale: open weights to drive scientific research and empower artists to develop innovative workflows.[^flux-dev-readme]
- **Reported** output-use permission: generated outputs can be used for personal, scientific, and commercial purposes as described in the `FLUX.1 [dev]` Non-Commercial License.[^flux-dev-readme]

## Usage

- **Reported** reference implementation: sampling code and reference implementation in dedicated GitHub repository `black-forest-labs/flux`, encouraged as starting point for developers and creatives building on top; repository itself was not captured locally and remains uninspected.[^flux-dev-readme]
- **Reported** API hosts: `bfl.ml` docs (currently `FLUX.1 [pro]`), `replicate.com` Flux collection, `fal.ai` `fal-ai/flux/dev`, and `mystic.ai` `black-forest-labs/flux1-dev`; no endpoint was called or verified.[^flux-dev-readme]
- **Reported** ComfyUI availability: available in ComfyUI for local inference with node-based workflow; specific workflow or version is not pinned in this capture.[^flux-dev-readme]
- **Reported** Diffusers procedure: install or upgrade with `pip install -U diffusers`, then run `FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-dev", torch_dtype=torch.bfloat16)` with `enable_model_cpu_offload()` for VRAM savings; example generation uses prompt `A cat holding a sign that says hello world`, `height=1024`, `width=1024`, `guidance_scale=3.5`, `num_inference_steps=50`, `max_sequence_length=512`, seeded `torch.Generator("cpu").manual_seed(0)`, saving to `flux-dev.png`.[^flux-dev-readme]
- **Synthesis:** treat the Diffusers snippet as a **reported** entry-point example, not a reproduced run; no install, download, or generation was executed for this concept.[^flux-dev-readme]

## Limitations

- **Reported** factuality: model is not intended or able to provide factual information.[^flux-dev-readme]
- **Reported** bias: as a statistical model this checkpoint might amplify existing societal biases.[^flux-dev-readme]
- **Reported** prompt mismatch: model may fail to generate output that matches the prompts.[^flux-dev-readme]
- **Reported** prompting sensitivity: prompt following is heavily influenced by prompting style.[^flux-dev-readme]

## Out-of-scope prohibitions

The card lists these **reported** prohibited derivative uses; this is a disclosure boundary, not legal verification:[^flux-dev-readme]

- Violating applicable law or regulation.
- Exploiting or harming minors, including solicitation, creation, acquisition, or dissemination of child-exploitative content.
- Generating or disseminating verifiably false information to harm others.
- Generating or disseminating personal identifiable information usable to harm an individual.
- Harassing, abusing, threatening, stalking, or bullying individuals or groups.
- Creating non-consensual nudity or illegal pornographic content.
- Fully automated decision-making that adversely impacts legal rights or creates or modifies a binding enforceable obligation.
- Generating or facilitating large-scale disinformation campaigns.

## License and disclosure boundary

- **Reported** license: falls under `FLUX.1 [dev]` Non-Commercial License linked as `LICENSE.md` on Hugging Face; frontmatter names `flux-1-dev-non-commercial-license` with `extra_gated_prompt` requiring agreement to that license plus acknowledgment of the Acceptable Use Policy.[^flux-dev-readme]
- **Observed:** no immutable revision hash, publication date, or local capture date is present in `README.md`; freshness is unbounded beyond local capture.
- **Synthesis:** verify current license, POLICY.md, and gated terms upstream before commercial or derivative reuse; the capture links but does not inline the full license text.

## Relationships

- For a ComfyUI host that lists pre-quantized FLUX.1-dev GGUF support, see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md); for a separate ggml-based local engine that reports FLUX.1-dev/schnell support, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md).
- Contrasts with closed-source alternatives referenced only as prompt-following comparators; no benchmark, dataset, or metric is given in this capture to support the comparison.

## Coverage limits

- **Observed:** only `../raw/FLUX.1-dev/README.md` was statically inspected; no code was executed and no install, API, ComfyUI, Diffusers, quality, efficiency, or bias claim was reproduced.
- **Observed:** uninspected material outside this scope includes `./dev_grid.jpg` grid image, upstream `black-forest-labs/flux` repository, Black Forest Labs blog post, all four API hosts, ComfyUI project, Diffusers `flux` pipeline docs, `LICENSE.md`, and `POLICY.md`.
- All capability, compatibility, efficiency, quality-rank, and permission statements above are **reported** by the model card, not independently verified.
- No measurements, evaluation protocol, variance, ablations, or negative-result analysis beyond the Limitations list are present in this capture.

[^flux-dev-readme]: Model-card capture in `../raw/FLUX.1-dev/README.md`; 12B rectified-flow identity and blog pointer from header; quality, prompt-following, guidance-distillation, open-weights, and output-use claims from Key Features; reference implementation, API hosts, ComfyUI, and Diffusers install plus `FluxPipeline` parameters from Usage; factuality, bias, mismatch, and prompting-style limits from Limitations; eight prohibitions from Out-of-Scope Use; non-commercial license plus frontmatter `license_name`, `license_link`, and `extra_gated_prompt` from License and YAML frontmatter.
