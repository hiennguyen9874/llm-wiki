---
type: Concept
title: DPDFNet Design, Training and Evaluation
description: How DPDFNet is built and trained: DeepFilterNet2 ERB-gain plus deep-filter framework, causal DPRNN blocks in both encoder branches, over-attenuation loss with sensitivity analysis, long-sequence fine-tuning for always-on use, the PRISM min-max composite metric, and branch ablation, with attribution of gains and metric caveats.
tags: [pipeline, speech-enhancement, denoising, streaming, training, evaluation, paper]
status: draft
created: 2026-10-24
generated: { by: llm-wiki-agent/1, at: 2026-10-24T15:00:00Z }
stale_after: 2027-10-24
sources:
  - id: dpdfnet-paper
    resource: ../raw/arXiv-2512.16420v3-DPDFNet/main_elsevier.tex
    scope: ../raw/arXiv-2512.16420v3-DPDFNet/
    kind: paper
    revision: arXiv 2512.16420v3
    title: "DPDFNet: Boosting DeepFilterNet2 via Dual-Path RNN (LaTeX source)"
  - id: dpdfnet-readme
    resource: ../raw/arXiv-2512.16420v3-DPDFNet/README-github.md
    kind: documentation
    title: ceva-ip/DPDFNet GitHub README (undated capture)
---

