---
type: Concept
title: vLLM Startup Optimization
description: Faster time-to-first-token on repeated boots via compile-cache reuse, kv-cache-memory skip, and eager fallback.
tags: [vllm, startup, compilation, kv-cache, cudagraphs]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: opt-startup
    resource: ../raw/vllm/configuration/optimization.md
    title: Optimization and Tuning
---

vLLM shortens repeated-boot time-to-first-token by reusing persisted `torch.compile` artifacts, skipping memory profiling with a logged `--kv-cache-memory` value, or skipping compilation and CUDA-graph capture entirely with `--enforce-eager`[^opt-startup].

## Reuse the compile cache

vLLM persists `torch.compile` artifacts under `VLLM_CACHE_ROOT` (default `~/.cache/vllm`); the cache directory can be copied between machines or baked into a container image[^opt-startup].

Set `VLLM_FORCE_AOT_LOAD=1` to fail loudly instead of silently recompiling on cache miss. Any change to the model, config, relevant `VLLM_*` environment variables, torch build, or GPU model invalidates the cache[^opt-startup].

## Skip memory profiling with `--kv-cache-memory`

On startup vLLM logs the exact `--kv-cache-memory` value that reproduces the current allocation. Passing it back on the next boot skips the memory-profiling measurement and the CUDA-graph memory-estimation pass[^opt-startup].

Trade-offs[^opt-startup]:

- The KV cache is sized to exactly the given value instead of being measured.
- A conservative value caps batch concurrency and therefore throughput.
- An optimistic value fails at allocation time.
- The value is only valid on the same GPU with the same initial free memory; after hardware or co-tenant changes that cause boot OOM, remove the flag to re-profile.

## Serve without CUDA graphs with `--enforce-eager`

`--enforce-eager` skips both compilation and CUDA-graph capture for the fastest possible startup, at the cost of steady-state decode performance[^opt-startup].

Useful for development loops and for measuring how much of a boot is compile and capture[^opt-startup].

## Relationships

- Uses [vLLM Optimization Levels](vllm-optimization-levels.md) — `-O0` through `-O3` presets select the compilation, CUDA-graph, fusion, and autotune defaults that the startup mechanisms above bypass or reuse.
- Uses [vLLM torch.compile Integration](vllm-torch-compile.md) — cache design and invalidation behind `VLLM_CACHE_ROOT` and `VLLM_FORCE_AOT_LOAD`.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — capture pass skipped by `--enforce-eager` and estimated during the profiling pass skipped by `--kv-cache-memory`.
- Uses [vLLM Memory Conservation](vllm-memory-conservation.md) — `enforce_eager` as a memory versus graph-speedup trade-off.

## Coverage limits

- Referenced `../design/torch_compile.md` cache design and `../design/optimization_levels.md` preset tables were not re-ingested here; maintained synthesis is in the linked concepts[^opt-startup].
- Container-baking steps and `VLLM_CACHE_ROOT` sharing procedures beyond copy-or-bake were not detailed in the source[^opt-startup].

[^opt-startup]: Optimization and Tuning — `../raw/vllm/configuration/optimization.md`, Faster Startup section covering `VLLM_CACHE_ROOT` reuse and `VLLM_FORCE_AOT_LOAD=1` invalidation, `--kv-cache-memory` profiling skip with concurrency and validity warnings, and `--enforce-eager` startup versus decode trade-off.
