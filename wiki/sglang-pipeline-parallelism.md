---
type: Concept
title: SGLang Pipeline Parallelism
description: Pipeline-parallel long-context serving in SGLang with async micro-batching, dynamic chunked prefill, and PP-size tuning.
tags: [sglang, pipeline-parallelism, long-context, chunked-prefill]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:05:02Z }
sources:
  - id: sgl-pp
    resource: ../raw/sglang/advanced_features/pipeline_parallelism.mdx
    title: Pipeline Parallelism for Long Context
---

SGLang uses pipeline parallelism (PP) with dynamic chunked prefill and async P2P micro-batching to reduce time-to-first-token (TTFT) for ultra-long inputs and to scale across nodes with less communication than tensor parallelism[^sgl-pp].

## Why pipeline parallelism

KV-cache techniques remove redundant computation but do not remove the large initial-input (ITL) TTFT cost of ultra-long sequences[^sgl-pp]:

- Tensor parallelism (TP) is the conventional intra-node approach but hits communication bottlenecks in multi-node deployments.
- Pipeline parallelism only communicates at pipeline-stage boundaries, giving better computation-communication overlap than large TP and improving throughput.
- Detailed analysis is in the linked LMSYS chunked-pipeline blog post.

## Async micro-batching implementation

With dynamic chunked prefill, each request's input tokens are partitioned into chunks no longer than the chunked-prefill size, and different chunks of the same request can be processed simultaneously on different nodes[^sgl-pp].

SGLang supported PP since `#5724` and made it compatible with PD disaggregation in `#8846`, but the early implementation left performance headroom[^sgl-pp]. The refactor adds a micro-batching event loop with non-blocking async peer-to-peer communication to overlap GPU computation with CPU metadata work and PP communication, first proposed in `#7979` and redesigned in `#11852`[^sgl-pp].

Key mechanisms[^sgl-pp]:

- **Decoupled sync/async event loop:** the scheduler uses `async_send` in `_pp_send_pyobj_to_next_stage`, returning a `P2PWork` handle instead of blocking; synchronization with `P2PWork.work.wait()` is deferred until `_pp_commit_comm_work`, so the CPU can schedule the next batch or process metadata while data is in flight.
- **Multi-stream execution:** besides the synchronizing `default_stream`, SGLang uses `forward_stream` for forward-pass compute and `copy_stream` for device-to-host transfers; while `_pp_launch_batch` runs the current micro-batch on GPU, the CPU processes the previous micro-batch result with `_pp_process_batch_result`.

## Dynamic chunking

Fixed-size chunked prefill causes pipeline bubbles, especially at large PP sizes, because Transformer runtime is non-uniform: identical chunk sizes take longer when the prefix sequence length `L` is larger, and the misalignment propagates to later stages and degrades scale efficiency[^sgl-pp].

SGLang predicts the next chunk size so that[^sgl-pp]:

```text
Runtime(L + Next Chunk Size) - Runtime(L) = Runtime(Initial Chunk Size)
```

It profiles requests with different ITLs, fits cumulative runtime as a quadratic function of sequence length, solves for the next chunk size at prefix length `L`, and progressively shrinks later chunks as `L` grows to keep stage execution times aligned[^sgl-pp]. The scheduler aligns the predicted value downward to the nearest multiple of `max(--page-size, 64)` for KV-cache memory management and hardware efficiency[^sgl-pp].

Configuration[^sgl-pp]:

- `--enable-dynamic-chunking` enables the mode; `--chunked-prefill-size` sets the initial chunk size and should be set larger than the fixed-mode optimum so there are not too many chunks.
- `SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR` controls adjustment aggressiveness, default `0.75`. `1` follows the quadratic model strictly; larger values change chunk size more aggressively with better potential performance but smaller tail chunks, possible degradation, and more total chunks; smaller values are more conservative with fewer chunks; `0` disables dynamic adjustment and equals fixed-size chunking.

## Tuning guidance

Because hardware, models, and workloads differ, dynamic chunking needs tuning[^sgl-pp]:

