## Kết luận

**Có các giải pháp xử lý riêng con dấu và chữ ký**, nhưng nên tách yêu cầu thành các bài toán khác nhau:

1. **Phát hiện:** tài liệu có chữ ký/con dấu không, ở vị trí nào?
2. **Đọc nội dung:** đọc chữ trong con dấu, hoặc họ tên viết tay gần chữ ký.
3. **Xác minh:** chữ ký có đúng người ký, con dấu có thật, tài liệu có bị chỉnh sửa không?

OCR chủ yếu giải quyết bài toán **đọc chữ**; detection giải quyết **tìm vùng**. Không nên coi kết quả OCR hay việc phát hiện được chữ ký/con dấu là bằng chứng xác thực pháp lý.

Dưới đây là các phương pháp và mô hình tìm được trong kho kiến thức hiện có. **Tôi chưa thể tìm kiếm web trực tiếp trong phiên này**, nên chưa thể khẳng định danh sách đầy đủ hoặc xác nhận tình trạng phát hành mới nhất.

## 1. Những mô hình đáng thử

| Giải pháp | Phù hợp với | Điểm cần lưu ý |
|---|---|---|
| [PP-StructureV3](wiki/pp-structurev3.md) / PP-OCRv4-seal | **Đọc chữ trên con dấu**, đặc biệt chữ chạy cong | Pipeline có module riêng PP-OCRv4-seal. Nguồn trong wiki chưa chứng minh chất lượng trên dấu pháp lý tiếng Việt hoặc trên ảnh dấu chồng chữ. |
| [PaddleOCR-VL-1.5](wiki/paddleocr-vl-1.5.md) và [1.6](wiki/paddleocr-vl-1.6.md) | Phân tích tài liệu và **nhận dạng vùng con dấu** | Bản 1.5 mô tả layout detection → crop vùng → nhận dạng seal. Wiki ghi 1.6 là bản kế tiếp; cần thử trực tiếp trên dữ liệu Việt Nam. |
| [Nanonets-OCR2](wiki/nanonets-ocr2.md) | OCR tài liệu và **đánh dấu sự hiện diện của chữ ký** trong đầu ra | Model card mô tả prompt yêu cầu xuất thẻ `<signature>`. Điều này **không chứng minh** có bounding box chính xác, nhận dạng người ký hay xác minh chữ ký. |
| [SenOCR-Vi](wiki/senocr-vi.md) | Baseline đọc **văn bản tiếng Việt** và một số trường hợp chữ viết tay | Được chuyên biệt hóa từ PaddleOCR-VL-1.6, nhưng bằng chứng trong wiki **không xác lập hiệu quả riêng cho chữ ký hay con dấu**. Dùng bổ sung, không mặc định thay thế module chuyên biệt. |

**Về benchmark con dấu:** tác giả PaddleOCR-VL báo cáo normalized edit distance trên bộ **300 ảnh nội bộ** là **0,138 cho 1.5** và **0,119 cho 1.6**; thấp hơn là tốt hơn. Tuy nhiên, dữ liệu và quy trình chưa đủ công khai để kiểm chứng độc lập, và không rõ tính đại diện cho con dấu Việt Nam. Không nên dùng các số này làm cam kết chất lượng. [Nguồn 1.5](wiki/paddleocr-vl-1.5.md) · [Nguồn 1.6](wiki/paddleocr-vl-1.6.md)

## 2. Các phương pháp xử lý

### A. Phát hiện chữ ký và con dấu: object detection hoặc segmentation

**Đề xuất kỹ thuật:**

1. Chuyển trang PDF scan thành ảnh.
2. Chạy detector để tìm các lớp như `signature`, `seal`.
3. Lưu **trang, bounding box hoặc mask**, ảnh crop và điểm số của detector.
4. Đưa từng crop sang nhánh xử lý phù hợp.

Có thể bắt đầu bằng model layout/vision sẵn có, sau đó **fine-tune detector** trên tài liệu thực tế nếu không phát hiện ổn định. Segmentation đáng thử khi cần tách vùng dấu hoặc chữ ký có hình dạng bất quy tắc; bounding box đơn giản hơn nếu chỉ cần tìm vị trí.

**Lưu ý quan trọng:** phải phân biệt vùng có nhãn “Ký, ghi rõ họ tên” với **chữ ký thực sự đã xuất hiện**. Nên có trạng thái `không chắc chắn`, không ép mọi trang thành có hoặc không.

### B. Đọc nội dung con dấu: seal OCR

Với dấu tròn, chữ thường nhỏ, cong, mờ hoặc chồng lên văn bản khác. Một pipeline thực tế có thể là:

```text
Trang tài liệu
  → phát hiện vùng dấu
  → crop và giữ ảnh màu gốc
  → thử tăng tương phản / xoay / xử lý hình học
  → seal OCR hoặc VLM nhận dạng crop
  → kiểm tra kết quả trên ảnh gốc
```

