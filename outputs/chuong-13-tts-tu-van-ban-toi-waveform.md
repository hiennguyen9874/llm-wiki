# Chương 13. TTS: từ văn bản tới waveform 🔴

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần IV.
> **Chương trước:** [Chương 12. LLM trong vòng hội thoại nói](chuong-12-llm-trong-vong-hoi-thoai-noi.md). **Chương tiếp theo:** [Chương 14. Speaker: embedding, speaker lock, diarization](chuong-14-speaker-embedding-speaker-lock-diarization.md).
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.5 (cầu text → speech), §5.6 (TTS tiếng Việt), §8.2 (ngân sách latency), §9.4 (fallback).
> **Cơ sở:** phần giải thích về kiến trúc TTS (text frontend, acoustic model, vocoder, neural codec, RVQ, flow matching, diffusion), xử lý tín hiệu (resample, lượng tử hoá) và đánh giá (MOS, CMOS) là kiến thức nền chung, không phải claim lấy từ nguồn wiki. Tham số và hành vi cụ thể lấy từ wiki và gắn nhãn bằng chứng: [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md), [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md), [VieNeu-TTS Streaming Runtime and Performance](../wiki/vieneu-tts-streaming-runtime.md), [VieNeu-TTS OpenAI-compatible Speech API](../wiki/vieneu-tts-openai-speech-api.md), [Qwen3-TTS-Tokenizer-12Hz](../wiki/qwen3-tts-tokenizer-12hz.md), [VietNormalizer](../wiki/vietnormalizer.md), [TTS Model Survey](../wiki/tts-model-survey.md), cùng các trang pipeline ở đầu chương 12. Số liệu wiki là **Reported** (chưa chạy lại model nào). Các mô phỏng ở §13.4.2, §13.8.3 và §13.9 chạy bằng script Python thuần (**Reproduced**, script ở "Phụ lục chương"); chúng chỉ minh hoạ số học và logic, không đo model thật. Suy luận của tác giả là **Synthesis**.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Vẽ được chuỗi **text → normalization → G2P → acoustic model → vocoder** và chuỗi **text → token codec → codec decoder**, chỉ ra mỗi khối nhận gì, trả gì.
2. Đọc được thông số kiểu "12.5 Hz, 16 codebook, 48 kHz" và suy ra số mẫu mỗi frame, số token mỗi giây, ý nghĩa với latency.
3. Phân biệt **audio-output streaming** và **incremental text-input (bi-streaming)**, biết cái nào có thật cho tiếng Việt và hệ quả với thiết kế chunker.
4. Đọc đúng **TTFA, RTF một stream, RTF throughput, lead, số stream đồng thời**; không nhầm các số với nhau.
5. Thiết kế **output contract** (sample rate, kênh, dtype, framing, kết thúc, cancel) và chuyển 48 kHz float32 sang 16 kHz int16 đúng cách.
6. Biết các nút điều khiển (preset voice, cloning, tốc độ, prosody, cue cảm xúc) và giới hạn của chúng.
7. Vận hành: warmup, CUDA graph, idle clock-down, `max_streams`, 429, fallback.
8. Đánh giá chất lượng TTS tiếng Việt đúng cách (MOS/CMOS, round-trip CER là proxy, lỗi thanh điệu) và nhận diện các lỗi thường gặp.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. Text đi qua những bước nào để thành mẫu audio: normalization → G2P → acoustic model → vocoder hoặc codec decoder?
- Q2. Neural codec token ở 12.5 Hz nghĩa là gì? TTFA phụ thuộc vào đâu?
- Q3. Audio-output streaming khác incremental text-input (bi-streaming) thế nào?
- Q4. TTS trả 48 kHz float32, pipeline cần 16 kHz int16. Chuyển đổi ở đâu, và mất gì?
- Q5. Vì sao "RTF 0.011" trong tài liệu VieNeu không có nghĩa một stream chạy nhanh gấp 90 lần realtime?
- Q6. Vì sao round-trip CER (TTS → ASR → so với text gốc) chỉ là proxy?

---

## 13.1 Bức tranh tổng thể

TTS biến một chuỗi ký tự thành một chuỗi mẫu biên độ. Khó khăn cốt lõi: **một-nhiều**. Cùng một câu có vô số cách đọc hợp lệ (nhịp, cao độ, giọng, cảm xúc), nên model phải *chọn hoặc lấy mẫu* một cách đọc, chứ không "tính ra" duy nhất một đáp án như ASR.

```text
Đường cổ điển (modular):
  text ─► normalizer ─► G2P ─► [acoustic model] ─► mel-spectrogram ─► [vocoder] ─► waveform
           (số→chữ)    (chữ→âm vị)  (âm vị→đặc trưng)                 (đặc trưng→mẫu)

Đường LLM/codec (phổ biến ở model streaming hiện nay):
  text ─► normalizer ─► (G2P tuỳ model) ─► [backbone AR] ─► token codec rời rạc ─► [codec decoder] ─► waveform
                          + prompt giọng (reference codes / speaker embedding)

Đường end-to-end một khối (VITS-like), hoặc flow matching / diffusion:
  text/âm vị ─► model sinh trực tiếp mel hoặc waveform (không AR trên token)
```

Ba điều cần nhớ ngay:

- Mọi nhánh đều có **hai nửa**: nửa "ngôn ngữ" (text → biểu diễn trung gian) và nửa "âm thanh" (biểu diễn trung gian → mẫu). Lỗi phát âm thường thuộc nửa đầu; lỗi "rè, kim loại, artifact" thuộc nửa sau.
- Biểu diễn trung gian quyết định **khả năng streaming**: mel dài cả câu thì vocoder chạy được từng đoạn, nhưng model sinh mel non-AR thường cần cả câu; token codec AR sinh tuần tự nên stream tự nhiên (§13.4).
- TTS trong pipeline voice là **dịch vụ có hợp đồng** (§13.7), không phải hàm `text → file`.

---

## 13.2 Text frontend: normalization và G2P

### 13.2.1 Normalization (text → spoken form)

Văn bản của LLM/người dùng chứa thứ **không đọc được trực tiếp**: số, ngày, tiền, đơn vị, viết tắt, URL, markdown. Normalizer chuyển sang dạng "đọc to". Với tiếng Việt, nhiều quyết định phụ thuộc ngữ cảnh:

| Loại | Ví dụ | Điểm khó |
|---|---|---|
| Số | `123` → "một trăm hai mươi ba" | "lẻ/linh", "mươi/mười", "mốt", "tư", "lăm" thay đổi theo vị trí |
| Ngày/giờ | `25/12`, `14:30` | `5/12` là "ngày năm tháng mười hai" hay "năm phần mười hai" tuỳ domain |
| Tiền | `1.250.000đ` | Dấu `.` là phân cách nghìn (vi) chứ không phải thập phân |
| Thập phân | `6,5%` | Dấu `,` là thập phân: "sáu phẩy năm phần trăm" |
| Đơn vị | `km/h`, `m2` | "ki-lô-mét trên giờ", "mét vuông" |
| Số điện thoại, mã | đọc từng chữ số | Phải biết đây là mã chứ không phải số |
| Viết tắt | `TP.HCM`, `UBND` | Đọc từng chữ cái hay đọc như từ |
| Từ nước ngoài | `container`, `database` | Giữ nguyên (nếu model xử lý code-switch) hay phiên âm |

