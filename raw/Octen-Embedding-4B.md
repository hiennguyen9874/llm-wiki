---
language:
- en
- zh
- multilingual
license: apache-2.0
library_name: sentence-transformers
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- embedding
- text-embedding
- retrieval
pipeline_tag: sentence-similarity
base_model: Qwen/Qwen3-Embedding-4B
---

# Octen-Embedding-4B

Octen-Embedding-4B is a text embedding model developed by [Octen](https://octen.ai/) for semantic search and retrieval tasks. This model is fine-tuned from [Qwen/Qwen3-Embedding-4B](https://huggingface.co/Qwen/Qwen3-Embedding-4B) and supports multiple languages, providing high-quality embeddings for various applications.

## Key Highlights

### 🥇 RTEB Leaderboard Champion (as of January 12, 2026)
- **Octen-Embedding-8B ranks #1 on the [RTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)** with Mean (Task) score of **0.8045**
- Excellent performance on both Public (0.7953) and Private (0.8157) datasets
- Demonstrates true generalization capability without overfitting to public benchmarks

### Industry-Oriented Vertical Domain Expertise
- **Legal**: Legal document retrieval
- **Finance**: Financial reports, Q&A, and personal finance content
- **Healthcare**: Medical Q&A, clinical dialogues, and health consultations
- **Code**: Programming problems, code search, and SQL queries

### Ultra-Long Context Support
- Supports up to **32,768 tokens** context length
- Suitable for processing long documents in legal, healthcare, and other domains
- High-dimensional embedding space for rich semantic representation

### Multilingual Capability
- Supports **100+ languages**
- Includes various programming languages
- Strong multilingual, cross-lingual, and code retrieval capabilities

---

## Open Source Model List

| Model Type | Model | Size | Max Tokens | Embedding Dimensions | HuggingFace Link |
|------------|-------|------|------------|---------------------|------------------|
| Text Embedding | [Octen-Embedding-0.6B](https://huggingface.co/Octen/Octen-Embedding-0.6B) | 0.6B | 32,768 | 1024 | ✅ Available |
| Text Embedding | [Octen-Embedding-4B](https://huggingface.co/Octen/Octen-Embedding-4B) | 4.0B | 32,768 | 2560 | ✅ Available |
| Text Embedding | [Octen-Embedding-8B](https://huggingface.co/Octen/Octen-Embedding-8B) | 7.6B | 32,768 | 4096 | ✅ Available |

**Model Family Design**:
- **Octen-Embedding-8B**: Best performance, RTEB #1, for high-precision retrieval
- **Octen-Embedding-4B**: Best in 4B category, balanced performance and efficiency
- **Octen-Embedding-0.6B**: Lightweight deployment, suitable for edge devices and resource-constrained environments

For API access, deployment solutions, and technical documentation, visit [octen.ai](https://octen.ai/).

---

## Experimental Results

### RTEB Leaderboard (Overall Performance)

| Model | Embedding Dim | Max Tokens | Mean (Public) | Mean (Private) | Mean (Task) |
|-------|---------------|------------|---------------|----------------|-------------|
| **Octen-Embedding-8B** | **4096** | **32768** | **0.7953** | **0.8157** | **0.8045** |
| voyage-3-large | 1024 | 32000 | 0.7434 | 0.8277 | 0.7812 |
| gemini-embedding-001 | 3072 | 2048 | 0.7218 | 0.8075 | 0.7602 |
| **Octen-Embedding-4B** | **2560** | **32768** | **0.7747** | **0.7942** | **0.7834** |
| MoD-Embedding | 2560 | 32768 | 0.7642 | 0.7900 | 0.7758 |
| Qwen3-Embedding-8B | 4096 | 32768 | 0.7310 | 0.7838 | 0.7547 |
| **Octen-Embedding-0.6B** | **1024** | **32768** | **0.7241** | **-** | **-** |
| voyage-3.5 | 1024 | 32000 | 0.7139 | 0.8102 | 0.7571 |
| Cohere-embed-v4.0 | 1536 | 128000 | 0.6534 | 0.7943 | 0.7166 |
| jina-embeddings-v4 | 2048 | 32768 | 0.6652 | 0.7664 | 0.7105 |
| GritLM-7B | 4096 | 32768 | 0.6187 | 0.7385 | 0.6724 |
| text-embedding-3-large | 3072 | 8191 | 0.6110 | 0.7130 | 0.6567 |
| e5-mistral-7b-instruct | 4096 | 32768 | 0.5090 | 0.7091 | 0.5987 |
| NV-Embed-v2 | 4096 | 32768 | 0.5805 | 0.6691 | 0.6203 |
| snowflake-arctic-embed-l-v2.0 | 1024 | 8192 | 0.5395 | 0.7079 | 0.6150 |
| multilingual-e5-large-instruct | 1024 | 514 | 0.5478 | 0.6859 | 0.6097 |
| gte-multilingual-base | 768 | 8192 | 0.5291 | 0.6697 | 0.5921 |
| text-embedding-3-small | 1536 | 8191 | 0.5260 | 0.6630 | 0.5874 |
| bge-m3 | 1024 | 8194 | 0.5216 | 0.6726 | 0.5893 |
| Qwen3-Embedding-4B | 2560 | 32768 | - | 0.7711 | - |
| Qwen3-Embedding-0.6B | 1024 | 32768 | - | 0.7117 | - |

---

## Model Details

- **Base Model**: [Qwen/Qwen3-Embedding-4B](https://huggingface.co/Qwen/Qwen3-Embedding-4B)
- **Model Size**: 4B parameters
- **Max Sequence Length**: 40,960 tokens
- **Embedding Dimension**: 2560
- **Languages**: English, Chinese, and multilingual support
- **Training Method**: LoRA fine-tuning

## Usage

### Using Sentence Transformers

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Octen/Octen-Embedding-4B")

# Encode sentences
sentences = [
    "This is an example sentence",
    "Each sentence is converted to a vector"
]

embeddings = model.encode(sentences)
print(embeddings.shape)
# Output: (2, 2560)

# Compute similarity
from sentence_transformers.util import cos_sim
similarity = cos_sim(embeddings[0], embeddings[1])
print(f"Similarity: {similarity.item():.4f}")
```

### Using Transformers

```python
from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F

tokenizer = AutoTokenizer.from_pretrained("Octen/Octen-Embedding-4B", padding_side="left")
model = AutoModel.from_pretrained("Octen/Octen-Embedding-4B")
model.eval()

def encode(texts):
    inputs = tokenizer(texts, padding=True, truncation=True,
                      max_length=8192, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        # Use last token embedding
        embeddings = outputs.last_hidden_state[:, -1, :]
        # Normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)

    return embeddings

# Example usage
texts = ["Hello world", "你好世界"]
embeddings = encode(texts)
similarity = torch.matmul(embeddings[0], embeddings[1])
print(f"Similarity: {similarity.item():.4f}")
```

## Recommended Use Cases

- Semantic search and information retrieval
- Document similarity and clustering
- Question answering
- Cross-lingual retrieval
- Text classification with embeddings

## Limitations

- Performance may vary across different domains and languages
- Very long documents (>40K tokens) require truncation
- Optimized for retrieval tasks, not for text generation

## License

This model is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

This model is derived from [Qwen/Qwen3-Embedding-4B](https://huggingface.co/Qwen/Qwen3-Embedding-4B), which is also licensed under Apache License 2.0.

## Paper

For more details, please refer to our blog post: [Octen Series: Optimizing Embedding Models to #1 on RTEB Leaderboard](https://octen-team.github.io/octen_blog/posts/octen-rteb-first-place/)

## Citation

If you find our work helpful, please consider citing:

```bibtex
@misc{octen2025rteb,
  title={Octen Series: Optimizing Embedding Models to #1 on RTEB Leaderboard},
  author={Octen Team},
  year={2025},
  url={https://octen-team.github.io/octen_blog/posts/octen-rteb-first-place/}
}
```
