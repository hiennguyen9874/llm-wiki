---
type: Synthesis
title: So sánh benchmark Qwen3-ASR, Nemotron 3.5 và Cohere Transcribe
description: Đối chiếu benchmark Qwen3-ASR-1.7B, Nemotron 3.5 ASR Streaming 0.6B và Cohere Transcribe 03-2026 2B, tách English offline, Vietnamese WER, human preference, throughput và streaming protocol.
tags: [stt, asr, comparison, benchmark, vietnamese, streaming]
status: draft
created: 2026-10-15
generated: { by: llm-wiki-agent/1, at: 2026-10-15T10:21:49Z }
stale_after: 2027-10-06
sources:
  - id: cohere-release-blog
    resource: ../raw/cohere-transcribe-release-research-2026-10-15/README.md
    scope: ../raw/cohere-transcribe-release-research-2026-10-15/
    kind: documentation
    title: Cohere Transcribe release blog and benchmark figures
  - id: qwen-family
    resource: qwen3-asr-family.md
    kind: synthesis
    title: Qwen3-ASR family and primary-paper clarification
  - id: qwen-readme
    resource: ../raw/Qwen3-ASR-0.6B.md
    kind: documentation
    title: Qwen3-ASR family README
  - id: nemotron-card
    resource: ../raw/nemotron-3.5-asr-streaming-0.6b.md
    kind: documentation
    title: Nemotron 3.5 ASR model card
---

**Synthesis, chưa tái lập benchmark:** [Cohere 2B](cohere-transcribe-03-2026.md) có English offline average WER và throughput tốt hơn [Qwen 1.7B](qwen3-asr-family.md) trong snapshot của Cohere; Qwen có Vietnamese WER thấp hơn một chút trong biểu đồ aggregate của chính Cohere. [Nemotron 3.5 0.6B](nemotron-3.5-asr-streaming-0.6b.md) có bảng streaming chunk–WER và concurrency riêng, không có phép thử chung đủ để xếp hạng cả ba tại cùng latency. Các kết quả là **Reported** của vendor/author; đọc ảnh là **Observed** nội dung ảnh, không xác minh chất lượng model.[^cohere-release-blog][^qwen-family][^nemotron-card]

## English offline: cùng snapshot Cohere 26/03/2026

WER%, thấp hơn tốt hơn; bảng `Results` của blog (**Reported**). Nemotron 3.5 không có trong bảng này.[^cohere-release-blog]

| Dataset | Qwen3-ASR-1.7B | Cohere Transcribe 2B |
|---|---:|---:|
| Average | 5.76 | **5.42** |
| AMI | 10.56 | **8.15** |
| Earnings22 | **10.25** | 10.84 |
| GigaSpeech | **8.74** | 9.33 |
| LibriSpeech clean | 1.63 | **1.25** |
| LibriSpeech other | 3.40 | **2.37** |
| SPGISpeech | **2.84** | 3.08 |
| TEDLIUM | **2.28** | 2.49 |
| VoxPopuli | 6.35 | **5.87** |

**Synthesis:** Cohere giảm 0.34 điểm phần trăm average WER, khoảng 5.9% tương đối so với Qwen; mỗi model thắng 4/8 tập, nên không suy ra Cohere thắng mọi domain. Đây là so sánh trong cùng bảng công bố, không kiểm toán scorer hoặc tái lập protocol.[^cohere-release-blog]

Qwen `-hf` còn có snapshot 26/06/2026 với Mean WER **5.59%** và 7 tập hiển thị, không có TEDLIUM. Không ghép số này với Cohere 5.42% của tháng 3 để tính matched improvement; các cells và checkpoint/runtime snapshot khác nhau (**Reported**, giới hạn **Synthesis**).[^qwen-family]

## Vietnamese: tách aggregate khỏi FLEURS-only

### Cùng biểu đồ aggregate của Cohere

Blog Figure 4 (`figure-3.png`, nhóm `vi`) cho **ước lượng trực quan**, không có nhãn số chính xác (**Observed** bar heights; kết quả gốc **Reported**):[^cohere-release-blog]

| Model | Vietnamese aggregate WER, xấp xỉ |
|---|---:|
| Qwen3-ASR-1.7B | **≈8.3%** |
| Cohere Transcribe 2B | ≈8.8% |
| Nemotron 3.5 | Không có trong biểu đồ |

