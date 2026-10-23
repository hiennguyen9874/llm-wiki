---
type: Concept
title: Comfi-FastGRNN and RNN State Drift
description: FastGRNN's reported hidden-state drift and quality decay on audio longer than about 60 s, and Comfi-FastGRNN's two-parameter trainable complementary filter that suppresses it in Fast-ULCNet, with the supporting 90 s results and the mechanism's open questions.
tags: [pipeline, speech-enhancement, rnn, streaming, long-sequence, paper]
status: draft
created: 2026-10-24
generated: { by: llm-wiki-agent/1, at: 2026-10-24T18:00:00Z }
stale_after: 2027-10-24
sources:
  - id: fast-ulcnet-paper
    resource: ../raw/arXiv-2601.14925v1-Fast-ULCNet/Template.tex
    scope: ../raw/arXiv-2601.14925v1-Fast-ULCNet/
    kind: paper
    revision: arXiv 2601.14925v1
    title: "Fast-ULCNet: a Fast and Ultra Low Complexity Network for Single-Channel Speech Enhancement (LaTeX source)"
---

FastGRNN is a small gated RNN whose gate and candidate state share the same weights; its authors claim training stability independent of sequence length. The [Fast-ULCNet](fast-ulcnet.md) paper reports that this guarantee does not extend to inference on long audio: with FastGRNN layers the mean hidden-state magnitude climbed steadily while enhancement quality fell once input exceeded about 60 s. The proposed fix, Comfi-FastGRNN, adds a complementary filter with two trainable scalars per layer, `h_comfi = γ·h + (1 − γ)·λ`, and on a 90 s test it restores ULCNet-level DNSMOS with no measured speed cost (**Reported**).[^fast-ulcnet-paper] The evidence is one model family, one dataset and one run, so treat it as a failure mode to test for, not an established property of FastGRNN.

## FastGRNN cell

Equations 1–3 (**Reported**):[^fast-ulcnet-paper]

- `z_t = σ(W x_t + U h_{t−1} + b_z)`
- `h̃_t = tanh(W x_t + U h_{t−1} + b_h)`
- `h_t = (ζ(1 − z_t) + ν) ⊙ h̃_t + z_t ⊙ h_{t−1}`

`σ` is sigmoid, `W` and `U` are shared by gate and candidate, and `ζ, ν ∈ [0, 1]` are trainable scalars. The original FastGRNN evaluation used sequences up to 1.63 s, which the paper highlights as the longest audio clip tested there (**Reported**).[^fast-ulcnet-paper]

## Observed drift

- Applied to speech enhancement on audio longer than 60 s, performance degrades over time, correlated with an increasing mean RNN state magnitude (Fig. 2, **Reported**).[^fast-ulcnet-paper]
- Reading Fig. 2 (`drift_vs_signal_dejavusans.pdf`, ~83 s clip; values approximate from the plot): with FastGRNN the mean state rises roughly linearly from about 0 to about 0.75, and the output waveform gains a growing noise-like component from roughly 40–50 s onward; with Comfi-FastGRNN the mean state stays below about 0.1 and the output stays clean (**Observed**, approximate).
- **Authors' explanation**: Eq. 3 has no contraction guarantee and its coefficients are not constrained to sum to one, so state can accumulate over long horizons (**Reported** explanation; not tested by an ablation, so **Unverified** as the cause).[^fast-ulcnet-paper]

## Comfi-FastGRNN

