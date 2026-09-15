---
type: Concept
title: FlashInfer Attention Engine
description: Code-generated block-sparse attention engine with composable KV-cache formats, JIT attention variants, and load-balanced CUDAGraph-compatible scheduling.
tags: [attention, flashinfer, kv-cache, block-sparsity, jit, scheduling, cudagraphs, llm-serving]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: fi-abs
    resource: ../raw/arXiv-2501.01005v2/sections/abs.tex
    title: FlashInfer abstract
  - id: fi-intro
    resource: ../raw/arXiv-2501.01005v2/sections/intro.tex
    title: FlashInfer introduction
  - id: fi-bg
    resource: ../raw/arXiv-2501.01005v2/sections/background.tex
    title: FlashInfer background on FlashAttention, composition, and block sparsity
  - id: fi-design
    resource: ../raw/arXiv-2501.01005v2/sections/design.tex
    title: FlashInfer storage, compute, JIT, runtime, and API design
  - id: fi-eval
    resource: ../raw/arXiv-2501.01005v2/sections/evaluation.tex
    title: FlashInfer kernel and end-to-end evaluation
  - id: fi-related
    resource: ../raw/arXiv-2501.01005v2/sections/related-work.tex
    title: FlashInfer related work
  - id: fi-discuss
    resource: ../raw/arXiv-2501.01005v2/sections/discussions.tex
    title: FlashInfer discussion and generality limits
  - id: fi-concl
    resource: ../raw/arXiv-2501.01005v2/sections/conclusion.tex
    title: FlashInfer conclusion
  - id: fi-app
    resource: ../raw/arXiv-2501.01005v2/sections/appendix.tex
    title: FlashInfer appendix on GQA fusion, sparsity overhead, backend choice, memory, overlap, FP8, and extra evaluation
  - id: fi-main
    resource: ../raw/arXiv-2501.01005v2/main.tex
    title: FlashInfer paper front matter and authorship
  - id: fi-code
    resource: ../raw/arXiv-2501.01005v2/code/programming_interface.py
    title: FlashInfer PyTorch programming-interface example
---

FlashInfer is a code-generation attention engine for LLM serving that unifies heterogeneous KV-cache layouts in block-sparse formats, generates custom attention variants by JIT, and schedules variable-length work with load balancing while staying CUDAGraph-compatible[^fi-abs][^fi-intro].

It is reported integrated with SGLang, vLLM, and MLC-Engine, and evaluated as v0.2 on A100/H100 with CUDA 12.4, PyTorch 2.4.0, and fp16 storage/computation[^fi-intro][^fi-eval]. The project is published as `FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving` by Ye et al. with project page `http://flashinfer.ai`[^fi-abs][^fi-main].

## Unified block-sparse KV-cache storage

Queries and outputs are packed as unpadded ragged tensors; keys/values start ragged from the same `W_q/W_k/W_v` projections and then join a KV-cache stored as block-sparse-row (BSR) with arbitrary `(B_r, B_c)`[^fi-design].

PageAttention page tables, RadixAttention radix trees, tree attention for speculative decoding, and importance masks are all represented as sparse matrices under this abstraction[^fi-design]. This builds on the older page-table-as-sparse-matrix view and on the paper's claim that block sparsity improves register reuse, tensor-core compatibility, and empty-block skipping[^fi-design][^fi-bg].

`B_r` is aligned with the query tile size `T_q`; `B_c` is set by KV-cache management[^fi-design].

## Composable formats for shared prefix

A single fixed `B_r` forces a fragmentation versus reuse trade-off: larger `B_r` improves shared-memory/register reuse inside a block but increases fragmentation, while different blocks cannot share shared memory[^fi-design].

FlashInfer therefore decomposes the KV sparse matrix into multiple BSR formats when prior knowledge exists, notably a dense shared-prefix submatrix stored with larger `B_r` plus a per-request suffix with smaller `B_r`, without moving KV data—only indices and indptr arrays are computed[^fi-design].

The claimed benefit is that the larger-block prefix path can reuse KV through fast shared memory/registers rather than only global memory or L2[^fi-design]. Unlike cited prefix-decoding systems requiring separate prefix/suffix KV management, composable formats are presented as supporting multi-level, multiple-prefix decoding under unified page-table management[^fi-related].

