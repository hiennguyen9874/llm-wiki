# Chương 9. Nền tảng ML cho speech, đủ để đọc model card 🔴 (cơ bản) / 🟢 (sâu)

> **Loại tài liệu:** bài học chi tiết (deliverable trong `outputs/`, không phải tri thức canonical).
> **Thuộc:** [Đề cương kiến thức nền tảng cho pipeline speech-to-speech tiếng Việt](de-cuong-kien-thuc-nen-tang-speech-pipeline.md), Phần IV.
> **Chương trước:** [Chương 8. Transport mạng cho audio realtime](chuong-08-transport-mang-cho-audio-realtime.md). **Chương tiếp theo:** Chương 10. VAD, endpointing và turn detection.
> **Phục vụ:** [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md) §5.4 (ASR tiếng Việt, ba nghĩa của "realtime"), §5.6 (TTS), §5.8 (deploy tools), §9.2 (VRAM).
> **Cơ sở:** phần lớn là kiến thức giáo trình về học sâu và nhận dạng tiếng nói (CTC, transducer, attention, Conformer, lượng tử hoá). Những chỗ lấy từ tài liệu thiết kế hoặc wiki được ghi rõ kèm nhãn bằng chứng (**Reported**, **Observed**, **Synthesis**…). Các phép tính ở §9.4, §9.9, §9.10 được chạy bằng script Python thuần (**Reproduced**; script nằm ở "Phụ lục chương"). Mọi con số của model cụ thể (WER, số tham số, số stream) là **Reported** theo model card qua wiki, chưa chạy lại. Chi tiết kiến trúc của từng model (số lớp, kernel size…) là hiểu biết chung, hãy kiểm tra với model card/config bạn tải.

---

## Mục tiêu

Học xong chương này, bạn phải:

1. Đọc một model card ASR/TTS và trả lời được trong 5 phút: **kiến trúc gì, streaming kiểu nào, cần bao nhiêu bộ nhớ, đo bằng giao thức nào, dùng được cho tiếng Việt không**.
2. Giải thích được khác biệt giữa **CTC**, **Transducer (RNN-T/TDT)**, **attention encoder-decoder (Whisper)** và **LLM-based ASR**, và nói loại nào streaming tự nhiên.
3. Hiểu **cache-aware streaming**, **chunk**, **lookahead**, và tính được sàn độ trễ từ tốc độ frame của encoder.
4. Hiểu tokenization (BPE/SentencePiece), các token đặc biệt (language, timestamp, task, `<EOU>`) và vì sao chúng ảnh hưởng đến hành vi pipeline.
5. Phân biệt greedy, beam search, temperature fallback, hotword biasing, LM fusion và biết tham số nào đụng đến độ trễ/hallucination.
6. Ước lượng được bộ nhớ: **weights = params × bytes**, thêm KV cache, encoder cache, activation, workspace; hiểu fp32/fp16/bf16/int8/int4, GGUF/ggml, `int8_float16`.
7. Biết cách ML của TTS khác ASR ở mức đủ để đọc card: token audio, codec, vocoder, autoregressive vs diffusion/flow (chi tiết ở Chương 13).
8. Không bị lừa bởi các con số: WER/CER, RTF/RTFx, TTFT, concurrency, chuẩn hoá văn bản trước khi chấm.

## Câu hỏi phải trả lời được (đáp án ở cuối chương)

- Q1. CTC, RNN-T/TDT và attention encoder-decoder (Whisper) khác nhau thế nào? Loại nào streaming tự nhiên?
- Q2. "Cache-aware streaming" nghĩa là gì? Nó khác "buffered streaming" ở đâu?
- Q3. Model 0.6B ở BF16 cần khoảng bao nhiêu VRAM cho weights? Ngoài weights còn cần gì?
- Q4. Tại sao Whisper hallucinate trên im lặng còn CTC thì hầu như không?
- Q5. Nemotron có chunk 80 ms nhưng "độ trễ ASR" không phải 80 ms. Vì sao?
- Q6. Một model card ghi "WER 5.55" và một card khác ghi "WER 12.29" cho tiếng Việt. Có thể kết luận model đầu tốt hơn không?

---

## 9.1 Bức tranh tổng: một model speech là gì khi nhìn từ pipeline

Ở Chương 4 bạn đã biến waveform thành tensor log-mel. Từ đây, mọi model ASR đều có cùng "xương sống" ba khối:

```text
audio features (n_mels × T)                        Chương 4
   │
   ▼
[1] Encoder: nén thời gian + hiểu ngữ cảnh âm học
     CNN subsampling → N khối Conformer/Transformer
     ra: chuỗi vector (D × T')   với T' = T / hệ số subsampling
   │
   ▼
[2] Cơ chế căn chỉnh âm thanh ↔ chữ  (khác nhau giữa các họ)
     CTC  |  Transducer (RNN-T/TDT)  |  Attention decoder  |  LLM decoder
   │
   ▼
[3] Tokenizer: id token ↔ văn bản (BPE/SentencePiece)
   │
   ▼
văn bản (+ timestamp, language tag, punctuation tuỳ model)
```

Bốn câu hỏi quyết định cách bạn tích hợp model vào pipeline:

| Câu hỏi | Trả lời nằm ở | Ảnh hưởng đến pipeline |
|---|---|---|
| Encoder có **causal** (không nhìn tương lai) không? | khối [1] | Có streaming thật không; độ trễ do lookahead |
| Căn chỉnh theo kiểu nào? | khối [2] | Có phát được partial không; hành vi lỗi (bỏ chữ, lặp, hallucinate) |
| Vocab và token đặc biệt là gì? | khối [3] | Có language tag, `<EOU>`, timestamp; có tiếng Việt có dấu không |
| Bao nhiêu byte mỗi tham số, cache bao nhiêu? | §9.8–9.9 | VRAM, số phiên đồng thời |

> **Quy tắc đọc model card:** đừng bắt đầu từ bảng WER. Bắt đầu từ *kiến trúc + chế độ streaming + ngôn ngữ + license*; bảng WER chỉ có nghĩa khi bạn biết nó đo gì (§9.12).

---

## 9.2 Khối kiến trúc cơ bản

### 9.2.1 Subsampling (nén thời gian)

Log-mel có 100 frame/s (hop 10 ms). Encoder sâu mà chạy ở 100 frame/s thì quá đắt (attention có độ phức tạp theo bình phương độ dài) và không cần: một âm vị kéo dài ~50–100 ms. Vì vậy đầu encoder có **conv subsampling** giảm số frame:

| Hệ số | Frame rate | Mỗi frame = | Gặp ở |
|---:|---:|---:|---|
| 4× | 25 fps | 40 ms | Conformer/Zipformer cổ điển, nhiều model ESPnet/WeNet |
| 8× | 12.5 fps | 80 ms | FastConformer (họ Parakeet/Nemotron), theo hiểu biết chung |
| 2× (ở giai đoạn đầu) rồi nén thêm | 50 fps | 20 ms | Whisper: conv stride 2 → 1500 frame cho 30 s |

Hệ quả cho pipeline: **frame của encoder là đơn vị nhỏ nhất của độ trễ**. Một model 8× không thể phát hiện gì nhanh hơn 80 ms; chunk 80 ms của Nemotron tương ứng đúng 1 frame encoder (**Synthesis**: suy ra từ chunk 80 ms theo [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md) và giả định FastConformer 8×; hãy xác nhận trong config). Số chunk theo frame (tính ở §9.4): 80/160/320/560/1120 ms ↔ 1/2/4/7/14 frame.

### 9.2.2 Transformer, self-attention và vì sao nó khó streaming

**Self-attention:** mỗi frame tính "độ liên quan" với mọi frame khác rồi lấy trung bình có trọng số. Tốt cho ngữ cảnh dài, nhưng:

- **Bidirectional (non-causal):** frame t nhìn cả quá khứ lẫn tương lai. Chính xác hơn, nhưng phải có cả câu (hoặc cả cửa sổ) trước khi tính được frame nào. Whisper encoder là loại này: mỗi lần nó xử lý trọn 30 s.
- **Causal:** frame t chỉ nhìn t và quá khứ. Streaming được, nhưng mất ngữ cảnh tương lai nên WER cao hơn (xem đường cong Nemotron ở §9.5.3).
- **Chi phí:** tính attention toàn chuỗi là O(T²) theo thời gian và bộ nhớ. Đây là lý do audio dài (podcast, cuộc họp) cần chunking/long-form riêng (ví dụ ChunkFormer, [wiki](../wiki/chunkformer-vietnamese.md)).

### 9.2.3 Conformer và FastConformer

**Conformer** = Transformer + convolution. Attention bắt phụ thuộc xa (toàn câu), convolution bắt mẫu cục bộ (chuyển tiếp giữa các âm, thanh điệu). Mỗi khối gồm (xấp xỉ): feed-forward → self-attention → **depthwise conv module** → feed-forward, có residual và LayerNorm. Với tiếng nói, đây là kiến trúc encoder phổ biến nhất hiện nay.

