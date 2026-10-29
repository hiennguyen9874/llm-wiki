# PaddleOCR vs MinerU vs Docling

**Kết luận ngắn:** không nên xem đây là ba OCR engine tương đương rồi chọn một “con thắng toàn diện”.

- **PaddleOCR:** nên ưu tiên khi cần **OCR như một thành phần có thể huấn luyện, thay thế và tối ưu**, từ model nhỏ chạy CPU/edge đến document parser dùng VLM.
- **MinerU 4:** nên ưu tiên đánh giá khi cần **workflow xử lý tài liệu hoàn chỉnh**: parsing theo mức chất lượng, xuất nội dung có cấu trúc, thư viện cục bộ, cache/search và đọc tiếp theo page/block.
- **Docling:** nên ưu tiên khi cần **document ingestion có hợp đồng dữ liệu rõ**, giữ cấu trúc/provenance để đưa vào chunking, RAG và các bước xử lý downstream.

Đây là **kết luận lựa chọn từ kiến trúc**, không phải thứ hạng accuracy đã được benchmark chung.

Mình đã đọc các concept liên quan và đối chiếu thêm raw về implementation, benchmark và license. Phạm vi là các snapshot trong repository: PaddleOCR `dab3fe3`, MinerU 4.0.12 `b7f3dd0`, Docling `8f7ae54`. **Không chạy inference hoặc benchmark thực tế.**

---

## 1. Trước hết, phải so đúng thứ

| Hệ | Những nhánh cần phân biệt |
|---|---|
| **PaddleOCR** | **PP-OCRv6**: text detection/recognition; **PP-StructureV3**: document parser gồm nhiều specialist model; **PaddleOCR-VL-1.6**: layout + VLM nhận dạng nội dung |
| **MinerU** | **MinerU 4**: application và pipeline orchestration; **MinerU2.5-Pro**: model VLM 1.2B được dùng trong các đường parsing chất lượng cao |
| **Docling** | **Standard PDF pipeline**: native text + layout + OCR + table structure; **VLM pipeline**: conversion bằng model preset, sau đó đưa vào biểu diễn tài liệu |

Vì thế:

> So PP-OCRv6 với MinerU full parser là so **bộ đọc chữ** với **hệ thống tái dựng tài liệu**.  
> So PaddleOCR-VL với Docling mà không ghi Docling đang dùng pipeline/model nào cũng chưa đủ nghĩa.

Nguồn: [PaddleOCR pipelines](wiki/paddleocr-repository-pipelines.md), [MinerU 4 architecture](wiki/mineru-4-architecture.md), [Docling standard PDF pipeline](wiki/docling-standard-pdf-pipeline.md), [Docling VLM models và engines](wiki/docling-models-and-inference-engines.md).

---

## 2. Khác biệt kiến trúc thực chất

### PaddleOCR: toolkit rộng, nhiều mức can thiệp

PaddleOCR cung cấp hai lớp đáng phân biệt:

1. **Training/classic inference stack:** cấu hình transform, backbone, neck, head, loss, optimizer, postprocessing.
2. **Python pipeline wrappers:** gọi pipeline do **PaddleX** thực thi.

Ở snapshot đã đọc, wrapper OCR mặc định chọn PP-OCRv6 medium detector và recognizer nếu không chỉ định language/version. Nhưng selector của PP-StructureV3 chỉ nhận OCR v3–v5: **không phải mọi pipeline đều tự động dùng model v6 mới nhất**.

Các lựa chọn chính:

- **PP-OCRv6:** phù hợp khi đầu ra cần text, boxes và recognition scores.
- **PP-StructureV3:** dùng module riêng cho OCR, layout, table, formula, chart, seal và reading order.
- **PaddleOCR-VL-1.6:** PP-DocLayoutV3 phân vùng và xác định thứ tự, rồi VLM 0.9B nhận dạng crop.

**Hệ quả thực dụng — suy luận:** PaddleOCR phù hợp với đội muốn kiểm soát và tối ưu từng thành phần, hoặc cần tự train OCR cho domain riêng. Đổi lại, phải phân biệt rõ trách nhiệm giữa wrapper, PaddleX, model và inference backend.

Nguồn: [Pipelines](wiki/paddleocr-repository-pipelines.md), [training architecture](wiki/paddleocr-model-training-architecture.md), [PP-StructureV3](wiki/pp-structurev3.md), [VL-1.6](wiki/paddleocr-vl-1.6.md).

### MinerU 4: application có nhiều đường xử lý

