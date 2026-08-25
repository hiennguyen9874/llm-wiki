---
type: Concept
title: SCONE scalable contextualized offloaded n-gram embeddings
description: SCONE substitutes the longest matched frequent n-gram’s jointly learned contextualized embedding for a token embedding, then caches those embeddings in off-accelerator lookup storage for inference.
tags: [embeddings, n-grams, language-modeling, inference, offloading, sparse-models]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T15:29:19Z }
sources:
  - id: scone-2025
    resource: ../raw/2502.01637_ScalingEmbeddingLayersinLanguageModels/main.tex
    title: "Scaling Embedding Layers in Language Models"
---

# SCONE scalable contextualized offloaded n-gram embeddings

SCONE (Scalable, Contextualized, Offloaded, N-gram Embedding) augments a decoder-only model’s input interface without enlarging its token vocabulary or output head. At each position, it substitutes the longest matched frequent token n-gram’s contextualized embedding; a separate f-gram Transformer produces that vector during training, then its outputs are precomputed into an off-accelerator lookup table for inference.[^scone-2025]

## Input representation

Let $\mathcal V_f$ be selected frequent token n-grams of lengths $2$ through $K$. For an input token $\sigma_i$, SCONE selects the longest suffix $\omega=(\sigma_j,\ldots,\sigma_i)\in\mathcal V_f$, falling back to the ordinary token embedding $\mathcal T(\sigma_i)$ when no such suffix exists. Thus its per-position embedding is

$$
e_i = \begin{cases}
\mathcal T(\sigma_i), & \text{no matching f-gram};\\
\mathcal A_f(\mathcal T(\sigma_j),\ldots,\mathcal T(\sigma_i)), & \text{training};\\
\mathcal F(\sigma_j,\ldots,\sigma_i), & \text{inference}.
\end{cases}
$$

The main Transformer consumes $e_1,\ldots,e_m$ normally and still predicts over the original token vocabulary. The figure’s pipeline makes the boundary explicit: f-grams are local input keys, not output tokens or replacements for the main model’s sequence-level contextualization.[^scone-2025]

## Training-time parameterization

SCONE constructs $\mathcal V_f$ by counting token n-grams through $K$, ranking them by frequency, and retaining a target-sized set. The implementation performs one corpus scan per length and uses a minimum-count filter after the first scan; the authors describe this as BPE-like discovery without repeatedly merging and recounting pairs. At $i$, the f-gram model $\mathcal A_f$ takes the selected short token-embedding sequence and returns the final representation; it is jointly trained with the base token embeddings and the main model.[^scone-2025]

This parameterization avoids instantiating a full billion-row f-gram table on accelerators during training and lets related n-grams share $\mathcal A_f$ parameters. It does add short-sequence Transformer work, predominantly feed-forward work according to the authors. To avoid runtime matching during parallel training, their implementation pre-scans the corpus to tag each position’s longest matching length; batches pad f-grams to their batch maximum and use absolute positions within the f-gram model.[^scone-2025]

## Inference-time lookup boundary

After training, SCONE evaluates $\mathcal A_f$ for every retained f-gram and stores the results as $\mathcal F$. The base token embeddings remain accelerator-resident; the added f-gram table is independent of the dense next-token prediction head and can reside in system memory or on NVMe. The reported in-memory layout is a dense embedding matrix plus a hash dictionary from f-gram to row, while the NVMe layout uses LMDB’s B+ tree to map f-grams directly to vectors.[^scone-2025]

This shifts, rather than eliminates, serving cost: a request must test suffix keys and transfer a selected vector to the accelerator, and large tables require host RAM or storage. The source’s fixed accelerator-FLOPs/memory claim applies to the added f-gram capacity after precomputation; it does not mean fixed total storage, zero lookup latency, or unchanged training cost.[^scone-2025]

## Contrast with direct vocabulary and table scaling

Increasing the base vocabulary also expands the dense output logits layer. In the paper’s GPT-2/WebText sweep, bits per character improved at first and then worsened as vocabulary size reached the largest tested values; over 100M training tokens, the share of entries receiving more than 100 updates was 97.6% for 32K vocabulary versus 7.3% for 2M. Those results motivate SCONE’s learned generator, but do not establish a universal vocabulary-size threshold.[^scone-2025]

[Over-Encoding](over-encoding-hierarchical-n-gram-input-embeddings.md) also retains the base output vocabulary and adds local n-gram input capacity. Its direct hashed tables are materialized during training; SCONE instead learns f-gram representations through $\mathcal A_f$ and materializes the large table only after training. Both still require explicit storage and lookup/communication engineering at scale.[^scone-2025]

## Relationships

- **Specific instance of:** [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md); SCONE is a frequency-selected, neural-parameterized local lookup variant.
- **Contrasts with:** [Over-Encoding hierarchical n-gram input embeddings](over-encoding-hierarchical-n-gram-input-embeddings.md); both preserve base-token decoding, but differ in f-gram selection, table parameterization, and training-time materialization.
- **Modifies the input side of:** [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md), while retaining causal next-token prediction.
- **Evaluated by:** [SCONE evaluation and serving trade-offs](scone-evaluation-and-serving-trade-offs.md).

[^scone-2025]: Da Yu et al., “Scaling Embedding Layers in Language Models,” [LaTeX source](../raw/2502.01637_ScalingEmbeddingLayersinLanguageModels/main.tex), Abstract; Sections 1–3; Appendix “Additional Algorithms,” “Challenges of Scaling Vocabulary Size,” and “Implementation Details”; and bundled figures `ngram-embedding-illustration.pdf`, `olmo_num_ngrams.pdf`, `openwebtext_vocab_size_*.pdf`.
