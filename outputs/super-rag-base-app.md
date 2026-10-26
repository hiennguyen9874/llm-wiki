**Tôi khuyên bắt đầu từ WeKnora.** Kết luận này dựa trên wiki hiện có, mà wiki chỉ được dựng từ việc đọc code. Không dự án nào được chạy hay đo, nên bạn cần kiểm chứng (bước 3) trước khi chốt.

## 1. Vì sao chọn WeKnora làm nền

| Tiêu chí                  | Lý do                                                                                                                                                                                   |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kiến trúc dễ mở rộng      | Go modular monolith dùng DI (Dig), có pipeline plugin, parser registry và connector interface. Thêm tính năng là gắn vào chỗ có sẵn, không phải sửa lõi.                                |
| Đã có đủ các lớp khó làm  | Nó đã có sẵn nhiều phần khó tự làm: RBAC 4 role, API key bị từ chối mặc định, task queue tách pool có dead-letter, agent ReAct có guard, memory, auto-wiki có revision, và MCP/CLI/SDK. |
| Retrieval tốt sẵn         | Có RRF chuẩn hoá, rerank lùi về thứ tự cũ khi lỗi, MMR, và giữ kết quả từng phần khi một engine lỗi.                                                                                    |
| Vận hành linh hoạt        | Chạy được bằng Compose, Helm, hoặc Lite (SQLite). Bắt đầu nhỏ rồi scale sau được.                                                                                                       |
| License                   | MIT, thoải mái nhất khi nhận code từ dự án khác.                                                                                                                                        |
| Cùng ngôn ngữ với RAGFlow | RAGFlow là nguồn tính năng phong phú nhất, và cũng viết bằng Go, nên port sang dễ nhất.                                                                                                 |

**Vì sao không chọn các cái còn lại:**

- **RAGFlow:** hạ tầng quá nặng (5 lớp lưu trữ, CGO, asset native). Repo có private key commit sẵn, và còn code/CI cũ chưa dọn.
- **OpenRAG:** chỉ chạy được 1 worker. Phụ thuộc chặt vào Langflow và OpenSearch. Nhiều auth mặc định yếu.
- **LightRAG, txtai:** là engine/framework chứ không phải platform. Phải tự xây toàn bộ phần tenant, agent, connector và UI.

**Ngoại lệ:** nếu nhu cầu số 1 của bạn là PDF phức tạp (layout, bảng, scan) thì RAGFlow đáng cân nhắc làm nền hơn.

## 2. Những gì nên lấy từ các app khác

Mức ưu tiên: ⭐⭐⭐ = làm sớm · ⭐⭐ = nên làm · ⭐ = tuỳ nhu cầu.

### Từ RAGFlow (Go sang Go, port dễ nhất)

| Tính năng                                                                                                                                       | Vì sao                                                                                                                | Ưu tiên |
| ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------- |
| **Evidence registry + chèn citation** (`internal/agentic_rag/evidence_registry.go`, `internal/service/citation.go`)                             | Wiki chưa ghi nhận cơ chế citation của WeKnora. Trước khi port, kiểm tra phần `answer references` sẵn có của WeKnora. | ⭐⭐⭐  |
| **Sync runner** (`internal/syncer`): chỉ lưu checkpoint sau khi batch thành công, bỏ qua tài liệu không đổi nhờ fingerprint xxh3, có lock lease | Làm cứng connector của WeKnora (hiện mới có interface).                                                               | ⭐⭐⭐  |
| **Lớp chặn SSRF cho connector** (`connector/ssrf.go`): kiểm tra từng bước redirect, ghim DNS, xoá header nhạy cảm khi đổi origin                | Bổ sung cho outbound filter hiện có của WeKnora.                                                                      | ⭐⭐    |
| **Chunker chuyên biệt**: table, QA, manual, hierarchy                                                                                           | WeKnora đã có parent-child; phần còn thiếu là chunker theo loại tài liệu.                                             | ⭐⭐    |
| **Mở rộng truy vấn bằng từ đồng nghĩa (synonym)** (`query_builder.go`)                                                                          | Tăng recall lexical, chi phí thấp.                                                                                    | ⭐      |
| Biến thể compile RAPTOR tree / mindmap                                                                                                          | WeKnora đã có wiki; đây chỉ là sản phẩm bổ sung.                                                                      | ⭐      |
| ⚠️ **Không port DeepDoc**                                                                                                                       | Kéo theo CGO và ONNX native. Thay vào đó, thêm MinerU hoặc Docling làm engine trong parser registry của WeKnora.      |         |

