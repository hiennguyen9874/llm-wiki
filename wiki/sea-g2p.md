---
type: Concept
title: SEA-G2P
description: Rust-core multilingual text normalizer and phonemizer for Vietnamese, Thai and Indonesian with English code-switching, usable from Python and a six-function C ABI, with README-reported throughput, mmap dictionary design, markup tags, and no license or accuracy evidence in the capture.
tags: [tts, g2p, text-normalization, vietnamese, thai, indonesian, rust, c-abi, phonemes]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T18:00:00Z }
stale_after: 2027-04-21
sources:
  - id: sea-g2p-readme
    resource: ../raw/pnnbao97-sea-g2p.md
    kind: documentation
    title: SEA-G2P README capture (pnnbao97/sea-g2p)
---

SEA-G2P (`pip install sea-g2p`, author Pham Nguyen Ngoc Bao) is a text-to-phoneme front end for TTS: per-language normalization (numbers, dates, units, abbreviations, formulas) followed by grapheme-to-phoneme conversion into IPA with one syllable per space, for **Vietnamese**, **Thai** and **Indonesian**, each with **English** code-switching. A Rust core backs both a Python package and a C ABI (**Reported**).[^sea-g2p-readme] It is the phonemizer credited by [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md), and it overlaps in role with the rule-based [VietNormalizer](vietnormalizer.md) while going further by also emitting phonemes.

## Languages and behavior

| Language | Front end | Output conventions | Notes (README) |
| --- | --- | --- | --- |
| Vietnamese (`lang="vi"`) | 17-stage normalizer (numbers, dates, units, formulas, technical terms) then G2P | IPA with tone digits (e.g. `4`, `6`, `5`), stress `ˈ`/`ˌ` | Mixed vi/en text: English runs go to an English engine and come out in one phoneme string |
| Thai (`lang="th"`) | 8-stage normalizer (Thai digits ๐-๙, Buddhist-era dates, `ๆ` repetition, abbreviation table), segmentation, rule-based G2P | IPA with **Chao tone letters** (`˧`, `˨˩`, `˥˩`, `˦˥`, `˩˩˦`), deliberately different from the Vietnamese digit tones so one inventory serves both | Normalize, segment and look up in one pass; 91,865-word dictionary with unigram-cost dynamic program; boundary F1 0.987 against PyThaiNLP `newmm`; out-of-dictionary text read by orthographic rule |
| Indonesian (`lang="id"`) | Normalizer (expands chat contractions such as `yg`→`yang`, `tdk`→`tidak`) then rule-based G2P | One syllable per space | 172,557-word dictionary from WikiPron and KBBI plus affix, compounding and reduplication derivation; KBBI settles the ambiguous ⟨e⟩ (/ə/ vs /e/) |

All figures and examples are **Reported**.[^sea-g2p-readme] The `lang` code for Indonesian is `"id"`; the README notes the variable should not be named `id` because it shadows the built-in (**Observed**).[^sea-g2p-readme]

## Python API

- `SEAPipeline(lang=...).run(text_or_list)` runs normalize + G2P; passing a list triggers automatic parallel processing.
- `Normalizer(lang=...).normalize(...)` and `G2P(lang=...).convert(...)` expose the stages separately; the Vietnamese normalizer emits `<en>…</en>` spans (e.g. `<en>u s d</en>`) that the G2P hands to the English phonemizer.[^sea-g2p-readme]
- **Markup tags** let the caller control reading: `<en>…</en>` keeps content for the English phonemizer; `<math>…</math>` reads a formula (variable clusters spelled letter by letter, operators voiced, function names such as `sin`, `cos`, `log`, `lim` preserved; examples given for Vietnamese).[^sea-g2p-readme]
- Development: `pip install -e .`; tests via `cargo test --release`, a `capi`-only variant without PyO3, and `python -m pytest tests/`.[^sea-g2p-readme]

## C / C++ interface

A native host (C++ TTS runtime, mobile app, game engine) can call the same Rust core instead of reimplementing rules; the README argues that two Vietnamese normalizers drift apart when one is corrected and the drift appears as untraceable mispronunciation (**Reported** rationale).[^sea-g2p-readme]

- Artifacts: `libsea_g2p_rs.{so,dylib}` / `sea_g2p_rs.dll`, `sea_g2p.h`, and the `sea_g2p.bin` dictionary from a release (Linux, Windows, macOS), or build with `cargo build --release --no-default-features --features capi`; from a checkout the dictionary is `python/sea_g2p/sea_g2p.bin`.
- Surface of six functions: `sea_g2p_open(dict)`, `sea_g2p_phonemize(g, text, flag)`, `sea_g2p_normalize()` (the length a chunker should measure, after numbers become words), `sea_g2p_punc_norm()` (trailing-punctuation rule alone), `sea_g2p_string_free()`, `sea_g2p_close()`, plus `sea_g2p_last_error()` for a per-thread message. Strings are UTF-8 and caller-owned; failures return NULL; Rust panics are caught at the boundary. The meaning of the third `phonemize` argument (`1` in the example) is not explained in the README.
- The library can be loaded at runtime, which the README says is how [audio.cpp](audio-cpp-framework.md) reads Vietnamese text for VieNeu-TTS without a Rust build dependency; that audio.cpp-side behavior is not corroborated here.[^sea-g2p-readme]

