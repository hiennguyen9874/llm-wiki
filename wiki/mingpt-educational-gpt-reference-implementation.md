---
type: Concept
title: minGPT educational GPT reference implementation
description: minGPT is a semi-archived MIT-licensed PyTorch reference that exposes a GPT-2-style decoder-only Transformer, compatible GPT-2 BPE, checkpoint import, and uncached autoregressive sampling in a small, readable codebase.
tags: [mingpt, gpt, gpt-2, decoder-only-transformer, pytorch, reference-implementation]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-13T00:00:00Z }
sources:
  - id: mingpt-readme
    resource: ../raw/minGPT/README.md
    title: minGPT README
  - id: mingpt-model
    resource: ../raw/minGPT/mingpt/model.py
    title: minGPT GPT model implementation
  - id: mingpt-bpe
    resource: ../raw/minGPT/mingpt/bpe.py
    title: minGPT GPT-2 BPE implementation
  - id: mingpt-huggingface-test
    resource: ../raw/minGPT/tests/test_huggingface_import.py
    title: minGPT Hugging Face import test
---

# minGPT educational GPT reference implementation

minGPT is Andrej Karpathy’s MIT-licensed PyTorch reimplementation of GPT, deliberately organized as a small, readable educational codebase. Its January 2023 README calls it semi-archived and points readers needing more current development toward nanoGPT; it is therefore useful as an inspectable dense-GPT baseline, not as a current production-training stack.[^mingpt-readme]

## Architecture exposed directly in code

`mingpt/model.py` implements a decoder-only Transformer with learned token and absolute-position embeddings, embedding dropout, a stack of pre-LayerNorm residual blocks, final LayerNorm, and an untied vocabulary projection.[^mingpt-model]

Each block applies:

1. LayerNorm → multi-head causal self-attention → residual addition;
2. LayerNorm → `D → 4D → D` MLP with the OpenAI-GPT GELU approximation and residual dropout → residual addition.[^mingpt-model]

The attention module produces Q, K, and V through one `D → 3D` linear projection, reshapes them into heads, applies a lower-triangular causal mask to scaled QKᵀ scores before softmax, then applies an output projection and residual dropout. The model asserts that sequence length does not exceed `block_size` and that embedding width is divisible by head count.[^mingpt-model]

## Configurations and initialization

The model can accept explicit layer/head/width parameters or select named presets including GPT-1, GPT-2 (124M through XL), a 44M Gopher entry, and small `gpt-mini`, `gpt-micro`, and `gpt-nano` configurations.[^mingpt-model] Linear and embedding weights initialize from a normal distribution with standard deviation 0.02; residual `c_proj` weights are subsequently reinitialized with standard deviation $0.02/\sqrt{2N}$ for $N$ layers.[^mingpt-model]

## GPT-2 compatibility path

`BPETokenizer` implements the GPT-2 byte-to-Unicode mapping, regex pre-tokenization, ranked BPE merges, and inverse decoding. `get_encoder()` retrieves GPT-2’s `encoder.json` and `vocab.bpe` into a local cache and asserts the expected 50,257-token vocabulary and 50,000 merges.[^mingpt-bpe]

`GPT.from_pretrained()` constructs a supported GPT-2 configuration, loads a Hugging Face `GPT2LMHeadModel`, and transposes the Conv1D-layout attention and MLP weights when copying them to PyTorch `nn.Linear` modules.[^mingpt-model] The supplied unit test loads both implementations, then checks close logits, equal greedy token IDs, and equal decoded text for one prompt. This is an implementation-parity test for that configuration, not an accuracy or broad interoperability evaluation.[^mingpt-huggingface-test]

## Generation boundary

`generate()` repeatedly forwards the current sequence, takes the final-position logits, optionally applies temperature and top-k filtering, then greedily selects or multinomial-samples one token and appends it. When the sequence exceeds `block_size`, it crops to the latest window.[^mingpt-model] The implementation does not retain per-layer attention keys and values between decoding steps, so it recomputes the active prefix on each step; [KV caching](kv-caching.md) is the corresponding optimization.

## Scope limits

- The README lists mixed precision, distributed training, benchmark reproduction, richer logging, and broader checkpoint loading as unfinished work.[^mingpt-readme]
- The package metadata declares only `torch`, while the BPE and Hugging Face test code also import additional libraries; a runnable environment therefore requires dependencies beyond the minimal package declaration.[^mingpt-bpe][^mingpt-huggingface-test]
- Its MIT license permits reuse but supplies the software without warranty.[^mingpt-readme]

## Relationships

- **Implements:** the dense baseline described in [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md).
- **Operationalizes:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md)'s shifted-loss and autoregressive-decoding interfaces.
- **Matches:** the GPT-2-style pre-normalization, learned-position configuration documented in [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md), while remaining a separate implementation rather than the GPT-2 training release.
- **Lacks:** [KV caching](kv-caching.md)'s retained decode state.

[^mingpt-readme]: Karpathy, “minGPT,” [README](../raw/minGPT/README.md), status note, library description, usage, TODOs, and license reference.
[^mingpt-model]: Karpathy, [minGPT GPT model implementation](../raw/minGPT/mingpt/model.py), `CausalSelfAttention`, `Block`, `GPT`, `from_pretrained`, and `generate`.
[^mingpt-bpe]: Karpathy, [minGPT GPT-2 BPE implementation](../raw/minGPT/mingpt/bpe.py), `Encoder`, `get_encoder`, and `BPETokenizer`.
[^mingpt-huggingface-test]: Karpathy, [minGPT Hugging Face import test](../raw/minGPT/tests/test_huggingface_import.py), `TestHuggingFaceImport.test_gpt2`.
