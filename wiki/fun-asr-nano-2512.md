---
type: Concept
title: Fun-ASR-Nano-2512
description: 800M-parameter Chinese/English/Japanese ASR checkpoint with 7 dialects, 26 regional accents, lyric and rap coverage, FunASR inference with hotwords and ITN, and family-level benchmark tables.
tags: [ml, asr, speech-recognition, multilingual, chinese-dialects]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T07:00:00Z }
stale_after: 2027-10-06
sources:
  - id: fun-asr-nano-card
    resource: ../raw/Fun-ASR-Nano-2512.md
    kind: documentation
    title: Fun-ASR-Nano-2512 model card
---

Fun-ASR-Nano-2512 is the 800M-parameter Chinese/English/Japanese checkpoint in the Fun-ASR family from Tongyi Lab / FunAudioLLM, trained on tens of millions of hours of real speech for low-latency real-time transcription with dialect, accent, lyric, and rap coverage, run through the FunASR inference API with language selection plus hotword and ITN controls (**Reported**).[^fun-asr-nano-card]

## Model identity and family

- Card title is `Fun-ASR-Nano-2512`; launcher is Tongyi Lab; ecosystem is FunASR / FunAudioLLM (`FunASR`, `SenseVoice`, `Fun-ASR`, `FunClip`); model repositories are ModelScope `FunAudioLLM/Fun-ASR-Nano-2512` and Hugging Face `FunAudioLLM/Fun-ASR-Nano-2512`; online demos are ModelScope and Hugging Face Spaces; frontmatter declares `library_name: funasr`, `pipeline_tag: automatic-speech-recognition`, `license: apache-2.0`, `datasets: custom`, and tags including `speech-recognition`, `asr`, `end-to-end`, `multilingual`, `chinese`, `dialects`, `streaming`, `speaker-diarization`, `timestamps`, `hotwords`, `whisper-alternative`, `vllm`, and `real-time` (**Reported**, with frontmatter fields **Observed** by static inspection).[^fun-asr-nano-card]
- Release note dates this checkpoint to 2025/12 as an end-to-end large model trained on tens of millions of hours of real speech with contextual understanding and industry adaptability; the companion FunASR toolkit note dates to 2024/7 and covers ASR, VAD, punctuation restoration, language models, speaker verification, speaker diarization, and multi-talker ASR (**Reported**).[^fun-asr-nano-card]
- Family table contrasts two 800M checkpoints: `Fun-ASR-Nano` (tens of millions of hours; Chinese, English, Japanese; lyric and rap recognition) versus `Fun-ASR-MLT-Nano` (hundreds of thousands of hours; 31 languages) — for the MLT sibling see [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md) (**Reported**).[^fun-asr-nano-card]
- CPU/edge pointer: the header banner offers a self-contained binary via llama.cpp / GGUF (whisper.cpp-style) with built-in VAD, no GPU or Python required, linking prebuilt binaries, a one-command model download (`Fun-ASR-Nano-GGUF`), a `runtime/llama.cpp` path, and a setup guide; the GGUF runtime packaging is compiled separately in [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md) (**Reported**).[^fun-asr-nano-card]

## Supported languages, dialects, and accents

- `Fun-ASR-Nano` scope in the model table is Chinese, English, and Japanese; Chinese covers 7 dialects (Wu, Cantonese, Min, Hakka, Gan, Xiang, Jin) and 26 regional accents (Henan, Shanxi, Hubei, Sichuan, Chongqing, Yunnan, Guizhou, Guangdong, Guangxi and more than 20 other regions); English and Japanese cover multiple regional accents; lyric recognition and rap-speech recognition are listed as additional features (**Reported**).[^fun-asr-nano-card]
- Scope-limit note: the card intro and `What's New` entry state low-latency real-time transcription covering 31 languages, while the model table scopes `Fun-ASR-Nano` to Chinese/English/Japanese and assigns the 31-language list to `Fun-ASR-MLT-Nano`; reuse the table-level scope for this checkpoint and treat the 31-language sentence as family-level wording (**Synthesis**).[^fun-asr-nano-card]
- Inference language control uses names such as `中文`, `英文`, `日文` for this checkpoint; the code comment lists the extended 31-language names only for `Fun-ASR-MLT-Nano-2512` (**Reported**).[^fun-asr-nano-card]

## Core features

- Far-field high-noise recognition: optimized for far-distance pickup and high-noise scenarios (conference rooms, in-vehicle, industrial sites), stated at 93% recognition accuracy (**Reported**).[^fun-asr-nano-card]
- Chinese dialect and accent coverage as listed above (**Reported**).[^fun-asr-nano-card]
- Multi-language free speech: the card claims 31-language recognition with East and Southeast Asian optimization and free language switching plus mixed recognition; per the scope note above, attribute the 31-language list to the MLT sibling and the Chinese/English/Japanese focus to this checkpoint (**Reported**).[^fun-asr-nano-card]
- Music-background lyric recognition: enhanced recognition under music interference for accurate lyric content (**Reported**).[^fun-asr-nano-card]
- Industry positioning: education and finance verticals, professional terminology, and reduced hallucination and language-confusion effects (**Reported**).[^fun-asr-nano-card]

