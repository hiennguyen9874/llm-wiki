---
type: Concept
title: CrispASR
description: Unified C++ ggml speech engine forked from whisper.cpp, shipping one CLI and binary for ASR, TTS, translation, and speech-processing backends selected by flag or GGUF auto-detection, with no Python runtime and MIT-licensed code.
tags: [stt, tts, pipeline, asr, ggml, gguf, cpp, edge-deployment]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:25:00Z }
stale_after: 2027-10-13
sources:
  - id: crispasr-readme
    resource: ../raw/CrispASR.md
    kind: documentation
    title: CrispASR README
---

CrispASR is a C++ speech engine on ggml that began as a fork of whisper.cpp and now ships one `crispasr` binary and CLI for about 119 backends, which the README counts as 62 TTS engines (it gives 52 elsewhere), plus text translation and speech-processing helpers. It needs no Python, PyTorch, or per-model binary at runtime: `--backend` names the backend or GGUF metadata selects it, and `-m auto` downloads the model on first use (**Reported**).[^crispasr-readme]

## Identity and positioning

- Presented as "one build, one binary, one consistent CLI" with ggml C++ runtimes for major open-weights ASR and TTS architectures (**Reported**).[^crispasr-readme]
- Origin: a fork of whisper.cpp. The Whisper path is described as byte-identical to upstream whisper.cpp, and code is MIT-licensed like upstream (**Reported**).[^crispasr-readme]
- Build and runtime footprint: a C++17 compiler and CMake 3.14+ build it; no Python, PyTorch, pip install, or per-model binary is needed (**Reported**).[^crispasr-readme]
- Model weights are not MIT by default. Each keeps its upstream license, and the README tables mix Apache-2.0, MIT, CC-BY-4.0, CC-BY-NC variants, and bespoke terms (**Reported**; per-backend detail in [CrispASR ASR Backend Selection](crispasr-asr-backend-selection.md) and [CrispASR TTS Engines](crispasr-tts-engines.md)).[^crispasr-readme]
- Browser target: all backends compile to a 4.3 MB WebAssembly module (`build-wasm.sh`) that runs client-side with COOP/COEP headers (**Reported**).[^crispasr-readme]

## Architecture

- A stable C-ABI in `src/` holds the algorithms (VAD, diarization, LID, alignment, cache, registry). Language wrappers consume that ABI, and the CLI is a thin layer in `examples/cli/` (**Reported**).[^crispasr-readme]
- Per-model runtimes sit in `src/{whisper,parakeet,canary,...}.cpp` and share primitives in `src/core/`, including mel, FFN, attention, the GGUF loader, and FastConformer, Conformer, and Granite-LLM blocks (**Reported**).[^crispasr-readme]
- Four static libraries (`crisp_audio`, `crisp_punc`, `crisp_lid`, `crisp_truecase`) are shared with CrispEmbed (**Reported**).[^crispasr-readme]
- Quality control is a `crispasr-diff` harness against PyTorch ground truth, a `tools/test-all-backends.py` capability-tier matrix, and a five-file recipe for adding a backend (**Reported**; the contributing and regression docs were not captured).[^crispasr-readme]

## Ecosystem

- The README names three sibling projects: CrisperWeaver (a Flutter transcription app built on CrispASR), CrispEmbed (ggml text embeddings, OCR, and notation), and Susurrus (a Python ASR GUI described as the Python counterpart) (**Reported**).[^crispasr-readme]
- Language bindings are listed for Python, Rust, Dart, Go, Ruby, Java, JavaScript, and mobile (**Reported**).[^crispasr-readme]
- A HuggingFace Space demo is auto-deployed from `hf-space/` (**Reported**).[^crispasr-readme]

## Concept map