Caption nói trung bình trên FLEURS, Common Voice 17.0, MLS và Wenet khi phù hợp với từng ngôn ngữ; chưa xác lập tập con/trọng số riêng của tiếng Việt. **Synthesis:** Qwen nhỉnh hơn trong chart này, không có căn cứ gán ≈8.8% thành Cohere FLEURS-only hay coi đây là benchmark Vietnamese streaming.[^cohere-release-blog]

Toàn chart: Cohere thấp lỗi hơn Qwen ở de/fr/it/es/el/nl/pl/ar/ja; Qwen thấp hơn ở pt/vi/zh/ko. zh/ja/ko dùng CER, còn lại WER. Parakeet TDT v3 trong legend không phải Nemotron 3.5 (**Observed**, không xếp hạng ngoài phạm vi chart).[^cohere-release-blog]

### Các số FLEURS riêng, không matched streaming

Qwen paper Appendix A.2 báo cáo **FLEURS-vi offline 5.55%**, MLC-SLM-vi 14.92% WER cho 1.7B. Không có Vietnamese streaming WER tương ứng trong phần primary-paper đã compile (**Reported**).[^qwen-family]

Nemotron FLEURS-vi WER% theo chunk (**Reported**):[^nemotron-card]

| Chunk | LangID vi-VN cho trước | Auto |
|---|---:|---:|
| 80 ms | 13.41 | 13.59 |
| 160 ms | 12.87 | 13.02 |
| 320 ms | 12.29 | 12.40 |
| 560 ms | 11.78 | 12.02 |
| 1120 ms | 11.18 | 11.22 |

**Synthesis:** không so trực tiếp các số này với chart aggregate Cohere; cũng không dùng Qwen offline 5.55 vs Nemotron streaming 11.18 để tuyên bố thắng khi cùng latency. LangID, normalizer, context và commit policy chưa được khớp.[^cohere-release-blog][^qwen-family][^nemotron-card]

## Streaming English và chính sách context

Các số dưới đây là **Reported**, từ hai nguồn khác nhau, không matched protocol.[^qwen-readme][^nemotron-card]

| Model/chế độ | Chunk | FLEURS-English WER% |
|---|---:|---:|
| Qwen 1.7B offline | — | 3.35 |
| Qwen 1.7B streaming | 2000 ms | 4.02 |
| Nemotron 3.5, LangID cho trước | 80 ms | 9.43 |
| Nemotron 3.5, LangID cho trước | 160 ms | 8.88 |
| Nemotron 3.5, LangID cho trước | 320 ms | 8.27 |
| Nemotron 3.5, LangID cho trước | 560 ms | 7.99 |
| Nemotron 3.5, LangID cho trước | 1120 ms | 7.91 |

Qwen paper §4.5/Table 8 dùng **2-second chunks, 5-token fallback, bốn chunk cuối unfixed**. Nemotron có cache-aware streaming ở các chunk nhỏ hơn. Chunk size không phải end-to-end stable-text delay. **Synthesis:** các số Qwen thấp hơn tại cấu hình riêng không chứng minh thắng ở cùng latency; cần đo first stable text, revision và endpoint→final trên cùng audio/scorer.[^qwen-family][^nemotron-card]

Cohere blog mô tả offline throughput và serving variable-length inputs; không có native microphone-streaming benchmark tương ứng trong capture. Không suy ra causal streaming từ chunking hoặc batching (**Synthesis**).[^cohere-release-blog]

## Human preference và throughput

**Reported, đọc nhãn ảnh:** blog Figure 3 cho Cohere English win rate **55% vs Qwen**. Figure 5 cho tỷ lệ tương ứng: Ý 60%, Pháp 51%, Đức 44%, Tây Ban Nha 48%, Bồ Đào Nha 48%, Nhật 70%. Không có Vietnamese panel; cỡ mẫu, tie handling và khoảng tin cậy chưa rõ, không kết luận ý nghĩa thống kê (**Synthesis**).[^cohere-release-blog]

**Reported:** blog Figure 1 gắn nhãn **Cohere 525 RTFx vs Qwen 148 RTFx**, khoảng **3.55×** (phép chia **Synthesis**). Chưa xác lập hardware/batch/runtime parity; đây là offline throughput, không phải response latency.[^cohere-release-blog]

