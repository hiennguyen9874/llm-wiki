---
type: Concept
title: SGLang GLM-5.2 NVFP4 Optimization
description: 500+ TPS agentic serving for GLM-5.2 NVFP4 via Spec V2 IndexShare MTP, TopK-V2, indexer prologue fusion, and CuTe DSL BF16 GEMMs.
tags: [sglang, glm52, nvfp4, speculative-decoding, sparse-attention, kernels]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T23:00:00Z }
sources:
  - id: glm52-opt
    resource: ../raw/2026-07-13-glm52-optimization/index.md
    title: "Serving GLM5.2 NVFP4 Agentic Workload with SGLang: Reaching 500 TPS in 2 Weeks"
---

SGLang turns day-0 GLM-5.2-NVFP4 support into 500+ TPS single-user interactivity on 8xB300 by combining Spec V2 zero-overhead scheduling with IndexShare MTP reuse and three kernel wins — TopK-V2 selection, indexer prologue fusion, and CuTe DSL BF16 GEMMs — measured on a high-cache-hit agentic coding workload[^glm52-opt].

## Model background

GLM-5.2 keeps the earlier GLM backbone — DSA with a sparse-attention indexer over a DeepSeek-V3-style MoE — and adds IndexShare for DSA plus an MTP head with IndexShare and KVShare[^glm52-opt].

SGLang served the GLM-5.2-NVFP4 checkpoint from day 0 on (Grace) Blackwell hardware using trtllm-gen kernels for both sparse attention and MoE[^glm52-opt].

## Runtime optimization

### Spec V2 zero-overhead scheduling

Spec V2 is SGLang's overlap runtime for speculative decoding: while the GPU runs the current forward on the forward stream, the next step's KV allocation and metadata preparation run on the plan stream[^glm52-opt].

The source reports Spec V2 now on by default, plus four fixes needed to realize the overlap benefit for DSA: making the DSA draft-extend path CUDA-graphable, making `seq_lens_cpu` optional to drop the D2H sync, removing the remaining H2D syncs, and fusing small eager metadata ops in `_apply_cuda_graph_metadata`[^glm52-opt].

With GPU bubbles gone there is no bubble between `run_batch` iterations, for an 11% end-to-end TPS speedup on the reported setup[^glm52-opt].

### IndexShare MTP

GLM-5.2 ships a strong MTP head with accept lengths frequently hitting 5+, valuable for low-latency agentic coding workloads[^glm52-opt].

IndexShare requires reusing the DSA indexer top-k across draft steps: the top-k computed at draft step 0 is held and passed to later steps so they skip recomputing the indexer, cutting draft-step cost by up to ~1.9x at long context with no reported hit to output quality[^glm52-opt].

The seed must come from the draft-extend of the previous `run_batch` iteration; because Spec V2 runs asynchronously, SGLang threads that seed through the overlap scheduler's relay buffer[^glm52-opt].

## Kernel optimization

### TopK-V2

The DSA indexer scores each query over historical KV positions and selects top candidates; following the Lightning-TopK selection-not-sorting design, TopK-V2 replaces the original TopK-V1 sort path[^glm52-opt].

Design[^glm52-opt]:

- Short and medium score rows use register-resident or single-CTA streaming paths.
- Long rows use a cluster of eight CTAs, each building a local 10-bit histogram; FP32 scores are rounded to FP16 and mapped to order-preserving unsigned keys, with the upper 10 key bits selecting one of 1,024 bins.
- A cluster-wide reduction finds the bin containing the 2048th-largest score; values above it emit directly while boundary candidates undergo exact FP32 radix selection with tie-break to return exactly `k`, with runtime `k` up to 2048.
- Selection plus page-table transform from logical positions to physical indexer KV-cache slots is fused in one kernel.
- A planning kernel picks the cluster cutoff from the batch sequence-length distribution and builds a work list for a persistent cluster pool; the plan is generated each forward and reused across DSA layers.

Reported kernel latency at batch size 1 with 6 draft tokens, TopK plus page-table transform fused in both arms[^glm52-opt]:

