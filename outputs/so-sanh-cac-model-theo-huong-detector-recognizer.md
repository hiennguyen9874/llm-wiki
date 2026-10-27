# So sánh các model theo hướng Detector → Recognizer

**Kết luận nhanh:** Nếu ưu tiên **OCR chữ thuần với model nhỏ**, PP-OCRv6 là họ có nhiều lựa chọn đáng thử nhất trong các nguồn đã lưu: từ **1,5M đến 34,5M tham số**, và bản medium cải thiện rõ so với PP-OCRv5 trên benchmark nội bộ của tác giả. Nếu ưu tiên **GPU NVIDIA và throughput**, Nemotron OCR v2 đáng cân nhắc, nhưng benchmark của NVIDIA cho thấy đổi lại tốc độ cao thì chất lượng không phải lúc nào cũng hơn PaddleOCR. Nếu cần **CPU, PDF và output có cấu trúc cơ bản**, Indra OCR đáng thử, song nó nằm ở ranh giới giữa OCR theo dòng và document parser.

Điểm quan trọng: **chưa có benchmark được lưu nào chạy tất cả model dưới cùng điều kiện**, nên không thể kết luận một model thắng toàn diện. Các số dưới đây đều do tác giả hoặc nhà cung cấp báo cáo, chưa được tái lập độc lập trong wiki. Nguồn tổng hợp chính: [Detector–recognizer OCR benchmarks](wiki/detector-recognizer-ocr-benchmarks.md) và [OmniParseBench](wiki/omniparsebench.md).

## 1. Phạm vi và ngày ra mắt

Phạm vi chính là các hệ thống phát hiện vùng chữ rồi nhận dạng chữ theo **word hoặc line**: PP-OCRv5/v6 và Nemotron OCR v2. **Indra OCR** được đưa vào như trường hợp mở rộng vì vẫn nhận dạng theo dòng nhưng có thêm layout, reading order và xử lý PDF. PP-StructureV3 là document parser đầy đủ hơn, chỉ dùng làm đối chứng ở một số bảng.

| Model | Thời điểm có thể xác định từ nguồn đã lưu | Ghi chú |
|---|---|---|
| [PP-OCRv5](wiki/pp-ocrv5.md) | Có trong technical report PaddleOCR 3.0 mang mã arXiv `2507.05595` — **tháng 07/2025** | Đây là tháng của report theo mã arXiv, **không khẳng định là ngày phát hành model đầu tiên**. |
| [Nemotron OCR v2](wiki/nemotron-ocr-v2.md) | **15/04/2026** trên NVIDIA Build và NGC | Model card không ghi ngày cụ thể cho Hugging Face. [Nguồn: model card, Release Date](raw/nemotron-ocr-v2.md) |
| [PP-OCRv6](wiki/pp-ocrv6.md) | Technical report mang mã arXiv `2606.13108` — **tháng 06/2026** | Tháng của report theo mã arXiv; chưa xác định được ngày phát hành weights từ nguồn đã kiểm tra. |
| [Indra OCR](wiki/indra-ocr.md) | **Chưa xác định được ngày ra mắt** | Model card lưu trong kho không cung cấp ngày phát hành rõ ràng; ngày tạo trang wiki không phải ngày ra mắt model. |

## 2. So sánh model, size và phạm vi sử dụng

**M = triệu tham số.** Số tham số và dung lượng file là hai đại lượng khác nhau: dung lượng còn phụ thuộc định dạng, precision và các tài nguyên đi kèm.

| Model / biến thể | Size được báo cáo | Phạm vi ngôn ngữ / đơn vị OCR | Điểm đáng chú ý |
|---|---:|---|---|
| **PP-OCRv5 server** | Khoảng **70M** cho hệ thống được report; recognizer **<100 MB** | Chinese, Pinyin, English, Japanese; nhận dạng dòng/vùng | Có server và mobile; nguồn đã lưu không cho đủ số tham số riêng để lập bảng size đầy đủ của cả hai biến thể. |
| **PP-OCRv5 mobile** | Chưa có số tổng đáng tin cậy trong nguồn đã kiểm tra | Cùng họ PP-OCRv5; còn có các checkpoint chuyên English/Latin | Nên so sánh theo checkpoint cụ thể, không mặc định mọi bản mobile có cùng chất lượng. |
| **PP-OCRv6 medium** | **34,5M**: detector 15,5M + recognizer 19M | Report nói hỗ trợ 50 ngôn ngữ | Bản mạnh nhất của v6 trong các bảng nội bộ được lưu. |
| **PP-OCRv6 small** | **7,7M**: detector 2,48M + recognizer 5,2M | Report nói hỗ trợ 50 ngôn ngữ | Điểm cân bằng size–chất lượng đáng thử. |
| **PP-OCRv6 tiny** | **1,5M**: detector 0,43M + recognizer 1,1M, số đã làm tròn | Report nói hỗ trợ 49 ngôn ngữ; **không có Japanese** | Rất nhỏ, nhưng chất lượng recognition giảm đáng kể ở một số tập. |
| **Nemotron OCR v2 English** | **53,8M**, gồm detector, recognizer và relational model | English; xử lý **word-level** | Tối ưu theo tiếng Anh; model card yêu cầu môi trường NVIDIA GPU cho package được tài liệu hóa. |
| **Nemotron OCR v2 multilingual** | **83,9M**, gồm ba thành phần | English, Chinese giản thể/phồn thể, Japanese, Korean, Russian; **line-level** | Nhận dạng đa ngôn ngữ tốt hơn bản English trên các tập không phải English. |
| **Indra OCR** | **7,3M** cho toàn bộ default models; khoảng **76 MB** tài nguyên mặc định, gồm 30 MB networks và 46 MB language models | 80+ ngôn ngữ theo công bố; model card báo cáo đánh giá 95 ngôn ngữ | CPU/ONNX; thêm layout, reading order và khả năng dùng text layer PDF. Model math tùy chọn không tính trong số mặc định. |

Nguồn chi tiết: [PP-OCRv6 — bảng tham số detector/recognizer](raw/2606.13108_PP-OCRv6/main.tex), [Nemotron OCR v2 — Parameter Counts](raw/nemotron-ocr-v2.md), [Indra OCR — Installation](raw/datalab-to-indra-ocr.md), [PP-OCRv5](wiki/pp-ocrv5.md).

