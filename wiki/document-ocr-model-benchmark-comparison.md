---
type: Synthesis
title: Document OCR model benchmark comparison
description: So sánh theo từng dataset các kết quả benchmark được báo cáo của Chandra OCR 2, MinerU2.5-Pro, Surya OCR 2.5, MonkeyOCRv2-B-Parsing, OvisOCR3, PaddleOCR-VL-1.6, Infinity-Parser2-Pro, LightOnOCR-3, TeleOCR và MiniCPM-OCR 1.0.
tags: [ml, ocr, document-parsing, benchmarks, comparison]
status: draft
created: 2026-10-30
generated: { by: llm-wiki-agent/1, at: 2026-10-30T03:07:00Z }
stale_after: 2027-01-30
sources:
  - id: chandra2-card
    resource: ../raw/chandra-ocr-2.md
    kind: model-card
    title: Chandra OCR 2 model card
  - id: chandra2-bench-img
    resource: ../raw/ocr-benchmark-assets-2026-10-30/chandra-bench.png
    kind: figure
    title: Chandra OCR 2 olmOCR benchmark chart
  - id: chandra2-full-bench
    resource: ../raw/ocr-benchmark-assets-2026-10-30/chandra-full-benchmarks.md
    kind: article
    title: Chandra 2 full 90-language benchmark
  - id: surya25-card
    resource: ../raw/surya-ocr-2.5-hf.md
    kind: model-card
    title: Surya OCR 2.5 model card
  - id: surya25-size-chart
    resource: ../raw/ocr-benchmark-assets-2026-10-30/surya-opb_size_chart.png
    kind: figure
    title: OmniParseBench against model size chart
  - id: opb-card
    resource: ../raw/ocr-benchmark-assets-2026-10-30/omniparsebench-card.md
    kind: dataset-card
    title: Omni Parse Bench dataset card
  - id: mineru-pro-2604-card
    resource: ../raw/MinerU2.5-Pro-2604-1.2B.md
    kind: model-card
    title: MinerU2.5-Pro-2604-1.2B model card
  - id: mineru-pro-2605-card
    resource: ../raw/MinerU2.5-Pro-2605-1.2B.md
    kind: model-card
    title: MinerU2.5-Pro-2605-1.2B model card
  - id: mineru-pro-leaderboard
    resource: ../raw/ocr-benchmark-assets-2026-10-30/mineru-leaderboard.png
    kind: figure
    title: MinerU2.5-Pro OmniDocBench v1.6 leaderboard figure
  - id: mineru-pro-end2end
    resource: ../raw/ocr-benchmark-assets-2026-10-30/mineru-end2end.png
    kind: figure
    title: MinerU2.5-Pro OmniDocBench v1.6 end-to-end table
  - id: mineru-pro-table-img
    resource: ../raw/ocr-benchmark-assets-2026-10-30/mineru-table_performance.png
    kind: figure
    title: MinerU2.5-Pro table-recognition table
  - id: monkeyocrv2-paper
    resource: ../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex
    kind: paper
    title: "MonkeyOCRv2: A Visual-Text Foundation Model for Document AI"
  - id: mdpbench-readme
    resource: ../raw/ocr-benchmark-assets-2026-10-30/mdpbench-readme.md
    kind: article
    title: MDPBench README (main results)
  - id: ovisocr3-card
    resource: ../raw/ATH-MaaS-OvisOCR3.md
    kind: model-card
    title: OvisOCR3 model card
  - id: ovisocr3-overview-img
    resource: ../raw/ocr-benchmark-assets-2026-10-30/ovisocr3_performance_overview.png
    kind: figure
    title: OvisOCR3 performance overview figure
  - id: paddle16-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    kind: paper
    title: PaddleOCR-VL-1.6 technical report
  - id: infinity2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    kind: paper
    title: Infinity-Parser2 Technical Report
  - id: infinity2-card
    resource: ../raw/Infinity-Parser2-Pro.md
    kind: model-card
    title: Infinity-Parser2-Pro model card
  - id: infinity2-olmocr-img
    resource: ../raw/ocr-benchmark-assets-2026-10-30/infinity-olmocr_bench_perf.png
    kind: figure
    title: Infinity-Parser2 olmOCR-bench chart
  - id: lightonocr3-blog
    resource: ../raw/lightonocr-3/index.md
    scope: ../raw/lightonocr-3/
    kind: article
    title: "LightOnOCR-3: High-Performance OCR and Layout Extraction in One Model"
  - id: teleocr-v3
    resource: ../raw/arXiv-2608.12898v3-TeleOCR/main.tex
    scope: ../raw/arXiv-2608.12898v3-TeleOCR/
    kind: paper
    revision: arXiv:2608.12898v3
    title: "TeleOCR: Navigating Document Parsing Across Digital and Camera-Captured Documents"
  - id: minicpm-repo
    resource: ../raw/MiniCPM-OCR/README.md
    scope: ../raw/MiniCPM-OCR/
    kind: code
    revision: b33b474
    title: MiniCPM-OCR repository
  - id: xiaomi-card
    resource: ../raw/Xiaomi-OCR-0.md
    kind: model-card
    title: Xiaomi-OCR-0 model card
