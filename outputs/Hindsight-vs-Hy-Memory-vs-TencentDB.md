# Hindsight vs Hy-Memory vs TencentDB

Nguồn: hai trang so sánh đã đọc, cùng hai concept của TencentDB ([pipeline](tencentdb-memory-pipeline.md), [retrieval/storage](tencentdb-retrieval-storage.md)). Tôi không mở `raw/`. Evidence class mặc định là **Observed**, tức đọc code tĩnh và không chạy. Phần nhận xét là **Synthesis**.

## Tóm tắt

| | **Hindsight** | **Hy-Memory** | **TencentDB** |
|---|---|---|---|
| Trường phái | Fact có kiểu, nối bằng link | Hierarchy L0–L7 | Hierarchy L0–L3 |
| LLM khi ghi | Lõi, không bỏ được | Lõi ở `pro`/`ultra`, tuỳ chọn ở `lite` | Cần cho L1–L3, L0 thì không |
| Consolidation | Tự động sau mỗi lần ghi | System 1 sau mỗi lần ghi, System 2 gọi tường minh | Scheduler bất đồng bộ |
| Retrieval | 4 arm, RRF, cross-encoder | Điểm cộng rồi blend RRF, rồi graph, MMR, decay | Keyword, embedding, hybrid |
| Độ chi tiết trong wiki | Cao | Cao | **Thấp** |

## 1. Data model

- **Hindsight**
  - Đơn vị là `memory_unit` trong một **bank**.
  - `fact_type` gồm `world`, `experience`, `observation`.
  - Phía trên có mental model, knowledge page và directive.
  - `memory_links` có bốn loại: entity, temporal, semantic, causal.
  - Có hai chiều thời gian: lúc xảy ra và lúc được ghi nhận.
- **Hy-Memory**
  - Đơn vị là node, mỗi node thuộc một tầng: L0 profile, L1 raw, L2 fact, L3 summary, L4 identity (legacy), L5 knowledge (chưa làm), L6 schema, L7 intention.
  - Có evolution chain, và graph projection ở `pro`/`ultra`.
  - Nhánh working/coding dùng **fact + experience**, liên kết chéo với nhau. Coding có thêm diff chain, và fact chain tối đa 8 thế hệ.
- **TencentDB**
  - L0 hội thoại, L1 atomic fact, L2 scene block, L3 core/persona.
  - Ngoài ra có asset skill, wiki và CodeGraph.
  - Wiki có page-link graph, CodeGraph có caller/callee.

**Synthesis:** Hy và TencentDB cùng kiểu "raw → fact → tổng hợp → persona/schema". Hy có nhiều tầng hơn và có graph schema. Hindsight có ít tầng hơn nhưng mạng link giàu hơn (4 loại quan hệ, 2 chiều thời gian).

## 2. Storage

| | Backend | Ghi chú |
|---|---|---|
| **Hindsight** | PostgreSQL 15+ có pgvector, hoặc Oracle 23ai. Mặc định là `pg0` embedded. | 116 Alembic revision. **Không có lớp storage abstraction**, nên bị ràng buộc vào Postgres/Oracle. |
| **Hy-Memory** | Chroma + Kuzu + SQLite (cache và history). Tuỳ chọn Qdrant, FAISS, Neo4j, MySQL. | Tên collection có hậu tố `_{dims}`. MemHub chỉ lưu grant/queue/receipt trong SQLite, không lưu memory. |
| **TencentDB** | Database cho L0/L1 và file cho conversation/scene/persona/checkpoint. SQLite (FTS5 + bảng vector) là mặc định. | Tencent Cloud VectorDB có hybrid native. **MongoDB: dense search là no-op** trong snapshot này. |

## 3. Write path

**Hindsight (`retain_batch`)**
1. Kiểm tra bank và embedding, rồi chunk 3000 ký tự.
2. Quyết định delta retain.
3. LLM trích fact. Các mode: `concise`, `verbose`, `custom`, `verbatim`, `chunks`.
4. Entity resolution: trigram mặc định.
5. Lưu, rồi tạo link temporal, semantic (ngưỡng 0.7, top-50) và causal.
6. Kích hoạt consolidation bất đồng bộ.

**Hy chat**
1. Ghi `L1_RAW`.
2. Nếu mode khác `lite`: 1 lần LLM trả về memory, intentions, basic_info.
3. Upsert L0, rồi dedup bằng cosine.
4. Reconcile `ADD`/`SUPERSEDE`/`UPDATE`.
5. Từ 2.0.13, lỗi thì **fail closed**, không lưu raw làm fallback.

