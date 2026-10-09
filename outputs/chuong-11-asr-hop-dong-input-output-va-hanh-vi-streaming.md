# Chương 11. ASR: hợp đồng input/output và hành vi streaming 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần IV.
> **Chương trước:** [Chương 10. VAD, endpointing và turn detection](chuong-10-vad-endpointing-va-turn-detection.md). **Chương tiếp theo:** Chương 12. LLM trong vòng hội thoại nói.
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.4 (ASR), §6, §7.2.
> **Cơ sở:** phần lý thuyết (đặc tả contract, streaming, WER/RTF, revision/stable prefix) là kiến thức giáo trình và kỹ thuật chung. Số liệu và tham số cụ thể lấy từ wiki, gắn nhãn bằng chứng: [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md), [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md), [Nemotron 3.5 ASR](../wiki/nemotron-3.5-asr-streaming-0.6b.md), [Parakeet Realtime EOU 120M v1](../wiki/parakeet-realtime-eou-120m-v1.md), [Faster-Whisper](../wiki/faster-whisper.md), [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md), [WhisperLiveKit](../wiki/whisperlivekit.md), [Community Usable STT](../wiki/community-usable-stt-voice-agents.md). Số liệu wiki là **Reported** (chưa chạy lại model nào). Ví dụ stable-prefix ở §11.5 chạy bằng script Python thuần (**Reproduced**, script ở "Phụ lục chương"). Suy luận từ số liệu sang trải nghiệm là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Mô tả ASR như một **thành phần có contract**: audio vào có định dạng gì, kết quả ra gồm những trường nào, khi nào ra, tin được tới đâu.
2. Phân biệt **partial / stable prefix / final**, và biết lúc nào được hành động trên text.
3. Phân loại ba nghĩa của "realtime": **native streaming**, **buffered/policy**, **turn-final**; không nhầm RTF < 1 với "có text sớm".
4. Hiểu cơ chế revision, stable prefix, LocalAgreement, two-pass và cách reconcile.
5. Nhận diện và chặn **hallucination** (đặc biệt Whisper trên im lặng, nhạc, nhiễu).
6. Dùng đúng metric (WER/CER, RTF, RTFx, first partial, first stable text, endpoint→final) và tránh các bẫy benchmark.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Input chuẩn của ASR là gì? Output nên gồm những trường nào?
- Q2. Partial, stable prefix và final khác nhau thế nào? Vì sao không gọi tool/ghi CRM trên partial?
- Q3. Ba nghĩa của "realtime" là gì? RTF < 1 có nghĩa là "có text sớm" không?
- Q4. Vì sao phải ép `language="vi"`? Rủi ro của auto LangID?
- Q5. Whisper hallucinate trong điều kiện nào, lọc bằng tín hiệu nào?
- Q6. Vì sao không so trực tiếp WER 5.55 (Qwen3-ASR, FLEURS-vi) với 12.29 (Nemotron 3.5, FLEURS-vi, chunk 320 ms)?
- Q7. Confidence của ASR dùng thế nào cho an toàn khi có số điện thoại/số tiền?

---

## 11.1 ASR như một thành phần có contract

Trong pipeline cascade, ASR là **hàm từ luồng audio sang luồng text kèm metadata**. Viết contract rõ giúp thay model (Whisper → Nemotron → Qwen3-ASR) mà không sửa phần còn lại.

### 11.1.1 Input

| Thuộc tính | Giá trị chuẩn | Ghi chú |
|---|---|---|
| Sample rate | **16 kHz** | Đa số model speech train ở 16 kHz; audio 8 kHz (điện thoại) cần upsample *và* biết rằng băng thông thật vẫn chỉ ~4 kHz (Chương 2–3) |
| Kênh | **mono** | Stereo phải downmix; không đưa 2 kênh vào model mono |
| Kiểu mẫu | `float32` trong `[-1, 1]` (hoặc `int16` nếu API ghi rõ) | Sai kiểu/chuẩn hoá là bug phổ biến: tín hiệu quá nhỏ ×32768 hoặc bị clip |
| Độ dài tối thiểu | tuỳ model | Parakeet Realtime EOU yêu cầu ≥ 160 ms (**Reported**)[^eou] |
| Độ dài tối đa | tuỳ model | Whisper xử lý cửa sổ 30 s; Nemotron bị chặn bởi bộ nhớ GPU (**Reported**)[^nemotron] |
| Ngôn ngữ | chỉ định tường minh nếu biết | Nemotron nhận language ID dạng `vi-VN` (**Reported**)[^nemotron]; Whisper dùng `language="vi"` |

Hai kiểu giao input:

- **Offline/turn-final:** truyền cả đoạn (đã cắt bằng VAD, Chương 10) → nhận kết quả sau.
- **Streaming:** truyền từng chunk (vd 80–1120 ms) → nhận chuỗi sự kiện. Chunk phía **client** (kích thước mỗi lần gửi) khác chunk phía **model** (kích thước mà encoder xử lý); đừng gộp hai khái niệm.

### 11.1.2 Output

Một contract output đầy đủ (đề xuất; không model nào cung cấp đủ tất cả):

```text
TranscriptEvent {
  session_id, utterance_id, revision_id    # định danh để reconcile
  kind:   "partial" | "stable" | "final"
  text:   str                              # đã (hoặc chưa) punctuation/ITN
  segments: [ { start, end, text,
                avg_logprob?, no_speech_prob?, compression_ratio? } ]
  words?: [ { word, start, end, prob? } ] # nếu model hỗ trợ
  language: "vi" (ép hoặc detect) , language_probability?
  audio_range: [t0, t1]                    # đoạn audio đã tiêu thụ
  eou?: bool                               # nếu ASR phát <EOU>
  confidence: float | "unknown"
}
```

