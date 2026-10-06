---
type: Concept
title: MOSS-Audio family
description: Open-source 4B/8B audio-understanding family with dedicated 12.5 Hz encoder, DeepStack injection and time-aware tokens, reporting leading open-source ASR, timestamp-ASR and speech-captioning figures with SGLang serving.
tags: [stt, asr, audio-understanding, timestamp-asr, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: moss-audio-card
    resource: ../raw/MOSS-Audio-4B-Instruct.md
    kind: documentation
    title: MOSS-Audio model card and README (4B/8B Instruct and Thinking)
---

MOSS-Audio is an open-source audio-understanding family from MOSI.AI, the OpenMOSS team, and Shanghai Innovation Institute, released 2026.4.13 with four checkpoints (4B/8B Instruct for direct instruction following and 4B/8B Thinking for chain-of-thought reasoning), built as MOSS-Audio-Encoder (12.5 Hz, trained from scratch) plus adapter plus Qwen3 LLM with DeepStack cross-layer injection and time-marker pretraining, covering speech transcription, word/sentence timestamp ASR, speaker/emotion/event analysis, scene and sound-cue extraction, music understanding, audio QA/summarization, and multi-hop reasoning, with vendor-reported leads on open-source general-audio understanding, 11/13 speech-captioning dimensions, overall ASR CER 11.30, and timestamp AAS 35.77 (zh) / 131.61 (en), served via local `infer.py`, Gradio, and an SGLang branch (**Reported**).[^moss-audio-card]

## Model identity and lineage

- Family table lists `MOSS-Audio-4B-Instruct`, `MOSS-Audio-4B-Thinking`, `MOSS-Audio-8B-Instruct`, and `MOSS-Audio-8B-Thinking`, each pairing `MOSS-Audio-Encoder` with a Qwen3 backbone (4B or 8B) at ~4.6B / ~8.6B total size, with Hugging Face links under `OpenMOSS-Team` (**Reported**).[^moss-audio-card]
- Creators are MOSI.AI, the OpenMOSS team, and Shanghai Innovation Institute; news dates the release to 2026.4.13 with blog and paper marked coming soon (**Reported**).[^moss-audio-card]
- Raw frontmatter declares `license: apache-2.0`, `language: [en, zh]`, tags `audio/speech/music/understanding/multimodal/instruct`, and `pipeline_tag: audio-text-to-text` (**Observed** by static inspection).[^moss-audio-card]
- Models are Apache-2.0 licensed; citation is `mossaudio2026` (OpenMOSS Team, 2026, GitHub repository URL) (**Reported**).[^moss-audio-card]

## Architecture

- Modular three-part design: raw audio is encoded by `MOSS-Audio-Encoder` into continuous temporal representations at 12.5 Hz, projected through a modality adapter into the LLM embedding space, then consumed by the LLM for autoregressive text generation; the encoder is trained from scratch rather than reusing an off-the-shelf frontend for claimed robustness, tighter temporal alignment, and cross-domain extensibility (**Reported**).[^moss-audio-card]
- DeepStack cross-layer injection: besides the encoder final-layer output, earlier and intermediate layer features are selected, independently projected, and injected into the language model's early layers to preserve multi-granularity detail (rhythm, timbre, transients, background structure) that a single top-layer representation loses (**Reported**).[^moss-audio-card]
- Time-aware representation: explicit time tokens are inserted between audio frame representations at fixed intervals during pretraining so the model learns "what happened when" for timestamp ASR, event localization, time-based QA, and long-audio retrospection (**Reported**).[^moss-audio-card]
- Architecture and capability figures (`arc.png`, `moss-audio-image.png`, `speech_caption_radar.png`) are linked images not present in `raw/`; architecture detail here comes from prose only (**Observed**, with image limit **Synthesis**).[^moss-audio-card]

## Capabilities

- Speech and content understanding with clean structured outputs plus word- and sentence-level timestamp alignment (**Reported**).[^moss-audio-card]
- Speaker, emotion, and event analysis from tone, timbre, and context, including speaker characteristics and key acoustic events (**Reported**).[^moss-audio-card]
- Scene and sound-cue extraction from background sounds, environmental noise, music, and non-speech signals to infer scene context and atmosphere (**Reported**).[^moss-audio-card]
- Music understanding (style, emotional progression, instrumentation, salient acoustic features) is claimed as part of general-audio coverage; it is peripheral to the VAD → STT → LLM → TTS loop and compiled here only as a capability headline, not a selection criterion (**Reported**, with scoping **Synthesis**).[^moss-audio-card]
- Audio QA and summarization over speech, podcasts, meetings, interviews, and environmental recordings; time-aware QA including word/sentence timestamp ASR; complex multi-hop reasoning via chain-of-thought training and reinforcement learning (Thinking variants) (**Reported**).[^moss-audio-card]

## Benchmark highlights

All figures below are vendor-reported tables from the card; nothing was executed or reproduced (**Synthesis**).[^moss-audio-card]

- General audio understanding accuracy (higher is better) on MMAU / MMAU-Pro / MMAR / MMSU: 8B-Thinking averages 71.08 in-table (77.33 / 64.92 / 66.53 / 75.52) against the card text headline of 70.80 for the same checkpoint (see [Contradictions](#contradictions)); other family rows are 4B-Thinking 68.37, 8B-Instruct 66.32, 4B-Instruct 64.04, ahead of listed open baselines MiMo-Audio-7B 62.97, Kimi-Audio 61.14, Qwen2.5-Omni-7B 58.96, Audio Flamingo 3 57.73, MiniCPM-o-4.5 56.83, Qwen3-Omni-30B 67.91, Step-Audio-R1.1 66.48, and Step-Audio-R1 70.67, but below closed Gemini-3-Pro 77.86 and Gemini-3.1-Pro 79.89 (**Reported**).[^moss-audio-card]
- Speech captioning LLM-as-judge (higher is better, 13 dimensions plus average): 8B-Instruct averages 3.7252 and 4B-Instruct 3.7105, ahead of Qwen3-Omni-30B-Instruct 3.5986, Qwen3-Omni-30B-Thinking 3.5667, Gemini-3-Pro 3.3763, and Gemini-3.1-Pro 3.5986 in-table; the card claims Instruct variants lead 11/13 fine-grained dimensions (**Reported**).[^moss-audio-card]
- ASR on a 12-dimension suite (overall CER, lower is better): 8B-Instruct 11.30 is the lowest overall in the card table, followed by Qwen3-Omni-30B-Instruct 11.39 and 4B-Instruct 11.58, against Fun-ASR-Nano 12.04, SenseVoice-Small 14.50, Kimi-Audio-7B-Instruct 14.12, Qwen2.5-Omni-3B 15.26 / 7B 15.05, Paraformer-Large 15.77, and GLM-ASR-Nano 17.29; vendor-called strengths are health-condition (8B 19.18), dialect (8B 8.76), singing (8B 9.81), non-speech vocalizations (4B 4.01 best in column), and code-switching (4B 10.11 best, 8B 10.18); the card also ships a 21-column per-dataset detail table (AISHELL-1/2, THCHS-30, MAGICDATA, AISHELL6-Whisper, AliMeeting, AISHELL-4, SeniorTalk, ChildMandarin, AISHELL-6A/6B, WenetSpeech, Fleurs, CS-Dialogue, TALCS, ASCEND, KeSpeech, WSYue, MIR-1K, openc-pop, MNV_17) summarized here, not cell-compiled (**Reported**, with omission **Synthesis**).[^moss-audio-card]
- Timestamp ASR AAS (lower is better): 8B-Instruct 35.77 on AISHELL-1 (zh) and 131.61 on LibriSpeech (en), versus 4B-Instruct 76.96 / 358.13, Qwen3-Omni-30B-Instruct 833.66 / 646.95, and Gemini-3.1-Pro 708.24 / 871.19 (**Reported**).[^moss-audio-card]

## Inference and serving

- Recommended environment is Python 3.12 in a clean conda env with `ffmpeg=7` from conda-forge and `pip install --extra-index-url https://download.pytorch.org/whl/cu128 -e ".[torch-runtime]"` after cloning `https://github.com/OpenMOSS/MOSS-Audio.git`; FlashAttention 2 GPUs use `-e ".[torch-runtime,flash-attn]"` (**Reported**).[^moss-audio-card]
- Basic usage downloads weights via `huggingface-cli download OpenMOSS-Team/MOSS-Audio --local-dir ./weights/MOSS-Audio` and `huggingface-cli download OpenMOSS-Team/MOSS-Audio-Instruct --local-dir ./weights/MOSS-Audio-Instruct` (second ID does not match any of the four table rows; treat as a card inconsistency), then edits `MODEL_PATH` / `AUDIO_PATH` in `infer.py` and runs `python infer.py`; default prompt is `Describe this audio`, editable for transcription, QA, or captioning (**Reported**, with inconsistency flagged as **Synthesis**).[^moss-audio-card]
- Gradio demo starts with `python app.py` (**Reported**).[^moss-audio-card]
- SGLang serving follows `moss_audio_usage_guide.md` (not in `raw/`): clone `https://github.com/OpenMOSS/sglang.git` on branch `moss-audio`, `pip install -e "python[all]"`, pin `nvidia-cudnn-cu12==9.16.0.29` under the default `torch==2.9.1+cu128` runtime, then `sglang serve --model-path ./weights/MOSS-Audio --trust-remote-code` (**Reported**).[^moss-audio-card]

## Relationships

- Qwen3-backbone comparison: [Qwen3-ASR family](qwen3-asr-family.md) is built on the Qwen3-Omni foundation with 0.6B/1.7B offline/streaming ASR and vLLM serving; MOSS-Audio instead pairs a dedicated 12.5 Hz encoder with Qwen3-4B/8B for joint transcription plus audio understanding and timestamp QA — cross-read both when choosing between a transcription-focused ASR checkpoint and a general audio-understanding checkpoint (**Synthesis**).[^moss-audio-card]
- Open-source audio-understanding baseline: [Audio Flamingo 3 and Next GGUF](audio-flamingo-3-and-next-gguf.md) packages the Audio Flamingo 3 baseline that appears in this card's general-understanding table (57.73 avg); read both when comparing audio.cpp-deployable understanding checkpoints against this card's 64.04–71.08 family band (**Synthesis**).[^moss-audio-card]
- ASR-baseline neighbors: [Fun-ASR-Nano-2512](fun-asr-nano-2512.md) and [GLM-ASR-Nano-2512](glm-asr-nano-2512.md) appear as named rows in this card's 12-dimension ASR table; cross-read them for compact Chinese-oriented ASR alternatives to this family's 11.30–11.58 overall-CER band (**Synthesis**).[^moss-audio-card]
- Open-source large baseline: [Step-Audio-R1.1](step-audio-r1-1.md) is the realtime-dialogue upgrade of the Step-Audio-R1 baseline in this card's general-understanding table (R1 70.67, R1.1 66.48); read both when weighing dialogue serving against understanding accuracy (**Synthesis**).[^moss-audio-card]
- OpenMOSS sibling: [MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)](moss-transcribe-cpp-gguf.md) covers the joint transcription-plus-diarization-plus-timestamp OpenMOSS checkpoint for CPU GGUF deployment, while this concept covers the 4B/8B general audio-understanding family with captioning, scene/sound cues, and timestamp QA; no shared checkpoint is asserted (**Synthesis**).[^moss-audio-card]
- Serving runtime: [SGLang-Omni](sglang-omni.md) is the multi-stage GPU serving runtime for omni/speech/TTS/ASR models; this card's SGLang path uses a dedicated `moss-audio` fork branch plus cuDNN pin rather than the generic SGLang-Omni flow — check both before serving (**Synthesis**).[^moss-audio-card]

## Contradictions

- **8B-Thinking general-audio average:** the Evaluation prose claims 70.80 average accuracy outperforming all open-source models, while the table row for the same checkpoint averages 71.08 from its four printed cells; neither value is chosen here (**Reported**).[^moss-audio-card]
- **Speech-captioning duplicate row:** the in-table Gemini-3.1-Pro row (4.436 / 3.936 / … / 3.5986) is cell-identical to the Qwen3-Omni-30B-A3B-Instruct row, so treat that baseline comparison as a card copy artifact (**Observed**).[^moss-audio-card]

## Coverage and limits

- Source inspected statically only; no environment created, no package installed, no model downloaded, no audio transcribed or captioned, and no accuracy, CER, AAS, or latency figure reproduced (**Synthesis**).[^moss-audio-card]
- Linked but unfetched and absent from `raw/`: all `./assets/` images (logo, `moss-audio-image.png`, `arc.png`, `speech_caption_radar.png`, `wechat.jpg`), `moss_audio_usage_guide.md`, `infer.py`, `app.py`, `./weights/` contents, the four Hugging Face model pages plus the collection page, the `OpenMOSS/sglang` `moss-audio` branch, the `OpenMOSS/MOSS-Audio` GitHub repository, MOSI.AI / OpenMOSS sites, Discord/X/WeChat links, and the pending blog plus arXiv paper; install, download, inference, and serve fences are transcribed, not executed (**Synthesis**).[^moss-audio-card]
- Material gaps: language coverage beyond frontmatter `en/zh` is unstated; per-language ASR detail beyond the summarized 21-column table, training data and compute, long-audio limits, streaming behavior, VRAM/latency, and timestamp-AAS protocol are not in the card; `MOSS-Audio-Instruct` download ID matches no released-model row; all identity, architecture, capability, and benchmark claims are source assertions, and model-release plus benchmark details carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^moss-audio-card]

[^moss-audio-card]: [MOSS-Audio model card and README](../raw/MOSS-Audio-4B-Instruct.md) — locators: frontmatter (`license`, `language`, `tags`, `pipeline_tag`); header (MOSI.AI / OpenMOSS / Shanghai Innovation Institute credit, unified speech/sound/music/captioning/time-aware/reasoning claim, four-model Instruct-vs-Thinking sentence); `News` (2026.4.13 release, blog/paper coming soon); `Introduction` (seven capability bullets incl. word/sentence timestamps, speaker/emotion/event, scene/sound cues, music style/progression/instrumentation, QA/summarization, time-aware QA, CoT+RL reasoning); `Model Architecture` (encoder plus adapter plus LLM, 12.5 Hz, from-scratch encoder claim; `DeepStack Cross-Layer Feature Injection` and `Time-Aware Representation` subsections with time-token insertion); `Released Models` (4-row table: Qwen3-4B/8B backbones, ~4.6B/~8.6B sizes, HF links); `Evaluation` (70.80 prose headline; general-understanding 16-row table with 71.08 in-table 8B-Thinking avg; speech-captioning radar plus 6-row 14-column table with 3.7252 8B-Instruct avg and 11/13 claim; ASR 10-row 13-column CER table with 11.30 8B-Instruct overall plus health/dialect/singing/non-speech/code-switch strengths; 21-column detail table; timestamp-AAS 4-row table with 35.77/131.61 8B-Instruct cells); `Quickstart` (`conda create -n moss-audio python=3.12`, `ffmpeg=7`, `pip install -e ".[torch-runtime]"` cu128 and `flash-attn` variant, `huggingface-cli download` pair, `MODEL_PATH`/`AUDIO_PATH` plus `Describe this audio` in `infer.py`, `python app.py`, `moss_audio_usage_guide.md` plus `moss-audio` SGLang branch with `nvidia-cudnn-cu12==9.16.0.29` and `torch==2.9.1+cu128` pins); `More Information`, `LICENSE` (Apache-2.0), `Citation` (`mossaudio2026` bibtex).
