---
type: Concept
title: FlashInfer evaluation and serving trade-offs
description: FlashInfer reports lower latency than its compared serving and kernel baselines in selected A100/H100 workloads, while sparse gathering, host planning, integration overhead, and workload shape constrain those results.
tags: [flashinfer, evaluation, llm-serving, gpu-kernels, kv-cache, latency]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-13T00:00:00Z }
sources:
  - id: flashinfer-2025
    resource: ../raw/arXiv-2501.01005v2/main.tex
    title: "FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving"
---

# FlashInfer evaluation and serving trade-offs

On the authors’ NVIDIA A100 40 GB SXM and H100 80 GB SXM experiments (CUDA 12.4, PyTorch 2.4.0, FP16), FlashInfer v0.2 reports lower latency than the paper’s selected baselines for variable-length serving, fused long-context attention, and moderate-degree shared-prefix parallel generation. These are author-reported measurements under named models, servers, request distributions, precision, and integration versions—not general latency guarantees.[^flashinfer-2025]

## Serving and kernel results

With SGLang v0.3.4, Llama 3.1 8B on one H100, the paper’s plot reports median inter-token latency of 13.5 ms versus 21.7 ms for its Triton setting on ShareGPT and 9.1 versus 29.6 ms on a synthetic 512–2048-token input-length workload. For Llama 3.1 70B on four H100s, the plotted values are 24.0 versus 48.3 ms (ShareGPT) and 21.8 versus 30.7 ms (synthetic). The paper summarizes these results as a 29–69% inter-token-latency reduction, with P99 TTFT constrained below 200 ms by adjusting request rate.[^flashinfer-2025]

At fixed batch size 16, the kernel study compares constant 1,024-token, uniform 512–1,024-token, and Zipf-distributed KV lengths against an identified FlashAttention repository commit. The authors attribute their higher measured bandwidth/FLOPs utilization under uneven lengths to runtime load balancing and, for decode, to additional tile-size choices. This supports adaptation to the tested length distributions, not superiority for every batch shape or baseline configuration.[^flashinfer-2025]

For Streaming-LLM running Vicuna-13B on MT-Bench, the paper reports a 28–30% inter-token-latency reduction from a FlashInfer RoPE-attention fusion versus its optimized unfused comparison; its plotted H100 values are 13.2–13.4 ms for fused FlashInfer versus 18.2–20.0 ms for unfused FlashAttention across recent-window sizes 1K–4K. The gain is evidence for this fusion and workload, not evidence that fusion helps every attention variant.[^flashinfer-2025]

## Cache-layout and integration boundaries

For shared-prefix parallel generation in MLC-Engine, composable formats performed best at moderate parallel degrees ($4\leq n\leq32$). At $n=4$, the reported peak ITL reductions were 13.73% for Llama 3.1 8B and 17.42% for 70B; the paper reports no benefit at small degrees and plateauing gains at large degrees as attention became less dominant. The attached scatter plot corroborates that several $n=1$ or $n=2$ configurations favor the single format.[^flashinfer-2025]

The appendix reports negligible (within 1%) sparse-versus-dense decode-kernel difference for its page-size-one configuration, but about a 10% prefill gap. On Hopper, sparse gathers cannot use fixed-stride TMA in the described design, so they fall back to asynchronous copies and pointer arithmetic with higher register pressure and smaller KV tiles. Larger sparse blocks could allow TMA, but reduce layout flexibility.[^flashinfer-2025]

The paper’s vLLM integration table illustrates that a faster kernel does not automatically improve an end-to-end server: its BF16 case has slightly worse median ITL/TTFT than the default (10.63/36.60 ms versus 10.42/35.85 ms), while FP8 KV cache reports 10.92/37.93 ms versus 12.56/39.74 ms. The authors attribute the BF16 regression to host-side Python overhead. Treat this as a version-specific integration observation, not a vLLM-wide result.[^flashinfer-2025]

## Evidence limits

All comparisons are from the FlashInfer authors. The source does not establish independent reproducibility, current behavior of SGLang/vLLM/MLC-Engine, model quality, cost, tail latency beyond its stated P99 TTFT constraint, or performance on non-NVIDIA hardware. Its conclusions also depend on cache layout, model/head configuration, request rate, context and output lengths, precision, and whether the full serving path—not only an attention kernel—is measured.[^flashinfer-2025]

## Relationships

- **Evaluates:** [FlashInfer attention engine](flashinfer-attention-engine.md), separating the engine’s architecture from configuration-bounded outcomes.[^flashinfer-2025]
- **Contextualizes:** [PagedAttention evaluation and serving trade-offs](pagedattention-evaluation-and-serving-trade-offs.md): cache layout and specialized kernels must be evaluated with the full server and workload rather than inferred from allocation efficiency alone.[^flashinfer-2025]
- **Extends the deployment boundary of:** [FlashAttention implementation evolution](flashattention-implementation-evolution.md) with serving-specific variable-length and fusion measurements.[^flashinfer-2025]

[^flashinfer-2025]: Zihao Ye et al., “FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving,” arXiv:2501.01005v2, [bundled LaTeX source](../raw/arXiv-2501.01005v2/main.tex), abstract, Section 5, and appendices. The bundled variable-length, SGLang latency, Streaming-LLM, and parallel-generation figures were visually reviewed; numerical claims here are author-reported under the stated configurations.