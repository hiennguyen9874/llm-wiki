# Super-RAG: chọn nền tảng và lộ trình phát triển

## Tóm tắt quyết định

**Đề xuất: fork WeKnora, giữ một hệ thống sở hữu lifecycle và nâng cấp có chọn lọc.** Không ghép nguyên runtime của nhiều ứng dụng chỉ để có thêm tính năng.

Với giả định sản phẩm là kho tri thức cho nhóm hoặc doanh nghiệp, ba khoản đầu tư đầu tiên nên là:

1. **Eval, retrieval trace và security baseline:** biết hệ thống sai ở đâu trước khi thay thuật toán.
2. **Table/token-aware ingestion và lexical retrieval theo domain:** cải thiện tài liệu đầu vào và khả năng tìm đúng bằng chứng.
3. **Sync recovery; thêm source ACL nếu sản phẩm cần phân quyền theo tài liệu.**

Embedding migration, multimodal enrichment và graph retrieval nâng cao đến sau, khi dữ liệu thực tế chứng minh nhu cầu. Đây là **Synthesis — đề xuất thiết kế**, không phải kết quả benchmark hay một fork đã được triển khai. Cơ sở tổng hợp: [WeKnora selective fork roadmap](../wiki/weknora-fork-roadmap.md).

## 1. Vì sao chọn WeKnora làm nền?

WeKnora phù hợp với hướng sản phẩm này vì đã có các lớp ứng dụng cần giữ chung: workspace, RAG, agent, auto-wiki và các kênh tích hợp. Backend là Go/Gin, lắp ghép qua Dig; parsing có thể đi qua Python docreader. Standard và Lite chọn persistence/queue khác nhau thay vì tách thành hai ứng dụng nghiệp vụ. Đây là ranh giới mở rộng hữu ích, **không bảo đảm mọi tính năng mới chỉ cần cắm plugin**. [Kiến trúc](../wiki/weknora-backend-architecture.md)

Các cơ chế đã được wiki ghi nhận qua đọc code gồm adaptive/parent-child chunking, weighted RRF, rerank fallback, MMR và citation registry. Nên lấy chúng làm baseline để kiểm thử, thay vì xây lại từ đầu. [Ingestion](../wiki/weknora-document-ingestion.md) · [Retrieval](../wiki/weknora-hybrid-retrieval.md) · [Citation](../wiki/weknora-citations-source-boundary.md)

### Khi nào nên chọn nền khác?

| Nền tảng | Trường hợp đáng cân nhắc | Đánh đổi đã được wiki ghi nhận |
|---|---|---|
| **WeKnora** | Kho tri thức nhiều workspace, agent, auto-wiki và tích hợp ứng dụng | Cần kiểm chứng hardening, lifecycle và chất lượng trên corpus thật |
| **RAGFlow** | PDF phức tạp, chunker chuyên biệt, canvas workflow là yêu cầu trung tâm | Nhiều persistence plane, native assets và yêu cầu CGO |
| **OpenRAG** | Đã dùng OpenSearch/Langflow, cần tham khảo ACL từ nguồn đến retrieval | Phụ thuộc stack đó; backend ở snapshot có giới hạn một worker và auth cần hardening |
| **LightRAG** | Sản phẩm đặt graph/multi-hop làm lõi, hoặc cần engine trong Python | Không thay thế toàn bộ lớp quản trị ứng dụng của một knowledge platform |
| **txtai** | Xây pipeline riêng, semantic search nhúng/local hoặc thử nghiệm fusion | Là framework, không phải ứng dụng quản trị tri thức tương đương WeKnora |

Đây là đánh giá mức phù hợp từ [so sánh năm nền tảng](../wiki/rag-platform-comparison.md), không phải bảng xếp hạng chất lượng. Nếu tài liệu khó là yêu cầu số một, nên chạy WeKnora và RAGFlow trên cùng bộ regression trước khi chốt.

## 2. Những gì đã có: giữ lại, kiểm thử, không port trùng

Các đính chính dưới đây thay thế những giả định thiếu chính xác trong đề xuất ban đầu.

