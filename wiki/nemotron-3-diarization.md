---
type: Concept
title: Nemotron 3 Diarization
description: NVIDIA open-weight streaming/offline speaker-diarization model for up to eight speakers with arrival-order channels, configurable latency profiles, NeMo and Transformers inference, and published DER/RTFx benchmarks.
tags: [vad, diarization, speaker-tagging, streaming, nemotron]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T17:00:00Z }
stale_after: 2027-10-06
sources:
  - id: nemotron-3-diar-card
    resource: ../raw/Nemotron-3-Diarization.md
    kind: documentation
    title: Nemotron 3 Diarization
  - id: sortformer-4spk-card
    resource: ../raw/diar_sortformer_4spk-v1.md
    kind: documentation
    title: Sortformer Diarizer 4spk v1
---

Nemotron 3 Diarization is NVIDIA's open-weight speaker-diarization model that determines "who spoke when" for up to eight speakers in streaming or offline mode, resolving speaker permutation by ordering output channels on first arrival (Sortformer) and preserving identities across chunks with an Arrival-Order Speaker Cache (AOSC) plus FIFO queue (Streaming Sortformer); the card publishes architecture, four latency configurations (0.32–30.4 s input buffer latency), NeMo and Transformers inference paths, training-data composition (~10,000 h real conversations plus 82,611 h simulated mixtures), DER benchmarks against a 4-speaker Sortformer baseline across eight evaluation conditions, and BF16 RTFx figures on Blackwell (**Reported**).[^nemotron-3-diar-card]

## Identity and release

- Model: NVIDIA Nemotron 3 Diarization (General Access), released 2026-09-23; Hugging Face blog announcement and live demo Space ("Nemotron-Diarization with Streaming ASR") with demo GIF and an 8-speaker audio/video demo are linked from the card (**Reported**).[^nemotron-3-diar-card]
- Card frontmatter declares `license: openmdw-1.1`, `pipeline_tag: voice-activity-detection`, `library_name: nemo`, and tags `speaker-diarization`, `streaming-sortformer`, `speaker-tagging`, `transformers`; the card states the model is ready for commercial or non-commercial use (**Reported**).[^nemotron-3-diar-card]
- Research lineage: Sortformer for permutation-resolved supervision [1], Streaming Sortformer with AOSC/FIFO [2], FastMSS synthetic-mixture toolkit [3], forced-alignment methodology discussion [4], and NEST SSL initialization [5] (**Reported**).[^nemotron-3-diar-card]

## Architecture and I/O

- 31-layer Transformer encoder with Rotary Positional Embeddings (RoPE); 10 ms mel-spectrogram input features downsampled 8× by feature stacking to an 80 ms encoder frame rate; a Conv1D layer above the encoder upsamples predictions back to 10 ms input-feature resolution; AOSC plus FIFO queue for streaming; 100M parameters (1.0 × 10⁸) (**Reported**).[^nemotron-3-diar-card]
- Input: single-channel 16 kHz audio in `.wav`, `.flac`, `.opus`, or `.mp3`; no maximum duration when chunked inference is used (**Reported**).[^nemotron-3-diar-card]
- Output: float tensor of shape `[T, 8]` with per-speaker activity probabilities in `[0, 1]`; eight channels ordered by each speaker's arrival time; default 10 ms frame stride, configurable to any multiple of 10 ms (e.g. 30, 80, 240 ms); probabilities postprocess to generic speaker labels with start/end timestamps, e.g. `["speaker1", 0.51, 12.62]` (**Reported**).[^nemotron-3-diar-card]
- One checkpoint covers the full latency range: input buffer latency as low as 80 ms is supported, but the lowest recommended configuration is 0.32 s and the offline-style configuration uses 30.4 s (**Reported**).[^nemotron-3-diar-card]

## Streaming latency configurations

- Streaming parameters are measured in 80 ms frames: `SPKCACHE_LEN`, `FIFO_LEN`, `CHUNK_LEN`, `RIGHT_CONTEXT`, `UPDATE_PERIOD`; input buffer latency = (`CHUNK_LEN` + `RIGHT_CONTEXT`) × 80 ms, excluding compute time (**Reported**).[^nemotron-3-diar-card]

