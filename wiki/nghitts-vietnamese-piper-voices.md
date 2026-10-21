---
type: Concept
title: NGHI-TTS Vietnamese Piper Voices (unofficial mirror)
description: Unofficial Hugging Face mirror of 18 named Vietnamese NGHI-TTS voices (21 variants) fine-tuned from Piper voices, shipped as Piper ONNX and Sherpa ONNX files with Python CPU/GPU/OpenVINO recipes and no quality, latency, or consent evidence.
tags: [tts, vietnamese, piper, vits, onnx, sherpa-onnx, edge]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T12:00:00Z }
stale_after: 2027-10-21
sources:
  - id: nghitts-mirror-card
    resource: ../raw/nghitts-copy.md
    kind: documentation
    title: Unofficial mirror of NGHI-TTS models (Hugging Face card capture)
---

The capture is the card of an unofficial third-party mirror of NGHI-TTS, a set of Vietnamese-only single-speaker voices fine-tuned from `rhasspy/piper-voices` (relation `finetune`, checkpoints from `rhasspy/piper-checkpoints`), distributed as original Piper ONNX files and as Sherpa-ONNX-converted copies, with Python recipes for CPU, NVIDIA GPU, Intel OpenVINO and streaming playback (**Reported**).[^nghitts-mirror-card] It is a deployment-friendly, CPU-class VITS-style option for Vietnamese TTS, but the card offers no quality, latency, sample-rate, size, training-data or voice-rights evidence, so it is a candidate to audition rather than a verified baseline (**Synthesis**).

## Identity and provenance

- Frontmatter: `license: apache-2.0`, `language: vi`, `pipeline_tag: text-to-speech`, `base_model: rhasspy/piper-voices` with `base_model_relation: finetune`, `datasets: rhasspy/piper-checkpoints`, `repo: https://github.com/nghimestudio/nghitts` (**Observed**).[^nghitts-mirror-card]
- The title says "unofficial mirror"; it points to an official Facebook-group announcement, the official repo `nghimestudio/nghitts`, and an official Google Drive download folder, none of which were fetched (**Reported**).[^nghitts-mirror-card] The mirror's author is not named in the capture, and no revision or date is recorded (**Observed** absence).
- The same `nghitts` upstream is named by [VietNormalizer](vietnormalizer.md) as the JavaScript project it was ported from, so the voices and the normalizer's text rules plausibly come from one project family; the capture itself does not mention normalization (**Synthesis**).

## Voices

The mirror states it contains only Vietnamese voices (**Reported**):[^nghitts-mirror-card]

- Ban Mai, Chiếu Thành, Duy Oryx (described as a very deep male voice), Lạc Phi, Mai Phương, Mạnh Dũng, Minh Khang (Kiến Giải Mã), Minh Quang, Minh Thu, Phương Trang, Thanh Phương Viettel, Thiện Tâm, Việt Thảo, Ngọc Ngạn, Trấn Thành.
- Two-version voices: Mỹ Tâm, Ngọc Huyền (labeled as film review), Tài An (labeled CD Media).
- That is 18 names and 21 variants by count (**Observed**). Only one file name, `ngocngan3701.onnx`, appears in examples; the mapping of the other names to file names is not in the capture.
- Several names match well-known Vietnamese public figures or brands. The card states no training data, consent, or licensing basis for them, and the blanket Apache-2.0 declaration does not address voice or likeness rights; treat deployment of such voices as unresolved until the official repo clarifies (**Synthesis**).

## Folder layout and formats

- `piper-tts/` holds the original ONNX files, usable directly with Piper TTS; examples load `piper-tts/config.json` alongside the model (**Reported**).[^nghitts-mirror-card]
- `sherpa-onnx/` holds ONNX files converted for Sherpa ONNX following the k2-fsa Piper conversion guide, plus a generated `tokens.txt` (**Reported**).[^nghitts-mirror-card]
- Sherpa also needs the `espeak-ng-data` archive from the sherpa-onnx `tts-models` release, extracted and passed as `data_dir`; see [eSpeak NG](espeak-ng.md) for the phonemizer (**Reported**).[^nghitts-mirror-card]

## Usage recipes

