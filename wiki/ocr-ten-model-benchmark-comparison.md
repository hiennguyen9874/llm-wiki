---
type: Synthesis
title: "OCR ten-model benchmark comparison: supplementary evidence"
description: Bằng chứng bổ sung cho so sánh benchmark mười OCR model, gồm component vectors, benchmark chuyên biệt và in-house, điều kiện throughput và coverage ledger.
tags: [ml, ocr, benchmarks, comparison, document-parsing]
status: draft
created: 2026-10-30
generated: { by: llm-wiki-agent/1, at: 2026-10-30T03:07:00Z }
stale_after: 2027-01-30
sources:
  - id: fetched-assets
    resource: ../raw/ocr-benchmark-assets-2026-10-30/README.md
    scope: ../raw/ocr-benchmark-assets-2026-10-30/
    kind: reference-collection
    title: OCR benchmark evidence fetched on 2026-10-30
  - id: minicpm
    resource: ../raw/MiniCPM-OCR/README.md
    scope: ../raw/MiniCPM-OCR/
    kind: code
    revision: b33b474
    title: MiniCPM-OCR repository
  - id: ovis3
    resource: ../raw/ATH-MaaS-OvisOCR3.md
    kind: model-card
    title: OvisOCR3 model card
  - id: paddle16
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    kind: paper
    title: PaddleOCR-VL-1.6 technical report
  - id: teleocr
    resource: ../raw/arXiv-2608.12898v3-TeleOCR/main.tex
    scope: ../raw/arXiv-2608.12898v3-TeleOCR/
    kind: paper
    revision: arXiv:2608.12898v3
    title: TeleOCR technical report v3
  - id: infinity2
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    kind: paper
    title: Infinity-Parser2 technical report
  - id: lighton3
    resource: ../raw/lightonocr-3/index.md
    scope: ../raw/lightonocr-3/
    kind: article
    title: LightOnOCR-3 blog and figures
  - id: monkey2
    resource: ../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex
    kind: paper
    title: MonkeyOCRv2 paper
  - id: mineru2605
    resource: ../raw/MinerU2.5-Pro-2605-1.2B.md
    kind: model-card
    title: MinerU2.5-Pro-2605 model card
  - id: chandra2
    resource: ../raw/chandra-ocr-2.md
    kind: model-card
    title: Chandra OCR 2 model card
  - id: surya25
    resource: ../raw/surya-ocr-2.5-hf.md
    kind: model-card
    title: Surya OCR 2.5 model card
  - id: ovis2-report
    resource: ../raw/2607.13639_OvisOCR2/main.tex
    kind: paper
    title: OvisOCR2 report, comparator rows only
  - id: unlimited2
    resource: ../raw/Unlimited-OCR-2.pdf
    kind: paper
    title: Unlimited OCR Works 2, coverage check
---

# OCR ten-model benchmark comparison: supplementary evidence

Phụ lục bằng chứng cho [Document OCR model benchmark comparison](document-ocr-model-benchmark-comparison.md). Trang chính giữ các bảng headline theo dataset (OmniDocBench v1.6, Real5, Wild, MDPBench, PureDocBench, olmOCR-Bench, OmniParseBench, ParseBench, CHAOS, OCRBench), contradictions giữa các nguồn và tổng hợp theo mô hình. Trang này **chỉ** giữ phần chi tiết không lặp lại ở đó: component vectors, kết quả crop-level, benchmark chuyên biệt và in-house, điều kiện throughput, và coverage ledger cho cùng mười model. Mọi điểm là **Reported**; việc đọc được con số từ LaTeX, card, PDF hoặc ảnh là **Observed**; không có inference hay scorer nào được chạy lại, nên không có kết quả **Reproduced**.[^fetched-assets]

## Quy tắc

- `—` = chưa tìm thấy điểm cho đúng model/protocol trong bằng chứng đã đọc, không phải 0.
- Không chuyển điểm giữa các biến thể: LightOn-3-1B ≠ 4B, Surya 2 ≠ 2.5, OvisOCR2 ≠ OvisOCR3, Infinity-Parser-7B/Flash ≠ Parser2-Pro, MonkeyOCRv2 backbone/B-Und ≠ B-Parsing.
- Chỉ so trực tiếp trong cùng một bảng nguồn có cùng split/scorer; các nguồn khác nhau đứng cạnh nhau chỉ để truy xuất.

## 1. OmniDocBench v1.6: MinerU2.5-Pro Base / Hard

