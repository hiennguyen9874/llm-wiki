---
type: Concept
title: Fast-ULCNet
description: Bang & Olufsen's ULCNet variant for single-channel speech enhancement with GRUs replaced by FastGRNN or Comfi-FastGRNN (0.338M vs 0.685M parameters, RTF 0.60–0.66 vs 0.93–0.98 on one Cortex-A53/Pi 3 B+ thread) with reported DNS-2020 10 s and 90 s results, but no ASR, algorithmic-latency, or license evidence.
tags: [pipeline, speech-enhancement, denoising, edge, low-complexity, paper]
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

Fast-ULCNet (Arrieta Larraza and de Koeijer, Bang & Olufsen; ICASSP-2026 template) takes ULCNet, a two-stage magnitude-mask plus phase-refinement speech-enhancement (SE) network, and swaps every GRU layer for a FastGRNN-based layer, optionally with the trainable complementary filter described in [Comfi-FastGRNN and RNN State Drift](comfi-fastgrnn-state-drift.md). The paper reports 0.338M parameters against 0.685M for its own TensorFlow re-implementation of ULCNet, 1.691M against 2.057M MACs, and mean real-time factor (RTF) 0.657 against 0.976 on a Raspberry Pi 3 B+ and 0.604 against 0.927 on an Arm Cortex-A53 (single thread, 10,000 iterations), a 33–35% RTF reduction. On the 10 s DNS-2020 synthetic non-reverberant test set it is within 0.01 DNSMOS OVRL and 0.11–0.12 PESQ of ULCNet. For a voice pipeline it is a candidate CPU-only noise-suppression front end; the paper reports speech-quality metrics only (**Reported**).[^fast-ulcnet-paper]

## Architecture

Figure 3 and Sec. 2.2 describe two stages (**Observed** from the figure and text).[^fast-ulcnet-paper]

1. **Magnitude stage**: modified power-law compression of the real and imaginary STFT parts, channel-wise feature reorientation (reduces input dimensionality), a Conv Block of four depthwise-separable convolutions, a bidirectional frequency-axis "Freq-FastGRNN", a pointwise convolution, sub-band splitting into two sub-band temporal FastGRNN blocks, concatenation, and two fully connected layers that predict a real-valued magnitude mask.
2. **Phase stage**: a small CNN over representations from the estimated magnitude mask and the noisy phase, followed by complex ratio masking (CRM) and power-law decompression to the clean-speech estimate.

In the figure the FastGRNN-based components (Freq-FastGRNN and the two sub-band blocks) are the only boxes changed from ULCNet; the rest is the original design (**Observed**).[^fast-ulcnet-paper]

Reported implementation settings (Sec. 3.1.1): channel-wise reorientation with an overlapping rectangular window of 1.5 kHz resolution and overlap factor 0.33; Conv Block of four 1×3 depthwise-separable layers (frequency axis only) with 32, 64, 96, 128 filters and max-pool by 2 in the last three; Freq-FastGRNN 64 units plus a 64-filter pointwise convolution; two sub-band blocks of two 128-unit FastGRNN layers each; two FC layers of 257 neurons; phase CNN of two 1×3 convolutions with 32 filters plus a 2-channel pointwise convolution (**Reported**).[^fast-ulcnet-paper]

## Training and evaluation protocol

| Item | Reported setting |
| --- | --- |
| Training data | Interspeech 2020 DNS Challenge pipeline; 1,000 h of 10 s mixtures at 16 kHz, SNR uniform −10 to 30 dB; 85/15 train/validation split |
| Test data | DNS-2020 synthetic non-reverberant test set (the one used in the ULCNet paper), 10 s clips; plus a 90 s version made by concatenating each clip with itself nine times |
| STFT | 32 ms window, 16 ms hop, 512-point FFT |
| Loss | Mean of L1 on magnitude spectra plus L1 on complex spectrogram values (Eq. 5) |
| Optimizer | Adam, lr 1e-3, gradient clip 3.0, halve lr after 3 epochs without validation gain; early stop after 5; best-validation checkpoint tested |
| Batches | 32 × 10 s; 4,000 training and 1,000 validation steps per epoch |
| Metrics | DNSMOS (SIGMOS, BAKMOS, OVRLMOS), PESQ, SI-SDR |
| Framework | ULCNet re-implemented in TensorFlow from the original paper's specification |

