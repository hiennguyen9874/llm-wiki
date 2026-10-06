---
type: Concept
title: Supertonic 3
description: Supertone's ~99M-parameter on-device multilingual TTS covering 31 languages with ONNX runtime, preset plus Voice Builder custom voices, and expression-tag control.
tags: [tts, on-device, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T23:55:00Z }
stale_after: 2027-10-06
sources:
  - id: supertonic-3-card
    resource: ../raw/supertonic-3.md
    kind: documentation
    title: Supertonic 3 Hugging Face model card
---

Supertonic 3 is Supertone Inc's on-device multilingual text-to-speech release, running on ONNX Runtime with no cloud call required for synthesis, expanding language coverage from 5 to 31 languages at about 99M parameters across the public ONNX assets, with claimed improvements in reading stability and speaker similarity over Supertonic 2 plus simple expression tags (**Reported**).[^supertonic-3-card]

## Model identity and release

- Title is `Supertonic 3 | Lightning Fast, On-Device, Accurate TTS`; creator and copyright holder is Supertone Inc (copyright 2026); demo is `https://huggingface.co/spaces/Supertone/supertonic-3`, code is `https://github.com/supertone-inc/supertonic`, and the Python SDK is `supertonic` on PyPI (**Reported**).[^supertonic-3-card]
- Frontmatter declares `pipeline_tag: text-to-speech`, `library_name: supertonic`, `license: openrail`, 31 language codes (`en, ko, ja, ar, bg, cs, da, de, el, es, et, fi, fr, hi, hr, hu, id, it, lt, lv, nl, pl, pt, ro, ru, sk, sl, sv, tr, uk, vi`), and tags `text-to-speech, speech-synthesis, tts, onnx, multilingual, on-device` (**Observed** by static inspection).[^supertonic-3-card]
- Positioned as the successor to the 5-language Supertonic 2 release, keeping the lightweight local-inference design with no cloud call required for synthesis (**Reported**).[^supertonic-3-card]

## What's new versus Supertonic 2

- Language coverage expands from 5 to 31 languages (**Reported**).[^supertonic-3-card]
- Reading is claimed to be more stable, with fewer repeat and skip failures, especially on short and long utterances (**Reported**).[^supertonic-3-card]
- Speaker similarity is claimed to be higher across the shared-language set compared with Supertonic 2 (**Reported**).[^supertonic-3-card]
- Expression tags are supported, with simple tags such as `<laugh>`, `<breath>`, and `<sigh>` named as examples (**Reported**).[^supertonic-3-card]

## Supported languages

- The 31 supported language codes are English (`en`), Korean (`ko`), Japanese (`ja`), Arabic (`ar`), Bulgarian (`bg`), Czech (`cs`), Danish (`da`), German (`de`), Greek (`el`), Spanish (`es`), Estonian (`et`), Finnish (`fi`), French (`fr`), Hindi (`hi`), Croatian (`hr`), Hungarian (`hu`), Indonesian (`id`), Italian (`it`), Lithuanian (`lt`), Latvian (`lv`), Dutch (`nl`), Polish (`pl`), Portuguese (`pt`), Romanian (`ro`), Russian (`ru`), Slovak (`sk`), Slovenian (`sl`), Swedish (`sv`), Turkish (`tr`), Ukrainian (`uk`), and Vietnamese (`vi`) (**Reported**).[^supertonic-3-card]

| Code | Language | Code | Language | Code | Language | Code | Language |
|------|----------|------|----------|------|----------|------|----------|
| `en` | English | `ko` | Korean | `ja` | Japanese | `ar` | Arabic |
| `bg` | Bulgarian | `cs` | Czech | `da` | Danish | `de` | German |
| `el` | Greek | `es` | Spanish | `et` | Estonian | `fi` | Finnish |
| `fr` | French | `hi` | Hindi | `hr` | Croatian | `hu` | Hungarian |
| `id` | Indonesian | `it` | Italian | `lt` | Lithuanian | `lv` | Latvian |
| `nl` | Dutch | `pl` | Polish | `pt` | Portuguese | `ro` | Romanian |
| `ru` | Russian | `sk` | Slovak | `sl` | Slovenian | `sv` | Swedish |
| `tr` | Turkish | `uk` | Ukrainian | `vi` | Vietnamese | | |

