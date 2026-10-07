---
type: Concept
title: Qwen3-TTS-12Hz-0.6B-CustomVoice
description: 0.6B-parameter multilingual CustomVoice TTS checkpoint on the 12Hz tokenizer with 9 preset timbres, instruction-driven style control, 10-language coverage, and streaming synthesis down to 97 ms latency.
tags: [tts, multilingual, streaming, custom-voice]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: qwen3-tts-06b-customvoice-card
    resource: ../raw/Qwen3-TTS-12Hz-0.6B-CustomVoice.md
    kind: documentation
    title: Qwen3-TTS-12Hz-0.6B-CustomVoice model card
  - id: gwen-tts-card
    resource: ../raw/gwen-tts-0.6B.md
    kind: documentation
    title: Gwen-TTS 0.6B model card
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
---

Qwen3-TTS-12Hz-0.6B-CustomVoice is the Qwen team's 0.6B-parameter CustomVoice text-to-speech checkpoint in the Qwen3-TTS series, built on the 12Hz tokenizer with 9 premium preset timbres, natural-language instruction-driven style control across 10 major languages, and streaming-optimized synthesis with end-to-end latency as low as 97 ms (**Reported**).[^qwen3-tts-06b-customvoice-card]

## Model identity and release

- Series is Qwen3-TTS, described as multilingual, controllable, robust, and streaming text-to-speech models developed by the Qwen team; this checkpoint is the 0.6B CustomVoice variant based on the 12Hz tokenizer (**Reported**).[^qwen3-tts-06b-customvoice-card]
- Model identifier is `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice`; linked resources are the Qwen3-TTS Technical Report (`arXiv:2601.15621`), GitHub repository `QwenLM/Qwen3-TTS`, and the `Qwen/Qwen3-TTS` Hugging Face Spaces demo (**Reported**).[^qwen3-tts-06b-customvoice-card]
- Card frontmatter declares `license: apache-2.0`, `pipeline_tag: text-to-speech`, languages `zh, en, ja, ko, de, fr, ru, pt, es, it`, tags `tts, qwen, audio`, and `arxiv: 2601.15621` (**Observed** by static inspection).[^qwen3-tts-06b-customvoice-card]

## Capabilities

- Multilingual synthesis across 10 languages: Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, and Italian (**Reported**).[^qwen3-tts-06b-customvoice-card]
- Intelligent control adapts tone, rhythm, and emotional expression from natural-language instructions, exemplified by instructing a happy tone such as "Speak in a very happy tone" (**Reported**).[^qwen3-tts-06b-customvoice-card]
- Low-latency streaming generation uses the Qwen3-TTS-Tokenizer-12Hz, with end-to-end synthesis latency claimed as low as 97 ms; no measurement protocol or hardware is given in this card (**Reported**).[^qwen3-tts-06b-customvoice-card]

## Supported speakers

Nine supported preset speakers with the card's recommendation to use each speaker's native language for the best results (**Reported**):[^qwen3-tts-06b-customvoice-card]

| Speaker | Voice description | Native language |
| --- | --- | --- |
| Vivian | Bright young female voice. | Chinese |
| Serena | Warm, gentle young female voice. | Chinese |
| Uncle_Fu | Seasoned male voice, mellow timbre. | Chinese |
| Dylan | Youthful Beijing male voice. | Chinese (Beijing) |
| Eric | Lively Chengdu male voice. | Chinese (Sichuan) |
| Ryan | Dynamic male voice with rhythm. | English |
| Aiden | Sunny American male voice. | English |
| Ono_Anna | Playful Japanese female voice. | Japanese |
| Sohee | Warm Korean female voice. | Korean |

- Six supported synthesis languages (German, French, Russian, Portuguese, Spanish, Italian) have no native speaker in the preset table, so those languages are served cross-lingually from the nine listed timbres (**Synthesis**).[^qwen3-tts-06b-customvoice-card]

## Inference usage

