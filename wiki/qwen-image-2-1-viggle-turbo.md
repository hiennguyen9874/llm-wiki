---
type: Concept
title: Qwen-Image-2.1 Viggle Turbo Few-Step LoRA
description: Viggle distilled 6-step and 9-step LoRA plus merged quantized transformers for faster Qwen-Image-2.1 text-to-image and editing without CFG.
tags: [qwen, lora, distillation, image-generation, image-editing, comfyui, quantization, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T04:54:24Z }
sources:
  - id: viggle-turbo-readme
    resource: ../raw/Qwen-Image-2.1-viggle-turbo/README.md
    scope: ../raw/Qwen-Image-2.1-viggle-turbo/
    kind: documentation
    revision: v0.3-2026-09-29
    title: Qwen-Image-2.1-viggle-turbo — v0.3
---

Viggle's `Qwen-Image-2.1-viggle-turbo` is a **reported** few-step distilled LoRA for `Qwen/Qwen-Image-2.1` covering text-to-image and instruction-driven editing with 1–3 reference images in 6 steps instead of 40, with no classifier-free guidance, described as about 5× faster end to end and hard to tell apart from the base model except on small dense text and complicated edits.[^viggle-turbo-readme]

## Versions and adapters

- **Reported** versions: v0.3 (2026-09-29) current; v0.2.1 (2026-09-24) and v0.2 (2026-09-23) retained in the repo with the same 6-step usage.[^viggle-turbo-readme]
- **Reported** v0.3 balance versus v0.2.1: less grain and cleaner surfaces, fine texture a little softer; diversity still close to the base model and small-text accuracy about the same; not a strict upgrade — keep v0.2.1 if the crisper look is preferred.[^viggle-turbo-readme]
- **Reported** capacity view: gains at 6 steps since v0.2.1 traded sharpness against grain/softness, so further quality is bought with steps via the 9-step mode.[^viggle-turbo-readme]
- **Reported** files:[^viggle-turbo-readme]

| File | Purpose |
|---|---|
| `Qwen-Image-2.1-viggle-turbo-v0.3-6step-lora-r256.safetensors` | v0.3 LoRA rank 256, bf16, 1.3 GB, loaded on base transformer at runtime; **use this** |
| `Qwen-Image-2.1-viggle-turbo-v0.3-6step-lora-r128.safetensors` | Same adapter cut to rank 128, 0.7 GB, used by ComfyUI workflows |
| `peft_v0.3/` | v0.3 adapter in peft key format; pick either this or the safetensors, not both |
| `...-6step-{int8_convrot,fp8_e4m3fn}.safetensors`, `...-{Q8_0,Q6_K,Q5_K_M,Q4_K_M}.gguf` | LoRA merged into base transformer in fp32 then quantized once, one file per format for ComfyUI single-file use |
| `comfyui/` | Custom nodes, text-to-image/edit workflows, example inputs |
| `scheduler/` | Base scheduler config with `shift_terminal: null` |

- **Reported** rank-128 construction: exact per-layer SVD truncation of the r256 update; what the cut drops is about ten times smaller than bf16 rounding of the base weights.[^viggle-turbo-readme]

## Diffusers use conditions

- **Reported** install: `torch`, `transformers>=5.17,<6`, `accelerate`, `safetensors`, `peft`, `pillow`, plus pinned `diffusers` git `80c7ed262aeffbeb43ef13ae04baeb9b84515a69` because `QwenImage21Pipeline` is not in a released diffusers yet; `peft` is required.[^viggle-turbo-readme]
- **Reported** pipeline: `QwenImage21Pipeline.from_pretrained("Qwen/Qwen-Image-2.1", dtype=torch.bfloat16)`, `load_lora_weights("Viggle/Qwen-Image-2.1-viggle-turbo", weight_name="...-v0.3-6step-lora-r256.safetensors")`, scheduler replaced with `FlowMatchEulerDiscreteScheduler.from_pretrained("Viggle/Qwen-Image-2.1-viggle-turbo", subfolder="scheduler")`.[^viggle-turbo-readme]
- **Reported** fixed 6-step settings: `num_inference_steps=6`, `sigmas=[1.0, 0.9375, 0.875, 0.75, 0.5, 0.25]`, `true_cfg_scale=1.0` with no negative prompt; pass sigmas as written at every size because the pipeline applies its resolution-dependent shift to these raw nodes.[^viggle-turbo-readme]
- **Reported** step-count rule: add or remove steps at the high-noise end only and keep `0.875, 0.75, 0.5, 0.25`; 5 steps `[1, 0.875, 0.75, 0.5, 0.25]`, 7 steps `[1, 0.9583, 0.9167, 0.875, 0.75, 0.5, 0.25]`; moving low-noise nodes softens images and plain `num_inference_steps` without `sigmas=` plus CFG does not help.[^viggle-turbo-readme]
- **Reported** scheduler and LoRA handling: use the shipped scheduler config because the base config's `shift_terminal: 0.02` wrecks the last step; keep the LoRA unmerged at scale 1.0 because merging into bf16 weights loses part of the update.[^viggle-turbo-readme]
- **Reported** editing: same pipe object, `image=[...]` list with 1–3 references where order fixes `<image1>`, `<image2>`, and `output_resolution=1024`; without `height`/`width` the output aspect follows the last reference.[^viggle-turbo-readme]
- **Reported** prompt and resolution guidance: official `Qwen/Qwen-Image-2.1-PE-T2I` / `PE-I2I` rewriters help composition and rendered text though raw prompts work; about 1 MP is the sweet spot and up to about 4 MP works with width/height multiples of 16.[^viggle-turbo-readme]

