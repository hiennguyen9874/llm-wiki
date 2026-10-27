# So sánh txtai, WeKnora, RAGFlow và LightRAG

Wiki đã có trang cho cả 4 hệ thống (`wiki_check` báo OK, 120 concept). Câu trả lời dưới đây chỉ dựa trên wiki, tôi không đọc lại `raw/`.

Cả 4 trang tổng quan đều ở trạng thái `draft`. Kiến thức đến từ việc đọc code tại một commit cố định, chưa build hay chạy test, chưa chạy benchmark. "Observed" nghĩa là đã thấy trong code. "Reported" nghĩa là README nói vậy nhưng chưa ai kiểm chứng. "Synthesis" là suy luận của tôi.

## 1. Mỗi hệ thống là gì

| | [txtai](wiki/txtai.md) | [WeKnora](wiki/weknora.md) | [RAGFlow](wiki/ragflow.md) | [LightRAG](wiki/lightrag.md) |
|---|---|---|---|---|
| Loại | Framework Python có thể nhúng vào ứng dụng khác, xoay quanh một embeddings database | Nền tảng kiến thức gồm RAG, agent, tự sinh wiki và nhiều cách tích hợp | Nền tảng RAG/context engine cho doanh nghiệp, có agent canvas | Engine RAG kết hợp graph và vector, kèm server và WebUI |
| Ngôn ngữ / stack | Python ≥3.11, FastAPI tuỳ chọn, không có UI chính thức | Go/Gin + Dig DI, UI Vue/Vite/Pinia, docreader Python | Go 1.27 + Gin + CloudWeGo eino, UI React/Vite | Python ≥3.10, FastAPI, UI React 19/Vite |
| Commit đã đọc | `738aac4` (v9.15.0) | `fd7a258` (v0.8.3) | `1731e54` | `aaebfe1` (v1.5.8) |
| License | Apache-2.0 | MIT (thành phần bên thứ ba có license riêng) | Apache-2.0 | MIT |
| Kiểu kiến trúc | Ghép các thành phần qua factory, không bắt buộc service ngoài | Một khối modular monolith dựa vào hạ tầng ngoài | Một binary Go, chạy theo nhiều mode (API/ingestor/syncer/DeepDoc/migrate) | Một dataclass facade ghép các mixin, lưu trữ chia làm 4 trục |

Nhận xét (Synthesis): txtai là thư viện, bạn tự lắp thành ứng dụng. WeKnora và RAGFlow là ứng dụng hoàn chỉnh chạy nhiều service. LightRAG nằm giữa: cốt lõi là một engine RAG, có thêm server và UI. Xem [txtai-architecture](wiki/txtai-architecture.md), [weknora-backend-architecture](wiki/weknora-backend-architecture.md), [ragflow-architecture](wiki/ragflow-architecture.md), [lightrag-architecture](wiki/lightrag-architecture.md).

## 2. Parsing và chunking

| | txtai | WeKnora | RAGFlow | LightRAG |
|---|---|---|---|---|
| Parser | `Textractor` thử lần lượt Tika → Docling → LiteParse, rồi chuyển HTML sang Markdown | docreader Python gọi qua gRPC/HTTP: builtin, MarkItDown, OpenDataLoader. Giới hạn file 50 MB | DeepDoc native (PDF layout/OCR/table) cùng nhiều họ định dạng khác | Registry: native/legacy/MinerU/Docling, chọn engine theo từng file |
| Chunking | Tắt theo mặc định. Thứ tự ưu tiên: chunker ngoài (Chonkie) → sentences → lines → paragraphs → sections | `auto` dựa trên profile cấu trúc, kiểm tra kết quả (`ValidateChunks`), fallback về splitter cũ. Mặc định 512/80 ký tự, có parent 4096 / child 384 | Pipeline canvas File→Parser→GeneralChunker→Extractor→Tokenizer, mặc định 512 token. Parent chunk ẩn để mở rộng ngữ cảnh | Chọn được F/R/V/P/C. Fixed mặc định 1200/100 token. Tham số được lưu cố định cho từng tài liệu lúc enqueue |
| Multimodal | Pipeline riêng cho caption, object, transcription, image hash | Làm sạch ảnh base64 trước khi embedding. Embedding ảnh: Reported | Có parser cho hình ảnh và âm thanh | Phân tích image/table/equation bằng VLM thành sidecar (không cần RAG-Anything) |

Nguồn: [txtai-pipelines](wiki/txtai-pipelines.md), [weknora-document-ingestion](wiki/weknora-document-ingestion.md), [ragflow-ingestion](wiki/ragflow-ingestion.md), [lightrag-chunking](wiki/lightrag-chunking.md), [lightrag-parsing-multimodal](wiki/lightrag-parsing-multimodal.md).

## 3. Retrieval và ranking

