---
type: Concept
title: Streaming Sortformer Diarizer 4spk v2
description: NVIDIA NeMo streaming speaker-diarization model for up to four speakers with arrival-order channels, Arrival-Order Speaker Cache, configurable 0.32–30.4 s latency profiles, NeMo and NeMo-Speech.cpp inference, and published DER benchmarks.
tags: [vad, diarization, speaker-tagging, streaming, sortformer, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T19:00:00Z }
stale_after: 2027-10-06
sources:
  - id: streaming-sortformer-v2-card
    resource: ../raw/diar_streaming_sortformer_4spk-v2.md
    kind: documentation
    title: Streaming Sortformer Diarizer 4spk v2
---

Streaming Sortformer Diarizer 4spk v2 (`nvidia/diar_streaming_sortformer_4spk-v2`) is NVIDIA's streaming end-to-end neural speaker-diarization model for up to four speakers, resolving permutation by ordering output channels on speaker arrival time (Sortformer) and preserving identities across chunks with an Arrival-Order Speaker Cache (AOSC) plus FIFO queue (Streaming Sortformer), with a 117M-parameter NEST FastConformer plus Transformer stack, four recommended latency configurations (0.32–30.4 s input buffer latency), NeMo `diarize()` and NeMo-Speech.cpp GGUF inference, and DER benchmarks with and without post-processing; the card announces [Nemotron 3 Diarization](nemotron-3-diarization.md) as a newer 8-speaker release with greatly improved accuracy (**Reported**).[^streaming-sortformer-v2-card]

## Identity and release

