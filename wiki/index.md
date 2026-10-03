---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts
- [ComfyUI-GGUF Quantized Model Support](comfyui-gguf.md) — Custom nodes for running GGUF-quantized UNET/DiT and T5 models in ComfyUI.
- [FLUX.1-dev Text-to-Image Model](flux-1-dev.md) — Black Forest Labs 12B rectified flow text-to-image model with guidance distillation and non-commercial licensing.
- [FLUX.1-schnell Text-to-Image Model](flux-1-schnell.md) — Black Forest Labs 12B rectified flow text-to-image model with latent adversarial diffusion distillation for 1-4 step inference under Apache-2.0.
- [Ideogram 4 Text-to-Image Model](ideogram-4.md) — Ideogram 9.3B open-weight flow-matching text-to-image foundation model with JSON prompting, layout and palette control, and nf4/fp8 releases under a non-commercial license.
- [Image Model, Library, and Workflow Roles](image-inference-tool-roles.md) — Distinguishes image-model weights from Diffusers Python pipelines, ComfyUI graph workflows, and the stable-diffusion.cpp C/C++ inference engine.
- [Juggernaut XL v9 Photorealism Model](juggernaut-xl-v9.md) — RunDiffusion/KandooAI SDXL photorealism fine-tune with baked-in VAE, 8 GB VRAM target, and SDXL tooling compatibility under Open RAIL-M.
- [Krea 2 Raw Text-to-Image Model](krea-2-raw.md) — Krea.ai 12B diffusion-transformer text-to-image base checkpoint for fine-tuning, with a post-trained Turbo variant under the Krea 2 Community License.
- [Krea 2 Turbo Text-to-Image Model](krea-2-turbo.md) — Krea.ai 12B diffusion-transformer distilled checkpoint for few-step text-to-image inference under the Krea 2 Community License.
- [Latent Image Generation Pipeline](latent-image-generation.md) — How prompt embeddings, noisy latents, an image network, a scheduler, and a VAE cooperate in diffusion or flow-based image generation.
- [Ming-Image-0.1-Design Text-to-Image Model](ming-image-0-1-design.md) — inclusionAI 6B text-to-image model for UI, infographics, posters, and text-rich designs with RGBA transparent-background support under MIT.
- [Pruna Qwen-Image-2.1 Few-Step LoRA Adapters](pruna-qwen-image-2-1.md) — DMD-distilled 5-step and 8-step LoRA adapters for faster Qwen-Image-2.1 text-to-image and editing without CFG.
- [Qwen-Image-2.1 Text-to-Image and Editing Model](qwen-image-2-1.md) — Qwen 7B unified text-to-image and editing model with native RGBA, multi-reference editing, and diffusers support under Qwen Research License.
- [Qwen-Image-2.1 Text Encoder (Heretic)](qwen-image-2-1-text-encoder-heretic.md) — Refusal-ablated Qwen3-VL text encoder for Qwen-Image-2.1 with GGUF, FP8, and bf16 builds and ComfyUI setup.
- [Qwen-Image-2.1 Edit LoRAs (WarmBloodAban)](qwen-image-2-1-edit-loras.md) — Community edit-focused LoRA pair for anime character consistency and realistic character conversion on Qwen-Image-2.1.
- [Qwen-Image-2.1 GGUF Quantized Checkpoints (Abiray)](qwen-image-2-1-gguf-abiray.md) — Community GGUF quants of Qwen-Image-2.1 with size/VRAM options and ComfyUI setup via ComfyUI-GGUF.
- [Qwen-Image-2.1 GGUF Quantized Checkpoints (Leejet)](qwen-image-2-1-gguf-leejet.md) — Leejet GGUF quants of Qwen-Image-2.1 converted with stable-diffusion.cpp for sd.cpp and leejet ComfyUI-GGUF use.
- [Qwen-Image-2.1 GGUF Quantized Checkpoints (Unsloth)](qwen-image-2-1-gguf-unsloth.md) — Unsloth Dynamic 2.0 GGUF quants of the Qwen-Image-2.1 denoiser with VAE and Qwen3-VL encoder pairing and sd-cli use.
- [Qwen-Image-2.1 PE-I2I Rewriter (Heretic GGUF)](qwen-image-2-1-pe-i2i-heretic-gguf.md) — Community refusal-ablated GGUF packaging of the Qwen-Image-2.1 PE-I2I image-editing prompt rewriter with multimodal llama.cpp use and low-damage ablation point.
- [Qwen-Image-2.1 PE-T2I Rewriter (Heretic GGUF)](qwen-image-2-1-pe-t2i-heretic-gguf.md) — Community refusal-ablated GGUF packaging of the Qwen-Image-2.1 PE-T2I text-to-image prompt rewriter with a Q6_K embedding deviation and llama.cpp use.
- [Qwen-Image-2.1 Uncensored GGUF Checkpoints (Abenzerps)](qwen-image-2-1-uncensored-gguf-abenzerps.md) — Abenzerps GGUF and low-bit Qwen-Image-2.1 checkpoints with uncensored and base variants, encoder/VAE pairing, and ComfyUI-GGUF setup.
- [Qwen-Image-2.1 Viggle Turbo Few-Step LoRA](qwen-image-2-1-viggle-turbo.md) — Viggle distilled 6-step and 9-step LoRA plus merged quantized transformers for faster Qwen-Image-2.1 text-to-image and editing without CFG.
- [Qwen-Image-2.1-Fix LoRA Adapter](qwen-image-2-1-fix.md) — Community LoRA adapter reported to improve Qwen Image 2.1 generation consistency without replacing the base model.
- [Qwen-Image-2.1-Fun ControlNet-Union Branch](qwen-image-2-1-fun-controlnet-union.md) — Single-checkpoint ControlNet-Union branch for Qwen-Image 2.1 covering 8 structural controls plus inpainting via VideoX-Fun.
- [Qwen-Image-2512 GGUF Quantized Checkpoints (Unsloth)](qwen-image-2512-gguf-unsloth.md) — Unsloth Dynamic 2.0 GGUF quants of the Qwen-Image-2512 December text-to-image model with ComfyUI and stable-diffusion.cpp guides.
- [Qwen-Image-Edit-2511 Multiple-Angles LoRA](qwen-image-edit-2511-multiple-angles-lora.md) — Camera-control LoRA for Qwen-Image-Edit-2511 with 96 precise poses, <sks> trigger vocabulary, and Gaussian Splatting training provenance.
- [Qwen-Image-Edit Semantic and Appearance Control](qwen-image-edit-conditioning.md) — Contrasts classic noisy-latent img2img with Qwen-Image-Edit's reported Qwen2.5-VL semantic and VAE appearance conditioning.
- [Wulver Krea-2 Anthro Fine-Tune](wulver-krea-2.md) — Vaelico full fine-tune of Krea 2 Raw for anthro, furry, and anime/kemono generation with multi-character composition and 1,113 artist tokens, shipped as Turbo and Non-Turbo checkpoints under the Krea 2 Community License.
- [stable-diffusion.cpp Local Diffusion Inference](stable-diffusion-cpp.md) — ggml-based C/C++ engine for local SD, FLUX, Qwen-Image, Wan and related image/video model inference.
- [Z-Image Lookalike LoRA Collection (nphSi)](z-image-lookalike-loras.md) — Community lookalike LoRA collection for Z-Image and Z-Image-Turbo with vrtl trigger convention and Turbo preview settings.
- [Z-Image-Turbo GGUF Quantized Checkpoints (Unsloth)](z-image-turbo-gguf-unsloth.md) — Unsloth Dynamic 2.0 GGUF quants of the Z-Image-Turbo 6B single-stream DiT model with 8-NFE Turbo inference and diffusers use.
- [Z-Image-Turbo Text-to-Image Model](z-image-turbo.md) — Tongyi-MAI 6B single-stream DiT distilled checkpoint for 8-NFE text-to-image inference with bilingual rendering under Apache-2.0.