## Compute template and sparse data movement

Templates are CUDA/CUTLASS for NVIDIA Turing through Hopper (`sm75`–`sm90a`), using the FlashAttention-2 algorithm up to Ada (`sm89`) and FlashAttention-3 on Hopper[^fi-design].

Sparse or dense KV tiles are gathered from scattered global memory into contiguous shared memory before dense tensor-core math; sparse addresses come from BSR `indices`, dense addresses from affine row transforms[^fi-design]. The head dimension `d` (commonly 128 or 256) stays contiguous for coalesced access with 128B `LDGSTS` async copies[^fi-design].

Hopper Tensor Memory Accelerator (TMA) is used only for contiguous KV because TMA does not support non-affine access; other sparse cases fall back to Ampere-style async copies[^fi-design][^fi-app].

## Tile-size selection and GQA fusion

FlashAttention operational intensity is given as `O(1/(1/l_qo + 1/l_kv))`, simplified to `O(l_qo)` for serving where query length is at most KV length, and `O(g·l_qo)` for MQA/GQA with group size `g = H_qo/H_kv`[^fi-bg].

FlashInfer provides FA2 query/key tile combinations from `{1,16,32,64,128} × {32,64,128}` and FA3 row tiles that are multiples of 64 for WGMMA; query tile 1 uses CUDA cores because tensor-core minimum `m` is 16, larger query tiles use tensor cores[^fi-design].

Heuristic selection is: pick the minimal query tile covering average query length (with GQA query length fused with head-group size), then maximize SM occupancy under register/shared-memory constraints for KV tile size[^fi-design].

For short-query GQA, head-group fusion maps different KV heads to threadblocks while fusing query heads with the query-length dimension, so one shared-memory KV load serves a whole query group; fusion is less important once query length alone saturates reuse[^fi-app].

## JIT attention variants

The paper argues per-variant handwritten CUDA libraries are unsustainable, so most variants reuse the FlashAttention skeleton with small functor substitutions[^fi-design].

User variant classes supply[^fi-design]:

- `QueryTransform`, `KeyTransform`, `ValueTransform`: pre-attention transforms, usable to fuse normalization, RoPE, or projection.
- `OutputTransform`: post-attention transform.
- `LogitsTransform`, `LogitsMask`: logits postprocessing such as custom masks, soft-cap, or sliding windows.
- Optional softmax toggle, enabling non-softmax variants such as FlashSigmoid.

CUDA code strings populate kernel templates, are JIT-compiled with PyTorch's JIT extension path, registered as custom ops, and can also target other runtimes via DLPack; users may embed PTX or their own libraries[^fi-design].

This extends the [FlexAttention Programmable Attention Kernels](flex-attention.md) style `score_mod`/`mask_mod` interface with query/key transforms, but generates CUDA/CUTLASS rather than Triton; the paper positions CUDA/CUTLASS as giving earlier access to warp specialization/TMA and finer register control, and says FlashInfer can serve as a forward-pass backend for FlexAttention[^fi-design][^fi-related][^fi-app].

## Load-balanced dynamism-aware runtime

Attention state is defined as output plus log-sum-exp scale, with an associative/commutative composition operator `⊕` analogous to GEMM summation; this is the canonical reduction used after KV splitting[^fi-bg]. Ring-Attention and Flash-Decoding are cited as prior users of the same property[^fi-bg].

The scheduler takes per-request `{l_qo(i), l_kv(i)}` plus `T_q`, estimates total work, computes a maximum KV chunk `L_kv` as total query-tile-weighted KV divided by CTA count, splits query tiles into chunks bounded by `L_kv`, sorts chunks descending, and greedily assigns each chunk to the currently least-loaded CTA under `cost(l_q,l_kv) = α·l_q + β·l_kv`[^fi-design].

Long-KV chunks produce partial outputs in a user-provided workspace; a variable-length composition kernel contracts them deterministically without Stream-K-style atomic aggregation[^fi-design]. The same plan is reused across layers in a generation step[^fi-design].

