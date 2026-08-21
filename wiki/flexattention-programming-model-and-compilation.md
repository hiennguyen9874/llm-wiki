---
type: Concept
title: FlexAttention programming model and template lowering
description: FlexAttention exposes score_mod and mask_mod callables that express attention variants as elementwise score and mask logic and compiles them into hand-written Triton attention templates via torch.compile.
tags: [flexattention, attention, pytorch, torch-compile, triton, kernel-fusion, score-mod]
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
  - id: flexattention-intro
    resource: ../raw/2412.05496_FlexAttention/sections/01-intro.tex
    title: "FlexAttention introduction"
---

# FlexAttention programming model and template lowering

FlexAttention is a compiler-driven programming model that expresses most attention variants as two small PyTorch callables applied to the intermediate score matrix before softmax, then injects their compiled code into hand-written fused attention kernels. It preserves exact softmax attention semantics while allowing few-line variant definitions and their logical composition without a new hand-written kernel per variant.[^flexattention-2024][^flexattention-intro]

## Unified abstraction: score_mod and mask_mod

Standard attention computes `softmax(QK^T / sqrt(d_k)) V`. FlexAttention generalizes it as `softmax(mod(QK^T / sqrt(d_k))) V`, where `mod` is supplied by the user.[^flexattention-intro]

Two callables define the variant:

```python
def mask_mod(batch_idx: int, head_idx: int, q_idx: int, kv_idx: int) -> bool
def score_mod(score: T, batch_idx: int, head_idx: int, q_idx: int, kv_idx: int) -> T
```

- `mask_mod` returns whether a scalar is masked to `-inf`. For a score matrix `S in R^{B x H x M x N}`, it decides per `(b,h,q,kv)` position.[^flexattention-design]
- `score_mod` takes the scalar score and updates it based on position (e.g., scaling, bias, tanh). It operates on arbitrary scalar dtype `T` such as `bfloat16` or `float32`.[^flexattention-design]

Examples captured by the abstraction:

- **Causal:** `q_idx >= kv_idx` (batch/head independent).[^flexattention-design]
- **Sliding window:** `q_idx - kv_idx <= window`.[^flexattention-design]
- **Document mask:** `document_id[q_idx] == document_id[kv_idx]` for packed multi-document sequences.[^flexattention-design]
- **ALiBi bias:** `score + alibi_bias[h] * (q_idx - kv_idx)`, a head-dependent distance bias; other scalings or non-linear transforms are also expressible.[^flexattention-design]

`mask_mod` is semantically a special case of `score_mod`, but separating them matters: converting a mask to a score multiply adds per-element work, and the boolean mask provides sparsity information that the backend exploits to skip blocks entirely rather than computing and masking them.[^flexattention-design]

## Logical fusion and composability

Many deployed variants combine existing patterns (e.g., sliding window + ALiBi). Hand-writing each combination causes a combinatorial explosion of kernels.[^flexattention-intro]

FlexAttention supports logical fusion of masks via `and_mask` and `or_mask`, which take two `mask_mod` functions and return a new `mask_mod` applying the elementwise boolean operation. The result can be further composed. For example, PrefixLM (full bidirectional on prefix, causal on remainder) is built by composing a simple prefix mask with a causal mask via `or_mask` rather than writing conditional branches.[^flexattention-design]

Score modifications compose by nesting `score_mod` callables.[^flexattention-intro]

## Template-based lowering pipeline

The backend combines compiler flexibility with hand-tuned kernel performance:

1. **Capture:** TorchDynamo captures computation graphs of `score_mod` and `mask_mod`. These are typically lightweight pointwise ops suitable for fusion.[^flexattention-design]
2. **Template:** Three hand-written Triton templates cover forward, backward, and decoding. They already implement fused-attention optimizations: online softmax, GPU occupancy management, tiling/broadcasting, and grouped-query attention (GQA) support.[^flexattention-design]
3. **Code generation:** TorchInductor lowers the captured subgraphs into Triton code blocks for both forward and backward. At runtime the blocks are dynamically injected into the template's main loop. Compute buffers for inputs, outputs, and saved intermediates are pre-allocated.[^flexattention-design]
4. **Autograd:** Backward graph generation for `score_mod`/`mask_mod` is handled automatically via `torch.autograd` through the `torch.compile` lowering framework, which is natively compatible with PyTorch.[^flexattention-intro][^flexattention-design]

This separation lets common Triton optimizations (FlashAttention-style fusion and online softmax) remain in the template while variant-specific pointwise logic is generated, rather than requiring a general compiler to rediscover online-softmax and dual-GEMM fusion.[^flexattention-design]

## Evidence boundary

This concept summarizes the programming interface and lowering design from the bundled LaTeX source and its design section. It does not add runtime claims beyond the cited sections; kernel-performance, BlockMask/sparsity, and paged-attention mechanisms are covered in companion concepts.

## Relationships

- **Generalizes:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) by injecting arbitrary score/mask logic into a fused online-softmax template rather than supporting a fixed variant set.[^flexattention-2024]
- **Contrasts with:** [FlashInfer attention engine](flashinfer-attention-engine.md), which JIT-specializes CUDA/CUTLASS attention variants and schedules variable-length work; FlexAttention uses PyTorch/Triton templates with BlockMask sparsity.[^flexattention-design]
- **Uses:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) as the base computation whose score matrix is modified.[^flexattention-intro]
- **Extends:** [Rotary position embedding (RoPE)](rotary-position-embedding.md) and [ALiBi attention with linear biases](alibi-attention-with-linear-biases.md) contexts as examples of positional score modifications expressible via `score_mod`.[^flexattention-design]
- **Detailed by:** [FlexAttention BlockMask and paged attention](flexattention-block-sparsity-and-paged-attention.md) for sparsity exploitation; [FlexAttention evaluation and deployment limits](flexattention-evaluation-and-deployment-limits.md) for performance evidence.

[^flexattention-2024]: Juechu Dong et al., "FlexAttention: a Programming Model for Generating Optimized Attention Kernels," MLSys 2024, bundled [main.tex](../raw/2412.05496_FlexAttention/main.tex), abstract and Sections 1, 3.
[^flexattention-intro]: bundled [01-intro.tex](../raw/2412.05496_FlexAttention/sections/01-intro.tex), unified abstraction and Eq. 1.
[^flexattention-design]: bundled [03-design.tex](../raw/2412.05496_FlexAttention/sections/03-design.tex), Sections 3.1–3.3, Figures mask.pdf and lowering_path.pdf.
