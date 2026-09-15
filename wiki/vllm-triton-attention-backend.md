---
type: Concept
title: vLLM Triton Attention Backend
description: Performance-portable Triton paged-attention backend with Q-block tiling, parallel softmax, and persistent kernels for CUDA-graph efficiency.
tags: [vllm, attention, triton, portability]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T03:48:36Z }
sources:
  - id: triton-backend
    resource: ../raw/2026-03-04-vllm-triton-backend-deep-dive/index.md
    title: vLLM Triton Attention Backend Deep Dive
---

vLLM's Triton attention backend is a single portable paged-attention implementation that matches specialized kernels while running unchanged on NVIDIA, AMD, and Intel GPUs through tile autotuning, query-side blocking, split-KV parallel softmax, and fixed-grid persistent kernels for CUDA Graphs[^triton-backend].

## Why Triton for portability

Writing many specialized kernels per model and GPU generation does not scale across NVIDIA Hopper/Blackwell, AMD MI300, Intel, and future platforms[^triton-backend].

Triton addresses this as a Python-embedded GPU DSL with a tiled programming model: developers express logical tiles while the compiler and autotuner map tile shapes and layouts to each GPU, trading a small amount of low-level control for hardware-agnostic source portability[^triton-backend].

The source cites autotuning as central to portability, pointing to `GPU Performance Portability needs Autotuning (arxiv.org)`[^triton-backend].

## Backend position

vLLM isolates attention behind an attention-backend abstraction separating attention from linear layers and norms; alongside FlashAttention, FlashInfer, ROCm, and MLA-specialized backends, the Triton backend is implemented entirely in Triton and native to vLLM[^triton-backend].

Implementation lives at `vllm/v1/attention/backends/triton_attn.py` with the unified kernel at `vllm/v1/attention/ops/triton_unified_attention.py`[^triton-backend].

It was built over the past year by IBM Research, Red Hat, and AMD, is now community maintained, depends only on PyTorch plus Triton, is always available, and therefore doubles as a fallback when FlashAttention, FlashInfer, or other dependencies are unavailable or fail to import[^triton-backend].

The source reports roughly 800 lines for the Triton paged-attention implementation versus around 70,000 for FlashAttention 3[^triton-backend].

## When it is used

Reported selection rules[^triton-backend]:

- Default on AMD ROCm GPUs and used on Intel XPU.
- Fallback for float32 where FlashAttention lacks fp32 support.
- Required-feature path for ALiBi sqrt used by StepFun audio models, plus sink tokens and GPT-OSS behavior, particularly on pre-Hopper NVIDIA GPUs such as A100.
- Supports small head sizes, encoder and decoder attention, multimodal prefix attention, and batch invariance.

## Development method: microbenchmarks first

The kernel was first built outside vLLM against a vLLM-compatible API and tuned in isolation before end-to-end integration[^triton-backend].

