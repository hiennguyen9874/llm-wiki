---
type: Concept
title: Inflect-Nano-v1
description: 4.63M-parameter English-only single-speaker local TTS stack with FastSpeech-style acoustic model and Snake HiFi-GAN vocoder at 24 kHz, for sub-5M baseline and embedded experiments.
tags: [tts, edge, experimental]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: inflect-nano-v1-card
    resource: ../raw/Inflect-Nano-v1.md
    kind: documentation
    title: Inflect-Nano-v1 model card
---

Inflect-Nano-v1 is a tiny experimental English text-to-speech stack with 4.632M total inference parameters including its vocoder, producing 24 kHz audio from a single English male voice via a compact FastSpeech-style acoustic model plus a small Snake-activation HiFi-GAN-style vocoder, intended as a local sub-5M baseline for tiny-model, offline-assistant, and efficient-inference experiments rather than production narration (**Reported**).[^inflect-nano-v1-card]

## Model identity and size

- Title is `Inflect-Nano-v1`; upstream is `owensong/Inflect-Nano-v1` on Hugging Face; frontmatter declares `license: apache-2.0`, `language: en`, `pipeline_tag: text-to-speech`, `library_name: pytorch`, and tags including `text-to-speech`, `tts`, `ultra-small`, `local-tts`, and `efficient-inference` (**Reported**).[^inflect-nano-v1-card]
- Total inference stack is 4.632M parameters: acoustic model 3.465M, vocoder generator 1.167M; headline rounds this to 4.63M and the differentiator claim keeps the full text-to-waveform path under 5M (**Reported**).[^inflect-nano-v1-card]
- Fixed voice scope is single English male voice at 24 kHz; the card positions the model as testing how far ultra-lightweight synthesis can go, not as competing with large TTS models (**Reported**).[^inflect-nano-v1-card]

## Pipeline and architecture

- Pipeline is `text -> English text frontend -> compact FastSpeech-style acoustic model -> 80-bin mel spectrogram -> small Snake HiFi-GAN-style vocoder -> 24 kHz waveform` (**Reported**).[^inflect-nano-v1-card]
- The acoustic model is a compact non-autoregressive FastSpeech-style network predicting duration, pitch, energy, and brightness, then decoding an 80-bin mel spectrogram (**Reported**).[^inflect-nano-v1-card]
- The vocoder is a small Snake-activation HiFi-GAN-style generator trained for 24 kHz waveform reconstruction, and including it in the published stack (rather than depending on a separate larger vocoder) is the card's stated differentiator (**Reported**).[^inflect-nano-v1-card]
- Main settings: sample rate 24 kHz, 80 mel bins, acoustic hidden size 168, 5 encoder layers, 6 decoder layers, vocoder upsample rates 8, 8, 2, 2 (**Reported**).[^inflect-nano-v1-card]

## Repository layout and dependencies

- Layout: `weights/` model weights, `examples/` audio examples, `assets/` README banner, `inflect_nano/` runtime model code, `third_party/tiny_tts_frontend/` vendored text frontend for English G2P/token IDs, `inference.py` CLI inference, `app.py` local Gradio demo (**Reported**).[^inflect-nano-v1-card]
- Weight files are `weights/inflect_nano_v1_acoustic.pt` and `weights/inflect_nano_v1_vocoder.pt`; the vendored frontend exists only to reproduce the same text normalization and tokenization path (**Reported**).[^inflect-nano-v1-card]
- License is Apache-2.0, with the vendored English frontend covered by its own license at `third_party/tiny_tts_frontend/LICENSE` (**Reported**).[^inflect-nano-v1-card]

## Inference usage

