# Chương 16. Dataflow end-to-end và audio contract 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần V (Ghép pipeline).
> **Chương trước:** [Chương 15. Kiến trúc: cascade, end-to-end full-duplex và lai](chuong-15-kien-truc-cascade-end-to-end-full-duplex-va-lai.md). **Chương tiếp theo:** [Chương 17. Turn-taking, event, barge-in và cancellation](chuong-17-turn-taking-event-barge-in-va-cancellation.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §3 nguyên tắc 4 (mỗi backend khai báo audio contract), §4 (kiến trúc tổng thể), §7.1 (audio ingress), §7.2 (event schema). Gián tiếp phục vụ §8.1 (critical path cần timestamp đúng) và §10 gate 5 (contract tests).
> **Cơ sở:** sample index, ring buffer, reblocking, bội chung nhỏ nhất của các kích thước khối, Nyquist và aliasing, sequence number, jitter, PLC là **kiến thức nền chung**, không phải claim lấy từ nguồn wiki. Hợp đồng audio của từng backend lấy từ wiki và gắn nhãn bằng chứng: [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md) và các trang con ([Realtime Engine](../wiki/speech-to-speech-realtime-engine.md), [OpenAI-Compatible Backends](../wiki/speech-to-speech-openai-compatible-backends.md), [Browser Demo](../wiki/speech-to-speech-browser-demo.md), [CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md)), [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md), [VieNeu Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md), [Silero VAD](../wiki/silero-vad.md), [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md). Thông tin vendor là **Reported** (wiki chưa chạy lại). Hai script ở "Phụ lục chương" chạy bằng Python thuần ngày 2026-10-07 (**Reproduced** cho phép tính và hành vi của chính script, không phải đo model hay mạng thật). Suy luận và thiết kế của tác giả là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Lần theo một khung audio từ mic tới loa, gọi tên được **từng cạnh** của dataflow, và tại mỗi cạnh nói được: dữ liệu có dạng gì, sample rate, số kênh, dtype, đơn vị đóng gói, kích thước, **ai sở hữu state**, và kết thúc hay huỷ bằng cách nào.
2. Giải thích vì sao VAD (32 ms), transport (20 ms), ASR (160–320 ms), text (theo mệnh đề) và TTS (chunk 320 ms) dùng đơn vị khác nhau, và nối chúng bằng **một timeline chung theo chỉ số mẫu** cùng ba loại adapter: reblocker, accumulator theo sự kiện, pacer.
3. Thiết kế ring buffer, pre-roll, turn audio buffer và các buffer downlink với kích thước tính được, vòng đời rõ ràng và điểm giải phóng bộ nhớ.
4. Giữ timestamp đúng khi mạng mất gói, tới muộn hoặc dồn cục; chọn được policy cho gap.
5. Liệt kê state theo session và chứng minh không state nào bị dùng chung giữa các user.
6. Dùng đúng sáu định danh `session_id`, `turn_id`, `revision`, `generation_id`, `chunk_id`, `sequence`: ai tạo, khi nào tăng, chặn lỗi gì.
7. Giải thích vì sao một pipeline có thể bị khoá trần băng thông ở 16 kHz dù TTS xuất 48 kHz, nghe ra sao, và khi nào chấp nhận được.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Vẽ được sơ đồ: tại mỗi cạnh là sample rate nào, dtype nào, chunk bao nhiêu ms, ai giữ state?
- Q2. Vì sao VAD (32 ms), transport (20 ms), ASR (160–320 ms), text (theo mệnh đề) và TTS (chunk audio) dùng đơn vị khác nhau, và nối với nhau ra sao?
- Q3. Pre-roll lấy từ đâu? Turn audio buffer giữ bao lâu?
- Q4. Giữa một lượt nói, 5 frame uplink liên tiếp (100 ms) bị mất. Nên nối thẳng các frame còn lại hay chèn im lặng? Mỗi cách làm sai cái gì?
- Q5. Hai user được phục vụ bởi cùng một `VADIterator` (hoặc cùng một ASR streaming cache). Chuyện gì xảy ra?
- Q6. Sáu định danh khác nhau ở phạm vi nào? Định danh nào chặn "bot phát tiếp câu cũ sau khi bị ngắt"?
- Q7. Vì sao trong HF s2s với `--tts openai`, giọng VieNeu 48 kHz đến tai người nghe chỉ còn băng thông 8 kHz? Điều đó làm hỏng thanh điệu không?

---

## 16.1 Bức tranh: một khung audio đi từ mic tới loa

Sơ đồ dưới đây là kiến trúc ở §4 của tài liệu thiết kế, được "mở" ra tới mức cạnh dữ liệu.[^design] Mỗi mũi tên có nhãn là một **cạnh** mà §16.3 sẽ mô tả contract. `U` là uplink (audio người dùng), `C` là sự kiện điều khiển, `T` là text, `D` là downlink (audio bot).

```text
CLIENT (browser)                         GATEWAY: 1 đối tượng Session cho mỗi user                 BACKEND (giữ weights)
────────────────                         ──────────────────────────────────────────               ─────────────────────
mic + AEC/NS/AGC
 │ U0  float32, rate của AudioContext (thường 48 kHz), quantum 128 frame
 ▼
capture worklet: resample→16 kHz, f32→s16, gom 20 ms, gắn seq + capture time
 │ U1  s16le 16 kHz mono, 320 mẫu = 640 byte / frame
 ▼
WebSocket binary (MVP)  ── hoặc ── WebRTC Opus 48 kHz, RTP 20 ms
 │ U2
 ▼
                                         decode (ghép byte lẻ, s16→f32 / Opus→PCM)
                                          │ U3  f32 [-1,1], rate gốc của transport
                                          ▼
                                         resample có state → 16 kHz (nếu cần)
                                          │ U4  f32 16 kHz mono, liên tục
                                          ▼
                                         RING BUFFER 16 kHz, đồng hồ mẫu w (≥ 8 s)
                                          ├─U5v─► reblock 512 ─► [denoise?] ─► Silero VAD ─► prob/32 ms ─┐
                                          ├─U5s─► cửa sổ ≤ 8 s cuối ─► Smart Turn ─► complete/incomplete ─┤
                                          ├─U5a─► chunk 160/320 ms ─► ASR streaming (cache/session) ──┐   │
                                          └─U5t─► TURN BUFFER (pre-roll + lượt) ─► ASR turn-final ────┤   │
                                                                                                       │   ▼
                                                                  C1 asr.partial / asr.final ─────────►TURN OWNER
                                                                                                    (turn_id, revision)
                                                                                                       │ C2 turn.commit
                                                                                                       ▼
                                         LLM client (stream, cancel) ◄─────────────────────────────────┘ ──► LLM server
                                          │ T1 token delta (generation_id)
                                          ▼
                                         clause chunker ─T2 text.chunk(raw_text, chunk_id)─► normalizer + lexicon
                                          │ T3 spoken_text (cùng chunk_id)
                                          ▼
                                         TTS adapter ─D1 POST /v1/audio/speech hoặc SDK─────────────────────► TTS (VieNeu)
                                          ◄─D2 s16le 48 kHz mono, chunk 160/320 ms, X-Sample-Rate ─────────────┘
                                          │ D3 audio.start(meta) + audio.chunk(generation_id, chunk_id, sequence)
 ┌────────────────────────────────────────┘ D4 WS binary / WebRTC Opus
 ▼
client queue có giới hạn, pre-buffer 150–300 ms, bỏ chunk khác generation
 │ D5  f32, resample một lần về rate AudioContext
 ▼
AudioWorklet playback, đếm mẫu đã render ─D6─► loa
 │ C3 audio.played(generation_id, played_sample_offset)
 └───────────────────────────────────────► gateway: cắt history theo phần đã phát
```

Ba nhận xét quan trọng trước khi đi vào chi tiết (**Synthesis**):

1. **Có hai đồng hồ phần cứng độc lập.** Uplink được "đánh nhịp" bởi mic: 20 ms audio tới sau mỗi 20 ms thời gian thật. Downlink được đánh nhịp bởi loa: loa tiêu thụ đúng 48 000 mẫu mỗi giây. Ở giữa, TTS sinh nhanh hơn thời gian thật (RTF < 1), nên luôn cần một buffer có giới hạn để hấp thụ chênh lệch (Chương 6).
2. **Ring buffer là "nguồn sự thật" về audio của user.** VAD, Smart Turn, ASR streaming và turn buffer không nhận audio "đẩy" vào từng cái một, mà mỗi cái đọc một cửa sổ khác nhau trên **cùng một timeline**. Đây là cách nối các đơn vị khác nhau (§16.4).
3. **Turn owner là nút duy nhất đổi trạng thái lượt.** VAD, ASR và TTS chỉ phát tín hiệu lên nó (nguyên tắc 2 của tài liệu thiết kế).[^design] Chương này chỉ đề cập owner ở mức dataflow; state machine chi tiết nằm ở Chương 17.

---

## 16.2 Ngôn ngữ mô tả dataflow

### 16.2.1 Nút, cạnh và owner

- **Nút** là một bước xử lý: decode, resample, VAD, ASR, chunker, TTS adapter, playback.
- **Cạnh** là chỗ dữ liệu đi từ nút này sang nút khác. Một cạnh có thể là lời gọi hàm trong cùng process, một `asyncio.Queue`, một socket, hay một HTTP request.
- **Owner của state** là nút được phép sửa state đó. Ví dụ: hidden state của Silero chỉ do nhánh VAD của session sửa; `generation_id` chỉ do turn owner tăng.

Quy tắc thực hành (**Synthesis**): mọi cạnh **đi qua ranh giới** (process, mạng, ngôn ngữ lập trình, thư viện bên thứ ba) đều phải có contract viết ra giấy. Cạnh nội bộ trong cùng một module vẫn nên có `assert` ở đầu vào.

### 16.2.2 Ba mặt phẳng dữ liệu

| Mặt phẳng | Dữ liệu | Nhịp | Mất mát chấp nhận được? | Ví dụ cạnh |
|---|---|---|---|---|
| **Audio** | Mẫu PCM liên tục | Theo đồng hồ phần cứng (mic, loa) | Có, nếu được che (PLC, im lặng) và **được đánh dấu** | U0–U5, D2–D6 |
| **Điều khiển** | Sự kiện rời rạc có định danh | Theo sự kiện | **Không.** Mất `turn.commit` hay `client.clear` là bug logic | C1–C3, `response.cancel`, `client.clear` |
| **Text** | Chuỗi UTF-8, delta hoặc mệnh đề | Theo tốc độ sinh của model | Không | T1–T3 |

Đặt mỗi mặt phẳng lên kênh phù hợp với nó. Trên WebSocket, dùng binary frame cho audio và text frame JSON cho điều khiển. Blueprint đề xuất đúng cách này: audio PCM16 16 kHz binary, JSON nhỏ mang `type` và `sequence`.[^blueprint] Trên WebRTC, audio đi media track, sự kiện đi data channel. HF s2s dùng `oai-events` data channel cho JSON và từ chối `input_audio_buffer.append` trên transport WebRTC (**Reported**).[^engine]

### 16.2.3 Push, pull và backpressure

- Uplink là **push**: client đẩy audio theo nhịp mic. Gateway phải tiêu thụ kịp, nếu không backlog tăng và mọi quyết định VAD đến muộn.
- Downlink là **pull** ở đầu cuối: loa kéo mẫu theo nhịp của nó. TTS đẩy nhanh hơn nhịp đó, nên queue phía client phải có giới hạn trên và cơ chế "credit" (Chương 8 §8.5).
- Giữa hai đầu, mọi queue đều phải **bounded**. Queue không giới hạn biến một sự cố chậm tạm thời thành độ trễ vĩnh viễn (**Synthesis**).

---

## 16.3 Audio contract cho từng cạnh

### 16.3.1 Một contract gồm những gì

Nguyên tắc 4 của tài liệu thiết kế yêu cầu mỗi backend khai báo **sample rate, dtype, số kênh, framing và cách cancel**.[^design] Viết đầy đủ, một audio contract có chín trường:

| Trường | Câu hỏi | Ví dụ sai thường gặp |
|---|---|---|
| `sample_rate` | Bao nhiêu mẫu mỗi giây? | Phát 48 kHz ở 24 kHz → giọng chậm và trầm gấp đôi |
| `channels` + layout | Mono? Stereo interleaved hay planar? | Đọc stereo interleaved như mono → dài gấp đôi |
| `sample_format` | `s16le`, `f32le`? signed? endian? | Đọc `s16le` như `f32` → nhiễu trắng rất lớn |
| Container | PCM thô, WAV header, Opus, base64? | Ghép header WAV vào giữa stream PCM → tiếng "tách" |
| Framing | Đơn vị mỗi message: 20 ms, 512 mẫu, chunk 320 ms, SSE event? | Giả định chunk đều nhau; chunk cuối thường ngắn hơn |
| Metadata | `sequence`, timestamp, định danh | Không có sequence → không phát hiện được mất gói |
| Kết thúc | Báo hết stream thế nào? | Chờ `done` mà server chỉ đóng body |
| Cancel | Huỷ giữa chừng thế nào, có giải phóng tài nguyên phía server không? | Đóng HTTP nhưng GPU vẫn chạy tiếp |
| Lỗi/quá tải | Mã lỗi, backpressure | Không xử lý `429` → mất câu trả lời |

### 16.3.2 Uplink: từ mic tới các nhánh phân tích

| Cạnh | Dữ liệu | Rate / kênh | dtype | Đơn vị | Kích thước tiêu biểu | State và owner | Kết thúc / lỗi |
|---|---|---|---|---|---|---|---|
| **U0** mic → capture node | PCM sau AEC/NS/AGC của trình duyệt | Rate của `AudioContext` (thường 48 kHz), mono nếu `channelCount: 1` | f32 [-1, 1] | Render quantum 128 frame (2,67 ms @48 kHz) | 512 byte/quantum | Trình duyệt | Mất quyền mic, đổi thiết bị |
| **U1** worklet → transport | PCM đã resample | **16 kHz mono** | `s16le` | **20 ms = 320 mẫu** + `seq` + capture time | 640 byte/frame | Client: resampler có state, bộ đếm `seq` | Ngừng gửi khi tắt mic, gửi sự kiện đóng |
| **U2** transport | WS binary; hoặc WebRTC Opus | WS 16 kHz; WebRTC 48 kHz | WS `s16le`; Opus nén | 1 message/frame; RTP 20 ms | WS 256 kbps payload | Kết nối | Close/timeout → teardown session |
| **U3** decode | PCM | Rate của transport | f32 | Tuỳ message | – | Session: byte lẻ còn dư | Gap → policy §16.6.3 |
| **U4** resample → ring | PCM chuẩn của gateway | **16 kHz mono** | f32 | Liên tục | 64 KB/s f32 | Session: lịch sử bộ lọc resampler | – |
| **U5v** ring → VAD | Khối cố định | 16 kHz (8 kHz: 256 mẫu) | f32 | **512 mẫu = 32 ms** | 2 048 byte | Session: `VADIterator`, `reset_states()` khi hết lượt | – |
| **U5s** ring → Smart Turn | Cửa sổ trượt | 16 kHz | f32 | ≤ **8 s** audio cuối, gọi khi có ứng viên end | ≤ 512 KB | Không giữ state giữa các lần gọi (classifier) | – |
| **U5a** ring → ASR streaming | Chunk của model | 16 kHz | f32 | **160 / 320 ms** (2 560 / 5 120 mẫu) + lookahead của model | 10–20 KB | Session: encoder/decoder cache | Giải phóng cache sau final hoặc khi đóng session |
| **U5t** ring → turn buffer → ASR turn-final | Một lượt | 16 kHz | f32 (hoặc WAV PCM16 khi gửi HTTP) | Cả lượt: pre-roll + speech + pad | ~320 KB cho 5 s | Turn: mở lúc `speech_start`, đóng khi commit xong | Trần độ dài → buộc endpoint |

Nguồn cho các giá trị (**Reported** trừ khi ghi khác):

- WebSocket PCM16 16 kHz mono, binary frame 20–32 ms, không dùng base64: tài liệu thiết kế §5.1 và blueprint.[^design][^blueprint]
- Silero nhận 8 hoặc 16 kHz; từ v5, cửa sổ cố định 512 mẫu (16 kHz) hoặc 256 mẫu (8 kHz); model nhận tensor float32 1-D; mỗi session một `VADIterator`, gọi `reset_states()` khi hết lượt.[^silero]
- Smart Turn chạy classifier trên 8 s audio cuối sau 200–300 ms im lặng.[^wikidesign]
- Nemotron thử chunk 160/320 ms; ASR chuẩn của gateway là 16 kHz mono (§7.1, **Synthesis**).[^design]
- WebRTC trong HF s2s: Opus 48 kHz, resample sang/từ pipeline 16 kHz bằng resampler có state, RTP 20 ms.[^engine]

### 16.3.3 Mặt phẳng text và điều khiển

| Cạnh | Dữ liệu | Đơn vị | Định danh bắt buộc | Owner | Ghi chú |
|---|---|---|---|---|---|
| **C1** ASR adapter → turn owner | `asr.partial(text, stable_prefix?)`, `asr.final(text, model_id, language, quality_flags)` | Một hypothesis | `turn_id`, `revision`, `audio_range` theo chỉ số mẫu | ASR adapter | Lột token đặc biệt (`<vi-VN>`, `<EOU>`) trước khi đẩy lên (Chương 11) |
| **C2** turn owner → orchestration | `turn.commit(turn_id, revision)` | Một lần cho mỗi lượt | `turn_id`, `revision` | Turn owner | Side effect chỉ sau mốc này (nguyên tắc 5)[^design] |
| **T1** LLM → chunker | Token delta | Token/nhóm token | `generation_id` | LLM client | Huỷ = đóng stream; kiểm stale theo từng delta |
| **T2** chunker → normalizer | `text.chunk(raw_text)` | **Mệnh đề**: flush ở `.?!…;:` hoặc xuống dòng; chunk đầu cắt ở dấu phẩy khi ≥ ~25 ký tự; gộp mảnh < 8 ký tự | `generation_id`, `chunk_id` | Chunker | Giữ `raw_text` cho hiển thị và history |
| **T3** normalizer → TTS adapter | `spoken_text` | Cùng mệnh đề | `generation_id`, `chunk_id` | Normalizer | NFC, số/tiền/ngày, viết tắt, lexicon (Chương 19) |
| **C3** client → gateway | `audio.played(generation_id, played_sample_offset)` | Định kỳ và khi bị ngắt | `generation_id` | Client | Offset đo theo rate của `audio.start` |

Quy tắc chunker là **Reported** từ report, dùng làm giá trị khởi điểm.[^design] Event schema là **Synthesis** của tài liệu thiết kế, không phải schema của vendor nào.[^design]

### 16.3.4 Downlink: từ TTS tới loa

| Cạnh | Dữ liệu | Rate / kênh | dtype | Đơn vị | Kích thước tiêu biểu | State và owner | Kết thúc / cancel |
|---|---|---|---|---|---|---|---|
| **D1** adapter → TTS | HTTP `POST /v1/audio/speech` (`input`, `voice`, `response_format=pcm`, `stream_format=audio\|sse`, `sample_rate`) hoặc SDK `infer_stream` | Xin rate: 48 000 (gốc), 24 000, 16 000, 8 000 | – | Một request cho mỗi `chunk_id` | `input` ≤ 20 000 ký tự | Adapter: handle request theo `generation_id` | `429` + `Retry-After` khi hết slot |
| **D2** TTS → adapter | PCM thô (chunked) hoặc SSE `speech.audio.delta` (base64) | **48 kHz mono** mặc định | HTTP: **`s16le`**; SDK: **f32** | Frame codec 80 ms; chunk đầu 2 frame (GPU) hoặc 4 frame (CPU), sau đó 4 frame = **320 ms** | 30 720 byte/chunk s16 @48 kHz | Server TTS: slot | Chunked: đóng body; SSE: `speech.audio.done` kèm `usage`. Cancel: đóng kết nối (server-side best-effort) |
| **D3** adapter → transport | `audio.start(generation_id, format, sample_rate, channels)` rồi `audio.chunk(generation_id, chunk_id, sequence, payload)` | Giữ **rate gốc** | Tuỳ transport | Có thể cắt lại 20–40 ms để pacing | – | Session: bộ đếm `sequence`, bảng `chunk_id → [mẫu đầu, mẫu cuối)` | `response.cancel` → ngừng gửi ngay |
| **D4** transport → client | WS binary kèm header nhỏ; hoặc WebRTC Opus 48 kHz | WS: rate gốc; WebRTC: 48 kHz | WS: `s16le`; Opus | WS: tuỳ; WebRTC: RTP 20 ms, gửi im lặng khi rảnh | 768 kbps payload cho 48 kHz s16 | Kết nối | `client.clear(generation_id)` |
| **D5** client queue | PCM đã decode | Resample **một lần** về rate `AudioContext` | f32 | Chunk | Trần ~2 s | Client: `generation_id` hiện tại, `last_seq` | Flush khi `clear`; bỏ chunk khác generation |
| **D6** worklet → loa | PCM | Rate `AudioContext` | f32 | Quantum 128 frame | – | Client: số mẫu đã render (không tính im lặng khởi động và underrun) | Fade ngắn khi cắt để tránh click |

Nguồn (**Reported**):

- VieNeu HTTP: `response_format` `pcm` là s16le mono không header, `wav` có header với độ dài "unknown"; `sample_rate` mặc định 48 000, nhận 24 000/16 000/8 000 và resample từng chunk bằng soxr; header `X-Request-Id`, `X-Sample-Rate`; SSE `speech.audio.delta` chứa base64 PCM s16le, kết thúc bằng `speech.audio.done`; `429` kèm `Retry-After` khi hết slot.[^vieneuapi]
- VieNeu SDK trả float32 48 kHz, HTTP trả s16le 48 kHz: tài liệu thiết kế §3 nguyên tắc 4.[^design]
- Frame codec 80 ms; chunk đầu 2 frame trên GPU, 4 frame trên CPU; các chunk sau 4 frame = 320 ms; khuyến nghị client pre-buffer 150–300 ms (GPU), ≥ 300 ms (CPU).[^vieneurt]
- WebRTC gửi RTP 20 ms và gửi im lặng khi rảnh (HF s2s).[^engine]
- Playback worklet đếm số PCM đã render, không tính độ trễ khởi động và im lặng do underrun, rồi dùng số đó cho `conversation.item.truncate`; fade 32 frame để chống click (HF browser demo).[^demo]

### 16.3.5 Contract của một số backend trong wiki

Không backend nào giống backend nào. Bảng này là lý do nguyên tắc 4 tồn tại (**Reported** trừ dòng cuối):

| Backend / đường đi | Audio vào | Audio ra | Ghi chú |
|---|---|---|---|
| HF s2s, nội bộ pipeline | `input_audio_buffer.append` base64 PCM → resample **16 kHz**, cắt **512 mẫu** cho VAD[^engine] | Khối **16 kHz mono int16 512 mẫu**[^backends] | `sample_rate=16000` là mặc định VAD[^cli] |
| HF s2s, `--stt openai` | WAV PCM16 **16 kHz mono** trong bộ nhớ, gửi cả utterance[^backends] | JSON `text` hoặc text thuần | Live transcription upload lại cả utterance tích luỹ |
| HF s2s, `--stt openai-realtime` | PCM **24 kHz** (handler resample từ 16 kHz); `sample_rate` khác 24 000 thì setup lỗi[^backends] | Partial theo provider | Giao thức transcription của OpenAI |
| HF s2s, `--tts openai` | – | PCM16 theo `--openai_tts_sample_rate` (mặc định 24 000) → chuyển dần về khối 16 kHz mono int16 512 mẫu[^backends][^cli] | Đây là gốc của trần 16 kHz (§16.9) |
| HF browser demo | Worklet resample về **24 kHz**, đóng gói Int16 LE[^demo] | Decode Int16 → Float32, nội suy tuyến tính 24 → 48 kHz[^demo] | Cache key `audio-24k-v2` phải khớp phiên bản worklet |
| VieNeu HTTP | – | **48 kHz** s16le mono (hoặc 24/16/8 kHz theo request)[^vieneuapi] | Framework mặc định 24 kHz phải xin `sample_rate: 24000` hoặc đặt rate 48 000[^vieneuapi] |
| MOSS-TTS Local | – | Codec stereo 48 kHz nhưng ví dụ stream là mono[^design] | Phải xác nhận số kênh thật |
| Higgs TTS | – | SSE base64 WAV[^design] | Mỗi event có header WAV |
| Gateway tự viết (đề xuất) | 16 kHz mono cho ASR | Giữ **rate gốc** tới playback adapter | **Synthesis**, §7.1[^design] |

### 16.3.6 Viết contract thành code và kiểm ở biên

Chương 2 §2.9.3 đã giới thiệu `AudioFormat`. Ở cấp pipeline, contract cần gắn với **cạnh** và được kiểm bằng **giá trị thật** mà backend trả về, không chỉ bằng cấu hình tĩnh:

```python
@dataclass(frozen=True)
class AudioContract:
    sample_rate: int
    channels: int
    sample_format: str          # "s16le" | "f32le"
    framing: str                # "ws-binary-20ms" | "chunked" | "sse-base64" | ...

    def check(self, *, sample_rate: int, channels: int, sample_format: str) -> None:
        got = (sample_rate, channels, sample_format)
        want = (self.sample_rate, self.channels, self.sample_format)
        if got != want:
            raise ValueError(f"audio contract mismatch: got {got}, want {want}")

EDGE_U1 = AudioContract(16_000, 1, "s16le", "ws-binary-20ms")
EDGE_D2_VIENEU_HTTP = AudioContract(48_000, 1, "s16le", "chunked")

# Khi nhận response TTS: đọc header thay vì tin config
EDGE_D2_VIENEU_HTTP.check(sample_rate=int(resp.headers["X-Sample-Rate"]),
                          channels=1, sample_format="s16le")
```

Script ở Phụ lục (mục D) cho thấy contract bắt được trường hợp server trả 24 kHz trong khi adapter chờ 48 kHz (**Reproduced**, trên dữ liệu giả lập). Nếu không có bước kiểm này, lỗi chỉ lộ ra khi có người nghe: giọng chậm và trầm gấp đôi.

Ba quy tắc đi kèm (**Synthesis**):

- **Assert ở biên, chuyển đổi ở một chỗ.** Mỗi cạnh qua ranh giới có một `check`. Mỗi phép resample có tên, có owner, và chỉ xảy ra một lần trên mỗi đường.
- **Metadata đi cùng dữ liệu, không đi riêng.** `audio.start` mang `format`, `sample_rate`, `channels` của chính generation đó, vì hai generation liên tiếp có thể đến từ hai backend khác nhau (fallback).
- **Không đoán.** Header thiếu, số kênh không rõ, WAV độ dài "unknown": coi là lỗi contract cho tới khi có test chứng minh adapter xử lý được.

---

## 16.4 Đơn vị khác nhau và cách nối

### 16.4.1 Năm đơn vị, năm lý do

| Thành phần | Đơn vị | Lý do tồn tại của đơn vị đó | Nguồn |
|---|---|---|---|
| Transport | **20 ms** frame | Cân bằng overhead header với độ trễ đóng gói; 20 ms là kích thước frame Opus phổ biến | Kiến thức nền; thiết kế §5.1 (20–32 ms)[^design] |
| VAD (Silero) | **512 mẫu = 32 ms** | Model được huấn luyện với cửa sổ cố định; từ v5 không đổi được | **Reported**[^silero] |
| ASR streaming | **160–320 ms** chunk (+ lookahead) | Encoder cần đủ ngữ cảnh mỗi bước; chunk lớn hơn thì WER thấp hơn nhưng chậm hơn | **Reported** (Nemotron)[^design] |
| ASR turn-final | **Cả lượt** | Model không causal, cần toàn câu | Chương 11 |
| Text | **Mệnh đề** (sự kiện, không phải thời gian) | TTS cần ngữ cảnh để có prosody; per-token làm gãy prosody và bùng nổ số request | **Reported**[^design][^blueprint] |
| TTS | **Frame codec 80 ms**, chunk 320 ms | Codec neural sinh theo frame; chunk là đơn vị decode của codec | **Reported** (VieNeu)[^vieneurt] |
| Playback | **128 frame** quantum | Đơn vị render của Web Audio | Kiến thức nền |

Tài liệu thiết kế nói rõ: "Không bắt VAD, ASR và TTS dùng chung một chunk length".[^design] Ép tất cả về một đơn vị sẽ buộc ít nhất một model chạy ngoài điều kiện huấn luyện của nó, hoặc buộc transport đóng gói quá to.

### 16.4.2 Số học: bội chung 160 ms

Ở 16 kHz, frame transport 20 ms là 320 mẫu, khối VAD là 512 mẫu. Bội chung nhỏ nhất của chúng là **2 560 mẫu = 160 ms = 8 frame transport = 5 khối VAD** (**Reproduced**, Phụ lục mục 1a). Chunk ASR 160 ms và 320 ms chia hết cho cả hai; chunk 560 ms thì không chia hết cho 512 (mục 1b). Điều này cho hai hệ quả thực tế:

- Cứ mỗi 160 ms, ba đồng hồ (transport, VAD, ASR 160 ms) "khớp pha" một lần. Đây là chu kỳ tự nhiên để log, kiểm tra timeline và debug.
- ASR 560 ms vẫn chạy bình thường, vì nó không đọc theo khối VAD. Nó đọc thẳng từ ring buffer theo chỉ số mẫu. Đừng thiết kế ASR "gom 17,5 khối VAD".

### 16.4.3 Ba loại adapter nối các đơn vị

| Loại | Vào → ra | Ví dụ | Độ trễ thêm vào |
|---|---|---|---|
| **Reblocker** (kích thước cố định) | Mảng độ dài bất kỳ → khối đúng N mẫu | 320 → 512 cho VAD; 320 → 2 560 cho ASR 160 ms; 24 kHz TTS → 512 mẫu 16 kHz trong HF s2s | Tối đa (frame vào − ước chung) |
| **Accumulator theo sự kiện** | Luồng nhỏ → đơn vị có nghĩa | Token → mệnh đề (chunker); khối VAD → lượt (turn buffer) | Phụ thuộc nội dung: chờ dấu câu, chờ endpoint |
| **Pacer/splitter** | Khối to, tới dồn → luồng đều theo nhịp thời gian thật | Chunk TTS 320 ms → RTP 20 ms; queue client → quantum 128 | Bằng lượng pre-buffer chọn |

Với reblocker 320 → 512, khối VAD hoàn tất **trễ hơn mẫu cuối của nó từ 0 đến 16 ms, trung bình 8 ms** vì phải chờ frame transport chứa mẫu đó tới trọn vẹn (**Reproduced**, mục 1c). Con số này nhỏ so với 200–300 ms im lặng mà endpointing cần, nhưng cần biết để không đổ lỗi nhầm cho VAD khi đo latency từng cạnh.

### 16.4.4 Nguyên tắc: một timeline, nhiều cửa sổ đọc

```text
chỉ số mẫu w (16 kHz)   0        2560      5120      7680      10240     ...
transport 20 ms         |..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|..|
VAD 512                 |....|....|....|....|....|....|....|....|....|....|
ASR 160 ms              |.........|.........|.........|.........|
turn buffer                         [pre-roll|=========== lượt ===========|pad]
Smart Turn                               ◄────────── ≤ 8 s cuối ──────────►
```

Mỗi consumer giữ **con trỏ đọc của riêng nó** trên ring buffer: "tôi đã xử lý tới mẫu số bao nhiêu". Không consumer nào cần biết consumer khác dùng khối bao nhiêu. Mọi sự kiện (VAD `speech_start`, ASR `audio_range`, Smart Turn quyết định) đều được gắn **chỉ số mẫu** chứ không phải số thứ tự khối, nên turn owner so sánh được chúng trực tiếp (**Synthesis**).

Với text và TTS, "timeline" không còn là mẫu của user mà là **mẫu của audio bot**: mỗi `chunk_id` được adapter ghi lại khoảng `[mẫu đầu, mẫu cuối)` trong luồng output của generation. Nhờ đó, `played_sample_offset` từ client tra ngược ra mệnh đề nào đã phát (§16.6.4).

---

## 16.5 Reblocking và buffering

### 16.5.1 Ring buffer: xương sống của gateway

Ring buffer là mảng kích thước cố định, ghi đè dữ liệu cũ nhất, kèm một **bộ đếm tuyệt đối** `w` = tổng số mẫu đã ghi kể từ đầu session. Chỉ số tuyệt đối `i` nằm ở ô `i % capacity`. Đọc đoạn `[start, end)` hợp lệ khi `start ≥ w − capacity` (Chương 6 §6.6.1).

**Định cỡ (Synthesis).** Dung lượng phải lớn hơn **cửa sổ dài nhất mà bất kỳ consumer nào cần đọc lùi**:

| Consumer | Cần đọc lùi | Nguồn |
|---|---|---|
| Pre-roll | 200–300 ms | Thiết kế §7.1 (**Synthesis**)[^design] |
| HF s2s `speech_pad_ms` | 500 ms | **Observed** trong argument class[^cli] |
| Smart Turn | ≤ 8 s | **Reported**[^wikidesign] |
| ASR streaming bị chậm tạm thời | Backlog cho phép (vd 1–2 s) | Synthesis |

Vì vậy ring buffer **≥ 8 s** cộng biên an toàn nếu dùng Smart Turn. Ở 16 kHz f32, 8 s là 512 KB mỗi session (**Reproduced**, mục 4). Ring buffer nhỏ hơn nhu cầu sẽ gây lỗi im lặng (đọc ra dữ liệu đã bị ghi đè). Script ở Phụ lục (mục C) cố tình đọc pre-roll 300 ms từ ring 200 ms và nhận ngoại lệ thay vì dữ liệu sai (**Reproduced**). Hãy để code của bạn **ném lỗi** ở tình huống này.

### 16.5.2 Pre-roll lấy từ đâu (Q3)

VAD cần vài khối để chắc chắn có tiếng nói. Khi nó báo `speech_start`, phần đầu âm tiết đầu tiên đã trôi qua. Pre-roll **lấy từ ring buffer**, vốn ghi liên tục **bất kể VAD nói gì**. Khi mở lượt, turn buffer copy đoạn `[speech_start − pre-roll, w)` từ ring (Chương 6 §6.11).

- Tài liệu thiết kế đặt pre-roll 200–300 ms, ghi rõ là thiết kế khởi điểm, chưa phải cutoff đã đo (**Synthesis**).[^design]
- Blueprint đặt `PRE_ROLL_MS = 200` trong phần văn xuôi, nhưng code mẫu của nó dùng 250 ms. Wiki ghi nhận độ lệch này khi đọc tĩnh (**Observed**).[^blueprint]
- Silero `speech_pad_ms` 100–200 ms (report) và HF s2s `speech_pad_ms=500` là **padding hai đầu đoạn VAD**, khác với pre-roll ở gateway. Chúng cộng dồn nếu cả hai cùng bật. Hãy ghi rõ lớp nào thêm bao nhiêu (**Synthesis**, số liệu **Reported/Observed**).[^silero][^cli]
- Nếu client chỉ gửi audio khi có tiếng nói (VAD phía client để tiết kiệm băng thông), **client** phải gửi kèm pre-roll. Gateway không thể lấy lại audio chưa từng được gửi (Chương 6 §6.11). Các backend realtime transcription của HF s2s giữ pre-speech padding và không upload audio mic lúc rảnh, tức là pre-roll nằm ở phía gửi (**Reported**).[^backends]

Với tiếng Việt, mất phần đầu âm tiết là mất phụ âm đầu, đôi khi cả phần đầu của vần. Đó là thông tin phân biệt từ (Chương 5).

### 16.5.3 Turn audio buffer giữ bao lâu (Q3)

Turn buffer giữ audio của **một lượt** để ASR turn-final, final-pass (Profile D), hoặc chạy lại khi lượt mở lại. Vòng đời (**Synthesis**):

```text
speech_start ──► OPEN: copy pre-roll từ ring, sau đó append mỗi frame
                  │
                  ├─ chạm trần (vd 30 s) ───────────────► buộc endpoint
                  ▼
soft end ──────► HOLD: còn giữ, vì lượt có thể mở lại (reopen)
                  │   └─ user nói tiếp ─► revision mới, append tiếp (cùng buffer)
                  ▼
turn.commit + final ASR được chấp nhận ──► RELEASE
(hoặc revision bị thay hoàn toàn, hoặc session đóng)
```

Thời gian giữ phụ thuộc vào triết lý điều khiển (Chương 10 §10.5):

| Thiết kế | Giữ tới khi | Lý do |
|---|---|---|
| Commit cứng sau timeout (report) | Final ASR xong sau timeout 1.2–1.5 s | Không có reopen |
| Speculative + revision (HF s2s) | Hết grace reopen (800 ms) và có output đã commit; trần reopen khi chưa trả lời `--unanswered_reopen_ms` 7 000 ms | Khi user nói tiếp, HF s2s mở lại lượt thành revision mới và **phát lại audio đã tích luỹ** (**Reported**)[^hf] |
| Two-pass (Profile D) | Final-pass chạy lại trên turn audio đã giữ và kết quả được commit | "Final-pass chạy lại trên turn audio đã giữ" (**Synthesis** của thiết kế §7.2)[^design] |

Trần độ dài: blueprint đặt `MAX_UTTERANCE_MS = 30_000` (**Reported**)[^blueprint]. Script ở Phụ lục (mục B) mô phỏng trần 1,5 s: turn buffer báo "chạm trần" sau đúng số frame dự kiến, gateway phải buộc endpoint thay vì tiếp tục cấp bộ nhớ (**Reproduced**).

**Giữ lâu hơn để đánh giá?** Chỉ khi user đồng ý và có policy lưu trữ. Tài liệu thiết kế yêu cầu corpus đánh giá phải opt-in, có kiểm soát truy cập, có thời hạn lưu và có consent. Log mặc định chỉ chứa metadata, không chứa audio hay transcript (**Synthesis**).[^wikidesign] Turn buffer là dữ liệu nhạy cảm: giải phóng đúng hạn vừa là quản lý bộ nhớ, vừa là privacy.

### 16.5.4 Buffer ở downlink

| Vị trí | Mục đích | Giới hạn | Khi barge-in |
|---|---|---|---|
| Adapter TTS (server) | Gom chunk, gắn `sequence`, cắt lại để pacing | Theo credit từ client (Chương 8 §8.5.3) | Bỏ toàn bộ, đóng request TTS |
| Transport (socket buffer, WebRTC jitter buffer) | Hấp thụ jitter mạng | Nhỏ; không kiểm soát trực tiếp | WebRTC trong HF s2s có `output_audio_buffer.clear` để xoá audio chưa phát phía server (**Reported**)[^engine] |
| Client queue | Pre-buffer chống giật | Pre-buffer 150–300 ms (GPU), ≥ 300 ms (CPU), theo VieNeu (**Reported**)[^vieneurt]; trần tổng ~2 s (Synthesis) | `client.clear(generation_id)`: flush |
| Worklet ring | Cấp quantum 128 frame | Vài chục ms | Fade-out ngắn rồi dừng |

Có một điểm tinh tế: HF browser demo đếm buffering **theo số mẫu PCM, không theo thời gian trôi qua** (**Reported**).[^demo] Đây là cách đúng. Chunk tới dồn cục hay rải rác thì lượng audio có sẵn vẫn đo chính xác.

### 16.5.5 Ngân sách bộ nhớ theo session

Script ở Phụ lục (mục 4, **Reproduced**) cho các con số sau, tính ở 16 kHz f32 trừ khi ghi khác:

| Buffer | Mẫu | Bộ nhớ |
|---|---|---|
| Pre-roll 300 ms | 4 800 | 19,2 KB |
| Ring buffer 8 s | 128 000 | 512 KB |
| Turn buffer 5 s (trung bình) | 80 000 | 320 KB |
| Turn buffer trần 30 s | 480 000 | 1,92 MB |
| Trường hợp xấu: ring 8 s + turn 30 s | – | **2,43 MB/session**; 200 session ≈ 486 MB; int16 thì một nửa |
| Downlink queue 2 s @48 kHz f32 | 96 000 | 384 KB |

Audio buffer **không phải** nút thắt bộ nhớ. Nút thắt là ASR cache trên GPU, KV cache của LLM và slot TTS (Chương 22). Nhưng audio buffer là nơi **rò rỉ** dễ xảy ra nhất: một turn buffer không được release sau mỗi lượt sẽ tăng không giới hạn theo độ dài cuộc hội thoại. Hãy đưa "kích thước turn buffer khi idle = 0" vào test (**Synthesis**).

---

## 16.6 Timeline và timestamp

### 16.6.1 Các đồng hồ trong hệ thống

| Đồng hồ | Ở đâu | Đơn vị | Dùng cho |
|---|---|---|---|
| Đồng hồ mẫu capture | Client (`AudioContext`) | mẫu @ rate của context | Capture timestamp |
| `sequence` uplink | Client | frame | Phát hiện mất, trùng, đảo thứ tự |
| **Chỉ số mẫu `w`** | Gateway | mẫu @16 kHz | VAD, ASR `audio_range`, biên lượt, pre-roll |
| Wall clock đơn điệu | Gateway | ns (`time.monotonic_ns()`) | Latency từng cạnh, deadline (output hold, timeout) |
| Đếm mẫu output | TTS adapter | mẫu @ rate gốc của generation | Biên `chunk_id`, offset trong `audio.chunk` |
| Đếm mẫu đã render | Client worklet | mẫu | `played_sample_offset` |
| Wall clock client | Client (`performance.now()`) | ms | Voice-to-voice đo phía client (Chương 6 §6.10) |

HF s2s là ví dụ thực tế cho việc dùng **hai đồng hồ khác nhau có chủ đích**: trần reopen khi chưa trả lời dùng thời gian audio đã stream (nên push-to-talk im lặng không làm nó tăng), còn processing và output hold dùng deadline wall clock (**Reported**).[^hf]

### 16.6.2 Chỉ số mẫu là đồng hồ chủ cho audio

Quy tắc (**Synthesis**): **vị trí trong audio** luôn đo bằng chỉ số mẫu. **Thời điểm xảy ra sự kiện** đo bằng wall clock. Nối hai đồng hồ bằng các cặp neo `(w, t_wall)` ghi lại mỗi khi một frame tới:

- `lag = t_wall_now − t_wall_neo − (w_now − w_neo) / 16000`. `lag` tăng dần nghĩa là gateway xử lý chậm hơn thời gian thật (backlog). `lag` dao động nghĩa là jitter mạng.
- Mốc "mẫu speech cuối của user" ở critical path §8.1 được xác định bằng **chỉ số mẫu** (từ VAD), rồi mới quy ra wall clock qua neo.[^design] Nếu dùng wall clock lúc gói tới làm mốc, bạn đang đo cả jitter mạng vào độ trễ endpoint.

### 16.6.3 Sequence, gap và packet thiếu (Q4)

Tài liệu thiết kế chỉ yêu cầu: packet thiếu hoặc có gap thì cần policy rõ ràng, **không nối lệch timeline**.[^design] Chương này đề xuất cụ thể (**Synthesis**):

| Tình huống | Thường gặp ở | Policy đề xuất |
|---|---|---|
| Gói tới **dồn cục** sau một lúc chậm, không mất | WebSocket/TCP (head-of-line blocking, Chương 8 §8.2) | Không làm gì với timeline: chỉ số mẫu vẫn đúng. Ghi `lag` để đo. VAD xử lý backlog nhanh nhất có thể |
| **Mất ngắn** (≤ vài frame), transport tự che | WebRTC: jitter buffer + PLC của Opus | Gateway nhận PCM liên tục đã che. Không thấy gap. Chấp nhận |
| **Mất ngắn**, transport không che | WS khi client tự bỏ frame (worklet tràn) | **Chèn im lặng đúng số mẫu bị mất**, ghi `gap(w_start, n)`. Trong gap, turn owner **không đếm** im lặng chèn vào cho endpoint |
| **Mất dài** (vd > 500 ms) | Mạng chập chờn, reconnect | Đánh dấu lượt hiện tại là hỏng: huỷ hoặc hỏi lại user. Không cho ASR một lượt bị thủng lớn |
| Tới muộn hoặc trùng (`seq` < kỳ vọng) | Retransmit, client gửi lại | Bỏ: chỗ đó đã được lấp |
| **Reconnect** | Đổi mạng | Mở một đoạn timeline mới, hoặc cộng thêm đúng thời gian mất. Không bao giờ nối thẳng |

Vì sao không nối thẳng? Nếu mất 5 frame (100 ms) mà nối thẳng, mọi timestamp phía sau **sớm hơn thực tế 100 ms**. Frame `seq=60` lẽ ra ở 1 200 ms lại bị gán 1 100 ms (**Reproduced**, mục 5). "Mẫu speech cuối" sai 100 ms, ASR `audio_range` lệch với wall clock, voice-to-voice đo sai cùng lượng. Tệ hơn, âm tiết bị cắt mất phần giữa được dán liền, ASR thấy một âm "lai" không tồn tại.

Vì sao chèn im lặng lại cần đánh dấu? Vì 100 ms im lặng giả có thể khiến VAD tính sai im lặng cuối lượt. Gap phải là **sự kiện** mà turn owner biết, không chỉ là số 0 trong mảng.

Script ở Phụ lục (mục A) mô phỏng mất `seq` 40–44 rồi `seq` 41 tới muộn. Kết quả: timeline vẫn đủ 2 000 ms, một gap được ghi tại mẫu 12 800 dài 1 600 mẫu, gói muộn bị bỏ (**Reproduced**).

### 16.6.4 Downlink: played offset và cắt history

Client báo `audio.played(generation_id, played_sample_offset)`. Gateway giữ bảng `chunk_id → [mẫu đầu, mẫu cuối)` cho generation đó, nên tra được:

- Mệnh đề nào **đã phát hết**: lưu nguyên vào history.
- Mệnh đề nào **phát dở**: lưu phần ước lượng, kèm tag `[bị ngắt]` theo trình tự barge-in ở §7.3.[^design]
- Mệnh đề nào **chưa phát**: bỏ.

Script ở Phụ lục (mục 7) cắt tại 2,9 s trên ba mệnh đề: mệnh đề 1 đã phát hết, mệnh đề 2 phát 58 %, mệnh đề 3 chưa phát (**Reproduced**). Phần "58 %" tính theo tỷ lệ ký tự, nên chỉ là **ước lượng**. Tài liệu thiết kế cảnh báo: không có alignment giữa token và audio thì chỉ khẳng định được "played offset", không khẳng định được chính xác từ nào đã phát.[^design] Chính sách an toàn là lưu mệnh đề phát dở ở dạng "đã bắt đầu nói: …" thay vì giả vờ biết chính xác.

Hai lưu ý (**Reported**):

- HF browser demo tính played offset bằng số PCM đã render, **không tính** độ trễ khởi động và im lặng do underrun, rồi gửi `conversation.item.truncate` cho phần chưa nghe.[^demo]
- Server HF s2s hiện chấp nhận `conversation.item.truncate` như một no-op, không cắt lịch sử phía server.[^engine] Nếu cần cắt history thật, gateway của bạn phải tự làm.

---

## 16.7 State theo session (Q5)

### 16.7.1 Bảng kiểm kê

| State | Phạm vi | Owner | Tạo khi | Reset / giải phóng khi |
|---|---|---|---|---|
| Byte lẻ của transport | Kết nối | Decoder | Accept | Close |
| Lịch sử bộ lọc resampler uplink | Session | Ingress | Accept | Close; reset sau reconnect |
| Ring buffer + `w` + neo wall clock | Session | Ingress | Accept | Close |
| Ước lượng nền nhiễu (2–3 s đầu, ngưỡng thích ứng) | Session | VAD policy | Đầu session | Close |
| `VADIterator` (state của model, cờ đang nói) | Session | Nhánh VAD | Accept | `reset_states()` khi hết lượt; close |
| Con trỏ đọc của từng consumer | Session | Consumer đó | Accept | Close |
| ASR streaming cache (encoder/decoder, hypothesis) | Session × stream | ASR adapter | Lượt đầu | Sau final; close → **giải phóng GPU** |
| Turn buffer | Lượt | Turn owner | `speech_start` | Commit + final được chấp nhận; revision bị thay |
| Transcript revisions | Lượt | Turn owner | Partial đầu | Commit |
| History hội thoại | Session | Orchestrator | Accept | Close; cắt theo played offset |
| LLM stream handle | Generation | LLM client | Commit | Done / cancel |
| Request TTS + resampler downlink | Generation × chunk | TTS adapter | Mệnh đề đầu | Done / cancel |
| Bảng `chunk_id → khoảng mẫu` | Generation | TTS adapter | `audio.start` | Sau khi history đã cắt |
| Speaker embedding (speaker lock) | Session | Barge-in policy | Lượt đầu | Close. **Dữ liệu nhạy cảm**, không ghi log |

Nguồn: `VADIterator` mỗi session và `reset_states()` khi hết lượt là **Reported**.[^silero] "Mỗi session có state VAD/ASR riêng, không bao giờ dùng chung cache giữa các user" và yêu cầu giải phóng ASR cache, cancel inference, flush queue, bỏ callback đến trễ khi session đóng là **Synthesis** của thiết kế §7.1–7.2.[^design] Speaker embedding là dữ liệu có ranh giới công bố, không ghi vào log vận hành (**Synthesis**).[^wikidesign] Các dòng còn lại là **Synthesis** của chương này.

### 16.7.2 Chia sẻ được gì, không chia sẻ được gì

- **Chia sẻ được:** weights, session ONNX/TensorRT (nếu runtime cho phép gọi đồng thời), process giữ model. Tài liệu thiết kế khuyến nghị một model owner cho mỗi process, thay vì mỗi gateway worker tự load weights (**Synthesis**).[^wikidesign]
- **Không chia sẻ được:** mọi thứ trong bảng trên. Batching qua nhiều session vẫn được, **miễn là state tách theo hàng**. VieNeu continuous batching là ví dụ: mỗi request giữ một hàng (slot) riêng với sampling setting riêng trong cùng một CUDA graph (**Reported**).[^vieneurt]

Với các model mà state là tensor input/output (nhiều model VAD và ASR streaming xuất ONNX theo kiểu này), một session ONNX có thể phục vụ nhiều user nếu **mỗi user truyền tensor state của riêng mình** (kiến thức nền; phải kiểm với phiên bản cụ thể, **Unverified** cho Silero/Nemotron trong wiki).

### 16.7.3 Chuyện gì xảy ra khi dùng chung (Q5)

- **Chung `VADIterator`:** state của model trộn audio của hai người. Im lặng của B làm "nguội" xác suất speech của A. Cờ "đang nói" bật bởi A rồi bị tắt bởi frame của B. Kết quả: endpoint sai, barge-in ảo. Lỗi kiểu này không lặp lại được khi test một user, nên rất khó tìm.
- **Chung ASR streaming cache:** encoder của B dùng ngữ cảnh của A. Transcript của B có thể chứa **từ của A**. Đây không chỉ là bug: đây là **sự cố rò rỉ dữ liệu** giữa người dùng.
- **Chung resampler:** lịch sử bộ lọc của A trộn vào vài mẫu đầu mỗi frame của B. Nghe như tiếng click nhỏ, rất khó chẩn đoán.
- **Callback đến muộn sau khi session đóng:** kết quả ASR của session cũ xuất hiện trong session mới tái sử dụng cùng slot. HF s2s chặn điều này bằng một **session generation**, kiểm tra nguyên tử cùng lúc với việc đẩy vào queue (**Reported**).[^backends]

---

## 16.8 Định danh (Q6)

### 16.8.1 Sáu định danh

| Định danh | Phạm vi | Ai tạo / tăng | Tăng khi | Chặn lỗi gì |
|---|---|---|---|---|
| `session_id` | Một kết nối hội thoại | Gateway lúc accept | Không đổi | Lẫn state giữa user; callback của session cũ |
| `turn_id` | Một lượt của user | Turn owner | `speech_start` mở lượt mới | Ghép nhầm audio hoặc transcript của hai lượt |
| `revision` | Một phiên bản của một lượt | Turn owner | Reopen (user nói tiếp trong grace); final-pass thay transcript | Hành động trên bản cũ; final bị trùng |
| `generation_id` | Một response của bot | Turn owner / session | Mỗi response mới; **mỗi lần cancel** | **Phát audio cũ sau barge-in** (stale) |
| `chunk_id` | Một mệnh đề → một đơn vị TTS | Chunker | Mỗi mệnh đề | Ghép text ↔ audio; cắt history |
| `sequence` | Một message trên một luồng | Bên gửi của luồng đó | Mỗi message | Mất, trùng, đảo thứ tự |

Schema gốc là **Synthesis** của thiết kế §7.2.[^design] HF s2s dùng cùng ý tưởng cho `generation_id`: `CancelScope` giữ một bộ đếm generation. `cancel()` tăng bộ đếm để mọi generation cũ thành stale. Các thread kiểm `is_stale(gen)` trên từng token, và output mang `cancel_generation` để send loop bỏ phần không còn hiện hành (**Reported**).[^engine]

### 16.8.2 Quan hệ giữa các định danh

```text
session_id
 ├─ turn_id = 17
 │   ├─ revision 1  (soft end → speculative LLM, generation 41, bị bỏ khi user nói tiếp)
 │   └─ revision 2  ── turn.commit(17, 2) ──► generation_id = 42
 │                                             ├─ chunk_id 0 ─ audio.chunk seq 0,1
 │                                             ├─ chunk_id 1 ─ audio.chunk seq 2,3,4
 │                                             └─ chunk_id 2 ─ (bị huỷ: barge-in → generation 43)
 └─ turn_id = 18 ...
```

Quy tắc (**Synthesis**):

- Một generation **luôn gắn với một cặp `(turn_id, revision)`**. Ghi cặp đó vào sự kiện tạo generation để log join được. HF s2s ghi "response thuộc generation input của nó" lên conversation item và tool call (**Reported**).[^hf]
- `sequence` đơn điệu tăng chặt **trong một luồng**. Downlink có hai lựa chọn: đánh số lại từ 0 cho mỗi generation (client kiểm `(generation_id, sequence)`), hoặc đánh số liên tục cả session. Chọn một và ghi vào contract. Script ở Phụ lục (mục E) dùng cách thứ nhất: client bỏ chunk của generation 7 tới muộn sau khi đã `clear(8)`, và bỏ chunk `seq 0` bị trùng (**Reproduced**).
- Định danh **không được tái sử dụng** trong một session. Đừng reset `generation_id` về 0 khi bắt đầu lượt mới.
- Mọi log theo lượt join bằng `turn_id`/`revision`/`generation_id`/`chunk_id`, không theo thứ tự thời gian. Thiết kế §8.1 nhấn mạnh điều này cho trường hợp reopen, cancel và nhiều chunk TTS.[^design]

### 16.8.3 Một trace mẫu

```text
t_wall(ms)  w(mẫu)   sự kiện
  10 004    160 064  vad.speech_start         session=s1 turn=17 rev=1
  10 004       –     turn_buffer.open          from_w=155 264 (pre-roll 300 ms)
  11 860    189 760  vad.speech_end           turn=17 rev=1
  12 070       –     smart_turn=complete      → soft_end, speculative gen=41
  12 300    196 800  vad.speech_start         turn=17 rev=2 (reopen) → cancel gen=41
  13 420    214 720  vad.speech_end, smart_turn=complete
  14 220       –     turn.commit              turn=17 rev=2 → gen=42
  14 610       –     text.chunk               gen=42 chunk=0 "Dạ, em kiểm tra rồi ạ."
  14 760       –     audio.start              gen=42 fmt=s16le sr=48000 ch=1
  14 760       –     audio.chunk              gen=42 chunk=0 seq=0 n=7 680
  16 900       –     barge-in                 → gen=43, response.cancel(42), client.clear(42)
  16 950       –     audio.played             gen=42 offset=95 040 (1,98 s @48 kHz) → cắt history
```

Các con số là minh hoạ (**Synthesis**), không phải đo; cột `w` khớp với `t_wall × 16` vì giả định không có backlog. Played offset 1,98 s nhỏ hơn khoảng 2,14 s từ `audio.start` tới lúc ngắt, vì client giữ pre-buffer (~150 ms) trước khi phát mẫu đầu tiên. Điểm cần thấy: mọi sự kiện audio có `w`, mọi sự kiện đều có định danh, và generation 41 (speculative trên revision 1) bị huỷ trước khi có audio nào được phát.

---

## 16.9 Trần băng thông 16 kHz (Q7)

### 16.9.1 Cơ chế

Trong HF s2s, audio đi giữa các stage là **khối 16 kHz mono int16 512 mẫu** ở cả hai chiều:

- Chiều vào: server resample audio của client về 16 kHz và cắt khối 512 mẫu cho VAD (**Reported**).[^engine]
- Chiều ra: backend `--tts openai` nhận PCM16 ở `--openai_tts_sample_rate` (mặc định 24 000) rồi **chuyển dần về khối 16 kHz mono int16 512 mẫu** của pipeline (**Reported**).[^backends][^cli] Các handler TTS khác cũng vậy: OmniVoice chuyển output float 24 kHz thành khối int16 16 kHz; Supertonic chuyển 44,1 kHz xuống 16 kHz (**Reported**).[^hf]
- Sau đó transport lại đưa audio lên: WebRTC resample 16 kHz lên Opus 48 kHz (**Reported**).[^engine] Browser demo nhận PCM 24 kHz và nội suy lên 48 kHz (**Reported**).[^demo]

Ghép lại, giọng VieNeu đi đường **48 → 16 → 24 → 48 kHz** (hoặc 48 → 16 → 48 qua WebRTC). Theo Nyquist, một tín hiệu 16 kHz chỉ chứa được tần số **dưới 8 kHz**. Upsample lên 24 hay 48 kHz sau đó không khôi phục được gì, chỉ thêm mẫu nội suy (kiến thức nền; thiết kế §5.1 cũng nhấn mạnh upsample không khôi phục thông tin đã mất).[^design] Tài liệu thiết kế kết luận: trần băng thông của cả pipeline là 16 kHz (**Synthesis** trên cơ sở Reported).[^design]

Script ở Phụ lục (mục 6, **Reproduced**) minh hoạ bằng tín hiệu tổng hợp gồm tone 3 kHz và tone 10 kHz ở 48 kHz:

- Hạ về 16 kHz **có lọc thông thấp**: tone 3 kHz còn nguyên biên độ 0,50; tone 10 kHz biến mất hoàn toàn (biên độ tại vị trí alias 6 kHz là 0,000).
- Hạ về 16 kHz **không lọc** (lấy 1 mẫu bỏ 2): tone 10 kHz gập về 6 kHz với biên độ 0,50. Đây là aliasing: một âm không có trong giọng gốc xuất hiện (Chương 2 §2.2.3).

### 16.9.2 Nghe ra sao, có hỏng thanh điệu không

Đây là kiến thức nền về ngữ âm học, áp dụng cho tiếng Việt:

- **Thanh điệu không bị ảnh hưởng.** Thanh điệu nằm ở F0 và đường nét F0, vốn ở khoảng vài chục tới vài trăm Hz, cùng chất giọng như thanh hầu hoá ở thanh ngã và nặng. Tất cả nằm rất xa dưới 8 kHz (Chương 1, Chương 5).
- **Độ rõ (intelligibility) gần như giữ nguyên.** Băng thông 8 kHz là mức "wideband", tốt hơn nhiều so với điện thoại 8 kHz sample rate (băng thông ~3,4 kHz).
- **Độ sáng và "độ thoáng" giảm.** Năng lượng của các âm xát như /s/, /x/, /ph/ (/f/) và phần "hơi" của giọng trải lên trên 8 kHz. Mất phần này, giọng nghe **đục và xa hơn**, giống chất lượng cuộc gọi wideband hơn là giọng thu studio.

Hệ quả cho việc đánh giá (**Synthesis**): nếu A/B giọng VieNeu qua HF s2s, bạn đang nghe **bản giới hạn ở 8 kHz**. Đừng so điểm MOS đó với điểm MOS của VieNeu ở 48 kHz, và đừng kết luận "model đục" khi lỗi nằm ở pipeline.

### 16.9.3 Khi nào chấp nhận, khi nào không

| Bối cảnh | Chấp nhận trần 16 kHz? | Lý do |
|---|---|---|
| MVP, đo latency và luồng điều khiển | Có | Mục tiêu là vòng đo đầu tiên (Profile A) |
| Telephony 8 kHz | Có, thừa | Đường truyền đã giới hạn ở ~3,4 kHz |
| Agent trên loa ngoài hoặc tai nghe chất lượng cao, sản phẩm coi giọng là thương hiệu | Không | Người nghe phân biệt được |
| Đánh giá chất lượng TTS | Không | Phải nghe ở rate gốc |

Cách xử lý, theo thứ tự công sức (**Synthesis**):

1. **Biết và ghi lại** trần 16 kHz trong contract của đường downlink.
2. Nếu đằng nào cũng bị hạ xuống 16 kHz, hãy **xin TTS trả 16 kHz ngay** (VieNeu nhận `sample_rate=16000` và resample theo chunk, **Reported**[^vieneuapi]). Kết quả nghe giống hệt, nhưng bớt một lần resample và giảm băng thông giữa TTS và pipeline ba lần.
3. Muốn giữ rate gốc: viết đường downlink riêng giữ rate gốc tới playback adapter (thiết kế §7.1: "Output giữ sample rate gốc tới tận playback adapter").[^design] Với HF s2s, việc này nghĩa là sửa handler TTS và transport. Wiki chưa có tài liệu nào cho thấy làm được bằng cờ cấu hình (**Unverified**).

Cách phát hiện: thu audio phía client, xem spectrogram (Audacity, Sonic Visualiser, `sox … spectrogram`). Nếu có một "trần" phẳng ở 8 kHz thì bạn đang gặp đúng vấn đề này.

---

## 16.10 Ghép lại: lần theo một lượt với số liệu

Giả sử: Profile A qua gateway tự viết, WebSocket, VieNeu GPU qua HTTP, user nói "Cho tôi đặt vé đi Đà Nẵng" dài 1,8 s. Các thời điểm là **minh hoạ** (Synthesis), dùng ngân sách tham khảo của report ở thiết kế §8.2 (**Reported**, chưa đo).[^design]

| # | Cạnh | Chuyện gì xảy ra | Dữ liệu / kích thước | State bị chạm | Định danh |
|---|---|---|---|---|---|
| 1 | U0→U1 | Worklet gom 20 ms, resample 48 → 16 kHz, f32 → s16 | 320 mẫu, 640 byte/frame, 50 frame/s | Resampler client | `seq` |
| 2 | U2→U4 | Gateway ghép byte lẻ, s16 → f32, ghi vào ring | 64 KB/s f32 | Ring, `w`, neo wall clock | `session_id` |
| 3 | U5v | Mỗi 512 mẫu chấm VAD; sau vài khối speech, `speech_start` | 2 048 byte/khối | `VADIterator` | – |
| 4 | U5t | Mở turn buffer từ `w − 4 800` (pre-roll 300 ms) | 19,2 KB pre-roll | Turn buffer | `turn_id` mới |
| 5 | U5t | 1,8 s speech được append | +28 800 mẫu | Turn buffer | – |
| 6 | U5v, U5s | 200–300 ms im lặng → Smart Turn trên ≤ 8 s cuối → complete | ≤ 512 KB đọc từ ring | – | `revision` |
| 7 | U5t→C1 | ASR turn-final trên ~2,4 s (pre-roll + speech + pad) | ~38 400 mẫu | – | `turn_id`, `revision` |
| 8 | C2 | Validity gate qua → `turn.commit` | – | Transcript revisions | `generation_id` mới |
| 9 | T1→T2 | LLM stream; chunker cắt mệnh đề đầu khi ≥ ~25 ký tự gặp dấu phẩy | 20–60 ký tự | – | `chunk_id=0` |
| 10 | T3→D1 | Normalizer và lexicon → POST `/v1/audio/speech`, `response_format=pcm` | JSON nhỏ | Request handle | `generation_id`, `chunk_id` |
| 11 | D2 | Chunk đầu: 2 frame = 160 ms = 7 680 mẫu = 15 360 byte; sau đó 320 ms = 30 720 byte | 768 kbps | – | `X-Request-Id` |
| 12 | D2 check | Đọc `X-Sample-Rate: 48000` và so với contract | – | – | – |
| 13 | D3→D4 | `audio.start(sr=48000, ch=1, s16le)`, rồi `audio.chunk` | – | Bảng `chunk_id → khoảng mẫu` | `sequence` |
| 14 | D5 | Client pre-buffer 150–300 ms rồi mới phát; resample 48 kHz → rate context (thường không cần) | – | Queue client | Kiểm `generation_id` |
| 15 | D6→C3 | Worklet render, đếm mẫu, gửi `audio.played` | – | Đếm đã render | `played_sample_offset` |
| 16 | – | Commit xong, final chấp nhận → release turn buffer; `VADIterator.reset_states()` | −320 KB | Turn buffer, VAD | – |

Ba nhận xét (**Synthesis**):

- Từ bước 1 tới bước 8, mọi thứ nằm ở 16 kHz. Từ bước 11 tới bước 15, mọi thứ nằm ở 48 kHz. Chỉ có **hai** phép resample trên toàn tuyến: một ở client (uplink), một (nếu có) ở playback. Đây là đích của nguyên tắc "chuyển đổi một lần, ở một chỗ".
- Pre-buffer ở bước 14 cộng thẳng vào voice-to-voice. Chunk đầu 160 ms của VieNeu GPU chưa đủ pre-buffer 200 ms, nên client phải chờ thêm một phần chunk thứ hai. Đây là đánh đổi "bớt giật nhưng chậm bắt đầu" mà thiết kế §8.3 nhắc tới.[^design]
- Mỗi bước đều có ít nhất một định danh. Nếu bạn không viết được cột "Định danh" cho một bước, bước đó không debug được khi có reopen hay barge-in.

---

## 16.11 Khung code tham khảo

Đây là phần lõi của `session_audio.py` (Python thuần, **Synthesis**, chỉ minh hoạ). Nó hiện thực bốn ý chính của chương: timeline theo chỉ số mẫu với gap được lấp và đánh dấu, ring buffer báo lỗi khi bị đọc quá xa, turn buffer có pre-roll và trần, và guard downlink theo generation và sequence. Phần chạy thử và kết quả nằm ở Phụ lục.

```python
from array import array
from dataclasses import dataclass, field

SR = 16_000
FRAME = 320            # 20 ms transport @16k
VAD_BLOCK = 512        # Silero @16k


class Ingress:
    """Nhận frame có sequence, dựng timeline theo chỉ số mẫu. Gap → chèn im lặng (giữ timeline)."""
    def __init__(self, ring: "Ring", max_gap_frames: int = 25):
        self.ring, self.expect, self.max_gap = ring, 0, max_gap_frames
        self.gaps, self.late = [], 0

    def on_frame(self, seq: int, pcm: array) -> None:
        if seq < self.expect:                # tới muộn/trùng: đã lấp im lặng, bỏ
            self.late += 1
            return
        if seq > self.expect:                # mất gói
            missing = seq - self.expect
            if missing > self.max_gap:
                raise ConnectionError(f"gap {missing} frame > giới hạn → reset turn/session")
            self.gaps.append((self.ring.w, missing * FRAME))
            self.ring.push(array("f", [0.0]) * (missing * FRAME))
        self.ring.push(pcm)
        self.expect = seq + 1


class Ring:
    """Ring buffer float32 với đồng hồ mẫu tuyệt đối `w` (tổng số mẫu đã ghi)."""
    def __init__(self, seconds: float):
        self.cap = int(seconds * SR)
        self.buf = array("f", [0.0]) * self.cap
        self.w = 0

    def push(self, x: array) -> None:
        for v in x[-self.cap:]:
            self.buf[self.w % self.cap] = v
            self.w += 1
        if len(x) > self.cap:                # phần bị cắt vẫn phải đếm vào đồng hồ
            self.w += len(x) - self.cap

    def read(self, start: int, end: int) -> array:
        if start < self.w - self.cap:
            raise IndexError("đoạn yêu cầu đã bị ghi đè: ring quá nhỏ cho pre-roll/turn")
        return array("f", (self.buf[i % self.cap] for i in range(start, min(end, self.w))))


class TurnBuffer:
    """Audio một lượt = pre-roll (copy từ ring lúc mở) + mọi frame sau đó, có trần độ dài.
    Ring chỉ cần đủ cho pre-roll/cửa sổ phân tích; turn buffer tự giữ phần còn lại."""
    def __init__(self, ring: Ring, preroll_ms: int = 300, max_ms: int = 30_000):
        self.ring, self.pre, self.maxn = ring, preroll_ms * SR // 1000, max_ms * SR // 1000
        self.start, self.data = None, None

    def open(self, speech_start_sample: int) -> None:
        self.start = max(0, speech_start_sample - self.pre)
        self.data = self.ring.read(self.start, self.ring.w)       # pre-roll + phần đã tới

    def append(self, x: array) -> bool:
        room = self.maxn - len(self.data)
        self.data.extend(x[:max(room, 0)])
        return room > len(x)                  # False → chạm trần: buộc endpoint

    def release(self) -> None:                # sau commit + final ASR, hoặc revision bị thay
        self.start, self.data = None, None


@dataclass
class Downlink:
    """Client-side guard: chỉ nhận chunk của generation hiện tại, sequence tăng chặt."""
    generation_id: int = 0
    last_seq: int = -1
    accepted: int = 0
    dropped: list = field(default_factory=list)

    def on_chunk(self, gid: int, seq: int, n_samples: int) -> bool:
        if gid != self.generation_id or seq <= self.last_seq:
            self.dropped.append((gid, seq))
            return False
        self.last_seq, self.accepted = seq, self.accepted + n_samples
        return True

    def clear(self, new_gid: int) -> None:
        self.generation_id, self.last_seq = new_gid, -1
```

Những gì khung này **cố ý chưa làm** (để dành cho Chương 17, 18):

- Không có `asyncio`. Trong gateway thật, `Ingress.on_frame` chạy trên event loop, còn VAD/ASR chạy trong worker và đọc ring qua con trỏ riêng (Chương 18).
- Không có state machine của lượt và không có cancel xuyên tầng (Chương 17).
- Ring dùng vòng lặp Python từng mẫu cho dễ đọc. Bản thật dùng `numpy` với hai lần copy slice (Chương 6 §6.11).
- Gap được lấp bằng số 0. Turn owner vẫn phải đọc `ingress.gaps` để không đếm im lặng giả vào endpoint (§16.6.3).

---

## 16.12 Contract tests

Gate 5 của thiết kế (§10) liệt kê các test contract cần có trước khi phát hành.[^wikidesign] Bảng dưới mở rộng danh sách đó thành test cụ thể (**Synthesis**):

| Nhóm | Test | Kỳ vọng |
|---|---|---|
| Rate | TTS trả 48k, 24k, rate lạ, không có header rate | Adapter đọc `X-Sample-Rate`/`audio.start`; rate không rõ → lỗi contract, không phát |
| Kênh | Backend trả stereo interleaved (MOSS) | Downmix có chủ đích, hoặc từ chối; không bao giờ đọc như mono |
| dtype | s16le và f32le; endian sai | Phát hiện bằng kiểm biên độ (f32 phải nằm trong [-1, 1]) |
| Container | PCM thô, WAV độ dài "unknown", SSE base64, SSE base64 WAV (Higgs) | Header WAV chỉ bóc ở đầu stream; SSE decode đúng |
| Framing | Message cắt giữa một mẫu s16 (số byte lẻ) | Byte lẻ được giữ lại cho message sau, không có click |
| Uplink gap | Mất 1, 5, 50 frame; frame trùng; frame đảo thứ tự | Timeline đúng theo `seq`; gap được đánh dấu; mất dài → lượt bị huỷ hoặc hỏi lại |
| Pre-roll | `speech_start` ngay sau khi session mở (ring chưa đủ 300 ms) | Pre-roll ngắn hơn nhưng không lỗi |
| Trần lượt | User nói liên tục > trần | Buộc endpoint; bộ nhớ không tăng quá trần |
| Revision | Reopen trong grace; final-pass thay transcript | Không có final trùng; commit đúng một lần |
| Stale | Chunk của generation cũ tới sau `clear` | Bị bỏ ở client; không có âm thanh |
| Cancel | Cancel giữa chunk TTS; đóng request | Âm thanh dừng; slot TTS được giải phóng (kiểm `/health`: `active` giảm)[^vieneuapi] |
| Quá tải | TTS trả `429` | Retry theo `Retry-After` hoặc báo trạng thái; không treo |
| Session | Disconnect giữa lượt; reconnect; 2 session song song nói xen kẽ | Không rò state; callback muộn bị bỏ; turn buffer = 0 khi idle |
| Đơn điệu | `sequence`, `revision`, `generation_id` | Tăng chặt trong phạm vi của nó |

---

## 16.13 Lỗi thường gặp: triệu chứng → nguyên nhân → cách sửa

| Triệu chứng | Nguyên nhân hay gặp | Cách sửa |
|---|---|---|
| Transcript rác dù model tốt | Lệch sample rate uplink (mic 48 kHz đưa thẳng vào ASR 16 kHz). Cộng đồng ghi nhận "9/10 lần" là do lệch sample rate (**Reported**, anecdote)[^design] | Assert rate ở U1/U4; resample một lần |
| Giọng bot chậm và trầm, hoặc nhanh và cao | Phát 48 kHz ở 24 kHz hoặc ngược lại; framework mặc định 24 kHz gặp VieNeu 48 kHz[^vieneuapi] | Đọc rate từ `audio.start`/header; hoặc xin `sample_rate` khớp |
| Nhiễu trắng rất lớn | Đọc `s16le` như f32, hoặc sai endian | Contract dtype; kiểm biên độ |
| Giọng dài gấp đôi, méo | Stereo interleaved đọc như mono | Contract channels |
| Mất âm tiết đầu | Không có pre-roll; ring quá nhỏ; VAD phía client không gửi pre-roll | Pre-roll từ ring ≥ 300 ms; client gửi kèm pre-roll nếu gating |
| Latency đo ra âm, hoặc nhảy bất thường | Dùng wall clock lúc gói tới làm vị trí audio; nối thẳng khi mất gói | Chỉ số mẫu cho vị trí; policy gap |
| Bot nói tiếp câu cũ sau khi bị ngắt | Client không kiểm `generation_id`; chunk còn trên đường | Guard downlink; `client.clear(generation_id)` |
| Transcript của người khác xuất hiện | State dùng chung (ASR cache, VAD) hoặc callback session cũ | State theo session; session generation |
| Giọng đục dù TTS 48 kHz | Trần 16 kHz trong pipeline (§16.9) | Ghi vào contract; xin 16 kHz ngay hoặc giữ rate gốc |
| Click giữa các chunk | Cắt giữa mẫu s16; resampler không giữ state giữa các chunk; không fade khi clear | Giữ byte lẻ; resampler có state; fade ngắn |
| Giật cục ở downlink | Không pre-buffer; RTF > 1 (CPU nhiều stream)[^vieneurt] | Pre-buffer 150–300 ms (GPU), ≥ 300 ms (CPU); giới hạn stream |
| Bộ nhớ tăng theo độ dài cuộc gọi | Turn buffer, partial window hoặc bảng `chunk_id` không được release | Test "idle = 0"; release ở commit |
| Băng thông uplink cao hơn dự tính 33 % | Gửi base64 trong JSON thay vì binary | Binary frame (256 kbps so với 341 kbps, **Reproduced** mục 2) |

---

## 16.14 Bài tập thực hành

1. **Vẽ contract cho Profile B** (Nemotron streaming 160 ms + VieNeu). Viết lại bảng §16.3.2–16.3.4 cho profile này, thêm cột "lookahead của ASR" và "ai giải phóng cache".
2. **Chạy hai script ở Phụ lục.** Đổi transport sang 32 ms và tính lại bội chung với khối VAD. Đổi chunk ASR sang 80 ms và 1 120 ms, kiểm tra tính chia hết.
3. **Policy gap.** Sửa `Ingress` để mất dài (> 25 frame) không ném lỗi mà phát sự kiện `turn.invalidated(turn_id)`. Viết test cho mất 1, 5, 30 frame.
4. **Trần 16 kHz.** Gọi VieNeu `/v1/audio/speech` với `sample_rate=48000` và `16000` cho cùng một câu có nhiều âm /s/, /x/, /ph/. Xem spectrogram hai file và nghe A/B trên tai nghe tốt. Ghi nhận xét (nhãn: Reproduced nếu bạn chạy thật).
5. **Contract test VieNeu.** Viết một test gửi `sample_rate=24000`, đọc `X-Sample-Rate`, và khẳng định adapter phát đúng tốc độ. Thêm một test cố tình để adapter tin nhầm 48 kHz và kiểm tra `AudioContract.check` bắt được.
6. **Join log.** Dùng trace mẫu ở §16.8.3, viết một hàm nhóm sự kiện theo `(turn_id, revision, generation_id)` và tính: thời gian từ `vad.speech_end` cuối cùng của revision được commit tới `audio.start` của generation tương ứng.

---

## 16.15 Đáp án các câu hỏi tự kiểm tra

**Q1.** Xem sơ đồ §16.1 và ba bảng §16.3.2–16.3.4. Tóm tắt một dòng cho mỗi đoạn: client capture f32 ở rate của context (thường 48 kHz) → uplink s16le 16 kHz mono 20 ms (640 byte), state resampler ở client → gateway f32 16 kHz vào ring buffer, state là ring, `w`, resampler của session → VAD 512 mẫu f32, state `VADIterator` của session → ASR streaming 160/320 ms, cache của session; turn-final đọc turn buffer của lượt → text theo mệnh đề, có `generation_id` và `chunk_id` → TTS s16le 48 kHz mono, chunk 160/320 ms, slot ở server TTS → client queue, state `generation_id` và `last_seq` → worklet f32 ở rate context, đếm mẫu đã render.

**Q2.** Mỗi đơn vị phục vụ một ràng buộc khác nhau: transport cân bằng overhead với độ trễ đóng gói; Silero được huấn luyện với cửa sổ cố định 512 mẫu; ASR cần đủ ngữ cảnh mỗi bước; TTS cần ngữ cảnh mệnh đề để có prosody; codec sinh theo frame 80 ms. Ép chung một đơn vị sẽ buộc một thành phần chạy sai điều kiện. Cách nối: một timeline chung theo chỉ số mẫu (ring buffer), mỗi consumer giữ con trỏ đọc riêng; ba loại adapter là reblocker (320 → 512, bội chung 160 ms), accumulator theo sự kiện (token → mệnh đề, khối VAD → lượt) và pacer (chunk 320 ms → RTP 20 ms, queue → quantum 128). Phía bot, timeline là mẫu output, với bảng `chunk_id → khoảng mẫu`.

**Q3.** Pre-roll lấy từ **ring buffer ở gateway**, vốn ghi liên tục bất kể VAD. Khi `speech_start`, turn buffer copy `[speech_start − 200…300 ms, w)`. Nếu client gating bằng VAD riêng thì client phải gửi kèm pre-roll. Turn buffer giữ từ `speech_start` tới khi lượt được commit **và** final ASR được chấp nhận. Với thiết kế speculative, nó giữ qua cả grace reopen, vì HF s2s phát lại audio đã tích luỹ khi lượt mở lại. Với two-pass, nó giữ tới khi final-pass xong. Luôn có trần độ dài (vd 30 s), và giải phóng ngay khi revision bị thay hoặc session đóng.

**Q4.** Chèn im lặng đúng 100 ms **và đánh dấu gap**. Nối thẳng làm mọi timestamp phía sau sớm 100 ms (frame `seq=60` bị gán 1 100 ms thay vì 1 200 ms), làm sai mốc "mẫu speech cuối", sai latency, và dán liền hai nửa âm tiết thành một âm không tồn tại. Chèn im lặng mà không đánh dấu thì VAD có thể tính im lặng giả vào endpoint và cắt lượt sớm. Nếu gap dài (vd > 500 ms) thì lượt đó nên bị huỷ hoặc hỏi lại.

**Q5.** Dùng chung `VADIterator`: state model trộn audio hai người, endpoint và barge-in sai một cách không lặp lại được. Dùng chung ASR cache: transcript của B có thể chứa từ của A, tức là rò rỉ dữ liệu giữa người dùng. Weights được chia sẻ; state thì không bao giờ. Batching vẫn được nếu state tách theo hàng.

**Q6.** `session_id` cho một kết nối; `turn_id` cho một lượt user; `revision` cho một phiên bản của lượt; `generation_id` cho một response của bot; `chunk_id` cho một mệnh đề và đơn vị TTS tương ứng; `sequence` cho một message trên một luồng. Lỗi "bot phát tiếp câu cũ sau khi bị ngắt" bị chặn bởi **`generation_id`**: barge-in tăng nó, client bỏ mọi chunk có `generation_id` cũ, kết hợp `sequence` để bỏ chunk trùng hoặc đảo thứ tự.

**Q7.** Vì audio giữa các stage của HF s2s là khối 16 kHz mono int16 512 mẫu: `--tts openai` chuyển PCM của TTS về 16 kHz, và transport chỉ upsample lại sau đó. Tín hiệu 16 kHz không chứa được gì trên 8 kHz (Nyquist), và upsample không khôi phục được. Thanh điệu (F0, vài trăm Hz) và độ rõ không bị ảnh hưởng. Mất phần năng lượng cao của các âm xát và "độ thoáng" của giọng, nên giọng nghe đục hơn. Chấp nhận được cho MVP và telephony; không chấp nhận được khi đánh giá chất lượng TTS hoặc khi giọng là một phần của sản phẩm.

---

## 16.16 Tóm tắt một trang

- **Mỗi cạnh qua ranh giới có contract:** rate, kênh, dtype, container, framing, metadata, kết thúc, cancel, lỗi. Kiểm bằng giá trị thật (header, `audio.start`), không bằng cấu hình.
- **Uplink chuẩn hoá về 16 kHz mono f32 một lần.** Downlink **giữ rate gốc** tới playback, trừ khi transport bắt buộc khác.
- **Một timeline theo chỉ số mẫu, nhiều cửa sổ đọc.** Transport 20 ms, VAD 32 ms, ASR 160/320 ms gặp nhau mỗi 160 ms. Text và TTS dùng timeline của audio bot, với bảng `chunk_id → khoảng mẫu`.
- **Ring buffer ≥ cửa sổ đọc lùi dài nhất** (8 s nếu dùng Smart Turn). Pre-roll lấy từ ring. Turn buffer sống từ `speech_start` tới commit + final, có trần.
- **Gap phải lấp đúng thời lượng và được đánh dấu.** Không bao giờ nối thẳng.
- **State theo session, không chia sẻ.** Weights chia sẻ được; state thì không.
- **Sáu định danh**, mỗi cái một phạm vi. `generation_id` chặn audio cũ; `revision` chặn hành động trên bản cũ; `sequence` chặn mất và trùng.
- **Biết trần băng thông của pipeline.** HF s2s giới hạn ở 16 kHz: giọng đục hơn, thanh điệu vẫn nguyên.

---

## Hạn chế và phạm vi bao phủ

- Chương không chạy pipeline, không gọi VieNeu hay HF s2s, không đo mạng. Mọi hợp đồng của backend là **Reported** qua wiki. Hai script chỉ kiểm chứng phép tính và hành vi của chính chúng.
- Kích thước ring buffer 8 s dựa trên cửa sổ Smart Turn mà wiki ghi qua report thứ cấp. Nếu dùng turn detector khác, hãy định cỡ lại.
- Policy gap, ngưỡng "mất dài" 500 ms, trần downlink 2 s và cách đánh số `sequence` là đề xuất (**Synthesis**), chưa được thử trên mạng thật.
- Phần ngữ âm ở §16.9.2 là kiến thức nền chung; wiki chưa có phép đo cảm nhận nào về VieNeu ở 16 kHz so với 48 kHz.
- Wiki chưa xác nhận các bước để giữ rate gốc qua HF s2s (sửa handler và transport); mục đó là **Unverified**.

---

## Phụ lục chương

### Script 1: số học dataflow (`/tmp/ch16/dataflow_sim.py`, đã chạy)

```python
# Chương 16 — mô phỏng số học dataflow và audio contract (Python thuần, không đo model thật)
import math
from math import gcd

SR = 16_000
def ms2s(ms, sr=SR): return int(round(ms * sr / 1000))
def lcm(a, b): return a * b // gcd(a, b)

# 1) Đơn vị khác nhau: transport 20 ms, VAD 512 samples, ASR chunk 160/320 ms
tr, vad = ms2s(20), 512
L = lcm(tr, vad)
print(f"1a. transport={tr} samples, VAD={vad} samples, LCM={L} samples = {L*1000/SR:.0f} ms"
      f" = {L//tr} frame transport = {L//vad} block VAD")
for asr_ms in (160, 320, 560):
    a = ms2s(asr_ms)
    print(f"1b. ASR chunk {asr_ms} ms = {a} samples; chia hết cho VAD block? {a % vad == 0};"
          f" chia hết cho transport frame? {a % tr == 0}")

# 1c. Reblock: độ trễ chờ đủ khối (từ lúc mẫu cuối của frame đến lúc khối VAD hoàn tất)
def reblock_waits(frame, block, n_blocks=500):
    # Mẫu cuối của khối j là mẫu thứ (j+1)*block; nó chỉ tới gateway khi trọn frame chứa nó tới.
    waits = []
    for j in range(n_blocks):
        end = (j + 1) * block
        arrive = math.ceil(end / frame) * frame
        waits.append((arrive - end) / SR * 1000)
    return waits
w = reblock_waits(tr, vad)
print(f"1c. VAD reblock: khối hoàn tất trễ hơn mẫu cuối của nó: min {min(w):.0f} ms, max {max(w):.0f} ms,"
      f" tb {sum(w)/len(w):.1f} ms")

# 2) Băng thông theo cạnh (payload audio, chưa tính header giao thức)
def kbps(sr, ch, bytes_per_sample): return sr * ch * bytes_per_sample * 8 / 1000
rows = [
    ("mic float32 48k mono (trong trình duyệt)", kbps(48_000, 1, 4)),
    ("uplink WS PCM16 16k mono (binary)", kbps(16_000, 1, 2)),
    ("uplink WS PCM16 16k mono (base64 JSON)", kbps(16_000, 1, 2) * 4 / 3),
    ("uplink PCM16 24k mono (OpenAI Realtime / HF demo)", kbps(24_000, 1, 2)),
    ("downlink VieNeu pcm s16le 48k mono", kbps(48_000, 1, 2)),
    ("downlink VieNeu SSE base64 48k", kbps(48_000, 1, 2) * 4 / 3),
    ("VieNeu SDK float32 48k (in-process)", kbps(48_000, 1, 4)),
]
for name, v in rows:
    print(f"2.  {name:52s} {v:7.0f} kbps")

# 3) Kích thước theo cạnh
print(f"3a. frame transport 20 ms PCM16 16k = {ms2s(20)*2} byte; Opus 20 ms ở 48k = {ms2s(20,48000)} samples")
print(f"3b. VAD block 512 float32 = {512*4} byte")
tts_chunk_48 = int(0.320 * 48_000)
print(f"3c. TTS chunk 320 ms @48k = {tts_chunk_48} samples = {tts_chunk_48*2} byte s16 = {tts_chunk_48*4} byte f32")
c16 = tts_chunk_48 // 3
print(f"3d. cùng chunk sau khi ép về 16k (HF s2s --tts openai) = {c16} samples = {c16//512} block 512")
print(f"3e. AudioWorklet render quantum 128 frames @48k = {128/48:.2f} ms; 1 chunk TTS = {tts_chunk_48//128} quantum")

# 4) Bộ nhớ theo session (float32 16k mono trừ khi ghi khác)
def mb(samples, b=4): return samples * b / 1e6
items = [
    ("pre-roll 300 ms", ms2s(300)),
    ("ring buffer 8 s (đủ cửa sổ Smart Turn 8 s)", ms2s(8000)),
    ("turn buffer trung bình 5 s", ms2s(5000)),
    ("turn buffer trần 30 s (MAX_UTTERANCE_MS)", ms2s(30_000)),
]
tot = 0
for name, n in items:
    print(f"4.  {name:45s} {n:7d} samples  {mb(n)*1000:7.1f} KB")
worst = ms2s(8000) + ms2s(30_000)
print(f"4z. trường hợp xấu (ring 8 s + turn 30 s) float32: {mb(worst):.2f} MB/session;"
      f" x200 session = {mb(worst)*200:.0f} MB; int16 = một nửa")
down = int(2.0 * 48_000)
print(f"4y. downlink queue giới hạn 2 s @48k float32 = {mb(down)*1000:.0f} KB/session")

# 5) Gap: nối thẳng vs chèn im lặng
frames = list(range(100))                 # 100 frame 20 ms = 2 s
lost = set(range(40, 45))                 # mất 5 frame liên tiếp (100 ms)
recv = [s for s in frames if s not in lost]
t_concat = {s: i * 20 for i, s in enumerate(recv)}      # timeline nối thẳng
t_fill = {s: s * 20 for s in recv}                      # timeline theo sequence
print(f"5a. frame seq 60: nối thẳng → {t_concat[60]} ms, theo sequence → {t_fill[60]} ms,"
      f" lệch {t_fill[60]-t_concat[60]} ms")
print(f"5b. sau mất gói, mọi timestamp phía sau lệch {len(lost)*20} ms nếu nối thẳng; 'last speech sample' đo sai cùng lượng")

# 6) Trần 16 kHz: tone 3 kHz + 10 kHz ở 48k → hạ về 16k (lọc thông thấp + decimate 3) → còn gì
def sinc(x): return 1.0 if x == 0 else math.sin(math.pi * x) / (math.pi * x)
def lowpass_taps(fc, fs, n=129):
    m = (n - 1) / 2
    taps = [2 * fc / fs * sinc(2 * fc / fs * (i - m)) * (0.54 - 0.46 * math.cos(2 * math.pi * i / (n - 1))) for i in range(n)]
    s = sum(taps); return [t / s for t in taps]
def goertzel_amp(x, f, fs):
    k = f / fs; w = 2 * math.pi * k; c = 2 * math.cos(w); s1 = s2 = 0.0
    for v in x: s0 = v + c * s1 - s2; s2, s1 = s1, s0
    p = s1 * s1 + s2 * s2 - c * s1 * s2
    return 2 * math.sqrt(max(p, 0)) / len(x)
fs = 48_000; N = 4800
x = [0.5 * math.sin(2 * math.pi * 3000 * n / fs) + 0.5 * math.sin(2 * math.pi * 10_000 * n / fs) for n in range(N)]
taps = lowpass_taps(7_200, fs)
y = [sum(taps[k] * x[n - k] for k in range(len(taps)) if n - k >= 0) for n in range(N)]
d = y[200::3]                             # bỏ phần khởi động bộ lọc, decimate 3 → 16k
print(f"6a. trước: biên độ 3 kHz={goertzel_amp(x,3000,fs):.2f}, 10 kHz={goertzel_amp(x,10000,fs):.2f} (fs=48k)")
print(f"6b. sau 16k có lọc: biên độ 3 kHz={goertzel_amp(d,3000,16000):.2f}; tại 6 kHz (chỗ alias của 10 kHz)={goertzel_amp(d,6000,16000):.3f}; 10 kHz mất hẳn (Nyquist 8 kHz)")
naive = x[::3]                            # decimate không lọc
print(f"6c. decimate KHÔNG lọc: 10 kHz bị gập về 6 kHz → biên độ tại 6 kHz = {goertzel_amp(naive,6000,16000):.2f} (aliasing)")

# 7) played_sample_offset → phần text đã phát (không có alignment: tỷ lệ theo ký tự trong chunk)
chunks = [("Dạ, em kiểm tra rồi ạ.", 1.40), ("Chuyến bay VN123 khởi hành lúc tám giờ.", 2.60), ("Anh có muốn đổi giờ không?", 1.70)]
played = int(2.9 * 48_000)
acc = 0
for txt, dur in chunks:
    n = int(dur * 48_000)
    if played >= acc + n:
        print(f"7.  ĐÃ PHÁT HẾT : {txt}")
    elif played > acc:
        frac = (played - acc) / n
        print(f"7.  PHÁT DỞ {frac:4.0%}: {txt[:int(len(txt)*frac)]}… (ước lượng theo ký tự, không phải alignment)")
    else:
        print(f"7.  CHƯA PHÁT   : {txt}")
    acc += n
```

Đầu ra khi chạy (Python 3, không numpy, 2026-10-07):

```text
1a. transport=320 samples, VAD=512 samples, LCM=2560 samples = 160 ms = 8 frame transport = 5 block VAD
1b. ASR chunk 160 ms = 2560 samples; chia hết cho VAD block? True; chia hết cho transport frame? True
1b. ASR chunk 320 ms = 5120 samples; chia hết cho VAD block? True; chia hết cho transport frame? True
1b. ASR chunk 560 ms = 8960 samples; chia hết cho VAD block? False; chia hết cho transport frame? True
1c. VAD reblock: khối hoàn tất trễ hơn mẫu cuối của nó: min 0 ms, max 16 ms, tb 8.0 ms
2.  mic float32 48k mono (trong trình duyệt)                1536 kbps
2.  uplink WS PCM16 16k mono (binary)                        256 kbps
2.  uplink WS PCM16 16k mono (base64 JSON)                   341 kbps
2.  uplink PCM16 24k mono (OpenAI Realtime / HF demo)        384 kbps
2.  downlink VieNeu pcm s16le 48k mono                       768 kbps
2.  downlink VieNeu SSE base64 48k                          1024 kbps
2.  VieNeu SDK float32 48k (in-process)                     1536 kbps
3a. frame transport 20 ms PCM16 16k = 640 byte; Opus 20 ms ở 48k = 960 samples
3b. VAD block 512 float32 = 2048 byte
3c. TTS chunk 320 ms @48k = 15360 samples = 30720 byte s16 = 61440 byte f32
3d. cùng chunk sau khi ép về 16k (HF s2s --tts openai) = 5120 samples = 10 block 512
3e. AudioWorklet render quantum 128 frames @48k = 2.67 ms; 1 chunk TTS = 120 quantum
4.  pre-roll 300 ms                                  4800 samples     19.2 KB
4.  ring buffer 8 s (đủ cửa sổ Smart Turn 8 s)     128000 samples    512.0 KB
4.  turn buffer trung bình 5 s                      80000 samples    320.0 KB
4.  turn buffer trần 30 s (MAX_UTTERANCE_MS)       480000 samples   1920.0 KB
4z. trường hợp xấu (ring 8 s + turn 30 s) float32: 2.43 MB/session; x200 session = 486 MB; int16 = một nửa
4y. downlink queue giới hạn 2 s @48k float32 = 384 KB/session
5a. frame seq 60: nối thẳng → 1100 ms, theo sequence → 1200 ms, lệch 100 ms
5b. sau mất gói, mọi timestamp phía sau lệch 100 ms nếu nối thẳng; 'last speech sample' đo sai cùng lượng
6a. trước: biên độ 3 kHz=0.50, 10 kHz=0.50 (fs=48k)
6b. sau 16k có lọc: biên độ 3 kHz=0.50; tại 6 kHz (chỗ alias của 10 kHz)=0.000; 10 kHz mất hẳn (Nyquist 8 kHz)
6c. decimate KHÔNG lọc: 10 kHz bị gập về 6 kHz → biên độ tại 6 kHz = 0.50 (aliasing)
7.  ĐÃ PHÁT HẾT : Dạ, em kiểm tra rồi ạ.
7.  PHÁT DỞ  58%: Chuyến bay VN123 khởi … (ước lượng theo ký tự, không phải alignment)
7.  CHƯA PHÁT   : Anh có muốn đổi giờ không?
```

Giới hạn: băng thông ở mục 2 chỉ là payload audio, chưa tính header WebSocket/TCP/IP hay overhead SSE. Thời lượng các mệnh đề ở mục 7 là giả định. Bộ lọc ở mục 6 là FIR Hamming 129 tap viết tay để minh hoạ, không phải soxr.

### Script 2: state audio theo session (`/tmp/ch16/session_audio.py`, đã chạy)

Phần class đã in ở §16.11, cộng thêm `AudioContract` ở §16.3.6. Phần chạy thử:

```python
if __name__ == "__main__":
    ring = Ring(seconds=8)
    ing = Ingress(ring)
    tone = array("f", [0.1]) * FRAME
    for seq in range(100):                   # 2 s audio, mất seq 40..44, seq 41 tới muộn
        if 40 <= seq <= 44:
            continue
        ing.on_frame(seq, tone)
    ing.on_frame(41, tone)
    print("A. w =", ring.w, "samples =", ring.w * 1000 // SR, "ms; gaps =", ing.gaps, "; late =", ing.late)

    tb = TurnBuffer(ring, max_ms=1_500)
    tb.open(speech_start_sample=SR + 4_800)  # VAD báo speech_start ở t = 1.3 s, lúc đó w = 2.0 s
    print("B. mở lượt: copy từ", tb.start, "→", ring.w, "=", len(tb.data) * 1000 // SR, "ms (gồm 300 ms pre-roll)")
    n = 0
    while tb.append(tone):
        n += 1
    print("   append", n + 1, "frame thì chạm trần 1.5 s →", len(tb.data) * 1000 // SR, "ms; buộc endpoint")
    tb.release()

    small = Ring(seconds=0.2)
    small.push(array("f", [0.0]) * SR)
    try:
        small.read(small.w - int(0.3 * SR), small.w)
    except IndexError as e:
        print("C. ring 200 ms + pre-roll 300 ms →", e)

    vieneu_http = AudioContract(48_000, 1, "s16le", "chunked")
    try:
        vieneu_http.check(sample_rate=24_000, channels=1, sample_format="s16le")  # X-Sample-Rate: 24000
    except ValueError as e:
        print("D.", e)

    dl = Downlink(generation_id=7)
    for s in range(3):
        dl.on_chunk(7, s, 15_360)
    dl.clear(8)                              # barge-in: generation_id++ rồi client.clear
    dl.on_chunk(7, 3, 15_360)                # chunk cũ tới muộn
    dl.on_chunk(8, 0, 15_360)
    dl.on_chunk(8, 0, 15_360)                # trùng sequence
    print("E. accepted =", dl.accepted, "samples; dropped =", dl.dropped)
```

Đầu ra khi chạy (Python 3, 2026-10-07):

```text
A. w = 32000 samples = 2000 ms; gaps = [(12800, 1600)] ; late = 1
B. mở lượt: copy từ 16000 → 32000 = 1000 ms (gồm 300 ms pre-roll)
   append 25 frame thì chạm trần 1.5 s → 1500 ms; buộc endpoint
C. ring 200 ms + pre-roll 300 ms → đoạn yêu cầu đã bị ghi đè: ring quá nhỏ cho pre-roll/turn
D. audio contract mismatch: got (24000, 1, 's16le'), want (48000, 1, 's16le')
E. accepted = 61440 samples; dropped = [(7, 3), (8, 0)]
```

Đọc kết quả: (A) mất 5 frame được lấp đúng 1 600 mẫu tại mẫu 12 800, timeline vẫn tròn 2 000 ms, và frame 41 tới muộn bị bỏ. (B) `speech_start` tại 1,3 s cho turn buffer bắt đầu từ 1,0 s (pre-roll 300 ms). (C) ring quá nhỏ báo lỗi thay vì trả dữ liệu đã bị ghi đè. (D) contract bắt được rate lệch. (E) client nhận 3 chunk của generation 7 và 1 chunk của generation 8, bỏ chunk cũ tới muộn và chunk trùng.

### Liên kết sang chương khác

- Chương 2 (số hoá): công thức quy đổi, int16 ↔ float32, resample có state, `AudioFormat` (§2.9.3) và ingress tối thiểu (§2.10).
- Chương 3 (định dạng, codec): WAV header, Opus, base64, μ-law, nền cho các trường "container" của contract.
- Chương 5 (ngữ âm tiếng Việt): vì sao mất âm tiết đầu là mất thông tin phân biệt; vì sao trần 8 kHz không làm mất thanh điệu.
- Chương 6 (capture, playback): ring buffer, pre-roll (§6.11), pre-buffer, underrun, đo phía client.
- Chương 7 (front-end âm học): AEC cần tín hiệu tham chiếu có timeline khớp với downlink.
- Chương 8 (transport): WebSocket, WebRTC, backpressure theo credit, HTTP streaming và huỷ request.
- Chương 10 (VAD, turn): `VADIterator`, `speech_pad_ms`, hai triết lý commit, nền cho vòng đời turn buffer.
- Chương 11 (ASR): contract input/output của ASR, `audio_range`, revision.
- Chương 13 (TTS): output contract của TTS (§13.7), chuyển 48 kHz float32 → 16 kHz int16 (§13.9).
- Chương 15 (kiến trúc): các model full-duplex có contract rate vào/ra khác nhau.
- Chương 17 (turn-taking, cancellation): state machine dùng các định danh ở §16.8; barge-in dùng guard downlink ở §16.11.
- Chương 18 (async, streaming): hiện thực ring buffer, con trỏ đọc và queue bounded bằng `asyncio`.
- Chương 19 (cầu text → speech): chunker và normalizer ở cạnh T2–T3.
- Chương 20 (latency): timestamp theo chỉ số mẫu và wall clock, join log theo định danh.

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) — §3 nguyên tắc 2 (một owner cho quyết định lượt), 4 (mỗi backend khai báo sample rate, dtype, số kênh, framing, cách cancel; VieNeu SDK float32 48 kHz, HTTP s16le 48 kHz; HF s2s `--tts openai` chuyển về khối 16 kHz mono int16, trần 16 kHz; MOSS stereo/mono; Higgs SSE base64 WAV), 5 (không hành động trên văn bản chưa commit); §4 (sơ đồ kiến trúc tổng thể: ring buffer 20 ms, ba nhánh, pre-roll 200–300 ms, `audio.played(offset)`); §5.1 (WebSocket PCM16 16 kHz mono binary 20–32 ms, không base64; lệch sample rate "9/10 lần"; telephony decode trước, upsample không khôi phục thông tin); §5.4.2 (Nemotron chunk 160/320 ms); §5.5 (quy tắc chunker); §7.1 (reblock 512/256, không ép chung chunk length, 16 kHz cho ASR, giữ rate gốc ở output, pre-roll, state theo session, policy gap); §7.2 (event schema và các định danh; final-pass chạy lại turn audio đã giữ; giải phóng khi session đóng); §7.3 (trình tự barge-in, lưu phần đã phát kèm `[bị ngắt]`; played offset khi không có alignment); §8.1 (critical path; join log theo định danh); §8.2 (ngân sách tham khảo); §8.3 (playback buffer, đánh đổi bớt giật và chậm bắt đầu).
[^wikidesign]: [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md) — "Hợp đồng điều khiển chi tiết" §1 (privacy: logs metadata, corpus opt-in, speaker embedding không ghi log) và §2 (bảng policy: "End candidate có Smart Turn: 200–300 ms silence rồi classifier trên 8 s audio cuối"); "Deploy tools: chọn đúng tầng" (deployment plan: một model owner mỗi process); "Latency, monitoring và release gates" (gate 5 contract tests: 48k/24k/unknown rate, mono/stereo, dtype, PCM-vs-WAV/SSE, sequence/revision đơn điệu, cancel giữa chunk, disconnect/reconnect, 429, không stale audio, không duplicate final). Trang `status: draft`.
[^hf]: [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md) — "Endpointing and turn-taking" (reopen thành revision mới, phát lại audio đã tích luỹ, bỏ việc chưa commit; trần unanswered reopen theo thời gian audio đã stream, processing và output hold theo wall clock; response gắn với generation input); "Supported components" (Supertonic 44,1 kHz → 16 kHz); "TTS notes" (OmniVoice float 24 kHz → khối int16 16 kHz).
[^engine]: [Speech-to-Speech Realtime Engine](../wiki/speech-to-speech-realtime-engine.md) — Architecture (inbound `input_audio_buffer.append` base64 PCM, resample 16 kHz, khối 512 mẫu); Client-to-server events (`conversation.item.truncate` là no-op); Interruption (`CancelScope`, generation counter, `is_stale`, output gắn `cancel_generation`); WebRTC transport (Opus 48 kHz, resampler có state sang/từ 16 kHz, RTP 20 ms, gửi im lặng khi rảnh, `oai-events` data channel, từ chối `input_audio_buffer.append`, `output_audio_buffer.clear`).
[^backends]: [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](../wiki/speech-to-speech-openai-compatible-backends.md) — "OpenAI-compatible STT" (WAV PCM16 16 kHz mono trong bộ nhớ); "STT turn and session lifecycle" (session generation kiểm nguyên tử khi đẩy queue); "Stateful streaming STT" (giữ pre-speech padding, không upload audio rảnh; OpenAI Realtime cần 24 kHz, resample từ 16 kHz); "OpenAI-compatible TTS" (PCM16 theo `--openai_tts_sample_rate`, chuyển dần về khối 16 kHz mono int16 512 mẫu; cancel best-effort).
[^demo]: [Speech-to-Speech Browser Demo](../wiki/speech-to-speech-browser-demo.md) — "Audio pipeline notes" (buffering đếm mẫu PCM, không theo thời gian; capture worklet resample về 24 kHz Int16 LE; playback decode Int16 → Float32, nội suy tuyến tính 24 → 48 kHz, fade 32 frame; đếm PCM đã render không tính độ trễ khởi động và underrun, gửi `conversation.item.truncate`).
[^cli]: [Speech-to-Speech CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md) — VAD arguments (`sample_rate=16000`, `speech_pad_ms=500`); OpenAI TTS arguments (`openai_tts_sample_rate=24000`, `openai_tts_blocksize=512`). **Observed** trong argument class đã capture.
[^vieneuapi]: [VieNeu-TTS OpenAI-Compatible Speech API](../wiki/vieneu-tts-openai-speech-api.md) — bảng field `POST /v1/audio/speech` (`response_format` pcm s16le mono / wav độ dài unknown; `stream_format` audio / sse; `sample_rate` 48000/24000/16000/8000, resample từng chunk bằng soxr; `input` ≤ 20 000 ký tự); headers `X-Request-Id`, `X-Sample-Rate`; lỗi `429` kèm `Retry-After`; sự kiện SSE `speech.audio.delta`/`speech.audio.done`; `/health` (`active`, `waiting`); mục Clients (framework giả định 24 kHz phải xin `sample_rate: 24000` hoặc đặt 48 000).
[^vieneurt]: [VieNeu-TTS Streaming Runtime and Performance](../wiki/vieneu-tts-streaming-runtime.md) — "Three numbers" (frame codec 80 ms, chunk đầu 2 frame GPU / 4 frame CPU, chunk sau 4 frame = 320 ms; pre-buffer 150–300 ms); GPU mechanism (continuous batching, slot riêng, sampling theo hàng); CPU (lead-in 4 frame, pre-buffer ≥ 300 ms); bảng troubleshooting (giật khi không pre-buffer hoặc RTF > 1).
[^silero]: [Silero VAD](../wiki/silero-vad.md) — Key characteristics (8 000/16 000 Hz); Dependencies (tensor float32 1-D); Versions and streaming configuration (từ v5 cửa sổ cố định 512 mẫu @16 kHz / 256 @8 kHz; `VADIterator` mỗi session, `reset_states()` khi hết lượt; `speech_pad_ms` 100–200). Phần streaming là AI report thứ cấp.
[^blueprint]: [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md) — "Turn flow and defaults" (client mono 16 kHz s16 PCM 20–32 ms binary, JSON `type` + `sequence`; `PRE_ROLL_MS = 200`, `MAX_UTTERANCE_MS = 30_000`, pre-roll 200–300 ms); "Per-token TTS is rejected" (đơn vị một câu hoặc 20–60 ký tự); "Reference async worker layout" (ring-buffer pre-roll 250 ms) và đoạn đọc tĩnh ghi nhận độ lệch (**Observed**). Nguồn là câu trả lời ChatGPT, chưa kiểm chứng.

---

## 16.17 Lưu ý khi thiết kế và hiện thực pipeline speech-to-speech tiếng Việt

Phần này nối kiến thức của chương với [tài liệu thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md): mục nào của tài liệu phụ thuộc vào dataflow và audio contract, điều gì phải chốt trước khi viết code, chỗ nào tài liệu còn mơ hồ, và lỗi nào dễ mắc khi hiện thực. Toàn bộ phần này là **Synthesis** từ nội dung chương và tài liệu thiết kế, chưa kiểm chứng bằng implementation. Các lưu ý riêng về transport (WebSocket/WebRTC, backpressure, TURN, token) đã nằm ở Chương 8 §8.17, không lặp lại ở đây.

### 16.17.1 Dataflow chạm vào những mục nào của tài liệu thiết kế

| Mục trong tài liệu thiết kế | Chương này quyết định điều gì | Kiến thức trong chương |
|---|---|---|
| §3 nguyên tắc 2 (một owner cho lượt) | Mọi tín hiệu VAD/ASR/Smart Turn đổ về turn owner, gắn chỉ số mẫu | §16.1, §16.4.4 |
| §3 nguyên tắc 4 (audio contract) | Chín trường của contract, kiểm bằng giá trị thật ở biên | §16.3 |
| §3 nguyên tắc 5 (không hành động trên văn bản chưa commit) | `turn.commit(turn_id, revision)` là mốc duy nhất cho side effect | §16.3.3, §16.8 |
| §4 Kiến trúc tổng thể | Sơ đồ cạnh U0–U5, C1–C3, T1–T3, D1–D6 | §16.1 |
| §5.1 Transport, AEC | Định dạng uplink, nơi resample, lệch sample rate "9/10 lần" | §16.3.2, §16.13 |
| §5.2–5.3 VAD, turn | Reblock 512, cửa sổ 8 s của Smart Turn quyết định cỡ ring | §16.4, §16.5.1 |
| §5.6, §5.7 TTS, orchestration | Contract output của VieNeu, trần 16 kHz của HF s2s | §16.3.4–16.3.5, §16.9 |
| §7.1 Audio ingress | Ring buffer, pre-roll, state theo session, policy gap | §16.5, §16.6.3, §16.7 |
| §7.2 Event schema | Sáu định danh, phạm vi và quy tắc tăng | §16.8 |
| §7.3 Barge-in | `played_sample_offset` → bảng `chunk_id → khoảng mẫu` → cắt history | §16.6.4 |
| §8.1 Critical path | "Mẫu speech cuối" đo bằng chỉ số mẫu, nối wall clock qua neo | §16.6.2 |
| §9.2–9.3 VRAM, scaling | Ngân sách bộ nhớ audio theo session; batching với state tách theo hàng | §16.5.5, §16.7.2 |
| §9.5 Privacy | Turn buffer và speaker embedding là dữ liệu nhạy cảm, release đúng hạn | §16.5.3, §16.7.1 |
| §10 gate 5 Contract tests | Danh sách test cụ thể | §16.12 |

### 16.17.2 Những quyết định phải chốt trước khi viết code

1. **Rate chuẩn của từng đoạn, viết thành bảng.** Uplink: 16 kHz mono f32 trong gateway (§7.1). Downlink: rate gốc của TTS, khai báo trong `audio.start`. Ghi rõ **mọi** phép resample trên tuyến: ở đâu, ai làm, có state hay không. Mục tiêu là tối đa một lần resample mỗi chiều (§16.10).
2. **Có chấp nhận trần 16 kHz hay không.** Đây là quyết định sản phẩm, không phải chi tiết kỹ thuật. Nếu Profile A chạy trên HF s2s với `--tts openai`, toàn pipeline bị khoá ở băng thông 8 kHz (§16.9). Nếu chấp nhận: xin VieNeu trả `sample_rate=16000` luôn và ghi trần này vào contract. Nếu không: phải dùng gateway tự viết (hoặc sửa handler và transport của HF s2s, **Unverified**) để giữ rate gốc như §7.1 yêu cầu.
3. **Cỡ ring buffer.** Bằng cửa sổ đọc lùi dài nhất cộng biên: ≥ 8 s nếu dùng Smart Turn, cộng backlog cho phép của ASR streaming. Ghi số này vào config kèm lý do; khi đổi turn detector phải tính lại.
4. **Ai giữ pre-roll.** Uplink liên tục → gateway lấy pre-roll từ ring. Client gating bằng VAD → client phải gửi kèm pre-roll. Đồng thời liệt kê mọi lớp padding (pre-roll gateway, `speech_pad_ms` của Silero, `--speech_pad_ms 500` của HF s2s) để chúng không cộng dồn ngoài ý muốn (§16.5.2).
5. **Triết lý commit, vì nó quyết định vòng đời turn buffer.** Commit cứng sau timeout, speculative + revision (HF s2s), hay two-pass (Profile D) cho ba thời gian giữ turn buffer khác nhau (§16.5.3). Chọn một trước khi viết `TurnBuffer.release()`.
6. **Policy gap uplink.** Chốt: ngưỡng "mất ngắn" (chèn im lặng + đánh dấu), ngưỡng "mất dài" (huỷ lượt hoặc hỏi lại, gợi ý ~500 ms), xử lý frame tới muộn/trùng, và hành vi sau reconnect (§16.6.3).
7. **Cách đánh số `sequence` downlink.** Reset theo generation (client kiểm cặp `(generation_id, sequence)`) hay liên tục cả session. Chọn một, ghi vào contract, viết test (§16.8.2).

### 16.17.3 Chỗ tài liệu thiết kế còn mơ hồ hoặc thiếu, cần bổ sung

| Vị trí | Vấn đề | Đề xuất bổ sung |
|---|---|---|
| §4 "ring buffer 20 ms" | Dễ đọc nhầm thành ring dài 20 ms. 20 ms là **frame transport**; ring phải ≥ 8 s nếu dùng Smart Turn | Sửa thành "frame 20 ms → ring buffer ≥ 8 s, đồng hồ mẫu tuyệt đối" |
| §3 nguyên tắc 4 so với §6 Profile A và §7.1 | §7.1 muốn "giữ sample rate gốc tới playback", nhưng Profile A gợi ý HF s2s `serve`, vốn ép downlink về 16 kHz | Ghi rõ Profile A qua HF s2s là ngoại lệ có chủ đích, hoặc đổi Profile A sang gateway tự viết |
| §7.2 danh sách định danh | Không có `chunk_id` ở dòng định danh chung (chỉ xuất hiện trong `text.chunk`, `audio.chunk`) | Đưa `chunk_id` vào danh sách và mô tả phạm vi như §16.8.1 |
| §7.2 `asr.partial` / `asr.final` | Không mang `turn_id`, `revision`, `audio_range` | Thêm cả ba; `audio_range` theo chỉ số mẫu 16 kHz |
| §7.2 | Không có sự kiện cho gap và lượt hỏng | Thêm `ingress.gap(w_start, n_samples)` và `turn.invalidated(turn_id, reason)` |
| §7.2 `audio.chunk` | Không nói `sequence` đánh số theo generation hay theo session; không có offset mẫu | Chốt quy tắc đánh số; thêm `sample_offset` để client và gateway cùng dựng bảng `chunk_id → khoảng mẫu` |
| §7.1 "policy rõ ràng" cho gap | Chỉ yêu cầu "không nối lệch timeline", chưa có policy cụ thể | Dùng bảng §16.6.3 làm khởi điểm |
| §7.1 pre-roll | Không nói pre-roll lấy từ đâu, cũng không nói quan hệ với `speech_pad_ms` | Ghi "pre-roll copy từ ring" và bảng các lớp padding |
| §7.2 "Final-pass chạy lại trên turn audio đã giữ" | Không nói giữ bao lâu, ai release | Thêm vòng đời turn buffer (OPEN → HOLD → RELEASE) và trần độ dài (vd 30 s) |
| §7.3 bước 5 "chỉ lưu phần đã thực sự phát" | Không nói cơ chế tra từ offset ra text | Thêm bảng `chunk_id → [mẫu đầu, mẫu cuối)` ở TTS adapter; phần phát dở ghi là ước lượng |
| §7.4 pseudo-code | `silero.score(reblock_512(denoise_opt(frame)))` giả định mỗi frame cho đúng một khối; `asr_stream.feed(frame)` và `last_8s_audio` không nói đọc từ đâu | Viết lại theo mô hình "một ring, nhiều con trỏ đọc" (§16.4.4): reblocker trả 0..n khối; ASR và Smart Turn đọc theo chỉ số mẫu |

### 16.17.4 Lưu ý thiết kế theo từng mục

**Audio contract (§3 nguyên tắc 4).**
- Viết contract cho **từng cạnh qua ranh giới**, không chỉ cho từng backend. Cùng VieNeu nhưng SDK (f32) và HTTP (s16le) là hai contract khác nhau.
- Kiểm bằng **giá trị thật** mà backend trả về (`X-Sample-Rate`, header WAV, metadata SSE), không bằng config. Rate không rõ → lỗi contract, không phát.
- `audio.start` mang format của **chính generation đó**. Fallback TTS (§9.4) có thể đổi rate giữa hai generation; client không được giả định rate cố định cho cả session.
- MOSS (codec stereo, ví dụ mono) và Higgs (SSE base64 WAV, mỗi event có header) là hai backend dễ vỡ nhất: viết contract test trước khi đưa vào A/B.

**Audio ingress (§7.1).**
- Một ring buffer theo session là nguồn sự thật. VAD, Smart Turn, ASR streaming và turn buffer mỗi cái một con trỏ đọc. Đừng "đẩy" frame lần lượt qua từng nhánh như pseudo-code §7.4, vì nhánh chậm sẽ chặn nhánh nhanh và mỗi nhánh lại tự dựng timeline riêng.
- Ring phải **ném lỗi** khi bị đọc quá xa (§16.5.1), không trả dữ liệu đã bị ghi đè.
- Nhánh denoise (§3 nguyên tắc 3) có frame size, rate và state riêng. Nó đọc ring rồi đưa vào reblocker của VAD; ASR vẫn đọc audio AEC gốc từ ring. Hai nhánh này **chung timeline**, nên độ trễ thuật toán của denoise phải được bù khi so `speech_start` với `audio_range` của ASR.
- Với tiếng Việt, mất phần đầu âm tiết là mất phụ âm đầu (thông tin phân biệt từ). Test pre-roll với lệnh một âm tiết ("không", "dừng") và lưu ý `--min_speech_ms 384` của HF s2s có thể nuốt luôn các lệnh này (§5.3 thiết kế).

**Event schema và định danh (§7.2).**
- Mọi sự kiện audio mang **chỉ số mẫu**; mọi sự kiện mang ít nhất một định danh. Bước nào không viết được cột "Định danh" ở bảng §16.10 thì không debug được khi có reopen hoặc barge-in.
- Định danh không bao giờ tái sử dụng trong session. Không reset `generation_id` khi sang lượt mới.
- Generation speculative (trên revision chưa commit) vẫn có `generation_id` riêng, và phải bị huỷ khi revision đổi (trace §16.8.3, generation 41).
- Kiểm stale ở **mọi** consumer: LLM client theo từng delta, chunker, TTS adapter, send loop, client queue. Chỉ kiểm ở client thì GPU vẫn sinh audio thừa.

**Barge-in và history (§7.3).**
- `played_sample_offset` phải đếm mẫu **đã render**, không tính pre-buffer và underrun (như HF browser demo). Đếm mẫu đã gửi sẽ lưu vào history cả phần người dùng chưa nghe.
- HF s2s chấp nhận `conversation.item.truncate` như no-op. Nếu dùng HF s2s, việc cắt history phải do gateway của bạn làm.
- Phần phát dở chỉ là **ước lượng theo ký tự** khi không có alignment. Lưu dạng "đã bắt đầu nói: …" kèm `[bị ngắt]`, không giả vờ biết chính xác từ nào đã phát.

**Latency và đo lường (§8).**
- Mốc "mẫu speech cuối của user" ở §8.1 phải lấy từ chỉ số mẫu (VAD), rồi quy ra wall clock qua neo `(w, t_wall)`. Dùng thời điểm gói tới làm mốc là đo cả jitter mạng vào endpoint.
- Log `lag` của ingress. `lag` tăng dần là backlog của gateway, không phải lỗi model.
- Biết các độ trễ cấu trúc nhỏ: reblock 320 → 512 thêm 0–16 ms (tb 8 ms); chunk đầu VieNeu GPU 160 ms nhỏ hơn pre-buffer 200 ms nên client phải chờ một phần chunk thứ hai. Chúng không lớn, nhưng nếu không biết sẽ đổ lỗi nhầm chỗ.
- Join log theo `turn_id`/`revision`/`generation_id`/`chunk_id`, không theo thứ tự thời gian (§8.1 thiết kế).

**Bộ nhớ, scaling và privacy (§9).**
- Audio buffer không phải nút thắt bộ nhớ (~2,4 MB/session trường hợp xấu), nhưng là nơi **rò rỉ** dễ nhất. Đưa "turn buffer = 0 khi idle" và "bảng `chunk_id` được dọn sau khi cắt history" vào test.
- Chia sẻ weights và process giữ model (§9.1); **không bao giờ** chia sẻ `VADIterator`, ASR cache, resampler, turn buffer. Batching qua session chỉ hợp lệ khi state tách theo hàng (như slot của VieNeu).
- Callback đến muộn sau khi session đóng phải bị bỏ bằng một session generation kiểm nguyên tử, giống HF s2s. Dùng chung ASR cache giữa user là **sự cố rò rỉ dữ liệu**, không chỉ là bug.
- Turn buffer, transcript revisions và speaker embedding là dữ liệu nhạy cảm. Release đúng hạn vừa là quản lý bộ nhớ vừa là privacy (§9.5). Giữ lâu hơn cho corpus đánh giá chỉ khi có opt-in.

### 16.17.5 Lưu ý theo profile

| Profile (§6) | Điểm dataflow cần chú ý |
|---|---|
| **A** MVP turn-final | Không có U5a. Turn buffer là đầu vào duy nhất của ASR, nên pre-roll và trần lượt quyết định chất lượng. Nếu chạy qua HF s2s: trần 16 kHz, `speech_pad_ms 500` cộng dồn với pre-roll, browser demo uplink 24 kHz (không phải 16 kHz) |
| **B** native streaming | U5a đọc ring theo chunk 160/320 ms (chia hết cho cả frame 20 ms và khối VAD; 560 ms thì không chia hết cho 512, nhưng vẫn chạy vì đọc theo chỉ số mẫu). ASR cache theo session phải được giải phóng sau final và khi đóng session. `audio_range` của partial phải gắn chỉ số mẫu để turn owner so với VAD |
| **C** quality single-pass | Buffered ASR có rollback: revision của transcript thay đổi nhiều hơn, nên `revision` và quy tắc "commit một lần" quan trọng hơn ở đây |
| **D** two-pass | Turn buffer phải sống tới khi final-pass xong. Hai ASR đọc **cùng** timeline (streaming đọc ring, final đọc turn buffer); final thay revision, không đổ vào luồng partial |
| **E** CPU/edge | Bộ nhớ và CPU cho reblock/resample đáng kể hơn; dùng int16 cho ring nếu cần. VieNeu CPU: chunk đầu 4 frame (320 ms), pre-buffer ≥ 300 ms. Kiểm `lag` để phát hiện CPU không theo kịp thời gian thật |
| **F** license-strict | Không đổi về dataflow; contract test phải chạy lại khi thay backend vì lý do license (VoxCPM2, MOSS có contract output khác VieNeu) |

### 16.17.6 Bổ sung cho release gates (§10)

- **Gate 5 (contract tests):** dùng bảng §16.12 làm danh sách tối thiểu. Thêm ba test mà §10 chưa nêu: message cắt giữa một mẫu s16 (byte lẻ), `speech_start` ngay sau khi session mở (ring chưa đủ pre-roll), và hai session song song nói xen kẽ không rò state.
- **Gate 1 (corpus ASR):** thêm biến số **pre-roll** (0 / 200 / 300 ms) và **gap uplink giả lập** (mất 1, 5, 25 frame giữa lượt). Đo riêng lỗi ở âm tiết đầu lượt.
- **Gate 2 (TTS):** ghi rõ đường nghe khi chấm MOS: rate gốc hay qua trần 16 kHz. Không so điểm của hai đường với nhau. Kiểm spectrogram audio thu ở client để phát hiện trần 8 kHz.
- **Gate 3 (turn và barge-in):** kiểm cắt history theo `played_sample_offset` (đã phát hết / phát dở / chưa phát) và không có audio của generation cũ sau `clear`.
- **Gate 4 (tải):** đo bộ nhớ theo session sau N lượt dài (không được tăng tuyến tính theo độ dài cuộc gọi) và `lag` ingress ở concurrency 1/4/8/16.

### 16.17.7 Thứ tự hiện thực gợi ý, khớp lộ trình §12

1. **Phase 1 (MVP):** `AudioContract` + `check` ở mọi cạnh qua ranh giới; ingress có `sequence` và policy gap; ring buffer theo session với đồng hồ mẫu và neo wall clock; reblocker 512 cho Silero; turn buffer có pre-roll, trần và release; `generation_id`, `chunk_id`, `sequence` trên downlink; guard ở client; `audio.played` đếm mẫu đã render; log join theo định danh. Viết contract test cho backend TTS đã chọn **trước** khi ghép vào pipeline. Ghi quyết định về trần 16 kHz.
2. **Phase 2 (Beta):** con trỏ đọc riêng cho ASR streaming (Profile B) và Smart Turn; nhánh denoise chỉ cho VAD với bù độ trễ; bảng `chunk_id → khoảng mẫu` và cắt history thật; test gap/reconnect; đo `lag` và các độ trễ cấu trúc.
3. **Phase 3 (Production):** giữ rate gốc tới playback nếu sản phẩm cần; turn buffer cho final-pass (Profile D); test tải bộ nhớ theo session; rà retention của turn buffer và speaker embedding theo §9.5.

**Ba điều dễ bị bỏ qua nhất** (Synthesis): (1) mọi vị trí audio đo bằng **chỉ số mẫu** trên một timeline, mọi gap được lấp đúng thời lượng **và** được đánh dấu; (2) state theo session không bao giờ dùng chung, và mọi buffer có điểm release được test; (3) biết trần băng thông thật của pipeline trước khi đánh giá chất lượng giọng.
