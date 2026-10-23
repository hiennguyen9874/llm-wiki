---
type: Concept
title: DPDFNet
description: Ceva's causal single-channel speech-enhancement family extending DeepFilterNet2 with dual-path RNN blocks (2.3–3.6M parameters, 8/16/48 kHz releases, Apache-2.0 code) with reported VoiceBank+DEMAND, DNS4 and 12-language low-SNR results, Ceva NeuPro-Nano NPU real-time factors and a streaming Python API, but no ASR-in-the-loop or CPU/GPU latency evidence.
tags: [pipeline, speech-enhancement, denoising, streaming, edge, npu, paper]
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

DPDFNet (Rika, Sapir, Gus; Ceva Technologies; manuscript formatted for *Speech Communication*) is a causal single-channel speech-enhancement (SE, noise-suppression) model that keeps the DeepFilterNet2 two-stage framework (ERB gains, then complex deep filtering) and inserts N causal dual-path RNN (DPRNN) blocks into both encoder branches; N = 2, 4 or 8 gives DPDFNet-2/-4/-8 (2.49/2.84/3.54M parameters, 1.35/2.36/4.37 GMACs) against a retrained DeepFilterNet2 "Baseline" at 2.31M parameters and 0.36 GMACs. Mechanism, loss, fine-tuning and metric details are in [DPDFNet Design, Training and Evaluation](dpdfnet-design-and-training.md). The paper reports that all DPDFNet sizes beat DeepFilterNet2/3 and other causal open-source models on an aggregate score (PRISM) over VoiceBank+DEMAND, the DNS4 blind test and a new 12-language low-SNR set, and that DPDFNet-4 runs in real time (RTF 0.968) on a Ceva NeuPro-Nano NPU core. For a voice pipeline it is a candidate noise-suppression front end for on-device or CPU use; the sources give no ASR-in-the-loop result, no CPU/GPU latency, and no per-language numbers (**Reported**).[^dpdfnet-paper][^dpdfnet-readme]

## Model zoo (README)

All weights are fp32-sized (ONNX size ≈ 4 bytes per parameter: 2.49M parameters ↔ 9.7 MB), so the public ONNX/TFLite files are not the int8/int16 quantized models behind the NPU numbers (**Observed** from the README table; inference **Synthesis**).[^dpdfnet-readme]

| Rate | Model | Params (M) | MACs (G) | TFLite (MB) | ONNX (MB) |
| --- | --- | --- | --- | --- | --- |
| 8 kHz | `dpdfnet2_8khz` | 2.51 | 1.29 | 10.5 | 9.7 |
| 8 kHz | `dpdfnet8_8khz` | 3.56 | 3.99 | 16.5 | 13.8 |
| 16 kHz | `baseline` | 2.31 | 0.36 | 8.5 | 8.3 |
| 16 kHz | `dpdfnet2` | 2.49 | 1.35 | 10.7 | 9.7 |
| 16 kHz | `dpdfnet4` | 2.84 | 2.36 | 12.9 | 11.1 |
| 16 kHz | `dpdfnet8` | 3.54 | 4.37 | 17.2 | 13.9 |
| 48 kHz | `dpdfnet2_48khz_hr` | 2.58 | 2.42 | 11.6 | 10.0 |
| 48 kHz | `dpdfnet8_48khz_hr` | 3.63 | 7.17 | 18.7 | 14.2 |

- The 16 kHz rows match the paper's parameter and MACs columns exactly (**Observed**). The paper describes only 16 kHz processing (inputs resampled to 16 kHz) and says full-band operation is a "lightweight postprocessing step"; the 8 kHz and 48 kHz "HR" models, and what "HR" means, appear only in the README and have no quality results in the paper (**Observed** absence).[^dpdfnet-paper][^dpdfnet-readme]
- The MACs denominator (per second of audio or per frame) is not stated in either source.

## Reported results

All numbers are the authors' own; open-source baselines (DTLN, GTCRN, RNNoise, NSNet2, FullSubNet, DPCRN, aTENNuate, DEMUCS, CleanUNet, DeepFilterNet2/3) were run as official checkpoints, while "Baseline" and DPDFNet were trained with the authors' framework on different data (**Reported**).[^dpdfnet-paper]

### Multilingual low-SNR set (324 clips, 13.5 h; 12 languages including Vietnamese)

