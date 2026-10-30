# So sánh các model End-to-end Generative OCR

## 1. Phạm vi và cách đọc kết quả

Ở đây, **end-to-end generative OCR** là nhóm model nhận ảnh trang tài liệu và sinh trực tiếp văn bản hoặc biểu diễn có cấu trúc như Markdown, HTML, JSON, LaTeX. Khác với pipeline layout-first, nhóm này không bắt buộc chạy một layout detector riêng trước khi nhận dạng. Xem [phân loại trong wiki](../wiki/task-end-to-end-generative-ocr.md).

Tôi tập trung vào **model, kích thước, ngày công bố và benchmark**; không đi sâu kiến trúc. Các điểm cần lưu ý trước khi so sánh:

- **Ngày trống nghĩa là chưa tìm thấy ngày ra mắt đáng tin cậy trong tài liệu đã kiểm tra**, không phải model chưa ra mắt. Ngày tạo trang wiki không phải ngày ra mắt model.
- **B** = tỷ tham số. Với model MoE, số tham số tổng và số tham số hoạt động cho mỗi token khác nhau; cũng không nên dùng chỉ số đó như ước lượng trực tiếp VRAM.
- Các benchmark dưới đây chủ yếu là **kết quả do tác giả/model card báo cáo hoặc chép từ leaderboard**; wiki chưa chạy lại độc lập.
- Không ghép điểm giữa các benchmark hoặc các phiên bản benchmark thành một bảng xếp hạng chung. Ngay cả cùng tên benchmark, prompt, render PDF, retry và evaluator có thể khác nhau.

Nguồn chính là [catalog benchmark end-to-end](../wiki/end-to-end-generative-ocr-vlm-benchmarks.md), bổ sung bằng các trang model riêng và hai trang so sánh theo dataset: [Document OCR model benchmark comparison](../wiki/document-ocr-model-benchmark-comparison.md) và [phụ lục bằng chứng](../wiki/ocr-ten-model-benchmark-comparison.md).

**Phạm vi model:** tài liệu này chỉ giữ các model end-to-end theo [phân loại trong wiki](../wiki/task-end-to-end-generative-ocr.md), cộng **Surya OCR 2.5** là hệ thống ranh giới vì chế độ mặc định của nó là OCR toàn trang. Trong mười model của hai trang so sánh trên, chỉ **Chandra OCR 2, OvisOCR3, Infinity-Parser2-Pro và LightOnOCR-3** thuộc nhóm này. **Xiaomi-OCR-0** có giao diện whole-page mặc định và chỉ có tùy chọn layout-first, nên được đưa vào đây. Các model layout-first gồm **TeleOCR, PaddleOCR-VL, MinerU2.5, MiniCPM-OCR 1.0, MonkeyOCRv2-B-Parsing và SenOCR-Vi** đã được loại khỏi các bảng; xem [so sánh layout-first](so-sanh-cac-model-ocr-theo-huong-layout-first-modular.md). Ký hiệu nguồn: **[M]** = MiniCPM tự chạy (bên cạnh tranh); **[L]** = blog LightOn; **[OPB]** = Datalab chạy OmniParseBench.

---

## 2. Bảng tổng quan model

