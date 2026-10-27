# Tổng quan: nên chọn hướng OCR nào?

**Kết luận ngắn:** đừng bắt đầu bằng câu hỏi “model OCR nào tốt nhất?”. Hãy xác định **đầu ra cần dùng**: chỉ cần chữ và tọa độ, cần dựng lại tài liệu, hay cần trích xuất các trường nghiệp vụ. Sau đó chọn pipeline đơn giản nhất đáp ứng yêu cầu; chỉ bổ sung model chuyên biệt hoặc bước kiểm tra khi thấy lỗi trên dữ liệu thực tế.

Tôi đã đọc các tài liệu tổng hợp và cả 8 trang task bạn chỉ định. Phần khuyến nghị bên dưới là **tổng hợp thực hành từ wiki**, không phải kết quả benchmark tôi tự chạy. Các tài liệu khởi điểm là [Current OCR approaches](wiki/current-ocr-approaches.md), [PDF-to-Markdown tool selection](wiki/pdf-to-markdown-tool-selection.md) và [PDF-to-Markdown parser architectures](wiki/pdf-to-markdown-parser-architectures.md).

---

## 1. Phân biệt các bài toán trước khi chọn model

Một hệ thống xử lý tài liệu thường đi qua các tầng sau:

```text
PDF / ảnh
  │
  ├─ PDF có text layer đáng tin? ──► Trích xuất chữ và vị trí trực tiếp
  │
  └─ Scan / ảnh / text layer lỗi ──► OCR nhận diện chữ
                                      │
             Layout + reading order ◄─┤
             Bảng / công thức       ◄─┤
                                      ▼
                         Document: Markdown / HTML / JSON
                                      │
                         KIE: trích xuất trường theo schema
                                      ▼
                         Kiểm tra → xuất kết quả / RAG
```

Các tầng này **không nhất thiết là các model riêng**: một VLM có thể làm nhiều việc trong một lượt; ngược lại, một pipeline modular có thể dùng nhiều model chuyên biệt.

| Bài toán | Câu hỏi chính | Đầu ra |
|---|---|---|
| **Text detection + recognition** | Chữ nằm ở đâu và viết gì? | Text box/polygon và chữ |
| **Layout + reading order** | Vùng nào là tiêu đề, đoạn, bảng… và đọc theo thứ tự nào? | Vùng có loại, tọa độ và thứ tự |
| **Table structure** | Hàng, cột, ô gộp được tổ chức ra sao? | Cấu trúc ô hoặc HTML |
| **Document parsing** | Làm sao tái tạo cả trang thành tài liệu có cấu trúc? | Markdown, HTML, JSON |
| **KIE — key information extraction** | Số hóa đơn, ngày, tổng tiền… là gì? | Key-value hoặc JSON theo schema |
| **Grounding** | Một nội dung hoặc đối tượng cụ thể nằm ở đâu? | Box, polygon, mask hoặc điểm |
| **Cross-page table** | Bảng ở trang này có tiếp tục sang trang sau không? | Bảng đã nối kèm nguồn trang |

Nguồn: [layout và reading order](wiki/task-layout-analysis-reading-order.md), [table structure](wiki/task-table-structure-recognition.md), [KIE](wiki/task-structured-extraction-kie.md), [grounding](wiki/task-unified-perception-grounding.md), [cross-page table](wiki/task-cross-page-table-reconstruction.md).

---

## 2. Các hướng OCR và khi nào nên dùng

### Hướng A — Ưu tiên text layer cho PDF điện tử

**Cách làm:** đọc text và tọa độ từ chính PDF, dùng quy tắc hoặc layout analysis để sắp xếp; chỉ OCR khi text layer thiếu hoặc không đáng tin.

**Nên dùng khi:** PDF sinh từ Word, LaTeX hoặc hệ thống xuất báo cáo; cần xử lý số lượng lớn, CPU-only, chi phí thấp.

**Điểm cần chú ý:**

- Có text layer không đồng nghĩa với đúng reading order hoặc đúng cấu trúc bảng.
- PDF scan có thể có text layer OCR cũ nhưng lỗi; cần kiểm tra thay vì tin tuyệt đối.
- PDF hỗn hợp có thể có trang điện tử và trang scan trong cùng một file.

