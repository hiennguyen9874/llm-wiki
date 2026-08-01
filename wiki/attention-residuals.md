---
type: Concept
title: Attention Residuals
description: Attention Residuals replace uniform residual accumulation with learned softmax retrieval over earlier depth-wise representations, with a block form that bounds cache and communication overhead.
tags: [attention-residuals, residual-stream, depth, retrieval]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:00:00Z }
sources:
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# Attention Residuals

Attention Residuals (AttnRes) make representations selectively addressable across model depth. Instead of passing only the uniform additive accumulation of prior layer outputs, each layer uses a learned pseudo-query and softmax weights to mix the embedding and preceding representations.[^kimi-k3-2026]

## Full form

For layer $l$, a learned query $w_l$ scores RMS-normalized earlier layer outputs. Softmax-normalized scores $\alpha_{i\to l}$ produce

$$
h_l=\sum_{i=0}^{l-1}\alpha_{i\to l}v_i.
$$

RMS normalization prevents output magnitude alone from dominating depth attention. This gives token attention and depth attention distinct jobs: one retrieves across sequence positions, while AttnRes retrieves intermediate transformations.[^kimi-k3-2026]

Full AttnRes has affordable $O(L^2d)$ arithmetic for fewer than 100 layers, according to the report, but retains $O(Ld)$ live representations and adds cross-stage communication under pipeline parallelism.[^kimi-k3-2026]

## Block form

Block AttnRes sums outputs within each block and applies full depth attention only over the embedding and completed block representations. A layer inside the current block can also access its intra-block partial sum. This reduces memory and communication from $O(Ld)$ to $O(Nd)$ for $N$ blocks and supports an online-softmax merge between parallel inter-block retrieval and the sequential current-block sum.[^kimi-k3-2026]

Kimi K3 uses eight 12-layer blocks plus a partial final block; counting the embedding source yields nine retrievable block representations. This corrects the earlier secondary summary’s ambiguous statement that the model had only eight total block sources.[^gpt2-kimi3-2026][^kimi-k3-2026]

## Systems implications

During training, block representations are generated once and shared; checkpointing keeps per-layer saved activations comparable to a standard residual stack. During serving, sequence parallelism avoids replicating block representations across tensor-parallel ranks, while side-stream execution and fused online-softmax/RMSNorm reduce decode overhead. These are design claims from the Kimi K3 system, not architecture-independent guarantees.[^kimi-k3-2026]

## Relationships

- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Operationalized by:** [Kimi K3 lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md).

## Evidence limits

The Kimi K3 report provides the mechanism and system design but refers to a separate AttnRes paper for broad model-scale ablations. Its statement that approximately eight blocks recover most benefits is therefore cited evidence, not independently reproduced here.[^kimi-k3-2026]

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.2 and 5.