**FastConformer** (NVIDIA): Conformer với subsampling 8× mạnh hơn và vài tối ưu, nên nhanh hơn nhiều với cùng chất lượng. Nemotron 3.5 dùng encoder FastConformer 24 lớp, embedding đầu ra D=1024 (**Reported**, [wiki](../wiki/nemotron-3.5-asr-streaming-0.6b.md), mục "Architecture and I/O").

**Zipformer** (k2/icefall; k2-fsa/sherpa): biến thể có tốc độ frame thay đổi theo tầng và attention rẻ hơn; xuất hiện trong ASR tiếng Việt như [Gipformer 68M](../wiki/gipformer-68m-rnnt.md) và [ZipFormer 30M](../wiki/zipformer-30m-vietnamese.md) (**Reported**).

### 9.2.4 Causal, chunked và lookahead

Ba cách cho encoder "biết tương lai" tới mức nào:

```text
Offline (non-causal)   [──────── cả câu ────────]  nhìn tất cả; đợi hết câu
Chunked attention      [quá khứ (cache)][CHUNK]    nhìn toàn bộ trong chunk + quá khứ
                                                    chunk càng lớn càng chính xác, càng trễ
Causal + lookahead     [quá khứ][t][+R frame]      nhìn thêm R frame tương lai
                                                    độ trễ tối thiểu ≈ R × (ms/frame)
```

- **Chunk size**: số frame xử lý mỗi lần. Chunk lớn → nhiều ngữ cảnh → WER thấp hơn, trễ cao hơn.
- **Lookahead (right context)**: số frame tương lai được phép nhìn. Mỗi frame lookahead cộng 1 frame thời gian vào độ trễ *bắt buộc*, dù compute nhanh đến đâu.
- Một model có thể **train với nhiều cỡ chunk** để chọn ở inference. Nemotron 3.5 cho chọn 80/160/320/560/1120 ms ở inference-time (**Reported**) — đây là một *núm xoay* trade-off độ trễ/WER mà bạn tune theo sản phẩm.

---

## 9.3 Bốn họ ASR: cách căn chỉnh âm thanh với chữ

Vấn đề cốt lõi: audio có T' frame, chữ có U token, thường T' ≫ U và **không biết frame nào tương ứng token nào** (alignment). Mỗi họ giải bài toán này khác nhau.

### 9.3.1 CTC (Connectionist Temporal Classification)

- **Ý tưởng:** mỗi frame dự đoán *một* token trong vocab + một token đặc biệt **blank** (`_`). Đầu ra cuối = bỏ lặp liên tiếp rồi bỏ blank.
- **Ví dụ** (**Reproduced**, §9.4): chuỗi frame `h h _ e e _ l l _ l l o` → gộp lặp → bỏ blank → `hello`. Chữ `l` đôi ở "hello" cần blank xen giữa; `hel_lo` cũng ra `hello`, còn `hello` không có blank giữa hai `l` ra `helo`.
- **Giả định độc lập có điều kiện:** mỗi frame được quyết định độc lập, không có "trí nhớ ngôn ngữ" giữa các token đã sinh. Hệ quả: dễ viết sai chính tả/âm gần giống nếu không có LM bên ngoài.
- **Ưu:** đơn giản, **rất nhanh** (một lượt encoder + argmax, song song hoá hoàn toàn), dễ streaming nếu encoder causal/chunked, timestamp theo frame tự nhiên.
- **Nhược:** WER thường kém transducer/attention cùng cỡ nếu không có LM; không tự sinh dấu câu/viết hoa tốt (trừ khi train với text đã định dạng).
- **Hành vi lỗi:** thường *bỏ* hoặc *thay* âm; **ít hallucinate** vì không có decoder tự do sinh chữ từ không khí. Trên im lặng nó thường ra chuỗi blank → rỗng. Đây là câu trả lời của Q4 (§9.14).
- **Gặp ở:** [Parakeet CTC](../wiki/parakeet-ctc-0.6b.md), [ChunkFormer CTC 110M](../wiki/chunkformer-vietnamese.md), Granite TurboCTC (**Reported**).

### 9.3.2 Transducer: RNN-T và TDT

- **Ý tưởng:** thêm một **prediction network** (như language model nhỏ, nhìn các token đã phát) và một **joint network** kết hợp encoder frame + trạng thái prediction để quyết định: phát token nào *hoặc* phát blank (= "sang frame tiếp theo").

```text
encoder frame t ─┐
                 ├→ joint → {token ∈ vocab | blank}
prediction(y<u) ─┘      token → u += 1 (ở lại frame t, hỏi tiếp)
                        blank → t += 1 (sang frame mới)
```

- **Ưu:** (1) **streaming tự nhiên**: quyết định từng bước theo thời gian, không cần thấy tương lai ngoài lookahead của encoder; (2) có phụ thuộc giữa các token (ngầm LM) nên chính xác hơn CTC; (3) phát partial ngay khi token xuất hiện.
- **Nhược:** huấn luyện nặng hơn; decode tuần tự hơn CTC (vòng lặp trên frame và token); triển khai (batching, GPU kernel) phức tạp hơn.
- **TDT (Token-and-Duration Transducer):** ngoài token, joint còn dự đoán **duration** (nhảy bao nhiêu frame), nên bỏ qua các frame blank hàng loạt → nhanh hơn RNN-T chuẩn. Dòng [Parakeet TDT](../wiki/parakeet-tdt-0.6b-v3.md) thuộc loại này (**Reported**).
- **Hành vi lỗi:** tương tự CTC nhưng mượt hơn; hiếm khi sinh cả câu bịa. Có thể "kẹt lặp" hiếm.
- **Gặp ở:** Nemotron 3.5 (FastConformer-**RNNT**, cache-aware), [Parakeet RNNT](../wiki/parakeet-rnnt-0.6b.md), [Gipformer 68M](../wiki/gipformer-68m-rnnt.md), ChunkFormer RNNT 113M, Multitalker Parakeet.

### 9.3.3 Attention encoder-decoder (AED) — họ Whisper

- **Ý tưởng:** encoder biến audio thành chuỗi vector; **decoder** là Transformer autoregressive sinh từng token, mỗi bước dùng **cross-attention** nhìn vào toàn bộ output của encoder.
- **Whisper cụ thể** (kiến thức chung): input log-mel 80 (v1–v2) hoặc 128 bin (large-v3) cho cửa sổ **cố định 30 s** (pad nếu ngắn), encoder ra 1500 frame (§9.4), decoder sinh token kèm **token đặc biệt điều khiển**: `<|startoftranscript|>`, `<|vi|>` (ngôn ngữ), `<|transcribe|>`/`<|translate|>` (tác vụ), `<|notimestamps|>` hay token timestamp. Huấn luyện bằng ~5 triệu giờ dữ liệu weak supervision (**Reported**, [Whisper large-v3-turbo](../wiki/whisper-large-v3-turbo.md)).
- **Ưu:** mạnh, đa ngôn ngữ, tự có dấu câu/viết hoa, tự dịch, chịu nhiễu tốt vì dữ liệu train rất đa dạng.
- **Nhược:**
  - **Không streaming tự nhiên:** encoder non-causal trên cửa sổ 30 s; muốn "live" phải bọc ngoài (chia cửa sổ, chồng lấp, commit prefix ổn định như WhisperLiveKit). Bọc WebSocket **không** biến nó thành causal encoder (**Reported**, thiết kế §5.4.1).
  - **Hallucination:** decoder là language model tự do. Khi audio là im lặng/nhạc/nhiễu, nó có xu hướng sinh những câu "quen" từ dữ liệu train (YouTube outro kiểu "hãy subscribe cho kênh…"). Wiki ghi nhận cho tiếng Việt ([Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md), **Reported**).
  - **Lặp/loop:** `condition_on_previous_text=True` có thể lan truyền lỗi lặp sang đoạn sau.
  - Chi phí decoder tỉ lệ với số token sinh ra (autoregressive), nên **cắt số lớp decoder** là cách tăng tốc chính: large-v3-turbo giảm decoder từ 32 xuống 4 lớp (809M vs 1550M tham số, **Reported**).
- **Biến thể liên quan:** Faster-Whisper (cùng model, chạy trên CTranslate2 — nhanh hơn tới ~4×, ít bộ nhớ hơn, hỗ trợ int8; **Reported**, [wiki](../wiki/faster-whisper.md)); PhoWhisper (fine-tune Whisper cho tiếng Việt; [wiki](../wiki/phowhisper.md)); Distil-Whisper (chưng cất; bản v3.5 chỉ tiếng Anh theo thiết kế §5.4.2, **Reported**).

### 9.3.4 LLM-based ASR (audio encoder → projector → LLM decoder)

- **Ý tưởng:** lấy một **audio encoder** (kiểu Whisper/Conformer), một **projector** (MLP/Q-Former) ánh xạ vector audio vào không gian embedding của LLM, rồi để **LLM** (Qwen, Llama…) *đọc "token audio" như đọc prompt* và sinh transcript.

```text
audio ─▶ audio encoder ─▶ projector ─▶ [token audio...][prompt text] ─▶ LLM decoder ─▶ transcript
```

