---
type: Concept
title: sanoTTS
description: Sub-2.2M-parameter multilingual neural TTS family down to 294k params / 337KB INT8 with ESP32-class MCU deployment, teacher-distilled stack, and author-reported SCOREQ/UTMOS and RTF figures.
tags: [tts, edge, microcontroller, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:47:01Z }
stale_after: 2027-10-07
sources:
  - id: sanotts-thread
    resource: ../raw/i_released_sanotts_smallest_complete_tts_stack_in.md
    kind: documentation
    title: sanoTTS release announcement r/LocalLLaMA thread capture
  - id: sanotts-hf-card
    resource: ../raw/sanoTTS.md
    kind: documentation
    title: sanoTTS Hugging Face model card
---

sanoTTS is Ampixa's GPL-3.0 tiny neural TTS family spanning 294,279–2,272,145 parameters (337 KB INT8 to 8.7 MB per voice) across 11 voices in 6 languages, built from two distilled lineages — piperlite (Piper/VITS-distilled, 22.05 kHz time-domain decoder) and nano (Kokoro-distilled mel-100 → ConvNeXt1D → iSTFT, 24 kHz, INT8 on a $3 ESP32-S3) — shipping numpy-only Python, WebAssembly browser, and C/Arduino runtimes with on-chip phonemization, whose headline Amy voice (1.46M) is author-reported at SCOREQ 4.13 / UTMOS 4.10 / DNS-SIG 3.61, the best naturalness to 15M params in its own 24-sentence no-reference scorecard; every performance and quality figure below is an author assertion without independent verification in this wiki (**Reported**).[^sanotts-hf-card][^sanotts-thread]

## Family identity and size

- Exact parameter range is 294,279–2,272,145; per-voice footprint is 337 KB to 8.7 MB with zero dependencies (espeak-ng phonemizer included); coverage is 11 voices across 6 languages — English, Nepali, Hindi, Vietnamese, Indonesian, Chinese — with a live in-browser demo and no cloud or NPU required (**Reported**).[^sanotts-hf-card]
- The release thread (poster `u/Affectionate_Hat_585` on r/LocalLLaMA; capture shows 509 votes, 121 comments, partially anonymized bylines) rounds the range to 294k–2.2M, claims the smallest neural TTS model at ~2% WER on Whisper, and compares 244x smaller than Kokoro and 9000x smaller than Voxtral TTS, targeting a $3 chip with 512 KB SRAM (**Reported**).[^sanotts-thread]
- Frontmatter of the card declares `license: gpl-3.0`, `language: [en, ne, hi, vi, id, zh]`, `pipeline_tag: text-to-speech`, and `library_name: sanotts` (**Observed**).[^sanotts-hf-card]
- Upstream pointers given (none fetched): repo `https://github.com/Ampixa/sanoTTS`, live demo `https://tts.ampixa.com/sanoTTS`, Hub `https://huggingface.co/ampixa/sanoTTS`, paper `https://arxiv.org/abs/2608.21378`, npm `sanotts-web`, PyPI `sanotts` (**Reported**, with unfetched-pointer limit).[^sanotts-hf-card][^sanotts-thread]

## Voice roster (card Samples table)

The card's Samples table lists one row per voice with parameter count, SCOREQ where scored, and package status; SCOREQ is a no-reference naturalness predictor (higher better) reported only for the English voices, which share one 24-sentence eval set, while the other languages have not been scored against a comparable reference (**Reported**).[^sanotts-hf-card]

| Voice | Language | Params | SCOREQ | Package status |
| --- | --- | ---: | :---: | --- |
| heart | English | 2.27 M | 3.48 | packaged (`heart/`) |
| hfc | English | 1.83 M | 3.94 | packaged (`hfc-en-1p8m/`) |
| amy | English | 1.46 M | **4.13** | packaged (`amy-en-1p46m/`) |
| kristin | English | 1.40 M | 4.09 | packaged (`kristin-en-1p4m/`) |
| amy-small | English | 1.08 M | 3.70 | packaged (`amy-en-1p1m/`) |
| robot (on-device, int8) | English | 567 k | — | not packaged (int8 MCU format); the 567,008-param model that runs on the ESP32-S3 |
| heart-nano | English | 294 k | 2.29 | packaged (`heartnano/`) |
| Indonesian | Bahasa | 1.46 M | — | packaged (`id-newstts-1p46m/`) |
| Vietnamese | Tiếng Việt | 1.46 M | — | packaged (`vi-vais1000-1p46m/`) |
| Nepali | नेपाली | 1.47 M | — | not exported yet; browser `web/voices/nepali/` only |
| Hindi | हिन्दी | 1.50 M | — | not exported yet; browser `web/voices/hindi/` only |
| Chinese | 中文 | 1.50 M | — | not exported yet; browser `web/voices/chinese/` only |