## Environment setup

- `git clone https://github.com/FunAudioLLM/Fun-ASR.git`, then `cd Fun-ASR` and `pip install -r requirements.txt` (**Reported**).[^fun-asr-nano-card]

## Inference

- `AutoModel` path loads `model="FunAudioLLM/Fun-ASR-Nano-2512"` with `hub="hf"`, `trust_remote_code=True`, `device="cuda:0"`, then calls `model.generate(input=[wav_path], cache={}, batch_size=1, hotwords=["开放时间"], language="中文", itn=True)` and reads `res[0]["text"]`, where `wav_path` is `f"{model.model_path}/example/zh.mp3"`; `itn=True` or `False` toggles inverse text normalization (**Reported**).[^fun-asr-nano-card]
- VAD-segmented variant uses the same loader plus `vad_model="funasr/fsmn-vad"` and `vad_kwargs={"max_single_segment_time": 30000}`, then `model.generate(input=[wav_path], cache={}, batch_size=1)` (**Reported**).[^fun-asr-nano-card]
- Direct-inference path uses `from model import FunASRNano`, then `FunASRNano.from_pretrained(model=model_dir, device="cuda:0")`, `m.eval()`, sets `wav_path` from `kwargs['model_path']/example/zh.mp3`, and calls `m.inference(data_in=[wav_path], **kwargs)`, reading `res[0][0]["text"]` (**Reported**).[^fun-asr-nano-card]
- Documented parameters: `model_dir` (model name or local path), `trust_remote_code` (whether to trust remote code for custom model implementations), `remote_code` (location of model code such as `model.py`, absolute or relative), `device` (for example `cuda:0` or `cpu`) (**Reported**).[^fun-asr-nano-card]

## TODO and unsupported features

- Returning timestamps, speaker diarization, and model training are listed as unchecked TODO items, so they are not supported by this checkpoint documentation (**Reported**).[^fun-asr-nano-card]

## Performance

- Open-source WER results (%, lower is better) compare `Fun-ASR-nano` (0.8B) and `Fun-ASR` (7.7B) against GLM-ASR-nano, Whisper-large-v3, Seed-ASR, Kimi-Audio, Step-Audio2, and FireRed-ASR (**Reported**):[^fun-asr-nano-card]

| Test set | GLM-ASR-nano | GLM-ASR-nano* | Whisper-large-v3 | Seed-ASR | Seed-ASR* | Kimi-Audio | Step-Audio2 | FireRed-ASR | Fun-ASR-nano | Fun-ASR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Model Size | 1.5B | 1.5B | 1.6B | - | - | - | - | 1.1B | 0.8B | 7.7B |
| OpenSource | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| AIShell1 | 1.81 | 2.17 | 4.72 | 0.68 | 1.63 | 0.71 | 0.63 | 0.54 | 1.80 | 1.22 |
| AIShell2 | - | 3.47 | 4.68 | 2.27 | 2.76 | 2.86 | 2.10 | 2.58 | 2.75 | 2.39 |
| Fleurs-zh | - | 3.65 | 5.18 | 3.43 | 3.23 | 3.11 | 2.68 | 4.81 | 2.56 | 2.53 |
| Fleurs-en | 5.78 | 6.95 | 6.23 | 9.39 | 9.39 | 6.99 | 3.03 | 10.79 | 5.96 | 4.74 |
| Librispeech-clean | 2.00 | 2.17 | 1.86 | 1.58 | 2.8 | 1.32 | 1.17 | 1.84 | 1.76 | 1.51 |
| Librispeech-other | 4.19 | 4.43 | 3.43 | 2.84 | 5.69 | 2.63 | 2.42 | 4.52 | 4.33 | 3.03 |
| WenetSpeech Meeting | 6.73 | 8.21 | 18.39 | 5.69 | 7.07 | 6.24 | 4.75 | 4.95 | 6.60 | 6.17 |
| WenetSpeech Net | - | 6.33 | 11.89 | 4.66 | 4.84 | 6.45 | 4.67 | 4.94 | 6.01 | 5.46 |

- Industry WER results (%, lower is better) across nearfield, farfield, complex-background, English-general, opensource, dialect, accent, lyrics, and hiphop sets (**Reported**):[^fun-asr-nano-card]

