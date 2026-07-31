---
type: Concept
title: Speculative decoding exact sampling
description: Speculative decoding uses a fast draft model and modified rejection sampling to emit blocks whose sampled distribution exactly matches a slower target model.
tags: [speculative-decoding, speculative-sampling, inference, decoding, rejection-sampling]
status: draft
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T00:00:00Z }
sources:
  - id: speculative-decoding-summary
    resource: ../raw/SpeculativeDecoding.md
    title: "Speculative decoding overview (Vietnamese summary)"
---

# Speculative decoding exact sampling

Speculative decoding lets a small, fast draft model $q$ propose a sequence of tokens and has the target model $p$ score that sequence in one causal forward pass. Per-token modified rejection sampling accepts proposals from left to right and samples a residual distribution on the first rejection, so the emitted continuation is sampled exactly from $p$, not merely an approximation.[^speculative-decoding-summary]

## Draft, verify, and correct

Starting from a prefix, the draft model autoregressively samples $\gamma$ proposed tokens and records each proposal distribution $q_i$. The target model then evaluates distributions $p_i$ for every proposed position in parallel. For proposed token $\tilde{x}_i$, accept it with probability

$$
\min\left(1, \frac{p_i(\tilde{x}_i)}{q_i(\tilde{x}_i)}\right).
$$

Verification stops at the first rejected proposal, because later proposals were conditioned on a token that was not retained. The correction token at that position must be drawn from

$$
p_{\mathrm{residual}}(x) = \operatorname{Normalize}\bigl((p_i(x)-q_i(x))_+\bigr),
$$

rather than directly from $p_i$. If every draft token is accepted, the target's already computed next-position distribution provides one additional bonus token.[^speculative-decoding-summary]

## Distribution guarantee

For one proposed token $x$, the accepted branch contributes

$$
q(x)\min\left(1,\frac{p(x)}{q(x)}\right)=\min(p(x),q(x)).
$$

The rejection branch contributes $(p(x)-q(x))_+$. Their sum is $p(x)$, establishing exact target-model sampling at that position; the left-to-right construction extends this result to the continuation.[^speculative-decoding-summary]

This guarantee applies to stochastic sampling when acceptance and residual sampling are implemented as specified. In greedy decoding, a system can instead accept draft tokens while they equal the target distribution's argmax, then emit the target argmax at the first mismatch. The source notes that finite-precision arithmetic, random-number generation, and sampling-filter implementations can prevent bitwise-identical practical runs even where the theoretical distribution is preserved.[^speculative-decoding-summary]

## Relationships

- **Accelerates:** autoregressive decoding by replacing several sequential target-model calls with draft proposals and a block verification pass.[^speculative-decoding-summary]
- **Complemented by:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), which reduces decode KV-cache traffic through attention-head sharing rather than reducing the number of target decode iterations.
- **Operationalized by:** [Speculative decoding performance trade-offs](speculative-decoding-performance-trade-offs.md), which describes when the exact procedure yields latency gains.

[^speculative-decoding-summary]: “Speculative decoding overview” (Vietnamese summary), [raw source](../raw/SpeculativeDecoding.md), Sections 2–9, 15, and 18. This secondary source cites Leviathan, Kalman, and Matias, “Fast Inference from Transformers via Speculative Decoding” (ICML 2023), and Chen et al., “Accelerating Large Language Model Decoding with Speculative Sampling” (2023); neither primary paper has been independently ingested here.
