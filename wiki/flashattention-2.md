---
type: Concept
title: FlashAttention-2 Exact Attention Kernel
description: Exact IO-aware attention kernel that reaches GEMM-like GPU efficiency via deferred rescaling, sequence-parallel thread blocks, and split-Q warp partitioning.
tags: [attention, flashattention, gpu, kernels, io-aware, long-context]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T05:10:21Z }
sources:
  - id: fa2-doc
    resource: ../raw/FlashAttention-2.md
    title: FlashAttention-2
  - id: fa2-paper
    resource: ../raw/arXiv-2307.08691v1/flash2.tex
    title: 'FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning'
  - id: fa2-abstract
    resource: ../raw/arXiv-2307.08691v1/src/abstract.tex
    title: FlashAttention-2 abstract
  - id: fa2-intro
    resource: ../raw/arXiv-2307.08691v1/src/intro.tex
    title: FlashAttention-2 introduction
  - id: fa2-bg
    resource: ../raw/arXiv-2307.08691v1/src/background.tex
    title: FlashAttention-2 background
  - id: fa2-algo
    resource: ../raw/arXiv-2307.08691v1/src/algo.tex
    title: FlashAttention-2 algorithm, parallelism, and work partitioning
  - id: fa2-experiments
    resource: ../raw/arXiv-2307.08691v1/src/experiments.tex
    title: FlashAttention-2 empirical validation
  - id: fa2-discussion
    resource: ../raw/arXiv-2307.08691v1/src/discussion.tex
    title: FlashAttention-2 discussion and future directions
---

FlashAttention-2 is an exact GPU attention algorithm/kernel by Tri Dao (Princeton/Stanford), first published July 2023 and presented at ICLR 2024, that computes mathematically the same result as standard attention while reorganizing tiling and work partitioning to approach GEMM throughput[^fa2-doc][^fa2-paper][^fa2-abstract].

Its goal is not a new attention formula or approximate sparsity, but hardware co-design across the HBM/SRAM/register hierarchy, thread blocks, warps, and Tensor Cores[^fa2-doc][^fa2-intro].

## Standard-attention bottleneck

For `Q,K,V in R^(N×d)`, scaled dot-product attention computes `S=QK^T/sqrt(d)`, `P=softmax(S)`, `O=PV` with `O(N^2 d)` FLOPs and `O(N^2)` intermediates `S,P`[^fa2-doc].

Conventional implementations materialize `S`, write it to HBM, reread for softmax, write `P`, and reread for `P×V`; as context grows, HBM traffic dominates[^fa2-doc][^fa2-bg].

The paper grounds this in A100 characteristics: 40–80GB HBM at 1.5–2.0TB/s versus 192KB on-chip SRAM per each of 108 SMs at ~19TB/s estimated bandwidth, with programmer control focused on HBM versus SRAM because L2 is not directly controllable[^fa2-bg].

FlashAttention-1 tiles `Q,K,V` into SRAM-resident blocks and uses online softmax so full rows never materialize, cutting auxiliary memory from quadratic toward linear in sequence length while remaining exact[^fa2-doc].

## Online softmax recap

Per-row softmax `exp(x_i-m)/sum_j exp(x_j-m)` with `m=max_j x_j` is computed streaming by maintaining running maximum `m`, normalization sum `l`, and accumulated output `O`[^fa2-doc].

For a new block with maximum `m_block`, the update is `m_new=max(m_old,m_block)` and `l_new=exp(m_old-m_new)*l_old + sum_j exp(S_j-m_new)`, with `O` rescaled by the same factor before adding the block contribution[^fa2-doc].

## Why FlashAttention-2 was needed

FlashAttention-1 reduced HBM traffic but reportedly reached only about 25–40% of A100 theoretical FLOPs; the remaining bottleneck was partitioning across SMs, thread blocks, warps, and Tensor Core versus CUDA Core use[^fa2-doc][^fa2-abstract][^fa2-intro].

Forward pass reached roughly 30–50% of peak and backward only 25–35% on A100, against 80–90% for optimized GEMM[^fa2-intro].

FlashAttention-2 is reported at roughly 2× FlashAttention-1 and about 50–73% of A100 peak in tested configurations[^fa2-doc].

## Three main improvements

### Reduce non-matmul work

Modern GPUs run matmuls on high-throughput Tensor Cores, while scalar multiply/add, exp, max, and divide run on lower-throughput CUDA Cores[^fa2-doc].