| Configuration | Latency | `SPKCACHE_LEN` | `FIFO_LEN` | `CHUNK_LEN` | `RIGHT_CONTEXT` | `UPDATE_PERIOD` |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Very high latency (offline) | 30.4 s | 264 | 40 | 340 | 40 | 300 |
| Low latency | 1.04 s | 264 | 264 | 9 | 4 | 222 |
| Very low latency | 0.64 s | 264 | 264 | 6 | 2 | 222 |
| Ultra-low latency | 0.32 s | 264 | 264 | 3 | 1 | 222 |

Table values are the card's recommended NeMo configurations (**Reported**).[^nemotron-3-diar-card]

- The Transformers path exposes the same tradeoff as `streaming_mode`: `"low_latency"` 1.04 s (default), `"very_low_latency"` 0.64 s, `"ultra_low_latency"` 0.32 s, defined as chunk plus look-ahead audio before the model runs, excluding compute (**Reported**).[^nemotron-3-diar-card]

## Inference and usage

- NeMo-Speech.cpp native runtime: `nemo-speech diarize meeting.wav`, or word-level speaker tags via `nemo-speech transcribe meeting.wav --diarize --json`; further examples in the runtime's diarization CLI guide (**Reported**).[^nemotron-3-diar-card]
- NVIDIA NeMo Speech (Python 3.12+, Cython, recent PyTorch; `libsndfile1`, `ffmpeg`; `uv pip install Cython packaging` plus `nemo-toolkit[asr]`): load with `SortformerEncLabelModel.from_pretrained("nvidia/Nemotron-3-Diarization")` or `restore_from()` a `.nemo` file, call `.eval()`, set the five `sortformer_modules` streaming attributes, verify with `_check_streaming_parameters()`, then `diarize(audio=...)` returns `begin_seconds, end_seconds, speaker_index` segments and optionally activity-probability tensors via `include_tensor_outputs=True` (**Reported**).[^nemotron-3-diar-card]
- Accepted inputs: single file path, list of paths, numpy array(s) (requires explicit integer `sample_rate`, default 16000), or line-delimited JSON manifest with `audio_filepath`, `offset`, `duration` per line (**Reported**).[^nemotron-3-diar-card]
- Detailed DER evaluation uses `examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py` with flags for `chunk_len`, `fifo_len`, `chunk_right_context`, `spkcache_update_period`, plus `batch_size`, `collar`, `precision`, `compile_encoder`, `spkcache_len`; per-condition method detail is in the linked `diarization_evaluation.md` subcard, which was not present in `raw/` (**Reported**, with unavailable-link limit).[^nemotron-3-diar-card]
- Transformers (install from source): offline path runs `AutoProcessor` plus `AutoModelForAudioFrameClassification` to get `(1, num_frames, 8)` logits at one frame per 10 ms, then `processor.extract_speaker_dict`; streaming path sets `set_streaming_mode()`, feeds chunked processor outputs with `is_streaming` / `is_first_audio_chunk` / `is_last_audio_chunk`, threads `speaker_cache` between forwards, accounts `num_lookahead_frames` the model attends to but does not score, and concatenates per-chunk logits (**Reported**).[^nemotron-3-diar-card]
- Streaming-ASR integration is delegated to the linked `ASR_INTEGRATION_GUIDE.md`, which was not present in `raw/` (**Reported**, with unavailable-link limit).[^nemotron-3-diar-card]

## Training

- Initialized from a Transformer-based NEST SSL checkpoint [5]; trained on 8 nodes of 8× NVIDIA A100-SXM4-80GB GPUs in two stages: (1) offline training on simulated data only, (2) streaming fine-tuning on real conversations plus simulated mixtures, with the train scripts (`sortformer_diar_train.py`, `streaming_sortformer_diar_train.py`) and base configs (`sortformer_offline_8spk.yaml`, `sortformer_streaming_8spk.yaml`) linked in the NeMo Speech repository (**Reported**).[^nemotron-3-diar-card]

## Training and evaluation data