All values **Reported**; fixed hyperparameters, one training run per model, no variance or seed information.[^fast-ulcnet-paper]

## Reported results

Table 1 (objective metrics; best per column bolded in the paper):[^fast-ulcnet-paper]

| Test length | Model | OVRLMOS | SIGMOS | BAKMOS | PESQ | SI-SDR |
| --- | --- | --- | --- | --- | --- | --- |
| 10 s | ULCNet | 3.10 | 3.39 | 3.96 | 2.62 | 16.24 |
| 10 s | Fast-ULCNet | 3.09 | 3.39 | 3.95 | 2.51 | 15.99 |
| 10 s | Fast-ULCNet comfi | 3.09 | 3.39 | 3.97 | 2.50 | 16.01 |
| 90 s | ULCNet | 3.09 | 3.39 | 3.95 | 2.66 | 16.89 |
| 90 s | Fast-ULCNet | 2.93 | 3.39 | 3.62 | 2.24 | 13.58 |
| 90 s | Fast-ULCNet comfi | 3.10 | 3.39 | 3.99 | 2.51 | 16.48 |

Table 2 (complexity; the comfi variant "yields identical results" and is omitted):

| Model | Params (M) | MACs (M) | RTF Pi 3 B+ | RTF Cortex-A53 |
| --- | --- | --- | --- | --- |
| ULCNet | 0.685 | 2.057 | 0.976 | 0.927 |
| Fast-ULCNet | 0.338 | 1.691 | 0.657 | 0.604 |

Recomputed from the tables (**Observed**): parameters −50.7% (the abstract's "more than half" holds), MACs −17.8% (0.366M, as stated), RTF −32.7% (Pi 3 B+) and −34.8% (A53), mean 33.8% (the abstract's "34% on average"). The MACs unit is not stated per second or per frame, and the paper does not say what audio the 10,000 RTF iterations ran on.[^fast-ulcnet-paper]

### Reading the claims

- **"On par with ULCNet"** holds for DNSMOS and, with the comfi variant, for 90 s DNSMOS. PESQ trails ULCNet by 0.11–0.12 (10 s) and 0.15 (90 s, comfi), and SI-SDR by 0.23–0.25 (10 s) and 0.41 (90 s, comfi); the paper itself says PESQ and SI-SDR "marginally favor" ULCNet (**Observed**).[^fast-ulcnet-paper]
- **Plain Fast-ULCNet degrades on long input**: at 90 s OVRLMOS falls 3.09→2.93, BAKMOS 3.95→3.62, PESQ 2.51→2.24, SI-SDR 15.99→13.58, while ULCNet and the comfi variant do not fall (**Observed**). Mechanism and fix: [Comfi-FastGRNN and RNN State Drift](comfi-fastgrnn-state-drift.md).[^fast-ulcnet-paper]
- **Speed is measured as RTF, not latency in milliseconds**; algorithmic look-ahead, causality of each layer and frame-by-frame streaming behavior are not stated, although the 32 ms window and 16 ms hop imply a minimum 32 ms analysis delay (**Synthesis**).[^fast-ulcnet-paper]

## Voice-pipeline implications