MinerU report định nghĩa Base 1,355 trang, Hard 296 trang, Full 1,651 trang. MinerU2.5-Pro-2604 end-to-end Overall: **96.12 / 94.08 / 95.69**. Vector của Hard: text ED **0.052**, formula CDM **97.54**, table TEDS **89.91**, TEDS-S **93.61**, order ED **0.170**. Đây là điểm end-to-end; formula 98.79 trong bảng crop ở §5 không thay được 97.54.[^fetched-assets]

## 2. PureDocBench: component vectors theo track

TeleOCR paper: 4,425 ảnh từ 1,475 trang, 10 domain, ba track Clean / Digital-degraded / Real-degraded. Thứ tự `Text ED ↓ / Formula CDM ↑ / Table TEDS ↑`:[^teleocr]

| Model | Clean | Digital degraded | Real degraded |
|---|---|---|---|
| TeleOCR | 0.111 / 81.01 / 91.09 | 0.206 / 72.59 / 80.45 | 0.302 / 65.11 / 77.66 |
| MinerU2.5-Pro | 0.222 / 65.14 / 84.68 | 0.272 / 61.79 / 80.73 | 0.375 / 52.70 / 72.47 |

Báo cáo OvisOCR2 ghi MinerU2.5-Pro theo track 75.87 / 71.77 / 62.56 và Avg3 **70.07**, khớp phép tính trung bình ở trang chính.[^ovis2-report] Overall 82.31 của OvisOCR3 (card) không nêu định nghĩa, nên không đánh đồng với bất kỳ track nào.[^ovis3]

## 3. ParseBench 3 category và fr-bench-pdf2md theo category

Cùng các bảng blog LightOn, higher is better. Trang chính đã có các cột 5 category; ở đây bổ sung Overall 3 category:[^lighton3]

| Model | ParseBench Overall 3 cats | Overall 5 cats |
|---|---:|---:|
| LightOnOCR-3-4B | 80.4 | 75.1 |
| Infinity-Parser2-Pro | 78.4 | 74.3 |
| Chandra OCR 2 | 78.1 | 70.1 |

| Model | French Overall | Baseline | Forms | Graphics | Handwritten | Long table | Long table 2 | Multi-column | Tiny text |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LightOnOCR-3-4B | 74.1 | 98.3 | 49.6 | 70.5 | 46.1 | 83.6 | 71.7 | 83.6 | 88.3 |
| Chandra OCR 2 | 69.0 | 99.7 | 39.1 | 75.1 | 26.1 | 81.3 | 79.4 | 73.3 | 76.9 |
| Infinity-Parser2-Pro | 63.2 | 98.0 | 42.3 | 63.7 | 39.4 | 52.2 | 38.7 | 69.7 | 90.6 |

Điểm Surya **2** (ParseBench 64.8, fr-bench 54.1) trong cùng blog không thuộc Surya **2.5**.[^lighton3]

## 4. CHAOS-Bench: giao thức của MiniCPM

Guide MiniCPM: 500 trang, 1,025 từ bị thay đổi; normalize whitespace trong Markdown cả trang, tìm `ocr_ans` không phân biệt hoa thường, theo word boundary, không align bbox; tính recall theo trang rồi lấy trung bình. Điểm cao chỉ đo việc giữ đúng các từ bất thường, không đo toàn bộ hallucination của hệ thống. Bảng điểm và trạng thái `pending_confirmation` trong JSON nằm ở trang chính.[^minicpm]

## 5. Benchmark chuyên biệt của OvisOCR3

Chỉ OvisOCR3 trong mười model có hàng KIE trong card: **OCRBench KIE 90.50; OCRBench v2 KIE 83.01; CC-OCR KIE 88.69; in-house KIE 77.73**. Đây là các task/subset riêng, không phải điểm parsing hay OCRBench overall.[^ovis3]

Thang điểm và evaluator của DocFigCapBench caption score (OvisOCR3 6.93, PaddleOCR-VL-1.6 4.29, MinerU2.5-Pro 4.61) không được định nghĩa trong card; không quy ra phần trăm.[^ovis3]

CrossTabBench theo precision/recall, cùng card:[^ovis3]