## 9-step mode

- **Reported** shape: 7 turbo steps, then the LoRA is switched off and the base model finishes the last two; finer detail with small text right more often but not always; about 1.4–1.5× as long as 6 steps and still about 3.5× faster than the base model; works in diffusers and the demo Space only.[^viggle-turbo-readme]
- **Reported** sigmas: `[1.0, 0.9583, 0.9167, 0.875, 0.75, 0.5, 0.25, 1/6, 1/12]` with `num_inference_steps=9` and `true_cfg_scale=1.0`; after the 7th step call `disable_lora()` via `callback_on_step_end`, force KV re-extract from `cached` to `extract` once because the pipeline reuses turbo text/reference K/V, then `enable_lora()` after the call for the next turbo request.[^viggle-turbo-readme]

## ComfyUI

- **Reported** maturity: port described as mostly vibe-coded, sigma schedule matches diffusers to float precision and workflows run end to end, but rough edges expected; tested with ComfyUI 0.37.0 / frontend 1.53.6 with native Qwen-Image-2.1 support.[^viggle-turbo-readme]
- **Reported** assets in `comfyui/`: `viggle_turbo.py` two custom nodes to copy into `ComfyUI/custom_nodes/`; `Qwen-Image-2.1-viggle-turbo-t2i.json` and `-edit.json` workflows; `input/woman2.webp` and `input/cat.webp` example references from the `black-forest-labs/flux-klein-9b-kv` Space to copy into `ComfyUI/input/`.[^viggle-turbo-readme]
- **Reported** model files: `diffusion_models/` `qwen_image_2.1_int8_convrot.safetensors` (7.3 GB) or bf16 (14.2 GB); `text_encoders/` `qwen3vl_8b_int8_convrot.safetensors` (9.4 GB) or bf16 (17.5 GB); `vae/` `qwen_image_2.1_vae_bf16.safetensors` (0.7 GB); `loras/` v0.3 r128 (0.7 GB) or r256 (1.3 GB); workflows default to int8 files, r128 LoRA, and prompt enhancer on, peaking at about 26 GB VRAM at 1248×832.[^viggle-turbo-readme]
- **Reported** nodes: **Viggle Turbo Sigmas** supplies the 6-step schedule with resolution shift, used instead of a KSampler scheduler with euler and `BasicGuider` and no CFG/negative prompt; **Viggle Turbo LoRA (unmerged)** applies the LoRA at runtime like diffusers because stock loaders merge it, which drops about 30% of this adapter's update on bf16 and adds noise on int8, at 10–25% more time per step with strength kept at 1.0.[^viggle-turbo-readme]
- **Reported** gaps: 9-step mode is not in the workflows; edit-workflow output size follows image 1 at about 1 MP; with `comfy_kitchen` 0.2.35 on NVIDIA driver older than 580 the `TextGenerate` enhancer fails — update the driver or turn Enhance prompt off.[^viggle-turbo-readme]

## Single-file merged transformers

- **Reported** construction: base transformer with the r256 LoRA merged in fp32 then quantized once; place in `models/diffusion_models/` with `.gguf` needing ComfyUI-GGUF nodes; text encoder and VAE stay the same Comfy-Org files and **Viggle Turbo Sigmas** is still required; only 6-step mode is available as a single file.[^viggle-turbo-readme]
- **Reported** options with mean LPIPS (VGG, ≤512 px) against diffusers plus r256 LoRA on 96 held-out requests, same prompt/inputs/seed/noise, lower is closer:[^viggle-turbo-readme]

| Format suffix | Size | Loader | LPIPS v0.3 | LPIPS v0.2.1 |
|---|---:|---|---:|---:|
| `-6step-Q8_0.gguf` | 7.7 GB | Unet Loader (GGUF) | 0.051 | 0.054 |
| `-6step-int8_convrot.safetensors` | 7.3 GB | Load Diffusion Model | 0.057 | 0.060 |
| `-6step-Q6_K.gguf` | 6.0 GB | Unet Loader (GGUF) | 0.055 | 0.067 |
| `-6step-fp8_e4m3fn.safetensors` | 7.3 GB | Load Diffusion Model | 0.068 | 0.070 |
| `-6step-Q5_K_M.gguf` | 5.1 GB | Unet Loader (GGUF) | 0.076 | 0.083 |
| `-6step-Q4_K_M.gguf` | 4.3 GB | Unet Loader (GGUF) | 0.100 | 0.118 |
| *reference: Comfy-Org int8 + LoRA r128 LoRA workflow* | 7.3 + 0.7 GB | — | 0.041 | 0.044 |

