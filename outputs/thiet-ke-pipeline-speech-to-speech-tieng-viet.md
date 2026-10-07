# Lựa chọn và thiết kế pipeline speech-to-speech tiếng Việt

> **Loại tài liệu:** bài viết tổng hợp (deliverable trong `outputs/`, không phải tri thức canonical).
> **Ngày:** 2026-10-07.
> **Cơ sở:** chỉ dùng wiki đã compile. Điểm xuất phát là [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md). Tôi đọc trước các trang tổng hợp: các trang `type: Synthesis` và các trang mà `wiki/log.md` ghi là *Answered*/*Reconciled*. Sau đó mới đọc tới các concept về model, runtime và control.
> **Phạm vi bằng chứng:** không mở `raw/`, không cài đặt, không chạy inference, không đo benchmark. Mọi con số trong bài là của vendor/tác giả/report (**Reported**). Mọi lựa chọn và cấu hình đề xuất là suy luận tổng hợp (**Synthesis**). Không có thành phần nào đã được kiểm chứng end-to-end trên tiếng Việt.

---

## 0. TL;DR

1. **Với tiếng Việt, dùng cascade chứ không dùng end-to-end.** Hai model full-duplex speech-to-speech mã nguồn mở có trong wiki ([PersonaPlex 7B](../wiki/personaplex-7b-v1.md) và [NemotronLabs VoiceChat 11B](../wiki/nvidia-nemotronlabs-voicechat-11b.md)) đều khai báo `language: en`. Qwen3-Omni nhận được giọng nói tiếng Việt nhưng không phát được giọng nói tiếng Việt. Còn lại là con đường cascade **VAD → turn detection → ASR → LLM → TTS**, được bọc bởi một gateway có trạng thái theo từng session.
2. **Kiến trúc đề xuất:**
   `Client (AEC) → Silero VAD → endpoint manager (Smart Turn + timeout) → ASR → validity/hallucination gate → [LLM bên ngoài, giao diện OpenAI-compatible] → clause chunker + Vietnamese normalizer → TTS streaming → bounded playback`.
   Barge-in dùng `generation_id`.
3. **Chọn model theo nhu cầu, không theo bảng xếp hạng:**
   - MVP ít tích hợp nhất: faster-whisper `large-v3-turbo` với `language="vi"` + [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md), chạy trên Pipecat hoặc [HF speech-to-speech](../wiki/speech-to-speech-pipeline.md) (**Profile A**).
   - Cần partial transcript sớm: [Nemotron 3.5 ASR Streaming](../wiki/nemotron-3.5-asr-streaming-0.6b.md) với chunk 160–320 ms (**Profile B**).
   - Cần độ chính xác cao: [Qwen3-ASR](../wiki/qwen3-asr-family.md) single-pass (**C**), hoặc two-pass có điều kiện (**D**).
   - CPU/edge: **E**. Ràng buộc license thương mại chặt: **F**.
4. **Ba điều quyết định chất lượng cảm nhận** hơn việc chọn model:
   - Endpointing đúng: không cắt ngang lời user, không chờ quá lâu.
   - Cầu text→speech tiếng Việt: chunker theo mệnh đề, normalizer số/tiền/ngày/viết tắt, lexicon cho tên riêng.
   - Cancellation sạch khi barge-in.
5. **Chưa có số đo cùng điều kiện** về WER, MOS hay độ trễ voice-to-voice tiếng Việt trên cùng một stack. Mọi lựa chọn trong bài là thứ tự thử nghiệm, kèm các gate đo lường cần vượt qua.

---

## 1. Cách đọc bài này

### 1.1 Nguồn đã dùng

| Lớp | Trang wiki | Vai trò trong bài |
|---|---|---|
| Thiết kế tổng hợp | [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md) | Khung chính: kiến trúc, 6 profile, control contracts, gates |
| Answered/Synthesis | [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md) | Phân loại realtime ASR, shortlist tiếng Việt, single-pass và two-pass |
| Answered/Reconciled/Synthesis | [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md) | Shortlist TTS tiếng Việt; phân biệt streaming audio-output và text-input |
| Answered/Synthesis | [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md) | Phân tầng model, runtime, server, streaming policy, orchestration |
| Answered/Reconciled/Synthesis | [Phân nhóm ASR/STT và shortlist realtime](../wiki/realtime-asr-selection.md) | Trục kiến trúc ASR, dải kích thước, các nhãn native/buffered/turn-final |
| Answered/Reconciled | [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md), [TTS Model Survey](../wiki/tts-model-survey.md) | Catalog rộng, phần Streaming & latency, Selection guide |
| Report pipeline | [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md), [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md), [Community STT-LLM-TTS Wiring](../wiki/community-stt-llm-tts-pipeline.md) | Ngân sách latency/VRAM, chunker, normalizer, cấu trúc service |
| Control | [Barge-in & Echo](../wiki/voice-agent-barge-in-and-echo-handling.md), [Turn Detection](../wiki/turn-detection-models.md), [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md), [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md), [Silero VAD](../wiki/silero-vad.md) | Tham số khởi điểm cho VAD/turn/barge-in/filter |
| Orchestration | [HF Speech-to-Speech](../wiki/speech-to-speech-pipeline.md), [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md) | Turn tracker, Realtime API subset, Pipecat composition |
| End-to-end | [PersonaPlex 7B](../wiki/personaplex-7b-v1.md), [NemotronLabs VoiceChat 11B](../wiki/nvidia-nemotronlabs-voicechat-11b.md) | Cơ sở cho quyết định cascade so với full-duplex |

### 1.2 Nhãn bằng chứng

- **Reported:** nguồn khẳng định, chưa ai kiểm tra độc lập. Gồm card, README, paper và các AI report.
- **Observed:** đã thấy trực tiếp trong tài liệu, ví dụ một field, một API hay một bảng.
- **Synthesis:** suy luận của người viết từ các bằng chứng được dẫn.
- **Unverified:** chưa có sự kiện kiểm chứng nào. Điều này không có nghĩa là sai.

Lưu ý quan trọng về độ tin cậy: khá nhiều tham số control đến từ hai **AI report thứ cấp** (bản Claude và bản ChatGPT trong `raw/`). Các tham số này gồm ngưỡng Smart Turn, barge-in, denoise, bộ lọc Whisper, latency budget và so sánh framework. Hãy coi chúng là giá trị khởi điểm để tune, không phải default đã được chứng minh.

---

## 2. Quyết định nền: cascade hay end-to-end?

### 2.1 Hai họ kiến trúc

| Tiêu chí | Cascade VAD→ASR→LLM→TTS | End-to-end full-duplex (speech-in/speech-out) |
|---|---|---|
| Đại diện trong wiki | HF s2s, Pipecat stack, RealtimeVoiceChat, blueprint | PersonaPlex 7B (Moshi-based), NemotronLabs VoiceChat 11B |
| Turn-taking | Gateway hoặc tracker quyết định, dựa trên VAD và turn detector | Model tự xử lý: nghe và nói đồng thời, chồng lời, barge-in |
| Latency được báo cáo | ~0.7–1.2 s voice-to-voice (ước lượng của report, chưa đo) | PersonaPlex: smooth turn-taking 0.170, interruption 0.240 (FullDuplexBench). VoiceChat 11B: ~448 ms turn-taking, 480 ms interruption |
| Tiếng Việt | Ghép được từ ASR và TTS có hỗ trợ `vi` | Cả hai card khai báo `language: en` |
| Kiểm soát, RAG, tool | Dễ: LLM là text, thay được từng thành phần | Khó hơn. VoiceChat 11B có tool calling, nhưng đổi thành phần thì không làm được |
| Phần cứng | Từ CPU/edge đến multi-GPU | PersonaPlex thử trên A100 80 GB. VoiceChat 11B chạy vLLM trên A100/H100/H200/B100/B200/RTX-6000 |

Thông tin về hai model end-to-end là **Reported** từ card. AI report về stack tiếng Việt cũng kết luận rằng omni/end-to-end "chưa thay được cascade cho tiếng Việt": khó kiểm soát, khó gắn RAG/tool, khó thay từng thành phần, và thiếu giọng nói đầu ra tiếng Việt. Report còn ghi Qwen3-Omni-30B-A3B nhận 19 ngôn ngữ giọng nói đầu vào (có vi) nhưng chỉ phát 10 ngôn ngữ (không có vi).

**Kết luận (Synthesis):** chọn cascade. Đây không phải vì cascade "tốt hơn" về bản chất. Lý do là trong snapshot của wiki, chỉ cascade ghép được một vòng tiếng Việt hoàn chỉnh. Sau này, nếu xuất hiện một model full-duplex hỗ trợ tiếng Việt có bằng chứng, hãy đánh giá lại bằng cùng các gate ở Mục 10.

### 2.2 Một biến thể lai đáng biết

HF speech-to-speech có chế độ **direct audio input**: `--stt none --llm_backend chat-completions`. Ở chế độ này, mỗi đoạn VAD được gửi thẳng tới một LLM nhận audio (**Reported**). Cộng đồng cũng có người bỏ hẳn tầng STT bằng một Omni model trong llama.cpp, đổi lại phải dùng LLM nhỏ hơn (**Reported**, anecdote). Với tiếng Việt, khả năng hiểu giọng nói của LLM audio phải được đo riêng. Hướng này chỉ nên coi là thử nghiệm (**Synthesis**).

---

## 3. Nguyên tắc thiết kế

Các nguyên tắc dưới đây là **Synthesis** rút ra từ các trang tổng hợp.

1. **Tách năm tầng:** model, inference runtime, API server, streaming policy, orchestration. Lý do: một runtime hỗ trợ GGUF không có nghĩa là mọi checkpoint đều streaming. Một endpoint "OpenAI-compatible" không có nghĩa là drop-in. Và license của runtime không thay cho license của weights.
2. **Mỗi quyết định turn chỉ có một owner.** Gateway (hoặc turn tracker của framework) là nơi duy nhất quyết định close, reopen và commit một lượt. VAD, ASR và TTS chỉ cung cấp tín hiệu.
3. **ASR nghe audio sau AEC, không qua enhancement.** Denoise chỉ dùng cho nhánh VAD/barge-in, cho tới khi A/B trên WER tiếng Việt chứng minh điều ngược lại.
4. **Mỗi backend khai báo rõ audio contract:** sample rate, dtype, số kênh, framing, cách cancel. VieNeu SDK trả `float32` 48 kHz, còn HTTP trả `s16le` 48 kHz. MOSS Local có codec stereo nhưng ví dụ stream lại là mono. Higgs dùng SSE base64 WAV.
5. **Không hành động trên văn bản chưa commit.** Partial dùng cho caption và cho tính toán speculative. Side effect (tool call, phát âm thanh đã cam kết) chỉ chạy sau `turn.commit`.
6. **Không cộng các con số khác loại.** Chunk size của ASR không phải độ trễ ra văn bản ổn định. TTFT 92 ms của Qwen không phải độ trễ từ mic. TTFA 115 ms của VieNeu không phải độ trễ voice-to-voice. RTF của batch không phải RTF của một stream.
7. **License là hard gate,** áp dụng trước mọi điểm chất lượng.

---

## 4. Kiến trúc tổng thể

```text
Client: mic + AEC (getUserMedia echoCancellation) + capture timestamp
  │  WebRTC Opus (production) / WebSocket PCM16 16 kHz mono (MVP, LAN)
  ▼
Gateway (state theo từng session): decode → resample 16 kHz → ring buffer 20 ms
  ├─► [denoise nhẹ, tùy chọn] → Silero VAD (512 samples/32 ms)
  │        → Smart Turn v3 + fallback timeout → endpoint / barge-in policy
  ├─► audio AEC gốc (không enhance) → ASR streaming state  (Profile B/D)
  └─► turn audio buffer (+ pre-roll 200–300 ms) → ASR turn-final / final-pass
  ▼
transcript revisions → validity gate
   (confidence, hallucination filter, entity checks, speaker lock tùy chọn)
  ▼
turn.commit → LLM bên ngoài (OpenAI-compatible, streaming text, cancel được)
  ▼
clause chunker → Vietnamese spoken-text normalizer + lexicon
  ▼
TTS router/adapter (/v1/audio/speech hoặc SDK) → audio.start(meta) + audio.chunk
  ▼
bounded client queue (AudioWorklet) → playback → audio.played(offset)
        ▲
        └─ barge-in ⇒ generation_id++ ⇒ cancel LLM + TTS, flush queue,
           client.clear, lưu phần đã phát vào history kèm tag [bị ngắt]
```

Sơ đồ này là **Synthesis**, chưa phải một implementation đã test. Nó kết hợp kiến trúc trong [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md) (**Reported**) với các chỉnh sửa trong [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md).

---

## 5. Lựa chọn theo từng tầng

### 5.1 Transport, AEC và tiền xử lý

| Lựa chọn | Khi nào dùng | Ghi chú |
|---|---|---|
| **WebRTC** (Opus, AEC, jitter buffer, chịu packet loss) | Production qua Internet, mobile, barge-in từ xa | Cần AEC khi dùng loa ngoài (**Reported**) |
| **WebSocket PCM16 16 kHz mono**, binary frame 20–32 ms | MVP, LAN, loopback trên edge | Gửi binary, không dùng base64. Client phải có playback queue (AudioWorklet) và biết sample rate của từng backend, ví dụ VieNeu 48 kHz (**Reported**) |
| **Denoise RNNoise / DeepFilterNet 3** | Chỉ nhánh VAD/barge-in | Bằng chứng mâu thuẫn, xem Mục 11 (**Reported**) |

Ba tầng xử lý echo (**Reported**, theo [Barge-in & Echo](../wiki/voice-agent-barge-in-and-echo-handling.md)):

1. **Đơn giản:** tắt mic khi bot nói. Không có barge-in.
2. **Tốt hơn:** AEC của trình duyệt (`echoCancellation`, `noiseSuppression`, `autoGainControl`). VAD vẫn chạy để phát hiện ngắt lời.
3. **Production:** AEC ở tầng WebRTC, cộng với so sánh audio bot vừa phát với tín hiệu mic.

Lỗi thường gặp nhất khi mới làm là **lệch sample rate**: mic 48 kHz, Whisper cần 16 kHz, TTS xuất 22–24–48 kHz. Cộng đồng ghi nhận "9/10 lần" transcript bị rác là do lệch sample rate chứ không phải do model (**Reported**, anecdote). Với telephony 8 kHz: decode đúng rồi mới resample. Upsample không khôi phục được thông tin đã mất (**Synthesis**).

### 5.2 VAD

| | Silero VAD v5/v6 (pick) | Thay thế |
|---|---|---|
| Đặc điểm | ONNX, MIT, ~2 MB, <1 ms/chunk trên CPU, cửa sổ cố định 512 samples ở 16 kHz | TEN VAD: Apache "with conditions", hop 10/16 ms. FireRed Stream-VAD: extra `fireredvad` trong HF s2s |
| Giới hạn | Chỉ phát hiện speech, không hiểu end-of-turn | TEN và Silero có claim mâu thuẫn (Mục 11) |

Tham số khởi điểm (**Reported** từ AI report, cần tune):

- `load_silero_vad(onnx=True)`. Mỗi session một `VADIterator`, gọi `reset_states()` khi hết lượt.
- `threshold=0.5`. Nâng lên 0.6–0.7 khi nền rất ồn.
- `min_silence_duration_ms` 200–300 (khi có Smart Turn phía sau).
- `speech_pad_ms` 100–200, để giữ phụ âm đầu và cuối. Điều này quan trọng với thanh điệu tiếng Việt.
- `min_speech_duration_ms` 250.
- **Ngưỡng thích ứng:** đo VAD prob và RMS trong 2–3 s đầu, trước khi user nói. Nếu xác suất trung bình của nền > 0.3, nâng threshold lên 0.65–0.7 và nâng luôn gate barge-in.

### 5.3 Turn detection (semantic endpointing)

VAD chỉ biết "đang im lặng". Turn detector trả lời câu hỏi "user đã nói xong chưa".

| Model | Tiếng Việt | Kích thước / latency | License |
|---|---|---|---|
| **Pipecat Smart Turn v3.x** (pick) | Có. Accuracy 81.27%, **FP 14.84%**, FN 3.88% (vendor, 1.004 mẫu) | ~8M params, CPU int8 8 MB. 12 ms CPU, ~60–65 ms trên cloud | BSD-2 |
| Namo (community, `dangvansam`) | Có, do tác giả tự đo | ~200 MB (bản VN), 4–36 ms | Plugin LiveKit, chưa có benchmark độc lập |
| LiveKit Turn Detector | **Không** (14 ngôn ngữ) | ~25 ms | License riêng của LiveKit |

Tất cả là **Reported** qua AI report, chưa kiểm chứng từ nguồn gốc.

**Hệ quả thiết kế:**

- FP 14.84% nghĩa là khoảng **1/7 lần** detector báo "hết lượt" trong khi user vẫn đang nói. Vì vậy luôn kèm **fallback timeout 1.2–1.5 s**.
- Nếu tỷ lệ false-interruption tiếng Việt vẫn > 10%, thay sang Namo hoặc một model fine-tune (ngưỡng thay thế, **Reported**).
- Khi không có semantic detector, dùng 500–800 ms im lặng, tune theo tốc độ nói (**Synthesis**, theo blueprint).

**Tham chiếu triển khai cụ thể nhất** là turn tracker của HF s2s (**Reported**, từ README gốc):

- Các trạng thái: `LISTENING → SOFT_ENDED → ANSWERING → CLOSED`.
- Turn được đánh giá là complete: chạy STT/LLM ngay, kèm speculative reopen 800 ms trước khi commit output.
- Turn được đánh giá là incomplete: chờ 600 ms rồi mới chạy. Output bị gate bởi max wait 2 s.
- User nói tiếp: turn mở lại thành một revision mới, công việc chưa commit bị bỏ.

Đây là thiết kế "speculative + revision", khác thiết kế "commit cứng sau timeout" của report. Không nên chép default 64 ms/800 ms/2 s của HF sang cùng bảng tham số với Silero 200–300 ms + 1.2–1.5 s, vì hai triết lý control khác nhau (**Synthesis**).

### 5.4 ASR tiếng Việt

#### 5.4.1 Ba nghĩa khác nhau của "realtime"

Theo [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md) (**Synthesis**):

1. **Native/stateful streaming:** audio vào liên tục, giữ encoder/decoder cache. Ví dụ: Nemotron 3.5.
2. **Buffered/policy streaming:** nhận audio liên tục nhưng chờ đủ context và stable prefix rồi mới commit. Ví dụ: Qwen3-ASR (paper dùng chunk 2 s), hoặc Whisper bọc bởi WhisperLiveKit. Bọc model bằng WebSocket/SSE không biến nó thành causal encoder.
3. **Turn-final:** nhận cả câu sau endpoint rồi decode nhanh. Ví dụ: Whisper, PhoWhisper, ChunkFormer large, Cohere.

RTF < 1 chỉ có nghĩa là theo kịp luồng audio, chưa đủ để có văn bản dùng được sớm. Độ trễ ra văn bản dùng được gồm cả chunk accumulation, lookahead, compute, scheduling, transport và commit policy.

#### 5.4.2 Shortlist

Các con số là **Reported**. Vai trò là **Synthesis**.

| Candidate | Kiểu | Bằng chứng tiếng Việt | Runtime | License |
|---|---|---|---|---|
| **Nemotron 3.5** 600M | Native cache-aware RNNT, chunk 80–1120 ms | FLEURS vi-VN WER (LangID): 13.41 / 12.87 / 12.29 / 11.78 / 11.18 tại 80 / 160 / 320 / 560 / 1120 ms | NeMo script; [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md) Q8 GGUF (HTTP/WS/C SDK); Transformers ≥5.13 | OpenMDW-1.1 (card ghi commercial-ready) |
| **Qwen3-ASR** 1.7B / 0.6B | Buffered; mạnh ở turn-final | Offline FLEURS-vi 5.55 / 8.52; MLC-SLM-vi 14.92 / 17.67 | `qwen-asr` + vLLM; WLK windowed | Apache-2.0 |
| **Whisper large-v3-turbo** 809M | Turn-final (live captions cần WLK) | Chưa có điểm vi đo cùng điều kiện cho turbo. Whisper large-v3: 16.44% WER trung bình trên 3 tập vi (VietASR, qua report) | [Faster-Whisper](../wiki/faster-whisper.md) CT2 fp16/`int8_float16` | MIT |
| [PhoWhisper](../wiki/phowhisper.md) medium/large | Turn-final | large: VIVOS 4.67, CMV 8.14 | Convert sang CT2, cần test parity | BSD-3 |
| [ChunkFormer](../wiki/chunkformer-vietnamese.md) RNNT large 113M | Final-pass | VIVOS 2.49, CMV 5.18, VLSP2020 T1/T2 12.75/20.47 | ONNX CPU/GPU | CC-BY-4.0 (bản CTC 110M là NC) |
| Fun-ASR-MLT 800M / Cohere Transcribe 2B | Challenger turn-final | Có vi trong language list, chưa có điểm | FunASR; Transformers/vLLM | Apache-2.0 |
| [ZipFormer 30M](../wiki/zipformer-30m-vietnamese.md) | CPU, nghiên cứu | VLSP2020 T1 12.29 | sherpa-onnx | **CC-BY-NC-ND**, loại khỏi dùng thương mại |

**Bẫy khi so sánh:**

- Đừng đặt Qwen 5.55 lên trước Nemotron 12.29. Hai con số khác giao thức (offline so với streaming, có LangID) và khác chunk.
- Đừng so VIVOS với FLEURS. Hai tập khác nhau, normalizer cũng khác.
- TTFT 92 ms của Qwen 0.6B đo ở concurrency 1, với input ~2 phút có sẵn. Ở concurrency 128, TTFT là 3210 ms (P95 6195 ms). Không con số nào trong đó là độ trễ từ mic.
- Nemotron phải đặt `vi-VN` tường minh, vì pipeline Transformers mặc định là `en-US`.
- Tên "0.6B/1.7B" của Qwen chưa tính hết encoder, projector và cache.

**Loại khỏi shortlist tiếng Việt** vì language list không có vi: Parakeet (25 ngôn ngữ châu Âu) và các bản phái sinh, Canary, Voxtral, Audio8, SenseVoiceSmall, GLM-ASR, Hojo, ARK, VibeVoice Streaming, Granite TurboCTC, Distil-Whisper (chỉ English) (**Reported**). Hệ quả thực tế: **default Parakeet TDT của HF s2s và RealtimeSTT không dùng được cho tiếng Việt**. Phải đổi backend.

#### 5.4.3 Ba mẫu ghép ASR

| Mẫu | Luồng | Ưu | Nhược |
|---|---|---|---|
| **1. Single-pass turn-final** | VAD/turn cắt lượt → Whisper turbo / Qwen3-ASR / PhoWhisper | Đơn giản nhất | Latency = endpoint + decode cả câu. Không có partial cho caption hay speculative LLM |
| **2. Single-pass native streaming** | Nemotron 160–320 ms | Partial sớm, cache được tái sử dụng, hợp nhiều phiên | FLEURS thấp hơn Qwen offline |
| **3. Two-pass selective** | Nemotron cho partial/UI → cuối lượt chạy Qwen3-ASR 1.7B hoặc ChunkFormer RNNT cho final | Kết hợp partial sớm với final chính xác hơn | Tốn compute. Phải reconcile các revision. Không được hành động trên partial chưa commit |

Model final-pass **không phải ground truth**. Khi có mơ hồ ở số, tên riêng hay phủ định, hãy hỏi lại user thay vì lấy đa số phiếu.

#### 5.4.4 Cấu hình bắt buộc khi dùng faster-whisper

Theo [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md) (**Reported**).

**Tham số decode:**

```text
language="vi"                       # auto-detect trên clip ngắn, ồn dễ sai
beam_size=1–3                       # 3 tốt hơn nhưng chậm hơn ~30–50%
condition_on_previous_text=False
temperature=0.0
vad_filter=True, min_silence_duration_ms=500   # lớp lọc thứ hai
no_speech_threshold=0.6, log_prob_threshold=-1.0, compression_ratio_threshold=2.4
hotwords / initial_prompt ngắn cho tên riêng
# KHÔNG đưa câu kiểu "cảm ơn đã xem" vào prompt
```

**Lọc sau decode:**

- Bỏ segment có `no_speech_prob > 0.6` và `avg_logprob < -1.0`.
- Bỏ cả turn nếu `compression_ratio > 2.4`, hoặc nếu turn có dưới 2 từ trong khi VAD < 400 ms.
- Regex blacklist: `subscribe`, `đăng k[ýí] (cho )?kênh`, `cảm ơn (các bạn )?đã (xem|theo dõi)`, `để không bỏ lỡ những video`, `La La School`, `Ghiền Mì Gõ`, và câu bị lặp nguyên văn 3 lần.
- Materialize generator (`list(segs)`) trong worker thread (`asyncio.to_thread`). Nếu lặp lazy generator ngay trên event loop, cả pipeline bị block. Pipecat từng gặp đúng lỗi này ở PR #5931.

**Lưu ý (Synthesis):** blacklist chỉ là một tín hiệu, cần kết hợp với bằng chứng âm học. User có thể nói thật chữ "subscribe", hoặc nói lệnh ngắn "không", "dừng". Vì vậy luật "< 2 từ" phải tune trên dữ liệu thật.

**Khi nào thay Whisper (Reported):** WER tiếng Việt trong môi trường ồn > ~15%, hallucination vẫn lọt qua filter, hoặc cần partial.

### 5.5 Cầu text → speech tiếng Việt

Tầng này hay bị xem nhẹ, nhưng nó quyết định trực tiếp chất lượng nghe.

**Giao diện LLM.** Thiết kế không gắn với model LLM cụ thể. Gateway chỉ cần LLM có streaming text, `done`, `error`, `cancel` và correlation theo `generation_id` (**Synthesis**). Prompt hệ thống cho hội thoại nói nên yêu cầu (**Reported**):

- 1–3 câu ngắn.
- Không markdown, emoji, bảng hay URL.
- Hỏi lại khi không chắc mình nghe đúng.
- Tắt thinking mode (`enable_thinking=False`) nếu model có chế độ đó.

Để tham khảo, report đề xuất Qwen3-8B AWQ trên vLLM cho GPU 24 GB và Qwen3-4B 4-bit cho GPU 12 GB. Đây là **Reported** và nằm ngoài phạm vi bài này.

**Chunker** (**Reported**, quy tắc khởi điểm):

- Flush khi gặp `.?!…;:` hoặc xuống dòng.
- Với chunk đầu, cắt ở dấu phẩy khi đã có ≥ ~25 ký tự, để giảm TTFA.
- Gộp các mảnh < 8 ký tự vào câu sau.
- Không flush từng token: prosody gãy, TTS thiếu context, số request bùng nổ. Cũng không chờ đủ cả câu trả lời. Đơn vị tốt thường là một câu, hoặc khoảng 20–60 ký tự.

**Normalizer** (**Reported**, ví dụ). Tách text hiển thị khỏi text để đọc:

| Loại | Ví dụ |
|---|---|
| Tiền | `1.250.000đ` → "một triệu hai trăm năm mươi nghìn đồng" |
| Số điện thoại | Đọc từng chữ số |
| Ngày/giờ | Cần luật theo domain vì có thể mơ hồ |
| %, đơn vị | `km/h`, `%` |
| Viết tắt | `TP.HCM`, `UBND` |
| Code-switch | Giữ tiếng Anh nếu TTS xử lý được (VieNeu xử lý được). Nếu không thì phiên âm |

Ngoài ra cần thêm (**Synthesis**): Unicode NFC, strip markup/URL, giữ dấu câu cho prosody, và bộ regression prompts. Lưu ý: wiki **chưa chọn được thư viện Vietnamese normalizer nào đã kiểm chứng**.

**Lexicon.** VieNeu v3 Turbo được báo đọc `chánh` thành `tránh` (issue #207, chưa reproduce, **Reported/Unverified**). Cần một substitution dictionary cho tên riêng và thuật ngữ domain.

**Hai nghĩa của "streaming TTS"** (**Synthesis**):

- *Audio-output streaming:* nhận text hoàn chỉnh, phát audio theo từng chunk. VieNeu `infer_stream` và VoxCPM2 `generate_streaming` thuộc loại này.
- *Incremental text-input (bi-streaming):* nhận token dần dần trong khi đang nói. Chưa có bằng chứng ứng viên tiếng Việt nào làm được. CosyVoice bi-streaming và Qwen Dual-Track đều không có vi.

Vì vậy "clause chunker + gọi TTS theo mệnh đề" là cây cầu đề xuất. Đừng gọi đó là native bi-streaming.

### 5.6 TTS tiếng Việt

Capabilities là **Reported**. Thứ tự ưu tiên là **Synthesis** theo độ phù hợp triển khai, **không phải xếp hạng chất lượng nghe**.

| Candidate | Vai trò | Deploy | Streaming/perf (Reported) | License / gate |
|---|---|---|---|---|
| **VieNeu v3 Turbo** | Baseline | SDK `infer_stream`; `apps/openai_speech.py` `POST /v1/audio/speech` (pcm/wav, chunked/SSE); Docker `api-gpu`/`api-cpu` cổng 8000 | RTX 3060: 1 stream TTFA ~115 ms, RTF 0.49; 16 streams median 185 ms (max 339 ms khi bắt đầu đồng loạt), RTF 0.59; 32 streams ~450 ms, RTF 0.93. CPU fp32 260–400 ms; CPU int8 140–195 ms (cần VNNI) | FAQ ghi Apache/commercial, roadmap lại ghi "personal use". **Mâu thuẫn, chưa giải quyết** |
| [VoxCPM2](../wiki/voxcpm2.md) 2B | Challenger GPU về chất lượng/cloning | `generate_streaming`, cần tự viết API adapter | RTF ~0.3 trên RTX 4090 (~0.13 với Nano-vLLM), ~8 GB VRAM. Chưa có TTFA hay MOS vi | Apache-2.0 |
| Supertonic 3 ~99M | Challenger CPU | ONNX SDK | `synthesize` trả full waveform, không phải frame streaming | OpenRAIL-M |
| [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md) | A/B trên CPU | ONNX/PyTorch, `vig2p` | Không có số liệu | Apache (theo capture) |
| [MOSS-TTS Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md) | Challenger GPU streaming | HF / SGLang-Omni | Codec stereo 48 kHz nhưng ví dụ là mono, phải xác nhận số kênh. Không có số liệu | Apache (theo card) |
| Higgs TTS 3 / Fish S2 Pro | Expressive | SGLang-Omni (Higgs có thêm vLLM-Omni) | Số đo trên H100/H200 không chứng minh TTFA cho vi | **Non-commercial** |
| G-OmniVoice / Gwen-TTS | A/B về cloning | `omnivoice` / `qwen-tts` | Full waveform, chưa có streaming | Phải rà lineage NC / quyền dữ liệu TikTok |
| VieNeu v3 Nano / sanoTTS vi | Edge | Nano 48M ONNX 24 kHz; sano 1.46M 22.05 kHz | Nano chỉ trả chunk đã xong; English/code-switch yếu hơn | sanoTTS là GPL-3.0 |

**Ba điều dễ hiểu sai về VieNeu (Synthesis):**

1. Bulk RTF 0.011–0.02 là throughput của batch, **không phải RTF một stream**.
2. 16 TTS streams không có nghĩa là 16 pipeline đồng thời. Tác giả ước 16 streams phục vụ được khoảng 45–80 user đang chat, vì một stream chỉ sống trong lúc bot nói.
3. GPU idle vài giây sẽ hạ clock, request đầu tiên phải trả thêm 100–300 ms. CUDA graph capture mất ~0.5 s cho mỗi batch size. Phải gọi `warm_fused()` khi khởi động.

**Không dùng out-of-box cho tiếng Việt:** Qwen3-TTS chính thức (10 ngôn ngữ, không có vi). Đây là điểm mà [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md) mắc lỗi khi truyền `language="vi"` vào Qwen3-TTS. Danh sách tương tự: CosyVoice2/3, Chatterbox, Pocket, VibeVoice, IndexTTS, GPT-SoVITS và một số model khác (**Reported**).

### 5.7 Orchestration

| Lựa chọn | Phù hợp | Chi phí tích hợp tiếng Việt |
|---|---|---|
| **Pipecat** (BSD-2) | Cascade tùy biến; WebRTC (Daily, SmallWebRTC), WS, telephony | Có sẵn `SileroVADAnalyzer`, `LocalSmartTurnAnalyzerV3`, `WhisperSTTService`, `OpenAILLMService(base_url=...)`. Chỉ cần viết một `TTSService` tùy biến có `run_tts()` gọi VieNeu. Nemotron và Qwen streaming cần adapter riêng |
| **HF speech-to-speech** (Apache-2.0) | Muốn có OpenAI Realtime subset (gồm `response.cancel`, `conversation.item.truncate`) và Smart Turn v3.2 sẵn | Phải đổi default không có vi: `--stt faster-whisper --language vi` hoặc backend Qwen3-ASR; TTS qua OpenAI-compatible `/v1/audio/speech` trỏ tới VieNeu. Nemotron chỉ có qua extra `nemo` với `--stt nemotron-streaming`; **chưa xác nhận hỗ trợ Nemotron 3.5 `vi-VN`** |
| LiveKit Agents (Apache-2.0) | Cần WebRTC SFU / SIP | Turn detector không có vi |
| TEN / FastRTC | Agora RTC / Gradio WebRTC | Không có lợi thế gì cho tiếng Việt |
| Gateway FastAPI/asyncio tự viết | Kiểm soát toàn bộ turn và cancel | Report có reference server (`VADIterator` mỗi session, gate barge-in 400 ms, `{"type":"clear"}`). Phải tự làm metrics và cancellation |

So sánh framework là bằng chứng thứ cấp (AI report). Riêng HF s2s có README gốc. Các plugin hiện hành chưa được kiểm tra.

HF s2s còn có các điểm vận hành đáng học: log mặc định không chứa nội dung (content-free; `--log_transcripts` là opt-in), và log độ trễ STT, LLM, first-TTS-audio theo từng response. Một lưu ý bảo mật: LLM proxy của nó **không có auth hay throttling**. Phải để tắt, hoặc đặt sau một gateway có kiểm soát truy cập.

### 5.8 Deploy tools: chọn đúng tầng

Theo [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md):

| Tầng | Lựa chọn | Ranh giới bằng chứng |
|---|---|---|
| VAD trên CPU | Silero ONNX | Chỉ là detector, không phải orchestrator |
| Nemotron | NeMo reference; NeMo-Speech.cpp (HTTP/WS/C SDK); Transformers ≥5.13 | Con số 27 ms CPU / 2.3 ms RTX 4090 cho mỗi chunk 160 ms là của **model EN**, không phải 3.5/vi |
| Qwen ASR | `qwen-asr`/vLLM; WLK windowed | Toolkit gốc: streaming chỉ qua vLLM, không batch, không timestamps. WLK causal chỉ có English |
| Whisper | Faster-Whisper CT2; WLK hoặc RealtimeSTT nếu cần live | Không để hai owner cùng quyết định segmentation |
| TTS tiếng Việt | VieNeu SDK/API; VoxCPM2 Python adapter | `VIENEU_MAX_STREAMS` mặc định 16 (GPU) / 1 (CPU); vượt ngưỡng → HTTP 429. Mỗi slot đặt trước cộng ~2.5 ms vào mỗi lần gọi codec |
| GPU multi-stage | SGLang-Omni / vLLM-Omni | Chọn theo recipe của model, chưa có bên nào thắng chung |
| Native C++ | audio.cpp (có community port `vieneu_v3_turbo`); transcribe.cpp | Port chưa được kiểm tra parity. GGUF giữa các runtime không thay thế cho nhau được |

**Quy ước đo (Synthesis):** RTF = wall/audio (thấp hơn thì nhanh hơn). RTFx = audio/wall. Faster Qwen3-TTS dùng chữ "RTF" theo nghĩa RTFx. Luôn đọc định nghĩa trước khi so sánh.

---

## 6. Sáu cấu hình ghép model và deploy tool

| Profile | VAD/Turn | ASR + runtime | TTS + runtime | Orchestration | Chọn khi nào / gate |
|---|---|---|---|---|---|
| **A — MVP turn-final** (1 GPU 12–24 GB) | Silero ONNX + Smart Turn CPU + timeout 1.2–1.5 s | Whisper turbo `vi` + Faster-Whisper fp16/`int8_float16` + filter; hoặc Qwen3-ASR 0.6B | VieNeu GPU qua `/v1/audio/speech` | Pipecat + SmallWebRTC, hoặc HF s2s `serve` | Ít adapter nhất. Không có ASR streaming. Cần test schema TTS và cancellation |
| **B — native streaming** | Như A, state per-session trên CPU | Nemotron 3.5 `vi-VN`, chunk 160/320 ms; NeMo hoặc NeMo-Speech.cpp Q8 | VieNeu GPU hoặc ONNX CPU | Pipecat hoặc gateway tự viết; WebRTC | Thử đầu tiên nếu cần partial sớm. Có thể phải viết adapter ASR riêng |
| **C — quality single-pass** | Như A | Qwen3-ASR 0.6B → 1.7B; vLLM hoặc WLK windowed | VieNeu; A/B với VoxCPM2 | Gateway có transcript revision policy | Chấp nhận buffering/rollback. Chưa có số WER streaming cho vi |
| **D — two-pass selective** | Như B | Nemotron partial + Qwen3-ASR 1.7B hoặc ChunkFormer RNNT final | VieNeu GPU server (`VIENEU_MAX_STREAMS` theo tải) | Pipecat/LiveKit + WebRTC; tách GPU theo service; gateway sở hữu commit | Chỉ khi số, tên, phủ định cần kiểm tra lại và B/C chưa đạt |
| **E — CPU/edge/on-prem** | Silero ONNX + Smart Turn int8 | Nemotron Q8 qua NeMo-Speech.cpp CPU (đo lại), hoặc Whisper CT2 INT8 turn-final | VieNeu ONNX fp32 (INT8 chỉ khi có VNNI); A/B với Supertonic 3 / Kokoro vi; Nano cho CPU yếu | Gateway local, WS loopback, model đã pre-stage | Không cam kết realtime trên mọi CPU. Final mặc định của RealtimeSTT là Parakeet, không có vi |
| **F — license-strict thương mại** | Silero (MIT) + Smart Turn (BSD-2) | Qwen3-ASR (Apache), Whisper (MIT), PhoWhisper (BSD-3), ChunkFormer RNNT (CC-BY-4.0); Nemotron (OpenMDW) sau khi legal review | VoxCPM2 (Apache); VieNeu chỉ sau khi giải quyết mâu thuẫn license; MOSS Local | Pipecat, LiveKit, HF s2s | Tránh ZipFormer NC-ND, ChunkFormer CTC NC, OmniVoice NC lineage, Higgs/Fish, Gwen (quyền dữ liệu), sanoTTS GPL (nếu không chấp nhận copyleft), Supertonic OpenRAIL-M |

### 6.1 Cây quyết định gợi ý (Synthesis)

```text
Cần tiếng Việt cả hai chiều?
 └─ Có → cascade (Mục 2)
     │
     ├─ Ràng buộc license thương mại chặt? → áp lớp lọc F lên mọi lựa chọn bên dưới
     │
     ├─ Chỉ có CPU / edge?                       → E
     │
     ├─ Cần caption live hoặc speculative LLM trên partial?
     │    ├─ Có  → B (Nemotron 160–320 ms)
     │    │         └─ Lỗi số/tên/phủ định vẫn cao sau khi tune? → D (thêm final-pass có điều kiện)
     │    └─ Không → A (Whisper turbo vi) để có vòng đo đầu tiên
     │               └─ WER noisy > ~15% hoặc hallucination lọt filter? → C (Qwen3-ASR 0.6B→1.7B)
     │
     └─ TTS: VieNeu baseline → A/B VoxCPM2 (GPU, cloning) / Supertonic 3, Kokoro vi (CPU)
```

**Nguyên tắc (Synthesis):**

- Đừng triển khai D ngay từ đầu. Two-pass có thể chỉ bật cho các critical span.
- Nếu output phụ thuộc vào bản sửa của final-pass, đừng phát âm thanh hay tạo side effect trước khi commit.
- Nếu đã chạy speculation trên partial, hãy discard/cancel khi revision thay đổi.

---

## 7. Hợp đồng điều khiển (control contracts)

### 7.1 Audio ingress

Các điểm sau là **Synthesis** dựa trên Silero, report và HF s2s.

- Frame transport 20 ms được reblock thành 512 samples (32 ms) cho Silero (256 samples ở 8 kHz). Không bắt VAD, ASR và TTS dùng chung một chunk length.
- Audio chuẩn của gateway cho ASR: 16 kHz mono. Output giữ sample rate gốc tới tận playback adapter.
- Pre-roll 200–300 ms để không mất âm tiết đầu. Đây là thiết kế khởi điểm, chưa phải cutoff đã đo.
- Mỗi session có state VAD/ASR riêng, không bao giờ dùng chung cache giữa các user.
- Packet thiếu hoặc có gap thì cần policy rõ ràng, không nối lệch timeline.

### 7.2 Event schema đề xuất

Đây là **Synthesis**, không phải schema của vendor nào.

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
client.clear(generation_id)        # ≈ {"type":"clear"} / audio_cancel
```

Các quy tắc đi kèm:

- `asr.partial` chỉ dùng cho caption và speculation. `stable_prefix` không phải confidence.
- Final-pass chạy lại trên turn audio đã giữ. Kết quả thay thế một revision và chỉ commit một lần. Không đổ full transcript vào luồng partial, vì sẽ bị trùng lặp.
- Confidence của các ASR khác nhau không được calibrate cùng thang. Nếu thiếu confidence thì để "unknown".
- Khi session đóng: giải phóng cache ASR, cancel inference, flush queue, bỏ các callback đến trễ.

### 7.3 Barge-in và cancellation

Trình tự (**Reported**, gộp từ hai report):

1. Mic luôn mở, có AEC. VAD tiếp tục chấm điểm trong lúc bot nói.
2. Khi phát hiện user nói đủ lâu: `generation_id++`.
3. Cancel LLM stream. Cancel request TTS (HTTP/WS). Xóa các câu đang xếp hàng.
4. Gửi `{"type":"clear"}` / `audio_cancel` để client flush buffer AudioWorklet.
5. Trong history, chỉ lưu **phần đã thực sự phát**, kèm tag `[bị ngắt]`.
6. Client bỏ mọi chunk thuộc generation cũ.

Gating chống ngắt nhầm (**Reported**):

| Cơ chế | Giá trị khởi điểm |
|---|---|
| Duration gate (môi trường sạch) | 100–200 ms speech liên tục (ưu tiên độ nhạy) |
| Duration gate (môi trường ồn) | threshold 0.7 và ≥300–500 ms (reference server dùng 400 ms) |
| Speaker lock | Cosine của embedding ECAPA/CAM++ so với embedding user (lấy từ lượt đầu, cập nhật dần); bỏ nếu < ~0.5–0.6, cần calibrate |
| Quick ASR (tùy chọn) | ≥2 từ và không trùng câu bot đang phát |

Lưu ý (**Synthesis**):

- Speaker lock **không phải là xác thực**.
- Đừng mặc định coi mọi "ừ/vâng/ok" là backchannel để bỏ qua. Trong một số domain, đó chính là lời xác nhận.
- Đo cả hai: user-speech → âm thanh bot dừng (nghe được), và thời gian giải phóng compute.
- Nếu một SDK không cancel được từ bên trong, đó là một deployment gate.
- Nếu không có alignment giữa token và audio, chỉ khẳng định được "played offset", không khẳng định được chính xác từ nào đã phát. `conversation.item.truncate` của HF s2s là điểm nối tự nhiên cho việc này.

### 7.4 Phác thảo vòng điều khiển (minh họa, Synthesis)

Đây là pseudo-code để mô tả luồng điều khiển. Nó không bám API của bất kỳ thư viện nào.

```python
class Session:
    generation_id = 0
    turn = TurnTracker()          # LISTENING / SOFT_ENDED / ANSWERING / CLOSED
    bot_speaking = False

    on_audio_frame(frame):
        vad_p = silero.score(reblock_512(denoise_opt(frame)))   # nhánh VAD
        asr_stream.feed(frame)                                    # nhánh ASR: audio AEC gốc
        if bot_speaking and speech_run_ms(vad_p) >= BARGE_MS and speaker_lock_ok():
            interrupt()
        if silence_ms(vad_p) >= STOP_MS:
            if smart_turn.complete(last_8s_audio) or silence_ms >= FALLBACK_MS:
                turn.soft_end()        # có thể chạy ASR/LLM speculative ở đây
        if user_resumed():
            turn.reopen()              # revision mới, discard việc chưa commit

    on_turn_commit(turn_id, revision):
        text = asr.final(turn_audio)                  # hoặc final-pass (Profile D)
        if not validity_gate(text): return ask_back_or_ignore()
        gid = generation_id
        for clause in chunker(llm.stream(history, text, gid)):
            if gid != generation_id: break             # stale
            tts.enqueue(gid, normalize_vi(lexicon(clause)))

    interrupt():
        generation_id += 1
        llm.cancel(); tts.cancel(); tts_queue.clear()
        client.send({"type": "clear"})
        history.append(played_part_only() + " [bị ngắt]")
```

### 7.5 Diarization

Agent một-user thì **không** đặt diarizer vào critical path. Với meeting hoặc nhiều user: ưu tiên track riêng theo participant. Nếu chỉ có audio trộn, thử [Nemotron 3 Diarization](../wiki/nemotron-3-diarization.md) (tối đa 8 speakers, input buffer 0.32/0.64/1.04 s, **Reported**). Chưa có số DER tiếng Việt.

---

## 8. Latency: ngân sách, đo lường và tối ưu

### 8.1 Critical path cần đo

```text
mẫu speech cuối của user
  → endpoint commit
  → final ASR được chấp nhận
  → LLM: mệnh đề có nghĩa đầu tiên
  → TTS: mẫu audio phát được đầu tiên
  → client: mẫu audio nghe được đầu tiên
```

Đo từng cạnh và tổng. Không cộng các tính toán đã chạy chồng lấn.

**Output gate trong thiết kế speculative** (**Synthesis** từ [HF s2s — Endpointing](../wiki/speech-to-speech-pipeline.md#endpointing-and-turn-taking), bổ sung 2026-10-07 sau review PoC). Khi ASR/LLM chạy speculative trong grace trước commit, thời điểm gate mở có thể quyết định latency thay cho tốc độ model:

```text
v2v ≈ (cuối tiếng user → soft-end) + max(output-hold, ASR + LLM tới mệnh đề đầu)
      + TTS tới audio đầu + transport/playback
```

Với default HF s2s, output-hold là 800 ms cho lượt complete và tới 2 s cho lượt incomplete. Nếu TTS chỉ chạy sau commit thì TTS nằm ngoài `max`. Hệ quả:

- Đo riêng output-hold và thời điểm response sẵn sàng trước khi đổi model.
- Streaming ASR không vượt qua được output gate.
- Chunker phải nằm ở consumer của LLM stream. Chia câu sau khi đã nhận cả câu trả lời không lấy lại được thời gian chờ LLM.
- Khi có reopen, cancel hoặc nhiều TTS chunk, join log theo `turn_id`/`revision`/`generation_id`/`chunk_id`, không theo thứ tự lượt.

### 8.2 Ngân sách tham khảo

Đây là ước lượng của report (**Reported**), **không phải target**.

| Stage | Claude report (vi stack) | ChatGPT blueprint |
|---|---|---|
| Network + jitter | 30–80 ms | 50–200 ms |
| VAD silence / end-of-speech | 200–300 ms | 400–600 ms |
| Smart Turn | 10–65 ms | — |
| ASR turn-final | 100–300 ms (turbo, GPU, câu 3–5 s) | 200–700 ms |
| LLM TTFT + chunk đầu | 150–350 ms | 100–500 ms + tách câu 100–400 ms |
| TTS TTFA | 64–300 ms (VieNeu ~115 ms) | 100–500 ms |
| **Voice-to-voice** | **~0.7–1.2 s** | **mục tiêu 1–2 s** (tổng các dải thực ra là 0.95–2.9 s) |

Hai bảng chênh nhau chủ yếu ở cách endpointing: có Smart Turn với 200–300 ms im lặng, hay dùng 400–600 ms im lặng thuần (**Synthesis**). LLM nằm ngoài phạm vi bài này. Vì vậy speech pipeline không thể cam kết tổng ~1 s khi chưa biết endpoint LLM.

### 8.3 Các đòn bẩy tối ưu

Theo report (**Reported**):

- Warm up mọi model và giữ resident trong VRAM. Không load model theo request. Không ghi file WAV tạm ra đĩa.
- Bật prefix cache cho system prompt (vLLM).
- Chạy faster-whisper trong `asyncio.to_thread`.
- **Preemptive ASR + LLM** khi VAD im 200 ms, và cancel nếu user nói tiếp. Cơ chế speculative reopen của HF s2s là phiên bản có kỷ luật của ý tưởng này.
- Clause chunking để TTS bắt đầu sớm. Blueprint gọi đây là tối ưu quan trọng nhất.
- Playback buffer nhỏ để chống giật. Client đóng gói sẵn của HF s2s đệm 196 ms khi dùng TTS OpenAI-compatible. Đánh đổi là bớt giật nhưng chậm bắt đầu hơn.

### 8.4 Monitoring theo từng turn

Các metric (**Reported**): `vad_end→asr_done`, `asr_done→llm_first_token`, `first_sentence→tts_first_byte`, voice-to-voice đo phía client, tỷ lệ transcript bị lọc, tỷ lệ barge-in, tỷ lệ false-interruption.

Gate khởi điểm cho TTS (**Synthesis**, SLO đề xuất): TTFA P95 ~250–400 ms và RTF P95 ≤ 0.7 dưới tải thực.

---

## 9. Triển khai, VRAM, scaling và privacy

### 9.1 Topology

Theo **Synthesis** từ phần so sánh deploy tools và report.

- Bắt đầu với Docker Compose. Mỗi model một owner process, đừng để mỗi gateway worker tự load weights.
- Tách environment của ASR, TTS và ONNX để tránh xung đột torch/transformers/CUDA. HF s2s là ví dụ: DeepFilterNet cần `numpy<2`, xung đột với Pocket TTS.
- Danh sách container: `gateway` (public RTC/WS), `asr-service` (private), `final-asr-service` (tùy chọn), `tts-service`, `telemetry`. LLM nằm ngoài, nhưng phải tính contention nếu dùng chung GPU.
- Pin revision và checksum cho runtime, weights, G2P, voicepack, normalizer. Pre-stage offline. Health/readiness chỉ báo ready sau khi warmup xong.
- Có admission cap, bounded queue, backpressure/429, deadline theo session, circuit breaker và cleanup.

### 9.2 VRAM

Các con số là ước lượng của report (**Reported**, chưa đo).

| GPU | Phân bổ |
|---|---|
| 24 GB | Whisper turbo fp16 ~2–3 GB; VieNeu GPU ~2–3 GB (tác giả ghi peak 1.1 GB ở 16 streams); phần còn lại cho LLM + KV cache |
| 12 GB | Whisper turbo `int8_float16`, VieNeu, LLM 4B 4-bit |
| Lựa chọn khác (cộng đồng) | Đặt TTS trên CPU để GPU dành cho STT + LLM (**Reported**, anecdote) |

Ước lượng thô weights = params × bytes/param. Ví dụ 0.6B BF16 ≈ 1.2 GB, 1.7B ≈ 3.4 GB. Con số này chưa gồm encoder (nếu tên model chỉ tính decoder), KV/encoder cache, workspace và số phiên (**Synthesis**).

### 9.3 Scaling

Theo report (**Reported**):

- State VAD theo session chạy trên CPU.
- ASR turn-final qua một worker pool batch (faster-whisper `BatchedInferencePipeline`).
- Continuous batching cho LLM và TTS.
- Khi số phiên tăng thì tách GPU theo service.

Thêm (**Synthesis**): ưu tiên nhịp audio đều (cadence) hơn throughput batch. Tách service theo GPU trước khi nghĩ đến Kubernetes hay disaggregated Omni. Năng lực Nemotron 3.5 trên H100 (~240 streams ở chunk 80 ms, ~2.400 ở 1.12 s, **Reported** theo card) là trần lý thuyết của riêng ASR, không phải năng lực của cả pipeline.

### 9.4 Fallback

Nếu đổi TTS giữa chừng một câu, giọng sẽ thay đổi. Nên retry hoặc chuyển sang mệnh đề mới kèm thông báo trạng thái, thay vì ghép hai giọng (**Synthesis**).

### 9.5 Privacy và bảo mật

Các yêu cầu sau là **Synthesis**.

- TLS và auth ở gateway. Cổng của model service để private.
- Giới hạn thời lượng upload, giới hạn kích thước reference. Không cho client tự trỏ tới URL/path reference.
- Log mặc định chỉ có metadata, không có audio hay transcript.
- Corpus đánh giá phải opt-in, có access control, retention và consent.
- Speaker embedding và reference dùng để clone giọng cũng là dữ liệu nhạy cảm. Không ghi chúng vào operational log.
- Quyền với preset voice không bao gồm quyền với reference do user tự cung cấp (VieNeu FAQ, **Reported**).

---

## 10. Đánh giá và release gates

Đây là **Synthesis** từ các gate ASR, TTS, control và server trong wiki.

1. **Corpus ASR:**
   - Giọng Bắc/Trung/Nam. Tên riêng, số, địa chỉ, phủ định, code-switch.
   - Call 8 kHz so với mic 16 kHz. Far-field.
   - Tiếng ồn quán café, xe máy, TV ở SNR 0/5/10/20 dB, có và không có denoise.
   - Đoạn im lặng và nhạc để đo hallucination.
   - Dùng cùng ground truth và normalizer. Đo WER/CER, độ chính xác chính xác (exact) của các critical span, tỷ lệ partial bị sửa, first partial, first-stable-text, endpoint→final P50/P95.
2. **TTS: 150–300 prompts.**
   - Blind pairwise/MOS/CMOS với 10–20 người nghe là người Việt.
   - Chấm thanh điệu, phát âm, độ tự nhiên, độ nhất quán giọng. Test riêng preset và cloning. Test normalizer, lexicon và ranh giới chunk.
   - ASR round-trip CER chỉ là proxy.
3. **Turn và barge-in:**
   - Các tình huống: pause dài giữa câu, lệnh ngắn "không"/"dừng", backchannel, TV nền, echo của bot, user nói đè, ho, gõ phím.
   - Đo false-cutoff, missed/false interrupt, thời gian tới khi âm thanh dừng, khả năng phục hồi.
   - Ngưỡng thay Smart Turn: false-interruption tiếng Việt > 10%.
4. **Tải:**
   - Warm và cold. Tải đều và nhiều phiên bắt đầu cùng lúc. Concurrency 1/4/8/16.
   - Memory theo session, stall, frame bị rớt, TTS underrun, GPU dùng chung giữa ASR/TTS/LLM.
   - Chỉ tăng concurrency khi vẫn đạt P95 và cadence.
5. **Contract tests:**
   - Sample rate 48k/24k/không rõ. Mono/stereo. dtype. PCM so với WAV/SSE. sequence và revision tăng đơn điệu.
   - Cancel giữa chunk, disconnect/reconnect, timeout, OOM, 429.
   - Đảm bảo không có audio cũ, không có final trùng, không có action trên text chưa commit.
6. **Quyền và bảo mật:**
   - Rà license riêng cho runtime, weights, voicepack và lineage dữ liệu. Consent cho reference.
   - Logs content-free.
   - Các gate thương mại: VieNeu, Fish/Higgs/Omni NC, G-OmniVoice, Gwen, GPL/RAIL.

---

## 11. Mâu thuẫn còn mở

Phần này giữ nguyên các mâu thuẫn trong wiki, không chọn bên nào.

| Chủ đề | Bên A | Bên B |
|---|---|---|
| License VieNeu v3 Turbo | Card FAQ: Apache-2.0, preset voices dùng thương mại được | README §7 Roadmap và report: "on-device, personal use" |
| Cửa sổ kích hoạt barge-in | ~100–200 ms speech (ưu tiên nhạy, bản ChatGPT) | ≥300–500 ms ở threshold 0.7 (chống ồn; 400 ms trong reference server) |
| Enhancement trước ASR | arXiv 2403.06387 (ARN/CrossNet, CHiME-4): giúp ASR | arXiv 2512.17562 và 2603.04710: làm giảm chất lượng ở mọi cấu hình đã thử (Whisper 10 dB: 8.82% → 25.83% semWER). Không có nghiên cứu nào trên tiếng Việt |
| TEN VAD so với Silero | Vendor: TEN chính xác hơn | Benchmark cộng đồng nhỏ: Silero F1 91.9% so với TEN 69.2% |
| Default endpoint | HF s2s: `--min_silence_ms` 64 + speculative reopen 800 ms + Smart Turn max wait 2 s | Report: Silero 200–300 ms + fallback 1.2–1.5 s. Đây là hai triết lý control khác nhau |
| Qwen3-TTS và tiếng Việt | Blueprint dùng `language="vi"` | Card chính thức có 10 ngôn ngữ, không có vi |

---

## 12. Lộ trình triển khai đề xuất

| Phase | Nội dung | Ghi chú |
|---|---|---|
| **1 — MVP** (report ước 1–2 tuần) | Profile A: HF s2s hoặc Pipecat + Whisper turbo `vi` + VieNeu. Bắt đầu half-duplex nếu cần, sau đó thêm streaming TTS, `generation_id`, AEC, full-duplex barge-in | Từ ngày đầu: warmup, normalizer/lexicon, audio contract tường minh, Whisper filter, log theo turn, đo voice-to-voice và WER. Chọn B ngay nếu partial là yêu cầu bắt buộc |
| **2 — Beta** | A/B Nemotron 160/320/560 ms so với Qwen 0.6B/1.7B, mỗi bên dùng đúng policy của mình. TTS: VieNeu so với VoxCPM2; trên CPU: VieNeu so với Supertonic 3/Kokoro. Thêm duration-gated barge-in, speaker lock, denoise chỉ cho nhánh VAD, confidence gating | Mỗi lần chỉ đổi một thành phần |
| **3 — Production** | Thêm D nếu lợi ích về lỗi entity đáng với compute/latency bỏ ra. Tách GPU theo service, P95 observability. Calibrate Smart Turn/Namo. Thêm diarization khi có nhiều user. Chuyển sang audio.cpp/native chỉ sau parity gate | Fine-tune TTS/ASR chỉ khi đã xác định được failure case và có quyền dữ liệu |

---

## 13. Giới hạn của bài viết

- **Không có số đo nào cùng điều kiện** về WER, MOS, TTFA hay voice-to-voice tiếng Việt trên một stack hoàn chỉnh. Tất cả các trang nguồn tổng hợp đều đang ở `status: draft`.
- Các tham số control (Smart Turn vi, barge-in, denoise, Whisper filter, latency/VRAM budget) và bảng so sánh framework phần lớn dựa trên **AI report thứ cấp**. Các nguồn gốc mà report trích dẫn chưa được capture vào `raw/`.
- Event schema, cây quyết định và pseudo-code là **đề xuất thiết kế**, không phải API đã triển khai.
- Không mở `raw/`, không chạy model hay benchmark. Các khẳng định "không có vi" nghĩa là "chưa có trong phạm vi đã compile", không phải bằng chứng là không thể.
- Số liệu về model và runtime có `stale_after` khoảng 2027-10. Cần kiểm tra lại release mới trước khi chốt.

---

## Tài liệu tham chiếu trong wiki

**Synthesis / Answered / Reconciled**

- [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md)
- [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md)
- [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md)
- [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md)
- [Phân nhóm ASR/STT và shortlist realtime](../wiki/realtime-asr-selection.md)
- [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md) — Streaming and latency; Selection guide
- [TTS Model Survey](../wiki/tts-model-survey.md) — Streaming and latency; Selection guide

**Pipeline reports và wiring**

- [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md)
- [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md)
- [Community-Reported STT-LLM-TTS Pipeline Wiring](../wiki/community-stt-llm-tts-pipeline.md)

**Control**

- [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md)
- [Turn Detection Models](../wiki/turn-detection-models.md)
- [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md)
- [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md)
- [Silero VAD](../wiki/silero-vad.md)

**Orchestration và runtime**

- [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md)
- [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md)
- [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md)
- [Faster-Whisper](../wiki/faster-whisper.md)
- [audio.cpp Framework](../wiki/audio-cpp-framework.md)

**Model**

- [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md)
- [Qwen3-ASR family](../wiki/qwen3-asr-family.md)
- [Whisper Large v3 Turbo](../wiki/whisper-large-v3-turbo.md)
- [PhoWhisper](../wiki/phowhisper.md)
- [ChunkFormer Vietnamese](../wiki/chunkformer-vietnamese.md)
- [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md)
- [VoxCPM2](../wiki/voxcpm2.md)
- [MOSS-TTS Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md)
- [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md)
- [Nemotron 3 Diarization](../wiki/nemotron-3-diarization.md)

**End-to-end (đối chiếu)**

- [PersonaPlex 7B v1](../wiki/personaplex-7b-v1.md)
- [NVIDIA NemotronLabs VoiceChat 11B](../wiki/nvidia-nemotronlabs-voicechat-11b.md)
