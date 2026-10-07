# Spec PoC speech-to-speech tiếng Việt — Phase 1

> **Loại tài liệu:** spec deliverable trong `outputs/`, không phải tri thức canonical.
> **Ngày:** 2026-10-07.
> **Nguồn:** các quyết định đã chốt qua phỏng vấn (Q1–Q30), dựa trên [thiết kế pipeline](thiet-ke-pipeline-speech-to-speech-tieng-viet.md), [ASR](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md), [TTS](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md), [HF Speech-to-Speech](../wiki/speech-to-speech-pipeline.md) và [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md).
> **Nhãn bằng chứng:** **Reported** = nguồn tự công bố, chưa kiểm chứng; **Synthesis** = suy luận/đề xuất của spec; **TBD** = phải xác minh khi triển khai. Chưa có thành phần nào được chạy thử.

---

## 1. Mục tiêu

PoC nghiên cứu nội bộ, không gắn sản phẩm. Phase 1 dựng **một vòng hội thoại tiếng Việt full-duplex chạy được và đo được**, để trả lời:

| # | Câu hỏi | Cách trả lời ở Phase 1 |
|---|---|---|
| G1 | Latency voice-to-voice thực tế là bao nhiêu? | Đo P50/P95 phía client + latency từng stage từ log server |
| G2 | ASR tiếng Việt có dùng được không, lỗi entity (số, tên, phủ định) ra sao? | **Định tính**: nghe/đọc transcript, ghi lỗi. WER định lượng để Phase 2 |
| G3 | TTS tiếng Việt nghe có ổn không (thanh điệu, đọc số, tên)? | **Định tính**: nghe cảm nhận, ghi lỗi |
| G4 | Endpointing và barge-in có tự nhiên không? | Đếm cắt lời sai, ngắt nhầm, ngắt trượt; đo thời gian bot im lặng sau khi bị ngắt |
| G5 | Đổi ASR/TTS ảnh hưởng thế nào tới G1–G4? | A/B 5 run, mỗi lần đổi 1 thành phần |

### Mục tiêu latency (mềm)

- Voice-to-voice (user ngừng nói → nghe tiếng bot, đo phía client): **P50 ≤ 1.5 s, P95 ≤ 2.5 s**.
- Đây là mục tiêu tham chiếu, không phải gate. Report ước 0.7–1.2 s (**Reported**, chưa đo); tổng các dải của blueprint là 0.95–2.9 s.

### Ràng buộc

- **License:** nội bộ/nghiên cứu, được dùng model non-commercial (CC-BY-NC, v.v.). Không dùng artifact PoC cho thương mại.
- **Privacy:** mọi thứ self-host. Không gửi audio hay text ra dịch vụ bên ngoài.
- **Phần cứng speech:** 1 GPU 24 GB (3090/4090/L4 hoặc tương đương).
- **LLM:** endpoint OpenAI-compatible có sẵn trên máy riêng; spec chỉ cần `base_url` + model name.

### Ngoài phạm vi Phase 1

WER/CER bằng corpus có nhãn; partial transcript/caption; Qwen3-ASR buffered streaming; two-pass (Profile D); speaker lock; denoise riêng nhánh VAD; normalizer đầy đủ; telephony 8 kHz; nhiều user đồng thời; tối ưu production.

---

## 2. Kiến trúc

```text
Trình duyệt (getUserMedia: echoCancellation, noiseSuppression, autoGainControl)
  │  WebRTC
  ▼
HF speech-to-speech `serve`  (máy GPU 24 GB)
  ├─ Silero VAD v5 + Smart Turn v3.2 + turn tracker (default)
  ├─ STT backend ──► (A) Qwen3-ASR 0.6B / 1.7B   in-process
  │                └► (B) NeMo-Speech.cpp `serve` Nemotron 3.5  qua /v1/audio/transcriptions
  ├─ LLM backend `chat-completions` ──► LLM endpoint trên máy riêng (LAN)
  └─ TTS backend ──► (1) VieNeu v3 Turbo  qua /v1/audio/speech (Docker api-gpu)
                   ├► (2) G-OmniVoice     qua handler `omnivoice` có sẵn
                   └► (3) Gwen-TTS        qua server /v1/audio/speech tự bọc
  ▲
  └─ barge-in: cơ chế sẵn có của HF s2s (`response.cancel`, `conversation.item.truncate`)
```

