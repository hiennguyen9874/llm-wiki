---
type: Concept
title: sanoTTS
description: Sub-2.2M-parameter multilingual neural TTS family down to 294k params / 337KB INT8 with ESP32-class MCU deployment, teacher-distilled stack, and author-reported SCOREQ/UTMOS and RTF figures.
tags: [tts, edge, microcontroller, multilingual]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: sanotts-thread
    resource: ../raw/i_released_sanotts_smallest_complete_tts_stack_in.md
    kind: documentation
    title: sanoTTS release announcement r/LocalLLaMA thread capture
---

sanoTTS is an author-reported sub-2.2M-parameter multilingual neural TTS family, bottoming at 294k parameters (337KB INT8), claiming 11 voices across 6 languages with ESP32-class microcontroller deployment at 0.225 RTF, built by distilling teacher models per component, with the 1.51M Amy voice author-reported at 4.13 SCOREQ / 4.10 UTMOS and ~2% Whisper WER; all figures below are release-thread assertions without independent verification in this wiki (**Reported**).[^sanotts-thread]

## Family identity and size

- Release poster (`u/Affectionate_Hat_585` on r/LocalLLaMA; capture shows 509 votes, 121 comments, partially anonymized bylines) claims this family holds the smallest neural TTS model at ~2% WER on Whisper; parameter range is 294k–2.2M, with 11 voices and 6 languages (**Reported**).[^sanotts-thread]
- Size anchors: 337KB for the 294k model quantized to INT8; 244x smaller than Kokoro and 9000x smaller than Voxtral TTS by the author's comparison; goal was fitting a $3 chip with 512KB SRAM and no NPU (**Reported**).[^sanotts-thread]
- Upstream pointers given (not fetched): repo `https://github.com/ampixa/sanoTTS`, live demo `https://tts.ampixa.com/sanoTTS`, Hub `https://huggingface.co/ampixa/sanoTTS`, paper `https://arxiv.org/abs/2608.21378`, web package `sanotts-web` (**Reported**, with unfetched-pointer limit).[^sanotts-thread]

## Author-reported quality figures

- The 1.5M model is reported at SCOREQ 4.13 and UTMOS 4.10; sanoTTS-Amy (1.51M) at 4.13 SCOREQ is claimed better than Inflect Nano (4.63M) at 3.81 and KittenTTS (15M) at 3.02 (**Reported**).[^sanotts-thread]
- Intelligibility is claimed at around 2% WER on Whisper; a comment exchange adds wav2vec2 also gave good results, and one commenter asks whether Whisper remains the best WER checker for multilingual evaluation (unanswered) (**Reported**).[^sanotts-thread]
- Quality caveats from the author: smaller sizes stay intelligible to ASR but lose naturalness with headroom remaining; fewer parameters sound more "whispery" (commenter impression); non-English voices got less tuning and Chinese sounds robotic; a custom sibilant/metallic artifact detector exists for English only (**Reported**).[^sanotts-thread]

## Architecture and distillation recipe

- The stack has four parts: text frontend (text→phoneme), acoustic model (→spectrogram), duration predictor (per-phoneme timing), and decoder/vocoder (spectrogram→waveform) (**Reported**).[^sanotts-thread]
- Training distills a teacher (Piper-plus and Kokoro tested): generate a 50,000-item "fivesome" of text, audio, acoustic latent, duration, and mel spectrogram, then train each component individually; the repo README is cited as the starting point (**Reported**).[^sanotts-thread]
- Extension recipe: new languages/voices need a teacher plus a text frontend, then follow the recipe; eSpeak is named as making Italian/German frontends doable; a closed-model teacher path is described as extra work via mel-100 targets, acoustic modelling, and MFA-style duration handling (**Reported**).[^sanotts-thread]
- Voice cloning posture: a recipe clones teacher-model voices, but zero-shot cloning is explicitly unsupported (two author answers); one community agent-workflow pattern is large-model zero-shot first, then a "smol" sanoTTS version (**Reported**).[^sanotts-thread]

