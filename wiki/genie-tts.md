---
type: Concept
title: Genie-TTS
description: Lightweight CPU-first ONNX inference engine for GPT-SoVITS V2/V2ProPlus with 1.13 s first-inference latency, 200 MB runtime, predefined multilingual characters, and FastAPI serving.
tags: [tts, voice-cloning, onnx, cpu-inference]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: genie-readme
    resource: ../raw/Genie-TTS.md
    kind: documentation
    title: GENIE GPT-SoVITS Lightweight Inference Engine README
---

Genie-TTS (GENIE) is a lightweight CPU-oriented inference engine built on the open-source GPT-SoVITS project, packaging TTS inference, ONNX model conversion, and a FastAPI server for GPT-SoVITS V2 and V2ProPlus checkpoints in Japanese, English, Chinese, and Korean with near-instantaneous CPU synthesis (**Reported**).[^genie-readme]

## Model identity and compatibility

- Name is `GENIE`, glossed as "GPT-SoVITS Lightweight Inference Engine" with the tagline "Experience near-instantaneous speech synthesis on your CPU"; upstream is `github.com/RVC-Boss/GPT-SoVITS`; supported model versions are GPT-SoVITS V2 and V2ProPlus; supported languages are Japanese, English, Chinese, and Korean; supported Python is `>= 3.10` (**Reported**).[^genie-readme]
- V3, V4, and later GPT-SoVITS lines are explicitly out of support in this source; the roadmap lists V3/V4 support as open (**Reported**).[^genie-readme]
- Demo evidence is a Bilibili video (`BV1d2hHzJEz9`, Chinese); the video itself was not fetched and contributes no transcribed claim to this concept (**Synthesis**).[^genie-readme]

## Performance claims

- First-inference latency: GENIE 1.13 s vs official PyTorch model 1.35 s vs official ONNX model 3.57 s; runtime size ~200 MB vs ~several GB vs similar-to-GENIE; model size ~230 MB vs similar-to-GENIE vs ~750 MB (**Reported**).[^genie-readme]
- Measurement protocol stated in source: 100 Japanese sentences of ~20 characters each, averaged, on CPU i7-13620H; no variance, precision, thread count, power plan (beyond the Administrator-mode recommendation), checkpoint variant, or text list accompanies the figures (**Reported**).[^genie-readme]
- Figures are source assertions without independent verification in this wiki and carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^genie-readme]

## Installation and resources

- Install via `pip install genie-tts`; source recommends running in Administrator mode to avoid potential performance degradation (**Reported**).[^genie-readme]
- First run requires ~391 MB of resource files, downloadable automatically via the library prompts or `genie.download_genie_data()`; manual placement is supported by downloading from `huggingface.co/High-Logic/Genie/tree/main/GenieData` and setting `GENIE_DATA_DIR` before importing `genie_tts` (**Reported**).[^genie-readme]
- Optional Chinese RoBERTa text features (`genie.download_roberta_data()`) improve Chinese prosody and are intended only for the Chinese path; the source states they should not be used for Japanese, English, or Korean inference (**Reported**).[^genie-readme]

## Usage

- Zero-model tryout uses predefined characters, e.g. Mika (Blue Archive, Japanese), ThirtySeven / 37 (Reverse: 1999, English), Feibi (Wuthering Waves, Chinese), browsable at `huggingface.co/High-Logic/Genie/tree/main/CharacterModels`; entry point is `genie.load_predefined_character('mika')` then `genie.tts(character_name, text, play)` plus `genie.wait_for_playback_done()` (**Reported**).[^genie-readme]
- Custom-voice path is `genie.load_character(character_name, onnx_model_dir, language)` with language codes `en`, `zh`, `jp`, `kr`; then `genie.set_reference_audio(character_name, audio_path, audio_text)` for emotion and intonation cloning; then `genie.tts(character_name, text, play, save_path)` (**Reported**).[^genie-readme]
- Model conversion requires `torch` (`pip install torch`) and calls `genie.convert_to_onnx(torch_pth_path, torch_ckpt_path, output_dir)`; the source states it currently supports V2 and V2ProPlus models (**Reported**).[^genie-readme]
- Serving uses `genie.start_server(host, port, workers)` with the example `host="0.0.0.0"`, `port=8000`, `workers=1`; request formats and API details are delegated to `./Tutorial/English/API Server Tutorial.py`, which was not captured in `raw/` (**Reported**).[^genie-readme]