- Model: Streaming Sortformer Diarizer 4spk v2, Hugging Face model card with `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, tags `speaker-diarization`, `speaker-recognition`, `speech`, `audio`, `Transformer`, `FastConformer`, `Conformer`, `NEST`, `pytorch`, `NeMo`; research lineage is Sortformer [1], Streaming Sortformer with AOSC [2], NEST [3], FastConformer [4], Transformer [5], NeMo Framework [6], and NeMo speech data simulator [7] (**Reported**).[^streaming-sortformer-v2-card]
- License: CC-BY-4.0; downloading the public release accepts its terms (**Reported**).[^streaming-sortformer-v2-card]
- Successor notice: the announcement banner points to [Nemotron-3-Diarization](https://huggingface.co/nvidia/nemotron-3-diarization), supporting 8 speakers with greatly improved accuracy; no deprecation or migration date for this 4-speaker checkpoint is stated (**Reported**).[^streaming-sortformer-v2-card]
- Voice-agent use: the card states this model enables the NeMo Voice Agent to recognize speakers in conversations, linking the voice-agent example and its server YAML configuration (**Reported**).[^streaming-sortformer-v2-card]

## Architecture and streaming mechanism

- Streaming mechanism: pre-encode layer in the Fast-Conformer generates the speaker cache; at each step the cache is filtered to retain only high-quality speaker-cache vectors; AOSC stores frame-level acoustic embeddings of previously observed speakers; output speaker channels follow arrival-time order of each speaker's speech segments (**Reported**).[^streaming-sortformer-v2-card]
- Encoder stack: L-size (17-layer) NeMo Encoder for Speech Tasks (NEST) based on FastConformer, followed by an 18-layer Transformer encoder with hidden size 192 and two feedforward layers with 4 sigmoid outputs per input frame; model-size badge states 117M parameters; aside from speaker-cache management, the architecture follows the offline Sortformer (**Reported**).[^streaming-sortformer-v2-card]
- Input: single-channel (mono) audio sampled at 16,000 Hz; each clip is an Ns × 1 matrix (e.g. 10 s at 16 kHz forms a 160,000 × 1 matrix) (**Reported**).[^streaming-sortformer-v2-card]
- Output: T × S matrix with S = 4 maximum speakers and T frames including zero-padding at one frame per 0.08 s; each element is a speaker-activity probability in [0, 1] (e.g. a(150, 2) = 0.95 means 95% activity for the second speaker over [12.00, 12.08] s) (**Reported**).[^streaming-sortformer-v2-card]

## Streaming configurations

- Streaming parameters are measured in 80 ms frames: `CHUNK_SIZE` (frames per processing chunk), `RIGHT_CONTEXT` (future frames after the chunk), `FIFO_SIZE` (previous frames from the FIFO queue), `UPDATE_PERIOD` (frames extracted from FIFO to update the speaker cache), `SPEAKER_CACHE_SIZE` (total frames in the speaker cache); NeMo attributes are `chunk_len`, `chunk_right_context`, `fifo_len`, `spkcache_update_period`, `spkcache_len`, verified with `_check_streaming_parameters()` (**Reported**).[^streaming-sortformer-v2-card]
- Latency means input buffer latency = `CHUNK_SIZE` + `RIGHT_CONTEXT`, excluding compute time; Real-Time Factor (RTF) means processing time divided by audio duration, measured at batch size 1 on an NVIDIA RTX 6000 Ada Generation GPU (**Reported**).[^streaming-sortformer-v2-card]

| Configuration | Latency | RTF | `CHUNK_SIZE` | `RIGHT_CONTEXT` | `FIFO_SIZE` | `UPDATE_PERIOD` | `SPEAKER_CACHE_SIZE` |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Very high latency | 30.4 s | 0.002 | 340 | 40 | 40 | 300 | 188 |
| High latency | 10.0 s | 0.005 | 124 | 1 | 124 | 124 | 188 |
| Low latency | 1.04 s | 0.093 | 6 | 7 | 188 | 144 | 188 |
| Ultra low latency | 0.32 s | 0.180 | 3 | 1 | 188 | 144 | 188 |

Table values are the card's recommended configurations; the 10.0 s and 0.32 s rows have no counterpart in the v2.1 card's two-row table (**Reported**, with cross-card comparison as **Synthesis**).[^streaming-sortformer-v2-card]

## Inference and usage

- Runtime: NVIDIA NeMo (`apt-get install libsndfile1 ffmpeg`; `pip install Cython packaging`; `pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]`); quick-start loads `SortformerEncLabelModel.from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2")`, calls `.eval()`, sets `chunk_len=340`, `chunk_right_context=40`, `fifo_len=40`, `spkcache_update_period=300`, then `diarize(audio=[...], batch_size=1)` (**Reported**).[^streaming-sortformer-v2-card]
- NeMo-Speech.cpp native runtime: `hf download nvidia/diar_streaming_sortformer_4spk-v2 diar_streaming_sortformer_4spk-v2.q8_0.gguf --local-dir models`, then `nemo-speech diarize meeting.wav --model models/diar_streaming_sortformer_4spk-v2.q8_0.gguf`, or word-level speaker tags via `nemo-speech transcribe meeting.wav --model models/asr-model.gguf --diar-model models/diar_streaming_sortformer_4spk-v2.q8_0.gguf --json`; further examples in the runtime's diarization CLI guide (**Reported**).[^streaming-sortformer-v2-card]
- NeMo checkpoint use: the model is available as a pre-trained checkpoint for inference or fine-tuning; `from_pretrained()` needs a Hugging Face token (no token value is given), and `restore_from()` loads a downloaded `.nemo` file with `map_location='cuda', strict=False` (**Reported**).[^streaming-sortformer-v2-card]
- Accepted inputs: a single audio path, a list of audio paths, numpy array(s) (requires explicit integer `sample_rate`, default 16000), or a JSONL manifest where each line carries `audio_filepath`, `offset`, and `duration` (nullable on the NeMo main branch) (**Reported**).[^streaming-sortformer-v2-card]
- Diarization calls: `diarize(audio=audio_input, batch_size=1)` returns speaker-marked segments as `begin_seconds, end_seconds, speaker_index`; `diarize(..., include_tensor_outputs=True)` additionally returns speaker-activity probability tensors (**Reported**).[^streaming-sortformer-v2-card]
- Evaluation path: `examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py` with `model_path`, `dataset_manifest`, `batch_size`, `spkcache_len`, `spkcache_update_period`, `fifo_len`, `chunk_len`, `chunk_right_context`; per-development-set optimized post-processing is reproduced via YAML configs in `examples/speaker_tasks/diarization/conf/post_processing` (**Reported**).[^streaming-sortformer-v2-card]

## Training and data

- Hardware and regime: trained on 8 nodes of 8× NVIDIA Tesla V100 GPUs with 90-second training samples and batch size 4; train script `sortformer_diar_train.py` and base config `sortformer_diarizer_hybrid_loss_4spk-v1.yaml` are linked (**Reported**).[^streaming-sortformer-v2-card]
- Data scale: a combination of 2,445 hours of real conversations and 5,150 hours of simulated audio mixtures generated by the NeMo speech data simulator; all sets use RTTM labeling with a processed RTTM subset for training (**Reported**).[^streaming-sortformer-v2-card]
- Real-conversation sets: Fisher English (LDC), AMI Meeting Corpus, VoxConverse-v0.3, ICSI, AISHELL-4, Third DIHARD Challenge Development (LDC), 2000 NIST Speaker Recognition Evaluation split1 (LDC), DiPCo, AliMeeting; collection methods vary (phone calls, interviews, web videos, audiobooks) with LDC/dataset pages as the authority (**Reported**).[^streaming-sortformer-v2-card]
- Mixture-simulation sources: 2004–2010 NIST Speaker Recognition Evaluation (LDC) and Librispeech (**Reported**).[^streaming-sortformer-v2-card]