---

# Document OCR model benchmark comparison

Trang này gom **mọi kết quả benchmark tìm được trong wiki và `raw/`** cho 10 mô hình document OCR, rồi so sánh **theo từng dataset**: [Chandra OCR 2](chandra-ocr-2.md), [MinerU2.5-Pro](mineru2-5-pro.md), [Surya OCR 2.5](surya-ocr-2-5.md), MonkeyOCRv2-B-Parsing ([MonkeyOCRv2](monkeyocrv2.md)), [OvisOCR3](ovisocr3.md), [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), Infinity-Parser2-Pro ([Infinity-Parser2](infinity-parser2.md)), [LightOnOCR-3](lightonocr-3.md) (4B, kèm 0.8B/1B khi đó là biến thể duy nhất được đo), [TeleOCR](teleocr.md) và [MiniCPM-OCR 1.0](minicpm-ocr-1-0.md). **Synthesis:** không có mô hình nào dẫn đầu mọi dataset; thứ hạng đảo chiều giữa họ benchmark kiểu OmniDocBench (edit distance/TEDS/CDM) và họ benchmark unit-test (olmOCR-Bench, OmniParseBench, ParseBench). Mọi con số là **Reported** (tác giả/vendor tự chạy hoặc chép lại), không được chạy lại ở đây.

## Phương pháp và quy ước

- Mỗi ô ghi nguồn đo: **own** = báo cáo của chính tác giả mô hình; **[M]** = bảng của MiniCPM-OCR; **[T]** = bài TeleOCR; **[O3]** = card OvisOCR3; **[P]** = báo cáo PaddleOCR-VL-1.6; **[OPB]** = dataset card OmniParseBench do Datalab chạy; **[L]** = blog LightOnOCR-3; **[I]** = báo cáo Infinity-Parser2.
- Số từ ảnh đã được tải về `raw/ocr-benchmark-assets-2026-10-30/` (manifest kèm URL, thời điểm tải, SHA-256) và đọc trực tiếp; các ảnh đã có sẵn trong gói nguồn (MiniCPM, LightOnOCR-3, TeleOCR) cũng được đọc lại để đối chiếu với bảng text.
- "—" nghĩa là **không tìm thấy kết quả**, không phải điểm 0. Điểm giữa các dataset khác thang, không được cộng hay so trực tiếp.
- Trang này giữ các bảng headline. Component vectors (PureDocBench theo track, MinerU Hard, crop-level), benchmark chuyên biệt/in-house, điều kiện throughput chi tiết và coverage ledger nằm ở [OCR ten-model benchmark comparison: supplementary evidence](ocr-ten-model-benchmark-comparison.md).

## Ma trận phủ benchmark (overall, cao hơn là tốt hơn)

| Mô hình | OmniDocBench v1.6 | Real5 | Wild (giao thức M / T) | MDPBench | PureDocBench | olmOCR-Bench | OmniParseBench | ParseBench |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Chandra OCR 2 | 92.27 [M] | 88.74 [M] | 89.08 / — | 79.7 | — | 85.8 own | **90.1** | 70.1 |
| MinerU2.5-Pro | 95.69 own; 95.75 [P][T][M] | 88.96 [P]; 88.94 [M] | 90.06 / 87.33 | 71.0 | 70.07 [T] | 79.5 [M] | 87.1 | — |
| Surya OCR 2.5 | — | — | — | — | — | 83.7 own | 85.9 | — |
| MonkeyOCRv2-B-Parsing | 91.57 own | 89.22 [O3] | — | 83.3 | 64.91 [O3] | — | — | — |
| OvisOCR3 | 96.74 own | 93.63 own | — | **88.8** own | **82.31** own | — | — | — |
| PaddleOCR-VL-1.6 | 96.33 own; 96.34 [O3][M] | 93.19 own | 91.49 / 87.36 | 78.9; 75.0 (MonkeyOCRv2) | 65.44 [O3] | 80.2 [M] | 78.7 | — |
| Infinity-Parser2-Pro | 93.95 own | — | — | — | — | **87.6** own | 87.0 | 74.3 |
| LightOnOCR-3 (4B) | — (1B: 89.87 [M]) | — (1B: 83.62 [M]) | — (1B: 84.36 / —) | — | — | 86.3 [L] | 82.9 | **75.1** [L] |
| TeleOCR | **96.87** own; 96.91 [M] | 90.72 [M] | 90.71 / 88.53 own | — | 78.41 own (TB 3 track) | 77.1 [M] | — | — |
| MiniCPM-OCR 1.0 | 96.51 own | **93.68** own | **92.39** own / — | — | — | 82.7 own | 83.2 | — |

Nguồn: [^minicpm-repo][^teleocr-v3][^ovisocr3-card][^paddle16-report][^opb-card][^lightonocr3-blog][^infinity2-report][^mdpbench-readme][^mineru-pro-2604-card][^monkeyocrv2-paper][^chandra2-card][^surya25-card]

## OmniDocBench v1.6 (Full)

