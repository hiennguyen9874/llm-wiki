# Lựa chọn và thiết kế ASR/STT realtime cho tiếng Việt

> **Loại tài liệu:** bài viết tổng hợp, là deliverable trong `outputs/`. Đây không phải tri thức canonical của wiki.
> **Ngày:** 2026-10-15 (bản đầu 2026-10-07; xem các mục thay đổi bên dưới).
> **Cập nhật lần này:** bổ sung [QUAN-Transcribe-1.0](../wiki/quan-transcribe-1.0.md) và [runtime/live streaming](../wiki/quan-transcribe-inference.md) từ wiki; không mở thêm raw, không chạy inference. Các phần cũ ngoài phạm vi QUAN được giữ lại, không phải đã kiểm chứng lại toàn bộ.
> **Nguồn chính:** [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md), [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md), [Phân nhóm ASR/STT và shortlist realtime](../wiki/realtime-asr-selection.md).
> **Nguồn model tiếng Việt:** [Nemotron 3.5 ASR](../wiki/nemotron-3.5-asr-streaming-0.6b.md), [Qwen3-ASR family](../wiki/qwen3-asr-family.md), [PhoWhisper](../wiki/phowhisper.md), [ChunkFormer Vietnamese](../wiki/chunkformer-vietnamese.md), [ZipFormer 30M Vietnamese](../wiki/zipformer-30m-vietnamese.md), [Gipformer 1.5 68M RNNT](../wiki/gipformer1.5-68m-rnnt.md), [Gipformer 68M RNNT](../wiki/gipformer-68m-rnnt.md), [Gipformer Inference Repository](../wiki/gipformer-inference-repo.md), [VietASR (zzasdf)](../wiki/zzasdf-viet-asr.md), [VietASR (dangvansam)](../wiki/dangvansam-viet-asr.md).
> **Nguồn runtime / đóng gói:** [NeMo-Speech.cpp ASR Configuration](../wiki/nemo-speech-asr-configuration.md), [NeMo-Speech.cpp HTTP and Realtime API](../wiki/nemo-speech-http-api.md), [handy-computer Qwen3-ASR-1.7B GGUF](../wiki/handy-computer-qwen3-asr-1.7b-gguf.md), [CSTR Qwen3-ASR-1.7B GGUF](../wiki/cstr-qwen3-asr-1.7b-gguf.md), [ggml-org Qwen3-ASR-1.7B GGUF](../wiki/ggml-org-qwen3-asr-1.7b-gguf.md), [CrispASR ASR Backend Selection](../wiki/crispasr-asr-backend-selection.md), [transcribe.cpp](../wiki/transcribe-cpp.md), [WhisperLiveKit](../wiki/whisperlivekit.md).
> **Nguồn control / hậu xử lý:** [Smart Turn v3.2](../wiki/smart-turn.md), [Turn Detection Models](../wiki/turn-detection-models.md), [Punctuation Restoration (base, 307M)](../wiki/punctuation-restoration-base.md), [VietNormalizer](../wiki/vietnormalizer.md), [ViSoNorm](../wiki/visonorm-visobert-normalizer.md), [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md), [Facebook Denoiser](../wiki/facebook-denoiser.md), [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md), [Community-Reported Usable STT for Voice Agents](../wiki/community-usable-stt-voice-agents.md).
> **Phạm vi bằng chứng:**
> - Bài dựa trên các trang wiki đã compile. `raw/` chỉ được mở có chủ đích ở hai chỗ mà wiki chưa ghi đủ chi tiết: (1) dòng `Vietnamese` trong bảng per-language FLORES của card Punctuation Restoration; (2) các hàng comparator (PhoASR-whisper-small, parakeet-ctc-0.6b-Vietnamese, wav2vec2-base-vi, Qwen3-ASR-0.6B, PhoWhisper small/medium, zipformer-rnnt 68M) trong bảng WER của hai card Gipformer.
> - Không cài đặt, không tải weights, không chạy model, không đo benchmark.
> - Mọi con số đều do vendor, tác giả hoặc report công bố (**Reported**). Mọi đề xuất lựa chọn, cấu hình và kiến trúc là suy luận tổng hợp (**Synthesis**).
> - Chưa có benchmark tiếng Việt nào chạy trên cùng audio, cùng normalizer, cùng chunk và cùng phần cứng cho các ứng viên chính.

---

## Bổ sung ngày 2026-10-15: QUAN-Transcribe

- Thêm model chuyên Việt **356M**, EmbeddingGemma 2 + CTC, full-context và chunked streaming **0.48 s**; vendor báo avg WER **6.87%**, throughput **3.713× realtime trên H100**. Đây không phải latency mic hay số streaming WER trung bình.[^quan]
- Live runtime chạy lại câu đang nói từ đầu mỗi update; sau silence mặc định **0.8 s**, decode lại full-context. Không gộp vào nhóm runtime cache-aware chỉ vì model có chunked attention.[^quan-live]
- Thêm vào shortlist như **challenger partial/final trên GPU**, không thay thứ tự baseline. Bổ sung điều kiện Gemma terms/gated encoder, output lowercase/không dấu câu/số dạng chữ, tùy chọn KenLM và benchmark gate riêng.[^quan][^quan-live]
- Bỏ nhận định cũ rằng chỉ bảng Gipformer so nhiều model Việt cùng normalizer: card QUAN cũng có bảng so sánh như vậy, nhưng hai bảng khác protocol và đều do vendor công bố.

## Thay đổi từ bản 2026-10-07 đến 2026-10-13

Bản 2026-10-13 ghi nhận các thay đổi sau từ log 2026-10-07 đến 2026-10-13 (`wiki/log.md`); lần cập nhật 2026-10-15 bổ sung QUAN ở mục trên:

| Nhóm | Bổ sung / sửa |
|---|---|
| Model chuyên Việt mới | **Gipformer 1.5 68M** và **Gipformer 68M** (Zipformer-RNNT, ONNX int8, MIT), có bảng WER vendor 12–16 tập; repo inference chỉ có đường **offline**. **VietASR (zzasdf, arXiv 2505.21527)**: pipeline SSL, checkpoint 70.000 giờ pseudo-label. **VietASR (dangvansam)**: QuartzNet 13M, không có WER. |
| Đóng gói Qwen3-ASR | Ba GGUF của 1.7B: handy-computer (transcribe.cpp, FLEURS-vi 6.15 ở Q8_0), CSTR (CrispASR, Q4_K rebake giữ encoder Q8_0), ggml-org (llama-server, card tối giản). |
| Runtime | NeMo-Speech.cpp có **word boosting cho cache-aware RNNT** (Nemotron), endpointing token-silence 800 ms, realtime WebSocket. CrispASR: tiếng Việt chỉ được nêu cho `fun-asr-mlt-nano`; server serialize inference. transcribe.cpp liệt kê `moonshine-*-vi` (chưa có concept). |
| Sửa số liệu | Smart Turn tiếng Việt cập nhật theo benchmark primary v3.2: **82.47% / 79.38%** accuracy (GPU/CPU), thay cho số 81.27% / FP 14.84% của AI report. Bản cũ ghi "Nemotron không có hotword" là sai với NeMo-Speech.cpp. |
| Hậu xử lý | Punctuation Restoration 307M (88 ngôn ngữ; Vietnamese F1 FLORES 0.866 cased / 0.791 lowercase). VietNormalizer (viết → nói) và ViSoNorm (informal → chuẩn). |
| VAD / denoise | TEN VAD, FireRedVAD, MarbleNet v2.0, PulseVAD: không có bằng chứng tiếng Việt. Facebook Denoiser: causal, CC-BY-NC. |
| Bằng chứng mới quan trọng | Cùng một model nhưng nguồn khác cho số rất khác nhau. Ví dụ Qwen3-ASR-1.7B FLEURS-vi: 5.55 (paper), 6.15 (GGUF Q8_0), 10.13 (bảng Gipformer). Xem 5.4. |

---

## 0. TL;DR

1. **Trước khi so sánh model, phải định nghĩa "realtime".** Có ba chế độ:
   - **native/stateful streaming:** giữ cache, xử lý audio theo chunk;
   - **buffered/policy streaming:** chờ đủ context, có thể rollback rồi mới commit;
   - **turn-final:** chờ endpoint rồi decode cả lượt nói.

   RTF < 1 chỉ cho biết model theo kịp luồng audio. Nó không phải độ trễ người dùng cảm nhận.
2. **Shortlist tiếng Việt, theo vai trò:**
   - **Partial sớm (native streaming):** [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md), chunk 160–320 ms. Ưu tiên khi cần runtime cache-aware có bằng chứng tiếng Việt; QUAN có chunked streaming nhưng live runtime recompute cả câu.[^quan-live]
   - **Chất lượng, chấp nhận buffering:** [Qwen3-ASR](../wiki/qwen3-asr-family.md) 0.6B → 1.7B.
   - **Baseline turn-final có runtime chín muồi nhất:** [Whisper large-v3-turbo](../wiki/whisper-large-v3-turbo.md) qua faster-whisper.
   - **Final-pass chuyên Việt, nhẹ:** [ChunkFormer RNNT large 113M](../wiki/chunkformer-vietnamese.md) (CC-BY-4.0), [Gipformer 1.5 68M](../wiki/gipformer1.5-68m-rnnt.md) (MIT, ONNX int8, CPU/edge, mạnh nhất trong bảng vendor ở call-center/domain), [PhoWhisper](../wiki/phowhisper.md) medium.
   - **Challenger chuyên Việt partial/final trên GPU:** [QUAN-Transcribe-1.0](../wiki/quan-transcribe-1.0.md), 356M; update 0.48 s, final full-context sau endpoint. Cần đo recomputation theo độ dài câu, final revision và license Gemma trước khi chọn.[^quan][^quan-live]
3. **Thiết kế khuyến nghị:**
   - **single-pass:** đủ cho MVP và cho nhiều sản phẩm.
   - **two-pass selective:** Nemotron xuất partial, cuối lượt chạy Qwen3-ASR 1.7B, ChunkFormer RNNT hoặc Gipformer 1.5 để ra final. Chỉ bật khi lỗi số, tên hay phủ định vượt ngưỡng chấp nhận.
   - Dù chọn kiểu nào, chỉ hành động trên **transcript đã commit**.
4. **Thứ tự lọc:** ngôn ngữ → chế độ realtime → license weights → runtime/phần cứng → đo trên dữ liệu thật. Không lọc bằng size hoặc leaderboard tiếng Anh.
5. **Các số liệu hiện có không so sánh trực tiếp được, kể cả cho cùng một model.**
   - Qwen 5.55 (FLEURS-vi, offline) và Nemotron 12.29 (FLEURS-vi, streaming 320 ms) khác protocol.
   - Cùng Qwen3-ASR-1.7B trên FLEURS-vi: 5.55 / 6.15 / 10.13 tùy nguồn. Khoảng chênh do normalizer, runtime và cách chạy còn lớn hơn khoảng chênh giữa nhiều model.
   - Bảng Gipformer so hơn 10 model trên cùng normalizer, nhưng do vendor tự chạy, có 4 tập private, và không có Nemotron hay Whisper turbo. Card QUAN cũng so nhiều model với cùng normalization/scoring theo tác giả; không ghép hai bảng thành một ranking. QUAN avg 6.87% là full-context greedy, không chứng minh thắng Nemotron ở cùng latency.[^quan]

   Muốn quyết định thì phải tự benchmark (xem mục 10).

---

## 1. Nhãn bằng chứng dùng trong bài

| Nhãn | Ý nghĩa |
|---|---|
| **Reported** | Số liệu hoặc tuyên bố của nguồn, chưa tái lập |
| **Observed** | Đã kiểm tra tĩnh trên artifact, ví dụ trường license trong card, hoặc code trong repo |
| **Synthesis** | Suy luận của bài từ các nguồn đã dẫn |
| **Unverified** | Chưa có sự kiện kiểm chứng. Không đồng nghĩa với sai |

Trang [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md) và [realtime shortlist](../wiki/realtime-asr-selection.md) đang ở `status: draft`. Lý do: thiếu WER streaming tiếng Việt cùng điều kiện, thiếu phần cứng và SLA mục tiêu, và chưa có bằng chứng về checkpoint streaming nhỏ của ChunkFormer. Các trang VietASR (zzasdf), handy-computer GGUF và ggml-org GGUF cũng là `draft`.

---

## 2. "Realtime" nghĩa là gì với ASR

### 2.1 Ba chế độ vận hành

