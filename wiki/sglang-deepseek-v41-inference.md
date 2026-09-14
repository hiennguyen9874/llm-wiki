---
type: Concept
title: SGLang DeepSeek-V4.1 Inference
description: Day-0 SGLang inference for DeepSeek-V4.1 with low-ratio compression plus SWA, shared KV and indexer state, Engram host offload, SWA bounded replay, and fused execution kernels.
tags: [sglang, deepseek-v4.1, sparse-attention, sliding-window-attention, engram, prefix-caching, kernels]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:59:16Z }
sources:
  - id: dsv41-infer
    resource: ../raw/2026-09-10-deepseek-v41/index.md
    title: 'SGLang and Miles Add Day-0 Support for DeepSeek-V4.1'
---

SGLang serves DeepSeek-V4.1 on day 0 with systems for low-ratio KV compression plus sliding-window attention, manifold hyper-connections, Engram memory, cross-layer shared sparse retrieval, host offload for large embedding tables, and bounded SWA replay for prefix reuse and prefill savings[^dsv41-infer].

## Architecture overview

DeepSeek-V4.1 combines local and compressed long-range attention with auxiliary residual and memory paths[^dsv41-infer]:

- **Low-ratio compression and sliding-window attention (SWA).** Each layer keeps an FP8 sliding-window cache for its most recent 128 positions, while selected source layers produce an FP4 compressed representation for long-range attention. Beyond the first two layers, each query attends jointly to its local window and up to 512 compressed positions selected by the indexer. Layers 2–19 use pairwise compression, so KV source layers must retain incomplete pairs across decode steps[^dsv41-infer].
- **Manifold hyper-connections (mHC).** Each sublayer reads from and writes to four parallel residual streams through token-dependent mixing coefficients. A sublayer consumes the coefficients produced by its predecessor, allowing the next coefficient projection to overlap with the current attention or FFN computation[^dsv41-infer].
- **Engram memory.** Layers 1 and 14 retrieve rows keyed by hashed token n-grams from two large FP8 tables and gate the selected rows into the residual stream. Each step reads only a small number of rows, making table placement and lookup overhead more important than dense compute[^dsv41-infer].

## Cross-layer sharing and sparse retrieval

Four KV source layers produce compressed KV and indexer keys; consumer layers read from the most recent KV source instead of storing and generating their own copies, while window KV stays per-layer[^dsv41-infer].

Layer roles inspected from the source SVG: compression ratio 0 on layers 0–1, 2 on layers 2–19, and 1 on layers 20–39; compressed-KV plus indexer-key sources on layers 2, 8, 14, and 20; Engram on layers 1 and 14; and sharing summarized as layers 2–7 reading source 2, 8–13 reading 8, 14–19 reading 14, and 20–39 reading 20[^dsv41-infer].

Two-level selection reuses candidates across layers[^dsv41-infer]:

- **Shared candidates.** Layer 20 selects up to 2,048 blocks of eight positions per query, always retaining the block containing the newest position, and publishes these candidates for later index source layers while selecting its own top-512 from all reachable positions. Later index source layers restrict their top-512 to the shared candidates. When all reachable positions fit within the 16,384-position budget, the candidate filter excludes none of them[^dsv41-infer].
- **Cross-layer selection reuse.** Eight index source layers — layers 2, 8, 14, 20, 24, 28, 32, and 36 per the source SVG — score indexer keys with their own queries and select up to 512 compressed positions per query. The remaining compressed-attention layers reuse the most recent selection without running an indexer[^dsv41-infer].

## Engram optimization

Engram's two FP8 tables hold 189 GiB of weights, but each decode step reads only a small number of rows. SGLang can place the tables in GPU or host memory. Sharding across four GPUs keeps one quarter in each GPU's HBM and needs an all-reduce to assemble each lookup's results[^dsv41-infer].

SGLang supports two host layouts with different communication costs[^dsv41-infer]:

- **Host-sharded layout:** each TP rank holds a shard in host memory and lookups retain the all-reduce.
- **Shared host layout:** all TP ranks access one complete host-memory copy, so each rank gathers all rows it needs and the lookup all-reduce is removed.

Random access to large tables can be limited by address translation, and huge-page backing reduces this overhead. In the evaluated GB300 container, host-sharded tables used anonymous mappings that supported huge pages while shared mappings did not, so automatic layout selection chose host sharding — keeping the all-reduce in exchange for faster host lookups. Best placement depends on CPU–GPU connectivity, huge-page availability, and workload[^dsv41-infer].

In paired tests on 4x GB300 with TP4/EP4, host offload increased KV cache capacity by **36%** with comparable decode throughput and TTFT, using host-sharded tables with huge-page backing and the retained lookup all-reduce; all 28 greedy probe completions matched the baseline. Enable with `SGLANG_ENABLE_DSV41_ENGRAM_HOST_TABLE=1`[^dsv41-infer].

## SWA bounded replay

Sliding-window KV is per-layer. Keeping it for prefix reuse costs cache capacity, while full-sequence prefill computes window states that later decoding no longer accesses directly. The model's deployment note proposes bounded replay to cut both costs[^dsv41-infer].

### Encoder-side bounded replay

Standard prefix reuse needs cached compressed KV, indexer keys, and a valid sliding-window checkpoint. Encoder-side bounded replay removes the checkpoint requirement: the prefix cache keeps compressed KV and indexer keys, while each active request keeps a 128-position window[^dsv41-infer].

