---
type: Concept
title: LoRA training and deployment trade-offs
description: LoRA reduces trainable parameter and optimizer-state memory, but its quality, training cost, and multi-adapter serving behavior remain contingent on rank, target modules, data, and runtime design.
tags: [lora, peft, fine-tuning, gpu-memory, inference, limitations]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:31:26+07:00 }
sources:
  - id: lora-summary
    resource: ../raw/LoRA.md
    title: "LoRA overview (Vietnamese summary)"
---

# LoRA training and deployment trade-offs

By freezing the base model, LoRA avoids gradients and optimizer states for most pretrained weights, making task-specific checkpoints small and reducing parameter-related training memory. It does not eliminate activation memory or the cost of running the base model, and it does not establish that low-rank adaptation always matches full fine-tuning.[^lora-summary]

## Training economics and tuning

The source reports that, in its GPT-3 175B setup, LoRA reduced trainable parameters by approximately 10,000× and Adam GPU-memory requirements by approximately 3× relative to full fine-tuning. These are reported, setup-specific results, not general multipliers for all models or training stacks.[^lora-summary]

Rank $r$ controls adapter capacity: lower ranks reduce parameter, memory, and checkpoint cost, while higher ranks provide a more flexible update at greater cost and may not improve quality proportionally. Selecting target modules has a similar capacity–cost trade-off. The source describes $\alpha\approx r$ or $2r$ as common implementation heuristics rather than a universal rule.[^lora-summary]

LoRA's motivation is that the *adaptation update* $\Delta W$, not the pretrained weight $W_0$, may have low effective rank. If a task requires a higher-rank or broader change, a small-rank adapter may be insufficient. Dataset quality, label errors, data imbalance, and inconsistent prompt formatting remain independent training risks.[^lora-summary]

## Serving and operational implications

Merging a trained update into one base model can avoid a separate adapter computation during inference. Leaving adapters unmerged permits a shared base model to serve multiple task-specific adapters, but can add runtime overhead or require adapter-aware batching and serving support.[^lora-summary]

A large adapter fleet remains an operational system: it needs compatibility checks against the base model, versioning, routing, batching, tests, and access control. Small per-adapter files do not remove those governance and reliability requirements.[^lora-summary]

QLoRA is distinct from LoRA: the source describes it as using a quantized, typically 4-bit, frozen base while training higher-precision LoRA adapters. Quantization is therefore not required by the original LoRA mechanism.[^lora-summary]

## Relationships

- **Qualifies:** [LoRA low-rank adaptation](lora-low-rank-adaptation.md).
- **Contrasts with:** [InstructGPT human-feedback alignment](instructgpt-human-feedback-alignment.md); LoRA changes which parameters are trained during adaptation, while the documented InstructGPT recipe specifies supervision and preference-optimization stages.[^lora-summary]

[^lora-summary]: “LoRA overview” (Vietnamese summary), [raw source](../raw/LoRA.md), Sections 8–14 and 16–18. This is secondary-source evidence that links to Hu et al., “LoRA: Low-Rank Adaptation of Large Language Models,” ICLR 2022 / arXiv:2106.09685; the primary paper has not been independently ingested here.
