---
type: Synthesis
title: Current embedding-model architecture taxonomy
description: A taxonomy of current embedding architectures by retrieval representation, backbone, multimodal composition, and efficiency adaptations.
tags: [embedding, retrieval, multimodal, architecture, synthesis]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T15:14:57+07:00 }
sources:
  - id: granite-card
    resource: ../raw/granite-embedding-311m-multilingual-r2.md
    title: Granite Embedding 311M Multilingual R2 model card
  - id: qwen3-report
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report
  - id: deepx-card
    resource: ../raw/deepx-embedding-v1.md
    title: DeepX Embedding v1.0 model card
  - id: colqwen-card
    resource: ../raw/ColQwen3.5-4.5B-v3.md
    title: ColQwen3.5-4.5B-v3 model card
  - id: uembed-report
    resource: ../raw/2608.02583_UEmbed/main.tex
    title: UEmbed technical report
  - id: qwen3-vl-report
    resource: ../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex
    title: Qwen3-VL Embedding technical report
  - id: gelato-report
    resource: ../raw/2605.08384_jina-embeddings-v5-omni/main.tex
    title: GELATO technical report
---

# Current embedding-model architecture taxonomy

Current embedding models do not form one linear succession. They are best classified on three independent axes: **retrieval representation** (one vector, token vectors, or dense+sparse), **backbone** (bidirectional encoder, causal decoder, or efficient sequence model), and **multimodal composition** (native unified model or aligned modality towers). The strongest practical trade-off remains representation: single-vector ANN minimizes index and scoring cost; late interaction preserves localized matches at higher cost; dense+sparse adds lexical matching.[^granite-card][^colqwen-card][^uembed-report]

## 1. By retrieval representation

| Group | Architecture | Direction and trade-off | Examples in wiki |
|---|---|---|---|
| **Dense bi-encoder** | Encode query and item separately to one normalized vector; ANN plus cosine/dot-product scoring. | Default first-stage retrieval: compact index and low latency, but compresses a whole item into one vector. | [Granite 311M](granite-embedding-311m-multilingual-r2.md), [Qwen3 4B](qwen3-embedding-4b.md), [Qwen3-VL 8B](qwen3-vl-embedding-8b.md) |
| **Late-interaction / multi-vector** | Retain token/region vectors; score query--document pairs with ColBERT-style MaxSim. | Aimed at visual documents and fine-grained evidence matching; index size and query-time scoring grow with retained tokens. | [ColQwen3.5](colqwen3-5-4-5b-v3.md), [Jina v4](jina-embeddings-v4.md) |
| **Dense + learned sparse hybrid** | One backbone emits a semantic dense vector and vocabulary-weighted sparse vector. | Combines ANN with inverted-index lexical matching, avoiding separate embedding passes; sparse quality and cross-lingual lexical activation remain limits. | [UEmbed](uembed.md) |

## 2. By backbone and pooling

| Group | Architecture | Observed direction |
|---|---|---|
| **Bidirectional encoder** | BERT/ModernBERT-like encoder; usually CLS or mean pooling. | Remains the efficiency-oriented text baseline, including long-context variants. [^granite-card] |
| **Repurposed causal decoder / VLM** | Decoder-only LLM or VLM used as a bi-encoder; EOS or last-token hidden state is pooled. | Embedding capability is being added to general-purpose instruction-following backbones, providing long context and a common text--vision path. [^qwen3-report][^qwen3-vl-report] |
| **Efficient long-sequence backbone** | Linear attention and parameter sharing rather than conventional full attention. | Targets long, domain-specific documents at lower sequence cost; this is an emerging specialized branch rather than evidence of a universal replacement. | [DeepX](deepx-embedding-v1.md) |

## 3. By multimodal composition

| Group | Architecture | Direction and trade-off |
|---|---|---|
| **Native unified multimodal encoder** | A VLM directly maps text, image, video, and mixed inputs to one space. | Best when multimodal fusion and shared instruction conditioning are central; training and serving use the full backbone. | [Qwen3-VL Embedding](qwen3-vl-embedding-8b.md), [e5-omni](e5-omni.md) |
| **Locked aligned towers** | Preserve a text embedding space; freeze text/vision/audio towers and train small modality projectors. | Adds image/audio/video while retaining compatibility with an existing text index and allowing unused towers to be omitted. | [GELATO](gelato.md), [Jina v5 Omni Small](jina-embeddings-v5-omni-small.md) |

## Cross-cutting direction: adaptable vector budgets

**Matryoshka representation learning** is a cross-cutting design, not a separate retriever: one model exposes normalized vector prefixes at several dimensions, letting deployments trade accuracy for memory and latency without retraining. It appears in dense text and multimodal models and can also be combined with quantization. [^qwen3-report][^qwen3-vl-report]

## Practical reading

Choose the representation first: dense for broad, cost-sensitive recall; late interaction for page/region-level visual evidence; hybrid where lexical exactness matters. Then choose the backbone and modality composition to meet context, hardware, language, and input-modality requirements. Reported benchmarks in the linked concepts use different protocols, so they do **not** establish a universal ranking across these groups.

## Relationships

- **Synthesizes:** [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md), [Qwen3-VL, harrier, Qwen3, F2LLM, and Jina embedding comparison](embedding-model-comparison-qwen3-vl-harrier-qwen3-f2llm.md), and the architecture examples linked above.

[^granite-card]: [Granite Embedding 311M Multilingual R2 model card](../raw/granite-embedding-311m-multilingual-r2.md). Provider-reported architecture and results.
[^qwen3-report]: [Qwen3 Embedding technical report](../raw/2506.05176_Qwen3Embedding/main.tex). Author-reported architecture and training.
[^deepx-card]: [DeepX Embedding v1.0 model card](../raw/deepx-embedding-v1.md). Provider-reported architecture and results.
[^colqwen-card]: [ColQwen3.5-4.5B-v3 model card](../raw/ColQwen3.5-4.5B-v3.md). Provider-reported architecture and results.
[^uembed-report]: [UEmbed technical report](../raw/2608.02583_UEmbed/main.tex). Author-reported architecture and evaluation.
[^qwen3-vl-report]: [Qwen3-VL Embedding technical report](../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex). Author-reported architecture and training.
[^gelato-report]: [GELATO technical report](../raw/2605.08384_jina-embeddings-v5-omni/main.tex). Author-reported architecture and efficiency.
