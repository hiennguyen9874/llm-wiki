---
type: Concept
title: Chatterbox TTS
description: Open-source MIT-licensed TTS family from Resemble AI with Multilingual V3 across 23 languages, six single-language finetunes, low-latency Turbo 350M and Nano 110M models, and emotion exaggeration control.
tags: [tts, multilingual, voice-cloning]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T16:30:00Z }
stale_after: 2027-10-06
sources:
  - id: chatterbox-card
    resource: ../raw/chatterbox.md
    kind: documentation
    title: Chatterbox TTS
  - id: chatterbox-repo
    resource: ../raw/chatterbox-repo.md
    kind: documentation
    title: Chatterbox TTS GitHub repository README
---

Chatterbox TTS is Resemble AI's open-source MIT-licensed text-to-speech family built on a 0.5B Llama backbone for the general models, plus low-latency English Turbo (350M) and Nano (110M) models with a distilled single-step decoder and native paralinguistic tags, offering an English zero-shot model with emotion exaggeration control, a Multilingual V3 model covering 23 languages, and six dedicated single-language finetunes, with PerTh watermarking on every generated file (**Reported**).[^chatterbox-card][^chatterbox-repo]

## Model identity and release

- Family name is `Chatterbox TTS`; creator is Resemble AI; license is MIT; inference library is `chatterbox-tts` (`pip install chatterbox-tts`); demos are the Hugging Face Gradio app, the demo-samples page, and the Multilingual V3 Space (**Reported**).[^chatterbox-card]
- Source frontmatter declares `pipeline_tag: text-to-speech`, `library_name: chatterbox`, 23 language codes (`ar, da, de, el, en, es, fi, fr, he, hi, it, ja, ko, ms, nl, no, pl, pt, ru, sv, sw, tr, zh`), and tags including `text-to-speech`, `speech-generation`, and `voice-cloning` (**Reported**, with frontmatter fields **Observed** by static inspection).[^chatterbox-card]
- Multilingual V3 is the recommended general-purpose multilingual model: same 0.5B size as V2 with improved speaker similarity, reduced hallucinations (unwanted continuation, repetition, off-prompt speech), and more natural conversational output (**Reported**).[^chatterbox-card]

## Architecture and training

- Backbone is a 0.5B Llama model; inference is described as ultra-stable via alignment-informed inference; training used 0.5M hours of cleaned data (**Reported**).[^chatterbox-card]
- Acknowledgements name CosyVoice, HiFT-GAN, and Llama 3 as building blocks (**Reported**).[^chatterbox-card] The repository README additionally acknowledges Real-Time-Voice-Cloning, S3Tokenizer, and Podonos for reproducible subjective speech evaluation (**Reported**).[^chatterbox-repo]
- Source claims state-of-the-art zero-shot English TTS and links a Podonos side-by-side evaluation page asserting Chatterbox outperforms ElevenLabs; no benchmark numbers are reproduced in the source (**Reported**).[^chatterbox-card]

## Low-latency Turbo and Nano models

- Chatterbox-Turbo is a streamlined 350M-parameter English model for low-latency voice agents, described as delivering high-quality speech with less compute and VRAM than previous models; its speech-token-to-mel decoder was distilled from 10 steps to one while retaining high-fidelity output (**Reported**).[^chatterbox-repo]
- Chatterbox-Nano shares Turbo's architecture in a 110M-parameter package for on-device and CPU inference, rated at 3x faster than realtime on 8 CPU cores with the same single-step decoder; it is the recommended model when memory and latency budgets are tightest (**Reported**).[^chatterbox-repo]
- Both Turbo and Nano support native paralinguistic tags such as `[cough]`, `[laugh]`, and `[chuckle]` for added realism; Turbo is also positioned for narration and creative workflows beyond voice agents (**Reported**).[^chatterbox-repo]

## Supported languages

Arabic, Danish, German, Greek, English, Spanish, Finnish, French, Hebrew, Hindi, Italian, Japanese, Korean, Malay, Dutch, Norwegian, Polish, Portuguese, Russian, Swedish, Swahili, Turkish, and Chinese — 23 languages out of the box (**Reported**).[^chatterbox-card]

