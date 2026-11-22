---
type: Concept
title: Inkling 2 Mini pruning, quantization and training
description: Inkling 2 Mini combines middle-layer recurrence with expert pruning, distillation healing, low-precision training and post-training, as reported by its developer.
tags: [looped-models, mixture-of-experts, quantization, agent-training]
status: draft
created: 2026-11-22
generated: { by: llm-wiki-agent/1, at: 2026-11-22T10:24:19Z }
stale_after: 2027-05-22
sources:
  - id: tml-inkling-release
    resource: ../raw/inkling-2-mini/index.md
    scope: ../raw/inkling-2-mini/
    kind: web
    title: "Introducing Inkling 2 Mini"
---

# Inkling 2 Mini pruning, quantization and training

Thinking Machines Lab **reports** that its 24-layer looped MoE model combines three passes through the middle 12 layers with pruning, 4-bit expert training, post-pruning distillation and agent-oriented post-training. These are developer claims, not independently reproduced. See the [architecture report](inkling-2-mini-looped-moe-architecture-report.md) for layer structure and secondary diagram details.[^tml-inkling-release]

## Training recipe

- The starting model selects 8 of 384 experts per layer; at one midtraining point, two-thirds are pruned, leaving the 128 most-used experts per layer. A subsequent 1T tokens distilled from a larger internal Inkling model reportedly recover pre-pruning performance. Pruning reduces stored weights; neither the pruning effect alone nor its independent compute cost is quantified here.[^tml-inkling-release]
- Expert forward passes use NVFP4 from pretraining through RL with a dedicated GB300 hardware-accelerated kernel; the last four layers use MXFP8 forward passes. The release says deployed weights retain training precision (20 layers NVFP4, four MXFP8), avoiding an additional quantization conversion. It reports ~20 GB footprint; this is memory usage, not a speed measurement.[^tml-inkling-release]
- After healing, supervised fine-tuning is followed by 2.2T RL tokens over 2,000 steps; post-training includes on-policy distillation for alignment. The article does not give a complete data mixture, training compute, reward design or hyperparameters.[^tml-inkling-release]
- The developer compares an **unpruned** looped model with its unpruned non-looped scaling-ladder model: the latter used 7.5% less training compute, but needed 140% more inference compute to match loss on 512k-token agentic traces. This is a reported loss-matched compute comparison, not an isolated pruning test or measured latency improvement.[^tml-inkling-release]

## Capabilities and deployment limits

For agentic coding, the release reports DeepSWE v1.1 48.2% versus Qwen3.8-27B 42.2%, using mini-swe-agent v2.4.6, and SWE-bench Pro v2 Hard 77.9% versus 73.8% on 51 tasks. The models have different architectures and total/active parameter counts, and the release warns evaluation setups vary by model. The displayed decoding-speed comparison is a **theoretical** batch-one BF16 weight-bandwidth ceiling at 614 GB/s including repeat reads, not measured throughput.[^tml-inkling-release]

At launch the developer reports Ollama support on Macs with at least 32 GB RAM and native NVFP4 on NVIDIA DGX Spark; hardware, software support and benchmark rankings can change. It reports 50.0% MultiChallenge and 33.4% ComplexConstraints v1.1 and acknowledges weaker multi-turn and constraint following than Qwen3.8-27B.[^tml-inkling-release]

## Coverage and trust

The sole local artifact, the release capture, was inspected as text, including inline SVG chart labels and captions; the release is promotional and model-author reported. Two external demonstration videos were excluded as illustrative, and linked model cards, weights, kernel code, benchmark protocols and third-party energy study were not captured or inspected. Publication date, capture date, license and revision are not stated. Numerical claims are not independently verified; draft status records these missing artifacts and reproducibility limits.[^tml-inkling-release]

## Relationships

- Uses: [Inkling 2 Mini looped MoE architecture report](inkling-2-mini-looped-moe-architecture-report.md) describes the recurrent architecture used by this training recipe.[^tml-inkling-release]
- Related to: [Inkling variable-loop reasoning and monitorability](inkling-variable-loop-reasoning-and-monitorability.md) describes the related research variant and pass-count experiments.[^tml-inkling-release]

[^tml-inkling-release]: Thinking Machines Lab, *Introducing Inkling 2 Mini*, `raw/inkling-2-mini/index.md`, opening, §§“Capabilities” (table and limitations), “Architecture and training” (looping, NVFP4, pruning and healing, training), and “Try Inkling 2 Mini today”.