CUDAGraph compatibility is preserved by fixed grid size, persistent attention plus contraction kernels (merged into one persistent kernel), and fixed workspace-section offsets so pointers remain stable across steps[^fi-design][^fi-app].

Short-KV requests use split-K writethrough directly to the final output, saving workspace and contraction work; the stated partial-output upper bound is `2·#CTA·T_q·H_qo·(D+1)`, with `#CTA = k·#SM` typically `k ≤ 2` on Ampere and often 1 on Hopper[^fi-app]. Scheduler metadata maxima derive from user-supplied bounds on concurrent requests and accumulated length; host pinned buffers are copied async to device sections[^fi-app].

## Programming interface

The PyTorch flow initializes an attention wrapper from variant spec, task info, and workspace, JIT-compiles and caches kernels, optionally builds multiple wrappers/graphs for different block sizes or average query lengths, plans each generation step on CPU, and replays the selected CUDAGraph[^fi-design][^fi-code].

`plan(seqlen_info)` runs the CPU scheduler and is reusable across operators with matching length specs; `run(query,key,value,plan)` executes attention and is CUDAGraph-capturable[^fi-design][^fi-code]. The paper explicitly frames this `plan`/`run` split as Inspector-Executor for irregular workloads[^fi-design].

The scheduler can also accept a user SM budget to reserve SMs for overlapped GEMM, attention, and communication in the style of Nanoflow[^fi-app].

## Reported evaluation

Kernel and serving claims below inherit the paper's v0.2 setup, datasets, model/baseline versions, and H100/A100 hardware; they are paper-reported, not independently verified.

End-to-end SGLang v0.3.4 versus Triton v3.0 on ShareGPT plus synthetic uniform `512–2048` work, tuned to P99 TTFT below 200 ms, on Llama-3.1-8B (1×H100) and 70B (4×H100), shows consistent ITL/TTFT wins for FlashInfer in the paper's charts[^fi-eval]. The abstract packages the headline as 29–69% ITL reduction versus compiler backends on serving benchmarks, 28–30% long-context latency reduction, and 13–17% parallel-generation speedup[^fi-abs][^fi-eval].

Variable-length kernels use batch 16 with constant 1024, uniform `512–1024`, and Zipf-skewed average 1024 against FlashAttention main at commit `c1d146c`; FlashInfer is reported strongest on uniform/skewed mixes from load balancing and on decode from tile-size choice[^fi-eval].

Long-context Streaming-LLM fuses RoPE into attention with about 20 extra lines for query/key transforms; on Vicuna-13B/MT-Bench this is reported as 28–30% end-to-end latency reduction across recent-window settings and 1.6–3.7× higher bandwidth than unfused RoPE plus attention[^fi-eval].

Parallel generation in MLC-Engine with prefix caching on Llama-3.1-8B/70B and ShareGPT at request rate 16, varying `n ∈ {1,2,4,8,16,32,64}`, shows composable-format wins for moderate `n = 4–32`, peaking at `n=4` with ITL down 13.73% (8B) and 17.42% (70B) and TTFT down 16.41% (8B) and 22.86% (70B); very small `n` lacks enough block-size gain and very large `n` becomes non-attention-bound[^fi-eval].

Appendix AttentionGym comparison on H100 (batch 16, 16 heads, head dim 128, CUDA 12.4/Triton 3.2) reports FlashInfer ahead of FlexAttention on causal, logits-softcap, ALiBi, and sliding-window-1024 cases from 512 to 16384 tokens, attributed to Hopper warp specialization/TMA and CUTLASS register control[^fi-app].

Shared-prefix microbenchmarks with suffix 128 report larger composable-format gaps for long prefixes and larger batches, e.g. 32768-token prefix at batch 64 around 254.54 µs composable versus 4090 µs single format[^fi-app].

Load-balancing ablations on Llama-3.1-8B-Instruct/H100/SGLang report, for example, uniform `4096–16384` ITL 8.63 ms with balancing versus 13.89 ms without and 11.08 ms Triton; ShareGPT and `512–2048` gaps are smaller[^fi-app].

vLLM integration at request rate 16 reports about 13% ITL reduction with fp8 `e4m3` KV (12.56 ms default versus 10.92 ms FlashInfer) but a small bf16 regression attributed to host-side Python array overhead, with planned C++/device-scheduler fixes[^fi-app].

