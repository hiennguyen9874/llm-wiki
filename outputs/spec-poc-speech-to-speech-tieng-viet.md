# Spec PoC speech-to-speech tiếng Việt — Phase 1

> **Loại tài liệu:** spec deliverable trong `outputs/`, không phải tri thức canonical.
> **Ngày:** 2026-10-07.
> **Nguồn:** các quyết định đã chốt qua phỏng vấn (Q1–Q30), dựa trên [thiết kế pipeline](thiet-ke-pipeline-speech-to-speech-tieng-viet.md), [ASR](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md), [TTS](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md), [HF Speech-to-Speech](../wiki/speech-to-speech-pipeline.md) và [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md).
> **Nhãn bằng chứng:** **Reported** = nguồn tự công bố, chưa kiểm chứng; **Synthesis** = suy luận/đề xuất của spec; **TBD** = phải xác minh khi triển khai. Chưa có thành phần nào được chạy thử.
> **Cập nhật sau ingest tài liệu con (2026-10-07):** theo [review tài liệu thiếu](review-missing-document.md) và các trang wiki mới ([CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md), [OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md), [Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [Latency Instrumentation](../wiki/speech-to-speech-latency-instrumentation.md), [Browser Demo](../wiki/speech-to-speech-browser-demo.md), [NeMo-Speech.cpp HTTP API](../wiki/nemo-speech-http-api.md), [Server](../wiki/nemo-speech-server.md), [Smart Turn](../wiki/smart-turn.md), [VieNeu API](../wiki/vieneu-tts-openai-speech-api.md), [Qwen3-TTS Base](../wiki/qwen3-tts-12hz-0.6b-base.md)). Nhãn mới **Observed** = thấy trong code/tài liệu đã capture, chưa chạy. Thay đổi: tên cờ s2s đã biết (§3), số Smart Turn vi (§3.1), `truncate` chỉ là no-op (§2, §3.6), `stream_batch_sentences` và `compact_history` (§2.1, §3.2), s2s log có `hold_s` (§5.3), R1–R12 cập nhật trạng thái (§6), Nemotron streaming chưa chắc ghép được (§8). Không đổi quyết định Q1–Q30.
> **Cập nhật sau review (2026-10-07):** theo [review latency](review-ke-hoach-trien-khai-poc-speech-to-speech.md) và [review streaming](review-streaming-ke-hoach-trien-khai-poc-speech-to-speech.md). Thêm phân tích sàn latency do output gate (§1), bảng mức streaming theo tầng (§2.1), metric timeline theo lượt (§5.3), rủi ro R10–R12 (§6), thứ tự ưu tiên Phase 2 (§8). Không đổi quyết định Q1–Q30.

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
- **Sàn do turn tracker (Synthesis từ Reported):** với default Q30, lượt Smart Turn đánh giá complete chỉ commit output sau grace 800 ms tính từ soft-end; lượt đánh giá incomplete bị giữ output tới mốc 2 s ([HF s2s — Endpointing](../wiki/speech-to-speech-pipeline.md#endpointing-and-turn-taking)). Mô hình phân tích, chưa xác minh trên implementation:

  ```text
  v2v ≈ (cuối tiếng user → soft-end) + max(output-hold, ASR + LLM tới mệnh đề đầu [+ TTS nếu TTS chỉ chạy sau commit])
        + TTS tới audio đầu + transport/playback
  ```

  Hệ quả: lượt complete khó xuống dưới ~0.9 s dù model nhanh. P95 ≤ 2.5 s chỉ đạt được khi dưới ~5% lượt đi nhánh incomplete, hoặc gate mở sớm hơn 2 s. Nếu ASR/LLM đã xong trong grace thì đổi model nhanh hơn không cải thiện v2v. Vì vậy Phase 1 phải đo output-hold riêng (§5.3), chưa tune (Q30).

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
  └─ barge-in: cơ chế sẵn có của HF s2s (server VAD → `response.done` `cancelled`/`turn_detected`; hoặc `response.cancel`). `conversation.item.truncate` chỉ được nhận như no-op
```

**Nguyên tắc (Synthesis):**

- **Streaming theo tầng, commit theo lượt:** mỗi tầng dùng loại chunk riêng (audio frame để vận chuyển, mệnh đề để nói, audio chunk để phát). Có thể tính toán speculative trước commit, nhưng chỉ phát audio hoặc gây side effect sau khi turn commit.
- Một owner cho quyết định turn: turn tracker của HF s2s. ASR/TTS service chỉ cung cấp tín hiệu.
- Mỗi run chỉ nạp **1 ASR + 1 TTS** trên GPU; warmup xong mới đo.
- Mỗi model service có process riêng và environment riêng (tránh xung đột torch/CUDA/numpy).
- Log mặc định content-free. Chỉ bật `--log_transcripts` cho phiên test có chủ đích, và không đưa log có nội dung ra ngoài máy.

### 2.1 Mức streaming ở Phase 1

Phase 1 **chưa streaming xuyên suốt**. Tên model có chữ "Streaming" không có nghĩa pipeline dùng streaming.

| Tầng | Phase 1 | Trạng thái |
|---|---|---|
| Audio vào / VAD / turn tracker | Liên tục theo frame | Có sẵn trong HF s2s (**Reported**) |
| STT (cả Qwen và Nemotron) | **Turn-final** sau soft-end | Đã chốt (Q22). Nemotron qua HTTP không dùng được lợi thế streaming. Backend HTTP của s2s upload WAV 16 kHz mono PCM16 cho mỗi final (**Reported**) |
| LLM | Streaming text (`--responses_api_stream`) | Endpoint thật **TBD** (R6) |
| LLM → TTS | `--stream_batch_sentences` mặc định **3** (đặt 1 để stream từng câu) (**Observed** trong argument class). Độ mịn là *câu*, không phải mệnh đề; việc câu đầu tới TTS trước khi LLM xong và cách chia thật là **TBD** (R11) | Phải xác minh ở Day 0 |
| TTS VieNeu | Audio-output streaming: nhận một đoạn text hoàn chỉnh, trả PCM dần (**Reported**). `--tts openai` đọc body incrementally, đổi dần về 16 kHz (**Reported**) | Proxy phải giữ streaming (không gom body). Hủy là best-effort: s2s chỉ đóng HTTP response, không có hủy phía server |
| TTS G-OmniVoice / Gwen | Full waveform theo từng request/câu. Handler `omnivoice` gọi `generate()` blocking; nếu bị ngắt giữa lúc sinh thì kết quả bị bỏ sau khi hàm trả về (**Reported**) | Chia waveform đã sinh xong thành gói nhỏ **không** làm audio đầu tới sớm hơn |
| Playback trình duyệt | Incremental, buffer do demo quản lý | 196 ms chỉ là của client Python. Demo WebSocket mặc định 0 ms (chỉnh trong Settings); WebRTC không có tùy chọn buffer (**Reported**). Buffer thực đo ở M4 |

Chunker theo mệnh đề phải nằm ở **consumer của LLM stream, trước request TTS**, tức là trong s2s. Nếu proxy chỉ nhận cả câu trả lời rồi mới chia, thời gian chờ LLM không lấy lại được (**Synthesis**).

---

## 3. Thành phần và cấu hình

Tên cờ dưới đây lấy từ README và argument class đã compile vào wiki ([CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md), **Observed** trong code đã capture, chưa chạy). Cờ không có trong wiki vẫn đánh dấu **TBD**; xác nhận lại bằng `speech-to-speech serve -h` (đặt selector trước `-h`) vì argument class đã capture không đủ (thiếu `responses_api_language_model_arguments.py`).

### 3.1 Orchestration — HF speech-to-speech

| Mục | Giá trị | Ghi chú |
|---|---|---|
| Lệnh | `speech-to-speech serve --host 0.0.0.0 ...` | Default bind `127.0.0.1` (**Reported**) |
| Extras | `pip install speech-to-speech[omnivoice]`, `[webrtc]` (bắt buộc cho WebRTC, nếu không `/v1/realtime/calls` trả 501). Qwen3-ASR là backend built-in; `[nemo]` chỉ khi dùng `--stt nemotron-streaming` | Không cài DeepFilterNet ở Phase 1 |
| Turn/VAD | Giữ default (đã xác nhận trong argument class, **Observed**): `--thresh 0.6`, `--min_silence_ms 64`, `--min_speech_ms 384`, `--speculative_reopen_ms 800`, Smart Turn v3.2 bật (mặc định tải bản **CPU**), `--smart_turn_incomplete_delay_ms 600`, `--smart_turn_max_wait_ms 2000`, `--smart_turn_threshold 0.5`. Đặt `--enable_live_transcription false` vì Phase 1 không cần partial và với backend HTTP cờ này làm upload lại cả utterance nhiều lần (**Synthesis**, kiểm ở Day 0 bằng stub đếm request) | Không trộn với bộ 200–300 ms + 1.2–1.5 s của report. 64 ms là ngưỡng silence ứng viên, không phải thời điểm bot được nói. Phase 1 đo output-hold và kết quả Smart Turn từng lượt (§5.3); tune ở Phase 2 dựa trên log |
| Ngôn ngữ | Qwen3-ASR: `--qwen3_asr_language vi` (mặc định `auto`, **Observed**). STT HTTP: `--openai_stt_language` (mặc định rỗng). Browser demo không có ô đặt ngôn ngữ STT trong Settings (**Reported**), nên cờ server là chỗ pin chính | Không để auto-detect |
| Client | Browser demo của HF s2s (`uvicorn --app-dir demo server:app --port 7860`, `SPEECH_TO_SPEECH_URL=ws://localhost:8765/v1/realtime`), WebRTC | Mic cần HTTPS hoặc `localhost`; `http://192.168.x.y` không dùng được (**Reported**). WebRTC: chỉ handshake đi qua proxy `/api/calls` của demo, audio đi thẳng browser↔backend (UDP). Mặc định dùng host candidate + STUN của Google; để giữ ràng buộc self-host, đặt `SPEECH_TO_SPEECH_ICE_SERVERS` (backend) và `RTC_ICE_SERVERS` (demo) chỉ trỏ LAN (**Synthesis**, kiểm). Không đặt `SERPER_API_KEY` (tắt web search) và đặt `STARTUP_GREETING` rỗng (nếu không mỗi kết nối sinh một lượt LLM ẩn, làm lệch lượt đầu) |
| Smart Turn tiếng Việt | Benchmark vendor (1.004 mẫu vi, **Reported**): bản CPU mặc định accuracy 79.38%, FPR 8.86%, FNR 11.75%; bản GPU 82.47% / 9.56% / 7.97% ([Smart Turn v3.2](../wiki/smart-turn.md)). Con số 81.27% / 14.84% của AI report không khớp, chưa rõ bản nào | Vi là ngôn ngữ yếu nhất của model. Kỳ vọng thỉnh thoảng bị cắt lời và bỏ sót hết lượt; ghi vào log quan sát. `--smart_turn_model_path` cho phép thử bản GPU (để Phase 2) |

### 3.2 LLM

| Mục | Giá trị |
|---|---|
| Backend | `--llm_backend chat-completions` |
| Endpoint | `--responses_api_base_url http://<llm-host>:<port>/v1`, `--model_name <tên model trên endpoint>` |
| Thinking | Tắt: `--responses_api_reasoning_effort none` (gửi `extra_body.reasoning_effort`); khi không đặt thì s2s dùng `chat_template_kwargs.enable_thinking=false` (`--responses_api_disable_thinking`) (**Observed**). Chọn theo server |
| LLM proxy | Không bật `--enable_llm_proxy` (không có auth/throttling, **Reported**) |
| Chia text → TTS | `--stream_batch_sentences` mặc định 3: gom 3 câu mới gửi TTS. Phase 1 đặt **1** để ra TTS theo từng câu (**Synthesis**; R11 xác nhận hành vi thật) |
| Nén lịch sử | `--compact_history` mặc định bật: khi chat vượt `chat_size=30` (~15 lượt), s2s chạy thêm một lời gọi LLM nền để tóm tắt (**Observed**). Kịch bản ~21 lượt sẽ chạm ngưỡng này, làm lệch tải LLM và `llm-tap`. Tắt hoặc ghi lại sự kiện (cách tắt cờ bool **TBD**) |
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
| **ASR-Q06** (baseline) | Qwen3-ASR 0.6B | `--stt qwen3-asr --qwen3_asr_model_name Qwen/Qwen3-ASR-0.6B-hf` | Turn-final, `--qwen3_asr_language vi` (**Observed**). Default đã là `0.6B-hf` | FLEURS-vi offline 8.52 WER (**Reported**) |
| ASR-Q17 | Qwen3-ASR 1.7B | Như trên với `Qwen/Qwen3-ASR-1.7B-hf` (không phải `Qwen/Qwen3-ASR-1.7B`, bản dành cho vLLM) | Như trên | FLEURS-vi offline 5.55 (**Reported**). Theo dõi VRAM khi chung với TTS |
| ASR-NEM | Nemotron 3.5 ASR Streaming 0.6B | `nemo-speech serve --asr-model nemotron-3.5 --port <p>` → `--stt openai --openai_stt_base_url http://127.0.0.1:<p>/v1 --openai_stt_language vi-VN` (giá trị `vi` hay `vi-VN` **TBD**, xem R1). Server dùng một model đã nạp, field `model` bị bỏ qua (**Reported**) | Turn-final qua HTTP. Phương án dự phòng: `--stt nemotron-streaming` (NeMo Python, auto-detect, không ép được ngôn ngữ) | FLEURS-vi 12.29 @320 ms streaming (**Reported**), không so trực tiếp với Qwen |

Lưu ý:

- Khi khởi động, s2s gửi 1 giây im lặng tới endpoint STT và một câu ngắn tới endpoint TTS để kiểm tra (**Reported**); các service phải sẵn sàng (và chấp nhận im lặng) trước khi bật s2s.
- Ở Phase 1 cả 3 ASR đều chạy **turn-final** (sau khi turn tracker cắt lượt). So sánh Nemotron với Qwen vì vậy chỉ phản ánh chất lượng nhận dạng và thời gian decode, **không phản ánh lợi thế streaming** của Nemotron.
- Không đọc các con số WER ở bảng trên như xếp hạng: khác giao thức, khác chế độ.

### 3.4 TTS

| ID | Model | Cách nối | Output (Reported) | Ghi chú |
|---|---|---|---|---|
| **TTS-VIE** (baseline) | VieNeu v3 Turbo | Docker profile `api-gpu`, `POST /v1/audio/speech`; s2s: `--tts openai --openai_tts_base_url <proxy>/v1 --openai_tts_model vieneu-v3-turbo --openai_tts_voice <preset> --openai_tts_response_format pcm --openai_tts_sample_rate 48000 --openai_tts_stream false` (cờ **Observed**) | PCM `s16le` 48 kHz mono, chunked; TTFA ~115 ms trên RTX 3060 (**Reported**); 429 khi hết slot | `VIENEU_MAX_STREAMS` nhỏ (1–2); slot nhả khi client đóng kết nối (**Reported**); warmup lúc khởi động server (~12 s), chờ `/health` ok; `speed`/`instructions` bị bỏ qua; sampling mặc định 0.8/25/0.95/1.2 |
| TTS-GOV | G-OmniVoice | Handler `omnivoice`: `--tts omnivoice --omnivoice_model_name g-group-ai-lab/g-omnivoice --omnivoice_device cuda --omnivoice_ref_audio <ref.wav> --omnivoice_ref_text "<transcript>" --omnivoice_language vi` (cờ **Observed**; việc handler nạp được checkpoint G-OmniVoice vẫn **TBD**, R3). Mặc định `omnivoice_model_name=k2-fsa/OmniVoice`, `num_steps=32` | 24 kHz float → 16 kHz int16; **chờ hết câu** mới phát; s2s không log `tts_ttfa`/`e2e` cho handler này | Card G-OmniVoice khai Apache-2.0 nhưng weights gốc OmniVoice là CC-BY-NC: mâu thuẫn license chưa giải quyết, chấp nhận được vì PoC nội bộ |
| TTS-GWN | Gwen-TTS 0.6B | Server mini tự viết bọc `generate_voice_clone(..., language="Vietnamese")` → `POST /v1/audio/speech`; s2s dùng cùng cờ `--tts openai` | Full waveform; sample rate lấy từ `sr` model trả về (giá trị **TBD**) | Card Gwen dùng `language="Vietnamese"` trong ví dụ; checkpoint gốc Qwen3-TTS Base không liệt kê tiếng Việt ([Base card](../wiki/qwen3-tts-12hz-0.6b-base.md)), nên smoke test giá trị này. Lineage dữ liệu TikTok chưa rõ; chỉ dùng nội bộ |

**Giọng:**

- Preset: VieNeu dùng 1 giọng Bắc và 1 giọng Nam (lấy tên từ `list_preset_voices()`, pin phiên bản SDK).
- Clone: **1 reference có consent** (khuyến nghị 5–15 s, sạch, kèm transcript chính xác), dùng chung cho VieNeu, G-OmniVoice và Gwen để so sánh cùng giọng. Lưu file reference và consent ngoài repo nếu là dữ liệu cá nhân; không ghi đường dẫn hay embedding vào log. VieNeu: `POST /v1/voices` (multipart `name`, `file` 3–8 s, `denoise`) chỉ giữ giọng trong **bộ nhớ process**, nên phải đăng ký lại sau mỗi lần khởi động/restart container (đưa vào `start_run.sh`); trùng tên preset trả 409 (**Reported**).

**Server Gwen tự bọc — hợp đồng tối thiểu (Synthesis):**

```text
POST /v1/audio/speech
  body: { "model": "gwen-tts", "input": <spoken_text>, "voice": <voice_id>, "response_format": "pcm" | "wav" }
  response: audio, header khai báo sample rate / channels / dtype
GET  /health   -> ready chỉ sau khi warmup xong
```

HF s2s client nhận PCM16 thô theo `--openai_tts_sample_rate` hoặc WAV (`--openai_tts_stream false --openai_tts_response_format wav`) (**Reported**), nên server Gwen có thể trả `pcm` với sample rate khai báo bằng cờ. Vẫn kiểm các trường s2s thực sự gửi (**TBD**, stub Day 0), rồi làm server khớp đúng; dùng cùng hợp đồng cho G-OmniVoice nếu R3 thất bại.

### 3.5 Lớp text → speech (rule tối thiểu)

Chạy trên output LLM trước khi gửi TTS. Nếu HF s2s không có hook tiền xử lý TTS, đặt lớp này **trong các server `/v1/audio/speech`** (VieNeu cần một proxy mỏng) (**Synthesis**, TBD).

1. Unicode NFC.
2. Strip markdown, emoji, URL; giữ dấu câu.
3. Từ điển viết tắt nhỏ: `TP.HCM`, `TP`, `UBND`, `km/h`, `%`, `đ`/`VND`.
4. Lexicon thay thế cho tên riêng/thuật ngữ đọc sai, bổ sung dần khi nghe thấy lỗi (bao gồm case `chánh`/`tránh` đã báo cho VieNeu, **Reported/Unverified**).
5. Số còn sót (LLM không theo prompt): Phase 1 chỉ **log lại**, chưa tự động đọc thành chữ.

### 3.6 Barge-in

- Dùng cơ chế sẵn có của HF s2s; AEC từ trình duyệt (demo gọi `getUserMedia` với `echoCancellation`, `noiseSuppression`, `autoGainControl`, **Reported**). Server VAD ngắt response khi `turn_detection.interrupt_response` (mặc định true) cho phép; `response.done` có `status=cancelled`, `reason=turn_detected` (**Reported**). `conversation.item.truncate` chỉ được nhận như no-op, nên lịch sử LLM không bị cắt theo phần user đã nghe.
- Đường WebRTC gửi mic thô, không qua noise gate của worklet WebSocket (**Reported**).
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
| Latency | STT, LLM, first-TTS-audio, E2E (ước lượng cuối tiếng nói → audio TTS đầu), `vad_decision_s`, `smart_status`, `hold_s` theo từng response | Log INFO của HF s2s và `response.metadata["speech_to_speech.turn_latency"]` (schema v2); panel "Server timings" của demo. Stage chồng lấn, không cộng. `tts_ttfa`/`e2e` chỉ có với TTS `qwen3`/`openai`, **không có với handler `omnivoice`** (**Reported**). E2E không gồm playback, nên v2v phía client vẫn là số chính |
| Latency | **Timeline mỗi lượt** (phía server, cùng clock): soft-end → STT start/done → `llm_first_token` → `first_clause_ready`/`tts_request_start` → `llm_done` → output commit (gate mở) → TTS first byte. Tách được output-hold với compute; kiểm TTS có nhận câu/mệnh đề đầu trước `llm_done` không | `hold_s` của s2s cho trực tiếp thời gian bị gate (không cần suy ra). Còn lại: log `tts-proxy` + `llm-tap` (kế hoạch §5.3); s2s v2 đã bỏ `llm_ttft_s` nên `llm-tap` vẫn cần. Mốc nào không có thì ghi là thiếu (**Synthesis**) |
| Endpointing | Số lần cắt lời sớm; số lần chờ quá lâu (> ~2 s); tỷ lệ lượt Smart Turn đánh giá incomplete; số reopen | Phiếu quan sát + log turn (reopen/revision) |
| Barge-in | Ngắt đúng / ngắt trượt / ngắt nhầm; **user onset → bot im** (nghe được); **cancel → backend hết compute** (LLM/TTS) | Phiếu quan sát + bản ghi audio; log proxy/tap + GPU util |
| ASR (định tính) | Số lỗi entity (số, tên, phủ định) trên các lượt entity; transcript rác/hallucination | Đối chiếu kịch bản với transcript (bật `--log_transcripts` cho phiên test) |
| TTS (định tính) | Lỗi thanh điệu, đọc sai số/tên, ngắt nghỉ lạ, giật/underrun; điểm cảm nhận 1–5 | Phiếu nghe |
| Tài nguyên | Peak VRAM, thời gian warmup | `nvidia-smi` |

Các số TTFA/RTF/TTFT của vendor **không** được cộng thay cho đo thực (**Synthesis**).

Quy tắc phân tích (**Synthesis**):

- Join log theo ID (`response_id`/`item_id` nếu s2s log, `req_id` của proxy/tap). Chỉ dùng thứ tự lượt làm fallback và đối chiếu chéo với số response/reopen, vì reopen, cancel và nhiều TTS chunk làm lệch thứ tự. Audio phía client vẫn là căn cứ cho v2v.
- Báo riêng theo loại lượt: bình thường (complete), incomplete/reopen, barge-in, sau idle. Không chỉ nhìn P95 gộp C1–C4.
- v2v tính tới mệnh đề có nghĩa đầu tiên. Nếu audio đầu chỉ là tiếng đệm ("Vâng…") thì gắn cờ riêng.
- Tách warm liên tục, lượt sau GPU idle (VieNeu được báo +100–300 ms, **Reported**) và cold start (thời gian warmup). Warmup không được che mất hiện tượng người dùng sẽ gặp.

### 5.4 Phiếu quan sát (mỗi lượt)

```text
run | điều kiện | lượt | loại lượt | v2v_ms | cắt lời sớm? | barge-in kết quả | lỗi ASR | lỗi TTS | ghi chú
```

---

## 6. Rủi ro và việc phải xác minh trước (Day 0)

| # | Rủi ro / TBD | Kiểm tra | Phương án nếu thất bại |
|---|---|---|---|
| R1 | Giá trị `language` nào (`vi-VN`, `vi`, bỏ trống/auto) NeMo-Speech.cpp nhận trên `/v1/audio/transcriptions`. Đã biết (**Reported**): có field `language`, nhận WAV 8–96 kHz, `model` bị bỏ qua, xem model đã nạp ở `GET /v1/models`; chưa biết giá trị hợp lệ cho tiếng Việt | Gọi thử 1 file tiếng Việt với từng giá trị, xem có ra tiếng Việt không, có tag `<vi-VN>` không | `--stt nemotron-streaming` (NeMo Python, auto-detect); hoặc bọc NeMo Python `target_lang=vi-VN`; hoặc tạm bỏ R2 |
| R2 | Tên cờ đã suy từ argument class (§3); cần xác nhận với `serve -h` vì capture thiếu một file Responses-API (mặc định `--model_name` mâu thuẫn: base class `Qwen/Qwen3-4B-Instruct-2507`, README `gpt-5.6-terra`) | `serve -h` với từng selector; luôn truyền `--model_name` | Theo đúng tên cờ thực tế; cập nhật spec |
| R3 | Handler `omnivoice` có nạp được checkpoint G-OmniVoice không (cờ `--omnivoice_model_name` đã có, mặc định `k2-fsa/OmniVoice`) | Trỏ model name tới G-OmniVoice, sinh 1 câu | Bọc G-OmniVoice bằng server `/v1/audio/speech` như Gwen |
| R4 | `--openai_tts_sample_rate 48000` với PCM thô của VieNeu có phát đúng cao độ/tốc độ không (s2s biết sample rate qua cờ, không đọc header; mặc định 24000) | Tone-server/VieNeu phát 1 câu, kiểm tra | Proxy resample về giá trị cờ; hoặc xin `sample_rate=16000` từ VieNeu |
| R5 | VRAM: Qwen 1.7B + G-OmniVoice/Gwen + VieNeu trên 24 GB | Đo peak mỗi run | Giữ 1 ASR + 1 TTS; giảm precision |
| R6 | LLM endpoint có streaming và hủy được khi bị ngắt | Ngắt giữa câu, xem LLM server có dừng sinh | Ghi nhận; barge-in vẫn dừng phát âm thanh nhưng lãng phí compute |
| R7 | Hook tiền xử lý text trước TTS trong HF s2s (không thấy trong tài liệu đã capture) | Đọc code/handler | Đặt rule tối thiểu trong proxy/server TTS |
| R8 | Trình duyệt chặn mic khi không phải HTTPS/localhost (tài liệu demo xác nhận, **Reported**); ICE mặc định dùng STUN của Google; WebRTC cần UDP từ client tới backend | Mở demo từ máy khác; xem ICE candidate | Reverse proxy TLS tự ký, hoặc chạy trình duyệt trên chính máy GPU; đặt ICE server LAN |
| R9 | Mâu thuẫn tham số endpoint (HF s2s default so với report) | — | Giữ default HF s2s ở Phase 1 (đã quyết) |
| R10 | Trần chất lượng 16 kHz: tài liệu s2s nói cả `--tts openai` lẫn `omnivoice` đều đưa audio về khối mono `int16` 16 kHz (**Reported**), nên khả năng cao là có; Opus 48 kHz của WebRTC chỉ là transport (chi tiết trong kế hoạch §0.1) | Sweep 0–20 kHz qua tone-server, xem phổ loopback | Ghi giới hạn; A/B vẫn công bằng |
| R11 | s2s chia text LLM → TTS theo câu; `--stream_batch_sentences` mặc định 3 (gom 3 câu). Với giá trị 1, câu đầu có tới TTS trước khi LLM xong không, và có chia được ở mệnh đề không | Tone-server ghi số và thời điểm request TTS cho một câu trả lời ≥ 3 câu; so với `llm_done` | Chia câu ở proxy **không** lấy lại thời gian chờ LLM. Quyết định patch chunker trong s2s (kế hoạch D6) hay ghi giới hạn |
| R12 | TTS có chạy speculative trong grace 800 ms hay chỉ sau output commit | Nói, dừng, nói tiếp sau ~500 ms; xem tone-server có nhận request TTS của revision bị bỏ không | Không sửa ở Phase 1; dùng kết quả để đọc đúng timeline v2v (§1) |

---

## 7. Checklist Phase 1

- [ ] Day 0: xác minh R1–R8, R10–R12 (nhiều ô nay chỉ còn là xác nhận cờ/giá trị, xem §6).
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

**Thứ tự ưu tiên về latency (Synthesis, sau review):** (1) bảo đảm LLM → TTS theo mệnh đề (nếu R11 fail và chưa vá ở Phase 1); (2) A/B grace có kiểm soát `--speculative_reopen_ms` 800 → 600 → 400, đo kèm `E-CUT`/reopen; (3) giữ streaming proxy → browser, tune buffer playback theo v2v, underrun và thời gian bot im; (4) đo LLM tới mệnh đề đầu với context dài; (5) Nemotron streaming nếu timeline R0 cho thấy ASR sau soft-end là nút thắt (có thể kéo về cuối Phase 1, kế hoạch D8); (6) cuối cùng mới tới optimizer (`torch.compile`, vLLM) trên đúng workload hội thoại, không dùng tốc độ batch của vendor. Streaming ASR không vượt qua được output gate.

- Corpus đánh giá ASR có nhãn (3 miền, entity, nhiễu SNR 0/5/10/20 dB, đoạn im lặng/nhạc) → WER/CER + entity exact-match.
- Handler WebSocket cho Nemotron để có partial; đo lợi ích latency của streaming so với turn-final. Lưu ý (**Reported**): `--stt openai-realtime` của s2s nói giao thức transcription của OpenAI (24 kHz), còn `/v1/audio/transcriptions/realtime` của NeMo-Speech.cpp là giao thức riêng, nguồn ghi "không phải OpenAI Realtime API"; chưa có bằng chứng hai bên ghép được mà không cần handler/adapter. Thử bằng stub trước (có thể đưa vào Day 0, kế hoạch D8). Giữ cache encoder/decoder theo session, flush/finalize tại endpoint; không decode từng chunk độc lập rồi nối text. Chunk 160/320 ms là điểm bắt đầu để thử, không phải v2v. Không gọi LLM cho từng partial; speculation chỉ tại soft-end và hủy khi transcript đổi.
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
