---
type: Concept
title: DeepX Embedding v1.0
description: A 772M-parameter Vietnamese legal retrieval embedding model using Gated DeltaNet-2 linear attention, Hyperloop weight sharing, and 256–1536-dimensional Matryoshka embeddings.
tags: [embedding, retrieval, vietnamese, legal, linear-attention, matryoshka]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:13:15Z }
sources:
  - id: deepx-v1-card
    resource: ../raw/deepx-embedding-v1.md
    title: DeepX Embedding v1.0 model card
---

# DeepX Embedding v1.0

DeepX Embedding v1.0 is a 772M-parameter embedding model optimized for Vietnamese legal-document retrieval. It uses Gated DeltaNet-2 (linear attention), Hyperloop weight sharing, and Matryoshka embeddings; its supplied model card reports 0.8162 nDCG@10 on Zalo Legal Text Retrieval. [^deepx-v1-card]

## Benchmarks

On Zalo Legal Text Retrieval, the source reports **0.8162 nDCG@10**, **0.7672 MRR@10**, and **0.9537 Recall@10** for DeepX. Its comparison table reports that 0.8162 nDCG@10 exceeds the listed prior state of the art, `mainguyen9/vietlegal-harrier-0.6b` at 0.7813, by 0.0349 absolute (described by the source as +4.5%). [^deepx-v1-card]

| Model | Parameters | nDCG@10 |
|---|---:|---:|
| `intfloat/multilingual-e5-large` | 560M | 0.6660 |
| `mainguyen9/vietlegal-e5` | 560M | 0.7310 |
| `mainguyen9/vietlegal-harrier-0.6b` | 600M | 0.7813 |
| DeepX Embedding v1.0 | 772M | 0.8162 |

The benchmark comparison and state-of-the-art characterization are self-reported by the model card; it does not provide evaluation protocol details beyond the named dataset and metrics. [^deepx-v1-card]

## Model size and architecture

- **Size:** 772M parameters total: 286M frozen token-embedding parameters and 486M trainable backbone parameters. [^deepx-v1-card]
- **Tokenizer and embeddings:** a custom 186,046-token vocabulary feeds a frozen `186,046 × 1,536` token-embedding matrix. [^deepx-v1-card]
- **Backbone:** Gated DeltaNet-2 (GDN-2) pure linear attention, reported as $O(n)$, with Hyperloop sharing: 35 compute passes reuse nine unique layer-parameter sets. The card describes a begin block, two Phase 1 loops, four Phase 2 loops, and an end block; per-loop LoRA and Rotary Depth Embedding differentiate iterations. [^deepx-v1-card]
- **Sequence handling:** YaRN RoPE is reported as validated at 8K tokens and supporting 128K tokens. [^deepx-v1-card]
- **Outputs:** attention pooling yields a 1,536-dimensional single-vector embedding for ANN search; the model also provides 128-dimensional token vectors for ColBERT-style MaxSim reranking. [^deepx-v1-card]
- **Matryoshka dimensions:** the card reports nDCG@10 of 0.78, 0.79, 0.80, 0.81, and 0.8162 respectively at 256, 512, 768, 1,024, and 1,536 dimensions. [^deepx-v1-card]

## Language support

The model card identifies Vietnamese and English support. It describes the vocabulary as optimized for Vietnamese and English, while its stated optimization target is Vietnamese legal-document retrieval. [^deepx-v1-card]

## Training data and procedure

The card's metadata names `unicamp-dl/mmarco`, `miracl/miracl`, and `GreenNode/zalo-ai-legal-text-retrieval-vn` as datasets. It does not state their proportions, the number of training examples, filtering, licenses, or whether additional training data was used; these limits prevent a fuller account of the training corpus. [^deepx-v1-card]

Reported training used a conservative-training stage, 4K–8K long-sequence exposure, hard-negative mining, and a domain-boost stage. The stated configuration is two RTX 5070 Ti 16GB GPUs in pipeline parallelism, BF16, 8-bit AdamW, maximum sequence length 8,192, and approximately 600 GPU-hours. The loss combines InfoNCE ($\tau=0.07$) with Matryoshka objectives at 256, 512, 768, 1,024, and 1,536 dimensions. [^deepx-v1-card]

[^deepx-v1-card]: [DeepX Embedding v1.0 model card](../raw/deepx-embedding-v1.md). Architecture, training, language, and benchmark claims are reported by the model card.