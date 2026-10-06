---
type: Concept
title: SGLang-Omni
description: Multi-stage GPU serving runtime for omni, speech, TTS, and ASR models with stage-specialized scheduling, tensor transport, and OpenAI-compatible APIs.
tags: [tts, stt, serving, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: sglang-omni-readme
    resource: ../raw/sglang-omni.md
    kind: documentation
    title: SGLang-Omni GitHub README (v0.1.7-era, 2026/09 news)
---

SGLang-Omni is a multi-stage GPU serving runtime for omni, speech, and TTS models that models generation as coordinated heterogeneous stages — preprocessing, encoders, autoregressive engines, talkers, decoders, vocoders, and aggregators — with stage-matched scheduling and a control-plane plus relay-data-plane transport over shared memory, NCCL, NIXL, and Mooncake, exposing multimodal chat, speech generation, and transcription behind OpenAI-compatible endpoints while composing with SGLang for autoregressive scheduling and execution where applicable (**Reported**).[^sglang-omni-readme]

## Runtime identity and design target

- Design target is multi-stage decoding: generation split across heterogeneous stages with different compute patterns, dependency structures, and resource needs (**Reported**).[^sglang-omni-readme]
- SGLang-Omni owns pipeline topology, stage lifecycle, inter-stage transport, the model-family integration layer, and the OpenAI-compatible serving surface, while composing with [SGLang](https://github.com/sgl-project/sglang) for high-performance autoregressive scheduling and model execution where applicable (**Reported**).[^sglang-omni-readme]
- Upstream is `sgl-project/sglang-omni`; the captured README carries PyPI, stars, license, issue, and DeepWiki badges plus Blog, Documentation, Quick Start, Cookbook, SGLang, and Slack links, and solicits stars as open infrastructure for multimodal and speech serving (**Reported**).[^sglang-omni-readme]

## Release and news

- v0.1.7 is on PyPI with install fence `uv pip install --prerelease=allow "sglang-omni==0.1.7"` (**Reported**).[^sglang-omni-readme]
- Day-0 support entries: AuK and AuK-Flash in 2026/09 (text plus voice instructions to 24 kHz speech on `/v1/audio/speech`; audio plus editing instructions to edited speech on `/generate`), MiniMax Music 3 in 2026/08 (lyrics plus caption to 32 kHz stereo song on `/v1/audio/speech`), MOSS-TTS Local Transformer v1.5 native-streaming 48 kHz speech in 2026/06, and Higgs Audio v3 real-time controllable speech in 2026/06 (**Reported**).[^sglang-omni-readme]
- TTS architecture refactor in 2026/08 covers shared pipeline state, engine construction, reference encoding, capability metadata, and vocoder scheduling, with Roadmap and blog pointers (**Reported**).[^sglang-omni-readme]

## Served model coverage

- Omni chat and speech: Qwen3-Omni and Ming-Omni — multimodal in, text/audio out (**Reported**).[^sglang-omni-readme]
- Speech generation over `/v1/audio/speech` with batch, streaming, and uploaded voices: Higgs Audio v3, MOSS-TTS, MOSS-TTS Local, Fish Speech S2-Pro, Qwen3-TTS, Voxtral TTS, Ming-Omni-TTS, dots.tts, and ZONOS2, plus AuK and AuK-Flash per the News section (**Reported**).[^sglang-omni-readme]
- Audio transcription and diarization over `/v1/audio/transcriptions`: Qwen3-ASR, Fun-ASR, ARK-ASR, Nemotron 3.5 ASR, and MOSS-Transcribe-Diarize; MOSS-TD supports speaker labels and timestamps via `response_format=verbose_json` (**Reported**).[^sglang-omni-readme]
- SGLang-Omni Router is a multi-worker OpenAI-compatible front door covering health, readiness, lifecycle, and capability discovery (**Reported**).[^sglang-omni-readme]
- MiniMax Music 3 lyrics-plus-caption to 32 kHz stereo song is listed in the source but is music-only generation, out of voice-loop scope per `SCOPE.md`, and is retained here only as catalog context (**Synthesis**).[^sglang-omni-readme]

## Architecture: stages, scheduling, transport

- Multi-stage runtime stages: preprocessing, encoders, autoregressive engines, talkers, decoders, vocoders, and aggregators (**Reported**).[^sglang-omni-readme]
- Stage-specialized scheduling: each stage runs behind a scheduler matched to its workload, from SGLang-backed autoregressive scheduling to lightweight preprocessing and streaming vocoder loops (**Reported**).[^sglang-omni-readme]
- Transport-aware execution: a control plane coordinates requests while the relay data plane moves tensor payloads across shared-memory, NCCL, NIXL, and Mooncake backends (**Reported**).[^sglang-omni-readme]
- API surface exposes multimodal chat, speech generation, batch speech, streaming speech, uploaded voices, and transcription (**Reported**).[^sglang-omni-readme]

## Hardware, install, and usage pointers

- NVIDIA CUDA is the supported default backend with full model coverage (**Reported**).[^sglang-omni-readme]
- Apple Silicon is experimental: Qwen3-ASR runs through native MLX or Torch MPS on macOS arm64, installed with `install.sh` and the Qwen3-ASR guide (**Reported**).[^sglang-omni-readme]
- Intel GPU (XPU) is experimental: Intel Arc GPUs via PyTorch XPU serve Qwen3-ASR, Qwen3-TTS, ZONOS2, and Qwen3-Omni end to end (ZONOS2 with decode graphs; Omni thinker via multi-XPU tensor parallelism); install follows the Intel XPU guide and the backend is auto-detected (**Reported**).[^sglang-omni-readme]
- Quick-start pointers are macOS Apple Silicon one-command `./install.sh` for Homebrew plus uv setup, Installation, TTS usage, Qwen3-Omni usage, Qwen3-ASR / Nemotron 3.5 ASR / MOSS-Transcribe-Diarize cookbooks, Omni router, and Developer reference; the linked guides, `install.sh`, and `docs/` paths were not present in `raw/` and were not inspected (**Reported**, with unfetched-pointer limit).[^sglang-omni-readme]

## Community and support boundary

- The project welcomes contributors on inference systems, kernels, scheduling, inter-stage communication, model runners and cache efficiency, model integration, benchmarking, and production deployment, via Slack and the developer reference (**Reported**).[^sglang-omni-readme]
- Organizations are directed to a named maintainer contact published in the source; the address is omitted here and resolvable in `../raw/sglang-omni.md` (**Synthesis**).[^sglang-omni-readme]
- The source thanks the SGLang ecosystem and open TTS, speech, and omni-model communities, including model teams, systems contributors, and partner organizations (**Reported**).[^sglang-omni-readme]

## Relationships

- Serves: [Higgs TTS 3](higgs-tts-3-4b.md) names SGLang Omni as its documented production stack with continuous batching, `/v1/audio/speech` synthesis, cloning, and streaming; consult that page for model weights, tag controls, and H100 throughput (**Synthesis**).[^sglang-omni-readme]
- Serves: [Fish Audio S2 Pro](fish-audio-s2-pro.md) runs on an SGLang-based streaming engine with LLM-native batching and prefix-caching optimizations; consult that page for DualAR architecture and H200 latency figures (**Synthesis**).[^sglang-omni-readme]
- Serves: [AuK](auk.md) and [AuK-Flash](auk-flash.md) report Day-0 SGLang-Omni support for 16 instruction-driven speech generation and editing tasks; consult those pages for task coverage and weights (**Synthesis**).[^sglang-omni-readme]
- Serves: [Qwen3-ASR family](qwen3-asr-family.md), [Fun-ASR-Nano-2512](fun-asr-nano-2512.md), [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md), [ARK-ASR-3B](ark-asr-3b.md), [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md), and [MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)](moss-transcribe-cpp-gguf.md) cover the ASR and transcribe-diarize families this runtime fronts over `/v1/audio/transcriptions`; no shared-vendor claim is made (**Synthesis**).[^sglang-omni-readme]
- Serves: [dots.tts-mf](dots-tts-mf.md), [dots.tts-soar](dots-tts-soar.md), [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md), and [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) cover TTS families in this runtime's `/v1/audio/speech` speech-generation list; no shared codebase is asserted (**Synthesis**).[^sglang-omni-readme]
- Contrasts with [audio.cpp Framework](audio-cpp-framework.md): audio.cpp is a native ggml-based C++ runtime for local CPU/edge GGUF deployment across TTS, ASR, VAD, and diarization, while SGLang-Omni is a GPU multi-stage server runtime with SGLang-backed scheduling, tensor transport, and OpenAI-compatible serving; compare them when choosing edge-local versus server-GPU deployment (**Synthesis**).[^sglang-omni-readme]
- Complements [WhisperLiveKit](whisperlivekit.md): WhisperLiveKit is a self-hosted streaming STT server with simultaneous-speech policies and API-compatible serving, while SGLang-Omni fronts many ASR plus TTS/omni families behind one multi-worker router; compare them on backend breadth versus STT-pipeline specialization (**Synthesis**).[^sglang-omni-readme]
- Contrasts with [vLLM-Omni](vllm-omni.md): vLLM-Omni is the vLLM-line omni-modality serving counterpart with vLLM-derived KV-cache management, OmniConnector disaggregation, AR/DiT paged KV, and engine-owned full-duplex sessions; compare them when choosing a server-GPU omni/TTS serving stack (**Synthesis**).[^sglang-omni-readme]

## Coverage and limits

- Source inspected statically only; no package installed, no server launched, no model served, and no latency, throughput, streaming, or quality claim reproduced — all capability, compatibility, and version claims are source assertions (**Synthesis**).[^sglang-omni-readme]
- Logo SVG, badges, cookbook, installation, basic-usage, developer-reference, `install.sh`, and `docs/cookbook` plus `docs/get_started` guides were linked but not fetched and were not present in `raw/`; stage internals, scheduler behavior, transport backends, router semantics, and checkpoint contents were not inspected (**Synthesis**).[^sglang-omni-readme]
- License badge links to the upstream `LICENSE` but the license identifier is not stated in the captured text and was not resolved here (**Synthesis**).[^sglang-omni-readme]
- Release, Day-0 support, hardware-support, and API-surface claims carry `stale_after: 2027-10-06` per the `tts`/`stt`/`llm` domain rules (**Synthesis**).[^sglang-omni-readme]

[^sglang-omni-readme]: [SGLang-Omni GitHub README](../raw/sglang-omni.md) — locators: header badges and link row (PyPI, stars, license, issues, DeepWiki; Blog, Documentation, Quick Start, Cookbook, SGLang, Slack; star solicitation); `News` (2026/09 AuK/AuK-Flash 24 kHz `/v1/audio/speech` plus `/generate` editing and v0.1.7 `uv pip install` fence; 2026/08 MiniMax Music 3 32 kHz stereo song and TTS refactor with Roadmap/blog links; 2026/06 MOSS-TTS Local v1.5 48 kHz and Higgs Audio v3); `About` (multi-stage decoding target; owned topology/lifecycle/transport/integration/API versus SGLang composition; stage list; scheduler and control-plane/relay-plane transport sentences; API-surface sentence); `What SGLang-Omni Serves` (Qwen3-Omni/Ming-Omni; MiniMax Music 3; 9-family speech-generation list plus `/v1/audio/speech`/batch/streaming/uploaded-voices note; 5-family transcription list plus `/v1/audio/transcriptions` and MOSS-TD `verbose_json` note; Router sentence); `Hardware Support` table (CUDA supported/full; Apple Silicon experimental MLX/MPS `install.sh` plus Qwen3-ASR guide; Intel XPU experimental Arc/XPU 4-family end-to-end with decode-graphs/multi-XPU note plus install guide and auto-detect note); `Quick Start` (macOS `./install.sh`, Installation/TTS/Qwen3-Omni/ASR/MOSS-TD/Router/Developer-reference links); `Community & Support` (contributor topics, Slack/developer-reference, organizational contact); `Acknowledgments` (SGLang ecosystem and open-model communities).
