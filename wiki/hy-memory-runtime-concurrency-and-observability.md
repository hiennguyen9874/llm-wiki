---
type: Concept
title: Hy Memory runtime, concurrency and observability
description: How the SDK schedules work (write/search loops, SharedRuntime, workload gates, embedding batching) and what it logs, traces and measures.
tags: [agent-memory, hy-memory, concurrency, observability]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# Hy Memory runtime, concurrency and observability

The SDK isolates write and search scheduling on two persistent event-loop threads, shares process-wide resources through `SharedRuntime`, throttles LLM/embedding/graph work with per-loop semaphores, and writes pipeline logs and traces off the hot path (`hy_memory/client.py::_LoopThread`; `runtime.py`; `core/workload.py`).[^hy-memory]

## Concurrency model

- **Two loops**: a write loop and a separate search loop, so write queues cannot starve search scheduling. A persistent loop is needed because local Qdrant binds a file lock to its creating loop (`client.py::_LoopThread` docstring, `_ensure_search_loop`).[^hy-memory]
- **Lost-wakeup defences**: a 50 ms self-scheduled wake-up guard, optional lag probe (`MEMORY_EVENT_LOOP_LAG_MONITOR_ENABLED`), and guarded executor helpers that re-poll every 50 ms (`client.py::_schedule_wakeup_guard`; `utils/async_executor.py`).[^hy-memory]
- **`SharedRuntime`** hoists one write loop, one search loop, one cache pool, the metrics singleton and the observability hook out of per-client ownership; it fixes cross-loop aiomysql corruption seen when two clients bound separate pools to the singleton collector (`hy_memory/runtime.py` docstring; `await SharedRuntime.create(config)`).[^hy-memory]
- **Workload gates** (per-event-loop semaphores, `core/workload.py`): `MEMORY_LLM_GLOBAL_CONCURRENCY`=32, derived LLM 20, dynamic episode 20, graph projection 20, Kuzu projection 1, embedding global 20, reconcile retrieval 16, local reconcile retrieval 2; slow waits log `TRACE_PERF … wait_ms`.[^hy-memory]
- **Embedding batching** (`core/embed_service.py`): `embed()` direct for search latency, `embed_queued()` for writes; queues bucketed by effective `(base_url, api_key)`; flush at `MEMORY_EMBED_BATCH_SIZE`=8 or 100 ms; HTTP is sent outside the lock; LRU vector cache (10k).[^hy-memory]
- Init fails loudly rather than degrading: an unavailable directory-backed graph store raises, and local rerank enabled with an unloadable model raises (`client.py::_initialize_impl`, `_initialize_local_reranker`).[^hy-memory]

## Observability

- **Log**: JSONL at `{MEMORY_LOG_DIR}/{subdir}/{date}.log`, on by default (`MEMORY_PIPELINE_LOG_ENABLED`). **Trace**: `pipeline_logs` table read by `MemoryInspector`, on by default (`MEMORY_PIPELINE_TRACE_ENABLED`). The `memory_operations` audit table is **off** by default. Writes are fire-and-forget (`utils/pipeline_observability.py`; `client.py::_install_pipeline_observability_hooks`).[^hy-memory]
- `MemoryInspector` exposes pipeline logs, extract/search/reconcile logs, full and read traces, read summaries, evolve stats, user stats and system metrics (`hy_memory/inspector.py`).[^hy-memory]
- `MetricsCollector` is a process singleton with minute buckets, 60 s flush, 7-day retention (`hy_memory/metrics.py:30-42`); log files rotate with 15-day retention and contextvar request IDs (`utils/log_setup.py`).[^hy-memory]
- Prompt/LLM content is not logged by default (`MEMORY_LOG_LLM_CONTENT=false`, hashes and lengths only); since 2.0.8 conversation text moved from INFO/WARNING to DEBUG (`docs/perf_trace_README.md` §2; `CHANGELOG.md::2.0.8`).[^hy-memory]

## Relationships

- Part of: [SDK API and config](hy-memory-sdk-api-and-config.md).
- Uses: [Storage backends](hy-memory-storage-and-reembed.md).
- Related: [MemHub privacy](memhub-privacy-and-permissions.md) forces SDK pipeline logs off and flags debug logging as a privacy footgun.

## Coverage and limits

Static inspection (delegated). The latency benefit of the separate search loop is stated as design intent in docstrings; no measurement was run (Unverified).

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
