---
type: Concept
title: NeMo-Speech.cpp ASR Configuration
description: Recognizer-level configuration for NeMo-Speech.cpp ASR — the `asr.*` key surface, CTC greedy versus flashlight decoding, word boosting, Silero VAD feature masking, endpointing modes, batching policy, profanity/ITN/PnC postprocessing, and gRPC adapter limits.
tags: [stt, pipeline, asr, endpointing, vad, word-boosting, gguf]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:10:00Z }
stale_after: 2027-10-07
sources:
  - id: nemo-speech-cpp-docs
    resource: ../raw/nemo-speech-cpp-docs/README.md
    scope: ../raw/nemo-speech-cpp-docs/
    kind: documentation
    revision: 8642eaa5cc51efbc17ad0f3e433944ba858a873f
    title: NVIDIA/NeMo-Speech.cpp supporting docs
---

[NeMo-Speech.cpp](nemo-speech-cpp.md) shares one `asr.*` recognizer configuration set across `nemo-speech serve`, `nemo-speech transcribe`, and the separate `riva_server`, with strict precedence `built-in defaults < --config FILE.yaml < NEMO_SPEECH_<KEY> env < CLI option`, hard errors on unknown keys, and turn-on-able behavior for CTC flashlight rescoring, per-request word boosting, optional Silero VAD feature masking, mid-stream endpointing, and a profanity → ITN → PnC postprocessing chain (**Reported**).[^nemo-speech-cpp-docs]

## Configuration surface and precedence

- Keys nest under `asr.`; every key is optional and defaults are source-stated. The dotted form (`--asr.<key>`) always works and is what YAML uses, while short CLI aliases are conveniences — `nemo-speech serve` accepts aliases such as `--asr-model`, but `riva_server` does not (**Reported**).[^nemo-speech-cpp-docs]
- Environment variables uppercase the dotted key and replace `.` and `-` with `_`, so `asr.model.path` becomes `NEMO_SPEECH_ASR_MODEL_PATH`; boolean keys accept an explicit value such as `--asr.endpointing.enable=false` (**Reported**).[^nemo-speech-cpp-docs]
- `asr.enabled` is the one server-only key and takes `true`, `false`, or `auto` (default) (**Reported**).[^nemo-speech-cpp-docs]

### Selected key defaults

| key | default | meaning |
|---|---|---|
| `asr.model.path` | – | GGUF path, required for ASR |
| `asr.backend.gpu` | `0` | GPU index; `-1` = CPU |
| `asr.streaming.chunk_size` | `0.16` | CTC buffered window (s) |
| `asr.streaming.ctc_left_padding` / `ctc_right_padding` | `1.92` / `1.92` | CTC left / right context (s) |
| `asr.streaming.rnnt_right_context` | `1` | cache-aware R; `-1` = model max |
| `asr.decoder.kind` | `greedy` | `greedy` or `flashlight` |
| `asr.decoder.lm_path` / `lexicon_path` | – | KenLM `.bin`/`.arpa` + lexicon TSV (implies flashlight) |
| `asr.decoder.beam_size` / `lm_weight` / `word_insertion_score` | `32` / `0.8` / `1.0` | flashlight tuning |
| `asr.decoder.max_boost` | `10.0` | CTC max per-word boost |
| `asr.decoder.boosting_tree_alpha` / `boosting_max_boost` / `boosting_depth_scaling` | `1.0` / `5.0` / `2.0` | RNNT word-boosting weight, clamp, depth scaling |
| `asr.vad.model_path` | – | Silero VAD GGUF; empty = no VAD |
| `asr.vad.masker.mask_enable` | `false` | mask silence mel frames |
| `asr.vad.masker.onset` / `offset` | `0.5` / `0.3` | speech enter / leave thresholds |
| `asr.vad.masker.pad_ms` / `min_duration_off_ms` / `mask_value` | `200` / `500` / `-16.635` | edge padding, min maskable silence, log-mel fill |
| `asr.endpointing.enable` / `vad_based` | `false` / `false` | mid-stream EOU toggle / VAD-driven mode |
| `asr.endpointing.stop_history_eou_ms` | `800` | trailing-silence EOU threshold (ms) |
| `asr.postproc.profanity_list_path` / `itn_model_dir` / `pnc_model_path` | – | postprocessing artifacts |
| `asr.batching.enabled` / `max_batch_size` / `max_queue_delay_us` | surface-dependent / `1024` / `5000` | batching policy |

