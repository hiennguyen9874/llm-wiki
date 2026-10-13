---
type: Concept
title: Kokoro-FastAPI Voice and Markup Controls
description: How Kokoro-FastAPI mixes and aliases voices, switches voice, rate, and pauses inside text, handles SSML, dialogue, phonemes, captions, and voice tuning, and which flags gate each feature.
tags: [tts, kokoro, fastapi, ssml, voice-tags, captions]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:17:58Z }
stale_after: 2027-10-13
sources:
  - id: kokoro-fastapi-readme
    resource: ../raw/Kokoro-FastAPI.md
    kind: documentation
    title: Kokoro-FastAPI README capture
---

Kokoro-FastAPI extends the single `voice` field of a speech request into weighted voicepack mixes, named aliases, and in-text control tokens that switch speaker, pace, and pauses within one generation. Voice tags and SSML need `allow_voice_tags: true` on each request, and the server-side `ENABLE_VOICE_TAGS` flag (on by default) can turn them off. The README marks SSML and voice tuning as experimental and gives no quality evidence for either (**Reported**; **Unverified**).[^kokoro-fastapi-readme]

## Voice selection

- **Weighted mixes:** `af_bella(2)+af_sky(1)` gives a 67%/33% blend, and ratios normalize to 100% (lines 321–332; **Reported**).[^kokoro-fastapi-readme] `POST /v1/audio/voices/combine` returns the mix as a `.pt` file that can be passed back as `voice` (lines 321–369).
- **Aliases:** `voice_aliases` maps a short name to a voice or mix on each request, for both the `voice` field and `[voice:…]` tags. Matching is documented as preferring case-insensitive, and an alias pointing at a missing voice returns 400 (lines 371–410). The web UI's cast export uses the same `{"voice_aliases": {...}}` shape.
- **Alias presets:** an alias can carry a `rate`, for example `{"grandpa": {"voice": "am_michael", "rate": 0.8}}`, applied whenever that alias speaks (lines 505–511).

## Inline control tokens

| Token | Form | Gate stated in README | Behavior |
| --- | --- | --- | --- |
| Pause | `[pause:1.5s]` | none stated | Inserts silence. Must match exactly (colon, trailing `s`, case-insensitive); `[pause=1.5]` and `[PAUSE 1.0]` are read aloud. |
| Pronunciation | bracketed word, then IPA in parentheses: `[Worcester]` + `(/wˈʊstər/)` | none stated | Speaks the IPA between slashes. English only; `/dev/phonemize` finds IPA. |
| Voice | `[voice:am_michael]` | `allow_voice_tags` per request, plus `ENABLE_VOICE_TAGS` | Switches speaker for following text. Accepts combine syntax and aliases; an unknown value returns 400. |
| Rate | `[rate:1.5]` | same as voice tags | Scales the speaking voice's pace, clamped to 0.25–4.0 on top of request `speed`. `[rate:1.0]` reverts. |

- Lines 491–513 give this table's source (**Reported**).[^kokoro-fastapi-readme] With gating off, tags are "spoken as written" (line 501).
- Rate tags scale the speaker's calibrated pace. Each `[voice:…]` tag resets to that voice's own rate, so one calibrated speaker cannot carry its pace into the next. Use `speed` for a whole-request pace (lines 505–511).
- Whether `ENABLE_VOICE_TAGS` also suppresses pause and pronunciation tokens is not stated (**Unverified** open question).

## SSML input (experimental)

- Send `ssml: true` with `allow_voice_tags: true` on `/v1/audio/speech` or `/dev/captioned_speech`. Without both flags the request returns 400 (lines 515–519).
- Translation rules (lines 521–541; **Reported**):
  - `<break time="750ms"/>` becomes `[pause:0.75s]`. `strength=` maps none and x-weak to 0 s, weak to 0.25 s, medium to 0.5 s, strong to 1 s, and x-strong to 1.5 s.
  - `<voice name="…">` becomes `[voice:…]` and reverts at the closing tag.
  - `<prosody rate="slow">` becomes `[rate:0.75]`; percentages and numbers also work. `pitch` and `volume` are ignored.
  - `<phoneme alphabet="ipa" ph="…">` becomes a pronunciation token (IPA and English only).
  - `<sub alias="…">` speaks the alias. `<desc>` is dropped with its text. `<emphasis>`, `<say-as>`, `<p>`, `<s>`, and `<lang>` lose their markup and keep their text.
  - Malformed SSML returns 400; non-SSML passes through unchanged; DTDs are refused; nesting beyond `SSML_MAX_DEPTH` (10) returns 400.
- `POST /dev/ssml` returns the translated tokens as text for inspection; `GET /dev/ssml` serves the translation tables as data (line 541).
- Prefixed attributes such as `google:style` need their `xmlns:` declaration on `<speak>` (line 540).

## Multi-speaker and dialogue

- Inline: `[voice:…]` tags switch speakers within `input`. `/v1/audio/speech` needs `allow_voice_tags: true` on each request (lines 433–440).
- Structured: `POST /dev/dialogue` takes `turns` (each with `voice` and `text`) and `pause_between_turns` (example 0.4), and allows tags by default (lines 451–476).
- Rules (lines 478–481): text before the first tag uses the request's voice; each speaker keeps its own language pipeline from its voice prefix; an explicit `lang_code` overrides every speaker; consecutive turns with the same voice merge; tags accept aliases.
- Opt-out: `ENABLE_VOICE_TAGS=false` refuses the parameter, and `/dev/dialogue` returns 403 (line 437).

