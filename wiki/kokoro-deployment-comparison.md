---
type: Synthesis
title: Kokoro Deployment Comparison
description: Comparison of compiled Kokoro deployment routes across Python, dedicated APIs, native GGUF runtimes, voice-agent integrations, and Vietnamese PyTorch or ONNX artifacts.
tags: [tts, kokoro, deployment, comparison]
status: draft
created: 2026-10-15
generated: { by: llm-wiki-agent/1, at: 2026-10-15T10:59:14Z }
stale_after: 2027-04-15
sources:
  - id: library
    resource: kokoro-python-library.md
    kind: documentation
    title: Kokoro Python Library
  - id: fastapi
    resource: kokoro-fastapi.md
    kind: documentation
    title: Kokoro-FastAPI
  - id: performance
    resource: kokoro-fastapi-performance.md
    kind: documentation
    title: Kokoro-FastAPI Performance and Evaluation
  - id: speaches
    resource: speaches.md
    kind: documentation
    title: Speaches
  - id: packages
    resource: audio-cpp-gguf-packages.md
    kind: documentation
    title: audio.cpp GGUF Model Packages
  - id: native
    resource: audio-cpp-framework.md
    kind: documentation
    title: audio.cpp Framework
  - id: crisp
    resource: crispasr-tts-engines.md
    kind: documentation
    title: CrispASR TTS Engines
  - id: concurrency
    resource: crispasr-streaming-http-server.md
    kind: documentation
    title: CrispASR Streaming and HTTP Server
  - id: hf
    resource: speech-to-speech-pipeline.md
    kind: documentation
    title: HF Speech-to-Speech Pipeline
  - id: browser
    resource: speech-to-speech-browser-demo.md
    kind: documentation
    title: Speech-to-Speech Browser Demo
  - id: chat
    resource: realtime-voice-chat.md
    kind: documentation
    title: RealtimeVoiceChat
  - id: vi
    resource: kokoro-vietnamese.md
    kind: documentation
    title: Kokoro Vietnamese
  - id: model
    resource: kokoro-82m.md
    kind: documentation
    title: Kokoro-82M
  - id: distilled
    resource: sanotts.md
    kind: documentation
    title: sanoTTS
---

Kokoro deployment is not one choice: direct Python inference, an HTTP serving wrapper, a native C++ package, and a complete voice-agent pipeline occupy different layers. The compiled evidence supports the routes below, plus separate Vietnamese artifacts; it does not establish a fastest runtime or an exhaustive list of external projects. Capabilities remain **Reported**, recommendations are **Synthesis**, and none was execution-verified for this comparison.[^library][^fastapi][^packages][^crisp][^hf][^vi]

## Deployment routes

| Route | Documented deployment/interface | Selection rationale (Synthesis) | Important limit |
| --- | --- | --- | --- |
| Python kokoro | PyPI, KPipeline, per-segment 24 kHz audio; Windows/conda/Apple notes | Embed TTS in a Python app, batch generation, custom segmentation | Own the HTTP/concurrency/cancellation layer; README does not establish effective MPS device selection.[^library] |
| Kokoro-FastAPI | CPU/CUDA/experimental ROCm Docker, Compose, direct uv scripts, native Apple MPS; OpenAI-compatible speech API and WebUI | Dedicated Kokoro service with voice mixes, markup, captions | Extensions are outside OpenAI schema; CUDA latest-tag ambiguity; normalization can drop phrases.[^fastapi] |
| Speaches | CPU/GPU Docker or Compose; Kokoro/Piper TTS plus faster-whisper STT, dynamic load/offload, Realtime API | One STT/TTS API service | Overview only: precise API schema, license/version and benchmark unavailable.[^speaches] |
| audio.cpp | Kokoro-82M-GGUF, family kokoro_tts, BF16/Q8; shared native CLI/server/WebUI | Native multi-model audio deployment | CPU/CUDA/Vulkan/Metal are framework options, not proof of every Kokoro/backend combination or streaming support; no matched Kokoro timing.[^packages][^native] |
| CrispASR | kokoro backend, auto-download about 135 MB, CLI and OpenAI-compatible TTS HTTP surface | Native speech toolbox with easy Kokoro startup | README says all TTS is watermarked; inference serialized by default, no batched multi-stream inference. ASR worker claims do not prove TTS parallelism.[^crisp][^concurrency] |
| HF speech-to-speech | kokoro extra and --tts kokoro; local/serve pipeline, browser WebSocket/WebRTC integration | Complete VAD→STT→LLM→Kokoro conversation system | Pipeline wrapper, not another Kokoro checkpoint; browser is a server client, not browser-local model inference; one session per pipeline unit, scalable with --num_pipelines.[^hf][^browser] |
| RealtimeVoiceChat / RealtimeTTS | START_ENGINE=kokoro, Docker/manual Python, browser WebSocket audio and barge-in | Integrated conversation demo | Early preview, community-driven maintenance; source modules and exact engine behavior not inspected.[^chat] |
| Kokoro Vietnamese, PyTorch | Separate kokoro_vi.pth/config/voicepacks, vig2p, editable source install, kokoro-vietnamese CLI with CUDA example | Vietnamese finetune in PyTorch | No quality, timing, streaming, or concurrency evidence.[^vi] |
| Kokoro Vietnamese, ONNX | ONNX extra, kokoro-vietnamese-onnx CLI; CPU or CUDAExecutionProvider, export CLI | Vietnamese acoustic-model export via ONNX Runtime | Not documented as a drop-in for upstream Kokoro servers; no performance win demonstrated over PyTorch.[^vi] |