### Từ LightRAG (Python: viết lại thuật toán bằng Go, hoặc chạy sidecar như docreader)

| Tính năng                                                            | Vì sao                                                                                                                          | Ưu tiên |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------- |
| **Xoá tài liệu theo "contribution ownership" + recovery anchor**     | Khi bật graph, xoá một tài liệu phải gỡ được phần đóng góp của nó vào entity/relation. Wiki chưa ghi nhận cơ chế này ở WeKnora. | ⭐⭐⭐  |
| **Trích xuất/merge KG**: gleaning, tóm tắt mô tả, giới hạn source-ID | Phần trích xuất graph của WeKnora chưa được đọc; đây là chỗ LightRAG mạnh nhất.                                                 | ⭐⭐    |
| **Retrieval 2 tầng local/global/mix + ngân sách token** (6k/8k/30k)  | Cách ráp context rõ ràng, áp dụng cho câu hỏi multi-hop.                                                                        | ⭐⭐    |
| **Đánh dấu embedding space + tool rebuild vector**                   | Cho phép đổi embedding model mà không phải dựng lại cả KB.                                                                      | ⭐⭐    |
| **Không gọi LLM khi không retrieve được gì** (trả câu cố định)       | Rẻ, giảm hallucination.                                                                                                         | ⭐⭐    |
| Answer cache có key gồm cả cấu hình retrieval                        | Chỉ cần nếu chi phí LLM cao.                                                                                                    | ⭐      |

### Từ OpenRAG

| Tính năng                                                                                        | Vì sao                                                                                                                             | Ưu tiên |
| ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- | ------- |
| **`fence_untrusted_text`**: bọc chunk đã retrieve trong delimiter, escape trước delimiter có sẵn | Vài chục dòng code, giảm rủi ro prompt injection cho agent.                                                                        | ⭐⭐⭐  |
| **Truyền ACL từ nguồn vào chunk** (`DocumentACL`: owner, allowed users/groups) và lọc khi query  | WeKnora phân quyền theo workspace. Wiki chưa ghi nhận ACL theo từng tài liệu từ Drive/SharePoint. Cần nếu làm search doanh nghiệp. | ⭐⭐    |
| **Nhiều embedding space cùng tồn tại** (field gắn tên model), fallback về keyword                | WeKnora hiện từ chối search nhiều KB khác embedding model. Cách của OpenRAG cho phép migrate dần.                                  | ⭐⭐    |

### Từ txtai

| Tính năng                                                                                 | Vì sao                                         | Ưu tiên |
| ----------------------------------------------------------------------------------------- | ---------------------------------------------- | ------- |
| **SafeOpen / urlretrieve**: ghim IP, kiểm tra redirect, timeout 30s, giới hạn đọc 100 MiB | Mẫu tốt cho tính năng ingest URL.              | ⭐⭐    |
| Kiểm tra an toàn khi giải nén archive (tar từ chối link, kiểm tra đích giải nén)          | Cần nếu cho upload ZIP/TAR.                    | ⭐      |
| **Fusion log-odds/convex** làm tuỳ chọn song song với RRF                                 | Để thử nghiệm; chỉ giữ nếu đo thấy tốt hơn.    | ⭐      |
| Explain bằng token masking                                                                | Debug lý do một kết quả được xếp hạng như vậy. | ⭐      |

### Không nên copy

- RAGFlow `internal/harness`: chưa được nối vào runtime.
- Cơ chế key/passphrase commit sẵn của RAGFlow.
- Mặc định mở hoàn toàn của LightRAG (bind `0.0.0.0`, không auth, route Ollama luôn mở).
- JWT không kiểm tra chữ ký của OpenRAG.
- Pickle và "trusted config chạy code" của txtai.

## 3. Lộ trình gợi ý

1. **Kiểm chứng (1–2 tuần):** chạy WeKnora (và RAGFlow nếu PDF là trọng tâm) trên bộ tài liệu thật của bạn. Đo bằng [Ragas](wiki/ragas.md) theo cách trong [grounded-accuracy evaluation](wiki/grounded-accuracy-evaluation.md). Kết quả này làm baseline cho mọi lần port sau.
2. **Siết bảo mật WeKnora trước khi làm gì khác:**
   - tắt tự đăng ký;
   - đặt `JWT_SECRET` cố định và AES key đúng độ dài;
   - không mount Docker socket;
   - bật SSRF whitelist.
