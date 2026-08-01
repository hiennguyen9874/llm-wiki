---
type: Concept
title: DeepSeek-V3 training systems and FP8
description: DeepSeek-V3 reports co-designed DualPipe scheduling, cross-node MoE communication, and fine-grained FP8 mixed precision to reduce communication and memory overhead in a 671B-parameter training run.
tags: [deepseek-v3, distributed-training, mixture-of-experts, fp8, pipeline-parallelism, inference]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:38:26Z }
sources:
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
---

# DeepSeek-V3 training systems and FP8

DeepSeek-V3 reports a co-designed training stack for cross-node MoE: DualPipe overlaps forward/backward work with pipeline and all-to-all communication, custom kernels route traffic across InfiniBand and NVLink, and a fine-grained FP8 framework reduces GEMM, activation-storage, optimizer-state, and dispatch costs while retaining selected computations in higher precision.[^deepseek-v3-2024]

## Parallelism and communication

The reported run uses 16-way pipeline parallelism, 64-way expert parallelism across eight nodes, and ZeRO-1 data parallelism on 2,048 H800 GPUs. DualPipe feeds microbatches bidirectionally and splits backward work into input and weight-gradient components, scheduling paired chunks to overlap compute with both pipeline and all-to-all communication. The system avoids tensor parallelism and recomputes RMSNorm and MLA up-projections to reduce activation storage.[^deepseek-v3-2024]

Each token routes to at most four nodes. The custom all-to-all kernels send traffic across InfiniBand to a same-index GPU on a target node, then forward it over NVLink to the expert GPU; the report allocates 20 streaming multiprocessors to ten dynamically assigned communication channels. These reported overlaps and bandwidth figures depend on this topology, routing constraint, kernels, and workload; they are not a generic all-to-all latency bound.[^deepseek-v3-2024]

For serving, the report separates prefill from decode and adds redundant copies of high-load experts based on periodically observed traffic. This can improve load balance but requires large deployment units (32 GPUs for prefill and 320 GPUs for decode in the stated setup), which the authors identify as an operational limitation.[^deepseek-v3-2024]

## Fine-grained FP8 framework

V3 executes GEMMs in FP8, but keeps embeddings, output heads, MoE gating, normalization, and attention in BF16 or FP32 where needed. Activations use 1×128 tile scales and weights 128×128 block scales; intermediate FP8 GEMM results are promoted to CUDA cores for FP32 accumulation every 128 inner-dimension elements. The framework uses E4M3 for all FP8 tensor roles, online scale calculation, FP8 cached activations and MoE dispatch, BF16 AdamW moment states, and FP32 master weights and gradients.[^deepseek-v3-2024]

The report’s FP8-versus-BF16 ablations on approximately 16B and 230B MoE models claim loss error below 0.25%. A separate experiment finds block-wise activation-gradient quantization diverged for a 16B model, illustrating that its quantization granularity is a stability condition rather than a mere storage format choice.[^deepseek-v3-2024]

## Relationships

- **Implements:** [DeepSeek-V3 architecture and pretraining](deepseek-v3-architecture-and-pretraining.md).
- **Implements:** [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md) with node-limited routing and redundant serving experts.
- **Operationalizes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) through expert parallelism, routing limits, dispatch, and serving placement.

## Evidence limits

The report is primary evidence for this particular stack, but it does not supply source code, independent reproductions, or component-level end-to-end cost attribution. The FP8 ablation is smaller than V3, and reported efficiency does not establish comparable behavior on another accelerator, network, model shape, or serving mix.[^deepseek-v3-2024]

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex) and included [FP8 section](../raw/arXiv-2412.19437v2/content/fp8.tex), Sections 3–4 and Appendix A.
