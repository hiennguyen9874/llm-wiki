---
type: Concept
title: CrispASR Build, GPU, and Operations
description: "Building, installing, and operating CrispASR: CMake build, prebuilt CUDA and Vulkan tarball fallback rules, GPU backend selection, KV-cache and GGUF memory controls, quantization, model caching, and debugging environment variables."
tags: [pipeline, build, gpu, quantization, edge-deployment, ggml, gguf, debugging]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:50:00Z }
stale_after: 2027-10-13
sources:
  - id: crispasr-readme
    resource: ../raw/CrispASR.md
    kind: documentation
    title: CrispASR README
---

CrispASR builds from source with CMake into `crispasr`, `crispasr-quantize`, and `crispasr-diff`, or it runs from prebuilt tarballs whose GPU fallback rules differ by build. Without an override it picks CUDA, then Metal, then Vulkan, then CPU. Memory can be cut with KV-cache quantization, mmap weights, and GGUF quantization. The README's operating claims were not run here (**Reported**).[^crispasr-readme]

## Build from source

- Clone with `git clone --recursive`. If the clone lacked `--recursive`, run `git submodule update --init --recursive`, because the bundled `ggml/` submodule is required (**Reported**).[^crispasr-readme]
- Configure and build: `cmake -B build -DCMAKE_BUILD_TYPE=Release`, then `cmake --build build -j$(nproc)`. Requirements are a C++17 compiler and CMake 3.14+, with no Python needed at runtime (**Reported**).[^crispasr-readme]
- GPU options at configure time: `-DGGML_CUDA=ON` (NVIDIA), `-DGGML_METAL=ON` (Apple Silicon), `-DGGML_VULKAN=ON` (cross-vendor). The build-flag list also names `-DGGML_CANN=ON` (**Reported**).[^crispasr-readme]
- `docs/install.md` covers CUDA, Metal, Vulkan, MUSA, and SYCL, the Windows scripts, ffmpeg ingestion, optional BLAS, and glibc notes. It was not captured (**Synthesis**).[^crispasr-readme]
- On Windows, `build-vulkan.bat` produces a separate Vulkan binary at `build-vulkan\bin\crispasr.exe` (**Reported**).[^crispasr-readme]

## Prebuilt binaries

Prebuilt names by platform and GPU (**Reported**).[^crispasr-readme]

- **Windows CPU:** `crispasr-windows-x86_64-cpu.zip` needs AVX2 (Intel 2013+ or AMD 2015+). Older CPUs use `…-cpu-legacy.zip` (**Reported**).[^crispasr-readme]
- **Windows CUDA:** `crispasr-windows-x86_64-cuda.zip` is self-contained and needs no CUDA Toolkit. `…-cuda126.zip` is the legacy CUDA 12.6 build for Pascal, Volta, and newer through Hopper. `…-cuda13.zip` is the CUDA 13-native build for Turing and newer. The standard `-cuda` build uses CUDA 12.8 and supports Blackwell (**Reported**).[^crispasr-readme]
- **macOS:** `crispasr-macos-arm64.tar.gz` (Metal and Accelerate) and `crispasr-macos-x86_64.tar.gz` (CPU and Accelerate, requires AVX2, FMA, and F16C). Older Intel Macs use `crispasr-macos-x86_64-cpu-legacy.tar.gz` (**Reported**).[^crispasr-readme]
- **Linux:** `crispasr-linux-x86_64.tar.gz`, with `…-cuda.tar.gz` or `…-vulkan.tar.gz` for GPU use (**Reported**).[^crispasr-readme]

Fallback rule: the `-hip` and `-vulkan` builds need the matching driver and do **not** fall back to CPU. The Linux `-cuda` tarballs do fall back, since v0.8.30. Do not mix CUDA 12.8 binaries with CUDA 12.6 DLLs. The CUDA 12.6 split packages need `cuda126-runtime.zip` from the same release, and the SHA-256 manifest should be used when reusing runtime DLLs (**Reported**).[^crispasr-readme]

Verify with `crispasr --version`. CUDA builds also print `cuda toolkit` and `cuda runtime ABI`, which distinguishes the CUDA 12 and 13 packages (**Reported**).[^crispasr-readme]

## GPU backend selection

- Default: `ggml_backend_init_best()` chooses CUDA, then Metal, then Vulkan, then CPU (**Reported**).[^crispasr-readme]
- `--gpu-backend vulkan` forces Vulkan. It does not select the physical GPU; `-dev N` does. On some Windows laptops Vulkan device 0 is the Intel iGPU and device 1 the NVIDIA GPU, so slow Vulkan results call for `-dev 1` (**Reported**).[^crispasr-readme]
- `-ng` forces CPU, which the README suggests for benchmarking. `CRISPASR_ARG_DEVICE=N` sets a default device index when `-dev` is absent (**Reported**).[^crispasr-readme]
- `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1` lets CUDA swap to RAM when VRAM runs out. `GGML_VK_VISIBLE_DEVICES` and `CUDA_VISIBLE_DEVICES` filter devices (**Reported**).[^crispasr-readme]
- A Vulkan caveat from the LID section: Silero LID is routed to CPU on Vulkan pending an upstream kernel fix (see [CrispASR VAD and Language Identification](crispasr-vad-language-id.md)) (**Reported**).[^crispasr-readme]

## Memory controls

