---
type: Concept
title: Kimi K3 lifecycle infrastructure
description: Kimi K3 co-designs fixed-state attention, balanced sparse training, persistent rollout state, resumable sandboxes, hybrid prefix caching, and workload-aware serving across its lifecycle.
tags: [kimi-k3, distributed-training, inference, long-context, agent-infrastructure]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:00:00Z }
sources:
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# Kimi K3 lifecycle infrastructure

Kimi K3’s infrastructure treats model state, expert work, agent environments, and request cost as a connected lifecycle problem. Fixed-size KDA state enables exact context-parallel composition and cheap transfer, while sequence-growing MLA cache, 2.8T sparse weights, and million-token trajectories still require explicit memory, scheduling, and persistence policies.[^kimi-k3-2026]

## KDA execution and context parallelism

FlashKDA overlaps token-parallel intra-chunk computation with head-parallel recurrent propagation for training and prefill. An intra-device planner partitions long sequences across SMs and composes independently evaluated segment transitions.[^kimi-k3-2026]

Across devices, KDA Context Parallelism represents each segment by a cumulative transition $M$ and a locally generated state $\widetilde S$. Segment updates compose associatively as $S\leftarrow MS+\widetilde S$, so ranks exchange fixed-size fragments in one all-gather and reconstruct incoming states with a prefix scan. Unlike additive linear attention, KDA cannot recover cross-rank state by summing local zero-state outputs because its token-dependent transition transforms incoming memory.[^kimi-k3-2026]

## Balanced 3T-class sparse training

Training combines pipeline and virtual stages, expert parallelism, ZeRO-1 data parallelism, pipeline ZeRO-2 gradient sharding, and context parallelism. MoonEP dynamically prefetches redundant experts so every expert-parallel rank receives exactly the same aggregate token count and can use static computation shapes.[^kimi-k3-2026]

The report proves that at most $E/R$ redundant experts per rank guarantee a feasible balanced plan and provides a near-tight adversarial construction. Perfect aggregate rank balance does not imply equal per-expert work within a rank, so a workload-aware grouped-GEMM scheduler remains necessary.[^kimi-k3-2026]

A unified activation manager composes recomputation, blockwise FP8 storage, CPU or remote offload, and prefetch at tensor granularity. Gradient shards are offloaded to CPU; Muon retrieves only the remote shards required for locally owned full matrices through pipelined peer-to-peer communication rather than all-gathering every parameter.[^kimi-k3-2026]

## Persistent million-token agentic RL

Co-located rollout and training create contention between persistent KV caches and training state. A write-back external CPU cache stores idle prefixes only when GPU eviction occurs; KDA states and corresponding MLA blocks move together. Training weights and optimizer state move to NVMe during rollout, and the external cache is released before training.[^kimi-k3-2026]

Runtime throttling adjusts rollout concurrency from active and queued requests plus cache utilization rather than a fixed estimated trajectory length. Partial rollouts also persist environment state in AgentENV microVMs. The report gives best-case incremental checkpoint/resume latencies of 133/49 ms, sub-second launches, and up to $6.5\times$ memory overcommit in its workloads; these figures are implementation- and workload-specific.[^kimi-k3-2026]

## Hybrid serving

KDA recurrent states and MLA KV pages share one paged allocation and eviction system, but reuse requires both cache types at the same prefix boundary. Fine 512-token hash blocks are therefore decoupled from coarse 1,024–6,144-token physical pages; sparse KDA checkpoints are retained at selected hash endpoints, especially turn boundaries. A hit restores the longest boundary available in every KDA group and matching MLA cache.[^kimi-k3-2026]

Speculative KDA decode caches projected draft inputs rather than a full recurrent-state snapshot per draft position. After rejection, accepted states are replayed on-chip before verified and bonus states are committed, reducing state traffic.[^kimi-k3-2026]

At fleet level, consistent hashing assigns a primary cache-affine cluster and a cache-cold secondary. Admission control separates budgets by request class so bursts of million-token traffic cannot consume the capacity reserved for short requests.[^kimi-k3-2026]

## Relationships

- **Operationalizes:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Operationalizes:** [Stable LatentMoE and Quantile Balancing](stable-latentmoe-and-quantile-balancing.md).
- **Supports:** [Kimi K3 agentic post-training](kimi-k3-agentic-post-training.md).
- **Specializes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md).
- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) with shard-selective P2P assembly.

## Evidence limits

Most infrastructure measurements are self-reported and not accompanied by full end-to-end baselines, cluster configuration, or utilization data. Fixed-size KDA synchronization does not make end-to-end context handling constant-cost because periodic MLA, activations, tool histories, and prefill computation still grow with sequence length.[^kimi-k3-2026]

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Section 5 and Appendix E.