**Nguyên tắc (Synthesis):**

- Một owner cho quyết định turn: turn tracker của HF s2s. ASR/TTS service chỉ cung cấp tín hiệu.
- Mỗi run chỉ nạp **1 ASR + 1 TTS** trên GPU; warmup xong mới đo.
- Mỗi model service có process riêng và environment riêng (tránh xung đột torch/CUDA/numpy).
- Log mặc định content-free. Chỉ bật `--log_transcripts` cho phiên test có chủ đích, và không đưa log có nội dung ra ngoài máy.

---

## 3. Thành phần và cấu hình

Cờ CLI dưới đây chỉ lấy từ README đã compile vào wiki. Các tên cờ không có trong wiki được đánh dấu **TBD**: xác minh bằng `speech-to-speech serve -h` (đặt selector trước `-h` để xem cờ của backend đó).

### 3.1 Orchestration — HF speech-to-speech

| Mục | Giá trị | Ghi chú |
|---|---|---|
| Lệnh | `speech-to-speech serve --host 0.0.0.0 ...` | Default bind `127.0.0.1` (**Reported**) |
| Extras | `pip install speech-to-speech[omnivoice]` (+ extra Qwen3-ASR nếu có, **TBD**) | Không cài DeepFilterNet ở Phase 1 |
| Turn/VAD | Giữ default: `--thresh 0.6`, `--min_silence_ms 64`, `--speculative_reopen_ms 800`, Smart Turn v3.2 bật, `--smart_turn_incomplete_delay_ms 600`, `--smart_turn_max_wait_ms 2000`, `--smart_turn_threshold 0.5` | Không trộn với bộ 200–300 ms + 1.2–1.5 s của report. Tune ở Phase 2 dựa trên log |
| Ngôn ngữ | Pin `vi` qua session (`session.audio.input.transcription.language`) và cờ ngôn ngữ của backend STT (**TBD**) | Không để auto-detect |
| Client | Browser demo của HF s2s qua WebRTC | Truy cập từ máy khác trong LAN cần HTTPS hoặc localhost để trình duyệt cho dùng mic (**Synthesis**, TBD) |
| Smart Turn tiếng Việt | Vendor báo accuracy 81.27%, FP 14.84% (**Reported**, qua AI report) | Kỳ vọng thỉnh thoảng bị cắt lời; ghi vào log quan sát |

### 3.2 LLM

| Mục | Giá trị |
|---|---|
| Backend | `--llm_backend chat-completions` |
| Endpoint | `--responses_api_base_url http://<llm-host>:<port>/v1`, `--model_name <tên model trên endpoint>` |
| Thinking | Tắt (`--responses_api_reasoning_effort none` hoặc `chat_template_kwargs.enable_thinking=false`, tùy server) |
| LLM proxy | Không bật `--enable_llm_proxy` (không có auth/throttling, **Reported**) |
| Yêu cầu endpoint | Streaming text; cancel được khi client đóng stream (**TBD**: kiểm tra trên endpoint hiện có) |

**System prompt (bản khởi điểm, Synthesis):**

```text
Bạn là trợ lý giọng nói tiếng Việt. Câu trả lời sẽ được đọc thành tiếng.
- Trả lời 1–3 câu ngắn, văn nói tự nhiên.
- Không dùng markdown, emoji, bảng, danh sách, URL hay ký hiệu đặc biệt.
- Viết số, tiền, ngày, giờ, phần trăm, đơn vị bằng chữ tiếng Việt
  (ví dụ: "một triệu hai trăm nghìn đồng", "mười bốn giờ ba mươi").
- Viết đầy đủ các từ viết tắt (ví dụ: "Thành phố Hồ Chí Minh").
- Nếu không chắc đã nghe đúng, hỏi lại ngắn gọn.
```

### 3.3 ASR

