---
type: Concept
title: Supertonic
description: 66M-parameter on-device TTS with ONNX runtime, 11-runtime deployment examples, and published characters-per-second and real-time-factor benchmarks.
tags: [tts, on-device, onnx]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: supertonic-readme
    resource: ../raw/supertonic.md
    kind: documentation
    title: Supertonic GitHub repository README
---

Supertonic is Supertone Inc's 66M-parameter on-device text-to-speech system, running on ONNX Runtime with no cloud or API calls, claiming up to 167x faster than real-time on M4 Pro, natural handling of numbers, dates, currency, abbreviations, and complex expressions without pre-processing, configurable inference steps and batch processing, deployment across servers, browsers, and edge devices, and published characters-per-second and real-time-factor tables against cloud APIs and open models (**Reported**).[^supertonic-readme]

## Model identity and release

- Title is `Supertonic — Lightning Fast, On-Device TTS`; creator and copyright holder is Supertone Inc (copyright 2025); code is `https://github.com/supertone-inc/supertonic`, pre-trained models are at `https://huggingface.co/Supertone/supertonic`, demos are `https://huggingface.co/spaces/Supertone/supertonic#interactive-demo` and `https://huggingface.co/spaces/akhaliq/supertonic` (**Reported**).[^supertonic-readme]
- Frontmatter declares `license: openrail`, `language: en`, `pipeline_tag: text-to-speech`, and `library_name: supertonic` (**Observed** by static inspection).[^supertonic-readme]
- Value claims are blazingly fast generation up to 167x faster than real-time on M4 Pro, ultra-lightweight 66M parameters, complete privacy and zero latency from fully local processing, natural text handling, highly configurable inference steps and batch processing, and flexible deployment across servers, browsers, and edge devices with multiple runtime backends (**Reported**).[^supertonic-readme]

## Runtime and deployment matrix

- The source provides ready-to-use inference examples across 11 language/platform ecosystems, each with its own directory and `README.md` that is not in `raw/` (**Reported**).[^supertonic-readme]

| Language/Platform | Path | Description |
|-------------------|------|-------------|
| Python | `py/` | ONNX Runtime inference |
| Node.js | `nodejs/` | Server-side JavaScript |
| Browser | `web/` | WebGPU/WASM inference |
| Java | `java/` | Cross-platform JVM |
| C++ | `cpp/` | High-performance C++ |
| C# | `csharp/` | .NET ecosystem |
| Go | `go/` | Go implementation |
| Swift | `swift/` | macOS applications |
| iOS | `ios/` | Native iOS apps |
| Rust | `rust/` | Memory-safe systems |
| Flutter | `flutter/` | Cross-platform apps |

## Setup and technical details

- Setup clones `https://github.com/supertone-inc/supertonic.git`, then downloads ONNX models and preset voices via `git clone https://huggingface.co/Supertone/supertonic assets` into the `assets` directory (**Reported**).[^supertonic-readme]
- The Hugging Face repository uses Git LFS; the source instructs macOS `brew install git-lfs && git lfs install` and points generic platforms to `https://git-lfs.com` (**Reported**).[^supertonic-readme]
- Runtime is ONNX Runtime for cross-platform inference, stated as CPU-optimized with GPU mode not tested; browser inference uses onnxruntime-web; batch inference is supported for throughput; audio output is 16-bit WAV files (**Reported**).[^supertonic-readme]

## Performance method

- Evaluation uses two metrics across three input lengths: Short (59 chars), Mid (152 chars), Long (266 chars); characters per second is input characters divided by generation time (higher is better), and real-time factor is synthesis time relative to audio duration (lower is better, e.g. 0.1 means 0.1 s per 1 s of audio); the main tables use 2 inference steps with additional 5-step data in a details element (**Reported**).[^supertonic-readme]
- Test conditions stated in the notes: cloud `API` systems measured from Seoul; `Open` denotes open-source models; Supertonic on M4 Pro CPU and M4 Pro WebGPU tested with ONNX; Supertonic on RTX 4090 tested with the PyTorch model; Kokoro tested on M4 Pro CPU with ONNX; NeuTTS Air tested on M4 Pro CPU with Q8-GGUF (**Reported**).[^supertonic-readme]

## Performance results with 2 inference steps