- **Budget class**: an RTF near 0.6 on one in-order Cortex-A53 thread leaves about 40% of that core for everything else; ULCNet itself sat at 0.93–0.98, close to the real-time limit on those devices (**Observed** from Table 2). Hardware differs from the Xeon/M1 CPU RTFs in [FastEnhancer](fastenhancer.md) (0.0058–0.022), so the numbers are not comparable (**Synthesis**).
- **Always-on use**: voice agents run enhancement over streams far longer than 10 s, and the paper's 90 s experiment shows a drift failure with plain FastGRNN that appears only after tens of seconds (**Synthesis** from the figure and Table 1). Any recurrent enhancer deployed continuously needs a multi-minute soak test, not 10 s clips; compare [DPDFNet Design, Training and Evaluation](dpdfnet-design-and-training.md), which addresses a different always-on failure by fine-tuning on long sequences.
- **Unproven for ASR**: quality gains in DNSMOS/PESQ do not establish lower WER; see [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) for evidence that enhancement can hurt recognition (**Synthesis**).
- **Data and language**: DNS-2020 English-dominant speech at 16 kHz; no Vietnamese or reverberant evaluation (the test set is non-reverberant) and no echo, overlap or multi-speaker handling (**Observed** absence).[^fast-ulcnet-paper]
- **Availability**: the paper states open-source code at `github.com/narrietal/Fast-ULCNet` and an online demo; neither was inspected, so license, weights and a streaming or TFLite export are **Unverified**.[^fast-ulcnet-paper]

## Relationships

- Builds on ULCNet (Shetu et al., ICASSP 2024), whose paper is not in `raw/`; its claims (3–4× lower cost than prior work, channel-wise reorientation and power-law compression) are repeated here only as the Fast-ULCNet authors state them (**Reported**).[^fast-ulcnet-paper]
- Uses [Comfi-FastGRNN and RNN State Drift](comfi-fastgrnn-state-drift.md), the paper's drift-compensated FastGRNN layer.
- Alternative to [UL-UNAS](ul-unas.md) (171k parameters, 35M MACS/s, no device RTF), [FastEnhancer](fastenhancer.md) (CPU RTFs on Xeon/Apple silicon), and [DPDFNet](dpdfnet.md) (2.3–3.6M parameters, NPU RTFs): different datasets, baselines and metrics, so no table is directly comparable; Fast-ULCNet is not compared with any of them in its paper (**Synthesis**).
- Supports the noise-preprocessing question in [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) as a low-compute candidate, without ASR evidence (**Synthesis**).

## Coverage and limits

- Ledger: entry point `Template.tex` (all text, both tables, equations 1–5, and abstract read) and `00README.json` (pdflatex toplevel declaration). Figures `Comfi-FastGRNN_diagram_0_margin.pdf`, `Fast_ULCNet_diagram.pdf`, and `drift_vs_signal_dejavusans.pdf` were rendered and viewed. `refs.bib` was used only to identify cited papers (uninspected); `spconf.sty`, `IEEEbib.bst` and `strings.bib` are style/bibliography boilerplate and excluded. The paper was not compiled; no code was executed.
- No ablation separates the effect of FastGRNN from other changes, no baseline other than the authors' own ULCNet re-implementation is reported, and the re-implementation's parameter count (0.685M) is not compared against the original paper's figure in the published text (an editorial LaTeX comment says the replication is about 3,000 parameters smaller; it is commented out and not treated as a claim).
- The 90 s test set repeats each 10 s clip nine times, so it measures duration robustness, not novel long-form content. DNSMOS is a predicted metric and the authors list perceptual (listening) evaluation as future work.
- All figures are self-reported and unreproduced; there is no publication venue acceptance statement beyond the ICASSP-2026 template. No sensitive values were found.

[^fast-ulcnet-paper]: [Fast-ULCNet LaTeX source](../raw/arXiv-2601.14925v1-Fast-ULCNet/Template.tex) (arXiv 2601.14925v1) — locators: abstract and Sec. 1 (claims, GitHub and demo footnotes); Sec. 2.2 and Fig. 3 (`Fast_ULCNet_diagram.pdf`); Sec. 3.1.1 (architecture settings, sigmoid gate, γ/λ initialization); Sec. 3.1.2 and Eq. 5 (loss); Sec. 3.1.3 (dataset, 85/15 split, test set); Sec. 3.1.4 (training setup); Sec. 3.2.1 and Table 1 (objective evaluation, 10 s and 90 s sets); Sec. 3.2.2 and Table 2 (parameters, MACs, RTF on Pi 3 B+ and Cortex-A53); Sec. 4 (conclusion and future work).