- **KV-cache quantization:** `CRISPASR_KV_QUANT` accepts `f16`, `q8_0`, or `q4_0`. Per-half overrides `CRISPASR_KV_QUANT_K` and `CRISPASR_KV_QUANT_V` allow asymmetric settings; the README's recipe K=q8_0, V=q4_0 is said to save about 40% more KV memory than symmetric Q8_0. CTC-style backends without a KV cache do not apply (**Reported**).[^crispasr-readme]
- **mmap weights:** `CRISPASR_GGUF_MMAP=1` applies to backends that use `core_gguf::load_weights()`. Whisper uses upstream's loader and is unaffected (**Reported**).[^crispasr-readme]

## Quantization

- `crispasr-quantize input.gguf output.gguf q4_k` re-quantizes GGUF files across the supported families. The per-backend recommendations are in `docs/quantize.md`, which was not captured (**Reported**).[^crispasr-readme]
- Size points from the README: Canary-180M-Flash Q5_K_M is the smallest quant validated for both ASR and translation. MiMo-ASR's Q4_K (4.5 GB) is recommended over F16 (14.9 GB, about 16 GB RAM at inference). Wav2vec2 Q4_K is 212 MB, 6× smaller than F16 (**Reported**).[^crispasr-readme]
- On CPU the README advises Q4_K or Q5_K to reduce memory and compute (**Reported**).[^crispasr-readme]

## Model acquisition and caching

- `-m auto` downloads the model on first use into `~/.cache/crispasr/` (on Windows, `%USERPROFILE%\.cache\crispasr`) (**Reported**).[^crispasr-readme]
- `--dry-run-resolve` prints which model files would open and whether they are on disk, without loading anything (**Reported**).[^crispasr-readme]
- Gated models use `HF_TOKEN`, with `HUGGING_FACE_HUB_TOKEN` as the fallback. The README gives only the variable names, and this concept records no token value (**Reported**).[^crispasr-readme]

## Debugging and diagnostics

- `-v` or `--verbose` prints per-stage timings and device picks. For library use, `CRISPASR_VERBOSE=1` does the same (**Reported**).[^crispasr-readme]
- Per-backend families follow one pattern: `*_BENCH=1` for per-stage timings, `*_DEBUG=1` for per-step prints, and `*_DUMP_DIR` for F32 stage dumps used by `crispasr-diff`. `CRISPASR_DUMP_DIR` is the generic dump, and `CRISPASR_SCHED_PROFILE=1` reports scheduler time by op, with relative shares only (**Reported**).[^crispasr-readme]
- A run that prints its banner and then stops with no error and no output file is a crash, not a refusal. The README points to `docs/troubleshooting.md` and the exit code, which was not captured (**Reported**).[^crispasr-readme]
- Benchmark rule: measure transcribe time, not cold start, using server or in-process repetitions (`docs/benchmarking.md`, not captured) (**Reported**).[^crispasr-readme]

## Regression and contribution

- `tools/test-all-backends.py` runs the capability-tier matrix. Its cache modes are `keep` and `ephemeral`, and `--skip-missing` suits CI (**Reported**).[^crispasr-readme]
- `crispasr-diff` compares stage tensors against PyTorch ground truth. The README also names a TTS audio-cosine regression target. Adding a backend takes five files (**Reported**; contributing docs not captured).[^crispasr-readme]

## CPU operations

- On CPU-only hardware the README prefers moonshine, fc-ctc, parakeet, or whisper, and warns that audio-LLM backends can be far slower (see [CrispASR ASR Backend Selection](crispasr-asr-backend-selection.md)) (**Reported**).[^crispasr-readme]
- For progressive output on slow CPUs, use `--flush-after 1` and `-pp` for progress (see [CrispASR Streaming and HTTP Server](crispasr-streaming-http-server.md)) (**Reported**).[^crispasr-readme]

## Coverage and limits

- Not captured and therefore unverified: `docs/install.md`, `docs/troubleshooting.md`, `docs/quantize.md`, `docs/benchmarking.md`, `docs/contributing.md`, `docs/regression-matrix.md`, `docs/architecture.md`, `PERFORMANCE.md`, and `LEARNINGS.md` (**Synthesis**).[^crispasr-readme]
- Build, run, and version commands are transcribed, not executed. The v0.8.30 fallback change is a README statement that was not checked against release notes (**Synthesis**).[^crispasr-readme]
- No binary, GPU, or model was used. The memory percentages and the 4.5 GB and 14.9 GB sizes are README figures and were not reproduced (**Synthesis**).[^crispasr-readme]

## Relationships

- Sibling runtime: [audio.cpp Framework](audio-cpp-framework.md) is a separate native build with its own CUDA, Vulkan, and Metal paths; the two build systems are not compared here (**Synthesis**).
- Part of: [CrispASR](crispasr.md) (**Synthesis**).

[^crispasr-readme]: [CrispASR README](../raw/CrispASR.md) — locators: `Install & build` (clone, submodule note, cmake commands, GPU flags, `docs/install.md` pointer, troubleshooting pointer); `Start here` §1 "Get the binary" table and CUDA/Windows notes, §3 and `If nothing happened` (`--dry-run-resolve`, crash paragraph); `Table of contents` prebuilt-tarball and troubleshooting bullets (v0.8.30 note); `GPU backend selection` (default selection, `--gpu-backend`, `-dev`, `-ng`, unified memory, `build-vulkan.bat`, build-flags line); `Quantize models`; `Debugging & profiling` (`-v`, `CRISPASR_VERBOSE`, per-backend env table, HF token note); `CPU performance tips`; `Architecture, contributing, regression matrix`; `Feature matrix` memory notes (KV quant, mmap); `Quick start` (Canary-180M Flash, MiMo-ASR, Wav2Vec2 size notes); `Model caching` in `Start here` §2 (`~/.cache/crispasr/`).
