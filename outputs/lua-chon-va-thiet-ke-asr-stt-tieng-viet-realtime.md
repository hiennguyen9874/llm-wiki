# Lựa chọn và thiết kế ASR/STT realtime cho tiếng Việt

> **Loại tài liệu:** bài viết tổng hợp, là deliverable trong `outputs/`. Đây không phải tri thức canonical của wiki.
> **Ngày:** 2026-10-07.
> **Nguồn chính:** [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md), [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md), [Phân nhóm ASR/STT và shortlist realtime](../wiki/realtime-asr-selection.md).
> **Nguồn đọc thêm:** [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [Nemotron 3.5 ASR](../wiki/nemotron-3.5-asr-streaming-0.6b.md), [Qwen3-ASR family](../wiki/qwen3-asr-family.md), [PhoWhisper](../wiki/phowhisper.md), [ChunkFormer Vietnamese](../wiki/chunkformer-vietnamese.md), [ZipFormer 30M Vietnamese](../wiki/zipformer-30m-vietnamese.md), [WhisperLiveKit](../wiki/whisperlivekit.md), [Community-Reported Usable STT for Voice Agents](../wiki/community-usable-stt-voice-agents.md).
> **Phạm vi bằng chứng:** bài chỉ dùng các trang wiki đã compile. Không mở `raw/`, không cài đặt, không chạy model, không đo benchmark.
> - Mọi con số đều do vendor, tác giả hoặc report công bố (**Reported**).
> - Mọi đề xuất lựa chọn, cấu hình và kiến trúc là suy luận tổng hợp (**Synthesis**).
> - Chưa có bất kỳ benchmark tiếng Việt nào chạy trên cùng audio, cùng normalizer, cùng chunk và cùng phần cứng.

---

## 0. TL;DR

1. **Trước khi so sánh model, phải định nghĩa "realtime".** Có ba chế độ khác nhau:
   - **native/stateful streaming:** giữ cache, xử lý audio theo chunk;
   - **buffered/policy streaming:** chờ đủ context, có thể rollback rồi mới commit;
   - **turn-final:** chờ endpoint rồi decode cả lượt nói.

   RTF < 1 chỉ cho biết model theo kịp luồng audio. Nó không phải độ trễ người dùng cảm nhận.
2. **Shortlist tiếng Việt, theo thứ tự thử:**
   - [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md): native streaming, cần partial sớm. Thử chunk 160–320 ms trước.
   - [Qwen3-ASR](../wiki/qwen3-asr-family.md) 0.6B → 1.7B: ưu tiên chất lượng, chấp nhận buffering.
   - [Whisper large-v3-turbo](../wiki/whisper-large-v3-turbo.md) qua faster-whisper: baseline turn-final có runtime chín muồi nhất.
   - [ChunkFormer RNNT large 113M](../wiki/chunkformer-vietnamese.md) và [PhoWhisper](../wiki/phowhisper.md): ứng viên chuyên tiếng Việt cho final-pass.
3. **Thiết kế khuyến nghị:**
   - **single-pass:** đủ cho MVP và cho nhiều sản phẩm.
   - **two-pass selective:** Nemotron xuất partial, cuối lượt chạy Qwen3-ASR 1.7B hoặc ChunkFormer để ra final. Chỉ bật khi lỗi số, tên hay phủ định vượt ngưỡng chấp nhận.
   - Dù chọn kiểu nào, chỉ hành động trên **transcript đã commit**.
4. **Thứ tự lọc:** ngôn ngữ → chế độ realtime → license weights → runtime/phần cứng → đo trên dữ liệu thật. Không lọc bằng size hoặc leaderboard tiếng Anh.
5. **Các số liệu hiện có không so sánh trực tiếp được.**
   - Qwen 5.55 (FLEURS-vi, offline) và Nemotron 12.29 (FLEURS-vi, streaming 320 ms) khác protocol.
   - VIVOS, CMV và VLSP là các tập test khác nhau.

   Muốn quyết định thì phải tự benchmark (xem mục 10).

---

## 1. Nhãn bằng chứng dùng trong bài

| Nhãn | Ý nghĩa |
|---|---|
| **Reported** | Số liệu hoặc tuyên bố của nguồn, chưa tái lập |
| **Observed** | Đã kiểm tra tĩnh trên artifact, ví dụ trường license trong card |
| **Synthesis** | Suy luận của bài từ các nguồn đã dẫn |
| **Unverified** | Chưa có sự kiện kiểm chứng. Không đồng nghĩa với sai |

Trang [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md) và [realtime shortlist](../wiki/realtime-asr-selection.md) đang ở `status: draft`. Lý do: thiếu WER streaming tiếng Việt cùng điều kiện, thiếu phần cứng và SLA mục tiêu, và chưa có bằng chứng về checkpoint streaming nhỏ của ChunkFormer.

---

## 2. "Realtime" nghĩa là gì với ASR

### 2.1 Ba chế độ vận hành

| Chế độ | Cơ chế | Ví dụ trong wiki | Hệ quả thiết kế |
|---|---|---|---|
| **Native / stateful streaming** | Encoder (và decoder) giữ cache, chỉ xử lý audio mới không chồng lấp | Nemotron 3.5 / EN, Parakeet Realtime EOU, Voxtral Mini 4B Realtime, Audio8 Infinite, Confucius4-R2T2 (append-only) | Có partial sớm và latency cấu hình rõ. Chất lượng giảm khi chunk nhỏ |
| **Buffered / policy streaming** | Nhận audio liên tục, chờ đủ context, dùng stable-prefix hoặc rollback rồi mới commit | Qwen3-ASR (paper dùng chunk 2 s, fallback 5 token, giữ 4 chunk cuối chưa cố định), Whisper qua WhisperLiveKit SimulStreaming/LocalAgreement | Partial có thể bị sửa. Compute có thể phải recompute theo cửa sổ |
| **Turn-final** | VAD/endpoint cắt lượt, decode cả câu một lần | Whisper, PhoWhisper, ChunkFormer large, Cohere Transcribe, Fun-ASR-MLT, Parakeet TDT | Không có partial. Latency = endpoint + thời gian decode cả lượt |

Theo wiki, có hai điểm hay bị nhầm (**Synthesis**):

- WebSocket/SSE ở tầng API **không biến** một checkpoint thành causal encoder. Ví dụ, [Parakeet ASR Server](../wiki/parakeet-asr-server.md) upload toàn bộ audio rồi mới stream text ra.
- Đầu RNNT **không bảo đảm** encoder là streaming. IndicConformer và ZipFormer 30M có RNNT nhưng chưa có protocol streaming.

### 2.2 Các metric latency phải tách riêng

Một turn có các mốc thời gian sau:

```text
user bắt đầu nói ─► first partial ─► first STABLE text ─► ... ─► user ngừng nói
                                                                  └► endpoint commit ─► final transcript
```

| Metric | Đo gì | Không được nhầm với |
|---|---|---|
| RTF = compute / thời lượng audio | Model có theo kịp luồng không | Độ trễ cảm nhận |
| First partial | Lúc text đầu tiên xuất hiện | Text dùng được |
| **First stable text** | Lúc span đầu tiên không còn bị sửa | Chunk size của model |
| Partial revision rate / word lag | Mức "giật" của partial | WER |
| Endpoint → final (P50/P95) | Thời gian chờ sau khi user ngừng nói | TTFT của decoder trên audio có sẵn |
| Throughput / concurrency | Số phiên đồng thời ở mức latency mục tiêu | Throughput batch offline |

Latency thực tế cộng dồn từ chunk accumulation, lookahead, compute, scheduling/queue, transport và commit policy.[^vi-asr] Checklist cộng đồng còn nêu thêm một điểm (**Reported/Unverified**): *time-to-first-stable-token* và độ biến động của partial dự báo cảm giác "nhanh" tốt hơn WER.[^usable]

### 2.3 Những con số dễ bị đọc sai

- **Nemotron 3.5, chunk 80–1120 ms:** đây là kích thước chunk. Nó không phải first-stable-text hay endpoint→final.[^nemotron]
- **Qwen3-ASR, TTFT 92 ms:** đo cho model 0.6B ở concurrency 1, với audio dài khoảng 2 phút đã có sẵn, chạy vLLM 0.14 + CUDA Graph + BF16. Đây không phải độ trễ từ mic. Ở concurrency 128, TTFT là 3210/6195 ms (avg/P95) và throughput 2000 audio-giây/giây. Hai số này là hai operating point khác nhau.[^qwen]
- **NeMo-Speech.cpp, 27 ms CPU cho mỗi chunk 160 ms:** benchmark này đo trên **Nemotron EN**, không phải Nemotron 3.5 tiếng Việt.[^runtime]
- **ZipFormer 30M, 12 s audio trong 0.3 s trên CPU:** đây là throughput khi xử lý file, không phải độ trễ partial.[^zip]

---

## 3. Phân loại ASR theo kiến trúc

Wiki tổ chức ASR theo hai trục: **kiến trúc nhận dạng** và **cơ chế xuất transcript**. Kích thước, ngôn ngữ, endpointing, speaker attribution, runtime và license là các bộ lọc riêng.[^shortlist]

| Kiến trúc | Đại diện | Điểm mạnh | Chi phí/rủi ro cần đo |
|---|---|---|---|
| **Acoustic-first CTC / RNNT / TDT** (FastConformer, Conformer, ZipFormer) | Nemotron 3.5, Parakeet, ChunkFormer, ZipFormer, IndicConformer | Ít tham số, cache-aware streaming khi checkpoint hỗ trợ, phù hợp nhiều phiên, có tiềm năng chạy CPU | Lỗi ngôn ngữ/domain. License của checkpoint streaming. RNNT không tự bảo đảm streaming |
| **Encoder–decoder seq2seq** | Whisper, PhoWhisper, Distil-Whisper, Canary-1b-v2, Cohere Transcribe | Runtime chín muồi (CTranslate2, whisper.cpp), baseline dễ đối chiếu | Cửa sổ 30 s, partial phải recompute, hallucination khi gặp silence/nhạc, cần policy cho end-of-turn |
| **Audio encoder + LLM decoder** | Qwen3-ASR, Fun-ASR, Canary-Qwen, Voxtral, Audio8, ARK, Hojo, Higgs, Confucius4-R2T2 | Đa ngôn ngữ, prompt context/hotword, mạnh ở turn-final | Tài nguyên decoder + encoder, độ trễ do rollback/commit, rủi ro instruction-hallucination. Không phải LLM-ASR nào cũng streaming |
| **ASR kèm speaker attribution** | VibeVoice-ASR, MOSS-Transcribe-Diarize, Multitalker Parakeet | Trả lời được ai nói gì, lúc nào | Chủ yếu offline. Multitalker cần diarizer ngoài, mỗi speaker một instance |
| **Massive multilingual** | Omnilingual ASR (1600+), SeamlessM4T v2 | Phủ ngôn ngữ ít tài nguyên | Phải kiểm từng ngôn ngữ. Seamless là CC-BY-NC |

Bảng là **Synthesis**. Nó không khẳng định kiến trúc nào luôn chính xác hơn kiến trúc nào.[^vi-asr][^shortlist]

---

## 4. Kích thước, tài nguyên và cách ước lượng

### 4.1 Dải kích thước để thử (heuristic, Synthesis)

| Mục tiêu | Dải thử đầu | Ghi chú |
|---|---|---|
| CPU / edge | ~120M native streaming, hoặc 0.47–0.6B với runtime/quantization phù hợp | Với tiếng Việt: Nemotron 3.5 Q8 qua NeMo-Speech.cpp, ChunkFormer ONNX, Whisper CT2 INT8 (turn-final). Phải đo trên CPU đích |
| GPU dùng chung với LLM/TTS | 0.1–0.6B; ~0.8B cho Whisper Turbo | Đo contention và tổng bộ nhớ của cả pipeline |
| GPU riêng cho ASR, cần chất lượng tốt hơn | 0.6–1.7B | Chỉ nâng size khi mức giảm lỗi bù được latency/cost |
| Streaming LLM-ASR trên GPU riêng | ~4B | Voxtral Realtime cần GPU ≥16 GB BF16, nhưng **không hỗ trợ vi** |
| 7B+ | Chỉ khi có nhu cầu đặc thù | Không mặc định dùng cho voice agent |

[^shortlist]

### 4.2 Ước lượng trọng số

Công thức: `params × bytes/param`. Ở BF16: 0.6B ≈ 1.2 GB, 1.7B ≈ 3.4 GB, 4B ≈ 8 GB. Đây là **cận dưới chỉ tính weights**. Còn phải cộng encoder (khi tên model chỉ phản ánh decoder), KV/encoder cache theo từng phiên, workspace, allocator và runtime. Quantization cũng không bảo đảm tăng tốc.[^shortlist]

Tên kích thước dễ gây hiểu nhầm (**Reported**):

- **Qwen3-ASR "1.7B":** decoder Qwen3-1.7B + projector + encoder 300M. **"0.6B"**: decoder 0.6B + encoder 180M. Encoder AuT downsample 8x về 12.5 Hz, dynamic attention window 1–8 s.[^qwen]
- **Audio8-ASR-0.1B:** ~0.104B LM, nhưng ~0.324B tổng.[^shortlist]
- **Phonon-2 / Parakeet Redux:** model 0.6B được đóng gói chỉ còn 164 MB / 178 MB. Không được suy ra RAM peak từ kích thước file tải về.[^shortlist]

---

## 5. Bằng chứng tiếng Việt hiện có

### 5.1 Bảng tổng hợp

Mọi số là **Reported** và chưa tái lập. Đơn vị là WER %.

| Model | Size | Chế độ | FLEURS-vi | VIVOS | CMV-vi | VLSP2020 T1 / T2 | Khác | License weights |
|---|---|---|---:|---:|---:|---|---|---|
| Nemotron 3.5 ASR | 600M | Native streaming | 13.41 / 12.87 / 12.29 / 11.78 / 11.18 tại 80 / 160 / 320 / 560 / 1120 ms (LangID); auto 13.59 → 11.22 | — | — | — | — | OpenMDW-1.1 (card: ready for commercial use) |
| Qwen3-ASR-1.7B | ~1.7B + enc 300M | Offline (streaming vi chưa đo) | 5.55 | — | — | — | MLC-SLM-vi 14.92 | Apache-2.0 |
| Qwen3-ASR-0.6B | 0.6B + enc 180M | Offline | 8.52 | — | — | — | MLC-SLM-vi 17.67 | Apache-2.0 |
| ChunkFormer RNNT large | 113M, ~5000 h | Long-form / turn-final | — | 2.49 | 5.18 | 12.75 / 20.47 | — | CC-BY-4.0 |
| ChunkFormer CTC large | 110M, ~3000 h | Long-form / turn-final | — | 4.18 | 6.66 | 14.09 / 25.81 | — | **CC-BY-NC-4.0** |
| PhoWhisper large | 1.55B | Turn-final | — | 4.67 | 8.14 | 13.75 / 26.68 | — | BSD-3-Clause |
| PhoWhisper medium | 769M | Turn-final | — | 4.97 | 8.27 | 14.12 / 26.85 | — | BSD-3-Clause |
| PhoWhisper small | 244M | Turn-final | — | 6.33 | 11.08 | 15.93 / 32.96 | — | BSD-3-Clause |
| Whisper-large-v3 (bảng của ChunkFormer) | 1.55B | Turn-final | — | 8.81 | 15.45 | 20.41 / 68.61 | — | Apache-2.0 (card) |
| ZipFormer 30M | 30M, ~6000 h | Chưa có protocol streaming | — | — | — | 12.29 / — | VLSP2023 10.40/11.10; VLSP2025 7.97/8.10; GigaSpeech2 7.56 | **CC-BY-NC-ND-4.0** |
| Whisper large-v3-turbo | 809M | Turn-final / buffered | Chưa có số vi cùng điều kiện | — | — | — | — | MIT (card) |
| Fun-ASR-MLT-Nano | 800M | Turn-final | Có vi trong danh sách ngôn ngữ, không có điểm | — | — | — | Hotwords + ITN | Apache-2.0 |
| Cohere Transcribe 03-2026 | 2B | Turn-final | Có vi trong 14 ngôn ngữ; plot vi chưa inspect | — | — | — | Không có timestamps/diarization | Apache-2.0 |

[^vi-asr][^nemotron][^qwen][^chunk][^pho][^zip][^survey]

### 5.2 Những gì **không** được suy ra từ bảng

- **FLEURS, VIVOS, CMV, VLSP và MLC-SLM là các tập khác nhau.** WER còn phụ thuộc tokenizer và normalizer (số, chữ hoa, dấu câu). Không thể xếp hạng xuyên cột.[^vi-asr]
- **Qwen 5.55 < Nemotron 12.29 không chứng minh Qwen thắng ở cùng latency.** Số Qwen là offline, số Nemotron là streaming 320 ms có LangID.[^vi-asr]
- **Số của ChunkFormer large không áp dụng cho checkpoint small streaming** (`chunkformer-rnnt-small-vie-stream-dct`). Card của checkpoint này trả HTTP 401, nên size, license, WER và latency của nó đều chưa biết.[^chunk]
- **Bảng so sánh của ChunkFormer là do tác giả tự chạy.** Các cột API (Viettel/Google/FPT) không rõ version và ngày, không phải ranking hiện tại.[^chunk]
- **Khoảng cách streaming/offline của Qwen** (1.7B: 2.69 → 3.33; 0.6B: 3.48 → 4.40) chỉ đo trên LibriSpeech và FLEURS-en/zh, **không có tiếng Việt**.[^qwen]

### 5.3 Đường cong latency–accuracy của Nemotron tiếng Việt

```text
chunk (ms):   80     160    320    560    1120
WER LangID: 13.41  12.87  12.29  11.78  11.18
WER auto:   13.59  13.02  12.40  12.02  11.22
```

Hai đặc điểm (**Synthesis** từ số Reported):

- Đi từ 80 ms lên 1120 ms giảm khoảng 2.2 điểm WER. Bước 160 → 320 ms rẻ về latency mà vẫn được ~0.6 điểm.
- Auto-detect chỉ phạt nhẹ với tiếng Việt (≤ 0.24 điểm). Dù vậy, trong production nên đặt `vi-VN` tường minh, vì pipeline Transformers mặc định prompt `en-US`.[^nemotron]

---

## 6. Hồ sơ từng ứng viên

### 6.1 Nemotron 3.5 ASR Streaming 0.6B: native streaming đầu tiên nên thử

- **Kiến trúc:** FastConformer cache-aware 24 lớp + RNNT. Language-ID được đưa vào bằng one-hot 128 chiều, concat với embedding 1024 chiều. Cache được giữ cho mọi lớp self-attention và convolution.[^nemotron]
- **Tiếng Việt:** `vi-VN` thuộc tier *transcription-ready*. Model có punctuation và capitalization native.[^nemotron]
- **Tham số streaming (NeMo `att_context_size`, frame 80 ms, left context 56):**

  | `att_context_size` | Chunk |
  |---|---|
  | `[56, 0]` | 80 ms |
  | `[56, 1]` | 160 ms |
  | `[56, 3]` | 320 ms |
  | `[56, 6]` | 560 ms |
  | `[56, 13]` | 1120 ms |

- **Runtime:**
  - NeMo cache-aware streaming script (`target_lang=vi-VN`, `att_context_size`, `strip_lang_tags`);
  - [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md) với Q8 GGUF (CLI, HTTP/WebSocket, C SDK);
  - Transformers ≥ 5.13 (`set_num_lookahead_tokens`, `language` cho từng chunk).[^nemotron][^runtime]
- **Throughput (H100, Reported):** khoảng 240 stream ở 80 ms và khoảng 2400 stream ở 1.12 s. Phải đo lại cho tiếng Việt và phần cứng đích.[^nemotron]
- **Rủi ro:**
  - Lỗi WER ~12% trên FLEURS là đáng kể cho tên, số và phủ định.
  - License OpenMDW-1.1 cần legal review.
  - Runtime Apache-2.0 không thay thế license của weights.[^vi-asr]

### 6.2 Qwen3-ASR 0.6B / 1.7B: ưu tiên chất lượng

- **Điểm mạnh:** FLEURS-vi offline tốt nhất trong các số có được (5.55 / 8.52). Có LID 97.9% (1.7B). Hỗ trợ prompt context/hotword (`prompt="Vocabulary: ..."`), ép ngôn ngữ, và fine-tune qua `-hf`.[^qwen]
- **Streaming:**
  - Toolkit gốc chỉ stream trên vLLM, không có batch và không có timestamps.
  - WhisperLiveKit có backend `qwen3-streaming` (windowed, mặc định 12 s left context, bắt buộc `--language` vì auto-detect đổi giữa chừng với giọng có accent; khuyến nghị **một phiên realtime mỗi GPU**).
  - Bản causal `qfuxa/qwen3-asr-0.6b-streaming` **chỉ hỗ trợ tiếng Anh**, nên không dùng cho tiếng Việt.[^wlk]
- **Timestamps:** Qwen3-ForcedAligner chỉ có 11 ngôn ngữ và **không có vi**.[^qwen]
- **Rủi ro:** commit lag do rollback, tài nguyên encoder/decoder/cache, và rủi ro hallucination kiểu instruction. Cộng đồng có ý kiến trái chiều: Qwen ít hallucinate nhưng stream kém hơn Parakeet (**Reported/Unverified**).[^survey]

### 6.3 Whisper large-v3-turbo: baseline turn-final

- **Model:** 809M, decoder rút từ 32 xuống 4 lớp. Không phải native streaming. License MIT theo card.[^survey]
- **Runtime:** faster-whisper (CTranslate2, fp16 / `int8_float16`). Live caption đi qua WhisperLiveKit SimulStreaming (AlignAtt) hoặc LocalAgreement.[^wlk]
- **Cấu hình chống hallucination cho tiếng Việt (Reported, từ [Whisper Hallucination Mitigation](../wiki/whisper-hallucination-mitigation.md) qua pipeline design):**

  ```python
  segments, info = model.transcribe(
      turn_audio,                      # audio đã được VAD/endpoint cắt thành một lượt
      language="vi",                   # không auto-detect trên clip ngắn, ồn
      beam_size=1,                     # 3 chính xác hơn nhưng chậm hơn ~30–50%
      temperature=0.0,
      condition_on_previous_text=False,
      vad_filter=True,
      vad_parameters={"min_silence_duration_ms": 500},
      no_speech_threshold=0.6,
      log_prob_threshold=-1.0,
      compression_ratio_threshold=2.4,
      hotwords="<tên riêng/thuật ngữ domain>",  # ngắn; KHÔNG đưa "cảm ơn đã xem"
  )
  segments = list(segments)   # materialize trong worker thread, không lặp trên event loop
  ```

  Sau khi decode, lọc tiếp:
  - bỏ segment có `no_speech_prob > 0.6` **và** `avg_logprob < -1.0`;
  - bỏ cả turn nếu `compression_ratio > 2.4`;
  - dùng regex blacklist cho các câu "ma" của YouTube (`đăng ký kênh`, `cảm ơn đã xem`, ...).

  Blacklist chỉ là một tín hiệu, cần kết hợp với bằng chứng âm học. Người dùng có thể nói thật "không" hoặc "dừng", nên luật "<2 từ" phải tune trên dữ liệu thật (**Synthesis**).[^pipeline]
- **Trigger thay thế (Reported):** WER tiếng Việt có nhiễu vượt khoảng 15%, hallucination vẫn lọt qua filter, hoặc cần partial.[^pipeline]

### 6.4 PhoWhisper: Whisper chuyên Việt

- Finetune multilingual Whisper trên 844 giờ, có 5 size (39M–1.55B), BSD-3-Clause.[^pho]
- Mức giảm WER từ medium (769M) lên large (1.55B) nhỏ (VIVOS 4.97 → 4.67). Nên thử **medium trước**.[^pho]
- Đường CTranslate2/faster-whisper cần conversion và test parity riêng. Chưa có bằng chứng về stable partial (**Synthesis**).[^pho]

### 6.5 ChunkFormer Vietnamese: acoustic-first chuyên Việt

- Masked chunk-wise Conformer + CTC/RNNT. **RNNT large 113M** có số tác giả tốt nhất trên VIVOS/CMV/VLSP và license CC-BY-4.0. Bản CTC là NC.[^chunk]
- **ONNX:**
  - Export full-context và streaming là hai đường riêng.
  - `OnnxAsrModel.stream()` → `StreamingSession` giữ cache attention/conv và trạng thái LSTM của RNNT; dùng `push_waveform` / `push_features` / `finalize`.
  - Chỉ hỗ trợ greedy CTC/RNNT. Không có beam search hay attention rescoring.[^chunk]
- **Cấu hình streaming phải thuộc `dynamic_chunk_sizes` đã huấn luyện.** Không được tự giảm right context của bản large rồi coi như đã có model streaming.[^chunk]
- **Vai trò đề xuất:** final-pass chuyên Việt có chi phí thấp. Chỉ dùng làm streaming sau khi qua gate về availability, license và latency của checkpoint small.[^vi-asr]

### 6.6 Các ứng viên phụ

- **Fun-ASR-MLT-Nano 800M:** có vi, hotwords và ITN, Apache-2.0. Là challenger turn-final. Không nhầm với Fun-ASR-Nano (zh/en/ja) hay SenseVoiceSmall của WLK.[^vi-asr]
- **Cohere Transcribe 2B:** challenger final-pass. Không có timestamps/diarization, code-switch không ổn định, cần VAD.[^vi-asr]
- **ZipFormer 30M:** rất nhẹ cho CPU, nhưng **CC-BY-NC-ND** và chưa có protocol streaming. Chỉ dùng cho nghiên cứu.[^zip]
- **MOSS-Transcribe-Diarize 0.9B:** có vi trong danh sách challenge, nhưng là offline long-form. Phù hợp review meeting, không phù hợp agent.[^vi-asr]

### 6.7 Loại khỏi shortlist tiếng Việt

Danh sách ngôn ngữ đã compile **không có vi** cho các model sau:

- Parakeet 25-European và các derivative (Phonon, Redux, Ultra, Orukeet);
- Canary;
- Voxtral (13 ngôn ngữ, và 8);
- Audio8 Infinite (zh/en), Audio8 0.1B;
- SenseVoiceSmall, GLM-ASR, Hojo, ARK;
- VibeVoice-ASR-Streaming (10 ngôn ngữ);
- Granite TurboCTC, Distil-Large-v3.5, Parakeet EOU (chỉ tiếng Anh).

Confucius4-R2T2 chưa có bằng chứng tường minh cho vi. Điều đó chưa có nghĩa là không hỗ trợ, chỉ là chưa đủ để khuyến nghị. Omnilingual (1600+) chưa kiểm kết quả theo từng ngôn ngữ. SeamlessM4T v2 có vi nhưng là non-commercial và chưa có bằng chứng streaming. **Không suy ra hỗ trợ tiếng Việt từ parent encoder hoặc từ chữ "multilingual".**[^vi-asr][^survey]

---

## 7. Thiết kế hệ thống ASR

### 7.1 Vị trí của ASR trong pipeline

```text
Client mic + AEC ─► gateway (per-session) ─► resample 16 kHz mono, ring buffer
   ├─► [denoise nhẹ, tùy chọn] ─► Silero VAD ─► Smart Turn + timeout ─► endpoint/barge-in
   ├─► audio AEC gốc (không enhance) ─► ASR streaming state  ─► partial/stable
   └─► turn audio buffer ─────────────► final recognizer (tùy chọn) ─► final
                         ─► transcript revisions + validity gate ─► COMMITTED turn ─► LLM
```

Nguyên tắc (**Synthesis**):[^pipeline][^noise]

1. **ASR nghe audio đã qua AEC nhưng chưa denoise.** Bằng chứng về denoise-trước-ASR đang mâu thuẫn: có nguồn báo giúp, có nguồn ("When De-noising Hurts") báo hại. Chỉ denoise nhánh VAD/barge-in, rồi A/B ở SNR 0/5/10/20 dB.
2. **Mỗi session có state ASR/VAD riêng.** Không chia sẻ cache giữa người dùng. Giải phóng cache khi session đóng.
3. **Chỉ một owner quyết định turn commit**, là gateway hoặc tracker của framework. ASR server chỉ cung cấp tín hiệu.
4. **Telephony 8 kHz:** decode đúng rồi resample lên 16 kHz. Upsample không khôi phục được thông tin đã mất, nên phải có tập test 8 kHz riêng.
5. **Giữ pre-roll 200–300 ms** trước điểm VAD bắt đầu, để không mất phụ âm đầu và thanh điệu (**Synthesis**, chưa đo).

### 7.2 Bốn mẫu ghép ASR

| Mẫu | Mô tả | Khi nào chọn | Chi phí |
|---|---|---|---|
| **A. Single-pass turn-final** | VAD/turn cắt lượt → Whisper turbo / Qwen3-ASR / PhoWhisper / ChunkFormer large | MVP, không cần caption live | Không có partial. Latency = endpoint + decode |
| **B. Single-pass native streaming** | Nemotron 3.5 chunk 160–320 ms | Cần partial sớm, caption, speculative LLM | Accuracy thấp hơn Qwen offline (khác protocol) |
| **C. Single-pass buffered** | Qwen3-ASR qua vLLM streaming hoặc WLK windowed; Whisper qua WLK | Muốn chất lượng LLM-ASR mà vẫn có live text | Rollback/commit lag. Một phiên mỗi GPU với WLK windowed |
| **D. Two-pass selective** | Nemotron cho partial; cuối lượt Qwen3-ASR 1.7B hoặc ChunkFormer RNNT large chạy lại trên turn audio để ra final | Số/tên/phủ định cần độ chính xác cao hơn B/C | Thêm compute và lag. Phải reconcile revision |

Không triển khai D ngay từ đầu nếu B hoặc C đã đạt accuracy domain. D có thể chỉ bật cho *critical spans* hoặc cho lượt có confidence thấp. **Final recognizer không phải ground truth** (**Synthesis**).[^vi-asr][^pipeline]

### 7.3 Mô hình transcript revision

Đây là schema đề xuất (**Synthesis**), không phải event schema của vendor nào:

```text
asr.partial(session_id, turn_id, revision, text, stable_prefix?)   # caption, speculation
asr.final  (session_id, turn_id, revision, text, model_id, language, quality_flags)
turn.commit(session_id, turn_id, revision)                         # một lần duy nhất
```

Quy tắc:

- **Partial** dùng cho caption và cho compute speculative (prefetch LLM). **Không được gây side effect.** Nếu revision đổi, hủy speculation.
- **Stable prefix** không phải confidence, cũng không phải final.
- **Final-pass** chạy lại trên turn audio đã giữ. Nó thay một revision chứ không ghép vào partial stream, để tránh token bị lặp.
- **Confidence** giữa các model không được calibrate với nhau. Thiếu confidence thì ghi là `unknown`. Cộng đồng báo rằng confidence không đổi ngay cả khi accuracy sụp ở ngôn ngữ ít tài nguyên (**Reported/Unverified**).[^usable]
- **Action-bearing spans** (số tiền, số điện thoại, ngày, tên, phủ định "không hủy"/"hủy") phải chờ final đã commit, hoặc có read-back/xác nhận lại. Một lỗi kiểu "don't cancel" → "do cancel" là thất bại hoàn toàn dù WER rất thấp. Khi người dùng sửa ("không, 4 chứ không phải 5"), giá trị mới phải thay giá trị cũ ở mọi tool call, field và summary đang chờ (**Reported**).[^usable]

### 7.4 Vòng điều khiển minh họa

Pseudo-code này là **Synthesis**, chưa chạy:

```python
async def on_audio_frame(sess, frame):
    sess.ring.append(frame)
    vad = sess.vad.step(denoise_opt(frame))            # nhánh VAD
    if sess.mode in ("native", "buffered"):
        for ev in sess.asr_stream.push(frame):          # audio AEC gốc
            emit("asr.partial", sess, ev.text, ev.stable_prefix)
            maybe_speculate(sess, ev)                   # không side effect
    if sess.endpoint.update(vad, sess.turn_detector):   # Smart Turn + timeout
        turn_audio = sess.ring.cut_turn(pre_roll_ms=250)
        text = await finalize(sess, turn_audio)         # flush stream và/hoặc final-pass
        if passes_validity_gate(text, sess):            # confidence, hallucination, entity
            emit("turn.commit", sess, text)
        else:
            emit("ask_back", sess)                      # hỏi lại, không đoán

async def finalize(sess, audio):
    partial_final = sess.asr_stream.finalize() if sess.asr_stream else None
    if sess.two_pass and needs_recheck(partial_final):  # critical span / low conf
        return await to_thread(final_model.transcribe, audio, language="vi")
    return partial_final or await to_thread(turn_model.transcribe, audio, language="vi")
```

### 7.5 Endpointing: phần quyết định latency mà người dùng cảm nhận

ASR latency thường bị che bởi thời gian chờ endpoint. Các điểm khởi đầu dưới đây cần tune, **Reported** từ các trang control:[^pipeline][^turn]

| Policy | Điểm bắt đầu |
|---|---|
| Silero VAD | Cửa sổ 512 sample / 32 ms @16 kHz, `threshold` 0.5 (0.6–0.7 khi ồn), `min_silence_duration_ms` 200–300, `speech_pad_ms` 100–200 |
| Có semantic turn (Smart Turn v3) | Im lặng 200–300 ms, sau đó classifier chạy trên 8 s audio cuối. Tiếng Việt: accuracy 81.27%, FP 14.84% (vendor, ~1000 mẫu, qua AI report) |
| Không có semantic turn | Im lặng 500–800 ms |
| Fallback | 1.2–1.5 s im lặng là trần chờ |
| Nemotron | Chunk 160/320 ms, ép `vi-VN` |

Bẫy cần tránh: endpoint quá gắt sẽ "nuốt" các từ ngắn, năng lượng thấp như "không" hay "đừng". Đây chính là những token quan trọng nhất trong luồng hủy hoặc sửa (**Reported**, cộng đồng).[^usable] LiveKit turn detector **không có vi**. [Parakeet EOU](../wiki/parakeet-realtime-eou-120m-v1.md) chỉ hỗ trợ tiếng Anh, nên không dùng EOU tiếng Anh để tuyên bố endpoint tiếng Việt.[^vi-asr][^turn]

### 7.6 Hotwords, context và chuẩn hóa

- **Context biasing:**
  - Qwen3-ASR dùng `prompt` tự do;
  - Fun-ASR dùng `hotwords` và ITN;
  - Whisper dùng `hotwords` hoặc `initial_prompt` ngắn;
  - WLK dùng tham số `context` cho Whisper và SimulStreaming.

  Nemotron và ChunkFormer, trong các trang đã compile, không có cơ chế hotword được mô tả (**Reported/Synthesis**).[^qwen][^survey][^wlk]
- **ITN / chuẩn hóa:** output ASR là dạng nói hoặc dạng viết tùy model. Nemotron có punctuation và capitalization, còn ChunkFormer/PhoWhisper thì card chuẩn hóa thủ công khi tính WER. Phải có một bước chuẩn hóa tiếng Việt thống nhất trước khi so sánh model hay trích entity: Unicode NFC, vị trí dấu thanh, số ↔ chữ, tiền, ngày (**Synthesis**).
- **Code-switch** Việt–Anh, tên thương hiệu, địa chỉ: phải có trong tập test, vì không model nào có số đo riêng cho trường hợp này.

---

## 8. Runtime và triển khai

### 8.1 Chọn runtime theo model

| Model | Runtime đề xuất | Lưu ý |
|---|---|---|
| Nemotron 3.5 | NeMo cache-aware script (tham chiếu); NeMo-Speech.cpp Q8 GGUF cho CPU/GPU (HTTP/WS, C SDK); Transformers ≥5.13 | Benchmark CPU 27 ms/chunk là của model EN. Phải đo lại 3.5 vi. Ép `vi-VN` |
| Qwen3-ASR | `qwen-asr` + vLLM (`qwen-asr-serve`); WLK `qwen3-streaming` windowed (`--language vi`); SGLang-Omni chỉ qua HTTP `/v1/audio/transcriptions` | Pin version và môi trường (vLLM xung đột `cu129` trong WLK). Đo cache và concurrency thật |
| Whisper turbo / PhoWhisper | faster-whisper (CTranslate2) cho final; WLK SimulStreaming/LocalAgreement cho live | Không cắt audio mỗi 200 ms một cách độc lập rồi coi là transcript ổn định. Mỗi luồng chỉ có một segmentation owner |
| ChunkFormer | ONNX Runtime CPU/GPU, session state riêng | Dùng checkpoint streaming-trained với cấu hình chunk đã huấn luyện |
| ZipFormer 30M | sherpa-onnx | Chỉ nghiên cứu (NC-ND) |

[^vi-asr][^runtime][^wlk][^deploy]

**GGUF là container, không bảo đảm thay thế được cho nhau.** Ví dụ, layout tensor của NeMo-Speech.cpp khác layout của transcribe.cpp/Handy. Phải chọn artifact khớp với runtime trước khi so sánh quantization hay tốc độ. License MIT/Apache của runtime **không thay thế** license của weights (**Synthesis**).[^shortlist][^survey]

### 8.2 Topology và capacity

- **Một model owner cho mỗi process.** Gateway workers không tự load weights. Tách environment ASR, TTS và ONNX để tránh xung đột torch/transformers/CUDA.[^pipeline]
- **Tách pool:** streaming ASR (nhạy latency) tách khỏi final-pass/turn-final (có thể batch, ví dụ `BatchedInferencePipeline` của faster-whisper). Ưu tiên nhịp audio hơn throughput batch.[^pipeline]
- **GPU dùng chung với LLM/TTS:** thử 0.6B trước. Muốn chạy Qwen 1.7B thì phải chừa chỗ cho encoder, cache, workspace và contention.[^vi-asr]
- **Admission control:** đặt giới hạn số phiên, hàng đợi có giới hạn, backpressure/429, deadline theo phiên. Warmup xong mới báo readiness.
- **VRAM tham khảo (Reported từ AI report, chưa đo):** Whisper turbo fp16 khoảng 2–3 GB. Trên GPU 12 GB thì dùng `int8_float16`.[^pipeline]

### 8.3 License: hard gate trước khi xét chất lượng

| Dùng thương mại được (đọc từ card, không phải tư vấn pháp lý) | Cần review | Tránh dùng thương mại |
|---|---|---|
| Qwen3-ASR (Apache-2.0), Whisper (MIT/Apache theo card), PhoWhisper (BSD-3), ChunkFormer RNNT large (CC-BY-4.0), Fun-ASR-MLT, Cohere (Apache-2.0) | Nemotron 3.5 (OpenMDW-1.1, card ghi ready for commercial use), Confucius4-R2T2 weights (NetEase license) | ChunkFormer CTC (CC-BY-NC), ZipFormer 30M (CC-BY-NC-ND), SeamlessM4T v2 (CC-BY-NC), Audio8 0.1B (CC-BY-NC) |

[^survey][^vi-asr][^chunk][^zip]

---

## 9. Cây quyết định gợi ý (Synthesis)

```text
Cần text khi user đang nói (caption, speculative LLM, barge-in thông minh)?
├─ Không ─► Mẫu A (turn-final)
│           ├─ GPU có sẵn, muốn ít tích hợp nhất ─► Whisper turbo `vi` + faster-whisper + filter
│           ├─ Ưu tiên chất lượng tiếng Việt      ─► Qwen3-ASR 0.6B → 1.7B (vLLM)
│           └─ Muốn chuyên Việt, nhẹ, license mở  ─► ChunkFormer RNNT large (ONNX) / PhoWhisper medium
└─ Có ─► Chỉ chạy CPU/edge?
         ├─ Có ─► Nemotron 3.5 Q8 qua NeMo-Speech.cpp (đo lại!) ; fallback Whisper CT2 INT8 turn-final
         └─ Không ─► Mẫu B: Nemotron 3.5, chunk 160 → 320 → 560 ms
                     └─ Lỗi số/tên/phủ định vẫn quá cao?
                        ├─ Chấp nhận buffering ─► Mẫu C: Qwen3-ASR streaming (vLLM / WLK windowed)
                        └─ Cần cả partial sớm lẫn final tốt ─► Mẫu D: Nemotron + final-pass Qwen 1.7B / ChunkFormer
Mọi nhánh: lọc license weights trước; ép language = vi; chỉ hành động trên transcript đã commit.
```

---

## 10. Quy trình benchmark đề xuất

Mọi quyết định production phải dựa vào bước này, vì wiki chưa có số đo tiếng Việt cùng điều kiện (**Synthesis**).[^vi-asr][^usable][^pipeline]

### 10.1 Corpus holdout tiếng Việt

- **Giọng:** Bắc, Trung, Nam. Có người già/trẻ em nếu domain cần.
- **Nội dung:** tên riêng, tên domain, địa chỉ, số tiền, số điện thoại, ngày giờ, phủ định ("không", "đừng hủy"), code-switch Việt–Anh, lệnh rất ngắn.
- **Kênh:** mic 16 kHz, telephony 8 kHz, far-field.
- **Nhiễu:** quán café, xe máy, TV nền ở SNR 0/5/10/20 dB, chạy cả có và không có denoise. Thêm đoạn chỉ có silence hoặc nhạc để đo hallucination.
- **Quyền riêng tư:** dữ liệu phải opt-in, có access control và retention policy.

### 10.2 Chuẩn hóa và chấm điểm

- Dùng cùng ground truth và cùng normalizer cho mọi model: NFC, dấu thanh, số, punctuation.
- Báo WER/CER, kèm **exact-match accuracy riêng** cho số, tên và phủ định. Không để normalizer che mất lỗi nghiêm trọng.
- Chạy mỗi model ở **đúng chế độ dự kiến dùng**: Nemotron ở 160/320/560 ms, Qwen ở policy buffered thật, Whisper per-turn.

### 10.3 Metric latency và tải

| Nhóm | Metric |
|---|---|
| Live | first partial, **first stable text**, partial revision rate, word lag |
| Cuối lượt | endpoint → final P50/P95 |
| Tài nguyên | RTF, peak memory/session, cold vs warm |
| Tải | concurrency 1/4/8/16, sustained + simultaneous starts, queue delay, contention khi LLM/TTS chạy cùng GPU |
| Hành vi | tỷ lệ transcript bị lọc, hallucination trên silence/nhạc, false-cutoff của từ ngắn |

### 10.4 Logging theo từng turn

Ghi một timeline duy nhất với timestamp căn chỉnh: `audio_in → partial → stable → endpoint → final → commit → LLM first token → TTS first byte`. Có timeline này mới biết chỗ "chậm" nằm ở ASR, endpoint hay playback. Cộng đồng báo từng mất khoảng một tháng tune nhầm stage vì không có timeline này (**Reported**).[^usable]

### 10.5 Ma trận thí nghiệm tối thiểu

| # | Cấu hình | Mục đích |
|---|---|---|
| 1 | Whisper turbo `vi`, faster-whisper fp16, turn-final + filter | Baseline |
| 2 | Nemotron 3.5 `vi-VN` @160 / 320 / 560 ms | Đường cong latency–accuracy thật |
| 3 | Qwen3-ASR 0.6B và 1.7B, turn-final | Trần chất lượng LLM-ASR |
| 4 | Qwen3-ASR streaming (vLLM hoặc WLK windowed) | Cái giá của buffering |
| 5 | ChunkFormer RNNT large, PhoWhisper medium, turn-final | Đối chứng chuyên Việt |
| 6 | Two-pass: #2 + final #3 hoặc #5 | Chỉ khi 2–4 chưa đạt mức lỗi entity |

Mỗi lần chỉ đổi một thành phần. Gate production gồm: availability, license, hiệu năng trên phần cứng đích, và **không hành động trên text chưa ổn định**.

---

## 11. Lộ trình

1. **Tuần đầu (MVP):** mẫu A với Whisper turbo `vi` và filter, cộng per-turn log và corpus nhỏ. Mục tiêu là có một vòng đo được.
2. **Beta:** A/B Nemotron (160/320/560 ms) với Qwen 0.6B/1.7B, đúng policy của từng model. Thêm ChunkFormer/PhoWhisper làm đối chứng. Calibrate endpoint trên từ ngắn tiếng Việt.
3. **Production:** chọn B hoặc C. Chỉ thêm D khi mức lợi về entity error đáng với compute và latency bỏ thêm. Chuyển sang runtime native (NeMo-Speech.cpp, ONNX) chỉ sau khi qua gate parity về output và latency.

---

## 12. Mâu thuẫn còn mở và giới hạn

- **Chất lượng streaming của Qwen3-ASR:** vendor báo khoảng cách nhỏ (2.69 → 3.33 trên en/zh), trong khi một commenter nói Qwen stream kém hơn Parakeet. Chưa có phép đo chung nào giải quyết được.[^survey]
- **Denoise trước ASR:** các nguồn mâu thuẫn và chưa có nghiên cứu tiếng Việt.[^noise]
- **ChunkFormer small streaming:** card trả HTTP 401. Không suy ra là checkpoint không tồn tại, nhưng size, license và WER của nó chưa xác định.[^chunk]
- **Smart Turn tiếng Việt, khuyến nghị denoise, cấu hình Whisper filter:** phần lớn đến từ AI report thứ cấp, chưa được kiểm chứng ở nguồn gốc.[^turn][^pipeline]
- **Phạm vi khảo sát:** đây là snapshot của wiki, không phải khảo sát toàn thị trường. API cloud/proprietary chưa được nghiên cứu (ngôn ngữ, region, streaming, giá) nên không xếp hạng.[^vi-asr]
- **Bài viết không chạy model nào.** Mọi số liệu là Reported. Mọi khuyến nghị là Synthesis và cần đo lại trên dữ liệu, phần cứng và SLA của bạn.

---

## Tài liệu tham chiếu trong wiki

[^vi-asr]: [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md): Định nghĩa realtime; Shortlist và bằng chứng tiếng Việt; Qwen streaming/efficiency; Kiến trúc và hướng triển khai; Chọn runtime; Loại khỏi shortlist; Gate đánh giá.
[^survey]: [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md): Master catalog; Multilingual coverage (Vietnamese); Streaming and latency; Licensing; Serving runtimes; Community-reported field notes; Contradictions.
[^shortlist]: [Phân nhóm ASR/STT và shortlist realtime](../wiki/realtime-asr-selection.md): Nhóm và hướng phát triển; Size cho realtime; Shortlist triển khai thử; Runtime và diarization; Quyết định cho tiếng Việt.
[^pipeline]: [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md): Kiến trúc tổng thể; ASR tiếng Việt (ba mẫu ghép, cấu hình Whisper); VAD/endpointing; Transcript revisions; Deploy tools; Release gates.
[^nemotron]: [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md): Architecture and I/O; Streaming operating points; Throughput; Vietnamese operating curve; Inference and usage.
[^qwen]: [Qwen3-ASR family](../wiki/qwen3-asr-family.md): Language and audio coverage; Inference and serving; Transformers-native usage; Primary-paper clarification (2026-10-07).
[^chunk]: [ChunkFormer Vietnamese](../wiki/chunkformer-vietnamese.md): Checkpoint và kết quả; ONNX và online streaming; License và giới hạn triển khai.
[^pho]: [PhoWhisper](../wiki/phowhisper.md): Model và benchmark; Triển khai và quan hệ.
[^zip]: [ZipFormer 30M Vietnamese](../wiki/zipformer-30m-vietnamese.md): Benchmark và speed; License và quan hệ.
[^wlk]: [WhisperLiveKit](../wiki/whisperlivekit.md): Streaming policies; Backend notes (Qwen3 windowed/causal); Optional dependencies.
[^runtime]: [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md): Performance; Server, SDK, and source build.
[^usable]: [Community-Reported Usable STT for Voice Agents](../wiki/community-usable-stt-voice-agents.md): Usable-text evaluation checklist; Failure order; Logging. Bằng chứng cộng đồng, Unverified.
[^turn]: [Turn Detection Models](../wiki/turn-detection-models.md): Comparison; Operating practice. Nguồn AI report thứ cấp.
[^noise]: [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md): Evidence; Practice; Contradictions.
[^deploy]: [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md): STT streaming; API server; Runtime native.