Nên bắt đầu bằng **PP-OCRv4-seal** trong PP-StructureV3, rồi so sánh với PaddleOCR-VL. Các bước tăng tương phản, tách màu hay làm thẳng chữ cong chỉ là **các biến thể cần thử**: dấu đỏ không phải lúc nào cũng đỏ rõ, và tiền xử lý có thể làm mất nét hoặc tạo artefact.

Nếu dấu đè lên văn bản, nên chạy **hai nhánh song song**: OCR trang gốc và OCR crop dấu. Giữ kết quả cùng ảnh gốc để người kiểm duyệt đối chiếu, thay vì xóa dấu khỏi tài liệu gốc.

### C. Xử lý chữ ký: detection khác với verification

Có ít nhất ba mục tiêu:

- **Có chữ ký hay chưa?** Dùng detector hoặc thử Nanonets-OCR2 để nhận diện dấu hiệu chữ ký.
- **Người ký là ai?** Đọc **họ tên được ghi riêng** gần chữ ký, nếu có; không suy diễn danh tính chỉ từ nét ký.
- **Chữ ký có thật không?** Cần một quy trình xác minh riêng, có dữ liệu tham chiếu và đánh giá sai số phù hợp. Ảnh scan có thể là bản sao hoặc đã bị chỉnh sửa; mô hình so khớp hình ảnh đơn thuần không đủ kết luận pháp lý.

Với **PDF ký số**, cần thêm nhánh kiểm tra chữ ký số bằng thông tin/chứng thư và dữ liệu ký trong PDF, chứ không chỉ kiểm tra hình ảnh chữ ký hiển thị. Quy trình kiểm tra pháp lý cụ thể cần đối chiếu yêu cầu nghiệp vụ và quy định áp dụng.

## 3. Pipeline tôi khuyến nghị để thử nghiệm

Đây là **đề xuất tổng hợp**, chưa được kiểm chứng bằng cách chạy trên tài liệu của bạn:

```text
PDF / ảnh
 ├─ Kiểm tra thông tin chữ ký số của PDF, nếu có
 └─ Render trang
     ├─ OCR toàn trang: PaddleOCR-VL hoặc SenOCR-Vi
     ├─ Detector: tìm chữ ký và con dấu
     │   ├─ Chữ ký → lưu vị trí, crop, trạng thái phát hiện
     │   └─ Con dấu → crop → PP-OCRv4-seal / PaddleOCR-VL
     └─ Ghép kết quả + trang/vị trí + chuyển trường hợp khó cho người duyệt
```

Ví dụ cấu trúc dữ liệu nên lưu:

```json
{
  "page": 3,
  "signatures": [
    {
      "bbox": [120, 600, 310, 720],
      "presence": "detected",
      "identity": null,
      "verification": "not_performed"
    }
  ],
  "seals": [
    {
      "bbox": [250, 520, 470, 740],
      "text": "Kết quả OCR cần được kiểm tra",
      "verification": "not_performed"
    }
  ]
}
```

`bbox` ở đây chỉ là ví dụ; khi triển khai cần quy định rõ hệ tọa độ và kích thước ảnh.

## 4. Cách đánh giá trước khi dùng cho hồ sơ pháp lý

Tạo một tập kiểm thử riêng, được phép sử dụng, có cả **trang không có chữ ký/dấu** và các trường hợp khó: dấu mờ, dấu chồng chữ, ảnh scan đen trắng, nhiều chữ ký, bản chụp nghiêng, họ tên viết tay.

Đánh giá riêng:

- **Detection:** precision và recall cho chữ ký và con dấu; kiểm tra riêng tỷ lệ bỏ sót.
- **Seal OCR:** character error rate hoặc normalized edit distance; đánh giá thêm các trường quan trọng như tên cơ quan, mã số nếu có.
- **Nghiệp vụ:** tỷ lệ trang cần duyệt tay và tỷ lệ sai sót sau duyệt.
- Chia dữ liệu theo **tài liệu hoặc nguồn**, không chia các trang của cùng tài liệu vào cả tập huấn luyện và kiểm thử.

Với tài liệu pháp lý, nên giữ ảnh gốc, kết quả theo từng vùng và lịch sử chỉnh sửa; hạn chế đưa hồ sơ mật hoặc dữ liệu cá nhân lên dịch vụ bên ngoài khi chưa rõ điều kiện xử lý dữ liệu.

**Giới hạn bằng chứng:** Các khả năng và benchmark trên chủ yếu là báo cáo của tác giả/model card, chưa được tôi chạy lại; tôi cũng chưa mở nghiên cứu gốc trong phiên này. Kiểm tra cấu trúc kho hiện báo **36 lỗi liên kết**, gồm một số nguồn gốc không còn tại đường dẫn được ghi, nên cần thận trọng với tính đầy đủ của kho. Tôi chưa ghi tổng hợp này vào wiki do tình trạng đó.

Nếu bạn cho biết mục tiêu chính là **(1) tìm dấu/ký, (2) đọc chữ trên dấu, hay (3) xác minh thật–giả**, cùng yêu cầu **chạy offline hay dùng API**, tôi có thể đề xuất PoC và tiêu chí chọn mô hình cụ thể hơn.