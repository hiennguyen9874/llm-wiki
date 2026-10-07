---
type: Concept
title: Vietnamese Realtime Voice Agent Stack
description: Research-report recommendation for an open-source Vietnamese realtime voice agent in noisy environments combining Silero VAD, Smart Turn, faster-whisper or Qwen3-ASR, Qwen3 LLM, and VieNeu-TTS/Qwen3-TTS, with architecture, configuration, latency and VRAM budgets, and hardware tiers.
tags: [pipeline, vad, stt, llm, tts, vietnamese, streaming, noisy-audio]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:10:00Z }
stale_after: 2027-10-06
sources:
  - id: vi-primary-research
    resource: ../raw/vietnamese-asr-research-2026-10-07/README.md
    scope: ../raw/vietnamese-asr-research-2026-10-07/
    kind: documentation
    title: Vietnamese ASR primary-source follow-up
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
---

A Vietnamese-language research report dated 10/2026 concludes that a cascaded Silero VAD → Whisper → Qwen3 → Qwen3-TTS realtime voice chat is buildable, but that a Vietnamese product breaks at the TTS stage because official Qwen3-TTS supports 10 languages without Vietnamese; it therefore recommends VieNeu-TTS v3 Turbo for Vietnamese, keeps Qwen3-TTS for English/Chinese and its other supported languages, and puts every TTS behind one `/v1/audio/speech` endpoint so swapping TTS is only a URL change (**Reported**).[^claude-pipeline-report] For noisy environments it argues that AEC, speaker lock, duration-gated barge-in, confidence gating, and a Vietnamese hallucination blacklist matter more than placing a denoiser in front of ASR (**Reported**).[^claude-pipeline-report]

## ASR primary-source corrections (2026-10-07)

The sections below preserve the original AI-report recommendations, not a current validated stack. Use [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) for updated model/streaming/license filtering (**Synthesis**).[^vi-primary-research]

- Qwen Vietnamese offline WER5.55/8.52 and14.92/17.67 is now directly inspected in paper AppendixTableA.2. Streaming §4.5 uses2s chunks,5-token fallback and four unfixed chunks, evaluates only LibriSpeech/FLEURS-en/zh.92ms TTFT is Table2 concurrency1; concurrency128 TTFT3210ms/P95 6195ms yields throughput2000 audio-seconds/second on complete~2min inputs, not mic stable-text latency (**Reported**).[^vi-primary-research]
- [PhoWhisper](phowhisper.md) README/card confirm844h finetuning and BSD-3. [ChunkFormer Vietnamese](chunkformer-vietnamese.md) CTC110M card says~3000h/CC-BY-NC-4.0, RNNT113M says~5000h/CC-BY-4.0, so the report's generic110M/~25Kh/NC label is not applicable to every checkpoint. ONNX true-streaming uses a distinct small streaming-trained example; its card returned401, with access/license/WER unresolved (**Reported/Observed**).[^vi-primary-research]
- [ZipFormer30M](zipformer-30m-vietnamese.md) upstream says6000h and CC-BY-NC-ND-4.0, contradicting the report's Apache label. CPU12s/0.3s file throughput does not establish native streaming; the CPU/edge tier below is a historical unverified recommendation, not approved commercial deployment (**Reported/Synthesis**).[^vi-primary-research]
- No model execution or independent benchmark occurred; paper/ONNX-code/checkpoint coverage remains partial per ledger. Other VAD/TTS/noise/turn and hardware estimates stay AI-report/draft evidence.[^vi-primary-research]

## Source and trust

- The source is an AI-compiled survey-plus-integration report (file name attributes it to Claude) written in Vietnamese, self-dated 10/2026, that cites vendor model cards, papers, GitHub issues, and third-party blogs without capturing them; none of those primary sources is in `raw/` (**Observed**).[^claude-pipeline-report]
- The report itself labels which figures are vendor/author claims (Qwen3-TTS 97 ms, vLLM-Omni 64 ms TTFP, faster-qwen3-tts RTF/TTFA, VieNeu 115 ms and 16 streams, Smart Turn accuracy, Qwen3-ASR and Nemotron WER, Silero v6 16%, TEN VAD vs Silero), which are third-party (VietASR 16.44% Whisper WER, denoise studies, NOVA-VAD), and which are its own engineering estimates (latency and VRAM budgets) (**Reported**).[^claude-pipeline-report]
- Items it explicitly did not re-check: FireRedVAD, MarbleNet, Cobra, Kyutai, Moshi/Unmute, MiniCPM-o, GLM-4-Voice, Ultravox, LFM2-Audio, CosyVoice 3, F5-TTS-Vietnamese, viXTTS, and small frameworks (Bolna, Dograh, Speaches, LocalAI, xiaozhi); Qwen3.6/3.8 are seen only in secondary sources and excluded from recommendations (**Reported**).[^claude-pipeline-report]