- **Ưu:** tận dụng kiến thức ngôn ngữ rất lớn của LLM → thường tốt ở ngữ cảnh khó, tên riêng, code-switch; **một model làm nhiều việc** (ASR + dịch + hỏi đáp về audio) bằng prompt; có thể nhận context/hotword trong prompt.
- **Nhược:** nặng (hàng tỉ tham số), decode autoregressive nên TTFT/độ trễ phụ thuộc runtime LLM; streaming cần thiết kế riêng (chunk + commit policy); rủi ro **hallucination kiểu LLM** (bịa/ tự sửa câu). Con số "0.6B/1.7B" của Qwen3-ASR **chưa tính hết** encoder, projector và cache (**Reported**, thiết kế §5.4.2).
- **Gặp ở:** Qwen3-ASR (0.6B/1.7B), [Canary-Qwen-2.5B](../wiki/canary-qwen-2.5b.md) (kết hợp FastConformer encoder + Qwen), Audio8, GLM-ASR, Fun-ASR, Higgs Audio STT, VibeVoice-ASR (xem [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md)).
- **Streaming:** với họ này, thiết kế gọi là *buffered/policy streaming* (paper Qwen3-ASR dùng chunk 2 s, **Reported**). Dùng được nhưng **không đồng nghĩa** với cache-aware streaming (§9.5).

### 9.3.5 Bảng so sánh bốn họ (trả lời Q1)

| Tiêu chí | CTC | Transducer (RNN-T/TDT) | AED (Whisper) | LLM-based |
|---|---|---|---|---|
| Căn chỉnh | blank + gộp lặp, độc lập theo frame | joint(encoder, prediction) từng bước | cross-attention, sinh tự do | LLM đọc audio token, sinh tự do |
| Streaming tự nhiên | **Có** (encoder causal/chunked) | **Có, tốt nhất** | **Không** (cửa sổ 30 s) | Không; cần chunk+commit |
| Partial sớm | Có | Có | Chỉ qua bọc ngoài | Chỉ qua bọc ngoài |
| Tốc độ | Rất nhanh | Nhanh | Trung bình (decoder tuần tự) | Chậm hơn (LLM) |
| Chính xác (cùng cỡ) | Thấp hơn nếu không LM | Cao | Cao, mạnh đa ngôn ngữ | Thường cao nhất ở ngữ cảnh khó |
| Dấu câu/viết hoa | Chỉ nếu train với text có định dạng | Tuỳ model (Nemotron 3.5 có PnC) | Có | Có |
| Rủi ro đặc trưng | Sai chính tả/âm | Hiếm: lặp | **Hallucination trên im lặng**, lặp | Bịa nội dung, tự sửa câu |
| Timestamp | Theo frame | Theo frame | Token timestamp hoặc alignment ngoài | Thường không có |

**Heuristic chọn:** cần *partial sớm + nhiều phiên* → transducer cache-aware. Cần *final chính xác sau lượt nói* → AED/LLM-based turn-final. Cần *rất rẻ, CPU* → CTC hoặc transducer nhỏ int8. Đây chính là logic của ba "nghĩa realtime" và mẫu ghép **two-pass** trong thiết kế (§5.4.3, **Reported/Synthesis**).

---

## 9.4 Tính tay: frame, chunk và độ trễ do lookahead (**Reproduced**)

Một số phép tính đơn giản giúp đọc card nhanh hơn (script ở phụ lục).

**Tốc độ frame sau subsampling**

| Subsampling | fps | ms/frame |
|---:|---:|---:|
| 4× | 25 | 40 |
| 8× | 12.5 | 80 |

**Whisper:** 30 s × 100 fps / 2 (conv stride 2) = **1500 frame** encoder — cố định bất kể audio ngắn hay dài, vì được pad tới 30 s. Đây là lý do clip rất ngắn vẫn tốn ~đúng như clip dài ở phía encoder (nếu không dùng kỹ thuật cắt/pad đặc biệt), và có "nhiều không gian trống" để decoder hallucinate.

**Chunk Nemotron theo frame 8× (80 ms)** (**Synthesis**: giả định 8×):

| Chunk | Số frame encoder |
|---:|---:|
| 80 ms | 1 |
| 160 ms | 2 |
| 320 ms | 4 |
| 560 ms | 7 |
| 1120 ms | 14 |

**Sàn độ trễ của một lần tính (không tính compute, mạng, endpoint):**

```text
độ trễ nhìn thấy tối thiểu ≈ thời gian chờ đủ chunk  +  lookahead  +  compute  (+ commit policy)
```

- Thời gian chờ đủ chunk: token ở *đầu* chunk phải đợi tới *cuối* chunk mới được xử lý → trung bình trễ ≈ chunk/2, trễ tối đa ≈ chunk.
- Chunk 320 ms nghĩa là bạn nhận cập nhật mỗi 320 ms; **không** nghĩa là chữ hiện sau 320 ms từ lúc nói. Chữ có thể còn **chưa ổn định** (revision) hoặc chờ commit.
- Vì vậy thiết kế nói: "chunk size không phải độ trễ stable-text hay endpoint→final" (**Reported/Synthesis**, wiki Nemotron mục "Vietnamese operating curve"). Đây là đáp án của Q5 (§9.14).

---

## 9.5 Streaming ở mức model

### 9.5.1 Ba mức "streaming" cần phân biệt

Khớp với §5.4.1 của thiết kế:

| Mức | Cơ chế | Ví dụ | Dấu hiệu trong card |
|---|---|---|---|
| **Native/stateful (cache-aware)** | Encoder causal/chunked, giữ **cache** nội bộ; mỗi chunk chỉ tính phần mới | Nemotron 3.5, Parakeet realtime EOU, Multitalker Parakeet | "cache-aware", "streaming", chunk size/`att_context_size` |
| **Buffered/policy** | Model offline, bọc ngoài bằng cửa sổ trượt + chồng lấp + quy tắc commit prefix | Qwen3-ASR (chunk 2 s), Whisper + WhisperLiveKit | "streaming via wrapper", vLLM streaming, chunk ~giây |
| **Turn-final** | Chờ hết lượt (VAD/turn) rồi decode cả câu | Whisper, PhoWhisper, ChunkFormer large, Cohere | "offline", "long-form", không nói đến chunk/cache |

### 9.5.2 Cache-aware streaming hoạt động thế nào (trả lời Q2)

**Streaming kiểu buffered cổ điển** (không cache): mỗi lần có audio mới, bạn đưa vào model *cả cửa sổ chồng lấp* gồm audio cũ + mới. Phần audio cũ bị tính lại nhiều lần → lãng phí compute, nhất là khi nhiều phiên.

**Cache-aware streaming:** mỗi lớp encoder giữ lại **state** từ các chunk trước:

- với **self-attention**: cache các key/value (hoặc đầu ra lớp) của ngữ cảnh quá khứ trong cửa sổ attention;
- với **convolution** (Conformer): cache các frame cuối đủ để lấp **receptive field** của kernel;
- mỗi chunk mới chỉ đi qua **một lần**, nhưng vẫn "thấy" ngữ cảnh quá khứ qua cache.

```text
chunk k-1 ─▶ [encoder layers] ─▶ lưu cache_k-1 (attn K/V + conv tail)
chunk k   ─▶ [encoder layers + cache_k-1] ─▶ output_k, cache_k
```

Wiki ghi Nemotron: "caches for all encoder self-attention and convolution layers so only new non-overlapping audio chunks are processed while cached context is reused, eliminating the redundant overlapping computation of traditional buffered streaming" (**Reported**, [wiki](../wiki/nemotron-3.5-asr-streaming-0.6b.md)). Hệ quả thực tế:

- **Compute mỗi chunk gần như không đổi** theo độ dài hội thoại, nên số phiên đồng thời cao hơn. Card báo throughput trên H100 cỡ ~240 stream ở chunk 80 ms và ~2.400 ở 1.12 s (**Reported**; thiết kế §9.3). Đó là trần của riêng ASR, không phải của cả pipeline.
- **Mỗi phiên có state riêng** → bạn phải quản lý vòng đời state theo session (tạo khi mở, reset khi hết lượt/huỷ, giải phóng khi đóng). Đây là nguồn bug thực tế: rò state giữa các phiên, hoặc quên reset sau barge-in.
- **Phải giữ thứ tự chunk** và không bỏ chunk; mất một chunk làm cache lệch với audio thật.

### 9.5.3 Núm xoay độ trễ ↔ độ chính xác

Từ đường cong vi-VN trong wiki (FLEURS, LangID, **Reported**, chưa chạy lại):

| Chunk | WER vi-VN (%) |
|---:|---:|
| 80 ms | 13.41 |
| 160 ms | 12.87 |
| 320 ms | 12.29 |
| 560 ms | 11.78 |
| 1120 ms | 11.18 |

Đọc đúng: tăng chunk 14× (80→1120 ms) chỉ giảm ~2.2 điểm WER tuyệt đối, và sau 320 ms lợi ích mỗi nấc nhỏ. Thiết kế đề xuất bắt đầu thử **160–320 ms**, coi là *thí nghiệm* chứ không phải SLA đã kiểm chứng (**Synthesis**). Lưu ý đây là điểm tốt nhất trong một dải liên tục; nếu pipeline có VAD/turn timeout 1.2–1.5 s thì lợi ích chunk nhỏ có thể bị che bởi endpoint (Chương 10, 20).

