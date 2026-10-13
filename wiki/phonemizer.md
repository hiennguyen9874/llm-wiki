---
type: Concept
title: Phonemizer
description: Python package and phonemize CLI for text-to-phones transcription across many languages through four user-chosen backends (espeak, espeak-mbrola, festival, segments), with JOSS citation and GPL-3.0-or-later licensing.
tags: [tts, g2p, phonemization, phonemizer, gpl-3.0, open-source]
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

Phonemizer converts words and texts in many languages into phonetic transcriptions. It exposes a `phonemize` command-line tool and a `phonemizer.phonemize` Python function, and it is built on four backends that the user chooses: espeak, espeak-mbrola, festival, and segments (**Reported**).[^phonemizer-readme] The backend sets the phone set, language coverage, and token granularity, so it is the main decision; the comparison is in [Phonemizer Backends](phonemizer-backends.md). The capture is the README only, so function signatures, options, and install steps are not established here.

## Identity and provenance

- **Name and upstream:** `phonemizer`, developed in the `bootphon/phonemizer` GitHub repository. The README's badge and documentation links point there, the package is published on PyPI, and the documentation is at `bootphon.github.io/phonemizer` (**Observed** from the links).[^phonemizer-readme]
- **Authors and copyright:** the BibTeX entry names Mathieu Bernard and Hadrien Titeux, and the license notice reads "Copyright 2015-2021 Mathieu Bernard" (**Reported**).[^phonemizer-readme]
- **Revision:** none recorded. The release badges track the latest release, and the `v1.0` tag link is defined but not used in the text (**Observed**). The capture has no version or date.

## Interfaces

- **Command line:** the `phonemize` tool. Its flags are not captured (**Unverified**).
- **Python:** `phonemizer.phonemize`. The README links a pinned `phonemize.py` (lines 33–156 at commit `c5e2f38`) but does not use the link in its text, and that file was not fetched.
- **Backend selection:** left to the caller. The README names no default backend and no automatic choice (**Reported**: "The backend choice is let to the user").[^phonemizer-readme]

## Licensing and citation

- **License:** GNU General Public License version 3 or later, per the license notice in the README (**Observed**). The `COPYING` file was not captured.
- **Consequence:** a deployment that bundles or links phonemizer takes on GPL-3.0-or-later terms for this package. The wiki has not evaluated what that means for a product, which matches the treatment of [eSpeak NG](espeak-ng.md) (**Synthesis**).
- **Citation:** the README asks users to cite the JOSS paper (DOI `10.21105/joss.03958`; JOSS volume 6, issue 68, pages 3958, 2021). Its badge also gives Zenodo DOI `10.5281/zenodo.1045825` (**Reported**).[^phonemizer-readme]

## Relationships

- **Uses:** [eSpeak NG](espeak-ng.md) as the engine behind the espeak backend (**Synthesis** from the README's link; see [Phonemizer Backends](phonemizer-backends.md)).

The wiki's [Misaki](misaki.md) page records an install of `phonemizer-fork`. This README names no fork, so the relationship between the two packages is not established (**Synthesis**).

## Coverage and limits

- **Inspected statically:** the whole README capture, including the badge table, introduction, backend list, comparison table, citation, license notice, and link definitions (**Observed**).[^phonemizer-readme]
- **Not captured:** the documentation site, the source code (including the pinned `phonemize.py`), the tests and CI workflows behind the badges, the JOSS paper, the `COPYING` file, and the language lists and phoneset pages linked from the backend table.
- **Not executed:** nothing was installed, run, or phonemized, so the speed labels and language counts are reported, not measured (**Unverified**).
- **Not established:** whether Vietnamese is supported by any backend. The linked eSpeak NG language list would settle this for the espeak backend.
- **Excluded as decorative:** the title's pronunciation respelling and the badge images.
- **Sensitive values:** none. The capture holds public links and bibliographic data only.

[^phonemizer-readme]: [Phonemizer README capture](../raw/phonemizer.md) — locators: header badge table (Tests, Documentation, Release, and Citation rows); title and introduction bullets (purpose, `phonemize` and `phonemizer.phonemize`, four backends, backend choice); `## Citation` (BibTeX entry); `## Licence`; link reference definitions `[phonemizer-1.0]` and `[phonemize-function]`. The capture records no version or date.
