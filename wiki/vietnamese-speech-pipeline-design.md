---
type: Synthesis
title: Vietnamese Speech Pipeline Design
description: Thiết kế speech pipeline tiếng Việt không chọn LLM chính, so sánh lựa chọn transport, VAD/turn, ASR, chunker/normalizer, TTS, orchestration và ghép thành sáu cấu hình model+deploy tool với tham số khởi điểm, hợp đồng streaming/cancellation, ngân sách latency, license và gate đánh giá.
tags: [pipeline, vietnamese, vad, stt, tts, streaming, deployment, architecture, comparison]
status: draft
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T05:20:00Z }
stale_after: 2027-10-07
sources:
  - { id: asr, resource: vietnamese-realtime-asr-selection.md, kind: synthesis, title: Vietnamese Realtime ASR Selection }
  - { id: tts, resource: vietnamese-realtime-tts-selection.md, kind: synthesis, title: Vietnamese Realtime TTS Selection }
  - { id: stack, resource: vietnamese-realtime-voice-agent-stack.md, kind: synthesis, title: Vietnamese Realtime Voice Agent Stack }
  - { id: deploy, resource: speech-deployment-tools-comparison.md, kind: synthesis, title: So sánh công cụ triển khai speech }
  - { id: silero, resource: silero-vad.md, kind: synthesis, title: Silero VAD }
  - { id: turns, resource: turn-detection-models.md, kind: synthesis, title: Turn Detection Models }
  - { id: noise, resource: speech-enhancement-before-asr.md, kind: synthesis, title: Speech Enhancement Before ASR }
  - { id: halluc, resource: whisper-hallucination-mitigation.md, kind: synthesis, title: Whisper Hallucination Mitigation for Vietnamese }
  - { id: barge, resource: voice-agent-barge-in-and-echo-handling.md, kind: synthesis, title: Voice-Agent Barge-in and Echo Handling }
  - { id: hf, resource: speech-to-speech-pipeline.md, kind: synthesis, title: HF Speech-to-Speech Pipeline }
  - { id: frameworks, resource: voice-agent-frameworks.md, kind: synthesis, title: Voice Agent Frameworks }
  - { id: nemotron, resource: nemotron-3.5-asr-streaming-0.6b.md, kind: synthesis, title: Nemotron 3.5 ASR Streaming 0.6B }
  - { id: qwen, resource: qwen3-asr-family.md, kind: synthesis, title: Qwen3-ASR family }
  - { id: whisper, resource: whisper-large-v3-turbo.md, kind: synthesis, title: Whisper Large v3 Turbo }
  - { id: nemo, resource: nemo-speech-cpp.md, kind: synthesis, title: NeMo-Speech.cpp }
  - { id: vieneu, resource: vieneu-tts-v3-turbo.md, kind: synthesis, title: VieNeu-TTS v3 Turbo }
  - { id: vox, resource: voxcpm2.md, kind: synthesis, title: VoxCPM2 }
  - { id: moss, resource: moss-tts-local-transformer-v1-5.md, kind: synthesis, title: MOSS-TTS-Local-Transformer-v1.5 }
  - { id: audio, resource: audio-cpp-framework.md, kind: synthesis, title: audio.cpp Framework }
  - { id: diar, resource: nemotron-3-diarization.md, kind: synthesis, title: Nemotron 3 Diarization }
---

**Synthesis, chưa triển khai/benchmark:** pipeline speech tiếng Việt đề xuất là cascade **Client (AEC) → Silero VAD → endpoint manager (Smart Turn tùy chọn + timeout) → ASR → validity/hallucination gate → [giao diện LLM bên ngoài] → clause chunker + Vietnamese normalizer → TTS streaming → bounded playback**, với barge-in bằng `generation_id`. Thứ tự thử theo nhu cầu: cần partial sớm thì bắt đầu với Nemotron 3.5 ASR streaming + VieNeu v3 Turbo sau Pipecat/custom gateway (Profile B); cần MVP ít tích hợp thì HF speech-to-speech hoặc Pipecat + faster-whisper large-v3-turbo `vi` + VieNeu `/v1/audio/speech` (Profile A); cần accuracy thì A/B Qwen3-ASR single-pass hoặc thêm final-pass có điều kiện (C/D); CPU/edge và license-strict có profile riêng (E/F). Đây là tổ hợp từ các synthesis/concept đã compile, không có voice-to-voice, WER hay MOS tiếng Việt đo trên cùng stack và không khẳng định stack nào thắng.[^asr][^tts][^stack][^deploy][^hf][^frameworks]

## Phạm vi và cơ sở quyết định

- Giả định thiết kế: user/bot một-một, mic browser/mobile hoặc call audio; ưu tiên self-host và hội thoại. Không chọn, fine-tune hay budget model LLM chính; vẫn định nghĩa text-stream/cancel boundary để vòng speech chạy hoàn chỉnh (**Synthesis**).
- Đã đọc index/log, các trang `type: Synthesis` (ASR/TTS selection, deploy comparison, Vietnamese stack, realtime ASR shortlist), hai model surveys, pipeline reports và các concept model/runtime/control liên quan. Log ghi các thao tác `Query` (filed answers) và `Update` (reconciliation), không có type `Answered`/`Reconciled` riêng (**Observed**, session 2026-10-07).
- Capabilities và benchmark ASR/TTS là **Reported** qua concepts có locator về nguồn; lựa chọn, cấu hình thử, protocol và topology là **Synthesis**. Framework, Smart Turn, denoise, hallucination filter, barge-in và latency budget phần lớn dựa AI report thứ cấp, không primary-verified.[^asr][^tts][^frameworks][^turns][^noise][^barge][^halluc][^stack]
- Chưa có hardware, số phiên, domain, commercial boundary và SLA cụ thể. Không coi model chưa benchmark là yếu; không gọi snapshot trong repo là khảo sát toàn thị trường (**Synthesis**).

## Kiến trúc tổng thể

Sơ đồ là **Synthesis**, không phải implementation đã test.[^asr][^tts][^noise][^barge][^hf][^stack]

```text
Client mic + AEC + capture timestamp
  → WebRTC Opus / WS PCM16 16 kHz
  → Gateway (per-session state): decode/resample/ring buffer
      ├→ [denoise nhẹ, tùy chọn] → Silero VAD → Smart Turn + timeout → endpoint / barge-in policy
      ├→ AEC audio (không enhance) → ASR streaming state
      └→ turn audio buffer → optional final recognizer
  → transcript revisions + validity gate (confidence, hallucination filter, entity checks, speaker lock tùy chọn)
  → COMMITTED user turn → external LLM interface (OpenAI-compatible stream; không chọn model)
  → meaningful clause chunker → Vietnamese spoken-text normalizer + lexicon
  → TTS router/adapter → audio stream metadata + chunks
  → bounded client queue → playback + played-offset acknowledgement
                        ↖ barge-in ⇒ generation_id++ ⇒ cancel LLM + TTS, flush queues, lưu phần đã phát
```

Nguyên tắc (**Synthesis**): tách model, runtime, API server, streaming policy và orchestration thành tầng riêng; ASR nghe audio AEC gốc, denoise chỉ cho nhánh VAD/barge-in cho đến khi A/B chứng minh khác; mỗi backend khai báo sample rate/dtype/channels/framing/cancellation riêng; một owner duy nhất quyết định turn commit.[^deploy][^noise][^stack][^tts]

