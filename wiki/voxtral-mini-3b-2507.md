---
type: Concept
title: Voxtral Mini 3B 2507
description: Mistral AI 3B-scale audio-text model built on Ministral 3B for transcription with auto language detection, audio Q&A and summarization, voice-triggered function calling, and 30–40 minute long-form context with vLLM and Transformers inference.
tags: [stt, asr, audio-understanding, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: voxtral-mini-3b-card
    resource: ../raw/Voxtral-Mini-3B-2507.md
    kind: documentation
    title: Voxtral Mini 3B 2507 model card
---

Voxtral Mini 3B 2507 (`mistralai/Voxtral-Mini-3B-2507`) is Mistral AI's 3B-scale enhancement of Ministral 3B with native audio input, covering dedicated transcription with automatic source-language prediction, long-form audio (30 minutes for transcription, 40 minutes for understanding in 32k context), direct audio Q&A and summarization without a separate ASR plus language-model stack, and voice-triggered function calling, served via vLLM (recommended) or Transformers (**Reported**).[^voxtral-mini-3b-card]

## Model identity and lineage

- Card title is `Voxtral Mini 1.0 (3B) - 2507`; checkpoint is `mistralai/Voxtral-Mini-3B-2507`; backbone is Ministral 3B with retained text performance; companion pointers are the Voxtral blog post and research paper arXiv 2507.13264 (**Reported**).[^voxtral-mini-3b-card]
- Frontmatter declares `library_name: mistral-common`, `license: apache-2.0`, `inference: false`, tag `vllm`, and eight languages: en, fr, de, es, it, pt, nl, hi (**Observed** by static inspection).[^voxtral-mini-3b-card]

## Capabilities

- Dedicated transcription mode that by default predicts the source audio language and transcribes accordingly (**Reported**).[^voxtral-mini-3b-card]
- Long-form context: 32k token context length; up to 30 minutes of audio for transcription or 40 minutes for understanding (**Reported**).[^voxtral-mini-3b-card]
- Built-in audio Q&A and summarization: questions asked directly through audio and structured summaries without separate ASR and language models (**Reported**).[^voxtral-mini-3b-card]
- Natively multilingual with automatic language detection across the eight frontmatter languages (**Reported**).[^voxtral-mini-3b-card]
- Function calling straight from voice: spoken intents directly trigger backend functions, workflows, or API calls (**Reported**).[^voxtral-mini-3b-card]
- Retains the Ministral-3B text understanding backbone, including text-only chat (**Reported**).[^voxtral-mini-3b-card]

## Benchmarks

- The card's `Benchmark Results` section reports average word error rate over FLEURS, Mozilla Common Voice, and Multilingual LibriSpeech for audio, plus a text-understanding figure, but both are embedded remote PNG images with no numeric values in the captured text, so no WER or text score is recorded here (**Observed** by static inspection).[^voxtral-mini-3b-card]

## Inference envelope and defaults

- Supported frameworks are vLLM (recommended) and Transformers; sampling defaults are `temperature=0.2` with `top_p=0.95` for chat/audio understanding and `temperature=0.0` for transcription (**Reported**).[^voxtral-mini-3b-card]
- Multiple audios per message and multiple user turns with audio are supported; system prompts are not yet supported (**Reported**).[^voxtral-mini-3b-card]
- Version pins: vLLM >= 0.10.0 installed as `vllm[audio]` (pulls `mistral_common >= 1.8.1`); Transformers >= 4.54.0 with `mistral-common[audio]` / `mistral_common[audio]` on the client (**Reported**).[^voxtral-mini-3b-card]
- Running the checkpoint on GPU needs about 9.5 GB of GPU RAM in bf16 or fp16 (**Reported**).[^voxtral-mini-3b-card]

## vLLM serving and client use

- Offline smoke test: clone the vLLM repo and run `python examples/offline_inference/audio_language.py --num-audios 2 --model-type voxtral` (**Reported**).[^voxtral-mini-3b-card]
- Serve: `vllm serve mistralai/Voxtral-Mini-3B-2507 --tokenizer_mode mistral --config_format mistral --load_format mistral`; the card recommends the 24B Voxtral-Small-24B-2507 for server/client settings (**Reported**).[^voxtral-mini-3b-card]
- Audio-instruct client: OpenAI-compatible `client.chat.completions.create` with `mistral_common` `AudioChunk`/`TextChunk`/`UserMessage` content (multi-audio plus text) at `temperature=0.2`, `top_p=0.95`; multi-turn continues by appending the assistant message and a new user turn (**Reported**).[^voxtral-mini-3b-card]
- Transcription client: `mistral_common` `TranscriptionRequest(model, audio, language, temperature=0.0).to_openai(...)` sent via `client.audio.transcriptions.create` (**Reported**).[^voxtral-mini-3b-card]

## Transformers use

- Stack is `AutoProcessor` plus `VoxtralForConditionalGeneration`, loaded in `torch.bfloat16` on CUDA; chat input goes through `processor.apply_chat_template(conversation)` and generation uses `max_new_tokens=500` with prompt-token slicing and `skip_special_tokens=True` decoding (**Reported**).[^voxtral-mini-3b-card]
- Covered patterns: multi-audio plus text instruction, multi-turn with audio, text-only, audio-only, and batched conversations (**Reported**).[^voxtral-mini-3b-card]
- Transcription pattern: `processor.apply_transcription_request(language="en", audio=..., model_id=repo_id)` then the same `model.generate` plus decode fence (**Reported**).[^voxtral-mini-3b-card]

## Relationships

- Comparable small multilingual speech model: [Qwen3-ASR family](qwen3-asr-family.md) covers 0.6B/1.7B offline/streaming ASR with vLLM serving; cross-read it when choosing between a transcription-focused ASR checkpoint and Voxtral Mini's joint transcription plus audio-understanding and function-calling scope (**Synthesis**).[^voxtral-mini-3b-card]
- Serving consumer: [WhisperLiveKit](whisperlivekit.md) lists Voxtral among its pluggable ASR backends; read both when wiring Voxtral Mini into a low-latency streaming transcription pipeline (**Synthesis**).[^voxtral-mini-3b-card]
- Family neighbor: [Audio8 ASR Infinite](audio8-asr-infinite.md) inherits the Voxtral realtime audio architecture for native-streaming bilingual ASR, while this concept covers the non-realtime 3B audio-understanding checkpoint; use both when scoping Mistral-lineage audio checkpoints (**Synthesis**).[^voxtral-mini-3b-card]
- Large sibling: [Voxtral Small 24B 2507](voxtral-small-24b-2507.md) is the Mistral-Small-3-based 24B checkpoint with the same 8-language coverage, 30/40-minute context limits, and vLLM/Transformers usage at about 55 GB VRAM versus about 9.5 GB here; this card recommends it for server/client settings — read both when choosing between single-GPU and multi-GPU Mistral-lineage audio understanding (**Synthesis**).[^voxtral-mini-3b-card]
- Realtime sibling: [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) is the natively streaming Mistral transcription checkpoint (≈3.4B LM plus ≈970M causal audio encoder) with a latency-tunable delay knob and vLLM realtime serving; read both when choosing between joint audio understanding (this 3B card) and realtime transcription (**Synthesis**).[^voxtral-mini-3b-card]
- Packaging catalog: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) lists a `Voxtral-Mini-4B-Realtime` GGUF entry, a different realtime checkpoint from this 3B card; check that catalog before assuming edge packaging exists for this checkpoint (**Synthesis**).[^voxtral-mini-3b-card]

