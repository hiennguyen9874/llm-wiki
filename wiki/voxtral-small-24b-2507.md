---
type: Concept
title: Voxtral Small 24B 2507
description: Mistral AI 24B-scale audio-text model built on Mistral Small 3 for transcription with auto language detection, audio Q&A and summarization, voice-triggered function calling, and 30–40 minute long-form context with vLLM and Transformers inference.
tags: [stt, asr, audio-understanding, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: voxtral-small-24b-card
    resource: ../raw/Voxtral-Small-24B-2507.md
    kind: documentation
    title: Voxtral Small 24B 2507 model card
---

Voxtral Small 24B 2507 (`mistralai/Voxtral-Small-24B-2507`) is Mistral AI's 24B-scale enhancement of Mistral Small 3 with native audio input, covering dedicated transcription with automatic source-language prediction, long-form audio (30 minutes for transcription, 40 minutes for understanding in 32k context), direct audio Q&A and summarization without a separate ASR plus language-model stack, and voice-triggered function calling, served via vLLM (recommended) or Transformers (**Reported**).[^voxtral-small-24b-card]

## Model identity and lineage

- Card title is `Voxtral Small 1.0 (24B) - 2507`; checkpoint is `mistralai/Voxtral-Small-24B-2507`; backbone is `mistralai/Mistral-Small-24B-Base-2501` with retained text performance (the header says Mistral Small 3, the features list says Mistral Small 3.1; both wordings are recorded without choosing between them); companion pointers are the Voxtral blog post and research paper arXiv 2507.13264 (**Reported**).[^voxtral-small-24b-card]
- Frontmatter declares `library_name: vllm`, `pipeline_tag: audio-text-to-text`, `license: apache-2.0`, `inference: false`, tag `vllm`, and eight languages: en, fr, de, es, it, pt, nl, hi (**Observed** by static inspection).[^voxtral-small-24b-card]

## Capabilities

- Dedicated transcription mode that by default predicts the source audio language and transcribes accordingly (**Reported**).[^voxtral-small-24b-card]
- Long-form context: 32k token context length; up to 30 minutes of audio for transcription or 40 minutes for understanding (**Reported**).[^voxtral-small-24b-card]
- Built-in audio Q&A and summarization: questions asked directly through audio and structured summaries without separate ASR and language models (**Reported**).[^voxtral-small-24b-card]
- Natively multilingual with automatic language detection across the eight frontmatter languages (**Reported**).[^voxtral-small-24b-card]
- Function calling straight from voice: spoken intents directly trigger backend functions, workflows, or API calls; the card labels this support experimental (**Reported**).[^voxtral-small-24b-card]
- Retains the Mistral Small 3 text understanding backbone, including text-only chat (**Reported**).[^voxtral-small-24b-card]

## Benchmarks

- The card's `Benchmark Results` section reports average word error rate over FLEURS, Mozilla Common Voice, and Multilingual LibriSpeech for audio, plus a text-understanding figure, but both are embedded remote PNG images with no numeric values in the captured text, so no WER or text score is recorded here (**Observed** by static inspection).[^voxtral-small-24b-card]

## Inference envelope and defaults

- Supported frameworks are vLLM (recommended) and Transformers; sampling defaults are `temperature=0.2` with `top_p=0.95` for chat/audio understanding and `temperature=0.0` for transcription (**Reported**).[^voxtral-small-24b-card]
- Multiple audios per message and multiple user turns with audio are supported; function calling is supported; system prompts are not yet supported (**Reported**).[^voxtral-small-24b-card]
- Version pins: vLLM >= 0.10.0 installed as `vllm[audio]` (pulls `mistral_common >= 1.8.1`); Transformers >= 4.54.0 with `mistral-common[audio]` / `mistral_common[audio]` on the client (**Reported**).[^voxtral-small-24b-card]
- Running the checkpoint on GPU needs about 55 GB of GPU RAM in bf16 or fp16 (**Reported**).[^voxtral-small-24b-card]

## vLLM serving and client use

- Offline smoke test: clone the vLLM repo and run `python examples/offline_inference/audio_language.py --num-audios 2 --model-type voxtral` (**Reported**).[^voxtral-small-24b-card]
- Serve: `vllm serve mistralai/Voxtral-Small-24B-2507 --tokenizer_mode mistral --config_format mistral --load_format mistral --tensor-parallel-size 2 --tool-call-parser mistral --enable-auto-tool-choice`; the card recommends a server/client setting for this checkpoint (**Reported**).[^voxtral-small-24b-card]
- Audio-instruct client: OpenAI-compatible `client.chat.completions.create` with `mistral_common` `AudioChunk`/`TextChunk`/`UserMessage` content (multi-audio plus text) at `temperature=0.2`, `top_p=0.95`; multi-turn continues by appending the assistant message and a new user turn (**Reported**).[^voxtral-small-24b-card]
- Transcription client: `mistral_common` `TranscriptionRequest(model, audio, language, temperature=0.0).to_openai(...)` sent via `client.audio.transcriptions.create` (**Reported**).[^voxtral-small-24b-card]
- Function-calling client: define the tool with `mistral_common` `Tool`/`Function`, transcribe the spoken request first, then call `client.chat.completions.create` with `tools=[tool.to_openai()]` and read `response.choices[0].message.tool_calls` (**Reported**).[^voxtral-small-24b-card]

## Transformers use

- Stack is `AutoProcessor` plus `VoxtralForConditionalGeneration`, loaded in `torch.bfloat16` on CUDA; chat input goes through `processor.apply_chat_template(conversation)` and generation uses `max_new_tokens=500` with prompt-token slicing and `skip_special_tokens=True` decoding (**Reported**).[^voxtral-small-24b-card]
- Covered patterns: multi-audio plus text instruction, multi-turn with audio, text-only, audio-only, and batched conversations (**Reported**).[^voxtral-small-24b-card]
- Transcription pattern: `processor.apply_transcription_request(language="en", audio=..., model_id=repo_id)` then the same `model.generate` plus decode fence (**Reported**).[^voxtral-small-24b-card]

## Relationships

- Smaller sibling: [Voxtral Mini 3B 2507](voxtral-mini-3b-2507.md) is the Ministral-3B-based checkpoint with the same 8-language coverage, the same 30/40-minute context limits, and the same vLLM/Transformers usage at about 9.5 GB VRAM versus about 55 GB here; its card recommends this 24B checkpoint for server/client settings — read both when choosing between single-GPU and multi-GPU Mistral-lineage audio understanding (**Synthesis**).[^voxtral-small-24b-card]
- Realtime sibling: [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) is the natively streaming Mistral transcription checkpoint (≈3.4B LM plus ≈970M causal audio encoder) with a latency-tunable delay knob and vLLM realtime serving; read both when choosing between joint audio understanding (this 24B card) and realtime transcription (**Synthesis**).[^voxtral-small-24b-card]
- Comparable small multilingual speech model: [Qwen3-ASR family](qwen3-asr-family.md) covers 0.6B/1.7B offline/streaming ASR with vLLM serving; cross-read it when choosing between a transcription-focused ASR checkpoint and Voxtral Small's joint transcription plus audio-understanding and function-calling scope (**Synthesis**).[^voxtral-small-24b-card]
- Serving consumer: [WhisperLiveKit](whisperlivekit.md) lists Voxtral among its pluggable ASR backends; read both when wiring a Voxtral checkpoint into a low-latency streaming transcription pipeline (**Synthesis**).[^voxtral-small-24b-card]
- Packaging catalog: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) lists a `Voxtral-Mini-4B-Realtime` GGUF entry, a different realtime checkpoint from this 24B card; check that catalog before assuming edge packaging exists for this checkpoint (**Synthesis**).[^voxtral-small-24b-card]