Overall = trung bình của `(1 − TextEdit)×100`, Formula CDM và Table TEDS; reading order và TEDS-S báo riêng.[^teleocr-v3][^minicpm-repo]

| Mô hình (nguồn) | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| TeleOCR (own) | **96.87** | **0.027** | 96.36 | **97.05** | **98.52** | 0.122 |
| OvisOCR3 (own, chỉ overall) | 96.74 | — | — | — | — | — |
| MiniCPM-OCR 1.0 (own, chỉ overall) | 96.51 | — | — | — | — | — |
| PaddleOCR-VL-1.6 (own) | 96.33 | 0.033 | **97.49** | 94.76 | 97.11 | 0.127 |
| MinerU2.5-Pro (bảng [P]/[T]/MonkeyOCRv2) | 95.75 | 0.036 | 97.45 | 93.42 | 95.92 | **0.120** |
| MinerU2.5-Pro-2605 (own card) | 95.72 | 0.036 | 97.15 | 93.62 | 96.01 | 0.123 |
| MinerU2.5-Pro-2604 (own card/ảnh) | 95.69 | 0.036 | 97.29 | 93.42 | 95.92 | 0.120 |
| Infinity-Parser2-Pro (own, chỉ overall) | 93.95 | — | — | — | — | — |
| Chandra OCR 2 ([M], chỉ overall) | 92.27 | — | — | — | — | — |
| MonkeyOCRv2-B-Parsing (own) | 91.57 | 0.053 | 91.83 | 88.24 | 91.38 | 0.131 |
| LightOnOCR-3-1B ([M], chỉ overall) | 89.87 | — | — | — | — | — |

Ảnh leaderboard của MinerU còn cho tập con: MinerU2.5-Pro Base **96.12**, Hard **94.08**; single-task (Full) text 1−edit 96.37, formula CDM 97.29, table TEDS 93.42, reading order 1−edit 87.97.[^mineru-pro-leaderboard][^mineru-pro-end2end][^mineru-pro-2605-card] Infinity-Parser2-Flash đạt 91.98.[^infinity2-report] Surya OCR 2.5 không có kết quả OmniDocBench.

**Synthesis:** TeleOCR, OvisOCR3, MiniCPM-OCR 1.0 và PaddleOCR-VL-1.6 nằm trong khoảng 96.3–96.9 — chênh lệch nhỏ hơn mức trôi giữa các nguồn (ví dụ TeleOCR 96.87 vs 96.91, MinerU2.5-Pro 95.69 vs 95.75), nên không đủ để xếp hạng chắc chắn trong cụm này. Reading order tốt nhất thuộc MinerU2.5-Pro (0.120), không phải mô hình có overall cao nhất.

## Real5-OmniDocBench

Năm điều kiện vật lý (scan, warp, screen photo, illumination, skew) trên annotation OmniDocBench v1.5.[^paddle16-report]

| Mô hình | Overall ↑ | Scan | Warp | Screen | Illum. | Skew | Nguồn |
|---|---:|---:|---:|---:|---:|---:|---|
| MiniCPM-OCR 1.0 | **93.68** | — | — | — | — | — | own [M] |
| OvisOCR3 | 93.63 | — | — | — | — | — | own |
| PaddleOCR-VL-1.6 | 93.19 | **94.74** | **92.48** | **92.78** | **93.28** | **92.66** | own [P] |
| TeleOCR | 90.72 | — | — | — | — | — | [M] |
| MonkeyOCRv2-B-Parsing | 89.22 | — | — | — | — | — | [O3] |
| MinerU2.5-Pro | 88.96 (88.94 ở [M] và Xiaomi) | 92.11 | 88.72 | 91.29 | 91.42 | 81.26 | [P] |
| Chandra OCR 2 | 88.74 | — | — | — | — | — | [M] |
| LightOnOCR-3-1B | 83.62 | — | — | — | — | — | [M] |

[^paddle16-report][^minicpm-repo][^ovisocr3-card][^xiaomi-card] MiniCPM ghi rõ Real5 = trung bình đều năm kịch bản, mỗi kịch bản 1,355 trang.[^minicpm-repo] **Synthesis:** skew là điểm phân hóa lớn nhất (MinerU2.5-Pro 81.26 so với 92.66 của PaddleOCR-VL-1.6).

## Wild-OmniDocBench — hai giao thức không gộp được

- **Giao thức [M]** (scorer v1.6, GT v1.5 tương ứng, xoay ảnh bằng SDK MiniCPM trước khi chấm): MiniCPM-OCR 1.0 **92.39**, PaddleOCR-VL-1.6 91.49, TeleOCR 90.71, MinerU2.5-Pro 90.06, Chandra OCR 2 89.08, LightOnOCR-3-1B 84.36.[^minicpm-repo]
- **Giao thức [T]** (Wild OmniDocBench v1.5 Full, `quick_match`), thứ tự text edit ↓ / CDM ↑ / TEDS ↑ / TEDS-S ↑ / order edit ↓: TeleOCR **88.53** (**0.1173** / 88.26 / **89.05** / **92.14** / **0.2011**), PaddleOCR-VL-1.6 87.36 (0.1369 / 88.42 / 85.76 / 90.14 / 0.2057), MinerU2.5-Pro 87.33 (0.1362 / **90.15** / 85.46 / 90.12 / 0.2013); card Xiaomi-OCR-0 chép lại đúng các overall này.[^teleocr-v3][^xiaomi-card]

