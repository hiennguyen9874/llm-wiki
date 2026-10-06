---
type: Concept
title: Parakeet TDT 0.6B V2
description: NVIDIA 600M-parameter English offline FastConformer-TDT ASR model with punctuation, capitalization, word timestamps, 120K-hour Granary training, and published multi-domain WER plus noise and telephony robustness tables.
tags: [stt, asr, english, fastconformer, tdt, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: parakeet-tdt-card
    resource: ../raw/parakeet-tdt-0.6b-v2.md
    kind: documentation
    title: Parakeet TDT 0.6B V2 (En)
---

Parakeet TDT 0.6B V2 (`nvidia/parakeet-tdt-0.6b-v2`) is NVIDIA's ~600M-parameter English offline ASR model that transcribes 16 kHz mono speech into punctuated, capitalized English text with word-level timestamps, using a FastConformer encoder with a TDT decoder trained on ~120K hours of Granary data, served as a NeMo checkpoint with a hosted build.nvidia.com API option (**Reported**).[^parakeet-tdt-card]

## Identity and lineage

- Hugging Face ID `nvidia/parakeet-tdt-0.6b-v2`; XL FastConformer variant with TDT decoder (~600M parameters); release date 05/01/2025; commercial and non-commercial use ready (**Reported**).[^parakeet-tdt-card]
- Frontmatter declares `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, language `en`, tags `Transducer`, `TDT`, `FastConformer`, `Conformer`, `pytorch`, `NeMo`, `hf-asr-leaderboard`, and training datasets `nvidia/Granary` plus `nvidia/nemo-asr-set-3.0` (**Observed** by static inspection).[^parakeet-tdt-card]
- License is CC-BY-4.0; deployment geography is global (**Reported**).[^parakeet-tdt-card]
- Card banner points to a newer multilingual successor covered in this wiki as [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) (`nvidia/parakeet-tdt-0.6b-v3`, 25 European languages); no claim about that successor beyond the banner is adopted on this page (**Reported**).[^parakeet-tdt-card]

## Architecture and capabilities

- FastConformer encoder with TDT decoder, trained with full attention; transcribes audio segments up to 24 minutes in a single pass; card reports RTFx of 3380 on the HF Open ASR leaderboard at batch size 128, varying with audio duration and batch size (**Reported**).[^parakeet-tdt-card]
- Native output features: accurate word-level timestamp predictions, automatic punctuation and capitalization, and robustness on spoken numbers and song-lyrics transcription (**Reported**).[^parakeet-tdt-card]
- Input: 16 kHz mono-channel audio in `.wav`/`.flac`; output: 1D text string with punctuation and capitalization (**Reported**).[^parakeet-tdt-card]

## Training data and procedure

- Total: ~120,000 hours of English speech in the Granary dataset — ~10,000 hours human-transcribed NeMo ASR Set 3.0 plus ~110,000 hours pseudo-labeled data (**Reported**).[^parakeet-tdt-card]
- Named human-transcribed sources: LibriSpeech (960 hours), Fisher Corpus, National Speech Corpus Part 1, VCTK, VoxPopuli (English), Europarl-ASR (English), Multilingual LibriSpeech MLS English 2,000-hour subset, Mozilla Common Voice v7.0, AMI; pseudo-labeled sources: YTC (YouTube-Commons), YODAS, LibriLight; all transcripts preserve punctuation and capitalization (**Reported**).[^parakeet-tdt-card]
- Procedure: initialized from a FastConformer SSL checkpoint pretrained with a wav2vec method on LibriLight; 150,000 steps on 64 A100 GPUs with temperature sampling 0.5 for corpus balancing; stage-2 fine-tuning 2,500 steps on 4 A100 GPUs on ~500 hours of high-quality human-transcribed NeMo ASR Set 3.0 data; tokenizer built from training transcripts; training used the `speech_to_text_rnnt_bpe.py` example script with the `fastconformer_hybrid_tdt_ctc_bpe.yaml` TDT config (**Reported**).[^parakeet-tdt-card]

## Benchmarks (greedy Transducer WER without external LM)

All numbers below are source assertions for greedy Transducer decoding without an external language model, scored as WER percent on Open ASR Leaderboard sets; nothing was executed or reproduced for this wiki (**Synthesis**).[^parakeet-tdt-card]

- Base table (average 6.05) (**Reported**):[^parakeet-tdt-card]

| AMI | Earnings-22 | GigaSpeech | LS test-clean | LS test-other | SPGI Speech | TEDLIUM-v3 | VoxPopuli |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 11.16 | 11.15 | 9.74 | 1.69 | 3.19 | 2.17 | 3.38 | 5.95 |

- Frontmatter `model-index` gives per-dataset test splits and configs: AMI Meetings test (`ihm`), Earnings-22 test, GigaSpeech test, LibriSpeech clean and other (both labeled `other` config as printed), SPGI test, TEDLIUM release1, VoxPopuli en, each `args.language: en` (**Observed** by static inspection).[^parakeet-tdt-card]
- Noise robustness (MUSAN music/noise; average WER and relative change): clean 6.05; SNR 10 → 6.95 (−14.75%); SNR 5 → 8.23 (−35.97%); SNR 0 → 11.88 (−96.28%); SNR −5 → 20.26 (−234.66%), with per-dataset columns as printed in the card (**Reported**).[^parakeet-tdt-card]
- Telephony audio (μ-law 8 kHz via 16 kHz→8 kHz→16 kHz conversion): average WER 6.32 versus 6.05 standard, relative change −4.10%, with per-dataset columns as printed (**Reported**).[^parakeet-tdt-card]

## Inference and usage

- NeMo one-liner: `nemo.collections.asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v2")`, then `asr_model.transcribe(['2086-149220-0033.wav'])` after fetching the sample wav; install is latest PyTorch then `pip install -U nemo_toolkit["asr"]` (**Reported**).[^parakeet-tdt-card]
- Timestamped transcription: `asr_model.transcribe([...], timestamps=True)` returning char, word, and segment levels via `output[0].timestamp['word' | 'segment' | 'char']`, with a segment loop printing `start`–`end` spans (**Reported**).[^parakeet-tdt-card]
- Hosted API option on build.nvidia.com with a free API key and the Riva client (`riva.client.ASRService.offline_recognize` with `RecognitionConfig(language_code="en-US", enable_automatic_punctuation=True, enable_word_time_offsets=True)`), plus a CLI via the riva python-clients `transcribe_file_offline.py` script; hosted input is 16-bit mono WAV/OGG/OPUS (auth placeholder in the card is redacted here, not a usable credential) (**Reported**).[^parakeet-tdt-card]

## Deployment requirements

- Runtime engine NeMo 2.2; supported microarchitectures Ampere, Blackwell, Hopper, Volta; preferred OS Linux; at least 2 GB RAM to load, with larger RAM supporting larger audio inputs (**Reported**).[^parakeet-tdt-card]
- Test hardware listed: A10, A100, A30, H100, L4, L40, Turing T4, Volta V100; NVIDIA GPU acceleration via CUDA is the stated performance path over CPU-only (**Reported**).[^parakeet-tdt-card]

## Limitations and trust notes

- Card-stated limits: transcripts may not be 100% accurate, varying with domain, accent, noise, speech type, and context; words outside the trained vocabulary are unlikely to be recognized; not recommended for word-for-word or incomplete-sentence use (**Reported**).[^parakeet-tdt-card]
- Bias subcard: no participation considerations from protected groups and no mitigation measures stated; privacy subcard asserts provenance for training datasets and labeling compliant with privacy law, but notes externally sourced data cannot honor correction/removal requests (**Reported**).[^parakeet-tdt-card]

## Contradictions

- Base performance body table prints a trailing `-` value after the VoxPopuli column (10 values under 9 data labels plus the average); the frontmatter `model-index` lists exactly 8 datasets whose values match the 8 WER figures, so this concept treats the trailing dash as an empty placeholder, not a measurement — neither the card nor this wiki was independently verified (**Observed** by static inspection).[^parakeet-tdt-card]

## Relationships

- Extended by [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): same ~0.6B FastConformer-TDT offline recipe and CC-BY-4.0 terms, expanded from this page's English-only coverage to 25 European languages; read that page for multilingual benchmarks and this page for English-only SNR/telephone robustness rows (**Synthesis**).[^parakeet-tdt-card]
- TDT sibling of [Parakeet RNNT 0.6B](parakeet-rnnt-0.6b.md): same ~0.6B FastConformer-Transducer offline family and CC-BY-4.0 terms, differing in decoder (TDT here versus RNNT there), training data (120K-hour Granary recipe here versus 64K-hour NeMo+Suno recipe there), and output style (punctuated/capitalized with word timestamps here versus lowercase there); compare the two WER tables when choosing a 0.6B offline checkpoint (**Synthesis**).[^parakeet-tdt-card]
- Decoder counterpart of [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md) and [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md): those pages are the CTC checkpoints of the offline Parakeet lineage, while this page is the TDT checkpoint with punctuation, capitalization, and timestamping; read both when choosing between decoder types (**Synthesis**).[^parakeet-tdt-card]
- Scale counterpart of [Parakeet RNNT 1.1B](parakeet-rnnt-1.1b.md): that page is the larger ~1.1B RNNT checkpoint on the 64K-hour recipe, while this page is the 0.6B TDT checkpoint on the Granary recipe with robustness tables; compare when trading model scale against punctuated output and noise/telephone characterization (**Synthesis**).[^parakeet-tdt-card]
- Contrast streaming operating points with [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md) and [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md): those pages cover cache-aware chunked streaming and overlapped-multitalker streaming respectively, versus this page's offline up-to-24-minute single-pass transcription (**Synthesis**).[^parakeet-tdt-card]
- Compare offline English accuracy with [Canary-1b-v2](canary-1b-v2.md), [Qwen3-ASR family](qwen3-asr-family.md), and [Audio8-ASR-0.1B](audio8-asr-0.1b.md): this page's differentiator in the wiki is the 0.6B TDT greedy WER table on eight Open ASR Leaderboard sets plus SNR and telephony robustness rows (**Synthesis**).[^parakeet-tdt-card]

## Coverage and limits

- Source inspected statically only; no NeMo install, no checkpoint download, no audio transcribed, and no WER figure reproduced (**Synthesis**).[^parakeet-tdt-card]
- Referenced but unfetched and absent from `raw/`: NeMo documentation and GitHub example/config/tokenizer paths, FastConformer paper [1], TDT paper [2], NeMo toolkit [3], YTC [4], YODAS [5], Open ASR Leaderboard [6], LibriLight/MOSEL [7], Granary [8], Hugging Face demo space, build.nvidia.com API, Riva references, sample wav and widget audio; all install and inference fences are transcribed, not executed (**Synthesis**).[^parakeet-tdt-card]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^parakeet-tdt-card]

