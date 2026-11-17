# Kiến trúc WeKnora

Dưới đây là kiến trúc đọc trực tiếp từ Fork trong `references/WeKnora` (VERSION `0.9.0`, commit `818f53a46`) cộng với topology triển khai của repo này (`compose.yaml`). Wiki `references/llm-wiki-rag/wiki/weknora-*.md` chụp bản `0.8.3` nên tôi dùng nó làm bản đồ, còn chi tiết thì kiểm lại trong code `0.9.0`.

## 1. Tóm tắt

WeKnora là **modular monolith Go** + **một service Python riêng để parse tài liệu** + **SPA Vue**, tất cả dùng chung một pipeline tri thức. Ba chế độ sản phẩm — hỏi đáp RAG, agent nhiều bước, và wiki tự sinh — cùng đọc/ghi trên một tập knowledge base, chứ không phải ba hệ thống.

Điểm thiết kế cốt lõi:

- **Mọi thứ là dữ liệu, không phải code cứng**: model, knowledge base, vector store, storage backend, parser engine, agent, MCP service đều là row trong DB, tham chiếu bằng ID.
- **Workspace = tenant**: gần như mọi bảng có `tenant_id`, mọi truy vấn lọc theo tenant.
- **Tác vụ nặng chạy nền** qua Asynq (Redis) với 6 worker pool tách theo giai đoạn.
- **Ingestion tách khỏi truy vấn**: chunker nằm trong Go, parser nằm trong docreader, embedding/rerank gọi qua model gateway.

## 2. Bản đồ triển khai

```
        Trình duyệt
            │  HTTP (SPA + /api proxy)
     ┌──────▼───────┐
     │  frontend    │  nginx: Vue 3 build + proxy /api → app:8080
     └──────┬───────┘
            │
     ┌──────▼───────────────────────────────┐
     │  app (Go, Gin + dig)                 │
     │  • REST /api/v1, SSE chat            │
     │  • toàn bộ service + repository      │
     │  • asynq worker pools (cùng process) │
     └──┬────────┬─────────┬────────┬───────┘
        │gRPC    │SQL      │Redis   │Bolt
   ┌────▼────┐ ┌─▼──────┐ ┌▼─────┐ ┌▼─────┐
   │docreader│ │postgres│ │redis │ │neo4j │
   │ Python  │ │ParadeDB│ │queue │ │graph │
   │ parse → │ │pgvector│ │stream│ │(tuỳ  │
   │ Markdown│ │+BM25   │ │cache │ │chọn) │
   └────┬────┘ └────────┘ └──────┘ └──────┘
        │
   LLM / embeder-gateway / PaddleOCR-VL gateway (ngoài stack, qua host.docker.internal)
```

- `app`: monolith; HTTP server **và** worker nằm chung process (`internal/container/container.go` build cả hai).
- `docreader`: service Python, gRPC cổng 50051, chỉ làm nhiệm vụ chuyển file → Markdown + ảnh; không gọi model.
- `postgres` (ParadeDB pg17): vừa là DB nghiệp vụ (GORM), vừa là **vector store + keyword index** (`embeddings` table: `halfvec` + `pg_search`/BM25).
- `redis`: queue Asynq, `StreamManager` cho SSE/resume, lock wiki, pub/sub system settings, governor gọi model.
- `neo4j`: knowledge graph, chỉ bật khi `NEO4J_ENABLE=true` (repo này bật).

## 3. Backend Go: phân lớp

```
cmd/server/main.go            entrypoint, signal, shutdown
  └── internal/container      DI bằng Uber Dig; wiring toàn bộ hệ thống
        └── internal/router   Gin engine, middleware, route groups
              └── internal/handler/*            HTTP: parse request, DTO, SSE
                    └── internal/application/service/*   nghiệp vụ
                          └── internal/application/repository/*  GORM / retriever
                                └── internal/types, internal/types/interfaces
```

- **`internal/container/container.go`** (~2.300 dòng) là "bản đồ kiến trúc" thật sự: mỗi `container.Provide`/`Invoke` là một thành phần. Đọc file này trước khi đọc bất cứ service nào.
- **`internal/router/router.go`** gom route theo nhóm: auth, tenant, KB, knowledge, chat, model, agent, MCP, sandbox, IM, embed… Middleware xếp theo thứ tự: CORS → logger → recovery → auth (JWT/API key) → tenant context → RBAC guard.
- **Khởi động**: load `.env` → `LogStartupEnv` → `BuildContainer` (DB, migration, Redis, docreader client, Neo4j, Langfuse tuỳ chọn, worker server) → `runStartupBootstrap` (ví dụ nâng tài khoản thành system admin) → serve HTTP.
- **Tắt**: drain HTTP rồi cleanup, tổng ngân sách mặc định 30s (`internal/runtime/shutdown.go`), tín hiệu thứ hai thì đóng cưỡng bức.

