---
type: Concept
title: SGLang Qwen3.8 Inference
description: Day-0 SGLang and Miles serving for Qwen3.8-2.4T-A95B hybrid GDN-MoE with three-state caching, chunked PP prefill, PD disaggregation, fused kernels, and colocated LoRA RL.
tags: [sglang, qwen3.8, hybrid-attention, gdn, moe, nvfp4, speculative-decoding, pd-disaggregation, pipeline-parallelism, miles, rl]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T23:30:00Z }
sources:
  - id: qwen38-day0
    resource: ../raw/2026-08-12-qwen3-8-day0-support/index.md
    title: 'SGLang and Miles Add Day-0 Support for Qwen3.8'
  - id: qwen38-flash-next-day0
    resource: ../raw/2026-08-26-qwen-flash-next/index.md
    title: 'Qwen3.8-Flash-Next: Day-0 Support in SGLang'
---

SGLang and Miles cover Qwen3.8-2.4T-A95B on launch day with a serving stack built for hybrid GDN plus GQA attention and 512-expert MoE, pairing three-state prefix caching and ReplaySSM speculative state recovery with phase-split parallelism and a colocated LoRA RL path[^qwen38-day0].

## Model identity

- `Qwen3.8-2.4T-A95B`: 2.4T total parameters, 95B active per token, 92 layers, described as Qwen's largest open-source model[^qwen38-day0].
- Hybrid attention in a 3:1 interleaved pattern: 69 GDN linear-attention layers plus 23 GQA full-attention layers, continuing the Qwen3.5/3.6 hybrid design[^qwen38-day0].
- GDN (Gated Delta Network) linear-attention layers combine SSM with CausalConv1d; fixed-size recurrent state replaces the growing KV cache, so per-layer memory is `O(1)` while compute scales as `O(N)`[^qwen38-day0].
- Sparse MoE: 512 routed experts plus one shared expert per MoE layer, top-k=10 routing, hidden dimension 8,192[^qwen38-day0].
- Day-0 checkpoints: `Qwen/Qwen3.8-2.4T-A95B` plus quantized `RadixArk/Qwen3.8-2.4T-A95B-NVFP4` and FP8; launch commands and per-workload guidance live in the Qwen3.8 cookbook linked in the source[^qwen38-day0].

## Three serving states

Each request maintains KV cache for full-attention layers, recurrent state for GDN layers, and GDN convolution windows; prefix caching, speculative decoding, and PD disaggregation must manage all three consistently[^qwen38-day0].

## ReplaySSM for GDN state

MTP verification creates a GDN state-recovery problem: each layer updates recurrent state in place while verifying multiple drafts, but only the accepted-prefix state should commit[^qwen38-day0].

- Qwen3.8 applies ReplaySSM raw-input replay: record recurrence inputs during verification instead of snapshotting full GDN state at every draft position, then a fold kernel replays the accepted prefix from the committed checkpoint and advances state in place[^qwen38-day0].
- Recording path is integrated into FlashInfer's CuTe DSL GDN MTP kernel for BF16 states; the verify prologue already holds required values in registers, so ReplaySSM only adds ring-buffer stores[^qwen38-day0].
- Source reports verification results bitwise unchanged with no measurable verify-throughput regression; the same mutable-state caching path composes with prefix caching, overlap scheduling, and PD disaggregation[^qwen38-day0].
- The mechanism is described in detail in the earlier Kimi-K3 Day-0 post linked in the source[^qwen38-day0].

## PD disaggregation with typed state and staging buffer

PD transfer moves all three state types through a typed state registry with per-type handlers for KV cache, GDN recurrent state, and GDN convolution windows[^qwen38-day0].

- The `q`, `k`, and `v` sub-blocks of each convolution window shard independently across tensor-parallel ranks, so the transfer layer slices and reassembles them for the destination layout[^qwen38-day0].
- The same payload carries MTP draft-model KV cache, hidden states, and top-k metadata, letting speculative decoding continue on the decode worker[^qwen38-day0].
- When prefill and decode use different attention-sharding layouts, a GPU staging buffer coalesces per-layer slices into one bulk RDMA transfer per chunk instead of per-slice transfers[^qwen38-day0].
- Contract is a chunk index plus per-peer watermark: prefill writes completed chunks and publishes watermarks while decode scatters into its own layout with chunk-by-chunk prefetch, overlapping transfer with remaining prefill; prefill:decode ratio, pipeline depth, and decode EP width can then be tuned separately, and the same path carries draft KV[^qwen38-day0].

## Radix cache and HiCache

Qwen3.8 uses SGLang Unified Radix Cache for both full-attention KV and GDN state: `FULL` manages full-attention KV while `MAMBA` manages GDN checkpoints, each checkpoint bundling recurrent state plus convolution windows[^qwen38-day0].