## Quick start and usage

- Installation is `pip install supertonic`; on first run the SDK downloads the model assets from Hugging Face when constructed with `TTS(auto_download=True)` (**Reported**).[^supertonic-3-card]
- Synthesis follows `get_voice_style(voice_name="M1")` for a preset style and then `synthesize(text, voice_style=style, lang="en")`, which returns `wav` audio plus `duration`, with `save_audio(wav, "output.wav")` writing the file; the worked example synthesizes an English sentence and prints the generated duration in seconds (**Reported**).[^supertonic-3-card]
- The usage snippet was inspected statically only; no package was installed and no synthesis was executed (**Synthesis**).[^supertonic-3-card]

## Voices and custom-voice demo

- The open-weight package includes fixed preset voice styles for immediate local inference (**Reported**).[^supertonic-3-card]
- Zero-shot custom voice styles are demonstrated through an external audio-sample demo page with reference/generated pairs, including a call-center English sample, a Japanese character-voice sample, a Korean elder character-voice sample, two audiobook samples (English and Japanese), and an English news sample announcing the Supertonic 3 release; the audio itself was not listened to and only the quoted prompt texts were captured (**Reported** with an availability limit).[^supertonic-3-card]
- Custom voice-style JSON is created from reference audio with the external Supertonic Voice Builder; purchased Voice Builder styles include downloadable embeddings for both Supertonic 2 and Supertonic 3 (**Reported**).[^supertonic-3-card]

## Performance highlights

- The card frames Supertonic 3 as designed for practical on-device inference: compact enough to run locally while staying competitive with much larger open TTS systems (**Reported**).[^supertonic-3-card]
- Reading accuracy: across measured languages Supertonic 3 is claimed to stay within a competitive WER/CER range against much larger open TTS models such as VoxCPM2 while preserving a lightweight on-device deployment path; asterisked languages use CER and the others use WER; the underlying values are plotted in an image that is not in `raw/`, so no numeric WER/CER figures are recorded here (**Reported** with an image-only limit).[^supertonic-3-card]
- Supertonic 2 to Supertonic 3: the card claims reduced repeat and skip failures, improved speaker similarity across the shared-language set, and expanded coverage from 5 to 31 languages; the comparison is plotted in an image that is not in `raw/`, so no numeric values are recorded here (**Reported** with an image-only limit).[^supertonic-3-card]
- Runtime footprint: Supertonic 3 is claimed to run fast on CPU even compared with larger baselines measured on A100 GPU, to use substantially less memory, and to require no GPU, which eases local, browser, and edge deployment; the latency/memory figure is image-only and not in `raw/`, so no numeric latency or memory figures are recorded here (**Reported** with an image-only limit).[^supertonic-3-card]
- Model size: about 99M parameters across the public ONNX assets, described as much smaller than 0.7B-to-2B class open TTS systems, with stated practical advantages for download size, startup time, and on-device inference; the size comparison is image-only and not in `raw/` (**Reported** with an image-only limit).[^supertonic-3-card]

## License

- Sample code is under the MIT License; the accompanying model is under the OpenRAIL-M License; training used PyTorch under BSD 3-Clause without redistributing it (**Reported**).[^supertonic-3-card]

## Relationships