| Model | Params (M) | MACs (G) | PESQ | STOI % | SI-SNR | DNSMOS OVL | P.808 | NISQA MOS | PRISM |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Noisy | – | – | 1.32 | 83.2 | 0.38 | 1.56 | 2.53 | 2.00 | 0.04 |
| GTCRN | 0.023 | 0.039 | 2.21 | 87.2 | 9.11 | 2.25 | 3.00 | 2.53 | 0.49 |
| RNNoise | 0.087 | 0.04 | 2.36 | 88.5 | 8.97 | 2.51 | 3.01 | 1.88 | 0.52 |
| DPCRN | 0.53 | 1.10 | 2.76 | 90.7 | 11.93 | 2.40 | 3.03 | 2.92 | 0.69 |
| DeepFilterNet2 | 2.31 | 0.36 | 2.59 | 91.2 | 11.95 | 2.58 | 3.19 | 3.24 | 0.75 |
| DeepFilterNet3 | 2.14 | 0.35 | 2.76 | 90.5 | 12.10 | 2.72 | 3.22 | 3.84 | 0.82 |
| DEMUCS | 33.53 | 7.70 | 2.57 | 91.5 | 12.36 | 2.69 | 3.09 | 2.52 | 0.72 |
| CleanUNet | 46.07 | 15.44 | 2.82 | 93.0 | 12.50 | 2.77 | 3.15 | 2.83 | 0.79 |
| Baseline (no OA, no fine-tune) | 2.31 | 0.36 | 2.85 | 89.2 | 10.25 | 2.65 | 3.17 | 3.95 | 0.79 |
| Baseline + OA + fine-tune | 2.31 | 0.36 | 3.04 | 91.6 | 13.27 | 2.83 | 3.21 | 3.96 | 0.91 |
| DPDFNet-2 | 2.49 | 1.35 | 3.14 | 92.6 | 13.72 | 2.85 | 3.26 | 4.06 | 0.95 |
| DPDFNet-4 | 2.84 | 2.36 | 3.18 | 93.0 | 14.11 | 2.87 | 3.28 | 4.15 | 0.98 |
| DPDFNet-8 | 3.54 | 4.37 | 3.20 | 93.4 | 14.47 | 2.89 | 3.28 | 4.21 | 1.00 |

(Subset of Table 1; DTLN, NSNet2, FullSubNet, aTENNuate and the other DNSMOS/NISQA columns are in the paper. PRISM is a min-max composite normalized over the models in each table, see caveats below.)[^dpdfnet-paper]

- Set construction: nine noise scenes (airport, car, office, pub, rain, restaurant, street, subway, train) × SNR 0/5/10 dB × 12 Speech-MASSIVE languages (Arabic, Dutch, French, German, Hungarian, Korean, Polish, Portuguese, Russian, Spanish, Turkish, Vietnamese), one ~2.5 min clip per combination with speech-free gaps up to 15 s; 9 × 3 × 12 = 324 clips and 324 × 2.5 min = 13.5 h, so the stated totals are consistent (**Observed**, recomputed). Vietnamese is one of twelve languages, with no per-language result reported (**Observed** absence).[^dpdfnet-paper]
- DPDFNet-2 versus the DeepFilterNet2 official checkpoint: PESQ +0.55, SI-SNR +1.77 dB, NISQA MOS +0.82 with 1.1× the parameters and 3.75× the MACs (1.35 vs 0.36 G). DPDFNet-8 versus fine-tuned Baseline: PESQ +0.16, SI-SNR +1.20 dB for 12.1× the MACs (**Observed**, recomputed). How much of the improvement comes from architecture versus the training recipe is analysed in [DPDFNet Design, Training and Evaluation](dpdfnet-design-and-training.md).[^dpdfnet-paper]
- Large waveform-domain models are beaten on this set at far lower cost: DPDFNet-4 (2.84M, 2.36 G) exceeds CleanUNet (46.07M, 15.44 G) on PESQ (3.18 vs 2.82), SI-SNR (14.11 vs 12.50) and NISQA MOS (4.15 vs 2.83), and ties it on STOI (93.0 both) (**Observed**).[^dpdfnet-paper]

### Standard benchmarks (paper Tables 2 and 3)

