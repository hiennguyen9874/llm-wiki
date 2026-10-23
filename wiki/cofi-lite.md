---
type: Concept
title: CoFi-Lite
description: Nanjing University's ultra-lightweight causal speech-enhancement model (12.87M MACs/s, 83.12k parameters at 16 kHz) with parallel coarse and fine paths, reported DNS3 and DNS-2020 results versus GTCRN, LiSenNet, UL-UNAS and AdaptCRN, released code and checkpoint, and no ASR, VAD, latency-on-device or license evidence.
tags: [pipeline, speech-enhancement, denoising, edge, causal, paper]
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
  - id: cofilite-readme
    resource: ../raw/arXiv-2607.10142v1-CoFi-Lite/README-github.md
    kind: documentation
    title: CoFi-Lite GitHub README (undated capture, newest news item 2026-10-19)
---

CoFi-Lite (Yang, Wang, Rong, Zhao, Lu; Nanjing University / Horizon Robotics; IEEE Signal Processing Letters) is a causal time-frequency-domain speech-enhancement (SE, noise-suppression) model for 16 kHz audio that targets the bottom of the "ultra-lightweight" range: **12.87M MACs/s and 83.12k parameters**, about 40% of GTCRN's 31.97M MACs/s. Two parallel encoder–decoder paths, one for a compressed full-band magnitude envelope and one for low-frequency (below 2 kHz) detail with phase information, each predict a magnitude mask, joined by a Cross-Path Fusion (CPF) module at the bottleneck. On the authors' simulated DNS3 test set it reaches PESQ 2.16 and DNSMOS OVRL 2.70 against GTCRN's 2.07 and 2.63, and a scaled-up CoFi-Lite (Large, 32.91M MACs/s) ties AdaptCRN on PESQ and OVRL with 19.34% fewer MACs (**Reported**, ratios recomputed **Observed**).[^cofilite-paper] For a voice pipeline it is a candidate sub-15M-MAC noise-suppression front end; the paper measures speech-quality metrics only, with no ASR word-error rate, no on-device latency and no Vietnamese evaluation. Architecture and ablations are in [CoFi-Lite Design and Ablations](cofi-lite-design-and-ablations.md).

## Reported results

Baselines are GTCRN, LiSenNet, UL-UNAS and AdaptCRN plus scaled-down "Small" variants made by proportionally cutting channels; "Level I" is below 20M MACs/s and "Level II" above 30M. Training uses DNS3 plus the DiDiSpeech Mandarin corpus, 72,000 ten-second pairs (200 h), SNR −5 to 15 dB with random RIRs, target = speech with the first 100 ms of reverberation; 1,000 pairs each for validation and test (**Reported**).[^cofilite-paper] Metrics: PESQ (wide-band), ESTOI, SI-SNR, DNSMOS P.808 and P.835 (OVRL/SIG/BAK).

Simulated DNS3 test set (Table I; bold = best in the level in the source):[^cofilite-paper]

| Model | Params (k) | MACs/s (M) | RTF | PESQ | ESTOI ×100 | SI-SNR | P.808 | OVRL / SIG / BAK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Noisy | – | – | – | 1.40 | 66.90 | 5.61 | 2.82 | 1.63 / 2.05 / 1.86 |
| *Level I* | | | | | | | | |
| GTCRN (Small) | 7.91 | 13.63 | 0.040 | 1.88 | 72.18 | 10.07 | 3.38 | 2.53 / 2.88 / 3.76 |
| LiSenNet (Small) | 12.46 | 15.57 | 0.031 | 1.94 | 72.74 | 10.49 | 3.36 | 2.58 / 2.93 / 3.80 |
| UL-UNAS (Small) | 56.43 | 13.63 | 0.054 | 2.05 | 74.87 | 11.16 | 3.47 | 2.60 / 2.94 / 3.81 |
| AdaptCRN (Small) | 34.98 | 12.97 | 0.047 | 2.06 | 75.15 | 11.19 | 3.50 | 2.65 / 2.99 / 3.85 |
| **CoFi-Lite** | 83.12 | 12.87 | 0.033 | 2.16 | 76.10 | 11.80 | 3.53 | 2.70 / 3.05 / 3.85 |
| *Level II* | | | | | | | | |
| GTCRN | 23.67 | 31.97 | 0.050 | 2.07 | 75.11 | 11.30 | 3.48 | 2.63 / 2.98 / 3.81 |
| LiSenNet | 36.78 | 55.77 | 0.035 | 2.17 | 76.19 | 11.74 | 3.53 | 2.69 / 3.03 / 3.85 |
| UL-UNAS | 171.33 | 34.91 | 0.066 | 2.25 | 77.69 | 12.07 | 3.55 | 2.69 / 3.01 / 3.86 |
| AdaptCRN | 134.51 | 40.80 | 0.053 | 2.30 | 78.15 | 12.35 | 3.59 | 2.75 / 3.08 / 3.88 |
| **CoFi-Lite (Large)** | 221.31 | 32.91 | 0.036 | 2.30 | 77.94 | 12.43 | 3.56 | 2.75 / 3.09 / 3.88 |

