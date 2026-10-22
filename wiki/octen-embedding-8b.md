---
type: Concept
title: Octen-Embedding-8B
description: A Qwen3-Embedding-8B-derived multilingual text embedding model with 7.57B BF16 parameters per Hub metadata, 4,096-dimensional outputs, an Apache-2.0 license, and a self-reported 0.8045 RTEB Mean (Task).
tags: [embedding, retrieval, multilingual, qwen, lora]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-10-22T16:05:40Z }
sources:
  - id: octen-8b-card
    resource: ../raw/Octen-Embedding-8B.md
    title: Octen-Embedding-8B model card
  - id: octen-8b-hf-page
    resource: ../raw/Octen-Octen-Embedding-8B.md
    kind: web
    revision: Hub lastModified 2026-10-10T06:46:47Z
    title: Octen/Octen-Embedding-8B Hugging Face page capture
---

# Octen-Embedding-8B

Octen-Embedding-8B is a text embedding model fine-tuned from Qwen/Qwen3-Embedding-8B using LoRA. It produces 4,096-dimensional embeddings and is positioned for multilingual semantic search and retrieval. The card text gives 7.6B (family table) and 8B (Model Details); Hugging Face's safetensors metadata gives 7,567,295,488 BF16 parameters. [^octen-8b-card] [^octen-8b-hf-page]

## Benchmarks

The model card reports **0.7953 RTEB Public**, **0.8157 RTEB Private**, and **0.8045 RTEB Mean (Task)** for Octen-Embedding-8B. It claims the model ranked #1 on the RTEB leaderboard as of January 12, 2026. These are self-reported results; the card does not provide task-level scores or evaluation-protocol details. [^octen-8b-card]

| Model | RTEB Public | RTEB Private | RTEB Mean (Task) |
|---|---:|---:|---:|
| Octen-Embedding-8B | 0.7953 | 0.8157 | 0.8045 |
| Qwen3-Embedding-8B | 0.7310 | 0.7838 | 0.7547 |

The card's full RTEB table (self-reported; same January 12, 2026 snapshot) lists these competitors by Mean (Task): voyage-3-large 0.7812, Octen-Embedding-4B 0.7834, MoD-Embedding 0.7758, gemini-embedding-001 0.7602, voyage-3.5 0.7571, Cohere-embed-v4.0 0.7166, jina-embeddings-v4 0.7105, GritLM-7B 0.6724, text-embedding-3-large 0.6567, and bge-m3 0.5893. Note that voyage-3-large has a higher Private score (0.8277) than Octen-Embedding-8B (0.8157), and Octen-Embedding-4B (0.7834) is the only listed model close to the 8B's Mean (Task). Rows for Octen-Embedding-0.6B (Public 0.7241 only) and Qwen3-Embedding-4B/0.6B (Private only) have missing cells, so they cannot be ranked on Mean (Task). The Hub page capture reproduces the same numbers. [^octen-8b-card] [^octen-8b-hf-page]

## Model size and architecture

- **Size:** the model-family table gives **7.6B** parameters and Model Details gives **8B**; the card does not reconcile them. [^octen-8b-card] The Hub safetensors metadata reports **7,567,295,488 parameters, all BF16** (sharded, 15,134,665,036 bytes total), and the Hub header rounds this to "8B params". [^octen-8b-hf-page] Synthesis: the 7.6B figure is the precise one and "8B" is rounding. Evidence class: Observed (Hub metadata, not independently counted).
- **Base model and adaptation:** fine-tuned from `Qwen/Qwen3-Embedding-8B` using LoRA. The card does not specify LoRA rank, target modules, trainable-parameter count, or training hyperparameters. [^octen-8b-card]
- **Inputs and outputs:** 4,096-dimensional embeddings. The supplied Transformers example takes the final-token hidden state and L2-normalizes it; the card does not otherwise describe pooling or embedding-head architecture. [^octen-8b-card]
- **Context-length discrepancy:** the highlights, model-family table, and RTEB table list 32,768 maximum tokens, whereas Model Details lists 40,960 maximum sequence length; the source does not reconcile them. [^octen-8b-card] The supplied Transformers example truncates at `max_length=8192`, and the Limitations section says documents over 40K tokens need truncation. [^octen-8b-hf-page]
- **Undisclosed architecture:** the source does not provide layer count, hidden size, attention design, tokenizer details, or a parameter breakdown. [^octen-8b-card]

