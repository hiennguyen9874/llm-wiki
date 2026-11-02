---
type: Concept
title: KaLM-Reranker-V1-Small
description: A 1B-activated-parameter multilingual T5Gemma2 reranker that compresses document states before pointwise query-conditioned scoring.
tags: [reranking, multilingual, compression, retrieval]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:42:13Z }
sources:
  - id: kalm-small-card
    resource: ../raw/KaLM-Embedding-KaLM-Reranker-V1-Small.md
    kind: model-card
    title: KaLM-Reranker-V1-Small model card
---

# KaLM-Reranker-V1-Small

**Reported:** KaLM-Reranker-V1-Small is an Apache-2.0 multilingual, instruction-aware text reranker with 1B activated parameters, based on `google/t5gemma-2-1b-1b`. Its fast-but-not-late-interaction (FBNL) architecture pre-encodes and compresses documents, then uses decoder cross-attention for pointwise query–document relevance scoring. It is not listwise ranking or late-interaction MaxSim. [^kalm-small-card]

## Architecture and training

**Reported:** The encoder processes the document independently, while the decoder processes the instruction and query and cross-attends to the document states. The card lists 698M non-embedding and 302M embedding parameters, 26 layers, 1,152-dimensional document token states, 128K sequence length, and 1×–32× Matryoshka embedding pooling (MEP). The example uses mask-aware mean pooling over consecutive document states. The card lists KaLM reranker training data, KaLM embedding fine-tuning data and BGE-M3 data, but does not describe a complete training procedure or enumerate supported languages. [^kalm-small-card]

## Inference and constraints

- **Reported:** The document is formatted as `<Document>: {document}`; a separate decoder prompt includes the task instruction and query and requests a yes/no answer. Sentence Transformers accepts `(query, document)` pairs and returns `P(yes)` by default; identity activation gives the yes-minus-no logit margin. [^kalm-small-card]
- **Reported:** Defaults truncate raw queries to 512 tokens and prefixed encoder documents to 1,024 tokens, separate limits rather than a combined window. `chunk_size=4` mean-pools four encoder states, and `None` disables compression. These example limits are not the advertised 128K sequence length. [^kalm-small-card]
- **Reported:** Sentence Transformers requires `sentence-transformers>=5.6,<6`, `transformers>=5.3,<6`, PyTorch and `trust_remote_code=True`; load only trusted revisions. The release supports PyTorch inference, not training, ONNX or OpenVINO. The prose calls the example Nano, but its code loads Small; the separate Transformers example imports `kalm_reranker`, whose implementation was not inspected. [^kalm-small-card]
- **Reported:** An experimental single-GPU vLLM adapter was validated by its publisher with Python 3.12, vLLM 0.19.1, Transformers 5.6.2 and CUDA BF16. It supports chunk sizes 1, 2, 4, 8, 16 and 32 and optional `/rerank` and `/score` endpoints, but runs the semantic forward through Transformers rather than fully native vLLM kernels. [^kalm-small-card]

## Evaluation and evidence limits

**Reported, not independently verified:** the authors claim competitive BEIR, MIRACL and LMEB reranking performance and reduced online overhead. Numerical results and evaluation details are in linked figures unavailable at their local paths; no ranking, measured speedup or cross-protocol comparison is established here. [^kalm-small-card]

**Observed:** the local model card and embedded examples were inspected statically. Six linked architecture, prompt and evaluation images and `vllm_support/README.md` are absent at their referenced local paths. The external papers, datasets, model weights, implementation and adapter were not inspected; decorative badge images were excluded. No model or example was executed. The source has no immutable revision or capture date; the license and behavioral claims are publisher-reported. These material gaps make the concept draft. [^kalm-small-card]

## Relationships

- **Newer version:** The card identifies [KaLM-Reranker-V1-Small-R2](kalm-reranker-v1-small-r2.md) as a newer version; it does not establish formal deprecation or an effective replacement date. [^kalm-small-card]
- **Sibling of:** [KaLM-Reranker-V1-Nano](kalm-reranker-v1-nano.md) and [KaLM-Reranker-V1-Large](kalm-reranker-v1-large.md), the smaller and larger family members. [^kalm-small-card]

[^kalm-small-card]: [KaLM-Reranker-V1-Small model card](../raw/KaLM-Embedding-KaLM-Reranker-V1-Small.md), frontmatter; introduction; “Model Details,” “Prompt Template,” “Evaluation,” “Using Sentence Transformers,” “Using transformers,” and “Using vLLM.” Figures and implementation not available locally.
