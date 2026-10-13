---
type: Concept
title: CrispASR VAD and Language Identification
description: CrispASR's voice activity detectors (Silero default, FireRedVAD, MarbleNet, Whisper-VAD) and its audio and text language-identification providers, with model sizes, language coverage, and selection flags.
tags: [vad, lid, stt, endpointing, language-identification, ggml]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:35:00Z }
stale_after: 2027-10-13
sources:
  - id: crispasr-readme
    resource: ../raw/CrispASR.md
    kind: documentation
    title: CrispASR README
---

CrispASR uses VAD as a chunking front end (`--vad`), with four providers and Silero as the default. Audio language identification (LID) is a pre-step for backends without native language detection (`-l auto`), with five providers. Text LID runs on transcripts. The README cautions that an external detector can return a language the ASR model was never trained on, and it describes a probe that asks the ASR model itself (**Reported**).[^crispasr-readme]

## Voice activity detection

- `--vad` uses Silero VAD by default (~885 KB, auto-downloaded). The CLI table calls it "strongly recommended for multi-minute audio" (**Reported**).[^crispasr-readme]
- Each VAD segment is transcribed on its own, so SRT and VTT entries carry correct timestamps. `--vad --split-on-punct` is recommended for subtitle output (**Reported**).[^crispasr-readme]
- Four providers, selected with `-vm`:
  - **Silero** (default): described as industry-standard and well-tested (**Reported**).[^crispasr-readme]
  - **FireRedVAD** (`-vm firered`, auto-download, 2.4 MB): the README's recommendation, with F1 = 97.57%. That figure comes from FireRed's own FLEURS-VAD-102 table on an unreleased set; see [FireRedVAD](firered-vad.md) for the caveat (**Reported**; test-set caveat **Synthesis**).[^crispasr-readme]
  - **MarbleNet** (`-vm marblenet`, 439 KB): a 1D separable CNN covering EN, DE, FR, ES, RU, and ZH, from `cstr/marblenet-vad-GGUF`. NVIDIA's related checkpoint is covered in [Frame-VAD Multilingual MarbleNet v2.0](frame-vad-multilingual-marblenet-v2-0.md) (**Reported**; link **Synthesis**).[^crispasr-readme]
  - **Whisper-VAD-EncDec** (`-vm whisper-vad`, experimental, 22 MB Q4_K): a Whisper-base encoder with a Transformer decoder head, trained on Japanese ASMR, which the README says may not generalise. It is slower, about 1 s against about 50 ms for the others (**Reported**).[^crispasr-readme]

## Language identification for ASR

Cohere, canary, granite, voxtral, and voxtral4b need an explicit language code. `-l auto` runs an LID pre-step before the main call, and `--lid-backend` selects the provider. `--lid-backend off` skips LID (**Reported**).[^crispasr-readme]

| Provider | Model and size | Coverage | Notes (README) |
| --- | --- | --- | --- |
| `whisper` (default) | `ggml-tiny.bin`, ~75 MB, auto-download | 99 languages | Uses the crispasr C API |
| `silero` | Native GGUF, 16 MB F32 | 95 languages | Analyzes the first 30 s (`CRISPASR_SILERO_LID_MAX_S`); routed to CPU on Vulkan pending a kernel fix |
| `ecapa` | ECAPA-TDNN, Apache-2.0 | 107 (default, `cstr/ecapa-lid-107-GGUF`, 43 MB F16, ISO codes) or 45 (`cstr/ecapa-lid-commonlanguage-GGUF`, 40 MB F16, full names) | Marked "recommended"; the README claims "very high accuracy" on a TTS benchmark it does not name |
| `firered` | FireRedLID, Conformer encoder with Transformer decoder | 120 languages incl. Chinese dialects | Q4_K is 544 MB; the provider bullet gives 1.7 GB without naming its precision; slower |
| `probe` | No second model; implemented by cohere | The model's own declared languages | Runs automatically only for models with ≤ 4 languages (`CRISPASR_COHERE_PROBE_MAX_LANGS`) |

