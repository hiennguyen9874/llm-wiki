# So sánh các model OCR theo hướng layout-first modular

**Kết luận nhanh:** Trong các bảng đã kiểm tra, [TeleOCR](../wiki/teleocr.md) đạt **96,87** trên OmniDocBench v1.6 Full, cao nhất trong các model layout-first xuất hiện ở bảng của chính bài báo TeleOCR. [PaddleOCR-VL-1.6](../wiki/paddleocr-vl-1.6.md) đạt **96,33**, còn [MinerU2.5-Pro](../wiki/mineru2-5-pro.md) đạt **95,75** và có reading-order edit thấp nhất trong nhóm ở bảng đó. Nếu ưu tiên model nhỏ, [FalconOCR](../wiki/falcon-ocr.md) chỉ **0,3B**, nhưng đánh giá được lưu chủ yếu là **tiếng Anh**, không nên ghép trực tiếp vào bảng đa ngôn ngữ.

Bổ sung từ diff: [MiniCPM-OCR 1.0](../wiki/minicpm-ocr-1-0.md) là ứng viên layout-first 1,3B. Trong bảng riêng do nhóm MiniCPM công bố, model đạt **96,51** trên OmniDocBench v1.6 và **93,68** trên Real5; TeleOCR đạt **96,91** trên v1.6 trong cùng bảng. Không ghép trực tiếp các con số này vào bảng của paper TeleOCR hoặc report PaddleOCR vì điều kiện và nguồn khác nhau.

Bổ sung từ diff mới: [Xiaomi-OCR-0](../wiki/xiaomi-ocr-0.md) là VLM **0,8B** có chế độ layout-first tùy chọn, bên cạnh chế độ whole-page. Model card báo cáo **96,83** trên OmniDocBench v1.6 và **95,24** trên Real5, nhưng không xác lập cấu hình pipeline của các kết quả này. Cần xem đây là ứng viên ranh giới, không tự coi điểm đó là kết quả của chế độ layout-first.

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
5. **Không nên coi khoảng cách vài phần mười điểm là thứ hạng tuyệt đối.** Bảng trong [tổng hợp benchmark layout-first](../wiki/layout-first-modular-ocr-benchmarks.md) chép từ report PaddleOCR-VL-1.6 ghi VL-1.5 **94,93** thay vì **94,87** ở bảng TeleOCR; MinerU card cũng có các giá trị Pro hơi khác. Wiki không có snapshot leaderboard và cấu hình đầy đủ để giải thích chênh lệch.

**Lưu ý:** Đây không phải toàn bộ model trong họ. FalconOCR, PP-StructureV3, SenOCR-Vi, Xiaomi-OCR-0 và các trường hợp ranh giới không có hàng tương ứng trong bảng trên; không nên tự điền từ benchmark khác.

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

**Điểm đáng chú ý:** trên bảng này, PaddleOCR-VL-1.6 dẫn đầu cả năm điều kiện. Chênh lệch đặc biệt lớn ở **lệch góc**: 92,66 so với 81,26 của MinerU2.5-Pro và 37,98 của PP-StructureV3. Đây là bằng chứng hữu ích để chọn ứng viên thử nghiệm ảnh chụp, nhưng Real5 không bao phủ mọi điều kiện thực tế.

### TeleOCR: benchmark ảnh chụp khác, không ghép với Real5

Paper TeleOCR báo cáo trên **Wild-OmniDocBench v1.5 Full**:

| Model | Overall ↑ | Nguồn |
|---|---:|---|
| **TeleOCR** | **88,53** | Bảng của tác giả TeleOCR |
| PaddleOCR-VL-1.6 | 87,36 | Cùng bảng |

