---
type: Concept
title: N-gram embeddings and conditional memory
description: N-gram embedding methods augment token representations with learned local-pattern lookups, offering sparse embedding capacity distinct from both count-based n-gram language models and routed MoE computation.
tags: [embeddings, n-grams, conditional-memory, sparse-models, tokenization]
status: draft
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-27T03:11:23Z }
sources:
  - id: ngram-embedding-overview-2026
    resource: ../raw/N-gramembeddingsinLLM.md
    title: "N-gram embeddings in LLM (Vietnamese research overview)"
  - id: over-tokenized-transformer-2025
    resource: ../raw/2501.16975_Over-TokenizedTransformer/main.tex
    title: "Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling"
  - id: scone-2025
    resource: ../raw/2502.01637_ScalingEmbeddingLayersinLanguageModels/main.tex
    title: "Scaling Embedding Layers in Language Models"
  - id: conditional-memory-2026
    resource: ../raw/2601.07372_ConditionalMemoryviaScalableLookup/main.tex
    title: "Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models"
  - id: longcat-2-card-2026
    resource: ../raw/LongCat-2.0.md
    title: LongCat-2.0 model card
  - id: longcat-flash-lite-card-2026
    resource: ../raw/LongCat-Flash-Lite.md
    title: LongCat-Flash-Lite model card
  - id: longcat-embedding-scaling-2026
    resource: ../raw/2601.21204_ScalingEmbeddingsOutperformsScalingExpertsinLanguageModels/longcat.tex
    title: "Scaling Embeddings Outperforms Scaling Experts in Language Models"
  - id: qwen38-next-config
    resource: ../raw/Qwen3.8-Flash-Next/config.json
    title: Qwen3.8-Flash-Next checkpoint configuration
  - id: qwen38-next-modeling
    resource: ../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py
    title: Qwen4-Exp Transformers modeling implementation
  - id: qwen38-next-blog
    resource: ../raw/Qwen3.8-Flash-Next/blog.md
    title: Qwen3.8-Flash-Next release blog
  - id: qwen38-next-report
    resource: ../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md
    title: "On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability"
---

# N-gram embeddings and conditional memory

N-gram embedding methods enrich a token's input representation with learned vectors addressed by adjacent token sequences. They are a sparse local-pattern memory: the Transformer still produces the next-token distribution, whereas the n-gram is a lookup key rather than a count-based conditional-probability model.[^ngram-embedding-overview-2026]

## Mechanism

For a token sequence $t_1,\ldots,t_T$, one common formulation adds representations for suffix n-grams ending at position $i$:

$$
e_i = E_1(t_i) + \sum_{n=2}^{N} E_n\!\left(H_n(t_{i-n+1},\ldots,t_i)\right).
$$

$H_n$ maps an n-gram to a table address, commonly by hashing. Direct tables would require $V^n$ entries for vocabulary size $V$; hashing makes a bounded table practical but permits collisions. Implementations may add or otherwise fuse the retrieved vectors with the ordinary token embedding.[^ngram-embedding-overview-2026]

This is distinct from a classical n-gram language model, which estimates a probability such as $P(t_i\mid t_{i-n+1:i-1})$ directly from sequence statistics. Here, the local sequence selects a learned feature and downstream Transformer layers remain responsible for contextual processing and prediction.[^ngram-embedding-overview-2026]

## Reported design line

The supplied overview groups several variants under embedding scaling, over-encoding, or conditional memory:

- **Over-Encoding** adds hierarchical, modulo-addressed n-gram embeddings at the input while retaining the base-token output head. Its primary source reports input-table ablations up to 12.8M rows; see [Over-Encoding hierarchical n-gram input embeddings](over-encoding-hierarchical-n-gram-input-embeddings.md).[^over-tokenized-transformer-2025]
- **SCONE** selects frequent f-grams, learns their embeddings with a separate f-gram Transformer during training, and precomputes them into off-accelerator lookup storage for inference; its source reports table size and f-gram-model size as separate scaling axes. See [SCONE scalable contextualized offloaded n-gram embeddings](scone-scalable-contextualized-offloaded-n-gram-embeddings.md).[^scone-2025]
- **Byte Latent Transformer** uses hash-based byte n-gram embeddings (the overview reports orders 3–8).
- **Engram** places deterministic, multi-head hashed suffix n-gram lookup in selected Transformer layers, applies hidden-state-conditioned gating, and supports sharded training plus proposed host-prefetch inference. See [Engram conditional-memory architecture](engram-conditional-memory-architecture.md).[^conditional-memory-2026]
- **LongCat-Flash-Lite** is now documented by a technical report as using projected, multi-subtable hashed suffix N-gram embeddings. Its author-run matched scaling study finds a high-sparsity regime where this allocation lowers reported loss more effectively than adding experts, with collision, width, depth, and allocation limits; see [N-gram embedding scaling versus MoE expert scaling](n-gram-embedding-scaling-versus-moe-expert-scaling.md) and [LongCat-Flash-Lite N-gram-embedding architecture](longcat-flash-lite-ngram-embedding-architecture.md).[^longcat-embedding-scaling-2026]
- **LongCat-2.0** reports 135B N-gram Embedding parameters alongside its MoE and characterizes them as sparse dimensions orthogonal to MoE. Its card does not disclose the lookup mechanism or support its asserted optimal-allocation principles; see [LongCat-2.0 sparse-attention and embedding architecture](longcat-2-0-sparse-attention-and-embedding-architecture.md).[^longcat-2-card-2026]
- **Qwen3.8-Flash-Next** injects a checkpoint-verified layer-2 memory with eight deterministic hash heads for each of bigrams and trigrams. Its roughly 51.2B parameters are projected, gated against four residual streams, and augmented by a dilated local convolution. Under a fixed N-gram parameter budget, the report finds one layer sufficient and selects layer 2 so host prefetch can overlap layer 1; splitting capacity across two layers gives no consistent downstream benefit. With MoE capacity held fixed, increasing vocabulary from 20× to 200× the base vocabulary lowers loss monotonically while downstream scores saturate or fluctuate; under a fixed total parameter budget, a 10× allocation has the lowest loss but no clear downstream advantage over MoE-only. The implementation does not establish the reported host-offload path; see [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md).[^qwen38-next-config][^qwen38-next-modeling][^qwen38-next-report]
- **TN-gram**, **Lngram**, and tokenizer-agnostic Engram are described in the overview as later work on factor sharing/collision reduction, latent rather than token-ID keys, and tokenizer portability, respectively.[^ngram-embedding-overview-2026]

