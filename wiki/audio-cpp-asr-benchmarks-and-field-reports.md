---
type: Concept
title: audio.cpp ASR Benchmarks and Field Reports
description: Maintainer-reported RTX 5090 ASR figures for audio.cpp (Nemotron 3.5, Higgs Audio STT, VibeVoice ASR, Voxtral Mini 4B Realtime, plus VoxCPM2 streaming TTS) with third-party French-meeting field reports on session reuse, short-chunk empty output, mp3 input, and language drift.
tags: [stt, asr, streaming, benchmark, audio-cpp, gguf, field-report, pipeline]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T21:00:00Z }
stale_after: 2027-04-21
sources:
  - id: audiocpp-4-asr-thread
    resource: ../raw/audiocpp_what_does_the_fox_say_4_asr_models.md
    kind: documentation
    title: "audio.cpp: What Does the Fox Say — 4 ASR models, initial streaming (r/LocalLLaMA, updates to 07/21/2026)"
---

The [audio.cpp](audio-cpp-framework.md) maintainer's thread announces four ASR/STT ports (Nemotron 3.5 ASR, Higgs Audio STT, VibeVoice ASR, Hviske ASR for Danish only) with first streaming support, reporting 1.07x–2.41x speedups over Python, and headlines Nemotron transcribing 327.6 s of audio in 2.17 s offline on an RTX 5090 at 3.18% WER (**Reported**).[^audiocpp-4-asr-thread] Its comments add the most useful material for a VAD → STT loop: a third-party meeting-transcription team's real-audio results and two failure modes (empty output on reused sessions, silently empty text on short single-clip requests), all **Reported** and unreproduced here.[^audiocpp-4-asr-thread]

## Maintainer benchmark: ASR, no quantization (RTX 5090)

Ratio and RTF columns check out by arithmetic on the captured numbers (e.g. 327.6 s / 2.17 s ≈ 151x, RTF 0.0066); the file's language and content are not stated, and the post gives no per-model Python baseline for these rows (**Reported**; arithmetic **Observed**).[^audiocpp-4-asr-thread]

| Model | Mode | Audio | TTFT | Wall | RTF | WER | Peak VRAM |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Nemotron | Offline | 327.6 s | n/a | 2.17 s | 0.0066 | 3.18% | 8,294 MiB |
| Nemotron | SSE streaming | 327.6 s | 308 ms | 11.62 s | n/a | 3.18% | 4,382 MiB |
| Nemotron | SSE one-shot | 1,800 s | n/a | 53.66 s | 0.0298 | 3.45% | 4,167 MiB |
| Higgs STT | Offline | 327.6 s | n/a | 11.17 s | 0.0341 | 3.95% | 12,519 MiB |
| Higgs STT | SSE streaming | 327.6 s | 468 ms | 14.46 s | n/a | 3.95% | 6,945 MiB |
| VibeVoice | Offline | 327.6 s | n/a | 19.24 s | 0.0587 | 0.66% | 25,833 MiB |
| VibeVoice | Offline | 1,800 s | n/a | 123.72 s | 0.0687 | 1.51% | 31,209 MiB |

- Reading: Nemotron has the best speed/VRAM trade; its streaming path produced the same WER with about half the VRAM and a 307–308 ms TTFT, but needed about 5x the wall time of offline for the same file. VibeVoice gave the lowest WER (0.66%) but is the heaviest (about 26–31 GB). Higgs STT sits between, and its streaming path is described as more experimental because the reference behavior is less straightforward (**Reported**; interpretation **Synthesis**).[^audiocpp-4-asr-thread]
- Model pages: [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md), [Higgs Audio v3 STT](higgs-audio-v3-stt.md) (the thread says "Higgs Audio STT" without a version, so the match is **Synthesis**), [VibeVoice-ASR](vibevoice-asr.md).

## Voxtral Mini 4B Realtime ASR streaming (07/18/2026 update, RTX 5090)

