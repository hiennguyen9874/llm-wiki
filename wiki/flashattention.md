---
type: Concept
title: FlashAttention Exact IO-Aware Attention
description: Exact tiled attention that avoids materializing N×N scores via online softmax and kernel fusion to cut HBM traffic and activation memory.
tags: [attention, flashattention, gpu, kernels, io-aware, long-context]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T05:10:21Z }
sources:
  - id: fa-doc
    resource: ../raw/FlashAttention.md
    title: FlashAttention
  - id: fa-paper
    resource: ../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex
    title: 'FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness'
  - id: fa-theory
    resource: ../raw/arXiv-2205.14135v2/src/theory.tex
    title: 'Analysis: IO Complexity of FlashAttention'
  - id: fa-algo
    resource: ../raw/arXiv-2205.14135v2/src/algo_details.tex
    title: FlashAttention Algorithm Details
  - id: fa-limit
    resource: ../raw/arXiv-2205.14135v2/src/discussion.tex
    title: FlashAttention Limitations and Future Directions
---

FlashAttention is an exact self-attention algorithm by Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra, and Christopher Ré (Stanford and Buffalo, NeurIPS 2022, arXiv 2205.14135v2) that keeps the mathematics of standard attention while reordering computation into SRAM-resident tiles with online softmax and kernel fusion, sharply reducing GPU HBM traffic and activation memory[^fa-doc][^fa-paper].

Its core message is that FLOPs complexity alone does not predict LLM attention speed; data movement through the GPU memory hierarchy must also be optimized[^fa-doc].

## Standard-attention cost

For one head with `Q,K,V in R^(N×d)`, scaled dot-product attention computes `S=QK^T/sqrt(d)`, `P=softmax(S)`, `O=PV`, where `S` and `P` are `N×N`[^fa-doc].

A naive implementation materializes the full `S`, writes it to HBM, rereads it for softmax, writes `P`, then rereads `P` and `V` for `O=PV`[^fa-doc].

At `N=32768`, one head has `N^2 ≈ 1.07B` elements; one FP16 score matrix alone is about `1.07B × 2 bytes ≈ 2.15 GB`, before batch, heads, gradients, masks, and other intermediates[^fa-doc].

A larger worked example in the source uses `B=4, H=32, N=8192` in FP16: `B×H×N^2 = 8,589,934,592` elements, or about `17.2 GB` for a single `N×N` tensor[^fa-doc].

## True bottleneck: memory IO, not just FLOPs

Attention compute remains `O(N^2 d)`, which FlashAttention does not remove[^fa-doc].

The observation is that modern GPUs are often memory-bandwidth-bound on attention: repeatedly writing and reading `N×N` matrices through slow HBM costs more than extra arithmetic[^fa-doc].

Relevant hierarchy from the paper's A100 example, fastest to slowest: registers, SRAM/shared memory, HBM/VRAM, with about 192KB SRAM per each of 108 streaming multiprocessors at roughly 19TB/s versus 40–80GB HBM at 1.5–2.0TB/s[^fa-doc][^fa-paper].

FlashAttention therefore trades a small amount of recomputation for much less HBM traffic — “increase a little compute to greatly reduce memory IO” — called IO-aware attention[^fa-doc].

## Tiling

Instead of forming the full `QK^T in R^(N×N)`, FlashAttention splits `Q,K,V` into blocks small enough for SRAM[^fa-doc].

For each query block `Q_i`, it streams `K_j,V_j` blocks through SRAM, computes small `S_ij=Q_i K_j^T`, applies masking, updates softmax state, accumulates into the output, then discards `S_ij`[^fa-doc].

The full `N×N` attention matrix is therefore never stored in HBM; only the final output and small per-row statistics leave SRAM[^fa-doc].

Conceptually:

```text
Standard attention:
Q,K -> full S -> HBM
S -> softmax -> full P -> HBM
P,V -> O

FlashAttention:
Q block + K/V block -> small scores in SRAM
                    -> online softmax
                    -> update O
                    -> discard scores
```

## Why online softmax is needed

Row softmax `softmax(x_i)=exp(x_i)/sum_j exp(x_j)` appears to need the whole row because of the denominator[^fa-doc].