| Chế độ | Cơ chế | Ví dụ trong wiki | Hệ quả thiết kế |
|---|---|---|---|
| **Native / stateful streaming** | Encoder (và decoder) giữ cache, chỉ xử lý audio mới không chồng lấp | Nemotron 3.5 / EN, Parakeet Realtime EOU, Voxtral Mini 4B Realtime, Audio8 Infinite, Confucius4-R2T2 (append-only), ChunkFormer small streaming (chưa truy cập được) | Có partial sớm và latency cấu hình rõ. Chất lượng giảm khi chunk nhỏ |
| **Buffered / policy streaming** | Nhận audio liên tục, chờ đủ context, dùng stable-prefix hoặc rollback rồi mới commit | Qwen3-ASR (paper dùng chunk 2 s, fallback 5 token, giữ 4 chunk cuối chưa cố định), Whisper qua WhisperLiveKit SimulStreaming/LocalAgreement, CrispASR `--stream` (sliding window) | Partial có thể bị sửa. Compute có thể phải recompute theo cửa sổ |
| **Turn-final** | VAD/endpoint cắt lượt, decode cả câu một lần | Whisper, PhoWhisper, ChunkFormer large, Gipformer (repo chỉ có `OfflineRecognizer`), VietASR zzasdf (`pretrained.py`), Cohere Transcribe, Fun-ASR-MLT, Qwen3-ASR GGUF trên transcribe.cpp (`streaming: false`) | Không có partial. Latency = endpoint + thời gian decode cả lượt |

**Trường hợp bổ sung — QUAN:** model dùng chunked attention, nhưng live runtime chạy lại câu hiện tại từ đầu mỗi 0.48 s, không có bằng chứng cache reuse. `streaming=True` trên file hoàn chỉnh chỉ trả transcript tương đương chế độ streaming; live audio dùng `LiveSession`. Vì vậy ba nhóm trên là khung thiết kế, không nên ép QUAN vào nhóm stateful chỉ theo kiến trúc.[^quan-live]

Có ba điểm hay bị nhầm (**Synthesis**):

- WebSocket/SSE ở tầng API **không biến** một checkpoint thành causal encoder. Ví dụ, [Parakeet ASR Server](../wiki/parakeet-asr-server.md) upload toàn bộ audio rồi mới stream text ra.
- Đầu RNNT/Zipformer **không bảo đảm** encoder là streaming. IndicConformer, ZipFormer 30M, Gipformer và VietASR zzasdf đều có transducer nhưng chưa có protocol streaming được công bố. Với Gipformer, code tham chiếu chỉ decode offline (**Observed** trong `infer_onnx.py`).[^gip-repo]
- Ma trận tính năng ghi "streaming ✔" cho mọi backend (CrispASR) không phân biệt native với windowed. README chỉ nêu cơ chế streaming cụ thể cho vài backend như voxtral4b, xasr, confucius4-r2t2.[^crisp-stream]

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
- **Qwen3-ASR GGUF, các key `rtf_*` (handy-computer: M4 Max cpu 9.59 / metal 41.08; Ryzen 4750U cpu 2.47 / vulkan 4.08):** card không định nghĩa đơn vị. Giá trị tăng theo backend nhanh hơn, nên nhiều khả năng là hệ số "x realtime" chứ không phải RTF thông thường. "0.2x realtime" của CSTR (một clip JFK 11 s, CPU 4 thread) cũng mơ hồ về đơn vị. Không so hai con số này với nhau (**Synthesis**).[^handy][^cstr]
- **QUAN, 3.713× H100:** audio duration / waveform-to-text wall time trong benchmark greedy; chưa có batch size hay live P95. **0.48 s** là chunk/update cadence và **0.8 s** là silence endpoint mặc định, không phải cùng một metric. README cảnh báo CPU lag trên câu dài.[^quan][^quan-live]
- **Gipformer:** script in RTF cho từng file nhưng repo và card **không công bố** con số RTF, latency hay memory nào.[^gip-repo]

---

## 3. Phân loại ASR theo kiến trúc

Wiki tổ chức ASR theo hai trục: **kiến trúc nhận dạng** và **cơ chế xuất transcript**. Kích thước, ngôn ngữ, endpointing, speaker attribution, runtime và license là các bộ lọc riêng.[^shortlist]

| Kiến trúc | Đại diện có tiếng Việt | Điểm mạnh | Chi phí/rủi ro cần đo |
|---|---|---|---|
| **Acoustic-first CTC / RNNT / TDT** (FastConformer, Conformer, Zipformer, QuartzNet) | Nemotron 3.5, ChunkFormer, ZipFormer 30M, Gipformer 68M/1.5, VietASR zzasdf (Zipformer), VietASR dangvansam (QuartzNet), parakeet-ctc-0.6b-Vietnamese (chỉ thấy trong bảng bên thứ ba) | Ít tham số, cache-aware streaming khi checkpoint hỗ trợ, phù hợp nhiều phiên, chạy được CPU/ONNX | Lỗi ngôn ngữ/domain. License của checkpoint streaming. RNNT không tự bảo đảm streaming. Nhiều model chuyên Việt chưa mô tả output có dấu câu/chữ hoa hay không |
| **Encoder–decoder seq2seq** | Whisper large-v3 / turbo, PhoWhisper, PhoASR-whisper-small, Cohere Transcribe, Moonshine `-vi` (chỉ có tên trong transcribe.cpp) | Runtime chín muồi (CTranslate2, whisper.cpp), baseline dễ đối chiếu | Cửa sổ 30 s, partial phải recompute, hallucination khi gặp silence/nhạc, cần policy cho end-of-turn |
| **Audio encoder + LLM decoder** | Qwen3-ASR, Fun-ASR-MLT-Nano | Đa ngôn ngữ, prompt context/hotword, mạnh ở turn-final | Tài nguyên decoder + encoder, độ trễ do rollback/commit, rủi ro instruction-hallucination. Không phải LLM-ASR nào cũng streaming |
| **SSL encoder + finetune** | wav2vec2-base-vi (chỉ trong bảng bên thứ ba); VietASR zzasdf (ASR-biased SSL + pseudo-label) | Tận dụng dữ liệu không nhãn lớn | Chất lượng phụ thuộc pseudo-label; dữ liệu và quyền dữ liệu ít được mô tả |
| **ASR kèm speaker attribution** | MOSS-Transcribe-Diarize (vi trong danh sách challenge) | Trả lời được ai nói gì, lúc nào | Chủ yếu offline long-form |
| **Massive multilingual** | SeamlessM4T v2 (vi), Omnilingual ASR (1600+, chưa kiểm vi) | Phủ ngôn ngữ ít tài nguyên | Phải kiểm từng ngôn ngữ. Seamless là CC-BY-NC |

Bảng là **Synthesis**. Nó không khẳng định kiến trúc nào luôn chính xác hơn kiến trúc nào.[^vi-asr][^shortlist][^survey]

---

## 4. Kích thước, tài nguyên và cách ước lượng

### 4.1 Dải kích thước để thử (heuristic, Synthesis)

| Mục tiêu | Dải thử đầu | Ghi chú |
|---|---|---|
| CPU / edge | 30–120M chuyên Việt, hoặc 0.6B với runtime/quantization phù hợp | Tiếng Việt: Gipformer 1.5 68M int8 (turn-final), ChunkFormer ONNX, Nemotron 3.5 Q8 qua NeMo-Speech.cpp (native streaming, phải đo lại), Whisper CT2 INT8 (turn-final), Qwen3-ASR-1.7B GGUF Q4_K/Q8_0 (offline). Phải đo trên CPU đích |
| GPU dùng chung với LLM/TTS | 0.1–0.6B; ~0.8B cho Whisper Turbo | Đo contention và tổng bộ nhớ của cả pipeline |
| GPU riêng cho ASR, cần chất lượng tốt hơn | 0.6–1.7B | Chỉ nâng size khi mức giảm lỗi bù được latency/cost |
| Streaming LLM-ASR trên GPU riêng | ~4B | Voxtral Realtime cần GPU ≥16 GB BF16, nhưng **không hỗ trợ vi** |
| 7B+ | Chỉ khi có nhu cầu đặc thù | Không mặc định dùng cho voice agent |

[^shortlist]

Bảng vendor của Gipformer cho thấy size không quyết định accuracy tiếng Việt: các model 30–68M Zipformer đứng trên Qwen3-ASR-1.7B và PhoWhisper-large 1.5B ở hầu hết tập call-center và domain (**Reported**; nhận xét là **Synthesis**).[^gip15]

### 4.2 Ước lượng trọng số

Công thức: `params × bytes/param`. Ở BF16: 0.6B ≈ 1.2 GB, 1.7B ≈ 3.4 GB, 4B ≈ 8 GB. Đây là **cận dưới chỉ tính weights**. Còn phải cộng encoder (khi tên model chỉ phản ánh decoder), KV/encoder cache theo từng phiên, workspace, allocator và runtime. Quantization cũng không bảo đảm tăng tốc.[^shortlist]

Tên kích thước dễ gây hiểu nhầm (**Reported**):

- **Qwen3-ASR "1.7B":** decoder Qwen3-1.7B + projector + encoder 300M. **"0.6B"**: decoder 0.6B + encoder 180M. Encoder AuT downsample 8x về 12.5 Hz, dynamic attention window 1–8 s.[^qwen]
- **Kích thước file GGUF của Qwen3-ASR-1.7B** (card): BF16/F16 ~4.08–4.09 GB, Q8_0 2.19 GB, Q6_K 1.69 GB, Q5_K_M 1.52 GB, Q4_K_M 1.32 GB (handy-computer); Q4_K ~1.5 GB, Q8_0 ~2.5 GB, F16 ~4.7 GB và cần ~5 GB RAM (CSTR).[^handy][^cstr]
- **Audio8-ASR-0.1B:** ~0.104B LM, nhưng ~0.324B tổng.[^shortlist]
- **Phonon-2 / Parakeet Redux:** model 0.6B được đóng gói chỉ còn 164 MB / 178 MB. Không được suy ra RAM peak từ kích thước file tải về.[^shortlist]

---

## 5. Khảo sát toàn bộ ASR có tiếng Việt trong wiki

### 5.1 Danh mục

Mọi số là **Reported** và chưa tái lập. Đơn vị là WER %. Cột "Nguồn số" cho biết ai chạy.

**A. Model chuyên tiếng Việt**

| Model | Size | Kiến trúc / chế độ | Số tiếng Việt tiêu biểu | Nguồn số | License weights |
|---|---|---|---|---|---|
| [QUAN-Transcribe-1.0](../wiki/quan-transcribe-1.0.md) | 356M, ~2800 h | EmbeddingGemma 2 Conformer + CTC reader; full/chunked 0.48 s; live recompute câu | Avg 6.87; fleurs 6.75; VIVOS 8.15; FLEURS-valid greedy full 6.71 / streaming 8.40 (khác protocol) | qnguyen3, card + inference README; chưa tái lập[^quan] | Gemma Terms of Use; encoder gated |
| [Gipformer 1.5 68M RNNT](../wiki/gipformer1.5-68m-rnnt.md) | 68M | Zipformer-RNNT, ONNX int8; repo chỉ offline | tele-medium 15.44; vi-asr-pubadmin 14.82; VIVOS 4.25; CMV 6.45; vlsp-t1 13.37; FLEURS 12.65 | Vendor (G-Group), 16 tập, 4 tập private | MIT (card; file LICENSE không có trong snapshot repo) |
| [Gipformer 68M RNNT](../wiki/gipformer-68m-rnnt.md) | 68M | Như trên, bản trước | tele-medium 15.53; vlsp-t2 20.40; VIVOS 4.12 | Vendor, 12 tập | MIT (card) |
| [ChunkFormer RNNT large](../wiki/chunkformer-vietnamese.md) | 113M, ~5000 h | Masked chunk-wise Conformer; long-form / turn-final | VIVOS 2.49; CMV 5.18; VLSP2020 T1/T2 12.75/20.47 | Tác giả | CC-BY-4.0 |
| ChunkFormer CTC large | 110M, ~3000 h | Như trên | VIVOS 4.18; CMV 6.66; T1/T2 14.09/25.81 | Tác giả | **CC-BY-NC-4.0** |
| ChunkFormer RNNT small streaming DCT | Chưa rõ | Stateful ONNX session | Không có | — (card HTTP 401) | Chưa rõ |
| [PhoWhisper](../wiki/phowhisper.md) tiny → large | 39M–1.55B | Whisper finetune 844 h; turn-final | large: VIVOS 4.67, CMV 8.14, T1/T2 13.75/26.68; medium: 4.97/8.27/14.12/26.85 | VinAI | BSD-3-Clause |
| [ZipFormer 30M](../wiki/zipformer-30m-vietnamese.md) | 30M, ~6000 h | Zipformer-RNNT; chưa có protocol streaming | VLSP2020 T1 12.29; VLSP2023 10.40/11.10; VLSP2025 7.97/8.10; GigaSpeech2 7.56 | Tác giả | **CC-BY-NC-ND-4.0** |
| [VietASR (zzasdf)](../wiki/zzasdf-viet-asr.md) | Chưa nêu (BPE 2000, đường dẫn `zipformer`) | Zipformer qua icefall; ASR-biased SSL + k-means pseudo-label, checkpoint `viet_iter3_pseudo_label` 70.000 giờ | README không có WER | — | Code Apache-2.0; license checkpoint không nêu |
| [VietASR (dangvansam)](../wiki/dangvansam-viet-asr.md) | 13M | QuartzNet (NeMo); `infer.py` file, `app.py` web | Không có WER | — | Chưa xác lập |

