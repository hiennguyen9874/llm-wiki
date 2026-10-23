---
type: Concept
title: ClearVoice
description: Alibaba/ModelScope ClearerVoice-Studio inference package unifying speech enhancement, separation, super-resolution, and audio-visual target speaker extraction with six MossFormer/FRCRN checkpoints and self-reported PESQ/SI-SNRi benchmarks, but no ASR, latency, streaming, or license evidence.
tags: [pipeline, speech-enhancement, denoising, speech-separation, super-resolution, target-speaker-extraction, mossformer, python]
status: draft
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T12:00:00Z }
stale_after: 2027-10-21
sources:
  - id: clearvoice-readme
    resource: ../raw/ClearVoice.md
    kind: documentation
    title: ClearVoice README capture (ClearerVoice-Studio `clearvoice/` package)
---

ClearVoice is the `clearvoice` Python package of ClearerVoice-Studio (`modelscope/ClearerVoice-Studio`, Alibaba SpeechLab `alibabasglab` checkpoints) that exposes pre-trained models for four tasks behind one `ClearVoice(task=..., model_names=[...])` interface: speech enhancement (16 kHz and 48 kHz), speech separation (16 kHz), speech super-resolution (48 kHz), and audio-visual target speaker extraction (16 kHz). For the voice pipeline it is a candidate noise-suppression front end or speaker-isolation stage; the README gives only signal-quality metrics (PESQ, SI-SNRi, LSD), no ASR word-error results, no latency or real-time-factor figures, and no statement of streaming support or license (**Reported**).[^clearvoice-readme]

## Model inventory

| Task | Sampling rate | Checkpoints |
| --- | --- | --- |
| Speech enhancement | 16 kHz and 48 kHz | `MossFormer2_SE_48K`, `FRCRN_SE_16K`, `MossFormerGAN_SE_16K` |
| Speech separation | 16 kHz | `MossFormer2_SS_16K` |
| Speech super-resolution | 48 kHz | `MossFormer2_SR_48K` |
| Audio-visual target speaker extraction | 16 kHz | `AV_MossFormer2_TSE_16K` |

- Checkpoints are hosted on HuggingFace under `alibabasglab/`; they download automatically on first inference into `./clearvoice/checkpoints`, with ModelScope (`iic/ClearerVoice-Studio`) as the manual fallback (**Reported**).[^clearvoice-readme]
- Demos: a HuggingFace Space and a ModelScope Studio (links only; not inspected) (**Reported**).[^clearvoice-readme]

## Usage

- Install with `pip install clearvoice`, or clone the repository, `cd ClearerVoice-Studio/clearvoice`, and `pip install --editable .`. Three demo scripts exist: `demo.py`, `demo_with_more_comments.py`, and `demo_Numpy2Numpy.py`; cases are enabled by setting flags to `True` (**Reported**).[^clearvoice-readme]
- FFmpeg is optional: needed only for non-`.wav` formats (apt, Homebrew, or a Windows static build on `PATH`). Supported audio is `.flac` and `.wav`; supported video is `.avi`, `.mp4`, `.mov`, `.webm` (**Reported**).[^clearvoice-readme]
- `demo_Numpy2Numpy.py` demonstrates an in-memory NumPy-array-in, NumPy-array-out interface instead of file I/O, which is the form relevant to a live pipeline; its code, buffering, and latency behavior were not captured (**Reported**).[^clearvoice-readme]
- Sample call (enhancement): `ClearVoice(task='speech_enhancement', model_names=['MossFormer2_SE_48K'])`, then call the object on a wav path, directory, or `.scp` list file; `online_write=False` returns the audio for `write(...)`, `True` writes to `output_path`. For `speech_enhancement` and `speech_separation` on a single wav file only `online_write=False` is supported (**Reported**).[^clearvoice-readme]
- The parameter description lists `task` as one of `speech_enhancement`, `speech_separation`, `target_speaker_extraction`; the super-resolution task string is not named there, though the model table lists the task (**Observed** gap).[^clearvoice-readme]

## Reported benchmarks

