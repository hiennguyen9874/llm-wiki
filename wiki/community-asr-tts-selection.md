---
type: Concept
title: Community-Reported Local ASR/TTS Selection
description: Community-reported local ASR/TTS tradeoffs and voice-agent practices from an r/LocalLLaMA thread, with model comparisons, VAD use, and regression practices.
tags: [stt, tts, vad, streaming, voice-cloning]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: reddit-asr-tts-thread
    resource: ../raw/good_asr_and_tts_models.md
    kind: documentation
    title: Good ASR and TTS models? r/LocalLLaMA thread capture
---

This thread captures community-reported preferences for local speech-to-text and text-to-speech in voice agents, comparing Whisper, Parakeet, Qwen3-ASR/TTS, Kokoro, Pocket TTS, OmniVoice, VoxCPM2, Chatterbox, VibeVoice, Nemotron streaming ASR, and smaller runtimes, plus reusable pipeline practices for VAD frontends, voice-design-to-clone workflows, evaluation leaderboards, and golden-clip regression checks; every comparative claim below is an unverified anecdote from anonymous commenters, not a measured result (**Reported**).[^reddit-asr-tts-thread]

## Source scope and request

- The thread starter reports using Whisper plus Kokoro with koboldcpp and asks for solid replacements, naming Qwen3-ASR and Qwen3-TTS as untested candidates; the stated need is English in both directions with Dutch as a nice-to-have bonus (**Reported**).[^reddit-asr-tts-thread]
- The capture holds the prompt plus 51 comments with anonymous authors, no capture date, and upstream links to the subreddit thread, the Hugging Face Open ASR Leaderboard, audio.cpp, Handy, Genie-TTS, MOSS-Transcribe-Diarize, and Chatterbox; per-comment vote tallies are omitted here as volatile and non-durable (**Reported**, with omission **Synthesis**).[^reddit-asr-tts-thread]

## ASR selection tradeoffs

- Parakeet is described as lightweight and fast with a CPU-optimized port that runs decently, while Whisper is described as more thorough on noisy speech with lower word error rate on mixed speakers and multilingual input but heavy on VRAM and slower; choice depends on requirements and hardware (**Reported**).[^reddit-asr-tts-thread]
- Autoregressive models like Whisper are characterized as usually slower than conformer-style models, which are characterized as faster with smaller variants runnable even on a microcontroller; the Hugging Face Open ASR Leaderboard ranking word error rate and realtime factor is recommended for use-case-specific selection (**Reported**).[^reddit-asr-tts-thread]
- Parakeet v3 is reported to support Dutch with good German experience from one commenter; FunASR plus OmniVoice is reported as a good stack for one commenter's multilingual-plus-speed need (**Reported**).[^reddit-asr-tts-thread]
- Whisper Large V3 Turbo is reported as very fast on the commenter's M1 Max and not worth further optimizing there; faster-whisper is reported as holding up better than vanilla Whisper in production on CPU-only boxes, and as hard to beat for stability without a specific reason to switch (**Reported**).[^reddit-asr-tts-thread]
- Nemotron 3.5 ASR Streaming 0.6B in streaming mode is named as one commenter's best ASR pick; Qwen3 ASR is named as another commenter's default after trying models in the Handy project; Qwen3-ASR is also characterized as strong but heavier on VRAM, and as streaming worse than Parakeet by one commenter (**Reported**).[^reddit-asr-tts-thread]
- VibeVoice ASR is described as stable and production-ready with speaker diarization as a plus; MOSS-Transcribe-Diarize is described as really good especially on Chinese (**Reported**).[^reddit-asr-tts-thread]
- Gemma 4 or Mistral Voxtral with audio input is suggested as an alternative producing optimized and cleaned output instead of a pure transcript, depending on use case (**Reported**).[^reddit-asr-tts-thread]

## TTS selection tradeoffs

