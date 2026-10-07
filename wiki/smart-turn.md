---
type: Concept
title: Smart Turn v3.2
description: Pipecat's BSD-2 audio-native semantic end-of-turn detector: Whisper Tiny encoder plus a linear head at ~8M params, 23 languages including Vietnamese, int8 CPU and fp32 GPU ONNX variants, and a 31,527-sample per-language benchmark.
tags: [vad, endpointing, turn-detection, multilingual, onnx, edge]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:04:00Z }
stale_after: 2027-10-07
sources:
  - id: smart-turn-v3.2
    resource: ../raw/smart-turn/README.md
    scope: ../raw/smart-turn/
    kind: documentation
    revision: github 4786657e242dfe77dd138699ac564ee074a2a543; hf f766f81d3cfdf7737ac64aad813d91bbfd56bf93
    title: Smart Turn v3.2 (pipecat-ai) capture
---

Smart Turn v3.2 is pipecat-ai's open-source, audio-native semantic end-of-turn (endpointing) model: a Whisper Tiny encoder with a shallow linear classifier, about 8M parameters, that decides from raw 16 kHz PCM whether a speaker has finished a turn rather than from a transcript. It is BSD-2-Clause with open weights, datasets, and training script, ships as an 8 MB int8 ONNX (CPU) or 32 MB fp32 ONNX (GPU) checkpoint, supports 23 languages including Vietnamese, and is designed to run on top of a lightweight VAD once silence is detected (**Reported**).[^smart-turn-v3.2]

## Identity and license

- Publisher `pipecat-ai`; part of the [Pipecat](voice-agent-frameworks.md) ecosystem (**Reported**).[^smart-turn-v3.2]
- BSD-2-Clause (`bsd-2-clause`), open weights, datasets, and training script; Hugging Face `pipeline_tag: voice-activity-detection` with `speech-processing`, `semantic-vad`, and `multilingual` tags (**Reported**).[^smart-turn-v3.2]
- Captured at GitHub commit `4786657e242dfe77dd138699ac564ee074a2a543` (`github/README.md`) and Hugging Face revision `f766f81d3cfdf7737ac64aad813d91bbfd56bf93` (`hf/README.md`) on 2026-10-07 UTC (**Observed** by static inspection of the capture and its manifest).[^smart-turn-v3.2]

## Architecture and variants

- Backbone: Whisper Tiny encoder; head: shallow linear classifier; transformer-based, approximately 8M parameters (**Reported**).[^smart-turn-v3.2]
- Two checkpoints: an 8 MB int8-quantized ONNX for CPU and a 32 MB unquantized (fp32) ONNX for GPU; the GPU variant runs slightly faster on GPUs and is about 1% more accurate, while the CPU variant is significantly smaller and faster for CPU inference at a slight accuracy cost (**Reported**).[^smart-turn-v3.2]
- Audio-native: the model consumes PCM samples directly, so it can use prosody rather than depending on STT quality (**Reported**).[^smart-turn-v3.2]
- Earlier architecture experiments included wav2vec2-BERT, wav2vec2, LSTM, and additional transformer classifier layers (**Reported**).[^smart-turn-v3.2]
- Latency claims: as little as 10 ms on some CPUs and under 100 ms on most cloud instances; Pipecat Cloud is reported at around 65 ms on a standard 1x instance with `LocalSmartTurnAnalyzerV3` (**Reported**).[^smart-turn-v3.2]

## Input and operating protocol

- Input is 16 kHz mono PCM; up to 8 seconds of audio is supported, and the full current user turn is recommended (**Reported**).[^smart-turn-v3.2]
- Designed to run after a lightweight VAD such as [Silero VAD](silero-vad.md) detects silence, on the entire recording of the user's turn (**Reported**).[^smart-turn-v3.2]
- If the turn is longer than 8 s, truncate from the beginning; if shorter, zero-pad at the beginning so the audio sits at the end of the input vector (**Reported**).[^smart-turn-v3.2]
- If more user speech arrives before inference finishes, re-run on the whole turn recording including the new audio, not just the new segment; audio from previous turns is not needed and very short segments are not the intended input (**Reported**).[^smart-turn-v3.2]
- The bundled `record_and_predict.py` utility streams from the system microphone, segments start/stop with VAD, and predicts a phrase endpoint per segment; it requires PortAudio development libraries for PyAudio (**Reported**).[^smart-turn-v3.2]

## Benchmark

The vendor benchmark report covers 31,527 samples across 23 languages and 12 datasets, generated 2026-01-07 UTC. Overall performance differs modestly between the GPU fp32 and CPU int8 checkpoints (**Reported**).[^smart-turn-v3.2]

| Variant | Accuracy | Precision | Recall | F1 | FPR | FNR |
|---|---:|---:|---:|---:|---:|---:|
| GPU fp32 | 93.71% | 0.931 | 0.944 | 0.937 | 3.51% | 2.78% |
| CPU int8 | 92.63% | 0.909 | 0.947 | 0.927 | 4.73% | 2.64% |

Vietnamese is the weakest of the 23 languages in both variants (1,004 samples); the strongest languages are Korean, Japanese, Turkish, Dutch, and German (**Reported**).[^smart-turn-v3.2]

| Vietnamese metric | GPU fp32 | CPU int8 |
|---|---:|---:|
| Accuracy | 82.47% | 79.38% |
| Precision | 0.814 | 0.811 |
| Recall | 0.840 | 0.764 |
| F1 | 0.826 | 0.786 |
| FPR | 9.56% | 8.86% |
| FNR | 7.97% | 11.75% |

