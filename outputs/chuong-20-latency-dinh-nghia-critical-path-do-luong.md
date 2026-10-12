# Chương 20. Latency: định nghĩa, critical path, đo lường 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần VI (Đo lường và vận hành). Đây là chương đầu của Phần VI.
> **Chương trước:** [Chương 19. Cầu text → speech: chunker, normalizer, lexicon](chuong-19-cau-text-to-speech-chunker-normalizer-lexicon.md). **Chương tiếp theo:** Chương 21. Đánh giá chất lượng và release gate.
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §3 nguyên tắc 6 (không cộng các con số khác loại), §8.1 (critical path và output gate), §8.2 (ngân sách tham khảo), §8.3 (đòn bẩy), §8.4 (monitoring theo turn), §10 (gate đo lường và nguyên tắc A/B).
> **Cơ sở:** phân phối xác suất và phân vị, hàng đợi (Little, utilization), coordinated omission, ước lượng offset đồng hồ kiểu NTP, bootstrap, và các tham số đo audio phía trình duyệt là **kiến thức nền chung**, không phải claim lấy từ nguồn wiki. Định nghĩa chỉ số và số đo của từng hệ lấy từ wiki và gắn nhãn bằng chứng: [Speech-to-Speech Response Latency Instrumentation](../wiki/speech-to-speech-latency-instrumentation.md), [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md), [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md), [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md), [VieNeu-TTS Streaming Runtime and Performance](../wiki/vieneu-tts-streaming-runtime.md), [Qwen3-ASR family](../wiki/qwen3-asr-family.md), [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md), [Parakeet Realtime EOU 120M v1](../wiki/parakeet-realtime-eou-120m-v1.md), [Smart Turn](../wiki/smart-turn.md), [Voice Agent Frameworks](../wiki/voice-agent-frameworks.md). Thông tin vendor và report AI là **Reported** (wiki chưa chạy lại). Năm script ở "Phụ lục chương" chạy bằng Python 3.12.3 thuần (không thư viện ngoài) ngày 2026-10-13: **Reproduced** cho hành vi của chính mã minh hoạ. Mọi tham số trong script là **giả định** lấy trong dải Reported, không gọi model hay GPU thật. Thiết kế và suy luận của tác giả là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Định nghĩa được "voice-to-voice latency" bằng hai mốc cụ thể, biết năm biến thể đang bị gọi cùng một tên, và chọn đúng biến thể cho đúng câu hỏi.
2. Vẽ được critical path của một lượt, giải thích vì sao các stage chồng lấn không cộng được, và viết được công thức có output gate `max(hold, ASR + LLM)`; tính được **slack** để biết tối ưu stage nào là vô ích.
3. Phân biệt chính xác TTFT, TTFC, TTFA, RTF, RTFx, first partial, first stable text, endpoint→final và các số "chunk size", "EOU latency", "final-token latency" mà model card đưa ra.
4. Đọc một bảng ngân sách latency một cách phê phán: mốc đầu/cuối là gì, phân vị nào, có output-hold không, đã tính playback chưa.
5. Báo cáo latency đúng: P50/P95/P99 có điều kiện, warm và cold tách riêng, theo concurrency, với cỡ mẫu đủ; tránh hai ảo ảnh benchmark (warm giả và coordinated omission).
6. Thiết kế instrumentation: tập mốc thời gian, ID để join, đồng hồ đơn điệu, đo v2v không cần đồng bộ đồng hồ client/server, đọc được bản ghi latency của HF s2s.
7. Chọn đòn bẩy tối ưu dựa trên stage nào đang nằm trên critical path, biết giá của từng đòn bẩy.
8. Chạy được một A/B latency có kết luận thống kê.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Voice-to-voice latency bắt đầu từ đâu, kết thúc ở đâu? Đo ở client hay server?
- Q2. Vì sao các stage chạy chồng lấn thì không cộng được với nhau? Output gate quyết định latency khi nào?
- Q3. TTFT, TTFA, RTF, RTFx, first partial, first stable text, endpoint→final: định nghĩa của từng cái?
- Q4. Một bảng ngân sách latency phải được đọc phê phán như thế nào?
- Q5. Báo cáo P50/P95/P99, warm/cold và concurrency thế nào cho không tự lừa mình?
- Q6. Làm sao đồng bộ đồng hồ client/server và join log của các stage?
- Q7. Khi cần giảm latency, làm gì trước? Mỗi đòn bẩy tác động lên số hạng nào?
- Q8. Làm sao biết một thay đổi thật sự làm pipeline nhanh hơn?

---

## 20.1 Bức tranh: latency không phải một con số

Một lượt hội thoại trong pipeline cascade đi qua nhiều tầng, mỗi tầng được các tài liệu mô tả bằng một con số "latency" riêng. Các con số đó **không cùng loại**: có cái đo từ mic, có cái đo từ lúc gửi request, có cái là kích thước cửa sổ, có cái là thông lượng ở batch 128.

```text
 thời gian →
 user nói ───────────────┤ mẫu speech cuối (M0)
                         ├── chờ im lặng / VAD quyết định (M1) ── soft-end (M2)
                         │      ├─ ASR final ──────────────┤ (M4)
                         │      └─ LLM prefill → token đầu → mệnh đề đầu (M6, M7)
                         │      ├──────────── output hold H ───────────┤ gate mở / commit (M3)
                         │                                              ├─ TTS request → byte audio đầu (M8, M9)
                         │                                              └─ mạng → client → pre-buffer → render → nghe được (M10..M12)
```

Hình này mô tả một thiết kế speculative có output gate (**Synthesis** từ HF s2s và thiết kế §8.1).[^design][^s2s] Ba điều rút ra ngay:

1. Có **hai nhánh song song** (nhánh gate và nhánh compute), nên tổng latency là `max` chứ không phải tổng.
2. "Latency của model X" chỉ là **một đoạn** trên hình. Nó không là v2v.
3. Muốn tối ưu thì phải biết nhánh nào đang quyết định; đo từng đoạn và đo cả hai nhánh.

Quy tắc xuyên suốt, đã ghi ở thiết kế §3 nguyên tắc 6: **không cộng các con số khác loại**. Chunk size của ASR không phải độ trễ ra văn bản ổn định. TTFT 92 ms của Qwen không phải độ trễ từ mic. TTFA 115 ms của VieNeu không phải độ trễ voice-to-voice. RTF của batch không phải RTF của một stream (**Synthesis**).[^design]

---

## 20.2 Voice-to-voice: bắt đầu từ đâu, kết thúc ở đâu (Q1)

Thiết kế §8.1 đặt critical path: *"mẫu speech cuối của user → endpoint commit → final ASR được chấp nhận → LLM: mệnh đề có nghĩa đầu tiên → TTS: mẫu audio phát được đầu tiên → client: mẫu audio nghe được đầu tiên"* (**Synthesis**).[^design] Nghĩa là mốc đầu là **mẫu speech cuối của user**, mốc cuối là **mẫu audio đầu tiên nghe được**. Nhưng trong thực tế, hai mốc này được xấp xỉ theo nhiều cách khác nhau.

### 20.2.1 Năm định nghĩa đang dùng chung một tên

| # | Tên | Mốc đầu | Mốc cuối | Đo ở đâu | Còn thiếu so với D0 |
|---|---|---|---|---|---|
| D0 | **Perceived v2v** (chuẩn vàng) | Mẫu speech cuối **thật** của user (ground truth: annotation file thử, hoặc đo trên tín hiệu) | Mẫu audio đầu của bot **nghe được** ở loa | Ngoài hệ thống (loopback, ghi âm hai kênh) | — |
| D1 | **Client v2v** | Mẫu speech cuối do server **ước lượng** (VAD), quy ra đồng hồ client bằng chỉ số mẫu | Mẫu đầu render ở worklet cộng `outputLatency` | Client | Sai số ước lượng speech-end, chênh lệch mic→mẫu |
| D2 | **Server `e2e`** (HF s2s v2) | **Ước lượng** cuối tiếng nói | Khối audio đầu TTS yield ra | Server | Uplink, downlink, pre-buffer, playback, sai số ước lượng |
| D3 | `e2e` cũ (HF s2s v1) | Thời điểm VAD handoff | Khối audio đầu TTS yield ra | Server | D2 + thời gian chờ im lặng; **không so được** với D2 |
| D4 | **Response latency** của framework/service | Lúc gửi request cho từng service hoặc lúc commit | Byte đầu của service đó | Server | Toàn bộ endpoint wait; chỉ là một đoạn |

Về D2/D3: tài liệu HF s2s phiên bản 2 định nghĩa lại `e2e` là từ **estimated speech end** tới **first generated audio**, gồm thời gian VAD decision, Smart Turn, audio enhancement và hold, nhưng đo audio sinh ra chứ không đo playback của trình duyệt; nếu không có ước lượng speech end thì `e2e` là `null`, không lùi về mốc handoff cũ (**Reported**).[^s2slat] Nghĩa là số `e2e` của bản v1 và v2 là hai đại lượng khác nhau dù tên giống hệt.

### 20.2.2 Chọn định nghĩa theo câu hỏi

| Câu hỏi | Dùng | Lý do |
|---|---|---|
| "Người dùng cảm thấy chậm bao nhiêu?" | D1 (hoặc D0 khi cần chuẩn vàng) | Gồm mạng, pre-buffer, playback |
| "Đổi model ASR từ A sang B có nhanh hơn không?" | D2 hoặc đo từng đoạn, cùng một harness | Cô lập khỏi mạng và client |
| "Tầng nào đang chậm trong turn này?" | D4 nhiều đoạn, join theo ID (§20.7) | Phân rã |
| "Có đạt SLO sản phẩm không?" | D1 P95 | Con số người dùng thấy |
| "So sánh với report/blueprint" | Phải hỏi report dùng D nào (§20.5) | Thường không nói |

Nguyên tắc: **con số tiêu đề đo ở client (D1), phân rã đo ở server, hai bên join bằng ID** (**Synthesis**). Một panel timings của server cho bạn D2 và các stage, nhưng không cho bạn buffer và playback của trình duyệt: demo HF s2s ghi rõ panel "Server timings" đo ở server và các stage chồng lấn nên không được cộng (**Reported**, theo [Chương 6](chuong-06-capture-va-playback-realtime.md) §6.10.3).[^s2slat]

### 20.2.3 Chênh lệch D1 so với D2 gồm những gì

Với các giá trị giả định ở §20.3.3, D1 − D2 = capture buffer + uplink (50 ms) + downlink (30 ms) + pre-buffer (100 ms) + `outputLatency` (20 ms) = **200 ms**. Hai điểm cần nhớ (**Synthesis**):

- **Pre-buffer nằm trực tiếp trên critical path.** Mỗi ms pre-buffer là một ms v2v ([Chương 6](chuong-06-capture-va-playback-realtime.md) §6.5.3, [Chương 13](chuong-13-tts-tu-van-ban-toi-waveform.md) §13.8.3). VieNeu khuyến nghị client pre-buffer 150–300 ms, nên con số TTFA 115 ms của TTS và con số "nghe được" cách nhau hàng trăm ms (**Reported**).[^vieneu]
- **Sai số ước lượng speech-end ăn thẳng vào D2.** VAD mô tả "cuối tiếng nói" bằng một mẫu ước lượng: Silero dùng đầu chunk có confidence thấp đầu tiên, FireRed dùng cuối frame speech cuối, và độ chính xác bị giới hạn bởi hàng đợi, jitter, kích thước chunk, độ phân giải frame (**Reported**).[^s2slat] Nếu ước lượng muộn hơn cuối thật, D2 nhỏ hơn D0.

### 20.2.4 Ngữ cảnh cảm nhận

Trong hội thoại người–người, khoảng lặng giữa hai lượt thường được trích khoảng 200 ms (nghiên cứu đa ngôn ngữ như Stivers và cộng sự, 2009; **kiến thức nền**, chưa kiểm chứng trong wiki). Một pipeline cascade có endpoint wait, ASR, LLM và TTS không thể sát mức đó. Vì vậy mục tiêu thực tế là tập trung vào (a) phân phối đuôi (P95), (b) không có lượt "chết" quá lâu, và (c) tín hiệu cho người dùng biết hệ thống đang xử lý. Điểm (c) là đòn bẩy cảm nhận chứ không phải đòn bẩy đo được (xem §20.9.3).

---

## 20.3 Critical path và vì sao không cộng được (Q2)

### 20.3.1 Hai kiểu quan hệ giữa stage

| Quan hệ | Ví dụ | Latency kết hợp |
|---|---|---|
| **Nối tiếp phụ thuộc** (stage sau cần output của stage trước) | LLM cần transcript cuối; TTS cần mệnh đề đầu | Cộng |
| **Song song / chồng lấn** (hai việc chạy cùng lúc) | ASR+LLM speculative trong lúc output bị giữ; TTS mệnh đề 1 trong lúc LLM sinh mệnh đề 2; ASR streaming chạy trong khi user còn nói | `max` hoặc phần chồng lấn không tính |

Tài liệu của HF s2s nói rõ các stage chồng lấn nên **không được cộng để dựng lại E2E**, và `hold_s` chỉ tính thời gian bị chặn thực sự ở các gate, trong đó các chờ worker chồng nhau chỉ đếm một lần (**Reported**).[^s2slat]

### 20.3.2 Công thức có output gate

