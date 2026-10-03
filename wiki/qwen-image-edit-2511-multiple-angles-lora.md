---
type: Concept
title: Qwen-Image-Edit-2511 Multiple-Angles LoRA
description: Camera-control LoRA for Qwen-Image-Edit-2511 with 96 precise poses, <sks> trigger vocabulary, and Gaussian Splatting training provenance.
tags: [qwen, lora, image-editing, camera-control, multi-angle, diffusers]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T12:00:00Z }
sources:
  - id: qwen-edit-2511-multi-angles
    resource: ../raw/Qwen-Image-Edit-2511-Multiple-Angles-LoRA/README.md
    scope: ../raw/Qwen-Image-Edit-2511-Multiple-Angles-LoRA/
    kind: documentation
    title: Qwen-Image-Edit-2511-Multiple-Angles-LoRA model card
---

Qwen-Image-Edit-2511-Multiple-Angles-LoRA is a **reported** camera-control LoRA that adds 96 precise viewpoint poses to `Qwen/Qwen-Image-Edit-2511` image editing, prompted with a `<sks>` trigger followed by azimuth, elevation, and distance descriptors.[^qwen-edit-2511-multi-angles]

## Camera pose system

- **Reported** composition: 4 elevations × 8 azimuths × 3 distances = 96 poses, trained on 3000+ Gaussian Splatting renders for 3D-consistent spatial control.[^qwen-edit-2511-multi-angles]
- **Reported** azimuth vocabulary (horizontal rotation):[^qwen-edit-2511-multi-angles]

| Angle | Descriptor |
|---|---|
| 0° | `front view` |
| 45° | `front-right quarter view` |
| 90° | `right side view` |
| 135° | `back-right quarter view` |
| 180° | `back view` |
| 225° | `back-left quarter view` |
| 270° | `left side view` |
| 315° | `front-left quarter view` |

- **Reported** elevation vocabulary (vertical angle):[^qwen-edit-2511-multi-angles]

| Angle | Descriptor |
|---|---|
| -30° | `low-angle shot` (camera below, looking up) |
| 0° | `eye-level shot` |
| 30° | `elevated shot` |
| 60° | `high-angle shot` (camera high, looking down) |

- **Reported** distance vocabulary:[^qwen-edit-2511-multi-angles]

| Factor | Descriptor | Usage |
|---|---|---|
| ×0.6 | `close-up` | Details, textures |
| ×1.0 | `medium shot` | Balanced, standard |
| ×1.8 | `wide shot` | Context, environment |

- **Synthesis:** any pose is compositional as `<sks> [azimuth] [elevation] [distance]`, e.g. `<sks> front view eye-level shot medium shot` (reference pose), `<sks> right side view high-angle shot close-up`, `<sks> back view low-angle shot wide shot`; the source enumerates all 96 combinations under its All 96 Prompts Reference section rather than requiring memorization.[^qwen-edit-2511-multi-angles]

## Compatibility and use

- **Reported** prompt format: `<sks> [azimuth] [elevation] [distance]` with exact order; the `<sks>` trigger is essential.[^qwen-edit-2511-multi-angles]
- **Reported** settings: LoRA strength `0.8–1.0` (start at `0.9`); base model `Qwen/Qwen-Image-Edit-2511`.[^qwen-edit-2511-multi-angles]
- **Reported** artifacts: `qwen-image-edit-2511-multiple-angles-lora.safetensors` weights and `comfyui-workflow-multiple-angles.json` ComfyUI workflow; live demo via the fal.ai `qwen-image-edit-2511-multiple-angles` endpoint.[^qwen-edit-2511-multi-angles]
- **Reported** tips: respect descriptor order, use exact vocabulary, prefer clear well-lit input subjects, and try low-angle (`-30°`) poses where the adapter is claimed to excel.[^qwen-edit-2511-multi-angles]
- **Observed** task tagging: frontmatter declares `pipeline_tag: image-to-image`, `library_name: diffusers`, `license: apache-2.0`, `base_model: Qwen/Qwen-Image-Edit-2511`, and tags including `lora`, `multi-angle`, `camera-control`, `gaussian-splatting`, and `fal`.[^qwen-edit-2511-multi-angles]