| Hạng mục | Bằng chứng đã được wiki ghi nhận | Hành động phù hợp |
|---|---|---|
| **Citation/evidence registry** | Có source handle theo request, khôi phục chunk gốc sau merge/expand, chuyển citation nội bộ thành citation công khai | Giữ implementation; test đúng identity, đúng nguồn và đúng nội dung hỗ trợ |
| **Untrusted-source boundary** | Có instruction coi tài liệu, web và tool result là dữ liệu không đáng tin | Audit renderer, escaping và tool authorization; không thêm wrapper trùng ngay |
| **Datasource sync** | Handler serialize cursor và gọi repository để lưu checkpoint; có trạng thái partial | Bổ sung durable retry cho từng item lỗi, không thay toàn bộ sync framework |
| **Xoá graph theo tài liệu** | Đường xoá đã gọi `DelGraph` theo document/KB namespace | Kiểm tra shared contribution, lỗi giữa các store và recovery |
| **Query expansion** | Có biến thể cục bộ như bỏ stopword, lấy cụm trích dẫn, tách segment và bỏ tiền tố câu hỏi tiếng Trung; chỉ bổ sung nhánh keyword | Mở rộng domain synonyms/phrase weighting nếu eval cho thấy thiếu recall |

Nguồn: [citation/source boundary](../wiki/weknora-citations-source-boundary.md), [sync](../wiki/weknora-datasource-sync.md), [graph deletion](../wiki/weknora-graph-multimodal-retrieval.md), [query expansion](../wiki/weknora-hybrid-retrieval.md).

**Giới hạn quan trọng:** registry bảo đảm identity/format không đồng nghĩa citation thực sự hỗ trợ mọi claim; prompt boundary không chứng minh chống được prompt injection; gọi API xoá graph không chứng minh xoá an toàn với entity dùng chung.

## 3. Những tính năng nên học từ dự án khác

Mọi mức ưu tiên dưới đây là **đề xuất**, cần acceptance test và ablation trước khi bật mặc định. “Học từ” nghĩa là tiếp thu thuật toán hoặc contract, không mặc định copy nguyên module.

| Mức | Hạng mục | Tham khảo | Cách đưa vào fork |
|---|---|---|---|
| **P0** | Eval, trace, security baseline | Ragas; grounded evaluation; controls hiện có của WeKnora | Harness riêng, trace được phân quyền/redact, baseline có thể tái lập |
| **P1** | Table-aware chunking và tokenizer-aware budget | RAGFlow; chunker hiện có của WeKnora | Mở rộng ingestion, giữ source locator |
| **P1** | Domain synonyms, phrase boost và field-aware ranking | RAGFlow | Mở rộng retriever theo backend; test tiếng Việt/Anh riêng |
| **P1** | Durable retry cho sync item/delete lỗi | RAGFlow sync contracts | Retry ledger trên queue/persistence của WeKnora |
| **P1 nếu enterprise** | Source ACL xuyên suốt retrieval và derived knowledge | OpenRAG | Thay đổi end-to-end, không chỉ thêm field vào document |
| **P2** | Embedding-space identity và migration có rollback | LightRAG, OpenRAG | Versioned index, backfill, validation và chuyển traffic có kiểm soát |
| **P2 nếu cần** | Enrichment riêng cho bảng, hình và công thức | LightRAG | Worker/sidecar có provenance, giới hạn chi phí và truy cập file |
| **P3** | Relation/global retrieval và contribution-safe graph recovery | LightRAG | Nhánh tùy chọn, chỉ bật khi multi-hop eval có lợi |
| **Thử nghiệm** | Semantic chunking, local rerank fallback, log-odds/convex fusion | LightRAG, RAGFlow, txtai | Feature flag và thí nghiệm từng biến |

