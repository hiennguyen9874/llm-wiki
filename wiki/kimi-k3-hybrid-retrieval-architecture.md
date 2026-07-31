---
type: Concept
title: Kimi K3 hybrid retrieval architecture
description: Kimi K3 combines bounded recurrent memory, periodic softmax retrieval, sparse expert capacity, and depth-wise residual retrieval.
tags: [kimi-k3, hybrid-attention, mixture-of-experts, retrieval]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:06:35Z }
sources:
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
---

# Kimi K3 hybrid retrieval architecture

Kimi K3 is described as a hybrid that assigns different storage and retrieval jobs to different components: Kimi Delta Attention (KDA) maintains bounded recurrent state, Multi-head Latent Attention (MLA) periodically retrieves from token context, sparse experts supply routed capacity, and Attention Residuals retrieve earlier depth-wise representations.[^gpt2-kimi3-2026]

## Reported backbone

The source reports 23 four-layer macrocycles, each containing three KDA layers followed by one MLA layer. It says the first layer uses a dense feed-forward network and subsequent layers use latent-space Mixture-of-Experts (MoE), with blockwise Attention Residuals at 12-layer boundaries.[^gpt2-kimi3-2026]

The resulting division of labor is:

| Component | Functional role |
|---|---|
| KDA | Constant-size recurrent memory with fine-grained decay |
| Periodic MLA | Full softmax retrieval over token context |
| Latent MoE | Sparse routed compute and parameter capacity in a compressed expert space |
| Attention Residuals | Selective retrieval over earlier representations in model depth |

This hybrid design treats bounded-state loss as something to mitigate with complementary retrieval paths rather than assuming one memory mechanism preserves everything.[^gpt2-kimi3-2026]

## Other reported changes

The explainer attributes gated MLA, MLA query LoRA, output gating, SiTU expert activations, and latent-space MoE to Kimi K3. It reports 898 experts: two shared experts and 896 routed experts, with 16 routed experts selected per token. These implementation details and associated latency or throughput claims require primary-source verification.[^gpt2-kimi3-2026]

## Relationships

- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) through fine-grained KDA state updates.
- **Uses:** [Attention Residuals](attention-residuals.md) for selective access across depth.
- **Mitigates limits of:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) by periodically retaining softmax access to token context.

## Evidence limits

All architecture details on this page are attributed to a single secondary social-media explainer. The underlying Kimi K3 paper, model card, and code were not included in the ingested source, so this page is an unverified architectural map rather than an authoritative specification.

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).