| Set | Model | PESQ | STOI % | SI-SNR | NISQA MOS | PRISM |
| --- | --- | --- | --- | --- | --- | --- |
| VoiceBank+DEMAND | Noisy | 2.11 | 97.2 | 19.89 | 3.05 | 0.23 |
| VoiceBank+DEMAND | GTCRN | 2.60 | 97.5 | 21.41 | 4.14 | 0.59 |
| VoiceBank+DEMAND | aTENNuate | 3.06 | 97.9 | 18.33 | 4.00 | 0.69 |
| VoiceBank+DEMAND | DeepFilterNet2 | 2.75 | 98.2 | 21.67 | 4.68 | 0.85 |
| VoiceBank+DEMAND | DeepFilterNet3 | 2.80 | 98.2 | 21.22 | 4.60 | 0.84 |
| VoiceBank+DEMAND | Baseline | 2.62 | 98.4 | 22.91 | 4.67 | 0.84 |
| VoiceBank+DEMAND | DPDFNet-2 | 2.68 | 98.6 | 23.56 | 4.73 | 0.90 |
| VoiceBank+DEMAND | DPDFNet-4 | 2.66 | 98.8 | 23.87 | 4.78 | 0.91 |
| VoiceBank+DEMAND | DPDFNet-8 | 2.71 | 98.8 | 24.07 | 4.78 | 0.93 |
| DNS4 blind | Noisy | – | – | – | 2.09 | 0.12 |
| DNS4 blind | DeepFilterNet2 | – | – | – | 3.61 | 0.93 |
| DNS4 blind | DeepFilterNet3 | – | – | – | 3.60 | 0.90 |
| DNS4 blind | Baseline | – | – | – | 3.50 | 0.94 |
| DNS4 blind | DPDFNet-8 | – | – | – | 3.53 | 0.98 |

(DNS4 has no clean reference, so only non-intrusive metrics and PRISM are reported; Table 3 also lists DNSMOS SIG/BAK/OVL/P.808.)[^dpdfnet-paper]

Checks against the tables (**Observed**, recomputed):

- The paper says DPDFNet variants "consistently improve over the Baseline and DeepFilterNet2/3" on VoiceBank+DEMAND. That does not hold for PESQ: DPDFNet-2/-4/-8 score 2.68/2.66/2.71 against DeepFilterNet2's 2.75 and DeepFilterNet3's 2.80, and aTENNuate leads at 3.06. DPDFNet-4 is also below DPDFNet-2 on PESQ. SI-SNR, STOI and NISQA do improve.[^dpdfnet-paper]
- On DNS4, DeepFilterNet2 is still ahead of DPDFNet-8 on NISQA MOS (3.61 vs 3.53), DIS (3.99 vs 3.88) and COL (3.54 vs 3.48); the aggregate PRISM lead (0.93 vs 0.98) rests on DNSMOS gains of 0.07–0.10 (SIG 3.40 vs 3.32, BAK 4.06 vs 3.99, OVL 3.12 vs 3.02, P.808 3.80 vs 3.73) and small NISQA NOI/LOUD leads (4.07 vs 4.02, 3.79 vs 3.75). The paper concedes that "some competing methods remain slightly stronger on individual submetrics" (**Observed**).[^dpdfnet-paper]
- The VoiceBank+DEMAND intrusive metrics were computed after a 70 Hz high-pass on the signals because the authors found low-frequency contamination in the clean references. GTCRN therefore scores PESQ 2.60 / SI-SNR 21.41 here against 2.87 / 18.8 in [FastEnhancer](fastenhancer.md) and [UL-UNAS](ul-unas.md); numbers from the three papers must not be compared directly (**Observed** difference; protocol explanation **Synthesis**).[^dpdfnet-paper]
- Gaps are small in absolute terms on the standard sets (e.g., DPDFNet-8 vs DeepFilterNet2 on VoiceBank+DEMAND: STOI +0.6 points, DNSMOS OVL +0.03), and no variance across training seeds is reported.[^dpdfnet-paper]

## Edge deployment: Ceva NeuPro-Nano

Figure `real_time_npn_500mhz.png` shows real-time factors (RTF, below 1.0 means faster than real time) for the int8-weight / int16-activation deployment configuration. The paper's text states only that DPDFNet-4 reaches real time on NPN32 at 0.97 and that NPN64 lowers every RTF (**Reported**; values read from the figure).[^dpdfnet-paper]

| Model | MACs (G) | RTF NPN32 | RTF NPN64 |
| --- | --- | --- | --- |
| Baseline | 0.36 | 0.124 | 0.100 |
| DPDFNet-2 | 1.35 | 0.546 | 0.442 |
| DPDFNet-4 | 2.36 | 0.968 | 0.784 |
| DPDFNet-8 | 4.37 | 1.814 | 1.470 |