| Model | Relation F1 ↑ | Precision / Recall | Reconstruction TEDS ↑ | MPDocBench-Parse truncated-table TEDS ↑ |
|---|---:|---:|---:|---:|
| OvisOCR3 | 97.07 | 96.20 / 97.96 | 89.66 | 92.04 |
| MinerU2.5-Pro | 59.14 | 93.81 / 43.18 | 41.02 | 91.44 |
| MinerU2.5-Pro + MinerU-PoPo | 54.76 | 97.40 / 38.09 | 36.42 | 91.87 |
| PaddleOCR-VL-1.6 | 42.61 | 90.13 / 27.90 | 24.24 | 83.39 |

MinerU-PoPo là hệ thống tăng cường riêng, không thay cho MinerU2.5-Pro thuần. **Synthesis:** baseline thua chủ yếu ở recall: chúng ít nối nhầm nhưng bỏ sót nhiều quan hệ bảng qua trang. TEDS trên mảnh bảng (91.44) và TEDS khi ghép bảng qua trang (41.02) trả lời hai câu hỏi khác nhau, nên không mâu thuẫn.[^ovis3]

## 6. Benchmark thành phần và in-house

### MinerU2.5-Pro-2604: crop theo GT box

Đánh giá trên crop theo ground-truth box, nên loại bỏ ảnh hưởng của lỗi layout; đây không phải end-to-end.[^fetched-assets]

| Dataset / task | Metric | MinerU2.5-Pro |
|---|---|---:|
| OmniDocBench v1.6 text crops Base / Hard / Full | ED ↓ | 0.015 / 0.048 / 0.019 |
| OmniDoc formula crops Base / Hard | CDM ↑ | 99.20 / 98.79 |
| UniMER-Test CPE / HWE / SCE / SPE | CDM ↑ | 98.97 / 95.38 / 97.04 / 99.44 |
| LaTeX-80M | CDM ↑ | 97.23 |
| In-house Chinese / Fuzzy formulas | CDM ↑ | 95.28 / 94.90 |
| OmniDoc table crops Base | TEDS / TEDS-S ↑ | 95.67 / 97.42 |
| OmniDoc table crops Hard | TEDS / TEDS-S ↑ | 92.46 / 94.67 |
| CC-OCR table subset | TEDS / TEDS-S ↑ | 88.49 / 91.90 |
| OCRBench v2 table subset | TEDS / TEDS-S ↑ | 93.56 / 96.27 |
| In-house tables | TEDS / TEDS-S ↑ | 82.70 / 89.65 |
| Trung bình năm bộ table | TEDS / TEDS-S ↑ | 91.10 / 94.48 |

### Infinity-Parser2-Pro: layout, element, chart, chem, multimodal chung

Không model nào khác trong mười model có hàng đúng tên ở các bảng này; không lấy MinerU2.5 hoặc PaddleOCR-VL-1.5 thay cho Pro/1.6.[^infinity2]

| Dataset / task | Metric / split | Infinity-Parser2-Pro |
|---|---|---:|
| DocLayNet | Layout mIoU ↑, remap năm category | 64.93 |
| OmniDocBench v1.5 layout subset | mIoU ↑ | 74.56 |
| D4LA | mIoU ↑ | 52.41 |
| OmniDocBench v1.5 text crops | EDS ↑ | 95.05 |
| PubTabNet validation | TEDS ↑ | 94.76 |
| FinTabNet validation | TEDS ↑ | 98.88 |
| UniMER-Test SPE / SCE / CPE / HWE / Avg | CDM ↑ | 99.4 / 96.2 / 98.3 / 96.7 / 97.7 |
| ChartQA làm Chart2Table, không phải QA accuracy | RMS-F1 ↑ | 86.5 |
| ChartX-SE Chart2JSON | AP strict / slight / high ↑ | 61.7 / 68.9 / 73.7 |
| ChartMimic direct-600 Chart2Code | execution / low-level / high-level ↑ | 87.1 / 70.1 / 79.6 |
| CoSyn-Chemical validation | InChI exact / Tanimoto / valid SMILES ↑ | 53.91 / 73.19 / 86.72 |
| ChemDraw-Bench in-house | InChI exact / Tanimoto / valid SMILES ↑ | 49.95 / 72.35 / 77.28 |
| AI2D / MathVista testmini / MMMU / MMStar | score ↑ | 88.89 / 71.4 / 61.89 / 69.66 |
| MMBench EN / CN dev | score ↑ | 87.54 / 86.43 |
| OCRBench | score ↑ | 86.2 |
| DocVQA / InfoVQA validation | ANLS ↑ | 96.43 / 86.26 |

