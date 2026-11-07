Có. Khả năng bạn đang tìm thường được gọi là **cross-page document parsing** hoặc **cross-page reconstruction**: không chỉ OCR từng trang, mà còn nhận biết đoạn văn hoặc bảng tiếp tục qua trang kế tiếp.

Cần phân biệt hai mức:

- **Gộp output:** OCR từng trang rồi nối chuỗi theo thứ tự trang. Cách này chưa chắc nhận ra đoạn văn hay bảng bị ngắt.
- **Khôi phục nội dung xuyên trang:** xem ngữ cảnh của hai hoặc nhiều trang để quyết định phần nào thực sự nối tiếp, rồi tái tạo nội dung chung.

### Những lựa chọn đáng thử

| Công cụ | Khả năng liên quan | Phù hợp khi |
|---|---|---|
| [Unlimited OCR 2](wiki/unlimited-ocr-2.md) | Theo báo cáo của tác giả, xử lý nhiều trang theo thứ tự, dùng các cửa sổ trang có phần chồng lấp; benchmark có đánh giá cả **đoạn văn và bảng xuyên trang**. | Bạn cần xử lý tài liệu dài và muốn thử nối cả văn bản lẫn bảng. Ví dụ triển khai trong wiki dùng GPU A800-80GB; cần kiểm tra yêu cầu thực tế theo cấu hình. |
| [OvisOCR3](wiki/ovisocr3.md) | Có quy trình rõ ràng cho **bảng xuyên trang**: parse từng trang, sau đó đưa hai ảnh trang liền kề cùng Markdown vào model để quyết định và ghép bảng thành HTML. Có thể lặp để ghép bảng dài hơn hai trang. | PDF có bảng bị cắt ngang trang. Đây là xử lý bảng cụ thể, **không nên mặc định** nó cũng tự nối tốt mọi đoạn văn xuyên trang. |
| [PaddleOCR-VL-1.5](wiki/paddleocr-vl-1.5.md) | Tài liệu ghi nhận có hậu xử lý ghép bảng xuyên trang và chỉnh phân cấp tiêu đề. | Bạn đã dùng hệ sinh thái PaddleOCR. Đây là phiên bản cũ; cần kiểm tra pipeline và cấu hình phiên bản bạn định dùng trước khi giả định tính năng được bật sẵn. |

Ngoài ra, [MiniCPM-OCR SDK](wiki/task-cross-page-table-reconstruction.md) có cơ chế ghép bảng dựa trên quy tắc; theo cấu hình được ghi nhận trong wiki thì tính năng này **mặc định tắt**. Nó có thể bỏ sót bảng nối tiếp hoặc ghép nhầm hai bảng giống nhau.

**Gợi ý chọn nhanh:** nếu trọng tâm là **đoạn văn tiếp tục qua trang**, thử Unlimited OCR 2; nếu trọng tâm là **bảng qua trang**, thử OvisOCR3. Dù dùng công cụ nào, nên thử trên vài PDF thực tế của bạn, nhất là trang có header/footer, bảng lặp tiêu đề và nội dung nhiều cột. Các kết quả trong wiki chủ yếu là báo cáo của tác giả, chưa được kiểm chứng độc lập tại đây.

**Giới hạn:** Wiki hiện có lỗi liên kết tới một số nguồn gốc, nên tính toàn vẹn và khả năng kiểm tra lại bằng chứng bị hạn chế; tôi chưa chạy OCR hay nghiên cứu thêm từ nguồn gốc trong lượt này. Phần so sánh trên được để ở dạng trả lời tạm thời, chưa lưu lại vào wiki.

PDF của bạn chủ yếu bị ngắt **đoạn văn**, **bảng**, hay cả hai? Và bạn cần chạy **local** hay dùng API cũng được?