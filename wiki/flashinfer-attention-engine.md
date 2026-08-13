---
type: Concept
title: FlashInfer attention engine
description: FlashInfer is a CUDA/CUTLASS-based LLM-serving attention engine that maps heterogeneous KV layouts to block-sparse matrices, JIT-specializes attention variants, and schedules variable-length work independently of the compiled kernel.
tags: [flashinfer, attention, gpu-kernels, kv-cache, llm-serving, jit-compilation, scheduling]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-13T00:00:00Z }
sources:
  - id: flashinfer-2025
    resource: ../raw/arXiv-2501.01005v2/main.tex
    title: "FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving"
---

# FlashInfer attention engine

FlashInfer is an LLM-serving attention engine built on CUDA/CUTLASS templates. It represents paged, tree, and sparse-mask KV-cache accesses as block-sparse matrices; JIT-compiles a specified attention variant; and uses a runtime planner to distribute variable-length work while holding the captured kernel configuration fixed for CUDA Graph replay.[^flashinfer-2025]

## Unified cache and composable layouts

FlashInfer packs variable-length query/output tensors without padding and represents the KV cache as a block-sparse-row (BSR) matrix. The paper maps page tables, radix-tree cache layouts, speculative-decoding tree attention, and KV importance masks to this representation; the application chooses the block dimensions. A sparse kernel gathers indexed K/V rows into contiguous shared memory before dense tensor-core computation, while contiguous layouts can use affine addressing.[^flashinfer-2025]

A single block size trades reuse against fragmentation. FlashInfer’s *composable formats* partition one logical attention problem into multiple BSR layouts: a larger query-row block can place shared-prefix K/V in shared memory or registers for several queries, while a small-block layout covers unique suffixes. It combines the partial attention states—output plus log-sum-exp—using the associative attention-composition operation. This is a cache-layout and kernel strategy; it does not change causal-attention semantics.[^flashinfer-2025]

## Custom attention kernels

The engine supplies FlashAttention-2-style templates through Ada and FlashAttention-3-style templates on Hopper, with tile sizes selected at compile time from task and hardware constraints. For irregular sparse loads it uses asynchronous copies; Hopper TMA is limited to fixed-stride contiguous loads in the described implementation.[^flashinfer-2025]

An attention specification can define Q/K/V and output transformations, logits transformation and masking, additional variables, and whether softmax is used. FlashInfer inserts these functors into CUDA templates, compiles with PyTorch’s JIT extension mechanism, and registers a custom operator. The paper identifies custom masks, logits soft-cap, sliding-window attention, fused normalization/RoPE/projection, and non-softmax FlashSigmoid as supported template uses; arbitrary inserted CUDA/PTX also makes this an extensibility and code-safety boundary for an integrator.[^flashinfer-2025]

## Dynamic scheduling and graph capture

At each generation step, the CPU scheduler uses query and KV lengths to split long-KV query tiles, assign chunks to CTAs with a priority queue, and produce a deterministic reduction map for partial attention states. It transfers scheduler metadata to fixed workspace regions and uses persistent attention/contraction kernels. The plan is reusable across layers with matching length specifications, while `run` calls can be CUDA-Graph captured because the grid and workspace pointers remain fixed; `plan` itself remains on the CPU and outside the graph.[^flashinfer-2025]

This separation means the engine can react to changing request lengths without recompiling a different launch shape every step. It also incurs workspace provisioning and host-side planning requirements; the source’s described vLLM integration attributes some BF16 regression to host-side Python overhead and proposes C++ or device-side scheduling as future work.[^flashinfer-2025]

## Scope

The paper describes forward attention only. Backward templates would be needed for training. Its CUDA/CUTLASS implementation targets NVIDIA Turing through Hopper; although the scheduling concept is described as largely backend-agnostic, portability to Triton or other hardware is future work rather than demonstrated support.[^flashinfer-2025]

## Relationships

- **Implements a cache representation compatible with:** [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md), including page-table-style non-contiguous blocks, while adding a kernel and scheduling layer.[^flashinfer-2025]
- **Extends the serving-kernel context of:** [FlashAttention implementation evolution](flashattention-implementation-evolution.md) with sparse gathers, variant JIT, and variable-length scheduling.[^flashinfer-2025]
- **Optimizes:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) through GQA head-group fusion when short query lengths make shared-KV reuse valuable.[^flashinfer-2025]
- **Evaluated by:** [FlashInfer evaluation and serving trade-offs](flashinfer-evaluation-and-serving-trade-offs.md).[^flashinfer-2025]

[^flashinfer-2025]: Zihao Ye et al., “FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving,” arXiv:2501.01005v2, [bundled LaTeX source](../raw/arXiv-2501.01005v2/main.tex), abstract, Sections 2–4 and appendices. The bundled architecture, composable-layout, JIT, and scheduler diagrams were visually reviewed.