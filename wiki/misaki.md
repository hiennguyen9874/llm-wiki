---
type: Concept
title: Misaki
description: "Misaki G2P engine for Kokoro models: English usage with optional espeak-ng fallback, the bracket-and-slash phoneme override shown in its example, install extras, and roadmap items the README leaves unchecked, including homograph disambiguation."
tags: [tts, g2p, kokoro, misaki, phonemes, espeak-ng]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-21T15:12:59Z }
stale_after: 2027-04-13
sources:
  - id: paradee-card
    resource: ../raw/Paradee-8M-v1.0.md
    kind: documentation
    title: Paradee-8M v1.0 model card capture
  - id: misaki-readme
    resource: ../raw/misaki.md
    kind: documentation
    title: misaki README capture
---

Misaki is the grapheme-to-phoneme (G2P) engine that its README describes as "designed for Kokoro models" (**Reported**).[^misaki-readme] Its English path turns text into a phoneme string and a token list, and can back out-of-dictionary words with [eSpeak NG](espeak-ng.md). The capture is a README only. Nothing was installed, imported, or run, so the printed outputs are reported and not reproduced (**Observed** from static reading). Per-language text frontends are covered in [Misaki Language Frontends](misaki-language-frontends.md).

## Identity and provenance

- **Name and upstream:** `misaki`, developed in the `hexgrad/misaki` GitHub repository. The README also links a hosted Hugging Face Space demo, `hexgrad/Misaki-G2P` (line 4; **Reported**).[^misaki-readme]
- **Role:** the G2P package that [Kokoro Python Library](kokoro-python-library.md) hands its grapheme-to-phoneme step to (**Synthesis** from that concept, which cites its own README).
- **Revision:** none. The capture has no version number or date.
- **License:** not stated in the README, and the repository was not captured (**Unverified**).

## Install

- **English:** `pip install "misaki[en]"` (line 9). The `[en]` extra is the English path. [Kokoro Python Library](kokoro-python-library.md) uses `misaki[ja]` and `misaki[zh]` for Japanese and Chinese.
- **Espeak fallback:** the README installs system `espeak-ng` with apt on Colab and notes that espeak installation "varies across platforms" (lines 22–25). It then runs `pip install "misaki[en]" phonemizer-fork` (line 27). The README does not say how misaki uses `phonemizer-fork`. The base [Phonemizer](phonemizer.md) concept, which cites its own README, names no fork either, so the fork's identity stays open (**Synthesis**).
- **Per-language installs:** the TODO list marks per-language pip installs complete (line 80).

## English G2P usage

- **Constructor:** `en.G2P(trf=False, british=False, fallback=None)` (line 13). The inline comments read `trf=False` as "no transformer" and `british=False` as American English.
- **Fallback:** `espeak.EspeakFallback(british=False)`, commented as en-us, is passed as `fallback=` (lines 31, 33).
- **Call:** `phonemes, tokens = g2p(text)` (lines 17, 37). The README does not document the token structure.
- **Fallback path:** the second example's input says out-of-dictionary words "are handled by espeak" (line 35). The README does not say which words take the dictionary path and which take the fallback (**Synthesis**).

## Phoneme override syntax

The English example annotates two words with a bracketed word followed by a parenthesized, slash-delimited IPA string: `[Misaki]` then `(/misˈɑki/)`, and `[Kokoro]` then `(/kˈOkəɹO/)` (line 15). The printed output starts with `misˈɑki` and contains `kˈOkəɹO` (line 19), which matches the annotated pronunciations (**Reported**; from the printed comment, not executed).[^misaki-readme] The README does not document this as a feature, so its semantics are **Synthesis**. [Kokoro Python Library](kokoro-python-library.md) uses the same pattern in its own examples.

## Transformer path

- Both examples set `trf=False` (lines 13, 33).
- The homograph TODO says that, assuming `trf=True`, BERT contextual word embeddings can be read from `doc._.trf_data`, citing `misaki/en.py` line 479 in the upstream repository. That line is not captured (**Reported**).[^misaki-readme]

