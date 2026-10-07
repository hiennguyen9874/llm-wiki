---
type: Concept
title: ZipFormer 30M Vietnamese
description: Vietnamese 30M ZipFormer-RNNT trained on 6000 hours with reported CPU throughput and Vietnamese WER, restrictive CC-BY-NC-ND weights and no established native streaming protocol.
tags: [stt, asr, vietnamese, zipformer, rnnt, cpu, edge]
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

`hynt/Zipformer-30M-RNNT-6000h` là model tiếng Việt ~30M dùng ZipFormer, RNNT loss, PyTorch/k2, train ~6000 giờ và được đóng gói ONNX bởi sherpa community. Card báo cáo tốc độ CPU rất nhanh, nhưng không công bố cache/lookahead/partial protocol, nên native streaming còn **Unverified**; license weights là CC-BY-NC-ND-4.0 (**Reported** model; license field **Observed**).[^vi-research]

## Identity và training

- `csukuangfj2/sherpa-onnx-zipformer-vi-30M-2026-02-09` pointer card chỉ rõ upstream hynt; không nhầm với `csukuangfj/sherpa-onnx-zipformer-vi-2025-04-20`, vốn trỏ `zzasdf/viet_iter3_pseudo_label` ~70k giờ (**Observed** docs).[^vi-research]
- Training data gồm VLSP2020/2021/2023, VLSP2023 pseudo-voting, FPT, VIET_BUD500, VietSpeech, FLEURS, VietMed, subsets GigaSpeech2-Vi/ViVoice/PhoAudioBook; author dùng OOV-aware augmentation và Whisper-refined transcripts (**Reported**).[^vi-research]

## Benchmark và speed

WER tác giả báo cáo, chưa tái lập; split hygiene/normalizer chưa inspect (**Reported**).[^vi-research]

| Test | WER % |
|---|---:|
| VLSP2020 T1 | 12.29 |
| VLSP2023 public / private | 10.40 / 11.10 |
| VLSP2025 public / private | 7.97 / 8.10 |
| GigaSpeech2 test | 7.56 |

12s audio trong 0.3s trên CPU “Hugging Face Basic”, dưới 0.1s trên RTX3090 (**Reported**). Đây là throughput của file; không phải thời gian chờ stable partial, endpoint→final hoặc concurrency benchmark. RNNT head và “real-time” positioning không tự chứng minh encoder streaming (**Synthesis**).[^vi-research]

## License và quan hệ

- CC-BY-NC-ND-4.0 upstream weights không phù hợp làm lựa chọn mặc định cho thương mại hoặc finetune/redistribution; cần đọc terms và xin quyền nếu cần. Không thay license model bằng license runtime sherpa-onnx (**Synthesis**, không tư vấn pháp lý).[^vi-research]
- Compare [ChunkFormer Vietnamese](chunkformer-vietnamese.md): hai hướng acoustic-first nhỏ, nhưng khác training, splits và license; không xếp hạng bằng bảng tác giả riêng.[^vi-research]
- Used by [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) cho nhánh CPU nghiên cứu, không baseline native-streaming đã xác nhận.[^vi-research]

## Coverage và giới hạn

Đọc toàn bộ upstream card và hai pointer cards. Paper ACL 2025.vlsp-1.4, runtime guides, ONNX/TorchScript weights, demo, datasets, QR/donation asset chưa fetch; không chạy audio. Không kết luận model offline-only, chỉ chưa có streaming evidence trong nguồn đã inspect. Package ledger lưu thêm multilingual streaming Zipformer pointer còn thiếu protocol/license/WER.[^vi-research]

[^vi-research]: [Research capture](../raw/vietnamese-asr-research-2026-10-07/README.md) — `zipformer-30m-upstream.md` frontmatter license, Model Architecture and Training strategy, Training Data, Evaluation Results, Inference Speed, How to Run; `zipformer-30m-card.md` và `zipformer-vi-card.md` Introduction.