## Dedicated server hardware choices

Kokoro-FastAPI documents these distinct paths (**Reported**):[^fastapi]

- CPU Docker: linux/amd64 and linux/arm64.
- NVIDIA CUDA Docker: amd64/arm64; named CUDA variants include cu126 and cu128, but the latest-tag documentation conflicts with the arm64 cu129 statement. Inspect the manifest and pin a release before deployment.
- AMD ROCm Docker: experimental, linux/amd64, with /dev/kfd and /dev/dri.
- Apple Silicon: native ./start-gpu_mac.sh with MPS, not the CUDA Docker GPU image.
- Direct development run: CPU/GPU shell or Windows PowerShell scripts through uv.

## Performance cannot determine a winner

Only the dedicated FastAPI page supplies detailed Kokoro-serving timing here; these are vendor figures, not reproduced or matched against the other routes (**Reported**, **Unverified**).[^performance]

| Reported workload | Figure | Qualification |
| --- | --- | --- |
| NVIDIA GPU, chunk size 400 | about 300 ms first token | GPU unnamed; first-token timer not defined |
| Older i7 CPU, chunk size 200 | about 3.5 s first token | Not an end-to-end voice-turn measurement |
| M3 Pro CPU, chunk size 200 | under 1 s first token | Explicitly CPU, not an MPS benchmark |
| RTX 4060 Ti 16 GB, Windows/WSL2 long-form | 35–100× realtime speed reported | Source ratio wording is ambiguous; long-book rows support audio/wall interpretation |

The same RTX setup reports a roughly 2.37 GB loaded-process/CUDA-context floor even after unload, and roughly five seconds reload cost. Small weights do not establish total process VRAM (**Synthesis**). No evidence here supports ranking ONNX, Q8 GGUF, native C++, Python, and MPS by speed or fidelity.[^performance][^vi][^packages][^library]

## Selection guidance (Synthesis)

- **Default dedicated Kokoro HTTP service:** shortlist Kokoro-FastAPI for its documented platform paths and Kokoro-specific controls, not as a proven speed winner.[^fastapi]
- **Embedded Python or offline generation:** KPipeline avoids adding a separate server layer.[^library]
- **Combined STT and TTS service:** Speaches, pending target-version schema and operations validation.[^speaches]
- **Native/no Python inference process:** audio.cpp or CrispASR; test the exact runtime package and backend. GGUF is not universally interchangeable.[^native][^packages][^crisp]
- **Complete voice agent:** HF speech-to-speech; RealtimeVoiceChat is an alternative with an explicit maintenance warning.[^hf][^browser][^chat]
- **Vietnamese:** use the separate finetune and vig2p, then evaluate PyTorch versus ONNX on target hardware. Upstream KPipeline's eight-language list has no Vietnamese; upstream server support does not establish finetune compatibility.[^library][^vi][^fastapi]

