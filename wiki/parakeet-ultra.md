---
type: Concept
title: Parakeet Ultra
description: Post-trained full-precision Parakeet TDT 0.6B V3 derivative reporting 5.80% English Open ASR WER and 9.55% FLEURS average with Photon GPU inference and built-in VAD long-form segmentation.
tags: [stt, asr, multilingual, parakeet, photon, gpu]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: parakeet-ultra-card
    resource: ../raw/parakeet-ultra.md
    kind: documentation
    title: Moondream Parakeet Ultra model card
---

Parakeet Ultra (`moondream/parakeet-ultra`) is Moondream's post-trained full-precision version of NVIDIA's `parakeet-tdt-0.6b-v3` that keeps the same architecture, tokenizer, and 0.6B parameters while reporting wins on every benchmark group in its card — 5.80% average English Open ASR WER, 9.55% FLEURS average over 25 languages, and 1.94% on TED-LIUM long-form — served through Photon on an NVIDIA GPU (**Reported**).[^parakeet-ultra-card]

## Identity and lineage

- Model name Moondream Parakeet Ultra; a post-trained version of [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) (`nvidia/parakeet-tdt-0.6b-v3`) with the same architecture, same tokenizer, and same 0.6B parameters in full precision (**Reported**).[^parakeet-ultra-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, the same 25-language list as V3 (en, de, fr, es, it, pt, ru, uk, hr, sl, lv, lt, et, fi, sv, da, nl, pl, cs, sk, hu, ro, bg, el, mt), tags `parakeet, tdt, speech-recognition`, and `license: cc-by-4.0` (**Observed** by static inspection).[^parakeet-ultra-card]
- Languages, tokenizer, and output conventions (punctuation, casing, numerals) are the original's; license CC-BY-4.0, same as the original (**Reported**).[^parakeet-ultra-card]
- Sibling [Parakeet Redux](parakeet-redux.md) (`moondream/parakeet-redux`) is the ternary 178 MB version of the same architecture built for CPUs and Apple silicon; the release story for both models is deferred to the linked release post (**Reported**).[^parakeet-ultra-card]

## Benchmarks (WER percent, lower is better)

Headline comparison against the original, scored on the same files with the Open ASR Leaderboard's own pipeline as of September 2026 (its normalizers and compound-merging alignment, with the FLEURS references prepared as the leaderboard's text column); Ultra runs in Photon on an NVIDIA GPU and the original in NeMo in bf16; every accuracy number on the page is stated to be Photon on an NVIDIA GPU; nothing was executed or reproduced for this wiki (**Reported**; non-reproduction is **Synthesis**).[^parakeet-ultra-card]

| Suite | parakeet-tdt-0.6b-v3 | parakeet-ultra |
| --- | --: | --: |
| Open ASR Leaderboard, 7 English sets | 6.26 | **5.80** |
| FLEURS, 25 languages | 11.62 | **9.55** |
| Business speech, AA-WER style | 6.15 | **5.79** |
| Background noise, 9 MUSAN conditions | 6.72 | **5.82** |
| TED-LIUM long-form | 2.71 | **1.94** |

### Open ASR Leaderboard (7 English sets)

Audiobooks (LibriSpeech), meetings (AMI), earnings calls (Earnings-22), podcasts and YouTube (GigaSpeech), financial calls (SPGISpeech), and parliament (VoxPopuli) (**Reported**).[^parakeet-ultra-card]

| Set | parakeet-tdt-0.6b-v3 | parakeet-ultra |
| --- | --: | --: |
| LibriSpeech test-clean | 1.52 | 1.41 |
| LibriSpeech test-other | 3.13 | 2.98 |
| AMI | 10.86 | 9.77 |
| Earnings-22 | 10.75 | 9.76 |
| GigaSpeech | 8.05 | 7.71 |
| SPGISpeech | 3.63 | 3.34 |
| VoxPopuli | 5.88 | 5.65 |
| **average** | **6.26** | **5.80** |

### FLEURS (test split, read Wikipedia sentences, a few hundred per language)

