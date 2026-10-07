**Chưa. Theo spec hiện tại, pipeline mới streaming ở một số tầng, chưa phải streaming xuyên suốt.** Đây là cấu hình trong tài liệu; chưa có bằng chứng implementation đã chạy đúng như vậy.

## 1. Hiện tại từng tầng đang làm gì?

| Tầng | Theo spec/kế hoạch hiện tại |
|---|---|
| **Audio đầu vào / VAD** | Audio vào liên tục; VAD/turn tracker theo dõi để xác định lượt nói. |
| **STT** | **Turn-final**, cả Qwen và Nemotron: nhận nguyên lượt sau soft-end/cắt lượt, không nhận dạng incremental trong lúc user nói. |
| **LLM** | Yêu cầu **streaming text**, kế hoạch bật `--responses_api_stream`; endpoint thật vẫn cần kiểm tra. |
| **LLM → TTS** | **Chưa chốt/kiểm chứng clause chunking**: phải xác minh HF s2s gửi từng mệnh đề hay chờ cả câu trả lời. |
| **VieNeu TTS** | Có **audio-output streaming**: nhận một đoạn text hoàn chỉnh rồi sinh audio dần. |
| **G-OmniVoice / Gwen** | Đường dùng hiện tại trả **full waveform**. Kế hoạch đề xuất sinh từng câu rồi phát, không phải frame-level streaming. |
| **Playback** | Phải phát incremental và giữ buffer nhỏ; behavior thực của browser còn cần kiểm tra. |

Cơ sở: [spec §3.2–3.4](outputs/spec-poc-speech-to-speech-tieng-viet.md), [kế hoạch §6.4](outputs/ke-hoach-trien-khai-poc-speech-to-speech-tieng-viet.md).

**Điểm quan trọng:** model có chữ “Streaming” trong tên không có nghĩa pipeline đang dùng streaming. Nemotron hiện được nối qua HTTP turn-final nên chưa tận dụng lợi thế đó.

## 2. Tôi đề xuất pipeline như thế nào?

**Streaming ở từng tầng, nhưng giữ ranh giới lượt nói để bảo đảm ý nghĩa. Không dùng cùng một loại/kích thước chunk cho toàn bộ pipeline.**

```text
Mic + AEC
  │ audio frames nhỏ
  ▼
VAD ───────────────────► Turn manager
  │                          │ soft-end / reopen / commit
  ▼                          │
Stateful streaming ASR        │
  │ partial + revisions      │
  └────► transcript được chấp nhận
                │
                ▼
          LLM text stream
                │ text deltas
                ▼
       Semantic clause chunker
                │ mệnh đề đủ nghĩa
                ▼
       Vietnamese normalizer
                │ spoken text
                ▼
       TTS audio-output stream
                │ audio chunks
                ▼
       Bounded playback queue
                ▼
              Loa
```

Đây là **đề xuất Synthesis**, chưa benchmark. Nó dựa trên [thiết kế pipeline](wiki/vietnamese-speech-pipeline-design.md) và [hai tầng streaming TTS](wiki/vietnamese-realtime-tts-selection.md#triển-khai-realtime-hai-tầng-streaming-khác-nhau).

### A. STT: nhận dạng trong lúc user đang nói

Nếu ưu tiên độ trễ, tôi chọn thử:

- Nemotron 3.5, ép `vi-VN`.
- Audio transport khoảng **20 ms/frame**, gom thành chunk ASR **160–320 ms** để thử.
- Giữ encoder/decoder cache riêng cho mỗi session.
- Cuối lượt: flush phần audio còn lại và finalize transcript.
- Không decode từng chunk độc lập rồi nối text; cách đó dễ mất context hoặc trùng từ.

Các kích thước này là **điểm bắt đầu để thử**, không phải SLA. [ASR selection](wiki/vietnamese-realtime-asr-selection.md) phân biệt rõ native streaming, buffered streaming và turn-final.

**Qwen 0.6B turn-final vẫn nên giữ làm baseline.** Không cần thêm Qwen final-pass vào mọi lượt ngay từ đầu; two-pass chỉ thêm khi lỗi nhận dạng chứng minh là cần thiết.

### B. STT → LLM: không gọi LLM cho từng partial

Streaming STT **không có nghĩa mỗi vài từ lại tạo một response LLM**.

Ví dụ:

```text
Partial: "Hủy lịch..."
Final:   "Hủy lịch hôm nay thì không cần, giữ nguyên nhé."
```

Nếu bot hành động hoặc nói quá sớm, phần bổ sung có thể đảo ngược ý nghĩa.

Tôi đề xuất:

1. Trong lúc user nói: cập nhật transcript, chưa phát câu trả lời.
2. Khi soft-end: có thể chạy LLM speculative trên **candidate transcript**.
3. Nếu user nói tiếp hoặc transcript đổi: hủy kết quả speculative không còn khớp.
4. Chỉ cho phát audio/thực hiện tool có side effect sau khi turn được commit.

**Cho phép tính toán sớm, không cam kết ý nghĩa sớm.** Đây cũng là boundary trong [thiết kế — Transcript revisions](wiki/vietnamese-speech-pipeline-design.md#3-transcript-revisions-và-safety-boundary).

### C. LLM → TTS: chunk theo mệnh đề, không theo token

Đây là tầng tôi ưu tiên hoàn thiện trước.

```text
LLM sinh text dần
  → chunker tích lũy
  → đủ một mệnh đề có nghĩa
  → normalize
  → gọi TTS ngay
```

Quy tắc khởi điểm:

- Ưu tiên ranh giới câu `.?!`.
- Với chunk đầu, có thể cắt ở dấu phẩy nếu phần trước đủ nghĩa.
- Gộp những mảnh quá ngắn.
- Không cắt giữa số tiền, ngày, viết tắt hoặc tên riêng chưa hoàn chỉnh.
- Khi LLM kết thúc, flush phần text còn lại.
- Timeout chỉ giúp tìm ranh giới an toàn, không ép đọc một đoạn đang dang dở.

**Chunk đầu có thể ngắn hơn để đáp nhanh; các chunk sau dài hơn để giữ prosody.** Phải tune bằng nghe thử, không chỉ theo số ký tự.

Chunker cần nằm ở **consumer của LLM stream, trước request TTS**. Nếu proxy chỉ nhận full reply rồi mới chia câu, đã mất lợi ích streaming của LLM.

### D. TTS → playback: streaming audio ngay, không gom toàn bộ

Với VieNeu:

- Mỗi request nhận một mệnh đề hoàn chỉnh.
- Forward audio chunk ngay khi có.
- Browser bắt đầu phát sau một buffer nhỏ đã tune.
- Khi đang phát chunk hiện tại, có thể chuẩn bị chunk tiếp theo.
- Giữ thứ tự và giới hạn queue; không sinh trước cả phút audio.

Đây là **clause-level text chunking + audio-output streaming**, không phải native bi-streaming nhận text token liên tục trong cùng request.

Với Gwen/G-OmniVoice, có thể dùng cùng clause chunker, nhưng mỗi clause vẫn phải chờ full waveform. **Chia waveform đã sinh xong thành các gói nhỏ không làm first audio xuất hiện sớm hơn.**

### E. Barge-in: hủy xuyên suốt

Mọi công việc/chunk cần gắn với `turn/revision/generation`.

Khi user ngắt lời:

- Dừng playback và flush audio cũ.
- Hủy LLM, TTS và text đang chờ.
- Bỏ callback/audio tới muộn của generation cũ.
- Tiếp tục thu audio cho lượt mới.

Không được chờ inference backend kết thúc rồi mới làm bot im.

## 3. Tôi sẽ triển khai theo thứ tự nào?

### Bước 1 — Sửa đường output trước

```text
Qwen turn-final
  → LLM streaming
  → clause chunker
  → normalizer
  → VieNeu audio streaming
  → browser incremental playback
```

Giữ baseline hiện tại, nhưng **bắt buộc TTS bắt đầu trước khi LLM hoàn thành toàn bộ câu trả lời**.

### Bước 2 — Thêm streaming STT để A/B

```text
Nemotron stateful streaming
  → finalize tại endpoint
  → cùng đường output phía trên
```

Như vậy đo được lợi ích streaming ASR mà không đổi đồng thời chunker/TTS/playback.

### Bước 3 — Thêm speculation có kiểm soát

Chạy LLM sớm tại soft-end, với reopen/cancel và output gate rõ ràng. Không bắt đầu bằng speculation trên mọi partial.

**Tóm lại: tôi chọn “streaming theo tầng, commit theo lượt”.** Audio chunk nhỏ để vận chuyển, ASR chunk có cache để nhận dạng, text chunk theo mệnh đề để nói, audio-output chunk để phát. Không cố biến mọi tầng thành xử lý từng token tức thì.

*Review này chưa sửa spec/wiki, không mở `raw/` hoặc chạy benchmark.*