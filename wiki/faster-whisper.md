---
type: Concept
title: Faster-Whisper
description: CTranslate2-based reimplementation of OpenAI Whisper with batched inference, 8-bit quantization, Silero VAD filtering, word timestamps, and a Transformers-to-CTranslate2 conversion path.
tags: [stt, whisper, quantization, vad, deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T14:07:36Z }
stale_after: 2027-10-06
sources:
  - id: faster-whisper-readme
    resource: ../raw/faster-whisper.md
    kind: documentation
    title: Faster-Whisper README
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
  - id: distil-large-v3.5-card
    resource: ../raw/distil-large-v3.5.md
    kind: documentation
    title: Distil-Whisper Distil-Large-v3.5 model card
---

Faster-Whisper by SYSTRAN is a reimplementation of OpenAI's Whisper model on the CTranslate2 inference engine that claims up to 4x faster transcription than openai/whisper at the same accuracy with less memory, improvable further with 8-bit quantization on CPU and GPU, plus batched inference, word-level timestamps, Silero VAD filtering, and a script plus API for converting Transformers-compatible Whisper checkpoints (**Reported**).[^faster-whisper-readme]

## Identity and engine claim

- Reimplementation target: OpenAI's Whisper model run through [CTranslate2](https://github.com/OpenNMT/CTranslate2/), described as a fast inference engine for Transformer models (**Reported**).[^faster-whisper-readme]
- Efficiency claim: up to 4 times faster than openai/whisper for the same accuracy while using less memory, with further gains from 8-bit quantization on CPU and GPU (**Reported**).[^faster-whisper-readme]

## Requirements and installation

- Requires Python 3.9 or greater; unlike openai-whisper, system FFmpeg is not needed because audio is decoded with the Python library PyAV, which bundles the FFmpeg libraries (**Reported**).[^faster-whisper-readme]
- GPU execution requires NVIDIA cuBLAS for CUDA 12 and cuDNN 9 for CUDA 12; current `ctranslate2` supports only CUDA 12 plus cuDNN 9, with workarounds of downgrading to `ctranslate2==3.24.0` for CUDA 11 plus cuDNN 8 or `ctranslate2==4.4.0` for CUDA 12 plus cuDNN 8 (**Reported**).[^faster-whisper-readme]
- NVIDIA library install routes named: official NVIDIA documentation (recommended), the `nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04` Docker image, Linux-only `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12==9.*` with `LD_LIBRARY_PATH` exported from the installed package paths, and Purfview's `whisper-standalone-win` single-archive library bundle for Windows and Linux placed on `PATH` (**Reported**).[^faster-whisper-readme]
- Install fences: `pip install faster-whisper` from PyPI; master branch via `pip install --force-reinstall "faster-whisper @ https://github.com/SYSTRAN/faster-whisper/archive/refs/heads/master.tar.gz"`; a pinned commit via the corresponding `archive/<sha>.tar.gz` URL (**Reported**).[^faster-whisper-readme]

## Usage

