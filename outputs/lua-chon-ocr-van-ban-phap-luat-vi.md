# Lựa chọn hướng OCR cho văn bản pháp luật và hành chính tiếng Việt

## Kết luận lựa chọn

**Đề xuất kiến trúc: native-text-first → layout/structure reconstruction → OCR chọn lọc → kiểm tra nghiệp vụ và đối chiếu nguồn.** Với trang scan, ưu tiên thử **layout-first modular**, cụ thể **PaddleOCR-VL-1.6 + SenOCR-Vi**, đối chiếu với **PaddleOCR-VL-1.6 base** và **MonkeyOCRv2-B-Parsing**. Với PDF có text layer, không mặc định OCR lại: thử **Docling standard PDF pipeline** làm đường chuyển đổi có cấu trúc. **MinerU 4 standard** là ứng viên thay thế toàn parser để benchmark, không phải một bước bắt buộc chạy sau Docling.

Đây là **Synthesis — khuyến nghị kỹ thuật**, chưa phải quyết định model thắng benchmark nội bộ. Chưa biết phần cứng, số trang/ngày và yêu cầu đầu ra cuối; vì vậy chọn được kiến trúc và vòng thử đầu, chưa thể cam kết latency/VRAM hoặc chốt checkpoint production.

**Điều chỉnh so với các báo cáo OCR tiếng Việt tổng quát:** không xếp một model duy nhất đứng đầu cho mọi đầu vào. Mẫu thực tế có cả scan, PDF có chữ và bảng dài qua trang; mỗi loại có nút thắt khác nhau.

## 1. Phạm vi bằng chứng

Đã đọc bốn báo cáo do người dùng chỉ định:

1. [PaddleOCR vs MinerU vs Docling](paddleocr-mineru-docling-comparison.md).
2. [So sánh model end-to-end và lựa chọn cho tiếng Việt](so-sanh-cac-model-end-to-end-generative-ocr-vi.md).
3. [Tổng quan các hướng OCR](tong-quan-cac-huong-ocr.md).
4. [So sánh model layout-first cho tiếng Việt](so-sanh-cac-model-ocr-theo-huong-layout-first-modular-vi.md).

Đã đối chiếu các concept liên quan, đặc biệt [so sánh ba hệ thống](../wiki/paddleocr-mineru-docling-comparison.md), [SenOCR](../wiki/senocr-vi.md), [MonkeyOCRv2](../wiki/monkeyocrv2.md), [Docling PDF pipeline](../wiki/docling-standard-pdf-pipeline.md), [serialization](../wiki/docling-serialization.md), [chunking](../wiki/docling-native-chunking.md), [MDPBench](../wiki/mdpbench.md), [PP-OCRv6](../wiki/pp-ocrv6.md), [OvisOCR3](../wiki/ovisocr3.md) và [Chandra OCR 2](../wiki/chandra-ocr-2.md).

**Observed / Reproduced trong phiên:** chạy `pdfinfo`, `pdftotext -layout`, xem danh sách image objects bằng `pdfimages -list`; render đủ 35 trang bằng Poppler, xem contact sheets toàn bộ và ảnh chi tiết ở các trang tiêu biểu. Đây là kiểm tra PDF và text extraction, **không phải chạy OCR hoặc benchmark model**. Việc xem contact sheets không tương đương đối chiếu thủ công mọi ký tự của 35 trang.

Không mở lại `raw/`, không truy cập web, không tải model và không gửi tài liệu tới API. Báo cáo này là tư vấn thử nghiệm trong `outputs/`, chưa đưa thành kiến thức canonical trong wiki; không sửa `examples/`, wiki hoặc log.

## 2. Ba mẫu thực tế nói gì?

Các số trang bên dưới là **thứ tự trang PDF, bắt đầu từ 1**, không phải số trang in trên tài liệu.