mIoU (category-area union) không phải mAP detection; EDS 95.05 là similarity, không phải ED. UniMER trùng tên subset với bảng MinerU nhưng khác protocol và độ chính xác làm tròn, nên không kết luận MinerU hơn hay kém Infinity từ chênh lệch nhỏ. OCRBench 86.2 khác lần chạy với 88.8 của card OvisOCR3.[^infinity2][^ovis3]

### PaddleOCR-VL-1.6: in-house trong paper của Paddle

| Dataset | PaddleOCR-VL-1.6 | Comparator trong mười model |
|---|---:|---|
| Chart, 1,801 mẫu, RMS-F1 Overall / EN / ZH ↑ | 91.74 / 90.11 / 93.37 | Không có |
| Text spotting, Overall ↑ | 87.47 | Không có |
| Seal, 300 ảnh, NED ↓ | 0.119 | Không có |

Spotting theo chín category: Ancient **85.98**, Blur **90.59**, Common **77.28**, handwriting ZH **85.90**, handwriting EN **92.60**, printing ZH **91.26**, printing EN **86.51**, Table **92.32**, Japanese **84.76**. Hard table 1,258 mẫu (91.71 vs MinerU2.5-Pro 89.77 TEDS) nằm ở trang chính.[^paddle16]

### Bộ in-house của OvisOCR2: chỉ hàng comparator

Không gán điểm OvisOCR2 cho OvisOCR3. Report có thêm các hàng PaddleOCR-VL-1.6 và MinerU2.5-Pro trên bộ in-house hơn 1,000 trang của Ovis:[^ovis2-report]

| Subset / metric | PaddleOCR-VL-1.6 | MinerU2.5-Pro |
|---|---:|---:|
| Full Overall ↑ | 82.88 | 65.54 |
| Full text ED ↓ | 0.1292 | 0.1645 |
| Full formula CDM ↑ | 85.13 | 34.85 |
| Full TEDS / TEDS-S ↑ | 76.42 / 80.74 | 78.20 / 82.68 |
| Full order ED ↓ | 0.2358 | 0.3351 |
| Easy / Medium / Hard Overall ↑ | 84.98 / 83.16 / 75.06 | 66.12 / 65.37 / 64.60 |
| Handwriting Overall ↑ | 67.66 | 55.04 |
| Handwriting text ED / CDM | 0.2148 / 77.88 | 0.2903 / 40.63 |
| Handwriting TEDS / TEDS-S / order ED | 46.57 / 57.39 / 0.2202 | 53.52 / 67.21 / 0.4353 |
| Complex tables Overall ↑ | 73.19 | 71.43 |
| Complex tables text ED ↓ | 0.2760 | 0.3407 |
| Complex tables TEDS / TEDS-S ↑ | 73.98 / 77.41 | 76.92 / 79.71 |
| Complex tables missing rate ↓ | 0.1593 | 0.1327 |

### Sci-ImageMiner (TeleOCR)

ICDAR 2026 Sci-ImageMiner data extraction: TeleOCR **F1 17.23**, **TEDS 66.39**, **weighted 41.81**; không có model nào khác trong mười model ở bảng này. 41.81 không phải độ chính xác OCR văn bản.[^teleocr]

## 7. Throughput: điều kiện chi tiết

Không trộn phần cứng hoặc workload giữa các mục; tóm tắt nằm ở trang chính.

