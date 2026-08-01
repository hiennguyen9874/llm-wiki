---
type: Concept
title: Kimi K3 hybrid retrieval architecture
description: Kimi K3 combines fixed-state KDA, periodic global MLA, depth-wise Attention Residuals, sparse latent experts, and a native vision pathway in a 2.8T-parameter model.
tags: [kimi-k3, hybrid-attention, mixture-of-experts, multimodal]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:00:00Z }
sources:
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# Kimi K3 hybrid retrieval architecture

Kimi K3 is a native multimodal Mixture-of-Experts model with 2.78T total and 104.2B activated parameters, 93 backbone layers, and a reported context window up to one million tokens. Its architecture divides information flow among fixed-state sequence memory, periodic global token retrieval, selective depth retrieval, and sparse channel mixing rather than relying on one mechanism for every role.[^kimi-k3-2026]

## Backbone and division of labor

Each repeated block contains three Kimi Delta Attention (KDA) layers followed by one NoPE Gated Multi-head Latent Attention (MLA) layer; an additional MLA layer ends the backbone, giving 69 KDA and 24 MLA layers. Every attention layer is paired with a Stable LatentMoE feed-forward layer except the first dense layer.[^kimi-k3-2026]

| Component | Role | State or capacity behavior |
|---|---|---|
| KDA | Position-sensitive, recency-aware sequence mixing | Fixed-size recurrent state; channel-wise decay and delta correction |
| Gated MLA | Unrestricted global content interaction | Compressed per-token KV state that grows with context |
| Block AttnRes | Selective retrieval over model depth | Caches block-level representations rather than every layer output |
| Stable LatentMoE | Sparse channel mixing | Two shared experts plus top-16 of 896 routed latent experts |
| MoonViT-V2 | Image and video encoding | Projects visual tokens into the shared backbone |

The hybrid is complementary: bounded KDA state reduces sequence-growing cache pressure but can lose token-isolated detail, while periodic MLA preserves global token-addressable retrieval. No explicit positional encoding is applied to MLA; the report attributes position sensitivity to KDA and claims direct extension to 1M contexts without RoPE rescaling.[^kimi-k3-2026]

## KDA changes from Kimi Linear

K3 retains the channel-wise delta recurrence but lower-bounds each log-decay at $g_{\min}=-5$. Over a 16-token tile this bounds reciprocal decay rescaling below $e^{80}$, within BF16 range, allowing diagonal as well as off-diagonal causal tiles to use dense Tensor Core matrix multiplication. It also replaces Kimi Linear’s low-rank output gate with a full-rank, input-dependent channel gate.[^kimi-k3-2026]

## Scale and efficiency claim

The report attributes an approximately $2.5\times$ overall scaling-efficiency improvement over Kimi K2 to the combined architecture, data, and training recipe, measured through fitted held-out out-of-distribution validation-loss curves. Because the changes were evaluated jointly, this does not isolate the causal contribution of KDA, AttnRes, Stable LatentMoE, data, optimizer, or schedule.[^kimi-k3-2026]

## Relationships

- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) through KDA.
- **Uses:** [Attention Residuals](attention-residuals.md) for depth-wise retrieval.
- **Uses:** [Stable LatentMoE and Quantile Balancing](stable-latentmoe-and-quantile-balancing.md) for sparse channel capacity.
- **Mitigates limits of:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) with periodic global MLA.
- **Trained by:** [Kimi K3 native multimodal pre-training](kimi-k3-native-multimodal-pre-training.md).
- **Operationalized by:** [Kimi K3 lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md).

## Evidence limits

The primary technical report specifies the architecture and reports ablations and scaling curves, but does not provide component-isolated evidence for the headline efficiency gain. The model’s global attention remains sequence-growing, so the hybrid does not make all long-context state constant size. The earlier secondary explainer is retained as provenance but is superseded here by the primary specification.[^gpt2-kimi3-2026][^kimi-k3-2026]

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Abstract and Sections 1–3.
