---
type: Concept
title: CoFi-Lite Design and Ablations
description: How CoFi-Lite splits speech enhancement into a coarse full-band path and a fine sub-2 kHz path joined by Cross-Path Fusion, with its input features, sequential mask equation, configuration, training recipe, and the reported ablations on paths, CPF, compression ratios and cutoff frequency.
tags: [pipeline, speech-enhancement, denoising, edge, architecture, ablation, paper]
status: draft
created: 2026-10-24
generated: { by: llm-wiki-agent/1, at: 2026-10-24T20:00:00Z }
stale_after: 2027-10-24
sources:
  - id: cofilite-paper
    resource: ../raw/arXiv-2607.10142v1-CoFi-Lite/main.tex
    scope: ../raw/arXiv-2607.10142v1-CoFi-Lite/
    kind: paper
    revision: arXiv 2607.10142v1
    title: "CoFi-Lite: Pushing the Limits of Ultra-Lightweight Speech Enhancement (LaTeX source)"
---

The authors' preliminary experiments found that naively shrinking a GTCRN-style convolutional recurrent network (CRN) degrades quickly, especially in low-frequency bands where noise stays under-suppressed. CoFi-Lite therefore spends capacity unevenly: a **coarse path** works on a heavily compressed full-band magnitude envelope, a **fine path** works on the uncompressed low band (bins 0–64, up to 2 kHz) using magnitude and phase, and a **Cross-Path Fusion (CPF)** module at the bottleneck lets the two exchange information. In the ablations CPF is the largest single gain (PESQ +0.14 at the same budget), while pushing the fine path to deeper compression or raising the cutoff beyond 2 kHz does not help (**Reported**).[^cofilite-paper] Results versus other models are in [CoFi-Lite](cofi-lite.md).

## Signal flow (Fig. 1a, Eq. 1–3)

- STFT of the noisy 16 kHz signal (32 ms square-root Hanning window, 16 ms hop, FFT 512), then two inputs: `I_c` for the coarse path and `I_f` for the fine path. Each path is an encoder, two inter-frame GRUs (Inter-RNN, from DPCRN) around the CPF bottleneck, and a decoder (**Observed** from Fig. 1, **Reported**).[^cofilite-paper]
- Two ideal-ratio-mask (IRM) predictions `M_c` and `M_f` (sigmoid outputs) are applied in sequence to the noisy magnitude: `|S̃| = |X| ⊗ M_c ⊗ M_f` for bins ≤ `f_low`, and `|X| ⊗ M_c` above it (Eq. 1). The noisy phase is reused and an inverse STFT yields the output; no phase is estimated, which the authors accept as a performance ceiling for the complexity gain (**Reported**).[^cofilite-paper]
- Training loss is the GTCRN loss (**Reported**; its components are listed in the README, see [CoFi-Lite](cofi-lite.md)).[^cofilite-paper]

## Coarse path

- **Input** (Eq. 2): `I_c = SFE(log10(ERB(|X|)))`. The band-merging (BM) module from GTCRN keeps the 65 bins below `f_low` and compresses the 192 higher bins into 64 ERB bands (129 features in total); SFE is GTCRN's subband feature extraction with kernel 3 (**Reported**).[^cofilite-paper]
- **Encoder**: three MB blocks, each halving frequency resolution (factor 8 from the blocks, 16 overall including BM); kernels (3,5) for the first block and (1,5) for the other two. The decoder mirrors it with transposed convolutions and skip connections, then a sigmoid and band splitting (BS) reverse the BM step to give `M_c` (**Reported**).[^cofilite-paper]
- **MB block** (Fig. 1b): point-wise conv → depth-wise conv → point-wise conv, with batch norm and affine PReLU (APReLU) between, and a temporal recurrent attention (TRA) module from GTCRN. The block derives from UL-UNAS but swaps its causal time-frequency attention (cTFA) for TRA "for simplicity and computational efficiency"; no ablation of that swap is given (**Reported**).[^cofilite-paper]

## Fine path

