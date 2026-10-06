---
type: Concept
title: VibeVoice-ASR-Streaming-7B GGUF
description: GGUF packaging of VibeVoice-ASR-Streaming-7B for audio.cpp with BF16, Q8_0, and Q4_K weights, offline CLI, server, and 16 kHz live-streaming usage.
tags: [stt, streaming, gguf, audio-cpp, speaker-attribution, hotwords]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T15:00:00Z }
stale_after: 2027-10-06
sources:
  - id: vibevoice-asr-streaming-7b-gguf-card
    resource: ../raw/VibeVoice-ASR-Streaming-7B-GGUF.md
    kind: documentation
    revision: 60d858b518b4e19d404af3737f848fc185b30177
    title: VibeVoice ASR Streaming 7B GGUF for audio.cpp
---

VibeVoice-ASR-Streaming-7B GGUF is an audio.cpp-native GGUF distribution of `microsoft/VibeVoice-ASR-Streaming-7B`, shipping self-contained BF16, Q8_0, and Q4_K packages with the Q8_0 build recommended for audio.cpp, plus documented model-manager install, offline CLI, server, and 16 kHz live-streaming paths (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]

## Package identity and provenance

- Card title is `VibeVoice ASR Streaming 7B GGUF for audio.cpp`; it contains audio.cpp-native GGUF builds of `microsoft/VibeVoice-ASR-Streaming-7B` (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, `license: mit`, `base_model: microsoft/VibeVoice-ASR-Streaming-7B`, 10 languages (`en`, `zh`, `es`, `pt`, `de`, `ja`, `ko`, `fr`, `ru`, `it`), and tags `audio.cpp`, `gguf`, `asr`, `streaming`, and `speaker-attributed-transcription` (**Observed** by static inspection).[^vibevoice-asr-streaming-7b-gguf-card]
- Upstream repository is `https://huggingface.co/microsoft/VibeVoice-ASR-Streaming-7B` at pinned revision `60d858b518b4e19d404af3737f848fc185b30177` under the MIT license; the GGUF conversion preserves the upstream MIT license and defers original model documentation and responsible-use guidance to the upstream model card and Microsoft VibeVoice repository (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]

## Files

- `vibevoice-asr-streaming-7b-bf16.gguf`: BF16 highest-precision package (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]
- `vibevoice-asr-streaming-7b-q8_0.gguf`: Q8_0 recommended package for audio.cpp (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]
- `vibevoice-asr-streaming-7b-q4_k.gguf`: smaller lower-bit Q4_K package (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]
- Each GGUF is self-contained and embeds the audio.cpp package spec and required sidecars (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]

## Usage

- Install the recommended Q8_0 package through the audio.cpp model manager: `python3 tools/model_manager_v2.py install vibevoice_asr_streaming_7b_q8_0` (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]
- Offline ASR via `build/debug/bin/audiocpp_cli` with `--task asr --family vibevoice_asr_streaming --model models/VibeVoice-ASR-Streaming-7B-GGUF/vibevoice-asr-streaming-7b-q8_0.gguf --backend cuda --threads 8 --audio input.wav --text-out transcript.txt --metrics --log` (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]
- Server mode uses a `server.json` with `host 127.0.0.1`, `port 8080`, `backend cuda`, `threads 8`, and one `models` entry (`id: vibevoice-streaming-7b`, `family: vibevoice_asr_streaming`, Q8_0 `path`, `task: asr`, `mode: streaming`), started with `build/debug/bin/audiocpp_server --config server.json --log` (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]
- Live streaming sends 16 kHz mono signed 16-bit PCM to `POST /v1/audio/transcriptions/live` with query `model=vibevoice-streaming-7b&sample_rate=16000&channels=1&sample_format=s16le`, exemplified by an `ffmpeg -f s16le -ac 1 -ar 16000` pipe into chunked-transfer `curl -N -X POST -T -` (**Reported**).[^vibevoice-asr-streaming-7b-gguf-card]

## Relationships

- Packaged deployment of the streaming-ASR family: [VibeVoice-ASR-Streaming-1.5B](vibevoice-asr-streaming-1.5b.md) covers the 1.5B unified streaming ASR model card (speaker-attributed transcription, hotwords, 10 languages, no deployment packaging), while this concept covers the audio.cpp GGUF distribution of the larger 7B checkpoint with install, CLI/server, and live-endpoint usage; no shared weight file is asserted (**Synthesis**).[^vibevoice-asr-streaming-7b-gguf-card]
- Sibling audio.cpp GGUF packaging: [VibeVoice-7B GGUF](vibevoice-7b-gguf.md) covers a Q8_0 GGUF of the VibeVoice-7B long-form multi-speaker TTS checkpoint for CLI/server/WebUI use, while this concept covers a streaming ASR checkpoint in BF16/Q8_0/Q4_K with offline plus live-streaming server paths; no shared weight file is asserted (**Synthesis**).[^vibevoice-asr-streaming-7b-gguf-card]
- Streaming ASR comparison: [Audio8 ASR Infinite](audio8-asr-infinite.md) covers a native streaming bilingual ASR model with selectable clock, transcription delay, rolling KV cache, and semantic VAD, while this concept documents GGUF deployment (quant choices, CLI/server/live endpoint) without a published clock, delay, cache, or accuracy figure; no shared architecture is asserted (**Synthesis**).[^vibevoice-asr-streaming-7b-gguf-card]

## Coverage and limits

- Source inspected statically only; no GGUF downloaded, no model-manager install, CLI, server, or ffmpeg/curl streaming run executed, and no accuracy, latency, or resource claim reproduced (**Synthesis**).[^vibevoice-asr-streaming-7b-gguf-card]
- Linked but unfetched and not in `raw/`: the upstream Hugging Face checkpoint at the pinned revision, all three `.gguf` weight files and embedded sidecars, the audio.cpp model manager/CLI/server/WebUI, and the upstream model card plus Microsoft VibeVoice repository guidance (**Synthesis**).[^vibevoice-asr-streaming-7b-gguf-card]
- No benchmark, WER, latency, RTF, VRAM, or quantization-quality figure is stated in this source, so none is compiled here; all packaging, command, endpoint, and licensing claims are source assertions without independent verification, and release figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^vibevoice-asr-streaming-7b-gguf-card]

