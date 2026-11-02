---
type: Concept
title: KaLM-Reranker-V1-Nano
description: A 0.27B-activated-parameter multilingual T5Gemma2 reranker that pre-encodes and compresses documents before pointwise query-conditioned scoring.
tags: [reranking, multilingual, compression, retrieval]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:40:42Z }
sources:
  - id: nano-v1-card
    resource: ../raw/KaLM-Embedding-KaLM-Reranker-V1-Nano.md
    kind: model-card
    title: KaLM-Reranker-V1-Nano model card
---

# KaLM-Reranker-V1-Nano

**Reported:** KaLM-Reranker-V1-Nano is an Apache-2.0 multilingual text reranker with 0.27B activated parameters, based on `google/t5gemma-2-270m-270m`. Its fast-but-not-late-interaction (FBNL) design pre-encodes and compresses document states, then uses decoder cross-attention to score each query–document pair with a task instruction. This is pointwise scoring rather than listwise ranking or late-interaction MaxSim. [^nano-v1-card]

## Architecture and training

**Reported:** The model has 100M non-embedding and 168M embedding parameters, 18 layers as listed in the card, and 640-dimensional document token states. The family table specifies a 128K sequence length and 1×–32× Matryoshka embedding pooling (MEP); these token states are not presented as a standalone dense embedding. The card lists KaLM reranker training data, KaLM embedding finetuning data and BGE-M3 data, but does not describe a complete training recipe or enumerate supported languages. [^nano-v1-card]

## Inference and constraints

- **Reported:** The encoder receives `<Document>: {document}`; a separate decoder prompt contains the query and task instruction and requests a yes/no answer. Sentence Transformers accepts `(query, document)` pairs; its default output is `P(yes)`, while identity activation returns the yes-minus-no logit margin. [^nano-v1-card]
- The examples default to truncating the raw query at 512 tokens and the encoder document including its prefix at 1,024 tokens; these are separate limits, not a combined window. `chunk_size=4` mask-aware mean-pools each group of four document states, while `None` disables pooling. The advertised 128K length is not the default document limit. [^nano-v1-card]
- The card specifies `sentence-transformers>=5.6,<6`, `transformers>=5.3,<6` and PyTorch inference. Loading custom code requires `trust_remote_code=True`: use only trusted, pinned revisions. Training, ONNX and OpenVINO are not included in this release, according to the card. [^nano-v1-card]
- An experimental single-GPU vLLM adapter is reported validated with Python 3.12, vLLM 0.19.1, Transformers 5.6.2 and CUDA BF16. It supports chunk sizes 1, 2, 4, 8, 16 and 32, and offline ranking plus optional `/rerank` and `/score` endpoints; the semantic forward still runs through Transformers, not native vLLM kernels. [^nano-v1-card]

## Evaluation and coverage limits

**Reported, not independently verified:** the authors claim competitive BEIR, MIRACL and LMEB results and reduced online overhead. Numerical comparisons and supporting experimental details appear in figures missing from the local capture, so the available text cannot establish a ranking or measured speedup. [^nano-v1-card]

**Observed:** the local card was inspected statically; its six linked architecture, prompt and evaluation images and `vllm_support/README.md` are absent at their referenced local paths. The external paper, datasets, model weights, custom code, adapter and other external links were not inspected; decorative badges were excluded. No model or example code was run. The card gives no immutable revision or capture date. Publisher claims, including the license, remain unverified, and missing evidence makes this page draft. [^nano-v1-card]

## Relationships

- **Newer version:** The card identifies [KaLM-Reranker-V1-Nano-R2](kalm-reranker-v1-nano-r2.md) as a newer version; this does not establish formal deprecation or an effective replacement date. [^nano-v1-card]
- **Sibling of:** [KaLM-Reranker-V1-Large](kalm-reranker-v1-large.md), another size of the reported V1 family. [^nano-v1-card]

[^nano-v1-card]: [KaLM-Reranker-V1-Nano model card](../raw/KaLM-Embedding-KaLM-Reranker-V1-Nano.md), frontmatter; introduction; “Model Details,” “Prompt Template,” “Evaluation,” “Using Sentence Transformers,” “Using transformers,” and “Using vLLM.” Linked figures and implementation unavailable locally.
