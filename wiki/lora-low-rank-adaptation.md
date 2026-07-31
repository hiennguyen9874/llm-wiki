---
type: Concept
title: LoRA low-rank adaptation
description: LoRA adapts a frozen pretrained linear layer by training a scaled low-rank update, reducing task-specific trainable parameters while retaining a mergeable effective weight.
tags: [lora, peft, fine-tuning, low-rank-adaptation, adapters]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:31:26+07:00 }
sources:
  - id: lora-summary
    resource: ../raw/LoRA.md
    title: "LoRA overview (Vietnamese summary)"
---

# LoRA low-rank adaptation

Low-Rank Adaptation (LoRA) is a parameter-efficient fine-tuning (PEFT) method that freezes a pretrained weight matrix $W_0$ and learns a low-rank update instead of updating the full matrix. For a linear layer, its effective weight is $W'=W_0+(\alpha/r)BA$, where $A\in\mathbb{R}^{r\times k}$, $B\in\mathbb{R}^{d\times r}$, and $r\ll\min(d,k)$.[^lora-summary]

## Mechanism

For an input $x$, LoRA changes the base computation from $W_0x$ to:

$$
h=W_0x+\frac{\alpha}{r}BAx.
$$

Only $A$ and $B$ are trainable. A full $d\times k$ update has $dk$ parameters, whereas the LoRA factors have $r(d+k)$ parameters. The source's $d=k=4096$, $r=8$ example gives 65,536 trainable parameters rather than 16,777,216 for that one full matrix (about 0.39%). The whole-model saving depends on the target modules, rank, and any additional trainable parameters.[^lora-summary]

The source reports initializing $A$ randomly and $B$ to zero, so $BA=0$ at insertion and the model initially behaves identically to the pretrained base. $\alpha/r$ scales the adapter contribution; $\alpha$ is therefore a forward-pass scaling hyperparameter, not merely a learning rate.[^lora-summary]

## Transformer placement and merging

The original reported experiments focus on attention projections, especially $W_Q$ and $W_V$. Later implementations may target additional attention projections or MLP linear layers; this increases adaptation capacity and trainable state, but is not a property of every LoRA configuration.[^lora-summary]

After training, the scaled update can be merged into the base weight, $W_{\mathrm{merged}}=W_0+(\alpha/r)BA$. A merged adapter uses the ordinary linear computation at inference, so it need not add a separate adapter path or inference latency. Keeping adapters separate instead enables switching task-specific updates on a shared base model, with runtime and serving implications described in [LoRA training and deployment trade-offs](lora-training-and-deployment-trade-offs.md).[^lora-summary]

## Relationships

- **Uses:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md); the source applies LoRA to Transformer linear projections, particularly self-attention projections.[^lora-summary]
- **Qualified by:** [LoRA training and deployment trade-offs](lora-training-and-deployment-trade-offs.md).

[^lora-summary]: “LoRA overview” (Vietnamese summary), [raw source](../raw/LoRA.md), Sections 1–7, 10, 12, and 15–16. This is secondary-source evidence that links to Hu et al., “LoRA: Low-Rank Adaptation of Large Language Models,” ICLR 2022 / arXiv:2106.09685; the primary paper has not been independently ingested here.