- Direct predecessor: [Supertonic 2](supertonic-2.md) covers the 66M-parameter 5-language ONNX on-device TTS with published characters-per-second and real-time-factor tables, while this concept covers the 31-language successor at about 99M parameters with claimed stability, similarity, and expression-tag deltas but image-only benchmark figures; no deprecation of Supertonic 2 is asserted in this source (**Synthesis**).[^supertonic-3-card]
- Family origin: [Supertonic](supertonic.md) covers the original repository README with 66M parameters, up-to-167x-real-time claims, numeric throughput tables, and 11-runtime deployment examples, while this concept covers the third-generation 31-language release with Voice Builder custom voices (**Synthesis**).[^supertonic-3-card]
- Reported comparator: [VoxCPM2](voxcpm2.md) covers a 2B-parameter tokenizer-free diffusion-autoregressive multilingual TTS model that this source names as a much larger open system against which Supertonic 3 claims a competitive WER/CER range at a fraction of the size; the underlying values are image-only and no ranking is reproduced here (**Synthesis**).[^supertonic-3-card]
- Packaged derivative: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) catalogs a `Supertonic-3-GGUF` conversion (original plus F16 plus Q8 weights under BigScience OpenRAIL-M) with an audio.cpp CLI usage fence, while this concept covers the upstream Hugging Face card and Python SDK path; the GGUF artifact is compiled from a different source and is not covered here (**Synthesis**).[^supertonic-3-card]

## Coverage and limits

- Source inspected statically only; no checkpoint downloaded, no ONNX inference executed, and no reading-stability, speaker-similarity, latency, memory, model-size, or no-cloud claims reproduced (**Synthesis**).[^supertonic-3-card]
- The hero image and all four metric figures (`Supertonic3_HeroImage.png`, reading-accuracy, v2-vs-v3 comparison, CPU/GPU latency-memory, and model-size plots) are referenced by relative `img/` paths that are not in `raw/` and were not fetched; no numeric benchmark, latency, or memory value from those images is recorded (**Synthesis**).[^supertonic-3-card]
- The demo Space, GitHub repository, PyPI package, audio-sample demo page, Voice Builder, the 12 reference/generated audio files, and the linked LICENSE and PyTorch-license pages were not fetched; model weights, preset voices, generated audio quality, and voice-cloning fidelity were not inspected (**Synthesis**).[^supertonic-3-card]
- All capability, language-coverage, speed, efficiency, benchmark, and license claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^supertonic-3-card]
- This ingest covers only `raw/supertonic-3.md`; the related `raw/supertonic.md` and `raw/supertonic-2.md` are compiled in [Supertonic](supertonic.md) and [Supertonic 2](supertonic-2.md), and the `Supertonic-3-GGUF` packaging is cataloged from `raw/audio.cpp-gguf.md` in [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) (**Synthesis**).[^supertonic-3-card]

[^supertonic-3-card]: [Supertonic 3 Hugging Face model card](../raw/supertonic-3.md) — locators: frontmatter (`license: openrail`, 31-code `language`, `pipeline_tag: text-to-speech`, `tags`, `library_name: supertonic`); H1 plus intro paragraph (ONNX Runtime, on-device, no cloud call); badge links (Hugging Face demo Space, GitHub repository, PyPI `supertonic`); `Quick Start` fences (`pip install supertonic`, `TTS(auto_download=True)`, `get_voice_style(voice_name="M1")`, `synthesize(text, voice_style, lang="en")` returning `wav, duration`, `save_audio`); `What's New in Supertonic 3` bullets (31 languages from 5, stable reading with fewer repeat/skip on short and long utterances, higher speaker similarity, `<laugh>`/`<breath>`/`<sigh>` tags); `Custom Voices and Audio Samples` section (fixed preset styles, audio-sample demo page, Voice Builder JSON creation plus purchased-embedding note, six reference/generated pairs with quoted prompt texts); `Performance Highlights` intro plus `Reading Accuracy` (competitive WER/CER vs larger open models such as VoxCPM2, asterisked CER note), `Supertonic 2 to Supertonic 3` (repeat/skip, similarity, 5-to-31 coverage), `Runtime Footprint` (fast CPU vs A100-GPU baselines, less memory, no GPU, local/browser/edge), and `Model Size` (~99M ONNX params vs 0.7B–2B class, download/startup/on-device advantages) subsections, all with image-only figures under `img/metrics/`; `Supported Languages` 31-code table; `License` section (MIT sample code, OpenRAIL-M model, PyTorch BSD 3-Clause, 2026 Supertone copyright).
