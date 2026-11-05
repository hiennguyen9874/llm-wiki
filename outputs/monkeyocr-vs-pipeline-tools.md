**Kết luận ngắn:** MonkeyOCRv2-B-Parsing là một model parsing kèm serving stack. PaddleOCR, MinerU 4 và Docling là các lớp xung quanh hoặc thay thế model đó. Các công cụ này hơn ở khả năng điều phối, cấu trúc dữ liệu đầu ra và workflow. Wiki không cho thấy chúng hơn B-Parsing về độ chính xác trên mọi tiêu chí. Ngược lại, B-Parsing dẫn ở MDPBench, kể cả tiếng Việt. Đây là kết luận tổng hợp từ wiki, chưa có phép đo trực tiếp giữa B-Parsing và ba công cụ.

## 1. Hai bên không cùng cấp

**B-Parsing** gồm encoder ViT-B 0.1B, projector MLP và Qwen3-0.6B, tổng 0.7B. Model dự đoán loại phần tử và tọa độ theo thứ tự đọc, crop từng phần tử để nhận dạng nội dung, rồi ghép kết quả ([MonkeyOCRv2](../wiki/monkeyocrv2.md)). Phần serving gồm vLLM, tùy chọn DFlash, CLI, Gradio và FastAPI. `POST /parse` trả về một file zip chứa Markdown ([serving stack](../wiki/monkeyocrv2-serving-stack.md)).

Ba công cụ kia là các lớp khác:
- **PaddleOCR:** toolkit gồm model, training và deployment.
- **MinerU 4:** application có tier routing.
- **Docling:** converter có document IR (intermediate representation).

Ngoài ra, MinerU dùng nhiều model Paddle, còn Docling có thể dùng PP-OCR qua RapidOCR. Vì vậy phép so sánh công bằng là "model parse" với "model parse cộng orchestration" ([so sánh](../wiki/paddleocr-mineru-docling-comparison.md) §2).

## 2. Công cụ mang lại gì (Synthesis từ wiki)

| Lợi ích | Công cụ | B-Parsing có tương đương không? |
|---|---|---|
| Đường nhanh cho PDF có native text, không cần chạy model | MinerU `flash`; Docling selective OCR ưu tiên PDF text | Wiki chỉ ghi quy trình crop rồi recognize. Không có ghi nhận về native-text path. |
| Chọn mức nỗ lực: specialist model, rồi VLM | MinerU `basic`, `standard`, `advanced` | Không có trong wiki. |
| Nhiều cấu hình model và engine có thể thay thế | Docling (OCR, layout, table, plugin); Paddle (PP-OCRv6, PP-StructureV3, VL-1.6); MinerU (tách small model và VLM) | Một checkpoint, một đường parsing. |
| Biểu diễn trung gian có kiểu dữ liệu, kèm provenance | Docling `DoclingDocument` | Đầu ra được ghi nhận là Markdown trong zip. |
| Chunking theo cấu trúc, có token budget | Docling `HierarchicalChunker` và `HybridChunker` | Không có. Chỉ có tích hợp RAGFlow, do vendor tự báo cáo. |
| Giữ cấu trúc bảng khi xuất | Docling JSON/HTML giữ span; Markdown thì flatten | Không có thông tin. |
| Cell coordinates chi tiết | PP-StructureV3 (theo README Paddle) | Không có thông tin. |
| Quality gate cho review routing | Docling confidence grades (`table_score` chưa implement) | Không có. |
| Model nhỏ cho CPU/edge, tự train detector và recognizer | PP-OCRv6 (1.5M–34.5M tham số) | B-Parsing có CPU path (2026.08.22), không có số latency. Có fine-tuning entry points nên "trainable" không riêng của Paddle. |
| Library, cache, search, đọc tiếp theo page/block | MinerU 4 | Không có. |
| Nhiều định dạng đầu vào | Docling, MinerU | Wiki chưa ghi định dạng đầu vào của `parse.py`. |

## 3. Chất lượng: B-Parsing không thua toàn diện

