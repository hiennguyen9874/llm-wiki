---
type: Concept
title: nanoGPT training, data, and reproduction workflow
description: nanoGPT combines contiguous uint16 token streams, random shifted windows, mixed-precision AdamW, gradient accumulation, and PyTorch DDP in a compact GPT-2 reproduction workflow.
tags: [nanogpt, training-loop, distributed-training, data-preparation, gpt-2, pytorch]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-13T09:29:00Z }
sources:
  - id: nanogpt-readme
    resource: ../raw/nanoGPT/README.md
    title: nanoGPT README
  - id: nanogpt-train
    resource: ../raw/nanoGPT/train.py
    title: nanoGPT training implementation
  - id: nanogpt-configurator
    resource: ../raw/nanoGPT/configurator.py
    title: nanoGPT command-line configurator
  - id: nanogpt-openwebtext
    resource: ../raw/nanoGPT/data/openwebtext/prepare.py
    title: nanoGPT OpenWebText preparation
  - id: nanogpt-gpt2-config
    resource: ../raw/nanoGPT/config/train_gpt2.py
    title: nanoGPT GPT-2 training configuration
  - id: nanogpt-sizing
    resource: ../raw/nanoGPT/transformer_sizing.ipynb
    title: nanoGPT Transformer sizing notebook
---

# nanoGPT training, data, and reproduction workflow

nanoGPT couples a deliberately compact training script to flat token-ID files: it samples random adjacent input/target windows, trains with mixed precision and AdamW, supports one-process-per-GPU PyTorch DDP, evaluates validation loss, and checkpoints from rank zero.[^nanogpt-train] Its supplied OpenWebText recipe is a reproduction-oriented configuration, not independently verified evidence that it reproduces GPT-2.

## Data interface

The OpenWebText preparation script makes a shuffled 0.05% validation split with seed 2357, encodes each document with GPT-2 BPE, appends the end-of-text ID, and concatenates each split into a `uint16` memory-mapped binary stream.[^nanogpt-openwebtext] It reports roughly 9.04B training and 4.43M validation tokens after processing, but these are source-reported artifacts rather than data-governance or quality validation.[^nanogpt-openwebtext]

For each training batch, `train.py` samples random start offsets and forms `x = data[i:i+block_size]` and the one-token-shifted `y = data[i+1:i+1+block_size]`. It reopens the NumPy memmap each batch to avoid a cited memory leak, then pins and asynchronously transfers CUDA tensors.[^nanogpt-train] Character-level datasets provide `meta.pkl` token maps; otherwise the script defaults to the padded GPT-2-sized vocabulary.[^nanogpt-train]

## Distributed optimization loop

The script detects DDP through `RANK`, initializes the selected backend, assigns each process its local CUDA device, and divides gradient-accumulation steps by world size after asserting exact divisibility.[^nanogpt-train] Each update performs the configured number of forward/backward microsteps, suppressing DDP gradient synchronization until the final microstep, unscales and optionally clips gradients, then steps AdamW and clears gradients with `set_to_none=True`.[^nanogpt-train]

CUDA runs enable TF32 matmul/cuDNN and use autocast; `float16` additionally enables a `GradScaler`, while `bfloat16` does not.[^nanogpt-train] Optional `torch.compile` wraps the model before DDP. Validation periodically averages sampled train and validation losses; rank zero can log to Weights & Biases and saves model, optimizer, arguments, iteration, best validation loss, and configuration to one checkpoint.[^nanogpt-train]

The configurator executes a supplied Python config file and then applies type-checked `--key=value` overrides to script globals.[^nanogpt-configurator] It is convenient for local experiments, but config files are executable code and must be treated as trusted inputs.

## Supplied GPT-2-scale recipe and evidence limits

`config/train_gpt2.py` configures a 12-layer/12-head/768-width model with 12-token microbatches, context 1,024, and `5 × 8` accumulation steps. At eight processes this is 491,520 tokens per global update; its nominal 600,000-update schedule is about 295B tokens.[^nanogpt-gpt2-config] The README reports about four days on one 8×A100 40GB node and validation loss around 2.85, while the bundled plot reaches about 2.905 by displayed step 399.[^nanogpt-readme] These are author-reported, configuration- and hardware-specific results—not a substitute for rerunning the recipe with documented data and environment.

The sizing notebook estimates parameters, checkpoint state, FLOPs, and model-FLOPs utilization using an A100 BF16 peak assumption and the approximate $6ND$ training-cost rule.[^nanogpt-sizing] It explicitly notes an unresolved mismatch when trying to reproduce one Chinchilla-derived allocation, so its outputs are planning estimates rather than validated scaling-law results.[^nanogpt-sizing]

## Relationships

- **Uses:** [nanoGPT GPT-2 reference implementation](nanogpt-gpt-2-reference-implementation.md) for model, loss, optimizer groups, and MFU estimate.
- **Implements:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md)’s shifted-window objective and autoregressive evaluation boundary.
- **Uses:** [PyTorch DDP gradient synchronization](pytorch-ddp-gradient-synchronization.md)’s gradient-synchronization mechanism through the DDP wrapper.
- **Informs:** [Chinchilla compute-optimal training allocation](chinchilla-compute-optimal-training-allocation.md) only as an implementation-level sizing exercise, not replacement evidence.

[^nanogpt-readme]: Karpathy, [nanoGPT README](../raw/nanoGPT/README.md), launch instructions and reported reproduction results.
[^nanogpt-train]: Karpathy, [nanoGPT training implementation](../raw/nanoGPT/train.py), data loader, initialization, DDP, training, evaluation, checkpoint, and logging paths.
[^nanogpt-configurator]: Karpathy, [nanoGPT command-line configurator](../raw/nanoGPT/configurator.py), config execution and command-line override behavior.
[^nanogpt-openwebtext]: Karpathy, [nanoGPT OpenWebText preparation](../raw/nanoGPT/data/openwebtext/prepare.py), split, encoding, and binary-stream export.
[^nanogpt-gpt2-config]: Karpathy, [nanoGPT GPT-2 training configuration](../raw/nanoGPT/config/train_gpt2.py), batch, accumulation, token, and schedule settings.
[^nanogpt-sizing]: Karpathy, [nanoGPT Transformer sizing notebook](../raw/nanoGPT/transformer_sizing.ipynb), FLOP, utilization, and timing calculations.