- Copy-on-write restores a shared GDN checkpoint into a private request slot before a forward pass mutates it[^qwen38-day0].
- New checkpoints are created at prefill chunk boundaries and regular decode intervals; a shared cache controller coordinates KV and GDN components across device and host tiers, composing prefix caching and HiCache with MTP and PD disaggregation[^qwen38-day0].

## Chunked pipeline-parallel prefill

Decode and prefill favor different layouts at the measured operating points: wide expert parallelism with EPLB for decode to shard all 512 experts, versus pure pipeline parallelism for 8K prefill to use full-width GEMMs without MoE dispatch, combine, or EPLB[^qwen38-day0].

- Pure PP gives each stage a contiguous slice of the 92 layers on one rank; inter-stage traffic is activation transfer at stage boundaries, and splitting requests into chunks lets hand-off for chunk `i` overlap compute for chunk `i+1` as chunks flow back to back[^qwen38-day0].
- Chunked-PP diagram inspected as SVG text: wide-EP row shows per-layer attn plus dispatch/combine all-to-all growing with 92 layers, while the PP schedule shows 4 stages with chunked diagonal flow, hand-off arrows, and drain/bubble annotations[^qwen38-day0].

Measured 8K prefill input tokens/s/GPU[^qwen38-day0]:

| Checkpoint | Chunked PP prefill | Wide EP + EPLB | Speedup |
| --- | --- | --- | --- |
| FP8, 16 GPUs | **5231** (PP16) | 3421 | **1.53x** |
| NVFP4, 8 GPUs | **8363** (PP8) | 5151 | **1.62x** |

## Pipeline-parallel prefill with MTP

Pipelined prefill and speculative decoding were previously mutually exclusive because the embedding sits on the first stage and the LM head on the last, so no single stage holds both while the draft head needs both[^qwen38-day0].

- Fix: place the draft head on the last stage with its own copy of the missing half, stage draft KV across the PD boundary alongside target KV, and let ranks hosting no draft own no draft KV pool[^qwen38-day0].
- Result: prefill topology becomes a free variable while the decode worker keeps its speculative decoding however prefill is sliced[^qwen38-day0].

## Performance: 8K/1K Pareto on GB300

All Pareto numbers are 8,192-input / 1,024-output on GB300; throughput is total input plus output tokens/s per active model-serving GPU and per-user speed is output tok/s per request; Pareto SVG inspected as text for curve shape, endpoint labels, and active/allocated counts[^qwen38-day0].

- Representative labels report active/allocated GPUs with `P`/`D` active prefill/decode split; the PP6 maximum uses 20 active GPUs (`12P + 8D`) from 24 allocated, with TPS/GPU divided by active GPUs[^qwen38-day0].
- PD points use forced accept length 3.3; FP8 aggregate points report TPOT from their respective runs[^qwen38-day0].

| Checkpoint | Max throughput (PD disagg) | Low-latency endpoint |
| --- | --- | --- |
| NVFP4 (2xPP6 prefill, DP2-attn / TP4 / EP8 decode) | **5126** tok/s/GPU @ 36 tok/s/user | PD: **108** tok/s/GPU @ **334** tok/s/user (PP2xTP4 prefill + TP16 decode) |
| FP8 (2xPP16 prefill, DP4-attn / TP4 / EP16 decode) | **3532** tok/s/GPU @ 30 tok/s/user | Aggregate CC1: **220** tok/s/GPU @ **362** tok/s/user (TP16 aggregate, concurrency 1) |

Speculative-decoding detail[^qwen38-day0]:

- At TP8 on B300, the NVFP4 checkpoint decodes at **346** tok/s batch-size-1 with MTP at accept length 3.3, and **378** tok/s with DSpark at accept length 4.0; both include the bonus token[^qwen38-day0].
- On the matched dual-PP6 NVFP4 backbone, adding MTP moves throughput +10.0% and per-user speed 2.33x; the updated 5126 point is not used for that matched comparison[^qwen38-day0].
- Source asymmetry note: in a saturated decode worker, tokens per step are roughly `running_requests x draft_tokens` fixed by the memory budget, so speculation mostly converts a fixed step budget into fewer, longer steps per request[^qwen38-day0].

## Kernel optimizations

- **Fused MoE finalize, AllReduce, and RMSNorm.** At 8K input, `8192 x 10 x 8192 x sizeof(bfloat16)` needs 1.25 GiB finalize input buffer and finalization is up to 10% of prefill; PDL-chained persistent fused compute/communication kernels improve end-to-end latency/throughput by more than 10% in tested configs; FlashInfer PR #4358[^qwen38-day0].
- **Context-parallel GDN prefill.** Partitions the sequence into chunks processed in parallel for long-sequence small-batch utilization; improves prefill 2-3%; tracked in FlashInfer issue #3491[^qwen38-day0].
- **Low-latency single-GEMM path.** Avoids separate Split-K reduction for small GEMMs; up to 1.5x kernel-level speedup and ~4% end-to-end; FlashInfer PR #4266[^qwen38-day0].
- **Fused GDN decode ops.** Fuses SplitKV reshape and Conv1D for low-latency tensor-parallel configs; improves end-to-end decode 2-3%; SGLang PR #32919[^qwen38-day0].
- Kernels built with NVIDIA and shipped through FlashInfer; collaboration also covered GQA and MoE communication plus parallel-config tuning[^qwen38-day0].

