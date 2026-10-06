---
type: Concept
title: IndexTTS-2.5
description: Zero-shot multilingual TTS model by IndexTeam that clones a voice from a single reference clip, with cross-lingual transfer, emotion and pronunciation control, and a 0.8B GPT backbone.
tags: [tts, zero-shot, voice-cloning, multilingual, emotion-controllable]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T19:00:00Z }
stale_after: 2027-10-06
sources:
  - id: indextts25-card
    resource: ../raw/IndexTTS-2.5.md
    kind: documentation
    title: IndexTTS-2.5 model card
---

IndexTTS-2.5 is IndexTeam (Bilibili)'s autoregressive zero-shot text-to-speech model that clones a voice from a single reference audio clip, covering Chinese, English, Japanese, Spanish, and Arabic with cross-lingual voice transfer and timbre-disentangled emotion control, and is documented as a faster, speed-controllable successor to IndexTTS-2 with improved Pinyin, CMU-phoneme, and Kana controllability (**Reported**).[^indextts25-card]

## Model identity and release

- Developed by IndexTeam, Bilibili; repository `github.com/index-tts/index-tts`; weights `IndexTeam/IndexTTS-2.5` on Hugging Face and ModelScope; paper `arXiv:2601.03888` (2026 technical report by Li et al.) (**Reported**).[^indextts25-card]
- Frontmatter declares `language: [zh, en, ja, es, ar]`, `pipeline_tag: text-to-speech`, `library_name: indexts` (spelled `indextts`), tags for zero-shot, voice-cloning, multilingual, cross-lingual, and emotion-controllable synthesis, and license `bilibili-model-license` via `LICENSE` (**Observed** by static inspection).[^indextts25-card]
- License is the bilibili Model Use License Agreement; the linked `LICENSE` file itself was not captured in `raw/` and its terms were not inspected (**Synthesis**).[^indextts25-card]
- Compared with IndexTTS-2, the card claims added Japanese, Spanish, and Arabic support, faster inference, new speaking-speed control, and improved Chinese Pinyin, English CMU-phoneme, and Japanese Kana controllability; no benchmark numbers or latency measurements support the faster-inference claim in the card (**Reported**).[^indextts25-card]

## Architecture and output

- Autoregressive zero-shot TTS with a GPT backbone (~0.8B parameters for the GPT component), a flow-matching speech-to-mel decoder, and a BigVGAN vocoder, emitting a 22.05 kHz waveform (**Reported**).[^indextts25-card]
- Auxiliary models w2v-bert-2.0, MaskGCT semantic codec, CAMPPlus, and BigVGAN are not part of the repository and download into `checkpoints/hf_cache/` on first run (**Reported**).[^indextts25-card]
- No training data, hyperparameters, evaluation protocol, or benchmark figures appear in the card (**Synthesis**).[^indextts25-card]

## Languages and voice capabilities

- Supported languages: Chinese, English, Japanese, Spanish, Arabic, with cross-lingual voice transfer and emotion control disentangled from timbre (**Reported**).[^indextts25-card]
- Emotion control takes an 8-float vector in the order [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]; the example sets afraid to 0.8 for a Chinese line (**Reported**).[^indextts25-card]
- Pronunciation control uses `<word|reading>` inline form for Pinyin, CMU phonemes, or Kana; the example disambiguates Chinese `行` as `XING2` versus `HANG2` (**Reported**).[^indextts25-card]
- Speaking-speed control uses `duration_factor` in the range 0.5–2.0, where values above 1.0 slow down and below 1.0 speed up; the example uses 1.2 (**Reported**).[^indextts25-card]

## Inference usage