Thiết kế §8.1 (bổ sung 2026-10-07) cho (**Synthesis**, từ [HF s2s — Endpointing](../wiki/speech-to-speech-pipeline.md#endpointing-and-turn-taking)):[^design]

```text
v2v ≈ (cuối tiếng user → soft-end) + max(output-hold, ASR + LLM tới mệnh đề đầu)
      + TTS tới audio đầu + transport/playback
```

Với default HF s2s, output-hold là 800 ms cho lượt complete và tới 2 s cho lượt incomplete: lượt complete dùng `--speculative_reopen_ms` 800 ms; lượt incomplete chờ `--smart_turn_incomplete_delay_ms` 600 ms trước khi bắt đầu STT/LLM và output bị giữ tới `--smart_turn_max_wait_ms` 2 s (**Reported**).[^s2s] Nếu TTS chỉ chạy sau khi gate mở thì TTS nằm ngoài `max`. Nếu hệ thống tổng hợp sẵn audio của mệnh đề đầu và giữ nó tới khi gate mở, TTS lọt vào trong `max`:

```text
v2v ≈ soft-end + max(H, A + L + T) + transport/playback      (TTS speculative, Synthesis)
```

Hệ quả quan trọng: **khi H > A + L, giảm ASR hay LLM không làm v2v đổi.** Streaming ASR không vượt qua được output gate (**Synthesis**).[^design]

### 20.3.3 Ví dụ số: một lượt, ba kiến trúc (Reproduced, tham số giả định)

Script 1 (phụ lục) dùng: capture+uplink 50 ms, soft-end sau 250 ms im lặng, Smart Turn 30 ms, ASR final 200 ms, LLM tới mệnh đề đầu 250 ms, TTS TTFA 115 ms, downlink 30 ms, pre-buffer 100 ms, `outputLatency` 20 ms. Kết quả:

| Kiến trúc | v2v (ms) | Bị gate quyết định? |
|---|---|---|
| Tuần tự sau commit, không hold | 1045 | — |
| Speculative, hold H = 0 | 1045 | Không |
| Speculative, hold H = 300 | 1045 | Không (ASR+LLM = 450 > 300) |
| Speculative, hold H = 800 | **1395** | **Có** |
| Speculative + TTS speculative, H = 800 | 1280 | Có |

Phân rã cho dòng H = 800: 50 + 250 + 30 + `max(800, 450)` + 115 + 30 + 100 + 20 = **1395 ms**, trong đó 350 ms của nhánh compute là **slack** (nhánh gate chờ 800, compute xong từ 450).

Độ nhạy khi giảm 100 ms ở từng stage:

| Thay đổi | Tuần tự | H = 800 | H = 300 |
|---|---|---|---|
| ASR −100 ms | −100 | **0** | −100 |
| LLM −100 ms | −100 | **0** | −100 |
| TTS −100 ms | −100 | −100 | −100 |
| Hold 800 → 300 | n/a | **−350** (v2v 1395 → 1045) | |

Đọc kết quả (**Synthesis**):

1. Trong cấu hình gate-bound, đổi sang ASR nhanh hơn hay LLM nhanh hơn không tiết kiệm được ms nào. Đòn bẩy đúng là **hold** hoặc **TTS**.
2. Speculative có hold không nhanh hơn kiến trúc tuần tự không hold. Giá trị của nó là **giảm false cutoff** với cùng ngưỡng im lặng ([Chương 10](chuong-10-vad-endpointing-va-turn-detection.md) §10.5), và chỉ nhanh hơn khi so với tuần tự dùng im lặng dài để đạt cùng độ an toàn. Muốn so công bằng phải đo cả **tỉ lệ cắt nhầm** ([Chương 21](de-cuong-kien-thuc-nen-tang-speech-pipeline.md)).
3. Công thức này là mô hình "đúng bậc nhất". Thực tế còn contention GPU giữa ASR/LLM/TTS khi chạy chồng lấn ([Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.8), nên `A + L` khi chạy song song với TTS có thể lớn hơn khi chạy riêng.

### 20.3.4 Slack analysis: quy trình ba bước

1. Với mỗi lượt, ghi mốc thời gian của cả hai nhánh (xem §20.7.1): `t_gate_open` và `t_compute_ready`.
2. Tính `slack = t_gate_open − t_compute_ready`. Slack > 0 nghĩa là lượt đó bị gate-bound; slack < 0 là compute-bound.
3. Báo cáo **tỉ lệ lượt gate-bound** theo loại lượt (complete/incomplete). Script 2 cho thấy với H = 400 ms và ASR+LLM có P50 450 ms, khoảng 27,5% lượt vẫn bị gate quyết định: đó là lượt mà tối ưu compute là vô ích, trong khi ở 72,5% còn lại thì có ích. Một tỉ lệ như vậy cho biết nên đặt công sức ở đâu (**Reproduced**, tham số giả định).

### 20.3.5 Các lỗi cộng nhầm thường gặp

| Lỗi | Vì sao sai | Số liệu trong wiki |
|---|---|---|
| Lấy chunk size ASR làm latency ra text | Chunk là cận dưới; latency thật còn cộng compute, hàng đợi, transport, commit policy | Nemotron 80–1120 ms là cấu hình suy luận, WER 13.41 → 11.18 theo chunk (**Reported**) |
| Lấy TTFT 92 ms của Qwen3-ASR làm độ trễ từ mic | Đo ở concurrency 1, vLLM, input ~2 phút có sẵn, không phải audio đến từ mic | 92/105 ms (avg/P95); concurrency 128: 3210/6195 ms (**Reported**)[^qwen] |
| Lấy TTFA 115 ms của VieNeu làm v2v | TTFA chỉ là đoạn TTS, một stream, RTX 3060, chưa gồm mạng/playback | (**Reported**)[^vieneu] |
| Lấy RTFx batch làm tốc độ một stream | RTFx throughput đo ở batch lớn | Parakeet TDT 0.6B V2: RTFx 3380 ở batch 128 (**Reported**)[^survey] |
| Cộng cận dưới các stage làm "v2v tốt nhất" | Mỗi stage không đạt cận dưới cùng lúc; xem §20.5 | Blueprint: tổng các dải 0,95–2,9 s, mục tiêu 1–2 s (**Reported/Synthesis**)[^blueprint] |
| Cộng P95 của các stage để ra P95 tổng | Phân vị không cộng được (§20.6.2) | Script 2 |

---

## 20.4 Từ điển chỉ số (Q3)

Mỗi chỉ số dưới đây được xác định bởi **mốc đầu, mốc cuối, nơi đo**. Khi đọc một con số mới, hỏi ba điều đó trước.

### 20.4.1 Nhóm endpoint và turn

| Chỉ số | Mốc đầu → cuối | Ghi chú |
|---|---|---|
| **Endpoint wait** (`min_silence`) | Cuối tiếng nói → đủ im lặng để đóng đoạn | Tham số cấu hình, cộng thẳng vào v2v; HF s2s mặc định `--min_silence_ms` 64 ms, Pipecat khuyến nghị `stop_secs=0.2` khi có Smart Turn, blueprint 500 ms, thiết kế 500–800 ms khi không có semantic detector (**Reported**)[^s2s][^stack][^blueprint] |
| **`vad_decision_s`** (HF) | Ước lượng cuối voiced audio → VAD iterator trả segment cuối (trước Smart Turn) | `null` nếu iterator không cho vị trí mẫu cuối (**Reported**)[^s2slat] |
| **Smart Turn analysis** | Gọi `predict_endpoint` → kết quả | Vendor: ~10 ms trên một số CPU, dưới 100 ms trên hầu hết cloud, ~65 ms Pipecat Cloud 1x (**Reported**)[^smart] |
| **`hold_s`** (HF) | Tổng thời gian bị chặn thực sự ở các gate xử lý/giải phóng response, chờ chồng nhau đếm một lần | Grace có việc hữu ích chạy bên trong **không** tính là hold; Smart Turn tắt thì `null` (**Reported**)[^s2slat] |
| **EOU latency** (model) | Cuối tiếng nói → model phát `<EOU>` | Parakeet Realtime EOU 120M: P50 160, P90 280, P95 320 ms, đo trên audio TTS-generated DialogStudio có 3 s im lặng nối thêm; thực tế biến thiên theo môi trường (**Reported**)[^eou] |

EOU latency của model chỉ là **cận dưới sạch** vì audio là giọng tổng hợp có im lặng tuyệt đối. Không đem nó cộng với `min_silence` (đã gồm trong cùng khoảng chờ) và không coi là v2v (**Synthesis**).

### 20.4.2 Nhóm ASR

| Chỉ số | Định nghĩa | Phân biệt với |
|---|---|---|
| **Chunk size / algorithmic latency** | Cỡ audio mà model xử lý mỗi bước, cộng lookahead | Chỉ là cận dưới. Nemotron: 80/160/320/560/1120 ms chọn lúc suy luận, WER FLEURS-vi 13.41 → 11.18 (**Reported**)[^nemotron] |
| **First partial** | Từ mẫu voiced đầu tiên (hoặc từ lúc mẫu đó được gửi) tới event partial không rỗng đầu tiên | Phải nêu mốc đầu; partial có thể bị sửa |
| **Emission lag** (từng từ) | Thời điểm text của từ được phát − thời điểm audio của từ kết thúc | Dùng để so các model streaming khác chunk |
| **First stable text** | Tới khi một tiền tố được coi ổn định (append-only, LocalAgreement, "giữ bốn chunk cuối chưa cố định") | "Stable" phụ thuộc chính sách; không là first partial ([Chương 11](chuong-11-asr-hop-dong-input-output-va-hanh-vi-streaming.md) §11.5) |
| **Endpoint→final** | Từ lúc endpoint niêm phong audio → transcript final được chấp nhận | Với model turn-final tăng theo độ dài lượt; với streaming nhỏ (flush chunk cuối). `stt` của HF: từ lúc xếp VAD commit cuối tới khi nhận transcript final (Realtime) hoặc từ lúc request final worker bắt đầu (HTTP), **không** gồm các lần transcription lũy tiến và delta partial (**Reported**)[^s2slat] |
| **Final-token latency** | Độ trễ token cuối ở một mức concurrency | Nemotron công bố median ở nhiều mức concurrency trên một H100: 240 stream ở 80 ms vs 14 của Parakeet RNNT 1.1B buffered (**Reported**)[^nemotron] |
| **ASR TTFT** (paper Qwen3-ASR) | Time-to-first-token cho request async với input đầy đủ | Không phải latency từ mic (§20.3.5) |
| **RTF / RTFx** | Xem §20.4.5 | |

Ví dụ giả định để thấy vì sao "RTF thấp" không có nghĩa "text sớm" ([Chương 11](chuong-11-asr-hop-dong-input-output-va-hanh-vi-streaming.md) §11.3.4): Whisper turn-final RTF 0,3 trên một lượt 10 s, chờ endpoint 1,2 s rồi decode 3 s, text chỉ có sau ≈ 4,2 s kể từ cuối tiếng nói. Một model streaming RTF 0,8 vẫn cho first partial sau vài trăm ms (**Synthesis**).

### 20.4.3 Nhóm LLM và cầu text

| Chỉ số | Định nghĩa | Ghi chú |
|---|---|---|
| **Prefill time** | Xử lý toàn bộ prompt | Nằm trong TTFT; giảm bằng prefix cache |
| **TTFT** | Gửi request → token đầu | Thành phần cố định |
| **Tokens/s** | Tốc độ decode sau token đầu | Quyết định underrun |
| **TTFC** (time to first clause) | Gửi request → chunker có mệnh đề đầu | **Số cần tối ưu thật**; = TTFT + thời gian sinh đủ một mệnh đề ([Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.3.1) |
| **Chunker hold** | Mệnh đề hoàn thành → chunk được flush | Rất nhỏ khi đã có đủ text: ClauseChunker 0,148 ms cho câu 258 ký tự, Normalizer 0,090 ms trên 86 ký tự (**Reproduced** trong [Chương 19](chuong-19-cau-text-to-speech-chunker-normalizer-lexicon.md)); phần còn lại là **chờ LLM sinh đủ text** |
| **`first_sentence→tts_first_byte`** | Từ lúc câu đầu có → byte TTS đầu | Metric theo từng turn trong thiết kế §8.4 (**Reported**)[^design][^stack] |

Chương 19 mô phỏng (tham số giả định, **Reproduced**) rằng với LLM 40 token/s và TTS GPU, audio đầu có lúc 752 ms khi flush theo mệnh đề, 1428 ms theo câu, 2890 ms khi chờ cả câu trả lời. Đây là minh hoạ rằng chunker thay đổi **số hạng TTFC**, không đổi TTFT.

### 20.4.4 Nhóm TTS và phát

| Chỉ số | Định nghĩa | Ghi chú |
|---|---|---|
| **TTFA** | VieNeu: từ lúc gửi request tới **byte audio thật** đầu tiên (header WAV ~2 ms không tính). HF s2s `tts_ttfa`: từ lúc bắt đầu tổng hợp segment text đầu → mẫu audio đầu của provider tới | Hai định nghĩa **khác mốc đầu** (gửi request vs bắt đầu tổng hợp); HTTP TTS của HF loại header WAV, resample và gom block diễn ra sau (**Reported**)[^vieneu][^s2slat] |
| **RTF một stream** | Thời gian sinh / thời lượng audio | `< 1` thì stream không tụt |
| **Lead** | Audio đã nhận − thời gian đã trôi kể từ chunk đầu | Âm = có khe im lặng. VieNeu GPU lead nhỏ nhất +80 ms (≤ 16 stream), CPU +320 ms (**Reported**)[^vieneu] |
| **Inter-chunk gap** | Khoảng chunk kết thúc phát → chunk kế sẵn sàng | Metric underrun; phụ thuộc cả tốc độ LLM lẫn RTF TTS ([Chương 19](chuong-19-cau-text-to-speech-chunker-normalizer-lexicon.md), [Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.3.3) |
| **Pre-buffer wait** | Thời gian chờ đủ đệm client trước khi phát | Cộng thẳng vào D1 |
| **`outputLatency`** | Mẫu được render → ra loa | `ctx.outputLatency`; Bluetooth lớn hơn nhiều ([Chương 6](chuong-06-capture-va-playback-realtime.md) §6.5) |

Coverage đo của HF s2s hiện giới hạn: `tts_ttfa` và `e2e` chỉ đo cho `qwen3` và `openai`; `chatTTS`, `facebookMMS`, `omnivoice`, `pocket`, `kokoro`, `supertonic` là `n/a`, và `stt` không đo cho `parakeet-unified`, `paraformer` (**Reported**).[^s2slat] Nghĩa là không thể rút ra so sánh TTS từ bản ghi này nếu backend nằm ngoài danh sách.

### 20.4.5 RTF và RTFx: bốn con số cùng tên

```text
RTF  = T_xử_lý / T_audio          RTFx = 1 / RTF = T_audio / T_xử_lý
```

| Biến thể | Đo gì | Dùng để | Không dùng để |
|---|---|---|---|
| **RTF một stream (streaming)** | Một stream chạy theo nhịp thời gian thực, đo từ chunk đầu | Biết stream có tụt không, còn bao nhiêu dư | — |
| **RTF throughput (bulk)** | Nhiều request batch, tổng thời gian / tổng audio | Ước tính chi phí batch offline | Dự đoán latency hội thoại |
| **RTF một câu không streaming** | Sinh nguyên câu rồi mới có audio | So backend | Dự đoán TTFA |
| **RTFx leaderboard** | Throughput ở batch lớn (ví dụ batch 128) | So hiệu quả GPU offline | Một stream |

VieNeu là ví dụ điển hình: trên GPU cùng một model có **ba** RTF khác nhau: bulk 0,011–0,02; một câu không streaming 0,10; streaming một stream 0,49 trên RTX 3060 (**Reported**, theo [Chương 13](chuong-13-tts-tu-van-ban-toi-waveform.md) §13.8.2).[^vieneu] Luôn hỏi: RTF đo ở chế độ nào?

Hai quan hệ hữu ích (**Synthesis**, số học trên số Reported):

1. **Điều kiện ổn định:** với một tài nguyên xử lý tuần tự, tổng RTF của các stream đang chạy phải `< 1`. CPU fp32 6 nhân của VieNeu: một stream RTF 0,55–0,61; hai request cùng lúc đo được RTF 1,19 mỗi stream, tức tụt cả hai; khớp với 2 × 0,6 ≈ 1,2 > 1.[^vieneu] Int8 một stream RTF 0,35, hai stream 0,58–0,67, vẫn realtime.[^vieneu]
2. **Turn-final ASR:** `endpoint→final ≈ RTF_final × T_lượt + overhead`, nên **phụ thuộc độ dài lượt**; báo cáo phải gắn bucket độ dài.

---

## 20.5 Đọc ngân sách latency một cách phê phán (Q4)

### 20.5.1 Hai bảng ngân sách trong wiki

| Stage | Claude report (vi stack) | ChatGPT blueprint |
|---|---|---|
| Network + jitter | 30–80 ms | 50–200 ms |
| VAD silence / end-of-speech | 200–300 ms | 400–600 ms |
| Smart Turn | 10–65 ms | — |
| ASR turn-final | 100–300 ms | 200–700 ms |
| LLM TTFT + chunk đầu | 150–350 ms | 100–500 ms + tách câu 100–400 ms |
| TTS TTFA | 64–300 ms | 100–500 ms |
| **Voice-to-voice (report tự nêu)** | **~0,7–1,2 s** | **mục tiêu 1–2 s** |

Cả hai là ước lượng của report AI, **Reported**, không phải target và chưa đo.[^stack][^blueprint][^design]

### 20.5.2 Cộng thử (Reproduced, Script 1)

| Bảng | Tổng cận dưới | Tổng trung điểm | Tổng cận trên | Con số report nêu |
|---|---|---|---|---|
| Claude vi-stack | 554 ms | 974 ms | 1395 ms | ~0,7–1,2 s |
| ChatGPT blueprint | 950 ms | 1925 ms | 2900 ms | 1–2 s |

Đọc kết quả (**Synthesis**): dải của Claude hẹp hơn dải tổng các cận (ngầm giả định các stage ở vùng giữa trở xuống), và dải của ChatGPT mục tiêu 1–2 s ngầm giả định các stage gần cận dưới hoặc chồng lấn. Cả hai đều là "kỳ vọng" chứ không phải bất đẳng thức.

### 20.5.3 Danh sách câu hỏi khi đọc một ngân sách

1. **Mốc đầu là gì?** Cuối tiếng nói thật, ước lượng VAD, hay commit? Hai bảng trên không nói rõ.
2. **Có gồm output-hold không?** HF s2s mặc định giữ 800 ms (complete), tới 2 s (incomplete); không có dòng "hold" trong hai bảng, trong khi bản ghi HF v2 có `hold_s` riêng (**Reported**).[^s2s][^s2slat] Nếu hold lớn hơn ASR+LLM thì bảng cộng sai theo hướng thấp.
3. **Có gồm playback không?** Pre-buffer 150–300 ms và `outputLatency` không có trong bảng nào.
4. **Phân vị nào?** Con số thường là "điển hình" hoặc dải, không nêu P50/P95.
5. **Phần cứng, concurrency, warm/cold?** Ví dụ VieNeu ~115 ms là RTX 3060, một stream, ấm.
6. **Cộng hay max?** Dải có được cộng không, hay stage nào chồng lấn?
7. **Phạm vi LLM:** LLM là dependency ngoài; thiết kế nói speech pipeline không thể cam kết tổng ~1 s khi chưa biết endpoint LLM (**Reported/Synthesis**).[^design]

### 20.5.4 Dùng ngân sách như SLO phân rã

Một ngân sách có ích khi nó là **mục tiêu phân bổ**, không phải dự báo. Cách dùng (**Synthesis**):

1. Chọn mốc và định nghĩa v2v (D1), một phân vị mục tiêu, một điều kiện (phần cứng, concurrency).
2. Đo baseline trước, rồi mới đặt mục tiêu; không lấy số của report làm cam kết.
3. Chia mục tiêu cho **nhánh** (gate, compute, TTS, transport), không chia đều cho stage.
4. Với từng stage đặt gate riêng, vì gate ở stage dễ kiểm hơn v2v. Thiết kế §8.4 đề xuất gate khởi điểm cho TTS: TTFA P95 khoảng 250–400 ms và RTF P95 ≤ 0,7 dưới tải thực (**Synthesis**, SLO đề xuất).[^design]

---

## 20.6 Phân vị, warm/cold và concurrency (Q5)

### 20.6.1 Vì sao phải dùng phân vị

Trung bình bị đuôi kéo và che đi lượt tệ. Ngoài ra, người dùng trải nghiệm theo **hội thoại** chứ không theo lượt (**Synthesis**, số học):

- Xác suất ít nhất một lượt trong 10 lượt vượt P95 = 1 − 0,95¹⁰ ≈ **40%**; trong 20 lượt ≈ **64%**.
- Với P99 và 20 lượt: 1 − 0,99²⁰ ≈ 18%.

Nên P95 là "một lượt trong hai hội thoại ngắn sẽ gặp", không phải "hiếm".

| Phân vị | Ý nghĩa vận hành | Số mẫu tối thiểu để ước lượng ổn định (kiến thức nền) |
|---|---|---|
| P50 | Trải nghiệm điển hình | Vài chục |
| P95 | Một lượt trong hai mươi | Hàng trăm |
| P99 | Một lượt trong một trăm | Hàng nghìn |

Script 2 xác nhận bằng mô phỏng: với phân bố giả định có P95 thật ≈ 901 ms, độ lệch chuẩn của ước lượng P95 là 94 ms ở n = 30, 31 ms ở n = 300, 9 ms ở n = 3000; P99 còn bất ổn hơn (154 ms ở n = 30, 72 ms ở n = 300, 21 ms ở n = 3000) (**Reproduced**).

### 20.6.2 Phân vị không cộng được

Với ba stage độc lập có (P50, P95) giả định là ASR (200, 320), LLM (250, 450), TTS (115, 200): tổng P50 = 565 ms, tổng P95 = 970 ms. Mô phỏng 200 000 lượt (Script 2, **Reproduced**):

| Tương quan giữa stage | P50 tổng | P95 tổng | P99 tổng | ΣP95 − P95(tổng) |
|---|---|---|---|---|
| ρ = 0 (độc lập) | 583 | 818 | 950 | 152 |
| ρ = 0,5 | 574 | 900 | 1086 | 70 |
| ρ = 0,9 (tải GPU chung chi phối) | 567 | 958 | 1193 | 12 |

Kết luận (**Synthesis**):

1. P95 của tổng **không bằng** tổng các P95. Khi stage độc lập, tổng P95 đánh giá quá cao; khi các stage cùng chịu một nguyên nhân (GPU chung, mạng chung), chúng đồng hành và tổng P95 gần đúng hơn.
2. **Đừng dựng P95 từ P95 của stage.** Đo P95 của v2v trực tiếp, bằng join theo turn (§20.7).
3. Với `max(H, A + L)`, phân vị của max khác max của phân vị: ví dụ H = 400 ms, P50 = 460 ms, P95 = 686 ms (Script 2).

### 20.6.3 Điều kiện hoá: không có "một" phân phối

Một phân phối latency thật là hỗn hợp của nhiều tổng thể con. Báo cáo cần **cắt lát** theo các chiều:

| Chiều | Vì sao khác nhau | Số liệu trong wiki |
|---|---|---|
| Loại lượt: complete / incomplete / có tool | Hold 800 ms vs tới 2 s; tool follow-up giữ speech-end gốc nên `e2e` gồm cả thời gian tool (**Reported**)[^s2slat] | |
| Độ dài lượt | ASR turn-final tăng theo độ dài (§20.4.5) | |
| Độ dài text của chunk đầu | TTFA tăng theo độ dài prompt TTS | VieNeu CPU int8: 141–144 / 163–169 / 192–194 ms cho 27 / 88 / 147 ký tự; fp32: 264–282 / 313–357 / 345–401 ms (**Reported**)[^vieneu] |
| Lượt đầu của session / lượt sau | Cache lạnh, kết nối lạnh | |
| Phần cứng, concurrency | Xem 20.6.5 | |
| Trạng thái response: completed / cancelled | §20.7.4 | |

### 20.6.4 Warm và cold

**Cold** có nhiều tầng, mỗi tầng có cách khử riêng (**Synthesis**):

| Tầng cold | Biểu hiện | Cách xử lý |
|---|---|---|
| Process | Tải weights, capture CUDA graph, khởi tạo ONNX session | Giữ model resident trong VRAM; không load theo request; warm-up lúc khởi động |
| Page cache / đĩa | Lần đọc weights đầu chậm | Warm-up; không ghi file WAV tạm ra đĩa (**Reported**)[^design] |
| Cache logic | Prefix cache của system prompt chưa có; lượt đầu prefill cả prompt | Warm-up bằng request giả qua **cùng đường** như request thật ([Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.3.4) |
| Kết nối | Handshake TLS/WebSocket, thiết lập WebRTC | Connection pool, mở kết nối sớm trong lúc user nói |
| **Thiết bị (xung GPU/CPU)** | GPU hạ xung khi rảnh | Khoá xung ở host |

Ví dụ thiết bị rất đáng nhớ: VieNeu guide báo rằng trong khoảng ~2 s rảnh, driver NVIDIA đưa GPU vào trạng thái tiết kiệm điện (RTX 3060: P8, 210 MHz, 12 W); request kế tiếp chạy prefill, hai frame lead-in và lần gọi codec ở xung thấp đó. **Ấm 118 ms so với 403 ms sau 8 s rảnh**; 16 client ấm median 194 ms (max 354) so với 330–400 ms (max 450–540) sau 5–8 s rảnh. Giữ ấm từ trong process **không hiệu quả** (matmul 2048² hay replay graph mỗi 100–250 ms vẫn bị driver hạ xung); cách chữa nằm ở host: khoá xung `nvidia-smi -lgc 1500,2100` (hoàn tác `-rgc`, trên Linux thêm `-pm 1`), hoặc "Prefer maximum performance" trên Windows (**Reported**).[^vieneu]

Hệ quả cho đo đạc (**Synthesis**, Script 3A, **Reproduced** với tham số lấy từ hai điểm 118/403 ms):

| Cách đo | P50 | P95 | P99 |
|---|---|---|---|
| Benchmark liên tục (rảnh ~0,1 s) | 118 | 131 | 137 |
| Hội thoại (rảnh 6–20 s giữa hai lần bot nói) | **404** | 452 | 471 |
| Hỗn hợp: 75% request ấm | 122 | 427 | 456 |

Trong một cuộc gọi, **chunk đầu của mỗi lượt có thể luôn gặp GPU nguội** vì người dùng nói và nghĩ lâu hơn 2 s; chỉ chunk 2, 3... của cùng lượt là ấm. Vòng lặp benchmark chạy liên tục báo "118 ms" có thể không bao giờ đúng với chunk đầu trong sản xuất. Quy tắc: **harness phải mô phỏng khoảng rảnh thật giữa các request** và báo riêng "chunk đầu của lượt" với "chunk sau".

### 20.6.5 Concurrency

Latency là hàm của tải. Báo cáo phải là **đường cong latency–concurrency** chứ không phải một điểm.

| Hệ | Điểm đo | Kết quả | Gốc |
|---|---|---|---|
| VieNeu GPU, `max_streams=16`, RTX 3060, N request bắt đầu cùng lúc | N = 1 / 4 / 8 / 16 | TTFA median 115 / 130 / 164 / 185 ms (max 339 ở N=16), RTF tệ nhất 0,49 / 0,52 / 0,56 / 0,59 | (**Reported**)[^vieneu] |
| VieNeu GPU `max_streams=32` | N = 24 / 32 | TTFA 448 / 456 ms (max 629), RTF 0,86 / 0,93, lead âm | (**Reported**)[^vieneu] |
| VieNeu HTTP, 40 client (16 slot + 16 queue) | — | 32 OK, 8 × `429`; request xếp hàng thấy TTFA 1,5–3 s | (**Reported**)[^vieneu] |
| Qwen3-ASR-0.6B (vLLM, input ~2 phút) | concurrency 1 vs 128 | TTFT 92/105 → 3210/6195 ms (avg/P95); thông lượng 2000 audio-s/s | (**Reported**)[^qwen] |
| Nemotron 3.5 ASR (H100) | 80 ms và 1120 ms | 240 và 2400 stream song song ở độ trễ token cuối thấp, so với 14 và 400 của Parakeet RNNT 1.1B buffered | (**Reported**)[^nemotron] |

Ba điều cần rút ra:

1. **Hình dạng đường cong có gối.** VieNeu ở 16 stream giữ TTFA dưới 200 ms, ở 32 stream khoảng 450 ms và hết dư địa. Capacity là mức concurrency cao nhất mà P95 còn dưới mục tiêu.
2. **Kiểu đến cũng quan trọng.** "N cùng lúc" là trường hợp xấu (prefill dồn); request đến rải rác giữa 15 stream đang chạy có TTFA ~134 ms ở `max_streams=16`, so với 185 ms median khi cùng bắt đầu (**Reported**).[^vieneu] Hãy dùng đúng mô hình đến của sản phẩm.
3. **Cấu hình dư làm chậm mọi người.** Chi phí codec chung ≈ 65 ms + 2,5 ms × số slot **đã đặt trước**, nên slot dư làm chậm mọi request; đặt `max_streams` bằng số stream **đồng thời** thực tế (**Reported**).[^vieneu] Số stream ≠ số user: một user chat giữ stream khoảng 20–35% thời gian, nên 16 stream ≈ 45–80 user (tác giả ước, **Reported**).[^vieneu]

### 20.6.6 Hai ảo ảnh khi benchmark

**(a) Warm giả** (§20.6.4): vòng lặp liên tục che cold start thiết bị.

**(b) Coordinated omission.** Một load generator kiểu closed-loop chờ phản hồi xong mới gửi request kế, nên khi server đứng hình, nó **ngừng tạo tải đúng lúc tệ nhất** và chỉ ghi nhận một mẫu chậm. Script 3B (server đứng 1,0 s ở giây 10, dịch vụ bình thường 100 ms, lịch gửi 250 ms): closed-loop báo P95 = P99 = 100 ms (chỉ một mẫu 1100 ms), open-loop đo từ **thời điểm gửi dự định** báo P99 = 800 ms, cùng max 1100 ms (**Reproduced**). Quy tắc (**kiến thức nền**): dùng **open-loop** theo lịch cố định hoặc mô hình đến thật, và đo từ thời điểm dự định gửi.

Với voice agent, cách mô phỏng tự nhiên là **replay audio theo thời gian thực** ([Chương 18](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md) mục test): mỗi "người dùng ảo" phát file audio theo đồng hồ thật, rồi im lặng cho tới khi nhận được hoặc hết thời gian chờ, giống hành vi thật.

---

## 20.7 Instrumentation: mốc, ID, đồng hồ, join (Q6)

### 20.7.1 Tập mốc thời gian

Mỗi mốc là một **sự kiện có tên, thời điểm đơn điệu của host, và ID**. Từ mốc dẫn xuất khoảng, không ghi khoảng tại thời điểm phát. Đề xuất (**Synthesis**, dựa trên critical path §8.1 và bản ghi HF):

| Mốc | Sự kiện | Host | Ghi chú |
|---|---|---|---|
| M0 | Mẫu speech cuối **thật** | Harness | Chỉ có trong test có ground truth |
| M1 | `vad.speech_end` (ước lượng) kèm `sample_index` | Server | |
| M2 | `turn.soft_end` | Server | Bắt đầu speculative |
| M3 | `turn.commit` / gate mở | Server | Hết hold |
| M4 | `asr.final` được chấp nhận | Server | Kèm cờ endpoint→final |
| M5 | `llm.request_sent` | Server | |
| M6 | `llm.first_token` | Server | |
| M7 | `llm.first_clause` (chunker flush chunk 0) | Server | TTFC = M7 − M5 |
| M8 | `tts.request_sent` (chunk 0) | Server | |
| M9 | `tts.first_byte` | Server | TTFA = M9 − M8 |
| M10 | `audio.first_chunk_sent` / `received` | Server / Client | Mạng downlink |
| M11 | `playback.first_sample_rendered` | Client | `currentFrame` ở worklet |
| M12 | `audible` = M11 + `outputLatency` | Client | Mốc cuối D1 |

Từ đó:

```text
endpoint wait   = M1 → M2          (+ Smart Turn nếu tách)
nhánh compute   = M2 → max(M4, M7)
nhánh gate      = M2 → M3          (hold)
slack           = M3 − max(M4, M7) (với thiết kế TTS sau gate)
TTFA            = M8 → M9
v2v (D1)        = M12 − M0'        (M0' = M1 quy ra đồng hồ client)
```

### 20.7.2 ID để join

Join **theo ID, không theo thứ tự**. Dùng các ID đã định nghĩa ở [Chương 16](chuong-16-dataflow-end-to-end-va-audio-contract.md) §16.8 và [Chương 17](chuong-17-turn-taking-event-barge-in-va-cancellation.md) §17.6: `session_id`, `turn_id`, `revision`, `generation_id`, `chunk_id`, `sequence`. HF s2s thêm `response_key` để phân biệt một tool call với response nói tiếp của nó (cùng turn và revision), và response nói tiếp **không lặp lại** thời gian STT của turn gốc (**Reported**).[^s2slat] Khi có reopen, cancel hoặc nhiều chunk TTS, join theo `turn_id/revision/generation_id/chunk_id` (**Synthesis**, thiết kế §8.1).[^design]

Script 4A (**Reproduced**) minh hoạ hậu quả. Một lượt có hai revision: rev 0 bị huỷ (user nói tiếp), rev 1 hoàn tất.

| Cách join | Kết quả |
|---|---|
| Theo `(turn, rev)` | rev 0: `cancelled`, không có first audio; rev 1: `completed`, speech_end → first audio = **1320 ms** |
| Ngây thơ: speech_end **đầu tiên** của turn → first audio | **3720 ms** (sai: gồm cả thời gian user nói tiếp) |

### 20.7.3 Đồng hồ

| Nguyên tắc | Chi tiết |
|---|---|
| **Một khoảng, một đồng hồ, một máy** | Đo khoảng bằng hiệu hai mốc của **cùng** host; dùng đồng hồ đơn điệu (`time.perf_counter_ns()`, `performance.now()`), không dùng wall clock `Date.now()`/`time.time()` vì NTP có thể làm nhảy (**kiến thức nền**; [Chương 6](chuong-06-capture-va-playback-realtime.md) §6.10.1) |
| **Đồng hồ audio là chủ** | Mốc audio dùng **chỉ số mẫu** (`currentFrame`), không dùng wall clock ([Chương 16](chuong-16-dataflow-end-to-end-va-audio-contract.md) §16.6.2) |
| **v2v không cần đồng bộ** | Server gửi chỉ số mẫu của speech-end trong `turn.commit`; client quy ra đồng hồ client bằng ánh xạ capture, trừ với mốc render của nó ([Chương 6](chuong-06-capture-va-playback-realtime.md) §6.10.3, **Synthesis**) |
| **Giữa service** | Mỗi callee tự đo thời gian xử lý trên đồng hồ của nó; caller đo toàn bộ; chênh = mạng + hàng đợi. HF cũng nêu thời gian remote đo ở server gồm truyền mạng và chờ provider, không phải thuần suy luận (**Reported**)[^s2slat] |

Script 4B (**Reproduced**, số minh hoạ phép tính, không phải đo thật): ánh xạ capture client `frame 0 ↔ 77000 ms`, `last_speech_sample = 520000` ở 48 kHz → mẫu cuối ứng với 87833,3 ms trên đồng hồ client; mẫu đầu render ở 89013,3 ms và `outputLatency` 22 ms cho "nghe được" tại 89035,3 ms → **v2v_client = 1202 ms**, không dùng đồng hồ server.

Khi **buộc phải** so hai đồng hồ khác máy, ước lượng offset kiểu NTP: `offset ≈ ((t1 − t0) + (t2 − t3)) / 2`. Sai số tối đa bằng **một nửa độ bất đối xứng** đường đi, `|d_up − d_down| / 2`. Script 4C (**Reproduced**):

| d_up (ms) | d_down (ms) | Sai số offset đo được | Tối đa lý thuyết |
|---|---|---|---|
| 20 | 20 | 0,0 | 0,0 |
| 20 | 28 | −4,0 | 4,0 |
| 10 | 60 | −25,0 | 25,0 |
| 5 | 120 | −57,5 | 57,5 |

Nghĩa là đồng bộ bằng ping **không thể loại bỏ** sai số trên mạng bất đối xứng (4G, Wi-Fi tải nặng) vì sai số cùng bậc với các khoảng ta muốn đo. Vì vậy ưu tiên cách tránh đồng bộ (chỉ số mẫu, đo khoảng trên một máy).

### 20.7.4 Ba cạm bẫy của instrumentation

1. **Survivorship.** HF s2s không sinh bản ghi cho response bị bỏ giữa chừng: *"an abandoned response has no terminal record"*, và bản ghi chỉ xuất hiện cho response có terminal event (**Reported**).[^s2slat] Nếu chỉ phân tích response hoàn tất, bạn bỏ mất các lượt cancel (barge-in, reopen) vốn thường nhanh hoặc chậm bất thường. Ghi **mọi** response kèm `status` (`completed`/`cancelled`/`failed`) và phân tích riêng.
2. **Chi phí đo.** Ghi log đồng bộ trên thread audio hay event loop làm chính nó thành nguồn trễ. Đẩy sự kiện vào hàng đợi, ghi ở thread khác ([Chương 6](chuong-06-capture-va-playback-realtime.md) §6.2, [Chương 18](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md)).
3. **Riêng tư.** Bản ghi latency chỉ cần độ dài, không cần nội dung: ghi `n_chars`, `n_tokens`, `n_samples`, không ghi transcript. HF giới hạn metadata Realtime ở 512 ký tự mỗi giá trị và 16 slot, và khi response kết thúc nó xoá khoá latency dành riêng nếu client tự đặt rồi ghi số đo của server (**Reported**; mục đích chống giả mạo là suy luận **Synthesis**).[^s2slat]

### 20.7.5 Một bản ghi tham chiếu: HF s2s version 2

Mỗi response hoàn tất ghi một dòng INFO và đặt cùng bản ghi vào `response.done` dưới khoá `response.metadata["speech_to_speech.turn_latency"]` (**Reported**).[^s2slat] Dòng log mẫu:

```text
Turn turn_3 rev=0 latency: stt=0.18s llm=1.24s tts_ttfa=0.12s e2e=2.01s vad_decision=0.36s hold=0.24s smart_turn_status=complete status=completed response_key=...
```

Các khoá JSON (schema `version: 2`): `e2e_s`, `hold_s`, `llm_s`, `response_key`, `smart_status`, `status`, `stt_s`, `tts_ttfa_s`, `turn_id`, `turn_revision`, `vad_decision_s`, `version`. Metadata Realtime là chuỗi nên giá trị là JSON gọn. Phiên bản 2 đã bỏ `llm_ttft_s`, `smart_analysis_s`, `smart_grace_s`, `smart_delay_s`, `mlx_lock_wait_s` khỏi metadata. Thời gian tính bằng giây; làm tròn hai chữ số ở log, đo không có là `null` (**Reported**).[^s2slat]

Hai điều cần lưu ý khi dùng làm khuôn mẫu (**Synthesis**):

- Số trong dòng log mẫu **không thể cộng**: `stt` 0,18 + `llm` 1,24 + `tts_ttfa` 0,12 = 1,54 ≠ `e2e` 2,01. Chênh 0,47 s không phải sai số: `llm` ở đây là toàn bộ thời gian sinh (đến khi hết output), `e2e` gồm `vad_decision` và `hold` và các chồng lấn khác.[^s2slat] Điều này cho thấy `llm` của HF **không phải TTFT hay TTFC**; để tối ưu v2v bạn cần thêm mốc M6/M7.
- Tài liệu **chỉ định nghĩa ngữ nghĩa đo, không công bố số latency nào** và wiki chưa chạy lại server nào, nên không thể dùng nó để so sánh backend (**Reported**).[^s2slat]

### 20.7.6 Đo từ bên ngoài (black-box harness)

Một harness đáng giá nên đo **không nhờ cộng tác của hệ thống** để kiểm tra các mốc bên trong (**Synthesis**; chi tiết kỹ thuật là kiến thức nền):

1. Phát một file audio có **speech-end đã biết** (annotation) làm đầu vào (với trình duyệt, Chrome có cờ `--use-fake-device-for-media-stream --use-file-for-fake-audio-capture=file.wav`).
2. Ghi lại đồng thời đầu vào và đầu ra âm thanh của client (hai kênh).
3. Phát hiện onset của audio bot trên kênh đầu ra bằng ngưỡng năng lượng; v2v (D0) = onset − speech-end đã biết.
4. So D0 với D1 của chính hệ thống để phát hiện sai lệch ước lượng speech-end và đo bù `outputLatency`.

Với thiết bị thật, đo độ trễ mic+loa bằng loopback xung/chirp và cross-correlation ([Chương 6](chuong-06-capture-va-playback-realtime.md) §6.10.4).

### 20.7.7 Dashboard và cảnh báo

Waterfall theo turn (Gantt: hai nhánh gate và compute, rồi TTS, mạng, playback) cho thấy ngay nhánh nào quyết định. Metric theo thiết kế §8.4 (**Reported**): `vad_end→asr_done`, `asr_done→llm_first_token`, `first_sentence→tts_first_byte`, v2v đo ở client, tỉ lệ transcript bị lọc, tỉ lệ barge-in, tỉ lệ false-interruption.[^design][^stack] Bổ sung (**Synthesis**): tỉ lệ lượt gate-bound (§20.3.4), `inter_chunk_gap` và `underrun_count`, `prebuffer_wait_ms`, tỉ lệ `429`/hàng đợi, và time-to-silence khi barge-in ([Chương 17](chuong-17-turn-taking-event-barge-in-va-cancellation.md) §17.8.4).

---

## 20.8 Quy trình benchmark và A/B (Q8)

### 20.8.1 Checklist một lần đo

1. **Ghi điều kiện:** phần cứng, driver, xung GPU (đã khoá chưa), phiên bản model/runtime, cấu hình VAD/Smart Turn/chunker, concurrency, mạng, trình duyệt/thiết bị.
2. **Tập đầu vào cố định:** cùng bộ audio (đa dạng độ dài, giọng ba miền, môi trường ồn), cùng ground truth ([Chương 21](de-cuong-kien-thuc-nen-tang-speech-pipeline.md)).
3. **Warm-up** qua cùng đường như request thật, rồi **bỏ** các lượt warm-up khỏi thống kê; đồng thời đo riêng cold (lượt đầu, sau khoảng rảnh dài).
4. **Open-loop**, theo thời gian thực, mô phỏng khoảng rảnh thật giữa lượt (§20.6.6).
5. **Đủ mẫu** cho phân vị cần báo (§20.6.1), ghi số mẫu cạnh số phân vị.
6. **Báo cáo:** P50/P95/P99 theo lát cắt (§20.6.3) và đường cong theo concurrency, kèm tỉ lệ thất bại (`429`, timeout, cancel).

### 20.8.2 A/B: ghép cặp, xen kẽ, khoảng tin cậy

Thiết kế §10 đặt nguyên tắc: mỗi lần đổi **một** thành phần, cùng ground truth, cùng điều kiện (**Synthesis**).[^design] Với latency cần thêm:

1. **Ghép cặp theo audio.** Chạy A và B trên cùng từng file, để độ khó lượt (độ dài, nội dung) triệt tiêu trong hiệu.
2. **Xen kẽ A/B/A/B** thay vì chạy hết A rồi hết B, để trôi nhiệt độ, xung GPU, tải nền không dồn vào một nhánh.
3. **Khoảng tin cậy bootstrap** cho hiệu P50 và P95; chỉ kết luận khi khoảng không chứa 0.
4. **Kiểm tra chất lượng kèm theo.** Giảm latency bằng cách hạ ngưỡng im lặng sẽ tăng false cutoff; so cả tỉ lệ cắt nhầm và WER ([Chương 21](de-cuong-kien-thuc-nen-tang-speech-pipeline.md)).

Script 5 (**Reproduced**, tham số giả định: B nhanh hơn A khoảng 8% ở thân phân phối): với n = 30 lượt, khoảng tin cậy 95% của hiệu P50 là [−174, 69] ms, **chưa kết luận được**; n = 100: [−103, 16] cho P50 và [−282, 119] cho P95, vẫn chưa; n = 400: P50 −56 ms [−82, −34] và P95 −120 ms [−185, −23], phân biệt được. Bài học: cải thiện thật cỡ vài chục ms cần hàng trăm lượt cho P50 và nhiều hơn cho P95. Khoảng tin cậy trong Script 5 còn rộng vì bootstrap trên hiệu hai phân vị không tận dụng hết cấu trúc cặp; kiểm định trên hiệu **theo từng lượt** thường chặt hơn (**Synthesis**).

---

## 20.9 Đòn bẩy tối ưu (Q7)

### 20.9.1 Thứ tự làm việc

```text
1. Đo (D1 + phân rã) ở điều kiện thật, bao gồm cold.
2. Xác định nhánh quyết định (gate hay compute) và tỉ lệ gate-bound.
3. Loại bỏ chờ không cần thiết trên nhánh quyết định (hold, endpoint wait, pre-buffer, cold start).
4. Mới tối ưu stage trên nhánh compute, theo thứ tự đóng góp lớn nhất.
5. Đo lại bằng A/B có CI; kiểm tra chất lượng (false cutoff, WER).
```

Quy tắc kiểu Amdahl (**Synthesis**): nếu stage chiếm tỉ lệ nhỏ trên nhánh quyết định thì tăng tốc nó không đáng kể; nếu nó nằm ngoài nhánh quyết định thì đóng góp bằng 0 (xem §20.3.3).

### 20.9.2 Bảng đòn bẩy

| Đòn bẩy | Số hạng bị tác động | Giá phải trả / rủi ro | Bằng chứng trong wiki |
|---|---|---|---|
| Warm-up mọi model, giữ resident trong VRAM, không ghi WAV tạm | Cold start (mọi stage) | Tốn VRAM thường trực | Báo cáo khuyến nghị (**Reported**)[^design][^stack] |
| Khoá xung GPU ở host | TTFA lượt sau khoảng rảnh | Điện, nhiệt; cần quyền host/Docker | VieNeu: 118 vs 403 ms (**Reported**)[^vieneu] |
| Prefix cache cho system prompt | TTFT, TTFC | Phải giữ tiền tố ổn định, không chèn dữ liệu động ở đầu ([Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.3.4) | (**Reported**)[^stack] |
| Tắt thinking của LLM | TTFC | Chất lượng lập luận | (**Reported**)[^stack] |
| Preemptive ASR + LLM từ soft-end | `A + L` chồng lấn với hold | Tốn compute vô ích nếu user nói tiếp; cần cancel sạch | Report: speculative ở 200 ms VAD im; HF s2s là phiên bản có kỷ luật (**Reported**)[^design] |
| Giảm hold / đặt hold theo loại lượt | Nhánh gate | Tăng false cutoff | HF s2s 800 ms/2 s; [Chương 10](chuong-10-vad-endpointing-va-turn-detection.md) §10.3 |
| Giảm `min_silence` khi có Smart Turn | Endpoint wait | Chỉ an toàn khi có tầng semantic; Pipecat 0,2 s (**Reported**)[^stack] | |
| Clause chunking | TTFC → TTFA (audio đầu) | Prosody gãy nếu chunk quá nhỏ; underrun nếu LLM chậm | Blueprint: tối ưu quan trọng nhất (**Reported**)[^blueprint]; mô phỏng [Chương 19](chuong-19-cau-text-to-speech-chunker-normalizer-lexicon.md) |
| Chunk đầu ngắn hơn (cắt ở dấu phẩy ≥ ~25 ký tự) | TTFA (do prompt ngắn) | Khe hở giữa chunk 1 và 2 | VieNeu TTFA tăng theo độ dài ký tự (**Reported**)[^vieneu] |
| Chọn ASR streaming/chunk nhỏ | `A` | WER tăng khi chunk nhỏ (13,41% ở 80 ms vs 11,18% ở 1120 ms) (**Reported**)[^nemotron] | Vô ích nếu gate-bound |
| `max_streams` đúng tải thật | TTFA dưới tải | Giảm capacity nếu đặt quá nhỏ | (**Reported**)[^vieneu] |
| Pre-buffer client nhỏ | Playback (cộng thẳng vào D1) | Underrun nếu jitter hoặc RTF cao; không cứu được RTF > 1 ([Chương 13](chuong-13-tts-tu-van-ban-toi-waveform.md) §13.8.3) | VieNeu khuyến nghị 150–300 ms (**Reported**)[^vieneu] |
| Transport: WebSocket LAN vs WebRTC | Mạng, jitter | WebRTC thêm độ phức tạp, đổi lại chịu mất gói ([Chương 8](chuong-08-transport-mang-cho-audio-realtime.md)) | |
| Đặt các service cùng mạng/host | Mạng giữa service | Tranh chấp tài nguyên | |
| Tách GPU hoặc lập lịch ASR/LLM/TTS | Contention khi chồng lấn | Chi phí hạ tầng ([Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.8) | |

### 20.9.3 Latency cảm nhận so với đo được

Một số kỹ thuật không giảm D1 nhưng giảm cảm giác chờ: câu xác nhận ngắn trước khi trả lời ("Dạ, để em kiểm tra ạ"), caption của partial transcript, báo trạng thái "đang xử lý". Rủi ro (**Synthesis**): nếu tính TTFA là "audio đầu tiên bất kỳ", câu xác nhận làm số đẹp lên mà không đổi thời điểm có **nội dung**; nó còn làm giãn thời gian nói và có thể bị coi là backchannel khi user ngắt lời ([Chương 17](chuong-17-turn-taking-event-barge-in-va-cancellation.md) §17.7). Hãy báo cáo hai chỉ số: `ttfa_any` và `ttfa_content`.

---

## 20.10 Trạng thái bằng chứng và giới hạn

| Chủ đề | Mức bằng chứng |
|---|---|
| Định nghĩa v2v và critical path, công thức có output gate | **Synthesis** từ thiết kế §8.1 và HF s2s; công thức là mô hình bậc nhất |
| Số TTFA/RTF/concurrency của VieNeu | **Reported**; một máy (RTX 3060, i5), một ngày; wiki chưa chạy lại |
| Số Qwen3-ASR, Nemotron, Parakeet EOU | **Reported** từ paper/model card; không so được trực tiếp với nhau (khác tập đo, khác định nghĩa) |
| Ngân sách latency của Claude và ChatGPT | **Reported**, ước lượng chưa đo, không phải target |
| Bản ghi latency HF s2s | **Reported**; đọc tài liệu, chưa chạy server; coverage backend còn khuyết |
| Mô phỏng ở phụ lục | **Reproduced** cho hành vi mã; tham số **giả định**, không thay cho đo thật |
| Chưa có | Số v2v tiếng Việt đo trên một stack hoàn chỉnh, đo ở client, đo cold, đo theo concurrency (thiết kế §1.1 mục 5) |

---

## Đáp án các câu hỏi

**Q1. v2v bắt đầu từ đâu, kết thúc ở đâu, đo ở client hay server?**
Bắt đầu: mẫu speech cuối của user. Kết thúc: mẫu audio đầu tiên của bot nghe được. Trong thực tế mốc đầu được xấp xỉ bằng ước lượng VAD và mốc cuối bằng thời điểm server yield audio (D2, HF `e2e`) hoặc thời điểm client render cộng `outputLatency` (D1). Chuẩn vàng D0 đo ngoài hệ thống. Con số tiêu đề đo ở client; phân rã đo ở server; join bằng ID; cách đo client không cần đồng bộ đồng hồ (§20.2, §20.7.3).

**Q2. Vì sao stage chồng lấn không cộng được? Output gate quyết định khi nào?**
Vì chúng chạy song song, thời gian kết hợp là `max` chứ không là tổng; các stage khác loại cũng không cộng được. Công thức: `v2v ≈ soft-end + max(H, A + L) + TTS + transport/playback`. Gate quyết định khi `H > A + L` (slack dương): lúc đó giảm ASR/LLM không đổi v2v. Với H = 800 ms và A + L = 450 ms, v2v = 1395 ms, và giảm ASR hoặc LLM 100 ms cho 0 ms lợi, trong khi hạ hold 800 → 300 cho −350 ms (§20.3).

**Q3. Định nghĩa các chỉ số.**
- **TTFT:** gửi request LLM → token đầu. **TTFC:** gửi request → mệnh đề đầu có ở chunker.
- **TTFA:** gửi request TTS (hoặc bắt đầu tổng hợp, tuỳ hệ) → byte/mẫu audio thật đầu tiên.
- **RTF:** thời gian xử lý / thời lượng audio; **RTFx:** nghịch đảo. Phân biệt RTF streaming một stream với RTF/RTFx throughput ở batch.
- **First partial:** tới event partial không rỗng đầu tiên (nêu mốc đầu). **First stable text:** tới khi tiền tố được chính sách coi ổn định. **Endpoint→final:** từ lúc endpoint niêm phong audio tới khi final được chấp nhận.
Mỗi chỉ số phải có mốc đầu, mốc cuối, nơi đo (§20.4).

**Q4. Đọc ngân sách phê phán.**
Hỏi mốc đầu/cuối, có hold, có playback, phân vị, phần cứng/concurrency/warm-cold, cộng hay max, phạm vi LLM. Cộng thử các dải: Claude 554–1395 ms (nêu 0,7–1,2 s), ChatGPT 950–2900 ms (nêu 1–2 s). Dùng ngân sách như mục tiêu phân bổ sau khi đo baseline, không như dự báo (§20.5).

**Q5. Báo cáo phân vị, warm/cold, concurrency.**
Báo P50/P95/P99 có số mẫu và có điều kiện (loại lượt, độ dài, chunk đầu, phần cứng, tải); không dựng P95 tổng từ P95 từng stage; tách cold (thiết bị, cache, kết nối, process) khỏi warm và mô phỏng khoảng rảnh thật; đưa đường cong latency–concurrency; dùng load open-loop để tránh coordinated omission (§20.6).

**Q6. Đồng bộ đồng hồ và join log.**
Tránh cần đồng bộ: đo khoảng trên một đồng hồ đơn điệu của một máy; dùng chỉ số mẫu cho mốc audio; server gửi chỉ số mẫu speech-end để client tính v2v. Nếu buộc so đồng hồ, offset kiểu NTP có sai số tối đa `|d_up − d_down|/2`. Join theo `turn_id/revision/generation_id/chunk_id/response_key`, không theo thứ tự; ghi cả response bị huỷ (§20.7).

**Q7. Tối ưu cái gì trước?**
Đo, tìm nhánh quyết định, bỏ chờ không cần thiết trên nhánh đó (hold, endpoint wait, cold start, pre-buffer), rồi mới tối ưu stage compute theo đóng góp. Mỗi đòn bẩy ánh xạ tới một số hạng của công thức và có giá riêng (bảng §20.9.2). Đo lại bằng A/B có CI và kiểm tra chất lượng đi kèm.

**Q8. Làm sao biết thay đổi có thật sự nhanh hơn?**
Cùng bộ audio, ghép cặp theo file, xen kẽ A/B, open-loop, bỏ warm-up, đủ mẫu, bootstrap CI cho hiệu P50 và P95, chỉ kết luận khi CI không chứa 0, đồng thời theo dõi false cutoff và WER (§20.8). Với cải thiện cỡ 5–10% cần hàng trăm lượt.

---

## Phụ lục chương: năm script minh hoạ

Tất cả chạy bằng Python 3.12.3 thuần, ngày 2026-10-13, trong `/tmp/ch20/`. Tham số là giả định lấy trong dải Reported; kết quả mô tả hành vi của mã, không phải đo hệ thật.

### Script 1: critical path, output-hold, slack (`critical_path.py`)

```python
# Chương 20 — Script 1: critical path, output-hold và slack. Mọi tham số là GIẢ ĐỊNH lấy trong dải Reported của report,
# không phải đo model thật.
UP, DOWN = 50, 30            # capture buffer + uplink; downlink (ms)
SOFT = 250                   # cuối tiếng nói -> soft-end (min_silence ~200-300 ms với Smart Turn)
SMART = 30                   # Smart Turn inference
PRE, OUTLAT = 100, 20        # pre-buffer client, outputLatency

def seq(A, L, T):            # không speculative: ASR/LLM/TTS bắt đầu sau commit, commit = soft-end
    return UP + SOFT + SMART + A + L + T + DOWN + PRE + OUTLAT

def spec(A, L, T, H):        # ASR+LLM chạy ngay từ soft-end, output bị giữ H ms; TTS chạy sau khi gate mở
    return UP + SOFT + SMART + max(H, A + L) + T + DOWN + PRE + OUTLAT

def spec_tts(A, L, T, H):    # biến thể: TTS cũng chạy speculative (audio giữ sẵn tới khi gate mở)
    return UP + SOFT + SMART + max(H, A + L + T) + DOWN + PRE + OUTLAT

print("== Cộng ngân sách của hai report (dải Reported) ==")
claude = {"net+jitter": (30, 80), "VAD silence": (200, 300), "Smart Turn": (10, 65), "ASR": (100, 300),
          "LLM TTFT+chunk": (150, 350), "TTS TTFA": (64, 300)}
gpt = {"net/buffer": (50, 200), "VAD end": (400, 600), "ASR": (200, 700), "LLM first token": (100, 500),
       "split câu": (100, 400), "TTS first": (100, 500)}
for name, d in (("Claude vi-stack", claude), ("ChatGPT blueprint", gpt)):
    lo = sum(v[0] for v in d.values()); hi = sum(v[1] for v in d.values())
    mid = sum(sum(v) / 2 for v in d.values())
    print(f"{name:18s} tổng cận dưới {lo:5d} ms | tổng trung điểm {mid:6.0f} ms | tổng cận trên {hi:5d} ms")
print("   (report tự nêu: Claude ~700-1200 ms; ChatGPT mục tiêu 1000-2000 ms)")

A, L, T = 200, 250, 115
print(f"\n== Một lượt: ASR={A} LLM(TTFC)={L} TTS(TTFA)={T} ms; UP={UP} SOFT={SOFT} SMART={SMART} DOWN={DOWN} PRE={PRE} OUT={OUTLAT} ==")
print(f"{'kiến trúc':34s} {'v2v ms':>7s}")
print(f"{'tuần tự sau commit':34s} {seq(A,L,T):7d}")
for H in (0, 300, 800):
    print(f"{'speculative, hold H=%d' % H:34s} {spec(A,L,T,H):7d}   (gate-bound: {H > A + L})")
print(f"{'speculative + TTS speculative H=800':34s} {spec_tts(A,L,T,800):7d}")

print("\n== Độ nhạy: giảm 100 ms ở từng stage, hold H=800 vs H=300 vs tuần tự ==")
base = {"seq": seq(A, L, T), "H=800": spec(A, L, T, 800), "H=300": spec(A, L, T, 300)}
rows = {"ASR -100": (A - 100, L, T), "LLM -100": (A, L - 100, T), "TTS -100": (A, L, T - 100)}
print(f"{'thay đổi':12s} {'seq':>6s} {'H=800':>7s} {'H=300':>7s}")
for k, (a, l, t) in rows.items():
    print(f"{k:12s} {seq(a,l,t)-base['seq']:6d} {spec(a,l,t,800)-base['H=800']:7d} {spec(a,l,t,300)-base['H=300']:7d}")
print(f"{'hold 800->300':12s} {'n/a':>6s} {spec(A,L,T,300)-base['H=800']:7d}")
print("\nSlack của nhánh compute khi H=800: H - (ASR+LLM) =", 800 - (A + L), "ms  -> tối ưu ASR/LLM dưới mức này không đổi v2v")
```

Output:

```text
== Cộng ngân sách của hai report (dải Reported) ==
Claude vi-stack    tổng cận dưới   554 ms | tổng trung điểm    974 ms | tổng cận trên  1395 ms
ChatGPT blueprint  tổng cận dưới   950 ms | tổng trung điểm   1925 ms | tổng cận trên  2900 ms
   (report tự nêu: Claude ~700-1200 ms; ChatGPT mục tiêu 1000-2000 ms)

== Một lượt: ASR=200 LLM(TTFC)=250 TTS(TTFA)=115 ms; UP=50 SOFT=250 SMART=30 DOWN=30 PRE=100 OUT=20 ==
kiến trúc                           v2v ms
tuần tự sau commit                    1045
speculative, hold H=0                 1045   (gate-bound: False)
speculative, hold H=300               1045   (gate-bound: False)
speculative, hold H=800               1395   (gate-bound: True)
speculative + TTS speculative H=800    1280

== Độ nhạy: giảm 100 ms ở từng stage, hold H=800 vs H=300 vs tuần tự ==
thay đổi        seq   H=800   H=300
ASR -100       -100       0    -100
LLM -100       -100       0    -100
TTS -100       -100    -100    -100
hold 800->300    n/a    -350

Slack của nhánh compute khi H=800: H - (ASR+LLM) = 350 ms  -> tối ưu ASR/LLM dưới mức này không đổi v2v
```

### Script 2: phân vị không cộng được, cỡ mẫu, `max` (`percentiles.py`)

```python
# Chương 20 — Script 2: phân vị không cộng được; tương quan giữa các stage; cỡ mẫu cho P95/P99.
# Phân bố lognormal với P50 và P95 GIẢ ĐỊNH (ms). Dùng random.seed cố định.
import math, random, statistics
random.seed(20)
Z95 = 1.6449
STAGES = {"ASR": (200, 320), "LLM": (250, 450), "TTS": (115, 200)}   # (P50, P95)

def params(p50, p95):
    mu = math.log(p50); sigma = (math.log(p95) - mu) / Z95
    return mu, sigma

def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))]

def simulate(rho, n=200_000):
    out = []
    ps = {k: params(*v) for k, v in STAGES.items()}
    for _ in range(n):
        shared = random.gauss(0, 1)                         # tải GPU chung
        tot = 0.0
        for k, (mu, s) in ps.items():
            z = math.sqrt(rho) * shared + math.sqrt(1 - rho) * random.gauss(0, 1)
            tot += math.exp(mu + s * z)
        out.append(tot)
    return out

print("Stage (P50/P95 giả định):", STAGES)
print(f"Tổng các P50 = {sum(v[0] for v in STAGES.values())} ms | Tổng các P95 = {sum(v[1] for v in STAGES.values())} ms\n")
print(f"{'tương quan rho':>14s} {'P50 tổng':>9s} {'P95 tổng':>9s} {'P99 tổng':>9s} {'ΣP95 - P95(tổng)':>17s}")
for rho in (0.0, 0.5, 0.9):
    xs = simulate(rho)
    print(f"{rho:14.1f} {pct(xs,.5):8.0f}ms {pct(xs,.95):8.0f}ms {pct(xs,.99):8.0f}ms {sum(v[1] for v in STAGES.values()) - pct(xs,.95):15.0f}ms")

print("\n== Độ ổn định của ước lượng phân vị theo cỡ mẫu (rho=0.5, lặp 300 lần) ==")
pop = simulate(0.5, 100_000)
true95, true99 = pct(pop, .95), pct(pop, .99)
print(f"giá trị 'thật' P95={true95:.0f} ms, P99={true99:.0f} ms")
print(f"{'n':>6s} {'P95 trung bình':>15s} {'P95 độ lệch chuẩn':>18s} {'P99 độ lệch chuẩn':>18s}")
for n in (30, 100, 300, 1000, 3000):
    e95, e99 = [], []
    for _ in range(300):
        s = random.sample(pop, n); e95.append(pct(s, .95)); e99.append(pct(s, .99))
    print(f"{n:6d} {statistics.mean(e95):13.0f}ms {statistics.pstdev(e95):16.1f}ms {statistics.pstdev(e99):16.1f}ms")

print("\n== max(hold, ASR+LLM): phân vị của max khác max của phân vị ==")
ps = {k: params(*v) for k, v in STAGES.items()}
H = 400
xs = []
for _ in range(200_000):
    a = math.exp(ps['ASR'][0] + ps['ASR'][1] * random.gauss(0, 1)); l = math.exp(ps['LLM'][0] + ps['LLM'][1] * random.gauss(0, 1))
    xs.append(max(H, a + l))
print(f"H={H} ms: P50={pct(xs,.5):.0f} ms, P95={pct(xs,.95):.0f} ms; tỉ lệ lượt bị gate quyết định (H > ASR+LLM) = "
      f"{sum(1 for x in xs if x == H) / len(xs):.1%}")
```

Output:

```text
Stage (P50/P95 giả định): {'ASR': (200, 320), 'LLM': (250, 450), 'TTS': (115, 200)}
Tổng các P50 = 565 ms | Tổng các P95 = 970 ms

tương quan rho  P50 tổng  P95 tổng  P99 tổng  ΣP95 - P95(tổng)
           0.0      583ms      818ms      950ms             152ms
           0.5      574ms      900ms     1086ms              70ms
           0.9      567ms      958ms     1193ms              12ms

== Độ ổn định của ước lượng phân vị theo cỡ mẫu (rho=0.5, lặp 300 lần) ==
giá trị 'thật' P95=901 ms, P99=1088 ms
     n  P95 trung bình  P95 độ lệch chuẩn  P99 độ lệch chuẩn
    30           890ms             94.2ms            154.0ms
   100           908ms             53.6ms            138.0ms
   300           906ms             30.6ms             71.8ms
  1000           900ms             16.8ms             39.1ms
  3000           902ms              9.3ms             21.2ms

== max(hold, ASR+LLM): phân vị của max khác max của phân vị ==
H=400 ms: P50=460 ms, P95=686 ms; tỉ lệ lượt bị gate quyết định (H > ASR+LLM) = 27.5%
```

### Script 3: hai ảo ảnh benchmark: warm giả và coordinated omission (`bench_artifacts.py`)

```python
# Chương 20 — Script 3: hai ảo ảnh khi benchmark.
# (A) "warm" vs "cold": GPU hạ xung sau ~2 s rảnh (VieNeu guide: 118 ms warm vs 403 ms sau 8 s rảnh, RTX 3060, Reported).
#     Trong hội thoại thật, khoảng cách giữa hai lần TTS được gọi thường > 2 s.
# (B) coordinated omission: vòng lặp closed-loop chờ phản hồi mới gửi tiếp nên che mất hàng đợi.
import random, statistics
random.seed(7)

def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))]

print("== (A) TTFA theo khoảng rảnh trước request ==")
def ttfa(idle_s):
    base = random.gauss(118, 8)                       # warm
    if idle_s > 2.0:                                  # GPU đã hạ xung
        return random.gauss(403, 30)                  # cold, theo điểm đo 8 s rảnh
    return base

# Benchmark liên tục (khoảng rảnh ~0.1 s) vs hội thoại (user nghe + nói + nghĩ: 6-20 s giữa hai lần bot nói)
bench = [ttfa(0.1) for _ in range(2000)]
chat = [ttfa(random.uniform(6, 20)) for _ in range(2000)]
mixed = [ttfa(random.choice([0.2, 0.2, 0.2, 8])) for _ in range(2000)]   # bot nói nhiều câu liền, rồi nghỉ
for name, xs in (("benchmark liên tục", bench), ("hội thoại (rảnh 6-20 s)", chat), ("lượt nhiều chunk (75% warm)", mixed)):
    print(f"{name:28s} P50={pct(xs,.5):4.0f} ms  P95={pct(xs,.95):4.0f} ms  P99={pct(xs,.99):4.0f} ms")
print("-> chunk đầu của mỗi lượt gặp GPU 'nguội' nếu lượt trước cách > 2 s; chunk 2.. thì ấm.")

print("\n== (B) closed-loop vs open-loop khi server đứng hình 1.0 s (GC/compile/migration) ==")
SERVICE = 0.100                                       # 100 ms/request bình thường
STALL_AT, STALL_LEN = 10.0, 1.0
def run(open_loop, duration=60.0, period=0.25):
    lat, t_free, t, nxt = [], 0.0, 0.0, 0.0
    while True:
        intended = nxt if open_loop else t           # open-loop: lịch gửi cố định, đo từ thời điểm DỰ ĐỊNH
        if intended > duration: break
        start = max(intended, t_free)
        if STALL_AT <= start < STALL_AT + STALL_LEN:
            start = STALL_AT + STALL_LEN
        done = start + SERVICE
        lat.append(done - intended)
        t_free = done
        t = done + 0.15 if not open_loop else t      # closed-loop: nghỉ 150 ms sau phản hồi rồi gửi tiếp
        nxt += period
    return lat
for name, ol in (("closed-loop", False), ("open-loop (đo từ lịch dự định)", True)):
    xs = run(ol)
    print(f"{name:32s} n={len(xs):4d} P50={pct(xs,.5)*1000:5.0f} ms P95={pct(xs,.95)*1000:5.0f} ms P99={pct(xs,.99)*1000:5.0f} ms max={max(xs)*1000:5.0f} ms")
```

Output:

```text
== (A) TTFA theo khoảng rảnh trước request ==
benchmark liên tục           P50= 118 ms  P95= 131 ms  P99= 137 ms
hội thoại (rảnh 6-20 s)      P50= 404 ms  P95= 452 ms  P99= 471 ms
lượt nhiều chunk (75% warm)  P50= 122 ms  P95= 427 ms  P99= 456 ms
-> chunk đầu của mỗi lượt gặp GPU 'nguội' nếu lượt trước cách > 2 s; chunk 2.. thì ấm.

== (B) closed-loop vs open-loop khi server đứng hình 1.0 s (GC/compile/migration) ==
closed-loop                      n= 237 P50=  100 ms P95=  100 ms P99=  100 ms max= 1100 ms
open-loop (đo từ lịch dự định)   n= 241 P50=  100 ms P95=  100 ms P99=  800 ms max= 1100 ms
```

### Script 4: join theo ID, v2v không đồng bộ đồng hồ, sai số offset (`trace_join.py`)

```python
# Chương 20 — Script 4: join log theo ID, đo v2v không cần đồng bộ đồng hồ, và sai số của ước lượng offset kiểu NTP.
import json, random
random.seed(4)

# ---------- (A) Log của một phiên có reopen: rev0 bị huỷ, rev1 hoàn tất ----------
# Mỗi sự kiện: (host, t_ms đơn điệu của host đó, event, ids...). Thời gian server dùng đồng hồ server, client dùng đồng hồ client.
SRV = 1_000_000          # gốc đồng hồ server (ms); client có gốc khác
events = [
 # turn 3 rev 0: user ngập ngừng -> soft_end -> speculative response bắt đầu -> user nói tiếp -> bị huỷ
 dict(h="srv", t=SRV+0,    e="vad.speech_end",   turn=3, rev=0, sample=480_000),
 dict(h="srv", t=SRV+250,  e="turn.soft_end",    turn=3, rev=0),
 dict(h="srv", t=SRV+470,  e="llm.first_clause", turn=3, rev=0, gen=11),
 dict(h="srv", t=SRV+600,  e="response.cancel",  turn=3, rev=0, gen=11, why="user_resumed"),
 # rev 1: user nói thêm, mẫu speech cuối mới
 dict(h="srv", t=SRV+2400, e="vad.speech_end",   turn=3, rev=1, sample=520_000),
 dict(h="srv", t=SRV+2650, e="turn.soft_end",    turn=3, rev=1),
 dict(h="srv", t=SRV+3450, e="turn.commit",      turn=3, rev=1),            # hold 800 ms
 dict(h="srv", t=SRV+3600, e="llm.first_clause", turn=3, rev=1, gen=12),
 dict(h="srv", t=SRV+3720, e="tts.first_byte",   turn=3, rev=1, gen=12, chunk=0),
]
print("== (A) Join theo (turn, rev, gen) ==")
by = {}
for ev in events:
    by.setdefault((ev["turn"], ev["rev"]), []).append(ev)
def get(evs, name):
    return next((e for e in evs if e["e"] == name), None)
for key, evs in by.items():
    end, fa = get(evs, "vad.speech_end"), get(evs, "tts.first_byte")
    canc = get(evs, "response.cancel")
    status = "cancelled" if canc else ("completed" if fa else "no-audio")
    v = f"{fa['t'] - end['t']} ms" if fa else "—"
    print(f"turn={key[0]} rev={key[1]} status={status:9s} speech_end→first_audio={v}")
# Sai lầm hay gặp: ghép "speech_end đầu tiên của turn" với "first_audio cuối cùng"
naive = get(events, "tts.first_byte")["t"] - events[0]["t"]
print(f"Join ngây thơ (speech_end đầu của turn → first audio): {naive} ms  (sai: gồm cả thời gian user nói tiếp)")

# ---------- (B) v2v đo hoàn toàn trên đồng hồ client, không cần đồng bộ ----------
print("\n== (B) v2v bằng chỉ số mẫu (không cần đồng bộ đồng hồ) ==")
FS = 48_000
cap_ref_ms, cap_ref_frame = 77_000.0, 0                  # ánh xạ capture của client: frame 0 ↔ performance.now()=77000 ms
last_speech_sample = 520_000                              # server gửi trong turn.commit (chỉ số mẫu, rate của client)
t_last_speech_client = cap_ref_ms + (last_speech_sample - cap_ref_frame) / FS * 1000
first_sample_rendered_client = cap_ref_ms + 10_833.3 + 1_180 + 0.0   # ghi bởi worklet, cùng đồng hồ client
OUTLAT = 22.0
heard = first_sample_rendered_client + OUTLAT
print(f"mẫu speech cuối ↔ t_client = {t_last_speech_client:.1f} ms; mẫu đầu được render = {first_sample_rendered_client:.1f} ms; nghe được ≈ {heard:.1f} ms")
print(f"v2v_client = {heard - t_last_speech_client:.1f} ms (không dùng đồng hồ server)")

# ---------- (C) Ước lượng offset kiểu NTP và sai số do bất đối xứng ----------
print("\n== (C) Offset đồng hồ client-server bằng ping: sai số tối đa = |d_up − d_down|/2 ==")
def estimate(true_offset, d_up, d_down, jitter=1.0):
    t0 = 0.0                                              # client gửi
    t1 = t0 + d_up + true_offset + random.uniform(0, jitter)      # server nhận (đồng hồ server)
    t2 = t1 + 0.3                                          # server trả
    t3 = (t2 - true_offset) + d_down + random.uniform(0, jitter)  # client nhận
    return ((t1 - t0) + (t2 - t3)) / 2
TRUE = 12_345.0
print(f"{'d_up':>5s} {'d_down':>7s} {'offset ước':>11s} {'sai số':>8s} {'tối đa lý thuyết':>17s}")
for d_up, d_down in ((20, 20), (20, 28), (10, 60), (5, 120)):
    est = sum(estimate(TRUE, d_up, d_down) for _ in range(200)) / 200
    print(f"{d_up:5d} {d_down:7d} {est:11.1f} {est - TRUE:8.1f} {abs(d_up - d_down) / 2:17.1f}")
```

Output:

```text
== (A) Join theo (turn, rev, gen) ==
turn=3 rev=0 status=cancelled speech_end→first_audio=—
turn=3 rev=1 status=completed speech_end→first_audio=1320 ms
Join ngây thơ (speech_end đầu của turn → first audio): 3720 ms  (sai: gồm cả thời gian user nói tiếp)

== (B) v2v bằng chỉ số mẫu (không cần đồng bộ đồng hồ) ==
mẫu speech cuối ↔ t_client = 87833.3 ms; mẫu đầu được render = 89013.3 ms; nghe được ≈ 89035.3 ms
v2v_client = 1202.0 ms (không dùng đồng hồ server)

== (C) Offset đồng hồ client-server bằng ping: sai số tối đa = |d_up − d_down|/2 ==
 d_up  d_down  offset ước   sai số  tối đa lý thuyết
   20      20     12345.0      0.0               0.0
   20      28     12341.0     -4.0               4.0
   10      60     12320.0    -25.0              25.0
    5     120     12287.5    -57.5              57.5
```

Lưu ý: phần (B) là phép tính minh hoạ, mốc render được dựng từ số giả định nên chỉ kiểm tra công thức ánh xạ chỉ số mẫu → đồng hồ client, không phải phép đo.

### Script 5: A/B ghép cặp và bootstrap (`ab_bootstrap.py`)

```python
# Chương 20 — Script 5: A/B có cặp (cùng audio) và khoảng tin cậy bootstrap cho hiệu P50 / P95.
# Giả định: B nhanh hơn A khoảng 8% ở thân phân phối và ít đuôi hơn; nhiễu theo lượt là chung cho cả hai (cùng audio, cùng điều kiện).
import math, random
random.seed(5)
def pct(xs, q):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(q * len(xs)))]
def gen(n):
    A, B = [], []
    for _ in range(n):
        turn = math.exp(random.gauss(math.log(900), 0.25))          # độ khó của lượt (độ dài câu, nội dung): chung A và B
        a = turn * math.exp(random.gauss(0, 0.10))
        b = turn * 0.92 * math.exp(random.gauss(0, 0.10))
        A.append(a); B.append(b)
    return A, B
def boot(A, B, q, reps=2000):
    n, ds = len(A), []
    for _ in range(reps):
        idx = [random.randrange(n) for _ in range(n)]               # resample CẶP
        ds.append(pct([B[i] for i in idx], q) - pct([A[i] for i in idx], q))
    ds.sort(); return ds[int(.025 * reps)], ds[int(.975 * reps)]
print(f"{'n lượt':>7s} {'chỉ số':>6s} {'B − A (ms)':>11s} {'CI 95%':>20s}  kết luận")
for n in (30, 100, 400):
    A, B = gen(n)
    for q, name in ((.5, "P50"), (.95, "P95")):
        d = pct(B, q) - pct(A, q); lo, hi = boot(A, B, q)
        print(f"{n:7d} {name:>6s} {d:11.0f} [{lo:7.0f}, {hi:7.0f}]  {'phân biệt được' if hi < 0 or lo > 0 else 'CHƯA kết luận được'}")
```

Output:

```text
 n lượt chỉ số  B − A (ms)               CI 95%  kết luận
     30    P50         -30 [   -174,      69]  CHƯA kết luận được
     30    P95          25 [   -169,      38]  CHƯA kết luận được
    100    P50         -37 [   -103,      16]  CHƯA kết luận được
    100    P95         -63 [   -282,     119]  CHƯA kết luận được
    400    P50         -56 [    -82,     -34]  phân biệt được
    400    P95        -120 [   -185,     -23]  phân biệt được
```

### Liên kết sang chương khác

- Chương 6 (capture và playback): buffer thiết bị, pre-buffer, `outputLatency`, ba mốc client, v2v không cần đồng bộ (§6.10).
- Chương 8 (transport): RTT, jitter, WebSocket vs WebRTC, huỷ request.
- Chương 10 (VAD và endpointing): `min_silence`, hold, speculative reopen, Smart Turn, hai triết lý điều khiển lượt.
- Chương 11 (ASR): streaming, first partial, stable prefix, endpoint→final, RTF < 1 không có nghĩa là có text sớm.
- Chương 12 (LLM): TTFT, TTFC, underrun, prefix cache, tắt thinking, contention GPU.
- Chương 13 (TTS): TTFA, RTF ba nghĩa, lead, pre-buffer và underrun.
- Chương 16 (dataflow): timeline, đồng hồ, định danh để join.
- Chương 17 (turn-taking): time-to-silence và time-to-release, `generation_id`.
- Chương 18 (async): replay theo thời gian thực, jitter, ngân sách giữa hai `await`.
- Chương 19 (cầu text → speech): chunker là đòn bẩy TTFC, `inter_chunk_gap` trên critical path.
- Chương 21 (đánh giá): bộ audio, ground truth, false cutoff, release gate, nguyên tắc A/B.
- Chương 22 (runtime): `max_streams`, admission control, khoá xung GPU, capacity theo concurrency.

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) — §3 nguyên tắc 6 (không cộng con số khác loại; ví dụ ASR chunk size, TTFT 92 ms, TTFA 115 ms, RTF batch); §8.1 (critical path sáu mốc, output gate, công thức `v2v ≈ … + max(output-hold, ASR + LLM) + …`, output-hold 800 ms/2 s mặc định HF s2s, chunker ở consumer, join theo `turn_id/revision/generation_id/chunk_id`); §8.2 (bảng ngân sách, ghi rõ không phải target, tổng các dải của blueprint 0,95–2,9 s, speech pipeline không cam kết ~1 s khi chưa biết endpoint LLM); §8.3 (đòn bẩy: warm-up, prefix cache, `asyncio.to_thread`, preemptive ASR+LLM, clause chunking, playback buffer); §8.4 (metric theo turn, gate TTS khởi điểm TTFA P95 ~250–400 ms, RTF P95 ≤ 0,7); §10 (nguyên tắc A/B).
[^stack]: [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md) — "Latency budget (report estimates)" (bảng: network 30–80, VAD 200–300 ms với Pipecat `stop_secs=0.2`, Smart Turn 10–65, ASR 100–300, LLM TTFT + chunk 150–350, TTS TTFA 64–300, v2v ~0,7–1,2 s, "must be measured on real hardware"); gạch đầu dòng tối ưu (warm-up, prefix caching, `asyncio.to_thread`, preemptive ASR+LLM); "Deployment tiers" gạch Monitoring (metric per-turn `vad_end→asr_done`, `asr_done→llm_first_token`, `first_sentence→tts_first_byte`, v2v client); "ASR primary-source corrections" (TTFT 92 ms ở concurrency 1 vs 3210/6195 ms ở 128, không phải latency từ mic). Nguồn gốc là report AI thứ cấp, **Reported**.
[^blueprint]: [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md) — "Latency budget" (bảng VAD 400–600, Whisper 200–700, Qwen3 first token 100–500, tách câu 100–400, TTS first audio 100–500, network 50–200; mục tiêu 1–2 s; các dải cộng thành khoảng 0,95–2,9 s là diễn giải **Synthesis** của wiki); "Turn flow and defaults" (sentence-buffered TTS là tối ưu quan trọng nhất).
[^s2slat]: [Speech-to-Speech Response Latency Instrumentation](../wiki/speech-to-speech-latency-instrumentation.md) — "Recording and transport" (dòng log mẫu, `response_key`, JSON schema version 2 và danh sách khoá, khoá bị bỏ, đơn vị và độ chính xác, giới hạn 512 ký tự/16 slot, response bị bỏ không có bản ghi); "Stage definitions" (`stt`, `llm`, `tts_ttfa`, `e2e`, `vad_decision_s`, `smart_status`, `hold_s`; các stage chồng lấn không cộng; thời gian remote gồm mạng); "Coverage matrix" (backend STT/LLM/TTS; tool follow-up); "Coverage and limits" (chỉ định nghĩa, không có số liệu, chưa chạy server). **Reported**.
[^s2s]: [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md) — "Endpointing and turn-taking" (gạch `--min_silence_ms` 64 ms mặc định, `--speculative_reopen_ms` 800 ms; Smart Turn: lượt complete bắt đầu STT/LLM ngay và dùng grace 800 ms trước khi commit output, lượt incomplete chờ `--smart_turn_incomplete_delay_ms` 600 ms, output bị giữ bởi `--smart_turn_max_wait_ms` 2 s); mục logging latency (gạch trỏ tới trang instrumentation). **Reported**.
[^vieneu]: [VieNeu-TTS Streaming Runtime and Performance](../wiki/vieneu-tts-streaming-runtime.md) — "Three numbers: TTFA, RTF, lead" (định nghĩa, lead +80/+320 ms, pre-buffer 150–300 ms, frame 80 ms); "GPU: measurements on an RTX 3060" (bảng `max_streams` 8/16/32 × N, request mới giữa các stream, bảng HTTP, 40 client 16 slot + 16 queue, 8 × `429`, TTFA queue 1,5–3 s, đoạn "cold GPU" 118 vs 403 ms và cách chữa); "Choosing `max_streams`" (slot dư làm chậm mọi request, streams ≠ users, 45–80 user); "CPU: how streaming works, measurements" (bảng fp32/int8 TTFA theo 27/88/147 ký tự, RTF, hai request cùng lúc RTF 1,19). Một máy, một ngày (2026-09-15), **Reported**; chưa chạy lại.
[^qwen]: [Qwen3-ASR family](../wiki/qwen3-asr-family.md) — gạch §2.4/Table 2 (TTFT 0.6B concurrency 1: 92/105 ms avg/P95; concurrency 128: 3210/6195 ms; thông lượng 2000 audio-s/s; input ~2 phút; phần cứng chỉ là "single typical computing resource"; "online async with complete inputs is not microphone streaming latency", diễn giải **Synthesis**).
[^nemotron]: [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md) — "Five runtime chunk sizes" (80/160/320/560/1120 ms), bảng WER theo chunk (13,41 → 11,18 FLEURS-vi, trích qua Chương 11), phần throughput H100 (240 vs 14 stream ở 80 ms; 2400 vs 400 ở 1120 ms; "median final-token latency at a given concurrency"); ghi chú "Chunk size is not total stable-text or endpoint→final latency". **Reported**.
[^eou]: [Parakeet Realtime EOU 120M v1](../wiki/parakeet-realtime-eou-120m-v1.md) — mô tả (80–160 ms ASR latency); gạch EOU latency (P50 160, P90 280, P95 320 ms; đánh giá trên audio TTS-generated DialogStudio có 3 s im lặng nối thêm; cảnh báo thực tế biến thiên). **Reported**.
[^smart]: [Smart Turn](../wiki/smart-turn.md) — gạch "Latency claims" (10 ms trên một số CPU, dưới 100 ms trên hầu hết cloud, ~65 ms Pipecat Cloud 1x với `LocalSmartTurnAnalyzerV3`); "Coverage and limits" (số của vendor, chưa kiểm chứng). **Reported**.
[^survey]: [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md) — dòng bảng Parakeet TDT 0.6B V2 (RTFx 3380 ở batch 128). **Reported**, mốc đo (batch lớn) theo model card.

---

## Áp dụng vào bản thiết kế: lưu ý và điểm quan trọng khi thiết kế, hiện thực

> Phần này ánh xạ nội dung Chương 20 vào [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md). Mọi nhận định ở đây là **Synthesis** của tác giả dựa trên các mục trong chương (đã dẫn nguồn ở trên) và các mục của bản thiết kế; số liệu nhắc lại giữ nguyên nhãn gốc (**Reported**/**Reproduced**). Chưa có gì được đo trên stack thật.

### A. Năm điều quan trọng nhất

1. **Chốt định nghĩa v2v trước khi viết dòng code đầu tiên.** Con số tiêu đề là D1 (đo ở client, từ mẫu speech cuối tới mẫu bot nghe được), phân rã đo ở server, join theo ID (§20.2.2). Nếu bắt đầu bằng HF s2s, `e2e` của nó là D2 (không gồm mạng, pre-buffer, playback) và **không** so được với `e2e` bản v1 (§20.2.1).
2. **Với cấu hình speculative của HF s2s, output-hold thường quyết định latency chứ không phải model.** Default 800 ms (complete) / tới 2 s (incomplete) lớn hơn ASR + LLM điển hình, nên v2v ước ≈ 1,4 s ở ví dụ §20.3.3, cao hơn dải 0,7–1,2 s của bảng ngân sách thiết kế §8.2 (bảng đó không có dòng hold, không có playback). Đừng hứa con số của §8.2.
3. **Xác định nhánh quyết định trước khi chọn đòn bẩy.** Đo tỉ lệ lượt gate-bound (§20.3.4). Nếu gate-bound: đổi ASR/LLM nhanh hơn cho 0 ms; đòn bẩy là hold, TTS, pre-buffer, cold start (§20.9.1).
4. **Cold start thiết bị ăn vào chunk đầu của mọi lượt.** GPU hạ xung sau ~2 s rảnh; trong hội thoại, chunk đầu của lượt luôn sau khoảng rảnh > 2 s. VieNeu 118 → 403 ms (**Reported**). `warm_fused()` ở thiết kế §5.6 chỉ giải quyết CUDA graph, không giải quyết xung; phải khoá xung ở host (§20.6.4).
5. **Đo bằng phân phối có điều kiện, không bằng một số.** P50/P95/P99 kèm n, tách theo loại lượt, độ dài, warm/cold, concurrency; không dựng P95 tổng từ P95 từng stage (§20.6).

### B. Lưu ý theo từng mục của bản thiết kế

| Mục thiết kế | Lưu ý từ Chương 20 | Việc cần làm khi hiện thực |
|---|---|---|
| §3 nguyên tắc 6 | Mỗi con số phải có mốc đầu, mốc cuối, nơi đo (§20.4) | Trong code và dashboard, đặt tên metric theo cặp mốc (`speech_end→first_audible`), không đặt tên chung chung `latency` |
| §4 kiến trúc | Pre-buffer client và `outputLatency` nằm trực tiếp trên critical path (§20.2.3) | AudioWorklet ghi `currentFrame` của mẫu đầu được render; báo `prebuffer_wait_ms` riêng |
| §5.3 hai triết lý endpoint | "Commit cứng sau timeout" và "speculative + hold" cho v2v khác nhau, nhưng speculative không tự động nhanh hơn; giá trị của nó là giảm false cutoff ở cùng mức im lặng (§20.3.3 điểm 2) | So hai triết lý bằng **cặp** chỉ số: v2v P50/P95 và tỉ lệ cắt nhầm; không so chỉ v2v |
| §5.4 ASR / Profile A | Turn-final: endpoint→final tăng theo độ dài lượt (§20.4.5) | Báo cáo theo bucket độ dài lượt (ví dụ < 3 s, 3–8 s, > 8 s) |
| §5.4 ASR / Profile B | Chunk 160–320 ms là cận dưới, không phải latency ra text; streaming ASR không vượt qua output gate (§20.3.2) | Chỉ chọn B vì lý do latency khi đã đo được lượt **compute-bound**; nếu không, lý do chọn B là caption/speculation |
| Profile D two-pass | Final-pass nằm trên nhánh compute; nếu còn slack dưới hold thì không làm tăng v2v (suy từ §20.3.4), nhưng vẫn gây contention GPU | Đo slack trước khi bật D; đo TTFA/TTFC khi final-pass chạy chồng lấn |
| §5.5 chunker | Chunker đổi số hạng TTFC, không đổi TTFT; chunk đầu ngắn giảm TTFA vì TTFA VieNeu tăng theo số ký tự (§20.4.3, §20.4.4) | Ghi mốc `llm.first_clause` (M7), đo `inter_chunk_gap` để bắt underrun do chunk đầu quá ngắn |
| §5.6 VieNeu | Có ba RTF khác nhau (bulk, một câu, streaming); TTFA tăng mạnh khi N request bắt đầu cùng lúc; slot dư làm chậm mọi request (§20.4.5, §20.6.5) | Đặt `VIENEU_MAX_STREAMS` theo số stream **đồng thời** đo được, không theo số user; theo dõi tỉ lệ `429` |
| §5.7 HF s2s instrumentation | `llm` của HF là toàn bộ thời gian sinh, không phải TTFT/TTFC; response bị bỏ không có bản ghi (§20.7.4, §20.7.5) | Bổ sung mốc M6/M7 và bản ghi cho response `cancelled`/`failed`; kiểm tra backend STT đang dùng có nằm trong coverage của `stt` không |
| §7.2 event schema | Schema chưa có thời điểm và chỉ số mẫu; không có `status` của response (§20.7.1, §20.7.2) | Thêm `t_mono_ns` cho mọi event, `speech_end_sample` trong `turn.commit`, `status` trong bản ghi kết thúc response; giữ `audio.played` làm nguồn cho M11 |
| §7.3 barge-in | Time-to-silence là một latency riêng, cũng phải đo ở client (§20.7.7) | Đo `user_speech_start→bot_audio_stopped` ở client và `→compute_released` ở server |
| §8.1 công thức gate | Có biến thể TTS speculative (TTS lọt vào trong `max`, §20.3.2) | Chỉ cân nhắc TTS speculative sau khi đo được tỉ lệ gate-bound cao; phải huỷ được audio đã sinh khi reopen |
| §8.2 ngân sách | Không phải target; cộng thử ra 554–1395 ms và 950–2900 ms (§20.5.2) | Đo baseline trước, rồi mới phân bổ mục tiêu theo **nhánh** (gate, compute, TTS, transport), không chia đều cho stage (§20.5.4) |
| §8.3 đòn bẩy | Mỗi đòn bẩy tác động lên một số hạng và có giá (bảng §20.9.2) | Thêm "khoá xung GPU ở host" và "`max_streams` đúng tải" vào danh sách; xem pre-buffer là tham số phải tune theo lead/jitter đo được |
| §8.4 monitoring | `asr_done→llm_first_token` là TTFT, chưa phải TTFC; câu xác nhận ngắn làm đẹp TTFA mà không đổi thời điểm có nội dung (§20.9.3) | Bổ sung: tỉ lệ gate-bound, slack, `ttfa_any` và `ttfa_content`, `underrun_count`, `prebuffer_wait_ms`, tỉ lệ `429` |
| §9.1 topology | Readiness chỉ sau warm-up, nhưng warm-up lúc khởi động không chống được hạ xung khi rảnh (§20.6.4) | Khoá xung GPU (`nvidia-smi -lgc`, `-pm 1`) là việc của host/Docker, đưa vào runbook triển khai |
| §9.5 privacy | Bản ghi latency chỉ cần độ dài, không cần nội dung (§20.7.4) | Log `n_chars`, `n_tokens`, `n_samples`; không log transcript |
| §10 gate 4 (tải) | Concurrency 1/4/8/16 phải đo cả kiểu đến "cùng lúc" và "rải rác"; closed-loop che mất stall (§20.6.5, §20.6.6) | Harness open-loop, replay audio theo thời gian thực, có khoảng rảnh thật giữa lượt; báo đường cong latency–concurrency |
| §12 lộ trình | Mỗi lần đổi một thành phần (§10 thiết kế) chưa đủ để kết luận latency (§20.8.2) | A/B ghép cặp theo file, xen kẽ, bootstrap CI; cải thiện vài chục ms cần hàng trăm lượt |

### C. Checklist instrumentation cho Phase 1 (MVP)

Nên có ngay từ ngày đầu, vì thêm sau sẽ mất baseline:

- [ ] Đồng hồ đơn điệu ở mọi host (`time.perf_counter_ns()`, `performance.now()`); mốc audio dùng chỉ số mẫu.
- [ ] Tập mốc M1–M12 (§20.7.1), mỗi event mang `session_id`, `turn_id`, `revision`, `generation_id`, `chunk_id`.
- [ ] Client tự tính v2v (D1) từ `speech_end_sample` do server gửi, không cần đồng bộ đồng hồ (§20.7.3).
- [ ] Ghi log ra hàng đợi, không ghi đồng bộ trên thread audio hay event loop.
- [ ] Bản ghi cho mọi response, kể cả `cancelled`/`failed`.
- [ ] Waterfall theo turn hiển thị hai nhánh gate và compute.
- [ ] Bộ audio cố định có annotation speech-end (để đo D0 bằng black-box harness, §20.7.6) dùng lại cho mọi A/B.

### D. Những sai lầm dễ gặp khi hiện thực

| Sai lầm | Hậu quả | Cách tránh |
|---|---|---|
| Báo "TTFA 115 ms" hoặc "TTFT 92 ms" làm latency hệ thống | Kỳ vọng sai hàng trăm ms | Chỉ báo D1 làm con số tiêu đề |
| Benchmark bằng vòng lặp liên tục | Bỏ sót cold GPU, số đẹp gấp ~3 lần thực tế | Mô phỏng khoảng rảnh 6–20 s; báo riêng chunk đầu của lượt |
| Join log theo thứ tự lượt khi có reopen | v2v bị thổi phồng (1320 → 3720 ms trong Script 4A) | Join theo `(turn_id, revision, generation_id)` |
| Chỉ phân tích response hoàn tất | Bỏ sót lượt barge-in/reopen | Ghi và phân tích riêng theo `status` |
| Đổi ASR/LLM để "giảm latency" khi đang gate-bound | Tốn công, v2v không đổi | Đo slack trước |
| Hạ `min_silence` hoặc hold mà không đo false cutoff | Nhanh hơn nhưng cắt lời user | Luôn báo kèm tỉ lệ cắt nhầm |
| Đặt `max_streams` theo số user | Mọi request chậm thêm do slot dư | Đặt theo số stream đồng thời đo được |
| Pre-buffer cố định lấy từ demo | Hoặc thêm hàng trăm ms, hoặc underrun | Tune theo lead và jitter đo được trên mạng thật |
