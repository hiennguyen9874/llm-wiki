---
type: Concept
title: SenseVoiceSmall GGUF
description: Self-contained Q8_0 GGUF packaging of SenseVoiceSmall for the audio.cpp sense_asr runtime with embedded model spec, file identity, CPU CLI usage, and a Mandarin transcription parity check.
tags: [stt, asr, speech-recognition, gguf, audio-cpp, cpu]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: sensevoice-small-gguf-card
    resource: ../raw/SenseVoiceSmall-GGUF-audiocpp.md
    kind: documentation
    title: SenseVoiceSmall GGUF for audio.cpp
---

SenseVoiceSmall GGUF is a self-contained Q8_0 export of SenseVoiceSmall for the audio.cpp spec-backed runtime, embedding the `sense_asr` schema-v1 model specification so it loads directly without `--model-spec-override`, with a single-file identity, CPU CLI usage, and a reported exact-match Mandarin transcription against the original Q8 model (**Reported**).[^sensevoice-small-gguf-card]

## Package identity and components

- Card title is `SenseVoiceSmall GGUF for audio.cpp`; upstream model is [SenseVoiceSmall](https://huggingface.co/FunAudioLLM/SenseVoiceSmall) and runtime target is [audio.cpp](https://github.com/0xShug0/audio.cpp) (**Reported**).[^sensevoice-small-gguf-card]
- Frontmatter declares `license: apache-2.0`, `language: [zh, en, yue, ja, ko]`, `library_name: gguf`, `pipeline_tag: automatic-speech-recognition`, and tags including `automatic-speech-recognition`, `asr`, `sensevoice`, `funasr`, `audio.cpp`, `gguf`, `ggml`, and `cpu` (**Observed** by static inspection).[^sensevoice-small-gguf-card]
- The GGUF embeds the `sense_asr` schema-v1 model specification, SenseVoice metadata, SentencePiece vocabulary, CMVN tensors, and 919 model tensors (**Reported**).[^sensevoice-small-gguf-card]
- The audio.cpp integration is tracked in [audio.cpp pull request #218](https://github.com/0xShug0/audio.cpp/pull/218) (**Reported**).[^sensevoice-small-gguf-card]

## File

- `sensevoice-small-q8-audiocpp-v1.gguf`: 254,211,200 bytes, SHA256 `4dedf169f625437fb336f2959674f399819729a765e184128c0e25a6e16ff0ec` (**Reported**).[^sensevoice-small-gguf-card]

## Usage

- Run ASR on CPU with `audiocpp_cli --task asr --family sense_asr --model sensevoice-small-q8-audiocpp-v1.gguf --backend cpu --audio zh.wav --request-option audio_chunk_mode=none` (**Reported**).[^sensevoice-small-gguf-card]

## Export reproducibility and parity check

- Export source is `FunAudioLLM/SenseVoiceSmall` revision `3847d57b6bdf2dd8875cb1508d2af43d80a16bf7`, using the official `runtime/llama.cpp/export_sensevoice_gguf.py` exporter with `--wtype q8_0` and `--model-spec` (**Reported**).[^sensevoice-small-gguf-card]
- On the official 5.616-second Mandarin sample, direct CPU inference produced `开饭时间早上9点至下午5点。`, reported as an exact match to the original Q8 model loaded with an external model specification (**Reported**).[^sensevoice-small-gguf-card]

## Relationships

- Uses [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md): both are FunASR/SenseVoice-ecosystem GGUF packages for C++ CPU/edge runtimes, but this concept targets the audio.cpp `sense_asr` runtime while Fun-ASR-Nano GGUF targets the zero-Python FunASR llama.cpp runtime with a SenseVoice SAN-M encoder plus Qwen3-0.6B decoder (**Synthesis**).[^sensevoice-small-gguf-card]

## Coverage and limits

- Source inspected statically only; no GGUF downloaded, no CLI executed, and no transcription reproduced (**Synthesis**).[^sensevoice-small-gguf-card]
- Linked but unfetched and not in `raw/`: the `sensevoice-small-q8-audiocpp-v1.gguf` weight file, `zh.wav` and the official 5.616-second Mandarin sample, the upstream `FunAudioLLM/SenseVoiceSmall` checkpoint and `runtime/llama.cpp/export_sensevoice_gguf.py` exporter, audio.cpp PR #218, and the SenseVoice, FunASR, and funasr.com links (**Synthesis**).[^sensevoice-small-gguf-card]
- All file-identity, embedding, usage, export-revision, and transcription-match claims are source assertions without independent verification in this wiki; model-release and parity figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^sensevoice-small-gguf-card]

[^sensevoice-small-gguf-card]: [SenseVoiceSmall GGUF for audio.cpp](../raw/SenseVoiceSmall-GGUF-audiocpp.md) — locators: frontmatter (`license`, `language`, `library_name`, `tags`, `pipeline_tag`); intro paragraph (self-contained Q8_0 export, `sense_asr` schema-v1 embedding, SenseVoice metadata, SentencePiece vocabulary, CMVN tensors, 919 tensors, no `--model-spec-override` note); section `File` (file name, 254,211,200-byte size, SHA256 `4dedf169…ff0ec`); section `Usage` (`audiocpp_cli --task asr --family sense_asr --model … --backend cpu --audio zh.wav --request-option audio_chunk_mode=none` fence); usage paragraph (audio.cpp PR #218 link); section `Reproducibility` (source revision `3847d57b…16bf7`, `runtime/llama.cpp/export_sensevoice_gguf.py` with `--wtype q8_0` and `--model-spec`, 5.616-second Mandarin sample, `开饭时间早上9点至下午5点。` output, exact-match sentence); section `Links` (SenseVoice source/exporter, FunASR, funasr.com deployment-guide links).
