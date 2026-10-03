---
type: Concept
title: Wulver Krea-2 Anthro Fine-Tune
description: Vaelico full fine-tune of Krea 2 Raw for anthro, furry, and anime/kemono generation with multi-character composition and 1,113 artist tokens, shipped as Turbo and Non-Turbo checkpoints under the Krea 2 Community License.
tags: [krea, text-to-image, fine-tune, furry, anime, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T12:00:00Z }
sources:
  - id: wulver-readme
    resource: ../raw/Wulver/README.md
    scope: ../raw/Wulver/
    kind: documentation
    title: Krea 2 - Wulver v0.5 model card
---

Wulver v0.5 is the **reported** full fine-tune of Krea 2 Raw by Vaelico for anthro, furry, anime, and kemono generation with multi-character composition and 1,113 callable `@artist` style tokens, distributed as Turbo-merged and Non-Turbo checkpoints with ComfyUI setup and prompting guidance.[^wulver-readme]

## Identity and release

- **Reported** identity: model name Krea 2 - Wulver, version v0.5, creator Vaelico, base model `Comfy-Org/Krea-2`, described as a full fine-tune of Krea 2 Raw at 12.8B DiT scale; frontmatter declares `pipeline_tag: text-to-image` and `library_name: diffusers`.[^wulver-readme]
- **Reported** naming: named for the Wulver, a wolf-headed being from Shetland folklore described as never cruel, which fished the lochs and left its catch for those in need.[^wulver-readme]
- **Reported** upstream: Civitai page and `vaelico.ai`, with GGUF quants (Q8_CR, Q5_0, Q4_0) hosted Civitai-only rather than in the weight repository.[^wulver-readme]
- **Reported** previous version: v0.1 files (`Wulver_v0.1_*`) remain in the repository unchanged; v0.5 is the current capture.[^wulver-readme]
- **Reported** license: modified version of Krea 2 under the Krea 2 Community License Agreement including the Acceptable Use Policy; full license text ships as `LICENSE.md` with an attribution `NOTICE`; explicitly not affiliated with or endorsed by Krea.[^wulver-readme]

## Capabilities

- **Reported** home turf: anthro and furry generation with species knowledge described as far beyond generalist models.[^wulver-readme]
- **Reported** style range: anime and kemono styles, positioned as beyond the usual western-model anime approximation.[^wulver-readme]
- **Reported** composition: multi-character scenes with characters interacting rather than merging.[^wulver-readme]
- **Reported** artist styles: 1,113 `@artistname` tokens callable by name; in v0.1 the `@` prefix was ignored, while in v0.5 the tokens work.[^wulver-readme]

## Training

All training statements below are **reported**; no training was executed or verified here.

- **Reported** v0.5 schedule: 13 full epochs over a curated corpus at 512 px (384,672 samples per epoch, about 156k steps at batch 32), with the 13th epoch learning rate annealed to zero, followed by an artist-focused pass at 512 px and a final curated pass at 1024 px.[^wulver-readme]
- **Reported** Turbo derivation: Turbo files merge the official Krea 2 Turbo LoRA (`krea2_turbo_lora_rank_64_bf16.safetensors` from `Comfy-Org/Krea-2`, `loras/`) at strength 1.0 for 8-step CFG-1 inference; Non-Turbo files ship without the merge for custom strength, LoRA training, or further fine-tuning.[^wulver-readme]

## Files

- **Reported** checkpoint and precision options:[^wulver-readme]

| File | Size | Use |
|---|---|---|
| `Wulver_v0.5_fp8_e4m3fn.safetensors` | 12.8 GB | ComfyUI, Turbo, 8 steps — the one most people want |
| `Wulver_v0.5_int8_convrot.safetensors` | 13.5 GB | forge-neo and other int8 runtimes, Turbo |
| `Wulver_v0.5_w4a8-convrot.safetensors` | 7.7 GB | Smallest, ComfyUI native W4A8, Turbo |
| `Wulver_v0.5_bf16.safetensors` | 25.6 GB | Turbo-merged full precision — merging, quantizing |
| `Wulver_v0.5_non_turbo_bf16.safetensors` | 25.6 GB | Non-Turbo base for LoRA training, further fine-tuning, or custom Turbo strength |
| `Wulver_v0.5_non_turbo_int8-convrot.safetensors` | 13.5 GB | Non-Turbo, int8 |
| `Wulver_workflow.json` | — | Drag-and-drop ComfyUI workflow (fp8, 8 steps) |
| `ARTISTS.md` | — | The 1,113 artist tokens |

- **Reported** checksums (SHA256) for provenance verification:[^wulver-readme]

| File | SHA256 |
|---|---|
| `Wulver_v0.5_fp8_e4m3fn.safetensors` | `ef8b8e1cf596e9564df79d9688af3c6faf85772b3226f1ba880db9970271619e` |
| `Wulver_v0.5_int8_convrot.safetensors` | `e3d89a4faa32633374f00ed37a9a0b49663a9a243725f39573a119c8c7009877` |
| `Wulver_v0.5_w4a8-convrot.safetensors` | `905af7686bb48d4f40dc80117f6839f6a9491b1af13e46b6242ecaadda6bf996` |
| `Wulver_v0.5_bf16.safetensors` | `c8f2b29749cee4386f2215033bca5e26af0cc8fd0fd0c49f4c1d55b35b3ebde3` |
| `Wulver_v0.5_non_turbo_bf16.safetensors` | `84012bb362249e15efd18fa46034d98be74f180e8decaf858e127c07f8a6700f` |
| `Wulver_v0.5_non_turbo_int8-convrot.safetensors` | `97417e247e3bea10fc8e5a023e4bbb2f075a9a363430a01681c529955bf602b3` |
| `Wulver_workflow.json` | `3040420f4aa830a2611fb5d202ae9b227f6e87ed4ca3c6657fd00312b26ebd07` |

