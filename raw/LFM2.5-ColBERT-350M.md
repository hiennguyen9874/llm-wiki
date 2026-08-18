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
- ColBERT
- PyLate
- sentence-transformers
- multi-vector
- sentence-similarity
- feature-extraction
pipeline_tag: sentence-similarity
library_name: PyLate
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

# LFM2.5-ColBERT-350M

We release two new **best-in-class multilingual retrieval** models:

- **[LFM2.5-Embedding-350M](https://huggingface.co/LiquidAI/LFM2.5-Embedding-350M)** — A dense bi-encoder, one vector per document. Smallest, fastest index.
- **LFM2.5-ColBERT-350M** — A late-interaction model. One vector per *token*, matched via MaxSim. Higher accuracy and better generalization at the cost of index size.

Both models are 350M params and the first bidirectional members of the LFM family, built on [LFM2.5-350M-Base](https://huggingface.co/LiquidAI/LFM2.5-350M-Base). They can be used as a **drop-in replacement** for your current RAG pipeline and target fast, cheap, and reliable multilingual / cross-lingual search across 11 languages.

Find more details about the bidirectional architecture and training recipe in our [blog post](https://www.liquid.ai/blog/lfm2-5-retrievers).

> [!NOTE]
> 💻 **Demo**: https://huggingface.co/spaces/LiquidAI/colbert-tool-selection

![colb](https://cdn-uploads.huggingface.co/production/uploads/63f389fda096536aeaae0a66/snq-O6VmWRJNMYCNHGtDD.png)

## 📄 Model details

| Property              | **LFM2.5-ColBERT-350M**                | **[LFM2.5-Embedding-350M](https://huggingface.co/LiquidAI/LFM2.5-Embedding-350M)** |
| --------------------- | -------------------------------------- | ----------------------------------- |
| **Type**              | Late interaction (per-token vectors)   | Dense bi-encoder (single vector)    |
| **Total parameters**  | ~353M                                  | ~354M                               |
| **Backbone**          | [LFM2.5-350M-Base](https://huggingface.co/LiquidAI/LFM2.5-350M-Base) + bi-directional patches  |  [LFM2.5-350M-Base](https://huggingface.co/LiquidAI/LFM2.5-350M-Base) + bi-directional patches |
| **Layers**            | 17 (10 conv + 6 attn + 1 dense)        | 17 (10 conv + 6 attn + 1 pool)      |
| **Vocabulary size**   | 64,402                                 | 65,536                              |
| **Output**            | 128-dim per token                      | 1024-dim CLS vector                 |
| **Similarity**        | MaxSim                                 | Cosine                              |
| **Training precision**| BF16                                   | BF16                                |
| **License**           | LFM Open License v1.0                  | LFM Open License v1.0               |

**Document length:** 512 tokens &nbsp;&nbsp; 

**Query length:** 32 tokens

**Supported languages:** English, Spanish, German, French, Italian, Portuguese, Arabic, Swedish, Norwegian, Japanese, Korean.

**Architecture:**

```text
ColBERT(
  (0): Transformer({'max_seq_length': 511, 'do_lower_case': False}) with Transformer model: Lfm2BidirectionalModel
  (1): Dense({'in_features': 1024, 'out_features': 128, 'bias': False, 'activation_function': 'torch.nn.modules.linear.Identity'})
)
```

We recommend LFM2.5-Embedding-350M and LFM2.5-ColBERT-350M for short-context retrieval use cases, such as:

- **E-commerce**: find products across many languages with semantic search at scale.
- **FAQ and support knowledge bases**: retrieve the right answer reliably across customer-facing surfaces.
- **On-device semantic search**: search files, emails, and notes locally on consumer hardware.
- **Enterprise knowledge assistants**: retrieve internal legal, financial, and technical documents across languages.

## 🏃 How to run

<a href="https://colab.research.google.com/drive/1uLswYrRTNw4P2P2qZ8JG-b8j-KDkQqwL?usp=sharing"><img src="https://cdn-uploads.huggingface.co/production/uploads/61b8e2ba285851687028d395/vlOyMEjwHa_b_LXysEu2E.png" width=120 alt="Colab link"></a>

### Using Sentence Transformers

This model can be used as a multi-vector (ColBERT-style late interaction) retriever directly with [Sentence Transformers](https://www.sbert.net/) via the `MultiVectorEncoder`.

```bash
pip install "sentence-transformers>=6.0.0"
```

```python
from sentence_transformers import MultiVectorEncoder

model = MultiVectorEncoder("LiquidAI/LFM2.5-ColBERT-350M", trust_remote_code=True)

query = "Which planet is known as the Red Planet?"
documents = [
    "Venus is often called Earth's twin because of its similar size and proximity.",
    "Mars, known for its reddish appearance, is often referred to as the Red Planet.",
    "Jupiter, the largest planet in our solar system, has a prominent red spot.",
    "Saturn, famous for its rings, is sometimes mistaken for the Red Planet.",
]

query_embeddings = model.encode_query([query])
document_embeddings = model.encode_document(documents)
print(query_embeddings[0].shape, document_embeddings[0].shape)
# (32, 128) (17, 128)

# MaxSim late-interaction scoring (the Mars document ranks highest)
scores = model.similarity(query_embeddings, document_embeddings)
print(scores)
# tensor([[27.1621, 28.2578, 27.7266, 28.1992]])
```

### Using PyLate

Use this model with PyLate to index and retrieve documents. The index uses [FastPLAID](https://github.com/lightonai/fast-plaid) for efficient similarity search. First, install PyLate and transformers:

```bash
pip install -U pylate
```

#### Indexing documents

Load LFM2.5-ColBERT-350M and initialize the PLAID index, then encode and index your documents:

```python
from pylate import indexes, models, retrieve

# Step 1: Load the ColBERT model (trust_remote_code applies the bidirectional patches)
model = models.ColBERT(
    model_name_or_path="LiquidAI/LFM2.5-ColBERT-350M",
    trust_remote_code=True,
)
model.tokenizer.pad_token = model.tokenizer.eos_token

# Step 2: Initialize the PLAID index
index = indexes.PLAID(
    index_folder="pylate-index",
    index_name="index",
    override=True,  # This overwrites the existing index if any
)

# Step 3: Encode the documents
documents_ids = ["1", "2", "3"]
documents = ["document 1 text", "document 2 text", "document 3 text"]

documents_embeddings = model.encode(
    documents,
    batch_size=32,
    is_query=False,  # Ensure that it is set to False to indicate that these are documents, not queries
    show_progress_bar=True,
)

# Step 4: Add document embeddings to the index by providing embeddings and corresponding ids
index.add_documents(
    documents_ids=documents_ids,
    documents_embeddings=documents_embeddings,
)
```

Note that you do not have to recreate the index and encode the documents every time. Once you have created an index and added the documents, you can re-use the index later by loading it:

```python
# To load an index, simply instantiate it with the correct folder/name and without overriding it
index = indexes.PLAID(
    index_folder="pylate-index",
    index_name="index",
)
```

#### Retrieving top-k documents for queries

Once the documents are indexed, you can retrieve the top-k most relevant documents for a given set of queries. To do so, initialize the ColBERT retriever with the index you want to search in, encode the queries, and then retrieve the top-k documents to get the top matches ids and relevance scores:

```python
# Step 1: Initialize the ColBERT retriever
retriever = retrieve.ColBERT(index=index)

# Step 2: Encode the queries
queries_embeddings = model.encode(
    ["query for document 3", "query for document 1"],
    batch_size=32,
    is_query=True,  # Ensure that it is set to True to indicate that these are queries
    show_progress_bar=True,
)

# Step 3: Retrieve top-k documents
scores = retriever.retrieve(
    queries_embeddings=queries_embeddings,
    k=10,  # Retrieve the top 10 matches for each query
)
```

### Reranking

If you only want to use LFM2.5-ColBERT-350M to perform reranking on top of your first-stage retrieval pipeline without building an index, you can simply use the `rank` function and pass the queries and documents to rerank:

```python
from pylate import rank, models

queries = [
    "query A",
    "query B",
]

documents = [
    ["document A", "document B"],
    ["document 1", "document C", "document B"],
]

documents_ids = [
    [1, 2],
    [1, 3, 2],
]

model = models.ColBERT(
    model_name_or_path="LiquidAI/LFM2.5-ColBERT-350M",
    trust_remote_code=True,
)

queries_embeddings = model.encode(
    queries,
    is_query=True,
)

documents_embeddings = model.encode(
    documents,
    is_query=False,
)

reranked_documents = rank.rerank(
    documents_ids=documents_ids,
    queries_embeddings=queries_embeddings,
    documents_embeddings=documents_embeddings,
)
```

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

```
@misc{PyLate,
  title={PyLate: Flexible Training and Retrieval for Late Interaction Models},
  author={Chaffin, Antoine and Sourty, Raphaël},
  url={https://github.com/lightonai/pylate},
  year={2024}
}
```