FlashAttention-1 renormalized the accumulated output after each `K,V` block. FlashAttention-2 defers division, keeps an unnormalized accumulator across blocks, and divides once by `l` at the end, reducing rescales and divisions in the hot loop[^fa2-doc][^fa2-algo].

The paper motivates this by A100 asymmetry: 312 TFLOPs/s FP16/BF16 matmul versus 19.5 TFLOPs/s non-matmul FP32, so each non-matmul FLOP is ~16× more expensive; sustaining >50% peak requires maximizing matmul share[^fa2-algo].

Backward is tweaked the same way to keep only row-wise logsumexp `L=m+log(l)` instead of both max `m` and sum `l`[^fa2-algo].

For causal attention it also skips fully masked blocks at block granularity, pushing work share toward matmuls[^fa2-doc][^fa2-algo].

Paper detail: for large sequences roughly half the blocks have all column indices beyond row indices and are skipped, giving ~1.7–1.8× speedup over non-causal; blocks fully under the mask need no mask application, so with square blocks only one block per row needs masking[^fa2-algo].

### Sequence-dimension parallelism

FlashAttention-1 commonly parallelized over `B×H` (one thread block per head per batch element), leaving SMs idle for small batch, few heads, and very long sequences (for example `B=1,H=16` gives only 16 large work units)[^fa2-doc].

FlashAttention-2 additionally splits the `Q` sequence dimension so each thread block owns one row-block `Q_i`; parallelism becomes approximately `B×H×ceil(N/B_r)` (for example `1×16×8192/128=1024` blocks), raising occupancy for long-context, small-batch training[^fa2-doc].

The paper describes this as parallelizing a single head across multiple thread blocks[^fa2-doc][^fa2-algo].

The paper credits swapping to outer-loop-over-row-blocks plus sequence-length parallelism to Phil Tillet's Triton fused-attention implementation[^fa2-algo].

Backward parallelizes over sequence length as well by scheduling one thread block per column block; the only cross-block sharing is the `dQ` update, handled with atomic adds after load-update-writeback[^fa2-algo].

### Split-Q instead of split-K warp partitioning

In FlashAttention-1-style split-K, warps in a block share `Q_i` but split `K_j,V_j`, then need shared-memory writes, warp synchronization, rereads, and reduction[^fa2-doc].

FlashAttention-2 uses split-Q: warps share `K_j,V_j` but own disjoint `Q` rows, producing independent outputs without inter-warp reduction[^fa2-doc].

Reported benefits are less shared-memory traffic, less synchronization, longer register residence per warp, and a shorter Tensor Core-to-output path[^fa2-doc][^fa2-algo].

Backward avoids split-K for the same reason, though some synchronization remains because `Q,K,V,O,dO,dQ,dK,dV` have more complex dependencies[^fa2-algo].

Typical block sizes are `{64,128}×{64,128}` depending on head dimension and device SRAM; larger blocks cut shared-memory traffic but raise register pressure and can spill or exceed SRAM, and the paper manually tunes per head dimension rather than auto-tuning[^fa2-algo].

## Forward pass

For each `Q_i`: load `Q_i` to SRAM/registers, initialize `m_i=-inf,l_i=0,O_i=0`, loop over `K_j,V_j` computing `S_ij=Q_i K_j^T`, applying scale and causal mask, updating row max, forming `P_ij=exp(S_ij-m_new)`, rescaling old `l_i,O_i` by `alpha=exp(m_i-m_new)`, accumulating `rowsum(P_ij)` and `P_ij V_j`, then normalizing once `O_i/=l_i` and writing back to HBM[^fa2-doc].

Full `P=softmax(QK^T)` is never stored in HBM[^fa2-doc].

## Backward pass

Gradients are `dV=P^T dO`, `dP=dO V^T`, `dS=P⊙(dP-rowsum(dP⊙P))`, `dQ=dS K`, `dK=dS^T Q`[^fa2-doc].

Instead of storing `O(N^2)` `P`, the method stores small softmax statistics and recomputes `S,P` blocks in backward — extra FLOPs in exchange for much less HBM traffic and activation memory, a favorable trade on GPUs[^fa2-doc].

FlashAttention-2 also repartitions backward work to reduce atomics and communication when multiple blocks contribute to `dQ,dK,dV`[^fa2-doc][^fa2-algo].

