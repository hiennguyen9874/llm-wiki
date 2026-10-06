---
type: Concept
title: Whistle
description: 16.9 MB on-device multilingual STT model with word timestamps, per-frame speech embeddings, and keyword biasing sharing the Needle CPU engine.
tags: [stt, on-device, edge, multilingual, quantization]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T16:40:00Z }
stale_after: 2027-10-06
sources:
  - id: whistle-card
    resource: ../raw/whistle.md
    kind: documentation
    title: 'Whistle: Speech Recognition for Tiny Devices'
---

Whistle is Cactus Compute's tiny on-device speech-to-text model for mobiles, wearables, robots, smart home, automotive, and microcontrollers, shipping as a single 16.9 MB `whistle.cact` file that runs on the same CPU engine, container, and quantisation as the Needle LLM with no dependencies and no GPU, covering 16 kHz mono transcription up to 30 seconds per pass in seven languages with auto language detection, decoder-attention word timestamps, per-frame speech embeddings, and keyword biasing (**Reported**).[^whistle-card]

## Model identity and release

- Title is `Whistle: Speech Recognition for Tiny Devices`, built by the Cactus Compute team and cited as Mroz, Ndubuaku, Mosoyan, Cylich, Kumar, Sandhu, Shemet, and Lee (2026), Cactus Compute, Inc., with `https://github.com/cactus-compute/needle` as the publication handle and `founders@cactuscompute.com` as the contact (**Reported**).[^whistle-card]
- Frontmatter declares `library_name: cactus-needle`, `pipeline_tag: automatic-speech-recognition`, `license: apache-2.0`, a seven-code `language` list (`en`, `de`, `fr`, `es`, `it`, `nl`, `pl`), and tags including `speech-recognition`, `speech-to-text`, `on-device`, `edge`, `quantization`, and `webassembly` (**Observed** by static inspection).[^whistle-card]

## Capabilities

- **Transcription**: 16 kHz mono audio, up to 30 seconds in one pass, in English, German, French, Spanish, Italian, Dutch, and Polish; the language is auto-detected unless forced, and silence returns an empty transcript rather than an invented sentence (**Reported**).[^whistle-card]
- **Word timestamps**: every word with its start, end, and probability, aligned from the decoder's own attention, for highlight, seek, or cut on a word (**Reported**).[^whistle-card]
- **Speech embedding**: the encoder output at one row per 80 ms frame, for matching and retrieval without decoding a transcript (**Reported**).[^whistle-card]
- **Keyword biasing**: caller-supplied names, places, and product words are favoured during the search so the terms that matter survive (**Reported**).[^whistle-card]

## Architecture and Needle engine

- Front end is log-mel plus a convolutional stem feeding an audio encoder, read by a Needle-shaped decoder through gated cross attention at every layer (**Reported**).[^whistle-card]
- Whistle reuses Needle's `.cact` container, Cactus Quants, SIMD kernels, and KV cache, so a device that already runs Needle runs Whistle in the same binary with no second runtime; this repository holds `whistle.cact` while the engine and platform folders live in `Cactus-Compute/needle3` (**Reported**).[^whistle-card]
- The decoder is laddered like Needle's: every depth from 2 layers up is a deployable model, picked at load time with `--audio-depth` (**Reported**).[^whistle-card]

## Benchmark protocol and limits

- Word error rate is scored on the full test splits with the Whisper normalizers; Whisper and Moonshine figures are the ones their authors published, and Whistle's own WER is measured over 86,174 utterances (**Reported**).[^whistle-card]
- Speed method is 10 seconds of audio on an Apple M4 Pro with each model on its official runtime at defaults: Whistle's C++ engine at 5 beams, `openai-whisper`, and non-streaming `moonshine-voice` over whole audio; time to first token runs from audio in to first token, and decode rate is tokens divided by wall time after it so the encoder is not counted twice (**Reported**).[^whistle-card]
- Precision tiers are Whistle 2 to 4 bit, Whisper fp32 in memory on CPU, and Moonshine int8; the Whisper row uses the multilingual checkpoint, not `base.en` (**Reported**).[^whistle-card]
- Comparability notes: a missing bar means that model's authors never published that benchmark; Moonshine is English only; Whisper reports no SPGISpeech, Earnings-22, or AMI cleaned; AMI includes empty references per the Open ASR Leaderboard convention while Whisper's figure is AMI-IHM; TED-LIUM excludes the corpus's `ignore_time_segment_in_scoring` regions; FLEURS and MLS are averaged over Whistle's seven languages (MLS over six, no English) with the same set for every model; no test audio appears in Whistle's training or validation data, verified by audio checksums and speaker IDs across every reported test set (**Reported**).[^whistle-card]
- Numeric-result limit: the actual WER and speed values live only in the `whistle-benchmarks.svg` figure, which is not in `raw/` and was not inspected, so no numeric benchmark is recorded here (**Synthesis**).[^whistle-card]

## Python usage

