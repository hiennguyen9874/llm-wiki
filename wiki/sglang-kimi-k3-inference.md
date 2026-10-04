---
type: Concept
title: SGLang Kimi K3 Day-0 Inference
description: Day-0 SGLang serving for Kimi K3's hybrid KDA-MLA MoE with KDA checkpoint prefix caching, a two-ended unified memory pool, chunked PP8 prefill, DCP decode, and GB300 BS=1 and PD-disaggregated benchmarks.
tags: [sglang, kimi-k3, hybrid-attention, kimi-delta-attention, mla, prefix-caching, memory-pool, pipeline-parallelism, decode-context-parallelism, pd-disaggregation, gb300, benchmark, serving]
status: stable
created: 2026-10-04
generated: { by: llm-wiki-agent/1, at: 2026-10-04T10:30:00Z }
stale_after: 2027-04-04
sources:
  - id: sglang-k3-day0
    resource: ../raw/kimi-k3-day0-support/index.md
    kind: article
    title: 'Kimi K3: Architecture and SGLang Day-0 Support'
---

SGLang supported Kimi K3 on release day. Its serving stack is built around one fact: K3 keeps two kinds of inference state with very different lifecycles. The 24 MLA layers append about 27KB of KV per token per GPU. The 69 KDA layers each hold a fixed-size recurrent state, about 54MB per request per GPU at TP8, overwritten in place every step[^sglang-k3-day0]. SGLang's day-0 work handles that split in three places:

- **Memory:** KDA prefix caching through read-only checkpoints with copy-on-write, and one opt-in memory pool that holds both state types.
- **Prefill:** chunked pipeline parallelism (PP8).
- **Decode:** decode context parallelism (DCP) on top of TP8.

On 8×GB300, 15 optimizations took non-speculative BS=1 decode from 44.3 to 112.5 tok/s, and DSpark reaches about 423 tok/s[^sglang-k3-day0]. All performance figures are **Reported** by the SGLang team. The source names no SGLang version or commit.

## Serving-relevant architecture

- **Scale.** 2.8T total and 104B active parameters per token (≈3.7%), with a native 1M-token context[^sglang-k3-day0].
- **Layer layout.** 93 layers: 69 KDA linear-attention and 24 gated global MLA, arranged as 23 × (3 KDA + 1 MLA) plus one final MLA layer. No layer uses RoPE[^sglang-k3-day0]. The KDA mechanism is covered in [Kimi Delta Attention (KDA)](kimi-delta-attention.md).
- **MoE.** The first layer is a dense FFN, and the other 92 use Stable LatentMoE. Each token picks 16 of 896 routed experts (1.8% of the routed pool), and 2 shared experts are always active. Routing scores the full 7168-d hidden state, but the selected experts compute in a 3584-d latent space. That halves both the 16-way all-to-all dispatch traffic and the expert weight volume[^sglang-k3-day0].
- **Attention Residual.** Layers are grouped into 8 blocks (seven of 12 layers, one of 9). That gives 9 sources per token (8 block summaries plus the embedding), or `9 × 7168` values per token. These summaries travel with the activations through a pipeline, so the block count feeds directly into PP communication volume[^sglang-k3-day0].
- **Precision.** Quantization-aware training starts at SFT. MoE expert weights are MXFP4 and their input activations MXFP8. Attention, the LatentMoE projections, shared experts, and routers stay at higher precision[^sglang-k3-day0].
- **Vision.** The native vision tower is MoonViT-V2, which feeds the shared embedding space through a lightweight projector[^sglang-k3-day0].

The canonical architecture description is in [Kimi K3 Architecture and Pre-training](kimi-k3-architecture-pretraining.md).

## Two state types and their memory

|  | MLA (24 layers) | KDA (69 layers) |
| --- | --- | --- |
| State | KV cache, appended per token | Recurrent state, fixed size |
| Size | ~27KB per token per GPU, append-only | ~54MB per request per GPU (TP=8), overwritten in place each step |
| Grows with | Total cached tokens | Number of active requests or branches |

