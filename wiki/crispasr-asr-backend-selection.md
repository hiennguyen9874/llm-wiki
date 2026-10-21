---
type: Concept
title: CrispASR ASR Backend Selection
description: "Choosing a CrispASR ASR backend: families from Whisper and NVIDIA NeMo through speech-LLMs to CTC-only and streaming models, the 24-column capability matrix, Vietnamese coverage, translation, and CPU speed guidance, all README-reported."
tags: [stt, asr, backend-selection, streaming, multilingual, ggml]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:25:00Z }
stale_after: 2027-10-13
sources:
  - id: crispasr-readme
    resource: ../raw/CrispASR.md
    kind: documentation
    title: CrispASR README
---

CrispASR's README lists about 78 ASR table rows and a 24-column capability matrix. Backend families run from Whisper and NVIDIA NeMo models (Parakeet, Canary, FastConformer-CTC) through speech-LLMs (Qwen3-ASR, Voxtral, Granite, GLM-ASR, Fun-ASR) to CTC-only and streaming models. Its own guidance is: whisper for battle-tested use, cohere for lowest English WER, moonshine or fc-ctc for CPU speed, parakeet for multilingual work with word timestamps, and canary, voxtral, or qwen3 for speech translation (**Reported**).[^crispasr-readme]

## Backend families