Vì worker và HTTP chung process, muốn scale riêng phần ingest phải sửa code/topology — đây là lựa chọn "monolith dễ vận hành" chứ không phải microservice.

## 4. Luồng nạp tài liệu (ingestion)

```
POST /api/v1/knowledge-bases/:id/knowledge
  → tạo row knowledge (parse_status=pending)
  → enqueue TypeDocumentProcess (queue "default", pool core)
        │
        ├─ 1. convert(): tải file → docreader (gRPC)
        │      docreader chọn parser engine: builtin / markitdown /
        │      paddleocr_vl / mineru / opendataloader (per-KB rules)
        │      → Markdown + ảnh + source locators
        │
        ├─ 2. chuẩn hoá: NFC, line endings, HTML table → GFM
        ├─ 3. ảnh: lưu vào storage (local/S3/MinIO/COS/OSS/…), viết lại link
        ├─ 4. chunk: Go chunker (auto | heading | heuristic | recursive | legacy)
        │      hỗ trợ parent-child, breadcrumb tiêu đề, protected spans
        │      (code/math/link/table), validate chunk trước khi nhận
        ├─ 5. CreateChunks() → bảng chunks
        ├─ 6. BatchIndex(): embedding → bảng embeddings
        │      (pgvector HNSW + pg_search BM25 trên cùng bảng)
        └─ 7. enqueue post-process:
               summary, generated questions, graph extract,
               image multimodal (VLM), auto-tag, wiki ingest
```

Chi tiết đáng chú ý:

- **Idempotency và attempt**: mỗi lần parse có `Attempt`; task cũ bị "superseded" thì bỏ qua, không ghi đè chunk của lần mới (`knowledge_process.go`).
- **Trạng thái tài liệu**: `pending → processing → finalizing → completed | failed | cancelled | deleting`; `finalizing` nghĩa là parse xong nhưng enrichment còn chạy.
- **Chunker không gọi model**, parser cũng không; chỉ embedding, VLM caption/OCR, summary, question generation mới gọi model.
- **Ảnh** nằm trên volume `docreader-tmp` (docreader ghi, app mount read-only) và storage chính.

## 5. Hàng đợi nền

`internal/types/task.go` là nguồn sự thật duy nhất:

| Pool | Queue | Việc |
|---|---|---|
| core (8) | `default`, `chat_attachment` | parse tài liệu KB, parse file chat |
| postprocess (2) | `postprocess` | gắn kết quả enrichment |
| enrichment (12) | `summary`, `multimodal`, `graph`, `question`, `memory` | summary, caption ảnh, trích graph, sinh câu hỏi, memory |
| maintenance (4) | `sync`, `low` | datasource sync, clone/move/delete/reparse |
| shared (6) | mượn core/enrichment | đệm đàn hồi |
| wiki (8) | `wiki` | ingest/finalize wiki |

Kèm theo: retry backoff, dead-letter cho task ảnh hưởng trạng thái tài liệu, model concurrency governor (tách background với chat tương tác), và `SyncTaskExecutor` cho chế độ không Redis (Lite) — repo này không dùng Lite.

## 6. Luồng hỏi đáp RAG

`POST /api/v1/knowledge-chat/:session_id` → `sessionService`.

Điểm hay: pipeline **không cố định**, được lắp theo nhu cầu (`session_knowledge_qa.go`):

```go
// chat thuần
LOAD_HISTORY → MEMORY_RECALL → CHAT_COMPLETION_STREAM

// RAG
LOAD_HISTORY → MEMORY_RECALL → QUERY_UNDERSTAND → CHUNK_SEARCH_PARALLEL
  → CHUNK_RERANK → [WEB_FETCH] → CHUNK_MERGE → FILTER_TOP_K
  → [DATA_ANALYSIS] → INTO_CHAT_MESSAGE → CHAT_COMPLETION_STREAM
```

Mỗi stage là một `Plugin` đăng ký vào `EventManager` (`chat_pipeline/chat_pipeline.go`, mô hình middleware `next()`); nhiều plugin có thể cùng một event và chạy theo thứ tự đăng ký (ví dụ `CHUNK_RERANK`: rerank rồi memory-affinity). Mỗi stage được bọc một span Langfuse.

Chi tiết retrieval (0.9.0):