## Coverage and limits

- Source inspected statically only; no vLLM or Transformers install, no model download, no audio transcribed, and no WER, latency, or VRAM figure reproduced (**Synthesis**).[^voxtral-small-24b-card]
- Benchmark PNGs (audio WER figure, text figure), the Voxtral blog post, arXiv 2507.13264, the Mistral Small 3 base page, vLLM and Transformers repositories, `mistral-common` releases, and Hugging Face audio-sample datasets were linked but not fetched and are absent from `raw/`; all install, serve, and inference fences are transcribed, not executed (**Synthesis**).[^voxtral-small-24b-card]
- All capability, language-coverage, context-length, version-pin, VRAM, and usage claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^voxtral-small-24b-card]

[^voxtral-small-24b-card]: [Voxtral Small 24B 2507 model card](../raw/Voxtral-Small-24B-2507.md) — locators: frontmatter (`library_name`, `language` 8-code list, `license`, `tags`, `inference`, `base_model` Mistral-Small-24B-Base-2501, `pipeline_tag`); header (Mistral-Small-3 enhancement, transcription/translation/understanding positioning, blog and arXiv 2507.13264 links); `Key Features` (6 bullets: transcription mode with auto LID, 32k context with 30/40-minute limits, Q&A/summarization without separate ASR+LM, 8-language list, voice function calling, Small-3.1 text retention); `Benchmark Results > Audio` (FLEURS/Common Voice/MLSI WER figure, image-only) and `> Text` (figure, image-only); `Usage` (framework list, `temperature`/`top_p` defaults, multi-audio/multi-turn support, function-calling support, no-system-prompts note); `vLLM > Installation` (`vllm[audio]`, `mistral_common >= 1.8.1` check), `> Offline` (clone plus `audio_language.py --num-audios 2 --model-type voxtral`), `> Serve` (serve command with `--tensor-parallel-size 2 --tool-call-parser mistral --enable-auto-tool-choice`, ~55 GB VRAM note, server/client recommendation); `Audio Instruct` (client install, chat-completions fence); `Transcription` (client install, `TranscriptionRequest` fence); `Function Calling` (experimental note, tool-definition plus transcribe-then-call fence); `Transformers` (version/install pins, five `apply_chat_template` fences, one `apply_transcription_request` fence, all with `max_new_tokens=500` bf16 generate/decode).