Recomputed from the table (**Observed**):

- CoFi-Lite versus GTCRN (Level II): MACs 12.87/31.97 = 40.26% (matches the claim); RTF 0.033 vs 0.050 is 34% lower; PESQ +0.09, OVRL +0.07, SIG +0.07, SI-SNR +0.50, but parameters are 3.5× higher (83.12k vs 23.67k).
- CoFi-Lite versus Level I baselines at about the same MACs: PESQ +0.10 over AdaptCRN (Small) and +0.28 over GTCRN (Small); parameters are 2.4× AdaptCRN (Small) and 10.5× GTCRN (Small). LiSenNet (Small) has the lowest RTF at Level I (0.031 vs 0.033), and GTCRN (Small) the fewest parameters.
- CoFi-Lite (Large) versus AdaptCRN: MACs −19.34% (32.91 vs 40.80), RTF 0.036 vs 0.053 (−32%), parameters +64.5% (221.31k vs 134.51k); PESQ and OVRL are equal, ESTOI is 0.21 lower, P.808 0.03 lower, SI-SNR 0.08 higher. "On par" is accurate; it does not beat AdaptCRN on quality.
- At Level II, UL-UNAS has a higher RTF (0.066) than every other model despite similar MACs to GTCRN, supporting [FastEnhancer](fastenhancer.md)'s argument that MACs poorly predict wall-clock speed; the paper itself only notes CoFi-Lite "records one of the lowest RTFs" (**Synthesis**).[^cofilite-paper]

DNS Challenge 2020 test set (Table II; DNSMOS P.835 only because the anechoic references mismatch the early-reverberation training target; all models retrained) (**Reported**):[^cofilite-paper]

| Model | No reverb OVRL / SIG / BAK | With reverb OVRL / SIG / BAK |
| --- | --- | --- |
| Noisy | 2.48 / 3.39 / 2.62 | 1.39 / 1.76 / 1.50 |
| GTCRN (Small) | 2.99 / 3.31 / 3.91 | 2.33 / 2.72 / 3.55 |
| AdaptCRN (Small) | 3.11 / 3.39 / 4.02 | 2.46 / 2.85 / **3.63** |
| **CoFi-Lite** | **3.15 / 3.43 / 4.03** | **2.48 / 2.89** / 3.57 |
| GTCRN | 3.09 / 3.38 / 4.01 | 2.43 / 2.86 / 3.52 |
| AdaptCRN | **3.20 / 3.45 / 4.10** | **2.51 / 2.92 / 3.57** |
| CoFi-Lite (Large) | 3.19 / 3.44 / 4.09 | 2.50 / **2.92 / 3.57** |

LiSenNet, UL-UNAS and the other Small variants are in the source table and omitted here; the trend matches DNS3, and CoFi-Lite is below AdaptCRN (Small) on reverberant BAK (3.57 vs 3.63).

## Evaluation protocol and measurement limits