## TTS selection follow-up (2026-10-07)

Use [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) for current local-primary-card filtering of VieNeu, VoxCPM2, Supertonic 3, Higgs TTS 3, Fish S2 Pro and OmniVoice. It distinguishes per-stream RTF/TTFA from batched throughput, frame-level audio output from incremental text input, and Vietnamese-listed support from matched listening quality. This report's VieNeu-only routing, generic VRAM estimates, G2P issue and community checkpoint pointers remain secondary/unverified; the follow-up does not validate the entire stack (**Synthesis**).

## Recommended stack (single 24 GB GPU)

| Stage | Pick | Key setting |
|---|---|---|
| Noise handling | Light denoise (RNNoise/DeepFilterNet 3) on the VAD/barge-in branch only | ASR hears the original AEC-processed audio |
| VAD | [Silero VAD](silero-vad.md) v6.2 (drop-in for v5, same API) | 512 samples / 32 ms at 16 kHz |
| Turn detection | Smart Turn v3.x, see [Turn Detection Models](turn-detection-models.md) | Plus 1.2–1.5 s silence fallback timeout |
| STT | [Faster-Whisper](faster-whisper.md) `large-v3-turbo`, `language="vi"` | Anti-hallucination parameters plus garbage filter, see [Whisper Hallucination Mitigation](whisper-hallucination-mitigation.md) |
| LLM | Qwen3-8B (or Qwen3.5-9B), thinking off, served by vLLM | Sentence-chunked streaming |
| TTS | [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) for Vietnamese; Qwen3-TTS 12Hz via vLLM-Omni for other languages | PCM over HTTP/WebSocket streaming |
| Framework | Pipecat, see [Voice Agent Frameworks](voice-agent-frameworks.md) | Custom `TTSService` needed for Qwen3-TTS/VieNeu |

All rows are the report's recommendation (**Reported**).[^claude-pipeline-report]

## Architecture

- Client captures with `getUserMedia` (`echoCancellation` on; `noiseSuppression` A/B tested) and sends WebRTC Opus or WebSocket PCM16 16 kHz mono to an asyncio gateway that resamples to 16 kHz into a 20 ms ring buffer (**Reported**).[^claude-pipeline-report]
- The denoised branch feeds Silero VAD then Smart Turn plus a 1.2 s timeout; on end-of-turn the original AEC audio goes to faster-whisper, then a garbage filter (`no_speech`, `avg_logprob`, `compression_ratio`, Vietnamese blacklist, speaker lock), then Qwen3 via vLLM with `enable_thinking=False` streaming, a sentence chunker plus Vietnamese text normalizer, and a TTS router (VieNeu for `vi`, Qwen3-TTS via vLLM-Omni for en/zh) returning PCM chunks; user speech ≥300 ms while the bot talks triggers barge-in, see [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) (**Reported**).[^claude-pipeline-report]
- Transport: WebRTC (Opus, browser AEC, packet-loss tolerance, jitter buffer) for production over the Internet; WebSocket PCM16 for MVP or LAN; returned audio is 24 kHz (Qwen3-TTS) or 48 kHz (VieNeu) played through an AudioWorklet, so the client must know the per-backend sample rate (**Reported**).[^claude-pipeline-report]
- The report ships a FastAPI + WebSocket asyncio reference server (`Session` with per-session `VADIterator`, 400 ms barge-in gate, `asyncio.to_thread` transcription, LLM stream to TTS queue worker, `{"type":"clear"}` interrupt message); its VieNeu streaming JSON body and vLLM-Omni Docker tags are flagged as needing verification against installed versions (**Reported**).[^claude-pipeline-report]