**Công cụ nên thử:** [LiteParse](wiki/liteparse.md), [OpenDataLoader PDF](wiki/opendataloader-pdf.md), [Marker](wiki/marker.md). Đây là lựa chọn khởi đầu, không phải cam kết rằng tool-free/model-free sẽ xử lý tốt mọi bảng hay layout phức tạp. Xem [so sánh kiến trúc](wiki/pdf-to-markdown-parser-architectures.md).

### Hướng B — Detector → recognizer: OCR chữ theo dòng hoặc vùng

**Cách làm:** model thứ nhất phát hiện vùng chữ; model thứ hai đọc chữ trong từng vùng.

**Nên dùng khi:**

- Cần chữ kèm bounding box, không cần dựng lại toàn bộ tài liệu.
- Cần chạy nhanh, CPU/mobile hoặc số lượng lớn.
- Xử lý ảnh chụp nhãn, biển hiệu, màn hình, biểu mẫu đơn giản.

**Ví dụ:** [PP-OCRv6](wiki/pp-ocrv6.md), [Nemotron OCR v2](wiki/nemotron-ocr-v2.md); [Indra OCR](wiki/indra-ocr.md) mở rộng hướng này bằng layout nhẹ và định tuyến theo script.

**Hạn chế:** text box không tự giải quyết thứ tự đọc, bảng, công thức hay phân cấp tài liệu. Nếu cần những phần đó, phải bổ sung xử lý khác hoặc chọn document parser. Nguồn: [Detector–recognizer OCR](wiki/task-detector-recognizer-ocr.md).

### Hướng C — Layout-first modular: phân vùng rồi xử lý chuyên biệt

**Cách làm:**

```text
Trang → phát hiện layout + thứ tự đọc
      → crop từng vùng ở độ phân giải phù hợp
      → text recognizer / table recognizer / formula recognizer / ...
      → ghép thành tài liệu
```

**Nên dùng khi:**

- Tài liệu nhiều cột, chữ nhỏ, bảng, công thức, dấu/mộc.
- Cần tọa độ vùng và khả năng kiểm tra từng thành phần.
- Cần thay riêng recognizer cho một ngôn ngữ hoặc một loại nội dung.
- Muốn xử lý có kiểm soát hơn thay vì giao cả trang cho một model sinh văn bản.

**Ví dụ:** [PP-StructureV3](wiki/pp-structurev3.md), [PaddleOCR-VL-1.6](wiki/paddleocr-vl-1-6.md), [GLM-OCR](wiki/glm-ocr.md), [MinerU2.5](wiki/mineru2-5.md).

**Đánh đổi:** nhiều thành phần và cấu hình hơn; nếu phát hiện sai vùng hoặc sai thứ tự, lỗi có thể lan sang các bước sau. Đây là lựa chọn tốt để **đánh giá đầu tiên** cho tài liệu phức tạp, không phải bảo đảm luôn tốt hơn VLM end-to-end. Nguồn: [Layout-first modular parsing](wiki/task-layout-first-modular-parsing.md).

### Hướng D — End-to-end generative OCR: ảnh trang → tài liệu

**Cách làm:** đưa cả ảnh trang cho document VLM để sinh Markdown, HTML, JSON hoặc biểu diễn khác.

**Nên dùng khi:**

- Muốn chuyển trang sang Markdown/HTML mà không tự ghép nhiều component.
- Cần xử lý linh hoạt bảng, công thức hoặc nội dung đa dạng.
- Có tài nguyên inference phù hợp và chấp nhận đánh giá kỹ đầu ra sinh.

**Ví dụ:** [OvisOCR3](wiki/ovisocr3.md), [DeepSeek-OCR 2](wiki/deepseek-ocr-2.md), [LightOnOCR-3](wiki/lightonocr-3.md), [Chandra OCR 2](wiki/chandra-ocr-2.md).

**Đánh đổi:** có nguy cơ sinh thiếu, lặp hoặc bịa; output dài làm tăng chi phí; không phải model nào cũng trả tọa độ hoặc tuân thủ schema theo cùng cách. Prompt phải theo interface của từng model — chẳng hạn LightOnOCR-3 có mode transcription và `grounding` riêng. Nguồn: [End-to-end generative OCR](wiki/task-end-to-end-generative-ocr.md).

### Hướng E — KIE và grounding: dùng *sau* hoặc *cùng* OCR

Đây là các bài toán liên quan nhưng **không đồng nghĩa với OCR**:

- **KIE:** lấy trường nghiệp vụ như `invoice_number`, `date`, `total`. Cần xác thực schema, kiểu dữ liệu và đối chiếu bằng chứng; JSON hợp lệ chưa chứng minh giá trị đúng. Ví dụ: [PP-ChatOCRv4](wiki/pp-chatocrv4.md), [lift](wiki/lift.md), [OvisOCR3](wiki/ovisocr3.md).
- **Grounding:** xác định vùng chứa nội dung hoặc đối tượng được hỏi. Hữu ích cho highlight, audit và human review. [Rex-Omni](wiki/rex-omni.md) và [GroundAnything](wiki/groundanything.md) thiên về perception/grounding; chúng **không mặc nhiên thay thế** pipeline chuyển cả tài liệu thành Markdown.

Nguồn: [Structured extraction and KIE](wiki/task-structured-extraction-kie.md), [Unified perception and grounding](wiki/task-unified-perception-grounding.md).

---

## 3. Khi nào cần kết hợp nhiều model?

**Không nên kết hợp chỉ vì có nhiều model.** Mỗi bước thêm latency, vận hành và khả năng truyền lỗi. Nên kết hợp khi có một lỗi hoặc yêu cầu cụ thể mà một bước đơn lẻ không đáp ứng.

| Tình huống | Cách kết hợp nên thử | Vì sao |
|---|---|---|
| **PDF hỗn hợp**: trang điện tử lẫn scan | Text-layer extraction → kiểm tra chất lượng → OCR trang/vùng cần thiết | Tránh OCR toàn bộ khi phần chữ gốc dùng được |
| **Chữ đúng nhưng thứ tự đọc sai** | Layout/order model + recognizer | Detection chữ không tự biết cấu trúc nhiều cột |
| **Bảng hoặc công thức khó** | Layout detector → table/formula specialist → ghép lại | Xử lý từng loại vùng bằng phương pháp phù hợp |
| **Tiếng Việt là trọng tâm** | Layout/parser + recognizer chuyên tiếng Việt; thử [SenOCR-Vi](wiki/senocr-vi.md) trong pipeline PaddleOCR-VL | Thay đúng thành phần nhận dạng thay vì tự xây lại toàn bộ |
| **Cần trường nghiệp vụ** | OCR/parser → KIE/LLM theo schema → validation và đối chiếu vị trí | Tách transcription khỏi suy luận và kiểm tra nghiệp vụ |
| **Trang khó hoặc kết quả đáng ngờ** | Pipeline nhanh → kiểm tra → parser/VLM khác cho trang hoặc vùng lỗi | Dành compute đắt cho trường hợp cần thiết |
| **Cần độ tin cậy cao** | Hai kết quả độc lập để phát hiện bất đồng → đối chiếu ảnh/human review | Bất đồng là tín hiệu kiểm tra, không chứng minh model nào đúng |
| **Bảng qua nhiều trang** | Parse từng trang → nhận biết continuation → nối bảng | Cấu trúc một bảng đơn trang không đủ để quyết định nối qua trang |

Đây là **khuyến nghị tổng hợp**, không phải kết quả đo rằng mọi tổ hợp sẽ nhanh hơn hay chính xác hơn. Nguồn nền: [kiến trúc routing](wiki/pdf-to-markdown-parser-architectures.md), [layout-first](wiki/task-layout-first-modular-parsing.md), [KIE](wiki/task-structured-extraction-kie.md), [cross-page tables](wiki/task-cross-page-table-reconstruction.md).

### Một vài trường hợp đặc biệt

**Bảng phức tạp.** OCR đúng chữ trong ô vẫn có thể ghép sai hàng/cột. Nếu có ô gộp, header nhiều tầng hay bảng không có đường kẻ, hãy đánh giá riêng cấu trúc bảng. Giữ HTML hoặc biểu diễn cell/span nếu downstream cần cấu trúc; Markdown có thể làm mất thông tin span. Xem [Table structure recognition](wiki/task-table-structure-recognition.md).

**Bảng qua trang.** [OvisOCR3](wiki/ovisocr3.md) mô tả quy trình dùng **cùng một checkpoint hai lần**: parse từng trang, rồi đưa cặp trang liền kề cùng kết quả parse để quyết định và nối bảng. Đây là kết hợp nhiều *bước*, không nhất thiết nhiều *model*. Kết quả vẫn phụ thuộc parse ban đầu và thứ tự trang. Xem [Cross-page table reconstruction](wiki/task-cross-page-table-reconstruction.md).

**Tiếng Việt.** [SenOCR-Vi](wiki/senocr-vi.md) là bản chuyên tiếng Việt dựa trên PaddleOCR-VL-1.6 và có interface để dùng làm recognizer trong pipeline đó. Model card báo cáo cải thiện trên lát cắt tiếng Việt, nhưng wiki ghi rõ giới hạn so sánh và chưa tự tái lập kết quả. Hãy thử trên scan, ảnh chụp, dấu tiếng Việt, chữ viết tay và bảng của chính bạn; không nên suy ra model này tốt nhất cho mọi ngôn ngữ hay mọi tài liệu.

**Dùng confidence để routing.** [Docling confidence grades](wiki/docling-confidence-grades.md) có grade theo trang/tài liệu để hỗ trợ chọn review hoặc xử lý lại. Tuy nhiên, tài liệu được lưu trong wiki nói thành phần `table_score` **chưa được triển khai**: không nên dùng grade chung như bảo đảm bảng đúng.

---

## 4. Thư viện, toolkit và model: nên dùng cái nào?

Điều quan trọng là phân biệt **toolkit/pipeline** với **model**: ví dụ, PaddleOCR là toolkit; PP-OCR và PaddleOCR-VL là các model/pipeline trong hệ sinh thái đó. Một toolkit có thể tự kết hợp nhiều model, nên bạn không nhất thiết phải tự viết orchestration.

| Công cụ | Vai trò và trường hợp nên thử |
|---|---|
| [PaddleOCR](wiki/paddleocr-3.md) | Toolkit có Python API/CLI, từ OCR chữ đến structured parsing và KIE. Thích hợp khi muốn chọn hoặc phối hợp các component trong cùng hệ sinh thái. |
| [MinerU](wiki/mineru.md) | Document parser xuất Markdown/JSON; có backend pipeline, VLM và hybrid. Nên thử với PDF scan, tài liệu khoa học hoặc layout phức tạp. Hybrid được dự án mô tả là kết hợp VLM với native text. |
| [Docling](wiki/docling-architecture.md) | Framework chuyển tài liệu sang `DoclingDocument`, phù hợp khi cần cấu trúc trung gian, metadata và chunking cho RAG, không chỉ Markdown. Có nhiều [OCR engine tích hợp](wiki/docling-ocr-engines.md). |
| [Marker](wiki/marker.md) | Pipeline chuyển PDF/tài liệu thành Markdown, JSON, HTML hoặc chunks; kết hợp text layer, layout và OCR chọn lọc. Có tùy chọn dùng LLM để hỗ trợ vùng khó. |
| [LiteParse](wiki/liteparse.md) | Baseline không dùng model cho text-layer PDF; có OCR tùy chọn. Hợp để thử trên PDF điện tử đơn giản, CPU-only; wiki lưu ý heuristic có giới hạn với bảng dày đặc và trang khó. |
| [OpenDataLoader PDF](wiki/opendataloader-pdf.md) | Parser ưu tiên extraction/geometry cục bộ, có AI tùy chọn; đáng thử khi ưu tiên throughput CPU và PDF điện tử. |
| [Tesseract, RapidOCR, EasyOCR](wiki/docling-ocr-engines.md) | OCR engine có thể dùng trong tích hợp Docling; chọn theo ngôn ngữ, OS và runtime. Đây không tự động là giải pháp đầy đủ cho bảng, layout và reading order. |
| [Surya OCR 2](wiki/surya-ocr-2.md) | Hệ thống OCR/layout/table; [Marker](wiki/marker.md) sử dụng Surya trong pipeline của mình. |
| [Transformers / vLLM](wiki/senocr-vi.md) | Runtime/inference stack cho một số model VLM; ví dụ SenOCR-Vi có hướng dẫn Transformers, còn [Chandra OCR 2](wiki/chandra-ocr-2.md) tài liệu hóa vLLM và Transformers. Chúng không thay thế các bước xử lý PDF, routing và validation của ứng dụng. |