**B. Model đa ngôn ngữ có tiếng Việt**

| Model | Size | Chế độ | Số tiếng Việt | License weights |
|---|---|---|---|---|
| [Nemotron 3.5 ASR](../wiki/nemotron-3.5-asr-streaming-0.6b.md) | 600M | Native cache-aware streaming, `vi-VN` transcription-ready | FLEURS 13.41 / 12.87 / 12.29 / 11.78 / 11.18 tại 80 / 160 / 320 / 560 / 1120 ms (LangID); auto 13.59 → 11.22 | OpenMDW-1.1 (card: ready for commercial use) |
| [Qwen3-ASR-1.7B](../wiki/qwen3-asr-family.md) | ~1.7B + enc 300M | Offline; streaming chỉ trên vLLM, chưa đo vi | FLEURS 5.55, MLC-SLM 14.92 (paper) | Apache-2.0 |
| Qwen3-ASR-0.6B | 0.6B + enc 180M | Offline | FLEURS 8.52, MLC-SLM 17.67 (paper) | Apache-2.0 |
| [handy-computer Qwen3-ASR-1.7B GGUF](../wiki/handy-computer-qwen3-asr-1.7b-gguf.md) | 1.32–4.09 GB | Offline, transcribe.cpp, tự nhận ngôn ngữ, **không** cho ép ngôn ngữ | FLEURS-vi 6.15 (chỉ Q8_0, không nêu protocol) | Apache-2.0 (kế thừa) |
| [CSTR Qwen3-ASR-1.7B GGUF](../wiki/cstr-qwen3-asr-1.7b-gguf.md) | ~1.5–4.7 GB | CrispASR, có `-l` language hint | Không có số vi | Apache-2.0 |
| [ggml-org Qwen3-ASR-1.7B GGUF](../wiki/ggml-org-qwen3-asr-1.7b-gguf.md) | Chưa nêu | `llama-server -hf`; card không nêu quant, license, định dạng request | Không có | Không có trường license |
| [Whisper large-v3-turbo](../wiki/whisper-large-v3-turbo.md) | 809M | Turn-final / buffered | Chưa có số vi cùng điều kiện | MIT (card) |
| [Whisper large-v3](../wiki/whisper-large-v3.md) | 1.55B | Turn-final | Bảng ChunkFormer: VIVOS 8.81, CMV 15.45, T1/T2 20.41/68.61 | Apache-2.0 (card) |
| [Fun-ASR-MLT-Nano](../wiki/fun-asr-mlt-nano-2512.md) | 800M | Turn-final | Có vi trong 31 ngôn ngữ, không có điểm | Apache-2.0 theo card; CrispASR ghi "FunASR Model License v1.1" (cần đối chiếu) |
| [Cohere Transcribe 03-2026](../wiki/cohere-transcribe-03-2026.md) | 2B | Turn-final | Có vi trong 14 ngôn ngữ; plot vi chưa inspect | Apache-2.0 |
| [MOSS-Transcribe-Diarize](../wiki/moss-transcribe-diarize.md) | 0.9B | Offline long-form + diarization | Vi trong danh sách MLC-SLM challenge, không có điểm riêng | Apache-2.0 |
| [SeamlessM4T v2 Large](../wiki/seamless-m4t-v2-large.md) | 2.3B | Offline | Vi có cả speech/text vào-ra | **CC-BY-NC** |
| Moonshine `moonshine-base-vi`, `moonshine-tiny-vi` | Chưa rõ | transcribe.cpp liệt kê, không có cờ streaming | Không có | Chưa rõ (chưa có concept) |

**C. Chỉ xuất hiện trong bảng của bên thứ ba (chưa có concept)**

`nvidia/parakeet-ctc-0.6b-Vietnamese` (600M), `nguyenvulebinh/wav2vec2-base-vi` (95M), `Qualcomm-AI-Research/PhoASR-whisper-small` (244M), `zipformer-rnnt` 68M (tên "VietASR-zipformer" trong card Gipformer 68M). Wiki chưa đối chiếu hàng "VietASR-zipformer" này với dự án zzasdf, nên không gán số cho nhau.[^gip68][^zzasdf]

[^vi-asr][^nemotron][^qwen][^chunk][^pho][^zip][^survey][^gip15][^gip68][^zzasdf][^dvs][^handy][^cstr][^ggml][^tcpp]

### 5.2 Bảng so sánh nhiều model trên cùng normalizer (vendor Gipformer)

Đây là một bảng vendor chạy hơn 10 model tiếng Việt với cùng normalizer (không phải bảng duy nhất; xem QUAN ở 5.6): lowercase, bỏ dấu câu, số chuyển sang dạng nói. Nhưng vendor tự chạy, không mô tả test-set hygiene, và 4 tập `tele-*` là private. Số lấy từ card Gipformer 1.5 (**Reported**).[^gip15][^gip-raw]

**Call-center (private) và domain (public trên Hugging Face `g-group-ai-lab`):**

| Model | Params | tele-medium | tele-hard N / M / S | vi-asr tech / edu / finance / pubadmin |
|---|---:|---:|---|---|
| gipformer1.5-68M | 68M | **15.44** | 26.24 / 33.31 / **32.48** | **27.49 / 23.32 / 22.34 / 14.82** |
| gipformer-68M | 68M | 15.53 | **25.10 / 32.27** / 32.62 | 36.59 / 29.81 / 29.67 / 20.09 |
| Zipformer-30M-6000h | 30M | 19.53 | 38.13 / 44.73 / 41.58 | 29.77 / 25.91 / 25.86 / 17.92 |
| zipformer-rnnt | 68M | 20.30 | 42.21 / 49.01 / 47.86 | 36.81 / 30.26 / 29.13 / 18.62 |
| wav2vec2-base-vi | 95M | 23.71 | 40.49 / 48.90 / 46.33 | 59.86 / 53.06 / 49.66 / 39.82 |
| Qwen3-ASR-1.7B | 1.7B | 26.34 | 46.80 / 59.85 / 51.84 | 27.95 / 29.93 / 34.09 / 31.83 |
| PhoWhisper-medium | 769M | 26.46 | 51.20 / 59.04 / 55.39 | 47.93 / 43.00 / 41.60 / 34.81 |
| PhoWhisper-large | 1.5B | 26.82 | 50.39 / 59.44 / 56.70 | 42.94 / 44.99 / 40.54 / 33.78 |
| chunkformer-large-vie | 110M* | 27.60 | 46.30 / 51.91 / 49.09 | 39.81 / 37.20 / 34.31 / 29.30 |
| PhoASR-whisper-small | 244M | 30.73 | 50.30 / 56.66 / 54.12 | 44.35 / 41.65 / — / 35.99 |
| parakeet-ctc-0.6b-Vietnamese | 600M | 31.82 | 55.33 / 61.65 / 56.70 | 48.69 / 45.86 / 43.16 / 38.84 |
| Qwen3-ASR-0.6B | 600M | 32.29 | 48.57 / 61.88 / 55.43 | 37.52 / 36.97 / 38.31 / 38.65 |
| PhoWhisper-small | 244M | 33.96 | 55.88 / 65.41 / 62.35 | 56.81 / 51.87 / 47.36 / 41.46 |

**Tập public đọc/broadcast/y tế:**

| Model | VIVOS | CMV | vlsp-t1 | VietMed | MultiMED | LSVSC | FLEURS | ViMD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gipformer1.5-68M | 4.25 | 6.45 | 13.37 | **19.23** | **19.17** | 8.97 | 12.65 | **7.00** |
| gipformer-68M | **4.12** | 6.63 | 13.39 | 19.41 | 19.35 | 8.96 | 12.92 | 7.17 |
| Zipformer-30M-6000h | 4.55 | **4.16** | **11.78** | 19.91 | 19.88 | 9.04 | 13.03 | 7.18 |
| chunkformer-large-vie | 4.18 | 6.94 | 14.09 | 19.59 | 22.60 | 8.85 | 14.17 | 11.77 |
| PhoWhisper-large | 4.73 | 8.60 | 13.70 | 24.37 | 24.47 | 10.08 | 12.62 | 11.18 |
| PhoASR-whisper-small | 5.87 | 9.73 | 14.60 | 23.10 | 22.78 | **7.59** | 13.97 | 9.75 |
| Qwen3-ASR-1.7B | 7.17 | 10.76 | 16.29 | 20.21 | 20.11 | 9.64 | **10.13** | 11.16 |
| parakeet-ctc-0.6b-Vietnamese | 7.76 | 11.40 | 17.00 | 23.53 | 23.79 | 10.46 | 16.11 | 12.95 |
| Qwen3-ASR-0.6B | 10.23 | 16.68 | 18.62 | 22.51 | 22.65 | 10.96 | 13.11 | 14.37 |

\* Card Gipformer 68M ghi "110M" cho `chunkformer-large-vie`, và VIVOS 4.18 khớp card **CTC** 110M (license NC). Vì vậy nhiều khả năng hàng này là bản CTC chứ không phải RNNT 113M CC-BY. ChunkFormer RNNT large (VIVOS 2.49 theo tác giả) không có mặt trong bảng này (**Synthesis**).[^gip68][^chunk]

Cách đọc (**Synthesis**):

- Gipformer 1.5 dẫn đầu ở call-center và domain với khoảng cách lớn: hơn đối thủ ngoài họ Gipformer gần nhất (Zipformer-30M) khoảng 9–12 điểm ở ba tập tele-hard.
- Trên tập public đọc/broadcast, khoảng cách nhỏ hoặc âm: Zipformer-30M thắng CMV và vlsp-t1, Qwen3-ASR-1.7B thắng FLEURS, PhoASR-whisper-small thắng LSVSC.
- Bảng **không có** Nemotron 3.5, Whisper turbo/large-v3, Fun-ASR-MLT hay Cohere. Bảng cũng không đo latency hay streaming.
- Đây là benchmark của bên có lợi ích, chưa có xác minh độc lập.

### 5.3 Đường cong latency–accuracy của Nemotron tiếng Việt

```text
chunk (ms):   80     160    320    560    1120
WER LangID: 13.41  12.87  12.29  11.78  11.18
WER auto:   13.59  13.02  12.40  12.02  11.22
```

Hai đặc điểm (**Synthesis** từ số Reported):

- Đi từ 80 ms lên 1120 ms giảm khoảng 2.2 điểm WER. Bước 160 → 320 ms rẻ về latency mà vẫn được ~0.6 điểm.
- Auto-detect chỉ phạt nhẹ với tiếng Việt (≤ 0.24 điểm). Dù vậy, trong production nên đặt `vi-VN` tường minh, vì pipeline Transformers mặc định prompt `en-US`.[^nemotron]

### 5.4 Cùng một model, nhiều con số

| Model / tập | Giá trị theo từng nguồn | Ghi chú |
|---|---|---|
| Qwen3-ASR-1.7B, FLEURS-vi | 5.55 (paper, offline vLLM BF16) · 6.15 (handy-computer GGUF Q8_0, transcribe.cpp, không nêu protocol) · 10.13 (bảng Gipformer, normalizer số→chữ) | Chênh gần gấp đôi giữa các nguồn |
| Qwen3-ASR-0.6B, FLEURS-vi | 8.52 (paper) · 13.11 (Gipformer) | |
| PhoWhisper-large, VIVOS / CMV / vlsp-t1 | 4.67 / 8.14 / 13.75 (VinAI) · 4.73 / 8.60 / 13.70 (Gipformer) | Chênh nhỏ |
| ZipFormer 30M, vlsp-t1 | 12.29 (tác giả) · 11.78 (Gipformer 1.5) · 11.76 (Gipformer 68M) | |
| ChunkFormer large, CMV | 6.66 (card CTC) · 6.94 (Gipformer 1.5) | |
| Gipformer-68M, LSVSC | 8.96 (card 68M) · 9.04 (card 1.5) | Cùng vendor, hai card khác nhau |

[^qwen][^handy][^gip15][^gip68][^pho][^zip][^chunk]

