---
type: Concept
title: Over-Encoding hierarchical n-gram input embeddings
description: Over-Encoding augments a base-token embedding with hashed, hierarchical n-gram lookup embeddings, allocating sparse local-context capacity without changing the next-token output vocabulary.
tags: [embeddings, n-grams, tokenization, sparse-models, language-modeling]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T15:25:18Z }
sources:
  - id: over-tokenized-transformer-2025
    resource: ../raw/2501.16975_Over-TokenizedTransformer/main.tex
    title: "Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling"
---

# Over-Encoding hierarchical n-gram input embeddings

Over-Encoding (OE) preserves a model’s base tokenizer and next-token output head, but augments each input position with learned embeddings addressed by the current base token and its preceding $n-1$ tokens. It uses modulo-addressed tables to make the otherwise $V^n$ n-gram address space tractable, making the added parameters sparse lookup capacity rather than a larger dense unembedding layer.[^over-tokenized-transformer-2025]

## Input construction

For base-token IDs $x_1,\ldots,x_T$ from a vocabulary of size $V$, the source maps the suffix ending at position $i$ to an $r$-gram address:

$$
x_i^{(-r)} = \sum_{j=0}^{r-1} x_{i-j}V^j,
$$

with zero padding before the sequence. A direct address is unique when its radix is at least $V$, but would require $V^r$ rows. OE instead reads a bounded $m\times d$ table at $x_i^{(-r)}\bmod m$, which permits collisions.[^over-tokenized-transformer-2025]

The reported default is hierarchical: retain the usual 1-gram embedding and add 2- and 3-gram lookup contributions, then average the contributions. A table may be split along its embedding width into smaller lookup tables, each projected back to model width; the authors give each split table a slightly different row count to avoid identical collision patterns. The ordinary 1-gram input and tied next-token output embedding remain in place.[^over-tokenized-transformer-2025]

## What it changes—and does not

OE adds local context features at the embedding interface. It does not shorten the base-token sequence, replace Transformer contextual processing, or expand the dense output classification vocabulary. Consequently, its added FLOPs can be small relative to the Transformer, but its large tables still consume parameter storage, lookup bandwidth, and distributed communication.[^over-tokenized-transformer-2025]

The source frames a larger output vocabulary separately as **Over-Decoding**: an $n$-gram output objective can be factorized into per-future-token cross-entropies, but it makes output-side prediction denser and was not uniformly helpful at small scale. The paper’s **Over-Tokenized Transformer** combines OE with a sequential multi-token-prediction objective; this is an experimental combination, not a change to OE’s basic input mechanism.[^over-tokenized-transformer-2025]

## Reported design evidence

On the authors’ OLMoE-1.3B ablations, adding only hashed 2-gram lookup degraded less than using it without the base 1-gram embedding, and the 1+2+3-gram hierarchy had the lowest listed loss among their compared 50B-token configurations. With approximately equal table size, choosing an $m$ that was an exact multiple of $V$ had worse reported loss than a nearby 3.2M-row table; the authors attribute this to more collision conflicts. These are configuration-specific ablations, not a proof that hierarchy or coprimality is generally optimal.[^over-tokenized-transformer-2025]

## Evidence limits

This is primary evidence for the method and its author-run experiments, but the bundle contains pseudocode rather than a released training implementation. The claimed vocabulary–loss relationship, collision explanation, and comparisons require independent reproduction. A large input table also changes total parameter and memory accounting even when the per-token dense arithmetic changes little.[^over-tokenized-transformer-2025]

## Relationships

- **Specific instance of:** [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md); OE is a primary-source-documented hierarchical, token-ID-addressed variant.
- **Modifies the input side of:** [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md), while retaining its base-token next-token interface.
- **Can combine with:** [Sequential multi-token prediction](sequential-multi-token-prediction.md); the source calls the combined objective Over-Tokenized Transformer, with qualified results in [Over-tokenized Transformer evaluation and systems trade-offs](over-tokenized-transformer-evaluation-and-systems-trade-offs.md).

[^over-tokenized-transformer-2025]: Hongzhi Huang et al., “Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling,” ICML 2025, [LaTeX source](../raw/2501.16975_Over-TokenizedTransformer/main.tex), Sections 1–3 and Appendix “Pytorch Implementation.”
