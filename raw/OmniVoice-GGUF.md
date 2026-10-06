---
license: cc-by-nc-4.0
license_link: https://huggingface.co/k2-fsa/OmniVoice#license
library_name: gguf
pipeline_tag: text-to-speech
tags:
  - tts
  - text-to-speech
  - voice-cloning
  - voice-design
  - ggml
  - gguf
  - omnivoice
  - cpp
language:
  - en
  - fr
  - de
  - es
  - it
  - pt
  - zh
  - ja
  - ko
  - ar
  - ru
base_model: k2-fsa/OmniVoice
---

# OmniVoice GGUF

GGUF weights for [omnivoice.cpp](https://github.com/ServeurpersoCom/omnivoice.cpp),
a C++17/GGML port of OmniVoice (k2-fsa/OmniVoice). Multilingual zero
shot TTS, 646 languages, 24 kHz mono. Runs on CPU, CUDA, ROCm, Metal,
Vulkan.

## Files

Two GGUFs load together :

  omnivoice-base-{variant}.gguf       Qwen3 0.6B backbone, text -> tokens
  omnivoice-tokenizer-{variant}.gguf  HuBERT + DAC + RVQ, tokens <-> 24 kHz audio

| variant | base    | tokenizer | use case                       |
|---------|---------|-----------|--------------------------------|
| F32     | 2.46 GB | 734 MB    | reference, debug, conversion   |
| BF16    | 1.23 GB | 373 MB    | source faithful, max precision |
| Q8_0    | 656 MB  | 289 MB    | recommended default            |
| Q4_K_M  | 407 MB  | 252 MB    | lowest VRAM                    |

## Quick start

```
git clone --recurse-submodules https://github.com/ServeurpersoCom/omnivoice.cpp.git
cd omnivoice.cpp && ./buildcuda.sh

mkdir -p models
huggingface-cli download Serveurperso/OmniVoice-GGUF \
    omnivoice-base-Q8_0.gguf omnivoice-tokenizer-Q8_0.gguf \
    --local-dir models

cd examples
./tts.sh        # voice design   -> tts.wav
./clone.sh      # voice cloning  -> clone.wav
```

## Backends

Set `GGML_BACKEND` to force a device, otherwise the runtime picks the
best one available.

| value     | target                                       |
|-----------|----------------------------------------------|
| `CUDA0`   | NVIDIA GPU, fastest path on Ada / Blackwell  |
| `Vulkan0` | Cross vendor GPU (AMD / Intel / NVIDIA)      |
| `Metal`   | Apple Silicon GPU                            |
| `CPU`     | CPU fallback, x86 variant auto selected      |

## Quantization policy

Tokenizer GGUFs are not uniform quants. Three categories get a
dedicated treatment :

| tensor                                            | dtype across all variants |
|---------------------------------------------------|---------------------------|
| RVQ codebooks, fc, fc2, project_in / project_out  | F32                       |
| Snake activation alpha                            | F32                       |
| Conv kernels with non alignable rows (K=7,3,1)    | F16 (in Q* variants)      |

Same fallback as llama.cpp `tensor_type_fallback` : F16 has no block
size and matches the runtime target dtype on every backend. The base
LM (Qwen3 0.6B, hidden = 1024) has all dimensions divisible by 256 so
the fallback never triggers, the LM follows standard llama.cpp K-quant
across variants.

## License

  Upstream weights : OmniVoice by Xiaomi / k2-fsa, CC-BY-NC 4.0
  Upstream code    : OmniVoice by Xiaomi / k2-fsa, Apache 2.0
  Audio codec      : Higgs Audio v2 (bosonai/higgs-audio-v2-tokenizer), Apache 2.0
  GGUF tooling     : omnivoice.cpp, MIT

The upstream code is Apache 2.0 but the pre-trained weights are CC-BY-NC
because of constraints from the training data. These GGUF files are
conversions of those weights and carry the same non commercial terms.