Cùng một mô hình chênh 2–3 điểm giữa hai giao thức (TeleOCR 90.71 vs 88.53), nên chỉ so trong cùng một dòng giao thức.

## MDPBench (17 ngôn ngữ, digital + photographed)

Bảng chính thức trong README MDPBench (bản tải 2026-10-30):[^mdpbench-readme]

| Mô hình | All ↑ | Digital | Photo | Latin avg | Non-Latin avg | VI | ZH | Private |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MonkeyOCRv2-B-Parsing | **83.3** | 88.1 | **81.7** | **84.2** | **82.1** | 83.2 | 83.6 | **84.7** |
| Chandra OCR 2 | 79.7 | 87.8 | 77.1 | 82.7 | 76.4 | **85.6** | 73.8 | 82.4 |
| PaddleOCR-VL-1.6 | 78.9 | 87.1 | 76.3 | 81.4 | 76.1 | 80.9 | **85.9** | 83.0 |
| MinerU2.5-Pro | 71.0 | 86.2 | 66.1 | 74.6 | 67.0 | 74.2 | 76.5 | 74.3 |

- **OvisOCR3** tự báo cáo **88.8** trong card của nó, nhưng không xuất hiện trong bảng README đã tải và card không nêu split/giao thức.[^ovisocr3-card] So với hàng cao nhất của README (Gemini-3-pro-preview 86.4) là phép so **giữa hai nguồn**; trong bảng của chính card OvisOCR3, hàng 86.40 là Qwen3.8-Max, không có Gemini.[^ovisocr3-card][^mdpbench-readme]
- Sáu mô hình còn lại không có kết quả MDPBench (LightOnOCR chỉ có thế hệ 2-1B: 63.9).[^mdpbench-readme]

## PureDocBench (Clean / Digital-degraded / Real-degraded)

| Mô hình | Overall | Clean | Digital | Real | Nguồn |
|---|---:|---:|---:|---:|---|
| OvisOCR3 | **82.31** | — | — | — | own (định nghĩa "overall" không nêu) |
| TeleOCR | 78.41 (TB 3 track) | **86.90** | **77.47** | **70.85** | own |
| MinerU2.5-Pro | 70.07 (TB 3 track) | 75.87 | 71.77 | 62.56 | [T] |
| PaddleOCR-VL-1.6 | 65.44 | — | — | — | [O3] |
| MonkeyOCRv2-B-Parsing | 64.91 | — | — | — | [O3] |

[^teleocr-v3][^ovisocr3-card] TeleOCR loại sáu prediction lỗi lặp (1 Clean, 5 Real) và tính chúng bằng 0.[^teleocr-v3] Text edit/CDM/TEDS theo từng track nằm ở trang supplementary evidence.

## olmOCR-Bench (unit-test pass rate)

| Mô hình | Overall ↑ | ArXiv | Old math | Tables | Old scans | Hdr/Ftr | Multi-col | Tiny text | Base | Nguồn |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Infinity-Parser2-Pro | **87.6** | 88.1 | **91.3** | 91.2 | **58.2** | **95.8** | 83.7 | 92.5 | 99.9 | own, [L] |
| LightOnOCR-3-4B | 86.3 | **91.1** | 89.1 | 90.2 | 52.5 | 89.2 | 85.6 | 93.2 | 99.5 | [L] |
| Chandra OCR 2 | 85.8 ± 0.8 | 86.9 | 89.1 | **92.1** | 51.1 | 91.4 | 82.1 | 93.7 | 99.9 | own, [L] |
| LightOnOCR-3-0.8B | 85.5 | 89.6 | 87.6 | 90.8 | 48.7 | 88.2 | 85.2 | 94.1 | 99.7 | [L] |
| LightOnOCR-3-1B | 84.5 | 90.4 | 80.6 | 89.9 | 48.3 | 87.6 | **85.9** | 93.7 | 99.5 | [L], [M] |
| Surya OCR 2.5 | 83.7 | 87.0 | 78.6 | 90.9 | 44.3 | 90.9 | 83.3 | **94.8** | 99.9 | own (TB 3 lượt) |
| MiniCPM-OCR 1.0 | 82.7 | — | — | — | — | — | — | — | — | own |
| PaddleOCR-VL-1.6 | 80.2 | — | — | — | — | — | — | — | — | [M] |
| MinerU2.5-Pro | 79.5 | — | — | — | — | — | — | — | — | [M] |
| TeleOCR | 77.1 | — | — | — | — | — | — | — | — | [M] |

[^lightonocr3-blog][^chandra2-card][^chandra2-bench-img][^infinity2-report][^surya25-card][^minicpm-repo] Ảnh benchmark Chandra (đã tải) khớp bảng text 85.8.[^chandra2-bench-img]

