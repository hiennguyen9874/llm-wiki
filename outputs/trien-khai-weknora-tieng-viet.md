# Triển khai weknora tiếng việt

Tôi đã kiểm tra lại WeKnora ở commit `fd7a2586fd58` (v0.8.3), đọc code trực tiếp cùng với wiki. Kết luận: **WeKnora trả lời được bằng tiếng Việt, nhưng chưa hỗ trợ tiếng Việt đầy đủ.** Tôi chỉ đọc code, chưa chạy build, test, tokenizer, model hay OCR nào. Mọi đánh giá về chất lượng đều phải đo lại.

## 1. Những gì đã ổn

- **Prompt:** prompt chính viết bằng tiếng Anh, có chỗ điền ngôn ngữ (`{{language}}`). LLM hỗ trợ tiếng Việt thì câu trả lời, tóm tắt, câu hỏi gợi ý, wiki và graph đều ra tiếng Việt được.
- **VLM:** chỉnh được ngôn ngữ mô tả ảnh (`description_language`). Prompt OCR của VLM giữ nguyên ngôn ngữ gốc.
- **ASR:** có tham số ngôn ngữ theo từng knowledge base.
- **Embedding và rerank:** không thấy code nào phụ thuộc ngôn ngữ trong các phần đã đọc.

## 2. Các lỗ hổng tìm thấy trong code

| Hạng mục | Hiện trạng | Hệ quả với tiếng Việt |
|---|---|---|
| Chọn ngôn ngữ | Thứ tự ưu tiên: biến `WEKNORA_LANGUAGE` → header `Accept-Language` → mặc định `zh-CN`. Hàm `LanguageLocaleName` không có tiếng Việt | Prompt nhận chuỗi `"vi-VN"` thay vì "Vietnamese". UI để tiếng Anh thì tóm tắt và câu hỏi gợi ý ra tiếng Anh |
| Danh sách locale | Cố định 6 locale (zh-CN/zh-TW/en/ko/ja/ru) ở cả backend lẫn frontend | Kênh IM từ chối `vi-VN`. Phần sinh hướng dẫn MCP gặp ngôn ngữ lạ thì **quay về tiếng Trung giản thể** |
| Viết lại câu hỏi | Ví dụ mẫu (few-shot) trong `rewrite.yaml` bằng tiếng Trung | Có nguy cơ câu hỏi bị viết lại thành tiếng Trung, phân loại ý định kém đi |
| Mã hoá văn bản | Không chuẩn hoá NFC. File txt/md được đọc nguyên byte. docreader thử gb18030 trước latin-1 | File TCVN3/VNI/cp1258 dễ thành chữ rác. Văn bản NFD không khớp từ khoá với câu hỏi NFC |
| Chunker | Chỉ nhận diện en/de/zh. Tiếng Việt bị coi là tiếng Anh (ước lượng 4 ký tự/token). Dấu ngắt câu mặc định có `。` nhưng không có `. ` | Không nhận ra tiêu đề "Chương/Mục/Điều/Khoản", tiêu đề viết hoa có Ư/Đ/Ơ, chân trang "Trang" |
| PaddleOCR-VL | Tham số gửi đi bị cố định: tắt xoay trang (orientation) và nắn trang (unwarping), **bỏ qua footnote**, header và footer | Ảnh chụp bị nghiêng xử lý kém. Văn bản pháp lý mất chú thích |
| BM25 trên PostgreSQL | Tokenizer `chinese_lindera`, toán tử `\|\|\|` khớp bất kỳ token nào | Chưa rõ cách nó tách tiếng Việt, **bắt buộc phải test** |
| Mở rộng câu hỏi | Stopword chỉ có zh/en. Mỗi đoạn tách theo khoảng trắng thành một biến thể tìm kiếm | Sinh ra các truy vấn chỉ một âm tiết như "nghiệp", gây nhiễu |
| Backend khác | Milvus đưa tiếng Việt vào bộ phân tích tiếng Anh. Qdrant tách câu hỏi bằng jieba. ES/OpenSearch dùng analyzer standard | Phải test từng backend nếu không dùng PostgreSQL |
| Chỉ mục vector | HNSW chỉ có cho số chiều 798, 1024, 3584 | Model khác số chiều sẽ quét tuần tự (chậm) |
| Đánh giá | Tách từ cho BLEU/ROUGE chỉ nhận chữ Hán và ASCII | Điểm BLEU/ROUGE cho tiếng Việt sai, không dùng được |
| Chuỗi tiếng Trung trong backend | Nhãn tool của agent và bot IM viết cứng tiếng Trung. Có 212 file Go chứa chuỗi chữ Hán | Cần rà xem chuỗi nào hiện ra cho người dùng |

**Mâu thuẫn trong tài liệu:** `.env.example` ghi thứ tự `Accept-Language` > env > `en-US`. Code thực tế là env > `Accept-Language` > `zh-CN`. Nên làm theo code.

## 3. Lộ trình triển khai