**Hy coding/working**
- Mỗi trace gọi 1 LLM.
- **Cả quyết định cho fact lẫn experience phải thành công thì mới ghi.**
- Chỉ ghi khi có tool-call trace và mode là `pro`/`ultra`.

**TencentDB**
1. `performAutoCapture` ghi L0, có checkpoint và đã sanitize.
2. Scheduler chạy L1 extraction (có `batchDedup`), rồi L2 scene, rồi L3 persona. Tất cả bất đồng bộ.
3. Seed runtime chỉ chờ L1 rảnh, nên L2/L3 có thể vẫn đang chạy (**Reported**). Không có gì chứng minh mọi turn đã lên hết các tầng.

### Dedup, cập nhật và xoá

| | Dedup / cập nhật | Decay / xoá |
|---|---|---|
| **Hindsight** | Entity resolution. Observation dedup ở cosine ≥ 0.97, chỉ Postgres. Observation được *refine*, không ghi đè, và proof count tăng hoặc giảm. | Chỉ boost recency lúc recall (365 ngày, α=0.2), không decay khi lưu. Delete kích hoạt consolidation. |
| **Hy** | `SUPERSEDE`/`UPDATE` đẩy bản cũ về `SHADOW`. Subject gate của coding **tắt mặc định**, nên có thể merge nhầm subject. | Strength decay khi đọc: `(1+log(access))·exp(−idle/180)`. `delete-data` của MemHub cần xác nhận hai lần. |
| **TencentDB** | `batchDedup` ở L1. Chi tiết reconcile và mâu thuẫn **không có trong wiki**. | Decay không có trong wiki. Script purge xoá dữ liệu deployment. |

## 4. Consolidation

- **Hindsight**
  - Tự chạy sau retain/delete/update, batch 50, LLM batch 8.
  - *Mental model* refresh theo `full` hoặc `delta`, giữ 50 bản lịch sử.
  - Decision-model triage được báo cáo giảm khoảng 40% lời gọi LLM (**Reported**).
- **Hy**
  - System 1 chạy sau mỗi lần ghi.
  - System 2 (`ultra`) không bao giờ tự chạy. Phải gọi `evolve()`, lời gọi này đồng bộ và không idempotent.
  - DBSCAN gom cụm, mỗi batch (tối đa 24 fact) là một lời gọi LLM, tối đa 128 batch.
  - MemHub lên lịch evolve hằng đêm lúc 03:00.
- **TencentDB**: chỉ có pipeline L1 → L2 → L3 do scheduler điều khiển. Wiki không có chi tiết về cadence hay chiến lược.

## 5. Retrieval

| | Arm | Fusion | Rerank | Budget |
|---|---|---|---|---|
| **Hindsight** | Semantic, BM25, graph, temporal (song song) | RRF k=60, trọng số các arm bằng nhau | Cross-encoder trên top 300 (hoặc decision model) | `low/mid/high` = 100/300/1000 token. REST mặc định `max_tokens` 4096. |
| **Hy chat** | Vector, keyword, L0, alias, graph L6, tag, episode, intention | `sem + 0.35·bm25 + 0.3·tag`, rồi blend RRF (hệ số 0.4) | Graph rerank, MMR (khi `limit < 20`), cross-encoder local tắt mặc định | `limit` theo channel |
| **TencentDB** | Keyword, embedding, hybrid | RRF, hoặc hybrid native của backend | Không có | Proxy inject profile và scene |

Điểm riêng của từng hệ:
- **Hindsight**
  - Boost `1 + α(signal − 0.5)` cho recency, temporal proximity và proof count.
  - Điểm graph: `tanh(shared_entities × 0.5) + semantic_link + causal_link`.
  - Docstring nhắc MMR nhưng code không có.
- **Hy**
  - Chroma không có BM25, nên hybrid trên Chroma thực chất chỉ là vector.
  - Coding: fact là index chính, experience được kéo theo link.
  - `search_mode="agentic"` thêm judge, rewrite và parse thời gian bằng LLM.
- **TencentDB**
  - **Injector auto-recall L1 không được đăng ký** trong proxy. L1 và tìm kiếm hội thoại chỉ có qua tool khi agent gọi. Chỉ profile và điều hướng scene được inject.
  - SQLite lọc *sau* khi over-retrieve, MongoDB lọc ngay trong truy vấn.
  - MemoryKnowledge tìm wiki bằng FTS rồi mở rộng theo page-link graph.

