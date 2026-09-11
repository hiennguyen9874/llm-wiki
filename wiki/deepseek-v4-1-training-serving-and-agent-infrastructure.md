---
type: Concept
title: DeepSeek-V4.1 training, serving, and agent infrastructure
description: DeepSeek-V4.1 reports disaggregated multimodal training and serving, pipeline-aware CSA2 and Engram execution, bounded SWA replay, asynchronous rollout resumption, and the DSec sandbox platform.
tags: [deepseek-v4-1, distributed-training, llm-serving, kv-cache, reinforcement-learning, agent-sandbox]
status: draft
created: 2026-09-11
generated: { by: llm-wiki-agent/1, at: 2026-09-11T05:35:45Z }
sources:
  - id: deepseek-v41-tech-report
    resource: ../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
---

# DeepSeek-V4.1 training, serving, and agent infrastructure

DeepSeek-V4.1-Flash’s report co-designs multimodal training, compressed-attention execution, cache persistence, and asynchronous agentic post-training. It disaggregates vision encoding from the language-model pipeline, coordinates shared CSA2 state across pipeline stages, separates long-lived global KV from short-lived SWA state, and persists interrupted rollout state at token granularity. Its DSec sandbox platform trades globally coordinated placement for node-enforced admission and workload isolation.[^deepseek-v41-tech-report]

## Multimodal and shared-state training

The vision encoder is replicated outside the LLM parameter tree, splitting each step into vision forward, LLM forward/backward, and vision backward phases. Contrastive-training all-gathers overlap with opposite-modality computation. At ultra-long lengths, images are balanced across context-parallel ranks and loaded once; rollout preprocessing is transferred incrementally and cached for reuse.[^deepseek-v41-tech-report]

CSA2 sharing can cross pipeline stages. Lightweight shadow indexers execute on consumer stages while one logical owner handles optimization and checkpoints; pipeline payloads carry shared representations and sparse routes under context-parallel partitioning; and micro-batch-scoped lifetime tracking retains shared state through recomputation and backward only until its last consumer. Engram tables are row-sharded over dedicated groups, prefetched before pipeline micro-batches, stored and transferred in FP8, and return buffered gradients after backbone backward.[^deepseek-v41-tech-report]

## Serving and persistent cache policy

The serving design uses Encoder–Prefill–Decode disaggregation. The report says fused kernels reduce the common CSA2 Reuse layer to 15 kernel launches in prefill and 11 in decode, but provides no end-to-end throughput comparison.[^deepseek-v41-tech-report]

Global KV remains in persistent storage for at least 72 hours. SWA KV is removed from that store and placed in a distributed host-memory pool with a minutes-scale TTL. If global KV hits after SWA state has expired, **Encoder SWA Bounded Replay** recomputes only the last 128-token window while reusing cached global KV. **Decoder SWA Bounded Replay** passes only that trailing window through decoder layers to reconstruct decode-start SWA state. Both paths deliberately truncate cross-layer SWA dependencies and are approximate; the report identifies cache-resumption boundaries as an uncharacterized robustness risk.[^deepseek-v41-tech-report]

## Asynchronous post-training

Rollout and training time-share the same devices. Sample-level dispatch maintains target concurrency without waiting for complete prompt groups; training can interrupt generation at any token boundary. KV caches and expert routes are persisted per token so rollouts can resume after checkpoint changes without re-prefill, while concatenated routing replay preserves routes generated under successive checkpoints.[^deepseek-v41-tech-report]

The system controls asynchronous bias by limiting per-dataset concurrency, optionally discarding early short samples, bounding the off-policy ratio, and masking excessively stale tokens. Its final full-vocabulary on-policy distillation uses more than 40 architecturally heterogeneous teachers and supports changing teachers, data mixtures, and concurrency while old-configuration samples remain in flight.[^deepseek-v41-tech-report]

## DSec sandbox platform

DeepSeek Elastic Compute (DSec) hosts the synthesized agent environments. It shards machines into isolated scale units and uses independent placement replicas with relaxed global consistency; every node applies a hard local admission check. Worker VMs are bound to sub-NUMA domains, with containers confined to local CPU and memory. The report claims this raised density from roughly 1,000 to more than 2,500 live containers per physical node before measurable end-to-end degradation, under unspecified comparable workloads.[^deepseek-v41-tech-report]

Latency-sensitive tasks use Linux scheduling priority and core scheduling to reduce interference. Per-sandbox AppArmor profiles and eBPF network policies mitigate filesystem destruction, network abuse, answer leakage, and vulnerability exploitation. Crashed environments produce failed trajectories and a repercussion signal; this is a defense-in-depth design, not evidence that the sandbox boundary is complete.[^deepseek-v41-tech-report]

## Relationships

- **Implements:** [DeepSeek-V4.1-Flash architecture and pretraining](deepseek-v4-1-flash-architecture-and-pretraining.md), especially CSA2, Engram, and bounded replay.
- **Supports:** [DeepSeek-V4.1-Flash post-training, evaluation, and interface limits](deepseek-v4-1-flash-post-training-evaluation-and-interface-limits.md) with resumable asynchronous rollouts and isolated task environments.
- **Extends:** [DeepSeek-V4 training and serving infrastructure](deepseek-v4-training-and-serving-infrastructure.md) by replacing exact/long SWA reconstruction with bounded approximate replay and adding multimodal and large-scale agent infrastructure.

## Evidence limits

All capacity, kernel-count, cache-retention, quality-impact, and scalability statements are vendor-reported. The report omits hardware and workload detail sufficient to reproduce end-to-end training or serving efficiency, does not quantify bounded-replay failures, and does not provide a public DSec implementation or security audit. Persisting KV and routing across policy checkpoints also raises numerical and policy-consistency questions beyond the stated stale-token controls.[^deepseek-v41-tech-report]

[^deepseek-v41-tech-report]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” [technical report](../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md), Sections 3 and 5.1–5.2.
