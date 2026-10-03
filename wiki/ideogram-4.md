---
type: Concept
title: Ideogram 4 Text-to-Image Model
description: Ideogram 9.3B open-weight flow-matching text-to-image foundation model with JSON prompting, layout and palette control, and nf4/fp8 releases under a non-commercial license.
tags: [ideogram, text-to-image, diffusion-transformer, flow-matching, fp8, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T12:00:00Z }
sources:
  - id: ideogram-4-fp8-card
    resource: ../raw/ideogram-4-fp8/README.md
    scope: ../raw/ideogram-4-fp8/
    kind: documentation
    title: Ideogram 4 fp8 model card (ideogram-ai)
---

Ideogram 4 is the **reported** first open-weight text-to-image model from Ideogram, described as a 9.3B-parameter foundation model trained from scratch with a structured JSON prompting interface, multilingual text rendering, bounding-box layout and color-palette controls, and native 2K output.[^ideogram-4-fp8-card]

## Identity and model family

- **Observed** task tagging: frontmatter declares `pipeline_tag: text-to-image`, `license: other` with `license_name: ideogram-4-non-commercial`, and tags for `text-to-image`, `image-generation`, `diffusion`, `flow-matching`, `dit`, and `ideogram`.[^ideogram-4-fp8-card]
- **Reported** family: state-of-the-art foundation model trained from scratch, explicitly not a fine-tune of any existing model.[^ideogram-4-fp8-card]
- **Observed** Model Zoo status at capture:[^ideogram-4-fp8-card]

| Model | Params | Weight Quantization | Supported Hardware | Diffusers Support | License |
|---|---|---|---|---|---|
| Ideogram 4 (nf4) | 9.3B | nf4 | CUDA | Yes | Ideogram 4 Non-Commercial |
| Ideogram 4 (fp8) | 9.3B | fp8 | All | No | Ideogram 4 Non-Commercial |

- **Synthesis:** this concept covers the Ideogram 4 family from the fp8 package capture; use the nf4 row when CUDA plus diffusers support matters and the fp8 row when broader hardware support matters without diffusers support, both under the same non-commercial license.

## Capabilities (reported)

- **Reported** extreme controllability from structured JSON captions: composition, style, lighting, color palette, typography, and spatial layout from a single prompt.[^ideogram-4-fp8-card]
- **Reported** state-of-the-art text rendering for signage, logos, captions, watermarks, and multi-line text, including multilingual rendering.[^ideogram-4-fp8-card]
- **Reported** spatial layout control via `bbox` coordinates for subjects, text elements, and background regions, plus `compositional_deconstruction` with bounding boxes and per-element descriptions.[^ideogram-4-fp8-card]
- **Reported** color-palette conditioning via a `colour_palette` array of hex colors in the style description.[^ideogram-4-fp8-card]
- **Reported** flexible resolution: any multiple-of-16 resolution from 256 to 2048 per side, aspect ratios up to 6:1, with noise schedule auto-adjusting per resolution; highest-quality guidance is `--height 2048 --width 2048` in the CLI section.[^ideogram-4-fp8-card]
- All capability claims above are **reported**; no generation, rendering, layout, palette, resolution, or multilingual claim was reproduced here.

## Architecture (reported)

- **Reported** class: flow-matching text-to-image model on a fully single-stream Diffusion Transformer; text and image tokens are concatenated into one unified sequence through the same 34-layer transformer with no separate branches.[^ideogram-4-fp8-card]
- **Reported** text encoder: Qwen3-VL-8B-Instruct vision-language model instead of a text-only encoder such as CLIP or T5; hidden states from 13 intermediate layers are extracted and concatenated for multi-scale semantic features.[^ideogram-4-fp8-card]
- **Reported** guidance: dual-branch classifier-free guidance whose conditional and unconditional branches can be independently refined for separate control over prompt adherence and image quality.[^ideogram-4-fp8-card]
- **Observed:** no code, weights, architecture diagram, or pipeline document was inspected to verify these claims; the card points to `docs/model_architecture.md` and `docs/pipeline.md` in the separate `ideogram-oss/ideogram4` repo.[^ideogram-4-fp8-card]