- Kokoro plus Whisper is still called a strong combination; Kokoro is called the local latency king with no rush to swap it, while Qwen3-TTS is described as sounding better but slower; one commenter advises testing Qwen3-ASR/TTS against Whisper/Kokoro especially for non-English languages and speed (**Reported**).[^reddit-asr-tts-thread]
- Kokoro is reported to have consistent mispronunciations on some words by two commenters; its Hugging Face model page is noted in-thread as last updated April 2025, with no in-thread evidence of improvement elsewhere (**Reported**).[^reddit-asr-tts-thread]
- Pocket TTS is reported as a step up from Kokoro, barely bigger in size, much better, with cloning support, and as not noticeably worse than Qwen3-TTS for cloning voices made with Qwen3 VoiceDesign; one commenter pairs OmniVoice with VoxCPM2 for liked voice quality, while VoxCPM and Chatterbox are named as best for another commenter's language (**Reported**).[^reddit-asr-tts-thread]
- Qwen3-TTS 0.6B CustomVoice is named as one commenter's best TTS pick; faster Qwen3 TTS plus Whisper is reported as working well for another setup; F5-TTS and Kokoro are named as current favorites for quality-per-VRAM with Piper named for running on almost anything (**Reported**).[^reddit-asr-tts-thread]
- VibeVoice 7B is described as the largest model with best quality and emotion but not a stable model; smaller VibeVoice Realtime is described as pretty decent (**Reported**).[^reddit-asr-tts-thread]
- Echo TTS is described as really good but VRAM-expensive at 10 GB; Genie-TTS and Chatterbox are linked without in-thread evaluation detail (**Reported**).[^reddit-asr-tts-thread]
- A failure report states Pocket TTS output a choppy male voice for a female-voice attempt after about four minutes of trying; the counter-claim is that sample-audio quality may explain poor results (**Reported**).[^reddit-asr-tts-thread]

## Reusable pipeline practices

- Pair Qwen3-ASR with a VAD frontend instead of running it standalone to kill false-trigger issues; VAD is described as sitting on top of ASR/STT to detect when an utterance stops, with cheap CPU options sufficient and STT selection more important (**Reported**).[^reddit-asr-tts-thread]
- Silero VAD is the only named open-weight VAD, installable with `pip install silero-vad>=5.0.0` and auto-downloaded from Hugging Face (**Reported**).[^reddit-asr-tts-thread]
- Voice-design-to-clone workflow: create a voice with Qwen3-TTS-VoiceDesign, clone that generated voice with Pocket TTS, then use the cloned voice for the agent to keep personas consistent (**Reported**).[^reddit-asr-tts-thread]
- One implementation keeps a `personas/` directory with one folder per persona holding `reference_audio.wav`, `reference_text.txt`, and `voice_description.txt`; the UI writes a new voice description, VoiceDesign generates the folder, the reference audio/text drive the agent's selected persona, the voice description is also placed in the system prompt so the dialogue model is aware of the personality, each persona has its own memory directory, and latency is reported as sub-1s with a small/fast local model where the LLM backend drives latency; all code runs in Python as part of the voice-agent server, with snippets promised but absent from the capture (**Reported**).[^reddit-asr-tts-thread]
- Golden-clip regression practice: keep a tiny set of golden reference clips for the chosen local TTS and diff new output against them after any model or version change, because local models drift silently on updates like hosted ones (**Reported**).[^reddit-asr-tts-thread]
- Use the Hugging Face Open ASR Leaderboard at `https://huggingface.co/spaces/hf-audio/open_asr_leaderboard` for word-error-rate versus realtime-factor ranking by use case; a single RTX 5060 Ti is asserted in-thread as plenty for this selection task (**Reported**).[^reddit-asr-tts-thread]

## Tooling and runtimes

- audio.cpp at `https://github.com/0xShug0/audio.cpp` is recommended to simplify setup and evaluate a variety of models with good performance; favorites named are Qwen3-TTS and OmniVoice on RTX 3060 (**Reported**).[^reddit-asr-tts-thread]
- The Handy project at `https://github.com/cjpais/Handy` is reported as containing quite a few good models, with the commenter ending up on Qwen3 ASR (**Reported**).[^reddit-asr-tts-thread]
- faster-whisper is named for CPU-only production voice pipelines; Whisper Turbo is named for CPU-only constraint (**Reported**).[^reddit-asr-tts-thread]

