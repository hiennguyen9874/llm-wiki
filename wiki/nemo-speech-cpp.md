---
type: Concept
title: NeMo-Speech.cpp
description: NVIDIA's official native C++ ggml runtime for local Nemotron speech inference with streaming ASR/TTS, diarization, translation, VoiceChat serving, CLI/server/C-SDK paths, and published RTX 4090/CPU latency figures.
tags: [pipeline, stt, tts, vad, diarization, streaming, gguf, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:18:00Z }
stale_after: 2027-10-06
sources:
  - id: nemo-speech-readme
    resource: ../raw/NeMo-Speech.cpp.md
    kind: documentation
    title: NeMo-Speech.cpp README
  - id: nemo-speech-cpp-docs
    resource: ../raw/nemo-speech-cpp-docs/README.md
    scope: ../raw/nemo-speech-cpp-docs/
    kind: documentation
    revision: 8642eaa5cc51efbc17ad0f3e433944ba858a873f
    title: NVIDIA/NeMo-Speech.cpp supporting docs
---

NeMo-Speech.cpp is NVIDIA's official native C++ runtime for local inference across the Nemotron speech family, offering day-0 support for models from NVIDIA NeMo Speech with ggml-powered execution across streaming ASR, diarization, translation, TTS, speech processing, and full-duplex VoiceChat behind CLI, local HTTP/WebSocket server, Riva gRPC, and C-SDK paths (**Reported**).[^nemo-speech-readme]

## Runtime identity and scope

- Stated positioning is a lightweight native C++ runtime with broad hardware support; upstream is `NVIDIA/NeMo-Speech.cpp` with ggml as the inference engine (**Reported**).[^nemo-speech-readme]
- NVIDIA-authored code is under Apache License 2.0 with the project copyright in `NOTICE`; third-party components keep their own terms in `THIRD_PARTY_NOTICES.md`, also shipped under `share/licenses/nemo-speech/` in release archives (**Reported**).[^nemo-speech-readme]
- External contributions are accepted under the `CONTRIBUTING.md` terms with Developer Certificate of Origin sign-off (**Reported**).[^nemo-speech-readme]

## Supported applications and models

All rows below are source assertions from the `Models and applications` table; Hugging Face pages and checkpoints were not fetched for this wiki (**Synthesis**).[^nemo-speech-readme]

| Application | Models named in source |
| --- | --- |
| Speech recognition | [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md), [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md), [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md), [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md) |
| Speaker diarization | [Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md) and [Nemotron 3 Diarization](nemotron-3-diarization.md), standalone or combined with ASR |
| Text and speech translation | Riva Translate 4B Instruct v2, with composed ASR-to-NMT-to-TTS speech translation (no wiki concept for this checkpoint yet) |
| Speech synthesis | MagpieTTS Multilingual 357M with NeMo NanoCodec at 22 kHz / 1.89 kbps / 21.5 fps (no wiki concept for either yet) |
| Full-duplex voicechat | [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md), including realtime audio, transcripts, and tool calling |
| Speech processing | [Silero VAD](silero-vad.md), punctuation and capitalization, endpointing, text normalization, and subtitles |

## Performance (Reported, Q8_0 vendor figures)

- Headline claims: ASR transcribes in 160 ms chunks up to 67x faster than realtime; TTS generates up to 60x faster than realtime with first audio under 10 ms; both stay faster than realtime even on CPU (**Reported**).[^nemo-speech-readme]
- Streaming ASR with Nemotron Speech Streaming 0.6B (Q8_0), 160 ms chunks (**Reported**):[^nemo-speech-readme]

| Device | Latency per chunk | Throughput | Speedup over NeMo (FP32) |
| --- | --- | --- | --- |
| GeForce RTX 4090 | 2.3 ms | 67x realtime | 8.8x |
| CPU | 27 ms | 6x realtime | 3.7x |

- Streaming TTS with MagpieTTS Multilingual (Q8_0), 186 ms audio chunks (**Reported**):[^nemo-speech-readme]

