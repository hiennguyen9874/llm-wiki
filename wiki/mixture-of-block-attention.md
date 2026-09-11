---
type: Concept
title: Mixture of Block Attention
description: MoBA routes each causal query to its current KV block and dynamically selected historical blocks using query-to-mean-key top-k scores, then computes sparse softmax attention without adding model parameters.
tags: [attention, sparse-attention, long-context, block-routing, flashattention]
status: stable
created: 2026-09-11
generated: { by: llm-wiki-agent/1, at: 2026-09-11T04:57:39Z }
sources:
  - id: moba-2025
    resource: ../raw/2502.13189-MoBA/iclr2025_conference.tex
    title: "MoBA: Mixture of Block Attention for Long-Context LLMs"
---

# Mixture of Block Attention

Mixture of Block Attention (MoBA) partitions token-level keys and values into contiguous blocks, scores each block by the dot product between a query and the block’s mean key, and routes the query to top-ranked historical blocks. The query’s current block is always included and receives a causal mask. MoBA changes the access pattern rather than the parameterization or KV representation, so a layer can switch between MoBA and full attention without checkpoint surgery.[^moba-2025]

## Block routing

For sequence length $N$, block width $B$, and $n=N/B$ blocks, MoBA represents block $i$ by its mean key and computes

$$
\bar{k}_i=\operatorname{mean}(K[I_i]),\qquad
s_i=q\bar{k}_i^\top.
$$

After excluding future blocks, it selects top-$k$ blocks and runs ordinary softmax attention over their raw token-level K/V entries. The selected block is therefore a routing unit, not a compressed KV entry: every token inside it remains separately addressable by core attention, and the retained KV state still grows with context.[^moba-2025]

Causality has two parts:

- blocks containing future positions cannot be selected;
- the current block is forced into the read set, but attention within it uses a token-level causal mask so its mean-key router cannot leak future content.

The always-on current block also supplies a local path. Sliding-window attention and attention-sink patterns can be expressed as restricted MoBA routers that always choose recent blocks or initial-plus-recent blocks, but this expressivity statement does not imply that learned routing will recover either pattern reliably.[^moba-2025]

## Execution path

The reported implementation separates current-block causal attention from selected historical-block non-causal attention. It groups queries by assigned KV block, invokes variable-length FlashAttention on each path, restores query order, and combines partial outputs with online-softmax statistics. This imports MoE-style dispatch into attention while preserving exact softmax over the **selected** entries; it is not exact full attention once blocks are omitted.[^moba-2025]

MoBA introduces no learned router parameters in the stated formulation because routing reuses Q and mean-pooled K. It still incurs block pooling, query-to-block scoring, top-k selection, dispatch/gather, and online-softmax combination. For fixed $B$, scoring all query–block pairs is $O(N^2/B)$ and core attention is roughly $O(NkB)$; practical scaling therefore depends on how $B$, $k$, and the number of blocks change with context. “Sub-quadratic” is not a configuration-independent guarantee.[^moba-2025]

## Hybrid use

Because MoBA retains the original attention projections and parameter count, the report studies two transitions:

- **schedule-wise:** train mostly with MoBA, then switch to full attention near the end;
- **layer-wise:** retain full attention in several final layers while earlier layers use MoBA.

The latter is motivated by a hypothesized sparse-gradient problem in supervised fine-tuning when prompt-token losses are masked. This explanation is an author hypothesis; the reported loss curves establish configuration-specific improvement from full-attention layers, not the causal mechanism.[^moba-2025]

## Relationships

- **Uses:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) for variable-length selected-block computation and online-softmax merging.
- **Evaluated by:** [Mixture of Block Attention evaluation and systems trade-offs](mixture-of-block-attention-evaluation-and-systems-trade-offs.md).
- **Precedes and relates to:** the learned block-retrieval branch in [Sparse Attention evolution and architecture comparison](sparse-attention-evolution-and-architecture-comparison.md).
- **Contrasts with:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md), which selects token-level MLA entries, and [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md), which changes remote KV representation through compression.

## Evidence limits

The source is a Moonshot AI technical report with author-run experiments and a linked code repository that was not included in the supplied raw bundle or independently executed here. The LaTeX source, method pseudocode, tables, and ten material mechanism/evaluation figures were inspected; bibliography/style files and appendix scaling plots were not individually inspected because their material numeric results are present in source tables. The report says MoBA supported Kimi long-context requests but gives no production configuration, traffic distribution, end-to-end serving measurements, or independent verification.[^moba-2025]

[^moba-2025]: Enzhe Lu et al., “MoBA: Mixture of Block Attention for Long-Context LLMs,” technical report, arXiv:2502.13189, [LaTeX source](../raw/2502.13189-MoBA/iclr2025_conference.tex), Sections 1–2 and included [routing](../raw/2502.13189-MoBA/fig/running_example.pdf) and [FlashAttention integration](../raw/2502.13189-MoBA/fig/Attn_with_MoBA.pdf) figures.
