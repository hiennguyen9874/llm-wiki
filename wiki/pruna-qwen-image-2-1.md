---
type: Concept
title: Pruna Qwen-Image-2.1 Few-Step LoRA Adapters
description: DMD-distilled 5-step and 8-step LoRA adapters for faster Qwen-Image-2.1 text-to-image and editing without CFG.
tags: [qwen, lora, distillation, image-generation, image-editing, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T04:47:48Z }
sources:
  - id: pruna-qwen-21-readme
    resource: ../raw/Pruna-Qwen-Image-2.1/README.md
    scope: ../raw/Pruna-Qwen-Image-2.1/
    kind: documentation
    revision: v0.1
    title: Pruna-Qwen-Image-2.1 model card
---

Pruna-Qwen-Image-2.1 is a set of PrunaAI LoRA adapters reported to let `Qwen/Qwen-Image-2.1` generate and edit images in 5 or 8 steps instead of the base-model regime, loading on top of the unchanged pipeline, text encoder, and VAE with no CFG.[^pruna-qwen-21-readme]

## Variants and trade-off

- **Reported** identity: few-step LoRA adapters for `Qwen/Qwen-Image-2.1`, DMD-based training; pipeline, text encoder, and VAE stay unchanged.[^pruna-qwen-21-readme]
- **Reported** options, both v0.1, load one at a time because each is trained for its own sigma schedule:[^pruna-qwen-21-readme]

| File | Steps | Trade-off |
|---|:---:|---|
| `p_qwen_image_2.1_8step_v0.1.safetensors` | 8 | Higher quality; recommended default |
| `p_qwen_image_2.1_5step_v0.1.safetensors` | 5 | Higher speed, noticeably lower visual quality |

- **Reported** headline: 5 or 8 steps, up to 6.3x faster, no CFG, text-to-image and image editing covered by the same pipeline.[^pruna-qwen-21-readme]
- **Reported** maturity: v0.1 first release, work in progress; does not yet match base-model visual quality and will be updated.[^pruna-qwen-21-readme]

## Use conditions

- **Reported** training coverage: 1K resolution only, with simple and upsampled prompts, text-to-image generation, and single- and multi-image editing with up to 3 reference images.[^pruna-qwen-21-readme]
- **Reported** starting point: 1024 × 1024 and at most 3 reference images for editing; higher resolutions including 2K and more reference images may work but are outside training coverage so quality may vary.[^pruna-qwen-21-readme]
- **Reported** prompting: upsampling is optional; detailed prompts usually give better results, especially longer descriptive text-to-image prompts covering subject, setting, lighting, and style.[^pruna-qwen-21-readme]
- **Reported** fixed settings: keep LoRA strength at 1.0, keep `true_cfg_scale=1.0` with no negative prompt, and do not use other step counts, schedules, or CFG values.[^pruna-qwen-21-readme]

## Scheduler and sigma schedules

- **Reported** scheduler setup: use `FlowMatchEulerDiscreteScheduler` with `use_dynamic_shifting=False`, `shift=1.0`, `shift_terminal=None`, passing the sigmas exactly as given with no extra shifting.[^pruna-qwen-21-readme]
- **Reported** 8-step sigmas: `1 → 14/15 → 6/7 → 10/13 → 2/3 → 6/11 → 0.4 → 2/9 → 0`, described as shift 2 computed as `σ = 2t / (1 + t)` on evenly spaced `t`.[^pruna-qwen-21-readme]
- **Reported** 5-step sigmas: `1 → 0.94 → 6/7 → 2/3 → 0.4 → 0`; terminal sigma 0 is appended by the scheduler.[^pruna-qwen-21-readme]
- **Reported** runtime needs: CUDA GPU, `torch>=2.4.0`, `transformers>=5.17`, `accelerate`, `peft`, `pillow`, plus `diffusers` at commit `6256aa7666cedd47443adc8f82da9a10e110b09c`; load via `QwenImage21Pipeline.from_pretrained("Qwen/Qwen-Image-2.1", torch_dtype=torch.bfloat16)` then `load_lora_weights("PrunaAI/Pruna-Qwen-Image-2.1", weight_name=...)`.[^pruna-qwen-21-readme]