- **Fan-out**: mỗi KB/store một nhóm truy vấn; vector và keyword chạy song song; KB nhiều embedding model khác nhau bị từ chối gộp.
- **Vector**: pgvector `halfvec`, `ORDER BY embedding <=> query` (comment trong code giải thích vì sao cast cả hai phía để dùng HNSW).
- **Keyword**: ParadeDB `content ||| query`, điểm lấy từ `paradedb.score()` hoặc `pgsearch.score()` (tự dò schema).
- **Hợp nhất**: weighted RRF (`k=60`, vector 0.7 / keyword 0.3), chuẩn hoá về `[0,1]`; vector-only giữ nguyên cosine, keyword-only chia theo điểm cao nhất của danh sách.
- **Rerank**: lấy `max(top_k, 50)` ứng viên; threshold cao mà rỗng thì nới `max(threshold*0.7, 0.3)`; model lỗi thì trả thứ tự retrieval kèm diagnostics chứ không bịa điểm.
- **Đa dạng**: MMR lambda 0.7, Jaccard trên token set.
- **Citation**: registry nguồn tách "ngữ cảnh mở rộng để xếp hạng" khỏi "chunk gốc làm bằng chứng" (`citation_sources.go`, `types.References`).

## 7. Tầng model

Model là **row trong DB**, không phải client hard-code:

- 5 loại: `KnowledgeQA` (chat), `Embedding`, `Rerank`, `VLLM`, `ASR`; API nhận alias `chat`/`vlm`/`vllm`.
- `api_key` được mã hoá AES bằng `SYSTEM_AES_KEY`.
- Gắn ở 3 tầng: KB (`embedding_model_id`, `summary_model_id`, `vlm_config`, `asr_config`…), agent (`model_id`, `rerank_model_id`…), workspace (`retrieval_config.rerank_model_id`, memory extract model).
- Ba bề mặt cấu hình khác nhau: row runtime (UI/API/CLI), `config/builtin_models.yaml` (upsert lúc khởi động, `is_builtin=true`), `config/models.json` (catalog vendor, không tạo row).
- ~30 provider trong `internal/models/providers`, cộng `generic` OpenAI-compatible — đúng cái repo này dùng cho LLM/embeder-gateway.
- Bọc thêm: concurrency limiter, Langfuse wrapper, token estimator/calibration cho agent.

## 8. Agent runtime

`internal/agent/engine.go` là một **ReAct engine có guard**:

- `Execute` → `executeLoop` → `runReActIteration`; mặc định 20 vòng, có thể unlimited.
- Budget riêng cho từng kiểu thất bại: 2 lần rỗng, 2 vòng lặp nội dung giống nhau, 3 lần cùng tool fail, 3 lần `length`, một lần compact-and-retry khi overflow context.
- Tool registry có **capability gate** (`agent/tools/capabilities.go`): tool đọc tài liệu chỉ bật khi KB trong scope có capability tương ứng (vector/keyword/wiki/graph/FAQ).
- Tool tiêu biểu: `search_knowledge`, `read_document`, `list_documents`, `query_knowledge_graph`, `web_search`, `web_fetch`, `data_analysis`, `search_memory`, `wiki_*`, và nhóm sandbox `shell_exec`, `read_file`/`write_file`.
- Có approval cho tool nguy hiểm, `ask_user`, HITL, steer giữa lượt (message bơm vào round boundary), checkpoint/compaction, memory dài hạn, sub-agent collaboration.
- **Stateless giữa các lượt**: history do caller nạp từ DB (`LoadAgentHistory`) rồi truyền vào; engine không cache hội thoại.
- Sandbox (Docker/Cube/E2B) cô lập lệnh shell khỏi host WeKnora.

Endpoint: `POST /api/v1/agent-chat/:session_id`.

## 9. Wiki và knowledge graph

- **Wiki** là một KB type (`document | faq | wiki`). Sau khi tài liệu được index, post-process enqueue `TypeWikiIngest` (pool wiki) → các batch map/reduce sinh trang wiki có slug, link chéo, citation, lịch sử revision; `TypeWikiFinalize` chốt. Có lock theo slug/identity trên Redis để nhiều batch cùng KB không lost-update.
- **Graph**: task `TypeChunkExtract` trích entity/relation, ghi Neo4j theo namespace (`tenant/kb/knowledge`); plugin `ENTITY_SEARCH` chạy song song với chunk search và kết quả được hợp nhất ở bước rerank/merge. Neo4j nằm sau `NEO4J_ENABLE`.

## 10. Streaming và frontend

