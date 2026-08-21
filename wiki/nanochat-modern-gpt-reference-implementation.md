---
type: Concept
title: nanochat modern GPT reference implementation
description: nanochat is an MIT-licensed PyTorch decoder-only language-model implementation combining RoPE, QK normalization, alternating sliding-window attention, value embeddings, explicit mixed precision, and KV-cached inference.
tags: [nanochat, decoder-only-transformer, pytorch, reference-implementation, sliding-window-attention, kv-cache]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T15:55:51Z }
sources:
  - id: nanochat-readme
    resource: ../raw/nanochat/README.md
    title: nanochat README
  - id: nanochat-gpt
    resource: ../raw/nanochat/nanochat/gpt.py
    title: nanochat GPT implementation
  - id: nanochat-flash
    resource: ../raw/nanochat/nanochat/flash_attention.py
    title: nanochat FlashAttention interface
  - id: nanochat-engine
    resource: ../raw/nanochat/nanochat/engine.py
    title: nanochat inference engine
  - id: nanochat-license
    resource: ../raw/nanochat/LICENSE
    title: nanochat MIT License
---

# nanochat modern GPT reference implementation

nanochat is a compact, hackable implementation of a current decoder-only language model rather than a faithful GPT-2 architecture clone. Its model combines pre-RMSNorm residual blocks with RoPE, QK normalization, ReLU² MLPs, untied input/output embeddings, alternating local/full causal attention, value embeddings, learned residual-path scalars, and a KV-cached inference engine.[^nanochat-readme][^nanochat-gpt]

## Decoder architecture

`GPTConfig` defaults to 12 layers, width 768, six query and KV heads, a 32,768-token vocabulary, and 2,048-token sequences. Depth is the project’s main complexity dial: the training script derives width as a rounded multiple of the target head dimension, then derives the head count from width.[^nanochat-gpt]

Each block applies parameter-free RMS normalization before causal attention and before a bias-free `D → 4D → D` ReLU² MLP. Attention projects Q, K, and V separately, applies half-split RoPE and RMS normalization to Q/K, and supports grouped-query attention when `n_kv_head < n_head`.[^nanochat-gpt]

The default `SSSL` window pattern tiles three short-window layers and one full-context layer; the final layer is always full-context. For a 2,048-token sequence, the code rounds the nominal quarter-context short window to a FlashAttention tile multiple, yielding 768 tokens. This changes attention work and KV reads but not allocated cache length.[^nanochat-gpt]

## Experimental residual and value paths

The implementation adds several nonstandard mechanisms whose benefits cannot be isolated from code inspection alone:

- alternating layers add a token-indexed value embedding through an input-dependent per-KV-head gate;
- each layer scales the current residual and blends the initial normalized token embedding through learned scalars;
- a learned “smear” gate can mix the previous token embedding into the current position;
- before the final norm, a learned scalar subtracts the residual captured halfway through the stack.[^nanochat-gpt]

Attention and MLP output projections initialize to zero, while layer-wise residual and input-blend scalars receive depth-dependent initial values. Input and output embedding weights are untied.[^nanochat-gpt]

## Precision, kernels, and inference

Weights used by custom linear layers remain FP32 for optimization and are cast to the activation dtype in each forward pass; embeddings are normally stored directly in the selected compute dtype. The model soft-caps FP32 logits to ±15 before cross-entropy or sampling.[^nanochat-gpt]

The attention wrapper dispatches to downloaded FlashAttention-3 kernels when compatible and otherwise uses PyTorch SDPA. The fallback preserves causal, sliding-window, GQA, and in-place cache semantics, but kernel choice and performance remain hardware-, dtype-, and environment-dependent.[^nanochat-flash]

The inference engine performs one batch-one prompt prefill, copies that prefilled cache across requested samples, then decodes all rows in parallel. It preallocates per-layer K/V tensors and tracks a previous embedding for the smear path. Its bounded calculator tool accepts arithmetic and a narrow `.count()` expression subset, injecting tool output as forced tokens that are distinguishable from sampled tokens.[^nanochat-engine]

## Evidence and operational limits

- The README’s GPT-2-grade cost and speed figures are author-reported results tied to particular commits, datasets, and 8×H100 runs; code inspection does not reproduce them.[^nanochat-readme]
- The model exposes GQA, but the pretraining builder currently sets KV heads equal to query heads, so the default training path uses MHA-shaped KV state.[^nanochat-gpt]
- The rotary cache is statically overallocated to ten times configured sequence length and asserts if exceeded; this is storage headroom, not evidence of trained long-context capability.[^nanochat-gpt]
- The project is MIT-licensed and supplied without warranty.[^nanochat-license]

## Relationships

- **Supersedes as project direction:** [nanoGPT GPT-2 reference implementation](nanogpt-gpt-2-reference-implementation.md), whose README directs users to nanochat.
- **Implements:** [Rotary position embedding](rotary-position-embedding.md), [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), and [KV caching](kv-caching.md).
- **Uses:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md), with an SDPA fallback.
- **Optimized by:** [nanochat distributed Muon–AdamW training](nanochat-distributed-muon-adamw-training.md).
- **Trained through:** [nanochat end-to-end language-model workflow](nanochat-end-to-end-language-model-workflow.md).

[^nanochat-readme]: Andrej Karpathy, [nanochat README](../raw/nanochat/README.md), project scope, reported speedrun, precision notes, and status.
[^nanochat-gpt]: Andrej Karpathy, [nanochat GPT implementation](../raw/nanochat/nanochat/gpt.py), configuration, attention, residual paths, initialization, precision, loss, and cache accounting.
[^nanochat-flash]: nanochat contributors, [FlashAttention interface](../raw/nanochat/nanochat/flash_attention.py), runtime dispatch and SDPA fallback.
[^nanochat-engine]: nanochat contributors, [inference engine](../raw/nanochat/nanochat/engine.py), KV-cache generation and calculator state machine.
[^nanochat-license]: Andrej Karpathy, [nanochat MIT License](../raw/nanochat/LICENSE).