The overview also places fastText character n-grams and CANINE among earlier related representation work. **SuperBPE** is a nearby but different choice: it makes frequent multiword spans tokenizer tokens rather than retaining base tokens and adding an auxiliary n-gram lookup.[^ngram-embedding-overview-2026]

## Capacity and systems trade-offs

The proposed benefit is to allocate many parameters to sparse lookups without proportional dense arithmetic per token. It does **not** imply that those parameters are free: table size, lookup bandwidth, collision behavior, and accelerator/host placement are system constraints. Token-ID n-gram keys also couple the memory to a tokenizer unless the design explicitly avoids that coupling.[^ngram-embedding-overview-2026]

LongCat’s technical report now supplies a controlled comparison for its own architecture, but its high-sparsity advantage and allocation threshold remain configuration-bound. MoE sparsifies conditional FFN computation; N-gram embedding supplies sparse local-pattern representation lookup. Their quality, memory, communication, and activation costs still need matched measurement in each deployment setting.[^longcat-embedding-scaling-2026]

## Evidence limits

This page began from one secondary Vietnamese overview. The Over-Encoding, SCONE, Engram, and LongCat embedding-scaling sources have since been independently compiled; their source-specific mechanisms and measurements are primary evidence in their linked pages. LongCat-2.0 adds direct model-card evidence for its 135B allocation but not a technical mechanism or controlled comparison. Other overview-linked papers remain uninspected, so their architecture details, dates, and comparisons remain attributed to the overview rather than independently verified.[^ngram-embedding-overview-2026][^longcat-embedding-scaling-2026][^longcat-2-card-2026]

## Relationships

- **Contrasts with:** [Foundations for training a bigram language model](foundations-for-training-a-bigram-language-model.md): a bigram model directly predicts from the preceding token, while this method supplies auxiliary representations to a Transformer.
- **Related sparse-capacity mechanism:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md). Both distinguish total from per-token-active capacity, but their execution and systems costs differ.
- **Modifies the input side of:** [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md).
- **Primary-source instances:** [Over-Encoding hierarchical n-gram input embeddings](over-encoding-hierarchical-n-gram-input-embeddings.md), with its [evaluation and systems limits](over-tokenized-transformer-evaluation-and-systems-trade-offs.md); [SCONE scalable contextualized offloaded n-gram embeddings](scone-scalable-contextualized-offloaded-n-gram-embeddings.md), with its [evaluation and serving trade-offs](scone-evaluation-and-serving-trade-offs.md); [Engram conditional-memory architecture](engram-conditional-memory-architecture.md), with its [evaluation and serving trade-offs](engram-evaluation-and-serving-trade-offs.md); and the [LongCat allocation study](n-gram-embedding-scaling-versus-moe-expert-scaling.md).

[^ngram-embedding-overview-2026]: “N-gram embeddings in LLM” (Vietnamese research overview), [raw source](../raw/N-gramembeddingsinLLM.md); it links Over-Tokenized Transformer (2025), SCONE (2025), Byte Latent Transformer (2025), Engram and related 2026 work, fastText, CANINE, and SuperBPE.

[^over-tokenized-transformer-2025]: Hongzhi Huang et al., “Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling,” ICML 2025, [LaTeX source](../raw/2501.16975_Over-TokenizedTransformer/main.tex), Sections 2–4.

[^scone-2025]: Da Yu et al., “Scaling Embedding Layers in Language Models,” [LaTeX source](../raw/2502.01637_ScalingEmbeddingLayersinLanguageModels/main.tex), Sections 1–4 and Appendix “Additional Experiments.”

[^conditional-memory-2026]: Xin Cheng et al., “Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models,” [LaTeX source](../raw/2601.07372_ConditionalMemoryviaScalableLookup/main.tex), Sections 1–2.

[^longcat-2-card-2026]: Meituan LongCat team, “LongCat-2.0,” [model card](../raw/LongCat-2.0.md), N-gram Embedding section.

[^longcat-flash-lite-card-2026]: Meituan LongCat team, “LongCat-Flash-Lite,” [model card](../raw/LongCat-Flash-Lite.md), Model Introduction and Key Features.

[^qwen38-next-config]: Qwen Team, “Qwen3.8-Flash-Next checkpoint configuration,” [config](../raw/Qwen3.8-Flash-Next/config.json), Per-Layer Embedding fields.

[^qwen38-next-modeling]: Qwen Team and Hugging Face, “Qwen4-Exp Transformers modeling implementation,” [source](../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py), `Qwen4ExpTextNGramEmbedding` and `Qwen4ExpTextPLELayer`.

[^qwen38-next-blog]: Qwen Team, “Qwen3.8-Flash-Next,” [release blog](../raw/Qwen3.8-Flash-Next/blog.md), N-gram Embedding section.

[^qwen38-next-report]: Qwen Team, “On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability,” [technical report](../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md), Section 2.3 and Tables 7–9.