## MCU and host efficiency (author-reported)

- ESP32-class figure: RTF 0.225, glossed as 4s of audio generated in 1s; the smallest 294k model needs 98,224 bytes of working memory; compute need is ~45M multiply-accumulates per second, feasible on a 240MHz chip versus billions of MACs on desktop CPUs (**Reported**).[^sanotts-thread]
- Memory behavior: max RSS 1.8MB on the author's computer without optimization; ESP32-S3 (512KB RAM) shows small initial latency then faster-than-real-time output within the RAM constraint; ESP32-P4/Teensy-class chips called "a piece of cake"; rule of thumb is anything above ~500KB RAM with ~337KB weight storage works (**Reported**).[^sanotts-thread]
- Flash/PSRAM: ESP32 XIP executes from flash and is used here; weights also tested from PSRAM with a slight penalty; chips doing 29+ MMAC run it comfortably (**Reported**).[^sanotts-thread]

## Deployment paths

- Web: runs in the browser via WebAssembly as `npm install sanotts-web` (**Reported**).[^sanotts-thread]
- Python: `pip install sanotts` then `sanotts.synthesize("Hello from a tiny neural voice.", voice="heart-nano")` with `soundfile` write-out; JS self-host deploy link and a bare C library / C99 target are offered, with author help offered for an iPhone loading problem (no resolution in-thread) (**Reported**).[^sanotts-thread]
- audio.cpp: the thread reports a community PR adding sanoTTS, merged and CPU-tested, with a 7-row voice/graph/lang/duration/RTF table (all ASR "OK"): `nano` graph voices (heart-nano, heart) at RTF 0.0027–0.0044 and `piperlite` graph voices (amy, hfc, kristin, vi, id) at RTF 0.0321–0.0390 (**Reported**).[^sanotts-thread]
- Benchmark adoption: the model was requested for and added to the community `tts-bench` project (**Reported**).[^sanotts-thread]

## Language backlog and forks

- Requested backlog so far: German, Spanish, Italian, Urdu (plus Punjabi/Persian asks); Hindi already has a voice; French promised soon; Vietnamese (`vi`) and Indonesian (`id`) test rows imply coverage beyond English (**Reported**).[^sanotts-thread]
- A community Japanese fork is linked (`ayutaz/sanoTTS-jp`) (**Reported**).[^sanotts-thread]
- Streaming behavior: asked whether audio can start before full generation (Home Assistant use), the author describes small ESP32-S3 start latency then faster-than-real-time synthesis outpacing audio output under the RAM constraint, rather than a confirmed chunk-streaming API (**Reported**).[^sanotts-thread]

## Fit and non-fit (synthesis of thread)