Kết luận (**Synthesis**): khác biệt do normalizer (số, dấu câu, chữ hoa), runtime/quantization và cách chạy có thể lớn hơn khác biệt giữa các model. Không ghép số từ các nguồn khác nhau vào một ranking. Chỉ tin phép đo chạy cùng pipeline chấm điểm.

### 5.5 Những gì **không** được suy ra

- **FLEURS, VIVOS, CMV, VLSP, MLC-SLM và các tập `tele-*` là các tập khác nhau.** Không xếp hạng xuyên cột.[^vi-asr]
- **Qwen 5.55 < Nemotron 12.29 không chứng minh Qwen thắng ở cùng latency.** Số Qwen là offline, số Nemotron là streaming 320 ms có LangID.[^vi-asr]
- **Số của ChunkFormer large không áp dụng cho checkpoint small streaming** (`chunkformer-rnnt-small-vie-stream-dct`). Card của checkpoint này trả HTTP 401, nên size, license, WER và latency của nó đều chưa biết.[^chunk]
- **Gipformer thắng call-center không có nghĩa Gipformer dùng được cho partial.** Card không nêu streaming, chunk, lookahead, endpointing, hotword, dấu câu hay ITN. Code tham chiếu chỉ decode offline.[^gip15][^gip-repo]
- **Con số 16.44% WER của Whisper large-v3 "theo VietASR"** (xuất hiện trong Vietnamese Voice Agent Stack và Pipeline Design) không có trong README VietASR đã capture. Nó vẫn **Unverified** cho đến khi đối chiếu bảng của paper.[^zzasdf]
- **Các bảng so sánh do tác giả tự chạy** (ChunkFormer, Gipformer) có cột API Viettel/Google/FPT hoặc model đối thủ không rõ version/ngày. Chúng không phải ranking hiện tại.[^chunk]
- **Khoảng cách streaming/offline của Qwen** (1.7B: 2.69 → 3.33; 0.6B: 3.48 → 4.40) chỉ đo trên LibriSpeech và FLEURS-en/zh, **không có tiếng Việt**.[^qwen]

---

### 5.6 QUAN: benchmark riêng, không ghép ranking với Gipformer

Card QUAN báo cùng utterances, normalization/scoring và greedy cho các model; GPU được ghi H100 bf16/fp16, nhưng các hàng API có speed N/A và setup chưa rõ. Không có batch size, split/count chi tiết hay uncertainty trong bảng chính.[^quan]

| QUAN: tập theo nhãn card | WER % |
|---|---:|
| bud500 / cv17 / fleurs / gigaspeech2 | 1.62 / 10.19 / 6.75 / 12.34 |
| lsvsc / phoaudiobook / vimd / VIVOS | 5.48 / 1.35 / 9.05 / 8.15 |
| **Average** | **6.87** |

Trong **chính bảng QUAN**, Qwen3-ASR-1.7B và Cohere cùng avg 7.01%, PhoWhisper-large 7.21%. Nhưng Qwen tốt hơn ở fleurs/gigaspeech2 (4.88/8.47), PhoWhisper-large tốt hơn ở cv17/phoaudiobook/VIVOS (9.12/0.87/4.52). Đây là **Reported** của vendor, không xác minh SOTA độc lập.[^quan]

Inference README có protocol khác: FLEURS-valid greedy full **6.71% → streaming 8.40%**. Bảng KenLM loại reference chứa digits, dùng beam 32, alpha 0.3, beta 1.0, tune trên valid:

| Subset đã lọc digits | Số câu | Greedy | + KenLM |
|---|---:|---:|---:|
| FLEURS valid / test | 317 / 679 | 6.71 / 7.10 | 4.79 / 5.03 |
| Common Voice 17 valid / test | 641 / 1274 | 6.58 / 9.64 | 5.05 / 7.32 |

Không thay fleurs 6.75 bằng filtered-test 7.10 hay LM 5.03 mà bỏ nhãn protocol; chưa có matched streaming + LM WER. Train và test cùng nêu tên một số corpora nhưng chưa đủ thông tin xác lập split disjointness; cũng không đủ để kết luận leakage (**Synthesis/giới hạn**).[^quan]

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
  - [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md) với Q8 GGUF (CLI, HTTP/WebSocket, C SDK); `nemotron-3.5` là model mặc định của CLI;
  - Transformers ≥ 5.13 (`set_num_lookahead_tokens`, `language` cho từng chunk).[^nemotron][^runtime][^nemo-models]
- **Tính năng qua NeMo-Speech.cpp (Reported):**[^nemo-cfg][^nemo-api]
  - **Word boosting** cho cache-aware RNNT qua `speech_contexts` (HTTP/realtime/gRPC) hoặc `--speech-context`. Mức boost điển hình 2–3, trần `boosting_max_boost` 5.0. Cần GGUF có SentencePiece tokenizer nhúng.
  - **Endpointing** giữa luồng, tắt mặc định. Bật lên thì EOU kích hoạt khi im lặng đạt `stop_history_eou_ms` = 800 ms, ở chế độ token-silence (không cần VAD) hoặc VAD-driven (Silero GGUF).
  - **Realtime WebSocket** `/v1/audio/transcriptions/realtime`: protocol riêng của dự án, không phải OpenAI Realtime. Nhận PCM16, trả `...delta` cho partial và `...completed` cho final; `session.update` có `language`, `endpointing_ms`, `speech_contexts`.
  - **ITN** (Sparrowhawk) chọn grammar theo thư mục con theo ngôn ngữ (`en`, `es`, `de`, …). Tài liệu không nêu grammar tiếng Việt, nên với `vi` coi như chưa có ITN (**Synthesis**).
  - Hạn chế gRPC: chỉ LINEAR_PCM; confidence của RNNT hiện luôn là 1.0, nên **không dùng được làm tín hiệu chất lượng**.
- **Throughput (H100, Reported):** khoảng 240 stream ở 80 ms và khoảng 2400 stream ở 1.12 s. Phải đo lại cho tiếng Việt và phần cứng đích.[^nemotron]
- **Rủi ro:**
  - Lỗi WER ~12% trên FLEURS là đáng kể cho tên, số và phủ định.
  - License OpenMDW-1.1 cần legal review.
  - Runtime Apache-2.0 không thay thế license của weights.[^vi-asr]

### 6.2 Qwen3-ASR 0.6B / 1.7B: ưu tiên chất lượng

- **Điểm mạnh:** FLEURS-vi offline tốt nhất trong paper (5.55 / 8.52). Có LID 97.9% (1.7B). Hỗ trợ prompt context/hotword (`prompt="Vocabulary: ..."`), ép ngôn ngữ, và fine-tune qua `-hf`.[^qwen]
- **Điểm yếu trong bảng Gipformer:** trên call-center tiếng Việt, Qwen3-ASR-1.7B kém các model Zipformer 30–68M khoảng 7–27 điểm WER (tele-medium 26.34 so với 15.44). Riêng vi-asr-tech thì gần ngang (27.95 so với 27.49) (**Reported**, vendor).[^gip15]
- **Streaming:**
  - Toolkit gốc chỉ stream trên vLLM, không có batch và không có timestamps.
  - WhisperLiveKit có backend `qwen3-streaming` (windowed, mặc định 12 s left context, bắt buộc `--language` vì auto-detect đổi giữa chừng với giọng có accent; khuyến nghị **một phiên realtime mỗi GPU**).
  - Bản causal `qfuxa/qwen3-asr-0.6b-streaming` **chỉ hỗ trợ tiếng Anh**, nên không dùng cho tiếng Việt.[^wlk]
  - [Confucius4-R2T2](../wiki/confucius4-r2t2.md) là derivative true-streaming append-only của Qwen3-ASR-1.7B, nhưng chỉ tối ưu zh/en và **không có bằng chứng vi**.
- **Đóng gói GGUF cho CPU/edge (1.7B):**

  | Gói | Runtime | Ép ngôn ngữ | Streaming | Ghi chú |
  |---|---|---|---|---|
  | handy-computer | transcribe.cpp | **Không** ("not supported at this time") | `false` | 6 mức BF16 → Q4_K_M; LibriSpeech 1.62 → 1.81; FLEURS-vi 6.15 (Q8_0) |
  | CSTR | CrispASR (`--backend qwen3`, alias `qwen3-1.7b`) | Có (`-l`) | Server serialize inference mặc định | Q4_K bản rebake 2026-07 giữ audio encoder ở Q8_0. Bản Q4_K cũ có thể trả transcript rỗng hoặc lặp mà vẫn báo thành công |
  | ggml-org | llama.cpp `llama-server -hf` | Không nêu | Không nêu | Card không nêu quant, license hay định dạng request audio |

  Với tiếng Việt, việc không ép được ngôn ngữ trên transcribe.cpp là rủi ro trên clip ngắn và code-switch. Với CrispASR, phải kiểm bản Q4_K tải về có phải bản rebake không, vì card không có checksum hay ngày cụ thể (**Synthesis**).[^handy][^cstr][^ggml]
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
- Mức giảm WER từ medium (769M) lên large (1.55B) nhỏ (VIVOS 4.97 → 4.67). Trong bảng Gipformer, medium còn nhỉnh hơn large ở tele-medium và vi-asr-edu. Nên thử **medium trước**.[^pho][^gip15]
- Đường CTranslate2/faster-whisper cần conversion và test parity riêng. Chưa có bằng chứng về stable partial (**Synthesis**).[^pho]
- Trong bảng Gipformer, `PhoASR-whisper-small` (Qualcomm, 244M) tốt hơn PhoWhisper-small ở mọi cột có số và dẫn đầu LSVSC (7.59). Wiki chưa có concept hay license cho model này.[^gip-raw]

### 6.5 ChunkFormer Vietnamese: acoustic-first chuyên Việt

- Masked chunk-wise Conformer + CTC/RNNT. **RNNT large 113M** có số tác giả tốt nhất trên VIVOS/CMV/VLSP và license CC-BY-4.0. Bản CTC là NC.[^chunk]
- **ONNX:**
  - Export full-context và streaming là hai đường riêng.
  - `OnnxAsrModel.stream()` → `StreamingSession` giữ cache attention/conv và trạng thái LSTM của RNNT; dùng `push_waveform` / `push_features` / `finalize`.
  - Chỉ hỗ trợ greedy CTC/RNNT. Không có beam search hay attention rescoring.[^chunk]
- **Cấu hình streaming phải thuộc `dynamic_chunk_sizes` đã huấn luyện.** Không được tự giảm right context của bản large rồi coi như đã có model streaming.[^chunk]
- **Vai trò đề xuất:** final-pass chuyên Việt có chi phí thấp. Chỉ dùng làm streaming sau khi qua gate về availability, license và latency của checkpoint small.[^vi-asr]

### 6.6 Gipformer 68M / 1.5: chuyên Việt cho CPU/edge, mạnh ở call-center

- **Model:** Zipformer Transducer 68M, ONNX Runtime int8, MIT, định vị cho on-device/edge offline. Bản 1.5 chủ yếu cải thiện 4 tập domain (tech 36.59 → 27.49, pubadmin 20.09 → 14.82). Ở call-center thì gần như ngang bản trước, thậm chí hơi kém ở north và middle (**Reported**).[^gip15]
- **Repo inference (`ggroup-ai-lab/gipformer`, rev `0cac5b1`, Observed):**[^gip-repo]
  - Đường ONNX: `sherpa_onnx.OfflineRecognizer.from_transducer(...)`, 16 kHz, fbank 80 chiều. Cả file đi qua `accept_waveform` rồi `decode_streams`, tức là **decode offline**. Repo không có `OnlineRecognizer`, chunking hay endpointing.
  - Mặc định CLI: `--quantize fp32`, `--num-threads 4`, `--decoding-method modified_beam_search` (có thể đổi `greedy_search`). Weights tải từ Hugging Face theo `--version 1` / `1.5`.
  - Đường PyTorch: clone `k2-fsa/icefall` không pin version lúc chạy; `torch.load(..., weights_only=False)` và `strict=False`, nên **chỉ nạp checkpoint tin cậy**. Chỉ Linux x86_64 + CUDA 12.8.
  - Hàm `load_model()` mặc định `int8`, còn CLI mặc định `fp32`. Phải đặt tường minh khi đo.
- **Chưa biết:** output có dấu câu/chữ hoa hay không (card chấm trên văn bản đã lowercase và bỏ dấu câu), dữ liệu train và quyền dữ liệu, RTF/latency/memory, hotword.[^gip15]
- **Vai trò đề xuất (Synthesis):**
  - final-pass hoặc turn-final trên CPU/edge, đặc biệt cho tổng đài và domain hành chính/tài chính;
  - final recognizer cho mẫu two-pass (Nemotron partial → Gipformer final);
  - chỉ đưa vào nhánh partial khi có checkpoint hoặc runtime streaming được chứng minh.