| Language | parakeet-tdt-0.6b-v3 | parakeet-ultra |
| --- | --: | --: |
| Bulgarian | 11.90 | 10.09 |
| Croatian | 10.93 | 9.65 |
| Czech | 10.85 | 9.97 |
| Danish | 16.78 | 14.31 |
| Dutch | 6.18 | 5.46 |
| English | 4.25 | 3.55 |
| Estonian | 13.23 | 9.69 |
| Finnish | 11.05 | 9.19 |
| French | 4.81 | 4.32 |
| German | 4.13 | 3.61 |
| Greek | 35.71 | 32.25 |
| Hungarian | 13.65 | 10.76 |
| Italian | 2.61 | 2.00 |
| Latvian | 21.38 | 15.95 |
| Lithuanian | 21.09 | 16.36 |
| Maltese | 19.13 | 14.92 |
| Polish | 6.70 | 5.54 |
| Portuguese | 4.65 | 3.96 |
| Romanian | 11.54 | 9.18 |
| Russian | 5.91 | 5.21 |
| Slovak | 9.46 | 7.03 |
| Slovene | 21.76 | 16.64 |
| Spanish | 3.12 | 2.72 |
| Swedish | 13.75 | 11.57 |
| Ukrainian | 5.94 | 4.75 |
| **average** | **11.62** | **9.55** |

### Business speech (AA-WER style)

AMI and VoxPopuli with Artificial Analysis cleaning, plus Earnings-22 in 30-second chunks joined per call (**Reported**).[^parakeet-ultra-card]

| Set | parakeet-tdt-0.6b-v3 | parakeet-ultra |
| --- | --: | --: |
| AMI (cleaned) | 9.52 | 8.48 |
| VoxPopuli (cleaned) | 3.02 | 3.10 |
| Earnings-22, 30-second chunks | 5.90 | 5.78 |
| **average** | **6.15** | **5.79** |

- VoxPopuli (cleaned) is the one sub-split where the original scores better (3.02 vs 3.10); all other headline and sub-split rows favor Ultra (**Reported**).[^parakeet-ultra-card]

### Background noise (MUSAN, fixed SNR; 0 dB means noise as loud as speech)

Clean sets with the half of the MUSAN corpus not used for training mixed in at a fixed signal-to-noise ratio (**Reported**).[^parakeet-ultra-card]

| Set | parakeet-tdt-0.6b-v3 | parakeet-ultra |
| --- | --: | --: |
| LibriSpeech test-other, 10 dB | 4.12 | 3.87 |
| LibriSpeech test-other, 5 dB | 5.49 | 5.10 |
| LibriSpeech test-other, 0 dB | 9.06 | 8.31 |
| FLEURS German, 10 dB | 5.78 | 4.98 |
| FLEURS German, 5 dB | 8.07 | 6.91 |
| FLEURS German, 0 dB | 14.45 | 12.08 |
| FLEURS Spanish, 10 dB | 3.99 | 3.13 |
| FLEURS Spanish, 5 dB | 4.12 | 3.38 |
| FLEURS Spanish, 0 dB | 5.44 | 4.64 |
| **average** | **6.72** | **5.82** |

### Long-form (eleven complete TED-LIUM 3 talks, 10–20 minutes each)

| Set | parakeet-tdt-0.6b-v3 | parakeet-ultra |
| --- | --: | --: |
| TED-LIUM 3, 11 full talks | 2.71 | **1.94** |

- Ultra transcribes through Photon, whose segmenter cuts each talk at pauses found by the model's VAD head into segments of at most 30 seconds; the original runs NeMo's own long-audio path (**Reported**).[^parakeet-ultra-card]

## Performance (realtime factor: seconds of audio per second of wall clock, higher is faster)

One NVIDIA B200 with 128 requests in flight and the same files on both sides; NeMo 3.0 runs the original checkpoint with its own transcribe call at batch 128, Photon runs Ultra (**Reported**).[^parakeet-ultra-card]

| Set | NeMo, parakeet-tdt-0.6b-v3 | Photon, parakeet-ultra |
| --- | --: | --: |
| LibriSpeech test-clean, 2,620 utterances, 5.4 hours | 6,005× | **9,743×** |
| AMI test, 12,643 utterances, 8.7 hours | 4,394× | **6,688×** |

## Inference and usage

- Runs with Photon (`moondream.ai/photon`); install with `pip install moondream`, then `md.photon("moondream/parakeet-ultra")` as a context manager yielding `speech` (**Reported**).[^parakeet-ultra-card]
- `speech.transcribe(audio="speech.wav")` returns `result["text"]`; `timestamps="segment"` returns one entry per sentence with start and end in seconds in `result["segments"]`; `timestamps="word"` adds per-word start, end, and word inside each segment (**Reported**).[^parakeet-ultra-card]
- Long audio is segmented by the model itself: the weights carry a small voice-activity head on the encoder's subsampler, and Photon uses it to cut recordings at pauses into segments of at most 30 seconds, with no external VAD model needed (**Reported**).[^parakeet-ultra-card]

## Relationships

