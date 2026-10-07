---
type: Concept
title: PhoWhisper
description: Vietnamese-specialized Whisper family finetuned on 844 hours, with five checkpoint sizes, Vietnamese WER tables and BSD-3-Clause weights but no native streaming evidence.
tags: [stt, asr, vietnamese, whisper, offline]
status: stable
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

PhoWhisper của VinAI là họ Whisper chuyên tiếng Việt, finetune multilingual Whisper trên 844 giờ có nhiều accent tiếng Việt; có năm kích thước 39M–1.55B và license BSD-3-Clause. Đây là ứng viên nhận dạng cuối lượt hoặc buffered streaming, không có bằng chứng native streaming trong hai tài liệu đã đọc (**Reported** về model; vai trò triển khai là **Synthesis**).[^vi-research]

## Model và benchmark

WER (%) do tác giả báo cáo, chưa tái lập; không phải benchmark realtime. Các checkpoint có prefix `vinai/PhoWhisper-` (**Reported**).[^vi-research]

| Variant | Params | CMV-Vi | VIVOS | VLSP2020 T1 | VLSP2020 T2 |
|---|---:|---:|---:|---:|---:|
| tiny | 39M | 19.05 | 10.41 | 20.74 | 49.85 |
| base | 74M | 16.19 | 8.46 | 19.70 | 43.01 |
| small | 244M | 11.08 | 6.33 | 15.93 | 32.96 |
| medium | 769M | 8.27 | 4.97 | 14.12 | 26.85 |
| large | 1.55B | 8.14 | 4.67 | 13.75 | 26.68 |

Publication: Le, Nguyen và Nguyen, *PhoWhisper: Automatic Speech Recognition for Vietnamese*, ICLR 2024 Tiny Papers. README minh họa Transformers `pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small")` với audio 16 kHz (**Reported**).[^vi-research]

## Triển khai và quan hệ

- Uses kiến trúc [Whisper](whisper-large-v3.md); không suy ra PhoWhisper là finetune large-v3 từ tên family. Nguồn chỉ nói multilingual Whisper (**Synthesis**).[^vi-research]
- Compare [ChunkFormer Vietnamese](chunkformer-vietnamese.md): RNNT card có bảng đối chiếu trên cùng tên tập tiếng Việt; đó vẫn là benchmark tác giả, không independent reproduction.[^vi-research]
- Used by [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md): thử medium trước large nếu cân bằng tài nguyên; quality gain của large trên README nhỏ ở một số tập, không đồng nghĩa latency tương đương (**Synthesis**).[^vi-research]
- Đường CTranslate2/[Faster-Whisper](faster-whisper.md) cho PhoWhisper cần conversion và test riêng; chưa chứng minh wrapper compatibility hoặc stable partial cho checkpoint này (**Synthesis**).[^vi-research]

## Coverage và giới hạn

Hai card/README được đọc toàn bộ; package ledger tại nguồn. Paper, dữ liệu, weights và implementation chưa đọc/chạy; không xác nhận chống ồn production, code-switch, latency, conversion hay protocol chuẩn hóa WER. License model card được inspect, không phải thẩm định pháp lý. Không có `verified` metadata.[^vi-research]

[^vi-research]: [Research capture](../raw/vietnamese-asr-research-2026-10-07/README.md) — `phowhisper-card.md` frontmatter `license: bsd-3-clause`, `language: vi`, introduction và citation; `phowhisper-readme.md` introduction, `Model download & WER results`, `Run the model`.