## Usage and known issues

- **Pooling and normalization:** the Transformers example uses left padding, takes the last-token hidden state (`last_hidden_state[:, -1, :]`), and L2-normalizes it; the Sentence Transformers example calls `model.encode` and `cos_sim`, with an expected output shape of `(n, 4096)`. [^octen-8b-hf-page] The card does not state whether the Sentence Transformers configuration reproduces the same pooling.
- **Document-prefix workaround:** the card says documents encoded without an instruction prefix may behave unexpectedly because of an upstream Qwen3-Embedding issue (linked to Qwen3-Embedding-8B discussion 21), and recommends prepending `"- "` (dash and space) to each document. No measurement of the effect is given. Evidence class: Reported. [^octen-8b-card] [^octen-8b-hf-page] See [Qwen3-Embedding-8B](qwen3-embedding-8b.md) for the base model's instruction-aware use.
- **Intended uses:** semantic search, document similarity and clustering, question answering, cross-lingual retrieval, and text classification with embeddings; it is not intended for text generation. [^octen-8b-card] [^octen-8b-hf-page]
- **Serving:** the Hub tags include `text-embeddings-inference`, `endpoints_compatible`, and `deploy:azure`; see [Text Embeddings Inference](text-embeddings-inference.md). [^octen-8b-hf-page]

## License and provenance

The model is licensed under Apache 2.0, and the card notes that its base, Qwen3-Embedding-8B, is also Apache 2.0. [^octen-8b-hf-page] The card points to the Octen Team blog post "Octen Series: Optimizing Embedding Models to #1 on RTEB Leaderboard" (cited as `octen2025rteb`, 2025) instead of a paper; that blog post is not in the raw sources, so its details are not compiled here. [^octen-8b-hf-page]

## Hub snapshot

In the page capture, the repository was created 2025-12-23 and last modified 2026-10-10, with 194 likes, 150,721 downloads in the last month, and 1,450,639 all-time downloads (counts as of capture; volatile). The Hub's `model-index` is empty, so the RTEB scores are card prose, not Hub-verified evaluation results. [^octen-8b-hf-page]

## Language support

The card claims support for **100+ languages**, specifically naming English and Chinese in its metadata, and says support includes programming languages. It describes multilingual, cross-lingual, and code retrieval capability, but does not enumerate the supported languages or give per-language benchmark results. [^octen-8b-card]

## Relationships

- **Derived from:** [Qwen3-Embedding-8B](qwen3-embedding-8b.md) by LoRA fine-tuning. [^octen-8b-card]
- **Sibling models:** [Octen-Embedding-4B](octen-embedding-4b.md) and [Octen-Embedding-0.6B](octen-embedding-0-6b.md). [^octen-8b-card]

## Training data

The model card does not identify any training datasets, corpus sizes, mixture proportions, collection dates, licenses, filtering procedures, synthetic-data use, or domain-specific sample counts. It only names LoRA fine-tuning as the training method. Therefore, its claims of expertise in legal, finance, healthcare, and code retrieval cannot be tied to disclosed training data from this source. [^octen-8b-card]

[^octen-8b-card]: [Octen-Embedding-8B model card](../raw/Octen-Embedding-8B.md). Model, training, language, and benchmark claims are reported by the model card.
[^octen-8b-hf-page]: [Octen/Octen-Embedding-8B Hugging Face page capture](../raw/Octen-Octen-Embedding-8B.md). Locators: rendered model-card sections (Open Source Model List, RTEB table, Model Details, Usage, Known Issues, Limitations, License, Paper) and the embedded page JSON (`safetensors.parameters.BF16`, `safetensors.totalFileSize`, `createdAt`, `lastModified`, `downloads`, `likes`, `tags`, `model-index`). Coverage: the card text duplicates [the earlier card capture](../raw/Octen-Embedding-8B.md); navigation, scripts, CSS, and the chat-template JSON were excluded as non-durable. Hub counts are as of capture and are Reported by the platform.