| Model | Size | Ngày ra mắt được ghi nhận | Kết quả đáng chú ý | Nhận xét ngắn |
|---|---:|---|---|---|
| [OvisOCR3](../wiki/ovisocr3.md) | **0.8B** | Chưa ghi rõ | OmniDocBench 1.6 **96.74**; Real5 **93.63**; MDPBench **88.8**; PureDocBench **82.31** | Model nhỏ, nhiều tác vụ; card chỉ công bố điểm tổng. Điểm MDPBench 88.8 do card tự báo cáo, không có trong README MDPBench chính thức và không nêu split. |
| [OvisOCR2](../wiki/ovisocr2.md) | **0.8B** | Chưa ghi rõ | OmniDocBench 1.6 **96.58**; PureDocBench Avg3 **75.06** | Có bảng thành phần text/formula/table/order chi tiết hơn OvisOCR3. |
| [Xiaomi-OCR-0](../wiki/xiaomi-ocr-0.md) | **0.8B** | **30/09/2026** (phát hành weights), theo model card | OmniDocBench 1.6 **96.83**; Real5 **95.24**; Wild **87.94** | Card không nêu điểm chạy ở chế độ whole-page hay two-stage. Prompt whole-page bỏ header/footer, còn bảng được xuất dạng OTSL. Card OvisOCR3 chép Real5 của model này là **92.73**. |
| [LightOnOCR-3](../wiki/lightonocr-3.md) | **0.8B / 1B / 4B** | Chưa xác nhận ngày ra mắt | Bản 4B: olmOCR-Bench **86.3**, ParseBench 5 mục **75.1**, fr-bench-pdf2md **74.1**, OmniParseBench **82.9** [OPB]; bản 1B: OmniDocBench 1.6 **89.87** [M] | Blog nhà phát hành báo cáo phần lớn benchmark; hỗ trợ transcription và grounding. Không có điểm OmniDocBench cho bản 4B. [Chi tiết](../wiki/lightonocr-3-evaluation.md). |
| [LightOnOCR-2-1B](../wiki/lightonocr.md) | **1B** | Chưa ghi rõ | olmOCR-Bench **83.2 ± 0.9** | Điểm loại header/footer khỏi aggregate, không so trực tiếp với các dòng giữ các mục này. |
| [HunyuanOCR-1.5](../wiki/hunyuanocr-1.5.md) | Bảng so sánh gọi family là **1B**; card không xác nhận size | **07/07/2026**, theo README | OmniDocBench 1.6 **94.74** trong bảng OvisOCR2 | Có kết quả được bên khác chép lại; card/README được lưu không có bảng benchmark riêng. |
| [FireRed-OCR](../wiki/firered-ocr.md) | **2B** | Chưa ghi rõ | OmniDocBench 1.5 **92.94**; 1.6 **93.26** | Có cả bảng benchmark chuẩn và benchmark nội bộ cho trang biến dạng. |
| [Infinity-Parser2 Flash](../wiki/infinity-parser2.md) | **2B** | **11/05/2026**, theo model card | OmniDocBench 1.6 **91.98**; olmOCR-Bench **86.0 ± 0.8** | Điểm ở hai benchmark đến từ bảng đánh giá của nhóm tác giả. |
| [Infinity-Parser2 Pro](../wiki/infinity-parser2.md) | **35B tổng / 3B active** | **11/05/2026**, theo model card | OmniDocBench 1.6 **93.95**; olmOCR-Bench **87.6 ± 0.8**; OmniParseBench **87.0** [OPB]; ParseBench 5 mục **74.3** [L] | Bản lớn hơn Flash; active parameter không thể hiểu là chỉ cần bộ nhớ như model dense 3B. |
| [DeepSeek-OCR 2](../wiki/deepseek-ocr-2.md) | Decoder **3B MoE / ~0.5B active** | Chưa ghi rõ | OmniDocBench 1.5 **91.09**; 1.6 **90.25** | Size nêu theo decoder; các báo cáo khác nhau cho điểm 1.5 khác nhau. |
| [Unlimited OCR](../wiki/unlimited-ocr.md) | **3B tổng / 0.5B active** | Chưa ghi rõ | OmniDocBench 1.5 **93.23**; 1.6 **93.92** | Có thêm đánh giá tài liệu nhiều trang do tác giả xây dựng. |
| [Unlimited OCR 2](../wiki/unlimited-ocr-2.md) | Báo cáo nêu **3B tổng / 0.5B active** | Chưa ghi rõ | OmniDocBench 1.6 **94.02**; MPDocBench **84.59**; MarathonDocBench **77.06** | Tập trung tài liệu dài; bảng điểm đơn trang đến từ báo cáo riêng. |
| [Qianfan-OCR](../wiki/qianfan-ocr.md) | **4B** | Chưa ghi rõ | OmniDocBench 1.5 **93.12**; 1.6 **93.90** | Có thêm bảng cho general OCR, VQA và KIE. |
| [dots.ocr](../wiki/dots-ocr.md) | Card nêu **1.7B LLM foundation**; bảng khác ghi 3B | Chưa ghi rõ | OmniDocBench 1.6 **90.77**; olmOCR-Bench **79.1 ± 1.0** | Cần phân biệt `dots.ocr` gốc với 1.5 và dots.mocr. |
| [olmOCR-2-7B-1025](../wiki/olmocr-2-7b-1025.md) | **7B** | Chưa ghi rõ | olmOCR-Bench **82.3 ± 1.1** BF16; **82.4 ± 1.1** FP8 | Cần chú ý PDF metadata/anchoring và toolkit khi đối chiếu benchmark. |
| [Chandra OCR 2](../wiki/chandra-ocr-2.md) | **5.3B trong bảng so sánh**; card riêng không xác nhận | Chưa ghi rõ | olmOCR-Bench **85.8 ± 0.8** theo card; OmniParseBench **90.1** [OPB]; MDPBench **79.7** (VI 85.6); ParseBench 5 mục **70.1** [L]; OmniDocBench 1.6 **92.27** [M] | Dẫn OmniParseBench, nhưng benchmark này do chính Datalab xây và chạy. Có giới hạn thương mại cho weights; phải kiểm tra license trước khi chọn. |
| [Nanonets-OCR2](../wiki/nanonets-ocr2.md) | **3B**, thử nghiệm **1.5B**; Plus hosted | Chưa ghi rõ | Bản 3B: ChartQA **78.56**, DocVQA **89.43** | Hữu ích khi cần cả parsing và VQA; cấu hình benchmark không được mô tả đầy đủ. |
| [Typhoon OCR 1.5](../wiki/typhoon-ocr.md) | **2B** | Chưa ghi rõ | Bộ Thai nội bộ: BLEU **0.644**, ROUGE-L **0.774** | Chuyên Thai/English; không so trực tiếp các điểm này với OmniDocBench. |
| [Surya OCR 2.5](../wiki/surya-ocr-2-5.md) | **689M** | Chưa xác nhận ngày ra mắt | OmniParseBench **85.9**; olmOCR-bench **83.7** | Hệ thống ranh giới: mặc định sinh HTML theo trang, tùy chọn OCR theo block sau layout; cần kiểm tra license weights. |
| [Granite Docling](../wiki/granite-docling-258m.md) | **258M** | Chưa ghi rõ | Full-page OCR edit **0.45** trong model-card evaluation | Model rất nhỏ, nhưng thuộc nhóm ranh giới: được định vị là thành phần trong Docling. |
| [NVIDIA Nemotron Parse v1.1 / 2.0](../wiki/nemotron-parse-2-0.md) | Cả hai được mô tả là **dưới 1B** | Chưa ghi rõ | Card v1.1 được lưu **không có kết quả số** | Model trực tiếp page-to-structure; chưa đủ bảng đối chiếu trong catalog này. |