- [CrispASR ASR Backend Selection](crispasr-asr-backend-selection.md): ASR families, capability matrix, which-backend guidance, translation, and speech-to-speech helpers (**Synthesis**).
- [CrispASR TTS Engines](crispasr-tts-engines.md): synthesis engines, the cloning/sampling/sample-rate matrix, license gating, watermarking, and consent (**Synthesis**).
- [CrispASR VAD and Language Identification](crispasr-vad-language-id.md): voice activity detectors and audio and text language-ID providers (**Synthesis**).
- [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md): speaker diarization methods, punctuation, truecasing, forced alignment, and hotwords (**Synthesis**).
- [CrispASR Streaming and HTTP Server](crispasr-streaming-http-server.md): live modes, progressive output, the OpenAI-compatible server, and concurrency limits (**Synthesis**).
- [CrispASR Build, GPU, and Operations](crispasr-build-gpu-operations.md): building, prebuilt-tarball rules, GPU selection, memory controls, quantization, caching, and debugging (**Synthesis**).

## Relationships

- Sibling: [audio.cpp Framework](audio-cpp-framework.md) is another native ggml audio runtime with overlapping TTS, ASR, and VAD coverage. The two are separate projects, and this wiki does not establish shared code (**Synthesis**).
- Alternative Whisper runtime: [Faster-Whisper](faster-whisper.md) is a CTranslate2 reimplementation of Whisper. CrispASR keeps a whisper.cpp-derived Whisper path (**Synthesis**).[^crispasr-readme]
- GGUF model packaging: [CSTR Qwen3-ASR-1.7B GGUF](cstr-qwen3-asr-1.7b-gguf.md) provides Q4_K, Q8_0, and F16 files for the 1.7B Qwen3-ASR checkpoint, run through the `qwen3` and `qwen3-1.7b` backends. Its Q8_0 audio-encoder rebake is a file-level detail, not a CrispASR-wide claim (**Synthesis**).

## Contradictions

- TTS engine count: the intro and the backend section give 62 TTS engines, while the table of contents gives 52 for the same TTS section. Neither figure is chosen (**Reported**).[^crispasr-readme]
- Backend count: the feature-matrix section cites a "119-backend" surface and, in the same section, a "full 109-backend matrix" in `docs/feature-matrix.md`. Neither figure is chosen (**Reported**).[^crispasr-readme]

## Coverage and limits

- One README capture (1,204 lines) was inspected statically. No revision, commit, or release tag is recorded; the entry point cites upstream `github.com/CrispStrobe/CrispASR` without a snapshot (**Synthesis**).[^crispasr-readme]
- Linked material not captured: `docs/*.md` (install, cli, tts, streaming, server, concurrency, architecture, contributing, troubleshooting, eu-ai-act, quantize, bindings, benchmarking, feature-matrix, regression-matrix), `PERFORMANCE.md`, `PLAN.md`, `HISTORY.md`, `LEARNINGS.md`, and the feature-matrix HTML. Those docs may refine or override README statements (**Synthesis**).[^crispasr-readme]
- Excluded: the README's "Music & audio analysis" section (source separation, piano, multi-instrument, beat, chord, tablature, and pitch tracking). These are non-speech modalities that do not feed the VAD → STT → LLM → TTS loop, so `SCOPE.md` excludes them (**Synthesis**).[^crispasr-readme]
- Provenance: the README states that parts of the integration layer, all model converters, and FastConformer/attention/mel core helpers were co-authored with Claude Code (**Reported**).[^crispasr-readme]
- Nothing was built, installed, downloaded, or run. All figures are README assertions and carry no independent verification (**Synthesis**).[^crispasr-readme]

[^crispasr-readme]: [CrispASR README](../raw/CrispASR.md) — locators: title tagline and `Ecosystem` table; browser paragraph; `Table of contents` TTS bullet (52 engines); `Start here` §1–§3 and `If nothing happened`; `Supported backends` intro (119 backends, 62 TTS); `Feature matrix` intro (119-backend and 109-backend statements); `Install & build`; `Architecture, contributing, regression matrix` and shared-libraries paragraph; `Credits` (Claude Code note); `License`.