FlashAttention uses numerically stable online softmax with running state per row: maximum `m=max_j x_j` and normalization sum `l=sum_j exp(x_j-m)`, giving `softmax(x_i)=exp(x_i-m)/l`[^fa-doc].

When a new block arrives with stored `(m_old,l_old,o_old)` and new block values `x_new` with corresponding values `v`:

- `m_block=max(x_new)`
- `m_new=max(m_old,m_block)`
- `l_new=exp(m_old-m_new)*l_old + sum_j exp(x_new,j-m_new)`
- `o_new=exp(m_old-m_new)*o_old + sum_j exp(x_new,j-m_new)*v_j`

After all blocks, `O=o/l`[^fa-doc].

## Forward pseudocode

Intuitive form from the source; production CUDA kernels add careful block sizing, thread-block/warp assignment, and register/shared-memory placement[^fa-doc]:

```python
for each query block Qi:
    m = -inf
    l = 0
    Oi = 0

    for each key/value block Kj, Vj:
        Sij = Qi @ Kj.T / sqrt(d)

        if causal:
            Sij = apply_causal_mask(Sij)

        block_max = row_max(Sij)
        new_m = maximum(m, block_max)

        Pij = exp(Sij - new_m)
        correction = exp(m - new_m)

        new_l = correction * l + row_sum(Pij)
        Oi = correction * Oi + Pij @ Vj

        m, l = new_m, new_l

    Oi = Oi / l
```

## Exactness

FlashAttention does not drop tokens, approximate the attention matrix, use low-rank projection, restrict to local windows, or change softmax; it only changes operation order and data movement[^fa-doc].

Mathematically it computes `softmax(QK^T/sqrt(d))V`; residual differences come only from ordinary floating-point effects such as FP16/BF16, reduction order, rounding, and mixed precision, not algorithmic approximation[^fa-doc].

## Complexity

Standard attention: `O(N^2 d)` compute and `O(N^2)` intermediate memory for the attention matrix[^fa-doc].

FlashAttention: still `O(N^2 d)` compute, but auxiliary sequence-dimension memory falls toward `O(Nd)` — output plus per-row statistics — because quadratic intermediates are not materialized[^fa-doc].

The paper formalizes this as IO complexity for SRAM size `M` with `d ≤ M ≤ Nd`: standard attention needs `Θ(Nd + N^2)` HBM accesses while FlashAttention needs `Θ(N^2 d^2 M^-1)`; for typical `d=64–128` and `M≈100KB`, `d^2` is much smaller than `M`, so FlashAttention needs many times fewer accesses[^fa-theory].

The paper's block sizes expose that trade-off directly: `B_c=ceil(M/4d)` and `B_r=min(ceil(M/4d), d)`, giving `Θ(NdM^-1)` passes over `Q` at `Θ(Nd)` elements per pass[^fa-theory].

It also proves a lower bound: no exact-attention algorithm achieves `o(N^2 d^2 M^-1)` HBM accesses for all `M in [d,Nd]`; the argument uses `M=Θ(Nd)`, where any algorithm needs `Ω(Nd)` accesses[^fa-theory].

The same bounds hold for the backward pass: standard `Θ(Nd + N^2)` versus FlashAttention `Θ(N^2 d^2 M^-1)`[^fa-algo].

A GPT-2-medium micros result (seq 1024, head dim 64, 16 heads, batch 64, A100) makes the IO-not-FLOPs point concrete: standard 66.6 GFLOPs, 40.3GB HBM traffic, 41.7ms versus FlashAttention 75.2 GFLOPs, 4.4GB HBM traffic, 7.3ms[^fa-theory].

## Backward pass

Training backward conventionally reuses stored `P=softmax(QK^T)`, which is `N×N` and VRAM-heavy[^fa-doc].

FlashAttention stores only small forward state such as output `O`, row-wise maximum or log-sum-exp, and dropout seeds/counters, then reloads `Q,K,V` blocks and recomputes needed score/probability blocks during backward[^fa-doc].

The paper's backward derivation makes this explicit: `dV=P^T dO`, `dP=dO V^T`, row-wise `dS_{i:}=P_{i:}∘dP_{i:}−D_i P_{i:}` with `dS_{ij}=P_{ij}(dP_{ij}−D_i)`, then `dq_i=Σ_j dS_{ij} k_j` and `dk_j=Σ_i dS_{ij} q_i`, all computable in `O(N)` extra memory by repeated block summation[^fa-algo].