**Hậu xử lý (postprocessing) làm thay đổi thứ hạng:** theo ảnh của LightOn, điểm thô (raw) là Infinity-Parser2-Pro 85.9, Chandra 2 85.1, LightOnOCR-3-4B 85.0; sau postprocessing tăng lên 87.6 / 85.8 / 86.3.[^lightonocr3-blog] Vì vậy chênh lệch <2 điểm trong top-3 phụ thuộc vào bước chuẩn hóa đầu ra.

## OmniParseBench (Datalab, 16,288 test pass/fail, 2,937 trang, 2,343 tài liệu, 22 suite, 92 ngôn ngữ)

Headline = trung bình text, tables, layout. Model open-weight được Datalab chạy bằng server image của `omni-parse-bench` với default do vendor khuyến nghị.[^opb-card]

| Mô hình | Headline ↑ | Text | Tables | Layout |
|---|---:|---:|---:|---:|
| Chandra OCR 2 | **90.1** | **87.4** | 87.4 | 95.4 |
| MinerU2.5-Pro | 87.1 | 77.4 | **92.1** | 91.7 |
| Infinity-Parser2-Pro | 87.0 | 83.3 | 84.1 | 93.5 |
| Surya OCR 2.5 | 85.9 | 83.8 | 78.3 | **95.7** |
| MiniCPM-OCR 1.0 | 83.2 | 72.8 | 89.1 | 87.6 |
| LightOnOCR-3-4B | 82.9 | 83.9 | 70.8 | 94.0 |
| LightOnOCR-3-0.8B | 81.6 | 81.1 | 72.1 | 91.7 |
| PaddleOCR-VL-1.6 | 78.7 | 61.7 | 83.7 | 90.7 |

[^opb-card][^surya25-size-chart] Biểu đồ "OmniParseBench against model size" trong card Surya 2.5 khớp các headline này.[^surya25-size-chart] MonkeyOCRv2, OvisOCR3 và TeleOCR không có mặt. **Synthesis:** PaddleOCR-VL-1.6 dẫn cụm OmniDocBench nhưng đứng cuối nhóm ở đây, chủ yếu do điểm text 61.7; benchmark này do Datalab (tác giả Chandra/Surya) xây và chạy, nên cần coi là bằng chứng vendor-run.

## ParseBench và fr-bench-pdf2md (bảng của LightOn)

| Mô hình | ParseBench 5 mục ↑ | Tables | Charts | Faithfulness | Semantic fmt | Visual grounding | fr-bench-pdf2md ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|
| LightOnOCR-3-4B | **75.1** | 83.8 | **66.1** | 89.9 | **67.6** | 68.3 | **74.1** |
| LightOnOCR-3-0.8B | 74.6 | 84.5 | 64.7 | 88.9 | 66.7 | 68.2 | 70.5 |
| Infinity-Parser2-Pro | 74.3 | 86.4 | 61.3 | 89.7 | 59.1 | **74.9** | 63.2 |
| LightOnOCR-3-1B | 71.4 | 84.8 | 57.3 | 88.6 | 64.5 | 61.7 | 69.6 |
| Chandra OCR 2 | 70.1 | **89.2** | 65.1 | 83.7 | 61.4 | 51.2 | 69.0 |

[^lightonocr3-blog] Báo cáo Infinity-Parser2 cho cùng ParseBench Pro 74.3 và Chandra-OCR-2 70.1.[^infinity2-report]

## Benchmark chuyên biệt và phụ

- **CHAOS-Bench (page-average recall của từ bị thay đổi):** hai nguồn mâu thuẫn. [M] (MiniCPM tự chạy; 500 trang, 1,025 từ bị thay đổi, tìm theo word boundary trong output cả trang): MiniCPM 29.78, TeleOCR 21.28, MinerU2.5-Pro 13.90, PaddleOCR-VL-1.6 9.32, LightOnOCR-3-1B 7.73, Chandra 2 2.87. Ảnh in 29.78 nhưng `benchmark-data.json` để ô CHAOS của MiniCPM là `null` với `status: pending_confirmation`. MonkeyOCRv2: MonkeyOCRv2-B 17.9, MinerU2.5-Pro 6.3, PaddleOCR-VL-1.6 6.0; caption ghi các hàng baseline "taken from CHAOS-Bench", tức nguồn leaderboard gốc chứ không phải lần chạy của MiniCPM.[^minicpm-repo][^monkeyocrv2-paper]
- **OCRBench v2:** [M] một số duy nhất: MiniCPM 54.7, PaddleOCR-VL-1.6 35.2, Chandra 2 32.9, MinerU2.5-Pro 29.1, TeleOCR 23.3, LightOnOCR-3-1B 12.7. Card OvisOCR3 tách EN/ZH: OvisOCR3 65.9/61.3, PaddleOCR-VL-1.6 23.8/30.4.[^minicpm-repo][^ovisocr3-card]
- **OCRBench (v1):** OvisOCR3 88.8, Infinity-Parser2-Pro 86.20, PaddleOCR-VL-1.6 55.9.[^ovisocr3-card][^infinity2-card]
- **DocFigCapBench (localization F1 / caption score):** OvisOCR3 90.97/6.93, PaddleOCR-VL-1.6 85.32/4.29, MinerU2.5-Pro 85.00/4.61.[^ovisocr3-card][^ovisocr3-overview-img]
- **CrossTabBench (relation F1 / reconstruction TEDS) và MPDocBench-Parse truncated-table TEDS:** OvisOCR3 97.07/89.66 và 92.04; MinerU2.5-Pro 59.14/41.02 và 91.44; PaddleOCR-VL-1.6 42.61/24.24 và 83.39.[^ovisocr3-card]
- **Hard table (in-house Paddle, 1,258 mẫu):** PaddleOCR-VL-1.6 91.71 TEDS / 94.67 TEDS-S; MinerU2.5-Pro 89.77 / 93.78.[^paddle16-report]
- **Table recognition 5 benchmark (MinerU):** MinerU2.5-Pro overall 91.10 TEDS / 94.48 TEDS-S trên OmniDoc Base, OmniDoc Hard, CCOCR, OCRBv2 và in-house; không có mô hình nào khác trong 10 mô hình ở bảng này.[^mineru-pro-table-img]
- **Đa ngôn ngữ nội bộ Datalab (không cùng tập test):** Chandra 2 77.8% (43 ngôn ngữ), 72.7% (90 ngôn ngữ, VI 82.6%); Surya 2.5 74.9% (91 ngôn ngữ, phiên bản "khó hơn", VI 63.6%).[^chandra2-card][^chandra2-full-bench][^surya25-card]

