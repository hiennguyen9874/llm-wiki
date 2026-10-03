---
language:
- en
- zh
base_model:
- Qwen/Qwen-Image-2.1
tags:
- gguf
- text-to-image
- stable-diffusion.cpp
---

# Qwen-Image-2.1 GGUF quantized files

The license of the quantized files follows the license of the original model:
 - Qwen RESEARCH LICENSE AGREEMENT: https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE

These files are converted using https://github.com/leejet/stable-diffusion.cpp

## Usage

### stable-diffusion.cpp

This model can be used with [`stable-diffusion.cpp`](https://github.com/leejet/stable-diffusion.cpp).

For setup instructions and usage details, please refer to:

[Qwen-Image-2.1 Documentation](https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/qwen_image_2.1.md)

### ComfyUI

To use this model in **ComfyUI**, first install the following custom node:

[leejet/ComfyUI-GGUF](https://github.com/leejet/ComfyUI-GGUF)

> [!IMPORTANT]
> Please use the **leejet** version of `ComfyUI-GGUF`, rather than the version maintained by `city96`.
> The `city96` repository appears to no longer be actively maintained.

#### Example Workflow

An example ComfyUI workflow is available here:

[`qwen_image_2_1_t2i_gguf.json`](qwen_image_2_1_t2i_gguf.json)

#### Example Output

<img width=200 height=200 alt="Qwen Image 2.1 example" src="https://huggingface.co/leejet/Qwen-Image-2.1-GGUF/resolve/main/Qwen_image_2.1_t2i.png" />