---
type: Concept
title: Qwen3-TTS-12Hz-1.7B-CustomVoice
description: 1.7B-parameter multilingual CustomVoice TTS checkpoint on the 12Hz tokenizer with 9 preset timbres, instruction-driven style control, 10-language coverage, and streaming synthesis down to 97 ms latency.
tags: [tts, multilingual, streaming, custom-voice]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: qwen3-tts-17b-customvoice-card
    resource: ../raw/Qwen3-TTS-12Hz-1.7B-CustomVoice.md
    kind: documentation
    title: Qwen3-TTS-12Hz-1.7B-CustomVoice model card
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
---

Qwen3-TTS-12Hz-1.7B-CustomVoice is the Qwen team's 1.7B-parameter CustomVoice text-to-speech checkpoint in the Qwen3-TTS series, offering style control over 9 premium preset timbres via natural-language instructions across 10 major languages, on the discrete multi-codebook 12Hz-tokenizer architecture with streaming synthesis claimed down to 97 ms end-to-end latency (**Reported**).[^qwen3-tts-17b-customvoice-card]

## Model identity and release

- Series is Qwen3-TTS, described as multilingual, controllable, robust, and streaming text-to-speech models developed by the Qwen team; this checkpoint is the 1.7B CustomVoice variant based on the 12Hz tokenizer (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Model identifier is `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice`; linked resources are the Qwen3-TTS Technical Report (`arXiv:2601.15621`), GitHub repository `QwenLM/Qwen3-TTS`, and DashScope realtime APIs for custom-voice, voice-cloning, and voice-design (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Card frontmatter declares `license: apache-2.0` and `pipeline_tag: text-to-speech` (**Observed** by static inspection).[^qwen3-tts-17b-customvoice-card]
- ModelScope and Hugging Face download commands are documented for the tokenizer plus all five released checkpoints (1.7B VoiceDesign/CustomVoice/Base, 0.6B CustomVoice/Base); weights also auto-download on `from_pretrained` / vLLM load (**Reported**).[^qwen3-tts-17b-customvoice-card]

## Architecture

- Speech representation is powered by the self-developed `Qwen3-TTS-Tokenizer-12Hz`, claimed to give efficient acoustic compression with high-dimensional semantic modeling, preserving paralinguistic and acoustic-environment information for high-fidelity reconstruction through a lightweight non-DiT architecture (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Universal end-to-end architecture uses a discrete multi-codebook LM, claimed to bypass the information bottlenecks and cascading errors of traditional LM+DiT schemes (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Streaming uses a Dual-Track hybrid architecture: one model supports streaming and non-streaming generation, emitting the first audio packet after a single input character with end-to-end latency claimed as low as 97 ms; no measurement protocol or hardware is given in this card (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Instruction-driven control steers timbre, emotion, and prosody from natural-language instructions, with text-semantic understanding adaptively adjusting tone, rhythm, and emotional expression (**Reported**).[^qwen3-tts-17b-customvoice-card]

## Model family

All five released checkpoints cover the same 10 languages (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian) with streaming support; only the 1.7B variants support instruction control (**Reported**):[^qwen3-tts-17b-customvoice-card]

| Model | Features | Instruction control |
| --- | --- | --- |
| Qwen3-TTS-12Hz-1.7B-VoiceDesign | Voice design from user descriptions. | ✅ |
| Qwen3-TTS-12Hz-1.7B-CustomVoice | Style control over target timbres via instructions; 9 premium timbres. | ✅ |
| Qwen3-TTS-12Hz-1.7B-Base | 3-second rapid voice clone from user audio; usable for fine-tuning. | — |
| Qwen3-TTS-12Hz-0.6B-CustomVoice | 9 premium timbres. | — |
| Qwen3-TTS-12Hz-0.6B-Base | 3-second rapid voice clone; usable for fine-tuning. | — |

## Supported speakers

Nine preset speakers; the card recommends each speaker's native language for best quality while noting every speaker can speak any supported language (**Reported**):[^qwen3-tts-17b-customvoice-card]

| Speaker | Voice description | Native language |
| --- | --- | --- |
| Vivian | Bright, slightly edgy young female voice. | Chinese |
| Serena | Warm, gentle young female voice. | Chinese |
| Uncle_Fu | Seasoned male voice with a low, mellow timbre. | Chinese |
| Dylan | Youthful Beijing male voice with a clear, natural timbre. | Chinese (Beijing dialect) |
| Eric | Lively Chengdu male voice with a slightly husky brightness. | Chinese (Sichuan dialect) |
| Ryan | Dynamic male voice with strong rhythmic drive. | English |
| Aiden | Sunny American male voice with a clear midrange. | English |
| Ono_Anna | Playful Japanese female voice with a light, nimble timbre. | Japanese |
| Sohee | Warm Korean female voice with rich emotion. | Korean |

- Six supported synthesis languages (German, French, Russian, Portuguese, Spanish, Italian) have no native speaker in the preset table, so those languages are served cross-lingually from the nine listed timbres (**Synthesis**).[^qwen3-tts-17b-customvoice-card]

## Inference usage

- Install via `pip install -U qwen-tts` in a fresh Python 3.12 environment (conda example given); source install with `pip install -e .` and optional FlashAttention 2 (`torch.float16`/`bfloat16` only) are documented (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Load with `Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="flash_attention_2")`; extra `model.generate` kwargs (e.g. `max_new_tokens`, `top_p`) are accepted (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Synthesize with `model.generate_custom_voice(text=..., language=..., speaker=..., instruct=...)`, supporting single strings and batch lists; `language="Auto"` (or omitted) selects auto language adaptation. Documented example: Chinese text with `speaker="Vivian"` and `instruct="用特别愤怒的语气说"`; batch example pairs Vivian/Ryan with Chinese/English (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Introspect with `model.get_supported_speakers()` and `model.get_supported_languages()`; write output with `soundfile.write`, e.g. `sf.write("output_custom_voice.wav", wavs[0], sr)` (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Family workflows documented in the same card: `generate_voice_design(text, language, instruct)` for the VoiceDesign model; `generate_voice_clone(text, language, ref_audio, ref_text)` for Base models with `ref_audio` as path/URL/base64/(array, sr) tuple and reusable prompts via `create_voice_clone_prompt` / `voice_clone_prompt`; a VoiceDesign-then-Clone pattern (design a reference clip, build a clone prompt, reuse across lines); and `Qwen3TTSTokenizer` encode/decode (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Serving paths: `qwen-tts-demo <model-id> --ip --port` local WebUI (Base deployments should use HTTPS via `--ssl-certfile/--ssl-keyfile` with an `openssl` self-signed-cert recipe); DashScope realtime APIs for custom-voice, voice-clone, and voice-design; vLLM-Omni day-0 offline inference (`end2end.py --query-type CustomVoice|VoiceDesign|Base`) with online serving marked as later (**Reported**).[^qwen3-tts-17b-customvoice-card]

## Evaluation (as reported)

Evaluation ran at `dtype=torch.bfloat16`, `max_new_tokens=2048`, checkpoint-default sampling, `language="auto"` for Seed-Test and InstructTTS-Eval and explicit language elsewhere; all figures below are source assertions without in-wiki reproduction (**Reported**):[^qwen3-tts-17b-customvoice-card]

- Seed-TTS zero-shot content consistency (WER ↓): 12Hz-1.7B-Base scores 0.77 test-zh / 1.24 test-en — best English of the table, second-best Chinese behind CosyVoice 3 (0.71); 12Hz-0.6B-Base scores 0.92 / 1.32 (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Multilingual TTS test set (WER ↓ / SIM ↑): 12Hz-1.7B-Base leads speaker similarity on 8 of 10 languages (e.g. Chinese 0.799, English 0.775, Italian 0.817) and takes content-consistency bests on Italian (0.948), Korean (1.755), and Russian (3.212); MiniMax and ElevenLabs trail on most SIM columns (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Cross-lingual pairs (mixed error rate ↓): 12Hz-1.7B-Base is best on 8 of 12 directions (e.g. en-to-zh 4.77, zh-to-en 2.77, zh-to-ko 4.82); CosyVoice3 takes ja-to-zh (3.05), ko-to-zh (1.06), zh-to-ja (7.08), en-to-ja (6.80) (**Reported**).[^qwen3-tts-17b-customvoice-card]
- InstructTTSEval control accuracy (APS/DSD/RP ↑): 12Hz-1.7B-CustomVoice target-speaker scores ZH 83.0/77.8/61.2 and EN 77.3/77.1/63.7, behind Gemini-flash/pro and near the 25Hz-1.7B-CustomVoice sibling; 12Hz-1.7B VoiceDesign (ZH 85.2/81.1/65.1, EN 82.9/82.4/68.4) leads the open voice-design rows (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Target-speaker multilingual WER ↓ vs GPT-4o-Audio Preview: the 1.7B CustomVoice variants beat it on most languages (e.g. 12Hz-1.7B-CustomVoice English 0.899 vs 2.197, Chinese 0.903 vs 3.519); GPT-4o-Audio Preview is best only on Portuguese (1.504) (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Long-form generation (WER ↓): 25Hz-1.7B-CustomVoice (1.517 zh / 1.225 en) beats 12Hz-1.7B-CustomVoice (2.356 / 2.812); both beat Higgs-Audio-v2, VibeVoice, and VoxCPM on Chinese, while VibeVoice leads English (1.780) (**Reported**).[^qwen3-tts-17b-customvoice-card]
- Tokenizer reconstruction: Qwen-TTS-Tokenizer-12Hz (NQ 16, codebook 2048, 12.5 FPS) leads PESQ_WB 3.21 / PESQ_NB 3.68 / STOI 0.96 / UTMOS 4.16 / SIM 0.95 against SpeechTokenizer, X-codec/2, XY-Tokenizer, Mimi, and FireRedTTS 2 tokenizers (**Reported**).[^qwen3-tts-17b-customvoice-card]

## Vietnamese gap and serving-layer streaming (secondary report)

- A 10/2026 AI-compiled report confirms the official 10-language list has no Vietnamese, notes an unanswered community request (GitHub Discussion #274, 03/2026), and points to unbenchmarked community fine-tunes `ShiniChien/Qwen3-TTS-12Hz-1.7B-Vietnamese` and `-VN-Style` trained from `1.7B-Base` with unclear data license; it recommends [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) for Vietnamese and this family for other languages (**Reported**).[^claude-pipeline-report]
- The same report qualifies the 97 ms streaming claim: the official `qwen-tts` package returns `(wavs, sr)` only after full generation, so streaming comes from the serving layer — vLLM-Omni `POST /v1/audio/speech` with `response_format="pcm"`, `stream_format="audio"` (`async_chunk: true`) or its WebSocket protocol, 24 kHz PCM, `speed` unsupported when streaming, TTFP 64 ms at concurrency 1 per vLLM-Omni docs — or community forks such as [Faster Qwen3-TTS](faster-qwen3-tts.md) (**Reported**).[^claude-pipeline-report]
- Voice cloning (`create_voice_clone_prompt`, `generate_voice_clone`) exists only on Base checkpoints; calling it on CustomVoice or VoiceDesign raises `ValueError` (**Reported**).[^claude-pipeline-report]
- Used for non-Vietnamese languages in [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md), with estimated VRAM ~5–7 GB (**Reported**).[^claude-pipeline-report]

## Relationships

- Underlying tokenizer [Qwen3-TTS-Tokenizer-12Hz](qwen3-tts-tokenizer-12hz.md): the shared 12.5 Hz 16-codebook causal-ConvNet codec with the dedicated encode/decode interface; tokenizer benchmark rows here are now complemented by that authority (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- Larger sibling of [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md): same 9-speaker CustomVoice setup, 10-language coverage, and 97 ms streaming claim at 1.7B scale with instruction control; the 0.6B page lacks instruction control per the family table (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- Tokenizer family of [Breeze TTS 2](breeze-tts-2.md): Breeze TTS 2 reports its audio tokenizer is based on Qwen3-TTS by the Alibaba Qwen Team under Apache 2.0, while this concept covers the 1.7B CustomVoice checkpoint; no shared training-data claim is asserted (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- 1.7B comparison with [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md): that concept covers a 0.6B DualAR zero-shot cloning model with ONNX/SGLang paths, while this concept covers a 1.7B preset-timbre model with instruction style control and `qwen-tts`/FlashAttention 2 plus vLLM-Omni paths; neither replaces the other (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- Packaged in [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md): the catalog lists `Qwen3-TTS-12Hz-1.7B-CustomVoice-GGUF` (`qwen3_tts`, BF16 + Q8, Apache-2.0) (**Synthesis**).[^qwen3-tts-17b-customvoice-card]

## Coverage and limits

- Source inspected statically only; no `qwen-tts` package installed, no checkpoint downloaded, no audio synthesized, and no latency, quality, instruction-following, or benchmark claim reproduced (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- Linked but unfetched and absent from `raw/`: Qwen3-TTS GitHub repository, technical-report paper `arXiv:2601.15621`, Hugging Face Spaces demo, `qwen-tts` PyPI package, ModelScope/Hugging Face weight downloads, DashScope API docs, vLLM-Omni docs and `end2end.py` examples, and tokenizer-demo/clone reference audio (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- Architecture images (`qwen3_tts_introduction.png`, `overview.png`) were not visually inspected; architecture claims above come from surrounding prose and tables only (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- Tokenizer internals are summarized from this card's prose and benchmark rows only; the dedicated `raw/Qwen3-TTS-Tokenizer-12Hz.md` card is now compiled as [Qwen3-TTS-Tokenizer-12Hz](qwen3-tts-tokenizer-12hz.md) and is the authority for tokenizer detail (**Synthesis**).[^qwen3-tts-17b-customvoice-card]
- All capability, latency, benchmark, and usage claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^qwen3-tts-17b-customvoice-card]

[^qwen3-tts-17b-customvoice-card]: [Qwen3-TTS-12Hz-1.7B-CustomVoice model card](../raw/Qwen3-TTS-12Hz-1.7B-CustomVoice.md) — locators: frontmatter (`license`, `pipeline_tag`); `Overview/Introduction` section (10-language list, 4 key-feature bullets including 97 ms Dual-Track streaming and instruction-control sentences); `Model Architecture` image lines; `Released Models` table (tokenizer row plus 5-model Features/Language/Streaming/Instruction-Control matrix); `ModelScope`/`Hugging Face` download fences; `Quickstart/Environment Setup` (`conda create -n qwen3-tts python=3.12`, `pip install -U qwen-tts`, `flash-attn` fences); `Custom Voice Generate` fence (`generate_custom_voice` single/batch, Vivian/Ryan examples, `get_supported_speakers/languages`); `Supported speaker` 9-row table; `Voice Design`, `Voice Clone`, `Voice Design then Clone`, `Tokenizer Encode and Decode` fences; `Launch Local Web UI Demo` commands plus `Base Model HTTPS Notes` `openssl` recipe; `DashScope API Usage` 3-row table; `vLLM Usage/Offline Inference` commands; `Evaluation` protocol sentence plus `Speech Generation Benchmarks` and `Speech Tokenizer Benchmarks` tables (Seed-TTS, multilingual WER/SIM, cross-lingual, InstructTTSEval, target-speaker multilingual, long-form, tokenizer ASR/reconstruction); `Citation` BibTeX (`arXiv:2601.15621`).

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `Key Findings` 1–2 (10-language list, Discussion #274, `ShiniChien` fine-tunes, serving-layer streaming, vLLM-Omni 64 ms TTFP); `PHẦN 1` §6 Qwen3-TTS row; `PHẦN 2` `Qwen3-TTS: chọn model và cách dùng` (model choice, Base-only cloning `ValueError`, `qwen-tts` non-streaming API, vLLM-Omni HTTP/WebSocket streaming parameters); VRAM list; `Caveats`.
