---
type: Concept
title: Z-Image Lookalike LoRA Collection (nphSi)
description: Community lookalike LoRA collection for Z-Image and Z-Image-Turbo with vrtl trigger convention and Turbo preview settings.
tags: [z-image, lora, image-generation, diffusers]
status: draft
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T12:00:00Z }
sources:
  - id: zimage-lora-card
    resource: ../raw/Z-Image-Lora/README.md
    scope: ../raw/Z-Image-Lora/
    kind: documentation
    title: Z-Image-Lora model card (nphSi)
---

nphSi Z-Image-Lora is a community collection of lookalike/person-likeness LoRA adapters reported for the `Tongyi-MAI/Z-Image` and `Tongyi-MAI/Z-Image-Turbo` base checkpoints, packaged with `diffusers`/`safetensors` tagging and a shared `vrtl`-prefixed trigger convention.[^zimage-lora-card] The durable technical content is the trigger/usage convention, base-model pairing, training provenance, fixed preview recipe, license, and misuse boundary; the large per-person trigger roster is intentionally not reproduced here.[^zimage-lora-card]

## Trigger and usage convention

- **Reported** trigger form: each adapter uses a full LoRA name plus a `vrtlxxxx`-style trigger token in the prompt; generic person terms alone are reported not to work with this captioning approach.[^zimage-lora-card]
- **Reported** disambiguation rules: add gender for ambiguous names; drop the real name when base-model knowledge is weak, censored, or confusing; for multi-trigger adapters use only the trigger tokens or their combination, with `vrtlMain` combining all triggers.[^zimage-lora-card]
- **Synthesis:** the convention is adapter-specific activation rather than natural-language person description, so reuse depends on copying the exact trigger rather than paraphrasing it.

## Base, training, and preview setup

- **Observed** base pairing: card frontmatter declares `base_model: Tongyi-MAI/Z-Image` and `Tongyi-MAI/Z-Image-Turbo`.[^zimage-lora-card]
- **Observed** packaging tags: `text-to-image`, `lora`, `diffusers`, `safetensors`, and `z-image`.[^zimage-lora-card]
- **Reported** training provenance: adapters are trained at 1MP with OneTrainer on the base Z-Image checkpoint using public-domain images found on the public internet, with no nudity or pornography in the training process.[^zimage-lora-card]
- **Reported** preview recipe: previews use a fixed Turbo configuration (quantized Turbo, Euler, beta schedule, low step count, CFG 1, auraflow sampler setting) with a fixed upper-body portrait template on a plain gradient background.[^zimage-lora-card] Exact preview-prompt wardrobe and lettering details are omitted here as non-durable and sexualized; the reusable point is that previews share one template rather than per-adapter prompts.
- **Observed** license: card frontmatter declares `apache-2.0`.[^zimage-lora-card]

## Community resources and provenance

- **Observed** companion surfaces: the card links a LoRA index Space offering direct download, preview, and info, plus a Hugging Face discussion thread for feedback, help, and community discussion; neither linked surface is captured locally.[^zimage-lora-card]
- **Observed** freshness signals: the card carries `2026 Updates` and `2025` roster sections listing a large number of person-specific additions, establishing that the collection is incrementally extended over time.[^zimage-lora-card] Names and per-adapter triggers are excluded from this synthesis as low-reuse, high-volume catalog detail.
- **Synthesis:** treat any person count or trigger list as point-in-time **reported** card content, not a stable inventory, because the card has no captured immutable revision.

## Trust and misuse boundary

- **Reported** prohibition: the card states users are not allowed to share nudity or pornographic deepfakes of famous people made with these LoRAs, notes such content is illegal in almost all countries, disclaims author responsibility for illegal creations, and asks users not to spread deepfakes and to respect dignity and privacy.[^zimage-lora-card]
- **Synthesis:** this wiki entry records only the generic technical convention and explicitly does not provide per-person triggers, name-to-trigger mappings, or portrait-generation procedures, keeping the minimum useful redacted description under the repository privacy rule.

## Relationships

- For a local ggml-based engine that separately reports Z-Image support, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md); neither source claims these lookalike adapters work with that engine.

## Coverage limits

- **Observed:** only `../raw/Z-Image-Lora/README.md` was statically inspected; no code was executed and no image was generated or reproduced.
- **Observed:** the `<Gallery />` preview set, underlying LoRA weight files, the linked Lookalike-LoRA-Index Space, and the linked discussion thread are not captured in `../raw/Z-Image-Lora/` and remain uninspected.
- The card capture carries no immutable revision, so future card, weight, or roster updates would be a new revision; per-person roster detail and preview-prompt specifics were deliberately excluded as non-durable.

[^zimage-lora-card]: Hugging Face model-card capture in `../raw/Z-Image-Lora/README.md`; base models, `apache-2.0` license, and `text-to-image`/`lora`/`diffusers`/`safetensors`/`z-image` tags from YAML frontmatter; index-Space and discussion links from opening link lines; full-name-plus-`vrtl` trigger rule, gender/name-removal/multi-trigger/`vrtlMain` rules, fixed Turbo preview settings, and shared portrait-template setup from usage bullets; OneTrainer 1MP public-image training claim and no-nudity training claim plus NSFW-deepfake prohibition, illegality notice, responsibility disclaimer, and dignity/privacy request from training/disclaimer paragraphs; incremental-collection evidence from `2026 Updates` and `2025` roster sections.