## Model zoo

| Model | Size | Languages | Key features | Best for |
| --- | --- | --- | --- | --- |
| Chatterbox-Turbo | 350M | English | Paralinguistic tags (`[laugh]`), lower compute and VRAM, distilled one-step decoder | Zero-shot voice agents, production |
| Chatterbox-Nano | 110M | English | Same architecture as Turbo, paralinguistic tags, runs on CPU (3x realtime on 8 cores) | On-device / CPU inference, tight latency and memory budgets |
| Chatterbox Multilingual V3 | 500M | 23+ | Improved speaker similarity, reduced hallucinations, more natural multilingual speech | Global applications, localization, cross-language voice cloning |
| Single Language Pack | 500M each | 6 dedicated finetunes | Language- and region-specific quality control | Priority languages and dialect-sensitive applications |
| Chatterbox (English) | 500M | English | CFG and exaggeration tuning | General zero-shot TTS with creative controls |

Table values are source assertions (**Reported**).[^chatterbox-card][^chatterbox-repo]

## Single Language Pack

Dedicated 500M finetunes for priority languages and regional variants, each with its own Hugging Face model card and demo Space (**Reported**):[^chatterbox-card][^chatterbox-repo]

| Language variant | Model card | Demo Space |
| --- | --- | --- |
| Chinese | `ResembleAI/Chatterbox-Multilingual-zh-cmn` | Multilingual-TTS-zh-cmn Space |
| LatAm Spanish | `ResembleAI/Chatterbox-Multilingual-es-mx-latam` | Multilingual-TTS-es-mx-latam Space |
| Brazilian Portuguese | `ResembleAI/Chatterbox-Multilingual-pt-br` | Multilingual-TTS-pt-br Space |
| Spain Spanish | `ResembleAI/Chatterbox-Multilingual-es-es` | Multilingual-TTS-es-es Space |
| Portugal Portuguese | `ResembleAI/Chatterbox-Multilingual-pt-pt` | Multilingual-TTS-pt-pt Space |
| Hindi | `ResembleAI/Chatterbox-Multilingual-hi` | Multilingual-TTS-hi Space |

## Capabilities

- Zero-shot voice cloning synthesizes from text alone or with a reference voice via `audio_prompt_path` (**Reported**).[^chatterbox-card][^chatterbox-repo]
- Exaggeration/intensity control tunes emotional expressiveness; the source presents Chatterbox as the first open-source TTS model with emotion exaggeration control (**Reported**).[^chatterbox-card]
- CFG guidance weight (`cfg`) trades stability against expressiveness and pacing alongside `exaggeration` (**Reported**).[^chatterbox-card]
- Native paralinguistic tags on Turbo and Nano (`[cough]`, `[laugh]`, `[chuckle]`, and more) add distinct realism inline in the input text (**Reported**).[^chatterbox-repo]
- Voice conversion is offered via an easy voice-conversion script (listed; script contents not in source) (**Reported**).[^chatterbox-card] The repository capture additionally points to `example_vc.py` alongside `example_tts.py`, `example_tts_turbo.py`, and `example_tts_nano.py` (**Reported**).[^chatterbox-repo]
- Every generated file carries an imperceptible Resemble AI PerTh (Perceptual Threshold) neural watermark, claimed to survive MP3 compression, audio editing, and common manipulations at nearly 100% detection accuracy (**Reported**).[^chatterbox-card][^chatterbox-repo]

## Requirements and inference usage

- Install with `pip install chatterbox-tts` (**Reported**).[^chatterbox-card][^chatterbox-repo] Installing from source clones `https://github.com/resemble-ai/chatterbox.git` and runs `pip install -e .`; the repository reports development and testing on Python 3.11 on Debian 11 with dependency versions pinned in `pyproject.toml` (**Reported**).[^chatterbox-repo]
- English inference loads `ChatterboxTTS.from_pretrained(device="cuda")` and calls `model.generate(text)`, saving with `torchaudio.save(path, wav, model.sr)`; passing `audio_prompt_path` clones a different voice (**Reported**).[^chatterbox-card]
- Turbo inference loads `ChatterboxTurboTTS.from_pretrained(device="cuda")` from `chatterbox.tts_turbo` and calls `generate(text, audio_prompt_path=...)`, saving with `torchaudio.save(path, wav, model.sr)`; Nano uses the same class with `nano=True` and also runs on `device="cpu"` (**Reported**).[^chatterbox-repo]
- Multilingual inference loads `ChatterboxMultilingualTTS.from_pretrained(device="cuda", t3_model="v3")` and calls `generate(text, language_id=...)` (e.g. `"fr"`, `"zh"`); omitting `t3_model` or passing `"v2"` selects the legacy V2 checkpoint (**Reported**).[^chatterbox-card][^chatterbox-repo]

