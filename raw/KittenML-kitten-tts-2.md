---
pipeline_tag: text-to-speech
license: other
license_name: stellon-labs-community-license
license_link: LICENSE.md
tags:
  - text-to-speech
  - voice-cloning
  - multilingual
---

# KittenTTS 2

A 1.7B speech language model with in-context voice cloning. It reads text and writes S3
codec tokens, which a vocoder turns into 24 kHz audio.

```bash
pip install kittenml
```

```python
from kittenml import KittenTTS
import soundfile as sf

m = KittenTTS("KittenML/kitten-tts-2")

# a built-in voice
audio = m.generate("Hi! umm.. how are you, I guess?  .. uh.. nice to meet you??",
                   voice="WeatherPresenterCheerful")

# or clone one, from 5-30 seconds of a single speaker
audio = m.generate("This is my own voice.", reference="my_voice.wav")

sf.write("output.wav", audio, m.sample_rate)
```

Everything the model needs is in this repository, so no Hugging Face login is required.

## Voices

`m.available_voices` lists all 115. Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki
and Leo are the same speakers as in KittenTTS 0.8, so existing code keeps working.

Voices named after a person are English. The rest are named for the language they
speak followed by what they are — `SpanishAbuela`, `JapaneseTrainConductor`,
`RussianBabushka` — and are how you reach those languages, since the voice is what
carries the accent. Nine older entries carry a bare language name: Arabic, Chinese,
French, German, Hindi, Italian, Portuguese, Russian, Spanish.

```python
m.generate("Guten Morgen. Ich wünsche dir einen wunderschönen Tag.",
           voice="German", normalize=False)

m.generate("Buenas tardes. Hoy vamos a preparar algo muy especial.",
           voice="SpanishAbuela", normalize=False)
```

Sixteen languages have a named voice: Arabic, Chinese, Dutch, French, German, Hindi,
Indonesian, Italian, Japanese, Korean, Polish, Portuguese, Russian, Spanish, Turkish,
and English.

Pass `normalize=False` for non-English text: the text normalizer is English-tuned and
will mangle numbers and dates in other languages.

## Expression controls

> **Beta.** Emotion control steers delivery rather than guaranteeing it, and the effect
> varies by voice and by sentence.

```python
m.generate("[joyful] We won the grant <laugh> I can (((hardly))) believe it!",
           voice="Kiki", preset="expressive")
```

A leading `[emotion]` tag, inline `<event>` tags and `(((emphasis)))` spans reach the
model as markup rather than being spoken, and switch on its expression conditioning.

**Emotions** — one leading tag sets the emotion for the whole line:

`[angry]` `[contemplative]` `[excited]` `[joyful]` `[mundane]`
`[nervous]` `[sad]` `[stern]` `[surprised]` `[tender]`

**Vocal events** — inline, anywhere in the line:

`<gasp>` `<giggle>` `<growl>` `<gulp>` `<laugh>`
`<pause>` `<scoff>` `<sigh>` `<sob>` `<um>`

**Emphasis** — triple parentheses stress a word or short phrase:

```python
m.generate("I told you (((never))) to open that door.", voice="Victor")
```

Only these twenty tags are recognised. They are the most common of the many in the
training data, so a rarer one such as `[reverent]` is spoken as ordinary text rather
than treated as markup — as is anything else bracketed, like `section [3]` or `x < 5`.

## Weight variants

The language model ships in three packings of the same weights. `weights=` picks one;
`model.available_weights` lists them.

| `weights=` | On disk | |
|---|---|---|
| `"packed"` *(default)* | 954 MB | 1.58-bit ternary body, bf16 embedding. **Lossless** |
| `"emb4"` | 469 MB | Same body in TL2, plus a 4-bit embedding. **Lossy** |
| `"full"` | 3469 MB | Plain bf16 |

```python
m = KittenTTS("KittenML/kitten-tts-2", weights="emb4")
```

Only the variant you ask for is downloaded.

`emb4` halves the download, and the saving is almost entirely the token embedding — 324M
parameters that `packed` has to leave at bf16 because they are not ternary. Its transformer
body is still bit-exact: all 313 non-embedding tensors reproduce `full` exactly. The
embedding is not, at L2 relative error 0.118 against the bf16 export, and it is coded at
4.21 bits per weight across three frequency tiers. That is the one lossy thing here, which
is why `packed` stays the default.

## Decoders

Audio is decoded in two stages, and the first can be swapped for a smaller distilled
student with weights packed to 4 or 8 bits:

```python
m = KittenTTS("KittenML/kitten-tts-2", decoder="student_w4")
```

| Decoder | Flow on disk | |
|---|---|---|
| `default` | 459 MB | Best quality |
| `student_w4` | 39 MB | Distilled single-step student, weights packed to 4 bits |

These trade fidelity for footprint, not for speed: quantisation shrinks storage and
memory bandwidth, not arithmetic.

## What is in here

```
lm/          the speech language model, plus its spk_proj speaker head
speaker/     the speaker-embedding model used when cloning
voices/      reference clips, transcripts, and precomputed embeddings
decoders/    the optional 4-bit decoder
cpp/         GGUF weights for the llama.cpp fork, see "Running on CPU"
config.json  token layout, decode presets, voice and decoder indexes
```

The weights are 947 MiB: 910 MiB for the language model and 37 MiB for the decoder.
A load pulls those rather than the whole repository, and only the decoder you ask for.

The language model's linear weights are ternary — within every 128-wide group each
value is exactly one of `{-scale, 0, +scale}` — so bf16 spends 16 bits to say one of
three things. `lm/model-ternary.safetensors` packs them five trits to a byte, 1.6 bits
per weight, with each group keeping its scale at full precision:

| | |
|---|---|
| `lm/model.safetensors` | 3.47 GB, bf16 throughout |
| `lm/model-ternary.safetensors` | **0.95 GB**, the same weights, 3.6x smaller |

The packing is exact rather than approximate, so the two produce bit-identical audio.
`config.json` points `lm_packed` at the smaller file and that is what gets downloaded;
the full file stays for anything loading this with plain `transformers`.

## Running on CPU

KittenTTS 2 runs on CPU out of the box — `device` is auto-detected — but the fastest way
is [kitten-tts-2-cpp](https://github.com/KittenML/kitten-tts-2-cpp), our llama.cpp fork.
The `cpp/` directory here holds what it needs: the GGUF language model and its decoders.

## Requirements

Python 3.10 or later, and PyTorch.

## License

These weights are released under the [Stellon Labs Community License](LICENSE.md). Research,
non-commercial and limited commercial use are free of charge; the commercial grant ends once you
or your affiliates pass USD $1,000,000 in annual revenue or in total cumulative funding, at which
point you need a separate license from Stellon Labs. Distributing the weights, a derivative, or a
product built on them carries attribution requirements — see Section IV(a).

Two things in here are covered by their own terms instead: `speaker/`, the pyannote
speaker-embedding model, under [MIT](speaker/LICENSE), and the `kittenml` Python package that
loads this repository, under Apache 2.0.
