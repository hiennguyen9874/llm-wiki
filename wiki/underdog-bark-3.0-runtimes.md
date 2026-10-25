---
type: Concept
title: Underdog Bark 3.0 Platform Runtimes
description: Execution matrix for Underdog Bark 3.0 on Transformers, MLX/mlx-audio, macOS Core ML GPU and ANE packages, an iOS Core ML embedding contract, and Windows CUDA/CPU, with pinned versions, file manifests, and the card's unqualified paths.
tags: [stt, asr, on-device, coreml, ios, macos, windows, mlx, apple-silicon, deployment]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T02:49:29Z }
stale_after: 2027-10-25
sources:
  - id: bark-3.0-card
    resource: ../raw/ConwayResearch-Underdog-Bark-3.0.md
    kind: documentation
    title: Underdog Bark 3.0 (verbatim) model card
---

The [Underdog Bark 3.0](underdog-bark-3.0.md) card ships one checkpoint with several mutually exclusive execution packages: the original Python paths (`bark_loader.py` on Transformers, `bark_mlx.py` on mlx-audio), Core ML packages for Apple GPU or Neural Engine on macOS 15+, the same Core ML files embedded in an iOS 18 app through a documented Swift porting contract, and a Windows PyTorch runtime for NVIDIA CUDA or CPU (**Reported**).[^bark-3.0-card] Each route is a separate download of the same weights, and the card's only general warning is that download size is not runtime memory: the packed `model.bark` is expanded in memory before inference (**Reported**).[^bark-3.0-card] On the sibling Clean release the 180 MB download unpacks to 1.25 GB, so plan RAM or VRAM from the unpacked size (**Reported** for Clean; transfer is **Synthesis**).[^bark-3.0-card]

## Choose a route

| Route | Platform requirement | Entry point | Package to download |
| --- | --- | --- | --- |
| Transformers / PyTorch | Linux, macOS, or Windows; Python | `bark_loader.py model.bark recording.wav`, or `load_model(...)` + `transcribe(...)` with `device` set to `cuda`, `cpu`, or `mps` | `model.bark`, `bark_loader.py`, `NOTICE` |
| mlx-audio | Apple silicon | `python bark_mlx.py recording.wav` | `model.bark`, `bark_mlx.py`, `mlx/*` |
| Core ML GPU | Apple silicon, macOS 15+, Python 3.11 | `python coreml/gpu/bark_coreml.py recording.wav --units gpu` | `coreml/gpu/*`, `coreml/LICENSE`, `coreml/NOTICE`, `runtime/requirements-coreml.txt` |
| Core ML ANE | Apple silicon, macOS 15+, Python 3.11 | `python coreml/ane/bark_coreml.py recording.wav --units ane` | `coreml/ane/*`, `coreml/LICENSE`, `coreml/NOTICE`, `runtime/requirements-coreml.txt` |
| iOS app | iOS 18+ (device path untested by the vendor) | `BarkEncoder.mlpackage` + `decoder.npz` + `vocab.json` inside an Xcode target | `coreml/ane/` or `coreml/gpu/` |
| Windows CUDA | 64-bit Python 3.11, NVIDIA GPU, CUDA 12.8-compatible driver | `runtime\transcribe_bark.py --model bark-model --audio recording.wav --device cuda` | `model.bark`, `bark_loader.py`, `NOTICE`, `runtime/transcribe_bark.py`, `runtime/requirements-windows.txt` |
| Windows CPU | 64-bit Python 3.11 | same script with `--device cpu` | same as CUDA, CPU torch wheel |

All rows are **Reported** from the card's command fences; none was executed for this page (**Synthesis**).[^bark-3.0-card]

## Pinned versions

