---
type: Concept
title: FlashAttention-3 Asynchronous Low-Precision Attention
description: Exact Hopper attention that overlaps GEMMs, softmax, and data movement via warp specialization and adds FP8 with block quantization.
tags: [attention, flashattention, hopper, wgmma, tma, fp8, kernels, io-aware]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T05:09:34Z }
sources:
  - id: fa3-main
    resource: ../raw/arXiv-2407.08608v2/fa3_neurips2024.tex
    title: 'FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision'
  - id: fa3-abstract
    resource: ../raw/arXiv-2407.08608v2/src/abstract.tex
    title: FlashAttention-3 abstract
  - id: fa3-intro
    resource: ../raw/arXiv-2407.08608v2/src/intro.tex
    title: FlashAttention-3 introduction
  - id: fa3-bg
    resource: ../raw/arXiv-2407.08608v2/src/background.tex
    title: FlashAttention-3 background and Hopper execution model
  - id: fa3-algo
    resource: ../raw/arXiv-2407.08608v2/src/algo.tex
    title: FlashAttention-3 algorithm
  - id: fa3-exp
    resource: ../raw/arXiv-2407.08608v2/src/experiments.tex
    title: FlashAttention-3 empirical validation
  - id: fa3-disc
    resource: ../raw/arXiv-2407.08608v2/src/discussion.tex
    title: FlashAttention-3 limitations and conclusion
  - id: fa3-bwd
    resource: ../raw/arXiv-2407.08608v2/src/appendix_algo.tex
    title: FlashAttention-3 backward and pipelining appendix
  - id: fa3-expapp
    resource: ../raw/arXiv-2407.08608v2/src/appendix_experiments.tex
    title: FlashAttention-3 system and FP8 benchmark appendix
  - id: fa3-related
    resource: ../raw/arXiv-2407.08608v2/src/related_work.tex
    title: FlashAttention-3 related work
---

FlashAttention-3 is an exact attention algorithm and Hopper kernel by Shah, Bikshandi, Zhang, Thakkar, Ramani, and Tri Dao that keeps FlashAttention tiling and online softmax while redesigning the kernel around Hopper asynchrony and FP8, reporting 1.5–2.0× over FlashAttention-2 in FP16 forward (up to 740 TFLOPs/s, 75% utilization) and close to 1.2 PFLOPs/s in FP8 on H100[^fa3-abstract][^fa3-intro][^fa3-exp].

Its thesis is that FlashAttention-2 follows a synchronous model and leaves Hopper throughput on the table: about 35% utilization versus 80–90% for optimized GEMM, because Tensor Cores (WGMMA), data movement (TMA), and low-precision units run asynchronously and need explicit overlap[^fa3-intro].

## Hopper substrate

Relevant H100 SXM5 hierarchy from the paper: GMEM 80 GiB at 3.35 TB/s, L2 50 MiB at ~12 TB/s, SMEM 228 KiB per SM at 31 TB/s per GPU, RMEM 256 KiB per SM; thread hierarchy threads, warps, warpgroups, CTAs, clusters, grids[^fa3-bg].

Key mechanisms[^fa3-bg]:

- TMA is a dedicated async GMEM–SMEM copy engine; Hopper WGMMA Tensor Cores are also async and can source operands directly from SMEM.
- Warp specialization splits a CTA into producer warps (TMA loads) versus consumer warps (GEMM plus softmax), improving scheduling and hiding issue latency.
- `setmaxnreg` reallocates registers between warpgroups so MMA warps get more RMEM than single-thread TMA warps.
- FP8 WGMMA offers about 2× FP16/BF16 Tensor Core throughput, but imposes layout conformance: FP8 operands must be k-major in SMEM, and FP32 accumulator versus FP8 operand-A register layouts clash when fusing back-to-back GEMMs.

Standard versus FlashAttention framing is unchanged: standard attention materializes `S` and `P` (`N×N`) to HBM; FlashAttention fuses `QK^T`, softmax, and `PV` into one kernel with block-local softmax rescaling[^fa3-bg].

## Three techniques

1. **Producer-consumer asynchrony with circular SMEM buffer.** Producers issue `Q_i` then `K_j,V_j` TMA loads into an `s`-stage circular buffer and commit/notify; consumers wait on barriers, compute `S=Q_i K_j^T` (SS-GEMM), local softmax update, then `O += P V` (RS-GEMM), and release stages[^fa3-algo].
2. **Pingpong scheduling across warpgroups.** Because softmax special-function throughput (~3.9 TFLOPS on H100) is far below matmul throughput (989 TFLOPS FP16), the paper uses `bar.sync` to force warpgroup 1 GEMMs before warpgroup 2 GEMMs so one group's softmax runs while the other runs GEMMs, then swaps roles; reported gain example 570 to 620–640 TFLOPS for FP16 forward, head dim 128, seqlen 8192[^fa3-algo].
3. **Intra-warpgroup 2-stage GEMM-softmax overlap.** By buffering an extra `S_next` in registers and committing WGMMA without waiting, iteration `j`'s second WGMMA (`P_cur V_{j-1}`) overlaps iteration `j+1`'s softmax on `S_next`; SASS inspection shows the first WGMMA interleaved with softmax/exp/row-sum/`O` rescale and FP32→FP16 conversion, while the second WGMMA runs packed without overlap, as designed[^fa3-algo][^fa3-bwd].

