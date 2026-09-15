---
type: Concept
title: FlexAttention Programmable Attention Kernels
description: Compiler-driven score_mod and mask_mod interface with BlockMask sparsity and fused paged-attention support at near-FlashAttention performance.
tags: [attention, flexattention, pytorch, triton, block-sparsity, paged-attention]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: flex-abstract
    resource: ../raw/2412.05496_FlexAttention/sections/00-abstract.tex
    title: FlexAttention abstract
  - id: flex-intro
    resource: ../raw/2412.05496_FlexAttention/sections/01-intro.tex
    title: FlexAttention introduction
  - id: flex-bg
    resource: ../raw/2412.05496_FlexAttention/sections/02-background.tex
    title: FlexAttention background
  - id: flex-design
    resource: ../raw/2412.05496_FlexAttention/sections/03-design.tex
    title: FlexAttention front-end and backend design
  - id: flex-eval
    resource: ../raw/2412.05496_FlexAttention/sections/06-evaluation.tex
    title: FlexAttention evaluation
  - id: flex-appendix
    resource: ../raw/2412.05496_FlexAttention/sections/aa-Appendix.tex
    title: FlexAttention appendix on Neighborhood Attention
---

FlexAttention is a compiler-driven programming model for generating optimized attention kernels from small idiomatic PyTorch callables instead of handwritten variant-specific kernels[^flex-abstract][^flex-intro].

It addresses the reported "software lottery" where researchers are limited to the handful of variants supported by fused kernels such as FlashAttention[^flex-abstract][^flex-intro].

## Unified abstraction

Many variants are expressed as a score modification before softmax[^flex-intro]:

```text
Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V
FlexAttention(Q,K,V) = softmax(mod(QK^T / sqrt(d_k))) V
```

Users supply two callables operating on position indices[^flex-design]:

```python
def mask_mod(batch_idx: int, head_idx: int, q_idx: int, kv_idx: int) -> bool
def score_mod(score: T, batch_idx: int, head_idx: int, q_idx: int, kv_idx: int) -> T
```

`mask_mod` sets selected score scalars to `-inf`; `score_mod` transforms a score scalar of arbitrary type such as `bfloat16` or `float32`[^flex-design].

Representative encodings[^flex-design]:

- Causal: `q_idx >= kv_idx`.
- Sliding window: `q_idx - kv_idx <= window`.
- Document masking: `document_id[q_idx] == document_id[kv_idx]`.
- ALiBi-style bias: `score + alibi_bias[h] * (q_idx - kv_idx)`; scaling and nonlinear transforms are also expressible.

`mask_mod` is semantically a special case of `score_mod`, but it is kept separate for two reasons: converting masks to score multiplications would apply expensive work to every scalar, and masks expose skippable computation used for sparsity acceleration[^flex-design].

## Composability

Mask variants compose with `and_mask` and `or_mask`, which combine two `mask_mod` functions elementwise and can themselves be further composed[^flex-design].

Example: PrefixLM, bidirectional over a prefix plus causal elsewhere, is built as a simple prefix mask composed with a causal mask via `or_mask` instead of complex branches[^flex-design].

This directly targets the combinatorial explosion from combining variants such as sliding-window plus ALiBi[^flex-intro][^flex-design].

## Template-based lowering

TorchDynamo captures the lightweight `score_mod` and `mask_mod` graphs; TorchInductor lowers them to Triton code blocks injected into three handwritten attention templates for forward, backward, and decoding[^flex-intro][^flex-design].

The templates retain established fused-attention optimizations including online softmax, GPU-occupancy management, partitioning and broadcasting, and grouped-query attention support; backward generation uses `torch.autograd`, with preallocated buffers for inputs, outputs, and saved intermediates[^flex-design].

The design rationale is that variants differ mainly in pointwise score work, so common computation can stay templatized while custom pointwise blocks are compiler-generated[^flex-design].

This is positioned against general compilers: attention needs fusion of two matmuls (`QK^T` and `SV`), attention-specific online softmax, and block sparsity, which torch.compile, TVM, and Mirage do not jointly deliver; Mirage is specifically noted as missing safe softmax and backward support[^flex-bg].