- **Complexity**: parameters and MACs/s from `ptflops`; a per-module breakdown is said to be on the demo page (not inspected) (**Reported**).[^cofilite-paper]
- **RTF**: ONNX Runtime, streaming inference, Intel Core i5-14600KF desktop CPU, STFT and iSTFT excluded, no future frames. The authors state this gives zero algorithmic delay; the 32 ms STFT window and 16 ms hop still bound the end-to-end audio latency of a real deployment (**Synthesis** from the stated STFT settings). Thread count and ONNX settings are not stated (**Reported**, limit).[^cofilite-paper]
- **Device gap**: the conclusion concedes desktop-CPU RTF may not reflect ARM Cortex-M or DSP deployment, and that closing the gap is future work (**Reported**).[^cofilite-paper]
- **Baseline provenance**: the Table I caption says "Only UL-UNAS uses the statistics reported in its original paper", while the Level II UL-UNAS row (PESQ 2.25, SI-SNR 12.07, 171.33k parameters, 34.91M MACs/s) differs from the figures the UL-UNAS paper itself reports (PESQ 2.30, SISNR 12.30, 35M MACs; see [UL-UNAS](ul-unas.md)). Whether it was retrained or the caption is imprecise is unresolved (**Observed** mismatch; cause **Unverified**). GTCRN is also listed with 23.67k parameters here versus 48k in the UL-UNAS paper's table.
- Retrained baselines use the authors' own training configuration except AdaptCRN and its variant, which follow the original work's settings; Small variants are proportional channel cuts, not published designs (**Reported**).[^cofilite-paper]
- No seed variance, confidence intervals or significance tests are given; differences such as PESQ 2.16 vs 2.06 are single-run (**Observed** absence).

## Code, checkpoint and recipe (README)

- The README says the source code and a checkpoint trained on the simulated DNS3 dataset were released (news item dated 2026-10-19); the manuscript was accepted by IEEE SPL on 2026-7-7 and posted to arXiv on 2026-7-14. Citation: IEEE SPL vol. 33, pp. 2954–2958, 2026 (**Reported**).[^cofilite-readme]
- Layout: `checkpoint/model_on_dns3.tar`, `configs/cfg_train.yaml`, `configs/cfg_infer.yaml`, `model/cofilite.py`, `train.py` (single-GPU or DDP), `infer.py`, `evaluate.py`, a hybrid `loss_factory.py` (30 × compressed RI loss + 70 × compressed magnitude MSE + negative SI-SNR, compress factor 0.3 — the GTCRN loss the paper reuses), and bundled DNSMOS ONNX models (**Reported**).[^cofilite-readme]
- Run: `python infer.py -C configs/cfg_infer.yaml -D 0` (GPU index; CPU fallback), then `python evaluate.py --metric dnsmos|intrusive --config configs/cfg_infer.yaml --device 0`. DNSMOS scoring needs `espnet`, `onnxruntime` and `onnx2torch`. Inference reads 16 kHz noisy WAVs and writes `<uid>_enh.wav`; the clean folder is needed only for intrusive metrics (**Reported**).[^cofilite-readme]
- Train recipe: Adam, lr 1e-3, warmup 25k steps then cosine to 250k steps (min 1e-6), batch 8, 200 epochs with 10k samples drawn per epoch from 72k ten-second clips, gradient clipping 3.0; the clean file is located by replacing `noisy` with `clean` in the path. This agrees with the paper's 1,250 iterations × 8 = 10,000 samples per epoch and 200 × 1,250 = 250,000 iterations (**Reported**, consistency **Observed**).[^cofilite-readme][^cofilite-paper]
- The README results tables repeat the paper's GTCRN versus CoFi-Lite numbers (DNS3 and DNS-2020) without discrepancy (**Observed**).[^cofilite-readme]
- No license, streaming/ONNX export or ONNX RTF script is described in the capture; the README mentions only PyTorch inference (**Observed** absence).

## Voice-pipeline implications

