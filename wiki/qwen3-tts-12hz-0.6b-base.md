---
type: Concept
title: Qwen3-TTS-12Hz-0.6B-Base
description: 0.6B-parameter multilingual Base TTS checkpoint on the 12Hz tokenizer providing 3-second voice cloning from a reference clip plus transcript, 10-language coverage, and Apache-2.0 weights for fine-tuning.
tags: [tts, multilingual, voice-cloning, base-model]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T22:30:00Z }
stale_after: 2027-10-07
sources:
  - id: qwen3-tts-06b-base-card
    resource: ../raw/Qwen3-TTS-12Hz-0.6B-Base.md
    kind: documentation
    title: Qwen3-TTS-12Hz-0.6B-Base model card
  - id: qwen3-tts-17b-customvoice-card
    resource: ../raw/Qwen3-TTS-12Hz-1.7B-CustomVoice.md
    kind: documentation
    title: Qwen3-TTS-12Hz-1.7B-CustomVoice model card
  - id: gwen-tts-card
    resource: ../raw/gwen-tts-0.6B.md
    kind: documentation
    title: Gwen-TTS 0.6B model card
---

Qwen3-TTS-12Hz-0.6B-Base is the Qwen team's 0.6B-parameter voice-cloning checkpoint in the Qwen3-TTS series: a discrete multi-codebook LM on the 12Hz tokenizer that clones a voice from a user-provided reference clip plus its transcript and synthesizes new text in that voice, covering 10 major languages under Apache-2.0, without the preset timbres or instruction control of the CustomVoice variants (**Reported**).[^qwen3-tts-06b-base-card][^qwen3-tts-17b-customvoice-card]

## Model identity

- Model identifier is `Qwen/Qwen3-TTS-12Hz-0.6B-Base`; linked resources are the Qwen3-TTS Technical Report (`arXiv:2601.15621`), GitHub repository `QwenLM/Qwen3-TTS`, and the `Qwen/Qwen3-TTS` Hugging Face Spaces demo (**Reported**).[^qwen3-tts-06b-base-card]
- Card frontmatter declares `license: apache-2.0`, `pipeline_tag: text-to-speech`, languages `zh, en, ja, ko, de, fr, ru, pt, es, it`, and tags `audio, tts, voice-clone` (**Observed** by static inspection).[^qwen3-tts-06b-base-card]
- The card introduces the Qwen3-TTS family as multilingual, controllable, robust, and streaming, trained on over 5 million hours of speech across 10 languages, and states that this checkpoint is specifically the 0.6B Base model capable of rapid voice cloning from a user-provided audio input (**Reported**).[^qwen3-tts-06b-base-card]
- Language coverage is the same 10 languages as the whole family: Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian — Vietnamese is absent (**Reported**).[^qwen3-tts-06b-base-card]

## Capabilities and family position

- In the family's released-checkpoint table this row is described as the Base model with 3-second rapid voice cloning from user audio, usable for fine-tuning other models, with no instruction-control mark (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Voice cloning is the checkpoint's defining capability; preset timbres and instruction-driven style control belong to the 1.7B and CustomVoice lines, so the 0.6B Base is the small cloning/fine-tuning entry point of the family (**Synthesis**).[^qwen3-tts-06b-base-card][^qwen3-tts-17b-customvoice-card]
- Card feature bullets — 12Hz tokenizer speech representation, discrete multi-codebook end-to-end architecture, streaming synthesis claimed as low as 97 ms end-to-end, and natural-language instruction control — are stated for the Qwen3-TTS family rather than validated for this checkpoint; no measurement protocol or hardware is given (**Reported**).[^qwen3-tts-06b-base-card]

## Inference usage (voice clone)

