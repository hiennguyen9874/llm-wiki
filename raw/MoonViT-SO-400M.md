---
license: mit
pipeline_tag: image-feature-extraction
library_name: transformers
---

<div align="center">
  <img width="30%" src="figures/logo.png">
</div>


## Introduction

**MoonViT** is a Native-resolution Vision Encoder, which is initialized from and continually pre-trained on **SigLIP-SO-400M**.
To facilitate the standalone use of MoonViT, we have separated the implementation and weights of MoonViT from [moonshotai/Kimi-VL-A3B-Instruct](https://huggingface.co/moonshotai/Kimi-VL-A3B-Instruct).

If you are interested in the training process of MoonViT, you are welcome to read Paper [Kimi-VL Technical Report](https://huggingface.co/papers/2504.07491).

## Example usage

```python
from PIL import Image
from transformers import AutoModel, AutoImageProcessor

model_path = "moonshotai/MoonViT-SO-400M"
model = AutoModel.from_pretrained(
    model_path,
    torch_dtype="auto",
    device_map="auto",
    trust_remote_code=True,
)
processor = AutoImageProcessor.from_pretrained(model_path, trust_remote_code=True)

image_path = "./figures/demo.png"
image = Image.open(image_path)

images_processed = processor(image, return_tensors="pt").to(dtype=model.dtype, device=model.device)
image_features: list = model(images_processed.pixel_values, images_processed.image_grid_hws)

print(f"dtype: {image_features[0].dtype}, shape: {image_features[0].shape}")
# dtype: torch.bfloat16, shape: torch.Size([1092, 4, 1152])
```