**Về ngày ra mắt:** Trong các tài liệu model đã kiểm tra, tôi chỉ thấy ngày cụ thể cho **HunyuanOCR-1.5**, **Infinity-Parser2** và **Xiaomi-OCR-0** như trên. Đây là ngày do nhà phát hành công bố, chưa kiểm tra độc lập. Không dùng ngày tạo trang wiki hay mã thư mục paper làm ngày release.

---

## 3. Benchmark quan trọng nhất: OmniDocBench v1.6

Đây là bảng gần nhất trong wiki có nhiều model end-to-end được đặt cạnh nhau. Nó được [OvisOCR2 báo cáo/chép lại](../wiki/end-to-end-generative-ocr-vlm-benchmarks.md); phiên bản checkpoint và cấu hình evaluator của các dòng chưa hoàn toàn đồng nhất.

**Overall, Formula CDM, Table TEDS:** càng cao càng tốt.  
**Text edit và Order edit:** càng thấp càng tốt.

| Model | Size | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| **OvisOCR2** | **0.8B** | **96.58** | **0.025** | **97.53** | **94.76** | **0.111** |
| HunyuanOCR-1.5 | ~1B theo bảng | 94.74 | 0.039 | 94.50 | 93.67 | 0.129 |
| Unlimited OCR | 3B / 0.5B active | 93.92 | 0.042 | 95.79 | 90.16 | 0.129 |
| Qianfan-OCR | 4B | 93.90 | 0.040 | 95.08 | 90.53 | 0.130 |
| FireRed-OCR | 2B | 93.26 | 0.037 | 95.44 | 88.04 | 0.131 |
| dots.ocr | 1.7B foundation | 90.77 | 0.048 | 89.95 | 87.18 | 0.138 |
| DeepSeek-OCR 2 | 3B decoder / ~0.5B active | 90.25 | 0.050 | 91.84 | 83.89 | 0.144 |
| olmOCR — tên như trong bảng | Không xác định chính xác checkpoint | 85.74 | 0.139 | 88.10 | 83.00 | 0.216 |
| Nanonets-OCR-S | Không xác định trong bảng | 83.61 | 0.108 | 81.46 | 80.18 | 0.213 |

### OvisOCR3, Infinity-Parser2 và các dòng từ nguồn khác: giữ riêng nguồn

| Model | Size | OmniDocBench 1.6 overall | Nguồn và giới hạn |
|---|---:|---:|---|
| Xiaomi-OCR-0 | 0.8B | **96.83** | Model card Xiaomi-OCR-0; card OvisOCR3 chép cùng số. Chưa rõ chế độ whole-page hay two-stage. |
| OvisOCR3 | 0.8B | 96.74 | Model card OvisOCR3; không công bố vector thành phần. |
| OvisOCR2 | 0.8B | 96.58 | Dòng đối chiếu trong cùng card OvisOCR3. |
| Unlimited OCR 2 | 3B / 0.5B active | 94.02 | Bảng riêng trong báo cáo Unlimited OCR 2. |
| Infinity-Parser2 Pro | 35B / 3B active | 93.95 | Bảng riêng của Infinity-Parser2. |
| Chandra OCR 2 | 5.3B trong bảng so sánh | 92.27 | [M], chỉ overall; card Chandra không báo OmniDocBench. |
| Infinity-Parser2 Flash | 2B | 91.98 | Cùng bảng Infinity-Parser2 Pro. |
| LightOnOCR-3-1B | 1B | 89.87 | [M], chỉ overall; không có số cho bản 4B. |

**Diễn giải:**

