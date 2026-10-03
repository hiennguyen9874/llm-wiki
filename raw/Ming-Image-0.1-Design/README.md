---
license: mit
library_name: custom
pipeline_tag: text-to-image
inference: false
tags:
  - text-to-image
  - image-generation
  - graphic-design
  - text-rendering
  - rgba
---

# Ming-Image-0.1-Design

[🧩 ModelScope](https://www.modelscope.cn/models/inclusionAI/Ming-Image-0.1-Design) · [🤗 Hugging Face](https://huggingface.co/inclusionAI/Ming-Image-0.1-Design) · [📄 Blog](https://mp.weixin.qq.com/s/VGdtxfM8kbHIQJw50VD_Sw) · [🖥️ Demo](https://huggingface.co/spaces/hugging-apps/ming-image-0-1-design-demo)<br>
[🎨 Design Skill](https://github.com/inclusionAI/ling-cookbook/tree/main/resources/recommended-skills/ling-ui-design) · [📊 PPT Skill](https://github.com/inclusionAI/ling-cookbook/tree/main/resources/recommended-skills/image-to-editable-ppt)

Ming-Image-0.1-Design is a 6B text-to-image model for UI, infographics,
posters, and other text-rich visual designs. It generates complete visual
compositions and supports RGBA output with transparent backgrounds.

## UI/UX Design leaderboard

<p align="center">
  <img src="./assets/uiux_leaderboard.webp" width="100%" alt="Ming-Image-0.1-Design UI/UX Design leaderboard">
</p>

## Quick Start

Use the companion [Ming-Image repository](https://github.com/inclusionAI/Ming-Image)
for installation and inference:

```bash
git clone https://github.com/inclusionAI/Ming-Image
cd Ming-Image
pip install -r requirements.txt

python infer.py \
  --model inclusionAI/Ming-Image-0.1-Design \
  --task text-to-image \
  --prompt assets/t2i_four_seasons_cabin_prompt.json \
  --resolution 2048 \
  --output-dir outputs/t2i
```

Prompt enhancement (PE) can use `Ling-3.0-flash-VL` or `qwen3.8-27B`; see
[text-to-image prompt rewriting](https://github.com/inclusionAI/Ming-Image#text-to-image-prompt-rewriting).

### Transparent-background generation

For transparent-background generation, prepend exactly one of the recommended
RGBA phrases. See the
[transparent-background generation tip](https://github.com/inclusionAI/Ming-Image#transparent-background-generation-tip).

## Deployment

We recommend the following inference frameworks to serve the model:

- vLLM-Omni: see the [recipes](https://github.com/vllm-project/vllm-omni/blob/main/recipes/inclusionAI/Ming-Image.md)
  and [installation guide](https://docs.vllm.ai/projects/vllm-omni/en/latest/getting_started/quickstart/).

## Recommended settings

- Resolution: **2048 x 2048** (recommended), or **1024 x 1024** for faster
  generation.
- Sampling steps: **12**.
- CFG scale: **1.0**.
- Precision: **BF16**.
- Hardware: **one CUDA GPU with 80 GiB VRAM** (validated configuration).

The public inference code maps text-to-image resolution requests to the
supported 1024 or 2048 bucket.

## Gallery

### Text-to-image

<p align="center">
  <img src="./assets/showcase.webp" width="100%" alt="Ming-Image-0.1-Design generated examples">
</p>

### Transparent-background text-to-image

<p align="center">
  <img src="./assets/transparency_showcase.webp" width="100%" alt="Ming-Image-0.1-Design transparent-background examples">
</p>

The checkerboard is used only to preview transparency; it is not part of the
generated RGBA images.

## License

This model is released under the [MIT License](./LICENSE).