Isolated [microbenchmarks](https://github.com/foundation-model-stack/vllm-triton-backend) covered prefill-heavy, decode-heavy, and mixed workloads across batch sizes and context lengths; microbenchmarks expose kernel behavior hidden by system effects, and the results showed no single variant dominates all regimes[^triton-backend].

Inspected Figure 2 plots normalized latency versus token count for `decode_share 0.0/0.5/1.0`, comparing Triton GQA-opt, parallel-tiled, naive, and `flash_attn`: GQA-opt leads at small token counts in prefill/mixed, while differences compress at large decode-heavy sizes[^triton-backend].

## Paged kernel structure

For each query batch, the kernel processes each query token, iterates query heads and corresponding KV heads, then traverses the paged KV cache to compute scores and apply values; query tokens form one axis, query heads another, and KV-page traversal is the innermost loop, with causal masking and sliding windows omitted from the overview diagram[^triton-backend].

For low-level details the source defers to the kernel authors' PyTorch blog on enabling vLLM v1 on AMD GPUs with Triton[^triton-backend].

## Q blocks for `tl.dot` utilization

Attention matmuls use `tl.dot`, which needs large tiles; KV-side tiles are constrained by KV-cache page size, so optimization focuses on the query side[^triton-backend].

For grouped-query attention, all query heads sharing one KV head are processed together to increase cache reuse; multiple query tokens are additionally grouped into one work item called a Q block[^triton-backend].

The launch grid spans batch size and KV heads while Q blocks set how many query tokens and heads each kernel instance handles; autotuning picks block sizes per platform[^triton-backend].

Inspected Figure 4 formalizes this as `BLOCK_M / BLOCK_Q = num_query_heads / num_kv_heads`, with `BLOCK_Q` query tokens, `BLOCK_M/BLOCK_Q` query heads, and `HEAD_SIZE` features per Q block[^triton-backend].

## Parallel tiled softmax for decode

Q blocking helps prefill but not decode, where only one query token exists; the backend therefore adds KV-split parallelism via parallel tiled softmax, called the "3D kernel"[^triton-backend].

KV traversal is split across kernel instances computing partial results followed by a reduction; because Triton has no global barrier, reduction needs a second kernel launch, so heuristics weigh added parallelism against launch overhead[^triton-backend].

## CUDA Graphs: variable grids to persistent kernels

CUDA Graphs cut launch overhead by replaying fixed graphs, but attention launch grids normally vary with batch and sequence length[^triton-backend].

GPUs run kernels in SM-sized waves, so oversubscribed grids tail with underutilized waves; capturing that shape freezes the waste, replaying extra work and latency even after the effective workload shrinks[^triton-backend].

Early kernels used variable launch grids scaling with workload, which interacts poorly with graphs; the fix is persistent kernels with PRs pending at the time of writing: launch a fixed instance count sized to compute resources, let each instance read GPU-resident metadata to claim work, and keep the grid constant for efficient graph reuse[^triton-backend].

This explains the companion design note that Triton prefers `FULL_AND_PIECEWISE` because its prefill/mixed and pure-decode kernels differ[^triton-backend].

## Benchmark results

Late-2025 end-to-end results for Llama 3.1 8B at batch size 1 and 500 input tokens on H100 and MI300, swept over output length[^triton-backend]:

- H100: Triton reached 100.7% of FlashAttention 3 performance on long decodes.
- MI300: about 5.8x speedup over earlier implementations.
- Same Triton source ran on both platforms.

Inspected Figure 9(a) for H100 shows the Triton baseline far above FlashAttention V3 at long outputs, Q-block tiling closing much of the gap, and Q-block plus parallel tiled softmax plus static launch grid converging onto the FlashAttention curve[^triton-backend].

## Helion preview

Helion, described as a higher-level Triton or tiled PyTorch from the PyTorch team, was used for a simplified experimental paged-attention kernel with promising early results; code was a draft vLLM PR 27293 and write-up a PyTorch blog on portable paged attention in Helion[^triton-backend].

Further results are deferred to `The Anatomy of a Triton Attention Kernel (arxiv.org)`[^triton-backend].

## Coverage limits

- Figures 1, 3, and 5–8 were compiled from prose and captions; Figures 2, 4, and 9(a) were additionally pixel-inspected. Figure 9(b) for MI300 and exact numeric tables were not present in `raw/` beyond the prose summary[^triton-backend].
- External code, microbenchmark repo, Office Hours video, PyTorch blogs, Helion draft PR, and both arXiv papers were referenced but not ingested; persistent-kernel PRs were still pending at publication time[^triton-backend].
- The source is adapted from a Red Hat-hosted vLLM Office Hours session with Burkhard Ringlein of IBM Research[^triton-backend].

## Relationships

- Uses [vLLM Attention Backends](vllm-attention-backends.md) — backend registry and priority/feature tables are the selection context in which this portable Triton implementation and its fallback role apply.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — historical CUDA paged-attention walkthrough illustrates the query/key/value and softmax computation this Triton unified kernel reimplements portably.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — dispatcher, `BatchDescriptor` keys, and full versus piecewise capture are the mechanism that variable grids break and persistent fixed-grid kernels repair.

[^triton-backend]: vLLM Triton Attention Backend Deep Dive — `../raw/2026-03-04-vllm-triton-backend-deep-dive/index.md`.