| ID | Model | Cách nối | Cấu hình | Ghi chú |
|---|---|---|---|---|
| **ASR-Q06** (baseline) | Qwen3-ASR 0.6B | Backend Qwen3-ASR có sẵn của HF s2s | Turn-final, ép ngôn ngữ vi (cờ **TBD**) | FLEURS-vi offline 8.52 WER (**Reported**) |
| ASR-Q17 | Qwen3-ASR 1.7B | Như trên | Như trên | FLEURS-vi offline 5.55 (**Reported**). Theo dõi VRAM khi chung với TTS |
| ASR-NEM | Nemotron 3.5 ASR Streaming 0.6B | `nemo-speech serve --asr-model nemotron-3.5` → HF s2s STT backend OpenAI-compatible `/v1/audio/transcriptions` | Turn-final qua HTTP; ngôn ngữ `vi-VN` (**TBD**, xem R1) | FLEURS-vi 12.29 @320 ms streaming (**Reported**), không so trực tiếp với Qwen |

Lưu ý:

- Ở Phase 1 cả 3 ASR đều chạy **turn-final** (sau khi turn tracker cắt lượt). So sánh Nemotron với Qwen vì vậy chỉ phản ánh chất lượng nhận dạng và thời gian decode, **không phản ánh lợi thế streaming** của Nemotron.
- Không đọc các con số WER ở bảng trên như xếp hạng: khác giao thức, khác chế độ.

### 3.4 TTS

| ID | Model | Cách nối | Output (Reported) | Ghi chú |
|---|---|---|---|---|
| **TTS-VIE** (baseline) | VieNeu v3 Turbo | Docker profile `api-gpu`, `POST /v1/audio/speech` (pcm), HF s2s TTS backend OpenAI-compatible (cờ **TBD**) | PCM `s16le` 48 kHz, frame-level streaming; TTFA ~115 ms trên RTX 3060 | `VIENEU_MAX_STREAMS` đặt nhỏ (1–2) cho PoC 1 user; gọi `warm_fused()`/câu mẫu khi khởi động; temperature ~0.8 |
| TTS-GOV | G-OmniVoice | Handler `omnivoice`: `--tts omnivoice --omnivoice_device cuda --omnivoice_ref_audio <ref.wav> --omnivoice_ref_text "<transcript>"` + đường dẫn checkpoint G-OmniVoice (**TBD**, xem R3) | 24 kHz float → 16 kHz int16; **chờ hết câu** mới phát | Weights base OmniVoice là CC-BY-NC: chấp nhận được vì PoC nội bộ |
| TTS-GWN | Gwen-TTS 0.6B | Server mini tự viết bọc `generate_voice_clone` → `POST /v1/audio/speech` | Full waveform (sample rate **TBD**) | Lineage dữ liệu TikTok chưa rõ; chỉ dùng nội bộ |

**Giọng:**

- Preset: VieNeu dùng 1 giọng Bắc và 1 giọng Nam (lấy tên từ `list_preset_voices()`, pin phiên bản SDK).
- Clone: **1 reference có consent** (khuyến nghị 5–15 s, sạch, kèm transcript chính xác), dùng chung cho VieNeu, G-OmniVoice và Gwen để so sánh cùng giọng. Lưu file reference và consent ngoài repo nếu là dữ liệu cá nhân; không ghi đường dẫn hay embedding vào log.

**Server Gwen tự bọc — hợp đồng tối thiểu (Synthesis):**

```text
POST /v1/audio/speech
  body: { "model": "gwen-tts", "input": <spoken_text>, "voice": <voice_id>, "response_format": "pcm" | "wav" }
  response: audio, header khai báo sample rate / channels / dtype
GET  /health   -> ready chỉ sau khi warmup xong
```

Kiểm tra xem HF s2s client OpenAI-compatible gửi những trường nào và nhận định dạng gì (**TBD**), rồi làm server khớp đúng; dùng cùng hợp đồng cho G-OmniVoice nếu R3 thất bại.

### 3.5 Lớp text → speech (rule tối thiểu)

Chạy trên output LLM trước khi gửi TTS. Nếu HF s2s không có hook tiền xử lý TTS, đặt lớp này **trong các server `/v1/audio/speech`** (VieNeu cần một proxy mỏng) (**Synthesis**, TBD).