Two implementation tricks matter: rewrite `D_i=P_{i:}^T dP_{i:}` as `D_i=do_i^T o_i` so the reduction is over head dim `d` rather than sequence length `N`, and save only the forward RNG state then regenerate the dropout mask in backward instead of storing an `N×N` mask[^fa-algo].

This selective recomputation uses less memory at the cost of extra matmuls, a favorable trade because GPU matmuls are fast relative to HBM transfers[^fa-doc].

## Causal attention

Decoder-only LLMs mask future positions with `S_ij=-inf` for `j>i`[^fa-doc].

FlashAttention applies the mask per tile and can skip blocks fully above the diagonal, avoiding part of the causal-attention work[^fa-doc].

The paper's full forward pass generalizes this: scale by `τ` (typically `1/√d`), apply a general `mask` mapping disallowed entries to `-inf` (causal, key-padding, or both), then dropout with probability `p_drop` before accumulating into `O`[^fa-algo].

## Relation to Rabe et al.

Both FlashAttention and Rabe et al. (2021) use tiling plus recomputation to avoid storing the `N×N` matrix, but Rabe et al. optimizes total memory footprint while FlashAttention optimizes HBM access count and wall-clock speed: FlashAttention runs 2–4× faster than standard attention where Rabe et al. is roughly the same speed or slightly slower[^fa-algo].

FlashAttention incrementally updates one copy of the output per block instead of keeping temporaries for all blocks, and it uses the analytic `D_i=do_i^T o_i` backward rather than checkpointing per-block temporaries[^fa-algo].

## Kernel fusion

Standard attention maps to several GPU kernels — `QK^T` GEMM, scaling, masking, softmax, dropout, `PV` GEMM — each potentially round-tripping through HBM[^fa-doc].

FlashAttention fuses `QK^T -> scale -> mask -> softmax -> PV` into one tightly coordinated kernel or kernel sequence, keeping intermediates in registers or SRAM[^fa-doc].

Tiling shrinks the working set; fusion reduces HBM round-trips[^fa-doc].

## LLM effects

Training can use saved activation memory for longer sequences, larger batches, faster steps, less attention checkpointing, and higher GPU utilization; the original paper reported end-to-end training speedups on BERT, GPT-2, and long-range tasks, with exact gains hardware- and model-dependent[^fa-doc][^fa-paper].

For the paper's detailed numbers — BERT 15% over MLPerf 1.1, GPT-2 up to 3×, LRA 2.4×, GPT-2 4K perplexity 17.5, long-document and Path-X/Path-256 results, kernel benchmarks to 64K, Apex FMHA deltas, and per-GPU speedups — see [FlashAttention Original Paper Evaluation](flashattention-paper-evaluation.md).

Inference prefill over a long prompt processes many tokens jointly, so FlashAttention helps most there[^fa-doc].

Single-token decode with query length 1 reads KV cache and is bounded differently, so FlashAttention helps less; paged KV cache, MQA/GQA, KV quantization, and continuous batching matter more in that regime[^fa-doc].

## Non-goals

FlashAttention makes full attention more efficient but leaves its `O(N^2)` nature intact: doubling `N` to `2N` still roughly quadruples attention work[^fa-doc].

Very long context may still need sliding-window, sparse, chunked, ring, or sequence-parallel attention, retrieval, state-space or linear/hybrid architectures[^fa-doc].

It mainly optimizes activation/intermediate memory, not model-weight storage or the full KV cache[^fa-doc].

## Comparison with approximate attention

Source comparison, simplified: standard attention is exact but saves neither quadratic FLOPs nor intermediate memory; FlashAttention is exact while saving intermediate memory; sparse, linear, low-rank, and sliding-window methods can save FLOPs and memory but are generally not exact versus full attention[^fa-doc].

The broader lesson highlighted is that equal-FLOPs algorithms can differ greatly in wall-clock speed once memory hierarchy is optimized[^fa-doc].

## Limitations