## Performance (reported)

- **Reported** Design Arena: top-ranked open-weight model overall, trailing only proprietary GPT and Gemini models; leading open-weight model by a commanding margin when filtered to open weights.[^ideogram-4-fp8-card]
- **Reported** ContraLabs blind typography evaluation by ten professional designers: 47.9% first-place win rate versus Gemini 3.1 Flash Image Preview (30.0%), FLUX.2 [max] (15.5%), and Grok Imagine 1.0 (15.0%); highest practical-usability rating at 3.55/5 versus 2.84, 2.61, and 2.49 for the same competitors.[^ideogram-4-fp8-card]
- **Reported** LMArena: top-ranked open-weight lab and top-5 image-generation lab overall.[^ideogram-4-fp8-card]
- **Reported** Ideogram internal human-preference benchmark for graphic design and photography: Bradley-Terry #2 overall behind GPT Image 2 medium and top open-weight model.[^ideogram-4-fp8-card]
- **Reported** open-source benchmarks: layout control (7Bench), spatial reasoning and object fidelity (SpatialGenEval), text rendering (X-Omni OCR), and prompt alignment (Prism); closes the gap to closed-source models on every axis and is significantly better than all closed-source models on 7Bench layout control.[^ideogram-4-fp8-card]
- **Reported** parameter efficiency: at 9.3B parameters, best text rendering of any benchmarked open-weight release, ahead of Qwen-Image (20B), FLUX.2 [dev] (32B), and HunyuanImage 3.0 (80B MoE).[^ideogram-4-fp8-card]
- **Observed:** all charts are remote images not captured locally and no score table, sample size, date range, or variance beyond the prose above was inspected; treat every ranking as **reported** without independent verification.

## Inference and access (reported)

All procedures below are **reported**; no install, authentication, download, screening, or generation was executed for this concept.

- **Reported** code location: inference code lives in the `ideogram-oss/ideogram4` GitHub repo; install with `pip install .` or `pip install -e .` for editable use under `src/ideogram4/`.[^ideogram-4-fp8-card]
- **Reported** gated weights: accept the license gate on the `ideogram-ai/ideogram-4-nf4` or `ideogram-ai/ideogram-4-fp8` Hugging Face page, then authenticate with `hf auth login` or `export HF_TOKEN="hf_..."`; unauthenticated download fails with `404` / `GatedRepoError`.[^ideogram-4-fp8-card]
- **Reported** magic prompt: plain `--prompt` is expanded into structured JSON by an LLM; default is Ideogram's hosted magic-prompt API, described as free and server-side with no local model needed, reading `IDEOGRAM_API_KEY`; alternatively run expansion through your own provider with the open-source magic-prompt system prompt.[^ideogram-4-fp8-card]
- **Reported** CLI example: `python run_inference.py --prompt "..." --output out.png --quantization "nf4" --magic-prompt-key "$IDEOGRAM_API_KEY"`, with `--sampler-preset V4_QUALITY_48` named for highest quality.[^ideogram-4-fp8-card]
- **Reported** safety screening via Hive: prompt and output screening needs Text Moderation and Visual Content Moderation keys as `HIVE_TEXT_MODERATION_KEY` / `HIVE_VISUAL_MODERATION_KEY` or `--hive-text-key` / `--hive-visual-key`.[^ideogram-4-fp8-card]
- **Observed:** `IDEOGRAM_API_KEY`, `HF_TOKEN`, and Hive keys appear only as placeholder variable names; no live credential was captured.

## Prompting (reported)

