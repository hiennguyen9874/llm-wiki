---
license: other
license_name: qwen-research
license_link: LICENSE
base_model: Qwen/Qwen-Image-2.1
base_model_relation: adapter
library_name: diffusers
pipeline_tag: text-to-image
tags:
  - diffusers
  - lora
  - text-to-image
  - image-to-image
  - image-editing
  - distillation
  - turbo
  - few-step
  - qwen-image
  - comfyui
  - gguf
  - int8
  - fp8
  - quantized
---

# Qwen-Image-2.1-viggle-turbo — v0.3

**Built with Qwen.** A few-step distilled version of [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1)
by Viggle. Text-to-image and instruction-driven editing with 1–3 reference images in **6 steps instead of 40**, with
**no classifier-free guidance**.

<video controls autoplay muted loop playsinline width="100%"
  src="https://huggingface.co/Viggle/Qwen-Image-2.1-viggle-turbo/resolve/main/assets/viggle_turbo_promo.mp4"></video>

About **5× faster** than the 40-step base model end to end, and very competitive with it in quality: on the official
Qwen examples the two are hard to tell apart on most prompts. The clearest gaps are small, dense text and complicated
edits ([Known limitations](#known-limitations)). Compare them yourself in the **Comparison** tab of the
[demo Space](https://huggingface.co/spaces/Viggle/Qwen-Image-2.1-viggle-turbo).

## v0.3 (2026-09-29)

* **6 steps, a different balance.** Against v0.2.1: less grain and cleaner surfaces, fine texture a little softer;
  diversity (still close to the base model's) and small-text accuracy about the same. It is not a strict upgrade: if
  you prefer the crisper look, v0.2.1 is still in the repository.
* **New 9-step mode:** 7 turbo steps, then the LoRA is switched off and the base model finishes the last two.
  Finer detail, and small text comes out right more often (not always). It takes about 1.4–1.5× as long as 6 steps
  (still about 3.5× faster than the base model). It works in diffusers and the demo Space only ([9 steps](#9-steps)).
* **We think 6 steps is close to its capacity.** Since v0.2.1, every gain we found at 6 steps cost something
  elsewhere: sharper came with more grain, less grain came with a softer look. Beyond this point, quality most likely
  has to be paid for with steps, which is what the 9-step mode does.

| file | |
|---|---|
| `Qwen-Image-2.1-viggle-turbo-v0.3-6step-lora-r256.safetensors` | **v0.3 LoRA** (rank 256, bf16, 1.3 GB), loaded on the base transformer at runtime. **Use this.** |
| `Qwen-Image-2.1-viggle-turbo-v0.3-6step-lora-r128.safetensors` | the same adapter cut to rank 128 (0.7 GB), used by the [ComfyUI workflows](#comfyui) |
| `peft_v0.3/` | the v0.3 adapter in peft key format |
| `...-{v0.3,v0.2.1}-6step-{int8_convrot,fp8_e4m3fn}.safetensors`, `...-{Q8_0,Q6_K,Q5_K_M,Q4_K_M}.gguf` | the LoRA merged into the base transformer, one file per format, for ComfyUI ([single-file transformers](#single-file-transformers)) |
| `comfyui/` | ComfyUI custom nodes, text-to-image / edit workflows, example inputs |
| `scheduler/` | the base scheduler config with `shift_terminal: null` |
| `...-v0.2.1-6step-lora-r256/r128.safetensors`, `peft_v0.2.1/` | v0.2.1 (2026-09-24), same usage |
| `...-v0.2-5step-lora-r256/r128.safetensors`, `peft_v0.2/` | v0.2 (2026-09-23), same usage (6 steps) |

## Install

```bash
pip install -U torch "transformers>=5.17,<6" accelerate safetensors peft pillow
pip install "git+https://github.com/huggingface/diffusers.git@80c7ed262aeffbeb43ef13ae04baeb9b84515a69"
```

`QwenImage21Pipeline` is not in a released `diffusers` yet, hence the pinned git install. `peft` is required.

## Usage

```python
import torch
from diffusers import QwenImage21Pipeline, FlowMatchEulerDiscreteScheduler

pipe = QwenImage21Pipeline.from_pretrained("Qwen/Qwen-Image-2.1", dtype=torch.bfloat16)
pipe.load_lora_weights(
    "Viggle/Qwen-Image-2.1-viggle-turbo",
    weight_name="Qwen-Image-2.1-viggle-turbo-v0.3-6step-lora-r256.safetensors",
)
pipe.scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(
    "Viggle/Qwen-Image-2.1-viggle-turbo", subfolder="scheduler"
)
pipe.to("cuda")

STEPS, SIGMAS = 6, [1.0, 0.9375, 0.875, 0.75, 0.5, 0.25]   # pass both to every call
```

### Text to image

```python
image = pipe(
    prompt="A studio portrait of an old fisherman mending a net, warm rim light, 85mm.",
    height=1024,
    width=1024,
    num_inference_steps=STEPS,
    sigmas=SIGMAS,
    true_cfg_scale=1.0,                                   # no CFG (also the default)
    generator=torch.Generator("cuda").manual_seed(0),
).images[0]
image.save("out.png")
```

### Image editing (1–3 reference images)

```python
from diffusers.utils import load_image

image = pipe(                                             # same pipe object as above
    prompt="Replace the background with a sunset beach, keep the subject unchanged.",
    image=[load_image("input.png")],                      # list; order fixes <image1>, <image2>, ...
    output_resolution=1024,
    num_inference_steps=STEPS,
    sigmas=SIGMAS,
    true_cfg_scale=1.0,
    generator=torch.Generator("cuda").manual_seed(0),
).images[0]
```

### 9 steps

```python
SIGMAS_9 = [1.0, 0.9583, 0.9167, 0.875, 0.75, 0.5, 0.25, 1 / 6, 1 / 12]

# The pipeline computes the text/reference K/V once and reuses them; those come from the turbo, so the first
# base-model step computes them again.
forward = pipe.transformer.forward
reextract = [False]

def transformer_forward(*args, kv_cache_mode=None, **kwargs):
    if reextract[0] and kv_cache_mode == "cached":
        kv_cache_mode, reextract[0] = "extract", False
    return forward(*args, kv_cache_mode=kv_cache_mode, **kwargs)

pipe.transformer.forward = transformer_forward

def base_tail(pipe, i, t, kwargs):
    if i == 6:                      # runs after the 7th step; the base model takes the last two
        pipe.disable_lora()
        reextract[0] = True
    return kwargs

image = pipe(
    prompt="...",                                         # works for editing too
    num_inference_steps=9,
    sigmas=SIGMAS_9,
    true_cfg_scale=1.0,
    callback_on_step_end=base_tail,
    generator=torch.Generator("cuda").manual_seed(0),
).images[0]
pipe.enable_lora()                                        # back to the turbo for the next call
```

### Rules that matter

* **6 steps with `sigmas=[1.0, 0.9375, 0.875, 0.75, 0.5, 0.25]`, `true_cfg_scale=1.0`, no negative prompt.** These
  are raw nodes: the pipeline applies its resolution-dependent shift to them, so pass them as written at every size.
* **To change the step count, add or remove steps at the high-noise end only**, and keep `0.875, 0.75, 0.5, 0.25`:
  5 steps `[1, 0.875, 0.75, 0.5, 0.25]`, 7 steps `[1, 0.9583, 0.9167, 0.875, 0.75, 0.5, 0.25]`. Moving the low-noise
  nodes makes images softer; plain `num_inference_steps` without `sigmas=` and CFG do not help.
* **Use the shipped scheduler config.** The base config's `shift_terminal: 0.02` wrecks the last step.
* **Keep the LoRA unmerged and at scale 1.0.** Merging it into bf16 weights loses part of the update. For ComfyUI there
  are also [single-file transformers](#single-file-transformers) with the LoRA merged in fp32, then quantized once.
* Reference order decides which image `image 1` / `image 2` in the prompt refers to. Without `height`/`width`, the
  output aspect ratio follows the **last** reference (in ComfyUI: the **first**).
* Prompt rewriting with the official [PE-T2I](https://huggingface.co/Qwen/Qwen-Image-2.1-PE-T2I) /
  [PE-I2I](https://huggingface.co/Qwen/Qwen-Image-2.1-PE-I2I) rewriters helps composition and rendered text. Raw
  prompts work too.
* About 1 MP is the sweet spot; up to about 4 MP works. Keep width and height at multiples of 16.
* `peft` users can load `peft_v0.3/` instead:
  `pipe.transformer.load_lora_adapter("Viggle/Qwen-Image-2.1-viggle-turbo", subfolder="peft_v0.3", weight_name="adapter_model.safetensors", prefix=None)`.
  It holds the same weights under different key names, so pick one of the two, not both.

### Rank 128

The r128 file is the r256 adapter truncated by an exact per-layer SVD of its update. What the cut drops is about ten
times smaller than bf16 rounding of the base weights.

## ComfyUI

> The ComfyUI port is mostly vibe-coded with an AI coding assistant, and I don't use ComfyUI day to day. The sigma
> schedule matches diffusers to float precision and the workflows run end to end, but expect rough edges. Issues
> and fixes are very welcome.

Tested with ComfyUI 0.37.0 (frontend 1.53.6), which has native Qwen-Image-2.1 support. In [`comfyui/`](comfyui):

* `viggle_turbo.py` — two custom nodes. Copy it into `ComfyUI/custom_nodes/` and restart ComfyUI.
* `Qwen-Image-2.1-viggle-turbo-t2i.json`, `Qwen-Image-2.1-viggle-turbo-edit.json` — the workflows (drag into ComfyUI).
* `input/woman2.webp`, `input/cat.webp` — the edit workflow's example references (from the
  [black-forest-labs/flux-klein-9b-kv](https://huggingface.co/spaces/black-forest-labs/flux-klein-9b-kv) Space); copy
  them into `ComfyUI/input/`.

| ComfyUI folder | file | size |
|---|---|---|
| `diffusion_models/` | [`qwen_image_2.1_int8_convrot.safetensors`](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) or `qwen_image_2.1_bf16.safetensors` | 7.3 / 14.2 GB |
| `text_encoders/` | [`qwen3vl_8b_int8_convrot.safetensors`](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) or `qwen3vl_8b_bf16.safetensors` | 9.4 / 17.5 GB |
| `vae/` | [`qwen_image_2.1_vae_bf16.safetensors`](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) | 0.7 GB |
| `loras/` | `Qwen-Image-2.1-viggle-turbo-v0.3-6step-lora-r128.safetensors` (this repo) or the r256 file | 0.7 / 1.3 GB |

The workflows default to the int8 files, the r128 LoRA and the prompt enhancer on; this peaks at about 26 GB of VRAM
at 1248 × 832.

* **Viggle Turbo Sigmas** — the 6-step schedule with the pipeline's resolution-dependent shift. Use it instead of a
  KSampler scheduler, with euler and `BasicGuider` (no CFG, no negative prompt).
* **Viggle Turbo LoRA (unmerged)** — applies the LoRA at runtime, as diffusers does. The stock LoRA loaders merge it
  into the weights, which drops about 30% of this adapter's update on bf16 and adds noise on int8. The unmerged node
  costs 10–25% more time per step. Keep its strength at 1.0.

The 9-step mode is not in the workflows. In the edit workflow the output size follows **image 1**, at about 1 MP.

**Troubleshooting:** with `comfy_kitchen` 0.2.35 on an NVIDIA driver older than 580, `TextGenerate` (the prompt
enhancer) fails with a CUDA driver error. Update the driver, or turn *Enhance prompt* off.

### Single-file transformers

If you would rather not load a LoRA, these files are the base transformer with the r256 LoRA already merged in
(in fp32, then quantized once). Put the file in `models/diffusion_models/` (`.gguf` files need the
[ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) nodes) and open the matching workflow in `comfyui/`. The text
encoder and VAE are the same Comfy-Org files as above, and you still need **Viggle Turbo Sigmas** from
`comfyui/viggle_turbo.py`. Only the 6-step mode is available as a single file.

| format | file suffix | size | ComfyUI loader | LPIPS ¹ v0.3 | LPIPS ¹ v0.2.1 |
|---|---|---|---|---|---|
| GGUF Q8_0 | `-6step-Q8_0.gguf` | 7.7 GB | Unet Loader (GGUF) | 0.051 | 0.054 |
| int8 (Comfy-Org convrot recipe) | `-6step-int8_convrot.safetensors` | 7.3 GB | Load Diffusion Model | 0.057 | 0.060 |
| GGUF Q6_K | `-6step-Q6_K.gguf` | 6.0 GB | Unet Loader (GGUF) | 0.055 | 0.067 |
| fp8 e4m3fn, weight-only | `-6step-fp8_e4m3fn.safetensors` | 7.3 GB | Load Diffusion Model | 0.068 | 0.070 |
| GGUF Q5_K_M | `-6step-Q5_K_M.gguf` | 5.1 GB | Unet Loader (GGUF) | 0.076 | 0.083 |
| GGUF Q4_K_M ² | `-6step-Q4_K_M.gguf` | 4.3 GB | Unet Loader (GGUF) | 0.100 | 0.118 |
| *reference:* Comfy-Org int8 + LoRA r128 (the LoRA workflows) | | 7.3 + 0.7 GB | | 0.041 | 0.044 |

Full names are `Qwen-Image-2.1-viggle-turbo-v0.3` or `-v0.2.1` followed by the suffix. Workflows:
`comfyui/Qwen-Image-2.1-viggle-turbo-{v0.3,v0.2.1}-6step-merged-{t2i,edit}.json` (int8 by default; pick the fp8 file
in the loader) and `…-6step-gguf-{t2i,edit}.json` (Q8_0 by default; pick another GGUF in the loader).

**Merged is close to, but not the same as, the LoRA path.** On most requests the image matches the LoRA workflow up to
fine detail, but on a few (about 8 in 96 at int8 or Q8_0, against 3–5 in 96 for the LoRA workflow) the merged model
settles on a different composition or outfit. The result is not necessarily worse, just different. If you need
outputs that match diffusers, use the LoRA workflows.

² **Q4_K_M drifts visibly more** (23–29 of 96 requests change noticeably). Use it only if nothing larger fits in memory.

¹ mean LPIPS (VGG, ≤512 px) against diffusers with the r256 LoRA on our 96 held-out requests, same prompt, inputs,
seed and noise; lower is closer. For scale, ComfyUI and diffusers differ by about 0.03–0.04 with no LoRA at all.

## Known limitations

* **Complicated edits** (multi-reference composition, face swaps, identity-preserving edits, instructions with
  several constraints) can still fall short of the base model: duplicated or ghosted figures, identity drift.
* **Small or long rendered text** garbles more often than with the base model. 9 steps often helps, not always.
* Colours come out a few percent less saturated than the base model's.
* At 6 steps, v0.3 is a little softer on fine texture than v0.2.1.
* 2K output, RGBA output, mask-guided edits and edits with more than 3 references are checked only by eye on the
  Comparison tab examples. No standard benchmark is claimed.

## License

This model is a derivative work of Qwen-Image-2.1 and is distributed under the **Qwen RESEARCH LICENSE AGREEMENT**
([`LICENSE`](LICENSE)): **non-commercial use only** — research or evaluation purposes. Commercial use requires a
separate licence from the licensor (`model-business@notice.qwencloud.com`). See [`NOTICE`](NOTICE) for the required
attribution.

> Qwen is licensed under the Qwen RESEARCH LICENSE AGREEMENT, Copyright (c) 2026 Hangzhou Tongyi Laboratory Technology
> Co., Ltd. All Rights Reserved.

Relative to [`Qwen/Qwen-Image-2.1`](https://huggingface.co/Qwen/Qwen-Image-2.1) this repository **adds** LoRA
adapters (v0.3, v0.2.1 and v0.2, at rank 256 and 128), single-file transformers (the base transformer with the v0.3 or
v0.2.1 adapter merged in, quantized to int8, fp8 or GGUF), ComfyUI nodes, workflows and two example input photos, and a
scheduler config with `shift_terminal` changed from `0.02` to `null`. Text encoder, VAE and processor are not
redistributed; the base transformer only in modified form (see [`NOTICE`](NOTICE)).

Distillation and release by **Viggle**. **Built with Qwen.**