- **MiniCPM, RTX 5090, OmniDocBench v1.6 Full:** official SDK, có acceleration; concurrency theo ảnh = 1 nhưng concurrency theo region có thể > 1. Guide: MiniCPM 1.217, PaddleOCR-VL-1.6 0.818, MinerU2.5-Pro 0.336, TeleOCR 0.141, Chandra OCR 2 0.068, LightOnOCR-3 0.340 (không nêu biến thể, nên không gán cho 4B) pages/s. JSON tách MinerU2.5-Pro-Standard **0.531** và Advanced **0.336**. MiniCPM ở concurrency 1/2/4/6/8: **1.217 / 1.613 / 1.888 / 2.031 / 2.133** pages/s.[^minicpm]
- **LightOn, 512 trang olmOCR, một H100/model, vLLM 0.30.0:** LightOnOCR-3-4B median single-page latency **6.6 s**, peak **2.03** pages/s, **3.36** ở long side 1540 px; Chandra OCR 2 **8.1 s**, **1.68**, **2.95**. Render benchmark lần lượt 400 DPI ≤ 5 MP và 300 DPI ≤ 6.3 MP; Chandra có prompt 579 token; peak = gửi cả 512 request cùng lúc. Không suy ra chất lượng ở 1540 px từ chất lượng ở cấu hình render của benchmark.[^lighton3]
- **Surya OCR 2.5, OmniParseBench pages:** một H100 80 GB, vLLM 0.25.1, concurrency 32, 300 trang mỗi resolution: **6.19 / 6.03 / 4.52 / 2.68** pages/s ở **96 / 150 / 192 / 300 DPI**; tại 192 DPI p50/p95 **6.8 / 11.3 s**. M4 Max 36 GB, Metal, 96 DPI, concurrency 8, 32 request: **0.190** (bf16) và **0.198** (Q8_0) pages/s, chỉ đếm trang xong trước token cap.[^surya25]
- **Chandra OCR 2 card:** H100 80 GB, vLLM, concurrency 96: **1.44** pages/s, mean / P95 **60 / 156 s**, 0% lỗi trong lần chạy đó; khác phép đo của LightOn.[^chandra2]
- **MinerU2.5-Pro card:** **2.12 fps** với `vllm-async-engine` trên một A100, không rõ workload.[^mineru2605]
- **Infinity-Parser2-Pro, tài liệu tài chính in-house:** H100, vLLM, `doc2json`, TP 2: concurrency 1 **173.58** tokens/s, **8.48 s**/trang; concurrency 8 **703.71** tokens/s, **2.13 s**/trang; khoảng 1,500 token output mỗi trang, không tính thời gian khởi động server. Bảng FinIE (95.75 F1) chỉ có Infinity-Parser2-**Flash** được fine-tune thêm, không có Pro.[^infinity2]

## 8. Coverage, exclusions và giới hạn

- **Observed:** đã đối chiếu bảng raw của mười model, card OvisOCR2 để lấy đúng hàng baseline, và các ảnh benchmark đã tải ngày 2026-10-30 (archive và manifest ghi nguồn tải, kể cả một file JPEG mang đuôi PNG khi tải lại).[^fetched-assets][^minicpm][^lighton3]
- **Đã kiểm tra, không có điểm cho mười model:** Tables 1–2 của Unlimited OCR Works 2 (MPDocBench, MarathonDocBench) chỉ có general VLM và model Unlimited. Ngoại lệ duy nhất có bằng chứng là MPDocBench-Parse truncated-table subset trong card OvisOCR3 (§5).[^unlimited2][^ovis3]
- **Loại vì khác model:** các bảng MonkeyOCRv2 về Total-Text, CTW1500, ICDAR2015, ArT, recognition, MathWriting, UniMER, DocTamper, MOT và VQA thuộc backbone/head hoặc B-Und, không phải B-Parsing; các ablation và checkpoint trung gian không được tính.[^monkey2]
- **Chưa có / không truy cập được:** output của model, dataset/gold, commit chung của scorer, chart tương tác, OmniParseBench per-tag parquet, manifest inference, khoảng tin cậy/kiểm định ý nghĩa cho phần lớn chênh lệch.
- **Unverified:** mọi hiệu năng vẫn do tác giả/vendor báo cáo; chưa có xác minh độc lập. `draft` phản ánh độ phủ protocol và attachment chưa đầy đủ.

## Contradictions