**Bước 0 – Chuẩn bị**
- Cố định phiên bản WeKnora.
- Chọn backend tìm kiếm và model embedding 1024 chiều, hoặc thêm migration tạo chỉ mục HNSW cho số chiều khác.
- Dựng bộ dữ liệu test tiếng Việt: scan, bảng lớn, văn bản luật, viết tắt (BHXH, TNCN), câu hỏi không dấu, trộn Việt–Anh, câu không có đáp án.
- Đo baseline.

**Bước 1 – Chỉ cấu hình, chưa sửa code**
- Biến môi trường: `WEKNORA_LANGUAGE=vi-VN`, `TZ=Asia/Ho_Chi_Minh`, `DEFAULT_LOCALE=en-US`.
- Khai báo model, đặt `max_input_chars` và truncate cho embedding.
- Cấu hình từng knowledge base:
  - dùng PaddleOCR-VL cho PDF và ảnh;
  - VLM: `description_language=Vietnamese`;
  - ASR: `language=vi`;
  - thêm dấu ngắt `. `, `; `, chỉnh kích thước chunk hoặc bật parent-child.
- Mount thư mục `prompt_templates` có ví dụ viết lại câu hỏi bằng tiếng Việt.
- Đổi toàn bộ nguồn sang UTF-8 NFC trước khi upload.
- Kiểm tra `SHOW lc_ctype` của PostgreSQL.

**Bước 2 – Bản vá backend nhỏ**
- Thêm ánh xạ `vi`/`vi-VN` → "Vietnamese". Thêm `vi-VN` vào danh sách locale được hỗ trợ và vào bảng ngôn ngữ của MCP.
- Chunker: nhận diện tiếng Việt, tỉ lệ ký tự/token riêng, mẫu tiêu đề Chương/Mục/Điều/Khoản, chân trang "Trang", tiêu đề viết hoa có dấu, dấu ngắt câu.
- Mở rộng câu hỏi: thêm stopword và từ để hỏi tiếng Việt ("là gì", "như thế nào", "bao nhiêu"…), bỏ biến thể chỉ một âm tiết.
- Chuẩn hoá NFC lúc nạp tài liệu và lúc truy vấn. Xử lý mã hoá cũ (cp1258/TCVN3).
- Dịch nhãn tool của agent và bot IM.

**Bước 3 – Tìm kiếm từ khoá**
- So sánh `chinese_lindera` với tokenizer/analyzer phù hợp tiếng Việt: có và không có trường bỏ dấu, có và không có tách từ.
- Migrate chỉ mục, giữ tương đương giữa PostgreSQL và SQLite, có phương án rollback.

**Bước 4 – Giao diện và kênh**
- Viết bản dịch `vi-VN` (khoảng 8.800 dòng).
- Đăng ký locale ở mọi nơi liên quan: i18n, embed, các bộ chọn ngôn ngữ, `docker-entrypoint.sh`, kiểu dữ liệu API.
- Kiểm tra locale tiếng Việt của TDesign (chưa xác minh được vì snapshot không có `node_modules`).
- Cho IM và embed nhận `vi-VN`.

**Bước 5 – Go-live**
- Chặn phát hành nếu chưa đạt ngưỡng trên bộ test giữ riêng.
- Đánh giá bằng metric truy xuất (recall/MRR/NDCG) cùng một LLM-judge cố định (ví dụ Ragas), không dùng BLEU/ROUGE có sẵn.
- Chạy lại bộ test mỗi lần nâng cấp hoặc đổi model.

## 4. Checklist kiểm tra

- Log và prompt thể hiện đúng ngôn ngữ hiệu lực. Các worker chạy nền (tóm tắt, câu hỏi gợi ý, wiki, VLM) kế thừa đúng ngôn ngữ.
- Cùng một câu hỏi, thử: có dấu và không dấu, NFC và NFD, trộn Việt–Anh, "Điều 5 Khoản 2", ngày tháng, số kiểu "1.000.000 đồng". So kết quả của tìm từ khoá, tìm vector và hybrid.
- Xem chunk của một văn bản luật, một PDF scan, một bảng lớn: ranh giới tiêu đề, giới hạn token, footnote có bị mất không.
- Upload thử một file không phải UTF-8 để thấy lỗi thực tế.
- Kiểm tra `lc_ctype`, phiên bản ParadeDB, định nghĩa chỉ mục BM25, và dùng `EXPLAIN` xem HNSW có được dùng cho số chiều đã chọn không.

## Kết quả lưu vào wiki

- Trang mới: [wiki/weknora-vietnamese-deployment.md](wiki/weknora-vietnamese-deployment.md), trạng thái draft.
- Thêm liên kết từ trang tổng quan WeKnora, trang lộ trình fork, trang parsing/chunking, trang hybrid retrieval và trang source map.
- Cập nhật 56 dòng trong sổ coverage và sửa số đếm cũ bị lệch trên trang source map.
- Thêm một mục log.
- `tools/wiki_check.py` chạy qua.

Các giả định chưa kiểm chứng (được đánh dấu Unverified trong trang wiki): cách ParadeDB, jieba và pg_trgm xử lý tiếng Việt, và giả định của bạn rằng các model đều hỗ trợ tiếng Việt.