For a streaming voice agent, `sea_g2p_normalize()` is the natural hook for the chunker → normalizer → TTS stage described in [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md): chunk on post-normalization length (**Synthesis**).

## Architecture

- **mmap dictionary:** a custom binary `.bin` mapped into memory rather than loading JSON/SQLite into RAM, for near-instant start and low memory.
- **String pooling:** unique words and phonemes stored once and referenced by 4-byte IDs.
- **Binary search:** words pre-sorted at build time for O(log n) lookup directly on mapped data.
- **Per-language sections:** one binary holds all languages; non-Latin scripts get their own namespace so Thai data ships beside Vietnamese/English tables and cannot desynchronize.
- Source layout: `src/core/` (dictionary loader, generic abbreviation table), `src/lang/{vi,en,th,id}/`, `src/g2p/` (shared Latin-script engine), `tests/` (Rust integration and Python end-to-end). The binary format spec is `src/core/dict.rs`.[^sea-g2p-readme]

## Reported throughput

| Language | Stage | Sentences/s |
| --- | --- | --- |
| Vietnamese | Normalizer | ~41,000 |
| Vietnamese | G2P | ~415,000 |
| Vietnamese | Full pipeline | ~37,000 |
| Thai | Normalizer | ~1,000,000 |
| Thai | Full pipeline (normalize + segment + G2P) | ~180,000 |
| Indonesian | Full pipeline | ~500,000 |

Conditions stated: a dataset of 1,000,000 sentences, CPython 3.12, Windows 11, multithreaded (**Reported**).[^sea-g2p-readme] The README does not name the corpus, thread count, CPU, or sentence-length distribution, so rates are not comparable to the [VietNormalizer](vietnormalizer.md) per-call latency (~0.6 ms, single call), and throughput under Rayon batching says little about single-clause latency in a realtime loop (**Synthesis**).

## Relationships

- Phonemizer for [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) (README "Used By" list and that model card's credits); both are by the same author, so the "high-fidelity pronunciation and seamless code-switching" claim is self-reported (**Reported**).[^sea-g2p-readme]
- Alternative or complement to [VietNormalizer](vietnormalizer.md) for Vietnamese text normalization; the two differ in normalization stages (17 vs 19), output (SEA-G2P adds phonemes), and implementation (Rust vs pure Python). Which reads Vietnamese more accurately is untested (**Synthesis**).
- Fills the normalizer/phonemizer slot discussed in [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) and [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md), but only for TTS models trained on its phoneme inventory (**Synthesis**).
- Comparable in role to [Misaki](misaki.md) (G2P for Kokoro), whose [language frontends](misaki-language-frontends.md) do not establish a Vietnamese module; the phoneme sets are not interchangeable (**Synthesis**).
- Runtime loading from [audio.cpp Framework](audio-cpp-framework.md) is claimed by this README only.

## Coverage and limits

- Inspected statically: the single README capture `raw/pnnbao97-sea-g2p.md` (**Observed**); no revision, version number, release tag or date recorded; no license statement appears in the capture.[^sea-g2p-readme]
- Not inspected: `thai/README.md`, `indo/README.md` (data pipelines and the measurements/rejected approaches they describe), `include/sea_g2p.h`, `src/core/dict.rs`, source, tests, releases, the PyPI package, and the header image. No install, build, execution or listening.
- Not stated: accuracy (phoneme error rate, normalization correctness) for any language, ambiguity handling in Vietnamese dates/numbers, Thai F1 evaluation corpus, single-call latency, memory footprint, dictionary size for Vietnamese/English, thread-safety of the C handle, and the phoneme-inventory spec downstream models must match.
- Marketing wording ("Zero Dependency", "Blazing Fast", "seamless") is promotional; "zero dependency" refers to pre-compiled wheels, and the Rust crate has its own dependencies (PyO3/Rayon named in the text) (**Observed** wording, **Synthesis** reading).
- `stale_after` follows the `tts` domain rule for tooling and benchmark numbers.

[^sea-g2p-readme]: [SEA-G2P README capture](../raw/pnnbao97-sea-g2p.md) — locators: title and intro (languages, Python and C ABI, author); `## 🚀 Used By` (VieNeu-TTS); `## Usage` (`### Simple Pipeline`, `### Thai`, `### Indonesian`, `### Individual Modules`); `## Using it from C / C++` (artifacts, cargo `capi` build, C example, six-function surface, runtime loading by audio.cpp); `## Features` (17/8-stage normalizers, Thai segmentation F1 0.987, Indonesian 172,557-word dictionary, markup tags `<en>`/`<math>`); `## 📊 Performance` (throughput table and test conditions); `## Technical Architecture` (mmap, string pooling, binary search, per-language sections, source layout table); `## Development`.
