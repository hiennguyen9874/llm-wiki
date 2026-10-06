---
type: Concept
title: IndexTTS2
description: Autoregressive zero-shot TTS system claiming emotionally expressive and duration-controlled synthesis, released by IndexTeam with paper arXiv:2506.21619 and Hugging Face plus ModelScope weights.
tags: [tts, zero-shot, voice-cloning]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T17:30:00Z }
stale_after: 2027-10-06
sources:
  - id: indextts2-readme
    resource: ../raw/IndexTTS-2.md
    kind: documentation
    title: IndexTTS-2 README fragment
---

IndexTTS2 is IndexTeam's autoregressive zero-shot text-to-speech system whose subtitle claims emotionally expressive and duration-controlled synthesis, documented in the captured fragment only by release identity, upstream links, seven acknowledged projects, and two arXiv citations, with no architecture, parameter, language-coverage, usage, or evaluation detail present (**Reported**, with the missing-detail qualifier **Synthesis**).[^indextts2-readme]

## Model identity and release

- Names appear as `IndexTTS2` in the page heading and `IndexTTS-2` in badges and model links; treat them as aliases for the same release in this fragment (**Observed** by static inspection).[^indextts2-readme]
- Subtitle is `IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech`; the emotionally expressive, duration-controlled, auto-regressive, zero-shot characterization is a source claim with no supporting mechanism or measurement in the fragment (**Reported**).[^indextts2-readme]
- Frontmatter declares `language: [en, zh]` and `pipeline_tag: text-to-speech` (**Observed** by static inspection).[^indextts2-readme]
- Release links point to arXiv `2506.21619`, GitHub `github.com/index-tts/index-tts`, demo `index-tts.github.io/index-tts2.github.io`, Hugging Face `IndexTeam/IndexTTS-2`, and ModelScope `IndexTeam/IndexTTS-2`; the `IndexTeam` publisher namespace is read from the Hugging Face and ModelScope URLs and the `index-tts` GitHub organization (**Observed** by static inspection).[^indextts2-readme]
- No license, version tag, commit revision, parameter count, sample rate, supported-language list beyond frontmatter, or runtime requirement is stated in the fragment (**Synthesis**).[^indextts2-readme]

## Citations and predecessor

- IndexTTS2 citation is `zhou2025indextts2`, titled `IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech`, by Siyi Zhou, Yiquan Zhou, Yi He, Xun Zhou, Jinchao Wang, Wei Deng, and Jingchen Shu, `arXiv preprint arXiv:2506.21619`, year 2025 (**Reported**).[^indextts2-readme]
- Predecessor citation is `deng2025indextts`, titled `IndexTTS: An Industrial-Level Controllable and Efficient Zero-Shot Text-To-Speech System`, by Wei Deng, Siyi Zhou, Jingchen Shu, Jinchao Wang, and Lu Wang, `arXiv preprint arXiv:2502.05512`, year 2025 (**Reported**).[^indextts2-readme]
- The fragment asserts no supersession, replacement, compatibility, or weight-sharing relationship between IndexTTS and IndexTTS2 beyond co-citation; no supersession edge is recorded (**Synthesis**).[^indextts2-readme]

## Acknowledged lineage

- The `Acknowledge` list names tortoise-tts, XTTSv2, BigVGAN, wenet, icefall, maskgct, and seed-vc with repository links; the fragment states no architecture reuse, weight derivation, training-data, or license-inheritance claim for any of them (**Reported**).[^indextts2-readme]

## Relationships

- Successor release: [IndexTTS-2.5](indextts-2-5.md) claims added Japanese, Spanish, and Arabic support, faster inference, speaking-speed control, and improved Pinyin/CMU/Kana controllability over IndexTTS-2; this concept covers only the IndexTTS2 README fragment, so capability and usage detail lives in the 2.5 concept (**Synthesis**).[^indextts2-readme]
- Packaged runtime: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) catalogs `IndexTTS2-GGUF` and `IndexTTS2.5-GGUF` under the `index_tts2` family with original plus F16 plus Q8 weights, while this concept covers only the upstream IndexTTS2 release identity from the README fragment; no shared benchmark or serving claim is asserted (**Synthesis**).[^indextts2-readme]
- Benchmark baseline: [Higgs TTS 3](higgs-tts-3-4b.md) reports IndexTTS-2 as a comparison baseline in multilingual voice-clone WER/CER tables and Emergent-TTS judge win-rates, while this concept carries no evaluation figures of its own; the comparison direction runs from the Higgs source, not from the IndexTTS-2 fragment (**Synthesis**).[^indextts2-readme]

## Coverage and limits

- Source inspected statically only; no repository cloned, no paper fetched, no checkpoint downloaded, no demo visited, and no expressiveness, duration-control, cloning-quality, or latency claim reproduced (**Synthesis**).[^indextts2-readme]
- Remote paper, GitHub repository, demo site, Hugging Face and ModelScope weights, and all seven acknowledged upstream projects were linked but not fetched and are not in `raw/`; architecture, parameters, training data, hyperparameters, tokenizer/vocoder detail, inference usage, streaming behavior, evaluation protocol, and license are absent from the captured fragment (**Synthesis**).[^indextts2-readme]
- Status is `draft` because the fragment supports release identity and provenance only; all capability, compatibility, serving, and benchmark claims remain source assertions without independent verification in this wiki, and model-release figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^indextts2-readme]

[^indextts2-readme]: [IndexTTS-2 README fragment](../raw/IndexTTS-2.md) — locators: frontmatter (`language: [en, zh]`, `pipeline_tag: text-to-speech`); heading `IndexTTS2` and subtitle `IndexTTS2: A Breakthrough in Emotionally Expressive and Duration-Controlled Auto-Regressive Zero-Shot Text-to-Speech`; badge/link block (arXiv `2506.21619`, GitHub `index-tts/index-tts`, demo `index-tts.github.io/index-tts2.github.io`, Hugging Face `IndexTeam/IndexTTS-2`, ModelScope `IndexTeam/IndexTTS-2`); `Acknowledge` numbered list (tortoise-tts, XTTSv2, BigVGAN, wenet, icefall, maskgct, seed-vc); `Citation` BibTeX blocks (`zhou2025indextts2` with `arXiv:2506.21619`; `deng2025indextts` with `arXiv:2502.05512`).
