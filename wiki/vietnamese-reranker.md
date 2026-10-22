---
type: Concept
title: Vietnamese_Reranker
description: A Vietnamese cross-encoder reranker fine-tuned from BAAI/bge-reranker-v2-m3 on about 1.1M triplets, with a 2,304-token input limit and self-reported Legal Zalo 2021 results.
tags: [reranking, vietnamese, bge-reranker-v2-m3, legal]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T14:00:00Z }
sources:
  - id: vi-reranker-card
    resource: ../raw/AITeamVN-Vietnamese_Reranker.md
    kind: web
    title: AITeamVN/Vietnamese_Reranker model card
---

# Vietnamese_Reranker

Vietnamese_Reranker (AITeamVN) is an Apache-2.0 reranker for Vietnamese, fine-tuned from `BAAI/bge-reranker-v2-m3` on roughly 1,100,000 Vietnamese (query, positive document, negative document) triplets.[^vi-reranker-card] It is a pointwise scorer: each query–passage pair yields one raw logit. Reported evidence is author-run (Reported) and covers one legal-domain dataset.

## Specification

| Item | Value |
|---|---|
| Base model | `BAAI/bge-reranker-v2-m3` |
| Language / license | Vietnamese / Apache-2.0 |
| Max sequence length | 2,304 tokens (256 query + 2,048 passage) |
| Training data | ~1.1M triplets (query, positive, negative) |
| Loading | `AutoModelForSequenceClassification` + `AutoTokenizer`, `max_length=2304` |
| Parameter count | Not stated |

Locator for all rows: model card header, "Model Details", and "Usage".[^vi-reranker-card]

## Usage

Pairs `[query, passage]` are tokenized with truncation and the model's `logits` are used as scores. The card's example gives about 7.56 for a relevant passage and −9.07 for an irrelevant one, so scores are unbounded logits, not probabilities.[^vi-reranker-card]

## Reported evaluation

The card evaluates on the full Legal Zalo 2021 training set, stating the model was not trained on it. Reported results (Reported, vendor-run; protocol not detailed):[^vi-reranker-card]

| Model | Acc@1 | Acc@3 | Acc@5 | Acc@10 | MRR@10 |
|---|---:|---:|---:|---:|---:|
| Vietnamese_Reranker | 0.7944 | 0.9324 | 0.9537 | 0.9740 | 0.8672 |
| Vietnamese_Embedding_v2 | 0.7262 | 0.8927 | 0.9268 | 0.9578 | 0.8149 |
| Vietnamese_Embedding | 0.7274 | 0.8992 | 0.9305 | 0.9568 | 0.8181 |
| Vietnamese-bi-encoder (BKAI) | 0.7109 | 0.8680 | 0.9014 | 0.9299 | 0.7951 |
| BGE-M3 | 0.5682 | 0.7728 | 0.8382 | 0.8921 | 0.6822 |

The card also notes that Vietnamese_Embedding_v2 (phase 2) scored slightly lower on legal data than the first phase but used much larger, broader data.[^vi-reranker-card]

## Limits and caveats

- The card does not say whether the reranker was run over a first-stage candidate list or the full corpus, nor the candidate-set size; the comparison to bi-encoders is therefore not a like-for-like protocol (Synthesis).
- Only one domain (legal) is evaluated; general-domain Vietnamese performance is unreported.
- The metadata labels it a "Sentence Transformer" with 1,024 output dimensions and dot-product similarity, while the usage example is a sequence-classification head returning one logit; the card does not reconcile these (Observed inconsistency).
- Parameter count and training hyperparameters are absent. Not checked against the raw model weights.
- Contact and developer names appear in the source and are omitted here.

## Relationships

- Derived from `BAAI/bge-reranker-v2-m3`, the same backbone family as [XProvence-reranker](xprovence-reranker.md).
- Sibling Vietnamese retrieval work in the wiki: [DeepX Embedding v1.0](deepx-embedding-v1.md), [DEk21_hcmute_embedding](dek21-hcmute-embedding.md), and [Vintern-Embedding-1B](vintern-embedding-1b.md).
- Reranker peers are compared in [Reranker model comparison](reranker-model-comparison.md); this model is not yet included there because its protocol is not comparable.

[^vi-reranker-card]: [AITeamVN/Vietnamese_Reranker model card](../raw/AITeamVN-Vietnamese_Reranker.md), publisher-authored; sections "Model Card", "Model Details", "Usage", "Evaluation".
