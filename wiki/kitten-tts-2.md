---
type: Concept
title: Kitten TTS 2
description: KittenML 1.7B ternary speech language model with 115 preset voices across 16 languages, in-context cloning from 5–30 s of reference audio, 20 emotion/event/emphasis markup tags, a 954 MB ternary-packed weight variant, a 39 MB 4-bit student decoder, and a revenue-capped Stellon Labs community license.
tags: [tts, multilingual, voice-cloning, edge, quantization]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:00:29Z }
stale_after: 2027-10-25
sources:
  - id: kitten-tts-2-card
    resource: ../raw/KittenML-kitten-tts-2.md
    kind: documentation
    title: KittenTTS 2 model card (KittenML/kitten-tts-2)
---

Kitten TTS 2 is KittenML's 1.7B-parameter speech language model that reads text and emits S3 codec tokens, which a two-stage decoder turns into 24 kHz audio, shipped as a self-contained Hugging Face repository (`KittenML/kitten-tts-2`) loadable with `pip install kittenml` and no Hub login (**Reported**).[^kitten-tts-2-card] Its distinctive engineering choice is ternary storage: the language model's linear weights are natively ternary — every value in each 128-wide group is exactly one of `{-scale, 0, +scale}` — so the default `packed` export stores them five trits per byte at 1.6 bits per weight and stays bit-identical in output while cutting the LM file from 3.47 GB to 0.95 GB (**Reported**).[^kitten-tts-2-card] It pairs 115 preset voices across 16 languages with in-context cloning from 5–30 s of single-speaker reference audio, beta emotion/vocal-event/emphasis markup, and a distilled one-step 4-bit student decoder that trades fidelity for footprint rather than speed (**Reported**).[^kitten-tts-2-card] The card publishes no benchmark, latency, throughput, or memory figure of any kind, so this page documents capability and packaging, not quality or turn latency (**Reported** absence).[^kitten-tts-2-card]

## Identity and license

- Model name is `KittenTTS 2`; Hub repository `KittenML/kitten-tts-2`; inference package `kittenml` (`pip install kittenml`); Python 3.10 or later plus PyTorch (**Reported**).[^kitten-tts-2-card]
- Card frontmatter declares `pipeline_tag: text-to-speech`, `license: other` with `license_name: stellon-labs-community-license`, `license_link: LICENSE.md`, and tags `text-to-speech`, `voice-cloning`, and `multilingual`; no revision, release date, or capture date appears in the file (**Observed** by static inspection).[^kitten-tts-2-card]
- Weights are released under the Stellon Labs Community License: research, non-commercial, and limited commercial use are free, and the commercial grant ends once the user or its affiliates pass USD $1,000,000 in annual revenue **or** in total cumulative funding, after which a separate license is required; distributing the weights, a derivative, or a product built on them carries attribution requirements under Section IV(a) (**Reported**).[^kitten-tts-2-card]
- Two bundled components carry their own terms instead: `speaker/` is the pyannote speaker-embedding model under MIT (`speaker/LICENSE`), and the `kittenml` Python loader package is Apache 2.0 (**Reported**).[^kitten-tts-2-card]
- The card states everything the model needs lives in the repository, so loading requires no Hugging Face login (**Reported**).[^kitten-tts-2-card]

## Voices and language reach