Thực tế:

- **Faster-Whisper** trả `(segments, info)`; `info.language`, `info.language_probability`; mỗi segment có `start`, `end`, `text`, và với `word_timestamps=True` có `segment.words` (**Reported**)[^fw]. Các trường `avg_logprob`, `no_speech_prob`, `compression_ratio` có trên segment (theo các tham số lọc ở §11.7; **Reported**)[^hallu].
- **Nemotron 3.5** trả chuỗi text một chiều, có punctuation và viết hoa; khi dùng auto-detect, nó gắn thẻ `<xx-XX>` sau dấu câu cuối, và có tuỳ chọn strip (`strip_lang_tags` trong NeMo, `skip_special_tokens` trong Transformers) (**Reported**)[^nemotron].
- **Parakeet Realtime EOU** có thể phát token `<EOU>` nằm ngay trong luồng text (ví dụ `what is your name<EOU>`), và có thể trả chuỗi rỗng khi không có speech (**Reported**)[^eou].

Hệ quả thiết kế: lớp **adapter** phải chuẩn hoá mọi model về một schema nội bộ, điền `"unknown"` cho trường model không có (xem §11.9), và **lột** token đặc biệt (`<EOU>`, `<vi-VN>`) trước khi đưa text cho LLM.

### 11.1.3 Ép ngôn ngữ và rủi ro auto LangID

- Với câu ngắn, ồn, hoặc có từ mượn, auto-detect hay đoán sai ngôn ngữ, kéo theo output sai hoàn toàn (không phải sai vài từ). Báo cáo của wiki yêu cầu `language="vi"` là bắt buộc cho Whisper trên turn ngắn ồn (**Reported**)[^hallu].
- WhisperLiveKit ghi nhận với Qwen3-streaming: phải truyền `--language` tường minh vì auto-detect đổi ngôn ngữ giữa chừng trên audio có giọng vùng miền (**Reported**)[^wlk].
- Nếu sản phẩm có code-switch (Việt–Anh), ép `vi` thường vẫn phiên âm được từ tiếng Anh phổ biến nhưng có thể "Việt hoá" chính tả; kiểm trên dữ liệu thật (**Synthesis**). Cách khác là model có LangID tag (Nemotron auto) và xử lý tag ở adapter.
- Quy tắc: **biết ngôn ngữ thì ép; chỉ detect khi thật sự phải**, và log `language_probability`.

---

## 11.2 Streaming: partial, stable prefix, final

### 11.2.1 Ba loại kết quả

| Loại | Đặc điểm | Được phép làm gì |
|---|---|---|
| **Partial** (interim) | Giả thuyết hiện tại, có thể bị **sửa/xoá** ở lần cập nhật sau | Hiển thị UI, **prefetch** (LLM warm-up, RAG), tham gia quyết định lượt |
| **Stable prefix** | Phần đầu của partial mà policy tin là sẽ không đổi nữa | Có thể xử lý downstream theo lô nhỏ nếu hành động đảo ngược được |
| **Final** | Kết quả cuối của một utterance/turn, sau endpoint | Nguồn chính để LLM, tool call, lưu hội thoại |

Lý do không hành động trên partial: ASR dùng ngữ cảnh *về sau* để sửa quyết định *về trước*. Ví dụ "tôi muốn **đạt** vé" → "tôi muốn **đặt** vé". Một cộng đồng voice-agent báo cáo: đo "bao lâu một đoạn text sống sót trước khi bị sửa" dự đoán cảm giác "nhanh" tốt hơn WER; và các thực thể hành động (ngày, số điện thoại, "đừng huỷ") nên đợi final hoặc read-back (**Reported**, anecdote chưa kiểm chứng)[^usable].

### 11.2.2 Các mốc thời gian

```text
user nói:   |==== "tôi muốn đặt vé đi Đà Nẵng" ====|  im lặng ...
mic time:   t0                                    t_stop    t_endpoint
ASR emit:       p1  p2  p3  p4  p5 ...(partials)         final
                 ▲                  ▲                     ▲
          first partial     first stable text     endpoint→final
```

- **First partial:** text đầu tiên xuất hiện (có thể rác).
- **First stable text:** text đầu tiên mà policy cam kết không sửa. Đây mới là mốc "có text dùng được" (**Synthesis**, ý tưởng trùng với khuyến nghị của wiki Usable STT)[^usable].
- **Word lag:** khoảng cách giữa lúc từ được nói và lúc từ vào stable.
- **Endpoint→final:** từ lúc hệ thống quyết định hết lượt đến lúc có final.

Đo từng mốc **riêng**; một con số "latency" duy nhất sẽ che mất nguồn chậm.

### 11.2.3 Revision: mô hình dữ liệu để xử lý sửa

Mỗi event mang `revision_id` tăng dần cho cùng `utterance_id`. Consumer giữ **bản mới nhất thắng**. Với thao tác hạ nguồn:

- **Idempotent/đảo ngược được** (hiển thị, prefetch, tính embedding): làm trên partial được.
- **Không đảo ngược** (gọi API đặt vé, ghi CRM, trả lời bằng TTS): chỉ làm trên final hoặc stable đã qua ngưỡng.
- **Sửa sau commit** ("không, 4 chứ không phải 5"): đây là bài toán của state machine hội thoại, không phải của ASR; cộng đồng gọi là "architecture problem masquerading as an STT problem" (**Reported**)[^usable]. Phải có đường cập nhật giá trị cũ trong mọi pending tool call, field, summary.

