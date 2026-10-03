---
license: other
license_name: qwen-research
base_model:
  - Qwen/Qwen-Image-2.1
base_model_relation: quantized
pipeline_tag: text-to-image
library_name: gguf
tags:
  - gguf
  - qwen
  - image-generation
  - comfyui
  - comfyui-gguf
---

# Qwen-Image-2.1 Uncensored GGUF

GGUF quantizations of [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1) for local image generation using the original upstream base weights.

## Benchmark

![Qwen-Image-2.1 benchmark](assets/Qwen-Image-2.1-Benchmark.png)

## Uncensored GGUF Files

| **Quantization** | **File** | **Size** |
| --- | --- | ---: |
| BF16 | [**qwen-image-2.1-UC-BF16.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-BF16.gguf) | 14.23 GB |
| FP8 | [**qwen-image-2.1-UC-fp8.safetensors**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-fp8.safetensors) | 6.63 GB |
| INT8 ConvRot | [**qwen-image-2.1-UC-int8_convrot.safetensors**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-int8_convrot.safetensors) | 6.76 GB |
| NVFP4 | [**qwen-image-2.1-UC-NVFP4.safetensors**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-NVFP4.safetensors) | 4.20 GB |
| MLX 4-bit | [**qwen-image-2.1-UC-MLX-4bit.safetensors**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-MLX-4bit.safetensors) | 4.00 GB |
| MLX 6-bit | [**qwen-image-2.1-UC-MLX-6bit.safetensors**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-MLX-6bit.safetensors) | 5.78 GB |
| MLX 8-bit | [**qwen-image-2.1-UC-MLX-8bit.safetensors**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-MLX-8bit.safetensors) | 7.56 GB |
| Q8_0 | [**qwen-image-2.1-UC-Q8_0.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-Q8_0.gguf) | 7.59 GB |
| Q6_K | [**qwen-image-2.1-UC-Q6_K.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-Q6_K.gguf) | 5.88 GB |
| Q5_K_M | [**qwen-image-2.1-UC-Q5_K_M.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-Q5_K_M.gguf) | 5.22 GB |
| Q4_K_M | [**qwen-image-2.1-UC-Q4_K_M.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-Q4_K_M.gguf) | 4.60 GB |
| Q4_0 | [**qwen-image-2.1-UC-Q4_0.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/qwen-image-2.1-UC-Q4_0.gguf) | 4.15 GB |

**Q4_K_M** is recommended for the best balance of size and quality.

## GGUF files

| **Quantization** | **File** | **Size** |
| --- | --- | ---: |
| Q8_0 | [**qwen-image-2.1-Q8_0.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/base/qwen-image-2.1-Q8_0.gguf) | 7.59 GB |
| Q6_K | [**qwen-image-2.1-Q6_K.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/base/qwen-image-2.1-Q6_K.gguf) | 5.88 GB |
| Q5_K_M | [**qwen-image-2.1-Q5_K_M.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/base/qwen-image-2.1-Q5_K_M.gguf) | 5.22 GB |
| Q4_K_M | [**qwen-image-2.1-Q4_K_M.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/base/qwen-image-2.1-Q4_K_M.gguf) | 4.60 GB |
| Q4_0 | [**qwen-image-2.1-Q4_0.gguf**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/base/qwen-image-2.1-Q4_0.gguf) | 4.05 GB |


## Text Encoders & VAE

Companion model files packaged for ComfyUI:

| **Type** | **File** | **Precision** | **Size** |
| --- | --- | --- | ---: |
| Text Encoder | [**text_encoders/qwen3vl_8b_bf16.safetensors**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/text_encoders/qwen3vl_8b_bf16.safetensors) | BF16 | 17.53 GB |
| Text Encoder | [**text_encoders/qwen3vl_8b_int8_convrot.safetensors**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/text_encoders/qwen3vl_8b_int8_convrot.safetensors) | Int8 | 9.35 GB |
| VAE | [**vae/qwen_image_2.1_vae_bf16.safetensors**](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-GGUF/blob/main/vae/qwen_image_2.1_vae_bf16.safetensors) | BF16 | 676 MB |

## Usage

Use the model with [ComfyUI](https://github.com/comfyanonymous/ComfyUI) and [ComfyUI-GGUF](https://github.com/leejet/ComfyUI-GGUF).

All required companion files (GGUF transformer, text encoder, and VAE) are hosted directly in this repository.

### 1. Download & File Placement

Download the files and place them in their respective ComfyUI directories:

```text
ComfyUI/
└── models/
    ├── diffusion_models/
    │   └── qwen-image-2.1-UC-Q4_K_M.gguf      # Choose one GGUF quantization (Q4_K_M recommended)
    ├── text_encoders/
    │   └── qwen3vl_8b_bf16.safetensors        # Or qwen3vl_8b_int8_convrot.safetensors (recommended for lower memory)
    └── vae/
        └── qwen_image_2.1_vae_bf16.safetensors
```

### 2. ComfyUI Setup

1. **Install ComfyUI-GGUF**: Use the maintained fork with native Qwen-Image 2.1 support by cloning [leejet/ComfyUI-GGUF](https://github.com/leejet/ComfyUI-GGUF) into your custom nodes:
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/leejet/ComfyUI-GGUF
   ```
   *(Note: If you have the older `city96/ComfyUI-GGUF` installed and encounter an `Unknown model architecture!` error, update to the `leejet` fork above or add `ModelQwenImage` to `tools/convert.py`).*
2. **Node Configuration**:
   - **Diffusion Model**: Add the **`Unet Loader (GGUF)`** node and select your downloaded `.gguf` file.
   - **Text Encoder**: Add the standard **`CLIPLoader`** node, select `qwen3vl_8b_bf16.safetensors` (or `int8`), and set **`type`** to **`qwen_image`**.
   - **VAE**: Add the standard **`VAELoader`** node and select `qwen_image_2.1_vae_bf16.safetensors`.
3. **Official Workflows**:
   - You can use the official Comfy-Org workflow templates: [Text-to-Image](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_t2i.json) or [Image Edit](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_image_edit.json).
   - In the workflow, simply replace the default `UNETLoader` node with **`Unet Loader (GGUF)`**.

### Memory & Performance Notes

- **Optimal Setup (GPU + RAM)**: Keep the **GGUF diffusion model in GPU VRAM** (where speed is crucial during sampling) and let the **text encoder run in / offload to System RAM (CPU)**. Because text encoding only runs once per prompt, this saves 9–17 GB of VRAM with virtually zero impact on generation speed.
- **Recommended Configuration**:
  - **Diffusion**: `qwen-image-2.1-UC-Q4_K_M.gguf` (~4.6 GB in VRAM)
  - **Text Encoder**: `qwen3vl_8b_int8_convrot.safetensors` (~9.35 GB in RAM)
- **Low VRAM Mode**: If you experience VRAM out-of-memory errors, start ComfyUI with the `--lowvram` argument.

## Uncensored

This GGUF release has no built-in safety checker or content filter. It generates adult, NSFW, and sensitive imagery directly without prompt refusals or blacked-out images. Output behavior depends solely on the input prompts and the environment in which the model is executed.

## Source and build

- **Source model:** [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1)
- **Text encoder & VAE source:** [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1)
- **Source revision:** `b3179ad355be050328e483a9dfdd9e60cd62adfa`
- **Conversion:** [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) commit `1330cebae8f2ba99249df846cc0c9444fcbd4308`
- **License:** Qwen Research License
- **Checksums:** [SHA256SUMS](./SHA256SUMS)
