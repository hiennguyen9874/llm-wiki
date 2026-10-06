---
type: Concept
title: Parakeet Redux
description: 1.58-bit ternary Parakeet TDT 0.6B V3 derivative with 178 MB weights, 113× CPU realtime, reporting 6.55% English Open ASR WER and 10.56% FLEURS average.
tags: [stt, asr, multilingual, quantization, ternary, parakeet, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: parakeet-redux-card
    resource: ../raw/parakeet-redux.md
    kind: documentation
    title: Moondream Parakeet Redux model card
---

Parakeet Redux (`moondream/parakeet-redux`) is Moondream's 1.58-bit ternary version of NVIDIA's `parakeet-tdt-0.6b-v3` that keeps the same architecture and tokenizer while constraining every encoder weight to -1, 0, or +1, fitting in 178 MB and reporting 113× realtime on eight x86 CPU cores, 6.55% average English Open ASR WER, 10.56% FLEURS average over 25 languages, and 2.51% on TED-LIUM long-form (**Reported**).[^parakeet-redux-card]

## Identity and lineage

- Model name Moondream Parakeet Redux; a 1.58-bit version of [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) (`nvidia/parakeet-tdt-0.6b-v3`) with the same architecture and tokenizer (**Reported**).[^parakeet-redux-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, 25-language list (en, de, fr, es, it, pt, ru, uk, hr, sl, lv, lt, et, fi, sv, da, nl, pl, cs, sk, hu, ro, bg, el, mt), tags `ternary, parakeet, tdt, speech-recognition, cpu, apple-silicon`, and `license: cc-by-4.0` (**Observed** by static inspection).[^parakeet-redux-card]
- Languages, tokenizer, and output conventions (punctuation, casing, numerals) are the original's; license CC-BY-4.0, same as the original (**Reported**).[^parakeet-redux-card]
- Sibling [Parakeet Ultra](parakeet-ultra.md) (`moondream/parakeet-ultra`) is the full-precision post-trained version of the same architecture for GPUs, stated to beat the original on every benchmark (English 5.80 vs 6.26, FLEURS 9.55 vs 11.62, TED-LIUM 1.94 vs 2.71); the release story is deferred to the linked release post (**Reported**).[^parakeet-redux-card]

## Quantization and size

- Every encoder weight is -1, 0, or +1 (ternary, 1.58-bit) (**Reported**).[^parakeet-redux-card]
- Weights 178 MB against the original's 1.2 GB; headline also claims 2.5× the fastest other Parakeet runtime measured and within 0.3 WER of the original on English (**Reported**).[^parakeet-redux-card]

## Benchmarks (WER percent, lower is better)

Headline comparison against the original, scored on the same files with the Open ASR Leaderboard's own pipeline as of September 2026 (its normalizers and compound-merging alignment, FLEURS references as the leaderboard's text column), with Redux run in Photon on an NVIDIA GPU and the original in NeMo in bf16; nothing was executed or reproduced for this wiki (**Reported**; non-reproduction is **Synthesis**).[^parakeet-redux-card]

| Suite | parakeet-tdt-0.6b-v3 | parakeet-redux |
| --- | --: | --: |
| Open ASR Leaderboard, 7 English sets | **6.26** | 6.55 |
| FLEURS, 25 languages | 11.62 | **10.56** |
| Business speech, AA-WER style | **6.15** | 6.96 |
| Background noise, 9 MUSAN conditions | **6.72** | 9.04 |
| TED-LIUM long-form | 2.71 | **2.51** |
| Weights | 1.2 GB | **178 MB** |

### Open ASR Leaderboard (7 English sets)

Audiobooks (LibriSpeech), meetings (AMI), earnings calls (Earnings-22), podcasts and YouTube (GigaSpeech), financial calls (SPGISpeech), and parliament (VoxPopuli) (**Reported**).[^parakeet-redux-card]

| Set | parakeet-tdt-0.6b-v3 | parakeet-redux |
| --- | --: | --: |
| LibriSpeech test-clean | 1.52 | 1.96 |
| LibriSpeech test-other | 3.13 | 4.34 |
| AMI | 10.86 | 10.80 |
| Earnings-22 | 10.75 | 9.95 |
| GigaSpeech | 8.05 | 8.73 |
| SPGISpeech | 3.63 | 4.01 |
| VoxPopuli | 5.88 | 6.07 |
| **average** | **6.26** | **6.55** |

### FLEURS (test split, read Wikipedia sentences)

| Language | parakeet-tdt-0.6b-v3 | parakeet-redux |
| --- | --: | --: |
| Bulgarian | 11.90 | 11.23 |
| Croatian | 10.93 | 9.26 |
| Czech | 10.85 | 10.25 |
| Danish | 16.78 | 15.94 |
| Dutch | 6.18 | 7.45 |
| English | 4.25 | 4.90 |
| Estonian | 13.23 | 9.15 |
| Finnish | 11.05 | 10.38 |
| French | 4.81 | 7.71 |
| German | 4.13 | 5.42 |
| Greek | 35.71 | 32.48 |
| Hungarian | 13.65 | 14.15 |
| Italian | 2.61 | 3.24 |
| Latvian | 21.38 | 12.80 |
| Lithuanian | 21.09 | 17.27 |
| Maltese | 19.13 | 13.65 |
| Polish | 6.70 | 8.59 |
| Portuguese | 4.65 | 4.99 |
| Romanian | 11.54 | 10.32 |
| Russian | 5.91 | 7.91 |
| Slovak | 9.46 | 7.26 |
| Slovene | 21.76 | 16.21 |
| Spanish | 3.12 | 3.71 |
| Swedish | 13.75 | 12.71 |
| Ukrainian | 5.94 | 7.06 |
| **average** | **11.62** | **10.56** |

### Business speech (AA-WER style)

AMI and VoxPopuli with Artificial Analysis cleaning, plus Earnings-22 in 30-second chunks joined per call (**Reported**).[^parakeet-redux-card]

| Set | parakeet-tdt-0.6b-v3 | parakeet-redux |
| --- | --: | --: |
| AMI (cleaned) | 9.52 | 9.14 |
| VoxPopuli (cleaned) | 3.02 | 3.86 |
| Earnings-22, 30-second chunks | 5.90 | 7.89 |
| **average** | **6.15** | **6.96** |

### Background noise (MUSAN, fixed SNR; 0 dB means noise as loud as speech)

| Set | parakeet-tdt-0.6b-v3 | parakeet-redux |
| --- | --: | --: |
| LibriSpeech test-other, 10 dB | 4.12 | 5.66 |
| LibriSpeech test-other, 5 dB | 5.49 | 7.32 |
| LibriSpeech test-other, 0 dB | 9.06 | 10.95 |
| FLEURS German, 10 dB | 5.78 | 8.97 |
| FLEURS German, 5 dB | 8.07 | 12.36 |
| FLEURS German, 0 dB | 14.45 | 19.18 |
| FLEURS Spanish, 10 dB | 3.99 | 4.46 |
| FLEURS Spanish, 5 dB | 4.12 | 5.25 |
| FLEURS Spanish, 0 dB | 5.44 | 7.22 |
| **average** | **6.72** | **9.04** |

- Noise is where the gap to the original is widest: the card attributes it to the ternary encoder's thinner acoustic margin substituting similar-sounding words more often at low SNR, while dropped or invented content is stated to be no more frequent than the original's (**Reported**).[^parakeet-redux-card]

### Long-form (eleven complete TED-LIUM 3 talks, 10–20 minutes each)

| Set | parakeet-tdt-0.6b-v3 | parakeet-redux |
| --- | --: | --: |
| TED-LIUM 3, 11 full talks | 2.71 | **2.51** |

- Redux transcribes through Photon, whose segmenter cuts each talk at pauses found by the model's VAD head into segments of at most 30 seconds; the original runs NeMo's own long-audio path (**Reported**).[^parakeet-redux-card]

## Performance (realtime factor: seconds of audio per second of wall clock, higher is faster)

One utterance at a time; incumbents are parakeet.cpp (ggml), sherpa-onnx and onnx-asr (ONNX Runtime), and on Mac parakeet-mlx, each at its own defaults; x86 uses LibriSpeech test-clean (2,620 utterances) on the same 8 cores, Apple uses a 50-utterance slice of LibriSpeech dev-clean with cool-downs; WER scored the same way as the benchmarks; every speed number is Photon, which reads the packed weights directly with AVX-512 VNNI on x86, NEON on ARM, and Metal on Apple GPUs (**Reported**).[^parakeet-redux-card]

### x86 CPU (AMD EPYC 9575F Zen 5 up to 5.0 GHz, 8 physical cores of one chiplet, DDR5-6000, Ubuntu 22.04)

| Runtime | Weights | Realtime | WER |
| --- | --- | --: | --: |
| **Photon, this model** | ternary, 178 MB | **113×** | 1.94 |
| parakeet.cpp (ggml) | q8_0, 0.94 GB | 45× | 1.51 |
| sherpa-onnx (ONNX Runtime) | int8, 0.67 GB | 42× | 1.97 |
| onnx-asr (ONNX Runtime) | int8, 0.67 GB | 28× | 1.93 |

### Apple silicon (MacBook Air Apple M2, 4 performance + 4 efficiency CPU cores, 10-core GPU, 16 GB unified memory, macOS 15)

| Runtime | Weights | CPU | GPU |
| --- | --- | --: | --: |
| **Photon, this model** | ternary, 178 MB | **38×** | **43×** |
| parakeet.cpp (ggml) | q8_0, 0.94 GB | 12× | 38× (Metal) |
| parakeet.cpp (ggml) | f16, 1.44 GB | 9× | 39× (Metal) |
| parakeet-mlx | fp32, 2.51 GB | — | 37× |
| onnx-asr (ONNX Runtime) | int8, 0.67 GB | 33× | — |
| sherpa-onnx (ONNX Runtime) | int8, 0.67 GB | 28× | — |

## Inference and usage

- Runs with Photon (`moondream.ai/photon`); install `pip install moondream` (2.4.0 or later), then `md.photon("moondream/parakeet-redux", device="cpu")` with `device` one of `cpu`, `mps`, or `cuda`, defaulting to CUDA, then Apple silicon, then CPU (**Reported**).[^parakeet-redux-card]
- `speech.transcribe(audio="speech.wav")` returns `result["text"]`; `timestamps="segment"` returns one entry per sentence with start and end in seconds in `result["segments"]`; `timestamps="word"` adds per-word start, end, and word inside each segment (**Reported**).[^parakeet-redux-card]
- Long audio is segmented by the model itself: the weights carry a small voice-activity head on the encoder's subsampler, and Photon uses it to cut recordings at pauses into segments of at most 30 seconds, with no external VAD model needed (**Reported**).[^parakeet-redux-card]

## Relationships

- Ternary-quantized derivative of [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): same FastConformer-TDT recipe, tokenizer, 25 European languages, and CC-BY-4.0 terms, trading full-precision weights (1.2 GB) for ternary encoder weights (178 MB) with a small English penalty (6.55 vs 6.26), a noise penalty (9.04 vs 6.72), and wins on FLEURS pooled (10.56 vs 11.62) and TED-LIUM long-form (2.51 vs 2.71); prefer that page for the teacher baseline and this page for the CPU/edge operating point (**Synthesis**).[^parakeet-redux-card]
- Contrasts with quantized English derivative [Phonon-2](phonon-2.md): that page keeps the same teacher's conventions at ~2.1-bit five-level encoder precision for a 164 MB English-only throughput play (5.21% seven-set mean in its vendor-run table, where it lists this model at 5.69), while this page keeps 25-language multilingual coverage at ternary precision with Photon CPU/GPU runtimes (**Synthesis**).[^parakeet-redux-card]
- Contrasts with multilingual finetune [Orukeet](orukeet.md): that page keeps full parameter count with frozen Gabor taps for accuracy (FLEURS pooled 9.85 vs 11.01), while this page compresses the encoder to ternary for size and CPU speed (**Synthesis**).[^parakeet-redux-card]
- Full-precision sibling [Parakeet Ultra](parakeet-ultra.md) keeps the same teacher at full precision for the GPU accuracy operating point (English 5.80, FLEURS 9.55, TED-LIUM 1.94 via Photon on NVIDIA GPU), while this page trades a small English penalty and a noise penalty for 178 MB ternary CPU/edge weights (**Synthesis**).[^parakeet-redux-card]
- Surveyed alongside sibling checkpoints in [ASR/STT Model Survey](asr-stt-model-survey.md): compare its 7-set English, 25-language FLEURS, noise, and CPU realtime rows against the teacher, Phonon-2, and Orukeet rows when choosing a Parakeet-family checkpoint (**Synthesis**).[^parakeet-redux-card]

## Coverage and limits

- Source inspected statically only; no Photon install, no checkpoint download, no audio transcribed, and no WER or realtime-factor figure reproduced (**Synthesis**).[^parakeet-redux-card]
- Referenced but unfetched and absent from `raw/`: Hugging Face `parakeet-tdt-0.6b-v3` and `moondream/parakeet-ultra` pages, release post, Photon page and package, LibriSpeech test-clean/dev-clean slices, AMI, Earnings-22, GigaSpeech, SPGISpeech, VoxPopuli, FLEURS, TED-LIUM 3, MUSAN, and the Open ASR Leaderboard pipeline and normalizers; all install and inference fences are transcribed, not executed (**Synthesis**).[^parakeet-redux-card]
- All accuracy, size, quantization, runtime, and speed claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^parakeet-redux-card]