---

## 11.3 Taxonomy "realtime": ba nghĩa khác nhau

Theo wiki lựa chọn ASR tiếng Việt, "realtime" gồm ba lớp không đồng nhất (**Synthesis**)[^sel]:

### 11.3.1 Native / stateful streaming (cache-aware)

- Encoder được **huấn luyện nhân quả có giới hạn lookahead** và giữ **cache** cho self-attention và convolution; mỗi chunk mới chỉ tính phần audio mới, tái dùng ngữ cảnh cũ, không tính lại phần chồng lấn (**Reported**, Nemotron)[^nemotron].
- Ví dụ: Nemotron 3.5 ASR (FastConformer-RNNT, 600M, `vi-VN`, chunk chọn lúc suy luận 80/160/320/560/1120 ms)[^nemotron]; Parakeet Realtime EOU (chỉ tiếng Anh)[^eou].
- Ưu: độ trễ ổn định, chi phí tuyến tính theo độ dài audio, nhiều phiên đồng thời. Nhược: model bị ràng vào kiến trúc và ngôn ngữ/domain đã train.
- Đánh đổi chunk–chính xác (FLEURS-vi, LangID cung cấp, **Reported**)[^sel]:

| Chunk | 80 ms | 160 ms | 320 ms | 560 ms | 1120 ms |
|---|---|---|---|---|---|
| WER % | 13.41 | 12.87 | 12.29 | 11.78 | 11.18 |

Chunk lớn hơn → WER thấp hơn nhưng first partial muộn hơn; đây là quy luật chung (nhiều lookahead = nhiều ngữ cảnh tương lai). Đừng cộng nhầm: **chunk size là cận dưới của latency, không phải latency**.

### 11.3.2 Buffered / policy streaming

- Model gốc là **offline** (nhìn cả cửa sổ audio). Hệ thống gửi audio dồn lại (có thể lặp lại phần cũ), chạy decode nhiều lần, và dùng **policy** để quyết định phần nào commit: LocalAgreement, AlignAtt/SimulStreaming, "giữ N chunk cuối unfixed", v.v.
- Ví dụ: Whisper trong WhisperLiveKit (SimulStreaming mặc định hoặc LocalAgreement)[^wlk]; Qwen3-ASR: paper dùng chunk 2 s, fallback 5 token, giữ bốn chunk cuối chưa cố định; WER trung bình 1.7B tăng 2.69→3.33 và 0.6B 3.48→4.40, đo trên LibriSpeech/FLEURS-en/zh, **không** có tiếng Việt (**Reported**)[^sel].
- WebSocket/SSE chỉ là **transport**; chúng không biến checkpoint offline thành causal encoder (**Synthesis**)[^sel].
- Chi phí: tính lại ngữ cảnh (WLK Qwen recompute cửa sổ mặc định 12 s) và độ trễ commit (**Reported**)[^wlk].

### 11.3.3 Turn-final

- Chỉ chạy sau khi endpoint (Chương 10), decode cả đoạn. Dùng cho Whisper large-v3-turbo, PhoWhisper, ChunkFormer large, Cohere Transcribe, Gipformer (card không nêu streaming) (**Reported/Synthesis**)[^sel].
- Latency cảm nhận = chờ endpoint + thời gian decode final. Không có partial → không prefetch được, nhưng đơn giản và thường chính xác hơn trên cùng model.

### 11.3.4 RTF < 1 không có nghĩa là "có text sớm"

- **RTF** (real-time factor) = thời gian xử lý / thời gian audio. RTF = 0.3 nghĩa là xử lý 10 s audio mất 3 s. **RTFx** = nghịch đảo (3.3×).
- RTF < 1 chỉ nói rằng hệ thống **theo kịp** luồng audio về lâu dài (không dồn hàng đợi). Nó **không** nói first text xuất hiện sau bao lâu.
- Ví dụ: Whisper offline có RTF 0.3 nhưng chỉ chạy sau endpoint; 10 s user nói + 1.2 s timeout + 3 s decode = 4+ s sau khi người dùng ngừng, dù RTF "tốt". Ngược lại model streaming RTF 0.8 vẫn cho first partial sớm.
- Latency usable text gồm: chunk accumulation + lookahead + compute + scheduling + transport + commit policy; và endpoint→final khác first stable text (**Synthesis**)[^sel][^usable].
- Nhiều phiên đồng thời cũng đổi bức tranh: paper Qwen3-ASR báo TTFT 0.6B ở concurrency 1 là 92/105 ms (avg/P95) nhưng 3210/6195 ms ở concurrency 128 (vLLM, input ASR ~2 phút có sẵn). Đây là hiệu quả request/decode, **không** phải latency nhận audio từ mic; không được ghép 92 ms với throughput 2000 audio-s/s như cùng một operating point (**Reported**; diễn giải **Synthesis**)[^sel].

---

## 11.4 Hai bảng tra nhanh: kiến trúc và vai trò

| Họ kiến trúc | Ví dụ | Streaming thế nào | Rủi ro cần đo |
|---|---|---|---|
| Cache-aware acoustic RNNT | Nemotron, ChunkFormer (streaming-trained) | Native, cache | Ngôn ngữ/domain; giấy phép checkpoint streaming |
| Encoder + LLM decoder | Qwen3-ASR | Buffered/rollback | Tài nguyên, độ trễ commit, "instruction hallucination" |
| Encoder-decoder seq2seq | Whisper, PhoWhisper | Policy trên offline model | Recompute, sửa partial, hallucination im lặng |
| Compact specialized | ZipFormer 30M, Gipformer 68M | Chưa rõ | Size không bảo đảm streaming |

