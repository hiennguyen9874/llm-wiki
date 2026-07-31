---
type: Concept
title: Attention Residuals
description: Attention Residuals replace uniform residual accumulation with learned retrieval over earlier depth-wise representations.
tags: [attention-residuals, residual-stream, depth, retrieval]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:06:35Z }
sources:
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
---

# Attention Residuals

Attention Residuals (AttnRes) make the residual stream selectively addressable across model depth. Instead of giving a later layer only an equally weighted additive accumulation of all preceding outputs, AttnRes learns weights that retrieve the earlier representations most useful to that layer.[^gpt2-kimi3-2026]

## Mechanism

A conventional residual stack can be summarized as an embedding plus the unweighted sum of preceding layer outputs. AttnRes assigns each term a learned, normalized weight. In the described implementation, a layer-specific query scores normalized earlier residual states; a softmax over depth produces the weights used to mix those states.[^gpt2-kimi3-2026]

This creates a second retrieval axis:

- token attention retrieves information across sequence positions;
- AttnRes retrieves representations across network depth.

The source argues that selective depth access mitigates residual dilution and the need for later layers to overcome an increasingly large accumulated stream.[^gpt2-kimi3-2026]

## Blockwise form

Applying depth attention at every layer would be costly. Kimi K3 is described as grouping the outputs of 12 decoder layers into block representations and applying AttnRes at those boundaries. The source reports eight such blocks across the model's 23 four-layer macrocycles.[^gpt2-kimi3-2026]

## Relationships

- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) as a complement to token-context retrieval and bounded recurrent memory.

## Evidence limits

The mechanism and Kimi K3 placement are compiled from one secondary explainer. Reported compute and latency benefits were excluded from the synthesis because no primary benchmark evidence was included.

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).
