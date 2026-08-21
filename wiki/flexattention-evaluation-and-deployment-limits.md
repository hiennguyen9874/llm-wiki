---
type: Concept
title: FlexAttention evaluation and deployment limits
description: Author H100/A100 benchmarks report near-parity to FlashAttention for supported variants and large gains for unsupported variants, with 2x end-to-end speedups in gpt-fast/torchtune and <1% paged-attention overhead under tested configs.
tags: [flexattention, evaluation, flashattention, gqa, pagedattention, gpt-fast, torchtune]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T12:00:00Z }
sources:
  - id: flexattention-2024
    resource: ../raw/2412.05496_FlexAttention/main.tex
    title: "FlexAttention: a Programming Model for Generating Optimized Attention Kernels"
  - id: flexattention-eval
    resource: ../raw/2412.05496_FlexAttention/sections/06-evaluation.tex
    title: "FlexAttention evaluation"
---

# FlexAttention evaluation and deployment limits

On the authors' H100/A100/A6000 benchmark grid, FlexAttention matches hand-written FlashAttention kernels on natively supported variants and substantially outperforms PyTorch SDPA with itemized or boolean masks on unsupported variants, while remaining within the paper's tested model, sequence-length, and dtype scope. Numeric error is reported as not increased relative to baselines in their RMSE comparison.[^flexattention-eval]

## Setup

Seven variants were tested as MHA and GQA: `noop`, `causal`, `alibi_bias`, `sliding_window`, `prefixLM`, `soft_cap` (tanh), and `document_mask` for packed variable-length sequences, plus Neighborhood Attention in the appendix. Baselines: FlashAttention-v2 (FAv2), experimental FlashAttention-v3 (`c1d146c`), FlashDecoding (FAKV) for decoding, and PyTorch SDPA with `cuDNN`/`mem_efficient` and `math` backends (the latter with itemized masks or jagged tensors where applicable). End-to-end workloads replaced SDPA with FlexAttention in `gpt-fast` and `torchtune` on LLaMA 3/3.1 families.[^flexattention-eval]

Benchmark grid for micro-kernels: KV size fixed at 256 MiB, head dim 64, bfloat16, Q/KV lengths 1K–64K (training) and 1K–132K (decoding, query=1). End-to-end repeats use power-capped H100 (650 W, 2.4 TB/s) and A100 (330 W) as noted. A support table records that, among the baselines, only FlexAttention natively handles `alibi_bias`, `prefixLM`/`sliding_window` combinations, `soft_cap`, `document_mask`, and `neighbor attention` without itemized masks or missing support.[^flexattention-eval]

## Kernel performance

- **Training (causal, varying length):** Forward 1.00x–1.22x vs FAv2 across lengths; backward 0.86x–1.05x vs FAv2.[^flexattention-eval]
- **Training (variant sweep, 16K QKV):** 0.68x–1.43x vs FAv2 where FAv2 natively supports the variant; 5.49x–8.00x vs SDPA with itemized masks where the variant lacks native FlashAttention support (FlexAttention avoids realizing and loading the full mask by evaluating `mask_mod` at runtime plus BlockMask skipping).[^flexattention-eval]
- **Decoding (query=1, varying KV 1K–132K):** 0.93x–1.45x vs FAKV across tested variants, with one outlier of 5.37x vs FAKV for GQA + ALiBi — attributed to FAKV's fallback lacking GQA+ALiBi tuning (an instance of the "software lottery" the paper highlights).[^flexattention-eval]
- **Numerics:** Reported RMSE of bf16/fp16 outputs vs fp64 golden shows no additional error versus baselines in their figure; the paper does not claim reduced error.[^flexattention-eval]

## End-to-end workloads