## Training provenance

- **Reported** training platform: fal.ai Qwen Image Edit 2511 Trainer; dataset 3000+ synthetic 3D renders with precise camera control; built by Lovis Odin at fal.[^qwen-edit-2511-multi-angles]
- **Reported** positioning: presented as the first multi-angle camera-control LoRA for Qwen-Image-Edit-2511, complementing rather than replacing the base model's built-in viewpoint capability; sibling work by the same author includes a 72-pose multi-angle LoRA for Flux and a next-scene Qwen LoRA.[^qwen-edit-2511-multi-angles]
- **Synthesis:** the Gaussian Splatting data claim is the mechanism offered for better spatial understanding, but no ablation, metric, or comparison protocol is given, so treat precision and low-angle-excellence claims as unverified vendor reporting.

## Limitations and qualifiers

- **Reported** evidence type: animated result GIFs and camera-system diagrams (`all_animations_combined.gif`, `poses_96_animated.gif`, `poses_96_distance_comparison.png`) are referenced but were not captured locally, so visual quality claims are uninspected in this entry.[^qwen-edit-2511-multi-angles]
- **Synthesis:** no sampler, step count, CFG, resolution, seed, or diffusers/ComfyUI loader snippet is given in the capture; reuse depends on the base-model documentation plus the LoRA-strength and prompt-format guidance above.
- Freshness is unbounded: the capture carries no publication date or immutable revision, so future weight or prompt-vocabulary updates would be a new revision.

## Relationships

- Uses the upstream `Qwen/Qwen-Image-Edit-2511` base model (external to this wiki); this concept records only the multiple-angles LoRA packaging, vocabulary, and settings, not the base model's own behavior.
- Related to [Qwen-Image-2.1 Edit LoRAs (WarmBloodAban)](qwen-image-2-1-edit-loras.md), which targets character consistency/conversion on the distinct `Qwen-Image-2.1` base; neither source claims the other's capability or base.
- For the Qwen-Image-2.1 base family behavior itself, see [Qwen-Image-2.1 Text-to-Image and Editing Model](qwen-image-2-1.md); do not conflate `Qwen-Image-2.1` with `Qwen-Image-Edit-2511`.

## Coverage limits

- **Observed:** only `../raw/Qwen-Image-Edit-2511-Multiple-Angles-LoRA/README.md` was statically inspected; no generation, viewpoint-accuracy, or low-angle claim was executed or reproduced.
- **Observed:** uncaptured/uninspected material includes the `.safetensors` LoRA weights, the `comfyui-workflow-multiple-angles.json` workflow, all result/diagram GIF and PNG assets, the `Qwen/Qwen-Image-Edit-2511` base weights, and the fal.ai trainer and live-demo targets.
- The full 96-prompt enumeration and azimuth diagram were intentionally not duplicated here; the compositional rule plus vocabulary tables above reproduce the retrieval-relevant content, with the source section as the exhaustive reference.
- No immutable revision or snapshot date is present in the capture; future weight or card updates would be a new revision.

[^qwen-edit-2511-multi-angles]: Model-card capture in `../raw/Qwen-Image-Edit-2511-Multiple-Angles-LoRA/README.md`; 96-pose identity, trigger format, and Gaussian Splatting training from title, Highlights, Why This LoRA, and Training Details sections; azimuth/elevation/distance vocabularies and 96-prompt reference from 96 Camera Positions and All 96 Prompts Reference sections; LoRA strength, base model, files, fal.ai demo, and tips from Files, Recommended Settings, and Tips sections; author/trainer/sibling-work attribution from Training Details, Related Work, and Author sections; `license: apache-2.0`, `base_model`, `pipeline_tag: image-to-image`, `library_name: diffusers`, and tags from YAML frontmatter.