## Contradictions

- Pocket TTS versus OmniVoice: one commenter enjoys Pocket TTS cloning at about Qwen3-TTS quality, faster, with streaming support unlike OmniVoice, and was not happy with OmniVoice; another calls Pocket TTS drop-dead garbage from a four-minute try while finding OmniVoice voice quality liked (paired with VoxCPM2); neither side gives audio, versions, or configs, so neither claim is chosen (**Reported**).[^reddit-asr-tts-thread]
- Whisper versus Parakeet: Whisper is favored for noisy, mixed-speaker, multilingual accuracy while Parakeet is favored for lightweight speed and streaming; one commenter recommends neither but picks Parakeet if forced while noting better newer models exist, so the correct pick stays requirement- and hardware-dependent (**Reported**).[^reddit-asr-tts-thread]
- Kokoro versus Qwen3-TTS: Kokoro is favored for local latency and Qwen3-TTS for sound quality with a speed penalty; no measurement in-thread resolves the tradeoff (**Reported**).[^reddit-asr-tts-thread]

## Relationships

- Uses [Pocket TTS](pocket-tts.md): the thread's voice-design-to-clone workflow and cloning-quality comparison target the CPU-first multilingual TTS system covered there; the personas-directory procedure and streaming contrast are new community-reported uses not present in that concept (**Synthesis**).[^reddit-asr-tts-thread]
- Uses [OmniVoice](omnivoice.md): the thread reports OmniVoice as an evaluation favorite in audio.cpp and as a liked voice-quality pick, and disputes its cloning satisfaction and streaming support relative to Pocket TTS (**Synthesis**).[^reddit-asr-tts-thread]
- Uses [Qwen3-ASR family](qwen3-asr-family.md): the thread names Qwen3-ASR as an upgrade candidate, a Handy-project default, and a strong but VRAM-heavy pick with worse streaming than Parakeet per one report; read that concept for the verified family scope, languages, and serving toolkit (**Synthesis**).[^reddit-asr-tts-thread]
- Uses [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md): the thread names this checkpoint as one commenter's streaming ASR pick (**Synthesis**).[^reddit-asr-tts-thread]
- Uses [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): the thread's Parakeet v3 Dutch/German note and Parakeet-streams-better-than-Whisper remark relate to the multilingual Parakeet TDT lineage covered there; no version-to-checkpoint mapping is asserted (**Synthesis**).[^reddit-asr-tts-thread]
- Uses [VibeVoice-1.5B](vibevoice-1.5b.md) and [VibeVoice-ASR](vibevoice-asr.md): the thread's VibeVoice 7B quality-versus-stability remark and VibeVoice ASR production-readiness plus diarization remark relate to that family; no size-to-checkpoint mapping beyond the names is asserted (**Synthesis**).[^reddit-asr-tts-thread]
- Uses [VoxCPM2](voxcpm2.md): the thread pairs it with OmniVoice for liked voice quality and names VoxCPM among best for one language (**Synthesis**).[^reddit-asr-tts-thread]
- Uses [Chatterbox TTS](chatterbox-tts.md): the thread names Chatterbox among best for one language and links its GitHub repository (**Synthesis**).[^reddit-asr-tts-thread]
- Uses [MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)](moss-transcribe-cpp-gguf.md): the thread's MOSS Transcribe plus diarize praise, especially on Chinese, relates to the packaged model covered there (**Synthesis**).[^reddit-asr-tts-thread]
- Uses [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md): the thread's audio.cpp evaluation recommendation and RTX 3060 favorites relate to that packaging catalog (**Synthesis**).[^reddit-asr-tts-thread]

## Coverage and limits

