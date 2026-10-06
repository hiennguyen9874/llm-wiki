---
type: Concept
title: Streaming Sortformer Diarizer 4spk v2.1
description: NVIDIA NeMo streaming speaker-diarization model for up to four speakers with arrival-order channels, Arrival-Order Speaker Cache, configurable 1.04–30.4 s latency profiles, NeMo inference, and published DER benchmarks.
tags: [vad, diarization, speaker-tagging, streaming, sortformer, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T19:00:00Z }
stale_after: 2027-10-06
sources:
  - id: streaming-sortformer-card
    resource: ../raw/diar_streaming_sortformer_4spk-v2.1.md
    kind: documentation
    title: Streaming Sortformer Diarizer 4spk v2.1
---

Streaming Sortformer Diarizer 4spk v2.1 (`nvidia/diar_streaming_sortformer_4spk-v2.1`) is NVIDIA's streaming end-to-end neural speaker-diarization model for up to four speakers, resolving permutation by ordering output channels on speaker arrival time (Sortformer) and preserving identities across chunks with an Arrival-Order Speaker Cache (AOSC) plus FIFO queue (Streaming Sortformer), with a 117M-parameter NEST FastConformer plus Transformer stack, two recommended latency configurations (1.04 s and 30.4 s input buffer latency), NeMo `diarize()` inference, and DER benchmarks showing large meeting-corpus gains over v2; the card announces [Nemotron 3 Diarization](nemotron-3-diarization.md) as a newer 8-speaker release with greatly improved accuracy (**Reported**).[^streaming-sortformer-card]

## Identity and release

