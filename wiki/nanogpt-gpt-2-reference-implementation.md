---
type: Concept
title: nanoGPT GPT-2 reference implementation
description: nanoGPT is a compact, now-deprecated PyTorch GPT-2-style implementation with tied embeddings, optional PyTorch SDPA, GPT-2 checkpoint import, and uncached autoregressive generation.
tags: [nanogpt, gpt-2, decoder-only-transformer, pytorch, reference-implementation]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-21T15:55:51Z }
sources:
  - id: nanogpt-readme
    resource: ../raw/nanoGPT/README.md
    title: nanoGPT README
  - id: nanogpt-model
    resource: ../raw/nanoGPT/model.py
    title: nanoGPT model implementation
  - id: nanogpt-license
    resource: ../raw/nanoGPT/LICENSE
    title: nanoGPT MIT License
---

# nanoGPT GPT-2 reference implementation

nanoGPT is a small PyTorch implementation for training or fine-tuning medium-sized GPTs. The source now labels the repository old and deprecated (November 2025) and directs new users to nanochat, so this page records it as an inspectable GPT-2-era reference rather than a current training stack.[^nanogpt-readme]

## Model shape and attention path

The default `GPTConfig` is GPT-2-small-shaped: 12 layers, 12 heads, width 768, a 1,024-token learned absolute-position table, and a 50,304-token vocabulary padded from GPT-2’s 50,257 for efficiency.[^nanogpt-model] The model uses token and position embeddings, embedding dropout, pre-LayerNorm residual blocks, a final LayerNorm, and a vocabulary head whose weight is tied to the token embedding.[^nanogpt-model]

Each block is LayerNorm → causal multi-head attention → residual addition, followed by LayerNorm → `D → 4D → D` GELU MLP → residual addition. Q, K, and V come from one projection and the attention module uses PyTorch `scaled_dot_product_attention` when available; otherwise it applies an explicit lower-triangular mask before softmax.[^nanogpt-model] The source’s comment calls the former “Flash Attention,” but the code’s actual dispatch condition is only PyTorch SDPA availability, so the precise kernel remains runtime- and hardware-dependent.[^nanogpt-model]

Linear and embedding weights initialize with normal standard deviation 0.02; residual projection weights are reinitialized at $0.02/\sqrt{2L}$ for $L$ layers.[^nanogpt-model] `configure_optimizers()` applies weight decay to parameters with two or more dimensions, excludes scalar/vector parameters such as biases and normalization weights, and selects fused AdamW only when it is supported on CUDA.[^nanogpt-model]

## GPT-2 import and generation

`GPT.from_pretrained()` supports GPT-2, medium, large, and XL. It constructs the matching 50,257-vocabulary, 1,024-context, bias-enabled configuration, imports Hugging Face `GPT2LMHeadModel` weights, and transposes the four Conv1D-layout attention/MLP matrices for `nn.Linear`.[^nanogpt-model]

With targets, `forward()` returns logits at every position and next-token cross-entropy, ignoring target ID `-1`. Without targets, it projects only the final hidden state as an inference optimization.[^nanogpt-model] `generate()` crops an overlong prefix to `block_size`, then repeatedly recomputes that active prefix, applies temperature and optional top-k filtering, samples one token, and appends it.[^nanogpt-model]

## Operational limits

- The generation path stores no per-layer key/value cache, so each output token recomputes its active context; see [KV caching](kv-caching.md) for the omitted optimization.[^nanogpt-model]
- `crop_block_size()` only reduces a model’s context table; it is not a method for extending context beyond the loaded configuration.[^nanogpt-model]
- The MIT license permits reuse but disclaims warranty.[^nanogpt-license]

## Relationships

- **Rewrites:** [minGPT educational GPT reference implementation](mingpt-educational-gpt-reference-implementation.md), as stated by nanoGPT’s README.
- **Superseded as project direction by:** [nanochat modern GPT reference implementation](nanochat-modern-gpt-reference-implementation.md); nanoGPT’s README directs new users to nanochat while this historical implementation remains available.
- **Implements:** the dense baseline in [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md).
- **Operationalizes:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md).
- **Lacks:** [KV caching](kv-caching.md)’s retained decode state.

[^nanogpt-readme]: Karpathy, [nanoGPT README](../raw/nanoGPT/README.md), repository description and November 2025 status notice.
[^nanogpt-model]: Karpathy, [nanoGPT model implementation](../raw/nanoGPT/model.py), `GPTConfig`, attention, `GPT`, checkpoint import, optimizer setup, and generation.
[^nanogpt-license]: Karpathy, [nanoGPT MIT License](../raw/nanoGPT/LICENSE).