3. **Đợt 1 (⭐⭐⭐):** citation/evidence registry, sync runner, untrusted-text fence, xoá tài liệu theo ownership.
4. **Đợt 2 (⭐⭐):** ACL theo tài liệu, nhiều embedding space, chunker chuyên biệt, KG extraction, ngân sách token.
5. **Mỗi lần port:** chạy lại eval. Chỉ giữ thay đổi nào cải thiện số đo.

**Về license:** ưu tiên port thiết kế và thuật toán, viết lại có test, thay vì copy nguyên file. Nếu copy code Apache-2.0 (RAGFlow, OpenRAG, txtai) vào WeKnora (MIT), phải giữ header license gốc và thêm vào `NOTICE`/`THIRD_PARTY_NOTICES.md`.

**Hạn chế của khuyến nghị:** wiki mới đọc khoảng 4% code của WeKnora và RAGFlow. Một số chỗ tôi ghi là "chưa ghi nhận" (citation, xoá graph, ACL theo tài liệu) có thể đã có sẵn, nên kiểm tra trong code trước khi port.

Bạn có muốn tôi lưu khuyến nghị này vào wiki không? Nó sẽ là một trang Synthesis liên kết với [rag-platform-comparison](wiki/rag-platform-comparison.md).

## Những tính năng quan trọng

Câu trả lời dựa trên wiki, cộng thêm một lượt grep nhanh trong `raw/WeKnora`. Lượt grep đó chỉ để biết WeKnora **đã có sẵn** gì, nhằm tránh đề xuất port lại thứ đã có. Mức bằng chứng của nó chỉ là thấy tên file/symbol, chưa đọc kỹ thân hàm.

**Đính chính câu trả lời trước:** WeKnora đã có `chat_pipeline/citation_sources.go`, `query_expansion.go`, `query_understand.go` và `rerank.go`. Vậy citation không còn là khoảng trống lớn như tôi nói lần trước.

Mức ưu tiên: ⭐⭐⭐ = nên làm sớm · ⭐⭐ = nên làm · ⭐ = thử nghiệm.

---

## 1. Parsing/OCR

**WeKnora đã có:**

- docreader Python (builtin, MarkItDown, OpenDataLoader).
- Các engine Go: `builtin`, `simple`, `anydoc`, `mineru` (+cloud), `paddleocr_vl` (+cloud).
- Pipeline smartOCR cho ảnh, chuẩn hoá bảng HTML, giới hạn file 50 MB.

Phần OCR/layout vì vậy đã khá đủ. Thứ còn thiếu chủ yếu là **phân tích đa phương thức sau khi parse** và **kiểm soát chất lượng**.

| Lấy gì                                                                                                                                                                                                | Từ đâu                                                                                                                                       | Vì sao                                                                                          | Ưu tiên |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------- |
| Bộ tài liệu khó để chạy regression sau mỗi lần đổi parser                                                                                                                                             | ý tưởng trong [rag-ingestion-validation](wiki/rag-ingestion-validation.md); bài học từ OpenRAG: định dạng được chấp nhận ≠ định dạng đã test | Rẻ, và mọi thay đổi parser phía dưới cần nó để đo                                               | ⭐⭐⭐  |
| Phân tích riêng từng hình vẽ/bảng/công thức dưới dạng sidecar (`.drawings/.tables/.equations.json`). Hình dùng VLM, bảng/công thức dùng model extract. Thêm ±2.000 token ngữ cảnh xung quanh mỗi item | LightRAG `analyze_multimodal` ([trang wiki](wiki/lightrag-parsing-multimodal.md))                                                            | Bảng và công thức thành mô tả tìm kiếm được, không chỉ là ảnh OCR                               | ⭐⭐    |
| Lớp chặn ảnh: kiểm tra đường dẫn nằm trong thư mục sidecar, tối thiểu 64 px, tối đa 5 MiB, chỉ cho PNG/JPEG/GIF/WebP, cache theo từng item                                                            | LightRAG `_resolve_sidecar_image_path`                                                                                                       | Tránh tốn VLM cho icon/ảnh rác, chặn path traversal                                             | ⭐⭐    |
| Đóng băng parse/chunk options lúc enqueue để reparse ra kết quả lặp lại được                                                                                                                          | LightRAG `resolve_parser_directives`, `full_docs`                                                                                            | Đổi cấu hình global không âm thầm làm khác đi tài liệu cũ                                       | ⭐⭐    |
| Thêm engine Docling, kèm phân loại lỗi: lỗi tạm/5xx khác với 413, retry 500 tối đa 5 lần, probe tương thích `traverse_pictures`                                                                       | OpenRAG `docling_remote.py`, `export_docling_document.py`                                                                                    | Một lựa chọn local, không phải cloud, cho PDF/Office                                            | ⭐      |
| DeepDoc (layout/table PDF native)                                                                                                                                                                     | RAGFlow                                                                                                                                      | Chỉ nên lấy nếu MinerU/PaddleOCR đo ra kém. Nó kéo theo CGO và ONNX, nên chạy như service riêng | ⭐      |