- Real conversations (~10,000 h): Fisher English 1+2, AMI (train/dev, force-aligned), ICSI, VoxConverse v0.3 (dev/test), AISHELL-4 (train), Third DIHARD (dev), 2000 NIST SRE CALLHOME Part 1, AliMeeting (train, force-aligned), DiPCo (dev), NOTSOFAR1 (train/dev, force-aligned), DISPLACE 2024 (dev/eval), DISPLACE-M 2026 (dev 1–3), David AI D2 Multispeaker (licensed, 3–4 speakers, 1,000 h), YODAS-v2 pseudo-labeled 5,000 h subset; languages span English, Mandarin, Hindi, Kannada, Telugu, Bengali, and other multilingual sources; voice recordings may constitute personal data (**Reported**).[^nemotron-3-diar-card]
- Single-speaker audio used for simulation (~28,000 h): LibriSpeech train-960h, AMI and AliMeeting individual headsets, Fisher English 1+2, David AI Chit Chat / Multispeaker / Podcast / Advice / Expert Assistant (all licensed), David AI D12 Human Transcripts (21 languages, licensed), MUSAN noises for augmentation (**Reported**).[^nemotron-3-diar-card]
- Simulated multi-talker mixtures (82,611 h total): Librispeech 6,694 h; AMI 6,743 h; AliMeeting 6,745 h; Fisher English 6,755 h; David AI English 36,458 h; David AI Multilingual 19,216 h (**Reported**).[^nemotron-3-diar-card]
- Evaluation: 901 condition-specific recordings of real multilingual conversational speech across telephone, meeting, near-field, far-field, and multi-microphone conditions — DIHARD III Eval (259; 1–9 speakers), CALLHOME-Part2 (250; 2–6 speakers), AliMeeting Test Near/Far (20 each; 2–4 speakers), AMI Test MHM/SDM (16 each; 3–4 speakers), NOTSOFAR1 Eval MHM/SC (160 each; 3–7 speakers); recordings may contain voice personal data (**Reported**).[^nemotron-3-diar-card]

## Evaluation protocol and baselines

- Metrics: diarization error rate (DER = false alarm + miss + confusion, overlap included; collar 0 s except 0.25 s on CALLHOME-Part2), speaker-counting accuracy (SCA, exact-match 1/0), counting MAE (magnitude-aware), and RTFx (audio duration / processing time); higher RTFx is faster, lower DER/MAE is better (**Reported**).[^nemotron-3-diar-card]
- Reference-label protocol: scores must use the exact published reference RTTMs in the card's `Labels` column; AMI, AliMeeting, and NOTSOFAR1 use forced-alignment references because original transcription-oriented segment annotations label within-segment silence as speech and would inflate missed-speech error; different references are a different protocol and not directly comparable (**Reported**).[^nemotron-3-diar-card]
- Baseline is `nvidia/diar_streaming_sortformer_4spk-v2.1` (4-speaker), evaluated at 30.4 s (`188/40/340/40/300`), 1.04 s (`188/188/6/7/144`), and 0.32 s (`188/188/3/1/144`) in the same `SPKCACHE_LEN/FIFO_LEN/CHUNK_LEN/RIGHT_CONTEXT/UPDATE_PERIOD` order (**Reported**).[^nemotron-3-diar-card]

## Benchmark results

Full-set DER (lower is better) from the NeMo `e2e_diarize_speech.py` runs; 0.64 s rows exist only for Nemotron 3 Diarization (**Reported**).[^nemotron-3-diar-card]

| Condition | Nemotron 30.4 s | Nemotron 1.04 s | Nemotron 0.64 s | Nemotron 0.32 s | Baseline 30.4 s | Baseline 0.32 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DIHARD III full | 12.73 | 13.18 | 13.28 | 13.55 | 19.09 | 19.85 |
| CALLHOME-Part2 full | 9.10 | 10.29 | 10.66 | 11.32 | 10.32 | 12.67 |
| AliMeeting Near | 6.40 | 6.59 | 6.74 | 7.19 | 11.57 | 13.68 |
| AliMeeting Far | 10.47 | 10.80 | 11.03 | 11.60 | 13.69 | 16.85 |
| AMI MHM | 9.25 | 9.48 | 9.62 | 10.05 | 15.81 | 17.77 |
| AMI SDM | 11.14 | 12.80 | 13.06 | 12.95 | 21.42 | 23.89 |
| NOTSOFAR1 MHM full | 6.77 | 7.70 | 7.99 | 8.65 | 21.77 | 23.37 |
| NOTSOFAR1 SC full | 11.00 | 12.77 | 13.35 | 14.53 | 30.49 | 32.95 |

