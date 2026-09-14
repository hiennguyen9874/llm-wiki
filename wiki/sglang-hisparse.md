---
type: Concept
title: SGLang HiSparse Hierarchical Sparse-Attention Memory
description: Hierarchical host-device KV offload for DSA sparse attention with hot GPU buffer, swap-in kernel, and high-concurrency throughput gains.
tags: [sglang, hisparse, sparse-attention, kv-cache, hicache, prefill-decode-disaggregation]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T20:00:00Z }
sources:
  - id: sgl-hisparse
    resource: ../raw/2026-04-10-sglang-hisparse/index.md
    title: 'HiSparse: Turbocharging Sparse Attention with Hierarchical Memory'
---

SGLang HiSparse is an experimental hierarchical memory system for DeepSeek Sparse Attention (DSA) models that keeps the full KV cache in host memory and serves decode from a hot GPU-HBM device buffer, lifting the HBM-capacity limit on batch size to get near-linear throughput scaling at high concurrency[^sgl-hisparse].

## Why sparse attention is still capacity-bound

Top-k sparse attention reduces compute and I/O by attending to only a selected KV subset, but the full-context KV cache must still reside in GPU HBM for fast access even though only a small fraction is active per decode step[^sgl-hisparse].

The result is capacity-bound rather than compute-bound serving: token-generation throughput plateaus early once the KV footprint hits GPU capacity, limiting batch size and long-context throughput[^sgl-hisparse].

## Design

Following the earlier HiCache direction, HiSparse proactively offloads inactive KV entries to host memory while keeping frequently accessed regions in a hot device buffer on GPU HBM to minimize critical-path data movement[^sgl-hisparse].

The design applies to both prefill–decode-disaggregated and colocated deployments[^sgl-hisparse].

```text
prefill Model Executor ── staging KV ──► decode Host Memory (full KV)
                                              │ write-back new KV ▲
                                              ▼                   │
                                     Swap-in Kernel ◄── Top-K Selector
                                              │
                                              ▼
                                     GPU HBM (hot device buffer)
                                              │
                                              ▼
                                     decode Model Executor
```

Workflow inspected from the source overview diagram[^sgl-hisparse]:

- Prefill stages KV into the decode instance's host memory.
- The top-k selector drives a swap-in kernel that moves only missed entries host → GPU hot buffer.
- The decode model executor reads from the hot buffer.
- Newly generated KV is written back to host memory.

### Swap-in kernel

A specialized CUDA kernel[^sgl-hisparse]:

1. Identifies top-k cache misses in the device buffer.
2. Selects eviction candidates via an LRU policy.
3. Updates the page table and fetches required entries from host to device memory.

## Hot-buffer sizing and eviction

Larger hot buffers and LRU eviction directly lower swap-in latency by cutting miss counts[^sgl-hisparse].

Benchmark setup is DeepSeek-V3.2 with `top_k=2048` on LongBenchV2, with miss counts smoothed by a 100-step rolling window[^sgl-hisparse].

Trend inspected from the source miss-count chart[^sgl-hisparse]:

- `Swap-vanilla (2048)` stays highest, roughly 350–700 top-k token misses over 1000 steps.
- `FIFO (4096)`, `Random (4096)`, and `LRU (4096)` all stay substantially lower, roughly 130–450.
- `LRU (4096)` is lowest for most of the run, ending near ~125 versus ~175–200 for FIFO/Random.

## Throughput benchmarks

### Concurrency scaling

Setup: GLM-5.1-FP8 with 32k-input, 8k-output queries on a PD-colocated 8×H200 deployment[^sgl-hisparse].

- Baseline sparse attention without HiSparse plateaus after ~32 concurrent requests at ~770–790 tokens/s[^sgl-hisparse].
- HiSparse scales near-linearly to ~2,640 tokens/s at 256 concurrent requests, over 3× the baseline[^sgl-hisparse].
- At low concurrency HiSparse is slower because sparse-KV loading I/O outweighs memory savings; the chart shows HiSparse below baseline at 8 and 16 requests and crossing over between 32 and 64 requests[^sgl-hisparse].

### Sequence-length sweep

Setup: GLM-5.1-FP8 across input/output lengths on a two-H20 PD-disaggregated deployment; bar labels inspected from the source chart[^sgl-hisparse]:

| Input / Output | Baseline (tok/s) | HiSparse (tok/s) |
| --- | --- | --- |
| 20k / 10k | 752 | 2320 |
| 20k / 20k | 600 | 2280 |
| 40k / 10k | 472 | 2080 |
| 40k / 20k | 368 | 2050 |
| 60k / 10k | 360 | 1820 |
| 60k / 20k | 352 | 1720 |

The source summarizes this as up to 5× throughput improvement on long-context scenarios[^sgl-hisparse].

## Deployment

Enable with `--enable-hisparse` plus `--hisparse-config` JSON carrying `top_k`, `device_buffer_size`, and `host_to_device_ratio`[^sgl-hisparse].

Decode-side requirements in the examples are `--kv-cache-dtype bfloat16` and `--nsa-decode-backend flashmla_sparse`[^sgl-hisparse].

Representative configurations[^sgl-hisparse]:

```bash
# PD-disaggregation decode (recommended), two H20 nodes
--disaggregation-mode decode \
--kv-cache-dtype bfloat16 --nsa-decode-backend flashmla_sparse \
--enable-hisparse \
--hisparse-config '{"top_k": 2048, "device_buffer_size": 6144, "host_to_device_ratio": 10}'

# PD-colocation, single 8xH200 instance
--disable-radix-cache \
--enable-hisparse \
--hisparse-config '{"top_k": 2048, "device_buffer_size": 4096, "host_to_device_ratio": 8}'
```

Full prefill/decode launch commands use `--tp-size 8 --dp-size 8 --enable-dp-attention`, `--chunked-prefill-size 65536`, `--max-running-requests 480`, `--mem-fraction-static 0.8/0.85`, and Mooncake/IB disaggregation flags; see the source for the complete commands[^sgl-hisparse].

Detailed instructions are linked in the source as the [HiSparse guide](https://github.com/sgl-project/sglang/blob/main/docs/advanced_features/hisparse_guide.md)[^sgl-hisparse].

## Model coverage and limits

- Currently supports DSA model families, including DeepSeek-V3.2 and GLM-5.1[^sgl-hisparse].
- Experimental feature; performance and model coverage are expected to keep improving[^sgl-hisparse].
- Designed for high-concurrency throughput; adds I/O overhead from top-k cache misses that dominates at low concurrency[^sgl-hisparse].
- Planned mitigations are better overlap and higher CPU–GPU bandwidth on emerging platforms such as Grace Blackwell systems[^sgl-hisparse].
- Planned extension to broader emerging architectures, including hybrid models, following the earlier HiCache direction[^sgl-hisparse].

## Relationships

- Uses [SGLang HiCache System Design](sglang-hicache-design.md) — prior three-tier GPU/host/storage hierarchy and prefetch/write-back direction that HiSparse specializes for sparse-attention decode.
- Depends on [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — recommended prefill/decode split and KV staging path used by the PD-disaggregated HiSparse deployment.
- Depends on [SGLang Attention Backends](sglang-attention-backends.md) — DSA/NSA sparse-attention execution context, including the `flashmla_sparse` decode backend used with HiSparse.
- Uses [vLLM HiSparse Local KV Offload](vllm-hisparse.md) — vLLM-side counterpart for local host-tier sparse KV with resident/hot resolution; compare coordinator/worker ownership there against SGLang's host-full plus hot-buffer plus swap-in kernel here.
- Uses [vLLM IndexCache for DeepSeek Sparse Attention](vllm-index-cache.md) — complementary DSA optimization that reuses top-k indices across layers rather than offloading KV.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — DeepSeek-V4 Day-0 application extending only the C4 KV pool to CPU for up to 3x long-context throughput.

## Coverage limits

- All four source attachments were inspected as rendered images: throughput-concurrency, workflow overview, miss-count trend, and sequence-length sweep charts; numeric values above the source prose come from chart-label inspection[^sgl-hisparse].
- The linked HiSparse guide, HiCache blog, DSA reference, and hybrid-model PR were not inspected[^sgl-hisparse].
- No accuracy, tail-latency, TTFT/ITL, or CPU–GPU bandwidth measurements beyond the quoted throughput and miss-count trends were in the source[^sgl-hisparse].

[^sgl-hisparse]: HiSparse: Turbocharging Sparse Attention with Hierarchical Memory — `../raw/2026-04-10-sglang-hisparse/index.md`, covering sparse-attention capacity bottleneck, HiSparse hierarchy and swap-in kernel, hot-buffer/eviction miss results, GLM-5.1-FP8 concurrency and sequence-length benchmarks, `--enable-hisparse` PD-disaggregated and colocated launch commands, DSA model coverage, and future work.
