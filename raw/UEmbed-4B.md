---
license: cc-by-4.0
pipeline_tag: feature-extraction
library_name: transformers
tags:
- embeddings
- multimodal
- retrieval
- sparse-retrieval
- splade
- dense-retrieval
- vision
---

<h1 align="center">UEmbed: Unified Sparse and Dense Multimodal Embeddings</h1>

<p align="center">
  <a href="https://alibaba-nlp.github.io/UEmbed"><img src="https://img.shields.io/badge/Website-UEmbed-green.svg" alt="Website"></a>
  <a href="https://arxiv.org/abs/2608.02583"><img src="https://img.shields.io/badge/arXiv-UEmbed-b31b1b.svg" alt="arXiv"></a>
  <a href="https://github.com/Alibaba-NLP/UEmbed"><img src="https://img.shields.io/badge/GitHub-UEmbed-black.svg" alt="GitHub"></a>
  <img src="https://img.shields.io/badge/License-CC--BY--4.0-blue.svg" alt="License: CC-BY-4.0">
</p>

UEmbed is a decoder-only multimodal embedding model that produces both **dense embeddings** and **SPLADE-style sparse lexical embeddings** from a single causal forward pass. It supports text, image, video, and mixed-modal inputs for retrieval, multimodal search, and visual-document retrieval.

## News 🔥

- **[2026-08-15]**: UEmbed achieves state-of-the-art results on the text and agent tracks of MMEB-v3, and ranks second only to the Qwen3-VL-Embedding series among open-source models on MMEB-v2.
- **[2026-08-13]**: We updated the inference code — UEmbed now loads natively with `transformers` (no `trust_remote_code` or processor patching needed), and we added a vLLM backend for high-throughput dense and sparse embedding inference. See the runnable examples: [`examples/transformers_example.py`](./examples/transformers_example.py) and [`examples/vllm_example.py`](./examples/vllm_example.py).

## Model Family

| Model | Backbone | Parameters | Outputs | Modalities |
|---|---:|---:|---|---|
| [UEmbed-2B](https://huggingface.co/Alibaba-NLP/UEmbed-2B) | Qwen3.5 | 2B | Dense + Sparse | Text, image, video |
| [UEmbed-4B](https://huggingface.co/Alibaba-NLP/UEmbed-4B) | Qwen3.5 | 4B | Dense + Sparse | Text, image, video |
| [UEmbed-9B](https://huggingface.co/Alibaba-NLP/UEmbed-9B) | Qwen3.5 | 9B | Dense + Sparse | Text, image, video |

## Highlights

- **Unified dense and sparse retrieval**: one checkpoint returns normalized dense vectors and sparse lexical vectors.
- **Multimodal inputs**: text, images, videos, and mixed inputs are represented in the same retrieval space.
- **Sparse interpretability**: sparse activations correspond to vocabulary terms and can be used with inverted indexes.
- **Causal-model serving compatibility**: the sparse design keeps the decoder-only backbone, no conversion to a bidirectional encoder.

## Architecture

| Component | Design |
|---|---|
| Backbone | Decoder-only Qwen3.5 multimodal model |
| Dense pooling | Hidden state of the EOS token before sparse special tokens |
| Sparse tokens | `N=16` appended special tokens |
| Sparse heads | One subset-specific linear head per special token |
| Sparse vocabulary | Compressed from 248,320 tokenizer entries to 184,016 canonical entries |
| Sparse activation | `log(1 + ReLU(logits))` |
| Training objective | Dense InfoNCE + sparse InfoNCE + query/document FLOPS regularization |

## Usage

Requires a recent `transformers` build with Qwen3.5/Qwen3-VL support:

```bash
pip install "transformers>=5.4.0" torch qwen-vl-utils tokenizers huggingface-hub pillow numpy
```

Download the complete model repository, since sparse inference requires both `sparse_info.json` and `sparse_weights.pt` in the local model directory:

```bash
huggingface-cli download Alibaba-NLP/UEmbed-2B --local-dir ./models/UEmbed-2B
```

Inference code is provided in the [GitHub repository](https://github.com/Alibaba-NLP/UEmbed). Set `pooling="last.normal"` for dense embeddings or `pooling="splade.last"` for sparse embeddings.

```python
import torch
from src.models.qwen35_embedding import Qwen35Embedder

model = Qwen35Embedder(
    model_name_or_path="./models/UEmbed-2B",
    torch_dtype=torch.bfloat16,
    # flash_attention_2 for better acceleration and memory saving
    attn_implementation="flash_attention_2",
)

inputs = [{
    "text": "A woman playing with her dog on a beach at sunset.",
    "instruction": "Retrieve images or text relevant to the user's query.",
}, {
    "text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust."
}, {
    "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"
}, {
    "text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust.",
    "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"
}]

embeddings = model.process(inputs)
print(embeddings @ embeddings.T)
```

### Input Format

`Qwen35Embedder.process` accepts a list of dictionaries with the following fields:

| Field | Type | Description |
|---|---|---|
| `text` | `str` or `list[str]` | Text content. |
| `image` | path, URL, `PIL.Image`, or list | One or more images. |
| `video` | path, URL, frame list, or list | One or more videos. |
| `instruction` | `str` | Optional task-specific instruction. |
| `fps` | `float` | Optional frame sampling rate for video files. |
| `max_frames` | `int` | Optional maximum number of sampled video frames. |

## Training Data

UEmbed is trained on **3.94M** public samples:

- E5 training data for broad text retrieval coverage.
- M3 training data, using the MLDR subset.
- MMEB training sets for multimodal query-document pairs.

For multimodal data, hard negatives are mined with Qwen3-VL-Embedding-8B as the teacher retriever.

## Citation

If you use UEmbed, please cite the paper:

```bibtex
@misc{uembed2026,
      title={UEmbed: Unified Sparse and Dense Multimodal Embeddings}, 
      author={Tingyu Song and Mingxin Li and Yanzhao Zhang and Dingkun Long and Pengjun Xie and Zhijie Nie and Yilun Zhao and Shu Wu},
      year={2026},
      eprint={2608.02583},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2608.02583}, 
}
```


## Acknowledgements

Thanks to the [Qwen3-VL-Embedding](https://github.com/QwenLM/Qwen3-VL-Embedding) repo for the evaluation framework.