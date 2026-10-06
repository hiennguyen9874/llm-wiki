---
type: Concept
title: Hojo-ASR-V1
description: 4B-scale conversational ASR model with Encoder-Adapter-Qwen3-LLM architecture and multi-frame acoustic fusion, covering Mandarin, English, Cantonese, and Sichuan dialect with reported English WER table and hojo-asr batch inference.
tags: [stt, asr, speech-recognition, multilingual, chinese-dialects]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T15:00:00Z }
stale_after: 2027-10-06
sources:
  - id: hojo-asr-v1-doc
    resource: ../raw/Hojo-ASR-V1.md
    kind: documentation
    title: Hojo-ASR-V1 model card
---

Hojo-ASR-V1 is a 4B-scale high-performance conversational speech recognition model using an Encoder-Adapter-LLM framework with a Qwen3 LLM decoder and customized multi-frame acoustic fusion, trained with multi-stage modular training plus reinforcement learning for noisy environments, informal pronunciation, oral correction, and Chinese-English code-switching, and supporting Mandarin, English, Cantonese, and Sichuan dialect for industrial deployment (**Reported**).[^hojo-asr-v1-doc]

## Architecture and training

- Classic Encoder-Adapter-LLM framework with a customized multi-frame acoustic fusion architecture, stated to combine fine-grained acoustic features with LLM semantic capability; the LLM decoder is Qwen3 (**Reported**).[^hojo-asr-v1-doc]
- Optimized with multi-stage modular training and reinforcement learning; positioned as balancing accuracy and inference efficiency for industrial deployment (**Reported**).[^hojo-asr-v1-doc]
- Design focus is complex real-world scenarios: noisy environments, informal pronunciation, oral correction, and Chinese-English code-switching (**Reported**).[^hojo-asr-v1-doc]

## Supported languages

Mandarin, English, Cantonese, and Sichuan dialect (**Reported**).[^hojo-asr-v1-doc] Multi-lingual and multi-dialect support beyond this set is roadmap work, not a current claim (**Reported**).[^hojo-asr-v1-doc]

## Performance

Public English-dataset WER table for Hojo-ASR 4B, lower is better (**Reported**).[^hojo-asr-v1-doc]

| Dataset | Hojo-ASR 4B WER |
| --- | ---: |
| AMI | 8.64 |
| Earnings22 | 8.54 |
| Gigaspeech | 7.6 |
| LibriSpeech Clean | 1.74 |
| LibriSpeech Other | 3.66 |
| SPGISpeech | 1.92 |
| Tedlium | 3.13 |
| Voxpopuli | 7.02 |

- The arithmetic mean of the eight cells above is 5.28 (*computed*, **Synthesis**); the card prints no average, protocol, decoding, normalization, or hardware detail, so rank comparisons against 7-split Open ASR Leaderboard averages in this wiki (e.g. [ARK-ASR-3B](ark-asr-3b.md)) should not drive a decision on their own (**Synthesis**).[^hojo-asr-v1-doc]

## Inference

- Install path is the `hojo-asr` Python package from PyPI with a `conda create -n hojo-asr python=3.10` environment and `pip install -U hojo-asr` for transformers-backend support (**Reported**).[^hojo-asr-v1-doc]
- Usage loads a local checkpoint with `HOJO_ASR.load_model("/path/to/model_folder", device=args.device)` (`--device` default `cuda:0`, `--batch_size` default `10`) and transcribes via `model.run_infer(...)`, which accepts a wav-path scp file (`str`), a list of wav paths, or a list of wav byte strings, and returns per-utterance dicts with `key` and `text` fields (**Reported**).[^hojo-asr-v1-doc]
- No streaming/chunking knob, timestamp, punctuation, hotword, diarization, or serving (vLLM/SGLang/server) claim appears in this card (**Synthesis**).[^hojo-asr-v1-doc]

## Release, license, and support

