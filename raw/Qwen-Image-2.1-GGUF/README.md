---
base_model: Qwen/Qwen-Image-2.1
base_model_relation: quantized
license: other
license_name: qwen-research
license_link: https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE
language:
- en
- zh
pipeline_tag: text-to-image
tags:
- gguf
- quantized
- unsloth
- qwen
- image-generation
widget:
- text: Photorealistic editorial photograph of a woman barista making a latte in a modern, minimalist café on a sunny tropical morning. 
  output:
    url: assets/cafe.png
- text:  A lone astronaut crossing a dark, frozen lake beneath enormous rings stretching across an alien sky. Fine cracks visible under the translucent ice, distant mountains, soft blue twilight, cinematic scale, photorealistic detail.
  output:
    url: assets/spaces.png
---
# Read our How to [Run Qwen-Image-2.1 Guide!](https://unsloth.ai/docs/models/qwen-image-2.1) 💜 

This is a GGUF quantized version of [Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1). <br>
unsloth/Qwen-Image-2.1-GGUF uses [Unsloth Dynamic 2.0](https://docs.unsloth.ai/basics/unsloth-dynamic-2.0-ggufs) methodology for SOTA performance.

- Important layers are upcasted to higher precision, per tensor, from a measured sensitivity scan.
- Run these with [Unsloth Desktop](https://github.com/unslothai/unsloth), stable-diffusion.cpp and more. A GGUF is the denoiser only, so it needs the VAE and the Qwen3-VL text encoder alongside it.
- VAE: [unsloth/Qwen-Image-2.1-FP8](https://huggingface.co/unsloth/Qwen-Image-2.1-FP8) `vae/qwen_image_2.1_vae_bf16.safetensors`. Text encoder: [unsloth/Qwen3-VL-8B-Instruct-GGUF](https://huggingface.co/unsloth/Qwen3-VL-8B-Instruct-GGUF) `Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf`, the Dynamic 2.0 4-bit rung rather than the uniform `Q4_K_M`. Measured against the `Q4_K_M` encoder at a shared seed, with the denoiser and VAE held fixed: LPIPS 0.029, SSIM 0.959, 5.15 GB vs 5.03 GB, 36.5 s vs 39.0 s.
<div>
  <div style="display: flex; gap: 5px; align-items: center; ">
    <a href="https://github.com/unslothai/unsloth/">
      <img src="https://github.com/unslothai/unsloth/raw/main/images/unsloth%20new%20logo.png" width="133">
    </a>
    <a href="https://discord.gg/unsloth">
      <img src="https://github.com/unslothai/unsloth/raw/main/images/Discord%20button.png" width="173">
    </a>
    <a href="https://unsloth.ai/docs/models/qwen-image-2.1">
      <img src="https://raw.githubusercontent.com/unslothai/unsloth/refs/heads/main/images/documentation%20green%20button.png" width="143">
    </a>
  </div>
</div>
See below for image editing operating inside of Unsloth Desktop:
<img width="600" alt="qwen-image-2.1 unsloth desktop" src="https://unsloth.ai/docs/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252F8E4zaQZmeYBhYIXkvveM%252F01-2edit-multi-image.webp%3Falt%3Dmedia%26token%3Dad7d102c-b304-4c75-b66d-4a68cd518a37&width=768&dpr=3&quality=100&sign=a5a37f593c66ddc27c847bab0d138eda&sv=3" />


```bash
sd-cli --diffusion-model qwen-image-2.1-Q4_K_M.gguf \
  --vae qwen_image_2.1_vae_bf16.safetensors \
  --llm Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf \
  -p "a cartoon sloth mascot waving, flat vector illustration, bright colours" \
  --steps 20 --cfg-scale 6.0 --sampling-method euler -W 1024 -H 1024 --diffusion-fa \
  -o out.png
```

### Samples

Rendered with the Q4_K_M denoiser and the Q4_K_M text encoder, 1024x1024, 20 steps, cfg 6.0, euler.

<table>
  <tr>
    <td><img src="assets/cafe.png" width="200"></td>
    <td><img src="assets/spaces.png" width="200"></td>
  </tr>
  <tr>
    <td><img src="assets/cinema.png" width="200"></td>
    <td><img src="assets/cardesert.png" width="200"></td>
  </tr>
</table>

---

<p align="center">
    <img src="https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-Image/image2.1/logo.png" width="400"/>
</p>
<p align="center">
    🤖 <a href="https://modelscope.cn/models/Qwen/Qwen-Image-2.1">ModelScope</a>&nbsp;&nbsp;|
    &nbsp;&nbsp;🤗 <a href="https://huggingface.co/Qwen/Qwen-Image-2.1">HuggingFace</a>&nbsp;&nbsp;|
    &nbsp;&nbsp;📑 <a href="https://qwen.ai/blog?id=qwen-image-2.1">Blog</a>&nbsp;&nbsp;|
    &nbsp;&nbsp;🖥️ <a href="https://huggingface.co/spaces/Qwen/Qwen-Image-2.1">Demo</a>&nbsp;&nbsp;|
    &nbsp;&nbsp;🫨 <a href="https://discord.gg/BEYSk3pkSu">Discord</a>&nbsp;&nbsp;|
    &nbsp;&nbsp;💬 <a href="https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/assets/qr.png">WeChat</a>
</p>

## Introduction

We are excited to open-source **Qwen-Image-2.1**, a unified text-to-image generation and image editing model in the Qwen family. With just **7B parameters in its visual generation component** (32 Single-Stream DiT layers), Qwen-Image-2.1 balances generation quality, inference efficiency, and versatility.

Four key improvements define this release:

- **Compact and Efficient**: a lightweight architecture with mixed-granularity attention and prefix KV cache reuse delivers strong image quality at low computational cost.
- **Native Transparency, Unified Creation and Editing**: generate regular or transparent (RGBA) images from text, edit transparent layers, and extract subjects from photographs, all in one model.
- **Versatile Editing**: support up to **10 reference images**, specify local edits via circles, painted annotations, or separate masks, and preserve identity for people and products.
- **Realistic Textures and Refined Aesthetics**: improved typography, portrait lighting, and fine details for more visually compelling results.

<p align="center">
    <img src="https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen-Image/image2.1/images/example-01.png" width="100%"/>
</p>

For more details, see the [GitHub repo](https://github.com/QwenLM/Qwen-Image-2.1) and [Blog](https://qwen.ai/blog?id=qwen-image-2.1).

## Quick Start

### Installation

```bash
pip install torch>=2.4.0
pip install transformers>=5.17
pip install git+https://github.com/huggingface/diffusers
pip install accelerate pillow
```

### Text-to-Image

```python
import torch
from diffusers import QwenImage21Pipeline

pipe = QwenImage21Pipeline.from_pretrained(
    "Qwen/Qwen-Image-2.1", torch_dtype=torch.bfloat16
).to("cuda")

image = pipe(
    prompt="A neon shop sign that reads \"QWEN IMAGE 2.1\", rainy night, reflections on wet pavement",
    width=2048, height=2048,
    num_inference_steps=40,
    generator=torch.Generator("cuda").manual_seed(42),
).images[0]

image.save("t2i_example.png")
```

### Image Editing

```python
import torch
from PIL import Image
from diffusers import QwenImage21Pipeline

pipe = QwenImage21Pipeline.from_pretrained(
    "Qwen/Qwen-Image-2.1", torch_dtype=torch.bfloat16
).to("cuda")

input_image = Image.open("input.png")

image = pipe(
    prompt="Change the background to a sunset beach",
    image=input_image,
    num_inference_steps=40,
    generator=torch.Generator("cuda").manual_seed(42),
).images[0]

image.save("edit_example.png")
```

### Transparent Image Generation (RGBA)

Use the recommended prompt format for transparent images:

```python
image = pipe(
    prompt="This is an RGBA image with transparency. A cute cartoon dragon sticker. The image has alpha channel and the background is transparent.",
    width=2048, height=2048,
    num_inference_steps=40,
    generator=torch.Generator("cuda").manual_seed(42),
).images[0]

image.save("transparent_example.png")
```

### Supported Aspect Ratios

```python
aspect_ratios = {
    "1:1":  (2048, 2048),
    "4:3":  (2400, 1792),
    "3:4":  (1792, 2400),
    "3:2":  (2528, 1696),
    "2:3":  (1696, 2528),
    "16:9": (2752, 1536),
    "9:16": (1536, 2752),
}
```

### Memory Optimization

```python
pipe = QwenImage21Pipeline.from_pretrained(
    "Qwen/Qwen-Image-2.1", torch_dtype=torch.bfloat16
)
pipe.enable_model_cpu_offload()
```

## Showcase

<p align="center">
<img src="https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen-Image/image2.1/images/example-04.png" width="30%"/>
<img src="https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen-Image/image2.1/images/example-05.png" width="30%"/>
<img src="https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen-Image/image2.1/images/example-06.png" width="30%"/>
</p>
<p align="center"><em>Native transparent image generation</em></p>

<p align="center">
<img src="https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen-Image/image2.1/images/example-15.png" width="100%"/>
</p>
<p align="center"><em>Group photograph generated from six portrait references</em></p>

<p align="center">
<img src="https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen-Image/image2.1/images/example-43.png" width="48%"/>
<img src="https://qianwen-res.oss-accelerate.aliyuncs.com/Qwen-Image/image2.1/images/example-44.png" width="48%"/>
</p>
<p align="center"><em>Text rendering</em></p>

## License

This model is licensed under the [Qwen Research License Agreement](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE).
