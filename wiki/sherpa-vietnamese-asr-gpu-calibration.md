---
type: Concept
title: Sherpa Vietnamese ASR GPU Device Calibration
description: How Sherpa Vietnamese ASR 2.6.x optionally benchmarks CPU against DirectML or OpenVINO per stage and keeps ASR, VAD, ffmpeg and clustering on CPU, with a 20% speed-gain rule, add-on install layout and pitfalls.
tags: [stt, pipeline, gpu, directml, openvino, onnx-runtime, calibration, windows, edge]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T22:00:00Z }
stale_after: 2027-04-21
sources:
  - id: sherpa-vi-readme
    resource: ../raw/sherpa-vietnamese-asr.md
    kind: documentation
    revision: "2.6.3 (README version badge)"
    title: welcomyou/sherpa-vietnamese-asr README capture
---

From version 2.6.2, [Sherpa Vietnamese ASR](sherpa-vietnamese-asr.md) can add an app-local GPU add-on and use a "Tối ưu thiết bị" (Optimize device) dialog that benchmarks CPU against the available GPU per stage and picks the GPU only for stages where it is measurably faster. The default install stays CPU-only; the core ASR encoder/decoder/joiner never moves to GPU (**Reported**).[^sherpa-vi-readme] The mechanism is useful as a pattern for per-stage execution-provider selection in ONNX Runtime pipelines, but all numbers come from the app's own dialog and no benchmark figures are published (**Synthesis**).

## Provider policy

| Hardware | Provider | Packages |
| --- | --- | --- |
| No GPU, or AMD CPU without GPU | CPUExecutionProvider | none |
| NVIDIA GPU | DirectML | DirectML add-on, plus GPU-models zip if the app reports it missing |
| AMD GPU or iGPU | DirectML | same as NVIDIA |
| Intel GPU or iGPU | OpenVINO | Intel OpenVINO add-on, plus GPU-models zip if missing |

CUDA is no longer published by default from 2.6.2 (**Reported**; GPU policy, Công nghệ).[^sherpa-vi-readme] The browser PWA is separate: it uses ONNX Runtime Web with WebGPU when available and falls back to WASM/CPU, and needs neither add-on (**Reported**).[^sherpa-vi-readme]

## Calibration rule

A stage uses the GPU only when its inference is at least 20% faster than CPU and the numerical difference stays within an allowed threshold; otherwise it runs on CPU. The speeds shown in the dialog are per-stage inference times, not total file processing time (**Reported**).[^sherpa-vi-readme] The README does not state the numerical tolerance, test audio, or number of repeats. Saved calibration results persist when switching between "CPU-only" and "GPU auto" (**Reported**).[^sherpa-vi-readme]

## Stages

| Eligible for GPU benchmark | Pinned to CPU by design |
| --- | --- |
| CAM++ speaker embedding (GPU graph generated from the CPU model on demand) | ASR encoder, decoder, joiner |
| Pyannote embedding encoder | ffmpeg decode and resample |
| DNSMOS quality | Silero VAD |
| ViBERT FP32 punctuation | Speaker segmentation, VBx, clustering, postprocessing |

(**Reported**; Stage GPU hiện tại.)[^sherpa-vi-readme] Consequence (**Synthesis**): GPU hardware shortens diarization, punctuation and quality scoring, not recognition itself, so a transcription speedup should not be assumed from adding a GPU.

## Install layout and pitfalls

- Extract the add-on zip into the application root so that `gpu_addons\directml\Lib\site-packages\onnxruntime\` or `gpu_addons\intel-openvino\Lib\site-packages\onnxruntime\` exists, and `models\vibert-capu\vibert-capu.onnx` for the GPU-models zip. An extra wrapper folder from the zip name breaks the layout (**Reported**).[^sherpa-vi-readme]
- After installing, fully close and reopen the app, then run the optimize dialog; choose CPU-only to revert (**Reported**).[^sherpa-vi-readme]
- Add-ons must match the app version (all 2.6.3 in the capture); GPU-models currently contains only the ViBERT-capu ONNX file (**Reported**).[^sherpa-vi-readme]
- Add-ons are built with `build-portable/build_gpu_addons.py directml intel-openvino` and `build_gpu_models.py` (**Reported**).[^sherpa-vi-readme]

## Coverage and limits

Single README capture, static inspection only; no installation, calibration run, driver check, or code review. The stated 20% threshold and tolerance behavior are **Reported**, not verified in code. No GPU speed, memory, or accuracy values are available. Stale after 2027-04-21 because add-on packaging and provider support change with releases.