- Install via `git clone https://huggingface.co/owensong/Inflect-Nano-v1` followed by `pip install -r requirements.txt` (**Reported**).[^inflect-nano-v1-card]
- Basic synthesis: `python inference.py --text "<text>" --out sample.wav`; CPU path adds `--device cpu`; prosody controls add `--length-scale`, `--pitch-scale`, and `--energy-scale` (example values 1.03, 1.00, 1.00); local Gradio demo runs via `python app.py` (**Reported**).[^inflect-nano-v1-card]
- The card ships 8 text/audio demo pairs (dialogue prosody, parking-meter sentence, multisyllabic clarity, number disambiguation, inference-path narrative, time/currency/year formatting, uneasy-prosody pause, aluminum/entrepreneur stress) as remote-hosted `<audio>` examples; audio content was not auditioned in this wiki (**Reported**).[^inflect-nano-v1-card]

## Fit and non-fit

- Good for tiny local TTS experiments, offline assistant prototypes, efficient inference research, embedded speech demos, browser/WASM-style exploration, and a sub-5M TTS baseline (**Reported**).[^inflect-nano-v1-card]
- Not good for production narration, accessibility-critical output, voice cloning, multilingual speech, high-fidelity audiobook generation, or matching large modern TTS systems (**Reported**).[^inflect-nano-v1-card]

## Limitations

- Very small experimental model: can sound robotic, buzzy, or unstable, especially on difficult unseen text; long prompts and unusual phrasing are less reliable; the vocoder is a clear quality bottleneck; use as a research/demo release, not a production TTS engine (**Reported**).[^inflect-nano-v1-card]

## Relationships

- Uses a bundled-vocoder single-speaker design, unlike the larger multilingual zero-shot cloning models [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md), [CosyVoice2-0.5B](cosyvoice2-0.5b.md), [Fun-CosyVoice3-0.5B-2512](fun-cosyvoice3-0.5b-2512.md), and [Breeze TTS 2](breeze-tts-2.md): Inflect-Nano-v1 is roughly two orders of magnitude smaller, English-only, single-voice, and non-cloning, so it fits sub-5M baseline and embedded-demo selection while those fit multilingual or voice-design selection (**Synthesis**).[^inflect-nano-v1-card]

## Coverage and limits

- Source inspected statically only; no code executed, no audio synthesized, and no parameter-count, quality, latency, or resource-footprint figures reproduced (**Synthesis**).[^inflect-nano-v1-card]
- Weights, example WAV files, banner asset, runtime code, vendored frontend, `inference.py`, `app.py`, `requirements.txt`, and third-party license file were described but not present in `raw/` and were not inspected; upstream Hugging Face repo was linked but not fetched (**Synthesis**).[^inflect-nano-v1-card]
- All architecture, size, voice-scope, usage, fit, and limitation claims are source assertions without independent verification in this wiki (**Synthesis**).[^inflect-nano-v1-card]

[^inflect-nano-v1-card]: [Inflect-Nano-v1 model card](../raw/Inflect-Nano-v1.md) — locators: frontmatter (`license`, `language`, `pipeline_tag`, `library_name`, `tags`); intro paragraph (4.63M, vocoder included, tiny local complete text-to-waveform claim); `Highlights` section (4.63M, vocoder, 24 kHz, single male voice, PyTorch, use cases); `Listen` table (8 text prompts with remote `<audio>` sources); `Install` fenced block (`git clone`, `pip install -r requirements.txt`); `Generate Speech` fenced blocks (basic, `--device cpu`, `--length-scale/--pitch-scale/--energy-scale`, `app.py`); `Model Size` table (3.465M acoustic, 1.167M vocoder generator, 4.632M total) plus `weights/` code fence; `Repo Layout` fence and paragraphs (vendored frontend purpose); `What Makes It Different` section (separate-vocoder contrast, pipeline fence); `Architecture` section (FastSpeech-style predictor list, Snake HiFi-GAN vocoder sentence, 6-row settings table); `Good For` / `Not Good For` lists (6 items each); `Limitations` paragraph (robotic/buzzy/unstable, long prompts, vocoder bottleneck, research/demo); `License` section (Apache-2.0, third-party frontend license path).