## Roadmap (unchecked TODOs)

The README leaves these items unchecked, so this page does not describe them as shipped (**Reported**; status **Synthesis**).[^misaki-readme]

- **Data:** compress the `misaki/data` dictionaries by dropping indented JSON, and remove redundancy between the gold and silver dictionaries (line 76).
- **Fallback models:** train seq2seq fallback models on the dictionaries, using a linked Kyubyong notebook as the template (line 77).
- **Homographs:** disambiguate hard words listed as `axes bass bow lead tear wind`, using BERT contextual embeddings and per-word logistic-regression models (`nn.Linear` followed by a sigmoid), following an Amazon paper. The README names WikipediaHomographData, llama-hd-dataset, and LLM-generated data as training sources (line 78).

Completed TODO items: more languages, with `ko.py`, `ja.py`, and `zh.py` added (line 79), and per-language pip installs (line 80).

## Relationships

- **Depended on by:** [Paradee-8M v1.0](paradee-8m-v1-0.md) requires misaki-compatible phoneme spelling, matching its teacher-generated training inputs. Its card links `web/misaki.js` to convert browser kokoro-js/eSpeak NG phonemes, reporting about 31% Whisper word errors without conversion versus about 2% with it. Judge version, sample count and protocol are not supplied; this is not an independent G2P evaluation (**Reported**). Code, weights and audio are uninspected; [Paradee's ledger](paradee-8m-v1-0.md#coverage-and-trust-limits) records the missing evidence.[^paradee-card]

- **Depended on by:** [Kokoro Python Library](kokoro-python-library.md) depends on misaki for G2P (**Reported** in that concept).
- **Depends on:** [eSpeak NG](espeak-ng.md) as an optional out-of-dictionary fallback, wired through `fallback=` (lines 22–39).[^misaki-readme]
- **Related:** [Misaki Language Frontends](misaki-language-frontends.md) holds the per-language tokenizer lineage. [Kokoro Vietnamese](kokoro-vietnamese.md) uses its own `vig2p` path for Vietnamese G2P (per that concept). The misaki README lists Viphoneme but no Vietnamese module, so this page asserts no link between them.

## Coverage and limits

- **Inspected statically:** all 88 lines of the README capture, including both code cells, the language sections, the TODO list, and the acknowledgements (**Observed**).
- **Not executed:** no install, import, model load, or G2P call. Printed outputs are reported only.
- **Not captured:** the `hexgrad/misaki` repository (`misaki/en.py`, `misaki/espeak.py`, `misaki/data`, `EN_PHONES.md`, tests, license, and release history); the hosted demo; and the upstream projects the README links (see [Misaki Language Frontends](misaki-language-frontends.md)).
- **Excluded as decorative or non-durable:** the acknowledgement prose, the Discord invite, and the closing note on the name and the character image.
- **Sensitive values:** none. The Discord invite was omitted.
- **Freshness:** `stale_after` is six months after this ingest, because install commands and G2P behavior follow library releases. The capture has no date, so no release was checked.

[^paradee-card]: [Paradee-8M v1.0 card](../raw/Paradee-8M-v1.0.md) — Files, paragraphs after ONNX Inputs/Output (`misaki`, kokoro-js/eSpeak NG, `web/misaki.js`, about 31% versus 2%); How it was made (teacher-generated training data).
[^misaki-readme]: [misaki README capture](../raw/misaki.md) — locators: line 2 description; line 4 hosted demo; lines 6–20 English usage cell (line 9 install, line 13 constructor and comments, lines 15–19 example input and printed output); lines 22–40 espeak fallback (lines 24–25 install, line 27 `phonemizer-fork`, line 31 `EspeakFallback`, line 35 input, line 39 printed output); lines 42–45 English links; lines 47–56 Japanese; lines 58–61 Korean; lines 63–70 Chinese; lines 72–73 Vietnamese; lines 75–80 TODO list; lines 82–88 acknowledgements.
