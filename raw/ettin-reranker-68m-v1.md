---
language:
- en
license: apache-2.0
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:143393475
- loss:MSELoss
base_model: jhu-clsp/ettin-encoder-68m
pipeline_tag: text-ranking
library_name: sentence-transformers
metrics:
- map
- mrr@10
- ndcg@10
model-index:
- name: ettin-reranker-68m-v1
  results:
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoMSMARCO R100
      type: NanoMSMARCO_R100
    metrics:
    - type: map
      value: 0.6173
      name: Map
    - type: mrr@10
      value: 0.6132
      name: Mrr@10
    - type: ndcg@10
      value: 0.6834
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoNFCorpus R100
      type: NanoNFCorpus_R100
    metrics:
    - type: map
      value: 0.3725
      name: Map
    - type: mrr@10
      value: 0.562
      name: Mrr@10
    - type: ndcg@10
      value: 0.4075
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoNQ R100
      type: NanoNQ_R100
    metrics:
    - type: map
      value: 0.7219
      name: Map
    - type: mrr@10
      value: 0.7526
      name: Mrr@10
    - type: ndcg@10
      value: 0.7746
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoFiQA2018 R100
      type: NanoFiQA2018_R100
    metrics:
    - type: map
      value: 0.538
      name: Map
    - type: mrr@10
      value: 0.6521
      name: Mrr@10
    - type: ndcg@10
      value: 0.5906
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoTouche2020 R100
      type: NanoTouche2020_R100
    metrics:
    - type: map
      value: 0.4771
      name: Map
    - type: mrr@10
      value: 0.8264
      name: Mrr@10
    - type: ndcg@10
      value: 0.5631
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoSciFact R100
      type: NanoSciFact_R100
    metrics:
    - type: map
      value: 0.7019
      name: Map
    - type: mrr@10
      value: 0.6999
      name: Mrr@10
    - type: ndcg@10
      value: 0.7462
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoHotpotQA R100
      type: NanoHotpotQA_R100
    metrics:
    - type: map
      value: 0.9324
      name: Map
    - type: mrr@10
      value: 0.99
      name: Mrr@10
    - type: ndcg@10
      value: 0.9583
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoArguAna R100
      type: NanoArguAna_R100
    metrics:
    - type: map
      value: 0.574
      name: Map
    - type: mrr@10
      value: 0.575
      name: Mrr@10
    - type: ndcg@10
      value: 0.6876
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoFEVER R100
      type: NanoFEVER_R100
    metrics:
    - type: map
      value: 0.9257
      name: Map
    - type: mrr@10
      value: 0.955
      name: Mrr@10
    - type: ndcg@10
      value: 0.9434
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoDBPedia R100
      type: NanoDBPedia_R100
    metrics:
    - type: map
      value: 0.6533
      name: Map
    - type: mrr@10
      value: 0.8846
      name: Mrr@10
    - type: ndcg@10
      value: 0.7253
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoClimateFEVER R100
      type: NanoClimateFEVER_R100
    metrics:
    - type: map
      value: 0.4863
      name: Map
    - type: mrr@10
      value: 0.7599
      name: Mrr@10
    - type: ndcg@10
      value: 0.5685
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoSCIDOCS R100
      type: NanoSCIDOCS_R100
    metrics:
    - type: map
      value: 0.2997
      name: Map
    - type: mrr@10
      value: 0.5042
      name: Mrr@10
    - type: ndcg@10
      value: 0.3472
      name: Ndcg@10
  - task:
      type: cross-encoder-reranking
      name: Cross Encoder Reranking
    dataset:
      name: NanoQuoraRetrieval R100
      type: NanoQuoraRetrieval_R100
    metrics:
    - type: map
      value: 0.9503
      name: Map
    - type: mrr@10
      value: 0.9733
      name: Mrr@10
    - type: ndcg@10
      value: 0.9683
      name: Ndcg@10
  - task:
      type: cross-encoder-nano-beir
      name: Cross Encoder Nano BEIR
    dataset:
      name: NanoBEIR R100 mean
      type: NanoBEIR_R100_mean
    metrics:
    - type: map
      value: 0.6347
      name: Map
    - type: mrr@10
      value: 0.7499
      name: Mrr@10
    - type: ndcg@10
      value: 0.6895
      name: Ndcg@10
---