- Good for ESP32/IoT speech output, offline gadgets and robots, game-engine C++ voice lines without GPU, on-demand phone audiobooks, and sub-5M TTS research baselines (**Synthesis**).[^sanotts-thread]
- Not good for zero-shot cloning, production narration parity with large models, non-English quality parity without extra diagnostic work, or guaranteed artifact-free output on sibilants (/z/ neighbours, 1–6kHz metallic band per the author's own diagnosis) (**Synthesis**).[^sanotts-thread]

## Limitations and open reports

- A period-pause bug ("10-second delay after every period", any sentence) is unresolved: the author asked for a replicating sentence and got "any sentence", with no fix in-thread (**Reported**).[^sanotts-thread]
- A "fifteen vs fifty" spoken-instruction confusion worry over a tiny speaker went unanswered (**Reported**).[^sanotts-thread]
- Diagnosis method detail: mostly aggregate SCOREQ, then worst-decoder-vs-teacher band analysis found the 1–6kHz /z/-neighbour metallic artifacts and retrained a model on those bands (**Reported**).[^sanotts-thread]

## Relationships

- Compared against [Inflect-Nano-v1](inflect-nano-v1.md): the thread's headline comparator, author-reporting sanoTTS-Amy (1.51M, SCOREQ 4.13) above Inflect Nano (4.63M, 3.81); Inflect-Nano-v1 is the English-only single-speaker 24 kHz sub-5M baseline while sanoTTS claims multilingual multi-voice below 2.2M with MCU deployment (**Synthesis**).[^sanotts-thread]
- Integrated with [audio.cpp Framework](audio-cpp-framework.md): thread reports a merged audio.cpp PR with CPU-tested RTF table, matching that runtime's native local-model path; no shared-vendor claim (**Synthesis**).[^sanotts-thread]
- Edge-TTS neighbours for sub-100M selection: [Soprano-1.1-80M](soprano-1-1-80m.md), [Supertonic 2](supertonic-2.md), [Pocket TTS](pocket-tts.md), and [MOSS-TTS-Nano](moss-tts-nano.md) — sanoTTS is one to two orders of magnitude smaller, MCU-targeted, and non-zero-shot-cloning, unlike several cloning-capable neighbours (**Synthesis**).[^sanotts-thread]

## Coverage and limits

- Statically inspected the Reddit capture only; no code executed, no audio synthesized, and no parameter, SCOREQ/UTMOS/WER, RTF, RSS, or MAC figure reproduced — all performance and quality claims are author or commenter assertions (**Synthesis**).[^sanotts-thread]
- Upstream repo, paper, Hub weights, demo site, WASM package, tts-bench entries, and the Japanese fork were linked but not fetched; Python/JS/C snippets were not run; vote/comment counts record capture-time attention, not quality (**Synthesis**).[^sanotts-thread]
- Capture bylines are partly anonymized (`unknown`) and the audio.cpp discussion mixes poster and commenter voices, so maintainer identity is not attributed here; jokes, solicitations, and voice-request chatter were excluded as non-durable (**Synthesis**).[^sanotts-thread]
- Figures carry `stale_after: 2027-10-06` per `tts` domain rules for model releases and benchmarks; a future ingest of the repo/paper/Hub package should reconcile architecture, language list, license, and numbers and may promote this draft to `stable` (**Synthesis**).[^sanotts-thread]

[^sanotts-thread]: [sanoTTS release thread](../raw/i_released_sanotts_smallest_complete_tts_stack_in.md) — locators: header (r/LocalLLaMA, u/Affectionate_Hat_585, 509 votes, 121 comments); post bullets + paragraphs (11 voices/6 languages, 294k–2.2m, 244x Kokoro / 9000x Voxtral, 4.13 SCOREQ / 4.10 UTMOS, 337KB INT8, WASM `sanotts-web`, extension recipe, ~2% Whisper WER, repo/demo/HF links, Amy 4.13 vs Inflect 3.81 vs KittenTTS 3.02, ESP32 RTF 0.225 = 4s-per-1s); audio.cpp PR + merged/CPU-tested update + 7-row RTF table (nano 0.0027–0.0044, piperlite 0.0321–0.0390, ASR OK); Home Assistant/German + ESP32-S3 latency/RAM answers; Spanish/Persian/Japanese/German/Urdu/Punjabi/Hindi/French language answers + `ayutaz/sanoTTS-jp`; four-part pipeline + 50k fivesome + per-component training + closed-teacher mel-100/MFA answers; RSS 98,224 bytes / 1.8MB max RSS / 45M MAC / 240MHz / XIP / PSRAM / 29+ MMAC answers; `pip install sanotts` + `synthesize(..., voice="heart-nano")` snippets + C99/iPhone answers; repo + `arxiv.org/abs/2608.21378` answers; /z/ + 1–6kHz band diagnosis + sibilant/metallic detector + Chinese/whispery quality answers; teacher-clone recipe vs no zero-shot answers; Persian closed-model exchange; period-delay bug + fifteen/fifty threads; Whisper/wav2vec WER exchange; tts-bench add thread.