- Install with `pip install -U qwen-tts` (**Reported**).[^qwen3-tts-06b-customvoice-card]
- Load with `Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="flash_attention_2")` (**Reported**).[^qwen3-tts-06b-customvoice-card]
- Synthesize with `model.generate_custom_voice(text=..., language=..., speaker=..., instruct=...)`; the documented example passes Chinese text, `language="Chinese"`, `speaker="Vivian"`, and `instruct="用特别愤怒的语气说"` (speak in a very angry tone) (**Reported**).[^qwen3-tts-06b-customvoice-card]
- Save output with `soundfile.write`, e.g. `sf.write("output_custom_voice.wav", wavs[0], sr)` where `wavs, sr` is the generation return value (**Reported**).[^qwen3-tts-06b-customvoice-card]

## Vietnamese gap and serving-layer streaming (secondary report)

- A 10/2026 AI-compiled report confirms the official 10-language list has no Vietnamese, notes an unanswered community request (GitHub Discussion #274, 03/2026), and points to unbenchmarked community fine-tunes `ShiniChien/Qwen3-TTS-12Hz-1.7B-Vietnamese` and `-VN-Style` trained from `1.7B-Base` with unclear data license; it recommends [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) for Vietnamese and this family for other languages (**Reported**).[^claude-pipeline-report]
- A separate compiled Vietnamese finetune from the 0.6B Base line now exists: [Gwen-TTS 0.6B](gwen-tts-0.6b.md) by G-Group AI Lab, trained on a claimed ~1,000 hours of TikTok-crawled Vietnamese audio with `generate_voice_clone` cloning and a fixed sampling configuration, but with no benchmarks, streaming figures, or data-rights review in its card (**Reported**).[^gwen-tts-card]
- The same report qualifies the 97 ms streaming claim: the official `qwen-tts` package returns `(wavs, sr)` only after full generation, so streaming comes from the serving layer — vLLM-Omni `POST /v1/audio/speech` with `response_format="pcm"`, `stream_format="audio"` (`async_chunk: true`) or its WebSocket protocol, 24 kHz PCM, `speed` unsupported when streaming, TTFP 64 ms at concurrency 1 per vLLM-Omni docs — or community forks such as [Faster Qwen3-TTS](faster-qwen3-tts.md) (**Reported**).[^claude-pipeline-report]
- Voice cloning (`create_voice_clone_prompt`, `generate_voice_clone`) exists only on Base checkpoints; calling it on CustomVoice or VoiceDesign raises `ValueError` (**Reported**).[^claude-pipeline-report]
- Used for non-Vietnamese languages in [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md), with estimated VRAM below the 1.7B's ~5–7 GB (**Reported**).[^claude-pipeline-report]

## Relationships

- Underlying tokenizer [Qwen3-TTS-Tokenizer-12Hz](qwen3-tts-tokenizer-12hz.md): the shared 12.5 Hz 16-codebook causal-ConvNet codec this checkpoint builds on for encode/decode and streaming; tokenizer detail lives there (**Synthesis**).[^qwen3-tts-06b-customvoice-card]
- Smaller sibling [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md): same 9-speaker CustomVoice setup, 10-language coverage, and 97 ms streaming claim at 1.7B scale with instruction control; this 0.6B checkpoint lacks instruction control per the family table (**Synthesis**).[^qwen3-tts-06b-customvoice-card]
- Tokenizer family of [Breeze TTS 2](breeze-tts-2.md): Breeze TTS 2 reports its audio tokenizer is based on Qwen3-TTS by the Alibaba Qwen Team under Apache 2.0, while this concept covers the 0.6B CustomVoice Qwen3-TTS checkpoint with preset timbres and instruction-driven style control; no shared training-data claim is asserted (**Synthesis**).[^qwen3-tts-06b-customvoice-card]
- Vietnamese Base-lineage finetune [Gwen-TTS 0.6B](gwen-tts-0.6b.md): trained from `Qwen/Qwen3-TTS-12Hz-0.6B-Base` on a claimed ~1,000 hours of TikTok-crawled Vietnamese audio for zero-shot voice cloning, while this concept covers the official 0.6B CustomVoice checkpoint with preset timbres and no Vietnamese; the finetune carries no benchmarks, streaming, or data-rights evidence (**Synthesis**).[^gwen-tts-card]
- 0.6B multilingual comparison with [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md): that concept covers a 0.6B multilingual zero-shot voice-cloning model with DualAR architecture and ONNX/SGLang serving paths, while this concept covers a 0.6B preset-timbre CustomVoice model with instruction-driven style control and a `qwen-tts` plus FlashAttention 2 loading path; neither replaces the other (**Synthesis**).[^qwen3-tts-06b-customvoice-card]
- Instruction-control comparison with [CosyVoice2-0.5B](cosyvoice2-0.5b.md): that concept covers a 0.5B streaming TTS model with zero-shot cloning plus cross-lingual and instruct modes, while this concept covers a 0.6B preset-timbre model steered by natural-language instructions over fixed speakers; no shared vendor or codebase is asserted (**Synthesis**).[^qwen3-tts-06b-customvoice-card]

## Coverage and limits

- Source inspected statically only; no `qwen-tts` package installed, no checkpoint downloaded, no audio synthesized, and no 97 ms latency, multilingual-quality, or instruction-following claim reproduced (**Synthesis**).[^qwen3-tts-06b-customvoice-card]
- Linked but unfetched and absent from `raw/`: Qwen3-TTS GitHub repository, technical-report paper `arXiv:2601.15621`, Hugging Face Spaces demo, `qwen-tts` PyPI package, and the `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` weights; checkpoint contents, tokenizer weights, and reference audio were not inspected (**Synthesis**).[^qwen3-tts-06b-customvoice-card]
- Sibling `raw/Qwen3-TTS-12Hz-1.7B-CustomVoice.md` now compiled as [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) (family overview, model table, usage, evaluation tables); tokenizer detail now compiled as [Qwen3-TTS-Tokenizer-12Hz](qwen3-tts-tokenizer-12hz.md) from `raw/Qwen3-TTS-Tokenizer-12Hz.md` (**Synthesis**).[^qwen3-tts-06b-customvoice-card]
- All capability, language-coverage, latency, compatibility, and usage claims are source assertions without independent verification in this wiki; model-release and latency figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^qwen3-tts-06b-customvoice-card]

