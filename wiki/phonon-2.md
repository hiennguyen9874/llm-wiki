---
type: Concept
title: Phonon-2
description: Fermion Research 164 MB quantized English ASR model distilled from Parakeet TDT 0.6B V3, reporting 5.21% mean WER on seven Open ASR sets with MLX, CPU, CUDA, and Docker runtimes.
tags: [stt, asr, english, quantization, edge-deployment, parakeet, mlx]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T23:05:00Z }
stale_after: 2027-10-06
sources:
  - id: phonon-2-card
    resource: ../raw/Phonon-2.md
    kind: documentation
    title: Phonon-2 model card
  - id: parakeet-redux-card
    resource: ../raw/parakeet-redux.md
    kind: documentation
    title: Moondream Parakeet Redux model card
---

Phonon-2 is Fermion Research's quantized English ASR checkpoint derived from NVIDIA's `parakeet-tdt-0.6b-v3`, reporting a 5.21% mean word error rate over seven Open ASR Leaderboard English sets from a 164 MB download, with Apple-silicon MLX, Linux/Windows CPU, and CUDA Docker runtimes (**Reported**).[^phonon-2-card]

## Identity and lineage

- Model name Phonon-2; the card frontmatter declares `base_model: nvidia/parakeet-tdt-0.6b-v3` with `base_model_relation: quantized`, English language, `library_name: mlx`, `pipeline_tag: automatic-speech-recognition`, and `metrics: wer` (**Observed** by static inspection).[^phonon-2-card]
- Based on `parakeet-tdt-0.6b-v3` by NVIDIA; the tokenizer and output conventions (punctuation, casing, numerals) are the original's (**Reported**).[^phonon-2-card]
- The model shipped inside [Detta](https://www.fermionresearch.com/products/detta), the dictation app for the Mac (**Reported**).[^phonon-2-card]
- License CC-BY-4.0, same as the original, with a `NOTICE` file listing the changes; the command-line package and the repository code are Apache 2.0 (**Reported**).[^phonon-2-card]

## Quantization and size

- The encoder holds each weight at one of five learned levels in about 2.1 bits (**Reported**).[^phonon-2-card]
- Download size 164 MB against the 2,508 MB full-precision teacher in the same table, described as a download 15 times smaller (**Reported**).[^phonon-2-card]
- Card headline claim: the most accurate open speech-recognition model for English under 900 MB, averaging 5.21% word error across the seven English sets and beating models multiple times its size in raw bytes (**Reported**).[^phonon-2-card]
- Teacher-parity claim: holds the accuracy of its 2.5 GB full-precision teacher, reaching 100.8% of the teacher's word accuracy on parliamentary speech and beating it on meetings (**Reported**); mapped to the table's VoxPopuli (2.46 vs 3.19, parliamentary) and AMI (9.37 vs 9.42, meetings) cells this reads as a VoxPopuli win and a narrow AMI win (**Synthesis**).[^phonon-2-card]

## Benchmarks (vendor-run Open ASR table)

Vendor-run table using the Open ASR Leaderboard's code on the full test sets; dagger rows are the leaderboard's published rows and the other rows reuse its code (**Reported**). Values are WER percent; Average is the row mean as printed (**Reported**).[^phonon-2-card]

| Model | Download | LS clean | LS other | AMI | Earnings-22 | GigaSpeech | SPGISpeech | VoxPopuli | Average |
| --- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| **Phonon-2** | **164 MB** | 1.72 | 3.92 | 9.37 | 6.96 | 8.35 | 3.70 | **2.46** | 5.21 |
| Parakeet TDT 0.6B v3, teacher† | 2,508 MB | **1.52** | **3.13** | 9.42 | **5.85** | **7.99** | 3.63 | 3.19 | **4.96** |
| Parakeet Redux | 178 MB | 1.94 | 4.35 | **9.16** | 7.90 | 8.62 | 4.01 | 3.87 | 5.69 |
| Phonon-1 | 415 MB | 2.11 | 5.03 | 10.31 | 12.34 | 8.73 | 3.67 | 3.73 | 6.56 |
| Canary 180M Flash† | 737 MB | **1.52** | 3.42 | 12.09 | 8.33 | 8.87 | **2.04** | 3.57 | 5.69 |
| Voxtral Mini 4B Realtime† | ~8,000 MB\* | 1.62 | 4.94 | 13.34 | 9.31 | 8.80 | 2.23 | 2.60 | 6.12 |
| Whisper large-v3-turbo† | 1,618 MB | 2.13 | 3.71 | 13.88 | 8.09 | 8.47 | 2.79 | 7.02 | 6.58 |
| Nemotron 3.5 ASR Streaming 0.6B† | 2,368 MB | 2.83 | 6.79 | 13.43 | 15.30 | 9.86 | 3.27 | 4.24 | 7.96 |

- Footnote in source: size marked \* is from the parameter count at 16 bits (**Reported**).[^phonon-2-card]
- Comparability limit: this 7-set selection (no TEDLIUM) and vendor-run scoring differ from the 8-set card protocols behind neighboring [ASR/STT Model Survey](asr-stt-model-survey.md) rows, so gaps under ~0.5 points across cards should not drive a decision alone (**Synthesis**).[^phonon-2-card]

## Speed (vendor-reported throughput)

- About 20 seconds per hour of audio on an M5 MacBook Air (174x realtime), 143x on eight Zen 5 cores (16 vCPU), and 6,680x on one H100 in batches of 128 (**Reported**).[^phonon-2-card]
- No latency, streaming-mode, or word-timestamp accuracy figures are stated beyond the `--json` word-timing output; treat the speed rows as throughput, not streaming latency (**Synthesis**).[^phonon-2-card]

## Inference and usage

- Apple silicon command line: `pip install fermion-research` plus `pip install mlx mlx-audio mlx-lm soundfile scipy zstandard`, then `phonon transcribe recording.wav` or `fermion transcribe phonon-2 recording.wav` (**Reported**).[^phonon-2-card]
- `--json` adds a start and end time for every word; the command line and server are documented at `fermionresearch.com/docs/speech` (**Reported**).[^phonon-2-card]
- The same package runs on Linux (x86-64 and Arm) and Windows CPUs with engines at `github.com/fermionresearch/phonon` (**Reported**).[^phonon-2-card]
- Docker CPU and GPU fences (pinned tags in source): `ghcr.io/fermionresearch/phonon-cpu:2.0.6 transcribe phonon-2 /audio/recording.wav` and `ghcr.io/fermionresearch/phonon-cuda:1.0.5 transcribe phonon-2 /audio/recording.wav`, both mounting `$PWD:/audio` and a `phonon-cache` volume (**Reported**).[^phonon-2-card]

## Relationships

- Derived from [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): keeps the teacher's tokenizer and punctuation/casing/numeral conventions while quantizing the encoder to ~2.1 bits; prefer that page for the 25-language multilingual coverage and this page for the English-only sub-900MB accuracy/size operating point (**Synthesis**).[^phonon-2-card]
- In-card baselines with a new wiki concept: [Parakeet Redux](parakeet-redux.md) (178 MB, 5.69 in this vendor-run table; canonical card reports ternary 1.58-bit weights, 113× realtime on eight x86 cores, and 6.55% seven-set Open ASR average with FLEURS and long-form wins) (**Reported**).[^phonon-2-card][^parakeet-redux-card] Remaining in-card baselines without wiki concepts (no links created): Phonon-1 (415 MB, 6.56) and Canary 180M Flash (737 MB, 5.69) (**Reported**).[^phonon-2-card]
- Contrasts with offline giants in the same table: [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) (~8 GB at 16 bits, 6.12) and [TheWhisper-Large-V3-Turbo](thewhisper-large-v3-turbo.md) (1,618 MB, 6.58) both trail Phonon-2's 5.21 in this vendor-run table despite far larger downloads (**Reported**; cross-card comparability limit above applies).[^phonon-2-card]
- Contrasts with streaming: [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) (2,368 MB, 7.96 in this table) trades accuracy for cache-aware 80–1120 ms streaming while Phonon-2 is an offline throughput play with no streaming-latency claim (**Synthesis**).[^phonon-2-card]

## Coverage and limits

- Source inspected statically only; no checkpoint downloaded, no audio transcribed, and no WER or RTFx figure reproduced (**Synthesis**).[^phonon-2-card]
- Referenced but unfetched and absent from `raw/`: Detta product page, `fermionresearch.com/docs/speech` CLI/server docs, PyPI `fermion-research` package, `github.com/fermionresearch/phonon` CPU/CUDA engines, Docker images `phonon-cpu:2.0.6` / `phonon-cuda:1.0.5`, NOTICE file, Open ASR Leaderboard code and full test sets; all install and inference fences are transcribed, not executed (**Synthesis**).[^phonon-2-card]
- All accuracy, size, quantization, and speed claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^phonon-2-card]

