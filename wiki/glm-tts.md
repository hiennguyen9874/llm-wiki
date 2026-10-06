---
type: Concept
title: GLM-TTS
description: Zero-shot bilingual Chinese-English TTS system with LLM plus flow-matching synthesis, multi-reward GRPO emotion control, phoneme-level pronunciation control, and streaming inference.
tags: [ml, tts, voice-cloning, streaming, bilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:06:16Z }
stale_after: 2027-10-06
sources:
  - id: glm-tts-readme
    resource: ../raw/GLM-TTS.md
    kind: documentation
    title: GLM-TTS README and model card
---

GLM-TTS is zai-org's open-source large-language-model text-to-speech system for controllable, emotion-expressive zero-shot voice cloning, released with base and RL checkpoints that the source presents as reaching the lowest Character Error Rate (CER) on `seed-tts-eval` while supporting 3–10 second prompt cloning, hybrid phoneme-plus-text pronunciation control, and streaming inference for Chinese-English mixed text (**Reported**).[^glm-tts-readme]

## Model identity and release

- Name is GLM-TTS; publisher is zai-org (`github.com/zai-org/GLM-TTS`); header links list the paper `arXiv:2512.14291`, GitHub repository, and `audio.z.ai` demo; frontmatter declares languages `zh, en`, `pipeline_tag: text-to-speech`, `library_name: glm-tts`, license `mit`, and tags `llm, tts, zero-shot, voice-cloning, reinforcement-learning, flow-matching` (**Reported**, with frontmatter fields **Observed** by static inspection).[^glm-tts-readme]
- Technical-report citation is `cui2025glmttstechnicalreport`, titled `GLM-TTS Technical Report` by Jiayan Cui, Zhihan Yang, Naihan Li, Jiankun Tian, Xingyu Ma, Yi Zhang, Guangyu Chen, Runxuan Yang, Yuqing Cheng, Yizhi Zhou, Guochen Yu, Xiaotao Gu, and Jie Tang, year 2025, `eprint 2512.14291`, `primaryClass cs.SD` (**Reported**).[^glm-tts-readme]
- Family context credits CosyVoice (frontend processing framework and vocoder), Llama (base language-model architecture), Vocos (vocoder), and GRPO-Zero (RL algorithm inspiration); no shared weights or training-data claim beyond these acknowledged code/architecture sources is asserted (**Reported**).[^glm-tts-readme]

## Architecture and controllability

- Two-stage design: Stage 1 is a Llama-based model converting input text into speech token sequences; Stage 2 is a Flow Matching model converting token sequences into mel-spectrograms, then into waveforms via a vocoder (**Reported**).[^glm-tts-readme]
- Reinforcement-learning alignment uses Group Relative Policy Optimization (GRPO) with multiple reward functions — Similarity, CER, Emotion, and Laughter — to counter flat emotional expression and align the LLM generation strategy toward more natural prosody and emotion control (**Reported**).[^glm-tts-readme]
- Zero-shot voice cloning needs only 3–10 seconds of prompt audio for any speaker (**Reported**).[^glm-tts-readme]
- Phoneme-level control accepts hybrid phoneme-plus-text input for precise pronunciation (e.g. polyphones), enabled in inference with a `--phoneme` flag (**Reported**).[^glm-tts-readme]
- Streaming inference supports real-time audio generation for interactive applications; no time-to-first-audio, RTF, chunk-size, or hardware figures are given in the source (**Reported**, with the missing-latency qualifier **Synthesis**).[^glm-tts-readme]
- Bilingual support is optimized for Chinese and English mixed text; no additional language list, dialect list, sample rate, or parameter count is given in the source (**Reported**).[^glm-tts-readme]

## Performance and evaluation

- Evaluated on `seed-tts-eval`; the source presents GLM-TTS_RL as achieving the lowest CER in the table while maintaining high speaker similarity (**Reported**).[^glm-tts-readme]
- Table rows: Seed-TTS CER 1.12 with SIM 79.6 (closed-source); CosyVoice2 CER 1.38 with SIM 75.7 (open-source); F5-TTS CER 1.53 with SIM 76.0 (open-source); GLM-TTS Base CER 1.03 with SIM 76.1 (open-source); GLM-TTS_RL CER 0.89 with SIM 76.4 (open-source), the lowest CER in the column (**Reported**, with the column-minimum reading **Observed** by static inspection).[^glm-tts-readme]
- No evaluation protocol, split definitions, hardware, uncertainty, audio samples, or independent verification accompany the table in this source; all benchmark claims are source assertions without independent verification in this wiki (**Synthesis**).[^glm-tts-readme]