MinerU 4 cung cấp bốn tier:

| Tier | Đường xử lý khái quát |
|---|---|
| `flash` | PDF có native text có thể đi đường không khởi tạo model; scan vẫn cần OCR |
| `basic` | Chuỗi specialist model |
| `standard` | Thêm VLM cho parsing chất lượng cao |
| `advanced` | Mức effort cao hơn; không nên tự đồng nhất với việc dùng model lớn hơn |

MinerU tách:

- **DocVortex:** native parsing, PDF classification/access, deterministic postprocessing và rendering.
- **MinerU:** inference, orchestration và các bước enhancement tùy chọn.

Một phát hiện quan trọng trong registry:

- Layout: **PP-DocLayoutV2**.
- OCR: **PP-OCRv6 Tiny detector + Small recognizer**.
- Formula: **PP-FormulaNet plus-M**.
- Tables: **SLANet Plus** và các table assets.
- VLM: **MinerU2.5-Pro-2605-1.2B**.

**MinerU không hoàn toàn là đối thủ độc lập với PaddleOCR về model: nó dùng nhiều thành phần của Paddle.** Giá trị khác biệt nằm thêm ở routing, kết hợp native text với inference, postprocessing và workflow tài liệu.

Nguồn: [MinerU 4 architecture](wiki/mineru-4-architecture.md), [OCR pipeline](wiki/mineru-4-ocr-pipeline.md), [models và engines](wiki/mineru-4-models-and-engines.md).

### Docling: lấy document representation làm trung tâm

Standard PDF pipeline hiện được nối theo thứ tự:

```text
preprocessing
→ layout
→ OCR
→ layout postprocessing
→ table structure
→ optional form fields
→ page assembly
→ document reading order / optional heading hierarchy
```

Điểm đáng chú ý:

- Có **PDF-aware selective OCR**, không bắt buộc OCR lại toàn bộ mọi trang.
- Khi merge ở chế độ này, native PDF text được ưu tiên hơn OCR chồng lấn.
- Kết quả đưa vào **DoclingDocument**, không chỉ là một chuỗi Markdown.
- VLM pipeline là một nhánh khác; **Granite Docling không phải model mặc định của standard PDF pipeline**.

Docling còn có thể dùng PP-OCR qua RapidOCR và có đường conversion MinerU2 hai bước. Vì vậy, cũng không nên xem “Docling accuracy” là một hằng số độc lập với cấu hình.

Nguồn: [Standard PDF pipeline](wiki/docling-standard-pdf-pipeline.md), [document representation](wiki/docling-document-representation.md), [OCR engines](wiki/docling-ocr-engines.md), [VLM engines](wiki/docling-models-and-inference-engines.md).

---

## 3. Chất lượng parsing: bằng chứng nói gì?

### 3.1. PaddleOCR-VL-1.6 vs MinerU2.5-Pro

Trong **cùng bảng OmniDocBench v1.6 của báo cáo PaddleOCR-VL-1.6**:

| Metric | PaddleOCR-VL-1.6 | MinerU2.5-Pro |
|---|---:|---:|
| Parameters được ghi | 0.9B | 1.2B |
| Overall ↑ | **96.33** | 95.75 |
| Text edit distance ↓ | **0.033** | 0.036 |
| Formula CDM ↑ | **97.49** | 97.45 |
| Table TEDS ↑ | **94.76** | 93.42 |
| Table TEDS-S ↑ | **97.11** | 95.92 |
| Reading-order edit distance ↓ | 0.127 | **0.120** |

**Đọc đúng kết quả:**

- PaddleOCR-VL-1.6 dẫn overall, text, formula và table trong bảng này.
- MinerU-Pro có reading-order edit thấp hơn.
- Không có bên thắng mọi metric.
- “96.33 overall” **không có nghĩa 96.33% ký tự được đọc đúng**.

**Giới hạn:** đây là số report công bố, được report dẫn từ leaderboard; mình không tái chạy hoặc kiểm leaderboard độc lập. Dòng MinerU-Pro không ghi rõ checkpoint/revision.

Nguồn raw: [báo cáo VL-1.6](raw/2606.03264_PaddleOCR-VL-1.6/main.tex), §Experiments → Document Parsing, bảng `tab:omni16_full_performance`.

### 3.2. Có discrepancy, không nên trộn nguồn

[Model card MinerU2.5-Pro-2605](raw/MinerU2.5-Pro-2605-1.2B.md), bảng **OmniDocBench v1.6_full**, ghi:

- Overall **95.72**, không phải 95.75.
- Formula CDM **97.15**, không phải 97.45.
- Table TEDS **93.62**.
- Reading-order edit **0.123**.

Chưa đủ thông tin để xác định chênh lệch đến từ revision, evaluation setup hay yếu tố nào khác. Vì thế **không nên lấy số tốt nhất từ mỗi nguồn rồi tạo thành một leaderboard tổng hợp**.

### 3.3. Với ảnh chụp cong/nghiêng, PaddleOCR-VL có tín hiệu đáng chú ý

Trong bảng Real5-OmniDocBench của cùng report:

| Model | Overall ↑ | Skew ↑ |
|---|---:|---:|
| PaddleOCR-VL-1.6 | **93.19** | **92.66** |
| MinerU2.5-pro | 88.96 | 81.26 |
| PP-StructureV3 | 64.45 | 37.98 |

**Suy luận lựa chọn:** nếu corpus nhiều ảnh chụp, biến dạng, nghiêng, nên đưa **PaddleOCR-VL-1.6 vào nhóm thử nghiệm đầu tiên**, thay vì mặc định dùng PP-StructureV3 chỉ vì cùng tên PaddleOCR.

Nhưng đây không phải kết quả của toàn bộ MinerU 4, và không tự chuyển thành kết luận tương tự trên tài liệu tiếng Việt.

Nguồn: [report](raw/2606.03264_PaddleOCR-VL-1.6/main.tex), bảng `tab:real5-omnidocbench-performance`.

### 3.4. Còn Docling?

**Không có cấu hình Docling tương ứng trong hai bảng trên.**

Do đó, bằng chứng vừa đọc **không đủ để kết luận “Paddle > MinerU > Docling” về accuracy**. Muốn đánh giá Docling cần ghi rõ:

- Standard hay VLM pipeline?
- OCR engine/model nào?
- Native text hay force OCR?
- Layout/table model nào?
- Export nào?

Các trang so sánh cũ trong wiki có khuyến nghị sử dụng, nhưng chính chúng cũng ghi rõ chưa phải controlled benchmark. Mình không dùng chúng làm bằng chứng cho một thứ hạng tuyệt đối.

---

## 4. Output, bảng biểu và RAG: khác biệt lớn không nằm ở chữ OCR

| Tiêu chí | PaddleOCR | MinerU 4 | Docling |
|---|---|---|---|
| Trọng tâm output | OCR/document parsing results | Structured document + render targets + page/block locators | Typed document IR |
| Điều khiển chi tiết | Nhiều module/model/config | Tier + runtime + parsing options | Backend/pipeline/model/plugin/serializer |
| Workflow đáng chú ý | Train và deploy OCR/document-AI components | Parse, library, cache, search, đọc tiếp | Convert, giữ cấu trúc, serialize, chunk |
| Chunking có cấu trúc | Cần thiết kế theo result và downstream | Có thể xây trên structured result | Có native chunkers được tài liệu hóa |

Nguồn: [Paddle pipelines](wiki/paddleocr-repository-pipelines.md), [MinerU architecture](wiki/mineru-4-architecture.md), [Docling IR](wiki/docling-document-representation.md), [Docling chunking](wiki/docling-native-chunking.md).

### Vì sao Docling đáng cân nhắc cho RAG?

`DoclingDocument` giữ:

- Typed text/table/picture items.
- Body và furniture trees.
- Heading/group structure.
- Reading order.
- Bounding boxes và provenance khi có.

Native chunkers có thể dùng chính cấu trúc này:

- **HierarchicalChunker:** chunk theo document elements, headings, captions.
- **HybridChunker:** thêm token-aware split/merge.
- Với bảng trải qua nhiều chunks, có thể lặp header.

**Suy luận:** nếu cần citation, heading context và token budget, Docling cho một nền tảng downstream rõ hơn cách “xuất Markdown rồi chunk theo số ký tự”. Điều đó **không tự chứng minh retrieval accuracy cao hơn**; vẫn cần đánh giá RAG end-to-end.

### Bảng parse đúng vẫn có thể hỏng khi export

Theo [Docling serialization](wiki/docling-serialization.md):

- JSON giữ cell-span metadata.
- HTML biểu diễn `rowspan`/`colspan`.
- Markdown flatten merged cells.
- LaTeX serializer được tài liệu mô tả cũng chưa phát `multirow`/`multicolumn`.

**Khuyến nghị:** bảng tài chính, merged headers hoặc dữ liệu cần kiểm toán nên giữ **JSON/HTML**, không chỉ Markdown.