**Lưu ý triển khai:** hỗ trợ ngôn ngữ, GPU/CPU, phiên bản runtime và license phải kiểm tra theo đúng phiên bản model và tool. Ví dụ, wiki ghi [Marker](wiki/marker.md) có điều kiện license riêng cho model weights, còn README [MinerU](wiki/mineru.md) mô tả license có điều kiện bổ sung nhưng wiki chưa kiểm tra toàn văn license. Nếu dùng LLM/API bên ngoài, cần kiểm tra thêm quyền gửi tài liệu, chi phí và chính sách dữ liệu.

---

## 5. Chọn nhanh theo bài toán

| Nhu cầu | Bắt đầu thử |
|---|---|
| Chỉ cần text + box, ưu tiên CPU/mobile | **PaddleOCR / PP-OCR**, hoặc OCR engine phù hợp ngôn ngữ |
| PDF điện tử, volume lớn, ít bảng phức tạp | **LiteParse hoặc OpenDataLoader PDF**, có fallback OCR |
| PDF scan, nhiều cột, bảng/công thức | **MinerU hoặc PaddleOCR-VL / PP-StructureV3** |
| Muốn một document VLM sinh Markdown trực tiếp | **OvisOCR3, LightOnOCR-3, DeepSeek-OCR 2** — kiểm tra prompt, cấu trúc và output |
| PDF → RAG có metadata/cấu trúc | **Docling**; so sánh với Marker/MinerU trên retrieval thực tế |
| Tài liệu tiếng Việt | Thử **SenOCR-Vi + PaddleOCR-VL pipeline**, so với một baseline tổng quát trên cùng tập dữ liệu |
| Hóa đơn, hợp đồng → JSON nghiệp vụ | **Parser/OCR + KIE + schema validation + đối chiếu evidence** |
| Bảng xuyên trang | Parser có hỗ trợ hoặc thêm bước như quy trình **OvisOCR3**; lưu `source_pages` |
| Highlight vùng theo truy vấn / tương tác thị giác | Model có **grounding**, tách biệt với yêu cầu dựng toàn tài liệu |

Đây là **danh sách ứng viên để benchmark**, không phải xếp hạng. Việc chọn MinerU/Marker/Docling theo use case dựa một phần trên so sánh nguồn trong wiki; chính trang đó ghi đây không phải benchmark độc lập chung. Xem [PDF-to-Markdown tool selection](wiki/pdf-to-markdown-tool-selection.md).

---

## 6. Quy trình đánh giá thực tế đề xuất

1. **Lấy 20–50 tài liệu đại diện**, không chỉ PDF điện tử đẹp: scan, ảnh chụp, nhiều cột, bảng ô gộp, công thức, tiếng Việt và các trường hợp quan trọng với bạn.
2. **Xác định ground truth theo nhu cầu:** văn bản, thứ tự đọc, bảng, công thức, tọa độ, trường KIE — không chỉ chấm “Markdown nhìn có đẹp không”.
3. **Chạy 2–3 pipeline** trên cùng đầu vào, cấu hình render và điều kiện phần cứng được ghi lại.
4. **Chấm tách biệt:** lỗi chữ/dấu tiếng Việt; thiếu hoặc thừa nội dung; thứ tự; cấu trúc bảng; độ đúng trường; tỷ lệ cần human review.
5. **Đo vận hành:** latency, throughput, RAM/VRAM, chi phí, tỷ lệ lỗi và yêu cầu privacy.
6. **Chỉ thêm fallback hoặc specialist** cho loại lỗi có tần suất và chi phí đủ đáng kể. Với tài liệu pháp lý/tài chính hoặc trường quan trọng, giữ nguồn trang/vùng và có human review.

Khuyến nghị lấy mẫu và phân rã các hạng mục đánh giá dựa trên [PDF-to-Markdown tool selection](wiki/pdf-to-markdown-tool-selection.md); các bước routing và kiểm soát là tổng hợp từ những trang task đã đọc.

### Giới hạn bằng chứng

Các tổng hợp OCR chính trong wiki có trạng thái `draft`; nhiều kết quả model là **tác giả hoặc nhà cung cấp báo cáo**, không phải kiểm chứng độc lập. Điểm benchmark giữa các paper không thể ghép thành một leaderboard chung khi khác dữ liệu, phiên bản benchmark, prompt và cấu hình. Tôi **không chạy OCR hay benchmark**, không nghiên cứu thêm trong `raw/`, và để câu trả lời này ở dạng tạm thời, không ghi thêm vào wiki.