## Vietnamese coverage by component

| Component | Vietnamese status in the report |
|---|---|
| Qwen3-TTS (official) | No: 10 languages (zh, en, ja, ko, de, fr, ru, pt, es, it); community request Discussion #274 (03/2026) unanswered; community fine-tunes `ShiniChien/Qwen3-TTS-12Hz-1.7B-Vietnamese` and `-VN-Style` from `1.7B-Base` lack independent benchmarks and clear data license |
| Qwen3-Omni-30B-A3B | Vietnamese speech input (19 input languages) but no Vietnamese speech output (10 output languages) |
| [Qwen3-ASR family](qwen3-asr-family.md) | Yes: Fleurs-vi 5.55 (1.7B) / 8.52 (0.6B), MLC-SLM-vi 14.92 / 17.67 (vendor tech report); ForcedAligner has no Vietnamese |
| Whisper large-v3 | Yes but not best: 16.44% mean WER on three Vietnamese test sets (VietASR, arXiv 2505.21527) |
| PhoWhisper (VinAI) large | Vietnamese-specialized: CMV-vi 8.14, VIVOS 4.67, VLSP2020-T1 13.75, T2 26.68 (authors' paper); BSD-3 |
| ChunkFormer-large-vie | 110M, ~25K h Vietnamese; N-WER 6.89 on a revisit benchmark (arXiv 2603.14779); license CC-BY-NC to be rechecked |
| sherpa-onnx Zipformer VN 6000h | ~30M, true streaming on CPU/edge; no independent WER |
| [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) | Yes: FLEURS-vi 13.41 (80 ms) → 11.18 (1.12 s), vendor figures |
| [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) | No (25 European languages) |
| Smart Turn v3 | Yes (81.27% accuracy, vendor) |
| LiveKit turn detectors | No (14 languages) |

All cells are as reported, with the report's own attribution of vendor versus third-party origin (**Reported**).[^claude-pipeline-report]

## LLM choice and invocation

- Qwen3 (04/2025, Apache-2.0): dense 0.6B–32B plus MoE 30B-A3B and 235B-A22B, 119 languages, thinking switch via `enable_thinking=False` or `/no_think`; Qwen3.5 (02–03/2026, Apache-2.0): 0.8B–397B-A17B, natively multimodal, 201 languages, with 4-bit 9B ~6 GB and 4B ~3 GB per Artificial Analysis, and its reasoning mode is token-heavy so voice must use non-thinking (**Reported**).[^claude-pipeline-report]
- Size by hardware: 24 GB → Qwen3-8B-AWQ or Qwen3.5-9B 4-bit; 12 GB → Qwen3-4B or Qwen3.5-4B; large server → Qwen3-30B-A3B (~3B active MoE for good TTFT); disable thinking with `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` on vLLM (**Reported**).[^claude-pipeline-report]
- Spoken-dialogue system prompt: 1–3 short sentences, no markdown/emoji/tables/URLs, numbers and dates written as words (or left to the normalizer), and ask again when unsure of what was heard (**Reported**).[^claude-pipeline-report]
- Sentence chunking: flush to TTS on `.?!…;:` or newline; cut the first chunk at a comma once ~25 characters exist to cut time-to-first-audio; merge fragments under 8 characters into the next sentence (**Reported**).[^claude-pipeline-report]
- History: keep the last ~10–20 turns and summarize older ones; on interruption store only the actually played part of the reply tagged `[bị ngắt]` (**Reported**).[^claude-pipeline-report]
- Gemma 3, Llama, and Phi-4 work behind the same OpenAI-compatible endpoint; Qwen as the safer Vietnamese choice is a qualitative judgment with no benchmark checked (**Reported**).[^claude-pipeline-report]

## TTS routing and Vietnamese text normalization

- Qwen3-TTS checkpoint choice: `12Hz-0.6B-CustomVoice` for low latency/VRAM, `1.7B-CustomVoice` for `instruct` voice control, `Base` (1.7B or 0.6B) for cloning, since only Base exposes `create_voice_clone_prompt`/`generate_voice_clone` and CustomVoice/VoiceDesign raise `ValueError`; see [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md) and [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) (**Reported**).[^claude-pipeline-report]
- Streaming is a serving-layer property: the official `qwen-tts` package returns `(wavs, sr)` after full generation; streaming comes from vLLM-Omni (`vllm-omni serve ... --omni`, `POST /v1/audio/speech` with `response_format="pcm"`, `stream_format="audio"` requiring `async_chunk: true`, or a WebSocket `session.config`/`input.text`/`input.done` → `audio.start`/binary PCM/`audio.done` protocol; `speed` unsupported when streaming; TTFP 64 ms at concurrency 1 per vLLM-Omni docs) or community forks [Faster Qwen3-TTS](faster-qwen3-tts.md) (`generate_voice_clone_streaming(chunk_size=8)`, RTF 5.6 on RTX 4090 per author) and `dffdeeq/Qwen3-TTS-streaming` (~0.17 s first chunk on RTX 5090 per author) (**Reported**).[^claude-pipeline-report]
- Vietnamese TTS paths ranked: (a) VieNeu-TTS v3 Turbo via `/v1/audio/speech` (recommended); (b) the community Vietnamese Qwen3-TTS fine-tune with `language="Vietnamese"`, requiring own MOS/CER evaluation; (c) self fine-tune from Base with the official `finetuning/` folder (**Reported**).[^claude-pipeline-report]
- Other Vietnamese-capable TTS named: VieNeu-TTS v3 Nano preview (48M, flow-matching, CPU-only) and KhanhTTS-OmniVoice (community, Qwen3-0.6B backbone, Vi+En ~1,500 h, 4 GB GPU, Apache-2.0 per repo); XTTS-v2/viXTTS carry the non-commercial Coqui Public Model License (**Reported**).[^claude-pipeline-report]
- Normalize text before TTS: numbers to words (`1.250.000đ` → `một triệu hai trăm năm mươi nghìn đồng`), dates, times, percentages, units, abbreviations (TP.HCM, UBND, km/h), and English words kept only when the TTS handles code-switching (VieNeu does) else transliterated; keep a substitution dictionary for proper nouns and domain terms because of known G2P errors such as VieNeu v3 Turbo reading `chánh` as `tránh` (issue #207) (**Reported**).[^claude-pipeline-report]

## Latency budget (report estimates)

| Stage | Target | Basis |
|---|---|---|
| Network + jitter buffer | 30–80 ms | WebRTC |
| VAD silence | 200–300 ms | Pipecat `stop_secs=0.2` |
| Smart Turn | 10–65 ms | Vendor |
| ASR (turbo, GPU, 3–5 s utterance) | 100–300 ms | Estimate, no independent benchmark |
| LLM TTFT + first chunk | 150–350 ms | Qwen3-8B AWQ, vLLM, prefix cache |
| TTS TTFA | 64–300 ms | vLLM-Omni and community forks; VieNeu ~115 ms per author |
| **Voice-to-voice** | **~0.7–1.2 s** | Must be measured on real hardware |

Budget rows are the report's engineering estimates (**Reported**).[^claude-pipeline-report]

- Optimizations: warm up all models and keep them resident in VRAM; vLLM prefix caching for the system prompt; run faster-whisper's lazy `transcribe` generator to completion inside `asyncio.to_thread` because iterating it on the event loop blocks the pipeline (Pipecat PR #5931); preemptive ASR+LLM on 200 ms VAD silence cancelled if the user resumes; connect stages with async queues (**Reported**).[^claude-pipeline-report]
- VRAM on one 24 GB GPU (estimate): Whisper turbo fp16 ~2–3 GB, Qwen3-8B-AWQ plus KV cache for a few sessions ~8–10 GB (`--gpu-memory-utilization 0.4`), Qwen3-TTS 1.7B ~5–7 GB (0.6B less), VieNeu GPU ~2–3 GB — fits with little headroom; on 12 GB use Qwen3-4B 4-bit, Qwen3-TTS 0.6B or VieNeu, and turbo `int8_float16` (**Reported**).[^claude-pipeline-report]

## Deployment tiers

| Tier | VAD/Turn | STT | LLM | TTS |
|---|---|---|---|---|
| GPU server (multi-session) | Silero v6.2 + Smart Turn v3.2 (CPU) | Qwen3-ASR-1.7B via vLLM streaming, or batched faster-whisper turbo | Qwen3-30B-A3B or Qwen3.5-35B-A3B via vLLM/SGLang | VieNeu v3 Turbo GPU server (vi) + Qwen3-TTS 1.7B via vLLM-Omni |
| 1 GPU 12–24 GB | Silero v6.2 + Smart Turn v3 | faster-whisper large-v3-turbo fp16/int8, or PhoWhisper | Qwen3-8B-AWQ (24 GB) / Qwen3-4B or Qwen3.5-4B 4-bit (12 GB) | VieNeu v3 Turbo (vi); Qwen3-TTS 0.6B-CustomVoice (en/zh) |
| CPU / edge | Silero ONNX + Smart Turn int8 | sherpa-onnx Zipformer VN streaming, or whisper.cpp small/turbo q5 | Qwen3.5-2B/4B or Qwen3-1.7B GGUF via llama.cpp | VieNeu v3 Turbo ONNX/GGUF or v3 Nano |

Tier rows are the report's recommendation (**Reported**).[^claude-pipeline-report]

- Scaling: per-session VAD state on CPU; ASR through a batched worker pool (faster-whisper `BatchedInferencePipeline`); continuous batching for LLM and TTS in vLLM/vLLM-Omni; split ASR, LLM, and TTS across GPUs at high session counts; Qwen3-ASR-0.6B via vLLM reportedly reaches 92 ms average TTFT and 2000 s of speech per second at concurrency 128 (RTF 0.064) per its tech report (arXiv 2601.21337) (**Reported**).[^claude-pipeline-report]
- Monitoring: per-turn `vad_end→asr_done`, `asr_done→llm_first_token`, `first_sentence→tts_first_byte`, client-side voice-to-voice, filtered-transcript rate, barge-in rate, and false-interruption rate (**Reported**).[^claude-pipeline-report]
- Evaluation: Vietnamese WER/CER on an internal set mixed with café, motorbike, and TV noise at SNR 0/5/10/20 dB with and without denoise; TTS MOS/CMOS with 10–20 listeners plus ASR round-trip CER; turn-detection false-cutoff rate; false-interruption rate under background noise; voice-to-voice P50/P95 (**Reported**).[^claude-pipeline-report]

## Roadmap and replacement triggers

- MVP (1–2 weeks): Pipecat + SmallWebRTC; Silero + Smart Turn + `WhisperSTTService` (turbo, `vi`) + Qwen3-8B via vLLM + a custom TTS service calling VieNeu; measure voice-to-voice and WER from day one (**Reported**).[^claude-pipeline-report]
- Beta: hallucination blacklist, confidence gating, duration-gated barge-in, CAM++/ECAPA speaker lock, Vietnamese text normalizer, and A/B of denoise before ASR with no-denoise on the ASR branch as the default (**Reported**).[^claude-pipeline-report]
- Production: per-GPU service split with continuous batching, P95 latency observability, swap to streaming Qwen3-ASR if it beats Whisper on the internal noisy Vietnamese set, and consider fine-tuning Qwen3-TTS Base for Vietnamese to get one TTS for all languages (**Reported**).[^claude-pipeline-report]
- Replace Whisper when noisy Vietnamese WER exceeds ~15%, hallucinations still pass filters, or partial transcripts are needed for preemptive generation (candidates Qwen3-ASR, PhoWhisper, ChunkFormer; not Parakeet v3); replace Qwen3-TTS for Vietnamese from the start, and for other languages when CPU-only (Kokoro, Piper) or different license/cloning is needed (CosyVoice, Fish S2 Pro); replace Smart Turn with Namo or a fine-tuned model if Vietnamese false-interruption stays above 10% (**Reported**).[^claude-pipeline-report]
- Omni end-to-end does not yet replace the cascade for Vietnamese: omni models offer low latency and preserved prosody but are hard to control, to attach RAG/tools to, and to swap per component, and lack Vietnamese speech output (**Reported**).[^claude-pipeline-report]

## Relationships

- Uses [Silero VAD](silero-vad.md), [Faster-Whisper](faster-whisper.md), [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md), and the Qwen3-TTS CustomVoice checkpoints as the core recommended components (**Synthesis**).[^claude-pipeline-report]
- Depends on [Turn Detection Models](turn-detection-models.md), [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md), [Whisper Hallucination Mitigation](whisper-hallucination-mitigation.md), and [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) for its noisy-environment practices, split out as independently retrievable concepts (**Synthesis**).[^claude-pipeline-report]
- Uses [Voice Agent Frameworks](voice-agent-frameworks.md) (Pipecat) as the low-code orchestration route (**Synthesis**).[^claude-pipeline-report]
- Compares with [Community-Reported STT-LLM-TTS Pipeline Wiring](community-stt-llm-tts-pipeline.md): both use OpenAI-compatible HTTP services and sentence-chunked TTS streaming; this report adds Vietnamese-specific component coverage, explicit latency/VRAM budgets, and barge-in mechanics, while the community page reports keeping TTS on CPU to free the 24 GB card — a different VRAM placement from this report's all-GPU budget (**Synthesis**).[^claude-pipeline-report]
- Compares with [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md): a ChatGPT answer to the same Silero VAD → Whisper → Qwen3 → Qwen3-TTS request; this report diverges by routing Vietnamese away from Qwen3-TTS (the blueprint passes `language="vi"` to Qwen3-TTS, recorded as a contradiction there) and by a longer barge-in gate, recorded in [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) (**Synthesis**).[^claude-pipeline-report]
- Compares with [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) and [RealtimeVoiceChat](realtime-voice-chat.md) as alternative cascaded VAD → STT → LLM → TTS assemblies (**Synthesis**).[^claude-pipeline-report]

## Coverage and limits

- Source inspected statically in full (TL;DR, Key Findings, Part 1 survey §1–§8, Part 2 integration incl. mermaid diagram, reference Python server, docker-compose skeleton, Recommendations, Caveats); no code executed, no model installed, and no latency, VRAM, WER, or accuracy figure reproduced (**Synthesis**).[^claude-pipeline-report]
- The original ingest did not capture the report's cited primary sources. The2026-10-07 follow-up captures selected Qwen/PhoWhisper/ChunkFormer/ZipFormer ASR documentation, but not all cited sources or a complete deployment validation; remaining report citations are still unverified secondhand claims, so this concept stays `draft` (**Synthesis**).[^claude-pipeline-report]
- The reference server and docker-compose are summarized rather than reproduced; the report flags VieNeu streaming field names and vLLM-Omni image tags as unverified (**Synthesis**).[^claude-pipeline-report]
- Release dates and benchmark numbers carry `stale_after: 2027-10-06` per the `pipeline`, `vad`, `stt`, `llm`, and `tts` domain rules (**Synthesis**).[^claude-pipeline-report]

[^vi-primary-research]: [Primary research capture](../raw/vietnamese-asr-research-2026-10-07/README.md) — `qwen-report.html` §2.4/Table2, §4.5/Table8, AppendixTableA.2; PhoWhisper card/README; ChunkFormer CTC/RNNT cards Model Description/frontmatter and ONNX guide; ZipFormer30M upstream frontmatter/Inference Speed. Ledger records unavailable checkpoint and pending artifacts.

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: title and opening paragraph (Qwen3-TTS lacks Vietnamese, VieNeu recommendation, `/v1/audio/speech` swap); `TL;DR` (recommended 24 GB stack, verified-to-10/2026 facts, noisy-environment bullets); `Key Findings` 1–5; `PHẦN 1` §1 VAD, §2 preprocessing, §3 turn detection, §4 STT/ASR table, §5 LLM table plus serving paragraph, §6 TTS table, §7 speech-to-speech/omni, §8 framework table; `PHẦN 2` `Kiến trúc tổng thể` (mermaid flowchart, transport paragraph), `Qwen3: chọn cỡ và cách gọi`, `Qwen3-TTS: chọn model và cách dùng` (model choice, `qwen-tts` API, vLLM-Omni streaming, Vietnamese options, normalization, G2P issue #207), `Ngân sách độ trễ` table plus `Kỹ thuật tối ưu` and VRAM list, `Code mẫu` (server.py plus usage notes), `Triển khai` (docker-compose, scaling, monitoring, evaluation); `Recommendations` (tier table, `Lộ trình`, `Khi nào nên thay thành phần`); `Caveats`.