| Device | Time to first audio | Inter-chunk latency | Throughput | Speedup over NeMo (FP32) |
| --- | --- | --- | --- | --- |
| GeForce RTX 4090 | 9 ms | 3 ms | 60x realtime | 40x |
| CPU | 203 ms | 64 ms | 2.7x realtime | 9.7x |

- Methodology and further results are delegated to `BENCHMARK.md`, which was not inspected; device/CPU identity, power, thread, and batch conditions are not stated in the captured README (**Synthesis**).[^nemo-speech-readme]

## Install, quick start, and CLI

- The source recommends building natively from source for best performance; tagged releases can trail `main`, and a daily-rebuilt nightly prerelease is available via `--channel nightly` (`-Channel nightly` on Windows) (**Reported**).[^nemo-speech-readme]
- Installer: `curl -fsSL https://github.com/NVIDIA/NeMo-Speech.cpp/raw/main/scripts/install.sh | sh` on Linux/macOS (reopen shell for `PATH`), and `irm .../scripts/install.ps1 | iex` on Windows PowerShell; it downloads the prebuilt archive for the latest release, verifies it against the published SHA-256 checksum, and builds from source when no archive exists for the platform; `--source` (`-Source`) forces a `main`-branch source build requiring Git, CMake 3.26+, Ninja, a C++17 compiler, SentencePiece development files, and any backend toolchain (**Reported**).[^nemo-speech-readme]
- Quick start: `nemo-speech transcribe /path/to/audio.wav` downloads the pinned default Nemotron 3.5 GGUF from Hugging Face on first use and verifies size plus SHA-256; source checkouts can smoke-test with `test_files/asr/wav/test/jfk.wav`; `nemo-speech transcribe --live` uses the default microphone on builds with live capture (**Reported**).[^nemo-speech-readme]
- Model selection: `nemo-speech model list` shows defaults, short names, and per-command usage; `nemo-speech pull nemotron-en` pre-downloads the English-only model and `--model nemotron-en` selects it; local GGUF paths work without downloads; the CLI picks an available backend and handles common mono/stereo PCM WAV sample rates automatically (**Reported**).[^nemo-speech-readme]
- The CLI is the primary interface (`nemo-speech --help` lists build capabilities); the CLI guide covers model selection, GPU controls, directory transcription, subtitles, diarization, NMT, TTS, structured output, and benchmarking, and a separate VoiceChat guide covers building and serving the realtime pipeline — neither guide was fetched (**Reported**, with unfetched-pointer limit).[^nemo-speech-readme]

## Server, SDK, and source build

- Local server and playground: `nemo-speech serve --asr-model nemotron-3.5 --open` binds `http://127.0.0.1:8080` by default; transcription and speech routes expose documented OpenAI-compatible subsets plus realtime WebSocket transcription and realtime VoiceChat when its model is loaded; a separately built `riva_server` binary provides the ASR, TTS, and translation gRPC interfaces (**Reported**).[^nemo-speech-readme]
- Native SDK: release archives ship stable C headers, shared libraries, and an exported CMake package; an installed app links only the capability it uses, e.g. `find_package(NeMoSpeech REQUIRED COMPONENTS ASR)` plus `target_link_libraries(my_app PRIVATE NeMoSpeech::ASR)` (**Reported**).[^nemo-speech-readme]
- Source build requirements are CMake 3.26+, Ninja, C and C++17 compilers, SentencePiece development files, plus the selected backend toolchain; the CUDA ASR/TTS server example runs `git submodule update --init llama.cpp third_party/cpp-httplib`, `scripts/configure.sh cuda-server`, and `cmake --build --preset cuda-server`, where the configure helper validates submodules and applies the pinned ggml patch series for CUDA builds; CPU, Metal, Vulkan, server, component, Windows, and container variants live in the unfetched build guide (**Reported**, with unfetched-pointer limit).[^nemo-speech-readme]
- The captured README maps 11 follow-on documents (install, CLI, model conversion, S2S VoiceChat, servers, HTTP API, native SDK, client integration, troubleshooting, source build, docs index); none was fetched for the first capture, so conversion, endpoint, ABI-lifetime, threading, and troubleshooting detail is absent from this concept (**Synthesis**).[^nemo-speech-readme]
- A later capture supplies `docs/server.md`, `docs/api.md`, `docs/asr/configuration.md`, `docs/asr/models.md`, and `docs/clients.md` at upstream revision `8642eaa5cc51efbc17ad0f3e433944ba858a873f`; the server/listener operations, HTTP and realtime contracts, recognizer keys, and model/quantization roster are compiled as [NeMo-Speech.cpp Server and Deployment](nemo-speech-server.md), [NeMo-Speech.cpp HTTP and Realtime API](nemo-speech-http-api.md), [NeMo-Speech.cpp ASR Configuration](nemo-speech-asr-configuration.md), and [NeMo-Speech.cpp ASR Models and Quantization](nemo-speech-asr-models.md), while conversion, SDK-ABI, threading, and troubleshooting remain unfetched (**Reported**).[^nemo-speech-cpp-docs]