| Route | Install | Notes |
| --- | --- | --- |
| Piper, CPU | `pip install piper-tts` | `PiperVoice.load(onnx, config_path=...)`; `synthesize_wav` writes a WAV file |
| Piper, NVIDIA GPU | `piper-tts`, then replace `onnxruntime` with `onnxruntime-gpu` (comment says CUDA 13; a CUDA 12 extra index is given commented out) | `use_cuda=True` flag is shown only as a comment |
| Piper, Intel iGPU/CPU | `openvino==2025.4.1` plus `onnxruntime-openvino` (needs Python up to 3.13 at time of writing) | Build `PiperVoice` from an `onnxruntime` session with `OpenVINOExecutionProvider` and `device_type: HETERO:GPU,CPU`; Windows requires two `add_openvino_libs_to_path` lines |
| Sherpa ONNX, CPU | `pip install sherpa-onnx onnxruntime` | `OfflineTts` with VITS config (`model`, `tokens`, `data_dir`); `generate` returns samples written with `soundfile` |
| Sherpa ONNX, GPU | `sherpa-onnx` from the k2-fsa CUDA wheel page, CUDA 12 only at time of writing | `provider="cuda"` appears only as a comment |

All rows are **Reported**; none was executed here.[^nghitts-mirror-card]

- Synthesis variation: the examples pass `SynthesisConfig(noise_scale=1., noise_w_scale=1.)` with the comment "add more variation"; defaults are not stated in the capture (**Reported**).[^nghitts-mirror-card]
- Streaming: the Piper example iterates `TTS.synthesize(text)` and writes each chunk's float array to a `sounddevice` output stream, reading the sample rate and channels from a warm-up chunk. The chunk granularity (likely sentence-level) is not stated, and no time-to-first-audio is reported, so true low-latency streaming is unestablished (**Reported** usage; granularity **Unverified**).[^nghitts-mirror-card]
- OpenAI-compatible serving: the card links to an external gist that wraps Piper as an OpenAI-style endpoint; it was not fetched (**Reported**).[^nghitts-mirror-card] [Speaches](speaches.md) is a separate compiled server that also serves Piper models (**Synthesis**, compatibility with these voices untested).
- The mirror author reports failing to use OpenVINO from Python with Sherpa because "the source code is written in C"; the sentence follows the Sherpa section and its scope is ambiguous (**Reported**).[^nghitts-mirror-card]

## Pipeline fit

- Vietnamese text should be converted to spoken form before synthesis; [VietNormalizer](vietnormalizer.md) is the compiled candidate, and whether these voices expect normalized text, diacritic-complete NFC input or an espeak-ng Vietnamese phonemization is not stated (**Synthesis**).
- Piper/VITS-style graphs are non-autoregressive and small, which suits CPU edge deployment; see [sanoTTS](sanotts.md), which distills a Piper lineage, and [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) for how such candidates are gated. These traits are inferred from the Piper/Sherpa/VITS naming, not measured here (**Synthesis**).

## Coverage and limits

- Inspected statically: the entire 189-line capture `raw/nghitts-copy.md` (frontmatter, voice list, folder structure, sections 0, 1, 1.1 and 2) (**Observed**).
- Not inspected or unavailable: model weights, `config.json`, `tokens.txt`, the official repo, announcement and Drive folder, the Piper API doc, Sherpa guide, OpenAI-endpoint gist and OpenVINO provider docs. Nothing was downloaded, installed or executed; no audio was heard.
- Not stated: sample rate, parameter counts and file sizes, quality tier (low/medium/high), training data and hours, number of speakers per file, consent and likeness permissions, training recipe, WER/MOS/RTF, and the relation between Apache-2.0 here and the license of the upstream Piper checkpoints. The `piper1-gpl` API reference link suggests the Python runtime is GPL-licensed (inferred from the repo name only, **Unverified**); check before commercial embedding.
- Internal inconsistency: Piper examples load `piper-tts/config.json`, whereas the OpenVINO example reads `<model>.onnx.json`; whether per-voice configs exist is not shown. `stale_after` follows the `tts` domain rule for versions and install pins (OpenVINO 2025.4.1, CUDA 13/12).

## Relationships

- Related to [VietNormalizer](vietnormalizer.md): same named upstream (`nghitts`), complementary text front end (**Synthesis**).
- Alternative edge candidate in [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) alongside [Kokoro Vietnamese](kokoro-vietnamese.md) and [sanoTTS](sanotts.md) (**Synthesis**).
- Runtime kin: [Speaches](speaches.md) (Piper serving) and [eSpeak NG](espeak-ng.md) (phonemizer data needed by Sherpa VITS models) (**Synthesis**).

[^nghitts-mirror-card]: [Unofficial mirror of NGHI-TTS models](../raw/nghitts-copy.md) — locators: YAML frontmatter; `# unofficial mirror of NGHI-TTS models` (links, voice list, folder structure); `## 0. PiperTTS as OpenAI-compatible endpoint`; `## 1. with Piper TTS` (CPU/GPU install, WAV and streaming examples); `### 1.1. Intel CPU` (OpenVINO install and usage); `## 2. with Sherpa ONNX` (CPU/GPU install, example, closing OpenVINO remark).
