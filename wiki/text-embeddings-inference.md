---
type: Concept
title: Text Embeddings Inference (TEI)
description: Hugging Face's Rust serving toolkit for open text-embedding, reranker, sequence-classification, and SPLADE models, with documented architecture support, pooling overrides, and token-based dynamic batching.
tags: [embedding, reranking, serving, inference, deployment]
status: stable
created: 2026-10-04
generated: { by: llm-wiki-agent/1, at: 2026-10-04T09:52:00Z }
stale_after: 2027-01-04
sources:
  - id: tei-readme
    resource: ../raw/text-embeddings-inference.md
    kind: documentation
    title: Text Embeddings Inference README (v1.9 images)
---

# Text Embeddings Inference (TEI)

Text Embeddings Inference (TEI) is Hugging Face's toolkit for deploying and serving open-source text-embedding and sequence-classification models. It runs a `text-embeddings-router` server with HTTP and optional gRPC endpoints for dense embeddings, reranking, classification, and SPLADE sparse embeddings. For model selection, it defines which encoder architectures can be served without a model-graph compilation step, how pooling and prompts are applied, and which hardware constraints hold. All claims below are **Reported** by the upstream README; nothing was executed here. (README introduction and feature list) [^tei-readme]

## Model compatibility

| Role | Architectures listed by TEI | Examples named in the README |
| --- | --- | --- |
| Text embeddings | Nomic, BERT, CamemBERT, XLM-RoBERTa (absolute positions); JinaBERT (ALiBi); Mistral, Alibaba GTE, Qwen2 (RoPE); MPNet, ModernBERT, Qwen3, Gemma3 | [Qwen3-Embedding-8B](qwen3-embedding-8b.md), [Qwen3-Embedding-4B](qwen3-embedding-4b.md), [Qwen3-Embedding-0.6B](qwen3-embedding-0-6b.md), [EmbeddingGemma 300M](embeddinggemma-300m.md) (gated), gte-Qwen2, multilingual-e5-large-instruct, Snowflake Arctic Embed v2.0, nomic-embed-text v1/v1.5/v2-moe, jina-embeddings-v2, voyage-4-nano |
| Re-ranking | Sequence-classification cross-encoders: CamemBERT, XLM-RoBERTa, GTE, ModernBERT | BAAI/bge-reranker-large/base, gte-multilingual-reranker-base, gte-reranker-modernbert-base |
| Sparse | SPLADE pooling on BERT and DistilBERT MaskedLM (`ForMaskedLM`) models | naver/efficient-splade-VI-BT-large-query |

Source: (README §Supported Models, §Using Re-rankers models, §Using SPLADE pooling) [^tei-readme]

- The supported-model table has an "MTEB Rank" column with no snapshot date or benchmark version. Under this wiki's benchmark rules, those ranks are **not** comparable with dated leaderboard snapshots such as the [MTEB Multilingual v2 leaderboard snapshot](mteb-multilingual-v2-leaderboard-snapshot.md), so they are not recorded here. (README §Supported Models, §Using Re-rankers models, §Using SPLADE pooling) [^tei-readme]
- TEI defines re-rankers as single-class sequence-classification cross-encoders that score query–text similarity. The README's examples omit LLM-based point-wise rerankers such as the Qwen3-Reranker family (see [reranker model comparison](reranker-model-comparison.md)), as well as multimodal and late-interaction models. This source does not establish whether TEI can serve them (**Unverified**; **Synthesis**). (README §Supported Models, §Using Re-rankers models, §Using SPLADE pooling) [^tei-readme]
- Compatible Hub models carry the `text-embeddings-inference` tag. A local directory saved by Transformers or Sentence Transformers `save_pretrained(...)` also works. (README §Docker, `text-embeddings-router --help`) [^tei-readme]

## Serving behavior relevant to models

