---
type: Concept
title: UL-UNAS Design Components and NAS
description: Efficient-block comparison, affine PReLU (APReLU), causal time-frequency attention (cTFA), the MACS-aware reinforcement-learning architecture search, and the reported ablations behind the UL-UNAS speech-enhancement model.
tags: [pipeline, speech-enhancement, nas, ablation, edge, paper]
status: draft
created: 2026-10-24
generated: { by: llm-wiki-agent/1, at: 2026-10-24T12:00:00Z }
stale_after: 2027-10-24
sources:
  - id: ulunas-paper
    resource: ../raw/arXiv-2503.00340v2-UL-UNAS/main.tex
    scope: ../raw/arXiv-2503.00340v2-UL-UNAS/
    kind: paper
    revision: arXiv 2503.00340v2
    title: "UL-UNAS: Ultra-Lightweight U-Nets for Real-Time Speech Enhancement via Network Architecture Search (LaTeX source)"
---

The [UL-UNAS](ul-unas.md) model is the product of three steps: pick the most cost-effective convolutional block types for an ultra-lightweight U-Net (Conv, DWS, MB win), boost them with two small additions (a frequency-dependent activation called APReLU and a causal two-branch attention called cTFA), then let a MACS-penalized reinforcement-learning search choose block types, strides, groups, channels, and kernels in about 2 GPU days. All ablations below use a small prototype on a 10% DNS3 subset (4-second crops), so absolute numbers differ from the full-data results on the model page; the paper reports PESQ gains of +0.05 (APReLU), +0.16 (cTFA), and +0.05 (NAS over the best hand-built network) (**Reported**).[^ulunas-paper]

## Base block comparison

Prototype: five identical blocks of 16 channels, kernel (3,3), frequency strides 2, 2, 1, 1, 1. Modifications: pointwise conv moved before depthwise in DWS and Rep blocks; first depthwise removed in Star; extra final batch norm in MB and Star; residual only when shapes match (**Reported**).[^ulunas-paper]

| Block ×5 | Params (k) | MACS (M/s) | SISNR | PESQ | Note |
| --- | --- | --- | --- | --- | --- |
| Conv | 52.12 | 57.96 | 11.12 | 2.05 | best quality, heaviest |
| DWS | 37.23 | 23.72 | 10.80 | 1.99 | cheapest |
| Ghost | 43.39 | 37.82 | 10.98 | 2.02 | marginal gain, high cost |
| Rep | 37.23 | 23.72 | 10.87 | 2.00 | reparameterization adds no meaningful gain; same inference cost as DWS |
| MB | 39.98 | 30.68 | 10.86 | 2.03 | clear advantage over Star with fewer MACS |
| Star | 39.97 | 31.46 | 10.73 | 1.98 | |

Blocks are grouped by convolution-layer count (Conv; DWS/Ghost/Rep; MB/Star) and the winner of each group (Conv, DWS, MB) becomes a NAS candidate, extended with APReLU and cTFA as XConv, XDWS, XMB (**Reported**).[^ulunas-paper]

## Affine PReLU (APReLU)

- **Definition**: `h(x) = γx + β + PReLU(x)`, with `γ, β ∈ R^(C×F)` (channel × frequency) and PReLU slope `α ∈ R^C`; initialized γ=1, β=0, α=0.25, so the affine part begins as an identity/residual path. The motivation is that speech and noise statistics differ by frequency band, so the activation should be frequency-dependent (**Reported**).[^ulunas-paper]
- **Ablation** (DWS prototype, PESQ): plain PReLU 1.99 → frequency-independent affine (1 or C values) 1.99–2.00, no gain → frequency-dependent affine (C×F) with channel-wise slope 2.04 (ID6) → also C×F slope 2.05 (ID7, but DNSMOS drops, judged redundant). Params rise from 37.23k to 62.79k; MACS unchanged because affine cost is disregarded as negligible (**Reported**; the "negligible" assumption is not measured).[^ulunas-paper]
- **Generality**: adding the C×F affine to GELU (1.99 → 2.03) and Swish (1.99 → 2.03) also helps; the paper concludes frequency-dependent affine recalibration is a general design principle. PReLU(C)+affine(C×F) 2.04 still beats both (**Reported**).[^ulunas-paper]

## Causal time-frequency attention (cTFA)

- **Problem**: TFA's frequency-attention branch average-pools over time, which is non-causal; GTCRN's TRA dropped that branch, losing frequency-dependent attention.[^ulunas-paper]
- **Design**: two parallel branches multiplied into a 4-D attention map `A_TF(b,c,t,f) = A_T(b,c,t)·A_F(b,t,f)` applied to the input. Time attention (TA) pools squared activations over frequency and uses GRU → FC → sigmoid (same as TRA). Frequency attention (FA) pools squared activations over channels instead of time, then applies *frequency folding* (F bins regrouped into H groups of local size R=4, zero-padded when F is not divisible), BiGRU → FC → sigmoid. The BiGRU runs over the frequency axis, not time, so the module stays causal (**Reported**; causality is an argument from the design, not tested separately).[^ulunas-paper]
- **Ablation** (DWS prototype):

| TA | FA | Params (k) | MACS (M/s) | SISNR | PESQ |
| --- | --- | --- | --- | --- | --- |
| – | – | 37.23 | 23.72 | 10.80 | 1.99 |
| ✓ | – | 85.22 | 26.87 | 11.38 | 2.09 |
| – | ✓ | 39.99 | 26.43 | 10.85 | 2.00 |
| ✓ | ✓ | 87.98 | 29.59 | 11.66 | 2.15 |

FA alone gives almost nothing, TA alone +0.10 PESQ, both +0.16, so FA is complementary rather than independent; the module adds about 5.9M MACS (**Reported**; difference recomputed, **Observed**).[^ulunas-paper]

