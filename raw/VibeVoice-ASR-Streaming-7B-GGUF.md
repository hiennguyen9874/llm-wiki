---
language:
- en
- zh
- es
- pt
- de
- ja
- ko
- fr
- ru
- it
license: mit
pipeline_tag: automatic-speech-recognition
tags:
- audio.cpp
- gguf
- asr
- streaming
- speaker-attributed-transcription
base_model: microsoft/VibeVoice-ASR-Streaming-7B
---

# VibeVoice ASR Streaming 7B GGUF for audio.cpp

This repository contains audio.cpp-native GGUF builds of
`microsoft/VibeVoice-ASR-Streaming-7B`.

## Use with audio.cpp

Install the recommended Q8_0 package through the audio.cpp model manager:

```bash
python3 tools/model_manager_v2.py install vibevoice_asr_streaming_7b_q8_0
```

Run offline ASR:

```bash
build/debug/bin/audiocpp_cli \
  --task asr \
  --family vibevoice_asr_streaming \
  --model models/VibeVoice-ASR-Streaming-7B-GGUF/vibevoice-asr-streaming-7b-q8_0.gguf \
  --backend cuda \
  --threads 8 \
  --audio input.wav \
  --text-out transcript.txt \
  --metrics \
  --log
```

Run the server with the model loaded:

```json
{
  "host": "127.0.0.1",
  "port": 8080,
  "backend": "cuda",
  "threads": 8,
  "models": [
    {
      "id": "vibevoice-streaming-7b",
      "family": "vibevoice_asr_streaming",
      "path": "models/VibeVoice-ASR-Streaming-7B-GGUF/vibevoice-asr-streaming-7b-q8_0.gguf",
      "task": "asr",
      "mode": "streaming"
    }
  ]
}
```

Then start the server:

```bash
build/debug/bin/audiocpp_server --config server.json --log
```

For live streaming, send 16 kHz mono signed 16-bit PCM to the live endpoint:

```bash
ffmpeg -hide_banner -loglevel error -i input.wav -f s16le -ac 1 -ar 16000 - \
  | curl -N -X POST \
      -H 'Content-Type: application/octet-stream' \
      -H 'Transfer-Encoding: chunked' \
      -H 'Expect:' \
      -T - \
      'http://127.0.0.1:8080/v1/audio/transcriptions/live?model=vibevoice-streaming-7b&sample_rate=16000&channels=1&sample_format=s16le'
```

## Files

| File | Format | Notes |
|---|---|---|
| `vibevoice-asr-streaming-7b-bf16.gguf` | BF16 | Highest precision package. |
| `vibevoice-asr-streaming-7b-q8_0.gguf` | Q8_0 | Recommended package for audio.cpp. |
| `vibevoice-asr-streaming-7b-q4_k.gguf` | Q4_K | Smaller lower-bit package. |

Each GGUF is self-contained and embeds the audio.cpp package spec and required
sidecars.

## Source and license

These GGUF files were converted from the upstream Hugging Face model:

- Upstream repository: https://huggingface.co/microsoft/VibeVoice-ASR-Streaming-7B
- Pinned upstream revision: `60d858b518b4e19d404af3737f848fc185b30177`
- Upstream license: MIT

The GGUF conversion preserves the upstream MIT license. See the upstream model
card and Microsoft VibeVoice repository for the original model documentation,
usage notes, and any responsible-use guidance.