### MQA and GQA support

Multi-query attention (MQA) and grouped-query attention (GQA) let multiple query heads share one KV head to shrink KV-cache during inference[^fa2-algo].

FlashAttention-2 supports them without duplicating KV heads by implicitly manipulating head indices in the computation; backward sums `dK` and `dV` across the implicitly duplicated heads[^fa2-algo].

## Complexity

Compute remains `O(N^2 d)`; FlashAttention-2 is not linear or sub-quadratic[^fa2-doc].

Auxiliary attention memory falls to near `O(N)` — output plus log-sum-exp/softmax statistics plus small SRAM/register tiles — because the quadratic matrix is not materialized[^fa2-doc].

## Reported results

Kernel studies covered forward/backward, causal/non-causal, sequences up to about 16K, head dimensions 64 and 128, against PyTorch attention, xFormers/CUTLASS, and FlashAttention-1; end-to-end tests used 1.3B and 2.7B GPT-style models at several context lengths[^fa2-doc].

Headline numbers from the paper are about 2× FlashAttention-1, 50–73% of A100 theoretical peak, up to about 225 TFLOPs/s per A100 in end-to-end GPT-style training, or about 72% model FLOPs utilization in the best reported configuration[^fa2-doc][^fa2-abstract][^fa2-experiments].

Benchmark method on A100 80GB SXM4 varied sequence length 512 through 16K with batch sized for 16K total tokens, hidden dimension 2048, and head dimension 64 (32 heads) or 128 (16 heads)[^fa2-experiments]. Forward FLOPs were counted as `4·seqlen²·head-dim·num-heads`, halved with causal mask; backward FLOPs were 2.5× forward to reflect 2 forward versus 5 backward matmuls with recomputation[^fa2-experiments].

Finer paper claims: ~1.7–3.0× over FlashAttention-1, ~1.3–2.5× over Triton FlashAttention-1, 3–10× over standard PyTorch attention, up to 230 TFLOPs/s (73% peak) forward and up to 63% peak backward; forward ~1.3–1.5× over Triton and backward ~2× over Triton[^fa2-experiments].

On H100 with no new TMA / fourth-gen Tensor Core / FP8 instructions, the same implementation reached up to 335 TFLOPs/s; the paper expected another 1.5–2× from H100-specific instructions as future work[^fa2-experiments][^fa2-discussion].

End-to-end on 8×A100 80GB SXM, GPT-style training reached up to 225 TFLOPs/s per GPU: GPT3-1.3B 2K 142/189/196, 8K 72/170/220; GPT3-2.7B 2K 149/189/205, 8K 80/175/225 TFLOPs/s for baseline without FlashAttention / FlashAttention-1 / FlashAttention-2, or up to ~1.3× over FlashAttention-1 and ~2.8× over baseline[^fa2-experiments]. MFU used the Megatron-LM formula `6·seqlen·params + 12·layers·hidden·seqlen²`, kept unhalved for causal attention for literature consistency even though causal halves attention entries[^fa2-experiments].

## LLM implications

Long-context training benefits because doubling `N` quadruples attention elements; avoiding materialization makes longer sequences feasible[^fa2-doc].

Saved activation memory can go to larger batch, longer sequence, larger model, or less activation checkpointing[^fa2-doc].

Faster attention raises tokens/s and lowers step time, but end-to-end gains are smaller than kernel-only gains because MLP, projections, norms, inter-GPU communication, optimizer, and data loading remain[^fa2-doc].

Inference benefits concentrate in long-prompt prefill and batched multi-query processing; single-token autoregressive decode with KV-cache reads is memory-bandwidth-bound in a different way that FlashAttention-2 alone does not solve[^fa2-doc].

## Non-goals

FlashAttention-2 still computes `softmax(QK^T/sqrt(d))V` exactly, subject only to floating-point ordering differences; it is not approximation or token-dropping[^fa2-doc][^fa2-algo].

It does not reduce compute from `O(N^2)` to `O(N)`; it mainly cuts IO and improves hardware efficiency[^fa2-doc].

It is not MQA/GQA (which reorganize KV heads) nor paged attention (which manages KV-cache for serving); it can compose with MQA/GQA via implicit head-index handling and addresses a different layer than paged KV management[^fa2-doc][^fa2-algo].

## Future directions

