---
type: Concept
title: Nemotron 3.5 Lightning architecture and training
description: Nemotron 3.5 Lightning is NVIDIA’s reported 30B-total/3B-active hybrid model, interleaving Mamba-2 state-space blocks, sparse MoE blocks, and six global GQA blocks after more than 20T pre-training tokens.
tags: [nemotron, hybrid-model, mamba-2, mixture-of-experts, long-context, pretraining]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T14:46:56Z }
sources:
  - id: nemotron-lightning-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/README.md
    title: NVIDIA Nemotron 3.5 Lightning 30B A3B BF16 model card
  - id: nemotron-lightning-config
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/config.json
    title: NVIDIA Nemotron 3.5 Lightning 30B A3B checkpoint configuration
  - id: nemotron-lightning-code
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/modeling_nemotron_h.py
    title: NVIDIA Nemotron-H Transformers modeling implementation
---

# Nemotron 3.5 Lightning architecture and training

NVIDIA describes Nemotron 3.5 Lightning as a 30B-total/3B-active text model for reasoning, chat, and agentic customization. Its shipped configuration alternates 23 Mamba-2 blocks with 23 sparse-MoE blocks and inserts six causal GQA blocks, combining fixed-size recurrent sequence state with occasional token-addressable attention and sparse channel capacity.[^nemotron-lightning-card][^nemotron-lightning-config]

## Hybrid backbone

The 52-block schedule contains 23 `mamba`, 23 `moe`, and six `attention` entries; attention occurs at blocks 6, 13, 20, 27, 34, and 43. The Transformers configuration migrates those legacy labels to `linear_attention` and `full_attention`, and the implementation applies one pre-normalized mixer or expert block plus a residual connection at each depth.[^nemotron-lightning-config][^nemotron-lightning-code]

- **Model width:** 2,688, with a 131,072-token vocabulary and untied output head.
- **Mamba-2 path:** 64 heads of width 64, state size 128, eight state groups, expansion factor 2, convolution width 4, and training chunk size 128. Decode uses recurrent cache state rather than a token-growing KV cache for these blocks.
- **Attention path:** 32 query heads but only two KV heads, each of width 128. These six causal GQA blocks retain token-addressable KV history and dominate the context-growing portion of decode state.
- **MoE path:** 128 routed experts with top-6 routing plus one always-on shared MLP. Routed experts are ungated two-projection ReLU² MLPs of intermediate width 1,856; the shared path has width 3,712. The checkpoint does not use the optional latent expert projection.

The router computes sigmoid affinities in FP32, adds a learned correction bias only for top-$k$ selection, then gathers and normalizes the original affinities for output weighting and scales them by 2.5. In this checkpoint `n_group=topk_group=1`, so the implementation’s group mask does not narrow expert choice.[^nemotron-lightning-config][^nemotron-lightning-code]

## Training pipeline

The card reports more than 20T pre-training tokens from curated, crawled, and synthetic code, math, science, legal, multilingual, and general-knowledge data. Pre-training used Megatron-LM and an NVFP4 recipe; a continued-pre-training stage trained multi-token-prediction layers. Post-training then used synthetic and curated SFT for reasoning, tool use, structured output, and long retrieval, followed by asynchronous multi-environment GRPO across math, code, science, instruction following, multi-step tools, conversations, and structured-output environments.[^nemotron-lightning-card]

The card lists pre-training freshness through September 2025 and post-training freshness through May 2026, but elsewhere gives training-data collection through December 2025. The source does not reconcile whether the latter date applies to acquisition, filtering, or actual pre-training inclusion.[^nemotron-lightning-card]

## Context and MTP implementation gaps

The model card advertises up to one million tokens and gives 1,048,576-token vLLM recipes for eight H100s and one GB200. The checkpoint itself declares `max_position_embeddings=262144`, RoPE theta 10,000, and no explicit RoPE scaling; the recipes bypass vLLM’s configured-length guard. The bundle therefore documents a 1M serving claim but does not, by itself, establish how attention-position behavior was extended or validated from the checkpoint’s native 256K metadata.[^nemotron-lightning-card][^nemotron-lightning-config]

Likewise, the configuration declares one next-token-prediction extension composed of attention and MoE blocks, but the bundled `NemotronHForCausalLM` constructs only the 52 backbone blocks and language-model head. No MTP module or MTP loss appears in the supplied implementation. The card supports MTP as a training and rollout-acceleration claim; this code bundle is not a runnable reference for that path.[^nemotron-lightning-card][^nemotron-lightning-config][^nemotron-lightning-code]

## Relationships

- **Uses:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) for most sequence-mixing blocks.
- **Uses:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) in six global-attention blocks.
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) through 128 routed experts and a shared path.
- **Trained with:** [Group Relative Policy Optimization](group-relative-policy-optimization.md) during multi-environment post-training.
- **Declares:** [Sequential multi-token prediction](sequential-multi-token-prediction.md), subject to the bundled-implementation gap above.
- **Evaluated by:** [Nemotron 3.5 Lightning evaluation and deployment limits](nemotron-3-5-lightning-evaluation-and-deployment-limits.md).

## Evidence limits

The model card and implementation are NVIDIA-authored release artifacts, not independent validation. Weights, tokenizer/chat template, evaluation recipes, data samples, and four linked Model Card++ subcards were not included in this raw bundle. Two referenced benchmark images were also absent; the textual benchmark table was available. Architecture claims above were checked against the config and modeling code, but training, parameter counts, data filtering, and long-context capability could not be independently reproduced.[^nemotron-lightning-card][^nemotron-lightning-config][^nemotron-lightning-code]

[^nemotron-lightning-card]: NVIDIA, “NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16,” [model card](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/README.md), Model Summary, Model Design, Training Methodology, data disclosures, and Quick Start Guide.

[^nemotron-lightning-config]: NVIDIA, “NVIDIA Nemotron 3.5 Lightning checkpoint configuration,” [config](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/config.json).

[^nemotron-lightning-code]: NVIDIA/Hugging Face, “Nemotron-H modeling implementation,” [source](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/modeling_nemotron_h.py), Mamba mixer, MoE/router, attention, block, model, and causal-LM classes.
