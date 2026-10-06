---
type: Concept
title: Fun-ASR-MLT-Nano-2512
description: 800M-parameter multilingual ASR checkpoint covering 31 languages with East and Southeast Asian focus, FunASR inference with hotwords and ITN, and family-level benchmark context.
tags: [ml, asr, multilingual, speech-recognition]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: fun-asr-mlt-nano-card
    resource: ../raw/Fun-ASR-MLT-Nano-2512.md
    kind: documentation
    title: Fun-ASR-MLT-Nano-2512 model card
---

Fun-ASR-MLT-Nano-2512 is the 800M-parameter multilingual checkpoint in the Fun-ASR family from FunAudioLLM, trained on hundreds of thousands of hours of speech and covering 31 languages with emphasis on East and Southeast Asian languages, run through the FunASR inference API with language selection plus hotword and ITN controls (**Reported**).[^fun-asr-mlt-nano-card]

## Model identity and family

- Card title is `Fun-ASR-MLT-Nano-2512`; ecosystem is FunASR / FunAudioLLM (`FunASR`, `SenseVoice`, `Fun-ASR`, `FunClip`); model repositories are ModelScope `FunAudioLLM/Fun-ASR-MLT-Nano-2512` and Hugging Face `FunAudioLLM/Fun-ASR-MLT-Nano-2512`; frontmatter declares `library_name: funasr`, `pipeline_tag: automatic-speech-recognition`, `license: apache-2.0`, and tags including `speech-recognition`, `asr`, `multilingual`, `31-languages`, `end-to-end`, `streaming`, `whisper-alternative`, `real-time`, and `vllm` (**Reported**, with frontmatter fields **Observed** by static inspection).[^fun-asr-mlt-nano-card]
- Release note dates the MLT checkpoint to 2025/12; the companion FunASR toolkit note dates to 2024/7 and covers ASR, VAD, punctuation restoration, language models, speaker verification, speaker diarization, and multi-talker ASR (**Reported**).[^fun-asr-mlt-nano-card]
- Family table contrasts two 800M checkpoints: `Fun-ASR-Nano` trained on tens of millions of hours for Chinese, English, and Japanese (Chinese covers 7 dialects — Wu, Cantonese, Min, Hakka, Gan, Xiang, Jin — plus 26 regional accents including Henan, Shanxi, Hubei, Sichuan, Chongqing, Yunnan, Guizhou, Guangdong, Guangxi; English and Japanese cover multiple regional accents; plus lyric and rap recognition) versus `Fun-ASR-MLT-Nano` trained on hundreds of thousands of hours for 31 languages (**Reported**).[^fun-asr-mlt-nano-card]
- Homepage, Core Features, Performance Evaluation, Environment Setup, and Usage Tutorial navigation is listed; this repository hosts the MLT checkpoint and its supported-language scope differs from the standard Fun-ASR-Nano checkpoint (**Reported**).[^fun-asr-mlt-nano-card]

## Supported languages

31 languages total: Chinese, English, Cantonese, Japanese, Korean, Vietnamese, Indonesian, Thai, Malay, Filipino, Arabic, Hindi, Bulgarian, Croatian, Czech, Danish, Dutch, Estonian, Finnish, Greek, Hungarian, Irish, Latvian, Lithuanian, Maltese, Polish, Portuguese, Romanian, Slovak, Slovenian, and Swedish (**Reported**).[^fun-asr-mlt-nano-card]

## Core features

- Compact multilingual model with approximately 800M parameters (**Reported**).[^fun-asr-mlt-nano-card]
- Focused optimization on East and Southeast Asian languages (**Reported**).[^fun-asr-mlt-nano-card]
- Language control accepts the language names shown in the inference example and supports multilingual recognition; the example uses `language="中文"` (**Reported**).[^fun-asr-mlt-nano-card]
- Context controls: the FunASR inference API exposes hotwords (example `hotwords=["开放时间"]`) and inverse text normalization via `itn=True` or `False` (**Reported**).[^fun-asr-mlt-nano-card]

## Environment setup

- Requires `python -m pip install -U "funasr>=1.4.1"` (**Reported**).[^fun-asr-mlt-nano-card]
- Optional local demo: `git clone https://github.com/FunAudioLLM/Fun-ASR.git`, then `cd Fun-ASR` and `python -m pip install -r requirements.txt` (**Reported**).[^fun-asr-mlt-nano-card]

## Inference

- `AutoModel` path loads `model="FunAudioLLM/Fun-ASR-MLT-Nano-2512"` with `hub="hf"`, `trust_remote_code=True`, `remote_code="./model.py"`, `device="cuda:0"`, then calls `model.generate(input=[wav_path], cache={}, batch_size=1, hotwords=..., language="中文", itn=True, llm_kwargs={"do_sample": False})` and reads `res[0]["text"]`, where `wav_path` is `f"{model.model_path}/example/zh.mp3"` (**Reported**).[^fun-asr-mlt-nano-card]
- VAD-segmented variant uses the same loader plus `vad_model="fsmn-vad"` and `vad_kwargs={"max_single_segment_time": 30000}`, then `generate` with `language="中文"` and `llm_kwargs={"do_sample": False}` (**Reported**).[^fun-asr-mlt-nano-card]
- Direct-inference path uses `from model import FunASRNano`, then `FunASRNano.from_pretrained(model=model_dir, hub="hf", device="cuda:0")`, `m.eval()`, sets `kwargs["llm_kwargs"] = {"do_sample": False}`, and calls `m.inference(data_in=[wav_path], **kwargs)` with `wav_path` from `kwargs['model_path']/example/zh.mp3`, reading `res[0][0]["text"]` (**Reported**).[^fun-asr-mlt-nano-card]
- Documented parameters: `model_dir` (model name or local path), `trust_remote_code` (whether to trust remote code for custom model implementations), `remote_code` (location of model code such as `model.py`, absolute or relative), `device` (for example `cuda:0` or `cpu`) (**Reported**).[^fun-asr-mlt-nano-card]

