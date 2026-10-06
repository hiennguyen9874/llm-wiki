---
type: Concept
title: Silero VAD
description: MIT-licensed enterprise-grade pre-trained voice activity detector with sub-1 ms per 30 ms chunk CPU inference, ~2 MB JIT footprint, 8/16 kHz support, and PyTorch plus ONNX runtimes.
tags: [vad, endpointing, pytorch, onnx, edge]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: silero-vad-readme
    resource: ../raw/silero-vad.md
    kind: documentation
    title: Silero VAD README
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
---

Silero VAD by the Silero Team is a MIT-licensed pre-trained enterprise-grade Voice Activity Detector that reports sub-1 ms processing per 30+ ms audio chunk on a single CPU thread with up to 4–5x further speedup under ONNX, a ~2 MB JIT footprint, training coverage across 6000+ languages, 8000/16000 Hz sampling-rate support, and PyTorch plus ONNX portability with pip and `torch.hub` entry points and a `get_speech_timestamps` API (**Reported**).[^silero-vad-readme]

## Identity and license

- Pre-trained enterprise-grade Voice Activity Detector from the Silero Team; repository `snakers4/silero-vad` with PyPI package `silero-vad` (**Reported**).[^silero-vad-readme]
- Published under a permissive MIT license with no telemetry, keys, registration, built-in expiration, or vendor lock stated (**Reported**).[^silero-vad-readme]
- Citation fence names Silero Team (2024), GitHub repository publisher, contact `hello@silero.ai`, Telegram chats, issue/discussion trackers, and project wiki pointers (**Reported**).[^silero-vad-readme]

## Key characteristics

- Accuracy positioning: described as stellar with excellent speech-detection results, deferred to the external Quality Metrics wiki comparison against other solutions (**Reported**).[^silero-vad-readme]
- Speed: one 30+ ms audio chunk takes less than 1 ms on a single CPU thread; batching or GPU improves performance further and ONNX may run up to 4–5x faster under certain conditions, with details deferred to the external Performance Metrics wiki (**Reported**).[^silero-vad-readme]
- Footprint: JIT model around two megabytes (**Reported**).[^silero-vad-readme]
- Generality: trained on corpora covering over 6000 languages and stated to perform well across domains with varied background noise and quality levels (**Reported**).[^silero-vad-readme]
- Sampling rates: supports 8000 Hz and 16000 Hz, deferred to the external sample-rate comparison (**Reported**).[^silero-vad-readme]
- Portability: benefits from PyTorch and ONNX ecosystems and runs everywhere those runtimes are available (**Reported**).[^silero-vad-readme]

## Requirements and installation

- Python examples on `x86-64` need Python 3.8+, 1 GB+ RAM, and a modern CPU with AVX, AVX2, AVX-512, or AMX instruction sets; the model itself needs only `torch>=1.12.0` when audio is loaded by the caller as a 1-D float32 `torch.Tensor` (**Reported**).[^silero-vad-readme]
- Optional extras: `silero-vad[audio]` (`torchaudio>=0.12.0,<2.10` plus `torchcodec` on Python 3.9+, `read_audio`/`save_audio` use), `silero-vad[codec]` (`torchcodec`, `read_audio`/`save_audio` with no torchaudio), `silero-vad[onnx-cpu]` (`onnxruntime>=1.16.1`, `numpy`, ONNX and sequence models), `silero-vad[onnx-gpu]` (`onnxruntime-gpu>=1.16.1`, `numpy`, ONNX on GPU), `silero-vad[all]` (everything) (**Reported**).[^silero-vad-readme]
- Audio-backend notes: `[audio]` pulls in torchcodec on Python 3.9+ because `torchaudio>=2.9` hands decoding to it; torchcodec needs system FFmpeg 4–9; on Python 3.8 pip resolves an older torchaudio that decodes on its own; bundled `read_audio`/`save_audio` work with either torchaudio or torchcodec, with torchcodec resampling through FFmpeg rather than `torchaudio.transforms.Resample` so resampled files can differ by ~1e-3 (**Reported**).[^silero-vad-readme]
- Torchaudio backend options: FFmpeg (`conda install -c conda-forge 'ffmpeg<7'`), `sox_io` (`apt-get install sox`, tested on libsox 14.4.2), or `soundfile` (`pip install soundfile`) (**Reported**).[^silero-vad-readme]
- Pure `onnxruntime` use runs on any supported ONNX Runtime architecture but requires implementing I/O and adapting wrappers, examples, and post-processing (**Reported**).[^silero-vad-readme]
- Install fences: `pip install silero-vad[audio]` or plain `pip install silero-vad` when loading audio without helpers (**Reported**).[^silero-vad-readme]

## Usage