- **Mechanism** (Eq. 4): a complementary filter, borrowed from accelerometer–gyroscope orientation fusion, blends the FastGRNN state with a learned constant offset: `γ` sets the share kept from `h_t` and `λ` is a scalar drift-compensation term. Both are scalars per layer, so the parameter cost is negligible and the paper reports identical parameters, MACs and RTF to plain Fast-ULCNet (**Reported**).[^fast-ulcnet-paper]
- **Initialization**: `γ = 0.999`, `λ = 0.0` (**Reported**); the trained values are not reported.[^fast-ulcnet-paper]
- **Placement**: Fig. 1 draws the filter after the FastGRNN state update, before `h_t` leaves the cell (**Observed**). The text does not say whether the filtered state is fed back as `h_{t−1}`; if it is, `γ < 1` makes the state a contraction toward `λ`, with a time constant near 1/(1 − γ) = 1,000 frames (about 16 s at the 16 ms hop) at initialization, which would explain bounded state; this is **Synthesis**, not stated by the paper.
- **Results** (Table 1, 90 s set): plain Fast-ULCNet drops to OVRLMOS 2.93, BAKMOS 3.62, PESQ 2.24, SI-SDR 13.58, while the comfi variant reaches 3.10, 3.99, 2.51, 16.48, matching ULCNet on DNSMOS (3.09 / 3.95) and trailing it by 0.15 PESQ and 0.41 dB SI-SDR. On the 10 s set the comfi variant is indistinguishable from plain Fast-ULCNet (PESQ 2.50 vs 2.51; SI-SDR 16.01 vs 15.99) (**Reported**, recomputed deltas **Observed**).[^fast-ulcnet-paper]

## Practical implications

- **Soak-test recurrent frontends**: a streaming voice agent can run for minutes to hours. Any recurrent noise-suppression or VAD-adjacent model validated only on 10 s utterances may hide a drift failure; the 90 s self-concatenation protocol is a cheap first check (**Synthesis**). Whether other recurrent enhancers or GRU-based ULCNet suffer is not established; ULCNet showed no 90 s drop in this paper.[^fast-ulcnet-paper]
- **Alternative remedies**: resetting hidden state at detected silence or fine-tuning on long sequences (as [DPDFNet Design, Training and Evaluation](dpdfnet-design-and-training.md) does for a different always-on failure) are untested alternatives here; the paper compares only plain versus comfi (**Synthesis**).
- **Transferability untested**: the authors list applying Comfi-FastGRNN to other architectures as future work (**Reported**).[^fast-ulcnet-paper]

## Relationships

- Component of [Fast-ULCNet](fast-ulcnet.md); that page holds the architecture, protocol and complexity results.
- Related to [FastEnhancer Design Choices and Ablations](fastenhancer-design-and-ablations.md), which instead uses a GRU along time in its RNNFormer block for CPU speed, with no long-sequence drift test reported (**Synthesis**).
- Related to [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) only insofar as long-session stability matters when enhancement runs ahead of ASR (**Synthesis**).

## Coverage and limits

- Source coverage is as listed in [Fast-ULCNet](fast-ulcnet.md); Figures 1 and 2 were viewed, with plot values read approximately.
- Drift was shown on one model family at one sample rate, with speech repeated across the 90 s test; no hidden-state statistics beyond Fig. 2, no sweep over γ or λ, no trained-parameter values, no comparison with simple alternatives (state reset, clipping, normalization) and no evaluation beyond about 90 s. The "first trainable complementary filter for RNN drift" claim is the authors' and was not checked against literature (**Reported**).
- No sensitive values were found.

[^fast-ulcnet-paper]: [Fast-ULCNet LaTeX source](../raw/arXiv-2601.14925v1-Fast-ULCNet/Template.tex) (arXiv 2601.14925v1) — locators: abstract and Sec. 1 (drift claim, contributions); Sec. 2.1 (FastGRNN Eqs. 1–3, drift observation, Eq. 4, Fig. 1 `Comfi-FastGRNN_diagram_0_margin.pdf`, Fig. 2 `drift_vs_signal_dejavusans.pdf`); Sec. 3.1.1 (sigmoid gate, γ/λ initialization); Sec. 3.2.1 and Table 1 (10 s and 90 s results); Sec. 3.2.2 (variant has identical complexity); Sec. 4 (future work).
