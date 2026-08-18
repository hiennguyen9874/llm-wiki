---
license: mit
library_name: transformers
pipeline_tag: image-feature-extraction
tags:
- mage-vl
- vision-encoder
- codec-vit
- video-understanding
---

<h1 align="center">Mage-ViT<br><span style="font-size: 0.55em; font-weight: normal;">A Codec-Native Visual Encoder Trained from Scratch</span></h1>

<p align="center">
  <a href="https://microsoft.github.io/Mage"><img alt="Project Page" src="https://img.shields.io/badge/%F0%9F%8C%90-Project%20Page-blue" height="22" /></a>
  <a href="https://github.com/microsoft/Mage"><img src="https://img.shields.io/badge/Code-GitHub-181717?logo=github" alt="GitHub" height="22"></a>
  <a href="https://huggingface.co/microsoft/Mage-VL"><img alt="Mage-VL" src="https://img.shields.io/badge/%F0%9F%A4%97-Mage--VL-yellow" height="22" /></a>
  <a href="https://huggingface.co/microsoft/Mage-ViT"><img alt="Mage-ViT" src="https://img.shields.io/badge/%F0%9F%A4%97-Mage--ViT-yellow" height="22" /></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green" alt="License: MIT" height="22"></a>
</p>

---

**Mage-ViT** is the visual encoder at the core of **[Mage-VL](https://huggingface.co/microsoft/Mage-VL)**. It is a *Codec-ViT* built primarily for video, where a single image is simply the degenerate one-frame case. Mage-ViT follows a **codec-aligned sparsity** principle: visual tokens should be spent where a video codec spends bits, since codec bit-allocation is a natural proxy for spatio-temporal importance. On a shared `16×16` patch grid it keeps every anchor (I-frame) patch and only the motion-salient predicted (P-frame) patches, while a shared **3D rotary position encoding** preserves spatio-temporal structure even after large fractions of the grid are dropped.

This repository is the **ViT-pre-trained checkpoint only** — it has not gone through the joint VLM training with the language model. Use it as a data-efficient, codec-native visual encoder, or as a drop-in ViT for your own multimodal training.

## ✨ Highlights

- **Codec-driven patchifier.** Patches are selected by a per-patch importance map derived from the codec — motion vectors + P-frame residual energy for HEVC/H.265, or the learned rate map of the neural codec DCVC-RT. For a 64-frame clip it keeps all I-frame patches plus the top-*k* P-frame patches within a **4096-token budget (~75% token reduction)**. Chunk-wise and collage patchification are also supported.
- **Codec-agnostic.** The same interface accepts a traditional codec (HEVC/H.265) or a neural codec (DCVC-RT) with no architecture or retraining change.
- **Trained from scratch.** No billion-scale image-text ViT initialization — Mage-ViT is optimized with a large-scale **cluster-discrimination** objective on **~100M unlabeled images/videos**.

## 🏗️ Architecture

A **24-layer pre-norm Vision Transformer** trunk (hidden size `1024`, `16` attention heads, GELU MLP at 4× expansion) processes the variable-length token sequence produced by the codec-driven patchifier, followed by a multi-head attention pooling head. The standalone encoder in this repo consumes `pixel_values` (and optional `patch_positions`); codec-driven patch **selection** is applied upstream in the Mage-VL data pipeline.

Pre-training is a two-stage, from-scratch recipe in bf16: **(1)** variable-resolution image pre-training (224–448), then **(2)** joint image + video pre-training (video at resolution 256, 64 frames per clip, 4096-token budget).

## 📦 Installation

Mage-ViT follows the Mage-VL runtime:

```bash
pip install "transformers>=5.7" torch torchvision pillow
# optional, for the fastest GPU attention path:
# pip install flash-attn --no-build-isolation
```

Attention is dispatched internally to `sdpa` (default) → `flash_attention_2` → `eager`, so **flash-attn is optional** and the model runs on CPU or GPU out of the box.

## 🚀 Encoding an image

```python
import torch
from PIL import Image
from transformers import AutoModel, AutoImageProcessor

model = AutoModel.from_pretrained(
    "microsoft/Mage-ViT", trust_remote_code=True
).to("cuda").eval()
processor = AutoImageProcessor.from_pretrained(
    "microsoft/Mage-ViT", trust_remote_code=True
)

image = Image.open("your_image.jpg")
pixel_values = processor(images=image, return_tensors="pt")["pixel_values"].to("cuda")

with torch.no_grad():
    out = model(pixel_values)              # pixel_values: [B, 3, H, W]

patch_features = out.last_hidden_state     # [B, num_patches, 1024]
pooled_feature = out.pooler_output         # [B, 1024]
```

Pass `attn_implementation="flash_attention_2"` (or `"sdpa"` / `"eager"`) to `from_pretrained` to pick the attention backend.

## 🎞️ Encoding a video

Stack the preprocessed frames into `[B, C, T, H, W]` and pass a `patch_positions` tensor of shape `[B, T * tokens_per_frame, 3]` giving the `(t, h, w)` grid coordinate of every patch:

```python
import torch
from PIL import Image

PATCH = 16

def build_patch_positions(num_frames, target_frames, grid_h, grid_w, device="cuda"):
    # temporal index for each frame, spread across the target timeline
    t = torch.linspace(0, target_frames - 1, num_frames, device=device).long()
    t = t.repeat_interleave(grid_h * grid_w)                    # [T * H * W]
    h = torch.arange(grid_h, device=device).repeat_interleave(grid_w).repeat(num_frames)
    w = torch.arange(grid_w, device=device).repeat(grid_h).repeat(num_frames)
    return torch.stack([t, h, w], dim=-1).unsqueeze(0)          # [1, T*H*W, 3]

frames = [Image.open(f"frame_{i}.jpg") for i in range(16)]      # your sampled frames
pv = processor(images=frames, return_tensors="pt")["pixel_values"]   # [T, C, H, W]
video = pv.unsqueeze(0).permute(0, 2, 1, 3, 4).to("cuda")            # [1, C, T, H, W]

gh, gw = video.shape[-2] // PATCH, video.shape[-1] // PATCH
patch_positions = build_patch_positions(num_frames=16, target_frames=64,
                                        grid_h=gh, grid_w=gw)

with torch.no_grad():
    out = model(video, patch_positions=patch_positions)
```

## 📤 Outputs

| Field | Shape | Description |
| ----- | ----- | ----------- |
| `last_hidden_state` | `[B, num_patches, 1024]` | per-patch features after the final layer norm |
| `pooler_output`     | `[B, 1024]`              | global feature from the multi-head attention pooling head |

## 📋 Specifications

| | |
| --- | --- |
| Architecture | Codec-ViT (pre-norm ViT, SigLIP-style MLP) |
| Parameters | ~316M |
| Hidden size / MLP | 1024 / 4096 |
| Layers / heads | 24 / 16 |
| Patch size | 16 |
| Position encoding | shared 3D rotary (4:6:6 split over T:H:W) |
| Pooling | learned-probe multi-head attention head |
| Pre-training resolution | images 224–448 (variable), video 256 |
| Weights dtype | bfloat16 |
| License | MIT |

## 📄 License

Released under the [MIT License](https://opensource.org/licenses/MIT).
