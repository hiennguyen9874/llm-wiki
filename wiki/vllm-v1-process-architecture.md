---
type: Concept
title: vLLM V1 Process Architecture
description: API server, engine core, GPU worker, and DP coordinator processes and counts.
tags: [vllm, architecture, multiprocessing, deployment]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: arch-overview
    resource: ../raw/vllm/design/arch_overview.md
    title: Architecture Overview
---

vLLM V1 separates concerns into API server, engine core, and GPU worker processes, plus a conditional data-parallel coordinator, to maximize throughput and clarify CPU sizing[^arch-overview].

## API server process

- Handles HTTP requests including the OpenAI-compatible API, performs input processing such as tokenization and multimodal data loading, and streams results to clients[^arch-overview].
- Communicates with engine core processes over ZMQ sockets in a many-to-many topology, so any API server can route to any engine core[^arch-overview].
- Count: `A`, defaulting to data-parallel size `DP`; overridable with `--api-server-count`[^arch-overview].
- Media loading uses multiple CPU threads controlled by `VLLM_MEDIA_LOADING_THREAD_COUNT` (default 8)[^arch-overview].
- Code: `vllm/entrypoints/launchers/api_server` and `vllm/v1/utils.py`[^arch-overview].

## Engine core process

- Runs the scheduler, manages KV cache, and coordinates model execution across GPU workers in a continuous busy loop[^arch-overview].
- Count: one per data-parallel rank (`DP`, default 1); `--data-parallel-size 4` yields 4 engine cores[^arch-overview].
- Code: `vllm/v1/engine/core.py` and `vllm/v1/engine/utils.py`[^arch-overview].

## GPU worker processes

- Each worker loads model weights, executes forward passes, and manages GPU memory for its assigned GPU[^arch-overview].
- Count: one per GPU; total `N = DP x PP x TP` (`tensor_parallel_size x pipeline_parallel_size` per engine core)[^arch-overview].
- Code: `vllm/v1/executor/multiproc_executor.py` and `vllm/v1/worker/gpu_worker.py`[^arch-overview].

## DP coordinator process

- Present only when `--data-parallel-size > 1`; manages load balancing across DP ranks and coordinates synchronized forward passes for MoE models[^arch-overview].
- Count: 1 if `DP > 1`, else 0[^arch-overview].
- Code: `vllm/v1/engine/coordinator.py`[^arch-overview].

## Process count summary

Total is `A + DP + N (+ 1 if DP > 1)`[^arch-overview]:

| Process type | Count | Notes |
|---|---|---|
| API server | `A` (default `DP`) | HTTP and input processing |
| Engine core | `DP` (default 1) | Scheduling and KV cache |
| GPU worker | `N` | One per GPU |
| DP coordinator | 1 if `DP > 1` | Cross-DP coordination |

Examples[^arch-overview]:

- 4 GPUs with `-tp=4`: 1 API server + 1 engine core + 4 workers = 6 processes.
- 8 GPUs with `-tp=2 -dp=4`: 4 API servers + 4 engine cores + 8 workers + 1 coordinator = 17 processes.

CPU sizing guidance is in [vLLM CPU Sizing, NUMA Binding, and Thread Affinity](vllm-cpu-sizing-numa.md)[^arch-overview].

## Coverage limits

- Process-architecture diagrams for `TP=4` and `TP=2, DP=4` were referenced but their image files were absent from `raw/` and were not inspected[^arch-overview].

## Relationships

- Used by [vLLM Entrypoints](vllm-entrypoints.md) — online serving traffic enters through these processes.
- Uses [vLLM Engine, Worker, and Model Hierarchy](vllm-engine-worker-hierarchy.md) — engine core and workers host the scheduler, model runner, and model.
- Uses [vLLM CPU Sizing, NUMA Binding, and Thread Affinity](vllm-cpu-sizing-numa.md) — physical-core minima and NUMA pinning for the process counts above.

[^arch-overview]: Architecture Overview — `../raw/vllm/design/arch_overview.md`, V1 Process Architecture section; CPU sizing detail is now compiled in [vLLM CPU Sizing, NUMA Binding, and Thread Affinity](vllm-cpu-sizing-numa.md).