Wiki ghi nhận [VietNormalizer](../wiki/vietnormalizer.md)[^norm]: thư viện Python thuần, pipeline cố định 19 bước (NFC → ký tự đặc biệt/URL → dấu câu → … → số → lowercase → từ điển viết tắt → từ điển từ nước ngoài → phiên âm theo luật), tốc độ báo cáo ~0.6 ms/lần gọi (**Reported**). Thư viện **chưa được wiki kiểm chứng** và thiết kế pipeline chưa chọn normalizer nào (**Reported**, theo [Thiết kế pipeline](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.5). Hai điểm kỹ thuật rút ra (**Synthesis**): thứ tự bước quan trọng (lowercase đứng trước từ điển nên mục từ điển tuỳ biến phải viết chữ thường), và normalizer đầu ra lowercase **mất thông tin viết hoa** mà một số model dùng để nhận tên riêng/viết tắt, nên cần test với đúng model TTS đích.

> **Quy tắc thiết kế (Synthesis):** tách **text hiển thị** (cho UI, log, history LLM) khỏi **text để đọc** (đưa vào TTS). Không bao giờ ghi text đã normalize vào history LLM.

Chi tiết chunker, lexicon, bộ regression prompt thuộc Chương 19 (cầu text → speech). Chương này chỉ cần bạn hiểu **vì sao** TTS cần đầu vào đã được dọn sạch.

### 13.2.2 G2P: grapheme → phoneme

**G2P** (grapheme-to-phoneme) chuyển chữ viết thành chuỗi âm vị. Với tiếng Việt, G2P *tương đối dễ* so với tiếng Anh vì chính tả gần với âm vị, nhưng vẫn có bẫy:

- **Thanh điệu** (6 thanh) là một phần của âm tiết, thay đổi nghĩa. G2P phải giữ thanh, không được bỏ.
- Phương ngữ: `gi/d/r`, `s/x`, `ch/tr`, vần `-n/-ng`, `-t/-c` khác nhau theo Bắc/Trung/Nam. Model có preset giọng vùng thường ngầm chọn một hệ ánh xạ.
- Từ mượn/viết tắt/tên riêng không theo chính tả vi: cần từ điển ngoại lệ.
- **Code-switching** (xen tiếng Anh vào câu vi): G2P phải nhận biết ngôn ngữ từng đoạn. VieNeu v3 Turbo được báo là xử lý bilingual vi/en và dùng phonemizer `sea-g2p` (**Reported**).

Nhiều model hiện đại **không** có bước G2P tách rời: backbone đọc thẳng ký tự/byte/subword và tự học phát âm (ưu điểm: ít thành phần, nhược điểm: khó sửa một từ đọc sai; phải dùng thay thế văn bản hoặc fine-tune). Phân loại này nên đọc từ model card; chương 5 đã giải thích ngữ âm và thanh điệu.

> **Hệ quả vận hành:** lỗi phát âm một từ cụ thể (wiki ghi một báo cáo VieNeu đọc `chánh` thành `tránh`, **Reported/Unverified**) được xử lý bằng **lexicon thay thế** ở tầng text trước TTS, rẻ hơn nhiều so với retrain.

---

## 13.3 Nửa âm học: acoustic model và vocoder (đường cổ điển)

### 13.3.1 Mel-spectrogram làm biểu diễn trung gian

Acoustic model (Tacotron 2, FastSpeech 2…) sinh **mel-spectrogram** (riêng VITS gộp luôn vocoder và sinh thẳng waveform): ma trận `[số frame × số băng mel]` (ví dụ 80 băng, frame 10–12.5 ms). Mel nén thông tin phổ theo thang tai người, bỏ **pha**. Điều này kéo theo việc cần một khối thứ hai để dựng lại pha và waveform.

| Họ acoustic model | Cách sinh | Streaming | Đánh đổi |
|---|---|---|---|
| **AR** (Tacotron-style) | Từng frame mel, dựa vào frame trước + attention | Có thể, nhưng attention dễ lỗi (lặp, bỏ từ) | Tự nhiên, nhưng chậm và có thể mất ổn định |
| **Non-AR** (FastSpeech-style) | Dự đoán độ dài âm vị (duration) rồi sinh mọi frame song song | Khó (cần cả câu), nhưng mỗi câu rất nhanh | Nhanh, ổn định; prosody có thể "phẳng" |
| **Flow-based / VITS** | Mô hình xác suất end-to-end, sinh waveform từ âm vị + biến ẩn | Thường theo câu | Chất lượng tốt, mô hình nhỏ, khó điều khiển chi tiết |
| **Diffusion / flow matching** | Lặp nhiều bước khử nhiễu từ nhiễu → mel hoặc latent | Theo khối; số bước quyết định tốc độ | Chất lượng cao; chi phí tỉ lệ số bước |

### 13.3.2 Vocoder: mel → waveform

Vocoder là mạng sinh waveform có điều kiện trên mel. Các thế hệ: WaveNet (rất chậm) → WaveRNN → **GAN vocoder** (HiFi-GAN, BigVGAN: nhanh, song song, chạy GPU/CPU tốt) → vocoder dựa phổ (Vocos: sinh phổ biên độ/pha rồi iSTFT).

- Vocoder GAN dùng transposed conv **không nhân quả hoàn toàn**; để streaming, người ta cắt mel thành đoạn có chồng lấp (overlap) rồi cross-fade, nếu không sẽ có "click" ở ranh giới.
- Vocoder quyết định **sample rate đầu ra** (22.05/24/44.1/48 kHz). Mel chỉ định băng tần tối đa; nâng sample rate không tự thêm chi tiết.

---

## 13.4 TTS dựa trên LLM và neural codec

### 13.4.1 Neural audio codec và token rời rạc

**Neural codec** là bộ nén âm thanh học được gồm: *encoder* (waveform → vector theo frame), *quantizer* (vector → số nguyên rời rạc), *decoder* (số nguyên → waveform). Quantizer thường là **RVQ** (residual vector quantization): một frame được mã hoá bằng `K` token (K codebook); codebook 1 nắm cấu trúc thô, các codebook sau mã hoá *phần dư* để tinh chỉnh chi tiết.

Khi đã có token rời rạc, bài toán TTS thành **mô hình ngôn ngữ**: một backbone Transformer (AR) nhận text (+ prompt giọng) và sinh chuỗi token codec, rồi **codec decoder** dựng waveform.

```text
Mỗi frame codec:  [t1 t2 … t16]        ← 16 codebook (RVQ)
Tốc độ frame:      12.5 Hz  →  80 ms / frame
```

Sinh `K` token cho mỗi frame thường theo **hai tầng AR**: backbone lớn bước một lần mỗi frame, rồi một decoder nhỏ sinh lần lượt các codebook trong frame (ví dụ Fish S2: Slow AR dự đoán codebook semantic, Fast AR dự đoán các codebook dư; VieNeu: acoustic decoder 16 codebook chạy sau mỗi bước backbone) (**Reported**).[^selection][^runtime] Vì vậy "200 token/s" không có nghĩa là 200 bước backbone/s.

Ví dụ trong wiki (đều **Reported** trừ khi ghi khác):

- **Qwen3-TTS-Tokenizer-12Hz:**[^qwen] 12.5 Hz, 16 codebook, decoder ConvNet nhân quả nhẹ, mục tiêu phát gói đầu tức thì. Con số 97 ms end-to-end trong card thuộc **hệ thống** Qwen3-TTS (Dual-Track), không phải đo riêng tokenizer (**Synthesis**). Quan trọng cho tiếng Việt: card Qwen3-TTS chính thức liệt kê 10 ngôn ngữ **không có vi**, nên không dùng out-of-box (**Reported**, [Thiết kế pipeline](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.6).
- **VieNeu-TTS v3 Turbo:**[^vieneu] codec `MOSS-Audio-Tokenizer-Nano`, acoustic decoder 16 codebook, 12.5 frame/s, 80 ms/frame, 48 kHz đầu ra (**Reported**).
- **MOSS-Audio-Tokenizer-Nano** (codec của VieNeu, theo README MOSS-TTS-Nano): ~20M tham số, 48 kHz **stereo**, 12.5 Hz, RVQ 16 codebook, bitrate thay đổi 0.125–2 kbps bằng số codebook dùng lúc suy luận (**Reported**).[^moss]

### 13.4.2 Số học frame: đọc thông số codec

Từ "12.5 Hz" và "48 kHz":

- 1 frame = `1000 / 12.5 = 80 ms`.
- Số mẫu mỗi frame = `48000 / 12.5 = 3840` mẫu (tại 24 kHz: 1920; tại 16 kHz: 1280).
- Số token/s = `12.5 × 16 = 200` token/s. Backbone phải sinh *một frame* (16 token, thường qua một acoustic decoder nhỏ) trong **ít hơn 80 ms** để không tụt sau thời gian thực.
- Bitrate rất thấp. MOSS-Audio-Tokenizer-Nano báo tối đa 2 kbps với 16 codebook (**Reported**); `2000 / 200 = 10 bit/token`, tức mỗi codebook ~1024 mục (**Synthesis**, suy từ số học, card không ghi kích thước codebook). So sánh: PCM 16 kHz int16 mono = 256 kbps, 48 kHz int16 mono = 768 kbps, tức codec nhỏ hơn hàng trăm lần. Nén mạnh như vậy buộc decoder "bịa" lại chi tiết, nên chất lượng phụ thuộc rất nhiều vào decoder (§13.8).

**Hệ quả với latency (Synthesis):** granularity là 80 ms. Chunk audio đầu tiên nhỏ nhất bằng 1 frame (80 ms âm thanh); TTFA thực = `prefill + thời gian sinh k frame đầu + giải mã codec`. VieNeu GPU dùng chunk đầu 2 frame (160 ms audio), CPU 4 frame (320 ms), các chunk sau 4 frame (**Reported**).

### 13.4.3 Tại sao codec nhân quả quan trọng

Decoder streaming được **chỉ khi không nhìn trước (no lookahead)**. Nếu decoder cần frame tương lai để dựng frame hiện tại, bạn phải chờ. Wiki ghi decoder codec của VieNeu không có lookahead và audio streamed khớp bản decode toàn bộ tới sai lệch 6e-4 (**Reported**); decoder Qwen là ConvNet nhân quả (**Reported**). Ngược lại, chế độ `use_cuda_graph` có sẵn của codec rẻ hơn 3 lần nhưng cho audio sai (tương quan 0.2), nên VieNeu không dùng (**Reported**): bài học là *tối ưu tốc độ không được kiểm tra tương đương số học thì có thể phá chất lượng*.

---

## 13.5 Các họ sinh: AR, non-AR, flow matching, diffusion

Ví dụ lấy từ catalog và bảng shortlist của wiki.[^survey][^selection][^vieneu]

| Họ | Ví dụ trong wiki (Reported) | Cơ chế sinh | Streaming | Rủi ro điển hình |
|---|---|---|---|---|
| **AR trên token codec** | VieNeu v3 Turbo, Higgs TTS 3, Fish S2 Pro (Slow AR + Fast AR), Qwen3-TTS | Từng frame/token | **Tự nhiên, frame-level** | Lặp/bỏ từ, drift giọng, ổn định phụ thuộc sampling |
| **AR trên latent liên tục + diffusion cục bộ** | VoxCPM2 (2B, 48 kHz, `generate_streaming`) | Tokenizer-free: `LocEnc → TSLM → RALM → LocDiT`, LM 6.25 Hz, AudioVAE ra 48 kHz | Có (API streaming) | Cần GPU (~8 GB VRAM theo card); RTF ~0.3 (~0.13 với Nano-vLLM) trên 4090; chưa có TTFA |
| **Flow matching / diffusion LM** | VieNeu v3 Nano (flow matching, 48M, ONNX, **24 kHz**), OmniVoice (diffusion LM) | Lặp `steps` bước (Nano: 16 mặc định, 8 nhanh ~2× nhưng thô hơn) | **Thường chỉ trả cả câu/chunk xong**; RTF rất thấp (OmniVoice 0.025) | Chất lượng theo `steps`; không frame streaming |
| **Non-AR nhỏ, CPU-first** | Supertonic 3 (~99M ONNX) | Một lượt | `synthesize` trả cả waveform | Latency tuỳ độ dài câu |

**Ba nguyên tắc chọn họ (Synthesis):**

1. **RTF thấp ≠ TTFA thấp.** Với model chỉ trả cả chunk, `TTFA ≈ overhead cố định + RTF × độ dài chunk`: RTF 0.025 với mệnh đề 2 s chỉ tốn ~50 ms tính toán, nhưng với câu 15 s là ~375 ms, và con số RTF công bố thường đo ở GPU mạnh, batch, trạng thái nóng. AR frame-level RTF 0.5 có TTFA gần như không phụ thuộc độ dài câu. Voice agent quan tâm **TTFA (P95) và lead**, không chỉ RTF; một model non-streaming RTF rất thấp + chunker mệnh đề ngắn vẫn có thể đạt TTFA tốt, nhưng phải đo chứ không suy từ RTF (**Synthesis**).[^selection]
2. **Streaming thật phụ thuộc cả decoder, không chỉ backbone.** AR backbone + decoder cần cả câu ⇒ vẫn không stream.
3. **Non-streaming chạy được qua "chunker + một request mỗi mệnh đề"**, đổi lấy việc prosody không liền mạch giữa các mệnh đề (xem §13.6.2 và Chương 19).

---

## 13.6 Điều khiển: giọng, cloning, tốc độ, prosody

### 13.6.1 Các cách chọn giọng

| Cơ chế | Cách hoạt động | Chi phí/giới hạn |
|---|---|---|
| **Preset voice** | Giọng đã đăng ký sẵn (speaker embedding + reference codes) | Ổn định nhất, không cần audio mẫu. VieNeu v3 Turbo: 25 preset Bắc/Trung/Nam (card SDK 3.7.1 ghi 23, nên ghim version) (**Reported**) |
| **Zero-shot voice cloning** | Đưa reference audio (+ transcript), model bắt chước giọng | VieNeu: clip 3–8 s, tự denoise/trim tối đa 8 s; chất lượng clip quyết định kết quả (**Reported**) |
| **Speaker embedding** | Vector đặc trưng người nói điều kiện hoá model | Dùng chung ý tưởng với Chương 14 |
| **Fine-tune (LoRA)** | Học một giọng từ 10–30 phút audio sạch | VieNeu: ~6 GB GPU, merged model đóng gói speaker embedding (**Reported**) |

Lưu ý cloning: **reference audio + transcript** phải *khớp nhau*; transcript sai làm model học sai căn chỉnh (**Synthesis**). Reference ồn/echo/nhạc nền làm giọng sinh ra bị nhiễm. Về pháp lý/đạo đức, cloning giọng người thật cần đồng ý rõ ràng (Chương 23).

### 13.6.2 Prosody, tốc độ, pause, cảm xúc

Prosody gồm cao độ (F0), độ dài âm, nhịp, nhấn, ngắt nghỉ. Với model AR/codec, prosody được quyết định bởi **context**: phần text đã thấy, dấu câu, và *giọng tham chiếu*. Hệ quả thực tế:

- **Dấu câu là công cụ điều khiển prosody chính** (`,` nghỉ ngắn, `.` kết câu, `?` lên giọng, `…` kéo dài). Normalizer không được xoá dấu câu.
- **Chunk quá ngắn** làm model thiếu context nên giọng cụt, ngữ điệu "đọc từng mẩu"; **chunk quá dài** làm TTFA tăng. Wiki khuyến nghị đơn vị khoảng một câu hoặc 20–60 ký tự; chunk đầu có thể cắt ở dấu phẩy khi đã có ≥ ~25 ký tự, gộp mảnh < 8 ký tự vào câu sau (**Reported**, [Thiết kế pipeline](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.5; Chương 12 §12.3.2).[^design]
- **Tốc độ:** nhiều API nhận `speed` nhưng không phải model nào thực thi. Server VieNeu `speed` và `instructions` được nhận để tương thích nhưng **bị bỏ qua** (có header `X-VieNeu-Ignored`) (**Reported**). Đừng giả định tham số có hiệu lực: kiểm bằng nghe và đo độ dài audio.
- **Cue cảm xúc inline** của VieNeu (`[cuoi]`, `[tho dai]`, `[hang giong]`) là **experimental** (**Reported**); trường `style` đã deprecated, phong cách theo giọng tham chiếu (**Reported**). Kiểm trước khi dùng cho sản phẩm.
- **Nhiệt độ lấy mẫu:** card VieNeu khuyên ~0.8 cho ổn định; cao hơn tăng biểu cảm nhưng kém ổn định (**Reported**). Mặc định server: temperature 0.8, top_k 25, top_p 0.95, repetition_penalty 1.2 (**Reported**).

> **Voice agent nên ưu tiên ổn định hơn biểu cảm (Synthesis).** Temperature thấp, preset voice cố định, nhất quán giữa các lượt; biểu cảm cao chỉ khi sản phẩm yêu cầu.

---

## 13.7 Output contract của dịch vụ TTS

Pipeline nên coi TTS như một service với hợp đồng rõ ràng. Mẫu hợp đồng (**Synthesis**, phần field cụ thể lấy từ [VieNeu OpenAI-compatible API](../wiki/vieneu-tts-openai-speech-api.md), **Reported**):[^api]

| Mục | Điều phải xác định | Ví dụ VieNeu (Reported) |
|---|---|---|
| Sample rate | Gốc của model và các rate hỗ trợ | Gốc 48 kHz; hỗ trợ 24 k, 16 k, 8 k (resample từng chunk bằng soxr) |
| Kênh | Mono hay stereo | HTTP `pcm` là s16le **mono**. Lưu ý: codec MOSS-Audio-Tokenizer-Nano được mô tả là 48 kHz stereo, nên cần xác nhận số kênh thật của mảng SDK (`ndim`/shape) trước khi giả định mono |
| dtype | float32 hay int16 | SDK `infer_stream` trả `np.float32` 48 kHz; HTTP `pcm` là s16le |
| Container | PCM thô hay WAV | `pcm` không header; `wav` header với độ dài "unknown" để player phát ngay (một số thư viện đọc WAV không chấp nhận độ dài này, **Synthesis**); `mp3/opus/aac/flac` → 400, cần tự encode (~20–40 ms) |
| Framing | Chunked raw hay SSE | `stream_format=audio` (chunked) hoặc `sse` (base64 PCM trong `speech.audio.delta`) |
| Kết thúc | Tín hiệu hết stream | Chunked: đóng body; SSE: `speech.audio.done` kèm `usage` (samples, rate, seconds) |
| Cancel | Huỷ giữa chừng | Client đóng kết nối; server phải **giải phóng slot** (cần kiểm trong test) |
| Định danh | Correlate request | `X-Request-Id`, `X-Sample-Rate` |
| Lỗi/backpressure | Quá tải | `429` + `Retry-After` khi hết slot/hàng đợi |

### 13.7.1 Kích thước chunk và framing

- Audio-output streaming trả **chuỗi chunk PCM**. Kích thước chunk theo đơn vị frame codec: với 4 frame = 320 ms (VieNeu), chunk 48 kHz mono int16 = `0.32 × 48000 × 2 = 30,720 byte`; float32 gấp đôi.
- Chunk cuối thường ngắn hơn; không giả định chunk đều nhau.
- SSE base64 tăng kích thước ~33% và cần decode; thích hợp qua proxy/browser, còn chunked raw hiệu quả hơn cho service-to-service.

### 13.7.2 Đưa vào audio contract của pipeline

Pipeline có **audio contract nội bộ** (Chương 16): ví dụ 16 kHz mono int16 cho đường ASR, còn playback có thể 24/48 kHz. TTS output **không nhất thiết** phải 16 kHz; thường playback *không* cần hạ xuống 16 kHz trừ khi:

- gửi qua telephony (8/16 kHz) hoặc codec Opus có băng thông thấp,
- cần đưa chính audio TTS làm **tham chiếu AEC** ở 16 kHz (Chương 7),
- ghi log/QA cùng định dạng với đường vào.

Điểm quan trọng nhất: **ghi rõ rate/dtype ở *mỗi* ranh giới** và chỉ chuyển đổi **một lần** ở một nơi. Mỗi lần resample thêm độ trễ, sai số và nguy cơ aliasing/clip (§13.9).

---

## 13.8 Hai nghĩa của "streaming TTS" và các chỉ số

### 13.8.1 Audio-output streaming vs bi-streaming

| | **Audio-output streaming** | **Incremental text-input (bi-streaming)** |
|---|---|---|
| Đầu vào | Text **đầy đủ** của một đơn vị (câu/mệnh đề) | Text đến **dần dần** (token LLM) trong lúc đang nói |
| Đầu ra | Audio theo chunk | Audio theo chunk |
| Ví dụ | VieNeu `infer_stream`, VoxCPM2 `generate_streaming` | CosyVoice bi-streaming, Qwen Dual-Track |
| Bằng chứng cho tiếng Việt | **Có** (VieNeu, VoxCPM2) | **Chưa có** ứng viên vi nào (**Reported**, [Thiết kế pipeline](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.5)[^design][^selection] |

Hệ quả: để nối LLM streaming → TTS không bi-streaming, ta cần **clause chunker**: đủ ngắn để TTFA nhỏ, đủ dài để prosody tốt. Đây là "cầu text → speech" (Chương 19), **không phải** native bi-streaming; đừng gọi sai tên khi viết tài liệu thiết kế.

```text
LLM tokens ─► chunker (mệnh đề) ─► TTS.infer_stream(mệnh đề 1) ─► chunk PCM… ─► playback
                                 └► TTS.infer_stream(mệnh đề 2) (xếp hàng, nối liền)
```

Giữa các mệnh đề có thể nghe **khe hở** hoặc **đổi ngữ điệu** vì mỗi lần gọi là một context mới. Giảm bằng: giữ cùng giọng/seed/temperature, đọc trước mệnh đề kế khi mệnh đề hiện tại còn đang phát, và đủ buffer phía client.

### 13.8.2 Các chỉ số và cách đọc

- **TTFA (time to first audio):** từ lúc gửi request tới **byte audio thật đầu tiên**. Với `wav`, header đến sau ~2 ms nhưng không tính (**Reported**). Gồm: mạng + chờ slot/queue + prefill + frame đầu + giải mã codec + (resample) + đóng gói.
- **RTF một stream:** `thời gian sinh / thời lượng audio`. `< 1` mới không tụt; `0.5` nghĩa là còn dư một nửa thời gian.
- **RTF throughput (bulk):** tổng thời gian xử lý / tổng audio sinh ra khi **batch** nhiều request. Con số này có thể rất nhỏ (VieNeu ghi bulk RTF 0.011–0.02, ví dụ 30 câu / 130 s audio trong 1.5–2.3 s, **Reported**)[^vieneu] nhưng **không phải** tốc độ một stream. Dùng nó để ước tính chi phí batch offline, không để dự đoán độ trễ hội thoại. Cùng VieNeu trên GPU có **ba** con số RTF khác nhau (**Reported**): bulk 0.011–0.02; một câu không streaming 0.10 (launch-bound); streaming một stream 0.49 trên RTX 3060 (theo nhịp frame + lần gọi codec chung). Luôn hỏi RTF đo ở chế độ nào.
- **Lead:** `audio đã nhận − thời gian đã trôi kể từ chunk đầu`. Lead âm = có khe im lặng (underrun). VieNeu GPU đo lead tối thiểu +80 ms (≤ 16 stream) và CPU +320 ms; khuyến nghị **pre-buffer 150–300 ms** ở client để hấp thụ jitter (**Reported**).
- **Số stream đồng thời:** `max_streams`. 16 stream TTS không có nghĩa 16 pipeline; một stream chỉ sống trong lúc bot đang nói, nên 16 stream ước phục vụ khoảng 45–80 user đang chat (tác giả ước, **Reported**).

Số đo VieNeu trên RTX 3060, `infer_stream` in-process, N request bắt đầu cùng lúc (**Reported**, nguồn: [Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md)):[^runtime]

| `max_streams` | N=1 TTFA / RTF | N=16 TTFA median / RTF | N=32 TTFA / RTF |
|---|---|---|---|
| 16 (mặc định) | ~115 ms / 0.49 | 185 ms / 0.59 | — |
| 32 | 141 ms / 0.70 | 220 ms / 0.82 | ~456 ms / 0.93 (lead âm) |

Hai điểm cấu trúc: (1) chi phí chung của codec ≈ `65 ms + 2.5 ms × số slot đã đặt trước`, gần như **toàn bộ chi phí GPU** và không phụ thuộc số stream đang chạy, nên **mỗi slot dư làm chậm mọi request**; chọn `max_streams` đúng tải thật. (2) CPU fp32 trên 6 nhân chỉ chạy đúng 1 stream (RTF 0.55–0.61; hai request cùng lúc RTF 1.19, tức tụt); int8 (cần CPU có VNNI, thiếu VNNI thì model nói lảm nhảm) cho 1 stream RTF 0.35 và 2 stream đồng thời RTF 0.58–0.67, vẫn realtime (**Reported**). Lưu ý: "N cùng lúc" là trường hợp xấu (prefill dồn đống); request đến rải rác giữa 15 stream đang chạy có TTFA ~134 ms ở `max_streams=16` (**Reported**).

### 13.8.3 Mô phỏng: RTF, chunk đầu, pre-buffer và underrun

Script ở phụ lục mô phỏng một stream 125 frame (10 s) với prefill 21 ms, chunk đầu 2 frame, các chunk sau 4 frame (**Reproduced**, mô phỏng thuần):

| RTF | Pre-buffer | TTFA (ms) | Underrun | Tổng gap (ms) | Buffer nhỏ nhất khi chunk tới (ms) |
|---|---|---|---|---|---|
| 0.5 | 0 | 101 | 0 | 0 | 0 |
| 0.5 | 200 | 101 | 0 | 0 | 200 |
| 0.9 | 0 | 165 | 1 | 128 | 0 |
| 0.9 | 200 | 165 | 0 | 0 | 72 |
| 1.2 | 0 | 213 | 30 | 2080 | 0 |
| 1.2 | 200 | 213 | 30 | 1880 | 0 |

Đọc kết quả (**Synthesis**): (a) RTF 0.5 thì không bao giờ tụt, pre-buffer chỉ làm tăng "mức đệm an toàn" nhưng *tăng độ trễ nghe được đúng bằng pre-buffer*; (b) RTF 0.9 là vùng nguy hiểm: không có pre-buffer thì gặp underrun, 200 ms pre-buffer che được nhưng chỉ còn đệm 72 ms; (c) RTF > 1 thì **không pre-buffer nào cứu được**, vì sinh chậm hơn phát. Kết luận: pre-buffer là **van an toàn cho jitter**, không phải thay cho việc giữ RTF thấp. Đây là mô hình lý tưởng (không có jitter mạng, tốc độ sinh hằng số).

---

## 13.9 Chuyển định dạng: 48 kHz float32 → 16 kHz int16

Đây là nơi chất lượng bị âm thầm làm hỏng nhiều nhất. Có ba phép biến đổi độc lập:

1. **Đổi sample rate (resample):** 48 kHz → 16 kHz, tỷ lệ 3:1.
2. **Đổi dtype:** float32 `[-1, 1]` → int16 `[-32768, 32767]`.
3. **Đổi kênh** (nếu stereo → mono).

### 13.9.1 Resample: vì sao không được "lấy mỗi mẫu thứ 3"

16 kHz có Nyquist 8 kHz. Mọi thành phần phổ trên 8 kHz phải bị **lọc bỏ trước khi** hạ tần số, nếu không chúng **gập (alias)** vào dải dưới. Thí nghiệm (**Reproduced**, script phụ lục): tín hiệu sin 10 kHz tại 48 kHz.

| Thành phần | Decimate thô (`x[::3]`) | Low-pass (sinc cửa sổ Hann) rồi decimate |
|---|---|---|
| Tone 1 kHz (trong băng) | 1.000 | 1.002 |
| Tone 7 kHz (trong băng, sát tần cắt) | 1.000 | 0.500 |
| Tone 10 kHz (ngoài băng) tại 6 kHz | **1.000** (alias đầy đủ) | **0.000** (bị loại) |

Tone 10 kHz vô hại ở 48 kHz nhưng nếu decimate thô nó biến thành một tone 6 kHz **cường độ đầy đủ** trong tín hiệu 16 kHz. Với giọng nói thật, phần "xì" của âm xát (s, x) có năng lượng trên 8 kHz và sẽ gập thành nhiễu tạp trong dải ASR. Tone 7 kHz có biên độ 0.5 trong ví dụ vì tần cắt đặt đúng 7 kHz (điểm −6 dB): minh hoạ rằng bộ lọc thực tế có **dải chuyển tiếp** và bạn mất một ít phần cao sát Nyquist.

> **Quy tắc (Synthesis):** dùng resampler chất lượng (soxr, `torchaudio`, `scipy.signal.resample_poly`, libsamplerate) có lọc anti-alias, và **không tự viết** decimate. Server VieNeu resample từng chunk bằng soxr và nêu "không thêm latency" (**Reported**). Nếu tự resample theo chunk, resampler phải **giữ trạng thái** giữa các chunk (stateful) để không tạo click ở ranh giới.

**Mất gì khi hạ xuống 16 kHz:** toàn bộ thông tin trên 8 kHz (độ "sáng", không khí của âm xát/âm bật). Với **ASR** thì đủ (ASR thường học ở 16 kHz); với **playback cho người nghe** thì nghe "bí" hơn so với 24/48 kHz. Vì vậy: đường **ASR/AEC reference** dùng 16 kHz, đường **playback** giữ rate cao nhất mà thiết bị và mạng cho phép.

### 13.9.2 float32 → int16: scale, clip, dither

- Công thức: `int16 = round(clip(x, -1, 1) × 32767)`. Một số thư viện dùng `× 32768` rồi clip về 32767; chênh lệch không nghe thấy, quan trọng là **một quy ước** cho cả pipeline.
- **Clip:** nếu mẫu float vượt `[-1, 1]` (TTS đôi khi overshoot), phải clip hoặc giảm gain; nếu để tràn số nguyên sẽ **wrap-around** và phát ra tiếng nổ lớn. Mô phỏng: sin biên độ đỉnh 1.3 làm 2200/4800 mẫu vượt ngưỡng; nếu ép kiểu không clip, các mẫu này wrap sang dấu ngược (đỉnh dương thành ≈ −31741) (**Reproduced**). Hãy **kiểm peak** và dùng limiter nhẹ thay vì để clip cứng.
- **Lượng tử hoá:** lỗi RMS ≈ 0.29 LSB (lý thuyết `1/√12`), SNR ≈ 98 dB với sin toàn thang (lý thuyết `6.02 × 16 + 1.76`) (**Reproduced**). Với giọng nói bình thường đây không nghe thấy. **Dither** chỉ cần khi tín hiệu rất nhỏ hoặc bit-depth thấp hơn nữa.
- Ngược lại int16 → float32: chia 32768; làm **một lần**, đừng cộng dồn nhiều phép scale.
- **Endianness và interleave:** `s16le` là little-endian; stereo interleave (L R L R). Sai một trong hai gây tiếng rít/nhiễu toàn phần (hay gặp khi đọc PCM thô bằng `np.frombuffer`).

### 13.9.3 Điều cần ghi lại ở contract

Mỗi interface ghi rõ `(sample_rate, channels, dtype, endianness, frame_ms)`. Thêm kiểm tra tự động: khi nhận chunk, assert độ dài byte chia hết cho `channels × bytes_per_sample`, kiểm peak, kiểm duration tổng ≈ `ký tự × hệ số` để bắt trường hợp rate sai (audio nhanh/chậm gấp đôi: lỗi đặc trưng khi tưởng 24 kHz nhưng thực tế 48 kHz).

---

## 13.10 Chất lượng giọng nhất quán giữa các chunk

Vì mệnh đề được tổng hợp bằng nhiều request, nhiều lỗi chỉ xuất hiện *giữa* chunk:

- **Drift giọng:** timbre hơi khác từng lần do sampling ngẫu nhiên. Giảm bằng temperature thấp, cùng preset/reference, và (nếu hỗ trợ) cố định `seed`.
- **Ranh giới:** click do cắt không đúng zero-crossing hoặc resampler mất trạng thái; khe hở do TTS thêm silence đầu/cuối. Nên **trim silence thừa** ở đầu/cuối mỗi chunk và cross-fade vài ms nếu cần.
- **Loudness khác nhau:** chuẩn hoá cùng mức (ví dụ giới hạn peak, không chuẩn hoá từng chunk theo RMS vì đổi độ to giữa câu).
- **Ngữ điệu đứt:** như §13.6.2. Giữ mệnh đề đủ dài, dùng dấu câu hợp lý.

Test đơn giản: đọc cùng một đoạn dài theo ba cách (một request / chunk theo câu / chunk theo mệnh đề ngắn), nghe so sánh và đo số khe hở.

---

## 13.11 Vận hành: warmup, CUDA graph, idle clock-down, giới hạn stream

Các hiện tượng dưới đây là **Reported** từ [Streaming Runtime](../wiki/vieneu-tts-streaming-runtime.md); nguyên lý chung là kiến thức nền.

| Vấn đề | Cơ chế | Cách xử lý |
|---|---|---|
| **Cold start** | Nạp weights, tạo session ONNX, capture CUDA graph (~0.5 s mỗi batch size) | Warmup lúc khởi động bằng một câu ngắn (server VieNeu tự warm; SDK có `warm_fused()`) |
| **CUDA graph** | Ghi lại chuỗi kernel một lần rồi replay: giảm overhead launch, hợp với model nhỏ bị launch-bound | Cần shape tĩnh (vì thế KV cache dạng ring buffer, batch cố định B slot) |
| **Idle clock-down** | GPU rảnh ~2 s thì driver hạ xung (RTX 3060: P8, 210 MHz); request tiếp theo +100–300 ms (đo: 118 ms ấm vs **403 ms** sau 8 s idle) | Khoá clock bằng `nvidia-smi -lgc`, hoặc chế độ "Prefer maximum performance"; **không** giữ ấm trong process (matmul định kỳ không đủ) |
| **Slot dư** | Chi phí codec tăng theo số slot đặt trước | `max_streams` = tải đồng thời thật |
| **Hết slot** | Hàng đợi đầy hoặc quá hạn | HTTP `429` + `Retry-After`; thiết kế client retry/fallback |
| **Một worker sở hữu GPU** | Một scheduler thread, nhiều queue | Scale bằng nhiều container, mỗi cái một GPU; không fork |
| **Watermark** | Perth watermark theo chunk (`VIENEU_WATERMARK=1` mặc định) | Biết là có; số đo in-process của nguồn tắt watermark, số đo HTTP bật, nên so sánh cùng cấu hình[^api] |
| **Warmup chưa xong** | Request đầu sau khởi động mất 1–2 s | Chờ `/health` trả `ok` rồi mới đưa traffic vào[^runtime] |

**Bài học tổng quát (Synthesis):** đo TTFA ở **ba trạng thái**: (1) nóng, (2) sau idle, (3) dưới tải đồng thời, và báo cáo P50/P95/max. Một con số TTFA trung bình lấy lúc nóng sẽ đánh giá quá lạc quan.

**Fallback.** Tài liệu thiết kế §9.4 chỉ chốt một nguyên tắc: **không đổi backend TTS giữa một câu** vì giọng sẽ đổi; retry, hoặc chuyển sang mệnh đề mới kèm thông báo trạng thái (**Synthesis**).[^design] Một thang suy giảm khả dĩ (**Synthesis** của chương này): retry theo `Retry-After` → backend CPU (Turbo int8; Nano chỉ khi chấp nhận chất lượng thấp hơn và không frame-streaming) cho thông báo ngắn → trả lời bằng văn bản. Chú ý Nano xuất **24 kHz** chứ không phải 48 kHz, nên adapter phải đọc rate từ backend thay vì hard-code (§13.7). Mỗi nấc có chất lượng và latency khác nhau; test nó như một tính năng, không phải ngoại lệ.

---

## 13.12 Chất lượng và đánh giá

### 13.12.1 Các lớp đánh giá

| Lớp | Câu hỏi | Công cụ |
|---|---|---|
| **Khả năng hiểu** | Nghe có đúng chữ không? | Round-trip CER/WER (proxy), nghe thử |
| **Tự nhiên** | Giống người không? | **MOS** (điểm tuyệt đối 1–5), **CMOS** (so sánh cặp) |
| **Giống giọng** | Có đúng người nói không? | Speaker similarity (cosine embedding, nghe thử) |
| **Phát âm/thanh điệu** | Có đọc sai từ, sai thanh? | Bộ câu thử có chủ đích, người bản ngữ |
| **Nhất quán** | Giọng/loudness ổn qua chunk | Nghe, đo lead/gap |
| **Vận hành** | TTFA, RTF, concurrency, lỗi 429 | Đo trên phần cứng đích |

### 13.12.2 Round-trip CER chỉ là proxy

Pipeline đo: text → TTS → ASR → so với text gốc. Nó **chỉ đo "ASR hiểu được"**, và có ba điểm mù (**Synthesis**):

- ASR tốt có thể "sửa lỗi" cho TTS (đoán từ đúng dù phát âm sai nhẹ), nên CER thấp không bảo đảm người nghe thấy tự nhiên.
- Sai **thanh điệu** nhẹ có thể không đổi chữ ASR nhận ra nhờ ngữ cảnh, nhưng người nghe bản ngữ thấy rõ.
- Không đo prosody, độ tự nhiên, giọng, artifact.

Dùng round-trip CER để **bắt lỗi thô và regression** (câu bị bỏ từ, đọc sai số), không để xếp hạng model. Wiki nhấn mạnh: chưa có MOS/CMOS tiếng Việt cùng điều kiện giữa các ứng viên; thứ tự ứng viên là "độ phù hợp triển khai", **không phải xếp hạng chất lượng nghe** (**Reported/Synthesis**).

### 13.12.3 Lỗi đặc thù tiếng Việt cần luôn có trong bộ test

- **Thanh điệu:** cặp tối thiểu (ma/má/mà/mả/mã/mạ), từ nhiều dấu, câu hỏi/khẳng định.
- **Số và định dạng:** số lớn, thập phân, ngày giờ, tiền, số điện thoại (xem §13.2.1).
- **Địa danh, tên riêng, viết tắt:** `TP.HCM`, tên người/thương hiệu.
- **Từ dễ đọc nhầm:** như báo cáo `chánh → tránh` (**Reported/Unverified**).
- **Code-switch:** câu pha tiếng Anh, tên sản phẩm.
- **Câu rất ngắn** ("Dạ.", "Vâng ạ."): dễ cụt/clip.
- **Câu dài:** drift và lặp.
- **Tính nhất quán qua nhiều lượt:** cùng giọng giữa lượt đầu và lượt cuối.

---

## 13.13 Chọn model: ma trận quyết định (tóm tắt)

Chi tiết ở [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md)[^selection] và [Lựa chọn và thiết kế TTS realtime cho tiếng Việt](lua-chon-va-thiet-ke-tts-tieng-viet-realtime.md). Đây là **Synthesis** theo độ phù hợp triển khai, không phải xếp hạng nghe:

| Nhu cầu | Ứng viên đầu tiên | Lưu ý |
|---|---|---|
| Baseline realtime vi, frame streaming, CPU/GPU | VieNeu v3 Turbo | License có mâu thuẫn FAQ (Apache) và roadmap ("personal use"): rà trước thương mại |
| Chất lượng/cloning, có GPU | VoxCPM2 (2B, Apache-2.0) | Chưa có TTFA hay MOS vi |
| CPU/edge | Supertonic 3 (OpenRAIL-M weights), VieNeu v3 Nano | Không frame-level streaming; Nano 24 kHz, yếu hơn ở English/code-switch |
| Expressive, chấp nhận mua license thương mại riêng | Higgs TTS 3, Fish S2 Pro | Weights research/non-commercial; sản phẩm cần thỏa thuận thương mại; vi chưa được chứng minh tốt hơn VieNeu/VoxCPM2 |
| Cloning/accuracy, cần nghe thử | G-OmniVoice, Gwen-TTS | Full waveform, chưa streaming; rà lineage license |
| **Không dùng out-of-box cho vi** | Qwen3-TTS chính thức | 10 ngôn ngữ, không có vi |

---

## 13.14 Lỗi thường gặp (checklist)

| Triệu chứng | Nguyên nhân thường gặp | Mục liên quan |
|---|---|---|
| Giọng nhanh/chậm gấp đôi, "chipmunk" | Gắn nhãn sample rate sai (24 k vs 48 k) | §13.7, §13.9.3 |
| Tiếng nổ lớn, méo | Float vượt `[-1,1]` rồi wrap/clip khi ép int16 | §13.9.2 |
| Tiếng rít, nhiễu toàn phần | Sai endianness hoặc interleave/số kênh | §13.9.2 |
| Âm "xì" thành nhiễu lạ trong ASR | Decimate không lọc anti-alias | §13.9.1 |
| Click ở ranh giới chunk | Resampler không giữ trạng thái; không cross-fade | §13.9.1, §13.10 |
| Khe im lặng giữa mệnh đề | Underrun: RTF gần 1, chunk đầu nhỏ, thiếu pre-buffer | §13.8.3 |
| Request đầu sau idle chậm 100–300 ms | GPU hạ xung | §13.11 |
| TTFA tốt khi test nhưng xấu lúc chạy thật | Chỉ đo ở trạng thái nóng, một stream | §13.8.2, §13.11 |
| Càng nhiều slot, mọi request càng chậm | Chi phí codec tăng theo `max_streams` | §13.8.2 |
| `429` giờ cao điểm | Hết slot/hàng đợi | §13.11 |
| Đọc "một hai ba bốn" thay vì số tiền | Chưa normalize | §13.2.1 |
| Đọc dấu `*`, URL, emoji | Markdown/URL lọt vào TTS | §13.2.1, Ch.12, Ch.19 |
| Từ cụ thể đọc sai thanh/vần | Lỗi G2P hoặc model; cần lexicon | §13.2.2 |
| Giọng đổi nhẹ giữa các câu | Temperature cao, không cố định giọng/seed | §13.6, §13.10 |
| Ngữ điệu cụt, từng mẩu | Chunk quá ngắn, thiếu context | §13.6.2 |
| Bot tiếp tục nói sau khi bị ngắt | Không huỷ stream TTS hoặc chunk cũ còn hàng đợi | §13.7, Ch.17 |
| Echo tự kích bot | Playback không đưa vào AEC reference đúng rate | §13.7.2, Ch.7 |
| `speed`/`instructions` không có tác dụng | Tham số được nhận nhưng bị bỏ qua | §13.6.2 |

---

## Đáp án tự kiểm tra

**Q1.** Chuỗi: (1) *normalization* chuyển text hiển thị sang dạng đọc to (số, ngày, tiền, viết tắt); (2) *G2P* (nếu model có) chuyển chữ sang âm vị, giữ thanh điệu và xử lý code-switch; (3) *acoustic model* sinh biểu diễn trung gian (mel, hoặc token codec nếu là TTS dựa trên LLM); (4) *vocoder* (mel → waveform, ví dụ HiFi-GAN) hoặc *codec decoder* (token → waveform). Nhiều model gộp (2) vào backbone và học phát âm trực tiếp từ ký tự.

**Q2.** 12.5 Hz nghĩa là mỗi giây có 12.5 frame, mỗi frame 80 ms, và mỗi frame được mã hoá bằng nhiều token (16 codebook RVQ), tức 200 token/s; ở 48 kHz một frame ứng với 3840 mẫu. TTFA ≈ mạng + chờ slot + prefill + thời gian sinh `k` frame đầu + giải mã codec (+ resample/đóng gói). Nó phụ thuộc vào số frame chunk đầu (VieNeu: 2 trên GPU, 4 trên CPU), tốc độ sinh mỗi frame (RTF), tải đồng thời (slot, hàng đợi), và trạng thái nóng/lạnh của GPU.

**Q3.** *Audio-output streaming*: input text đầy đủ, output audio theo chunk (VieNeu `infer_stream`, VoxCPM2 `generate_streaming`). *Incremental text-input (bi-streaming)*: model nhận text đến dần (token LLM) và vừa nhận vừa nói (CosyVoice bi-streaming, Qwen Dual-Track). Chưa có ứng viên tiếng Việt nào làm bi-streaming được ghi nhận, nên thiết kế dùng chunker mệnh đề + gọi TTS theo mệnh đề; đó là cây cầu, không phải bi-streaming bản địa.

**Q4.** Chuyển đổi ở **một điểm duy nhất** trên ranh giới cần 16 kHz (thường là đường tới ASR/AEC reference hoặc telephony), không phải ở TTS nếu playback chấp nhận rate cao. Phải *low-pass anti-alias rồi decimate* (resampler chất lượng, giữ trạng thái giữa chunk), rồi `clip` và scale float → int16. Mất: toàn bộ phổ trên 8 kHz (ảnh hưởng cảm nhận độ sáng với người nghe, ít ảnh hưởng ASR), một ít độ chính xác (lượng tử hoá ~98 dB SNR, không nghe thấy), nguy cơ clip nếu peak quá cao, và nguy cơ alias nếu lọc sai.

**Q5.** RTF 0.011–0.02 là **throughput của batch**: tổng thời gian xử lý chia tổng audio sinh ra khi gom nhiều câu cùng lúc, nên mỗi request không hề xong nhanh gấp ~90 lần. Ngay một câu không streaming trên GPU đã là RTF 0.10, còn RTF streaming một stream của VieNeu trên RTX 3060 là 0.49 (1 stream) tới 0.59 (16 stream). Nhầm hai số sẽ dẫn tới ngân sách latency lạc quan sai.

**Q6.** Vì ASR là model mạnh có thể suy đoán đúng từ ngữ cảnh dù TTS phát âm sai nhẹ hoặc sai thanh, nên CER thấp không chứng minh nghe tự nhiên; ngược lại ASR yếu hay lỗi trên giọng/domain lạ làm CER cao dù TTS tốt. Nó không đo prosody, giọng, artifact, nhất quán. Dùng để bắt regression thô, không để xếp hạng; chất lượng phải xác nhận bằng MOS/CMOS hoặc nghe thử của người bản ngữ.

---

## Hạn chế và phạm vi bao phủ

- Mọi số liệu về model (TTFA, RTF, VRAM, số stream, license) là **Reported** từ wiki, tự đo bởi tác giả model trên một máy (RTX 3060, Windows 11, preset voice, câu 88–147 ký tự), chưa được chạy lại; không có benchmark tiếng Việt cùng điều kiện giữa các ứng viên.
- Wiki không có MOS/CMOS tiếng Việt, TTFA trên phần cứng đích, hay audit license triển khai; `status` của trang so sánh TTS là `draft`.
- Kiến thức về text frontend, họ acoustic model/vocoder, RVQ, flow matching/diffusion, MOS/CMOS và resample là giáo trình chuẩn, không phải claim từ nguồn wiki. Bit/token trong §13.4.2 (10 bit) là **suy luận số học** từ bitrate tối đa báo cáo của MOSS-Audio-Tokenizer-Nano, không phải kích thước codebook được card ghi; số kênh thật của đầu ra SDK VieNeu chưa được xác nhận.
- Mô phỏng §13.8.3 giả định tốc độ sinh hằng số và không có jitter mạng/client; thí nghiệm resample §13.9 dùng tín hiệu sin và bộ lọc sinc-Hann tự viết để minh hoạ aliasing, không phải đánh giá chất lượng resampler thực tế. Không tải weights, không chạy TTS thật hay nghe audio.
- Không bao quát: huấn luyện TTS, voice conversion, singing, TTS đa người nói trong một lượt hội thoại (Chương 14), đo lường latency end-to-end (Chương 20) và license/privacy chi tiết cho cloning (Chương 23).
- Chunker, lexicon và bộ regression prompt chi tiết thuộc Chương 19.

---

## Phụ lục chương

### Script mô phỏng số học codec, streaming lead và resample (`/tmp/ch13/tts_sim.py`, đã chạy)

```python
import math, struct

# --- A. Số học frame codec ---
fr=12.5; frame_ms=1000/fr
print("frame_ms",frame_ms,"| samples/frame @48k",48000/fr,"@24k",24000/fr,"@16k",16000/fr)
n_cb=16; max_bps=2000  # MOSS-Audio-Tokenizer-Nano: tối đa 2 kbps (Reported)
print("token/s =",fr*n_cb,"| bit/token suy ra =",max_bps/(fr*n_cb),"| PCM16 16k/48k mono kbps =",16*16,16*48)

# --- B. Mô phỏng streaming: TTFA, RTF, lead, underrun ---
def sim(rtf, first_frames, chunk_frames, prefill_ms, n_frames, frame_ms=80.0, prebuf_ms=0):
    gen_per_frame = rtf*frame_ms
    t = prefill_ms; ready=[]; produced=0; first=True
    while produced<n_frames:
        k = first_frames if first else chunk_frames
        k=min(k,n_frames-produced); t += k*gen_per_frame; produced+=k
        ready.append((t,k)); first=False
    ttfa=ready[0][0]; start=ttfa+prebuf_ms
    play_end=start; under=0; gap=0.0; min_lead=1e9
    for t,k in ready:
        if t>play_end: gap+=t-play_end; under+=1; play_end=t
        min_lead=min(min_lead, play_end-t)   # audio còn trong buffer khi chunk tới
        play_end+=k*frame_ms
    return ttfa,under,gap,min_lead
for rtf in (0.5,0.9,1.2):
    for pre in (0,200):
        print(rtf, pre, sim(rtf,2,4,21,125,prebuf_ms=pre))

# --- C. Resample 48k -> 16k: decimate thô vs low-pass rồi decimate ---
def tone(f,sr,n): return [math.sin(2*math.pi*f*i/sr) for i in range(n)]
def sinc_lp(x,sr_in,decim,cut,taps=161):
    h=[];M=taps//2
    for i in range(-M,M+1):
        a=2*cut/sr_in
        s=a if i==0 else math.sin(math.pi*a*i)/(math.pi*i)
        w=0.5+0.5*math.cos(math.pi*i/M)
        h.append(s*w)
    g=sum(h); h=[v/g for v in h]
    return [sum(h[j]*x[n-M+j] for j in range(taps)) for n in range(M,len(x)-M,decim)]
def tone_amp(x,f,sr):
    c=sum(v*math.cos(2*math.pi*f*i/sr) for i,v in enumerate(x))*2/len(x)
    s=sum(v*math.sin(2*math.pi*f*i/sr) for i,v in enumerate(x))*2/len(x)
    return math.hypot(c,s)
sr=48000; N=4800
for f in (1000,7000,10000):
    x=tone(f,sr,N); fa=f if f<8000 else abs(16000-f)
    print(f, tone_amp(x[::3],fa,16000), tone_amp(sinc_lp(x,sr,3,7000),fa,16000))

# --- D. float32 -> int16: lượng tử hoá, clip, wrap-around ---
x=[math.sin(2*math.pi*997*i/48000) for i in range(48000)]
q=[max(-32768,min(32767,round(v*32767))) for v in x]
err=[v*32767-k for v,k in zip(x,q)]
rms=math.sqrt(sum(e*e for e in err)/len(err))
print("rms LSB",rms,"SNR dB",20*math.log10((32767/math.sqrt(2))/rms))
y=[1.3*math.sin(2*math.pi*1000*i/48000) for i in range(4800)]
print("vuot nguong",sum(abs(v)>1 for v in y),"/",len(y))
w=[(round(v*32767)+32768)%65536-32768 for v in y]   # ép kiểu không clip
print("wrap min/max",min(w),max(w))
```

Kết quả đã chạy: `frame_ms 80.0`, 3840/1920/1280 mẫu mỗi frame ở 48/24/16 kHz, 200 token/s, 10 bit/token suy ra, PCM16 mono 256/768 kbps; bảng §13.8.3; tone 1/7/10 kHz: 1.000/1.000/1.000 (decimate thô) so với 1.002/0.500/0.000 (có low-pass); lỗi lượng tử hoá int16 ≈ 0.289 LSB RMS (SNR ≈ 98.1 dB); biên độ 1.3 làm 2200/4800 mẫu vượt ngưỡng, ép kiểu không clip cho đỉnh wrap tới ±31741.

Điểm cần tự thử: đổi RTF, số frame chunk đầu (1/2/4) và pre-buffer để thấy trade-off TTFA ↔ underrun; thay `x[::3]` bằng `scipy.signal.resample_poly` (nếu có) để so với bộ lọc tự viết; thử phát PCM s16le với sample rate gắn sai để nghe lỗi "chipmunk".

### Liên kết sang chương khác

- Chương 2, 3 (số hoá, định dạng/codec): sample rate, PCM, WAV, Opus; nền cho §13.7 và §13.9.
- Chương 5 (ngữ âm, chữ viết, văn bản tiếng Việt): thanh điệu, chuẩn hoá văn bản; nền cho §13.2.
- Chương 7 (AEC): audio TTS làm tham chiếu echo; yêu cầu rate khớp.
- Chương 9 (nền ML cho speech): RVQ, token, flow matching, diffusion ở mức đọc model card.
- Chương 12 (LLM): chunk đầu ra LLM, prompt cho văn bản để đọc.
- Chương 14 (speaker): speaker embedding, cloning, tính nhất quán giọng.
- Chương 16 (dataflow, audio contract): ranh giới rate/dtype toàn pipeline.
- Chương 17 (turn-taking, cancellation): huỷ stream TTS, `generation_id`, played offset.
- Chương 18 (async/streaming): hàng đợi chunk, backpressure, jitter buffer.
- Chương 19 (cầu text → speech): chunker, normalizer, lexicon, bộ regression.
- Chương 20, 21 (latency, đánh giá): TTFA trong ngân sách; MOS/CMOS, round-trip CER.
- Chương 22, 23 (runtime, license/privacy): warmup, GPU, `max_streams`; license model, cloning giọng, watermark.

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) — §5.5 (chunker, normalizer, lexicon, hai nghĩa streaming TTS), §5.6 (bảng ứng viên, ba điều dễ hiểu sai về VieNeu), §8.2 (ngân sách latency), §9.4 (fallback).
[^selection]: [Vietnamese Realtime TTS Selection](../wiki/vietnamese-realtime-tts-selection.md) — bảng "Model nào có bằng chứng tiếng Việt?", khuyến nghị có điều kiện, phạm vi và độ tin cậy.
[^vieneu]: [VieNeu-TTS v3 Turbo](../wiki/vieneu-tts-v3-turbo.md) — Model identity, Capabilities (preset, cloning, cue cảm xúc, LoRA), Runtime and SDK (`infer_stream`, `max_streams`, precision).
[^runtime]: [VieNeu-TTS Streaming Runtime and Performance](../wiki/vieneu-tts-streaming-runtime.md) — Three numbers (TTFA/RTF/lead), GPU: how streaming works, measurements on an RTX 3060, cold GPU, Choosing `max_streams`.
[^api]: [VieNeu-TTS OpenAI-compatible Speech API](../wiki/vieneu-tts-openai-speech-api.md) — `POST /v1/audio/speech` (`response_format`, `stream_format`, `sample_rate`, SSE events, mã lỗi), Server configuration.
[^qwen]: [Qwen3-TTS-Tokenizer-12Hz](../wiki/qwen3-tts-tokenizer-12hz.md) — Design (12.5 Hz, 16 codebook, ConvNet nhân quả), Encode and decode usage; phạm vi 97 ms.
[^norm]: [VietNormalizer](../wiki/vietnormalizer.md) — Capabilities, Pipeline order; chưa được wiki kiểm chứng.
[^survey]: [TTS Model Survey](../wiki/tts-model-survey.md) — catalog họ model TTS (AR codec, flow matching, diffusion, non-AR).
[^moss]: [MOSS-TTS-Nano](../wiki/moss-tts-nano.md) — mục MOSS-Audio-Tokenizer-Nano (~20M, 48 kHz stereo, 12.5 Hz, RVQ-16, 0.125–2 kbps).