- Per-dataset accuracy spread on the GPU checkpoint runs from 98.85% (`midcentury_1`) down to 87.70% (`mundo_1`), with the large `chirp3_1` (16,254 samples) at 94.80% and `chirp3_2` (8,428 samples) at 90.76% (**Reported**).[^smart-turn-v3.2]
- The CPU checkpoint trades FNR for FPR relative to GPU on Vietnamese (recall 0.764 vs 0.840, FPR 8.86% vs 9.56%), so variant choice shifts which turn-taking failure mode dominates (**Synthesis**).[^smart-turn-v3.2]

## Integration and training

- Native Pipecat support via `LocalSmartTurnAnalyzerV3` (available in v0.0.85); the [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) enables a v3.2 CPU checkpoint by default (**Reported**).[^smart-turn-v3.2]
- Local inference imports `model.py` and `inference.py` and calls `predict_endpoint()`; `predict.py` and `record_and_predict.py` are the usage examples (**Reported**).[^smart-turn-v3.2]
- Training code is `train.py`, runnable locally or via `train_modal.py` on Modal with optional Weights & Biases logging; it downloads datasets from the `pipecat-ai` Hugging Face organization and is intended to be easy to fine-tune for specific applications (**Reported**).[^smart-turn-v3.2]
- Stated goals: a state-of-the-art, permissively usable, production-deployable, fine-tunable turn detector; medium-term work targets more languages, architecture/optimization experiments, more human data, and text conditioning for modes such as credit-card, phone-number, and address entry (**Reported**).[^smart-turn-v3.2]

## Relationships

- Depends on [Silero VAD](silero-vad.md) (or another VAD) to signal silence before invocation (**Synthesis**).[^smart-turn-v3.2]
- Compared against LiveKit, Namo, and TEN detectors, and its operating practice described, in [Turn Detection Models](turn-detection-models.md) (**Synthesis**).[^smart-turn-v3.2]
- Used by [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) as its default endpointing classifier and by Pipecat-based [voice-agent frameworks](voice-agent-frameworks.md) (**Reported**).[^smart-turn-v3.2]
- Contrasts with [Parakeet Realtime EOU 120M v1](parakeet-realtime-eou-120m-v1.md), which folds end-of-utterance detection into a streaming English ASR model instead of a separate audio classifier (**Synthesis**).[^smart-turn-v3.2]

## Contradictions

Recorded but not chosen:

- **Training dataset version:** the GitHub README names `pipecat-ai/smart-turn-data-v3.2-train` and `-v3.2-test`, while the Hugging Face model card frontmatter lists `pipecat-ai/smart-turn-data-v3.1-train` and `-v3.1-test`. The benchmark report does not state which split or dataset version produced its per-language numbers.[^smart-turn-v3.2]

## Coverage and limits

- The four captured Markdown files were inspected statically; their SHA-256 digests and byte lengths were recomputed and match `checksums.json` (capture integrity **Observed**).[^smart-turn-v3.2]
- Excluded from the capture: `docs/data_generation_contribution_guide.md`, training and inference source code, the v3.0 and v3.1 benchmark files, and the ONNX weights; no weights, code, or audio were downloaded, and nothing was executed or reproduced (**Observed** exclusion; benchmark figures remain **Reported**).[^smart-turn-v3.2]
- All accuracy, FPR/FNR, and latency figures are vendor reports asserted in the captured docs; no independent verification or reproduction was performed. `stale_after` is set because model releases and benchmark numbers are time-sensitive.[^smart-turn-v3.2]

[^smart-turn-v3.2]: [Smart Turn v3.2 package](../raw/smart-turn/README.md) — a capture at GitHub commit `4786657e242dfe77dd138699ac564ee074a2a543` and Hugging Face revision `f766f81d3cfdf7737ac64aad813d91bbfd56bf93` (2026-10-07). Locators: `github/README.md` → Features (23 languages incl. Vietnamese, 10 ms CPU / under 100 ms cloud, CPU 8 MB int8 vs GPU 32 MB fp32, ~1% accuracy note, audio-native, fully open source), Run the model locally (`record_and_predict.py`, PortAudio), Model usage (`LocalSmartTurnAnalyzerV3` v0.0.85, Pipecat Cloud ~65 ms, `predict_endpoint()`), Notes on input format (16 kHz mono PCM, 8 s window, padding/truncation, re-run on whole turn), Project goals, Model architecture (Whisper Tiny + linear classifier, 8M params, int8/fp32, wav2vec2/LSTM experiments), Training (`train.py`, `train_modal.py`, W&B, v3.2 datasets); `hf/README.md` → frontmatter (`license: bsd-2-clause`, `pipeline_tag: voice-activity-detection`, v3.1 datasets), Model architecture, How to use, Thanks; `hf/benchmarks/smart-turn-v3.2-gpu.md` and `hf/benchmarks/smart-turn-v3.2-cpu.md` → title, `Model`, `Generated`, `Total Samples` 31,527, `Unique Languages`, `Unique Datasets`, and the Overall, Performance by Language (Vietnamese 1,004 samples), and Performance by Dataset tables. Limitations: no weights, code, v3.0/v3.1 benchmarks, or blog post captured; no execution, download, or benchmark reproduction.
