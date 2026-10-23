---
type: Concept
title: UL-UNAS
description: Ultra-lightweight causal U-Net speech-enhancement model (171k parameters, 35M MACS/s, zero look-ahead) found by MACS-aware neural architecture search, with reported DNS3 and VCTK-DEMAND results versus GTCRN, LiSenNet, DeepFilterNet and no ASR, latency, or deployment evidence.
tags: [pipeline, speech-enhancement, denoising, edge, causal, paper, nas]
status: draft
created: 2026-10-24
generated: { by: llm-wiki-agent/1, at: 2026-10-24T20:00:00Z }
stale_after: 2027-10-24
sources:
  - id: ulunas-paper
    resource: ../raw/arXiv-2503.00340v2-UL-UNAS/main.tex
    scope: ../raw/arXiv-2503.00340v2-UL-UNAS/
    kind: paper
    revision: arXiv 2503.00340v2
    title: "UL-UNAS: Ultra-Lightweight U-Nets for Real-Time Speech Enhancement via Network Architecture Search (LaTeX source)"
---

UL-UNAS (Rong, Yang, Wang, Hu, Zhu, Chen, Lu; Nanjing University / Horizon Robotics) is a time-frequency-domain speech-enhancement (SE) model built on the GTCRN backbone: a noisy log-power spectrogram goes through band merging, a five-block convolutional encoder, a grouped dual-path RNN, a mirrored decoder, and band splitting to a sigmoid magnitude mask applied to the noisy magnitude with the noisy phase reused. The final model has 171k parameters and about 35M MACS per second of audio, runs with 0 ms look-ahead, and reports PESQ 2.30 on the authors' DNS3 test set (GTCRN 2.10, LiSenNet 2.23) and 3.09 on VCTK-DEMAND when trained with an added PESQ loss. For a voice pipeline it is a candidate edge-sized noise-suppression front end; the paper measures speech-quality metrics only, with no ASR word-error rate, wall-clock latency, or streaming implementation (**Reported**).[^ulunas-paper] How its blocks and search were built is in [UL-UNAS Design Components and NAS](ul-unas-design-and-nas.md).

## Architecture summary

- **Backbone**: GTCRN's band merging (BM, 192 high-frequency bins mapped to 64 ERB bands, 65 low bins kept, giving 129 features), band splitting (BS), and grouped dual-path RNN (G-DPRNN) are kept; only the convolutional encoder/decoder blocks are replaced by XConv, XDWS, and XMB blocks, with transposed convolutions in the decoder (**Observed** from Fig. 1 and text).[^ulunas-paper]
- **Output**: an IRM-style magnitude mask in (0, 1) via sigmoid; the enhanced spectrogram combines the masked magnitude with the noisy phase. The authors chose IRM over complex ratio masking because they observed cIRM predictions collapsing to near-zero imaginary parts at this model size (**Reported**, attributed to insufficient capacity).[^ulunas-paper]
- **Discovered configuration** (five encoder blocks): types XConv, XMB, XDWS, XMB, XDWS; frequency strides 2, 2, 1, 1, 1; groups 1, 2, 2, 2, 2; channels 12, 24, 24, 32, 16; kernels (3,3), (2,3), (2,3), (1,5), (1,5) (**Reported**).[^ulunas-paper]
- **Front end**: 16 kHz audio, 32 ms Hanning window, 16 ms hop, 512-point FFT. Together with 0 ms look-ahead this implies a 32 ms analysis window and 16 ms frame step for a streaming port, but the paper does not state a measured or algorithmic end-to-end latency (**Synthesis** from the stated STFT settings).[^ulunas-paper]
- **Complexity metric**: MACS from `ptflops` at a fixed 1-second input, not tied to hardware. The paper argues MACS predicts edge latency better than parameter count (**Reported**; the argument is not tested on a device).[^ulunas-paper]

## Reported results

All models in the DNS3 table were retrained by the authors under the same setup; the training set is DNS3 (2,000 h; 720,000 ten-second pairs mixed with RIRs and noise at -5 to 15 dB SNR) plus the DiDiSpeech Mandarin corpus, evaluated on 1,000 synthesized test pairs (**Reported**).[^ulunas-paper]

