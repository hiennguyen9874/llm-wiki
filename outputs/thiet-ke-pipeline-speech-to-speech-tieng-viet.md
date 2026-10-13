# Thiết kế pipeline speech-to-speech tiếng Việt (bản production)

> **Loại tài liệu:** thiết kế kiến trúc, là deliverable trong `outputs/`, không phải tri thức canonical của wiki.
> **Phiên bản:** v2, ngày 2026-10-14. Bản này thay v1 (2026-10-07). V1 tập trung vào chọn model và lộ trình MVP; v2 là thiết kế để chạy production. Danh sách thay đổi và bảng ánh xạ số mục cũ sang mới nằm ở [Phụ lục A](#phụ-lục-a-thay-đổi-so-với-v1-và-ánh-xạ-số-mục). Các chương 8, 12, 16–20 đang trỏ vào số mục của v1, và số mục chính được giữ nguyên nghĩa.
> **Đầu vào:**
> - **Yêu cầu** lấy từ [Spec PoC Phase 1](spec-poc-speech-to-speech-tieng-viet.md): mục tiêu, ràng buộc, quyết định Q1–Q30. Chỉ lấy yêu cầu. Kiến trúc PoC (HF s2s `serve` chạy model in-process) **không** được lấy làm kiến trúc production.
> - **Lựa chọn thành phần** lấy từ [ASR/STT realtime](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md), [TTS realtime](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md), [survey VAD/turn/denoise](survey-vad-turn-detection-denoise-tieng-viet.md) và [survey cầu text → speech](survey-cau-text-to-speech-tien-hau-xu-ly-sau-llm.md).
> - **Bất biến khi hiện thực** lấy từ các mục "lưu ý khi thiết kế" của [Chương 8](chuong-08-transport-mang-cho-audio-realtime.md), [12](chuong-12-llm-trong-vong-hoi-thoai-noi.md), [16](chuong-16-dataflow-end-to-end-va-audio-contract.md), [17](chuong-17-turn-taking-event-barge-in-va-cancellation.md), [18](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md), [19](chuong-19-cau-text-to-speech-chunker-normalizer-lexicon.md) và [20](chuong-20-latency-dinh-nghia-critical-path-do-luong.md).
>
> **Nhãn bằng chứng:**
> - **Reported:** nguồn tự công bố, chưa kiểm chứng.
> - **Observed:** thấy trong tài liệu hoặc code đã capture, chưa chạy.
> - **Synthesis:** suy luận và đề xuất của tài liệu này.
> - **Unverified:** chưa có sự kiện kiểm chứng.
> - **Chốt sau PoC:** tham số hoặc lựa chọn phải lấy từ số đo Phase 1 của spec, không tự đặt.
>
> **Phạm vi bằng chứng:** chưa có thành phần nào được cài đặt, chạy hay đo. Kiến trúc, API, schema và pseudo-code trong bài đều là **Synthesis**. Mọi con số về model và runtime là **Reported** và giữ nguyên nhãn của tài liệu nguồn.

---

## 0. TL;DR

1. **Hệ thống là cascade gồm năm khối chạy riêng và một LLM bên ngoài.**

   ```text
   client (WebRTC) → edge → orchestrator → asr-service
                                         → LLM (host riêng)
                                         → tts-service → orchestrator → client
   ```

   Model nặng không bao giờ chạy trong process của orchestrator.

2. **Orchestrator là owner duy nhất của lượt hội thoại.** Mỗi session là một actor có một inbox. Actor này sở hữu `turn_id`, `revision`, `generation_id`, output gate, barge-in và history. VAD (Silero) và Smart Turn v3.2 chạy ngay trong orchestrator vì chúng chạy được bằng ONNX trên CPU, cần độ trễ theo từng frame, và phải nằm cạnh owner. Orchestrator không import torch.

3. **`asr-service` có một hợp đồng cố định:** `Describe`, `StreamingRecognize`, `Recognize`. Bên trong là các engine adapter.
   - Production v1 chạy **turn-final**. Engine mặc định là Qwen3-ASR (0.6B hoặc 1.7B, **Chốt sau PoC**).
   - Có thể thêm streaming (Nemotron 3.5 qua NeMo-Speech.cpp) hoặc two-pass mà không phải đổi hợp đồng.
   - Lý do không bắt đầu bằng streaming: streaming ASR không vượt qua được output gate (§8.1).

4. **`tts-service` gộp cầu text → speech và engine TTS thành một service, đúng theo yêu cầu.** Service nhận **luồng text delta** từ LLM, rồi tự chạy chuỗi:

   ```text
   ThinkFilter → lọc markup → clause chunker → lexicon/normalizer tiếng Việt
              → engine → resample → watermark
   ```

   Đầu ra gồm audio, kèm `text.chunk` (`display_text`, `spoken_text`, `segments`, version). Orchestrator dùng `text.chunk` để làm caption và để cắt history theo phần người dùng đã nghe.
   - Lý do gộp: toàn bộ chính sách đọc (`max_chars`, code-switch, lexicon, tag hợp lệ, vùng miền) phụ thuộc vào engine. Gộp lại thì đổi TTS chỉ là đổi một khối.
   - Engine baseline là VieNeu v3 Turbo, chạy dưới dạng sidecar `api-gpu`.

5. **Có thể thay ASR hoặc TTS mà không sửa orchestrator.** Các cơ chế:
   - hợp đồng gRPC cố định;
   - capability descriptor (`Describe`) khai báo audio contract và text contract;
   - engine registry có version và checksum;
   - voice profile riêng theo engine;
   - bộ conformance test;
   - quy trình offline → shadow → canary → promote, với rollback bằng config.

6. **Khác PoC ở bảy điểm:**
   - Không chạy HF s2s trong production.
   - Không bị trần 16 kHz: TTS 48 kHz đi thẳng ra Opus 48 kHz.
   - History cắt thật theo played offset; HF s2s chỉ có `truncate` no-op.
   - Có admission control và backpressure theo từng cạnh.
   - Chạy nhiều session.
   - Có timeline đo theo lượt, join theo ID.
   - Có degradation ladder khi một service lỗi.

7. **Latency thường bị quyết định bởi output gate, không phải tốc độ model.** Thiết kế có ba mức speculation (L0, L1, L2) chọn bằng config. SLO lấy từ spec: v2v đo ở client P50 ≤ 1.5 s, P95 ≤ 2.5 s (mục tiêu mềm). Các đòn bẩy xếp theo thứ tự ở §8.3.

8. **Một số tham số chưa chốt, phải lấy từ PoC:** engine ASR/TTS mặc định, biến thể Smart Turn, grace và max wait, ngưỡng barge-in, `first_min` của chunker, `max_streams` của VieNeu, mức speculation, pre-buffer phía client. Danh sách đầy đủ ở §12.2.

---

## 1. Yêu cầu

Yêu cầu dưới đây chuyển từ spec PoC sang ngữ cảnh production. Cột "Nguồn" ghi Q (quyết định trong spec) hoặc mục của spec. Chỗ nào production mở rộng hơn spec thì ghi **Synthesis**.

### 1.1 Yêu cầu chức năng

| ID | Yêu cầu | Nguồn |
|---|---|---|
| FR1 | Hội thoại giọng nói tiếng Việt full-duplex: người dùng nói, bot trả lời bằng giọng nói, người dùng ngắt lời được (barge-in) | Q7, Q12, Q17 |
| FR2 | Client là trình duyệt, nối qua WebRTC; mic có AEC, NS, AGC | Q7, spec §2 |
| FR3 | Endpointing tự nhiên: không cắt khi người dùng ngập ngừng, không chờ quá lâu | spec G4 |
| FR4 | LLM là endpoint OpenAI-compatible có sẵn, streaming text, tắt thinking | Q5, Q9, Q23, spec §3.2 |
| FR5 | Đọc đúng số, tiền, ngày, giờ, viết tắt, tên riêng; system prompt cho văn nói cộng normalizer và lexicon | Q25, spec §3.5 |
| FR6 | Giọng preset (Bắc, Nam) và giọng clone từ reference **có consent** | Q15 |
| FR7 | **Thay được ASR và TTS** bằng config, A/B mỗi lần một thành phần | Q8, Q28; mở rộng cho production (**Synthesis**) |
| FR8 | Nhiều session đồng thời | spec loại khỏi PoC; production cần (**Synthesis**) |
| FR9 | Có điểm cắm cho: partial/caption, two-pass, speaker lock, denoise nhánh VAD, telephony 8 kHz | spec §8 backlog |

### 1.2 Yêu cầu phi chức năng

| ID | Yêu cầu | Giá trị | Nguồn |
|---|---|---|---|
| NFR1 | Latency voice-to-voice, đo ở client (D1) | P50 ≤ 1.5 s, P95 ≤ 2.5 s, mục tiêu mềm, báo theo loại lượt | spec §1 (Q24) |
| NFR2 | Privacy | Self-host toàn bộ. Không gửi audio hoặc text ra ngoài, kể cả STUN công cộng | Q6, spec §3.1 |
| NFR3 | Log | Mặc định không chứa nội dung (content-free). Transcript chỉ ghi khi opt-in | spec §2 |
| NFR4 | Phần cứng speech | Mỗi node speech có 1 GPU 24 GB. Scale bằng cách thêm node | Q4; mở rộng (**Synthesis**) |
| NFR5 | License | PoC được dùng model NC. Production phải qua license gate theo `license_profile` của từng deployment | Q3; §3 nguyên tắc 7 |
| NFR6 | Cách ly môi trường | Mỗi model service có process và environment riêng | spec §2 |
| NFR7 | Khả năng quan sát | Timeline theo lượt có các mốc soft-end, ASR, LLM, commit, TTS, playback; join theo ID | spec §5.3 |
| NFR8 | Vận hành | Warmup xong mới báo ready. Có healthcheck, admission, backpressure, degradation | **Synthesis**, Chương 18 |

### 1.3 Giả định và ngoài phạm vi

- LLM nằm trên host riêng. Thiết kế chỉ phụ thuộc vào `base_url`, tên model, streaming và khả năng hủy (R6 của spec).
- Agent phục vụ một người dùng mỗi session, không có diarization trong critical path (§7.5).
- Ngoài phạm vi v1: telephony 8 kHz (đã chừa ingress adapter), meeting nhiều người nói, model end-to-end speech-in/speech-out, tool có side effect (đã chừa hook, §5.7.6).

### 1.4 Khác biệt giữa PoC và production

| Chủ đề | PoC (spec Phase 1) | Production (tài liệu này) | Lý do |
|---|---|---|---|
| Orchestration | HF s2s `serve`, ASR Qwen chạy in-process | Orchestrator riêng, ASR và TTS là service | Cách ly, scale và thay thế; tránh các giới hạn ở §2 AD2 |
| Trần băng thông | 16 kHz (R10, **Reported**) | 48 kHz đầu cuối | `--tts openai` của s2s ép về 16 kHz `int16` |
| History khi bị ngắt | `conversation.item.truncate` là no-op | Cắt theo played offset và `segments` | Chương 17 §17.9, Chương 19 §19.5.3 |
| Cầu text → speech | Proxy mỏng hoặc rule tối thiểu (R7) | Nằm trong `tts-service`, có version, có test L1/L2/L3 | Yêu cầu gộp và Chương 19 |
| Chia text cho TTS | `--stream_batch_sentences` theo câu | Clause chunker trên luồng delta | R11 |
| Session | Một người dùng | Nhiều session, có admission | FR8 |
| Đo | Log s2s cộng `tts-proxy`/`llm-tap` | Timeline theo lượt, có ID và `t_mono_ns` ở mọi event | NFR7 |
| ICE | Đặt ICE server trỏ vào LAN | TURN/STUN tự host | NFR2 |

---

## 2. Quyết định kiến trúc

Mỗi quyết định ghi lý do và phương án đã loại. Tất cả là **Synthesis**, trừ phần bằng chứng có nhãn riêng.

| ID | Quyết định | Lý do | Phương án loại |
|---|---|---|---|
| **AD1** | **Cascade** VAD → turn → ASR → LLM → TTS | Hai model full-duplex mở trong wiki ([PersonaPlex 7B](../wiki/personaplex-7b-v1.md), [VoiceChat 11B](../wiki/nvidia-nemotronlabs-voicechat-11b.md)) chỉ khai `language: en`. Qwen3-Omni nhận tiếng Việt nhưng không phát ra tiếng Việt (**Reported**). Cascade cho phép kiểm soát, thay từng thành phần, và gắn RAG/tool | End-to-end. Đánh giá lại bằng các gate ở §10 khi có model full-duplex hỗ trợ tiếng Việt |
| **AD2** | **Tự viết orchestrator.** HF s2s chỉ dùng làm harness đo trong PoC và làm tham chiếu cho turn tracker | HF s2s có các giới hạn production sau (**Reported/Observed**): TTS bị ép về 16 kHz; `truncate` là no-op; text gửi TTS chia theo câu và không có hook normalizer (R7, R11); ASR Qwen chạy in-process; không có admission dùng chung; LLM proxy không có auth; `compact_history` tạo một lời gọi LLM ẩn; handler `omnivoice` không có `tts_ttfa`. Phần điều khiển (owner, generation floor, output hold) là phần lõi cần đúng tuyệt đối theo Chương 17–18 | Chạy HF s2s trong production. Pipecat được phép làm khung hiện thực **nếu** qua được bộ test ở §10 (cách gom câu, cách lưu context và khả năng hủy giữa câu của Pipecat vẫn **Unverified**) |
| **AD3** | Model ASR/TTS chạy **ngoài process** của orchestrator, mỗi model một owner process | Cách ly torch/CUDA/numpy (HF s2s từng xung đột DeepFilterNet `numpy<2` với Pocket TTS, **Reported**). Scale riêng từng service. Thay engine không phải restart session | Load model trong gateway worker |
| **AD4** | **Cầu text → speech nằm trong `tts-service`.** Service nhận luồng text delta | Chính sách đọc gắn với engine và voice (Chương 19 §A.7). Gộp lại thì đổi engine là đổi cả bộ chính sách. Chunker vẫn nằm ở consumer của LLM stream, vì orchestrator chuyển delta tới ngay khi nhận | Đặt chunker và normalizer trong orchestrator; đặt proxy normalizer đứng riêng |
| **AD5** | **Endpointing speculative + revision** (triết lý của HF s2s), chọn bằng config | Ở cùng mức im lặng, cách này giảm cắt nhầm lời người dùng. ASR và LLM chạy trong thời gian grace (Chương 20 §A.2). Commit cứng (grace = 0) vẫn là một chế độ config | Trộn tham số HF (64 ms, 800 ms, 2 s) với tham số của report (200–300 ms, 1.2–1.5 s) |
| **AD6** | **Downlink giữ sample rate gốc:** TTS 48 kHz s16le → Opus 48 kHz. Mỗi chiều resample tối đa một lần | Bỏ trần 16 kHz. VieNeu sinh 48 kHz (**Reported**) | Đưa mọi thứ về 16 kHz như HF s2s |
| **AD7** | Production dùng WebRTC. WebSocket PCM chỉ dùng cho dev và harness test. Cả hai nằm sau interface `Transport` | WebRTC có AEC, jitter buffer, chịu mất gói (**Reported**). WebSocket dễ replay và dễ debug | Chỉ dùng WebSocket |
| **AD8** | RPC nội bộ dùng **gRPC bidi streaming** (protobuf, deadline, hủy lan truyền). Engine sidecar nói API gốc của nó, chỉ trên localhost trong pod | Hủy stream là tín hiệu cancel chuẩn. Có deadline. Schema có version | REST/SSE cho mọi cạnh, khi đó hủy chỉ là đóng kết nối và không có cách xác nhận |
| **AD9** | **v1 dùng ASR turn-final.** Streaming ASR là tùy chọn có gate | Với output gate 800 ms đến 2 s, ASR sau soft-end thường nằm gọn trong grace. Streaming chỉ có lợi khi timeline cho thấy lượt bị giới hạn bởi compute, hoặc khi cần caption (Chương 20 §B, spec §8) | Bắt đầu bằng Nemotron streaming. Cầu NeMo realtime WS ↔ client chưa chắc ghép được (spec §8) |
| **AD10** | Tự host toàn bộ, kể cả TURN/STUN | NFR2 | STUN của Google (mặc định của demo HF, **Reported**) |

---

## 3. Nguyên tắc thiết kế

Nguyên tắc 1–7 giữ nguyên số thứ tự và nghĩa như v1 (các chương khác đang trỏ vào). Nguyên tắc 8–12 được thêm cho production. Tất cả là **Synthesis**.

1. **Tách năm tầng:** model, inference runtime, API server, streaming policy, orchestration. Runtime có hỗ trợ GGUF không có nghĩa là checkpoint stream được. Route "OpenAI-compatible" không có nghĩa là thay thẳng được. License của runtime không thay cho license của weights.
2. **Mỗi quyết định về lượt chỉ có một owner:** session actor trong orchestrator. Trong code chỉ có đúng một chỗ commit, một chỗ reopen và một chỗ tăng `generation_id`. VAD, Smart Turn, ASR, LLM, TTS, client và timer chỉ gửi sự kiện vào inbox. Endpointing riêng của ASR engine (ví dụ NeMo-Speech.cpp EOU) phải tắt, hoặc chỉ được dùng làm tín hiệu.
3. **ASR nghe audio đã qua AEC, chưa qua enhancement.** Denoise chỉ dùng cho nhánh VAD/barge-in, cho đến khi có A/B trên WER tiếng Việt chứng minh điều ngược lại. Bằng chứng hiện tại mâu thuẫn (§11).
4. **Mỗi backend tự khai báo hợp đồng qua `Describe`.** Audio contract gồm sample rate, dtype, số kênh, framing và cách hủy. Text contract gồm `max_chars`, code-switch, phân biệt hoa thường, tham số bị bỏ qua và inline tag hợp lệ. Client của hợp đồng không được hard-code các giá trị này.
5. **Không hành động trên văn bản chưa commit.** Phát audio là ranh giới cứng: không chunk audio nào ra client trước `turn.commit` của đúng `(turn_id, revision)`. Partial chỉ dùng cho caption và cho tính toán speculative. Ghi history và tool có side effect chỉ chạy sau commit.
6. **Không cộng các con số khác loại.** Chunk size của ASR không phải độ trễ ra text. TTFT của LLM không phải độ trễ từ mic. TTFA của TTS không phải v2v. RTF batch không phải RTF một stream. Mỗi metric được đặt tên theo cặp mốc đầu và cuối.
7. **License là hard gate,** xét trước mọi điểm chất lượng. Production đọc `license_profile` (`research` hoặc `commercial`) của deployment. Registry chặn engine không đạt profile.
8. **Service sở hữu model.** Orchestrator chỉ chạy model nhỏ bằng ONNX Runtime trên CPU (VAD, Smart Turn). Mọi thứ cần torch, vLLM hay CUDA nằm trong service riêng.
9. **Hợp đồng trước, engine sau.** Orchestrator chỉ biết hợp đồng `asr.v1` và `tts.v1`. Mọi chi tiết riêng của engine (sample rate, endpoint, quirk, lexicon, filter hallucination) nằm trong adapter của service.
10. **Mọi queue đều có giới hạn, mỗi cạnh có policy riêng** (§9.6). Hủy là best-effort, còn lọc theo `generation_id` là bắt buộc ở mọi chỗ dữ liệu đổi chủ. Hủy task không đồng nghĩa với dừng compute, nên phải đo cả hai.
11. **History là thứ người dùng đã nghe.** History chỉ lưu `display_text`, không lưu `spoken_text`, và cắt theo played offset một cách bảo thủ.
12. **Quan sát được mà không chứa nội dung.** Mọi event mang `session_id`, `turn_id`, `revision`, `generation_id`, `chunk_id`, `t_mono_ns`. Log vận hành chỉ ghi độ dài, loại và version, không ghi text hay audio.

---

## 4. Kiến trúc tổng thể

### 4.1 Sơ đồ

```text
┌──────────────────────────── Client (web app) ────────────────────────────────┐
│ getUserMedia{echoCancellation, noiseSuppression, autoGainControl}            │
│ WebRTC: audio track lên (Opus) ─┐   ┌─ audio track xuống (Opus 48 kHz)       │
│ DataChannel: event điều khiển, caption, audio.stats/audio.played, lỗi       │
└──────────────────────────────────┼───┼───────────────────────────────────────┘
          HTTPS signaling + token  │   │  SRTP/UDP (TURN tự host khi cần)
┌──────────────────────────────────▼───┴───────────────────────────────────────┐
│ edge: TLS, xác thực, signaling, admission theo session, route sticky          │
└──────────────────────────────────┬───────────────────────────────────────────┘
┌──────────────────────────────────▼──────── orchestrator (CPU, N session/process)┐
│ Transport (WebRTC | WS) → Opus decode → 16 kHz mono f32 → ring ≥ 10 s           │
│   ├─ VAD consumer: Silero ONNX (512 mẫu) ─┐                                     │
│   ├─ Smart Turn v3.2 ONNX (executor riêng)─┼─► SessionActor (owner, 1 inbox)    │
│   └─ barge-in gate (+ speaker lock, P2) ──┘    turn/revision/generation         │
│ SessionActor: response scope, held output, history, validity gate               │
│ LLM client (SSE, aclosing, deadline) ───────────────────────────► LLM (host riêng)│
│ Downlink pacer (lịch tuyệt đối, credit) → Opus 48 kHz encode → track            │
└───────┬────────────────────────────────────────────┬──────────────────────────────┘
        │ gRPC asr.v1                                 │ gRPC tts.v1
        │ (PCM16 16 kHz / audio của lượt)             │ ↓ text.delta   ↑ text.chunk + audio 48 kHz
┌───────▼──────────────────────────┐   ┌──────────────▼────────────────────────────────────────┐
│ asr-service                      │   │ tts-service                                           │
│  API + session/stream mgmt       │   │  API + bridge cho mỗi generation:                     │
│  post: NFC, punct (nếu cần),     │   │  ThinkFilter → markup → ClauseChunker →               │
│        filter, quality_flags     │   │  pre-lexicon → VietNormalizer → post-lexicon → tag    │
│  engine adapter                  │   │  engine adapter → resample (soxr) → watermark         │
│  ┌ engine sidecar (GPU) ┐        │   │  ┌ engine sidecar (GPU) ┐  fixed-phrase cache         │
│  │ vLLM qwen-asr /      │        │   │  │ VieNeu api-gpu /     │                             │
│  │ NeMo-Speech.cpp ...  │        │   │  │ VoxCPM2 ...          │                             │
│  └──────────────────────┘        │   │  └──────────────────────┘                             │
└──────────────────────────────────┘   └───────────────────────────────────────────────────────┘
  registry (git, read-only mount): model manifest + checksum, voice registry, lexicon, text policy
  observability: OpenTelemetry collector → metrics/traces; log content-free; corpus opt-in tách riêng
  coturn (TURN/STUN tự host)
```

### 4.2 Các service

| Service | Trách nhiệm | Chứa | Phần cứng | Trạng thái | Đơn vị scale |
|---|---|---|---|---|---|
| **edge** | TLS, xác thực, signaling WebRTC, admission (trần số session), route session tới orchestrator (sticky), cấp ICE config | Reverse proxy cộng signaling API | CPU | Không có state | Ngang |
| **coturn** | TURN/STUN tự host | coturn | CPU, mạng | Không có state | Ngang |
| **orchestrator** | Transport, ingress audio, VAD, Smart Turn, owner của lượt, barge-in, LLM client, history, downlink pacer, telemetry theo lượt | onnxruntime (CPU), Opus, resampler; **không có** torch | CPU | State session trong RAM | Theo process, session sticky |
| **asr-service** | Nhận dạng tiếng Việt theo hợp đồng `asr.v1`; hậu xử lý; gắn cờ chất lượng | API process cộng engine sidecar | GPU (engine), CPU (API) | State stream trong lúc gRPC stream còn mở | Theo pool engine |
| **tts-service** | Cầu text → speech cộng tổng hợp giọng theo hợp đồng `tts.v1` | API/bridge process cộng engine sidecar, fixed-phrase cache | GPU (engine), CPU (bridge) | State theo stream (một generation) | Theo pool engine |
| **speaker-service** (P2, tùy chọn) | Embedding người nói cho speaker lock | ECAPA/CAM++ ONNX | CPU hoặc GPU | Không có state (embedding giữ ở orchestrator) | Ngang |
| **registry** | Manifest model (revision, sha256), voice registry (kèm consent), lexicon, text policy, routing thí nghiệm | Repo git, mount read-only | — | Có version | — |
| **observability** | Metrics, trace, log content-free | OTel collector, Prometheus, Grafana (hoặc tương đương) | CPU | — | — |
| **LLM** (ngoài phạm vi) | Sinh text streaming | Endpoint OpenAI-compatible có sẵn | Host riêng | — | — |

### 4.3 Ranh giới trách nhiệm

| Service | Làm | **Không** làm |
|---|---|---|
| orchestrator | Quyết định lượt, commit, cancel, history, policy validity, chọn engine theo session | Load model torch/vLLM. Tự normalize text đọc. Tự resample TTS |
| asr-service | Trả partial/final kèm `quality_flags`. Filter đặc thù engine (blacklist Whisper, …) | Quyết định hết lượt. Quyết định bỏ lượt. Gọi LLM |
| tts-service | Biến luồng text thành audio cộng alignment. Chính sách đọc theo engine/voice | Quyết định commit hoặc phát. Ghi history. Tự sinh câu đệm khi không được yêu cầu. Định tuyến backend theo từng chunk |
| edge | Xác thực, admission, route | Xử lý audio |

### 4.4 Thành phần đặt ở đâu

| Thành phần | Đặt ở | Runtime | Lý do (**Synthesis**) |
|---|---|---|---|
| Silero VAD v5/v6 | orchestrator | onnxruntime CPU, state riêng mỗi session | Dưới 1 ms mỗi khối (**Reported**), chạy theo frame, phải ở cạnh owner. Mất một hop mạng mỗi 32 ms là vô lý |
| Smart Turn v3.2 (CPU int8) | orchestrator, **executor riêng** | onnxruntime CPU | Mất 10 ms đến hơn 100 ms (**Reported**), nên không được gọi trên event loop (Chương 18) |
| Smart Turn bản GPU fp32 | `turn-service` riêng (chỉ khi chọn bản GPU) | onnxruntime CUDA | Không cho orchestrator phụ thuộc CUDA |
| Denoise nhánh VAD (RNNoise / DeepFilterNet 3) | orchestrator (RNNoise, thư viện C) hoặc process riêng (DeepFilterNet, vì xung đột `numpy<2`) | CPU | Mặc định tắt (§5.2) |
| Opus, WebRTC, resample uplink | orchestrator (transport) hoặc SFU | CPU | Chỉ resample một lần: 48 kHz → 16 kHz |
| Model ASR | asr-service, engine sidecar | vLLM / NeMo-Speech.cpp / CTranslate2 / sherpa-onnx | Cách ly môi trường, scale theo GPU |
| Punctuation restoration (nếu engine không có) | asr-service | ONNX | Phụ thuộc engine |
| Filter hallucination (Whisper) | asr-service adapter | CPU | Phụ thuộc engine |
| Policy hợp lệ, hỏi lại | orchestrator | — | Là quyết định về lượt |
| LLM client, prompt, history | orchestrator | httpx/SSE async | Thuộc về owner |
| ThinkFilter, chunker, VietNormalizer, lexicon, whitelist tag, LID | tts-service bridge | Python thuần (VietNormalizer khoảng 0.6 ms/lần, **Reported**) | Chính sách gắn với engine (AD4) |
| Model TTS | tts-service, engine sidecar | VieNeu Docker `api-gpu`, … | Cách ly, slot, warmup |
| Resample downlink, watermark | tts-service | soxr | Orchestrator nhận đúng format nó yêu cầu |
| Opus encode downlink, fade khi cắt | orchestrator pacer | CPU | Pacer là nơi cắt audio |
| Speaker embedding | speaker-service (P2) | ONNX | Tùy chọn |

**Khi nào tách thêm service:** chỉ khi đo được nhu cầu.
- Smart Turn tách thành `turn-service` khi chọn bản GPU, hoặc khi executor làm loop lag P99 > 5 ms.
- VAD batch hóa giữa các session khi loop lag tăng theo số session. Chương 18 ước khoảng 30 session thì một loop bão hòa (**Synthesis**).
- Punctuation restoration tách ra khi nhiều engine ASR dùng chung.

---

## 5. Các tầng xử lý

### 5.1 Transport, AEC và client

**Client.** Production dùng web app riêng, không dùng browser demo của HF.
- Gọi `getUserMedia` với `echoCancellation`, `noiseSuppression`, `autoGainControl` (AEC tầng 2, **Reported**).
- Gửi audio lên bằng track WebRTC. Nhận audio xuống bằng track WebRTC, Opus 48 kHz.
- DataChannel dùng cho event điều khiển (§7.2).
- Mic chỉ hoạt động trên HTTPS hoặc `localhost` (**Reported**).

**Đường đi của audio.**
- Lên: Opus → decode 48 kHz → resample **một lần** xuống 16 kHz mono f32 trong orchestrator. Frame transport 20 ms, reblock thành 512 mẫu cho Silero.
- Xuống: tts-service trả PCM s16le 48 kHz mono → pacer → Opus 48 kHz. Không đi qua 16 kHz (AD6).

**Kết thúc WebRTC ở đâu** (**Synthesis**, phải đánh giá lúc hiện thực):

| Phương án | Khi nào | Ghi chú |
|---|---|---|
| WebRTC kết thúc ngay trong orchestrator | LAN, nội bộ, số session vừa phải | Đơn giản nhất. Orchestrator cần cổng UDP và TURN |
| SFU tự host (ví dụ LiveKit server), orchestrator vào phòng như một participant | Internet hoặc mobile, nhiều session, sau này có SIP | SFU lo ICE, TURN và congestion. Turn detector của LiveKit không có tiếng Việt (**Reported**) nên không dùng nó |

Cả hai nằm sau interface `Transport`, nên đổi phương án không làm thay đổi phần ASR, LLM hay TTS.

**ICE.** Chỉ trỏ tới coturn tự host. Không dùng STUN công cộng (NFR2).

**AEC tầng 3** (P2) là kiểm tra echo phía server. Khi bot đang nói mà VAD bật, quick-ASR của đoạn đó được so với text bot đang phát. Nếu trùng thì coi là echo (**Reported** là ý tưởng, **Synthesis** là cách đặt).

**WebSocket transport (dev/harness).** PCM16 16 kHz lên. PCM 48 kHz xuống, mỗi frame có header `(generation_id, sequence)`. Client có `floor` và AudioWorklet đếm số mẫu đã render để báo `audio.played` chính xác. Transport này dùng để replay audio cố định trong test (§10).

### 5.2 VAD

| Mục | Thiết kế |
|---|---|
| Model | Silero VAD v5/v6 ONNX. Mỗi session một state, cửa sổ 512 mẫu (32 ms) ở 16 kHz (**Reported**) |
| Threshold | Khởi điểm 0.6 theo default HF s2s (**Observed**). Hiệu chỉnh theo nhiễu: đo xác suất VAD và RMS trong 2–3 s đầu; nếu nền > 0.3 thì nâng lên 0.65–0.7 (**Reported**, AI report). **Chốt sau PoC** |
| Padding | Liệt kê **mọi** lớp padding: pre-roll lấy từ ring, `speech_pad`. Mục đích là để chúng không cộng dồn ngoài ý muốn (Chương 16 §16.17.2) |
| Chạy ở đâu | Task consumer của uplink, không chạy trong reader của transport |
| Ứng viên thay thế | FireRedVAD có false alarm thấp hơn trong bảng của chính vendor (2.69% so với Silero 9.41%, **Reported**). Đáng A/B khi nền là TV hoặc nhạc. Không có VAD nào có số đo riêng cho tiếng Việt |
| Denoise | Mặc định **tắt**. Nếu bật thì RNNoise hoặc DeepFilterNet 3, **chỉ** cho nhánh VAD/barge-in. Facebook Denoiser là CC-BY-NC và không có metric chất lượng (**Reported**) |

### 5.3 Turn detection và endpointing

**Máy trạng thái lượt** (speculative + revision, theo turn tracker của HF s2s, **Reported**):

```text
LISTENING ──VAD im ≥ min_silence──► SOFT_ENDED ──Smart Turn: complete────► (grace) ──► COMMIT
    ▲                                   │      └─Smart Turn: incomplete──► chờ incomplete_delay ─► (gate tới max_wait) ─► COMMIT
    └──────── user nói tiếp (≥ continuation_ms) ◄──── reopen: revision++, bỏ việc chưa commit
```

**Tham số khởi điểm.** Đây là default của HF s2s, đã thấy trong argument class (**Observed**). Giữ nguyên bộ này cho tới khi PoC có số đo, và **không** trộn với bộ tham số của report.

| Tham số | Khởi điểm | Ghi chú |
|---|---|---|
| `min_silence_ms` | 64 | Đây là ngưỡng *ứng viên* soft-end, chưa phải thời điểm bot được nói |
| `min_speech_ms` | 384 | Rủi ro mất các lệnh một âm tiết như "không" hay "dừng". Phải test riêng (§10) |
| `continuation_ms` | 192 | Phải nhỏ hơn ngưỡng mở lượt và ngưỡng barge-in (Chương 17) |
| `speculative_reopen_ms` (grace) | 800 | **Chốt sau PoC.** Spec §8 đề xuất A/B 800 → 600 → 400 |
| `smart_turn_threshold` | 0.5 | |
| `smart_turn_incomplete_delay_ms` | 600 | |
| `smart_turn_max_wait_ms` | 2000 | Timeout dự phòng |
| Ring buffer | ≥ 10 s | Smart Turn cần cửa sổ 8 s, cộng thêm biên cho pre-roll và backlog (Chương 16) |
| Pre-roll | 200–300 ms, lấy từ ring | Khi barge-in, turn buffer bắt đầu từ đầu đoạn nói trừ pre-roll |

**Smart Turn với tiếng Việt** (**Reported**, benchmark vendor trên 1.004 mẫu):

| Bản | Accuracy | FPR | FNR |
|---|---|---|---|
| GPU fp32 | 82.47% | 9.56% | 7.97% |
| CPU int8 (mặc định của HF s2s) | 79.38% | 8.86% | 11.75% |

Bản CPU ít cắt lời hơn nhưng chờ thừa nhiều hơn. Chọn bản nào tùy theo lỗi nào sản phẩm khó chịu đựng hơn (**Chốt sau PoC**). Nếu false-interruption tiếng Việt trên dữ liệu thật vượt 10%, thử Namo hoặc fine-tune (ngưỡng thay thế, **Reported**). TEN Turn Detection và LiveKit turn detector không hỗ trợ tiếng Việt.

**Một owner.** Endpointing trong NeMo-Speech.cpp (`stop_history_eou_ms`) và segmentation của WhisperLiveKit hay RealtimeSTT phải tắt, hoặc chỉ được dùng làm tín hiệu.

**Timer.** Mọi timer (grace, incomplete, max wait, unanswered) mang token `(turn_id, revision)`. Khi revision đã đổi, timer tự vô hiệu. Config ghi rõ timer nào chạy theo đồng hồ audio (chỉ số mẫu) và timer nào chạy theo wall clock.

### 5.4 ASR service

**Trách nhiệm:** nhận dạng tiếng Việt, hậu xử lý, gắn cờ chất lượng. Không quyết định lượt. Hợp đồng ở §7.6.

**Ba chế độ, cùng một hợp đồng:**

| Chế độ | Luồng | Khi nào |
|---|---|---|
| `turn_final` (v1) | Orchestrator gửi audio của lượt (16 kHz, có pre-roll) qua `Recognize` ngay lúc soft-end. Nếu reopen thì gửi lại toàn bộ lượt với `revision` mới | Mặc định. Có speculation vì ASR chạy trong grace |
| `native_stream` / `buffered_stream` | `StreamingRecognize` nhận frame từ lúc bắt đầu nói trừ pre-roll, trả `partial`. `Finalize(turn_id, revision)` lúc soft-end | Cần caption, speculation trên partial, hoặc timeline cho thấy bị giới hạn bởi compute |
| `two_pass` | Stream để lấy partial, cộng `Recognize` trên engine final cho lượt cần kiểm tra lại (critical span hoặc cờ chất lượng) | Khi lỗi số, tên hay phủ định vẫn cao sau khi tune (P3) |

**Engine adapter đầu tiên.** Số liệu là **Reported**, vai trò là **Synthesis**. Chi tiết ở [tài liệu ASR](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md).

| Engine | Adapter → runtime | Chế độ | Vai trò | Gate |
|---|---|---|---|---|
| Qwen3-ASR 0.6B / 1.7B | vLLM `qwen-asr-serve` (sidecar), ép `language=vi` | turn_final | **Mặc định v1**. Chọn 0.6B hay 1.7B theo PoC (R0 so với R1) | Đo TTFT dưới concurrency: 92 ms ở c=1, 3.210 ms ở c=128 (**Reported**). Admission theo model là bắt buộc. Giới hạn tỷ lệ VRAM vLLM được cấp phát trước |
| Nemotron 3.5 Streaming 0.6B | NeMo-Speech.cpp `serve`, HTTP `/v1/audio/transcriptions` (turn_final) hoặc realtime WS (stream) | turn_final → native_stream | Challenger. Partial 160–320 ms ở P2 | Giá trị `language` hợp lệ (R1). WS là giao thức riêng của dự án. Confidence RNNT luôn bằng 1.0 nên không dùng làm tín hiệu được. Có word boosting `speech_contexts`. Route health không có auth, chỉ bind loopback |
| Gipformer 1.5 68M | sherpa-onnx `OfflineRecognizer` (CPU) | turn_final / final-pass | Final-pass trên CPU, tổng đài/domain; giải phóng GPU | Output có dấu câu hay không chưa rõ, có thể cần bước punctuation. File LICENSE chưa có |
| faster-whisper large-v3-turbo | CTranslate2 | turn_final | Đối chứng | Bắt buộc có filter hallucination ([cấu hình](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md#63-whisper-large-v3-turbo-baseline-turn-final)). Gọi `list(segments)` trong executor |
| ChunkFormer RNNT large | ONNX | turn_final / final-pass | Đối chứng chuyên Việt (CC-BY-4.0) | Bản CTC là NC |

**Hậu xử lý trong service:**
1. Unicode NFC.
2. Punctuation restoration nếu `Describe.punctuation=false`. Ứng viên: [Punctuation Restoration 307M](../wiki/punctuation-restoration-base.md), F1 tiếng Việt 0.866 (**Reported**).
3. Filter riêng theo engine.
4. Gắn `quality_flags`: `empty`, `no_speech`, `hallucination_suspect`, `language_mismatch`, `truncated`, `low_confidence` (chỉ khi confidence đã được calibrate, nếu không thì `unknown`).

**Validity gate** chạy ở orchestrator, không chạy trong ASR service:

| Cờ / tình huống | Hành vi |
|---|---|
| `empty`, hoặc `no_speech` khi VAD ngắn | Bỏ lượt, quay về LISTENING. Không gọi LLM |
| `hallucination_suspect` | Hỏi lại bằng câu soạn sẵn, phát từ cache. Không gọi LLM |
| Đoạn ngắn trong lúc bot đang nói | Xử lý theo policy backchannel ba kết cục (§7.3) |
| Lượt có entity quan trọng (P3, khi có tool) | Đọc lại để xác nhận trước khi chạy tool |

**Capacity.** Mỗi engine có semaphore riêng và hàng đợi có giới hạn. Khi quá tải, service trả `RESOURCE_EXHAUSTED` kèm `retry_after_ms`. Tách pool streaming (nhạy cadence) khỏi pool final (có thể batch, nhưng chỉ khi cửa sổ gom nhỏ hơn nhiều so với ngân sách từ endpoint tới final).

### 5.5 TTS service, phần 1: cầu text → speech

**Vì sao cầu nằm trong `tts-service`** (**Synthesis**, theo yêu cầu và Chương 19):
- Chính sách đọc phụ thuộc engine và voice: `max_chars` (VieNeu mặc định 256), có đọc được code-switch không, tag hợp lệ, vùng miền của giọng (`nghìn`/`ngàn`, `linh`/`lẻ`), scope của lexicon, tham số bị bỏ qua (VieNeu bỏ qua `speed` và `instructions`, **Reported**).
- Đổi engine thì đổi trọn bộ. Orchestrator không cần biết gì.
- Cầu là hàm thuần, khoảng 0.1 ms mỗi chunk, nên không làm tăng latency.
- Chunker vẫn là consumer của LLM stream, vì orchestrator chuyển `text.delta` ngay khi nhận (L1 và L2 ở §5.7.3).

**Pipeline cho mỗi stream `Synthesize` (một generation):**

```text
text.delta ─► ThinkFilter ─► markup/emoji/URL policy ─► ClauseChunker ─┐
                                                                      ▼
   text.chunk{display_text, segments, kind, warnings, versions} ◄── pre-lexicon (bảo vệ thực thể)
                                                                      ▼
                                       VietNormalizer (verbalizer trên segment `plain`)
                                                                      ▼
                                       post-lexicon (respelling theo engine/voice) → alert list
                                                                      ▼
                                       whitelist inline tag theo engine → spoken_text
                                                                      ▼
                         hàng engine (bounded) → engine adapter → resample → watermark → audio.chunk
```

**Bất biến** (từ Chương 19 §A, **Synthesis**):
1. Mỗi `generation_id` có một instance cầu. Khi bị hủy thì vứt bỏ instance, **không** gọi `flush()`.
2. Chunker chỉ cắt khi đã thấy ký tự đứng sau dấu câu. Nhờ vậy đầu ra không phụ thuộc vào cách LLM chia token (fuzz test L2).
3. Có ba dạng text, mỗi dạng một nơi dùng. `display_text` cho caption và history. `spoken_text` chỉ cho engine. `raw_text` chỉ cho debug opt-in.
4. Normalizer chạy **sau** chunker, trên từng chunk, và là hàm thuần. Mỗi loại ký hiệu chỉ có một stage sở hữu.
5. Normalizer không sửa nội dung. Gặp chỗ mơ hồ thì theo chính sách đã ghi thành văn bản. Không chắc thì đọc nguyên văn và ghi `warnings`.
6. Lexicon là dữ liệu sản phẩm, có version, scope theo engine/voice, và có test.
7. Chunk nào có `spoken_text` rỗng thì phát event nhưng **không** gọi engine.

**Tham số chunker khởi điểm** (**Reported** từ AI report, cần tune, **Chốt sau PoC**):
- Flush khi gặp `.?!…;:` hoặc xuống dòng.
- Chunk đầu: cắt ở dấu phẩy khi đã có ít nhất `first_min` ≈ 25 ký tự.
- Gộp mảnh ngắn hơn 8 ký tự vào chunk sau.
- `hard_max` < `max_chars` của engine. Khi buộc phải cắt vì `hard_max`, cắt **trước** liên từ.
- Không cắt bên trong giá trị: `1.250.000đ`, `3,5`, `14:30`, `TP.HCM`, URL, `TS. Nguyễn`.
- Chỉ hạ `hard_max` khi đo thấy `inter_chunk_gap_ms` P95 cao.

**Normalizer.** [VietNormalizer](../wiki/vietnormalizer.md) (MIT, 19 bước, **Reported**, chưa chạy) được bọc làm verbalizer cho các segment `plain`.
- Với VieNeu Turbo: tắt `enable_transliteration`, vì engine tự đọc được code-switch.
- Output của VietNormalizer bị lowercase. Phải kiểm tra việc này có làm mất prosody không. Giữ dấu câu.
- ViSoNorm mặc định tắt (chưa có license, hợp với text người dùng gõ hơn).
- Pin version. Ghi `normalizer_version` và `lexicon_version` vào mỗi `text.chunk`.

**Lexicon hai pha.**
- Pre-TN bảo vệ thực thể: tên riêng, mã.
- Post-TN respell theo engine.
- Một **alert list** riêng cho các từ respelling không cứu được. Ví dụ `chánh` → `tránh` của VieNeu (issue #207, **Reported/Unverified**). Phải reproduce trên đúng version và voice trước khi xử lý.

**Phòng thủ đầu tiên vẫn nằm ở orchestrator.** System prompt cho văn nói và tắt thinking (§5.7.4). ThinkFilter trong cầu chỉ là lưới an toàn. Đo mức LLM tuân thủ prompt bằng `norm_warnings` và `chunk_kind_ratio`.

### 5.6 TTS service, phần 2: engine, giọng và capacity

**Engine adapter.** Số liệu là **Reported**. Chi tiết ở [tài liệu TTS](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md).

| Engine | Adapter → runtime | Streaming | Rate gốc | Hủy | Vai trò / gate |
|---|---|---|---|---|---|
| **VieNeu v3 Turbo** | `openai_speech_pcm` → sidecar Docker `api-gpu`, `POST /v1/audio/speech`, `response_format=pcm`, `sample_rate=48000`, chunked | Theo frame (80 ms) | 48 kHz | Đóng response thì giải phóng slot ở tick kế tiếp (**Reported**) | **Baseline.** License mâu thuẫn (FAQ ghi Apache, roadmap ghi personal use) nên `license_profile=commercial` sẽ chặn cho tới khi giải quyết |
| VoxCPM2 2B | Adapter in-process trong sidecar Python, `generate_streaming`, cờ stop theo từng bước | Có | 48 kHz | Phải tự viết | Challenger cho cloning, Apache-2.0. Chưa có TTFA |
| MOSS-TTS Local v1.5 | SGLang-Omni, `stream=true` | PCM | 48 kHz | Chưa rõ | Challenger khi đã có SGLang-Omni. Phải xác nhận số kênh |
| G-OmniVoice / Gwen-TTS | Server tự bọc | Full waveform | 24 kHz / chưa rõ | Không có | Chỉ dùng nghiên cứu (`license_profile=research`). TTFA bằng thời gian sinh cả mệnh đề |
| Supertonic 3 / Kokoro vi / VieNeu Nano | ONNX CPU | Theo chunk / full | Theo model | — | Đường CPU/edge |

**Chi tiết sidecar VieNeu** (**Reported**, theo [API](../wiki/vieneu-tts-openai-speech-api.md), [Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md), [Docker](../wiki/vieneu-tts-docker-deployment.md)):
- Bind `127.0.0.1` trong pod. Nếu phải lộ ra ngoài thì đặt `VIENEU_API_KEY`. Docker profile mặc định `HOST=0.0.0.0`.
- `VIENEU_MAX_STREAMS` bằng số stream **đồng thời** đo được, không bằng số user. Mỗi slot dư cộng khoảng 2.5 ms vào mọi lần gọi codec. Một user giữ stream khoảng 20–35% thời gian, nên 16 stream tương ứng khoảng 45–80 user đang hoạt động (ước lượng của tác giả).
- Có `VIENEU_QUEUE` và `VIENEU_QUEUE_TIMEOUT` (mặc định 10 s). Khi quá tải trả 429 kèm `Retry-After`.
- Server tự warmup khoảng 12 s. Chỉ nhận traffic khi `/health` trả `ok`. `/health` trả 503 khi scheduler GPU chết; scheduler không tự phục hồi, nên container phải được restart.
- GPU hạ clock sau khoảng 2 s rảnh (đo được 118 ms → 403 ms). Phải khóa clock ở host (§9.7). Giữ GPU nóng từ trong process không có tác dụng.
- Watermark Perth bật mặc định. Bật hay tắt là quyết định chính sách, ghi trong config.
- Giọng clone đăng ký qua `POST /v1/voices` chỉ sống trong bộ nhớ process. tts-service phải **đăng ký lại sau mỗi lần sidecar khởi động**, lấy từ voice registry, trước khi báo ready. Trùng tên preset trả 409.
- `mp3` và `opus` trả 400. `speed` và `instructions` bị bỏ qua.

**Voice registry.** `voice_id` là định danh ổn định của sản phẩm. Mỗi `voice_id` ánh xạ sang (engine, preset hoặc reference, vùng, scope lexicon, tham số sampling cố định).
- Reference clone lưu ngoài repo, kèm bản ghi consent và thời hạn lưu.
- Log chỉ ghi `voice_id`, không ghi đường dẫn hay embedding.
- Session được pin một `voice_id` và một engine. Không đổi giọng giữa chừng một utterance (§9.4).

**Fixed-phrase cache.** Các câu đệm, câu hỏi lại và câu báo lỗi được tổng hợp sẵn lúc khởi động bằng đúng `voice_id` (`SynthesizePhrase`), cache theo `(voice_id, phrase_id, engine_version)`. Khi engine lỗi vẫn phát được các câu này (§9.4).

**Cadence.** Mặc định mỗi generation chỉ có một request engine đang chạy. Request cho mệnh đề kế tiếp được gửi khi audio của mệnh đề trước đã **nhận** xong (không cần chờ phát xong). Vì RTF < 1 nên khe hở được che. Đo `inter_chunk_gap_ms` trước khi bật prefetch hai request.

### 5.7 Orchestrator: session runtime, LLM và history

#### 5.7.1 Mô hình actor

Mỗi session có các thành phần sau (theo Chương 17–18, **Synthesis**):

- `SessionActor`: một task đọc một inbox, xử lý tuần tự. Giữa lúc đọc và lúc ghi trạng thái không có `await`. Inbox control không bao giờ bỏ phần tử.
- `transport_reader`: chỉ đẩy frame vào uplink queue (drop-oldest, có đánh dấu gap).
- `vad_consumer`: reblock, chạy VAD, gửi sự kiện `vad.*` vào inbox. Gọi Smart Turn qua executor.
- `response scope` (TaskGroup) cho mỗi generation: LLM stream, stream gRPC tới tts-service, buffer `held`. Hủy cả scope một lần.
- `send_loop` / pacer: nơi duy nhất ghi ra transport. Kiểm generation **nguyên tử** ngay trước khi gửi. Pacing theo lịch tuyệt đối. Có credit theo played offset.
- `lag_monitor` cho mỗi process.

#### 5.7.2 Vòng đời response

```text
SPECULATIVE ──commit(turn, rev)──► COMMITTED ──audio đầu ra client──► RELEASED ──► DONE
     │                                 │                                 │
     └─reopen/cancel──► DISCARDED      └─────cancel/fail──► CANCELLED/FAILED ◄─┘
```

- `generation_id` tăng đơn điệu trong suốt session, không reset theo lượt. Cancel cũng làm tăng. Cancel khi không có response nào đang active là no-op.
- Buffer `held[gen]` giữ text và audio đã sinh trước commit. Khi commit thì thả ra. Khi reopen thì bỏ.

#### 5.7.3 Mức speculation

Chọn bằng config `speculation_level`. Mặc định L1. Lên L2 **sau PoC**, khi đã đo được tỷ lệ lượt bị giới hạn bởi gate và tỷ lệ reopen (Chương 20).

| Mức | ASR | LLM | TTS | Ảnh hưởng tới v2v (§8.1) | Chi phí |
|---|---|---|---|---|---|
| L0 commit cứng | Sau commit | Sau commit | Sau commit | ASR + LLM + TTS cộng nối tiếp | Thấp nhất. Dùng để debug hoặc cho telephony |
| **L1** (mặc định) | Tại soft-end | Speculative, text giữ trong `held` | Mở stream lúc commit, flush text đã giữ | `max(hold, ASR + LLM→mệnh đề đầu)` cộng TTS | Mỗi reopen tốn một inference LLM |
| L2 | Tại soft-end | Speculative | Speculative cho mệnh đề đầu (`Start.speculative=true`), audio giữ trong `held` | `max(hold, ASR + LLM + TTS)` | Tốn thêm slot TTS cho mỗi reopen. Stream speculative có độ ưu tiên thấp và bị từ chối trước khi tải cao |

#### 5.7.4 LLM client

- Adapter chuẩn hóa SSE (Chat Completions hoặc Responses) thành `LLMEvent` nội bộ: `delta`, `done(finish_reason, usage)`, `error`.
- Map tham số theo backend: tắt thinking (`enable_thinking=false` hoặc `reasoning_effort`, chọn theo server), `max_tokens` làm chặn an toàn (không dùng để giữ câu ngắn), `include_usage`.
- Bốn loại timeout (connect, TTFT, inter-token, tổng), đặt dưới một deadline tuyệt đối cho mỗi response. Tiêu thụ stream bên trong `aclosing`. Lỗi được chuyển thành event `response.failed` gửi vào inbox, không làm chết session.
- **Không tự retry** sau khi đã nhận token đầu. Trước token đầu, chỉ retry nếu còn trong deadline.
- Hủy bằng cách đóng stream. Endpoint LLM phải giải phóng compute khi client đóng stream (R6, deployment gate).
- System prompt cho văn nói lấy từ spec §3.2. Phần tĩnh đặt đầu để tận dụng prefix cache. Không chèn timestamp hay `session_id` vào đầu prompt.
- Không dùng LLM proxy của HF s2s. Không có lời gọi LLM ẩn: tóm tắt history là một job tường minh, chạy giữa các lượt, có log và metric.

#### 5.7.5 History

- Mỗi `text.chunk` nhận từ tts-service được lưu cùng bảng `chunk_id → [mẫu đầu, mẫu cuối)` trên timeline downlink.
- Khi response DONE: history lưu nối các `display_text`.
- Khi bị ngắt: chờ played offset (§7.3), rồi lưu `played_display_prefix` theo cách **bảo thủ**. Segment đã bị viết lại (số, tiền, ngày) chỉ được tính khi đã phát hết. Sau đó thêm tag `[bị ngắt]`.
- Khi reopen: message user cũ bị thay bằng transcript gộp. Assistant dở dang bị bỏ.

#### 5.7.6 Tool (hook cho P3)

Tool chỉ chạy sau commit, và sau khi người dùng xác nhận bằng lời nếu tool có side effect. Mỗi lần gọi có idempotency key `(session_id, turn_id, revision, tool_call_index)`. Kiểm `generation_id` ngay trước khi chạy. Không coi mọi "ừ", "vâng" là backchannel trong luồng xác nhận.

### 5.8 Runtime và cách ly dependency

| Process | Dependency chính | Ghi chú (**Synthesis**) |
|---|---|---|
| orchestrator | Python asyncio (hoặc ngôn ngữ khác), onnxruntime CPU, Opus, soxr/libsamplerate, WebRTC stack | Không có torch. Executor riêng cho Smart Turn, có semaphore |
| asr-service API | gRPC, adapter client | Mỏng, có thể chung image cho mọi engine |
| asr engine sidecar | vLLM + `qwen-asr` / NeMo-Speech.cpp / CTranslate2 / sherpa-onnx | Mỗi engine một image. Pin version và checksum. GGUF giữa các runtime không thay thế cho nhau được |
| tts-service API/bridge | gRPC, VietNormalizer, lexicon, soxr, watermark | Thuần Python |
| tts engine sidecar | Image VieNeu `api-gpu` / Python cho VoxCPM2 / SGLang-Omni | Mỗi engine một image |

Mọi việc nặng chạy ngoài event loop. Mỗi model có executor riêng. Không có `to_thread(f)` nào trả generator rồi lặp trên loop (Chương 18 §A).

---

## 6. Thay thế ASR và TTS

### 6.1 Cơ chế

| Cơ chế | Mô tả (**Synthesis**) |
|---|---|
| Hợp đồng cố định | `asr.v1` và `tts.v1` (§7.6, §7.7). Thay đổi không tương thích ngược thì tạo `v2`, chạy song song |
| Khai báo năng lực | `Describe()` trả chế độ, partial, ép ngôn ngữ, sample rate, cách hủy, `max_streams`, text contract, license. Orchestrator điều chỉnh hành vi theo đó (ví dụ không có partial thì không bật caption) |
| Adapter SDK | Một interface Python cho mỗi loại: `open_stream`, `recognize`, `synthesize_stream`, `cancel`, `describe`, `health`, `warmup`. Engine mới chỉ cần viết adapter |
| Engine registry | YAML có version trong repo registry (§6.2): endpoint, revision và sha256 của weights, tham số, license, `max_streams` |
| Voice profile | Text policy theo `(engine, voice)`: `max_chars`, `hard_max`, code-switch, vùng, scope lexicon, tag hợp lệ, sampling |
| Định tuyến theo session | Engine được chọn lúc mở session (mặc định hoặc theo thí nghiệm) và **pin** cho tới hết session |
| Conformance suite | Bắt buộc phải qua trước khi engine được vào registry (§6.3) |

### 6.2 Ví dụ registry

```yaml
license_profile: research          # research | commercial; commercial chặn engine có license NC/mâu thuẫn
asr:
  default: qwen3-asr-0.6b          # Chốt sau PoC (R0 so với R1/R2)
  engines:
    qwen3-asr-0.6b:
      adapter: qwen3_asr_vllm
      endpoint: http://127.0.0.1:8101
      model: { repo: Qwen/Qwen3-ASR-0.6B, revision: <commit>, sha256: <...> }
      language: vi
      modes: [turn_final]
      license: apache-2.0
      limits: { max_inflight: 4, queue: 8, max_turn_s: 30 }
    nemotron-3.5:
      adapter: nemo_speech_cpp
      endpoint: http://127.0.0.1:8102           # WS realtime ở P2
      language: vi-VN                            # TBD theo R1 của spec
      modes: [turn_final]                        # native_stream sau khi qua gate
      license: openmdw-1.1                       # cần legal review
tts:
  default: vieneu-v3-turbo
  engines:
    vieneu-v3-turbo:
      adapter: openai_speech_pcm
      endpoint: http://127.0.0.1:8000/v1/audio/speech
      native_sample_rate: 48000
      max_streams: 8                             # Chốt sau PoC; = VIENEU_MAX_STREAMS
      text_contract: { max_chars: 256, codeswitch: true, ignored: [speed, instructions] }
      license: disputed                          # FAQ Apache vs roadmap personal use
  voices:
    vi-north-01: { engine: vieneu-v3-turbo, preset: <từ list_preset_voices()>, region: north,
                   lexicon_scope: [common, vieneu], text_policy: { hard_max: 200, first_min: 25 } }
    vi-south-01: { engine: vieneu-v3-turbo, preset: <...>, region: south, lexicon_scope: [common, vieneu] }
experiments:
  - name: asr-1.7b-canary
    component: asr
    split: { qwen3-asr-0.6b: 95, qwen3-asr-1.7b: 5 }
    pin: session
```

### 6.3 Conformance suite (bắt buộc)

**ASR** (stub client cộng audio cố định):
- Nhận đúng 16 kHz mono PCM16. Từ chối format sai bằng lỗi có mã.
- Turn chứa toàn im lặng hoặc nhạc thì trả `empty` hoặc `no_speech`, không trả text rác.
- `revision` mới thay revision cũ. Không có final trùng.
- `Finalize` sau đúng một lần thì có final.
- Hủy stream giữa chừng thì giải phóng tài nguyên (đo bằng số stream active).
- Quá tải trả `RESOURCE_EXHAUSTED` kèm `retry_after_ms`.
- Ép `vi` có tác dụng.
- Transcript rỗng hoặc lặp trên audio dài thì bị gắn cờ. Kiểm này cần cho các bản quantized.

**TTS:**
- Fuzz chia token (L2): đầu ra của chunker giống nhau với mọi cách chia, kể cả chia từng ký tự.
- Không chunk nào vượt `max_chars`. Không cắt trong số, tiền, giờ, URL.
- Không có `<think>`, markdown hay emoji nào tới engine.
- `sample_offset` và `seq` tăng đơn điệu. Rate và số kênh khớp `audio.start`.
- Hủy giữa chunk thì không còn chunk nào của generation đó. Slot của engine về 0 trong khoảng thời gian X (đo).
- 429 của engine được chuyển thành `RESOURCE_EXHAUSTED`.
- Chunk có `spoken_text` rỗng thì không gọi engine.
- Mỗi `text.chunk` có `normalizer_version` và `lexicon_version`.
- Golden L1 của normalizer đạt 100%.

### 6.4 Quy trình đưa engine mới vào

| Bước | Nội dung | Điều kiện qua |
|---|---|---|
| 1. Offline | ASR: corpus tiếng Việt (§10 mục 1), cùng normalizer chấm điểm. TTS: tập nghe L3 (150–300 prompt) cộng TTFA/RTF dưới tải | Tốt hơn hoặc bằng baseline ở metric chính; không thua ở exact-match entity (ASR) hay lỗi thanh điệu (TTS); qua license gate |
| 2. Conformance | §6.3 | 100% |
| 3. Shadow (chỉ ASR) | Engine mới chạy song song trên cùng audio lượt. Chỉ ghi metric, không ảnh hưởng hội thoại. Kết quả transcript chỉ lưu trong corpus opt-in | Không làm tăng latency của engine chính. Có khác biệt thì đem đi review |
| 4. Canary | 1–5% session, pin theo session | SLO §8.2 không xấu đi; tỷ lệ lỗi và 429 không tăng |
| 5. Promote / rollback | Đổi `default` trong registry | Rollback chỉ là revert một commit config |

TTS không có shadow trực tiếp, vì tổng hợp hai lần làm tốn GPU. Thay vào đó dùng tập nghe offline cộng canary.

### 6.5 Cấu hình engine theo kịch bản

Bảng này thay cho các "Profile A–F" của v1. Profile giờ chỉ là một bộ registry. **Synthesis**.

| Kịch bản | ASR | TTS | Chế độ | Ghi chú |
|---|---|---|---|---|
| **v1 mặc định** (1×24 GB, research) | Qwen3-ASR 0.6B/1.7B, turn_final | VieNeu v3 Turbo | L1 | Theo kết quả PoC |
| Cần caption hoặc speculation trên partial | Nemotron 3.5 stream 160/320 ms | VieNeu | L1/L2 | Profile B cũ. Gate: R1, WS adapter |
| Lỗi số, tên, phủ định cao | Nemotron partial cộng final-pass Qwen 1.7B (GPU) hoặc Gipformer 1.5 (CPU) | VieNeu | two_pass | Profile D cũ. Chỉ bật cho critical span |
| CPU/edge | Gipformer 1.5 int8 hoặc Nemotron Q8 (NeMo-Speech.cpp CPU) | VieNeu ONNX / Supertonic 3 / Kokoro vi | L0/L1 | VieNeu CPU fp32 chạy được 1 stream, int8 chạy được 2 stream nếu có VNNI (**Reported**) |
| `license_profile=commercial` | Qwen3-ASR (Apache), Whisper (MIT), PhoWhisper (BSD-3), ChunkFormer RNNT (CC-BY-4.0); Nemotron sau khi qua legal | VoxCPM2 (Apache), MOSS Local; VieNeu sau khi giải quyết mâu thuẫn license | — | Loại ZipFormer NC-ND, ChunkFormer CTC, OmniVoice/G-OmniVoice, Higgs/Fish, Gwen (quyền dữ liệu) |

### 6.6 Khi đổi engine phải làm lại những gì

- **ASR:** chạy lại corpus và exact-match entity. Kiểm định dạng output (dấu câu, chữ hoa, số viết bằng chữ hay chữ số) vì LLM nhạy với các thứ này. Kiểm lại filter và `quality_flags`. Đo capacity.
- **TTS:** chạy lại toàn bộ L3 cho mọi mục lexicon. Viết lại voice profile (vùng, code-switch, `max_chars`). Đổi G2P của engine là lý do chạy lại tập nghe. Tổng hợp lại fixed-phrase cache. Đo `max_streams`, TTFA và RTF dưới tải chung với ASR. Nếu rate gốc khác 48 kHz thì xác nhận chỉ resample một lần.

---

## 7. Hợp đồng điều khiển và API

### 7.1 Audio ingress và audio contract theo từng đoạn

| Đoạn | Định dạng | Ai resample |
|---|---|---|
| Client → orchestrator | Opus (WebRTC) hoặc PCM16 16 kHz mono frame 20 ms (WS dev) | — |
| Trong orchestrator | f32 16 kHz mono, ring ≥ 10 s, chỉ số mẫu tuyệt đối | Orchestrator, một lần (48 → 16 kHz) |
| Orchestrator → asr-service | PCM16 16 kHz mono, frame mang `sample_index` | — |
| Orchestrator → tts-service | Text UTF-8 (delta) | — |
| tts-service → orchestrator | PCM s16le, rate lấy từ `Start.output` (mặc định 48 kHz) mono, chunk mang `sample_offset` | tts-service, tối đa một lần (rate gốc → rate yêu cầu) |
| Orchestrator → client | Opus 48 kHz (WebRTC) hoặc PCM 48 kHz có header (WS) | — |

**Policy khi có gap ở uplink** (Chương 16, **Synthesis**):
- Mất ngắn (< 100 ms): chèn im lặng đúng độ dài và gửi `ingress.gap`.
- Mất dài (≥ khoảng 500 ms) giữa lượt: `turn.invalidated`, rồi hỏi lại.
- Frame đến muộn hoặc trùng: bỏ.
- Có metric `uplink_dropped`.

**Vòng đời turn buffer:** OPEN → HOLD (từ soft-end tới khi có final hoặc final-pass) → RELEASE. Trần 30 s mỗi lượt, cấu hình được. Turn buffer là dữ liệu nhạy cảm và được giải phóng đúng hạn.

### 7.2 Định danh và event schema

**Định danh:**

| ID | Phạm vi | Quy tắc |
|---|---|---|
| `session_id` | Một kết nối | Edge cấp |
| `turn_id` | Lượt của user | Tăng khi mở lượt mới |
| `revision` | Trong một lượt | Tăng khi reopen |
| `generation_id` | Cả session | Tăng đơn điệu khi tạo response và khi cancel. Không reset |
| `chunk_id` | Trong một generation | Do tts-service cấp, tăng đơn điệu |
| `sequence` | Theo `(generation_id)` cho audio downlink | Client kiểm cặp `(generation_id, sequence)` |

Mọi event mang thêm `t_mono_ns` (đồng hồ đơn điệu của host phát event). Event audio mang chỉ số mẫu.

**Event giữa client và orchestrator (DataChannel hoặc WS text):**

```text
↓ session.ready(session_id, uplink_format, downlink_format, capabilities)
↓ turn.state(turn_id, revision, state)                 # tùy chọn, cho UI
↓ caption.user(turn_id, revision, text, final)          # chỉ khi ASR có partial
↓ response.created(generation_id, turn_id, revision)
↓ caption.bot(generation_id, chunk_id, display_text)    # gửi lúc audio của chunk bắt đầu phát
↓ audio.end(generation_id, n_samples)
↓ client.clear(cancelled_generation_id)                 # client nâng floor ≥ id này
↓ response.done(generation_id, status, reason)          # completed | cancelled | failed
↓ error(code, retry_after_ms?)                          # overloaded | auth | format | timeout
↑ audio.played(generation_id, played_sample_offset)     # WS: chính xác; WebRTC: ước lượng (§7.3)
↑ audio.stats(jitter_buffer_ms, output_latency_ms, underruns)
↑ response.cancel()                                     # nút dừng trên UI
↑ session.end(reason)
```

**Event nội bộ trong inbox của actor:** `vad.speech_start(sample)`, `vad.speech_end(sample)`, `smart_turn.result(turn_id, revision, prob)`, `timer.fired(kind, turn_id, revision)`, `asr.partial(...)`, `asr.final(turn_id, revision, text, flags, audio_range)`, `llm.delta/done/failed(generation_id, ...)`, `tts.text_chunk/audio/done/failed(generation_id, ...)`, `ingress.gap(...)`, `turn.invalidated(...)`, `client.*`.

**Quy tắc:**
- Event có `generation_id` nhỏ hơn generation hiện tại thì bị bỏ ở mọi chặng.
- Partial là latest-only, nên `sequence` của partial có lỗ là bình thường.
- `turn.commit(turn_id, revision, speech_end_sample)` chỉ phát một lần cho mỗi lượt.

### 7.3 Barge-in và cancellation

**Trình tự trong actor.** Tất cả chạy đồng bộ, không có `await` xen giữa bước 1 và bước 2 (Chương 17–18):

1. Tăng `generation_id` (`cancelled = old`).
2. Đẩy `client.clear(old)` vào hàng ưu tiên. Pacer ngừng gửi audio của `old` ngay lập tức. Fade-out khoảng 5–10 ms tại điểm cắt (**Synthesis**).
3. Set cờ stop và hủy response scope: đóng stream LLM, hủy stream gRPC tới tts-service (tts-service đóng request engine, VieNeu nhả slot), hủy `Recognize` đang chạy nếu có.
4. Mở lượt mới. Turn buffer bắt đầu từ đầu đoạn nói trừ pre-roll.
5. Phát `response.done(old, cancelled, reason)`.
6. **Sau đó**, khi có played offset, cắt history (§5.7.5). Bước này không làm trong lúc ngắt.

**Played offset:**
- WebSocket: client đếm mẫu đã render trong AudioWorklet và báo `audio.played`. Giá trị này chính xác.
- WebRTC: client không chặn được audio trong jitter buffer. Server ước lượng `played ≈ sent_samples − (jitter_buffer_ms + output_latency_ms) × rate` từ `audio.stats` (WebRTC `getStats`), làm tròn về phía bảo thủ. Cách này là **Synthesis** và phải kiểm trên trình duyệt đích. Phần đuôi audio đã nằm trong jitter buffer (vài chục ms) không flush được từ xa và được tính vào T_silence.

**Gate chống ngắt nhầm.** Tất cả là tham số, **Chốt sau PoC** trên dữ liệu tiếng Việt:

| Cơ chế | Khởi điểm | Ghi chú |
|---|---|---|
| Duration gate | Hai giá trị khởi điểm mâu thuẫn: 100–200 ms (ưu tiên nhạy) và threshold 0.7 cộng 300–500 ms (ưu tiên chống ồn) (**Reported**, §11) | Đo đánh đổi: 150 ms dễ ngắt nhầm vì "ừ"; 400 ms làm gate chiếm phần lớn T_silence |
| Backchannel ba kết cục | Ngắt / ghi nhận không ngắt / bỏ qua | Không mặc định bỏ qua "ừ, vâng, ok" |
| Speaker lock (P2) | Cosine ECAPA/CAM++ so với embedding của user, khoảng 0.5–0.6, cần calibrate | Speaker lock không phải xác thực |
| Kiểm echo (P2) | Quick-ASR ≥ 2 từ và không trùng câu bot đang phát | |

**Đo** (bắt buộc, kèm `(turn, rev, gen)` và lý do cancel):
- **T_silence:** từ lúc user bắt đầu nói tới lúc âm thanh bot dừng, đo ở client.
- **T_release:** từ lúc cancel tới lúc LLM và TTS hết compute, đo ở server qua slot VieNeu và metric của LLM.
- Tỷ lệ ngắt đúng, ngắt trượt, ngắt nhầm.

### 7.4 Vòng điều khiển (minh họa, **Synthesis**)

Pseudo-code dưới đây đã sửa các lỗi mà Chương 17–19 chỉ ra trong pseudo-code của v1: owner một inbox, hold output speculative, timer có token, guard ở send loop, history chờ played offset, cầu text → speech nằm trong tts-service.

```python
class SessionActor:                      # một task, một inbox; không await giữa đọc và ghi state
    async def run(self):
        async for ev in self.inbox:
            match ev:
                case VadSpeechEnd(sample):
                    if self.turn.state == LISTENING:
                        self.turn.soft_end(sample)
                        self.executors.smart_turn.submit(self.ring.window_8s(), token=self.turn.token())
                        self.start_speculative()             # L1/L2: ASR (+LLM) ngay tại soft-end
                case VadSpeechStart(sample):
                    if self.response_playing() and self.barge_gate.ok(sample):
                        self.cancel_response("barge_in")
                    elif self.turn.state in (SOFT_ENDED, ANSWERING) and not self.committed():
                        self.turn.reopen(sample)             # revision++, timer cũ tự vô hiệu
                        self.discard_speculative()
                case SmartTurnResult(token, complete):
                    if token == self.turn.token():
                        self.timers.arm("commit", GRACE if complete else MAX_WAIT, token)
                case TimerFired("commit", token) if token == self.turn.token():
                    self.commit()                            # điểm commit DUY NHẤT
                case AsrFinal(turn_id, rev, text, flags) if (turn_id, rev) == self.turn.key():
                    verdict = self.validity.check(text, flags, self.turn)
                    if verdict.ok: self.resp.start_llm(self.history, text)   # vẫn SPECULATIVE
                    else: self.plan_fallback(verdict)                         # hỏi lại từ cache
                case TtsTextChunk(gid, chunk) if gid == self.gen:
                    self.resp.record_chunk(chunk)            # display_text + segments
                case ClientPlayed(gid, offset):
                    self.history.truncate_if_cancelled(gid, offset)
                case LlmFailed(gid) | TtsFailed(gid) if gid == self.gen:
                    self.play_fixed_phrase("loi_tam_thoi")

    def commit(self):
        self.turn.commit()
        self.resp.mark_committed()               # L1: mở stream TTS, flush text đã held
        self.pacer.release(self.gen)             # L2: thả audio đã held

    def cancel_response(self, reason):
        if not self.resp.active(): return        # no-op, không tăng generation
        old, self.gen = self.gen, self.gen + 1   # tăng trước mọi await
        self.pacer.clear(old)                    # hàng ưu tiên: client.clear(old) + ngừng gửi
        self.resp.scope_cancel(old)              # đóng LLM + gRPC TTS; cờ stop
        self.emit(ResponseDone(old, "cancelled", reason))

# pacer (task duy nhất ghi ra transport)
async def send_loop(self):
    async for frame in self.schedule.absolute(20 * MS):
        chunk = self.queue.peek()
        if chunk and chunk.gid == self.actor.gen and self.released(chunk.gid):   # kiểm nguyên tử
            self.transport.send_audio(self.queue.pop())
```

### 7.5 Diarization

Agent một người dùng **không** đặt diarizer trong critical path. Khi có nhiều người nói, ưu tiên mỗi participant một track riêng (SFU). Nếu chỉ có audio trộn, thử [Nemotron 3 Diarization](../wiki/nemotron-3-diarization.md) (tối đa 8 speaker, **Reported**). Hiện chưa có DER cho tiếng Việt.

### 7.6 ASR service API (`asr.v1`)

```proto
syntax = "proto3";
package asr.v1;

service Asr {
  rpc Describe(DescribeRequest) returns (AsrCapabilities);
  rpc StreamingRecognize(stream AsrClientMsg) returns (stream AsrServerMsg); // native/buffered stream
  rpc Recognize(RecognizeRequest) returns (RecognizeResponse);               // turn_final / final-pass
}

message AsrCapabilities {
  string engine_id = 1; string engine_version = 2;
  repeated string modes = 3;            // "turn_final" | "native_stream" | "buffered_stream"
  bool partials = 4; bool stable_prefix = 5;
  bool language_forcing = 6; repeated string languages = 7;
  bool context_biasing = 8; bool punctuation = 9; bool itn = 10;
  bool confidence_calibrated = 11;      // false ⇒ orchestrator coi confidence = unknown
  repeated int32 input_sample_rates = 12;
  int32 max_inflight = 13; int32 max_turn_seconds = 14; string license = 15;
}

message StreamConfig { string session_id = 1; string language = 2; int32 sample_rate = 3;
                       repeated string context_phrases = 4; string mode = 5; }
message AudioFrame   { uint64 sample_index = 1; bytes pcm16 = 2; }
message Finalize     { uint64 turn_id = 1; uint32 revision = 2; uint64 end_sample = 3; }
message AsrClientMsg { oneof msg { StreamConfig config = 1; AudioFrame audio = 2; Finalize finalize = 3; } }

message Partial { uint64 turn_id = 1; uint32 revision = 2; string text = 3;
                  int32 stable_prefix_chars = 4; uint64 start_sample = 5; uint64 end_sample = 6; }
message Final   { uint64 turn_id = 1; uint32 revision = 2; string text = 3; string language = 4;
                  repeated string quality_flags = 5; uint64 start_sample = 6; uint64 end_sample = 7;
                  Timings timings = 8; }       // queue_ms, compute_ms (không chứa nội dung)
message AsrServerMsg { oneof msg { Partial partial = 1; Final final = 2; Error error = 3; } }

message RecognizeRequest { string session_id = 1; uint64 turn_id = 2; uint32 revision = 3;
                           bytes pcm16 = 4; int32 sample_rate = 5; string language = 6;
                           repeated string context_phrases = 7; }
message RecognizeResponse { Final final = 1; }
message Error { string code = 1; uint32 retry_after_ms = 2; }   // RESOURCE_EXHAUSTED, INVALID_AUDIO, ...
```

Ngữ nghĩa:
- Hủy một RPC (gRPC cancel) là cancel. Service phải dừng decode hoặc bỏ kết quả và giải phóng slot.
- Deadline do orchestrator đặt theo ngân sách của lượt.
- Final của `(turn_id, revision)` cũ đến muộn sẽ bị orchestrator bỏ.

### 7.7 TTS service API (`tts.v1`)

```proto
syntax = "proto3";
package tts.v1;

service Tts {
  rpc Describe(DescribeRequest) returns (TtsCapabilities);
  rpc ListVoices(ListVoicesRequest) returns (VoiceList);
  rpc Synthesize(stream TtsClientMsg) returns (stream TtsServerMsg);   // 1 stream = 1 generation
  rpc SynthesizePhrase(PhraseRequest) returns (stream AudioChunk);     // câu cố định, cache được
}

message TtsCapabilities {
  string engine_id = 1; string engine_version = 2;
  string streaming = 3;               // "frame" | "chunk" | "full_waveform"
  int32 native_sample_rate = 4; repeated int32 output_sample_rates = 5; int32 channels = 6;
  string cancel = 7;                  // "server" | "close_connection" | "none"
  int32 max_streams = 8;
  TextContract text_contract = 9;     // max_chars, codeswitch, case_sensitive, ignored_params, inline_tags
  string normalizer_version = 10; string lexicon_version = 11; string license = 12;
}

message Start { string session_id = 1; uint64 turn_id = 2; uint32 revision = 3; uint64 generation_id = 4;
                string voice_id = 5; int32 sample_rate = 6;   // mặc định 48000, PCM16 mono
                bool speculative = 7;                         // L2: ưu tiên thấp, có thể bị từ chối
                map<string,string> policy_overrides = 8; }
message TextDelta { uint32 seq = 1; string text = 2; }
message TextEnd {}
message Cancel { string reason = 1; }
message TtsClientMsg { oneof msg { Start start = 1; TextDelta delta = 2; TextEnd end = 3; Cancel cancel = 4; } }

message Segment { uint32 display_start = 1; uint32 display_end = 2;
                  uint32 spoken_start = 3; uint32 spoken_end = 4; bool rewritten = 5; }
message TextChunk { uint32 chunk_id = 1; string display_text = 2; string spoken_text = 3;
                    repeated Segment segments = 4; string kind = 5;   // clause | first_comma | hard_max | final
                    repeated string warnings = 6; string normalizer_version = 7; string lexicon_version = 8; }
message AudioChunk { uint32 chunk_id = 1; uint32 seq = 2; uint64 sample_offset = 3; bytes pcm16 = 4; }
message ChunkEnd { uint32 chunk_id = 1; uint64 n_samples = 2; uint32 ttfa_ms = 3; }
message Done { string status = 1; uint32 chars = 2; uint64 audio_samples = 3; }
message TtsServerMsg { oneof msg { TextChunk text_chunk = 1; AudioChunk audio = 2; ChunkEnd chunk_end = 3;
                                   Done done = 4; Error error = 5; } }
message Error { string code = 1; uint32 retry_after_ms = 2; }
```

Ngữ nghĩa:
- Mỗi stream ứng với đúng một `generation_id`. Hủy stream là cancel, và bridge của generation đó bị vứt bỏ, **không** flush.
- `sample_offset` tính trên timeline của generation. Orchestrator dùng nó để dựng bảng `chunk_id → [mẫu đầu, mẫu cuối)`.
- `spoken_text` là nội dung. Nó chỉ được gửi cho orchestrator (để debug opt-in) và không bao giờ được ghi vào log vận hành.
- Từ chối do quá tải trả `RESOURCE_EXHAUSTED` kèm `retry_after_ms`. Stream `speculative` bị từ chối trước stream thường.

---

## 8. Latency: critical path, SLO, đòn bẩy, đo lường

### 8.1 Critical path và output gate

```text
mẫu speech cuối của user (chỉ số mẫu)
  → soft-end (VAD im ≥ min_silence)
  → [grace / incomplete delay / max wait]   ‖   ASR final → LLM tới mệnh đề đầu [→ TTS mệnh đề đầu nếu L2]
  → turn.commit (gate mở)
  → TTS first byte (nếu L1) → pacer → Opus → mạng/jitter → client: mẫu nghe được đầu tiên
```

Công thức (**Synthesis** từ Reported, spec §1):

```text
L1: v2v ≈ (cuối tiếng → soft-end) + max(hold, ASR + LLM→mệnh đề đầu) + TTS TTFA + transport/playback
L2: v2v ≈ (cuối tiếng → soft-end) + max(hold, ASR + LLM→mệnh đề đầu + TTS TTFA) + transport/playback
```

Hệ quả:
- Với default HF (hold 800 ms cho lượt complete, tới 2 s cho lượt incomplete), lượt complete khó xuống dưới khoảng 0.9 s, dù model nhanh tới đâu.
- Nếu ASR và LLM đã nằm gọn trong grace thì đổi sang model nhanh hơn được 0 ms.
- Phải đo **tỷ lệ lượt bị giới hạn bởi gate** và **slack** trước khi chọn đòn bẩy (Chương 20).
- Join log theo `(turn_id, revision, generation_id, chunk_id)`, không theo thứ tự lượt.

### 8.2 SLO

Ngân sách tham khảo của report (0.7–1.2 s và 0.95–2.9 s, **Reported**) **không** phải mục tiêu. Bảng đó không có dòng hold và không có dòng playback.

| SLO | Mục tiêu | Nguồn / nhãn |
|---|---|---|
| v2v D1 (client), lượt complete | P50 ≤ 1.5 s, P95 ≤ 2.5 s, mục tiêu mềm | spec §1 |
| v2v D1, báo riêng theo loại lượt | complete / incomplete-reopen / sau barge-in / sau idle (GPU nguội) | spec §5.3 |
| T_silence (barge-in) | Đặt sau PoC. Khởi điểm: duration gate cộng ≤ 200 ms | **Synthesis** |
| Audio cũ phát sau `clear` | 0 ms ngoài phần đuôi trong jitter buffer | Chương 17 |
| TTS TTFA dưới tải | P95 ≤ 250–400 ms | Tài liệu TTS (**Synthesis**) |
| TTS RTF mỗi stream dưới tải | P95 ≤ 0.7 | Tài liệu TTS. VieNeu khuyến nghị giảm `max_streams` nếu RTF > 0.8 |
| Loop lag của orchestrator | P99 < 5 ms ở số session mục tiêu | Chương 18 |
| False-interruption tiếng Việt | ≤ 10%; vượt thì thay hoặc fine-tune turn detector | **Reported** trigger |
| False cutoff | Báo **cùng** v2v; không hạ hold khi chưa đo chỉ số này | Chương 20 |

### 8.3 Đòn bẩy theo thứ tự ưu tiên

Thứ tự theo spec §8, chỉnh lại cho production (**Synthesis**):

1. Bảo đảm LLM → TTS theo mệnh đề. Chunker nằm trong tts-service, nhận delta ngay khi orchestrator nhận.
2. Khóa clock GPU ở host. Đặt `max_streams` đúng tải. Warmup xong mới báo readiness. Chunk đầu của mỗi lượt luôn đến sau một khoảng rảnh > 2 s.
3. A/B grace có kiểm soát (800 → 600 → 400 ms), đo kèm false cutoff và reopen.
4. Dùng L2 (TTS speculative) khi tỷ lệ lượt bị giới hạn bởi gate cao và tỷ lệ reopen thấp.
5. Tune pre-buffer và `MAX_LEAD` của pacer theo jitter và underrun đo được.
6. Đo LLM tới mệnh đề đầu với context dài. Dùng prefix cache.
7. Streaming ASR, chỉ khi timeline cho thấy bị giới hạn bởi compute.
8. Cuối cùng mới tối ưu runtime (`torch.compile`, vLLM, …) trên đúng workload hội thoại.

### 8.4 Monitoring theo lượt

**Mốc thời gian** (khớp với tập M1–M12 của Chương 20 §20.7.1). Mỗi mốc ghi `t_mono_ns` và ID:

`speech_end_sample` → `soft_end` → `smart_turn_done` → `asr_request` → `asr_final` → `llm_request` → `llm_first_token` → `first_clause_ready` (tts-service) → `turn_commit` → `tts_first_byte` → `downlink_first_send` → `client_first_audible` → `llm_done` → `response_done(status)`.

Client tự tính D1 từ `speech_end_sample` do server gửi xuống, nên không cần đồng bộ đồng hồ giữa client và server.

**Metric theo service:**

| Service | Metric |
|---|---|
| orchestrator | `hold_ms`, tỷ lệ lượt bị giới hạn bởi gate, slack, tỷ lệ Smart Turn incomplete, số reopen, `speculative_discard`, T_silence, T_release, loop lag, độ sâu, số bỏ và thời gian chờ của mỗi queue, `uplink_dropped`, `downlink_lead_ms`, `client_underrun_total`, `prebuffer_wait_ms` |
| asr-service | queue_ms, compute_ms, endpoint→final theo bucket độ dài lượt, tỷ lệ từng `quality_flags`, `RESOURCE_EXHAUSTED`, số stream active |
| tts-service | `ttfc_ms` (time-to-first-clause), `ttfa_ms`, `inter_chunk_gap_ms` P95, độ dài chunk, `chunk_kind_ratio`, `chunks_per_reply`, `norm_warnings{type}`, `alert_hits`, `spoken_empty_chunks`, slot của engine, 429, RTF |
| LLM client | TTFT, TTFC, tokens/s, cached tokens, `finish_reason`, lỗi theo loại |

---

## 9. Triển khai, capacity và vận hành

### 9.1 Topology

**Một node speech (v1):**

```text
node-speech-01 (1× GPU 24 GB)
  ├─ asr-api            (CPU)  ──localhost── asr-engine-qwen3   (GPU, vLLM)
  ├─ tts-api            (CPU)  ──localhost── tts-engine-vieneu  (GPU, Docker api-gpu)
  ├─ orchestrator ×K    (CPU; WebRTC kết thúc tại đây hoặc ở SFU)
  ├─ edge + coturn      (có thể ở host riêng)
  └─ otel-collector
llm-host (riêng)        ── endpoint OpenAI-compatible (spec Q5)
```

- Bắt đầu bằng Docker Compose. Mỗi model có một owner process. Gateway không load weights.
- Engine sidecar chỉ bind localhost hoặc mạng nội bộ của pod.
- Chỉ edge và TURN được lộ ra ngoài.

### 9.2 GPU và VRAM trên node 24 GB

Số liệu là **Reported** hoặc ước lượng thô, phải đo lại (R5 của spec):

| Thành phần | Ước lượng | Ghi chú |
|---|---|---|
| Qwen3-ASR 0.6B | Weights khoảng 1.2 GB BF16, cộng encoder 180M, cache, workspace | Phải giới hạn tỷ lệ VRAM vLLM được cấp phát trước, nếu không nó chiếm GPU của TTS |
| Qwen3-ASR 1.7B | Weights khoảng 3.4 GB, cộng encoder 300M, cache | |
| VieNeu v3 Turbo | 0.64–0.72 GB (8 stream) đến 0.91–1.10 GB (16 stream), theo harness của tác giả | Report thứ cấp ước 2–3 GB |
| Context CUDA của mỗi process | Phải đo | |
| Smart Turn, VAD | 0 (chạy CPU) | |
| LLM | 0 (ở host khác) | |

VRAM đủ **không có nghĩa là** cadence đủ. Một burst ASR turn-final có thể làm bước codec của TTS chậm lại. Phải đo P99 thời gian một bước TTS khi ASR đang chạy. Nếu cadence vỡ, có ba cách: (a) chuyển final-pass sang CPU (Gipformer), (b) tách GPU theo service, (c) giảm `max_inflight` của ASR.

### 9.3 Scale và mô hình capacity

- **Đơn vị scale** là một node speech: một GPU chạy ASR engine và TTS engine, cộng một pool orchestrator CPU.
- **Capacity của node** là giá trị nhỏ nhất trong ba giới hạn sau (**Synthesis**). Cả ba đều phải đo bằng harness open-loop có khoảng rảnh thật giữa các lượt:
  - TTS: `max_streams` / duty cycle (khoảng 0.2–0.35, **Reported**).
  - ASR: số lượt mỗi giây mà engine chịu được ở P95 endpoint→final mục tiêu.
  - CPU orchestrator: loop lag P99 < 5 ms.
- **Routing:**
  - Edge route session sticky tới orchestrator.
  - Orchestrator gọi asr-api và tts-api qua LB nội bộ theo kiểu least-outstanding.
  - Stream gRPC tự sticky trong suốt vòng đời của nó.
  - Ưu tiên node local (cùng máy) để tránh hop mạng.
- Khi số session tăng, tách GPU theo service trước, rồi mới tính tới Kubernetes hay kiến trúc disaggregated.
- Năng lực Nemotron trên H100 (khoảng 240 stream ở 80 ms, **Reported**) là trần lý thuyết của riêng ASR, không phải của cả pipeline.

### 9.4 Fallback và degradation ladder

| Sự cố | Phát hiện | Hành vi (**Synthesis**) |
|---|---|---|
| TTS 429 / `RESOURCE_EXHAUSTED` | Mã lỗi | Retry ở replica khác trong deadline. Nếu vẫn lỗi, phát câu đệm từ cache ("Anh/chị chờ em một chút"), rồi thử lại **ở mệnh đề mới** |
| TTS engine chết (`/health` 503) | Health, circuit breaker | Breaker mở, route sang replica khác. Nếu không có replica nào thì phát câu báo lỗi từ cache. Container restart |
| Fallback sang engine TTS khác | Registry `fallback:` | Chỉ đổi engine ở ranh giới response, không đổi giữa câu. Đổi luôn voice profile. Ghi vào history kèm nhãn |
| ASR quá tải hoặc timeout | Mã lỗi, deadline | Hỏi lại ("Anh/chị nói lại giúp em được không?") từ cache. Không gọi LLM |
| LLM timeout trước token đầu | Deadline | Retry một lần nếu còn ngân sách. Nếu không, phát câu xin lỗi từ cache. `response.failed` |
| LLM lỗi giữa stream | `error` hoặc `finish_reason=length` | Kết thúc ở ranh giới mệnh đề bằng câu fallback ngắn. Không đọc lại từ đầu |
| Uplink mất dài | Gap ≥ khoảng 500 ms | `turn.invalidated`, hỏi lại |
| Quá tải toàn node | Admission ở edge | Từ chối session mới bằng `error(overloaded)`. Session đang chạy giữ chất lượng |

### 9.5 Privacy và bảo mật

- TLS và xác thực ở edge (token ngắn hạn cho signaling). Mạng nội bộ riêng; nên dùng mTLS giữa các service.
- Port của engine chỉ bind loopback. NeMo-Speech.cpp có route health và playground không cần auth (**Reported**). VieNeu phải có API key nếu không bind loopback.
- Không dùng STUN/TURN công cộng. Không dùng LLM proxy của HF s2s.
- Giới hạn theo session: thời lượng session, độ dài lượt (30 s), tốc độ event trên DataChannel, kích thước message.
- Reference clone chỉ được nạp qua pipeline quản trị, có bản ghi consent. Client không được trỏ tới URL hay path reference. Quyền với preset voice không bao gồm reference do người dùng cung cấp (**Reported**).
- Log mặc định content-free: độ dài, loại, version, ID. Transcript, `display_text`/`spoken_text`, audio và speaker embedding chỉ vào **corpus opt-in** có kiểm soát truy cập, retention và consent. `lexicon_hits` chỉ ghi id của mục, không ghi term.
- Turn buffer và embedding giải phóng đúng hạn. Không log payload trong handler exception.
- Watermark (VieNeu Perth) là một quyết định chính sách và được ghi vào config.

### 9.6 Admission, queue và backpressure

Có ba tầng admission (Chương 18):
- Session, ở edge.
- Model, bằng semaphore và hàng đợi của engine.
- Request, bằng deadline.

| Cạnh | Giới hạn | Khi đầy | Metric |
|---|---|---|---|
| Transport → uplink | Vài trăm ms audio | Drop-oldest, ghi `ingress.gap` | `uplink_dropped`, độ sâu |
| Partial ASR → actor | 1 | Latest-only | Số bị thay |
| Final ASR → actor | Nhỏ | Không bỏ (control) | Thời gian chờ |
| Control (`clear`, `cancel`, timer) | Không giới hạn trên thực tế, hàng ưu tiên | Không bao giờ bỏ, vượt lên trước audio | — |
| LLM delta → stream TTS | Lookahead 1–2 mệnh đề (credit) | Chặn producer (LLM sinh chậm lại) | Thời gian bị chặn |
| tts-service: hàng engine | 1 request đang chạy cộng 1 mệnh đề chờ cho mỗi generation | Chặn | `inter_chunk_gap_ms` |
| TTS audio → pacer | `MAX_LEAD` 1–2 s audio (**Chốt sau PoC**, phải lớn hơn pre-buffer) | Chặn theo generation. Đọc response engine hết tốc độ vào buffer, **không** giữ slot engine theo tốc độ phát | `downlink_lead_ms` |
| Executor Smart Turn | Semaphore | Bỏ yêu cầu cũ của cùng session (latest-only) | Thời gian chờ executor |

### 9.7 Config, version và runbook host

- **Pin và checksum:** runtime, weights, G2P, voicepack, normalizer, lexicon, image. Pre-stage offline. Registry là nguồn sự thật duy nhất.
- **Host GPU:** khóa clock (`nvidia-smi -lgc …`) và bật persistence mode. Giữ GPU nóng từ trong process không có tác dụng (**Reported**). Driver và CUDA khớp với image.
- **Readiness:** từng service chỉ báo ready sau khi warmup xong. Với tts-service, điều kiện gồm: sidecar `/health` ok, voice đã được đăng ký lại, fixed-phrase cache đã có.
- **Healthcheck:** liveness tách khỏi readiness. Engine có `start_period` (VieNeu GPU 120 s, CPU 180 s, **Reported**).
- **Rollout:** canary theo §6.4. Mỗi lần chỉ đổi một thành phần.

---

## 10. Đánh giá và release gates

Đây là **Synthesis** từ các gate ASR, TTS, control và server trong wiki, cộng các checklist của Chương 16–20.

1. **Corpus ASR:**
   - Giọng Bắc, Trung, Nam.
   - Tên riêng, số, địa chỉ, phủ định, code-switch, lệnh rất ngắn ("không", "dừng").
   - Mic 16 kHz, telephony 8 kHz, far-field.
   - Nhiễu quán café, xe máy, TV ở SNR 0/5/10/20 dB, có và không có denoise. Đoạn chỉ có im lặng hoặc nhạc.
   - Cùng một normalizer chấm điểm. Báo WER/CER, exact-match riêng cho entity, và endpoint→final P50/P95 theo bucket độ dài lượt.
2. **TTS:**
   - L1: golden normalizer, 100% pass.
   - L2: fuzz chunker.
   - L3: 150–300 prompt, blind pairwise/MOS/CMOS với 10–20 người nghe Việt. Có ca riêng cho ranh giới chunk, chunk đầu ngắn, từng mục lexicon và alert. Lưu cả `raw_text` và `spoken_text` cho mỗi prompt.
3. **Turn và barge-in:**
   - Các tình huống: ngập ngừng dài, lệnh ngắn, backchannel, TV nền, echo của bot ở loa ngoài (C2/C4 của spec), user nói đè, ho, gõ phím.
   - Báo false-cutoff, missed/false interrupt, T_silence, T_release.
4. **Tải:**
   - Harness open-loop replay audio theo thời gian thực, có khoảng rảnh 6–20 s.
   - Concurrency 1/4/8/16, cả kiểu đến rải rác lẫn bắt đầu đồng loạt.
   - Warm và cold (GPU nguội).
   - LLM **thật**, chạy chung GPU nếu production cũng chạy chung.
   - Báo đường cong latency theo concurrency.
5. **Contract và replay:**
   - Contract test giữa các service (§6.3).
   - Replay sự kiện: jitter, burst, gap, đảo thứ tự, disconnect/reconnect, backend chậm, 429/503, client chậm, loop bị chiếm.
   - Assert: không có audio cũ; không có final trùng; `sequence` và `revision` đơn điệu; không có hành động trên text chưa commit; không còn task nào sau teardown (`asyncio.all_tasks()`).
   - Soak 1.000 session.
6. **Quyền và bảo mật:**
   - License của runtime, weights, voicepack, lexicon, normalizer và lineage dữ liệu, đối chiếu với `license_profile`.
   - Consent cho reference. Log content-free. Kiểm port nào đang lộ ra ngoài.
7. **Thay engine:** quy trình §6.4 cộng checklist §6.6.

**Điều kiện xong P1:** qua cả 7 gate với cấu hình v1 trên phần cứng đích; đạt SLO §8.2 cho lượt complete; bộ conformance chạy trong CI.

---

## 11. Mâu thuẫn còn mở

Phần này ghi nhận mâu thuẫn, không chọn bên.

| Chủ đề | Bên A | Bên B |
|---|---|---|
| License VieNeu v3 Turbo | Card FAQ: Apache-2.0, preset dùng thương mại được | README Roadmap và report: "on-device, personal use" |
| Cửa sổ kích hoạt barge-in | 100–200 ms (ưu tiên nhạy) | Threshold 0.7 cộng 300–500 ms (chống ồn; reference server dùng 400 ms) |
| Enhancement trước ASR | arXiv 2403.06387: có ích | arXiv 2512.17562, 2603.04710: có hại ở mọi cấu hình đã thử. Không có nghiên cứu nào trên tiếng Việt |
| TEN VAD so với Silero | Vendor TEN: TEN tốt hơn | NOVA-VAD: Silero F1 91.9 so với TEN 69.2. Bảng FireRed: Silero trên TEN |
| Default endpoint | HF s2s: 64 ms cộng reopen 800 ms cộng max wait 2 s | Report: 200–300 ms cộng fallback 1.2–1.5 s |
| Số liệu Smart Turn tiếng Việt | AI report: 81.27% / FP 14.84% / FN 3.88% | Capture v3.2: GPU 82.47 / 9.56 / 7.97; CPU 79.38 / 8.86 / 11.75 |
| Qwen3-ASR-1.7B trên FLEURS-vi | 5.55 (paper) | 6.15 (GGUF Q8_0) và 10.13 (bảng Gipformer). Khác normalizer và runtime |
| G-OmniVoice | Card ghi Apache-2.0 | Base OmniVoice là CC-BY-NC, tokenizer theo license Boson |
| Qwen3-TTS và tiếng Việt | Blueprint dùng `language="vi"` | Card chính thức không có vi. Gwen (finetune) dùng `"Vietnamese"` trong ví dụ |

---

## 12. Lộ trình từ PoC tới production

### 12.1 Các phase

| Phase | Mục tiêu | Nội dung | Điều kiện xong |
|---|---|---|---|
| **P0: PoC** ([spec](spec-poc-speech-to-speech-tieng-viet.md)) | Đo, chưa xây | HF s2s làm harness. Chạy R0–R5 × C1–C4. Timeline có `hold_s`. Day 0 kiểm R1–R12 | Có các số liệu ở §12.2 |
| **P1: Production v1, một node** | Một vòng hội thoại production | Orchestrator (actor, L1, Smart Turn, duration gate cộng AEC trình duyệt, history cắt theo played offset). asr-service (`asr.v1`, Qwen3-ASR turn_final cộng một engine đối chứng). tts-service (`tts.v1`, cầu đầy đủ, VieNeu). WebRTC cộng coturn. Registry, observability, admission, degradation ladder. Conformance trong CI | Gate §10 mục 1–7, SLO §8.2 |
| **P2: Scale và chất lượng** | Nhiều node, giảm lỗi tương tác | Scale-out, LB nội bộ. Engine TTS thứ hai qua §6.4 (VoxCPM2 hoặc MOSS). Nemotron stream adapter cho caption/speculation nếu gate cho phép. L2. Speaker lock, kiểm echo, denoise nhánh VAD (A/B). Thử FireRedVAD và Namo. Tune grace | Canary đạt, SLO giữ được dưới tải |
| **P3: Nâng cao** | Theo nhu cầu sản phẩm | Two-pass cho critical span. Tool có xác nhận bằng lời. Telephony 8 kHz (ingress adapter, tập test riêng). SFU, multi-region. Fine-tune hoặc LoRA khi có failure case và quyền dữ liệu. Runtime native (audio.cpp, NeMo-Speech.cpp) sau khi qua parity gate | Theo từng hạng mục |

### 12.2 Những gì PoC phải trả lời trước khi chốt P1

| Tham số / lựa chọn | Lấy từ PoC |
|---|---|
| ASR mặc định: Qwen 0.6B, 1.7B hay Nemotron | R0, R1, R2: lỗi entity, thời gian decode, VRAM |
| TTS mặc định cho preset và cho clone | R0, R3–R5 |
| Biến thể Smart Turn (CPU hay GPU), grace, max wait | Tỷ lệ incomplete, `hold_s`, false cutoff |
| Ngưỡng duration gate cho barge-in | Phiếu quan sát C2/C4: ngắt nhầm hoặc trượt |
| `first_min`, `hard_max` của chunker | R11, `inter_chunk_gap` |
| `VIENEU_MAX_STREAMS`, khóa clock GPU | Peak VRAM, lượt sau idle |
| Mức speculation (L1 hay L2) | R12, tỷ lệ lượt bị giới hạn bởi gate, tỷ lệ reopen |
| Pre-buffer phía client, `MAX_LEAD` | Underrun, v2v |
| Nemotron streaming có ghép được không | Stub D8 |
| Giá trị `language` cho NeMo-Speech.cpp | R1 |
| LLM endpoint có stream và hủy được không | R6 |

---

## 13. Giới hạn của tài liệu

- Chưa có gì được hiện thực hay đo. Mọi API, schema, pseudo-code, topology và SLO đều là **Synthesis**.
- Chưa có số đo tiếng Việt cùng điều kiện cho WER, MOS, TTFA hay v2v trên một stack hoàn chỉnh.
- Nhiều tham số control (barge-in, denoise, filter Whisper, ngân sách latency/VRAM) đến từ AI report thứ cấp và chỉ là giá trị khởi điểm.
- Một số điểm hiện thực **Unverified**:
  - cách ước lượng played offset trên WebRTC từ `getStats`;
  - hành vi của VieNeu khi client đọc chậm;
  - Pipecat có thay được orchestrator tự viết không;
  - SFU có hợp với mô hình actor không;
  - ghép NeMo realtime WS.
- License không phải tư vấn pháp lý.
- Số liệu model và runtime có `stale_after` khoảng 2027-10.

---

## Phụ lục A. Thay đổi so với v1 và ánh xạ số mục

**Thay đổi chính:**
- Chuyển từ "chọn model và profile" sang kiến trúc service production.
- Thêm yêu cầu lấy từ spec (§1) và các quyết định kiến trúc (§2).
- Cầu text → speech chuyển vào `tts-service` (AD4).
- Bỏ phương án HF s2s cho production (AD2).
- Thêm hợp đồng `asr.v1`/`tts.v1` (§7.6–7.7) và cơ chế thay engine (§6).
- Sửa pseudo-code theo Chương 17–19 (§7.4).
- Thay bảng ngân sách latency bằng SLO (§8.2).
- Thêm admission, degradation và runbook (§9.4–9.7).
- Phần survey model rút gọn thành tham chiếu sang các tài liệu ASR, TTS và VAD.

| Mục v1 | Nội dung v1 | Mục v2 |
|---|---|---|
| §0 | TL;DR | §0 |
| §1 | Cách đọc, nguồn | Header, §1 (yêu cầu) |
| §2 | Cascade hay end-to-end | §2 AD1 |
| §3 nguyên tắc 1–7 | Nguyên tắc | §3 nguyên tắc 1–7 (giữ số), thêm 8–12 |
| §4 | Kiến trúc tổng thể | §4 |
| §5.1 | Transport, AEC | §5.1, §7.1 |
| §5.2 | VAD | §5.2 |
| §5.3 | Turn detection | §5.3 |
| §5.4 | ASR tiếng Việt | §5.4, §7.6, [tài liệu ASR](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md) |
| §5.5 | Cầu text → speech | §5.5 (trong tts-service), §7.7 |
| §5.6 | TTS tiếng Việt | §5.6, [tài liệu TTS](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md) |
| §5.7 | Orchestration (HF s2s, Pipecat, …) | §2 AD2, §5.7 |
| §5.8 | Deploy tools | §5.8, §9 |
| §6, §6.1 | Profile A–F, cây quyết định | §6.5 (cấu hình engine), §6.4 |
| §7.1 | Audio ingress | §7.1 |
| §7.2 | Event schema | §7.2 |
| §7.3 | Barge-in, cancellation | §7.3 |
| §7.4 | Pseudo-code | §7.4 (đã sửa) |
| §7.5 | Diarization | §7.5 |
| §8.1 | Critical path, output gate | §8.1 |
| §8.2 | Ngân sách tham khảo | §8.2 (SLO) |
| §8.3 | Đòn bẩy | §8.3 |
| §8.4 | Monitoring | §8.4 |
| §9.1–9.5 | Topology, VRAM, scaling, fallback, privacy | §9.1–9.5 (cùng số), thêm §9.6–9.7 |
| §10 gate 1–6 | Release gates | §10 gate 1–6 (cùng số), thêm gate 7 |
| §11 | Mâu thuẫn | §11 |
| §12 | Lộ trình | §12 |
| §13 | Giới hạn | §13 |

---

## Phụ lục B. Tài liệu tham chiếu

**Trong `outputs/`:**
- [Spec PoC Phase 1](spec-poc-speech-to-speech-tieng-viet.md): yêu cầu, R1–R12, kịch bản đo.
- [Lựa chọn và thiết kế ASR/STT tiếng Việt realtime](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md).
- [Lựa chọn và thiết kế TTS tiếng Việt realtime](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md).
- [Survey VAD, turn detection, denoise](survey-vad-turn-detection-denoise-tieng-viet.md).
- [Survey cầu text → speech](survey-cau-text-to-speech-tien-hau-xu-ly-sau-llm.md).
- Các chương nền: [8 Transport](chuong-08-transport-mang-cho-audio-realtime.md), [12 LLM](chuong-12-llm-trong-vong-hoi-thoai-noi.md), [16 Dataflow và audio contract](chuong-16-dataflow-end-to-end-va-audio-contract.md), [17 Turn-taking, barge-in](chuong-17-turn-taking-event-barge-in-va-cancellation.md), [18 Async và streaming](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md), [19 Cầu text → speech](chuong-19-cau-text-to-speech-chunker-normalizer-lexicon.md), [20 Latency](chuong-20-latency-dinh-nghia-critical-path-do-luong.md).

**Wiki:**
- Tổng hợp: [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md), [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md), [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md).
- Control: [Smart Turn v3.2](../wiki/smart-turn.md), [Turn Detection Models](../wiki/turn-detection-models.md), [Silero VAD](../wiki/silero-vad.md), [FireRedVAD](../wiki/firered-vad.md), [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md), [Barge-in & Echo](../wiki/voice-agent-barge-in-and-echo-handling.md), [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md).
- HF s2s (tham chiếu turn tracker, harness PoC): [Pipeline](../wiki/speech-to-speech-pipeline.md), [CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md), [OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md), [Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [Latency Instrumentation](../wiki/speech-to-speech-latency-instrumentation.md), [Browser Demo](../wiki/speech-to-speech-browser-demo.md).
- ASR: [Qwen3-ASR family](../wiki/qwen3-asr-family.md), [Nemotron 3.5 ASR Streaming](../wiki/nemotron-3.5-asr-streaming-0.6b.md), [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md), [HTTP and Realtime API](../wiki/nemo-speech-http-api.md), [ASR Configuration](../wiki/nemo-speech-asr-configuration.md), [Gipformer 1.5](../wiki/gipformer1.5-68m-rnnt.md), [ChunkFormer](../wiki/chunkformer-vietnamese.md), [Faster-Whisper](../wiki/faster-whisper.md), [Punctuation Restoration](../wiki/punctuation-restoration-base.md).
- TTS: [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md), [OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md), [Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md), [Docker Deployment](../wiki/vieneu-tts-docker-deployment.md), [VoxCPM2](../wiki/voxcpm2.md), [MOSS-TTS Local v1.5](../wiki/moss-tts-local-transformer-v1-5.md), [Supertonic 3](../wiki/supertonic-3.md), [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md), [G-OmniVoice](../wiki/g-omnivoice.md), [Gwen-TTS 0.6B](../wiki/gwen-tts-0.6b.md), [VietNormalizer](../wiki/vietnormalizer.md), [Resemblyzer](../wiki/resemblyzer.md).
- Framework và end-to-end: [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md), [PersonaPlex 7B](../wiki/personaplex-7b-v1.md), [NemotronLabs VoiceChat 11B](../wiki/nvidia-nemotronlabs-voicechat-11b.md), [Nemotron 3 Diarization](../wiki/nemotron-3-diarization.md).