- `EventBus` in-process phát event (`answer`, `thought`, `tool_call`, `references`, `complete`, `stop`…).
- `StreamManager` (`STREAM_MANAGER_TYPE=redis`) lưu event theo `session/message` và một key "live run", nên client rớt kết nối có thể `GET /api/v1/sessions/continue-stream/:session_id` để phát lại; heartbeat ~10s.
- Frontend: Vue 3 + Vite + Pinia + TDesign, `fetch-event-source`, state machine dựng lại answer/reasoning/tool/approval từ event, có versioned request coordinator để chống response cũ ghi đè.
- Chạy tiếp: nginx của frontend proxy `/api` sang `app:8080`; app chỉ bind `127.0.0.1` trên host (dành cho `setup.py`/E2E).

## 11. Multi-tenant, auth, an toàn

- **Tenant = workspace**: KB, knowledge, chunk, model, session, message, vector store, storage quota, memory đều scoped.
- **Chia sẻ**: KB share và agent share giữa tenant, có phân quyền đọc/ghi riêng.
- **Auth**: JWT người dùng; API key theo tenant (scope capability) và platform key cần thêm `X-Tenant-ID`; RBAC guard (`Viewer`, `Admin`, system admin) ở route; audit log.
- **Bảo vệ**: credential vault mã hoá, SSRF allowlist (`SSRF_WHITELIST` — repo này phải chứa `host.docker.internal`), URL parser security, sandbox, rate limit, policy cho tool.

## 12. Bề mặt tích hợp

REST `/api/v1`, SSE; **MCP server** cho agent ngoài tại `/mcp/:endpoint_id` (bearer token riêng) và **MCP client** để agent gọi dịch vụ ngoài (kèm OAuth); CLI + Go SDK; datasource connector (`notion`, `feishu`, `confluence`, `gitlab`, `rss`, `seafile`…); kênh IM và embed widget.

## 13. Phần riêng của repo này (Fork tiếng Việt)

Theo ADR 0003, Fork **chỉ chạy PostgreSQL, không feature flag**:

- `DB_DRIVER=postgres`, `RETRIEVE_DRIVER=postgres` → chỉ một retriever engine (`KVHybridRetrieveEngine` trên ParadeDB); nhánh SQLite/Lite/Milvus/Qdrant… trở thành dead code trong triển khai này.
- Toàn bộ metadata + vector + BM25 nằm **một Postgres** → ít thành phần, nhưng trần hiệu năng và backup gắn với DB; `scripts/check-db.sh` kiểm tra `lc_ctype`, index và EXPLAIN.
- Các bản vá tiếng Việt nằm thẳng trong Fork: ánh xạ `vi`/`vi-VN` → `Vietnamese` trong prompt, chunker theo tiêu đề Chương/Mục/Điều, mở rộng truy vấn, NFC, footnote, tokenizer BM25 (ADR 0002, #11).
- Overlay `config/prompt_templates/` mount read-only đè lên image; `config/builtin_models.yaml` khai báo 4 model built-in trỏ tới LLM/embeder-gateway/OCR gateway.
- `docreader-tmp` volume chia sẻ ảnh giữa docreader và app; storage local `/data/files`.

## 14. Thứ tự đọc code đề xuất

1. `compose.yaml` — topology.
2. `cmd/server/main.go` — vòng đời.
3. `internal/container/container.go` — wiring (đọc theo `Provide`/`Invoke`).
4. `internal/router/router.go` + `routes_chat.go` — bề mặt API.
5. `internal/application/service/knowledge_process.go::ProcessDocument` + `processChunks` — ingestion.
6. `internal/application/service/session_knowledge_qa.go` (pipeline builder) + `chat_pipeline/` — RAG.
7. `internal/application/service/knowledgebase_search*.go` + `reranking/` — retrieval.
8. `internal/agent/engine.go` + `agent/tools/` — agent.
9. `internal/types/task.go` — queue topology.
10. `internal/models/model.go` + `providers/` — model layer.

## Ghi chú nguồn

- Kiến trúc backend, persistence, queue, retrieval, agent, streaming: wiki `weknora-backend-architecture.md`, `-persistence`, `-task-queues`, `-hybrid-retrieval`, `-agent-runtime`, `-frontend-streaming` (bản 0.8.3).
- Các chi tiết tôi kiểm lại trực tiếp trong Fork 0.9.0: pipeline builder trong `session_knowledge_qa.go`, queue definitions `internal/types/task.go`, SQL ParadeDB trong `retriever/postgres/repository.go`, plugin list trong `container.go`, SSE/`StreamManager`, `NEO4J_ENABLE` trong `container.go` và `.env.example`, shutdown budget trong `internal/runtime/shutdown.go`.
- Tôi chưa chạy stack hay test nào trong lần này; mọi phát biểu về hành vi runtime (retry, resume, threshold fallback) là đọc code, không phải đo.