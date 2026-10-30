Có thêm một khác biệt phiên bản đáng lưu ý: Docling đang cài là `2.90.0`, chưa có parser `DOTS_JSON`; snapshot trong `references/docling` đã có. Ngay cả parser mới cũng nhận bbox theo pixel, còn Monkey trả tọa độ chuẩn hóa 0–1000, nên không thể nối thẳng chỉ vì output đều trông giống JSON.
**Bạn đúng về hướng kiến trúc: hoàn toàn có thể tận dụng pipeline có sẵn và tích hợp MonkeyOCRv2-B-Parsing. Nhưng “chỉ thay model” chỉ đúng khi model mới tương thích với hợp đồng của component cũ — Monkey chưa tương thích trực tiếp như vậy.**

Sau khi đọc [issue #1](https://github.com/hiennguyen9874/legal-vi-ocr/issues/1), tài liệu và code liên quan, mình đánh giá: **giữ PyMuPDF + Monkey độc lập là baseline hợp lý, nhưng chưa đủ bằng chứng để kết luận tốt hơn các phương án tích hợp.** Câu “chưa có lý do nhúng model” trong issue nên hiểu là *chưa xác định lợi ích cần kiểm chứng*, không phải *không tích hợp được*.

## 1. Trước hết: không phải Monkey “vs” PyMuPDF

Hai công cụ đảm nhiệm hai việc khác nhau:

```text
PDF
 ├─ Text layer dùng được → PyMuPDF lấy chữ và tọa độ
 └─ Scan/text layer lỗi  → Monkey nhận dạng ảnh
                          ↓
                     JSON canonical
```

- **PyMuPDF** lấy chữ đã lưu trong PDF, không phải đoán lại từ ảnh.
- **Monkey** nhận ảnh, sinh nội dung và cấu trúc.
- **PaddleOCR, MinerU, Docling** cung cấp các luồng orchestration, model và hậu xử lý khác nhau.

Docling và MinerU cũng có khả năng khai thác native text. Vì vậy, **native-first không phải ưu điểm độc quyền của phương án PyMuPDF + Monkey**.

Adapter PyMuPDF hiện chỉ lấy `get_text("dict")` rồi xuất text block; chưa dựng bảng hoặc thứ tự đọc đáng tin cậy. Đây là khoảng trống thực sự, không nên coi stack hiện tại đã thay thế đầy đủ document parser.  
Nguồn: `src/legal_vi_ocr/native.py:15–37`.

## 2. Monkey có thể làm component, không chỉ đọc cả trang

Đây là điểm ủng hộ đề xuất của bạn mạnh nhất.

Code Monkey có riêng các prompt cho:

| Chức năng | Prompt Monkey |
|---|---|
| Đọc vùng chữ | `Please output the text content from the image.` |
| Đọc bảng | `Please extract the table from the image and represent it in OTSL format.` |
| Đọc công thức | Yêu cầu xuất LaTeX |
| Layout | Yêu cầu category + coordinates theo reading order |
| End-to-end | Category + coordinates + content theo reading order |

Upstream còn có luồng **layout → crop → recognition**, không chỉ end-to-end. Vì vậy, dùng layout của framework khác rồi đưa crop cho Monkey **là phương án có căn cứ từ implementation**, không phải ý tưởng suy đoán.

Nguồn: [Monkey `core_runner.py:35–49`](https://github.com/hiennguyen9874/MonkeyOCRv2/blob/106914e55e399f09af6a34634a2ed44c6bdec950/parsing/core_runner.py#L35-L49), [tạo và nhận dạng crop](https://github.com/hiennguyen9874/MonkeyOCRv2/blob/106914e55e399f09af6a34634a2ed44c6bdec950/parsing/core_runner.py#L884-L924).

**Nhưng kết quả đang được đánh giá tốt trong #1 là cấu hình khác:** adapter hiện dùng **full-page end-to-end, bỏ preprocessing**, giới hạn ảnh 1.003.520 pixel. Không thể chuyển nhận xét chất lượng đó sang cấu hình “Paddle/MinerU/Docling crop → Monkey” mà không đo lại.  
Nguồn: `docs/monkeyocr-v2.md:50–56`.

## 3. Đánh giá từng pipeline

### A. PaddleOCR: khả thi, đặc biệt nhánh PaddleOCR-VL

Cần phân biệt hai trường hợp.

#### A1. Thay recognizer của PP-OCR / PP-StructureV3

**Không thể chỉ trỏ `text_recognition_model_dir` sang checkpoint Monkey.**

Các tham số đó lựa chọn model của component tương ứng; chúng không biến component thành một trình chạy VLM bất kỳ. Monkey có kiến trúc, processor, prompt và cơ chế sinh khác recognizer thông thường.

Có thể viết adapter để:

```text
Paddle phát hiện dòng/vùng → Monkey đọc crop → chuyển về kết quả recognition
```

Nhưng phải quyết định rõ:

- Đọc từng dòng hay từng đoạn?
- Ánh xạ kết quả về box nào?
- Xử lý confidence thế nào khi không có score tương đương?
- Có dùng Monkey để đọc bảng, hay vẫn dùng table model cũ?

**Đánh giá:** làm được, nhưng không phải đường tích hợp tự nhiên nhất cho checkpoint Parsing này. Chia trang thành quá nhiều crop nhỏ cũng có thể làm tăng số request; cần đo, không mặc định nhanh hơn.

Nguồn component configuration: `references/PADDLEOCR/paddleocr/_pipelines/pp_structurev3.py:35–95`.

#### A2. Giữ PaddleOCR-VL layout, thay VLM recognizer bằng Monkey

**Đây là phương án phù hợp hơn.**

Wrapper có sẵn:

- `vl_rec_backend`
- `vl_rec_server_url`
- `vl_rec_api_model_name`

Nghĩa là có thể tách môi trường PaddleX khỏi server Monkey, không cần ép hai runtime vào cùng process.  
Nguồn: `references/PADDLEOCR/paddleocr/_pipelines/paddleocr_vl.py:39–53`.

**Tuy nhiên, chỉ đổi endpoint chưa đủ.** PaddleX đang gửi các prompt như:

```text
OCR:
Table Recognition:
Formula Recognition:
```

Trong khi Monkey sử dụng các prompt riêng ở trên; bảng Monkey được yêu cầu xuất **OTSL**, nên cần chuyển sang representation mà pipeline nhận.

Mình kiểm tra trực tiếp phần này trong PaddleX `3.7.2` đang cài:  
`experiments/paddleocr-vl/.venv/lib/python3.12/site-packages/paddlex/inference/pipelines/paddleocr_vl/pipeline.py:290–355`.

Công việc tích hợp thực tế:

1. Giữ layout và crop của Paddle.
2. Đổi prompt theo loại vùng sang prompt Monkey.
3. Chuyển OTSL bảng sang cấu trúc tương thích.
4. Kiểm soát resize, token limit, lỗi và truncation.
5. Kiểm tra hậu xử lý không làm mất nội dung pháp lý.

**Lợi ích đáng thử:** crop có thể giữ chi tiết chữ nhỏ tốt hơn ảnh toàn trang bị resize; tận dụng layout/order và cơ chế ghép của Paddle.

**Rủi ro:** layout bỏ sót hoặc crop cắt dấu thì Monkey không khôi phục được phần không nhận được. Chất lượng layout của Paddle có thể tốt hơn hoặc kém hơn Monkey trên corpus này — chưa có số đo.

**Kết luận:** **ứng viên ưu tiên nếu mục tiêu là cải thiện OCR scan bằng layout-first.**

Một đối chứng rất rõ: **SenOCR thực sự gần với “chỉ thay model”**, vì model card xác nhận cùng interface và kiến trúc PaddleOCR-VL-1.6. Monkey không có cam kết tương thích này.  
Nguồn: `models/SenOCR-Vi/README.md:34–47`.

---

### B. MinerU 4: tích hợp được, nhưng phụ thuộc giao thức MinerU nhiều hơn

MinerU có cấu hình VLM endpoint và model name. Vì thế, về tầng kết nối, hoàn toàn có thể hướng tới server local của Monkey.  
Nguồn: `references/mineru/docs/en/usage/model_source.md:69–96`.

Nhưng client không đơn thuần gửi ảnh và nhận văn bản tùy ý. Nó có:

- Prompt riêng: `Text Recognition:`, `Table Recognition:`, `Layout Detection:`.
- Parser layout theo định dạng riêng.
- Kiểu `ContentBlock`, `ExtractResult`.
- Hậu xử lý và quy ước cho từng loại nội dung.

**Hai khả năng cần đánh giá riêng:**

#### B1. Standard: giữ layout MinerU, Monkey đọc crop

Đây là hướng khả thi hơn. Code Standard ánh xạ sang effort `high`, gọi `batch_extract_with_layout()`.

Có thể tận dụng layout/native processing của MinerU rồi thay bước nhận dạng. Client cấp thấp có tham số tùy chỉnh prompt, nên không nhất thiết phải viết lại toàn bộ client. Tuy nhiên, orchestration hiện tại vẫn cần được điều chỉnh để truyền cấu hình Monkey và chuyển kết quả bảng.

Nguồn:

- `references/mineru/mineru/parser/tier.py:12–17`
- `references/mineru/mineru/backend/analysis/pdf/window.py:565–614`
- `references/mineru/mineru/model/vlm/contracts.py:14–55`

**Đánh giá:** khả thi; có ích nếu muốn giữ luồng hybrid native + specialist của MinerU.

#### B2. Advanced: Monkey thay cả layout và recognition của MinerU VLM

Advanced gọi `batch_two_step_extract()`. Lúc này phải thích nghi cả output layout.

Monkey trả phần tử có `label`, `bbox`, `content`; client MinerU parse layout bằng giao thức riêng. **Đổi prompt thôi không giải quyết được khác biệt này.**

Cần adapter predictor hoặc sửa lớp chuyển đổi layout, bên cạnh phần nhận dạng crop.

**Đánh giá:** can thiệp sâu hơn Standard; chưa đáng ưu tiên nếu nhu cầu hiện tại chỉ là dùng Monkey đọc chữ tốt hơn.

Ngoài ra:

- Luồng native của MinerU là khả năng thật; run hiện tại đưa ảnh vào với `ocr_mode=ocr` **không đại diện cho mọi cấu hình MinerU**.
- Cross-page merge không tự được bảo đảm khi thay checkpoint. Runtime hiện khởi tạo client với `enable_cross_page_table_merge=False`.  
  Nguồn: `references/mineru/mineru/model/vlm/runtime.py:312–332`.

**Kết luận:** **không nên loại MinerU, nhưng thay model ở đây là thay một giao thức inference, không chỉ thay weights.**

---

### C. Docling: có đường mở rộng rõ nhất, nhưng phải chọn đúng tầng

#### C1. Monkey làm OCR plugin cho Standard PDF pipeline

**Docling hỗ trợ chính thức custom OCR engine** qua plugin và `BaseOcrModel`. Ngoài OCR, còn có extension point cho layout và table structure.  
Nguồn: `references/docling/docs/concepts/plugins.md:47–67`, `:145–176`.

Luồng có thể là:

```text
Native text + layout Docling
        ↓
Vùng cần OCR → Monkey
        ↓
TextCell → table structure → reading order → DoclingDocument
```

Cần chuyển output Monkey thành text cells, quy đổi tọa độ từ crop về trang và thực hiện merge native/OCR.

Điểm hạn chế quan trọng: **OCR plugin không tự đưa toàn bộ cấu trúc Monkey vào document.** Nếu chỉ trả text cells, phần layout/order/table do Monkey sinh có thể không được tận dụng; Docling tiếp tục làm các bước đó.

Đặc biệt, box cấp đoạn hoặc cả bảng của Monkey chưa tương đương độ chi tiết dòng/từ mà các bước downstream có thể cần. Phải kiểm tra trên bảng thực tế.

**Đánh giá:** hợp lý nếu mục tiêu là **Docling native-first với Monkey OCR bổ sung**, không phải giữ nguyên kết quả parsing Monkey.

**Lưu ý với lỗi đã thấy trong #1:** một trang Docling lỗi tách chữ dù không gọi OCR. Vì vậy, thay RapidOCR bằng Monkey **không mặc nhiên sửa được lỗi native extraction/assembly đó**. Nguyên nhân component bên trong vẫn chưa xác định.

#### C2. Monkey làm model cho Docling VLM pipeline

Docling có `ApiVlmOptions`, prompt tùy chỉnh và `decode_response()`: đủ cơ sở để gọi server Monkey local và chuyển output sang representation phù hợp.

Nhưng có khác biệt phiên bản:

- Môi trường dự án pin **Docling 2.90.0**, chưa có `DOTS_JSON`.
- Snapshot `references/docling` đã có parser `DOTS_JSON`.

Ngay cả trên snapshot mới, **không thể đưa nguyên output Monkey vào parser Dots**:

| | Monkey | Dots parser |
|---|---|---|
| Nhãn | `label` | `category` |
| Nội dung | `content` | `text` |
| Tọa độ | Chuẩn hóa 0–1000 | Pixel theo ảnh đầu vào |
| Bảng | Có thể OTSL | HTML |

Nguồn: `src/legal_vi_ocr/monkey.py:35–61`; `references/docling/docling/utils/dots_utils.py:5–18`.

Còn một chi tiết dễ sai: nhánh Dots của Docling tính kích thước ảnh theo quy ước Qwen2-VL. Vì vậy, **đổi tên field và chọn `DOTS_JSON` vẫn chưa đủ để bảo đảm bbox đúng**.  
Nguồn: `references/docling/docling/pipeline/vlm_pipeline.py:749–785`.

Có thể viết converter đúng tọa độ, xuất DocTags hoặc dựng `DoclingDocument` trực tiếp. Không nhất thiết phải fork toàn framework.

**Đánh giá:** **rất đáng cân nhắc nếu mục tiêu là sử dụng DoclingDocument, serializer và chunker.** Nhưng đó là thay nhánh conversion bằng Monkey, không phải tự động kết hợp mọi lợi ích của Standard pipeline.

#### C3. Không nhúng inference: chuyển kết quả Monkey sang DoclingDocument

Đây có thể là cách ít can thiệp nhất nếu chỉ cần downstream Docling:

```text
Monkey → kết quả có cấu trúc → DoclingDocument → export/chunking
```

Không chạy lại layout/OCR chỉ để dùng serializer hoặc chunker. Tuy nhiên, với #1, dự án đã chọn canonical riêng; cần tránh thêm một representation trung gian nếu chưa có người dùng cụ thể cho nó.

## 4. Vậy tại sao hiện tại vẫn nên giữ baseline độc lập?

Có ba lý do thực dụng, **không phải vì tích hợp bất khả thi**:

1. **Giữ đúng cấu hình đang có bằng chứng.** Đổi sang crop/layout khác là một engine configuration mới cần đánh giá lại.
2. **Cô lập nguyên nhân lỗi.** Biết lỗi đến từ Monkey, native text, layout hay hậu xử lý; không gộp chúng thành một kết quả khó giải thích.
3. **Không thêm tầng chuyển đổi trước khi biết lợi ích.** Monkey → canonical hiện đã có. Nhúng vào framework rồi lại chuyển về canonical thêm hợp đồng phải kiểm thử.

Nhưng phía ngược lại cũng đúng: **tự xây layout/table reconstruction hoàn chỉnh chỉ để tránh adapter framework có thể tốn công hơn nhiều**. PyMuPDF hiện chưa giải quyết những phần đó.

## 5. Khuyến nghị cho dự án này

| Mục tiêu | Phương án nên thử |
|---|---|
| Baseline chép trung thực, dễ truy vết | Giữ PyMuPDF native + Monkey độc lập |
| Chữ nhỏ/scan bị giới hạn ảnh toàn trang | So Monkey end-to-end với **Monkey two-stage upstream**, rồi thử **Paddle layout + Monkey** |
| Native PDF cần bảng/cấu trúc | Tiếp tục Docling Standard; chẩn đoán riêng lỗi native |
| Muốn Docling native-first nhưng OCR tốt hơn | Monkey OCR plugin |
| Muốn downstream Docling từ output Monkey | Converter sang `DoclingDocument`, chưa cần nhúng inference |
| Muốn toàn workflow hybrid MinerU | Thử Standard + Monkey crop recognizer trước Advanced |

**Kết luận cuối:** mình đồng ý với bạn rằng cần đánh giá phương án tái sử dụng pipeline. Tuy nhiên, lựa chọn đúng không phải “tự xây hay chỉ thay model”, mà là **thay component nào, giữ hợp đồng gì và pipeline đó giải quyết lỗi nào đang tồn tại**.

Với #1, mình ưu tiên giữ baseline hiện tại, sau đó thử **Monkey two-stage và Paddle layout + Monkey** cho nhánh scan; **Docling + Monkey** đáng ưu tiên nếu nhu cầu chính là native/table hoặc hệ sinh thái Docling. Chưa có cơ sở chọn tổ hợp nào thắng về chất lượng.

*Đây là đánh giá tài liệu và mã nguồn; mình không sửa file, không chạy inference hay benchmark mới. Các phương án tích hợp trên là khả thi về thiết kế, chưa được xác nhận chất lượng/runtime bằng chạy thử.*