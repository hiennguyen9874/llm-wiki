---
type: Concept
title: eSpeak NG
description: Compact open-source C formant-synthesis TTS engine for 100+ claimed languages, with CLI, shared-library, and SAPI5 builds, text-to-phoneme output usable as a front end, and GPL-3.0-or-later licensing.
tags: [tts, formant-synthesis, g2p, phonemizer, gpl-3.0, open-source]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:53:00Z }
stale_after: 2027-10-13
sources:
  - id: espeak-ng-readme
    resource: ../raw/espeak-ng.md
    kind: documentation
    title: eSpeak NG README capture
---

eSpeak NG is a compact, open-source text-to-speech synthesizer written in C for Linux, Windows, Android, and other systems. It is based on Jonathan Duddington's eSpeak engine and uses formant synthesis, which keeps language data small and speech clear at high rates but less natural than synthesizers built on human recordings. It can also emit phoneme codes with pitch and length, so other engines can use it as a front end. The README claims more than 100 languages and accents, but the capture does not list them, so Vietnamese coverage is unestablished. Claims below are **Reported** unless marked otherwise.[^espeak-ng-readme]

## Synthesis method and output

- **Formant synthesis:** the README describes a small, clear, fast-speaking voice that is less natural and smooth than recording-based systems (**Reported**).[^espeak-ng-readme]
- **Klatt and MBROLA:** the engine also supports Klatt formant synthesis and can use MBROLA as its backend speech synthesizer (**Reported**).[^espeak-ng-readme]
- **Output and markup:** speech can be written to a WAV file and voice characteristics can be altered. SSML support is described as incomplete, and HTML input is also accepted (**Reported**).[^espeak-ng-readme]
- **Phoneme output:** text can be translated into phoneme codes, so the engine "could be adapted as a front end for another speech synthesis engine" (**Reported**).[^espeak-ng-readme]
- **Footprint:** the program and data for many languages total a few megabytes (**Reported**). No measurement was made here.

## Interfaces and platforms

- **Command line:** `espeak-ng` speaks text from a file or stdin on Linux and Windows (**Reported**).[^espeak-ng-readme]
- **Shared library:** a library for other programs, built as a DLL on Windows. The C API is covered in [eSpeak NG Lineage and espeak Compatibility](espeak-ng-lineage-and-compatibility.md) (**Reported**).[^espeak-ng-readme]
- **SAPI5:** a Windows SAPI5 build serves screen readers and other SAPI5 clients (**Reported**).[^espeak-ng-readme] A third-party SAPI 5 engine, `espeak-ng-sapi`, is listed separately (**Reported**).[^espeak-ng-readme]
- **Platforms:** the table lists Linux (with a CI badge), BSD, Android (minimum 4.0), Windows (minimum Windows 8), and Mac. Three rows have blank minimums. The README also says the project has been ported to Solaris and Mac OS X (**Reported**).[^espeak-ng-readme] Per-platform status is unverified.

## Licensing

- The project is released under GPL version 3 or later. Its Windows `getopt.c` comes from NetBSD under a 2-clause BSD license (**Reported**).[^espeak-ng-readme]
- **Synthesis:** a product that bundles or links eSpeak NG takes on GPL-3.0-or-later terms. [sanoTTS](sanotts.md) reports that its GPLv3 stack builds on espeak-ng, so the copyleft consequences belong in any deployment decision. The wiki has not evaluated them, and the license text was not captured.

## Downstream use in this wiki

These links are **Synthesis** from the linked pages, which cite their own sources:

- [Kokoro-82M](kokoro-82m.md) names `espeak-ng` as a system dependency on its usage path.
- [Kokoro-FastAPI](kokoro-fastapi.md) installs it as an optional fallback for unknown words.
- [sanoTTS](sanotts.md) includes an espeak-ng phonemizer and converts text to espeak-ng phoneme IDs.
- [Phonemizer](phonemizer-backends.md) names eSpeak NG as the engine of its `espeak` backend, linked from its README.
- [Misaki](misaki.md) names `espeak-ng` as the optional fallback for out-of-dictionary English words, via `espeak.EspeakFallback`.

## Relationships

- **Uses:** MBROLA diphone voices as an optional backend (**Reported**; MBROLA has no concept in this wiki).[^espeak-ng-readme]

## Retrieval notes

- **Vietnamese is open (Synthesis).** The README names no language list, and the linked `docs/languages.md` was not captured. Check that list before relying on eSpeak NG for Vietnamese text.
- **Role (Synthesis).** This is a formant synthesizer and a phoneme front end, not a neural voice. Speed and quality figures are absent from this capture, so any latency or naturalness comparison with neural models in the [TTS Model Survey](tts-model-survey.md) needs separate measurement.
- **Edge fit (Synthesis).** The claimed few-megabyte footprint and the CLI, library, and SAPI5 surfaces suggest fit for offline, embedded, or fallback use. This is an inference from the claim, not a tested result.

## Coverage and limits

- **Inspected statically:** the whole capture `raw/espeak-ng.md`, including the introduction, features, platform table, documentation, compatibility, related projects, history, license, and acknowledgements (**Observed**).[^espeak-ng-readme]
- **Not captured:** the linked `docs/languages.md`, `docs/integration.md`, `docs/mbrola.md`, `docs/guide.md`, `docs/building.md`, `docs/index.md`, and `docs/contributing.md`; `ChangeLog.md`, `src/espeak-ng.1.ronn`, `COPYING`, and `COPYING.BSD2`; the external roadmap; and the `espeak-ng-sapi` repository. The language list, CLI flags, build steps, and license text are therefore unverified.
- **Not executed:** nothing was installed, built, or synthesized, so no audio, phoneme, or platform claim is reproduced.
- **Revision:** none recorded. The capture has no version, release, or date. The upstream repository is inferred from the CI badge link to `github.com/espeak-ng/espeak-ng` (**Observed**).
- **Excluded as boilerplate:** the table of contents, the CI badge image, and the Android trademark line. Funding and history details are kept in the lineage concept.
- **Sensitive values:** none. The capture contains public links only.

[^espeak-ng-readme]: [eSpeak NG README capture](../raw/espeak-ng.md) — locators: title and introduction (formant synthesis, languages, platform table); `## Features`; `## Documentation`; `## eSpeak Compatibility`; `## Related projects`; `## History`; `## License Information`; `## Acknowledgements`. The capture records no version, date, or revision.
