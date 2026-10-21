---
type: Concept
title: parakeet.cpp
description: MIT-licensed C++17/ggml port of NVIDIA NeMo Parakeet and Nemotron ASR with GGUF models, CPU/CUDA/Metal/Vulkan backends, CLI, OpenAI-style example server, a flat C API (ABI 10), reported 1.1x–1.7x CPU speedups over NeMo, and WER-0 parity claims.
tags: [stt, asr, parakeet, ggml, gguf, edge-deployment, streaming, cpp]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T12:00:00Z }
stale_after: 2027-04-21
sources:
  - id: parakeet-cpp-readme
    resource: ../raw/mudler-parakeet.cpp.md
    kind: documentation
    title: mudler/parakeet.cpp README
---

parakeet.cpp (`mudler/parakeet.cpp`, by the LocalAI team) is a C++17/ggml inference engine that ports NVIDIA NeMo's Parakeet speech-recognition models to self-contained GGUF files with no Python at inference time, running on CPU and on CUDA, Metal, and Vulkan backends. The README claims transcripts match NeMo (WER 0) on every published NVIDIA checkpoint and reports CPU speedups of 1.11x–1.69x over NeMo's PyTorch runtime (**Reported**).[^parakeet-cpp-readme] Its VAD, bundle, diarization, sound-event, and speaker features are covered in [parakeet.cpp Bundles, VAD, Diarization and Scene Stream](parakeet-cpp-bundle-vad-scene.md).

## Identity

- Repository `mudler/parakeet.cpp`, MIT license for the code; model weights keep each original license; GGUF models are hosted at `mudler/parakeet-cpp-gguf`; author Ettore Di Giacinto, "Brought to you by the LocalAI team" (**Reported**).[^parakeet-cpp-readme]
- Latest tagged release at capture: v0.5.0 (2026-08-01); entries dated 2026-09-28 to 2026-10-05 are on `master` only and need a source build or the `:latest` Docker images (**Reported**).[^parakeet-cpp-readme]
- LocalAI embeds it as its `parakeet-cpp` backend; the README points production use there rather than at the example server (**Reported**).[^parakeet-cpp-readme]
- The capture is undated; its newest "what is new" entry is 2026-10-05, so it is at least that recent (**Synthesis**).[^parakeet-cpp-readme]

## Supported models

All are published as GGUF (ASR models in f16, q8_0, q6_k, q5_k, q4_k). NVIDIA models are stated to be validated at WER 0 against NeMo; the Moondream derivatives are not (**Reported**).[^parakeet-cpp-readme]

| Model | Type | Size | Note |
| --- | --- | --- | --- |
| parakeet-tdt_ctc-110m | hybrid TDT+CTC | 110M | English; small anchor checkpoint |
| [parakeet-ctc-0.6b](parakeet-ctc-0.6b.md), [parakeet-ctc-1.1b](parakeet-ctc-1.1b.md) | CTC | 0.6B, 1.1B | English |
| [parakeet-rnnt-0.6b](parakeet-rnnt-0.6b.md), [parakeet-rnnt-1.1b](parakeet-rnnt-1.1b.md) | RNNT | 0.6B, 1.1B | English |
| [parakeet-tdt-0.6b-v2](parakeet-tdt-0.6b-v2.md), parakeet-tdt-1.1b | TDT | 0.6B, 1.1B | English |
| [parakeet-tdt-0.6b-v3](parakeet-tdt-0.6b-v3.md) | TDT | 0.6B | 25 European languages |
| parakeet-tdt_ctc-1.1b | hybrid TDT+CTC | 1.1B | English |
| [parakeet_realtime_eou_120m-v1](parakeet-realtime-eou-120m-v1.md) | RNNT streaming | 120M | cache-aware streaming with end-of-utterance events (`--stream`) |
| [nemotron-3.5-asr-streaming-0.6b](nemotron-3.5-asr-streaming-0.6b.md) | RNNT streaming | 0.6B | 40+ locales, `--lang` default `auto`, offline and streaming; OpenMDW-1.1 |
| [Parakeet Ultra](parakeet-ultra.md), [Parakeet Redux](parakeet-redux.md) | TDT + VAD head | 0.6B | Moondream derivatives of v3; CC-BY-4.0; Redux is CPU-only and offline-only |

Diarization, VAD, CED, and speaker models are in the companion page. Own checkpoints convert with `scripts/convert_parakeet_to_gguf.py` and quantize with `parakeet-cli quantize` (q4_0, q5_0, q8_0, q4_k, q5_k, q6_k) (**Reported**; the linked conversion and quantization docs are not in `raw/`).[^parakeet-cpp-readme]

## Interfaces