- DPDFNet-8 is not real time on either core (1.814 and 1.470); DPDFNet-4 on NPN32 leaves about 3% headroom, which is thin for a shared device (**Observed**; headroom reading **Synthesis**).
- NPN64/NPN32 is 0.81 for every model, and RTF grows faster than MACs: 4.4× (0.546/0.124) for 3.75× the MACs at DPDFNet-2, 7.8× for 6.6× at DPDFNet-4, 14.6× for 12.1× at DPDFNet-8 (**Observed**, recomputed). Baseline-to-DPDFNet cost is therefore higher on this NPU than MACs alone suggest, plausibly because the RNN blocks are less efficient than convolutions there (**Synthesis**).
- The figure filename suggests a 500 MHz clock, but neither the paper text nor the caption states it, and the RTF definition and measurement protocol are not given. Quantization is quantization-aware training; the NPU models and toolchain are "not included in the public research artifacts" and no quantized-accuracy result exists (**Reported**).[^dpdfnet-paper]
- No CPU, GPU, mobile or ONNX-Runtime RTF appears in either source; the README only advises trying smaller models and benchmarking ONNX Runtime "to compare RTF" if CPU is too slow.[^dpdfnet-readme]

## Usage (README)

- Install `pip install dpdfnet` for CPU-only ONNX inference. CLI: `dpdfnet enhance in.wav out.wav --model dpdfnet4 --attn-limit-db 12`, `enhance-dir` (all cores by default, `--workers N`), `download [model] [--force]`. Python: `dpdfnet.enhance(audio, sample_rate=sr, model=..., attn_limit_db=12)`, `enhance_file`, `available_models`, `download`. The meaning and default of `--attn-limit-db` are not defined in the README (**Reported**).[^dpdfnet-readme]
- Streaming: `dpdfnet.StreamEnhancer(model=...)` keeps RNN state across calls, accepts any chunk size, resamples internally from the device rate and returns audio at the same rate; `flush()` drains the tail and `reset()` clears state between independent segments; one `StreamEnhancer` per stream. The README's example uses `dpdfnet2_48khz_hr` at 48 kHz with 480-sample (10 ms) blocks; `sounddevice` is not a declared dependency (**Reported**).[^dpdfnet-readme]
- README latency note: first enhanced output after one full ~20 ms model window, then about 10 ms additional delay per block. The paper's equations apply deep filtering with look-ahead ℓ = 2 frames (20 ms at the 10 ms hop), which this note does not mention, so total algorithmic latency is unresolved and not measured in either source (**Reported** note; discrepancy **Synthesis**).[^dpdfnet-paper][^dpdfnet-readme]
- From source: model files are not bundled; PyTorch checkpoints, ONNX and TFLite models come from the Hugging Face repo `Ceva-IP/DPDFNet` via `hf download`. Offline inference modules `tflite_model.infer_dpdfnet_tflite` and `onnx_model.infer_dpdfnet_onnx` scan one folder non-recursively for `.wav` files and write `<stem>_<model>.wav`; separate ONNX exporters exist for 8 kHz, 16 kHz and 48 kHz HR with `--dprnn-num-blocks` set to match the checkpoint. A PyQt real-time demo (`python -m real_time_demo`) shows live spectrograms, a 0–1 noise-reduction control and optional AGC; it is not usable on headless servers (**Reported**).[^dpdfnet-readme]

## Voice-pipeline implications

- **Fit**: a 16 kHz, 10 ms-hop causal enhancer that ships as ONNX with a stateful streaming wrapper makes it directly pluggable ahead of VAD or as a barge-in-branch denoiser; the NPU results target earbud/watch-class hardware. No CPU RTF means CPU-only suitability must be measured; compared to [FastEnhancer](fastenhancer.md)'s 22k–1.1M parameters, DPDFNet's 2.3–3.6M is heavier, though no controlled comparison exists (**Synthesis**).
- **ASR risk**: only perceptual and intrusive metrics are reported; there is no WER with or without enhancement. [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) records studies where enhancement before ASR raised error rates, so an A/B WER/CER test in the target language is needed before placing DPDFNet on the ASR branch (**Synthesis**).
- **Language coverage**: the evaluation includes Vietnamese among twelve languages but only as an average, and training clean speech is DNS4 (six languages) plus 4,000 h of English Multilingual LibriSpeech, so Vietnamese robustness is untested (**Observed** absence; training mix per [DPDFNet Design, Training and Evaluation](dpdfnet-design-and-training.md)).
- **Always-on behaviour**: the paper's own finding that the base models truncated speech after 3–4 s of silence until a long-sequence fine-tune was added is directly relevant to endpointing-heavy voice agents; the fine-tuned public checkpoints are assumed but not verified to include it (**Unverified**).[^dpdfnet-paper]

