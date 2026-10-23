---
type: Concept
title: FastEnhancer Design Choices and Ablations
description: Why FastEnhancer is fast on CPU — time-axis kernel size 1, fusable BatchNorm, a time-GRU plus frequency-attention RNNFormer block — with the reported ablations against time-kernel 3, LayerNorm, dual-path RNN and dual-path transformer variants, and its loss and training recipe.
tags: [pipeline, speech-enhancement, streaming, ablation, edge, cpu, paper]
status: draft
created: 2026-10-24
generated: { by: llm-wiki-agent/1, at: 2026-10-24T12:00:00Z }
stale_after: 2027-10-24
sources:
  - id: fastenhancer-paper
    resource: ../raw/arXiv-2509.21867v1-FastEnhancer/main.tex
    scope: ../raw/arXiv-2509.21867v1-FastEnhancer/
    kind: paper
    revision: arXiv 2509.21867v1
    title: "FastEnhancer: Speed-Optimized Streaming Neural Speech Enhancement (LaTeX source)"
---

The [FastEnhancer](fastenhancer.md) paper's central argument is that parameter and MAC counts mispredict real streaming speed: sub-band splitting, grouped RNNs and channel shuffles reduce MACs but add memory operations, so a plain encoder–decoder built only from operations that are cheap per frame at inference time wins on CPU RTF. Three choices carry the claim: convolutions with time-axis kernel 1 (no frame cache), BatchNorm that fuses into neighboring layers, and an RNNFormer bottleneck pairing a unidirectional GRU over time with multi-head self-attention (MHSA) over frequency. The ablations support each choice at one model size (Base) or across sizes (**Reported**).[^fastenhancer-paper]

## Architecture

- **Encoder/decoder**: a pre-encoder strided convolution (kernel 8, stride 4 along frequency) cuts frequency resolution from N_fft/2 to N_fft/8 and raises channels from 2 to C₁; L encoder blocks (Conv k=3, BatchNorm, SiLU) follow; the decoder mirrors them with 1×1-conv fusion of skip connections and ends with a transposed convolution restoring resolution (**Observed** from Fig. 2 and Sec. 3).[^fastenhancer-paper]
- **Bridge**: pre-RNNFormer reduces frequency to F with a linear layer (initialized as a linear filterbank) and channels from C₁ to C₂ with a 1×1 conv; post-RNNFormer reverses it (linear layer initialized as linear interpolation). Both linear layers are frozen at 16 kHz because training them gave no gain; the README says they are learnable in the 48 kHz variants (**Reported**).[^fastenhancer-paper]
- **RNNFormer block** (×K): a GRU sub-block (unidirectional time GRU, 1×1 conv, BatchNorm, residual) then an MHSA sub-block (four heads over frequency, same wrapper); a trainable positional encoding is added at the first MHSA block's input. Whole model: weight normalization and SiLU activations (**Reported**).[^fastenhancer-paper]
- **Why hybrid**: a GRU keeps temporal state in a small hidden vector, whereas a time-axis transformer needs cached key/value frames; frequency attention needs no cache and can model global relations such as harmonics rather than the sequential frequency dependency a frequency-axis RNN assumes (**Reported** argument, tested in the ablations below).[^fastenhancer-paper]

## Speed-motivated choices and evidence

| Variant (from FastEnhancer-B) | Params (k) | RTF Xeon | RTF M1 | SISDR | STOI % |
| --- | --- | --- | --- | --- | --- |
| FastEnhancer-B (baseline) | 92 | 0.022 | 0.026 | 19.0 | 94.5 |
| Time-axis kernel size 3 (every frequency-kernel-3 conv) | 187 | 0.028 | 0.037 | 19.0 | 94.5 |
| LayerNorm instead of BatchNorm | 92 | 0.028 | 0.029 | 18.9 | 94.5 |

- **Time kernel**: kernel 3 on the time axis needs a cached buffer of k−1 past frames concatenated and rewritten each frame; it roughly doubled parameters (92k to 187k) and raised RTF by 27% (Xeon) and 42% (M1) with no SISDR or STOI gain (percentages recomputed, **Observed**).[^fastenhancer-paper]
- **BatchNorm versus LayerNorm**: same parameters and MACs, but LN cannot be fused into adjacent layers; RTF rose 27% (Xeon) and 12% (M1) for equal quality (SISDR 18.9 vs 19.0; percentages recomputed, **Observed**). BN is therefore fused into neighbors at inference.[^fastenhancer-paper]
- **Caveat**: both ablations are single-size (Base) and the RTFs come from the authors' ONNXRuntime export; the relative cost of cached convolutions or unfused LN on other runtimes, or with different threading, is not measured (**Synthesis**).

## RNNFormer versus dual-path alternatives (Fig. 3)

