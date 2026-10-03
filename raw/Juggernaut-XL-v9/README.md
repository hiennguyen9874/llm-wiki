---
license: creativeml-openrail-m
language:
- en
library_name: diffusers
pipeline_tag: text-to-image
base_model: stabilityai/stable-diffusion-xl-base-1.0
tags:
- stable-diffusion
- stable-diffusion-xl
- sdxl
- text-to-image
- photorealistic
- photography
- cinematic
- portrait
- juggernaut
- rundiffusion
- kandooai
---

<div align="center">

<a href="https://www.rundiffusion.com/juggernaut?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=header_banner">
  <img src="https://huggingface.co/RunDiffusion/Juggernaut-XL-v9/resolve/main/assets/Juggernaut_v9_banner.webp" alt="Juggernaut XL v9 — by RunDiffusion" />
</a>

<h1>Juggernaut XL v9 by RunDiffusion</h1>

<p><i>The world's most-downloaded SDXL model — purpose-built for photorealism.</i></p>

<p><b>6M+ downloads on Hugging Face · Overwhelmingly Positive on Civitai · 26 months in production</b></p>

<p>
  <a href="https://app.rundiffusion.com/login?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=hero_cta"><img alt="Try Juggernaut XL v9 — Free" src="https://img.shields.io/badge/%E2%96%B6%20Try%20Juggernaut%20XL%20v9%20%E2%80%94%20Free-7C3AED?style=for-the-badge&labelColor=7C3AED"></a>
</p>

<p>
  <a href="https://www.rundiffusion.com/prompting?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=prompting_resource"><img alt="Prompting Guides" src="https://img.shields.io/badge/%F0%9F%93%96%20Prompting%20Guides-1f1f23?style=for-the-badge"></a>&nbsp;<a href="https://www.rundiffusion.com/juggernaut?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=lineup_compare"><img alt="Compare the Lineup" src="https://img.shields.io/badge/Compare%20the%20Lineup-1971c2?style=for-the-badge&labelColor=1f1f23"></a>&nbsp;<a href="https://civitai.com/models/133005/juggernaut-xl"><img alt="Civitai" src="https://img.shields.io/badge/Civitai-Overwhelmingly%20Positive-EAB308?style=for-the-badge&labelColor=1f1f23"></a>&nbsp;<img alt="License: CreativeML Open RAIL-M" src="https://img.shields.io/badge/License-OpenRAIL--M-2ea44f?style=for-the-badge">
</p>

</div>

> Juggernaut XL is the most popular SDXL fine-tune in the world. Version 9 — co-developed by **KandooAI** and **RunDiffusion**, integrating **RunDiffusion Photo v2** — is the proven photorealism workhorse trusted by **hundreds of thousands of creators**: 6M+ all-time downloads on Hugging Face, 1.5M+ on Civitai, and an *Overwhelmingly Positive* rating across 7,780+ reviews.

## Why Juggernaut XL v9 in 2026?

The SDXL ecosystem is the single most mature corner of open image generation, and v9 is its most refined photorealism checkpoint. Choose Juggernaut XL v9 when you want:

- 📸 **Photorealism that holds up under scrutiny** — skin texture, micro-contrast, and natural lighting that translates from concept to print.
- 💻 **Reasonable hardware** — runs comfortably on 8 GB of VRAM, unlike newer DiT-based models that demand 16+ GB.
- 🧰 **The full SDXL toolbox** — drop-in compatibility with the thousands of SDXL ControlNets, IP-Adapter variants, AnimateDiff, regional prompting tools, and LoRAs already in your workflow.
- 🏆 **Battle-tested reliability** — 26+ months in production, used in agencies, studios, and shipping products around the world.