- **CLI `parakeet-cli`:** `info`, `transcribe` (offline default decoder; `--decoder ctc|tdt`; `--timestamps`/`--json` with word times and confidence; `--beam-size`/`--nbest` TDT N-best; `--stream` for EOU and Nemotron models; `--lang`; `--input -` reads WAV from stdin), plus `vad`, `scene`, `enroll`, `quantize`, `bench`, `bench-decode`, `bench-batch` (**Reported**).[^parakeet-cpp-readme]
- **Device selection:** automatic, first GPU the ggml registry reports; `PARAKEET_DEVICE=cpu` forces CPU, or a device name such as `CUDA0`/`Vulkan1`; ops a backend lacks run on CPU (**Reported**).[^parakeet-cpp-readme]
- **Server `parakeet-server`:** OpenAI-compatible `POST /v1/audio/transcriptions`; one model, one request at a time, WAV uploads only, described as an example. Images `ghcr.io/mudler/parakeet.cpp-cli` and `-server` are published on every `master` push (CPU and CUDA; amd64 and arm64) (**Reported**).[^parakeet-cpp-readme]
- **C API `include/parakeet_capi.h`:** flat, exception-free, for `dlopen`/FFI/LocalAI; built with `-DPARAKEET_SHARED=ON`. Covers offline and streaming transcription (text or JSON with word/token timestamps), batched transcription, VAD, diarization, speaker-attributed ASR, sound events, scene stream, speaker identification, bundle loading, and the concurrency pool. ABI version **10**; later additions are additive; LocalAI depends on the transcription symbols, so their signatures need a coordinated bump to change (**Reported**).[^parakeet-cpp-readme]
- **Batching and concurrency:** CPU batched transducer decode gives the same tokens as per-clip decode; an opt-in pool of CPU backends lets several requests run on one model (**Reported**).[^parakeet-cpp-readme]

## Build and deployment

- `git clone --recursive`, then `cmake -B build && cmake --build build -j`; `-DGGML_NATIVE=OFF` for a portable binary (**Reported**).[^parakeet-cpp-readme]
- GPU flags: `PARAKEET_GGML_CUDA` (release binaries for Turing sm_75+, benchmarked on a GB10), `PARAKEET_GGML_METAL` (macOS arm64, benchmarked on M4), `PARAKEET_GGML_VULKAN` (Linux/Windows; needs the Vulkan loader), `PARAKEET_GGML_HIP` (forwarded to ggml, untested). GPU backends are not exercised in CI (**Reported**).[^parakeet-cpp-readme]
- Other options: `PARAKEET_BUILD_TESTS` (off), `PARAKEET_BUILD_CLI`/`SERVER` (on), `PARAKEET_SHARED` (off), `PARAKEET_WITH_CED` and `PARAKEET_WITH_VOICEDETECT` (on) (**Reported**).[^parakeet-cpp-readme]
- Releases ship Linux x64 (cpu, vulkan, cuda), Linux arm64 (cpu, vulkan), macOS arm64 (metal), macOS x64 (cpu), Windows x64 (cpu, vulkan, cuda), AppImages and library tarballs; Windows CUDA needs the separate `cudart-parakeet-bin-win-cuda-x64.zip` unless the toolkit is installed (**Reported**).[^parakeet-cpp-readme]
- A community iOS demo (`Kashif-E/parakeet-ios-demo`) streams on-device through the streaming C API; not maintained by the core team (**Reported**).[^parakeet-cpp-readme]

## Benchmarks (reported)

RTFx is audio seconds over processing seconds against NeMo's PyTorch runtime, batch size 1. CPU runs used 8 threads on a 20-core x86 host; GPU runs used one NVIDIA GB10; both are shared development machines, not quiet lab hosts (**Reported**).[^parakeet-cpp-readme]

| Measurement | Result |
| --- | --- |
| CPU f32, 10 models, LibriSpeech test-clean | 1.11x–1.69x faster than NeMo (mean 1.40x), same transcripts |
| CPU q8_0 | mean 1.56x, up to 1.89x; 37% of f32 size |
| GPU (GB10) f32 | median 1.25x, up to 4.3x (`tdt_ctc-110m`); smallest gain (~1.2x) on CTC models |
| Nemotron 3.5, one 7.4 s clip, CPU | 2.40x f32, 2.52x q8_0 |
| Batched decode, batch 16 | ~10–12x on GB10 (f16); ~3–5x on CPU (q5_k) |
| Apple M4, Metal vs CPU | 1.3x–5.6x, most on 0.6B and 1.1B models |
| Redux packed ternary vs same model in F16 (CPU) | median RTF 75.6 vs 46.1 per utterance (8 threads, AVX-512 VNNI); 6.8x smaller file; WER 1.96% on 100 LibriSpeech utterances |
| Peak RAM vs NeMo | ~2x lower at f32 (2582 MB vs 5598 MB on `tdt-0.6b-v3`) |