- Install with `pip install -U qwen-tts`, optionally adding `pip install -U flash-attn --no-build-isolation` for optimized performance (**Reported**).[^qwen3-tts-06b-base-card]
- Load with `Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-0.6B-Base", device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="flash_attention_2")` (**Reported**).[^qwen3-tts-06b-base-card]
- Synthesize with `model.generate_voice_clone(text=..., language="English", ref_audio=..., ref_text=...)` returning `(wavs, sr)`, then save with `sf.write("output_voice_clone.wav", wavs[0], sr)`; the documented example passes a hosted reference clip URL plus its transcript (**Reported**).[^qwen3-tts-06b-base-card]
- The card exercises the multilingual path with `language="English"` and text containing an equation, an em-dash, and an emoji, showing the intended handling of mixed symbolic and paralinguistic input (**Observed** in the card's example).[^qwen3-tts-06b-base-card]

## Relationships

- Sibling CustomVoice checkpoints [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md) and [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md): same 10-language, 12Hz-tokenizer family, but those offer 9 preset timbres with instruction-driven style control instead of reference-audio cloning; this concept covers the cloning-only small checkpoint (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- Underlying tokenizer [Qwen3-TTS-Tokenizer-12Hz](qwen3-tts-tokenizer-12hz.md): the shared 12.5 Hz 16-codebook codec the checkpoint builds on for speech encoding and decoding; tokenizer detail lives there (**Synthesis**).[^qwen3-tts-06b-base-card]
- Vietnamese finetune [Gwen-TTS 0.6B](gwen-tts-0.6b.md): G-Group AI Lab states it fine-tuned this exact checkpoint on roughly 1,000 hours of TikTok-crawled Vietnamese audio for `generate_voice_clone`, which is direct evidence that the "usable for fine-tuning" claim is exercised in practice (**Reported**).[^gwen-tts-card]
- Inference-wrapper and packaging targets for this checkpoint include [Faster Qwen3-TTS](faster-qwen3-tts.md) and the audio.cpp GGUF package `Qwen3-TTS-12Hz-0.6B-Base-GGUF`; those runtimes are covered in their own concepts and are not inspected here (**Synthesis**).[^qwen3-tts-06b-base-card]

## Contradictions

- The Base card's family feature bullet advertises "Intelligent Text Understanding and Voice Control" driven by natural-language instructions,[^qwen3-tts-06b-base-card] while the family checkpoint table marks instruction control only for the 1.7B variants and leaves the 0.6B Base unmarked.[^qwen3-tts-17b-customvoice-card] The bullets appear to describe the family-level architecture rather than this checkpoint; neither reading is confirmed by a checkpoint-level evaluation, so this stays unresolved.

## Coverage and limits

- Source inspected statically only; no `qwen-tts` install, checkpoint download, inference, or audio synthesis was performed, and no cloning-quality, language-coverage, or 97 ms latency claim was reproduced (**Synthesis**).[^qwen3-tts-06b-base-card]
- The card's `## Model Architecture` section contains only an image with no accompanying text, so architecture detail beyond the feature bullets is unavailable from this source and the images were not inspected (**Observed** coverage limit).[^qwen3-tts-06b-base-card]
- Linked but unfetched and absent from `raw/`: the Qwen3-TTS GitHub repository, technical-report paper `arXiv:2601.15621`, Hugging Face Spaces demo, `qwen-tts` PyPI package, this checkpoint's weights, and the referenced clone reference-audio URL (**Synthesis**).[^qwen3-tts-06b-base-card]
- Benchmark figures for this checkpoint exist only in the sibling family card (Seed-TTS 0.92 test-zh / 1.32 test-en) and are not restated here as this card's evidence; see [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) and [TTS Model Survey](tts-model-survey.md) (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- Model-release and latency claims carry `stale_after: 2027-10-07` per the `tts` domain rule (**Synthesis**).[^qwen3-tts-06b-base-card]

[^qwen3-tts-06b-base-card]: [Qwen3-TTS-12Hz-0.6B-Base model card](../raw/Qwen3-TTS-12Hz-0.6B-Base.md) — locators: frontmatter (`license: apache-2.0`, `pipeline_tag: text-to-speech`, 10-code `language`, `tags: [audio, tts, voice-clone]`); title plus `Paper`/`GitHub`/`Demo` link line; intro paragraph (family description, 5 million hours, 10 languages, 3-second cloning and description-based control, "this specific checkpoint is the 0.6B Base model"); `## Quickstart` installation fences (`pip install -U qwen-tts`, optional `flash-attn`); `### Sample Usage (Voice Clone)` fence (`Qwen3TTSModel.from_pretrained` with `device_map`/`dtype`/`attn_implementation`, `ref_audio`/`ref_text` variables with the hosted clone.wav URL and its transcript, `generate_voice_clone` with `language="English"` and the equation/emoji text, `sf.write` line); `## Overview/### Introduction` paragraph plus four feature bullets (Tokenizer-12Hz representation, discrete multi-codebook LM, 97 ms streaming, instruction-driven control); `## Model Architecture` section containing only an `overview.png` image; `## Citation` BibTeX (arXiv 2601.15621).

[^qwen3-tts-17b-customvoice-card]: [Qwen3-TTS-12Hz-1.7B-CustomVoice model card](../raw/Qwen3-TTS-12Hz-1.7B-CustomVoice.md) — locators: `Released Models` table (the `Qwen3-TTS-12Hz-0.6B-Base` row describing 3-second rapid voice clone and fine-tuning with an empty instruction-control mark); `Overview/Introduction` (10-language list); evaluation tables (Seed-TTS WER: 12Hz-0.6B-Base 0.92 zh / 1.32 en).

[^gwen-tts-card]: [Gwen-TTS 0.6B model card](../raw/gwen-tts-0.6B.md) — locators: frontmatter (`base_model: Qwen/Qwen3-TTS-12Hz-0.6B-Base`, `license: mit`); `Key highlights` (~1,000 h TikTok-crawled Vietnamese finetune); `## How to Use` (`generate_voice_clone` with `ref_audio`/`ref_text`).