1. Unicode NFC.
2. Strip markdown, emoji, URL; giữ dấu câu.
3. Từ điển viết tắt nhỏ: `TP.HCM`, `TP`, `UBND`, `km/h`, `%`, `đ`/`VND`.
4. Lexicon thay thế cho tên riêng/thuật ngữ đọc sai, bổ sung dần khi nghe thấy lỗi (bao gồm case `chánh`/`tránh` đã báo cho VieNeu, **Reported/Unverified**).
5. Số còn sót (LLM không theo prompt): Phase 1 chỉ **log lại**, chưa tự động đọc thành chữ.

### 3.6 Barge-in

- Dùng cơ chế sẵn có của HF s2s; AEC từ trình duyệt.
- Không có speaker lock, không có denoise nhánh VAD ở Phase 1.
- Ghi lại mọi lần ngắt nhầm (bot tự ngắt vì tiếng của chính nó, TV, ho, gõ phím) để làm căn cứ cho patch Phase 2.

---

## 4. Ma trận A/B

Baseline **Qwen3-ASR 0.6B + VieNeu v3 Turbo**; mỗi run đổi đúng 1 thành phần.

| Run | ASR | TTS | Giọng | Mục đích |
|---|---|---|---|---|
| R0 | ASR-Q06 | TTS-VIE | Preset | Baseline |
| R1 | ASR-Q17 | TTS-VIE | Preset | Cái giá/lợi của ASR lớn hơn |
| R2 | ASR-NEM | TTS-VIE | Preset | Nemotron turn-final qua HTTP |
| R3 | ASR-Q06 | TTS-VIE | Clone (ref chung) | Mốc so sánh clone |
| R4 | ASR-Q06 | TTS-GOV | Clone (ref chung) | G-OmniVoice so với R3 |
| R5 | ASR-Q06 | TTS-GWN | Clone (ref chung) | Gwen so với R3 |

R3 được thêm so với 5 run ban đầu để R4/R5 so cùng giọng clone thay vì so với preset (**Synthesis**). Nếu VieNeu không clone được qua API, so R4/R5 với R0 và ghi rõ là khác giọng.

**Quy trình mỗi run:**

1. Khởi động đúng 1 ASR + 1 TTS; ghi lại version/commit/checksum của model và runtime.
2. Warmup: 3 lượt hội thoại bỏ đi, không tính.
3. Chạy kịch bản hội thoại (mục 5.2) ở 4 điều kiện âm thanh (mục 5.1).
4. Ghi peak VRAM của máy GPU.
5. Lưu log server + bản ghi audio + phiếu quan sát.

---

## 5. Giao thức đo

### 5.1 Điều kiện âm thanh

| Mã | Đầu ra | Môi trường |
|---|---|---|
| C1 | Tai nghe | Phòng yên tĩnh |
| C2 | Loa ngoài laptop | Phòng yên tĩnh |
| C3 | Tai nghe | Nhiễu nền (TV/nhạc) |
| C4 | Loa ngoài laptop | Nhiễu nền (TV/nhạc) |

C2/C4 là nơi lộ lỗi AEC và barge-in. Giữ cùng thiết bị, âm lượng và vị trí nguồn nhiễu cho mọi run.

### 5.2 Kịch bản hội thoại (~20 lượt/điều kiện)

Cùng một kịch bản cho mọi run, gồm:

- Câu hỏi thường (5–7 lượt).
- Entity: số tiền, số điện thoại, ngày giờ, tên người/địa danh, code-switch Việt–Anh (5 lượt).
- Phủ định và lệnh ngắn: "không", "dừng lại", "đừng hủy" (3 lượt).
- Ngập ngừng giữa câu, nghỉ dài 1–2 s giữa ý (2 lượt) → kiểm tra cắt lời sớm.
- Ngắt lời bot giữa câu trả lời (3 lượt) → kiểm tra barge-in.
- Câu yêu cầu bot đọc số/tiền/ngày (2 lượt) → kiểm tra prompt + normalizer.

### 5.3 Metric

