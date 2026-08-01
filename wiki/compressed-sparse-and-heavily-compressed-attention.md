---
type: Concept
title: Compressed sparse and heavily compressed attention
description: DeepSeek-V4’s CSA and HCA replace groups of token KV entries with learned compressed entries, combining sparse retrieval at modest compression with dense retrieval at much heavier compression and a local uncompressed window.
tags: [attention, long-context, kv-cache, sparse-attention, compression]
status: draft
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T00:00:00Z }
sources:
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
---

# Compressed sparse and heavily compressed attention

DeepSeek-V4’s hybrid attention interleaves compressed sparse attention (CSA) and heavily compressed attention (HCA). Both replace multiple token-level KV representations with learned weighted compressed entries and retain a local uncompressed window; CSA uses modest compression plus top-$k$ sparse retrieval, while HCA uses far heavier compression with dense attention over the resulting entries.[^deepseek-v4-2026]

## Compression and retrieval

CSA produces a compressed entry for each $m$ tokens from two weighted, partly overlapping windows, then applies a lightning indexer to select the top-$k$ preceding compressed entries for a query. In the reported models $m=4$; Flash selects 512 entries and Pro selects 1,024. HCA compresses non-overlapping groups at $m'=128$ and attends densely over its compressed entries. Both use shared-KV multi-query attention, low-rank query projection, grouped output projection, and a 128-token sliding-window branch for local dependencies.[^deepseek-v4-2026]

The design applies RMSNorm before core attention, partial RoPE to query/KV/output dimensions, and attention-sink logits. These are model-specific components of a lossy aggregate representation: compression can lower cache size and attention work, but cannot retain all token-addressable information outside the local window.[^deepseek-v4-2026]

## Storage and serving implications

V4 stores RoPE dimensions in BF16 and remaining compressed KV dimensions in FP8; its CSA indexer performs QK work in FP4. Because compression produces entries only at complete block boundaries, an implementation must retain uncompressed tail state. The report’s cache layout therefore separates fixed-size per-request state (sliding-window and unready tail entries) from block-mapped compressed entries, and it permits on-disk storage of complete compressed-prefix entries.[^deepseek-v4-2026]

The report’s stated 1M-context cache and FLOP reductions are relative to DeepSeek-V3.2 or a conventional BF16 GQA baseline under its configurations. They are not a general bound on compression quality, throughput, or latency; sparse indexing, compression, local-state recomputation, and specialized kernels introduce their own costs.[^deepseek-v4-2026]

## Relationships

- **Used by:** [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md).
- **Specializes:** [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) through learned KV aggregation built into attention layers.
- **Uses:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) in shared-KV MQA form.
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which removes sequence-growing token memory rather than retaining compressed sequence entries.

## Evidence limits

The source gives the V4 mechanism and configurations but does not isolate CSA, HCA, compression ratios, sparse selection, local windows, or precision choices in public controlled ablations. Results remain author-reported.[^deepseek-v4-2026]

[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Section 2.3 and Sections 4.5–4.6.
