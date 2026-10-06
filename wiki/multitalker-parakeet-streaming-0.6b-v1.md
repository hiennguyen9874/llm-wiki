---
type: Concept
title: Multitalker Parakeet Streaming 0.6B v1
description: NVIDIA NeMo 0.6B-parameter streaming multitalker ASR model using speaker-kernel injection with one instance per speaker, fronted by streaming diarization, with published cpWER and single-speaker WER benchmarks.
tags: [stt, multitalker, streaming, diarization, speaker-tagging, fastconformer, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: multitalker-parakeet-card
    resource: ../raw/multitalker-parakeet-streaming-0.6b-v1.md
    kind: documentation
    title: Multitalker Parakeet Streaming 0.6B v1
---

Multitalker Parakeet Streaming 0.6B v1 (`nvidia/multitalker-parakeet-streaming-0.6b-v1`) is NVIDIA's streaming multitalker ASR model that transcribes fully overlapped speech by deploying one 600M-parameter FastConformer-Transformer instance per speaker, where each instance adapts to its target speaker through learnable speaker-kernel injection driven only by external diarization activity — no enrollment audio or speaker embeddings — and it preserves single-speaker ASR performance close to its [Nemotron speech streaming base](https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b) (**Reported**).[^multitalker-parakeet-card]

## Identity and release

- Model: Multitalker Parakeet Streaming 0.6B v1, Hugging Face model card with `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, tags `speaker-diarization`, `speech-recognition`, `multitalker-ASR`, `multispeaker-ASR`, `FastConformer`, `RNNT`, `Conformer`, `NEST`, `pytorch`, `NeMo`; research lineage is self-speaker adaptation via speaker targeting [1], Sortformer [2], Streaming Sortformer [3], NEST [4], FastConformer [5], Transformer [6], NeMo Framework [7], and the NeMo speech data simulator [8] (**Reported**).[^multitalker-parakeet-card]
- Base checkpoint: fine-tuned from Nemotron-Speech-Streaming (English 0.6B), so single-speaker ASR performance is preserved alongside the multitalker capability (**Reported**).[^multitalker-parakeet-card]
- License: NVIDIA Open Model License Agreement; frontmatter declares `other` / `nvidia-open-model-license` with the NVIDIA license URL (**Reported**).[^multitalker-parakeet-card]
- Voice-agent use: streaming multitalker transcription in the VAD → STT loop — diarization supplies per-speaker activity, one ASR instance per speaker produces speaker-tagged output in SegLST form (**Synthesis**).[^multitalker-parakeet-card]

## Architecture

- Speaker-kernel injection: learnable speaker kernels are injected into selected Fast-Conformer encoder layers (pre-encode layer), generated via speaker-supervision activations that detect each target speaker's speech activity, making encoder states responsive to the targeted speaker even during fully overlapped speech (**Reported**).[^multitalker-parakeet-card]
- Multi-instance decoding: one model instance is deployed per speaker; every instance receives the same mixed audio plus its speaker's diarization activity, injects that speaker's kernels, and emits that speaker's transcript independently and in parallel, which sidesteps the permutation problem of other multitalker approaches at the cost of one instance per speaker (**Reported**).[^multitalker-parakeet-card]
- Encoder: NeMo Encoder for Speech Tasks (NEST) based on FastConformer, in the Parakeet family (**Reported**).[^multitalker-parakeet-card]
- Key advantages claimed: no speaker enrollment (only diarization activity needed, unlike target-speaker ASR requiring pre-enrollment audio or embeddings); handles severe/fully overlapped speech with one focus per instance; streaming-capable with configurable latency–accuracy tradeoff; fine-tunable from strong single-speaker models with single-speaker performance preserved (**Reported**).[^multitalker-parakeet-card]

## Streaming configuration

- Latency is set by `att_context_size`, measured in 80 ms frames; the card's published benchmark latency is 1.12 s with 13+1 lookahead frames (**Reported**).[^multitalker-parakeet-card]

| `att_context_size` | Chunk size | Latency |
| --- | --- | --- |
| [70, 0] | 1 frame | 0.08 s |
| [70, 1] | 2 frames | 0.16 s |
| [70, 6] | 7 frames | 0.56 s |
| [70, 13] | 14 frames | 1.12 s |

Table values are the card's latency mapping (**Reported**).[^multitalker-parakeet-card]

## Inference and usage

- Runtime: NVIDIA NeMo (`apt-get install libsndfile1 ffmpeg`; `pip install Cython packaging`; `pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]`) (**Reported**).[^multitalker-parakeet-card]
- Method 1 (snippet): load a streaming Sortformer diarizer (`SortformerEncLabelModel.from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2.1")`) plus `ASRModel.from_pretrained("nvidia/multitalker-parakeet-streaming-0.6b-v1")`; configure via the `MultitalkerTranscriptionConfig` dataclass (`audio_file`, `output_path`, streaming diarization parameters); buffer audio with `CacheAwareStreamingAudioBuffer`; drive per-chunk inference with the `SpeakerTaggedASR` helper (`perform_parallel_streaming_stt_spk` over `streaming_buffer_iter`, honoring `pad_and_drop_preencoded` / `drop_extra_pre_encoded`); finalize with `generate_seglst_dicts_from_parallel_streaming` (**Reported**).[^multitalker-parakeet-card]
- Method 2 (example script): `examples/asr/asr_cache_aware_streaming/speech_to_text_multitalker_streaming_infer.py` with `asr_model` / `diar_model` `.nemo` paths, `att_context_size="[70,13]"`, `generate_realtime_scripts`, and `audio_file` (or `manifest_file` for batch mode, one JSON object per line with `audio_filepath`, `offset`, `duration` nullable on the NeMo main branch) (**Reported**).[^multitalker-parakeet-card]
- Single-speaker mode: set `cfg.single_speaker_mode=True` to reproduce the single-speaker benchmark figures below (**Reported**).[^multitalker-parakeet-card]
- Input: single-channel (mono) audio at 16,000 Hz (**Reported**).[^multitalker-parakeet-card]
- Output: speaker-tagged transcript in [SegLST](https://github.com/fgnt/meeteval?tab=readme-ov-file#segment-wise-long-form-speech-transcription-annotation-seglst) format at `output_path` (**Reported**).[^multitalker-parakeet-card]

## Training data

- Regime: large combination of real conversations and simulated audio mixtures, all with transcriptions and speaker labels in SegLST format; collection methods vary per dataset (phone calls, interviews, web videos, meeting recordings, audiobooks), with LDC/dataset pages as the authority (**Reported**).[^multitalker-parakeet-card]
- Real conversations: Granary (single speaker), Fisher English (LDC), LibriSpeech, AMI Corpus, NOTSOFAR, ICSI (**Reported**).[^multitalker-parakeet-card]
- Mixture simulation source: Librispeech (**Reported**).[^multitalker-parakeet-card]

## Benchmarks

- Multitalker protocol: all evaluations include overlapping speech; concatenated minimum-permutation WER (cpWER); diarization frontend is Streaming Sortformer v2; post-processing can be tuned on held-out splits; latency 1.12 s (**Reported**).[^multitalker-parakeet-card]

| Dataset | Speakers | Sessions | cpWER (Streaming Sortformer v2 frontend) |
| --- | --- | ---: | ---: |
| AMI IHM | 3–4 | 219 | 21.26 |
| AMI SDM | 3–4 | 40 | 37.44 |
| CH109 | 2 | 259 | 15.81 |
| Mixer 6 | 2 | 148 | 23.81 |

Table values are the card's multitalker cpWER table and evaluation-data specification (**Reported**).[^multitalker-parakeet-card]

- Diarization DER figures in this card's frontmatter `model-index` (speaker diarization with post-processing, 1.04 s input buffer): DIHARD III Eval 1–4spk 13.24, 5–9spk 42.56, full 18.91 (0.0 s overlap collar); CALLHOME-part2 2spk 6.57, 3spk 10.05, 4spk 12.44, 5spk 21.68, 6spk 28.74, full 10.7 (0.25 s collar); CHA-ES CH109 4.88 (0.25 s collar) (**Reported**).[^multitalker-parakeet-card]
- Single-speaker protocol: Hugging Face Open ASR Leaderboard datasets, single-speaker mode enabled (**Reported**).[^multitalker-parakeet-card]

| Model | Avg | AMI | Earnings | GigaSpeech | LS test-clean | LS test-other | SPGI | Tedlium | Voxpopuli |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Nemotron Speech Streaming 0.6B (base) | 7.16 | 11.58 | 12.48 | 11.45 | 2.31 | 4.75 | 2.62 | 4.50 | 7.57 |
| Multitalker Parakeet, single-speaker mode | 7.44 | 11.62 | 14.68 | 11.49 | 2.19 | 4.76 | 2.68 | 4.65 | 7.45 |

Table values are the card's single-speaker WER table; lower is better (**Reported**).[^multitalker-parakeet-card]

## Relationships

- Fine-tuned from [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md): that concept covers the English-only 0.6B cache-aware streaming base this model preserves in single-speaker mode; read both when tracing the 0.6B lineage from single-speaker to multitalker (**Synthesis**).[^multitalker-parakeet-card]
- Depends on [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md): the card's Method 1 snippet loads this 4-speaker streaming diarizer as the speech-activity frontend, and the multitalker cpWER figures are reported with a Streaming Sortformer frontend; the diarizer page keeps its own AOSC/FIFO mechanism, latency profiles, and DER tables (**Synthesis**).[^multitalker-parakeet-card]
- Uses [Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md): the card's Method 2 example command names the v2 `.nemo` diarizer checkpoint and the cpWER table names Streaming Sortformer v2 as the evaluated frontend; the v2 page covers the predecessor checkpoint with four latency profiles and NeMo-Speech.cpp/Riva paths (**Synthesis**).[^multitalker-parakeet-card]
- Speaker-attribution comparison: [VibeVoice-ASR-Streaming-1.5B](vibevoice-asr-streaming-1.5b.md) covers a unified streaming ASR model that jointly transcribes who said what with hotwords across 10 languages, while this concept covers a multi-instance architecture that needs an external diarizer and one instance per speaker; no shared checkpoint or codebase is asserted (**Synthesis**).[^multitalker-parakeet-card]

## Coverage and limits

- Source inspected statically only; no NeMo install, checkpoint download, audio transcription, streaming run, or cpWER/WER/DER figure was executed or reproduced (**Synthesis**).[^multitalker-parakeet-card]
- Embedded figures (`figures/speaker_injection.png`, `figures/multi_instance.png`), linked NeMo example script and config (`speech_to_text_multitalker_streaming_infer.py`, `multitalker_transcript_config.py`, `multispk_transcribe_utils`), Sortformer checkpoints, arXiv references [1]–[8], SegLST/meetval link, demo video, NVIDIA portal/Riva/NeMo docs, and Librispeech sample widget audio were not fetched; figure files are absent from `raw/` (**Synthesis**).[^multitalker-parakeet-card]
- All architecture, procedure, data-composition, benchmark, latency, compatibility, and licensing characterizations are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `stt`/`vad` domain rules (**Synthesis**).[^multitalker-parakeet-card]

[^multitalker-parakeet-card]: [Multitalker Parakeet Streaming 0.6B v1](../raw/multitalker-parakeet-streaming-0.6b-v1.md) — locators: frontmatter (`license`, `license_name`, `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, `datasets` list, `model-index` with 10 diarization DER results at 1.04 s input buffer length plus task/dataset/config/split/metric keys, widget Librispeech samples); intro (Nemotron-Speech-Streaming base link, diarization-outputs-only + no-enrollment + Wang et al. 2025 link, speaker-kernel + pre-encode + Fast-Conformer paragraphs, one-instance-per-speaker paragraph); `Video Demo` (YouTube link); `Key Advantages` (4 bullets); `Model Architecture` (`Speaker Kernel Injection` + `figures/speaker_injection.png` paragraph, `Multi-Instance Architecture` + `figures/multi_instance.png` paragraph with 4 per-instance bullets, NEST [4] + Fast-Conformer [5] links); `NVIDIA NeMo` (install fence); `How to Use` (multi-instance note, Method 1 fence with `SortformerEncLabelModel.from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2.1")` + `ASRModel.from_pretrained("nvidia/multitalker-parakeet-streaming-0.6b-v1")` + `MultitalkerTranscriptionConfig` + `CacheAwareStreamingAudioBuffer` + `SpeakerTaggedASR.perform_parallel_streaming_stt_spk` + `generate_seglst_dicts_from_parallel_streaming`, Method 2 `speech_to_text_multitalker_streaming_infer.py` commands with `asr_model/diar_model/att_context_size="[70,13]"/generate_realtime_scripts/audio_file/manifest_file` plus `audio_filepath/offset/duration` JSONL schema); `Setting up Streaming Configuration` (`att_context_size` 4-row 80 ms-frame table); `Input` (mono 16 kHz); `Output` (SegLST link); `Datasets` (SegLST paragraph, phone/interview/web-video/meeting/audiobook + LDC note, 6-item real list, Librispeech simulation line); `Evaluation: Multitalker ASR Performance` (cpWER table with Streaming Sortformer v2 row: AMI IHM 21.26 / AMI SDM 37.44 / CH109 15.81 / Mixer 6 23.81, spec table with speaker/session rows, overlap-included / collar 0 s vs 0.25 s / post-processing / 1.12 s + 13+1-lookahead notes); `Evaluation: Single-speaker Mode ASR Performance` (`cfg.single_speaker_mode=True` fence, 2-row 9-column WER table vs Nemotron base); `References` ([1]–[8]).