- Basic fence: `WhisperModel(model_size, device="cuda", compute_type="float16")` with variants `device="cuda", compute_type="int8_float16"` for GPU INT8 and `device="cpu", compute_type="int8"` for CPU INT8, then `model.transcribe("audio.mp3", beam_size=5)` returning `(segments, info)` with `info.language` and `info.language_probability`, iterating segments for `segment.start`, `segment.end`, and `segment.text` (**Reported**).[^faster-whisper-readme]
- Generator semantics: `segments` is a generator, so transcription only starts on iteration and is run to completion by collecting it in a list or `for` loop; the fence `segments = list(segments)` is where transcription actually runs (**Reported**).[^faster-whisper-readme]
- Batched transcription: `BatchedInferencePipeline(model=model)` whose `transcribe` is a drop-in replacement for `WhisperModel.transcribe`, e.g. `WhisperModel("turbo", device="cuda", compute_type="float16")` wrapped and called with `batch_size=16`; VAD filtering is enabled by default for batched transcription (**Reported**).[^faster-whisper-readme]
- Distil-Whisper fence: Distil-Whisper checkpoints are compatible, with `distil-large-v3` designed for the Faster-Whisper transcription algorithm; the fence uses `WhisperModel("distil-large-v3", device="cuda", compute_type="float16")` with `transcribe("audio.mp3", beam_size=5, language="en", condition_on_previous_text=False)` and defers to the original `distil-whisper/distil-large-v3` model card for details (**Reported**).[^faster-whisper-readme]
- Word-level timestamps: `model.transcribe("audio.mp3", word_timestamps=True)` exposes `segment.words` with per-word `start`, `end`, and `word` (**Reported**).[^faster-whisper-readme]
- VAD filter: integrates the Silero VAD model via `vad_filter=True`; the default is conservative and only removes silence longer than 2 seconds, with customization through `vad_parameters` (e.g. `dict(min_silence_duration_ms=500)`) whose full parameter list and defaults live in `faster_whisper/vad.py` (**Reported**).[^faster-whisper-readme]
- Logging fence: `logging.getLogger("faster_whisper").setLevel(logging.DEBUG)` after `logging.basicConfig()`; further model and transcription options are deferred to the `WhisperModel` implementation in `faster_whisper/transcribe.py` (**Reported**).[^faster-whisper-readme]

## Benchmarks

- Protocol: time and memory to transcribe 13 minutes of audio (linked YouTube source) across openai/whisper@v20240930, whisper.cpp@v1.7.2, transformers@v4.46.3, and faster-whisper@v1.1.0; GPU figures on CUDA 12.4 with an NVIDIA RTX 3070 Ti 8GB and CPU figures with 8 threads on an Intel Core i7-12700K (**Reported**).[^faster-whisper-readme]
- Large-v2 on GPU (fp16/int8, beam size 5): openai/whisper fp16 2m23s and 4708 MB VRAM; whisper.cpp with Flash Attention fp16 1m05s and 4127 MB; transformers with SDPA fp16 1m52s and 4960 MB (with transformers OOM for any batch size above 1); faster-whisper fp16 1m03s and 4525 MB, or 17 s and 6090 MB with `batch_size=8`; faster-whisper int8 59 s and 2926 MB, or 16 s and 4500 MB with `batch_size=8` (**Reported**).[^faster-whisper-readme]
- distil-whisper-large-v3 on GPU (`batch_size=16`, fp16, beam size 5): transformers with SDPA 46m12s at 14.801 YT-Commons WER versus faster-whisper 25m50s at 13.527 WER (**Reported**).[^faster-whisper-readme]
- Small model on CPU (fp32/int8, beam size 5): openai/whisper fp32 6m58s and 2335 MB RAM; whisper.cpp fp32 2m05s and 1049 MB; whisper.cpp with OpenVINO fp32 1m45s and 1642 MB; faster-whisper fp32 2m37s and 2257 MB, or 1m06s and 4230 MB with `batch_size=8`; faster-whisper int8 1m42s and 1477 MB, or 51 s and 3608 MB with `batch_size=8` (**Reported**).[^faster-whisper-readme]

## Model conversion and loading

- Loading by size such as `WhisperModel("large-v3")` automatically downloads the corresponding CTranslate2 model from the Hugging Face Hub (`Systran` organization) (**Reported**).[^faster-whisper-readme]
- Conversion fence for any Transformers-compatible Whisper model (original OpenAI or fine-tuned): `pip install transformers[torch]>=4.23` then `ct2-transformers-converter --model openai/whisper-large-v3 --output_dir whisper-large-v3-ct2 --copy_files tokenizer.json preprocessor_config.json --quantization float16`; `--model` accepts a Hub name or local directory, and without `--copy_files tokenizer.json` the tokenizer configuration downloads automatically at later load time; conversion from code is deferred to the CTranslate2 `TransformersConverter` API (**Reported**).[^faster-whisper-readme]
- Loading a converted model: directly from a local directory (`WhisperModel("whisper-large-v3-ct2")`) or from the Hub after upload (`WhisperModel("username/whisper-large-v3-ct2")`) (**Reported**).[^faster-whisper-readme]

