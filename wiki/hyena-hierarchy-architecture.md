---
type: Concept
title: Hyena hierarchy architecture
description: Hyena replaces attention with an input-controlled recurrence of gated, implicitly parameterized long convolutions evaluated through FFTs.
tags: [hyena, convolution, attention-free, long-context, sequence-modeling]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T00:00:00Z }
sources:
  - id: poli-etal-2023
    resource: ../raw/2302.10866_HyenaHierarchy/main.tex
    title: "Hyena Hierarchy: Towards Larger Convolutional Language Models"
---

# Hyena hierarchy architecture

Hyena is an attention-free sequence operator that alternates input-derived elementwise gates and long convolutions. Its filters are generated implicitly, so their parameter count does not grow with sequence length, and FFT convolution evaluates an order-$N$ recurrence in $O(NL\log L)$ time per channel rather than materializing its dense, input-controlled matrix.[^poli-etal-2023]

## Operator

From input $u$, Hyena forms one value projection $v$ and $N$ gate projections $x^1,\ldots,x^N$ (the implementation also applies a short depthwise convolution to the projections). Given learned long filters $h^1,\ldots,h^N$, it computes

$$
z^1=v,\qquad z^{n+1}_t=x^n_t\,(h^n*z^n)_t,\qquad y=z^{N+1}.
$$

For a fixed input, the map from $v$ to $y$ is linear, but its matrix depends on the input-derived gates:

$$
H(u)=D_{x^N}S_{h^N}\cdots D_{x^1}S_{h^1}.
$$

Here $D_x$ is diagonal and $S_h$ is the Toeplitz convolution matrix. Thus Hyena is data-controlled without computing a query–key score matrix. Causal filters make every $S_h$ lower triangular, so their product is causal.[^poli-etal-2023]

## Implicit long filters

Each filter is produced at requested positions by a shallow feed-forward network over positional features and then modulated by a window, $h_t=\operatorname{Window}(t)\operatorname{FFN}(\operatorname{PE}(t))$. The reported design uses sinusoidal activations and an exponentially decaying window on at least one convolution; it also retains short explicit convolutions. This decouples filter length from filter-parameter count, unlike a directly learned finite impulse-response filter.[^poli-etal-2023]

FFT convolution computes each long convolution without materializing $S_h$. The operator cost quoted for sequence width $D$ includes projections and is $O(NDL(\log L+D))$; lower asymptotic mixing cost does not by itself establish lower whole-model runtime.[^poli-etal-2023]

## Relationships

- **Contrasts with:** [Self-attention computational profile](self-attention-computational-profile.md). Both make the mixing depend on input, but self-attention forms dense query–key interactions whereas Hyena factors its matrix into diagonal gates and Toeplitz convolutions.
- **Uses:** [State-space models: continuous, recurrent, and convolutional forms](state-space-models-continuous-recurrent-convolutional-forms.md) as one possible implicit-filter family. The paper identifies GSS as a particular order-1 Hyena and H3 as an order-2 Hyena when their long filters use SSM parameterizations.[^poli-etal-2023]
- **Evaluated by:** [Hyena hierarchy evaluation and trade-offs](hyena-hierarchy-evaluation-and-trade-offs.md).

## Evidence limits

“Unrestricted context” means the operator is not architecturally limited to a fixed local kernel; it does not guarantee accurate long-range retrieval. The matrix factorization is a characterization of the operator, not an equivalence to softmax attention or a proof of equal expressivity. The source is a submitted draft and reports its own implementation and experiments.[^poli-etal-2023]

[^poli-etal-2023]: Michael Poli et al., “Hyena Hierarchy: Towards Larger Convolutional Language Models,” arXiv:2302.10866, bundled [LaTeX source](../raw/2302.10866_HyenaHierarchy/main.tex), Sections 1–3 and Appendix B.
