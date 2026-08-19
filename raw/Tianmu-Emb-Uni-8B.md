---
license: apache-2.0
language:
  - zh
  - en
tags:
  - multimodal
  - embedding
  - retrieval
  - audio
  - video
  - image
  - text
  - visdoc
  - qwen3-vl
  - mmeb-v3
pipeline_tag: feature-extraction
library_name: transformers
base_model:
  - Qwen/Qwen3-VL-Embedding-8B
  - Qwen/Qwen2.5-Omni-7B
---

# Tianmu-Emb-Uni-8B

**Tianmu-Emb-Uni-8B** is a unified multimodal embedding model for general-purpose retrieval and representation learning. 

The name means **Tianmu Unified Multimodal Embedding 8B**. 

"Tianmu" is the model family name, "Emb" denotes embedding-based representation learning, "Uni" indicates unified cross-modal encoding, and "8B" refers to the model scale.

![image](https://cdn-uploads.huggingface.co/production/uploads/6846a5eaec85046a456c20bc/qKlQ8TqDiuF4wCLw8OhG_.png)


## Model Details

- **Model name:** Tianmu-Emb-Uni-8B
- **Repository:** https://huggingface.co/TianmuLab/Tianmu-Emb-Uni/tree/main
- **Model type:** unified multimodal embedding model
- **Embedding dimension:** 3584
- **Base vision-language embedding model:** Qwen3-VL-Embedding-8B
- **Base audio model:** Qwen2.5-Omni-7B audio tower
- **Released checkpoint stage:** `stage1b_adapter_proto_retrieval`
- **Released weights:** trained audio-side modules, connector, projection, adapter, and prototype modules
- **Full base model weights included:** no
- **Native `AutoModel.from_pretrained` support:** no

## Model Architecture

Tianmu-Emb-Uni-8B is built on Qwen3-VL embedding backbone and an audio branch initialized from Qwen2.5-Omni. The audio branch is connected to the Qwen3-VL embedding space through trainable connector, projection, adapter, and prototype modules.


## Intended Use

Tianmu-Emb-Uni-8B is intended for research and evaluation of unified multimodal embedding models, especially retrieval and representation tasks involving multiple modalities.

Typical use cases include:

- text-to-image retrieval
- image-to-text retrieval
- text-to-video retrieval
- audio-to-text retrieval
- audio classification and audio retrieval
- visual document retrieval
- multimodal RAG retrieval backbones
- cross-modal candidate recall and semantic matching

## Evaluation

Tianmu-Emb-Uni-8B was evaluated on **MMEB-V3**, following the 190-task setting described in the MMEB-V3 paper. The image task group includes **MCMR**, resulting in 37 image tasks and 190 total tasks.

| Modality | Tasks | Primary Metric | Score |
|---|---:|---|---:|
| Image | 37 | hit@1 | 73.83 |
| Video | 18 | hit@1 | 59.37 |
| Visual Document | 24 | ndcg_linear@5 | 72.03 |
| Audio | 11 | hit@1 | 38.94 |
| Text | 53 | ndcg_linear@5 | 43.62 |
| Agent | 47 | hit@1 | 39.42 |
| **All** | **190** | mixed primary metrics | **53.27** |

The code used to evaluate the `stage1b_adapter_proto_retrieval` checkpoint is shown below:

```bash
bash code/scripts/run_omni_stage1b_adapter_proto_retrieval.sh
```

## Files

```text
model.safetensors
model.safetensors.index.json
config.json
weights/final_audio_weights.pt
tianmu_model/
processors/
eval/mmeb_v3_eval/
requirements.txt
examples/load_weights.py
```

`model.safetensors` is converted from `weights/final_audio_weights.pt` and contains the same final state dict in Hugging Face's safer tensor format. The `.pt` checkpoint is kept for compatibility with the original training and evaluation scripts.

## Loading

This package uses lightweight project-specific model code instead of a native `transformers.AutoModel.from_pretrained` implementation. Users should prepare the base Qwen3-VL-Embedding-8B and Qwen2.5-Omni-7B models separately, then load the Tianmu adapter/audio-side weights.

A minimal loading example is provided at:

```text
examples/load_weights.py
```

Example:

```python
from pathlib import Path
import sys

from safetensors.torch import load_file

repo_dir = Path("/path/to/Tianmu-Emb-Uni")
sys.path.insert(0, str(repo_dir))

from tianmu_model.modeling import OmniEmbedModel

model = OmniEmbedModel(
    audio_encoder_type="omni",
    audio_model_path="/path/to/Qwen2.5-Omni-7B",
    vl_model_name="/path/to/Qwen3-VL-Embedding-8B",
    freeze_vl=True,
    freeze_audio_encoder=True,
)

state_dict = load_file(str(repo_dir / "model.safetensors"), device="cpu")
missing, unexpected = model.load_state_dict(state_dict, strict=False)
model.eval()
```

## Limitations

- This release does not contain the full Qwen3-VL-Embedding-8B or Qwen2.5-Omni-7B base weights.
- This release does not provide a fully integrated `AutoModel.from_pretrained` interface.
- The model is primarily released for research and evaluation of multimodal embeddings.
- Performance may vary across domains outside the MMEB-V3 evaluation distribution.
- Open-ended audio retrieval remains more challenging than audio classification in the current checkpoint.

## Third-Party Components

This project builds on external open-source model ecosystems, including Qwen3-VL-Embedding and Qwen2.5-Omni, together with common libraries such as PyTorch, Transformers, safetensors, NumPy, librosa, soundfile, and Pillow.

Users should comply with the licenses and usage terms of the corresponding base models and dependencies.

## License

The released Tianmu adapter/audio-side code and weights in this repository are provided under the Apache-2.0 license unless otherwise specified. Third-party base models and dependencies are governed by their respective licenses.
