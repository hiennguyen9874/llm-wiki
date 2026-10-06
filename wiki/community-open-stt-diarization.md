---
type: Concept
title: Community-Reported Open STT and Realtime Diarization Selection
description: Community-reported open STT and realtime diarization tradeoffs for Wispr Flow-style dictation versus live meeting transcription, comparing Parakeet, Whisper variants, Qwen3-ASR, and diarization stacks.
tags: [stt, vad, streaming]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: reddit-open-stt
    resource: ../raw/whats_the_best_open_speech_to_text_today.md
    kind: documentation
    title: What's the best open speech to text today? r/LocalLLaMA thread capture
---

This thread collects community-reported picks for open speech-to-text plus realtime diarization as a local alternative to Wispr Flow-style tools, separating fast dictation and batch transcription (Parakeet, Whisper variants, Qwen3-ASR) from the harder speaker-diarization half (pyannote/diart, NeMo streaming, offline WhisperX plus pyannote), with side notes on streaming wrappers, English-only low-latency options, CPU/quantization tradeoffs, and a local-first dictation product disclosure; every comparative or performance claim below is an unverified anecdote from anonymous commenters, not a measured result (**Reported**).[^reddit-open-stt]

## Source scope and request

- The starter (u/zxyzyxz) asks for a realtime setup with diarization as an alternative to Wispr Flow and similar tools, reports knowing MacParakeet (Parakeet-based) and Whisper models, and asks what newer realtime models exist; vote count 8 and 36 comments are preserved here as volatile context, not durable findings (**Reported**).[^reddit-open-stt]
- The capture holds the prompt plus 36 comments with anonymous authors except the starter, no capture date, and upstream links to the subreddit thread, the Hugging Face Open ASR Leaderboard, a YouTube Whisper test, the pfspeak TTS runtime, and a TypeWhisper disclosure; per-comment vote tallies are omitted here as volatile and non-durable (**Reported**, with omission **Synthesis**).[^reddit-open-stt]

## ASR selection tradeoffs

- The Hugging Face Open ASR Leaderboard at `https://huggingface.co/spaces/hf-audio/open_asr_leaderboard` is recommended as the selection resource, with the guidance to pick the lowest word error rate among open weights; one reply notes the metrics are hard to map to a use case despite the page's explanations (**Reported**).[^reddit-open-stt]
- NVIDIA Parakeet 0.6 TDT v3 is reported as better than or equal to Whisper large (v3/large phrasing varies by comment) depending on language and about ten times faster; TDT v2 is reported as better for English-only use, and Parakeet v2 is reported as much faster than v3 for English (**Reported**).[^reddit-open-stt]
- Whisper baselines still satisfy several commenters: faster-whisper large-v3 for voice satellites, faster-whisper generally, large-v2 preferred over v3 by one commenter, and one claim of about 99.9% local accuracy with no need to switch; Vosk is named once without evaluation (**Reported**).[^reddit-open-stt]
- Qwen3-ASR is reported by two commenters as the best of Parakeet, Whisper large v3.5, FunASR/FunASR-adjacent, and Qwen3-ASR for their use case, hallucinating the least and rejecting non-speech better; the 0.6B checkpoint is reported to beat the others, running as fast or slightly faster than faster-whisper 3.5 while being more reliable every time, with Parakeet described as really fast but getting utterances wrong enough to be not worth it (**Reported**).[^reddit-open-stt]
- Quantization tradeoff left open: Parakeet's quantized version is reported to lose very little performance, run blazing fast, and run on most CPUs; the follow-up asks whether Qwen3-ASR (noting the 1.7B wins benchmarks) shares that CPU/quantization behavior or trades speed and weight, with no answer in the capture (**Reported**).[^reddit-open-stt]
- One Sherpa (sherpa-onnx) report calls it pretty amazing for STT without any comparison to other models (**Reported**).[^reddit-open-stt]

## Realtime versus diarization split

- The thread's most reusable framing separates use cases: short/basic dictation (Apple Dictation good enough), batch transcription (Whisper variants solid local/offline), realtime voice typing (latency, correction behavior, hotkeys, app integration, and post-processing matter as much as the model), and realtime diarization as the harder bit that dictation-grade tools do not solve (**Reported**).[^reddit-open-stt]
- A companion framing states realtime transcription and realtime diarization are two separate problems most tools just glue together: Parakeet is the fast text side but mostly English plus some European languages; for more realtime languages, Whisper large-v3-turbo streamed through whisper_streaming or WhisperLive works well because Whisper itself is not streaming and those wrappers chunk it; turbo is reported as almost as accurate as large-v3 but much faster; Moonshine is named for lowest-latency English-only use (**Reported**).[^reddit-open-stt]
- Diarization is repeatedly named the weak half: pyannote is the standard with diart running it live, NeMo now has streaming diarization, live diarization is noticeably worse than offline, and a batch pass afterwards with WhisperX plus pyannote gives way cleaner speaker labels; one weak suggestion mentions separating voices by frequency without a stack or measurement (**Reported**).[^reddit-open-stt]
- Follow-ups probe the deployment boundary: whether everything must stay strictly on-device or some cloud processing is acceptable for the non-live part, with one reporter using local tools live then WhisperAI uploads for diarization later (**Reported**).[^reddit-open-stt]