Mọi số dưới đây là **Reported**, chưa chạy lại. Mục này so model với model: PaddleOCR-VL-1.6 và MinerU2.5-Pro, không phải MinerU 4 hay Docling nguyên cả hệ ([benchmark](../wiki/document-ocr-model-benchmark-comparison.md)).

| Benchmark | B-Parsing | PaddleOCR-VL-1.6 | MinerU2.5-Pro |
|---|---:|---:|---:|
| OmniDocBench v1.6 overall | 91.57 | **96.33** | 95.75 |
| Table TEDS | 88.24 | **94.76** | 93.42 |
| Real5 overall (ảnh chụp) | 89.22 (qua OvisOCR3) | **93.19** | 88.96 |
| MDPBench overall (README 2026-10-30) | **83.3** | 78.9 | 71.0 |
| MDPBench ảnh chụp | **81.7** | 76.3 | 66.1 |
| MDPBench tiếng Việt | **83.2** | 80.9 | 74.2 |

Cách đọc:
- Trên OmniDocBench, tài liệu số sạch và bảng, B-Parsing thấp hơn rõ.
- Trên MDPBench đa ngôn ngữ và ảnh chụp, B-Parsing dẫn đầu.
- Docling không có hàng nào trong các bảng này, nên không xếp hạng được.
- Số Real5 của B-Parsing lấy từ card OvisOCR3, không phải của chính tác giả.
- Số MDPBench của MinerU là 71.0 và số của Paddle là 78.9 trong README, không phải 75.0 như trong paper MonkeyOCR.

## 4. Giới hạn

- Wiki không có so sánh trực tiếp "B-Parsing một mình" với ba công cụ. Các hàng "Không có" ở bảng trên nghĩa là không compiled hoặc không retrieved, không phải B-Parsing chắc chắn thiếu tính năng đó.
- Wiki không ghi B-Parsing có thể chạy bên trong Docling, MinerU hay Paddle hay không. Tích hợp duy nhất được ghi là RAGFlow (vendor-reported). Phương án "dùng B-Parsing làm engine, công cụ làm khung" chưa có bằng chứng.
- Không có số throughput so sánh được. DFlash "up to 2×" thiếu phần cứng và protocol. Các trang `monkeyocrv2*` đều ở `status: draft`.
- Tôi không mở `raw/` trong lượt này. Mọi nội dung lấy từ output file và wiki.

## 5. Đối chiếu `outputs/paddleocr-mineru-docling-comparison.md` với wiki

- Output khớp với [wiki/paddleocr-mineru-docling-comparison.md](../wiki/paddleocr-mineru-docling-comparison.md). Các số 96.33, 95.75, 93.19, 88.96 và 82.83 vs 80.90 đều trùng.
- **Khoảng trống:** output và trang wiki đó không đề cập MonkeyOCRv2. Mục tiếng Việt (§7) khuyên thử Paddle và SenOCR-Vi. Nhưng theo bảng MDPBench trong wiki, B-Parsing đạt VI 83.2, cao hơn SenOCR-Vi (82.83, đã re-aggregate) và PaddleOCR-VL-1.6 (80.9). Với corpus tiếng Việt, B-Parsing đáng vào shortlist.

## 6. Gợi ý lựa chọn (Synthesis)

- Cần ảnh chụp, đa ngôn ngữ hoặc tiếng Việt, và chỉ cần Markdown: thử B-Parsing trước.
- Cần RAG có provenance, chunking hoặc bảng có merged cells: chọn Docling.
- Cần tài liệu khó hoặc PDF dài theo tier, kèm library và agent reading: chọn MinerU 4.
- Cần train OCR riêng hoặc chạy CPU/edge: chọn PaddleOCR.

Tôi chưa lưu kết quả này vào wiki và để nó ở dạng tạm thời. Nếu bạn muốn, tôi sẽ lưu thành concept `Synthesis` qua `wiki-ingest`, bổ sung MonkeyOCRv2 vào so sánh hiện có.