| Mẫu                                                                              | Kết quả kiểm tra trực tiếp                                                                                                                                  | Rủi ro cần xử lý                                                                                                        | Đường đề xuất                                                                                          |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| [A —](./examples/0a50d77d-fb3a-44c8-b862-ca66282437eb__sub_file.pdf) `0a50d77d…` | 10 trang A4 dọc; `pdftotext -layout` trả 0 ký tự không phải khoảng trắng trên cả 10 trang. Trang 1–9 có nội dung; trang 10 gần trắng, có dấu mờ             | Chữ Việt có dấu, heading đậm/nghiêng, phân cấp I/II → 1/2 → a/b; đoạn nối trang; khối nơi nhận và ký đóng dấu ở trang 9 | OCR ảnh trang với layout-first; giữ ảnh trang 10 thay vì tự loại là trang trắng                        |
| [B —](./examples/0fab3ae3-dee0-41f3-8f2a-56920f46f771__sub_file.pdf) `0fab3ae3…` | Quyết định 2 trang A4 dọc; trích xuất được 1.475 và 1.511 ký tự không phải khoảng trắng; có Điều 1–3, số hiệu, ngày và ảnh ký/dấu                           | Bố cục đầu trang hai khối; Điều 1 nối từ trang 1 sang 2; nơi nhận và người ký song song                                 | Native text + tọa độ + layout; OCR vùng ảnh chỉ khi có yêu cầu đọc nội dung trong vùng đó              |
| [C —](./examples/1b80c6d8-6a44-4bfc-a659-8c77cff4c598__sub_file.pdf) `1b80c6d8…` | Phụ lục 23 trang A4 ngang; cả 23 trang trích xuất được chữ, khoảng 402–1.666 ký tự không phải khoảng trắng/trang; bảng 5 cột ở phần đầu và 9 cột từ phần II | Header lặp, ô dài, hàng nối trang, ô trống, footnote nhỏ màu xanh trang 14, dấu chồng vùng tiêu đề trang 1              | Native text + table geometry/structure; giữ cell/span và provenance, thêm bước nối bảng/hàng qua trang |




### 2.1. Những chi tiết ảnh hưởng trực tiếp đến lựa chọn

- **Mẫu A không phù hợp đường native-only.** Kết quả extraction rỗng cùng hình render và image objects cho thấy phải xử lý phần nội dung nhìn thấy dưới dạng ảnh; không suy từ đó rằng cả corpus đều là scan.
- **Mẫu B không nên OCR lại chỉ vì có dấu và chữ ký.** Phần nội dung chính đã có chữ trích xuất được. Tuy nhiên số ký tự và việc không có replacement character chưa chứng minh text layer đúng toàn bộ.
- **Mẫu C chủ yếu là bài toán dựng lại bảng, không chỉ OCR.** Ví dụ trang 3 mở đầu bằng đoạn tiếp tục ở cột “Mô tả”, trong khi các cột bên trái của dòng đó trống. Trang 14 mở đầu bằng phần tiếp tục của kết quả thực hiện, rồi mới đến hàng STT 5; nội dung hàng 5 tiếp tục sang trang 15. Không thể coi mọi hàng đầu trang là một nhiệm vụ mới.
- `pdftotext -layout` của mẫu C xuất hiện chuỗi như `1quyết`, `3định` và `1115.` ở các vị trí sát cột. Đây là **dấu hiệu extraction cần kiểm tra vị trí/visibility**, chưa xác định nguyên nhân; không được tự xóa chữ số bằng regex toàn cục hoặc quy hết cho lỗi OCR.
- **Footnote là nội dung nghiệp vụ:** trang 14 mẫu C có các chú thích giải thích số liệu. Không áp dụng quy tắc “xóa footer” cho mọi phần nằm gần đáy trang.
- **Thiếu tài liệu không phải lỗi OCR:** mẫu B dẫn Phụ lục I–VI nhưng file được cung cấp chỉ có 2 trang quyết định. Phải ghi nhận phần được dẫn chưa có trong file, không yêu cầu model tự tạo. Mẫu C có tiêu đề gắn với một báo cáo khác; không tự ghép nó thành phụ lục của mẫu B.
- Các mẫu gồm thông báo, quyết định và phụ lục báo cáo, không chỉ luật/nghị định. Vì vậy schema phải hỗ trợ cả cấu trúc Điều–Khoản–Điểm lẫn Mục–Tiểu mục–Nhiệm vụ.

Nguồn các quan sát: mẫu A trang 1, 3, 9, 10; mẫu B trang 1–2; mẫu C trang 1–4, 11, 14–15, kết hợp text extraction toàn bộ hai file có chữ.

