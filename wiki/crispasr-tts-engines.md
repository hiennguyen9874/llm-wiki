---
type: Concept
title: CrispASR TTS Engines
description: "CrispASR's text-to-speech surface: engine count and matrix (cloning, sampling, sample rate), license-gated checkpoints, built-in watermarking, the voice-cloning consent flag, and conflicting engine lists in the README."
tags: [tts, voice-cloning, watermark, licensing, ggml, gguf]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:30:00Z }
stale_after: 2027-10-13
sources:
  - id: crispasr-readme
    resource: ../raw/CrispASR.md
    kind: documentation
    title: CrispASR README
---

CrispASR drives synthesis with `--tts` and `--tts-output PATH.wav`, and with `POST /v1/audio/speech` in server mode. Its README counts 62 TTS engines in one place and 52 in another, and its engine tables do not match each other. Every TTS output is said to carry a watermark, cloning requires an explicit rights flag, and several checkpoints are non-commercial or license-gated (**Reported**).[^crispasr-readme]

## Invocation

- Quick start: `crispasr --backend kokoro -m auto --tts "..." --tts-output hello.wav`. The Kokoro model (~135 MB) downloads on first use, and the README's example output is "78000 samples @ 24000 Hz, 3.25 sec" (**Reported**).[^crispasr-readme]
- Server: `crispasr --server --backend qwen3-tts-customvoice -m auto --voice-dir ./voices --port 8080` exposes `POST /v1/audio/speech` and `/v1/voices` automatically for any loaded TTS backend (**Reported**).[^crispasr-readme]
- Output language: `-tl <lang>` (or `-l`) selects the spoken language. `cosyvoice3-tts`, `qwen3-tts`, and `moss-tts` act on it natively. For cross-lingual cloning, `-sl <lang>` names the language of the reference clip so cosyvoice3 drops the reference transcript instead of carrying its accent. Over HTTP the fields are `language` and `source_lang` (**Reported**).[^crispasr-readme]

## Engine matrix

The README's 25-row feature matrix records, per engine, cloning support, sampling mode, sample rate, auto-download, and flash attention. Sample rates given there (**Reported**).[^crispasr-readme]

- 16 kHz: speecht5. 22 kHz: piper, fastpitch, confucius4-tts (22.05). 24 kHz: most engines, including kokoro, orpheus, chatterbox, cosyvoice3-tts, csm, bark, pocket-tts, tada, and qwen3-tts. 44 kHz: dia and parler-tts. 44.1 kHz: supertonic. 48 kHz: voxcpm2-tts, irodori-tts, and dots-tts (**Reported**).[^crispasr-readme]
- Cloning is listed for vibevoice-tts, qwen3-tts (CustomVoice variant only), omnivoice, chatterbox, outetts (JSON speaker profile), indextts, voxcpm2-tts, cosyvoice3-tts, f5-tts, irodori-tts (WAV), bark (`.npz`), speecht5 (x-vector), pocket-tts, tada, dots-tts, fireredtts3 (reference WAV plus `--ref-text`), and confucius4-tts. Kokoro, orpheus, csm, dia, parler-tts, fastpitch, piper, and supertonic (fixed presets F1–F5 and M1–M5) do not clone (**Reported**).[^crispasr-readme]
- Controls: `--tts-speed` and `--tts-steps` for supertonic; VoiceDesign `--instruct` for irodori-tts; prompt description via `--instruct` for parler-tts; `[S1]`/`[S2]` dialogue tags for dia, which the README says need prompts over 100 characters (**Reported**).[^crispasr-readme]

The TTS table (30 backend rows, some covering several checkpoints) adds architecture, languages, and license. Engine-specific notes from it (**Reported**).[^crispasr-readme]

- **Breeze TTS 2** (`bt2-tts`): voice cloning plus voice design through `--tts-instruct`, with `--tts-cfg-scale 4` to strengthen it. Its weights are non-commercial and need `--accept-license other`. See [Breeze TTS 2](breeze-tts-2.md) (**Reported**).[^crispasr-readme]
- **Qwen3-TTS** (`qwen3-tts`, `qwen3-tts-customvoice`): the Base checkpoints use baked speakers via `--voice <name>`. The CustomVoice 1.7B adds nine built-in speakers and `--instruct` style control (**Reported**).[^crispasr-readme]
- **CosyVoice3** (`cosyvoice3-tts`): baked-voice cloning via `--voice <name>`, or any WAV via `--voice ref.wav --ref-text "<exact transcript>"`. `--backend cosyvoice3-tts-rl` selects the RL-tuned talker. Setting `COSYVOICE3_FLOW_STEPS=5` gives a fast mode against the quality default of 10. Batched classifier-free guidance and request-sized KV caching are the default, and the S3 tokenizer and CAMPPlus companions load only when a WAV cloning voice is first requested (**Reported**).[^crispasr-readme]
- **VibeVoice** (`vibevoice-tts`): described as the lowest-latency streaming engine. The README's example downloads about 636 MB on first run (**Reported**).[^crispasr-readme]
- **Kokoro**: described as "multilingual, smallest" and has no cloning (**Reported**).[^crispasr-readme]
- **Chatterbox**: German through the Kartoffelbox fine-tune and separate Arabic, German, and Finnish (`chatterbox-finnish-nano`) fine-tunes (**Reported**).[^crispasr-readme]

