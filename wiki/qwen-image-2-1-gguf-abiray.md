---
type: Concept
title: Qwen-Image-2.1 GGUF Quantized Checkpoints (Abiray)
description: Community GGUF quants of Qwen-Image-2.1 with size/VRAM options and ComfyUI setup via ComfyUI-GGUF.
tags: [qwen, gguf, quantization, comfyui, image-generation, local-inference]
status: stable
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T04:39:19Z }
sources:
  - id: abiray-qwen-gguf-readme
    resource: ../raw/Abiray-Qwen-Image-2.1-GGUF/README.md
    scope: ../raw/Abiray-Qwen-Image-2.1-GGUF/
    kind: documentation
    title: Qwen-Image-2.1 GGUF Quants
---

Abiray's package provides quantized GGUF checkpoints of `Qwen/Qwen-Image-2.1` for low-VRAM text-to-image and image-to-image generation in ComfyUI via the ComfyUI-GGUF custom node, with six size/VRAM options and packaged workflows.[^abiray-qwen-gguf-readme]

## Quantization options

- **Reported** purpose: quantizing the diffusion transformer reduces memory pressure during generation while preserving sharp detail, composition, and prompt alignment.[^abiray-qwen-gguf-readme]
- **Reported** options and recommended profiles:[^abiray-qwen-gguf-readme]

| Filename | Quant type | Size | Recommended VRAM / profile |
|---|---|---:|---|
| `qwen_image_2.1_Q8_0.gguf` | Q8_0 | 7.59 GB | 12 GB+ (near-lossless fidelity) |
| `qwen_image_2.1_Q6_K.gguf` | Q6_K | 5.88 GB | 10–12 GB (high-quality sweet spot) |
| `qwen_image_2.1_Q5_K_M.gguf` | Q5_K_M | 5.01 GB | 8–10 GB (balanced performance and memory) |
| `qwen_image_2.1_Q4_K_M.gguf` | Q4_K_M | 4.19 GB | 6–8 GB (standard consumer-GPU baseline) |
| `qwen_image_2.1_Q4_K_S.gguf` | Q4_K_S | 4.06 GB | 6–8 GB (compact 4-bit) |
| `qwen_image_2.1_Q3_K_M.gguf` | Q3_K_M | 3.19 GB | 4–6 GB (extreme budget / minimum VRAM) |

- **Synthesis:** the Q6_K entry is positioned as the quality sweet spot, Q5_K_M as the balanced choice, Q4_K_M as the baseline, and Q3_K_M as the minimum-VRAM fallback; no benchmark, protocol, or variance is given, so treat sizes as **reported** file facts and VRAM/fidelity labels as **reported** guidance, not reproduced measurements.[^abiray-qwen-gguf-readme]

## ComfyUI setup

- **Reported** text encoders: download from `Comfy-Org/Qwen-Image-2.1` `text_encoders` and place into `ComfyUI/models/clip/` or `ComfyUI/models/text_encoders/`.[^abiray-qwen-gguf-readme]
- **Reported** VAE: download from `Comfy-Org/Qwen-Image-2.1` `vae` and place into `ComfyUI/models/vae/`.[^abiray-qwen-gguf-readme]
- **Reported** diffusion model: download the chosen `.gguf` from this package and place into `ComfyUI/models/diffusion_models/` or `ComfyUI/models/unet/`.[^abiray-qwen-gguf-readme]
- **Reported** workflows: `Qwen_Image_2.1_GGUF_Text2Image.json` for text-to-image and `Qwen_Image_2.1_GGUF_Image2Image_Edit.json` for image-to-image/editing are packaged in the repo; neither JSON was captured locally and both remain uninspected.[^abiray-qwen-gguf-readme]
- **Reported** procedure: install `ComfyUI-GGUF` via ComfyUI Manager, drag-drop a workflow JSON, select the `.gguf` in the Unet Loader (GGUF) node, verify CLIP/text-encoder and VAE loaders, then queue the prompt; no step was executed or reproduced for this entry.[^abiray-qwen-gguf-readme]

## Provenance and trust boundary

- Base model is **reported** as Qwen Team / Alibaba Cloud `Qwen/Qwen-Image-2.1`; ComfyUI integration assets and pipeline weights are **reported** as provided by Comfy-Org; GGUF quantization is **reported** as powered by llama.cpp and ComfyUI-GGUF.[^abiray-qwen-gguf-readme]
- License frontmatter in the capture states `qwen-research` with a link to the upstream `Qwen-Image-2.1` LICENSE; this is a **reported** disclosure boundary, not legal verification.[^abiray-qwen-gguf-readme]
- Widget frontmatter lists four sample-image outputs, and the body advertises Q4_K_M sample generations, but no images were captured locally and the gallery is empty in this scope.[^abiray-qwen-gguf-readme]

## Relationships

- Uses the upstream Qwen-Image-2.1 base model and Comfy-Org text encoders, VAE, and pipeline weights; this concept records only the Abiray GGUF packaging and setup, not the base model's own behavior.
- Uses ComfyUI with the ComfyUI-GGUF custom node as the supported host; for a separate ggml-based local engine that also reports Qwen-Image-2.1 support, see [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md).
- Related to [Qwen-Image-2.1-Fix LoRA Adapter](qwen-image-2-1-fix.md), which addresses generation consistency on top of a Qwen Image 2.1 checkpoint; the Abiray source makes no claim about that adapter.

## Coverage limits

- **Observed:** only `../raw/Abiray-Qwen-Image-2.1-GGUF/README.md` was statically inspected; no code was executed and no quant, download, placement, workflow, or generation claim was reproduced.
- **Observed:** no immutable revision or date is present in the capture; freshness is unbounded beyond the local capture.
- **Observed:** uninspected linked material outside this scope includes the upstream base model, Comfy-Org text encoders and VAE, both workflow JSONs, widget/sample images, and the ComfyUI-GGUF and llama.cpp projects.
- A similarly named local directory `../raw/Qwen-Image-2.1-GGUF/` is a different source identity and was not ingested in this operation.

[^abiray-qwen-gguf-readme]: Model-card README capture in `../raw/Abiray-Qwen-Image-2.1-GGUF/README.md`; identity, license, and base-model attribution from frontmatter and Acknowledgments; quant table from Quantization Breakdown section; encoder/VAE/model placement from Required Components section; workflow filenames and five-step procedure from Workflows and How to Use sections; sample-generation and credit claims from Sample Generations and Acknowledgments sections.