## Fair-comparison guidance

- When comparing against other Whisper implementations, use similar settings: the same beam size (noting openai/whisper `model.transcribe` defaults to beam size 1 while faster-whisper defaults to 5), comparable WER since transcription speed tracks word count, and the same CPU thread count, e.g. `OMP_NUM_THREADS=4 python3 my_script.py` since many frameworks read `OMP_NUM_THREADS` (**Reported**).[^faster-whisper-readme]

## Community integrations

- Non-exhaustive downstream list named in the source: [Speaches](speaches.md) (OpenAI-compatible server with Docker, streaming, and live transcription), WhisperX (speaker diarization plus wav2vec2-aligned word timestamps), `whisper-ctranslate2` (CLI compatible with the original openai/whisper client), `whisper-diarize` (faster-whisper plus NVIDIA NeMo diarization), `whisper-standalone-win` (standalone CLI executables for Windows, Linux, and macOS), `asr-sd-pipeline` (AzureML multi-speaker pipeline), Open-Lyrics (transcription plus GPT polish into `.lrc`), `wscribe` plus `wscribe-editor` (word-level transcript export and editing), aTrain (BANDAS-Center GUI for transcription and diarization, including a Windows Store app), Whisper-Streaming (realtime mode with faster-whisper as the recommended backend and self-adaptive latency), WhisperLive (nearly-live transcription on a faster-whisper backend), Faster-Whisper-Transcriber (voice transcriber UI), open-dubbing (AI dubbing with translation and synchronization), and Whisper-FastAPI (API backend compatible with OpenAI, HomeAssistant, and Konele formats) (**Reported**).[^faster-whisper-readme]

## Relationships

- Uses [Silero VAD](silero-vad.md): the `vad_filter` plus `vad_parameters` path integrates this VAD with a conservative 2-second-silence default; consult that page for model footprint, runtimes, and sampling-rate scope (**Synthesis**).[^faster-whisper-readme]
- Used by [RealtimeSTT](realtimestt.md): RealtimeSTT's default general-purpose engine path is `faster_whisper`; consult that page for the VAD-gated realtime-plus-final library and server integration around this engine (**Synthesis**).[^faster-whisper-readme]
- Used by [WhisperLiveKit](whisperlivekit.md): WLK lists `faster-whisper` as an explicit `--backend` (and the non-MLX default under `auto`); consult that page for the SimulStreaming/LocalAgreement streaming policies and API-compatible serving around this backend (**Synthesis**).[^faster-whisper-readme]
- Used by [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md): that LLM-generated draft recommends this runtime with Whisper small/medium (FP16 GPU or INT8 CPU) as the per-utterance ASR stage behind gateway VAD endpointing (**Synthesis**).[^faster-whisper-readme]
- Related to [GPT-SoVITS](gpt-sovits.md): that voice-conversion/TTS WebUI names Faster-Whisper Large V3 among its data-preparation ASR options; consult that page for the dataset-tooling context rather than transcription serving (**Synthesis**).[^faster-whisper-readme]
- Evaluated with [Community-Reported Local ASR/TTS Selection](community-asr-tts-selection.md), [Community-Reported Noisy On-Premise STT Selection](community-noisy-call-stt.md), and [Community-Reported Open STT and Realtime Diarization Selection](community-open-stt-diarization.md): those drafts report production-CPU stability, ~1x-realtime noisy-call baselines, and voice-satellite use for faster-whisper against Parakeet, Whisper Turbo, and Qwen3-ASR alternatives; treat those anecdotes as unverified alongside this page's source-reported benchmarks (**Synthesis**).[^faster-whisper-readme]
- Configured by [Whisper Hallucination Mitigation for Vietnamese](whisper-hallucination-mitigation.md): an AI-compiled report's `large-v3-turbo` decoding parameters, confidence filters, and Vietnamese phrase blacklist for this runtime, plus the warning to materialize the lazy `transcribe` generator inside `asyncio.to_thread` (Pipecat PR #5931); used as the default STT in [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) (**Reported**).[^claude-pipeline-report]
- Serves [Distil-Large-v3.5](distil-large-v3.5.md): that checkpoint's card names the `distil-whisper/distil-large-v3.5-ct2` upload for this engine with `beam_size=5, language="en"`; consult that page for the v3.5 short/long-form benchmarks and the sequential-versus-chunked guidance (**Synthesis**).[^distil-large-v3.5-card]

