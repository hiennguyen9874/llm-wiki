---
type: Synthesis
title: Causal Encoder-Decoder compared with Transformer architectures
description: CED reorganizes one causal language-model stream into a causal encoder and decoder so prompt-wide decoder global KV can be projected from the encoder boundary, unlike both layer-local decoder-only caching and the original source–target encoder–decoder Transformer.
tags: [causal-encoder-decoder, decoder-only-transformer, encoder-decoder, kv-cache, prefill]
status: draft
created: 2026-09-13
generated: { by: llm-wiki-agent/1, at: 2026-09-13T02:56:16Z }
sources:
  - id: deepseek-v41-tech-report
    resource: ../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: radford-generative-pre-training-2018
    resource: ../raw/gpt.pdf
    title: Improving Language Understanding by Generative Pre-Training
---

# Causal Encoder-Decoder compared with Transformer architectures

DeepSeek-V4.1-Flash's Causal Encoder–Decoder (CED) is best understood as an inference-oriented reorganization of a single causal language-model backbone, not as a return to the original Transformer’s source–target architecture. Its lower half causally encodes the whole prompt; each upper decoder layer derives global KV through layer-specific projections of the encoder-boundary states, while retaining layer-local sliding-window attention. This lets long prompt tokens avoid full upper-half computation during prefill, but new output tokens still traverse both halves during autoregressive decode.[^deepseek-v41-tech-report]

## Three information-flow patterns

| Dimension | Standard decoder-only Transformer | CED in DeepSeek-V4.1-Flash | Original Transformer encoder–decoder |
|---|---|---|---|
| Logical sequences | One combined prompt/continuation stream | One combined prompt/continuation stream | Separate source and target streams |
| Encoder visibility | No encoder | Causal: position $i$ sees only $j\le i$ | Bidirectional over the complete source |
| Decoder self-attention | Causal | Causal local SWA plus causal global memory | Causal over target prefix |
| Global K/V source | Every layer’s own hidden states | Encoder-boundary state $H_{L/2}$, with layer-dependent projections | Encoder outputs through cross-attention projections |
| Classic source–target cross-attention | No | No; the encoder/decoder split remains inside one causal stream | Yes |
| Primary design goal | General next-token modeling | Reduce long-prompt prefill and KV costs | Conditional sequence transduction |
| Prompt/source processing | All prompt positions through all $L$ layers | All positions through lower $L/2$; bounded recent replay through upper $L/2$ for local state | Full source through encoder once |
| Output generation | Every new token traverses all layers | Every new token traverses causal encoder and decoder | Every target token traverses decoder and reads fixed encoder memory |

The shared word “encoder” therefore hides different semantics: CED’s encoder preserves autoregressive causality within the language stream, whereas the 2017 Transformer encoder contextualizes a separately supplied source bidirectionally.[^deepseek-v41-tech-report][^vaswani-transformer-2017]

## CED mechanism

Let a causal backbone have $L$ layers and hidden states $H_l$. CED designates layers $1\ldots L/2$ as the causal encoder. For every upper decoder layer $l>L/2$, its global compressed KV entries and compression weights are not generated from that layer’s own prompt states. Instead:

$$
C_l=H_{L/2}W_l^{KV},\qquad Z_l=H_{L/2}W_l^Z.
$$

Although all upper layers share the same encoder-boundary representation as input to KV construction, their projection weights remain layer-dependent. The global memories are therefore not necessarily numerically identical across decoder layers.[^deepseek-v41-tech-report]

The decoder query is still formed at its current depth and uses this projected global memory. In parallel, every layer constructs local SWA K/V from its own hidden state. CED thus deliberately combines:

1. **shallow-to-build, prompt-wide global memory** from $H_{L/2}$; and
2. **deep, layer-local recent memory** from the bounded sliding window.[^deepseek-v41-tech-report]

For DeepSeek-V4.1-Flash, $L=40$: 20 causal-encoder layers followed by 20 decoder layers. The first two layers are SWA-only; later layers use CSA2 global attention alongside SWA. CSA2 additionally shares main KV and indexing state across selected layers, and its sparse indexer limits which global entries a query reads. Those are complementary mechanisms rather than consequences of CED itself.[^deepseek-v41-tech-report]

## Prefill and decode

For a prompt of length $N$ and SWA replay window $W$:

- a conventional causal stack performs roughly $NL$ layer-token evaluations before attention-specific costs;
- CED runs all $N$ prompt tokens through the lower $L/2$ layers;
- upper-layer global KV is projected cheaply from $H_{L/2}$;
- only the last $W$ prompt tokens are replayed through the upper $L/2$ layers to reconstruct decoder-local SWA state.

