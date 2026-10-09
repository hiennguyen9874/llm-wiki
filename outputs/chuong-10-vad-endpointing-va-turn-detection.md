# Chương 10. VAD, endpointing và turn detection 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần IV.
> **Chương trước:** [Chương 9. Nền tảng ML cho speech](chuong-09-nen-tang-ml-cho-speech-du-de-doc-model-card.md). **Chương tiếp theo:** [Chương 11. ASR: hợp đồng input/output và hành vi streaming](chuong-11-asr-hop-dong-input-output-va-hanh-vi-streaming.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.2 (VAD), §5.3 (turn detection), §7.1 (barge-in), §11 (mâu thuẫn).
> **Cơ sở:** phần lý thuyết (state machine, hysteresis, đánh đổi FPR/FNR, turn-taking trong hội thoại) là kiến thức giáo trình/kỹ thuật chung. Số liệu model và tham số cụ thể lấy từ wiki, gắn nhãn bằng chứng: [Silero VAD](../wiki/silero-vad.md), [Smart Turn v3.2](../wiki/smart-turn.md), [Turn Detection Models](../wiki/turn-detection-models.md), [Parakeet Realtime EOU 120M v1](../wiki/parakeet-realtime-eou-120m-v1.md), [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md) (**Reported** trừ khi ghi khác; chưa chạy lại model nào). Ví dụ mô phỏng ở §10.4 chạy bằng script Python thuần (**Reproduced**, script ở "Phụ lục chương"). Các suy luận từ số liệu sang trải nghiệm là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Phân biệt ba bài toán hay bị gộp làm một: **phát hiện có tiếng nói** (VAD), **quyết định kết thúc đoạn nói** (endpointing) và **quyết định hết lượt** (turn detection).
2. Dùng được Silero VAD đúng cách: input/output, state, các tham số, ý nghĩa của từng tham số lên hành vi.
3. Vẽ và cài đặt được state machine speech/silence có hysteresis, pre-roll, padding.
4. Hiểu hai triết lý điều khiển lượt: **commit cứng sau timeout** và **speculative + revision**.
5. Đọc được ma trận nhầm lẫn của turn detector và dịch FPR/FNR sang trải nghiệm người dùng.
6. Biết VAD thất bại thế nào khi có echo/nhiễu và vì sao bot có thể tự ngắt mình.
7. Không nhầm VAD làm filter cho ASR với VAD điều khiển lượt nói.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Input và output của Silero VAD là gì? State của nó nằm ở đâu?
- Q2. `threshold`, `min_silence_duration_ms`, `min_speech_duration_ms`, `speech_pad_ms` mỗi cái tác động thế nào?
- Q3. VAD (âm học) khác semantic turn detection thế nào? FPR/FNR của Smart Turn trên tiếng Việt có ý nghĩa gì với trải nghiệm?
- Q4. Vì sao không nên chép default của HF s2s (64 ms/800 ms/2 s) sang cùng bảng tham số với Silero 200–300 ms + 1.2–1.5 s?
- Q5. Vì sao chỉ giảm `min_silence` xuống thật thấp lại làm tệ trải nghiệm?
- Q6. Khi bot đang nói, vì sao VAD có thể "nghe thấy" user dù không ai nói, và xử lý ra sao?

---

## 10.1 Ba bài toán, ba lớp quyết định

Người mới thường nghĩ "VAD phát hiện im lặng thì là hết lượt". Đây là nguồn bug lớn nhất của voice agent. Thực tế có ba lớp:

| Lớp | Câu hỏi | Tín hiệu | Thời gian quyết định | Ví dụ công cụ |
|---|---|---|---|---|
| **VAD** | *Frame này có tiếng nói không?* | Âm học, từng frame 10–32 ms | Tức thì | Silero VAD, TEN VAD, WebRTC VAD |
| **Endpointing** | *Đoạn nói liên tục này bắt đầu/kết thúc ở đâu?* | VAD + luật thời gian (min speech, min silence, pad) | Vài trăm ms | `VADIterator`, `get_speech_timestamps` |
| **Turn detection** | *User đã nói xong ý, bot được phép trả lời chưa?* | Ngữ điệu, nội dung, ngữ cảnh | Thêm 10–100 ms suy luận + chờ | Smart Turn, LiveKit, Namo, `<EOU>` của ASR |

Vì sao tách? Vì **im lặng không đồng nghĩa với hết lượt**. Người nói dừng để nghĩ ("tôi muốn đặt vé đi… Đà Nẵng"), để lấy hơi, để do dự, hoặc đọc số điện thoại từng cụm. Ngược lại, hết lượt đôi khi gần như không có im lặng (user nói tiếp "cảm ơn nhé" rồi bot cắt vào). Vì vậy:

- VAD trả lời về **âm học**, chỉ biết "có/không có tiếng người".
- Endpointing biến chuỗi quyết định nhiễu từng frame thành **đoạn** ổn định.
- Turn detection thêm **ngữ nghĩa/ngữ điệu** để quyết định có nên hành động ngay.

> Wiki ghi rõ giới hạn này: Silero "chỉ phát hiện speech, không hiểu end-of-turn" (§5.2 tài liệu thiết kế, **Reported**).

```text
audio 16 kHz ──► [VAD: p(speech) mỗi 32 ms] ──► [endpointing: state machine, pad, min/max]
                                                       │ "đã im ≥ N ms"
                                                       ▼
                                             [turn detector: complete?]
                                                │ yes                 │ no
                                                ▼                     ▼
                                          chạy ASR/LLM          chờ thêm / timeout dự phòng
```

## 10.2 VAD: xác suất theo frame

### 10.2.1 Bản chất

VAD là bộ phân loại nhị phân trên cửa sổ ngắn: với mỗi frame âm thanh, trả xác suất `p ∈ [0,1]` rằng frame chứa tiếng nói. Các họ chính:

| Họ | Cách làm | Ưu | Nhược |
|---|---|---|---|
| Năng lượng/zero-crossing | So RMS với ngưỡng | Cực rẻ | Hỏng ngay khi nền ồn; coi mọi tiếng to là speech |
| GMM (WebRTC VAD) | Mô hình thống kê trên đặc trưng phổ | Nhẹ, không cần weights lớn | Kém trên nhiễu không dừng, nhạc, tiếng ồn giống giọng |
| Neural nhỏ (Silero, TEN, MarbleNet, FireRed Stream-VAD, PulseVAD) | CNN/RNN/transformer nhỏ học từ dữ liệu lớn | Chính xác hơn nhiều trên nhiễu, vẫn rẻ (Silero báo <1 ms/chunk) | Cần state, có weak spot (Silero: nhạc giống giọng, giọng rất cao) |
| Semantic VAD (Smart Turn, `semantic_vad_heads` của Audio8) | Dự đoán "hết lượt" thay vì "có tiếng" | Phân biệt pause và hết lượt | Cần ngữ cảnh dài hơn, nặng hơn, thiên về ngôn ngữ |

VAD không phân biệt **ai** nói: tiếng TV, người bên cạnh, và tiếng bot vọng lại đều là "speech". Phân biệt người nói là bài toán của speaker embedding/diarization (Chương 14) và echo cancellation (Chương 7).

### 10.2.2 Silero VAD: hợp đồng input/output

Theo [Silero VAD](../wiki/silero-vad.md) (**Reported**):

- MIT, ~2 MB JIT, <1 ms cho một chunk 30+ ms trên một CPU thread, ONNX có thể nhanh hơn 4–5×, hỗ trợ 8000 và 16000 Hz, huấn luyện trên dữ liệu hơn 6000 ngôn ngữ.
- **Từ v5, cửa sổ cố định:** 512 samples (32 ms) ở 16 kHz, 256 samples ở 8 kHz. Tham số `window_size_samples` bị deprecated (**Reported**, AI report).
- Input: tensor `float32` 1 chiều, mono, biên độ chuẩn hoá `[-1, 1]`; sample rate đúng 16 kHz hoặc 8 kHz. **Đừng đưa PCM int16 thô** mà chưa chia 32768: model vẫn chạy nhưng xác suất vô nghĩa. Đây là lỗi hợp đồng audio kinh điển (xem Chương 2, 16).
- Output: một số `p` mỗi chunk. API cao hơn (`get_speech_timestamps`, `VADIterator`) bọc logic ngưỡng và state machine.

**State nằm ở đâu?** Silero là mạng hồi quy: output của chunk *n* phụ thuộc state ẩn (và một ít context mẫu cuối) từ các chunk trước. Hệ quả thực hành:

1. **Một instance/state cho mỗi session** (mỗi kết nối, mỗi user). Dùng chung một model state cho hai luồng làm hai người "nhiễu" nhau.
2. **Phải gọi `reset_states()` khi kết thúc lượt/đổi cuộc gọi**, nếu không state tích lũy từ lượt trước ảnh hưởng chunk đầu của lượt sau (AI report khuyến nghị reset ở mỗi turn end, **Reported**).
3. **Không được bỏ chunk hoặc đưa chunk sai kích thước** giữa chừng; audio phải liên tục. Bỏ frame (ví dụ do backpressure) thì phải coi như có "đứt" và cân nhắc reset.
4. Model weights (stateless) có thể chia sẻ giữa nhiều session; chỉ state ẩn là per-session. Cách làm cụ thể phụ thuộc runtime (PyTorch vs ONNX), hãy kiểm tra wrapper bạn dùng.
5. Dùng `load_silero_vad(onnx=True)` để tránh kéo cả torch vào worker CPU (**Reported**).

Hai API:

```python
# Offline: xử lý cả file, trả danh sách đoạn
speech = get_speech_timestamps(wav, model, return_seconds=True)

# Streaming: mỗi chunk 512 samples, trả {"start": ...} / {"end": ...} / None
vad = VADIterator(model, threshold=0.5,
                  min_silence_duration_ms=250, speech_pad_ms=100)
for chunk in stream_16k_float32(512):
    ev = vad(chunk)          # None, {'start': n} hoặc {'end': n}
vad.reset_states()           # hết lượt
```

(Chữ ký là hiểu biết theo README/API chung, kiểm tra với phiên bản bạn cài; không chạy trong chương này.)

Hai API **không có cùng bộ tham số**, theo mã nguồn Silero các bản v5/v6 (kiến thức chung, không có trong wiki; kiểm tra `utils_vad.py` của bản bạn cài):

| Tham số | `get_speech_timestamps` | `VADIterator` |
|---|---|---|
| `threshold` | có (0.5) | có (0.5) |
| `min_speech_duration_ms` | có (250) | **không có**, phải tự cài |
| `min_silence_duration_ms` | có (100) | có (100) |
| `speech_pad_ms` | có (30) | có (30) |
| `max_speech_duration_s` | có (vô hạn) | **không có** |

Nghĩa là các giá trị "khởi điểm" ở §10.3 (250 ms silence, 100–200 ms pad) là cấu hình bạn **phải truyền vào**, không phải default của thư viện. Với streaming, `min_speech` và `max_speech` thường phải tự viết trong state machine của bạn (§10.4).

### 10.2.3 Frame, latency và phân giải

Với chunk 32 ms, VAD không thể báo "bắt đầu nói" sớm hơn 32 ms sau khi âm xuất hiện, cộng độ trễ của bộ đệm capture (Chương 6) và `min_speech`. Đây là **sàn** của mọi endpointing. TEN VAD dùng hop 10/16 ms, hữu ích khi cần phân giải mịn hơn (**Reported**; có mâu thuẫn về độ chính xác so với Silero, xem §10.9).

## 10.3 Các tham số endpointing và ảnh hưởng

Bốn tham số cốt lõi (tên theo Silero; tham số tương đương có ở WebRTC VAD, Pipecat, HF s2s với tên khác):

### `threshold` (ngưỡng xác suất)

`p ≥ threshold` → frame coi là speech. Thấp: nhạy, bắt được giọng nhỏ nhưng dễ kích hoạt bởi nhiễu; cao: sạch hơn nhưng bỏ sót đầu/cuối từ, giọng thì thầm.

- Mặc định Silero `0.5`; nền rất ồn thì `0.6–0.7` (**Reported**). HF s2s mặc định `--thresh 0.6` (**Observed** qua [CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md)), tức đã nghiêng về phía chống false trigger.
- `VADIterator` dùng **hysteresis**: ngưỡng tắt thấp hơn ngưỡng bật khoảng 0.15 (AI report, **Reported**). Tức khi đang ở trạng thái speech, chỉ khi `p < threshold − 0.15` mới tính là frame im lặng. Điều này ngăn việc `p` dao động quanh 0.5 làm đoạn nói bị băm vụn.
- Ngưỡng thích ứng: đo `p` trung bình và RMS trong 2–3 s đầu trước khi user nói; nếu `p` nền trung bình > 0.3 thì nâng threshold lên 0.65–0.7 và nâng luôn gate barge-in (**Reported**).

### `min_speech_duration_ms`

Speech phải kéo dài ít nhất chừng này mới được coi là một đoạn. Lọc tiếng click, ho, gõ phím, tiếng bật quạt. Cao quá thì mất các từ rất ngắn ("ừ", "dạ", "không", lệnh một âm tiết).

- Khởi điểm 250 ms (**Reported**). HF s2s mặc định `--min_speech_ms 384` (**Observed** trong code qua [CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md)); nên lưu ý đoạn ngắn hơn có thể không thành lượt (**Synthesis**, cần thử với tiếng Việt).
- HF s2s tách hai ngưỡng (**Observed**): lượt mới và barge-in luôn cần `min_speech_ms` (384), còn speech *nối tiếp* một lượt soft-ended chưa commit chỉ cần `min_speech_continuation_ms` (192). Thêm `short_segment_merge_ms` (mặc định 0, tắt) để giữ và ghép các mảnh ngắn hơn `min_speech_ms` thay vì bỏ, hữu ích khi `min_silence_ms` rất thấp. Đây là cách giữ "dạ/ừ" mà không hạ ngưỡng cho lượt mới.

### `min_silence_duration_ms`

Cần im lặng liên tục bao lâu thì đóng đoạn nói. Đây là tham số tác động trực tiếp nhất lên **độ trễ cảm nhận** và lên **tỷ lệ cắt ngang**:

- Nhỏ (64–150 ms): phản hồi nhanh, nhưng ngắt cả ở chỗ ngập ngừng/ranh giới cụm từ. Chỉ hợp lý nếu có tầng turn detection hoặc cơ chế speculative ở sau để sửa sai.
- Lớn (500–800 ms): ít cắt nhầm, nhưng cộng thẳng vào độ trễ mỗi lượt.
- Có Smart Turn phía sau: 200–300 ms (Pipecat khuyến nghị `stop_secs=0.2`, **Reported**). Không có semantic detector: blueprint đề xuất 500 ms (**Reported**); tài liệu thiết kế nới thành 500–800 ms, tune theo tốc độ nói (**Synthesis**).

### `speech_pad_ms` (và pre-roll)

Mở rộng mỗi đoạn về hai phía. Lý do: VAD thường kích hoạt **sau** khi âm bắt đầu và tắt **sau** khi âm đã kết thúc một lúc; phụ âm đầu (vô thanh như *t, k, ch, x*) và phụ âm cuối/dấu của âm tiết yếu năng lượng nên dễ bị cắt. Với tiếng Việt, mất phụ âm đầu hoặc đuôi âm tiết có thể đổi từ hoặc thanh điệu (Chương 5).

- Khởi điểm 100–200 ms (**Reported**); HF s2s mặc định 500 ms (**Observed**).
- **Pre-roll** là khái niệm liên quan nhưng khác: bạn phải **giữ ring buffer** vài trăm ms audio *trước* thời điểm VAD phát hiện speech để cắt đoạn gửi cho ASR bắt đầu sớm hơn điểm kích hoạt. Blueprint đề xuất 200 ms pre-roll (**Reported**, chưa đo); tài liệu thiết kế dùng 200–300 ms. Nếu chỉ "bắt đầu thu từ khi VAD bật" thì chắc chắn cắt mất đầu câu.
- **Kích thước ring buffer ≠ pre-roll** (**Synthesis**): nếu sự kiện START chỉ được xác nhận sau khi đủ `min_speech`, lúc xác nhận bạn đã ở sau điểm bắt đầu nói chừng `min_speech` + 1 frame. Ring buffer phải giữ ít nhất `min_speech + frame + pre-roll` (ví dụ 250 + 32 + 200 ≈ 480 ms), nếu không thì "pre-roll 200 ms" trên giấy vẫn cắt mất âm tiết đầu. Giữ dư (1 s) là rẻ.

### Tham số hay bị quên

- **Max speech duration:** giới hạn trên của một đoạn (ép cắt ở điểm im lặng dài nhất gần đó), cần cho ASR có giới hạn 30 s (Chương 11).
- **Timeout chờ người dùng:** user mở mic nhưng không nói, hoặc im quá lâu sau khi bot hỏi; logic này thuộc tầng hội thoại, bạn tự đặt (**Synthesis**).
- **Trần cho lượt speculative chưa được trả lời:** HF s2s có `--unanswered_reopen_ms 7000`. Đây **không** phải timeout "user không nói" mà là sanity cap cho một lượt đã soft-ended nhưng chưa được trả lời; không có tác dụng nếu nhỏ hơn `speculative_reopen_ms`, và bị kẹp theo `smart_turn_max_wait_ms` khi bật Smart Turn (**Observed**). README còn ghi cap này đếm theo thời gian audio đã stream, nên push-to-talk im lặng không gửi audio thì không làm nó chạy (**Reported**).
- **Max wait của turn detector:** trần tuyệt đối cho việc "đợi thêm" (§10.5).

### Bảng tóm tắt hiệu ứng

| Tham số | Tăng lên thì… | Triệu chứng khi chỉnh sai |
|---|---|---|
| `threshold` | Ít false trigger, dễ sót tiếng nhỏ | Thấp: bot bị kích hoạt bởi nhiễu. Cao: cụt đầu/cuối câu |
| `min_speech` | Bỏ tiếng ngắn | Cao: "dạ", "ừ" biến mất |
| `min_silence` | Chờ lâu hơn mới đóng đoạn | Thấp: cắt ngang khi user ngập ngừng. Cao: bot "đơ" |
| `speech_pad` | Giữ phụ âm đầu/cuối | Thấp: ASR nhận sai từ. Cao: kéo thêm nhiễu/echo vào ASR |

## 10.4 State machine speech/silence

Endpointing cài đặt tốt là một automaton nhỏ:

```text
            p ≥ on (tích lũy ≥ min_speech)
  SILENCE ───────────────────────────────► SPEECH
     ▲                                        │
     │   p < off liên tục ≥ min_silence       │ p ≥ off  → reset bộ đếm im lặng
     └────────────────────────────────────────┘
        phát sự kiện END (+ pad), trả đoạn [start − pre-roll, end + pad]
```

- `on = threshold`, `off = threshold − 0.15` (hysteresis).
- Trong SPEECH, mỗi frame `p ≥ off` làm **reset bộ đếm im lặng**. Do đó một nhịp ngắt nhỏ hơn `min_silence` không cắt đoạn.
- **Silero `VADIterator` làm hơi khác** (kiến thức chung về mã nguồn, kiểm tra theo phiên bản): nó ghi mốc `temp_end` ở frame đầu tiên `p < off`, và chỉ xoá mốc này khi gặp frame `p ≥ on` (không phải `≥ off`). Các frame nằm trong vùng `[off, on)` vẫn tính vào thời gian im. Hai cách cho kết quả khác nhau khi giọng nhỏ/đuôi câu có `p` lơ lửng quanh 0.4; nếu tự viết state machine, hãy chọn có chủ đích và test cả hai.
- Sự kiện START đến **muộn** `min_speech` so với điểm bắt đầu nói, sự kiện END đến muộn `min_silence` so với điểm thôi nói. Timestamp của đoạn thì được lùi về đúng chỗ (cộng pad), nhưng **thời điểm bạn biết** thì không; đó là lý do cần ring buffer (§10.3).
- Có thể thêm **smoothing** (trung bình trượt/median trên `p`) khi nhiễu nhiều, đổi lấy vài chục ms trễ.

### Ví dụ mô phỏng (Reproduced)

Chuỗi `p` mô phỏng với frame 32 ms: 20 frame im (0.05), 30 frame nói (0.9), **5 frame ngắt (0.2, tức 160 ms)**, 20 frame nói, 30 frame im. `threshold=0.5`, off=0.35, `min_speech=250`, `pad=100`:

| `min_silence` | Kết quả | Ý nghĩa |
|---|---|---|
| 250 ms | **1 đoạn** `[540 ms, 2500 ms]` | nhịp ngắt 160 ms được "bỏ qua", user nói liền mạch |
| 100 ms | **2 đoạn** `[540, 1700]`, `[1660, 2500]` | đoạn bị tách đôi, hai đoạn còn chồng lên nhau 40 ms do pad |

Bài học: cùng một giọng nói, chỉ đổi `min_silence` từ 250 xuống 100 ms đã băm câu thành hai lượt tiềm năng. Ngoài ra, ở cấu hình 250 ms, sự kiện END chỉ phát sau 8 frame im liên tục (256 ms) kể từ điểm thôi nói 2400 ms: `min_silence` cộng thẳng vào độ trễ. Trong pipeline, lượt đầu tiên có thể đã bị đưa vào ASR/LLM trước khi user nói xong. Ví dụ chỉ minh hoạ logic, không phải đo Silero thật.

## 10.5 Hai triết lý điều khiển lượt

### 10.5.1 Commit cứng sau timeout

Luồng: VAD báo im → (tuỳ chọn) semantic detector → nếu "complete" hoặc quá **timeout dự phòng** thì **commit**: chốt transcript, gọi LLM/TTS. Sau khi commit **không quay lại**; nếu user nói tiếp thì đó là barge-in vào lượt trả lời.

- Thiết kế gateway của AI report: VAD silence 200–300 ms → Smart Turn (10–65 ms) → fallback timeout **1.2–1.5 s** (**Reported**).
- Ưu: đơn giản, dễ suy luận, tài nguyên không lãng phí.
- Nhược: mọi lỗi "hết lượt sớm" đều thành **cắt ngang user** hoặc phải xử lý bằng barge-in; mọi lỗi "chờ lâu" đều thành độ trễ.

### 10.5.2 Speculative + revision

Luồng của turn tracker HF s2s (**Reported**, README; default đối chiếu **Observed** ở [CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md)): các trạng thái `LISTENING → SOFT_ENDED → ANSWERING → CLOSED`.

```text
LISTENING ──VAD im──► SOFT_ENDED ──turn detector complete──► ANSWERING ──TTS xong──► CLOSED
    ▲                     │  │                                   │
    │                     │  └─ incomplete: chờ 600 ms, trần 2 s ┘
    └──── user nói tiếp (speculative reopen ≤ 800 ms): mở lại thành revision mới,
          bỏ công việc chưa commit ◄─────────────────────────────┘
```

- Khi turn được đánh giá **complete**: chạy STT/LLM *ngay* (speculative), nhưng **chưa phát ra** trong một cửa sổ `speculative_reopen_ms` (800 ms mặc định). Nếu user nói tiếp trong cửa sổ này, kết quả speculative bị **huỷ**, lượt mở lại thành một revision mới.
- Khi **incomplete**: đợi `smart_turn_incomplete_delay_ms` (600 ms) rồi mới chạy STT/LLM; output vẫn bị gate bởi `smart_turn_max_wait_ms` (2 s).
- Khi user nói tiếp: lượt mở lại thành revision mới, audio tích luỹ được phát lại cho STT, công việc chưa commit bị bỏ. Turn tracker là owner duy nhất của quyết định reopen; VAD và Smart Turn chỉ cung cấp tín hiệu (**Reported**, [HF Speech-to-Speech](../wiki/speech-to-speech-pipeline.md)).
- Ưu: giấu được độ trễ (tính toán song song với việc chờ xác nhận), vẫn sửa được lỗi hết-lượt-sớm mà không thành "cắt ngang lời".
- Nhược: phức tạp hơn nhiều (cancellation, version/revision của lượt, chi phí tính toán lãng phí khi huỷ). Đây là chủ đề của Chương 17.

### 10.5.3 So sánh và cảnh báo tham số

| | Commit cứng | Speculative + revision |
|---|---|---|
| Khi VAD im | Đợi turn detector/timeout rồi commit | Bắt đầu việc ngay, giữ output |
| Sửa lỗi hết-lượt-sớm | Không (thành barge-in) | Có, trong cửa sổ reopen |
| Tham số điển hình | silence 200–300 ms, timeout 1.2–1.5 s | min_silence 64, reopen 800, max wait 2000 |
| Độ phức tạp | Thấp | Cao |

**Cảnh báo (Synthesis):** các con số ở hai cột *không cộng tác* được. `min_silence 64 ms` của HF s2s chỉ an toàn vì phía sau có speculative reopen; đặt 64 ms vào kiến trúc commit cứng sẽ cắt ngang user liên tục. Ngược lại 1.2–1.5 s là timeout *commit*, không phải trần *chờ speculative*. Hãy chọn một triết lý, rồi tune trọn bộ tham số của nó.

Khi **không có** semantic detector: 500–800 ms im lặng, tune theo tốc độ nói (**Synthesis**).

## 10.6 Semantic/prosodic end-of-utterance

### 10.6.1 Vì sao cần

Dữ liệu hội thoại cho thấy khoảng lặng giữa các lượt ở người thường chỉ vài trăm ms, còn pause *trong* lượt cũng có thể vài trăm ms hoặc hơn (do nghĩ, ngập ngừng). Hai phân phối chồng lấn, nên không có một ngưỡng thời gian nào tách được. (Kiến thức chung từ nghiên cứu turn-taking đa ngôn ngữ; wiki chưa có số liệu riêng cho hội thoại tiếng Việt.) Cần thêm **ngữ điệu** (hạ giọng cuối câu, kéo dài âm cuối, "à…", "thì…") và **nội dung** (câu còn dang dở, đang đọc số điện thoại).

### 10.6.2 Các hướng tiếp cận

| Hướng | Input | Ví dụ | Ghi chú |
|---|---|---|---|
| **Audio-native** (prosody) | PCM cuối lượt | **Smart Turn v3.2** | Không phụ thuộc chất lượng STT, hoạt động khi ASR sai |
| **Text-based** | Transcript đang có | LiveKit Turn Detector (text), Namo | Cần ASR trước; dùng được ngữ nghĩa, nhưng lỗi ASR lan sang |
| **Tích hợp trong ASR** | Chính audio streaming | `<EOU>` của Parakeet Realtime EOU 120M; semantic VAD heads của Audio8 ASR Infinite | Không cần thành phần riêng, nhưng gắn vào một model/ngôn ngữ |
| **Heuristic** | Chỉ thời gian | Silence timeout | Làm lớp dự phòng cho mọi cách còn lại |

### 10.6.3 Smart Turn v3.2 (Reported)

Theo [Smart Turn v3.2](../wiki/smart-turn.md):

- Whisper Tiny encoder + linear head, ~8M params, BSD-2, 23 ngôn ngữ **có tiếng Việt**; bản int8 CPU 8 MB, bản fp32 GPU 32 MB.
- **Input:** PCM 16 kHz mono, tối đa **8 s**, khuyến nghị toàn bộ lượt hiện tại của user. Dài hơn 8 s thì **cắt phần đầu**; ngắn hơn thì **zero-pad ở đầu** để audio nằm cuối vector. (Tức model quan tâm *phần cuối* của lượt.)
- **Output:** xác suất "complete" (kết thúc lượt); so với ngưỡng (HF s2s mặc định `--smart_turn_threshold 0.5`).
- **Vận hành:** chạy *sau* VAD khi đã im. Nếu user nói thêm trước khi suy luận xong, chạy lại trên **toàn bộ lượt gồm audio mới**, không chỉ đoạn mới. Không cần audio các lượt trước. Đoạn quá ngắn không phải input dự kiến.
- Latency: 10 ms trên một số CPU, dưới 100 ms trên đa số cloud, ~65 ms Pipecat Cloud (vendor).
- Giới hạn: đây là **classifier nhị phân** trên ngữ điệu; không hiểu nội dung nghiệp vụ (số thẻ, địa chỉ). Hướng text conditioning là việc tương lai của vendor.

Lưu ý khớp với §10.1: Smart Turn *không thay* VAD; nó cần VAD để biết *khi nào hỏi*.

### 10.6.4 Namo, LiveKit và `<EOU>`

- **LiveKit Turn Detector**: 14 ngôn ngữ, **không có tiếng Việt**, ~25 ms, license riêng (**Reported** qua AI report).
- **Namo (cộng đồng, `dangvansam`)**: có bản Việt (~200 MB), 4–36 ms, nhưng do tác giả tự đo, chưa có benchmark độc lập (**Reported**).
- **Parakeet Realtime EOU 120M v1**: ASR streaming tiếng Anh, phát token `<EOU>` cuối utterance, ví dụ `what is your name<EOU>`. EOU latency P50 160 ms, P90 280 ms, P95 320 ms, đo trên audio TTS tạo sinh có 3 s im lặng nối thêm (**Reported**). Model card cảnh báo hiệu năng thật thay đổi theo môi trường và giọng. Chỉ tiếng Anh nên không dùng được cho pipeline Việt (**Synthesis**).

## 10.7 Đọc ma trận nhầm lẫn: accuracy, FPR, FNR

### 10.7.1 Định nghĩa với turn detection

Lớp dương = "turn complete (đã hết lượt)".

|  | Thực tế: hết lượt | Thực tế: còn nói |
|---|---|---|
| **Dự đoán: hết lượt** | TP | **FP** (cắt ngang lời user) |
| **Dự đoán: còn nói** | **FN** (chờ quá lâu) | TN |

- `FPR = FP / (FP + TN)`: trong các lần user **còn nói** (đang pause), bao nhiêu % bị phán "hết lượt". → **cắt ngang**.
- `FNR = FN / (FN + TP)`: trong các lần user **thực sự xong**, bao nhiêu % bị phán "chưa xong". → **bot chờ lâu**.
- Precision, recall, F1 tóm tắt thêm nhưng không cho biết lỗi nào đau hơn. Hai lỗi **không đối xứng về trải nghiệm**: cắt ngang gây bực và mất thông tin, còn chờ lâu chỉ thêm độ trễ (và có timeout cứu).

### 10.7.2 Số liệu Smart Turn v3.2 (Reported, vendor)

| | Accuracy | FPR | FNR | Mẫu |
|---|---:|---:|---:|---:|
| Tổng 23 ngôn ngữ, GPU fp32 | 93.71% | 3.51% | 2.78% | 31.527 |
| Tổng, CPU int8 | 92.63% | 4.73% | 2.64% | 31.527 |
| **Tiếng Việt**, GPU fp32 | 82.47% | **9.56%** | 7.97% | 1.004 |
| **Tiếng Việt**, CPU int8 | 79.38% | 8.86% | **11.75%** | 1.004 |

Tiếng Việt là **ngôn ngữ yếu nhất** trong 23 ngôn ngữ ở cả hai bản. Vendor benchmark, chưa tái hiện; tập dữ liệu không nhất thiết giống hội thoại với bot của bạn.

### 10.7.3 Dịch sang trải nghiệm (Synthesis)

- FPR ≈ 9–10% nghĩa là khoảng **1 trên 10** lần user *dừng giữa chừng*, detector báo "hết lượt". Nó **không** nói rằng 1/10 *lượt* bị cắt: tỷ lệ này tính trên các khoảng pause "còn nói", nên số cắt thực tế/hội thoại phụ thuộc user hay ngập ngừng đến đâu và có bao nhiêu lần VAD đã báo im.
- FNR 11.75% ở CPU nghĩa là ~1/8 lần user thực sự xong mà bot vẫn chờ tới timeout (600 ms–2 s trong HF s2s). Đó là độ trễ cộng thêm đáng kể ở đúng những lượt đó.
- Bản CPU **giảm nhẹ FPR (8.86% vs 9.56%) nhưng tăng mạnh FNR (11.75% vs 7.97%)** so với GPU (recall 0.764 vs 0.840): cùng model nhưng *lỗi chiếm ưu thế khác nhau*. HF s2s tải checkpoint CPU mặc định, nên nếu có GPU rảnh, bản fp32 đáng thử.
- Ví dụ số học (Synthesis): giả sử một cuộc gọi có 10 khoảng pause "còn nói" mà VAD đã báo im ≥ `min_silence`. Với FPR 9.56%, kỳ vọng ~0.96 lần cắt nhầm mỗi cuộc, và xác suất ít nhất một lần = 1 − 0.9044¹⁰ ≈ 63% (giả định các pause độc lập và cùng phân phối với tập benchmark, điều thực tế hiếm đúng). Con số này chỉ minh hoạ độ nhạy với số pause; **không** phải đo.
- Vì thế **không bao giờ** coi detector là chân lý: luôn có (1) timeout dự phòng, (2) cơ chế sửa sai (speculative reopen hoặc barge-in tốt), (3) đo false-cutoff trên dữ liệu thật.

### 10.7.4 Đánh đổi bằng threshold

Tăng ngưỡng "complete" (ví dụ 0.5 → 0.7): FPR giảm, FNR tăng; giảm ngưỡng thì ngược lại. Vẽ **đường ROC/PR** trên dữ liệu nội bộ của bạn (ghi âm hội thoại thật, gán nhãn điểm kết thúc lượt) rồi chọn điểm vận hành theo chi phí lỗi. Quy tắc thực tế: với agent kiểu hỏi–đáp ngắn, chấp nhận FNR cao hơn FPR; với dictation/đọc số, ưu tiên FPR rất thấp.

Ngưỡng thay model: nếu tỷ lệ false-interruption tiếng Việt vẫn > 10%, thay sang Namo hoặc model fine-tune (**Reported**). Smart Turn có training script (`train.py`) và dữ liệu mở, nên fine-tune cho miền hẹp khả thi (**Reported**).

## 10.8 VAD trên kênh có echo: bot tự kích hoạt barge-in

Khi bot phát loa và mic thu lại, VAD nhìn thấy "tiếng người" (giọng bot hoặc nhiễu) và báo speech. Nếu logic là "user nói trong lúc bot nói = barge-in" thì bot **tự ngắt chính mình**. Đây là lỗi phổ biến nhất của prototype chạy loa ngoài.

Các lớp phòng thủ (theo [Voice-Agent Barge-in and Echo Handling](../wiki/voice-agent-barge-in-and-echo-handling.md), **Reported** trừ khi ghi khác):

1. **Echo cancellation** ở front-end (AEC của trình duyệt/WebRTC; Chương 7). Tốt nhất, nhưng không bao giờ triệt tuyệt đối.
2. **Half-duplex mềm:** khi bot đang nói, nâng threshold Silero lên **0.7** và yêu cầu **≥ 300–500 ms** speech liên tục mới tính là ngắt (server tham chiếu dùng `speech_ms >= 400`). Tuỳ chọn thêm: chạy nhanh ASR, yêu cầu ≥ 2 từ và không trùng câu đang phát. **Mâu thuẫn chưa giải:** một nguồn khác (ChatGPT answer) kích hoạt barge-in sau chỉ ~100–200 ms speech trên ngưỡng. Hai giá trị đều chưa đo, phục vụ hai ưu tiên khác nhau (nhạy vs chống ngắt nhầm); wiki không chọn bên.
3. **Ngưỡng thích ứng** theo nền ồn (xem §10.3).
4. **Speaker lock:** so cosine similarity embedding ECAPA/CAM++ của đoạn mới với embedding user (lấy từ lượt đầu, cập nhật dần); bỏ đoạn dưới ~0.5–0.6 (ngưỡng phải tự calibrate; Chương 14).
5. **Backchannel:** "ừ", "vâng", "ok" khi bot nói không phải ngắt.
6. **Denoise chỉ trên nhánh VAD/barge-in**, không trên input ASR (RNNoise/DeepFilterNet có thể làm méo âm cho ASR).
7. **Đo:** barge-in rate và false-interruption rate dưới nền ồn phát lại.

Chuỗi hành động khi ngắt hợp lệ (nối sang Chương 17): huỷ stream LLM, huỷ request TTS, xoá hàng đợi câu, gửi `{"type":"clear"}` để client flush AudioWorklet buffer, và chỉ lưu phần **thực sự đã phát** vào lịch sử (đánh dấu `[bị ngắt]`).

Điểm chốt: VAD dùng khi *bot im* và khi *bot nói* là hai bài toán khác nhau về ngưỡng và chi phí lỗi (**Synthesis**). Nên tách cấu hình, hoặc ít nhất hai bộ ngưỡng.

## 10.9 Chọn VAD, các mâu thuẫn cần nhớ

| VAD | Ghi chú |
|---|---|
| **Silero VAD v5/v6** (pick) | MIT, ONNX, ~2 MB, 512 samples @16 kHz. Vendor v6: "16% ít lỗi hơn trên dữ liệu nhiễu thực", "11% ít lỗi hơn đa miền"; điểm yếu: nhạc cụ giống giọng, giọng rất cao (**Reported**) |
| TEN VAD | Apache có điều kiện, hop 10/16 ms; vendor tuyên bố chính xác hơn Silero và WebRTC, RTF thấp hơn 32%, thư viện nhỏ hơn 86% |
| WebRTC VAD | GMM nhẹ, dùng làm baseline/gate rẻ |
| FireRed Stream-VAD, MarbleNet, PulseVAD | Có trong HF s2s / audio.cpp (Chương 22) |

**Mâu thuẫn chưa giải (không chọn bên):** TEN vs Silero. Vendor TEN nói tốt hơn; một benchmark cộng đồng nhỏ (NOVA-VAD với nhiễu UrbanSound8K) cho Silero F1 91.9% so với TEN 69.2%. Khuyến nghị: **đo trên dữ liệu của bạn**, giữ Silero mặc định, cân nhắc TEN khi cần frame 10 ms (**Reported**).

**Mâu thuẫn số liệu Smart Turn:** AI report ghi 81.27% / FP 14.84% / FN 3.88%, khác capture v3.2 (82.47%/9.56%/7.97% GPU). Chưa rõ report mô tả bản nào; capture v3.2 là nguồn gốc, nên dùng số capture (**Reported**, xem [Turn Detection Models](../wiki/turn-detection-models.md)).

## 10.10 Hai vai trò khác nhau của VAD trong pipeline

Cùng tên "VAD" nhưng hai mục đích khác hẳn:

| | VAD làm **filter cho ASR** | VAD **điều khiển lượt nói** |
|---|---|---|
| Ví dụ | `vad_filter=True` của faster-whisper (tuỳ chọn `vad_parameters`), VAD chunking ≤ 30 s của Parakeet Redux/server | `VADIterator` + turn tracker |
| Mục tiêu | Loại im lặng/nhiễu để ASR không hallucinate, và cắt audio dài | Biết khi nào user bắt đầu/ngừng, khi nào bot được trả lời |
| Chế độ | Thường offline/batch, nhìn được tương lai | Online, nhân quả, từng chunk |
| Tham số | Thiên về **bảo thủ** (không cắt mất tiếng): default faster-whisper chỉ bỏ im lặng > 2 s; README ví dụ hạ xuống `min_silence_duration_ms=500` | Thiên về **độ trễ** (200–300 ms) |
| Sai thì | ASR hallucinate, mất từ | Cắt ngang, bot đơ, tự ngắt |

Thiết kế thường dùng **hai lớp**: VAD streaming điều khiển lượt, rồi VAD filter lớp thứ hai ở ASR (§5.5 tài liệu thiết kế: `vad_filter=True, min_silence_duration_ms=500`, cùng `no_speech_threshold=0.6`, `log_prob_threshold=-1.0`, `compression_ratio_threshold=2.4` để chống hallucination của Whisper; **Reported**). Đừng dùng chung tham số cho hai lớp, và đừng coi VAD filter là bằng chứng "đã có endpointing".

## 10.11 Ngân sách độ trễ

Thành phần của "độ trễ kết thúc lượt" (từ lúc user thôi nói đến lúc có thể bắt đầu phản hồi), kiến trúc commit cứng (**Reported/Synthesis**):

```text
frame VAD (32 ms) + min_silence (200–300 ms) + Smart Turn (10–65 ms)
   + [nếu incomplete: chờ thêm đến timeout 1.2–1.5 s]
   → rồi mới tới ASR final / LLM TTFT / TTS first audio (Chương 20)
```

- Trường hợp tốt: ~250–400 ms trước khi ASR/LLM chạy.
- Trường hợp FNR: thêm tới timeout (hơn 1 s).
- Với `<EOU>` trong ASR streaming: không cộng riêng thành phần turn detection, nhưng EOU latency P50 160 ms – P95 320 ms (điều kiện thử nghiệm xem §10.6.4).
- Speculative giảm độ trễ cảm nhận bằng cách chạy ASR/LLM song song với cửa sổ chờ.

Đo bằng cách ghi **timestamp theo sự kiện**: `t_user_stop` (nhãn tay hoặc từ audio gốc), `t_vad_end`, `t_turn_complete`, `t_asr_final`, `t_llm_first_token`, `t_tts_first_audio`. Không đo thì không tune được.

## 10.12 Quy trình tune và kiểm thử

1. **Thu dữ liệu:** 30–60 phút hội thoại thật (đúng micro, đúng môi trường, đúng giọng vùng miền), có cả nhiễu nền, loa ngoài, pause dài, đọc số.
2. **Gán nhãn:** `speech_start/end` và `turn_end` (người gán, hoặc forced alignment sơ bộ rồi sửa tay).
3. **Tune VAD trước** (threshold, min_speech, pad) để recall tiếng nói cao, loại false trigger.
4. **Tune endpoint** (min_silence) và turn detector (ngưỡng complete), vẽ ROC/PR.
5. **Đo chỉ số lượt:** false-cutoff rate (cắt khi user chưa xong), late-response rate/độ trễ p50/p95, barge-in rate hợp lệ, false barge-in rate.
6. **Test điều kiện xấu:** nền ồn, phát lại giọng bot qua loa, giọng nhỏ, user nói dặt dẹo, câu rất ngắn ("dạ"), đọc dãy số.
7. **Regression:** lưu bộ audio + kết quả mong đợi; chạy lại mỗi khi đổi model, ngưỡng hoặc phiên bản VAD (v5→v6 là "drop-in" nhưng hành vi đổi).

## 10.13 Lỗi thường gặp (checklist)

- [ ] Đưa PCM int16 chưa chuẩn hoá hoặc sai sample rate vào Silero.
- [ ] Dùng chung một state VAD cho nhiều session, hoặc quên `reset_states()`.
- [ ] Bỏ frame/chunk size khác 512 samples (v5+).
- [ ] Không có pre-roll, mất phụ âm đầu câu.
- [ ] `min_silence` quá thấp mà không có tầng sửa sai.
- [ ] Không có timeout dự phòng cho semantic detector.
- [ ] Để nguyên ngưỡng khi bot đang nói (tự ngắt vì echo).
- [ ] Chép tham số từ hai kiến trúc khác nhau vào cùng cấu hình.
- [ ] Chạy Smart Turn chỉ trên đoạn mới thay vì toàn bộ lượt hiện tại.
- [ ] Tin số liệu vendor mà không đo trên dữ liệu tiếng Việt thật của mình.
- [ ] Nhầm `vad_filter` của ASR với endpointing.

## Đáp án tự kiểm tra

**Q1.** Input: tensor `float32` mono chuẩn hoá `[-1, 1]`, 16 kHz (hoặc 8 kHz), chunk cố định 512 (hoặc 256) samples từ v5. Output: xác suất speech mỗi chunk; các wrapper (`VADIterator`, `get_speech_timestamps`) biến thành sự kiện start/end. State ẩn hồi quy nằm **trong instance model/iterator, per-session**; phải `reset_states()` khi hết lượt và không bỏ chunk.

**Q2.** `threshold`: độ nhạy (cao = ít false trigger, dễ sót; có hysteresis ~0.15 cho ngưỡng tắt). `min_speech_duration_ms`: loại tiếng ngắn (ho, click), nhưng cao quá mất "dạ/ừ". `min_silence_duration_ms`: thời gian im cần để đóng đoạn, đánh đổi trực tiếp độ trễ và cắt ngang. `speech_pad_ms`: nới hai đầu để giữ phụ âm đầu/cuối, quan trọng với tiếng Việt; khác với pre-roll (ring buffer trước điểm kích hoạt, phải đủ dài để phủ cả độ trễ xác nhận `min_speech`). Lưu ý `VADIterator` không có `min_speech_duration_ms`; tham số đó chỉ có ở `get_speech_timestamps`.

**Q3.** VAD: âm học, "có tiếng nói không", từng frame. Turn detection: "user nói xong chưa", dựa ngữ điệu/nội dung, chạy sau khi VAD im. FPR 9–10% (tiếng Việt, Smart Turn v3.2): ~1/10 lần user dừng giữa chừng bị phán hết lượt, tức bị cắt ngang. FNR 8–12%: bot chờ thêm ở ~1/8–1/12 lần user thực sự xong. Do đó cần timeout dự phòng, cơ chế sửa sai và đo trên dữ liệu thật.

**Q4.** Vì chúng thuộc hai triết lý điều khiển khác nhau. `min_silence 64 ms` của HF s2s chỉ ổn nhờ speculative reopen 800 ms và max wait 2 s sau nó. Trong thiết kế commit cứng, 64 ms sẽ cắt ngang user liên tục; ngược lại 1.2–1.5 s là timeout commit, không tương đương trần chờ của speculative.

**Q5.** Vì pause trong lượt và khoảng lặng giữa các lượt chồng lấn; giảm `min_silence` chỉ đổi FNR lấy FPR. Mô phỏng §10.4: 250 → 100 ms làm một lượt thành hai đoạn. Phải có tầng turn detector hoặc speculative/revision đi kèm.

**Q6.** Giọng bot vọng qua mic (echo) hoặc tiếng ồn bị VAD coi là speech. Xử lý bằng AEC, nâng threshold (≈0.7) và duration gate (≥300–500 ms) khi bot đang nói, speaker lock, bỏ qua backchannel, denoise nhánh VAD, và đo false-interruption rate.

## Hạn chế và phạm vi bao phủ

- Chưa chạy Silero VAD, Smart Turn, Namo, TEN hay Parakeet EOU; mọi số liệu model là **Reported** qua wiki, chưa tái hiện. Tham số mặc định HF s2s là **Observed** theo wiki CLI, không chạy lại.
- Chữ ký API `VADIterator`/`get_speech_timestamps`, default của chúng (§10.2.2) và chi tiết hysteresis/`temp_end` (§10.4) là kiến thức chung về mã nguồn Silero, không có trong `raw/`; hãy kiểm tra theo phiên bản bạn cài.
- Namo, LiveKit, TEN chỉ có thông tin thứ cấp (AI report); chưa có benchmark độc lập cho tiếng Việt.
- Mô phỏng §10.4 dùng xác suất giả lập, không phải đo Silero thật.
- Các số "1/10", "63%" ở §10.7.3 là suy luận minh hoạ (**Synthesis**).
- Số liệu có hạn dùng ngắn (`stale_after` của wiki: 2027-10); kiểm tra lại phiên bản model.
- Chương này chưa đi sâu vào full-duplex/E2E (model tự quyết định lượt; Chương 15) và cancellation chi tiết (Chương 17).

## Phụ lục chương

### Script mô phỏng (`/tmp/vad_sim.py`, đã chạy)

```python
FR = 32  # ms mỗi frame
def run(probs, on=0.5, off=0.35, min_sil=250, min_sp=250, pad=100):
    st, sp, sil, out, start = "S", 0, 0, [], None
    for i, p in enumerate(probs):
        t = i * FR
        if st == "S":
            if p >= on:
                if sp == 0: start = t
                sp += FR
                if sp >= min_sp: st, sil = "V", 0
            else:
                sp = 0
        else:
            if p < off:
                sil += FR
                if sil >= min_sil:
                    out.append((max(0, start - pad), t - sil + pad + FR))
                    st, sp = "S", 0
            else:
                sil = 0
    return out

probs = [0.05]*20 + [0.9]*30 + [0.2]*5 + [0.9]*20 + [0.1]*30
print(run(probs))                 # [(540, 2500)]
print(run(probs, min_sil=100))    # [(540, 1700), (1660, 2500)]
```

### Liên kết sang chương khác

- Chương 6–7: capture, ring buffer, AEC, denoise (nền của §10.3, §10.8).
- Chương 11: ASR streaming, `<EOU>`, VAD chunking cho ASR dài.
- Chương 14: speaker embedding cho speaker lock.
- Chương 15, 17: E2E full-duplex, state machine lượt, cancellation, barge-in.
- Chương 20–21: đo độ trễ và false-cutoff.