[^parakeet-redux-card]: [Moondream Parakeet Redux model card](../raw/parakeet-redux.md) — locators: frontmatter (`license: cc-by-4.0`, 25-code `language` list, `pipeline_tag: automatic-speech-recognition`, `tags: ternary/parakeet/tdt/speech-recognition/cpu/apple-silicon`); intro (1.58-bit version of `parakeet-tdt-0.6b-v3`, same architecture/tokenizer, -1/0/+1 encoder, 178 MB, 113× realtime on eight x86 cores, 2.5× fastest other runtime, within 0.3 WER English, FLEURS and long-form wins; 6-row headline table with Open ASR 6.55 vs 6.26 / FLEURS 10.56 vs 11.62 / business 6.96 vs 6.15 / noise 9.04 vs 6.72 / TED-LIUM 2.51 vs 2.71 / 178 MB vs 1.2 GB; Parakeet Ultra sibling and release-post link); `Usage` (`pip install moondream` 2.4.0+, `md.photon("moondream/parakeet-redux", device="cpu")` with `cpu/mps/cuda` default order, `transcribe` text/segment/word fences; Photon AVX-512-VNNI/NEON/Metal line); `Performance` (realtime-factor definition, one-utterance method, incumbent list with own defaults, x86 LibriSpeech test-clean 2,620 utterances on same 8 cores, Apple 50-utterance dev-clean slice with cool-downs; x86 table EPYC 9575F/DDR5-6000/Ubuntu 22.04 with Photon 113×/1.94 vs parakeet.cpp 45×/1.51 vs sherpa-onnx 42×/1.97 vs onnx-asr 28×/1.93; Apple table M2 Air 16 GB/macOS 15 with Photon 38× CPU/43× GPU vs parakeet.cpp q8_0/f16, parakeet-mlx fp32, onnx-asr/sherpa-onnx int8 rows); `Benchmarks` (same-files Open ASR Leaderboard September-2026 pipeline with normalizers and compound-merging alignment, FLEURS text-column refs, Photon-GPU vs NeMo-bf16 note; 7-row Open ASR table; 25-row FLEURS table; 3-row AA-WER business table; 9-row MUSAN noise table with 0 dB definition and thinner-margin substitution note; TED-LIUM 11-talk table with Photon ≤30 s VAD segmenter vs NeMo long-audio path); `Notes` (NVIDIA lineage, original languages/tokenizer/output conventions, Photon runtime, encoder-subsampler VAD head with no external VAD, CC-BY-4.0).
