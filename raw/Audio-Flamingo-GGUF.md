---
license: other
license_name: nvidia-oneway-noncommercial
license_link: https://huggingface.co/nvidia/audio-flamingo-next-hf/blob/5634886e2615c2f587dcf8b93c6edfe9907930ca/static/NVIDIA-OneWay-Noncommercial-License_22Mar2022-academic.docx
base_model:
  - nvidia/audio-flamingo-3-hf
  - nvidia/audio-flamingo-next-hf
tags:
  - audio.cpp
  - gguf
  - audio-text-to-text
  - automatic-speech-recognition
language:
  - en
---

# Audio Flamingo 3 and Next GGUF

For use with [audio.cpp](https://github.com/0xShug0/audio.cpp).

These self-contained GGUFs package the model tensors, tokenizer, configuration,
and audio.cpp model spec for Audio Flamingo 3 and Audio Flamingo Next. Both
models support transcription, captioning, and questions about speech, music,
and environmental sounds.

| File | Upstream checkpoint | Size | Maximum audio |
| --- | --- | ---: | ---: |
| `audio-flamingo-3-bf16.gguf` | [Audio Flamingo 3](https://huggingface.co/nvidia/audio-flamingo-3-hf) | 15.4 GiB | 10 minutes |
| `audio-flamingo-3-q8_0.gguf` | Audio Flamingo 3 | 8.7 GiB | 10 minutes |
| `audio-flamingo-3-q4_k.gguf` | Audio Flamingo 3 | 5.1 GiB | 10 minutes |
| `audio-flamingo-next-bf16.gguf` | [Audio Flamingo Next](https://huggingface.co/nvidia/audio-flamingo-next-hf) | 15.4 GiB | 30 minutes |
| `audio-flamingo-next-q8_0.gguf` | Audio Flamingo Next | 8.7 GiB | 30 minutes |
| `audio-flamingo-next-q4_k.gguf` | Audio Flamingo Next | 5.1 GiB | 30 minutes |

## Usage

```bash
audiocpp_cli --task asr --family audio_flamingo \
  --model /path/to/audio-flamingo-3-bf16.gguf --backend cuda \
  --audio input.wav \
  --request-option "instruct=Transcribe the input speech." \
  --text-out response.txt --log
```

Select either GGUF with `--model`. Use a question such as
`Describe the instruments and tempo.` for general audio understanding. Requested
timestamps or speaker descriptions are generated text, not structured alignment
or diarization results.

For server use, configure family `audio_flamingo`, task `asr`, and mode `offline`,
then submit audio to `/v1/audio/transcriptions` with the instruction in `prompt`.

## Correctness Reference

Official Python BF16 output is the reference. Correctness comparisons and
performance measurements are separate tests.

| Model | Runtime / weights | Result compared with official Python |
| --- | --- | --- |
| Audio Flamingo 3 | Official Python BF16 | Reference |
| Audio Flamingo 3 | audio.cpp BF16 | Exact transcription and music answer |
| Audio Flamingo 3 | audio.cpp Q8_0 | Exact transcription; coherent but different music answer |
| Audio Flamingo 3 | audio.cpp Q4_K | Same transcription words with different wrapper and punctuation; coherent but different music answer |
| Audio Flamingo Next | Official Python BF16 | Reference |
| Audio Flamingo Next | audio.cpp BF16 | Exact short transcription; matching words and line boundaries on the three-minute test after timestamps were removed |
| Audio Flamingo Next | audio.cpp Q8_0 | Same short transcription words with one comma omitted |
| Audio Flamingo Next | audio.cpp Q4_K | Exact short transcription |

Audio Flamingo Next generates timestamps as text rather than structured
alignment. Its BF16 three-minute response used the same words and line boundaries
as Python after timestamps were removed, but the generated timestamps drifted.

## CUDA Performance and Quantization

The following results use an RTX 5090 and the same decoded 10-second, 16-kHz
mono speech input. Python uses the official Transformers BF16 model with SDPA.
audio.cpp uses the CUDA backend and 8 CPU threads. Wall time and RTF are from
the second request in an already-loaded session. Peak VRAM covers the complete
process and was sampled every 100 ms.

| Model | Runtime / weights | Warm wall time | RTF | Peak VRAM |
| --- | --- | ---: | ---: | ---: |
| Audio Flamingo 3 | Official Python BF16 | 292.4 ms | 0.0292 | 16,766 MiB |
| Audio Flamingo 3 | audio.cpp BF16 | 283.3 ms | 0.0283 | 16,854 MiB |
| Audio Flamingo 3 | audio.cpp Q8_0 | 184.9 ms | 0.0185 | 9,956 MiB |
| Audio Flamingo 3 | audio.cpp Q4_K | 151.7 ms | 0.0152 | 6,280 MiB |
| Audio Flamingo Next | Official Python BF16 | 249.0 ms | 0.0249 | 16,784 MiB |
| Audio Flamingo Next | audio.cpp BF16 | 246.3 ms | 0.0246 | 16,890 MiB |
| Audio Flamingo Next | audio.cpp Q8_0 | 160.9 ms | 0.0161 | 9,992 MiB |
| Audio Flamingo Next | audio.cpp Q4_K | 129.9 ms | 0.0130 | 6,314 MiB |

Quantized outputs remained coherent on the transcription and music-understanding
requests. Q4_K is the default package and offers the lowest tested VRAM. Q8_0 is
the higher-precision quantized alternative. Quantization can change wording,
punctuation, or factual details in open-ended answers and should not be treated
as exact parity with BF16.

## Audio Preprocessing

For comparisons with Python, supply the same decoded 16-kHz mono WAV to both
implementations. Python's optional TorchCodec loader and librosa fallback use
different downmixing and resampling paths. audio.cpp averages channels and uses
SOXR when resampling is needed.

Both checkpoints use the NVIDIA OneWay Noncommercial License. The upstream
license is included in this directory. Review its terms before use or redistribution.

See the [audio.cpp model documentation](https://github.com/0xShug0/audio.cpp/blob/main/docs/models/audio_flamingo.md)
for request options, conversion, and additional usage details.
