---
license: apache-2.0
language:
- zh
- en
library_name: gguf
tags:
- automatic-speech-recognition
- asr
- fun-asr
- funasr
- qwen3
- llama.cpp
- ggml
- cpu
- chinese
- arxiv:2407.04051
pipeline_tag: automatic-speech-recognition
---

# Fun-ASR-Nano · GGUF (FunASR llama.cpp runtime)

GGUF build of **Fun-ASR-Nano** (SenseVoice SAN-M encoder + adaptor + **Qwen3-0.6B** LLM decoder) for the zero-Python, CPU/edge **[FunASR llama.cpp runtime](https://github.com/FunAudioLLM/Fun-ASR/tree/main/runtime/llama.cpp)** — the accuracy leader (LLM decoder), single C++ binary.

## LLM quantization (pick by size vs accuracy)

The Fun-ASR-Nano LLM (Qwen3-0.6B) ships in three tiers — all within 0.1% CER (184-file micro-CER). Pair any with `funasr-encoder-f16.gguf` (470 MB).

| LLM file | size | CER ↓ | speed |
|---|---|---|---|
| `qwen3-0.6b-q4km.gguf` | **484 MB** | 8.35% | 6.1× | smallest |
| `qwen3-0.6b-q5km.gguf` | 551 MB | **8.25%** | 5.7× | best accuracy |
| `qwen3-0.6b-q8_0.gguf` | 805 MB | 8.30% | 6.0× | |

Recommended: **q4_K_M** (smallest) or **q5_K_M** (best).

## Get it running (no Python, no build)

These are GGUF weights for the **[FunASR llama.cpp runtime](https://github.com/modelscope/FunASR/tree/main/runtime/llama.cpp)** — a whisper.cpp-style, single self-contained binary for CPU / edge. Grab a prebuilt binary, then fetch this model and run:

- **Prebuilt binaries (Linux / macOS / Windows) → [GitHub Releases](https://github.com/modelscope/FunASR/releases)** (tag `runtime-llamacpp-v*`)
- **Deployment guide & qualified benchmarks → [funasr.com/deploy/llama-cpp](https://www.funasr.com/deploy/llama-cpp.html)**

```bash
bash download-funasr-model.sh nano ./gguf
llama-funasr-cli --enc ./gguf/funasr-encoder-f16.gguf -m ./gguf/qwen3-0.6b-q8_0.gguf --vad ./gguf/fsmn-vad.gguf -a audio.wav
```

## Files
| file | size | notes |
|---|---|---|
| `funasr-encoder-f16.gguf` | 470 MB | audio encoder + adaptor (f16) |
| `qwen3-0.6b-q8_0.gguf` | 805 MB | LLM decoder, **recommended** (Q8_0) |
| `qwen3-0.6b-q4km.gguf` | 484 MB | LLM decoder, smaller (Q4_K_M) |

## Usage (needs both the encoder and the LLM gguf)
```bash
llama-funasr-cli --enc funasr-encoder-f16.gguf -m qwen3-0.6b-q8_0.gguf -a audio.wav --vad fsmn-vad.gguf
```
On CPU: **8.30 % CER** on the 184-clip Mandarin benchmark (vs whisper.cpp 22–31 %).

## Links
- 🧩 Runtime & build: **[Fun-ASR · runtime/llama.cpp](https://github.com/FunAudioLLM/Fun-ASR/tree/main/runtime/llama.cpp)** — ⭐ **Star [Fun-ASR](https://github.com/FunAudioLLM/Fun-ASR)!**
- Source model: [FunAudioLLM/Fun-ASR-Nano-2512](https://huggingface.co/FunAudioLLM/Fun-ASR-Nano-2512)