| Nhóm | Metric | Nguồn |
|---|---|---|
| Latency | Voice-to-voice P50/P95 | Ghi âm stereo: kênh 1 mic user, kênh 2 loa/tai nghe (hoặc loopback); đo khoảng từ cuối tiếng user tới đầu tiếng bot (**Synthesis**) |
| Latency | STT, LLM, first-TTS-audio, speech-to-audio theo từng response | Log mặc định của HF s2s (**Reported**) |
| Endpointing | Số lần cắt lời sớm; số lần chờ quá lâu (> ~2 s) | Phiếu quan sát + log turn (reopen/revision) |
| Barge-in | Ngắt đúng / ngắt trượt / ngắt nhầm; thời gian từ lúc user bắt đầu nói tới lúc bot im | Phiếu quan sát + bản ghi audio |
| ASR (định tính) | Số lỗi entity (số, tên, phủ định) trên các lượt entity; transcript rác/hallucination | Đối chiếu kịch bản với transcript (bật `--log_transcripts` cho phiên test) |
| TTS (định tính) | Lỗi thanh điệu, đọc sai số/tên, ngắt nghỉ lạ, giật/underrun; điểm cảm nhận 1–5 | Phiếu nghe |
| Tài nguyên | Peak VRAM, thời gian warmup | `nvidia-smi` |

Các số TTFA/RTF/TTFT của vendor **không** được cộng thay cho đo thực (**Synthesis**).

### 5.4 Phiếu quan sát (mỗi lượt)

```text
run | điều kiện | lượt | loại lượt | v2v_ms | cắt lời sớm? | barge-in kết quả | lỗi ASR | lỗi TTS | ghi chú
```

---

## 6. Rủi ro và việc phải xác minh trước (Day 0)

| # | Rủi ro / TBD | Kiểm tra | Phương án nếu thất bại |
|---|---|---|---|
| R1 | NeMo-Speech.cpp có cho truyền `vi-VN` qua `/v1/audio/transcriptions` không (tài liệu HTTP API chưa được capture) | Gọi thử 1 file tiếng Việt, xem có ra tiếng Việt không, có prompt `en-US` mặc định không | Chạy Nemotron qua NeMo Python script với `target_lang=vi-VN` bọc HTTP; hoặc tạm bỏ R2 |
| R2 | Cờ chọn Qwen3-ASR, ép ngôn ngữ, và backend TTS OpenAI-compatible của HF s2s | `serve -h` với từng selector | Theo đúng tên cờ thực tế; cập nhật spec |
| R3 | Handler `omnivoice` có nạp được checkpoint G-OmniVoice không | Trỏ model path tới G-OmniVoice, sinh 1 câu | Bọc G-OmniVoice bằng server `/v1/audio/speech` như Gwen |
| R4 | HF s2s client OpenAI-compatible có xử lý đúng sample rate 48 kHz (VieNeu) và PCM/WAV không | Phát 1 câu, kiểm tra cao độ/tốc độ | Proxy resample/đổi định dạng |
| R5 | VRAM: Qwen 1.7B + G-OmniVoice/Gwen + VieNeu trên 24 GB | Đo peak mỗi run | Giữ 1 ASR + 1 TTS; giảm precision |
| R6 | LLM endpoint có streaming và hủy được khi bị ngắt | Ngắt giữa câu, xem LLM server có dừng sinh | Ghi nhận; barge-in vẫn dừng phát âm thanh nhưng lãng phí compute |
| R7 | Hook tiền xử lý text trước TTS trong HF s2s | Đọc code/handler | Đặt rule tối thiểu trong proxy/server TTS |
| R8 | Trình duyệt chặn mic khi không phải HTTPS/localhost | Mở demo từ máy khác | Reverse proxy TLS tự ký, hoặc chạy trình duyệt trên chính máy GPU |
| R9 | Mâu thuẫn tham số endpoint (HF s2s default so với report) | — | Giữ default HF s2s ở Phase 1 (đã quyết) |

---

## 7. Checklist Phase 1

