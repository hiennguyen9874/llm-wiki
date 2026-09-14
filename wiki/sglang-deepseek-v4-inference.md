---
type: Concept
title: SGLang DeepSeek-V4 Inference
description: Day-0 hybrid sparse-attention inference for DeepSeek-V4 with ShadowRadix prefix caching, in-graph speculative metadata, HiSparse C4 offload, fused kernels, and parallel deployment.
tags: [sglang, deepseek-v4, hybrid-attention, shadowradix, prefix-caching, speculative-decoding, hisparse, kernels, parallelism]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:59:16Z }
sources:
  - id: dsv4-infer
    resource: ../raw/2026-04-25-deepseek-v4/index.md
    title: 'DeepSeek-V4 on Day 0: From Fast Inference to Verified RL with SGLang and Miles'
  - id: glm52-opt
    resource: ../raw/2026-07-13-glm52-optimization/index.md
    title: 'Serving GLM5.2 NVFP4 Agentic Workload with SGLang: Reaching 500 TPS in 2 Weeks'
---

SGLang is the first open-source stack to serve DeepSeek-V4 (1.6T Pro, 284B Flash) on launch day, with systems purpose-built for hybrid sparse attention, manifold-constrained hyper-connections (mHC), and FP4 expert weights[^dsv4-infer].

## Model key features

DeepSeek-V4 extends DeepSeek-V3.2 along three axes[^dsv4-infer]:

- **Hybrid sparse attention**: each layer mixes sliding-window attention (SWA) over the last 128 raw tokens with one of two compression mechanisms — C4 (top-512 sparse over 4:1-compressed KV) or C128 (dense over 128:1-compressed KV) — keeping the 1M-token context window tractable[^dsv4-infer].
- **mHC (manifold-constrained hyper-connections)**: a generalization of standard residual connections that improves gradient flow and representation quality[^dsv4-infer].
- **FP4 expert weights**: native FP4 MoE experts for efficient serving on Blackwell hardware[^dsv4-infer].

Per-layer attention scope inspected from the source diagram (N = 1024 example): raw sequence with current query, SWA covering the last 128 raw tokens at full precision, plus either C4 sparse compressed cells with an inflight-token tail or C128 dense compressed cells with an inflight-token tail[^dsv4-infer].

## ShadowRadix prefix caching

Each compression layer carries a state pool holding in-progress compression state, so three heterogeneous KV pools (SWA / C4 / C128) plus two compression-state pools must stay coherent across prefill, decode, and speculative decoding — breaking traditional prefix-caching assumptions[^dsv4-infer].

ShadowRadix is the native prefix-caching mechanism for this hybrid layout[^dsv4-infer].

**One core idea.** A radix tree indexes virtual full-token slots — a unified coordinate system shared by all layers — and each slot projects shadows (per-pool index mappings) into the physical pools[^dsv4-infer]. Compression-state ring buffers sit in their own pool, with a second-level arithmetic shadow mapping each ring slot from the SWA page index — logically nested inside SWA, physically independent[^dsv4-infer]. Lifetimes decouple through **tombstoning**: a node's SWA slots are freed once the sliding window moves past it, while its C4/C128 shadows stay alive and shareable — a 10k-token request keeps only 128 SWA tokens plus its full C4/C128 compressed KV, and that compressed KV is what prefix-matching requests reuse[^dsv4-infer].

Storage layout inspected from the source diagram: source row of 4 pages (1024 raw, 256 slots/page, bookkeeping only); Shadow A (SWA pool, window 128) with tombstoned prefix pages and live suffix pages plus nested C4 ring (8 slots, 16 tokens/slot) and C128 ring (128 slots, 1 token/slot); Shadow B (C4 KV pool, 64 cells/page, 1:1 to source, survives SWA tombstone); Shadow C (C128 KV pool, 2 cells/page, 1:1 to source, survives SWA tombstone)[^dsv4-infer].

Mechanics[^dsv4-infer]:

- **Two-counter lock** per node: `full_lock_ref` covers the source (and therefore its C4/C128 shadows), while `swa_lock_ref` tracks only whether the node still falls inside someone's sliding window; when the SWA counter hits zero the node's SWA slots drop but the node stays in the tree and its compressed shadows keep serving prefix matches[^dsv4-infer].
- **SWA-safe matching** requires 128 consecutive live tokens from the match point before extending into the window[^dsv4-infer].
- Nested ring shadows inherit reclamation for free since a ring slot's address is `swa_page * ring_size + pos % ring_size`: releasing an SWA page automatically invalidates the rings inside it, and ring sizes are picked so MTP rollback cannot race a wrap[^dsv4-infer].
- **Speculative decoding works without design change** except one fix: draft tokens are written into the ring before verification decides acceptance, so a rejected-then-retried step can wrap and overwrite live-window slots — **doubling ring sizes under spec** (C4 8 → 16, C128 128 → 256) leaves enough headroom that in-flight speculative writes land outside the active window, so EAGLE works out of the box[^dsv4-infer].

## Speculative decoding

DeepSeek-V4 ships a single-layer MTP head — a separately trained DSv4 decoder layer running SWA-only attention (no compressor, no indexer), combining the previous-step hidden state (`h_proj`) and next-token embedding (`e_proj`) as input; SGLang supports it Day-0[^dsv4-infer].

The systems work sits one level below: hybrid-attention metadata is heavy, and eager preparation on the scheduler stream becomes the launch bottleneck under speculative decoding — so preparation is fused into the CUDA graph for both draft and verify passes[^dsv4-infer].

- **In-graph metadata preparation.** Per-pass metadata (SWA page indices, shadow-mapped pool slots, compressor/indexer plans, per-pool write locations) is index arithmetic over page tables and lengths that fits device kernels; each captured graph takes only raw batch state as per-replay input (active requests, current lengths, new-KV destinations) copied into fixed buffers, captured kernels rebuild the rest inside the graph, and Python never touches the per-pass path during replay[^dsv4-infer].
- **Overlap scheduling.** CPU-side work (result processing, batch preparation, deallocation) runs in parallel with GPU execution[^dsv4-infer].

Combined with ShadowRadix, this keeps decode throughput essentially flat from 4K to 900K context — under 10% drop on both B200 (199 → 180 tok/s) and H200 (266 → 240 tok/s), close to the full 1M window[^dsv4-infer].

## HiSparse for C4 layers

HiSparse offloads inactive KV to CPU memory for larger batches and higher throughput, and fits naturally with C4 layers: each step the indexer top-k touches only a small fraction of compressed positions, so most C4 KV is inactive and can live on CPU[^dsv4-infer]. C128 is dense (every position touched) and SWA is already small (128 tokens), so neither benefits from offload[^dsv4-infer]. A CPU memory pool extends just the C4 KV pool, improving long-context serving token capacity and throughput by up to 3x[^dsv4-infer].

Reported setup is DeepSeek-V4-Flash on 2×B200, 200K-input / 20K-output, `swa_full_tokens_ratio=0.001`: the GPU keeps small device buffers for the active C4 working set while a larger pinned CPU mirror holds full-context KV; the HiSparse coordinator swaps missed pages in and evicts inactive GPU pages under LRU, and newly generated tokens are asynchronously backed up to the CPU mirror[^dsv4-infer].

## Fast kernel integrations

- **New FlashMLA path for hybrid attention**: SWA over the local window plus extra attention over C4 (sparse top-k) or C128 (dense) run in a single fused kernel call taking both `k_cache` and `extra_k_cache` with respective indices, sharing metadata construction; targets Hopper/SM90 and Blackwell/SM100[^dsv4-infer].
- **FlashInfer TRTLLM-Gen fused MoE for MXFP8 × MXFP4**: pairs MXFP8 activations with MXFP4 expert weights for small-batch MoE decode sensitive to expert-weight bandwidth, adapting SGLang's weight/scale layout; Blackwell-only path relying on FP4 tensor-core machinery and tiled/persistent execution[^dsv4-infer].
- **TileLang mHC kernels with split-K**: mHC mixes `hc_mult` parallel branches per token with Sinkhorn-normalized GEMM-output mixture weights; at small-batch decode the pre-GEMM TileLang kernel bottlenecks on limited parallelism, so the two-stage split-K kernel (`mhc_pre_gemm_sqrsum_splitk_kernel`) partitions K across CTAs, plus a fused `mhc_pre_big_fuse_tilelang` path combining RMSNorm, Sinkhorn, and residual mixing with PDL[^dsv4-infer].
- **DeepGEMM Mega MoE**: fuses EP dispatch, first FP8×FP4 expert GEMM, SwiGLU, second FP8×FP4 expert GEMM, and EP combine into one symmetric-memory mega-kernel overlapping NVLink communication with tensor-core compute; Mega MoE needs transformed FP4 expert weights with UE8M0 scales, so the EP/MoE activation path consumes the transformed layout directly to avoid two resident expert copies while keeping both DeepEP and Mega MoE paths available[^dsv4-infer].