## Inference settings

- **Reported** Turbo-file settings: 8 steps, CFG 1.0, sampler euler with scheduler simple, shift 1.15 (ComfyUI default for Krea 2, no extra node needed), 1024 native resolution, `CLIPLoader` type `krea2`.[^wulver-readme]
- **Reported** Non-Turbo recipes with the Turbo LoRA loaded via a `LoraLoaderModelOnly` node, sampler euler with scheduler simple in all three:[^wulver-readme]

| Recipe | Turbo LoRA strength | Steps | CFG |
|---|---|---|---|
| Same as the Turbo files | 1.0 | 8 | 1.0 |
| No LoRA | — | 52 | 3.5 |
| Advanced lighter Turbo | 0.6 | 14 | 1.0 |

- **Reported** negative-prompt notes: without the Turbo LoRA and CFG above 1, use an empty `CLIPTextEncode` as the negative rather than `ConditioningZeroOut`; at CFG 1.0 the negative prompt has no effect.[^wulver-readme]

## ComfyUI setup

Procedure below is **reported**; no download or generation was executed for this concept.

1. Place `Wulver_v0.5_fp8_e4m3fn.safetensors` in `ComfyUI/models/diffusion_models/`.[^wulver-readme]
2. Place text encoder `qwen3vl_4b_bf16.safetensors` from `Comfy-Org/Krea-2` in `models/text_encoders/`.[^wulver-readme]
3. Place VAE `qwen_image_vae.safetensors` from the same repo in `models/vae/`.[^wulver-readme]
4. Drag `Wulver_workflow.json` into ComfyUI and queue.[^wulver-readme]

## Prompting

- **Reported** caption order: training captions start with a rating tag, then the artist token if present, then the description; prompting in the same order is recommended.[^wulver-readme]
- **Reported** template: `sfw, @artistname, A digital painting of [subject & species, appearance details]. [What they are doing, pose, expression]. [Clothing / body details]. The background features [setting, lighting, atmosphere].`[^wulver-readme]
- **Reported** guidance: detailed descriptive prose works best and booru-style tag lists also work; artist tokens must match `ARTISTS.md` exactly with `@` included and sit right after the rating tag; one- or two-word prompts sample the model's whole range and yield random styles, so describe what is wanted.[^wulver-readme]

## Compatibility notes

- **Reported** architecture: same as Krea 2 Raw with Qwen3-VL-4B text encoder, Qwen Image VAE, and stock ComfyUI loaders.[^wulver-readme]
- **Reported** `w4a8-convrot` requirements: ComfyUI 0.31.0 or newer with native W4A8 loader, an SM 8.0+ GPU, and PyTorch cu130+.[^wulver-readme]
- **Reported** LoRA drift: LoRAs trained on base Krea 2 or on Wulver v0.1 may behave differently on v0.5 because weights have moved.[^wulver-readme]

## Relationships

- Depends on [Krea 2 Raw Text-to-Image Model](krea-2-raw.md) as its reported fine-tuning base.
- Uses [Krea 2 Turbo Text-to-Image Model](krea-2-turbo.md) distillation via the official Turbo LoRA merged into Wulver Turbo files at strength 1.0.
- For running GGUF-quantized checkpoints of this model family in ComfyUI, see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md).

## Coverage limits

- **Observed:** only `../raw/Wulver/README.md` was statically inspected; no code was executed and no download, inference, training, quality, artist-token, or checksum claim was reproduced.
- **Observed:** referenced but locally unavailable and uninspected: `ARTISTS.md` (1,113 artist tokens), `SHA256SUMS_v0.5.txt`, `NON_TURBO_v0.5.md`, `NON_TURBO.md`, `Wulver_workflow.json`, `assets/vaelico-logo.png`, `LICENSE.md`, `NOTICE`, all six `.safetensors` weights, and the Civitai-only GGUF and plain int8 files.
- All capability, training, settings, setup, prompting, compatibility, checksum, and license statements above are **reported** by the model card, not independently verified.
- **Synthesis:** verify the current Krea 2 Community License, Acceptable Use Policy, Civitai terms, and upstream file versions before commercial, derivative, or deployment reuse; this capture records no card date and no immutable weight revision beyond the reported SHA256 values.

[^wulver-readme]: Model-card capture in `../raw/Wulver/README.md`; identity, base model, and pipeline/library tags from header and YAML frontmatter; folklore naming from blockquote; upstream, GGUF, and v0.1 statements from Files, Checksums, and Previous-version sections; license position from License section; capabilities from What-it-does section; training schedule and Turbo-LoRA merge from What's-new section; file table, sizes, and uses from Files section; SHA256 values from Checksums section; Turbo settings, Non-Turbo recipes, negative-prompt notes, and LoRA filename from Settings and Other-recipes sections; setup paths from ComfyUI-setup section; caption order, template, and token-placement rules from Prompting-tips section; encoder, VAE, loader, version, GPU, PyTorch, and LoRA-drift notes from Compatibility-notes section.