- Post-trained full-precision derivative of [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): same FastConformer-TDT recipe, tokenizer, 25 European languages, and CC-BY-4.0 terms, reporting better figures on every headline suite (English 5.80 vs 6.26, FLEURS pooled 9.55 vs 11.62, business 5.79 vs 6.15, noise 5.82 vs 6.72, TED-LIUM 1.94 vs 2.71) plus higher B200 batch throughput; prefer that page for the teacher baseline and this page for the accuracy-improved GPU operating point (**Synthesis**).[^parakeet-ultra-card]
- Full-precision sibling of [Parakeet Redux](parakeet-redux.md): that page keeps the same teacher at 1.58-bit ternary precision (178 MB, 113× on eight x86 CPU cores, English 6.55, FLEURS 10.56) for the CPU/edge operating point, while this page keeps full precision for the GPU accuracy operating point (**Synthesis**).[^parakeet-ultra-card]
- Contrasts with quantized English derivative [Phonon-2](phonon-2.md): that page keeps the same teacher's conventions at ~2.1-bit encoder precision for a 164 MB English-only throughput play, while this page keeps 25-language multilingual coverage at full precision with Photon GPU serving (**Synthesis**).[^parakeet-ultra-card]
- Contrasts with multilingual finetune [Orukeet](orukeet.md): that page keeps full parameter count with frozen Gabor taps for accuracy (FLEURS pooled 9.85), while this page is a vendor post-train reporting FLEURS pooled 9.55 under its own September-2026 Open ASR Leaderboard scoring protocol; do not compare the two pooled figures directly without reconciling protocols (**Synthesis**).[^parakeet-ultra-card]
- Surveyed alongside sibling checkpoints in [ASR/STT Model Survey](asr-stt-model-survey.md): compare its 7-set English, 25-language FLEURS, business, noise, long-form, and B200 throughput rows against the teacher, Redux, Phonon-2, and Orukeet rows when choosing a Parakeet-family checkpoint (**Synthesis**).[^parakeet-ultra-card]

## Coverage and limits

- Source inspected statically only; no Photon install, no checkpoint download, no audio transcribed, and no WER or realtime-factor figure reproduced (**Synthesis**).[^parakeet-ultra-card]
- Referenced but unfetched and absent from `raw/`: Hugging Face `parakeet-tdt-0.6b-v3` and `moondream/parakeet-ultra` pages, the `moondream` Python package and Photon page, the release post, LibriSpeech test-clean slices, AMI, Earnings-22, GigaSpeech, SPGISpeech, VoxPopuli, FLEURS, TED-LIUM 3, MUSAN, and the Open ASR Leaderboard pipeline and normalizers; all install and inference fences are transcribed, not executed (**Synthesis**).[^parakeet-ultra-card]
- All accuracy, size, runtime, and speed claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^parakeet-ultra-card]

[^parakeet-ultra-card]: [Moondream Parakeet Ultra model card](../raw/parakeet-ultra.md) — locators: frontmatter (`license: cc-by-4.0`, 25-code `language` list, `pipeline_tag: automatic-speech-recognition`, `tags: parakeet/tdt/speech-recognition`); intro (post-trained `parakeet-tdt-0.6b-v3`, same architecture/tokenizer/0.6B full precision, 5-row headline table with Open ASR 5.80 vs 6.26 / FLEURS 9.55 vs 11.62 / business 5.79 vs 6.15 / noise 5.82 vs 6.72 / TED-LIUM 1.94 vs 2.71; Redux sibling and release-post link); `Usage` (`pip install moondream`, `md.photon("moondream/parakeet-ultra")`, `transcribe` text/segment/word fences; every-accuracy-number-is-Photon-on-NVIDIA-GPU note); `Performance` (realtime-factor definition, B200 128-in-flight method with NeMo 3.0 batch-128 baseline; LibriSpeech test-clean 2,620 utterances / 5.4 h 9,743× vs 6,005× and AMI test 12,643 utterances / 8.7 h 6,688× vs 4,394× rows); `Benchmarks` (same-files September-2026 Open ASR Leaderboard pipeline with normalizers and compound-merging alignment, FLEURS text-column refs, Photon-GPU vs NeMo-bf16 note; 7-row Open ASR table; 25-row FLEURS table; 3-row AA-WER business table; 9-row MUSAN noise table with 0 dB definition; TED-LIUM 11-talk table with Photon ≤30 s VAD segmenter vs NeMo long-audio path); `Notes` (NVIDIA lineage, original languages/tokenizer/output conventions, Photon runtime, encoder-subsampler VAD head with no external VAD, CC-BY-4.0).