(**Synthesis** từ tài liệu model trong wiki)[^sel]. Khuyến nghị tham khảo cho tiếng Việt, **chưa benchmark triển khai**: Nemotron 3.5 khi cần partial sớm; Qwen3-ASR 1.7B khi ưu tiên chất lượng và chịu được buffering; Whisper large-v3-turbo làm baseline turn-final; hai-pass (native partial + final-pass bằng Qwen3-ASR 1.7B hoặc ChunkFormer RNNT large) là thiết kế đề xuất, tăng compute và phải reconcile transcript (**Synthesis**)[^sel].

---

## 11.5 Stable prefix và LocalAgreement

### 11.5.1 Ý tưởng

Mỗi lần có audio mới, model buffered cho ra một hypothesis `H_t` cho cả buffer. Hypothesis thay đổi nhưng phần đầu thường ổn định. **LocalAgreement-k**: commit **tiền tố chung dài nhất** của `k` hypothesis liên tiếp. Chọn `k=2` là phổ biến: nhanh, cần hai lần đồng ý.

### 11.5.2 Ví dụ chạy được (**Reproduced**)

Chuỗi hypothesis mô phỏng tăng dần (không có revision) và `k=2` cho kết quả (số từ đã commit sau mỗi bước):

```text
t0: committed=0  ''
t1: committed=1  'tôi'
t2: committed=3  'tôi muốn đặt'
t3: committed=5  'tôi muốn đặt vé đi'
t4: committed=6  'tôi muốn đặt vé đi đà'
t5: committed=7  'tôi muốn đặt vé đi đà nẵng'
t6: committed=9  'tôi muốn đặt vé đi đà nẵng ngày mười'
```

Nhận xét:

- Commit luôn **chậm hơn partial một nhịp** (từ cuối của `H_t` chỉ vào stable khi `H_{t+1}` đồng ý). Đây là cái giá của độ ổn định: **word lag ≥ một chu kỳ cập nhật**.
- Từ "mười lăm" ở cuối ngày chưa commit khi user vừa dứt lời; chờ final. Do đó **con số, tên, ngày** nằm cuối câu thường là phần chưa stable khi endpoint xảy ra.
- Khi model sửa tiền tố đã commit (không thể xảy ra với policy đúng, nhưng xảy ra với policy rút gọn như "commit sau N token"), phải có kênh `revision` để sửa UI/log.

### 11.5.3 Các policy khác

- **AlignAtt/SimulStreaming** (Whisper): dùng attention alignment quyết định đã nghe đủ audio để phát token hay chưa (WLK mặc định; **Reported**)[^wlk].
- **Giữ N chunk cuối unfixed** (Qwen paper): chỉ cố định phần cũ hơn N chunk.
- **Native RNNT**: token phát khi encoder/joint quyết định, thường stable hơn vì nhân quả, nhưng vẫn có sửa nếu có decoding beam hoặc LM.

---

## 11.6 Two-pass: partial + final và cách reconcile

Thiết kế: pass 1 là streaming nhanh (Nemotron) cho partial/endpoint; pass 2 chạy trên **toàn bộ đoạn audio của lượt** bằng model chính xác hơn (Qwen3-ASR 1.7B, ChunkFormer large, Whisper turbo) → final (**Synthesis**)[^sel].

Quy tắc reconcile:

1. **Final của pass 2 thay hoàn toàn** partial của pass 1 cho cùng `utterance_id`; không merge từ.
2. Mọi thứ đã làm trên partial phải **idempotent** hoặc có bước kiểm: nếu final khác partial ở *span hành động* (số, tên, phủ định), huỷ prefetch và chạy lại.
3. Ghi **version** (`asr_pass`, `model_id`) vào log để debug.
4. Cấm duplicate: không nối final vào cuối partial đã hiển thị; thay thế theo `utterance_id`.
5. Không coi final là ground truth: các thực thể quan trọng cần confidence hoặc câu hỏi xác nhận (§11.9).
6. Chi phí: pass 2 tăng latency endpoint→final; chỉ chạy khi lượt đủ quan trọng hoặc khi pass 1 chênh/độ tin cậy thấp (**Synthesis**).

---

## 11.7 Hallucination

### 11.7.1 Nó là gì