- Original Python route: `huggingface_hub==2.2.0`, `transformers==5.19.0`, `torch==2.8.0`, `constriction==0.5.0`, `numpy==2.4.6`, `soundfile==0.14.0`, `soxr==1.1.0`, `librosa==0.11.0` (**Reported**).[^bark-3.0-card]
- Apple silicon mlx-audio route: `mlx==0.32.2`, `mlx-audio==0.5.3`, `constriction==0.5.0`, `numpy==2.4.6`, `soundfile==0.14.0`, `soxr==1.1.0` (**Reported**).[^bark-3.0-card]
- Core ML route: `huggingface_hub==2.2.0` plus `runtime/requirements-coreml.txt`, which the card does not reproduce; the Python version is pinned to 3.11 and the OS floor to macOS 15 (**Reported**; the requirements file's contents are an unread limit).[^bark-3.0-card]
- Windows route: `torch==2.8.0` from the `cu128` or `cpu` index plus `runtime/requirements-windows.txt`, again not reproduced in the card (**Reported**).[^bark-3.0-card]
- The exact-pin style matters for reproduction because every throughput number in this family is tied to one build: the card states that unpacking is exact so the weights loaded are the weights measured, which covers weights but not the runtime stack (**Reported**; the limitation is **Synthesis**).[^bark-3.0-card]

## Core ML on macOS

- Two alternative packages for the same model, not a cascade: the GPU route runs supported encoder operations on the Apple GPU and the ANE route on the Neural Engine, while both keep audio preprocessing and greedy text decoding on the CPU; Core ML decides operation placement, so neither package runs everything on the accelerator (**Reported**).[^bark-3.0-card]
- Both retain the source quantized weight values, with FP16 encoder arithmetic and FP32 preprocessing and decoding (**Reported**).[^bark-3.0-card]
- Window policy differs: the GPU package uses a fixed 15-second encoder, while the ANE package shares weights between 8-second and 15-second encoder functions and selects the smallest window that fits the clip (**Reported**).[^bark-3.0-card]
- Cost of the first run: model loading and first-use Core ML compilation can take several minutes, and the card advises keeping a `Transcriber` instance alive across requests to avoid reloading — directly relevant to a voice loop, where per-turn process restarts would dominate latency (**Reported**; implication is **Synthesis**).[^bark-3.0-card]
- The long-recording path is explicitly unqualified on Core ML: only short recordings are validated, and segmentation for long audio "has not been qualified" (**Reported**).[^bark-3.0-card]

## iOS embedding contract

- Requirements: iOS 18 or later; the encoder is a Core ML multifunction model exposing `w8` and `w15` in the ANE package and `w15` in the GPU package; the model files are the same ones used on the Mac and nothing is converted for iOS (**Reported**).[^bark-3.0-card]
- Files an app needs from one package: `BarkEncoder.mlpackage` (about 185 MB), `decoder.npz` (11 MB), and `vocab.json`; the `.mlpackage` is added to the Xcode target, which compiles it to `.mlmodelc` at build time, or it can be compiled once on device with `MLModel.compileModel(at:)` and the compiled copy kept (**Reported**).[^bark-3.0-card]
- Encoder configuration: `MLModelConfiguration.computeUnits` set to `.cpuAndNeuralEngine` (ANE) or `.cpuAndGPU` (GPU) with `functionName` set to `w8` or `w15`; inputs are `features`, FP16 `[1, T, 128]` with `T = window_seconds * 100 + 1`, and `mask`, Int32 `[1, T]`; output is `encoded`, `[1, T', 640]` (**Reported**).[^bark-3.0-card]
- The two CPU stages must be ported to Swift, because iOS has no Python: a `Frontend` (pre-emphasis, centred STFT, mel filters from `mel_filters` in `decoder.npz`, log, per-utterance normalization) and a `Decoder` (2-layer LSTM plus joint head, with int8 `*.q` weights times per-row FP16 `*.s` scales); `bark_coreml.py` is named as the reference implementation to port line by line and compare transcripts against on the Mac (**Reported**).[^bark-3.0-card]
- `decoder.npz` is a zip of `.npy` arrays to be read in Swift or converted once to raw arrays (**Reported**).[^bark-3.0-card]
- Input handling must match `bark_coreml.py`: mono 16 kHz float audio, 0.25 s of leading silence, the smallest window that holds the clip, and longer audio cut at pauses into pieces of at most 15 s (**Reported**).[^bark-3.0-card]
- Status warning: the card states the iOS path is "Not yet tested on an iPhone or iPad", so the contract is a specification rather than a vendor-verified result (**Reported**, negative finding).[^bark-3.0-card]
- Escape hatch that avoids porting the decoder: Bark 3.0 Pro ships frontend, encoder, decoder and joint as Core ML models, runs through the FluidAudio Swift package, and has iOS instructions, at 1.23 GB instead of about 200 MB (**Reported**).[^bark-3.0-card]

## Windows CUDA or CPU

- Windows reuses `model.bark` and the original `bark_loader.py`, not the Core ML packages; the loader expands the packed weights to FP32 in memory, so the download size is not the RAM or VRAM requirement (**Reported**).[^bark-3.0-card]
- It is a PyTorch runtime, explicitly not an ONNX/DirectML or native low-bit CUDA export; the CUDA path is stated to have been tested on Windows with an NVIDIA GPU, and other GPUs must use the CPU path (**Reported**).[^bark-3.0-card]
- The CUDA wheel comes from `https://download.pytorch.org/whl/cu128`; the CPU path replaces it with `.../whl/cpu` in a fresh environment and then runs the same script with `--device cpu` (**Reported**).[^bark-3.0-card]
- The entry point fails explicitly when the requested accelerator is unavailable, downmixes and resamples input, and preserves the original loader's per-model padding (**Reported**).[^bark-3.0-card]
- First use needs internet access to fetch the NVIDIA processor and generation configuration — not NVIDIA model weights — and `hf auth login` is required when repository access needs authentication (**Reported**).[^bark-3.0-card]

## Measured behaviour shared by all routes

- One-pass transcription: stock mlx-audio processes a whole file at once, so memory grows with length — a 10-minute file peaked at about 15 GB on a 16 GB M2, and the card advises splitting long recordings into a few-minute pieces on 8 or 16 GB Macs (**Reported**).[^bark-3.0-card]
- Batch throughput is not streaming: the card's only speed figures are whole-file rates (41× realtime on an M2 via mlx-audio), and no route in this card exposes partial hypotheses or a chunk clock (**Reported**; the distinction is **Synthesis**).[^bark-3.0-card]
- Padding convention conflict: this card says `transcribe` adds 0.25 s of pre-audio silence and that the benchmark numbers use it, while the sibling Clean card says `transcribe` adds none; treat the exact measurement conditions of the reported WER as unresolved (**Reported**; see [Underdog Bark 3.0](underdog-bark-3.0.md#contradictions)).[^bark-3.0-card]

## Relationships

- Serves [Underdog Bark 3.0](underdog-bark-3.0.md) and, through the same `model.bark` format and loader, the [Bark 3.0 Clean](underdog-bark-3.0-clean.md) dictation variant (**Synthesis** from both cards).[^bark-3.0-card]
- The iOS contract here is the concrete instance of a recurring pattern in this wiki — a Core ML encoder plus a hand-ported CPU decoder — that [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) derivatives face too: [Parakeet Redux](parakeet-redux.md) ships Photon instead, and [TheWhisper-Large-v3-Turbo](thewhisper-large-v3-turbo.md) packages the whole pipeline in Core ML for Apple platforms (**Reported** for those pages; the pattern is **Synthesis**).
- For voice-loop deployment the routes differ in what they can promise: native Swift/MLX and Core ML give on-device English dictation without a server, but none of them offers the streaming VAD-plus-partial contract that [Parakeet Realtime EOU 120M V1](parakeet-realtime-eou-120m-v1.md) or [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) document, so Bark 3.0 fits push-to-talk or chunked-turn capture rather than always-on barge-in (**Synthesis**).

## Coverage and limits

- One capture, `raw/ConwayResearch-Underdog-Bark-3.0.md`, read in full and inspected statically only; no route was installed, built, or run, and no Core ML or iOS package was downloaded (**Synthesis**).[^bark-3.0-card]
- Uninspected and excluded: `bark_loader.py`, `bark_mlx.py`, `bark_coreml.py`, `runtime/transcribe_bark.py`, `coreml/*` (including `BarkEncoder.mlpackage`, `decoder.npz`, `vocab.json`, `LICENSE`, `NOTICE`), `runtime/requirements-coreml.txt`, `runtime/requirements-windows.txt`, `mlx/config.json`, the tokenizer files, and the weights. Every API shape, tensor signature, and pin above is therefore the card's claim, not an inspection of the artifact (**Reported**; the limit is **Synthesis**).[^bark-3.0-card]
- Not covered by the card: Android, Linux-specific packaging beyond the generic PyTorch route, ONNX/DirectML export, batched or multi-stream serving, per-request warm-up guidance beyond "keep the instance alive", and Core ML latency or memory figures (**Synthesis**).[^bark-3.0-card]
- The pinned versions and platform floors make this page time-sensitive: `stale_after: 2027-10-25` follows the `stt` domain rule for model and API releases (**Synthesis**).[^bark-3.0-card]

[^bark-3.0-card]: [Underdog Bark 3.0 model card](../raw/ConwayResearch-Underdog-Bark-3.0.md) — locators: `## Run it` (pip `huggingface_hub==2.2.0`; `hf download ... --include "model.bark" --include "bark_loader.py" --include "bark_mlx.py" --include "mlx/*" --include "NOTICE"`; `transformers==5.19.0 torch==2.8.0 constriction==0.5.0 numpy==2.4.6 soundfile==0.14.0 soxr==1.1.0 librosa==0.11.0`; `python bark_loader.py model.bark recording.wav`; `load_model("model.bark", device="cuda")` plus `transcribe(model, wave.mean(1), sr)`; MLX fence `mlx==0.32.2 mlx-audio==0.5.3 ...` and `python bark_mlx.py recording.wav`; first-run unpack and cache; "Unpacking is exact"; `transcribe` adds 0.25 s of silence; 10-minute file peaking at ~15 GB on a 16 GB M2; split guidance for 8/16 GB Macs); `## Additional platform runtimes` preamble ("The original interfaces above remain available. Choose one runtime below and download only its files."); `### Mac: Core ML GPU or ANE` (macOS 15+, Python 3.11, GPU encoder operations on Apple GPU versus ANE on Neural Engine, CPU preprocessing and greedy decoding, Core ML operation placement, source quantized weight values with FP16 encoder arithmetic and FP32 preprocessing/decoding, fixed 15 s GPU encoder, ANE 8 s/15 s shared-weight functions with smallest-window selection, `BARK_BACKEND=ane|gpu`, download includes `coreml/$BARK_BACKEND/*` + `coreml/LICENSE` + `coreml/NOTICE` + `runtime/requirements-coreml.txt`, `bark_coreml.py recording.wav --units`, downmix/resample and printed transcript, long-recording segmentation not qualified, several-minute first-use compilation, keep `Transcriber` alive, `hf auth login`); `### iPhone and iPad (iOS)` (iOS 18+, multifunction encoder `w8`/`w15` ANE and `w15` GPU, same files as Mac, "**Not yet tested on an iPhone or iPad.**", `BarkEncoder.mlpackage` ~185 MB / `decoder.npz` 11 MB / `vocab.json`, Xcode `.mlmodelc` compilation or `MLModel.compileModel(at:)`, `MLModelConfiguration.computeUnits` `.cpuAndNeuralEngine`/`.cpuAndGPU`, `functionName` `w8`/`w15`, inputs `features` FP16 `[1, T, 128]` with `T = window_seconds * 100 + 1` and `mask` Int32 `[1, T]`, output `encoded` `[1, T', 640]`, Swift `Frontend` (pre-emphasis, centred STFT, `mel_filters`, log, per-utterance normalization) and `Decoder` (2-layer LSTM + joint head, int8 `*.q` × FP16 `*.s`), `bark_coreml.py` as reference implementation, `decoder.npz` as `.npy` zip, mono 16 kHz float input with 0.25 s leading silence, smallest window, cut at pauses into ≤15 s pieces, Bark 3.0 Pro whole-pipeline Core ML via FluidAudio at 1.23 GB instead of ~200 MB); `### Windows: NVIDIA CUDA or CPU` (64-bit Python 3.11, `model.bark` + original `bark_loader.py`, loader expands to FP32 so download ≠ RAM/VRAM, PyTorch rather than ONNX/DirectML or native low-bit CUDA, CUDA path tested on Windows with an NVIDIA GPU, `torch==2.8.0` from `download.pytorch.org/whl/cu128` or `/whl/cpu`, `runtime/transcribe_bark.py --model bark-model --audio recording.wav --device cuda|cpu`, explicit failure when the accelerator is unavailable, downmix/resample and original per-model padding, first use fetches the NVIDIA processor and generation configuration but not NVIDIA weights, `hf.exe auth login`); `## Benchmarks` (download sizes are weight-file sizes); `## Notes` (CC-BY-4.0 plus `NOTICE`).