[^parakeet-tdt-card]: [Parakeet TDT 0.6B V2 (En)](../raw/parakeet-tdt-0.6b-v2.md) — locators: frontmatter (`pipeline_tag`, `library_name: nemo`, `language: en`, `tags`, `license: cc-by-4.0`, `datasets`, 8-entry `model-index` with AMI 11.16 / Earnings22 11.15 / GigaSpeech 9.74 / LS-clean 1.69 / LS-other 3.19 / SPGI 2.17 / TEDLIUM 3.38 / VoxPopuli 5.95); header badges (FastConformer-TDT, 0.6B params, en) and v3 banner; `Description` (600M params, punctuation/capitalization/timestamps, 24-minute single pass, RTFx 3380 @ batch 128, key features, demo link); `License/Terms of Use` (CC-BY-4.0); `Use Case` / `Release Date` (05/01/2025) / `Model Architecture` (FastConformer encoder + TDT decoder); `Input` (16 kHz mono wav/flac) / `Output` (punctuated capitalized string); `How to Use` (NeMo `pip install`, `ASRModel.from_pretrained`, `transcribe` fences, timestamps fence with `timestamp['word'/'segment'/'char']`); `Try via API` (build.nvidia.com key + Riva client/CLI fences, 16-bit mono WAV/OGG/OPUS note); `Software Integration` (NeMo 2.2, Ampere/Blackwell/Hopper/Volta, Linux, 2 GB RAM); `Training` (SSL wav2vec LibriLight init, 150k steps / 64 A100, temp sampling 0.5, stage-2 2500 steps / 4 A100 on ~500h NeMo ASR Set 3.0, example script + TDT yaml, tokenizer script); `Training Dataset` (Granary ~120k hrs = 10k human + 110k pseudo, 9+3 named sources); `Performance` (greedy WER without LM, base 8-dataset row avg 6.05 with trailing `-`, MUSAN SNR table, μ-law telephony table, leaderboard link); `Inference` (NeMo engine, A10/A100/A30/H100/L4/L40/T4/V100); `Ethical/Bias/Explainability/Privacy/Safety` subcards; `References [1]–[8]`.
