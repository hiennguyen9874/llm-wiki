---
type: Concept
title: XProvence-reranker
description: A 568M-parameter multilingual BGE-M3-derived model that jointly prunes irrelevant sentences from retrieved passages and supplies reranking scores for RAG question answering.
tags: [reranking, context-pruning, rag, multilingual, bge-m3, xprovence]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T13:30:00Z }
sources:
  - id: xprovence-reranker-bgem3-v2-model-card
    resource: ../raw/xprovence-reranker-bgem3-v2.md
    title: XProvence-reranker model card
---

# XProvence-reranker

XProvence-reranker is a 568M-parameter, CC BY-NC-ND-4.0 multilingual model for RAG question answering that removes question-irrelevant sentences from retrieved passages while returning a passage relevance score usable for reranking. It has an 8,192-token context limit and is based on BAAI's `bge-reranker-v2-m3`.[^xprovence-reranker-bgem3-v2-model-card]

## Pruning and reranking

The model processes a question and retrieved passage, encodes all sentences in the passage together, and produces a pruned passage plus a reranking score. A threshold selects sentences automatically; the model card recommends `0.3` for conservative pruning with no or minimal reported performance loss and `0.7` for higher compression, while noting that the threshold can be tuned per use case.[^xprovence-reranker-bgem3-v2-model-card]

`process(question, context)` accepts one question and context or batches of questions with their context lists. Its output includes `pruned_context`, `reranking_score`, and `compression_rate`. With `reorder=True`, contexts are sorted by relevance and `top_k` limits retained passages; otherwise input order is preserved. The default batch size is 32.[^xprovence-reranker-bgem3-v2-model-card]

By default, `always_select_title=True`: when selection is non-empty, the model retains the title. A title is the first sentence by default, may be disabled with `title=None`, or may be provided explicitly; retaining it is documented as useful for contextualizing Wikipedia-like passages.[^xprovence-reranker-bgem3-v2-model-card]

## Training and language coverage

XProvence was initialized from `bge-reranker-v2-m3` and fine-tuned for both a binary sentence-selection mask and retention of its initial reranking capability. Training used English MS MARCO plus translations of a subset into 16 languages; pairs were monolingual during training. The source expects cross-lingual pairs to work through cross-lingual transfer, but does not report that expectation as a separately evaluated result.[^xprovence-reranker-bgem3-v2-model-card]

The model card states native support for Arabic, Bengali, English, Spanish, Persian, Finnish, French, Hindi, Indonesian, Japanese, Korean, Russian, Swahili, Telugu, Thai, and Chinese, and claims 100+ language coverage through the BGE-M3 backbone's cross-lingual transfer. It describes evaluation across 26 languages and six datasets, reporting little-to-no performance drop while pruning and a better Pareto frontier than unspecified existing baselines; detailed scores and protocols are not included in this source.[^xprovence-reranker-bgem3-v2-model-card]

## Deployment limits

The supplied implementation loads with Hugging Face Transformers `AutoModel` and `trust_remote_code=True`, and requires spaCy plus the `xx_sent_ud_sm` sentence model. Although the model accepts up to 8,192 tokens, the source says training examples were paragraph-sized; behavior on longer contexts is therefore not characterized by the described training data.[^xprovence-reranker-bgem3-v2-model-card]

[^xprovence-reranker-bgem3-v2-model-card]: [XProvence-reranker model card](../raw/xprovence-reranker-bgem3-v2.md). Architecture, licensing, training, language, interface, and evaluation claims are publisher-authored.