## TODO and unsupported features

- Returning timestamps, speaker diarization, and model training are listed as unchecked TODO items, so they are not supported by this checkpoint documentation (**Reported**).[^fun-asr-mlt-nano-card]

## Performance

- Benchmark scope limit: the tables below are Fun-ASR family results reproduced from the project report; they do not contain a column identified as `Fun-ASR-MLT-Nano-2512`, so they must not be interpreted as checkpoint-specific results for this MLT model; MLT per-language results will be added when a reproducible evaluation is published (**Reported**).[^fun-asr-mlt-nano-card]
- Open-source WER results (%, lower is better) are family-level comparisons across open-source benchmarks; columns `Fun-ASR-nano` (0.8B) and `Fun-ASR` (7.7B) are included for context, not as MLT claims (**Reported**):[^fun-asr-mlt-nano-card]

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

- Industry WER results (%, lower is better) are family-level comparisons across industry test sets; same non-attribution to MLT applies (**Reported**):[^fun-asr-mlt-nano-card]

| Test set | GLM-ASR-Nano | Whisper-large-v3 | Seed-ASR | FireRed-ASR | Kimi-Audio | Paraformer v2 | Fun-ASR-nano | Fun-ASR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Model Size | 1.5B | 1.6B | - | 1.1B | 8B | 0.2B | 0.8B | 7.7B |
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

- `Seed-ASR*` results are evaluated using the official API on volcengine; `GLM-ASR-nano*` results are evaluated using the open-source checkpoint (**Reported**).[^fun-asr-mlt-nano-card]
- Technical-report citation is `an2025fun`, `Fun-ASR Technical Report`, `arXiv:2509.12508`, 2025 (**Reported**).[^fun-asr-mlt-nano-card]

## Coverage and limits

- Source inspected statically only; no code executed, no audio transcribed, and no WER figures reproduced (**Synthesis**).[^fun-asr-mlt-nano-card]
- Linked but unfetched and not in `raw/`: `README_zh.md`, `images/funasr-v2.png`, `images/compare_en.png`, ModelScope and Hugging Face repositories, `FunASR` / `SenseVoice` / `Fun-ASR` / `FunClip` GitHub projects, the `Fun-ASR-Nano-2512` checkpoint, `example/zh.mp3`, `model.py` (`remote_code`), `requirements.txt`, and arXiv 2509.12508; benchmark figure `compare_en.png` was not inspected (**Synthesis**).[^fun-asr-mlt-nano-card]
- All identity, language-coverage, training-data-scale, usage, and accuracy claims are source assertions without independent verification in this wiki; the performance tables must be reused only as Fun-ASR family context, not as MLT checkpoint results (**Synthesis**).[^fun-asr-mlt-nano-card]

[^fun-asr-mlt-nano-card]: [Fun-ASR-MLT-Nano-2512 model card](../raw/Fun-ASR-MLT-Nano-2512.md) — locators: frontmatter (`language`, `license`, `library_name`, `pipeline_tag`, `tags`); header FunASR ecosystem banner; title `Fun-ASR-MLT-Nano-2512` intro paragraph (800M, hundreds of thousands of hours, 31 languages, East/Southeast Asia focus; pointer to Fun-ASR-Nano-2512); model table (Nano vs MLT-Nano rows: tasks, dialects/accents/lyrics/rap detail, training-data scales, 800M params); section `What's New` (2025/12 MLT entry; 2024/7 FunASR toolkit entry); section `Core Features` (MLT scope note; 31 languages; 800M; language-control and hotword/ITN bullets); section `Environment Setup` (`funasr>=1.4.1` install; `Fun-ASR` clone + `requirements.txt`); section `TODO` (timestamps, diarization, training checkboxes); section `Usage / Inference` (two `AutoModel` code fences with `model_dir`, `hub`, `trust_remote_code`, `remote_code`, `device`, `example/zh.mp3`, `hotwords`, 31-language `language` comment, `itn`, `llm_kwargs`, `fsmn-vad` + `max_single_segment_time`; `FunASRNano` direct-inference fence); `Parameter Description` (`model_dir`, `trust_remote_code`, `remote_code`, `device`); section `Performance` scope blockquote plus open-source WER table (10 columns, 8 test sets) and industry WER table (8 columns, 10 test sets + average) with `Seed-ASR*` / `GLM-ASR-nano*` note and `compare_en.png` figure; section `Citations` (`an2025fun`, arXiv:2509.12508).