### 9.5.4 Endpointing trong chính model: token `<EOU>`

Một số model streaming phát **token end-of-utterance** ngay trong chuỗi token (ví dụ Parakeet Realtime EOU 120M, độ trễ 80–160 ms, **Reported**, [wiki](../wiki/parakeet-realtime-eou-120m-v1.md); model chỉ English theo wiki). Ý nghĩa: ASR tự dự đoán "người nói xong rồi" từ cả âm học lẫn ngữ cảnh ngôn ngữ, bổ sung (không thay thế) VAD năng lượng. Chi tiết ở Chương 10.

---

## 9.6 Tokenization

### 9.6.1 Vì sao không dùng chữ cái hay từ

- **Ký tự:** vocab nhỏ (~100 với tiếng Việt có dấu thêm), nhưng chuỗi dài, mô hình khó học thứ tự.
- **Từ:** vocab khổng lồ, từ hiếm/OOV không có. Tiếng Việt viết có dấu cách giữa *âm tiết*, không giữa *từ* → "từ" theo chính tả là âm tiết, vocab âm tiết khoảng vài nghìn (Chương 5).
- **Subword (BPE/SentencePiece/unigram):** cân bằng: ~256–10 000 token, tự chia từ hiếm thành mảnh.

### 9.6.2 BPE và SentencePiece (mức khái niệm)

- **BPE:** bắt đầu từ ký tự, lặp lại *gộp cặp liền kề thường gặp nhất* cho đến khi đủ kích thước vocab.
- **SentencePiece:** thư viện huấn luyện tokenizer (BPE hoặc unigram) trực tiếp trên văn bản thô, coi khoảng trắng là ký hiệu `▁`, nên **tái tạo văn bản không mất khoảng trắng**.
- **Tiếng Việt:** chuẩn Unicode quan trọng (NFC vs NFD: "ế" là một code point hay hai). Nếu tokenizer train trên NFC mà data của bạn là NFD, bạn sẽ thấy token lạ hoặc `<unk>`. Hãy chuẩn hoá về cùng dạng *trước* khi tokenize (Chương 5).
- **Tác động lên pipeline:**
  - **Số token ảnh hưởng độ dài decode** → với AED/LLM-based là tốc độ.
  - **Tokenizer của ASR ≠ tokenizer của LLM ≠ tokenizer của TTS.** Chúng không dùng chung; bạn chuyển giữa chúng bằng *văn bản*, không bằng id (Chương 19).

### 9.6.3 Token đặc biệt

| Loại | Ví dụ | Ý nghĩa với pipeline |
|---|---|---|
| Ngôn ngữ | `<|vi|>` (Whisper); prompt one-hot `vi-VN` (Nemotron 3.5) | **Phải đặt tường minh**; mặc định có thể là `en-US` (pipeline Transformers của Nemotron mặc định index-0 `en-US`; **Reported**, thiết kế §5.4.2) |
| Tác vụ | `<|transcribe|>`, `<|translate|>` | Dùng nhầm → ra tiếng Anh thay vì tiếng Việt |
| Timestamp | `<|0.00|>` … hoặc `<|notimestamps|>` | Bật/tắt ảnh hưởng tốc độ và định dạng |
| Tag ngôn ngữ phát hiện | `<vi-VN>` sau dấu câu cuối (Nemotron `auto`) | Phải **lọc** trước khi đưa cho LLM/TTS: `strip_lang_tags`/`skip_special_tokens` (**Reported**) |
| Điều khiển | `<EOU>`, `<blank>`, `<unk>`, BOS/EOS | `<EOU>` là tín hiệu turn; `<unk>` là dấu hiệu tokenizer không phủ ký tự |
| LLM-ASR | prompt hệ thống, hotword, context | Một cách đưa thuật ngữ/tên riêng (§9.7.4) |

> **Bẫy thực tế:** token đặc biệt rò vào văn bản gửi sang TTS sẽ bị đọc thành tiếng hoặc làm TTS lỗi. Luôn có bước lọc/chuẩn hoá giữa ASR và các tầng sau.

---

## 9.7 Decoding: từ xác suất ra văn bản

### 9.7.1 Greedy và beam search

- **Greedy:** mỗi bước chọn token xác suất cao nhất. Nhanh nhất, ổn định, hơi kém chính xác.
- **Beam search (beam size B):** giữ B giả thuyết tốt nhất. Chính xác hơn một chút, **chi phí ~tuyến tính theo B** và có thể thêm độ trễ. Report cho faster-whisper: `beam_size=1–3` (greedy nhanh nhất; 3 tốt hơn nhưng tốn thêm ~30–50% độ trễ; **Reported**, [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md)).
- Với CTC/transducer, greedy thường đủ tốt; beam hữu dụng khi có LM hoặc hotword.

### 9.7.2 Temperature và temperature fallback (Whisper)

Whisper có chiến lược dự phòng: giải mã với `temperature=0`; nếu kết quả "trông xấu" (log-prob trung bình thấp, compression ratio cao tức là lặp, hoặc `no_speech_prob` cao) thì **thử lại với temperature cao hơn** (0.2, 0.4, … 1.0). Hệ quả:

- Có thể **tăng đáng kể và không đoán trước độ trễ** (một lượt có thể decode 2–6 lần).
- Sinh ngẫu nhiên → có thể tạo nội dung bịa.
- Khuyến nghị cho voice agent (**Reported**): `temperature=0.0` để tắt fallback, `condition_on_previous_text=False`, `language="vi"` bắt buộc, kết hợp ngưỡng `no_speech`/`log_prob`/compression ratio để loại segment nghi ngờ.

### 9.7.3 Language model fusion

- **Shallow fusion:** cộng điểm LM bên ngoài (n-gram/neural) vào điểm decode: `score = log P_asr + λ · log P_lm + μ · len`. Dễ dùng khi muốn ép từ vựng miền (y tế, ngân hàng).
- **Deep/cold fusion**, **rescoring N-best:** phức tạp hơn; thường dùng trong hệ thống trước kỷ nguyên LLM-ASR.
- Cảnh báo: λ lớn thì LM "thắng" âm thanh → ASR *tự sửa thành câu trôi chảy nhưng sai nội dung*.

### 9.7.4 Hotword / context biasing

Mục tiêu: nhận đúng tên riêng, sản phẩm, thuật ngữ hiếm.

| Kỹ thuật | Cách hoạt động | Ghi chú |
|---|---|---|
| Boost trong beam search/trie | cộng điểm khi đường đi khớp cụm hotword | Cần beam; có thể làm tăng false-positive |
| Contextual adapter trong model | model học nhận danh sách phụ | Phải train; có ở một số model |
| Prompt cho LLM-ASR | nhét danh sách từ vào prompt | Linh hoạt, nhưng LLM có thể "ép" từ vào chỗ không có |
| Hậu xử lý (lexicon sửa) | ánh xạ cách đọc sai thường gặp → đúng | An toàn, dễ kiểm; cần dữ liệu lỗi thật |

Vẫn phải đo **false-positive** (từ hotword xuất hiện khi không ai nói) — Chương 21.

### 9.7.5 Dấu câu, viết hoa và ITN

Một số model xuất văn bản "đã định dạng" (PnC); số, ngày, tiền tệ có thể ở dạng *đọc* ("hai mươi ba tháng chín") hoặc *viết* ("23/9"). **ITN** (inverse text normalization) chuyển dạng đọc → dạng viết. Ngược chiều TTS cần **TN** (text normalization) dạng viết → dạng đọc. Biết model của bạn xuất dạng nào quyết định bạn có cần ITN/TN ở Chương 19 và cách chấm WER (§9.12).

---

## 9.8 Độ chính xác số và lượng tử hoá

### 9.8.1 Các kiểu số

| Kiểu | Bit | Byte/param | Ghi chú |
|---|---:|---:|---|
| fp32 | 32 | 4 | Chuẩn khi train; thường quá lớn cho serving |
| fp16 | 16 | 2 | Dải số hẹp hơn bf16; phổ biến trên GPU inference |
| bf16 | 16 | 2 | Cùng dải số fp32, độ chính xác thấp hơn; ổn định khi train/infer |
| int8 | 8 | 1 | Lượng tử hoá; cần scale; giảm bộ nhớ 2–4× so với fp16/fp32 |
| int4 | 4 | 0.5 | Giảm mạnh bộ nhớ; có thể giảm chất lượng, nhạy với model nhỏ |

### 9.8.2 Lượng tử hoá: cái gì được lượng tử

- **Weight-only** (chỉ trọng số): phổ biến nhất ở int8/int4; activation vẫn fp16. Giảm bộ nhớ/băng thông, tốc độ cải thiện tuỳ phần cứng.
- **Weight + activation** (W8A8…): giảm compute; cần calibration.
- **Per-channel/group** scale: chất lượng tốt hơn per-tensor.
- **Mixed precision**: một số lớp nhạy (embedding, lớp cuối, norm) giữ fp16.
- **`int8_float16`** trong CTranslate2/Faster-Whisper: trọng số int8, tính toán fp16 — lựa chọn cân bằng trên GPU (thiết kế §5.4, §6 profile A/E, **Reported**). **`int8`** thuần phù hợp CPU.
- **Lưu ý:** WER sau lượng tử hoá **phải đo lại** trên dữ liệu của bạn; model card hiếm khi báo số cho từng mức bit.