1. Trong bảng OvisOCR2, **OvisOCR2 dẫn tất cả thành phần được liệt kê**, dù chỉ 0.8B. Đây là kết quả rất đáng chú ý để đưa vào shortlist, không phải bằng chứng nó thắng mọi bộ dữ liệu.
2. Card OvisOCR3 báo **96.74 so với OvisOCR2 96.58**, nhưng chỉ có overall và không nêu đầy đủ cách chạy comparator. Chênh lệch **0.16 điểm** không đủ để khẳng định mức cải thiện thực tế trên tài liệu của bạn.
3. Không nên sắp Infinity-Parser2 hay Unlimited OCR 2 vào cùng thứ hạng chính xác với bảng đầu: chúng đến từ **bảng và protocol khác**. Chandra OCR 2 và LightOnOCR-3-1B do MiniCPM, một bên cạnh tranh, chạy.
4. Xiaomi-OCR-0 (96.83), OvisOCR3 (96.74) và OvisOCR2 (96.58) cách nhau dưới 0.3 điểm và đều chỉ có overall do nhà phát hành báo cáo. Khoảng cách này không đủ để xếp hạng chắc chắn giữa ba model 0.8B.

---

## 4. OmniDocBench v1.5: xem thêm nhưng không cộng gộp với v1.6

Các điểm trong bảng này dùng schema v1.5, **không so trực tiếp bằng số với v1.6**. Các dòng cũng đến từ nhiều báo cáo.

| Model | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|
| Unlimited OCR | **93.23** | 0.038 | 92.61 | 90.93 | 0.045 |
| Qianfan-OCR | 93.12 | 0.041 | 92.43 | 91.02 | 0.049 |
| FireRed-OCR | 92.94 | **0.032** | 91.71 | 90.31 | **0.041** |
| DeepSeek-OCR 2 | 91.09 | 0.048 | 90.31 | 87.75 | 0.057 |
| dots.ocr | 88.41 | 0.048 | 83.22 | 86.78 | 0.053 |
| DeepSeek-OCR | 87.36 | 0.073 | 84.14 | 85.25 | 0.085 |

**Điểm đáng chú ý:** FireRed có text/order edit tốt nhất trong các dòng trên; Qianfan có table TEDS cao hơn FireRed. Tuy nhiên, **không coi các khác biệt nhỏ là kết luận chắc chắn**, vì chúng được tổng hợp từ nhiều báo cáo. Ví dụ, một bảng khác báo DeepSeek-OCR 2 **89.17**, thay vì **91.09**, dù đều mang nhãn v1.5. [Nguồn và protocol](../wiki/end-to-end-generative-ocr-vlm-benchmarks.md).

---

## 5. PureDocBench: tài liệu sạch so với ảnh thực tế

PureDocBench tách ba điều kiện: **Clean**, **Digital** và **Real**. Bảng dưới đây từ báo cáo OvisOCR2; **Avg3 càng cao càng tốt**.

| Model | Clean ↑ | Digital ↑ | Real ↑ | Avg3 ↑ |
|---|---:|---:|---:|---:|
| **OvisOCR2** | **81.55** | **77.09** | **66.56** | **75.06** |
| FireRed-OCR | 70.81 | 68.49 | 57.42 | 65.57 |
| dots.ocr | 72.01 | 65.95 | 55.68 | 64.55 |
| olmOCR-2-7B | 69.36 | 65.87 | 56.10 | 63.78 |
| Nanonets-OCR2 | 64.83 | 61.23 | 49.03 | 58.36 |
| Qianfan-OCR | 57.22 | 50.85 | 45.06 | 51.04 |
| DeepSeek-OCR 2 | 55.53 | 49.41 | 43.60 | 49.51 |
| DeepSeek-OCR | 53.50 | 46.95 | 40.48 | 46.98 |

Trong bảng này, OvisOCR2 dẫn cả ba track, với khoảng cách gần 10 điểm Avg3 so với FireRed-OCR. Tuy nhiên, đây là bảng do tác giả OvisOCR2 báo cáo, nên không thể kết luận OvisOCR2 tốt nhất cho mọi ảnh chụp thực tế. [Nguồn](../wiki/end-to-end-generative-ocr-vlm-benchmarks.md).

Card OvisOCR3 báo **82.31 overall** trên PureDocBench nhưng không nêu cách tính overall và **không công bố Clean/Digital/Real**. Do đó, không thể đối chiếu mức cải thiện theo từng điều kiện hay coi con số này là Avg3. Cùng cột trong card ghi OvisOCR2 **75.10** (bảng OvisOCR2 trên ghi Avg3 75.06), Xiaomi-OCR-0 **74.60** và HunyuanOCR-1.5 **67.58**. [Nguồn](../wiki/end-to-end-generative-ocr-vlm-benchmarks.md).

### Real5 và Wild-OmniDocBench: biến dạng vật lý