- **Reported** fidelity reading: merged is close to but not the same as the LoRA path — on most requests it matches up to fine detail, but on a few (about 8 in 96 at int8 or Q8_0 versus 3–5 in 96 for the LoRA workflow) composition or outfit differs without being necessarily worse; use LoRA workflows for diffusers-matching outputs; Q4_K_M drifts visibly more (23–29 of 96) and should be used only if nothing larger fits; for scale, ComfyUI and diffusers differ by about 0.03–0.04 with no LoRA at all.[^viggle-turbo-readme]
- **Reported** workflow mapping: `comfyui/Qwen-Image-2.1-viggle-turbo-{v0.3,v0.2.1}-6step-merged-{t2i,edit}.json` for int8/fp8 and `…-6step-gguf-{t2i,edit}.json` for GGUF, defaulting to int8 and Q8_0 respectively.[^viggle-turbo-readme]

## Limitations and license

- **Reported** limitations: complicated multi-reference, face-swap, identity-preserving, or multi-constraint edits can fall short with duplicated/ghosted figures or identity drift; small or long rendered text garbles more often though 9 steps often helps; colours run a few percent less saturated; v0.3 is a little softer on fine texture than v0.2.1; 2K, RGBA, mask-guided, and >3-reference behavior is checked only by eye on Comparison-tab examples with no standard benchmark claimed.[^viggle-turbo-readme]
- **Reported** license boundary: derivative of Qwen-Image-2.1 under the Qwen RESEARCH LICENSE AGREEMENT for non-commercial research or evaluation only, commercial use needing a separate licence (`model-business@notice.qwencloud.com`); required attribution in `NOTICE`; this repo adds the v0.3/v0.2.1/v0.2 rank-256/128 adapters, merged int8/fp8/GGUF transformers, ComfyUI nodes/workflows/example photos, and the `shift_terminal 0.02 → null` scheduler change while text encoder, VAE, and processor are not redistributed and the base transformer appears only in modified form — a disclosure boundary, not legal verification.[^viggle-turbo-readme]
- **Reported** provenance: distillation and release by Viggle, built with Qwen.[^viggle-turbo-readme]

## Relationships

- Uses the upstream `Qwen/Qwen-Image-2.1` base model and Diffusers `QwenImage21Pipeline`; this concept records only the Viggle turbo packaging and settings, not the base model's own behavior.
- Uses ComfyUI workflows and Comfy-Org encoder/VAE/diffusion files; for GGUF loader mechanics see [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md).
- Related to [Pruna Qwen-Image-2.1 Few-Step LoRA Adapters](pruna-qwen-image-2-1.md), a separate 5-step/8-step distillation with its own sigma schedules; the Viggle source makes no claim about the Pruna adapters and the step/schedule and evaluation setups differ.
- Related to [Qwen-Image-2.1-Fix LoRA Adapter](qwen-image-2-1-fix.md), which targets generation consistency on the same base family; optimization goals differ (fewer steps/speed versus stability).
- For a separate ggml-based local engine that also reports Qwen-Image support, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md).

## Coverage limits

- **Observed:** only `../raw/Qwen-Image-2.1-viggle-turbo/README.md` was statically inspected; no code was executed and no install, download, generation, editing, timing, VRAM, or LPIPS claim was reproduced.
- **Observed:** uninspected material outside this scope includes all `.safetensors`/`.gguf`/peft weights, `comfyui/` nodes/workflows/example images, `scheduler/` config file, `assets/viggle_turbo_promo.mp4`, the demo Space and Comparison tab, upstream `Qwen/Qwen-Image-2.1` weights, `Comfy-Org/Qwen-Image-2.1` encoder/VAE/diffusion files, PE-T2I/PE-I2I rewriters, and ComfyUI-GGUF/`comfy_kitchen` projects.
- Freshness is bounded by the v0.3 2026-09-29 capture; future weight or workflow updates would be a new revision.

[^viggle-turbo-readme]: Model-card README capture in `../raw/Qwen-Image-2.1-viggle-turbo/README.md`; turbo identity, 6-vs-40-step, no-CFG, ~5× faster, quality gaps, and demo Comparison pointer from header; v0.3/v0.2.1/v0.2 dates, 6-step balance, 9-step shape/speed/scope, and capacity view from v0.3 section; file table, rank sizes, and peft/comfyui/scheduler contents from file table; install pins and `QwenImage21Pipeline` status from Install; T2I/edit/9-step code, sigmas, CFG, strength, resolution, reference-order, rewriter, and SVD notes from Usage, Rules, Rank 128, and 9 steps sections; ComfyUI versions, assets, model table, VRAM peak, node behavior, and driver troubleshooting from ComfyUI section; merged construction, format/size/loader/LPIPS table, workflow mapping, and drift counts from Single-file transformers section; edit/text/saturation/texture/2K-RGBA-mask benchmark limits from Known limitations; non-commercial Qwen Research boundary, NOTICE, added-vs-not-redistributed list, and Viggle attribution from License section.