- Largest gains are on many-speaker far-field audio: NOTSOFAR1 MHM full DER falls from 21.77 to 6.77 at 30.4 s (5–7-speaker split: 29.38 → 7.86) and NOTSOFAR1 SC from 30.49 to 11.00; DIHARD III 5–9-speaker DER falls from 40.21 to 27.58 at 30.4 s (**Reported**).[^nemotron-3-diar-card]
- Latency degradation is gradual: DIHARD III full DER moves 12.73 → 13.55 from 30.4 s to 0.32 s; CALLHOME full moves 9.10 → 11.32; NOTSOFAR1 SC moves 11.00 → 14.53 (**Reported**).[^nemotron-3-diar-card]
- Speaker-counting improves almost everywhere (e.g. NOTSOFAR1 MHM SCA 35.00 → 93.75 at 30.4 s; MAE 0.9375 → 0.0625; CALLHOME SCA 84.40 → 91.60), with two caveats: on AMI MHM/SDM Nemotron's SCA is 87.50 versus the baseline's 93.75 despite much lower DER, and on the CALLHOME 2-speaker split the baseline's 30.4 s DER (5.68) is slightly below Nemotron's (5.98) even though Nemotron wins the full set (9.10 vs 10.32) (**Reported**).[^nemotron-3-diar-card]

## Inference speed

- RTFx (audio duration / processing time; higher is faster) via NeMo/PyTorch with and without `torch.compile()`, BF16 on an NVIDIA Blackwell RTX PRO 5000; `batch_size=1` and `batch_size=32` eager/compiled pairs (**Reported**).[^nemotron-3-diar-card]

| Latency | Nemotron b=1 eager / compiled | Nemotron b=32 eager / compiled | Baseline b=1 eager / compiled | Baseline b=32 eager / compiled |
| --- | ---: | ---: | ---: | ---: |
| 30.4 s | 1340 / 4385 | 12196 / 15113 | 874 / 1468 | 3204 / 2619 |
| 1.04 s | 38 / 164 | 581 / 865 | 16 / 42 | 193 / 136 |
| 0.64 s | 25 / 113 | 391 / 579 | — | — |
| 0.32 s | 12.5 / 54 | 199 / 292 | 8 / 21 | 101 / 76 |

Table values are source-reported measurements (**Reported**).[^nemotron-3-diar-card]

## License, deployment, and ethics

- Governed by the OpenMDW License Agreement v1.1; deployment geography is global; intended for speaker diarization in live or recorded conversational audio (meetings, calls, podcasts, ASR pipelines needing speaker labels and timestamps); integration into systems needs use-case-specific testing following V-model unit/system validation (**Reported**).[^nemotron-3-diar-card]
- Supported stack: NeMo Framework v3.0 runtimes on NVIDIA GPU-accelerated systems (card lists Ampere, Ada Lovelace, Blackwell, Hopper families and DGX systems) on Linux (**Reported**).[^nemotron-3-diar-card]
- Ethical considerations defer to the `bias.md`, `explainability.md`, `safety.md`, and `privacy.md` subcards, which were not present in `raw/`; quality/risk/security reports go through the NVIDIA security reporting portal (**Reported**, with unavailable-link limit).[^nemotron-3-diar-card]

## Relationships

