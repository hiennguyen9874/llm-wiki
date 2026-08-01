---
type: Concept
title: OpenAI GPT PyTorch reference implementation
description: The supplied Hugging Face module implements configurable OpenAI GPT decoder blocks and base, language-model, multiple-choice, and sequence-classification wrappers.
tags: [openai-gpt, pytorch, reference-implementation, causal-language-modeling, transformer]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T05:33:53Z }
sources:
  - id: huggingface-openai-gpt-pytorch
    resource: ../raw/gpt-source.py
    title: PyTorch OpenAI GPT model
---

# OpenAI GPT PyTorch reference implementation

The supplied Hugging Face module implements a configurable OpenAI GPT decoder stack with learned token and position embeddings, causal multi-head self-attention, four-times-width MLPs, and post-residual layer normalization. It provides base-model, language-model, multiple-choice, and sequence-classification wrappers; this is library-code evidence, not a versioned reproduction or an experimental evaluation.[^huggingface-openai-gpt-pytorch]

## Decoder blocks

- The model sums token embeddings, learned position embeddings, and optional token-type embeddings, then applies embedding dropout.
- Each block projects a joint query/key/value tensor, splits it into heads, scales query–key scores by the square root of head width, applies a lower-triangular causal mask and any supplied attention mask before softmax, then projects and drops out the combined attention output.
- The MLP expands from model width to four times that width, applies the configured activation, projects back to model width, and applies dropout.
- Each block uses post-residual normalization: layer normalization follows the attention residual addition and again follows the MLP residual addition.[^huggingface-openai-gpt-pytorch]

## Inputs and task wrappers

The base model accepts either token IDs or input embeddings, but rejects receiving both. A provided two-dimensional attention mask is expanded for head-wise broadcasting and converted to an additive pre-softmax mask. It can return the final hidden states, and optionally all layer hidden states and attention weights.[^huggingface-openai-gpt-pytorch]

The language-model wrapper applies a vocabulary projection whose weight is declared tied to the input token embeddings. The multiple-choice wrapper combines language-model logits with a configurable sequence summary, defaulting to the final token, while the sequence-classification wrapper scores each token and pools the final non-padding token when a padding ID is configured. Both task wrappers select losses from their provided labels and configuration.[^huggingface-openai-gpt-pytorch]

## Generation boundary

`prepare_inputs_for_generation` forwards the full input-ID sequence and uninitialized keyword arguments. This module defines no past-key/value input or cache update path, so it does not itself evidence incremental cached decoding.[^huggingface-openai-gpt-pytorch]

## Relationships

- **Implements:** [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md)'s decoder-only architecture in a configurable PyTorch module.
- **Uses:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md)'s scaled causal attention pattern.
- **Contrasts with:** [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md), whose reported design uses pre-layer normalization rather than this module's post-residual normalization.[^huggingface-openai-gpt-pytorch]

[^huggingface-openai-gpt-pytorch]: Hugging Face `modeling_openai.py`, “PyTorch OpenAI GPT model,” bundled [source](../raw/gpt-source.py). The supplied file contains no repository revision, release version, or benchmark evidence.