Sizes as reported in the source[^sglang-k3-day0].

- **Why most layers can't be MLA.** 27KB across 24 layers is about 1.125KB per layer per token. If all 93 layers were MLA, one 1M-token request would need about 105GB on one GPU. Uncompressed MHA at the same shape would store 48KB per layer per token (96 heads × 128 dims × K/V × bf16), more than 40× the MLA latent[^sglang-k3-day0]. The arithmetic checks out (**Reproduced** by recomputation): 1.125KB × 93 × 1M ≈ 104.6GB, and 96 × 128 × 2 × 2 bytes = 48KB ≈ 42.7×.
- **Where the 54MB comes from (Synthesis).** The figure fits FP32 128×128 states for 12 heads per rank (96 heads / TP8) across 69 layers, about 54.3MB. The source does not give the state dtype, and convolution state is not counted.
- **Crossover point (Synthesis).** 54MB ÷ 27KB ≈ 2,000 tokens. Below about 2K tokens of context, a request's KDA state takes more memory than its MLA KV. Above that, MLA dominates, reaching about 27GB per GPU at 1M tokens. That is why fixed-split pools mis-size when the mix of short and long requests shifts.

## KDA prefix caching in RadixAttention

RadixAttention can share an attention-KV prefix because KV only grows and never rewrites history. A KDA state is different: every token overwrites it. If two requests sharing prefix `ABC` both used one `S(ABC)`, the first one's next step would turn it into `S(ABCD)`, and the other request could no longer start from `ABC`[^sglang-k3-day0].

- **Read-only checkpoints.** A KDA state stored in the radix tree is a read-only checkpoint. On a prefix hit, copy-on-write restores it into the request's private working slot, and the forward pass mutates only that copy[^sglang-k3-day0].
- **Lifecycle.** The source's walkthrough names the steps as copy-on-write, snapshot, donate, and checkpoint eviction. The snapshot and donate steps repeat at later checkpoint boundaries as generation continues. Beyond the step names and diagram, the source gives no further detail[^sglang-k3-day0].
- **What grows the cache.** KDA needs about 54MB per active request regardless of token count, and every active branch needs its own mutable working state. MLA KV depends on the total number of cached tokens, and branch topology adds none[^sglang-k3-day0].

In the [SGLang Unified Radix Cache](sglang-unified-radix-cache.md), this is the `FULL` + `MAMBA` composition for Kimi-K3.

## Unified memory pool (`--enable-unified-memory`)

**Problem.** The old approach preallocates a fixed KDA region and a fixed MLA region at startup. KDA demand follows concurrency while MLA demand follows total context length. When the workload drifts from the startup estimate, one region fills while the other sits idle, and free KDA slots cannot be lent to MLA[^sglang-k3-day0].

**Design.** SGLang puts both state types in one pool[^sglang-k3-day0]:

- Fixed-size KDA blocks are allocated from the left end and MLA pages from the right, with the free space between them shared.
- When a request finishes, aborts, or is retracted, it can leave a hole. SGLang moves a block from the end into the hole, so the free region stays contiguous and both ends stay packed.
- This lets 54MB KDA blocks and 27KB MLA pages draw from the same bytes without forcing a common page size.

**Availability.** At day 0 the pool is opt-in with `--enable-unified-memory`[^sglang-k3-day0].

**Comparison with Moonshot's design (Synthesis).** The K3 tech report's production serving design, in [Kimi K3 Systems and Infrastructure](kimi-k3-systems-infrastructure.md), takes a different route. It packs KDA states and MLA KV into one paged pool with uniform byte-size pages. SGLang's pool keeps each type's native unit size and handles fragmentation by compacting from the two ends.

## Chunked pipeline-parallel prefill (PP8)

**Why TP8 is slow for prefill.** TP8 splits every layer eight ways, so every one of the 93 layers needs a lockstep AllReduce before any rank can continue. That keeps communication on the critical path and narrows the GEMMs[^sglang-k3-day0].