## Throughput (không cùng phần cứng giữa các nguồn)

- **RTX 5090, 1,651 ảnh OmniDocBench v1.6, concurrency 1 [M]:** MiniCPM 1.217 p/s (guide; JSON throughput ghi 1.213), PaddleOCR-VL-1.6 0.818, LightOnOCR-3 (không nêu biến thể) 0.340, MinerU2.5-Pro 0.336 (Advanced; Standard 0.531), TeleOCR 0.141, Chandra 2 0.068.[^minicpm-repo]
- **H100, vendor tự đo:** Surya 2.5 4.52 p/s (192 DPI, 32 request); LightOnOCR-3-4B 2.03 p/s đỉnh vs Chandra 2 1.68 (cùng 512 trang olmOCR, vLLM 0.30.0); Chandra tự báo 1.44 p/s ở 96 concurrent; Infinity-Parser2-Pro 2.13 s/trang (TP2, C8).[^surya25-card][^lightonocr3-blog][^chandra2-card][^infinity2-report]

## Tổng hợp theo mô hình (Synthesis)

| Mô hình | Điểm mạnh theo bằng chứng | Điểm yếu / khoảng trống |
|---|---|---|
| Chandra OCR 2 | Dẫn OmniParseBench (90.1), top olmOCR, mạnh bảng ParseBench, VI MDPBench 85.6 | OmniDocBench 92.27 [M]; visual grounding 51.2; chậm nhất ở [M]; CHAOS thấp |
| MinerU2.5-Pro | Reading order v1.6 tốt nhất; bảng mạnh (OPB tables 92.1, hard table) | MDPBench 71.0; Real5 skew 81.26; cross-page relation F1 59.14 |
| Surya OCR 2.5 | Layout OmniParseBench 95.7; 689M, nhanh | Không có OmniDocBench/MDPBench/Real5 |
| MonkeyOCRv2-B-Parsing | MDPBench official cao nhất (83.3), CHAOS 17.9 ở bảng của chính nó | OmniDocBench 91.57; PureDocBench 64.91 [O3] |
| OvisOCR3 | Tự báo top MDPBench, PureDocBench, Real5, OCRBench, cross-page table | Chỉ overall; không có olmOCR/OmniParseBench; chưa có tech report |
| PaddleOCR-VL-1.6 | Real5 per-condition tốt nhất; formula CDM v1.6 97.49; nhanh | OmniParseBench text 61.7; OCRBench thấp; cross-page TEDS 24.24 |
| Infinity-Parser2-Pro | Top olmOCR (87.6), visual grounding ParseBench 74.9 | OmniDocBench 93.95; 35B-A3B; fr-bench 63.2 |
| LightOnOCR-3-4B | Top ParseBench (75.1), fr-bench (74.1) | OmniParseBench tables 70.8; số OmniDocBench chỉ có cho 1B (89.87) |
| TeleOCR | OmniDocBench v1.6 cao nhất (96.87), Wild [T], PureDocBench 3 track | olmOCR 77.1 [M]; throughput 0.141 p/s [M] |
| MiniCPM-OCR 1.0 | Real5/Wild [M] cao nhất, nhanh nhất ở [M], OCRBench v2 54.7 | Phần lớn số do chính MiniCPM chạy; OPB text 72.8 |

**Chọn theo nhu cầu (Synthesis):** tài liệu số sạch kiểu OmniDocBench → cụm TeleOCR/OvisOCR3/MiniCPM/PaddleOCR-VL-1.6; PDF tiếng Anh kiểu unit-test (olmOCR/OmniParseBench) → Infinity-Parser2-Pro, Chandra OCR 2, LightOnOCR-3-4B; ảnh chụp đa ngôn ngữ → MonkeyOCRv2-B (official) hoặc OvisOCR3 (self-reported); ảnh biến dạng vật lý → PaddleOCR-VL-1.6, MiniCPM, OvisOCR3.

