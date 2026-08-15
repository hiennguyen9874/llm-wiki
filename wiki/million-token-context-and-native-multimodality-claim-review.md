---
type: Synthesis
title: Review of claims about million-token context and native multimodality
description: A claim-by-claim review distinguishes advertised context capacity, token-addressable retrieval, and long-context reliability, and rejects treating a modular vision path as incompatible with native multimodal training.
tags: [long-context, multimodal, attention, evidence-review]
status: stable
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T13:33:13+07:00 }
sources:
  - id: vaswani-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: DeepSeek-V3 Technical Report
  - id: flashattention-2022
    resource: ../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex
    title: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
  - id: qwen35-config
    resource: ../raw/Qwen3.5-27B/config.json
    title: Qwen3.5-27B checkpoint configuration
  - id: qwen35-modeling
    resource: ../raw/Qwen3.5-27B/modeling_qwen3_5.py
    title: Qwen3.5 Transformers reference modeling implementation
---

# Review of claims about million-token context and native multimodality

The quoted statement mixes three non-equivalent properties: a system accepting a given input length, its ability to retrieve individual old tokens, and reliable task performance across that length. A million-token claim is not thereby proof of lossless all-token retrieval, but using a non-full-attention mechanism does not make the advertised context window fictitious.

## Claim-by-claim verdict

| Claim | Verdict | Evidence-bounded review |
|---|---|---|
| “No model truly has a 1M-token context; full/real context stops at 128K.” | **False as an absolute claim; ‘truly’ is undefined.** | Kimi K3 reports a 1M window and a training curriculum reaching 1M; its backbone combines fixed-state KDA with periodic global, token-addressable MLA. DeepSeek-V4 also reports progressive training to 1M, but is a draft, author-reported result. DeepSeek-V3’s 128K extension is one model configuration, not a Transformer-wide ceiling.[^kimi-k3-2026][^deepseek-v4-2026][^deepseek-v3-2024] |
| “Anything above 128K is merely interpolation, RoPE scaling, or sparse-attention trickery.” | **False and reductive.** | RoPE extrapolation/scaling is one context-extension technique, and it needs empirical validation. But K3 reports NoPE MLA plus recurrent KDA and long-context training; V4 uses learned KV compression and sparse/dense retrieval over compressed entries, plus long-context training. These are genuine architectural trade-offs, not evidence-free claims of exact full attention.[^kimi-k3-2026][^deepseek-v4-2026] |
| “A real Transformer must retain unrestricted, exact token-level full attention.” | **A possible strict definition, not a standard definition of a context window.** | Full self-attention gives direct token-to-token paths but has quadratic full-sequence arithmetic. MLA retains token-addressable softmax attention with a smaller per-token cache; recurrent/linear paths have bounded state but can suffer interference; hybrids deliberately combine both. Calling only the first type “real” is a terminological choice that hides the trade-off.[^vaswani-2017][^kimi-k3-2026] |
| “Multimodality is just easily bolting any image encoder onto Qwen.” | **Partly true architecturally, misleading operationally.** | A vision encoder plus projector into the language-token space is a common composition. The supplied Qwen3.5 path uses a 27-block vision encoder, spatial merge, projection from vision width 1,152 to text width 5,120, then replaces media-placeholder embeddings. But an arbitrary encoder is not interchangeable without compatible tokenization, positional handling, connector training, and end-to-end data/alignment.[^qwen35-config][^qwen35-modeling] |
| “If a model has a separate vision encoder/projector, it is not native multimodal, only a module.” | **False dichotomy.** | Components do not determine whether training is native. Kimi K3 has a separate from-scratch 27-layer vision encoder and a projection into its language backbone, while reporting joint text–image–video pre-training from the start under one next-token objective. It is therefore modular in implementation and native in the stated training/integration sense.[^kimi-k3-2026] |
| Specific claims about Claude 4.8 / Claude Fable 5 architecture, a small image encoder, or “just over 1K” projector width. | **Unverified by this wiki.** | The wiki has no primary Anthropic architecture/model-card source for those assertions. A third-party author report compares Claude Opus 4.6 Max on 1M benchmarks, but that is not documentation of Claude’s context contract or multimodal internals.[^deepseek-v4-2026] |

## The technical distinction that resolves the dispute

1. **Declared context window**: maximum input a model/service accepts and processes (for example, 128K, 262K, or 1M).
2. **Retrieval granularity**: full attention or MLA can retain a separately addressable representation per prior token; sparse selection or compression reduces which representations are read or how precisely they are retained.
3. **Reliability**: benchmarked ability to find, copy, reason over, or integrate evidence across positions. A window size alone does not establish this.

Full attention is exact with respect to its softmax formula, but its full-sequence arithmetic remains quadratic; FlashAttention reduces intermediate-memory traffic, not that arithmetic. Conversely, compression, sparse selection, and recurrent state each introduce different information-access or capacity limits. They should be measured, not dismissed by label.[^vaswani-2017][^flashattention-2022]

## Better phrasing

A defensible version is: “A 1M-token context claim does not by itself prove uniform, lossless, token-level retrieval across one million positions. Many long-context models trade exact all-token access for compression, sparsity, or recurrent memory; others retain periodic global token attention. Check the architecture, long-context training, and position-specific evaluations rather than treating 128K as a universal boundary.”

## Relationships

- **Synthesizes:** [Self-attention computational profile](self-attention-computational-profile.md), [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), [Multi-head Latent Attention](multi-head-latent-attention.md), and [Rotary position embedding (RoPE)](rotary-position-embedding.md).
- **Evaluates claims about:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), [Kimi K3 native multimodal pre-training](kimi-k3-native-multimodal-pre-training.md), [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md), and [Qwen3.5-27B checkpoint architecture and implementation](qwen3-5-27b-checkpoint-architecture.md).

## Evidence limits

Kimi K3 and DeepSeek-V4 one-million-token claims are primarily author-reported; V4 is explicitly `draft` in this wiki. Neither proves reliable use of every token, position, modality, and workload at 1M. The Qwen page documents supplied configuration and reference code, not its training or quality. No primary Anthropic source in the wiki supports the quoted Claude-specific implementation details.

[^vaswani-2017]: Vaswani et al., [Attention Is All You Need](../raw/arXiv-1706.03762v7/ms.tex), especially its self-attention complexity comparison; see also [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md).
[^deepseek-v3-2024]: DeepSeek-AI, [DeepSeek-V3 Technical Report](../raw/arXiv-2412.19437v2/main.tex), context extension from 4K to 32K and 128K with YaRN.
[^flashattention-2022]: Dao et al., [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex), exact tiled attention and its unchanged quadratic arithmetic.
[^kimi-k3-2026]: Kimi Team, [Kimi K3: Open Frontier Intelligence](../raw/arXiv-2607.24653v1/main.tex); see the corresponding [architecture](kimi-k3-hybrid-retrieval-architecture.md) and [multimodal pre-training](kimi-k3-native-multimodal-pre-training.md) concepts.
[^deepseek-v4-2026]: DeepSeek-AI, [DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence](../raw/arXiv-2606.19348v1/main.tex); author report, reflected in a `draft` concept.
[^qwen35-config]: Qwen Team, [Qwen3.5-27B checkpoint configuration](../raw/Qwen3.5-27B/config.json).
[^qwen35-modeling]: Qwen Team and Hugging Face, [Qwen3.5 reference modeling implementation](../raw/Qwen3.5-27B/modeling_qwen3_5.py).