- Source inspected statically only; no model installed, no audio transcribed or synthesized, no latency, VRAM, WER, or quality claim reproduced, and no linked repository, leaderboard, or model page fetched beyond the URLs quoted above (**Synthesis**).[^reddit-asr-tts-thread]
- Authors are anonymous in the capture (`unknown` except the prompt author), with no capture date, no hardware details for most claims, no model versions or configs, and no audio or measurement protocol; all comparative and performance claims are therefore **Reported** and **Unverified**, and this concept stays `draft` until primary sources or reproductions corroborate them (**Synthesis**).[^reddit-asr-tts-thread]
- Excluded as non-durable: pleasantries and follow-up promises (audio.cpp thanks, snippet requests), exact vote tallies, the two-word `Try liquid` comment for lack of identifiable model and evidence, and full sample URLs and repository contents behind the linked attachments (**Synthesis**).[^reddit-asr-tts-thread]
- Possible entity ambiguity persists: the thread's `OmniVoice` in the `FunASR plus OmniVoice` stack is treated here as the TTS model in [OmniVoice](omnivoice.md) only as a working link, not a verified identity match; `Echo`, `Genie-TTS`, `liquid`, `F5-TTS`, `Piper`, `Kokoro` checkpoints, and `Handy` internals have no primary-source concept in this wiki from this ingest (**Synthesis**).[^reddit-asr-tts-thread]
- Model-release and performance remarks carry `stale_after: 2027-10-06` per the `stt` and `tts` domain rules (**Synthesis**).[^reddit-asr-tts-thread]

[^reddit-asr-tts-thread]: [Good ASR and TTS models? r/LocalLLaMA thread capture](../raw/good_asr_and_tts_models.md) — locators: title plus upstream link `https://www.reddit.com/r/LocalLLaMA/comments/1v1auga/good_asr_and_tts_models/` and prompt paragraph (Whisper plus Kokoro with koboldcpp, Qwen3-ASR/TTS untested, English both directions with Dutch bonus); `Comments 51` section — Parakeet lightweight/fast versus Whisper noisy/mixed-speaker/VRAM remarks; audio.cpp recommendation; Open ASR Leaderboard plus autoregressive-versus-conformer remarks with `https://huggingface.co/spaces/hf-audio/open_asr_leaderboard`; FunASR plus OmniVoice stack remark; Parakeet v3 Dutch/German remark; PocketTTS cloning plus Qwen3 VoiceDesign workflow with `personas/` (`reference_audio.wav`, `reference_text.txt`, `voice_description.txt`), system-prompt, memory-directory, and sub-1s remarks; PocketTTS-versus-OmniVoice dispute including choppy-male-voice failure report and streaming remark; OmniVoice plus VoxCPM2, VoxCPM/Chatterbox, and Chatterbox-link remarks; Nemotron-3.5-asr-streaming-0.6B plus Qwen3-TTS-0.6B-CustomVoice picks; faster-whisper production plus Kokoro-checkpoint plus Qwen3-ASR-with-VAD remarks; Silero VAD install fence `pip install silero-vad>=5.0.0`; audio.cpp favorites on RTX 3060 with `https://github.com/0xShug0/audio.cpp`; Whisper-plus-Kokoro plus upgrade-test remark; VibeVoice-7B quality-versus-stability plus VibeVoice-ASR diarization remarks; Genie-TTS link `https://github.com/High-Logic/Genie-TTS`; faster-Qwen3-TTS plus Whisper remarks; Gemma-4/Mistral-Voxtral audio-input remark; Parakeet-plus-Kokoro and Whisper-turbo-CPU remarks; Parakeet-fast versus Whisper-large-v3-accuracy plus F5-TTS/Kokoro quality-per-VRAM, Piper, and golden-clip remarks; faster-whisper stability remark; Handy link `https://github.com/cjpais/Handy` plus Qwen3-ASR default remark; Echo 10GB VRAM remark; Kokoro-latency-king versus Qwen3-TTS-slower plus Parakeet-streams-better plus Qwen3-ASR-VRAM remarks; MOSS link `https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize` plus Chinese remark; Chatterbox link `https://github.com/resemble-ai/chatterbox`.
