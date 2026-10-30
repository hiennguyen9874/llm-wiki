# So sánh các model OCR theo hướng layout-first modular

**Kết luận nhanh:** Trong các bảng đã kiểm tra, [TeleOCR](../wiki/teleocr.md) đạt **96,87** trên OmniDocBench v1.6 Full, cao nhất trong các model layout-first xuất hiện ở bảng của chính bài báo TeleOCR. [PaddleOCR-VL-1.6](../wiki/paddleocr-vl-1.6.md) đạt **96,33**, còn [MinerU2.5-Pro](../wiki/mineru2-5-pro.md) đạt **95,75** và có reading-order edit thấp nhất trong nhóm ở bảng đó. Nếu ưu tiên model nhỏ, [FalconOCR](../wiki/falcon-ocr.md) chỉ **0,3B**, nhưng đánh giá được lưu chủ yếu là **tiếng Anh**, không nên ghép trực tiếp vào bảng đa ngôn ngữ.

[MiniCPM-OCR 1.0](../wiki/minicpm-ocr-1-0.md) là ứng viên layout-first 1,3B. Trong bảng riêng do nhóm MiniCPM công bố, model đạt **96,51** trên OmniDocBench v1.6 và **93,68** trên Real5; TeleOCR đạt **96,91** trên v1.6 trong cùng bảng. Không ghép trực tiếp các con số này vào bảng của paper TeleOCR hoặc report PaddleOCR vì điều kiện và nguồn khác nhau.

**Phạm vi model:** tài liệu này chỉ giữ các hệ thống layout-first theo [phân loại trong wiki](../wiki/task-layout-first-modular-parsing.md). [MonkeyOCRv2-B-Parsing](../wiki/monkeyocrv2.md) cũng được giữ vì nó dự đoán phần tử và tọa độ trước, rồi crop từng phần tử để nhận dạng. Các trường hợp ranh giới nằm riêng ở mục 7. Trong mười model của [so sánh benchmark mười model](../wiki/document-ocr-model-benchmark-comparison.md), các model layout-first là **TeleOCR, PaddleOCR-VL-1.6, MinerU2.5-Pro, MiniCPM-OCR 1.0 và MonkeyOCRv2-B-Parsing**. Các model end-to-end, gồm OvisOCR2/3, Chandra OCR 2, Infinity-Parser2, LightOnOCR-3 và Xiaomi-OCR-0, đã được loại khỏi bảng và nhận xét; xem [so sánh end-to-end](so-sanh-cac-model-end-to-end-generative-ocr.md). Surya OCR 2.5 mặc định OCR toàn trang, nên benchmark chi tiết của nó cũng nằm bên đó.

Các điểm số dưới đây là **tác giả hoặc nhà cung cấp công bố**, chưa được chạy lại độc lập trong wiki. Bảng cùng nguồn giúp so sánh tốt hơn, nhưng không nhất thiết chứng minh mọi baseline đã được chạy lại với cấu hình đồng nhất.

## 1. Danh sách model, thời điểm và kích thước

Phạm vi chính là các hệ thống phân vùng tài liệu trước rồi nhận dạng nội dung vùng. Các trường hợp ranh giới được tách riêng bên dưới. Số parameter thường là của **model nhận dạng hoặc VLM được công bố**, không mặc nhiên là tổng của toàn bộ pipeline, bao gồm layout model.

