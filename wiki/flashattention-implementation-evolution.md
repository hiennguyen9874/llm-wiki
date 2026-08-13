---
type: Concept
title: FlashAttention implementation evolution
description: FlashAttention-2 and -3 retain tiled exact attention while improving GPU work partitioning and, on Hopper, asynchronous low-precision execution; benefits are greatest for long-prompt prefill rather than one-token decode.
tags: [flashattention, gpu-kernels, prefill, decoding, kv-cache, hopper]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-13T23:21:30+07:00 }
sources:
  - id: flashattention-2022
    resource: ../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex
    title: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"
  - id: flashattention-summary
    resource: ../raw/FlashAttention.md
    title: "FlashAttention overview (Vietnamese summary)"
  - id: flashattention-2-summary
    resource: ../raw/FlashAttention-2.md
    title: "FlashAttention-2 overview (Vietnamese summary)"
  - id: flashattention-2-2023
    resource: ../raw/arXiv-2307.08691v1/flash2.tex
    title: "FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning"
  - id: flashattention-3-2024
    resource: ../raw/arXiv-2407.08608v2/fa3_neurips2024.tex
    title: "FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision"
  - id: flashinfer-2025
    resource: ../raw/arXiv-2501.01005v2/main.tex
    title: "FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving"
---

# FlashAttention implementation evolution

FlashAttention-2 and FlashAttention-3 retain tiled, exact softmax attention while targeting progressively better hardware utilization: FlashAttention-2 changes work partitioning and sequence parallelism, and FlashAttention-3 targets NVIDIA Hopper with asynchronous, warp-specialized execution and low-precision support.[^flashattention-2-2023][^flashattention-3-2024] These kernels most directly benefit long-sequence training and prompt prefill; one-token autoregressive decode is often constrained instead by KV-cache reads.[^flashattention-summary]

## Kernel evolution

The original FlashAttention fuses score computation, scaling, masking, softmax, dropout, and value aggregation so intermediate tensors mostly remain in registers or shared memory rather than making separate HBM round trips; its tiled recomputation supplies the shared exact-attention foundation for the later kernels.[^flashattention-2022]

FlashAttention-2 maintains an unnormalized output accumulator and applies the final softmax-normalizer division only after all key/value tiles have been processed; it stores row-wise logsumexp rather than separate maximum and exponential-sum statistics for backward recomputation. These exact-algorithm changes reduce non-matrix-multiply work, while entirely disallowed causal tiles are skipped.[^flashattention-2-2023]

Rather than making concurrency depend mainly on batch and head count, FlashAttention-2 assigns separate query-row tiles within each head to thread blocks. For batch $B$, heads $H$, query length $N$, and query-tile height $B_r$, this creates roughly $B\,H\,\lceil N/B_r\rceil$ blocks and can improve occupancy when long sequences make batch or head counts small. Its backward pass parallelizes column blocks and uses atomic additions for their shared query-gradient updates.[^flashattention-2-2023]

Within a thread block, its split-Q partition gives each warp independent query rows while sharing the key/value tile. This avoids the inter-warp reduction, shared-memory traffic, and synchronization associated with a split-K arrangement in which warps produce partial results for the same query rows.[^flashattention-2-2023]

On the authors’ A100 80GB SXM4 attention benchmarks—sequence lengths 512 to 16K, total batch tokens fixed at 16K, head dimensions 64 or 128, causal and non-causal cases—FlashAttention-2 was reported as 1.7–3.0× faster than FlashAttention, 1.3–2.5× faster than its Triton implementation, and 3–10× faster than PyTorch attention, reaching up to 230 TFLOPs/s (73% of theoretical peak). Their 8×A100 GPT-style 1.3B/2.7B training tests reported up to 1.3× over FlashAttention and 2.8× over the non-FlashAttention baseline, reaching 225 TFLOPs/s/GPU (72% model-FLOPs utilization). These are author-reported, configuration-specific results, not device-independent guarantees.[^flashattention-2-2023]

FlashAttention-3 is a Hopper-specific redesign. Producer warps use the Tensor Memory Accelerator (TMA) to fill a circular shared-memory buffer with Q/K/V tiles, while consumer warpgroups issue asynchronous WGMMA matrix multiplies; register allocation is shifted from producer to consumer warps. Its two-stage schedule pipelines the next $QK^T$ and current $PV$ GEMMs around softmax work from adjacent key tiles, and its pingpong schedule coordinates two warpgroups so one performs softmax while the other issues GEMMs.[^flashattention-3-2024]

The paper reports that a deeper three-stage pipeline performed worse in its implementation: compiler scheduling did not overlap the second WGMMA as intended, while the extra score/probability state increased register pressure and forced smaller tiles. Pipeline depth is therefore a hardware/compiler/profiled trade-off, not an unconditional optimization.[^flashattention-3-2024]

For FP8 forward attention, Hopper WGMMA layout constraints require a k-major V layout and a conversion between the first GEMM's FP32 accumulator layout and the second GEMM's FP8 operand layout. FlashAttention-3 uses an in-kernel V-tile transpose and register permutation rather than a separate global-memory transpose. It reduces quantization error with per-block scaling and an orthogonal, Hadamard-based incoherent transformation applied to Q and K before quantization; the transformation preserves their dot products before quantization.[^flashattention-3-2024]