### 9.8.3 GGUF và ggml

- **GGUF** là định dạng file chứa weights (đã lượng tử hoá) + metadata (kiến trúc, tokenizer, hyperparameter) cho hệ sinh thái **ggml**/llama.cpp. Tên như `*.q8_0.gguf` ghi mức lượng tử (Q8_0 ≈ 8-bit theo khối).
- Trong wiki: NeMo-Speech.cpp chạy Nemotron Q8 GGUF (HTTP/WS/C SDK), audio.cpp là framework C++ cho nhiều model audio (xem [Audio.cpp GGUF packages](../wiki/audio-cpp-gguf-packages.md), [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md)).
- **Bẫy:** GGUF giữa các runtime **không thay thế được cho nhau** (layout/tokenizer khác) và một port cộng đồng cần **kiểm tra parity** với bản gốc (**Reported**, thiết kế §5.8). Số liệu tốc độ của model EN (ví dụ 27 ms CPU/2.3 ms RTX 4090 mỗi chunk 160 ms) *không* chuyển sang model 3.5/vi.
- **ONNX** (Gipformer, Silero, VieNeu ONNX) là đường khác: đồ thị tính toán chuẩn chạy trên ONNX Runtime CPU/GPU, thường kèm int8.

### 9.8.4 Quy tắc chọn

```text
GPU server, model vừa đủ VRAM  →  bf16/fp16 (đơn giản, chất lượng gốc)
GPU thiếu VRAM / nhiều phiên   →  int8 weight-only (int8_float16) → đo WER
CPU / edge                     →  int8 hoặc Q8 GGUF; int4 chỉ khi đã A/B
Mọi trường hợp                 →  đo lại WER/CER, độ trễ, hallucination trên tập của bạn
```

---

## 9.9 Tài nguyên: bộ nhớ và compute (trả lời Q3)

### 9.9.1 Công thức nền

```text
weights_bytes ≈ params × bytes_per_param
```

**Bảng tính (GB, 10⁹ byte, bỏ qua overhead file; Reproduced):**

| Params | fp32 | bf16/fp16 | int8 | int4 |
|---:|---:|---:|---:|---:|
| 68M (Gipformer) | 0.27 | 0.14 | 0.07 | 0.03 |
| 120M (Parakeet EOU) | 0.48 | 0.24 | 0.12 | 0.06 |
| **0.6B** (Nemotron, Qwen3-ASR 0.6B) | 2.4 | **1.2** | 0.6 | 0.3 |
| 809M (Whisper turbo) | 3.24 | 1.62 | 0.81 | 0.40 |
| 1.55B (Whisper large-v3) | 6.2 | 3.1 | 1.55 | 0.78 |
| 1.7B (Qwen3-ASR 1.7B) | 6.8 | 3.4 | 1.7 | 0.85 |
| 4B (LLM voice loop) | 16 | 8 | 4 | 2.0 |
| 7B | 28 | 14 | 7 | 3.5 |

Số "0.6B BF16 ≈ 1.2 GB" khớp với ví dụ trong thiết kế §9.2 (**Synthesis**).

### 9.9.2 Ngoài weights còn cần gì

| Thành phần | Là gì | Tăng theo | Ghi chú |
|---|---|---|---|
| **Activation** | giá trị trung gian khi forward | batch × độ dài | thường nhỏ khi inference, lớn khi audio dài/batch lớn |
| **KV cache** (decoder/LLM) | K,V của các token đã sinh/đã đọc | độ dài ngữ cảnh × số phiên | xem công thức dưới |
| **Encoder cache** (streaming) | attention K/V + conv tail theo lớp | số phiên × cửa sổ attention | state per session |
| **Workspace/ CUDA context** | bộ đệm tạm, kernel, thư viện cuBLAS/cuDNN | cố định + theo kernel | thường vài trăm MB tới >1 GB |
| **Bộ nhớ phân mảnh** | allocator của framework | theo thời gian | cần dư headroom ~10–20% |
| **Nhiều model cùng GPU** | ASR + LLM + TTS | cộng dồn | thiết kế §9.2: 24 GB chia Whisper turbo + VieNeu + LLM |

**Công thức KV cache** (cho decoder Transformer; kiến thức chung):

```text
KV_bytes = 2 (K và V) × số_lớp × số_đầu_KV × head_dim × độ_dài_token × bytes × số_phiên
```

Ví dụ (**Reproduced**, giả định minh hoạ, *không phải* của model cụ thể nào): 28 lớp, 8 đầu KV (GQA), head_dim 128, 4096 token, bf16 → **≈ 0.44 GiB mỗi phiên**; nếu là MHA 32 đầu KV, 32 lớp → **≈ 2.0 GiB mỗi phiên**. Với 16 phiên thì KV một mình có thể vượt 7–32 GiB: đây là lý do **LLM trong voice loop** (Chương 12) thường là thành phần tốn VRAM nhất, và GQA/KV quantization/prefix caching quan trọng.

### 9.9.3 Batch, CUDA graph, warmup

- **Batch:** gộp nhiều yêu cầu để tăng throughput. Với voice realtime, ưu tiên **cadence đều** hơn throughput tối đa (Synthesis, thiết kế §9.3): batch lớn kéo dài độ trễ của từng phiên.
- **Continuous batching** (LLM/TTS): thêm/bớt phiên giữa các bước decode, giữ GPU bận mà không chờ batch đầy.
- **CUDA graph:** ghi sẵn chuỗi kernel để giảm overhead phóng kernel; hữu ích khi mỗi bước tính rất nhỏ (decoder token-by-token, streaming chunk nhỏ). Đổi lại: shape phải cố định → cần *padding/bucket*.
- **Warmup:** lần chạy đầu thường chậm (JIT, cudnn autotune, cấp phát, nạp lazy). **Phải warmup lúc khởi động** và **loại các lần chạy đầu khỏi số đo độ trễ**, nếu không p95/p99 sẽ bị nhiễu.

### 9.9.4 Concurrency và "năng lực" công bố

- Con số như "~240 stream tại chunk 80 ms trên H100" là **throughput của riêng ASR** dưới điều kiện benchmark. Nó không tính VAD, LLM, TTS, mạng, và có thể đo ở "độ trễ cuối-token" chấp nhận được khác với SLA của bạn.
- Số TTFT 92 ms của Qwen3-ASR 0.6B ở concurrency 1 (input ~2 phút có sẵn) so với **3210 ms (P95 6195 ms) ở concurrency 128** (**Reported**, thiết kế §5.4.2) cho thấy **độ trễ co giãn rất mạnh theo tải**. Luôn hỏi: *ở concurrency nào, đo cái gì?*

---

## 9.10 Chỉ số hiệu năng: RTF, RTFx, TTFT

| Chỉ số | Định nghĩa | Đọc thế nào |
|---|---|---|
| **RTF** (real-time factor) | thời gian xử lý ÷ thời lượng audio | **Thấp hơn là nhanh hơn**; RTF < 1 theo kịp thời gian thực |
| **RTFx** | thời lượng audio ÷ thời gian xử lý | **Cao hơn là nhanh hơn**; nghịch đảo của RTF |
| **TTFT** (time-to-first-token) | từ lúc gửi tới lúc có token đầu | Quan trọng với LLM/ASR sinh tự do |
| **TTFA** (time-to-first-audio) | từ lúc có text tới lúc có byte audio đầu | Quan trọng với TTS (Chương 13, 20) |
| **Stable-text latency** | từ lúc nói tới lúc chữ không còn bị sửa | Chỉ số *thật* của ASR streaming |
| **Endpoint → final** | từ lúc người nói dừng tới lúc có final transcript | Chỉ số *thật* của ASR turn-final |

> **Bẫy định nghĩa:** thiết kế ghi rõ "Faster Qwen3-TTS dùng chữ 'RTF' theo nghĩa RTFx" (**Reported/Synthesis**, §5.8). Một con số "RTF 6.0" có thể là *nhanh gấp 6* hoặc *chậm gấp 6* tuỳ tác giả. **Luôn đọc định nghĩa trước khi so sánh.**
>
> **RTF < 1 chỉ có nghĩa là theo kịp luồng audio, chưa đủ để có văn bản dùng được sớm** (thiết kế §5.4.1): độ trễ thật còn gồm chunk accumulation, lookahead, scheduling, transport và commit policy.

---

## 9.11 ML cho TTS: tối thiểu để đọc card (chi tiết ở Chương 13)

ASR đi *audio → text*. TTS đi *text → audio*, khó hơn ở chỗ **một văn bản có vô số cách đọc hợp lệ** (một-nhiều). Từ đó các họ kiến trúc:

| Họ | Cơ chế | Tính chất | Ví dụ trong wiki |
|---|---|---|---|
| **Acoustic model + vocoder** (2 giai đoạn) | text → mel (FastSpeech/VITS-like) → vocoder (HiFi-GAN…) → waveform | Nhẹ, nhanh, ổn định; khó clone giọng linh hoạt | Kokoro (vi), Supertonic (theo thiết kế §6) |
| **Neural codec LM** | text → *token audio rời rạc* (từ codec như EnCodec/DAC/…) bằng LM autoregressive → decoder codec → waveform | Tự nhiên, **voice cloning zero-shot**; tốc độ phụ thuộc số token/giây và LM | VieNeu-TTS, nhiều model clone giọng |
| **Diffusion / flow-matching** | sinh mel hoặc latent bằng quá trình khử nhiễu/dòng liên tục, rồi vocoder | Chất lượng cao; streaming khó hơn (cần chunk/causal) | CosyVoice-họ (flow matching) |
| **Hybrid LM + flow** | LM sinh token ngữ nghĩa, flow/diffusion dựng âm thanh | Cân bằng ngữ điệu và độ trung thực | CosyVoice 2/3 |

Những khái niệm cần nhận ra khi đọc card TTS:

- **Codec / token rate:** số token audio mỗi giây (ví dụ vài chục tới hơn 100 token/s). Token rate × số codebook quyết định chi phí sinh; codebook nhiều → chất lượng cao, sinh chậm.
- **Vocoder:** mạng chuyển đặc trưng (mel/latent) sang waveform; chất lượng và tốc độ phụ thuộc vocoder, **nhưng log-mel không "đảo" sạch thành audio** nên TTS cần vocoder (Chương 4).
- **Autoregressive vs non-autoregressive:** AR sinh tuần tự (streaming tự nhiên nhưng có rủi ro lặp/bỏ chữ), non-AR song song (nhanh, ổn định, ít tự nhiên hơn).
- **Voice cloning:** model nhận **reference audio** (vài giây tới chục giây) + đôi khi **transcript của reference**. Reference là **dữ liệu nhạy cảm** (thiết kế §9.5).
- **Streaming TTS:** phát audio ngay khi có chunk đầu; chỉ số quan trọng là TTFA và việc phát có **đứt/rè ở biên chunk** không (Chương 13, 19).
- **Đọc card TTS:** ngoài số tham số, hãy tìm **số stream đồng thời tối đa** (VieNeu `VIENEU_MAX_STREAMS` mặc định 16 trên GPU/1 trên CPU, vượt → HTTP 429; **Reported**, thiết kế §5.8), **sample rate đầu ra** (24 kHz thường gặp; cần resample cho playback/telephony), và **license của giọng/reference**.

---

## 9.12 Đọc model card: quy trình 10 bước

Dùng như checklist; mỗi mục kèm "bẫy" thường gặp.

| # | Câu hỏi | Tìm ở đâu trong card | Bẫy |
|---:|---|---|---|
| 1 | **Tác vụ & họ model** (CTC/RNNT/AED/LLM-ASR/TTS-codec…) | `pipeline_tag`, tags, mô tả kiến trúc | Tên "0.6B" chưa chắc gồm encoder/projector |
| 2 | **Ngôn ngữ** có `vi`? Mức hỗ trợ ("out-of-box" hay "cần fine-tune")? | `language`, bảng tier | Có trong tokenizer ≠ có chất lượng. Nemotron 3.5 xếp vi-VN vào nhóm *transcription-ready* (**Reported**). Parakeet cũ/Canary/Voxtral/Audio8/SenseVoiceSmall… **không có vi** (thiết kế §5.4.2) |
| 3 | **Streaming kiểu nào** (native/buffered/turn-final)? Chunk, lookahead, cache | mô tả "streaming", config | "Hỗ trợ streaming qua WebSocket" ≠ causal encoder |
| 4 | **Input**: sample rate, mono, độ dài tối đa, định dạng | I/O section | 16 kHz mono là chuẩn; độ dài tối đa có thể bị GPU-memory giới hạn |
| 5 | **Output**: có PnC/ITN, timestamp, language tag? | I/O section | Tag/special token phải lọc (§9.6.3) |
| 6 | **Tài nguyên**: params, dtype phát hành, VRAM ở các runtime | card, repo, file size | Chưa gồm cache/KV/workspace (§9.9) |
| 7 | **Runtime & đóng gói**: NeMo/Transformers/ONNX/GGUF/CT2/vLLM; version tối thiểu | "Inference/Usage" | Yêu cầu phiên bản (ví dụ Transformers ≥ 5.13 cho Nemotron 3.5; **Reported**). GGUF không hoán đổi giữa runtime |
| 8 | **Benchmark**: tập nào? chuẩn hoá thế nào? streaming hay offline? chunk nào? | bảng kết quả, footnote | Xem §9.13 |
| 9 | **Dữ liệu train** và nhãn (synthetic? ensemble?) | "Training data" | Nhãn synthetic từ model khác có thể kế thừa lỗi (Nemotron dùng ensemble Canary/Parakeet/Whisper/FunASR; **Reported**) |
| 10 | **License & điều kiện thương mại** | frontmatter + file LICENSE | Card ≠ license thực; có model **CC-BY-NC-ND** (ZipFormer 30M) *loại khỏi dùng thương mại*, CTC 110M của ChunkFormer là NC (**Reported**) |

> **Nguyên tắc vàng:** mọi số trong card là **Reported** cho tới khi bạn tự đo trên *audio của bạn* (giọng vùng miền, kênh điện thoại 8 kHz, nhiễu nền, code-switch). Wiki ghi `stale_after` cho mọi con số benchmark vì chúng cũ rất nhanh.

---

## 9.13 Đọc benchmark đúng cách (trả lời Q6)

### 9.13.1 WER/CER

```text
WER = (S + D + I) / N      S: thay thế, D: xoá, I: chèn, N: số từ tham chiếu
```

- Ví dụ (**Reproduced**): tham chiếu "tôi muốn đặt vé đi hà nội" (7 âm tiết), giả thuyết "tôi muốn đạt vé đi hà nội ngày mai" → 1 thay thế + 2 chèn → WER = 3/7 ≈ **0.43**. Lưu ý WER có thể > 100%.
- **Tiếng Việt: "từ" là gì?** Chính tả tách theo *âm tiết*, nên nhiều hệ thống đếm WER theo âm tiết; nếu tính theo từ ghép (word segmentation) con số khác. **Phải xem tác giả tính theo đơn vị nào.**
- **CER** (character error rate) dùng cho tiếng Nhật/Hàn/Trung (Nemotron báo CER cho ja/ko/zh; **Reported**) và đôi khi bổ sung cho tiếng Việt khi lỗi dấu thanh là điểm chính.
- **WER không đo hết lỗi thanh điệu:** "ma/má/mà/mả/mã/mạ" khác nghĩa hoàn toàn nhưng chỉ là một lỗi thay thế như mọi lỗi khác. Một lỗi dấu có thể phá nghĩa nhưng chỉ tăng WER 1 từ. Hãy xem thêm lỗi **dấu thanh**, **số, tên riêng, phủ định** (Chương 21; thiết kế §5.4.3).

### 9.13.2 Chuẩn hoá trước khi chấm

Các card thường **chuẩn hoá cả tham chiếu lẫn giả thuyết**: hạ chữ thường, bỏ dấu câu, đổi số sang dạng đọc, v.v. (Gipformer: lowercase, bỏ dấu câu, số → dạng đọc; Nemotron: "normalization aligns casing, punctuation, numerals, formatting"; **Reported**). Hệ quả:

- Cùng một transcript, đổi normalizer có thể đổi WER vài điểm.
- Model xuất "23/9" và tham chiếu "hai mươi ba tháng chín" bị phạt oan nếu không có ITN/TN.
- **Không so con số giữa các card nếu normalizer khác nhau.**

### 9.13.3 Bẫy so sánh (rút ra từ thiết kế §5.4.2)

1. **Đừng đặt "Qwen 5.55" lên trước "Nemotron 12.29".** Hai con số khác giao thức (offline vs streaming, có LangID), khác chunk, và khác tập. (**Reported/Synthesis**)
2. **Đừng so VIVOS với FLEURS.** Khác tập (VIVOS: đọc ở phòng thu, sạch; FLEURS: đọc câu có sẵn) và khác normalizer.
3. **Đừng dùng số offline làm số streaming.** Ví dụ: WER của ChunkFormer *large long-form* không chuyển sang checkpoint *small streaming* (**Reported**).
4. **Đừng dùng số trung bình nhiều tập** (ví dụ "16.44% trung bình trên 3 tập vi" của Whisper large-v3) cho một tập cụ thể của bạn.
5. **Số TTFT/throughput công bố** phụ thuộc concurrency và loại input (§9.9.4).
6. **Số do chính tác giả báo cáo** (ví dụ "tốt nhất 9/12 benchmark" của Gipformer, nhiều tập là private) chưa có đối chứng độc lập.
7. **Tập test có thể bị rò vào train** (contamination), nhất là với dữ liệu web lớn.
8. **Domain gap:** tập sạch/đọc khác xa hội thoại thật có nhiễu, cắt ngang, ngập ngừng, "ờ, ừm". Voice agent cần tập *giống traffic thật* (Chương 21).

---

## 9.14 Lỗi thường gặp (và cách nhận ra)