- The table carries 12 rows for 11 claimed voices because the robot row is the on-device INT8 render rather than a separate packaged voice (**Synthesis**).[^sanotts-hf-card]
- Size does not order quality: `amy` at 1.46M outscores `heart` at 2.27M because they come from different teachers and architectures, not because one is bigger (**Reported**).[^sanotts-hf-card]
- The `heart` and `heart-nano` scores were re-measured on 2026-09-04; eval set, checkpoint hashes, exact commands, and all 24 per-clip scores are claimed to be in `evidence/heart-diverse24-remeasure-20260904.json`, scored on the float32 reference render; shipped `heart-nano` INT8 tracks that render at 0.981 waveform correlation, while `heart` ships as float32 because its INT8 export reached only 0.951 against a 0.98 gate (**Reported**, evidence file not in `raw/`).[^sanotts-hf-card]

## Two lineages, two graphs

- **piperlite** (`amy`, `kristin`, `hfc`, `amy-small`, plus Indonesian, Vietnamese, and the other non-English voices): distilled from a Piper/VITS teacher at 22.05 kHz with a compact time-domain decoder running in fp32; the `sanotts` package picks this runtime automatically (**Reported**).[^sanotts-hf-card]
- **nano** (`heart`, `heart-nano`) plus the 567,008-parameter on-device model: mel-100 → ConvNeXt1D → iSTFT at 24 kHz, distilled from a Kokoro teacher through a frozen Vocos; this is the lineage that quantizes to INT8 and runs on a microcontroller (**Reported**).[^sanotts-hf-card]
- The two lineages are not interchangeable; the card states the package selects the right runtime per voice (**Reported**).[^sanotts-hf-card]
- The thread's four-part training recipe is consistent with this: text frontend (text→phoneme), acoustic model (→spectrogram), duration predictor (per-phoneme timing), decoder/vocoder (spectrogram→waveform), trained per component from a 50,000-item teacher-generated "fivesome" (text, audio, acoustic latent, duration, mel spectrogram) using Piper-plus or Kokoro teachers, with the repo README as starting point (**Reported**).[^sanotts-thread]

## Benchmark scorecard (card's "honest gate")

The card scores a diverse 24-sentence set with one no-reference suite — SCOREQ/UTMOS for naturalness, DNSMOS-SIG for signal quality, higher better — with inference-time parameter counts excluding the shared external G2P (**Reported**).[^sanotts-hf-card]

| System | Params | SCOREQ | UTMOS | DNS-SIG |
| --- | ---: | :---: | :---: | :---: |
| **sanoTTS (amy)** | **1.46 M** | **4.13** | **4.10** | 3.61 |
| TinyTTS | 1.62 M | 3.94 | 3.65 | **3.62** |
| Inflect Nano | 4.63 M | 3.81 | 3.65 | 3.58 |
| Kitten TTS nano | 15 M | 3.02 | 3.58 | 3.43 |
| _Piper (teacher)_ | _~15 M_ | _4.71_ | _4.47_ | _3.65_ |
| _Kokoro_ | _82 M_ | _4.89_ | _4.52_ | _3.69_ |

- The card claims sanoTTS is the smallest model here and the best on naturalness among everything up to 15M params, beating TinyTTS while smaller; on DNSMOS-SIG TinyTTS edges it by 0.01, and the frontier pulls ahead only at the ~15M Piper teacher and 82M Kokoro (56× larger), a gap the card does not claim to close (**Reported**).[^sanotts-hf-card]
- Shipped-file sizes quoted: sanoTTS amy 2.8 MB fp16 and TinyTTS 3.5 MB fp16 verified from released files; Kokoro ~330 MB fp32 as a widely cited public figure (**Reported**).[^sanotts-hf-card]
- Reproduction path named (not executed): `tools/eval_mos_all.py` + `tools/eval_scorecard.py` in the GitHub repo (**Reported**).[^sanotts-hf-card]