All figures come from the README's own tables; the README says it evaluates *unified* models on two test sets rather than per-test-set tailored models, and computes metrics with its `SpeechScore` tool (**Reported**).[^clearvoice-readme]

**Speech enhancement, PESQ (higher is better):**

| Model | VoiceBank+DEMAND (16 kHz) | DNS-Challenge-2020 non-reverb (16 kHz) | VoiceBank+DEMAND (48 kHz) |
| --- | --- | --- | --- |
| Noisy input | 1.97 | 1.58 | 1.97 |
| `FRCRN_SE_16K` | 3.23 | 3.24 | n/a |
| `MossFormerGAN_SE_16K` | 3.47 | 3.57 | n/a |
| `MossFormer2_SE_48K` | 3.16 | 2.94 | 3.15 |
| Resemble Enhance | n/a | n/a | 2.84 |
| DeepFilterNet | n/a | n/a | 3.03 |

- On the 16 kHz VoiceBank+DEMAND table `MossFormerGAN_SE_16K` is bolded best on PESQ, STOI (0.96), SI-SDR (19.45), and CSIG; `FRCRN_SE_16K` is bolded best on COVL, P808_MOS, BAK, and FWSEGSNR. On DNS-2020 `MossFormerGAN_SE_16K` is bolded best on most columns, with `MossFormer2_SE_48K` scoring below both 16 kHz-specialist models there on PESQ, SI-SDR (17.75 vs 20.60) and CBAK (**Reported**).[^clearvoice-readme]
- On the 48 kHz VoiceBank+DEMAND table `MossFormer2_SE_48K` leads Resemble Enhance (open-source 44.1 kHz enhancer from Resemble AI, resampled to 48 kHz for the test) and DeepFilterNet on PESQ, STOI, SI-SDR (19.36 vs 12.42 and 15.71); DeepFilterNet wins SDR (15.79 vs 4.06) and several other columns (**Reported**).[^clearvoice-readme]
- The README notes anomalies in LLR and LSD for the 48 kHz models and says the cause will be investigated; `MossFormer2_SE_48K` LLR is `NA` and its 48 kHz LSD (1.86, lower is better) is worse than the noisy input's 1.45 (**Reported**; comparison **Synthesis**).[^clearvoice-readme]

**Speech separation, SI-SNRi (dB, higher is better):** `MossFormer2_SS_16K` scores 15.5 on LRS2_2Mix, 22.0 on WSJ0-2Mix, 16.7 on Libri2Mix, and 17.4 on WHAM!. It is best on LRS2_2Mix (above TDANet Large 14.2) and tied best on WHAM! with SPMamba (17.4), but below TF-GridNet (22.8) and SPMamba (22.5) on WSJ0-2Mix and below SPMamba (19.9) and TF-GridNet (19.8) on Libri2Mix. Comparison numbers are copied from the TDANet and SPMamba repositories; the MossFormer2 figures come from one unified 16 kHz model evaluated without per-dataset retraining and scored on audio downsampled to 8 kHz, whereas every baseline was trained and tested per dataset (**Reported**).[^clearvoice-readme]

**Speech super-resolution:** on the VoiceBank+DEMAND 48 kHz test set downsampled to 16/24/32 kHz, the README's table reports Log Spectral Distance of 2.80 / 2.60 / 2.29 (48 kHz reference 1.46) for the original input versus 1.93 / 1.52 / 1.50 (1.42) after `MossFormer2_SR_48K`, with PESQ 1.97 versus 3.15. The enhanced row applied `MossFormer2_SE_48K` for denoising before super-resolution, so the PESQ gain is attributed by the README to enhancement (16 kHz PESQ improves markedly, LSD only marginally), and the LSD gains to super-resolution. The table's column header and row labels (`Origin`, `Enhanced`) are terse and the metric assignment is inferred from the prose (**Reported**; reading **Synthesis**).[^clearvoice-readme]

**Audio-visual target speaker extraction:** no benchmark appears for `AV_MossFormer2_TSE_16K` (**Observed** absence).[^clearvoice-readme]