- **torchtune training (LLaMA 3-8B, Alpaca, packed jagged sequences with document mask):** SDPA used a precomputed `B x N x N` boolean mask; FlexAttention used `BlockMask` plus a `B x N` document-ID tensor. The boolean-mask cost made SDPA throughput drop ~25% from 2K to 8K sequence length in their plot, while FlexAttention scaled and yielded >2.4x overall training throughput gain in the reported config (throughput, not kernel-only FLOPS).[^flexattention-eval]
- **gpt-fast inference (LLaMA 3.1-8B/70B):** Replacing SDPA with FlexAttention while retaining `torch.compile`, CUDA Graphs, parameter freezing, and kernel fusion gave 1.22x–2.04x on 8B and 0.99x–1.66x on 70B in their graphs, with speedup growing as context length (and thus attention dominance) increases. Benchmark used bfloat16; 16K context cited for the 2.04x headline.[^flexattention-eval]

## Paged attention

Varying sequence length (batch 32, head dim 64, 16 heads) the authors report <1% average overhead for paged FlexAttention vs non-paged FlexAttention, substantially below the 20–26% overhead they cite from vLLM's paged implementation — attributed to fused indirect access without kernel rewrites. At large sequence lengths, paged FlexAttention even outperformed non-paged FAv2 in their latency plot. Page-size sweep 16–256 showed no significant performance effect under the tested GPU-resident cache (no host-disk swapping, which the paper scopes out).[^flexattention-eval]

## Neighborhood Attention appendix

For NA, reorderings (2D-tiled, Morton/Hilbert) improve block sparsity substantially over naive NA. FlexAttention's <10-line mask implementations captured that sparsity via BlockMask and showed corresponding speedups in the appendix figures; the paper positions this as programmability evidence rather than a claim of optimal image-attention quality.[^flexattention-2024]

## Limits and caveats

- **Hardware/software scope:** Primary kernel figures are H100 bfloat16 with head dim 64 and specific tile/block choices (BS=128); A100/A6000 results are referenced but not detailed in the excerpted evaluation section. Generalization to other dtypes, head dims, or GPU generations is not established by this source alone.[^flexattention-eval]
- **Baseline versions:** FAv3 compared is experimental commit `c1d146c`; SDPA behavior depends on backend (`cuDNN 9.1.1`, `mem_efficient`). Support gaps (e.g., soft-cap, prefixLM, neighbor attention) reflect those versions.[^flexattention-eval]
- **Workload dependence:** End-to-end gains depend on attention's fraction of runtime (sequence length, model size, batching) and on `torchtune`/`gpt-fast` integration choices; the paper explicitly notes composition via BlockMask rather than exhaustive variant-by-variant tuning.[^flexattention-eval]
- **Evaluation provenance:** All measurements are author-run. Cross-validation against independent benchmarks (e.g., FlashInfer's AttentionGym comparison cited in raw, where FlashInfer reports higher TFLOPS/s than FlexAttention at longer lengths) is not reconciled in this source; that comparison belongs to the FlashInfer evaluation concept.[^flexattention-2024]

## Relationships

- **Evaluates:** [FlexAttention programming model and template lowering](flexattention-programming-model-and-compilation.md) and [FlexAttention BlockMask and paged attention](flexattention-block-sparsity-and-paged-attention.md).[^flexattention-eval]
- **Compares with:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) and [FlashAttention implementation evolution](flashattention-implementation-evolution.md) (FAv2/FAv3/FAKV), [FlashInfer attention engine](flashinfer-attention-engine.md) (host planning / TMA trade-offs noted elsewhere), and [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md).[^flexattention-eval]
- **Uses workloads from:** [KV caching](kv-caching.md) (decoding) and document-packing patterns referenced in [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) for GQA coverage.[^flexattention-eval]

[^flexattention-2024]: Juechu Dong et al., "FlexAttention ...," bundled [main.tex](../raw/2412.05496_FlexAttention/main.tex), abstract, intro, and [aa-Appendix.tex](../raw/2412.05496_FlexAttention/sections/aa-Appendix.tex) for NA case.
[^flexattention-eval]: bundled [06-evaluation.tex](../raw/2412.05496_FlexAttention/sections/06-evaluation.tex), Table 1, Figures causal_training_H100, masks_training_H100, decoding, errors, torchtune, gpt-fast, PagedSeqlen/PageSize, and Appendix Fig. NATTEN.
