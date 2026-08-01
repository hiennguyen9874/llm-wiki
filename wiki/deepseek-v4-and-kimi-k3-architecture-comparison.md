---
type: Synthesis
title: DeepSeek-V4 and Kimi K3 architecture comparison
description: DeepSeek-V4 compresses token-addressable attention throughout, while Kimi K3 combines fixed-state recurrent attention with periodic global latent attention, producing distinct long-context, residual, MoE, and multimodal trade-offs.
tags: [comparison, deepseek-v4, kimi-k3, long-context, mixture-of-experts, hybrid-attention]
status: draft
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T00:00:00Z }
sources:
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# DeepSeek-V4 and Kimi K3 architecture comparison

Both reported models are million-token MoE systems, but their central long-context mechanisms differ. DeepSeek-V4 retains token-derived memory in learned compressed entries and retrieves it sparsely or densely; Kimi K3 moves most sequence mixing into fixed-state Kimi Delta Attention (KDA), retaining global token-addressable attention only periodically. Consequently, V4's primary trade-off is lossy KV aggregation and sparse-selection overhead, whereas K3's is recurrent-state interference mitigated by periodic MLA retrieval.[^deepseek-v4-2026][^kimi-k3-2026]

## Comparison

| Dimension | DeepSeek-V4 | Kimi K3 |
|---|---|---|
| Reported scale | Pro: 1.6T total / 49B active, 61 layers, width 7,168; Flash: 284B / 13B, 43 layers, width 4,096 | 2.78T total / 104.2B active, 93 backbone layers |
| Sequence mixing | Interleaves compressed sparse attention (CSA: 4-token compression, top-$k$ retrieval) and heavily compressed attention (HCA: 128-token compression, dense attention), each with a 128-token uncompressed window | Repeats three KDA layers then one global NoPE gated MLA layer, plus a final MLA: 69 KDA and 24 MLA layers |
| Long-context state | Compressed token-derived KV entries still grow with sequence length; CSA/HCA reduce their number and use FP8/BF16 storage | KDA has fixed-size recurrent state; the 24 MLA layers retain compressed but sequence-growing per-token state |
| Position handling | Partial RoPE in attention projections | No explicit position encoding in MLA; KDA's learned recurrence supplies position/recency behavior |
| Residual/depth pathway | Four-channel manifold-constrained Hyper-Connections (mHC), with doubly stochastic residual mixing | Block Attention Residuals retrieves selectively among block-level depth representations |
| MoE | Every block: one shared expert plus six selected routed experts; first three layers use hash routing | All but first FFN: two shared experts plus top-16 of 896 routed latent experts, operating at compact latent width |
| Modality | The retrieved architecture specification describes a language long-context MoE family | Native text–image–video system: a from-scratch 27-layer MoonViT-V2 feeds the shared backbone |

## Architectural implications

- **V4 optimizes compressed global retrieval.** It preserves a representation for remote token groups in every attention layer, so remote access is compressed—not replaced by a fixed state. This favors a uniform attention-centric design, but information beyond the local window is necessarily aggregated and CSA additionally depends on the indexer selecting relevant groups.[^deepseek-v4-2026]
- **K3 partitions retrieval by timescale and depth.** KDA provides cheap recurrent mixing and recency behavior in three quarters of its attention layers; MLA periodically restores unrestricted token-level interaction; AttnRes independently retrieves useful intermediate transformations across depth. This provides several complementary memory paths, but does not make the complete model's context state constant-size.[^kimi-k3-2026]
- **Their MoE scaling choices are not directly comparable by parameter count.** V4's fine-grained DeepSeekMoE activates six routed experts plus one shared expert; K3 routes through a much larger 896-expert latent pool and activates 16, while its routed branch is narrower. Differences in active parameters, width, expert form, data, and training recipe prevent attributing quality or cost differences to routing alone.[^deepseek-v4-2026][^kimi-k3-2026]

## Evidence limits

This is a design comparison, not a head-to-head performance verdict. The V4 technical report and its wiki concepts are `draft`; both primary reports provide author-run measurements, with no independent replication or matched V4–K3 benchmark, hardware, serving, or component-ablation study available here. Reported one-million-token support does not establish reliable retrieval from every position or modality.[^deepseek-v4-2026][^kimi-k3-2026]

## Relationships

- **Synthesizes:** [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md) and [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Contrasts:** [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md) with [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) plus periodic [Multi-head Latent Attention](multi-head-latent-attention.md).
- **Contrasts:** [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) with [Attention Residuals](attention-residuals.md).

[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Sections 1–3.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 1–3.