## 3. Xếp ưu tiên các hướng


| Hướng                             | Quyết định cho bài toán này                             | Lý do và giới hạn                                                                                                      |
| --------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Native text + geometry/layout     | **Đường mặc định cho B, C nếu qua kiểm tra chất lượng** | Giữ chữ đã có, tránh một lần nhận dạng không cần thiết; vẫn phải kiểm order, ký tự và cấu trúc bảng                    |
| Layout-first modular              | **Đường chính để thử cho A và vùng cần OCR**            | Có vùng/tọa độ để kiểm tra; có thể đổi recognizer tiếng Việt; phải kiểm cả vùng bị bỏ sót chứ không chỉ chữ trong crop |
| Detector → recognizer             | **Baseline nhẹ hoặc bộ đọc đối chứng**                  | Hữu ích cho text/box, CPU và kiểm tra số hiệu; cần thêm layout/table/reading order                                     |
| End-to-end generative page parser | **Challenger/fallback, chưa làm đường duy nhất**        | Có thể đơn giản hóa parsing nhưng phải đo bỏ sót, sinh thêm/lặp, truncation và grounding                               |
| OCR → KIE/LLM theo schema         | **Bước sau, tách khỏi bản chép nguồn**                  | Trích số hiệu, cơ quan, ngày, căn cứ, điều khoản; JSON hợp lệ không bảo đảm giá trị đúng                               |
| Multi-page/long-document model    | **Chưa ưu tiên làm nền tảng**                           | Mẫu dài 23 trang chủ yếu đòi hỏi nối hàng/bảng chính xác; chưa có bằng chứng cần one-shot cả tài liệu                  |


Cơ sở kiến trúc: [báo cáo tổng quan](tong-quan-cac-huong-ocr.md), [so sánh ba hệ thống](../wiki/paddleocr-mineru-docling-comparison.md). Thứ tự ưu tiên là synthesis theo mẫu, không phải kết quả đo accuracy.

## 4. Chọn toolkit và model cụ thể



### 4.1. Stack khởi đầu đề xuất

**Một router riêng, hai đường chính:**

1. **PDF có text layer dùng được:** thử **Docling standard PDF pipeline**, ưu tiên native text, bật table reconstruction khi có bảng, giữ document JSON/provenance.
2. **Trang scan hoặc vùng text layer lỗi:** thử **PaddleOCR-VL-1.6 page pipeline + SenOCR-Vi recognizer**. Luôn giữ cấu hình base để A/B test.
3. **Đầu ra cả hai đường:** chuyển về schema chung của ứng dụng; khôi phục phân cấp văn bản, nối đoạn/bảng qua trang, validation và human review.

**Không phải tích hợp có sẵn được xác nhận:** SenOCR có interface thay recognizer trong PaddleOCR-VL; không từ đó suy ra SenOCR là OCR plugin drop-in của Docling. Adapter vào schema chung là phần ứng dụng cần xây và kiểm thử. Không cần chạy toàn bộ hai parser nối tiếp trên mỗi trang.