### Answer synthesis
- **Hindsight `reflect`**: agent loop tối đa 10 vòng, 100k token, timeout 300 giây. Thứ tự tra: mental model → observation → raw fact, và citation được đối chiếu với ID đã lấy.
- **Hy**: `search_mode="agentic"`. Profile và persona do System 2 dựng.
- **TencentDB**: wiki không ghi nhận bước tổng hợp câu trả lời trong lõi.

### Khi thiếu thành phần
- **Hindsight**: decision model thì `scores.reranker: null`. `min_scores.reranker` trả về 400.
- **Hy**: Chroma thiếu BM25 thì vector-only. Init lỗi thì báo to chứ không âm thầm suy giảm.
- **TencentDB**: không có embedding thì keyword. SQLite thiếu FTS thì mất keyword. MongoDB dense là no-op.

## 6. Embedding, LLM và đa ngôn ngữ

| | Embedding mặc định | LLM mặc định | Đa ngôn ngữ |
|---|---|---|---|
| **Hindsight** | Local `bge-small-en-v1.5` (384) | `openai`/`gpt-4o-mini`, khoảng 30 provider | Embedder mặc định chỉ tiếng Anh, nên cần `bge-m3` cho ngôn ngữ khác. BM25 `native` tokenize CJK kém. |
| **Hy** | `text-embedding-3-small` (1536). MemHub dùng ONNX local `bge-small-zh-v1.5` (512). | `gpt-4.1-nano` | Prompt cho 11 ngôn ngữ, spaCy + jieba. Thiên về tiếng Trung ở MemHub. |
| **TencentDB** | Không ghi nhận | Không ghi nhận | Không ghi nhận |

**Synthesis:** Hindsight chạy được không cần cloud cho embedding. Hy SDK mặc định dùng embedding cloud. Riêng MemHub, bản local tiếng Trung phù hợp nếu dữ liệu chủ yếu là tiếng Trung.

## 7. Bảo mật và isolation (chỉ phần có trong các trang đã đọc)

- **TencentDB**
  - Có một chỗ docs và code lệch nhau. `assertIsolation` ghi là sẽ throw khi thiếu field bắt buộc, nhưng thân hàm lại thay bằng default bucket.
  - Router v3 kiểm tra riêng các field định danh, nhưng không nên suy ra mọi route đều bị chặn như nhau.
  - SQLite post-filter còn MongoDB filter trong truy vấn, nên cần audit access boundary trước khi deploy.
- **Hy**: isolation key là `user_id:agent_id`. MemHub không bao giờ suy ra việc xoá từ chỗ dữ liệu vắng mặt.
- **Hindsight**: isolation theo bank. Tôi chưa đọc trang bảo mật cho phần này.

Muốn đối chiếu đầy đủ về bảo mật thì đọc [security and privacy comparison](agent-memory-security-and-privacy-comparison.md). Tôi chưa mở trang đó trong phiên này.

## Nên chọn hệ nào (Synthesis)

- **Hindsight**: bạn muốn retrieval nhiều arm và reflect có trích dẫn, đã chấp nhận Postgres. Cần nhớ rằng LLM luôn nằm trên write path.
- **Hy-Memory**: bạn cần nhiều tầng trừu tượng (profile, schema, intention), muốn chọn mức LLM theo client (`lite`/`pro`/`ultra`), hoặc có coding agent cần diff chain. Đổi lại là độ phức tạp cao và System 2 phải gọi tay.
- **TencentDB**: phù hợp khi bạn cần proxy inject profile và scene, CodeGraph, hoặc backend Tencent Cloud. Wiki thiếu thông tin về reconcile, decay, embedding, LLM mặc định và answer synthesis, nên **chưa thể so sánh ngang** với hai hệ kia ở các mục đó.

## Giới hạn

- Cả ba đều là `draft`, và `stale_after` của hai trang so sánh là 2027-02-06. Các concept TencentDB hết hạn ngày 2027-05-06.
- Đây là static inspection, không chạy code. Không có kết luận nào về chất lượng retrieval. Số benchmark nằm ở [benchmarks comparison](agent-memory-benchmarks-comparison.md), và các con số đó không xếp hạng chéo được.
- Các ô "không ghi nhận" của TencentDB là khoảng trống của wiki, không phải bằng chứng hệ đó thiếu tính năng.
