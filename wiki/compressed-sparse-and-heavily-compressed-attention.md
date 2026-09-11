---
type: Concept
title: Compressed sparse and heavily compressed attention
description: DeepSeek-V4’s CSA and HCA replace groups of token KV entries with learned compressed entries, combining sparse retrieval at modest compression with dense retrieval at much heavier compression and a local uncompressed window.
tags: [attention, long-context, kv-cache, sparse-attention, compression]
status: draft
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-09-11T05:35:45Z }
sources:
  - id: deepseek-v41-tech-report
    resource: ../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
  - id: deepseek-v41-flash-readme
    resource: ../raw/DeepSeek-V4.1-Flash/README.md
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
---

# Compressed sparse and heavily compressed attention

DeepSeek-V4’s hybrid attention interleaves compressed sparse attention (CSA) and heavily compressed attention (HCA). Both replace multiple token-level KV representations with learned weighted compressed entries and retain a local uncompressed window; CSA uses modest compression plus top-$k$ sparse retrieval, while HCA uses far heavier compression with dense attention over the resulting entries.[^deepseek-v4-2026]

## Compression and retrieval

CSA produces a compressed entry for each $m$ tokens from two weighted, partly overlapping windows, then applies a lightning indexer to select the top-$k$ preceding compressed entries for a query. In the reported models $m=4$; Flash selects 512 entries and Pro selects 1,024. HCA compresses non-overlapping groups at $m'=128$ and attends densely over its compressed entries. Both use shared-KV multi-query attention, low-rank query projection, grouped output projection, and a 128-token sliding-window branch for local dependencies.[^deepseek-v4-2026]

The design applies RMSNorm before core attention, partial RoPE to query/KV/output dimensions, and attention-sink logits. These are model-specific components of a lossy aggregate representation: compression can lower cache size and attention work, but cannot retain all token-addressable information outside the local window.[^deepseek-v4-2026]

## Storage and serving implications

V4 stores RoPE dimensions in BF16 and remaining compressed KV dimensions in FP8; its CSA indexer performs QK work in FP4. Because compression produces entries only at complete block boundaries, an implementation must retain uncompressed tail state. The report’s cache layout therefore separates fixed-size per-request state (sliding-window and unready tail entries) from block-mapped compressed entries, and it permits on-disk storage of complete compressed-prefix entries.[^deepseek-v4-2026]

The report’s stated 1M-context cache and FLOP reductions are relative to DeepSeek-V3.2 or a conventional BF16 GQA baseline under its configurations. They are not a general bound on compression quality, throughput, or latency; sparse indexing, compression, local-state recomputation, and specialized kernels introduce their own costs.[^deepseek-v4-2026]

## CSA2 extension

DeepSeek-V4.1’s CSA2 removes CSA’s overlapping $2m$ compression window and absolute positional embedding, and projects indexer K from main KV rather than through a separate hidden-state compression path. Full layers compute KV and indices; Reindex layers share KV but select fresh indices; Reuse layers share both. In the CED decoder, the first Full indexer also chooses up to 2,048 blocks of eight positions, bounding later Reindex searches to 16,384 candidates while the initial scan remains context-linear.[^deepseek-v41-tech-report]

## Relationships

- **Used by:** [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md).
- **Specializes:** [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) through learned KV aggregation built into attention layers.
- **Uses:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) in shared-KV MQA form.
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which removes sequence-growing token memory rather than retaining compressed sequence entries.
- **Extended by:** [DeepSeek-V4.1-Flash architecture and pretraining](deepseek-v4-1-flash-architecture-and-pretraining.md), whose CSA2 shares main KV and indexer state across static Full/Reindex/Reuse layer modes.

## Evidence limits

The V4 report gives the original mechanism and configurations but does not isolate CSA, HCA, compression ratios, sparse selection, local windows, or precision choices in public controlled ablations. The V4.1 technical report specifies CSA2 and explicitly identifies sparse-selection errors as an uncharacterized edge-case risk, but supplies no isolated quality, latency, or cache ablation for its individual changes. Results remain author-reported.[^deepseek-v4-2026][^deepseek-v41-tech-report]

[^deepseek-v41-tech-report]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” [technical report](../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md), Sections 2.3 and 6.

[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Section 2.3 and Sections 4.5–4.6.

[^deepseek-v41-flash-readme]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” [release README](../raw/DeepSeek-V4.1-Flash/README.md), Introduction.