## Signal path and architecture

- Text → espeak-ng phoneme IDs → duration model (timing) → acoustic model (generator latents) → decoder → audio; the `sanotts` package selects the piperlite or nano runtime per voice (**Reported**).[^sanotts-hf-card]
- piperlite voices use the compact time-domain decoder in fp32 at 22.05 kHz; nano and the on-device model use the iSTFT decoder at 24 kHz, quantized to INT8 where it must fit and run in real time on the ESP32-S3 (**Reported**).[^sanotts-hf-card]
- Full distillation recipe lives in `docs/distillation-recipe.md` in the GitHub repo (not fetched) (**Reported**).[^sanotts-hf-card]

## Install and deployment paths

| Platform | Install | Then |
| --- | --- | --- |
| Python | `pip install sanotts` (`sanotts` >= 0.3.0) | `sanotts say "Hello" --voice heart -o hello.wav` |
| Web (npm) | `npm install sanotts-web` (`sanotts-web` >= 0.3.0) | `const tts = await SanoTTS.load(); await tts.synthesize('Hello', {voice:'heart'})` |
| Web (no build) | copy `dist/` + `voices/` | self-host deploy per GitHub README |
| Arduino / PlatformIO | zip-install or `lib_deps = https://github.com/Ampixa/sanoTTS.git` | `arduino/README.md` |
| Hugging Face | this repo's voice packages | downloaded automatically by `pip install sanotts` |
| Browser | nothing | `https://tts.ampixa.com/sanoTTS` |

- Pip voices: `heart`, `hfc`, `amy-1p8m`, `amy`, `kristin`, `vi`, `id`, `amy-1p1m`, `heart-nano`; pure numpy inference, no torch, no onnxruntime (**Reported**).[^sanotts-hf-card]
- Both packages stream weights from the HF repo by default and fall back to GitHub releases or the Pages host if Hugging Face is unreachable; Python packages land in `~/.cache/sanotts/`; `SANOTTS_VOICE_SOURCE=hf` or `=github` pins one host; in the browser, passing `voiceBase` yourself turns the fallback off so a self-hosted deployment never quietly reaches back to project servers (**Reported**).[^sanotts-hf-card]
- ESP32-S3 talking device is a standalone WiFi dashboard: type text, the board phonemizes with on-chip espeak-ng and speaks via `mcu/ports/esp32s3/`; board-by-board measurements are in `BOARDS.md`, whose silicon figures cover the `en_us_e12nano` lineage — a sibling of `heart-nano`, not the same weights (**Reported**, both paths unfetched).[^sanotts-hf-card]
- The thread's MCU figures: RTF 0.225 on ESP32 (4 s of audio per 1 s); smallest 294k model needs 98,224 bytes working memory and ~45M MAC/s, feasible on a 240 MHz chip; max RSS 1.8 MB on the author's computer unoptimized; ESP32 XIP executes from flash, weights also tested from PSRAM with a slight penalty; chips doing 29+ MMAC run it comfortably (**Reported**).[^sanotts-thread]
- The thread reports a merged audio.cpp community PR (CPU-tested) with a 7-row voice/graph/lang/duration/RTF table, all ASR "OK": `nano` graph voices (heart-nano, heart) at RTF 0.0027–0.0044 and `piperlite` graph voices (amy, hfc, kristin, vi, id) at RTF 0.0321–0.0390 (**Reported**).[^sanotts-thread]
- Other-MCU porting guidance lives in `docs/mcu-classes-and-porting.md` (not fetched) (**Reported**).[^sanotts-hf-card]

## Package file layouts

Two package layouts exist because there are two graphs (**Reported**).[^sanotts-hf-card]

