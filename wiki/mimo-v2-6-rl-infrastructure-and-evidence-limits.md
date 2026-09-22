---
type: Concept
title: MiMo-V2.6 RL infrastructure and evidence limits
description: MiMo-V2.6 separates agent execution, trajectory payloads, scheduling metadata, training, and inference while replaying rollout decisions to support heterogeneous million-token RL workloads.
tags: [mimo-v2-6, rl-infrastructure, agent-harness, distributed-training, training-inference-consistency]
status: stable
created: 2026-09-22
generated: { by: llm-wiki-agent/1, at: 2026-09-22T15:21:59Z }
sources:
  - id: mimo-v2-6-report-2026
    resource: ../raw/MiMo-V2.6/MiMo_V2_6_technical_report.md
    scope: ../raw/MiMo-V2.6/
    kind: paper
    title: "MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement"
---

# MiMo-V2.6 RL infrastructure and evidence limits

MiMo-V2.6's reported RL stack separates agent lifecycle, trajectory storage, lightweight scheduling, inference, and training. Its core systems principle is to retain heavy, heterogeneous rollout state in distributed storage and context caches while moving compact metadata through the control plane, then replay rollout-time routing and sampling choices during training.[^mimo-v2-6-report-2026]

## Trajectory and agent execution model

An Agent Loop owns environment setup, interaction, reward evaluation, and cleanup, while external harnesses call a token-in/token-out endpoint. Trajectories use four levels—Sample → Sequence → Context → Segment—so one grouped prompt can have multiple agent executions, concurrent dialogue branches, and turn-level model/tool data. Only model-generated segments enter the loss; rule-triggered masking and advantage shaping can remove infrastructure failures or local behavior errors at the appropriate level.[^mimo-v2-6-report-2026]

The Harness Pool hosts many Agent Loops and harness instances as tenants inside fixed-size persistent Ray actor pools. This avoids one actor/file descriptor per rollout; tenants share an event loop and service objects, while blocking environment and tokenization work moves to background threads. Different harness codebases occupy separate pools, and harness code, behavior configuration, and environment settings remain independently configurable.[^mimo-v2-6-report-2026]

## Payload Porter and multimodal data

At rollout completion, heavy data—tokens, log probabilities, MoE routes, top-p candidate sets, and images—are written once to a distributed object store. The driver schedules with scalar rewards, context lengths, and payload keys; asynchronous graders can rewrite rewards, and packers fetch only rows and context-parallel windows needed by a tensor-parallel group. This avoids gathering or padding the full batch on one driver.[^mimo-v2-6-report-2026]

Multimodal requests transmit only newly introduced images while cached visual tokens represent history. For training, image items are balanced across replicated vision encoders independently of token placement, then embeddings are redistributed to the ranks that own corresponding tokens. This separates pixel movement from text packing but introduces a cross-rank redistribution stage.[^mimo-v2-6-report-2026]

## Sample Mixer

The Sample Mixer targets a fixed per-source training distribution despite a reported 90× range in mean generated tokens and 66× range in active rollout duration across 25 sources. It combines: adaptive per-source concurrency from target count, acceptance rate, and duration; weighted scheduling that blends long-run demand with current-batch deficit; rank placement constrained by estimated KV capacity and inference concurrency; and one-step replay after startup or recovery for selected slow sources.[^mimo-v2-6-report-2026]

Partial rollout keeps the batch saturated by pausing unfinished sequences and resuming them after training, at the cost of policy staleness and re-prefill after an update. The report's failure analysis shows that duration-estimate bias after restart exhausted GPU and pinned-host KV pools, and later harness-specific length skew repeated the problem. Replay and predictive dispatch therefore mitigate, but do not eliminate, heterogeneous-tail risk.[^mimo-v2-6-report-2026]

## Training–inference consistency and optimization

SGLang supplies inference and Megatron-LM training. Experts are quantized/dequantized after each update to match rollout-time MXFP4 kernel constraints. Rollout Routing Replay records discrete MoE expert choices for training, while each sampled token's top-p candidate set is recorded so training probability is renormalized over the same support. These controls replay execution choices; they do not make the two numerical engines identical in every operation.[^mimo-v2-6-report-2026]

Persistent per-context caches retain KV, routes, candidate sets, and visual history across turns. Idle state moves from HBM to pinned host memory on side CUDA streams. Rollouts use an RL-adapted FP8 DFlash block-6 drafter: the report claims 31.3% greater accepted length than inherited MTP-3, about 6% more global throughput than block-8, and about 10.3% more per-node throughput than its baseline on the long-context workload. These figures are workload-specific and lack hardware and full baseline disclosure.[^mimo-v2-6-report-2026]

At one-million-token training context, context-parallel SWA layers exchange only reachable window KV, while periodic global-attention layers remain full-context. Optimizer state is CPU-resident, and policy-gradient/OPD loss plus optional metrics are fused. Reported run failures still include GPU double-bit errors, Kubernetes and grader outages, MoE micro-batch imbalance above 30× mean on one expert-parallel rank, and CPU OOM during late-run packing.[^mimo-v2-6-report-2026]

## Open release evidence

The report says Xiaomi releases a Qwen3.5-9B derivative SFT-tuned on 77.4B generated tokens, approximately 7K RL tasks across code/cyber/general/visual domains plus about 1K music tasks, verifiers, a framework, and mini-harnesses. In report tables, domain-specific GRPO improves all 11 listed SFT-to-RL evaluations; separate four-harness coding RL improves all 21 dataset–harness pairs over SFT. These experiments support portability within the authors' released-resource setup, but the supplied local package contains only the report and images, not the claimed artifacts.[^mimo-v2-6-report-2026]

## Relationships

- **Supports:** [MiMo-V2.6 scaled agentic reinforcement learning](mimo-v2-6-scaled-agentic-rl.md).
- **Runs:** [MiMo-V2.6 omni-modal hybrid-SWA architecture](mimo-v2-6-omnimodal-hybrid-swa-architecture.md).
- **Uses:** [DFlash block-diffusion speculative decoding](dflash-block-diffusion-speculative-decoding.md) for high-concurrency rollout acceleration.
- **Uses:** [Group Relative Policy Optimization](group-relative-policy-optimization.md) and on-policy distillation as training workloads.

## Evidence limits

The report is primary design evidence but does not provide component APIs, complete cluster topology, hardware counts, source code, runnable configurations, or controlled end-to-end ablations for most infrastructure choices. Static inspection covered the complete report; all 31 referenced figures were inventoried, four material diagrams were directly inspected, and the remainder were represented by captions, tables, or surrounding prose rather than direct visual review. No code was executed. Fourteen unreferenced hash-named images were excluded as apparent extraction by-products. Release URLs, versions, licenses, and immutable revisions are absent from the supplied package, so availability and reproducibility claims were not independently verified.[^mimo-v2-6-report-2026]

[^mimo-v2-6-report-2026]: Xiaomi LLM-Core, “MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement,” [technical report](../raw/MiMo-V2.6/MiMo_V2_6_technical_report.md), Sections 5.5–7.2, Equations 6–7, Tables 4–7, and Figures 14–17.