## Lựa chọn theo tầng

### Transport, AEC và tiền xử lý

| Lựa chọn | Khi dùng | Ghi chú |
|---|---|---|
| WebRTC (Opus, AEC trình duyệt, jitter buffer, chịu packet loss) | Production qua Internet, mobile, remote barge-in | AEC cần thiết khi có loa ngoài (**Reported**).[^stack][^barge] |
| WebSocket PCM16 16 kHz mono | MVP, LAN, loopback edge | Đơn giản; cần playback queue (AudioWorklet) phía client, client biết sample rate từng backend (VieNeu 48 kHz) (**Reported**).[^barge][^stack] |
| Denoise RNNoise (CPU nhẹ) / DeepFilterNet 3 | Chỉ nhánh VAD/barge-in | Bằng chứng enhancement-trước-ASR mâu thuẫn và không có nghiên cứu tiếng Việt; A/B Vietnamese WER/CER ở SNR 0/5/10/20 dB (**Reported/Synthesis**). Trong HF s2s, DeepFilterNet cần `numpy<2` và xung đột Pocket TTS (**Reported**).[^noise][^hf] |

### VAD và turn detection

| Thành phần | Pick | Thay thế | Ghi chú |
|---|---|---|---|
| VAD | [Silero VAD](silero-vad.md) v5/v6 ONNX, MIT, ~2 MB, <1 ms/chunk CPU, cửa sổ cố định 512 samples/32 ms @16 kHz | TEN VAD (Apache "with conditions", hop 10/16 ms; claim vendor vs benchmark cộng đồng mâu thuẫn); FireRed Stream-VAD (extra `fireredvad` trong HF s2s) | Silero chỉ phát hiện speech, không hiểu end-of-turn (**Reported**).[^silero][^hf] |
| Turn detection | Pipecat [Smart Turn v3.2](smart-turn.md): ~8M params, CPU int8 8 MB / GPU fp32 32 MB, 10 ms CPU / ~65 ms cloud (vendor), BSD-2; tiếng Việt accuracy 82.47% (GPU) / 79.38% (CPU), FPR 9.56/8.86%, FNR 7.97/11.75% (vendor, 1.004 mẫu) | Namo (community `dangvansam`, VN build ~200 MB, 4–36 ms, author-measured, không benchmark độc lập); LiveKit turn detectors **không có vi** (14 ngôn ngữ) | Tiếng Việt là ngôn ngữ yếu nhất trong 23 ngôn ngữ của Smart Turn; FPR ~9.6% GPU vẫn là gần một trên mười lần "hết lượt" kích hoạt khi user còn nói; luôn kèm fallback timeout 1.2–1.5 s; thay Smart Turn nếu false-interruption tiếng Việt >10% (**Reported**).[^turns] |

HF speech-to-speech đã hiện thực Smart Turn v3.2 với turn tracker `LISTENING/SOFT_ENDED/ANSWERING/CLOSED`: turn complete bắt đầu STT/LLM ngay với speculative reopen 800 ms; turn incomplete chờ 600 ms rồi mới chạy, output bị gate bởi max wait 2 s; nói tiếp mở lại turn thành revision mới và bỏ việc chưa commit. Đây là tham chiếu triển khai cụ thể hơn số liệu report, nhưng defaults của nó (`--min_silence_ms` 64 ms) khác policy report (xem Contradictions) (**Reported**).[^hf] Số Smart Turn v3.2 tiếng Việt nay có primary vendor benchmark trong [Smart Turn v3.2](smart-turn.md), thay cho con số secondhand cũ; v3.2 vẫn là ngôn ngữ yếu nhất trong benchmark của chính nó (**Reported**).[^turns]

### ASR tiếng Việt: quality, latency và checkpoint là các trục riêng

Các số là **Reported**, vai trò là **Synthesis**.[^asr][^nemotron][^qwen][^stack]

| Candidate | Kiểu realtime | Bằng chứng tiếng Việt | Runtime deploy | License |
|---|---|---|---|---|
| [Nemotron 3.5](nemotron-3.5-asr-streaming-0.6b.md) 600M | Native cache-aware RNNT, chunk 80–1120 ms | FLEURS vi-VN WER (LangID): 13.41 / 12.87 / 12.29 / 11.78 / 11.18 tại 80 / 160 / 320 / 560 / 1120 ms (auto-detect 13.59 → 11.22) | NeMo cache-aware streaming script; [NeMo-Speech.cpp](nemo-speech-cpp.md) Q8 GGUF (CLI, HTTP/WS server, C SDK); Transformers ≥5.13 (`set_num_lookahead_tokens`, per-chunk `language`) | OpenMDW-1.1, card ghi ready for commercial use |
| [Qwen3-ASR](qwen3-asr-family.md) 1.7B / 0.6B | Buffered: paper dùng 2 s chunk, 5-token fallback, bốn chunk cuối unfixed; mạnh ở turn-final | Offline FLEURS-vi 5.55 / 8.52; MLC-SLM-vi 14.92 / 17.67 | `qwen-asr` + vLLM; WhisperLiveKit windowed; SGLang-Omni chỉ qua HTTP `/v1/audio/transcriptions` | Apache-2.0 |
| Whisper large-v3-turbo 809M | Turn-final; live captions cần WLK SimulStreaming/LocalAgreement | Chưa có matched vi score cho turbo; Whisper large-v3 16.44% mean WER trên ba tập vi (VietASR, theo report) | [Faster-Whisper](faster-whisper.md) CTranslate2 fp16 / `int8_float16`; HF s2s; Pipecat `WhisperSTTService` | MIT |
| [PhoWhisper](phowhisper.md) medium/large | Turn-final | large VIVOS 4.67, CMV 8.14 | Convert sang CTranslate2, cần test parity | BSD-3-Clause |
| [ChunkFormer](chunkformer-vietnamese.md) RNNT large 113M | Final-pass; streaming-trained checkpoint chưa rõ | VIVOS 2.49, CMV 5.18, VLSP2020 T1/T2 12.75/20.47 | ONNX CPU/GPU | CC-BY-4.0 (CTC 110M là NC) |
| Fun-ASR-MLT 800M / Cohere Transcribe 2B | Turn-final challengers | Có vi trong language list, thiếu matched vi score/latency | FunASR; Transformers/vLLM | Apache-2.0 |
| [ZipFormer 30M](zipformer-30m-vietnamese.md) vi | CPU research, chưa native streaming protocol | VLSP2020 T1 12.29; author CPU file throughput | sherpa-onnx | CC-BY-NC-ND — loại khỏi thương mại |

- Các con số khác tập test/normalizer/protocol; không xếp Qwen 5.55 trước Nemotron 12.29 như cùng realtime protocol, không xếp VIVOS trước FLEURS. Chunk size của Nemotron không phải tổng first-stable-text hay endpoint→final latency. Qwen 92 ms TTFT là decode request có audio ~2 phút sẵn ở concurrency 1, không phải mic latency và không phải capacity 128 cùng 92 ms. Tên 0.6B/1.7B của Qwen chưa gồm toàn encoder/projectors/cache (**Reported/Synthesis**).[^asr][^qwen][^nemotron]
- Nemotron phải đặt locale `vi-VN` tường minh: Transformers pipeline mặc định prompt index-0 `en-US` (**Reported**).[^nemotron]
- Không đủ Vietnamese scope để thay baseline: Parakeet 25-European/derivatives, Canary, Voxtral, Audio8 Infinite/0.1B, SenseVoiceSmall, GLM-ASR, Hojo, ARK, VibeVoice Streaming, Granite TurboCTC, Distil-Whisper English, English EOU. Confucius4-R2T2 chưa có explicit vi evidence. Không chọn model chỉ vì English leaderboard hoặc chữ "multilingual" (**Reported/Synthesis**).[^asr]