## RL: colocated LoRA on native NVFP4 with Miles

Day-0 RL is colocated LoRA training with Miles: BF16 Megatron trainer plus native NVFP4 SGLang rollout engines sharing the same 64 GB300s, rank-32 adapters on attention projections trained with GRPO[^qwen38-day0].

- Short GSM8K verification run: reward and eval score climb steadily while train/rollout KL stays flat; RL reward/eval/KL chart is a PNG taken from prose and caption without pixel re-measurement[^qwen38-day0].

## Relationships

- Uses [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — typed three-state transfer with convolution-window resharding plus watermarked staging-buffer bulk RDMA that lets PP prefill and wide-EP decode use independent layouts.
- Uses [SGLang Pipeline Parallelism](sglang-pipeline-parallelism.md) — chunked pure-PP prefill beating wide-EP at 8K plus last-stage draft-head placement that makes PP prefill composable with MTP.
- Uses [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) — `FULL` plus `MAMBA` GDN-checkpoint composition with copy-on-write and chunk-boundary checkpointing across device/host tiers.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — ReplaySSM GDN state recovery plus MTP and DSpark batch-1 rates and matched-backbone MTP throughput versus per-user-speed asymmetry.
- Uses [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — 378 tok/s DSpark path at accept length 4.0 versus 346 tok/s MTP path on the same TP8 B300 NVFP4 setup.
- Uses [SGLang for RL Systems](sglang-for-rl.md) — colocated BF16-trainer plus NVFP4-rollout LoRA GRPO discipline instantiated here on 64 GB300s.
- Related to [Miles DeepSeek-V4 Verified RL](miles-deepseek-v4-rl.md) — Miles Day-0 RL companion with shared trainer plus rollout colocation pattern, here rank-32 attention LoRA on GSM8K rather than full DeepSeek-V4 FP8/QAT/R3 verification.
- Uses [SGLang Quantization](sglang-quantization.md) — Day-0 NVFP4 plus FP8 checkpoint serving context for the 512-expert top-10 MoE.
- Depends on [SGLang Expert Parallelism](sglang-expert-parallelism.md) — wide-EP with EPLB decode layout contrasted with pure-PP prefill.
- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 2.4T-A95B identity served here at datacenter scale rather than via local GGUF/NVFP4 runs.
- Related to [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md) — Qwen4-preview Flash-Next sibling with 36-GDN/12-QSA sparse attention plus QSA IndexShare, 4-branch gated residual, and PLE host offload instead of the 69-GDN/23-GQA plus ReplaySSM stack here[^qwen38-flash-next-day0].

## Coverage limits

- Local SVG diagrams for chunked-PP schedule and 8K/1K Pareto were inspected as text; architecture PNG and GSM8K RL PNG were enumerated but not pixel-verified, so architecture detail and RL curves follow prose and captions[^qwen38-day0].
- Cookbook launch commands, FlashInfer and SGLang PR/issue diffs, Hugging Face checkpoints, and prior Kimi-K3 ReplaySSM post were referenced but not inspected beyond identifiers and claims above[^qwen38-day0].
- Throughput, accept-length, kernel-gain, and RL-stability figures are Day-0 source-reported snapshots on the stated GB300/B300 setups, not independently verified or universal defaults[^qwen38-day0].

[^qwen38-day0]: SGLang and Miles Add Day-0 Support for Qwen3.8 — `../raw/2026-08-12-qwen3-8-day0-support/index.md`, covering 2.4T-A95B 92-layer 69-GDN/23-GQA plus 512-expert top-10 architecture with NVFP4 checkpoint, three-state serving with ReplaySSM and Unified FULL/MAMBA caching, typed PD transfer with TP-resharding and watermarked staging buffer, chunked PP prefill 1.53x/1.62x table with PP+MTP draft-head fix, 8K/1K Pareto 5126/3532 endpoints with 346/378 tok/s MTP/DSpark batch-1 and +10%/2.33x matched MTP gain, four FlashInfer/SGLang kernel fusions with PR identifiers, and 64-GB300 colocated rank-32 LoRA GRPO GSM8K verification.
[^qwen38-flash-next-day0]: Qwen3.8-Flash-Next: Day-0 Support in SGLang — `../raw/2026-08-26-qwen-flash-next/index.md`, covering 125B-plus-51B 36-GDN/12-QSA Flash-Next sibling with QSA IndexShare, gated residual, and PLE offload.
