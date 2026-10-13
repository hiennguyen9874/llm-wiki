---
type: Concept
title: Phonemizer Backends
description: Comparison of the four phonemizer backends (espeak, espeak-mbrola, festival, segments) by phone set, language coverage, speed label, and token, punctuation, stress, and tie support.
tags: [tts, g2p, phonemization, phonemizer, ipa, sampa, espeak-ng, mbrola, festival, segments]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:52:00Z }
stale_after: 2027-04-13
sources:
  - id: phonemizer-readme
    resource: ../raw/phonemizer.md
    kind: documentation
    title: Phonemizer README capture
---

The backend determines what a [Phonemizer](phonemizer.md) run returns. The README compares its four backends in one table. espeak is the only backend marked for IPA output, stressed phones, and tie marks. espeak-mbrola is the only one marked for neither word tokens nor punctuation. Both points are **Reported** from the table and **Synthesis** as a summary.[^phonemizer-readme]

## Comparison

| Property | espeak | espeak-mbrola | festival | segments |
| --- | --- | --- | --- | --- |
| Phone set | IPA | SAMPA | Custom festival phoneset | User-defined |
| Supported languages | 100+ (claimed) | 35 (claimed) | US English only | User-defined |
| Processing speed (label) | fast | slow | very slow | fast |
| Phone tokens | yes | yes | yes | yes |
| Syllable tokens | no | no | yes | no |
| Word tokens | yes | no | yes | yes |
| Punctuation preserved | yes | no | yes | yes |
| Stressed phones | yes | no | no | no |
| Tie marks | yes | no | no | no |

Source: the comparison table under the backend list (**Reported**).[^phonemizer-readme]

## Backends

- **espeak:** the README links the name `espeak-ng` to the eSpeak NG project, which it describes as supporting many languages and IPA output. The wiki treats eSpeak NG as the engine behind this backend (**Synthesis** from the link). See [eSpeak NG](espeak-ng.md).
- **espeak-mbrola:** uses SAMPA instead of IPA and does not preserve word boundaries. The bullet links eSpeak NG's MBROLA documentation, so this backend runs through the eSpeak NG family (**Synthesis**). The bullet calls it `espeak-ng-mbrola` and the table calls it `espeak-mbrola`; this page treats them as one backend.
- **festival:** a Festival text-to-speech engine whose phonemizer backend supports only American English. It uses a custom phoneset, linked to the Festival phoneset reference, and allows tokenization at the syllable level (**Reported**).[^phonemizer-readme]
- **segments:** a Unicode tokenizer that builds phonemization from a grapheme-to-phoneme mapping file the user supplies, linked to the cldf/segments project (**Reported**).[^phonemizer-readme]

## Use notes for voice pipelines

- **espeak fits IPA output that must stay aligned to words (Synthesis).** The word-token, punctuation, stress, and tie columns favor espeak when phonemes must map back to words or keep punctuation for prosody. Whether a TTS model expects IPA or SAMPA is a model fact that this page does not cover.
- **espeak-mbrola fits SAMPA-based MBROLA voices (Synthesis).** Its SAMPA output and missing word boundaries mean word-level alignment has to come from another step.
- **festival is a poor fit for multilingual or low-latency loops (Synthesis).** It covers US English only and carries the README's "very slow" label.
- **segments trades effort for coverage (Synthesis).** It can handle the languages and phone sets the user maps, but the mapping file is the user's work.
- **Speed labels are ordinal, not measured (Unverified).** A latency budget needs a local benchmark before a backend is chosen.

## Relationships

- **Uses:** [eSpeak NG](espeak-ng.md) for the espeak backend, and eSpeak NG's MBROLA mode for espeak-mbrola (**Synthesis** from the README's links; the eSpeak NG page cites its own README).

## Coverage and limits

- **Inspected statically:** the backend list, the comparison table, and the link definitions for the language lists, the Festival phoneset, and the MBROLA voices (**Observed**).[^phonemizer-readme]
- **Not captured:** the linked eSpeak NG language list (`docs/languages.md`), the MBROLA voices list, the Festival phoneset page, the segments project and its mapping-file format, and the phonemizer documentation site.
- **Not established:** per-language coverage for each backend, including Vietnamese. The 100+ and 35 language counts are claimed, with no date.
- **Not measured:** the speed labels. Nothing was installed or executed.
- **Naming:** the MBROLA backend has two names in the README, as noted above; the README does not reconcile them.
- **Sensitive values:** none.

[^phonemizer-readme]: [Phonemizer README capture](../raw/phonemizer.md) — locators: title and introduction (backend list); backend bullets for `espeak-ng`, `espeak-ng-mbrola`, `festival`, and `segments`; the comparison table under the backend bullets (rows: phone set, supported languages, processing speed, and phone, syllable, word, punctuation, stressed, and tie tokens); link reference definitions `[espeak-languages]`, `[mbrola-languages]`, `[festival-phoneset]`, and `[tie-IPA]`. The capture records no version or date.