**Ba mẫu ghép ASR (Synthesis):**

1. **Single-pass turn-final** (đơn giản nhất): VAD/turn cắt lượt → Whisper turbo / Qwen3-ASR / PhoWhisper. Latency = endpoint + decode cả câu; không có partial cho captions hay speculative LLM.[^asr][^stack]
2. **Single-pass native streaming:** Nemotron 160–320 ms; partial sớm, accuracy FLEURS thấp hơn Qwen offline.[^nemotron][^asr]
3. **Two-pass selective:** Nemotron streaming cho partial/UI/speculation, cuối lượt Qwen3-ASR 1.7B hoặc ChunkFormer RNNT large cho final; tốn compute, phải reconcile transcript revision và không hành động trên partial chưa commit.[^asr]

**Cấu hình Whisper bắt buộc** khi dùng faster-whisper (**Reported**):[^halluc]

- Decode: `language="vi"` (auto-detect trên clip ngắn ồn dễ sai); `beam_size=1–3` (3 tốt hơn nhưng chậm ~30–50%); `condition_on_previous_text=False`; `temperature=0.0`; `vad_filter=True` với `min_silence_duration_ms=500` làm lớp lọc thứ hai; `no_speech_threshold=0.6`, `log_prob_threshold=-1.0`, `compression_ratio_threshold=2.4`; `hotwords`/`initial_prompt` ngắn cho tên riêng, không bao giờ đưa "cảm ơn đã xem" vào prompt.
- Lọc sau decode: bỏ segment `no_speech_prob > 0.6` và `avg_logprob < -1.0`; bỏ cả turn nếu `compression_ratio > 2.4` hoặc <2 từ khi VAD <400 ms; regex blacklist (`subscribe`, `đăng k[ýí] (cho )?kênh`, `để không bỏ lỡ những video`, `cảm ơn (các bạn )?đã (xem|theo dõi)`, `La La School`, `Ghiền Mì Gõ`, câu lặp nguyên văn ba lần).
- Materialize generator (`list(segs)`) trong worker thread; lặp lazy generator trên asyncio event loop sẽ block pipeline.
- **Synthesis caveat:** blacklist chỉ là signal kết hợp acoustic evidence; user có thể nói thật "subscribe" hoặc một lệnh ngắn "không/dừng", nên luật "<2 từ" phải tune trên dữ liệu thật. Thay Whisper khi WER tiếng Việt có nhiễu >~15%, hallucination vẫn lọt filter, hoặc cần partial (**Reported** trigger).[^halluc][^stack]

### Text→speech bridge tiếng Việt

**Synthesis:** external LLM adapter chỉ yêu cầu streaming text/done/error/cancel và generation correlation, không chọn model. Prompt hệ thống nói-chuyện nên yêu cầu câu ngắn, không markdown/emoji/bảng/URL và hỏi lại khi không chắc đã nghe đúng (**Reported**).[^stack][^hf]