- Requires Python 3.10–3.11, an NVIDIA GPU, and roughly 6 GB of VRAM for inference (**Reported**).[^indextts25-card]
- Install via `git clone https://github.com/index-tts/index-tts.git`, `pip install -U uv`, and `uv sync --all-extras`; weights via `hf download IndexTeam/IndexTTS-2.5 --local-dir=checkpoints` or `modelscope download --model IndexTeam/IndexTTS-2.5 --local_dir checkpoints`; Web UI via `uv run webui.py` (**Reported**).[^indextts25-card]
- Python entry point is `indextts.infer_v2_5.IndexTTS2`, constructed with `cfg_path="checkpoints/config.yaml"`, `model_dir="checkpoints"`, and `use_bf16=True`; `tts.infer` takes `spk_audio_prompt`, `text`, `lang` (`"EN"`, `"ZH"` in examples), `output_path`, plus optional `emo_vector` and `duration_factor` (**Reported**).[^indextts25-card]
- Text-description emotion control needs the QwenEmotion model, loaded only when constructed with `use_qwen_emo=True`; passing `use_emo_text=True` without it raises at inference time (**Reported**).[^indextts25-card]

## Constraints and limitations

- Long text is split into segments concatenated with a short silence, so prosody is not modelled across segment boundaries (**Reported**).[^indextts25-card]
- Enabling random emotion sampling (`use_random=True`) reduces voice-cloning fidelity (**Reported**).[^indextts25-card]
- The model does not verify speaker consent in the reference clip; obtaining consent is the user's responsibility and all use is subject to the license terms (**Reported**).[^indextts25-card]
- No streaming, latency-budget, real-time-factor, or edge-packaging claim appears in the card; GGUF or CPU deployment is covered only by related packaging concepts, not this source (**Synthesis**).[^indextts25-card]

## Relationships

- Predecessor lineage: [IndexTTS2](indextts2.md) is the prior IndexTeam release (arXiv:2506.21619) from which IndexTTS-2.5 claims added languages, speed, and controllability; no deprecation or weight-sharing claim is stated, so no supersession edge is recorded (**Synthesis**).[^indextts25-card]
- Packaged runtime: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) catalogs `IndexTTS2.5-GGUF` under the `index_tts2` family, while this concept covers only the upstream IndexTTS-2.5 release identity and usage from the model card (**Synthesis**).[^indextts25-card]

## Coverage and limits

- Source inspected statically only; no repository cloned, no weights downloaded, no inference executed, and no cloning-quality, emotion-fidelity, speed-control, or latency claim reproduced (**Synthesis**).[^indextts25-card]
- Remote GitHub repository, Hugging Face and ModelScope weights, arXiv paper 2601.03888, LICENSE text, and auxiliary checkpoints were linked but not fetched and are outside `raw/`; architecture internals beyond the GPT plus flow-matching plus BigVGAN statement, training data, and evaluation figures are absent from the card (**Synthesis**).[^indextts25-card]
- Status is `stable` because the intended synthesis of the card is complete and auditable; all capability and performance claims remain source assertions without independent verification, and model-release facts carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^indextts25-card]

[^indextts25-card]: [IndexTTS-2.5 model card](../raw/IndexTTS-2.5.md) — locators: frontmatter (`language: [zh, en, ja, es, ar]`, `pipeline_tag: text-to-speech`, `license_name: bilibili-model-license`); heading `IndexTTS-2.5` intro paragraphs (zero-shot cloning, 5-language list, IndexTTS-2 comparison); `Model Details` list (IndexTeam/Bilibili, autoregressive GPT plus flow-matching plus BigVGAN, ~0.8B, 5 languages, 22.05 kHz, LICENSE, GitHub URL, arXiv:2601.03888); `Getting Started` / `Install` / `Download the weights` / `Inference` / `Web UI` blocks (`infer_v2_5.IndexTTS2`, `spk_audio_prompt`/`lang`/`emo_vector`/`duration_factor` examples, `checkpoints/hf_cache/` auxiliaries, Python 3.10–3.11 plus 6 GB VRAM); `Limitations` list (segment-split prosody, `use_qwen_emo`/`use_emo_text`, `use_random` fidelity, consent responsibility); `Citation` BibTeX (`li2026indextts25technicalreport`, `2601.03888`).
