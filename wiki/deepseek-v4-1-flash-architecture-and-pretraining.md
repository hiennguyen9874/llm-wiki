---
type: Concept
title: DeepSeek-V4.1-Flash architecture and pretraining
description: DeepSeek-V4.1-Flash is a reported 552B-backbone multimodal MoE that uses a 20-layer causal encoder and 20-layer decoder, CSA2 cross-layer cache sharing, FP4 KV storage, Engram memory, and input-heavy prefill/decode activation asymmetry.
tags: [deepseek-v4-1, mixture-of-experts, causal-encoder-decoder, sparse-attention, kv-cache, multimodal]
status: draft
created: 2026-09-11
generated: { by: llm-wiki-agent/1, at: 2026-09-11T05:35:45Z }
sources:
  - id: deepseek-v41-tech-report
    resource: ../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
  - id: deepseek-v41-flash-readme
    resource: ../raw/DeepSeek-V4.1-Flash/README.md
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
  - id: deepseek-v41-config
    resource: ../raw/DeepSeek-V4.1-Flash/config.json
    title: DeepSeek-V4.1-Flash checkpoint configuration
  - id: deepseek-v41-reference-model
    resource: ../raw/DeepSeek-V4.1-Flash/inference/model.py
    title: DeepSeek-V4.1-Flash minimal inference model
---

# DeepSeek-V4.1-Flash architecture and pretraining

DeepSeek-V4.1-Flash is an author-described native multimodal MoE with a 552B-parameter backbone and a one-million-token context. Its 40-layer Causal Encoder-Decoder (CED) divides computation into a 20-layer causal encoder and 20-layer decoder: decoder global KV is projected from the final encoder states rather than separately retained from every decoder layer. The card reports 8B activated parameters per token during prefill and 16B during decode, making the design explicitly asymmetric for input-heavy workloads.[^deepseek-v41-flash-readme]

## Causal Encoder-Decoder and cache design

CED computes prompt-wide global state through the 20-layer causal encoder and projects every decoder layer’s global KV from the encoder’s final hidden states. Decoder layers still compute layer-local SWA over a bounded replay segment, so for prompt length $N$ much larger than the 128-token window the report gives prefill complexity of approximately $O(NL/2)$ rather than $O(NL)$. This savings is architectural but approximate SWA reconstruction remains a quality boundary.[^deepseek-v41-tech-report]

**Compressed Sparse Attention 2 (CSA2)** gives each attention layer one static mode:

- **Full** computes the main KV, indexer keys, and sparse indices.
- **Reindex** shares the main KV but recomputes indexing.
- **Reuse** shares both representations and reuses earlier top-$k$ indices.

A decoder-side hierarchical sparse indexer has the first Full layer score the complete visible range, select up to 2,048 eight-entry blocks, and expose at most 16,384 candidates to later Reindex layers; those layers then choose their own top-512 entries. The first scan remains context-linear, while later scans are bounded by the candidate pool. Main KV uses E2M1 FP4 with one E4M3 scale per 16 channels after RoPE; SWA KV remains FP8. Together, the report claims a global cache footprint of 890 bytes per token, approximately one quarter of DeepSeek-V4-Flash.[^deepseek-v41-tech-report]

The checkpoint config and readable inference code expose the layer schedule. Layers 0–1 are sliding-window-only; layers 2–19 use 2-to-1 compressed KV; layers 20–39 retain one compressed entry per token; and three appended DSpark stages are sliding-window-only. KV sources are layers 2, 8, 14, and 20. Those four also compute indices, while layers 24, 28, 32, and 36 reindex shared KV and intervening layers reuse the last indices. Layer 20 selects up to 2,048 candidate blocks of eight entries before later indexers select top-512 entries. This verifies the released reference path, not production kernel behavior or the README’s byte and latency claims.[^deepseek-v41-config][^deepseek-v41-reference-model]

## Sparse capacity, residuals, and modalities

Each backbone MoE layer has one shared expert and 384 routed experts, selecting six routed experts per token. The architecture also includes 196B parameters of token-lookup Engram conditional memory, a revised **Single-Pass mHC** residual mechanism with a Mega-mHC kernel, and DSpark semi-autoregressive speculative drafting.[^deepseek-v41-flash-readme] The config places Engram tables for n-gram orders 2–4 at layers 1 and 14, uses four residual streams and 20 Sinkhorn iterations, and defines three DSpark stages that draft blocks of five from backbone layers 37–39; those stages use 128 routed experts with three active, plus Markov and confidence heads. The reference implementation exposes DSpark’s forward path but not the speculative verification loop.[^deepseek-v41-config][^deepseek-v41-reference-model]

