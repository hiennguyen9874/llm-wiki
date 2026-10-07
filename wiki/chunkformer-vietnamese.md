---
type: Concept
title: ChunkFormer Vietnamese
description: Vietnamese ChunkFormer CTC 110M and RNNT 113M with reported Vietnamese WER, distinct weight licenses and ONNX streaming documentation that requires a streaming-trained checkpoint.
tags: [stt, asr, vietnamese, conformer, ctc, rnnt, onnx, streaming]
status: draft
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T03:56:09Z }
stale_after: 2027-10-07
sources:
  - id: vi-research
    resource: ../raw/vietnamese-asr-research-2026-10-07/README.md
    scope: ../raw/vietnamese-asr-research-2026-10-07/
    kind: documentation
    title: Vietnamese ASR primary-source research snapshots
---

ChunkFormer dùng masked chunk-wise Conformer, relative right context và masked batching cho long-form trên GPU ít bộ nhớ; có checkpoint CTC 110M và RNNT 113M chuyên tiếng Việt. Tài liệu ONNX tháng 6/2026 mô tả cache-aware online streaming nhưng ví dụ dùng checkpoint small streaming riêng: không chuyển WER của bản large long-form sang bản streaming (**Reported**; ranh giới benchmark là **Synthesis**).[^vi-research]

## Checkpoint và kết quả

Mọi số là tác giả báo cáo, chưa chạy; card chuẩn hóa thủ công số, chữ hoa và dấu câu. ID có prefix `khanhld/` (**Reported**).[^vi-research]

| Checkpoint | Params / data | VIVOS | Common Voice | VLSP2020 T1 | VLSP2020 T2 | License weights |
|---|---|---:|---:|---:|---:|---|
| `chunkformer-ctc-large-vie` | 110M / ~3000h | 4.18 | 6.66 | 14.09 | 25.81 (RNNT card) | CC-BY-NC-4.0 |
| `chunkformer-rnnt-large-vie` | 113M / ~5000h | 2.49 | 5.18 | 12.75 | 20.47 | CC-BY-4.0 |

RNNT card so sánh PhoWhisper-large ở 4.67 / 8.14 / 13.75 / 26.68 và Whisper-large-v3 ở 8.81 / 15.45 / 20.41 / 68.61; API Viettel/Google/FPT cũng có cột T1 nhưng version/date/configuration không rõ. Không dùng bảng này làm ranking API hiện tại (**Reported**, giới hạn **Synthesis**).[^vi-research]

Hai bản large minh họa `ChunkFormerModel.from_pretrained(...)`, `endless_decode` và `batch_decode` với `chunk_size=64`, left/right context=128. Đây là API đọc audio file, không chứng minh mic-to-partial latency (**Reported**; diễn giải **Synthesis**).[^vi-research]

## ONNX và online streaming

- Export full-context/limited-context và streaming là các đường riêng; graph gồm `encoder_full.onnx` hoặc `encoder_chunk.onnx`, CTC head, RNNT predictor/joint cùng vocab và config. Search loop ở host Python; CMVN baked vào encoder, input fbank 80 chiều (**Reported**).[^vi-research]
- Streaming export ví dụ `khanhld/chunkformer-rnnt-small-vie-stream-dct`, chunk=8, left=60, right=0. Configuration phải thuộc `dynamic_chunk_sizes` đã huấn luyện; không tự giảm right context của large rồi coi là model streaming tương đương (**Reported**; khuyến nghị **Synthesis**).[^vi-research]
- `OnnxAsrModel.stream()` tạo `StreamingSession`, giữ attention/conv cache, warm-up offset và RNNT LSTM/last-token state; `push_waveform` trả delta text, `push_features` chạy torch-free với numpy/ONNX Runtime, `finalize` flush tail (**Reported**).[^vi-research]
- CPU fp32 opset17 parity trên một sample được tác giả báo cáo: encoder_chunk small streaming max-diff 6.9e-6, transcript match. Không phải WER hoặc benchmark latency; chưa tái lập (**Reported**).[^vi-research]
- Chỉ export CTC/RNNT greedy; AED decoder, beam search và attention rescoring không được ONNX guide hỗ trợ (**Reported**).[^vi-research]

## License và giới hạn triển khai

README repo có badge CC-BY-4.0 nhưng CTC weights card là CC-BY-NC-4.0; RNNT large weights card là CC-BY-4.0. Đây là khác scope/checkpoint, không cho phép lấy badge repo thay license weights. License của small streaming chưa xác định (**Observed** fields; ý nghĩa triển khai **Synthesis**).[^vi-research]

Card small streaming mà ONNX guide nêu trả HTTP 401 trong phiên 2026-10-07. Không suy ra checkpoint không tồn tại; chưa xác định quyền truy cập, params, data, license hay Vietnamese streaming WER. Vì vậy family page giữ `draft` cho phần streaming (**Observed** fetch result, capability **Unverified**).[^vi-research]

## Relationships

- Compare [PhoWhisper](phowhisper.md) trên bảng WER của tác giả; ưu thế size/WER ở bản RNNT large chưa chứng minh ở streaming.[^vi-research]
- Used by [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md): ứng viên acoustic-first chuyên Việt/ONNX, sau gate availability/license/chunk-latency.[^vi-research]

## Coverage

Đọc toàn bộ repo README, CTC/RNNT cards và ONNX guide. Implementation, exporter, streaming runtime, parity scripts, training config/dataset.tsv, architecture image, paper, audio và weights đều chưa inspect; không cài/chạy model. Paper gốc arXiv 2502.14673 / ICASSP 2025 là pointer, không primary-paper inspection. Không xác nhận claim 16h, GPU memory table hoặc throughput production. Ledger đầy đủ tại package entry point.[^vi-research]

[^vi-research]: [Research capture](../raw/vietnamese-asr-research-2026-10-07/README.md) — `chunkformer-readme.md` Updates, Introduction, Key Features, Pretrained Models, Usage; `chunkformer-card.md` frontmatter/Model Description/Benchmark Results/Quick Usage; `chunkformer-rnnt-card.md` cùng sections; `chunkformer-onnx.md` Exported graphs, Export, Online (real-time) streaming, Verify parity, Notes / limitations. Unavailable small-card fetch recorded in entry-point ledger.