On a cache hit, SGLang recomputes the cached prefix's final 128 tokens to rebuild window KV; cached compressed KV and indexer keys stay unchanged. This trades bounded recomputation for lower cache storage and enables prefix reuse without a window checkpoint at the matched position[^dsv41-infer].

### Decoder-side tail-only computation

Layer 20 is the final compressed-KV source; layers 21–39 reuse its compressed KV and indexer keys while computing their own window KV. For each prefill chunk, SGLang runs layers 0–20 over all tokens and layers 21–39 over at most the final 128 tokens of each request[^dsv41-infer].

Layers 0–20 keep full-context computation. In late layers, local attention is restricted to the retained tail because earlier window KV is not computed[^dsv41-infer].

### Correctness boundaries and results

Both modes truncate local attention at the reconstruction boundary, so recomputed hidden states can differ from full prefill even when cached compressed KV is unchanged. Bounded replay is an approximation whose quality must be evaluated empirically[^dsv41-infer].

In paired tests with batches of eight 8K-token prompts, decoder-side replay raised prefill throughput by **1.56x on 8x H200** and **1.37x on 4x GB300**. On 4x GB300, the paired AIME 2026 evaluation measured the same pass@1 with replay off and on — 453/480 correct samples each[^dsv41-infer].

Both modes are opt-in via `--enable-encoder-swa-bounded-replay` and `--enable-decoder-swa-bounded-replay` and can be combined. Encoder replay excludes speculative decoding; decoder tail-only computation does not support input logprobs or full prompt hidden-state capture[^dsv41-infer].

## Kernel and execution optimizations

- **mHC execution and numerical consistency.** Predecessor pre-mix lets the next sublayer's mixing coefficients compute alongside current attention or FFN. SGLang overlaps this work and fuses mixing-statistic reductions with Sinkhorn iterations using a fixed order independent of batch size, keeping each token's coefficients consistent across batch compositions. For small batches, the HC=4 post-mix tiles across hidden dimensions to expose more parallel work[^dsv41-infer].
- **FP4 indexing and TP layout.** Indexer scoring reads directly from the FP4 cache. Indexer heads replicate across TP ranks because sharding this MQA-shaped operation would not reduce key bandwidth and would instead need an all-reduce of scores sized by context length[^dsv41-infer].
- **Fusion with preserved quantization semantics.** The indexer fuses RoPE, FP4 quantization, and packing or cache writes, but must keep the intermediate rounding and scaling of the original computation: removing an intermediate memory write does not permit removing its numerical effect. This cuts launches and intermediate traffic while preserving the quantization sequence[^dsv41-infer].
- **Low-ratio compression.** Compressor projections use BF16 checkpoint weights with FP32 accumulation and output. Ratio-2 decode pooling fuses each completed position pair into one kernel. Compression and indexing overlap attention preparation once inputs are ready, joining before attention consumes their outputs[^dsv41-infer].
- **Single-token projection and Engram fusion.** The grouped output projection uses a specialized BF16 matrix-vector kernel for single-token inputs where the general GEMM path has low utilization. Fused Engram gating cuts FP32 temporary storage, and n-gram hashing runs in one kernel — targeting the small projections and sparse memory ops repeated every decode step[^dsv41-infer].

## Relationships

- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — V4.1 keeps the hybrid sparse-attention plus mHC direction with lower compression ratios, explicit four-source KV sharing, added Engram tables, and SWA bounded replay instead of the V4 ShadowRadix plus C4/C128 plus HiSparse setup.
- Related to [Miles DeepSeek-V4.1 Verified RL](miles-deepseek-v41-rl.md) — training-side day-0 companion covering Megatron shared-state parallelism, FP4/FP8 quantization-aware training, routing replay, and the DAPO validation run.
- Related to [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) — encoder-side bounded replay changes the SWA prefix-reuse boundary by rebuilding window KV from the final 128 cached tokens instead of requiring a stored window checkpoint.
- Related to [SGLang HiSparse Hierarchical Sparse-Attention Memory](sglang-hisparse.md) — Engram host offload is a separate large-table capacity tradeoff from HiSparse C4 KV offload; both free HBM for larger KV capacity at the cost of host-access and communication choices.
- Depends on [SGLang Attention Backends](sglang-attention-backends.md) — execution context for joint local-window plus top-512 compressed attention with FP4 indexer reads.
- Uses [SGLang Quantized KV Cache](sglang-quantized-kv-cache.md) — FP8 sliding-window plus FP4 compressed KV and indexer-key formats underlying the memory and replay tradeoffs.

## Coverage limits

- Layer-role, Engram-placement, and bounded-replay SVG diagrams were inspected as text; the RL training PNG was inspected as a rendered image with numeric claims taken from prose. Remaining numeric values follow the source prose rather than pixel-level chart verification[^dsv41-infer].
- Prefill-throughput and AIME replay results are paired-test snapshots on the stated batch, prompt, and hardware configs, not general speed or quality claims[^dsv41-infer].
- The deployment-note bounded-replay proposal, SGLang cookbook flags, and linked Miles training details beyond the shared source were not separately inspected[^dsv41-infer].

[^dsv41-infer]: SGLang and Miles Add Day-0 Support for DeepSeek-V4.1 — `../raw/2026-09-10-deepseek-v41/index.md`, covering V4.1 architecture, cross-layer KV/candidate/selection sharing, Engram host layouts and 36% capacity result, encoder/decoder SWA bounded replay with throughput and AIME results, and mHC/FP4/fusion/compression/projection kernel optimizations.
