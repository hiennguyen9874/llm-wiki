---
type: Synthesis
title: GLM-5 and Kimi K3 architecture comparison
description: GLM-5 uses sparse token-addressable MLA/DSA throughout, whereas Kimi K3 combines recurrent KDA with periodic MLA, depth retrieval, latent MoE, and a native vision pathway.
tags: [glm-5, kimi-k3, architecture-comparison, long-context, mixture-of-experts]
status: stable
created: 2026-08-15
sources:
  - id: glm5-report-2026
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: glm5-code-2026
    resource: ../raw/glm-moe/modular_glm_moe_dsa.py
    title: Hugging Face GLM-MoE-DSA modular implementation
  - id: kimi-linear-modeling-2026
    resource: ../raw/kimi-k3-sources/modeling_kimi_linear.py
    title: Kimi K3 text-backbone reference modeling code
---

# GLM-5 and Kimi K3 architecture comparison

GLM-5 and Kimi K3 are both sparse MoE systems for long context, but make opposite primary memory choices. GLM-5 retains compressed, **token-addressable** MLA state in every backbone layer and uses DSA to select a token subset before attention. Kimi K3 puts **fixed-state recurrent** KDA in most sequence-mixing layers, then periodically restores unrestricted token retrieval with MLA; it further adds retrieval across depth and a native vision path.[^glm5-report-2026][^kimi-k3-2026]

| Dimension | GLM-5 | Kimi K3 | Architectural consequence |
|---|---|---|---|
| Scale | 744B total; 40B active; 78 backbone layers | 2.78T total; 104.2B active; 93 backbone layers | These are not matched-capability or latency comparisons. |
| Sequence memory | MLA in the backbone; DSA indexer selects up to 2,048 prior token entries for core attention | 69 KDA layers with bounded recurrent state; 24 global NoPE Gated MLA layers | GLM prioritizes sparse direct token lookup; K3 prioritizes cheap recurrent mixing, with periodic global correction. |
| Context-state growth | MLA cache remains linear in token count; DSA reduces main attention reads but retains token state and an indexer pass | KDA state is fixed-size, but MLA-layer caches and AttnRes prefill state still grow with sequence length | Neither model has constant-size end-to-end long-context state. |
| Positional treatment | MLA uses a decoupled RoPE path; its DSA indexer uses interleaved RoPE | MLA is NoPE; KDA supplies position-sensitive and recency-aware behavior | K3 avoids MLA position-rescaling during its stated context extension; this does not by itself establish reliable retrieval at every position. |
| Sparse FFN | 256 routed experts, top-8, plus one always-on shared expert | 896 latent routed experts, top-16, plus two full-width shared experts | K3 places more total and active expert capacity behind a latent bottleneck; GLM uses conventional-width expert tensors. |
| Additional retrieval axis | Token selection only; ordinary residual-stream treatment in the available specification | Block Attention Residuals retrieve learned mixtures of prior block representations across depth | K3 separates sequence-position, model-depth, and channel-capacity retrieval. |
| Modality | The reviewed GLM-5 architecture sources document a text MoE backbone; they do not establish a native vision pathway | Joint text/image/video pre-training with a from-scratch MoonViT-V2 encoder | The comparison is asymmetric: native multimodality is documented for K3, not established for GLM-5 by the reviewed sources. |

## How to read the trade-off

- **GLM-5:** Selective attention preserves direct access to chosen historical tokens. Its cost reduction depends on index quality, sparse-attention kernels, and workload; DSA is not a fixed-state memory mechanism.[^glm5-report-2026][^glm5-code-2026]
- **Kimi K3:** KDA avoids a growing cache in most layers, but recurrent state superposes past associations and can suffer interference. Periodic MLA compensates by retaining exact token-addressable global retrieval at those layers.[^kimi-k3-2026][^kimi-linear-modeling-2026]
- **MoE inference:** Lower active parameters does not imply lower latency: total weight residency, expert dispatch/all-to-all, batching, context length, and kernels remain material. K3’s larger activated capacity therefore cannot be read as a simple quality or cost advantage over GLM-5.

## Evidence limits

The figures and mechanisms above come from separate author reports and public reference implementations, with different scale, data, optimization, hardware, context curricula, and evaluation suites. They support a structural comparison—not a controlled attribution of quality, training efficiency, or serving cost to MLA/DSA versus KDA/MLA. The GLM reference code is not production serving code; K3's public multimodal and text implementations also have documented production-path and modality discrepancies.[^glm5-report-2026][^kimi-k3-2026][^glm5-code-2026][^kimi-linear-modeling-2026]

## Relationships

- **Compares:** [GLM-5 architecture, pre-training, and systems](glm-5-architecture-pretraining-and-systems.md) and [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Contrasts:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md) with [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) as their primary long-context memory mechanisms.
- **Uses context from:** [Attention Residuals](attention-residuals.md), [Multi-head Latent Attention](multi-head-latent-attention.md), and [Stable LatentMoE and Quantile Balancing](stable-latentmoe-and-quantile-balancing.md).

[^glm5-report-2026]: GLM-5 Team, “GLM-5: from Vibe Coding to Agentic Engineering,” arXiv:2602.15763v2, [main source](../raw/arXiv-2602.15763v2/0_main.tex), pre-training section, and architecture appendix.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2–3.

[^glm5-code-2026]: Hugging Face, “GLM-MoE-DSA modular implementation,” [source](../raw/glm-moe/modular_glm_moe_dsa.py), indexer, attention, router, MoE, decoder, and model classes.

[^kimi-linear-modeling-2026]: Moonshot AI Team, DeepSeek-AI, and Hugging Face, “Kimi K3 text-backbone reference modeling code,” [source](../raw/kimi-k3-sources/modeling_kimi_linear.py), KDA cache and attention, MLA cache, MoE, and Block AttnRes classes.