- Pip fence: `load_silero_vad`, `read_audio`, `get_speech_timestamps` with `model = load_silero_vad()`, `wav = read_audio('path_to_audio_file')`, and `get_speech_timestamps(wav, model, return_seconds=True)` returning speech timestamps in seconds instead of samples (**Reported**).[^silero-vad-readme]
- `torch.hub` fence: `torch.set_num_threads(1)` then `model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')` with `(get_speech_timestamps, _, read_audio, _, _) = utils` before the same `read_audio` plus `get_speech_timestamps(..., return_seconds=True)` call (**Reported**).[^silero-vad-readme]

## Deployment and ecosystem

- C++ ONNX Runtime example, ExecuTorch C++ example, browser VAD via ONNX Runtime Web, and community Rust, Rust wavekat-VAD WAV processing, Go, Java, C#, and other examples (**Reported**).[^silero-vad-readme]
- OpenVINO conversion guidelines, optional offline ONNX sequence inference for long recordings, and a tinygrad model plus pico example with separate safetensors weights (16 kHz model provided) (**Reported**).[^silero-vad-readme]
- Versioning, model variants, quality/performance numbers, examples/dependencies, FAQ, and further reading are deferred to the external wiki pages for Examples and Dependencies, Quality Metrics, Performance Metrics, Versions and Available Models, FAQ, and silero-models further reading (**Reported**).[^silero-vad-readme]

## Versions and streaming configuration (secondary report)

- Release line per a 10/2026 AI-compiled report: v5.0 (27/06/2024) → v6.0 (25/08/2025) → v6.2 (12/2025) → v6.2.1 (24/02/2026, ONNX Runtime made optional); v6 is described as a drop-in for v5 with the same API (`load_silero_vad`, `VADIterator`, `get_speech_timestamps`), and vendor v6 claims are "16% less errors on noisy real-life data" and "11% less errors on multi-domain", with remaining weak spots on instrument music resembling voice and very high-pitched voices; whisper.cpp ships `silero-v6.2.0` and browser `@ricky0123/vad-web` supports v6 since 09/2026 (**Reported**).[^claude-pipeline-report]
- From v5 the window is fixed at 512 samples (32 ms) at 16 kHz or 256 at 8 kHz and `window_size_samples` is deprecated (**Reported**).[^claude-pipeline-report]
- Streaming practice: prefer `load_silero_vad(onnx=True)` to avoid loading torch in CPU workers; one stateful `VADIterator` per session with `reset_states()` at each turn end; noisy-environment starting values `threshold=0.5` (0.6–0.7 with heavy background noise; `VADIterator` applies ~0.15 lower off-threshold hysteresis), `min_silence_duration_ms=200–300` so a turn detector decides quickly, `speech_pad_ms=100–200` to keep initial/final consonants important for Vietnamese tones, and `min_speech_duration_ms=250` (**Reported**).[^claude-pipeline-report]
- Turn-level use with end-of-turn detection and barge-in gating is covered in [Turn Detection Models](turn-detection-models.md) and [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) (**Synthesis**).[^claude-pipeline-report]

## Typical use cases

- Voice activity detection for IoT, edge, and mobile; data cleaning and preparation plus voice detection in general; telephony and call-center automation plus voice bots; voice interfaces (**Reported**).[^silero-vad-readme]

## Relationships

- Used by [Faster-Whisper](faster-whisper.md): that CTranslate2 Whisper reimplementation exposes Silero VAD through `vad_filter` plus `vad_parameters` with conservative silence defaults; consult that page for batched inference, quantization, and benchmark context around the filter (**Synthesis**).[^silero-vad-readme]
- Used by [Parakeet ASR Server](parakeet-asr-server.md): that Go server optionally bundles `silero_vad.onnx` for VAD-based long-audio chunking with mel-energy and midpoint fallbacks; consult that page for the serving, chunking, and operational context (**Synthesis**).[^silero-vad-readme]
- Used by [RealtimeSTT](realtimestt.md): that Python library uses WebRTC/Silero VAD gating and a `silero-onnx-cpu` extra for recorder smoke tests and live-microphone use; consult that page for engine profiles and the production server around VAD-gated capture (**Synthesis**).[^silero-vad-readme]
- Used by [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md) and [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md): those LLM-generated drafts propose gateway endpointing defaults (threshold 0.5, 500 ms silence, 200 ms pre-roll) and always-on interruption scoring on top of this VAD; treat their parameters as unmeasured starting points (**Synthesis**).[^silero-vad-readme]
- Referenced by [Community-Reported Local ASR/TTS Selection](community-asr-tts-selection.md): that draft names Silero VAD as the only open-weight VAD in a local ASR/TTS thread; treat those install and usage anecdotes as unverified alongside this page's source-reported characteristics (**Synthesis**).[^silero-vad-readme]

