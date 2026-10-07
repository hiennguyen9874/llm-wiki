**Theo tôi: thiết kế hiện tại hợp lý để làm PoC, có cơ sở để thử đạt P50 ≤ 1,5 s / P95 ≤ 2,5 s, nhưng chưa đủ bằng chứng để khẳng định “đủ nhanh”.** Nếu mục tiêu là phản hồi gần như tức thì, thường xuyên dưới 1 giây, tôi chưa đặt kỳ vọng đó vào cấu hình hiện tại.

Tôi đã đọc đủ ba tài liệu và các wiki liên quan. Điểm đáng tối ưu nhất **không phải đổi model ngay**, mà là **thời điểm cho phép phát câu trả lời và cách nối LLM streaming → TTS**.

> Các nhận xét và đề xuất dưới đây là **Synthesis**, chưa phải kết quả benchmark.

## 1. Nút thắt lớn nhất: endpointing có thể che hết lợi ích model nhanh

[Spec §3.1](outputs/spec-poc-speech-to-speech-tieng-viet.md) giữ default HF s2s:

- Silence candidate: **64 ms**.
- Speculative reopen: **800 ms**.
- Nếu Smart Turn đánh giá incomplete: delay **600 ms**, output gate tới **2 s**.

Theo [wiki HF s2s — Endpointing and turn-taking](wiki/speech-to-speech-pipeline.md#endpointing-and-turn-taking), STT/LLM được chạy speculative trong thời gian chờ; **64 ms không có nghĩa bot được nói sau 64 ms**.

Điều này có hai hệ quả:

1. **Không cộng 800 ms + toàn bộ ASR + toàn bộ LLM như các bước tuần tự**, nếu chúng thực sự chạy chồng lấn.
2. Nhưng nếu ASR/LLM đã xong sớm, **output gate vẫn có thể quyết định latency**. Đổi ASR nhanh hơn lúc đó không cải thiện nhiều.

Minh họa, **nếu TTS chỉ bắt đầu sau output commit**:

```text
v2v ≈ thời gian tới soft-end
    + max(output-hold, ASR + LLM tới mệnh đề đầu)
    + TTS tới audio đầu
    + transport/playback
```

Đây là mô hình phân tích, không phải timeline implementation đã xác minh; cần kiểm tra TTS có được tính speculative hay không.

**Đề xuất:** giữ default cho baseline R0, nhưng đo riêng:

- soft-end → bắt đầu STT;
- thời điểm response sẵn sàng;
- thời điểm gate được mở;
- thời điểm bắt đầu phát.

Sau đó mới A/B giảm reopen grace, chẳng hạn **800 → 600 → 400 ms**, đồng thời đo cắt lời sai và reopen. Đây là cấu hình thử nghiệm đề xuất, không phải default khuyến nghị.

**Nhánh chờ tới 2 s đặc biệt đáng chú ý:** nếu gate thực sự giữ output tới mốc đó, mục tiêu P95 2,5 s chỉ còn khoảng 0,5 s cho phần việc còn lại.

## 2. Chỗ tôi muốn sửa sớm nhất trong kế hoạch: clause chunking

Trong [kế hoạch §12](outputs/ke-hoach-trien-khai-poc-speech-to-speech-tieng-viet.md), nếu HF s2s gửi cả câu trả lời tới TTS một lần, phương án hiện tại là:

> Không chunk thêm ở proxy; ghi là yếu tố latency.

**Tôi không đồng ý để điểm này chỉ thành một giới hạn được ghi nhận**, nếu tốc độ là mục tiêu chính của PoC.

Phải phân biệt:

```text
Tốt:
LLM đang sinh → đủ mệnh đề đầu → TTS bắt đầu → bot nói

Chậm hơn:
LLM sinh xong toàn bộ → proxy chia câu → TTS bắt đầu
```

Chia câu ở proxy sau khi nhận full reply chỉ giảm một phần thời gian synthesis; **không lấy lại được thời gian đã chờ LLM**.

[Thiết kế canonical — Text→speech bridge](wiki/vietnamese-speech-pipeline-design.md#textspeech-bridge-tiếng-việt) đã đề xuất chunk theo mệnh đề, không chờ full answer và không gửi từng token.

**Tôi sẽ nâng kiểm tra này thành acceptance của M1:**

- TTS nhận mệnh đề đầu **trước khi LLM stream kết thúc**.
- Có timestamp `llm_first_token`, `first_clause_ready`, `tts_request_start`.
- Chunk không cắt giữa số tiền, ngày, tên viết tắt hoặc ý đang dang dở.
- Trong lúc phát chunk hiện tại, chuẩn bị chunk tiếp theo với queue hữu hạn.

Đây có khả năng là tối ưu đem lại lợi ích lớn nhất mà chưa cần thay model.

## 3. Đánh giá từng lựa chọn hiện tại

| Thành phần | Nhận xét của tôi |
|---|---|
| **Qwen3-ASR 0.6B turn-final** | Hợp lý làm baseline đơn giản. Nhưng decode nguyên lượt vẫn nằm sau soft-end; cần đo câu ngắn và dài riêng. |
| **Qwen3-ASR 1.7B** | Giữ làm A/B chất lượng. Chưa có cơ sở chọn làm mặc định nếu latency là ưu tiên. |
| **Nemotron qua HTTP turn-final** | Run hiện tại chưa kiểm tra lợi thế streaming quan trọng nhất của model. |
| **VieNeu streaming** | Lựa chọn baseline có bằng chứng triển khai phù hợp nhất trong nhóm đang chọn. |
| **G-OmniVoice/Gwen full waveform** | Phù hợp A/B giọng và chất lượng; chưa thể kỳ vọng đạt cùng latency như VieNeu. |
| **LLM trên máy riêng** | Hướng tốt để tránh dùng chung GPU speech, nhưng endpoint LLM vẫn là dependency chưa có số đo. |

Cơ sở: [ASR selection](wiki/vietnamese-realtime-asr-selection.md), [TTS selection](wiki/vietnamese-realtime-tts-selection.md), [G-OmniVoice](wiki/g-omnivoice.md), [Gwen](wiki/gwen-tts-0.6b.md).

### Có nên đưa Nemotron streaming lên sớm?

**Có, nếu baseline cho thấy ASR sau endpoint chiếm phần lớn latency.** Khi đó nên thêm một run thử streaming vào cuối Phase 1, thay vì chờ làm toàn bộ backlog Phase 2.

Lợi ích cần kiểm tra là:

> Khi user ngừng nói, phần lớn audio đã được nhận dạng; chỉ còn flush/finalize thay vì decode lại cả lượt.

Nhưng **streaming không tự vượt qua output gate 800 ms**, và chunk 160/320 ms không phải v2v 160/320 ms. [Wiki Nemotron](wiki/nemotron-3.5-asr-streaming-0.6b.md) cũng giữ rõ giới hạn này.

Tôi chưa thêm two-pass lúc này: nó tăng compute và reconciliation trước khi biết baseline thiếu gì.

## 4. Những tối ưu nhỏ nhưng phải làm đúng

### Proxy phải giữ được streaming

[Kế hoạch §4.2](outputs/ke-hoach-trien-khai-poc-speech-to-speech-tieng-viet.md) đã chọn đúng hướng: chuyển đổi streaming, pass-through khi contract khớp.

Cần test thêm:

- Không gom toàn bộ HTTP body rồi mới trả.
- Resampler giữ state qua các chunk.
- Không resample hai lần.
- Client nhận audio đầu khi upstream vẫn đang sinh.

**Không nên bỏ proxy chỉ để tiết kiệm một hop localhost trước khi đo.** Nguy cơ đáng quan tâm hơn là proxy vô tình biến streaming thành buffered output.

### Đo buffer thực của trình duyệt

196 ms trong tài liệu HF là buffer của **client Python**, không phải browser demo. Điểm này đã được kế hoạch sửa đúng.

Tôi sẽ đo browser startup buffer và thử giảm từng bước, theo dõi cả:

- v2v;
- underrun/giật;
- thời gian dừng tiếng khi barge-in.

Buffer nhỏ nhất chưa chắc tốt nhất.

### Barge-in: dừng tiếng trước, giải phóng compute sau

Gwen/G-OmniVoice trong kế hoạch chỉ kiểm disconnect giữa các lần `generate`. Vì vậy:

- Client vẫn phải dừng phát ngay và bỏ audio cũ.
- Không chờ `generate` kết thúc mới xử lý clear.
- Đo riêng **user onset → bot im** và **cancel → backend hết compute**.

Nếu compute cũ chưa dừng, lượt mới còn có thể phải chờ lock/GPU. Đây là vấn đề latency phục hồi, không chỉ lãng phí tài nguyên. Cơ sở: [barge-in wiki](wiki/voice-agent-barge-in-and-echo-handling.md) và kế hoạch §6.4.

### Warmup cả sau khoảng nghỉ

Warmup lúc khởi động là chưa đủ để đại diện mọi lượt. [VieNeu wiki — Benchmarks](wiki/vieneu-tts-v3-turbo.md#benchmarks) ghi nhận tác giả báo thêm 100–300 ms sau GPU idle.

Nên tách:

- warm liên tục;
- lượt sau idle;
- cold start.

Không chỉ warmup rồi loại bỏ toàn bộ hiện tượng người dùng sẽ gặp thật.

## 5. Bộ đo cần một chỉnh sửa quan trọng

Kế hoạch §5.3 đang join audio/log **theo thứ tự lượt**. Với reopen, cancel và nhiều TTS chunk, cách này có nguy cơ gán sai stage latency.

**Đề xuất:** ưu tiên join bằng `session_id`, `turn_id`, `revision`, `response_id`, `chunk_id`; timestamp monotonic đo duration trong từng process. Audio phía client vẫn là căn cứ cho v2v.

Ngoài ra:

- Báo riêng lượt bình thường, lượt incomplete/reopen và lượt barge-in.
- Không chỉ nhìn P95 gộp C1–C4: nó có thể che điều kiện loa ngoài + nhiễu bị chậm.
- Đo **mệnh đề có nghĩa đầu tiên**, không chỉ token đầu hay một tiếng đệm “Vâng…”.

## Kết luận và thứ tự ưu tiên

**Tôi giữ kiến trúc, framework và baseline Qwen 0.6B + VieNeu.** Chưa cần viết lại gateway hay chuyển toàn bộ sang runtime khác.

Thứ tự tôi chọn:

1. **Xác minh và bảo đảm LLM → TTS streaming theo mệnh đề.**
2. **Đo output-hold của turn tracker**, rồi tune grace có kiểm soát.
3. **Giữ streaming xuyên suốt proxy → browser**, tối ưu buffer.
4. **Đo latency LLM thật**, gồm thời gian tới mệnh đề đầu và context dài.
5. **Thêm Nemotron streaming nếu ASR là bottleneck.**
6. Sau đó mới thử optimizer như `torch.compile`/vLLM trên đúng workload; không lấy tốc độ batch từ vendor làm tốc độ hội thoại.

**Tóm lại: đủ tốt để bắt đầu đo, chưa đủ để cam kết nhanh. Rủi ro lớn nhất là model nhanh nhưng orchestration vẫn chờ.**

*Đây là review read-only, chưa sửa tài liệu hay wiki. Không mở `raw/` hoặc chạy inference/benchmark trong phiên này; structural check đã pass, nhưng không xác nhận hiệu năng.*