| Model (DNS3 test) | Look-ahead (ms) | Params (k) | MACS (M/s) | SISNR | PESQ | ESTOI ×100 | DNSMOS OVRL / SIG / BAK | DNSMOS P.808 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Noisy | – | – | – | 5.61 | 1.40 | 66.90 | 1.63 / 2.05 / 1.86 | 2.82 |
| CRN-small | 0 | 195 | 35 | 11.34 | 2.07 | 75.22 | 2.62 / 2.95 / 3.84 | 3.49 |
| DPCRN-small | 0 | 15 | 38 | 10.67 | 2.01 | 74.29 | 2.59 / 2.94 / 3.84 | 3.49 |
| DeepFilterNet | 0 | 1780 | 358 | 12.20 | 2.13 | 75.92 | 2.73 / 3.07 / 3.86 | 3.43 |
| GTCRN | 0 | 48 | 34 | 11.44 | 2.10 | 75.71 | 2.63 / 2.97 / 3.82 | 3.50 |
| LiSenNet | 32 | 37 | 56 | 12.12 | 2.23 | 77.02 | 2.70 / 3.04 / 3.85 | 3.55 |
| **UL-UNAS** | 0 | 171 | 35 | 12.30 | 2.30 | 78.24 | 2.71 / 3.05 / 3.88 | 3.56 |

- Versus GTCRN at nearly equal MACS (35M vs 34M): PESQ +0.20, OVRL +0.08, P.808 +0.06 (differences recomputed from the table, **Observed**).[^ulunas-paper]
- Versus DeepFilterNet: DeepFilterNet has about 10× the MACS (358 vs 35) and about 10× the parameters (1780k vs 171k), yet DeepFilterNet scores higher on DNSMOS OVRL (2.73 vs 2.71) and SIG (3.07 vs 3.05); UL-UNAS leads on SISNR, PESQ, ESTOI, BAK and P.808. The paper's phrasing "competitive or superior" is accurate; "best on all metrics" would not be (**Observed**).[^ulunas-paper]
- LiSenNet requires 32 ms look-ahead from its Griffin–Lim phase refinement, which UL-UNAS avoids (**Reported**).[^ulunas-paper]

| Model (VCTK-DEMAND test) | Params (M) | MACS (G/s) | SISNR | PESQ | STOI |
| --- | --- | --- | --- | --- | --- |
| Noisy | – | – | 8.45 | 1.97 | 0.921 |
| RNNoise (2018) | 0.06 | 0.04 | – | 2.29 | – |
| DeepFilterNet (2022) | 1.80 | 0.35 | 16.63 | 2.81 | 0.942 |
| GTCRN (2024) | 0.05 | 0.03 | 18.83 | 2.87 | 0.940 |
| LiSenNet† / ‡ (2024) | 0.04 | 0.06 | – | 2.95 / 3.07 | 0.937 / 0.939 |
| UL-UNAS† | 0.17 | 0.03 | 18.25 | 2.96 | 0.941 |
| UL-UNAS‡ | 0.17 | 0.03 | 18.48 | 3.09 | 0.941 |

† trained without PESQ loss; ‡ with additional PESQ loss (`torch-pesq`). Larger models in the paper's table (PercepNet 2.73, FullSubNet 2.89, GaGNet 2.94, Fast FullSubNet 2.79 PESQ) are omitted here; FullSubNet and Fast FullSubNet figures were taken from the LiSenNet paper and others partly from original papers rather than retrained (**Reported**).[^ulunas-paper]

- The paper says UL-UNAS has "the best performance among all the models" on VCTK-DEMAND. From its own table that holds for PESQ, but GTCRN has higher SISNR (18.83) and DeepFilterNet higher STOI (0.942) (**Observed**).[^ulunas-paper]

## Voice-pipeline implications

- **Fit**: at about 35M MACS/s the model is in the budget class of a CPU or microcontroller-scale noise-suppression stage ahead of VAD or STT; this is **Synthesis** from the MACS figure, since no device latency or real-time factor is reported.[^ulunas-paper]
- **Unproven for ASR**: SE gains in PESQ/DNSMOS do not establish lower WER; [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) records studies where enhancement degraded ASR, so any use before STT needs an A/B test on WER in the target language (**Synthesis**).
- **Language and rate**: trained on DNS3 plus Mandarin (DiDiSpeech) and VCTK-DEMAND English at 16 kHz; no Vietnamese or other-language evaluation (**Observed** absence).[^ulunas-paper]
- **Scope**: single-channel noise and reverberation suppression (target preserves the first 100 ms of reflections). It does not address echo cancellation, speaker separation, or overlapped speech (**Observed**).[^ulunas-paper]

