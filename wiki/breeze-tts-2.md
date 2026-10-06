---
type: Concept
title: Breeze TTS 2
description: Open-weight bilingual English-Chinese real-time TTS model with voice clone, reference-free voice design, reference-guided voice direction, inline vocal events, and sub-40 ms TTFA streaming on H100.
tags: [ml, tts, bilingual, voice-cloning, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T15:00:00Z }
stale_after: 2027-10-06
sources:
  - id: breeze-tts-2-card
    resource: ../raw/Breeze-TTS-2.md
    kind: documentation
    title: Breeze TTS 2 model card
---

Breeze TTS 2 is an open-weight bilingual (English and Chinese) text-to-speech model built for real-time interaction, ranking #1 among open-weight models on the Artificial Analysis TTS leaderboard, with voice clone, reference-free voice design, reference-guided voice direction, inline vocal events, under 40 ms time to first audio and 0.32 real-time factor on a warmed-up fast path on NVIDIA H100, and eager inference at about 7.7 GiB GPU memory (**Reported**).[^breeze-tts-2-card]

## Model identity and release

- Title is `Breeze TTS 2`; creator is BreezeBlue; model weights are `BreezeBlue/breeze-tts-2` on Hugging Face; inference code is `https://github.com/breezeblue-ai/breeze-tts`; frontmatter declares `library_name: transformers`, `pipeline_tag: text-to-speech`, languages `en, zh`, license `other` named `breezeblue-research-and-non-commercial-license`, and tags including `text-to-speech`, `speech-generation`, `voice-clone`, `voice-design`, `voice-direction`, `pytorch`, and `cuda` (**Reported**).[^breeze-tts-2-card]
- News entries record benchmark-suite releases on 2026.08.07 for voice design, voice direction, and latency evaluation, and model-weights plus PyTorch inference-code release on 2026.08.25 (**Reported**).[^breeze-tts-2-card]
- Source code is licensed under Apache 2.0; the audio tokenizer is based on Qwen3-TTS by the Alibaba Qwen Team under Apache 2.0; model weights, checkpoints, adapters, derivative models, and self-hosted outputs are governed by the BreezeBlue Research and Non-Commercial License; the Apache License grants no commercial rights to the model; commercial use of outputs applies only to outputs generated through BreezeBlue's hosted platform or API under an active paid subscription subject to its Terms of Service (**Reported**).[^breeze-tts-2-card]
- Unauthorized voice cloning, impersonation, fraud, and other unlawful or harmful uses are prohibited; users are responsible for applicable laws and for rights and consents for inputs, reference audio, voices, and outputs; code and Model Materials are provided "AS IS" without warranties or liability to the maximum extent permitted by law (**Reported**).[^breeze-tts-2-card]

## Capabilities

- Voice Clone uses reference audio with its exact transcript to preserve timbre, rhythm, emotion, and style; reference audio should contain clean speech with minimal background noise (**Reported**).[^breeze-tts-2-card]
- Voice Design creates a distinctive voice from a natural-language description without reference audio; the instruction language should match the target text; `--cfg-scale 4` strengthens instruction-following (**Reported**).[^breeze-tts-2-card]
- Voice Direction clones a voice from reference audio while steering tone, emotion, pace, and delivery via a natural-language instruction; `--cfg-scale 4` strengthens instruction-following (**Reported**).[^breeze-tts-2-card]
- Vocal Events add expressive inline events directly in the text: parentheses in English such as `(laugh)`, `(cough)`, `(clears throat)`, `(sigh)`; square brackets in Chinese such as `[笑]`, `[咳嗽]`, `[清嗓子]`, `[叹气]` (**Reported**).[^breeze-tts-2-card]
- Bilingual support generates natural English and Chinese speech with a single model (**Reported**).[^breeze-tts-2-card]

## Performance and efficiency

- Ultra-low latency achieves under 40 ms time to first audio (TTFA) with the warmed-up fast path on an NVIDIA H100 (**Reported**).[^breeze-tts-2-card]
- Real-time streaming reaches a 0.32 real-time factor (RTF), generating audio at approximately 3.1× real time with the warmed-up fast path on an NVIDIA H100 (**Reported**).[^breeze-tts-2-card]
- GPU-efficient eager inference uses approximately 7.7 GiB of GPU memory; 12 GB GPU is the minimum recommended configuration; with `--fast-all` memory is approximately 14.4 GiB, so a 24 GB GPU is recommended for the fast path (**Reported**).[^breeze-tts-2-card]

## Requirements and installation

- Requires Linux, Python 3.10 or newer, a CUDA-capable NVIDIA GPU, the Breeze TTS 2 checkpoint with all required model components included, and approximately 7.7 GiB GPU memory for eager inference or 14.4 GiB with `--fast-all` (**Reported**).[^breeze-tts-2-card]
- Install by cloning `https://github.com/breezeblue-ai/breeze-tts`, then `python -m pip install -r requirements.txt`; for the tested CUDA environment build the included Docker image with `bash docker/build.sh`, defaulting to H100/Hopper (sm90), or `FLASH_ATTN_CUDA_ARCHS=80 bash docker/build.sh` for A100 (**Reported**).[^breeze-tts-2-card]