## Tuning tips

- General use and voice agents: defaults `exaggeration=0.5`, `cfg=0.5` work well for most prompts; if the reference speaker is fast, lowering `cfg` to ~0.3 can improve pacing (**Reported**).[^chatterbox-card]
- Expressive or dramatic speech: try lower `cfg` (~0.3) with `exaggeration` ~0.7 or higher; higher `exaggeration` tends to speed up speech, and reducing `cfg` compensates with slower, more deliberate pacing (**Reported**).[^chatterbox-card]
- The reference clip must match the specified language tag, otherwise language-transfer output may inherit the reference clip's accent; setting the CFG weight to 0 mitigates this (**Reported**).[^chatterbox-card]

## Watermark extraction

- The repository documents watermark lookup with `perth.PerthImplicitWatermarker().get_watermark(audio, sample_rate=sr)` after loading audio with `librosa`, returning `0.0` (no watermark) or `1.0` (watermarked) (**Reported**).[^chatterbox-repo]

## Evaluation

- Chatterbox Turbo was evaluated through Podonos reproducible subjective speech evaluation on overall preference, naturalness, and expressiveness, with three public reports under identical conditions: Turbo vs ElevenLabs Turbo v2.5, Turbo vs Cartesia Sonic 3, and Turbo vs VibeVoice 7B; no scores are reproduced in the captured README (**Reported**).[^chatterbox-repo]

## Citation

- The source requests citation as `@misc{chatterboxtts2025, author = {Resemble AI}, title = {Chatterbox-TTS}, year = {2025}, howpublished = {https://github.com/resemble-ai/chatterbox}}` (**Reported**).[^chatterbox-repo]

## Production service

- Resemble AI offers a paid TTS service for scaling or tuning, advertised at sub-200 ms ultra-low latency for agents, applications, and interactive media (**Reported**).[^chatterbox-card]

## Relationships

- Acknowledged lineage: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) covers the CosyVoice-line LLM-based streaming TTS family, while this concept's source acknowledges CosyVoice among its building blocks; no shared weights are asserted (**Synthesis**).[^chatterbox-card]
- GGUF packaging pointer: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) catalogs `Chatterbox-GGUF` and `Chatterbox-Turbo-GGUF` packages, while this concept covers the upstream Chatterbox model family itself; deployment via those packages is not detailed here (**Synthesis**).[^chatterbox-card]
- Multilingual TTS comparison: [VoxCPM2](voxcpm2.md) covers a 2B diffusion-autoregressive 30-language TTS model with voice design and cloning modes, while this concept covers a 0.5B Llama-backbone TTS family with 23-language V3 plus six single-language finetunes and exaggeration/CFG controls; no shared vendor or codebase is asserted (**Synthesis**).[^chatterbox-card]

## Coverage and limits

- Both sources inspected statically only; no package installed, no checkpoint downloaded, no audio synthesized, and no speaker-similarity, hallucination-rate, benchmark-preference, watermark-robustness, or latency claims reproduced (**Synthesis**).[^chatterbox-card][^chatterbox-repo]
- Demo pages, Hugging Face Spaces and model pages, Discord invite, Podonos Turbo evaluation reports, `example_tts.py`, `example_tts_turbo.py`, `example_tts_nano.py`, `example_vc.py`, and the voice-conversion script were linked but not fetched and are not in `raw/`; checkpoint weights, reference-audio files, header image `Chatterbox-Multilingual.png`, and training data were listed but not present in `raw/` and were not inspected (**Synthesis**).[^chatterbox-card][^chatterbox-repo]
- The repository capture carries no explicit revision, date, or license statement; the MIT license and 0.5B Llama backbone rest on the earlier `raw/chatterbox.md` capture, and Turbo/Nano speed, VRAM, single-step-decoder, paralinguistic-tag, and Podonos-comparison claims are repository assertions without independent verification here (**Synthesis**).[^chatterbox-card][^chatterbox-repo]
- All identity, architecture, training-scale, language-coverage, capability, tuning, and usage claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^chatterbox-card]

