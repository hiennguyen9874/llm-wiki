---
type: Concept
title: xLSTM extended LSTM architecture
description: xLSTM combines exponentially gated scalar and matrix LSTM memories in residual blocks, trading sLSTM memory mixing for mLSTM’s fixed-state parallel sequence formulation.
tags: [associative-memory, gating, recurrent-models, sequence-modeling, xlstm]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T04:31:55Z }
sources:
  - id: beck-etal-2024
    resource: ../raw/2405.04517_xLSTM/xlstm.tex
    title: "xLSTM: Extended Long Short-Term Memory"
---

# xLSTM extended LSTM architecture

xLSTM extends LSTM with exponential input gating, normalization and numerical stabilization, then supplies two memory cells: sLSTM preserves recurrent memory mixing, while mLSTM uses a normalized key–value matrix memory that admits a parallel full-sequence formulation. The paper places these cells in different residual-block designs and stacks them; this is a reported architecture, not a claim that either cell universally replaces attention or SSMs.[^beck-etal-2024]

## Cells and gates

Both variants replace the conventional sigmoid input gate with an exponential gate and maintain a normalizer. For scalar sLSTM, the essential recurrence is

$$
c_t=f_tc_{t-1}+i_tz_t,\qquad n_t=f_tn_{t-1}+i_t,\qquad h_t=o_t(c_t/n_t),
$$

where $i_t=\exp(\tilde i_t)$ and $f_t$ can be sigmoid or exponential. A stabilizer rescales input and forget gates in log space so that the cell and normalizer are scaled together; their ratio, and therefore the output and parameter gradients, are unchanged. The source describes this as enabling storage decisions to be revised while avoiding exponential overflow.[^beck-etal-2024]

sLSTM retains hidden-to-hidden connections in its gate and candidate projections. With multiple cells, block-diagonal recurrent matrices partition memory mixing by head; the source also clips recurrent-gradient magnitude to 10. This mixing makes its time recurrence non-parallelizable in the reported design.[^beck-etal-2024]

mLSTM instead stores key–value outer products in a matrix state:

$$
C_t=f_tC_{t-1}+i_tv_tk_t^\top,\qquad
n_t=f_tn_{t-1}+i_tk_t,
$$

then reads with query $q_t$ as

$$
\tilde h_t=\frac{C_tq_t}{\max(|n_t^\top q_t|,1)},\qquad h_t=o_t\odot\tilde h_t.
$$

It has no hidden-to-hidden memory mixing. The source gives an equivalent stabilized full-sequence form using causal gate weights and matrix multiplication, enabling parallel training, while retaining the recurrence for autoregressive generation.[^beck-etal-2024]

## Residual-block composition

The report uses pre-LayerNorm residual stacks and two cell-specific blocks:

- **sLSTM:** post-up-projection residual block, optionally with causal convolution, followed by a gated MLP.
- **mLSTM:** pre-up-projection block, with causal convolution, a learnable skip connection, head-wise GroupNorm, component-wise output gate, and down-projection. The up-projection increases the matrix-memory width.

An xLSTM[$a$:$b$] model contains $a/b$ mLSTM-to-sLSTM blocks. For the reported xLSTM[7:1] configuration, sLSTM blocks are a minority among mLSTM blocks.[^beck-etal-2024]

## State and systems boundary

mLSTM carries a matrix state whose dimensions are set by head width rather than the number of prior tokens; it therefore avoids a sequence-growing token KV cache, but each head’s matrix update and read are $d\times d$ operations. The paper characterizes the sequence-length dependence as linear computation and constant state memory, while noting the matrix computation cost. sLSTM’s memory mixing prevents the same parallel sequence formulation; the source reports a custom CUDA implementation that was typically under twice as slow as its mLSTM implementation, but this is configuration-specific.[^beck-etal-2024]

## Relationships

- **Related to:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md). mLSTM is also a fixed-size, outer-product associative state, but it uses LSTM-style gates and the source’s normalizer rather than being identical to a feature-map linear-attention formulation.[^beck-etal-2024]
- **Contrasts with:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md). mLSTM’s reported covariance update adds a gated outer product; it does not apply the delta rule’s key-addressed corrective subtraction.[^beck-etal-2024]
- **Evaluated by:** [xLSTM evaluation and deployment limits](xlstm-evaluation-and-deployment-limits.md).

## Evidence limits

The equations, block details, and parallel formulation are primary-source descriptions. The paper does not establish that a fixed matrix state retains arbitrary long histories without interference, nor that parallel mathematical formulation guarantees an optimized kernel. The authors explicitly flag mLSTM’s $d\times d$ work, sLSTM’s non-parallel mixing, sensitive forget-gate initialization, possible fixed-state overload at longer contexts, and incomplete large-model architecture/hyperparameter optimization.[^beck-etal-2024]

[^beck-etal-2024]: Maximilian Beck et al., “xLSTM: Extended Long Short-Term Memory,” arXiv:2405.04517, bundled [LaTex source](../raw/2405.04517_xLSTM/xlstm.tex), Abstract; Sections 2, 3.4, and 6; Appendix A–B.
