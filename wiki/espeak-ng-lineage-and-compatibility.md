---
type: Concept
title: eSpeak NG Lineage and espeak Compatibility
description: "History from the 1995 RISC OS speak program through eSpeak to the 2015 eSpeak NG fork, and what eSpeak NG keeps or breaks for espeak users: CLI options, the espeak 1.48.15 C API, renamed data, and the removed espeakedit tool."
tags: [tts, espeak, compatibility, history, c-api]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:34:17Z }
stale_after: 2027-10-13
sources:
  - id: espeak-ng-readme
    resource: ../raw/espeak-ng.md
    kind: documentation
    title: eSpeak NG README capture
---

eSpeak NG is a 2015 fork of the eSpeak line rather than a rewrite. This page expands [eSpeak NG](espeak-ng.md). It keeps espeak's command-line options and its speech C API, which the README gives as the espeak 1.48.15 API and says is API and ABI compatible. It renames the data package, and it changes the voice, dictionary, and phoneme files, which the README calls incompatible with espeak. The README gives no support for mixing eSpeak NG binaries with espeak data, or the reverse. That reading is **Synthesis**; the compatibility claims are **Reported**.[^espeak-ng-readme]

## History

- **1995 origin:** written for Acorn/RISC OS computers as *speak*, starting in 1995, by Jonathan Duddington (**Reported**).[^espeak-ng-readme]
- **2007 eSpeak:** enhanced and rewritten as *eSpeak*, relaxing the original memory and processing limits and adding languages (**Reported**).[^espeak-ng-readme]
- **2010 to 2012 POSIX work:** Reece H. Dunn began maintaining a GitHub version in 2010 to ease POSIX builds, and moved the build to autotools in 2012 (**Reported**).[^espeak-ng-readme]
- **Late 2015 fork:** the project was officially forked as eSpeak NG to clean up the codebase, add features, and extend the languages. The README calls it a "significant departure" from eSpeak (**Reported**).[^espeak-ng-readme]
- **Historical branch:** it holds older eSpeak releases that are absent from the Subversion repository. Release 1.24.02 is the first in that repository, and releases 1.05 to 1.24 are on SourceForge (**Reported**).[^espeak-ng-readme] The README suggests `git replace 8d59235f 63c1c019` to view earlier history. This capture did not run it (not executed).
- **Funding note:** the Catalan extension was funded by the Generalitat de Catalunya (Departament de la Vicepresidència i de Polítiques Digitals i Territori) within Projecte AINA (**Reported**).[^espeak-ng-readme]

## Compatibility with espeak

The README's compatibility claims are summarized below.[^espeak-ng-readme]

| Surface | eSpeak NG behavior | Evidence |
| --- | --- | --- |
| Command line | Same options as `espeak`, plus additions such as naming the output audio device | Reported |
| Program names | The build creates symlinks `espeak` to `espeak-ng` and `speak` to `speak-ng` | Reported |
| C header | `speak_lib.h` sits at `espeak-ng/speak_lib.h`, with an optional `espeak/speak_lib.h` symlink. It carries the espeak 1.48.15 API, an `ESPEAK_API` macro change for Windows, and doc-comment edits | Reported |
| C ABI | Described as API and ABI compatible with espeak | Reported; not tested |
| Data | `espeak-data` is renamed `espeak-ng-data`. Voice, dictionary, and phoneme files changed and are incompatible with espeak | Reported |
| Tooling | `espeakedit` is not included. Dictionary, phoneme, and intonation build logic moved into `libespeak-ng.so`, reachable from the CLI and the C API | Reported |

- **Synthesis:** by the README's account, code written against espeak's `speak_lib.h` should build against the eSpeak NG header, with the data directory moved to `espeak-ng-data`. That is a reading of the claims, not a tested build.

## Related projects

- `espeak-ng-sapi` is a third-party Windows SAPI 5 engine implementation for eSpeak NG from the gozaltech project (**Reported**).[^espeak-ng-readme]

## Coverage and limits

- **Inspected statically:** the README's history, compatibility, related-projects, and acknowledgements sections (**Observed**).[^espeak-ng-readme]
- **Not verified:** the API and ABI claim, which needs a compile and link check against espeak's own headers; the 1.48.15 header version against upstream espeak; the `git replace` history, which needs the upstream repository and was not run; and the third-party SAPI engine.
- **Not captured:** `ChangeLog.md`, the `docs/` pages, the historical branch, and the upstream repository.
- **Revision:** none recorded. The capture has no version, release, or date beyond the historical dates in its text.

[^espeak-ng-readme]: [eSpeak NG README capture](../raw/espeak-ng.md) — locators: title and introduction; `## Features`; `## Documentation`; `## eSpeak Compatibility` (CLI options, symlinks, `speak_lib.h` and its 1.48.15 API, `espeak-data` rename, `espeakedit` removal); `## Related projects`; `## History` (1995 speak origin, 2007 eSpeak, 2010 and 2012 maintenance, late-2015 fork, historical branch and `git replace` note, Catalan funding); `## License Information`; `## Acknowledgements`. The capture records no version, date, or revision.