| ISL | TopK-V1 | TopK-V2 | Speedup |
| --- | --- | --- | --- |
| 80K | 40.7 µs | 17.5 µs | 2.33x |
| 1M | 372.1 µs | 36.6 µs | 10.17x |

The advantage grows with context length, which is why the ISL ablation below holds interactivity flat to 1M tokens[^glm52-opt].

### Indexer prologue fusion

The DSA indexer prologue prepares key state for the indexer KV cache and query state for candidate scoring; the original path used ~12 small kernels and projections[^glm52-opt].

PR #27705 collapses this to 4 kernels in two ways[^glm52-opt]:

- Fuses `wk` and `weights_proj` into one BF16 projection `wk_weights_proj`, splitting the output into key activations and raw head-gate weights reused by the fused query kernel.
- Fuses the elementwise tails: key path LayerNorm + RoPE + FP8 quantization + paged indexer KV-cache store, and query path RoPE + FP8 quantization + head-gate scaling.

Scheduling consequence: the key side runs as one kernel including the store while the query side runs as a separate fused kernel, so the two branches can overlap instead of extending the critical path through a long launch chain[^glm52-opt].

The fused path also drops the Hadamard transform; the source notes the orthonormal transform preserves Q/K inner products before quantization so its main effect was on the quantized representation, and the fused path quantizes untransformed activations directly[^glm52-opt].

Reported decode throughput gain is ~8% at batch size 1 where launch overhead dominates and ~5% at batch size 128[^glm52-opt].

### CuTe DSL BF16 GEMMs

Not all GLM-5.2 matmuls run in NVFP4: attention projections and the shared-expert MLP stay BF16 for accuracy while only routed experts are quantized[^glm52-opt].

PR #30117 adds a selectable CuTe DSL BF16 GEMM backend from FlashInfer TGV GEMM for these BF16 layers[^glm52-opt].

The kernel uses warp specialization — some warps only load, one warp only does MMA, others only store — so load, compute, and store overlap; it pipelines loads aggressively using nearly all shared memory to keep many tiles in flight, which helps small-batch memory-bound decode versus conservative general-purpose pipelining in cuBLAS[^glm52-opt].

A tuning step picks tile size per shape and a pre-measured heuristic falls back to cuBLAS per call when that is faster[^glm52-opt].

At TP4 across decode shapes M=1 to 32[^glm52-opt]:

- Fused QKV projection (M, 2624, 6144, replicated): wins at every batch size, ~1.08x average and 1.13x peak over cuBLAS.
- Attention output `o_proj` (M, 6144, 4096, sharded): wins at every batch size, ~1.05x average and 1.08x peak.
- End-to-end decode speedup ~4% at batch size 1.

## Performance results

Workload is OpenHands multi-turn agentic coding replay: ~80K-token starting prompt, ~220 output tokens per turn, 13 turns per conversation, ~92% aggregate prefix-cache hit rate with real EAGLE acceptance, sweeping concurrency and plotting per-GPU throughput against per-user interactivity[^glm52-opt].

Three reported findings[^glm52-opt]:

- GLM-5.2 is substantially more efficient than GLM-5.1 on the same SGLang release — ~1.4x single-user interactivity and ~1.3x per-GPU throughput on both 4xGB300 and 8xB300 — attributed to IndexShare in DSA layers plus the improved MTP head with IndexShare and KVShare.
- Single-user interactivity is up 18–34% since day 0, reaching 500+ TPS at batch size 1 on 8xB300 through per-token overhead cuts.
- No high-concurrency compromise: peak throughput at batch size 8 is also up 6–11%.

The ISL ablation with simulated accept length 5 shows the indexer payoff: the day-0 path degrades rapidly as the score row grows with context, while TopK-V2 holds interactivity essentially flat out to 1M tokens[^glm52-opt].

## Deployment pointers

Reproduction uses SGLang v0.5.15.post1 with evalscope as benchmark client and custom scripts on the source-linked `glm-nvfp4-blog-repro` branch[^glm52-opt].

Key server settings from the source appendix[^glm52-opt]:

