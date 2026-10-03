---
type: Concept
title: Juggernaut XL v9 Photorealism Model
description: RunDiffusion/KandooAI SDXL photorealism fine-tune with baked-in VAE, 8 GB VRAM target, and SDXL tooling compatibility under Open RAIL-M.
tags: [sdxl, text-to-image, diffusion, photorealism, local-inference, image-generation]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T00:00:00Z }
sources:
  - id: juggernaut-xl-v9-readme
    resource: ../raw/Juggernaut-XL-v9/README.md
    scope: ../raw/Juggernaut-XL-v9/
    kind: documentation
    title: Juggernaut XL v9 model card
---

Juggernaut XL v9 is a **reported** SDXL-base photorealism fine-tune by KandooAI and RunDiffusion integrating RunDiffusion Photo v2, positioned as a battle-tested 8 GB VRAM workhorse with baked-in VAE and full SDXL tooling compatibility under CreativeML Open RAIL-M.[^juggernaut-xl-v9-readme]

## Identity and key features

- **Reported** identity: SDXL fine-tune on base `stabilityai/stable-diffusion-xl-base-1.0`; Hugging Face `RunDiffusion/Juggernaut-XL-v9`; co-developed by KandooAI and RunDiffusion with photographic backbone RunDiffusion Photo v2; prompting workflow credit to Adam Stewart.[^juggernaut-xl-v9-readme]
- **Reported** adoption: 6M+ Hugging Face downloads, 1.5M+ Civitai downloads, Overwhelmingly Positive across 7,780+ reviews, 26 months in production; used in agencies, studios, and shipping products.[^juggernaut-xl-v9-readme]
- **Reported** positioning: most-downloaded SDXL model, refined for photorealism — skin texture, micro-contrast, natural lighting; improved skin detail, lighting and contrast control, and consistency across portrait, architecture, automotive, wildlife, food, interior, and landscape photography in v9 over v8.[^juggernaut-xl-v9-readme]
- **Reported** hardware target: runs comfortably on 8 GB VRAM, unlike newer DiT-based models requiring 16+ GB.[^juggernaut-xl-v9-readme]
- **Reported** ecosystem advantage: drop-in compatibility with SDXL ControlNets, IP-Adapter variants, AnimateDiff, regional prompting tools, and LoRAs.[^juggernaut-xl-v9-readme]
- **Reported** family context: v9 is the proven SDXL 1.0 workhorse; newer siblings are Juggernaut Z (Lumina-Image-2, cinematic), Juggernaut Pro Flux (FLUX.1, photo quality/consistency), and Juggernaut XII/XIII Ragnarok (SDXL, prompt adherence/realism); all pre-loaded on hosted RunDiffusion alongside 100+ other models.[^juggernaut-xl-v9-readme]

## Usage

- **Reported** hosted path: one-click access on RunDiffusion inside ComfyUI, Forge, Automatic1111, Fooocus, InvokeAI, or SwarmUI; free trial included; no install, download, or GPU rental in that path.[^juggernaut-xl-v9-readme]
- **Reported** local checkpoint path: download `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors` into `models/checkpoints/` for ComfyUI / Forge / InvokeAI / SwarmUI.[^juggernaut-xl-v9-readme]
- **Reported** local Diffusers procedure: `DiffusionPipeline.from_pretrained("RunDiffusion/Juggernaut-XL-v9", torch_dtype=torch.float16, variant="fp16", use_safetensors=True).to("cuda")`; example uses prompt `Cinematic mid shot photo of an astronaut walking through a neon-lit Tokyo alley at night, hyperdetailed photography, skin details, shallow depth of field`, `width=832, height=1216, num_inference_steps=35, guidance_scale=5.0`, saving to `juggernaut_xl_v9.png`.[^juggernaut-xl-v9-readme]
- **Synthesis:** treat the Diffusers snippet as a **reported** entry-point example, not a reproduced run; no install, download, or generation was executed for this concept.[^juggernaut-xl-v9-readme]

## Recommended settings

All values **reported** in the Recommended Settings table; VAE handling is explicit:[^juggernaut-xl-v9-readme]

- Resolution: `832 × 1216` portrait, `1216 × 832` landscape.
- Sampler: `DPM++ 2M Karras`; steps `30–40`; CFG `3–7` with lower values more realistic.
- VAE: already baked in, no external VAE required.
- Hi-Res fix: `4xNMKD-Siax_200k` upscaler, 15 steps, 0.3 denoise, 1.5× upscale.
- Negative prompts: start with none; add specific exclusions iteratively; heavy negatives often hurt.