All rows and the remaining keys are the source's `Key reference` table (**Reported**).[^nemo-speech-cpp-docs]

## CTC decoding: greedy versus flashlight

- CTC heads run greedy argmax by default; setting `asr.decoder.lm_path` (KenLM `.bin`/`.arpa`) plus `asr.decoder.lexicon_path` (flashlight lexicon TSV) enables Flashlight beam search with n-gram rescoring (**Reported**).[^nemo-speech-cpp-docs]
- Flashlight requires a `-DNEMO_SPEECH_WITH_FLASHLIGHT=ON` build and dynamically links `libkenlm` (`kenlm.dll` on Windows) from the shared-library search path; greedy is always available (**Reported**).[^nemo-speech-cpp-docs]
- LM artifacts are model-specific — source your own KenLM binary/ARPA plus a matching lexicon TSV — and beam tunables (`asr.decoder.beam_size` 32, `beam_threshold` 20.0, `lm_weight` 0.8, `word_insertion_score` 1.0) are meant to be tuned for the language model, lexicon, and audio domain (**Reported**).[^nemo-speech-cpp-docs]

## Word boosting

- Word boosting biases recognition toward caller-supplied names and jargon, exposed as `RecognitionConfig.speech_contexts` in gRPC, the `speech_contexts` HTTP/realtime field, and `--speech-context` in the CLI; HTTP `prompt` supplies one phrase at boost 10 (**Reported**).[^nemo-speech-cpp-docs]
- Support is decoder-specific: Flashlight CTC and cache-aware RNNT support boosting, while greedy CTC without an LM and Parakeet TDT ignore `speech_contexts` (**Reported**).[^nemo-speech-cpp-docs]
- Boosting requires the SentencePiece tokenizer embedded in current GGUFs; older GGUFs need reconversion with `convert_model.py`, or `asr.decoder.tokenizer_path` for CTC (**Reported**).[^nemo-speech-cpp-docs]
- Typical CTC flashlight request scores are 8–10, capped by `asr.decoder.max_boost` (10); typical cache-aware RNNT scores are 2–3, capped by `asr.decoder.boosting_max_boost` (5.0). CTC and RNNT scores are not directly comparable (**Reported**).[^nemo-speech-cpp-docs]

## VAD feature masking

