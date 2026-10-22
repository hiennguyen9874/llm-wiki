---
type: Concept
title: Vietnamese_Embedding
description: A BGE-M3-derived Vietnamese dense embedding model with 1,024-dimensional outputs, a 2,048-token limit, and self-reported Legal Zalo 2021 retrieval gains over BGE-M3.
tags: [embedding, retrieval, vietnamese, legal, sentence-transformers, bge-m3]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T12:00:00Z }
sources:
  - id: vi-embed-card
    resource: ../raw/AITeamVN-Vietnamese_Embedding.md
    kind: model-card
    title: AITeamVN Vietnamese_Embedding model card
---

# Vietnamese_Embedding

Vietnamese_Embedding (AITeamVN) is a Sentence Transformers embedding model fine-tuned from [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) to improve Vietnamese retrieval. It outputs 1,024-dimensional vectors scored by dot product, accepts up to 2,048 tokens, and is licensed Apache-2.0. [^vi-embed-card]

## Specifications

| Field | Value |
| --- | --- |
| Base model | BAAI/bge-m3 |
| Library / type | sentence-transformers, Sentence Transformer (ONNX tag also listed) |
| Max sequence length | 2,048 tokens (also the training length) |
| Output dimension | 1,024 (no Matryoshka claim) |
| Similarity | Dot product |
| Language | Vietnamese |
| License | Apache-2.0 |
| Parameter count, pooling | Not stated in the card (inherited from BGE-M3 is unverified) |

[^vi-embed-card]

## Training

Trained on about 300,000 Vietnamese (query, positive document, negative document) triplets. The card gives no loss, hyperparameters, hardware, data source, or negative-mining details. [^vi-embed-card]

## Evaluation (Reported)

Dataset: the entire Legal Zalo 2021 training set, which the card says the model was not trained on. Self-reported results: [^vi-embed-card]

| Model | Acc@1 | Acc@3 | Acc@5 | Acc@10 | MRR@10 |
| --- | --- | --- | --- | --- | --- |
| Vietnamese_Reranker | 0.7944 | 0.9324 | 0.9537 | 0.9740 | 0.8672 |
| Vietnamese_Embedding_v2 | 0.7262 | 0.8927 | 0.9268 | 0.9578 | 0.8149 |
| Vietnamese_Embedding (this model, public) | 0.7274 | 0.8992 | 0.9305 | 0.9568 | 0.8181 |
| Vietnamese-bi-encoder (BKAI) | 0.7109 | 0.8680 | 0.9014 | 0.9299 | 0.7951 |
| BGE-M3 | 0.5682 | 0.7728 | 0.8382 | 0.8921 | 0.6822 |

On this legal benchmark the model improves MRR@10 from 0.6822 (BGE-M3) to 0.8181 (Synthesis from the table). The card says the evaluation can be reproduced with `evaluation_model.py` using data from Kaggle, but that script is not in the raw source, so the results are unreproduced here. Only one domain (legal) is measured. [^vi-embed-card]

## Related models from the same team

The card states that Vietnamese_Embedding_v2 and Vietnamese_Reranker were trained on 1,100,000 triplets. v2 scores slightly lower on the legal set, but the authors say the larger data should help in other domains (Reported, no supporting evidence). The reranker, a stage-two model, scores highest in the table. [^vi-embed-card]

## Relationships

- Derived from BGE-M3, also the base of [XProvence-reranker](xprovence-reranker.md).
- Another Vietnamese legal retrieval model: [DEk21_hcmute_embedding](dek21-hcmute-embedding.md), and [DeepX Embedding v1.0](deepx-embedding-v1.md); the evaluation protocols differ, so scores are not directly comparable.
- Multilingual Vietnamese-capable alternative: [Vintern-Embedding-1B](vintern-embedding-1b.md) (multimodal).

## Coverage and limits

The single raw file was fully inspected. Contact details and the citation BibTeX were excluded as non-durable. The v2 link in the card is malformed (relative path), and the Vietnamese_Reranker raw card is not compiled by this ingest. [^vi-embed-card]

[^vi-embed-card]: [AITeamVN Vietnamese_Embedding model card](../raw/AITeamVN-Vietnamese_Embedding.md), YAML metadata, "Model Details", "Evaluation" table and following paragraph. All figures are self-reported.