- Characters per second (2-step): Supertonic RTX 4090 leads at 2615 / 6548 / 12164 (Short/Mid/Long), followed by Supertonic M4 Pro WebGPU at 996 / 1801 / 2509 and M4 Pro CPU at 912 / 1048 / 1263; the fastest compared cloud API is ElevenLabs Flash v2.5 at 144 / 209 / 287, and the fastest compared open model is Kokoro at 104 / 107 / 117 (**Reported**).[^supertonic-readme]

| System | Short (59 chars) | Mid (152 chars) | Long (266 chars) |
|--------|-----------------|----------------|-----------------|
| **Supertonic** (M4 Pro CPU, ONNX) | 912 | 1048 | 1263 |
| **Supertonic** (M4 Pro WebGPU, ONNX) | 996 | 1801 | 2509 |
| **Supertonic** (RTX 4090, PyTorch) | 2615 | 6548 | 12164 |
| `API` ElevenLabs Flash v2.5 | 144 | 209 | 287 |
| `API` OpenAI TTS-1 | 37 | 55 | 82 |
| `API` Gemini 2.5 Flash TTS | 12 | 18 | 24 |
| `API` Supertone Sona speech 1 | 38 | 64 | 92 |
| `Open` Kokoro (M4 Pro CPU, ONNX) | 104 | 107 | 117 |
| `Open` NeuTTS Air (M4 Pro CPU, Q8-GGUF) | 37 | 42 | 47 |

- Real-time factor (2-step): Supertonic RTX 4090 reports 0.005 / 0.002 / 0.001, M4 Pro WebGPU 0.014 / 0.007 / 0.006, and M4 Pro CPU 0.015 / 0.013 / 0.012; the best compared figures are ElevenLabs Flash v2.5 at 0.133 / 0.077 / 0.057 and Kokoro at 0.144 / 0.124 / 0.126 (**Reported**).[^supertonic-readme]

| System | Short (59 chars) | Mid (152 chars) | Long (266 chars) |
|--------|-----------------|----------------|-----------------|
| **Supertonic** (M4 Pro CPU, ONNX) | 0.015 | 0.013 | 0.012 |
| **Supertonic** (M4 Pro WebGPU, ONNX) | 0.014 | 0.007 | 0.006 |
| **Supertonic** (RTX 4090, PyTorch) | 0.005 | 0.002 | 0.001 |
| `API` ElevenLabs Flash v2.5 | 0.133 | 0.077 | 0.057 |
| `API` OpenAI TTS-1 | 0.471 | 0.302 | 0.201 |
| `API` Gemini 2.5 Flash TTS | 1.060 | 0.673 | 0.541 |
| `API` Supertone Sona speech 1 | 0.372 | 0.206 | 0.163 |
| `Open` Kokoro (M4 Pro CPU, ONNX) | 0.144 | 0.124 | 0.126 |
| `Open` NeuTTS Air (M4 Pro CPU, Q8-GGUF) | 0.390 | 0.338 | 0.343 |

- Additional 5-step data: characters per second on M4 Pro CPU 596 / 691 / 850, M4 Pro WebGPU 570 / 1118 / 1546, RTX 4090 1286 / 3757 / 6242; real-time factor on M4 Pro CPU 0.023 / 0.019 / 0.018, M4 Pro WebGPU 0.024 / 0.012 / 0.010, RTX 4090 0.011 / 0.004 / 0.002 (**Reported**).[^supertonic-readme]

## License

- Sample code is under the MIT License; the accompanying model is under the OpenRAIL-M License; training used PyTorch under BSD 3-Clause without redistributing it (**Reported**).[^supertonic-readme]

## Relationships

- Multilingual successor: [Supertonic 2](supertonic-2.md) covers the 5-language ONNX on-device TTS with the same 66M-parameter and up-to-167x-real-time claims and identical 2-step and 5-step CPS/RTF table values, while this concept covers the original repository README with 11-runtime deployment examples, assets-via-Hub setup, and CPU-optimized plus onnxruntime-web technical details; no deprecation of the original is asserted in this source (**Synthesis**).[^supertonic-readme]
- On-device lightweight TTS comparison: [Pocket TTS](pocket-tts.md) covers a 100M-parameter CPU-first multilingual TTS system with about 200 ms first-chunk streaming and about 6x real-time on MacBook Air M4, while this concept covers a 66M-parameter ONNX on-device TTS with vendor-reported up to 167x real-time and CPS/RTF tables; no shared codebase is asserted (**Synthesis**).[^supertonic-readme]
- Ultra-lightweight TTS comparison: [Soprano-1.1-80M](soprano-1-1-80m.md) covers an 80M-parameter English-only on-device TTS model with vendor-reported up to 2000x GPU real-time factor and sub-15 ms GPU streaming, while this concept covers a 66M-parameter on-device TTS with M4 Pro and RTX 4090 CPS/RTF tables and 11-runtime examples; no shared vendor or codebase is asserted (**Synthesis**).[^supertonic-readme]
- Real-time TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with voice clone/design/direction and H100 latency figures, while this concept covers an ONNX on-device TTS with 2-step and 5-step throughput tables and 16-bit WAV batch output; no shared vendor or codebase is asserted (**Synthesis**).[^supertonic-readme]

