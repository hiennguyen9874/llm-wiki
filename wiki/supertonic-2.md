---
type: Concept
title: Supertonic 2
description: Lightning-fast 66M-parameter on-device multilingual TTS with ONNX runtime, five-language coverage, and published characters-per-second and real-time-factor benchmarks.
tags: [tts, on-device, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: supertonic-2-card
    resource: ../raw/supertonic-2.md
    kind: documentation
    title: Supertonic 2 Hugging Face model card
---

Supertonic 2 is Supertone Inc's 66M-parameter on-device multilingual text-to-speech system, running on ONNX Runtime with no cloud or API calls, covering English, Korean, Spanish, Portuguese, and French while claiming the same inference speed as the original Supertonic at up to 167x faster than real-time, with published characters-per-second and real-time-factor tables against cloud APIs and open models (**Reported**).[^supertonic-2-card]

## Model identity and release

- Title is `Supertonic 2`; creator and copyright holder is Supertone Inc (copyright 2026); demo is `https://huggingface.co/spaces/Supertone/supertonic-2` and code is `https://github.com/supertone-inc/supertonic` (**Reported**).[^supertonic-2-card]
- Frontmatter declares `pipeline_tag: text-to-speech`, `library_name: supertonic`, `license: openrail`, languages `en, ko, es, pt, fr`, and tags `text-to-speech, speech-synthesis, tts, onnx` (**Observed** by static inspection).[^supertonic-2-card]
- Positioned as the multilingual successor to the original Supertonic with unchanged inference speed and efficiency: 66M parameters, same architecture and inference pipeline across all languages, and the same up-to-167x-real-time claim (**Reported**).[^supertonic-2-card]

## Multilingual support

- Supported languages and codes are English (`en`), Korean (`ko`), Spanish (`es`), Portuguese (`pt`), and French (`fr`) (**Reported**).[^supertonic-2-card]
- Cross-language consistency is claimed: all supported languages share the same model architecture and inference pipeline (**Reported**).[^supertonic-2-card]

## Architecture and deployment

- Runtime is ONNX Runtime for fully on-device inference with no cloud, no API calls, and no privacy exposure stated as the design goal (**Reported**).[^supertonic-2-card]
- Efficiency claims are 66M parameters, minimal computational overhead, and no speed degradation versus the original Supertonic (**Reported**).[^supertonic-2-card]
- Configurable inference steps are evidenced by separate 2-step (main) and 5-step (details element) benchmark sets (**Reported**).[^supertonic-2-card]

## Performance method

- Evaluation uses two metrics across three input lengths: Short (59 chars), Mid (152 chars), Long (266 chars); characters per second is input characters divided by generation time (higher is better), and real-time factor is synthesis time relative to audio duration (lower is better, e.g. 0.1 means 0.1 s per 1 s of audio) (**Reported**).[^supertonic-2-card]
- Test conditions stated in the notes: cloud `API` systems measured from Seoul; `Open` denotes open-source models; Supertonic on M4 Pro CPU and M4 Pro WebGPU tested with ONNX; Supertonic on RTX 4090 tested with the PyTorch model; Kokoro tested on M4 Pro CPU with ONNX; NeuTTS Air tested on M4 Pro CPU with Q8-GGUF (**Reported**).[^supertonic-2-card]

## Performance results with 2 inference steps

- Characters per second (2-step): Supertonic RTX 4090 leads at 2615 / 6548 / 12164 (Short/Mid/Long), followed by Supertonic M4 Pro WebGPU at 996 / 1801 / 2509 and M4 Pro CPU at 912 / 1048 / 1263; the fastest compared cloud API is ElevenLabs Flash v2.5 at 144 / 209 / 287, and the fastest compared open model is Kokoro at 104 / 107 / 117 (**Reported**).[^supertonic-2-card]

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

- Real-time factor (2-step): Supertonic RTX 4090 reports 0.005 / 0.002 / 0.001, M4 Pro WebGPU 0.014 / 0.007 / 0.006, and M4 Pro CPU 0.015 / 0.013 / 0.012; the best compared figures are ElevenLabs Flash v2.5 at 0.133 / 0.077 / 0.057 and Kokoro at 0.144 / 0.124 / 0.126 (**Reported**).[^supertonic-2-card]

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

- Additional 5-step data: characters per second on M4 Pro CPU 596 / 691 / 850, M4 Pro WebGPU 570 / 1118 / 1546, RTX 4090 1286 / 3757 / 6242; real-time factor on M4 Pro CPU 0.023 / 0.019 / 0.018, M4 Pro WebGPU 0.024 / 0.012 / 0.010, RTX 4090 0.011 / 0.004 / 0.002 (**Reported**).[^supertonic-2-card]

## License

- Sample code is under the MIT License; the accompanying model is under the OpenRAIL-M License; training used PyTorch under BSD 3-Clause without redistributing it (**Reported**).[^supertonic-2-card]

## Relationships

- Original predecessor: [Supertonic](supertonic.md) covers the original repository README with 11-runtime deployment examples, assets-via-Hub setup, and CPU-optimized plus onnxruntime-web technical details, while this concept covers the 5-language extension with the same 66M-parameter and up-to-167x-real-time claims and identical CPS/RTF table values; no deprecation of the original is asserted in either capture (**Synthesis**).[^supertonic-2-card]
- On-device lightweight TTS comparison: [Pocket TTS](pocket-tts.md) covers a 100M-parameter CPU-first multilingual TTS system with about 200 ms first-chunk streaming and about 6x real-time on MacBook Air M4, while this concept covers a 66M-parameter ONNX on-device multilingual TTS with vendor-reported up to 167x real-time and CPS/RTF tables; no shared codebase is asserted (**Synthesis**).[^supertonic-2-card]
- Ultra-lightweight TTS comparison: [Soprano-1.1-80M](soprano-1-1-80m.md) covers an 80M-parameter English-only on-device TTS model with vendor-reported up to 2000x GPU real-time factor and sub-15 ms GPU streaming, while this concept covers a 66M-parameter 5-language on-device TTS with M4 Pro and RTX 4090 CPS/RTF tables; no shared vendor or codebase is asserted (**Synthesis**).[^supertonic-2-card]
- Real-time TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual real-time TTS model with voice clone/design/direction and H100 latency figures, while this concept covers a 5-language ONNX on-device TTS with 2-step and 5-step throughput tables; no shared vendor or codebase is asserted (**Synthesis**).[^supertonic-2-card]
- Sub-1B multilingual TTS comparison: [MOSS-TTS-Nano](moss-tts-nano.md) covers a 0.1B-parameter multilingual zero-shot voice-cloning TTS model with 48 kHz stereo output and ONNX CPU streaming, while this concept covers a 66M-parameter multilingual on-device TTS with API/open-model comparative benchmarks; no shared vendor or codebase is asserted (**Synthesis**).[^supertonic-2-card]

## Coverage and limits

- Source inspected statically only; no checkpoint downloaded, no ONNX or PyTorch inference executed, and no characters-per-second, real-time-factor, 167x-real-time, or cross-language-consistency claims reproduced (**Synthesis**).[^supertonic-2-card]
- Preview image (`img/supertonic_preview_0.1.jpg`), demo Space, GitHub repository, compared API and open-model systems, and linked license pages were not fetched and are not in `raw/`; model weights, preset voices, audio output, and synthesis quality were not inspected (**Synthesis**).[^supertonic-2-card]
- All capability, speed, efficiency, language-coverage, benchmark, and license claims are source assertions without independent verification in this wiki; throughput, latency, and release figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^supertonic-2-card]
- This ingest covers only `raw/supertonic-2.md`; the related original `raw/supertonic.md` (copyright 2025) is now compiled in [Supertonic](supertonic.md), which holds the v1-only setup, 11-runtime examples, CPU-optimized plus onnxruntime-web details, and the missing-`Citation`-section limit; performance table values are identical across both captures (verified by diff); `Supertonic-3-GGUF` mentioned in the audio.cpp catalog is a different artifact and is not covered here (**Synthesis**).[^supertonic-2-card]