| Triệu chứng | Nguyên nhân gốc | Gợi ý xử lý |
|---|---|---|
| ASR trả tiếng Anh/ngôn ngữ lạ cho tiếng Việt | Không đặt language; mặc định `en-US`/tự detect trên clip ngắn | Đặt `vi`/`vi-VN` tường minh; kiểm tra tag auto |
| Câu "hãy đăng ký kênh…" xuất hiện khi im lặng | Whisper hallucination | VAD lọc trước, `condition_on_previous_text=False`, ngưỡng `no_speech`, loại segment nghi ngờ |
| Một số lượt trễ gấp nhiều lần | Temperature fallback / beam lớn | `temperature=0`, beam nhỏ |
| WER tốt trên card, tệ ở production | Domain gap, kênh 8 kHz, sai normalizer | Đo trên traffic thật; kiểm preprocessor khớp train (Chương 4) |
| Streaming "chạy" nhưng trễ hàng giây | Buffered mà tưởng cache-aware; commit policy chờ | Đọc kỹ cơ chế; đo stable-text latency |
| Lệch/nhảy chữ sau barge-in | Quên reset cache/state, mất chunk | Quản lý state theo session; reset khi huỷ |
| OOM khi tăng phiên | Bỏ qua KV/encoder cache, workspace | Tính theo §9.9; giới hạn `max_streams` |
| Latency p95 lúc đầu rất xấu | Không warmup | Warmup khi khởi động; loại khỏi số đo |
| WER lượng tử hoá tăng | int4 quá tay / lớp nhạy | Giữ fp16 cho lớp nhạy; A/B trên tập riêng |
| Token lạ vào TTS (`<vi-VN>`…) | Chưa lọc special token | Bước lọc/normalize giữa ASR→LLM→TTS |
| Dùng nhầm GGUF của runtime khác | Layout/tokenizer khác | Dùng đúng runtime; kiểm parity |
| `<unk>` xuất hiện nhiều | NFC/NFD khác, ký tự ngoài vocab | Chuẩn hoá Unicode trước tokenizer |

---

## 9.15 Bài tập

1. **Tính frame.** Encoder FastConformer 8×. Một câu nói 4.2 s ở 100 fps log-mel có bao nhiêu frame trước và sau encoder? Với chunk 320 ms, cần xử lý bao nhiêu chunk?
2. **CTC decode tay.** Cho chuỗi frame `x x _ y y y _ _ z z _ z` với blank `_`, cho ra gì? Nếu bỏ blank giữa hai `z` thì sao?
3. **VRAM.** Bạn dùng GPU 12 GB, chạy Whisper turbo `int8_float16`, VieNeu GPU, và LLM 4B 4-bit (thiết kế §9.2). Ước lượng weights từng thành phần (dùng bảng §9.9.1, nhớ rằng "4-bit" ≈ 0.5 byte/param) rồi nêu ít nhất 4 thành phần *không* nằm trong con số weights.
4. **KV cache.** LLM 32 lớp, 8 đầu KV (GQA), head_dim 128, ngữ cảnh 2048, bf16, 12 phiên. Tính KV (GiB). Nếu dùng MHA 32 đầu KV thì sao?
5. **Chọn họ.** Hệ thống A cần partial hiển thị ngay, nhiều phiên; hệ thống B cần transcript cuối chính xác nhất cho call-center. Chọn họ (§9.3) và giải thích.
6. **Đọc card.** Lấy [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md). Điền bảng 10 bước ở §9.12. Nêu 3 điều phải tự kiểm trước khi đưa vào production tiếng Việt.
7. **Benchmark.** Hai card: Model X "WER 6.0 trên LibriSpeech", Model Y "WER 12 trên FLEURS-vi". Nêu ít nhất 4 lý do không so sánh trực tiếp.
8. **WER tay.** Tham chiếu: "cho tôi hai vé đi đà nẵng". Giả thuyết: "cho tôi hai vé đi đà lạt". Tính WER theo âm tiết. Lỗi này nặng hơn WER cho thấy ở điểm nào?
9. **Hallucination.** Giải thích bằng ngôn ngữ của §9.3 vì sao decoder tự do dễ hallucinate hơn CTC; đề xuất 3 lớp phòng thủ.
10. **(Nâng cao)** Vì sao chunk lớn hơn thì WER thấp hơn trong model cache-aware? Liên hệ với right context và non-causal attention.

## 9.16 Đáp án

**Q1.** *CTC:* mỗi frame một nhãn + blank, độc lập có điều kiện, rất nhanh, streaming tự nhiên nếu encoder causal/chunked. *Transducer (RNN-T/TDT):* thêm prediction network + joint, quyết định từng bước token/blank (TDT thêm duration), chính xác hơn CTC, **streaming tự nhiên tốt nhất**. *AED (Whisper):* encoder non-causal trên cửa sổ 30 s + decoder autoregressive với cross-attention; mạnh và đa dụng nhưng **không streaming tự nhiên** và dễ hallucinate. *LLM-based:* audio encoder + projector + LLM; mạnh ở ngữ cảnh, nặng, streaming qua chunk+commit.

**Q2.** Cache-aware streaming: encoder lưu state (attention K/V, đuôi conv) cho từng lớp giữa các chunk, nên mỗi audio chỉ được tính một lần. *Buffered streaming:* đưa lại cả cửa sổ chồng lấp vào model offline, tính lặp và cần chính sách commit prefix. Cache-aware: ít compute dư, nhiều phiên hơn, nhưng cần quản lý state theo session.

**Q3.** 0.6B × 2 byte (bf16) ≈ **1.2 GB** cho weights. Thêm: encoder cache theo phiên, KV cache (decoder/LLM), activation, workspace/CUDA context (thường vài trăm MB–hơn 1 GB), phân mảnh bộ nhớ, và các model khác chung GPU. Tên "0.6B" có thể chưa tính hết encoder/projector.

**Q4.** CTC chỉ chọn nhãn theo từng frame và có blank nên trên im lặng thường ra blank → rỗng. Decoder AED/LLM là model ngôn ngữ tự do, khi encoder không đưa ra bằng chứng rõ thì nó "điền" chuỗi quen thuộc từ dữ liệu train (YouTube outro). Cửa sổ 30 s pad dài cũng cho nó nhiều chỗ để sinh.

**Q5.** Chunk 80 ms là *nhịp cập nhật*. Độ trễ thật còn gồm: chờ đủ chunk (đến ~1 chunk), lookahead, compute, scheduling/queue, transport, độ ổn định của chữ (revision) và commit policy; với turn-final còn có endpoint timeout. RTF < 1 cũng chỉ nói là theo kịp luồng.

**Q6.** Không. Khác tập (FLEURS vs khác), khác chế độ (offline vs streaming/chunk), khác normalizer, khác đơn vị đếm (âm tiết/từ), có thể khác LangID và concurrency; ngoài ra là số tự báo cáo, chưa tái lập.

**Bài 1.** 4.2 s × 100 = 420 frame; ÷8 = **52.5 → ~52–53 frame** (80 ms/frame, tuỳ padding). Chunk 320 ms = 4 frame ⇒ 52.5/4 ≈ **13–14 chunk**.

**Bài 2.** `x x _ y y y _ _ z z _ z` → gộp lặp: `x _ y _ z _ z` → bỏ blank: **`xyzz`**. Blank giữa hai `z` giữ lại hai chữ `z`; nếu bỏ blank đó (`z z z`) thì gộp lặp ra `xyz`.

**Bài 3.** Whisper turbo 809M int8: ~0.81 GB; LLM 4B 4-bit: ~2.0 GB; VieNeu: ~1–3 GB (thiết kế ghi 2–3 GB, peak 1.1 GB ở 16 streams; **Reported**). Thành phần ngoài weights: KV cache LLM (nhân số phiên), encoder/decoder state, activation, workspace CUDA, phân mảnh, cache của TTS codec/slot (`VIENEU_MAX_STREAMS`), vùng đệm audio.

**Bài 4.** KV = 2 × 32 × 8 × 128 × 2048 × 2 byte = 268 435 456 B ≈ **0.25 GiB/phiên** → 12 phiên ≈ **3.0 GiB**. Nếu MHA 32 đầu KV: ×4 → ≈ **1.0 GiB/phiên**, 12 phiên ≈ **12 GiB**.

**Bài 5.** A → transducer cache-aware (Nemotron-kiểu) ở chunk 160–320 ms. B → turn-final AED hoặc LLM-based (Whisper turbo/Qwen3-ASR/ChunkFormer RNNT), có thể two-pass với A. Kèm đánh giá riêng lỗi số/tên/phủ định.

**Bài 6.** (gợi ý) Họ: FastConformer-RNNT cache-aware + language-ID prompt; ngôn ngữ: vi-VN *transcription-ready*; streaming: native, chunk 80–1120 ms; I/O: mono wav, text có PnC, tag `<xx-XX>` khi auto; tài nguyên: 600M (bf16 ≈ 1.2 GB weights + cache); runtime: NeMo, NeMo-Speech.cpp Q8 GGUF, Transformers ≥ 5.13; benchmark: FLEURS WER 13.41→11.18; license OpenMDW-1.1; cần tự kiểm: (a) đặt `vi-VN` tường minh, (b) WER trên audio thực (vùng miền, nhiễu, 8 kHz), (c) độ trễ stable-text và hành vi cache sau barge-in, (d) Q8 GGUF parity và hiệu năng thực trên phần cứng của bạn.