## Voice-pipeline implications

- The only quantitative evidence is perceptual and signal-level quality; whether any ClearVoice model helps or hurts ASR is untested here, and [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) records conflicting external studies, so any use before STT should be A/B tested on WER/CER in the target language (**Synthesis**).[^clearvoice-readme]
- Several checkpoints (`MossFormer2_SE_48K`, `MossFormer2_SR_48K`) are 48 kHz, which does not match the 16 kHz input most ASR and VAD components expect; resampling would be required (**Synthesis** from the stated sampling rates).[^clearvoice-readme]
- Speech separation and audio-visual target speaker extraction address overlapped speech and speaker isolation, not just stationary noise; the AV model needs video input, which a typical audio-only voice agent lacks (**Synthesis**).[^clearvoice-readme]

## Relationships

- Used as a candidate in [Speech Enhancement Before ASR](speech-enhancement-before-asr.md), whose source report lists ClearerVoice-Studio (FRCRN, MossFormer2, target speaker extraction) among open enhancement options without benchmarks (**Synthesis**).[^clearvoice-readme]
- Comparable to [Facebook Denoiser](facebook-denoiser.md) (causal waveform enhancer, CC-BY-NC, README without quality metrics) and [Denoiser Live Streaming](denoiser-live-streaming.md); ClearVoice at least reports PESQ and related metrics, but neither README establishes causal/streaming performance for ClearVoice (**Synthesis**).[^clearvoice-readme]
- Smaller-scale alternative: [UL-UNAS](ul-unas.md) is a 171k-parameter, 35M MACS/s causal enhancer with PESQ reported on DNS3 and VCTK-DEMAND, a different metric setup from this README's tables, so the numbers are not directly comparable (**Synthesis**).[^clearvoice-readme]
- The 48 kHz PESQ/SDR baseline [Resemble Enhance](resemble-enhance.md) has its own page, with the tool's README-documented usage and training (**Synthesis**).
- Related to [SAM Audio GGUF](sam-audio-gguf.md): both address source separation or extraction before ASR, with different model families (**Synthesis**).[^clearvoice-readme]
- Related to [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md): enhancement, separation, and target-speaker extraction are alternatives or complements to echo cancellation and speaker lock (**Synthesis**).[^clearvoice-readme]

## Coverage and limits

- Ledger: the entry point `raw/ClearVoice.md` (README capture, undated, no revision, about 13 KB) was read in full. Not captured or inspected: the `clearvoice` code, `demo*.py` scripts, `samples/`, `speechscore/`, model cards, checkpoints, the demo Spaces, the Chinese tutorial link, the cited papers (MossFormer2, FRCRN, MossFormerGAN, TDANet, SPMamba, etc.), and the VoiceBank+DEMAND and DNS-2020 datasets. The README's table of contents lists "1. Introduction" and "2. Usage" but the file also has a "3. Model Performance" section (**Observed**).[^clearvoice-readme]
- Absent: license, revision, parameter counts, model sizes, training data, latency or RTF, streaming/causality, GPU/CPU requirements, and any ASR or diarization effect (**Observed** absence).[^clearvoice-readme]
- Bolding in the metric tables is inconsistent for metrics where lower is better or where the best value is ambiguous (for example ISR and SDR columns); treat bold as the README's marking, not a verified ranking (**Observed**).[^clearvoice-readme]
- All figures are self-reported by the package authors on their own evaluation pipeline; none was reproduced. No installation, download, or execution was performed. No sensitive values were found in the capture.

[^clearvoice-readme]: [ClearVoice README capture](../raw/ClearVoice.md) — locators: `1. Introduction` (task/model table, checkpoint download); `2. Usage` › `Install via PyPI`, `Install FFmpeg (optional)`, `Install from GitHub`, `Demo script`, `Sample Python Script` and `Parameter Description`; `3. Model Performance` › `Speech enhancement models` (three metric tables and the 48 kHz anomaly note), `Speech separation models` (SI-SNRi table and note), `Speech super-resolution model` (LSD/PESQ table).
