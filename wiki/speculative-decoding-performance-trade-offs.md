---
type: Concept
title: Speculative decoding performance trade-offs
description: Speculative decoding improves decode latency when cheap, target-aligned drafts and efficient block verification outweigh draft, memory, and serving overheads.
tags: [speculative-decoding, inference, decoding, latency, gpu-utilization, kv-cache]
status: draft
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T14:46:56Z }
sources:
  - id: speculative-decoding-summary
    resource: ../raw/SpeculativeDecoding.md
    title: "Speculative decoding overview (Vietnamese summary)"
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
  - id: kimi-k3-dspark-card
    resource: ../raw/KimiK3DSparkspeculator.md
    title: "Kimi K3 DSpark speculator (Hugging Face model card)"
  - id: dflash-2026
    resource: ../raw/arXiv-2602.06036v2/main.tex
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: nemotron-dflash-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DFlash.md
    title: NVIDIA Nemotron 3.5 Lightning DFlash model card
  - id: nemotron-dspark-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DSpark.md
    title: NVIDIA Nemotron 3.5 Lightning DSpark model card
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

## DSpark long-context acceptance evidence

The Kimi K3 DSpark speculator card reports SGLang `acc_len` — the histogram-native request acceptance length, averaged within each question and then equally across questions — of 2.99–5.51 across eight benchmarks. At one-million-token RULER V2 inputs (actual prompts of 1,000,432–1,047,925 tokens), average acceptance length stays about 4.26, so long-context acceptance does not collapse at scale in this configuration. AIME26 acceptance is weakest for 1–4K-token outputs (about 2.56–2.58) and rises to about 4.92 for two very long outputs, so acceptance varies with output regime. The draft is a 2.25B-parameter parallel draft (DFlash-style, block size 7) against a 2.8T target, an unusually large draft that shifts the draft-cost side of the trade-off. These figures measure accepted draft tokens, not end-to-end speedup; the card provides no latency or token-throughput claims.[^kimi-k3-dspark-card]

## DFlash parallel-draft evidence

DFlash replaces sequential autoregressive drafting with one parallel block-diffusion pass conditioned on target hidden features. In its author-run Qwen3 evaluation, average decoding speedup is 4.86–4.91× under greedy decoding and 4.03–4.24× at temperature 1, versus 1.68–1.81× for matched-width EAGLE-3. Serving results expose the boundary hidden by those averages: on Qwen3-8B, SGLang Math500 speedup falls from 5.1× at concurrency 1 to 2.8× at 32, and vLLM Qwen3.5-9B results show similar declines. Parallel drafting reduces the sequential draft term, but verification compute and device saturation still cap gains.[^dflash-2026]

## Same-target draft comparison

NVIDIA’s DFlash and DSpark cards provide a same-publisher, same-target SPEED-Bench comparison at draft length seven and temperature 1.0/top-p 0.95. DSpark reports higher accepted length in every category and 3.75 overall versus DFlash’s 3.16, but is larger at 967M versus 833M parameters. Without latency, throughput, concurrency, or memory measurements, the acceptance advantage cannot determine which draft is faster; it illustrates the central trade-off between proposal alignment and draft cost.[^nemotron-dflash-card][^nemotron-dspark-card]

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
- **Evidenced by:** [DSpark speculator evaluation and deployment](dspark-speculator-evaluation-and-deployment.md) with concrete acceptance lengths at up to one-million-token context.
- **Evidenced by:** [DFlash evaluation and serving trade-offs](dflash-evaluation-and-serving-trade-offs.md), which reports end-to-end speedups and their decline with concurrency.

[^speculative-decoding-summary]: “Speculative decoding overview” (Vietnamese summary), [raw source](../raw/SpeculativeDecoding.md), Sections 10–13 and 16–20. This secondary source cites Leviathan, Kalman, and Matias, “Fast Inference from Transformers via Speculative Decoding” (ICML 2023), and Chen et al., “Accelerating Large Language Model Decoding with Speculative Sampling” (2023); neither primary paper has been independently ingested here.

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), Section 6.3.

[^kimi-k3-dspark-card]: RadixArk, “Kimi K3 DSpark speculator,” Hugging Face model card, [source](../raw/KimiK3DSparkspeculator.md), Evaluation Results, Model Specifications, and Serving with SGLang.

[^dflash-2026]: Chen, Liang, and Liu, “DFlash: Block Diffusion for Flash Speculative Decoding,” arXiv:2602.06036v2, [source](../raw/arXiv-2602.06036v2/main.tex), Sections 3–5 and Appendix C.

[^nemotron-dflash-card]: NVIDIA, “NVIDIA Nemotron 3.5 Lightning DFlash,” [model card](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DFlash.md), Model Architecture and Evaluation.

[^nemotron-dspark-card]: NVIDIA, “NVIDIA Nemotron 3.5 Lightning DSpark,” [model card](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DSpark.md), Model Architecture and Evaluation.