- **Chunker (Reported starting rule):** flush khi gặp `.?!…;:` hoặc xuống dòng; chunk đầu cắt ở dấu phẩy khi đã có ≥~25 ký tự để giảm TTFA; gộp mảnh <8 ký tự vào câu sau.[^stack] Không flush từng token, không chờ full answer; giữ nguyên số/ngày/viết tắt/entity chưa hoàn chỉnh; A/B prosody ở ranh giới chunk đầu ngắn (**Synthesis**).[^tts]
- **Normalizer:** tách display/raw text khỏi spoken text: tiền (`1.250.000đ` → "một triệu hai trăm năm mươi nghìn đồng"), số điện thoại (đọc từng digit), số đếm, ngày/giờ (ambiguity cần domain rule), %, đơn vị (km/h), viết tắt (TP.HCM, UBND), tên riêng và code-switch (giữ tiếng Anh chỉ khi TTS xử lý được; VieNeu có) (**Reported**).[^stack] Unicode NFC/dấu, strip markup/URL theo spoken policy, giữ punctuation phục vụ prosody, regression prompts là yêu cầu đề xuất; wiki chưa chọn thư viện Vietnamese normalizer đã verified (**Synthesis**).[^tts]
- **Lexicon:** VieNeu v3 Turbo có lỗi G2P đã biết đọc `chánh` thành `tránh` (issue #207, chưa reproduce) → cần substitution dictionary cho tên riêng và domain terms (**Reported**).[^vieneu][^stack]
- Audio-output streaming ≠ incremental text-input: VieNeu `infer_stream` và VoxCPM2 `generate_streaming` nhận text sẵn rồi phát chunks; clause-level calls là bridge đề xuất, không gọi là native bi-streaming (**Reported/Synthesis**).[^tts]

### TTS tiếng Việt và đường phục vụ

Capabilities là **Reported**; deployment priority là **Synthesis**.[^tts]

| Candidate | Vai trò | Model + deploy path | Streaming / perf (Reported) | License / gate |
|---|---|---|---|---|
| [VieNeu v3 Turbo](vieneu-tts-v3-turbo.md) | Baseline | Vietnamese-first vi/en, 48 kHz, 25 preset voices, instant cloning; SDK `infer_stream`; `apps/openai_speech.py` `POST /v1/audio/speech` (pcm/wav, chunked hoặc SSE), Docker Compose `api-gpu`/`api-cpu` port 8000 | RTX 3060 warm: 1 stream TTFA ~115 ms RTF 0.49; 16 streams median 185 ms, RTF 0.59, max 339 ms; CPU fp32 260–400 ms, RTF 0.55–0.61; CPU INT8 140–195 ms, RTF ~0.35 (cần VNNI) | FAQ Apache/commercial vs roadmap "on-device, personal use" — mâu thuẫn mở; `style` bị bỏ qua, đọc theo reference.[^vieneu] |
| [VoxCPM2](voxcpm2.md) 2B | GPU quality/cloning challenger | 30 ngôn ngữ có vi, voice design/cloning; `voxcpm.generate_streaming`, API adapter tự làm | RTF ~0.3 RTX 4090, ~0.13 với Nano-vLLM (card; accelerator chưa inspect); ~8 GB VRAM; chưa có TTFA/vi MOS | Apache-2.0.[^vox] |
| Supertonic 3 ~99M | CPU/on-device challenger | ONNX SDK, vi trong 31 ngôn ngữ | `synthesize` trả full waveform; short-clause không đồng nghĩa frame streaming; không dùng RTF v2 cho v3 | OpenRAIL-M weights.[^tts] |
| Kokoro Vietnamese | CPU A/B | ONNX/PyTorch, vig2p, voicepacks | Chưa có numeric quality/TTFA/streaming; Kokoro support trong Speaches/HF không chứng minh checkpoint vi tương thích | Apache theo card.[^tts] |
| [MOSS-TTS Local v1.5](moss-tts-local-transformer-v1-5.md) | GPU streaming challenger | vi trong 31; HF / SGLang-Omni; language tags, cloning, pause | Native 48 kHz stereo nhưng PCM example mono — xác nhận channels/framing; thiếu numbers; không gán cùng path cho flagship 8B | Apache theo card.[^moss] |
| Higgs TTS 3 / Fish S2 Pro | Expressive | SGLang-Omni; Higgs còn vLLM-Omni | H100/H200 claims (Fish ~100 ms TTFA) không chứng minh vi TTFA | Non-commercial; chỉ research hoặc license riêng.[^tts] |
| G-OmniVoice / Gwen-TTS | Cloning/listening A/B | `omnivoice` / `qwen-tts` | Full waveform, chưa streaming/latency; G-OmniVoice MOS 7.685 thiếu scale/protocol | Lineage base-NC/tokenizer (G) và TikTok data rights (Gwen) pending.[^tts] |
| VieNeu v3 Nano / sanoTTS vi | Edge | Nano 48M ONNX 24 kHz finished chunks; sano voice vi 1.46M piperlite 22.05 kHz | Nano English/code-switch yếu hơn; sano vi chưa có điểm; không chuyển English MCU benchmarks sang voice vi | sanoTTS GPL-3.0.[^tts] |

- Bulk RTF 0.011–0.02 của VieNeu không đại diện một stream; 16 TTS streams không bằng 16 pipeline đồng thời; tất cả số chưa reproduce (**Reported/Synthesis**).[^vieneu]
- **Không dùng out-of-box cho vi** theo catalog đã đọc: Qwen3-TTS chính thức (10 ngôn ngữ không vi; Faster Qwen3-TTS/vLLM-Omni không tự thêm vi; Gwen là checkpoint khác cần parity riêng), CosyVoice2/Fun-CosyVoice3, Audio8 Preview, Chatterbox, Pocket, Sopro, Soprano, VibeVoice, Breeze, GLM-TTS, IndexTTS2/2.5, GPT-SoVITS, Supertonic v1/v2, Irodori, Indic Parler. Đây là thiếu vi trong scope đã compile, không phải chứng minh không thể (**Reported/Synthesis**).[^tts]

### Orchestration

| Lựa chọn | Phù hợp | Chi phí tích hợp tiếng Việt |
|---|---|---|
| Pipecat (BSD-2) | Custom cascade; WebRTC (Daily, SmallWebRTC), WS, telephony | Có sẵn `SileroVADAnalyzer`, `LocalSmartTurnAnalyzerV3`, `WhisperSTTService` (faster-whisper), `OpenAILLMService(base_url=...)`; chỉ cần custom `TTSService` có `run_tts()` gọi VieNeu `/v1/audio/speech`; Nemotron/Qwen streaming cần adapter riêng (**Reported/Synthesis**).[^frameworks][^vieneu] |
| LiveKit Agents (Apache-2.0) | Cần WebRTC SFU / SIP | Turn detector không có vi; ASR/TTS qua plugin OpenAI-compatible hoặc custom.[^frameworks][^turns] |
| [HF speech-to-speech](speech-to-speech-pipeline.md) (Apache-2.0) | OpenAI Realtime subset (bao gồm `response.cancel`, `conversation.item.truncate`), Smart Turn v3.2 sẵn, swappable backends | Đổi defaults không có vi (Parakeet TDT, Qwen3-TTS): `--stt faster-whisper` với `--language vi`, hoặc Qwen3-ASR backend; Nemotron chỉ qua extra `nemo` với `--stt nemotron-streaming` + model name — hỗ trợ Nemotron 3.5 `vi-VN` chưa được xác nhận; TTS qua OpenAI-compatible `/v1/audio/speech` trỏ VieNeu.[^hf] |
| TEN Framework (Apache "with conditions") / FastRTC (MIT) | Agora RTC / Gradio WebRTC | Không có lợi thế tiếng Việt đã compile.[^frameworks] |
| Gateway FastAPI/asyncio tự viết | Kiểm soát toàn bộ turn/cancel | Report có reference server (`VADIterator` mỗi session, gate barge-in 400 ms, `asyncio.to_thread` transcription, `{"type":"clear"}`) nhưng body VieNeu và Docker tags cần kiểm lại; phải tự làm cancellation/metrics (**Reported**).[^stack] |

So sánh framework là bằng chứng AI report thứ cấp; plugins hiện hành chưa inspect; HF s2s có README gốc (**Synthesis**).[^frameworks][^deploy]

## Sáu cấu hình ghép model và deploy tool

| Profile | VAD/Turn | ASR + runtime | TTS + runtime | Orchestration/transport | Chọn khi nào / gate |
|---|---|---|---|---|---|
| A — MVP turn-final (1 GPU 12–24 GB) | Silero ONNX + Smart Turn CPU + timeout 1.2–1.5 s | Whisper large-v3-turbo `vi` + Faster-Whisper fp16/`int8_float16` + filter; hoặc Qwen3-ASR 0.6B | VieNeu v3 Turbo GPU qua `/v1/audio/speech` | Pipecat + SmallWebRTC, hoặc HF s2s `serve` + external OpenAI-compatible LLM | Ít adapter nhất; chờ endpoint rồi decode. Không native ASR streaming; test TTS schema và cancellation.[^asr][^hf][^frameworks][^vieneu][^halluc] |
| B — native streaming baseline | Như A, state per-session trên CPU | Nemotron 3.5 0.6B `vi-VN`, thử chunk 160/320 ms; NeMo reference hoặc NeMo-Speech.cpp Q8 | VieNeu GPU streaming hoặc ONNX CPU | Pipecat/custom gateway; WebRTC khi cần remote barge-in | Thử đầu tiên nếu cần partial sớm; ASR custom adapter có thể cần, chưa có bằng chứng plug-and-play.[^asr][^nemotron][^nemo][^frameworks][^tts] |
| C — quality-oriented single-pass | Như A | Qwen3-ASR 0.6B→1.7B; `qwen-asr` vLLM hoặc WLK windowed | VieNeu; A/B VoxCPM2 `generate_streaming` + service riêng | Gateway/agent framework, transcript revision policy | Chấp nhận buffering/rollback; toolkit streaming gốc không batch/timestamps; chưa có vi streaming WER.[^asr][^qwen][^vox] |
| D — two-pass selective (production nhiều phiên) | Như B | Nemotron live partial + Qwen3-ASR 1.7B vLLM hoặc ChunkFormer RNNT large final-pass | VieNeu GPU server (`VIENEU_MAX_STREAMS` theo tải); thay VoxCPM2 nếu listening/cost gate tốt hơn | Pipecat/LiveKit + WebRTC; tách GPU theo service; gateway sở hữu revisions/commit/cancel; P95 observability | Chỉ khi số/tên/phủ định/domain cần final recheck và B/C chưa đạt; thêm compute/lag; chưa benchmark toàn tổ hợp.[^asr][^tts][^vieneu] |
| E — CPU/edge/on-prem | Silero ONNX + Smart Turn int8 | Nemotron 3.5 Q8 qua NeMo-Speech.cpp CPU (đo lại: 27 ms/160 ms chunk CPU là model EN); RealtimeSTT/sherpa INT8 là packaging khác cần gate; hoặc Whisper CT2 INT8 turn-final | VieNeu ONNX fp32 (INT8 chỉ khi có VNNI); A/B Supertonic 3 / Kokoro vi ONNX; VieNeu Nano cho CPU yếu; sanoTTS cho MCU | Gateway local/embedded, WS loopback, pre-stage models | Không cam kết full stack realtime trên CPU bất kỳ; Parakeet final mặc định của RealtimeSTT thiếu vi; audio.cpp port VieNeu chưa xác minh.[^deploy][^asr][^tts][^nemo][^vieneu][^audio] |
| F — license-strict thương mại | Silero (MIT) + Smart Turn (BSD-2, reported) | Qwen3-ASR (Apache-2.0), Whisper (MIT), PhoWhisper (BSD-3), ChunkFormer RNNT (CC-BY-4.0); Nemotron 3.5 (OpenMDW-1.1, card ghi commercial-ready) sau legal review | VoxCPM2 (Apache-2.0); VieNeu chỉ sau khi giải quyết mâu thuẫn license; MOSS Local (Apache theo card) | Pipecat (BSD-2), LiveKit (Apache-2.0), HF s2s (Apache-2.0) | Tránh ZipFormer NC-ND, ChunkFormer CTC NC, OmniVoice/G-OmniVoice NC lineage, Higgs/Fish, Gwen data rights chưa rõ, sanoTTS GPL (nếu không chấp nhận copyleft), Supertonic OpenRAIL-M use restrictions.[^asr][^tts][^turns][^silero][^whisper][^nemotron][^vieneu][^vox][^frameworks][^hf] |

**Synthesis:** không triển khai D ngay từ đầu nếu B/C đạt domain accuracy. Hai-pass có thể chỉ bật cho critical spans hoặc quality review; final recognizer không phải ground truth. Nếu output phụ thuộc final correction thì chưa phát âm/side effect trước commit; nếu speculation đã chạy trên partial thì discard/cancel khi revision đổi. License là hard gate trước điểm chất lượng ở mọi profile, F chỉ gom lại các lựa chọn ít rủi ro nhất.[^asr][^hf][^barge][^tts]

## Hợp đồng điều khiển chi tiết

### 1. Audio ingress và privacy

**Synthesis:** browser capture dùng AEC khi loa ngoài; noise suppression/AGC A/B thay vì cho là luôn giúp. Transport 20 ms frames có thể reblock thành 512 samples/32 ms ở 16 kHz cho Silero (256 ở 8 kHz); không bắt VAD/ASR/TTS dùng cùng chunk length. Gateway canonical ASR audio 16 kHz mono; telephony 8 kHz decode đúng rồi resample, không coi upsampling khôi phục thông tin mất. Output giữ native sample rate đến playback adapter; chỉ resample khi transport yêu cầu.[^silero][^barge][^hf]

Giữ 200–300 ms pre-roll là starting design, không cutoff đã đo. Một VAD/ASR state riêng mỗi session; không dùng cache người này cho người kia. Audio thiếu packet/gap cần policy rõ, không concatenate lệch timeline. Denoise optional ở VAD branch; ASR baseline là AEC audio (**Synthesis**).[^silero][^noise]

**Privacy requirements (Synthesis):** TLS/auth tại gateway, service ports private, giới hạn upload/reference duration và request size; không cho client tùy ý trỏ reference URL/path. Logs mặc định metadata không audio/transcript (HF s2s content-free mặc định, `--log_transcripts` là opt-in); corpus đánh giá phải opt-in, access control, retention và consent. Speaker embeddings/cloning refs cũng có disclosure boundary, không ghi vào operational log. LLM proxy của HF s2s không có auth/throttling riêng: giữ tắt hoặc đặt sau gateway.[^hf][^barge][^tts]

### 2. VAD, endpointing và turn ownership

Starting settings là **Reported** từ report hoặc **Synthesis**, không phải API copy-paste hay production defaults:[^silero][^turns][^asr][^barge][^stack]

| Policy | Điểm bắt đầu để tune |
|---|---|
| Input | 16 kHz mono; 20 ms transport; 512-sample VAD blocks |
| Silero | `load_silero_vad(onnx=True)`; một `VADIterator`/session, `reset_states()` mỗi khi hết lượt; `threshold=0.5` (0.6–0.7 khi nền rất ồn; `VADIterator` có hysteresis off ~0.15 thấp hơn); `min_silence_duration_ms` 200–300; `speech_pad_ms` 100–200 để giữ phụ âm đầu/cuối quan trọng cho thanh điệu; `min_speech_duration_ms` 250 (**Reported**) |
| Adaptive threshold | Đo VAD prob/RMS 2–3 s đầu trước khi user nói; nếu nền >0.3 thì nâng threshold lên 0.65–0.7 và nâng gate barge-in (**Reported**); không tự động raise theo một số cố định khi chưa calibrate (**Synthesis**) |
| End candidate có Smart Turn | 200–300 ms silence (Pipecat `stop_secs=0.2`) rồi classifier trên 8 s audio cuối; incomplete thì tiếp tục giữ turn |
| Không semantic detector | 500–800 ms silence, tune theo tốc độ nói và pause (**Synthesis**) |
| Fallback | 1.2–1.5 s silence là upper-wait; không cộng thêm sau mỗi positive |
| ASR | Nemotron `vi-VN` 160/320 ms trial; Qwen policy buffered riêng; Whisper per-turn với cấu hình trên |
| Barge-in | Clean: thử 150–200 ms speech; noisy: threshold 0.7 và ≥300–500 ms (reference server 400 ms); giữ lệnh ngắn có chủ đích |

Chỉ một owner (gateway hoặc tracker framework) quyết định turn close/reopen/commit; VAD/ASR/TTS servers chỉ cung cấp signals. Học control design của HF tracker (soft-end/reopen/revision/output-gating) nhưng không chép default 64 ms/800 ms/2 s thành cùng policy với bảng trên (**Reported/Synthesis**).[^hf]

### 3. Transcript revisions và safety boundary

**Synthesis schema proposal**, không phải vendor event schema:[^asr][^hf][^barge]

```text
session_id, turn_id, revision, generation_id, sequence
asr.partial(text, stable_prefix_if_available)
asr.final(text, model_id, language, quality_flags)
turn.commit(turn_id, revision)
text.chunk(generation_id, chunk_id, raw_text, spoken_text)
audio.start(generation_id, format, sample_rate, channels)
audio.chunk(generation_id, chunk_id, sequence, payload)
audio.played(generation_id, played_sample_offset)
response.cancel(generation_id)
client.clear(generation_id)          # tương đương {"type":"clear"} / audio_cancel
```

- Partial dùng cho captions; chỉ speculative compute trước commit, không side effects. Stable prefix không tự là confidence hay final truth.
- Final-pass (D) chạy lại turn audio giữ nguyên, không đổ full transcript lên partial stream gây duplicate; final event thay một revision, commit một lần. Ambiguity ở số/tên/phủ định → ask-back interface, không majority vote thành sự thật.
- Confidence scales giữa ASR models không calibrated; missing confidence giữ unknown. Validity gate (confidence, hallucination filter, speaker lock) là policy của gateway áp dụng theo khả năng từng ASR, không phải capability chung (**Synthesis**).[^halluc][^barge]
- Session closed/disconnected → release ASR cache, cancel inference nếu hỗ trợ, flush queues, không dispatch stale callbacks.

### 4. Barge-in, cancellation và history

- **Trình tự (Reported):** gắn `generation_id` vào mọi chunk LLM/TTS; khi ngắt: tăng id, cancel LLM stream, cancel request TTS HTTP/WS, xóa queued sentences, gửi `{"type":"clear"}`/`audio_cancel` để client flush AudioWorklet buffer, chỉ lưu phần đã phát vào history với tag `[bị ngắt]`.[^barge][^stack]
- **Gating (Reported):** duration gate chặn tiếng ngắn (ho, gõ phím); speaker lock so cosine embedding ECAPA/CAM++ của segment mới với embedding user (lấy từ lượt đầu, cập nhật dần), bỏ dưới ~0.5–0.6 — ngưỡng phải calibrate; tùy chọn yêu cầu quick ASR ≥2 từ không trùng câu đang phát.[^barge]
- **Synthesis:** giữ mic on + AEC; drop mọi late chunk của generation cũ. Đo cả user-speech→stop-audible và time-to-release-compute. SDK có thể không cancellable bên trong: đó là deployment gate. Speaker lock không phải authentication, diarization không biết danh tính. Không mặc định mọi "ừ/vâng/ok" là backchannel bị bỏ qua: domain có thể coi đó là xác nhận quan trọng. Không có token/audio alignment thì chỉ claim played offset, không exact words; HF s2s có `conversation.item.truncate` là điểm nối tự nhiên cho played offset.[^barge][^hf][^diar]

### 5. Diarization chỉ khi nhiệm vụ cần

Agent một-user: không thêm diarizer vào critical path. Meeting/multi-user: giữ separate tracks nếu đã có participant identity; audio-mix fallback thử Nemotron 3 Diarization / NeMo-Speech.cpp, tối đa 8 speakers, profiles input-buffer 0.32/0.64/1.04 s theo card. Các số không gồm compute hay speaker identity verification; DER vi/overlap chưa có (**Reported/Synthesis**).[^diar][^nemo]

## Deploy tools: chọn đúng tầng

| Tầng | Lựa chọn / vai trò | Evidence boundary |
|---|---|---|
| CPU VAD | Silero ONNX | Detector, không phải dialogue orchestrator.[^silero] |
| Nemotron inference/server | NeMo reference; NeMo-Speech.cpp native HTTP/WS/C SDK; Transformers ≥5.13 | Q8 runtime compatibility phải test; 27 ms CPU/160 ms chunk là model EN, không phải 3.5 vi.[^nemo][^nemotron] |
| Qwen ASR | `qwen-asr`/vLLM; WLK windowed; SGLang-Omni HTTP | Streaming protocol/cache/concurrency cần riêng; WLK causal English-only; SGLang transcription HTTP không chứng minh native audio WS.[^asr][^qwen][^deploy] |
| Whisper inference/live policy | Faster-Whisper CT2; WLK SimulStreaming/LocalAgreement hoặc RealtimeSTT | WLK không phải LiveKit Agents; không hai segmentation owners.[^deploy] |
| Vietnamese TTS | VieNeu SDK/API (Docker `api-gpu`/`api-cpu`); VoxCPM2 Python adapter; ONNX TTS service | VieNeu `VIENEU_MAX_STREAMS` mặc định 16 GPU / 1 CPU, hàng đợi nhỏ, vượt thì HTTP 429; mỗi slot dự trữ thêm ~2.5 ms mỗi codec call nên đặt theo tải thật. Không có tài liệu vLLM-Omni phục vụ VieNeu/VoxCPM2 trực tiếp.[^vieneu][^tts][^vox] |
| Multi-stage GPU serving | SGLang-Omni cho MOSS Local/Higgs/Fish; vLLM-Omni khi exact checkpoint recipe có evidence | Không cần cả hai mặc định.[^deploy][^moss] |
| Native multi-model | audio.cpp; transcribe.cpp STT-centric | Alternate implementation sau reference parity; VieNeu community port chưa inspect; GGUF khác runtime có thể khác layout.[^audio][^deploy] |
| Orchestration | HF s2s / Pipecat cho MVP; Pipecat custom cascade; LiveKit Agents cho RTC/SIP | Comparison thứ cấp; custom ASR/TTS adapters có thể cần.[^hf][^frameworks] |

**Deployment plan (Synthesis):** Docker Compose trước, một model owner/process thay vì mỗi gateway worker load weights; tách environment ASR/TTS/ONNX để tránh xung đột torch/transformers/CUDA. Containers: public RTC/gateway; private asr-service; optional final-asr-service; tts-service; telemetry. External LLM nằm ngoài scope nhưng phải tính contention nếu cùng GPU.[^deploy][^hf][^vieneu]

Pin revision/checksum của runtime/weights/G2P/voicepack/normalizer, pre-stage offline, warm models/graphs, health/readiness chỉ ready sau warmup. Admission cap/`max_streams`, bounded queues/backpressure/429, per-session rate-limit/deadlines/circuit breaker và cleanup là requirements đề xuất. Khi tải tăng, tách streaming ASR và TTS/final-pass sang pool riêng (report gợi ý faster-whisper `BatchedInferencePipeline` cho turn-final và continuous batching cho TTS); ưu tiên audio cadence hơn batch throughput. Không scale gateway workers thành GPU copies; tách service theo GPU trước khi cần Kubernetes/disaggregated Omni (**Reported/Synthesis**).[^vieneu][^deploy][^hf][^stack]

VRAM ước lượng của report cho một GPU 24 GB: Whisper turbo fp16 ~2–3 GB, VieNeu GPU ~2–3 GB, phần còn lại cho LLM/KV cache; trên 12 GB dùng turbo `int8_float16` (**Reported**, chưa đo). CPU ASR headroom, VRAM/cache/session và cold start phải đo; không gán claim TTS riêng lẻ thành tổng speech budget. Mid-utterance TTS fallback có thể đổi giọng: ưu tiên retry/new-clause có báo trạng thái thay vì stitch hai giọng (**Synthesis**).[^stack][^tts][^vieneu]

## Latency, monitoring và release gates

**Critical path (Synthesis):** đo từng edge và tổng, không cộng full audio capture vào endpoint latency và không double-count compute đã overlap:[^asr][^tts][^hf]

```text
last user speech sample
  → endpoint commit
  → accepted final ASR
  → external LLM first meaningful clause
  → TTS first playable samples
  → client first audible sample
```

**Ngân sách tham khảo của report (Reported, chưa đo; không phải target):**[^stack][^turns]

| Stage | Ước lượng | Ghi chú |
|---|---|---|
| Network + jitter buffer | 30–80 ms | WebRTC |
| VAD silence | 200–300 ms | Pipecat `stop_secs=0.2` |
| Smart Turn | 10–65 ms | Vendor |
| ASR turn-final (turbo, GPU, câu 3–5 s) | 100–300 ms | Ước lượng, không benchmark độc lập |
| LLM TTFT + chunk đầu | 150–350 ms | Giả định Qwen3-8B AWQ trên vLLM; ngoài scope trang này |
| TTS TTFA | 64–300 ms | VieNeu ~115 ms theo tác giả |
| Voice-to-voice | ~0.7–1.2 s | Phải đo trên phần cứng thật |

**Synthesis:** LLM là dependency bên ngoài nên speech pipeline không cam kết tổng ~1 s khi chưa biết endpoint đó. Preemptive ASR/LLM khi VAD im 200 ms có thể ẩn một phần latency nhưng phải cancel khi user nói tiếp. Qwen TTFT, VieNeu TTFA, batch RTFx, chunk size và classifier compute là metrics khác nhau. Gate khởi điểm: TTS TTFA P95 ~250–400 ms và RTF P95 ≤0.7 dưới tải thực; end-to-end theo SLA sản phẩm; profile C/D có thể chậm hơn B; CPU profile chưa cam kết cùng gate.[^tts][^asr][^stack]

**Monitoring per-turn (Reported):** `vad_end→asr_done`, `asr_done→llm_first_token`, `first_sentence→tts_first_byte`, voice-to-voice phía client, tỷ lệ transcript bị lọc, barge-in rate, false-interruption rate.[^stack] HF s2s đã log STT/LLM/first-TTS-audio/speech-to-audio per response (**Reported**).[^hf]

**Release gates (Synthesis từ evidence ASR/TTS/control/server):**[^asr][^tts][^barge][^hf][^deploy][^noise][^turns][^stack]

1. **ASR corpus:** Bắc/Trung/Nam; tên/số/địa chỉ/phủ định/code-switch; 8 kHz call vs 16 kHz mic; far-field; nhiễu café/xe máy/TV ở SNR 0/5/10/20 dB có và không denoise; silence/nhạc để đo hallucination. Cùng ground truth/normalizer; WER/CER + exact critical-span accuracy, tỷ lệ partial bị sửa, first partial, first-stable-text, endpoint→final P50/P95.
2. **TTS 150–300 prompts:** blind pairwise/MOS/CMOS với 10–20 người nghe Việt; thanh điệu/phát âm/tự nhiên/nhất quán giọng; cloning và presets tách riêng; test normalizer, lexicon và ranh giới chunk. ASR round-trip CER chỉ là proxy.
3. **Turn/barge-in:** pause dài giữa câu, "không/dừng" ngắn, backchannel, TV nền, bot echo, user nói đè, ho/gõ phím; false-cutoff, missed/false-interrupt, stop-audible, recovery; trigger thay Smart Turn khi false-interruption vi >10%.
4. **Load:** warm/cold, sustained + simultaneous starts, concurrency 1/4/8/16, memory/session, queue/stalls, dropped frames, TTS underrun, shared-GPU ASR/TTS/external LLM; chỉ nâng concurrency khi đạt P95/cadence, không suy từ throughput H100 trong paper.
5. **Contract tests:** 48k/24k/unknown rate, mono/stereo, dtype, PCM-vs-WAV/SSE, monotonic sequence/revision, cancel mid-chunk, disconnect/reconnect, timeout, OOM, 429; không stale audio, không duplicate final, không action trên text chưa commit.
6. **Rights/security:** license runtime/weights/voicepack/data lineage riêng; consent reference; TLS/auth; private model ports; content-free logs; commercial gates (VieNeu ambiguity, Fish/Higgs/Omni NC, G-OmniVoice lineage, Gwen data rights, GPL/RAIL/vendor terms).

## Quyết định và lộ trình

- **Phase 1:** A (HF s2s hoặc Pipecat + Whisper turbo `vi` + VieNeu) để có measurable whole loop từ ngày đầu; chọn B nếu partial là requirement ngay. Warmup, normalizer/lexicon, explicit audio contracts, Whisper filter và per-turn logs trước optimizer (**Synthesis**; route MVP Pipecat là **Reported**).[^hf][^asr][^tts][^stack][^halluc]
- **Phase 2 (beta):** A/B Nemotron 160/320/560 ms vs Qwen 0.6B/1.7B đúng streaming/turn-final policy; TTS VieNeu vs VoxCPM2, CPU VieNeu vs Supertonic 3/Kokoro; duration-gated barge-in, speaker lock và denoise-chỉ-nhánh-VAD; mỗi lần đổi một component (**Synthesis**).[^asr][^tts][^barge][^noise]
- **Phase 3 (production):** thêm D nếu entity-error gain đáng compute/latency; tách GPU theo service với P95 observability; Smart Turn/Namo sau calibrated false-interruption tests; multi-user mới thêm diarization; đổi runtime sang audio.cpp/native chỉ sau output/latency/parity gate (**Synthesis**).[^asr][^barge][^turns][^audio][^diar]

## Relationships

- Uses [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) và [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md): ghép shortlist thành profiles/control/deployment, không thay bảng source-specific quality.[^asr][^tts]
- Uses [So sánh công cụ triển khai speech](speech-deployment-tools-comparison.md): phân tầng runtime/API/policy/orchestration, không coi generic server là native streaming.[^deploy]
- Refines [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md): giữ chunker, normalizer, latency budget, monitoring và route MVP của report nhưng thay ASR/TTS theo primary-source follow-up và giữ LLM model out-of-scope; không supersede lịch sử report.[^stack]
- Depends on [Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md), [Turn Detection Models](turn-detection-models.md), [Speech Enhancement Before ASR](speech-enhancement-before-asr.md), [Whisper Hallucination Mitigation](whisper-hallucination-mitigation.md): các starting policies còn thứ cấp và phải tune.[^barge][^turns][^noise][^halluc]
- Complements [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) và [Voice Agent Frameworks](voice-agent-frameworks.md): thay defaults không có vi bằng backend tiếng Việt.[^hf][^frameworks]
- Uses [Nemotron 3.5 ASR](nemotron-3.5-asr-streaming-0.6b.md), [Qwen3-ASR family](qwen3-asr-family.md), [Whisper Large v3 Turbo](whisper-large-v3-turbo.md), [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md), [VoxCPM2](voxcpm2.md), [MOSS-TTS Local v1.5](moss-tts-local-transformer-v1-5.md), [NeMo-Speech.cpp](nemo-speech-cpp.md), [audio.cpp](audio-cpp-framework.md), [Silero VAD](silero-vad.md), [Nemotron 3 Diarization](nemotron-3-diarization.md) làm thành phần ứng viên.[^nemotron][^qwen][^whisper][^vieneu][^vox][^moss][^nemo][^audio][^silero][^diar]

## Contradictions

Giữ nguyên như các concept nguồn, không chọn phía:

- **VieNeu v3 Turbo license:** FAQ/card Apache-2.0 cho commercial vs roadmap/report ghi "on-device, personal use".[^vieneu]
- **Barge-in trigger window:** 100–200 ms speech (ưu tiên nhạy) vs ≥300–500 ms ở threshold 0.7 (ưu tiên chống ồn, reference server 400 ms).[^barge]
- **Enhancement trước ASR:** một số nguồn báo giúp, "When De-noising Hurts" báo hại trên mọi điều kiện/model đã thử; không có nghiên cứu tiếng Việt.[^noise]
- **TEN VAD vs Silero:** vendor claim TEN chính xác hơn vs benchmark cộng đồng nhỏ Silero F1 91.9% vs TEN 69.2%.[^silero]
- **Endpoint defaults:** HF s2s `--min_silence_ms` 64 ms + speculative reopen 800 ms + Smart Turn max wait 2 s vs report Silero 200–300 ms silence + fallback 1.2–1.5 s; khác thiết kế control (reopen/revision vs commit cứng), không phải cùng tham số.[^hf][^turns][^silero]

## Coverage và giới hạn

- Session chỉ compiled-wiki retrieval và structural check; không mở `raw/`, fetch upstream, cài/build, tải weights, nghe audio, inference hay benchmark. Source resources là local concepts; footnotes chỉ locator vào section đã đọc, chain raw nằm trên từng concept.
- Bản 2026-10-07 hợp nhất một draft thay thế chưa được file (chi tiết tham số Silero/Whisper/Smart Turn, chunker, lexicon, VieNeu deploy, Pipecat composition, latency budget, monitoring, profile license-strict, Contradictions); mọi claim đưa vào đã được kiểm lại trên concept nguồn, và các điểm draft sai/quá tay (two-pass mặc định, bỏ qua mọi backchannel, flag `--stt nemotron`, Qwen3-ASR native streaming qua SGLang-Omni) đã được sửa hoặc loại.
- Inspected map: index/log, các syntheses, ASR/TTS surveys, pipeline reports, HF s2s, WLK, RealtimeSTT, Silero, turn/noise/barge-in/Whisper filters, Nemotron 3.5/Qwen/Whisper turbo/Faster-Whisper/ChunkFormer, VieNeu/VoxCPM2/Supertonic 3/Kokoro/MOSS Local, NeMo-Speech.cpp/SGLang/vLLM-Omni/audio.cpp và Nemotron 3 Diarization. Không claim đọc toàn bộ concepts/raw closure.
- Evidence thứ cấp (AI report) còn trên framework/noise/control/latency budget/Whisper filters; turn detection đã có primary Smart Turn v3.2 capture nhưng chưa tune/đo trên corpus tiếng Việt tự thu; thiếu implementation/recipe/API docs; quyền weights/voices kế thừa từ concept. Không có compatibility event nào được verified; interface/schema là đề xuất, không phải API đã deploy. `draft` vì chưa có target-hardware load/latency, matched Vietnamese quality/cancellation tests và license review; không đặt `verified`.

[^asr]: [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) — Định nghĩa realtime; Shortlist và bằng chứng tiếng Việt (bảng candidates, VLSP/VIVOS/CMV, ZipFormer); Qwen streaming/efficiency; Kiến trúc và hướng triển khai (single/two-pass); Chọn runtime; Loại khỏi shortlist (language lists); Gate đánh giá; Coverage.
[^tts]: [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) — Model nào có bằng chứng tiếng Việt; Không chọn out-of-box cho vi; Không trộn throughput; Triển khai realtime hai tầng streaming (audio-output vs text-input); Gate chọn model; Contradictions và giới hạn (G/Gwen, Kokoro, MOSS, sano).
[^stack]: [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) — Architecture (transport, reference server); Vietnamese coverage by component (Whisper large-v3 16.44%); LLM choice and invocation (spoken prompt, sentence chunking, history `[bị ngắt]`); TTS routing and Vietnamese text normalization (`chánh`→`tránh`); Latency budget (report estimates, VRAM); Deployment tiers (scaling, monitoring, evaluation); Roadmap and replacement triggers.
[^deploy]: [So sánh công cụ triển khai speech](speech-deployment-tools-comparison.md) — Backend nền; Runtime native; Engine GPU; API server; STT streaming; Orchestration; Benchmark; Shortlist theo bài toán; Coverage/license limits.
[^silero]: [Silero VAD](silero-vad.md) — Key characteristics; Versions and streaming configuration (secondary report: 512-sample window, ONNX, `VADIterator`, threshold/min_silence/speech_pad/min_speech); Contradictions (TEN VAD vs Silero); Coverage.
[^turns]: [Turn Detection Models](turn-detection-models.md) — Comparison (Smart Turn, LiveKit, Namo, TEN); Operating practice (`stop_secs`, 8 s window, FP one-in-seven, 1.2–1.5 s timeout, >10% replacement, latency share); Coverage (AI-report provenance).
[^noise]: [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) — Evidence ("When De-noising Hurts"); Practice (no ASR-branch denoise, RNNoise/DeepFilterNet 3, SNR 0/5/10/20 dB A/B); Contradictions; Coverage.
[^halluc]: [Whisper Hallucination Mitigation](whisper-hallucination-mitigation.md) — Decoding parameters (per VAD-cut turn); Post-transcription filters (thresholds, regex blacklist, `list(segs)`); When to stop filtering and replace Whisper (~15% WER).
[^barge]: [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) — Interruption procedure (`generation_id`, `audio_cancel`); Echo-avoidance tiers; Noise-robust gating (0.7 threshold, 300–500 ms, adaptive threshold, ECAPA/CAM++ speaker lock, `{"type":"clear"}`, `[bị ngắt]`, 400 ms); Transport and playback; Contradictions.
[^hf]: [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) — Architecture (Realtime subset incl. `response.cancel`, `conversation.item.truncate`); Installation (DeepFilterNet/`fireredvad`/`nemo` extras); Supported components (STT/VAD/TTS backends, `--stt nemotron-streaming`); Realtime API and LLM proxy (latency logs, unauthenticated proxy); Endpointing and turn-taking (Smart Turn v3.2, 64/600/800 ms, 2 s, tracker states); Multilingual behavior (`--language` for Whisper); TTS notes/content-free logging; Coverage.
[^frameworks]: [Voice Agent Frameworks](voice-agent-frameworks.md) — Comparison (mid-2026: Pipecat, LiveKit Agents, TEN, FastRTC licenses/transport); Pipecat composition for the recommended stack (custom `TTSService`, SmallWebRTC MVP); Coverage (secondary report).
[^nemotron]: [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) — Vietnamese operating curve (80–1120 ms LangID/auto); Inference and usage (NeMo script, NeMo-Speech.cpp GGUF, Transformers ≥5.13 default `en-US`); Trust, license (OpenMDW-1.1, commercial-ready).
[^qwen]: [Qwen3-ASR family](qwen3-asr-family.md) — Family members/license; Inference and serving (`qwen-asr`, vLLM); Primary-paper clarification (2 s chunks, rollback, 92 ms concurrency 1, encoder sizes); Language and audio coverage (aligner no vi); Coverage.
[^whisper]: [Whisper Large v3 Turbo](whisper-large-v3-turbo.md) — Card provenance and license (`license: mit`, 809M); hallucination limits; Coverage (no numeric WER in card).
[^nemo]: [NeMo-Speech.cpp](nemo-speech-cpp.md) — Supported applications/models; Performance (Nemotron EN benchmark 27 ms CPU, not 3.5); Server, SDK, source build; Coverage (API/build/benchmark guides unavailable).
[^vieneu]: [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) — Model identity; Runtime and SDK (`infer_stream`); Serving API and Docker (`apps/openai_speech.py`, `/v1/audio/speech`, `VIENEU_MAX_STREAMS`, 429, `api-gpu`/`api-cpu`); Benchmarks (RTX 3060/CPU TTFA/RTF); Licensing and use rights; Voice-agent integration notes (G2P issue #207); Contradictions; Coverage.
[^vox]: [VoxCPM2](voxcpm2.md) — Intro and Real-Time Streaming (RTF ~0.3 RTX 4090, ~0.13 Nano-vLLM, `generate_streaming`); Architecture/training (~8 GB); Languages; License (Apache-2.0); Coverage (Nano-vLLM pointer uninspected).
[^moss]: [MOSS-TTS Local v1.5](moss-tts-local-transformer-v1-5.md) — Languages; HF inference (stereo 48 kHz, 12 RVQ); SGLang-Omni serving (PCM stream with mono example); Coverage (missing recipe and numbers).
[^audio]: [audio.cpp Framework](audio-cpp-framework.md) — Runtime/backends; Interfaces; Performance/quantization; Coverage (community guide and code missing); GGUF not interchangeable.
[^diar]: [Nemotron 3 Diarization](nemotron-3-diarization.md) — Architecture/I-O; Streaming configurations (buffer latency excludes compute); Inference; Evaluation protocol; Coverage (no matched Vietnamese verification).
