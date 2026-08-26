---
type: Concept
title: Qwen3.8-Flash-Next architecture and implementation
description: Qwen3.8-Flash-Next is a multimodal 48-layer hybrid MoE checkpoint combining three Gated DeltaNet layers with one Qwen Sparse Attention layer, widened gated residual streams, and a layer-2 hashed N-gram memory.
tags: [qwen3-8, multimodal, hybrid-attention, gated-deltanet, sparse-attention, mixture-of-experts, n-gram-embeddings]
status: stable
created: 2026-08-26
generated: { by: llm-wiki-agent/1, at: 2026-08-26T15:18:15Z }
sources:
  - id: qwen38-next-card
    resource: ../raw/Qwen3.8-Flash-Next/README.md
    title: Qwen3.8-Flash-Next model card
  - id: qwen38-next-config
    resource: ../raw/Qwen3.8-Flash-Next/config.json
    title: Qwen3.8-Flash-Next checkpoint configuration
  - id: qwen38-next-configuration
    resource: ../raw/Qwen3.8-Flash-Next/configuration_qwen4_exp.py
    title: Qwen4-Exp Transformers configuration implementation
  - id: qwen38-next-modeling
    resource: ../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py
    title: Qwen4-Exp Transformers modeling implementation
  - id: qwen38-next-modular
    resource: ../raw/Qwen3.8-Flash-Next/modular_qwen4_exp.py
    title: Qwen4-Exp Transformers modular source
  - id: qwen38-next-figure
    resource: ../raw/Qwen3.8-Flash-Next/architecture.png
    title: Qwen3.8-Flash-Next architecture diagram
  - id: qwen38-next-blog
    resource: ../raw/Qwen3.8-Flash-Next/blog.md
    title: Qwen3.8-Flash-Next release blog
---

# Qwen3.8-Flash-Next architecture and implementation

Qwen3.8-Flash-Next is an experimental multimodal architecture preview for Qwen4. Its 48-layer, width-2,560 language backbone repeats three fixed-state Gated DeltaNet layers and one token-addressable [Qwen Sparse Attention](qwen-sparse-attention.md) layer, with a sparse MoE after every mixer. It also widens the residual path to four gated streams and injects a large hashed bigram/trigram memory at language layer 2.[^qwen38-next-card][^qwen38-next-config][^qwen38-next-modeling]

## Language backbone

The 12 repeated hybrid groups contain 36 Gated DeltaNet and 12 QSA layers. Gated DeltaNet uses 16 Q/K heads and 48 value heads of width 128, a depthwise causal convolution of width four, normalized Q/K, sigmoid write strength, learned scalar decay, chunkwise sequence processing, and recurrent one-token decoding. QSA uses 24 query and two KV heads of width 256, but reads only tokens selected by its four-head block indexer under a 2,048-token budget.[^qwen38-next-config][^qwen38-next-modeling]

Each layer routes a token to 10 of 512 width-640 experts, renormalizes the selected softmax weights, and adds a separately sigmoid-gated shared width-640 expert. The model card reports 125B parameters with 6B activated per token, excluding a separately reported 51B N-gram embedding allocation and 4B MTP allocation; the local configuration verifies dimensions but does not independently reproduce all aggregate parameter accounting.[^qwen38-next-card][^qwen38-next-config][^qwen38-next-modeling]

## Widened residual and lexical memory

[Qwen Gated Residual](qwen-gated-residual.md) repeats the initial hidden state into four streams, computes element-wise low-rank read gates to form each branch input, and writes each attention or MoE output back with four scalar gates. A final read mixer reduces the expanded state for the language-model head.[^qwen38-next-modeling][^qwen38-next-figure]

At one-indexed layer 2, Per-Layer Embedding (PLE) hashes suffix bigrams and trigrams into eight independent subtables per order. With 16 heads, approximately 20M rows per head, and 160 dimensions per row, the configuration implies about 51.2B embedding parameters. PLE projects the concatenated lookup to keys and values, gates one shared value against each residual stream, and adds a zero-initialized dilated depthwise-convolution path. Hashing resets across EOS-delimited segments, and cached decode retains the preceding two token IDs.[^qwen38-next-config][^qwen38-next-modeling]

## Vision and position path

