---
license: apache-2.0
language:
- zh
- en
- yue
- ja
- ko
library_name: gguf
tags:
- automatic-speech-recognition
- asr
- sensevoice
- funasr
- audio.cpp
- gguf
- ggml
- cpu
pipeline_tag: automatic-speech-recognition
---

# SenseVoiceSmall GGUF for audio.cpp

This repository contains a self-contained Q8_0 export of
[SenseVoiceSmall](https://huggingface.co/FunAudioLLM/SenseVoiceSmall) for the
[audio.cpp](https://github.com/0xShug0/audio.cpp) spec-backed runtime. The GGUF
embeds the `sense_asr` schema-v1 model specification, SenseVoice metadata,
SentencePiece vocabulary, CMVN tensors, and 919 model tensors. It loads
directly without `--model-spec-override`.

## File

| File | Size | SHA256 |
|---|---:|---|
| `sensevoice-small-q8-audiocpp-v1.gguf` | 254,211,200 bytes | `4dedf169f625437fb336f2959674f399819729a765e184128c0e25a6e16ff0ec` |

## Usage

```bash
audiocpp_cli --task asr --family sense_asr \
  --model sensevoice-small-q8-audiocpp-v1.gguf \
  --backend cpu --audio zh.wav \
  --request-option audio_chunk_mode=none
```

The integration is tracked in
[audio.cpp pull request #218](https://github.com/0xShug0/audio.cpp/pull/218).

## Reproducibility

The model was exported from `FunAudioLLM/SenseVoiceSmall` revision
`3847d57b6bdf2dd8875cb1508d2af43d80a16bf7` with the official
`runtime/llama.cpp/export_sensevoice_gguf.py` exporter using `--wtype q8_0`
and `--model-spec`.

On the official 5.616-second Mandarin sample, direct CPU inference produced:

```text
开饭时间早上9点至下午5点。
```

The text exactly matched the original Q8 model loaded with an external model
specification.

## Links

- [SenseVoice source and exporter](https://github.com/FunAudioLLM/SenseVoice/tree/main/runtime/llama.cpp)
- [FunASR](https://github.com/modelscope/FunASR)
- [FunASR industrial deployment guides](https://www.funasr.com/)