- `m.available_voices` exposes all 115 voices; `Bella`, `Jasper`, `Luna`, `Bruno`, `Rosie`, `Hugo`, `Kiki`, and `Leo` are the same speakers as in KittenTTS 0.8, so existing voice selections keep working (**Reported**).[^kitten-tts-2-card]
- The voice name is also the language selector: voices named after a person speak English, while the rest concatenate a language and a persona (`SpanishAbuela`, `JapaneseTrainConductor`, `RussianBabushka`), because "the voice is what carries the accent" (**Reported**).[^kitten-tts-2-card]
- Sixteen languages have at least one named voice: Arabic, Chinese, Dutch, French, German, Hindi, Indonesian, Italian, Japanese, Korean, Polish, Portuguese, Russian, Spanish, Turkish, and English. Nine older entries carry a bare language name instead — Arabic, Chinese, French, German, Hindi, Italian, Portuguese, Russian, Spanish — so eight of the sixteen languages have both a bare entry and persona-named voices (**Observed** from the card's lists; the card does not enumerate which bare names map to which personas).[^kitten-tts-2-card]
- Pass `normalize=False` for non-English text: the text normalizer is English-tuned and will mangle numbers and dates in other languages (**Reported**).[^kitten-tts-2-card]
- Cloning takes a reference clip of 5–30 s from a single speaker via `m.generate(text, reference="my_voice.wav")`; a speaker-embedding model in `speaker/` feeds a `spk_proj` speaker head in `lm/` (**Reported**).[^kitten-tts-2-card]
- Output sample rate is available as `m.sample_rate`; the card states the vocoder produces 24 kHz audio (**Reported**; the numeric attribute value is not printed).[^kitten-tts-2-card]

## Expression controls (beta)

The card labels emotion control beta, warning that it steers delivery rather than guaranteeing it and that the effect varies by voice and by sentence (**Reported**).[^kitten-tts-2-card]

- One leading `[emotion]` tag sets the emotion for the whole line: `[angry]`, `[contemplative]`, `[excited]`, `[joyful]`, `[mundane]`, `[nervous]`, `[sad]`, `[stern]`, `[surprised]`, `[tender]` (**Reported**).[^kitten-tts-2-card]
- Inline `[event]` tags can appear anywhere in the line: `<gasp>`, `<giggle>`, `<growl>`, `<gulp>`, `<laugh>`, `<pause>`, `<scoff>`, `<sigh>`, `<sob>`, `<um>` (**Reported**).[^kitten-tts-2-card]
- Triple parentheses stress a word or short phrase: `(((never)))`, `(((hardly)))` (**Reported**).[^kitten-tts-2-card]
- Exactly these twenty tags are recognised; they are the most frequent of the many present in training data, so a rarer tag such as `[reverent]` is spoken as ordinary text, as is any other bracketed span like `section [3]` or `x < 5` (**Reported**).[^kitten-tts-2-card]
- The examples also pass `preset="expressive"` alongside a voice, but the card never documents `preset`, its permitted values, or its interaction with the emotion tags; `config.json` is described as holding "decode presets", which is the only other mention (**Reported**; the mapping is a limit).[^kitten-tts-2-card]

## Weight variants and ternary storage

The same language model ships as three packings selected with `weights=`, and only the requested variant is downloaded; `model.available_weights` lists them (**Reported**).[^kitten-tts-2-card]

| `weights=` | On disk | Composition | Fidelity |
| --- | --- | --- | --- |
| `"packed"` (default) | 954 MB | 1.58-bit ternary body plus bf16 embedding | Card labels it **lossless** |
| `"emb4"` | 469 MB | Same body in TL2 plus a 4-bit embedding | Card labels it **lossy** |
| `"full"` | 3469 MB | Plain bf16 | Reference export |

Values are card assertions (**Reported**); the decimal-MB figures reconcile with the card's binary figures of 947 MiB total (910 MiB language model + 37 MiB decoder), since 954 MB ≈ 910 MiB and 3469 MB ≈ 3.47 GB (**Observed** arithmetic).[^kitten-tts-2-card]

- The ternary packing is `lm/model-ternary.safetensors`, five trits per byte at 1.6 bits per weight, with each 128-wide group's scale kept at full precision; the bf16 file is `lm/model.safetensors` at 3.47 GB, so the packed LM is 3.6x smaller (**Reported**; 3.47/0.95 = 3.65, **Observed**).[^kitten-tts-2-card]
- Because the model's linear weights are natively ternary, the card says the packing is exact rather than approximate and the two files produce bit-identical audio; `config.json` points `lm_packed` at the smaller file, and the bf16 file remains for anything loading the repository with plain `transformers` (**Reported**).[^kitten-tts-2-card]
- `emb4` halves the download and the saving is almost entirely the 324M-parameter token embedding that `packed` must leave at bf16 because it is not ternary; all 313 non-embedding tensors reproduce `full` exactly, while the embedding differs at L2 relative error 0.118 against the bf16 export and is coded at 4.21 bits per weight across three frequency tiers (**Reported**).[^kitten-tts-2-card] This is the card's one lossy path, which is why `packed` stays the default (**Reported**).[^kitten-tts-2-card]
- The declared parameter budget is coherent: 324M embedding plus ~1.376B non-embedding tensors equals the headline 1.7B, and 1.7B parameters at 2 bytes reproduces the 3.47 GB `full` export (**Observed** arithmetic).[^kitten-tts-2-card]

## Decoders

Audio is decoded in two stages and the first can be swapped for a distilled student whose weights are packed to 4 or 8 bits; `decoder="student_w4"` selects it (**Reported**).[^kitten-tts-2-card]

| Decoder | Flow on disk | Description |
| --- | --- | --- |
| `default` | 459 MB | Best quality |
| `student_w4` | 39 MB | Distilled single-step student, weights packed to 4 bits |

The card is explicit that these trade fidelity for footprint and **not** for speed, because quantisation shrinks storage and memory bandwidth rather than arithmetic (**Reported**).[^kitten-tts-2-card] The 8-bit student variant is mentioned but not tabulated with a size or quality note (**Reported** absence).[^kitten-tts-2-card]

## Repository layout and CPU route

```
lm/          the speech language model, plus its spk_proj speaker head
speaker/     the speaker-embedding model used when cloning
voices/      reference clips, transcripts, and precomputed embeddings
decoders/    the optional 4-bit decoder
cpp/         GGUF weights for the llama.cpp fork
config.json  token layout, decode presets, voice and decoder indexes
```

Table is quoted from the card (**Reported**).[^kitten-tts-2-card]

- A load pulls the 947 MiB of weights rather than the whole repository, and only the decoder variant requested (**Reported**).[^kitten-tts-2-card]
- The model runs on CPU out of the box with `device` auto-detected, but the card names `kitten-tts-2-cpp` — "our llama.cpp fork" at `github.com/KittenML/kitten-tts-2-cpp` — as the fastest route, and `cpp/` holds the GGUF language model and decoders it consumes (**Reported**; the fork, its GGUF files, and its quantisation recipes were not inspected).[^kitten-tts-2-card]
- No HTTP server, OpenAI-compatible endpoint, batch API, streaming API, timestamp output, or multi-speaker dialogue mode is documented; the only interface shown is a blocking `generate()` returning a full waveform (**Reported** absence).[^kitten-tts-2-card]

## Limitations

- No WER, SIM, MOS, UTMOS, SCOREQ, RTF, time-to-first-audio, VRAM, or CPU-speed figure appears anywhere in the card, so this model cannot be ranked against other TTS models from its own evidence (**Reported** absence).[^kitten-tts-2-card]
- No architecture detail beyond "1.7B speech language model" plus S3 codec tokens: layer count, token codebook structure, frame rate, decoder families, and training data, compute, and recipe are all absent (**Reported** absence).[^kitten-tts-2-card]
- Whether the ternary linear weights come from ternary-aware training or post-training ternarization is not stated; "lossless" therefore qualifies the packing step, not the model's relation to an unquantized bf16 training artifact (**Synthesis** from the card's wording).[^kitten-tts-2-card]
- "TL2" (the `emb4` body format) is never expanded, and the card gives no per-tensor breakdown that would let the 469 MB figure be reproduced from the stated 1.6-bit body and 4.21-bit embedding (**Reported**; recomputation is a limit).[^kitten-tts-2-card]
- Voice quality is asserted only qualitatively. The card publishes no per-language clarity, accent, or cloning-similarity result, and it does not list which languages lack persona voices (**Reported** absence).[^kitten-tts-2-card]