## Contradictions

- **PaddleOCR-VL-1.6 trên MDPBench:** bài/card MonkeyOCRv2 ghi 75.0 (digital 82.8, photo 72.6), còn README MDPBench chính thức và card OvisOCR3 ghi 78.9 (87.1/76.3). Không nguồn nào giải thích.[^monkeyocrv2-paper][^mdpbench-readme][^ovisocr3-card]
- **Chandra OCR 2 trên olmOCR:** card Datalab 85.8; bảng báo cáo Infinity-Parser2 ghi 83.1 ± 0.9; ảnh olmOCR trên GitHub của Infinity ghi 85.9.[^chandra2-card][^infinity2-report][^infinity2-olmocr-img] Card Chandra ghi đúng **83.1 ± 0.9 cho Chandra 1**, nên **Synthesis (giả thuyết):** báo cáo Infinity có thể đã gán nhầm số của phiên bản trước; chưa có output/scorer để xác nhận.[^chandra2-card]
- **MiniCPM ảnh vs JSON:** `ocr-benchmarks.png` có số cho mọi ô, nhưng `benchmark-data.json` để `null` cho CHAOS của MiniCPM, OmniDocBench v1.6 của PaddleOCR-VL-1.6, Real5 và OmniDocBench của MinerU2.5-Pro, đánh dấu `pending_confirmation`; throughput 1.217 (guide) vs 1.213 (JSON).[^minicpm-repo]
- **MinerU2.5-Pro trên OmniDocBench v1.6:** 95.69/95.72 (card) vs 95.75 (các báo cáo khác); formula CDM 97.29 vs 97.45.[^mineru-pro-2605-card][^paddle16-report]
- **CHAOS-Bench:** MinerU2.5-Pro 13.90 vs 6.3, PaddleOCR-VL-1.6 9.32 vs 6.0 giữa [M] và MonkeyOCRv2.[^minicpm-repo][^monkeyocrv2-paper]
- **Wild-OmniDocBench:** chênh 2–4 điểm cho cùng mô hình giữa giao thức [M] và [T].[^minicpm-repo][^teleocr-v3]

## Giới hạn và độ tin cậy

- Không benchmark nào được chạy lại; không có output, prompt hay snapshot leaderboard đầy đủ. Mọi kết quả là Reported; các nhận định xếp hạng ở trên là Synthesis.
- Nhiều nguồn là bên cạnh tranh tự đánh giá (MiniCPM chạy TeleOCR/Chandra; Datalab chạy OmniParseBench; LightOn chạy Chandra/Infinity). Một ảnh cũ không được README tham chiếu (`benchmark-score-table.jpg` của MiniCPM) cho số khác bảng hiện hành, ví dụ TeleOCR Real5 90.5553 và OmniDocBench 96.87; trang này dùng `ocr-benchmarks.png` mà README tham chiếu.[^minicpm-repo]
- LightOnOCR-3 trong bảng [M] và [OPB] là biến thể 1B hoặc 0.8B/4B tùy nguồn; không suy chéo giữa các biến thể.

## Relationships

- **Compares:** [Chandra OCR 2](chandra-ocr-2.md), [MinerU2.5-Pro](mineru2-5-pro.md), [Surya OCR 2.5](surya-ocr-2-5.md), [MonkeyOCRv2](monkeyocrv2.md), [OvisOCR3](ovisocr3.md), [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), [Infinity-Parser2](infinity-parser2.md), [LightOnOCR-3 evaluation](lightonocr-3-evaluation.md), [TeleOCR](teleocr.md), [MiniCPM-OCR evaluation](minicpm-ocr-evaluation.md).
- **Uses:** [OmniParseBench](omniparsebench.md), [MDPBench](mdpbench.md), [Real5-OmniDocBench](real5-omnidocbench.md).
- **Detailed by:** [OCR ten-model benchmark comparison: supplementary evidence](ocr-ten-model-benchmark-comparison.md), giữ component vectors, benchmark chuyên biệt/in-house, throughput chi tiết và coverage ledger cho cùng mười mô hình.
- **Complements:** [End-to-end generative OCR VLM benchmarks](end-to-end-generative-ocr-vlm-benchmarks.md) và [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md), vốn liệt kê theo họ kiến trúc thay vì theo tập mô hình này.

