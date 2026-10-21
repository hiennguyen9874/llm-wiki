---
type: Concept
title: ZipFormer 30M Vietnamese
description: Vietnamese 30M ZipFormer-RNNT trained on 6000 hours with reported CPU throughput and Vietnamese WER, restrictive CC-BY-NC-ND weights and no established native streaming protocol.
tags: [stt, asr, vietnamese, zipformer, rnnt, cpu, edge]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-21T22:00:00Z }
stale_after: 2027-10-07
sources:
  - id: vi-research
    resource: ../raw/vietnamese-asr-research-2026-10-07/README.md
    scope: ../raw/vietnamese-asr-research-2026-10-07/
    kind: documentation
    title: Vietnamese ASR primary-source research snapshots
  - id: zip30-card
    resource: ../raw/Zipformer-30M-RNNT-6000h.md
    kind: documentation
    title: Vietnamese Speech-to-Text (ASR) — ZipFormer-30M-RNNT-6000h model card capture
---

`hynt/Zipformer-30M-RNNT-6000h` là model tiếng Việt ~30M dùng ZipFormer, RNNT loss, PyTorch/k2, train ~6000 giờ và được đóng gói ONNX bởi sherpa community. Card báo cáo tốc độ CPU rất nhanh, nhưng không công bố cache/lookahead/partial protocol, nên native streaming còn **Unverified**; license weights là CC-BY-NC-ND-4.0 (**Reported** model; license field **Observed**).[^vi-research]

## Identity và training

- `csukuangfj2/sherpa-onnx-zipformer-vi-30M-2026-02-09` pointer card chỉ rõ upstream hynt; không nhầm với `csukuangfj/sherpa-onnx-zipformer-vi-2025-04-20`, vốn trỏ `zzasdf/viet_iter3_pseudo_label` ~70k giờ (**Observed** docs).[^vi-research]
- Training data gồm VLSP2020/2021/2023, VLSP2023 pseudo-voting, FPT, VIET_BUD500, VietSpeech, FLEURS, VietMed, subsets GigaSpeech2-Vi/ViVoice/PhoAudioBook; author dùng OOV-aware augmentation và Whisper-refined transcripts (**Reported**).[^vi-research]

## Benchmark và speed

WER tác giả báo cáo, chưa tái lập; split hygiene/normalizer chưa inspect (**Reported**).[^vi-research]

| Test | ZipFormer-30M-6000h | ChunkFormer-110M-3000h | PhoWhisper-Large-1.5B-800h | VietASR-ZipFormer-68M-70,000h |
|---|---:|---:|---:|---:|
| VLSP2020-Test-T1 | 12.29 | 14.09 | 13.75 | 14.45 |
| VLSP2023-PublicTest | 10.40 | 16.15 | 16.83 | 14.70 |
| VLSP2023-PrivateTest | 11.10 | 17.12 | 17.10 | 15.07 |
| VLSP2025-PublicTest | 7.97 | 15.55 | 16.14 | 13.55 |
| VLSP2025-PrivateTest | 8.10 | 16.07 | 16.31 | 13.97 |
| GigaSpeech2-Test | 7.56 | 10.35 | 10.00 | 6.88 |

Đây là bảng `Evaluation Results` của card (lower is better); card in đậm cột 30M ở năm bộ VLSP và VietASR-68M ở GigaSpeech2 (**Reported**).[^zip30-card] Đọc bảng (**Synthesis**): 30M dẫn mọi cột đối thủ trên năm bộ VLSP và thua VietASR-68M (6.88) trên GigaSpeech2, dù VietASR dùng ~70,000 giờ so với 6000 giờ. Danh sách training data gồm VLSP2020/2021/2023, VLSP2023 pseudo-voting và subsets GigaSpeech2/FLEURS, còn card không nói split đánh giá có trùng hay không, nên các điểm này chưa chứng minh held-out (**Unverified**). Các đối thủ khác training size (3000/800/70,000 giờ) và card không nêu normalizer chung. Card bên thứ ba báo số khác cho cùng model, xem [Gipformer 68M RNNT](gipformer-68m-rnnt.md) (vlsp-t1 11.76) và [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md); tên test set và normalizer khác nhau, không chọn số nào.

