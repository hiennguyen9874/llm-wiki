---
type: Concept
title: Mamba selective state spaces and architecture
description: Mamba makes structured state-space dynamics input-dependent and packages the resulting selective scan in a homogeneous attention-free sequence block.
tags: [mamba, selective-ssm, ssm, recurrent-models, sequence-modeling]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T04:57:05Z }
sources:
  - id: gu-dao-2023
    resource: ../raw/2312.00752_Mamba/main.tex
    title: "Mamba: Linear-Time Sequence Modeling with Selective State Spaces"
  - id: bourdois-2024
    resource: ../raw/IntroductiontoStateSpaceModels.md
    title: "Introduction to State Space Models (SSM)"
---

# Mamba selective state spaces and architecture

Mamba changes a structured state-space model (SSM) from time-invariant to input-dependent dynamics, allowing its fixed recurrent state to selectively retain, ignore, or reset information. Its homogeneous block combines this selective SSM path with expansion, gating, normalization, and residual connections instead of alternating attention and MLP blocks.[^gu-dao-2023]

## Selective SSM (S6)

A diagonal SSM discretizes continuous parameters and updates a per-channel latent state as $h_t=\bar A_t h_{t-1}+\bar B_t x_t$, then reads $y_t=C_t h_t$. In prior LTI SSMs, $\Delta$, $B$, and $C$ are fixed over positions, so the recurrence also has a global-convolution form. Mamba keeps $A$ as a learned structured parameter but produces $B_t$, $C_t$, and the positive timestep $\Delta_t$ from the current input. The resulting transition is time-varying and cannot use that fixed-kernel convolution equivalence.[^gu-dao-2023]

$\Delta_t$ controls a retention-versus-update trade-off through discretization. In the paper's scalar special case ($A=-1$, $B=1$), input-dependent $\Delta_t=\operatorname{softplus}(\operatorname{Linear}(x_t))$ yields the gated update

$$
h_t=(1-g_t)h_{t-1}+g_t x_t,\qquad g_t=\sigma(\operatorname{Linear}(x_t)).
$$

Thus RNN-style gating is a special case of selection. Selective $B_t$ controls writing into state and selective $C_t$ controls reading from it; the reported language ablation found $\Delta$ selection most important, with all three together best in that configuration.[^gu-dao-2023]

## Block design and memory boundary

Each Mamba block expands the model width (the paper uses expansion factor $E=2$), applies a short convolution, SiLU activation, and the selective SSM on its main path, then gates and projects the result. It is stacked with normalization and residual connections. Most parameters are in the input and output projections, not the SSM; the design therefore folds sequence mixing and the role of a gated MLP into one repeated block.[^gu-dao-2023]

The recurrent state has fixed dimensions determined by model and SSM state widths, so autoregressive updates need not retain a token-by-token KV cache. This is a compression trade-off, not token-addressable retrieval: selective state can decide what to retain, but it does not preserve every prior token in isolated addressable slots.[^gu-dao-2023]

## Relationships

- **Contrasts with:** [Self-attention computational profile](self-attention-computational-profile.md), whose full attention directly connects tokens but incurs quadratic full-sequence interaction cost.
- **Extends:** [State-space models: continuous, recurrent, and convolutional forms](state-space-models-continuous-recurrent-convolutional-forms.md) by making the recurrence parameters input-dependent and using a hardware-aware scan; the lineage link is maintained synthesis.[^gu-dao-2023][^bourdois-2024]
- **Predecessor of:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md). This lineage link is maintained synthesis; that successor’s concept records its projection reorganization and SSD layer.

## Evidence limits

The recurrence, block description, and gating reduction are specified by the primary paper. “Select,” “forget,” and “reset” describe available dynamics, not a guarantee that a trained model will perform reliable semantic retrieval or boundary detection. Fixed recurrent state bounds state shape, while practical latency, quality, and length generalization still depend on state size, kernels, training, modality, and workload.

[^gu-dao-2023]: Albert Gu and Tri Dao, “Mamba: Linear-Time Sequence Modeling with Selective State Spaces,” arXiv:2312.00752, bundled [LaTeX source](../raw/2312.00752_Mamba/main.tex), Sections 3–4 and Appendix A.
[^bourdois-2024]: Loïck Bourdois, “Introduction to State Space Models (SSM),” Hugging Face blog, source snapshot [IntroductiontoStateSpaceModels.md](../raw/IntroductiontoStateSpaceModels.md), sections “Definition of an SSM in deep learning” through “Learning matrices.”