- Cần gate: tự đo trên audio tổng đài của mình (4 tập `tele-*` không công khai), kiểm file LICENSE thật, và thêm bước khôi phục dấu câu nếu output không có (xem 7.6).

### 6.7 VietASR (zzasdf) và VietASR (dangvansam): hai dự án trùng tên

- **zzasdf/VietASR (arXiv 2505.21527):**[^zzasdf][^zzasdf-proc]
  - pipeline 4 bước cho ASR ít nhãn: train ASR ban đầu trên tập nhãn nhỏ → k-means → pretrain SSL → finetune; chạy trên icefall + lhotse; audio không nhãn được cắt bằng FunASR `fsmn-vad`.
  - checkpoint `zzasdf/viet_iter3_pseudo_label` (70.000 giờ pseudo-label, Iteration 3); suy luận qua `ASR/zipformer/pretrained.py --method modified_beam_search`, tức là **turn-final**.
  - gói sherpa-onnx `csukuangfj/sherpa-onnx-zipformer-vi-2025-04-20` trỏ về checkpoint này (theo trang ZipFormer 30M).[^zip]
  - README không có WER. Code Apache-2.0; license checkpoint không nêu. Có mâu thuẫn về layout dữ liệu có nhãn (`download/supervised` hay `download/{train,test,dev}`).
  - **Vai trò:** hướng nghiên cứu khi có nhiều audio tiếng Việt không nhãn trong domain riêng (tổng đài, y tế). Chưa phải ứng viên production vì thiếu WER và license checkpoint.
- **dangvansam/viet-asr:** QuartzNet 13M trên NeMo, ~100 giờ dữ liệu trộn (YouTube, radio, tổng đài 8 kHz, TTS, VLSP/VIVOS/FPT). Không có WER, streaming hay license; Python/torch mâu thuẫn (badge 3.10, cài ≥3.8, torch 1.8.1). **Không đưa vào shortlist.**[^dvs]

### 6.8 Các ứng viên phụ

- **Fun-ASR-MLT-Nano 800M:** có vi, hotwords và ITN. Là challenger turn-final. Không nhầm với Fun-ASR-Nano (zh/en/ja) hay SenseVoiceSmall của WLK. CrispASR chỉ nêu tiếng Việt cho backend này.[^vi-asr][^crisp]
- **Cohere Transcribe 2B:** challenger final-pass. Không có timestamps/diarization, code-switch không ổn định, cần VAD.[^vi-asr]
- **ZipFormer 30M:** rất nhẹ cho CPU và mạnh trên CMV/vlsp-t1 trong bảng Gipformer, nhưng **CC-BY-NC-ND** và chưa có protocol streaming. Chỉ dùng cho nghiên cứu.[^zip][^gip15]
- **MOSS-Transcribe-Diarize 0.9B:** có vi trong danh sách challenge, nhưng là offline long-form. Phù hợp review meeting, không phù hợp agent.[^vi-asr]
- **Moonshine `-vi` (tiny/base) trong transcribe.cpp:** có tên model nhưng chưa có concept, WER hay license. CrispASR xếp Moonshine tiny nhanh nhất trên CPU (16× realtime) nhưng không nói về tiếng Việt. Chỉ đáng thử khi cần ASR CPU rất nhẹ, và phải đo trước khi tin (**Synthesis**).[^tcpp][^crisp]
- **parakeet-ctc-0.6b-Vietnamese, wav2vec2-base-vi:** chỉ thấy trong bảng Gipformer, và đều đứng sau các Zipformer chuyên Việt ở gần hết các cột.[^gip-raw]

### 6.9 Loại khỏi shortlist tiếng Việt

Danh sách ngôn ngữ đã compile **không có vi** cho các model sau:

- Parakeet 25-European và các derivative (Phonon, Redux, Ultra, Orukeet);
- Canary;
- Voxtral (13 ngôn ngữ, và 8);
- Audio8 Infinite (zh/en), Audio8 0.1B;
- SenseVoiceSmall, GLM-ASR, Hojo, ARK;
- VibeVoice-ASR-Streaming (10 ngôn ngữ);
- Granite TurboCTC, Distil-Large-v3.5, Parakeet EOU (chỉ tiếng Anh).

Confucius4-R2T2 chưa có bằng chứng tường minh cho vi (streaming tối ưu zh/en). Điều đó chưa có nghĩa là không hỗ trợ, chỉ là chưa đủ để khuyến nghị. Omnilingual (1600+) chưa kiểm kết quả theo từng ngôn ngữ. SeamlessM4T v2 có vi nhưng là non-commercial và chưa có bằng chứng streaming. **Không suy ra hỗ trợ tiếng Việt từ parent encoder hoặc từ chữ "multilingual".**[^vi-asr][^survey]

---

### 6.10 QUAN-Transcribe-1.0: challenger CTC chuyên Việt cho GPU

- **Kiến trúc (Reported):** encoder EmbeddingGemma 2 USM-style Conformer 12 lớp, fine-tune hai lớp trên; learned layer mix → Transformer reader 6 lớp, d=768, CTC vocabulary 14.917 token. Dynamic chunk training; ~2800 h tiếng Việt.[^quan]
- **Output:** 16 kHz mono; lowercase, không punctuation, số viết bằng chữ. Không coi đây là ITN; cần xử lý và kiểm riêng số/tên/phủ định.[^quan][^quan-live]
- **Live:** `LiveSession.accept(block)` nhận 16 kHz mono float32, trả câu đã xong; `session.partial` là câu đang nói, `flush()` kết thúc. Update mỗi 0.48 s, giữ text chunk đã xong trong streaming; silence mặc định 0.8 s thì decode full-context, nên final có thể sửa partial. Live chạy lại từ đầu câu mỗi update, README nói cần CUDA/MPS để theo kịp, CPU lag với câu dài.[^quan-live]
- **File/batch:** `asr.transcribe(path, streaming=True)` không phải API nhận chunk live. File dài chia tối đa 30 s ở quiet point; `batch_seconds` mặc định 600 s **padded audio** mỗi forward, giảm khi OOM. Device ưu tiên CUDA bf16 → MPS fp32 → CPU fp32; chưa có VRAM hay CPU benchmark.[^quan-live]
- **KenLM tùy chọn:** four-gram 91 MB, beam mặc định 32, CPU decode từng utterance. README báo ~15 ms/câu ở beam 32, ~7 ms ở beam 8, thiếu model CPU/độ dài câu; trên GPU đây có thể là chi phí chính. Live chỉ dùng LM cho final khi bật. Custom word-level KenLM cần lowercase/không punctuation/số dạng chữ; không phải API hotword trực tiếp.[^quan-live]
- **License:** Gemma Terms of Use cho weights; encoder gated, chấp nhận terms và authenticate trước first-use download. Code license chưa xác lập riêng; terms đầy đủ chưa inspect. Không xếp chung MIT/Apache.[^quan]
- **Vai trò (Synthesis):** A/B với Nemotron và Qwen cho partial/final chuyên Việt trên GPU; cũng thử turn-final. Không suy 356M hay throughput H100 thành khả năng CPU/edge hoặc concurrency. Giữ baseline hiện tại đến khi qua benchmark ở mục 10.[^quan][^quan-live]

---

## 7. Thiết kế hệ thống ASR

### 7.1 Vị trí của ASR trong pipeline

```text
Client mic + AEC ─► gateway (per-session) ─► resample 16 kHz mono, ring buffer
   ├─► [denoise nhẹ, tùy chọn] ─► Silero VAD ─► Smart Turn + timeout ─► endpoint/barge-in
   ├─► audio AEC gốc (không enhance) ─► ASR streaming state  ─► partial/stable
   └─► turn audio buffer ─────────────► final recognizer (tùy chọn) ─► final
                         ─► [punctuation/ITN nếu model không có] ─► transcript revisions
                         ─► validity gate ─► COMMITTED turn ─► LLM
```

Nguyên tắc (**Synthesis**):[^pipeline][^noise]

1. **ASR nghe audio đã qua AEC nhưng chưa denoise.** Bằng chứng về denoise-trước-ASR đang mâu thuẫn: có nguồn báo giúp, có nguồn ("When De-noising Hurts") báo hại, và không nguồn nào về tiếng Việt. Chỉ denoise nhánh VAD/barge-in, rồi A/B ở SNR 0/5/10/20 dB. Nếu thử [Facebook Denoiser](../wiki/facebook-denoiser.md) (causal, live, H=48 RTF 0.6–0.8 trên i5 4 nhân): repo là **CC-BY-NC**, và README không có số nào về chất lượng khử nhiễu hay ASR.[^denoiser]
2. **Mỗi session có state ASR/VAD riêng.** Không chia sẻ cache giữa người dùng. Giải phóng cache khi session đóng.
3. **Chỉ một owner quyết định turn commit**, là gateway hoặc tracker của framework. ASR server chỉ cung cấp tín hiệu. Nếu bật endpointing trong NeMo-Speech.cpp, coi đó là một tín hiệu, không để nó tự commit song song với Smart Turn.
4. **Telephony 8 kHz:** decode đúng rồi resample lên 16 kHz. Upsample không khôi phục được thông tin đã mất, nên phải có tập test 8 kHz riêng. NeMo-Speech.cpp gRPC/HTTP nhận PCM 8–96 kHz và tự resample, nhưng vẫn phải đo riêng audio 8 kHz.[^nemo-cfg]
5. **Giữ pre-roll 200–300 ms** trước điểm VAD bắt đầu, để không mất phụ âm đầu và thanh điệu (**Synthesis**, chưa đo).
6. **VAD:** [Silero VAD](../wiki/silero-vad.md) vẫn là mặc định có tài liệu tốt nhất. TEN VAD (hop 10/16 ms, thư viện nhỏ), FireRedVAD (có tách nhạc/hát), Frame-VAD MarbleNet v2.0 (6 ngôn ngữ, 20 ms/frame) và PulseVAD (2.118 tham số, cửa sổ 200 ms) đều **không có bằng chứng tiếng Việt hay tổng đài**. Chỉ đổi sau khi đo trên audio trong domain.[^silero][^vads]

### 7.2 Bốn mẫu ghép ASR

| Mẫu | Mô tả | Khi nào chọn | Chi phí |
|---|---|---|---|
| **A. Single-pass turn-final** | VAD/turn cắt lượt → Whisper turbo / Qwen3-ASR / PhoWhisper / ChunkFormer large / Gipformer 1.5 | MVP, không cần caption live; Gipformer khi chạy CPU/edge hoặc tổng đài | Không có partial. Latency = endpoint + decode |
| **B. Single-pass native streaming** | Nemotron 3.5 chunk 160–320 ms | Cần partial sớm, caption, speculative LLM | Accuracy thấp hơn Qwen offline (khác protocol) |
| **C. Single-pass buffered** | Qwen3-ASR qua vLLM streaming hoặc WLK windowed; Whisper qua WLK | Muốn chất lượng LLM-ASR mà vẫn có live text | Rollback/commit lag. Một phiên mỗi GPU với WLK windowed |
| **D. Two-pass selective** | Nemotron cho partial; cuối lượt Qwen3-ASR 1.7B, ChunkFormer RNNT large hoặc Gipformer 1.5 chạy lại trên turn audio để ra final | Số/tên/phủ định cần độ chính xác cao hơn B/C; Gipformer là lựa chọn final rẻ trên CPU | Thêm compute và lag. Phải reconcile revision |

**Biến thể C-QUAN (Synthesis):** QUAN chunked live → cùng weights full-context final, có/không KenLM. Đây là luồng partial/final với sentence recomputation, không phải mẫu B cache-aware và không bắt buộc có model thứ hai như D. Gateway phải chọn một endpoint owner; coi endpoint 0.8 s của runtime là policy cần tích hợp, không commit độc lập song song với Smart Turn.[^quan-live]

Không triển khai D ngay từ đầu nếu B hoặc C đã đạt accuracy domain. D có thể chỉ bật cho *critical spans* hoặc cho lượt có confidence thấp. **Final recognizer không phải ground truth** (**Synthesis**).[^vi-asr][^pipeline]

### 7.3 Mô hình transcript revision

Đây là schema đề xuất (**Synthesis**), không phải event schema của vendor nào:

```text
asr.partial(session_id, turn_id, revision, text, stable_prefix?)   # caption, speculation
asr.final  (session_id, turn_id, revision, text, model_id, language, quality_flags)
turn.commit(session_id, turn_id, revision)                         # một lần duy nhất
```