- **Reported** training: trained exclusively on structured JSON captions that are deliberately extremely descriptive, so training and inference share one prompt format and each pair supplies dense grounded supervision.[^ideogram-4-fp8-card]
- **Reported** inference guidance: use JSON prompts for maximum controllability; plain-text prompts work but perform worse because the model only saw structured JSON in training.[^ideogram-4-fp8-card]
- **Reported** escape hatch: magic prompt expands a casual plain-text prompt into a full structured caption before generation, giving JSON-quality results without hand-writing JSON.[^ideogram-4-fp8-card]
- **Observed:** no JSON schema, example caption, sampler table, or parameter reference was captured beyond the named `colour_palette`, `bbox`, and `compositional_deconstruction` keys; the card defers full detail to `docs/prompting.md` and `docs/inference.md`.[^ideogram-4-fp8-card]

## Endpoints and licensing

- **Observed** license: fp8 frontmatter and Model Zoo both state Ideogram 4 Non-Commercial; no commercial-use right is documented in the captured card.[^ideogram-4-fp8-card]
- **Reported** endpoints: ideogram.ai try-online site, technical blog post for 2026-06-03 release, `ideogram-oss/ideogram4` code repo, Hugging Face `ideogram-ai/ideogram-4` collection with nf4 and fp8 checkpoints, developer API at developer.ideogram.ai, and BibTeX citation key `ideogram-4-2026`.[^ideogram-4-fp8-card]

## Relationships

- Uses a Qwen VL-class encoder (`Qwen3-VL-8B-Instruct`); for Qwen-family image models with different encoders, checkpoints, and licenses, see [Qwen-Image-2.1 Text-to-Image and Editing Model](qwen-image-2-1.md).
- For comparable open-weight text-to-image coverage with different architectures, steps, and licenses, see [FLUX.1-dev Text-to-Image Model](flux-1-dev.md), [Z-Image-Turbo Text-to-Image Model](z-image-turbo.md), [Krea 2 Raw Text-to-Image Model](krea-2-raw.md), and [Ming-Image-0.1-Design Text-to-Image Model](ming-image-0-1-design.md).
- For local quantized-inference hosts, see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) and [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md); this card names only its own `run_inference.py` plus diffusers support for nf4 and explicitly marks fp8 as without diffusers support, and was not verified against either host in this operation.

## Coverage limits

- **Observed:** only `../raw/ideogram-4-fp8/README.md` was statically inspected; no code was executed and no install, authentication, download, screening, generation, benchmark, rendering, layout, or usability claim was reproduced.
- **Observed:** no immutable revision or capture date is present beyond the reported 2026-06-03 release note; freshness is unbounded beyond the local capture.
- **Observed:** uninspected material outside this scope includes all remote sample, logo, and benchmark images, the linked GitHub repo and `docs/` pages, Hugging Face collection and checkpoint pages, blog post, official site, developer API, Hive service, and hiring link.

[^ideogram-4-fp8-card]: Official model-card capture in `../raw/ideogram-4-fp8/README.md`; `pipeline_tag`, non-commercial license, and diffusion/flow-matching/DiT tags from YAML frontmatter; first-open-weight, trained-from-scratch, JSON interface, multilingual rendering, bbox/palette, and native-2K claims from intro; 2026-06-03 release note from News; 9.3B, nf4/fp8, hardware, diffusers Yes/No, and license from Model Zoo; Design Arena, ContraLabs 47.9%/3.55 figures, LMArena, internal Bradley-Terry, 7Bench/SpatialGenEval/X-Omni/Prism, and 9.3B vs 20B/32B/80B MoE claims from Performance; `pip install .`, gated-weights/`hf auth login`/`HF_TOKEN`, magic-prompt/`IDEOGRAM_API_KEY`, CLI example, `V4_QUALITY_48` plus 2048 guidance, and Hive key names from Quick Start; 34-layer single-stream DiT, Qwen3-VL-8B-Instruct 13-layer, dual-branch CFG, and 256–2048/6:1 resolution claims from Model Summary; JSON-only rationale, `colour_palette`/`bbox`/`compositional_deconstruction` keys, and magic-prompt expansion from Prompting Guide; `docs/` table, BibTeX `ideogram-4-2026`, endpoints, and hiring note from Documentation/Citation closing sections.