## Coverage and limits

- Source inspected statically only; no vLLM or Transformers install, no model download, no audio transcribed, and no WER, latency, or VRAM figure reproduced (**Synthesis**).[^voxtral-mini-3b-card]
- Benchmark PNGs (audio WER figure, text figure), the Voxtral blog post, arXiv 2507.13264, the Ministral 3B page, vLLM and Transformers repositories, `mistral-common` releases, and Hugging Face audio-sample datasets were linked but not fetched and are absent from `raw/`; all install, serve, and inference fences are transcribed, not executed (**Synthesis**).[^voxtral-mini-3b-card]
- All capability, language-coverage, context-length, version-pin, VRAM, and usage claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^voxtral-mini-3b-card]

[^voxtral-mini-3b-card]: [Voxtral Mini 3B 2507 model card](../raw/Voxtral-Mini-3B-2507.md) — locators: frontmatter (`library_name`, `language` 8-code list, `license`, `tags`, `inference`); header (Ministral-3B enhancement, transcription/translation/understanding positioning, blog and arXiv 2507.13264 links); `Key Features` (6 bullets: transcription mode with auto LID, 32k context with 30/40-minute limits, Q&A/summarization without separate ASR+LM, 8-language list, voice function calling, Ministral-3B text retention); `Benchmark Results > Audio` (FLEURS/Common Voice/MLSI WER figure, image-only) and `> Text` (figure, image-only); `Usage` (framework list, `temperature`/`top_p` defaults, multi-audio/multi-turn support, no-system-prompts note); `vLLM > Installation` (`vllm[audio]`, `mistral_common >= 1.8.1` check), `> Offline` (clone plus `audio_language.py --num-audios 2 --model-type voxtral`), `> Serve` (serve command, ~9.5 GB VRAM note, Small-24B server recommendation); `Audio Instruct` (client install, chat-completions fence); `Transcription` (client install, `TranscriptionRequest` fence); `Transformers` (version/install pins, five `apply_chat_template` fences, one `apply_transcription_request` fence, all with `max_new_tokens=500` bf16 generate/decode).
