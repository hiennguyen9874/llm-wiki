---
license: mit
base_model: vibevoice/VibeVoice-7B
library_name: audio.cpp
tags:
  - audio.cpp
  - gguf
  - text-to-speech
  - multi-speaker
  - long-form
---

# VibeVoice 7B GGUF for audio.cpp

GGUF conversion of [vibevoice/VibeVoice-7B](https://huggingface.co/vibevoice/VibeVoice-7B) for [audio.cpp](https://github.com/0xShug0/audio.cpp).

Upstream model: [vibevoice/VibeVoice-7B](https://huggingface.co/vibevoice/VibeVoice-7B)

## Files

- `vibevoice-7b-q8_0.gguf`: Q8_0 GGUF package for VibeVoice 7B.
- `LICENSE`: MIT license from the upstream VibeVoice project.

## Usage

Use the GGUF directly with audio.cpp CLI/server, or download/select it from the native WebUI once the package is published.

VibeVoice is a long-form, multi-speaker speech generation model. It is intended for English and Chinese speech synthesis.

## Local audio.cpp check

Observed quick-check performance on RTX 5090 for the Q8_0 GGUF in audio.cpp server mode:

- RTF: about `0.18`
- Output length: about `52s`
- Peak VRAM: about `13.3 GB`

These numbers are implementation and hardware dependent. They are only a quick audio.cpp sanity check, not a benchmark.