## Neural architecture search

- **Search space**: five encoder blocks, each with five nodes: type (XConv, XDWS, XMB), frequency stride (1, 2), group number (1, 2; channel shuffle when 2), channels (12, 16, 20, 24, 28, 32, 36), kernel (1×5, 1×7, 2×5, 3×3). That is 25 nodes and about 10^12 configurations (3·2·2·7·4 = 336 per block; 336^5 ≈ 4.2×10^12, **Observed**). The decoder mirrors the encoder (**Reported**).[^ulunas-paper]
- **Algorithm**: the MnasNet RL recipe with an LSTM controller (one cell per node: embedding 100, LSTM hidden 200, softmax sampling layer), trained with PPO and Adam (lr 0.001). The reward is `R(m) = (Q(m) − Q0) · (M(m)/M_T)^ω` with Q = mean validation PESQ over the last three of 20 epochs (5,000 random pairs per epoch on the DNS3 subset), Q0 = 1, target M_T = 30M MACS, ω+ = −0.15 when MACS exceed the target and ω− = 0 otherwise. It optimizes MACS, not measured latency, because no device is targeted (**Reported**).[^ulunas-paper]
- **Compute**: 40 architectures per episode on 8 RTX 3090 GPUs (5 per GPU, batch 8); the top-1/5/25 rewards converge after more than 1,200 sampled models (Fig. reward shows the top-1 reward plateauing near 0.94 by about 1,700 samples); total about 2 GPU-days (**Reported**; plot read visually, **Observed**).[^ulunas-paper]
- **Result** (full table in [UL-UNAS](ul-unas.md) for the final model; prototype-data numbers here):

| Encoder | Params (k) | MACS (M/s) | SISNR | PESQ | OVRL |
| --- | --- | --- | --- | --- | --- |
| XConv ×5 | 114.56 | 63.11 | 11.96 | 2.22 | 2.69 |
| XDWS ×5 | 113.53 | 28.00 | 11.69 | 2.16 | 2.66 |
| XMB ×5 | 116.53 | 34.94 | 11.85 | 2.20 | 2.67 |
| NAS-discovered | 171.33 | 34.91 | 12.07 | 2.25 | 2.69 |

The NAS model beats XMB×5 by +0.05 PESQ and +0.02 OVRL at equal MACS, with a stated (unquantified) lower inference latency from fewer convolution layers. Given a strict MACS budget the search chose a larger parameter count (171k vs about 116k), which the authors read as parameters mattering for quality (**Reported**).[^ulunas-paper]
- **Cumulative boost of APReLU + cTFA**: DWS×5 PESQ 1.99 → XDWS×5 2.16, MB 2.03 → XMB 2.20, Conv 2.05 → XConv 2.22 (**Observed** comparing Table I and Table V).[^ulunas-paper]

## Training objective

Hybrid loss `λ1·L_SISNR + (1−λ2)·L_mag + λ2·(L_real + L_imag)` with λ1 = 0.01, λ2 = 0.3 (values carried over from GTCRN); magnitude loss on compressed magnitude with exponent 0.3, real/imaginary losses on phase-preserving compressed terms with exponent 0.7. DNS3 training: Adam, linear warm-up 10⁻⁶ to 10⁻³ over 25k steps, cosine decay to 250k steps, batch 32. VCTK-DEMAND: lr 10⁻³ halved after 5 epochs without validation-loss improvement, batch 4. The optional PESQ loss for the VCTK-DEMAND ‡ results uses `torch-pesq` (**Reported**).[^ulunas-paper]

## Contradictions and inconsistencies

- The search-space kernel options are 1×5, 1×7, 2×5, 3×3, yet the discovered configuration lists kernels (2,3) in two blocks, which is not among them. The mismatch is not explained in the source (**Observed**).[^ulunas-paper]
- The paper calls XMB×5 "the overall best manually designed prototype", but XConv×5 scores higher PESQ (2.22 vs 2.20) at 63.11M MACS; the claim is therefore best under the MACS constraint, not in raw quality (**Synthesis**).[^ulunas-paper]
- The final model's 35M MACS exceeds the 30M search target; with ω+ = −0.15 this costs reward, and the paper does not say how the final model was selected from the search or whether it was retrained under a different budget (**Synthesis**).[^ulunas-paper]

## Relationships

- Component of [UL-UNAS](ul-unas.md), which holds the final results and pipeline implications.
- The cTFA and APReLU ideas are generic modules; no evidence here that they transfer to ASR, VAD, or TTS networks (**Synthesis**).

## Coverage and limits

- Ledger: `main.tex` Sections II (related work), III-C to III-E, IV, V and Tables I–V read in full; figure captions for `fig_base_blocks`, `fig_xblocks`, `fig_aprelu_1–4`, `fig_nas`, and `fig_controller` were read but the images were not viewed. Cited works (MnasNet, GhostNet, MobileOne, StarNet, TFA, GTCRN, PPO) are uninspected.
- The ablations use a subset and prototype; seed variance is asserted but not tabulated. No code or search logs were inspected, so the search is not reproduced.

[^ulunas-paper]: [UL-UNAS LaTeX source](../raw/arXiv-2503.00340v2-UL-UNAS/main.tex) (arXiv 2503.00340v2) — locators: Sec. II-B (efficient blocks), Sec. III-C1 (base blocks, Fig. base_blocks, Fig. xblocks), III-C2 (APReLU, Eq. 3–4, Fig. aprelu), III-C3 (cTFA, Eq. 5–10, Fig. ctfa), III-D (NAS, Eq. 11, Fig. nas, Fig. controller), III-E (loss); Sec. IV-B (training and NAS configurations); Tables I–V; Sec. V-A (ablation analysis, Fig. reward).