## Technical limitations

- Streaming (online) operation; maximum 4 speakers with degraded performance on 5 or more speakers (**Reported**).[^streaming-sortformer-v2-card]
- Designed for long-form audio of several hours, with possible degradation on very long recordings (**Reported**).[^streaming-sortformer-v2-card]
- Trained primarily on public English speech: performance may degrade on non-English speech and on out-of-domain data such as noisy recordings (**Reported**).[^streaming-sortformer-v2-card]

## Benchmarks

- Protocol: all evaluations include overlapping speech; collar tolerance is 0 s for DIHARD III Eval and 0.25 s for CALLHOME-part2 and CH109; post-processing (PP) is optimized on two held-out splits — DIHARD III Dev YAML for DIHARD III Eval and CALLHOME-part1 YAML for CALLHOME-part2 and CH109 (**Reported**).[^streaming-sortformer-v2-card]
- Frontmatter `model-index` DER values are the 1.04 s-latency post-processed figures: DIHARD III ≤4spk 13.24, ≥5spk 42.56, full 18.91; CALLHOME-part2 2spk 6.57, 3spk 10.05, 4spk 12.44, 5spk 21.68, 6spk 28.74, full 10.70; CH109 4.88 (**Reported**).[^streaming-sortformer-v2-card]

| Dataset | Speakers | Sessions |
| --- | --- | ---: |
| DIHARD III Eval ≤4spk / ≥5spk / full | 1–4 / 5–9 / 1–9 | 219 / 40 / 259 |
| CALLHOME-part2 2/3/4/5/6spk / full | 2 / 3 / 4 / 5 / 6 / 2–6 | 148 / 74 / 20 / 5 / 3 / 250 |
| CH109 | 2 | 109 |

Table values are the card's evaluation-data specification (**Reported**).[^streaming-sortformer-v2-card]

| Latency | PP | DIHARD ≤4spk | DIHARD ≥5spk | DIHARD full | CALLHOME 2spk | CALLHOME 3spk | CALLHOME 4spk | CALLHOME 5spk | CALLHOME 6spk | CALLHOME full | CH109 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 30.4 s | no | 14.63 | 40.74 | 19.68 | 6.27 | 10.27 | 12.30 | 19.08 | 28.09 | 10.50 | 5.03 |
| 30.4 s | yes | 13.45 | 41.40 | 18.85 | 5.34 | 9.22 | 11.29 | 18.84 | 27.29 | 9.54 | 4.61 |
| 10.0 s | no | 14.90 | 41.06 | 19.96 | 6.96 | 11.05 | 12.93 | 20.47 | 28.10 | 11.21 | 5.28 |
| 10.0 s | yes | 13.75 | 41.41 | 19.10 | 6.05 | 9.88 | 11.72 | 19.66 | 27.37 | 10.15 | 4.80 |
| 1.04 s | no | 14.49 | 42.22 | 19.85 | 7.51 | 11.45 | 13.75 | 23.22 | 29.22 | 11.89 | 5.37 |
| 1.04 s | yes | 13.24 | 42.56 | 18.91 | 6.57 | 10.05 | 12.44 | 21.68 | 28.74 | 10.70 | 4.88 |
| 0.32 s | no | 14.64 | 43.47 | 20.19 | 8.63 | 12.91 | 16.19 | 29.40 | 30.60 | 13.57 | 6.46 |
| 0.32 s | yes | 13.44 | 43.73 | 19.28 | 6.91 | 10.45 | 13.70 | 27.04 | 28.58 | 11.38 | 5.27 |

Table values are the card's DER table; lower is better (**Reported**).[^streaming-sortformer-v2-card]

## Deployment

- NVIDIA Riva: streaming Sortformer is deployed via Riva ASR speech recognition with speaker diarization; the card describes Riva as an accelerated speech AI SDK deployable on-prem, in clouds, hybrid, edge, and embedded, with out-of-the-box accuracy, run-time word boosting, acoustic/language-model/ITN customization, streaming recognition, Kubernetes scaling, and enterprise support, linking the supported-models list and live demo (**Reported**).[^streaming-sortformer-v2-card]

## Relationships