Demo-clip claims (≈1.5x NeMo on CPU, ≈12x whisper.cpp turbo on GPU, ≈27x on CPU) are described by the README itself as single-clip demos, not benchmarks (**Reported**).[^parakeet-cpp-readme]

## Limits

- GPU encoder kernels are open work: ggml's generic CUDA convolution and attention kernels trail NeMo's tuned cuDNN (**Reported**).[^parakeet-cpp-readme]
- Batching does not apply to standalone CTC models; on CPU batched decode is bit-identical, on GPU it agrees to about 1e-4 and the batched encoder is close to, not equal to, single-clip (**Reported**).[^parakeet-cpp-readme]
- Concurrency uses CPU backends only, can be slower than one backend on large models, and costs more memory per backend (**Reported**).[^parakeet-cpp-readme]
- `parakeet-server` is one model, one request, WAV only; Redux is CPU/offline only; non-x86/dotprod targets use a slow scalar ternary kernel (**Reported**).[^parakeet-cpp-readme]
- Licenses: most NVIDIA Parakeet models CC-BY-4.0; `nemotron-3.5-asr-streaming` and Nemotron-3-Diarization OpenMDW-1.1; `parakeet_realtime_eou_120m-v1` NVIDIA Open Model License; Silero files MIT; Moondream models CC-BY-4.0 with attribution and "converted copy" notes (**Reported**).[^parakeet-cpp-readme]

## Relationships

- Ports [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) and the other NVIDIA checkpoints in the model table to ggml/GGUF; those pages cover model training and accuracy, while this page covers the runtime (**Synthesis**).
- Alternative runtime to the ONNX-based [Parakeet ASR Server](parakeet-asr-server.md) (Go and ONNX Runtime) and to the multi-model ggml engines [audio.cpp Framework](audio-cpp-framework.md) and [CrispASR](crispasr.md); the audio.cpp maintainer recommends parakeet.cpp for Parakeet, and reports Nemotron 3.5 output on audio.cpp matching it (see [audio.cpp ASR Benchmarks and Field Reports](audio-cpp-asr-benchmarks-and-field-reports.md)) (**Reported**, **Synthesis**).
- Appears as the "parakeet.cpp (ggml)" baseline (q8_0 45x, f16 rows) in Moondream's Photon benchmarks in [Parakeet Redux](parakeet-redux.md); that table's vendor-run figures and this README's own Redux figures use different engines, hardware, and metrics and are not directly comparable (**Synthesis**).
- Runs the VAD in [Silero VAD](silero-vad.md) and diarization from [Nemotron 3 Diarization](nemotron-3-diarization.md) (details in the companion page).
- Surveyed with other ASR options in [ASR/STT Model Survey](asr-stt-model-survey.md).
- Voice-loop fit (**Synthesis**): the `--stream` EOU and Nemotron 3.5 modes, the C API streaming symbols, and the ggml CPU/GPU portability make it a candidate STT stage for edge voice agents; the README gives no end-to-end latency, first-token, or endpointing-delay measurements, so that fit is unmeasured.

## Coverage and limits

- Single README capture inspected statically (all sections, tables, code fences, and the "What is new" list); no build, model download, transcription, or benchmark was executed, so every speed, size, WER-parity, and RTF figure is **Reported** and unverified (**Synthesis**).[^parakeet-cpp-readme]
- Not in `raw/` and not inspected: `docs/` pages (cli, capi, parity, performance, quantization, conversion, docker, licenses, concurrency, batching, tdt-nbest), `benchmarks/BENCHMARK.md` and plots, `AGENTS.md`, source code, tests, `LICENSE`, GIF/MP4 demos, and Hugging Face model cards. Per-model WER-0 parity and per-type quantization WER therefore have no locator beyond the README's assertions (**Synthesis**).[^parakeet-cpp-readme]
- Excluded as decorative or promotional: badges, demo videos, LocalAI star request, BibTeX block (citation: Di Giacinto and Palethorpe, 2026) (**Synthesis**).
- Time-sensitive: release status, ABI version, and benchmark figures carry `stale_after: 2027-04-21` under the `stt` domain rule.

[^parakeet-cpp-readme]: [mudler/parakeet.cpp README](../raw/mudler-parakeet.cpp.md) — locators: intro and `What is new` (v0.5.0 date, master-only entries, LocalAI backend); `Models` table; `CLI cheat sheet` and device-selection paragraph; `Server and Docker`; `C API` (Surface and ABI bullets); `Build` (GPU backend table, option table, pre-built binaries); `Benchmarks` table and surrounding paragraphs; `Limits` bullets; `Contributing` (community projects); `License and credits`.