## Flash Compressor and Lightning TopK

**Flash Compressor** fuses the naive 5-stage compression chain (softmax-weighted averaging over per-token scores) into one on-chip pass — HBM round-trips 5 → 2 — with warp-local softmax for C4 and one CTA-wide reduction for C128, reaching up to 80% of peak memory bandwidth on H200 and over 10× a naive PyTorch pipeline[^dsv4-infer].

**Lightning TopK** replaces global sort for the indexer's top-k (256K candidates per request at 1M context with 4:1 compression; naive path exceeds 100 µs at batch 1, more than indexer GEMM and sparse-attention kernel combined) with a cluster-of-8 radix-select reduction: each CTA builds a local 10-bit radix histogram, the cluster reduces histograms to pick a threshold admitting exactly K = 512, then each CTA scatters only above-threshold entries — about 15 µs at small batch, still performant at large batch, using CUDA cluster launch with async copy to avoid HBM cross-CTA sync[^dsv4-infer].

TopK-V2 carries this selection-not-sorting design to GLM-5.2 DSA; see [SGLang GLM-5.2 NVFP4 Optimization](sglang-glm52-optimization.md)[^glm52-opt]. It keeps register/single-CTA paths for short rows, uses an eight-CTA 10-bit-histogram plus exact FP32 radix tie-break for long rows with runtime `k` up to 2048, fuses selection with page-table transform, and reuses a per-forward plan across DSA layers — 40.7 µs to 17.5 µs at 80K ISL (2.33x) and 372.1 µs to 36.6 µs at 1M ISL (10.17x) on the reported batch-1 6-draft-token setup[^glm52-opt].

## Parallelism and deployment

- **Context parallelism for long-context prefill.** Most of the hybrid path (SWA, C4/C128 compressors, indexer) cannot shard along heads, so TP ceilings on long prompts; CP round-robins tokens across attention ranks (each rank owns `1/cp_size` of the sequence), reindexes all per-token metadata locally (SWA page indices/lengths, C4/C128 positions, page tables, indexer top-k lengths), while compressor output-write locations stay global so KV lands contiguously; this prefill NSA path is what makes long-context TTFT scale[^dsv4-infer].
- **FlashMLA head padding under high TP.** FlashMLA needs `num_heads` as a multiple of 128 on Blackwell (64 on Hopper); per-call tensor-level padding allocates a full-width Q buffer, copies the rank's heads, pads, invokes, and trims — negligible overhead since MLA decode is memory-bandwidth-bound on KV reads[^dsv4-infer].
- **Paged KV transfer for PD disaggregation.** The PD transfer protocol gains page-indexed KV transport: pages move by index through the standard path and are reinterpreted via the receiver's own shadow mappings, keeping transport oblivious to the non-uniform on-device layout[^dsv4-infer].
- **Expert parallelism on DeepEP + Mega MoE.** MoE runs atop DeepEP all-to-all routing with the Mega MoE path above it; Mega MoE weights are an aliased view of DeepEP expert tensors (different layout expected) so large deployments avoid two GPU copies, paired with SwiGLU-clamp and JIT activation fusions on the EP side[^dsv4-infer].
- Hardware coverage is Hopper, Blackwell, Grace Blackwell, AMD, and NPU[^dsv4-infer].

## Hierarchical multi-stream overlap

Attention preparation is a crowd of small kernels (Q/KV projections, compressor, indexer) that underfill the GPU at small batch, letting serial launch overhead dominate decode[^dsv4-infer]. Work fans across CUDA streams on two levels: the top level runs four preparation ops in parallel, and inside the heaviest (indexer) Q projection, weights projection, and compressor GEMM overlap too, with `q_lora_ready` / `q_scale_ready` events handing off as soon as dependencies finish[^dsv4-infer]. This runs inside the CUDA graph and kicks in only at small batch — large prefills already saturate the device[^dsv4-infer].

## Day-0 benchmarks and caveats

Day-0 snapshot (not a definitive ranking), single-batch decode with OSL 4096 on a 30K-token prefix from *Dream of the Red Chamber*, throughput as `1000 / TPOT (ms)`; launch commands are in the SGLang cookbook[^dsv4-infer].

Decode throughput inspected from the source chart (30K context, single batch, with spec)[^dsv4-infer]:

| Setup | SGLang (tok/s) | Other OSS engine (tok/s) |
| --- | --- | --- |
| V4 Pro on B200, TP=8 | 158 | 65 |
| V4 Flash on H200, TP=4 | 215 | 147 |

Spec configs are best-effort per each engine's official recipe: SGLang EAGLE 3/1/4 with accept length ~2.5 on Pro and Flash; other engine MTP-3 on B200 Pro (accept ~1.19, heavily skewed to position 0: 2226/354/55 tokens at positions 0/1/2, suggesting the MTP path is mostly accepting only position 0) and MTP-1 fallback on H200 Flash (accept ~1.92) after `num_speculative_tokens >= 2` hit a `paged_mqa_logits_metadata` assertion at startup[^dsv4-infer]. Long-context head-to-head is pinned at 30K because stable long-context runs on the other engine (200K+ inputs) did not return within timeout — a handling configuration may exist but was not found in time[^dsv4-infer].

## Relationships

- Related to [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) — DeepSeek-V4 FULL plus SWA composition with C4/C128 sidecars is the Unified view of the ShadowRadix layout here.
- Uses [SGLang HiSparse Hierarchical Sparse-Attention Memory](sglang-hisparse.md) — CPU-extended C4 KV pool with coordinator swap-in/LRU described here is the DeepSeek-V4 application of that hierarchy.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — DeepSeek-V4 single-layer MTP head and in-graph hybrid metadata preparation extend the EAGLE/MTP speculation surface there.
- Depends on [SGLang Attention Backends](sglang-attention-backends.md) — hybrid SWA+C4/C128 execution context for the FlashMLA fused path, CP prefill sharding, and head-padding rules.
- Uses [SGLang Quantization](sglang-quantization.md) — MXFP8-activation × MXFP4-expert and FP8×FP4 Mega MoE weight layouts for native FP4 experts.
- Depends on [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — page-indexed KV transport reinterpreted through receiver shadow mappings.
- Depends on [SGLang Expert Parallelism](sglang-expert-parallelism.md) — DeepEP routing plus aliased Mega MoE execution for DSv4 MoE.
- Depends on [SGLang Pipeline Parallelism](sglang-pipeline-parallelism.md) — long-context serving context in which CP prefill and PP staging choices interact.
- Related to [Miles DeepSeek-V4 Verified RL](miles-deepseek-v4-rl.md) — training-side Day-0 companion covering Megatron modeling, FP8/QAT/R3 stability, and DAPO verification.
- Related to [SGLang GLM-5.2 NVFP4 Optimization](sglang-glm52-optimization.md) — TopK-V2 evolution of Lightning TopK plus IndexShare MTP and DSA kernel fusions for GLM-5.2.
- Related to [SGLang DeepSeek-V4.1 Inference](sglang-deepseek-v41-inference.md) — V4.1 successor with lower compression ratios, four-source KV sharing, Engram tables, and SWA bounded replay.

## Coverage limits

- Three source figures were inspected as rendered images (per-layer hybrid attention scope, ShadowRadix storage layout, SGLang-vs-other-OSS decode throughput); remaining figures (HiSparse arch/peak, Day-0 RL pipeline, kernel opts, multi-stream overlap, Miles reward/eval curves, long-context throughput) were taken from prose and captions without pixel-level chart-label verification[^dsv4-infer].
- SGLang cookbook launch commands, GB200 kernel-integration background blog, HiSparse blog, and the SGLang/Miles roadmap issues were not inspected[^dsv4-infer].
- Benchmark figures are Day-0 best-effort snapshots with the spec-config and long-context caveats above; they are not definitive rankings[^dsv4-infer].

[^dsv4-infer]: DeepSeek-V4 on Day 0: From Fast Inference to Verified RL with SGLang and Miles — `../raw/2026-04-25-deepseek-v4/index.md`, covering DSv4 model features, ShadowRadix design, MTP/in-graph spec decoding, HiSparse C4 offload, FlashMLA / TRTLLM-Gen MoE / mHC / Mega MoE integrations, Flash Compressor and Lightning TopK, CP/TP/PD/EP deployment, multi-stream overlap, Day-0 benchmarks with benchmark notes, Miles RL pipeline, roadmap, and acknowledgements.
[^glm52-opt]: Serving GLM5.2 NVFP4 Agentic Workload with SGLang: Reaching 500 TPS in 2 Weeks — `../raw/2026-07-13-glm52-optimization/index.md`.