Với model sinh (Whisper, ASR dựa LLM), decoder là mô hình ngôn ngữ có điều kiện: nếu audio không mang đủ thông tin, nó vẫn **viết ra thứ có xác suất cao theo ngôn ngữ** thay vì chuỗi rỗng. Kết quả thường gặp: câu lặp, câu ma ("Hãy subscribe cho kênh La La School Để không bỏ lỡ những video hấp dẫn", "Ghiền Mì Gõ"), vốn là dữ liệu huấn luyện từ phụ đề YouTube (**Reported**, whisperX #1086, whisper.cpp #1051 qua báo cáo trong wiki)[^hallu].

### 11.7.2 Điều kiện kích hoạt

| Điều kiện | Cơ chế |
|---|---|
| Im lặng dài, hoặc tiếng ồn/nhạc nền | Không có tín hiệu, decoder dùng prior |
| Cắt audio sát/lẫn tiếng nền cuối đoạn | Cửa sổ 30 s Whisper bị pad, model "điền" |
| `initial_prompt`/hotwords chứa câu giống outro | Prior bị kéo về cụm đó (không bao giờ đưa "cảm ơn đã xem" vào prompt) |
| `condition_on_previous_text=True` | Lỗi lặp lan sang đoạn sau |
| Auto LangID sai | Sinh text sai ngôn ngữ |
| Audio rất ngắn (<400 ms) | Dễ sinh 1–2 từ vô nghĩa |

### 11.7.3 Ba tầng phòng thủ

**Tầng 1: tránh đưa rác vào ASR.** VAD gating (Chương 10), `vad_filter=True` với `min_silence_duration_ms=500` làm lớp phụ (mặc định faster-whisper chỉ cắt im lặng > 2 s), cùng AEC/denoise nếu cần (**Reported**)[^hallu].

**Tầng 2: cấu hình decode** cho từng turn đã cắt (**Reported**)[^hallu]:

```python
segments, info = model.transcribe(
    audio, language="vi",
    beam_size=1,                      # 1–3; 3 chậm hơn ~30–50%
    temperature=0.0,                  # tắt fallback nhiệt độ
    condition_on_previous_text=False, # chống lặp lan truyền
    no_speech_threshold=0.6,
    log_prob_threshold=-1.0,
    compression_ratio_threshold=2.4,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500),
)
segs = list(segments)  # materialize trong worker thread
```

Lưu ý: generator của faster-whisper là **lazy**; lặp nó trên asyncio event loop sẽ chặn pipeline (Pipecat PR #5931; **Reported**)[^hallu].

**Tầng 3: lọc sau decode** (**Reported**)[^hallu]:

- Bỏ segment có `no_speech_prob > 0.6` **và** `avg_logprob < -1.0`.
- Bỏ cả turn nếu `compression_ratio > 2.4` (text quá lặp) hoặc ít hơn 2 từ trong khi VAD báo < 400 ms.
- Regex blacklist: `subscribe`, `đăng k[ýí] (cho )?kênh`, `để không bỏ lỡ những video`, `cảm ơn (các bạn )?đã (xem|theo dõi)`, `La La School`, `Ghiền Mì Gõ`; và câu lặp nguyên văn ≥ 3 lần.

### 11.7.4 Cảnh báo khi dùng blacklist

- Blacklist là **vá**, không phải giải pháp; người dùng thật có thể nói "cảm ơn đã xem" (ví dụ trong video hướng dẫn). Log mọi lần lọc để theo dõi false positive (**Synthesis**).
- Ngưỡng là từ báo cáo AI-compiled, chưa tune trên audio; hiệu chỉnh theo từng triển khai (**Reported**, wiki ghi giới hạn)[^hallu].
- Khi WER ồn tiếng Việt > ~15% hoặc hallucination vẫn lọt, wiki gợi ý thay model: Qwen3-ASR, PhoWhisper, ChunkFormer; Parakeet v3 không có tiếng Việt (**Reported**)[^hallu][^sel].
- Model native RNNT ít hallucinate dạng "câu ma" hơn vì decoder không phải LM tự do, nhưng vẫn có lỗi chèn/xoá khi nhiễu (**Synthesis**, chưa đo).

---

## 11.8 Chất lượng output: punctuation, casing, ITN, hotwords

- **Punctuation và casing:** Nemotron phát sẵn (**Reported**)[^nemotron]; Whisper cũng; nhiều model CTC thì không (cần model hậu xử lý). LLM phía sau chịu được text không dấu câu tốt hơn TTS; nhưng giao diện/log cần punctuation.
- **ITN (inverse text normalization):** đổi "không chín tám ba bốn" thành `0983…`, "hai mươi nghìn đồng" thành `20.000đ`. Là bước đối ngẫu của TTS text normalization (Chương 19). ITN sai là nguồn lỗi nặng cho số điện thoại, tiền, ngày. Fun-ASR-MLT-Nano có hotwords/ITN (**Reported**)[^sel]; nếu model không có, cần tầng rule hoặc LLM sau ASR (**Synthesis**).
- **Dấu thanh tiếng Việt:** model có thể xuất Unicode NFC hoặc NFD; **chuẩn hoá về NFC** ở adapter, nếu không, so khớp từ khoá và tính WER bị sai (Chương 5).
- **Hotwords/initial prompt:** `hotwords` cho tên sản phẩm/thương hiệu, hoặc `initial_prompt` ngắn có dấu câu chuẩn (**Reported**)[^hallu]. Không đưa câu dài, không đưa cụm "outro". Với Qwen có context biasing (**Reported** ở mức khả năng)[^sel]. Luôn A/B: hotwords có thể làm model "bịa" từ khoá khi audio không có.
- **Từ đệm, ngắt quãng, tiếng địa phương:** quyết định có giữ "ờ, ừm" hay không; quy định nhất quán giữa model và evaluation.

---

## 11.9 Confidence: không so được giữa các model

- Điểm tin cậy của mỗi model được hiệu chỉnh khác nhau (hoặc không hiệu chỉnh). `avg_logprob` của Whisper, xác suất token của RNNT, "confidence" của API đóng không cùng thang.
- Báo cáo cộng đồng: độ tin cậy không giảm dù độ chính xác giảm mạnh với ngôn ngữ ít tài nguyên; "confidence is unusable outside top-tier languages" (**Reported**, anecdote)[^usable].
- **Quy tắc:** nếu model không có điểm, adapter ghi `"unknown"`, **không bịa** `1.0`. Dùng tín hiệu **gián tiếp**: `no_speech_prob`, compression ratio, độ bất đồng giữa hai pass (Nemotron vs Qwen), độ dài text so với độ dài audio.
- **Entity-level safety:** WER không phản ánh rủi ro; "đừng huỷ" → "huỷ" chỉ sai một từ nhưng thất bại hoàn toàn. Chấm riêng *action-bearing span* (phủ định, số, tên, ngày); một báo cáo nêu độ chính xác thực thể thấp hơn độ chính xác transcript khoảng 15 điểm (**Reported**, anecdote)[^usable]. Chính sách: số điện thoại, số tiền, ngày và phủ định chỉ hành động sau final **và** read-back/xác nhận khi confidence "unknown" hoặc thấp.

---

## 11.10 Metric đánh giá

### 11.10.1 WER/CER

$$\text{WER} = \frac{S + D + I}{N}$$

(thay thế, xoá, chèn, trên N từ tham chiếu). Với tiếng Việt, "từ" là từ đơn tiết (tách theo khoảng trắng), mỗi âm tiết đã là một token; WER tiếng Việt ~ tương đương syllable error rate. **CER** (ký tự) nhạy hơn với lỗi dấu thanh. Nên báo cả hai, và báo thêm "WER không dấu" để tách lỗi dấu khỏi lỗi âm vị (**Synthesis**).

### 11.10.2 Normalizer khi đánh giá

Cùng một câu có thể bị tính khác: hoa/thường, dấu câu, số ("20" vs "hai mươi"), NFC/NFD, từ viết tắt. **Phải dùng cùng normalizer cho tham chiếu và dự đoán, và cùng cho các model đem so.** Card Nemotron nói rõ chuẩn hoá casing, punctuation, numerals trước khi chấm và cảnh báo sai lệch còn lại có thể làm tăng lỗi (**Reported**)[^sel]. Normalizer quá "dễ dãi" che mất lỗi số/tên quan trọng (**Synthesis**).

### 11.10.3 RTF, RTFx, TTFT và latency thật từ mic

- **RTF/RTFx:** throughput, không phải latency (§11.3.4).
- **TTFT** (time to first token): thời gian từ khi gửi request đến token đầu, đo ở server; không gồm thời gian user nói, capture, transport, endpoint.
- **Latency thật từ mic:** log timestamp theo sự kiện, cùng đồng hồ: `t_user_stop`, `t_vad_end`, `t_first_partial`, `t_first_stable`, `t_asr_final`, `t_llm_first_token`, `t_tts_first_audio` (Chương 10, 20). Cộng đồng báo cáo mất khoảng một tháng tinh chỉnh nhầm stage vì thiếu timeline thống nhất (**Reported**, anecdote)[^usable].

### 11.10.4 Metric đặc thù streaming

| Metric | Ý nghĩa |
|---|---|
| First partial / first stable latency | Độ sớm của text và độ sớm của text dùng được |
| Partial rewrite rate | Tỉ lệ token bị sửa sau khi hiển thị |
| Span survival time | Một đoạn sống bao lâu trước khi bị sửa |
| Word lag | Trễ giữa lúc nói và lúc stable |
| Endpoint→final P50/P95 | Độ trễ sau khi hết lượt |
| Entity accuracy | Số, tên, phủ định, ngày đúng nguyên vẹn |
| Hallucination rate | Số turn im lặng/nhiễu mà ASR vẫn xuất text |
| Cost per successful call | Chi phí tính trên kết quả đúng, không trên phút audio |

---

## 11.11 Bẫy benchmark

1. **Tập dữ liệu khác nhau.** FLEURS, VIVOS, CommonVoice (CMV), VLSP2020, MLC-SLM, và tập private không cùng phân phối (đọc vs tự nhiên, phòng thu vs ồn, giọng vùng miền). So 5.55 (Qwen FLEURS-vi) với 4.25 (Gipformer vivos) là vô nghĩa (**Reported**, diễn giải **Synthesis**)[^sel].
2. **Giao thức offline vs streaming.** Qwen3-ASR FLEURS-vi 5.55 và MLC-SLM-vi 14.92 là offline, không phải streaming WER (1.7B); Nemotron FLEURS-vi có chunk và LangID cụ thể. Do đó "5.55 vs 12.29" **không** chứng minh Qwen tốt hơn ở cùng latency (**Reported**, **Synthesis**)[^sel].
3. **Normalizer khác nhau.** Gipformer dùng normalizer riêng và test set private; số vendor không tái lập, không so trực tiếp với hàng khác (**Reported**)[^sel].
4. **Concurrency khác nhau.** TTFT/throughput ở concurrency 1 khác 128 (§11.3.4).
5. **Phần cứng không xác định.** Paper Qwen ghi "single typical computing resource"; benchmark 27 ms CPU của NeMo-Speech.cpp thuộc model tiếng Anh, không phải Nemotron 3.5 tiếng Việt (**Reported**)[^sel].
6. **Không có benchmark chung.** Wiki ghi rõ: không có một benchmark cùng audio, normalizer, chunk, hardware để tuyên bố model nào tốt nhất cho realtime tiếng Việt (**Reported**)[^sel]. Đây là việc phải tự làm (Chương 21).
7. **Tối ưu vào tập công khai.** Model fine-tune sát tập công khai có thể kém nặng trên audio thật; luôn giữ holdout tự thu có Bắc/Trung/Nam, tên riêng, số, nhiễu, điện thoại 8 kHz.

---

## 11.12 Gắn vào pipeline

```text
VAD/endpointing (Ch.10)
      │ audio turn / audio chunks
      ▼
┌──────────────── ASR adapter ────────────────┐
│ chuẩn hoá input (16k mono f32), ép language │
│ model: native stream | buffered | turn-final│
│ chuẩn hoá output: NFC, strip tag, ITN       │
│ lọc hallucination, gắn confidence/"unknown" │
└─────────────────────┬────────────────────────┘
        partial / stable / final (revision_id)
                      ▼
   LLM (Ch.12): prefetch trên partial, trả lời trên final
```

Điểm cần canh:

- ASR phát `<EOU>` (nếu có) là **một** tín hiệu endpoint; vẫn cần timeout dự phòng và VAD (Chương 10). Số liệu EOU của Parakeet là P50 160 ms, P95 320 ms trên audio TTS ghép im lặng, tiếng Anh; không dùng để tuyên bố endpoint tiếng Việt (**Reported**)[^eou][^sel].
- Khi bot đang nói, ASR nhận cả echo; AEC (Chương 7) quyết định ASR có "nghe" chính bot hay không.
- Mỗi session có **state riêng** (cache encoder, buffer, language); không dùng chung giữa session.
- ASR phải **huỷ được** (cancellation) khi barge-in/endpoint đổi quyết định (Chương 17).

---

## 11.13 Quy trình thử một ASR mới

1. **Đọc model card** (Chương 9): input rate, ngôn ngữ, streaming?, chunk, license, size, ràng buộc (độ dài tối thiểu/tối đa).
2. **Smoke test** với audio sạch 16 kHz mono: đúng ngôn ngữ, có punctuation, có dấu thanh?
3. **Test điều kiện xấu:** im lặng 30 s, nhạc, nhiễu, tiếng quạt, loa ngoài, 8 kHz điện thoại, từ rất ngắn ("dạ", "không"), đọc dãy số.
4. **Đo streaming:** first partial, first stable, rewrite rate, word lag, endpoint→final P50/P95.
5. **Đo thực thể:** địa chỉ, số tiền, số điện thoại, ngày, phủ định.
6. **Đo tài nguyên:** RTF/RTFx, peak VRAM/RAM mỗi session, concurrency, contention với LLM/TTS.
7. **Gate quyết định:** availability, license, hiệu năng trên phần cứng đích, nguyên tắc "không hành động trên text chưa ổn định". Đây là gate đề xuất của wiki (**Synthesis**)[^sel].

---

## 11.14 Lỗi thường gặp (checklist)

- [ ] Đưa audio sai sample rate/kênh/chuẩn hoá (int16 chưa chia 32768; stereo).
- [ ] Không ép `language`, để auto LangID đoán trên câu ngắn.
- [ ] Coi partial là final: gọi tool/ghi CRM trên text chưa stable.
- [ ] Nhầm RTF < 1 với "latency thấp"; báo TTFT server như latency người dùng cảm nhận.
- [ ] Cắt audio mỗi 200 ms rồi coi mỗi mảnh là một transcript độc lập (Whisper) thay vì dùng policy.
- [ ] Để `condition_on_previous_text=True` trong voice agent.
- [ ] Đưa "cảm ơn đã xem"/câu outro vào `initial_prompt`.
- [ ] Lặp lazy generator của faster-whisper trên event loop.
- [ ] Không lọc segment `no_speech_prob`/`compression_ratio` cao.
- [ ] Không chuẩn hoá Unicode (NFC) và token đặc biệt (`<EOU>`, `<vi-VN>`) trước khi đưa LLM.
- [ ] Bịa `confidence = 1.0` khi model không có điểm.
- [ ] So WER giữa các model khác tập dữ liệu, giao thức, normalizer, hardware.
- [ ] Không log timeline thống nhất audio-in/partial/final/LLM/TTS.
- [ ] Chỉ đo WER, bỏ qua entity accuracy và hallucination rate.

---

## Đáp án tự kiểm tra

**Q1.** Input chuẩn: 16 kHz, mono, `float32` trong `[-1, 1]` (hoặc `int16` nếu API quy định), có độ dài tối thiểu/tối đa tuỳ model; ngôn ngữ nên ép (`vi`, `vi-VN`). Output tối thiểu: text, segment với `start/end`, ngôn ngữ; nên có `revision_id`, `kind` (partial/stable/final), `avg_logprob`/`no_speech_prob` nếu có, `eou` nếu có, và `confidence` hoặc `"unknown"`.

**Q2.** Partial có thể bị sửa; stable prefix là phần policy tin sẽ không đổi; final là kết quả cuối sau endpoint. Hành động không đảo ngược (tool call, ghi CRM, TTS trả lời) chỉ nên làm trên final (hoặc stable qua ngưỡng kèm read-back cho thực thể), vì phần cuối (số, tên, ngày) thường là phần chưa stable khi user vừa dứt lời. Prefetch trên partial thì được vì đảo ngược được.

**Q3.** Native/stateful (cache-aware, encoder nhân quả, vd Nemotron), buffered/policy (model offline + LocalAgreement/AlignAtt/rollback, vd Whisper/Qwen3-ASR streaming), turn-final (decode sau endpoint). RTF < 1 chỉ nghĩa là theo kịp luồng audio; không cho biết first partial/first stable, vì còn chunk, lookahead, compute, hàng đợi, commit policy.

**Q4.** Auto LangID trên đoạn ngắn, ồn hoặc có từ mượn hay sai; sai ngôn ngữ kéo theo cả transcript sai. Ép `language="vi"` loại một nguồn lỗi và giảm một nguồn hallucination; vẫn log `language_probability` (nếu detect) và kiểm code-switch.

**Q5.** Whisper hallucinate khi audio im lặng, nhạc hoặc nhiễu, audio quá ngắn, prompt chứa câu outro, `condition_on_previous_text=True`. Lọc bằng `no_speech_prob`, `avg_logprob`, `compression_ratio`, số từ so với độ dài VAD, blacklist regex, kết hợp VAD gating và decode conservative (`temperature=0`, `beam_size 1–3`).

**Q6.** Khác giao thức (offline vs streaming với chunk 320 ms), khác chế độ LangID, khác tập chuẩn hoá/hardware, và Qwen FLEURS-vi là số offline; số của Nemotron có chunk cụ thể. Không thể kết luận Qwen thắng ở cùng latency.

**Q7.** Confidence không được calibrate giữa các model; dùng `"unknown"` khi thiếu, không bịa. Với số điện thoại/số tiền/ngày/phủ định: chỉ hành động sau final, kèm read-back/xác nhận khi tin cậy thấp hoặc không biết, và dùng tín hiệu gián tiếp (no-speech, compression ratio, bất đồng giữa hai pass).

---

## Hạn chế và phạm vi bao phủ

- Chưa chạy lại model ASR nào; mọi số WER, latency, TTFT, throughput là **Reported** qua wiki, và chưa có benchmark khớp (cùng audio, normalizer, chunk, hardware) cho tiếng Việt. Nhận xét như "native RNNT ít hallucinate dạng câu ma" là **Synthesis**, chưa đo.
- Số liệu hallucination và ngưỡng lọc đến từ một báo cáo AI-compiled (issue GitHub và PR không có trong `raw/`), chưa tune trên audio; trích từ các anecdote cộng đồng (Reddit) là **Reported/Unverified**.
- Bản chuẩn hoá `TranscriptEvent` ở §11.1.2 là **đề xuất thiết kế** (Synthesis), không phải API của model nào.
- Chi tiết `att_context_size` của Nemotron, API của Qwen3-ASR/vLLM, ChunkFormer streaming ONNX chưa đi sâu; model ChunkFormer small streaming có card HTTP 401 nên chưa xác định (**Reported**)[^sel].
- Chương này chưa đi sâu E2E full-duplex (Chương 15), cancellation (Chương 17), diarization (Chương 14) và ASR đo chất lượng bằng bộ dữ liệu riêng (Chương 21).
- Số liệu model có hạn dùng (`stale_after` wiki: 2027-10); kiểm tra lại phiên bản.

## Phụ lục chương

### Script mô phỏng LocalAgreement (`/tmp/asr_stable.py`, đã chạy)

```python
def lcp(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y: break
        n += 1
    return n

def local_agreement(hyps, k=2):
    committed, log = [], []
    for t, h in enumerate(hyps):
        if t >= k - 1:
            common = h
            for prev in hyps[t-k+1:t]:
                common = common[:lcp(common, prev)]
            if len(common) > len(committed):
                committed = common[:]
        log.append((t, len(committed), " ".join(committed)))
    return log

hyps = [h.split() for h in [
  "tôi", "tôi muốn đặt", "tôi muốn đặt vé đi", "tôi muốn đặt vé đi đà",
  "tôi muốn đặt vé đi đà nẵng", "tôi muốn đặt vé đi đà nẵng ngày mười",
  "tôi muốn đặt vé đi đà nẵng ngày mười lăm"]]
for r in local_agreement(hyps): print(r)
```

Kết quả chạy: số từ commit lần lượt 0, 1, 3, 5, 6, 7, 9; "lăm" cuối còn chưa commit khi chuỗi dừng. Hypothesis là dữ liệu giả lập, **không** phải đầu ra model thật.

### Liên kết sang chương khác

- Chương 2–3: sample rate, mono, codec (nền của §11.1.1).
- Chương 5: tiếng Việt, NFC/NFD, số, ITN (nền của §11.8).
- Chương 9: đọc model card (nền của §11.13).
- Chương 10: VAD, endpointing, `<EOU>` (nền của §11.2, §11.12).
- Chương 12: LLM dùng partial/final; prefetch.
- Chương 17–18: cancellation và async/streaming.
- Chương 19: ITN là đối ngẫu của text normalization cho TTS.
- Chương 20–21: đo latency và chất lượng.

---

[^eou]: [Parakeet Realtime EOU 120M v1](../wiki/parakeet-realtime-eou-120m-v1.md) — Input/output (16 kHz mono, ≥160 ms, `<EOU>` inline), EOU latency P50 160/P90 280/P95 320 ms trên DialogStudio TTS + 3 s im lặng.
[^nemotron]: [Nemotron 3.5 ASR](../wiki/nemotron-3.5-asr-streaming-0.6b.md) — Architecture and I/O; auto language tag `<xx-XX>`; Streaming operating points (80/160/320/560/1120 ms); cache-aware mechanism.
[^fw]: [Faster-Whisper](../wiki/faster-whisper.md) — `transcribe` returns `(segments, info)`, `info.language`/`language_probability`, `word_timestamps=True` → `segment.words`.
[^hallu]: [Whisper Hallucination Mitigation for Vietnamese](../wiki/whisper-hallucination-mitigation.md) — Decoding parameters; Post-transcription filters; When to stop filtering; Coverage and limits (nguồn: báo cáo AI-compiled).
[^wlk]: [WhisperLiveKit](../wiki/whisperlivekit.md) — streaming policies (SimulStreaming/AlignAtt, LocalAgreement), Qwen3-streaming bounded recompute window 12 s và yêu cầu `--language` tường minh.
[^sel]: [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md) — Định nghĩa realtime; Shortlist và bằng chứng tiếng Việt; Qwen streaming và efficiency; Kiến trúc và hướng triển khai; Gate đánh giá đề xuất; dẫn nguồn primary package `../raw/vietnamese-asr-research-2026-10-07/README.md`. Cộng với [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md).
[^usable]: [Community-Reported Usable STT for Voice Agents](../wiki/community-usable-stt-voice-agents.md) — Usable-text evaluation checklist; Failure order reported; Logging and diagnosis practice (anecdote Reddit, chưa kiểm chứng).