## Tooling and product disclosure

- TypeWhisper is disclosed by its builder as a local/offline-capable dictation product (not a diarization solution): profiles, prompts/post-processing, dictionary/snippets, engine choice, insertion workflows, history, and recorder/file transcription rather than one magic model; the builder asks whether the need is live captions/meeting notes, voice typing, or recording transcription (**Reported**).[^reddit-open-stt]
- Its reported stack is engine/plugin based: local WhisperKit/Parakeet on macOS, whisper.cpp/sherpa-onnx-style local engines on Windows, plus optional cloud engines; the product work is described as everything after model text (insertion, cleanup, per-app/site/hotkey switching); licensing is stated as GPLv3 with commercial licensing for non-GPL/proprietary use and maintained packaging/support, not a secret model (**Reported**).[^reddit-open-stt]
- MacParakeet is named in the prompt as the known FOSS Parakeet-based reference; the live-meeting multi-speaker reply recommends diarization-first tools over dictation products (**Reported**).[^reddit-open-stt]
- A beta TTS runtime link (`https://github.com/SamReynoso/pfspeak`) is corrected in-thread as off-topic because the request is speech-to-text, not text-to-speech; it carries no STT evaluation (**Reported**).[^reddit-open-stt]

## Contradictions

- Parakeet versus Whisper versus Qwen3-ASR: Parakeet is favored for speed (about 10x, quantized CPU-friendly), Whisper variants for adequate local accuracy and turbo efficiency, and Qwen3-ASR 0.6B for reliability and non-speech rejection despite Parakeet's raw speed; no shared audio, config, or WER protocol resolves the pick, so it stays requirement- and hardware-dependent (**Reported**).[^reddit-open-stt]
- Live versus offline diarization: live stacks (diart/pyannote live, NeMo streaming) are favored for immediacy while WhisperX plus pyannote batch is favored for cleaner speaker labels; no DER or cpWER measurement in-thread resolves the tradeoff (**Reported**).[^reddit-open-stt]

## Relationships

- Uses [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): the thread's Parakeet-v3-versus-Whisper-large speed/accuracy and English-plus-European scope remarks relate to the multilingual Parakeet TDT lineage covered there; the thread gives no checkpoint-to-version mapping beyond the v2/v3 names (**Synthesis**).[^reddit-open-stt]
- Uses [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md): the thread's English-only TDT-v2 preference relates to the English-only Parakeet checkpoint covered there (**Synthesis**).[^reddit-open-stt]
- Uses [Qwen3-ASR family](qwen3-asr-family.md): the thread's Qwen3-ASR 0.6B reliability and 1.7B benchmark remarks relate to the 0.6B/1.7B family covered there; read that concept for verified language scope, streaming/offline behavior, and serving toolkit (**Synthesis**).[^reddit-open-stt]
- Uses [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md): the thread's offline-diarization-is-cleaner advice relates to the offline diarization approach covered there; the thread names pyannote/WhisperX rather than a Sortformer checkpoint (**Synthesis**).[^reddit-open-stt]
- Uses [Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md) and [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md): the thread's live-diarization-worse-than-offline and NeMo-streaming remarks relate to streaming diarization latency/accuracy tradeoffs covered there (**Synthesis**).[^reddit-open-stt]
- Uses [Nemotron 3 Diarization](nemotron-3-diarization.md): the thread's NeMo streaming diarization remark relates to the streaming/offline diarization model covered there (**Synthesis**).[^reddit-open-stt]
- Uses [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md): the thread's glue-transcription-plus-diarization framing relates to the joint streaming multitalker approach covered there; the thread proposes no joint model (**Synthesis**).[^reddit-open-stt]
- Uses [Community-Reported Local ASR/TTS Selection](community-asr-tts-selection.md): the companion thread concept covers local ASR/TTS picks, VAD frontends, leaderboard ranking, and Handy/audio.cpp practices from a different capture; read both as unverified community reports, not measurements (**Synthesis**).[^reddit-open-stt]
- Uses [Community-Reported Noisy On-Premise STT Selection](community-noisy-call-stt.md): the companion thread concept covers noisy-call Parakeet-versus-Whisper tradeoffs with preprocessing and CPU/quantization notes; this concept adds the realtime-dictation versus live-diarization split (**Synthesis**).[^reddit-open-stt]
- Uses [Community-Reported Usable STT for Voice Agents](community-usable-stt-voice-agents.md): the companion thread concept covers live-agent usable-text, endpointing, and barge-in evaluation; this concept adds open-model and diarization-stack selection (**Synthesis**).[^reddit-open-stt]