- **Pooling:** TEI reads pooling from the model's `1_Pooling/config.json` unless `--pooling` overrides it with `cls`, `mean`, `splade` (MaskedLM only), or `last-token`. Last-token pooling corresponds to decoder embedders such as Qwen3-Embedding's EOS pooling (pairing is **Synthesis**). (README §Docker, `text-embeddings-router --help`) [^tei-readme]
- **Prompts:** `--default-prompt-name` selects a key from the Sentence Transformers `prompts` config; `--default-prompt` prepends literal text. The two flags are mutually exclusive, and no prompt is applied by default. This matters for instruction-aware models that need query instructions to reach their expected retrieval quality. (README §Docker, `text-embeddings-router --help`) [^tei-readme]
- **Dense projection:** `--dense-path` selects an extra `2_Dense` (or `2_Dense_<dims>`) Linear module, for example to choose a dimension variant. It applies only to the `candle` backend. (README §Docker, `text-embeddings-router --help`) [^tei-readme]
- **Batching and limits:** `--max-batch-tokens` (default 16,384) controls token-based dynamic batching. The README calls it the critical hardware-utilization control and says it must be tuned by hand. Other defaults are 512 maximum concurrent requests, 32 inputs per client request, a 2 MB payload limit, and auto-truncation enabled. With truncation disabled, the server refuses to start if the model's maximum input length exceeds `--max-batch-tokens`. (README §Docker, `text-embeddings-router --help`) [^tei-readme]
- **Precision:** `--dtype` accepts `float16` or `float32`, and the ROCm example uses `bfloat16`. Check this against model-specific limits; for example, EmbeddingGemma's card does not support `float16` activations (**Synthesis**). (README §AMD Instinct GPUs (ROCm)) [^tei-readme]

## Endpoints and operations

| Endpoint | Purpose |
| --- | --- |
| `/embed` | Dense embeddings |
| `/rerank` | Score a query against a list of texts |
| `/predict` | Sequence-classification outputs |
| `/embed_sparse` | SPLADE sparse embeddings |
| gRPC `tei.v1.Embed/Embed` | Alternative API through `-grpc` image tags |

OpenAI-compatible HTTP endpoints use `--served-model-name`. The server also provides an OpenAPI `/docs` route, optional bearer-token API-key authorization, OpenTelemetry tracing, and Prometheus metrics (default port 9000). Gated or private models need a Hugging Face token. For air-gapped deployment, mount pre-downloaded weights and point `--model-id` at the local path. (README §Docker, §API documentation, §Using a private or gated model, §Air gapped deployment, §Using Sequence Classification models, §Distributed Tracing, §gRPC) [^tei-readme]

## Hardware and installation

- Version 1.9 Docker images target CPU (x86_64 and aarch64), Turing (experimental, with Flash Attention off by default because of precision issues), Ampere 8.0/8.6, Ada Lovelace, Hopper, and Blackwell 10.0/12.0/12.1 (experimental). Volta is not supported. (README §Docker Images) [^tei-readme]
- CUDA builds require compute capability ≥7.5 and drivers compatible with CUDA 12.2+. CPU builds use ONNX (recommended on x86), Intel MKL, or Metal backends. Apple Silicon has a Homebrew binary with Metal acceleration, and AMD Instinct MI200/MI300 GPUs are supported via ROCm. (README §Docker GPU note, §Local install, §AMD Instinct GPUs (ROCm)) [^tei-readme]
- The README also claims no graph-compilation step, small images with fast boot, Flash Attention/Candle/cuBLASLt kernels, and Safetensors and ONNX weight loading. (README introduction and feature list) [^tei-readme]

## Limits

- The README's headline latency and throughput benchmark (BAAI/bge-base-en-v1.5 on an NVIDIA A10, sequence length 512, batch sizes 1 and 32) exists only as images (`assets/bs*-*.png`) that are absent from `raw/`. No performance numbers are recorded here. (README introduction and feature list) [^tei-readme]
- No repository revision or capture date is recorded. The version scope is inferred from the `1.9` Docker tags, and compatibility and defaults are time-sensitive (`stale_after` is set). TEI's code, protobuf definition, and linked guides were not inspected.

## Relationships

- **Uses:** pooling configuration and prompts from Sentence Transformers model packaging.
- **Serves:** [Qwen3-Embedding-0.6B](qwen3-embedding-0-6b.md), [Qwen3-Embedding-4B](qwen3-embedding-4b.md), [Qwen3-Embedding-8B](qwen3-embedding-8b.md), and [EmbeddingGemma 300M](embeddinggemma-300m.md) are listed as supported examples.

[^tei-readme]: [Text Embeddings Inference README](../raw/text-embeddings-inference.md). Upstream-authored documentation; inline parentheses give section locators (`§` = README heading). No repository revision recorded.
