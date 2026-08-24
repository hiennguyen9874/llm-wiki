---
type: Concept
title: Cross-layer value routing for delta memories
description: CLVR projects a DeltaNet-style layer’s write value into the shared residual stream through a zero-initialized projection; the supplied single-run comparisons show small matched validation-loss reductions over DeltaNet and Gated DeltaNet baselines.
tags: [associative-memory, cross-layer-routing, deltanet, evaluation, residual-stream]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T02:22:56Z }
sources:
  - id: linear-attention-architectures-2026
    resource: ../raw/2607.07953_LinearAttentionArchitectures/template.tex
    title: "Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing"
---

# Cross-layer value routing for delta memories

Cross-Layer Value Routing (CLVR) adds a DeltaNet-style layer's internal write value to the shared residual stream through a learned, zero-initialized projection. In the supplied matched, single-run comparisons, this hidden-stream route yields small lower final validation losses than non-routing DeltaNet and Gated DeltaNet baselines, whereas routing the delta-rule error into the next layer's value target (CLER) is neutral or worse.[^linear-attention-architectures-2026]

## From CLER to CLVR

For a recurrent layer's value $v_{l,t}$, memory prediction $\bar v_{l,t}=W_{l,t-1}\phi(k_{l,t})$, and delta-rule write error $r_{l,t}=v_{l,t}-\bar v_{l,t}$, the initial Cross-Layer Error Residuals (CLER) formulation modifies the next routing-capable layer's value target:

$$
\tilde v_{l,t}=v_{l,t}+\Gamma_l r_{p(l),t},
$$

where $p(l)$ is the nearest lower routing-capable layer and $\Gamma_l$ is learned. The host recurrent update and gates otherwise remain unchanged; intervening softmax layers only carry the side channel. At 350M parameters and about 1B tokens, CLER is flat or worse in all four reported optimizer/host comparisons: its one Muon DeltaNet difference is $-0.0004$, explicitly treated by the authors as too small to establish a gain.[^linear-attention-architectures-2026]

CLVR instead projects an internal signal $s_{l,t}$ into the model's shared residual stream:

$$
\varepsilon_{l,t}=P_l s_{l,t},\qquad h_{l,t}\leftarrow h_{l,t}+\varepsilon_{l,t}.
$$

For CLVR, $s_{l,t}=v_{l,t}$; for the parameter-matched CLER-H ablation, $s_{l,t}=r_{l,t}$. $P_l$ is zero-initialized, optionally low rank, so the route contributes exactly zero at initialization and the model starts from its host baseline. Unlike CLER's receiver-local value target, the residual stream is shared by later layers and the output head.[^linear-attention-architectures-2026]

## Reported matched results

Under Muon, the source reports the following final-loss deltas versus matched no-routing baselines (negative is lower loss):

| Host and scale | CLER-H (error) | CLVR (value) |
| --- | ---: | ---: |
| Gated DeltaNet, 350M / 1B tokens | -0.0073 | **-0.0103** |
| Gated DeltaNet, 350M / 15B tokens | -0.0042 | **-0.0059** |
| Gated DeltaNet, 1.3B / 40B tokens | -0.0010 | **-0.0019** |
| DeltaNet, 350M / 1B tokens | -0.0047 | **-0.0119** |
| DeltaNet, 350M / 15B tokens | -0.0002 | **-0.0016** |

CLVR beats CLER-H in every listed row at fixed projection shape. The reported effect diminishes with longer training or the larger available Gated DeltaNet run, and there is no 1.3B/40B hidden-stream DeltaNet comparison. The source interprets this as possible diminishing headroom, not an established scaling law.[^linear-attention-architectures-2026]

Matched 350M/15B downstream checks on HellaSwag and PIQA are mixed and broadly comparable to baseline; WinoGrande point estimates are higher for routing variants but are not treated as reliable evidence. The supported conclusion is no clear degradation on those checks, not broad downstream improvement.[^linear-attention-architectures-2026]

## Boundaries and open tests

The source attributes CLER's outcome to a possible basis mismatch: a lower layer's local value/error space need not align with a receiver's independently learned value space. That explanation is an author interpretation, not a causal ablation. It did not test CLVR on KDA or Gated DeltaNet-2, where separate erase/write quantities make the candidate routed signal less obvious.[^linear-attention-architectures-2026]

All main routing entries are single matched runs without standard deviations. Absolute losses across token budgets are not comparable because the 15B- and 40B-token runs use a different FineWeb-Edu slice. The paper provides training throughput and iteration-time measurements for the host architectures, but no empirical inference-speed benchmark for CLVR.[^linear-attention-architectures-2026]

## Relationships

- **Routes signals from:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md).
- **Contrasts with:** [Attention Residuals](attention-residuals.md): AttnRes replaces uniform residual aggregation using depth-wise output retrieval, while CLVR additively routes an internal recurrent write signal.
- **Evaluated alongside:** [Linear-attention architecture frontier and optimizer sensitivity](linear-attention-architecture-frontier-and-optimizer-sensitivity.md).
- **Open extension to:** [Gated DeltaNet-2 decoupled delta rule and training](gated-deltanet-2-decoupled-delta-rule-and-training.md).

[^linear-attention-architectures-2026]: Tommaso Cerruti, Tim Rieder, George Rowlands, Lingfeng Jin, and Imanol Schlag, “Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing,” supplied LaTeX source, [source](../raw/2607.07953_LinearAttentionArchitectures/template.tex), Abstract; Sections 3, 4.3, 5.6–5.7, and 6–8; Tables 5–6; and Appendix B.