- Roadmap state: Hojo-ASR-4B model plus inference engine released and four-language/dialect support checked; broader multi-lingual and multi-dialect support unchecked (**Reported**).[^hojo-asr-v1-doc]
- Card frontmatter declares `license: apache-2.0` with `language: [zh, en]`, and the Licence section states the project is open-sourced under Apache 2.0 for academic, personal, and commercial secondary development (**Reported**, with frontmatter fields **Observed** by static inspection).[^hojo-asr-v1-doc]
- Commercial support (integration assistance, custom voice development, enterprise licensing) is offered via `developer@hojoai.com` (**Reported**).[^hojo-asr-v1-doc]
- Credits name [Qwen](https://huggingface.co/Qwen), WenetSpeech-Yue, and WenetSpeech-Chuan as upstream open-source works (**Reported**).[^hojo-asr-v1-doc]

## Relationships

- Shares the Qwen-decoder ASR family with [Qwen3-ASR family](qwen3-asr-family.md) and [ARK-ASR-3B](ark-asr-3b.md): Hojo-ASR-V1 pairs an audio encoder/adapter with a Qwen3 LLM decoder the way ARK-ASR pairs a Whisper-style encoder and MLP adapter with a Qwen decoder, but Hojo-ASR-V1's distinguishing card claims are multi-frame acoustic fusion, RL optimization, and oral-correction plus code-switching robustness (**Synthesis**).[^hojo-asr-v1-doc]
- Dialect-overlap comparison with [Fun-ASR-Nano-2512](fun-asr-nano-2512.md) (7 dialects, 26 accents) and [GLM-ASR-Nano-2512](glm-asr-nano-2512.md) (Cantonese plus dialect optimization): Hojo-ASR-V1's concrete dialect claim is Cantonese and Sichuan dialect, narrower than Fun-ASR-Nano's set, with no shared numeric benchmark in this card (**Synthesis**).[^hojo-asr-v1-doc]

## Coverage and limits

- Source inspected statically only; no package installed, no model downloaded, no audio transcribed, and no WER or robustness claim reproduced (**Synthesis**).[^hojo-asr-v1-doc]
- Material gaps in the card: no model URL or checkpoint identifier, no release date or revision, no encoder/adapter parameter detail beyond 4B scale, no training data or compute, no Chinese/dialect/code-switching numbers despite the positioning, no streaming, latency, RTFx, or edge-packaging detail, and no evaluation protocol for the English table; all accuracy and robustness claims are source assertions without independent verification in this wiki (**Synthesis**).[^hojo-asr-v1-doc]
- Linked but unfetched and not in `raw/`: `LICENSE.txt`, the `hojo-asr` PyPI package, the `/path/to/model_folder` checkpoint, the Qwen and WenetSpeech-Yue/Chuan upstream links, and the commercial-support contact; `LICENSE.txt` absence means the Apache-2.0 grant is frontmatter-plus-text only here; model-release and benchmark details carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^hojo-asr-v1-doc]

[^hojo-asr-v1-doc]: [Hojo-ASR-V1 model card](../raw/Hojo-ASR-V1.md) — locators: frontmatter (`license: apache-2.0`, `language: [zh, en]`); section `Overview > Introduction` (Qwen3 LLM decoder, Encoder-Adapter-LLM framework, multi-frame acoustic fusion, multi-stage modular training plus reinforcement learning, noisy/informal-pronunciation/oral-correction/code-switching focus, Mandarin/English/Cantonese/Sichuan support, accuracy-efficiency balance); section `Quickstart > Environment Setup` (`conda create -n hojo-asr python=3.10`, `pip install -U hojo-asr`); section `Quickstart > Sample Usage` (`HOJO_ASR.load_model`, `run_infer` with `wav_scp`/`wav_paths`/`wav_bytes_list`, `batch_size`/`device` defaults, `key`/`text` output loop); section `Evaluation` (8-cell English WER table for Hojo-ASR 4B); section `Roadmap` (4B plus inference engine and 4-language support checked, multi-lingual/multi-dialect unchecked); sections `Commercial Support` (`developer@hojoai.com`), `Credits` (Qwen, WenetSpeech-Yue, WenetSpeech-Chuan), `Licence` (Apache 2.0 statement).