| Model | Real5 overall ↑ | Wild, giao thức [M] ↑ | Nguồn |
|---|---:|---:|---|
| OvisOCR3 | 93.63 | — | Card OvisOCR3 |
| Chandra OCR 2 | 88.74 | 89.08 | [M] |
| LightOnOCR-3-1B | 83.62 | 84.36 | [M] |
| Xiaomi-OCR-0 | 95.24 (card OvisOCR3: 92.73) | — | Card Xiaomi-OCR-0 |
| OvisOCR2 | 92.29 | — | Card Xiaomi-OCR-0 và card OvisOCR3 |
| HunyuanOCR-1.5 | 88.53 | — | Card OvisOCR3 |

Real5 gồm năm điều kiện: scan, warp, screen photo, illumination và skew. Không model end-to-end nào ở đây công bố điểm theo từng điều kiện. Real5 của Xiaomi-OCR-0 lệch **2.51 điểm** giữa card của chính nó và card OvisOCR3, vượt quá khoảng cách giữa các model dẫn đầu, nên chưa thể xếp Xiaomi và OvisOCR3 trên Real5. Card Xiaomi cũng báo Wild **87.94** (OvisOCR2 **87.91**) theo giao thức khác cột [M]. Cùng một model có thể chênh 2–3 điểm giữa hai giao thức, nên chỉ so trong cùng cột. [Nguồn](../wiki/document-ocr-model-benchmark-comparison.md).

---

## 6. olmOCR-Bench: hữu ích, nhưng cần đọc protocol

olmOCR-Bench dùng các unit test theo loại tài liệu/tác vụ; điểm dưới đây là **overall pass rate**. Bảng này **trộn các nguồn báo cáo**, vì vậy phù hợp để chọn model thử nghiệm hơn là tuyên bố thứ hạng chính xác.

| Model | Kết quả ↑ | Lưu ý |
|---|---:|---|
| Infinity-Parser2 Pro | **87.6 ± 0.8** | Pipeline đánh giá của tác giả; blog LightOn cũng ghi 87.6 sau postprocessing (raw 85.9). |
| LightOnOCR-3-4B | **86.3** | Blog LightOn, có postprocessing (raw 85.0); không nêu khoảng bất định. |
| Infinity-Parser2 Flash | **86.0 ± 0.8** | Pipeline đánh giá của tác giả. |
| Chandra OCR 2 | **85.8 ± 0.8** | Card Datalab tự chạy; LightOn ghi raw 85.1 → 85.8. Báo cáo Infinity-Parser2 chép 83.1 ± 0.9, trùng số của Chandra 1 nên có thể đã gán nhầm; ảnh GitHub của Infinity ghi 85.9. |
| LightOnOCR-3-0.8B / 1B | **85.5 / 84.5** | Blog LightOn, có postprocessing; không nêu khoảng bất định. |
| dots.ocr 1.5 / dots.mocr | 83.9 | Tên version không thống nhất giữa card/báo cáo. |
| [Surya OCR 2.5](../wiki/surya-ocr-2-5.md) | **83.7** | Datalab báo trung bình ba lượt, plain output; Surya 2 đạt 82.8 trong cùng báo cáo. |
| Chandra OCR | 83.1 ± 0.9 | Kết quả nhà cung cấp. |
| LightOnOCR-2-1B | 83.2 ± 0.9 | **Loại header/footer** khỏi aggregate. |
| olmOCR-2-7B BF16 | 82.3 ± 1.1 | Toolkit v0.4.0 có render, rotation và retry. |
| olmOCR-2-7B FP8 | 82.4 ± 1.1 | Cùng toolkit; card khuyến nghị FP8 cho sử dụng thực tế. |
| dots.ocr gốc | 79.1 ± 1.0 | Không nhầm với dots.ocr 1.5. |
| Qianfan-OCR | 79.8 | Kết quả từ báo cáo Qianfan. |

**Điểm chính:** Infinity-Parser2, Chandra 2 và LightOnOCR-3 là các ứng viên đáng thử trên tài liệu kiểu olmOCR-Bench, nhưng sự khác nhau về **anchoring, category, retry, postprocessing và evaluator** ngăn việc kết luận model nào sẽ thắng khi chạy cùng một pipeline. [Catalog benchmark](../wiki/end-to-end-generative-ocr-vlm-benchmarks.md); [đánh giá LightOnOCR-3](../wiki/lightonocr-3-evaluation.md).

### Cùng bảng do LightOn báo cáo: chất lượng và tốc độ

Bảng sau giữ riêng kết quả trong blog LightOn; các điểm **cao hơn là tốt hơn**, là kết quả nhà phát hành chọn và chạy, chưa được tái lập độc lập. ParseBench dùng overall **5 category**; không trộn với overall 3 category hay benchmark khác. [Nguồn và giới hạn](../wiki/lightonocr-3-evaluation.md).

| Model | olmOCR-Bench ↑ | ParseBench 5 mục ↑ | fr-bench-pdf2md ↑ |
|---|---:|---:|---:|
| LightOnOCR-3-0.8B | 85.5 | 74.6 | 70.5 |
| LightOnOCR-3-1B | 84.5 | 71.4 | 69.6 |
| LightOnOCR-3-4B | 86.3 | 75.1 | 74.1 |
| Infinity Parser Pro | 87.6 | 74.3 | 63.2 |
| Chandra 2 | 85.8 | 70.1 | 69.0 |