The paper frames 2× over FlashAttention-1 as training 16K context for the price of prior 8K-context training, enabling long books/reports, high-resolution images, audio, video, plus faster training, finetuning, and inference of existing models[^fa2-discussion].

Planned work was H100 optimization with TMA and fourth-gen Tensor Cores plus FP8, wider device coverage including AMD GPUs, combining low-level FA2 optimizations with local/dilated/block-sparse attention for much longer context, and compiler collaboration for programmability[^fa2-discussion].

## Comparison

| Property | Standard attention | FlashAttention-1 | FlashAttention-2 |
|---|---|---|---|
| Exact | Yes | Yes | Yes |
| Compute | `O(N^2 d)` | `O(N^2 d)` | `O(N^2 d)` |
| Materialize `N×N` | Usually yes | No | No |
| IO-aware tiling | No | Yes | Yes |
| Online softmax | Not required | Yes | Yes, leaner rescaling |
| Sequence parallelism | Kernel-dependent, limited | More limited | `B×H×ceil(N/B_r)` |
| Warp split | Generic | Split-K-like | Split-Q-like |
| Shared-memory/sync | Higher | Reduced | Further reduced |
| Reported A100 efficiency | Lower | 25–40% peak | 50–73% peak |

Table values are paper-reported numbers on specific configurations, not guarantees across models or GPUs[^fa2-doc].

## Relationships

- Extends [FlashAttention Exact IO-Aware Attention](flashattention.md) — synthesis: FA1 establishes tiling, kernel fusion, and online softmax; FA2 keeps that foundation while deferring rescaling and changing sequence and warp partitioning.
- Extended by [FlashAttention-3 Asynchronous Low-Precision Attention](flashattention-3.md) — synthesis: FA3 starts from FA2 and closes the reported Hopper utilization gap with warp specialization, GEMM-softmax overlap, and FP8.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — synthesis: serving stacks select FlashAttention versions through backend registries; use that matrix to map FA2-era kernels to current FA3/FA4 defaults and constraints.
- Uses [SGLang Attention Backends](sglang-attention-backends.md) — synthesis: SGLang automatic and hybrid prefill/decode selection determines where FA-family kernels run.
- Contrasts with [FlexAttention Programmable Attention Kernels](flex-attention.md) — synthesis: FlexAttention keeps fused-attention optimizations but adds compiler-generated `score_mod`/`mask_mod` variants, while FA2 is a fixed exact kernel tuned for throughput.
- Contrasts with [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — FA2 optimizes dense attention compute; paged attention manages KV-cache layout for serving[^fa2-doc].
- Contrasts with [LongCat Sparse Attention](longcat-sparse-attention.md) — synthesis: FA2 stays exact quadratic compute with near-linear auxiliary memory, while sparse/indexed methods change the attention pattern itself.

## Coverage limits

- Prior Vietnamese synthesis file read in full plus original `arXiv-2307.08691v1` LaTeX source (`flash2.tex` and `src/abstract.tex`, `intro.tex`, `background.tex`, `algo.tex`, `experiments.tex`, `discussion.tex`) read in full; figure PDFs under `figs/` were not independently measured, only their captions/method text.
- Paper numbers above follow direct paper text and formulas, not independent measurement; H100 figures are same-implementation port without TMA/fourth-gen Tensor Core use.
- No secrets, credentials, or PII were found in the source.

[^fa2-doc]: FlashAttention-2 — `../raw/FlashAttention-2.md`.
[^fa2-paper]: Tri Dao, FlashAttention-2 — `../raw/arXiv-2307.08691v1/flash2.tex`.
[^fa2-abstract]: FlashAttention-2 abstract — `../raw/arXiv-2307.08691v1/src/abstract.tex`.
[^fa2-intro]: FlashAttention-2 introduction — `../raw/arXiv-2307.08691v1/src/intro.tex`.
[^fa2-bg]: FlashAttention-2 background — `../raw/arXiv-2307.08691v1/src/background.tex`.
[^fa2-algo]: FlashAttention-2 algorithm and parallelism — `../raw/arXiv-2307.08691v1/src/algo.tex`.
[^fa2-experiments]: FlashAttention-2 empirical validation — `../raw/arXiv-2307.08691v1/src/experiments.tex`.
[^fa2-discussion]: FlashAttention-2 discussion — `../raw/arXiv-2307.08691v1/src/discussion.tex`.
