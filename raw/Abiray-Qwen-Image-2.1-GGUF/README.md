---
license: other
license_name: qwen-research
license_link: https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE
base_model: Qwen/Qwen-Image-2.1
tags:
  - text-to-image
  - image-to-image
  - gguf
  - comfyui
  - image-generation
  - quantized
widget:
- output:
    url: images/Qwen_image_2.1_00003.png
  text: '-'
- output:
    url: images/Qwen_image_2.1_00005.png
  text: '-'
- output:
    url: images/Qwen_image_2.1_00006.png
  text: '-'
- output:
    url: images/Qwen_image_2.1_00007.png
  text: '-'
---

# Qwen-Image-2.1 GGUF Quants

This repository provides quantized **GGUF** checkpoints for [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1), optimized for low-VRAM inference in **ComfyUI** using the [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) custom node.

Quantizing the diffusion transformer drastically reduces memory pressure during generation while preserving sharp detail, composition, and prompt alignment.

---

## 📦 Quantization Breakdown & File Details

| Filename | Quant Type | Size | Recommended VRAM / Profile |
| :--- | :---: | :---: | :--- |
| `qwen_image_2.1_Q8_0.gguf` | **Q8_0** | **7.59 GB** | 12 GB+ (Near-lossless fidelity) |
| `qwen_image_2.1_Q6_K.gguf` | **Q6_K** | **5.88 GB** | 10–12 GB (High quality sweet spot) |
| `qwen_image_2.1_Q5_K_M.gguf` | **Q5_K_M** | **5.01 GB** | 8–10 GB (Balanced performance & memory) |
| `qwen_image_2.1_Q4_K_M.gguf` | **Q4_K_M** | **4.19 GB** | 6–8 GB (Standard consumer GPU baseline) |
| `qwen_image_2.1_Q4_K_S.gguf` | **Q4_K_S** | **4.06 GB** | 6–8 GB (Compact 4-bit) |
| `qwen_image_2.1_Q3_K_M.gguf` | **Q3_K_M** | **3.19 GB** | 4–6 GB (Extreme budget / minimum VRAM) |

---
## 🖼️ Sample Generations (Q4_K_M)
<Gallery />

---
## 🧩 Required Components (Text Encoders & VAE)

To run these models in ComfyUI, you will need the matching text encoders and VAE:

1. **Text Encoders:**
   * Download from: [Comfy-Org/Qwen-Image-2.1 Text Encoders](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/tree/main/text_encoders)
   * Place files into: `ComfyUI/models/clip/` (or `ComfyUI/models/text_encoders/`)

2. **VAE:**
   * Download from: [Comfy-Org/Qwen-Image-2.1 VAE](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/tree/main/vae)
   * Place files into: `ComfyUI/models/vae/`

3. **Diffusion Model (This Repo):**
   * Download your preferred `.gguf` file from above.
   * Place into: `ComfyUI/models/diffusion_models/` (or `ComfyUI/models/unet/`)

---

## 🎨 Included Ready-to-Use Workflows

Both Text-to-Image and Image-to-Image editing workflows are packaged in this repo:

* **Text-to-Image:** [Qwen_Image_2.1_GGUF_Text2Image.json](https://huggingface.co/Abiray/Qwen-Image-2.1-GGUF/blob/main/Qwen_Image_2.1_GGUF_Text2Image.json)
* **Image-to-Image / Editing:** [Qwen_Image_2.1_GGUF_Image2Image_Edit.json](https://huggingface.co/Abiray/Qwen-Image-2.1-GGUF/blob/main/Qwen_Image_2.1_GGUF_Image2Image_Edit.json)

### How to Use:
1. Ensure you have installed **[ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF)** (search for `ComfyUI-GGUF` inside the ComfyUI Manager).
2. Drag and drop either of the `.json` workflow files into your ComfyUI workspace.
3. In the **Unet Loader (GGUF)** node, select the downloaded `.gguf` file.
4. Verify your CLIP/Text Encoder and VAE node loaders point to the files downloaded above.
5. Queue prompt and generate!

---

## 👏 Acknowledgments & Credits

* Base model developed by the **Qwen Team / Alibaba Cloud**: [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1).
* ComfyUI integration assets and pipeline weights provided by [Comfy-Org](https://huggingface.co/Comfy-Org/Qwen-Image-2.1).
* GGUF quantization powered by [llama.cpp](https://github.com/ggerganov/llama.cpp) and [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF).