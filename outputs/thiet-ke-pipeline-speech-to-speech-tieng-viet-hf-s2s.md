# Thiết kế pipeline speech-to-speech tiếng Việt dùng Hugging Face speech-to-speech

> **Loại tài liệu:** thiết kế kiến trúc, deliverable trong `outputs/`, không phải tri thức canonical.
> **Phiên bản:** HF s2s v1, nhánh thiết kế độc lập phát triển từ [bản production v2](thiet-ke-pipeline-speech-to-speech-tieng-viet.md). Không thay thế hay sửa bản gốc.
> **Quyết định khác bản gốc:** dùng `huggingface/speech-to-speech` làm orchestration framework, không tự viết lại toàn bộ orchestrator. ASR, LLM và TTS nặng vẫn chạy bên ngoài process HF.
> **Nguồn yêu cầu:** [Spec PoC Phase 1](spec-poc-speech-to-speech-tieng-viet.md). Lựa chọn model từ các tài liệu [ASR](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md), [TTS](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md), [VAD/turn/denoise](survey-vad-turn-detection-denoise-tieng-viet.md) và [cầu text → speech](survey-cau-text-to-speech-tien-hau-xu-ly-sau-llm.md).
> **Nguồn HF:** [Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md), [CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md), [Latency Instrumentation](../wiki/speech-to-speech-latency-instrumentation.md). Capture ở revision `f9c23282a564cbe5b1f015ccb36d58e941de8520`; chưa kiểm tra upstream hiện tại.
>
> **Nhãn bằng chứng:** **Reported** = nguồn công bố; **Observed** = thấy trong code/tài liệu capture, chưa chạy; **Synthesis** = thiết kế đề xuất; **Unverified** = cần kiểm chứng; **Chốt sau PoC** = lấy từ số đo, không tự đặt.
> **Nhãn khả năng:** **Stock** = có trong bản HF được mô tả; **Adapter** = bổ sung service/proxy ngoài HF; **Fork** = sửa phần lõi HF. Nhãn Stock không đồng nghĩa đã kiểm chứng runtime.
> **Phạm vi:** chưa cài đặt, chạy hoặc đo. API mở rộng, topology, patch và release gates trong bản này là **Synthesis**, không phải tính năng sẵn có của HF.

---

## 0. TL;DR

1. **Có thể dùng HF s2s cho cascade tiếng Việt:** Silero → Smart Turn → remote ASR → remote LLM → remote TTS. Tiếng Việt phụ thuộc model và chính sách đọc, không phụ thuộc việc framework có tên Hugging Face.
2. **Hai profile triển khai, không đánh đồng:**
   - **H0 — Stock + adapters:** HF `serve`, `--stt openai`, LLM OpenAI-compatible, `--tts openai`; TTS proxy normalize text rồi gọi VieNeu. Audio trong HF là 16 kHz; text chia theo câu; history chưa bảo đảm đúng phần đã nghe. Dùng cho PoC/MVP được chấp nhận giới hạn, **không** gọi là production parity với bản gốc.
   - **H1 — Production fork:** giữ framework, transport, pipeline pool, turn tracker và cancellation của HF; bổ sung bridge nhận text delta, audio downlink 48 kHz, playback-aware history, bounded queues và telemetry. Chỉ release khi qua các gate §10.
3. **ASR không bắt buộc in-process.** `--stt openai` gọi `/v1/audio/transcriptions` self-host. Qwen3-ASR ở sidecar riêng; không dùng handler Qwen local trong các profile này.
4. **HF có nhiều session:** `num_pipelines` là pool pipeline cô lập, mặc định 1. Nó không thay cho admission GPU dùng chung. Pool và model service phải có budget riêng.
5. **Không tạo owner lượt thứ hai.** Pipeline/turn tracker/RealtimeService của HF là miền sở hữu lượt. Patch phải thống nhất ranh giới commit/reopen/cancel; gateway và model service không tự quyết định endpointing.
6. **`tts-service` giữ policy theo engine:** ThinkFilter, markup, chunker, lexicon, normalizer, voice và resample. H0 chỉ nhận text đã chia bởi HF; H1 nhận delta và trả text/audio metadata qua hợp đồng mở rộng. Không thể đạt H1 chỉ bằng proxy `/audio/speech`.
7. **Ba khoảng trống lớn nhất:** trần audio 16 kHz, `conversation.item.truncate` no-op, và chunking/context mapping. Auth, self-host TURN và remote ASR là việc triển khai/adapter, không phải lý do framework hoàn toàn không dùng được.
8. **Mục tiêu latency vẫn giữ:** D1 ở client P50 ≤ 1.5 s, P95 ≤ 2.5 s (mềm). H0 là baseline đo; H1 cần số đo riêng, không suy ra từ H0.
9. **Ngưỡng dừng fork:** nếu không thể cô lập patch control/history/audio và qua replay tests, quay về orchestrator riêng của bản gốc. Không duy trì đồng thời hai owner hoặc hai máy trạng thái lượt.

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
| FR8 | Nhiều session đồng thời, dùng HF pipeline pool cộng admission backend | spec loại khỏi PoC; production cần (**Synthesis**) |
| FR9 | Có điểm cắm cho: partial/caption, two-pass, speaker lock, denoise nhánh VAD, telephony 8 kHz | spec §8 backlog |

### 1.2 Yêu cầu phi chức năng

| ID | Yêu cầu | Giá trị | Nguồn |
|---|---|---|---|
| NFR1 | Latency voice-to-voice, đo ở client (D1) | P50 ≤ 1.5 s, P95 ≤ 2.5 s, mục tiêu mềm, báo theo loại lượt | spec §1 (Q24) |
| NFR2 | Privacy | Self-host toàn bộ. Không gửi audio hoặc text ra ngoài, kể cả STUN công cộng | Q6, spec §3.1 |
| NFR3 | Log | Mặc định không chứa nội dung (content-free). Transcript chỉ ghi khi opt-in | spec §2 |
| NFR4 | Phần cứng speech | Mỗi node speech có 1 GPU 24 GB. Scale bằng cách thêm node | Q4; mở rộng (**Synthesis**) |
| NFR5 | License | PoC được dùng model NC. Production phải qua license gate theo `license_profile` của từng deployment | Q3; §3 nguyên tắc 7 |
| NFR6 | Cách ly môi trường | ASR/TTS/LLM nặng ở process và environment riêng; HF giữ VAD/turn | spec §2 |
| NFR7 | Khả năng quan sát | Timeline theo lượt có các mốc soft-end, ASR, LLM, commit, TTS, playback; join theo ID | spec §5.3 |
| NFR8 | Vận hành | Warmup xong mới báo ready. Có healthcheck, admission, backpressure, degradation | **Synthesis**, Chương 18 |

### 1.3 Giả định và ngoài phạm vi

- LLM nằm trên host riêng. Thiết kế chỉ phụ thuộc vào `base_url`, tên model, streaming và khả năng hủy (R6 của spec).
- Agent phục vụ một người dùng mỗi session, không có diarization trong critical path (§7.5).
- Ngoài phạm vi v1: telephony 8 kHz (ingress adapter dự kiến), meeting nhiều người nói, model end-to-end speech-in/speech-out, tool có side effect (policy/hook dự kiến ở §5.7.3).

### 1.4 Profile và mức đáp ứng yêu cầu

| Chủ đề | H0: HF stock + adapters | H1: HF production fork |
|---|---|---|
| Orchestration | HF `serve`, remote ASR/TTS | HF `serve` với patch có version |
| ASR | OpenAI-compatible HTTP, turn-final | Giữ HTTP turn-final; streaming tùy chọn sau gate |
| TTS input | Text đã được HF chia theo câu | Text delta, bridge tự clause-chunking |
| Audio downlink | Nội bộ HF 16 kHz; WebRTC encode Opus 48 kHz | PCM TTS 48 kHz tới WebRTC, không hạ xuống 16 kHz |
| History khi ngắt | Semantics HF stock; truncate no-op | Display prefix theo played offset, cắt bảo thủ |
| Session | Pool `num_pipelines` | Pool cộng budget RAM/CPU/model và overload tests |
| Commit/cancel | Cơ chế HF được mô tả, cần replay | Giữ một miền sở hữu; patch output/history validity nếu cần |
| Quan sát | Log HF + tap/proxy ngoài | Trace nối turn/revision/generation/chunk, client D1 |
| Privacy/auth | Edge auth, self-host ICE, audit log | Như H0, cộng audit metadata/patch |
| Được gọi là production đầy đủ? | Không, trừ khi sản phẩm chính thức hạ yêu cầu | Chỉ sau §10; chưa có bằng chứng đạt |

FR1–FR6 vẫn phải được kiểm thử trên cả hai profile. FR7/FR8/NFR8 ở H0 chỉ đáp ứng trong phạm vi adapter/pool đã đo. Không silently hạ tiêu chí history, chất lượng downlink hoặc overload để báo H1 thành công.

---

## 2. Quyết định kiến trúc

Tất cả quyết định là **Synthesis**; hành vi HF được dẫn nguồn và phân loại riêng.

| ID | Quyết định | Khả năng / lý do | Phương án loại |
|---|---|---|---|
| AD1 | Cascade tiếng Việt | Stock. Model ASR/TTS tiếng Việt thay thế độc lập; end-to-end chưa qua gate ngôn ngữ | End-to-end làm mặc định |
| AD2 | HF s2s là orchestrator framework | Stock cho H0; Fork cho H1. Tái sử dụng realtime protocol, WebRTC, pool, turn tracker, generation-tagged cancellation | Tự viết lại toàn bộ ngay từ đầu |
| AD3 | ASR/TTS/LLM nặng ngoài process HF | Stock remote backends + Adapter. `--stt openai` và `--tts openai` cho phép cách ly inference | Qwen local trong HF; load TTS weights theo session |
| AD4 | Bridge gắn với `tts-service` | H0 normalize text đã chia; H1 bridge sở hữu clause chunking trên delta | Proxy HTTP được coi như đã có delta streaming |
| AD5 | HF là miền sở hữu turn duy nhất | Stock cần kiểm chứng; Fork chỉ sửa tại miền này. Adapter không commit/reopen; không thêm SessionActor chạy song song | Owner riêng ở edge/ASR/TTS |
| AD6 | H0 giữ 16 kHz, H1 giữ downlink 48 kHz | Stock TTS remote resample về 16 kHz (**Reported**); H1 phải sửa handler/output/transport đồng bộ | Chỉ đổi `openai_tts_sample_rate` rồi tuyên bố hết trần 16 kHz |
| AD7 | WebRTC production, WS cho harness | Stock. Cả hai dùng cùng pool/send loop; ICE chỉ tự host | STUN công cộng mặc định |
| AD8 | HTTP OpenAI-compatible cho H0; bridge RPC riêng cho H1 | Adapter/Fork. H1 chọn gRPC bidi cho delta + metadata; không thay toàn bộ API realtime công khai | Đặt gRPC service vào HF mà không viết handler |
| AD9 | ASR v1 turn-final | Stock remote STT; progressive HTTP tắt để tránh upload lại nhiều lần. Streaming khi có số đo compute/caption | Streaming bắt buộc ngay từ P0 |
| AD10 | Admission ở edge, HF pool và model API | Adapter. Per-pipeline queue không giới hạn concurrency toàn GPU | Chỉ tăng `num_pipelines` |
| AD11 | Playback-aware history là patch bắt buộc H1 | Fork. `conversation.item.truncate` no-op (**Reported**); không giải quyết bằng TTS proxy | Context chứa cả phần chưa nghe |
| AD12 | Duy trì fork nhỏ, pin upstream và parity tests | Mỗi patch có test, owner, rollback; rebase không tự promote | Fork không version hoặc hai control plane |

**Điểm không kết luận quá mức:** HF có remote ASR và pool session. Không có admission model dùng chung hoặc auth tích hợp không có nghĩa là không dùng được; phải bổ sung và đo. Ngược lại, trần 16 kHz, no-op truncate và quyền sở hữu chunking là khoảng trống thật so với bản gốc.

---

## 3. Nguyên tắc thiết kế

Số thứ tự 1–7 giữ ý nghĩa bản gốc để tiện đối chiếu. Bản HF này không phải đích thay thế cho liên kết từ các chương khác.

1. **Tách năm tầng:** model, runtime, API, streaming policy, orchestration. OpenAI-compatible không bảo đảm format, latency hay cancellation tương đương.
2. **Một miền sở hữu turn:** HF pipeline/turn tracker/RealtimeService của session. Phải audit đường ghi state thực tế; không giả định kiến trúc queue/thread của HF đã tương đương actor một inbox.
3. **ASR nghe audio qua AEC, chưa enhancement.** Denoise chỉ nhánh VAD/barge-in khi có A/B.
4. **Contract trước engine:** H0 dùng manifest + startup validation, vì OpenAI HTTP không có `Describe` chuẩn. H1 bridge có `Describe`; mọi đổi engine qua conformance.
5. **Không phát speculative audio trước commit của đúng revision.** Stale-result filtering bắt buộc ở mọi chỗ đổi chủ. Tool có side effect và history không được chạy trên transcript chưa commit.
6. **Không cộng metric khác loại.** TTFT, first clause, TTS TTFA, endpoint→final và D1 báo riêng.
7. **License là hard gate** theo `license_profile`, kể cả weights, runtime, voice và lineage.
8. **Không load model ASR/TTS/LLM nặng trong HF.** VAD/Smart Turn ở HF. Không tuyên bố HF stock không import torch: dependency/import của framework cần kiểm chứng riêng.
9. **Patch nhỏ, ranh giới rõ:** không thêm owner ngoài HF. Nếu phải thay phần lớn control plane, chuyển về bản gốc thay vì duy trì hai cơ chế.
10. **Queue bounded theo cạnh; cancel best-effort, generation validity bắt buộc.** Đóng HTTP không bảo đảm compute dừng; đo slot backend và T_release.
11. **H1 history là phần người dùng đã nghe,** dùng `display_text`; H0 ghi rõ giới hạn và không claim parity.
12. **Quan sát content-free:** ID, thời lượng, độ dài, version; không log payload text/audio/reference. H1 ID mở rộng phải map với ID native, không giả định native có đủ mọi trường.

---

## 4. Kiến trúc tổng thể

### 4.1 H0 — HF stock + adapters

```text
Browser: AEC/NS/AGC, WebRTC audio + oai-events
    │ HTTPS signaling, SRTP/UDP qua coturn tự host khi cần
edge: TLS, auth, session admission, sticky route
    │ /v1/realtime/calls hoặc WS realtime
HF s2s serve (CPU deployment; kiểm dependency thực tế)
    ├─ pool PipelineUnit: VAD → turn tracker → remote STT
    ├─ RealtimeService / conversation state / CancelScope
    ├─ remote LLM → LMOutputProcessor chia câu
    └─ remote TTS → PCM16 16 kHz → send loop → WebRTC
           │                            │
           │                            └─ TTS downsample dù track Opus 48 kHz
           └─ tts-service /v1/audio/speech
                ThinkFilter → markup → giới hạn text → lexicon/normalizer
                → VieNeu sidecar → PCM16 48 kHz
remote STT → asr-service /v1/audio/transcriptions → Qwen3-ASR sidecar
remote LLM → endpoint self-host trên host riêng
```

H0 không có bridge text-delta, mapping text/audio hay history truncate chính xác. TTS adapter phải khai báo đúng 48 kHz nguồn cho handler HF. HTTP request fields không được VieNeu hỗ trợ phải được proxy xử lý/từ chối rõ ràng.

### 4.2 H1 — HF production fork

```text
Browser / edge / coturn: giữ transport realtime HF
    │
HF s2s pinned fork
    ├─ pool + VAD/Smart Turn + turn tracker: owner native được harden
    ├─ remote ASR HTTP + validity policy
    ├─ LLM stream → delta bridge handler (bỏ native sentence splitting cho H1)
    │                   │ gRPC tts.v1, 1 stream/generation
    │                   ▼
    │              tts-service
    │              filter → clause chunker → lexicon/normalizer
    │              → engine sidecar → PCM16 48 kHz + text/audio metadata
    ├─ held output / commit gate / generation validity
    ├─ playback-aware history + map native IDs ↔ internal IDs
    └─ send loop / WebRTC pacer: 48 kHz, clear, bounded audio lead
```

Không chạy cùng lúc `--tts openai` stock và delta handler cho một response. H1 bypass sentence splitting cho nhánh bridge nhưng giữ đường tool parts/usage/terminal có thứ tự.

### 4.3 Service và ranh giới

| Service | Trách nhiệm | Không làm | Scale |
|---|---|---|---|
| edge | TLS, auth, signaling proxy, admission, sticky routing | Quyết định turn; ghi audio payload | Ngang |
| coturn | STUN/TURN tự host | Xử lý model/turn | Theo mạng |
| hf-s2s | Pipeline pool, VAD/turn, realtime protocol, LLM, cancel, history, send loop | Load ASR/TTS/LLM weights nặng; normalize riêng ngoài bridge | Process và pool được đo |
| asr-service | OpenAI HTTP facade, ép vi, filter, deadline, admission; engine adapter | Endpointing/commit hội thoại | Pool inference |
| tts-service | H0 HTTP; H1 delta RPC; policy text/voice, engine, audio metadata | Commit, playback, ghi conversation history | Pool inference |
| registry | Pin weights/runtime/fork, contract manifest, voices/consent, lexicon | Thay engine giữa utterance | Versioned config |
| observability | OTel/metrics, content-free logs, trace join | Lưu transcript mặc định | Ngang |
| LLM | OpenAI-compatible streaming, host riêng | Tự quản turn audio | Ngoài phạm vi |

### 4.4 Placement và dependency

- Silero và Smart Turn CPU ONNX ở HF, state riêng mỗi pipeline/session. Kiểm Smart Turn không chặn audio/event loop; patch executor nếu cần, không giả định code capture đã chứng minh.
- RNNoise/DeepFilterNet mặc định tắt. DeepFilterNet tách process nếu dependency xung đột.
- ASR/TTS mỗi engine một environment; API facade có thể chỉ dùng HTTP/gRPC client.
- Ingress WebRTC: 48 → 16 kHz một lần cho VAD/ASR. H1 downlink giữ 48 kHz; không đổi ingress lên 48 kHz cho Silero.
- Không bắt buộc SFU ở v1. Nếu thêm LiveKit/SFU sau này, phải viết transport adapter và giữ HF làm owner; không coi là thay config đơn thuần.

---

## 5. Các tầng xử lý

### 5.1 Transport, AEC và client

**Stock (Reported):** `POST /v1/realtime/calls` nhận SDP offer, trả SDP answer và `Location`; audio qua RTP/Opus, JSON qua DataChannel `oai-events`. WS dùng `input_audio_buffer.append`. Mọi kết nối được cấp PipelineUnit từ cùng pool.

**Client:** web app riêng, `getUserMedia` bật AEC/NS/AGC. Mic yêu cầu HTTPS hoặc localhost. Không dùng browser demo nguyên bản như một ứng dụng production nếu chưa audit auth/log/reference.

**ICE:** đặt `SPEECH_TO_SPEECH_ICE_SERVERS` chỉ tới coturn tự host. Không để mặc định aiortc/Google STUN. Chuẩn bị wheel/model offline, kiểm network egress.

**H0 audio:** track Opus 48 kHz nhưng HF nhận/xuất nội bộ 16 kHz. `openai_tts_sample_rate=48000` mô tả response TTS; nó **không** bỏ bước downsample của stock handler.

**H1 audio:** patch toàn tuyến handler → output queue → transport/pacer để nhận PCM16 48 kHz. Format đi kèm stream/output; không hard-code 512 mẫu ở downlink. Một frame 20 ms có 960 mẫu tại 48 kHz. Ingress vẫn reblock 512 mẫu ở 16 kHz cho Silero.

**Clear:** native WebRTC `output_audio_buffer.clear` flush buffer phía server (**Reported**), không flush từ xa jitter buffer trình duyệt. Client WS riêng có AudioWorklet và generation floor để đo played offset chính xác hơn; client Realtime SDK stock chưa chắc hỗ trợ extensions H1.

**AEC server (P2):** quick-ASR so với bot text là tín hiệu kiểm echo, không phải owner endpointing mới. Đo echo loa ngoài và tình huống user đọc lại đúng câu bot.

### 5.2 VAD

| Mục | Thiết kế |
|---|---|
| Model | Silero VAD v5/v6 ONNX. Mỗi session một state, cửa sổ 512 mẫu (32 ms) ở 16 kHz (**Reported**) |
| Threshold | Khởi điểm 0.6 theo default HF s2s (**Observed**). Hiệu chỉnh theo nhiễu: đo xác suất VAD và RMS trong 2–3 s đầu; nếu nền > 0.3 thì nâng lên 0.65–0.7 (**Reported**, AI report). **Chốt sau PoC** |
| Padding | Liệt kê **mọi** lớp padding: pre-roll lấy từ ring, `speech_pad`. Mục đích là để chúng không cộng dồn ngoài ý muốn (Chương 16 §16.17.2) |
| Chạy ở đâu | VAD worker trong PipelineUnit HF; audit queue/backlog và state theo session |
| Ứng viên thay thế | FireRedVAD có false alarm thấp hơn trong bảng của chính vendor (2.69% so với Silero 9.41%, **Reported**). Đáng A/B khi nền là TV hoặc nhạc. Không có VAD nào có số đo riêng cho tiếng Việt |
| Denoise | Mặc định **tắt**. Nếu bật thì RNNoise hoặc DeepFilterNet 3, **chỉ** cho nhánh VAD/barge-in. Facebook Denoiser là CC-BY-NC và không có metric chất lượng (**Reported**) |

### 5.3 Turn detection và endpointing

**Máy trạng thái lượt** (speculative + revision, theo turn tracker của HF s2s, **Reported**):

```text
LISTENING ──VAD im ≥ min_silence──► SOFT_ENDED ──Smart Turn: complete────► (grace) ──► COMMIT
    ▲                                   │      └─Smart Turn: incomplete──► chờ incomplete_delay ─► (gate tới max_wait) ─► COMMIT
    └──────── user nói tiếp (≥ continuation_ms) ◄──── reopen: revision++, bỏ việc chưa commit
```

**Tham số khởi điểm.** Các ngưỡng VAD/Smart Turn dưới đây là default HF đã capture (**Observed**); ring buffer và pre-roll là đề xuất **Synthesis**, không phải default đã xác minh. Giữ bộ ngưỡng tới khi PoC có số đo; **không** trộn với bộ của report.

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

**Một miền sở hữu trong HF.** Endpointing trong NeMo-Speech.cpp (`stop_history_eou_ms`) và segmentation của WhisperLiveKit hay RealtimeSTT phải tắt, hoặc chỉ được dùng làm tín hiệu.

**Timer (H1, Synthesis).** Audit timer HF cho grace/incomplete/max-wait/unanswered; mỗi kết quả phải còn hợp lệ với turn/revision hiện hành. Bổ sung token nếu thiếu. Kiểm origin của từng timer theo timeline thực tế, không suy ra mọi timer bắt đầu cùng lúc tại soft-end. Config ghi rõ audio clock và wall clock.

**Ánh xạ stock (Observed):** `continuation_ms` của bảng là `min_speech_continuation_ms` trong CLI. Stock dùng `min_speech_ms` cho cả mở lượt và barge-in; duration gate riêng §7.3 là patch H1, không phải flag đã có. `speech_pad_ms` mặc định 500 ms: phải đo/tune cùng pre-roll, không cộng thêm padding 200–300 ms một cách mù quáng.

### 5.4 ASR service

**H0/H1 v1:** `--stt openai` gọi `POST /v1/audio/transcriptions` ở service riêng. Request upload WAV PCM16 16 kHz mono; response JSON `{ "text": "..." }` hoặc plain text theo cấu hình (**Reported**). Đây là đường remote ASR, không phải handler Qwen local.

**Facade ASR (Adapter):** pin engine/version, ép tiếng Việt, normalize NFC, filter hallucination, admission và deadline. Nếu API engine không đúng contract, facade chuyển đổi. Startup HF dùng 1 s silence để validate endpoint; readiness production vẫn cần warmup và bài test audio vi riêng, không chỉ `/v1/models`.

- Mặc định turn-final. Xác nhận `enable_live_transcription` và `enable_realtime_transcription` không kích hoạt progressive upload trong profile; dùng flag phủ định đúng parser bản pin, kiểm `--help` trước khi chạy.
- Progressive HTTP gửi lại cửa sổ tích lũy, **không phải** native streaming.
- Stock đã có queue final/progressive, revision/session stale filtering (**Reported**); kiểm concurrency và hủy trong upload/connect/read.
- `quality_flags` không thuộc response OpenAI tối thiểu. H0 chỉ bỏ final rỗng và dùng policy filter ở facade; H1 thêm field được custom handler đọc, hoặc một typed result nội bộ. Không giả định stock tiêu thụ mọi extra field.
- Nemotron turn-final có thể qua HTTP facade. Nemotron realtime WS là protocol riêng, không trỏ thẳng vào `openai-realtime` hay `vllm-realtime`; phải viết adapter và qua test endpointing owner.
- Two-pass là P3; final-pass chạy trước LLM/commit release phù hợp, không âm thầm tạo turn thứ hai.

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
2. Punctuation restoration nếu manifest engine khai `punctuation=false`; ASR HTTP không có `Describe` chuẩn. Ứng viên: [Punctuation Restoration 307M](../wiki/punctuation-restoration-base.md), F1 tiếng Việt 0.866 (**Reported**).
3. Filter riêng theo engine.
4. Gắn `quality_flags`: `empty`, `no_speech`, `hallucination_suspect`, `language_mismatch`, `truncated`, `low_confidence` (chỉ khi confidence đã được calibrate, nếu không thì `unknown`).

**Validity policy:** H1 đặt trong HF trước tạo LLM work. `empty/no_speech` → quay lại nghe; `hallucination_suspect` → hỏi lại bằng fixed phrase; `language_mismatch/truncated` → policy hỏi lại. Phản hồi cache vẫn có response/generation lifecycle, không được vượt gate.

**Capacity:** semaphore chung theo endpoint/engine, queue bounded, HTTP 429 + `Retry-After`; H1 handler map thành lỗi typed. Per-pipeline tám pending finals của HF (**Reported**) là giới hạn memory/request cục bộ, không phải GPU admission. Đóng HTTP là best-effort; final cũ không được tạo LLM work dù backend vẫn compute.

### 5.5 TTS service, phần 1: cầu text → speech

#### 5.5.1 H0: proxy HTTP nhận text đã chia

HF `LMOutputProcessor` chia text theo câu. Đặt `stream_batch_sentences=1` để baseline trả từng câu thay vì default 3 (**Observed**). `tts-service` nhận `/v1/audio/speech`, lọc thinking/markup, lexicon/normalizer rồi gọi engine, trả PCM16 48 kHz. HF stock downsample về 16 kHz.

Proxy có thể chia nhỏ câu dài để không vượt `max_chars`, nhưng **không** phục hồi latency clause đầu vì phải chờ HF gửi câu. Proxy có thể log content-free chunk timing, nhưng không gửi `display_text/segments` qua raw PCM response. Native caption/history vẫn là text HF, không phải bản normalized đã nói; đây là giới hạn H0 phải được chấp nhận tường minh.

ThinkFilter ở HTTP proxy chỉ bảo vệ từng request, không đủ xử lý `<think>` kéo dài qua nhiều request. H0 bắt buộc tắt thinking ở LLM và kiểm native text processing; nếu không chứng minh lọc an toàn, chặn profile hoặc thêm patch stateful filter trước chia câu. Không claim proxy stateless giải quyết mọi token split.

#### 5.5.2 H1: delta bridge thay native sentence splitting

```text
LLM text parts → custom HF bridge handler → tts.v1 text.delta
  → ThinkFilter (state theo generation) → markup/emoji/URL policy
  → ClauseChunker → pre-lexicon → VietNormalizer → post-lexicon/tag whitelist
  → engine queue → engine → resample/watermark
  → text.chunk{display_text, spoken_text, segments, versions} + audio.chunk 48 kHz
  → HF hold/commit/generation gate → caption/history + send loop
```

**Patch không chỉ ở TTS handler:** `LMOutputProcessor`/dispatcher phải chuyển delta có thứ tự, usage/tool parts/terminal đúng lifecycle. Bypass splitter native riêng cho H1; không chia lại cùng text ở HF và service.

**Bất biến (Synthesis):**
1. Mỗi generation có một instance filter/chunker. Cancel vứt state, không `flush()`.
2. Output không phụ thuộc cách token split; chỉ chốt dấu câu khi đủ lookahead. Fuzz cả `<think>`, markup, số và URL.
3. `display_text` cho caption/history; `spoken_text` cho engine; `raw_text` chỉ debug opt-in.
4. Normalizer sau chunker trên segment plain, không đổi ý nghĩa; ambiguous span có warning và policy cụ thể.
5. Pre-lexicon bảo vệ thực thể, post-lexicon respell theo engine/voice. Pin version và alert list; lỗi `chánh` → `tránh` của VieNeu phải reproduce đúng voice/version trước workaround.
6. Chunk rỗng không gọi engine. Không audio nào tới client trước commit của đúng revision.
7. Text segment map **không phải** word-level audio alignment. Nếu engine không có timestamps, chỉ ghi history của chunk đã phát hết; muốn giữ prefix trong chunk cần thêm word/segment timing đáng tin cậy.

**Chunker khởi điểm (Chốt sau PoC):** `.?!…;:`/newline; dấu phẩy chunk đầu sau khoảng 25 ký tự; gộp mảnh < 8 ký tự; `hard_max` dưới `max_chars` sau normalization. Không cắt trong `1.250.000đ`, `3,5`, `14:30`, `TP.HCM`, URL hay `TS. Nguyễn`. Nếu normalization làm vượt trần engine, split lại ở ranh giới segment an toàn và cập nhật mapping, không cắt tùy tiện.

**Normalizer:** VietNormalizer MIT, pin version. VieNeu code-switch → tắt transliteration theo voice policy. Kiểm lowercase có hại prosody không; giữ dấu câu. ViSoNorm mặc định tắt khi chưa qua license. Không dùng con số sub-ms của rule/normalizer để tuyên bố toàn bridge (RPC, batching, queue, engine) miễn phí latency.

**Defense phía LLM:** prompt văn nói và tắt thinking. Đo first-clause time, `norm_warnings`, chunk kind, semantic fidelity; không sửa prompt để che lỗi chunker.

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
- GPU hạ clock sau khoảng 2 s rảnh (118 ms → 403 ms theo nguồn). Đánh giá khóa clock ở host nếu phần cứng hỗ trợ (§9.7); không suy ra cùng số đo cho mọi GPU. Giữ GPU nóng từ process không có tác dụng trong thử nghiệm của nguồn.
- Watermark Perth bật mặc định. Bật hay tắt là quyết định chính sách, ghi trong config.
- Giọng clone đăng ký qua `POST /v1/voices` chỉ sống trong bộ nhớ process. tts-service phải **đăng ký lại sau mỗi lần sidecar khởi động**, lấy từ voice registry, trước khi báo ready. Trùng tên preset trả 409.
- `mp3` và `opus` trả 400. `speed` và `instructions` bị bỏ qua.

**Voice registry.** `voice_id` là định danh ổn định của sản phẩm. Mỗi `voice_id` ánh xạ sang (engine, preset hoặc reference, vùng, scope lexicon, tham số sampling cố định).
- Reference clone lưu ngoài repo, kèm bản ghi consent và thời hạn lưu.
- Log chỉ ghi `voice_id`, không ghi đường dẫn hay embedding.
- Session được pin một `voice_id` và một engine. Không đổi giọng giữa chừng một utterance (§9.4).

**Fixed-phrase cache (Adapter/H1).** Tổng hợp câu đệm/hỏi lại/lỗi lúc khởi động bằng đúng voice, cache theo `(voice_id, phrase_id, engine_version, text_policy_version)`. H1 có `SynthesizePhrase` trong bridge; H0 cần đường gọi cache và lifecycle riêng đã kiểm thử, không phải API HF stock. Khi engine lỗi, chỉ phát cache nếu đường fallback đã tích hợp đúng (§9.4).

**Cadence (Synthesis).** H1 mặc định một request engine active/generation; gửi mệnh đề kế tiếp khi đã nhận xong mệnh đề trước và còn staging credit (§9.6), không cần chờ phát hết. RTF < 1 có thể che khe hở nhưng không bảo đảm nếu TTFA/queue/jitter lớn; đo gap/underrun trước prefetch. H0 kiểm lịch request thực tế của HF/proxy; HTTP stock không tự mang generation ID hay credit bridge.

### 5.7 HF session runtime, LLM và history

#### 5.7.1 Giữ runtime native, không thêm actor song song

HF realtime engine có `PipelineUnit`, `RealtimeService`, turn tracker, `CancelScope`, workers và queues (**Reported**). Không đồng nhất kiến trúc đó với actor một inbox của bản gốc. H1 audit mọi đường ghi commit/reopen/cancel/history và dùng synchronization phù hợp trong miền HF.

- Mỗi session chiếm pipeline từ pool; teardown hủy/join workers và giải phóng state trước tái sử dụng.
- Generation-tagged audio/events đi qua sole send loop. Kiểm relevance ngay trước publication/send và cập nhật state không xen await gây race.
- Revision mới vô hiệu ASR/LLM/bridge/output cũ. Map native response/item IDs với internal turn/revision/generation; không suy diễn một native ID luôn tương ứng một turn.
- H1 held text/audio bounded. Commit mở gate; reopen bỏ scope speculative, không flush bridge.

#### 5.7.2 Speculation

| Profile / mức | Tính toán trước commit | Release | Trạng thái |
|---|---|---|---|
| H0 native | Speculative/reopen theo HF | Theo native output hold | Stock Reported; audit ordering/timer trước đo |
| H1 L0 | Không response compute trước commit | ASR → LLM → bridge sau commit | Patch mode cho debug |
| H1 L1 mặc định | ASR + LLM; text giữ bounded | Mở bridge lúc commit, gửi text đã held theo thứ tự | Fork; phải kiểm không nhân đôi delta |
| H1 L2 | ASR + LLM + TTS mệnh đề đầu | Audio giữ, thả lúc commit | Fork sau PoC; priority thấp, budget speculative riêng |

Không gắn nhãn native HF là L1/L2 nếu chưa kiểm vị trí start/hold/release thực tế. Công thức latency ở §8 là mô hình H1, không phải bằng chứng lịch thực thi stock.

#### 5.7.3 LLM

Dùng handler OpenAI-compatible phù hợp endpoint (Chat Completions hoặc Responses); không bật proxy LLM public của HF. Responses support không suy ra Chat Completions endpoint hỗ trợ cùng protocol/tool/usage.

Tắt thinking theo backend; prompt văn nói từ spec; `stream_batch_sentences=1` cho H0. Tắt `compact_history` tự động hoặc thay bằng job tường minh có metric, vì default có thể phát sinh lời gọi LLM bổ sung (**Observed**).

H1 bổ sung connect/TTFT/inter-token/overall deadline nếu native thiếu; close stream khi cancel; không retry sau token đầu; lỗi thành keyed lifecycle event, không làm chết pipeline. Cần kiểm backend giải phóng compute khi đóng stream. Tool có side effect chỉ sau commit và xác nhận; idempotency key theo turn/revision/tool index.

#### 5.7.4 History

**H0:** `conversation.item.truncate` là no-op (**Reported**). Native cancellation/rollback không tương đương history chính xác theo playback. Đo và ghi nhận context sau cancel/fail/incomplete; không báo FR history parity.

**H1 (Fork):**
- Lưu chunk `display_text`, range audio `[start_sample, end_sample)` và optional timing do engine/alignment cung cấp.
- `response.done(completed)` biểu thị generation kết thúc, **không** đồng nghĩa client phát hết. Giữ playback ledger tới ACK/drain timeout; finalize heard history theo policy.
- Khi cancel: cắt bảo thủ theo played offset. Không có within-chunk timing → chỉ giữ chunk đã phát hết. Span bị rewrite chỉ giữ khi đủ bằng chứng phát hết span, hoặc lùi về chunk boundary.
- Caption transcript `.done` và history cuối phải cùng chính sách nội dung, nhưng transcript hiển thị phát sinh trước playback không được coi là đã nghe.
- `conversation.item.truncate(item_id, audio_end_ms)` phải thật sự cập nhật đúng item/history, idempotent, reject unknown/wrong response, và không tăng heard prefix sau khi đã chốt cancel. Trả acknowledgement/error theo contract được test với client mục tiêu.
- Reopen thay transcript user cùng turn/revision; không xóa nhầm lượt đã commit trước đó. Error fallback/fixed phrase cũng phải vào playback ledger.

### 5.8 Runtime và cách ly dependency

| Process | Dependency / policy |
|---|---|
| HF H0/H1 | HF pinned package/fork, realtime/WebRTC extra, VAD/Smart Turn; không load speech/LLM weights nặng |
| asr-service facade | HTTP client/server, admission; engine sidecar environment riêng |
| asr-engine | vLLM/qwen-asr, NeMo-Speech.cpp, CTranslate2 hoặc sherpa-onnx |
| tts-service | HTTP H0 / gRPC H1, bridge, VietNormalizer, soxr, voice/cache policy |
| tts-engine | VieNeu api-gpu, VoxCPM2 hoặc engine đã qua license/conformance |

Không cam kết image HF không có torch/numpy xung đột chỉ vì chọn remote backend. Kiểm package/import graph, memory và CPU/GPU usage khi nhiều pipeline; cần lazy import/extra split thì ghi là patch. Không chạy heavy compute hay lặp blocking generator trên event loop.

---

## 6. Thay thế ASR và TTS

### 6.1 Contract theo profile

| Cơ chế | H0 | H1 |
|---|---|---|
| ASR contract | HTTP transcription WAV16k → JSON/text | Như H0 + handler đọc quality metadata đã version |
| TTS contract | HTTP speech text → raw PCM48k; HF đổi về16k | gRPC delta → text chunk + PCM48k + offsets |
| Capability | Manifest ở registry + startup validation; không có Describe OpenAI chuẩn | Bridge `Describe` + manifest có checksum |
| Text policy | Normalize/max_chars ở proxy, native splitter ở HF | Chunker/normalizer/lexicon theo engine/voice trong service |
| Engine routing | Pin deployment/pipeline pool; chưa claim per-session dynamic selection | Pin session qua patch nếu cần; kiểm voice/contract phù hợp |
| Rollback | Revert registry/image; drain session | Như H0, pin thêm fork commit + protocol version |

### 6.2 Registry minh họa (Synthesis, không phải CLI HF)

```yaml
profile: H1                         # H0 | H1
license_profile: research
hf:
  upstream_revision: f9c23282a564cbe5b1f015ccb36d58e941de8520
  fork_revision: <commit-after-tests>
  image_digest: <sha256>
  pool_size: 4                      # số đo quyết định, không phải capacity đã xác nhận
  extensions: [delta_bridge_v1, audio48_v1, playback_history_v1]
asr:
  adapter: openai_transcription
  endpoint: http://asr-api:8101/v1
  engine: qwen3-asr-0.6b             # 0.6B/1.7B Chốt sau PoC
  language: vi
  model_revision: <commit>
  weights_sha256: <sha256>
  limits: {max_inflight: 4, queue: 8, max_turn_s: 30}
tts:
  http_endpoint: http://tts-api:8103/v1     # H0
  bridge_endpoint: tts-api:9103            # H1; custom handler, không có CLI stock
  engine: vieneu-v3-turbo
  protocol: tts.v1
  native_rate: 48000
  max_streams: 8                     # Chốt sau PoC, không lấy từ pool_size
  license: disputed
  voices:
    vi-north-01:
      preset: <validated-name>
      region: north
      policy: {max_chars: 256, hard_max: 200, first_min: 25}
      lexicon_scope: [common, vieneu]
```

Mỗi manifest pin runtime, weights, G2P, policy, watermark, voicepack, reference consent và checksum. `Describe`/manifest phải thống nhất; không tự đổi engine khi mismatch.

### 6.3 Conformance

- **ASR:** format đúng, empty/no-speech, ép vi, timeout/429, ordering finals, revision mới bỏ kết quả cũ, session reuse không rò state, close RPC/HTTP đo release compute. Filter không làm mất phủ định/entity.
- **H0 TTS:** PCM source đúng rate/channels/dtype; WAV/raw header không lẫn; normalize không đổi nghĩa; dài quá trần được split an toàn; cancel đóng active body; 429 được quan sát và xử lý. Probe startup HF tương thích voice và request fields.
- **H1 bridge:** fuzz token split kể cả markup/think; chunk dưới trần **sau** normalize; offset/seq đơn điệu; mapping text đúng; cancel không flush; terminal đúng một lần; `Describe` đúng version/contract; held audio không leak trước commit.
- **Shared:** không có audio generation cũ; không task/worker/session state sau teardown; backend overload không phá session khác; log lỗi không có payload.

### 6.4 Đưa engine mới vào

Offline ASR WER/CER/entity, TTS blind listening/TTFA/RTF → license → conformance → shadow chỉ ASR khi đủ budget → canary 1–5% session/pool → promote/rollback. TTS dùng offline + canary, không double-synthesis shadow trong critical path.

H0 dùng pool/deployment khác cho A/B nếu chưa có dynamic routing; không hứa thay backend theo session bằng config stock. H1 session pin engine/voice/profile; không đổi giữa utterance. Rollback không migrate session state sống sang protocol khác.

### 6.5 Engine theo kịch bản

| Kịch bản | ASR | TTS | Gate |
|---|---|---|---|
| H0 baseline / H1 v1 research | Qwen3-ASR 0.6B/1.7B remote turn-final | VieNeu v3 Turbo | VRAM, cadence chung, license |
| Caption/compute-limited | Nemotron 3.5 | VieNeu | WS adapter riêng; single endpointing owner |
| CPU/edge | Gipformer/sherpa hoặc engine CPU đã đo | VieNeu ONNX/Supertonic/Kokoro vi | License, punctuation, latency |
| Commercial | Qwen/Whisper/ChunkFormer RNNT đã legal review | VoxCPM2/MOSS; VieNeu chỉ sau giải quyết license | Không dùng research profile để né gate |
| Two-pass | Partial + Qwen/Gipformer final-pass | Engine đang pin | P3; final revision đúng, budget riêng |

### 6.6 Khi đổi engine

ASR chạy lại corpus và exact-match entity, punctuation/flags/capacity. TTS chạy lại lexicon, nghe code-switch/prosody, policy/voice mapping, fixed-phrase cache và cancellation. Đo dưới tải chung ASR/TTS, không chỉ tổng VRAM. Thay HF upstream phải chạy lại control/transport/history tests dù model không đổi.

---

## 7. Hợp đồng điều khiển và API

### 7.1 Audio contract

| Cạnh | H0 | H1 |
|---|---|---|
| WebRTC uplink | Opus48k → HF16k mono | Giữ như H0 |
| HF → ASR HTTP | WAV PCM16 16k mono | Như H0 |
| LLM → TTS | Native HF sentence text | UTF-8 delta tới bridge |
| TTS → HF | PCM16 48k mono, stock resample16k | PCM16 48k mono + generation/chunk/offset |
| HF → WebRTC | PCM16k → Opus48k | PCM48k → Opus48k, không hạ xuống16k |
| WS harness | Native negotiated/base64 audio, đo contract thực tế | PCM48k output theo extension/negotiation đã test |

Ingress gap có marker/sample range; frame trùng/đến muộn bỏ; mất dài giữa lượt hỏi lại. Ngưỡng khởi điểm <100 ms chèn silence, ≥500 ms invalidate (**Synthesis**); khoảng giữa phải có policy config và test. HF stock gap handling chưa được xác minh; H1 bổ sung nếu thiếu. Turn buffer trần30s, teardown giải phóng audio nhạy cảm.

### 7.2 Native protocol và H1 extensions

**Stock (Reported):** `session.update`, `input_audio_buffer.append` (WS), `conversation.item.create`, `response.create`, `response.cancel`; response/transcription delta/done, response lifecycle, VAD speech events. WebRTC JSON trên `oai-events`; append audio bằng JSON bị từ chối trên transport này. `output_audio_buffer.clear` là native WebRTC clear server buffer; `conversation.item.truncate` hiện no-op.

Giữ event names và thứ tự native đã được SDK mục tiêu test. H1 không đổi toàn bộ thành schema client mới của bản gốc. Extensions phải opt-in/capability negotiated; client stock không bị ép nhận event lạ.

**Internal ID ledger (H1, Synthesis):**
- `session_id`: map với session native; `turn_id/revision`: map với turn tracker;
- `generation_id`: map với CancelScope generation và response key; không giả định các counter giống nhau nếu code thực tế khác;
- `response_id/item_id`: giữ ID native; `chunk_id/seq`: bridge cấp trong generation;
- event metric có `t_mono_ns` của host, host ID và version. Không trừ monotonic timestamps giữa host.

**Client extension đề xuất, chưa có trong stock:**

```text
↑ speech_to_speech.playback.ack.v1(response_id, generation_id, played_samples, rate)
↑ speech_to_speech.playback.stats.v1(response_id, jitter_buffer_ms, output_latency_ms)
↓ speech_to_speech.audio.contract.v1(response_id, generation_id, rate, channels, dtype)
↓ speech_to_speech.chunk.v1(response_id, generation_id, chunk_id, display_text,
                           start_sample, end_sample?)
```

`end_sample` có thể chưa biết lúc chunk bắt đầu, bổ sung khi chunk complete. Caption/history xử lý metadata trong RAM, mặc định không ghi payload log. Native transcript delta/done vẫn được phát với nội dung/version contract nhất quán.

### 7.3 Barge-in, cancellation và playback

**Stock (Reported):** generation/discard guard của `CancelScope`, response-keyed output, sole send loop, flush queue và WebRTC clear. Cancel no-active là no-op. Ordering giữa terminal/speech event/counter phải audit implementation; không coi README như chứng minh atomicity.

**H1 hardening (Synthesis):**
1. Tại miền control HF, invalidate generation/response key trước mọi asynchronous publication có thể gây race. Khóa/counter check nhất quán giữa producer và send loop.
2. Clear buffer phía server và drop mọi queued audio cũ, gửi lifecycle/clear events đúng native protocol ordering. Fade-out 5–10ms nếu không đưa thêm frame stale lên transport.
3. Hủy LLM stream, ASR request, bridge stream; bridge đóng engine body, vứt state, không flush.
4. Turn tracker mở/reopen user turn đúng semantics; giữ pre-roll, không mất lệnh ngắn.
5. Ghi keyed terminal đúng một lần; sau đó final heard history theo ledger/played ack với timeout và conservative fallback.

**Played offset:** WS AudioWorklet đếm mẫu render có thể chính xác trên timeline player đã instrument. WebRTC estimate từ sent sample count trừ jitter/output latency là **Unverified**: cần RTP/sample mapping, kiểm `getStats` là average hay instantaneous và tránh cộng hai latency chồng nhau. Không flush được audio đã trong browser jitter buffer. Khi estimate không đáng tin, giữ prefix chunk đã chắc chắn nghe hoặc không giữ assistant content; không tuyên bố word-accurate.

**Duration gate:** H0 barge-in dùng `min_speech_ms` (default384ms); `min_speech_continuation_ms` chỉ continuation, không phải barge-in. H1 có thể tách gate mới bằng patch: thử100–200ms nhạy hoặc300–500ms chống ồn, chọn bằng dữ liệu. Backchannel ba kết cục ngắt/ghi nhận/bỏ qua; không mặc định bỏ qua “ừ/vâng” trong xác nhận tool. Speaker lock/echo chỉ P2, không phải xác thực.

**Metric:** T_silence user bắt đầu nói → bot im ở client; T_release cancel → engine compute/slot kết thúc; false/missed interrupt; stale audio leak; số history chars/chunks discarded (không log text).

### 7.4 Patch boundaries và acceptance

| Patch | Ranh giới dự kiến, phải xác nhận implementation | Acceptance |
|---|---|---|
| P-A delta bridge | LMOutputProcessor/dispatcher + custom TTS handler | Delta không duplicate; tool/usage/terminal ordering giữ đúng |
| P-B audio48 | TTS output envelope, queue, resampler, WS/WebRTC pacer | PCM không qua16k; rate/channels đúng; pacing/clear không leak |
| P-C heard history | Conversation state, playback ledger, truncate handler | Không lưu phần chưa nghe; idempotent cancel/truncate; fallback có ledger |
| P-D control safety | Turn tracker, CancelScope, output hold, final publication | Reopen invalidates; commit đúng revision; cancel atomic validity |
| P-E capacity/trace | Queue limits, deadlines, model API errors, ID join | Overload bounded; trace đủ; teardown sạch |

Không cố định tên class/function ngoài những phần được tài liệu capture mô tả; code implementation đầy đủ chưa được inspect. Mỗi patch thành commit riêng, test trước merge; không viết pseudo-code actor rồi claim HF đã chạy theo actor đó.

### 7.5 Diarization

Một user/session: không đặt diarizer trong critical path. Speaker embedding P2 qua service riêng. Multi-participant/SFU là adapter mới; native optional diarization không tự chứng minh chất lượng tiếng Việt hay single-turn owner.

### 7.6 ASR HTTP contract

```text
POST /v1/audio/transcriptions
multipart: file=<WAV PCM16 16k mono>, model=<pinned>, language=<adapter-valid>,
           response_format=json
200: {"text": "..."}
429: bounded overload + Retry-After
```

`language=vi` phải map sang token engine thật sự chấp nhận; Nemotron có thể cần giá trị khác, chốt theo R1. Auth explicit, bind internal; facade không forward nhầm credential môi trường. H1 extra metadata có version và custom handler đọc; stock fallback chỉ dựa text contract.

### 7.7 H1 bridge RPC (Synthesis)

Giữ ý tưởng `tts.v1` của bản gốc, **không** coi là API native HF. Định nghĩa protobuf hoàn chỉnh ở bước hiện thực; schema dưới là contract logic, không phải code compile được.

```text
Describe() → engine/version/license, supported rates/channels/dtype,
             text max_chars/tags/code-switch, cancel, max_streams, policy versions
Synthesize(bidi stream), mỗi stream = một generation:
  client Start(session_id, turn_id, revision, generation_id, response_id,
               voice_id, output_rate=48000, speculative)
         TextDelta(seq, text)* → TextEnd | Cancel(reason)
  server TextChunk(chunk_id, display_text, spoken_text, segments, policy_versions)
         AudioChunk(chunk_id, seq, sample_offset, pcm16)*
         ChunkEnd(chunk_id, n_samples, timings, optional_segment_audio_timing)
         Done(status) | Error(code, retry_after_ms)
SynthesizePhrase(voice_id, phrase_id, version) → metadata + audio
```

Offsets theo generation, monotonic, byte count chia hết frame sample size; TextChunk tới trước audio cùng chunk. Text mapping theo Unicode codepoint hay byte phải chốt rõ trong proto/test. `spoken_text` chỉ để debug opt-in, HF không cần log nó. `segments` chỉ text offsets trừ khi timing có trường tường minh.

gRPC cancellation là tín hiệu cancel; service phải đo release engine, không chỉ ngừng gửi audio. Deadline propagation, `RESOURCE_EXHAUSTED`, queue budget và speculative priority là bắt buộc. HF custom handler map stream events vào native response events và ledger.

---

## 8. Latency: critical path, SLO và đo lường

### 8.1 Critical path

```text
speech cuối user → soft-end → turn gate/Smart Turn/grace
                              ‖ ASR → LLM → first clause [→ TTS nếu H1 L2]
  → commit/release → first send → network/jitter → audible sample đầu client
```

Mô hình **H1, Synthesis**, `hold` là thời gian gate thực tế kể từ soft-end, bao gồm lịch Smart Turn/timer đã đo:

```text
L1 v2v ≈ end→soft-end + max(hold, ASR + LLM→first clause) + TTS TTFA + playback
L2 v2v ≈ end→soft-end + max(hold, ASR + LLM→first clause + TTS TTFA) + playback
```

H0 thay first clause bằng native sentence batch và lịch speculation đã quan sát. Không gán công thức H1 vào stock khi chưa trace. Nếu compute nằm trong hold, tăng tốc ASR có thể không cải thiện D1; clause split giúp khi câu đầu dài, không xóa output gate.

### 8.2 SLO

| Metric | Mục tiêu |
|---|---|
| D1 client, lượt complete | P50≤1.5s, P95≤2.5s, mềm; cùng mục tiêu spec |
| D1 breakdown | Complete / incomplete-reopen / barge-in / idle-cold; H0/H1 tách riêng |
| TTS TTFA dưới tải | P95≤250–400ms, chốt target cụ thể sau PoC |
| TTS RTF | P95≤0.7 theo số stream mục tiêu |
| Client bot stop sau interrupt | Duration gate +≤200ms là khởi điểm, Chốt sau PoC |
| Audio stale | 0 ngoài đuôi jitter client đã đo; held precommit leak=0 |
| CPU responsiveness | Event/send-loop lag P99<5ms cho async loop; queue wait riêng cho workers |
| False cutoff / interruption | Báo cùng D1, không hạ grace chỉ để đạt latency |
| History H1 | Không giữ chunk chưa nghe trong ca replay; offset estimate có sai số công bố |

Không có số đo nào chứng minh stock/fork đã đạt. Nếu H0 không đạt đủ gate H1, gọi là MVP có giới hạn, không production parity.

### 8.3 Đòn bẩy

1. H0 `stream_batch_sentences=1`; H1 clause bridge, đo first-clause latency.
2. Warmup, max_streams, đo GPU nguội sau idle, khóa clock nếu GPU/host hỗ trợ và có lợi.
3. A/B grace800→600→400ms với false cutoff/reopen; không trộn default hai report.
4. H1 L2 chỉ khi gate-limited cao, reopen thấp và còn budget speculative.
5. Tune pacer audio lead/client prebuffer bằng jitter/underrun. Default196ms là packaged local client TTS OpenAI, không phải browser/WebRTC.
6. Prefix cache LLM, long-context TTFC; streaming ASR chỉ khi compute/caption cần.

### 8.4 Timeline

Join native session/response/item IDs với internal turn/revision/generation/chunk. Mốc: last user speech sample, soft-end, Smart Turn done, ASR dispatch/final, LLM request/first token, first clause, commit/release, TTS first byte, send first sample, client audible, cancellation, engine slot release, playback finalization.

**D1 client:** client lưu timeline mic capture sample index và map về `speech_end_sample` phía HF, đo audible sample trên cùng client clock. Mapping resample/RTP phải được instrument và kiểm; chỉ nhận sample index từ server chưa đủ. WS harness có thể đo chính xác hơn; browser WebRTC báo estimate và sai số nếu chưa instrument được playout.

Không trừ `t_mono_ns` giữa máy. Duration đo local từng service; distributed tracing nối spans, dùng clock alignment nếu thật sự cần tổng cross-host. Metrics: hold/slack/gate-limited/reopen, ASR queue/compute, LLM TTFT/TTFC, bridge TTFC/TTFA/gap, audio lead/underrun, model slots/429, T_silence/T_release, pool usage/rejection/teardown.

---

## 9. Triển khai, capacity và vận hành

### 9.1 Topology

```text
speech-node-01: 1×GPU24GB
  hf-s2s H0 hoặc H1 ×K             CPU, pool per process đã đo
  asr-api → asr-engine-qwen3       GPU; vLLM budget riêng
  tts-api → tts-engine-vieneu      GPU; stream slots riêng
  edge + coturn + otel            có thể host riêng
llm-host                          self-host OpenAI-compatible
```

Docker Compose trước. Chỉ edge/TURN lộ ra ngoài; backend API/internal signaling có auth/network policy. Container sidecar dùng DNS/network riêng hoặc shared pod namespace; `127.0.0.1` không nối container khác trong Compose bridge network. Bind loopback chỉ khi API/engine cùng network namespace.

HF chỉ load VAD/turn, kiểm actual GPU usage khi khởi động remote profile. Node scale tăng process/pool phải đo CPU/RAM overhead mỗi pipeline, không giả định một actor/task nhẹ như bản gốc.

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

### 9.3 Scale và capacity

- HF `num_pipelines` là trần session mỗi process (**Observed**); extra session bị từ chối. Edge route sticky, không gửi request session giữa nhiều process.
- Model API semaphore/admission dùng chung trên mọi HF process. Routing inference theo least-outstanding/replica health; preference local nếu giảm hop.
- Capacity node = min(pool session đã đo, ASR throughput tại P95, TTS streams/duty-cycle, CPU/RAM/network budget).
- TTS duty0.2–0.35 và estimates streams→users là **Reported**, không admission limit thực tế. Harness open-loop có idle6–20s để bắt cold-start/burst.
- Reused pipeline phải reset VAD/turn/history/CancelScope/bridge/voice/config; test disconnect→next user không rò dữ liệu.
- Scale node hoặc tách GPU khi ASR burst làm codec cadence vỡ, rồi mới cân nhắc orchestration hạ tầng phức tạp hơn.

### 9.4 Degradation

| Sự cố | H0 | H1 |
|---|---|---|
| Pool đầy | Native session-limit rejection + edge UI/retry | Như H0; metrics admission/pool |
| ASR429/timeout/empty | Không tạo LLM work; kiểm stock error semantics, proxy/app hỏi lại nếu tích hợp được | Typed policy hỏi lại qua cached response |
| TTS429 trước audio | Native error phải test; proxy retry giới hạn trước body nếu còn deadline | Route replica cùng engine/voice, retry trước output trong deadline |
| TTS lỗi sau audio | Dừng/fail response, không giả định resume | Kết thúc bảo thủ, fixed phrase mới; không retry nguyên chunk đã phát |
| Engine chết | Health/circuit breaker, restart | Như H0, cache/fallback response có ledger |
| LLM lỗi/length | Native failed/incomplete có rollback semantics, đo context thực tế | Heard prefix + terminal/fallback policy explicit |
| Uplink gap dài | Chưa claim stock recovery; disconnect/hỏi lại theo app policy đã test | Invalidate lượt, response hỏi lại qua lifecycle |
| Node quá tải | Edge từ chối session mới | Như H0; speculative work bị từ chối trước |

Cache câu hỏi lại/error nằm ở service hoặc HF patch; H0 không tự nhiên bypass được pipeline để phát cached audio. Phải test adapter invocation/lifecycle hoặc chấp nhận không có fallback audio. Đổi TTS engine chỉ ở ranh giới response, đổi luôn voice/policy; không đổi giữa utterance. Không migrate active session sang profile H0/H1 khác.

### 9.5 Privacy và bảo mật

- TLS và xác thực ở edge (token ngắn hạn cho signaling). Mạng nội bộ riêng; nên dùng mTLS giữa các service.
- Engine chỉ lộ trong network namespace/internal network có policy; loopback khi cùng namespace. NeMo health/playground có thể không auth; VieNeu API key nếu cần truy cập ngoài loopback. HF stock API cũng cần edge auth, không chỉ backend auth.
- Không dùng STUN/TURN công cộng. Không dùng LLM proxy của HF s2s.
- Giới hạn theo session: thời lượng session, độ dài lượt (30 s), tốc độ event trên DataChannel, kích thước message.
- Reference clone chỉ được nạp qua pipeline quản trị, có bản ghi consent. Client không được trỏ tới URL hay path reference. Quyền với preset voice không bao gồm reference do người dùng cung cấp (**Reported**).
- Log mặc định content-free: độ dài, loại, version, ID. Transcript, `display_text`/`spoken_text`, audio và speaker embedding chỉ vào **corpus opt-in** có kiểm soát truy cập, retention và consent. `lexicon_hits` chỉ ghi id của mục, không ghi term.
- Turn buffer và embedding giải phóng đúng hạn. Không log payload trong handler exception.
- Watermark (VieNeu Perth) là một quyết định chính sách và được ghi vào config.

### 9.6 Admission, queue và backpressure

H0 có per-pipeline STT queue được mô tả; không suy ra toàn tuyến bounded. H1 audit/patch theo budget dưới đây (**Synthesis**):

| Cạnh | Budget / policy |
|---|---|
| Session→HF pool | Trần pool; edge reserve/release đúng disconnect |
| Transport→VAD | Vài trăm ms audio; drop-oldest + gap marker; không drop im lặng không marker |
| STT pending | Bounded; final order, superseded revision removed; global API semaphore riêng |
| LLM delta→bridge | Credit theo lookahead1–2clause/bytes; overall timeout khi peer không tiến triển |
| Bridge engine queue | 1active +1pending clause/generation, trần global riêng |
| Held speculative | Trần text/audio/duration; đầy thì pause speculative hoặc cancel, không phát trước gate |
| TTS audio→send loop | MAX_LEAD1–2s khởi điểm + trần RAM per chunk/session |
| Control/terminal | Hàng ưu tiên, không drop cancel/clear/terminal; event-rate limit tại ingress |
| Smart Turn executor | Bounded/latest relevant request; metric queue wait |

Backpressure khi đọc HTTP/gRPC không chắc dừng LLM/GPU compute phía server; đo và cancel nếu budget hết. Không vừa yêu cầu buffer bounded vừa đọc engine không giới hạn: dùng bounded synthesis-ahead staging có trần byte/duration, tạm ngừng request clause mới. Một active clause bị chặn phải có timeout/cancel để không giữ slot vô hạn.

### 9.7 Config, readiness và fork runbook

- Pin upstream revision, fork revision, image digest, weights/runtime, G2P, voicepack, bridge protocol, normalizer và lexicon; stage offline.
- H0 config CLI chỉ từ `--help` phiên bản pin: `serve`, `--stt openai`, `--tts openai`, endpoints/model/voice/rate, LLM handler phù hợp, pool và sentence batch. Không invent flag H1; đăng ký custom handler/config trong fork và test parser trước publish command.
- Explicit STT/TTS/LLM API keys; không để fallback `OPENAI_API_KEY` vô tình đi tới self-host endpoint. Không bật public LLM proxy.
- Tắt progressive ASR khi baseline turn-final, tắt transcript logging và hidden history compaction; kiểm actual log/request count thay vì chỉ config.
- Readiness gồm backend warmup, health, voice clone re-register, cache và HF startup probes. Với VieNeu, slot/cold GPU và scheduler503 phải được theo dõi. Cache câu clone theo consent/retention.
- GPU persistence/clock ở host nếu được hỗ trợ; đo lợi ích/power tradeoff. Không áp dụng clock command mặc định cho mọi GPU.
- Rollout drain sessions, canary theo profile. Khi rebase HF, chạy lại native WS/WebRTC/SDK contract, patch suite và license/dependency audit; không auto-promote vì upstream tests pass.
- Revert image/fork/config đồng bộ; session sống tiếp tục trên phiên bản cũ tới drain hoặc reconnect theo policy, không ép map state khác version.

---

## 10. Đánh giá và release gates

### 10.1 H0: PoC/MVP acceptance

1. Remote ASR/TTS hoạt động, đúng format/auth/voice; HF không load speech model nặng. Silence startup probes không thay test thật.
2. Đo R0–R5×C1–C4 trong spec, D1 và stage timeline; sentence batch1, progressive ASR/compaction đã kiểm thực tế.
3. Barge-in/cancel/reopen không leak stale audio ngoài browser jitter tail; history limitation được quan sát và ghi nhận, không giấu.
4. Multi-session concurrency1/4/8/16 tới capacity đích, pool rejection và shared GPU overload; session reuse không rò state/content.
5. Self-host ICE/LLM/model, edge auth, content-free logs, consent/license profile.
6. Product owner chấp nhận bằng văn bản 16kHz internal, sentence latency và playback-history gap nếu dùng ngoài PoC. Không dùng acceptance này để tuyên bố H1 đạt.

### 10.2 H1: production gates bắt buộc

1. **ASR corpus:** Bắc/Trung/Nam, code-switch, số/tên/địa chỉ/phủ định, “không/dừng”, noise/echo/music/silence; WER/CER/entity exact match, latency theo độ dài. Telephony8k là dataset thử riêng, không claim đã support ingress.
2. **TTS:** golden normalizer100%, fuzz token/think/markup/chunker,150–300prompt blind listening10–20người Việt; semantic fidelity, code-switch/prosody, lexicon, chunk transitions. Rate48k thật, không hidden16k conversion.
3. **Control replay:** soft-end→continuation→revision, ASR cũ đến muộn, commit/cancel cùng tick, queued speculative output, no-active cancel, disconnect trong upload/read, session reuse. Assert no precommit/stale output, no duplicate final/terminal, no side effects trước commit.
4. **History playback:** ngắt giữa chunk, rewritten money/date span, response.done trước drain, mất ACK, jitter estimate sai, repeated truncate và wrong item. Không có within-chunk timing → chỉ giữ hoàn tất chunk. Cache/fallback cũng đúng heard history.
5. **Transport/SDK:** native WS và WebRTC, negotiation audio48/extensions, transcript delta/done, tool parts/usage ordering, clear, browser jitter tail. SDK capture pin0.14.3 chỉ là Reported coverage; chạy phiên bản client production thật.
6. **Load/failure:** open-loop idle6–20s, concurrency1/4/8/16, burst và cold,429/503/timeout/slow client/loop lag; bounded RAM/queues, teardown workers sạch, soak1000sessions, T_release và T_silence. Không chỉ `asyncio.all_tasks()` vì HF có workers/threads.
7. **Security/license/ops:** auth tất cả exposed routes, no public STUN, log/exception payload audit, model/voice consent, backend health/restart/re-register, promote/rollback/rebase tests.

**H1 release:** qua cả7gate, SLO §8 theo workload và capacity đích, contract suite chạy CI trên upstream/fork pin. Chưa có bằng chứng hiện tại đạt bất kỳ gate runtime nào. Nếu phải thay phần lớn control hoặc không qua history/audio tests, dừng fork và chọn bản orchestrator riêng; không triển khai hybrid hai owner.

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

## 12. Lộ trình từ PoC tới production HF

### 12.1 Phases

| Phase | Nội dung | Điều kiện xong |
|---|---|---|
| P0 H0 | HF stock+remote ASR/TTS, sentence batch1, self-host ICE, log/tap; R0–R5×C1–C4, startup probes và pool/load | §10.1, có timeline và bản ghi limitations |
| P1a fork spike | Inspect code implementation đầy đủ; thử P-A delta, P-B48k, P-C history; audit control P-D | Replay/contract mini-suite chứng minh ranh giới patch; ước lượng maintenance |
| P1b H1 | Pin fork, production bridge/history/audio, capacity/trace/error policies; L1 | §10.2, SLO workload đích; không promote chỉ vì demo chạy |
| P2 | Scale node, engine challenger, L2, streaming adapter khi cần, echo/speaker lock/denoise A/B | Canary giữ SLO/control correctness |
| P3 | Two-pass, tool side effects với xác nhận, telephony/SFU khi có nhu cầu | Gate riêng; một owner turn xuyên suốt |

### 12.2 Quyết định cần số đo

- ASR Qwen0.6B/1.7B/Nemotron; TTS preset/clone; license commercial.
- Smart Turn CPU/GPU, grace/max-wait origins, false cutoff và short commands.
- HF pool size/process count, CPU/RAM/threads mỗi pipeline, model max_inflight/max_streams, GPU contention/cold cadence.
- Stock speculation lịch thực tế; H1 L1/L2, held buffer budget/reopen waste.
- Chunker first_min/hard_max sau normalize; first-clause và inter-chunk gaps.
- WS/WebRTC played-offset accuracy và fallback heard-history policy.
- LLM cancellation/compute release; backend quality flags/protocol/token vi.
- Fork delta/tool/usage/terminal ordering, audio contract và upstream rebase cost.

### 12.3 Khi nào chuyển về bản gốc

Chuyển về [thiết kế orchestrator riêng](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) nếu code audit cho thấy phải thay phần lớn session/control plane, không thể làm truncate/generation safety đúng trong miền native, hoặc SDK/audio/history regressions không được giữ ổn định bằng CI. Chuyển kiến trúc là quyết định tường minh; không âm thầm thêm actor bên cạnh HF.

---

## 13. Giới hạn của tài liệu

- Đây là nhánh thiết kế HF, không bản triển khai hoặc chứng nhận production. Chưa model/service/session nào được chạy hay đo.
- Capture mô tả docs/defaults; implementation/tests đầy đủ không có trong package đã đọc. Hành vi Stock là Reported/Observed, không independently verified.
- H1 delta handler,48k downlink, playback history, extensions và safety patches chưa hiện thực. Không có CLI stock cho tất cả tính năng này.
- H0 không đạt đầy đủ production v2: mất bandwidth sau16k downsample, native sentence split và no-op truncate.
- WebRTC played offset/D1 instrumentation và within-chunk alignment là unresolved; text offsets không thay audio timestamps.
- Shared GPU cadence, HF per-pipeline overhead, dependency imports, cancellation compute và client compatibility phải đo.
- License không phải tư vấn pháp lý; mâu thuẫn VieNeu chưa được giải quyết bằng việc đổi orchestrator.
- Nguồn HF pin revision capture; không khẳng định tương đương upstream hiện tại. Model/runtime metrics giữ nhãn Reported và stale_after của nguồn.

---

## Phụ lục A. Khác biệt với bản production v2

| Phần | Bản gốc | Bản HF |
|---|---|---|
| Owner/orchestration | Orchestrator actor riêng | Miền native HF, audit/patch synchronization |
| ASR API | gRPC asr.v1 | OpenAI-compatible HTTP; streaming adapter tùy chọn |
| TTS API | gRPC tts.v1 ngay từ đầu | H0 HTTP; H1 custom delta handler+gRPC bridge |
| Audio |48k production mặc định | H0 internal16k; H1 patch toàn downlink48k |
| History | Heard history theo played offset | H0 no-op truncate; H1 fork ledger/truncate |
| Session | Actor nhẹ, admission thiết kế riêng | Pool PipelineUnit + external shared-model admission |
| Lộ trình | PoC HF → rời HF | PoC HF → fork spike → HF production nếu qua gate |
| Rollback | Registry/service config | Registry+fork/protocol/image version; drain sessions |

Các phần model ASR/TTS, VAD/Smart Turn và mâu thuẫn bằng chứng được kế thừa để so sánh cùng nền. API/runtime/control mới là Synthesis. Liên kết từ chương8/12/16–20 vẫn trỏ về bản gốc, không tự động đổi sang bản HF này.

---

## Phụ lục B. Tham chiếu

- [Thiết kế production v2 gốc](thiet-ke-pipeline-speech-to-speech-tieng-viet.md).
- [Spec PoC Phase1](spec-poc-speech-to-speech-tieng-viet.md).
- [ASR/STT tiếng Việt](lua-chon-va-thiet-ke-asr-stt-tieng-viet-realtime.md), [TTS tiếng Việt](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md).
- [Survey VAD/turn/denoise](survey-vad-turn-detection-denoise-tieng-viet.md), [Survey cầu text→speech](survey-cau-text-to-speech-tien-hau-xu-ly-sau-llm.md).
- HF: [Pipeline](../wiki/speech-to-speech-pipeline.md), [CLI/defaults](../wiki/speech-to-speech-cli-and-defaults.md), [Remote backends](../wiki/speech-to-speech-openai-compatible-backends.md), [Realtime engine](../wiki/speech-to-speech-realtime-engine.md), [Latency](../wiki/speech-to-speech-latency-instrumentation.md), [Browser demo](../wiki/speech-to-speech-browser-demo.md).
- Bất biến: [Chương16 audio contract](chuong-16-dataflow-end-to-end-va-audio-contract.md), [17 turn/cancel](chuong-17-turn-taking-event-barge-in-va-cancellation.md), [18 async/streaming](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md), [19 bridge](chuong-19-cau-text-to-speech-chunker-normalizer-lexicon.md), [20 latency](chuong-20-latency-dinh-nghia-critical-path-do-luong.md).
- Model/API: [Qwen3-ASR](../wiki/qwen3-asr-family.md), [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md), [VieNeuTurbo](../wiki/vieneu-tts-v3-turbo.md), [VieNeu speech API](../wiki/vieneu-tts-openai-speech-api.md), [Streaming runtime](../wiki/vieneu-tts-streaming-runtime.md), [Docker](../wiki/vieneu-tts-docker-deployment.md), [VietNormalizer](../wiki/vietnormalizer.md).