## 2. Chunking

**WeKnora đã có:**

- Các chiến lược `auto` / `heading` / `heuristic` / `recursive` / `legacy`.
- Validator loại chunk kém, giữ nguyên các đoạn code/math/bảng.
- Parent-child 4096/384.
- Heading breadcrumb ghép vào trước khi embed, và lưu offset rune về văn bản nguồn.

| Lấy gì                                                                                                                                        | Từ đâu                                          | Vì sao                                                                               | Ưu tiên |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------ | ------- |
| **Table chunker**: chia theo dòng, lặp lại header ở mỗi chunk. Có các bậc lùi: theo dòng → theo ký tự → recursive                             | RAGFlow table chunker; LightRAG chiến lược `P`  | Hiện bảng chỉ "không bị cắt ngang". Bảng lớn cần được chia mà vẫn giữ nghĩa từng cột | ⭐⭐⭐  |
| **Đếm token thật** theo tokenizer của embedding model, thay cho ước lượng ký tự × 0.9                                                         | LightRAG fixed `F` (1200/100 token)             | Tránh chunk vượt giới hạn embedding hoặc phí dung lượng                              | ⭐⭐    |
| **Semantic chunking**: cắt theo khoảng cách embedding (`V`) và theo đoạn/heading từ blocks sidecar (`P`). Đoạn quá dài cắt lại bằng recursive | LightRAG [chunking](wiki/lightrag-chunking.md)  | Tôi không thấy semantic splitter trong `internal/infrastructure/chunker`             | ⭐⭐    |
| Chunker chuyên biệt cho **QA/FAQ**, **manual**, **page**                                                                                      | RAGFlow `GeneralChunker` và các chunker cùng họ | Tài liệu hỏi-đáp và hướng dẫn sử dụng cho recall tốt hơn khi giữ trọn đơn vị câu hỏi | ⭐⭐    |
| Gắn ngữ cảnh xung quanh vào chunk bảng/ảnh (có cấu hình)                                                                                      | RAGFlow (table/image context)                   | Chunk ảnh/bảng đứng một mình thường không có từ khoá để tìm thấy                     | ⭐⭐    |
| Chunk ID ổn định `{doc_id}-chunk-{order}`                                                                                                     | LightRAG                                        | Cho phép re-index tăng dần và citation ổn định                                       | ⭐      |

## 3. Hybrid retrieval/fusion

**WeKnora đã có:**

- Weighted RRF có chuẩn hoá, fan-out ra nhiều store.
- `query_understand`, `search_entity`, `wiki_boost`, merge expand/overlap.
- `query_expansion` chỉ chạy khi recall thấp. Code của nó tự ghi rằng các biến thể chỉ là **bỏ stopword và đảo thứ tự từ**, và chỉ áp cho nhánh keyword.