## Benchmark protocol and limits

- **Reported** protocol: official Qwen model-card example prompt, BF16, batch size 1, one NVIDIA H100 80 GB, median of 3 requests after one warmup per configuration; includes prompt encoding, denoising, and decoding; excludes PNG saving, model loading, and warmup.[^pruna-qwen-21-readme]
- **Reported** comparison basis: base at 40 steps with KV cache on versus Pruna adapters at 5 or 8 steps with KV cache off as configured for the benchmark; the worked examples enable `use_kv_cache=True` for Pruna but the chart was not remeasured with that setting.[^pruna-qwen-21-readme]
- **Reported** LoRAs were unmerged with no CFG, compilation, or CPU offload; timings do not imply equal image quality.[^pruna-qwen-21-readme]
- **Synthesis:** treat the 2K timings as inference-speed signals only, not quality guarantees at 2K, per the source's own training-coverage warning; treat the up-to-6.3x speedup as a **reported** figure under the above H100 protocol, not a reproduced measurement.[^pruna-qwen-21-readme]

## Limitations and non-goals

- **Reported** limitations: first-version quality below the base model; 5-step visibly worse than 8-step; short or vague text-to-image prompts give weaker results.[^pruna-qwen-21-readme]
- **Reported** non-goals: not a standalone model (needs `Qwen/Qwen-Image-2.1` base weights); not a replacement when full base quality is needed; not a finished release and weights are expected to change.[^pruna-qwen-21-readme]
- License frontmatter states `qwen-research` with `base_model: Qwen/Qwen-Image-2.1`; the body states the adapters are a derivative distributed under the Qwen RESEARCH LICENSE AGREEMENT with use restrictions to review before use or redistribution — a **reported** disclosure boundary, not legal verification.[^pruna-qwen-21-readme]

## Relationships

- Uses the upstream `Qwen/Qwen-Image-2.1` base model and Diffusers `QwenImage21Pipeline`; this concept records only the Pruna few-step LoRA packaging and settings, not the base model's own behavior.
- Related to [Qwen-Image-2.1-Fix LoRA Adapter](qwen-image-2-1-fix.md), which targets generation consistency on the same base-model family; the Pruna source makes no claim about that adapter, and the optimization goals differ (fewer steps/speed versus stability).
- Related to [Qwen-Image-2.1 GGUF Quantized Checkpoints (Abiray)](qwen-image-2-1-gguf-abiray.md), which targets lower VRAM via quantization for ComfyUI; Pruna targets fewer steps via LoRA distillation in Diffusers, a distinct efficiency axis.
- For a separate ggml-based local engine that also reports Qwen-Image-2.1 support, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md).

## Coverage limits

- **Observed:** only `../raw/Pruna-Qwen-Image-2.1/README.md` was statically inspected; no code was executed and no install, download, generation, editing, or timing claim was reproduced.
- **Observed:** outside-scope or uncaptured material includes the `Qwen/Qwen-Image-2.1` base weights, both `.safetensors` adapters, the pinned `diffusers` commit, `assets/` header and four benchmark images, and the Pruna, dashboard, social, and Hugging Face URLs.
- Freshness is bounded by the v0.1 work-in-progress disclaimer in the capture; no capture date or immutable repo revision is present, so future weight updates would be a new revision.

[^pruna-qwen-21-readme]: Model-card README capture in `../raw/Pruna-Qwen-Image-2.1/README.md`; adapter identity, DMD basis, unchanged pipeline/encoder/VAE, v0.1 status, and up-to-6.3x/no-CFG/t2i-plus-editing headline from header and intro; variant filenames and quality/speed trade-off from Variants table; 1K-only training, up-to-3-images, 1024 start, 2K caveat, and prompt guidance from Prompts section; H100/BF16/median-of-3/KV-cache benchmark inclusions and exclusions from Benchmarking section; CUDA/pip/pipeline/LoRA/scheduler/sigma/CFG/strength settings from Quickstart and Recommended settings; limitations, non-goals, and Qwen Research license boundary from Limitations, What-this-is-not, and License sections.
