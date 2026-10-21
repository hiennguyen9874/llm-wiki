---
type: Concept
title: Misaki Language Frontends
description: "Per-language text frontends in the misaki G2P engine: Japanese and Chinese tokenizer generations, the copied Korean tokenizer, English dependencies, and a Vietnamese credit that does not establish a misaki Vietnamese module."
tags: [tts, g2p, misaki, japanese, chinese, korean, tokenizer]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:55:00Z }
stale_after: 2027-04-13
sources:
  - id: misaki-readme
    resource: ../raw/misaki.md
    kind: documentation
    title: misaki README capture
---

[Misaki](misaki.md) runs language-specific text processing before phoneme lookup. Its README describes two generations of Japanese and Chinese tokenizers, a copied Korean tokenizer, and English dependencies on spaCy and num2words (**Reported**).[^misaki-readme] The README calls the second generation of the Japanese and Chinese paths current. Upstream code was not read or run, so these are the README's claims and not verified behavior (**Unverified**).

## English

- **Dependencies:** spaCy and num2words are linked under the English heading without a stated role (lines 43–44; **Reported**).[^misaki-readme]
- **Phoneme reference:** a repository file, `EN_PHONES.md`, is linked (line 45). Its content was not captured.

## Japanese

| Generation | Stack per README | Claimed change | Lines |
| --- | --- | --- | --- |
| Second | `pyopenjtalk` with full `unidic` | pitch accent marks and improved phrase merging | 48–50 |
| First | `cutlet` → `fugashi` → `mecab` → `unidic-lite`, each a wrapper around the next | none stated | 52–56 |

- The second generation "now uses" `pyopenjtalk` (line 48). The README does not say whether first-generation code still ships, so the replacement is read as the current path, not as a removal (**Synthesis**).
- `jaconv` and `mojimoji` are linked (lines 55–56) without a stated role.
- Pitch-accent support is credited to a named contributor's advice (line 48). The README gives no accuracy measurement.

## Chinese

| Generation | Stack per README | Claimed change | Lines |
| --- | --- | --- | --- |
| Second | adapts logic from the PaddleSpeech frontend; Jieba cuts and tags | pinyin-to-IPA "is no longer used" | 64–65 |
| First | Jieba to cut, `pypinyin`, `pinyin-to-ipa` | none stated | 67–70 |

- The second generation drops the pinyin-to-IPA step (line 64). The README gives no accuracy comparison between generations.

## Korean

- The tokenizer is "copied from" 5Hyeons's g2pkc fork of Kyubyong's g2pK (line 59; links on lines 60–61).[^misaki-readme]
- Because the code is copied rather than reimplemented, the upstream license governs reuse. The README states no license for the copied code, and the upstream licenses were not captured (**Unverified**).

## Vietnamese

- The README has a Vietnamese heading with one link, to `v-nhandt21/Viphoneme` (line 73). It names no module, install step, or code path.
- The TODO list records `ko.py`, `ja.py`, and `zh.py` as added (line 79) and names no Vietnamese module. The README therefore does not establish a misaki Vietnamese frontend (**Observed** absence; the inference is **Synthesis**).
- [Kokoro Vietnamese](kokoro-vietnamese.md) uses a separate `vig2p` path for Vietnamese G2P (per that concept). The misaki README does not connect Viphoneme and `vig2p`, so this page asserts no link between them.

## Relationships

- **Part of:** the per-language layer of [Misaki](misaki.md); this page covers only that layer.
- **Depends on:** the upstream tokenizer and dictionary projects listed above. None is captured in `raw/` or compiled here.
- **Kokoro packaging:** [Kokoro Python Library](kokoro-python-library.md) installs the `misaki[ja]` and `misaki[zh]` extras for Japanese and Chinese and lists no Vietnamese `lang_code` (**Synthesis** from that concept).

## Coverage and limits

- **Inspected statically:** lines 42–80 of the README capture, covering the English, Japanese, Korean, Chinese, and Vietnamese sections and the TODO entries that record completed language work (**Observed**).
- **Not captured:** the upstream projects `pyopenjtalk`, `unidic-py`, `cutlet`, `fugashi`, `jaconv`, `mojimoji`, `g2pkc`, `g2pK`, the PaddleSpeech frontend, `jieba`, `python-pinyin`, `pinyin-to-ipa`, `Viphoneme`, `spaCy`, and `num2words`; the `EN_PHONES.md` file; and the misaki `ja.py`, `ko.py`, and `zh.py` modules.
- **Not tested:** no Japanese, Korean, Chinese, or Vietnamese text was run through the package. Behavior claims are the README's.
- **Licensing:** the copied Korean tokenizer's license is unverified.
- **Sensitive values:** none. Contributor credits are summarized by role and not recorded by handle.

[^misaki-readme]: [misaki README capture](../raw/misaki.md) — locators: lines 42–45 English links; lines 47–56 Japanese (line 48 second generation, lines 52 first generation, lines 55–56 `jaconv` and `mojimoji` links); lines 58–61 Korean (line 59 copied-tokenizer statement, lines 60–61 links); lines 63–70 Chinese (line 64 second generation, lines 67–70 first generation); lines 72–73 Vietnamese; lines 79–80 completed TODO items.