| Lấy gì                                                                                                                                                                               | Từ đâu                                                                  | Vì sao                                                                                                                          | Ưu tiên |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------- |
| **QueryBuilder có từ đồng nghĩa + cụm từ có trọng số**, cộng **boost theo field**: title, important keywords, generated questions, content                                           | RAGFlow `query_builder.go::Question`, `reranker.go`                     | Nâng cấp thật cho phần expansion hiện quá đơn giản. WeKnora đã sinh question ở bước ingest, nên chỉ cần thêm boost cho field đó | ⭐⭐⭐  |
| **Retrieval graph 2 tầng**: keyword low-level → entity vector, keyword high-level → **relation vector**, rồi lấy lại chunk nguồn, có ngân sách token riêng cho entity/relation/chunk | LightRAG mode `mix`/`global` ([trang wiki](wiki/lightrag-retrieval.md)) | WeKnora có entity search; nhánh relation-vector (`global`) giúp câu hỏi mang tính chủ đề hoặc tổng hợp                          | ⭐⭐    |
| **Nhiều embedding space cùng lúc**: field vector gắn tên model, query từng space rồi merge, tài liệu cũ vẫn tìm được bằng keyword                                                    | OpenRAG [hybrid retrieval](wiki/openrag-hybrid-retrieval.md)            | WeKnora hiện **từ chối** search nhiều KB khác embedding model. Cách này cho phép migrate model dần dần                          | ⭐⭐    |
| Fusion **log-odds** (chuẩn hoá dense score theo median/std) và **convex** làm tuỳ chọn bên cạnh RRF                                                                                  | txtai `hybrid.py::LogOdds`                                              | RRF bỏ mất độ lớn của score. Đáng thử A/B, chỉ giữ nếu đo thấy tốt hơn                                                          | ⭐      |
| Thử lại khi rỗng bằng cách nới điều kiện match/similarity                                                                                                                            | RAGFlow `Retrieval`                                                     | Bổ sung cho expansion hiện có                                                                                                   | ⭐      |
| Prior theo tài liệu (pagerank feature), fuzzy/phrase-prefix để chịu lỗi gõ                                                                                                           | RAGFlow; OpenRAG (ES/OpenSearch)                                        | Phụ thuộc backend. Chỉ đáng làm khi dùng ES/OpenSearch                                                                          | ⭐      |

## 4. Reranking

**WeKnora đã có:**

- Rerank bằng model, lỗi thì lùi về thứ tự retrieval.
- Nới threshold khi không có kết quả qua ngưỡng.
- Composite score 0.6/0.3/0.1, MMR λ=0.7, giữ lại ảnh có điểm vector tốt, passage fitting.

Đây là phần đã mạnh nhất, nên chỉ cần bổ sung vài chỗ.

| Lấy gì                                                                                                                 | Từ đâu                                                  | Vì sao                                                                                                        | Ưu tiên |
| ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| **Rerank cục bộ khi không có model**: kết hợp token similarity với vector similarity, có trọng số theo field           | RAGFlow `RerankWithKNN`, `HybridSimilarity`             | Hiện khi không có hoặc lỗi model thì chỉ còn thứ tự retrieval. Bản Lite/offline cần một phương án lùi tốt hơn | ⭐⭐⭐  |
| **Chia passage dài trước khi rerank** rồi gộp điểm (max), thay vì cắt bớt                                              | LightRAG (Cohere long-document params)                  | Parent chunk 4.096 ký tự dễ bị cắt mất nội dung nếu chỉ "fit"                                                 | ⭐⭐    |
| **Phễu cố định**: rerank → min score → top_k → **cắt theo ngân sách token còn lại của prompt** → đánh số lại reference | LightRAG `process_chunks_unified`, `_build_context_str` | Context không tràn, và số citation khớp với các chunk thực sự còn lại                                         | ⭐⭐    |
| Reranker local (cross-encoder/similarity pipeline) không cần vendor                                                    | txtai `Reranker`                                        | Phù hợp Lite/desktop                                                                                          | ⭐⭐    |
| Explain bằng token masking để debug xếp hạng                                                                           | txtai `Embeddings.explain`                              | Tiện khi tinh chỉnh                                                                                           | ⭐      |

**Cảnh báo:** theo [benchmark FRAMES](wiki/rag-retrieval-technique-tradeoffs.md) (vendor tự báo cáo), một cross-encoder yếu đã **kéo một pipeline tốt xuống gần 9 điểm**. Phải đo từng reranker trên dữ liệu của bạn, không bật mặc định.

---

## Thứ tự làm gợi ý

1. Bộ regression set + eval bằng [Ragas](wiki/ragas.md) để có baseline.
2. Table chunker, đếm token thật.
3. Từ đồng nghĩa + boost theo field, rerank cục bộ khi không có model.
4. Phân tích sidecar đa phương thức, nhiều embedding space.
5. Semantic chunking, graph `global`/`mix`, chia passage dài khi rerank.
6. Thử nghiệm: log-odds fusion, DeepDoc.

Ở mỗi bước, chỉ giữ thay đổi nếu số đo cải thiện. Với code Apache-2.0 từ RAGFlow/OpenRAG/txtai, giữ ghi công trong `THIRD_PARTY_NOTICES.md`.

Lần này tôi không ghi gì vào wiki. Bạn có muốn lưu kế hoạch port này thành một trang Synthesis, kèm cập nhật [weknora-hybrid-retrieval](wiki/weknora-hybrid-retrieval.md) về `query_expansion` và `citation_sources` vừa thấy, không?
