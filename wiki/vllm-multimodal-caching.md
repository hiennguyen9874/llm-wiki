---
type: Concept
title: vLLM Multimodal Caching and Encoder Batch Parallelism
description: Processor and IPC key-replicated versus shared-memory caches with encoder batch-level data parallelism.
tags: [vllm, multimodal, caching, ipc, encoder-parallelism]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: opt-mm-cache
    resource: ../raw/vllm/configuration/optimization.md
    title: Optimization and Tuning
---

vLLM avoids repeated multimodal transfer and processing with automatic processor and IPC caches, and can trade extra encoder memory for throughput by running vision encoders with batch-level data parallelism[^opt-mm-cache].

## Processor caching

Multimodal processor caching is automatically enabled to avoid reprocessing identical multimodal inputs in `BaseMultiModalProcessor`[^opt-mm-cache].

## IPC caching

Multimodal IPC caching is automatically enabled when API (`P0`) and engine-core (`P1`) processes have one-to-one correspondence, avoiding repeated transfer of identical inputs between them[^opt-mm-cache].

Modes[^opt-mm-cache]:

- **Key-replicated cache (default):** keys exist in both `P0` and `P1`, but data resides only in `P1`.
- **Shared-memory cache:** more efficient with multiple workers (e.g. `TP > 1`); enable with `mm_processor_cache_type="shm"`. Keys live on `P0` while data lives in shared memory accessible to all processes.

API-server scale-out disables IPC caching because it breaks the required one-to-one mapping; processor caching is unaffected[^opt-mm-cache].

## Configuration

Set cache size with `mm_processor_cache_gb` (default 4 GiB). An item larger than the budget is served uncached with a warning instead of failing startup; raise the budget to cache such items. Set `mm_processor_cache_gb=0` to disable both IPC and processor caching[^opt-mm-cache]:

```python
# Larger cache
llm = LLM(
    model="Qwen/Qwen2.5-VL-3B-Instruct",
    mm_processor_cache_gb=8,
)

# Shared-memory IPC cache
llm = LLM(
    model="Qwen/Qwen2.5-VL-3B-Instruct",
    tensor_parallel_size=2,
    mm_processor_cache_type="shm",
    mm_processor_cache_gb=8,
)

# Disable caches
llm = LLM(
    model="Qwen/Qwen2.5-VL-3B-Instruct",
    mm_processor_cache_gb=0,
)
```

Placement[^opt-mm-cache]:

| mm_processor_cache_type | Cache type | P0 cache | P1 engine cache | P1 worker cache | Max memory |
| --- | --- | --- | --- | --- | --- |
| lru | Processor caching | K + V | N/A | N/A | `mm_processor_cache_gb * data_parallel_size` |
| lru | Key-replicated caching | K | K + V | N/A | `mm_processor_cache_gb * api_server_count` |
| shm | Shared-memory caching | K | N/A | V | `mm_processor_cache_gb * api_server_count` |
| N/A | Disabled | N/A | N/A | N/A | `0` |

`K` stores multimodal-item hashes; `V` stores processed tensor data[^opt-mm-cache].

## Batch-level data parallelism for encoders

By default TP shards multimodal-encoder weights like language-decoder weights to reduce per-GPU memory and compute. Encoders are small relative to decoders, so TP gains are modest while every-layer all-reduce adds overhead[^opt-mm-cache].

Batch-level data parallelism instead shards batched input data with TP, effectively performing batch DP. Reported gains are about 10% throughput and TTFT at `tensor_parallel_size=8`, plus another 40% for vision encoders using hardware-unoptimized Conv3D versus regular TP. Replicated encoder weights slightly raise memory use and can OOM a barely fitting model[^opt-mm-cache].

Enable with `mm_encoder_tp_mode="data"`[^opt-mm-cache]:

```python
from vllm import LLM

llm = LLM(
    model="Qwen/Qwen2.5-VL-72B-Instruct",
    tensor_parallel_size=4,
    # Vision encoder uses TP=4 to shard input data (effective DP=4);
    # language decoder still uses TP=4 to shard weights.
    mm_encoder_tp_mode="data",
)
```

Notes[^opt-mm-cache]:

- Batch-level DP is distinct from request-level API DP controlled by `data_parallel_size`.
- It is independent of language-decoder DP size used in expert-parallel settings.
- It requires per-model implementation via `supports_encoder_tp_data = True` plus the engine argument.
- Known supported models include dots_ocr, GLM-4.1V and above, InternVL, Kimi-VL, Llama4, MiniCPM-V-2.5 and above, Qwen2-VL and above, and Step3; the source cites one PR per family.

## Relationships

- Uses [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — `BaseMultiModalProcessor` output caching that processor caching accelerates.
- Uses [vLLM Multimodal Inputs](vllm-multimodal-inputs.md) — multimodal request path whose repeated items hit these caches.
- Uses [vLLM Input Processing Performance](vllm-input-processing-tuning.md) — API scale-out disables IPC caching but preserves processor caching.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — weight-sharded TP baseline that encoder batch DP replaces for vision encoders.
- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — request-level `data_parallel_size` DP distinct from encoder `mm_encoder_tp_mode="data"`.
- Uses [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md) — encoder-graph data-parallel execution path using the same `mm_encoder_tp_mode="data"` mode.
- Uses [vLLM Memory Conservation](vllm-memory-conservation.md) — `mm_processor_cache_gb` CPU-RAM sizing shared with that conservation checklist.

## Coverage limits

- Per-model `supports_encoder_tp_data` implementations and cited encoder PR benchmarks were not inspected beyond the source list; treat the supported-model list as source-reported[^opt-mm-cache].
- Processor-cache hashing, eviction, and shared-memory internals beyond the placement table were not detailed in the source[^opt-mm-cache].

[^opt-mm-cache]: Optimization and Tuning — `../raw/vllm/configuration/optimization.md`, Multi-Modal Caching and Batch-level DP for Multi-Modal Encoders sections covering automatic processor/IPC enablement, key-replicated versus `shm` placement with `mm_processor_cache_gb` sizing and disable flag, `P0`/`P1` table, `mm_encoder_tp_mode="data"` semantics with throughput/Conv3D gains and OOM caveat, `data_parallel_size` distinction, `supports_encoder_tp_data` gate, and supported-model/PR list.