Về PaddleOCR, README nói **PP-StructureV3 có text/table-cell coordinates chi tiết hơn VL series**. Nếu ứng dụng cần highlight từng cell trên trang gốc, đây là tiêu chí riêng cần test, không thể thay bằng overall parsing score.

### Cross-page table: đừng đánh dấu “có” quá sớm

- **PaddleOCR:** code có `restructure_pages(..., merge_tables=True, relevel_titles=True)`, nhưng implementation được delegate cho PaddleX; chưa kiểm độ đúng.
- **MinerU-Pro:** card vừa claim cross-page merging, vừa ghi “Currently under integration”.
- **Docling:** việc chunker lặp header **không phải** bằng chứng reconstruct bảng qua page boundary.

Nguồn: [Paddle pipeline API](wiki/paddleocr-repository-pipelines.md#output-and-cross-page-api), [MinerU-Pro contradictions](wiki/mineru2-5-pro.md#contradictions), [Docling chunking](wiki/docling-native-chunking.md).

---

## 5. Triển khai và tốc độ

### PaddleOCR

Có nhiều lớp runtime:

- Paddle/static/dynamic, Transformers, ONNX Runtime.
- High-performance inference.
- VL recognition backend riêng: native hoặc vLLM/SGLang/FastDeploy/MLX/llama.cpp servers.

Điểm cần lưu ý: **recognition server không thay thế toàn bộ layout-plus-recognition pipeline**, và có tên backend trong selector không bảo đảm mọi model/hardware combination đều hoạt động.

### MinerU 4

Tách lựa chọn:

1. Small models: ONNX hoặc Torch.
2. VLM: llama.cpp, vLLM, LMDeploy, explicit MLX hoặc server.

Do có llama.cpp path, **không được tái dùng kết luận “MinerU VLM không hỗ trợ CPU” từ README 3.x cho MinerU 4**. Nhưng CPU có đường chạy không đồng nghĩa đạt throughput đủ dùng.

### Docling

- OCR engines thay thế được.
- VLM có Transformers, MLX và vLLM theo điều kiện.
- Auto-inline không đơn giản là “có CUDA thì luôn chọn vLLM”.

Nguồn: [Paddle engines](wiki/paddleocr-inference-engines.md), [MinerU engines](wiki/mineru-4-models-and-engines.md), [Docling engines](wiki/docling-models-and-inference-engines.md).

### Có thể kết luận ai nhanh nhất không?

**Chưa.**

Ví dụ:

- PP-OCRv6 Tiny được report ở **0.20 s/image** trên Xeon/OpenVINO.
- MinerU-Pro card nêu **2.12 fps concurrent** trên A100, thiếu workload chi tiết.

Hai số khác task, hardware và protocol; **không thể chia để lấy tỷ lệ nhanh hơn**.

Với bài toán thực tế, nên đo:

- End-to-end pages/s, p50/p95 latency.
- PDF rendering, inference, postprocessing, export.
- Peak RAM/VRAM.
- Retry và manual-review rate.

Nguồn: [PP-OCRv6](wiki/pp-ocrv6.md), [MinerU-Pro](wiki/mineru2-5-pro.md).

---

## 6. Failure modes, privacy và license

### Docling: “conversion success” chưa chứng minh OCR đã chạy

Code auto OCR có trường hợp:

- Không tìm thấy engine phù hợp.
- Warning rồi pass-through thay vì raise, nếu không gặp language rejection.

Vì vậy, cần kiểm tra text coverage và engine thực sự được chọn. Confidence grades có ích cho review routing, nhưng tài liệu confidence vẫn ghi **`table_score` chưa implement**; confidence không phải bảo đảm nội dung đúng.

Nguồn: [Standard PDF pipeline](wiki/docling-standard-pdf-pipeline.md), [confidence grades](wiki/docling-confidence-grades.md).

### “Local” không đồng nghĩa “không có network”

- MinerU: remote VLM có thể nhận page images; optional LLM enhancement là một ranh giới dữ liệu khác; có telemetry code được ghi nhận trong wiki.
- Docling: remote OCR/VLM cần opt-in, nhưng model downloads và source URL fetching là đường network riêng; KServe gRPC TLS mặc định off trong snapshot.
- Với cả ba, dữ liệu nhạy cảm cần pin artifacts/config và kiểm egress thực tế.

**Chưa có network audit đủ để xếp hạng privacy tuyệt đối.**

Nguồn: [MinerU engines](wiki/mineru-4-models-and-engines.md), [Docling standard pipeline](wiki/docling-standard-pdf-pipeline.md), [Docling VLM engines](wiki/docling-models-and-inference-engines.md).

### License: MinerU cần đọc kỹ hơn

| Phần mềm | Văn bản license đã đọc |
|---|---|
| PaddleOCR code | Apache-2.0 |
| Docling code | MIT; model licenses cần kiểm riêng |
| MinerU application | Apache-2.0 **kèm điều khoản bổ sung** |

[License MinerU](raw/MinerU/LICENSE.md), §§1–4, quy định:

- Cần commercial license nếu, tính gộp với affiliates, **MAU vượt 100 triệu** **hoặc** **doanh thu tháng vượt 20 triệu USD**.
- Online service cho bên thứ ba phải attribution MinerU rõ và nổi bật.
- Vi phạm nghĩa vụ áp dụng có thể dẫn tới automatic termination.

**Không có nghĩa MinerU cấm commercial**, nhưng cũng không nên gọi nó là Apache-2.0 nguyên bản. Model card MinerU-Pro khai báo Apache-2.0 không thay thế license application/dependencies. Đây là đọc văn bản, không phải tư vấn pháp lý.

---

## 7. Với tài liệu tiếng Việt

Bằng chứng đã đọc **chưa có controlled comparison đầy đủ cả ba cấu hình hiện tại trên cùng corpus tiếng Việt**.

Một nhánh đáng thử là [SenOCR-Vi](wiki/senocr-vi.md), fine-tune decoder của PaddleOCR-VL-1.6:

- Card báo Vietnamese composite **82.83**.
- Base PaddleOCR-VL-1.6 được dẫn ở **80.90**.

Nhưng hai số có khác biệt aggregation: SenOCR dùng corrected page re-aggregation, base lấy leaderboard. **Không nên coi +1.93 là kết quả cùng một rerun kiểm soát.**

Với tiếng Việt, nên test riêng:

- Dấu thanh và dấu phụ.
- Font nhỏ, scan nhòe.
- Bảng nhiều dòng và merged cells.
- Tài liệu Việt–Anh.
- Ảnh chụp cong, bóng đổ.
- Omission và reading order, không chỉ ký tự đọc sai.

**Số lượng ngôn ngữ được hỗ trợ không thay thế được accuracy tiếng Việt.**

---

## 8. Mình sẽ chọn thế nào?

Đây là **khuyến nghị thử nghiệm**, không phải thứ hạng đã đo:

| Nhu cầu chính | Thử trước |
|---|---|
| OCR text/boxes, scene/industrial text, CPU/edge | **PaddleOCR PP-OCRv6** |
| Tự train hoặc fine-tune detector/recognizer | **PaddleOCR** |
| Ảnh chụp cong/nghiêng, seal, document parsing dùng VLM | **PaddleOCR-VL-1.6**, đối chiếu MinerU-Pro |
| PDF/papers/books → structured content, local library và agent reading | **MinerU 4 standard**, thử advanced cho hard cases |
| Multi-format ingestion → IR → metadata/chunking/RAG | **Docling** |
| Bảng phức tạp cần giữ merged-cell semantics | Test cả ba, đánh giá **structured output/HTML**, không chỉ Markdown |
| Corpus tiếng Việt | Test cùng dữ liệu cả ba; thêm SenOCR như một nhánh Paddle nếu phù hợp |

### Nếu phải chọn một điểm xuất phát

- **Xây OCR service chuyên dụng:** bắt đầu bằng **PaddleOCR**.
- **Xây công cụ đọc/chuyển đổi tài liệu cho người dùng hoặc agent:** bắt đầu bằng **MinerU 4**.
- **Xây ingestion backbone cho RAG có provenance và chunking:** bắt đầu bằng **Docling**.

Trong production, mình nghiêng về thiết kế **native/selective fast path → quality checks → parser/VLM đắt hơn cho failure cases**, nhưng chỉ áp dụng sau khi đo trên corpus thật; chưa có measurement ở đây chứng minh routing đó tiết kiệm.

---

Đã lưu bản tổng hợp cùng provenance và các discrepancy tại **[wiki/paddleocr-mineru-docling-comparison.md](wiki/paddleocr-mineru-docling-comparison.md)**, đồng thời cập nhật các concept bị ảnh hưởng. Kiểm tra cấu trúc wiki, citation join, source paths và index metadata đều qua. **Các kết quả accuracy/tốc độ vẫn là nguồn công bố, chưa được tái lập trong phiên này.**