Cơ sở cơ chế và locator được tập hợp tại [fork roadmap — priorities and acceptance gates](../wiki/weknora-fork-roadmap.md#product-priorities-and-acceptance-gates).

### 3.1. Parsing và chunking: ưu tiên chất lượng đầu vào

WeKnora đã có parser routing/fallback, chunk validation, protected spans cho code/math/table, parent-child và source rune offsets. Tuy nhiên, token limit hiện dựa vào ước lượng ký tự theo ngôn ngữ với safety factor, **không phải exact tokenizer**. Coverage của nhiều format parser và OCR/VLM còn pending; chưa đủ cơ sở kết luận parsing/OCR “đã đủ”. [Nguồn](../wiki/weknora-document-ingestion.md)

Đề xuất bổ sung:

- **Table chunker:** chia bảng lớn theo nhóm dòng, lặp header, giữ caption và locator; test bảng nhiều trang, ô gộp và bảng có nội dung dài.
- **Tokenizer-aware budget:** tính theo embedding model; ghi rõ fallback nếu không có tokenizer tương thích. Budget context trả lời phải tính riêng cả instruction, history, query, tool/source wrapper và phần dành cho output.
- **Chunk lineage:** lưu document version, parser/chunker/options version và content identity để giải thích khác biệt sau re-ingest.
- **Regression corpus:** PDF scan, tài liệu hai cột, bảng lớn, code, công thức, tiếng Việt/Anh và file lỗi.

Không dùng riêng `{doc_id}-chunk-{order}` làm bảo đảm citation ổn định: chèn nội dung có thể làm thay đổi toàn bộ thứ tự. Contract mới nên phân biệt document version, content identity và source locator. [Cơ sở thiết kế](../wiki/weknora-fork-roadmap.md#implementation-shape-one-owner-for-lifecycle-and-authorization)

**Multimodal là bước có điều kiện:** chỉ thêm phân tích sidecar bảng/hình/công thức khi bộ eval chứng minh OCR/text hiện tại bỏ mất thông tin cần tìm. Worker phải giữ provenance, kiểm tra đường dẫn/loại/kích thước ảnh và giới hạn VLM cost. Không đưa DeepDoc vào mặc định chỉ để mở rộng danh sách parser. [Roadmap](../wiki/weknora-fork-roadmap.md)

### 3.2. Retrieval và reranking: sửa candidate trước

WeKnora đã có normalized weighted RRF, fan-out nhiều store, xử lý kết quả từng phần, rerank fallback và MMR. Query expansion hiện có không phải domain-synonym expansion; hỗ trợ riêng cho tiếng Việt chưa được xác lập. [Nguồn](../wiki/weknora-hybrid-retrieval.md)

Thứ tự đề xuất:

1. Từ điển theo workspace/KB: viết tắt, tên sản phẩm, tên cũ/mới, thuật ngữ Việt/Anh.
2. Phrase boost và trọng số cho title, keyword, generated question, content, tùy schema/backend hỗ trợ.
3. Local rerank fallback nếu bản Lite/offline hoặc lỗi model là tình huống quan trọng.
4. Passage splitting và final-context budget nếu trace cho thấy evidence bị cắt mất.
5. Sau cùng mới thử semantic splitting hoặc fusion khác RRF.

**Reranker không cứu được tài liệu chưa vào candidate set.** Vì vậy cần tách phép đo candidate recall khỏi rerank quality. Không copy nguyên tokenizer/query DSL của RAGFlow: cùng Go chỉ giảm một phần công sức, không làm storage schema và score semantics tương thích. [Cơ sở đề xuất](../wiki/weknora-fork-roadmap.md)

### 3.3. Sync: không để checkpoint che mất item lỗi

Theo code đã được wiki tổng hợp, WeKnora tiếp tục xử lý khi có lỗi ingest từng item; run có thể là partial. Lỗi xoá thông thường chỉ được thử lại ở lần full sync sau. Cursor đã được lưu, nhưng chưa xác lập durable failed-item replay. [Nguồn](../wiki/weknora-datasource-sync.md)

Contract đề xuất:

> Chỉ advance checkpoint khi item đã thành công, hoặc việc retry item đó đã được ghi bền vững.

Cần có retry ledger cho create/update/delete, idempotency key theo source/document/version, phân loại lỗi tạm thời/quyền/nội dung, và UI hiển thị partial cùng item lỗi. Test crash tại các điểm fetch → ingest → ghi retry → checkpoint. Mục tiêu là không phải full-sync cả kho chỉ để thử lại vài lần xoá lỗi. Đây là phần nên học từ sync contracts của RAGFlow, **không phải lý do nhập thêm NATS/Kvrocks vào WeKnora**. [Roadmap](../wiki/weknora-fork-roadmap.md)

### 3.4. ACL: bao phủ cả tri thức dẫn xuất

Nếu làm enterprise search, đưa source ACL lên trước graph nâng cao và multimodal. OpenRAG là mẫu tham khảo cho ACL propagation; việc này không chứng minh mọi downstream surface của nó đã giải quyết đầy đủ. [Cơ sở](../wiki/weknora-fork-roadmap.md#authorization-must-cover-derived-knowledge)

Trong fork, phải kiểm tra quyền ở các đường:

- Chunk search, source resolution, document/image download.
- Agent tools và MCP.
- Answer cache, conversation replay và revocation.
- Auto-wiki và entity/relation hợp nhất từ nhiều nguồn.

Ví dụ thiết kế: wiki page tổng hợp một tài liệu chung và một tài liệu chỉ HR được đọc không được mặc nhiên hiển thị cho mọi người. Hoặc compile theo nhóm quyền tương thích, hoặc giữ/enforce contribution provenance; nếu chưa bảo đảm, tắt derived surface đó cho corpus trộn ACL.

Đây là **yêu cầu phòng ngừa suy ra từ kiến trúc**, không phải kết luận đã tái hiện lỗ hổng. Không được đánh đổi quyền truy cập lấy recall.

### 3.5. Embedding và graph: nâng cấp sau khi có baseline

WeKnora hiện từ chối multi-KB search khi embedding model khác nhau. Không bỏ guard rồi trộn vector. Thiết kế migration nên tạo space/index mới, backfill, kiểm tra chất lượng, chuyển traffic và giữ rollback; dùng LightRAG/OpenRAG làm tham khảo về compatibility và nhiều space. [Retrieval hiện có](../wiki/weknora-hybrid-retrieval.md) · [Roadmap migration](../wiki/weknora-fork-roadmap.md)

Với graph, chỉ thêm relation-vector/global retrieval nếu câu hỏi multi-hop đủ quan trọng và lợi ích lớn hơn chi phí extraction/query. Trước đó phải test việc xoá một nguồn vẫn giữ đúng contribution của các nguồn còn lại. Chưa có bằng chứng end-to-end cho semantics này trong phần WeKnora đã đọc. [Graph boundaries](../wiki/weknora-graph-multimodal-retrieval.md)

## 4. Kiến trúc fork: một chủ sở hữu lifecycle

Sơ đồ dưới đây là **đề xuất mở rộng**, không phải mô tả một fork đã có:

```text
WeKnora UI / API / Agent / MCP
              │
    Identity + Authorization
              │
    Retrieval orchestration
      ├─ Keyword / Vector
      ├─ Optional graph branch
      ├─ Fusion / Rerank
      └─ Context budget + existing citation registry
              │
    WeKnora metadata / jobs / indexes
              ▲
    Ingestion orchestration
      ├─ Parser adapters
      ├─ Table/token-aware chunking
      └─ Optional Python/native enrichment worker
```

Nguyên tắc triển khai:

1. **WeKnora sở hữu document identity, quyền, job state và citation chuẩn.**
2. Thuật toán nhẹ triển khai trong Go; model/native runtime nặng cô lập sau worker/service boundary khi cần.
3. Không mặc định gọi nguyên LightRAG server trong mỗi query, tránh tạo thêm lifecycle document/index/cache/delete độc lập.
4. Mỗi cơ chế có feature flag, fallback và contract test; sidecar không được tự tạo nguồn dữ liệu ngoài kiểm soát quyền.
5. Giữ extension wiring nhỏ, tránh đổi tên/di chuyển file upstream không cần thiết.
6. Nếu hỗ trợ cả PostgreSQL và Lite SQLite, duy trì migration/test tương ứng.

Cơ sở: [kiến trúc hiện có](../wiki/weknora-backend-architecture.md) và [implementation contracts đề xuất](../wiki/weknora-fork-roadmap.md#implementation-shape-one-owner-for-lifecycle-and-authorization).

## 5. Lộ trình và điều kiện phát hành

### Release 1 — Baseline an toàn, nhìn được lỗi

- Pin upstream, model, parser options và cấu hình triển khai; thử restore/rollback.
- Chọn registration mode phù hợp, xác nhận RBAC được enforce, giữ JWT/AES key bền vững.
- Không mount Docker socket nếu không cần; đặt egress/allowlist cho các dependency hợp lệ.
- Trace candidate → fusion → rerank → **context thật đưa vào model** → citation.
- Test citation hiện có, truy cập chéo tenant, tool capability và prompt injection.

Ở snapshot được tổng hợp, `SYSTEM_AES_KEY` yêu cầu đúng **32 byte dữ liệu chuỗi môi trường**, không phải chuỗi hex được tự decode. Trace cũng cần phân quyền, redaction và retention; không biến debug thành kho tài liệu nhạy cảm. [Configuration](../wiki/weknora-configuration.md) · [Security](../wiki/weknora-security.md)

### Release 2 — Chất lượng tài liệu và tìm kiếm

Table chunker, tokenizer budget, domain synonyms và field boosts. Chỉ thêm local fallback hoặc thay fusion khi ablation cho thấy có lợi.

### Release 3 — Dữ liệu sống và enterprise

Durable item/deletion retry, connector sản phẩm thực sự cần, source ACL và permission-safe wiki/graph/cache. Nếu ACL là điều kiện bắt buộc của sản phẩm, phần này phải hoàn tất trước khi đưa dữ liệu enterprise vào sử dụng.

### Release 4 — Nâng cao có điều kiện

Embedding migration, multimodal enrichment và graph retrieval dựa trên nhu cầu đã đo. Chưa ưu tiên thêm database, canvas mới hoặc một agent runtime thứ hai. Trình tự này theo [roadmap tổng hợp](../wiki/weknora-fork-roadmap.md#evaluation-and-delivery-sequence), không gắn với ước lượng thời gian chưa có cơ sở.

### Điều kiện để merge

| Nhóm | Cần đo hoặc kiểm thử |
|---|---|
| Retrieval | Recall/ranking trên held-out set; tách candidate retrieval khỏi reranking |
| Answer | Correctness, support từ context thật và abstention khi thiếu bằng chứng |
| Citation | Đúng source identity, locator và nội dung hỗ trợ claim |
| Operations | p50/p95 latency, model cost, ingestion failure, crash recovery, update/delete |
| Security | Không lộ dữ liệu qua tenant, tool, cache, conversation hay derived knowledge |

Giữ cố định metric API, judge model, prompt, split và invalid-score policy khi so sánh. [Ragas metrics](../wiki/ragas-rag-metrics.md) cung cấp cơ chế đo, nhưng **faithfulness chỉ đo nhất quán với context, không đồng nghĩa sự thật độc lập**. [Grounded evaluation](../wiki/grounded-accuracy-evaluation.md) bổ sung closed-book/oracle controls và kiểm tra trace/checker; các số liệu vendor trong nguồn đó không phải mục tiêu hiệu năng cho fork.

## 6. License và giới hạn bằng chứng

- Bản tổng hợp này dựa trên wiki ở các snapshot: WeKnora `fd7a2586fd58`, RAGFlow `1731e54b3aa0`, OpenRAG `6fc819d3ec10`, LightRAG `aaebfe1bb8d5`, txtai `738aac498ccb`, Ragas `298b68274234`. Không suy rộng sang phiên bản mới hơn. [Nguồn và revision](../wiki/weknora-fork-roadmap.md)
- Phần lớn bằng chứng là **Observed qua đọc code được wiki ghi nhận**, với coverage từng phần và không đồng đều; các ưu tiên và kiến trúc là **Synthesis**. “Chưa xác lập” không có nghĩa tính năng không tồn tại.
- Lần biên tập này chỉ đối chiếu các trang wiki, **không nghiên cứu raw mới, không chạy ứng dụng, upstream test, model hay benchmark**. Vì vậy chưa chứng minh được chất lượng, latency, scale, chống prompt injection hoặc isolation end-to-end.
- Theo metadata đã tổng hợp, WeKnora/LightRAG dùng MIT; RAGFlow/OpenRAG/txtai dùng Apache-2.0. Tuy nhiên phải audit từng file/component và dependency trước khi tái sử dụng, giữ notice/attribution và nghĩa vụ tương ứng. Viết lại không tự động thay thế license review; tài liệu này không phải kết quả audit pháp lý. [So sánh license](../wiki/rag-platform-comparison.md#positioning) · [Giới hạn roadmap](../wiki/weknora-fork-roadmap.md#evidence-and-coverage-limits)

**Kết luận:** xây một fork truy vết được, phục hồi được và giữ đúng quyền trước; thêm thuật toán sau. Mục tiêu không phải có nhiều tính năng nhất, mà là biết mỗi thay đổi cải thiện điều gì, đánh đổi gì và có thể rollback thế nào.