[^chatterbox-card]: [Chatterbox TTS](../raw/chatterbox.md) — locators: frontmatter (`pipeline_tag`, `library_name`, 23-code `language` list, `tags`, `license: mit`); `Latest Release: Chatterbox Multilingual V3` section (V3 improvements, Single Language Pack intro, 23-language list, ElevenLabs side-by-side claim, sub-200 ms service sentence); `Model Zoo` table (3 rows: Multilingual V3 500M/23+, Single Language Pack, Chatterbox 500M English); `Key Details` list (V3, 6 finetunes, SoTA zeroshot English, 0.5B Llama backbone, exaggeration control, alignment-informed inference, 0.5M hours, watermarking, voice conversion, Podonos link); `Tips` section (defaults 0.5/0.5, fast-speaker cfg 0.3, expressive cfg 0.3 plus exaggeration 0.7+, language-tag/CFG-0 accent note); `Installation` fence (`pip install chatterbox-tts`); `Usage` fence (`ChatterboxTTS.from_pretrained`, `generate`, `audio_prompt_path`); `Multilingual Quickstart` fence (`ChatterboxMultilingualTTS.from_pretrained` with `t3_model="v3"`/`"v2"`, `language_id="fr"`/`"zh"`, `example_tts.py` pointer); `Single Language Pack` table (6 finetune model cards plus demo Spaces); `Acknowledgements` (Cosyvoice, HiFT-GAN, Llama 3); `Built-in PerTh Watermarking` section; `Disclaimer`.

[^chatterbox-repo]: [Chatterbox TTS GitHub repository README](../raw/chatterbox-repo.md) — locators: `Latest Release: Chatterbox Multilingual V3` section (V3 same 0.5B size, speaker-similarity, hallucination reduction, Single Language Pack intro, Turbo 350M plus one-step distilled decoder, Nano 110M plus 3x realtime on 8 CPU cores, paralinguistic tags, sub-200 ms service sentence); `Model Zoo` table (5 rows: Turbo 350M English, Nano 110M English, Multilingual V3 500M 23+, Single Language Pack, Chatterbox 500M English); `Installation` fences (`pip install chatterbox-tts`, `git clone https://github.com/resemble-ai/chatterbox.git` plus `pip install -e .`, Python 3.11 on Debian 11, `pyproject.toml` pins); `Usage` fences (`chatterbox.tts_turbo.ChatterboxTurboTTS.from_pretrained` with `nano=True`, `generate` with `audio_prompt_path`, `ChatterboxTTS`/`ChatterboxMultilingualTTS` with `t3_model="v3"`/`"v2"`, `language_id="fr"`/`"zh"`, `example_tts.py`/`example_tts_turbo.py`/`example_tts_nano.py`/`example_vc.py` pointers); `Supported Languages` list (23 codes ar–zh); `Single Language Pack` table (6 finetune model cards plus demo Spaces); `Original Chatterbox Tips` (defaults `exaggeration=0.5`/`cfg_weight=0.5`, fast-speaker 0.3, expressive 0.3 plus 0.7+, accent/CFG-0 note); `Built-in PerTh Watermarking` plus `Watermark extraction` fence (`perth.PerthImplicitWatermarker().get_watermark`, `0.0`/`1.0`); `Evaluation` (Podonos preference/naturalness/expressiveness; Turbo vs ElevenLabs Turbo v2.5, Cartesia Sonic 3, VibeVoice 7B); `Acknowledgements` (Podonos, Cosyvoice, Real-Time-Voice-Cloning, HiFT-GAN, Llama 3, S3Tokenizer); `Citation` (`@misc{chatterboxtts2025}`); `Disclaimer`.