Map sang NeMo-Speech.cpp realtime WS: `conversation.item.input_audio_transcription.delta` → `asr.partial`; `.completed` → `asr.final`. `turn.commit` vẫn do gateway quyết định.[^nemo-api]

Quy tắc:

- **Partial** dùng cho caption và cho compute speculative (prefetch LLM). **Không được gây side effect.** Nếu revision đổi, hủy speculation.
- **Stable prefix** không phải confidence, cũng không phải final.
- **Final-pass** chạy lại trên turn audio đã giữ. Nó thay một revision chứ không ghép vào partial stream, để tránh token bị lặp.
- **Confidence** giữa các model không được calibrate với nhau. Thiếu confidence thì ghi là `unknown`. NeMo-Speech.cpp hiện trả 1.0 cho RNNT và beam, và 0.0 cho interim, nên những giá trị này không mang thông tin.[^nemo-cfg] Cộng đồng còn báo rằng confidence không đổi ngay cả khi accuracy sụp ở ngôn ngữ ít tài nguyên (**Reported/Unverified**).[^usable]
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
        text = postprocess(text, sess)                  # punctuation/ITN nếu model không có
        if passes_validity_gate(text, sess):            # hallucination, entity, ngôn ngữ
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

ASR latency thường bị che bởi thời gian chờ endpoint. Các điểm khởi đầu dưới đây cần tune (**Reported**):[^pipeline][^turn][^smart]

| Policy | Điểm bắt đầu |
|---|---|
| Silero VAD | Cửa sổ 512 sample / 32 ms @16 kHz, `threshold` 0.5 (0.6–0.7 khi ồn), `min_silence_duration_ms` 200–300, `speech_pad_ms` 100–200 |
| Có semantic turn ([Smart Turn v3.2](../wiki/smart-turn.md)) | Im lặng 200–300 ms, sau đó classifier chạy trên tối đa 8 s audio cuối của lượt (pad 0 ở đầu). Nếu user nói tiếp trước khi có kết quả, chạy lại trên **toàn bộ lượt** |
| Smart Turn tiếng Việt (vendor, 1.004 mẫu) | GPU fp32: accuracy 82.47%, FPR 9.56%, FNR 7.97%. CPU int8: 79.38%, FPR 8.86%, FNR 11.75%. Tiếng Việt **yếu nhất trong 23 ngôn ngữ**. CPU int8 cắt hụt (FNR) nhiều hơn, GPU ngắt nhầm (FPR) nhiều hơn |
| Không có semantic turn | Im lặng 500–800 ms |
| NeMo-Speech.cpp endpointing (nếu bật) | `stop_history_eou_ms` 800, token-silence hoặc VAD-driven |
| Fallback | 1.2–1.5 s im lặng là trần chờ |
| Nemotron | Chunk 160/320 ms, ép `vi-VN` |

Bẫy cần tránh:

- Endpoint quá gắt sẽ "nuốt" các từ ngắn, năng lượng thấp như "không" hay "đừng". Đây chính là những token quan trọng nhất trong luồng hủy hoặc sửa (**Reported**, cộng đồng).[^usable]
- FPR ~9–10% của Smart Turn nghĩa là khoảng 1/10 lần "hết lượt" kích hoạt khi user còn nói. Thay hoặc fine-tune (training script mở) nếu false-interruption tiếng Việt trên dữ liệu thật vượt 10% (**Reported** trigger).[^turn][^smart]
- LiveKit turn detector **không có vi**. TEN Turn Detection chỉ có en/zh. [Parakeet EOU](../wiki/parakeet-realtime-eou-120m-v1.md) chỉ hỗ trợ tiếng Anh. Không dùng EOU tiếng Anh để tuyên bố endpoint tiếng Việt.[^vi-asr][^turn]

### 7.6 Hotwords, dấu câu, ITN và chuẩn hóa

- **Context biasing (Reported):**[^qwen][^survey][^wlk][^nemo-cfg]

  | Model / runtime | Cơ chế |
  |---|---|
  | Qwen3-ASR | `prompt` tự do (`"Vocabulary: ..."`) |
  | Fun-ASR-MLT | `hotwords` + ITN |
  | Whisper | `hotwords` hoặc `initial_prompt` ngắn; WLK dùng `context` |
  | Nemotron 3.5 qua NeMo-Speech.cpp | `speech_contexts` / `prompt` (boost 10 cho một cụm). RNNT boost điển hình 2–3, trần 5 |
  | Confucius4-R2T2 | `context` hint (không có bằng chứng vi) |
  | ChunkFormer, Gipformer, ZipFormer, VietASR | Không mô tả trong các trang đã compile |

- **QUAN:** không có API hotword được mô tả trong concept; có thể thay KenLM word-level nhưng phải train LM và đo lại. Không coi LM là bảo đảm nhận đúng entity.[^quan-live]
- **Dấu câu và chữ hoa:**
  - QUAN xác định rõ lowercase/không punctuation/số dạng chữ. Có thể thử punctuation restoration trên final, nhưng phải đo latency và entity preservation; VietNormalizer viết→nói không giải quyết nhu cầu số dạng chữ→số (**Synthesis**).[^quan][^quan-live]
  - Nemotron 3.5, Qwen3-ASR và Whisper xuất văn bản có dấu câu. Các card chuyên Việt (Gipformer, ChunkFormer, ZipFormer) chấm điểm trên văn bản đã chuẩn hóa và không mô tả định dạng output. Phải kiểm output thật trước khi đưa cho LLM (**Synthesis**).[^gip15][^chunk]
  - Nếu output không có dấu câu: [Punctuation Restoration base 307M](../wiki/punctuation-restoration-base.md) (Apache-2.0, mmBERT, 88 ngôn ngữ) có dòng tiếng Việt trong bảng FLORES của tác giả: **F1 0.866 khi có chữ hoa, 0.791 khi lowercase**, so với punctuate-all 0.718 (**Reported**).[^punct][^punct-raw] Model này chỉ khôi phục `. , ? : -`, không khôi phục chữ hoa. `:` và `-` kém tin cậy. Có ONNX int8 641 MB. Chưa đo latency, và dữ liệu nói có disfluency khó hơn.
  - NeMo-Speech.cpp có PnC BERT riêng, nhưng tài liệu không nêu tiếng Việt.[^nemo-models]
- **ITN / chuẩn hóa:**
  - ITN Sparrowhawk của NeMo-Speech.cpp cần grammar theo ngôn ngữ. Chưa thấy grammar `vi` (**Synthesis**).[^nemo-cfg]
  - Phải có một bước chuẩn hóa tiếng Việt thống nhất trước khi so sánh model hay trích entity: Unicode NFC, vị trí dấu thanh, số ↔ chữ, tiền, ngày.
  - [VietNormalizer](../wiki/vietnormalizer.md) (MIT, thư viện chuẩn Python, pipeline 19 bước, ~0.6 ms/lần theo README) đi theo hướng **viết → nói** (số, ngày, tiền, đơn vị, viết tắt). Hướng này khớp với cách Gipformer chấm điểm (số chuyển sang dạng nói). Vì vậy có thể dùng nó làm normalizer chung cho cả reference lẫn hypothesis khi chấm WER. Đây là đề xuất, chưa thử. Bước lowercase của nó nằm trước bước tra từ điển (**Synthesis**).[^vnorm]
  - [ViSoNorm](../wiki/visonorm-visobert-normalizer.md) đi theo hướng informal → chuẩn (viết tắt, thiếu dấu), dùng cho text chat. Nó không phải hậu xử lý ASR, và không có benchmark hay license.[^visonorm]
- **Code-switch** Việt–Anh, tên thương hiệu, địa chỉ: phải có trong tập test, vì không model nào có số đo riêng cho trường hợp này.

---

## 8. Runtime và triển khai

### 8.1 Chọn runtime theo model

| Model | Runtime đề xuất | Lưu ý |
|---|---|---|
| Nemotron 3.5 | NeMo cache-aware script (tham chiếu); NeMo-Speech.cpp Q8 GGUF cho CPU/GPU (realtime WS, word boosting, endpointing); Transformers ≥5.13 | Benchmark CPU 27 ms/chunk là của model EN. Phải đo lại 3.5 vi. Ép `vi-VN`. `--q8-layout planar` chỉ cho CUDA concurrency cao |
| Qwen3-ASR | `qwen-asr` + vLLM (`qwen-asr-serve`); WLK `qwen3-streaming` windowed (`--language vi`); SGLang-Omni chỉ qua HTTP `/v1/audio/transcriptions` | Pin version và môi trường (vLLM xung đột `cu129` trong WLK). Đo cache và concurrency thật |
| Qwen3-ASR-1.7B GGUF | CrispASR (CSTR, có `-l vi`); transcribe.cpp (handy, không ép ngôn ngữ, offline); llama-server (ggml-org) | GGUF giữa các runtime không thay thế được cho nhau. CrispASR serialize inference trên một model; muốn song song thì dùng `--server-workers N` hoặc nhiều replica. Không hỗ trợ batched multi-stream |
| Whisper turbo / PhoWhisper | faster-whisper (CTranslate2) cho final; WLK SimulStreaming/LocalAgreement cho live | Không cắt audio mỗi 200 ms một cách độc lập rồi coi là transcript ổn định. Mỗi luồng chỉ có một segmentation owner |
| QUAN-Transcribe | Python `quan_transcribe.QuanTranscribe`; CLI `quan-transcribe --mic`; `LiveSession` cho audio live | CUDA bf16 / MPS fp32 ưu tiên cho live; CPU fp32 có thể lag. Encoder gated; chưa có server/concurrency contract được compile. `streaming=True` xử lý file, không phải push API live[^quan-live] |
| ChunkFormer | ONNX Runtime CPU/GPU, session state riêng | Dùng checkpoint streaming-trained với cấu hình chunk đã huấn luyện |
| Gipformer 1.5 / 68M | sherpa-onnx `OfflineRecognizer` (fp32/int8, `modified_beam_search`, 4 thread); icefall/k2 PyTorch (Linux CUDA) | Turn-final. Đặt `--quantize` tường minh. Chỉ nạp checkpoint tin cậy ở đường PyTorch. Cần `sherpa-onnx-core` từ sherpa-onnx 1.13 |
| VietASR zzasdf | icefall `pretrained.py`; gói sherpa-onnx `zipformer-vi-2025-04-20` | Nghiên cứu; license checkpoint chưa rõ |
| ZipFormer 30M | sherpa-onnx | Chỉ nghiên cứu (NC-ND) |

[^vi-asr][^runtime][^wlk][^deploy][^gip-repo][^cstr][^handy][^crisp-stream][^nemo-models]

**GGUF là container, không bảo đảm thay thế được cho nhau.** Ví dụ, layout tensor của NeMo-Speech.cpp khác layout của transcribe.cpp/Handy, và ba gói Qwen3-ASR-1.7B GGUF không chia sẻ bằng chứng file nào. Phải chọn artifact khớp với runtime trước khi so sánh quantization hay tốc độ. Quantization encoder có thể làm hỏng âm thầm (ví dụ Q4_K cũ của CSTR), nên test phải kiểm cả transcript rỗng và lặp, không chỉ WER trung bình. License MIT/Apache của runtime **không thay thế** license của weights (**Synthesis**).[^shortlist][^survey][^cstr]

### 8.2 Topology và capacity

- **Một model owner cho mỗi process.** Gateway workers không tự load weights. Tách environment ASR, TTS và ONNX để tránh xung đột torch/transformers/CUDA.[^pipeline]
- **Tách pool:** streaming ASR (nhạy latency) tách khỏi final-pass/turn-final (có thể batch, ví dụ `BatchedInferencePipeline` của faster-whisper, hoặc batching 5 ms của NeMo-Speech.cpp `serve`). Ưu tiên nhịp audio hơn throughput batch.[^pipeline][^nemo-cfg]
- **GPU dùng chung với LLM/TTS:** thử 0.6B trước. Muốn chạy Qwen 1.7B thì phải chừa chỗ cho encoder, cache, workspace và contention. Gipformer/ChunkFormer trên CPU giúp giải phóng GPU cho LLM/TTS (**Synthesis**).[^vi-asr]
- **Admission control:** đặt giới hạn số phiên, hàng đợi có giới hạn, backpressure/429, deadline theo phiên. Warmup xong mới báo readiness.
- **Bảo mật server:** NeMo-Speech.cpp và CrispASR đều hỗ trợ API key. Route health/playground của NeMo-Speech.cpp không cần xác thực, nên phải bind loopback hoặc đặt sau proxy.[^nemo-api][^crisp-stream]
- **VRAM tham khảo (Reported từ AI report, chưa đo):** Whisper turbo fp16 khoảng 2–3 GB. Trên GPU 12 GB thì dùng `int8_float16`.[^pipeline]

