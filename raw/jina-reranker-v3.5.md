---
pipeline_tag: text-ranking
tags:
- transformers
- reranker
- qwen3
language:
- multilingual
base_model:
- Qwen/Qwen3-0.6B
inference: false
license: cc-by-nc-4.0
library_name: transformers
---

<p align="center">
<img src="https://huggingface.co/datasets/jinaai/documentation-images/resolve/main/logo.webp" alt="Jina AI: Your Search Foundation, Supercharged!" width="150px">
</p>


# jina-reranker-v3.5: Domain-Ready Listwise Document Reranker

[Blog](https://www.elastic.co/search-labs/blog/jina-reranker-35-legal-medical-structured-data) | [API](https://jina.ai/reranker) | [AWS](#) | [Azure](#) | [GCP](#) | [Arxiv](https://arxiv.org/abs/2607.18152) | [Predecessor: v3](https://huggingface.co/jinaai/jina-reranker-v3)

> [!TIP]
> [GGUF](https://huggingface.co/jinaai/jina-reranker-v3.5-GGUF) with quantizations and [MLX](https://huggingface.co/jinaai/jina-reranker-v3.5-mlx) versions are now available.

`jina-reranker-v3.5` is a 0.6B-parameter multilingual listwise document reranker and a drop-in upgrade to [`jina-reranker-v3`](https://huggingface.co/jinaai/jina-reranker-v3).
It keeps the same *last-but-not-late* (LBNL) listwise interface — ranking a query against many candidates in one forward pass — while improving **domain robustness**, **structured-data ranking**, **multilingual retrieval**, and **inference efficiency**.

Built on Qwen3-0.6B with 28 layers (hybrid **3L2G** attention: sliding-window layers interleaved with global layers, window = 1024, pinned terminal global layer required by LBNL) and a lightweight MLP projector (1024→512→512), it supports up to 131K tokens of context and ranks lists of documents jointly via causal self-attention and cosine scoring.

Compared with `jina-reranker-v3` under a unified top-100 protocol with [`jina-embeddings-v5-text-small`](https://huggingface.co/jinaai/jina-embeddings-v5-text-small) as the first stage:

| Model | Size | BEIR | MIRACL | RTEB‡ | Struct-IR† |
|-------|------|------|--------|------|------------|
| **jina-reranker-v3.5** | 0.6B | **63.20** | <u>74.11</u> | <u>70.95</u> | <u>48.3</u> |
| jina-reranker-v3 | 0.6B | 62.10 | 72.20 | 68.01 | 38.7 |
| Qwen3-Reranker-4B | 4.0B | 62.28 | **76.56** | **77.68** | **55.6** |
| Qwen3-Reranker-0.6B | 0.6B | 56.94 | 67.12 | 68.41 | 41.9 |
| mxbai-rerank-large-v2 | 1.5B | <u>62.45</u> | 69.65 | 70.81 | 43.0 |
| mxbai-rerank-base-v2 | 0.5B | 59.58 | 64.90 | 61.44 | 30.4 |

*nDCG@10 (%). Best per column in **bold**, second-best <u>underlined</u>. First-stage excluded.* †Struct-IR uses a controlled-pool protocol (gold docs + hardest distractors). ‡RTEB score excludes the MIRACL average score.

**Highlights vs. v3:** +1.10 BEIR (above 4B Qwen at ~7× fewer parameters), +2.6% relative MIRACL, +4.3% relative RTEB (large legal lifts), +24.8% relative Struct-IR, and **1.22×–1.56×** faster listwise inference on short → long contexts (A100, FlashAttention-2).


## Usage

### Local Inference

Use `transformers` for local inference:

**Installation:**

```bash
pip install transformers
```

**Load the model:**

```python
from transformers import AutoModel

model = AutoModel.from_pretrained(
    'jinaai/jina-reranker-v3.5',
    dtype="auto",
    trust_remote_code=True,
)
model.eval()
```

**Rank documents:**

```python
query = "What are the health benefits of green tea?"
documents = [
    "Green tea contains antioxidants called catechins that may help reduce inflammation and protect cells from damage.",
    "El precio del café ha aumentado un 20% este año debido a problemas en la cadena de suministro.",
    "Studies show that drinking green tea regularly can improve brain function and boost metabolism.",
    "Basketball is one of the most popular sports in the United States.",
    "绿茶富含儿茶素等抗氧化剂，可以降低心脏病风险，还有助于控制体重。",
    "Le thé vert est riche en antioxydants et peut améliorer la fonction cérébrale.",
]

# Rerank documents
results = model.rerank(query, documents)

# Results are sorted by relevance score (highest first)
for result in results:
    print(f"Score: {result['relevance_score']:.4f}")
    print(f"Document: {result['document'][:100]}...")
    print()
```

**API Reference:**

```python
model.rerank(
    query: str,                      # Search query
    documents: List[str],            # Documents to rank
    top_n: Optional[int] = None,     # Return only top N (default: all)
    return_embeddings: bool = False, # Include doc embeddings (default: False)
)
```

**Returns:** List of dicts with keys:
- `document`: Original document text
- `relevance_score`: Float score (higher = more relevant)
- `index`: Position in input documents list
- `embedding`: Document embedding (if `return_embeddings=True`)

**Example with options:**

```python
# Get only top 3 results
top_results = model.rerank(query, documents, top_n=3)

# Get embeddings for further processing
results_with_embeddings = model.rerank(query, documents, return_embeddings=True)
```


### API

Use Jina AI's [Reranker API](https://jina.ai/reranker) for the fastest integration:

```bash
curl -X POST \
  https://api.jina.ai/v1/rerank \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer JINA_API_KEY" \
  -d '{
  "model": "jina-reranker-v3.5",
  "query": "slm markdown",
  "documents": [
    ...
  ],
  "return_documents": false
}'
```

Response format:

```json
{
  "model": "jina-reranker-v3.5",
  "usage": {
    "total_tokens": 2813
  },
  "results": [
    {
      "index": 1,
      "relevance_score": 0.9310624287463884
    },
    {
      "index": 4,
      "relevance_score": 0.8982678574191957
    },
    {
      "index": 0,
      "relevance_score": 0.890233167219021
    }
  ]
}
```

If you already call `jina-reranker-v3`, switch the model string to `jina-reranker-v3.5` — same request schema, stronger domain / structured rankings, lower latency on long lists.


## Citation

If you find `jina-reranker-v3.5` useful in your research, please cite our technical report:

```bibtex
@misc{nasika2026jinarerankerv35,
      title={jina-reranker-v3.5: Hybrid-Attention Listwise Reranking with Self-Distillation for Domain-Robust Retrieval},
      author={Christina Nasika and Feng Wang and Antonis Minas Krasakis and Han Xiao},
      year={2026},
      eprint={2607.18152},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2607.18152},
}
```

See also the predecessor: [jina-reranker-v3 technical report](https://arxiv.org/abs/2509.25085).


## License

`jina-reranker-v3.5` is licensed under CC BY-NC 4.0. For commercial usage inquiries, feel free to [contact us](https://jina.ai/contact-sales/).