| Test set | GLM-ASR-Nano | Whisper-large-v3 | Seed-ASR | FireRed-ASR | Kimi-Audio | Paraformer v2 | Fun-ASR-nano | Fun-ASR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Model Size | 1.5B | 1.5B | - | 1.1B | 8B | 0.2B | 0.8B | 7.7B |
| OpenSource | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Nearfield | 16.95 | 16.58 | 7.20 | 10.10 | 9.02 | 8.11 | 7.79 | 6.31 |
| Farfield | 9.44 | 22.21 | 4.59 | 7.49 | 10.95 | 9.55 | 5.79 | 4.34 |
| Complex Background | 23.79 | 32.57 | 12.90 | 15.56 | 15.56 | 15.19 | 14.59 | 11.45 |
| English General | 16.47 | 18.56 | 15.65 | 21.62 | 18.12 | 19.48 | 15.28 | 13.73 |
| Opensource | 4.67 | 7.05 | 3.83 | 5.31 | 3.79 | 6.23 | 4.22 | 3.38 |
| Dialect | 54.21 | 66.14 | 29.45 | 52.82 | 71.94 | 41.16 | 28.18 | 15.21 |
| Accent | 19.78 | 36.03 | 10.23 | 14.05 | 27.20 | 17.80 | 12.90 | 10.31 |
| Lyrics | 46.56 | 54.82 | 30.26 | 42.87 | 65.18 | 50.14 | 30.85 | 21.00 |
| Hiphop | 43.32 | 46.56 | 29.46 | 33.88 | 57.25 | 43.79 | 30.87 | 28.58 |
| Average | 26.13 | 33.39 | 15.95 | 22.63 | 31.00 | 23.49 | 16.72 | 12.70 |

- `Seed-ASR*` results are evaluated using the official API on volcengine; `GLM-ASR-nano*` results are evaluated using the open-source checkpoint (**Reported**).[^fun-asr-nano-card]
- Technical-report citation is `an2025fun`, `Fun-ASR Technical Report`, `arXiv:2509.12508`, 2025 (**Reported**).[^fun-asr-nano-card]

## Relationships

- Related to [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md): same 800M Fun-ASR family and inference API, while this concept covers the Chinese/English/Japanese checkpoint with dialect, accent, lyric, and rap focus and the MLT concept covers the 31-language checkpoint; no shared training-data claim beyond the family table is asserted (**Synthesis**).[^fun-asr-nano-card]
- Packaged as [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md): the CPU/edge llama.cpp runtime build (SenseVoice SAN-M encoder plus Qwen3-0.6B decoder, quantized LLM tiers, `llama-funasr-cli` usage) is compiled from the separate GGUF card, not from this checkpoint card (**Synthesis**).[^fun-asr-nano-card]

## Coverage and limits

- Source inspected statically only; no code executed, no audio transcribed, and no WER figures reproduced (**Synthesis**).[^fun-asr-nano-card]
- Linked but unfetched and not in `raw/`: `README_zh.md`, `images/funasr-v2.png`, `images/compare_en.png`, ModelScope and Hugging Face repositories and Spaces, `FunASR` / `SenseVoice` / `Fun-ASR` / `FunClip` GitHub projects, the `Fun-ASR-Nano-GGUF` weight binaries and `runtime/llama.cpp` plus setup guide (the GGUF card itself is in `raw/` and compiled in [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md)), `example/zh.mp3`, `model.py`, `requirements.txt`, and arXiv 2509.12508; benchmark figure `compare_en.png` was not inspected beyond its table reproduction (**Synthesis**).[^fun-asr-nano-card]
- All identity, language-coverage, training-data-scale, usage, and accuracy claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `ml` domain rule (**Synthesis**).[^fun-asr-nano-card]

[^fun-asr-nano-card]: [Fun-ASR-Nano-2512 model card](../raw/Fun-ASR-Nano-2512.md) — locators: frontmatter (`language`, `license`, `library_name`, `pipeline_tag`, `tags`, `datasets`); header FunASR ecosystem banner plus llama.cpp/GGUF CPU-edge pointer (`Fun-ASR-Nano-GGUF`, `runtime/llama.cpp`, guide); title `Fun-ASR` intro paragraph (Tongyi Lab, tens of millions of hours, real-time, 31-language family wording, education/finance, hallucination/language-confusion claims); model table (Nano vs MLT-Nano rows: zh/en/ja scope, 7 dialects, 26 accents, lyric/rap detail, training-data scales, 800M params); section `What's New` (2025/12 Nano entry; 2024/7 FunASR toolkit entry); section `Core Features` (93% far-field/high-noise, dialects/accents, 31-language free-speech wording, lyric background); section `Environment Setup` (`Fun-ASR` clone + `requirements.txt`); section `TODO` (timestamps, diarization, training checkboxes); section `Usage / Inference` (two `AutoModel` fences with `model_dir`, `hub`, `trust_remote_code`, `device`, `example/zh.mp3`, `hotwords=["开放时间"]`, `language="中文"`, `itn`, `fsmn-vad` + `max_single_segment_time`; `FunASRNano` direct-inference fence); `Parameter Description` (`model_dir`, `trust_remote_code`, `remote_code`, `device`); section `Performance` open-source WER table (10 columns, 8 test sets) and industry WER table (8 columns, 10 test sets + average) with `Seed-ASR*` / `GLM-ASR-nano*` note and `compare_en.png` figure; section `Citations` (`an2025fun`, arXiv:2509.12508).
