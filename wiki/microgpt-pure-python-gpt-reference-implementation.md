---
type: Concept
title: microgpt pure-Python GPT reference implementation
description: microgpt is a dependency-free, character-level GPT training and inference script that makes scalar autograd, causal attention state, Adam updates, and temperature sampling explicit.
tags: [microgpt, gpt, decoder-only-transformer, autograd, causal-language-modeling, reference-implementation, python]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T15:41:31Z }
sources:
  - id: microgpt-code
    resource: ../raw/microgpt.py
    title: microgpt.py
---

# microgpt pure-Python GPT reference implementation

`microgpt.py` is a single-file, standard-library reference that trains and samples a small character-level causal GPT over a shuffled list of names. It exposes each major learning-system step directly: a scalar reverse-mode autograd graph, token and position embeddings, one causal multi-head-attention/MLP decoder layer, next-character negative log likelihood, hand-written Adam, and temperature-based autoregressive sampling.[^microgpt-code]

## Data and tokenization boundary

When `input.txt` is absent from the working directory, the script downloads the `makemore` names dataset; otherwise it reads non-empty lines from that local file. It creates a character vocabulary from the loaded documents, reserves one additional ID as both beginning- and end-of-sequence (`BOS`) marker, and converts each training name to `BOS + characters + BOS`.[^microgpt-code]

This is a character tokenizer whose vocabulary and parameter count depend on the input file. The code fixes Python's `random` seed to 42 before shuffling documents and initializing parameters, but its external download path and working-directory-relative `input.txt` remain environmental dependencies.[^microgpt-code]

## Explicit model mechanics

The default configuration has one layer, 16-dimensional embeddings, four heads of width four, and a maximum context length of 16. Its state dictionary contains learned token embeddings, learned position embeddings, an untied output projection, and per-layer Q/K/V/output and two-layer MLP matrices.[^microgpt-code]

For each token position, the model:

1. adds token and position embeddings, then applies RMSNorm;
2. creates Q, K, and V projections; appends the new K/V vectors to that layer's accumulated prefix state; and applies scaled dot-product attention only over that accumulated state;
3. projects and adds the attention residual; then applies RMSNorm, a `D → 4D → D` ReLU MLP, and its residual;
4. projects the final vector to vocabulary logits.[^microgpt-code]

The sequential K/V accumulation enforces causal access without constructing an explicit mask: at position `t`, the state contains keys and values only through `t`. The source comments characterize the design as GPT-2-like with deliberate differences: RMSNorm instead of LayerNorm, no biases, and ReLU instead of GeLU.[^microgpt-code]

## Training and sampling

Each of 1,000 default steps uses one document cyclically, predicts every next token in its truncated sequence, averages per-position negative log probabilities, calls `loss.backward()`, and applies Adam with fixed beta values and linearly decayed learning rate. `Value.backward()` topologically traverses the scalar computation graph and accumulates local derivatives in its child nodes; the optimizer resets each parameter gradient after its update.[^microgpt-code]

For inference, the script begins with `BOS`, preserves per-layer K/V prefixes across generated positions, divides logits by a default temperature of 0.5, samples with `random.choices`, and stops on the next `BOS` or after `block_size` positions.[^microgpt-code]

## Scope limits

- The source is a pedagogical algorithm, not an efficient implementation: tensors, matrix operations, and autograd nodes are represented with nested Python lists and scalar `Value` objects.[^microgpt-code]
- It processes training positions sequentially to make causal state visible; it does not provide batched tensor execution, explicit causal masks, distributed training, checkpointing, or evaluation.
- Its K/V lists demonstrate the state retained during a single sequential pass or generated sample, but do not constitute a production serving cache or its memory-management strategy.[^microgpt-code]

## Relationships

- **Implements:** the component sequence summarized in [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md), with source-specific normalization and activation choices.
- **Operationalizes:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md) through shifted next-token loss, teacher-forced training positions, and temperature sampling.
- **Demonstrates a minimal form of:** [KV caching](kv-caching.md): each new position appends K/V state and attends to the retained prefix, without production cache management.
- **Contrasts with:** [minGPT educational GPT reference implementation](mingpt-educational-gpt-reference-implementation.md), which is a PyTorch implementation with GPT-2 BPE and optional checkpoint import rather than dependency-free scalar autodifferentiation.

[^microgpt-code]: Karpathy, [microgpt.py](../raw/microgpt.py), module documentation and complete implementation: dataset loading, `Value`, model functions, training loop, and inference loop.