It is also positioned against FlashAttention and FlashMask: FlashAttention is IO-aware and avoids materializing the score matrix but supports only selected variants, while FlashMask adds column-wise sparsity but lacks score-modification flexibility and adds large overhead for complex masks[^flex-bg].

## BlockMask sparsity

Masking creates block-exploitable sparsity, for example about 50% from causal masking and more from sliding windows[^flex-design].

A naive per-scalar runtime check adds large overhead, while materializing a `B×H×Q_LEN×KV_LEN` mask contradicts FlashAttention's avoidance of the score matrix[^flex-design].

`BlockMask` instead records block-level sparsity with two tensors[^flex-design]:

- `kv_num_block` of shape `B×H×Num_Row`: number of unmasked blocks per row.
- `kv_indices` of shape `B×H×Num_Row×Num_Col`: indices of those blocks.

`create_block_mask` generates the structure from `mask_mod` with `torch.vmap`[^flex-intro][^flex-design].

Behavior[^flex-design]:

- Fully masked blocks are skipped without loading a large elementwise mask.
- Partially masked blocks still apply `mask_mod` elementwise to preserve semantics.
- Full blocks with no masked scalars skip `mask_mod` and apply only `score_mod`, reported as about a 15% improvement for patterns such as causal masks.
- Work per SM is sized by `kv_num_block`; `kv_indices` provide indirect access to the next block, supporting sliding-window, local-global, and custom sparse patterns without kernel edits.
- Tiling along `Q_LEN` plus KV-tile prefetch from HBM to SRAM hides access latency; removing per-scalar mask branches preserves pipelining.

Memory overhead scales as `O(ceil(Q_LEN/BS) × ceil(KV_LEN/BS))` with default block size 128, versus `O(M×N)` for the full score matrix[^flex-design].

## Paged attention and inference conversion

PagedAttention support is added without manually rewriting kernels by fusing page-table indirection with existing `BlockMask` indirection[^flex-design].

The logical-block indices in `kv_indices` are mapped to physical-block indices through the page table; `kv_num_blocks` is unchanged because paging does not change the unmasked-block count[^flex-design].

Because `mask_mod` and `score_mod` use logical positions, FlexAttention auto-generates converted forms taking `physical_kv_idx`[^flex-design]:

```python
def converted_mask_mod(batch_idx: int, head_idx: int, q_idx: int, physical_kv_idx: int) -> bool
def converted_score_mod(score: T, batch_idx: int, head_idx: int, q_idx: int, physical_kv_idx: int) -> T
```

A vector mapping physical blocks to logical blocks, maintained at `O(1)` cost during page-table updates, reconstructs the logical token index from physical block index plus offset before calling the user function[^flex-design].

Single-token iterative decoding needs an additional offset for the number of already-processed query tokens; a decorator converts user `mask_mod` and `score_mod` to offset-aware inference forms, illustrated for causal mask training versus inference[^flex-design].

The paper scopes paging to GPU-resident KV cache and leaves host-disk swapping as future work[^flex-design].

## Evaluated variants and baselines

Evaluation covers noop, causal, ALiBi, sliding-window, prefixLM, soft-cap/tanh, document masking for variable lengths, and Neighborhood Attention[^flex-eval][^flex-appendix].

Reported baseline support[^flex-eval]:

| Variant | FAv2 | FAv3 | SDPA cuDNN / mem-efficient | FlexAttention |
|---|---|---|---|---|
| noop, causal | native | native | native | native |
| alibi_bias | native | unsupported | itemized mask | native |
| sliding_win | native | native | itemized mask | native |
| prefix_lm | unsupported | unsupported | itemized mask | native |
| soft_cap | native | unsupported | unsupported | native |
| variable lengths | native | native | jagged tensors | native via document mask |
| neighbor attention | unsupported | unsupported | unsupported | native |

Baselines are FlashAttention-v2, FlashAttention-v3 at commit `c1d146c`, FlashDecoding/FAKV for inference, and PyTorch SDPA with math, memory-efficient, FAv2, and cuDNN v9.1.1 paths; end-to-end tests replace SDPA with FlexAttention in `gpt-fast` and `torchtune`[^flex-eval].