- [ ] Day 0: xác minh R1–R8.
- [ ] Dựng HF s2s `serve` + browser demo WebRTC, nối LLM endpoint, chạy được vòng hội thoại tiếng Việt với R0.
- [ ] Viết rule text→speech tối thiểu + lexicon khởi đầu.
- [ ] Dựng VieNeu Docker `api-gpu`, warmup, `VIENEU_MAX_STREAMS` nhỏ.
- [ ] Dựng NeMo-Speech.cpp `serve` cho Nemotron 3.5.
- [ ] Viết server `/v1/audio/speech` cho Gwen (và G-OmniVoice nếu R3 thất bại).
- [ ] Thu reference clone có consent + transcript.
- [ ] Soạn kịch bản ~20 lượt và phiếu quan sát.
- [ ] Thiết lập ghi âm stereo để đo voice-to-voice.
- [ ] Chạy R0–R5 × C1–C4.
- [ ] Viết báo cáo kết quả Phase 1 vào `outputs/`: bảng latency, quan sát ASR/TTS/barge-in, đề xuất cho Phase 2.

**Tiêu chí xong Phase 1:** đủ R0–R5 ở 4 điều kiện, có bảng P50/P95 voice-to-voice và latency từng stage, có danh sách lỗi định tính được phân loại, và có đề xuất Phase 2 dựa trên số liệu.

---

## 8. Backlog Phase 2 (đã chốt hướng, chưa chi tiết)

- Corpus đánh giá ASR có nhãn (3 miền, entity, nhiễu SNR 0/5/10/20 dB, đoạn im lặng/nhạc) → WER/CER + entity exact-match.
- Handler WebSocket cho Nemotron để có partial; đo lợi ích latency của streaming so với turn-final.
- Qwen3-ASR buffered streaming qua vLLM Realtime (đang experimental trong HF s2s).
- Patch speaker lock (ECAPA/CAM++) và denoise chỉ cho nhánh VAD; A/B chống ngắt nhầm.
- Tune Smart Turn/VAD dựa trên log Phase 1; cân nhắc Namo nếu false-interruption tiếng Việt > 10%.
- Normalizer đầy đủ (tiền, số điện thoại, ngày, đơn vị) + bộ regression prompt TTS; blind listening test.

---

## 9. Bảng quyết định (truy vết)

| Q | Quyết định |
|---|---|
| Q1 | Demo/PoC nghiên cứu |
| Q2 | Spec cho MVP Phase 1 |
| Q3 | Nội bộ/nghiên cứu, cho phép model NC |
| Q4 | 1 GPU 24 GB |
| Q5, Q9, Q23 | LLM trên máy riêng, endpoint OpenAI-compatible có sẵn |
| Q6 | Mọi thứ self-host |
| Q7 | Trình duyệt qua WebRTC |
| Q8 | Đo latency, ASR, TTS, endpointing/barge-in, A/B |
| Q10, Q14, Q22 | Nemotron 3.5 + Qwen3-ASR 0.6B/1.7B; Phase 1 chỉ turn-final |
| Q11 | VieNeu + G-OmniVoice + Gwen |
| Q12, Q17 | Full-duplex đầy đủ là đích; Phase 1 dùng barge-in sẵn có, patch speaker lock/denoise sau |
| Q13 | HF speech-to-speech |
| Q15 | Preset + 1 reference clone có consent dùng chung |
| Q16, Q20 | Phase 1 chỉ đo latency + nghe cảm nhận; WER sang Phase 2 |
| Q18, Q21 | Nemotron qua NeMo-Speech.cpp, `/v1/audio/transcriptions` trước, WS sau |
| Q19 | G-OmniVoice qua handler `omnivoice`, Gwen tự bọc |
| Q24 | Mềm: P50 ≤ 1.5 s, P95 ≤ 2.5 s |
| Q25 | System prompt + rule tối thiểu |
| Q26 | Tai nghe + loa ngoài, yên tĩnh + nhiễu nền |
| Q27 | File này |
| Q28 | Baseline Qwen 0.6B + VieNeu, đổi 1 thành phần/lần |
| Q29 | 1 ASR + 1 TTS mỗi run, warmup trước khi đo |
| Q30 | Default turn/VAD của HF s2s |