## Relationships

- Serves: [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md), [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md), [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md), and [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md) are the ASR checkpoints this runtime names; those pages hold the model-level WER, language, and checkpoint detail while this page holds the runtime path (**Synthesis**).[^nemo-speech-readme]
- Serves: [Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md) and [Nemotron 3 Diarization](nemotron-3-diarization.md) are the diarization checkpoints this runtime names for standalone or ASR-combined use (**Synthesis**).[^nemo-speech-readme]
- Serves: [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md) is the full-duplex checkpoint this runtime names for realtime audio, transcripts, and tool calling; that page holds the model-level latency and benchmark detail (**Synthesis**).[^nemo-speech-readme]
- Uses: [Silero VAD](silero-vad.md) is the named VAD component of this runtime's speech-processing group alongside endpointing, punctuation/capitalization, text normalization, and subtitles (**Synthesis**).[^nemo-speech-readme]
- Documented by: [NeMo-Speech.cpp Server and Deployment](nemo-speech-server.md), [NeMo-Speech.cpp HTTP and Realtime API](nemo-speech-http-api.md), [NeMo-Speech.cpp ASR Configuration](nemo-speech-asr-configuration.md), and [NeMo-Speech.cpp ASR Models and Quantization](nemo-speech-asr-models.md) compile this runtime's captured supporting docs — server/listener operations, HTTP and realtime contracts, recognizer keys, and the model/quantization roster — and hold that operational detail (**Synthesis**).[^nemo-speech-cpp-docs]
- Contrasts with: [audio.cpp Framework](audio-cpp-framework.md) is the community ggml-based multi-family audio runtime in this wiki; NeMo-Speech.cpp is NVIDIA's official single-vendor Nemotron-family runtime instead — compare them when choosing between official Nemotron day-0 support and broad multi-family coverage (**Synthesis**).[^nemo-speech-readme]
- Adjacent pipeline context: [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) and [RealtimeVoiceChat](realtime-voice-chat.md) cover alternative VAD → STT → LLM → TTS orchestration; NeMo-Speech.cpp covers the native-runtime plus VoiceChat-model path (**Synthesis**).[^nemo-speech-readme]

## Coverage and limits

