---
type: Concept
title: KaLM-Reranker-V1-Large
description: A 4B-activated-parameter multilingual T5Gemma2 reranker that pre-encodes and compresses documents before pointwise query-conditioned scoring.
tags: [reranking, multilingual, compression, retrieval]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:39:26Z }
sources:
  - id: kalm-v1-card
    resource: ../raw/KaLM-Embedding-KaLM-Reranker-V1-Large.md
    kind: model-card
    title: KaLM-Reranker-V1-Large model card
---

# KaLM-Reranker-V1-Large

**Reported:** KaLM-Reranker-V1-Large is an Apache-2.0 multilingual text reranker with 4B activated parameters, based on `google/t5gemma-2-4b-4b`. Its fast-but-not-late-interaction (FBNL) architecture pre-encodes and compresses documents, then uses decoder cross-attention to score each query–document pair with its instruction. This is pointwise relevance scoring, not listwise ranking or late-interaction MaxSim. [^kalm-v1-card]

## Architecture and family

**Reported:** Matryoshka embedding pooling (MEP) compresses consecutive document encoder states before query-conditioned decoder interaction; the example uses mask-aware mean pooling. The Large model has 3,209M non-embedding and 675M embedding parameters, 34 layers as listed in the card, and 2,560-dimensional document token states. The card reports 128K sequence length and 1×–32× MEP; these states are not advertised as a standalone dense embedding. [^kalm-v1-card]

The same card lists Nano at 0.27B activated parameters, 18 layers and 640-dimensional document states, and Small at 1B, 26 layers and 1,152 dimensions. Both have the same reported sequence length and compression range. Language coverage is only described as multilingual, not enumerated. The metadata names reranker and embedding finetuning datasets and BGE-M3 data; training procedure and evaluation protocol are not specified in sufficient detail to reproduce them. [^kalm-v1-card]

## Inference and constraints

- **Reported:** The model receives documents as `<Document>: {document}` and a separate decoder prompt containing task instruction and query; the answer is restricted to yes or no. Sentence Transformers accepts `(query, document)` pairs; default scoring is `P(yes)`, while identity activation returns the yes-minus-no logit margin. [^kalm-v1-card]
- Example defaults truncate the raw query to 512 tokens and encoder document input including its prefix to 1,024 tokens; these are separate limits, not a combined window. `chunk_size=4` pools four encoder states, while `None` disables compression. The 128K family figure should not be mistaken for the example's default input length. [^kalm-v1-card]
- The Sentence Transformers example specifically loads Nano, not Large, and requires `sentence-transformers>=5.6,<6`, `transformers>=5.3,<6`, PyTorch, and `trust_remote_code=True`; only trusted revisions should be loaded. The card says the release supports PyTorch inference, not training, ONNX, or OpenVINO. The separate Transformers example defaults to Large and imports `kalm_reranker`, whose implementation was not supplied. [^kalm-v1-card]
- The experimental single-GPU vLLM adapter is **reported** validated with Python 3.12, vLLM 0.19.1, Transformers 5.6.2 and CUDA BF16. It supports pooling chunks of 1, 2, 4, 8, 16, or 32, exposes offline ranking and optional `/rerank` and `/score` service endpoints, and still runs the T5Gemma2 semantic forward through Transformers rather than native vLLM kernels. The plugin and guide were not inspected. [^kalm-v1-card]

## Evaluation and evidence limits

**Reported, not independently verified:** the authors claim competitive BEIR, MIRACL and LMEB results and reduced online overhead. Their numerical comparisons and experimental details appear in linked figures unavailable in this capture, so no benchmark ranking, measured speedup, or comparison across protocols can be established from the available text. [^kalm-v1-card]

**Observed:** the local card was inspected statically; six linked architecture, prompt and evaluation images and the linked `vllm_support/README.md` are absent at their local paths. The external paper, datasets, model weights, implementation and adapter were not inspected; badge images are decorative. No model, code or benchmark was run. The card does not specify an immutable revision or capture date; license and other claims remain publisher-reported. These gaps make the concept draft. [^kalm-v1-card]

## Relationships

- **Newer version:** The card's metadata identifies [KaLM-Reranker-V1-Large-R2](kalm-reranker-v1-large-r2.md) as a newer version; this alone does not establish formal deprecation or an effective replacement date. [^kalm-v1-card]

[^kalm-v1-card]: [KaLM-Reranker-V1-Large model card](../raw/KaLM-Embedding-KaLM-Reranker-V1-Large.md), frontmatter; introduction; “Model Details,” “Prompt Template,” “Evaluation,” “Using Sentence Transformers,” “Using transformers,” and “Using vLLM.” Figures and implementation not available locally.
