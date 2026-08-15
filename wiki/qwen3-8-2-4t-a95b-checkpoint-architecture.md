---
type: Concept
title: Qwen3.8-2.4T-A95B checkpoint architecture
description: Qwen3.8-2.4T-A95B is a text-only 92-layer hybrid MoE checkpoint that repeats three Gated DeltaNet mixers and one global GQA mixer, with 512 routed experts plus a gated shared expert in every layer.
tags: [qwen3-8, checkpoint, hybrid-attention, gated-deltanet, grouped-query-attention, mixture-of-experts]
status: stable
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T04:30:52Z }
sources:
  - id: qwen38-card
    resource: ../raw/Qwen3.8-2.4T-A95B/README.md
    title: Qwen3.8-2.4T-A95B model card
  - id: qwen38-config
    resource: ../raw/Qwen3.8-2.4T-A95B/config.json
    title: Qwen3.8-2.4T-A95B checkpoint configuration
  - id: qwen38-modeling
    resource: ../raw/Qwen3.8-2.4T-A95B/modeling_qwen3_5_moe.py
    title: Qwen3.5-MoE Transformers reference implementation
  - id: qwen38-modular
    resource: ../raw/Qwen3.8-2.4T-A95B/modular_qwen3_5_moe.py
    title: Qwen3.5-MoE Transformers modular source
---

# Qwen3.8-2.4T-A95B checkpoint architecture

The supplied Qwen3.8-2.4T-A95B configuration selects a text-only causal-LM implementation with 92 layers: 69 Gated DeltaNet linear-attention layers and 23 global grouped-query-attention (GQA) layers in a repeating three-to-one schedule. Every layer then applies a 512-expert top-10 routed MoE plus a separately gated shared expert. The model card reports 2.4T total and 95B activated parameters; the configuration verifies the architectural dimensions but does not independently derive those totals.[^qwen38-card][^qwen38-config]

## Token mixers and cache state

The 8,192-wide backbone has 64 query heads and four KV heads of width 256 in each full-attention layer, so each KV head serves 16 query heads. The reference code applies per-head RMS normalization to Q/K, partial RoPE to 64 dimensions, a sigmoid output gate from a second query projection, and causal attention. These 23 layers retain ordinary per-token KV cache entries, preserving periodic global token-addressable retrieval while making that part of decode state grow with context.[^qwen38-config][^qwen38-modeling]

The other 69 layers use Gated DeltaNet with 16 Q/K heads of width 128 and 128 value heads of width 128. The implementation applies a depthwise causal convolution of width four, SiLU, normalized Q/K, sigmoid write strength, and input-dependent negative decay; it repeats each Q/K head eight times to align with value heads. It uses a chunked gated-delta kernel for sequence processing and a recurrent kernel for cached one-token decode, retaining convolution and recurrent states instead of one KV entry per token.[^qwen38-config][^qwen38-modeling]

The resulting cache is hybrid rather than fixed-size end to end: recurrent state is bounded in the linear layers, but global-attention KV state grows with the sequence.[^qwen38-modeling]

## Sparse feed-forward path

Each decoder layer has 512 routed experts, selects and renormalizes the top 10 routing probabilities per token, and adds a SiLU-gated shared-expert MLP controlled by a learned scalar sigmoid gate. Routed and shared expert intermediate widths are both 2,048. The configuration specifies a 0.001 router auxiliary-loss coefficient; the reference causal-LM wrapper adds that loss only when router-logit output is requested during labeled training.[^qwen38-config][^qwen38-modeling]

## Position, prediction, and modality boundary

The configuration uses a 248,320-token vocabulary, bfloat16 weights, a native 262,144-position limit, and default RoPE with base 10,000,000 over one quarter of an attention head. The model card calls the release text-only; although the generic family implementation also contains vision classes, this checkpoint selects `Qwen3_5MoeForCausalLM` and supplies no vision configuration.[^qwen38-card][^qwen38-config][^qwen38-modeling]

The card states that multi-token prediction (MTP) was trained with multiple steps, while the configuration declares one MTP hidden layer. However, the supplied causal-LM implementation neither constructs an MTP module nor consumes `mtp.*` checkpoint keys. The bundle therefore does not establish an active MTP inference path or its exact training objective.[^qwen38-card][^qwen38-config][^qwen38-modeling]

## Relationships

- **Uses:** [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md) for 69 recurrent token mixers.[^qwen38-modeling]
- **Uses:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) in 23 global layers, at 16 query heads per KV head.[^qwen38-config]
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) through normalized top-10 routing and an always-on gated shared path.[^qwen38-modeling]
- **Uses:** [Sequential multi-token prediction](sequential-multi-token-prediction.md) only as a declared training/checkpoint feature with an implementation boundary.[^qwen38-card][^qwen38-config][^qwen38-modeling]
- **Contrasts with:** [Qwen3.5-27B checkpoint architecture and implementation](qwen3-5-27b-checkpoint-architecture.md): both use a three-to-one Gated DeltaNet/global-attention schedule, but this checkpoint is text-only and sparse-MoE at every layer.[^qwen38-config]

## Evidence limits

This raw bundle contains a model card, configuration, and generic Transformers implementation, but no weights, tokenizer, license text, training data or procedure, benchmark artifacts, or serving measurements. The model-card frontmatter points to a `LICENSE` file that is not present in the supplied directory, so its use terms cannot be assessed from this bundle.

`modeling_qwen3_5_moe.py` is generated from `modular_qwen3_5_moe.py`; both were inspected. They document a reference family implementation and code paths, not measured runtime behavior or a complete training implementation.[^qwen38-modeling][^qwen38-modular]

[^qwen38-card]: Qwen Team, “Qwen3.8-2.4T-A95B,” [model card](../raw/Qwen3.8-2.4T-A95B/README.md), Highlights, Model Overview, API Usage, and Citation.

[^qwen38-config]: Qwen Team, “Qwen3.8-2.4T-A95B checkpoint configuration,” [config](../raw/Qwen3.8-2.4T-A95B/config.json).

[^qwen38-modeling]: Qwen Team and Hugging Face, “Qwen3.5-MoE Transformers reference implementation,” [source](../raw/Qwen3.8-2.4T-A95B/modeling_qwen3_5_moe.py), Gated DeltaNet, attention, MoE, decoder, text-model, and causal-LM classes.

[^qwen38-modular]: Qwen Team and Hugging Face, “Qwen3.5-MoE Transformers modular source,” [source](../raw/Qwen3.8-2.4T-A95B/modular_qwen3_5_moe.py), family-class inheritance and generated-source provenance.