The conditional-generation checkpoint includes a 27-block vision encoder with width 1,152, 16 attention heads, 16×16 spatial patches, temporal patch size two, and 2×2 spatial merging into width-2,560 language features. Image and video features replace dedicated placeholder-token embeddings, while multimodal RoPE uses separate temporal, height, and width positions; text attention rotates 64 of each 256 head dimensions.[^qwen38-next-config][^qwen38-next-modeling]

The native configured context is 262,144 tokens. The card describes extension to one million using static YaRN with factor four, explicitly warning that static scaling can hurt shorter inputs; one million is therefore an optional extrapolation configuration, not the checkpoint's native default.[^qwen38-next-card][^qwen38-next-config]

## Training-recipe declaration

The blog says Muon handles two-dimensional linear maps in attention, Gated DeltaNet, and MoE experts, while AdamW handles embeddings, the MoE router, and Gated Residual's low-rank parameters. Fused QKV, SwiGLU, and GDN projections are split into their independent transformations before orthogonalization. Qwen also reports refitting its scaling law, selecting larger learning rates and batch sizes, and starting directly at the target batch instead of batch-size warmup; these are training declarations not represented or independently testable in the checkpoint implementation.[^qwen38-next-blog]

## MTP implementation boundary

The card reports one MTP layer trained for multiple steps and allocates 4B parameters to MTP. The configuration contains a one-layer full-attention MTP sub-config, but the supplied causal and conditional generation classes do not construct an MTP module and explicitly ignore unexpected `mtp.*` keys. This bundle establishes training/checkpoint metadata, not a runnable native MTP loss or speculative-decoding path.[^qwen38-next-card][^qwen38-next-config][^qwen38-next-modeling]

## Relationships

- **Uses:** [Qwen Sparse Attention](qwen-sparse-attention.md) every fourth language layer.
- **Uses:** [Qwen Gated Residual](qwen-gated-residual.md) around every mixer and MoE branch.
- **Uses:** [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md) for its recurrent layers.
- **Uses:** [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md) through layer-2 hashed PLE.
- **Uses:** [Sequential multi-token prediction](sequential-multi-token-prediction.md) only as declared training/checkpoint metadata in this supplied implementation.
- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) in the blog-declared pre-training recipe.
- **Evaluated by:** [Qwen3.8-Flash-Next evaluation and deployment limits](qwen3-8-flash-next-evaluation-and-deployment-limits.md).

## Evidence limits

The sources compiled on this page contain a card, blog, configuration, architecture figure, and generated plus modular Transformers sources, but no weights, tokenizer/processor assets, license file, training data, optimizer implementation, optimized QSA kernels, or benchmark artifacts. A separately supplied technical report was not part of this two-source ingest. The generated configuration and material modeling paths were inspected; the modular source was checked for lineage and relevant definitions rather than treated as independent evidence or re-read line by line.[^qwen38-next-card][^qwen38-next-blog][^qwen38-next-configuration][^qwen38-next-modeling][^qwen38-next-modular]

[^qwen38-next-card]: Qwen Team, “Qwen3.8-Flash-Next,” [model card](../raw/Qwen3.8-Flash-Next/README.md), Highlights, Model Overview, Best Practices, and Citation.

[^qwen38-next-config]: Qwen Team, “Qwen3.8-Flash-Next checkpoint configuration,” [config](../raw/Qwen3.8-Flash-Next/config.json).

[^qwen38-next-configuration]: Qwen Team and Hugging Face, “Qwen4-Exp Transformers configuration implementation,” [source](../raw/Qwen3.8-Flash-Next/configuration_qwen4_exp.py), text, vision, and composite configuration classes and architecture validation.

[^qwen38-next-modeling]: Qwen Team and Hugging Face, “Qwen4-Exp Transformers modeling implementation,” [source](../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py), text mixer, QSA, MoE, Gated Residual, PLE, vision, cache, and generation classes.

[^qwen38-next-modular]: Qwen Team and Hugging Face, “Qwen4-Exp Transformers modular source,” [source](../raw/Qwen3.8-Flash-Next/modular_qwen4_exp.py), family inheritance and canonical generated-source input.

[^qwen38-next-figure]: Qwen Team, “Qwen3.8-Flash-Next Architecture,” [included diagram](../raw/Qwen3.8-Flash-Next/architecture.png).

[^qwen38-next-blog]: Qwen Team, “Qwen3.8-Flash-Next,” [release blog](../raw/Qwen3.8-Flash-Next/blog.md), architecture and optimization sections.