- CLI offline over 27.394 s of audio: BF16 2,312.030 ms session wall (RTF 0.0844, 11.85x); Q8_0 1,671.272 ms (RTF 0.0610, 16.39x) (**Reported**).[^audiocpp-4-asr-thread]
- Server, streaming mode plus multipart upload: BF16 server TTFT 208.786 ms (client 210.831 ms) at 10,082 MiB peak VRAM; Q8_0 170.508 ms (client 173.336 ms) at 6,495 MiB (**Reported**).[^audiocpp-4-asr-thread]
- Long-form 30-minute file, streaming plus multipart upload: BF16 411.807 s client wall (RTF 0.2288, 4.37x, 12,595 MiB); Q8_0 358.631 s (RTF 0.1992, 5.02x, 8,990 MiB) (**Reported**).[^audiocpp-4-asr-thread]
- Q8_0 is faster and uses about 36% less peak VRAM at the short-clip server point (6,495 vs 10,082 MiB; **Synthesis**, arithmetic). Model page: [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md); the GGUF package is catalogued in [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md).

## Streaming TTS data point (VoxCPM2, SSE)

- For 314.6 s of generated audio: memory-saver on gives 547 ms TTFT, 56.65 s wall, 7,638 MiB; memory-saver off gives 308 ms TTFT, 55.75 s wall, 9,091 MiB (about 5.6x real time either way; **Reported**, ratio **Synthesis**). The post describes streaming as initial: VoxCPM2 accepts text incrementally and returns audio chunks, and Nemotron streams results over SSE (**Reported**).[^audiocpp-4-asr-thread] See [VoxCPM2](voxcpm2.md).

## Third-party field reports (TranscrIA, French business meetings)

The commenter's corpus is real narrowband phone-bridge meeting audio with overlapping speakers, scored against an edited human transcript, so a good WER is "forty-something percent" and only deltas between engines matter; their numbers are not comparable to the maintainer's 3.18% on (apparently) clean audio. Attribution is by content: the capture's bylines are unreliable (**Reported**; **Synthesis** on comparability).[^audiocpp-4-asr-thread]

| Item | Result as reported |
| --- | --- |
| Qwen3-ASR 0.6B | 0.56 WER overall, 0.42 excluding one chaotic window; within about 5% relative of their production GPU engines (Whisper large-v3, Voxtral 3B); 7–10 s per 5-minute window on one 3090 |
| Qwen3-ASR 1.7B | 0.42 WER on 8/8 windows (second best of everything they measured), best single window 0.19, about 12 s per 5-minute window, about 4 GB weights; stutter loops on one chaotic multi-speaker opening (0.88 vs 1.55 for the 0.6B) |
| Nemotron 3.5 ASR | Strong French; after the maintainer's session fix, 0.49 WER on 8/8 windows at about 2 s per 5-minute window, matching parakeet.cpp for the same model at a quarter of the wall time |
| Kroko FR zipformer2 community model | Matched their best GPU engine on CPU only (155 MB weights, 8 threads); shipped as a built-in backend |