**Lưu ý về Indra:** Phần giới thiệu model card gọi nó là “1M-parameter”, nhưng phần cài đặt ghi recognizer Latin khoảng 1,25M và **toàn bộ model mặc định 7,3M**. Hai cách đếm không được tác giả giải thích rõ; không nên so “1M” trực tiếp với tổng pipeline của các model khác. [Nguồn](wiki/indra-ocr.md#contradictions)

**Về tiếng Việt:** Các nguồn đã kiểm tra chưa cung cấp một bảng benchmark tiếng Việt chung cho các model này. Con số “50 ngôn ngữ” không đủ để kết luận chất lượng tiếng Việt, đặc biệt với dấu thanh và tài liệu chuyên ngành.

---

## 3. Benchmark trực tiếp: PP-OCRv5 so với PP-OCRv6

Đây là so sánh có cùng bảng và metric giữa các biến thể PaddleOCR, nhưng **do nhóm PP-OCRv6 tự xây dựng benchmark**; không có đầy đủ dataset và cấu hình để tái lập.

### 3.1. Text detection — 16 nhóm dữ liệu nội bộ

Metric: **Hmean %, càng cao càng tốt**.

| Model | Trung bình | Chữ viết tay Trung | Chữ viết tay Anh | Japanese | Xoay | Công nghiệp |
|---|---:|---:|---:|---:|---:|---:|
| PP-OCRv5 server | 81,6 | 80,3 | **84,1** | 77,2 | 80,0 | 64,3 |
| PP-OCRv5 mobile | 75,2 | 74,4 | 77,7 | 72,7 | 64,7 | 52,8 |
| **PP-OCRv6 medium** | **86,2** | **83,7** | 84,0 | **84,3** | **93,8** | **73,3** |
| PP-OCRv6 small | 84,1 | 80,5 | **87,1** | 82,3 | 93,7 | 67,6 |
| PP-OCRv6 tiny | 80,6 | 79,4 | 85,9 | 76,6 | 91,0 | 62,0 |

**Đọc bảng:** v6 medium hơn v5 server **4,6 điểm** trung bình, đặc biệt đáng chú ý trên nhóm ảnh xoay: **93,8 so với 80,0**. Tuy nhiên, medium không thắng mọi nhóm: trên chữ viết tay tiếng Anh, v6 small đạt 87,1 và v5 server đạt 84,1 so với 84,0 của medium.

### 3.2. Text recognition — 15 nhóm dữ liệu nội bộ

Metric: **accuracy %, weighted average**, càng cao càng tốt.

| Model | Weighted average | Viết tay Trung | Viết tay Anh | In tiếng Anh | Japanese | Công nghiệp |
|---|---:|---:|---:|---:|---:|---:|
| PP-OCRv5 server | 78,1 | 58,0 | 59,6 | 85,1 | 73,7 | 70,2 |
| PP-OCRv5 mobile | 73,7 | 41,7 | 50,9 | 86,0 | 75,8 | 59,3 |
| **PP-OCRv6 medium** | **83,2** | **62,1** | **67,8** | **94,1** | **90,5** | **77,4** |
| PP-OCRv6 small | 81,3 | 57,6 | 61,1 | 93,3 | 88,2 | 76,4 |
| PP-OCRv6 tiny | 73,5 | 40,1 | 39,3 | 88,4 | 89,8 | 62,1 |

**Đọc bảng:**

- v6 medium hơn v5 server **5,1 điểm** weighted accuracy; small cũng đạt **81,3** với 7,7M tham số.
- Tiny không phải lựa chọn “miễn phí”: weighted average **73,5**, chữ viết tay Anh **39,3**, thấp hơn đáng kể so với medium.
- **Cần thận trọng với cột Japanese của tiny:** report có hàng kết quả Japanese, trong khi mô tả release nói tiny không hỗ trợ Japanese. Nguồn wiki chưa giải thích rõ sự khác biệt giữa cấu hình benchmark và cấu hình hỗ trợ; không nên dùng con số đó để khẳng định tiny hỗ trợ Japanese.

Các số và bảng đầy đủ: [Detector–recognizer OCR benchmarks — detection và recognition](wiki/detector-recognizer-ocr-benchmarks.md#pp-ocrv6-in-house-detection-benchmark); [technical report gốc](raw/2606.13108_PP-OCRv6/main.tex).

### 3.3. English và Latin: model chung so với checkpoint chuyên dụng

Accuracy trên các tập English/Latin riêng của nhóm PP-OCRv6; **nguồn không cung cấp danh tính và thành phần dataset**.

| Model | English | Latin |
|---|---:|---:|
| PP-OCRv5 server | 79,5 | — |
| PP-OCRv5 mobile | 78,3 | — |
| `en_PP-OCRv5_mobile` | 86,0 | — |
| `latin_PP-OCRv5_mobile` | 77,8 | 81,4 |
| **PP-OCRv6 medium** | **88,4** | **88,0** |
| PP-OCRv6 small | 86,3 | 84,0 |
| PP-OCRv6 tiny | 77,3 | 63,8 |

Trên **chính tập này**, v6 medium vượt cả các checkpoint chuyên dụng v5 được liệt kê; small gần bằng `en_PP-OCRv5_mobile` trên English. Tiny giảm mạnh trên Latin. Đây không thay thế cho benchmark tiếng Việt. [Nguồn](wiki/detector-recognizer-ocr-benchmarks.md#english-and-latin-script-recognition)

---

## 4. Benchmark trực tiếp: Nemotron OCR v2 so với PaddleOCR, OpenOCR và EasyOCR

### 4.1. OmniDocBench crop mode — chất lượng và throughput

Metric chất lượng là **NED — normalized edit distance**, càng thấp càng tốt. Throughput được NVIDIA báo cáo trên **một A100**. Bảng này **bỏ qua prediction rỗng**, và model card không ghi đầy đủ batch size, preprocessing, runtime hay phiên bản benchmark; vì vậy đây là so sánh tham khảo theo setup của NVIDIA, không phải benchmark triển khai đã kiểm soát đầy đủ.

| Model | Trang/s ↑ | English NED ↓ | Chinese NED ↓ | Mixed EN/ZH NED ↓ | Xoay 90° NED ↓ | Xoay 270° NED ↓ |
|---|---:|---:|---:|---:|---:|---:|
| PaddleOCR v5 server | 1,2 | 0,027 | 0,037 | **0,041** | 0,116 | 0,897 |
| OpenOCR server | 1,5 | **0,024** | **0,033** | 0,049 | **0,042** | 0,761 |
| **Nemotron v2 multilingual** | **34,7** | 0,048 | 0,072 | 0,142 | 0,109 | **0,332** |
| Nemotron v2 English | **40,7** | 0,038 | 0,830 | 0,437 | 0,232 | 0,827 |
| EasyOCR | 0,4 | 0,095 | 0,117 | 0,326 | 0,987 | 0,979 |
| Nemotron v1 | 39,3 | 0,038 | 0,876 | 0,436 | 0,358 | 0,871 |

**Diễn giải:**

- **PaddleOCR v5 và OpenOCR có NED tốt hơn Nemotron multilingual** trên English, Chinese và mixed trong bảng này.
- Nemotron multilingual được báo cáo **34,7 trang/s so với 1,2 trang/s** của PaddleOCR v5 server — khoảng **29 lần** theo đúng số của bảng, nhưng không nên coi đó là tỷ lệ tốc độ phổ quát.
- Nemotron multilingual xử lý nhóm **xoay 270°** tốt hơn các đối thủ được liệt kê, dù NED 0,332 vẫn cho thấy nhóm này khó.
- Không dùng bản Nemotron English như model Chinese: NED **0,830** so với **0,072** của multilingual.

[Nguồn: NVIDIA model card, bảng OmniDocBench](raw/nemotron-ocr-v2.md); [bảng đầy đủ và giới hạn](wiki/detector-recognizer-ocr-benchmarks.md#nemotron-ocr-v2-omnidocbench-crop-mode).

### 4.2. SynthDoG tổng hợp — OCR đa ngôn ngữ

Metric: **page-average NED**, càng thấp càng tốt. Đây là dữ liệu **tổng hợp**, không phải bằng chứng đủ cho hiệu quả trên tài liệu thực tế.

| Ngôn ngữ | PaddleOCR base | PaddleOCR specialized | OpenOCR server | Nemotron v2 English | **Nemotron v2 multilingual** |
|---|---:|---:|---:|---:|---:|
| English | 0,117 | 0,096 | 0,105 | 0,079 | **0,069** |
| Japanese | 0,201 | 0,201 | 0,586 | 0,765 | **0,046** |
| Korean | 0,943 | 0,133 | 0,837 | 0,924 | **0,047** |
| Russian | 0,959 | 0,163 | 0,950 | 0,632 | **0,043** |
| Chinese giản thể | 0,054 | 0,054 | 0,061 | 0,819 | **0,035** |
| Chinese phồn thể | 0,094 | 0,094 | 0,127 | 0,756 | **0,065** |

Nemotron multilingual đứng đầu cả sáu dòng trong bảng SynthDoG này, nhưng **không mâu thuẫn** với kết quả OmniDocBench ở trên: tập dữ liệu và cách tính khác nhau. Nguồn không cung cấp seed hoặc cấu hình sinh dữ liệu đầy đủ. [Nguồn](wiki/detector-recognizer-ocr-benchmarks.md#nemotron-ocr-v2-generated-synthdog)

---

## 5. Benchmark CPU: Indra OCR, PP-OCRv6 small và Tesseract

### OmniParseBench — cùng scorer, do Datalab chạy

Đây là benchmark document parsing gồm **16.288 phép thử pass/fail trên 2.937 trang**. Bảng báo cáo chạy trên x86, **4 vCPU/engine**, một trang mỗi lần, với default settings.

| Engine | Chế độ | Điểm text ↑ | Tables ↑ | Layout ↑ | Trung vị ms/trang ↓ |
|---|---|---:|---:|---:|---:|
| **Indra OCR** | `auto`: text layer + OCR | 46,7 | 61,1 | 92,2 | **212** |
| **Indra OCR** | OCR only | **40,7** | 52,7 | 90,3 | **344** |
| Indra OCR | `auto --math` | 62,7 | 59,6 | 92,0 | 357 |
| PP-OCRv6 small qua RapidOCR | Text models only | 35,8 | 0,0 | Không chấm | 2.685 |
| Tesseract 5 | Latin model | 19,3 | 0,0 | Không chấm | 5.496 |
| PP-StructureV3 | Full parser | 55,6 | 47,8 | 71,7 | 40.958 |

**Cách đọc công bằng hơn:**

1. Với câu hỏi về OCR ảnh thuần, hàng Indra **OCR only** phù hợp hơn `auto`, vì `auto` có thể tận dụng text layer PDF. Trên bảng này: **40,7 so với 35,8** điểm text của PP-OCRv6 small, và **344 so với 2.685 ms/trang**.
2. Đây vẫn **không phải so sánh hoàn toàn cân bằng**: Indra có thêm layout/reading order; RapidOCR chỉ chạy text models; các engine chạy với cấu hình mặc định và do chính Datalab thực hiện.
3. Điểm table **0** của PP-OCR và Tesseract phản ánh chúng xuất **dòng chữ thay vì cấu trúc bảng**; không có nghĩa chúng không đọc được chữ nằm trong bảng.
4. Indra và đối thủ không hoàn toàn cùng một lần chạy; nguồn nói latency giữa các lần chạy có thể dao động khoảng **15%**. PP-StructureV3 thiếu 19 trang do một shard bị treo.
5. `--math` cải thiện text score trong bảng nhưng thêm model, tốn thời gian hơn, và điểm bảng giảm nhẹ.

[Nguồn gốc: Indra model card, OmniParseBench](raw/datalab-to-indra-ocr.md); [phân tích protocol](wiki/omniparsebench.md#protocol-caveats).

### Throughput CPU riêng

Trên 300 trang OmniParseBench, AMD EPYC 9004, OCR mode, một worker đơn luồng mỗi core:

| Engine | 4 cores | 8 cores | 16 cores | 32 cores |
|---|---:|---:|---:|---:|
| **Indra OCR** | **6,2** | **11,9** | **23,7** | **43,9** trang/s |
| PP-OCRv6 small, RapidOCR | 0,65 | 1,24 | 2,42 | 4,28 trang/s |
| Tesseract 5 | 0,78 | 1,37 | 2,27 | 2,92 trang/s |

Ở 32 cores, Indra đạt khoảng **10,3 lần** throughput PP-OCRv6 small trong run do Datalab báo cáo. Đây là **một protocol CPU riêng**, không so trực tiếp với trang/s trên A100 của Nemotron. Model loading và một trang warm-up mỗi worker không được tính. [Nguồn](raw/datalab-to-indra-ocr.md).

---

## 6. Chọn model theo nhu cầu

| Nhu cầu | Lựa chọn nên thử trước | Lý do và giới hạn |
|---|---|---|
| **OCR tổng quát, ưu tiên chất lượng trong họ nhỏ** | **PP-OCRv6 medium** | Dẫn các biến thể PP-OCR trong trung bình detection/recognition nội bộ; 34,5M. Cần tự kiểm tra tiếng Việt và dữ liệu thực tế. |
| **Cân bằng size–chất lượng** | **PP-OCRv6 small** | 7,7M; weighted recognition 81,3 so với 83,2 của medium trên tập nội bộ. |
| **Thiết bị rất hạn chế tài nguyên** | **PP-OCRv6 tiny** | 1,5M, nhưng cần chấp nhận suy giảm trên handwriting/Latin và kiểm tra hỗ trợ ngôn ngữ. |
| **NVIDIA GPU, xử lý nhiều trang; cần nhóm chữ và reading order** | **Nemotron v2 multilingual** | Throughput NVIDIA báo cáo cao trong crop mode; không phải model có NED tốt nhất trên mọi tập. Package được tài liệu hóa yêu cầu NVIDIA GPU. |
| **CPU, PDF số + scan, cần output Markdown/boxes** | **Indra OCR** | Có routing text layer, layout và benchmark CPU thuận lợi trong run của Datalab. Cần xem license weights và kiểm tra handwriting, scan cũ, bảng phức tạp. |
| **Tiếng Việt là yêu cầu chính** | **Chưa đủ bằng chứng để chọn model thắng** | Nên chạy tập tiếng Việt riêng, đo CER/WER, dấu thanh, tốc độ, memory và tỷ lệ lỗi theo loại tài liệu. |

**Giới hạn và cách kiểm tra:** Tôi đã đọc các bảng benchmark trong wiki **và kiểm tra nguồn gốc lưu tại `raw/`**, gồm technical report PP-OCRv6 và model card NVIDIA/Datalab; không chạy inference hay benchmark, cũng không kiểm tra nguồn web mới ngoài kho. Báo cáo này được để **transient**, vì wiki đã có các trang benchmark tổng hợp; wiki và log không thay đổi.