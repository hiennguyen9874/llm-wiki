---
type: Concept
title: Parakeet Realtime EOU 120M v1
description: NVIDIA 120M-parameter cache-aware FastConformer-RNNT streaming English ASR model with <EOU> end-of-utterance detection, 80–160 ms ASR latency, and published Open ASR Leaderboard WER plus EOU latency tables.
tags: [stt, asr, streaming, endpointing, english, fastconformer, rnnt, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: parakeet-eou-card
    resource: ../raw/parakeet_realtime_eou_120m-v1.md
    kind: documentation
    title: Parakeet Realtime EOU 120M v1 model card
---

Parakeet Realtime EOU 120M v1 (`nvidia/parakeet_realtime_eou_120m-v1`) is NVIDIA's ~120M-parameter streaming English speech-recognition model that jointly performs end-of-utterance (EOU) detection by emitting an `<EOU>` token at the end of each utterance, targeting 80–160 ms ASR latency for voice-AI-agent pipelines via NeMo Voice Agent (**Reported**).[^parakeet-eou-card]

## Identity and lineage

- Hugging Face ID `nvidia/parakeet_realtime_eou_120m-v1`; model version `parakeet_realtime_eou_120m-v1`; English-only; output has no punctuation or capitalization; ready for commercial and non-commercial use (**Reported**).[^parakeet-eou-card]
- Frontmatter declares `library_name: nemo`, `language: [en]`, `metrics: [wer]`, tags `speech-recognition`, `FastConformer`, `end-of-utterance`, `voice agent`, and license `nvidia-open-model-license` (**Observed** by static inspection).[^parakeet-eou-card]
- License is the NVIDIA Open Model License Agreement; the card links the NeMo Voice Agent example tree, the NeMo toolkit repository, and the two architecture papers as references (**Reported**).[^parakeet-eou-card]

## Architecture and streaming

- Architecture type FastConformer-RNNT: cache-aware streaming FastConformer encoder with 17 layers and attention context `[70, 1]`, plus an RNNT decoder; 120M parameters total (**Reported**).[^parakeet-eou-card]
- Cache-aware (stateful) design reuses cached encoder context across streaming steps instead of recomputing overlapping buffers, which is what lets the model hold the 80–160 ms operating point (**Synthesis**).[^parakeet-eou-card]
- Input: single-channel 16 kHz audio waveform, at least 160 ms duration required; output: 1D text string with an optional `<EOU>` token (e.g. `what is your name<EOU>`); output may be empty when the input contains no speech (**Reported**).[^parakeet-eou-card]

## End-of-utterance detection

- EOU is signaled inline in the transcript stream: the model emits an `<EOU>` token at the end of each utterance, so a voice agent can use the ASR output directly for turn-taking without a separate endpointing component (**Reported**).[^parakeet-eou-card]
- EOU latency is evaluated on TTS-generated audio from DialogStudio with a 3-second silence appended to each sample; percentiles are P50 160 ms, P90 280 ms, P95 320 ms (**Reported**).[^parakeet-eou-card]
- The card warns actual EOU performance in real-world scenarios varies with acoustic environment, accents, and similar factors (**Reported**).[^parakeet-eou-card]

## Training and evaluation data

- Training data named: AMI, DialogStudio (commercially licensed task-oriented subset), Granary, Google Speech Commands, LibriTTS, and 10,000 hours from human-transcribed NeMo ASR Set 3.0 (LibriSpeech 960 hours, Fisher Corpus, National Speech Corpus Part 1, VCTK, Europarl-ASR, Multilingual LibriSpeech, Mozilla Common Voice v7.0) (**Reported**).[^parakeet-eou-card]
- Collection is Hybrid Human plus Synthetic (most audio human-recorded, some TTS-generated under commercial license); labeling is Hybrid Human plus Synthetic (some transcripts manual, some ASR-generated) (**Reported**).[^parakeet-eou-card]
- Evaluation sets named: Hugging Face Open ASR Leaderboard sets (AMI, Earnings22, Gigaspeech, LS-test-clean, LS-test-other, SPGI, Tedlium, Voxpopuli) plus the DialogStudio subset (**Reported**).[^parakeet-eou-card]

## Benchmarks

All numbers below are source assertions; nothing was executed or reproduced for this wiki (**Synthesis**).[^parakeet-eou-card]

- Word error rate in the 160 ms streaming setting on the Hugging Face Open ASR Leaderboard, text normalized with the leaderboard normalizer before scoring; average 9.30% (**Reported**):[^parakeet-eou-card]

| Avg | AMI | Earnings22 | Gigaspeech | LS-test-clean | LS-test-other | SPGI | TEDLIUM | VoxPopuli |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9.30 | 15.62 | 15.76 | 13.31 | 3.61 | 7.79 | 3.79 | 5.48 | 9.07 |

- EOU detection latency percentiles (TTS-generated DialogStudio audio plus appended silence): P50 160 ms, P90 280 ms, P95 320 ms (**Reported**).[^parakeet-eou-card]

## Inference and usage

- Streaming voice-agent path (primary design target): set `stt.type: nemo` and `stt.model: "nvidia/parakeet_realtime_eou_120m-v1"` in the NeMo Voice Agent server config YAML for ~80 ms ASR latency; full setup is in the NeMo Voice Agent example tree (**Reported**).[^parakeet-eou-card]
- Offline NeMo path: install recent PyTorch then `pip install -U nemo_toolkit['asr']`; `ASRModel.from_pretrained(model_name="nvidia/parakeet_realtime_eou_120m-v1")`, then `transcribe([...])`; the card demonstrates fetching a LibriSpeech sample (`2086-149220-0033.wav`) and printing `output[0].text` (**Reported**).[^parakeet-eou-card]
- Acceleration engine CUDA; test hardware V100, A100, A6000 (**Reported**).[^parakeet-eou-card]

## Deployment requirements

- Runtime engine NeMo 2.5.3+; supported microarchitectures Ampere, Blackwell, Hopper, Volta; preferred OS Linux (**Reported**).[^parakeet-eou-card]

## Limitations and trust notes

- Card-stated output limits: English only; no punctuation or capitalization; empty output when no speech is present; EOU latency figures come from synthetic TTS audio and real-world latency varies (**Reported**).[^parakeet-eou-card]
- Ethical framing is NVIDIA Trustworthy AI shared responsibility with developer-side fitness-for-use testing and a security-vulnerability reporting link (**Reported**).[^parakeet-eou-card]

## Relationships

- Contrasts with [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md): that concept covers the larger 0.6B cache-aware English streaming model with native punctuation and 80 ms–1.12 s chunk selection (6.93% average WER at 1.12 s); prefer this page for the lightweight 120M joint ASR-plus-EOU operating point and the 0.6B page for higher-accuracy punctuated streaming (**Synthesis**).[^parakeet-eou-card]
- Sibling of [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) and [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md): the 3.5 card names Parakeet Realtime EOU as a related model; this page is the English-only low-latency EOU specialist of that 0.6B streaming family (**Synthesis**).[^parakeet-eou-card]
- Compare turn-taking strategy with [Audio8 ASR Infinite](audio8-asr-infinite.md): Audio8 uses semantic VAD with configurable transcription delay and rolling KV cache for 24/7 operation, versus this page's inline `<EOU>`-token endpointing inside the RNNT transcript (**Synthesis**).[^parakeet-eou-card]
- Compare offline English accuracy with [Parakeet RNNT 0.6B](parakeet-rnnt-0.6b.md): the offline 0.6B RNNT is the higher-accuracy non-streaming counterpart in the same FastConformer-RNNT recipe family (**Synthesis**).[^parakeet-eou-card]

## Coverage and limits

- Source inspected statically only; no NeMo install, no checkpoint download, no audio transcribed, and no WER or EOU-latency figure reproduced (**Synthesis**).[^parakeet-eou-card]
- Referenced but unfetched and absent from `raw/`: `figure-streaming.png` streaming diagram, `voice-agent.png` pipeline diagram, NeMo Voice Agent example tree and server-config YAML, NeMo toolkit, the sample WAV, the Open ASR Leaderboard and its normalizer script, the DialogStudio subset, Granary and all other training/evaluation datasets, and references [1]–[3]; all install and inference fences are transcribed, not executed (**Synthesis**).[^parakeet-eou-card]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^parakeet-eou-card]