[^qwen3-tts-06b-customvoice-card]: [Qwen3-TTS-12Hz-0.6B-CustomVoice model card](../raw/Qwen3-TTS-12Hz-0.6B-CustomVoice.md) — locators: frontmatter (`license`, `pipeline_tag`, `language`, `tags`, `arxiv`); title plus intro paragraph (Qwen3-TTS series description, 0.6B CustomVoice variant, 12Hz tokenizer, 9 premium timbres, instruction style control, 10 languages); `Paper`/`GitHub`/`Demo` link lines; `Key Features` section (10-language list, intelligent-control sentence with happy-tone example, 97 ms streaming sentence with Tokenizer-12Hz); `Quickstart` section (`pip install -U qwen-tts` fence; `Qwen3TTSModel.from_pretrained` fence with `device_map`/`dtype`/`attn_implementation`; `generate_custom_voice` fence with Chinese text, `language="Chinese"`, `speaker="Vivian"`, `instruct="用特别愤怒的语气说"`; `sf.write` line); `Supported Speakers` section (intro recommendation sentence, 9-row speaker table with voice descriptions and native languages); `Citation` section (arXiv 2601.15621 BibTeX).

[^gwen-tts-card]: [Gwen-TTS 0.6B model card](../raw/gwen-tts-0.6B.md) — locators: frontmatter (`base_model: Qwen/Qwen3-TTS-12Hz-0.6B-Base`, `license: mit`, 11-code `language` with `vi`); intro plus `Key highlights` (~1,000 h TikTok-crawl finetune, few-second cloning); `## How to Use` (full `generation_config` dict, `generate_voice_clone` with `language="Vietnamese"`/`ref_audio`/`ref_text`); `## Voice Samples` (9 speaker tables); `## Supported Languages` (Vietnamese primary, non-Vietnamese caveat). No benchmarks, latency, or streaming figures stated.

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `Key Findings` 1–2 (10-language list, Discussion #274, `ShiniChien` fine-tunes, serving-layer streaming, vLLM-Omni 64 ms TTFP); `PHẦN 1` §6 Qwen3-TTS row; `PHẦN 2` `Qwen3-TTS: chọn model và cách dùng` (model choice, Base-only cloning `ValueError`, `qwen-tts` non-streaming API, vLLM-Omni HTTP/WebSocket streaming parameters); VRAM list; `Caveats`.