# ettin-reranker-68m-v1

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model finetuned from [jhu-clsp/ettin-encoder-68m](https://huggingface.co/jhu-clsp/ettin-encoder-68m) on the [cross-encoder/ettin-reranker-v1-data](https://huggingface.co/datasets/cross-encoder/ettin-reranker-v1-data) dataset using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

See the [release blogpost](https://huggingface.co/blog/ettin-reranker) for details on the training recipe, evaluation results, and speed benchmarks against other public rerankers. The [Evaluation](#evaluation) section below also has the headline numbers.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
- **Base model:** [jhu-clsp/ettin-encoder-68m](https://huggingface.co/jhu-clsp/ettin-encoder-68m) <!-- at revision ac19ae4bc51093b31c475665ac872a936d056cc2 -->
- **Maximum Sequence Length:** 7999 tokens
- **Number of Output Labels:** 1 label
- **Supported Modality:** Text
- **Training Dataset:** [cross-encoder/ettin-reranker-v1-data](https://huggingface.co/datasets/cross-encoder/ettin-reranker-v1-data)
- **Language:** en
- **License:** apache-2.0

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Documentation:** [Cross Encoder Documentation](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Cross Encoders on Hugging Face](https://huggingface.co/models?library=sentence-transformers&other=cross-encoder)

### Full Model Architecture

```
CrossEncoder(
  (0): Transformer({'transformer_task': 'feature-extraction', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'last_hidden_state'}}, 'module_output_name': 'token_embeddings', 'architecture': 'ModernBertModel'})
  (1): Pooling({'embedding_dimension': 512, 'pooling_mode': 'cls', 'include_prompt': True})
  (2): Dense({'in_features': 512, 'out_features': 512, 'bias': False, 'activation_function': 'torch.nn.modules.activation.GELU', 'module_input_name': 'sentence_embedding', 'module_output_name': 'sentence_embedding'})
  (3): LayerNorm({'dimension': 512})
  (4): Dense({'in_features': 512, 'out_features': 1, 'bias': True, 'activation_function': 'torch.nn.modules.linear.Identity', 'module_input_name': 'sentence_embedding', 'module_output_name': 'scores'})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import CrossEncoder

# Download from the 🤗 Hub
model = CrossEncoder(
    "cross-encoder/ettin-reranker-68m-v1",
    model_kwargs={"dtype": "bfloat16", "attn_implementation": "flash_attention_2"},  # Optional: pip install kernels
)

# Get scores for pairs of inputs
query = "Which planet is known as the Red Planet?"
passages = [
    "Venus is often called Earth's twin because of its similar size and proximity.",
    "Mars, known for its reddish appearance, is often referred to as the Red Planet.",
    "Jupiter, the largest planet in our solar system, has a prominent red spot.",
    "Saturn, famous for its rings, is sometimes mistaken for the Red Planet.",
]
scores = model.predict([(query, passage) for passage in passages])
print(scores)
# [ 6.375  11.5     7.625  10.4375]

# Or rank passages by relevance to a single query
ranked = model.rank(query, passages)
print(ranked)
# [{'corpus_id': 1, 'score': np.float32(11.5)}, ...]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

## Evaluation

### MTEB(eng, v2) Retrieval

Each model in the ettin-reranker-v1 family was evaluated on the full [`MTEB(eng, v2)` Retrieval benchmark](https://github.com/embeddings-benchmark/mteb) (10 tasks, top-100 reranked) using MTEB's [two-stage reranking flow](https://embeddings-benchmark.github.io/mteb/get_started/advanced_usage/two_stage_reranking/), pairing each reranker with six embedding models that span the speed/quality spectrum.
The dashed retriever-only line in each chart below is the headline number to beat. Anything below it means the reranker actively hurts the pipeline on average:

| | |
|-|-|
| ![MTEB(eng, v2) Retrieval with static-retrieval-mrl-en-v1 + reranker](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/ettin-reranker/mteb_ndcg10_static-retrieval-mrl-en-v1.png) | ![MTEB(eng, v2) Retrieval with all-MiniLM-L6-v2 + reranker](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/ettin-reranker/mteb_ndcg10_all-MiniLM-L6-v2.png) |
| ![MTEB(eng, v2) Retrieval with bge-small-en-v1.5 + reranker](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/ettin-reranker/mteb_ndcg10_bge-small-en-v1.5.png) | ![MTEB(eng, v2) Retrieval with nomic-embed-text-v1.5 + reranker](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/ettin-reranker/mteb_ndcg10_nomic-embed-text-v1.5.png) |
| ![MTEB(eng, v2) Retrieval with embeddinggemma-300m + reranker](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/ettin-reranker/mteb_ndcg10_embeddinggemma-300m.png) | ![MTEB(eng, v2) Retrieval with jina-embeddings-v5-text-small-retrieval + reranker](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/ettin-reranker/mteb_ndcg10_jina-embeddings-v5-text-small-retrieval.png) |

<details><summary>Full table of results (click to expand)</summary>

Mean NDCG@10 over the 6 embedder pairings, sorted by MTEB. The released ettin-reranker-v1 family is in **bold**, and the teacher [`mixedbread-ai/mxbai-rerank-large-v2`](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v2) is <u>underlined</u>.

| Reranker | Params | MTEB(eng, v2) Retrieval NDCG@10 |
| --- | ---: | ---: |
| [`Qwen/Qwen3-Reranker-4B`](https://huggingface.co/Qwen/Qwen3-Reranker-4B)<sup>†</sup> | 4.02B | 0.6367 |
| <u>[`mixedbread-ai/mxbai-rerank-large-v2`](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v2)</u> | <u>1.54B</u> | <u>0.6115</u> |
| **[`cross-encoder/ettin-reranker-1b-v1`](https://huggingface.co/cross-encoder/ettin-reranker-1b-v1)** | **1.00B** | **0.6114** |
| **[`cross-encoder/ettin-reranker-400m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-400m-v1)** | **401M** | **0.6091** |
| **[`cross-encoder/ettin-reranker-150m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-150m-v1)** | **151M** | **0.5994** |
| [`Qwen/Qwen3-Reranker-0.6B`](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B) | 596M | 0.5940 |
| [`mixedbread-ai/mxbai-rerank-base-v2`](https://huggingface.co/mixedbread-ai/mxbai-rerank-base-v2) | 494M | 0.5920 |
| **[`cross-encoder/ettin-reranker-68m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-68m-v1)** | **68.6M** | **0.5915** |
| [`jinaai/jina-reranker-m0`](https://huggingface.co/jinaai/jina-reranker-m0) | 2.44B | 0.5856 |
| [`Alibaba-NLP/gte-reranker-modernbert-base`](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base) | 150M | 0.5843 |
| **[`cross-encoder/ettin-reranker-32m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-32m-v1)** | **32.8M** | **0.5779** |
| [`ibm-granite/granite-embedding-reranker-english-r2`](https://huggingface.co/ibm-granite/granite-embedding-reranker-english-r2) | 150M | 0.5656 |
| **[`cross-encoder/ettin-reranker-17m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-17m-v1)** | **17.6M** | **0.5576** |
| [`BAAI/bge-reranker-v2-m3`](https://huggingface.co/BAAI/bge-reranker-v2-m3) | 568M | 0.5526 |
| [`zeroentropy/zerank-2-reranker`](https://huggingface.co/zeroentropy/zerank-2-reranker)<sup>†</sup> | 4.02B | 0.5300 |
| [`BAAI/bge-reranker-large`](https://huggingface.co/BAAI/bge-reranker-large) | 560M | 0.5098 |
| [`cross-encoder/ms-marco-MiniLM-L6-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) | 22.7M | 0.5082 |
| [`cross-encoder/ms-marco-MiniLM-L12-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L12-v2) | 33.4M | 0.5066 |
| [`mixedbread-ai/mxbai-rerank-large-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v1) | 435M | 0.5063 |
| [`cross-encoder/ms-marco-MiniLM-L4-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L4-v2) | 19.2M | 0.4979 |
| [`mixedbread-ai/mxbai-rerank-xsmall-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-xsmall-v1) | 70.8M | 0.4968 |
| [`BAAI/bge-reranker-base`](https://huggingface.co/BAAI/bge-reranker-base) | 278M | 0.4890 |
| [`mixedbread-ai/mxbai-rerank-base-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-base-v1) | 184M | 0.4865 |

<sup>†</sup> Capped to `max_seq_length=8192` (the 4B Qwen3-based rerankers don't fit on a single H100 80GB at native context). Native-context evaluation is likely higher.

</details>

See the [release blogpost](https://huggingface.co/blog/ettin-reranker) for the full analysis and per-model commentary.

### Speed

All six released models were benchmarked against thirteen public rerankers on three hardware tiers, using [`sentence-transformers/natural-questions`](https://huggingface.co/datasets/sentence-transformers/natural-questions) at `max_length=512` with each model's best supported attention implementation. The full sweep over `fp32+SDPA`, `bf16+SDPA`, padded `bf16+FA2`, and unpadded `bf16+FA2` (showing why the ettin-reranker-v1 family is faster than other ModernBERT-based rerankers) is in the [release blogpost](https://huggingface.co/blog/ettin-reranker#speed). This table shows the throughput in pairs per second on a NVIDIA H100 80GB, all in `bfloat16`:

| Model | Params | Attn | pairs / second |
|---|---:|---|---|
| **[`cross-encoder/ettin-reranker-17m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-17m-v1)** | **17M** | FA2 | **7517** |
| **[`cross-encoder/ettin-reranker-32m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-32m-v1)** | **32M** | FA2 | **6602** |
| **[`cross-encoder/ettin-reranker-68m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-68m-v1)** | **68M** | FA2 | **4913** |
| [`cross-encoder/ms-marco-MiniLM-L4-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L4-v2) | 19M | FA2 | 4029 |
| [`cross-encoder/ms-marco-MiniLM-L6-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) | 22M | FA2 | 3817 |
| [`cross-encoder/ms-marco-MiniLM-L12-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L12-v2) | 33M | FA2 | 3311 |
| **[`cross-encoder/ettin-reranker-150m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-150m-v1)** | **150M** | FA2 | **3237** |
| [`BAAI/bge-reranker-base`](https://huggingface.co/BAAI/bge-reranker-base) | 278M | FA2 | 2858 |
| [`mixedbread-ai/mxbai-rerank-xsmall-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-xsmall-v1) | 70M | eager | 2636 |
| [`mixedbread-ai/mxbai-rerank-base-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-base-v1) | 184M | eager | 1953 |
| **[`cross-encoder/ettin-reranker-400m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-400m-v1)** | **400M** | FA2 | **1738** |
| [`BAAI/bge-reranker-large`](https://huggingface.co/BAAI/bge-reranker-large) | 560M | FA2 | 1659 |
| [`BAAI/bge-reranker-v2-m3`](https://huggingface.co/BAAI/bge-reranker-v2-m3) | 568M | FA2 | 1569 |
| [`Alibaba-NLP/gte-reranker-modernbert-base`](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base) | 150M | FA2 | 1418 |
| [`ibm-granite/granite-embedding-reranker-english-r2`](https://huggingface.co/ibm-granite/granite-embedding-reranker-english-r2) | 150M | FA2 | 1404 |
| **[`cross-encoder/ettin-reranker-1b-v1`](https://huggingface.co/cross-encoder/ettin-reranker-1b-v1)** | **1B** | FA2 | **928** |
| [`mixedbread-ai/mxbai-rerank-large-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v1) | 435M | eager | 867 |
| [`mixedbread-ai/mxbai-rerank-base-v2`](https://huggingface.co/mixedbread-ai/mxbai-rerank-base-v2) | 494M | FA2 | 809 |
| <u>[`mixedbread-ai/mxbai-rerank-large-v2`](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v2)</u> | <u>1.5B</u> | FA2 | <u>387</u> |

<details><summary>Same benchmark on a consumer GPU (RTX 3090, 24 GB)</summary>

| Model | Params | Best attn | pairs / second |
|---|---:|---|---:|
| **[`cross-encoder/ettin-reranker-17m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-17m-v1)** | **17M** | FA2 | **9008** |
| [`cross-encoder/ms-marco-MiniLM-L4-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L4-v2) | 19M | FA2 | 5071 |
| **[`cross-encoder/ettin-reranker-32m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-32m-v1)** | **32M** | FA2 | **4497** |
| [`cross-encoder/ms-marco-MiniLM-L6-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) | 22M | FA2 | 4234 |
| [`cross-encoder/ms-marco-MiniLM-L12-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L12-v2) | 33M | FA2 | 2847 |
| **[`cross-encoder/ettin-reranker-68m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-68m-v1)** | **68M** | FA2 | **1916** |
| [`mixedbread-ai/mxbai-rerank-xsmall-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-xsmall-v1) | 70M | eager | 1677 |
| [`BAAI/bge-reranker-base`](https://huggingface.co/BAAI/bge-reranker-base) | 278M | FA2 | 1329 |
| **[`cross-encoder/ettin-reranker-150m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-150m-v1)** | **150M** | FA2 | **982** |
| [`mixedbread-ai/mxbai-rerank-base-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-base-v1) | 184M | eager | 772 |
| [`ibm-granite/granite-embedding-reranker-english-r2`](https://huggingface.co/ibm-granite/granite-embedding-reranker-english-r2) | 150M | FA2 | 598 |
| [`Alibaba-NLP/gte-reranker-modernbert-base`](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base) | 150M | FA2 | 586 |
| [`BAAI/bge-reranker-large`](https://huggingface.co/BAAI/bge-reranker-large) | 560M | FA2 | 448 |
| [`BAAI/bge-reranker-v2-m3`](https://huggingface.co/BAAI/bge-reranker-v2-m3) | 568M | FA2 | 436 |
| **[`cross-encoder/ettin-reranker-400m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-400m-v1)** | **400M** | FA2 | **429** |
| [`mixedbread-ai/mxbai-rerank-large-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v1) | 435M | eager | 266 |
| [`mixedbread-ai/mxbai-rerank-base-v2`](https://huggingface.co/mixedbread-ai/mxbai-rerank-base-v2) | 494M | FA2 | 221 |
| **[`cross-encoder/ettin-reranker-1b-v1`](https://huggingface.co/cross-encoder/ettin-reranker-1b-v1)** | **1B** | FA2 | **189** |
| <u>[`mixedbread-ai/mxbai-rerank-large-v2`](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v2)</u> | <u>1.5B</u> | FA2 | <u>69</u> |

</details>

<details><summary>Same benchmark on CPU (Intel Core i7-13700K)</summary>

| Model | Params | Best attn | pairs / second |
|---|---:|---|---:|
| **[`cross-encoder/ettin-reranker-17m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-17m-v1)** | **17M** | SDPA | **267.4** |
| [`cross-encoder/ms-marco-MiniLM-L4-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L4-v2) | 19M | SDPA | 206.2 |
| [`cross-encoder/ms-marco-MiniLM-L6-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) | 22M | SDPA | 143.9 |
| **[`cross-encoder/ettin-reranker-32m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-32m-v1)** | **32M** | SDPA | **92.5** |
| [`cross-encoder/ms-marco-MiniLM-L12-v2`](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L12-v2) | 33M | SDPA | 75.9 |
| [`mixedbread-ai/mxbai-rerank-xsmall-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-xsmall-v1) | 70M | eager | 38.9 |
| **[`cross-encoder/ettin-reranker-68m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-68m-v1)** | **68M** | SDPA | **31.2** |
| [`BAAI/bge-reranker-base`](https://huggingface.co/BAAI/bge-reranker-base) | 278M | SDPA | 19.2 |
| [`Alibaba-NLP/gte-reranker-modernbert-base`](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base) | 150M | SDPA | 14.7 |
| [`ibm-granite/granite-embedding-reranker-english-r2`](https://huggingface.co/ibm-granite/granite-embedding-reranker-english-r2) | 150M | SDPA | 14.5 |
| **[`cross-encoder/ettin-reranker-150m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-150m-v1)** | **150M** | SDPA | **14.0** |
| [`mixedbread-ai/mxbai-rerank-base-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-base-v1) | 184M | eager | 13.4 |
| [`BAAI/bge-reranker-large`](https://huggingface.co/BAAI/bge-reranker-large) | 560M | SDPA | 6.2 |
| [`BAAI/bge-reranker-v2-m3`](https://huggingface.co/BAAI/bge-reranker-v2-m3) | 568M | SDPA | 6.0 |
| **[`cross-encoder/ettin-reranker-400m-v1`](https://huggingface.co/cross-encoder/ettin-reranker-400m-v1)** | **400M** | SDPA | **5.2** |
| [`mixedbread-ai/mxbai-rerank-large-v1`](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v1) | 435M | eager | 4.3 |
| [`mixedbread-ai/mxbai-rerank-base-v2`](https://huggingface.co/mixedbread-ai/mxbai-rerank-base-v2) | 494M | SDPA | 3.5 |
| **[`cross-encoder/ettin-reranker-1b-v1`](https://huggingface.co/cross-encoder/ettin-reranker-1b-v1)** | **1B** | SDPA | **2.1** |

</details>


### Metrics

#### Cross Encoder Reranking

* Datasets: `NanoMSMARCO_R100`, `NanoNFCorpus_R100`, `NanoNQ_R100`, `NanoFiQA2018_R100`, `NanoTouche2020_R100`, `NanoSciFact_R100`, `NanoHotpotQA_R100`, `NanoArguAna_R100`, `NanoFEVER_R100`, `NanoDBPedia_R100`, `NanoClimateFEVER_R100`, `NanoSCIDOCS_R100` and `NanoQuoraRetrieval_R100`
* Evaluated with [<code>CrossEncoderRerankingEvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CrossEncoderRerankingEvaluator) with these parameters:
  ```json
  {
      "at_k": 10,
      "always_rerank_positives": true
  }
  ```

| Metric      | NanoMSMARCO_R100     | NanoNFCorpus_R100    | NanoNQ_R100          | NanoFiQA2018_R100    | NanoTouche2020_R100  | NanoSciFact_R100     | NanoHotpotQA_R100    | NanoArguAna_R100     | NanoFEVER_R100       | NanoDBPedia_R100     | NanoClimateFEVER_R100 | NanoSCIDOCS_R100     | NanoQuoraRetrieval_R100 |
|:------------|:---------------------|:---------------------|:---------------------|:---------------------|:---------------------|:---------------------|:---------------------|:---------------------|:---------------------|:---------------------|:----------------------|:---------------------|:------------------------|
| map         | 0.6173 (+0.1277)     | 0.3725 (+0.1115)     | 0.7219 (+0.3022)     | 0.5380 (+0.1729)     | 0.4771 (-0.0727)     | 0.7019 (+0.0321)     | 0.9324 (+0.1641)     | 0.5740 (+0.1633)     | 0.9257 (+0.1538)     | 0.6533 (+0.1414)     | 0.4863 (+0.2461)      | 0.2997 (+0.0254)     | 0.9503 (+0.1195)        |
| mrr@10      | 0.6132 (+0.1357)     | 0.5620 (+0.0622)     | 0.7526 (+0.3259)     | 0.6521 (+0.1613)     | 0.8264 (-0.0807)     | 0.6999 (+0.0218)     | 0.9900 (+0.0671)     | 0.5750 (+0.1820)     | 0.9550 (+0.1750)     | 0.8846 (+0.0839)     | 0.7599 (+0.3560)      | 0.5042 (-0.0553)     | 0.9733 (+0.1052)        |
| **ndcg@10** | **0.6834 (+0.1430)** | **0.4075 (+0.0824)** | **0.7746 (+0.2739)** | **0.5906 (+0.1532)** | **0.5631 (-0.1307)** | **0.7462 (+0.0363)** | **0.9583 (+0.1306)** | **0.6876 (+0.1988)** | **0.9434 (+0.1340)** | **0.7253 (+0.1110)** | **0.5685 (+0.2508)**  | **0.3472 (+0.0121)** | **0.9683 (+0.0997)**    |

#### Cross Encoder Nano BEIR

* Dataset: `NanoBEIR_R100_mean`
* Evaluated with [<code>CrossEncoderNanoBEIREvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CrossEncoderNanoBEIREvaluator) with these parameters:
  ```json
  {
      "dataset_names": [
          "msmarco",
          "nfcorpus",
          "nq",
          "fiqa2018",
          "touche2020",
          "scifact",
          "hotpotqa",
          "arguana",
          "fever",
          "dbpedia",
          "climatefever",
          "scidocs",
          "quoraretrieval"
      ],
      "dataset_id": "sentence-transformers/NanoBEIR-en",
      "rerank_k": 100,
      "at_k": 10,
      "always_rerank_positives": true
  }
  ```

| Metric      | Value                |
|:------------|:---------------------|
| map         | 0.6347 (+0.1298)     |
| mrr@10      | 0.7499 (+0.1185)     |
| **ndcg@10** | **0.6895 (+0.1150)** |

> [!NOTE]
> The [release blogpost](https://huggingface.co/blog/ettin-reranker) quotes a slightly higher NanoBEIR mean NDCG@10 of `0.6915` for this model, computed in `fp32` rather than the `bfloat16` used by the training-time evaluation above. Both numbers are valid.

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### ettin-reranker-v1-data

* Dataset: [cross-encoder/ettin-reranker-v1-data](https://huggingface.co/datasets/cross-encoder/ettin-reranker-v1-data)
* Size: 143,393,475 training samples
* Columns: <code>query</code>, <code>document</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | query                                                                                           | document                                                                                          | label                                                              |
  |:--------|:------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------|
  | type    | string                                                                                          | string                                                                                            | float                                                              |
  | details | <ul><li>min: 26 characters</li><li>mean: 55.52 characters</li><li>max: 249 characters</li></ul> | <ul><li>min: 63 characters</li><li>mean: 659.91 characters</li><li>max: 3975 characters</li></ul> | <ul><li>min: -2.94</li><li>mean: 8.51</li><li>max: 13.88</li></ul> |
* Samples:
  | query                                                                                         | document                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | label             |
  |:----------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------|
  | <code>Help me with my Reborn performance</code>                                               | <code>I was reading the comment section for Dotacinema's world of dota video, and a bunch of people were complaining how there were a lot of bugs and some talked about PERFORMANCE ISSUES. But there were also people saying that reborn has actually IMPROVED their gameplay?<br><br><br>I am one of those people who is running into performance issues and would desperately like to know how some are getting BETTER performance while others like me are getting worse. I'm not complaining about bugs, I'm complaing about framerate, I use to get 60 fps solid in source 1 but I now have 40 or at worst 30 fps in source 2.<br>I have an i3 processor/gtx560ti/16gb RAM<br><br>i dont think it's a potato pc, so I dont know what's happening, I cleaned my computer recently so dust isnt affecting anything in anyway.<br>So if you gained or had IMPROVED performance in source 2 please list the settings you are enabling, so I can see where I am at fault. (v sync is off btw)<br><br>TLDR: Have bad performance now from source 2, if you have good p...</code> | <code>9.5</code>  |
  | <code>Really wanna try out the game and expansion, ~$60 is hefty. Likelihood of sales?</code> | <code>As per title, steam sells the game and its expansions for $60 total. Heavy price to drop. Are there sales on any other website? This game looks fantastic to immerse in otherwise and I'm pleased that this subreddit has at least some attention to help out new folks!</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | <code>9.25</code> |
  | <code>Your Avatar. [MGSV Spoilers]</code>                                                     | <code>Was anyone else suprised he actually replaces the snake model in some cutscenes. I've only tried the first Quiet cutscenes, i was just amazed I haven't seen anybody else say this yet.<br>Sorry if repost.</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | <code>5.25</code> |
* Loss: [<code>MSELoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#mseloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity"
  }
  ```

### Evaluation Dataset

#### ettin-reranker-v1-data

* Dataset: [cross-encoder/ettin-reranker-v1-data](https://huggingface.co/datasets/cross-encoder/ettin-reranker-v1-data)
* Size: 5,000 evaluation samples
* Columns: <code>query</code>, <code>document</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | query                                                                                           | document                                                                                        | label                                                              |
  |:--------|:------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------|
  | type    | string                                                                                          | string                                                                                          | float                                                              |
  | details | <ul><li>min: 14 characters</li><li>mean: 52.62 characters</li><li>max: 168 characters</li></ul> | <ul><li>min: 11 characters</li><li>mean: 50.12 characters</li><li>max: 184 characters</li></ul> | <ul><li>min: 4.44</li><li>mean: 13.49</li><li>max: 18.62</li></ul> |
* Samples:
  | query                                                             | document                                                                               | label                |
  |:------------------------------------------------------------------|:---------------------------------------------------------------------------------------|:---------------------|
  | <code>Why do we need binomial distribution?</code>                | <code>Why is the binomial distribution important?</code>                               | <code>11.375</code>  |
  | <code>I already have Windows 10, can I delete Windows.old?</code> | <code>After resetting windows 10, can I safely delete the "old windows" folder?</code> | <code>10.875</code>  |
  | <code>How can guys last longer during sex?</code>                 | <code>How do men last longer in bed?</code>                                            | <code>10.8125</code> |
* Loss: [<code>MSELoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#mseloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity"
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 1
- `learning_rate`: 3e-05
- `warmup_steps`: 0.03
- `bf16`: True
- `per_device_eval_batch_size`: 16
- `load_best_model_at_end`: True
- `seed`: 12

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 1
- `max_steps`: -1
- `learning_rate`: 3e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0.03
- `optim`: adamw_torch
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1.0
- `label_smoothing_factor`: 0.0
- `bf16`: True
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: None
- `trackio_bucket_id`: None
- `trackio_static_space_id`: None
- `per_device_eval_batch_size`: 16
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: True
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 12
- `data_seed`: None
- `use_cpu`: False
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: True
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_static_graph`: None
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: []
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step   | Training Loss | Validation Loss | NanoMSMARCO_R100_ndcg@10 | NanoNFCorpus_R100_ndcg@10 | NanoNQ_R100_ndcg@10 | NanoFiQA2018_R100_ndcg@10 | NanoTouche2020_R100_ndcg@10 | NanoSciFact_R100_ndcg@10 | NanoHotpotQA_R100_ndcg@10 | NanoArguAna_R100_ndcg@10 | NanoFEVER_R100_ndcg@10 | NanoDBPedia_R100_ndcg@10 | NanoClimateFEVER_R100_ndcg@10 | NanoSCIDOCS_R100_ndcg@10 | NanoQuoraRetrieval_R100_ndcg@10 | NanoBEIR_R100_mean_ndcg@10 |
|:------:|:------:|:-------------:|:---------------:|:------------------------:|:-------------------------:|:-------------------:|:-------------------------:|:---------------------------:|:------------------------:|:-------------------------:|:------------------------:|:----------------------:|:------------------------:|:-----------------------------:|:------------------------:|:-------------------------------:|:--------------------------:|
| -1     | -1     | -             | -               | 0.0703 (-0.4701)         | 0.2412 (-0.0838)          | 0.0100 (-0.4906)    | 0.0506 (-0.3868)          | 0.1908 (-0.5030)            | 0.0301 (-0.6798)         | 0.0540 (-0.7737)          | 0.0440 (-0.4448)         | 0.0708 (-0.7387)       | 0.2433 (-0.3711)         | 0.0554 (-0.2623)              | 0.1278 (-0.2073)         | 0.0374 (-0.8313)                | 0.0943 (-0.4803)           |
| 0.0000 | 1      | 82.9845       | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.0250 | 14004  | 4.2695        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.0500 | 28007  | -             | 0.9225          | 0.6956 (+0.1552)         | 0.4356 (+0.1106)          | 0.7688 (+0.2681)    | 0.5333 (+0.0959)          | 0.5766 (-0.1172)            | 0.7555 (+0.0456)         | 0.9375 (+0.1098)          | 0.6710 (+0.1822)         | 0.9266 (+0.1172)       | 0.6903 (+0.0759)         | 0.5359 (+0.2182)              | 0.4009 (+0.0658)         | 0.9550 (+0.0863)                | 0.6833 (+0.1087)           |
| 0.0500 | 28008  | 1.3556        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.0750 | 42012  | 1.1872        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.1000 | 56014  | -             | 0.7973          | 0.6973 (+0.1569)         | 0.4100 (+0.0850)          | 0.7418 (+0.2411)    | 0.5121 (+0.0747)          | 0.5654 (-0.1284)            | 0.7504 (+0.0405)         | 0.9430 (+0.1153)          | 0.6897 (+0.2009)         | 0.9315 (+0.1221)       | 0.7047 (+0.0903)         | 0.5256 (+0.2078)              | 0.3979 (+0.0628)         | 0.9533 (+0.0846)                | 0.6787 (+0.1041)           |
| 0.1000 | 56016  | 1.1057        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.1250 | 70020  | 1.0520        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.1500 | 84021  | -             | 0.7338          | 0.7080 (+0.1676)         | 0.4309 (+0.1058)          | 0.7508 (+0.2502)    | 0.5368 (+0.0993)          | 0.5610 (-0.1328)            | 0.7300 (+0.0201)         | 0.9576 (+0.1299)          | 0.6945 (+0.2057)         | 0.9294 (+0.1200)       | 0.7097 (+0.0953)         | 0.5182 (+0.2005)              | 0.4058 (+0.0707)         | 0.9545 (+0.0858)                | 0.6836 (+0.1091)           |
| 0.1500 | 84024  | 1.0131        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.1750 | 98028  | 0.9822        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.2000 | 112028 | -             | 0.6552          | 0.7049 (+0.1645)         | 0.4210 (+0.0960)          | 0.7743 (+0.2737)    | 0.5139 (+0.0765)          | 0.5534 (-0.1404)            | 0.7315 (+0.0216)         | 0.9479 (+0.1201)          | 0.6923 (+0.2035)         | 0.9417 (+0.1323)       | 0.7163 (+0.1020)         | 0.5361 (+0.2184)              | 0.3778 (+0.0427)         | 0.9533 (+0.0846)                | 0.6819 (+0.1073)           |
| 0.2000 | 112032 | 0.9533        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.2250 | 126036 | 0.9289        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.2500 | 140035 | -             | 0.6013          | 0.6697 (+0.1293)         | 0.4329 (+0.1079)          | 0.7722 (+0.2715)    | 0.5643 (+0.1269)          | 0.5673 (-0.1265)            | 0.7402 (+0.0303)         | 0.9294 (+0.1017)          | 0.6890 (+0.2002)         | 0.9366 (+0.1271)       | 0.7153 (+0.1010)         | 0.5545 (+0.2368)              | 0.3771 (+0.0419)         | 0.9642 (+0.0955)                | 0.6856 (+0.1111)           |
| 0.2500 | 140040 | 0.9094        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.2750 | 154044 | 0.8895        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.3000 | 168042 | -             | 0.5823          | 0.6875 (+0.1471)         | 0.4295 (+0.1044)          | 0.7986 (+0.2979)    | 0.5681 (+0.1307)          | 0.5577 (-0.1361)            | 0.7287 (+0.0188)         | 0.9548 (+0.1270)          | 0.6830 (+0.1942)         | 0.9340 (+0.1246)       | 0.7235 (+0.1091)         | 0.5430 (+0.2253)              | 0.3649 (+0.0298)         | 0.9648 (+0.0961)                | 0.6876 (+0.1130)           |
| 0.3000 | 168048 | 0.8758        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.3250 | 182052 | 0.8595        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.3500 | 196049 | -             | 0.5575          | 0.7113 (+0.1709)         | 0.4263 (+0.1013)          | 0.7836 (+0.2829)    | 0.5835 (+0.1461)          | 0.5618 (-0.1320)            | 0.7348 (+0.0249)         | 0.9573 (+0.1296)          | 0.7017 (+0.2129)         | 0.9418 (+0.1323)       | 0.7099 (+0.0956)         | 0.5519 (+0.2342)              | 0.3760 (+0.0409)         | 0.9701 (+0.1014)                | 0.6931 (+0.1185)           |
| 0.3500 | 196056 | 0.8429        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.3750 | 210060 | 0.8316        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.4000 | 224056 | -             | 0.5408          | 0.6984 (+0.1579)         | 0.4353 (+0.1103)          | 0.7640 (+0.2634)    | 0.5745 (+0.1371)          | 0.5504 (-0.1434)            | 0.7442 (+0.0343)         | 0.9610 (+0.1333)          | 0.6955 (+0.2067)         | 0.9240 (+0.1146)       | 0.7232 (+0.1088)         | 0.5655 (+0.2477)              | 0.3688 (+0.0337)         | 0.9691 (+0.1004)                | 0.6903 (+0.1158)           |
| 0.4000 | 224064 | 0.8181        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.4250 | 238068 | 0.8067        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.4500 | 252063 | -             | 0.5930          | 0.6835 (+0.1431)         | 0.4318 (+0.1067)          | 0.7973 (+0.2967)    | 0.5764 (+0.1390)          | 0.5691 (-0.1247)            | 0.7294 (+0.0195)         | 0.9571 (+0.1293)          | 0.6813 (+0.1925)         | 0.9400 (+0.1306)       | 0.7161 (+0.1018)         | 0.5495 (+0.2317)              | 0.3607 (+0.0256)         | 0.9710 (+0.1023)                | 0.6895 (+0.1149)           |
| 0.4500 | 252072 | 0.7950        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.4750 | 266076 | 0.7870        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.5000 | 280070 | -             | 0.5138          | 0.6906 (+0.1502)         | 0.4454 (+0.1203)          | 0.7796 (+0.2790)    | 0.5843 (+0.1469)          | 0.5579 (-0.1359)            | 0.7200 (+0.0101)         | 0.9546 (+0.1269)          | 0.7131 (+0.2243)         | 0.9376 (+0.1282)       | 0.7181 (+0.1038)         | 0.5631 (+0.2454)              | 0.3679 (+0.0328)         | 0.9626 (+0.0939)                | 0.6919 (+0.1174)           |
| 0.5000 | 280080 | 0.7760        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.5250 | 294084 | 0.7680        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.5500 | 308077 | -             | 0.5217          | 0.6993 (+0.1589)         | 0.4477 (+0.1226)          | 0.7827 (+0.2821)    | 0.5833 (+0.1459)          | 0.5589 (-0.1349)            | 0.7332 (+0.0233)         | 0.9536 (+0.1259)          | 0.6676 (+0.1787)         | 0.9317 (+0.1222)       | 0.7247 (+0.1103)         | 0.5592 (+0.2415)              | 0.3530 (+0.0179)         | 0.9627 (+0.0940)                | 0.6890 (+0.1145)           |
| 0.5500 | 308088 | 0.7589        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.5750 | 322092 | 0.7509        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.6000 | 336084 | -             | 0.5018          | 0.6959 (+0.1555)         | 0.4317 (+0.1066)          | 0.7696 (+0.2689)    | 0.5909 (+0.1535)          | 0.5497 (-0.1441)            | 0.7242 (+0.0143)         | 0.9528 (+0.1251)          | 0.6652 (+0.1764)         | 0.9366 (+0.1272)       | 0.7291 (+0.1147)         | 0.5675 (+0.2498)              | 0.3478 (+0.0127)         | 0.9581 (+0.0894)                | 0.6861 (+0.1115)           |
| 0.6000 | 336096 | 0.7432        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.6250 | 350100 | 0.7350        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.6500 | 364091 | -             | 0.5098          | 0.6871 (+0.1467)         | 0.4322 (+0.1071)          | 0.7743 (+0.2737)    | 0.5893 (+0.1519)          | 0.5496 (-0.1442)            | 0.7447 (+0.0348)         | 0.9567 (+0.1290)          | 0.7018 (+0.2130)         | 0.9364 (+0.1270)       | 0.7274 (+0.1130)         | 0.5551 (+0.2374)              | 0.3567 (+0.0215)         | 0.9613 (+0.0926)                | 0.6902 (+0.1157)           |
| 0.6500 | 364104 | 0.7290        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.6750 | 378108 | 0.7233        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.7000 | 392098 | -             | 0.4997          | 0.6928 (+0.1524)         | 0.4211 (+0.0961)          | 0.7845 (+0.2839)    | 0.5891 (+0.1517)          | 0.5568 (-0.1370)            | 0.7451 (+0.0352)         | 0.9530 (+0.1253)          | 0.6800 (+0.1912)         | 0.9364 (+0.1270)       | 0.7244 (+0.1100)         | 0.5587 (+0.2409)              | 0.3581 (+0.0229)         | 0.9620 (+0.0934)                | 0.6894 (+0.1148)           |
| 0.7000 | 392112 | 0.7151        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.7250 | 406116 | 0.7108        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.7500 | 420105 | -             | 0.4818          | 0.6989 (+0.1585)         | 0.4118 (+0.0868)          | 0.7706 (+0.2699)    | 0.5871 (+0.1497)          | 0.5466 (-0.1472)            | 0.7432 (+0.0333)         | 0.9561 (+0.1284)          | 0.6731 (+0.1843)         | 0.9341 (+0.1247)       | 0.7184 (+0.1040)         | 0.5656 (+0.2479)              | 0.3535 (+0.0184)         | 0.9697 (+0.1011)                | 0.6868 (+0.1123)           |
| 0.7500 | 420120 | 0.7037        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.7750 | 434124 | 0.6982        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.8000 | 448112 | -             | 0.4681          | 0.6900 (+0.1496)         | 0.4205 (+0.0955)          | 0.7730 (+0.2723)    | 0.5925 (+0.1551)          | 0.5640 (-0.1298)            | 0.7385 (+0.0286)         | 0.9573 (+0.1296)          | 0.6994 (+0.2105)         | 0.9406 (+0.1312)       | 0.7262 (+0.1118)         | 0.5533 (+0.2356)              | 0.3496 (+0.0145)         | 0.9651 (+0.0964)                | 0.6900 (+0.1155)           |
| 0.8000 | 448128 | 0.6938        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.8250 | 462132 | 0.6882        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.8500 | 476119 | -             | 0.4709          | 0.6890 (+0.1485)         | 0.4163 (+0.0913)          | 0.7757 (+0.2751)    | 0.5894 (+0.1520)          | 0.5566 (-0.1372)            | 0.7447 (+0.0348)         | 0.9583 (+0.1306)          | 0.6830 (+0.1942)         | 0.9432 (+0.1338)       | 0.7362 (+0.1218)         | 0.5632 (+0.2455)              | 0.3468 (+0.0117)         | 0.9666 (+0.0979)                | 0.6899 (+0.1154)           |
| 0.8500 | 476136 | 0.6829        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.8750 | 490140 | 0.6775        | -               | -                        | -                         | -                   | -                         | -                           | -                        | -                         | -                        | -                      | -                        | -                             | -                        | -                               | -                          |
| 0.9000 | 504126 | -             | 0.4578          | 0.6834 (+0.1430)         | 0.4075 (+0.0824)          | 0.7746 (+0.2739)    | 0.5906 (+0.1532)          | 0.5631 (-0.1307)            | 0.7462 (+0.0363)         | 0.9583 (+0.1306)          | 0.6876 (+0.1988)         | 0.9434 (+0.1340)       | 0.7253 (+0.1110)         | 0.5685 (+0.2508)              | 0.3472 (+0.0121)         | 0.9683 (+0.0997)                | 0.6895 (+0.1150)           |


### Training Time
- **Training**: 11.2 hours
- **Evaluation**: 9.2 minutes
- **Total**: 11.3 hours

### Framework Versions
- Python: 3.11.15
- Sentence Transformers: 5.4.1
- Transformers: 5.7.0
- PyTorch: 2.7.0+cu126
- Accelerate: 1.13.0
- Datasets: 4.8.5
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Ettin Reranker Blogpost
```bibtex
@misc{aarsen2026ettin-reranker,
    title = "Introducing the Ettin Reranker Family",
    author = "Aarsen, Tom",
    year = "2026",
    publisher = "Hugging Face",
    url = "https://huggingface.co/blog/ettin-reranker",
}
```

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->