Docling được chọn ở đây vì [selective OCR/native text policy](../wiki/docling-standard-pdf-pipeline.md#ocr-region-and-text-layer-policy), [IR/provenance](../wiki/paddleocr-mineru-docling-comparison.md#4-output-rag-bảng-và-provenance) và [serialization](../wiki/docling-serialization.md), **không phải đã chứng minh đọc tiếng Việt chính xác nhất**. Auto OCR của Docling có thể pass-through khi không có engine; vì vậy phải cấu hình rõ engine và kiểm tra chữ đầu ra, không chỉ status success.

### 4.2. Shortlist có vai trò, không phải leaderboard


| Option                           | Vai trò trong vòng thử           | Chọn khi nào?                                                  | Giới hạn phải giữ                                                                                                         |
| -------------------------------- | -------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **PaddleOCR-VL-1.6 + SenOCR-Vi** | Ứng viên scan tiếng Việt chính   | A, chữ Việt, cần crop/provenance và khả năng thay recognizer   | Chưa chứng minh tốt nhất trên văn bản pháp luật; card nêu bảng phức tạp khó; benchmark FP32                               |
| **PaddleOCR-VL-1.6 base**        | Baseline bắt buộc của SenOCR     | Giữ layout và các option chung để cô lập khác biệt recognition | Điểm benchmark chung không bảo đảm dấu, số hiệu hay mức bỏ sót trên mẫu                                                   |
| **MonkeyOCRv2-B-Parsing**        | Challenger pipeline khác         | So độ trung thực text, coverage, order với nhánh Paddle        | Điểm Vietnamese slice được dẫn lại, không phải rerun chung; 0,7B không đại diện toàn chi phí pipeline                     |
| **Docling standard**             | Native/structure baseline        | B và C; cần IR, tọa độ, JSON/HTML và downstream RAG            | Không coi converter là model; ghi rõ OCR/layout/table config; không mặc định tự nối bảng qua trang                        |
| **MinerU 4 standard**            | Challenger toàn parser           | Muốn thử hệ thống parsing có routing/output sẵn, đặc biệt C    | Pin tier/model/version; không coi MinerU2.5-Pro là toàn ứng dụng; kiểm license application                                |
| **PP-OCRv6**                     | Baseline nhẹ/đối chứng text-box  | CPU hoặc cần kiểm số hiệu, dòng chữ ở vùng cụ thể              | Xác nhận checkpoint/dictionary hỗ trợ tiếng Việt thực tế; chưa có benchmark Việt trong concept đã đọc; không tự dựng bảng |
| **OvisOCR3**                     | Vòng hai: end-to-end và nối bảng | Nếu C còn lỗi nối trang hoặc muốn đối chứng page parser        | Có quy trình parse rồi merge page-pair; chưa có điểm riêng tiếng Việt ở nguồn đã đọc; kết quả merge phải kiểm lại         |
| **Chandra OCR 2**                | Quality challenger có điều kiện  | Nếu lỗi văn bản khó còn nhiều và license phù hợp               | Weights có điều khoản thương mại; điểm 85,60 được nguồn khác dẫn lại, không phải benchmark ba mẫu                         |


Nguồn: [SenOCR](../wiki/senocr-vi.md#identity-and-interface), [MonkeyOCRv2](../wiki/monkeyocrv2.md#parsing-system-and-reported-results), [so sánh hệ thống](../wiki/paddleocr-mineru-docling-comparison.md), [PP-OCRv6](../wiki/pp-ocrv6.md), [OvisOCR3](../wiki/ovisocr3.md#cross-page-table-reconstruction), [Chandra](../wiki/chandra-ocr-2.md#licensing-and-trust-limits).

### 4.3. Những model chưa ưu tiên

- **TeleOCR, FireRed:** mở vòng thử nếu corpus bổ sung nhiều ảnh chụp cong/nghiêng. Các mẫu hiện có chưa cho thấy camera distortion là nút thắt chính.
- **LightOnOCR-3, Infinity-Parser2 Flash:** mở vòng thử nếu grounding/structured output hoặc khả năng end-to-end là yêu cầu chính; chưa có căn cứ tiếng Việt đủ trong báo cáo để thay shortlist đầu.
- **Unlimited OCR 2:** chỉ ưu tiên nếu corpus dài hơn và lỗi liên trang thực sự là nút thắt; không cần one-shot nhiều trang chỉ vì file C có 23 trang.
- **Xiaomi/Hunyuan:** nếu thử, kiểm prompt bỏ header/footer. Với tài liệu này, có thể mất số hiệu, cơ quan và metadata quan trọng.
- **PP-StructureV3:** đáng thử khi cần text/cell coordinates chi tiết, CPU/modular components hoặc tự fine-tune; không mặc định mọi module đã dùng OCRv6 chỉ vì toolkit có v6.

Đây là phân bổ ngân sách thử nghiệm, không phải kết luận các model đó kém tiếng Việt. Cơ sở là các giới hạn/đặc tính trong bốn báo cáo đã đọc, nhất là [end-to-end](so-sanh-cac-model-end-to-end-generative-ocr-vi.md) và [layout-first](so-sanh-cac-model-ocr-theo-huong-layout-first-modular-vi.md).

## 5. Option và chính sách xử lý nên chốt

Các mục dưới là **đề xuất cấu hình thử nghiệm**, không phải API đã chạy thành công trong môi trường này.


| Hạng mục            | Chính sách khởi đầu                                                                                                                                        |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Routing             | Theo trang/vùng, không chỉ theo file; text layer có chữ chưa đủ để pass                                                                                    |
| Native quality gate | Kiểm glyph lỗi, dấu Việt, vị trí, visibility/overlap, coverage so với ảnh và reading order; không dùng số ký tự làm điều kiện duy nhất                     |
| Full-page OCR       | Không force toàn corpus. Chỉ force cho scan hoặc trang có text layer hỏng sau khi giữ nguyên bằng chứng                                                    |
| Render cho OCR      | Thử 300 DPI; tăng/crop vùng chữ nhỏ ở 400 DPI khi cần. Ghi cả resize cuối/giới hạn pixel của model; DPI cao không bảo đảm model thực sự nhận thêm chi tiết |
| Tiền xử lý          | Orientation/deskew khi có lỗi; không threshold/khử màu mạnh mặc định vì có dấu đỏ và footnote màu; mọi transform có ánh xạ về trang gốc                    |
| Layout/recognition  | Nhánh SenOCR và Paddle base giữ cùng layout, crop policy, precision khi khả thi; chấm thiếu vùng riêng                                                     |
| Precision           | Nếu thử SenOCR BF16/FP16/quantization, so với FP32 reference trên tập nhỏ, không mặc định giữ chất lượng công bố                                           |
| Header/footer       | Giữ bản đầy đủ; phân loại cơ quan, số hiệu, số trang, footer lặp và footnote riêng; chỉ loại furniture khỏi bản phục vụ tìm kiếm khi có căn cứ             |
| Bảng                | Canonical JSON cell/span + HTML; Markdown là view phụ. Bảng mẫu C có cột trống vẫn phải giữ                                                                |
| Nối trang           | Giữ fragment gốc; chỉ tạo logical row/table khi có bằng chứng continuation, schema/header và vị trí; lưu trạng thái chưa chắc chắn                         |
| Đoạn/điều nối trang | Ví dụ Điều 1 mẫu B nối sang trang 2; nối logical content nhưng giữ hai nguồn trang                                                                         |
| Ký/dấu              | Giữ crop và tọa độ nếu cần; không suy tính hợp lệ của chữ ký hoặc tính xác thực văn bản từ OCR                                                             |
| LLM hậu xử lý       | Không tự sửa chính tả/số hiệu/ngày/số tiền vào bản chép gốc; đề xuất sửa là một lớp riêng có diff, evidence và review                                      |
| LLM enhancement     | Tắt ở baseline để tách khả năng transcription khỏi rewrite; chỉ mở trong thí nghiệm riêng                                                                  |
| Offline/privacy     | Chạy local mặc định cho dữ liệu chưa rõ quyền công bố; pin artifacts, kiểm egress và telemetry; không đồng nhất local inference với air-gap                |


Về bảng: [Docling serialization](../wiki/docling-serialization.md#table-span-fidelity-by-target) ghi Markdown flatten span, JSON giữ metadata và HTML dùng rowspan/colspan. Việc [chunker lặp header](../wiki/docling-native-chunking.md#built-in-strategies) không chứng minh nó nối được bảng qua page boundary.

## 6. Đầu ra cần giữ cho ứng dụng pháp luật

**Schema đề xuất, không phải output có sẵn của mọi model:**

- Document: `document_id`, file hash, loại văn bản, số hiệu nguyên văn, cơ quan, ngày ban hành nguyên văn và giá trị normalized riêng, tiêu đề, phạm vi nguồn đã có/thiếu.
- Page/block: PDF page index, số trang in nếu đọc được, bbox/polygon, đơn vị tọa độ và orientation, block type, `raw_text`, text chuẩn hóa, engine/model/revision/config.
- Hierarchy: Phần/Chương/Mục/Điều/Khoản/Điểm nếu có; hỗ trợ I/II, mục đánh số và nhiệm vụ. Giữ ancestor context khi chunking.
- Table: table/row/cell IDs, row/column indices, spans, header role, fragment text và provenance từng fragment, logical continuation links, footnote references.
- Quality: engine confidence nếu có, rule flags, disagreement, truncation/invalid-output status, review status; không quy mọi engine score về cùng thang xác suất.
- Derived fields: giá trị trích xuất, evidence block/cell IDs, phương pháp và trạng thái được người xác nhận.

**Hai lớp tách biệt:** (1) bản chép trung thực và cấu trúc nhìn thấy; (2) trích xuất/diễn giải như quan hệ “thay thế”, thời hạn hoặc hiệu lực. OCR có thể ghi lại câu “có hiệu lực kể từ ngày ký”; nó không tự xác minh tình trạng hiệu lực hiện tại hay những văn bản ban hành sau đó.

Nếu làm RAG, chunk theo đơn vị nội dung pháp lý và hierarchy đã xác nhận, không chỉ số token. `HybridChunker` là công cụ token-aware hữu ích, nhưng không mặc định hiểu đúng Điều–Khoản–Điểm. Với bảng, không tách “kết quả” khỏi nhiệm vụ/cơ quan/thời hạn mà không mang theo context hàng và nguồn trang.

## 7. Benchmark để chốt: ít cấu hình nhưng đúng mục tiêu



### Vòng 0 — bộ regression từ 35 trang hiện có

Dùng cả 35 trang để kiểm completion/failure và phân loại. Annotate kỹ các ca sau:


| Ca bắt buộc         | Điều phải kiểm                                                                   |
| ------------------- | -------------------------------------------------------------------------------- |
| A trang 1           | Cơ quan, số hiệu, ngày, title và body không bị lẫn                               |
| A trang 3           | Heading số, a/b/c/d, chữ Việt đậm/nghiêng; đoạn nối trang                        |
| A trang 9           | Hai khối nơi nhận/ký; không lẫn thứ tự hoặc đưa nét ký thành chữ body            |
| A trang 10          | Gần trắng nhưng có dấu mờ; không sinh thêm đoạn văn và không âm thầm mất trang   |
| B trang 1–2         | Trích native, Điều 1 nối trang, số hiệu và ngày; metadata vùng đầu trang vẫn còn |
| C trang 1–4         | Bảng nhỏ và bảng 5 cột; header lặp; continuation ở trang 3 và 4                  |
| C trang 11–13       | Đổi schema sang bảng 9 cột; không nối với bảng trước chỉ vì cùng file            |
| C trang 14–15       | Footnote, ký hiệu tham chiếu, số liệu và hàng STT 5 nối trang                    |
| C các trang còn lại | Không bỏ cột trống, không duplicate header thành data, coverage và continuation  |


**Không dùng text layer làm ground truth tuyệt đối.** Native text có thể hỗ trợ annotation nhưng phải đối chiếu render, nhất là các chuỗi lẫn sát cột đã quan sát.

### Vòng 1 — shortlist vận hành

- **Track native/structure B+C:** Docling standard và MinerU 4 standard, đối chiếu baseline native extraction có tọa độ. Ghi trang/vùng thực sự đi qua OCR. Không coi baseline `pdftotext` là một parser bảng hoàn chỉnh.
- **Track scan A:** PaddleOCR-VL base, cùng pipeline + SenOCR, MonkeyOCRv2-B-Parsing. Nếu CPU là ràng buộc, thêm PP-OCRv6 với cấu hình tiếng Việt đã xác nhận và layout/reassembly tối thiểu.
- **Track diagnostic riêng:** render B/C để đo OCR ảnh nếu muốn đánh giá model; không trộn kết quả này với native-first end-to-end, vì đó là hai phép thử khác nhau.
- **Vòng 2:** chỉ thêm OvisOCR3 cho cross-page/end-to-end, hoặc Chandra nếu license phù hợp, khi chúng có loại lỗi cụ thể để giải quyết.



### Chấm theo lỗi có ý nghĩa

1. **Text fidelity:** CER/WER có dấu, Unicode NFC và quy tắc whitespace cố định; báo thêm omission, addition, repetition. Không bỏ dấu khi tính điểm chính.
2. **Critical fields:** exact match số hiệu, ngày, điều/khoản/điểm, cơ quan, số tiền/tỷ lệ và tham chiếu văn bản. Kiểm riêng từ phủ định, hạn định vì có thể đổi nghĩa dù chỉ sai một từ.
3. **Structure:** heading/parent assignment, reading order, boundary/coverage của Điều–Khoản–Điểm hoặc nhiệm vụ.
4. **Tables:** cell text, row/column assignment, spans, ô trống, continuation precision/recall và footnote linkage. TEDS là một chỉ báo, không thay kiểm đúng quan hệ nhiệm vụ–cơ quan–thời hạn–kết quả.
5. **Provenance:** tỷ lệ block/field/cell truy về đúng trang/vùng; crop highlight có khớp hay không.
6. **Operations:** p50/p95 end-to-end, pages/s, RAM/VRAM, retry, truncation/invalid output, tỷ lệ review và thời gian sửa tay. Tính cả render/layout/export, không chỉ decode.

Ngưỡng production cần thống nhất theo mục đích sử dụng. Trong bộ regression hiện tại, đặt mục tiêu không có critical error bị âm thầm chấp nhận; trường hợp chưa chắc phải review. **Zero error trên 35 trang không chứng minh zero error production.** Sau sàng lọc cần corpus khác, đa nguồn và giữ riêng holdout theo tài liệu, tránh để hai nửa của cùng một hàng nối trang rơi vào train/tuning và test.

Bất đồng giữa hai engine là tín hiệu review, không phải biểu quyết chân lý. SenOCR và Paddle base cùng họ nên mức độc lập hạn chế; dùng Monkey/engine khác cho đối chứng có thể hữu ích, nhưng vẫn không loại được lỗi chung.

## 8. Cách quyết định sau benchmark

- Nếu SenOCR giảm lỗi tiếng Việt/critical fields có ý nghĩa mà không tăng omission/table errors và chi phí hợp lý: chọn làm recognizer chính cho scan.
- Nếu base hoặc Monkey tốt hơn trên holdout: dùng kết quả đó, không giữ SenOCR chỉ vì nhãn “chuyên Việt”.
- Nếu native+Docling giữ B/C tốt: giữ fast path, không thêm VLM vào mọi trang.
- Nếu MinerU cho kết quả bảng/provenance và vận hành tốt hơn: có thể chọn thay Docling/native parser path; không cần duy trì cả hai trong production nếu không có lợi ích đo được.
- Nếu chỉ còn lỗi continuation: thêm module nối fragment/rule/human review trước khi thay toàn OCR bằng model long-document.
- Nếu cần CPU-only: ưu tiên native geometry + OCR nhẹ đã kiểm tiếng Việt, đo chi phí review; gửi vùng khó sang worker GPU nội bộ khi có hạ tầng, không mặc định CPU đạt SLA.



## 9. Giới hạn và mức tin cậy

- Các điểm tiếng Việt **Chandra 85,60 / Monkey 83,20 / SenOCR 82,83 / Paddle base 80,90** được lưu trong [SenOCR](../wiki/senocr-vi.md#reported-evaluation), nhưng SenOCR dùng corrected re-aggregation, các dòng khác dẫn leaderboard. Không phải controlled rerun chung, không phải accuracy pháp luật.
- [MDPBench](../wiki/mdpbench.md#evaluation-protocol-and-reported-results) bỏ qua header/footer/page number/page footnote khi chấm. Vì vậy điểm cao chưa giải quyết yêu cầu giữ metadata và footnote ở các mẫu này.
- Các concept model/pipeline chính đã đọc phần lớn là `draft`; nhiều giới hạn về code/weights/prompts và việc chưa tái lập benchmark được ghi ngay trong các trang đó.
- Chưa có inference hoặc số đo chất lượng/tốc độ nào của các ứng viên trên ba PDF. Không thể khẳng định một model thắng corpus này, mức VRAM cần thiết hay phần trăm tiết kiệm nhờ routing.
- Kiểm tra cấu trúc wiki trong phiên trả `OK: 112 concept(s), 1 index file(s)`; kết quả này chỉ xác nhận các mục checker bao phủ, không xác minh OCR hoặc mọi semantics của wiki.

**Chốt đề xuất:** bắt đầu bằng **native-first cho PDF có chữ + Docling để thử structure**, **PaddleOCR-VL-1.6/SenOCR cho scan**, **Monkey làm challenger**, **MinerU làm đối chứng toàn parser**. Đầu tư ngang mức vào **bảng nối trang, hierarchy, provenance và review** thay vì chỉ chọn model có overall benchmark cao nhất.