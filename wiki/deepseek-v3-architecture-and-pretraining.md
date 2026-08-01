---
type: Concept
title: DeepSeek-V3 architecture and pretraining
description: DeepSeek-V3 is a reported 671B-total/37B-active MoE model that combines MLA, fine-grained experts, auxiliary-loss-free routing balance, and one-depth multi-token prediction after 14.8T-token pretraining.
tags: [deepseek-v3, mixture-of-experts, multi-head-latent-attention, pretraining, long-context]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:38:26Z }
sources:
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
---

# DeepSeek-V3 architecture and pretraining

DeepSeek-V3 is DeepSeek-AI’s reported 671B-total-parameter MoE Transformer that activates 37B parameters per token. It retains Multi-head Latent Attention (MLA) and fine-grained DeepSeekMoE, while adding batch-wise auxiliary-loss-free router balancing and a one-depth sequential multi-token-prediction objective; the report describes pretraining on 14.8T tokens and subsequent extension from 4K to 128K context.[^deepseek-v3-2024]

## Model configuration

The 61-layer model has width 7,168, 128 attention heads of width 128, a 512-dimensional KV latent, a 1,536-dimensional query latent, and a 64-dimensional decoupled rotary path. The first three FFNs are dense; every later layer has one shared expert and 256 routed experts of intermediate width 2,048. Each token selects eight routed experts and is limited to at most four nodes.[^deepseek-v3-2024]

The report uses sigmoid router affinities, normalizes the selected affinities for routing weights, and introduces per-expert biases only for top-$k$ selection. The bias updates supply batch-wise load control, while a very small sequence-wise auxiliary loss guards against extreme per-sequence imbalance. This is a reported V3 configuration, not a general proof that it dominates other router designs.[^deepseek-v3-2024]

## Corpus and context extension

The authors report a 14.8T-token, high-quality multilingual corpus with increased math and programming content, document packing without cross-sample attention masking, 10% Prefix-Suffix-Middle fill-in-the-middle examples, and a 128K byte-level BPE vocabulary. They randomly split some punctuation-plus-newline tokens during training to mitigate a tokenizer boundary issue in multiline few-shot prompts.[^deepseek-v3-2024]

Initial pretraining uses a 4K sequence length. Two 1,000-step YaRN phases then extend context to 32K and 128K, applying YaRN only to MLA’s decoupled rotary key. The report’s Needle-in-a-Haystack figure shows strong results through 128K, but is not broad evidence of long-context reasoning or retrieval quality.[^deepseek-v3-2024]

## Reported cost boundary

The report assigns 2.664M H800 GPU-hours to pretraining, 119K to context extension, and 5K to post-training (2.788M total); its USD estimate assumes $2 per H800 GPU-hour and excludes earlier research and ablations. These are author-reported costs for an optimized H800 stack, not a transferable model-training price.[^deepseek-v3-2024]

## Relationships

- **Uses:** [Multi-head Latent Attention](multi-head-latent-attention.md) for compressed token-addressable attention state.
- **Uses:** [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md) and [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) for sparse routing.
- **Uses:** [Sequential multi-token prediction](sequential-multi-token-prediction.md) as an additional pretraining objective.
- **Implemented by:** [DeepSeek-V3 training systems and FP8](deepseek-v3-training-systems-and-fp8.md).
- **Extended by:** [DeepSeek-V3 post-training, evaluation, and limitations](deepseek-v3-post-training-evaluation-and-limitations.md).

## Evidence limits

This page records the authors’ technical report and internal evaluations, not an independent model audit. The corpus is not enumerated at source level; the causal effects of scale, data, MLA, routing, multi-token prediction, and systems work are not isolated in the full V3 run.[^deepseek-v3-2024]

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), Sections 1–3 and 5.