[^chandra2-card]: Datalab, [Chandra OCR 2 model card](../raw/chandra-ocr-2.md), §§ Benchmarks › olmOCR Benchmark, Multilingual Benchmark (43 Languages), Throughput.
[^chandra2-bench-img]: [chandra-bench.png](../raw/ocr-benchmark-assets-2026-10-30/chandra-bench.png), bar "Chandra 2 85.8%"; tải 2026-10-30 theo `manifest.json`.
[^chandra2-full-bench]: [chandra-full-benchmarks.md](../raw/ocr-benchmark-assets-2026-10-30/chandra-full-benchmarks.md), § Overall Scores và hàng `vi`.
[^surya25-card]: Datalab, [Surya OCR 2.5 model card](../raw/surya-ocr-2.5-hf.md), §§ Benchmarks › OmniParseBench, olmOCR-bench, Multilingual, Throughput › H100.
[^surya25-size-chart]: [surya-opb_size_chart.png](../raw/ocr-benchmark-assets-2026-10-30/surya-opb_size_chart.png), các nhãn điểm theo mô hình.
[^opb-card]: Datalab, [Omni Parse Bench dataset card](../raw/ocr-benchmark-assets-2026-10-30/omniparsebench-card.md), §§ Results, Results details.
[^mineru-pro-2604-card]: OpenDataLab, [MinerU2.5-Pro-2604 model card](../raw/MinerU2.5-Pro-2604-1.2B.md), § 1 "Defeating Leading Models on OmniDocBench v1.6".
[^mineru-pro-2605-card]: OpenDataLab, [MinerU2.5-Pro-2605 model card](../raw/MinerU2.5-Pro-2605-1.2B.md), § News › bảng "MinerU2.5-Pro-2605 vs. MinerU2.5-Pro-2604 on OmniDocBench (v1.6_full)".
[^mineru-pro-leaderboard]: [mineru-leaderboard.png](../raw/ocr-benchmark-assets-2026-10-30/mineru-leaderboard.png), panels Full/Base/Hard Overall và Single-task Performance.
[^mineru-pro-end2end]: [mineru-end2end.png](../raw/ocr-benchmark-assets-2026-10-30/mineru-end2end.png), hàng MinerU2.5-Pro.
[^mineru-pro-table-img]: [mineru-table_performance.png](../raw/ocr-benchmark-assets-2026-10-30/mineru-table_performance.png), hàng MinerU2.5-Pro, cột Overall.
[^monkeyocrv2-paper]: Liu et al., [MonkeyOCRv2](../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex), bảng MDPBench (dòng PaddleOCR-VL-1.6, chandra-ocr-2), bảng OmniDocBench 1.6, bảng `tab:chaos_bench_results`.
[^mdpbench-readme]: [MDPBench README](../raw/ocr-benchmark-assets-2026-10-30/mdpbench-readme.md), § Main Results; tải 2026-10-30 theo `manifest-extra.json`.
[^ovisocr3-card]: ATH-MaaS, [OvisOCR3 model card](../raw/ATH-MaaS-OvisOCR3.md), § Performance (Document Parsing, General OCR, Document Figure Captioning, Cross-Page Table Reconstruction).
[^ovisocr3-overview-img]: [ovisocr3_performance_overview.png](../raw/ocr-benchmark-assets-2026-10-30/ovisocr3_performance_overview.png), 12 panel; khớp bảng text của card.
[^paddle16-report]: Zhang et al., [PaddleOCR-VL-1.6 report](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex), bảng `tab:omni16_full_performance`, `tab:real5-omnidocbench-performance` và bảng hard table recognition.
[^infinity2-report]: INF Team, [Infinity-Parser2 report](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex), `latex/experiments.tex` bảng `tab:document_parsing_public` và bảng throughput.
[^infinity2-card]: INF Team, [Infinity-Parser2-Pro model card](../raw/Infinity-Parser2-Pro.md), bảng tổng hợp, hàng OCRBench.
[^infinity2-olmocr-img]: [infinity-olmocr_bench_perf.png](../raw/ocr-benchmark-assets-2026-10-30/infinity-olmocr_bench_perf.png), bar Chandra-OCR-2 85.9.
[^lightonocr3-blog]: Taghadouini, Cavaillès và Aubertin, [LightOnOCR-3 blog](../raw/lightonocr-3/index.md), § 2 (bảng olmOCR-Bench, ParseBench, fr-bench-pdf2md), `assets/VjGuS22FehyMGIaLiZ7fU.png` (raw vs postprocessed), `assets/QKQIrgIR9NpILnyGLu9fW.png` (speed).
[^teleocr-v3]: Cai et al., [TeleOCR](../raw/arXiv-2608.12898v3-TeleOCR/main.tex), bảng `tab:omni_result`, `tab:Wild_result`, `tab:puredoc`; [score.png](../raw/arXiv-2608.12898v3-TeleOCR/score.png) (PureDocBench trung bình 78.41 và 70.07).
[^minicpm-repo]: [MiniCPM-OCR repository](../raw/MiniCPM-OCR/README.md), revision `b33b474`; `assets/minicpm-ocr/ocr-benchmarks.png`; `docs/minicpm_ocr_1dot0_en.md` § Throughput; `docs/benchmark_reproduction_en.md` §§ Evaluation Settings, Scoring and Aggregation Rules (gồm CHAOS-Bench); `assets/minicpm-ocr/benchmark-data.json` (`benchmarks.models[].scores/status`, `throughput.models`).
[^xiaomi-card]: Xiaomi, [Xiaomi-OCR-0 model card](../raw/Xiaomi-OCR-0.md), § Document parsing: selected comparisons.