## Inference usage

- Voice Clone CLI passes `--ref-audio` and `--ref-text` (exact transcript) with `--text` and `--output`; English and Chinese examples use `(sigh)` and `[叹气]` vocal events respectively (**Reported**).[^breeze-tts-2-card]
- Voice Design CLI passes `--text` with `--instruction` and `--cfg-scale 4`, without reference audio; English example instruction is "A warm, thoughtful young woman with a clear voice and a calm, reflective delivery." and Chinese example instruction is "一位温柔自信的年轻女性，声音清晰，语气亲切，表达轻快而富有感染力。" (**Reported**).[^breeze-tts-2-card]
- Voice Direction CLI passes `--ref-audio`, `--ref-text`, `--text`, `--instruction` (e.g. "Speak slowly with a restrained, serious tone."), and `--cfg-scale 4` (**Reported**).[^breeze-tts-2-card]
- Streaming API starts a single-concurrency server with `python -m breeze_infer.api ../breeze-tts-2 --host 0.0.0.0 --port 7860` using the same PyTorch runtime and eager execution by default; a Voice Direction request posts multipart fields `cfg_scale`, `ref_audio`, `ref_text`, `text`, `instruction`, and `seed` to `/v1/audio/speech`; the response is streaming mono 24 kHz signed 16-bit little-endian PCM; starting the API with `--fast-all` enables the fast path (**Reported**).[^breeze-tts-2-card]
- Both CLI and API use eager streaming by default and skip graph warmup; `--fast-all` enables the best configuration for every inference stage when the additional cold-start time is acceptable; per-stage flags `--[no-]fast-text-encoder`, `--[no-]fast-backbone-prefill`, `--[no-]fast-backbone-decode`, `--[no-]fast-depth-decoder`, and `--[no-]fast-codec` select between native eager forwards and CUDA-graph or compiled variants, and are intended for profiling and debugging (**Reported**).[^breeze-tts-2-card]

## Relationships

- Uses Qwen3-TTS audio tokenizer: the audio tokenizer is based on [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS) by the Alibaba Qwen Team under Apache 2.0; for the Qwen3-TTS CustomVoice family member see [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md) (**Synthesis**).[^breeze-tts-2-card]
- TTS voice-cloning comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a compact multilingual zero-shot voice-cloning TTS model with DualAR architecture and ONNX/SGLang serving paths, while this concept covers a bilingual real-time TTS model with voice design and voice direction instruction-following plus H100 streaming latency figures; no shared codebase or vendor claim is asserted (**Synthesis**).[^breeze-tts-2-card]

## Coverage and limits

- Source inspected statically only; no code cloned or executed, no Docker image built, no checkpoint downloaded, no audio synthesized, and no TTFA, RTF, memory-footprint, leaderboard-rank, or instruction-following claims reproduced (**Synthesis**).[^breeze-tts-2-card]
- Leaderboard SVG figure, logo asset, Hugging Face checkpoint, GitHub inference repository, benchmark-suite repositories, hosted platform and API, and license/terms pages were linked but not fetched and were not present in `raw/`; checkpoint contents, tokenizer weights, reference-audio files, and Docker build contents were not inspected (**Synthesis**).[^breeze-tts-2-card]
- All ranking, capability, latency, throughput, memory, compatibility, and usage claims are source assertions without independent verification in this wiki (**Synthesis**).[^breeze-tts-2-card]

[^breeze-tts-2-card]: [Breeze TTS 2 model card](../raw/Breeze-TTS-2.md) — locators: frontmatter (`language`, `library_name`, `pipeline_tag`, `license`, `tags`); `IMPORTANT` license callout; `News` section (2026.08.25 weights/inference-code release, 2026.08.07 benchmark-suite releases); `Introduction` section (real-time interaction, #1 open-weight Artificial Analysis ranking, instruction-following, TTFA/streaming claims); `Highlights` section (voice clone/design/direction bullets, vocal-events syntax, TTFA 40 ms, RTF 0.32, 7.7 GiB memory, bilingual bullets); `Quick Start / Requirements` section (Linux, Python 3.10+, CUDA GPU, 7.7/14.4 GiB memory, checkpoint paragraph); `Installation` section (git-clone fence, pip-install fence, Docker `build.sh` fences including `FLASH_ATTN_CUDA_ARCHS=80`); Voice Clone/Design/Direction subsections (CLI fences with `--ref-audio`/`--ref-text`/`--text`/`--instruction`/`--cfg-scale`/`--output`, vocal-event examples); `Streaming API` section (server-start fence, curl multipart fence, PCM format paragraph, `--fast-all` sentence); `Fast Inference Options` section (eager-default paragraph, 5-row stage table); `License and Responsible Use` section (Apache 2.0 code, Qwen3-TTS tokenizer attribution, non-commercial weights/outputs, paid-subscription hosted-output terms, consent/prohibition paragraph, AS-IS paragraph).
