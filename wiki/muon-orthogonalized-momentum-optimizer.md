---
type: Concept
title: Muon orthogonalized-momentum optimizer
description: Muon updates hidden-layer weight matrices using the polar factor of momentum, approximated by Newton–Schulz iterations, rather than AdamW’s element-wise adaptive update.
tags: [muon, optimizer, pre-training, matrix-optimization, newton-schulz]
status: draft
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-26T15:18:15Z }
sources:
  - id: muon-overview-2026
    resource: ../raw/MuonOptimizer.md
    title: Muon Optimizer overview (Vietnamese summary)
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
  - id: glm5-report-2026
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
  - id: nanochat-optim-2026
    resource: ../raw/nanochat/nanochat/optim.py
    title: nanochat combined Muon–AdamW optimizer
  - id: qwen38-next-blog
    resource: ../raw/Qwen3.8-Flash-Next/blog.md
    title: Qwen3.8-Flash-Next release blog
---

# Muon orthogonalized-momentum optimizer

Muon (``MomentUm Orthogonalized by Newton-Schulz'') applies momentum to a hidden-layer weight matrix, then uses an approximation to the momentum matrix's polar factor as its update. Unlike AdamW, which adaptively rescales coordinates, it preserves the momentum's singular-vector directions while approximately equalizing its nonzero singular values.[^muon-overview-2026]

## Matrix update

For momentum $M_t=\mu M_{t-1}+\nabla\mathcal L_t(W_{t-1})$, ideal orthogonalization is

$$
\operatorname{Ortho}(M_t)=UV^\top, \qquad M_t=U\Sigma V^\top.
$$

The update therefore constrains the update's spectral geometry without requiring the weight matrix itself to remain orthogonal. The source describes this as the steepest linearized loss decrease under a spectral-norm constraint; it is an interpretation, not a complete causal explanation of Muon's empirical behavior.[^muon-overview-2026]

## Newton–Schulz approximation

Computing an SVD at every step is impractical, so the reported implementation normalizes $M_t$ by its Frobenius norm and performs about five bf16 Newton–Schulz matrix iterations. Its reported polynomial coefficients are $a=3.4445$, $b=-4.7750$, and $c=2.0315$; these are implementation-specific rather than universal Muon constants. The operations are predominantly matrix multiplications, making them suitable for GPU tensor cores.[^muon-overview-2026]

## Parameter groups and scale

Muon is intended for two-dimensional hidden-layer matrices, including attention projections and MLP matrices. Embeddings, the LM head, normalization gains, biases, and other vector or scalar parameters generally remain in AdamW, making the common setup a hybrid optimizer.[^muon-overview-2026]

For a full-rank $A\times B$ matrix, the source reports an unscaled orthogonalized update RMS of $1/\sqrt{\max(A,B)}$. The LLM-oriented variant multiplies the update by $0.2\sqrt{\max(A,B)}$ so update scale is less shape-dependent and can use AdamW-like learning-rate and weight-decay settings:

$$
W_t=W_{t-1}-\eta_t\left[0.2\sqrt{\max(A,B)}\operatorname{Ortho}(M_t)+\lambda W_{t-1}\right].
$$

The supplied overview reports that weight decay also controlled growing weight and activation scales during long bf16 training.[^muon-overview-2026]

## Qwen3.8-Flash-Next configuration

Qwen's release blog assigns Muon to two-dimensional linear maps in attention, Gated DeltaNet, and MoE experts, while embeddings, the MoE router, and Gated Residual's low-rank parameters remain under AdamW. It also says fused QKV, SwiGLU, and GDN projection matrices are split by their independent transformations before orthogonalization. This reinforces that semantic matrix boundaries—not merely a fused tensor's rank—govern parameter grouping in this implementation.[^qwen38-next-blog]

## DeepSeek-V4 configuration

DeepSeek-V4 provides primary configuration evidence for a hybrid optimizer: it assigns Muon to most modules while retaining AdamW for embeddings, the prediction head, mHC static biases and gates, and RMSNorm weights. Its implementation applies weight decay, a Nesterov-style momentum update, and RMS-rescales the matrix update; it uses ten hybrid Newton–Schulz iterations, with eight rapid-convergence iterations followed by two stabilizing iterations. These choices are V4-specific rather than Muon requirements.[^deepseek-v4-2026]

## nanochat implementation variant

nanochat supplies inspectable implementation evidence for a substantially extended Muon path. It applies Nesterov momentum, row equilibration, five Polar Express polynomial iterations, Frobenius renormalization, and a factored per-row or per-column second moment before a cautious decay/update. Equal-shaped matrices are stacked; in distributed runs, gradient chunks and optimizer states are partitioned across ranks with reduce-scatter and reconstructed with all-gather. These choices are nanochat-specific rather than definitions of Muon.[^nanochat-optim-2026]

## Per-head variant

Kimi K3 partitions Q/K/V momentum along the attention-head dimension and orthogonalizes each block separately. The stated motivation is to equalize update scale across heads instead of letting larger-gradient heads dominate a single full-matrix polar factor; tall per-head blocks also make Newton–Schulz iterations somewhat cheaper. GLM-5 independently reports the same per-head split for MLA Q/K/V up-projections and shows it closing an observed MLA-versus-GQA gap in its listed ablation. These are architecture-specific refinements, not changes to Muon’s core orthogonalized-momentum principle.[^kimi-k3-2026][^glm5-report-2026]

## Relationships

- **Operational limits and scaling evidence:** [Muon LLM training scaling and operational trade-offs](muon-llm-training-scaling-and-operational-trade-offs.md).
- **Applies to:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md), because the source reports Muon use for expert weight matrices in Moonlight.
- **Used by:** [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md), with a Muon-aware distributed implementation.
- **Implemented by:** [nanochat distributed Muon–AdamW training](nanochat-distributed-muon-adamw-training.md), with optimizer-integrated ZeRO-2-style state sharding.
- **Used by:** [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md), with blog-declared matrix splitting and hybrid Muon–AdamW parameter groups.

## Evidence limits

The core formula, original Newton–Schulz coefficients, and broad configuration guidance still come from a secondary Vietnamese overview; the primary Muon report was not independently ingested. The nanochat source provides primary evidence only for its own implementation variant, not for general quality or scaling claims.[^muon-overview-2026][^nanochat-optim-2026]

[^muon-overview-2026]: “Muon Optimizer overview (Vietnamese summary),” [raw source](../raw/MuonOptimizer.md), Sections 1–6, 12, and 15; it cites “Muon is Scalable for LLM Training” (arXiv:2502.16982), Keller Jordan’s Muon post, and the Muon repository.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Section 2.5.

[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Sections 2.4, 4.4.1, and 5.2.

[^glm5-report-2026]: GLM-5 Team, “GLM-5: from Vibe Coding to Agentic Engineering,” arXiv:2602.15763v2, [pre-training section](../raw/arXiv-2602.15763v2/2_pretrain.tex), Multi-latent Attention ablation.

[^nanochat-optim-2026]: nanochat contributors, [combined Muon–AdamW optimizer](../raw/nanochat/nanochat/optim.py), fused Muon kernel and distributed parameter-group update path.

[^qwen38-next-blog]: Qwen Team, “Qwen3.8-Flash-Next,” [release blog](../raw/Qwen3.8-Flash-Next/blog.md), Optimization section.
