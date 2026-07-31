---
type: Concept
title: Muon LLM training scaling and operational trade-offs
description: The supplied Muon overview reports lower compute-to-loss requirements than AdamW in one LLM scaling study, while full-matrix orthogonalization complicates distributed training and checkpoint fine-tuning.
tags: [muon, optimizer, scaling-laws, distributed-training, pre-training, mixture-of-experts]
status: draft
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T00:26:20+07:00 }
sources:
  - id: muon-overview-2026
    resource: ../raw/MuonOptimizer.md
    title: Muon Optimizer overview (Vietnamese summary)
---

# Muon LLM training scaling and operational trade-offs

In the supplied overview, the Muon LLM study reports approximately 52% of AdamW's training FLOPs to reach equivalent loss under its compute-optimal scaling setup. This is sample/compute efficiency evidence from a specific architecture, data, schedule, and implementation—not a guarantee of twofold throughput or wall-clock improvement.[^muon-overview-2026]

## Reported scaling and model evidence

The overview describes dense Llama-style runs from roughly 399M to 1.5B parameters and summarizes the fitted comparison as $\mathrm{FLOPs}_{\mathrm{Muon}}\approx0.52\,\mathrm{FLOPs}_{\mathrm{AdamW}}$ for equivalent loss. It also reports Moonlight, an MoE model with 2.24B active and 15.29B total non-embedding parameters, trained on 5.7T tokens. At a 1.2T-token checkpoint, the reported Muon model exceeded an AdamW counterpart on several code and mathematics benchmarks but not every benchmark.[^muon-overview-2026]

Muon saves optimizer-state memory only for the matrix parameters assigned to it: it retains one momentum buffer, whereas AdamW retains first- and second-moment buffers. Total training-memory savings depend on the parameters still managed by AdamW, precision policy, master weights, sharding, and activation memory.[^muon-overview-2026]

## Distributed execution

Newton–Schulz orthogonalization requires a full momentum matrix, which makes straightforward optimizer sharding insufficient. The described Distributed Muon procedure reduce-scatters gradients, updates local momentum shards, gathers the complete matrix for orthogonalization, retains each update shard, updates parameter shards, and all-gathers parameters. The overview estimates communication at roughly 1–1.25 times Distributed AdamW, but realized wall-clock cost remains dependent on matrix packing, kernels, parallelism, and communication overlap.[^muon-overview-2026]

## Limits for adoption

- Muon requires correct parameter grouping and is not a universal replacement for AdamW.
- Full-matrix access complicates use with tensor parallelism, FSDP, and ZeRO.
- It lacks AdamW's per-coordinate second-moment adaptation, so data, batch, and fine-tuning regimes can differ.
- The source reports degraded outcomes when swapping AdamW and Muon between pretraining and fine-tuning; it therefore does not establish Muon as a safe optimizer for arbitrary existing AdamW checkpoints.[^muon-overview-2026]

## Relationships

- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) for the matrix update and hybrid parameter partition.
- **Applies to:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md), since the reported Moonlight result is an MoE training case; it does not eliminate MoE routing or dispatch costs.
- **Qualifies:** [Chinchilla compute-optimal training allocation](chinchilla-compute-optimal-training-allocation.md): optimizer choice can alter empirical compute-to-loss results, so its allocation heuristic is not optimizer-invariant.

## Evidence limits

The source is a secondary Vietnamese overview. Its primary technical report, implementation measurements, and reported benchmark data have not been independently verified in this wiki.[^muon-overview-2026]

[^muon-overview-2026]: “Muon Optimizer overview (Vietnamese summary),” [raw source](../raw/MuonOptimizer.md), Sections 7–11 and 13–15; it cites “Muon is Scalable for LLM Training” (arXiv:2502.16982).