- Source inspected statically only; no installer ran, nothing compiled, no model or GGUF downloaded, no audio transcribed or synthesized, and no latency, throughput, or speedup figure reproduced — all performance claims are vendor assertions under the source's unstated setup (**Synthesis**).[^nemo-speech-readme]
- Snapshot has no stated commit revision or capture date; treat model defaults, nightly-channel behavior, and benchmark numbers as time-sensitive (**Synthesis**).[^nemo-speech-readme]
- Referenced but unfetched and absent from `raw/`: `BENCHMARK.md`, `docs/install.md`, `docs/cli.md`, `docs/model-conversion.md`, `docs/s2s/README.md`, `docs/s2s/clients.md`, `docs/sdk.md`, `docs/troubleshooting.md`, `docs/build.md`, `docs/README.md`, `scripts/install.sh`, `scripts/install.ps1`, `scripts/configure.sh`, Hugging Face checkpoint pages, and sample audio; install and inference fences are transcribed, not executed (**Synthesis**).[^nemo-speech-readme]
- The `raw/nemo-speech-cpp-docs/` capture contributes `docs/server.md`, `docs/api.md`, `docs/asr/configuration.md`, `docs/asr/models.md`, and `docs/clients.md`; their SHA-256 digests were re-computed to match the capture manifest (**Observed** for capture integrity), and their content is **Reported** on the four linked supporting concepts (**Synthesis**).[^nemo-speech-cpp-docs]
- Riva Translate 4B Instruct v2, MagpieTTS Multilingual 357M, and NeMo NanoCodec have no wiki concepts yet; translation-quality, TTS-quality, and codec-fidelity claims are therefore not covered here (**Synthesis**).[^nemo-speech-readme]
- Release and benchmark figures carry `stale_after: 2027-10-06` per `SCOPE.md` domain rules for `pipeline`, `stt`, `tts`, and `vad` (**Synthesis**).[^nemo-speech-readme]

[^nemo-speech-cpp-docs]: [NVIDIA/NeMo-Speech.cpp supporting docs](../raw/nemo-speech-cpp-docs/README.md) — capture at upstream revision `8642eaa5cc51efbc17ad0f3e433944ba858a873f` (2026-10-07) with a five-document coverage ledger; locators: `docs/server.md`, `docs/api.md`, `docs/asr/configuration.md`, `docs/asr/models.md`, `docs/clients.md` (compiled into the four linked supporting concepts), and package `README.md` (coverage ledger; root README and `docs/{tts,nmt,s2s,development}/` plus build/install/cli/sdk/troubleshooting docs excluded).

[^nemo-speech-readme]: [NeMo-Speech.cpp README](../raw/NeMo-Speech.cpp.md) — locators: header tagline (official local-speech solution, day-0 NeMo Speech support, ggml); `Models and applications` table (ASR 4 checkpoints; diarization 2 checkpoints standalone/combined; Riva Translate 4B Instruct v2 ASR-to-NMT-to-TTS; MagpieTTS 357M + NanoCodec 22 kHz/1.89 kbps/21.5 fps; VoiceChat 11B realtime audio/transcripts/tool calling; Silero VAD + PnC/endpointing/normalization/subtitles); `Performance` (160 ms chunks, 67x ASR / 60x TTS / <10 ms first audio / faster-than-realtime on CPU; ASR Q8_0 table 4090 2.3 ms/67x/8.8x and CPU 27 ms/6x/3.7x; TTS Q8_0 table 4090 9 ms/3 ms/60x/40x and CPU 203 ms/64 ms/2.7x/9.7x; `BENCHMARK.md` pointer); `Installation` + `IMPORTANT` callout (native-build recommendation, tagged-vs-`main` lag, `--channel nightly` daily rebuild; `install.sh`/`install.ps1` fences, `PATH` reopen, SHA-256 check, source fallback, `--source`/`-Source`, Git/CMake-3.26+/Ninja/C++17/SentencePiece/backend prerequisites); `Quick start` (`transcribe` WAV fence, pinned Nemotron 3.5 GGUF size+SHA-256 download, `test_files/asr/wav/test/jfk.wav`, `--live` mic, `model list`/`pull nemotron-en`/`--model`, local GGUF paths, backend selection, PCM WAV rates); `Command line` (primary interface, `--help`, CLI-guide scope, VoiceChat-guide pointer); `Local server and playground` (`serve --asr-model nemotron-3.5 --open`, `127.0.0.1:8080`, OpenAI-compatible subsets, realtime WebSocket transcription/VoiceChat, `riva_server` gRPC); `Native SDK` (C headers/shared libs/CMake package, `find_package(NeMoSpeech ... ASR)` fence); `Build from source` (requirements, `cuda-server` submodule/configure/build fences, ggml patch series, CPU/Metal/Vulkan/server/component/Windows/container pointer); `Documentation` 11-row table; `License` (Apache-2.0, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `share/licenses/nemo-speech/`); `Contributing` (`CONTRIBUTING.md`, DCO sign-off).