## Relationships

- Extends DeepFilterNet2; DeepFilterNet3 is treated as a related later variant and used as a baseline, not as the base (**Reported**).[^dpdfnet-paper]
- Alternative to [FastEnhancer](fastenhancer.md), [UL-UNAS](ul-unas.md), [Facebook Denoiser](facebook-denoiser.md), [ClearVoice](clearvoice.md) and [Resemble Enhance](resemble-enhance.md). DPDFNet and FastEnhancer both evaluate VoiceBank+DEMAND but with different checkpoints of GTCRN, a 70 Hz high-pass here, and different metrics, so their tables are not comparable; only DPDFNet reports edge-NPU RTF and only FastEnhancer reports CPU RTF (**Synthesis**).
- Supplies a noisy-input, multilingual and always-on stress set and a composite metric for the noise-preprocessing question in [Speech Enhancement Before ASR](speech-enhancement-before-asr.md), without ASR evidence (**Synthesis**).
- Design, loss, fine-tuning, metric and ablation detail: [DPDFNet Design, Training and Evaluation](dpdfnet-design-and-training.md).

## Coverage and limits

- Ledger: entry point `main_elsevier.tex` read in full (abstract through conclusions, Tables 1–3 and the branch-ablation table, all equations); `00README.json` read (pdflatex toplevel); `README-github.md` read in full; all six figures in `figures/` (`DPDFNet_deepfilternet.png`, `DPDFNet_dprnn.png`, `fine_tuning_case_spectrogram.png`, `oa_sensitivity_analysis.png`, `performance_complexity_footprint.png`, `real_time_npn_500mhz.png`) were rendered and viewed; values read from plots are approximate except bar labels. Excluded: `articles.bib` (cited-only bibliography, not followed). The paper was not compiled.
- Unavailable: the README references `figures/dpdfnet2_48khz_hr_gif.gif`, `figures/live_demo.png`, `COMMUNITY.md` and `LICENSE`, which are not in the capture. The Apache-2.0 statement comes from the README badge and footer only; licenses of the Hugging Face weights, the EvalSet dataset and Speech-MASSIVE-derived clips were not inspected and are **Unverified**.
- The Hugging Face repository, dataset, live demo, audio-example page, PyPI package and code were not inspected; no installation, download or execution; no figure was reproduced.
- The README capture is undated and has no revision; its model tables for 8 kHz and 48 kHz have no counterpart in the paper. Absent from both sources: ASR-in-the-loop WER, CPU/GPU/mobile RTF, algorithmic latency, memory footprint of the public models, quantized accuracy, per-language and per-noise breakdowns, multi-seed variance, reverberant-room results beyond the augmentation description, and echo/music handling. No sensitive values were found.

[^dpdfnet-paper]: [DPDFNet LaTeX source](../raw/arXiv-2512.16420v3-DPDFNet/main_elsevier.tex) (arXiv 2512.16420v3) — locators: Abstract; Sec. 1 (contributions); Sec. 3.2 `sec:new_eval_set` (supplementary evaluation set); Sec. 4 Table 1 `tab:overall_results`, Table 2 `tab:csv_full_results_with_intrusive`, Table 3 `tab:csv_full_results`; Sec. 4.1 (70 Hz high-pass, metrics, training setup); Sec. 4.5 `sec:results`; Sec. 4.7 "Deployment DPDFNet on NeuPro-Nano" and `real_time_npn_500mhz.png`; Sec. 2.1 Denoising Framework equations (DF order N = 5, look-ahead ℓ = 2).

[^dpdfnet-readme]: [DPDFNet GitHub README](../raw/arXiv-2512.16420v3-DPDFNet/README-github.md) (undated capture) — locators: `Model Profile` (8/16/48 kHz tables); `Install the PyPI Package` (CLI, Python API, `Streaming (Real-Time) API` and its Notes); `Run From Source` steps 1–3 and ONNX export; `Real-Time Demo`; `Troubleshooting / FAQ` (CPU too slow); `Evaluation Metrics`; `Citation`; `License`.
