# Chương 19. Cầu text → speech: chunker, normalizer, lexicon 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần V (Ghép pipeline). Đây là chương cuối của Phần V.
> **Chương trước:** [Chương 18. Lập trình async và streaming cho pipeline audio](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md). **Chương tiếp theo:** Chương 20. Latency: định nghĩa, critical path, đo lường.
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.5 (giao diện LLM, chunker, normalizer, lexicon, hai nghĩa của "streaming TTS"), §7.2 (`text.chunk(generation_id, chunk_id, raw_text, spoken_text)`), §7.3 (history chỉ lưu phần đã phát), §8.1 (chunker nằm ở consumer của LLM stream), §8.3 (clause chunking là đòn bẩy latency), §10 mục 2 (test normalizer, lexicon và ranh giới chunk).
> **Cơ sở:** sentence segmentation, text normalization theo semiotic class, lexicon/respelling, property-based testing là **kiến thức nền chung** về xử lý văn bản cho TTS, không phải claim lấy từ nguồn wiki. Quy tắc đọc số tiếng Việt dùng lại [Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.8–5.9; chương này **không** lặp lại bảng semiotic class và G2P mà đi vào phần kỹ thuật: chạy theo luồng, giữ alignment, quản trị lexicon, kiểm thử. Hành vi của các hệ cụ thể lấy từ wiki và gắn nhãn bằng chứng: [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md), [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md), [Community STT-LLM-TTS Wiring](../wiki/community-stt-llm-tts-pipeline.md), [VietNormalizer](../wiki/vietnormalizer.md), [ViSoNorm](../wiki/visonorm-visobert-normalizer.md), [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md), [VieNeu OpenAI Speech API](../wiki/vieneu-tts-openai-speech-api.md), [VieNeu Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md), [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md), [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md), [Speech-to-Speech CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md), [CosyVoice2-0.5B](../wiki/cosyvoice2-0.5b.md), [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md). Thông tin vendor là **Reported** (wiki chưa chạy lại). Bốn script ở "Phụ lục chương" chạy bằng Python 3.12.3 thuần (không thư viện ngoài) ngày 2026-10-12 trên Intel i7-1255U: **Reproduced** cho hành vi của chính mã minh hoạ (chunker, normalizer, lexicon, mô phỏng). Mô phỏng latency dùng tham số **giả định**, không gọi LLM hay TTS thật. Thiết kế và suy luận của tác giả là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Vẽ được vị trí của cầu text → speech giữa LLM stream và TTS, biết nó nhận gì, trả gì, và **không** chịu trách nhiệm việc gì.
2. Chọn được đơn vị flush (token, mệnh đề, câu, cả câu trả lời) bằng lập luận định lượng: TTFA, khe im lặng giữa chunk (underrun), số request, prosody.
3. Viết được một **clause chunker chạy theo luồng** cho tiếng Việt: không cắt giữa số, viết tắt, URL; gộp mảnh ngắn; có trần độ dài; cho kết quả **không phụ thuộc cách LLM chia token**.
4. Giải thích và hiện thực việc tách **`display_text`** (hiển thị, lưu history) khỏi **`spoken_text`** (đưa vào TTS), kèm alignment đủ để cắt history khi bị ngắt lời.
5. Thiết kế normalizer tiếng Việt chạy theo từng chunk: thứ tự luật, chính sách cho ca mơ hồ, cảnh báo thay vì "tự sửa", tham số vùng miền.
6. Thiết kế lexicon hai pha (bảo vệ thực thể trước TN, respelling sau TN), quy tắc khớp, quản trị phiên bản; biết khi nào lexicon **không** cứu được lỗi phát âm.
7. Ra quyết định code-switch Việt–Anh theo năng lực của TTS, và tránh định tuyến ngôn ngữ theo từng chunk.
8. Xây được bộ regression ba tầng (normalizer golden, thuộc tính chunker, tập nghe TTS) và các metric vận hành cho tầng này.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Flush theo token, theo mệnh đề hay theo câu? Mỗi cách đánh đổi gì?
- Q2. Vì sao phải tách text hiển thị và text để đọc?
- Q3. Normalizer tiếng Việt xử lý số, tiền, ngày, viết tắt, code-switch thế nào?
- Q4. Vì sao chunker phải "nhìn thêm một ký tự" sau dấu câu rồi mới cắt? Chunker ngây thơ làm hỏng gì?
- Q5. Normalizer chạy trước hay sau chunker? Vì sao?
- Q6. Lexicon đặt ở đâu so với normalizer? Khi nào respelling không cứu được lỗi phát âm?
- Q7. LLM sinh chậm làm bot im giữa hai mệnh đề. Chỉnh chunker thế nào, và phải trả giá gì?
- Q8. Làm sao biết một thay đổi luật normalizer không làm hỏng ca khác?

---

## 19.1 Bức tranh: cầu nằm ở đâu và làm gì

[Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) coi LLM là một streaming text service có thể huỷ. [Chương 13](chuong-13-tts-tu-van-ban-toi-waveform.md) coi TTS là một service nhận text hoàn chỉnh và trả audio theo chunk. Giữa hai thứ đó là một khoảng trống: LLM nhả **token**, còn TTS cần **câu đọc được**. Tầng lấp khoảng trống đó là cầu text → speech.

```text
 LLM (SSE)                          CẦU TEXT → SPEECH (một instance cho mỗi generation_id)                          TTS
 ─────────                          ───────────────────────────────────────────────────────                         ───
 delta, delta, …, done ──► ThinkFilter ──► ClauseChunker ──► raw_text ──► pre-lexicon ──► Normalizer ──► post-lexicon ──► spoken_text ──► TTS adapter
                                              │ T2 text.chunk                                   │                    │ T3
                                              │                                                 ▼                    ▼
                                              └──────────────────────────────────────► display_text  (caption, history, log)
                                                                                         + segments (alignment raw ↔ spoken)
```

T2, T3 là tên cạnh trong bảng audio contract của [Chương 16](chuong-16-dataflow-end-to-end-va-audio-contract.md) §16.3.3. Tài liệu thiết kế §7.2 định nghĩa event `text.chunk(generation_id, chunk_id, raw_text, spoken_text)` (**Synthesis** của thiết kế).[^design] Chương này thêm `display_text`, `segments` và `warnings`.

| Cầu **làm** | Cầu **không làm** |
|---|---|
| Cắt luồng token thành mệnh đề đọc được | Quyết định lượt, commit, cancel. Owner ở [Chương 17](chuong-17-turn-taking-event-barge-in-va-cancellation.md) làm |
| Lọc phần không được đọc (`<think>`, markdown, emoji, URL) | Sửa nội dung câu trả lời. Số sai, ngày sai vẫn đọc đúng như LLM viết, chỉ ghi cảnh báo |
| Chuyển dạng viết thành dạng nói (TN), áp lexicon | G2P bên trong TTS. TTS có frontend riêng (VieNeu dùng `sea-g2p`, Kokoro Vietnamese dùng `vig2p`; **Reported**)[^vieneu][^kokoro] |
| Giữ alignment raw ↔ spoken để cắt history | Đo played offset. Client đo ([Chương 16](chuong-16-dataflow-end-to-end-va-audio-contract.md) §16.6.4) |
| Bỏ toàn bộ buffer khi generation bị huỷ | Huỷ request TTS. Runtime làm ([Chương 18](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md) §18.4.6) |

Ba nguyên tắc xuyên suốt chương:

1. **Chunker nằm ở consumer của LLM stream.** Chia câu sau khi đã có cả câu trả lời không lấy lại được thời gian chờ LLM (**Synthesis**, thiết kế §8.1).[^design]
2. **Text gốc là nguồn sự thật, text đọc là bản dẫn xuất.** Mọi thứ người dùng *nhìn* và mọi thứ ghi vào history là `display_text`. Chỉ TTS nhận `spoken_text`.
3. **Normalizer không đoán ý.** Gặp chỗ mơ hồ hay sai, nó chọn một cách đọc có quy ước, ghi `warnings`, rồi để prompt LLM hoặc lexicon sửa ở gốc.

---

## 19.2 Vì sao cần cầu: TTS không nhận token

### 19.2.1 Hai nghĩa của "streaming TTS"

Thiết kế §5.5 phân biệt (**Synthesis**):[^design]

- **Audio-output streaming:** TTS nhận text hoàn chỉnh, trả audio dần. VieNeu `infer_stream` và VoxCPM2 `generate_streaming` thuộc loại này.
- **Incremental text-input (bi-streaming):** TTS nhận token dần trong khi đang nói. Chưa có ứng viên tiếng Việt nào trong wiki làm được.

Ngay cả TTS có bi-streaming cũng không bỏ được việc chia câu. Model card CosyVoice2 ghi chú rằng khi dùng chế độ bi-streaming (đưa generator text vào), người gọi vẫn nên giữ logic chia câu cơ bản vì LLM của TTS không xử lý được câu dài tuỳ ý (**Reported**).[^cosy]

Phía VieNeu, endpoint `POST /v1/audio/speech` nhận tối đa 20.000 ký tự và **tự chia** `input` thành các đoạn ≤ `max_chars` (mặc định 256, cho phép 64–512) ở ranh giới câu (**Reported**).[^vieneuapi] Gửi cả câu trả lời một lần thì server chia hộ, nhưng bạn đã phải chờ LLM sinh xong. Cầu text → speech tồn tại để **không phải chờ**.

### 19.2.2 Ba lực kéo ngược nhau

| Lực | Muốn chunk… | Vì sao |
|---|---|---|
| TTFA của cả hệ | **ngắn** (chunk đầu) | Chunk đầu sẵn sàng sớm hơn, TTS bắt đầu sớm hơn |
| Prosody | **dài**, cắt ở ranh giới tự nhiên | TTS dạng AR/codec quyết định ngữ điệu theo context đã thấy và dấu câu ([Chương 13](chuong-13-tts-tu-van-ban-toi-waveform.md) §13.6) |
| Chi phí và độ ổn định | **ít request** | Mỗi request trả lại prefill, lead-in, im lặng đầu/cuối, một lần xếp hàng slot và một lần rủi ro `429` |

Blueprint gọi việc không chờ LLM xong mới chạy TTS là tối ưu quan trọng nhất, và loại bỏ per-token TTS vì prosody gãy, TTS thiếu context, số request bùng nổ, khe hở nghe được. Đơn vị tốt thường là một câu hoặc khoảng 20–60 ký tự (**Reported**).[^blueprint] Thread cộng đồng minh hoạ bằng cặp `I want a...` và `I want a pizza right now!`: câu đầy đủ đầu tiên cho output thực hơn hẳn so với đọc từng từ (**Reported**).[^community]

---

## 19.3 Flush theo token, mệnh đề hay câu (Q1)

### 19.3.1 Năm chính sách

| Chính sách | Khi nào gửi TTS | Ví dụ trong hệ thật |
|---|---|---|
| `token` | Mỗi token (hoặc mỗi từ) | Bị wiki loại bỏ (**Reported**)[^blueprint] |
| `clause` | Ở `.?!…;:`/xuống dòng; chunk đầu cắt ở dấu phẩy khi ≥ ~25 ký tự; gộp mảnh < 8 ký tự | Quy tắc khởi điểm của thiết kế §5.5 (**Reported** từ report)[^design][^stack] |
| `sentence` | Chỉ ở ranh giới câu | Wyoming/Home Assistant được báo chia theo ranh giới câu (**Reported**)[^community] |
| `3sent` | Gom 3 câu mỗi lần | HF s2s có `stream_batch_sentences=3` mặc định, đặt `1` để stream từng câu (**Observed** trong capture CLI)[^cli] |
| `full` | Khi LLM `done` | Kiểu "chờ xong rồi đọc" |

### 19.3.2 Mô phỏng

Script 3 (Phụ lục) mô phỏng một câu trả lời 289 ký tự (≈ 93 âm tiết đọc, ≈ 18,6 s audio) qua chunker và normalizer thật của chương, với LLM và TTS **giả lập**. Tham số giả định: TTFT 300 ms; 1,5 token mỗi từ; giọng đọc 5 âm tiết/s; mỗi request TTS thêm 150 ms im lặng đầu/cuối. TTS "GPU" dùng TTFA 115 ms, RTF 0,49 (con số 1 stream của VieNeu trên RTX 3060, **Reported**).[^vieneurt] TTS "CPU int8" dùng TTFA = 131 + 0,42 × số ký tự (ms), RTF 0,35. Đường thẳng này nối ba điểm VieNeu báo cho câu 27/88/147 ký tự (~142/166/193 ms, **Reported**); việc khớp thành đường thẳng là **Synthesis**.[^vieneurt]

Kết quả (**Reproduced** cho mô hình đồ chơi, không phải đo hệ thật):

| Kịch bản | Chính sách | #request | Audio đầu | Gap lớn nhất | Kết thúc |
|---|---|---|---|---|---|
| LLM 40 tok/s, TTS GPU | `token` | 66 | **415 ms** | 0 | **28,92 s** |
| | `clause` | 5 | **752 ms** | 0 | 20,10 s |
| | `sentence` | 4 | 1428 ms | 0 | 20,63 s |
| | `3sent` | 2 | 2515 ms | 0 | 21,42 s |
| | `full` | 1 | 2890 ms | 0 | 21,64 s |
| LLM 40 tok/s, TTS CPU int8 | `clause` | 5 | 785 ms | 0 | 20,14 s |
| | `sentence` | 4 | 1525 ms | 0 | 20,73 s |
| LLM **8 tok/s**, TTS CPU int8 | `clause` | 5 | 2135 ms | **1273 ms** | 22,76 s |
| | `sentence` | 4 | 5575 ms | 0 | 24,78 s |
| | `full` | 1 | 12972 ms | 0 | 31,72 s |

Đọc kết quả:

- **`token` nhanh nhất về âm thanh đầu nhưng tệ nhất về tổng thể.** Với 66 request, phần im lặng đầu/cuối giả định cộng thêm gần 9 s vào một câu trả lời 18,6 s. Mô phỏng chưa tính prosody gãy, thứ mà wiki coi là lý do chính để loại per-token. 66 request còn chiếm slot TTS gấp 13 lần so với `clause`.
- **`clause` so với `sentence`:** chênh khoảng 680–740 ms âm thanh đầu, chỉ nhờ cắt ở dấu phẩy sau "Dạ, em đã kiểm tra lịch bay cho anh rồi," (40 ký tự).
- **`3sent` và `full` mất 1,8–2,3 s.** Gom câu chỉ hợp lý khi TTS có chi phí mỗi request lớn hoặc khi cần prosody liền nhiều câu (đọc tin, đọc sách). Đây là mô phỏng chính sách gom 3 câu, **không** mô phỏng code HF s2s.
- **LLM chậm đổi bài toán.** Chunk đầu 40 ký tự chỉ cho khoảng 2 s audio, trong khi LLM ở 8 tok/s cần khoảng 3,4 s để sinh xong mệnh đề thứ hai dài 85 ký tự. Kết quả là khe im 1,27 s giữa câu. `sentence` không có khe nhưng âm thanh đầu đến sau 5,6 s.

### 19.3.3 Điều kiện không đứt tiếng

Gọi `ready(k)` là lúc chunker nhả chunk k, `wait(k)` là thời gian chờ slot TTS, `TTFA(k)` là độ trễ tới audio đầu của request đó, `end(k-1)` là lúc audio của chunk trước phát xong. Chunk k phát liền mạch khi:

```text
ready(k) + wait(k) + TTFA(k)  ≤  end(k-1)
```

Năm hệ quả (**Synthesis**):

1. **Chunk đầu ngắn có cái giá của nó.** Chunk 1 ngắn thì `end(1)` đến sớm, chunk 2 có ít thời gian hơn để sẵn sàng. Bẫy "Dạ," ở [Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.3.2 là dạng cực đoan của hệ quả này.
2. **Chênh lệch độ dài giữa các chunk mới gây đứt tiếng, tốc độ trung bình thì không.** Ở 8 tok/s, LLM vẫn sinh text nhanh hơn tốc độ đọc tính trung bình (số mở rộng thành nhiều âm tiết). Khe hở sinh ra vì một mệnh đề ngắn bị theo sau bởi một mệnh đề dài không có dấu phẩy nào để cắt.
3. **TTFA phụ thuộc độ dài chunk ít hơn bạn nghĩ.** Theo bảng CPU của VieNeu, câu 147 ký tự so với câu 27 ký tự chỉ thêm khoảng 50 ms ở int8 và 80–120 ms ở fp32 (**Reported**).[^vieneurt] Còn LLM 40 tok/s cần khoảng 1 s để sinh 120 ký tự đó (giả định 1,5 token/từ, ~4,4 ký tự/từ). Cắt chunk đầu ngắn có lợi chủ yếu vì **không phải chờ LLM**, không phải vì TTS prefill nhanh hơn.
4. **Slot thứ hai (prefetch) chỉ giúp khi chunk ngắn hoặc TTS chậm.** Trong mô phỏng, 1 slot và 2 slot cho kết quả giống hệt nhau ở mọi chính sách (xem output Script 3). Với RTF 0,35–0,49, TTS sinh xong chunk k từ lâu trước khi chunk k phát xong. Slot có giá: VieNeu khuyên đặt `max_streams` bằng tải đồng thời thật, vì mỗi slot dư làm chậm codec của mọi request; trên CPU fp32 server chỉ chạy đúng một stream và request thứ hai xếp hàng rồi nhận `429` khi hết thời gian chờ (**Reported**).[^vieneurt] Prefetch nhân đôi số slot một session giữ.
5. **Khi LLM chậm, có ba núm vặn, núm nào cũng trả giá:**
   - Trần độ dài cứng (`hard_max`). Với `hard_max=60`, khe giảm từ 1273 ms xuống 315 ms. Với `hard_max=45`, khe còn 0 ms (**Reproduced**, mô phỏng). Cái giá: cắt giữa mệnh đề. Ở `hard_max=60` chunker cắt thành "…từ Nội Bài và" / "đến Tân Sơn Nhất lúc 16:40.", tức là cắt **sau** liên từ, một ranh giới ngữ điệu xấu.
   - Giữ âm thanh đầu cho tới khi có 2 chunk (thêm TTFC để chống underrun, [Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.3.3).
   - Đổi LLM nhanh hơn hoặc yêu cầu trong prompt "câu ngắn" để có nhiều điểm cắt tự nhiên.

> **Quy tắc thực hành (Synthesis).** Nếu buộc phải cắt cứng, cắt **trước** liên từ (`và`, `nhưng`, `để`, `nếu`, `vì`, `thì`, `mà`) chứ không cắt sau, và chỉ bật khi đo thấy underrun thật. Đo `inter_chunk_gap` P95 theo từng tổ hợp LLM/TTS rồi mới tune; đừng tune từ con số của chương này.

---

## 19.4 Thiết kế clause chunker theo luồng (Q4)

### 19.4.1 Năm loại vị trí trong text

| Loại | Ví dụ | Hành động |
|---|---|---|
| Ranh giới cứng | `.` `?` `!` `…` `;` `:` theo sau bởi khoảng trắng; xuống dòng | Cắt (nếu đủ dài) |
| Ranh giới mềm | `,` theo sau bởi khoảng trắng | Cắt nếu chunk đã ≥ ngưỡng (25 ký tự cho chunk đầu, 80 cho các chunk sau) |
| Cấm cắt: dấu câu không theo sau bởi khoảng trắng | `1.250.000` · `3,5` · `14:30` · `TP.HCM` · `https://vd.vn` · `hotro@vd.vn` | Bỏ qua |
| Cấm cắt: viết tắt chức danh/địa danh | `TS. Nguyễn` · `Q. Ba Đình` · `PGS. Lan` | Bỏ qua (danh sách `ABBR_NOEND`) |
| Tuỳ ngữ cảnh | `v.v.` | Chỉ kết câu nếu ký tự không trắng kế tiếp là chữ hoa hoặc xuống dòng |

Quy tắc dòng 3 làm được việc của nhiều regex đặc thù nhờ một quan sát đơn giản: trong văn bản tiếng Việt, dấu câu **kết thúc mệnh đề** luôn theo sau bởi khoảng trắng; dấu chấm, phẩy, hai chấm **bên trong một giá trị** thì không.

### 19.4.2 Nguyên tắc "nhìn thêm một ký tự"

LLM có thể chia `1.250.000đ` thành `1`, `.`, `250`, `.`, `000`, `đ`. Nếu chunker cắt ngay khi thấy dấu `.` ở cuối buffer, nó sẽ gửi `Giá vé là 1.` cho TTS. Vì vậy:

> Một dấu câu ở **cuối buffer** chưa phải ranh giới. Chunker chỉ quyết định khi đã thấy ký tự **sau** nó (hoặc khi stream kết thúc).

Hệ quả quan trọng: đầu ra của chunker **không phụ thuộc cách LLM chia token**. Đây là một **thuộc tính kiểm thử được**. Script 1 chia ngẫu nhiên năm câu trả lời thành token 1–6 ký tự, mỗi câu 5000 lần, cộng thêm một lần chia từng ký tự. Kết quả: **0/5000** lần khác tham chiếu ở cả năm câu (**Reproduced**). Một chunker có quyết định phụ thuộc thời điểm token đến sẽ cho ra chunk khác nhau giữa các lần chạy với cùng một text. Bug dạng này gần như không tái hiện được trong log.

Độ trễ thêm vào là một token, tức vài chục ms ở tốc độ decode thông thường. Đó là cái giá rẻ cho tính đúng.

### 19.4.3 Chunker ngây thơ hỏng thế nào

Cùng ba câu trả lời, chunker ngây thơ (cắt ngay ở `.?!;:…`, không nhìn ký tự sau, không gộp) cho (**Reproduced**, Script 1 phần c):

```text
… tức khoảng 290. | 000đ mỗi tháng, … | Anh xem chi tiết tại https: | //vd. | vn/goi nhé!
Văn phòng ở 12 Lý Thái Tổ, Q. | 1, TP. | HCM. | Anh liên hệ TS. | Nguyễn Văn An qua số 0912. | 345. | 678 …
… nộp hồ sơ, v. | v. | Sau đó anh chờ khoảng 5-7 ngày làm việc. | . | . | Rồi bên em …
```

Mỗi vết cắt hỏng một giá trị: số tiền tách đôi rồi được normalizer đọc thành hai số riêng, số điện thoại thành ba mảnh, URL bị đọc từng phần, và mỗi mảnh là một request TTS với ngữ điệu kết câu. Chunker của chương cho (**Reproduced**, Script 1 phần a):

```text
[0] comma  38c | Dạ. Gói cước 4G giá 3,5 triệu một năm,
[1] term   49c | tức khoảng 290.000đ mỗi tháng, rẻ hơn gói cũ 15%.
[2] term   43c | Anh xem chi tiết tại https://vd.vn/goi nhé!

[0] comma  26c | Văn phòng ở 12 Lý Thái Tổ,
[1] term   12c | Q.1, TP.HCM.
[2] term   88c | Anh liên hệ TS. Nguyễn Văn An qua số 0912.345.678 hoặc email hotro@vd.vn để được hỗ trợ.
```

Chú ý hai chi tiết. Một, `Dạ.` dài 3 ký tự bị gộp vào mệnh đề sau theo luật "gộp mảnh < 8 ký tự", nên TTS không phải đọc một chữ "Dạ." trơ trọi rồi im chờ chunk 2. Hai, nội dung `<think>…</think>` ở đầu câu trả lời thứ hai đã bị ThinkFilter bỏ trước khi vào chunker, kể cả khi thẻ bị chia qua nhiều token.

### 19.4.4 Thuật toán

```text
state: buf, scan_from, n_emitted
feed(delta):  buf += delta; return drain(final=False)
flush():      return drain(final=True)

drain(final):
  loop:
    r = scan(buf từ scan_from)           # vị trí cắt đầu tiên đã CHẮC CHẮN, hoặc None nếu cần thêm ký tự
    if (r is None and len(buf) > hard_max) or (r and r.pos > hard_max):
        r = cắt ở khoảng trắng cuối cùng trong buf[:hard_max]
    if r is None: break
    text = buf[:r.pos].strip()
    if len(text) < min_len and not (final and phần còn lại rỗng):
        scan_from = r.pos; continue      # gộp mảnh ngắn: tìm ranh giới tiếp theo, chunk sẽ bao cả mảnh này
    emit(text, r.kind); buf = buf[r.pos:]; scan_from = 0; n_emitted += 1
  if final: emit phần còn lại
```

`scan` chạy trái sang phải và mọi quyết định chỉ dựa trên tiền tố của buffer cộng một ký tự nhìn trước (hai, với `v.v.`). Đó là lý do thuộc tính bất biến ở §19.4.2 đúng. Mã đầy đủ ở Phụ lục (`bridge.py`, lớp `ClauseChunker`).

### 19.4.5 Tham số và hướng tune

| Tham số | Mặc định | Nguồn | Tăng thì | Giảm thì |
|---|---|---|---|---|
| `first_min` (ngưỡng phẩy cho chunk đầu) | 25 ký tự | Thiết kế §5.5 (**Reported**)[^design] | Prosody chunk đầu tốt hơn, TTFA tăng | TTFA giảm, rủi ro chunk 2 không kịp |
| `later_comma_min` | 80 ký tự | Chương này (**Synthesis**) | Ít request, prosody liền | Nhiều điểm cắt, chống underrun khi LLM chậm |
| `min_len` (gộp mảnh) | 8 ký tự | Thiết kế §5.5 (**Reported**)[^design] | Ít mảnh lẻ | "Dạ.", "Vâng." thành chunk riêng |
| `hard_max` | 180 ký tự | Chương này (**Synthesis**) | Ít cắt cứng | Chống underrun, cắt giữa mệnh đề |
| Ranh giới `;:` | cắt | Thiết kế §5.5 | – | Có thể coi `:` là ranh giới mềm: "Có ba bước:" (11 ký tự) thành chunk riêng ở Script 1 |

Hai lưu ý về `hard_max`:

- Đặt `hard_max` nhỏ hơn `max_chars` của TTS (VieNeu mặc định 256, **Reported**)[^vieneuapi] để server không chia thêm lần nữa theo luật của nó. Khi đó bạn biết chính xác ranh giới nào TTS thấy (**Synthesis**).
- Log `kind` của mỗi chunk (`term`, `comma`, `newline`, `hard_max`, `final`). Nếu tỷ lệ `hard_max` cao, lỗi nằm ở prompt (LLM viết câu quá dài), không phải ở chunker.

### 19.4.6 Những chi tiết hay bị quên

- **Lọc trước khi chunk.** Khối `<think>` có dấu câu bên trong. Nếu lọc sau khi chunk, ranh giới đã sai. [Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.3.5 khuyên luôn đặt lớp lọc này dù đã tắt thinking. Tag `[bị ngắt]` mà LLM nhại lại từ history cũng cần lọc (**Synthesis**, Chương 12 §12.5.4).
- **Markdown cấu trúc.** Danh sách `1. Bước một` sinh ranh giới giả ở `1.`. Luật gộp mảnh ngắn che được trường hợp này, nhưng gốc rễ phải sửa ở prompt (không markdown, **Reported**).[^stack]
- **Stall của LLM.** Khi LLM dừng giữa chừng (gọi tool, quá tải), buffer có thể đang giữ nửa mệnh đề. Đừng flush theo timer ở vị trí bất kỳ. Nếu có timer, chỉ flush ở ranh giới mềm đã đủ `first_min`, và log `kind=idle` (**Synthesis**). Câu đệm kiểu "Dạ, để em kiểm tra" nên do ứng dụng phát chủ động, có ghi vào history, chứ không phải do chunker tự bịa.
- **Huỷ.** Khi `generation_id` đổi, bỏ cả chunker lẫn ThinkFilter của generation cũ. Đừng flush phần còn lại, vì `flush()` sẽ nhả một chunk cũ ra hàng đợi TTS.
- **Unicode.** Chunker nhận text đã NFC. Nếu cắt theo số ký tự trên text NFD, dấu thanh có thể rơi sang chunk sau ([Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.13). Script 1 cắt ở khoảng trắng nên không gặp, nhưng trần `hard_max` cắt theo ký tự nên phải NFC trước.

---

## 19.5 Text hiển thị và text để đọc (Q2)

### 19.5.1 Sáu lý do phải tách

| # | Nơi dùng | Cần dạng | Nếu chỉ có `spoken_text` thì |
|---|---|---|---|
| 1 | Caption, UI | `1.250.000đ`, `0912 345 678` | Người dùng đọc "một triệu hai trăm năm mươi nghìn đồng" trên màn hình |
| 2 | History gửi lại LLM | Dạng viết | LLM bắt chước, sinh số bằng chữ ở lượt sau; câu dài hơn, khó hiển thị |
| 3 | Cắt history khi bị ngắt | Dạng viết + alignment | Không biết user đã nghe tới đâu trong text gốc |
| 4 | Log, audit | Cả hai | Không phân biệt được lỗi của LLM (viết sai) với lỗi normalizer (đọc sai). [Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.4.6 tách hai loại lỗi này |
| 5 | Đánh giá TTS | `spoken_text` | Round-trip CER so ASR(audio) với text gốc thì số và viết tắt luôn bị tính là lỗi |
| 6 | Tool call, trích xuất entity | Dạng viết | Regex số điện thoại không chạy trên chữ |

Thiết kế §5.5 ghi "tách text hiển thị khỏi text để đọc" (**Reported** từ report).[^design][^stack] Thiết kế §7.3 yêu cầu chỉ lưu vào history **phần đã thực sự phát**, kèm tag `[bị ngắt]` (**Reported**).[^design] Hai yêu cầu này gặp nhau ở lý do 3.

### 19.5.2 Bản ghi của một chunk

Script 2 đưa một câu trả lời có markdown và emoji qua chunker rồi normalizer (**Reproduced**):

```json
{"chunk_id": 1,
 "raw_text":     "Giá vé là **1.250.000đ**, đã gồm thuế.",
 "display_text": "Giá vé là 1.250.000đ, đã gồm thuế.",
 "spoken_text":  "Giá vé là một triệu hai trăm năm mươi nghìn đồng, đã gồm thuế."}
```

Ba trường, ba vai trò:

- `raw_text` là đúng những gì LLM sinh. Dùng để debug và tái hiện.
- `display_text` là `raw_text` bỏ markup và emoji. Dùng cho caption và history.
- `spoken_text` là đầu vào TTS.

Ghi thêm `normalizer_version`, `lexicon_version`, `warnings` để biết một câu đọc sai do luật nào, phiên bản nào.

### 19.5.3 Alignment bằng segment

Normalizer của chương không viết lại chuỗi bằng một loạt `re.sub`. Nó tách text thành **segment**, mỗi segment có `(raw, spoken, cls)`. Segment `plain` là phần chưa bị chạm tới. Các stage sau chỉ xử lý segment `plain`, nên:

- alignment raw ↔ spoken có sẵn ở mức segment;
- một stage không thể viết lại output của stage trước. Ví dụ "mười bốn giờ" sẽ không bị luật số nào chạm vào nữa.

Khi user ngắt lời, client báo `played_sample_offset` ([Chương 16](chuong-16-dataflow-end-to-end-va-audio-contract.md) §16.6.4), gateway quy ra tỷ lệ đã phát của chunk. Hàm `played_display_prefix` ánh xạ tỷ lệ này về `display_text` một cách **bảo thủ**: một segment đã viết lại (số, tiền, ngày) chỉ tính là đã nghe khi phát **hết** segment đó; segment `plain` cắt ở khoảng trắng gần nhất. Kết quả trên chunk ở trên (**Reproduced**):

```text
 20%: 'Giá vé là'
 45%: 'Giá vé là'
 60%: 'Giá vé là'                       ← "một triệu hai trăm năm mươi nghìn đồng" chưa phát hết
 90%: 'Giá vé là 1.250.000đ, đã'
100%: 'Giá vé là 1.250.000đ, đã gồm thuế.'
```

Ở 60%, user mới nghe "một triệu hai trăm…". Ghi `1.250.000đ` vào history là nói dối LLM rằng user đã nghe giá. Bảo thủ ở đây đúng hướng: LLM sẽ nhắc lại giá ở lượt sau.

[Chương 16](chuong-16-dataflow-end-to-end-va-audio-contract.md) §16.6.4 ước lượng theo tỷ lệ ký tự trên `raw_text`. Ước lượng trên `spoken_text` tốt hơn vì độ dài audio tỷ lệ với text đọc chứ không với text viết: `1.250.000đ` có 10 ký tự nhưng đọc mất khoảng 9 âm tiết. Cả hai vẫn chỉ là ước lượng. Thiết kế §7.3 nói rõ: không có alignment token ↔ audio thì chỉ khẳng định được played offset, không khẳng định được chính xác từ nào đã phát (**Synthesis**).[^design] Nếu TTS trả timestamp theo từ, dùng timestamp thay cho ước lượng.

---

## 19.6 Normalizer tiếng Việt (Q3, Q5)

### 19.6.1 Vị trí: sau chunker, theo từng chunk

| Phương án | Vấn đề |
|---|---|
| Normalize **cả câu trả lời** rồi mới chunk | Phải chờ LLM xong, mất toàn bộ lợi ích streaming |
| Normalize **trước** chunker, theo luồng | Normalizer chèn dấu phẩy (nhóm số điện thoại), làm mất dấu chấm (`TP.HCM` → "thành phố Hồ Chí Minh"), nên chunker thấy ranh giới giả hoặc mất ranh giới thật. Normalizer còn phải tự giữ lại giá trị đang sinh dở. |
| Normalize **sau** chunker, mỗi chunk một lần (**chọn**) | Chunker đã bảo đảm không cắt giữa giá trị. Normalizer là hàm thuần trên một chuỗi hoàn chỉnh, dễ test |

Wiki TTS selection mô tả đúng thứ tự LLM streaming → chunker theo cụm/câu có nghĩa → normalizer → TTS audio streaming → bounded playback queue, và nhấn mạnh không cắt giữa một giá trị còn đang hoàn thành (**Synthesis** của wiki).[^ttssel]

Cái giá của việc normalize theo từng chunk: mất ngữ cảnh xuyên chunk. Ví dụ "ngày" ở cuối chunk trước và `12/10` ở đầu chunk sau. Hiếm gặp, vì chunker chỉ cắt ở dấu câu. Nếu cần, truyền từ cuối của chunk trước vào làm `left_context` chỉ để đọc, không để viết lại (**Synthesis**).

Chi phí: normalizer của chương mất **0,09 ms** cho một chunk 86 ký tự trên i7-1255U (**Reproduced**). VietNormalizer báo khoảng 0,6 ms mỗi lần gọi với 17K+ mục từ điển (**Reported**, không nêu phần cứng).[^vnorm] Cả hai đều không đáng kể so với TTFA cỡ 100 ms trở lên của TTS. Normalizer không phải là chỗ để tối ưu latency.

### 19.6.2 Kiến trúc: pipeline luật có thứ tự trên segment

Thứ tự stage trong `bridge.py` (từ đặc thù tới chung):

```text
NFC → markup → emoji → pre-lexicon → approx(~) → url → email → abbr → admin(Q.1) → phone → date → time
    → percent → unit → money → code(VN123) → roman → ordinal → range → number → acronym(fallback)
    → symbol → post-lexicon(case-sensitive) → post-lexicon(case-insensitive) → cleanup
```

Vì sao thứ tự quan trọng, bằng một bug thật gặp khi viết chương: bản đầu của script đặt `VNĐ` trong từ điển viết tắt (`"VNĐ": "việt nam đồng"`). Stage `abbr` chạy trước stage `money`, nên `105.000 VNĐ` thành "một trăm linh năm nghìn **việt nam đồng**": số được stage `number` đọc riêng, còn luật tiền không bao giờ thấy ký hiệu tiền (**Reproduced**, lần chạy đầu của Script 2). Sửa: bỏ `VNĐ` khỏi bảng viết tắt để stage `money` xử lý. Bài học: **mỗi ký hiệu chỉ được một stage sở hữu**, và regression phải có ca cho mỗi ký hiệu.

VietNormalizer cũng dùng thứ tự cố định, 19 bước: NFC → ký tự đặc biệt/URL/email → dấu câu → … → số đứng riêng → lowercase → từ điển viết tắt → từ điển từ nước ngoài → phiên âm theo luật (**Reported**). Trang wiki lưu ý: vì lowercase chạy trước các bước từ điển, thứ tự ảnh hưởng tới cách viết mục từ tuỳ chỉnh (**Synthesis** của wiki).[^vnorm]

### 19.6.3 Bảng quyết định của normalizer mẫu

Tất cả 44 ca dưới đây PASS ở lần chạy cuối của Script 2 (**Reproduced**). Bảng rút gọn; đầy đủ ở Phụ lục.

| Lớp | Input | spoken | Quyết định / cảnh báo |
|---|---|---|---|
| Tiền | `1.250.000đ` | một triệu hai trăm năm mươi nghìn đồng | Chấm = nghìn (quy ước Việt) |
| Tiền lóng | `50k` · `2tr5` | năm mươi nghìn · hai triệu năm trăm nghìn | `k` không thêm "đồng"; `2tr5` = 2.500.000 |
| Ngoại tệ | `$10` · `25 USD` | mười đô la · hai mươi lăm đô la | `$` đứng trước được xử lý riêng |
| Thập phân | `3,5` · `0,05` | ba phẩy năm · không phẩy không năm | Phần lẻ bắt đầu bằng 0 hoặc > 2 chữ số thì đọc từng chữ số |
| Ngày | `ngày 01/05/2025` | ngày mùng một tháng năm năm hai nghìn không trăm hai mươi lăm | Ngày 1–10 đọc "mùng"; tháng 4 đọc "tư" |
| Ngày/phân số | `giảm 1/3 giá` | giảm một phần ba giá | ⚠ không có từ ngữ cảnh và d < m ≤ 10 thì đọc phân số |
| Ngày sai | `31/02` | ba mươi mốt tháng hai | ⚠ ngày không tồn tại, **vẫn đọc nguyên văn** |
| Giờ | `14:30` · `8h` · `trong 2h` | mười bốn giờ ba mươi phút · tám giờ · hai **tiếng** | Từ đứng trước (`trong`, `mất`, `khoảng`…) biến giờ thành thời lượng |
| Điện thoại | `0912.345.678` · `1900 1234` | không chín một hai, ba bốn năm, sáu bảy tám | Đọc từng chữ số, nhóm theo cách viết, phẩy giữa nhóm để có nhịp |
| Thứ tự | `Thứ 2` · `hạng 1` · `thế kỷ XXI` | Thứ hai · hạng nhất · thế kỷ hai mươi mốt | Số La Mã chỉ đọc khi có từ ngữ cảnh |
| Viết tắt | `Q.1` · `PGS.TS.` · `v.v.` | quận một · phó giáo sư tiến sĩ · vân vân | Từ điển; `Q.1` có luật riêng vì có số |
| Viết tắt lạ | `BHXH` · `CCCD` | bê hát ích xì hát · xê xê xê dê | ⚠ đánh vần và đề nghị thêm vào lexicon |
| Mã | `VN123` · `30A-123.45` | vê en nờ một hai ba · ba không a một hai ba bốn năm | Đánh vần ký tự, không đọc như số đếm |
| Mơ hồ | `1,250` · `3.5` | một phẩy hai năm không · ba phẩy năm | ⚠ cả hai đều ghi cảnh báo |
| Markup | `**Lưu ý:** …😊` · `- Bước 1:` | Lưu ý: … · Bước một: | Bỏ `**`, gạch đầu dòng, emoji |
| URL/email | `https://vd.vn/goi` · `hotro@vd.vn` | đường dẫn · hotro a còng vd chấm vn | URL không đọc; email đọc tối thiểu |
| Ký hiệu | `Có/Không & ~5 phút` | Có hoặc Không và khoảng năm phút | `/` chỉ thành "hoặc" khi giữa hai **chữ cái** (để không phá `12/10`) |

### 19.6.4 Năm chính sách cho ca mơ hồ (Synthesis)

1. **Sửa ở gốc trước.** Prompt yêu cầu LLM viết số theo quy ước Việt, không markdown, không URL ([Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.8.4, [Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.4). Report đề xuất prompt yêu cầu "số và ngày viết bằng chữ, hoặc để normalizer lo" (**Reported**).[^stack] Normalizer là lớp phòng thủ thứ hai.
2. **Không tự sửa nội dung.** `31/02` vẫn đọc "ba mươi mốt tháng hai" kèm cảnh báo. Một normalizer "thông minh" đổi thành 28/02 là đang bịa thông tin trong giọng nói của bot.
3. **Mỗi lựa chọn mặc định phải ghi ra, có test.** `1,250` đọc theo quy ước Việt (thập phân) là một **chính sách**. Nếu LLM của bạn hay viết kiểu Anh, đổi chính sách và đổi test, đừng vá bằng regex đơn lẻ.
4. **Cảnh báo là dữ liệu.** Đếm `warnings` theo loại. Tỷ lệ `viết tắt lạ` cao nghĩa là lexicon thiếu mục; tỷ lệ `số kiểu Anh` cao nghĩa là prompt không được tuân thủ.
5. **Dùng LLM để normalize chỉ cho phần dư.** Nếu dùng, chạy sau luật, chỉ trên span luật không xử lý được, và kiểm tra các con số trong output khớp các con số trong input ([Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.8.6). Gọi thêm một LLM trong critical path làm mất ý nghĩa của mọi tối ưu ở §19.3.

### 19.6.5 Tham số theo giọng đọc

Normalizer phải biết **giọng nào sẽ đọc**:

- **Vùng miền:** `nghìn`/`ngàn`, `linh`/`lẻ` ([Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.8.3). VieNeu v3 Turbo có preset voice theo ba vùng Bắc/Trung/Nam (**Reported**).[^vieneu] Giọng Nam đọc "một trăm linh năm" nghe lệch. Trong code mẫu, tham số `north` nên lấy từ cấu hình voice chứ không hard-code (**Synthesis**).
- **Năng lực TTS:** TTS có đọc được tiếng Anh không (§19.8)? Có xử lý được dấu gạch nối trong respelling (`ki-lô-mét` so với `ki lô mét`) không? Có phân biệt hoa thường không? VietNormalizer lowercase toàn bộ output (**Reported**)[^vnorm]; normalizer của chương giữ nguyên chữ hoa ở phần không bị viết lại. Ảnh hưởng của hai lựa chọn này lên một TTS cụ thể chưa được đo trong wiki. Phải nghe thử.
- **Dấu câu là tham số prosody.** VieNeu API nhận nhưng **bỏ qua** `speed` và `instructions` (header `X-VieNeu-Ignored`, **Reported**).[^vieneuapi] Với backend như vậy, dấu câu gần như là núm duy nhất để điều khiển ngắt nghỉ (**Synthesis**). Normalizer không được xoá dấu câu ([Chương 13](chuong-13-tts-tu-van-ban-toi-waveform.md) §13.6). Cũng vì vậy mà normalizer mẫu đọc số điện thoại có dấu phẩy giữa các nhóm.

### 19.6.6 Dùng thư viện có sẵn?

Thiết kế §5.5 ghi wiki chưa chọn được thư viện Vietnamese normalizer nào đã kiểm chứng.[^design] Wiki hiện có hai ứng viên, hướng ngược nhau:

| | [VietNormalizer](../wiki/vietnormalizer.md) | [ViSoNorm](../wiki/visonorm-visobert-normalizer.md) |
|---|---|---|
| Hướng | Viết → **nói** (TN cho TTS) | Viết không chuẩn → viết chuẩn (`sv` → "sinh viên", thêm dấu) |
| Cách làm | 19 bước luật, CSV từ điển, phiên âm từ Anh theo luật | ViSoBERT ba head, `trust_remote_code=True` |
| Hiệu năng | ~0,6 ms/lần gọi, ~40 ms khởi tạo (**Reported**) | Không nêu |
| License | MIT (**Reported**) | Không nêu |
| Hợp với cầu text→speech | Có: đúng slot normalizer | Hiếm khi: LLM ít sinh teencode; hợp hơn cho text người dùng gõ |
| Rủi ro | Chưa cài, chưa chạy; README tự mâu thuẫn ở `database` → `đa-ta-bâi`/`đa-ta-bê`; lowercase; phiên âm từ Anh mặc định **bật** | Chưa có license, benchmark; chạy remote code chưa review |

Nguồn: [^vnorm][^visonorm] (**Reported**, cả hai chưa được wiki chạy).

Cách tích hợp an toàn nếu dùng VietNormalizer (**Synthesis**, chưa thử):

- Bọc nó như **verbalizer cho segment `plain`** sau khi stage của bạn đã xử lý các lớp cần alignment (tiền, ngày, số điện thoại). Nếu không, bạn mất alignment.
- Tắt phiên âm (`enable_transliteration=False`) khi TTS tự đọc code-switch. Wiki lưu ý phiên âm tiếng Anh là quy ước của thư viện, không phải của từng TTS.[^vnorm]
- Pin phiên bản và chạy toàn bộ regression của bạn trên nó trước khi dùng.

Ở mức công nghiệp, TN/ITN thường làm bằng ngữ pháp WFST (kiểu NeMo text processing). Mức độ hoàn thiện cho TN tiếng Việt chưa được kiểm tra trong wiki (**Unverified**, kiến thức nền).

---

## 19.7 Lexicon và substitution dictionary (Q6)

### 19.7.1 Hai pha

| Pha | Chạy | Mục đích | Ví dụ |
|---|---|---|---|
| **Pre-TN** (bảo vệ) | Trước mọi luật số/ký hiệu | Thực thể có số hoặc ký hiệu mà luật chung sẽ đọc sai | `COVID-19` → "cô vít mười chín" (không phải "COVID trừ mười chín"); `iPhone 15`; `4G`; `OK` |
| **Post-TN** (respelling) | Trên segment `plain` còn lại | Tên riêng, từ mượn, thuật ngữ mà G2P của TTS đọc sai | `Shopee` → "sốp pi"; `email` → "i meo" (khi TTS không đọc được tiếng Anh) |
| **Alert** (không viết lại) | Quét song song | Từ tiếng Việt hợp lệ mà TTS được báo đọc sai | `chánh` → ghi cảnh báo, đếm metric |

[Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.9.3 nêu thứ tự TN → lexicon → G2P. Chương này tách lexicon thành hai pha: thực thể chứa số **phải** được bảo vệ trước TN, nếu không thì `COVID-19` đã thành chữ trước khi lexicon kịp nhìn thấy.

### 19.7.2 Quy tắc khớp

Các quy tắc sau đều được Script 2 kiểm (**Reproduced**):

- **Sau NFC.** Text NFD làm lexicon trượt dù nhìn giống hệt ([Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.5.2).
- **Theo ranh giới từ Unicode** (`(?<!\w)…(?!\w)`; `\w` của Python nhận chữ có dấu). `Pinterest` giữ nguyên dù có thể có mục `pin`.
- **Mục dài khớp trước** (sắp xếp theo độ dài giảm dần), để `TP.HCM` thắng `TP.`.
- **Phân biệt hoa thường theo mục.** `AI` → "ây ai" nhưng `ai` (đại từ "ai") giữ nguyên: "Hỏi ai cũng biết AI" → "Hỏi ai cũng biết ây ai". Code mẫu coi mọi mục viết hoa toàn bộ là case-sensitive.
- **Không với vào trong mã.** Mục `VN` → "vê en" **không** áp vào `VN123`, vì `VN123` là một từ. Stage `code` đánh vần nó thành "vê en nờ một hai ba". Nếu muốn "vê en", phải có luật cho mã chuyến bay, không phải mục lexicon. Đây là hành vi đúng: lexicon khớp lỏng sẽ sửa nhầm khắp nơi.

### 19.7.3 Respelling, phoneme và giới hạn của lexicon

[Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.9.4 phân hai kiểu frontend. Áp vào các TTS trong wiki:

| TTS | Frontend (**Reported**) | Lexicon dùng được |
|---|---|---|
| VieNeu v3 Turbo | `sea-g2p` nằm trong model; prompt gồm reference codes và phonemes[^vieneu][^vieneurt] | Chỉ **respelling** qua API text (**Synthesis**); muốn override phoneme thì phải can thiệp vào SDK |
| Kokoro Vietnamese | `vig2p`, khớp code inference và training[^kokoro] | Respelling, hoặc override phoneme nếu tự gọi G2P (phải dùng đúng `vig2p`) |
| Fun-CosyVoice3 (không có vi) | Pronunciation inpainting bằng Pinyin/CMU[^cosy3] | Ví dụ về điều khiển phát âm inline mà TTS tiếng Việt hiện chưa được ghi nhận có |

Respelling chỉ né được lỗi khi tồn tại một chuỗi chữ khác mà TTS đọc ra đúng âm cần có. Ca điển hình **không** cứu được: VieNeu v3 Turbo được báo đọc `chánh` thành `tránh` (issue #207). Ca này chỉ được report AI chuyển lại, wiki chưa mở issue và chưa reproduce (**Reported/Unverified**).[^stack][^ttssel] `chánh` là một âm tiết tiếng Việt hợp lệ, không có cách viết nào khác cho cùng âm đó. Thứ tự xử lý (**Synthesis**):

1. **Reproduce** trên đúng phiên bản và voice bạn dùng. Wiki TTS selection khuyên dùng ca này như regression case cần kiểm tra, không gọi là lỗi đã xác minh.[^ttssel]
2. Nếu lỗi có thật: đặt mục **alert** để đếm tần suất trong traffic thật. Code mẫu ghi `ALERT 'Chánh': …` và vẫn gửi nguyên văn.
3. Giảm phơi nhiễm ở gốc: prompt tránh từ đó khi có từ thay thế. Thường là không có: "Chánh văn phòng", "chánh án" là chức danh.
4. Báo upstream, hoặc định tuyến câu chứa từ đó sang TTS khác nếu domain dùng nhiều. Định tuyến làm đổi giọng giữa câu trả lời, xem §19.8.3.

### 19.7.4 Quản trị lexicon

Lexicon là **dữ liệu sản phẩm**, không phải hằng số trong code. Mỗi mục cần:

```yaml
- term: "Shopee"
  replacement: "sốp pi"
  phase: post            # pre | post | alert
  case_sensitive: false
  scope: always          # always | no_codeswitch | voice:<id> | tts:<backend>
  reason: "G2P đọc như từ Việt 'sô-pê'"
  test: "Mua iPhone 15 trên Shopee → Mua ai phôn mười lăm trên sốp pi"
  added: 2026-10-12
  owner: team-voice
```

- **Version** lexicon và normalizer cùng nhau, ghi phiên bản vào mỗi `text.chunk`.
- **Mỗi mục có ít nhất một ca test.** Mục không có test sẽ bị ai đó xoá mà không biết.
- **Scope theo TTS và voice.** Một respelling đúng với VieNeu có thể sai với Kokoro. Đổi TTS là phải chạy lại tập nghe cho toàn bộ lexicon.
- **Nguồn mục mới:** cảnh báo `viết tắt lạ` từ production; lỗi phát hiện ở tập nghe; khiếu nại người dùng; round-trip ASR lệch ở critical span (tên riêng, số).

---

## 19.8 Code-switch Việt–Anh

### 19.8.1 Ba lựa chọn

| Lựa chọn | Làm ở đâu | Khi nào |
|---|---|---|
| **Giữ nguyên** | Không làm gì | TTS được báo đọc tốt tiếng Anh xen trong câu Việt |
| **Respelling** | Post-lexicon (`scope: no_codeswitch`) | TTS không đọc được, hoặc từ này cần cách đọc Việt hoá cố định |
| **Thay từ Việt** | Prompt LLM | Có từ thuần Việt phổ biến tương đương. Không ép quá: "email" tự nhiên hơn "thư điện tử" ([Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.10) |

Report và thiết kế khuyên giữ tiếng Anh nếu TTS xử lý được code-switch, nếu không thì phiên âm; VieNeu được nêu là xử lý được (**Reported**).[^stack][^design] VieNeu v3 Turbo được train trên khoảng 10.000 giờ dữ liệu Anh–Việt; bản Nano preview được ghi là kém rõ rệt ở tiếng Anh và câu trộn Anh–Việt (**Reported**).[^vieneu] Hệ quả: **quyết định code-switch gắn với backend**. Fallback từ Turbo sang Nano phải kéo theo đổi chính sách lexicon.

Script 2 cho thấy cùng một câu với hai cấu hình (**Reproduced**):

```text
tts_codeswitch=True : Anh check email và họp online trước deadline nhé, link gửi qua Facebook.
tts_codeswitch=False: Anh check i meo và họp on lai trước đét lai nhé, link gửi qua phây búc.
```

Ở cấu hình `False`, `check` và `link` vẫn còn tiếng Anh vì không có trong lexicon. Một lexicon respelling không bao giờ phủ hết. Nếu TTS thật sự không đọc được tiếng Anh, cần thêm phiên âm theo luật (VietNormalizer có, **Reported**)[^vnorm] hoặc ràng buộc ở prompt.

### 19.8.2 Viết tắt: đánh vần kiểu nào?

`USB` đọc "u ét bê" (tên chữ cái Việt) hay "iu ét bi" (tiếng Anh)? `AI` đọc "ây ai" hay "trí tuệ nhân tạo"? Không có luật chung ([Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) §5.8.5). VietNormalizer chọn `AI` → "trí tuệ nhân tạo", `TV` → "ti vi" (**Reported**)[^vnorm]; code mẫu chọn "ây ai". Hãy chốt một bảng cho sản phẩm, đưa vào lexicon và cho người nghe duyệt.

### 19.8.3 Đừng định tuyến ngôn ngữ theo từng chunk

HF s2s có tuỳ chọn `--detect_llm_output_language`: phát hiện ngôn ngữ của từng chunk assistant bằng Lingua. Text dưới 20 ký tự hoặc mơ hồ thì dùng ngôn ngữ assistant phát hiện gần nhất (**Reported**).[^s2s] Cơ chế này hợp với hội thoại đổi hẳn ngôn ngữ giữa các lượt. Với câu trả lời tiếng Việt có nhiều từ Anh, nó tạo rủi ro (**Synthesis**):

- Chunk "Anh check email và update deadline nhé." có thể bị nhận là tiếng Anh và đi sang TTS tiếng Anh, làm **đổi giọng giữa câu trả lời**.
- Report đề xuất router theo ngôn ngữ (VieNeu cho `vi`, Qwen3-TTS cho en/zh, **Reported**).[^stack] Router nên quyết định theo **câu trả lời** hoặc theo **session**, không theo chunk. Chỉ chuyển backend khi cả câu trả lời là ngôn ngữ khác.

---

## 19.9 Ghép vào runtime

### 19.9.1 Stage cầu trong asyncio (phác thảo, chưa chạy)

Phác thảo dưới đây nối các lớp của `bridge.py` vào khung runtime ở [Chương 18](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md) §18.9. Nó **chưa được chạy** ở dạng này.

```python
async def bridge_stage(gen_id, llm_stream, tts_q: asyncio.Queue, events, norm, cfg):
    """Consumer của LLM stream. Một instance cho mỗi generation; bị huỷ cùng response scope."""
    think, chunker, chunk_id = ThinkFilter(), ClauseChunker(**cfg.chunker), 0
    async with aclosing(llm_stream) as stream:            # đóng SSE khi stage bị huỷ (Ch.18 §18.6)
        async for ev in stream:
            if ev.kind == "delta":
                got = chunker.feed(think.feed(ev.text))
            elif ev.kind == "done":
                got = chunker.feed(think.flush()) + chunker.flush()
            else:                                         # error: để owner quyết định, không flush
                raise LLMError(ev)
            for raw, kind in got:
                r = norm.normalize(raw)                   # ~0,1 ms: chạy thẳng trên loop là được
                rec = dict(generation_id=gen_id, chunk_id=chunk_id, kind=kind, raw_text=raw,
                           display_text=r.display, spoken_text=r.spoken, warnings=r.warnings,
                           normalizer_version=norm.version, lexicon_version=norm.lexicon_version)
                events.emit("text.chunk", rec)            # log + caption
                if r.spoken.strip():                      # chunk chỉ có emoji/markup: không gọi TTS
                    await tts_q.put((gen_id, chunk_id, r)) # bounded: backpressure ngược lên LLM
                chunk_id += 1
    await tts_q.put((gen_id, None, None))                 # sentinel kết thúc generation
```

Năm điểm chú ý (**Synthesis**):

1. **Một instance cho mỗi generation.** Không dùng lại chunker giữa hai generation. Khi bị huỷ, task bị cancel và mọi state biến mất cùng nó; không `flush()`.
2. **Normalizer chạy thẳng trên event loop** vì 0,1 ms nằm trong ngân sách giữa hai `await` ([Chương 18](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md) §18.2.2). Nếu thay bằng normalizer neural, chuyển sang executor.
3. **`tts_q` bounded.** TTS chậm thì chunker chờ, LLM stream bị đọc chậm lại. Backpressure đi ngược lên đúng hướng ([Chương 18](chuong-18-lap-trinh-async-va-streaming-cho-pipeline-audio.md) §18.5).
4. **Bảng `chunk_id → [mẫu đầu, mẫu cuối)`** do TTS adapter ghi khi audio về ([Chương 16](chuong-16-dataflow-end-to-end-va-audio-contract.md) §16.6.4). Kết hợp với `segments` của chunk thì có §19.5.3.
5. **Tham số TTS cố định trong một generation.** Mỗi chunk là một request độc lập. VieNeu lấy mẫu với `temperature` 0,8 mặc định (**Reported**).[^vieneuapi] Ngữ điệu và âm sắc có thể dao động giữa các chunk của cùng một câu trả lời. Giữ cùng voice và tham số sampling trong một generation; thử hạ `temperature` nếu tập nghe phát hiện giọng "nhảy" giữa các chunk. Chưa có số đo trong wiki. Xem thêm [Chương 13](chuong-13-tts-tu-van-ban-toi-waveform.md) §13.10 về giọng nhất quán giữa các chunk.

### 19.9.2 Một request mỗi chunk hay một request dài?

| | Một request mỗi chunk | Gom phần còn lại thành một request |
|---|---|---|
| Huỷ | Từng chunk; chunk là đơn vị nhỏ nhất | Phải huỷ cả request dài |
| Prosody giữa chunk | Đứt ở mỗi ranh giới | Liền (server tự chia ở ranh giới câu, **Reported** với VieNeu)[^vieneuapi] |
| Slot TTS | Một slot cho mỗi chunk đang sinh | Một slot |
| Khi nào hợp | Mặc định cho hội thoại | Chỉ khi LLM đã `done` và phần còn lại dài (đọc tin, tóm tắt) |

Chiến lược lai (**Synthesis**): chunk đầu gửi riêng để có TTFA thấp; khi LLM `done` mà còn nhiều chunk chưa gửi, gộp chúng thành một request. Cách này giữ được lợi ích của `clause` ở đầu và của `full` ở đuôi.

---

## 19.10 Bộ regression (Q8)

### 19.10.1 Ba tầng

| Tầng | Kiểm cái gì | Chạy khi | Thời gian | Chấm bằng |
|---|---|---|---|---|
| **L1: golden normalizer/lexicon** | `input → spoken_text` đúng từng ký tự, kèm `warnings` mong đợi | Mỗi commit | ms | Máy (so chuỗi) |
| **L2: thuộc tính chunker** | Bất biến với cách chia token; không cắt trong số/URL/viết tắt; độ dài trong `[min_len, hard_max]` trừ chunk cuối; nối các chunk = text đã lọc (bỏ qua khoảng trắng) | Mỗi commit | giây | Máy (fuzz) |
| **L3: tập nghe TTS** | Phát âm, thanh điệu, ngắt nghỉ ở ranh giới chunk, giọng nhất quán giữa chunk | Đổi TTS, voice, lexicon lớn | giờ | Người nghe + proxy |

Script 2 là một L1 tối thiểu: 44 ca, chạy dưới một giây, trả mã thoát khác 0 khi có ca FAIL nên gắn được vào CI. Script 1 phần (b) là một L2 tối thiểu.

### 19.10.2 Định dạng ca L1

```json
{"id": "money-007", "class": "tiền", "input": "Còn 105.000 VNĐ",
 "expect": "Còn một trăm linh năm nghìn đồng", "expect_warnings": [],
 "voice_region": "north", "tts_codeswitch": true,
 "why": "VNĐ phải thuộc stage money, không phải abbr (bug 2026-10-12)"}
```

Trường `why` ghi lý do ca test tồn tại. Phần lớn ca có giá trị là **bug đã từng xảy ra**.

### 19.10.3 Tập nghe L3

Thiết kế §10 mục 2 yêu cầu 150–300 prompt; chấm thanh điệu, phát âm, độ tự nhiên, độ nhất quán giọng; test riêng normalizer, lexicon và ranh giới chunk (**Synthesis** của thiết kế).[^design] Wiki TTS selection liệt kê các nhóm: sáu thanh, câu hỏi, hội thoại ngắn/dài, tiền/ngày/số điện thoại/đơn vị, tên riêng, code-switch, giọng vùng, ranh giới chunk. Wiki yêu cầu **lưu cả raw text và normalized spoken text** (**Synthesis** của wiki).[^ttssel] Bổ sung cho cầu text → speech (**Synthesis**):

- **Ca ranh giới chunk:** cùng một câu trả lời, phát (a) một request và (b) theo chunk của `clause`. Chấm CMOS (a) so với (b). Đây là cách đo trực tiếp cái giá prosody của §19.3.
- **Ca chunk đầu ngắn:** "Dạ," / "Vâng ạ," + câu dài, để nghe khe im lặng.
- **Ca lexicon:** mỗi mục lexicon có một câu; nghe trước và sau lexicon ([Chương 5](chuong-05-ngu-am-chu-viet-va-van-ban-tieng-viet.md) bài tập 8).
- **Ca alert:** `chánh`, và mọi từ đang nằm trong danh sách alert.

**Round-trip CER** (ASR chép lại audio TTS rồi so với `spoken_text`) chỉ là proxy. ASR mạnh đoán đúng từ dù TTS phát âm lệch thanh ([Chương 13](chuong-13-tts-tu-van-ban-toi-waveform.md) §13.12.2). Nó có ích nhất cho critical span: con số, tên riêng có bị đọc ra đúng không.

### 19.10.4 Gate

- L1 và L2: 100% PASS mới merge. Ca FAIL vì kỳ vọng sai thì sửa kỳ vọng **kèm lý do** trong `why`. Khi viết chương, Script 2 có 5 ca FAIL ở lần chạy đầu: 1 bug thật (`VNĐ`), 1 thiếu tính năng (`~`), 1 thiếu kiểm tra ngày hợp lệ, 2 kỳ vọng do tác giả viết sai (`CCCD` có chữ D đọc "dê", không phải "đê"; chính sách đọc `1,250`). Phân loại này là bình thường; giấu nó đi mới là vấn đề.
- L3: không có ca nào tệ hơn baseline ở nhóm số, tên riêng và thanh điệu. Mọi lần đổi TTS hoặc voice đều chạy lại toàn bộ.

---

## 19.11 Quan sát vận hành

| Metric | Định nghĩa | Dùng để |
|---|---|---|
| `ttfc_ms` | Gửi request LLM → chunker nhả chunk đầu | Tách phần LLM khỏi TTFA của TTS ([Chương 12](chuong-12-llm-trong-vong-hoi-thoai-noi.md) §12.3.1) |
| `first_chunk_chars`, `chunk_chars` P50/P95 | Độ dài chunk | Tune `first_min`, `hard_max` |
| `chunk_kind_ratio` | Tỷ lệ `term`/`comma`/`hard_max`/`idle`/`final` | `hard_max` cao → prompt sinh câu dài |
| `chunks_per_reply` | Số request TTS mỗi câu trả lời | Chi phí slot, rủi ro `429` |
| `inter_chunk_gap_ms` P95 | `max(0, audio đầu chunk k − hết audio chunk k−1)` đo ở client | Underrun (§19.3.3) |
| `norm_warnings{type}` | Đếm cảnh báo theo loại | Thiếu lexicon, prompt không được tuân thủ |
| `lexicon_hits{term}`, `alert_hits{term}` | Mục nào được dùng | Dọn mục chết; ưu tiên sửa lỗi phát âm hay gặp |
| `norm_latency_us` | Thời gian normalize mỗi chunk | Phát hiện regex thảm hoạ (catastrophic backtracking) |
| `spoken_empty_chunks` | Chunk mà `spoken_text` rỗng | LLM sinh emoji/markup thuần |

Report đề xuất metric `first_sentence→tts_first_byte` (**Reported**).[^stack] Metric này đo đúng cạnh từ cầu sang TTS và nên được join theo `generation_id` + `chunk_id`.

---

## 19.12 Lỗi thường gặp: triệu chứng → nguyên nhân → cách sửa

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| Bot đọc "một… hai trăm năm mươi nghìn đồng" với khoảng nghỉ lạ | Chunker cắt `1.` / `250.000đ` vì quyết định ở cuối buffer | Nhìn thêm một ký tự (§19.4.2); fuzz test L2 |
| Kết quả chunk khác nhau giữa hai lần chạy cùng câu | Quyết định phụ thuộc thời điểm token đến hoặc timer | Chỉ quyết định theo nội dung; test bất biến |
| "Dạ." rồi im 1 s | Chunk đầu quá ngắn, chunk 2 chưa sẵn sàng | `min_len` gộp mảnh; đo `inter_chunk_gap` |
| Khe im giữa câu khi tải cao | LLM chậm + mệnh đề dài không có dấu phẩy | Prompt câu ngắn; `later_comma_min` thấp hơn; `hard_max` cắt trước liên từ (§19.3.3) |
| Bot đọc "sao sao", "thăng thăng" | Markdown lọt qua | Prompt + stage markup |
| Bot đọc lý luận nội bộ | `<think>` lọt; lọc sau chunker | ThinkFilter trước chunker (§19.4.6) |
| "một trăm linh năm nghìn việt nam đồng" | Hai stage cùng sở hữu một ký hiệu, sai thứ tự | Mỗi ký hiệu một stage; regression (§19.6.2) |
| "mười hai phần mười" thay vì "mười hai tháng mười" | Luật phân số chạy trước luật ngày hoặc thiếu ngữ cảnh | Thứ tự stage; ngưỡng phân số (§19.6.3) |
| History ghi bot đã nói giá nhưng user ngắt trước đó | Cắt history theo tỷ lệ ký tự raw, tính cả segment phát dở | Alignment theo segment, bảo thủ (§19.5.3) |
| LLM lượt sau viết số bằng chữ | History lưu `spoken_text` | History lưu `display_text` |
| "ai" (đại từ) bị đọc thành "ây ai" | Lexicon khớp không phân biệt hoa thường | `case_sensitive` theo mục (§19.7.2) |
| Respelling sửa nhầm trong từ khác | Khớp substring, không theo ranh giới từ | `(?<!\w)…(?!\w)` sau NFC |
| Giọng đổi giữa câu trả lời | Router ngôn ngữ theo chunk | Router theo câu trả lời/session (§19.8.3) |
| Sau khi fallback sang TTS khác, từ tiếng Anh bị đọc như chữ Việt | Chính sách code-switch không đổi theo backend | `tts_codeswitch` và scope lexicon theo backend |
| Đọc "chánh" thành "tránh" | Lỗi model (Reported/Unverified) | Reproduce; alert; prompt; báo upstream (§19.7.3) |
| Server TTS chia câu khác chunker | Chunk dài hơn `max_chars` của server | `hard_max` < `max_chars` (§19.4.5) |
| Bot đọc nhầm ngày 31/02 thành 28/02 | Normalizer "sửa" nội dung | Đọc nguyên văn, cảnh báo, sửa ở prompt (§19.6.4) |

---

## 19.13 Bài tập thực hành

1. **Bất biến.** Thêm vào Script 1 một câu có `TS. Nguyễn`, `v.v.` ở giữa câu (theo sau là chữ thường), `...` và `?!`. Chạy fuzz. Sau đó sửa `ClauseChunker` để quyết định ngay ở cuối buffer (bỏ `return None`) rồi chạy lại. Đếm số lần chunk khác tham chiếu.
2. **Underrun.** Trong Script 3, đổi LLM sang 12 tok/s và TTFT 600 ms. Tìm `first_min`, `later_comma_min`, `hard_max` sao cho gap max < 150 ms mà audio đầu nhỏ nhất. Ghi lại các chunk bị cắt cứng và nghe xem có chấp nhận được không (nếu có TTS).
3. **Cắt trước liên từ.** Sửa `_force_cut` để ưu tiên cắt **trước** `và|nhưng|để|nếu|vì|thì|mà` trong `buf[:hard_max]`, fallback về khoảng trắng. Chạy lại phần `hard_max` của Script 3 và so các chunk.
4. **Regression.** Viết 30 ca L1 cho domain của bạn (tên sản phẩm, mã đơn hàng, giờ mở cửa, địa chỉ). Chạy, phân loại FAIL thành bug / thiếu tính năng / kỳ vọng sai.
5. **Vùng miền.** Thêm tham số `north=False` cho giọng Nam và kiểm tra `105`, `1.005`, `30.000`. Nối tham số này với cấu hình voice.
6. **Alignment.** Gọi `played_display_prefix` trên chunk chứa số điện thoại với tỷ lệ 0,3 / 0,5 / 0,8. Giải thích vì sao kết quả đúng hoặc sai cho việc cắt history.
7. **Thư viện.** (Cần mạng.) Cài VietNormalizer, chạy 44 ca của Script 2 qua `normalize()` với `enable_transliteration` bật và tắt. Ghi các ca khác biệt và quyết định có dùng hay không.
8. **Nghe ranh giới chunk.** (Cần VieNeu.) Gọi `/v1/audio/speech` với câu trả lời mẫu: một request so với năm request theo `clause`. Nối audio, nghe mù, chấm CMOS.

---

## 19.14 Đáp án các câu hỏi tự kiểm tra

**Q1.** Theo token: âm thanh đầu sớm nhất, nhưng prosody gãy, TTS thiếu context, số request bùng nổ (66 so với 5 trong mô phỏng), tổng thời lượng tăng vì mỗi request mang theo im lặng đầu/cuối và prefill. Theo câu: prosody tốt, ít request, nhưng âm thanh đầu phải chờ LLM sinh xong cả câu đầu (1428 ms so với 752 ms trong mô phỏng GPU). Theo mệnh đề: cắt chunk đầu ở dấu phẩy khi ≥ ~25 ký tự, các chunk sau theo câu; đây là điểm cân bằng mặc định của thiết kế. Gom nhiều câu hay chờ cả câu trả lời chỉ hợp với đọc nội dung dài. Khi LLM chậm, phải cân thêm underrun (§19.3.3).

**Q2.** UI và history cần dạng viết (`1.250.000đ`), TTS cần dạng nói. History lưu dạng nói thì LLM bắt chước. Cắt history khi bị ngắt cần alignment giữa hai dạng. Log phải tách được lỗi LLM khỏi lỗi normalizer. Đánh giá TTS phải so với dạng nói. Tool và regex entity chạy trên dạng viết. Xem bảng §19.5.1.

**Q3.** Sau NFC và lọc markup, chạy một pipeline luật có thứ tự từ đặc thù tới chung: lexicon bảo vệ → URL/email → viết tắt → số điện thoại (đọc từng chữ số theo nhóm) → ngày (mùng, tháng tư, phân biệt phân số theo ngữ cảnh) → giờ (giờ hay tiếng theo từ đứng trước) → phần trăm, đơn vị, tiền (đ, k, tr, $, USD) → mã (đánh vần) → số La Mã, thứ tự, khoảng → số (chấm = nghìn, phẩy = thập phân, luật mốt/tư/lăm/linh) → đánh vần viết tắt lạ → ký hiệu → respelling. Mỗi ký hiệu chỉ một stage sở hữu. Ca mơ hồ chọn theo chính sách và ghi cảnh báo, không tự sửa nội dung. Code-switch: giữ nguyên nếu TTS đọc được, respelling nếu không, chính sách gắn với backend.

**Q4.** Vì dấu câu ở cuối buffer có thể là một phần của giá trị chưa sinh xong (`1.` → `1.250.000đ`, `https:` → `https://…`, `TP.` → `TP.HCM`). Quy tắc "dấu câu kết mệnh đề phải theo sau bởi khoảng trắng" cần biết ký tự kế tiếp. Nhờ vậy, đầu ra chunker không phụ thuộc cách chia token (0/5000 lần khác ở Script 1). Chunker ngây thơ tách số tiền, số điện thoại, URL, viết tắt thành nhiều mảnh, mỗi mảnh một request với ngữ điệu kết câu (§19.4.3).

**Q5.** Sau chunker, theo từng chunk. Trước chunker thì normalizer phá dấu câu mà chunker dựa vào (thêm phẩy, mất chấm) và phải tự xử lý giá trị dở dang. Trên cả câu trả lời thì mất streaming. Theo chunk thì normalizer là hàm thuần, ~0,1 ms, dễ test. Cái giá là mất ngữ cảnh xuyên chunk, hiếm gặp vì chunker chỉ cắt ở dấu câu.

**Q6.** Hai pha. Pre-TN cho thực thể chứa số hoặc ký hiệu (`COVID-19`, `iPhone 15`, `4G`) để luật số không đọc chúng trước. Post-TN cho respelling tên riêng và từ mượn trên phần text còn nguyên. Khớp sau NFC, theo ranh giới từ, mục dài trước, phân biệt hoa thường theo mục. Respelling không cứu được khi TTS đọc sai một âm tiết tiếng Việt hợp lệ (`chánh` → `tránh`, Reported/Unverified), vì không có cách viết khác cho cùng âm. Khi đó: reproduce, alert, giảm phơi nhiễm ở prompt, báo upstream hoặc đổi backend.

**Q7.** Khe hở sinh ra khi `ready(k) + wait + TTFA > end(k−1)`, thường do một mệnh đề ngắn theo sau bởi mệnh đề dài. Các núm vặn: hạ `later_comma_min` để cắt ở phẩy sớm hơn; đặt `hard_max` (trong mô phỏng, 60 → khe 315 ms, 45 → 0 ms) và cắt **trước** liên từ; tăng độ dài chunk đầu hoặc giữ âm thanh đầu tới khi có hai chunk; prompt câu ngắn; LLM nhanh hơn. Cái giá là prosody (cắt giữa mệnh đề), nhiều request hơn, hoặc âm thanh đầu muộn hơn. Đo `inter_chunk_gap` P95 thật trước khi tune.

**Q8.** Bằng regression ba tầng. L1 golden: mọi ca `input → spoken` và cảnh báo mong đợi, chạy mỗi commit, 100% PASS. L2 thuộc tính chunker: fuzz cách chia token, không cắt trong giá trị, giới hạn độ dài. L3 tập nghe 150–300 prompt khi đổi TTS, voice, lexicon. Mỗi bug sửa xong thành một ca có trường `why`. FAIL được phân loại (bug, thiếu tính năng, kỳ vọng sai) chứ không sửa kỳ vọng cho qua.

---

## 19.15 Tóm tắt một trang

- **Vị trí:** LLM token → ThinkFilter → ClauseChunker → (pre-lexicon → Normalizer → post-lexicon) → TTS. Chunker là consumer của LLM stream. Một instance cho mỗi `generation_id`; khi huỷ thì bỏ, không flush.
- **Flush:** mặc định theo mệnh đề: `.?!…;:`/xuống dòng; chunk đầu cắt ở phẩy khi ≥ 25 ký tự; gộp mảnh < 8; trần `hard_max` < `max_chars` của TTS. Per-token bị loại; gom nhiều câu chỉ cho nội dung dài.
- **Điều kiện liền tiếng:** `ready(k) + wait + TTFA(k) ≤ end(k−1)`. Lợi ích của chunk đầu ngắn đến từ việc không chờ LLM, không từ prefill TTS.
- **Chunker đúng:** chỉ cắt khi đã thấy ký tự sau dấu câu. Dấu câu kết mệnh đề luôn theo sau bởi khoảng trắng. Kết quả bất biến với cách chia token, kiểm được bằng fuzz.
- **Ba dạng text:** `raw_text` (debug), `display_text` (UI, history, entity), `spoken_text` (TTS). History lưu dạng hiển thị của phần **đã nghe**; segment viết lại chỉ tính khi phát hết.
- **Normalizer:** sau chunker, mỗi chunk một lần, ~0,1 ms. Pipeline luật trên segment, từ đặc thù tới chung, mỗi ký hiệu một stage. Mơ hồ thì theo chính sách và cảnh báo; không tự sửa nội dung. Tham số theo giọng (vùng miền, code-switch); giữ dấu câu.
- **Lexicon:** pre-TN bảo vệ thực thể có số; post-TN respelling; alert cho lỗi model. Khớp sau NFC, ranh giới từ, dài trước, hoa thường theo mục. Version, test, scope theo TTS/voice.
- **Code-switch:** quyết định theo backend (Turbo đọc được, Nano yếu). Router ngôn ngữ theo câu trả lời, không theo chunk.
- **Kiểm thử:** L1 golden, L2 thuộc tính, L3 tập nghe có ca ranh giới chunk (CMOS một request so với chia chunk).
- **Thư viện:** VietNormalizer là ứng viên đúng slot nhưng chưa kiểm chứng; ViSoNorm là hướng ngược lại.

---

## Hạn chế và phạm vi bao phủ

- **Không có TTS hay LLM thật nào được gọi.** Mô phỏng latency dùng tham số giả định; TTFA/RTF lấy từ số VieNeu (Reported) trên RTX 3060 và i5 thế hệ 12, không đo lại. Im lặng đầu/cuối 150 ms mỗi request là giả định của tác giả. Con số tuyệt đối trong §19.3 chỉ để thấy hình dạng đánh đổi.
- **Normalizer và chunker là mã minh hoạ.** 44 ca golden không phải độ phủ: chưa có số âm, số rất lớn, phân số phức tạp, địa chỉ đầy đủ, biển số mọi định dạng, giờ kiểu `2 giờ 15`, ngày âm lịch, đơn vị đa nghĩa (`m`, `g`, `l`), email đọc đúng chuẩn. Tên chữ cái để đánh vần chỉ là một lựa chọn trong nhiều biến thể.
- **Chưa nghe bất kỳ output nào.** Các lựa chọn như "ki lô mét" so với "ki-lô-mét", giữ chữ hoa hay lowercase, đọc `14:30` có "phút" hay không, đều chưa được kiểm bằng tai trên TTS thật.
- **VietNormalizer, ViSoNorm chưa được cài hay chạy.** Mọi mô tả là Reported từ README/model card qua wiki.
- **Lỗi `chánh` → `tránh`** là Reported/Unverified, chỉ được report AI chuyển lại.
- **Mốc thời gian:** thông tin VieNeu, HF s2s và thư viện normalizer có `stale_after` khoảng 2027-10. Kiểm tra lại API (`max_chars`, trường bị bỏ qua, preset voice) trước khi dựa vào.

---

## Phụ lục chương

Tất cả script nằm ở `/tmp/ch19/`, chạy bằng `python3 <script>` trong thư mục đó (Python 3.12.3, không thư viện ngoài), ngày 2026-10-12, Intel i7-1255U.

### Module chung: `bridge.py` (ThinkFilter, ClauseChunker, Normalizer, lexicon, alignment)

```python
# Chương 19 — bridge.py: cầu text → speech tối giản (chỉ thư viện chuẩn, Python 3.10+).
# Gồm: ThinkFilter (lọc <think> theo luồng), ClauseChunker (cắt mệnh đề, bất biến với
# cách chia token), Normalizer tiếng Việt dạng "segment rewriting" (giữ alignment
# raw ↔ spoken), Lexicon hai pha (trước TN: bảo vệ thực thể; sau TN: respelling),
# danh sách cảnh báo (từ đã biết TTS đọc sai). Đây là mã minh hoạ, không phải thư viện.
import re
import unicodedata as ud
from dataclasses import dataclass, field

# =============================== 1. ThinkFilter ===============================
class ThinkFilter:
    """Bỏ mọi nội dung trong <think>…</think>, kể cả khi thẻ bị chia qua nhiều token."""
    OPEN, CLOSE = "<think>", "</think>"

    def __init__(self):
        self.buf, self.inside = "", False

    @staticmethod
    def _partial(buf, tag):                      # độ dài hậu tố của buf trùng tiền tố tag
        for k in range(min(len(tag) - 1, len(buf)), 0, -1):
            if buf.endswith(tag[:k]):
                return k
        return 0

    def feed(self, s):
        self.buf += s
        out = []
        while True:
            tag = self.CLOSE if self.inside else self.OPEN
            i = self.buf.find(tag)
            if i < 0:
                keep = self._partial(self.buf, tag)
                if not self.inside:
                    out.append(self.buf[: len(self.buf) - keep])
                self.buf = self.buf[len(self.buf) - keep:] if keep else ""
                return "".join(out)
            if not self.inside:
                out.append(self.buf[:i])
            self.buf = self.buf[i + len(tag):]
            self.inside = not self.inside

    def flush(self):
        s = "" if self.inside else self.buf
        self.buf, self.inside = "", False
        return s


# =============================== 2. ClauseChunker ===============================
TERM = set(".!?…;:")
CLOSERS = set("\"'”’)]»")
ABBR_NOEND = {"tp", "ts", "pgs", "gs", "ths", "bs", "ks", "q", "p", "tt", "mr", "mrs", "ms", "dr", "st"}
ABBR_MAYEND = {"v.v", "etc"}


class ClauseChunker:
    """Quy tắc khởi điểm của thiết kế §5.5 + các bảo vệ cho tiếng Việt.
    Nguyên tắc cốt lõi: chỉ quyết định cắt khi đã thấy ký tự SAU dấu câu, nên kết quả
    không phụ thuộc cách LLM chia token (split invariance)."""

    def __init__(self, first_min=25, later_comma_min=80, min_len=8, hard_max=180):
        self.first_min, self.later_comma_min = first_min, later_comma_min
        self.min_len, self.hard_max = min_len, hard_max
        self.buf, self.scan_from, self.n_emitted = "", 0, 0

    def _scan(self, final):
        b, n, i = self.buf, len(self.buf), self.scan_from
        while i < n:
            c = b[i]
            if c == "\n":
                return i + 1, "newline"
            if c in TERM or c == ",":
                j = i
                while j + 1 < n and b[j + 1] in TERM:
                    j += 1
                while j + 1 < n and b[j + 1] in CLOSERS:
                    j += 1
                if j + 1 >= n and not final:
                    return None                       # chưa biết ký tự kế tiếp → chờ
                nxt = b[j + 1] if j + 1 < n else ""
                if nxt and not nxt.isspace():         # 1.250 · 3,5 · 14:30 · TP.HCM · https://
                    i = j + 1
                    continue
                if c == ",":
                    thr = self.first_min if self.n_emitted == 0 else self.later_comma_min
                    if len(b[: j + 1].strip()) >= thr:
                        return j + 1, "comma"
                    i = j + 1
                    continue
                if c == "." and b[i: j + 1].count(".") == 1:
                    m = re.search(r"([\w.]+)$", b[:i])
                    w = m.group(1).lower() if m else ""
                    if w in ABBR_NOEND:               # "TS. Nguyễn", "Q. Ba Đình"
                        i = j + 1
                        continue
                    if w in ABBR_MAYEND:              # "v.v." chỉ kết câu nếu sau đó là chữ hoa/xuống dòng
                        k = j + 1
                        while k < n and b[k] in " \t":
                            k += 1
                        if k >= n and not final:
                            return None
                        if k < n and b[k] != "\n" and not b[k].isupper():
                            i = j + 1
                            continue
                return j + 1, "term"
            i += 1
        return None

    def _force_cut(self):
        head = self.buf[: self.hard_max]
        k = max(head.rfind(" "), head.rfind("\t"))
        return (k + 1 if k > 0 else self.hard_max), "hard_max"

    def _drain(self, final):
        out = []
        while self.buf.strip():
            r = self._scan(final)
            if (r is None and len(self.buf) > self.hard_max) or (r and r[0] > self.hard_max):
                r = self._force_cut()
            if r is None:
                break
            cut, kind = r
            text = self.buf[:cut].strip()
            rest_empty = not self.buf[cut:].strip()
            if len(text) < self.min_len and not (final and rest_empty):
                self.scan_from = cut                  # mảnh quá ngắn: gộp vào mệnh đề sau
                continue
            out.append((text, kind))
            self.buf, self.scan_from = self.buf[cut:], 0
            self.n_emitted += 1
        if final and self.buf.strip():
            out.append((self.buf.strip(), "final"))
            self.n_emitted += 1
        if final:
            self.buf, self.scan_from = "", 0
        return out

    def feed(self, delta):
        self.buf += delta
        return self._drain(final=False)

    def flush(self):
        return self._drain(final=True)


# =============================== 3. Đọc số ===============================
DIG = "không một hai ba bốn năm sáu bảy tám chín".split()


def read_lt1000(n, full, north=True):
    h, t, u = n // 100, n // 10 % 10, n % 10
    out = []
    if full or h:
        out += [DIG[h], "trăm"]
    if t == 0:
        if u and out:
            out.append("linh" if north else "lẻ")
        if u:
            out.append(DIG[u])
        return out
    out += ["mười"] if t == 1 else [DIG[t], "mươi"]
    if u == 1 and t > 1:
        out.append("mốt")
    elif u == 5:
        out.append("lăm")
    elif u == 4 and t > 1:
        out.append("tư")
    elif u:
        out.append(DIG[u])
    return out


def read_int(n, north=True):
    if n == 0:
        return "không"
    units = ["", "nghìn" if north else "ngàn", "triệu", "tỷ", "nghìn tỷ"]
    groups = []
    while n:
        groups.append(n % 1000)
        n //= 1000
    out, started = [], False
    for idx in range(len(groups) - 1, -1, -1):
        g = groups[idx]
        if g == 0:
            continue
        out += read_lt1000(g, full=started, north=north)
        if units[idx]:
            out.append(units[idx])
        started = True
    return " ".join(out)


def read_digits(s):
    return " ".join(DIG[int(c)] for c in s if c.isdigit())


NUM = r"\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?"


def read_number(tok, warn, north=True):
    """Quy ước Việt: chấm = nghìn, phẩy = thập phân. Ghi cảnh báo khi mơ hồ."""
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", tok):
        return read_int(int(tok.replace(".", "")), north)
    if re.fullmatch(r"\d{1,3}(?:,\d{3}){2,}", tok):            # 1,250,000 kiểu Anh
        warn.append(f"số kiểu Anh '{tok}' → đọc như phân cách nghìn")
        return read_int(int(tok.replace(",", "")), north)
    if re.fullmatch(r"\d+[.,]\d+", tok):
        a, b = re.split(r"[.,]", tok)
        if "." in tok:
            warn.append(f"'{tok}': dấu chấm + {len(b)} chữ số → đoán thập phân kiểu Anh")
        elif len(b) == 3:
            warn.append(f"'{tok}': mơ hồ (1,250 = 1.25 hay 1250?) → đọc theo quy ước Việt")
        frac = read_digits(b) if (b.startswith("0") or len(b) > 2) else read_int(int(b), north)
        return f"{read_int(int(a), north)} phẩy {frac}"
    if len(tok) > 1 and tok.startswith("0") or len(tok) > 15:
        return read_digits(tok)
    return read_int(int(tok), north)


# =============================== 4. Segment pipeline ===============================
@dataclass
class Seg:
    raw: str        # đoạn text gốc (LLM sinh)
    spoken: str     # đoạn text để đọc
    cls: str        # "plain" = chưa xử lý; các lớp khác = đã viết lại, stage sau không chạm vào


def rewrite(segs, pattern, fn, cls):
    out = []
    for s in segs:
        if s.cls != "plain":
            out.append(s)
            continue
        pos = 0
        for m in pattern.finditer(s.raw):
            r = fn(m)
            if r is None:                            # stage từ chối (ví dụ ngày không hợp lệ)
                continue
            if m.start() > pos:
                out.append(Seg(s.raw[pos:m.start()], s.raw[pos:m.start()], "plain"))
            out.append(Seg(m.group(0), r, cls))
            pos = m.end()
        if pos < len(s.raw):
            out.append(Seg(s.raw[pos:], s.raw[pos:], "plain"))
    return out


LETTER = dict(A="a", B="bê", C="xê", D="dê", Đ="đê", E="e", F="ép", G="giê", H="hát", I="i",
              J="gi", K="ca", L="e lờ", M="em mờ", N="en nờ", O="o", P="pê", Q="quy", R="e rờ",
              S="ét xì", T="tê", U="u", V="vê", W="vê kép", X="ích xì", Y="i dài", Z="dét")


def spell(s):
    out = []
    for ch in s:
        if ch.isdigit():
            out.append(DIG[int(ch)])
        elif ch.upper() in LETTER:
            out.append(LETTER[ch.upper()])
    return " ".join(out)


def kw_regex(keys, flags=0):
    alt = "|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True))
    return re.compile(rf"(?<!\w)(?:{alt})(?!\w)", flags)


@dataclass
class NormResult:
    spoken: str
    display: str
    segs: list
    warnings: list = field(default_factory=list)


class Normalizer:
    UNITS = {"km/h": "ki lô mét trên giờ", "km": "ki lô mét", "kg": "ki lô gam", "cm": "xen ti mét",
             "mm": "mi li mét", "m2": "mét vuông", "m²": "mét vuông", "m3": "mét khối", "ml": "mi li lít",
             "°C": "độ xê", "GB": "gi ga bai", "MB": "mê ga bai", "Mbps": "mê ga bít trên giây",
             "kW": "ki lô oát", "kWh": "ki lô oát giờ"}
    ABBR = {"TP.HCM": "thành phố Hồ Chí Minh", "TP. HCM": "thành phố Hồ Chí Minh",
            "TPHCM": "thành phố Hồ Chí Minh", "TP.": "thành phố", "UBND": "uỷ ban nhân dân",
            "v.v.": "vân vân", "PGS.TS.": "phó giáo sư tiến sĩ", "PGS.TS": "phó giáo sư tiến sĩ",
            "GS.": "giáo sư", "TS.": "tiến sĩ", "ThS.": "thạc sĩ", "BS.": "bác sĩ", "ĐH": "đại học",
            "CSKH": "chăm sóc khách hàng", "SĐT": "số điện thoại", "VTV": "vê tê vê", "ATM": "ây ti em",
            "USB": "u ét bê", "AI": "ây ai"}
    ROMAN_CTX = r"thế kỷ|thế kỉ|chương|phần|khoá|khóa|quý|đại hội"

    def __init__(self, pre_lexicon=None, post_lexicon=None, alerts=None, north=True, tts_codeswitch=True):
        self.north, self.tts_codeswitch = north, tts_codeswitch
        self.pre = pre_lexicon or {}
        self.post = post_lexicon or {}        # word -> (respelling, scope) ; scope "always" | "no_codeswitch"
        self.alerts = alerts or {}            # word -> lý do
        self._compile()

    def _compile(self):
        cs = {k: v for k, v in self.pre.items()}
        self.re_pre = kw_regex(cs) if cs else None
        post_cs = {k: v for k, v in self.post.items() if k.isupper()}           # "AI" ≠ "ai"
        post_ci = {k: v for k, v in self.post.items() if not k.isupper()}
        self.re_post_cs = kw_regex(post_cs) if post_cs else None
        self.re_post_ci = kw_regex(post_ci, re.I) if post_ci else None
        self.post_lc = {k.lower(): v for k, v in post_ci.items()}
        self.re_alert = kw_regex(self.alerts, re.I) if self.alerts else None
        self.re_abbr = kw_regex(self.ABBR)
        units = "|".join(re.escape(u) for u in sorted(self.UNITS, key=len, reverse=True))
        N = NUM
        self.stages = [
            ("markup", re.compile(r"\[([^\]]+)\]\([^)]+\)|\*\*|__|`+|^[ \t]*#{1,6}[ \t]*|^[ \t]*(?:[-*•]|\d+\.)[ \t]+", re.M), self._markup),
            ("emoji", re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+"), lambda m: ""),
            ("pre_lexicon", self.re_pre, lambda m: self.pre[m.group(0)]),
            ("approx", re.compile(r"~\s?(?=\d)"), lambda m: "khoảng "),
            ("url", re.compile(r"https?://\S+?(?=[.,;:!?]?(?:\s|$))|www\.\S+?(?=[.,;:!?]?(?:\s|$))"), lambda m: "đường dẫn"),
            ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), self._email),
            ("abbr", self.re_abbr, lambda m: self.ABBR[m.group(0)]),
            ("admin", re.compile(r"(?<!\w)(Q|P)\.\s?(\d{1,2})(?!\d)"), lambda m: ("quận " if m.group(1) == "Q" else "phường ") + read_int(int(m.group(2)))),
            ("phone", re.compile(r"(?<![\d.,])(?:\+84|0)\d{2,3}(?:[ .]?\d){6,8}(?![\d])|(?<!\d)1[89]00[ .]?\d{4}(?!\d)"), self._phone),
            ("date", re.compile(r"(?:(?P<ctx>ngày|hôm|sáng|trưa|chiều|tối|đêm|từ|đến|tới|trước|sau)\s+)?(?<![\d/])(?P<d>\d{1,2})/(?P<m>\d{1,2})(?:/(?P<y>\d{4}))?(?![\d/])"), self._date),
            ("time", re.compile(r"(?<![\d.,:])(?P<h>\d{1,2})(?:(?P<sep>[h:g])(?P<mi>\d{2})?)(?:p|ph|phút)?(?![\w:])"), self._time),
            ("percent", re.compile(rf"(?P<a>{N})(?:\s?[-–]\s?(?P<b>{N}))?\s?%"), self._range_unit("phần trăm")),
            ("unit", re.compile(rf"(?P<a>{N})(?:\s?[-–]\s?(?P<b>{N}))?\s?(?P<u>{units})(?![\w/])"), self._unit),
            ("money", re.compile(rf"(?P<cur>\$)\s?(?P<a1>{N})|(?P<a>{N})\s?(?P<u>đồng|đ|vnđ|vnd|VNĐ|VND|USD|usd|\$|k|K|tr)(?P<f>\d)?(?!\w)"), self._money),
            ("code", re.compile(r"(?<!\w)(?:[A-ZĐ]{1,3}\d{2,}[A-Z\d]*|\d{2}[A-Z]{1,2}-?\d{3}\.?\d{2})(?!\w)"), lambda m: spell(m.group(0))),
            ("roman", re.compile(rf"(?P<ctx>{self.ROMAN_CTX})\s+(?P<r>[IVXLC]+)(?!\w)", re.I), self._roman),
            ("ordinal", re.compile(r"(?P<w>thứ|hạng|Thứ|Hạng)\s+(?P<n>\d+)(?!\d)"), self._ordinal),
            ("range", re.compile(rf"(?<![\w.,])(?P<a>{N})\s?[-–]\s?(?P<b>{N})(?![\w])"), self._range_unit("")),
            ("number", re.compile(rf"(?<![\d.,])(?:{N})(?![\d])"), lambda m: read_number(m.group(0), self._w, self.north)),
            ("acronym", re.compile(r"(?<!\w)[A-ZĐ]{2,5}(?!\w)"), self._acronym),
            ("symbol", re.compile(r"\s?&\s?|(?<=[^\W\d_])/(?=[^\W\d_])|[()]|[→⇒]|->"), self._symbol),
            ("post_lexicon_cs", self.re_post_cs, self._post),
            ("post_lexicon_ci", self.re_post_ci, self._post),
        ]

    # ---- verbalizers ----
    def _markup(self, m):
        return m.group(1) if m.group(1) else ""

    def _email(self, m):
        local, dom = m.group(0).split("@", 1)
        return f"{local} a còng {' chấm '.join(dom.split('.'))}"

    def _phone(self, m):
        s = m.group(0)
        if s.startswith("+84"):
            head, s = "cộng tám bốn, ", s[3:]
        else:
            head = ""
        groups = re.split(r"[ .]", s)
        if len(groups) == 1:                                # không có dấu tách → nhóm 4-3-3 / 4-4
            g = groups[0]
            groups = [g[:4], g[4:]] if len(g) == 8 else [g[:4], g[4:7], g[7:]]
        return head + ", ".join(read_digits(g) for g in groups if g)

    def _date(self, m):
        d, mo, y, ctx = int(m["d"]), int(m["m"]), m["y"], m["ctx"]
        if not (1 <= d <= 31 and 1 <= mo <= 12):
            return None
        if d > (29 if mo == 2 else 30 if mo in (4, 6, 9, 11) else 31):
            self._w.append(f"'{m.group(0)}': ngày không tồn tại → vẫn đọc nguyên văn, không tự sửa")
        if not y and not ctx and d < mo <= 10:            # "1/3" trơ trọi → phân số
            self._w.append(f"'{m.group(0)}' không có ngữ cảnh → đọc phân số")
            return f"{read_int(d)} phần {read_int(mo)}"
        day = f"mùng {read_int(d)}" if d <= 10 else read_int(d)
        mon = "tư" if mo == 4 else read_int(mo)
        out = f"{day} tháng {mon}" + (f" năm {read_int(int(y))}" if y else "")
        return f"{ctx} {out}" if ctx else out

    def _time(self, m):
        h, mi, sep = int(m["h"]), m["mi"], m["sep"]
        if h > 24 or (mi and int(mi) >= 60) or (sep == ":" and not mi):
            return None
        prev = m.string[: m.start()].split()
        duration = bool(prev) and prev[-1].lower() in {"trong", "mất", "tầm", "chừng", "khoảng"}
        unit = "tiếng" if duration else "giờ"
        out = f"{read_int(h)} {unit}"
        if mi and int(mi):
            out += f" {read_int(int(mi))} phút"
        return out

    def _range_unit(self, unit):
        def f(m):
            a = read_number(m["a"], self._w, self.north)
            out = a + (f" đến {read_number(m['b'], self._w, self.north)}" if m["b"] else "")
            return f"{out} {unit}".strip()
        return f

    def _unit(self, m):
        return self._range_unit(self.UNITS[m["u"]])(m)

    def _money(self, m):
        if m["cur"]:
            return f"{read_number(m['a1'], self._w, self.north)} đô la"
        a, u, f = m["a"], m["u"], m["f"]
        if u in ("k", "K"):
            return f"{read_number(a, self._w, self.north)} nghìn"
        if u == "tr":
            if f:                                          # 2tr5 = 2.500.000
                return read_int(int(a) * 1_000_000 + int(f) * 100_000, self.north)
            return f"{read_number(a, self._w, self.north)} triệu"
        if u in ("USD", "usd", "$"):
            return f"{read_number(a, self._w, self.north)} đô la"
        return f"{read_number(a, self._w, self.north)} đồng"

    def _roman(self, m):
        val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
        r, tot = m["r"].upper(), 0
        for i, ch in enumerate(r):
            v = val[ch]
            tot += -v if i + 1 < len(r) and val[r[i + 1]] > v else v
        return f"{m['ctx']} {read_int(tot)}"

    def _ordinal(self, m):
        n = int(m["n"])
        word = {1: "nhất", 4: "tư"}.get(n, read_int(n))
        return f"{m['w']} {word}"

    def _acronym(self, m):
        self._w.append(f"viết tắt lạ '{m.group(0)}' → đánh vần (nên thêm vào lexicon)")
        return spell(m.group(0))

    def _symbol(self, m):
        s = m.group(0).strip()
        return {"&": " và ", "/": " hoặc ", "(": ", ", ")": ",", "→": " rồi ", "⇒": " rồi ", "->": " rồi "}[s]

    def _post(self, m):
        key = m.group(0)
        resp, scope = self.post.get(key) or self.post_lc[key.lower()]
        if scope == "always" or not self.tts_codeswitch:
            return resp
        return None                                      # TTS tự đọc code-switch → giữ nguyên

    # ---- entry point ----
    def normalize(self, text):
        self._w = []
        text = ud.normalize("NFC", text)
        segs = [Seg(text, text, "plain")]
        for name, pat, fn in self.stages:
            if pat is not None:
                segs = rewrite(segs, pat, fn, name)
        if self.re_alert:
            for m in self.re_alert.finditer(text):
                self._w.append(f"ALERT '{m.group(0)}': {self.alerts[m.group(0).lower()]}")
        spoken = cleanup("".join(s.spoken for s in segs))
        display = cleanup("".join(s.spoken if s.cls in ("markup", "emoji") else s.raw for s in segs))
        return NormResult(spoken, display, segs, self._w)


def cleanup(s):
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" +([,.;:!?…])", r"\1", s)
    s = re.sub(r",\s*,", ",", s)
    s = re.sub(r",(?=[.!?…;:])", "", s)
    return s.strip()


# ============ 5. Map played fraction → phần display đã phát (bảo thủ theo segment) ============
def played_display_prefix(res: NormResult, frac: float):
    """frac = tỷ lệ audio của chunk đã phát (từ played_sample_offset). Không có alignment
    token↔audio nên ước lượng theo tỷ lệ ký tự của spoken text; segment đã viết lại (số, tiền,
    ngày…) chỉ tính là đã nghe khi phát HẾT segment đó."""
    total = sum(len(s.spoken) for s in res.segs) or 1
    budget, out = frac * total, []
    for s in res.segs:
        L = len(s.spoken)
        if budget >= L:
            out.append(s.spoken if s.cls in ("markup", "emoji") else s.raw)
            budget -= L
            continue
        if s.cls == "plain" and budget > 0:
            cut = s.raw[: int(budget)]
            cut = cut[: cut.rfind(" ")] if " " in cut else ""     # không cắt giữa âm tiết
            out.append(cut)
        break
    return cleanup("".join(out))
```

### Script 1: chunker, bất biến với cách chia token, so với chunker ngây thơ (`/tmp/ch19/chunker_test.py`, đã chạy)

```python
# Chương 19 — Script 1: clause chunker + ThinkFilter.
# (a) In các mệnh đề cho vài câu trả lời mẫu; (b) kiểm tra bất biến với cách chia token:
# cùng một text, chia ngẫu nhiên thành token 1–6 ký tự (5000 lần) phải cho ĐÚNG cùng các chunk;
# (c) so với chunker ngây thơ (cắt ngay khi thấy dấu câu, không nhìn ký tự sau).
import random, re
from bridge import ClauseChunker, ThinkFilter

REPLIES = [
    "Dạ, chuyến bay VN123 của anh khởi hành lúc 14:30 ngày 12/10 từ Nội Bài. Giá vé hiện tại là 1.250.000đ, đã gồm thuế và phí. Anh có muốn em giữ chỗ luôn không ạ?",
    "<think>Người dùng hỏi giá. Cần trả lời ngắn.</think>Dạ. Gói cước 4G giá 3,5 triệu một năm, tức khoảng 290.000đ mỗi tháng, rẻ hơn gói cũ 15%. Anh xem chi tiết tại https://vd.vn/goi nhé!",
    "Văn phòng ở 12 Lý Thái Tổ, Q.1, TP.HCM. Anh liên hệ TS. Nguyễn Văn An qua số 0912.345.678 hoặc email hotro@vd.vn để được hỗ trợ.",
    "Có ba bước: chuẩn bị giấy tờ, nộp hồ sơ, v.v. Sau đó anh chờ khoảng 5-7 ngày làm việc... Rồi bên em sẽ gọi lại ạ.",
    "Ừm... để em kiểm tra lại. Thời gian xử lý là 2h, hoặc có thể lâu hơn nếu hệ thống đang bảo trì, nhưng thường thì không quá một ngày làm việc, anh yên tâm ạ.",
]


def stream(text, sizes):
    tf, ch, out = ThinkFilter(), ClauseChunker(), []
    i = 0
    for n in sizes:
        out += ch.feed(tf.feed(text[i:i + n]))
        i += n
    out += ch.feed(tf.feed(text[i:]) + tf.flush())
    return out + ch.flush()


def naive(text):  # cắt ngay ở .?!;: kể cả trong số/viết tắt/URL; không gộp, không lookahead
    text = re.sub(r"<think>.*?</think>", "", text)
    return [p.strip() for p in re.split(r"(?<=[.?!;:…])", text) if p.strip()]


print("=== (a) Mệnh đề do ClauseChunker sinh (feed cả chuỗi một lần) ===")
for t in REPLIES:
    for k, (c, kind) in enumerate(stream(t, [])):
        print(f"  [{k}] {kind:8s} {len(c):3d}c | {c}")
    print()

print("=== (b) Bất biến với cách chia token ===")
rng = random.Random(19)
for idx, t in enumerate(REPLIES):
    ref = stream(t, [])
    bad = 0
    for _ in range(5000):
        sizes, tot = [], 0
        while tot < len(t):
            s = rng.randint(1, 6)
            sizes.append(s)
            tot += s
        if stream(t, sizes) != ref:
            bad += 1
    char_by_char = stream(t, [1] * len(t)) == ref
    print(f"  reply {idx}: {len(ref)} chunk, khác tham chiếu {bad}/5000 lần chia ngẫu nhiên; từng-ký-tự khớp: {char_by_char}")

print("\n=== (c) Chunker ngây thơ trên cùng câu trả lời ===")
for t in REPLIES[1:4]:
    print("  " + " | ".join(naive(t)))
```

Output:

```text
=== (a) Mệnh đề do ClauseChunker sinh (feed cả chuỗi một lần) ===
  [0] term      71c | Dạ, chuyến bay VN123 của anh khởi hành lúc 14:30 ngày 12/10 từ Nội Bài.
  [1] term      50c | Giá vé hiện tại là 1.250.000đ, đã gồm thuế và phí.
  [2] term      36c | Anh có muốn em giữ chỗ luôn không ạ?

  [0] comma     38c | Dạ. Gói cước 4G giá 3,5 triệu một năm,
  [1] term      49c | tức khoảng 290.000đ mỗi tháng, rẻ hơn gói cũ 15%.
  [2] term      43c | Anh xem chi tiết tại https://vd.vn/goi nhé!

  [0] comma     26c | Văn phòng ở 12 Lý Thái Tổ,
  [1] term      12c | Q.1, TP.HCM.
  [2] term      88c | Anh liên hệ TS. Nguyễn Văn An qua số 0912.345.678 hoặc email hotro@vd.vn để được hỗ trợ.

  [0] term      11c | Có ba bước:
  [1] term      33c | chuẩn bị giấy tờ, nộp hồ sơ, v.v.
  [2] term      42c | Sau đó anh chờ khoảng 5-7 ngày làm việc...
  [3] term      24c | Rồi bên em sẽ gọi lại ạ.

  [0] term      25c | Ừm... để em kiểm tra lại.
  [1] comma    115c | Thời gian xử lý là 2h, hoặc có thể lâu hơn nếu hệ thống đang bảo trì, nhưng thường thì không quá một ngày làm việc,
  [2] term      14c | anh yên tâm ạ.

=== (b) Bất biến với cách chia token ===
  reply 0: 3 chunk, khác tham chiếu 0/5000 lần chia ngẫu nhiên; từng-ký-tự khớp: True
  reply 1: 3 chunk, khác tham chiếu 0/5000 lần chia ngẫu nhiên; từng-ký-tự khớp: True
  reply 2: 3 chunk, khác tham chiếu 0/5000 lần chia ngẫu nhiên; từng-ký-tự khớp: True
  reply 3: 4 chunk, khác tham chiếu 0/5000 lần chia ngẫu nhiên; từng-ký-tự khớp: True
  reply 4: 3 chunk, khác tham chiếu 0/5000 lần chia ngẫu nhiên; từng-ký-tự khớp: True

=== (c) Chunker ngây thơ trên cùng câu trả lời ===
  Dạ. | Gói cước 4G giá 3,5 triệu một năm, tức khoảng 290. | 000đ mỗi tháng, rẻ hơn gói cũ 15%. | Anh xem chi tiết tại https: | //vd. | vn/goi nhé!
  Văn phòng ở 12 Lý Thái Tổ, Q. | 1, TP. | HCM. | Anh liên hệ TS. | Nguyễn Văn An qua số 0912. | 345. | 678 hoặc email hotro@vd. | vn để được hỗ trợ.
  Có ba bước: | chuẩn bị giấy tờ, nộp hồ sơ, v. | v. | Sau đó anh chờ khoảng 5-7 ngày làm việc. | . | . | Rồi bên em sẽ gọi lại ạ.
```

### Script 2: normalizer, lexicon hai pha, regression, display/spoken, alignment (`/tmp/ch19/normalizer_test.py`, đã chạy)

```python
# Chương 19 — Script 2: normalizer + lexicon hai pha + regression (golden test).
# Mỗi ca: (lớp, input, spoken mong đợi). In PASS/FAIL, cảnh báo, rồi demo display/spoken,
# code-switch on/off, alert, và map played fraction → phần display đã phát.
import json, sys
from bridge import Normalizer, ClauseChunker, played_display_prefix

PRE = {"COVID-19": "cô vít mười chín", "iPhone 15": "ai phôn mười lăm", "4G": "bốn giê",
       "5G": "năm giê", "OK": "ô kê", "VN": "vê en"}
POST = {"Shopee": ("sốp pi", "always"), "email": ("i meo", "no_codeswitch"),
        "deadline": ("đét lai", "no_codeswitch"), "online": ("on lai", "no_codeswitch"),
        "Facebook": ("phây búc", "no_codeswitch")}
ALERTS = {"chánh": "issue #207: VieNeu v3 Turbo được báo đọc thành 'tránh' (Reported/Unverified)"}

CASES = [
    ("unicode",  "Hoà bình",                         "Hoà bình"),
    ("tiền",     "Giá 1.250.000đ.",                  "Giá một triệu hai trăm năm mươi nghìn đồng."),
    ("tiền",     "Phí 50k mỗi lần",                  "Phí năm mươi nghìn mỗi lần"),
    ("tiền",     "Lương 2tr5",                       "Lương hai triệu năm trăm nghìn"),
    ("tiền",     "Gói $10 hoặc 25 USD",              "Gói mười đô la hoặc hai mươi lăm đô la"),
    ("tiền",     "Còn 105.000 VNĐ",                  "Còn một trăm linh năm nghìn đồng"),
    ("số",       "Năm 2024 có 21 sự kiện",           "Năm hai nghìn không trăm hai mươi tư có hai mươi mốt sự kiện"),
    ("số",       "Tỷ lệ 3,5 và 0,05",                "Tỷ lệ ba phẩy năm và không phẩy không năm"),
    ("số",       "Mã giảm 007",                      "Mã giảm không không bảy"),
    ("số",       "Mất 1.005 ngày",                   "Mất một nghìn không trăm linh năm ngày"),
    ("phần trăm","Giảm 15% và 3-5%",                 "Giảm mười lăm phần trăm và ba đến năm phần trăm"),
    ("đơn vị",   "Chạy 120km/h, nặng 5kg",           "Chạy một trăm hai mươi ki lô mét trên giờ, nặng năm ki lô gam"),
    ("đơn vị",   "Căn hộ 75m2, 30°C",                "Căn hộ bảy mươi lăm mét vuông, ba mươi độ xê"),
    ("ngày",     "ngày 01/05/2025",                  "ngày mùng một tháng năm năm hai nghìn không trăm hai mươi lăm"),
    ("ngày",     "Hạn 12/4",                         "Hạn mười hai tháng tư"),
    ("ngày",     "giảm 1/3 giá",                     "giảm một phần ba giá"),
    ("ngày",     "Đóng 31/02",                       "Đóng ba mươi mốt tháng hai"),
    ("giờ",      "Họp lúc 14:30",                    "Họp lúc mười bốn giờ ba mươi phút"),
    ("giờ",      "Mở cửa 8h",                        "Mở cửa tám giờ"),
    ("giờ",      "Xử lý trong 2h",                   "Xử lý trong hai tiếng"),
    ("điện thoại","Gọi 0912 345 678",                "Gọi không chín một hai, ba bốn năm, sáu bảy tám"),
    ("điện thoại","Số 0912.345.678 nhé",             "Số không chín một hai, ba bốn năm, sáu bảy tám nhé"),
    ("điện thoại","Hotline 1900 1234",               "Hotline một chín không không, một hai ba bốn"),
    ("thứ tự",   "Thứ 2 và hạng 1",                  "Thứ hai và hạng nhất"),
    ("thứ tự",   "thế kỷ XXI",                       "thế kỷ hai mươi mốt"),
    ("khoảng",   "Chờ 5-7 ngày",                     "Chờ năm đến bảy ngày"),
    ("viết tắt", "UBND TP.HCM",                      "uỷ ban nhân dân thành phố Hồ Chí Minh"),
    ("viết tắt", "Ở Q.1, gặp PGS.TS. Lan",           "Ở quận một, gặp phó giáo sư tiến sĩ Lan"),
    ("viết tắt", "giấy tờ, v.v.",                    "giấy tờ, vân vân"),
    ("viết tắt", "Hỏi ai cũng biết AI",              "Hỏi ai cũng biết ây ai"),
    ("viết tắt", "Liên hệ BHXH",                     "Liên hệ bê hát ích xì hát"),
    ("mã",       "Chuyến VN123",                     "Chuyến vê en nờ một hai ba"),
    ("mã",       "Xe 30A-123.45",                    "Xe ba không a một hai ba bốn năm"),
    ("lexicon",  "Dịch COVID-19 và mạng 4G",         "Dịch cô vít mười chín và mạng bốn giê"),
    ("lexicon",  "Mua iPhone 15 trên Shopee",        "Mua ai phôn mười lăm trên sốp pi"),
    ("lexicon",  "Ứng dụng Pinterest",               "Ứng dụng Pinterest"),
    ("url",      "Xem tại https://vd.vn/goi nhé.",   "Xem tại đường dẫn nhé."),
    ("email",    "Gửi hotro@vd.vn",                  "Gửi hotro a còng vd chấm vn"),
    ("markup",   "**Lưu ý:** mang CCCD 😊",          "Lưu ý: mang xê xê xê dê"),
    ("markup",   "- Bước 1: nộp đơn",                "Bước một: nộp đơn"),
    ("ký hiệu",  "Có/Không & ~5 phút",               "Có hoặc Không và khoảng năm phút"),
    ("mơ hồ",    "Giá 1,250 đồng",                   "Giá một phẩy hai năm không đồng"),
    ("mơ hồ",    "Tăng 3.5 lần",                     "Tăng ba phẩy năm lần"),
    ("alert",    "Chánh văn phòng",                  "Chánh văn phòng"),
]

norm = Normalizer(PRE, POST, ALERTS, tts_codeswitch=True)
fails = 0
print("=== Regression: normalizer (tts_codeswitch=True) ===")
for cls, inp, exp in CASES:
    r = norm.normalize(inp)
    ok = r.spoken == exp
    fails += not ok
    mark = "PASS" if ok else "FAIL"
    print(f"{mark} [{cls:10s}] {inp!r:36} → {r.spoken!r}")
    if not ok:
        print(f"      expected {exp!r}")
    for w in r.warnings:
        print(f"      ⚠ {w}")
print(f"\n{len(CASES) - fails}/{len(CASES)} PASS")

print("\n=== Code-switch: cùng câu, TTS đọc được tiếng Anh (True) và không (False) ===")
s = "Anh check email và họp online trước deadline nhé, link gửi qua Facebook."
for flag in (True, False):
    print(f"  tts_codeswitch={flag!s:5}: {Normalizer(PRE, POST, ALERTS, tts_codeswitch=flag).normalize(s).spoken}")

print("\n=== Một câu trả lời đi qua chunker → normalizer: display vs spoken ===")
reply = ("Dạ, chuyến bay VN123 khởi hành lúc 14:30 ngày 12/10 từ Nội Bài. "
         "Giá vé là **1.250.000đ**, đã gồm thuế. Anh gọi 0912 345 678 nếu cần ạ 😊")
ch = ClauseChunker()
chunks = ch.feed(reply) + ch.flush()
records = []
for k, (raw, kind) in enumerate(chunks):
    r = norm.normalize(raw)
    records.append(r)
    print(json.dumps({"chunk_id": k, "raw_text": raw, "display_text": r.display, "spoken_text": r.spoken},
                     ensure_ascii=False))

print("\n=== played fraction → phần display user đã nghe (chunk 1) ===")
for frac in (0.2, 0.45, 0.6, 0.9, 1.0):
    print(f"  {frac:4.0%}: {played_display_prefix(records[1], frac)!r}")

sys.exit(1 if fails else 0)
```

Output (lần chạy cuối, sau khi sửa 5 ca FAIL của lần đầu như mô tả ở §19.10.4):

```text
=== Regression: normalizer (tts_codeswitch=True) ===
PASS [unicode   ] 'Hoà bình'                           → 'Hoà bình'
PASS [tiền      ] 'Giá 1.250.000đ.'                    → 'Giá một triệu hai trăm năm mươi nghìn đồng.'
PASS [tiền      ] 'Phí 50k mỗi lần'                    → 'Phí năm mươi nghìn mỗi lần'
PASS [tiền      ] 'Lương 2tr5'                         → 'Lương hai triệu năm trăm nghìn'
PASS [tiền      ] 'Gói $10 hoặc 25 USD'                → 'Gói mười đô la hoặc hai mươi lăm đô la'
PASS [tiền      ] 'Còn 105.000 VNĐ'                    → 'Còn một trăm linh năm nghìn đồng'
PASS [số        ] 'Năm 2024 có 21 sự kiện'             → 'Năm hai nghìn không trăm hai mươi tư có hai mươi mốt sự kiện'
PASS [số        ] 'Tỷ lệ 3,5 và 0,05'                  → 'Tỷ lệ ba phẩy năm và không phẩy không năm'
PASS [số        ] 'Mã giảm 007'                        → 'Mã giảm không không bảy'
PASS [số        ] 'Mất 1.005 ngày'                     → 'Mất một nghìn không trăm linh năm ngày'
PASS [phần trăm ] 'Giảm 15% và 3-5%'                   → 'Giảm mười lăm phần trăm và ba đến năm phần trăm'
PASS [đơn vị    ] 'Chạy 120km/h, nặng 5kg'             → 'Chạy một trăm hai mươi ki lô mét trên giờ, nặng năm ki lô gam'
PASS [đơn vị    ] 'Căn hộ 75m2, 30°C'                  → 'Căn hộ bảy mươi lăm mét vuông, ba mươi độ xê'
PASS [ngày      ] 'ngày 01/05/2025'                    → 'ngày mùng một tháng năm năm hai nghìn không trăm hai mươi lăm'
PASS [ngày      ] 'Hạn 12/4'                           → 'Hạn mười hai tháng tư'
PASS [ngày      ] 'giảm 1/3 giá'                       → 'giảm một phần ba giá'
      ⚠ '1/3' không có ngữ cảnh → đọc phân số
PASS [ngày      ] 'Đóng 31/02'                         → 'Đóng ba mươi mốt tháng hai'
      ⚠ '31/02': ngày không tồn tại → vẫn đọc nguyên văn, không tự sửa
PASS [giờ       ] 'Họp lúc 14:30'                      → 'Họp lúc mười bốn giờ ba mươi phút'
PASS [giờ       ] 'Mở cửa 8h'                          → 'Mở cửa tám giờ'
PASS [giờ       ] 'Xử lý trong 2h'                     → 'Xử lý trong hai tiếng'
PASS [điện thoại] 'Gọi 0912 345 678'                   → 'Gọi không chín một hai, ba bốn năm, sáu bảy tám'
PASS [điện thoại] 'Số 0912.345.678 nhé'                → 'Số không chín một hai, ba bốn năm, sáu bảy tám nhé'
PASS [điện thoại] 'Hotline 1900 1234'                  → 'Hotline một chín không không, một hai ba bốn'
PASS [thứ tự    ] 'Thứ 2 và hạng 1'                    → 'Thứ hai và hạng nhất'
PASS [thứ tự    ] 'thế kỷ XXI'                         → 'thế kỷ hai mươi mốt'
PASS [khoảng    ] 'Chờ 5-7 ngày'                       → 'Chờ năm đến bảy ngày'
PASS [viết tắt  ] 'UBND TP.HCM'                        → 'uỷ ban nhân dân thành phố Hồ Chí Minh'
PASS [viết tắt  ] 'Ở Q.1, gặp PGS.TS. Lan'             → 'Ở quận một, gặp phó giáo sư tiến sĩ Lan'
PASS [viết tắt  ] 'giấy tờ, v.v.'                      → 'giấy tờ, vân vân'
PASS [viết tắt  ] 'Hỏi ai cũng biết AI'                → 'Hỏi ai cũng biết ây ai'
PASS [viết tắt  ] 'Liên hệ BHXH'                       → 'Liên hệ bê hát ích xì hát'
      ⚠ viết tắt lạ 'BHXH' → đánh vần (nên thêm vào lexicon)
PASS [mã        ] 'Chuyến VN123'                       → 'Chuyến vê en nờ một hai ba'
PASS [mã        ] 'Xe 30A-123.45'                      → 'Xe ba không a một hai ba bốn năm'
PASS [lexicon   ] 'Dịch COVID-19 và mạng 4G'           → 'Dịch cô vít mười chín và mạng bốn giê'
PASS [lexicon   ] 'Mua iPhone 15 trên Shopee'          → 'Mua ai phôn mười lăm trên sốp pi'
PASS [lexicon   ] 'Ứng dụng Pinterest'                 → 'Ứng dụng Pinterest'
PASS [url       ] 'Xem tại https://vd.vn/goi nhé.'     → 'Xem tại đường dẫn nhé.'
PASS [email     ] 'Gửi hotro@vd.vn'                    → 'Gửi hotro a còng vd chấm vn'
PASS [markup    ] '**Lưu ý:** mang CCCD 😊'             → 'Lưu ý: mang xê xê xê dê'
      ⚠ viết tắt lạ 'CCCD' → đánh vần (nên thêm vào lexicon)
PASS [markup    ] '- Bước 1: nộp đơn'                  → 'Bước một: nộp đơn'
PASS [ký hiệu   ] 'Có/Không & ~5 phút'                 → 'Có hoặc Không và khoảng năm phút'
PASS [mơ hồ     ] 'Giá 1,250 đồng'                     → 'Giá một phẩy hai năm không đồng'
      ⚠ '1,250': mơ hồ (1,250 = 1.25 hay 1250?) → đọc theo quy ước Việt
PASS [mơ hồ     ] 'Tăng 3.5 lần'                       → 'Tăng ba phẩy năm lần'
      ⚠ '3.5': dấu chấm + 1 chữ số → đoán thập phân kiểu Anh
PASS [alert     ] 'Chánh văn phòng'                    → 'Chánh văn phòng'
      ⚠ ALERT 'Chánh': issue #207: VieNeu v3 Turbo được báo đọc thành 'tránh' (Reported/Unverified)

44/44 PASS

=== Code-switch: cùng câu, TTS đọc được tiếng Anh (True) và không (False) ===
  tts_codeswitch=True : Anh check email và họp online trước deadline nhé, link gửi qua Facebook.
  tts_codeswitch=False: Anh check i meo và họp on lai trước đét lai nhé, link gửi qua phây búc.

=== Một câu trả lời đi qua chunker → normalizer: display vs spoken ===
{"chunk_id": 0, "raw_text": "Dạ, chuyến bay VN123 khởi hành lúc 14:30 ngày 12/10 từ Nội Bài.", "display_text": "Dạ, chuyến bay VN123 khởi hành lúc 14:30 ngày 12/10 từ Nội Bài.", "spoken_text": "Dạ, chuyến bay vê en nờ một hai ba khởi hành lúc mười bốn giờ ba mươi phút ngày mười hai tháng mười từ Nội Bài."}
{"chunk_id": 1, "raw_text": "Giá vé là **1.250.000đ**, đã gồm thuế.", "display_text": "Giá vé là 1.250.000đ, đã gồm thuế.", "spoken_text": "Giá vé là một triệu hai trăm năm mươi nghìn đồng, đã gồm thuế."}
{"chunk_id": 2, "raw_text": "Anh gọi 0912 345 678 nếu cần ạ 😊", "display_text": "Anh gọi 0912 345 678 nếu cần ạ", "spoken_text": "Anh gọi không chín một hai, ba bốn năm, sáu bảy tám nếu cần ạ"}

=== played fraction → phần display user đã nghe (chunk 1) ===
   20%: 'Giá vé là'
   45%: 'Giá vé là'
   60%: 'Giá vé là'
   90%: 'Giá vé là 1.250.000đ, đã'
  100%: 'Giá vé là 1.250.000đ, đã gồm thuế.'
```

Đo tốc độ (chạy riêng, cùng máy): `Normalizer.normalize` trên chuỗi 86 ký tự mất 0,090 ms/lần (trung bình 5000 lần); `ClauseChunker` xử lý một câu trả lời 258 ký tự nhận 4 ký tự mỗi lần mất 0,148 ms.

### Script 3: mô phỏng chính sách flush (`/tmp/ch19/flush_sim.py`, đã chạy)

```python
# Chương 19 — Script 3: mô phỏng rời rạc chính sách flush (token / mệnh đề / câu / 3 câu / cả câu trả lời)
# × backend TTS × số slot TTS mỗi session. Mọi tham số là GIẢ ĐỊNH để thấy HÌNH DẠNG đánh đổi,
# không phải đo model thật. Mỗi request TTS thêm EDGE_SIL giây im lặng đầu/cuối (giả định). TTS "GPU" lấy TTFA 115 ms, RTF 0.49 (VieNeu RTX 3060, 1 stream, Reported);
# TTS "CPU int8" lấy TTFA = 131 + 0.42·số ký tự (đường thẳng nối 3 điểm Reported 27/88/147 ký tự →
# ~142/166/193 ms; phép khớp là Synthesis), RTF 0.35. LLM: mỗi từ = 1.5 token. Giọng đọc 5 âm tiết/s.
from bridge import ClauseChunker, Normalizer

REPLY = ("Dạ, em đã kiểm tra lịch bay cho anh rồi, chuyến VN123 khởi hành lúc 14:30 ngày 12/10 từ Nội Bài "
         "và đến Tân Sơn Nhất lúc 16:40. Giá vé hiện tại là 1.250.000đ, đã gồm thuế và phí sân bay. "
         "Nếu anh muốn, em có thể giữ chỗ trong 24 giờ để anh cân nhắc thêm. Anh có muốn em giữ chỗ luôn không ạ?")
NORM = Normalizer()
SYL_RATE = 5.0
EDGE_SIL = 0.15                                    # im lặng đầu+cuối mỗi request TTS (giả định)


def llm_events(ttft, tok_s):
    words = [w + " " for w in REPLY.split(" ")]
    t = ttft
    for w in words:
        yield t, w
        t += 1.5 / tok_s
    yield t, None                                  # done


def chunks_for(policy, ttft, tok_s):
    """Trả về [(ready_time, raw_text)]."""
    out = []
    if policy == "token":
        return [(t, w.strip()) for t, w in llm_events(ttft, tok_s) if w]
    if policy == "full":
        evs = list(llm_events(ttft, tok_s))
        return [(evs[-1][0], REPLY)]
    big = 10 ** 9
    ch = {"clause": ClauseChunker(), "clause+": ClauseChunker(later_comma_min=25),
          "sentence": ClauseChunker(first_min=big, later_comma_min=big), "3sent": ClauseChunker(first_min=big, later_comma_min=big)}[policy]
    pending, ready = [], []
    for t, w in llm_events(ttft, tok_s):
        got = ch.feed(w) if w else ch.flush()
        for text, _ in got:
            ready.append((t, text))
    if policy in ("clause", "clause+", "sentence"):
        return ready
    if policy == "3sent":                          # gom 3 câu/lần gọi TTS
        for i in range(0, len(ready), 3):
            grp = ready[i:i + 3]
            out.append((grp[-1][0], " ".join(x for _, x in grp)))
        return out


def tts_model(kind, spoken):
    if kind == "gpu":
        return 0.115, 0.49
    return (131 + 0.42 * len(spoken)) / 1000, 0.35


def simulate(policy, ttft, tok_s, tts, slots):
    chunks = chunks_for(policy, ttft, tok_s)
    slot_free = [0.0] * slots
    play_end, first_audio, gaps = None, None, []
    for ready, raw in chunks:
        spoken = NORM.normalize(raw).spoken
        dur = max(len(spoken.split()), 1) / SYL_RATE + EDGE_SIL
        ttfa, rtf = tts_model(tts, spoken)
        s = min(range(slots), key=lambda i: slot_free[i])
        start = max(ready, slot_free[s])
        slot_free[s] = start + ttfa + dur * rtf    # slot bận tới khi sinh xong chunk
        avail = start + ttfa
        if play_end is None:
            first_audio, play_start = avail, avail
        else:
            play_start = max(play_end, avail)
            gaps.append(play_start - play_end)
        play_end = play_start + dur
    big = [g for g in gaps if g > 0.15]
    return dict(first=first_audio, n=len(chunks), gap_sum=sum(gaps), gap_max=max(gaps, default=0),
                n_big=len(big), end=play_end)


SCEN = [("LLM nhanh 40 tok/s · TTS GPU", 0.30, 40, "gpu", 1),
        ("LLM nhanh 40 tok/s · TTS CPU int8 · 1 slot", 0.30, 40, "cpu", 1),
        ("LLM nhanh 40 tok/s · TTS CPU int8 · 2 slot", 0.30, 40, "cpu", 2),
        ("LLM chậm 8 tok/s · TTS CPU int8 · 1 slot", 0.30, 8, "cpu", 1)]

print(f"Câu trả lời: {len(REPLY)} ký tự, {len(REPLY.split())} từ; spoken {len(NORM.normalize(REPLY).spoken.split())} âm tiết "
      f"≈ {len(NORM.normalize(REPLY).spoken.split()) / SYL_RATE:.1f} s audio\n")
for name, ttft, tok, tts, slots in SCEN:
    print(f"--- {name} (TTFT {ttft*1000:.0f} ms) ---")
    print(f"{'chính sách':10s} {'#req':>5s} {'audio đầu':>10s} {'tổng gap':>9s} {'gap max':>8s} {'#gap>150ms':>10s} {'kết thúc':>9s}")
    for pol in ("token", "clause", "clause+", "sentence", "3sent", "full"):
        r = simulate(pol, ttft, tok, tts, slots)
        print(f"{pol:10s} {r['n']:5d} {r['first']*1000:8.0f}ms {r['gap_sum']*1000:7.0f}ms {r['gap_max']*1000:6.0f}ms "
              f"{r['n_big']:10d} {r['end']:8.2f}s")
    print()

for pol, tok in (("clause", 40), ("clause+", 8)):
    print(f"Chunk của '{pol}' (thời điểm sẵn sàng, LLM {tok} tok/s):")
    for t, c in chunks_for(pol, 0.30, tok):
        print(f"  {t*1000:6.0f} ms  {len(c):3d}c  {c}")

print("\nLLM chậm 8 tok/s · CPU int8 · 1 slot: thêm trần độ dài cứng (hard_max) cho 'clause+'")
for hm in (180, 60, 45):
    def cf(policy, ttft, tok_s, hm=hm):
        ch, ready = ClauseChunker(later_comma_min=25, hard_max=hm), []
        for t, w in llm_events(ttft, tok_s):
            for text, _ in (ch.feed(w) if w else ch.flush()):
                ready.append((t, text))
        return ready
    chunks_for = cf
    r = simulate("x", 0.30, 8, "cpu", 1)
    print(f"  hard_max={hm:3d}: #req {r['n']}, audio đầu {r['first']*1000:.0f} ms, gap max {r['gap_max']*1000:.0f} ms, "
          f"kết thúc {r['end']:.2f} s | chunk 2–3: {[c for _, c in cf('x', 0.3, 8)][1:3]}")
```

Output:

```text
Câu trả lời: 289 ký tự, 66 từ; spoken 93 âm tiết ≈ 18.6 s audio

--- LLM nhanh 40 tok/s · TTS GPU (TTFT 300 ms) ---
chính sách  #req  audio đầu  tổng gap  gap max #gap>150ms  kết thúc
token         66      415ms       0ms      0ms          0    28.92s
clause         5      752ms       0ms      0ms          0    20.10s
clause+        6      752ms       0ms      0ms          0    20.25s
sentence       4     1428ms       0ms      0ms          0    20.63s
3sent          2     2515ms       0ms      0ms          0    21.42s
full           1     2890ms       0ms      0ms          0    21.64s

--- LLM nhanh 40 tok/s · TTS CPU int8 · 1 slot (TTFT 300 ms) ---
chính sách  #req  audio đầu  tổng gap  gap max #gap>150ms  kết thúc
token         66      432ms       0ms      0ms          0    28.93s
clause         5      785ms       0ms      0ms          0    20.14s
clause+        6      785ms       0ms      0ms          0    20.29s
sentence       4     1525ms       0ms      0ms          0    20.73s
3sent          2     2681ms       0ms      0ms          0    21.58s
full           1     3072ms       0ms      0ms          0    21.82s

--- LLM nhanh 40 tok/s · TTS CPU int8 · 2 slot (TTFT 300 ms) ---
chính sách  #req  audio đầu  tổng gap  gap max #gap>150ms  kết thúc
token         66      432ms       0ms      0ms          0    28.93s
clause         5      785ms       0ms      0ms          0    20.14s
clause+        6      785ms       0ms      0ms          0    20.29s
sentence       4     1525ms       0ms      0ms          0    20.73s
3sent          2     2681ms       0ms      0ms          0    21.58s
full           1     3072ms       0ms      0ms          0    21.82s

--- LLM chậm 8 tok/s · TTS CPU int8 · 1 slot (TTFT 300 ms) ---
chính sách  #req  audio đầu  tổng gap  gap max #gap>150ms  kết thúc
token         66      432ms       0ms      0ms          0    28.93s
clause         5     2135ms    1273ms   1273ms          1    22.76s
clause+        6     2135ms    1273ms   1273ms          1    22.91s
sentence       4     5575ms       0ms      0ms          0    24.78s
3sent          2    11081ms       0ms      0ms          0    29.98s
full           1    12972ms       0ms      0ms          0    31.72s

Chunk của 'clause' (thời điểm sẵn sàng, LLM 40 tok/s):
     637 ms   40c  Dạ, em đã kiểm tra lịch bay cho anh rồi,
    1313 ms   85c  chuyến VN123 khởi hành lúc 14:30 ngày 12/10 từ Nội Bài và đến Tân Sơn Nhất lúc 16:40.
    1800 ms   58c  Giá vé hiện tại là 1.250.000đ, đã gồm thuế và phí sân bay.
    2400 ms   66c  Nếu anh muốn, em có thể giữ chỗ trong 24 giờ để anh cân nhắc thêm.
    2738 ms   36c  Anh có muốn em giữ chỗ luôn không ạ?
Chunk của 'clause+' (thời điểm sẵn sàng, LLM 8 tok/s):
    1988 ms   40c  Dạ, em đã kiểm tra lịch bay cho anh rồi,
    5362 ms   85c  chuyến VN123 khởi hành lúc 14:30 ngày 12/10 từ Nội Bài và đến Tân Sơn Nhất lúc 16:40.
    6488 ms   30c  Giá vé hiện tại là 1.250.000đ,
    7800 ms   27c  đã gồm thuế và phí sân bay.
   10800 ms   66c  Nếu anh muốn, em có thể giữ chỗ trong 24 giờ để anh cân nhắc thêm.
   12488 ms   36c  Anh có muốn em giữ chỗ luôn không ạ?

LLM chậm 8 tok/s · CPU int8 · 1 slot: thêm trần độ dài cứng (hard_max) cho 'clause+'
  hard_max=180: #req 6, audio đầu 2135 ms, gap max 1273 ms, kết thúc 22.91 s | chunk 2–3: ['chuyến VN123 khởi hành lúc 14:30 ngày 12/10 từ Nội Bài và đến Tân Sơn Nhất lúc 16:40.', 'Giá vé hiện tại là 1.250.000đ,']
  hard_max= 60: #req 8, audio đầu 2135 ms, gap max 315 ms, kết thúc 22.25 s | chunk 2–3: ['chuyến VN123 khởi hành lúc 14:30 ngày 12/10 từ Nội Bài và', 'đến Tân Sơn Nhất lúc 16:40.']
  hard_max= 45: #req 8, audio đầu 2135 ms, gap max 0 ms, kết thúc 21.94 s | chunk 2–3: ['chuyến VN123 khởi hành lúc 14:30 ngày 12/10', 'từ Nội Bài và đến Tân Sơn Nhất lúc 16:40.']
```

### Liên kết sang chương khác

- Chương 5 (ngữ âm, chữ viết): bảng semiotic class, quy tắc đọc số, NFC, G2P, lexicon cơ bản, code-switch. Chương này xây trên đó.
- Chương 12 (LLM): prompt cho văn nói, TTFC, underrun, lọc `<think>`, history `[bị ngắt]`.
- Chương 13 (TTS): audio-output streaming và bi-streaming, dấu câu là núm prosody, round-trip CER chỉ là proxy.
- Chương 16 (dataflow): cạnh T2/T3, bảng `chunk_id → khoảng mẫu`, played offset.
- Chương 17 (turn-taking): owner, `generation_id`, cắt history theo phần đã phát.
- Chương 18 (async): bounded queue, `aclosing`, response scope, ngân sách giữa hai `await`.
- Chương 20 (latency): `ttfc`, `first_sentence→tts_first_byte`, `inter_chunk_gap` trên critical path.
- Chương 21 (đánh giá): tập nghe 150–300 prompt, CMOS ranh giới chunk, gate release.

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) — §5.5 (giao diện LLM; chunker: flush `.?!…;:`/xuống dòng, chunk đầu cắt ở phẩy khi ≥ ~25 ký tự, gộp mảnh < 8 ký tự, không flush từng token, đơn vị 20–60 ký tự; bảng normalizer; NFC, strip markup/URL, giữ dấu câu, regression prompts; chưa chọn được thư viện normalizer; lexicon và issue #207; hai nghĩa của streaming TTS), §7.2 (`text.chunk(generation_id, chunk_id, raw_text, spoken_text)`), §7.3 (history chỉ lưu phần đã phát, tag `[bị ngắt]`; không có alignment thì chỉ khẳng định played offset), §8.1 (chunker ở consumer của LLM stream), §10 mục 2 (150–300 prompts, test normalizer/lexicon/ranh giới chunk).
[^stack]: [Vietnamese Realtime Voice Agent Stack](../wiki/vietnamese-realtime-voice-agent-stack.md) — "LLM choice and invocation" (prompt 1–3 câu, không markdown/emoji/bảng/URL, số và ngày viết bằng chữ hoặc để normalizer; luật sentence chunking `.?!…;:`, phẩy ≥ ~25 ký tự, gộp < 8 ký tự); "TTS routing and Vietnamese text normalization" (ví dụ `1.250.000đ`, viết tắt, giữ tiếng Anh nếu TTS đọc được code-switch, VieNeu đọc được; substitution dictionary; `chánh` → `tránh` issue #207); "Architecture" (sentence chunker + Vietnamese normalizer, TTS router VieNeu cho `vi`, Qwen3-TTS cho en/zh); "Latency budget" (metric `first_sentence→tts_first_byte`). Nguồn gốc là report AI thứ cấp, **Reported**.
[^blueprint]: [Cascaded Voice-Agent Blueprint](../wiki/cascaded-voice-agent-blueprint.md) — "Turn flow and defaults" bước 5 (sentence-buffered TTS là tối ưu quan trọng nhất) và đoạn ngay sau (loại per-token: prosody không tự nhiên, TTS thiếu context, số request bùng nổ, khe hở nghe được; đơn vị tốt là một câu hoặc ~20–60 ký tự); "Common failures and fixes" (TTS đọc Markdown).
[^community]: [Community-Reported STT-LLM-TTS Pipeline Wiring](../wiki/community-stt-llm-tts-pipeline.md) — "Latency: sentence-chunked streaming and RAG" (gửi vài từ đầu hoặc câu đầu; câu đầy đủ tốt hơn từng từ, ví dụ `I want a...` và `I want a pizza right now!`; Wyoming được báo chia theo ranh giới câu).
[^cli]: [Speech-to-Speech CLI and Defaults](../wiki/speech-to-speech-cli-and-defaults.md) — "LLM base": `stream_batch_sentences=3` (đặt 1 để stream từng câu), **Observed** trong capture.
[^s2s]: [HF Speech-to-Speech Pipeline](../wiki/speech-to-speech-pipeline.md) — "Multilingual behavior" (`--detect_llm_output_language` phát hiện ngôn ngữ từng chunk assistant bằng Lingua; text < 20 ký tự hoặc mơ hồ dùng ngôn ngữ phát hiện gần nhất).
[^cosy]: [CosyVoice2-0.5B](../wiki/cosyvoice2-0.5b.md) — gạch đầu dòng bi-streaming (nhận generator text; người gọi vẫn nên giữ logic chia câu cơ bản vì LLM không xử lý được câu dài tuỳ ý).
[^cosy3]: [Fun-CosyVoice3-0.5B-2512](../wiki/fun-cosyvoice3-0.5b-2512.md) — mô tả (pronunciation inpainting Pinyin/CMU, bi-streaming 150 ms; 9 ngôn ngữ, không có tiếng Việt).
[^vnorm]: [VietNormalizer](../wiki/vietnormalizer.md) — "Capabilities" (bảng ví dụ, `AI` → trí tuệ nhân tạo, `TV` → ti vi; output lowercase; xoá URL/email/emoji; NFC); "Pipeline order" (19 bước; lowercase trước bước từ điển); "API and configuration" (`enable_transliteration`); "Performance and fit" (~0,6 ms/lần gọi, ~40 ms khởi tạo, 17K+ mục; phiên âm tiếng Anh là quy ước của thư viện, không phải của TTS); "Contradictions" (`database`); "Coverage and limits" (chưa cài, chưa chạy). License MIT theo mô tả trang.
[^visonorm]: [ViSoNorm (visobert-normalizer)](../wiki/visonorm-visobert-normalizer.md) — mô tả (chuẩn hoá text mạng xã hội sang tiếng Việt chuẩn, hướng ngược với VietNormalizer); "Mechanism" (`trust_remote_code=True`); "Claims and limits" (không có license, benchmark, latency).
[^vieneu]: [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md) — mô tả và gạch đầu dòng nguồn gốc (khoảng 10.000 giờ dữ liệu Anh–Việt); preset voice ba vùng Bắc/Trung/Nam; v3 Nano kém rõ rệt ở tiếng Anh và câu trộn Anh–Việt; `sea-g2p` là thành phần bên thứ ba; lỗi G2P `chánh` → `tránh` (relayed từ report).
[^vieneuapi]: [VieNeu-TTS OpenAI-Compatible Speech API](../wiki/vieneu-tts-openai-speech-api.md) — bảng trường `POST /v1/audio/speech`: `input` tối đa 20.000 ký tự, chia thành đoạn ≤ `max_chars` ở ranh giới câu; `max_chars` mặc định 256 (64–512); `speed`, `instructions` được nhận nhưng bỏ qua (header `X-VieNeu-Ignored`); `temperature` mặc định 0,8.
[^vieneurt]: [VieNeu-TTS Streaming Runtime and Performance](../wiki/vieneu-tts-streaming-runtime.md) — mở đầu (1 stream ~115 ms TTFA, RTF 0,49 trên RTX 3060); "Choosing `max_streams`" (slot dư làm chậm mọi request); "CPU: how streaming works, measurements" (prompt gồm reference codes + phonemes; bảng TTFA theo độ dài câu 27/88/147 ký tự: fp32 264–282/313–357/345–401 ms, int8 141–144/163–169/192–194 ms; fp32 đúng một stream, request thứ hai xếp hàng rồi `429`).
[^ttssel]: [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md) — thiết kế đề xuất mục 1–2 (LLM streaming → chunker → normalizer → TTS → bounded playback queue; không cắt giữa giá trị đang hoàn thành); đoạn về G2P bug `chánh` → `tránh` (chỉ relayed, dùng như regression case); phần đánh giá (150–300 prompts, lưu raw text và normalized spoken text).
[^kokoro]: [Kokoro Vietnamese](../wiki/kokoro-vietnamese.md) — G2P tiếng Việt bằng `vig2p`, khớp code inference và training (**Reported**); `vig2p` chưa được inspect.
