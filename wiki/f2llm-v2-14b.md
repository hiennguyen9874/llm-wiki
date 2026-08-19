---
type: Concept
title: F2LLM-v2-14B
description: A 14B-parameter instruct embedding model in the multilingual F2LLM-v2 family, with 5,120-dimensional normalized embeddings and claimed support for more than 200 languages.
tags: [embedding, retrieval, multilingual, instruction-tuned]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:15:14Z }
sources:
  - id: f2llm-v2-14b-card
    resource: ../raw/F2LLM-v2-14B.md
    title: F2LLM-v2-14B model card
---

# F2LLM-v2-14B

F2LLM-v2-14B is the 14B instruct variant in the F2LLM-v2 multilingual embedding-model family. Its card claims more than 200-language support and training on a curated composite of 60 million publicly available high-quality data items; the supplied example produces normalized 5,120-dimensional embeddings. [^f2llm-v2-14b-card]

## Benchmarks

The supplied model card reports no named benchmark, metric, score, comparison, or evaluation protocol. Its claims of performance and efficiency therefore cannot be assessed from this source. [^f2llm-v2-14b-card]

## Model size and architecture

- **Size and family:** This is the 14B instruct model. The family spans eight released instruct sizes (80M, 160M, 330M, 0.6B, 1.7B, 4B, 8B, and 14B); base models are listed for the five sizes from 0.6B through 14B. [^f2llm-v2-14b-card]
- **Base model:** the card metadata names `codefuse-ai/F2LLM-v2-14B-Preview`. [^f2llm-v2-14b-card]
- **Embedding interface:** the provided Sentence Transformers and Transformers examples return 5,120-dimensional vectors. The Transformers example selects the final non-padding (EOS) hidden state and L2-normalizes it; the model-card examples use a query instruction for retrieval queries and no prompt for documents. [^f2llm-v2-14b-card]
- **Architecture limit:** the card does not specify the transformer layer count, hidden width, attention configuration, tokenizer, context length, pooling architecture beyond the example, or the parameter count’s accounting method. [^f2llm-v2-14b-card]

## Language support

The card describes F2LLM-v2 as supporting more than 200 languages, particularly mid- and low-resource languages. Its metadata also enumerates language codes spanning many languages, including English, Chinese, Russian, Spanish, French, German, Arabic, Vietnamese, Hindi, Korean, and Japanese; it does not establish whether that metadata list is exhaustive. [^f2llm-v2-14b-card]

## Training data and release

The card states that the family was trained on a curated composite of 60 million publicly available high-quality data items, and its metadata names `codefuse-ai/F2LLM-v2` as the dataset. It says the training data, training code, base and instruct models, and intermediate checkpoints are released. [^f2llm-v2-14b-card]

The source does not disclose the composition, languages, proportions, licenses, collection or filtering method, split, deduplication, training objective, hardware, token count, or training duration. Consequently, the 60-million figure is insufficient to characterize the corpus or reproduce training from this card alone. [^f2llm-v2-14b-card]

[^f2llm-v2-14b-card]: [F2LLM-v2-14B model card](../raw/F2LLM-v2-14B.md). All model, language, training-data, and capability claims are reported by the card.