- Optional Silero VAD masks silence features before the encoder; it stays off even with a loaded VAD model unless `asr.vad.masker.mask_enable` is set, and it works with greedy and LM decoding on CTC and RNNT (**Reported**).[^nemo-speech-cpp-docs]
- The VAD model is a separate GGUF, not part of the ASR model: `pip install "silero-vad==6.2.0"` then `python3 convert_model.py silero --outfile models/silero-v6.2.0.gguf`, passed via `--vad-model` (**Reported**).[^nemo-speech-cpp-docs]
- Masking and [endpointing](#endpointing) are independent and can be enabled separately or together (**Reported**).[^nemo-speech-cpp-docs]

## Endpointing

- Off by default, the server emits one final when the client closes the stream; with `asr.endpointing.enable` it detects end-of-utterance mid-stream and emits one final per utterance (multiple `is_final=true` per stream) (**Reported**).[^nemo-speech-cpp-docs]
- It works with buffered CTC and cache-aware RNNT; the offline-only [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) does not support streaming endpointing (**Reported**).[^nemo-speech-cpp-docs]
- EOU fires when trailing silence reaches `asr.endpointing.stop_history_eou_ms` (800) and then re-arms on the next speech. The default **token-silence** mode uses the gap since the decoder's last non-blank frame and needs no VAD model; **VAD-driven** mode (`asr.endpointing.vad_based` + a VAD model) uses the Silero timeline and falls back to token-silence with a warning when no VAD model is loaded (**Reported**).[^nemo-speech-cpp-docs]
- For Riva-compatible gRPC clients, `custom_configuration["stop_history_eou"]` overrides the threshold per stream and a `runtime_config["force_eou"] = "true"` message finalizes the current utterance once received audio is decoded (**Reported**).[^nemo-speech-cpp-docs]

## Batching

- Batching is off by default for direct library use to preserve single-request latency; `nemo-speech serve` enables it by default, while `nemo-speech transcribe` and `nemo-speech bench` enable and size it automatically only when they run more than one utterance concurrently; `nemo-speech transcribe --no-batching` disables the automatic policy, and the gRPC server and direct library users opt in with `--asr.batching.enabled` (**Reported**).[^nemo-speech-cpp-docs]
- With batching enabled, a default 5 ms neural queue window combines compatible CTC, RNNT, TDT, VAD, and PnC work while preserving bounded backpressure; `offline_bucket_ms` can silence-pad offline utterances to compatible lengths but is disabled by default because padding adds work (**Reported**).[^nemo-speech-cpp-docs]
- HTTP and gRPC streaming coordinate concurrent input streams before batching via `ingress_cohort_delay_us`; direct library calls and CLI commands do not add that transport delay. Tuning detail is delegated to `docs/development/asr-batching.md`, which is outside this capture (**Reported**, with unfetched-pointer limit).[^nemo-speech-cpp-docs]

## Postprocessing: profanity, ITN, PnC

Postprocessing runs on the final transcript in the fixed order profanity → ITN → PnC, and each stage needs its configured artifact plus its request option (**Reported**).[^nemo-speech-cpp-docs]

| stage | config key | build flag | per-request gate |
|---|---|---|---|
| Profanity filter | `asr.postproc.profanity_list_path` | none (always compiled) | request sets `profanity_filter` |
| ITN (Sparrowhawk) | `asr.postproc.itn_model_dir` | `-DNEMO_SPEECH_WITH_NORM=ON` | runs unless `verbatim_transcripts` |
| PnC (BERT punct + caps) | `asr.postproc.pnc_model_path` | none (always compiled) | request sets `enable_automatic_punctuation` |

- **Profanity** matches one word per line, case-insensitively, and masks while keeping the first letter (`damn` → `d***`) with trailing punctuation preserved (**Reported**).[^nemo-speech-cpp-docs]
- **ITN** converts spoken form to written form ("twenty twenty four" → "2024"); the grammar dir requires `tokenize_and_classify.far` and `verbalize.far`, loads lazily on first use, and requires a `-DNEMO_SPEECH_WITH_NORM=ON` build. For Nemotron 3.5, point it at a parent whose children are named `en`, `es`, `de`, … so the explicit request language selects the child and `language_code=auto` uses the model-detected language; locale codes such as `es-ES` fall back to `es` (**Reported**).[^nemo-speech-cpp-docs]
- **PnC** restores casing and `. , ?` with a BERT token classifier for models that emit lowercase unpunctuated text (for example [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md)); the request gates are independent (**Reported**).[^nemo-speech-cpp-docs]

## gRPC compatibility limits

The Riva-compatible gRPC adapter states these limitations (**Reported**).[^nemo-speech-cpp-docs]

- **LINEAR_PCM only.** Mono 16-bit PCM 8–96 kHz is accepted and resampled to the model rate with a streaming anti-alias filter; FLAC, µ-law, A-law, and Opus require client-side transcoding.
- **N-best is not implemented.** `max_alternatives` is accepted, but current decoders return one alternative per result.
- **No utterance-onset gating** and no `min_duration_on` short-speech deletion.
- **Confidence:** interim alternatives report 0.0; final greedy CTC alternatives report mean token posterior (with per-word minima when timestamps are requested); RNNT and beam-decoded results currently report 1.0.

## Relationships

- Configures [NeMo-Speech.cpp](nemo-speech-cpp.md): this is the recognizer-level sibling of that page's runtime identity; the server/listener and HTTP surfaces live in [NeMo-Speech.cpp Server and Deployment](nemo-speech-server.md) and [NeMo-Speech.cpp HTTP and Realtime API](nemo-speech-http-api.md) (**Synthesis**).[^nemo-speech-cpp-docs]
- Uses [Silero VAD](silero-vad.md) as the external GGUF behind VAD feature masking and VAD-driven endpointing; consult that page for the model's footprint and runtimes (**Synthesis**).[^nemo-speech-cpp-docs]
- Uses [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) for the language-prompt-conditioned ITN grammar selection, and contrasts with [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) (offline-only, no streaming endpointing) and [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md) (the model PnC is documented for) (**Synthesis**).[^nemo-speech-cpp-docs]

## Coverage and limits

- Source inspected statically only. The capture's five documents were read as captured Markdown and their SHA-256 digests re-computed to match `checksums.json` (**Observed** for capture integrity; the manifest is a local capture record, not independent provenance). Every configuration, default, and behavior claim is a documentation assertion not reproduced here (**Reported**).[^nemo-speech-cpp-docs]
- No build was configured, no server or CLI was run, no model or companion GGUF was downloaded or converted, and no boost/endpointing/masking effect was measured, so decoder, boosting, and endpointing quality claims remain unverified (**Synthesis**).[^nemo-speech-cpp-docs]
- `docs/development/asr-batching.md` (linked for batching tuning), `docs/model-conversion.md`, `config/*.example.yaml`, and the TTS/NMT/S2S configuration references are outside this capture and were not fetched (**Synthesis**).[^nemo-speech-cpp-docs]
- Defaults, model names, and build-flag requirements are version-sensitive and carry `stale_after: 2027-10-07` under the `stt`/`vad` domain rules (**Synthesis**).[^nemo-speech-cpp-docs]

[^nemo-speech-cpp-docs]: [NVIDIA/NeMo-Speech.cpp supporting docs](../raw/nemo-speech-cpp-docs/README.md) — capture at upstream revision `8642eaa5cc51efbc17ad0f3e433944ba858a873f` (2026-10-07). Locators: `docs/asr/configuration.md` → intro (shared config, `asr.enabled` server-only), `Key reference` table (all `asr.*` keys, CLI aliases, defaults), batching paragraph (`--no-batching`, 5 ms window, `offline_bucket_ms`, `ingress_cohort_delay_us`, `docs/development/asr-batching.md` pointer), `CTC decoding: greedy vs flashlight` (KenLM, lexicon, `NEMO_SPEECH_WITH_FLASHLIGHT=ON`, beam tunables), `Word boosting` (gRPC/HTTP/CLI surfaces, tokenizer requirement, CTC 8–10 vs RNNT 2–3, greedy-CTC/TDT ignore), `VAD feature masking` (Silero GGUF conversion, `--vad-masking`, masking/endpointing independence), `Endpointing` (off by default, token-silence vs VAD-driven, `stop_history_eou_ms`, TDT exclusion, `stop_history_eou`/`force_eou`), `Postprocessing: profanity, ITN, PnC` (order, stage table, masking behavior, Sparrowhawk parent-dir language selection, PnC), `gRPC compatibility` (LINEAR_PCM, N-best, onset gating, confidence); `docs/server.md` → `Engine and listener configuration` (precedence chain, env naming, aliases, boolean negation). Limitations: `config/*.example.yaml`, `docs/{tts,nmt,s2s,development}/`, and build/install/cli/sdk/troubleshooting docs are excluded by the capture.
