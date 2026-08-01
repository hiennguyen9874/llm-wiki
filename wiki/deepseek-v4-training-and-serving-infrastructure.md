---
type: Concept
title: DeepSeek-V4 training and serving infrastructure
description: DeepSeek-V4 reports fused wave-based expert parallelism, deterministic kernels, Muon-aware sharding, compressed-attention context parallelism, tensor-level checkpointing, and heterogeneous disk-backed KV-cache management.
tags: [deepseek-v4, distributed-training, llm-serving, mixture-of-experts, reproducibility]
status: draft
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T00:00:00Z }
sources:
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
---

# DeepSeek-V4 training and serving infrastructure

DeepSeek-V4’s report treats long-context sparse-model efficiency as a systems problem: it combines a fused, wave-scheduled expert-parallel kernel; deterministic and batch-invariant kernels; Muon-aware hybrid ZeRO; two-stage contextual parallelism for compressed attention; tensor-level recomputation; and a cache layout that separates compressed prefixes from per-request attention state.[^deepseek-v4-2026]

## Sparse-training execution

MegaMoE divides experts into waves so dispatch, expert GEMMs, and result combination overlap within a single pipeline. Against the paper’s non-fused baselines, the authors report $1.50$–$1.73\times$ general-inference speedup and up to $1.96\times$ for latency-sensitive workloads; the values depend on their GPU/NPU setups and do not measure complete model serving.[^deepseek-v4-2026]

To reproduce behavior across batch position and pipeline phases, the report avoids non-deterministic accumulation paths, uses paired decoding kernels with matched accumulation order, replaces cuBLAS with DeepGEMM for batch-invariant matmuls, and deterministically reduces otherwise atomic attention, MoE, and mHC gradients. Batch invariance and determinism can constrain kernel choice and need not improve raw throughput.[^deepseek-v4-2026]

## Memory and parallelism

Muon’s full-matrix update is reconciled with sharding by assigning complete matrices to bounded ZeRO buckets for dense parameters and flattening same-class expert matrices for distributed assignment. Compressed-attention contextual parallelism first exchanges boundary uncompressed KV entries, compresses them locally, then all-gathers and rearranges variable valid lengths. Tensor-level checkpoint annotations allow the framework to derive minimal recomputation graphs rather than retaining or recomputing entire modules.[^deepseek-v4-2026]

## Serving state

The system maintains a fixed per-request state cache for sliding-window and uncompressed compression-tail entries, plus block-mapped compressed caches whose block boundaries align to the least common multiple of CSA and HCA compression factors. For shared prefixes, complete compressed entries can be stored on disk; sliding-window state can instead be fully cached, periodically checkpointed and partially recomputed, or not cached and regenerated from a trailing dependency span.[^deepseek-v4-2026]

## Relationships

- **Implements:** [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md) and [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md).
- **Implements:** [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) with fused kernels and selective recomputation.
- **Specializes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) through wave-scheduled fused expert parallelism.
- **Specializes:** [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md) with heterogeneous compressed and state-cache policies.

## Evidence limits

All speed, overhead, and reproducibility claims are author-reported. The report does not provide a complete public implementation, cluster configuration, end-to-end serving comparison, or independent audit of its determinism and recovery behavior.[^deepseek-v4-2026]

[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Section 4.