The report therefore writes the layer-token prefill cost as

$$
O(NL/2+WL/2)\approx O(NL/2),\qquad N\gg W.
$$

This is not a universal dense-attention complexity claim: DeepSeek-V4.1-Flash also uses compressed sparse attention. It describes how many prompt tokens require expensive traversal through each half of this particular stack.[^deepseek-v41-tech-report]

Bounded replay is approximate. Exact reconstruction of stacked SWA dependencies would require a much longer replay; CED truncates those dependencies to the replay segment. The report says this had negligible quality impact and simulates the replay during post-training, but provides no independent audit of edge cases.[^deepseek-v41-tech-report]

During one-token decode, the new token must pass through both halves: the encoder produces its boundary state and new global-memory contribution, then decoder layers compute the final representation and logits. CED therefore primarily attacks input-heavy prefill, not the sequential dependency of autoregressive output generation.[^deepseek-v41-tech-report]

## Comparison with decoder-only Transformers

A GPT-style decoder-only Transformer serializes prompt and response into one stream. Every layer applies causal self-attention and an FFN; each layer ordinarily derives and caches its own K/V from its own hidden states.[^radford-generative-pre-training-2018]

CED preserves the same one-stream next-token semantics and causal no-future-leakage rule. It changes where upper-layer global memory comes from and exploits the fact that inference normally needs prompt cache state rather than final logits for every old prompt position. The trade is:

- **Gain:** nearly half of long-prompt upper-stack computation can be avoided under the report’s accounting.
- **Gain:** CED enables decoder global cache construction from one encoder-boundary representation; CSA2 can then compress/share that state further.
- **Cost:** upper layers no longer construct prompt-wide global KV from their own depth-specific hidden states.
- **Cost:** local deep state needs approximate bounded replay.
- **No gain:** each newly generated token still traverses the full causal encoder and decoder.

The reported 890-byte global-cache figure belongs to the complete DeepSeek-V4.1-Flash design—CED plus CSA2 reuse/compression and FP4 storage—not to CED alone.[^deepseek-v41-tech-report]

## Comparison with the original Transformer

The original Transformer first maps a complete source sequence to encoder memory using bidirectional self-attention. Each target decoder layer then performs causal target self-attention, cross-attention whose queries come from decoder states and whose K/V come from encoder outputs, and a position-wise FFN. This explicitly models $p(y\mid x)$ over separate source $x$ and target $y$.[^vaswani-transformer-2017]

CED is superficially similar because an upper stack reads memory produced by a lower stack, but the analogy stops there:

- CED has one vocabulary stream and one autoregressive ordering, not separate source and target sequences.
- Its lower encoder is causal, not bidirectional.
- Its split is primarily a cache/prefill computation boundary inside a language model.
- Its decoder’s global memory is layer-specifically projected from $H_{L/2}$, while local SWA still comes from each decoder layer.
- It does not introduce the original architecture’s explicit source–target cross-attention stage.

A useful shorthand is: **original encoder–decoder separates roles by sequence; CED separates work by depth and cache responsibility.**[^deepseek-v41-tech-report][^vaswani-transformer-2017]

## Selection intuition

- Use a standard **decoder-only** formulation when architectural simplicity, broad runtime support, and uniform prompt/continuation processing matter most.
- Use the original **encoder–decoder** pattern when input and output are naturally distinct sequences and bidirectional source understanding plus explicit target-to-source retrieval is desirable.
- CED is attractive for **very long, input-heavy autoregressive workloads** with repeated prefill/cache misses, provided the runtime supports its split cache path and the quality impact of projected global KV and bounded replay is acceptable.

These are architectural implications, not universal quality rankings. DeepSeek-V4.1-Flash’s efficiency and quality results remain vendor-reported; the released configuration and reference implementation verify important structural choices but not production latency or all replay edge cases.[^deepseek-v41-tech-report]

## Relationships

- **Compares:** [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md).
- **Compares:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md).
- **Explains:** [DeepSeek-V4.1-Flash architecture and pretraining](deepseek-v4-1-flash-architecture-and-pretraining.md)’s CED split and prefill/cache trade-off.
- **Uses:** [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md) through DeepSeek-V4.1-Flash’s CSA2 implementation; CSA2 is not part of the generic CED definition.

[^deepseek-v41-tech-report]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” [technical report](../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md), Sections 2.1–2.3 and 3.2.2.
[^vaswani-transformer-2017]: Ashish Vaswani et al., “Attention Is All You Need,” bundled [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), architecture sections.
[^radford-generative-pre-training-2018]: Alec Radford et al., “Improving Language Understanding by Generative Pre-Training,” bundled [PDF](../raw/gpt.pdf), model architecture and objective.
