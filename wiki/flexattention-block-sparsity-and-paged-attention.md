---
type: Concept
title: FlexAttention BlockMask and paged attention
description: FlexAttention exploits attention sparsity with a precomputed BlockMask over 128x128 score blocks, distinguishes full and partial blocks, and reuses its indirect index for paged KV-cache support and inference offset handling.
tags: [flexattention, blockmask, sparsity, pagedattention, kv-cache, triton]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T12:00:00Z }
sources:
  - id: flexattention-2024
    resource: ../raw/2412.05496_FlexAttention/main.tex
    title: "FlexAttention: a Programming Model for Generating Optimized Attention Kernels"
  - id: flexattention-design
    resource: ../raw/2412.05496_FlexAttention/sections/03-design.tex
    title: "FlexAttention design sections"
---

# FlexAttention BlockMask and paged attention

FlexAttention exploits mask-induced sparsity without materializing an `B x H x Q_LEN x KV_LEN` mask. It precomputes a block-level `BlockMask` that records which `128 x 128` score blocks are fully masked, skips those blocks, and reuses the same indirect index to support paged KV-cache attention and causal-offset conversion for decoding.[^flexattention-design]

## BlockMask data structure

The score matrix is partitioned along `Q_LEN` and `KV_LEN` into blocks (default `BS=128`). `BlockMask` stores:[^flexattention-design]

- `kv_num_blocks: B x H x Num_Row` — number of non-masked blocks per query-block row.
- `kv_indices: B x H x Num_Row x Num_Col` — column indices of those non-masked blocks (where `Num_Row = ceil(Q_LEN/BS)`, `Num_Col = ceil(KV_LEN/BS)`).

A block is classified as non-computed only if every scalar in it is masked to `-inf`. Creation is automated via `create_block_mask` using `torch.vmap` over the user-defined `mask_mod`, executed at compile time to remove runtime mask-construction overhead.[^flexattention-design]

Memory scales as `O(ceil(Q_LEN/BS) * ceil(KV_LEN/BS))` for the auxiliary tensors, versus `O(M x N)` for a full score or elementwise mask — a key difference from the FlashAttention goal of avoiding full score materialization.[^flexattention-design]

## Full versus partial blocks

To avoid applying `mask_mod` elementwise everywhere, blocks are split:[^flexattention-design]

- **Full blocks:** no scalar is masked; only `score_mod` is applied elementwise, `mask_mod` is skipped.
- **Partial blocks:** some scalars are masked; both `mask_mod` (elementwise) and `score_mod` are applied.

This yields a reported ~15% speedup for common patterns such as causal masks. The paper's sliding-window illustration shows `score_mod` (e.g., relative-position bias) applied to both full and partial blocks while the sliding-window `mask_mod` is applied only to partial blocks.[^flexattention-design]

## BlockMask-guided execution

FlexAttention adjusts per-SM workload by `kv_num_blocks` and iterates via `kv_indices` indirect access. Because indices need not be contiguous, the same mechanism can skip arbitrary sparse patterns (sliding window, local-global, custom) without kernel rewrites and without the manual start/end index bookkeeping used in hand-written FlashAttention variant kernels.[^flexattention-design]

Tiling along `Q_LEN` parallelizes across SMs. Each SM iterates along `KV_LEN` over its assigned row of blocks. Removing per-scalar mask branches enables a prefetch pipeline: while one KV tile's scores are computed in SRAM, the next KV tile is prefetched from HBM to SRAM, hiding latency.[^flexattention-design]

Naive per-scalar sparsity checks would add large runtime overhead; precomputing the elementwise `B x H x Q_LEN x KV_LEN` mask would add large memory overhead — the two extremes BlockMask avoids.[^flexattention-design]

## Paged attention via BlockMask conversion

PagedAttention stores a logical `B x Max_len x D` KV cache compactly as a physical `1 x Max_tokens x D` cache with a `B x Max_len` page table mapping `(batch, logical_kv_idx) -> physical_kv_idx`, reducing fragmentation and enabling cross-sequence block sharing. Traditional paged support requires manually rewriting the attention kernel for indirect loads and is tightly coupled to a specific mask.[^flexattention-design]

FlexAttention reuses BlockMask's indirect access:

1. **Index fusion:** The logical `kv_indices` are remapped through the page table to physical block indices. `kv_num_blocks` is unchanged because paging does not change which logical blocks are masked.[^flexattention-design]
2. **Position conversion:** User `mask_mod`/`score_mod` are defined on logical positions, but the kernel now operates on physical KV indices. A physical-to-logical map is maintained (O(1) overhead on page-table updates): from `physical_kv_idx` compute `physical_block_idx + offset`, look up `logical_block_idx`, reconstruct `logical_kv_idx`, and call the original mod with the logical index. Manual rewriting for each variant and each composition is thus avoided.[^flexattention-design]

The scope in the paper is GPU-resident physical KV cache; host-disk swapping is left as future work.[^flexattention-design]

## Inference offset handling

During autoregressive decoding, `mask_mod`/`score_mod` defined with training-index semantics (e.g., `q_idx >= kv_idx` for causal) must account for how many query tokens have already been processed (offset). FlexAttention provides a decorator that takes a user `mask_mod` and an offset and produces an inference variant that consumes the offset, illustrated for the causal-mask training-vs-inference difference.[^flexattention-design]

## Neighborhood Attention illustration

The appendix demonstrates Neighborhood Attention (NA) — each pixel attends to spatial neighbors, where the 1D-expanded mask is highly irregular. Naive NA has low block sparsity; 2D-tiled and Morton/Hilbert-curve reorderings improve it. FlexAttention implements these reorderings in <10 lines of PyTorch mask logic and captures the sparsity via BlockMask rather than hand-tuning a kernel.[^flexattention-2024]

## Relationships

- **Depends on:** [FlexAttention programming model and template lowering](flexattention-programming-model-and-compilation.md) for the `mask_mod`/`score_mod` definitions whose sparsity is exploited.[^flexattention-design]
- **Optimizes:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) lineage with sparsity-aware block skipping while retaining online tiling benefits.[^flexattention-design]
- **Implements a cache representation compatible with:** [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md), merging its page-table indirection with BlockMask's block indirection without kernel rewrites.[^flexattention-design]
- **Uses:** [KV caching](kv-caching.md) as the inference state that is paged and indexed via BlockMask.[^flexattention-design]
- **Evaluated by:** [FlexAttention evaluation and deployment limits](flexattention-evaluation-and-deployment-limits.md).

[^flexattention-2024]: Juechu Dong et al., "FlexAttention: a Programming Model ...," bundled [main.tex](../raw/2412.05496_FlexAttention/main.tex) and [aa-Appendix.tex](../raw/2412.05496_FlexAttention/sections/aa-Appendix.tex).
[^flexattention-design]: bundled [03-design.tex](../raw/2412.05496_FlexAttention/sections/03-design.tex), Sections 3.4–4.1, Figures BlockMask_kv.pdf, AssignBlockMasktoSM.pdf, paged_attention.pdf, offset.pdf.