For experimental and frontier work, see the rest of the [Juggernaut family](#looking-for-something-newer). For SDXL photorealism, this is the king of the hill.

---

<div align="center">

<h3>🚀 Skip the setup. Try Juggernaut XL v9 in your browser.</h3>

<p>No installs. No GPU rental. No model downloads. <b>Just generate.</b></p>

<a href="https://app.rundiffusion.com/login?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=midpage_cta"><img alt="Launch Juggernaut on RunDiffusion" src="https://img.shields.io/badge/%E2%96%B6%20Launch%20on%20RunDiffusion-7C3AED?style=for-the-badge&labelColor=7C3AED"></a>

<p><i>Pre-loaded into ComfyUI · Forge · Automatic1111 · Fooocus · InvokeAI · SwarmUI</i></p>

</div>

---

## What V9 Brought Over V8

- **RunDiffusion Photo v2** integration — a substantial upgrade to the photographic backbone of the model
- Improved **skin detail** and micro-texture rendering
- Stronger **lighting** and **contrast** control
- Better consistency across **portrait**, **architecture**, **automotive**, **wildlife**, **food**, **interior**, and **landscape** photography

## Two Ways to Run Juggernaut XL v9

### 🚀 Easiest — Run it on RunDiffusion (recommended)

One-click access to Juggernaut XL v9 inside the UI you already know — ComfyUI, Forge, Automatic1111, Fooocus, InvokeAI, or SwarmUI. No setup, no model downloads, no GPU to rent. **Free trial included.**

<div align="center">
  <a href="https://app.rundiffusion.com/login?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=quickstart_try"><img alt="Get Started Free" src="https://img.shields.io/badge/Get%20Started%20Free%20%E2%86%92-7C3AED?style=for-the-badge&labelColor=7C3AED"></a>
</div>

### 💻 Or run it locally — Diffusers

```python
import torch
from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained(
    "RunDiffusion/Juggernaut-XL-v9",
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True,
).to("cuda")

prompt = "Cinematic mid shot photo of an astronaut walking through a neon-lit Tokyo alley at night, hyperdetailed photography, skin details, shallow depth of field"

image = pipe(
    prompt,
    width=832, height=1216,
    num_inference_steps=35,
    guidance_scale=5.0,
).images[0]

image.save("juggernaut_xl_v9.png")
```

For ComfyUI / Forge / InvokeAI / SwarmUI: download `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors` and drop it into your `models/checkpoints/` directory.

## Recommended Settings

| Parameter | Value |
| --- | --- |
| Resolution | `832 × 1216` (portrait) · `1216 × 832` (landscape) |
| Sampler | `DPM++ 2M Karras` |
| Steps | `30 – 40` |
| CFG scale | `3 – 7` (lower = more realistic) |
| VAE | **Already baked in** — no external VAE required |
| Hi-Res fix | `4xNMKD-Siax_200k` upscaler · 15 steps · 0.3 denoise · 1.5× upscale |

> **Negative prompts:** start with **none**. Add specific things you don't want as you iterate. Heavy negatives often hurt more than they help on this model.

### Useful Prompt Keywords

These tokens reliably steer output:

```
Architecture Photography · Wildlife Photography · Car Photography
Food Photography · Interior Photography · Landscape Photography
Hyperdetailed Photography · Cinematic Movie · Still Mid Shot Photo
Full Body Photo · Skin Details
```

📖 **For deeper prompting technique** — sampler choices, multi-subject framing, lighting language, negative-prompt strategy — see the [**RunDiffusion prompting library**](https://www.rundiffusion.com/prompting?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=prompting_inline). Free to read, no signup.

## Files In This Repo

| File | Purpose |
| --- | --- |
| `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors` | Single-file checkpoint for ComfyUI / Forge / InvokeAI / SwarmUI |
| `unet/`, `text_encoder/`, `text_encoder_2/`, `vae/`, `tokenizer/`, `tokenizer_2/`, `scheduler/`, `model_index.json` | Diffusers-format directory tree (FP16 variant) for `from_pretrained` |

## Looking For Something Newer?

The Juggernaut family has continued to evolve. Match the model to your project:

| Model | Architecture | Best for |
| --- | --- | --- |
| **[Juggernaut Z](https://huggingface.co/RunDiffusion/Juggernaut-Z-Image)** | Lumina-Image-2 | Cinematic, presentation-ready output with stronger lighting and atmosphere |
| **[Juggernaut Pro Flux](https://www.rundiffusion.com/juggernaut-pro-flux?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=cross_promo_pro_flux)** | FLUX.1 | Highest photo quality with strong consistency and lower token cost |
| **[Juggernaut XII / XIII Ragnarok](https://www.rundiffusion.com/juggernaut?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=cross_promo_family)** | SDXL | The latest evolutions of the SDXL line, refined for prompt adherence and realism |
| **Juggernaut XL v9** *(this model)* | SDXL 1.0 | Proven SDXL photorealism workhorse with the broadest tooling ecosystem |

All of them — and 100+ other SOTA models — are pre-loaded on **[RunDiffusion](https://app.rundiffusion.com/login?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=family_compare)**. Switch between them in two clicks.

## Commercial Use

This model **may not be deployed behind paid API services** without explicit licensing. For commercial licensing, custom models, business inquiries, or consultation, contact **[juggernaut@rundiffusion.com](mailto:juggernaut@rundiffusion.com)**.

You are free to use this model for personal and creative work under the terms of the [CreativeML Open RAIL-M license](https://huggingface.co/spaces/CompVis/stable-diffusion-license).

## Credits

Juggernaut XL v9 was created by **[KandooAI](https://twitter.com/Juggernaut_AI)** in collaboration with **[RunDiffusion](https://www.rundiffusion.com/?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=credits)**. The photographic backbone — **RunDiffusion Photo v2** — was developed by the RunDiffusion team. Thanks to **Adam Stewart** for prompting workflow.

---

<div align="center">

<h3>Ready to generate?</h3>

<p>Juggernaut XL v9 is one click away — no setup, no GPU rental, no model downloads.</p>

<a href="https://app.rundiffusion.com/login?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=footer_cta"><img alt="Try Juggernaut XL v9 — Free" src="https://img.shields.io/badge/%E2%96%B6%20Try%20Juggernaut%20XL%20v9%20%E2%80%94%20Free-7C3AED?style=for-the-badge&labelColor=7C3AED"></a>

<p><sub><a href="https://www.rundiffusion.com/juggernaut?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=footer_lineup">Compare the full Juggernaut lineup</a> · <a href="https://www.rundiffusion.com/prompting?utm_source=huggingface&utm_medium=model_card&utm_campaign=juggernaut_xl_v9&utm_content=footer_prompting">Prompting guides</a> · <a href="mailto:juggernaut@rundiffusion.com">Commercial licensing</a></sub></p>

</div>