| Model | Thời điểm phát hành / mốc có bằng chứng | Size công bố | Điểm đáng chú ý khi chọn |
|---|---|---:|---|
| [PP-StructureV3](../wiki/pp-structurev3.md) | Chưa xác định chính xác ngày release từ bằng chứng đã kiểm tra | **Chưa rõ tổng pipeline**; hình trong report gợi ý khoảng 0,36B | Pipeline nhiều model chuyên biệt; có benchmark làm baseline nhưng kết quả trên tài liệu méo thấp hơn các bản VLM mới trong bảng Real5. |
| [MinerU2.5](../wiki/mineru2-5.md) | Checkpoint có tên `2509`; **chưa xác minh ngày release chính xác** | 1,2B | Baseline đời trước của MinerU2.5-Pro. |
| [PaddleOCR-VL](../wiki/paddleocr-vl.md) | **16/10/2025** theo model card | 0,9B | Bản đầu; wiki đánh dấu đã được thay thế bởi 1.5 và sau đó 1.6. |
| [PaddleOCR-VL-1.5](../wiki/paddleocr-vl-1.5.md) | **29/01/2026** theo model card | 0,9B | Cải thiện đáng kể trên tài liệu biến dạng so với bản đầu; đã được 1.6 thay thế trong wiki. |
| [GLM-OCR](../wiki/glm-ocr.md) | Report năm 2026; **chưa xác định ngày release chính xác** | 0,9B | Có cả document parsing và đường xử lý KIE riêng; các điểm KIE không đo riêng pipeline layout-first. |
| [FalconOCR](../wiki/falcon-ocr.md) | Report năm 2026; **chưa xác định ngày release chính xác** | 0,3B | Nhỏ nhất trong nhóm VLM chính ở đây; tập trung tiếng Anh. |
| [MinerU2.5-Pro](../wiki/mineru2-5-pro.md) | Bản `2604`: chưa xác minh ngày chính xác; bản **2605 phát hành 21/05/2026** | 1,2B | Nâng cấp từ MinerU2.5; hai bản 2604/2605 có điểm tương đối gần nhau. |
| [PaddleOCR-VL-1.6](../wiki/paddleocr-vl-1.6.md) | Report năm 2026; **chưa xác định ngày release chính xác** | 0,9B | Bản hiện tại trong chuỗi PaddleOCR-VL được wiki ghi nhận; mạnh ở cả OmniDocBench v1.6 và Real5. |
| [TeleOCR](../wiki/teleocr.md) | Trọng số **NaviDC-OCR phát hành 17/08/2026**; đổi tên thành TeleOCR **10/09/2026** | 1,2B | Nhắm cả tài liệu số lẫn ảnh chụp bị biến dạng; bảng của paper có kết quả mạnh về table. |
| [SenOCR-Vi](../wiki/senocr-vi.md) | Card trích preprint 2026 nhưng **không ghi ngày release** | **0,959B** | Fine-tune của PaddleOCR-VL-1.6 cho tiếng Việt; dùng được trong pipeline PaddleOCR-VL 1.6. |
| [MonkeyOCRv2-B-Parsing](../wiki/monkeyocrv2.md) | Paper năm 2026; **chưa xác định ngày release chính xác** | ~0,7B (encoder B 113M + Qwen3-0.6B) | Dự đoán loại phần tử và tọa độ theo thứ tự đọc, crop từng phần tử, rồi nhận dạng và ghép kết quả. Mạnh trên MDPBench đa ngôn ngữ. |
| [MiniCPM-OCR 1.0](../wiki/minicpm-ocr-1-0.md) | **Chưa xác minh ngày release chính xác** | 1,3B | PP-DocLayoutV3 → nhận dạng từng vùng → SDK ghép Markdown; ngôn ngữ chính là Trung và Anh. Có KIE trực tiếp và heuristic ghép bảng qua trang tùy chọn. |