## Prompting

- **Reported** steering tokens: `Architecture Photography`, `Wildlife Photography`, `Car Photography`, `Food Photography`, `Interior Photography`, `Landscape Photography`, `Hyperdetailed Photography`, `Cinematic Movie`, `Still Mid Shot Photo`, `Full Body Photo`, `Skin Details`.[^juggernaut-xl-v9-readme]
- **Reported** further guidance: RunDiffusion prompting library covers sampler choices, multi-subject framing, lighting language, and negative-prompt strategy; library itself was not captured locally and remains uninspected.[^juggernaut-xl-v9-readme]

## Files and distribution

- **Reported** repo contents: single-file `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors` for UI checkpoint folders plus Diffusers-format tree (`unet/`, `text_encoder/`, `text_encoder_2/`, `vae/`, `tokenizer/`, `tokenizer_2/`, `scheduler/`, `model_index.json`) as FP16 variant for `from_pretrained`.[^juggernaut-xl-v9-readme]
- **Observed:** only `../raw/Juggernaut-XL-v9/README.md` exists locally; the `.safetensors` weights and Diffusers subdirectories are absent and uninspected.[^juggernaut-xl-v9-readme]

## License and disclosure boundary

- **Reported** license: CreativeML Open RAIL-M; frontmatter declares `license: creativeml-openrail-m`, `base_model: stabilityai/stable-diffusion-xl-base-1.0`, `library_name: diffusers`, `pipeline_tag: text-to-image`, language `en`.[^juggernaut-xl-v9-readme]
- **Reported** commercial constraint: may not be deployed behind paid API services without explicit licensing; contact `juggernaut@rundiffusion.com` for commercial licensing, custom models, or consultation; personal and creative use permitted under Open RAIL-M terms.[^juggernaut-xl-v9-readme]
- **Observed:** no immutable revision hash, publication date, or local capture date is present in the capture; freshness is unbounded beyond local capture.
- **Synthesis:** verify current license and paid-API terms upstream before commercial or service deployment.[^juggernaut-xl-v9-readme]

## Relationships

- Uses SDXL-base lineage shared with the SDXL tooling ecosystem; for a ggml-based local engine that reports SD-family support, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md).
- Complements [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md): Juggernaut v9 documents a standard `.safetensors` checkpoint drop-in for ComfyUI/Forge/InvokeAI/SwarmUI, while ComfyUI-GGUF covers GGUF-quantized UNET/DiT workflows.
- Contrasts with [FLUX.1-dev Text-to-Image Model](flux-1-dev.md) and [FLUX.1-schnell Text-to-Image Model](flux-1-schnell.md): DiT-based 12B rectified-flow models with higher VRAM demands versus Juggernaut v9's **reported** 8 GB SDXL photorealism target and broader mature SDXL adapter/tooling compatibility.

## Coverage limits

- **Observed:** only `../raw/Juggernaut-XL-v9/README.md` was statically inspected; no code was executed and no install, hosted run, Diffusers generation, quality, VRAM, compatibility, or download-count claim was reproduced.
- **Observed:** uninspected or absent material includes the `.safetensors` weights, Diffusers subdirectories, header banner asset, Civitai page, RunDiffusion hosted app, prompting library, Juggernaut Z / Pro Flux / XII / XIII pages, and full Open RAIL-M license text.
- All capability, compatibility, efficiency, adoption, and permission statements above are **reported** by the model card, not independently verified.
- No measurements, evaluation protocol, variance, ablations, or negative-result analysis are present in this capture.

[^juggernaut-xl-v9-readme]: Model-card capture in `../raw/Juggernaut-XL-v9/README.md`; frontmatter license, base model, library, pipeline tag, and language; identity, creators, Photo v2, and credits from header and Credits; adoption and positioning from header, quote, and Why Juggernaut XL v9 in 2026; v9 improvements from What V9 Brought Over V8; hosted and local paths plus Diffusers snippet from Two Ways to Run; sampler, steps, CFG, resolution, baked-in VAE, Hi-Res fix, and negative-prompt advice from Recommended Settings; steering tokens and prompting library from Useful Prompt Keywords; checkpoint plus Diffusers tree from Files In This Repo; sibling models and hosted lineup from Looking For Something Newer; paid-API restriction and contact from Commercial Use.