**Reported:** Nemotron card nêu một H100 sustains khoảng **240 realtime streams @80 ms**, **2400 @1120 ms**. Không đổi hai số này thành RTFx offline rồi xếp hạng với chart Cohere; đây là workload và đại lượng khác (**Synthesis**).[^nemotron-card]

Không gán claim **92 ms TTFT / 2000 audio-seconds/second** của Qwen **0.6B** sang model **1.7B**; đó còn là hai concurrency operating points khác nhau, không phải microphone latency (**Synthesis** từ primary-paper clarification).[^qwen-family]

## Chọn ứng viên và giới hạn

Khuyến nghị **Synthesis**, không production validation:[^cohere-release-blog][^qwen-family][^nemotron-card]

- **English file/batch:** thử Cohere trước nếu ưu tiên average accuracy/throughput; giữ Qwen trong A/B theo domain.
- **Vietnamese final transcript:** Qwen là baseline hợp lý từ chart aggregate; Cohere vẫn là challenger cần corpus/normalizer riêng, không loại vì thiếu FLEURS-only số chính xác.
- **Low-latency partial:** Nemotron là ứng viên có operating curve trực tiếp; thử 160–320 ms rồi đo quality/stable-text/concurrency trên hardware đích. Không có matched three-way winner.

## Relationships

- Uses [Cohere Transcribe](cohere-transcribe-03-2026.md) cho kiến trúc, training, serving, các chart và mâu thuẫn prose-versus-chart; blog claim “comparable/better” trên mọi ngôn ngữ không đủ để bỏ qua các nhóm Qwen thấp lỗi hơn (**Synthesis**).[^cohere-release-blog]
- Uses [Qwen3-ASR family](qwen3-asr-family.md) cho checkpoint/protocol và primary-paper clarification.[^qwen-family]
- Uses [Nemotron 3.5 ASR](nemotron-3.5-asr-streaming-0.6b.md) cho cache-aware streaming và FLEURS chunk curve.[^nemotron-card]
- Complements [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md): benchmark evidence phải được khớp protocol trước khi dùng làm deployment gate (**Synthesis** từ các giới hạn ở trên).

## Coverage

Release-blog body và năm PNG được đọc đầy đủ, lưu trong raw package với ledger/checksums. Qwen/Nemotron dùng compiled concepts và các bảng raw cụ thể nêu dưới đây; không refresh toàn bộ upstream. Không model execution, audio listening hay benchmark reproduction. Không đặt `verified`; `draft` vì còn thiếu exact chart data, protocol/hardware parity và matched three-way Vietnamese streaming evaluation.[^cohere-release-blog][^qwen-family][^qwen-readme][^nemotron-card]

[^cohere-release-blog]: [Cohere blog/figures capture](../raw/cohere-transcribe-release-research-2026-10-15/README.md) — `release-blog.txt`, `Results` English table dated 03.26.2026 and Figure 4 caption; `figure-1.png` (blog Figure 1, RTFx labels), `figure-2.png` (Figure 3, Qwen 55% row), `figure-3.png` (Figure 4, language groups/legend and approximate vi bar heights), `figure-4.png` (Figure 5, per-language numeric preference labels). No Nemotron series; capture/protocol limits in README.
[^qwen-family]: [Qwen3-ASR family](qwen3-asr-family.md) — `Benchmark highlights`, June 26 `-hf` table and snapshot warning; `Primary-paper clarification (2026-10-07)`, arXiv 2601.21337v2 §2.4/Table 2 efficiency, §4.5/Table 8 streaming, Appendix A.2(a/b) Vietnamese rows. Secondary compiled evidence with primary capture linked there; no independent verification.
[^qwen-readme]: [Qwen family README](../raw/Qwen3-ASR-0.6B.md) — `Evaluation` → `ASR Inference Mode Performance (WER ↓)`, Qwen3-ASR-1.7B offline/streaming rows, Fleurs-en 3.35/4.02.
[^nemotron-card]: [Nemotron 3.5 card](../raw/nemotron-3.5-asr-streaming-0.6b.md) — `Model Architecture` cache-aware description; `Performance` normalization note and transcription-ready FLEURS English/Vietnamese rows, five chunks, LangID/auto headers; `Throughput & Efficiency`, single-H100 240/2400 stream claims. Source assertions, not reproduced.