**How chunked PP8 works.** Each GPU runs a contiguous range of whole layers. The prompt is split into chunks. After a GPU finishes a chunk, it sends that chunk's activations point-to-point to the next stage, and the transfer overlaps with compute on the next chunk. No AllReduce is needed between layers[^sglang-k3-day0].

| Stage | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Layers | 1–12 | 13–24 | 25–36 | 37–48 | 49–60 | 61–72 | 73–84 | 85–93 |

Stage-to-layer assignment as shown in the source[^sglang-k3-day0].

**Measured 8K prefill** on 2×4 GB300, with topology the only variable (**Reported**)[^sglang-k3-day0]:

| Metric | TEP8 baseline | PP8×TP1 |
| --- | --- | --- |
| Prefill capacity per node | 1.00× | 1.45–1.72× (representative point 1.64×) |
| Exposed critical-path communication per 1K tokens | 9.38 ms (labelled TP8) | 0.88 ms (about 91% lower) |

**Limits.**

- The measured baseline is labelled TEP8, while the explanatory diagram contrasts against plain TP8[^sglang-k3-day0].
- Filling and draining the pipeline costs some steps. Over a long-context prefill that overhead is diluted, but PP does not win when there are too few requests or chunks[^sglang-k3-day0].
- Decode usually has only one new token per step, which is not enough work to fill an 8-deep pipeline, so TP8 remains the better fit for decode. A common PD-disaggregated split is `PP8 prefill → TP8 / DCP8 decode`[^sglang-k3-day0].

## Decode context parallelism (DCP)

**Why TP replicates MLA KV.** MLA's heads all share one compressed KV latent, so there is no head axis for TP to shard. Every TP8 rank stores the full latent, and adding GPUs does not add logical context capacity[^sglang-k3-day0].

**How DCP works.** DCP shards by token position instead[^sglang-k3-day0]:

1. Each GPU projects the full, small `q` locally, with no broadcast needed.
2. KV is striped round-robin by token position, so each position is stored once.
3. Each GPU computes partial attention over its local 1/N of the KV.
4. One packed all-to-all exchanges the partial outputs.
5. A log-sum-exp-weighted merge gives exactly the full softmax result.

**Cost and placement.** DCP costs one all-to-all per MLA layer. DCP groups are built inside the TP group, so TP8 with DCP8 still uses 8 GPUs. The KDA state has no token-position axis and stays sharded by TP/head[^sglang-k3-day0].

**Effect on K3 (Reported).** Logical capacity goes from about 1.5M to 12.2M tokens (about 7.9×), and the system reaches 541 tok/s at 48 agent sessions[^sglang-k3-day0]. The rounded endpoints give 8.1×, so the stated 7.9× implies an unrounded baseline near 1.54M tokens (**Synthesis**).

**What DCP is for.** It mainly raises capacity and concurrency, not single-request latency for short prompts. Keeping more long sessions on the GPU avoids host offload, re-prefill, and throughput collapse[^sglang-k3-day0]. For vLLM's implementation and sizing rules, see [vLLM Decode Context Parallelism](vllm-decode-context-parallelism.md).

## Benchmark results

The source treats BS=1 decode, aggregate system throughput, and per-user speed as three distinct metrics[^sglang-k3-day0].

### BS=1 decode optimization

Setup: 8×GB300, TP8, BF16 KV cache, non-speculative. Steps P0–P15 add 15 kernel and communication optimizations (**Reported**)[^sglang-k3-day0]:

| Category | Steps | tok/s after category |
| --- | --- | --- |
| Baseline | P0 | 44.3 |
| Launch and copy elimination | P1–P4 | 64.2 |
| NVIDIA compute kernels | P5–P8 | 74.5 |
| Communication fusion | P9, P12, P13 | 102.1 |
| Overlap and prologue fusion | P10, P11, P14, P15 | 112.5 |
| DSpark speculative decoding (draft model) | — | ~423 |