- **Fit**: at 12.87M MACs/s and 83k parameters the model is in the budget class of a CPU-side or small-NPU noise-suppression stage ahead of VAD or STT; this is **Synthesis** from the MACs figure, since only a desktop-CPU RTF is reported (0.033, about 30× faster than real time on one unstated configuration).[^cofilite-paper]
- **Unproven for ASR**: PESQ/DNSMOS gains do not establish lower WER; [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) records studies where enhancement hurt ASR, so any use before STT needs a WER A/B test in the target language (**Synthesis**).
- **Language, data and condition**: trained on DNS3 plus Mandarin DiDiSpeech at 16 kHz with early-reverberation targets; DNS-2020 is the only external set; no Vietnamese, far-field, multi-talker, music or echo evaluation (**Observed** absence).[^cofilite-paper]
- **Phase handling**: the enhanced signal reuses the noisy phase; the authors accept a ceiling on quality for the complexity saving, which may matter for downstream perceptual quality but is not tested on ASR (**Reported**, implication **Synthesis**).[^cofilite-paper]
- **Streaming reality**: causal, frame-by-frame by design, but no streaming demo, state-handling description or long-session test is included; for recurrent models see the drift failure mode in [Comfi-FastGRNN and RNN State Drift](comfi-fastgrnn-state-drift.md) (**Synthesis**; CoFi-Lite uses GRUs, which that paper did not find drifting on its 90 s test).

## Relationships

- Design and ablations: [CoFi-Lite Design and Ablations](cofi-lite-design-and-ablations.md).
- Builds on GTCRN (band merging, SFE, TRA, loss) and on the UL-UNAS block (replacing cTFA with TRA); compare [UL-UNAS](ul-unas.md), whose MB-block lineage and 35M MACs/s budget it undercuts by about 2.7× (**Reported**; same authoring group).[^cofilite-paper]
- Compare [FastEnhancer](fastenhancer.md) (speed-optimized, 22k–1.1M parameters, Xeon/M1 RTFs) and [Fast-ULCNet](fast-ulcnet.md) (Cortex-A53 RTFs): all report speech-quality metrics on different data and protocols, so their numbers are not comparable with Table I here (**Synthesis**).
- Contrast with [DPDFNet](dpdfnet.md), a 2.3–3.6M-parameter DeepFilterNet2-derived family, roughly 28–43× more parameters than CoFi-Lite's 83k (**Synthesis**, parameter ratio only).
- Supports the noise-preprocessing question in [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) as a low-compute candidate, without ASR evidence (**Synthesis**).

## Coverage and limits

- Ledger: entry point `main.tex` (all 373 lines, including Tables I, II and the ablation table, footnotes and conclusion), `00README.json` (pdflatex toplevel declaration), `README-github.md` (read in full), and `cofilite.pdf` (the paper's Fig. 1; rendered and viewed, text matches the LaTeX description). Excluded: `IEEEtran.cls` (document class, boilerplate), `ref.bib` (bibliography; cited papers uninspected). The paper was not compiled and nothing was executed.
- The GitHub repository code, checkpoint, demo page, cited papers (GTCRN, UL-UNAS, AdaptCRN, LiSenNet) and any license file were not inspected; availability, license and a runnable streaming port are **Unverified**.
- The README capture is undated; its release news (2026-10-19) postdates the arXiv posting (2026-7-14), so it may describe a later code state than the arXiv v1 text.
- All figures are self-reported on authors' retrained baselines; none was reproduced. No sensitive values were found (author e-mail addresses in the source are not recorded here).

[^cofilite-paper]: [CoFi-Lite LaTeX source](../raw/arXiv-2607.10142v1-CoFi-Lite/main.tex) (arXiv 2607.10142v1) — locators: abstract and Sec. I (12.87M MACs/s, 83.12k parameters, 40.26% of GTCRN, 19.34% reduction versus AdaptCRN); Sec. III-A (dataset); Table I `tab:dns3` (DNS3 comparison, caption on UL-UNAS statistics); Table II `tab:dns1` (DNS-2020); Sec. III-B (parameter and training configuration); Sec. III-C (baselines, RTF protocol, metrics); Sec. IV-A (comparison analysis, `ptflops` footnote); Sec. V (conclusion, device-gap limit).

[^cofilite-readme]: [CoFi-Lite GitHub README](../raw/arXiv-2607.10142v1-CoFi-Lite/README-github.md) (undated capture) — locators: `News`; `Introduction`; `Results` (two tables); `Repository Structure`; `Inference` steps 1–4; `Evaluation`; `Training` steps 1–4 (config table); `Citation`.
