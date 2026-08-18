---
language:
- en
- es
- de
- fr
- it
- pt
- ar
- sv
- 'no'
- ja
- ko
tags:
- liquid
- lfm2
- lfm2.5
- edge
- sentence-transformers
- sentence-similarity
- feature-extraction
pipeline_tag: sentence-similarity
library_name: sentence-transformers
license: other
license_name: lfm1.0
license_link: LICENSE
base_model: LiquidAI/LFM2.5-350M-Base
---

<center>
<div style="text-align: center;">
  <img 
    src="https://cdn-uploads.huggingface.co/production/uploads/61b8e2ba285851687028d395/2b08LKpev0DNEk6DlnWkY.png" 
    alt="Liquid AI"
    style="width: 100%; max-width: 100%; height: auto; display: inline-block; margin-bottom: 0.5em; margin-top: 0.5em;"
  />
</div>
<div style="display: flex; justify-content: center; gap: 0.5em;">
<a href="https://playground.liquid.ai/"><strong>Try LFM</strong></a> • <a href="https://docs.liquid.ai/lfm/getting-started/welcome"><strong>Docs</strong></a> • <a href="https://leap.liquid.ai/"><strong>LEAP</strong></a> • <a href="https://discord.com/invite/liquid-ai"><strong>Discord</strong></a>
</div>
</center>

<br>

# LFM2.5-Embedding-350M

We release two new **best-in-class multilingual retrieval** models:

- **LFM2.5-Embedding-350M** — A dense bi-encoder, one vector per document. Smallest, fastest index.
- **[LFM2.5-ColBERT-350M](https://huggingface.co/LiquidAI/LFM2.5-ColBERT-350M)** — A late-interaction model. One vector per *token*, matched via MaxSim. Higher accuracy and better generalization at the cost of index size.

Both models are 350M params and the first bidirectional members of the LFM family, built on [LFM2.5-350M-Base](https://huggingface.co/LiquidAI/LFM2.5-350M-Base). They can be used as a **drop-in replacement** for your current RAG pipeline and target fast, cheap, and reliable multilingual / cross-lingual search across 11 languages.

Find more details about the bidirectional architecture and training recipe in our [blog post](https://www.liquid.ai/blog/lfm2-5-retrievers).

![bienc](https://cdn-uploads.huggingface.co/production/uploads/63f389fda096536aeaae0a66/LjpFnq59BbuhKLVTExtcU.png)

## 📄 Model details

| Property              | **LFM2.5-Embedding-350M**              | **[LFM2.5-ColBERT-350M](https://huggingface.co/LiquidAI/LFM2.5-ColBERT-350M)** |
| --------------------- | -------------------------------------- | ----------------------------------- |
| **Type**              | Dense bi-encoder (single vector)       | Late interaction (per-token vectors) |
| **Total parameters**  | ~354M                                  | ~353M                               |
| **Backbone**          | [LFM2.5-350M-Base](https://huggingface.co/LiquidAI/LFM2.5-350M-Base) + bi-directional patches | [LFM2.5-350M-Base](https://huggingface.co/LiquidAI/LFM2.5-350M-Base) + bi-directional patches |
| **Layers**            | 17 (10 conv + 6 attn + 1 pool)         | 17 (10 conv + 6 attn + 1 dense)     |
| **Vocabulary size**   | 65,536                                 | 64,402                              |
| **Output**            | 1024-dim CLS vector                    | 128-dim per token                   |
| **Similarity**        | Cosine                                 | MaxSim                              |
| **Training precision**| BF16                                   | BF16                                |
| **License**           | LFM Open License v1.0                  | LFM Open License v1.0               |

**Document length:** 512 tokens

**Supported languages:** English, Spanish, German, French, Italian, Portuguese, Arabic, Swedish, Norwegian, Japanese, Korean.

**Architecture:**

```text
SentenceTransformer(
  (0): Transformer({'max_seq_length': 512, 'do_lower_case': False}) with Transformer model: Lfm2BidirectionalModel
  (1): Pooling({'word_embedding_dimension': 1024, 'pooling_mode_cls_token': True, 'pooling_mode_mean_tokens': False})
)
```

**Asymmetric prompts:** `query: ` for queries, `document: ` for passages. They are stored in the model config and applied automatically via `prompt_name`.

We recommend LFM2.5-Embedding-350M and LFM2.5-ColBERT-350M for short-context retrieval use cases, such as:

- **E-commerce**: find products across many languages with semantic search at scale.
- **FAQ and support knowledge bases**: retrieve the right answer reliably across customer-facing surfaces.
- **On-device semantic search**: search files, emails, and notes locally on consumer hardware.
- **Enterprise knowledge assistants**: retrieve internal legal, financial, and technical documents across languages.

## 🏃 How to run

First, install `sentence-transformers`:

```bash
pip install -U sentence-transformers
```

### Encoding queries and documents

Load LFM2.5-Embedding-350M and encode your queries and documents separately, using the matching prompt name on each side. Cosine similarity (or a normalized dot product) ranks documents against queries:

```python
from sentence_transformers import SentenceTransformer

# Load the model (trust_remote_code applies the bidirectional patches)
model = SentenceTransformer(
    "LiquidAI/LFM2.5-Embedding-350M",
    trust_remote_code=True,
)

queries = [
    "What is the capital of France?",
    "Which city is Japan's capital?",
]
documents = [
    "Paris is the capital and largest city of France. Located on the Seine River in northern France, it serves as the country's political, economic, and cultural center.",
    "Tokyo, officially the Tokyo Metropolis, is the capital of Japan. It is the most populous metropolitan area in the world and serves as Japan's administrative, financial, and commercial hub.",
    "Berlin is the capital and largest city of Germany. Reunified in 1990 after the fall of the Berlin Wall, it now serves as a major cultural and political center in Europe.",
]

# Encode with the matching prompt name; normalize so the dot product == cosine similarity
q_emb = model.encode(queries,   prompt_name="query",    normalize_embeddings=True)
d_emb = model.encode(documents, prompt_name="document", normalize_embeddings=True)

scores = q_emb @ d_emb.T  # shape: (n_queries, n_documents)
```

Always pass `prompt_name="query"` for queries and `prompt_name="document"` for passages — the model was trained with these prefixes, and omitting them silently degrades retrieval quality.

### Flash Attention 2 (optional)

LFM2.5-Embedding-350M can run with FlashAttention-2 (requires `flash-attn` installed):

```python
import torch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "LiquidAI/LFM2.5-Embedding-350M",
    trust_remote_code=True,
    model_kwargs={"attn_implementation": "flash_attention_2", "dtype": torch.bfloat16},
)
```

Verified equivalent to the default within bf16 noise (multilingual NanoBEIR ndcg@10 within 0.002 across 11 languages). At the model's 512-token max length the speed gain is small (~5%); FA2 mainly helps memory and throughput if you fine-tune or run the backbone at longer contexts.

### Fine-tuning

Standard `sentence-transformers` training works directly. Example with `MultipleNegativesRankingLoss`:

```python
from datasets import Dataset
from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
)
from sentence_transformers.losses import MultipleNegativesRankingLoss

model = SentenceTransformer("LiquidAI/LFM2.5-Embedding-350M", trust_remote_code=True)
loss = MultipleNegativesRankingLoss(model)

train_ds = Dataset.from_dict({
    "query":    [...],
    "positive": [...],
    # optional: "negative": [...],
})

args = SentenceTransformerTrainingArguments(
    output_dir="out",
    num_train_epochs=1,
    per_device_train_batch_size=64,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    bf16=True,
    prompts={"query": "query: ", "positive": "document: "},
)

trainer = SentenceTransformerTrainer(model=model, args=args, train_dataset=train_ds, loss=loss)
trainer.train()
```

Notes:

- Always pass the asymmetric prompts during training (the model was trained with them).
- For larger effective batches without OOM, swap `MultipleNegativesRankingLoss` for `CachedMultipleNegativesRankingLoss`.
- Save with `model.save_pretrained(...)`; the modeling file and `auto_map` are preserved so the patched behavior survives reloads.

## 📈 Performance

We highlight (= bold) the best bi-encoder and best late retriever for each language.

### NanoBEIR Multilingual Extended — NDCG@10

[`LiquidAI/nanobeir-multilingual-extended`](https://huggingface.co/datasets/LiquidAI/nanobeir-multilingual-extended). Multilingual retrieval capabilities.

| Model | Type | AVG | ar | de | en | es | fr | it | ja | ko | no | pt | sv |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **LiquidAI/LFM2.5-ColBERT-350M** | late | **0.605** | **0.551** | **0.606** | 0.687 | **0.607** | **0.622** | **0.606** | **0.614** | **0.590** | **0.570** | **0.613** | **0.586** |
| **LiquidAI/LFM2.5-Embedding-350M** | dense | **0.577** | **0.529** | **0.581** | 0.644 | **0.581** | **0.592** | **0.583** | **0.575** | **0.563** | **0.557** | **0.581** | **0.566** |
| Qwen/Qwen3-Embedding-0.6B | dense | 0.556 | 0.514 | 0.560 | 0.649 | 0.568 | 0.565 | 0.565 | 0.551 | 0.530 | 0.516 | 0.571 | 0.525 |
| LiquidAI/LFM2-ColBERT-350M | late | 0.540 | 0.491 | 0.563 | 0.661 | 0.563 | 0.564 | 0.543 | 0.557 | 0.527 | 0.449 | 0.547 | 0.480 |
| Alibaba-NLP/gte-multilingual-base | dense | 0.528 | 0.477 | 0.523 | 0.624 | 0.537 | 0.542 | 0.528 | 0.511 | 0.494 | 0.516 | 0.534 | 0.526 |
| lightonai/GTE-ModernColBERT-v1 | late | 0.489 | 0.309 | 0.499 | 0.680 | 0.525 | 0.546 | 0.516 | 0.459 | 0.368 | 0.465 | 0.530 | 0.483 |
| lightonai/LateOn | late | 0.484 | 0.307 | 0.505 | **0.690** | 0.531 | 0.537 | 0.514 | 0.442 | 0.326 | 0.465 | 0.533 | 0.475 |
| lightonai/DenseOn | dense | 0.432 | 0.178 | 0.474 | **0.676** | 0.496 | 0.520 | 0.487 | 0.378 | 0.197 | 0.422 | 0.493 | 0.433 |
| Alibaba-NLP/gte-modernbert-base | dense | 0.383 | 0.112 | 0.449 | 0.666 | 0.448 | 0.475 | 0.408 | 0.275 | 0.180 | 0.376 | 0.431 | 0.391 |
| BAAI/bge-large-en-v1.5 | dense | 0.359 | 0.059 | 0.419 | 0.642 | 0.445 | 0.475 | 0.431 | 0.198 | 0.132 | 0.358 | 0.434 | 0.353 |

### MKQA-11 — Recall@20

[MKQA](https://github.com/apple/ml-mkqa). Cross-lingual capabilities (subset of the 11 languages we target).

| Model | Type | AVG | ar | de | en | es | fr | it | ja | ko | no | pt | sv |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **LiquidAI/LFM2.5-ColBERT-350M** | late | **0.694** | **0.608** | **0.709** | 0.748 | **0.711** | **0.715** | **0.707** | **0.703** | **0.640** | **0.689** | **0.703** | **0.700** |
| **LiquidAI/LFM2.5-Embedding-350M** | dense | **0.691** | **0.610** | **0.709** | 0.738 | **0.708** | **0.715** | **0.703** | **0.685** | **0.630** | 0.691 | **0.710** | **0.708** |
| Alibaba-NLP/gte-multilingual-base | dense | 0.675 | 0.567 | 0.692 | 0.741 | 0.705 | 0.703 | 0.697 | 0.655 | 0.563 | **0.698** | 0.700 | 0.699 |
| LiquidAI/LFM2-ColBERT-350M | late | 0.646 | 0.554 | 0.696 | 0.754 | **0.711** | 0.710 | 0.667 | 0.658 | 0.558 | 0.541 | 0.669 | 0.589 |
| Qwen/Qwen3-Embedding-0.6B | dense | 0.638 | 0.520 | 0.671 | 0.723 | 0.678 | 0.672 | 0.671 | 0.635 | 0.543 | 0.620 | 0.667 | 0.620 |
| lightonai/GTE-ModernColBERT-v1 | late | 0.459 | 0.092 | 0.532 | 0.754 | 0.552 | 0.615 | 0.510 | 0.275 | 0.166 | 0.503 | 0.524 | 0.524 |
| lightonai/LateOn | late | 0.454 | 0.157 | 0.492 | **0.755** | 0.537 | 0.577 | 0.481 | 0.316 | 0.209 | 0.472 | 0.502 | 0.501 |
| lightonai/DenseOn | dense | 0.435 | 0.165 | 0.482 | **0.751** | 0.491 | 0.553 | 0.457 | 0.325 | 0.222 | 0.438 | 0.443 | 0.453 |
| BAAI/bge-large-en-v1.5 | dense | 0.413 | 0.133 | 0.471 | 0.748 | 0.450 | 0.531 | 0.461 | 0.208 | 0.172 | 0.456 | 0.443 | 0.467 |
| Alibaba-NLP/gte-modernbert-base | dense | 0.295 | 0.060 | 0.333 | 0.736 | 0.273 | 0.417 | 0.291 | 0.100 | 0.052 | 0.332 | 0.326 | 0.330 |

### Inference speed - llama.cpp

End-to-end latency on **MacBook Pro M4 Max** via **llama.cpp** at **fp16**, measured at **32-token queries** and **256-token documents**. `Docs cached` means that the document embeddings are pre-computed and looked up (from an index).

| Model | Stage | Docs cached | p50 | p95 |
| --- | --- | :-: | :-: | :-: |
| LFM2.5-Embedding-350M  | Query embedding                          | yes | 7.3 ms  | 9.6 ms  |
| LFM2.5-ColBERT-350M    | Query embedding                          | yes | 8.1 ms  | 8.5 ms  |
| LFM2.5-ColBERT-350M    | Query embedding + MaxSim                 | yes | 8.2 ms  | 15.2 ms |
| LFM2.5-ColBERT-350M    | Query embedding + Doc embedding + MaxSim | no  | 34.3 ms | 36.3 ms |

Both models [LiquidAI/LFM2.5-ColBERT-350M-GGUF](https://huggingface.co/LiquidAI/LFM2.5-ColBERT-350M-GGUF/) and [LiquidAI/LFM2.5-Embedding-350M-GGUF](https://huggingface.co/LiquidAI/LFM2.5-Embedding-350M-GGUF/) are available on Hugging Face under different quantization schemas for llama.cpp.

### Inference speed - Enterprise GPU

For large-scale production-grade enterprise deployments, we also experiment with an internal GPU stack to deliver extremely low-latency serving under high inbound load. We observe latencies as low as 1 ms.

![GPU serving latency](https://cdn-uploads.huggingface.co/production/uploads/63f389fda096536aeaae0a66/WTdmKJ2LpG07-iAqXYGDe.png)

| Workload | Setup | p50 | p95 | p99 |
| --- | --- | :-: | :-: | :-: |
| LFM2.5-Embedding-350M | Query embedding                          | 1.5 ms  | 1.6 ms  | 1.7 ms  |
| LFM2.5-ColBERT-350M   | Query embedding                          | 1.3 ms  | 1.4 ms  | 1.5 ms  |
| LFM2.5-ColBERT-350M   | Query embedding + MaxSim                 | 2.5 ms  | 2.7 ms  | 2.8 ms  |
| LFM2.5-ColBERT-350M   | Query embedding + Doc embedding + MaxSim | 22.8 ms | 24.1 ms | 26.4 ms |

## 📬 Contact

- Got questions or want to connect? [Join our Discord community](https://discord.com/invite/liquid-ai).
- If you are interested in custom solutions with edge deployment, please contact [our sales team](https://www.liquid.ai/contact).

## Citation

```
@article{liquidai2025lfm2,
  title={LFM2 Technical Report},
  author={Liquid AI},
  journal={arXiv preprint arXiv:2511.23404},
  year={2025}
}
```