## Coverage and limits

- Source inspected statically only; no repository cloned, no checkpoint or preset voice downloaded, no ONNX or PyTorch inference executed, and no characters-per-second, real-time-factor, 167x-real-time, text-handling, or configurability claims reproduced (**Synthesis**).[^supertonic-readme]
- Per-language `README.md` files in `py/`, `nodejs/`, `web/`, `java/`, `cpp/`, `csharp/`, `go/`, `swift/`, `ios/`, `rust/`, and `flutter/`, the `assets/` model and voice contents, demo Spaces, GitHub repository, Hugging Face Hub, compared API and open-model systems, and linked license pages were not fetched and are not in `raw/`; model weights, preset voices, audio output, and synthesis quality were not inspected (**Synthesis**).[^supertonic-readme]
- All capability, speed, efficiency, deployment, benchmark, and license claims are source assertions without independent verification in this wiki; throughput, latency, and release figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^supertonic-readme]
- TTS language scope is bounded: frontmatter declares only `en` and the body lists implementation runtimes rather than a TTS language list, while [Supertonic 2](supertonic-2.md) positions itself as the 5-language extension with the same speed and table values (verified by diff of the performance sections); the table of contents lists a `Citation` section that has no corresponding body section in this capture (**Synthesis**).[^supertonic-readme]

[^supertonic-readme]: [Supertonic GitHub repository README](../raw/supertonic.md) — locators: frontmatter (`license`, `language`, `pipeline_tag`, `library_name`); H1 plus intro paragraph (ONNX Runtime, on-device, no cloud/API/privacy); `Try it now` callout (Interactive Demo, Hugging Face app, Hugging Face Hub links); `GitHub Repository` callout (supertone-inc/supertonic URL, multi-language examples pointer); `Table of Contents` (Why/Language/Getting Started/Performance/Citation/License); `Why Supertonic` bullets (167x M4 Pro, 66M parameters, privacy/zero latency, numbers/dates/currency/abbreviations/complex expressions, inference steps/batch, servers/browsers/edge); `Language Support` table (Python `py/`, Node.js `nodejs/`, Browser `web/` WebGPU/WASM, Java `java/`, C++ `cpp/`, C# `csharp/`, Go `go/`, Swift `swift/`, iOS `ios/`, Rust `rust/`, Flutter `flutter/` plus per-directory README pointer); `Getting Started` fences (`git clone https://github.com/supertone-inc/supertonic.git`, `cd supertonic`); `Prerequisites` fence (`git clone https://huggingface.co/Supertone/supertonic assets`) plus Git LFS note (macOS `brew install git-lfs && git lfs install`, `https://git-lfs.com`); `Technical Details` bullets (ONNX CPU-optimized GPU-untested, onnxruntime-web, batch inference, 16-bit WAV); `Performance` intro (2 inference steps; Short 59 / Mid 152 / Long 266 chars); `Metrics` bullets (Characters per Second, Real-time Factor with 0.1 example); `Characters per Second` 2-step table (Supertonic M4 Pro CPU/WebGPU + RTX4090 rows vs ElevenLabs/OpenAI/Gemini/Sona/Kokoro/NeuTTS Air rows); `Real-time Factor` 2-step table (same row layout); `Notes` callout (API measured from Seoul, Open meaning, ONNX vs PyTorch vs Q8-GGUF test conditions); `<details> Additional Performance Data (5-step inference)` tables (CPS + RTF for M4 Pro CPU/WebGPU + RTX4090); `License` section (MIT sample code, OpenRAIL-M model, PyTorch BSD 3-Clause, 2025 Supertone copyright).
