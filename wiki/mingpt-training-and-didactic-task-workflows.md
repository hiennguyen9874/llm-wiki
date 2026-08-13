---
type: Concept
title: minGPT training and didactic task workflows
description: minGPT pairs a generic single-process AdamW trainer with sorting, digit-addition, and character-language-model examples that make shifted targets, selective loss masking, greedy evaluation, and sampling explicit.
tags: [mingpt, training-loop, causal-language-modeling, pytorch, educational-code, evaluation]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-13T00:00:00Z }
sources:
  - id: mingpt-trainer
    resource: ../raw/minGPT/mingpt/trainer.py
    title: minGPT trainer implementation
  - id: mingpt-demo
    resource: ../raw/minGPT/demo.ipynb
    title: minGPT sorting demonstration
  - id: mingpt-adder
    resource: ../raw/minGPT/projects/adder/adder.py
    title: minGPT digit-addition project
  - id: mingpt-chargpt
    resource: ../raw/minGPT/projects/chargpt/chargpt.py
    title: minGPT character language-model project
  - id: mingpt-readme
    resource: ../raw/minGPT/README.md
    title: minGPT README
---

# minGPT training and didactic task workflows

minGPT separates the generic optimization loop from task-specific `Dataset` and evaluation code. Its examples use next-token targets but deliberately expose where loss is ignored, what a generated suffix is compared against, and how training versus sampling changes the input prefix.[^mingpt-trainer][^mingpt-demo][^mingpt-adder][^mingpt-chargpt]

## Generic trainer

`Trainer` selects CUDA when available (otherwise CPU), transfers the model to that device, creates the model’s optimizer, and draws replacement-sampled batches through a PyTorch `DataLoader`.[^mingpt-trainer] Each iteration runs forward loss computation, clears gradients with `set_to_none=True`, backpropagates, clips global gradient norm, steps the optimizer, invokes `on_batch_end` callbacks, and stops only once configured `max_iters` is reached.[^mingpt-trainer]

Its default configuration is batch size 64, AdamW learning rate `3e-4`, betas `(0.9, 0.95)`, weight decay `0.1`, gradient-norm limit `1.0`, four data-loader workers, and unlimited iterations unless the caller sets `max_iters`.[^mingpt-trainer] The trainer itself contains no validation split, checkpoint policy, learning-rate schedule, mixed precision, or distributed coordination; examples supply callbacks for logging, evaluation, and checkpoint saving.[^mingpt-trainer]

## Task examples

| Example | Sequence construction | Supervision and evaluation |
|---|---|---|
| Sorting notebook | Concatenates an input digit sequence with its sorted solution. | Masks targets while the model reads the input, trains on solution positions, then greedily generates and tests whole-solution equality on deterministic train/test partitions.[^mingpt-demo] |
| Addition project | Concatenates two zero-padded numbers with their sum written in reverse digit order. | Sets input-region labels to `-1`, which the model’s cross-entropy ignores; greedy completion is reversed and compared to the arithmetic sum.[^mingpt-adder] |
| Character LM project | Maps the unique characters of `input.txt` to IDs and returns adjacent fixed-length character windows. | Trains on every shifted next-character target and periodically samples a 500-character, top-k-limited continuation from a fixed text prompt.[^mingpt-chargpt] |

The sorting and addition examples isolate a useful pattern for conditional sequence tasks: serialize input and answer into one causal stream, then apply the loss only to answer positions. This is a pedagogical task formulation in the supplied code, not evidence that such tiny synthetic tasks transfer to general arithmetic or reasoning.[^mingpt-demo][^mingpt-adder]

## Operational limits

- The trainer samples with replacement for an effectively unbounded number of draws; an epoch metric is therefore not defined by the loop itself.[^mingpt-trainer]
- Checkpointing is callback-owned: addition saves only when a combined train/test correctness score improves, while the character example overwrites a latest checkpoint at each evaluation interval.[^mingpt-adder][^mingpt-chargpt]
- Evaluation coverage is example-specific. The repository’s supplied automated test validates GPT-2 import parity, not training quality, convergence, or project results.[^mingpt-readme]

## Relationships

- **Uses:** [minGPT educational GPT reference implementation](mingpt-educational-gpt-reference-implementation.md)'s `GPT`, optimizer configuration, loss handling, and generation method.
- **Illustrates:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md)'s target shift, ignored labels, clipping, validation distinction, and autoregressive generation.
- **Provides a learning baseline for:** [Foundations for training a bigram language model](foundations-for-training-a-bigram-language-model.md) and [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md).

[^mingpt-trainer]: Karpathy, [minGPT trainer implementation](../raw/minGPT/mingpt/trainer.py), `Trainer` configuration and `run` loop.
[^mingpt-demo]: Karpathy, [minGPT sorting demonstration](../raw/minGPT/demo.ipynb), `SortDataset`, training setup, and evaluation cells.
[^mingpt-adder]: Karpathy, [minGPT digit-addition project](../raw/minGPT/projects/adder/adder.py), `AdditionDataset`, evaluation, and callback.
[^mingpt-chargpt]: Karpathy, [minGPT character language-model project](../raw/minGPT/projects/chargpt/chargpt.py), `CharDataset` and sampling callback.
[^mingpt-readme]: Karpathy, “minGPT,” [README](../raw/minGPT/README.md), library/project inventory and test note.