- **Input** (Eq. 3): the low-band complex spectrum `X^l` as `[log10|X^l|, Re/|X^l|^0.7, Im/|X^l|^0.7]` through SFE; power-law compression 0.7 follows GTCRN, LiSenNet and AdaptCRN practice (**Reported**).[^cofilite-paper]
- **Encoder/decoder**: a single MB block with (3,3) kernel and (1,2) stride (frequency halved, `R_f` = 2), so the low band keeps high resolution while later modules stay cheap; the decoder mirrors it and a sigmoid produces `M_f`. The paper's rationale: deep compression and few channels weaken the coarse path's low-frequency modeling, which the fine path repairs (**Reported**).[^cofilite-paper]

## Cross-Path Fusion (Fig. 1c)

1. Reshape each path's bottleneck feature from `C × T × F'` to `T × (C·F')` and concatenate: `E_in ∈ R^{T×D}`, `D = C₁F'₁ + C₂F'₂`.
2. FC layer compresses to latent size `H`, then layer norm and ELU give `Z`.
3. An RNN over time (grouped GRU, 2 groups, `H = 76`) captures temporal patterns of the fused feature.
4. A second FC restores dimension `D`; the result is split, reshaped, and added back through skip connections to give `D_c` and `D_f` (**Reported**).[^cofilite-paper]

Because fusion happens after each path's first Inter-RNN, the only cross-path interaction is at this single bottleneck; the paper does not test fusion at other depths or compare with other fusion operators (**Observed** absence).

## Configuration

| Item | CoFi-Lite | CoFi-Lite (Large) |
| --- | --- | --- |
| `f_low` | bin 65 (2 kHz) | same |
| MB output channels | 6 in all blocks | coarse [6, 12, 14], fine 14 |
| CPF latent `H` | 76 | 102 |
| Inter-RNN / CPF RNN | GRU / grouped GRU (2 groups) | same |
| Parameters / MACs/s | 83.12k / 12.87M | 221.31k / 32.91M |

Training: Adam, linear warmup from 1e-6 to 1e-3 over 25k iterations then cosine decay to 250k iterations, 200 epochs × 1,250 iterations, batch size 8 (**Reported**).[^cofilite-paper] Dataset and baselines are in [CoFi-Lite](cofi-lite.md).

## Ablations (single table; DNS3 test set)

Table "ablation" IDs 1–12. Hidden sizes were adjusted so the complexity is comparable (**Reported**):[^cofilite-paper]

| ID | `R_c` | `R_f` | `f_low` | CPF | Params (k) | MACs/s (M) | PESQ | ESTOI ×100 | SI-SNR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 16 | – | 65 | no | 19.71 | 12.37 | 1.97 | 73.73 | 10.68 |
| 2 | – | 2 | 65 | no | 9.24 | 12.05 | 1.53 | 70.14 | 8.41 |
| 3 | 16 | 2 | 65 | no | 21.23 | 12.24 | 2.02 | 74.06 | 10.81 |
| 4 | 16 | 2 | 65 | no | 90.80 | 13.44 | 2.06 | 74.98 | 11.20 |
| 5 (final) | 16 | 2 | 65 | yes | 83.12 | 12.87 | 2.16 | 76.10 | 11.80 |
| 6 | 16 | 4 | 65 | yes | 71.18 | 11.89 | 2.12 | 75.72 | 11.55 |
| 7 | 16 | 8 | 65 | yes | 66.20 | 11.46 | 2.09 | 75.31 | 11.41 |
| 8 | 8 | 2 | 65 | yes | 95.06 | 13.84 | 2.16 | 76.10 | 11.73 |
| 9 | 32 | 2 | 65 | yes | 78.14 | 12.44 | 2.14 | 76.01 | 11.77 |
| 10 | 16 | 2 | 17 | yes | 58.79 | 11.51 | 2.08 | 75.30 | 11.39 |
| 11 | 16 | 2 | 33 | yes | 66.90 | 11.90 | 2.11 | 75.69 | 11.58 |
| 12 | 16 | 2 | 97 | yes | 99.35 | 14.09 | 2.15 | 76.25 | 11.72 |

Findings (deltas recomputed, **Observed**):

- **Two paths beat one**: ID3 (both paths, no CPF) PESQ 2.02 vs 1.97 (coarse only) and 1.53 (fine only). The fine path alone is weak, so it is a refinement, not a replacement.
- **CPF is the main gain**: ID5 vs ID3 +0.14 PESQ, +2.04 ESTOI, +0.99 SI-SNR. The control ID4 enlarges the no-CPF model to 90.80k parameters (9% more than ID5, MACs 13.44 vs 12.87), still 0.10 PESQ lower than ID5, which the authors read as complementarity rather than extra parameters. The control varies hidden size only; other capacity-equalization options are untested.
- **Fine-path compression hurts, mildly**: `R_f` 2 → 4 → 8 lowers PESQ 2.16 → 2.12 → 2.09 and saves 14–20% parameters and 8–11% MACs. The paper says performance "rapidly degrades"; the drop is 0.07 PESQ at most, so this is a trade-off curve rather than a cliff (**Observed**; wording is the authors' (**Reported**)).
- **Coarse-path resolution barely matters**: `R_c` = 8 gives equal PESQ (2.16) at +0.97M MACs/s and +12k parameters; `R_c` = 32 gives −0.02 PESQ at −0.43M MACs/s. This is where the paper's budget saving comes from, and the MAC difference between 16 and 32 is small (**Observed**).
- **Cutoff**: `f_low` 17 → 33 → 65 raises PESQ 2.08 → 2.11 → 2.16; 97 gives 2.15 PESQ with ESTOI +0.15 and SI-SNR −0.08 versus 65 at +1.22M MACs/s, supporting the 2 kHz choice (**Observed**; "salient speech structures below 2 kHz" is the authors' explanation, **Reported**).[^cofilite-paper]

## Implications and open questions

- **Design pattern for small voice front ends** (**Synthesis**): allocate fine resolution only where perceptual loss concentrates (below 2 kHz) and compress the rest; this applies to any edge enhancer, but the evidence is one dataset and one run per row.
- Not ablated: the TRA-for-cTFA swap, BM versus no BM, sequential IRM application versus a single merged mask, the GRU versus other RNNs inside CPF, or CPF positions; no streaming-state or long-sequence tests (**Observed** absence).
- Each ablation row is a single training run; seed variance is not reported, and differences of 0.01–0.04 PESQ (IDs 8, 9, 12 versus 5) are within plausible noise (**Synthesis**).

## Relationships

- Component of [CoFi-Lite](cofi-lite.md), which holds results, protocol and code release.
- Reuses GTCRN modules and the UL-UNAS MB block (see [UL-UNAS Design Components and NAS](ul-unas-design-and-nas.md) for APReLU and cTFA): CoFi-Lite keeps APReLU and swaps cTFA for TRA (**Observed** from Fig. 1b and text).
- Contrast with [FastEnhancer Design Choices and Ablations](fastenhancer-design-and-ablations.md), which optimizes wall-clock speed through time-kernel 1 and fusable BatchNorm rather than MACs; CoFi-Lite optimizes MACs and still reports RTF measured on a desktop CPU (**Synthesis**).

## Coverage and limits

- Ledger: `main.tex` Sec. II (overview, coarse, fine, CPF), Sec. III-B, III-C and Sec. IV-B (ablations) read in full; Fig. 1 (`cofilite.pdf`) rendered and viewed. The README's training table was reconciled against the LaTeX on [CoFi-Lite](cofi-lite.md). Code (`model/cofilite.py`) and the demo page's per-module MAC breakdown were not inspected, so exact tensor shapes (for example the value of `F'` in CPF) are not verified.
- Fig. 1 shows MB blocks in the coarse encoder as three stacked blocks and the fine encoder with one; no discrepancy with the text was found. No sensitive values were found.

[^cofilite-paper]: [CoFi-Lite LaTeX source](../raw/arXiv-2607.10142v1-CoFi-Lite/main.tex) (arXiv 2607.10142v1) — locators: abstract; Sec. II-A model overview (Eq. 1, `fig:cofi`a); Sec. II-B coarse path (Eq. 2, `fig:cofi`b); Sec. II-C fine path (Eq. 3); Sec. II-D cross-path fusion (`fig:cofi`c); Sec. III-B1 parameter configuration and III-B2 training configuration; Sec. IV-B ablation study (subsections 1–3) and Table `ablation` (IDs 1–12); Sec. I (motivation: naive downscaling).