## Tuyên bố cuộc thi VLSP 2025

Card nói tác giả đạt giải nhất VLSP 2025 khi train kiến trúc này trên 4,000 giờ dữ liệu, không phải checkpoint 6000 giờ này; chi tiết data, tối ưu, kiến trúc và đánh giá nằm ở paper ACL `aclanthology.org/2025.vlsp-1.4` (**Reported**; paper chưa fetch).[^zip30-card]

12s audio trong 0.3s trên CPU “Hugging Face Basic”, dưới 0.1s trên RTX3090 (**Reported**). Đây là throughput của file; không phải thời gian chờ stable partial, endpoint→final hoặc concurrency benchmark. RNNT head và “real-time” positioning không tự chứng minh encoder streaming (**Synthesis**).[^vi-research]

## License và quan hệ

- CC-BY-NC-ND-4.0 upstream weights không phù hợp làm lựa chọn mặc định cho thương mại hoặc finetune/redistribution; cần đọc terms và xin quyền nếu cần. Không thay license model bằng license runtime sherpa-onnx (**Synthesis**, không tư vấn pháp lý).[^vi-research]
- Sibling [ZipFormer 150M Vietnamese](zipformer-150m-vietnamese.md): the author's larger GPU-oriented CR-CTC + CTC + RNN-T checkpoint with the same 6000-hour data list, reporting lower WER on VLSP2023/2025 but higher on VLSP2020-T1 and about 3× slower file transcription (**Reported**; see that page).
- Compare [ChunkFormer Vietnamese](chunkformer-vietnamese.md): hai hướng acoustic-first nhỏ, nhưng khác training, splits và license; không xếp hạng bằng bảng tác giả riêng.[^vi-research]
- Used by [Sherpa Vietnamese ASR](sherpa-vietnamese-asr.md): that Windows app lists a Zipformer 30M checkpoint credited to this upstream as its small CPU mode, but does not restate the weight license (**Synthesis**, repo-id mapping).
- Used by [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) cho nhánh CPU nghiên cứu, không baseline native-streaming đã xác nhận.[^vi-research]

## Coverage và giới hạn

Đọc toàn bộ upstream card và hai pointer cards. Paper ACL 2025.vlsp-1.4, runtime guides, ONNX/TorchScript weights, demo, datasets, QR/donation asset chưa fetch; không chạy audio. Không kết luận model offline-only, chỉ chưa có streaming evidence trong nguồn đã inspect. Package ledger lưu thêm multilingual streaming Zipformer pointer còn thiếu protocol/license/WER.[^vi-research]

`raw/Zipformer-30M-RNNT-6000h.md` là bản sao byte-identical (SHA-256 `fa54d022…f70b`, 4184 bytes) của `zipformer-30m-upstream.md` trong package (**Observed**, diff + checksums.json); đã đọc tĩnh toàn bộ và dùng để bổ sung bảng so sánh đầy đủ và tuyên bố VLSP 2025. Card còn khai PyTorch + k2, demo Hugging Face Space (`hynt/k2-automatic-speech-recognition-demo`, chưa fetch), hướng dẫn chạy qua sherpa (Torch JIT và ONNX) và định vị “callbot/embedded”. Không tải weights, không chạy audio; ảnh `qr.jpg` (donation) loại vì không mang kiến thức kỹ thuật.[^zip30-card]

[^vi-research]: [Research capture](../raw/vietnamese-asr-research-2026-10-07/README.md) — `zipformer-30m-upstream.md` frontmatter license, Model Architecture and Training strategy, Training Data, Evaluation Results, Inference Speed, How to Run; `zipformer-30m-card.md` và `zipformer-vi-card.md` Introduction.
[^zip30-card]: [ZipFormer-30M-RNNT-6000h card](../raw/Zipformer-30M-RNNT-6000h.md) — frontmatter `license`; `Evaluation Results`; `Achievements`; `Inference Speed`; `How to Run This Model`; `Summary`.