- **PaddleOCR-VL-1.6 text spotting:** phần prose của paper nói dẫn đầu cả chín category, nhưng bảng cho PaddleOCR-VL-1.5 cao hơn ở handwriting ZH (89.52 vs 85.90) và printing EN (86.89 vs 86.51). Trang này dùng số trong bảng.[^paddle16]
- Các mâu thuẫn giữa nguồn về điểm headline (MinerU Full, Chandra olmOCR, MDPBench Paddle, CHAOS, Wild, MiniCPM ảnh vs JSON) được ghi ở [trang chính](document-ocr-model-benchmark-comparison.md#contradictions).

## Relationships

- **Supplements:** [Document OCR model benchmark comparison](document-ocr-model-benchmark-comparison.md), trang chính cho cùng mười model; trang này không lặp lại các bảng headline của trang chính.
- **Uses:** [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md) và [End-to-end generative OCR VLM benchmarks](end-to-end-generative-ocr-vlm-benchmarks.md) làm bản đồ truy xuất theo họ kiến trúc.
- **Uses:** [LightOnOCR-3 evaluation](lightonocr-3-evaluation.md) và [MiniCPM-OCR evaluation](minicpm-ocr-evaluation.md) cho định nghĩa protocol của từng vendor.

[^fetched-assets]: [Archive và coverage ledger](../raw/ocr-benchmark-assets-2026-10-30/README.md) và các manifest; `mineru-pro-report.pdf` §§ 5.3–6.3, Tables 2–6, appendix Tables 7–8 (Base/Hard definitions, Hard end-to-end vector, crop tables); `mineru-{leaderboard,end2end,text_performance,formula_performance,table_performance}.png` đọc trực tiếp. Snapshot tải 2026-10-30; hash/URL trong manifest. Chỉ các phần benchmark liên quan của report lớn được tổng hợp.
[^minicpm]: [MiniCPM README](../raw/MiniCPM-OCR/README.md), revision b33b474; [JSON](../raw/MiniCPM-OCR/assets/minicpm-ocr/benchmark-data.json), `throughput.models`; [reproduction guide](../raw/MiniCPM-OCR/docs/benchmark_reproduction_en.md), §§ Scoring and Aggregation Rules (CHAOS-Bench), Parsing Efficiency Test; [model guide](../raw/MiniCPM-OCR/docs/minicpm_ocr_1dot0_en.md), § Throughput và bảng concurrency. Guide mô tả protocol, không phải bản reproduction chạy được đầy đủ.
[^ovis3]: [OvisOCR3 card](../raw/ATH-MaaS-OvisOCR3.md), § Performance, các bảng Document Parsing, KIE, Document Figure Captioning, Cross-Page Table Reconstruction. Cách chạy lại/chép comparator, split và nhiều evaluator không được nêu.
[^paddle16]: [PaddleOCR-VL-1.6 report](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex), Tables `tab:chart_parsing`, `tab:spotting`, `table:seal_results` và phần prose đi kèm.
[^teleocr]: [TeleOCR v3](../raw/arXiv-2608.12898v3-TeleOCR/main.tex), mô tả PureDocBench (§ Experimental Evaluation), Tables `tab:puredoc`, `tab:leaderboard_data_extraction`.
[^infinity2]: [Infinity-Parser2 report entry](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex); [experiments](../raw/2607.07836_Infinity-Parser2/latex/experiments.tex), Tables `layout_analysis_public`, `element_parsing_public`, `chart_parsing_public`, `chem_formula_parsing`, `general_mm_public`, `inference_speed`, `finie`; [appendix](../raw/2607.07836_Infinity-Parser2/latex/appendix.tex), § Evaluation Benchmarks cho định nghĩa task/split.
[^lighton3]: [LightOnOCR-3 blog](../raw/lightonocr-3/index.md), § 2 (bảng ParseBench và fr-bench-pdf2md, hàng Surya OCR 2); [speed table](../raw/lightonocr-3/assets/QKQIrgIR9NpILnyGLu9fW.png), hàng LightOnOCR-3-4B/Chandra-OCR-2 và footnote render/concurrency.
[^monkey2]: [MonkeyOCRv2 paper](../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex), các bảng text spotting, recognition, formula, tampering, VQA và encoder-transfer trong appendix; chỉ hàng B-Parsing được coi là kết quả của model đích.
[^mineru2605]: [MinerU2.5-Pro-2605 card](../raw/MinerU2.5-Pro-2605-1.2B.md), ghi chú hiệu năng trong Quick Start (vLLM async engine, A100).
[^chandra2]: [Chandra OCR 2 card](../raw/chandra-ocr-2.md), § Throughput.
[^surya25]: [Surya OCR 2.5 card](../raw/surya-ocr-2.5-hf.md), §§ Throughput › H100, Apple Silicon (llama.cpp / Metal).
[^ovis2-report]: [OvisOCR2 report entry](../raw/2607.13639_OvisOCR2/main.tex); [evaluation](../raw/2607.13639_OvisOCR2/content/evaluation.tex), `tab:puredoc_full`, `tab:inhouse_all`, `tab:inhouse_all_difficulty`, `tab:inhouse_handwriting`, `tab:inhouse_table`. Chỉ hàng MinerU2.5-Pro và PaddleOCR-VL-1.6 được tổng hợp.
[^unlimited2]: [Unlimited OCR Works 2](../raw/Unlimited-OCR-2.pdf), § 5, Tables 1–2 (MPDocBench/MarathonDocBench); đã kiểm tra thành phần bảng, không chạy lại.