## Phonemes

- `POST /dev/phonemize` takes `text` and `language` (`"a"` for American English) and returns `phonemes` and `tokens` (lines 561–607).
- `POST /dev/generate_from_phonemes` takes `phonemes` and `voice`. With `Accept: audio/wav` it returns WAV bytes.

## Captions and timestamps

- **Word level:** `POST /dev/captioned_speech` returns JSON with base64 `audio` and a `timestamps` list. With `stream: true` it returns line-delimited JSON chunks (lines 609–671). With `allow_voice_tags`, each timestamp also carries the speaking `voice`; otherwise the field is absent (line 669).
- **Chunk level:** `POST /v1/audio/speech` with `stream`, `return_download_link`, and `return_timing` sets an `X-Timing-Path` header. That header points to a JSON sidecar of `{text, start, end}` chunks (lines 673–700). The sidecar is written when generation ends, so fetching it earlier returns 404.
- Chunks are sentence groups of roughly 10–20 s of audio, not words (line 695). `start` and `end` are seconds in the final audio, so pauses and speed are included. `[pause]` gaps appear as empty-text entries. Text is normalized, so align by words rather than exact strings.

## Voice tuning (experimental)

- `POST /dev/tune` takes a 3–30 s clip of one English speaker and speaks with a voice tuned toward it through [`inno-kokoro`](https://github.com/remsky/inno-kokoro). The README calls it "a tuner, not a cloner" that gives "the same neighbourhood, not a match" (line 414; **Reported**).[^kokoro-fastapi-readme]
- Output options: audio in the response; `return_voice_pack=true` for a `.pt` pack that lasts only for that response; or `save_voice` to keep it in `VOICES_DIR`, where saved names get a `_tuned` suffix (lines 417–422). Bundled tuned voices end in `_inno`.
- Knobs: `prosody_head` (default on) and `fmax` pitch ceiling in Hz (default auto) (line 424).
- Off by default: `ENABLE_INNO_TUNER=true` adds the feature and a web player tab; `ALLOW_LOCAL_VOICE_SAVING=true` allows saving to the live server (lines 425–427).
- The README says "Only tune voices you have permission to use" (line 416). That is a consent boundary for operators.

## Relationships

- Parent server, deployment, and flags: [Kokoro-FastAPI](kokoro-fastapi.md).
- Timing and chunking behavior of these features: [Kokoro-FastAPI Performance and Evaluation](kokoro-fastapi-performance.md) (**Synthesis**).
- Upstream model: [Kokoro-82M](kokoro-82m.md). The README does not list the upstream voice inventory; voice names here come only from its examples (**Observed**).
- Vietnamese: this feature set adds no Vietnamese voice, and the README's language list has no Vietnamese entry. For a separate Vietnamese artifact set see [Kokoro Vietnamese](kokoro-vietnamese.md) (**Synthesis**).
- Schema caveat: the extension fields are outside the OpenAI request schema. Test them before relying on an OpenAI-compatible client, as [Speech deployment tools comparison](speech-deployment-tools-comparison.md) advises (**Synthesis**).

## Coverage and limits

- Inspected statically: README lines 318–702 (voices, text control, SSML, phonemes, captions) and 433–489 (dialogue) (**Observed**).[^kokoro-fastapi-readme]
- Not executed: no request sent, no voicepack created, no SSML translated, no tuner run. The SSML tables are the README's own description and were not checked against the translator (**Synthesis**).
- Linked but not captured: `docs/inno-tune.md` (full tuning reference), the `inno-kokoro` project, `api/src/core/openai_mappings.json`, `docs/configuration.md` (normalization fields), `examples/phoneme_examples/`, `examples/assorted_checks/test_dialogue/`, and `examples/assorted_checks/test_openai/`.
- Experimental features (marked 🧪 for SSML and voice tuning) come with no quality, consent-verification, or failure-rate evidence in the capture (**Unverified**).

[^kokoro-fastapi-readme]: [Kokoro-FastAPI README capture](../raw/Kokoro-FastAPI.md) — locators: lines 321–369 Voice Combination (weighted ratios, `voice/combine` `.pt` output); lines 371–410 Voice Aliases; lines 412–431 Voice Tuning (`/dev/tune`, knobs, off-by-default flags, permission line 416); lines 433–489 Multi-Speaker / Dialogue (`allow_voice_tags`, `/dev/dialogue`, merge and language rules, line 437 opt-out); lines 491–513 Inline Control Tokens (pause, pronunciation, voice, rate); lines 505–511 rate bullet and alias `rate`; lines 515–549 SSML Input (translation table, 400 cases, DTD and depth limits, `/dev/ssml`); lines 561–607 Phoneme & Token Routes; lines 609–671 word-level captions; lines 669 `voice` field; lines 673–700 streaming chunk timing and `X-Timing-Path`; line 192 voice mapping file; lines 451–458 `extra_body` example.