Practical costs: 2-stage needs an extra `B_r × B_c` FP32 tile in registers per threadblock, trading pipeline depth against tile size; the 3-stage variant (overlap first WGMMA from `j+2`, softmax from `j+1`, second WGMMA from `j`) needs still more registers for extra `P` plus `scale_o` and the compiler did not overlap the second WGMMA, so it performed worse[^fa3-algo][^fa3-bwd].

MQA and GQA reuse the FlashAttention-2 approach of adjusting tensor indexing to avoid duplicating `K,V` in HBM[^fa3-algo].

## FP8 path

Efficiency changes[^fa3-algo]:

- `Q,K,V` arrive contiguous in head dim, but FP8 second GEMM needs `V` tiles contiguous in sequence length (k-major); TMA cannot change the contiguous dim, and GMEM pre-transpose or fusing into rotary is awkward for a library or wasteful for memory-bound inference.
- Chosen path is in-kernel transpose of `V` tiles after SMEM load using warp-collective LDSM/STSM (`ldmatrix`/`stmatrix`) at 128-byte granularity in the producer warpgroup, overlapped after the first iteration with the two WGMMAs on the prior `V` and current `K` tile.
- Register clash is fixed with byte permutes: reorder FP32 accumulator bytes from `{d0 d1 d2 d3 d4 d5 d6 d7}`-style order to `{d0 d1 d4 d5 d2 d3 d6 d7}` replicated per 8 bytes (a logical column permutation of the `P` tile), with the in-kernel transpose writing a matching row permutation of `V` so no cross-thread shuffles are needed.

Accuracy changes[^fa3-algo]:

- **Block quantization:** one scale per `B_r × d` or `B_c × d` block for each of `Q,K,V`, fused with a preceding memory-bound op such as rotary embedding; the FlashAttention block loop then absorbs per-block `S` scaling at no extra compute.
- **Incoherent processing:** multiply `Q` and `K` by a random orthogonal `M` before FP8 quantize; `M M^T=I` leaves `(QM)(KM)^T=QK^T` unchanged while spreading outliers because each output entry is a random sum of inputs. Following QuIP/QuIP#, `M` is random `±1` diagonals times a Hadamard matrix: `O(d log d)` and fusable with rotary.

## Backward pass

Backward keeps tiling plus recomputation and adds a third role beyond producer/consumer: a dedicated `dQ`-writer warp that atomically adds per-block `dQ_i^(local)` to global `dQ` via semaphore, avoiding stalls from many blocks contending on the same destination[^fa3-bwd].

Producer loads `K_j,V_j` once, then streams `Q_i,dO_i`; consumers compute `S_i^(j)=Q_i K_j^T`, `dP_i^(j)=dO_i V_j^T`, `P_i^(j)=exp(S-L_i)`, `dS=P∘(dP-D_i)` with precomputed `D=rowsum(dO∘O)`, then `dV+=P^T dO`, `dK+=dS^T Q`, and `dQ^(local)=dS K_j` to SMEM for the writer[^fa3-bwd].

## Reported performance

Benchmark setup on H100 80GB SXM5 with CUDA 12.3, cuDNN 9.1.1.17, CUTLASS 3.5, FA 2.5.8, Triton nightly, PyTorch 2.3.0, clocks fixed at 1830 MHz (989 TFLOPS FP16 peak), averaged over 100 runs; sequence lengths 512–16K with total tokens fixed at 16K, hidden dim 2048, head dims 64/128/256; forward FLOPs `4·seqlen²·hdim·nheads` (halved for causal), backward 2.5× forward[^fa3-exp][^fa3-expapp].

Headline results[^fa3-abstract][^fa3-exp]:

- FP16 forward ~1.5–2.0× FlashAttention-2, up to 740 TFLOPs/s; backward ~1.5–1.75×; up to 3–16× versus standard PyTorch attention.
- For medium/long sequences (≥1K), FP16 often beats the H100-optimized closed-source cuDNN baseline; FP8 reaches close to 1.2 PFLOPs/s.
- At large sequence length, FP16 is ahead of cuDNN and FP8 is competitive with head-dim dependence: head dim 64 ahead, 128/256 about at par without causal mask and behind with causal mask.

Ablation at `{batch,seqlen,nheads,hdim}={4,8448,16,128}`, non-causal FP16: full kernel 661 TFLOPs/s (3.538 ms) versus 582 without GEMM-softmax pipelining and 570 with pipelining but no warp specialization, confirming both contributions[^fa3-exp].