[^phonon-2-card]: [Phonon-2 model card](../raw/Phonon-2.md) — locators: frontmatter (`base_model: nvidia/parakeet-tdt-0.6b-v3`, `base_model_relation: quantized`, `language: en`, `library_name: mlx`, `pipeline_tag: automatic-speech-recognition`, `metrics: wer`); `# Phonon-2` intro (sub-900MB claim, 5.21% seven-set average, 100.8% teacher word accuracy on parliamentary speech, meetings win, 15x smaller download, five learned levels in ~2.1 bits, 20 s per hour on M5 Air at 174x / 143x on eight Zen 5 cores / 6,680x on H100 batch-128); `## Benchmarks` (8-row WER table incl. Phonon-2 164 MB 5.21, teacher 2,508 MB 4.96†, Parakeet Redux 5.69, Phonon-1 6.56, Canary 180M Flash 5.69†, Voxtral Mini 4B Realtime ~8,000 MB 6.12†, Whisper large-v3-turbo 1,618 MB 6.58†, Nemotron 3.5 Streaming 2,368 MB 7.96†; † = leaderboard row, \* = 16-bit size estimate); `## Run it` (Detta Mac app; `pip install fermion-research` + `mlx mlx-audio mlx-lm soundfile scipy zstandard`; `phonon transcribe` / `fermion transcribe phonon-2`; `--json` word timings; docs URL; Linux x86-64/Arm + Windows CPU engines; Docker `phonon-cpu:2.0.6` / `phonon-cuda:1.0.5` fences with `/audio` + `phonon-cache` mounts); `## Notes` (parakeet-tdt-0.6b-v3 lineage, original tokenizer and PnC/casing/numeral conventions, CC-BY-4.0 + NOTICE, CLI/repo Apache-2.0).
[^parakeet-redux-card]: [Moondream Parakeet Redux model card](../raw/parakeet-redux.md) — locators: intro (1.58-bit ternary version of `parakeet-tdt-0.6b-v3`, 178 MB, 113× realtime on eight x86 cores, 2.5× fastest other runtime); `Benchmarks` (Open ASR 6.55 vs 6.26, FLEURS 10.56 vs 11.62, TED-LIUM 2.51 vs 2.71).