Each new attention variant still needs a new CUDA kernel written below PyTorch level, with significant engineering effort and limited transfer across GPU architectures; the paper calls for compiling high-level attention code to IO-aware CUDA, analogous to Halide for image processing[^fa-limit].

IO-awareness should extend beyond attention since every layer touches HBM, and single-GPU optimality does not cover multi-GPU attention where inter-GPU transfer adds another IO layer[^fa-limit].

## Evolution: FlashAttention-2 and FlashAttention-3

FlashAttention-2 targets GPU underutilization in FlashAttention-1 by reducing non-matmul work, adding sequence-dimension parallelism including within one head, and improving warp partitioning; the source reports about `2×` over FlashAttention-1 in tested kernel benchmarks, about 50–73% of A100 theoretical peak, and up to 225 TFLOPs/s per A100 in some GPT training configurations[^fa-doc].

For full detail, see [FlashAttention-2 Exact Attention Kernel](flashattention-2.md).

FlashAttention-3 targets NVIDIA Hopper/H100 with warp specialization for loads versus compute, asynchronous data/compute overlap including Tensor Memory Accelerator use, interleaved GEMM and softmax, and FP8 block quantization with error reduction; the source reports about 1.5–2× over FlashAttention-2 on H100 in tested configurations with high FP16/BF16 and FP8 throughput[^fa-doc].

For paper-grounded Hopper mechanisms, 2-stage GEMM-softmax pipelining, FP8 layout and block-quantization plus incoherent-processing details, H100 benchmark method, and numerical-error evidence, see [FlashAttention-3 Asynchronous Low-Precision Attention](flashattention-3.md).

## Relationships

- Evaluated by [FlashAttention Original Paper Evaluation](flashattention-paper-evaluation.md) — synthesis: detailed BERT/GPT-2/LRA/long-document/Path-X/benchmark numbers live there; this page holds the reusable mechanism.
- Extended by [Block-Sparse FlashAttention](flashattention-block-sparse.md) — synthesis: same tiled loop with block-mask skipping for sparsity-proportional IO gains to 64K.
- Uses [FlashAttention-2 Exact Attention Kernel](flashattention-2.md) — synthesis: FA2 is the throughput follow-up that keeps FA1 tiling and online softmax while changing rescaling, sequence parallelism, and warp partitioning.
- Extended by [FlashAttention-3 Asynchronous Low-Precision Attention](flashattention-3.md) — synthesis: Hopper-specific follow-up adding TMA/WGMMA warp specialization, GEMM-softmax overlap, and FP8 block quantization with incoherent processing.
- Contrasts with [FlexAttention Programmable Attention Kernels](flex-attention.md) — synthesis: FlexAttention preserves fused-attention performance while adding compiler-generated score and mask variants; FlashAttention is a fixed exact kernel family.
- Contrasts with [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — synthesis: FlashAttention optimizes dense attention IO; paged attention manages KV-cache layout for serving.
- Contrasts with [LongCat Sparse Attention](longcat-sparse-attention.md) — synthesis: FlashAttention stays exact with quadratic compute and near-linear auxiliary memory; sparse/indexed methods change the attention pattern itself.

## Coverage limits

- Original synthesis `../raw/FlashAttention.md` read in full; arXiv v2 `streaming_attention_neurips_2022.tex`, `src/theory.tex`, `src/algo_details.tex`, and `src/discussion.tex` read in full; `src/intro.tex`, `src/background.tex`, `src/algo.tex`, `src/extension.tex`, and `src/experiments.tex` skimmed for reconciliation.
- Figure PDFs/JPGs under `figs/` were not visually rendered; benchmark and speedup figures are covered only via tex captions and `src/exp_supp.tex` numbers in the companion evaluation concept.
- No secrets, credentials, or PII were found in the compiled sources; public author emails in the tex preamble were not copied.

[^fa-doc]: FlashAttention — `../raw/FlashAttention.md`.
[^fa-paper]: Tri Dao et al., FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness — `../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex`.
[^fa-theory]: Analysis: IO Complexity — `../raw/arXiv-2205.14135v2/src/theory.tex`.
[^fa-algo]: Algorithm Details — `../raw/arXiv-2205.14135v2/src/algo_details.tex`.
[^fa-limit]: Limitations and Future Directions — `../raw/arXiv-2205.14135v2/src/discussion.tex`.