Theo bảng này, bản 4B đứng đầu các dòng được công bố trên ParseBench và fr-bench-pdf2md, còn Infinity dẫn olmOCR-Bench. Kết quả thay đổi theo loại tài liệu; trên ParseBench visual grounding, Infinity đạt 74.9 so với 68.3 của 4B. Không suy ra thứ hạng toàn cầu hay ý nghĩa thống kê từ các chênh lệch nhỏ. Trên olmOCR-Bench, postprocessing đổi thứ hạng top 3: điểm raw là Infinity **85.9**, Chandra 2 **85.1**, 4B **85.0**; sau xử lý lần lượt là **87.6 / 85.8 / 86.3**. Vì vậy, chênh lệch dưới 2 điểm phụ thuộc vào bước chuẩn hóa. Nếu dùng ParseBench overall **3 category**, thứ tự vẫn là 4B **80.4**, Infinity **78.4**, Chandra 2 **78.1**. Không trộn thang này với thang 5 category.

Về serving, tác giả dùng cùng 512 trang olmOCR, một H100/model và vLLM 0.30.0. Ở cấu hình render benchmark riêng của mỗi model, 0.8B / 1B / 4B lần lượt đạt latency trung vị **3.8 / 2.7 / 6.6 giây** mỗi trang và throughput đỉnh **3.32 / 3.52 / 2.03 trang/giây**; Chandra 2 đạt **8.1 giây** và **1.68 trang/giây**. Render và prompt khác nhau; ở 1540 px cạnh dài, throughput đỉnh 4B là **3.36**, Chandra 2 là **2.95 trang/giây**. Cấu hình này không chứng minh chất lượng khi giảm độ phân giải và không bảo đảm tốc độ trên phần cứng khác. [Chi tiết setup](../wiki/lightonocr-3-evaluation.md).

Các phép đo tốc độ khác dùng phần cứng hoặc workload khác nên **không so chéo** ([chi tiết](../wiki/ocr-ten-model-benchmark-comparison.md)):

- **Chandra OCR 2 card:** H100, vLLM, 96 request đồng thời: **1.44 trang/giây**, latency trung bình / P95 **60 / 156 giây**.
- **Infinity-Parser2 Pro:** H100, TP 2, 8 request đồng thời, tài liệu tài chính in-house: **2.13 giây/trang**, khoảng 1,500 token output mỗi trang.
- **[M], RTX 5090, 1 ảnh đồng thời:** LightOnOCR-3 **0.340** (không nêu biến thể) và Chandra OCR 2 **0.068** trang/giây.

---

### OmniParseBench (Datalab chạy, 16,288 test pass/fail, 2,937 trang)

Headline là trung bình của text, tables và layout. Datalab chạy các model open-weight bằng server image của `omni-parse-bench`, với cấu hình mặc định do vendor khuyến nghị. Datalab cũng là tác giả Chandra và Surya, nên đây là bằng chứng do vendor chạy. [Nguồn](../wiki/document-ocr-model-benchmark-comparison.md).

| Model | Headline ↑ | Text ↑ | Tables ↑ | Layout ↑ |
|---|---:|---:|---:|---:|
| Chandra OCR 2 | **90.1** | **87.4** | 87.4 | 95.4 |
| Infinity-Parser2 Pro | 87.0 | 83.3 | 84.1 | 93.5 |
| Surya OCR 2.5 | 85.9 | 83.8 | 78.3 | **95.7** |
| LightOnOCR-3-4B | 82.9 | 83.9 | 70.8 | 94.0 |
| LightOnOCR-3-0.8B | 81.6 | 81.1 | 72.1 | 91.7 |

Chandra OCR 2 dẫn headline, text và tables; Surya OCR 2.5 dẫn layout. LightOnOCR-3-4B yếu nhất ở tables (70.8). OvisOCR3 và Xiaomi-OCR-0 không có trong benchmark này.

### Surya OCR 2.5 so với Surya OCR 2 trên OmniParseBench

Theo [model card Surya 2.5 được tổng hợp trong wiki](../wiki/surya-ocr-2-5.md), hai checkpoint đạt **85.9 so với 83.3 overall**, **83.8 so với 81.0 text**, **78.3 so với 74.3 table** và **95.7 so với 94.5 layout**. Datalab báo dùng `surya-ocr` 0.23.0, 192 DPI, public scorer và một lượt mỗi model; khoảng tin cậy bootstrap cặp 95% cho chênh lệch overall là **+1.6 đến +3.7 điểm**. Đây là kết quả nhà phát hành, chưa được tái lập; OmniParseBench không phải OmniDocBench hay ParseBench trong các bảng trên.