| Config | Full FA3 | No pipelining | No warp-spec |
|---|---|---|---|
| Non-causal FP16, 8448×16×128 | 661 TFLOPs/s | 582 TFLOPs/s | 570 TFLOPs/s |

## Numerical error

Against an FP64 reference with synthetic outliers `N(0,1)+N(0,100)·Bernoulli(0.001)`[^fa3-exp]:

| Method | Baseline FP16 | FA2 FP16 | FA3 FP16 |
|---|---|---|---|
| RMSE | 3.2e-4 | 1.9e-4 | 1.9e-4 |

FP16 FA2/FA3 are ~1.7× better than baseline because softmax intermediates stay in FP32[^fa3-exp].

| Method | Baseline FP8 per-tensor | FA3 FP8 | No block quant | No incoherent |
|---|---|---|---|---|
| RMSE | 2.4e-2 | 9.1e-3 | 9.3e-3 | 2.4e-2 |

FP8 FA3 is ~2.6× more accurate than per-tensor FP8 baseline; the ablation shows incoherent processing carries most of the gain in this outlier regime[^fa3-exp].

## Limits and scope

FP16 FA3 used a persistent kernel plus load-balancing strategy while FP8 FA3 did not, partly explaining weaker small-sequence and causal-mask FP8 results versus FP8 cuDNN; listed future work is inference optimization, persistent FP8 design, and low-precision training effects[^fa3-disc].

The paper claims the async plus low-precision recipe should transfer to other accelerators with robust async execution and low-precision units, not only Hopper; it positions sparse/low-rank approximation, MQA/GQA/MLA KV-cache variants, Ring/striped distributed attention, SSM/RNN alternatives, KV-cache quantization, and LeanAttention/Stream-K load balancing as orthogonal or composable rather than replaced[^fa3-intro][^fa3-disc][^fa3-related].

Code is released permissively via the flash-attention repository with planned PyTorch/Hugging Face integration[^fa3-intro].

## Relationships

- Extends [FlashAttention Exact IO-Aware Attention](flashattention.md) — synthesis: keeps FA1 tiling, fusion, and online softmax while adding Hopper warp specialization and GEMM-softmax overlap.
- Extends [FlashAttention-2 Exact Attention Kernel](flashattention-2.md) — synthesis: starts from FA2 sequence parallelism and lean rescaling, then fixes the reported 35%-utilization Hopper gap with TMA/WGMMA asynchrony and FP8.
- Contrasts with [FlexAttention Programmable Attention Kernels](flex-attention.md) — synthesis: FA3 is a fixed high-throughput exact kernel; FlexAttention trades some peak for compiler-generated score/mask variants.
- Contrasts with [LongCat Sparse Attention](longcat-sparse-attention.md) — synthesis: FA3 stays exact quadratic compute; sparse/indexed methods change the attention pattern for sub-quadratic scaling.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — synthesis: use the serving backend matrix to map FA3 kernel availability and version defaults on Hopper versus FA2/FA4 paths.
- Uses [SGLang Attention Backends](sglang-attention-backends.md) — synthesis: SGLang backend selection determines where FA3-family kernels run for prefill/decode.

## Coverage limits

- `fa3_neurips2024.tex` preamble plus `src/abstract.tex`, `intro.tex`, `background.tex`, `algo.tex`, `experiments.tex`, `discussion.tex`, `related_work.tex`, `appendix_algo.tex`, and `appendix_experiments.tex` read in full; `.bbl`/`.fls`/build files not compiled.
- Figure assets under `figs/` (`*.png`, `*.pdf` speed curves, pipelining diagrams) were not visually rendered; speed claims follow tex body, captions, and tables.
- Numbers are paper-reported H100 results under the stated software/clock methodology, not independent measurements.
- No secrets, credentials, or PII were found; public author contact emails in the tex preamble were not copied.

[^fa3-main]: Jay Shah et al., FlashAttention-3 — `../raw/arXiv-2407.08608v2/fa3_neurips2024.tex`.
[^fa3-abstract]: Abstract — `../raw/arXiv-2407.08608v2/src/abstract.tex`.
[^fa3-intro]: Introduction — `../raw/arXiv-2407.08608v2/src/intro.tex`.
[^fa3-bg]: Background and hardware — `../raw/arXiv-2407.08608v2/src/background.tex`.
[^fa3-algo]: Algorithm — `../raw/arXiv-2407.08608v2/src/algo.tex`.
[^fa3-exp]: Empirical validation — `../raw/arXiv-2407.08608v2/src/experiments.tex`.
[^fa3-disc]: Discussion and limitations — `../raw/arXiv-2407.08608v2/src/discussion.tex`.
[^fa3-bwd]: Backward and pipelining appendix — `../raw/arXiv-2407.08608v2/src/appendix_algo.tex`.
[^fa3-expapp]: System and FP8 appendix — `../raw/arXiv-2407.08608v2/src/appendix_experiments.tex`.
[^fa3-related]: Related work — `../raw/arXiv-2407.08608v2/src/related_work.tex`.