### 8.3 License: hard gate trước khi xét chất lượng

| Dùng thương mại được (đọc từ card, không phải tư vấn pháp lý) | Cần review | Tránh dùng thương mại / chưa rõ |
|---|---|---|
| Qwen3-ASR và các GGUF CSTR/handy (Apache-2.0), Whisper (MIT/Apache theo card), PhoWhisper (BSD-3), ChunkFormer RNNT large (CC-BY-4.0), Gipformer 68M/1.5 (MIT theo card), Cohere (Apache-2.0), Smart Turn (BSD-2), Silero (MIT), Punctuation Restoration (Apache-2.0), VietNormalizer (MIT) | QUAN-Transcribe (Gemma Terms of Use, gated EmbeddingGemma 2; chưa inspect terms đầy đủ/code license); Nemotron 3.5 (OpenMDW-1.1, card ghi ready for commercial use); Fun-ASR-MLT (Apache theo card, CrispASR ghi FunASR Model License v1.1); Gipformer (file LICENSE không có trong snapshot repo); Confucius4-R2T2 weights (NetEase license) | ChunkFormer CTC (CC-BY-NC), ZipFormer 30M (CC-BY-NC-ND), SeamlessM4T v2 (CC-BY-NC), Audio8 0.1B (CC-BY-NC), Facebook Denoiser (CC-BY-NC). Chưa rõ: VietASR zzasdf checkpoint, VietASR dangvansam, ggml-org GGUF (card không có trường license), ChunkFormer small streaming, Moonshine `-vi`, ViSoNorm |

[^survey][^vi-asr][^chunk][^zip][^gip15][^gip-repo][^zzasdf][^dvs][^ggml][^denoiser][^crisp][^quan]

Quyền dữ liệu train cũng là rủi ro riêng. Gipformer không mô tả dữ liệu train. VietASR dangvansam dùng audio YouTube, radio và tổng đài mà không nêu license hay consent.[^gip15][^dvs]

---

## 9. Cây quyết định gợi ý (Synthesis)

```text
Cần text khi user đang nói (caption, speculative LLM, barge-in thông minh)?
├─ Không ─► Mẫu A (turn-final)
│           ├─ GPU có sẵn, muốn ít tích hợp nhất ─► Whisper turbo `vi` + faster-whisper + filter
│           ├─ Ưu tiên chất lượng tiếng Việt chung ─► Qwen3-ASR 0.6B → 1.7B (vLLM)
│           ├─ CPU/edge, tổng đài hoặc domain hành chính/tài chính
│           │                                   ─► Gipformer 1.5 int8 (sherpa-onnx) + punctuation nếu cần
│           └─ Chuyên Việt, license mở, VIVOS/CMV tốt ─► ChunkFormer RNNT large (ONNX) / PhoWhisper medium
└─ Có ─► Chỉ chạy CPU/edge?
         ├─ Có ─► Nemotron 3.5 Q8 qua NeMo-Speech.cpp (đo lại!) ; fallback Gipformer/Whisper CT2 INT8 turn-final
         └─ Không ─► Mẫu B: Nemotron 3.5, chunk 160 → 320 → 560 ms (+ speech_contexts cho tên riêng)
                     └─ Lỗi số/tên/phủ định vẫn quá cao?
                        ├─ Chấp nhận buffering ─► Mẫu C: Qwen3-ASR streaming (vLLM / WLK windowed)
                        └─ Cần cả partial sớm lẫn final tốt ─► Mẫu D: Nemotron + final-pass
                                                              Qwen 1.7B (GPU) / Gipformer 1.5 hoặc ChunkFormer (CPU)
Mọi nhánh: lọc license weights trước; ép language = vi nếu model/runtime có hỗ trợ; chỉ hành động trên transcript đã commit.
```

---

**Nhánh thử thêm, không thay baseline:** nếu có GPU và chấp nhận Gemma terms, A/B QUAN cho turn-final hoặc live chunked partial → full-context final. Chỉ chọn sau khi đo ở cùng corpus và tải, đặc biệt câu dài và partial→final revision; không áp `language="vi"` máy móc vào API QUAN chuyên Việt chưa mô tả tham số này.[^quan][^quan-live]

## 10. Quy trình benchmark đề xuất

Mọi quyết định production phải dựa vào bước này, vì wiki chưa có số đo tiếng Việt cùng điều kiện, và mục 5.4 cho thấy số từ các nguồn khác nhau lệch nhau rất nhiều (**Synthesis**).[^vi-asr][^usable][^pipeline]

### 10.1 Corpus holdout tiếng Việt

- **Giọng:** Bắc, Trung, Nam. Có người già/trẻ em nếu domain cần. Bảng Gipformer tách riêng `tele-hard-north/middle/south`, và giọng miền Trung khó nhất với mọi model, nên tập test phải cân bằng vùng miền (**Reported**/Synthesis).[^gip15]
- **Nội dung:** tên riêng, tên domain, địa chỉ, số tiền, số điện thoại, ngày giờ, phủ định ("không", "đừng hủy"), code-switch Việt–Anh, lệnh rất ngắn.
- **Kênh:** mic 16 kHz, telephony 8 kHz, far-field.
- **Nhiễu:** quán café, xe máy, TV nền ở SNR 0/5/10/20 dB, chạy cả có và không có denoise. Thêm đoạn chỉ có silence hoặc nhạc để đo hallucination.
- **Tập công khai để đối chiếu:** VIVOS, Common Voice vi, FLEURS vi, VLSP2020, cùng 4 tập domain `vi-asr-tech/edu/finance/pubadmin` (public). Đây chỉ là điểm neo, không thay được dữ liệu domain của mình.[^gip15]
- **Quyền riêng tư:** dữ liệu phải opt-in, có access control và retention policy.

### 10.2 Chuẩn hóa và chấm điểm

- Dùng cùng ground truth và cùng normalizer cho mọi model: NFC, dấu thanh, số, punctuation. Một lựa chọn: lowercase + bỏ dấu câu + số → chữ (giống Gipformer), dùng VietNormalizer cho bước số → chữ. Phải ghi rõ normalizer khi báo số.
- Báo WER/CER, kèm **exact-match accuracy riêng** cho số, tên và phủ định. Không để normalizer che mất lỗi nghiêm trọng.
- Chạy mỗi model ở **đúng chế độ dự kiến dùng**: Nemotron ở 160/320/560 ms, Qwen ở policy buffered thật, Whisper/Gipformer per-turn.
- Với bản quantized (GGUF Q4/Q8, ONNX int8): thêm kiểm tra transcript rỗng, lặp và audio dài.

### 10.3 Metric latency và tải

| Nhóm | Metric |
|---|---|
| Live | first partial, **first stable text**, partial revision rate, word lag |
| Cuối lượt | endpoint → final P50/P95 |
| Tài nguyên | RTF (tự định nghĩa = compute/thời lượng), peak memory/session, cold vs warm |
| Tải | concurrency 1/4/8/16, sustained + simultaneous starts, queue delay, contention khi LLM/TTS chạy cùng GPU |
| Hành vi | tỷ lệ transcript bị lọc, hallucination trên silence/nhạc, false-cutoff của từ ngắn, false-interruption của turn detector |

### 10.4 Logging theo từng turn

Ghi một timeline duy nhất với timestamp căn chỉnh: `audio_in → partial → stable → endpoint → final → commit → LLM first token → TTS first byte`. Có timeline này mới biết chỗ "chậm" nằm ở ASR, endpoint hay playback. Cộng đồng báo từng mất khoảng một tháng tune nhầm stage vì không có timeline này (**Reported**).[^usable]

### 10.5 Ma trận thí nghiệm tối thiểu

| # | Cấu hình | Mục đích |
|---|---|---|
| 1 | Whisper turbo `vi`, faster-whisper fp16, turn-final + filter | Baseline |
| 2 | Nemotron 3.5 `vi-VN` @160 / 320 / 560 ms (có và không có `speech_contexts`) | Đường cong latency–accuracy thật; tác dụng của boosting |
| 3 | Qwen3-ASR 0.6B và 1.7B, turn-final | Trần chất lượng LLM-ASR |
| 4 | Qwen3-ASR streaming (vLLM hoặc WLK windowed) | Cái giá của buffering |
| 5 | ChunkFormer RNNT large, PhoWhisper medium, Gipformer 1.5 (fp32 và int8), turn-final | Đối chứng chuyên Việt; CPU/edge |
| 6 | Qwen3-ASR-1.7B GGUF Q8_0 / Q4_K trên CPU đích (CrispASR với `-l vi`) | Đường CPU cho LLM-ASR; parity so với #3 |
| 7 | Two-pass: #2 + final #3 hoặc #5 | Chỉ khi 2–4 chưa đạt mức lỗi entity |
| 8 | Hậu xử lý: punctuation restoration trên output của #5 (nếu thiếu dấu câu) | Chất lượng đầu vào cho LLM |
| 9 | QUAN greedy full-context, live 0.48 s → full-context final; tách thử KenLM bật/tắt | So với #2–5 trên cùng audio/normalizer; đo compute theo độ dài câu, stable-text và final revision; peak memory/concurrency trên GPU đích[^quan][^quan-live] |

**Gate riêng cho QUAN (Synthesis):** không loại câu có digits khỏi holdout entity-critical chỉ để khớp bảng LM; ghi rõ subset khi tái lập số vendor. Đo cả silence endpoint 0.8 s mặc định và policy gateway, câu dài/liên tục, code-switch, tổng đài 8 kHz, greedy so với LM, CPU beam-search bottleneck và punctuation hậu xử lý. Adapter QUAN phải dùng API thật (`accept`/`partial`/`flush`), không coi pseudo-code `push/finalize` ở 7.4 là code chạy được.[^quan][^quan-live]

Mỗi lần chỉ đổi một thành phần. Gate production gồm: availability, license, hiệu năng trên phần cứng đích, và **không hành động trên text chưa ổn định**.

---

## 11. Lộ trình

1. **Tuần đầu (MVP):** mẫu A với Whisper turbo `vi` và filter (hoặc Gipformer 1.5 nếu chỉ có CPU), cộng per-turn log và corpus nhỏ. Mục tiêu là có một vòng đo được.
2. **Beta:** A/B Nemotron (160/320/560 ms) với Qwen 0.6B/1.7B, đúng policy của từng model. Thêm ChunkFormer/PhoWhisper/Gipformer làm đối chứng chuyên Việt. Calibrate Smart Turn và endpoint trên từ ngắn tiếng Việt, và đo false-interruption.
3. **Production:** chọn B hoặc C. Chỉ thêm D khi mức lợi về entity error đáng với compute và latency bỏ thêm. Chuyển sang runtime native (NeMo-Speech.cpp, ONNX, GGUF) chỉ sau khi qua gate parity về output và latency.
4. **Dài hạn (tùy chọn):** nếu có nhiều audio domain không nhãn, cân nhắc hướng pseudo-label/SSL kiểu VietASR zzasdf hoặc fine-tune Nemotron/Qwen. Cần xác minh license checkpoint và quyền dữ liệu trước.

---

## 12. Mâu thuẫn còn mở và giới hạn