The categories group steps that were applied interleaved. The chart plots them in P0→P15 order. Reading its point coordinates gives the following values in tok/s (**Observed** from the SVG; rounded to 0.1)[^sglang-k3-day0]:

| P0 | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | P11 | P12 | P13 | P14 | P15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44.3 | 53.2 | 61.9 | 62.4 | 64.2 | 65.3 | 71.0 | 72.0 | 74.5 | 84.3 | 85.2 | 90.2 | 92.0 | 108.0 | 111.4 | 112.5 |

Summing the per-step gains by category reproduces the category totals: communication fusion +27.6 → 102.1, and overlap +10.4 → 112.5 (**Reproduced** by recomputation). The source does not name or describe the individual P-steps.

### PD-disaggregated deployment trade-offs

Setup: GB300, 8K input / 1K output, PD disaggregation (**Reported**)[^sglang-k3-day0]:

| Goal | Layout | tok/s/GPU | tok/s/user |
| --- | --- | --- | --- |
| Total throughput | PP8 prefill → TP8 decode, FP4 | 2,808 | 18.7 |
| Long context | 2×PP8 prefill → 2×DCP8 decode | 2,633 | not given |
| Per-user speed | Add independent TP8 decode instances | not given | 116+ |

Aggregate throughput trades against per-user speed, and each deployment goal maps to a different parallel layout[^sglang-k3-day0].

## Interpretation

These points are **Synthesis** drawn from the cited measurements:

- **Communication is the biggest BS=1 lever.** Communication fusion contributes 27.6 of the 68.2 tok/s non-speculative gain (about 40%). P13 alone adds about 16 tok/s, the largest single step. Kernel work (P5–P8) adds about 10 tok/s. This matches other SGLang BS=1 journeys such as [SGLang DeepSeek-V4.1-Flash Kernel Optimization](sglang-deepseek-v41-flash-kernel-optimization.md), where removing launches and cross-rank waits matters more than raw FLOPs.
- **Not like-for-like.** 44.3 → 112.5 is a 2.54× gain under fixed conditions. The DSpark ~423 tok/s figure (about 3.8× over 112.5) comes with no stated workload, acceptance length, or block size, so treat it as an upper-range data point. The published draft checkpoint, with block size 7 and reported acceptance lengths, is in [Kimi K3 DSpark Speculator](kimi-k3-dspark.md).
- **Split layouts by phase.** Prefill favors PP, which removes per-layer AllReduce. Decode favors TP, with DCP added when MLA KV capacity is the constraint. The Qwen3.8 day-0 stack uses the same phase-split pattern, pairing PP prefill with wide-EP decode ([SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md)).
- **Pick the layout by goal.**
  - Throughput: PP8 → TP8 at FP4.
  - Long agent sessions: DCP8 decode, giving up about 6% tok/s/GPU versus the throughput layout.
  - Interactive per-user speed: more independent TP8 decode replicas, at lower GPU efficiency.

## Ecosystem

Day-0 support was a collaboration between the SGLang & Miles team at RadixArk and Moonshot AI, with NVIDIA, AMD, Approaching AI, Baseten, and Modal. DigitalOcean provided AMD instances for testing. Google Cloud, DigitalOcean, Nebius, fal, RunPod, DeepInfra, and GMI Cloud are named as serving Kimi K3 on SGLang (**Reported**)[^sglang-k3-day0].

## Relationships

