---
type: Concept
title: Kokoro Python Library
description: Python kokoro inference library for Kokoro-82M: KPipeline setup, lang_code and voice selection, per-segment grapheme, phoneme, and 24 kHz audio outputs, misaki and espeak-ng G2P roles, and per-platform install notes.
tags: [tts, kokoro, python, misaki, espeak-ng]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:58:00Z }
stale_after: 2027-04-13
sources:
  - id: kokoro-library-readme
    resource: ../raw/kokoro.md
    kind: documentation
    title: kokoro library README capture
  - id: kokoro-82m-card
    resource: ../raw/Kokoro-82M.md
    kind: documentation
    title: Kokoro-82M model card capture
---

The `kokoro` package is the Python inference library for [Kokoro-82M](kokoro-82m.md). It installs from PyPI, exposes a `KPipeline` object that turns text into a generator of audio segments at 24 kHz, and hands grapheme-to-phoneme (G2P) work to `misaki`, with `espeak-ng` as a fallback for out-of-dictionary words and some non-English languages. The README gives one basic and one advanced cell, both written for Google Colab. This concept is based on static reading only; nothing was installed or run (**Reported**; **Observed** from code).[^kokoro-library-readme]

## Identity and provenance

- **Package:** `kokoro` on PyPI, linked from the README's first line. The README names Kokoro-82M as the model it runs (**Reported**).[^kokoro-library-readme]
- **Repository:** the capture has no URL to its own repository. The model card links the GitHub repository `hexgrad/kokoro` (**Reported**).[^kokoro-82m-card] Only the README was captured, so source, tests, and release history are not covered.
- **Revision:** none recorded. The version pins in the README are the only version evidence (see [Contradictions](#contradictions)).
- **License:** the README states no license for the library code. The card's Apache-2.0 statement covers the model weights (**Reported**); it does not establish the library's license (**Unverified**).[^kokoro-82m-card]
- **Dependencies named:** `misaki` (G2P, linked to `hexgrad/misaki`), `soundfile` for WAV output, `torch` in the examples, and the system package `espeak-ng` (**Reported**).[^kokoro-library-readme] `misaki` is compiled as [Misaki](misaki.md).

## Install

- Both cells run `pip install kokoro>=0.9.4 soundfile` and `apt-get install espeak-ng` (lines 10–11 and 32–34).
- **Shell-quoting defect:** the requirement `kokoro>=0.9.4` is unquoted. In a POSIX shell `>` is a redirect, so pip receives `kokoro soundfile`, the `>=0.9.4` floor is dropped, and a stray file named `=0.9.4` is written to the working directory. I reproduced the parsing with `sh -c` and `bash -c` on the same token in a temporary directory; pip was not run (**Reproduced** for shell parsing). IPython `!` cells and terminal commands pass through a shell, so the same parsing applies on Colab (**Synthesis**). Quoting the requirement as `"kokoro>=0.9.4"` avoids the redirect (**Synthesis**).
- **Windows:** install `espeak-ng` from the upstream release page using the `.msi` installer. The example file name, `espeak-ng-20191129-…-x64.msi`, is a 2019 build, so choose the current release (lines 89–95).
- **Conda sample:** `environment.yml` pins Python 3.9, `kokoro>=0.3.1`, `misaki[en]`, and `libstdcxx~=12.4.0`. The README marks the `libstdcxx` pin as needed to load espeak correctly and says to remove it if espeak fallback fails (lines 106–119).
- **Apple Silicon:** the README says to set `PYTORCH_ENABLE_MPS_FALLBACK=1` to "enable GPU acceleration" (lines 98–103; **Reported**). It does not show a device argument, so which device the pipeline uses, and whether the variable changes it, is not established.

## Pipeline API

- `KPipeline(lang_code=...)` builds the pipeline. The README comment says the `lang_code` must match the voice (line 49).
- `pipeline(text, voice='af_heart', speed=1, split_pattern=r'\n+')` returns a generator. Each item is a `(gs, ps, audio)` tuple, which the example prints as index, graphemes, and phonemes (lines 70–86). The README does not define the tuple, so the meaning of `gs` and `ps` is **Observed** from the code only.
- Both examples write audio at 24,000 Hz, one WAV file per yielded segment (lines 24 and 86).
- `split_pattern` is a regex for segment boundaries. The advanced cell splits on newlines (`\n+`). The README gives no default.
- `voice` takes a voice name such as `af_heart`. The commented alternative passes a tensor loaded with `torch.load(..., weights_only=True)` (lines 75–79). Voice names are not listed in this README; the card links `VOICES.md`, which was not captured.
- Inline phoneme override: both samples set the pronunciation of the word Kokoro with a bracketed word followed by a parenthesized, slash-delimited IPA string, `[Kokoro]` plus `(/kˈOkəɹO/)` (lines 18 and 59). The README does not document this syntax (**Observed** usage; semantics **Synthesis**). The server wrapper has its own markup layer, covered in [Kokoro-FastAPI Voice and Markup Controls](kokoro-fastapi-voice-and-markup.md). This README does not say whether the two syntaxes match (**Synthesis**).

## Languages and G2P

The README lists nine `lang_code` values. Counting American and British English once, they cover eight languages.

| `lang_code` | Language (README) | Extra install (README) | Sample text in README |
| --- | --- | --- | --- |
| `a` | American English | none stated | basic and advanced cells (lines 17–19, 52–59) |
| `b` | British English | none stated | none |
| `e` | Spanish (`es`) | none stated | commented (line 63) |
| `f` | French (`fr-fr`) | none stated | commented (line 64) |
| `h` | Hindi (`hi`) | none stated | commented (line 65) |
| `i` | Italian (`it`) | none stated | commented (line 66) |
| `j` | Japanese | `pip install misaki[ja]` (line 46) | commented (line 61) |
| `p` | Brazilian Portuguese (`pt-br`) | none stated | commented (line 67) |
| `z` | Mandarin Chinese | `pip install misaki[zh]` (line 48) | commented (line 62) |

- **Vietnamese is absent.** No `lang_code`, sample, or install note covers it (**Observed** absence). Vietnamese Kokoro is a separate fine-tuned artifact set, [Kokoro Vietnamese](kokoro-vietnamese.md), which that concept says uses its own `vig2p` G2P. This README offers no Vietnamese path (**Synthesis**).
- **Eight languages across nine codes** matches the card's v1.0 "8" language count (**Synthesis**). It does not resolve the card's `en`-only frontmatter conflict, which is recorded in [Kokoro-82M](kokoro-82m.md#contradictions).
- **G2P roles:** [`misaki`](misaki.md) performs the grapheme-to-phoneme step "under the hood" (line 26). `espeak-ng` is the fallback for English out-of-dictionary words and some non-English languages (line 33 comment). The README does not list which languages use which path. Engine details are in [eSpeak NG](espeak-ng.md).

## Relationships

- Runs [Kokoro-82M](kokoro-82m.md), the model whose weights it loads (**Reported**).[^kokoro-library-readme]
- Depends on [Misaki](misaki.md) for G2P and on the system `espeak-ng`, described in [eSpeak NG](espeak-ng.md).
- [Kokoro-FastAPI](kokoro-fastapi.md) serves the same model over HTTP. This concept covers only the library, not the server (**Synthesis**).
- [Kokoro Vietnamese](kokoro-vietnamese.md) is a Vietnamese fine-tuned artifact set. This README gives no shared-code or shared-checkpoint link (**Synthesis**).

## Contradictions

- **Install version floor:** the model card's usage cell says `kokoro>=0.9.2`, the library README's two cells say `kokoro>=0.9.4`, and the sample conda file says `kokoro>=0.3.1` with Python 3.9. Neither floor is chosen here; the newest appears in the README cells (**Reported**).[^kokoro-82m-card][^kokoro-library-readme]

## Coverage and limits

- **Inspected statically:** the whole README capture (129 lines): both usage cells, the `lang_code` comments and commented samples, the Windows, Apple Silicon, and conda sections, and the acknowledgements (**Observed**).
- **Not executed:** no `pip install`, model download, import, or synthesis. The only execution was the shell-parsing check described under Install (**Reproduced**, shell parsing only).
- **Not captured:** the upstream `hexgrad/kokoro` repository (source, tests, packaging metadata, release notes, revision); `hexgrad/misaki` source (its README is compiled as [Misaki](misaki.md)); `SAMPLES.md` and `VOICES.md`; the Colab notebooks; and the PyPI page.
- **Excluded as decorative or non-durable:** the sample narrative passages used as demo input, the Discord invite, the acknowledgement list except the StyleTTS 2 credit, and the closing trivia about the name Kokoro.
- **Sensitive values:** none in the capture. The Discord invite was omitted.
- **Freshness:** the capture has no date. `stale_after` is set six months after this ingest because install pins and API details track library releases.

[^kokoro-library-readme]: [kokoro library README capture](../raw/kokoro.md) — locators: line 3 package description and PyPI link; lines 10–11 and 32–34 install commands; lines 16–24 basic pipeline cell (`KPipeline`, `voice='af_heart'`, 24000 Hz write); line 26 misaki note; lines 36–49 advanced setup, espeak comment (line 33), and `lang_code` comments (lines 41–48); lines 61–67 commented sample texts; lines 69–86 generator loop with `split_pattern=r'\n+'`; lines 75–79 voice-tensor alternative; lines 89–95 Windows install; lines 98–103 Apple Silicon note; lines 106–119 conda environment; lines 121–123 acknowledgements.
[^kokoro-82m-card]: [Kokoro-82M model card capture](../raw/Kokoro-82M.md) — locators: frontmatter (`license: apache-2.0`); opening paragraph (Kokoro-82M description); `### Usage` code block (`kokoro>=0.9.2`, `espeak-ng`); `### Releases` table (v1.0 row: 8 languages, 54 voices); `### Model Facts` (`Languages: Multiple`); line 13 GitHub link (`hexgrad/kokoro`).