- **Chất lượng streaming của Qwen3-ASR:** vendor báo khoảng cách nhỏ (2.69 → 3.33 trên en/zh), trong khi một commenter nói Qwen stream kém hơn Parakeet. Chưa có phép đo chung nào giải quyết được.[^survey]
- **Số FLEURS-vi của Qwen3-ASR-1.7B:** 5.55 (paper), 6.15 (GGUF Q8_0), 10.13 (bảng Gipformer). Không chọn số nào. Khác normalizer, runtime và protocol.[^qwen][^handy][^gip15]
- **Smart Turn tiếng Việt:** AI report ghi 81.27% / FP 14.84% / FN 3.88%. Benchmark primary v3.2 ghi 82.47% / 9.56% / 7.97% (GPU) và 79.38% / 8.86% / 11.75% (CPU) trên cùng 1.004 mẫu. Chưa rõ số của report thuộc revision nào. Bài này dùng số v3.2. Ngoài ra, GitHub ghi tập train v3.2 còn card HF ghi v3.1.[^turn][^smart]
- **Hai card Gipformer** cho số khác nhau trên cùng hàng (gipformer-68M LSVSC 8.96/9.04; Zipformer-30M tele-medium 19.95/19.53).[^gip68]
- **Hàng "chunkformer-large-vie" trong bảng Gipformer** nhiều khả năng là bản CTC 110M (NC), không phải RNNT 113M. Đây là suy luận từ cột params và VIVOS.[^gip68]
- **Con số 16.44% WER của Whisper large-v3 gán cho VietASR:** không có trong README đã capture, còn Unverified.[^zzasdf]
- **License Fun-ASR-MLT-Nano:** card ghi Apache-2.0, README CrispASR ghi FunASR Model License v1.1.[^crisp]
- **Denoise trước ASR:** các nguồn mâu thuẫn và chưa có nghiên cứu tiếng Việt.[^noise]
- **ChunkFormer small streaming:** card trả HTTP 401. Không suy ra là checkpoint không tồn tại, nhưng size, license và WER của nó chưa xác định.[^chunk]
- **Whisper filter và ngưỡng thay thế:** phần lớn đến từ AI report thứ cấp, chưa được kiểm chứng ở nguồn gốc.[^pipeline]
- **QUAN:** code, weights, base encoder, KenLM, benchmark scripts/data và terms đầy đủ chưa được inspect trong nguồn compile; hành vi và tốc độ vẫn Reported. Chưa có cache-reuse/concurrency guarantee, matched streaming LM WER, kiểm chứng SOTA độc lập hay phép đo production. Full-context avg, filtered LM scores và streaming-valid score là các operating point khác nhau.[^quan][^quan-live]
- **Phạm vi khảo sát:** bản nền là snapshot wiki đến 2026-10-13, bổ sung QUAN ngày 2026-10-15; không refresh mọi model, không phải khảo sát toàn thị trường. API cloud/proprietary (Viettel, FPT, Google...) chưa được nghiên cứu, nên không xếp hạng. Các model chỉ thấy trong bảng bên thứ ba (PhoASR-whisper-small, parakeet-ctc-0.6b-Vietnamese, wav2vec2-base-vi) và Moonshine `-vi` chưa có concept.[^vi-asr]
- **Bài viết không chạy model nào.** Mọi số liệu là Reported. Mọi khuyến nghị là Synthesis và cần đo lại trên dữ liệu, phần cứng và SLA của bạn.

---

## Tài liệu tham chiếu

[^quan]: [QUAN-Transcribe-1.0](../wiki/quan-transcribe-1.0.md): Architecture, training, and output; Reported Vietnamese benchmark; Greedy, streaming, and optional LM evaluation; License and deployment relevance; Coverage and limits. Vendor-reported, chưa tái lập.
[^quan-live]: [QUAN-Transcribe Inference and Live Streaming](../wiki/quan-transcribe-inference.md): Installation and input/output; Streaming and live finalization contract; Optional four-gram KenLM; Relationships and coverage. Documentation synthesis; chưa chạy runtime.

[^vi-asr]: [Vietnamese Realtime ASR Selection](../wiki/vietnamese-realtime-asr-selection.md): Định nghĩa realtime; Shortlist và bằng chứng tiếng Việt; Qwen streaming/efficiency; Kiến trúc và hướng triển khai; Chọn runtime; Loại khỏi shortlist; Gate đánh giá.
[^survey]: [ASR/STT Model Survey](../wiki/asr-stt-model-survey.md): Master catalog (gồm VietASR dangvansam); Multilingual coverage (Vietnamese); Streaming and latency; Licensing; Serving runtimes; Community-reported field notes; Contradictions.
[^shortlist]: [Phân nhóm ASR/STT và shortlist realtime](../wiki/realtime-asr-selection.md): Nhóm và hướng phát triển; Size cho realtime; Shortlist triển khai thử; Runtime và diarization; Quyết định cho tiếng Việt.
[^pipeline]: [Vietnamese Speech Pipeline Design](../wiki/vietnamese-speech-pipeline-design.md): Kiến trúc tổng thể; VAD và turn detection; ASR tiếng Việt (ba mẫu ghép, cấu hình Whisper); Transcript revisions; Deploy tools; Release gates.
[^nemotron]: [Nemotron 3.5 ASR Streaming 0.6B](../wiki/nemotron-3.5-asr-streaming-0.6b.md): Architecture and I/O; Streaming operating points; Throughput; Vietnamese operating curve; Inference and usage.
[^qwen]: [Qwen3-ASR family](../wiki/qwen3-asr-family.md): Language and audio coverage; Inference and serving; Transformers-native usage; Primary-paper clarification (2026-10-07); Relationships (Confucius4-R2T2, các gói GGUF).
[^handy]: [handy-computer Qwen3-ASR-1.7B GGUF](../wiki/handy-computer-qwen3-asr-1.7b-gguf.md): Files and quantization; Runtime usage (không có language hint); Capability and metadata (`streaming: false`); Multilingual FLEURS (vi 6.15, Q8_0); Performance keys.
[^cstr]: [CSTR Qwen3-ASR-1.7B GGUF](../wiki/cstr-qwen3-asr-1.7b-gguf.md): Files and quantization; Rebake: audio encoder at Q8_0; Usage with CrispASR (`-l`); Performance (0.2x realtime, một clip).
[^ggml]: [ggml-org Qwen3-ASR-1.7B GGUF](../wiki/ggml-org-qwen3-asr-1.7b-gguf.md): Conversion and lineage (không có trường license); Usage (`llama-server -hf`).
[^chunk]: [ChunkFormer Vietnamese](../wiki/chunkformer-vietnamese.md): Checkpoint và kết quả; ONNX và online streaming; License và giới hạn triển khai.
[^pho]: [PhoWhisper](../wiki/phowhisper.md): Model và benchmark; Triển khai và quan hệ.
[^zip]: [ZipFormer 30M Vietnamese](../wiki/zipformer-30m-vietnamese.md): Identity và training (pointer `sherpa-onnx-zipformer-vi-2025-04-20` → `zzasdf/viet_iter3_pseudo_label`); Benchmark và speed; License và quan hệ.
[^gip15]: [Gipformer 1.5 68M RNNT](../wiki/gipformer1.5-68m-rnnt.md): Identity; Reported benchmark (16 tập, normalizer); Deployment relevance; Coverage and limits. Số vendor, một card.
[^gip68]: [Gipformer 68M RNNT](../wiki/gipformer-68m-rnnt.md): Reported benchmark (12 tập, rankings summary); Contradictions (số khác giữa hai card); Deployment relevance.
[^gip-repo]: [Gipformer Inference Repository](../wiki/gipformer-inference-repo.md): ONNX path (`OfflineRecognizer`, defaults); PyTorch path (`weights_only=False`, icefall không pin); Dependencies and licensing; Discrepancies (int8 vs fp32 default). Revision `0cac5b1`.
[^gip-raw]: Card Gipformer 1.5 ([raw/gipformer1.5-68M-rnnt.md](../raw/gipformer1.5-68M-rnnt.md)), bảng `Benchmark Results (WER%)` dòng 46–60, và card Gipformer 68M ([raw/gipformer-68M-rnnt.md](../raw/gipformer-68M-rnnt.md)), bảng dòng 43–55. Dùng cho các hàng comparator chưa có trong wiki: PhoASR-whisper-small, parakeet-ctc-0.6b-Vietnamese, wav2vec2-base-vi, Qwen3-ASR-0.6B, PhoWhisper small/medium, zipformer-rnnt 68M, và cột params "110M" của chunkformer-large-vie. Vendor-reported; đọc tĩnh có chủ đích.
[^zzasdf]: [VietASR (zzasdf, arXiv 2505.21527)](../wiki/zzasdf-viet-asr.md): Method; Artifacts and dependencies (checkpoint 70.000 giờ, Apache-2.0 code, license checkpoint không nêu); Disambiguation (16.44% Unverified; hàng "VietASR-zipformer" chưa đối chiếu).
[^zzasdf-proc]: [VietASR Training and Checkpoint Procedure](../wiki/zzasdf-viet-asr-procedure.md): Data preparation; Training stages; Checkpoint inference; Contradictions (layout dữ liệu có nhãn).
[^dvs]: [VietASR (dangvansam, QuartzNet)](../wiki/dangvansam-viet-asr.md): Model and training data; Setup and entry points; Contradictions (Python/torch).
[^tcpp]: [transcribe.cpp](../wiki/transcribe-cpp.md): bảng họ model (Moonshine gồm `moonshine-base-vi`, `moonshine-tiny-vi`; "no concept yet").
[^crisp]: [CrispASR ASR Backend Selection](../wiki/crispasr-asr-backend-selection.md): Vietnamese coverage (chỉ `fun-asr-mlt-nano`, FunASR Model License v1.1); Which backend to pick; CPU guidance (moonshine 16× RT); Feature-matrix caveats.
[^crisp-stream]: [CrispASR Streaming and HTTP Server](../wiki/crispasr-streaming-http-server.md): Streaming mechanisms named in the ASR table; HTTP server; Concurrency (serialize mặc định, `--server-workers`, không có batched multi-stream).
[^runtime]: [NeMo-Speech.cpp](../wiki/nemo-speech-cpp.md): Performance; Server, SDK, and source build.
[^nemo-cfg]: [NeMo-Speech.cpp ASR Configuration](../wiki/nemo-speech-asr-configuration.md): Word boosting (RNNT 2–3, trần 5); Endpointing (800 ms, token-silence / VAD-driven); Batching; Postprocessing (ITN Sparrowhawk theo thư mục ngôn ngữ, PnC); gRPC compatibility limits (LINEAR_PCM 8–96 kHz, confidence).
[^nemo-models]: [NeMo-Speech.cpp ASR Models and Quantization](../wiki/nemo-speech-asr-models.md): Model roster (`nemotron-3.5` mặc định); Quantization (`--outtype`, planar Q8); Companion models (Silero, Sortformer, PnC).
[^nemo-api]: [NeMo-Speech.cpp HTTP and Realtime API](../wiki/nemo-speech-http-api.md): Conventions (API key, route không xác thực); POST /v1/audio/transcriptions (`speech_contexts`, `prompt`); Realtime transcription WebSocket (events, `session.update`).
[^wlk]: [WhisperLiveKit](../wiki/whisperlivekit.md): Streaming policies; Backend notes (Qwen3 windowed/causal); Optional dependencies.
[^usable]: [Community-Reported Usable STT for Voice Agents](../wiki/community-usable-stt-voice-agents.md): Usable-text evaluation checklist; Failure order; Logging. Bằng chứng cộng đồng, Unverified.
[^turn]: [Turn Detection Models](../wiki/turn-detection-models.md): Comparison (Smart Turn, LiveKit, Namo, TEN); Operating practice (>10% replacement trigger); Contradictions (số AI report so với v3.2).
[^smart]: [Smart Turn v3.2](../wiki/smart-turn.md): Architecture and variants; Input and operating protocol (8 s, pad đầu, chạy lại cả lượt); Benchmark (bảng tiếng Việt 1.004 mẫu); Contradictions (dataset v3.2 so với v3.1).
[^silero]: [Silero VAD](../wiki/silero-vad.md): Streaming practice (threshold, `min_silence_duration_ms`, `speech_pad_ms`).
[^vads]: [TEN VAD](../wiki/ten-vad.md), [FireRedVAD](../wiki/firered-vad.md), [Frame-VAD Multilingual MarbleNet v2.0](../wiki/frame-vad-multilingual-marblenet-v2-0.md), [PulseVAD](../wiki/pulsevad.md): mục Coverage and limits của từng trang (không có bằng chứng tiếng Việt hay telephony).
[^noise]: [Speech Enhancement Before ASR](../wiki/speech-enhancement-before-asr.md): Evidence; Practice; Contradictions.
[^denoiser]: [Facebook Denoiser](../wiki/facebook-denoiser.md) (CC-BY-NC, không có metric chất lượng hay ASR) và [Denoiser Live Streaming](../wiki/denoiser-live-streaming.md) (bảng RTF CPU, stride 16 ms).
[^punct]: [Punctuation Restoration (base, 307M)](../wiki/punctuation-restoration-base.md): Scope and labels; Usage paths (ONNX int8 641 MB); Evaluation; Limitations.
[^punct-raw]: Card Punctuation Restoration ([raw/punctuation-restoration-base.md](../raw/punctuation-restoration-base.md)), bảng `Per language (FLORES)`, dòng `Vietnamese` (0.866 / 0.791 / punctuate-all 0.718 / xlm-roberta truecase 0.668). Self-reported; đọc tĩnh có chủ đích vì trang wiki không ghi dòng tiếng Việt.
[^vnorm]: [VietNormalizer](../wiki/vietnormalizer.md): pipeline 19 bước (lowercase trước bước từ điển); hiệu năng ~0.6 ms (README); MIT.
[^visonorm]: [ViSoNorm (visobert-normalizer)](../wiki/visonorm-visobert-normalizer.md): mô tả; quan hệ với VietNormalizer; không có benchmark hay license.
[^deploy]: [So sánh công cụ triển khai speech](../wiki/speech-deployment-tools-comparison.md): STT streaming; API server; Runtime native (GGUF không dùng chung giữa runtime).
