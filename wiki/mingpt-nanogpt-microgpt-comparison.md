---
type: Synthesis
title: minGPT, nanoGPT, and microgpt comparison
description: minGPT is a readable PyTorch GPT baseline, nanoGPT extends that line into a compact GPT-2 reproduction workflow, and microgpt exposes the same core learning mechanics in one dependency-free scalar-autograd script.
tags: [mingpt, nanogpt, microgpt, comparison, decoder-only-transformer, educational-code]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T15:41:31Z }
sources:
  - id: mingpt-readme
    resource: ../raw/minGPT/README.md
    title: minGPT README
  - id: mingpt-model
    resource: ../raw/minGPT/mingpt/model.py
    title: minGPT GPT model implementation
  - id: mingpt-trainer
    resource: ../raw/minGPT/mingpt/trainer.py
    title: minGPT trainer implementation
  - id: nanogpt-readme
    resource: ../raw/nanoGPT/README.md
    title: nanoGPT README
  - id: nanogpt-model
    resource: ../raw/nanoGPT/model.py
    title: nanoGPT model implementation
  - id: nanogpt-train
    resource: ../raw/nanoGPT/train.py
    title: nanoGPT training implementation
  - id: microgpt-code
    resource: ../raw/microgpt.py
    title: microgpt.py
---

# minGPT, nanoGPT, and microgpt comparison

All three are educational decoder-only GPT references, but their teaching boundary differs: **microgpt** reveals the algorithm below a tensor framework; **minGPT** makes a conventional PyTorch GPT readable; **nanoGPT** adds a compact, practical GPT-2 training/reproduction workflow. minGPT is semi-archived and nanoGPT is deprecated, so neither is documented as a current production stack.[^mingpt-readme][^nanogpt-readme]

| Dimension | minGPT | nanoGPT | microgpt |
|---|---|---|---|
| Best fit | Inspecting a readable PyTorch GPT and small didactic tasks | Studying a compact GPT-2-scale training/reproduction path | Learning autograd, attention, optimization, and sampling from first principles |
| Implementation | Small PyTorch codebase | Compact PyTorch codebase | One standard-library Python file with scalar `Value` autograd |
| Tokens and data | GPT-2-compatible BPE; examples include character-level data | GPT-2 BPE token streams or character datasets | Character vocabulary built from names or local `input.txt` |
| Default/model recipe | Learned positions, pre-LayerNorm, GELU, untied output head | GPT-2-small-shaped default; learned positions, pre-LayerNorm, GELU, tied embedding/output weights | Default one layer, width 16, four heads; RMSNorm, ReLU, no biases |
| Checkpoint path | Imports supported Hugging Face GPT-2 weights and has a parity test | Imports GPT-2 through XL Hugging Face weights | No checkpoint-import path documented |
| Training | Single-process AdamW trainer; examples own evaluation/checkpointing | Mixed precision, gradient accumulation, validation, rank-zero checkpointing, and PyTorch DDP | Sequential single-document training with hand-written Adam; no batching, evaluation, or checkpointing |
| Decode state | Recomputes the active prefix; no KV cache | Recomputes the active prefix; no KV cache | Retains per-layer K/V prefixes during a sequential pass or sample, as a pedagogical cache |
| Lifecycle | Semi-archived; README directs newer development to nanoGPT | Deprecated; README directs new users to nanochat | No lifecycle claim is recorded in the available concept |

## Practical selection

- Choose **microgpt** to trace every operation—including reverse-mode autodifferentiation—at the cost of tensor performance and realistic scale.[^microgpt-code]
- Choose **minGPT** for the clearest conventional PyTorch baseline, GPT-2 BPE/checkpoint compatibility, and tiny task examples such as sorting and addition.[^mingpt-model][^mingpt-trainer]
- Choose **nanoGPT** when the subject is the training pipeline: token-stream data preparation, mixed precision, accumulation, DDP, validation, and checkpointing.[^nanogpt-train]
- For a new maintained training project, treat all three as study references rather than a default production foundation; that is directly documented for minGPT and nanoGPT, while microgpt's stated scope is pedagogical rather than efficient.[^mingpt-readme][^nanogpt-readme][^microgpt-code]

## Relationships

- **Compares:** [minGPT educational GPT reference implementation](mingpt-educational-gpt-reference-implementation.md), [minGPT training and didactic task workflows](mingpt-training-and-didactic-task-workflows.md), [nanoGPT GPT-2 reference implementation](nanogpt-gpt-2-reference-implementation.md), [nanoGPT training, data, and reproduction workflow](nanogpt-training-data-and-reproduction-workflow.md), and [microgpt pure-Python GPT reference implementation](microgpt-pure-python-gpt-reference-implementation.md).
- **Contextualizes:** [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) and [KV caching](kv-caching.md).

## Evidence limits

This comparison concerns the supplied repositories and scripts, not measured quality, speed, safety, or current upstream maintenance beyond their recorded status notices. microgpt's retained K/V lists demonstrate causal state in its own sequential implementation; they do not establish production-cache behavior.[^microgpt-code]

[^mingpt-readme]: Karpathy, [minGPT README](../raw/minGPT/README.md), status and project scope.
[^mingpt-model]: Karpathy, [minGPT GPT model implementation](../raw/minGPT/mingpt/model.py), architecture, checkpoint import, and generation.
[^mingpt-trainer]: Karpathy, [minGPT trainer implementation](../raw/minGPT/mingpt/trainer.py), training-loop scope; task workflow details are compiled in [minGPT training and didactic task workflows](mingpt-training-and-didactic-task-workflows.md).
[^nanogpt-readme]: Karpathy, [nanoGPT README](../raw/nanoGPT/README.md), status and project scope.
[^nanogpt-model]: Karpathy, [nanoGPT model implementation](../raw/nanoGPT/model.py), architecture, checkpoint import, and generation.
[^nanogpt-train]: Karpathy, [nanoGPT training implementation](../raw/nanoGPT/train.py), data, distributed optimization, validation, and checkpointing.
[^microgpt-code]: Karpathy, [microgpt.py](../raw/microgpt.py), dataset loading, scalar autograd, model, training, and inference.