- Upstream of [Nemotron 3 Diarization GGUF](nemotron-3-diarization-gguf.md): the GGUF concept covers the audio.cpp format conversion (BF16/Q8_0 weights, CLI/server-batch usage, RTX 5090 C++/Python comparison, Q8_0 consistency caveats), while this concept covers the NVIDIA source checkpoint, its streaming configurations, training data, and DER/RTFx benchmarks; neither deprecates the other (**Synthesis**).[^nemotron-3-diar-card]
- Uses Streaming Sortformer behavior (AOSC speaker cache plus FIFO recent-frame context with arrival-time ordering) and Sortformer permutation resolution, per the card's streaming-inference description and references [1][2] (**Reported**).[^nemotron-3-diar-card]
- Compared against [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md): the 4-speaker 117M-parameter streaming baseline evaluated across all eight evaluation conditions and shared latency points; that concept covers the baseline checkpoint, its AOSC/FIFO latency profiles, and v2-vs-v2.1 DER tables, while this concept covers the newer 8-speaker checkpoint and its gains over that baseline (**Synthesis**).[^nemotron-3-diar-card]
- Preceded by [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md): the 123M-parameter offline 4-speaker Sortformer checkpoint whose card announces this 8-speaker model as its successor with greatly improved accuracy; the predecessor keeps its own DER/RTFx tables and CC-BY-NC-4.0 terms, while this concept covers the newer streaming/offline checkpoint (**Synthesis**).[^sortformer-4spk-card]

## Coverage and limits

- Source inspected statically only; no code executed, no audio loaded, and no DER, SCA/MAE, or RTFx figures reproduced (**Synthesis**).[^nemotron-3-diar-card]
- Linked local subcards (`diarization_evaluation.md`, `ASR_INTEGRATION_GUIDE.md`, `bias.md`, `explainability.md`, `safety.md`, `privacy.md`) were not present in `raw/` and were not inspected; linked external pages (Hugging Face blog, demo Space, NeMo and Transformers repositories and docs, arXiv references, OpenMDW license text) were not fetched; demo GIF/video assets were not viewed (**Synthesis**).[^nemotron-3-diar-card]
- All architecture, data-composition, benchmark, speed, compatibility, and licensing characterizations are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `vad` domain rule (**Synthesis**).[^nemotron-3-diar-card]

[^nemotron-3-diar-card]: [Nemotron 3 Diarization](../raw/Nemotron-3-Diarization.md) — locators: frontmatter (`license`, `pipeline_tag`, `library_name`, `tags`); sections `Description` (8-speaker scope, streaming/offline, Sortformer arrival ordering, AOSC/FIFO, 80 ms–30.4 s latency range, 10 ms output resolution, commercial-use statement), `Release Date` (2026-09-23), `Live Action Demo Page` (Space, GIF, 8-speaker video); `How to use` (NeMo-Speech.cpp `diarize`/`transcribe --diarize --json` fences, NeMo install fence, quick-start `chunk_len/chunk_right_context/fifo_len/spkcache_update_period` fence, load/restore fences, four input-format code blocks incl. manifest JSONL, streaming-parameter definitions plus latency formula note, 4-row recommended-config table, `Getting Diarization Results` fences, `e2e_diarize_speech.py` command, Transformers offline/streaming `<details>` blocks incl. `streaming_mode` latency table and `speaker_cache`/`num_lookahead_frames`/`is_last_audio_chunk` flow, ASR-guide link); `Model Architecture`, `Input`, `Output` (31-layer RoPE encoder, 8× stacking to 80 ms, Conv1D to 10 ms, 100M params, 16 kHz wav/flac/opus/mp3, unlimited chunked duration, `[T, 8]` tensor, arrival ordering, `["speaker1", 0.51, 12.62]` example); `Software Integration` (NeMo v3.0, Ampere/Ada/Blackwell/Hopper compat lists, Linux, V-model paragraph); `Model Version`, `Training and Evaluation Datasets` (10,000 h real-conversation table, 28,000 h single-speaker table, 82,611 h mixture list, 8-row evaluation table with splits and `Labels` column, personal-data notes); `Training` (NEST init, 8×8 A100-80GB, two stages, script/config links); `Performance Evaluation` (forced-alignment IMPORTANT callout, baseline 3-row config table, DER/SCA/MAE/RTFx metric definitions, eight per-condition result tables, RTFx table with RTX PRO 5000/BF16/compile conditions); `License/Terms of Use` (OpenMDW-1.1), `Deployment Geography` (Global), `Use Case`, `References` ([1]–[5]), `Ethical Considerations` (subcard links, security portal).

[^sortformer-4spk-card]: [Sortformer Diarizer 4spk v1](../raw/diar_sortformer_4spk-v1.md) — locators: announcement banner (Nemotron-3-Diarization 8-speaker successor link); `Model Architecture` (123M badge, NEST/Transformer description); `Licence` (CC-BY-NC-4.0).