Hardware and config: NVIDIA H100 power-capped at 650W and 2.4TB/s memory bandwidth, plus A100 and A6000; kernel tests use 256MiB KV, head dimension 64, and `bfloat16`[^flex-eval].

## Reported performance

Training, causal mask over 1K–64K QKV with and without GQA: 1.00x–1.22x forward and 0.86x–1.05x backward versus FAv2[^flex-eval].

Across seven variants at 16K QKV: 0.68x–1.43x versus FAv2 where FAv2 supports the variant, and 5.49x–8.00x versus SDPA itemized-mask kernels where native support is absent, by computing masks from `mask_mod` instead of realizing and loading itemized masks[^flex-eval].

Decoding with one query token over 1K–132K KV: 0.93x–1.45x versus FlashDecoding/FAKV, with one outlier where FlexAttention is 5.37x faster for GQA plus ALiBi because the baseline falls back to an unoptimized path; this is presented as a "software lottery" example[^flex-eval].

No additional numeric error is reported relative to baselines under RMSE against an fp64 reference for bf16/fp16 outputs[^flex-eval].

End-to-end[^flex-eval]:

- `torchtune` fine-tuning of Llama3-8B on Alpaca: over 2.4x training throughput; SDPA needs a `B×N×N` boolean document mask whose access cost grows quadratically and loses about 25% throughput from 2K to 8K, while FlexAttention uses `BlockMask` plus a `B×N` document-ID tensor.
- `gpt-fast` inference: 1.22x–2.04x on Llama3.1-8B and 0.99x–1.66x on Llama3.1-70B versus SDPA, increasing with context length as attention dominates; 2.04x at 16K context is highlighted in the introduction[^flex-intro][^flex-eval].

Paged attention, batch 32 with head dimension 64 and 16 heads: under 1% average runtime overhead versus non-paged FlexAttention, compared with 20–26% attention-kernel overhead cited from vLLM; page sizes 16–256 show no significant performance effect, and paged FlexAttention is reported faster than non-paged FlashAttention-v2 at large sequence lengths[^flex-eval].

Neighborhood Attention for 2D images is implemented in under 10 lines each for tiled and Morton/Hilbert-curve mappings to improve block sparsity; the appendix reports the corresponding mask-sparsity and speed behavior[^flex-appendix].

## Coverage limits

- All `.tex` sources were read; `graphs/*.pdf` and `graphs/*.png` illustrations and performance charts were not visually rendered, so quantitative claims here follow the paper body, table, and captions rather than independent chart measurement.
- Reported numbers inherit the paper's hardware caps, FAv3 commit, cuDNN version, and bf16/head-dimension-64 test configuration.
- Paged-attention evidence is GPU-resident only; host-disk swapping was explicitly out of scope.
- Downstream `flex_attention` backend maturity in serving stacks is not established by this paper alone.

## Relationships

- Used by [SGLang Attention Backends](sglang-attention-backends.md) — SGLang exposes a `flex_attention` backend option alongside FlashInfer, FA3/FA4, Triton, and MLA paths.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — companion vLLM backend-selection reference for comparing where programmable attention such as FlexAttention fits against FlashAttention and MLA/sparse backends.

[^flex-abstract]: FlexAttention abstract — `../raw/2412.05496_FlexAttention/sections/00-abstract.tex`.
[^flex-intro]: FlexAttention introduction — `../raw/2412.05496_FlexAttention/sections/01-intro.tex`.
[^flex-bg]: FlexAttention background — `../raw/2412.05496_FlexAttention/sections/02-background.tex`.
[^flex-design]: FlexAttention front-end and backend design — `../raw/2412.05496_FlexAttention/sections/03-design.tex`.
[^flex-eval]: FlexAttention evaluation — `../raw/2412.05496_FlexAttention/sections/06-evaluation.tex`.
[^flex-appendix]: FlexAttention appendix on Neighborhood Attention — `../raw/2412.05496_FlexAttention/sections/aa-Appendix.tex`.