1. **Find the fixed-mode baseline:** iterate `--chunked-prefill-size` for the targeted PP size and ITL.
2. **Pick the dynamic initial size:** use 2–3x the optimal fixed size to reduce total chunks and avoid underutilizing “tail chunks”; the predictor keeps later chunks at least 1/4 of the initial size. For extremely large ITL, consider 4x the fixed optimum.
3. **Adjust the smooth factor:** `1.0` follows the model strictly; `0.6–0.85` is the recommended balance between dynamic scaling and hardware stability; `0` reverts to fixed chunking.

Layer-partition tip: when layers do not divide evenly, put the larger partition on the higher PP rank to keep it utilized while waiting for earlier stages, e.g. for DeepSeek-V3.1 `SGLANG_PP_LAYER_PARTITION=15,15,15,16` usually beats `16,15,15,15`[^sgl-pp].

## Long-context best practice

- Start tuning with a small chunked-prefill size such as 4K and increase until optimal for the model, hardware, PP size, and ITL, or size it from hardware capacity with a roofline model[^sgl-pp].
- Enable dynamic chunking plus smoothing-factor tuning for ultra-long ITL; this is experimental, needs tuning effort, and may not suit all workloads[^sgl-pp].

### H20 case study at 128K ITL

With fixed chunk sizes from 2K to 16K on NVIDIA H20, 4K gave the best prefill TTFT for DeepSeek-V3.1 and 6K for Qwen3-235B-A22B-FP8[^sgl-pp]. Scaling the fixed optimum by 3x as the dynamic initial size and tuning the default `0.75` smooth factor gave `0.65` with 12K initial chunks for DeepSeek-V3.1 and `0.8` with 18K initial chunks for Qwen3-235B-A22B-FP8[^sgl-pp].

Example shapes, all with `--disable-radix-cache --mem-fraction-static 0.8 --attention-backend fa3 --max-running-requests 128` on 4 nodes[^sgl-pp]:

- DeepSeek-V3.1 fixed: `--tp 8 --pp-size 4 --chunked-prefill-size 4096`.
- DeepSeek-V3.1 dynamic: `SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR=0.65`, `--tp 8 --pp-size 4 --chunked-prefill-size 12288 --enable-dynamic-chunking`.
- Qwen3-235B-A22B-FP8 fixed: `--tp 4 --pp-size 8 --chunked-prefill-size 6144`.
- Qwen3-235B-A22B-FP8 dynamic: `SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR=0.8`, `--tp 4 --pp-size 8 --chunked-prefill-size 18432 --enable-dynamic-chunking`.

`--disable-radix-cache` was for reproducible benchmarking only and is not recommended in production[^sgl-pp].

## Relationships

- Uses [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — PP implementation is compatible with PD disaggregation; combined PP-plus-PD best practice was still marked “to be added” in the source.
- Uses [SGLang Hyperparameter Tuning](sglang-hyperparameter-tuning.md) — shared `--chunked-prefill-size` / `--mem-fraction-static` / `--max-running-requests` sizing, with OOM versus prefill-speed trade-offs.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — vLLM-side TP/PP strategy and multi-node runtime analog for comparing stage-boundary versus sharded-weight communication.

## Coverage limits

- The LMSYS chunked-pipeline blog, PP PRs `#5724` / `#8846` / `#7979` / `#11852`, and the roofline-model procedure were referenced but not inspected; detail beyond the summary above is outside verified scope[^sgl-pp].
- No measured TTFT numbers beyond the stated optimal chunk sizes and smooth factors, and no PP-with-PD-disaggregation procedure, were in the source; that section was explicitly marked “To be added”[^sgl-pp].

[^sgl-pp]: Pipeline Parallelism for Long Context — `../raw/sglang/advanced_features/pipeline_parallelism.mdx`, covering PP versus TP for ultra-long ITL/TTFT, async micro-batching event loop with `async_send` / `P2PWork` / `_pp_commit_comm_work` and `forward_stream` / `copy_stream` / `_pp_launch_batch` / `_pp_process_batch_result`, dynamic-chunking quadratic model with `max(--page-size, 64)` alignment, `--enable-dynamic-chunking` / `--chunked-prefill-size` / `SGLANG_DYNAMIC_CHUNKING_SMOOTH_FACTOR` semantics, 2–3x initial-size and 0.6–0.85 smoothing tuning steps, `SGLANG_PP_LAYER_PARTITION` placement tip, H20 128K DeepSeek-V3.1 and Qwen3-235B-A22B-FP8 launch shapes, and benchmarking-only `--disable-radix-cache` note.
