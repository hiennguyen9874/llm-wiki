---
type: Concept
title: DeepSeek-V4 Systems and Infrastructure
description: Fine-grained EP MegaMoE overlap, TileLang kernels, batch-invariant deterministic libraries, Muon ZeRO plus mHC and CP training, and heterogeneous KV-cache with on-disk storage for DeepSeek-V4.
tags: [deepseek-v4, systems, expert-parallelism, tilelang, determinism, kv-cache]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: v4-report
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: 'DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence'
---

DeepSeek-V4 pairs its hybrid attention and mHC architecture with wave-scheduled expert-parallel overlap, TileLang fused kernels, bitwise batch-invariant and deterministic libraries, Muon-aware ZeRO plus compressed-attention context parallelism, and a split state plus classical KV-cache layout with tiered on-disk reuse[^v4-report].

## Fine-grained expert-parallel overlap

Each MoE layer splits into Dispatch and Combine communication stages plus Linear-1 and Linear-2 compute stages; profiling shows communication time below compute time, so fusion lets compute hide communication[^v4-report].

Experts are scheduled in waves: as soon as one wave finishes communication its compute starts while the next wave transfers and completed experts send results, keeping both paths continuous and helping long-tail small batches in RL rollout and agent serving[^v4-report]. Reported speedups over non-fused baselines are 1.50–1.73x general inference and up to 1.96x latency-sensitive rollout/agent cases on NVIDIA and Huawei Ascend; the CUDA mega-kernel is open-sourced as MegaMoE in DeepGEMM[^v4-report].

The report frames balance as a compute-communication ratio rather than raw bandwidth: hide holds when `C/B <= V_comp/V_comm`, or for Pro token-expert pairs `C/B <= 2d = 6144 FLOPs/Byte`, so 1 GBps hides about 6.1 TFLOP/s and extra bandwidth past that has diminishing returns[^v4-report]. Further proposals cover power headroom for fused concurrent load, lower-latency cross-GPU signaling to enable push dispatch instead of pull-based remote reads, and replacing SwiGLU with exp/division-free activation to avoid post-GEMM stalls[^v4-report].

## TileLang kernel workflow

TileLang replaces hundreds of fine ATen ops with fused kernels for architecture prototyping, training, and inference[^v4-report]. Host Codegen co-generates device kernels with lightweight TVM-FFI launchers carrying dtype/rank/shape/stride metadata, moving per-invocation checks out of Python and cutting host validation from tens or hundreds of microseconds below one microsecond[^v4-report].

Z3-backed formal integer analysis in QF_NIA strengthens layout, hazard, bound, vectorization, and barrier passes with only seconds of compile overhead[^v4-report]. Fast-math stays off by default with opt-in approximate ops and explicit IEEE intrinsics plus layout annotations for bit-identical CUDA-parity validation without giving up competitive performance[^v4-report].

## Batch invariance and determinism

Batch invariance keeps per-token outputs bit-identical across batch positions[^v4-report]. Attention avoids split-KV across SMs and instead uses a dual kernel: one SM per sequence for full waves plus a multi-SM tail kernel with identical accumulation order via distributed shared memory to curb wave quantization[^v4-report]. Matmul replaces non-invariant cuBLAS end to end with DeepGEMM and avoids split-k except where re-engineered, adding optimizations to match or beat split-k[^v4-report].

Determinism targets backward accumulation order: sparse-attention backward uses per-SM buffers plus global deterministic summation instead of cross-SM atomics; MoE backward uses per-rank token-order preprocessing plus cross-rank buffer isolation; small-output mHC matmul emits split parts with a later deterministic reduction[^v4-report].

## Training framework

Built on the V3 stack with additions for Muon, mHC, and hybrid attention[^v4-report]. Muon needs full gradient matrices, conflicting with element-wise ZeRO sharding, so dense params use knapsack bucket assignment with capped ZeRO width, balanced loads, padding under 10% with at most five matrices per rank, and redundant Muon updates past the ZeRO limit; MoE experts flatten down/up/gate matrices across layers for even distribution without splitting logical matrices and negligible padding[^v4-report]. Same-shape consecutive params merge for batched Newton-Schulz; MoE gradients sync in stochastically rounded BF16 to halve volume, replacing tree/ring reduce-scatter with all-to-all plus local FP32 summation[^v4-report].

mHC costs are contained with fused train/inference kernels, selective recomputation of inter-layer states and normalized inputs without recomputing heavy ops, and an adjusted DualPipe 1F1B schedule, holding wall-time overhead to 6.7% of the overlapped stage[^v4-report]. General recomputation uses TorchFX tracing with per-tensor annotations, minimal-subgraph insertion before gradient computation, storage-pointer reuse without copies, and dedup for storage-sharing ops[^v4-report].

Compressed-attention context parallelism uses two stages: each rank sends its last `m` uncompressed entries forward, compresses local plus received entries to fixed `s/m+1` length with padding, then all-gathers compressed entries across ranks, handling variable packed-sequence lengths and cross-boundary groups[^v4-report].

## Inference KV-cache and on-disk storage

Hybrid attention breaks PagedAttention assumptions through diverse SWA versus compressed policies and kernel alignment needs[^v4-report]. The layout splits into a classical cache for CSA/HCA compressed entries with multiple blocks per request sized to multiples of `lcm(m,m')`, yielding `lcm/m` CSA and `lcm/m'` HCA tokens per block, plus a fixed per-request state cache holding the last `n_win` SWA entries and uncompressed compression tails[^v4-report]. SWA plus tails are treated as position-dependent state from a limited preallocated pool; sparse-kernel co-design with cache-line padding lets layers use variable tokens per block without degradation[^v4-report].

On-disk prefix reuse stores CSA/HCA compressed entries and recomputes only the tail incomplete block; SWA offers three trade-offs: full caching with read of the last `n_win` prefix tokens but write-heavy SSD behavior, periodic checkpointing every `p` tokens with checkpoint load plus tail recompute, and zero caching with `n_win*L`-token recompute leveraging cached CSA/HCA entries[^v4-report].

## Relationships

- Related to [DeepSeek-V4 Architecture](deepseek-v4-architecture.md) — mHC, CSA/HCA, and Muon designs realized by these systems.
- Related to [DeepSeek-V4 Training and Evaluation](deepseek-v4-training-evaluation.md) — pretraining, OPD, FP4 QAT, rollout, and DSec workloads running on this stack.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — Day-0 serving companion with ShadowRadix, in-graph spec metadata, HiSparse C4 offload, and fused kernels.
- Related to [Miles DeepSeek-V4 Verified RL](miles-deepseek-v4-rl.md) — Day-0 training companion with Megatron modeling, FP8/QAT/R3, and deterministic controls.
- Uses [PagedAttention for LLM Serving](paged-attention.md) — baseline whose uniform paging assumptions this heterogeneous layout violates.

## Coverage limits

- Figures for MoE pipeline and KV layout were taken from captions and prose without pixel-level verification; V4.1 successor numbers were not used to reinterpret V4 figures[^v4-report].
- MegaMoE pull-request code, TileLang microbenchmarks, and exact CP halo versus all-gather sizing beyond the reported scheme were not inspected[^v4-report].

[^v4-report]: DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence — `../raw/arXiv-2606.19348v1/main.tex`, covering fine-grained EP plus MegaMoE, hardware proposals, TileLang Host Codegen/Z3/precision, batch-invariant and deterministic kernels, Muon ZeRO/mHC/CP/recomputation training, and heterogeneous plus on-disk KV-cache management.