## Relationships

- Compared with and an alternative to [Facebook Denoiser](facebook-denoiser.md) (causal waveform model, no quality metrics in its README), [ClearVoice](clearvoice.md) (larger MossFormer/FRCRN checkpoints with PESQ tables), and [Resemble Enhance](resemble-enhance.md) (offline 44.1 kHz enhancer); only UL-UNAS publishes a MACS budget (**Synthesis**).[^ulunas-paper]
- Extends GTCRN and compares with LiSenNet and DeepFilterNet; those papers are not in `raw/` and their numbers are used here only as the authors report them (**Reported**).[^ulunas-paper]
- Supports the noise-preprocessing question in [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) as a low-compute candidate, without ASR evidence (**Synthesis**).
- Design and search details: [UL-UNAS Design Components and NAS](ul-unas-design-and-nas.md).
- Related to [DPDFNet](dpdfnet.md): a larger DeepFilterNet2-derived causal enhancer that reports GTCRN at different VoiceBank-DEMAND numbers (PESQ 2.60, SI-SNR 21.41, with a 70 Hz high-pass on references) than the 2.87 / 18.83 used here, so tables across the papers are not comparable (**Synthesis**).
- Related to [FastEnhancer](fastenhancer.md): a later GTCRN-comparison paper that reports CPU real-time factors (0.012–0.022 on one Xeon thread for its Tiny and Base sizes) and argues MACs mispredict streaming speed; its GTCRN VoiceBank-DEMAND figures (SISDR 18.8, PESQ 2.87, STOI 0.940) match this paper's GTCRN row, but the two papers use different training recipes, so UL-UNAS's PESQ 3.09 and FastEnhancer-B's 3.13 are not a controlled comparison (**Synthesis**).
- Related to [Fast-ULCNet](fast-ulcnet.md): another edge-sized enhancer (0.338M parameters) that reports MACs and Cortex-A53/Pi 3 B+ RTFs but compares only against ULCNet on DNS-2020, so it is not directly comparable with the tables here (**Synthesis**).
- Related to [CoFi-Lite](cofi-lite.md): a later paper from the same group that reuses the UL-UNAS MB block (cTFA swapped for TRA) in a two-path design at 12.87M MACs/s; it lists UL-UNAS at PESQ 2.25 / 34.91M MACs/s on DNS3, below the 2.30 reported here, so the two tables are not interchangeable (**Synthesis**).

## Coverage and limits

- Ledger: entry point `main.tex` (all 610 lines read, including related work, method, tables 1–7, ablations, and conclusion) and `00README.json` (pdflatex toplevel declaration). Figures `fig_ulunas.pdf`, `fig_ctfa.pdf`, and `fig_reward.pdf` were rendered and viewed; `fig_base_blocks`, `fig_xblocks`, `fig_aprelu_1–4`, `fig_nas`, and `fig_controller` were not viewed (their captions in `main.tex` cover the content). `ref.bib` was used only to resolve a few citations; the cited papers are uninspected. The paper was not compiled.
- Source code and audio demos are said to be at `github.com/Xiaobin-Rong/ul-unas`; the repository, weights, license, and any streaming or ONNX export were not inspected, so availability, license, and a runnable causal implementation are unknown (**Unverified**).
- The LaTeX shows editorial `\rev` markup; the arXiv v2 text is treated as final. No publication venue or date appears in the source.
- All figures are self-reported on authors' own retrained baselines; none was reproduced. Whether results vary across seeds is asserted ("relatively stable") without numbers. No sensitive values were found.

[^ulunas-paper]: [UL-UNAS LaTeX source](../raw/arXiv-2503.00340v2-UL-UNAS/main.tex) (arXiv 2503.00340v2) — locators: abstract and Sec. I (contributions: 35M MACS, 171k parameters, PESQ 3.09); Sec. III-A (problem formulation, IRM masking) and III-B (model overview, Fig. 1); Sec. IV-A (datasets), IV-B (BM setup, STFT and training configuration), IV-C (baselines and metrics); Table IV (discovered configuration); Table VI (DNS3 comparison); Table VII (VCTK-DEMAND comparison); Sec. V-B (comparison analysis); Fig. fig_ulunas.pdf; `ptflops` footnote in Sec. IV-B.
