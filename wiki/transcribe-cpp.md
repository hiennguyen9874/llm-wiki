---
type: Concept
title: transcribe.cpp
description: C/C++ ggml-based STT inference runtime serving 20 ASR families plus a streaming diarizer via GGUF with Metal, Vulkan, CUDA, and ROCm backends, CLI plus four language bindings, and a catalog-driven verification workflow.
tags: [stt, streaming, gguf, edge-deployment, pipeline, diarization]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T14:00:00Z }
stale_after: 2027-10-06
sources:
  - id: transcribe-cpp-readme
    resource: ../raw/transcribe.cpp.md
    kind: documentation
    title: transcribe.cpp README
---

transcribe.cpp is a C/C++ speech-to-text inference library that runs diverse STT model families as GGUF weights on the ggml runtime, with Metal, Vulkan, and CUDA GPU backends plus a tinyBLAS-accelerated CPU path, covering streaming and batch transcription with every `handy-computer` release claimed numerically verified and WER-tested against its reference implementation (**Reported**).[^transcribe-cpp-readme]

## Runtime identity and scope

- Stated positioning is a C/C++ STT inference library over GGUF models on ggml, with Metal, Vulkan, and CUDA backends for GPU inference plus a tinyBLAS-accelerated CPU path (**Reported**).[^transcribe-cpp-readme]
- The source tagline claims 16 model families and 60+ variants with streaming and batch modes; the family tables in the same snapshot list 20 STT families plus one diarization-only family (see [Contradictions](#contradictions)) (**Observed** by static inspection).[^transcribe-cpp-readme]
- Every model published under [`handy-computer`](https://huggingface.co/handy-computer) is claimed numerically verified and WER-tested against its reference implementation (**Reported**).[^transcribe-cpp-readme]

## Supported models (Reported)

Capability tokens below transcribe the source's `Available capabilities` column verbatim; per-checkpoint accuracy, language, and license detail lives on the linked model pages (**Synthesis**).[^transcribe-cpp-readme]

| Family (source variants) | Capabilities in source | Wiki concept |
| --- | --- | --- |
| Canary (`canary-180m-flash`, `canary-1b`, `canary-1b-flash`, `canary-1b-v2`) | translate | [Canary-1b-v2](canary-1b-v2.md) covers the v2 checkpoint; other three variants have no concept |
| Canary-Qwen 2.5B (`canary-qwen-2.5b`) | — | [Canary-Qwen-2.5B](canary-qwen-2.5b.md) |
| Cohere Transcribe (`cohere-transcribe-03-2026`, `cohere-transcribe-arabic-07-2026`) | — | [Cohere Transcribe 03-2026](cohere-transcribe-03-2026.md), [Cohere Transcribe Arabic 07-2026](cohere-transcribe-arabic-07-2026.md) |
| Fun-ASR-Nano (`fun-asr-mlt-nano-2512`, `fun-asr-nano-2512`) | — | [Fun-ASR-Nano-2512](fun-asr-nano-2512.md), [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md) |
| GigaAM-v3 (`gigaam-v3-ctc`, `gigaam-v3-e2e-ctc`, `gigaam-v3-e2e-rnnt`, `gigaam-v3-rnnt`) | token timestamps | no concept yet |
| Granite Speech 4 / 4.1 (`granite-4.0-1b-speech`, `granite-speech-4.1-2b`, `granite-speech-4.1-2b-nar`, `granite-speech-4.1-2b-plus`) | diarize, translate, word timestamps | no concept yet (distinct from TurboCTC below) |
| Granite Speech 5.0 TurboCTC (`granite-speech-5.0-470m-turboctc`, `granite-speech-5.0-470m-turboctc-nc`) | — | [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) |
| MedASR (`medasr`) | token timestamps | no concept yet |
| Moonshine (8 `moonshine-base*` + 8 `moonshine-tiny*` variants incl. ar/ja/ko/uk/vi/zh) | — | no concept yet |
| Moonshine Streaming (`moonshine-streaming-medium/small/tiny`) | streaming | no concept yet |
| MOSS-Transcribe-Diarize (`moss-transcribe-diarize`) | diarize, segment timestamps | [MOSS-Transcribe-Diarize 0.9B](moss-transcribe-diarize.md) covers the upstream checkpoint |
| Multitalker Parakeet Streaming 0.6B v1 (`multitalker-parakeet-streaming-0.6b-v1`) | diarize, streaming, token timestamps | [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md) |
| Nemotron 3.5 ASR Streaming 0.6B (`nemotron-3.5-asr-streaming-0.6b`) | streaming, token timestamps | [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) |
| Nemotron Speech Streaming EN 0.6B (`nemotron-speech-streaming-en-0.6b`) | streaming, token timestamps | [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md) |
| Parakeet (13 variants: `parakeet-ctc-0.6b/1.1b`, `parakeet-primeline`, `parakeet-rnnt-0.6b/1.1b`, `parakeet-tdt-0.6b-v2/v3`, `parakeet-tdt-1.1b`, `parakeet-tdt_ctc-1.1b/110m`, `parakeet-ultra`, `parakeet-unified-en-0.6b`, `orukeet`) | streaming, token timestamps | [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md), [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md), [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md), [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md), [Parakeet RNNT 0.6B](parakeet-rnnt-0.6b.md), [Parakeet RNNT 1.1B](parakeet-rnnt-1.1b.md), [Parakeet Ultra](parakeet-ultra.md), [Orukeet](orukeet.md); remaining variants have no concept |
| Qwen3-ASR (`qwen3-asr-0.6b`, `qwen3-asr-1.7b`) | — | [Qwen3-ASR family](qwen3-asr-family.md) |
| SenseVoice Small (`sensevoice-small`) | — | [SenseVoiceSmall GGUF](sensevoice-small-gguf.md) covers the audio.cpp GGUF packaging of the same upstream checkpoint |
| Voxtral 2507 (`voxtral-mini-3b-2507`, `voxtral-small-24b-2507`) | translate | [Voxtral Mini 3B 2507](voxtral-mini-3b-2507.md), [Voxtral Small 24B 2507](voxtral-small-24b-2507.md) |
| Voxtral Realtime 2602 (`voxtral-mini-4b-realtime-2602`) | streaming | [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) |
| Whisper (`whisper-base/small/medium/large` tiers incl. `.en`, `large-v2/v3/turbo`, `breeze-asr-25`) | segment timestamps, translate | [Whisper Large v3](whisper-large-v3.md), [Whisper Large v3 Turbo](whisper-large-v3-turbo.md), [TheWhisper-Large-V3-Turbo](thewhisper-large-v3-turbo.md), [Distil-Large-v3.5](distil-large-v3.5.md); other size tiers have no concept |

- Diarization-only table (verified by DER/JER rather than WER, no transcription): Streaming Sortformer Diarizer 4spk v2.1 (`diar_streaming_sortformer_4spk-v2.1`) with diarize plus streaming capabilities (**Reported**).[^transcribe-cpp-readme]
- That diarizer maps to [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md); per-variant model cards live under `docs/models/` in the source checkout, none fetched here (**Synthesis**).[^transcribe-cpp-readme]

## Model catalog and verification workflow

- `catalog/` is stated as the source of truth for model metadata, accuracy, and performance; each release ships a queryable `catalog.db` plus SHA-256 checksum from the latest GitHub release, rebuildable locally with `uv run scripts/catalog/db.py --out catalog.db` (**Reported**).[^transcribe-cpp-readme]
- Accuracy and speed matrices plus standard benchmark recipes for publication live in `catalog/_benchmark_profiles.json`; `uv run scripts/catalog/check.py --publication-profile` enforces them while the ordinary catalog check reports the migration backlog without failing (**Reported**).[^transcribe-cpp-readme]
- Published tables are generated, not hand-written: a model doc delegates a region with a marker pair (e.g. `<!-- catalog:downloads -->` … `<!-- /catalog -->`) and `scripts/catalog/render.py` rewrites only what sits between the pair; `format.py --check`, `check.py` (schema, integrity, pairing), and `render.py` / `render.py --check` are the stated record-layout, validation, and rendering commands (**Reported**).[^transcribe-cpp-readme]
- Hugging Face card specs under `scripts/hf_cards/` hold editorial copy only (summary, tags, validation pin, prose notes); `scripts/hf_cards/generate.py` reads the spec plus the catalog record so repos, licence, languages, capabilities, quant table, and per-rig speedups are never written into YAML by hand (**Reported**).[^transcribe-cpp-readme]

## Build, backends, and dependencies

- Default build is `cmake -B build` then `cmake --build build`; Metal enables automatically on Apple Silicon (**Reported**).[^transcribe-cpp-readme]
- Vulkan (Linux/Windows) needs `build-essential cmake libvulkan-dev glslc libopenblas-dev` on Ubuntu/Debian or `vulkan-headers openblas-devel glslc spirv-headers-devel` on Fedora, then `cmake -B build -DTRANSCRIBE_VULKAN=ON` (**Reported**).[^transcribe-cpp-readme]
- CUDA (Linux + NVIDIA GPU) requires the CUDA toolkit (`nvcc`) on `PATH`, then `cmake -B build -DTRANSCRIBE_CUDA=ON`; HIP/ROCm (Linux + AMD GPU) needs ROCm 6.1 or newer with `cmake -B build -DTRANSCRIBE_HIP=ON -DAMDGPU_TARGETS=gfx1201` (replace `gfx1201` from `rocminfo | grep gfx`; semicolon-separated list for several architectures); ROCm devices report as the `rocm` backend kind, are picked up by default `auto` backend selection, and can be required explicitly with `--backend rocm` (**Reported**).[^transcribe-cpp-readme]
- `libopenblas-dev` is optional but recommended and claimed to accelerate the host-side decoder ~10–15x; without it the build falls back to a scalar path automatically; tinyBLAS (Justine Tunney's `llamafile_sgemm` kernels) is on by default (**Reported**).[^transcribe-cpp-readme]
- The quantization tool builds with `cmake -B build -DTRANSCRIBE_BUILD_TOOLS=ON`; Windows Vulkan setup, Visual Studio commands, and the short-build-root fallback for deep checkouts live in the unfetched `docs/build-windows.md` (**Reported**, with unfetched-pointer limit).[^transcribe-cpp-readme]

## GGUF conversion, quantization, and usage

- Pre-built GGUFs for all supported models are hosted under `handy-computer` on Hugging Face; each per-model doc linked in the family table carries direct download links for every quant; convert from source only for a different dtype or an un-prebuilt checkpoint (**Reported**).[^transcribe-cpp-readme]
- NeMo conversion loads directly from NVIDIA checkpoints via `ASRModel.from_pretrained` under `uv` (the parakeet env ships NeMo and deps), e.g. `uv run --project scripts/envs/parakeet scripts/convert-parakeet.py nvidia/parakeet-tdt-0.6b-v2`, writing `models/<slug>/<slug>-F32.gguf` in llama.cpp-style `<slug>-<QUANT>.gguf` naming; a local `.nemo` path or extracted directory supports offline conversion (**Reported**).[^transcribe-cpp-readme]
- `transcribe-quantize` produces smaller models from the reference GGUF with presets `F16`, `Q8_0`, `Q6_K`, `Q5_K_M`, `Q4_K_M`, e.g. `build/bin/transcribe-quantize <in>-F32.gguf <out>-Q4_K_M.gguf --quant Q4_K_M` (**Reported**).[^transcribe-cpp-readme]
- CLI usage is `build/bin/transcribe-cli -m <model>.gguf samples/jfk.wav`; input must be 16 kHz mono WAV, converted from other formats with `ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav` or `sox` (**Reported**).[^transcribe-cpp-readme]

## Bindings, tests, and project layout

- Official bindings wrap the C API: Python at `bindings/python`, TypeScript/JavaScript at `bindings/typescript`, Rust at `bindings/rust/transcribe-cpp`, Swift/ObjC at `bindings/swift`; `docs/bindings.md` covers generation and header sync; upgrading from 0.1 uses `docs/migrating-to-0.2.md` including the new exact-device selection API and the changed meaning of CLI `--device 0` (**Reported**).[^transcribe-cpp-readme]
- Tests run with `cd build && ctest`; real-model tests need `cmake -B build -DTRANSCRIBE_BUILD_REAL_MODEL_TESTS=ON`, a rebuild, and `TRANSCRIBE_PARAKEET_GGUF=path/to/model.gguf ctest --test-dir build`; the expected smoke-test, numerical-validation, and benchmark pattern for new ports lives in the unfetched `docs/model-family-testing.md` (**Reported**, with unfetched-pointer limit).[^transcribe-cpp-readme]
- Stated layout: `include/transcribe.h` public C API (single header); `src/` internals (C++17) with `src/arch/parakeet/` and `src/arch/cohere/` family implementations; `examples/cli/` CLI source; `tools/transcribe-quantize/` quantizer; `bindings/`; `docs/` porting/validation guidance; `scripts/` converter plus test tooling; vendored `ggml/` (recipe in `ggml/UPSTREAM`) with downstream patches in `patches/ggml/` applied by `scripts/sync-ggml.sh`; vendored `src/third_party/miniz/` deflate codec; `samples/` audio; `tests/` (**Reported**).[^transcribe-cpp-readme]

## Sponsors and license

- Named supporters: Mozilla AI plus BiR Program (research backing toward a ggml engine with agentic porting experiments); Hugging Face (extra storage for hosted models); Modal (GPU credits for reference-implementation WER validation); Blacksmith (CI runners) (**Reported**).[^transcribe-cpp-readme]
- License is MIT (`LICENSE`); vendored ggml and miniz (both MIT) are attributed in `THIRD-PARTY-LICENSES.md` (**Reported**).[^transcribe-cpp-readme]

## Relationships

- Serves: [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md), [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md), [Canary-1b-v2](canary-1b-v2.md), [Qwen3-ASR family](qwen3-asr-family.md), [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md), [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md), [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md), and [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) are the wiki-covered checkpoints this runtime names; those pages hold model-level accuracy and checkpoint detail while this page holds the runtime path (**Synthesis**).[^transcribe-cpp-readme]
- Packages: [Orukeet](orukeet.md) ships a Handy-compatible `orukeet-transcribe-cpp-Q8_0.gguf` export for this runtime family pinned to `transcribe-cpp` 0.2.0; that page holds the byte sizes, revision pins, and layout warning while this page holds the runtime's build and quantize path (**Synthesis**).[^transcribe-cpp-readme]
- Uses: [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md) is the diarization-only checkpoint this runtime names for streaming diarization verified by DER/JER rather than WER (**Synthesis**).[^transcribe-cpp-readme]
- Contrasts with: [audio.cpp Framework](audio-cpp-framework.md) is the community ggml-based multi-family audio runtime in this wiki; transcribe.cpp is the Handy STT-plus-diarization runtime with its own catalog/verification workflow — compare them when choosing between broad audio coverage and a dedicated transcription engine (**Synthesis**).[^transcribe-cpp-readme]
- Contrasts with: [NeMo-Speech.cpp](nemo-speech-cpp.md) is NVIDIA's official single-vendor Nemotron-family ggml runtime; transcribe.cpp is the multi-vendor Handy runtime instead — compare them when choosing between official Nemotron day-0 support and 20-family coverage (**Synthesis**).[^transcribe-cpp-readme]
- Adjacent batch GPU path: [Fast GPU ASR](fast-gpu-asr.md) covers TensorRT batched Zipformer/Parakeet inference on NVIDIA GPUs; transcribe.cpp covers the ggml GGUF path across Metal/Vulkan/CUDA/ROCm/CPU (**Synthesis**).[^transcribe-cpp-readme]

## Contradictions

- **Family count:** the header claims 16 model families and 60+ variants, while the snapshot's family tables list 20 STT families plus one diarization-only family (21 rows). Neither value is chosen here; the table above follows the row-level tables (**Observed** by static inspection).[^transcribe-cpp-readme]

## Coverage and limits

- Source inspected statically only; nothing built, no GGUF downloaded, no audio transcribed, no WER/DER figure or 10–15x OpenBLAS claim reproduced — all performance and verification claims are source assertions under unstated hardware and protocol (**Synthesis**).[^transcribe-cpp-readme]
- Snapshot has no stated commit revision or capture date; treat family coverage, quant presets, backend flags, and benchmark numbers as time-sensitive (**Synthesis**).[^transcribe-cpp-readme]
- Referenced but unfetched and absent from `raw/`: every `docs/models/*.md` per-model card, `docs/build-windows.md`, `docs/bindings.md`, `docs/migrating-to-0.2.md`, `docs/model-family-testing.md`, `catalog/` (including `catalog.db` and `_benchmark_profiles.json`), `scripts/catalog/*`, `scripts/hf_cards/*`, `scripts/convert-parakeet.py`, `scripts/envs/parakeet`, `scripts/sync-ggml.sh`, `include/transcribe.h`, `src/*`, `examples/cli/`, `tools/transcribe-quantize/`, all four `bindings/` trees, vendored `ggml/` plus `patches/ggml/`, `src/third_party/miniz/`, `samples/`, `tests/`, `LICENSE`, and `THIRD-PARTY-LICENSES.md`; install and inference fences are transcribed, not executed (**Synthesis**).[^transcribe-cpp-readme]
- Seven named families have no wiki concept yet (GigaAM-v3, Granite Speech 4/4.1, MedASR, Moonshine, Moonshine Streaming, plus uncovered Canary/Parakeet/Whisper variants); capability tokens for those rows come from this source alone (**Synthesis**).[^transcribe-cpp-readme]
- Release and benchmark figures carry `stale_after: 2027-10-06` per `SCOPE.md` domain rules for `stt` and `pipeline` (**Synthesis**).[^transcribe-cpp-readme]

[^transcribe-cpp-readme]: [transcribe.cpp](../raw/transcribe.cpp.md) — locators: header tagline (C/C++ STT library, GGUF on ggml, Metal/Vulkan/CUDA, tinyBLAS CPU, 16 families / 60+ variants, streaming + batch, handy-computer numerical verification + WER testing); `Supported models` family-index tables (20 STT families with variants + capabilities + `docs/models/*.md` links; `Speaker diarization models` table with `diar_streaming_sortformer_4spk-v2.1`, diarize + streaming, DER/JER note); `Model catalog` (`catalog/` source of truth, `catalog.db` + SHA-256 release assets, `db.py --out` rebuild, `_benchmark_profiles.json`, `check.py --publication-profile` vs ordinary check, `<!-- catalog:downloads -->` marker + `render.py` rewrite rule, `format.py --check` / `check.py` / `render.py` fences, `scripts/hf_cards/` spec + `generate.py` rule); `Build` (`cmake -B build` / `cmake --build build`, Metal auto, Vulkan apt/dnf fences + `-DTRANSCRIBE_VULKAN=ON`, CUDA `nvcc` + `-DTRANSCRIBE_CUDA=ON`, HIP/ROCm 6.1+ `-DTRANSCRIBE_HIP=ON -DAMDGPU_TARGETS=gfx1201` + `rocminfo` + `rocm` backend + `--backend rocm`, openblas ~10-15x + scalar fallback, tinyBLAS default, `-DTRANSCRIBE_BUILD_TOOLS=ON`, `docs/build-windows.md` pointer); `Models` (handy-computer prebuilt GGUFs, per-model doc download links, `ASRModel.from_pretrained` + `uv --project scripts/envs/parakeet convert-parakeet.py` fence, `<slug>-<QUANT>.gguf` naming, `.nemo`/extracted-dir offline path); `Quantize` (`transcribe-quantize` fence, `F16/Q8_0/Q6_K/Q5_K_M/Q4_K_M` presets); `Usage` (`transcribe-cli -m` fence, 16 kHz mono WAV, `ffmpeg -ar 16000 -ac 1` / `sox`); `Bindings` (Python/TypeScript/Rust/Swift paths, `docs/bindings.md`, `docs/migrating-to-0.2.md` + exact-device + `--device 0` note); `Tests` (`ctest`, `-DTRANSCRIBE_BUILD_REAL_MODEL_TESTS=ON`, `TRANSCRIBE_PARAKEET_GGUF=` fence, `docs/model-family-testing.md`); `Sponsors & Supporting Organizations` (Mozilla AI/BiR, Hugging Face storage, Modal WER GPU credits, Blacksmith CI); `Project layout` (transcribe.h, src C++17, arch/parakeet + arch/cohere, examples/cli, tools/transcribe-quantize, bindings, docs, scripts, ggml/UPSTREAM, patches/ggml + sync-ggml.sh, third_party/miniz, samples, tests); `License` (MIT, THIRD-PARTY-LICENSES.md, ggml/miniz MIT).