[^parakeet-eou-card]: [Parakeet Realtime EOU 120M v1 model card](../raw/parakeet_realtime_eou_120m-v1.md) — locators: frontmatter (`license_name: nvidia-open-model-license`, `language: [en]`, `metrics: [wer]`, `library_name: nemo`, `tags: speech-recognition / FastConformer / end-of-utterance / voice agent`); `Description` (streaming ASR plus EOU, 80–160 ms latency, `<EOU>` token, English-only, no punctuation/capitalization, voice-agent pipeline note, commercial-use line); `License/Terms of Use`; `Model Architecture` (FastConformer-RNNT, 17 encoder layers, attention context `[70,1]`, RNNT decoder, 120M params); `Input` (16 kHz mono waveform, ≥160 ms) / `Output` (`<EOU>` example, empty-on-nonspeech note); `References [1]–[3]`; `How to use` (NeMo Voice Agent `stt.type/model` YAML fence; `pip install -U nemo_toolkit['asr']`, `ASRModel.from_pretrained`, sample-WAV `wget` + `transcribe` fences); `Software Integration` (NeMo 2.5.3+, Ampere/Blackwell/Hopper/Volta, Linux); `Model Version(s)` (v1); `Training Dataset` (AMI / DialogStudio / Granary / Speech Commands / LibriTTS / 10k-hour ASR-Set-3.0 7-item list, Hybrid collection/labeling); `Evaluation Dataset` (8 Open-ASR-Leaderboard sets + DialogStudio, Hybrid collection/labeling); `Benchmark Score` (9-dataset WER table avg 9.30 incl. AMI 15.62 / Earnings22 15.76 / Gigaspeech 13.31 / LS-clean 3.61 / LS-other 7.79 / SPGI 3.79 / Tedlium 5.48 / VoxPopuli 9.07 with 160 ms + normalizer notes; EOU P50/P90/P95 160/280/320 ms with TTS-DialogStudio + 3 s-silence protocol and real-world-variance caveat); `Inference` (CUDA, V100/A100/A6000); `Ethical Considerations` (Trustworthy AI + vulnerability link).