## Related but insufficient routes

- **Managed APIs:** the model card mentions Replicate and DeepInfra in an April 2025 pricing snapshot. That evidence is past its recorded stale_after date and establishes neither current availability, price, deployment controls nor SLA; not a current hosted-provider comparison.[^model]
- **Browser/MCU distilled alternatives:** sanoTTS has Kokoro-distilled nano voices and WASM/MCU paths, but runs different, much smaller weights under GPLv3, not Kokoro-82M. Do not count it as the same model deployed to an ESP32.[^distilled]
- **Voice search rather than serving:** KVoiceWalk is linked from the model as a voice-tensor search tool, not another serving runtime.[^model]
- No compiled standalone upstream Kokoro ONNX/browser/Core ML/MLX runtime coverage was retrieved. This is a retrieval/coverage gap, not evidence that such projects do not exist.

## Relationships

- Compares deployment options for [Kokoro-82M](kokoro-82m.md) and distinguishes the separate [Kokoro Vietnamese](kokoro-vietnamese.md) artifacts.[^model][^vi]
- Uses [Kokoro-FastAPI Performance and Evaluation](kokoro-fastapi-performance.md) to keep timing, throughput and memory claims conditional.[^performance]

## Coverage and trust limits

- Wiki state: populated; initial structural check passed for 217 concepts. Retrieval used the root catalog, exact Kokoro search across wiki concepts, runtime/package and pipeline traversal; QMD was not needed.
- Inspected the cited compiled pages and relevant sections this session. No raw research, live web research, installation, model download, API execution, audio listening or benchmark ran.
- Citation sources are stable local concepts; inherit each concept's README-only, missing implementation/revision/configuration/weights, and unverified-capability limits. No claim of code-level support verification.
- Draft because external ecosystem completeness, current hosted-provider coverage, per-backend Kokoro parity and comparable target-hardware performance remain unresolved. Operational comparison is time-sensitive.
- Only public project/configuration identifiers and placeholder-free capability descriptions compiled; no sensitive values copied.

[^library]: [Kokoro Python Library](kokoro-python-library.md) — Install; Pipeline API; Languages and G2P; Contradictions; Coverage and limits.
[^fastapi]: [Kokoro-FastAPI](kokoro-fastapi.md) — Deployment paths; API surface; Known issues; Contradictions; Coverage and limits.
[^performance]: [Kokoro-FastAPI Performance and Evaluation](kokoro-fastapi-performance.md) — Streaming first-token latency; Throughput; VRAM unload and reload; Reading the figures.
[^speaches]: [Speaches](speaches.md) — Engines; Features (as listed); Coverage and limits.
[^packages]: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) — Files table, Kokoro-82M-GGUF row; Usage; Quality and licensing caveats.
[^native]: [audio.cpp Framework](audio-cpp-framework.md) — Distribution and model management; Interfaces: CLI, server, WebUI, pipelines; Performance and quantization.
[^crisp]: [CrispASR TTS Engines](crispasr-tts-engines.md) — Invocation; TTS feature matrix and engine notes; Coverage and limits.
[^concurrency]: [CrispASR Streaming and HTTP Server](crispasr-streaming-http-server.md) — HTTP server; Concurrency; Coverage and limits.
[^hf]: [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) — Installation; Supported components; Coverage and limits.
[^browser]: [Speech-to-Speech Browser Demo](speech-to-speech-browser-demo.md) — Local quick start; Transports and connection modes.
[^chat]: [RealtimeVoiceChat](realtime-voice-chat.md) — Identity and status; Configuration; Deployment and hardware; Coverage and limits.
[^vi]: [Kokoro Vietnamese](kokoro-vietnamese.md) — Artifact layout; Install and runtimes; Inference commands; Coverage and limits.
[^model]: [Kokoro-82M](kokoro-82m.md) — Market cost snapshot; Relationships; Contradictions; Coverage and limits.
[^distilled]: [sanoTTS](sanotts.md) — Two lineages, two graphs; Install and deployment paths; License.
