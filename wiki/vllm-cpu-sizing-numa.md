---
type: Concept
title: vLLM CPU Sizing, NUMA Binding, and Thread Affinity
description: Physical-core sizing, numactl NUMA pinning for GPU workers, and CPU-backend OpenMP affinity.
tags: [vllm, cpu, numa, affinity, deployment]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: opt-cpu-numa
    resource: ../raw/vllm/configuration/optimization.md
    title: Optimization and Tuning
---

vLLM V1 GPU deployments need enough physical CPU cores for API, engine, and worker processes, with optional `numactl` NUMA pinning for GPU workers and separate OpenMP affinity controls for the CPU backend[^opt-cpu-numa].

## Minimum CPU requirements

For `N` GPUs there are at minimum 1 API-server process for HTTP, tokenization, and input processing, 1 engine-core process running the scheduler busy loop, and `N` GPU worker processes — at least `2 + N` processes competing for CPU[^opt-cpu-numa].

Using fewer physical cores than processes causes contention and degrades throughput and latency; the engine-core busy loop is especially sensitive to starvation[^opt-cpu-numa].

Minimum is `2 + N` physical cores (1 API, 1 engine, 1 per worker); allocate more in practice for the OS, PyTorch background threads, and system processes. With hyperthreading, 1 vCPU equals half a physical core, so provision `2 x (2 + N)` minimum vCPUs[^opt-cpu-numa].

With data parallelism or multiple API servers[^opt-cpu-numa]:

```text
Minimum physical cores = A + DP + N + (1 if DP > 1 else 0)
```

where `A` is API-server count (default `DP`), `DP` is data-parallel size, and `N` is total GPUs. Example `DP=4, TP=2` on 8 GPUs needs 4 API + 4 engine + 8 workers + 1 coordinator = 17 processes[^opt-cpu-numa].

Underprovisioning hurts input-processing throughput (tokenization, chat templates, multimodal loading), scheduling latency (CPU scheduler gating GPU dispatch), and output processing (detokenization, networking, streaming). Low GPU utilization with available work can signal CPU contention; more cores and higher clocks can materially improve end-to-end performance[^opt-cpu-numa].

## NUMA binding for multi-socket GPU nodes

On multi-socket servers a GPU worker loses performance when CPU execution and memory drift from the nearest NUMA node. vLLM can pin each worker with `numactl` before the Python subprocess starts so interpreter, imports, and allocator state inherit the policy[^opt-cpu-numa].

Use `--numa-bind` for auto-detected GPU-to-NUMA mapping with `--cpunodebind=<node> --membind=<node>` per worker. Adding `--numa-bind-cpus` switches to `--physcpubind=<cpu-list> --membind=<node>` for custom CPU policy[^opt-cpu-numa].

`--numa-bind-nodes` takes one non-negative NUMA index per visible GPU in GPU-index order. `--numa-bind-cpus` takes one `numactl --physcpubind` CPU list per visible GPU in the same order, e.g. `0-3`, `0,2,4-7`, `16-31,48-63`[^opt-cpu-numa].

```bash
# Auto-detect NUMA nodes for visible GPUs
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --tensor-parallel-size 4 \
  --numa-bind

# Explicit NUMA-node mapping
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --tensor-parallel-size 4 \
  --numa-bind \
  --numa-bind-nodes 0 0 1 1

# Explicit CPU pinning for high-frequency core layouts
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --tensor-parallel-size 4 \
  --numa-bind \
  --numa-bind-nodes 0 0 1 1 \
  --numa-bind-cpus 0-3 4-7 48-51 52-55
```

Notes[^opt-cpu-numa]:

- CLI use forces multiprocessing `spawn` automatically; Python-API use also requires `VLLM_WORKER_MULTIPROC_METHOD=spawn`.
- Auto-detection relies on host NVML and NUMA support and currently covers CUDA/NVML and ROCM platforms; other backends must supply explicit lists, and pass explicit nodes when detection is unreliable.
- Explicit values get light validation; effective semantics remain `numactl` semantics.
- Binding covers GPU execution processes such as `EngineCore` and multiprocessing workers, not frontend API servers or the DP coordinator.
- Containers may need extra permission such as `--cap-add SYS_NICE` under `docker run`.
- These `--numa-bind*` options do not configure CPU-backend affinity.

## CPU-backend thread affinity

The CPU backend uses `VLLM_CPU_OMP_THREADS_BIND`, `VLLM_CPU_NUM_OF_RESERVED_CPU`, and `CPU_VISIBLE_MEMORY_NODES`, not the GPU-oriented `--numa-bind*` options[^opt-cpu-numa].

By default `VLLM_CPU_OMP_THREADS_BIND=auto` derives OpenMP placement from CPU and NUMA topology per CPU worker; set an explicit CPU list to override or `nobind` to disable[^opt-cpu-numa].

## Relationships

- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — API, engine-core, worker, and DP-coordinator counts behind the `2 + N` and `A + DP + N` sizing rules.
- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — DP and `--api-server-count` scaling that raises the process count.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — TP/PP worker layout that NUMA pinning follows.
- Uses [vLLM Python Multiprocessing Method Selection](vllm-python-multiprocessing.md) — `spawn` requirement for NUMA-bound workers.

## Coverage limits

- `../getting_started/installation/cpu.md` runtime-variable and `VLLM_CPU_OMP_THREADS_BIND` guidance was absent from `raw/` and was not inspected[^opt-cpu-numa].
- NVML/NUMA detection internals, `numactl` effective pinning semantics, and container permission policy beyond `--cap-add SYS_NICE` were not verified beyond the source[^opt-cpu-numa].

[^opt-cpu-numa]: Optimization and Tuning — `../raw/vllm/configuration/optimization.md`, CPU Resources for GPU Deployments, NUMA Binding for Multi-Socket GPU Nodes, and CPU Backend Thread Affinity sections covering process minima, hyperthread doubling, DP sizing formula, contention effects, `--numa-bind*` auto/explicit modes with spawn and container notes, GPU-only scope, and `VLLM_CPU_OMP_THREADS_BIND` auto/`nobind` behavior.