A from-scratch DeepSeek-ViT uses 2D RoPE and $3\times3$ pixel-unshuffle downsampling; a two-layer MLP projects visual features into embeddings jointly processed with text from the beginning of language-model pretraining. This supports a native-training-path claim, not independent evidence of visual quality.[^deepseek-v41-flash-readme]

## Pretraining

The report describes 45T-token training from scratch: CSA2 starts at 64K and context extends to one million tokens after 34T. The final corpus uses a reported 7:1 text-only-to-multimodal token ratio, replaces overlapping text samples with multimodal versions, and packs with at most $10^{-4}$ padding. The data pipeline filters low-information model output and machine translation, adds recent code and multimodal web/PDF, OCR, chart, grounding, image-code, and computer-use data, but does not disclose dataset inventories, licenses, governance, or contamination measurements.[^deepseek-v41-tech-report]

DeepSeek-ViT is first contrastively trained on about 47B image-text pairs at up to $224\times224$, then autoregressively tuned with a temporary 4B MoE LLM on 236B high-resolution tokens before integration. Backbone training uses a fixed 100.6M-token batch, sparse attention from the start, Muon for linear matrices, AdamW for non-matrix parameters, and momentum plus Sinkhorn balancing for embeddings and the prediction head. These are vendor-reported recipes without training-compute totals or controlled attribution.[^deepseek-v41-tech-report]

## Relationships

- **Extends:** [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md), especially the Flash branch, with CED, CSA2, lower-precision cache storage, and bounded SWA replay.
- **Extends:** [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md) through static Full/Reindex/Reuse modes and hierarchical candidate restriction.
- **Uses:** [Engram conditional-memory architecture](engram-conditional-memory-architecture.md) as a 196B sparse lookup component.
- **Uses:** [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) in a Single-Pass variant that shifts input-mixing coefficients by one block for kernel fusion.
- **Uses:** [DSpark parallel-draft speculative decoding](dspark-parallel-draft-speculative-decoding.md) for semi-autoregressive drafting.
- **Implemented by:** [DeepSeek-V4.1 training, serving, and agent infrastructure](deepseek-v4-1-training-serving-and-agent-infrastructure.md).
- **Evaluated by:** [DeepSeek-V4.1-Flash post-training, evaluation, and interface limits](deepseek-v4-1-flash-post-training-evaluation-and-interface-limits.md).
- **Encoded by:** [DeepSeek-V4.1 chat, tool, and reasoning encoding](deepseek-v4-1-chat-tool-and-reasoning-encoding.md).

## Evidence limits

Architecture, training, activation, cache, and quality figures remain vendor claims. The technical report and its 15 referenced figures were inspectable, while the release configuration and tensor-parallel reference implementation verify important layer and tensor choices. Neither artifact supplies production code, end-to-end serving measurements, training-compute totals, controlled component attribution, or an independent audit; the reference generator remains plain autoregressive sampling and omits DSpark target verification. CSA2 selection errors and approximate SWA reconstruction are explicitly identified as uncharacterized edge-case risks.[^deepseek-v41-tech-report][^deepseek-v41-reference-model]

[^deepseek-v41-tech-report]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” [technical report](../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md), Sections 1–4 and Figures 2–7.

[^deepseek-v41-flash-readme]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” [release README](../raw/DeepSeek-V4.1-Flash/README.md), Introduction, Prompt Encoding, Minimal Inference, and Reproducing DeepSWE Benchmark Results.

[^deepseek-v41-config]: DeepSeek-AI, [DeepSeek-V4.1-Flash checkpoint configuration](../raw/DeepSeek-V4.1-Flash/config.json), text and vision configuration.

[^deepseek-v41-reference-model]: DeepSeek-AI, [DeepSeek-V4.1-Flash minimal inference model](../raw/DeepSeek-V4.1-Flash/inference/model.py), `ModelArgs`, `Indexer`, `Attention`, `DSparkBlock`, and `Transformer`.