[^vibevoice-asr-streaming-7b-gguf-card]: [VibeVoice ASR Streaming 7B GGUF for audio.cpp](../raw/VibeVoice-ASR-Streaming-7B-GGUF.md) — locators: frontmatter (`language`, `license`, `pipeline_tag`, `tags`, `base_model`); H1 title plus intro paragraph (audio.cpp-native GGUF builds of `microsoft/VibeVoice-ASR-Streaming-7B`); `Use with audio.cpp` section (model-manager `install vibevoice_asr_streaming_7b_q8_0` fence; offline `audiocpp_cli --task asr --family vibevoice_asr_streaming --model ...q8_0.gguf --backend cuda --threads 8 --audio --text-out --metrics --log` fence; `server.json` fence with `host`/`port`/`backend`/`threads`/`models[]` (`id`/`family`/`path`/`task`/`mode`) plus `audiocpp_server --config server.json --log` fence; live-streaming paragraph and `ffmpeg ... -f s16le -ac 1 -ar 16000` pipe to `curl -N -X POST ... /v1/audio/transcriptions/live?model=...&sample_rate=16000&channels=1&sample_format=s16le` fence); `Files` table (BF16 highest-precision / Q8_0 recommended / Q4_K smaller lower-bit rows; self-contained GGUF plus embedded package-spec/sidecars sentence); `Source and license` section (upstream `https://huggingface.co/microsoft/VibeVoice-ASR-Streaming-7B` link, pinned revision `60d858b518b4e19d404af3737f848fc185b30177`, upstream MIT license, preserved-MIT plus upstream-card/VibeVoice-repo pointer sentence).