## Coverage and limits

- Source inspected statically only; no model installed, no audio transcribed, no latency, WER, hallucination-rate, non-speech-rejection, or diarization-accuracy claim reproduced, and no linked leaderboard, repository, video, or model page fetched beyond the URLs quoted above (**Synthesis**).[^reddit-open-stt]
- Authors are anonymous in the capture (`unknown` except the prompt author), with no capture date, no hardware details for most claims, no model versions or configs beyond the names quoted, and no audio or measurement protocol; all comparative and performance claims are therefore **Reported** and **Unverified**, and this concept stays `draft` until primary sources or reproductions corroborate them (**Synthesis**).[^reddit-open-stt]
- Excluded as non-durable: exact vote tallies, pleasantries and re-read prompts (`Reread my post`, `why switch if Whisper is good`), the unevaluated YouTube Whisper test link, the pfspeak TTS beta beyond its off-topic correction, and full repository or video contents behind the linked attachments (**Synthesis**).[^reddit-open-stt]
- Possible entity ambiguity persists: thread names such as `Whisper 3 large`, `large-v3`, `large v3.5`, `turbo`, `faster-whisper 3.5`, `FunASR/funasr`, `Qwen3 ASR`, `Parakeet v2/v3`, `MacParakeet`, `WhisperKit`, `whisper.cpp`, `sherpa-onnx`, `whisper_streaming`, `WhisperLive`, `Moonshine`, `pyannote`, `diart`, `WhisperX`, `WhisperAI`, `Vosk`, `Apple Dictation`, and `Wispr Flow` have no version-to-checkpoint mapping asserted here and no primary-source concept in this wiki from this ingest except where linked above (**Synthesis**).[^reddit-open-stt]
- Model-release and performance remarks carry `stale_after: 2027-10-06` per the `stt` and `vad` domain rules (**Synthesis**).[^reddit-open-stt]

[^reddit-open-stt]: [What's the best open speech to text today? r/LocalLLaMA thread capture](../raw/whats_the_best_open_speech_to_text_today.md) — locators: title plus upstream link `https://www.reddit.com/r/LocalLLaMA/comments/1u9ggke/whats_the_best_open_speech_to_text_today/` and prompt paragraph (Wispr Flow alternative, realtime diarization, MacParakeet/Parakeet/Whisper known); `Comments 36` section — Open ASR Leaderboard `https://huggingface.co/spaces/hf-audio/open_asr_leaderboard` plus lowest-WER and metrics-confusion remarks; Parakeet-0.6-TDT-v3 versus Whisper-3-large 10x remark; TDT-v2 English-only remark; Parakeet-v2-faster-than-v3 remark; faster-whisper-large-v3, faster-whisper, large-v2, 99.9-accuracy, and Vosk remarks; Qwen3-ASR best/hallucination/non-speech remarks plus 0.6B-versus-faster-whisper-3.5 and Parakeet-utterance-error remarks plus quantized-Parakeet-versus-Qwen-1.7B question; dictation/batch/voice-typing/diarization use-case split plus TypeWhisper disclosure (profiles/prompts/dictionary/engine choice, not diarization) and workflow question; live-meeting multi-speaker reply; TypeWhisper stack (WhisperKit/Parakeet macOS, whisper.cpp/sherpa-onnx Windows, cloud-optional, GPLv3/commercial) plus MacParakeet-FOSS comparison; frequency-separation suggestion; YouTube `https://youtu.be/hUGEh0NALBk` Whisper remark plus 4-years-since-Whisper reply; Sherpa-amazing remark; transcription-versus-diarization glue remark with Parakeet-English-plus-European, large-v3-turbo via whisper_streaming/WhisperLive chunking, turbo-accuracy/speed, and Moonshine remarks; pyannote/diart/NeMo-streaming, live-worse-than-offline, and WhisperX-plus-pyannote remarks; local-live plus WhisperAI-upload and on-device-versus-cloud remarks; pfspeak `https://github.com/SamReynoso/pfspeak` TTS off-topic correction.