- **piperlite** (`amy-en-1p46m/`, `kristin-en-1p4m/`, `hfc-en-1p8m/`, `amy-en-1p1m/`, `id-newstts-1p46m/`, `vi-vais1000-1p46m/`): flat fp16 blob addressed by manifest offsets — `manifest.json`, `weights.fp16.bin`, `piper-phoneme-config.json` (plus sibilant-injection calibration where applicable) (**Reported**).[^sanotts-hf-card]
- **nano** (`heart/`, `heartnano/`): mel-100 stack of two blobs plus generated offset header — `meta.json` (lineage, per-file sha256, sample rate, vocab), `front_*.bin` (duration + acoustic), `model_*.bin` (decoder), `nano_q8_meta.h` (tensor offsets); `heartnano/` ships `*_q8.bin` (INT8, 345,232 bytes total), `heart/` ships `*_f32.bin` (float32, 9,137,920 bytes) for the gate reason above; both layouts are consumed by the `sanotts` Python package and the portable C runtime (**Reported**).[^sanotts-hf-card]
- **`web/voices/`** is a third, browser-only artifact set: piperlite voices ship there as `front_f32.bin` + `dec_f32.bin`, a different artifact from the Python package's `weights.fp16.bin`, so the same voice appears twice under two names; it mirrors `web/` in the GitHub repo byte for byte and is what `sanotts-web` fetches, while the nano voices are not duplicated (`web/voices/heart/` and `heart/` hold the same blobs) (**Reported**).[^sanotts-hf-card]
- `samples/` holds the per-voice MP3 clips and `evidence/` the eval report behind the heart scores (neither in `raw/`, not auditioned) (**Reported**).[^sanotts-hf-card]

## License

- GPLv3 (card frontmatter `gpl-3.0`); the pipeline builds on GPLv3 components, notably espeak-ng for G2P and piper (piper1-gpl), so the project as a whole is GPLv3; copyright (C) 2026 Ampixa (**Reported**).[^sanotts-hf-card]

## Extension, cloning posture, and language backlog (thread)

- New languages/voices need a teacher plus a text frontend, then the recipe; eSpeak makes Italian/German frontends doable; a closed-model teacher path costs extra work via mel-100 targets, acoustic modelling, and MFA-style duration handling (**Reported**).[^sanotts-thread]
- Voice cloning posture: a recipe clones teacher-model voices, but zero-shot cloning is explicitly unsupported (two author answers); one community agent-workflow pattern is large-model zero-shot first, then a "smol" sanoTTS version (**Reported**).[^sanotts-thread]
- Requested backlog: German, Spanish, Italian, Urdu (plus Punjabi/Persian asks); Hindi already has a voice; French promised soon; a community Japanese fork is linked (`ayutaz/sanoTTS-jp`); Vietnamese (`vi`) and Indonesian (`id`) audio.cpp test rows imply coverage beyond English (**Reported**).[^sanotts-thread]
- Streaming behavior: asked whether audio can start before full generation (Home Assistant use), the author describes small ESP32-S3 start latency then faster-than-real-time synthesis outpacing audio output under the RAM constraint, rather than a confirmed chunk-streaming API (**Reported**).[^sanotts-thread]

## Fit and non-fit (synthesis of both sources)