All four rows are **Reported** by one team using one harness; see [Qwen3-ASR family](qwen3-asr-family.md) and [Kroko ASR support](#model-requests-and-roadmap-replies) below.[^audiocpp-4-asr-thread]

### Failure modes found

1. **Empty text from the second request on a reused server session (Nemotron).** First request good, restart fixes it; same model under parakeet.cpp answered three identical requests, so the tester attributed it to the audio.cpp runtime. The maintainer found and fixed it in a `main` commit (tester's pinned commit moved `3b4aed9` → `3982dfb`); the tester then confirmed three identical back-to-back requests worked and a previously always-empty window transcribed (**Reported**, fix confirmed by reporter).[^audiocpp-4-asr-thread]
2. **mp3 input returns HTTP 500 (`invalid WAV RIFF header`).** The maintainer states audio.cpp does not really handle mp3, calls it a gap, and says the server has had less attention than the core engine; tracked as upstream issue #44. The tester always sends 16 kHz mono wav, so the OpenAI-compatible endpoint shape invites mp3 but should be fed wav (**Reported**).[^audiocpp-4-asr-thread]
3. **Short single-clip offline requests return HTTP 200 with empty text (Voxtral Mini 4B Realtime, Q8_0).** On the tester's 46-minute meeting about 21 minutes went silently missing in contiguous holes when a ~25 s VAD segment was sent per request; the same span sent as a 150 s clip returned 2,018 characters. Reproduced on 4 of 5 short clips; whole-file offline (~0.15 RTF) and streaming SSE (TTFT about 0.6 s including upload of a 5-minute file, ~0.25 RTF) were clean. The tester suspected a minimum-context or short-window edge and planned an issue; the capture shows no maintainer response or fix (**Reported**, not reproduced; open at capture).[^audiocpp-4-asr-thread]
4. **Language drift in hard narrowband audio.** Voxtral spliced Russian phrases into French turns on the worst window while the tester's automated non-Latin-drift counter scored 0, so only manual reading caught it; Qwen3-ASR drifted into a different script on the same window. The tester calls it a hard-audio property, not a Voxtral-specific flaw (**Reported**).[^audiocpp-4-asr-thread]
5. **Build note:** copying `audiocpp_server` out of the source tree needs `-DAUDIOCPP_DEPLOYMENT_BUILD=ON` to embed per-family model specs, otherwise loading fails with `model package spec not found` (**Reported**; compare `--deployment-build` in [audio.cpp Framework](audio-cpp-framework.md)).[^audiocpp-4-asr-thread]

Implication for VAD-chunked pipelines (**Synthesis**): never trust HTTP 200 as success in a per-segment STT loop. Compare empty text against the VAD segment's duration, retry short segments with padding or merged context, and test per-chunk, whole-file, and streaming paths separately, because they diverged here. Pair this with the guidance in [Whisper Hallucination Mitigation for Vietnamese](whisper-hallucination-mitigation.md) for the opposite failure (text from silence).

## Quantization, memory, and speed-versus-VRAM replies

- A commenter notes Parakeet v3 Q4 runs in about 1.2 GB total VRAM versus this thread's multi-GB figures. The maintainer replies that audio.cpp loads quantization down to q8 through `--session-option <family>.weight_type=<mode>`, GGUF support arrives model by model, the framework trades memory for speed, memory-saver modes (requested by users) can be about 30% slower, and Q4 or even fp16-versus-bf16 can lower quality or produce NaNs so each model needs testing (**Reported**).[^audiocpp-4-asr-thread]
- The post's 07/21 OmniVoice table (357.0 s on RTX 5090: BF16 31.37x, Q8 34.82x, Q8 `perf=on` 43.10x) duplicates the figures already recorded in [audio.cpp Framework](audio-cpp-framework.md) and adds nothing new (**Observed** by comparison).[^audiocpp-4-asr-thread]
- One reported 3090 user saw about 2x improvement after the release; a commenter testing Nemotron ASR with VoxCPM2 on two RTX 3060s reports it as a "voice loop" setup without figures (**Reported**; anecdote).[^audiocpp-4-asr-thread]

## Model requests and roadmap replies

- Kroko ASR (zipformer2 family) was requested and later reported as supported; the commenter doubted feasibility because the architecture differs, and the maintainer says they want broader architectures beyond autoregressive models (**Reported**).[^audiocpp-4-asr-thread]
- The maintainer recommends `mudler/parakeet.cpp` for Parakeet and dropped Parakeet-TDT from this release because good implementations already exist (**Reported**).[^audiocpp-4-asr-thread]
- Roadmap replies: move the current autoregressive implementations toward llama.cpp in future, with release 0.2 as a preliminary step; no vLLM comparison exists yet because many models are non-AR; only an OpenAI-compatible server exists, with no llama.cpp RPC protocol; the next batch returns to TTS (Higgs TTS, IndexTTS2, Irodori TTS, maybe Kokoro, MOSS-TTS, Supertonic); the CPU path gets less optimization attention than CUDA; the subtitle pipeline uses Qwen3-ASR plus Qwen3-ForcedAligner through `--pipeline assets/pipeline/qwen3_asr_subtitles.json` and a batch variant (**Reported**).[^audiocpp-4-asr-thread]
- Maintainer validation stance: releases are slower because most time goes to measurement, validation, and making AI explain suspicious code changes rather than trusting AI-generated code (**Reported**).[^audiocpp-4-asr-thread]
- Release context in updates: 07/09 shared depthwise-conv1d module optimization (up to 40% on 13 models, 10%+ on released ASR models); 07/14 release 0.3 (five TTS models); 07/18 Voxtral ASR streaming; further comment-level notes of Docker support, Windows prebuilts, and later per-family speedups (VibeVoice 73.17%, PocketTTS 35.32%, Chatterbox 33.56%, Qwen3-TTS 30.60%, HeartMuLa 17.03%, VoxCPM2 14.7% on short requests) restate figures already in [audio.cpp Framework](audio-cpp-framework.md) (**Reported**).[^audiocpp-4-asr-thread]

## Contradictions

- The post says Parakeet-TDT was dropped from this release in favor of existing implementations (**Reported**).[^audiocpp-4-asr-thread] The [GGUF packages catalog](audio-cpp-gguf-packages.md) lists a `Parakeet-TDT-0.6B-v3` ASR package for audio.cpp. Neither is chosen; the catalog may postdate this thread, which is undated beyond 07/21/2026 (**Synthesis**).

## Relationships

- Runtime: documents benchmark and field evidence for [audio.cpp Framework](audio-cpp-framework.md); packaging details live in [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) (**Synthesis**).
- Models measured: [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md), [Higgs Audio v3 STT](higgs-audio-v3-stt.md), [VibeVoice-ASR](vibevoice-asr.md), [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md), [Qwen3-ASR family](qwen3-asr-family.md), [VoxCPM2](voxcpm2.md) (**Synthesis**).
- Decision context: [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) and [ASR/STT Model Survey](asr-stt-model-survey.md) rank models by quality and streaming; this concept adds runtime-level reliability evidence for the audio.cpp route, none of it Vietnamese (**Synthesis**).
- The maintainer-recommended Parakeet runtime is documented in [parakeet.cpp](parakeet-cpp.md); its README independently describes Nemotron 3.5 support and a cache-aware streaming mode (**Synthesis**).

## Coverage and limits

- The whole capture was read as text: post body, four dated update blocks and tables, and all 43 listed comments with replies. No images are in the capture; linked artifacts (upstream repo, `depthwise_conv1d_performance.md`, issues #34 and #44, PR #19, TranscrIA benchmark write-up and release notes, parakeet.cpp, Kroko repos, MOSS-Transcribe-Diarize, sa3.cpp, earlier threads) were not fetched (**Synthesis**).[^audiocpp-4-asr-thread]
- Static inspection only: no build, model download, transcription, or benchmark was run, so every figure is **Reported**. Not stated: test-file language and content, WER normalization, Python baseline per row, audio.cpp commit for the table, and whether the table numbers use the same hardware as the Voxtral update beyond "RTX 5090" (**Synthesis**).[^audiocpp-4-asr-thread]
- Comment bylines are unreliable, so replies are attributed by content. Third-party figures come from one corpus and one scorer, and the author of that corpus is also a downstream product maintainer that adopted audio.cpp, a potential bias (**Synthesis**).[^audiocpp-4-asr-thread]
- Benchmark and release figures carry `stale_after: 2027-04-21` per the `stt` domain rule; the empty-output and mp3 items were fixed or tracked upstream at capture time, so re-check current behavior before relying on them (**Synthesis**).

[^audiocpp-4-asr-thread]: [audio.cpp: What Does the Fox Say — 4 ASR models Reddit thread](../raw/audiocpp_what_does_the_fox_say_4_asr_models.md) — locators: title/subreddit/author/vote header and repo link; `Update(07/21/2026)` OmniVoice GGUF q8 table; `Update(07/18/2026)` Voxtral ASR streaming CLI, server TTFT, and 30-minute longform tables; `Update(07/14/2026)` release 0.3; `Update(07/09/2026)` depthwise conv doc; post body (four ASR models, 1.07x–2.41x, Parakeet-TDT drop, Nemotron/VoxCPM2 streaming, Higgs experimental streaming, headline 327.6 s in 2.17 s at 3.18% WER, contribution call); `ASR models (No Quant)` table; `Streaming TTS` VoxCPM2 table; `Comments 43` section (Docker/prebuilts/perf reply; subtitles pipeline example; DLC/TTS roadmap; issue #34/PR #19; validation-stance reply; quantization/Q4/memory-saver reply; Kroko zipformer2 exchange; two-3060 voice-loop comment; TranscrIA multi-engine French-meeting benchmark comment with Qwen3-ASR 0.6B, Nemotron reused-session empty text, mp3 500; maintainer fix reply; retest confirmation with 3b4aed9→3982dfb, 0.49 WER and Qwen3-ASR-1.7B 0.42 WER; issue #44 reply; Voxtral Mini 4B Realtime availability reply; Voxtral three-serving-mode test with `edbdf58`, `AUDIOCPP_DEPLOYMENT_BUILD=ON`, per-chunk empty-text finding, 150 s repro, language-drift note; vLLM comparison and llama.cpp-replacement replies; parakeet.cpp recommendation; llama.cpp RPC reply; MOSS-Transcribe-Diarize request).
