---
license: apache-2.0
base_model: OpenMOSS-Team/MOSS-Transcribe-Diarize
library_name: moss-transcribe.cpp
pipeline_tag: automatic-speech-recognition
tags:
  - gguf
  - ggml
  - speech-to-text
  - transcription
  - diarization
  - timestamps
  - moss-transcribe.cpp
  - localai
---

# MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)

GGUF weights for [**moss-transcribe.cpp**](https://github.com/mudler/moss-transcribe.cpp), a from-scratch C++/ggml inference port of [OpenMOSS MOSS-Transcribe-Diarize](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize). Joint long-form transcription, speaker diarization, and timestamps in one pass, on CPU (and on GPU through ggml backends as those land), with no Python, PyTorch, or CUDA toolkit at inference. Each file is fully self-contained (weights, tokenizer, mel filterbank, and all config live inside the GGUF).

Brought to you by the [LocalAI](https://github.com/mudler/LocalAI) team.

## Variants

Every file was verified end-to-end against the reference on the JFK sample (CPU, greedy, 8 threads). "Transcript" is versus the original PyTorch model; "speed" is total wall time on an 11 s clip on a 20-core x86 CPU at 8 threads (the whole model, load included; the autoregressive decode is memory-bandwidth bound, so smaller weights run faster).

| file | size | vs f32 | wall (11 s) | speed vs f32 | transcript vs reference |
| ---- | ---- | ------ | ----------- | ------------ | ----------------------- |
| `moss-transcribe-f16.gguf`  | 1.8 GB | 50% | 4.96 s | 1.6x | byte-identical |
| `moss-transcribe-q8_0.gguf` | 942 MB | 27% | 3.97 s | 2.0x | byte-identical |
| `moss-transcribe-q6_k.gguf` | 733 MB | 21% | 4.16 s | 1.9x | byte-identical |
| `moss-transcribe-q5_k.gguf` | 619 MB | 18% | 4.47 s | 1.8x | byte-identical |
| `moss-transcribe-q5_0.gguf` | 619 MB | 18% | 3.81 s | 2.1x | byte-identical |
| `moss-transcribe-q4_k.gguf` | 511 MB | 15% | 3.81 s | 2.1x | word-identical (one timestamp off 0.02 s) |
| `moss-transcribe-q4_0.gguf` | 511 MB | 15% | 3.57 s | 2.2x | word-identical (one timestamp off 0.07 s) |

Which to pick: **q5_k** or **q5_0** for the best size and accuracy (byte-identical to the reference at about one sixth the size); **q4_k**/**q4_0** for the smallest and fastest (word-identical); **q8_0** for the largest fidelity margin; **f16** if you want the near-lossless full-precision equivalent. The F32 GGUF (3.4 GB, the parity reference) is not published here; produce it with the converter if you need it.

Only the large `ggml_mul_mat`-fed weights (Qwen3 and Whisper attention/FFN projections, the adaptor linears, and the token embedding, 343 tensors) are quantized; norms, biases, the conv stem, positional embeddings, and the mel filterbank stay F32.

## Benchmarks

Same audio, same F32 weights, same threads, byte-identical transcript. moss-transcribe.cpp (ggml, CPU) stays under real time where PyTorch does not, and the gap holds as clips get longer:

![RTF vs audio length: moss-transcribe.cpp vs PyTorch on CPU](benchmarks/rtf_vs_length.png)

Quantization makes the model both smaller and faster (the decode is memory-bandwidth bound), with the transcript byte-identical through q5:

![Quantization ladder: size and speed by dtype](benchmarks/quant_ladder.png)

Full methodology and the reproducible harness are in the [benchmarks](https://github.com/mudler/moss-transcribe.cpp/blob/master/benchmarks/BENCHMARK.md).

## Usage

```sh
git clone --recursive https://github.com/mudler/moss-transcribe.cpp
cd moss-transcribe.cpp
cmake -B build && cmake --build build -j

hf download mudler/moss-transcribe.cpp-gguf moss-transcribe-q5_k.gguf --local-dir .
./build/moss-transcribe transcribe moss-transcribe-q5_k.gguf audio.wav
```

Output is the compact `[start][Sxx]text[end]` transcript with inline speaker tags and timestamps, for example:

```text
[0.28][S01] And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country.[10.59]
```

Set `MTD_THREADS` to tune CPU threads (8 is a good default on a 20-core box; the decode is bandwidth bound, so fewer busy threads often beat more).

## For production serving

Use [LocalAI](https://localai.io) for an OpenAI-compatible `/v1/audio/transcriptions` endpoint, a model gallery, concurrency, auth, and metrics.

## Model

The MOSS-Transcribe-Diarize model is by the [OpenMOSS / MOSI.AI team](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize) (arXiv:2601.01554), released under Apache-2.0. moss-transcribe.cpp is MIT-licensed; these GGUF weights keep the model's Apache-2.0 license.

## Citation

```bibtex
@software{moss_transcribe_cpp,
  title  = {moss-transcribe.cpp: a C++/ggml inference engine for MOSS-Transcribe-Diarize},
  author = {Di Giacinto, Ettore},
  url    = {https://github.com/mudler/moss-transcribe.cpp},
  year   = {2026}
}
```

---

Built by the [LocalAI](https://github.com/mudler/LocalAI) team. If you want to run speech transcription and diarization (and LLMs, vision, voice, image, and video models) locally on any hardware with an OpenAI-compatible API, [give LocalAI a star](https://github.com/mudler/LocalAI).