On the authors' H100 80 GB SXM5 measurements (fixed 1830 MHz; CUDA 12.3, cuDNN 9.1.1.17, CUTLASS 3.5, FlashAttention-2 2.5.8, PyTorch 2.3.0), FP16 FlashAttention-3 reached up to 740 TFLOPs/s (75% of stated peak), with reported forward and backward speedups of 1.5–2.0× and 1.5–1.75× over FlashAttention-2, respectively. The focused non-causal FP16 ablation (batch 4, sequence length 8448, 16 heads, head dimension 128) measured 661 TFLOPs/s for both optimizations, versus 582 without GEMM–softmax pipelining and 570 without warp specialization.[^flashattention-3-2024]

The source's synthetic-outlier numerical test reports FP16 RMSE of $1.9\times10^{-4}$ for both FlashAttention-2 and -3 versus $3.2\times10^{-4}$ for its standard baseline; its FP8 FlashAttention-3 variant reported $9.1\times10^{-3}$ versus $2.4\times10^{-2}$ for per-tensor-scaled baseline attention. These are not end-to-end model-quality results. The paper also reports that its FP8 kernel lacked the FP16 persistent-kernel/load-balancing design, which partly explains weaker small-sequence and causal results relative to FP8 cuDNN.[^flashattention-3-2024]

## FlashInfer serving specialization

FlashInfer applies FlashAttention-2-style templates through Ada and FlashAttention-3-style templates on Hopper to serving workloads with non-contiguous caches and varying request lengths. It pairs sparse gathers with a block-sparse cache abstraction, JIT-inserted attention variants, and a runtime schedule that splits and reduces long-KV work while preserving fixed launch/workspace configuration for CUDA Graph replay.[^flashinfer-2025]

## Operational boundary

During training, reduced attention activations can enable longer sequences or larger batches, but total memory remains affected by model weights, other activations, gradients, optimizer state, and hardware-specific kernels.[^flashattention-summary]

During inference prefill, many prompt tokens attend together, making FlashAttention especially applicable. In token-by-token decode, the query length is usually one and reading the accumulated KV cache can dominate; paged KV caches, multi- or grouped-query attention, KV-cache quantization, and continuous batching address distinct serving bottlenecks.[^flashattention-summary]

FlashAttention makes full attention more efficient but does not remove its $O(N^2)$ sequence-length arithmetic. Very long contexts may still require restricted or sparse attention, chunking, distributed sequence techniques, retrieval, or architectures with different attention/state trade-offs.[^flashattention-summary]

## Relationships

- **Contextualized by:** [KV caching](kv-caching.md), which explains why prefill is compute-heavy and one-token decode is bounded by KV-cache reads.[^flashattention-summary]
- **Extends:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) with hardware-aware scheduling and data-movement refinements.[^flashattention-summary]
- **Specialized for serving by:** [FlashInfer attention engine](flashinfer-attention-engine.md), which adds block-sparse cache access, variant JIT, and variable-length scheduling.[^flashinfer-2025]
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which changes the retrieval formulation and state-growth behavior rather than optimizing exact full-attention kernels.[^flashattention-summary]
- **Complemented by:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), which reduces KV-cache traffic in one-token decoding by sharing K/V heads rather than changing the exact-attention kernel.[^mqa-summary]

[^flashattention-summary]: “FlashAttention overview” (Vietnamese summary), [raw source](../raw/FlashAttention.md), Sections 11–16 and 18. It is secondary evidence for the FlashAttention-2 and -3 claims; those primary papers have not been independently ingested here.

[^flashattention-2022]: Tri Dao et al., “FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness,” NeurIPS 2022, bundled [LaTeX source](../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex), Sections 1–4 and Appendix A.

[^flashattention-2-2023]: Tri Dao, “FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning,” arXiv:2307.08691v1, [bundled LaTeX source](../raw/arXiv-2307.08691v1/flash2.tex), abstract and Sections 2–5. The source package’s reported A100 and H100 benchmark plots were reviewed as corroborating attachments; this synthesis uses the paper’s stated aggregate results rather than extracting every plotted value.

[^flashattention-3-2024]: Jay Shah et al., “FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision,” arXiv:2407.08608v2, [bundled LaTeX source](../raw/arXiv-2407.08608v2/fa3_neurips2024.tex), abstract, Sections 1–5, and appendices. The bundled pipeline diagrams and 14 benchmark-plot PDFs were visually reviewed. Results are author-reported on an H100 SXM5 under the stated software, clock, shape, precision, and masking conditions.

[^mqa-summary]: “MQA overview” (Vietnamese summary), [raw source](../raw/MQA.md), Sections 3–7 and 13. This is secondary-source evidence; its cited primary MQA and GQA papers have not been independently ingested here.

[^flashinfer-2025]: Zihao Ye et al., “FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving,” arXiv:2501.01005v2, [bundled LaTeX source](../raw/arXiv-2501.01005v2/main.tex), Sections 3.2–3.3 and 6. Its templates build on FA2/FA3 according to the source; this is not a claim of universal performance equivalence.