**Bài 7.** Khác ngôn ngữ; khác độ khó tập (đọc sách tiếng Anh vs đọc câu đa ngôn ngữ); khác normalizer; khác chế độ streaming/offline; khác đơn vị tính; khác dữ liệu train/contamination; số tự báo cáo.

**Bài 8.** Một thay thế: "nẵng" → "lạt" → WER = 1/7 ≈ **0.14**. Lỗi này nặng vì đổi **địa danh** và do đó phá ý định/đặt vé sai nơi, nhưng WER chỉ coi như một lỗi bất kỳ.

**Bài 9.** AED/LLM sinh token theo xác suất có điều kiện bởi cả prefix đã sinh (language model), nên có thể "đi tiếp" kể cả khi audio không có bằng chứng; CTC buộc mỗi frame chọn nhãn từ bằng chứng âm học, mặc định blank. Ba lớp: (1) VAD/gating trước ASR (cắt im lặng), (2) tham số decode an toàn (`temperature=0`, `condition_on_previous_text=False`, `language="vi"`), (3) lọc sau (`no_speech_prob`, compression ratio, danh sách cụm hallucination, confidence thấp thì hỏi lại).

**Bài 10.** Chunk lớn = nhiều frame được xử lý cùng lúc với attention hai chiều *trong chunk* (và lookahead dài hơn), nên mỗi frame thấy nhiều ngữ cảnh tương lai hơn, gần với mô hình offline; đổi lại chờ đủ chunk nên độ trễ cao hơn. Lợi ích giảm dần (đường cong §9.5.3).

---

## 9.17 Tóm tắt chương

- Model ASR = **encoder** (nén thời gian + ngữ cảnh) + **cơ chế căn chỉnh** + **tokenizer**. Bốn họ: **CTC** (nhanh, ít hallucinate), **Transducer** (streaming tự nhiên, chính xác), **AED/Whisper** (mạnh, 30 s, dễ hallucinate), **LLM-based** (ngữ cảnh mạnh, nặng).
- **Frame của encoder** (40/80 ms) là đơn vị độ trễ nhỏ nhất. **Chunk** là nhịp cập nhật, **lookahead** là độ trễ bắt buộc; chunk lớn → WER thấp hơn, trễ cao hơn.
- **Cache-aware streaming** giữ state theo lớp và theo phiên để không tính lại audio; *buffered* và *turn-final* là hai thứ khác. Bọc WebSocket không làm model thành streaming.
- **Tokenizer** và **token đặc biệt** (language, task, tag, `<EOU>`) quyết định hành vi; đặt `vi`/`vi-VN` tường minh và lọc tag trước các tầng sau.
- **Decoding:** greedy/beam, tắt temperature fallback, `condition_on_previous_text=False`, cẩn thận LM fusion và hotword; biết model xuất dạng đọc hay viết.
- **Bộ nhớ:** weights = params × byte; thêm KV cache, encoder cache, activation, workspace, nhiều model chung GPU; warmup và loại khỏi số đo.
- **Lượng tử hoá:** fp16/bf16 → int8 (`int8_float16`) → int4; GGUF/ONNX/CT2 là các hệ đóng gói khác nhau, **không hoán đổi**; luôn đo lại WER.
- **Đọc benchmark:** WER phụ thuộc tập, normalizer, đơn vị, chế độ streaming, chunk, concurrency. RTF và RTFx ngược chiều; đọc định nghĩa trước khi so sánh.

**Chương tiếp theo:** Chương 10. VAD, endpointing và turn detection.

---

## Giới hạn và điểm chưa kiểm chứng

- Phần kiến trúc và thuật toán (CTC, RNN-T/TDT, AED, LLM-ASR, cache-aware, KV cache, lượng tử hoá, beam/temperature, LM fusion) là **kiến thức giáo trình**, không phải claim từ nguồn wiki; chi tiết hiện thực của từng model cụ thể (số lớp, hệ số subsampling, kernel, kích thước cache) cần xác nhận bằng config/model card.
- Giả định FastConformer **subsampling 8× (80 ms/frame)** để suy ra "chunk 80 ms = 1 frame" là **Synthesis**; wiki chỉ ghi chunk 80/160/320/560/1120 ms, không ghi hệ số subsampling.
- Các con số WER, throughput (~240–~2.400 stream), TTFT (92 ms/3210 ms), số tham số, license, yêu cầu phiên bản đều là **Reported** theo model card/wiki, **chưa chạy lại**; trang wiki mang `stale_after` (đa số tới 2027-10).
- Các phép tính ở §9.4, §9.9, §9.10 và ví dụ CTC/WER được chạy bằng script Python thuần (**Reproduced**); ví dụ KV cache dùng tham số **minh hoạ**, không phải của model cụ thể.
- Mô tả về họ TTS (§9.11) ở mức khái niệm; nhãn "ví dụ trong wiki" cho từng họ là gợi ý phân loại **Synthesis**, cần kiểm trong trang model tương ứng và Chương 13.
- Chưa có trong wiki: đo WER sau lượng tử hoá cho tiếng Việt, so sánh độ trễ stable-text giữa native streaming và buffered trên cùng dữ liệu, số đo hallucination giữa các họ.
- Wiki không có ví dụ code ML ở chương này; không có đoạn code chạy trong repo ngoài script tính toán nhỏ ở phụ lục.

## Phụ lục chương: script tính toán (Reproduced)

```python
# Bảng bộ nhớ weights (GB, 1e9 byte): params(tỉ) × byte/param
for p in (0.068, 0.12, 0.6, 0.809, 1.55, 1.7, 4, 7):
    print(p, [round(p*b, 2) for b in (4, 2, 1, 0.5)])   # fp32, bf16/fp16, int8, int4

# Frame rate sau subsampling
for ss in (4, 8): print(ss, 100/ss, "fps", 1000/(100/ss), "ms/frame")

# KV cache (GiB mỗi phiên)
def kv(L, kvh, hd, T, b=2): return 2*L*kvh*hd*T*b/2**30
print(kv(28, 8, 128, 4096), kv(32, 32, 128, 4096))      # ≈ 0.438, 2.0

# CTC collapse
def ctc(seq, blank="_"):
    out, prev = [], None
    for s in seq:
        if s != prev and s != blank: out.append(s)
        prev = s
    return "".join(out)
print(ctc("hh_ee_ll_llo"), ctc("hel_lo"), ctc("helo"))   # hello hello helo

# Whisper encoder frames / 30 s
print(30*100/2)                                          # 1500.0

# WER theo âm tiết (Levenshtein)
def wer(r, h):
    r, h = r.split(), h.split()
    d = [[0]*(len(h)+1) for _ in range(len(r)+1)]
    for i in range(len(r)+1): d[i][0] = i
    for j in range(len(h)+1): d[0][j] = j
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+(r[i-1] != h[j-1]))
    return d[-1][-1]/len(r)
print(wer("tôi muốn đặt vé đi hà nội", "tôi muốn đạt vé đi hà nội ngày mai"))  # 0.4286
```

---

[^design]: [Thiết kế pipeline speech-to-speech tiếng Việt](thiet-ke-pipeline-speech-to-speech-tieng-viet.md), §5.4.1 (ba nghĩa của "realtime"), §5.4.2 (shortlist, bẫy so sánh, loại khỏi shortlist), §5.4.3 (ba mẫu ghép ASR), §5.8 (deploy tools, quy ước RTF/RTFx), §6 (profile A–E), §9.2 (VRAM), §9.3 (scaling), §9.5 (privacy) (Reported/Synthesis).
[^nemotron]: [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md), các mục "Architecture and I/O", "Streaming operating points", "Vietnamese operating curve", "Inference and usage", "Training data and procedure" (Reported).
[^survey]: [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md) và [Phân nhóm ASR/STT và shortlist realtime](../wiki/realtime-asr-selection.md): phân nhóm theo kiến trúc, kích thước, streaming, license (Reported/Synthesis).
[^whisper]: [Whisper large-v3-turbo](../wiki/whisper-large-v3-turbo.md) (decoder 32→4 lớp, 809M vs 1550M; dữ liệu >5M giờ), [Faster-Whisper](../wiki/faster-whisper.md) (CTranslate2, int8, tới 4× nhanh hơn), [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md) (tham số decode, hallucination tiếng Việt) (Reported).
[^viasr]: [Gipformer 68M RNN-T](../wiki/gipformer-68m-rnnt.md), [ChunkFormer Vietnamese](../wiki/chunkformer-vietnamese.md), [ZipFormer 30M Vietnamese](../wiki/zipformer-30m-vietnamese.md), [Parakeet Realtime EOU 120M v1](../wiki/parakeet-realtime-eou-120m-v1.md) (Reported).
[^deploy]: [Audio.cpp GGUF packages](../wiki/audio-cpp-gguf-packages.md), [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md) (GGUF/ggml, Q8, runtime) (Reported).