## Requirements, installation, and usage

- Installation is `git clone https://github.com/zai-org/GLM-TTS.git`, `cd GLM-TTS`, `pip install -r requirements.txt` (**Reported**).[^glm-tts-readme]
- Command-line inference is `python glmtts_inference.py --data=example_zh --exp_name=_test --use_cache`, with an optional commented `--phoneme` flag for phoneme capabilities; a `bash glmtts_inference.sh` script path is also given (**Reported**).[^glm-tts-readme]
- No Python version, dependency pins, model-download step, checkpoint identifier, configuration keys, or served-API usage are documented in the captured source (**Synthesis**).[^glm-tts-readme]

## Relationships

- TTS architecture comparison: [CosyVoice2-0.5B](cosyvoice2-0.5b.md) covers a 0.5B LLM-based streaming TTS model with saved-speaker reuse and vLLM/TRT-LLM serving mentions, while this concept covers a Llama-plus-flow-matching two-stage system with GRPO multi-reward emotion alignment and hybrid phoneme control; the CosyVoice lineage is an acknowledged frontend/vocoder source, not an asserted shared checkpoint (**Synthesis**).[^glm-tts-readme]
- RL-variant comparison: [Fun-CosyVoice3-0.5B-2512](fun-cosyvoice3-0.5b-2512.md) covers a 0.5B multilingual TTS model with base and RL checkpoints, Pinyin/CMU inpainting, and 150 ms bi-streaming figures, while this concept covers base and RL checkpoints with Similarity/CER/Emotion/Laughter GRPO rewards and a seed-tts-eval CER table; no shared vendor or training data is asserted (**Synthesis**).[^glm-tts-readme]
- Streaming TTS comparison: [Breeze TTS 2](breeze-tts-2.md) covers a bilingual English-Chinese real-time TTS model with voice design/direction and sub-40 ms TTFA figures on H100, while this concept covers a bilingual Chinese-English streaming TTS model with zero-shot cloning and emotion control but no published latency figures; no shared vendor or codebase is asserted (**Synthesis**).[^glm-tts-readme]
- Voice-cloning comparison: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B multilingual zero-shot TTS model with DualAR architecture and ONNX/SGLang paths, while this concept covers a two-stage LLM plus flow-matching model with RL-enhanced expressiveness and phoneme-level control; no shared vendor or codebase is asserted (**Synthesis**).[^glm-tts-readme]

## Coverage and limits

- Source inspected statically only; no repository cloned, no dependencies installed, no checkpoint downloaded, no inference executed, and no CER, speaker-similarity, emotion-control, pronunciation, bilingual-mix, or streaming claims reproduced (**Synthesis**).[^glm-tts-readme]
- Remote architecture diagram (`assets/images/architecture.png`), logo SVG, paper, GitHub repository, `audio.z.ai` demo, `example_zh` data, `glmtts_inference.py` / `glmtts_inference.sh` / `requirements.txt` contents, and acknowledged upstream projects were linked but not fetched and are not in `raw/`; parameter count, checkpoint identifiers, training data, hyperparameters, sample rate, and serving/runtime details are absent from the captured source (**Synthesis**).[^glm-tts-readme]
- All capability, compatibility, serving, and benchmark claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^glm-tts-readme]

[^glm-tts-readme]: [GLM-TTS README and model card](../raw/GLM-TTS.md) — locators: frontmatter (`language`, `tags`, `license`, `pipeline_tag`, `library_name`); title and `Model Introduction` section (two-stage LLM plus Flow Matching design, multi-reward RL expressiveness claim); `Key Features` list (3–10 s cloning, GRPO prosody/emotion, reduced CER, hybrid phoneme-plus-text polyphone control, streaming inference, Chinese-English mixed text); `System Architecture` section (Stage 1 Llama text-to-tokens, Stage 2 Flow tokens-to-mel plus vocoder) and `Reinforcement Learning Alignment` subsection (GRPO with Similarity, CER, Emotion, Laughter rewards); `Evaluation Results` table (`seed-tts-eval`: Seed-TTS 1.12/79.6, CosyVoice2 1.38/75.7, F5-TTS 1.53/76.0, Base 1.03/76.1, RL 0.89/76.4, open-source column); `Quick Start` fences (`git clone`, `pip install -r requirements.txt`, `glmtts_inference.py --data=example_zh --exp_name=_test --use_cache` with commented `--phoneme`, `glmtts_inference.sh`); `Acknowledgments & Citation` section (CosyVoice, Llama, Vocos, GRPO-Zero credits; `cui2025glmttstechnicalreport` BibTeX with `arXiv:2512.14291`).