- Recommended VAD in [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) and built into Pipecat per [Voice Agent Frameworks](voice-agent-frameworks.md) (**Synthesis**).[^claude-pipeline-report]

## Contradictions

- TEN VAD versus Silero: TEN VAD (Agora/TEN, Apache-2.0 with conditions, 10/16 ms hop) is vendor-claimed more accurate than Silero and WebRTC VAD with 32% lower RTF and an 86% smaller library, while a small community NOVA-VAD benchmark with UrbanSound8K noise reports Silero F1 91.9% versus TEN-VAD 69.2%; the report recommends measuring on own data and keeping Silero by default, considering TEN only when 10 ms frames are needed, so neither claim is chosen here (**Reported**).[^claude-pipeline-report]

## Coverage and limits

- Version history, v6 noise claims, and streaming parameters come from a secondary AI-compiled report whose GitHub release notes and benchmarks are not in `raw/` (**Synthesis**).[^claude-pipeline-report]
- Source inspected statically only; no `pip install`, `torch.hub` load, audio read, timestamp extraction, ONNX run, or latency/footprint measurement was executed, and no accuracy, speed, multilingual-coverage, or resampling-difference figure was reproduced (**Synthesis**).[^silero-vad-readme]
- Referenced but unfetched and absent from `raw/`: external wiki pages for Examples and Dependencies, Quality Metrics, Performance Metrics, Versions and Available Models, and FAQ; silero-models further reading; Colab notebook; CI workflow; header/figure images and demo video; `examples/` trees (C++, Rust, Go, Java, C#, OpenVINO, ONNX sequence), tinygrad model and safetensors weights, and browser/Rust ports; Hugging Face download destination; all install and inference fences above are transcribed, not executed (**Synthesis**).[^silero-vad-readme]
- All capability, compatibility, performance, and licensing claims are source assertions without independent verification; install matrices, backend versions, benchmark figures, and release details carry `stale_after: 2027-10-06` per the `vad` domain rule (**Synthesis**).[^silero-vad-readme]

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `TL;DR` VAD bullets; `PHẦN 1` §1 VAD table (Silero version/date/license/frame/size/noise cells, TEN VAD, WebRTC, pyannote rows) and `Kết luận VAD`; `PHẦN 2` `Silero VAD: tham số đề xuất` (version, ONNX vs JIT, noisy-environment parameters, adaptive threshold); `Caveats` (Silero 16% and TEN-vs-Silero are vendor/small-benchmark claims).

[^silero-vad-readme]: [Silero VAD README](../raw/silero-vad.md) — locators: header (`Silero VAD`, pre-trained enterprise-grade Voice Activity Detector, STT-models pointer, illustration/demo-video block); `Fast start` (pip fence `pip install silero-vad[audio]` / plain `pip install silero-vad`, `load_silero_vad` + `read_audio` + `get_speech_timestamps(..., return_seconds=True)` fence; `torch.hub` fence with `torch.set_num_threads(1)` and `torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')`); `Dependencies` collapsible (x86-64 Python 3.8+/1G+ RAM/AVX-family note, `torch>=1.12.0`, extras table `[audio]`/`[codec]`/`[onnx-cpu]`/`[onnx-gpu]`/`[all]` with version bounds, torchcodec/FFmpeg 4–9 note, Python 3.8-vs-3.9 torchaudio behavior, 1-D float32 Tensor note, torchaudio-vs-torchcodec I/O note with ~1e-3 resampling difference, FFmpeg/sox_io/soundfile backend options, pure-`onnxruntime` I/O-and-wrapper caveat); `Key Features` (accuracy with Quality-Metrics link, <1 ms per 30+ ms chunk plus batching/GPU and 4–5x ONNX note with Performance-Metrics link, ~2 MB JIT size, 6000+ languages generality, 8000/16000 Hz support with Quality-Metrics sample-rate link, PyTorch/ONNX portability, MIT no-strings-attached note); `Typical Use Cases` (IoT/edge/mobile, data cleaning/preparation, telephony/call-center/voice bots, voice interfaces); `Links` (Examples-and-Dependencies, Quality/Performance Metrics, Versions-and-Available-Models, Further-reading, FAQ); `Get In Touch` (issue/discussion links, Telegram, `hello@silero.ai`, news, wiki pointer) plus `Citations` BibTeX block; `Examples and VAD-based Community Apps` (C++ ONNX, ExecuTorch C++, browser ONNX Runtime Web, Rust/wavekat/Go/Java/C++/C# community list, OpenVINO guidelines, offline ONNX sequence inference, tinygrad model plus safetensors weights).