TeleOCR còn báo cáo **86,90 / 77,47 / 70,85** trên ba track PureDocBench **Clean / Digital Degraded / Real Degraded**. Với PureDocBench, tác giả loại sáu prediction Markdown không hợp lệ sau hiện tượng lặp nghiêm trọng và nói prediction bị thiếu được chấm 0. Đây là failure mode cần lưu ý khi thử nghiệm. Nguồn và giới hạn: [TeleOCR — Reported evaluation](../wiki/teleocr.md#reported-evaluation).

**Không so sánh trực tiếp 88,53 của Wild với 93,19 của Real5:** đây là hai benchmark khác nhau.

### Bảng riêng do nhóm MiniCPM-OCR công bố

Nguồn: [MiniCPM-OCR evaluation](../wiki/minicpm-ocr-evaluation.md#document-parsing-comparison). Các hàng dưới đây đến từ **cùng hình benchmark của nhà cung cấp MiniCPM**, không bổ sung vào các bảng trên. Điểm càng cao càng tốt; mỗi cột là một benchmark riêng.

| Model | OmniDocBench v1.6 ↑ | Real5 ↑ | Wild ↑ | olmOCR ↑ |
|---|---:|---:|---:|---:|
| MiniCPM-OCR 1.0 | 96,51 | **93,68** | **92,39** | **82,7** |
| TeleOCR | **96,91** | 90,72 | 90,71 | 77,1 |
| PaddleOCR-VL-1.6 | 96,34 | 93,19 | 91,49 | 80,2 |
| MinerU2.5-Pro | 95,75 | 88,94 | 90,06 | 79,5 |
| GLM-OCR | 95,22 | 90,32 | 90,40 | 75,2 |

Trong bảng này, MiniCPM cao hơn PaddleOCR-VL-1.6 **0,17 điểm** trên v1.6 và **0,49 điểm** trên Real5, nhưng thấp hơn TeleOCR **0,40 điểm** trên v1.6. Đó là tín hiệu để benchmark, không phải thứ hạng tuyệt đối. OmniDocBench v1.6 dùng `quick_match`; Real5 dùng ground truth v1.5 và trung bình đều năm điều kiện; Wild dùng scorer v1.6 với ground truth v1.5 tương ứng và sửa xoay bằng SDK. Cấu hình từng hệ thống và tài liệu tái lập còn thiếu chi tiết. Điểm TeleOCR v1.6 **96,91** ở đây khác **96,87** trong bảng paper phía trên; Wild cũng khác phiên bản/tiền xử lý nên không ghép trực tiếp.

**Tốc độ do vendor báo cáo:** trên 1.651 ảnh OmniDocBench v1.6, RTX 5090, image concurrency 1 và cấu hình tăng tốc riêng của từng hệ thống: MiniCPM **1,217 trang/s**, GLM-OCR **1,179**, PaddleOCR-VL-1.6 **0,818**, MinerU2.5-Pro **0,336**. Các vùng trong một trang vẫn có thể chạy song song. JSON benchmark lại ghi MiniCPM **1,213 trang/s** trong điều kiện được nêu; khác biệt chưa được giải thích. Thiếu version chính xác, timing boundary và lệnh/log đầy đủ, nên không suy rộng sang phần cứng hoặc workload khác. [Nguồn và giới hạn](../wiki/minicpm-ocr-evaluation.md#throughput).

**Khả năng bổ sung:** SDK có heuristic ghép bảng qua trang, mặc định tắt; đây là kết quả đọc mã tĩnh, chưa chạy test hay chứng minh độ chính xác. [Jev](../wiki/minicpm-ocr-jev.md) là model 2B riêng chấm tính đúng của vùng OCR để hỗ trợ chọn kết quả hoặc chuyển review, không tạo OCR; AUROC không tự xác lập ngưỡng chấp nhận an toàn. Xem [cross-page table reconstruction](../wiki/task-cross-page-table-reconstruction.md#minicpm-ocr-sdk-heuristic-merging).

### Bảng riêng trong model card Xiaomi-OCR-0

Nguồn: [model card Xiaomi-OCR-0 — Document parsing: selected comparisons](../raw/Xiaomi-OCR-0.md#document-parsing-selected-comparisons), đối chiếu với [trang wiki](../wiki/xiaomi-ocr-0.md#author-reported-evaluation). Các điểm là **Overall do nhà cung cấp báo cáo**, không chạy lại độc lập; dấu — nghĩa là nguồn không báo cáo. OvisOCR2 là model end-to-end được giữ làm baseline trong bảng gốc, không phải model layout-first lõi.

| Model | Size | OmniDocBench v1.6 ↑ | Real5 ↑ | Wild ↑ |
|---|---:|---:|---:|---:|
| Xiaomi-OCR-0 | 0,8B | 96,83 | 95,24 | 87,94 |
| TeleOCR | 1,2B | 96,87 | — | 88,53 |
| OvisOCR2 | 0,8B | 96,58 | 92,29 | 87,91 |
| PaddleOCR-VL-1.6 | 0,9B | 96,33 | 93,19 | 87,36 |
| MinerU2.5-Pro | 1,2B | 95,75 | 88,94 | 87,33 |
| GLM-OCR | 0,9B | 95,22 | 90,32 | 85,08 |

Trong bảng của Xiaomi, Real5 của Xiaomi cao hơn PaddleOCR-VL-1.6 **2,05 điểm**, còn OmniDocBench thấp hơn TeleOCR **0,04 điểm**. Tuy nhiên, card không cung cấp đủ protocol, độ bất định hoặc cấu hình inference để kết luận thứ hạng tổng quát; đặc biệt **chưa rõ điểm Xiaomi dùng whole-page hay two-stage**. Không ghép các hàng này vào bảng TeleOCR, PaddleOCR hoặc MiniCPM. Chẳng hạn, Wild của PaddleOCR-VL-1.6 là **87,36** ở đây nhưng **91,49** trong bảng MiniCPM, vốn nêu scorer và sửa xoay riêng.

Về triển khai, card mô tả tùy chọn **PP-DocLayoutV3 → nhận dạng vùng → ghép trang**, nhưng mã external chưa được kiểm tra; chưa rõ crop resolution và chi tiết ghép. Prompt bảng yêu cầu **OTSL**, không phải cell boxes; prompt KIE theo JSON schema cũng không bảo đảm output hợp lệ. Whole-page prompt yêu cầu bỏ header/footer, cần kiểm tra nếu workload cần giữ chúng. Card báo cáo **92,27 PubTabNet**, nhưng không đủ protocol để so sánh có kiểm soát. [Chi tiết và giới hạn](../wiki/xiaomi-ocr-0.md).

## 4. FalconOCR: nhỏ hơn, nhưng cần so đúng tập tiếng Anh

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

## 5. Nếu trọng tâm là tài liệu tiếng Việt: SenOCR-Vi

[SenOCR-Vi](../wiki/senocr-vi.md) là bản chuyên biệt hóa từ PaddleOCR-VL-1.6, có **958.588.736 parameter**. Model card báo cáo trên tập tiếng Việt 160 trang của MDPBench:

| Model | Size | Vietnamese document composite ↑ |
|---|---:|---:|
| SenOCR-Vi | 0,959B | **82,83** |
| PaddleOCR-VL-1.6 | khoảng 0,9B | 80,90 |

SenOCR-Vi còn báo cáo **86,7%** cho text recognition theo `1 − edit distance`; con số này **không phải** document composite. Với tập đánh giá EN/VI/ZH, card báo cáo macro **82,98** cho SenOCR-Vi so với **83,43** cho base, nên cải thiện tiếng Việt không đồng nghĩa cải thiện đều mọi ngôn ngữ.

**Giới hạn quan trọng:** 82,83 được tính lại sau khi sửa vấn đề tổng hợp số dòng; 80,90 của base lấy từ leaderboard và chưa được tính lại bằng cùng pipeline đã sửa. Vì vậy chênh **1,93 điểm** là tín hiệu để thử nghiệm, chưa phải so sánh kiểm soát hoàn toàn. [Nguồn và caveat](../wiki/senocr-vi.md#comparability-caveats).

## 6. Các trường hợp ranh giới

| Model | Size | Có nên đưa vào shortlist? | Bằng chứng benchmark |
|---|---:|---|---|
| [Xiaomi-OCR-0](../wiki/xiaomi-ocr-0.md) | 0,8B | Có, nếu muốn thử chế độ layout-first tùy chọn cùng whole-page; mã pipeline ngoài card chưa được kiểm tra. Trọng số phát hành **30/09/2026** theo card. | Card báo cáo **96,83** trên OmniDocBench v1.6 và **95,24** trên Real5; chưa xác định chế độ chạy hay đủ protocol để quy kết các điểm cho pipeline layout-first. |
| [Surya OCR 2](../wiki/surya-ocr-2.md) | 650M cho VLM | Có, nếu muốn thử chế độ block layout-first; hệ thống cũng có chế độ full-page nên không hoàn toàn cùng định nghĩa. | Vendor báo cáo **83,3** trên olmOCR-bench với preset 8.413 test và điều chỉnh cho HTML. Không ghép trực tiếp với bảng Falcon. |
| [Indra OCR](../wiki/indra-ocr.md) | Card nói **7,3M cho toàn bộ model mặc định**, nhưng có mô tả “1M” không được giải thích; tải mặc định khoảng **76 MB** gồm cả language model | Có, nếu ưu tiên **CPU, tốc độ và tài liệu in tương đối sạch** hơn là bảng phức tạp. | Trên [OmniParseBench](../wiki/omniparsebench.md), vendor báo cáo **66,7** mặc định và **71,4** với `--math`, so với **58,4** của PP-StructureV3. So sánh do vendor chạy; PP-StructureV3 thiếu 19 trang và các cấu hình không đối xứng. |
| [OXR-1.0](../wiki/oxr-1-0.md) | 1,3B | Có thể theo dõi, nhưng thiếu dữ liệu để xếp hạng. | README quảng bá thứ hạng cao nhưng bản lưu không có score vector, version benchmark hoặc điều kiện test; layout/recognition flow cũng chưa đủ rõ để xếp chắc vào nhóm lõi. |

## 7. Gợi ý shortlist theo nhu cầu

Đây là **suy luận từ các bảng đã dẫn**, không phải kết luận benchmark độc lập:

- **Điểm tổng thể và bảng trên OmniDocBench v1.6:** thử **TeleOCR** trước, sau đó **PaddleOCR-VL-1.6**. Kiểm tra thêm lỗi lặp và tính ổn định trên tài liệu của bạn.
- **Một model khoảng 0,9B cho nhiều loại tài liệu, kể cả ảnh biến dạng:** thử **PaddleOCR-VL-1.6**; nó dẫn bảng Real5 được lưu.
- **Tài liệu tiếng Anh/Trung, cần throughput hoặc pipeline theo vùng:** thêm **MiniCPM-OCR 1.0** vào shortlist cùng TeleOCR và PaddleOCR-VL-1.6; đo tốc độ và chất lượng trên cùng phần cứng, cấu hình và dữ liệu thực tế. Chưa có bằng chứng trong các trang này để suy ra chất lượng tiếng Việt.
- **Muốn thử một VLM 0,8B có cả whole-page và tùy chọn layout-first:** thêm **Xiaomi-OCR-0** vào thử nghiệm; đo riêng từng chế độ, kiểm tra OTSL, header/footer và phụ thuộc layout. Chưa có bằng chứng trong card đã kiểm tra để quy điểm benchmark cho chế độ two-stage hoặc suy ra chất lượng tiếng Việt.
- **Reading order hoặc đang dùng hệ MinerU:** thử **MinerU2.5-Pro** song song với PaddleOCR-VL-1.6; xác nhận bản 2604 hay 2605 và chức năng cross-page table trong môi trường triển khai, vì model card có mô tả chưa nhất quán về trạng thái tính năng này. [Nguồn](../wiki/mineru2-5-pro.md).
- **Chủ yếu tiếng Anh và cần model nhỏ:** thử **FalconOCR 0,3B**, nhất là nếu workload giống olmOCR-Bench hơn OmniDocBench.
- **Chủ yếu tiếng Việt:** thử **SenOCR-Vi và PaddleOCR-VL-1.6 trên cùng tập**, đặc biệt giữ nguyên cách tính dấu tiếng Việt, bảng và formula. Bằng chứng hiện tại chưa đủ để chốt mức tăng 1,93 điểm.
- **CPU-only, tài liệu đơn giản:** cân nhắc **Indra OCR**, nhưng đánh giá riêng handwriting, scan cũ và bảng có merged cells.

**Giới hạn kiểm tra:** Lần cập nhật này dựa trên diff đã stage, các trang Xiaomi và model card lưu cục bộ; không truy cập web, tải model hay chạy benchmark. `python3 tools/wiki_check.py` đã chạy và báo **OK: 103 concepts, 1 index**; đây là kiểm tra cấu trúc wiki, không xác minh điểm số hay chất lượng output. Trang Xiaomi ở trạng thái **draft**; repository, evaluation code và tài liệu ngoài card chưa được kiểm tra. Các trang MiniCPM liên quan cũng ở trạng thái draft và còn giới hạn coverage, tái lập. Bản so sánh nằm trong `outputs/`; lần cập nhật này không thay đổi wiki.