The ablation figure plots SISDR and STOI against RTF on Xeon with five points each for RNNFormer and DPRNN and four for DPT. Values below are read approximately from the rendered plot (**Observed**, approximate), while the direction matches the paper's text:[^fastenhancer-paper]

- **Dual-path RNN** (frequency GRU instead of frequency MHSA): STOI essentially equal to RNNFormer at equal size, SISDR lower at the larger sizes (for example about 19.2 vs 19.4 at the Medium size and about 19.35 vs 19.6 at Large). At the smallest size DPRNN's SISDR is about the same or slightly higher (about 18.65 vs 18.55), so the paper's "clearly degraded SISDR" is a mid-to-large-size result. DPRNN points also sit at slightly higher RTF than the same-size RNNFormer.
- **Dual-path transformer** (time MHSA with a 31-frame, 0.5 s look-behind instead of the time GRU): fewer parameters than RNNFormer but key/value caching raised RTF markedly; at comparable SISDR (about 19.2) its RTF is roughly twice RNNFormer-S's (about 0.07 vs 0.034), and its smallest point (RTF about 0.025) has lower SISDR and STOI than RNNFormer-B (about 18.4 vs 19.0 SISDR). Its largest point (RTF about 0.2, SISDR about 19.45) lies close to the RNNFormer curve, so the advantage is clearest at small and mid sizes.
- The paper concludes a recurrent approach is more efficient than self-attention for streaming time modeling, and self-attention beats recurrence for frequency modeling (**Reported**).[^fastenhancer-paper]

## Training and loss recipe

- Data: VoiceBank-DEMAND downsampled from 48 kHz to 16 kHz, random 2-second segments; AdamP optimizer, initial learning rate 0.002, weight decay 0.01, batch 64, cosine annealing with 500 warm-up steps; five random seeds averaged (**Reported**).[^fastenhancer-paper]
- Loss: weighted sum of compressed-magnitude MSE (λ=0.3), complex-spectrogram MSE (0.2), consistency loss between the target and the re-STFT of the output (0.3), waveform L1 (0.2) and a differentiable PESQ loss (0.001). The PESQ weight is kept tiny because PESQ-only optimization can hurt subjective quality, yet the authors observed it improved the other objective metrics too (**Reported**).[^fastenhancer-paper]
- Metrics: DNSMOS P.808 and P.835, SCOREQ (natural-speech full-reference), SISDR, PESQ (P.862.2 without Corrigendum 2), STOI, ESTOI, and WER with Whisper-large-v3-turbo (**Reported**).[^fastenhancer-paper]
- The README states that the DNS-1 models were trained without the PESQ loss; see [FastEnhancer](fastenhancer.md).

## Relationships

- Explains the results in [FastEnhancer](fastenhancer.md); that page holds the full performance tables and voice-pipeline implications.
- Contrasts with [UL-UNAS Design Components and NAS](ul-unas-design-and-nas.md): UL-UNAS optimizes a MACS budget through architecture search and keeps GTCRN's grouped dual-path RNN, whereas FastEnhancer treats MACs as a misleading target and optimizes measured CPU RTF; neither paper tests the other's claim on its own hardware metric (**Synthesis**).[^fastenhancer-paper]
- Relevant to edge packaging questions for the pipeline's noise-preprocessing stage; see [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) (**Synthesis**).

## Coverage and limits

- Ledger: `3.Model.tex`, `4.Setting.tex`, `5.Results.tex`, `2.Related.tex`, `table-ablation.tex` read in full; `fig_model.pdf` and `fig_ablation.pdf` rendered and viewed. The cited methods (DPRNN, DPT, GTCRN, LiSenNet, FSPEN, BSRNN, torch-pesq, AdamP) are uninspected.
- The ablation table reports STOI in percent while the main table uses a 0–1 scale; the figure-read values are approximate and no per-point numbers are tabulated in the source. The paper provides no ablation of the linear filterbank initialization, positional encoding, or number of attention heads, and no variance across the five seeds.
- No code was inspected; reproduction of the ablations is not attempted. No sensitive values were found.

[^fastenhancer-paper]: [FastEnhancer LaTeX source](../raw/arXiv-2509.21867v1-FastEnhancer/main.tex) (arXiv 2509.21867v1) — locators: Sec. 2.1 (dual-path networks, DPT caching argument) and 2.2 (processing speed versus MACs); Sec. 3 (input/output, convolutional layers, normalization layers, encoder and decoder, RNNFormer, loss functions) and Fig. 2 (`fig_model.pdf`); Sec. 4 (training setup, model-configuration table, metrics); Sec. 5.2 (ablation studies), Table 2 `table:ablation`, Fig. 3 (`fig_ablation.pdf`).
