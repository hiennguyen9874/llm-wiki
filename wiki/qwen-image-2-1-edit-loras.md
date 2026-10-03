---
type: Concept
title: Qwen-Image-2.1 Edit LoRAs (WarmBloodAban)
description: Community edit-focused LoRA pair for anime character consistency and realistic character conversion on Qwen-Image-2.1.
tags: [qwen, lora, image-editing, anime, photorealism]
status: draft
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T12:00:00Z }
sources:
  - id: warmblood-qwen-edit-loras
    resource: ../raw/Qwen-Image-2.1-LoRAs/README.md
    scope: ../raw/Qwen-Image-2.1-LoRAs/
    kind: documentation
    title: Qwen-Image-2.1-LoRAs model card
---

Qwen-Image-2.1-Edit-LoRAs is a community LoRA collection reported to extend `Qwen/Qwen-Image-2.1` image-editing with two functional variants — anime character consistency and anything-to-realistic-character conversion — loaded on top of the unchanged base model with LoRA weight around 0.6–0.8.[^warmblood-qwen-edit-loras]

## Variants and reported training

- **Reported** identity: LoRAs specifically fine-tuned for the image-editing capabilities of `Qwen-Image-2.1`; the collection is presented as continuously updated with functional and stylistic additions.[^warmblood-qwen-edit-loras]
- **Reported** `Qwen2.1_Anime_consistency`: enhances character consistency during anime-style image editing; primarily fine-tuned on character model sheets (4-view references) and facial-expression edits.[^warmblood-qwen-edit-loras]
- **Reported** `Qwen2.1_Anything2RealCharacters`: transforms images from any artistic style into realistic human character images; primarily fine-tuned on real-human images paired with facial-expression control reference groups.[^warmblood-qwen-edit-loras]
- **Observed** packaging: frontmatter declares `base_model: Qwen/Qwen-Image-2.1`, `license: apache-2.0`, `tags` including `text-to-image`, `lora`, `diffusers`, and `template: diffusion-lora`; `instance_prompt` is null.[^warmblood-qwen-edit-loras]
- **Synthesis:** the two variants answer different editing questions (consistency preservation versus style-to-realism conversion) but share one package, base model, and weight guidance, so one concept covers both.

## Compatibility and use

- **Reported** base settings: follow the official Qwen-Image-2.1 recommended sampling steps and CFG scale; start LoRA weight between `0.6` and `0.8` and adjust to the editing need.[^warmblood-qwen-edit-loras]
- **Reported** realism-variant settings: sampler `Euler` with `FlowMatchEulerDiscreteScheduler` for softer, more authentic high-fidelity realistic character rendering.[^warmblood-qwen-edit-loras]
- **Reported** download: Files-and-versions tab under `/WarmBloodAban/Qwen-Image-2.1-LoRAs/tree/main`; the weights themselves were not captured locally and remain uninspected.[^warmblood-qwen-edit-loras]
- **Synthesis:** no Diffusers/ComfyUI loader snippet, resolution, seed, CFG value, or step count is given in the capture, so reuse depends on the official base-model documentation plus weight tuning.

## Limitations and qualifiers

- **Reported** maturity: `Qwen2.1_Anime_consistency` is explicitly experimental, developed to test and benchmark optimal training parameters for Qwen Image 2.1; specific editing outcomes and output stability are not guaranteed.[^warmblood-qwen-edit-loras]
- **Reported** evidence type: a single remote preview image for the realism variant; no side-by-side benchmark, metric, evaluation protocol, or failure-mode breakdown is given for either variant.[^warmblood-qwen-edit-loras]
- **Synthesis:** treat both adapters as unverified community edits — plausible for character-consistency and realism experiments, but with no reproduced measurement in this wiki entry.

## Relationships

- Uses the upstream `Qwen/Qwen-Image-2.1` base model; this concept records only the WarmBloodAban edit-LoRA packaging and settings, not the base model's own behavior.
- Related to [Qwen-Image-2.1-Fix LoRA Adapter](qwen-image-2-1-fix.md), which targets general generation-issue reduction on the same base; this source claims editing-specific consistency/conversion, a distinct capability neither source claims about the other.
- Related to [Pruna Qwen-Image-2.1 Few-Step LoRA Adapters](pruna-qwen-image-2-1.md), which targets fewer-step inference speed on the same base; this source targets edit style/consistency with base-regime steps, a distinct optimization axis.
- For structural control and inpainting on the same base family, see [Qwen-Image-2.1-Fun ControlNet-Union Branch](qwen-image-2-1-fun-controlnet-union.md); neither source claims the other's capability.

## Coverage limits

- **Observed:** only `../raw/Qwen-Image-2.1-LoRAs/README.md` was statically inspected; no code was executed and no editing claim was reproduced.
- **Observed:** uncaptured/uninspected material includes the LoRA weights behind the Files-and-versions download target, the `images/2b2fbfd3-e134-4eff-b98a-a5e17c906539.png` widget asset, the remote realism-variant preview image, and the `Qwen/Qwen-Image-2.1` base weights.
- Community and commercial contact details listed in the source (video channels, group/chat handles, email) were excluded as non-durable personal data with no retrieval value.
- Freshness is unbounded: the capture carries no publication date or immutable revision, so future LoRA additions or weight updates would be a new revision.

[^warmblood-qwen-edit-loras]: Hugging Face model-card capture in `../raw/Qwen-Image-2.1-LoRAs/README.md`; collection identity and continuous-update intent from title and intro; variant overviews, training data, experimental disclaimer, and Euler/FlowMatchEulerDiscreteScheduler tip from Available Models section; steps/CFG/0.6–0.8 weight guidance from Recommended Parameters section; Files-and-versions download target from Download model section; `base_model`, `license: apache-2.0`, `tags`, `template: diffusion-lora`, and `instance_prompt: null` from YAML frontmatter.
