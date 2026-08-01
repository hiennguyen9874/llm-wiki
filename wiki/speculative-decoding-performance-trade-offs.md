---
type: Concept
title: Speculative decoding performance trade-offs
description: Speculative decoding improves decode latency when cheap, target-aligned drafts and efficient block verification outweigh draft, memory, and serving overheads.
tags: [speculative-decoding, inference, decoding, latency, gpu-utilization, kv-cache]
status: draft
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:38:26Z }
sources:
  - id: speculative-decoding-summary
    resource: ../raw/SpeculativeDecoding.md
    title: "Speculative decoding overview (Vietnamese summary)"
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
---

# Speculative decoding performance trade-offs

Speculative decoding can improve autoregressive decode latency because a target model can score a short proposed continuation more efficiently than making the same number of isolated one-token calls. Its realized gain depends on draft-model cost and agreement with the target, speculation length, hardware and batching, and KV-cache and communication overhead; it does not directly accelerate prompt prefill.[^speculative-decoding-summary]

## Acceptance and expected progress

For a draft distribution $q$ and target distribution $p$, the per-position acceptance probability is

$$
\alpha = \sum_x \min(p(x),q(x)) = 1-D_{\mathrm{TV}}(p,q).
$$

Under the simplifying assumption that each of $\gamma$ proposal positions has the same independent acceptance probability, the expected tokens emitted in a round, including the correction or bonus token, are

$$
E[N]=1+\alpha+\cdots+\alpha^{\gamma}
=\frac{1-\alpha^{\gamma+1}}{1-\alpha}.
$$

Thus, a draft need not be perfectly accurate, but it must be sufficiently close to the target for accepted prefixes to amortize target verification.[^speculative-decoding-summary]

## Latency model and boundary

If one target forward pass takes $T_p$, one draft step takes $T_q$, and $c=T_q/T_p$, a round is approximated by $T_p(1+\gamma c)$. The corresponding idealized speedup is

$$
\frac{1-\alpha^{\gamma+1}}{(1-\alpha)(1+\gamma c)}.
$$

This is a decision aid rather than a performance guarantee: a larger or more accurate draft can raise $\alpha$ while erasing savings through a higher $c$, and a longer proposal block adds both draft and verification work while making an early rejection more likely.[^speculative-decoding-summary]

Block verification is valuable especially when one-token decoding underuses the GPU or is limited by weight reads, memory bandwidth, and launch overhead. The source reports roughly $2$–$3\times$ speedups for a T5-XXL implementation and $2$–$2.5\times$ for a distributed Chinchilla 70B setting; these are workload-specific results, not general guarantees.[^speculative-decoding-summary]

## Sequential multi-token-head evidence

DeepSeek-V3 supplies a reported self-speculation case: its one-depth sequential multi-token-prediction module is trained as an additional objective and can be retained to propose a second token. The authors report 85–90% second-token acceptance across tested generation topics and 1.8× tokens/s, but do not specify enough workload, batching, or serving detail here to generalize the figure.[^deepseek-v3-2024]

## Deployment constraints

- A separate draft model increases memory use; placing it on a different device can add communication cost.
- A shared vocabulary and tokenizer make exact token-level verification straightforward; differing tokenizations require more complex handling.
- Benefits tend to be stronger for interactive, small-batch, predictable continuations. At high batch utilization, additional verification compute can reduce the gain.
- Speculation length can be tuned dynamically from draft confidence, acceptance history, entropy, context length, request type, or system load.
- Self-speculation, multi-token heads, tree proposals, and retrieval-derived proposals change how candidates are produced, but retain target verification as the mechanism for preserving target behavior.[^speculative-decoding-summary]

## Relationships

- **Operationalizes:** [Speculative decoding exact sampling](speculative-decoding-exact-sampling.md) under hardware and workload constraints.
- **Complemented by:** [FlashAttention implementation evolution](flashattention-implementation-evolution.md), whose prefill-oriented attention kernels address a different inference phase; speculative decoding primarily targets decode.[^speculative-decoding-summary]
- **Complemented by:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), which reduces growing KV-cache traffic during decode rather than proposing multiple tokens for target verification.[^speculative-decoding-summary]
- **Implemented by:** [Sequential multi-token prediction](sequential-multi-token-prediction.md) in the reported DeepSeek-V3 self-speculation setup.[^deepseek-v3-2024]

[^speculative-decoding-summary]: “Speculative decoding overview” (Vietnamese summary), [raw source](../raw/SpeculativeDecoding.md), Sections 10–13 and 16–20. This secondary source cites Leviathan, Kalman, and Matias, “Fast Inference from Transformers via Speculative Decoding” (ICML 2023), and Chen et al., “Accelerating Large Language Model Decoding with Speculative Sampling” (2023); neither primary paper has been independently ingested here.

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), Section 6.3.