Surya 2.5 mặc định sinh các block HTML có thứ tự và tọa độ trong một lượt VLM/trang; chế độ tùy chọn chạy layout trước rồi OCR từng block. Chế độ bảng đầy đủ sinh HTML có ô gộp, nhưng `--mode simple` lấy hình học hàng/cột cần checkpoint Surya 2, không hỗ trợ 2.5. Theo cùng nguồn, throughput 2.5 là **4.52 trang/giây** trên H100 80 GB, 192 DPI, 32 request đồng thời và 300 trang, với server vLLM đã chạy; không so trực tiếp tốc độ này với setup LightOn ở trên. [Chi tiết triển khai](../wiki/surya-ocr-2-5-deployment.md).

---

## 7. Tiếng Việt và tài liệu nhiều trang

### 7.1. Tiếng Việt và đa ngôn ngữ

Không model end-to-end nào trong tài liệu này được huấn luyện chuyên cho tiếng Việt. Baseline chuyên Việt [SenOCR-Vi](../wiki/senocr-vi.md) là bản fine-tune bộ nhận dạng của PaddleOCR-VL-1.6, nên thuộc hướng layout-first và nằm trong [tài liệu layout-first](so-sanh-cac-model-ocr-theo-huong-layout-first-modular.md).

| Model | Benchmark | Tiếng Việt ↑ | Bối cảnh |
|---|---|---:|---|
| Chandra OCR 2 | [MDPBench](../wiki/mdpbench.md), README chính thức (tải 2026-10-30), cột VI | **85.6** | All / Digital / Photo **79.7** / 87.8 / 77.1 trên 17 ngôn ngữ |
| Chandra OCR 2 | Bộ nội bộ 90 ngôn ngữ của Datalab | **82.6%** | Overall 72.7% |
| [Surya OCR 2.5](../wiki/surya-ocr-2-5.md) | Bộ nội bộ 91 ngôn ngữ của Datalab, phiên bản "khó hơn" | **63.6%** | Surya 2 đạt 57.9% trên cùng bộ |

Hai bộ nội bộ của Datalab không dùng cùng tập test, nên không so Surya với Chandra. Hai bộ này cũng **không so trực tiếp** với cột VI của MDPBench. [Nguồn](../wiki/document-ocr-model-benchmark-comparison.md).

Các điểm MDPBench overall khác **không có cột tiếng Việt**: card OvisOCR3 tự báo OvisOCR3 **88.8**, HunyuanOCR-1.5 76.8, Xiaomi-OCR-0 73.0 và OvisOCR2 69.0. Card không nêu split, và OvisOCR3 không có trong README chính thức. README chính thức ghi LightOnOCR-2-1B **63.9**. Không ghép các số tự báo này với bảng README.

### 7.2. Cross-page và tài liệu rất dài

| Model | Kết quả do tác giả báo cáo | Phù hợp khảo sát khi |
|---|---|---|
| [OvisOCR3](../wiki/ovisocr3.md) | CrossTabBench relation F1 **97.07** (P/R 96.20 / 97.96); reconstruction TEDS **89.66**; MPDocBench-Parse truncated-table TEDS **92.04**. Card không có model end-to-end nào khác để đối chứng. | Muốn phát hiện và ghép bảng qua các trang liên tiếp. |
| [Unlimited OCR 2](../wiki/unlimited-ocr-2.md) | MPDocBench overall **84.59**, table TEDS **89.54**; MarathonDocBench overall **77.06**, table TEDS **71.11** | Muốn parse tài liệu dài; báo cáo thử nghiệm quy mô hàng trăm trang. |

Các giá trị cross-page ở hai dòng **không cùng benchmark**, nên không so trực tiếp 89.66 với 89.54. Với OvisOCR3, phát hiện bảng tiếp nối và tái tạo đúng bảng cũng là hai việc khác nhau: relation F1 cao không bảo đảm reconstruction TEDS cao tương ứng.

---

## 8. Chọn model nào để thử trước?

Đây là **đề xuất tổng hợp**, không phải kết quả benchmark độc lập:

| Nhu cầu | Shortlist | Lý do |
|---|---|---|
| **Một model nhỏ để parse trang đa dụng** | **OvisOCR3, OvisOCR2, Xiaomi-OCR-0** | Cả ba đều 0.8B và có điểm OmniDocBench 1.6 tự báo từ 96.58 đến 96.83. OvisOCR3 có nhiều loại output hơn; Xiaomi có thêm tùy chọn chạy theo vùng. |
| **Ảnh chụp hoặc scan suy giảm** | **OvisOCR3, Xiaomi-OCR-0, OvisOCR2, FireRed-OCR** | OvisOCR3 tự báo Real5 93.63 và PureDocBench 82.31 (chỉ overall). Xiaomi tự báo Real5 95.24, nhưng card OvisOCR3 ghi 92.73. OvisOCR2 có PureDocBench theo track. Cần tự kiểm tra theo camera, ngôn ngữ và độ méo của dữ liệu. |
| **Tài liệu Việt** | **Chandra OCR 2** | Chandra có MDPBench VI 85.6, cao nhất bảng chính thức, và 82.6% trên bộ 90 ngôn ngữ của Datalab. Cần kiểm tra license. Baseline chuyên Việt SenOCR-Vi thuộc [hướng layout-first](so-sanh-cac-model-ocr-theo-huong-layout-first-modular.md). |
| **Tài liệu nhiều trang, bảng nối trang** | **OvisOCR3, Unlimited OCR 2** | Có đánh giá riêng cho cross-page hoặc long-document. |
| **Markdown + tọa độ / structured extraction** | **OvisOCR3, Infinity-Parser2 Flash/Pro, dots.ocr; Surya OCR 2.5** | Có các chế độ JSON/layout hoặc output theo tác vụ; Surya sinh HTML block có tọa độ và cần kiểm tra license weights. |
| **PDF kiểu unit-test (olmOCR-Bench / OmniParseBench / ParseBench)** | **Infinity-Parser2 Flash/Pro, Chandra OCR 2, LightOnOCR-3-4B** | Infinity dẫn olmOCR (87.6), Chandra dẫn OmniParseBench (90.1), LightOnOCR-3-4B dẫn ParseBench (75.1) và fr-bench (74.1). Mỗi bảng do một vendor khác chạy, protocol chưa đồng nhất và bước postprocessing có thể đổi thứ hạng. |
| **Thai/English** | **Typhoon OCR 1.5** | Chuyên biệt ngôn ngữ và có benchmark Thai nội bộ, nhưng không có đối chiếu công bằng với toàn bộ shortlist. |
| **Muốn thử grounding nhẹ** | **LightOnOCR-3 0.8B**, đối chiếu **4B** | Có bounding box, mô tả ảnh và bảng dữ liệu biểu đồ; blog báo cáo benchmark và tốc độ, nhưng cần kiểm thử trên dữ liệu thực tế. |

### Nếu phải bắt đầu bằng 3 model end-to-end

Cho một bài toán tài liệu hỗn hợp có tiếng Việt, tôi sẽ thử:

1. **OvisOCR3 0.8B** — baseline end-to-end nhỏ, nhiều tác vụ.
2. **Chandra OCR 2** — đối chiếu multilingual/Vietnamese, sau khi kiểm tra license.
3. **Infinity-Parser2 Flash 2B** — đối chiếu output có cấu trúc và olmOCR-Bench.

Nếu cần so với một baseline pipeline chuyên tiếng Việt, hãy dùng SenOCR-Vi từ [tài liệu layout-first](so-sanh-cac-model-ocr-theo-huong-layout-first-modular.md).

Đánh giá trên **cùng bộ trang của bạn**, giữ nguyên DPI, prompt, output schema và retry; tách ít nhất các nhóm **văn bản Việt có dấu, bảng, công thức, chữ viết tay, ảnh chụp, nhiều cột và bảng qua trang**. Báo riêng chất lượng và latency/VRAM thay vì chỉ lấy một điểm tổng.

**Giới hạn kiểm tra:** Lượt cập nhật mới nhất đối chiếu mọi số của Chandra OCR 2, OvisOCR3, Infinity-Parser2 Pro, LightOnOCR-3 và Surya OCR 2.5 với [Document OCR model benchmark comparison](../wiki/document-ocr-model-benchmark-comparison.md) và [phụ lục bằng chứng](../wiki/ocr-ten-model-benchmark-comparison.md). Các số đã có đều khớp; lượt này sắp xếp lại bảng olmOCR và bổ sung OmniParseBench, Real5/Wild, MDPBench, điểm raw so với postprocessed và throughput. Không chạy benchmark hay model. **Rà soát ngày 2026-10-30:** đã loại mọi model layout-first gồm TeleOCR, PaddleOCR-VL-1.6, MinerU2.5-Pro, MiniCPM-OCR 1.0, MonkeyOCRv2-B-Parsing và SenOCR-Vi, theo [phân loại task](../wiki/task-layout-first-modular-parsing.md) và [trang MonkeyOCRv2](../wiki/monkeyocrv2.md). Xiaomi-OCR-0 được chuyển từ tài liệu layout-first sang đây. Các số của Xiaomi và các cột MDPBench, PureDocBench, Real5 lấy từ card OvisOCR3 được đối chiếu trực tiếp với [card Xiaomi-OCR-0](../raw/Xiaomi-OCR-0.md) và [card OvisOCR3](../raw/ATH-MaaS-OvisOCR3.md). Các model không thuộc mười model của trang so sánh (OvisOCR2, FireRed, Qianfan, Unlimited, DeepSeek, dots.ocr, olmOCR-2…) giữ nguyên kết quả và giới hạn của bản trước. Kết quả là số do nguồn báo cáo; bản so sánh này được giữ trong `outputs/`, không ghi thêm vào wiki.