- Install with `pip install cactus-needle`; a 16 kHz WAV or raw samples need nothing beyond the base install, while other sample rates and microphone capture need the `[mic]` extra (**Reported**).[^whistle-card]
- `needle.transcribe("clip.wav")["text"]` returns the text plus the language, the milliseconds to the first token, and the decoder's tokens per second after it; `word_timestamps=True` adds each word with start, end, and probability, `keywords=[...]` favours user names, and `language="de"` forces the language instead of detecting it; engine and weights are fetched once and cached (**Reported**).[^whistle-card]
- `needle.Whistle()` exposes the same model as an object for `embed(audio)` or to hold one tuned `.cact`; `needle whistle playground` transcribes from the microphone and `needle whistle compare` runs Whistle next to Whisper and Moonshine on the same clip (**Reported**).[^whistle-card]

## With Needle

- One engine runs both models: `needle_load` reads whichever model a `.cact` carries, so the same binary transcribes on its own, answers text on its own, or does both at once — transcribing the clip, answering the transcript against caller tools, and returning one JSON object with the tool calls and the speech fields, the speech ones prefixed `audio_`; the transcription stays inside the engine so audio in and tool calls out is one call (**Reported**).[^whistle-card]
- CLI forms are `needle --model whistle.cact --audio clip.wav` for transcription alone and `needle --model needle3.cact --model whistle.cact --tools tools.json --audio clip.wav` for the joint call (**Reported**).[^whistle-card]

## Deploy

- The engine and platform folders come from `Cactus-Compute/needle3`; every folder holds a `needle` binary, `libneedle.a`, and `needle.h`, and loads any `.cact` handed to it — this model, Needle, or both (**Reported**).[^whistle-card]
- Download and run with `needle download macos-arm64`, `needle download whistle`, then `./macos-arm64/needle --model whistle.cact --audio clip.wav --audio-word-timestamps` (**Reported**).[^whistle-card]
- The whole speech C API is `needle_load`, `needle_transcribe`, and `needle_embed`, declared in `needle.h` beside Needle's own, with `needle_complete` taking the clip directly and doing the transcription; the engine reads no environment variables, so every behaviour is a compiled default or an explicit flag and every run of the same blob scores the same (**Reported**).[^whistle-card]
- The devices guide covers runner flags, the C API, the WASI component, and air-gapped setup (**Reported**).[^whistle-card]

## Relationships

- Benchmarked against [Whisper Large v3 Turbo](whisper-large-v3-turbo.md): the Whistle card's protocol pits its C++ engine at 5 beams against `openai-whisper` and non-streaming `moonshine-voice` on the same clips, using the multilingual Whisper checkpoint rather than `base.en` (**Synthesis**).[^whistle-card]

## Coverage and limits

- Source inspected statically only; no package installed, no checkpoint downloaded, no audio transcribed, and no WER, latency, or throughput claim reproduced (**Synthesis**).[^whistle-card]
- Banner, model, benchmark, loading, and deploy SVG figures plus the Needle3 engine repository, the `needle` GitHub source, and the devices guide were linked but not fetched and are not in `raw/`; only the single Markdown card was compiled (**Synthesis**).[^whistle-card]
- All identity, capability, architecture, protocol, usage, and accuracy claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^whistle-card]

[^whistle-card]: [Whistle: Speech Recognition for Tiny Devices](../raw/whistle.md) — locators: frontmatter (`library_name: cactus-needle`, `pipeline_tag: automatic-speech-recognition`, `license: apache-2.0`, 7-code `language` list, `tags`); intro (16.9 MB single file, same Needle CPU engine/container/quantisation, no dependencies/GPU, six target device classes, three on-device jobs); `Transcription` / `Word timestamps` / `Speech embedding` bullets (16 kHz mono, ≤30 s, 7 languages, auto LID, silence-to-empty; start/end/probability from decoder attention; one row per 80 ms frame); `Keyword biasing` sentence; section `Model` (log-mel front end, convolutional stem, audio encoder, Needle-shaped decoder, gated cross attention every layer, `.cact`/Cactus Quants/SIMD kernels/KV cache, laddered `--audio-depth`, `whistle.cact` vs `needle3` engine); section `Benchmarks` (full-split WER, Whisper normalizers, 86,174 utterances, M4 Pro 10 s method, 5 beams, TTFB/decode definitions, 2–4-bit vs fp32 vs int8, multilingual-checkpoint note, missing-bar rule, Moonshine English-only, SPGISpeech/Earnings-22/AMI-cleaned gaps, AMI-IHM and empty-reference convention, TED-LIUM exclusions, FLEURS/MLS 7- and 6-language averaging, checksum plus speaker-ID leak check; `whistle-benchmarks.svg` image-only); section `Get started` (`pip install cactus-needle`, `[mic]` extra, `needle.transcribe` fence with `word_timestamps`/`keywords`/`language`, return fields, `needle.Whistle()`/`embed`, `playground`/`compare`); section `With Needle` (`needle_load`, joint transcribe-plus-tools JSON with `audio_` prefix, two CLI fences); section `Deploy` (`needle download` fences, platform folders with `needle`/`libneedle.a`/`needle.h`, `--audio-word-timestamps`, `needle_load`/`needle_transcribe`/`needle_embed`/`needle_complete`, no-environment-variable determinism, devices guide); section `Citation` (BibTeX Mroz et al. 2026, Cactus Compute, GitHub URL, `founders@cactuscompute.com` contact).