```bash
export SGLANG_OPT_USE_TOPK_V2=1
export SGLANG_ENABLE_MOE_DEFERRED_FINALIZE=1

python3 -m sglang.launch_server \
  --model-path nvidia/GLM-5.2-NVFP4 \
  --tensor-parallel-size 8 \
  --quantization modelopt_fp4 \
  --context-length 90000 \
  --max-running-requests 16 \
  --max-prefill-tokens 8192 \
  --chunked-prefill-size 8192 \
  --cuda-graph-max-bs-decode 16 \
  --mem-fraction-static 0.87 \
  --trust-remote-code \
  --kv-cache-dtype fp8_e4m3 \
  --bf16-gemm-backend cutedsl \
  --reasoning-parser glm45 \
  --tool-call-parser glm47 \
  --speculative-algorithm EAGLE \
  --speculative-num-steps 5 \
  --speculative-eagle-topk 1 \
  --speculative-num-draft-tokens 6 \
  --enable-cache-report
```

TEP variants add `--ep-size 4/8` with matching `--tensor-parallel-size 4/8`; TP4/TP8 cover 4xGB300 and 8xB300 respectively[^glm52-opt].

## What's next

The source scopes this work to low-concurrency high-cache-hit cases and lists high-concurrency follow-ups: ragged TopK-V2 for prefill, faster MQA logits kernel for the indexer, PD disaggregation and expert-parallel tuning under agentic load, HiCache / HiSparse / LayerSplit cache use, and DSpark support for GLM-5.2 to lift speculative acceptance at large concurrency[^glm52-opt].

## Relationships

- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — IndexShare MTP and Spec V2 overlap extend the EAGLE/MTP speculation surface there.
- Uses [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — TopK-V2 selection design evolves the Lightning TopK radix-select path there.
- Depends on [SGLang Attention Backends](sglang-attention-backends.md) — DSA indexer plus trtllm-gen sparse-attention/MoE execution context.
- Uses [SGLang Native ModelOpt Quantization](sglang-modelopt-quantization.md) — NVFP4 quantize-export-deploy path with BF16 retention for attention and shared-expert layers.
- Uses [SGLang Quantized KV Cache](sglang-quantized-kv-cache.md) — FP8 E4M3 KV-cache setting used in the reproduction launch.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — canonical reference for parallelism, memory, quantization, backend, parser, and speculation launch flags.
- Related to [SGLang HiSparse Hierarchical Sparse-Attention Memory](sglang-hisparse.md) — host-device KV offload complement for high-concurrency DSA serving; listed as GLM-5.2 future work.
- Related to [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — confidence-driven variable verify listed as GLM-5.2 future work for large-concurrency acceptance.
- Depends on [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — PD tuning listed as future work for agentic load.
- Depends on [SGLang Expert Parallelism](sglang-expert-parallelism.md) — TEP deployment and MoE execution context for the TP/TEP launch paths.

## Coverage limits

- Ten attachments under `raw/2026-07-13-glm52-optimization/assets/` were enumerated; numeric claims above come from source prose, captions, and chart annotations (day-0 vs v0.5.15 TPS, Spec V2 before/after traces, TopK cluster/histogram/latency, prologue fusion, BF16 GEMM speedup, Pareto, ISL ablation) without pixel-level chart-label verification[^glm52-opt].
- The linked repro branch, evalscope harness, SGLang PR diffs, TGV GEMM source, and lmsys blog URL were not inspected beyond the source summary; exact harness and kernel implementation detail beyond the summary above are not compiled here[^glm52-opt].
- Throughput, latency, speedup, and launch-flag optima are workload-specific to the reported OpenHands 80K/220x13 92%-hit and ISL-ablation setups on B300/GB300, not universal defaults[^glm52-opt].

[^glm52-opt]: Serving GLM5.2 NVFP4 Agentic Workload with SGLang: Reaching 500 TPS in 2 Weeks — `../raw/2026-07-13-glm52-optimization/index.md`, covering GLM-5.2 IndexShare/MTP architecture, Spec V2 overlap and IndexShare MTP runtime work, TopK-V2 / prologue-fusion / CuTe DSL GEMM kernels, OpenHands Pareto and ISL-ablation results, roadmap, acknowledgements, reproduction launches, and PR list.
