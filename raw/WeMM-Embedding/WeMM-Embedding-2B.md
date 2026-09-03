---
library_name: transformers
license: other
license_name: apache-2.0
license_link: https://huggingface.co/tencent/WeMM-Embedding-2B/blob/main/LICENSE

base_model:
- Qwen/Qwen3.5-2B
pipeline_tag: feature-extraction

tags:
- sentence-transformers
- multimodal-embedding
- text-embedding
- image-embedding
- video-embedding
- mrl

language:
- zh
- en
---

# WeMM-Embedding-2B

[![Hugging Face](https://img.shields.io/badge/🤗-Hugging%20Face-yellow)](https://huggingface.co/collections/tencent/wemm-embedding)
[![Technical Report](https://img.shields.io/badge/📄-Technical%20Report-red)](https://arxiv.org/abs/2608.24053)
[![GitHub](https://img.shields.io/badge/GitHub-WeMM--Embedding-black?logo=github)](https://github.com/Tencent/WeMM-Embedding)

WeMM-Embedding-2B is a universal multimodal embedding model built on Qwen3.5. It accepts text, images, videos, visual documents, and interleaved multimodal inputs, and returns a 2,048-dimensional L2-normalized embedding. Audio input is not supported.

## Installation

```bash
pip install torch transformers==5.2.0 "qwen-vl-utils[decord]==0.0.14" \
  "sentence-transformers>=5.7.0" "accelerate>=1.1.0"
```

## Transformers

```python
import torch
from qwen_vl_utils import process_vision_info
from transformers import AutoModel, AutoProcessor

model_id = "tencent/WeMM-Embedding-2B"
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_id, trust_remote_code=True, dtype=torch.bfloat16
).cuda().eval()

messages = [{"role": "user", "content": [
    {"type": "image", "image": "/path/to/image.jpg"},
    {"type": "video", "video": "/path/to/video.mp4"},
    {"type": "text", "text": "This can be any text input."},
]}]
text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=False
)
images, videos, video_kwargs = process_vision_info(
    messages,
    image_patch_size=16,
    return_video_kwargs=True,
    return_video_metadata=True,
)
if videos is not None:
    videos, video_metadata = zip(*videos)
    videos, video_metadata = list(videos), list(video_metadata)
else:
    video_metadata = None
inputs = processor(
    text=text,
    images=images,
    videos=videos,
    video_metadata=video_metadata,
    return_tensors="pt",
    **video_kwargs,
).to("cuda")

with torch.inference_mode():
    embedding = model.embedding(**inputs)
```

Use any subset of the content items to encode text, image, or video independently.

## Sentence Transformers

```python
from sentence_transformers import SentenceTransformer

model_id = "tencent/WeMM-Embedding-2B"
model = SentenceTransformer(model_id, trust_remote_code=True)

queries = [
    "Which Llama 4 model variants are available?",
    "How is mapo tofu prepared?",
]
documents = [
    "Mapo tofu is a Sichuan dish of soft tofu simmered in a spicy, numbing sauce of chili bean paste and Sichuan peppercorn.",
    {
        "image": "https://huggingface.co/datasets/sentence-transformers/example-documents/resolve/main/llama4_hgf.png",
        "text": "Represent this image.",
    },
    {
        "video": "https://huggingface.co/datasets/sentence-transformers/example-documents/resolve/main/mapo_tofu.mp4",
        "text": "Represent this video.",
    },
]

query_embeddings = model.encode_query(queries)
document_embeddings = model.encode_document(documents)
print(query_embeddings.shape, document_embeddings.shape)
# (2, 2048) (3, 2048)

similarities = model.similarity(query_embeddings, document_embeddings)
print(similarities)
# tensor([[0.0683, 0.4972, 0.0309],
#         [0.7829, 0.1428, 0.5492]])
```

Each input is a string, a URL or path, a `PIL.Image`, or a dict combining `image`,
`video`, and `text` keys. Put `image` or `video` before `text` so the prompt matches
the ordering used above. Chat messages such as
`{"role": "user", "content": [{"type": "image", "image": ...}, {"type": "text", "text": ...}]}`
are also accepted, which is the way to interleave several images or videos in one input.

## Matryoshka Embeddings

```python
embedding_256 = torch.nn.functional.normalize(embedding[..., :256], dim=-1)
```

With Sentence Transformers, pass `truncate_dim` and let it renormalize:

```python
embeddings_256 = model.encode_document(documents, truncate_dim=256, normalize_embeddings=True)
```

Use a dimension listed in `model.config.matryoshka_dimensions`. On MMEB-v2, 256-dimensional embeddings retain 98.7% of the full-dimensional image and video performance.

## Serving

vLLM `0.27.0`:

```bash
MODEL_PATH=/path/to/WeMM-Embedding-2B
vllm serve "$MODEL_PATH" \
  --runner pooling \
  --chat-template "$MODEL_PATH/embedding_chat_template.jinja"
```

SGLang `0.5.9`:

```bash
MODEL_PATH=/path/to/WeMM-Embedding-2B
python patch_sglang_video.py
python -m sglang.launch_server \
  --model-path "$MODEL_PATH" \
  --is-embedding \
  --enable-precise-embedding-interpolation
```

## Evaluation

### MMEB-v2

Results on 78 datasets from Table 1 of the [technical report](https://github.com/Tencent/WeMM-Embedding/blob/main/assets/WeMM_Embedding_tech_report.pdf). Image and video tasks use Hit@1, while visual-document tasks use NDCG@5. Higher is better.

| Model | Size | AVG | Image | Video | VisDoc |
| --- | ---: | ---: | ---: | ---: | ---: |
| VLM2Vec | 2B | 47.8 | 59.7 | 29.0 | 44.0 |
| GME | 2B | 55.4 | 51.9 | 33.9 | 76.8 |
| VLM2Vec-V2 | 2B | 59.3 | 64.9 | 34.9 | 69.2 |
| Qwen3-VL-Embedding | 2B | 73.2 | 75.0 | 61.9 | 79.2 |
| DME-Small† | 2B | 74.8 | 75.9 | 65.6 | 79.9 |
| **WeMM-Embedding** | **2B** | **77.9** | **79.6** | **70.8** | **80.7** |
| **WeMM-Embedding** | **4B** | **79.2** | **80.8** | **72.1** | **82.0** |
| VLM2Vec | 8B | 53.2 | 65.5 | 34.0 | 49.1 |
| GME | 8B | 59.2 | 56.0 | 38.6 | 79.3 |
| Qwen3-VL-Embedding | 8B | 77.8 | 80.1 | 67.1 | 82.4 |
| DME-Medium† | 9B | 78.4 | 79.8 | 70.8 | 82.0 |
| **WeMM-Embedding** | **9B** | **80.6** | **81.9** | **74.3** | **83.3** |

† Closed-source leaderboard submission without publicly released model weights or a public inference endpoint.

### MMEB-v3

Results on all 190 tasks from Table 2 of the [technical report](https://github.com/Tencent/WeMM-Embedding/blob/main/assets/WeMM_Embedding_tech_report.pdf). V3-All includes the 78 MMEB-v2 tasks, 53 text tasks, 47 agent tasks, 11 audio tasks, and MCMR. Unsupported tasks are assigned a score of zero.

| Model | Size | V3-All | Text | Agent | MCMR | Audio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| VLM2Vec-V2 | 2B | 38.3 | 24.5 | 28.7 | 4.1 | 0.0 |
| Omni-Embed-Nemotron | 3B | 43.5 | 39.2 | 36.5 | 26.1 | 36.5 |
| E5-Omni | 3B | 44.6 | 26.7 | 36.9 | 31.9 | 30.8 |
| Qwen3-VL-Embedding | 2B | 50.9 | 39.2 | 39.3 | 42.0 | 0.0 |
| **WeMM-Embedding** | **2B** | **56.0** | **45.3** | **45.1** | **42.5** | **0.0** |
| **WeMM-Embedding** | **4B** | **58.2** | **47.9** | **49.0** | **41.9** | **0.0** |
| WAVE | 7B | 26.3 | 13.7 | 11.3 | 8.9 | 31.8 |
| VLM2Vec | 8B | 32.9 | 22.2 | 19.7 | 0.9 | 0.0 |
| LCO-Embedding-Omni | 7B | 40.6 | 32.4 | 27.8 | 20.0 | 43.2 |
| GME | 8B | 43.6 | 37.1 | 35.6 | 27.3 | 0.0 |
| E5-Omni | 7B | 47.1 | 26.9 | 36.7 | 41.1 | 43.0 |
| Tianmu-Emb-Uni | 8B | 53.3 | 43.6 | 39.4 | 38.8 | 38.9 |
| Qwen3-VL-Embedding | 8B | 53.5 | 42.5 | 38.4 | 38.0 | 0.0 |
| **WeMM-Embedding** | **9B** | **59.5** | **48.8** | **51.0** | **49.3** | **0.0** |

Text results use NDCG@5; agent, MCMR, and audio results use Hit@1.

## Citation
If you find this repository useful, please consider giving a star ⭐ and citation
```bibtex
@article{wemm-embedding,
      title={WeMM-Embedding: WeChat Multi-Modal Embedding Technical Report}, 
      author={Junjie Zhou and Ke Mei and Lei Li and Tianyi Wang and Fengyun Rao and Jing Lyu},
      year={2026},
      eprint={2608.24053},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2608.24053}, 
}
```

## License

WeMM-Embedding-2B, including the code, model parameters, and weights made publicly
available by Tencent, is licensed under the [Apache License 2.0](https://huggingface.co/tencent/WeMM-Embedding-2B/blob/main/LICENSE).
Third-party components remain subject to their respective original licenses.
