---
type: Concept
title: Engram conditional-memory architecture
description: Engram injects deterministic hashed n-gram embedding lookup into selected Transformer layers, contextually gates it, and separates its large static table from the dynamic MoE backbone.
tags: [embeddings, n-grams, conditional-memory, mixture-of-experts, offloading, sparse-models]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T15:33:29Z }
sources:
  - id: conditional-memory-2026
    resource: ../raw/2601.07372_ConditionalMemoryviaScalableLookup/main.tex
    title: "Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models"
---

# Engram conditional-memory architecture

Engram is a parametric conditional-memory module for a Transformer/MoE backbone. At selected intermediate layers it hashes a normalized suffix token n-gram into a fixed number of embedding-table rows, then uses the current hidden state to gate the retrieved static vector before residual fusion. This makes local-pattern access deterministic and sparse per token while leaving attention, MoE computation, the normal input embedding, and the output head in place.[^conditional-memory-2026]

## Lookup keys and static memory

A precomputed surjective tokenizer projection maps raw IDs to normalized canonical IDs (the source uses NFKC normalization and lowercasing). The authors report a 23% effective-vocabulary reduction for their 128K tokenizer; this increases sharing but can also deliberately collapse distinctions. The suffix $n$-gram ending at position $t$ is then

$$
g_{t,n}=(x'_{t-n+1},\ldots,x'_t).
$$

For each order $n=2,\ldots,N$ and hash head $k=1,\ldots,K$, a deterministic multiplicative-XOR hash maps $g_{t,n}$ to a row of prime-sized table $E_{n,k}$. Engram concatenates the $K(N-1)$ retrieved vectors. Bounded tables make the combinatorial n-gram space tractable, but collisions remain a mechanism-level limitation rather than being eliminated by multiple heads.[^conditional-memory-2026]

## Contextual fusion in Transformer layers

The lookup vector $e_t$ is static, so Engram derives key and value projections from it and gates the value with the layer hidden state $h_t$:

$$
\alpha_t=\sigma\!\left(\frac{\operatorname{RMSNorm}(h_t)^\top\operatorname{RMSNorm}(W_K e_t)}{\sqrt d}\right),
\qquad \tilde v_t=\alpha_t W_Ve_t.
$$

It applies RMSNorm, a causal depthwise convolution (kernel 4 and dilation equal to the maximum n-gram order in the reported design), SiLU, and a residual connection before the ordinary attention and MoE sublayers. The gate is intended to suppress lookup noise from collisions or polysemy, but that semantic interpretation is an author hypothesis rather than a guaranteed retrieval-correctness property.[^conditional-memory-2026]

The reported backbone uses manifold-constrained Hyper-Connections (mHC). It shares Engram’s table and value projection across the four residual branches, while using one key projection per branch for distinct gates. The module is therefore not intrinsically tied to mHC, but its reported large-scale configuration and ablations are.[^conditional-memory-2026]

## Storage and execution boundary

At training time, tables are sharded across GPUs; active row retrieval and gradient return use all-to-all communication. At inference time, token IDs determine future table addresses before the insertion layer runs. The authors propose fetching from host memory asynchronously while earlier on-device blocks execute, and placing Engram sufficiently deep to create that overlap window. A proposed cache hierarchy would retain frequent Zipf-distributed n-grams in faster tiers and rare entries in slower host or NVMe storage.[^conditional-memory-2026]

This is unlike [SCONE](scone-scalable-contextualized-offloaded-n-gram-embeddings.md), which substitutes a lookup-produced vector at the input interface after training. It is also unlike [Over-Encoding](over-encoding-hierarchical-n-gram-input-embeddings.md), which adds hashed n-gram features directly to token inputs: Engram’s retrieval is fused in intermediate layers and conditioned on an already contextualized hidden state.[^conditional-memory-2026]

## Relationships

- **Specific instance of:** [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md).
- **Complements:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md): Engram spends sparse capacity on deterministic static lookup, whereas MoE selects conditional FFN computation.
- **Uses in the reported backbone:** [Multi-head Latent Attention](multi-head-latent-attention.md) and [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md).
- **Evaluated by:** [Engram evaluation and serving trade-offs](engram-evaluation-and-serving-trade-offs.md).

## Evidence limits

The mechanism and systems design are documented in an author paper. Its stated GitHub link and proposed hierarchical cache were not independently inspected in this ingestion; this page does not claim released-code behavior or production performance. Hashing, normalization, gating, placement, table widths, and offload overlap are configuration choices, not universal properties of n-gram memory.[^conditional-memory-2026]

[^conditional-memory-2026]: Xin Cheng et al., “Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models,” [LaTeX source](../raw/2601.07372_ConditionalMemoryviaScalableLookup/main.tex), Abstract; Sections 1–2; Appendix “Detailed Model Architecture and Hyper Parameters”; and rendered bundled architecture/system figures.