- Uses [Kimi Delta Attention (KDA)](kimi-delta-attention.md): the fixed-size, in-place-overwritten recurrent state that drives the checkpoint caching, pool design, and head-only sharding here.
- Depends on [Kimi K3 Architecture and Pre-training](kimi-k3-architecture-pretraining.md): the 69 KDA + 24 MLA layout, Block AttnRes, Stable LatentMoE, and NoPE design being served.
- Related to [Kimi K3 Systems and Infrastructure](kimi-k3-systems-infrastructure.md): Moonshot's own hybrid-cache serving, which uses uniform byte-size paged blocks with decoupled hash granularity, compared with SGLang's two-ended unified pool and radix checkpoints.
- Uses [SGLang Unified Radix Cache](sglang-unified-radix-cache.md): the `FULL` + `MAMBA` composition with copy-on-write KDA checkpoints.
- Uses [SGLang Pipeline Parallelism](sglang-pipeline-parallelism.md): the chunked PP prefill mechanism, measured here as PP8×TP1 versus TEP8 on 8K prompts.
- Related to [vLLM Decode Context Parallelism](vllm-decode-context-parallelism.md): the vLLM counterpart for MLA KV striping and LSE merging, which listed Kimi K3 DCP benchmarks as pending.
- Uses [SGLang PD Disaggregation](sglang-pd-disaggregation.md): the PP8-prefill → TP8/DCP8-decode deployments.
- Uses [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md): the ~423 tok/s speculative line.
- Related to [Kimi K3 DSpark Speculator](kimi-k3-dspark.md): the draft checkpoint and TP8 + DCP8 1M-context launch recipe for the same model.
- Related to [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md): the sibling day-0 stack for a 3:1 linear/full-attention hybrid (GDN + GQA) with checkpointed recurrent state and phase-split PP prefill.
- Related to [Kimi K3 Local Deployment](kimi-k3.md): the same model run locally via GGUF instead of datacenter SGLang serving.

## Coverage limits

- **What was inspected.** The only local artifact is the entry-point capture. Inline SVGs were inspected as text, including architecture `<title>` elements, the KDA module drawing, and the BS=1 chart coordinates.
- **Interactive and illustrative content.** The widgets (KV comparison slider, radix copy-on-write walkthrough, memory-pool simulation, DCP GPU-count selector, deployment-goal toggle) were captured only in their initial state. Their toy counts (pages, cells, illustrative AttnRes `α` weights) were excluded as illustrative.
- **Missing provenance.** The source gives no publication date and no SGLang version, commit, or launch command. Flags such as `--enable-unified-memory` may change, and no commands were run. The LMSYS version of the post, linked under "Further reading", was not available locally. The Kimi Linear (arXiv 2510.26692) and Attention Residuals (arXiv 2603.15031) reports were not inspected. The K3 tech report is compiled separately.
- **ReplaySSM.** The [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md) source credits ReplaySSM to "the earlier Kimi-K3 Day-0 post", but this capture does not describe ReplaySSM or KDA speculative-state rollback. Whether the LMSYS version does is unverified.
- **Under-specified benchmarks.** Workload shape for the BS=1 chart, total GPU counts for the PD layouts, model precision for the BS=1 runs, and DSpark settings are not stated, so those numbers are **Reported** with these limits. Contributor name lists in the acknowledgments were excluded as non-durable.

[^sglang-k3-day0]: Kimi K3: Architecture and SGLang Day-0 Support (SGLang Team, sglang.io) — `../raw/kimi-k3-day0-support/index.md`. Locators: opening "Kimi K3 in SGLang" stage panel; "The Kimi K3 architecture" and architecture SVG `<title>` elements (2.8T/104B, Stable LatentMoE 16/896 + 2 shared with 3584-d latent, Gated MLA, KDA, NoPE, MoonViT-V2, MXFP4 QAT); "KV cache memory estimation" (27KB, 1.125KB/layer, 105GB, 48KB MHA, 54MB, 3 KDA + 1 MLA × 23 + final MLA); "Attention Residual" math/cost note (8 blocks, `9 × 7168`, pipeline traffic); "LatentMoE" (traffic and weight halving); "SGLang's day-0 adaptations" state table; "RadixAttention: prefix caching for KDA state"; "Memory management for two state types" (`--enable-unified-memory`); "Chunked pipeline prefill" (layer ranges, 2×4 GB300 8K measurement, PD split); "Decode context parallelism (DCP)" (1.5M → 12.2M, 541 tok/s at 48 sessions); "Performance numbers and benchmark results" (BS=1 chart polyline and labels, DSpark ~423, GB300 8K/1K deployment panel); "Acknowledgments"; "Further reading".
