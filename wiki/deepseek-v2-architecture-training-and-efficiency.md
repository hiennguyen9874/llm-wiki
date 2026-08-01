---
type: Concept
title: DeepSeek-V2 architecture, training, and efficiency
description: DeepSeek-V2 combines MLA and fine-grained DeepSeekMoE in a 236B-total/21B-active bilingual model, reporting lower training cost and KV state than DeepSeek 67B under its deployment configuration.
tags: [deepseek-v2, mixture-of-experts, multi-head-latent-attention, pretraining, inference, long-context]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:08:42Z }
sources:
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
---

# DeepSeek-V2 architecture, training, and efficiency

DeepSeek-V2 is a 60-layer bilingual MoE model with 236B total and 21B activated parameters per token. It combines MLA for sequence-growing decode-state reduction with DeepSeekMoE FFNs for sparse compute; the authors report 42.5% lower GPU-hours per trillion training tokens, 93.3% less deployed KV cache, and 5.76× maximum generation throughput than their dense DeepSeek 67B baseline.[^deepseek-v2-2024]

## Model and pretraining recipe

The model uses 128 attention heads of width 128, MLA latent widths of 512 (KV) and 1,536 (query), and a 64-dimensional decoupled rotary path. Except for the first layer, every FFN is an MoE layer with two shared experts and 160 routed experts; each token selects six routed experts. The report trains on 8.1T tokens with a 100K byte-level BPE vocabulary and states that Chinese tokens outnumber English tokens by about 12%.[^deepseek-v2-2024]

The initial 4K-context pretraining run uses AdamW, pipeline parallelism, eight-way expert parallelism, and ZeRO-1 data parallelism on H800 GPUs. For each token, routing is constrained to experts on at most three devices. The authors then extend context from 4K to 128K with 1,000 additional 32K-sequence steps, applying YaRN only to MLA’s decoupled shared rotary key; their Needle-in-a-Haystack plot is largely successful through 128K but contains a few non-perfect cells, and is not a broad long-context evaluation.[^deepseek-v2-2024]

## Sparse-routing controls

DeepSeek-V2 augments expert-level balancing with device-level and receiving-communication balance losses. It first selects up to $M$ devices with high-affinity experts, then performs top-$k$ expert selection only within them; this bounds each token’s cross-device fan-out. During training it also enforces a per-device capacity factor of 1.0 by dropping low-affinity assignments, while preserving all assignments for roughly 10% of sequences and disabling token dropping for evaluation.[^deepseek-v2-2024]

These controls make a specific distributed training run practical; they do not eliminate routing, dispatch, dropped-token, total-weight-storage, or target-workload quality trade-offs.[^deepseek-v2-2024]

## Reported efficiency and evaluation boundary

For the stated H800 training system, the report gives 172.8K GPU-hours per trillion tokens for DeepSeek-V2 versus 300.6K for dense DeepSeek 67B. Its serving configuration converts weights to FP8, quantizes KV cache to six bits on average, and uses MLA; on one eight-H800 node it reports over 50K generated tokens/s and over 100K prompt tokens/s. Thus the headline throughput and cache figures represent the combined architecture and serving stack, not MLA alone.[^deepseek-v2-2024]

The authors’ internal benchmark comparison places the 21B-active model near leading open models on many listed English, Chinese, code, and math tasks, but results vary: its Pile BPB (0.606) trails LLaMA 3 70B (0.602), while its MMLU (78.5), MATH (43.6), CMath (78.7), and several Chinese scores are competitive in that table. The model was trained on fewer than a quarter as many English tokens as the compared LLaMA 3 run according to the authors, and the evaluations use their internal framework. These are useful reported measurements, not independent capability rankings.[^deepseek-v2-2024]

## Relationships

- **Uses:** [Multi-head Latent Attention](multi-head-latent-attention.md) to reduce cached token state during inference.
- **Uses:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md) through shared experts and fine-grained routed experts.
- **Operationalizes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) with device-limited routing, three balance losses, and training-time token dropping.
- **Extended by:** [DeepSeek-V2 alignment, evaluation, and limitations](deepseek-v2-alignment-evaluation-and-limitations.md) through SFT and two-stage GRPO post-training.

## Evidence limits

All architecture, cost, throughput, and benchmark claims are from the authors’ technical report. The corpus composition, evaluation harness, kernels, quantization, request distribution, and production serving configuration are not independently reproduced here; causal contributions of MLA, MoE, quantization, and systems optimization are not isolated.[^deepseek-v2-2024]

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Sections 1–3 and Appendix B–D.