DPDFNet changes one thing architecturally (causal dual-path RNN blocks in both encoder branches of DeepFilterNet2) and two things in training (an over-attenuation loss and a long-sequence fine-tuning stage); the paper reports all three help. Recomputing its multilingual low-SNR table shows the training changes account for most of the Baseline-to-DPDFNet-8 gain on SI-SNR (about 72%) and about half on PESQ, so the architecture alone is not the main driver, and no compute-matched control isolates what is specific to "dual-path". Results, model zoo and usage are in [DPDFNet](dpdfnet.md) (**Reported** design; gain attribution **Synthesis** from the paper's tables).[^dpdfnet-paper]

## Signal model and framework (inherited from DeepFilterNet2)

- Noisy signal x = s * r + n (clean speech convolved with a room impulse response, plus additive noise). Features come from an STFT with a 20 ms window, 10 ms hop and Vorbis window at 16 kHz: complex features X_df are the lowest 96 bins (up to 4.8 kHz), and ERB features X_erb are the power spectrogram through 32 ERB filters (**Reported**).[^dpdfnet-paper]
- Stage 1 (masking): the network predicts ERB gains, expanded to full band with the transposed ERB filter bank and multiplied onto the noisy spectrogram. Stage 2 (reconstruction): the network predicts complex deep-filter (DF) coefficients applied to the masked spectrogram below 4.8 kHz, Y(k,f) = Σ C(k,i,f)·Y_G(k−i+ℓ,f) with DF order N = 5 and look-ahead ℓ = 2 frames (**Reported**).[^dpdfnet-paper]
- DeepFilterNet2 encoder: two parallel conv branches (separable conv, 64 channels, kernel (1,3) over time × frequency, batch norm, ReLU), flattened and concatenated, then grouped linear (GLinear) and a GRU. The ERB decoder has two GRUs, GLinear and transposed conv blocks with skip connections and a sigmoid output; the DF decoder has GLinear, two GRUs and GLinear with a skip from the encoder (**Reported**; structure confirmed in `DPDFNet_deepfilternet.png`, which shows four conv blocks in the ERB branch and two in the Complex branch, an inference from the figure rather than a paper statement).[^dpdfnet-paper]

## DPRNN block and placement

- Input tensor B × T × F × D. **Intra stage**: reshape to (B·T) × F × D and run a bidirectional GRU along frequency, one sequence per frame, zero initial state per frame; the figure shows Bi-GRU → fully connected (FC) → LayerNorm (LN) with a residual connection. **Inter stage**: reshape to (B·F) × T × D and run a unidirectional GRU along time, one sequence per frequency bin with a single shared parameter set but separate state, then FC, LN and a residual. Because the bidirectional part runs only inside one frame and the time RNN is unidirectional with zero initial state, the block is causal (**Reported**; figure **Observed**).[^dpdfnet-paper]
- The FC + LN after each stage follows DPCRN; DPRNN comes from Luo et al. (**Reported**).[^dpdfnet-paper]
- Placement: N blocks are inserted immediately after the convolutional stack of each of the two encoder branches (Complex and ERB) and before the concatenation and GLinear + GRU fusion (the figure shows a GLinear between the Complex-branch DPRNN and the concatenation); the conv channel count equals the feature dimension D. N = 2, 4, 8 yields DPDFNet-2/-4/-8; N = 0 is the retrained Baseline (**Reported**).[^dpdfnet-paper]
- Cost: the added blocks raise MACs from 0.36 G to 1.35, 2.36 and 4.37 G but parameters only from 2.31M to 2.49, 2.84 and 3.54M, because the per-frequency time GRU shares parameters across all frequencies while computing over every bin (**Observed** from the table; mechanism **Synthesis**).[^dpdfnet-paper]

## Training recipe

| Item | Value |
| --- | --- |
| Clean speech | DNS4 (760 h, six languages, 3,230 speakers) downsampled to 16 kHz, plus 4,000 h English Multilingual LibriSpeech; all clean audio passed through DPCRN to remove residual noise |
| Noise / RIR | DNS4 noise (181 h, 150 classes) and RIRs, plus MUSAN and FSD50K noise clips |
| Online augmentation | random second-order filtering, gain perturbation, reverberation with early-reflection targets (model learns to remove late reverberation, keep direct path and early reflections) |
| Examples | 3 s speech chunks, SNR sampled from −5 to 40 dB |
| Schedule | 1.6M iterations, batch 32, AdamW, cosine annealing, peak LR 1e-3 |
| Fine-tuning | batch 1, continuous 30–40 s segments, 5,000 iterations, fixed LR 1e-5 |

- 1.6M × 32 × 3 s = 153.6M s = 42,667 h, matching the paper's "42,667 hours of speech"; the fine-tuning stage sees 5,000 × 30–40 s ≈ 42–56 h, about 0.1% as much audio as the main run (**Observed**, recomputed).[^dpdfnet-paper]
- Vietnamese clean speech is not named in the training data; DNS4's six languages are not listed in the paper, and the 4,000 h MLS addition is English (**Observed** absence).[^dpdfnet-paper]
- Baseline and DPDFNet were trained on this data, whereas the DeepFilterNet2/3 comparison rows are the official checkpoints with their own training data; the paper treats the retrained Baseline as the controlled architecture comparison and reports it as comparable to DeepFilterNet2/3 (**Reported**).[^dpdfnet-paper]

## Loss: multi-resolution plus over-attenuation (OA)

- Multi-resolution loss L_MR from DeepFilterNet2: STFT windows of 5, 10, 20 and 40 ms, squared L2 distance between compressed magnitudes |·|^c (c = 0.3) and between compressed complex values (compressed magnitude with phase), summed over resolutions (**Reported**).[^dpdfnet-paper]
- OA loss L_OA: the same expression multiplied by a binary mask M_i(k,f) = 1 where the clean magnitude exceeds the enhanced magnitude at that bin, i.e., it penalizes only bins where the output is too quiet. Total loss = λ_MR·L_MR + λ_OA·L_OA with λ_MR = λ_OA = 500 (**Reported**).[^dpdfnet-paper]
- Reading: because masked bins appear in both terms, under-estimation is penalized with total weight 1000 versus 500 for over-estimation, an asymmetric loss that favors keeping speech energy (**Synthesis**).

### OA sensitivity (λ_OA ∈ {0, 500, 1000})

Two diagnostics on the multilingual set: speech preservation ratio SPR = Σ_speech r_e / Σ_speech r_c (below 1 means speech attenuated) and non-speech residual level NSRL_dB = 20·log10(mean non-speech r_e / mean speech r_c) (lower is better), with r the frame RMS. Values read from `oa_sensitivity_analysis.png` (approximate):[^dpdfnet-paper]

| λ_OA | SPR | NSRL (dB) |
| --- | --- | --- |
| 0 | ≈ 0.83 | ≈ −57.3 |
| 500 (chosen) | ≈ 0.89 | ≈ −52.5 |
| 1000 | ≈ 0.94 | ≈ −51.9 |

- Going from 0 to 500 buys about +0.06 SPR for about 4.8 dB more residual; going from 500 to 1000 buys about +0.05 SPR for about 0.6 dB. By this plot the second step is the cheaper trade, so "500 is balanced" is the authors' judgment rather than a knee in the curve; all residuals are below about −51 dB relative to speech level, and no listening test or ASR result says which is preferable (**Synthesis** from approximate plot readings).[^dpdfnet-paper]
- The model size used for this analysis and the speech/non-speech frame labeling method are not stated (**Observed** absence).

## Fine-tuning for always-on streaming

- Problem observed after the main run: in continuous streaming the models truncated the beginning of speech after extended silence (3–4 s) and sometimes leaked background noise after such pauses. The authors hypothesize that stateful RNN components never saw long state transitions because training used short isolated 3 s segments (**Reported**, hypothesis not tested).[^dpdfnet-paper]
- `fine_tuning_case_spectrogram.png` (16 s example, noisy / Baseline without fine-tuning / Baseline with fine-tuning / clean reference) shows the clip's speech segment around 7.1–8.2 s, after about two seconds of non-speech, partly erased by the non-fine-tuned model and restored by the fine-tuned one (**Observed**, one qualitative example).[^dpdfnet-paper]

## Gain attribution on the multilingual set

| Step | PESQ | SI-SNR (dB) | PRISM | Change |
| --- | --- | --- | --- | --- |
| Baseline (DeepFilterNet2 architecture) | 2.85 | 10.25 | 0.79 | |
| + OA loss | 2.92 | 11.21 | 0.85 | +0.07 PESQ, +0.96 SI-SNR |
| + fine-tuning | 3.04 | 13.27 | 0.91 | +0.12 PESQ, +2.06 SI-SNR |
| DPDFNet-2 | 3.14 | 13.72 | 0.95 | +0.10 PESQ, +0.45 SI-SNR |
| DPDFNet-4 | 3.18 | 14.11 | 0.98 | +0.04 PESQ, +0.39 SI-SNR |
| DPDFNet-8 | 3.20 | 14.47 | 1.00 | +0.02 PESQ, +0.36 SI-SNR |

- OA + fine-tuning contribute +0.19 of the +0.35 PESQ (54%) and +3.02 of the +4.22 dB SI-SNR (72%) between Baseline and DPDFNet-8; the DPRNN depth contributes the rest (**Observed**, recomputed).[^dpdfnet-paper]
- Diminishing returns: DPDFNet-2 → -4 adds about 1.0 G MACs for +0.04 PESQ and DPDFNet-4 → -8 adds about 2.0 G MACs for +0.02 PESQ. Together with the NPU result that DPDFNet-8 is not real time while DPDFNet-4 just is (see [DPDFNet](dpdfnet.md)), the middle size is the practical operating point (**Synthesis**).
- The OA loss alone lowers several NISQA scores (MOS 3.95 → 3.80, NOI 4.37 → 4.28, DIS 4.17 → 4.07, COL 3.87 → 3.79) while raising PESQ and SI-SNR; fine-tuning restores NISQA MOS to 3.96 (**Observed**). The paper's results text says the Baseline with OA loss and fine-tuning "surpasses both" DeepFilterNet2 and 3, yet it is 0.01 below DeepFilterNet3 on P.808 (3.21 vs 3.22), a negligible exception (**Observed**).[^dpdfnet-paper]
- Each size appears to be a single training run; there is no seed variance (**Unverified**).

## Branch ablation (DPDFNet-2, multilingual set)

| Metric | Baseline | ERB only | Complex only | Both |
| --- | --- | --- | --- | --- |
| PESQ | 3.04 | 3.04 | 3.12 | 3.14 |
| STOI % | 91.6 | 91.7 | 92.5 | 92.6 |
| SI-SNR | 13.27 | 13.43 | 13.74 | 13.72 |
| NISQA MOS | 3.96 | 4.02 | 4.05 | 4.06 |
| PRISM | 0.06 | 0.26 | 0.78 | 0.99 |

- Both single-branch variants improve on the Baseline and the Complex branch gives most of the gain (PESQ +0.08 of +0.10, 80%); inserting in both branches is best on almost every metric, except SI-SNR where Complex-only is 0.02 dB higher (**Observed**).[^dpdfnet-paper]
- The paper does not run a compute-matched control (e.g., extra GRU or conv layers with the same MACs), a causal-versus-bidirectional intra-stage comparison, or ablations at N = 4 or 8, so what is specific to the dual-path layout is unsupported by an ablation (**Observed** absence; **Synthesis**).

## PRISM (Performance Relative Integrated Scaled Metric)

- Definition: each metric is min-max normalized across all models in a table (lowest to 0, highest to 1); normalized scores are averaged within three groups (intrusive PESQ/STOI/SI-SNR; DNSMOS SIG/BAK/OVL/P.808; NISQA MOS/NOI/DIS/COL/LOUD); DNSMOS and NISQA are combined into a non-intrusive score; PRISM is the mean of the intrusive and non-intrusive scores. The paper contrasts it with URGENT's rank-based aggregation, saying min-max preserves magnitude gaps. DNS4 has no clean reference, so its PRISM can only use non-intrusive groups (the paper does not state this; **Synthesis**).[^dpdfnet-paper]
- Caveats (**Observed**/**Synthesis**): scores depend on which models are in the table, so they are not comparable across tables (Noisy scores 0.04, 0.23 and 0.12 on the three sets), and the same models get different values when fewer are normalized together (Baseline with fine-tuning 0.91 in the 18-row main table but 0.06 in the four-model branch ablation, where DPDFNet-2 is 0.99 versus 0.95). Equal weighting between groups means NISQA's five sub-scores carry half of the non-intrusive score, and on DNS4 (no intrusive group) PRISM rests entirely on two learned MOS predictors. Min-max over a narrow range stretches small gaps: PESQ 3.04 versus 3.14 in the ablation becomes a PRISM gap of 0.93.[^dpdfnet-paper]
- The README states the authors rely on PRISM for aggregate quality reporting and provide `pesq_stoi_sisnr_calc.py`, which auto-aligns reference and enhanced signals before scoring; DNSMOS uses the official DNS Challenge `dnsmos_local.py` and NISQA v2 its official `nisqa_predict.py`. The PRISM script itself is not listed in the README (**Reported**).[^dpdfnet-readme]

## Relationships

- Built on DeepFilterNet2 and compared with DeepFilterNet3; results, model zoo, deployment and usage are in [DPDFNet](dpdfnet.md).
- Contrasts with [FastEnhancer Design Choices and Ablations](fastenhancer-design-and-ablations.md): FastEnhancer ablates DPRNN and DPT against its GRU-plus-frequency-attention RNNFormer on CPU RTF and finds DPRNN no better (lower SISDR at mid-to-large sizes in its approximate plot readings), whereas DPDFNet adopts DPRNN inside a DeepFilterNet2 backbone for quality and reports only NPU RTF; the two papers use different backbones and metrics, so neither tests the other's design under its own conditions (**Synthesis**).
- Shares the grouped dual-path recurrence idea with [UL-UNAS Design Components and NAS](ul-unas-design-and-nas.md), which keeps GTCRN's grouped dual-path RNN; DPDFNet's blocks are ungrouped GRU DPRNN (**Synthesis**).
- Informs the noise-preprocessing question in [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) with an always-on silence-to-speech failure mode that matters for endpointing (**Synthesis**).

## Coverage and limits

- Same source coverage as [DPDFNet](dpdfnet.md): LaTeX read in full, all six figures viewed, README read, bibliography and cited papers (DeepFilterNet2/3, DPRNN, DPCRN, URGENT, NISQA, DNSMOS) not followed, no compilation or execution. Equations and architecture details come from the authors' text; training code, checkpoints and the PRISM implementation were not inspected.
- OA-sensitivity values are approximate plot readings. The number of DNS4 languages and the conv block counts per branch are not stated in the paper text. No evidence on training cost in GPU-hours, hardware, or seed variance. No sensitive values were found.

[^dpdfnet-paper]: [DPDFNet LaTeX source](../raw/arXiv-2512.16420v3-DPDFNet/main_elsevier.tex) (arXiv 2512.16420v3) — locators: Sec. 2.1 Denoising Framework; Sec. 2.2 DeepFilterNet2 Architecture; Sec. 2.3 Dual-Path RNN Block and Sec. 2.4 DPDFNet with Fig. 1 (`DPDFNet_dprnn.png`, `DPDFNet_deepfilternet.png`); Sec. 3.1 Datasets and Augmentations; Sec. 3.3 Loss Functions (L_MR, L_OA, λ values); Sec. 4.1 Implementation Details; Sec. 4.2 Fine-Tuning with `fine_tuning_case_spectrogram.png`; Sec. 4.3 PRISM and `performance_complexity_footprint.png`; Sec. 4.4 OA-Loss Sensitivity Analysis with `oa_sensitivity_analysis.png`; Table 1 `tab:overall_results`; Sec. 4.6 Architectural Ablation, Table `tab:branch_ablation`.

[^dpdfnet-readme]: [DPDFNet GitHub README](../raw/arXiv-2512.16420v3-DPDFNet/README-github.md) (undated capture) — locator: `Evaluation Metrics` (intrusive script with auto-alignment, official DNSMOS and NISQA tools, PRISM reference).