- **Whisper family:** `whisper` covers OpenAI Whisper variants (99 languages, MIT); `distil-whisper` distil-large-v3 is English-only; `tiron` is an experimental Whisper large-v3 variant with `<|speakerN|>` markers and constrained decoding (**Reported**).[^crispasr-readme]
- **NVIDIA NeMo:** `parakeet` covers TDT, RNNT, and CTC checkpoints, including parakeet-tdt-0.6b-v3 (25 European languages with auto-detect). `canary` covers canary-1b-v2 (25 European languages, explicit `-sl`/`-tl`) and canary-180m-flash (en, de, es, fr plus EN↔DE/ES/FR translation). `canary-qwen` covers the 2.5B English SALM model. `fastconformer-ctc` covers the CTC family (**Reported**).[^crispasr-readme]
- **Speech-LLM backends:** `qwen3` and `qwen3-1.7b` (30 languages plus Chinese dialects), `voxtral` and `voxtral4b` (the latter realtime, 13 languages), `granite` and `granite-4.1` variants, `glm-asr`, `funasr` and `fun-asr-mlt-nano`, `higgs-stt`, `kyutai-stt`, `moss-audio`, `moss-transcribe`, `moss-diarize`, `hojo-asr`, `mimo-asr`, `gemma4-e2b`/`e4b`, `vibevoice` and `vibevoice-streaming`, `lfm2-audio`, `index-echo`, and `confucius4-r2t2` (**Reported**).[^crispasr-readme]
- **Encoder-decoder and CTC-only:** `cohere` (Conformer plus Transformer; 13 languages in its table row, see [Contradictions](#contradictions)), `wav2vec2`, `omniasr` (CTC, "1600+" languages), `sensevoice` (CTC with native language ID and audio-event tags), `paraformer` (non-autoregressive, character vocabulary, no native punctuation), `firered-asr`, and the `moonshine` family (fastest CPU option) (**Reported**).[^crispasr-readme]
- **Regional specialists:** `dolphin` (Mandarin and Chinese dialects), `xasr` (zh/en streaming Zipformer2 with a realtime WebSocket session), `reazonspeech` and `parakeet` Japanese variants, and `gigaam` (Russian; the `e2e_rnnt` and `e2e_ctc` revisions emit punctuation, casing, and ITN) (**Reported**).[^crispasr-readme]

## Capability matrix

The README's matrix covers 24 ASR columns. Items below are the rows that most affect backend choice (**Reported**).[^crispasr-readme]

- **Native timestamps:** whisper, parakeet, canary, cohere, and kyutai-stt. Other backends get word-level timing through a CTC forced aligner (`-am`) (**Reported**).[^crispasr-readme]
- **Native language auto-detect:** whisper, parakeet, qwen3, glm-asr, gemma4-e2b, mimo-asr, and sensevoice. The other columns use an external LID pre-step (`-l auto`); see [CrispASR VAD and Language Identification](crispasr-vad-language-id.md) (**Reported**).[^crispasr-readme]
- **Speech translation:** whisper, canary, granite, granite-4.1, voxtral, and qwen3. Source and target language selection applies to canary, granite, granite-4.1, voxtral, and qwen3 (**Reported**).[^crispasr-readme]
- **Grammar (GBNF):** whisper only. **Audio Q&A (`--ask`):** full support for voxtral; experimental or partial for several speech-LLM columns (**Reported**).[^crispasr-readme]
- **Streaming and auto-download:** every ASR column is marked ✔ for both (see the caveat below) (**Reported**).[^crispasr-readme]

## Which backend to pick

The README's decision table, condensed (**Reported**; the speed and accuracy numbers are vendor or README claims):

- Battle-tested, all features exposed: whisper (**Reported**).[^crispasr-readme]
- Lowest English WER: cohere (**Reported**).[^crispasr-readme]
- Fastest on CPU: moonshine tiny (16× realtime) and fc-ctc (10×) (**Reported**).[^crispasr-readme]
- Multilingual with word timestamps and speed: parakeet (2.9× realtime) (**Reported**).[^crispasr-readme]
- Explicit language control: canary (**Reported**).[^crispasr-readme]
- Speech translation (X→en or en→X): canary, voxtral, qwen3 (**Reported**).[^crispasr-readme]
- 30 languages plus Chinese dialects: qwen3 (**Reported**).[^crispasr-readme]
- 1600+ languages: omniasr (CTC or LLM) (**Reported**).[^crispasr-readme]
- Realtime streaming ASR: voxtral4b (**Reported**).[^crispasr-readme]
- Apache-licensed speech-LLM: granite, voxtral, qwen3, omniasr-llm (**Reported**).[^crispasr-readme]
- Lightweight CTC-only: wav2vec2, fc-ctc, data2vec, omniasr (**Reported**).[^crispasr-readme]
- Russian: gigaam `e2e_rnnt` (8.4% average WER claim), whisper, qwen3 (**Reported**).[^crispasr-readme]
- Mandarin and dialects: firered-asr, qwen3, glm-asr, funasr, paraformer, sensevoice (**Reported**).[^crispasr-readme]
- Multilingual speech-LLM with 31 languages: fun-asr-mlt-nano, qwen3, omniasr-llm, gemma4-e2b (**Reported**).[^crispasr-readme]
- 50+ languages with LID and audio-event tags in one pass: sensevoice (**Reported**).[^crispasr-readme]

## CPU guidance

- Audio-LLM backends run full decoder stacks and can drop below 0.01× realtime on older dual-core CPUs. For CPU-only machines the README prefers moonshine (16× RT), fc-ctc (10× RT), parakeet (2.9× RT), or whisper (**Reported**).[^crispasr-readme]
- Use `--flush-after 1` for progressive output and quantize to Q4_K or Q5_K to reduce memory and compute (**Reported**).[^crispasr-readme]
- The README's throughput labels lack hardware descriptions. The "10.1× realtime" in its Start-here example and the "2.9× RT" CPU figure cannot be compared (**Synthesis**).[^crispasr-readme]

## Vietnamese coverage

- The README names Vietnamese only in the 31-language list of `fun-asr-mlt-nano` (FunAudioLLM Fun-ASR-MLT-Nano-2512, FunASR Model License v1.1) (**Reported**).[^crispasr-readme]
- No backend is described as Vietnamese-specific. Breadth claims such as omniasr's "1600+" and qwen3's "30 languages" are not per-language evaluations, so they do not establish Vietnamese quality (**Synthesis**).[^crispasr-readme]
- For Vietnamese selection context across the wiki, see [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md) (**Synthesis**).

## Translation and speech-to-speech helpers

- Text translation via `--text "..." -sl <src> -tl <tgt>`: m2m100 (100 languages, any-to-any), m2m100-wmt21 (4.7B, with separate en-x and x-en checkpoints), marian (24 directions, one per checkpoint), and madlad (419 languages). `--tr-sl`/`--tr-tl` set the languages for two-stage pipelines (**Reported**).[^crispasr-readme]
- Speech-to-speech restoration or upscaling via `--s2s`: sidon (16 kHz mono to restored 48 kHz) and voxcpm2-vae (upscaling) (**Reported**).[^crispasr-readme]

## Feature-matrix caveats

- The matrix marks speaker diarization ✔ for all 24 columns, yet the README describes diarization as a post-processing step (`--diarize`). Read it as tool-level availability, not a backend capability (**Synthesis**).[^crispasr-readme]
- The matrix marks streaming ✔ for all 24 columns. The README names native or session-based streaming for only a few paths: voxtral4b (native incremental encoder), xasr (realtime WebSocket session), confucius4-r2t2 (append-only session with prefix rollback), moonshine-streaming (sliding-window encoder plus AR decoder), and vibevoice-streaming (persistent-KV chunks). See [CrispASR Streaming and HTTP Server](crispasr-streaming-http-server.md) (**Synthesis**).[^crispasr-readme]

## Relationships

- Uses: the README's backend-to-checkpoint mapping points to model concepts already in the wiki, for example [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md), [Canary-1b-v2](canary-1b-v2.md), [Canary-Qwen-2.5B](canary-qwen-2.5b.md), [Cohere Transcribe 03-2026](cohere-transcribe-03-2026.md), [Whisper Large v3](whisper-large-v3.md), [Qwen3-ASR family](qwen3-asr-family.md), [Voxtral Mini 3B 2507](voxtral-mini-3b-2507.md), [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md), [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md), [SenseVoiceSmall GGUF](sensevoice-small-gguf.md), [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md), [GLM-ASR-Nano-2512](glm-asr-nano-2512.md), [Higgs Audio v3 STT](higgs-audio-v3-stt.md), and [VibeVoice-ASR](vibevoice-asr.md). Model-specific accuracy and license claims belong to those pages, not to this README (**Synthesis**).[^crispasr-readme]
- Part of: [CrispASR](crispasr.md) (**Synthesis**).

## Contradictions

- Cohere language count: the ASR table row for `cohere-transcribe-03-2026` says 13 languages, while the language-detection section says Cohere "accepts 14" and describes a "14-language base model". Neither figure is chosen (**Reported**).[^crispasr-readme]

## Coverage and limits

- The ASR table is condensed here (78 rows, 24-column matrix) and not reproduced. Per-backend sizes, licenses, and languages come from the README rows only (**Synthesis**).[^crispasr-readme]
- The 109-backend `docs/feature-matrix.md` and the sortable HTML view were not captured (**Synthesis**).
- No backend was loaded, run, or benchmarked. WER, RTF, and realtime figures stay **Reported** (**Synthesis**).

[^crispasr-readme]: [CrispASR README](../raw/CrispASR.md) — locators: `Supported backends` and `ASR backends` table rows (families, languages, licenses); `Feature matrix` intro and 24-column table (native timestamps, auto-detect, translation, GBNF, `--ask`, streaming, auto-download rows) and the caveat paragraph (`-am`, `pp`, `LID`, `*`); `Which backend should I pick?` table; `CPU performance tips`; `Translation` section; `Post-processing models` and `Speech-to-speech audio upscaling and restoration` sections; the `fun-asr-mlt-nano` row (31 languages incl. vi); `Supported backends` intro (diarization and streaming caveats via matrix).