## Licensing and gating

Engine licenses from the TTS table (**Reported**).[^crispasr-readme]

- Non-commercial: `bt2-tts` (BreezeBlue non-commercial, `--accept-license other`), `voxtral-tts` (CC-BY-NC-4.0, see [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md)), and `outetts` (CC-BY-NC-SA-4.0) (**Reported**).[^crispasr-readme]
- Conditional: `pocket-tts` (CC-BY-4.0 plus gated-use conditions), `tada` and `orpheus` (Llama 3.2 Community License; orpheus is also listed as MIT) (**Reported**).[^crispasr-readme]
- Permissive: MIT (melotts, piper, chatterbox, bark, speecht5, vibevoice-tts), Apache-2.0 (kokoro, qwen3-tts, moss-tts, moss-tts-local, miotts, omnivoice, cosyvoice3-tts, csm, dia, zonos-tts, parler-tts, indextts, voxcpm2-tts, kugelaudio, bananamind-tts), CC-BY-4.0 (fastpitch), and LFM Open v1.0 (lfm2-audio) (**Reported**).[^crispasr-readme]

## Trust controls

- **Watermarking:** "All TTS output is watermarked; post-embed verification warns if confidence is low." `--detect-watermark file.wav` checks any WAV for AI watermarks (**Reported**).[^crispasr-readme]
- **Cloning consent:** the Start-here table says cloning "requires `--i-have-rights`" and points to the consent rules in `docs/eu-ai-act.md` (**Reported**).[^crispasr-readme]
- **EU AI Act scope:** the TOC describes that guide as covering synthetic-audio marking (watermark, C2PA, and a spoken disclaimer), what counts as a voice clone, the speaker-biometrics boundary, why there is no emotion recognition, and the deployer's duties. The guide was not captured (**Reported**).[^crispasr-readme]
- **Emotion recognition withheld:** the SenseVoice ASR row says upstream's emotion classifier "is not exposed" in CrispASR, citing the EU AI Act guide (**Reported**).[^crispasr-readme]

## Contradictions

- Engine count: the intro and backend section give 62 TTS engines, while the table of contents gives 52 for the same section. Neither figure is chosen (**Reported**).[^crispasr-readme]
- Engine lists: the feature matrix names six engines that have no row in the 30-row TTS table, namely f5-tts, irodori-tts, supertonic, dots-tts, fireredtts3, and confucius4-tts. Neither list is treated as complete (**Reported**).[^crispasr-readme]
- Qwen3-TTS cloning: the README's footnote says "CustomVoice variant only; Base uses baked speakers via `--voice <name>`." The wiki's [Qwen3-TTS-12Hz-0.6B-Base](qwen3-tts-12hz-0.6b-base.md) concept, drawn from the upstream model card, describes 3-second voice cloning from a reference clip. The CrispASR runtime may differ from upstream. Neither claim is chosen here (**Reported**).[^crispasr-readme]

## Relationships

- Uses: the README's engine rows correspond to these wiki checkpoint pages, and claims about each checkpoint belong on its own page: [Pocket TTS](pocket-tts.md), [Chatterbox TTS](chatterbox-tts.md), [OmniVoice](omnivoice.md), [VibeVoice-Realtime-0.5B](vibevoice-realtime-0.5b.md), [VibeVoice-1.5B](vibevoice-1.5b.md), [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md), [Breeze TTS 2](breeze-tts-2.md), [MOSS-TTS-v1.5](moss-tts-v1-5.md), [MOSS-TTS-Local-Transformer-v1.5](moss-tts-local-transformer-v1-5.md), [Qwen3-TTS-12Hz-0.6B-Base](qwen3-tts-12hz-0.6b-base.md), and [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md). Model accuracy and latency claims belong to those pages (**Synthesis**).[^crispasr-readme]
- Compared across engines in: [TTS Model Survey](tts-model-survey.md) (**Synthesis**).
- Sibling runtime: [audio.cpp Framework](audio-cpp-framework.md) also serves Pocket TTS and other engines through a separate native stack (**Synthesis**).
- Part of: [CrispASR](crispasr.md) (**Synthesis**).

## Coverage and limits

- Engine detail lives in `docs/tts.md`, which was not captured. The README's `qwen3-tts` environment switches and per-engine env vars are therefore unexamined (**Synthesis**).[^crispasr-readme]
- Latency, quality, and sample-rate claims are README assertions. No engine was run, and the watermark behavior was not tested (**Synthesis**).[^crispasr-readme]

[^crispasr-readme]: [CrispASR README](../raw/CrispASR.md) — locators: `Start here` §2 "Make it speak" and "Where to go next" table (kokoro quick start, cloning consent row); `Supported backends` intro (62 TTS) and `Text-to-Speech models` table (30 rows: engine, architecture, languages, license) and its `TTS feature matrix` `<details>` (25 rows, cloning/sampling/kHz/auto-download/flash-attn) with the `*` footnote (CustomVoice-only cloning) and the output-language paragraph; `Table of contents` TTS bullet (52 engines) and EU AI Act bullet; `Streaming, TTS, and HTTP server` (watermark paragraph, CosyVoice3 flow-step and batching notes, `/v1/audio/speech` example); `ASR backends` SenseVoice row (emotion classifier not exposed); `Credits`.