## Relationships

- Uplifts the KittenTTS lineage referenced elsewhere in this wiki: [sanoTTS](sanotts.md) and [Paradee-8M v1.0](paradee-8m-v1-0.md) both tabulate a "Kitten TTS nano"/"KittenTTS nano 0.8" at roughly 14–15M parameters with one `Bella`-family voice, which is a different, far smaller release than this 1.7B model; only the eight inherited speaker names connect the two generations, and no benchmark is shared between them (**Synthesis**).
- Surveyed in [TTS Model Survey](tts-model-survey.md) as a mid-coverage, cloning-capable, ternary-packed entry (**Synthesis**).
- Uses the ternary-packing idea that appears as GGUF quantisation elsewhere in this wiki but keeps it in the native checkpoint format instead of a converted runtime; the [audio.cpp GGUF catalog](audio-cpp-gguf-packages.md) separately lists a `KittenTTS-GGUF` package under the `kitten_tts` family, whose model generation that catalog does not state, so it is not evidence for or against this model (**Synthesis**).
- Depends on a pyannote speaker-embedding model for cloning, bundled under `speaker/`; it is not the [Resemblyzer](resemblyzer.md) embedding toolkit compiled elsewhere in this wiki, and the bundled weights were not inspected (**Synthesis**).

## Contradictions