## Coverage and limits

- Source inspected statically only; no `pip install`, model download, transcription, VAD run, conversion, or benchmark was executed, and no latency, memory, WER, or speedup figure was reproduced (**Synthesis**).[^faster-whisper-readme]
- Referenced but unfetched and absent from `raw/`: the CTranslate2 engine, openai/whisper, whisper.cpp, transformers, and distil-large-v3 implementations and weights; the 13-minute benchmark audio; the Silero VAD model and `faster_whisper/vad.py`; `faster_whisper/transcribe.py`; the Hugging Face Hub `Systran` organization; the `ct2-transformers-converter` script and `TransformersConverter` API; all 14 community-integration repositories; and the Purfview library archive and NVIDIA install destinations; install, transcribe, VAD, conversion, and benchmark fences above are transcribed, not executed (**Synthesis**).[^faster-whisper-readme]
- All speed, memory, accuracy, compatibility, and recommendation claims are source assertions without independent verification in this wiki; benchmark figures and CUDA/cuDNN version guidance carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^faster-whisper-readme]

[^faster-whisper-readme]: [Faster-Whisper README](../raw/faster-whisper.md) — locators: header (SYSTRAN, CTranslate2 engine, up-to-4x-faster/same-accuracy/less-memory claim, 8-bit quantization note); `Benchmark` (13-minute audio link; implementation pins openai/whisper@v20240930, whisper.cpp@v1.7.2, transformers@v4.46.3, faster-whisper@v1.1.0; `Large-v2 model on GPU` table with fp16/int8 and `batch_size=8` rows; `distil-whisper-large-v3 model on GPU` table with `batch_size=16` rows and YT Commons WER; RTX 3070 Ti 8GB CUDA 12.4 note and transformers-OOM footnote; `Small model on CPU` table with fp32/int8 and `batch_size=8` rows; i7-12700K 8-thread note); `Requirements` (Python 3.9+, PyAV-bundled FFmpeg note; cuBLAS-CUDA-12 plus cuDNN-9 note; ctranslate2 CUDA 11/12 downgrade versions 3.24.0 and 4.4.0; Docker image, Linux `pip` plus `LD_LIBRARY_PATH`, and Purfview archive install routes); `Installation` (PyPI fence, master-branch and pinned-commit fences); `Usage` (`WhisperModel` fp16/int8 fences, generator warning plus `list(segments)` fence, `BatchedInferencePipeline` fence with VAD-on-by-default note, `distil-large-v3` fence with `language`/`condition_on_previous_text` args and model-card pointer, `word_timestamps` fence, `vad_filter` plus `vad_parameters` fences with 2-second-silence default and `vad.py` pointer, logging fence, `transcribe.py` pointer); `Community integrations` (14-project list as transcribed above); `Model conversion` (auto-download on `WhisperModel("large-v3")`, `ct2-transformers-converter` fence with `--model`/`--copy_files`/`--quantization` semantics, code-conversion API pointer, local-directory and Hub-name load fences); `Comparing performance against other implementations` (beam-size default 1-vs-5, WER/word-count, `OMP_NUM_THREADS` fence).

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `PHẦN 2` `Whisper: cấu hình chống hallucination`; `Kỹ thuật tối ưu` (PR #5931); `Recommendations` tier table.

[^distil-large-v3.5-card]: [Distil-Whisper Distil-Large-v3.5 model card](../raw/distil-large-v3.5.md) — locator: `Library Integrations` > `Faster-Whisper` (`distil-whisper/distil-large-v3.5-ct2` model id, transcribe fence with `beam_size=5, language="en"`).