- Good for ESP32/IoT speech output, offline gadgets and robots, game-engine C++ voice lines without GPU, on-demand phone audiobooks, and sub-5M TTS research baselines (**Synthesis**).[^sanotts-thread][^sanotts-hf-card]
- Not good for zero-shot cloning, production narration parity with large models, non-English quality parity without extra diagnostic work (non-English voices got less tuning and were unscored; Chinese sounds robotic per thread discussion), or guaranteed artifact-free output on sibilants (/z/ neighbours, 1–6 kHz metallic band per the author's own diagnosis) (**Synthesis**).[^sanotts-thread][^sanotts-hf-card]

## Limitations and open reports

- A period-pause bug ("10-second delay after every period", any sentence) is unresolved: the author asked for a replicating sentence and got "any sentence", with no fix in-thread (**Reported**).[^sanotts-thread]
- A "fifteen vs fifty" spoken-instruction confusion worry over a tiny speaker went unanswered (**Reported**).[^sanotts-thread]
- Diagnosis method detail: mostly aggregate SCOREQ, then worst-decoder-vs-teacher band analysis found the 1–6 kHz /z/-neighbour metallic artifacts and retrained a model on those bands; a custom sibilant/metallic artifact detector exists for English only (**Reported**).[^sanotts-thread]
- Intelligibility is claimed around 2% WER on Whisper; a comment exchange adds wav2vec2 also gave good results, with an unanswered question on whether Whisper remains the best multilingual WER checker (**Reported**).[^sanotts-thread]
- The model was requested for and added to the community `tts-bench` project; a bare C99 target exists with author help offered for an iPhone loading problem (no resolution in-thread) (**Reported**).[^sanotts-thread]

## Relationships

- Compared against [Inflect-Nano-v1](inflect-nano-v1.md): the card's own scorecard prints sanoTTS-Amy (1.46M, SCOREQ 4.13) above Inflect Nano (4.63M, 3.81), corroborating the thread's headline comparator; Inflect-Nano-v1 is the English-only single-speaker 24 kHz sub-5M baseline while sanoTTS claims multilingual multi-voice below 2.3M with MCU deployment (**Synthesis**).[^sanotts-hf-card][^sanotts-thread]
- Integrated with [audio.cpp Framework](audio-cpp-framework.md): thread reports a merged audio.cpp PR with CPU-tested RTF table, matching that runtime's native local-model path; no shared-vendor claim (**Synthesis**).[^sanotts-thread]
- Compared by [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) as an ultra-small Vietnamese edge candidate: the 1.46M piperlite voice is unscored, non-zero-shot and GPLv3; English nano MCU figures do not establish Vietnamese realtime performance (**Synthesis**).[^sanotts-hf-card][^sanotts-thread]
- Edge-TTS neighbours for sub-100M selection: [Soprano-1.1-80M](soprano-1-1-80m.md), [Supertonic 2](supertonic-2.md), [Pocket TTS](pocket-tts.md), and [MOSS-TTS-Nano](moss-tts-nano.md) — sanoTTS is one to two orders of magnitude smaller, MCU-targeted, and non-zero-shot-cloning, unlike several cloning-capable neighbours (**Synthesis**).[^sanotts-thread][^sanotts-hf-card]

## Coverage and limits

- Statically inspected the Hugging Face card capture and the earlier Reddit capture only; no code executed, no package installed, no audio synthesized, and no parameter, SCOREQ/UTMOS/DNS-SIG/WER, RTF, RSS, or MAC figure reproduced — all performance and quality claims are author assertions (**Synthesis**).[^sanotts-hf-card][^sanotts-thread]
- Upstream repo, paper, Hub weight packages, `evidence/heart-diverse24-remeasure-20260904.json`, `samples/` audio, `BOARDS.md`, `docs/distillation-recipe.md`, `docs/mcu-classes-and-porting.md`, `mcu/ports/esp32s3/`, `arduino/README.md`, demo site, WASM/npm/PyPI packages, tts-bench entries, and the Japanese fork were linked but not fetched; Python/JS/C snippets were not run; hero and signal-path diagrams were read as alt-text only; vote/comment counts record capture-time attention, not quality (**Synthesis**).[^sanotts-hf-card][^sanotts-thread]
- Reconciliation notes: the card's exact figures supersede the thread's rounded ones (294,279–2,272,145 vs 294k–2.2M; amy 1.46M vs thread "1.51m"/"1.5m"); the card's comparative table corroborates the thread's Amy-vs-Inflect-vs-Kitten numbers and adds TinyTTS, UTMOS, and DNS-SIG; non-English voices remain unscored in both sources; capture bylines are partly anonymized (`unknown`) so maintainer identity is not attributed beyond the card's Ampixa copyright; jokes, solicitations, and voice-request chatter were excluded as non-durable (**Synthesis**).[^sanotts-hf-card][^sanotts-thread]
- Figures carry `stale_after: 2027-10-07` per `tts` domain rules for model releases and benchmarks; a future ingest of the repo/paper/weights/evidence package should reconcile the distillation recipe, `BOARDS.md` silicon figures, and numbers against this synthesis (**Synthesis**).[^sanotts-hf-card][^sanotts-thread]

[^sanotts-thread]: [sanoTTS release thread](../raw/i_released_sanotts_smallest_complete_tts_stack_in.md) — locators: header (r/LocalLLaMA, u/Affectionate_Hat_585, 509 votes, 121 comments); post bullets + paragraphs (11 voices/6 languages, 294k–2.2m, 244x Kokoro / 9000x Voxtral, 4.13 SCOREQ / 4.10 UTMOS, 337KB INT8, WASM `sanotts-web`, extension recipe, ~2% Whisper WER, repo/demo/HF links, Amy 4.13 vs Inflect 3.81 vs KittenTTS 3.02, ESP32 RTF 0.225 = 4s-per-1s); audio.cpp PR + merged/CPU-tested update + 7-row RTF table (nano 0.0027–0.0044, piperlite 0.0321–0.0390, ASR OK); Home Assistant/German + ESP32-S3 latency/RAM answers; Spanish/Persian/Japanese/German/Urdu/Punjabi/Hindi/French language answers + `ayutaz/sanoTTS-jp`; four-part pipeline + 50k fivesome + per-component training + closed-teacher mel-100/MFA answers; RSS 98,224 bytes / 1.8MB max RSS / 45M MAC / 240MHz / XIP / PSRAM / 29+ MMAC answers; `pip install sanotts` + `synthesize(..., voice="heart-nano")` snippets + C99/iPhone answers; repo + `arxiv.org/abs/2608.21378` answers; /z/ + 1–6kHz band diagnosis + sibilant/metallic detector + Chinese/whispery quality answers; teacher-clone recipe vs no zero-shot answers; Persian closed-model exchange; period-delay bug + fifteen/fifty threads; Whisper/wav2vec WER exchange; tts-bench add thread.
[^sanotts-hf-card]: [sanoTTS Hugging Face model card](../raw/sanoTTS.md) — locators: frontmatter (`license: gpl-3.0`, `language: [en, ne, hi, vi, id, zh]`, `pipeline_tag: text-to-speech`, `library_name: sanotts`, tags); header (294,279–2,272,145 params, 337KB–8.7MB footprint, ESP32-S3 + WASM, 11 voices / 6 languages, GPL-3.0, demo `tts.ampixa.com/sanoTTS`); `Download` fences (`sanotts.synthesize`, `SanoTTS.load`, `sanotts>=0.3.0` / `sanotts-web>=0.3.0`, `~/.cache/sanotts/`, `SANOTTS_VOICE_SOURCE`, `voiceBase` fallback-off); `Samples` 12-row table (voice/language/params/SCOREQ/package columns, robot 567k MCU row, heart-nano 294k/2.29, non-English 1.46–1.50M unscored) + SCOREQ-scope paragraph + piperlite-vs-nano lineage paragraph (22.05 kHz Piper/VITS vs 24 kHz mel-100 → ConvNeXt1D → iSTFT Kokoro/frozen-Vocos) + 2026-09-04 re-measure paragraph (`evidence/heart-diverse24-remeasure-20260904.json`, float32 reference, 0.981 vs 0.951 against 0.98 gate); `Install & use` table (pip/npm/dist-copy/Arduino/HF/browser rows); `How it stacks up` 6-row table (SCOREQ/UTMOS/DNS-SIG vs TinyTTS/Inflect/Kitten/Piper/Kokoro) + shipped-size + `tools/eval_mos_all.py`/`eval_scorecard.py` paragraphs; `How it works` (espeak-ng → duration → acoustic → decoder diagram alt-text, fp32 vs INT8 decoder paragraph, `docs/distillation-recipe.md` pointer); `Deploy` (ESP32-S3 on-chip espeak-ng + `mcu/ports/esp32s3/`, `BOARDS.md` `en_us_e12nano`-sibling caveat, browser WASM + `web/`, `docs/mcu-classes-and-porting.md`); `Links`; `License` (GPLv3, espeak-ng, piper1-gpl, (C) 2026 Ampixa); `Files here` (piperlite `manifest.json`/`weights.fp16.bin`/`piper-phoneme-config.json` list, nano `meta.json`/`front_*.bin`/`model_*.bin`/`nano_q8_meta.h` list with 345,232-byte INT8 vs 9,137,920-byte float32 totals, `web/voices/` duplication vs nano non-duplication, `samples/` + `evidence/` notes).