Fine-grained Quest sparsity (block 16, 32 query/KV heads, dim 128, H100) is reported up to about 20× faster than PyTorch SDPA/FlexAttention paths; sparse-versus-dense decode is within about 1%, causal prefill has about a 10% gap, larger on FA3 because sparse gather cannot use TMA[^fi-app].

Mixed fp8-KV/fp16-query-output attention uses the cited fast dequantization/fragment-shuffle approach to cut memory and bandwidth without claimed material accuracy loss[^fi-app].

## Limits and future work

Coverage is forward-pass attention only; training/backward templates, higher-level DSL inputs such as Mirage/FlexAttention specifications, and additional backends such as ThunderKittens/DSL/Triton variants are listed as future work[^fi-discuss][^fi-concl][^fi-related].

The template design space is summarized as `f_epilogue(scan(f_logits(f_q(Q)·f_k(K)))·f_v(V))`, claimed to cover MLA and linear-attention intra-attention components; FlashDecoding++-style scale-statistics/TMA-store-reduce changes are called orthogonal future work[^fi-discuss][^fi-related].

## Coverage limits

- All `.tex` sections, `main.tex`, and `code/programming_interface.py` were read; `figures/*.pdf` charts were interpreted through body text, captions, and tables rather than independent visual measurement.
- Build files such as `.sty`, `.bst`, and `.bbl`/`.bib` were not treated as knowledge sources.
- Performance numbers are scoped to the paper's v0.2 code, GPU types, CUDA/PyTorch versions, model/config, baseline commits, and workload distributions.

## Relationships

- Uses [FlashAttention Exact IO-Aware Attention](flashattention.md) — online-softmax and kernel-fusion foundation extended to sparse/JIT/load-balanced serving kernels.
- Uses [FlashAttention-2 Exact Attention Kernel](flashattention-2.md) — FA2 template source for pre-Hopper FlashInfer kernels and tile/scheduling extensions.
- Uses [FlashAttention-3 Asynchronous Low-Precision Attention](flashattention-3.md) — FA3/WGMMA template source for Hopper FlashInfer kernels.
- Uses [PagedAttention for LLM Serving](paged-attention.md) — PageAttention page tables are one of the KV layouts unified as BSR/composable formats.
- Uses [Grouped-Query Attention](grouped-query-attention.md) — GQA grouping motivates head-group fusion and query-length fusion in tile selection.
- Uses [SGLang Attention Backends](sglang-attention-backends.md) — SGLang is a primary integration and end-to-end evaluation target.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — vLLM is a primary integration and fp8-KV evaluation target.

[^fi-abs]: FlashInfer abstract — `../raw/arXiv-2501.01005v2/sections/abs.tex`.
[^fi-intro]: FlashInfer introduction — `../raw/arXiv-2501.01005v2/sections/intro.tex`.
[^fi-bg]: FlashInfer background on FlashAttention, composition, and block sparsity — `../raw/arXiv-2501.01005v2/sections/background.tex`.
[^fi-design]: FlashInfer storage, compute, JIT, runtime, and API design — `../raw/arXiv-2501.01005v2/sections/design.tex`.
[^fi-eval]: FlashInfer kernel and end-to-end evaluation — `../raw/arXiv-2501.01005v2/sections/evaluation.tex`.
[^fi-related]: FlashInfer related work — `../raw/arXiv-2501.01005v2/sections/related-work.tex`.
[^fi-discuss]: FlashInfer discussion and generality limits — `../raw/arXiv-2501.01005v2/sections/discussions.tex`.
[^fi-concl]: FlashInfer conclusion — `../raw/arXiv-2501.01005v2/sections/conclusion.tex`.
[^fi-app]: FlashInfer appendix on GQA fusion, sparsity overhead, backend choice, memory, overlap, FP8, and extra evaluation — `../raw/arXiv-2501.01005v2/sections/appendix.tex`.
[^fi-main]: FlashInfer paper front matter and authorship — `../raw/arXiv-2501.01005v2/main.tex`.
[^fi-code]: FlashInfer PyTorch programming-interface example — `../raw/arXiv-2501.01005v2/code/programming_interface.py`.
