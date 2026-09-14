---
type: Concept
title: vLLM Request Preemption
description: V1 RECOMPUTE preemption on KV shortage with tuning knobs and Prometheus observability.
tags: [vllm, preemption, scheduling, kv-cache, observability]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: opt-preempt
    resource: ../raw/vllm/configuration/optimization.md
    title: Optimization and Tuning
---

When KV-cache space cannot hold all batched requests, vLLM preempts requests to free space and recomputes them when space becomes available again; preemption preserves robustness but recomputation can hurt end-to-end latency[^opt-preempt].

## Default mode

In vLLM V1 the default preemption mode is `RECOMPUTE` rather than `SWAP`, because recomputation has lower overhead in the V1 architecture[^opt-preempt].

A typical warning names the preempted sequence group, `PreemptionMode.RECOMPUTE`, the KV-shortage cause, and a cumulative counter such as `total_cumulative_preemption_cnt=1`, advising more KV memory via `gpu_memory_utilization` or `tensor_parallel_size`[^opt-preempt].

## Tuning

If preemptions are frequent[^opt-preempt]:

- Increase `gpu_memory_utilization` to pre-allocate more GPU cache as KV space.
- Decrease `max_num_seqs` or `max_num_batched_tokens` to run fewer concurrent requests per batch.
- Increase `tensor_parallel_size` to shard weights and leave more per-GPU memory for KV cache, at the cost of possible synchronization overhead.
- Increase `pipeline_parallel_size` to distribute layers and indirectly leave more KV memory, at the cost of possible latency penalties.

## Observability

Monitor preemption counts through vLLM Prometheus metrics, and log the cumulative count by setting `disable_log_stats=False`[^opt-preempt].

## Relationships

- Uses [vLLM Chunked Prefill](vllm-chunked-prefill.md) — shared `max_num_batched_tokens` and `max_num_seqs` batch-sizing controls for scheduler pressure.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — `tensor_parallel_size` and `pipeline_parallel_size` mitigations with their communication and latency costs.
- Uses [vLLM Metrics and Observability](vllm-metrics.md) — Prometheus and logging publishers and preempted-prefill versus preempted-decode interval semantics behind the counters above.
- Uses [vLLM Memory Conservation](vllm-memory-conservation.md) — `gpu_memory_utilization`, context and batch caps, and CUDA-graph tuning as complementary memory controls.

[^opt-preempt]: Optimization and Tuning — `../raw/vllm/configuration/optimization.md`, Preemption section covering autoregressive KV shortage, recompute behavior, warning text, V1 `RECOMPUTE` default, four tuning actions with overhead caveats, and Prometheus plus `disable_log_stats=False` observability.
