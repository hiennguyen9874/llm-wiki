---
type: Concept
title: VietNormalizer
description: Dependency-free MIT-licensed Python library that converts Vietnamese text to spoken form for TTS (numbers, dates, currency, units, acronyms, English-word transliteration) in a fixed 19-step pipeline with CSV dictionaries and a reported ~0.6 ms per call.
tags: [tts, vietnamese, text-normalization, python, pipeline]
status: stable
created: 2026-10-08
generated: { by: llm-wiki-agent/1, at: 2026-10-08T09:00:00Z }
stale_after: 2027-10-08
sources:
  - id: vietnormalizer-readme
    resource: ../raw/vietnormalizer.md
    kind: documentation
    title: Vietnamese Text Normalizer (vietnormalizer) README capture
---

VietNormalizer (`pip install vietnormalizer`) is a pure-standard-library Python 3.8+ package that rewrites Vietnamese text into spoken form before TTS or NLP, ported from the JavaScript project `nghitts`; it expands numbers, dates/times, currency, percentages, ordinals, phone numbers and measurement units, replaces acronyms and foreign words from CSV dictionaries, and transliterates remaining non-Vietnamese words by rule (**Reported**).[^vietnormalizer-readme] It fills the "Vietnamese spoken-text normalizer" slot that [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md) leaves without a chosen library, but this wiki has not verified it.

## Capabilities

| Input | Output (as shown in README) |
| --- | --- |
| `123` | `một trăm hai mươi ba` |
| `25/12/2023, lúc 14:30` | day/month/year and `mười bốn giờ ba mươi phút` words |
| `25-26/12` (date range) | `hai mươi lăm đến hai mươi sáu tháng mười hai` |
| `50.000đ` | `năm mươi nghìn đồng` (VND and USD supported) |
| `3-5%`, `6,5%` | `ba đến năm phần trăm`, `sáu phẩy năm phần trăm` |
| `1873-1907` | year range read as cardinals with `lẻ` |
| `thứ 2` | `thứ hai` |
| `120km/h`, `500m2` | `một trăm hai mươi ki-lô-mét trên giờ`, `năm trăm mét vuông` |
| `TV`, `AI`, `NASA` | `ti vi`, `trí tuệ nhân tạo`, `na-sa` (dictionary) |
| `container`, `Singapore` | `công-tê-nơ`, `xin-ga-po` (dictionary) |
| `algorithm`, `database` | rule-based phonetics, e.g. `a-go-rít`, `đa-ta-bê xơ-vơ` |
| `&`, `@`, `#` | `và`, `a còng`, `thăng` |

Phone numbers are read digit by digit; emojis, URLs, e-mails and non-Latin characters are removed; Unicode is normalized to NFC (**Reported**).[^vietnormalizer-readme] Output is lowercased.

## Pipeline order

The fixed order (matching `nghitts`) is: NFC → special characters/URL/e-mail → punctuation → text cleaning → year ranges → percentage ranges → date/time (with ranges) → ordinals → thousand-separator removal → currency → remaining percentages → phone numbers → decimals → measurement units → standalone numbers → lowercase → acronym CSV → non-Vietnamese word CSV → rule-based transliteration (**Reported**).[^vietnormalizer-readme] Because lowercasing precedes the dictionary steps, ordering matters when writing custom entries (**Synthesis**).

## API and configuration

- `VietnameseNormalizer(enable_transliteration=True, acronyms_path=, non_vietnamese_words_path=, data_dir=)`; `normalize(text, enable_transliteration=, enable_preprocessing=)`; `reload_dictionaries(...)` at runtime.[^vietnormalizer-readme]
- `enable_transliteration=False` keeps dictionary replacements only and leaves unknown words as-is; `enable_preprocessing=False` skips number/date conversion.[^vietnormalizer-readme]
- Helpers: `is_vietnamese_word`, `transliterate_word` (skips words detected as Vietnamese), `english_to_vietnamese` (always transliterates), `VietnameseTextProcessor.number_to_words` and `process_vietnamese_text` (no dictionary steps).[^vietnormalizer-readme]
- Dictionaries are CSVs: `acronyms.csv` (`acronym,transliteration`) and `non-vietnamese-words.csv` (`original,transliteration`); a built-in set of 17K+ entries ships with the package.[^vietnormalizer-readme]

## Performance and fit

README states ~0.6 ms per call with 17K+ entries, ~40 ms initialization, pre-compiled regexes and O(1) hash lookups (**Reported**, no hardware or protocol given).[^vietnormalizer-readme] That is negligible beside TTS first-audio latency, so it suits a per-clause step in the chunker → normalizer → TTS stage (**Synthesis**). Pair it with a TTS-specific lexicon: transliterated English is a convention of this library, not of each TTS model (see [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md), which handles some code-switch itself).

## Contradictions

- The README's `transliterate_word("database")` comment gives `đa-ta-bâi`, while the quick start shows `database` → `đa-ta-bê` inside a sentence; the cause (different code paths or a stale comment) is not stated.[^vietnormalizer-readme]
- The README comment for `is_vietnamese_word("database")` says "contains 'b' ending", yet the rule set is not documented; the detection heuristic cannot be assessed from the capture.[^vietnormalizer-readme]

## Coverage and limits

- Inspected statically: only the single README capture `raw/vietnormalizer.md`; no revision, version number or upstream commit is recorded (**Observed**).[^vietnormalizer-readme]
- Not inspected: package source, built-in CSV dictionaries, tests, `docs/publish-to-pypi.md`, `CONTRIBUTING.md`, the `nghitts` upstream and the GitHub repository `nghimestudio/vietnormalizer`. No install or execution; example outputs, speed and correctness (ambiguous dates, regional number readings, sentence-level foreign-word choices) are unreproduced.
- Not stated: pronunciation correctness against any specific TTS, streaming/chunk-boundary behavior, thread safety, handling of proper names. `stale_after` follows the `tts` domain rule.

## Relationships

- Fills the normalizer step in [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md) and [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) (**Synthesis**).
- Candidate preprocessing for [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) and [Kokoro Vietnamese](kokoro-vietnamese.md) inputs (**Synthesis**, untested).

[^vietnormalizer-readme]: [Vietnamese Text Normalizer README](../raw/vietnormalizer.md) — locators: `## Features`; `## Installation`; `## Quick Start`; `## Transliteration Control`; `## Vietnamese Word Detection`; `## Direct Transliteration`; `## Custom Dictionaries` (CSV Formats); `## Advanced Usage`; `## Processing Pipeline` (19 steps); `## Performance`; `## Requirements`; `## License` (MIT); `## Acknowledgments` (ported from nghitts).