The probe transcribes a 20 s clip once per declared language and keeps the best candidate, scored by length, text-LID agreement, and distinct-token ratio squared. The encoder runs once and decoding runs per candidate. The README reports a 14-candidate probe falling from 12 s to 4–5 s, with byte-identical output (**Reported**).[^crispasr-readme]

- **Why the probe exists:** external LID knows 99 languages, while Cohere Transcribe accepts 14 (the README's table row says 13; see [CrispASR ASR Backend Selection](crispasr-asr-backend-selection.md)). An external detector can therefore return a language the model was never trained on, and Cohere then answers "fluently" rather than failing (**Reported**).[^crispasr-readme]
- **Soft spot:** a language outside the model's training can yield a clean translation that text LID confirms. "Fluent French out is not evidence of French in," and a mismatched whitelist is called dangerous (**Reported**).[^crispasr-readme]
- JSON output with `-l auto -oj` adds `language_detected`, `language_confidence`, and `language_source` fields (**Reported**).[^crispasr-readme]

## Text language identification

Text LID tags written text, while audio LID tags speech. The README describes three GGUF families behind one dispatcher, which routes on `general.architecture` (**Reported**).[^crispasr-readme]

- **CLD3:** 109 ISO 639-1 labels, 440 KB F16, Apache-2.0, from `cstr/cld3-GGUF`. The default for `auto` (**Reported**).[^crispasr-readme]
- **GlotLID-V3:** 2,102 ISO 639-3 labels plus script, 250 MB, Apache-2.0, from `cstr/glotlid-GGUF`. Chosen for maximum coverage (**Reported**).[^crispasr-readme]
- **LID-176:** 176 ISO 639-1 labels, 63 MB, CC-BY-NC-4.0 (non-commercial), from `cstr/fasttext-lid176-GGUF` (**Reported**).[^crispasr-readme]

Usage: `crispasr-lid -m auto --text "..."` for the standalone CLI, and `--lid-on-transcript auto` to run LID on the assembled transcript after ASR (**Reported**).[^crispasr-readme]

## Contradictions

- FireRedLID size: the provider bullet gives 1.7 GB, while the detailed paragraph gives a Q4_K size of 544 MB. The README does not state the precision of the larger figure, so neither is chosen (**Reported**).[^crispasr-readme]

## Coverage and limits

- Accuracy and timing examples (for instance, the `p=0.977` detection and the Arabic `p=0.675` probe) are README examples on unnamed clips. They were not reproduced (**Synthesis**).[^crispasr-readme]
- The `docs/cli.md` VAD and CTC-alignment sections, and the LID model registry, were not captured (**Synthesis**).
- The README's FireRedVAD and ECAPA accuracy claims are vendor or unnamed-benchmark assertions (**Reported**).[^crispasr-readme]
- No VAD or LID provider was loaded or run (**Synthesis**).

## Relationships

- Uses: [Silero VAD](silero-vad.md) (default), [FireRedVAD](firered-vad.md), and [Frame-VAD Multilingual MarbleNet v2.0](frame-vad-multilingual-marblenet-v2-0.md) as the provider checkpoints the README names (**Synthesis**).[^crispasr-readme]
- Feeds: [CrispASR ASR Backend Selection](crispasr-asr-backend-selection.md), since LID choice determines whether a backend needs `-l auto` (**Synthesis**).
- Related: [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md) for speaker and punctuation steps that follow VAD (**Synthesis**).
- Part of: [CrispASR](crispasr.md) (**Synthesis**).

[^crispasr-readme]: [CrispASR README](../raw/CrispASR.md) — locators: `Feature matrix` section (`--vad` and "Voice activity detection" paragraph listing the four VAD providers with sizes and F1; `--lid-backend` paragraph); `CLI reference` table (`--vad`, `-l auto` rows); `Language detection for backends that don't do it natively` (LID pre-step, provider bullets, probe paragraph with the "ceiling is about cost" and "soft spot" text); `Text language identification (post-ASR / standalone)` (CLD3, GlotLID-V3, LID-176 table and usage); `Progressive subtitle output` and `JSON output with language detection`; `Credits` (Silero, pyannote).