Mốc ngày rõ ràng được đối chiếu thêm trong model card của [PaddleOCR-VL](../raw/PaddleOCR-VL.md#news), [PaddleOCR-VL-1.5](../raw/2601.21957_PaddleOCR-VL-1.5/README.md#news), [MinerU2.5-Pro-2605](../raw/MinerU2.5-Pro-2605-1.2B.md) và [TeleOCR](../raw/arXiv-2608.12898v3-TeleOCR/README.md#-news). Tên checkpoint `2509` hoặc `2604` **không đủ để khẳng định ngày phát hành**.

## 2. So sánh chính: OmniDocBench v1.6 Full

Bảng dưới lấy **cùng một bảng** trong [paper TeleOCR, bảng OmniDocBench v1.6 Full](../raw/arXiv-2608.12898v3-TeleOCR/main.tex), thay vì ghép điểm từ các bản report khác nhau. Chỉ giữ các model thuộc hướng đang xét.

- **Overall, Formula CDM, Table TEDS/TEDS-S:** cao hơn tốt hơn.
- **Text edit, Order edit:** thấp hơn tốt hơn.
- **TEDS-S** nhấn mạnh cấu trúc bảng; **TEDS** đánh giá bảng theo metric được báo cáo trong benchmark.

| Model | Size | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|
| **TeleOCR** | 1,2B | **96,87** | **0,027** | 96,36 | **97,05** | **98,52** | 0,122 |
| PaddleOCR-VL-1.6 | 0,9B | 96,33 | 0,033 | **97,49** | 94,76 | 97,11 | 0,127 |
| MinerU2.5-Pro | 1,2B | 95,75 | 0,036 | 97,45 | 93,42 | 95,92 | **0,120** |
| GLM-OCR | 0,9B | 95,22 | 0,044 | 97,18 | 92,83 | 95,39 | 0,133 |
| PaddleOCR-VL-1.5 | 0,9B | 94,87 | 0,038 | 96,69 | 91,67 | 94,37 | 0,130 |
| PaddleOCR-VL | 0,9B | 94,11 | 0,040 | 95,70 | 90,65 | 93,74 | 0,135 |
| MinerU2.5 | 1,2B | 92,98 | 0,045 | 95,59 | 87,88 | 91,47 | 0,130 |

### Diễn giải

1. **TeleOCR nổi bật về bảng:** trong bảng này, TEDS **97,05**, cao hơn PaddleOCR-VL-1.6 **2,29 điểm**; text edit cũng thấp hơn. Tuy nhiên, formula CDM của TeleOCR thấp hơn PaddleOCR-VL-1.6 và MinerU2.5-Pro.
2. **PaddleOCR-VL-1.6 cân bằng size/chất lượng:** 0,9B, overall chỉ thấp hơn TeleOCR **0,54 điểm**, đồng thời có formula CDM cao nhất trong nhóm trên.
3. **MinerU2.5-Pro đáng xét khi reading order quan trọng:** order edit **0,120**, thấp nhất trong nhóm này; overall và table TEDS thấp hơn TeleOCR và PaddleOCR-VL-1.6.
4. **GLM-OCR cùng cỡ 0,9B nhưng thấp hơn PaddleOCR-VL-1.6** ở các cột trong bảng này. Điều đó không quyết định kết quả KIE, vì GLM-OCR có đường KIE riêng.
5. **Không nên coi khoảng cách vài phần mười điểm là thứ hạng tuyệt đối.** Bảng trong [tổng hợp benchmark layout-first](../wiki/layout-first-modular-ocr-benchmarks.md) chép từ report PaddleOCR-VL-1.6 ghi VL-1.5 **94,93** thay vì **94,87** ở bảng TeleOCR; Model card MinerU cũng ghi giá trị khác: Pro-2604 **95,69** (CDM 97,29), Pro-2605 **95,72** (CDM 97,15), so với 95,75 / 97,45 trong bảng này. Wiki không có snapshot leaderboard và cấu hình đầy đủ để giải thích chênh lệch.
6. **MinerU2.5-Pro theo tập con (ảnh leaderboard của MinerU):** Base **96,12**, Hard **94,08**. Vector Hard: text edit 0,052, CDM 97,54, TEDS 89,91, TEDS-S 93,61, order edit 0,170. [Phụ lục §1](../wiki/ocr-ten-model-benchmark-comparison.md#1-omnidocbench-v16-mineru25-pro-base--hard)
7. **Các dòng layout-first từ nguồn khác:** MiniCPM-OCR 1.0 tự báo cáo **96,51** (mục 3). MonkeyOCRv2-B-Parsing tự báo cáo **91,57** trong bài của nó, với text edit 0,053, CDM 91,83, TEDS 88,24, TEDS-S 91,38 và order edit 0,131. Cụm TeleOCR / MiniCPM / PaddleOCR-VL-1.6 nằm trong khoảng 96,3–96,9. Chênh lệch trong cụm nhỏ hơn mức chênh giữa các nguồn, nên không đủ để xếp hạng chắc chắn. [Nguồn](../wiki/document-ocr-model-benchmark-comparison.md#omnidocbench-v16-full)

**Lưu ý:** Đây không phải toàn bộ model trong họ. FalconOCR, PP-StructureV3, SenOCR-Vi và các trường hợp ranh giới không có hàng tương ứng trong bảng trên; không nên tự điền từ benchmark khác.

## 3. Tài liệu chụp, scan và biến dạng

### Real5-OmniDocBench: cùng bảng trong report PaddleOCR-VL-1.6

Real5 đo năm điều kiện: scan, cong/biến dạng, chụp màn hình, ánh sáng và lệch góc. Điểm càng cao càng tốt. Nguồn: [bảng benchmark layout-first — Real5](../wiki/layout-first-modular-ocr-benchmarks.md#real5-omnidocbench).

| Model | Overall ↑ | Scan | Warp | Chụp màn hình | Ánh sáng | Lệch góc |
|---|---:|---:|---:|---:|---:|---:|
| **PaddleOCR-VL-1.6** | **93,19** | 94,74 | 92,48 | 92,78 | 93,28 | 92,66 |
| PaddleOCR-VL-1.5 | 92,05 | 93,43 | 91,25 | 91,76 | 92,16 | 91,66 |
| GLM-OCR | 90,32 | 92,67 | 90,68 | 91,75 | 91,12 | 85,39 |
| MinerU2.5-Pro | 88,96 | 92,11 | 88,72 | 91,29 | 91,42 | 81,26 |
| MinerU2.5 | 85,61 | 90,06 | 83,76 | 89,41 | 89,57 | 75,24 |
| PaddleOCR-VL | 85,54 | 92,11 | 85,97 | 82,54 | 89,61 | 77,47 |
| PP-StructureV3 | 64,45 | 84,68 | 59,34 | 66,89 | 73,38 | 37,98 |

**Điểm đáng chú ý:** trên bảng này, PaddleOCR-VL-1.6 dẫn đầu cả năm điều kiện. Chênh lệch đặc biệt lớn ở **lệch góc**: 92,66 so với 81,26 của MinerU2.5-Pro và 37,98 của PP-StructureV3. Đây là bằng chứng hữu ích để chọn ứng viên thử nghiệm ảnh chụp, nhưng Real5 không bao phủ mọi điều kiện thực tế. Card OvisOCR3 ghi thêm MonkeyOCRv2-B-Parsing **89,22** overall; nguồn này khác và không có điểm theo từng điều kiện.

### TeleOCR: benchmark ảnh chụp khác, không ghép với Real5

Paper TeleOCR báo cáo trên **Wild-OmniDocBench v1.5 Full**:

| Model | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | TEDS-S ↑ | Order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| **TeleOCR** | **88,53** | **0,1173** | 88,26 | **89,05** | **92,14** | **0,2011** |
| PaddleOCR-VL-1.6 | 87,36 | 0,1369 | 88,42 | 85,76 | 90,14 | 0,2057 |
| MinerU2.5-Pro | 87,33 | 0,1362 | **90,15** | 85,46 | 90,12 | 0,2013 |

Cả ba hàng lấy từ cùng bảng của paper TeleOCR, chấm bằng `quick_match`. PaddleOCR-VL-1.6 và MinerU2.5-Pro gần như ngang nhau; MinerU có formula CDM cao nhất. [Nguồn](../wiki/document-ocr-model-benchmark-comparison.md#wild-omnidocbench--hai-giao-thức-không-gộp-được)

### PureDocBench: Clean / Digital degraded / Real degraded

| Model | TB 3 track ↑ | Clean | Digital | Real | Nguồn |
|---|---:|---:|---:|---:|---|
| **TeleOCR** | **78,41** | **86,90** | **77,47** | **70,85** | Paper TeleOCR |
| MinerU2.5-Pro | 70,07 | 75,87 | 71,77 | 62,56 | Paper TeleOCR; báo cáo OvisOCR2 cũng ghi các số này |
| PaddleOCR-VL-1.6 | 65,44 (overall) | — | — | — | Card OvisOCR3; không nêu định nghĩa overall |
| MonkeyOCRv2-B-Parsing | 64,91 (overall) | — | — | — | Card OvisOCR3; không nêu định nghĩa overall |

Vector `Text ED ↓ / CDM ↑ / TEDS ↑` theo track: TeleOCR Clean 0,111 / 81,01 / 91,09 và Real 0,302 / 65,11 / 77,66; MinerU2.5-Pro Clean 0,222 / 65,14 / 84,68 và Real 0,375 / 52,70 / 72,47. Hai hàng PaddleOCR-VL-1.6 và MonkeyOCRv2-B-Parsing khác nguồn, nên không xếp cùng hai hàng đầu. [Phụ lục §2](../wiki/ocr-ten-model-benchmark-comparison.md#2-puredocbench-component-vectors-theo-track)

Với PureDocBench, tác giả TeleOCR loại sáu prediction Markdown không hợp lệ (1 Clean, 5 Real) sau hiện tượng lặp nghiêm trọng và nói prediction bị thiếu được chấm 0. Đây là failure mode cần lưu ý khi thử nghiệm. Nguồn và giới hạn: [TeleOCR — Reported evaluation](../wiki/teleocr.md#reported-evaluation).

**Không so sánh trực tiếp 88,53 của Wild với 93,19 của Real5:** đây là hai benchmark khác nhau.

### MDPBench: 17 ngôn ngữ, digital và ảnh chụp

Nguồn là bảng chính thức trong README MDPBench. TeleOCR và MiniCPM-OCR 1.0 không có trong bảng này.

| Model | All ↑ | Digital | Photo | Latin avg | Non-Latin avg | VI | ZH | Private |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **MonkeyOCRv2-B-Parsing** | **83,3** | **88,1** | **81,7** | **84,2** | **82,1** | **83,2** | 83,6 | **84,7** |
| PaddleOCR-VL-1.6 | 78,9 | 87,1 | 76,3 | 81,4 | 76,1 | 80,9 | **85,9** | 83,0 |
| MinerU2.5-Pro | 71,0 | 86,2 | 66,1 | 74,6 | 67,0 | 74,2 | 76,5 | 74,3 |

MonkeyOCRv2-B-Parsing dẫn mọi cột trừ ZH. Khoảng cách giữa ba model chủ yếu nằm ở trang **ảnh chụp** (81,7 / 76,3 / 66,1); trên trang digital, chúng chỉ cách nhau tối đa 1,9 điểm. Nhóm tác giả MonkeyOCRv2 cũng là bên quản lý benchmark và tự nộp hàng của mình. Bài MonkeyOCRv2 lại ghi PaddleOCR-VL-1.6 là **75,0** (82,8 / 72,6), và không nguồn nào giải thích chênh lệch này. Điểm VI 80,9 của PaddleOCR-VL-1.6 khớp với mốc base trong mục SenOCR-Vi bên dưới. [Nguồn](../wiki/document-ocr-model-benchmark-comparison.md#mdpbench-17-ngôn-ngữ-digital--photographed)

### Bảng riêng do nhóm MiniCPM-OCR công bố

Nguồn: [MiniCPM-OCR evaluation](../wiki/minicpm-ocr-evaluation.md#document-parsing-comparison). Các hàng dưới đây đến từ **cùng hình benchmark của nhà cung cấp MiniCPM**, không bổ sung vào các bảng trên. Điểm càng cao càng tốt; mỗi cột là một benchmark riêng.

| Model | OmniDocBench v1.6 ↑ | Real5 ↑ | Wild ↑ | olmOCR ↑ |
|---|---:|---:|---:|---:|
| MiniCPM-OCR 1.0 | 96,51 | **93,68** | **92,39** | **82,7** |
| TeleOCR | **96,91** | 90,72 | 90,71 | 77,1 |
| PaddleOCR-VL-1.6 | 96,34 | 93,19 | 91,49 | 80,2 |
| MinerU2.5-Pro | 95,75 | 88,94 | 90,06 | 79,5 |
| GLM-OCR | 95,22 | 90,32 | 90,40 | 75,2 |

Trong bảng này, MiniCPM cao hơn PaddleOCR-VL-1.6 **0,17 điểm** trên v1.6 và **0,49 điểm** trên Real5, nhưng thấp hơn TeleOCR **0,40 điểm** trên v1.6. Đó là tín hiệu để benchmark, không phải thứ hạng tuyệt đối. OmniDocBench v1.6 dùng `quick_match`; Real5 dùng ground truth v1.5 và trung bình đều năm điều kiện; Wild dùng scorer v1.6 với ground truth v1.5 tương ứng và sửa xoay bằng SDK. Cấu hình từng hệ thống và tài liệu tái lập còn thiếu chi tiết. Điểm TeleOCR v1.6 **96,91** ở đây khác **96,87** trong bảng paper phía trên. Wild cũng khác phiên bản và tiền xử lý: TeleOCR đạt 90,71 ở đây nhưng 88,53 trong bảng của paper, nên không ghép trực tiếp.

**Ảnh và JSON không khớp nhau:** `ocr-benchmarks.png` có số ở mọi ô. Tuy nhiên, `benchmark-data.json` để `null` và gắn `pending_confirmation` cho OmniDocBench v1.6 của PaddleOCR-VL-1.6, Real5 và OmniDocBench của MinerU2.5-Pro, cùng CHAOS của MiniCPM. Do đó, các ô này chưa được nhà cung cấp xác nhận. [Contradictions](../wiki/document-ocr-model-benchmark-comparison.md#contradictions)

**CHAOS-Bench và OCRBench v2 trong bảng của MiniCPM** (cao hơn là tốt hơn):

| Model | CHAOS-Bench recall ↑ | OCRBench v2 ↑ |
|---|---:|---:|
| MiniCPM-OCR 1.0 | **29,78** (JSON: pending) | **54,7** |
| TeleOCR | 21,28 | 23,3 |
| MinerU2.5-Pro | 13,90 | 29,1 |
| PaddleOCR-VL-1.6 | 9,32 | 35,2 |

CHAOS chỉ đo khả năng giữ đúng 1.025 từ bị thay đổi trên 500 trang, theo word boundary trong output cả trang; nó không đo toàn bộ hallucination. Bài MonkeyOCRv2 lại ghi MinerU2.5-Pro **6,3** và PaddleOCR-VL-1.6 **6,0**, lấy từ leaderboard CHAOS gốc. Vì vậy thứ hạng CHAOS phụ thuộc vào nguồn. [Phụ lục §4](../wiki/ocr-ten-model-benchmark-comparison.md#4-chaos-bench-giao-thức-của-minicpm)

**Tốc độ do vendor báo cáo:** trên 1.651 ảnh OmniDocBench v1.6, RTX 5090, image concurrency 1 và cấu hình tăng tốc riêng của từng hệ thống: MiniCPM **1,217 trang/s**, GLM-OCR **1,179**, PaddleOCR-VL-1.6 **0,818**, MinerU2.5-Pro **0,336** (Advanced; Standard **0,531**), TeleOCR **0,141**. TeleOCR chậm nhất nhóm layout-first trong phép đo này. MiniCPM chạy ở concurrency 2/4/6/8 đạt 1,613 / 1,888 / 2,031 / 2,133 trang/s. Các vùng trong một trang vẫn có thể chạy song song. JSON benchmark lại ghi MiniCPM **1,213 trang/s** trong điều kiện được nêu; khác biệt chưa được giải thích. Thiếu version chính xác, timing boundary và lệnh/log đầy đủ, nên không suy rộng sang phần cứng hoặc workload khác. [Nguồn và giới hạn](../wiki/minicpm-ocr-evaluation.md#throughput).

**Khả năng bổ sung:** SDK có heuristic ghép bảng qua trang, mặc định tắt; đây là kết quả đọc mã tĩnh, chưa chạy test hay chứng minh độ chính xác. [Jev](../wiki/minicpm-ocr-jev.md) là model 2B riêng chấm tính đúng của vùng OCR để hỗ trợ chọn kết quả hoặc chuyển review, không tạo OCR; AUROC không tự xác lập ngưỡng chấp nhận an toàn. Xem [cross-page table reconstruction](../wiki/task-cross-page-table-reconstruction.md#minicpm-ocr-sdk-heuristic-merging).

## 4. Benchmark unit-test và benchmark bảng

### OmniParseBench (Datalab chạy các model)

Headline là trung bình của text, tables và layout. Model open-weight được Datalab chạy bằng server image của `omni-parse-bench` với default do vendor khuyến nghị. Datalab là bên xây dựng và chạy benchmark, đồng thời có model cạnh tranh, nên đây là bằng chứng do vendor chạy. TeleOCR và MonkeyOCRv2 không có trong bảng.

| Model | Headline ↑ | Text | Tables | Layout |
|---|---:|---:|---:|---:|
| **MinerU2.5-Pro** | **87,1** | **77,4** | **92,1** | **91,7** |
| MiniCPM-OCR 1.0 | 83,2 | 72,8 | 89,1 | 87,6 |
| PaddleOCR-VL-1.6 | 78,7 | 61,7 | 83,7 | 90,7 |

**Synthesis:** MinerU2.5-Pro dẫn cả bốn cột trong nhóm này. PaddleOCR-VL-1.6 thuộc nhóm dẫn đầu OmniDocBench nhưng đứng cuối bảng này, chủ yếu vì text chỉ đạt 61,7. Indra OCR và PP-StructureV3 có điểm OmniParseBench ở mục 7, theo một phép so riêng trong card Indra. [Nguồn](../wiki/document-ocr-model-benchmark-comparison.md#omniparsebench-datalab-16288-test-passfail-2937-trang-2343-tài-liệu-22-suite-92-ngôn-ngữ)

### olmOCR-Bench (tỉ lệ pass của unit test)

| Model | Overall ↑ | Nguồn |
|---|---:|---|
| MiniCPM-OCR 1.0 | **82,7** | Nhà cung cấp MiniCPM |
| PaddleOCR-VL-1.6 | 80,2 | Bảng MiniCPM |
| MinerU2.5-Pro | 79,5 | Bảng MiniCPM |
| TeleOCR | 77,1 | Bảng MiniCPM |

Cả bốn hàng đến từ cùng bảng của MiniCPM, bên cũng có model trong bảng. FalconOCR chỉ có điểm trên bản lọc tiếng Anh (mục 5), nên không đưa vào đây. **Synthesis:** thứ hạng đảo chiều giữa họ OmniDocBench và họ unit-test. TeleOCR dẫn đầu OmniDocBench v1.6 nhưng đứng cuối ở đây. [Nguồn](../wiki/document-ocr-model-benchmark-comparison.md#olmocr-bench-unit-test-pass-rate)

### Bảng khó, bảng qua trang và bộ in-house

| Benchmark (nguồn) | Metric | PaddleOCR-VL-1.6 | MinerU2.5-Pro |
|---|---|---:|---:|
| Hard table in-house, 1.258 mẫu (report Paddle) | TEDS / TEDS-S ↑ | **91,71 / 94,67** | 89,77 / 93,78 |
| CrossTabBench (card OvisOCR3) | Relation F1 / reconstruction TEDS ↑ | 42,61 / 24,24 | **59,14 / 41,02** |
| CrossTabBench (card OvisOCR3) | Precision / Recall | 90,13 / 27,90 | 93,81 / 43,18 |
| MPDocBench-Parse truncated-table (card OvisOCR3) | TEDS ↑ | 83,39 | **91,44** |
| DocFigCapBench (card OvisOCR3) | Localization F1 ↑ | **85,32** | 85,00 |
| Bộ in-house >1.000 trang (report OvisOCR2) | Full overall ↑ | **82,88** | 65,54 |
| Bộ in-house (report OvisOCR2) | Handwriting / complex tables overall ↑ | **67,66 / 73,19** | 55,04 / 71,43 |

MinerU2.5-Pro còn đạt trung bình **91,10 TEDS / 94,48 TEDS-S** trên năm bộ bảng dạng crop theo GT box; cách đo này loại bỏ lỗi layout nên không phải end-to-end. **Synthesis:** khi ghép bảng qua trang, cả hai model đều có precision cao nhưng recall thấp: ít nối nhầm nhưng bỏ sót nhiều. MinerU-PoPo (54,76 F1) là hệ thống tăng cường riêng, không thay cho MinerU2.5-Pro thuần. ChartQA/spotting/seal của Paddle chỉ có hàng của chính Paddle. [Phụ lục §5–6](../wiki/ocr-ten-model-benchmark-comparison.md#5-benchmark-chuyên-biệt-của-ovisocr3)

## 5. FalconOCR: nhỏ hơn, nhưng cần so đúng tập tiếng Anh

### OmniDocBench v1.5 — chỉ các trang tiếng Anh

Nguồn Falcon loại các trang tiếng Trung, nên bảng này **không tương đương** OmniDocBench v1.5 song ngữ hoặc v1.6 ở trên. Nguồn: [layout-first benchmarks — Falcon English-only](../wiki/layout-first-modular-ocr-benchmarks.md#falcon-english-only-protocol).

| Model | Size | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ |
|---|---:|---:|---:|---:|---:|
| PaddleOCR-VL-1.5 | 0,9B | **94,37** | 0,075 | **94,4** | **91,1** |
| PaddleOCR-VL | 0,9B | 91,76 | **0,024** | 91,7 | 85,9 |
| FalconOCR | **0,3B** | 88,64 | 0,055 | 86,8 | 84,6 |

### olmOCR-Bench — lọc tiếng Anh

| Model | Overall ↑ | Multi-column ↑ | Old scan ↑ | Table ↑ |
|---|---:|---:|---:|---:|
| **FalconOCR** | **80,3** | **87,1** | **43,5** | **90,3** |
| PaddleOCR-VL-1.5 | 79,3 | 82,6 | 39,2 | 84,1 |
| PaddleOCR-VL | 79,2 | 82,5 | 38,8 | 83,9 |

**Nhận xét:** FalconOCR thua PaddleOCR-VL-1.5 khá rõ ở overall OmniDocBench tiếng Anh, nhưng lại dẫn nhẹ trên olmOCR-Bench tiếng Anh và dẫn ở các nhóm multi-column/table trong bảng đó. Vì vậy, với tài liệu **tiếng Anh** và yêu cầu model nhỏ, FalconOCR là ứng viên đáng benchmark thực tế; không thể từ đây kết luận nó tốt cho tiếng Việt. Hai bảng có task và scorer khác nhau. [Nguồn](../wiki/layout-first-modular-ocr-benchmarks.md#falcon-english-filtered-protocol).

## 6. Nếu trọng tâm là tài liệu tiếng Việt: SenOCR-Vi

[SenOCR-Vi](../wiki/senocr-vi.md) là bản chuyên biệt hóa từ PaddleOCR-VL-1.6, có **958.588.736 parameter**. Model card báo cáo trên tập tiếng Việt 160 trang của MDPBench:

| Model | Size | Vietnamese document composite ↑ |
|---|---:|---:|
| MonkeyOCRv2-B-Parsing | ~0,7B | **83,20** |
| SenOCR-Vi | 0,959B | 82,83 |
| PaddleOCR-VL-1.6 | khoảng 0,9B | 80,90 |

Hàng MonkeyOCRv2-B-Parsing và PaddleOCR-VL-1.6 được card SenOCR-Vi lấy từ leaderboard; chúng khớp cột VI của bảng MDPBench ở mục 3. Trong các model layout-first, MonkeyOCRv2-B-Parsing hiện cao nhất trên tiếng Việt, cao hơn SenOCR-Vi **0,37 điểm**. Khoảng cách này rất nhỏ, còn điểm SenOCR-Vi được tính theo cách khác (xem giới hạn bên dưới), nên không đủ để xếp hạng.

SenOCR-Vi còn báo cáo **86,7%** cho text recognition theo `1 − edit distance`; con số này **không phải** document composite. Với tập đánh giá EN/VI/ZH, card báo cáo macro **82,98** cho SenOCR-Vi so với **83,43** cho base, nên cải thiện tiếng Việt không đồng nghĩa cải thiện đều mọi ngôn ngữ.

**Giới hạn quan trọng:** 82,83 được tính lại sau khi sửa vấn đề tổng hợp số dòng; 80,90 của base lấy từ leaderboard và chưa được tính lại bằng cùng pipeline đã sửa. Vì vậy chênh **1,93 điểm** là tín hiệu để thử nghiệm, chưa phải so sánh kiểm soát hoàn toàn. [Nguồn và caveat](../wiki/senocr-vi.md#comparability-caveats).

## 7. Các trường hợp ranh giới

| Model | Size | Có nên đưa vào shortlist? | Bằng chứng benchmark |
|---|---:|---|---|
| [Surya OCR 2](../wiki/surya-ocr-2.md) | 650M cho VLM | Có, nếu muốn thử chế độ block layout-first; hệ thống cũng có chế độ full-page nên không hoàn toàn cùng định nghĩa. | Vendor báo cáo **83,3** trên olmOCR-bench với preset 8.413 test và điều chỉnh cho HTML. Không ghép trực tiếp với bảng Falcon. |
| [Surya OCR 2.5](../wiki/surya-ocr-2-5.md) | 689M cho VLM; detector dòng là model riêng | Có, nếu muốn thử cả full-page mặc định và layout-first theo block. Chưa xác lập crop resolution hoặc routing model chuyên biệt như nhóm lõi; ngày release chính xác chưa rõ. | Vendor báo cáo **85,9** OmniParseBench (Surya 2: 83,3) và **83,7** olmOCR-bench (Surya 2: 82,8 trong cùng lần chạy). Không xác định được các điểm này thuộc chế độ block; điều kiện chi tiết nằm trong [tài liệu end-to-end](so-sanh-cac-model-end-to-end-generative-ocr.md). |
| [Indra OCR](../wiki/indra-ocr.md) | Card nói **7,3M cho toàn bộ model mặc định**, nhưng có mô tả “1M” không được giải thích; tải mặc định khoảng **76 MB** gồm cả language model | Có, nếu ưu tiên **CPU, tốc độ và tài liệu in tương đối sạch** hơn là bảng phức tạp. | Trên [OmniParseBench](../wiki/omniparsebench.md), vendor báo cáo **66,7** mặc định và **71,4** với `--math`, so với **58,4** của PP-StructureV3. So sánh do vendor chạy; PP-StructureV3 thiếu 19 trang và các cấu hình không đối xứng. |
| [OXR-1.0](../wiki/oxr-1-0.md) | 1,3B | Có thể theo dõi, nhưng thiếu dữ liệu để xếp hạng. | README quảng bá thứ hạng cao nhưng bản lưu không có score vector, version benchmark hoặc điều kiện test; layout/recognition flow cũng chưa đủ rõ để xếp chắc vào nhóm lõi. |

[Xiaomi-OCR-0](../wiki/xiaomi-ocr-0.md) có tùy chọn PP-DocLayoutV3 → nhận dạng vùng, nhưng giao diện chính là whole-page, và card không nêu benchmark được chạy ở chế độ nào. Vì vậy, model này được chuyển sang [tài liệu end-to-end](so-sanh-cac-model-end-to-end-generative-ocr.md).

## 8. Gợi ý shortlist theo nhu cầu

Đây là **suy luận từ các bảng đã dẫn**, không phải kết luận benchmark độc lập:

- **Điểm tổng thể và bảng trên OmniDocBench v1.6:** thử **TeleOCR** trước, sau đó **PaddleOCR-VL-1.6**. Kiểm tra thêm lỗi lặp và tính ổn định trên tài liệu của bạn. TeleOCR chậm nhất trong phép đo RTX 5090 của MiniCPM (0,141 trang/s) và thấp nhất nhóm trên olmOCR-Bench (77,1) trong cùng bảng.
- **Một model khoảng 0,9B cho nhiều loại tài liệu, kể cả ảnh biến dạng:** thử **PaddleOCR-VL-1.6**. Model này dẫn bảng Real5 được lưu và vượt MinerU2.5-Pro trên MDPBench ảnh chụp. Nếu workload giống OmniParseBench, hãy kiểm tra kỹ phần text, vì điểm text trên bảng đó chỉ là 61,7.
- **Tài liệu tiếng Anh/Trung, cần throughput hoặc pipeline theo vùng:** thêm **MiniCPM-OCR 1.0** vào shortlist cùng TeleOCR và PaddleOCR-VL-1.6; đo tốc độ và chất lượng trên cùng phần cứng, cấu hình và dữ liệu thực tế. Chưa có bằng chứng trong các trang này để suy ra chất lượng tiếng Việt.
- **Tài liệu đa ngôn ngữ hoặc ảnh chụp đa ngôn ngữ:** thử **MonkeyOCRv2-B-Parsing** cùng PaddleOCR-VL-1.6. MonkeyOCRv2 dẫn bảng MDPBench chính thức với 83,3 overall và 81,7 photo, nhưng hàng này do nhóm quản lý benchmark tự nộp. Trên OmniDocBench v1.6, model chỉ tự báo cáo 91,57.
- **Reading order, bảng trong một trang, hoặc đang dùng hệ MinerU:** thử **MinerU2.5-Pro** song song với PaddleOCR-VL-1.6. MinerU có tables OmniParseBench 92,1, cao nhất bảng; tuy nhiên PaddleOCR-VL-1.6 dẫn trên bộ hard table in-house của Paddle. MinerU cũng dẫn PaddleOCR-VL-1.6 về bảng qua trang. Tuy vậy, recall ghép bảng qua trang của MinerU vẫn thấp (43,18), và điểm lệch góc trên Real5 chỉ đạt 81,26. Cần xác nhận bản 2604 hay 2605 và chức năng cross-page table trong môi trường triển khai, vì model card có mô tả chưa nhất quán về trạng thái tính năng này. [Nguồn](../wiki/mineru2-5-pro.md).
- **Chủ yếu tiếng Anh và cần model nhỏ:** thử **FalconOCR 0,3B**, nhất là nếu workload giống olmOCR-Bench hơn OmniDocBench.
- **Chủ yếu tiếng Việt:** thử **SenOCR-Vi và PaddleOCR-VL-1.6 trên cùng tập**, đặc biệt giữ nguyên cách tính dấu tiếng Việt, bảng và formula. Bằng chứng hiện tại chưa đủ để chốt mức tăng 1,93 điểm.
- **Muốn so sánh full-page với layout-first theo block:** thử **Surya 2.5** riêng từng chế độ; nếu cần row/column geometry, kiểm tra thêm **Surya 2**. Layout, OCR và bảng dùng inference server chung; xác minh license trọng số thực tế trước khi dùng thương mại. [Triển khai](../wiki/surya-ocr-2-5-deployment.md) · [Giới hạn license](../wiki/surya-ocr-2-5.md#license-and-evidence-limits).
- **CPU-only, tài liệu đơn giản:** cân nhắc **Indra OCR**, nhưng đánh giá riêng handwriting, scan cũ và bảng có merged cells.

**Đối chiếu 2026-10-30:** các số của TeleOCR, PaddleOCR-VL-1.6, MinerU2.5-Pro, MiniCPM-OCR 1.0, MonkeyOCRv2-B-Parsing và Surya OCR 2.5 trong output này đã được đối chiếu với [Document OCR model benchmark comparison](../wiki/document-ocr-model-benchmark-comparison.md), [supplementary evidence](../wiki/ocr-ten-model-benchmark-comparison.md) và [MDPBench](../wiki/mdpbench.md). GLM-OCR, FalconOCR, PP-StructureV3, SenOCR-Vi và các bản PaddleOCR-VL/MinerU cũ không nằm trong các trang đó, nên giữ nguyên. **Rà soát hướng cùng ngày:** đã loại các model end-to-end, gồm OvisOCR2/3, Chandra OCR 2, Infinity-Parser2, LightOnOCR-3 và Xiaomi-OCR-0, khỏi bảng và nhận xét. Bảng Xiaomi được chuyển sang tài liệu end-to-end, còn phần chi tiết Surya 2.5 so với Surya 2 chỉ được giữ bên đó. MonkeyOCRv2-B-Parsing được thêm vào vì pipeline của nó đi theo hướng layout-first. Các bảng có nguồn là card của model end-to-end, như card OvisOCR3/OvisOCR2, vẫn được giữ khi các hàng trong bảng đều là model layout-first.

**Giới hạn kiểm tra:** không truy cập web, tải model hay chạy benchmark. Các trang Surya 2.5, MonkeyOCRv2 và MiniCPM liên quan ở trạng thái **draft**, còn giới hạn về coverage và khả năng tái lập; mọi con số là báo cáo của tác giả hoặc vendor. Bản so sánh nằm trong `outputs/`; lần cập nhật này không thay đổi wiki.