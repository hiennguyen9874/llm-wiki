---
type: Concept
title: Mamba-2 architecture and parallelism
description: Mamba-2 couples the SSD sequence layer with parallel parameter projections, multi-input SSM heads, extra normalization, and Transformer-style distributed-training layouts.
tags: [mamba, mamba-2, parallelism, ssm, systems]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-24T04:51:57Z }
sources:
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
---

# Mamba-2 architecture and parallelism

Mamba-2 uses an SSD sequence layer in a parallel Mamba block: one input projection produces $A$, $B$, $C$, and sequence input $X$ together, then a convolution, SSD mixer, gate, added normalization, and output projection complete the block. This removes Mamba-1's sequential parameter projections and makes the block fit standard tensor-parallel sharding.[^dao-gu-2024]

## Block and head design

In Mamba-1, $A$, $B$, and $C$ are derived after the initial projected sequence stream. Mamba-2 instead projects them in parallel from the block input, analogous to parallel $Q$, $K$, and $V$ projections. The paper reports slightly fewer parameters and better small-scale perplexity for this change, while emphasizing its tensor-parallel benefit. An additional normalization before the output projection improved reported stability in preliminary larger-model experiments.[^dao-gu-2024]

Mamba-2 retains Mamba's multi-input SSM pattern: $X$ has multiple heads while $B$ and $C$ are shared across them; its SSD correspondence is multi-value attention. The authors report this pattern outperformed their parameter-matched multi-contract/multi-query, multi-expand/multi-key, and matched-head variants in their 125M and 360M ablations. Grouped-input SSMs extend that sharing pattern for parallel shards.[^dao-gu-2024]

## Distributed execution

- **Tensor parallelism:** Parallel $A,B,C,X$ projections let each shard retain its local SSM heads, use a shard-local GroupNorm, and require one output all-reduce per block. The paper contrasts this with Mamba-1, where deriving parameters from the sharded stream requires an additional all-reduce.[^dao-gu-2024]
- **Sequence/context parallelism:** Workers process contiguous chunks, pass the final recurrent state to the next worker, and communicate state linearly in worker count. This is the distributed counterpart of SSD's chunk decomposition; it does not require attention's all-to-all query–key block interactions.[^dao-gu-2024]
- **Variable lengths:** Packed sequences can reset state at a boundary by setting the transition factor to zero, avoiding padding without carrying state between examples.[^dao-gu-2024]

## Relationships

- **Extends:** [Mamba selective state spaces and architecture](mamba-selective-state-spaces-and-architecture.md) by reorganizing the original Mamba block’s parameter projections and replacing its selective-scan layer with SSD computation.[^dao-gu-2024]
- **Uses:** [Structured State Space Duality](structured-state-space-duality.md) for the core SSD layer and its chunked computation.
- **Adapts concepts from:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) to name head-sharing patterns; this is an analogy, not ordinary shared-KV decoding.
- **Contrasts with:** [Self-attention computational profile](self-attention-computational-profile.md), whose full token interactions require different context-parallel communication.

## Evidence limits

The architecture and communication patterns are specified by the primary paper. The reported tensor-parallel reduction is a per-block synchronization analysis, not an end-to-end scaling measurement across a disclosed cluster. Its stability and quality effects were tested in the authors' settings and do not isolate every coupled block change.

[^dao-gu-2024]: Tri Dao and Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), Sections 7–8 and Section 9.5.