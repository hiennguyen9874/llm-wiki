---
tags:
- vidore
- colpali
- multimodal-embedding
- multilingual-embedding
- Text-to-Visual Document (T→VD) retrieval
- feature-extraction
- sentence-similarity
- mteb
- sentence-transformers
- vllm
language:
- multilingual
inference: false
library_name: transformers
pipeline_tag: visual-document-retrieval
---
<br><br>

<p align="center">
<img src="https://huggingface.co/datasets/jinaai/documentation-images/resolve/main/logo.webp" alt="Jina AI: Your Search Foundation, Supercharged!" width="150px">
</p>


<p align="center">
<b>The embedding model trained by <a href="https://jina.ai/"><b>Jina AI</b></a>.</b>
</p>

# Jina Embeddings v4: Universal Embeddings for Multimodal Multilingual Retrieval


[GGUF](https://github.com/jina-ai/jina-embeddings-v4-gguf) | [Blog](https://jina.ai/news/jina-embeddings-v4-universal-embeddings-for-multimodal-multilingual-retrieval) | [Technical Report](https://arxiv.org/abs/2506.18902) | [API](https://jina.ai/embeddings)


## Intended Usage & Model Info
`jina-embeddings-v4` is a universal embedding model for multimodal and multilingual retrieval. 
The model is specially designed for complex document retrieval, including visually rich documents with charts, tables, and illustrations. 


Built on [Qwen/Qwen2.5-VL-3B-Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct), `jina-embeddings-v4` features:

- **Unified embeddings** for text, images, and visual documents, supporting both dense (single-vector) and late-interaction (multi-vector) retrieval.
- **Multilingual support** (30+ languages) and compatibility with a wide range of domains, including technical and visually complex documents.
- **Task-specific adapters** for retrieval, text matching, and code-related tasks, which can be selected at inference time.
- **Flexible embedding size**: dense embeddings are 2048 dimensions by default but can be truncated to as low as 128 with minimal performance loss.


Summary of features:

| Feature   | Jina Embeddings V4   |
|------------|------------|
| Base Model | Qwen2.5-VL-3B-Instruct |
| Supported Tasks | `retrieval`, `text-matching`, `code` |
| Model DType | BFloat 16 |
| Max Sequence Length | 32768 |
| Single-Vector Dimension | 2048 |
| Multi-Vector Dimension | 128 |
| Matryoshka dimensions | 128, 256, 512, 1024, 2048 |
| Pooling Strategy | Mean pooling |
| Attention Mechanism | FlashAttention2 |



## Training & Evaluation

Please refer to our [technical report of jina-embeddings-v4](https://arxiv.org/abs/2506.18902) for training details and benchmarks.


## Usage

<details>
  <summary>Requirements</a></summary>
  
The following Python packages are required:

- `transformers>=4.52.0`
- `torch>=2.6.0`
- `peft>=0.15.2`
- `torchvision`
- `pillow`
  
### Optional / Recommended
- **flash-attention**: Installing [flash-attention](https://github.com/Dao-AILab/flash-attention) is recommended for improved inference speed and efficiency, but not mandatory.
- **sentence-transformers**: If you want to use the model via the `sentence-transformers` interface, install this package as well.

</details>


<details>
  <summary>via <a href="https://jina.ai/embeddings/">Jina AI Embeddings API</a></summary>


```bash
curl https://api.jina.ai/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JINA_AI_API_TOKEN" \
  -d @- <<EOFEOF
  {
    "model": "jina-embeddings-v4",
    "task": "text-matching",
    "input": [
        {
            "text": "غروب جميل على الشاطئ"
        },
        {
            "text": "海滩上美丽的日落"
        },
        {
            "text": "A beautiful sunset over the beach"
        },
        {
            "text": "Un beau coucher de soleil sur la plage"
        },
        {
            "text": "Ein wunderschöner Sonnenuntergang am Strand"
        },
        {
            "text": "Ένα όμορφο ηλιοβασίλεμα πάνω από την παραλία"
        },
        {
            "text": "समुद्र तट पर एक खूबसूरत सूर्यास्त"
        },
        {
            "text": "Un bellissimo tramonto sulla spiaggia"
        },
        {
            "text": "浜辺に沈む美しい夕日"
        },
        {
            "text": "해변 위로 아름다운 일몰"
        },
        {
            "image": "https://i.ibb.co/nQNGqL0/beach1.jpg"
        },
        {
            "image": "https://i.ibb.co/r5w8hG8/beach2.jpg"
        }
    ]
  }
EOFEOF
```

</details>

<details>
  <summary>via <a href="https://huggingface.co/docs/transformers/en/index">transformers</a></summary>

```python
# !pip install transformers>=4.52.0 torch>=2.6.0 peft>=0.15.2 torchvision pillow
# !pip install
from transformers import AutoModel
import torch

# Initialize the model
model = AutoModel.from_pretrained("jinaai/jina-embeddings-v4", trust_remote_code=True, torch_dtype=torch.float16)

model.to("cuda")

# ========================
# 1. Retrieval Task
# ========================
# Configure truncate_dim, max_length (for texts), max_pixels (for images), vector_type, batch_size in the encode function if needed

# Encode query
query_embeddings = model.encode_text(
    texts=["Overview of climate change impacts on coastal cities"],
    task="retrieval",
    prompt_name="query",
)

# Encode passage (text)
passage_embeddings = model.encode_text(
    texts=[
        "Climate change has led to rising sea levels, increased frequency of extreme weather events..."
    ],
    task="retrieval",
    prompt_name="passage",
)

# Encode image/document
image_embeddings = model.encode_image(
    images=["https://i.ibb.co/nQNGqL0/beach1.jpg"],
    task="retrieval",
)

# ========================
# 2. Text Matching Task
# ========================
texts = [
    "غروب جميل على الشاطئ",  # Arabic
    "海滩上美丽的日落",  # Chinese
    "Un beau coucher de soleil sur la plage",  # French
    "Ein wunderschöner Sonnenuntergang am Strand",  # German
    "Ένα όμορφο ηλιοβασίλεμα πάνω από την παραλία",  # Greek
    "समुद्र तट पर एक खूबसूरत सूर्यास्त",  # Hindi
    "Un bellissimo tramonto sulla spiaggia",  # Italian
    "浜辺に沈む美しい夕日",  # Japanese
    "해변 위로 아름다운 일몰",  # Korean
]

text_embeddings = model.encode_text(texts=texts, task="text-matching")

# ========================
# 3. Code Understanding Task
# ========================

# Encode query
query_embedding = model.encode_text(
    texts=["Find a function that prints a greeting message to the console"],
    task="code",
    prompt_name="query",
)

# Encode code
code_embeddings = model.encode_text(
    texts=["def hello_world():\n    print('Hello, World!')"],
    task="code",
    prompt_name="passage",
)

# ========================
# 4. Use multivectors
# ========================

multivector_embeddings = model.encode_text(
    texts=texts,
    task="retrieval",
    prompt_name="query",
    return_multivector=True,
)

images = ["https://i.ibb.co/nQNGqL0/beach1.jpg", "https://i.ibb.co/r5w8hG8/beach2.jpg"]
multivector_image_embeddings = model.encode_image(
    images=images,
    task="retrieval",
    return_multivector=True,
)
```
</details>

<details>
  <summary>via <a href="https://sbert.net/">sentence-transformers</a></summary>
  
```python
from sentence_transformers import SentenceTransformer

# Initialize the model
model = SentenceTransformer("jinaai/jina-embeddings-v4", trust_remote_code=True)
# ========================
# 1. Retrieval Task
# ========================
# Encode query
query_embeddings = model.encode(
    sentences=["Overview of climate change impacts on coastal cities"],
    task="retrieval",
    prompt_name="query",
)

print(f"query_embeddings.shape = {query_embeddings.shape}")

# Encode passage (text)
passage_embeddings = model.encode(
    sentences=[
        "Climate change has led to rising sea levels, increased frequency of extreme weather events..."
    ],
    task="retrieval",
    prompt_name="passage",
)

print(f"passage_embeddings.shape = {passage_embeddings.shape}")

# Encode image/document
image_embeddings = model.encode(
    sentences=["https://i.ibb.co/nQNGqL0/beach1.jpg"],
    task="retrieval",
)

print(f"image_embeddings.shape = {image_embeddings.shape}")

# ========================
# 2. Text Matching Task
# ========================
texts = [
    "غروب جميل على الشاطئ",  # Arabic
    "海滩上美丽的日落",  # Chinese
    "Un beau coucher de soleil sur la plage",  # French
    "Ein wunderschöner Sonnenuntergang am Strand",  # German
    "Ένα όμορφο ηλιοβασίλεμα πάνω από την παραλία",  # Greek
    "समुद्र तट पर एक खूबसूरत सूर्यास्त",  # Hindi
    "Un bellissimo tramonto sulla spiaggia",  # Italian
    "浜辺に沈む美しい夕日",  # Japanese
    "해변 위로 아름다운 일몰",  # Korean
]

text_embeddings = model.encode(sentences=texts, task="text-matching")

# ========================
# 3. Code Understanding Task
# ========================

# Encode query
query_embeddings = model.encode(
    sentences=["Find a function that prints a greeting message to the console"],
    task="code",
    prompt_name="query",
)

# Encode code
code_embeddings = model.encode(
    sentences=["def hello_world():\n    print('Hello, World!')"],
    task="code",
    prompt_name="passage",
)

# ========================
# 4. Use multivectors
# ========================
# If you want to use multi-vector embeddings, please use the Hugging Face model directly.
```
</details>

<details>
  <summary>via <a href="https://github.com/vllm-project/vllm">vLLM</a></summary>

We provide separate model versions for each task (`retrieval`, `text-matching`, `code`) where specific adapter is merged into the base `Qwen2.5-VL` weights. 
This modification enables native compatibility with vLLM.

Instructions and usage examples for each task are available in their respective directories:
- [jina-embeddings-v4-vllm-retrieval](https://huggingface.co/jinaai/jina-embeddings-v4-vllm-retrieval)
- [jina-embeddings-v4-vllm-text-matching](https://huggingface.co/jinaai/jina-embeddings-v4-vllm-text-matching)
- [jina-embeddings-v4-vllm-code](https://huggingface.co/jinaai/jina-embeddings-v4-vllm-code)

Please refer to the directory that matches your task for more details.

</details>


## Jina-VDR
Alongside `jina-embeddings-v4`, we’re releasing [Jina VDR](https://github.com/jina-ai/jina-vdr), a multilingual, multi-domain benchmark for visual document retrieval. The task collection can be viewed [here](https://huggingface.co/collections/jinaai/jinavdr-visual-document-retrieval-684831c022c53b21c313b449), and evaluation instructions can be found [here](https://github.com/jina-ai/jina-vdr).


## License

This model was initially released under cc-by-nc-4.0 due to an error.
The correct license is the Qwen Research License, as this model is derived from Qwen-2.5-VL-3B which is governed by that license.

## Contact

Join our [Discord community](https://discord.jina.ai) and chat with other community members about ideas.


## Citation

If you find `jina-embeddings-v4` useful in your research, please cite the following paper:
```
@misc{günther2025jinaembeddingsv4universalembeddingsmultimodal,
      title={jina-embeddings-v4: Universal Embeddings for Multimodal Multilingual Retrieval}, 
      author={Michael Günther and Saba Sturua and Mohammad Kalim Akram and Isabelle Mohr and Andrei Ungureanu and Sedigheh Eslami and Scott Martens and Bo Wang and Nan Wang and Han Xiao},
      year={2025},
      eprint={2506.18902},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2506.18902}, 
}
```