[^supertonic-2-card]: [Supertonic 2 Hugging Face model card](../raw/supertonic-2.md) — locators: frontmatter (`license`, `language`, `pipeline_tag`, `tags`, `library_name`); H1 plus intro paragraph (ONNX Runtime, on-device, no cloud/API/privacy); `What's New in Supertonic 2` section (multilingual extension, same speed/efficiency); `Multilingual Support` table (en/ko/es/pt/fr codes); `Same Speed, More Languages` bullets (167x real-time, 66M parameters, cross-language consistency); `Performance` intro (2 inference steps; Short 59 / Mid 152 / Long 266 chars); `Metrics` bullets (Characters per Second, Real-time Factor with 0.1 example); `Characters per Second` 2-step table (Supertonic M4 Pro CPU/WebGPU + RTX4090 rows vs ElevenLabs/OpenAI/Gemini/Sona/Kokoro/NeuTTS Air rows); `Real-time Factor` 2-step table (same row layout); `Notes` callout (API measured from Seoul, Open meaning, ONNX vs PyTorch vs Q8-GGUF test conditions); `<details> Additional Performance Data (5-step inference)` tables (CPS + RTF for M4 Pro CPU/WebGPU + RTX4090); `License` section (MIT sample code, OpenRAIL-M model, PyTorch BSD 3-Clause, 2026 Supertone copyright).
