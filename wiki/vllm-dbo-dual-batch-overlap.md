---
type: Concept
title: vLLM Dual Batch Overlap (DBO)
description: Overlapping MoE sparse all-to-all with compute by splitting batches into paired microbatches on ping-ponging CPU threads.
tags: [vllm, moe, expert-parallelism, data-parallelism, cuda-graphs]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:52:15Z }
sources:
  - id: dbo
    resource: ../raw/vllm/design/dbo.md
    title: Dual Batch Overlap
---

vLLM's Dual Batch Overlap (DBO) overlaps sparse MoE all-to-all communication with surrounding compute by splitting the batch into two microbatches (UBatches) and running each on its own CPU worker thread, with `dbo_yield` points in `FusedMoEModularKernel` ping-ponging the threads so one computes while the other waits on communication[^dbo].

## Scope and motivation

- Core motivation is overlapping sparse all-to-all communication in the MoE layer with surrounding computation[^dbo].
- Currently targets DP+EP deployments only[^dbo].
- Throughout the code `ubatch` is short for microbatch, an ASCII-friendly form of µ-batch[^dbo].

## Overlap schedule

Currently implemented schedule, using `S` shared expert, `A0` MLA qkv proj, `A1` core attn + out proj + MoE gate, `D` dispatch, and `C` combine[^dbo]:

```python
# Comp: |-A0₀-A1₀-||-MLP₁-||-S₁-MLP₀-||-S₀-A0₁-A1₁-|
# Comm: |----D₁---||--D₀--||----C₁---||-----C₀-----|
# Order: D₁ send, A0₀, A1₀, D₁ recv, D₀ send, MLP₁, D₀ recv,
#        C₁ send, S₁, MLP₀, C₁ recv, C₀ send, S₀, A0₁, A1₁, C₀ recv.
# MLP_SHARED_OVERLAP = "mlp_shared_overlap"
```

## Running with DBO

- Enable with `--enable-dbo` on `vllm serve`, in conjunction with `--data-parallel-size N` where `N > 1` and `--enable-expert-parallel`[^dbo].
- Two token-count knobs gate per-batch use[^dbo]:
  - `--dbo-decode-token-threshold`: minimum tokens in a decode-only batch required to enable DBO for that batch.
  - `--dbo-prefill-token-threshold`: minimum tokens in a batch containing at least one prefill required to enable DBO for that batch.
- Currently only supported with DeepEP: DeepEP must be installed and `--all2all-backend` must be `deepep_low_latency` for primarily decode workloads or `deepep_high_throughput` for primarily prefill workloads[^dbo].
- Example two-DP-rank server with expert parallelism and DBO[^dbo]:

```bash
vllm serve deepseek-ai/DeepSeek-V2-Lite --trust-remote-code \
  --data-parallel-size 2 --enable-expert-parallel --enable-dbo \
  --all2all-backend deepep_low_latency
```

- Requires at least two GPUs visible in `CUDA_VISIBLE_DEVICES`[^dbo].

## Components

DBO modifies `GpuModelRunner` and `ModularKernel`, and defines two utility classes: `UBatchWrapper` for thread lifecycle plus CUDA-graph execution, and `UBatchContext` for synchronizing the two UBatch threads[^dbo].

### GPUModelRunner batch split

Batch splitting into microbatches happens in two steps[^dbo]:

1. Coordinate across all DP ranks whether microbatching applies. Microbatching must be uniform: if infeasible for any DP rank it is disabled for all ranks. When all ranks microbatch, total tokens are padded up to the max token count amongst ranks. If any rank would end with an empty second microbatch after padding, microbatching is aborted for all ranks.
2. Slice `CommonAttentionMetadata` in half so there is one attention metadata per microbatch.

### UBatchWrapper

`UBatchWrapper` is a model wrapper responsible for thread, `UBatchContext`, and CUDA-graph management, designed to be relatively transparent to the GPU model runner[^dbo]:

- Runs the model twice, once per microbatch, each invocation inside a UBatch thread. Threads launch in parallel and synchronize via `UBatchContext`; each receives a sliced attention metadata for its half-batch[^dbo].
- Owns DBO CUDA graphs entirely. DBO only supports running with Full CUDA graphs, but once captured a DBO CUDA graph can be replayed without multithreading or CPU synchronization[^dbo].
- `__init__` takes model, `VllmConfig`, `CUDAGraphMode`, and device[^dbo].
- `forward` takes only model arguments and decides whether to run with DBO based on whether a `ubatch_slices` object is present in the `forward_context`; otherwise the model runs without DBO[^dbo].

### UBatchContext

`UBatchContext` wraps `ForwardContext` to synchronize the two UBatch threads and should only be instantiated via `make_ubatch_contexts`[^dbo]:

- When a UBatch thread reaches `dbo_yield`, it pauses and starts the other thread, which runs until it reaches the same `dbo_yield`; this ping-pong continues at each yield until model execution completes[^dbo].
- Current implementation places all `dbo_yield` and `dbo_maybe_run_recv_hook` calls in `FusedMoEModularKernel.forward`[^dbo].
- `make_ubatch_context` initializes the two contexts from two CUDA streams, the preexisting `ForwardContext`s, and a CPU thread barrier, handling all event initialization[^dbo].
- `dbo_register_recv_hook` registers a callback returnable by `FusedMoEPrepareAndFinalizeModular` in the other UBatch thread's context, typically used to wait on an all-to-all kernel[^dbo].
- `dbo_maybe_run_recv_hook` runs that callback when set[^dbo].
- `dbo_yield` puts the current thread to sleep and wakes the other UBatch thread[^dbo].

## Coverage limits

- The standalone `gpu_ubatch_wrapper` and `ubatch_context` lines in the source look like unresolved diagram or file references; no corresponding attachments were found under `raw/` and no claims were inferred from them[^dbo].
- File paths, class member details, CLI flags, and schedule notation are reported as given; implementation files outside `raw/` were not inspected[^dbo].

## Relationships

- Uses [vLLM Fused MoE Modular Kernel](vllm-fused-moe-modular-kernel.md) — all current `dbo_yield` and `dbo_maybe_run_recv_hook` points live in its `forward` method, and recv hooks coordinate its prepare/finalize all-to-all.
- Uses [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) — async DeepEP prepare/finalize backends selected there are the DBO-capable communication substrate.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — DBO requires Full CUDA graphs and replays captured graphs without multithreading or CPU synchronization.

[^dbo]: Dual Batch Overlap — `../raw/vllm/design/dbo.md`.