- Model: Streaming Sortformer Diarizer 4spk v2.1, Hugging Face model card with `library_name: nemo`, `pipeline_tag: automatic-speech-recognition`, tags `speaker-diarization`, `speaker-recognition`, `speech`, `audio`, `Transformer`, `FastConformer`, `Conformer`, `NEST`, `pytorch`, `NeMo`; research lineage is Sortformer [1], Streaming Sortformer with AOSC [2], NEST [3], FastConformer [4], Transformer [5], NeMo Framework [5/6], NeMo speech data simulator [7], and forced-alignment repurposing discussion [7/8] (**Reported**).[^streaming-sortformer-card]
- License: NVIDIA Open Model License Agreement; license frontmatter declares `other` / `nvidia-open-model-license` with the NVIDIA license URL (**Reported**).[^streaming-sortformer-card]
- Successor notice: the announcement banner points to [Nemotron-3-Diarization](https://huggingface.co/nvidia/nemotron-3-diarization), supporting 8 speakers with greatly improved accuracy; no deprecation or migration date for this 4-speaker checkpoint is stated (**Reported**).[^streaming-sortformer-card]
- Voice-agent use: the card states this model enables the NeMo Voice Agent to recognize speakers in conversations, linking the voice-agent example and its server YAML configuration (**Reported**).[^streaming-sortformer-card]

## Architecture and streaming mechanism

- Streaming mechanism: pre-encode layer in the Fast-Conformer generates the speaker cache; at each step the cache is filtered to retain only high-quality speaker-cache vectors; AOSC stores frame-level acoustic embeddings of previously observed speakers; output speaker channels follow arrival-time order of each speaker's speech segments (**Reported**).[^streaming-sortformer-card]
- Encoder stack: L-size (17-layer) NeMo Encoder for Speech Tasks (NEST) based on FastConformer, followed by an 18-layer Transformer encoder with hidden size 192 and two feedforward layers with 4 sigmoid outputs per input frame; model-size badge states 117M parameters; aside from speaker-cache management, the architecture follows the offline Sortformer (**Reported**).[^streaming-sortformer-card]
- Input: single-channel (mono) audio sampled at 16,000 Hz; each clip is an Ns × 1 matrix (e.g. 10 s at 16 kHz forms a 160,000 × 1 matrix) (**Reported**).[^streaming-sortformer-card]
- Output: T × S matrix with S = 4 maximum speakers and T frames including zero-padding at one frame per 0.08 s; each element is a speaker-activity probability in [0, 1] (e.g. a(150, 2) = 0.95 means 95% activity for the second speaker over [12.00, 12.08] s) (**Reported**).[^streaming-sortformer-card]

## Streaming configurations

- Streaming parameters are measured in 80 ms frames: `CHUNK_SIZE` (frames per processing chunk), `RIGHT_CONTEXT` (future frames after the chunk), `FIFO_SIZE` (previous frames from the FIFO queue), `UPDATE_PERIOD` (frames extracted from FIFO to update the speaker cache), `SPEAKER_CACHE_SIZE` (total frames in the speaker cache); NeMo attributes are `chunk_len`, `chunk_right_context`, `fifo_len`, `spkcache_update_period`, `spkcache_len`, verified with `_check_streaming_parameters()` (**Reported**).[^streaming-sortformer-card]
- Latency means input buffer latency = `CHUNK_SIZE` + `RIGHT_CONTEXT`, excluding compute time; Real-Time Factor (RTF) means processing time divided by audio duration, measured at batch size 1 on an NVIDIA RTX 6000 Ada Generation GPU (**Reported**).[^streaming-sortformer-card]

| Configuration | Latency | RTF | `CHUNK_SIZE` | `RIGHT_CONTEXT` | `FIFO_SIZE` | `UPDATE_PERIOD` | `SPEAKER_CACHE_SIZE` |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Very high latency | 30.4 s | 0.002 | 340 | 40 | 40 | 300 | 188 |
| Low latency | 1.04 s | 0.093 | 6 | 7 | 188 | 144 | 188 |

Table values are the card's recommended configurations (**Reported**).[^streaming-sortformer-card]

## Inference and usage

- Runtime: NVIDIA NeMo (`apt-get install libsndfile1 ffmpeg`; `pip install Cython packaging`; `pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]`); quick-start loads `SortformerEncLabelModel.from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2.1")`, calls `.eval()`, sets `chunk_len=340`, `chunk_right_context=40`, `fifo_len=40`, `spkcache_update_period=300`, then `diarize(audio=[...], batch_size=1)` (**Reported**).[^streaming-sortformer-card]
- Loading variants: `from_pretrained()` needs a Hugging Face token; `restore_from()` loads a downloaded `.nemo` file with `map_location='cuda', strict=False`; the card's loading example names the `v2` checkpoint string while the quick-start names `v2.1`, so the exact checkpoint string to reuse is the `v2.1` quick-start form (**Reported**, with version-string caveat as **Synthesis**).[^streaming-sortformer-card]
- Accepted inputs: a single audio path, a list of audio paths, numpy array(s) (requires explicit integer `sample_rate`, default 16000), or a JSONL manifest where each line carries `audio_filepath`, `offset`, and `duration` (nullable on the NeMo main branch) (**Reported**).[^streaming-sortformer-card]
- Diarization calls: `diarize(audio=audio_input, batch_size=1)` returns speaker-marked segments as `begin_seconds, end_seconds, speaker_index`; `diarize(..., include_tensor_outputs=True)` additionally returns speaker-activity probability tensors (**Reported**).[^streaming-sortformer-card]
- Evaluation path: `examples/speaker_tasks/diarization/neural_diarizer/e2e_diarize_speech.py` with `model_path`, `dataset_manifest`, `batch_size`, `spkcache_len`, `spkcache_update_period`, `fifo_len`, `chunk_len`, `chunk_right_context`; per-development-set optimized post-processing for the offline model is reproduced via YAML configs in `examples/speaker_tasks/diarization/conf/post_processing` (**Reported**).[^streaming-sortformer-card]

## Training and data

- Hardware and regime: trained on 8 nodes of 8× NVIDIA Tesla V100 GPUs with 90-second training samples and batch size 4; train script `sortformer_diar_train.py` and base config `sortformer_diarizer_hybrid_loss_4spk-v1.yaml` are linked (**Reported**).[^streaming-sortformer-card]
- Data scale: approximately 5,000 hours combining real conversations and simulated mixtures generated by the NeMo speech data simulator; all sets use RTTM labeling with a processed RTTM subset for training (**Reported**).[^streaming-sortformer-card]
- Real-conversation sets: Fisher English (LDC), AMI Meeting Corpus (IHM, lapel-mix, SDM with forced-alignment RTTMs), VoxConverse-v0.3, ICSI, AISHELL-4, Third DIHARD Challenge Development (LDC), 2000 NIST SRE split1 (LDC), DiPCo, AliMeeting (with forced-alignment RTTMs), NOTSOFAR1; collection methods vary (phone calls, interviews, web videos, audiobooks) with LDC/dataset pages as the authority (**Reported**).[^streaming-sortformer-card]
- Mixture-simulation sources: 2004–2010 NIST Speaker Recognition Evaluation (LDC) and Librispeech (**Reported**).[^streaming-sortformer-card]

## Technical limitations

- Streaming (online) operation; maximum 4 speakers with degraded performance on 5 or more speakers (**Reported**).[^streaming-sortformer-card]
- Designed for long-form audio of several hours, with possible degradation on very long recordings (**Reported**).[^streaming-sortformer-card]
- Trained primarily on public English speech: performance may degrade on non-English speech and on out-of-domain data such as noisy recordings (**Reported**).[^streaming-sortformer-card]

## Benchmarks

- Protocol: all evaluations include overlapping speech; collar tolerance is 0.25 s for CALLHOME-part2 and CH109 and 0.0 s for DIHARD III Eval, AliMeeting Test, AMI Test, and NOTSOFAR1 Eval; forced-alignment ground-truth RTTMs are used for AMI and AliMeeting; frontmatter `model-index` DER values are the 1.04 s-latency post-processed figures (**Reported**).[^streaming-sortformer-card]

| Dataset | Speakers | Sessions |
| --- | --- | ---: |
| DIHARD III Eval ≤4spk / ≥5spk / full | 1–4 / 5–9 / 1–9 | 219 / 40 / 259 |
| CALLHOME-part2 2/3/4/5/6spk / full | 2 / 3 / 4 / 5 / 6 / 2–6 | 148 / 74 / 20 / 5 / 3 / 250 |
| CHAES CH109 (2spk set) | 2 | 109 |
| AliMeeting Test (2–4spk) | 2–4 | 20 |
| AMI Test (3–4spk) | 3–4 | 16 |
| NOTSOFAR1 Eval SC ≤4spk / ≥5spk / full | 3–4 / 5–7 / 3–7 | 70 / 90 / 160 |

Table values are the card's evaluation-data specification (**Reported**).[^streaming-sortformer-card]

- Telephonic and general-purpose DER, 1.04 s latency (frontmatter `model-index` for v2.1): DIHARD III ≤4spk 15.09, ≥5spk 41.42, full 20.21; CALLHOME-part2 2spk 6.65, 3spk 11.25, 4spk 13.35, 5spk 22.12, 6spk 24.51, full 11.19; CH109 5.09 (**Reported**).[^streaming-sortformer-card]

| Model | Latency | DIHARD ≤4spk | DIHARD ≥5spk | DIHARD full | CALLHOME 2spk | CALLHOME 3spk | CALLHOME 4spk | CALLHOME 5spk | CALLHOME 6spk | CALLHOME full | CH109 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v2 | 30.4 s | 14.63 | 40.74 | 19.68 | 6.27 | 10.27 | 12.30 | 19.08 | 28.09 | 10.50 | 5.03 |
| **v2.1** | 30.4 s | 14.84 | 38.90 | 19.49 | 5.65 | 10.03 | 12.33 | 22.35 | 22.26 | 10.10 | 5.04 |
| v2 | 1.04 s | 14.49 | 42.22 | 19.85 | 7.51 | 11.45 | 13.75 | 23.22 | 29.22 | 11.89 | 5.37 |
| **v2.1** | 1.04 s | 15.09 | 41.42 | 20.21 | 6.65 | 11.25 | 13.35 | 22.12 | 24.51 | 11.19 | 5.09 |

Table values are the card's telephonic/general-purpose DER table; lower is better (**Reported**).[^streaming-sortformer-card]

| Model | Latency | AliMeeting near | AliMeeting far | AMI IHM | AMI SDM | NOTSOFAR SC ≤4spk | NOTSOFAR SC ≥5spk | NOTSOFAR full |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v2 | 30.4 s | 19.63 | 21.09 | 22.39 | 28.56 | 23.31 | 40.49 | 33.43 |
| **v2.1** | 30.4 s | 11.73 | 13.55 | 15.90 | 17.80 | 15.95 | 34.81 | 27.07 |
| v2 | 1.04 s | 19.98 | 22.09 | 25.11 | 31.34 | 24.41 | 41.55 | 34.52 |
| **v2.1** | 1.04 s | 12.60 | 15.60 | 16.67 | 20.57 | 17.26 | 36.76 | 28.75 |

Table values are the card's meeting-corpus DER table; v2.1 shows the largest gains here (e.g. AliMeeting-near 19.98 → 12.60 at 1.04 s; AMI SDM 31.34 → 20.57) while telephonic changes are mixed (**Reported**, with cross-table comparison as **Synthesis**).[^streaming-sortformer-card]

## Relationships

- Preceded by [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md): the 123M-parameter offline 4-speaker checkpoint whose architecture this streaming model follows aside from speaker-cache management; the offline page keeps its own DER/RTFx tables and CC-BY-NC-4.0 terms, while this concept covers the 117M-parameter streaming checkpoint with AOSC/FIFO and two latency profiles (**Synthesis**).[^streaming-sortformer-card]
- Updated from [Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md): the CC-BY-4.0 predecessor checkpoint with four latency profiles (0.32–30.4 s), 2,445 h real plus 5,150 h simulated training description, and NeMo-Speech.cpp GGUF plus Riva deployment paths; this v2.1 concept keeps the v2-vs-v2.1 DER comparison tables, with the largest v2.1 gains on meeting corpora (**Synthesis**).[^streaming-sortformer-card]
- Succeeded by [Nemotron 3 Diarization](nemotron-3-diarization.md): the newer checkpoint supporting up to eight speakers with greatly improved accuracy per this card's announcement banner, and which uses this v2.1 checkpoint as its published 4-speaker DER/RTFx baseline; neither page deprecates the other (**Synthesis**).[^streaming-sortformer-card]
- Used by [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md): the streaming multitalker ASR model whose Method 1 snippet loads this v2.1 checkpoint as its speech-activity frontend and reports multitalker cpWER with a Streaming Sortformer frontend; this page keeps the diarizer mechanism, latency profiles, and DER tables (**Synthesis**).[^streaming-sortformer-card]

## Coverage and limits

- Source inspected statically only; no NeMo install, inference, training, evaluation script, or DER/RTF figure was executed or reproduced (**Synthesis**).[^streaming-sortformer-card]
- Embedded figures (`sortformer_intro.png`, `aosc_3spk_example.gif`, `aosc_4spk_example.gif`, `streaming_steps.png`, `sortformer-v1-model.png`), linked NeMo scripts/configs/post-processing YAMLs, voice-agent example and YAML, arXiv references [1]–[8], LDC/dataset pages, Riva/NeMo docs, and successor Hugging Face page were not fetched; Librispeech sample widget audio was not played (**Synthesis**).[^streaming-sortformer-card]
- All architecture, data-composition, procedure, benchmark, speed, compatibility, and licensing characterizations are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `vad` domain rule (**Synthesis**).[^streaming-sortformer-card]

[^streaming-sortformer-card]: [Streaming Sortformer Diarizer 4spk v2.1](../raw/diar_streaming_sortformer_4spk-v2.1.md) — locators: frontmatter (`license`, `library_name`, `pipeline_tag`, `tags`, `datasets`, `model-index` with 17 DER results at 1.04 s input buffer length plus task/dataset/config/split/metric keys); announcement banner (Nemotron-3-Diarization 8-speaker link); intro (Sortformer [1] and Streaming Sortformer AOSC [2] paragraphs, NeMo Voice Agent paragraph with YAML link); `Model Architecture` (Fast-Conformer pre-encode speaker-cache paragraph, filtering sentence, 117M badge, NEST L-size 17-layer FastConformer basis, 18-layer 192-hidden Transformer, 2 feedforward layers with 4 sigmoid outputs, streaming paper [2] link); `NVIDIA NeMo` (install fence); `Quick Start` (`from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2.1")` + 340/40/40/300 fence); `How to Use` (loading `v2` vs quick-start `v2.1` fences, single-file / list / numpy + `sample_rate` / JSONL manifest `audio_filepath+offset+duration` blocks, `CHUNK_SIZE/RIGHT_CONTEXT/FIFO_SIZE/UPDATE_PERIOD/SPEAKER_CACHE_SIZE` definitions, 2-row latency/RTF table with RTX 6000 Ada note, latency and RTF definition bullets, `sortformer_modules` setter + `_check_streaming_parameters()` fence, `diarize` and `include_tensor_outputs` fences, `e2e_diarize_speech.py` command, `Input` 16 kHz mono Ns×1 paragraph with 160,000×1 example, `Output` T×S / S=4 / 0.08 s-frame / [0,1] paragraph with a(150,2) example); `Train and evaluate` (8×8 V100, 90 s samples, batch size 4, train script + `sortformer_diarizer_hybrid_loss_4spk-v1.yaml` links, post-processing folder link, `Technical Limitations` 4 bullets); `Datasets` (~5,000 h + NeMo simulator [7], RTTM note, 10-item real list with forced-alignment [8] notes, 2-item simulation list, phone/interview/web-video/audiobook + LDC note); `Performance` (spec table with speaker/session rows, overlap-included / collar 0.25 s vs 0.0 s / forced-alignment notes, telephonic and meeting DER tables with v2 vs v2.1 × 30.4 s vs 1.04 s rows); `References` ([1]–[7]); `Licence` (NVIDIA Open Model License). Referenced figure files have no locator available in `raw/` (files absent).
