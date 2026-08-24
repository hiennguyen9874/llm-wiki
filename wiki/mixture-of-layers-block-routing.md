---
type: Concept
title: Mixture of Layers block routing
description: Mixture of Layers routes each token across parallel, down/up-projected thin Transformer blocks, using a shared softmax block and routed Gated DeltaNet blocks to retain global context under sparse block activation.
tags: [mixture-of-layers, sparse-models, routing, hybrid-attention, gated-deltanet]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T02:18:06Z }
sources:
  - id: mol-2026
    resource: ../raw/2605.09516_MixtureofLayerswithHybridAttention/submission.tex
    title: "Mixture of Layers with Hybrid Attention: Parallel Thin Blocks for Sparse Transformer Compute"
---

# Mixture of Layers block routing

Mixture of Layers (MoL) makes a Transformer stage a routed composition of complete, lower-width Transformer blocks rather than routing only its FFN. A shared full-sequence softmax block supplies global token access in every split stage, while top-$k$ routed Gated DeltaNet blocks process sparse token subsets; the reported design therefore trades total parameters and routing overhead for lower per-token active compute.[^mol-2026]

## Thin-block split stage

For model width $d_{\mathrm{model}}$ and thin width $d_{\mathrm{thin}}$, each block down-projects the residual stream, applies RMSNorm, attention, and FFN at thin width, subtracts the inner residual, then up-projects its computed delta:

$$
\operatorname{ThinBlock}(x)=W_{\mathrm{up}}\bigl(\operatorname{Block}_{d_{\mathrm{thin}}}(W_{\mathrm{down}}x)-W_{\mathrm{down}}x\bigr).
$$

A learned router selects $k$ of $K$ blocks and combines their softmax-normalized scores inside an outer residual:

$$
\operatorname{SplitStage}(x)=x+\frac{1}{k}\sum_{i\in\operatorname{topk}(K)}w_i\operatorname{ThinBlock}_i(x).
$$

The reported implementation uses a CV$^2$ penalty on per-block routing weights ($\alpha=0.05$) to avoid block collapse. It also holds head width at 64 and shares precomputed RoPE embeddings across the full- and thin-width blocks.[^mol-2026]

## Hybrid attention for sparse blocks

A softmax-only routed block sees only the tokens assigned to it. In the authors’ WikiText-103 example, top-3-of-15 gives each routed block about 20% of tokens, and the reported softmax-only perplexity worsens from 32.04 for 3-of-5 to 34.73 for 3-of-15 despite the larger block pool. MoL addresses that coverage loss as follows:[^mol-2026]

- **One shared block** is always active and runs full softmax attention over all tokens.
- **Routed blocks** are selected by the router and use sparse gather/compute/scatter dispatch with Gated DeltaNet linear attention on their routed subsequences.
- A name such as $1+3\text{of}15$ means one shared block plus three selected routed blocks from 14 candidates, hence four active blocks out of 15.[^mol-2026]

The source reports that Gated DeltaNet's thin-width advantage diminishes with width: its reported DeltaNet-minus-softmax perplexity gap changes from 2.79 at $d_{\mathrm{thin}}=128$ to 2.55 at 256, 1.12 at 512, and -0.10 at 1024. This is an architecture-specific ablation, not evidence that DeltaNet generally dominates softmax attention at small widths.[^mol-2026]

## Sparse-dispatch boundary

Sparse dispatch gathers each routed block’s tokens into compact tensors and scatters the output back. The authors report numerical agreement with dense restricted attention (maximum logit differences $5.7\times10^{-6}$ on GPU and $2.4\times10^{-7}$ on CPU) and forward-only speedups up to $4.94\times$ with `torch.compile` in their sparse configurations. Down/up projections remain a material floor: at the reported width 256 they account for 40% of wrapper parameters, rising to 57% and 73% at widths 128 and 64.[^mol-2026]

The blocks have no within-stage cross-block dependency, so the paper argues they can be placed in parallel. Its three-GPU PCIe prototype is analytic/prototype evidence (38% per-GPU parameter reduction, 23% VRAM savings, and 34% wall-clock penalty), not a demonstrated production scale-out result.[^mol-2026]

## Relationships

- **Extends:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) from routing FFN experts to routing complete thin Transformer blocks; both retain a load-balancing and dispatch problem.[^mol-2026]
- **Uses:** [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md) in the sparse routed pathway.[^mol-2026]
- **Mitigates limits of:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) by keeping a shared token-addressable softmax pathway at every split stage.[^mol-2026]
- **Uses:** [Self-attention computational profile](self-attention-computational-profile.md) as the global-context pathway, while avoiding its full-sequence computation in routed blocks.[^mol-2026]
- **Evaluated by:** [Mixture of Layers evaluation and serving trade-offs](mixture-of-layers-evaluation-and-serving-trade-offs.md).

## Evidence limits

This page compiles a single author preprint. The TeX source and its one loss-curve attachment were inspected; the figure agrees with the reported ordering and final 20K-step values, while bibliography, style, and ORCID assets were not claim sources. The reported routing, quality, and speed figures are not independently reproduced here, and several large-scale comparisons use one seed.

[^mol-2026]: Ivan Ternovtsii and Yurii Bilak, “Mixture of Layers with Hybrid Attention: Parallel Thin Blocks for Sparse Transformer Compute,” May 2026 preprint, [source](../raw/2605.09516_MixtureofLayerswithHybridAttention/submission.tex), Sections 1–3, 5–6, and appendices.