Đây là điểm khác nhau lớn nhất giữa 4 hệ thống.

| | Cơ chế hybrid | Fusion | Rerank |
|---|---|---|---|
| **txtai** | Dense ANN (Faiss mặc định, khoảng 12 backend) + sparse (BM25 trên SQLite, TF-IDF, neural sparse, Postgres FTS). Truy vấn được bằng SQL `similar()` | Chọn theo strategy: Bayesian log-odds, convex, hoặc RRF (`1/(rank+1)`, không có offset 60). Lấy dư `limit*10` ứng viên | Pipeline `Reranker` riêng, không tự chạy |
| **WeKnora** | Phân phối truy vấn tới vector và keyword engine gắn với từng store, cho nhiều KB. Từ chối nếu các KB dùng embedding model khác nhau | RRF có trọng số, đã chuẩn hoá: k=60, vector 0.7 / keyword 0.3. Lưu ý: đặt trọng số = 0 **không** tắt được retriever | Rerank bằng model, lỗi thì giữ thứ tự cũ. Có nới threshold, chấm điểm tổng hợp, chọn đa dạng bằng MMR |
| **RAGFlow** | QueryBuilder (synonym, weighted phrase) + kNN. Cách tính điểm khác nhau theo backend: ES/Infinity/OceanBase… | Trọng số vector + keyword phải có tổng bằng 1. Mặc định vector 0.3, threshold 0.2, có pagerank feature | Rerank bằng model (chỉ áp dụng ở page 1), field boost, đẩy child chunk lên parent |
| **LightRAG** | Graph + vector: entity/relation vector, mở rộng qua graph, thêm chunk vector. Các mode local/global/hybrid/**mix** (mặc định)/naive/bypass | **Không** phải BM25 hay RRF: xen kẽ round-robin rồi dedup. Ngân sách token: 6k entity, 8k relation, tổng 30k | Mặc định binding rerank là `null`, nên **thực tế không rerank** dù cờ đang bật |

Nhận xét (Synthesis): chỉ có WeKnora và RAGFlow làm hybrid lexical + dense đúng kiểu nền tảng doanh nghiệp. txtai có cách fusion linh hoạt nhất. LightRAG là hệ duy nhất đặt graph làm trục chính của retrieval. Nguồn: [txtai-retrieval](wiki/txtai-retrieval.md), [weknora-hybrid-retrieval](wiki/weknora-hybrid-retrieval.md), [ragflow-retrieval](wiki/ragflow-retrieval.md), [lightrag-retrieval](wiki/lightrag-retrieval.md).

## 4. Knowledge graph và "biên dịch" kiến thức

- **txtai:** Graph được suy ra từ độ tương đồng (similarity edges), không do LLM trích xuất. Có phát hiện cộng đồng (Louvain…) để tạo topic, và truy vấn kiểu openCypher. [txtai-graph](wiki/txtai-graph.md)
- **WeKnora:** Có 2 graph khác nhau.
  - Entity graph lưu trên Neo4j (tuỳ chọn). Khi truy vấn, nó kiểm tra lại các chunk được trích dẫn.
  - **Wiki tự động**: ingest/finalize bất đồng bộ, lưu lịch sử revision, có optimistic lock và trích citation từ chunk.

  Nguồn: [weknora-graph-multimodal-retrieval](wiki/weknora-graph-multimodal-retrieval.md), [weknora-wiki-compilation](wiki/weknora-wiki-compilation.md).
- **RAGFlow:** Knowledge compilation gồm 4 dạng: wiki, structure (hypergraph entity/relation), tree (kiểu RAPTOR), mindmap. Các bản dịch được gộp tăng dần ở cấp dataset và mặc định được đưa vào kết quả search. [ragflow-knowledge-compilation](wiki/ragflow-knowledge-compilation.md)
- **LightRAG:** LLM trích entity/relation cho từng chunk, có gleaning và tóm tắt mô tả khi merge. Trước khi merge có ghi recovery anchor, hỗ trợ xoá theo phần đóng góp của từng tài liệu và rebuild từ cache. [lightrag-extraction](wiki/lightrag-extraction.md), [lightrag-deletion](wiki/lightrag-deletion.md)

## 5. Agent và workflow

| | Agent | Workflow |
|---|---|---|
| txtai | Dùng smolagents (ToolCalling/Code agent). Tools có bash theo allowlist (docstring tự nhận là "not a sandbox"), MCP, skills. Memory chỉ nằm trong process | `Workflow` chạy task theo batch, có lập lịch |
| WeKnora | ReAct engine tự viết: mặc định 20 vòng lặp, có cơ chế phục hồi khi trả về rỗng, lặp lỗi, tràn context. Cho phép điều hướng giữa chừng. Có skills, sandbox và **memory xuyên session** (cần xác nhận khi lưu) | Hàng đợi tác vụ Asynq |
| RAGFlow | eino ReAct kết hợp agentic RAG: tool tra theo từ vựng/ngữ nghĩa, điều hướng qua knowledge đã compile | **Canvas DSL** có loop/parallel/interrupt/checkpoint, phát sự kiện SSE |
| LightRAG | Không có agent canvas. Wiki chưa ghi nhận runtime agent nào | Pipeline ingest qua các hàng đợi parse → analyze → process |

Nguồn: [txtai-agents-workflows](wiki/txtai-agents-workflows.md), [weknora-agent-runtime](wiki/weknora-agent-runtime.md), [weknora-memory](wiki/weknora-memory.md), [ragflow-agent-workflows](wiki/ragflow-agent-workflows.md).

## 6. Citation và provenance

- **txtai:** Chế độ `reference` chọn **một** context sau khi sinh câu trả lời, dựa trên similarity. Đây là heuristic, không phải grounding thật. [txtai-rag](wiki/txtai-rag.md)
- **WeKnora:** Message lưu lại reference của câu trả lời. Wiki được sinh từ citation gắn với chunk. Chunk giữ offset ký tự gốc trong tài liệu.
- **RAGFlow:** Có 2 cơ chế khác nhau.
  - Chat thường chèn `[ID:n]` bằng similarity giữa từng câu và chunk (ngưỡng hạ dần từ 0.63 xuống 0.3).
  - Agentic RAG dùng `EvidenceRegistry` với ID ổn định.

  Nguồn: [ragflow-citations](wiki/ragflow-citations.md).
- **LightRAG:** Danh sách reference được tạo từ các chunk còn lại sau lọc, nhóm theo file. Prompt chỉ *yêu cầu* LLM ghi citation, code không parse hay kiểm tra lại. [lightrag-query-contracts](wiki/lightrag-query-contracts.md)

## 7. Lưu trữ và vận hành

| | Lưu trữ | Triển khai |
|---|---|---|
| txtai | SQLite/DuckDB/client cho content, ANN lưu file, có archive và cloud. **Lưu ý:** `createtables` xoá dữ liệu bảng khi khởi tạo mới | pip với các extras, Docker (api/workflow/schedule), AWS Lambda |
| WeKnora | PostgreSQL/ParadeDB hoặc SQLite (bản Lite). Redis/Asynq, hoặc executor chạy trong process khi không có Redis | Compose, Helm (K8s ≥1.25), Lite, desktop qua Wails |
| RAGFlow | Tách thành nhiều tầng: MySQL/OceanBase (metadata), ES/Infinity/OceanBase… (chunks), MinIO/S3 (objects), Kvrocks (cache/lease), NATS (queue) | Compose. Cần build native (CGO, ONNX, pdfium) và tải asset/model riêng |
| LightRAG | 4 hợp đồng lưu trữ (KV/vector/graph/status). Mặc định là JSON+NanoVectorDB+NetworkX, README nói chỉ dành để test. PostgreSQL được khuyến nghị cho production | pip extras, Docker full/lite, Helm mặc định single-writer |

Nguồn: [txtai-persistence](wiki/txtai-persistence.md), [weknora-persistence](wiki/weknora-persistence.md), [ragflow-persistence](wiki/ragflow-persistence.md), [lightrag-storage](wiki/lightrag-storage.md), cùng các trang deployment/operations.

## 8. Bảo mật, multi-tenancy và MCP

| | Auth / tenancy | MCP | Phát hiện đáng chú ý |
|---|---|---|---|
| txtai | API **mở theo mặc định**. Nếu đặt `TOKEN` thì chỉ là một token dùng chung (lưu dạng SHA-256 digest). Không có role hay tenant | Có mount `/mcp`. Việc truyền auth qua MCP chưa rõ | Route đã tắt vẫn có thể bị gọi qua OpenAI selector. Config có thể nạp class Python tuỳ ý (config là đầu vào cần tin cậy) |
| WeKnora | **Mạnh nhất trong 4**: workspace RBAC (Owner/Admin/Contributor/Viewer), API key giới hạn theo scope, lọc kết nối outbound | Endpoint HTTP riêng cho từng workspace, có allowlist KB/tool và rate limit. Ngoài ra có server stdio cho CLI, còn server Python đã deprecated | Mặc định cho tự đăng ký tài khoản. Công tắc RBAC có thể tắt |
| RAGFlow | Quyền theo owner/tenant/shared, Community Edition | Có cả inbound (gắn với danh tính người gọi) và outbound (chống SSRF, pin DNS) | **Có private key nằm trong repo** (giá trị đã che). Credential mặc định trong config. Webhook công khai |
| LightRAG | Mặc định **không có auth**. Hỗ trợ API key/JWT dùng chung, **không** phân quyền theo user hay tài liệu. Route Ollama luôn nằm trong whitelist mở | Wiki chưa ghi nhận | Một file env mẫu trong repo chứa key có vẻ còn hoạt động (giá trị đã che) |

Nguồn: [txtai-security](wiki/txtai-security.md), [txtai-api](wiki/txtai-api.md), [weknora-security](wiki/weknora-security.md), [weknora-mcp-servers](wiki/weknora-mcp-servers.md), [ragflow-security](wiki/ragflow-security.md), [ragflow-mcp](wiki/ragflow-mcp.md), [lightrag-security](wiki/lightrag-security.md).

## 9. Nên chọn hệ nào (Synthesis)

- **txtai:** khi cần một thư viện nhẹ để nhúng vào ứng dụng Python, tự lắp pipeline và fusion. Phần auth, tenancy và UI bạn phải tự làm.
- **WeKnora:** khi cần nền tảng đa workspace có RBAC, agent ReAct, memory, wiki tự động, kết nối nguồn dữ liệu ngoài và MCP theo scope. Có bản Lite nếu không muốn chạy Redis/Postgres.
- **RAGFlow:** khi trọng tâm là parse tài liệu phức tạp (DeepDoc) và agent canvas trực quan. Đổi lại hạ tầng nặng nhất (MySQL+ES+Kvrocks+NATS+MinIO) và cần xử lý phát hiện private key trước khi triển khai.
- **LightRAG:** khi cần retrieval dựa trên graph và mô hình RAG gọn nhẹ. Phải tự bổ sung auth/tenancy, cấu hình reranker và chọn backend lưu trữ cho production.

## Giới hạn

- Wiki không có số đo chất lượng hay hiệu năng cho hệ nào. Mọi tuyên bố kiểu "tốt hơn" trong README đều chỉ là Reported.
- MCP của LightRAG và phần lớn adapter connector/provider chưa được ghi vào wiki. "Không thấy" chỉ có nghĩa là chưa compile, không có nghĩa là không tồn tại.
- `stale_after` đặt vào khoảng 2027-01-24/26, sau thời điểm đó cần ingest lại.

Tôi chưa lưu bảng so sánh này vào wiki. Nếu bạn muốn, tôi có thể lưu thành một trang `type: Synthesis` (ví dụ `wiki/rag-platform-comparison.md`) qua `wiki-ingest`.

## Parser và chunking: hệ nào hoàn thiện nhất?

**RAGFlow có phần parser hoàn thiện nhất. Chunking thì WeKnora được thiết kế kỹ nhất, còn LightRAG mạnh nhất ở chỗ mỗi tài liệu được cấu hình riêng và có xử lý multimodal.** txtai đứng cuối vì nó là bộ công cụ để tự lắp, không phải pipeline làm sẵn.

Lưu ý: đây là đánh giá về độ đầy đủ của cơ chế, dựa trên việc đọc code (Synthesis). Wiki không có benchmark chất lượng parse hay chunk nào, nên "xịn" ở đây không phải là kết quả đã đo.

### Xếp hạng

| Hạng | Parser | Chunking |
|---|---|---|
| 1 | **RAGFlow** | **WeKnora** |
| 2 | **LightRAG** | **LightRAG** ≈ **RAGFlow** |
| 3 | **WeKnora** | |
| 4 | **txtai** | **txtai** |

### Lý do

**RAGFlow: parser mạnh nhất** ([ragflow-ingestion](wiki/ragflow-ingestion.md))
- DeepDoc chạy ngay trong hệ thống (native): xử lý PDF theo từng trang, dựng layout, có OCR và nhận diện bảng.
- Không cần gọi service parser bên ngoài.
- Hỗ trợ nhiều họ định dạng nhất: PDF, Office, CSV, HTML, MD, EPUB, JSON, email, hình ảnh, âm thanh.
- Có nhiều loại chunker: general, page, hierarchy, table, QA, manual, title. Có parent chunk ẩn để mở rộng ngữ cảnh, và Extractor bổ sung keyword, câu hỏi, tóm tắt.
- Hạn chế:
  - Wiki chưa đọc hết cách hoạt động của từng chunker.
  - Lỗi parse với định dạng đã biết sẽ bị đẩy lên thành lỗi, không tự fallback.
  - Phải build native và tải model/asset riêng.

**WeKnora: chunking chặt chẽ nhất** ([weknora-document-ingestion](wiki/weknora-document-ingestion.md))
- Chế độ `auto` phân tích cấu trúc tài liệu, thử chia theo heading hoặc heuristic, rồi fallback về splitter cũ.
- `ValidateChunks` loại các kết quả hỏng: chunk rỗng, quá nhỏ, quá lớn, hoặc cả tài liệu dài chỉ thành một chunk.
- Không cắt ngang code, công thức toán, link/ảnh Markdown và bảng.
- Giữ offset gốc của chunk. Breadcrumb heading được ghép riêng vào lúc embedding, không làm thay đổi đoạn văn bản gốc.
- Có parent/child (4096/384).
- Hạn chế:
  - Giới hạn token chỉ ước lượng theo số ký tự (hệ số an toàn 0.9), không tokenize thật.
  - Parser trong phạm vi đã đọc chỉ có builtin, MarkItDown và OpenDataLoader. Các converter MinerU/PaddleOCR/AnyDoc chưa được đọc.

**LightRAG: linh hoạt và multimodal tốt nhất** ([lightrag-chunking](wiki/lightrag-chunking.md), [lightrag-parsing-multimodal](wiki/lightrag-parsing-multimodal.md))
- Mỗi file chọn được engine (native/legacy/MinerU/Docling) và chiến lược chunk F/R/V/P. Tham số được lưu cố định lúc enqueue, nên có thể parse lại đúng như lần đầu.
- Chiến lược P dùng sidecar cấu trúc để giữ heading, đoạn văn và bảng.
- Image, table và equation được phân tích bằng VLM hoặc LLM, có kèm ngữ cảnh xung quanh. Có kiểm soát đường dẫn ảnh và giới hạn kích thước.
- Hạn chế:
  - Muốn parse PDF tốt phải có service MinerU hoặc Docling bên ngoài.
  - Fallback nhiều tầng (V → R, P → R) có thể âm thầm làm giảm chất lượng.
  - Không phải chunk nào cũng có vị trí gốc (source span).

**txtai: thấp nhất** ([txtai-pipelines](wiki/txtai-pipelines.md))
- Phần parse giao cho Tika, Docling hoặc LiteParse rồi chuyển về Markdown.
- Mọi splitter đều tắt theo mặc định. Chunk theo ngữ nghĩa phải dùng Chonkie.
- `minlength` chỉ đếm ký tự, và không có cơ chế lưu vị trí trang (page provenance).

### Chọn theo nhu cầu (Synthesis)
- **Nhiều PDF scan hoặc bảng phức tạp, muốn mọi thứ chạy sẵn trong hệ thống:** RAGFlow.
- **Cần chunk ổn định, có kiểm tra, giữ cấu trúc Markdown/code/bảng và giữ offset:** WeKnora.
- **Cần cấu hình riêng cho từng file và mô tả ảnh/bảng/công thức bằng VLM:** LightRAG, đi kèm MinerU hoặc Docling.

Nếu muốn có câu trả lời "xịn nhất" dựa trên số đo thật, cần chạy cùng một bộ tài liệu qua cả 4 hệ, rồi đo độ chính xác của bảng/OCR và chất lượng retrieval (ví dụ dùng [Ragas](wiki/ragas.md)). Wiki chưa có kết quả đo nào như vậy.


# Độ hoàn thiện của pipeline retrieval và ranking

**Ngắn gọn:** nếu xét độ hoàn thiện của pipeline retrieval và ranking từ đầu đến cuối, **WeKnora** đứng đầu, **RAGFlow** sát ngay sau. Còn "xịn nhất" về chất lượng kết quả thì wiki không trả lời được: chưa hệ nào được benchmark, chỉ có đọc code tại commit đã ghi. Đánh giá dưới đây là **Synthesis**, dựa trên việc cơ chế nào có mặt và được làm kỹ đến đâu.

### Chấm theo từng tiêu chí

| Tiêu chí | txtai | WeKnora | RAGFlow | LightRAG |
|---|---|---|---|---|
| Lexical + dense hybrid | ✅ BM25/TF-IDF/neural sparse + ANN | ✅ vector + keyword theo từng store | ✅ full-text + kNN | ❌ không có lexical, chỉ graph + vector |
| Hiểu truy vấn | `+required`/`-prohibited`, SQL | — | ✅ **mạnh nhất**: synonym, weighted phrase | ✅ LLM tách keyword high/low-level |
| Fusion | ✅ **linh hoạt nhất**: Bayesian log-odds / convex / RRF | ✅ weighted RRF đã chuẩn hoá (k=60, 0.7/0.3) | Trọng số vector/keyword, tính lại điểm theo từng engine | ⚠️ round-robin rồi dedup, không phải score fusion |
| Rerank mặc định | ❌ là pipeline riêng, phải tự gắn | ✅ có, lỗi thì giữ thứ tự cũ | ✅ model rerank, field weights, pagerank | ⚠️ cờ bật nhưng binding mặc định `null`, nên thực tế không rerank |
| Hậu xử lý ranking | — | ✅ **đầy đủ nhất**: composite score (0.6 model / 0.3 retrieval / 0.1 source), **MMR** (λ 0.7), nới threshold có kiểm soát | ✅ đẩy child chunk lên parent, cắt tỉa, chạy lại khi rỗng | ✅ ngân sách token theo từng tầng (6k/8k/30k) |
| Nhiều KB / multi-tenant | — | ✅ phân phối truy vấn qua nhiều KB, chặn trộn embedding model khác nhau | ✅ lọc theo tenant/dataset | Theo workspace |
| Chịu lỗi | — | ✅ phân biệt lỗi một phần với lỗi toàn bộ engine | Fallback sang dense có điều kiện | Rerank lỗi thì giữ thứ tự cũ |
| Graph / compiled knowledge | Graph similarity + Cypher | Graph Neo4j có kiểm tra lại chunk | ✅ đưa wiki/tree/structure đã compile vào search | ✅ **graph là trục chính** |
| Số backend | ✅ **nhiều nhất** (~12 ANN) | Nhiều, nhưng mới audit một phần | 6 document engine | Nhiều storage |

### Kết luận

1. **WeKnora: pipeline ranking hoàn chỉnh nhất.** Chuỗi xử lý là fan-out → RRF chuẩn hoá → rerank → composite score → MMR → fallback có kiểm soát. Nó cũng xử lý lỗi từng phần và chặn trộn embedding model khác nhau giữa các KB. Đây là chuỗi ranking production đầy đủ nhất trong 4 hệ. [weknora-hybrid-retrieval](wiki/weknora-hybrid-retrieval.md)
   - Bẫy cần biết: đặt trọng số = 0 **không** tắt được retriever.
   - Muốn dùng keyword search trên PostgreSQL thì cần ParadeDB/pg_search.
2. **RAGFlow: mạnh nhất ở khâu trước và sau retrieval.** Khâu trước là query builder (synonym, weighted phrase). Khâu sau là parent-child promotion, đưa compiled knowledge vào kết quả và agentic retrieval nhiều bước. Điểm yếu là cách tính điểm khác nhau theo từng engine (ES/Infinity/OceanBase), nên cùng một trọng số không cho cùng một kết quả. [ragflow-retrieval](wiki/ragflow-retrieval.md)
3. **txtai: lý thuyết fusion hay nhất nhưng ở mức thư viện.** Nó có Bayesian log-odds fusion và nhiều backend ANN nhất. Tuy vậy rerank, MMR và multi-KB đều phải tự lắp. Lưu ý thêm: ý nghĩa của score (và các ngưỡng như `minscore`) thay đổi theo strategy fusion. [txtai-retrieval](wiki/txtai-retrieval.md)
4. **LightRAG: khác hạng, không cùng loại.** Ranking cổ điển yếu nhất: không có BM25, fusion là round-robin, và mặc định không rerank. Bù lại nó là hệ duy nhất lấy graph làm trung tâm, với cách lắp context theo ngân sách token rất chặt. Hệ này phù hợp với câu hỏi tổng hợp hoặc nhiều thực thể, không phải tìm passage chính xác. [lightrag-retrieval](wiki/lightrag-retrieval.md)

### Gợi ý chọn

- Cần tìm passage chính xác trên nhiều KB, chạy production: **WeKnora**, hoặc **RAGFlow** nếu tài liệu phức tạp.
- Cần thử nghiệm và tinh chỉnh fusion: **txtai**.
- Cần câu trả lời tổng quan, liên kết nhiều thực thể: **LightRAG**, và nên bật reranker.

Muốn biết hệ nào thực sự "xịn" hơn cần benchmark cùng một tập dữ liệu, ví dụ đo context precision/recall bằng [Ragas](wiki/ragas-rag-metrics.md). Wiki hiện chưa có kết quả như vậy.

## Graph tri thức và biên dịch kiến thức: hệ nào hoàn thiện nhất?

**Không có hệ nào hơn hẳn trên mọi mặt.** Wiki cũng chưa có số đo chất lượng nào (độ chính xác khi trích entity, chất lượng trang wiki sinh ra, khả năng mở rộng), nên chỉ so được độ hoàn thiện của cơ chế trong code, chưa so được chất lượng đầu ra. Chia theo từng mặt thì khá rõ:

| Tiêu chí | Đứng đầu | Lý do (Observed) |
|---|---|---|
| Graph dùng trực tiếp cho retrieval | **LightRAG** | Graph là trục chính khi truy vấn: các mode local/global/hybrid/mix, có ngân sách token riêng cho entity và relation |
| Vòng đời graph (cập nhật, xoá, khôi phục) | **LightRAG** | Ghi recovery anchor trước khi merge, xoá theo phần đóng góp của từng tài liệu, rebuild từ cache trích xuất, dữ liệu chỉ được coi là xong sau khi flush |
| Số loại sản phẩm biên dịch | **RAGFlow** | 4 loại: wiki, structure (hypergraph), tree (kiểu RAPTOR), mindmap. Gộp tăng dần ở cấp dataset |
| Đưa kết quả biên dịch vào retrieval và agent | **RAGFlow** | Mặc định dataset search có cả các dòng đã biên dịch. Agentic RAG thêm tool điều hướng và graph khi có sản phẩm biên dịch |
| Quản lý wiki (revision, chạy song song, an toàn khi ghi lại) | **WeKnora** | Revision có optimistic lock, giữ 50 bản (tối đa 200). Từ chối ghi đè nếu mất quá 20% số dòng bảng. Lane ingest/finalize bền vững, có dead-letter. Có lint (orphan, broken link, duplicate slug) |
| Kiểm tra bằng chứng khi truy vấn graph | **WeKnora** | Kiểm tra lại từng chunk được trích (còn tồn tại, đang bật, đúng KB/tài liệu) trước khi dùng |
| — | **txtai** (yếu nhất ở mảng này) | Graph chỉ suy ra từ độ tương đồng embedding, không do LLM trích entity/relation. Không có biên dịch kiến thức. Có community topic và truy vấn openCypher, hợp cho phân tích hơn là xây tri thức |

### Chi tiết từng hệ

**LightRAG: knowledge graph hoàn thiện nhất.**
- LLM trích entity/relation, có gleaning và chuẩn hoá. Merge vào graph và vector store cùng lúc, tóm tắt mô tả kiểu map/reduce, có giới hạn số nguồn.
- Điểm mạnh nhất là phần thường bị bỏ qua: xoá hoặc làm lại một tài liệu mà không làm hỏng graph, và khôi phục sau khi ghi dở.
- Điểm yếu:
  - Không sinh sản phẩm dạng wiki, cây hay mindmap.
  - Mô tả entity có thể bị cắt bớt. Trọng số relation là phép cộng dồn, không phải xác suất đúng.
  - Graph và vector được ghi bằng hai thao tác riêng, không có transaction chung.
- Nguồn: [lightrag-extraction](wiki/lightrag-extraction.md), [lightrag-deletion](wiki/lightrag-deletion.md), [lightrag-retrieval](wiki/lightrag-retrieval.md).

**RAGFlow: biên dịch kiến thức rộng nhất.**
- Một pipeline biên dịch ra nhiều dạng: wiki (map → reduce → lên kế hoạch trang → tinh chỉnh), hypergraph lọc self-loop, cây RAPTOR, mindmap.
- Lập lịch ở cấp dataset (MySQL + NATS) có xử lý khi tài liệu bị gỡ và chỉ cập nhật các trang bị ảnh hưởng.
- Điểm yếu: wiki chưa ghi nhận revision hay cơ chế chống ghi đè như WeKnora. Chất lượng graph và wiki sinh ra chưa được đo.
- Nguồn: [ragflow-knowledge-compilation](wiki/ragflow-knowledge-compilation.md).

**WeKnora: wiki tự động được làm kỹ nhất về vận hành.**
- Xử lý nhiều tài liệu cùng lúc mà vẫn hội tụ về một trang: claim dòng không chồng lấn, khoá theo slug, giữ chỗ danh tính 2 giờ để các slug khác nhau của cùng một thực thể gộp về một trang.
- Citation trích từ chunk, có link graph giữa các trang.
- Điểm yếu: entity graph (Neo4j) và trang wiki là hai hệ tách rời. Phần trích graph và truy vấn Neo4j chưa được đọc kỹ.
- Nguồn: [weknora-wiki-compilation](wiki/weknora-wiki-compilation.md), [weknora-graph-multimodal-retrieval](wiki/weknora-graph-multimodal-retrieval.md).

### Kết luận (Synthesis)

- **GraphRAG đúng nghĩa** (graph phục vụ trả lời câu hỏi): chọn **LightRAG**.
- **Biên dịch thành nhiều dạng tri thức và dùng lại trong agent**: chọn **RAGFlow**.
- **Wiki tự động chạy ổn định lâu dài, nhiều người hoặc agent cùng sửa**: chọn **WeKnora**.
- Nếu bắt buộc chọn một hệ "toàn diện nhất" cho cả graph lẫn biên dịch thì là **RAGFlow**, vì nó có cả hypergraph lẫn wiki, tree, mindmap và nối thẳng vào retrieval. Nhưng graph của nó chưa có cơ chế xoá và khôi phục như LightRAG, còn wiki chưa có revision như WeKnora.

Mọi nhận định trên đều từ đọc code tĩnh, các trang vẫn ở trạng thái `draft`. Cách duy nhất để biết hệ nào "xịn" về chất lượng là chạy benchmark trên cùng một bộ tài liệu, ví dụ bằng [Ragas](wiki/ragas.md).


## Agent và workflow: hệ nào hoàn thiện nhất?

Không có một hệ thắng tuyệt đối. Kết quả tách làm hai:

- **Workflow** (lắp quy trình bằng canvas, rẽ nhánh, loop, parallel, dừng chờ người dùng): **RAGFlow** mạnh nhất.
- **Agent runtime** (một agent chat chạy bền, có memory, skills, sandbox, cơ chế phục hồi): **WeKnora** mạnh nhất.

LightRAG không có agent. txtai chỉ có lớp mỏng bọc smolagents.

Lưu ý: wiki chỉ dựa trên việc đọc code, không chạy agent nào và không đo chất lượng. "Hoàn thiện" ở đây là độ đầy đủ của tính năng và thiết kế, không phải agent nào trả lời tốt hơn.

### Xếp hạng

| Hạng | Hệ | Điểm mạnh | Điểm yếu |
|---|---|---|---|
| 1 (đồng hạng) | **RAGFlow** | Canvas DSL biên dịch thành graph chạy được. Có loop/parallel, interrupt/checkpoint/resume, chờ người dùng (`waiting_for_user`). Phát sự kiện SSE theo từng node. Nhiều component: LLM/Agent, retrieval, switch, code, browser, xử lý dữ liệu. Agentic RAG có tool điều hướng qua knowledge đã compile, citation dùng `EvidenceRegistry`. Có quản lý version, publish, webhook, API tương thích OpenAI | Code execution và browser chưa được chứng minh có sandbox. Webhook công khai. Có một thư viện `internal/harness` (subagent, replay, metrics) nhưng **không được nối vào runtime đang chạy** |
| 1 (đồng hạng) | **WeKnora** | ReAct engine tự viết, phòng thủ kỹ: mặc định 20 vòng lặp, thử lại khi trả về rỗng, phát hiện lặp lỗi, giới hạn số lần bị cắt do `length`, tự compact khi tràn context, cho phép điều hướng giữa chừng. Timeout riêng cho từng tool. Skills chỉ nạp khi cần (3 cấp). Sandbox gắn với session, có checkpoint Git cho rewind/fork. **Memory xuyên session** cần xác nhận trước khi lưu. Tool bị chặn theo khả năng của KB | Không có workflow canvas. Workflow chỉ là hàng đợi nền. Sandbox Docker chạy bằng root, mount docker socket tương đương quyền root trên host. Phần approval/HITL chưa được review |
| 3 | **txtai** | Có cả `Agent` (smolagents, ToolCalling hoặc Code) và `Workflow` (task theo batch, lịch cron). Tool đa dạng: bash, file, web, MCP, skills Markdown | Logic agent nằm trong smolagents, txtai không tự xử lý. Memory chỉ trong process và mặc định tắt. Allowlist bash tự ghi là "not a sandbox". Workflow không có queue bền, không replay khi crash |
| 4 | **LightRAG** | Không áp dụng | Wiki không ghi nhận runtime agent hay workflow canvas nào. Chỉ có pipeline ingest |

### Chọn theo nhu cầu (Synthesis)

- **Muốn dựng quy trình trực quan**, có nhiều bước cố định và nhánh điều kiện, rồi publish thành app hoặc webhook: chọn **RAGFlow**. Đây là hệ duy nhất trong 4 có canvas đầy đủ với checkpoint và interrupt.
- **Muốn một trợ lý agent** chat lâu dài, nhớ người dùng, chạy skill hay code trong workspace riêng, tự phục hồi khi model trả lời lỗi: chọn **WeKnora**. Phần runtime và phân quyền theo workspace của nó chặt chẽ hơn.
- **Muốn nhúng agent vào code Python** của riêng bạn: chọn **txtai**, nhưng phải tự lo sandbox và việc lưu trạng thái.

Nếu bắt buộc chọn một hệ "hoàn thiện nhất" tổng thể, tôi nghiêng về **RAGFlow**, vì nó có cả agent (eino ReAct + agentic RAG) lẫn workflow engine. WeKnora chỉ mạnh về agent. Nếu ưu tiên vận hành an toàn cho nhiều người dùng thì WeKnora đáng tin hơn.

### Chưa xác minh

Chưa hệ nào được chạy end-to-end. Cũng chưa kiểm tra HITL/approval của WeKnora, mức cô lập của code tool trong RAGFlow, hay chất lượng suy luận nhiều bước của cả hai.

Nguồn: [ragflow-agent-workflows](wiki/ragflow-agent-workflows.md), [ragflow-harness](wiki/ragflow-harness.md), [weknora-agent-runtime](wiki/weknora-agent-runtime.md), [weknora-skills-sandboxes](wiki/weknora-skills-sandboxes.md), [weknora-memory](wiki/weknora-memory.md), [txtai-agents-workflows](wiki/txtai-agents-workflows.md).