- Preceded by [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md): the 123M-parameter offline 4-speaker checkpoint whose architecture this streaming model follows aside from speaker-cache management; the offline page keeps its own DER/RTFx tables and CC-BY-NC-4.0 terms, while this concept covers the 117M-parameter streaming checkpoint with AOSC/FIFO and four latency profiles (**Synthesis**).[^streaming-sortformer-v2-card]
- Succeeded by [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md): the follow-on streaming checkpoint that keeps the same AOSC/FIFO architecture but changes the license to the NVIDIA Open Model License, restates training as approximately 5,000 hours, adds NOTSOFAR1/AliMeeting/AMI evaluation, and publishes v2-vs-v2.1 DER comparison tables showing the largest gains on meeting corpora; neither page deprecates the other (**Synthesis**).[^streaming-sortformer-v2-card]
- Succeeded by [Nemotron 3 Diarization](nemotron-3-diarization.md): the newer checkpoint supporting up to eight speakers with greatly improved accuracy per this card's announcement banner; neither page deprecates the other (**Synthesis**).[^streaming-sortformer-v2-card]
- Used by [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md): the streaming multitalker ASR model whose Method 2 example names the v2 `.nemo` diarizer checkpoint and whose cpWER table names Streaming Sortformer v2 as the evaluated frontend; this page keeps the v2 checkpoint's own latency profiles, DER tables, and deployment paths (**Synthesis**).[^streaming-sortformer-v2-card]

## Coverage and limits

- Source inspected statically only; no NeMo install, NeMo-Speech.cpp run, inference, training, evaluation script, or DER/RTF figure was executed or reproduced (**Synthesis**).[^streaming-sortformer-v2-card]
- Embedded figures (`sortformer_intro.png`, `aosc_3spk_example.gif`, `aosc_4spk_example.gif`, `streaming_steps.png`, `sortformer-v1-model.png`), linked NeMo scripts/configs/post-processing YAMLs, voice-agent example and YAML, NeMo-Speech.cpp runtime and CLI guide, arXiv references [1]–[7], LDC/dataset pages, Riva/NeMo docs, and successor Hugging Face page were not fetched; Librispeech sample widget audio was not played (**Synthesis**).[^streaming-sortformer-v2-card]
- All architecture, data-composition, procedure, benchmark, speed, compatibility, and licensing characterizations are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `vad` domain rule (**Synthesis**).[^streaming-sortformer-v2-card]

[^streaming-sortformer-v2-card]: [Streaming Sortformer Diarizer 4spk v2](../raw/diar_streaming_sortformer_4spk-v2.md) — locators: frontmatter (`license`, `library_name`, `pipeline_tag`, `tags`, `datasets`, `model-index` with 10 DER results at 1.04 s input buffer length plus task/dataset/config/split/metric keys); announcement banner (Nemotron-3-Diarization 8-speaker link); intro (Sortformer [1] and Streaming Sortformer AOSC [2] paragraphs, NeMo Voice Agent paragraph with YAML link); `Model Architecture` (Fast-Conformer pre-encode speaker-cache paragraph, filtering sentence, 117M badge, NEST L-size 17-layer FastConformer basis, 18-layer 192-hidden Transformer, 2 feedforward layers with 4 sigmoid outputs, streaming paper [2] link); `NVIDIA NeMo` (install fence); `Quick Start` (`from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2")` + 340/40/40/300 fence); `How to Use` (NeMo-Speech.cpp `hf download` + `diarize` + `transcribe --diar-model --json` fences with CLI-guide link, NeMo Framework paragraph, `from_pretrained` (Hugging Face token note) / `restore_from` / `eval` fence, single-file / list / numpy + `sample_rate` / JSONL manifest `audio_filepath+offset+duration` blocks, `CHUNK_SIZE/RIGHT_CONTEXT/FIFO_SIZE/UPDATE_PERIOD/SPEAKER_CACHE_SIZE` definitions, 4-row latency/RTF table with RTX 6000 Ada note, latency and RTF definition bullets, `sortformer_modules` setter + `_check_streaming_parameters()` fence, `diarize` and `include_tensor_outputs` fences, `e2e_diarize_speech.py` command, `Input` 16 kHz mono Ns×1 paragraph with 160,000×1 example, `Output` T×S / S=4 / 0.08 s-frame / [0,1] paragraph with a(150,2) example); `Train and evaluate` (8×8 V100, 90 s samples, batch size 4, train script + `sortformer_diarizer_hybrid_loss_4spk-v1.yaml` links, post-processing folder link, `Technical Limitations` 4 bullets); `Datasets` (2445 h real + 5150 h simulated via NeMo simulator [7], RTTM note, 9-item real list, 2-item simulation list, phone/interview/web-video/audiobook + LDC note); `Performance` (spec table with speaker/session rows, overlap-included / collar 0 s vs 0.25 s / DIHARD-dev and CALLHOME-part1 YAML notes, 8-row DER table with 30.4 s / 10.0 s / 1.04 s / 0.32 s × PP-no/PP-yes rows); `NVIDIA Riva: Deployment` (Riva ASR diarization link, capability bullets, model-list/demo links); `References` ([1]–[7]); `Licence` (CC-BY-4.0). Referenced figure files have no locator available in `raw/` (files absent).
