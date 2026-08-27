---
type: Concept
title: Muon LLM training scaling and operational trade-offs
description: The supplied Muon overview reports lower compute-to-loss requirements than AdamW in one LLM scaling study, while full-matrix orthogonalization complicates distributed training and checkpoint fine-tuning.
tags: [muon, optimizer, scaling-laws, distributed-training, pre-training, mixture-of-experts]
status: draft
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-27T03:11:23Z }
sources:
  - id: muon-overview-2026
    resource: ../raw/MuonOptimizer.md
    title: Muon Optimizer overview (Vietnamese summary)
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: qwen38-next-blog
    resource: ../raw/Qwen3.8-Flash-Next/blog.md
    title: Qwen3.8-Flash-Next release blog
  - id: qwen38-next-report
    resource: ../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md
    title: "On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability"
---

# Muon LLM training scaling and operational trade-offs

In the supplied overview, the Muon LLM study reports approximately 52% of AdamW's training FLOPs to reach equivalent loss under its compute-optimal scaling setup. This is sample/compute efficiency evidence from a specific architecture, data, schedule, and implementation—not a guarantee of twofold throughput or wall-clock improvement.[^muon-overview-2026]

## Reported scaling and model evidence

The overview describes dense Llama-style runs from roughly 399M to 1.5B parameters and summarizes the fitted comparison as $\mathrm{FLOPs}_{\mathrm{Muon}}\approx0.52\,\mathrm{FLOPs}_{\mathrm{AdamW}}$ for equivalent loss. It also reports Moonlight, an MoE model with 2.24B active and 15.29B total non-embedding parameters, trained on 5.7T tokens. At a 1.2T-token checkpoint, the reported Muon model exceeded an AdamW counterpart on several code and mathematics benchmarks but not every benchmark.[^muon-overview-2026]

Muon saves optimizer-state memory only for the matrix parameters assigned to it: it retains one momentum buffer, whereas AdamW retains first- and second-moment buffers. Total training-memory savings depend on the parameters still managed by AdamW, precision policy, master weights, sharding, and activation memory.[^muon-overview-2026]

## Distributed execution

Newton–Schulz orthogonalization requires a full momentum matrix, which makes straightforward optimizer sharding insufficient. The described Distributed Muon procedure reduce-scatters gradients, updates local momentum shards, gathers the complete matrix for orthogonalization, retains each update shard, updates parameter shards, and all-gathers parameters. The overview estimates communication at roughly 1–1.25 times Distributed AdamW, but realized wall-clock cost remains dependent on matrix packing, kernels, parallelism, and communication overlap.[^muon-overview-2026]

## Kimi K3 refinements

Kimi K3 orthogonalizes Q/K/V momentum separately per attention head rather than as one full projection, aiming to prevent large-scale heads from dominating the shared update. For distributed optimizer sharding, each rank retrieves only remote shards needed to assemble its locally owned matrices through pipelined P2P communication, avoiding a full-parameter all-gather buffer. The report claims improved stability and lower overhead but does not isolate end-to-end gains.[^kimi-k3-2026]

## Qwen3.8-Flash-Next schedule claim

Qwen refit its scaling law after changing both architecture and optimizer, predicting larger learning rates and batch sizes. On a 10.8B-A0.89B MoE trained for 4T tokens, the predicted 25.2M-token batch ends at loss 1.5702 versus 1.5774 for the previous 12.6M recipe; 37.7M is nearly flat at 1.5707. Ramping from 6.3M to 25.2M by 524B tokens ends slightly worse and requires 18.8% more optimizer steps, so production starts at the target batch.[^qwen38-next-report]

On a 156B-A7B MoE trained for 419B tokens, the predicted $B=8.4$M and $\eta=1.76\times10^{-3}$ setting ends 0.0078 loss below the Qwen3.5 recipe. Nearby settings from $\eta/\sqrt2$ to $\eta\sqrt2$ and +25% batch lie within 0.0007 loss; the predicted setting has the highest seven-task average, 60.55 versus 56.41 for Qwen3.5. These are single author-run evaluations with narrow top-setting margins, not a disclosed general scaling equation or proof that Muon universally removes batch warmup.[^qwen38-next-report]

## Stability stress tests

At constant 4× optimal learning rate on a 25B-A3B MoE, the report records 183 loss spikes per 10K steps and 213 clipping-threshold crossings in 19,932 steps for Qwen3.5/AdamW. Both Muon runs avoid threshold crossings, and Muon plus Gated Residual records zero loss spikes. In an AdamW-controlled 3× test, adding GatedNorm reduces spikes from 32.0 to 3.2 per 10K and crossings from 256 to 20, isolating the multiplicative gate as one contributor rather than attributing all stability to Muon.[^qwen38-next-report]

For the first 276B production tokens, Qwen reports no loss spike for the full recipe, lower gradient variability, and a 0.058 loss gain over its Qwen3.5/Muon baseline. These comparisons share selected controls but change multiple components in the final recipe and provide no independent replication.[^qwen38-next-report]

## Limits for adoption

- Muon requires correct parameter grouping and is not a universal replacement for AdamW.
- Full-matrix access complicates use with tensor parallelism, FSDP, and ZeRO.
- It lacks AdamW's per-coordinate second-moment adaptation, so data, batch, and fine-tuning regimes can differ.
- The source reports degraded outcomes when swapping AdamW and Muon between pretraining and fine-tuning; it therefore does not establish Muon as a safe optimizer for arbitrary existing AdamW checkpoints.[^muon-overview-2026]

## Relationships

- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) for the matrix update and hybrid parameter partition.
- **Applies to:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md), since the reported Moonlight result is an MoE training case; it does not eliminate MoE routing or dispatch costs.
- **Qualifies:** [Chinchilla compute-optimal training allocation](chinchilla-compute-optimal-training-allocation.md): optimizer choice can alter empirical compute-to-loss results, so its allocation heuristic is not optimizer-invariant.
- **Applied by:** [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md), whose technical report describes a jointly refitted architecture/optimizer schedule.

## Evidence limits

The general Muon scaling claims still rely on a secondary Vietnamese overview whose underlying primary study has not been independently ingested. Qwen's technical report provides primary evidence for its own scaling-law validation and stress tests, but no repeated-seed uncertainty, general fitted equation, implementation release, or independent replication.[^muon-overview-2026][^qwen38-next-report]

[^muon-overview-2026]: “Muon Optimizer overview (Vietnamese summary),” [raw source](../raw/MuonOptimizer.md), Sections 7–11 and 13–15; it cites “Muon is Scalable for LLM Training” (arXiv:2502.16982).

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.5 and 5.2.

[^qwen38-next-blog]: Qwen Team, “Qwen3.8-Flash-Next,” [release blog](../raw/Qwen3.8-Flash-Next/blog.md), Optimization section.

[^qwen38-next-report]: Qwen Team, “On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability,” [technical report](../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md), Sections 3.2–3.3, Table 10, and Figures 8–13.