## Roadmap and deployment status

- Completed in source: Chinese and English language expansion, V2ProPlus compatibility, out-of-the-box Windows bundles (**Reported**).[^genie-readme]
- Open in source: V3/V4 model support and official Docker images (**Reported**).[^genie-readme]

## Relationships

- Depends on [GPT-SoVITS](gpt-sovits.md): GENIE is built on the GPT-SoVITS project and converts its V2/V2ProPlus `.pth`/`.ckpt` checkpoints to ONNX for lightweight inference, while that concept covers the upstream few-shot WebUI, training/fine-tune tooling, and v1–v5 checkpoint lineage (**Synthesis**).[^genie-readme]
- CPU-lightweight comparison: [Pocket TTS](pocket-tts.md) covers a 100M-parameter CPU-first multilingual TTS stack with ~200 ms first-chunk streaming on laptop-class hardware, while this concept covers an ONNX conversion and serving engine around GPT-SoVITS checkpoints with 1.13 s first-inference latency on i7-13620H; no shared vendor or checkpoint is asserted (**Synthesis**).[^genie-readme]
- ONNX CPU-serving comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B DualAR zero-shot TTS model with ONNX INT4 CPU and SGLang Omni serving paths, while this concept covers ONNX conversion plus FastAPI serving specifically for GPT-SoVITS V2/V2ProPlus; no shared vendor or training data is asserted (**Synthesis**).[^genie-readme]

## Coverage and limits

- Source inspected statically only; no environment created, no `pip install`, resource/character-model download, conversion, inference, playback, or server launch executed, and no latency, size, quality, or prosody claim reproduced (**Synthesis**).[^genie-readme]
- Linked Bilibili demo video, GPT-SoVITS upstream repository, Hugging Face `GenieData` and `CharacterModels` trees, Chinese/English README variant, and the API Server Tutorial file were not fetched and are not in `raw/`; parameter counts, training data, vocoder details, sample rates, API request/response schemas, concurrency behavior, and Docker availability are absent from the captured source (**Synthesis**).[^genie-readme]
- All capability, compatibility, serving, and benchmark claims are source assertions without independent verification in this wiki; latency and size figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^genie-readme]

[^genie-readme]: [GENIE GPT-SoVITS Lightweight Inference Engine README](../raw/Genie-TTS.md) — locators: header (GENIE title, GPT-SoVITS upstream link, CPU tagline, V2/V2ProPlus support, ja/en/zh/kr language list, Python >= 3.10, Bilibili `BV1d2hHzJEz9` demo link); `Performance Advantages` table (1.13 s vs 1.35 s vs 3.57 s first-inference latency; ~200 MB vs ~several GB runtime; ~230 MB vs ~750 MB model size) and latency-test blockquote (100 Japanese sentences ~20 chars, averaged, i7-13620H); `QuickStart` Administrator-mode note and `pip install genie-tts`; `Pretrained Models` (~391 MB first-run resources, `GENIE_DATA_DIR` pre-import pattern, `download_genie_data()` / `download_roberta_data()`, Chinese-only RoBERTa prosody note); `Quick Tryout` (`load_predefined_character('mika')`, Mika/ThirtySeven/Feibi examples, `CharacterModels` Hugging Face link, `tts(..., play=True)` plus `wait_for_playback_done()`); `TTS Best Practices` (`load_character` with `character_name`/`onnx_model_dir`/`language` en/zh/jp/kr, `set_reference_audio` with `audio_path`/`audio_text`, `tts` with `play`/`save_path`); `Model Conversion` (`pip install torch`, `convert_to_onnx(torch_pth_path, torch_ckpt_path, output_dir)`, V2/V2ProPlus tip); `Launch FastAPI Server` (`start_server(host, port, workers)`, `0.0.0.0:8000`/`workers=1` example, `Tutorial/English/API Server Tutorial.py` pointer); `Roadmap` (done: Chinese/English, V2ProPlus, Windows bundles; open: V3/V4, Docker images).