- The two on-disk size figures use mixed units — decimal MB in the weight-variant table (954 / 469 / 3469 MB) and binary MiB/GB in the prose (947 MiB, 0.95 GB, 3.47 GB) — which reads as a disagreement only until converted; they reconcile to within rounding, and the smaller `packed` figure is reproduced by 324M bf16 embedding parameters plus ~1.376B ternary parameters (**Observed** arithmetic, not a conflict).[^kitten-tts-2-card]
- The body bit-width is given both as "1.58-bit" (the ternary entropy) and "1.6 bits per weight" (five trits per byte); these describe different quantities and are not contradictory, but the card does not say which one it uses for footprint accounting (**Observed**).[^kitten-tts-2-card]

## Coverage and limits

Single capture, `raw/KittenML-kitten-tts-2.md` (187 lines), read in full and inspected statically; no source file inside the repository, no weights, no code and no audio were available in `raw/` (**Observed** inspection scope).[^kitten-tts-2-card]

- Entry point and scope: the whole Hugging Face model card. It is the repository's own README-style card, so it is the package entry point; the repository's `lm/`, `speaker/`, `voices/`, `decoders/`, `cpp/` trees, `config.json`, `LICENSE.md`, `speaker/LICENSE`, and the `kittenml` Python package are referenced but were not captured, so the coverage ledger treats all of them as uninspected (**Observed**).[^kitten-tts-2-card]
- Excluded as non-durable: the two code fences (they duplicate the API in the prose), the repository tree listing (quoted once, above), and the persona voice names beyond the eight inherited ones and the sampled examples (**Synthesis**).
- Unavailable or unverifiable: no revision or capture date; no `LICENSE.md` text, so the revenue cap and attribution clause are known only from the card's summary; no voices list, so the "115" and the sixteen-language roster are counted from prose rather than enumerated (**Observed** absence).[^kitten-tts-2-card]
- Not executed: nothing was installed, downloaded, synthesised, listened to, or benchmarked; every performance, quality, and licensing statement here is **Reported**, and only unit/parameter arithmetic is **Observed**.[^kitten-tts-2-card]
- Time-sensitivity: per the `tts` domain rule, `stale_after: 2027-10-25` covers the model/API release and would repeat the absent benchmark figures once published (**Synthesis**).
- No sensitive values are present in the capture or reproduced here (**Observed**).[^kitten-tts-2-card]

[^kitten-tts-2-card]: [KittenTTS 2 model card](../raw/KittenML-kitten-tts-2.md) — locators: frontmatter (`pipeline_tag: text-to-speech`, `license: other`, `license_name: stellon-labs-community-license`, `license_link: LICENSE.md`, tags); title plus lead paragraph (1.7B, in-context cloning, S3 codec tokens, 24 kHz); install and usage fences (`pip install kittenml`, `KittenTTS("KittenML/kitten-tts-2")`, `voice=`/`reference=`, `m.sample_rate`, "no Hugging Face login"); `## Voices` (115 voices, eight inherited speakers, naming convention, nine bare language names, 16-language list, `normalize=False`); `## Expression controls` (beta warning, ten emotions, ten vocal events, `(((emphasis)))`, twenty-tag limit, unrecognised-tag behaviour, `preset="expressive"` example); `## Weight variants` table (packed 954 MB / emb4 469 MB / full 3469 MB) plus the `lm_packed`, 313-tensor, 324M-embedding, L2 0.118 and 4.21-bit paragraphs; `## Decoders` table (default 459 MB, `student_w4` 39 MB, fidelity-not-speed sentence); `## What is in here` tree plus the 947 MiB / 910 MiB / 37 MiB split and the ternary 128-wide-group, five-trit, 3.47 GB vs 0.95 GB, bit-identical-audio paragraphs; `## Running on CPU` (auto-detected device, `kitten-tts-2-cpp` llama.cpp fork); `## Requirements` (Python 3.10+, PyTorch); `## License` (Stellon Labs Community License terms, USD $1,000,000 threshold, Section IV(a) attribution, pyannote MIT, Apache 2.0 loader). No revision, release date, or capture date in the file.
