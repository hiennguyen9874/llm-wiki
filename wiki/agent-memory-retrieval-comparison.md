---
type: Synthesis
title: Agent memory retrieval comparison
description: So sánh pipeline retrieval (phần "RAG" bên trong) của tám hệ agent-memory trong wiki — các arm, công thức fusion, rerank, token budget, temporal/graph retrieval, answer synthesis, chế độ suy giảm, embedding mặc định và hỗ trợ đa ngôn ngữ.
tags: [agent-memory, survey, comparison, retrieval, rag, hybrid-search]
status: draft
created: 2026-11-07
generated: { by: llm-wiki-agent/1, at: 2026-11-07T01:20:00Z }
stale_after: 2027-02-06
sources:
  - id: ai-memory
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory repository
  - id: cognee
    resource: ../raw/cognee/README.md
    scope: ../raw/cognee/
    kind: code
    revision: 525b1d1
    title: Cognee repository
  - id: gbrain
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain repository
  - id: headroom
    resource: ../raw/headroom/README.md
    scope: ../raw/headroom/
    kind: code
    revision: 2b0315b
    title: Headroom repository
  - id: hindsight
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight repository
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory SDK and MemHub)
  - id: mem0
    resource: ../raw/mem0/README.md
    scope: ../raw/mem0/
    kind: code
    revision: d16b8df
    title: Mem0 repository
  - id: tencentdb
    resource: ../raw/TencentDB-Agent-Memory/README.md
    scope: ../raw/TencentDB-Agent-Memory/
    kind: code
    revision: 2002196
    title: TencentDB Agent Memory repository
---

# Agent memory retrieval comparison

Trang này thuộc cụm [Agent memory landscape survey](agent-memory-landscape-survey.md). Nó so sánh *cách đọc memory*, tức pipeline retrieval-augmented nằm bên trong mỗi hệ. Hầu hết các hệ đã hội tụ về **hybrid retrieval**: vector + lexical (BM25/FTS) + một hoặc nhiều arm có cấu trúc (graph, temporal, entity, observation), fusion bằng **RRF `k = 60`**, rồi rerank và cắt theo **token budget**. Khác biệt nằm ở năm chỗ: đơn vị được xếp hạng (fact, chunk, page), cách chọn arm (cố định, router, hay mode bundle), công thức boost và authority, có bước agentic synthesis hay không, và cách hệ báo hiệu khi bị suy giảm. Evidence class mặc định là **Observed** (static inspection, chưa đo chất lượng); số liệu chất lượng nằm ở [benchmarks comparison](agent-memory-benchmarks-comparison.md).

## 1. Tổng quan arm và fusion

| Hệ | Đơn vị xếp hạng | Arm | Fusion | Rerank | Budget |
|---|---|---|---|---|---|
| Mem0 | Memory record | Semantic (tạo candidate) + BM25 + entity (chỉ boost) | `(sem + bm25 + entity)/max_possible`, chặn trên ở 1 | Có adapter reranker | `limit`[^mem0] |
| Cognee | Chunk / graph / summary | Router chọn lane: lexical, coding rules, code, broad, temporal, hybrid completion (21 `SearchType`) | Theo lane | — | —[^cognee] |
| Hindsight | Memory unit | Semantic, BM25, graph, temporal (song song) | RRF k=60, các arm có trọng số bằng nhau | Cross-encoder trên top 300 (hoặc decision model) | Token budget; kết quả đầu luôn được giữ nguyên vẹn[^hindsight] |
| Hy Memory (chat) | Node theo tầng | Vector, keyword, L0 ẩn, alias, graph L6, tag, episode, intention | Cộng điểm (sem + BM25 + tag) **rồi blend RRF** (K=60) | Graph rerank; cross-encoder local (tắt mặc định); MMR | `limit` theo channel[^hy-memory] |
| TencentDB | L1 record / hội thoại | Keyword, embedding, hybrid | RRF, hoặc hybrid native của backend | — | Proxy inject profile/scene[^tencentdb] |
| ai-memory | Page | FTS, entity, vector, abstract, graph, observation | RRF k=60 × hệ số authority [0.55, 1.50] | Tuỳ chọn | Budget khi tổng hợp answer[^ai-memory] |
| GBrain | **Page** (chunk tốt nhất đại diện cho page) | Vector, BM25, title, relational | RRF k=60 ở mức page, sau đó blend `0.7·RRF + 0.3·cosine` và các boost | Cross-encoder (`rerank-3-lite`) + relational re-pin | Token budget là bước cuối[^gbrain] |
| Headroom | Memory | Vector và FTS5 (hai đường riêng) | Chưa xác lập | — | Injection budget của proxy[^headroom] |

## 2. Chi tiết từng hệ

### Mem0 (OSS)
- Candidate chỉ đến từ semantic search. BM25 đã chuẩn hoá và entity boost **xếp hạng lại** các hit semantic chứ không thêm candidate keyword-only hay entity-only.
- Threshold áp lên điểm semantic *trước* khi cộng, nên điểm tổng trả về có thể thấp hơn threshold. Mẫu số phụ thuộc vào số tín hiệu đang hoạt động, vì vậy **điểm không so sánh được giữa các query** (Synthesis). `explain=True` cho xem từng thành phần.
- README mô tả ba tín hiệu được chấm song song; code gọi tuần tự, chỉ song song bên trong entity lookup (mâu thuẫn giữa doc và code).
- Entity scoping nằm trong `filters`. Bản hết hạn bị lọc sau retrieval. Graph store bên ngoài đã bị gỡ.[^mem0]

### Cognee
- `recall` là một lớp trên `search`, thêm chọn nguồn, nhãn kết quả và router. Một session ID trần có thể làm session hit chặn ngắn việc tra graph. `query_type` tường minh bỏ qua router.
- Router dùng regex theo thứ tự: cụm trong dấu ngoặc kép → lexical chunk; yêu cầu coding rule → coding rules; câu hỏi về code → code search; câu hỏi đếm → broad; câu hỏi có ngày → temporal; còn lại → hybrid completion. Không có LLM thì hệ chỉ trả context hoặc fallback.
- Enum `SearchType` có 21 giá trị, ví dụ `CHUNKS`, `RAG_COMPLETION`, `GRAPH_COMPLETION`, `GRAPH_COMPLETION_COT`, `TRIPLET_COMPLETION`, `TEMPORAL`, `CODE`, `CHUNKS_LEXICAL`, `AGENTIC_COMPLETION`, `CYPHER` (Observed trong phiên này). **Cypher không được route tự động** vì rủi ro chạy truy vấn tuỳ ý khi chỉ có quyền đọc.
- Query không chỉ định dataset có thể được route qua vector của global-context index, và được nới rộng nếu không ra kết quả (Reported).[^cognee]

### Hindsight
- Bốn arm: pgvector ANN, BM25, graph (mở rộng từ seed), temporal (lọc theo khoảng thời gian).
- RRF: `score(d) = Σ 1/(60 + rank_i(d))`.
- Cross-encoder rerank trên top 300, batch 32 (local) hoặc 128 (TEI).
- Boost dạng `1 + α(signal − 0.5)`: recency α=0.2, temporal proximity α=0.2, proof count α=0.1. Tổng cộng khoảng +27% / −23%.
- Budget `low/mid/high` = 100/300/1000 token; REST mặc định `max_tokens` 4096. Gate: semantic 0.3, graph seed 0.3, temporal 0.1.
- Điểm graph: `tanh(shared_entities × 0.5) + semantic_link + causal_link`.
- Khi bật decision model, nó thay cross-encoder và thứ tự của nó là kết quả cuối.
- Docstring có nói đến MMR nhưng code không có (mâu thuẫn doc/code).[^hindsight]

### Hy Memory
- Hai reader: `Legacy` (không có keyword) và `Hybrid`. Chroma không có kênh BM25, nên hybrid trên Chroma thực chất chỉ là vector.
- Tiền xử lý: lemmatize bằng spaCy + jieba, mở rộng query. Isolation key là `user_id:agent_id`.
- Fusion: `final = sem + 1[bm25]·0.35·bm25_norm + 1[tag]·0.3·max(tag_cos, entity_hit)`, sau đó blend RRF (hệ số 0.4); vector pool 30.
- Sau fusion: L6 forward/reverse, graph rerank (support propagation, mở rộng quan hệ có giới hạn, `TYPE_PRIOR` từ `causes` 0.9 xuống `semantic_neighbor` 0.35), MMR (khi `limit < 20`), strength decay, underflow fill.
- Kết quả trả về theo channel `normal`/`schema`/`proactive`; profile L0 lấy qua `get_user_profile()`.
- **Coding:** fact là index chính (gate 0.30); experience được kéo theo link hoặc tìm vector trực tiếp; BM25Plus chỉ dùng để xếp lại. `scene="all"` fusion các lane bằng RRF. `search_mode="agentic"` thêm judge, rewrite và parse thời gian bằng LLM.[^hy-memory]

### TencentDB
- MemoryCore hỗ trợ keyword, embedding và hybrid (RRF trừ khi backend có hybrid native). Không có embedding thì fallback về keyword. SQLite lọc *sau* khi over-retrieve, còn MongoDB lọc ngay trong truy vấn.
- Trong proxy, **injector auto-recall L1 không được đăng ký**: L1 và tìm kiếm hội thoại chỉ có qua tool khi agent gọi; profile và điều hướng scene thì có thể được inject.
- MemoryKnowledge tìm wiki bằng FTS và mở rộng theo page-link graph; CodeGraph có search, caller/callee và impact.[^tencentdb]

### ai-memory
- Stream: `fts` (bản mới nhất, chưa hết hạn), `entity`, `vector` (bị bỏ qua nếu không có query vector), `abstract` (tắt mặc định), `graph` (chỉ seed từ fts/vector/entity), `observation` (bật mặc định; mỗi observation bầu một phiếu cho trang session của nó).
- `PageFilter` (kind/tier/path_prefix/tag) được áp **trước** khi xếp hạng, để loại hiếm không bị đẩy ra ngoài.
- Authority: rule/decision +0.15, session −0.15, semantic/procedural +0.10, tag `canonical` +0.20, `superseded` bị chặn ở 0.65…
- Chế độ đặc biệt: `as_of` (chỉ entity timeline + FTS lọc theo phiên bản), `global` (chỉ FTS, có lọc theo người xem), `explain` (rank từng stream và thời gian từng stream).
- Embedder local chờ 250 ms rồi fallback về lexical.[^ai-memory]

### GBrain
- Thứ tự stage: intent → expansion (tắt) → recall 4 arm → re-rank SQL theo nguồn → RRF ở mức page (k=60) → blend cosine 0.7/0.3 → boost (backlink, salience, recency, graph, exact-match) → graph augment → dedup → **rerank** → feedback → relational re-pin (3) → alias hop → exact-lookup → autocut → limit → token budget.
- Mode bundle:

  | Mode | Budget | Limit | Reranker |
  |---|---|---|---|
  | `conservative` | 4k | 10 | Tắt |
  | `balanced` (mặc định) | 12k | 25 | `voyage:rerank-3-lite` |
  | `tokenmax` | Không giới hạn | 50 | Bật |

- Reranker fail-open khi không có key. Verb `recall` xếp hạng facts bằng cosine cộng điểm khớp nguyên từ.[^gbrain]

### Headroom
- Vector search và FTS5 là hai đường riêng. Proxy có injection budget, hoặc có thể tắt auto-inject để agent tự gọi tool.
- Có một hybrid scorer gần đó nhưng chưa xác lập nó có nối với memory hay không. Phần chính của Headroom là nén context (CCR), không phải retrieval.[^headroom]

## 3. Embedding, reranker và LLM mặc định

| Hệ | Embedding mặc định | Reranker mặc định | LLM mặc định / ghi chú |
|---|---|---|---|
| Mem0 | OpenAI | — | OpenAI; vector store mặc định là Qdrant[^mem0] |
| Cognee | Model local tải về lần đầu (quickstart dùng `cognee[gliner]`) | — | Không có LLM thì chỉ trả passage[^cognee] |
| Hindsight | `local` `BAAI/bge-small-en-v1.5` (384) | `local` `hindsight-ai/hs-rerank-1` | `openai` / `gpt-4o-mini`; khoảng 30 provider LLM; decision model `none`[^hindsight] |
| Hy Memory | `text-embedding-3-small` (1536) | Cross-encoder local tắt | `gpt-4.1-nano`[^hy-memory] |
| MemHub | ONNX local `bge-small-zh-v1.5` (512) | — | Cần model sinh để trích xuất[^hy-memory] |
| TencentDB | Không ghi nhận | — | —[^tencentdb] |
| ai-memory | Local `all-MiniLM-L6-v2` (384, candle) khi chưa đặt provider | Tuỳ chọn (`AI_MEMORY_RERANKER=llm` gửi query đi) | Không cần LLM; 10 lựa chọn provider LLM, 6 lựa chọn embedder[^ai-memory] |
| GBrain | `voyage:voyage-4` (1024) | `voyage:rerank-3-lite` | Keyless vẫn chạy được; nhiều provider embedding[^gbrain] |
| Headroom | Không ghi nhận | — | —[^headroom] |

**Synthesis.** ai-memory và Hindsight mặc định *chạy được không cần dịch vụ cloud cho embedding*. GBrain, Hy SDK và Mem0 mặc định dùng embedding cloud.

## 4. Temporal và graph retrieval

| Hệ | Temporal | Graph trong retrieval |
|---|---|---|
| Mem0 | Lọc expiration | Không (entity chỉ là boost)[^mem0] |
| Cognee | Lane `TEMPORAL` | Nhiều kiểu `GRAPH_COMPLETION*`, `TRIPLET_COMPLETION`[^cognee] |
| Hindsight | Arm temporal; hai chiều thời gian (xảy ra / ghi nhận) | Arm graph mở rộng theo entity/semantic/causal link[^hindsight] |
| Hy Memory | Evolution chain, `created_after`, boost thời gian nhẹ, L7 `valid_until` | L6 forward/reverse; graph rerank theo `TYPE_PRIOR`[^hy-memory] |
| TencentDB | — | Page-link graph (wiki), CodeGraph[^tencentdb] |
| ai-memory | `as_of` "bi-temporal-lite": chỉ mô hình hoá thời điểm ghi nhận | Stream graph mở rộng từ hàng xóm link; typed edge không có trọng số riêng[^ai-memory] |
| GBrain | `valid_from/until` trên fact; khung ngày trong `think` | Arm relational; duyệt BFS (giới hạn 20k page đã thăm); multi-hop có giới hạn; planner từ chối câu hỏi phủ định, đếm hoặc có ràng buộc thời gian[^gbrain] |
| Headroom | Khoảng hiệu lực trên `Memory` | Chưa inspect[^headroom] |

## 5. Answer synthesis và retrieval kiểu agentic

- **Hindsight `reflect`:** agent loop tối đa 10 vòng, 100k token, timeout 300 giây. Thứ tự tra: mental model → observation (bản stale được kiểm lại với fact) → raw fact. Citation được đối chiếu với ID đã lấy về. Disposition traits (skepticism/literalism/empathy) và directive (luật cứng) điều chỉnh câu trả lời. Đọc một mental model chỉ là một lần đọc DB.[^hindsight]
- **GBrain `think` / `synthesize`:** gom 5 stream (pages, takes, graph walk, anchor), viết câu trả lời có trích dẫn kèm *gap analysis* (page stale, claim không có trích dẫn, mâu thuẫn, lỗ hổng). CRAG chỉ được dùng cho `think`.[^gbrain]
- **ai-memory `answer=true`:** context bằng chứng có đánh số, cấm dùng kiến thức ngoài, output có cấu trúc. Câu trả lời bị **từ chối nếu có citation không rõ ràng**. Không có provider thì trả `answer_unavailable` chứ không báo lỗi.[^ai-memory]
- **Cognee:** các `SearchType` dạng `*_COMPLETION`, `AGENTIC_COMPLETION`, `GRAPH_COMPLETION_COT`.[^cognee]
- **Hy Memory:** `search_mode="agentic"` (judge, rewrite, time parsing); profile và persona do System 2 dựng.[^hy-memory]
- **Mem0, TencentDB, Headroom:** wiki không ghi nhận bước tổng hợp câu trả lời trong lõi.[^mem0][^tencentdb][^headroom]

## 6. Chế độ suy giảm và tín hiệu báo lỗi

| Hệ | Khi thiếu thành phần |
|---|---|
| Mem0 | Store không có keyword search thì bỏ tín hiệu BM25[^mem0] |
| Cognee | Không có LLM thì router ép về context-only hoặc fallback[^cognee] |
| Hindsight | `scores.reranker: null` khi dùng decision model; `min_scores.reranker` trả về 400[^hindsight] |
| Hy Memory | Chroma không có BM25 → vector-only; init lỗi to thay vì âm thầm suy giảm (graph hoặc rerank không tải được)[^hy-memory] |
| TencentDB | Không có embedding → keyword; SQLite không có FTS thì mất keyword; MongoDB dense là no-op[^tencentdb] |
| ai-memory | Đường zero-LLM luôn có; embedder chậm → lexical sau 250 ms[^ai-memory] |
| GBrain | Báo rõ trong `degraded[]`: `embed_timeout` (6 giây) → chỉ keyword; `vector_candidates_incomplete`; `safe_index_pending`; reranker fail-open; lỗi quyền truy cập thì raise `database_error` chứ không trả "không có kết quả"[^gbrain] |
| Headroom | Không ghi nhận[^headroom] |

GBrain là hệ duy nhất có hợp đồng tường minh "**kết quả rỗng không chứng minh trang không tồn tại**" (Synthesis).

## 7. Đa ngôn ngữ và CJK

- **ai-memory:** chỉ mục bigram `pages_cjk_fts` cho Han/Kana/Hangul, nên tìm được chuỗi con CJK không có dấu cách mà không cần LLM.[^ai-memory]
- **GBrain:** truy vấn CJK luôn dùng fallback `ILIKE`, deadline 3 giây (Reported).[^gbrain]
- **Hindsight:** embedder mặc định chỉ hỗ trợ tiếng Anh, nên dùng `bge-m3` cho ngôn ngữ khác; BM25 `native` dùng từ điển `english` và tokenize CJK kém. Reranker mặc định hỗ trợ 8 ngôn ngữ.[^hindsight]
- **Hy Memory:** prompt cho 11 ngôn ngữ; lemmatize bằng spaCy + jieba. MemHub dùng embedder tiếng Trung.[^hy-memory]

## Nhận xét: "RAG" so với "memory" (Synthesis)

- RAG cổ điển là semantic top-k trên một corpus tĩnh. Trong wiki, gần nhất với kiểu này là **Mem0** (semantic trước, các tín hiệu khác chỉ boost) và **Hy `lite`** ("plain vector RAG over raw"). Chính tài liệu của Hindsight cũng phân biệt RAG (chỉ semantic, không có entity, stateless) với memory (nhiều arm, entity graph, temporal, consolidation).[^mem0][^hy-memory][^hindsight]
- Retrieval của memory khác RAG ở bốn điểm: (1) có **arm có cấu trúc** (graph, temporal, entity, observation); (2) có **ưu tiên theo loại hoặc độ tin cậy** (authority của ai-memory, trust tier của GBrain, proof count của Hindsight); (3) đọc **dữ liệu đã được hợp nhất trước** (observation, mental model, schema, compiled truth) thay vì chunk thô; (4) **lọc theo danh tính** (user/agent/project/bank).
- GBrain và ai-memory xếp hạng **ở mức page**, Hindsight, Hy và Mem0 xếp hạng **ở mức fact**. Xếp theo page giảm trùng lặp ngữ cảnh, xếp theo fact cho độ hạt mịn hơn khi inject.

## Relationships

- Part of: [Agent memory landscape survey](agent-memory-landscape-survey.md).
- Related: [data model and write comparison](agent-memory-data-model-and-write-comparison.md) (dữ liệu được đọc ở đây), [benchmarks comparison](agent-memory-benchmarks-comparison.md) (chất lượng được báo cáo).

[^ai-memory]: [retrieval pipeline](ai-memory-retrieval-pipeline.md), [wiki storage/temporal](ai-memory-wiki-storage-and-okf.md), [providers](ai-memory-llm-and-embedding-providers.md), [data handling](ai-memory-data-handling-and-lifecycle-ops.md). Raw: `crates/ai-memory-store/src/reader.rs::hybrid_search_inner`, `PageFilter`, `PageAuthority::from_stored`, `SearchExplain`; `crates/ai-memory-mcp/src/server.rs::prepare_answer_request`, `validate_answer_citations`; `docs/temporal.md`; `crates/ai-memory-llm/src/local.rs::LOCAL_MODEL`; `src/fts_query.rs::cjk_index_terms`.
[^cognee]: [retrieval](cognee-retrieval.md), [overview](cognee-overview.md). Raw: `docs/recall-vs-search.md`; `cognee/api/v1/recall/query_router.py::_RULES`, `::constrain`; `cognee/modules/search/methods/search.py::authorized_search`; `cognee/modules/search/types/SearchType.py::SearchType` (21 giá trị, kiểm tra trong phiên này).
[^gbrain]: [retrieval pipeline](gbrain-retrieval-pipeline.md), [knowledge graph](gbrain-knowledge-graph.md), [embeddings](gbrain-embeddings-and-providers.md), [memory model](gbrain-memory-model.md). Raw: `src/core/search/hybrid.ts` (thứ tự stage); `src/core/search/mode.ts::MODE_BUNDLES`; `docs/architecture/RETRIEVAL.md` "Putting it together", "Breadth-first graph walks"; `src/core/think/gather.ts`; `src/core/ai/defaults.ts` dòng 15–19.
[^headroom]: [memory](headroom-memory.md), [cache/CCR](headroom-cache-and-ccr.md). Raw: `headroom/memory/core.py::HierarchicalMemory.search`, `text_search`; `headroom/proxy/memory_injection.py::MemoryInjectionBudget`; `headroom/relevance/hybrid.py::HybridScorer`.
[^hindsight]: [recall](hindsight-recall-pipeline.md), [reflect](hindsight-reflect-agent.md), [decision models](hindsight-decision-models.md), [providers](hindsight-llm-embedding-providers.md), [banks/multilingual](hindsight-memory-banks.md), [storage/config](hindsight-storage-and-configuration.md). Raw: `hindsight-docs/docs/developer/retrieval.md`; `hindsight-api-slim/hindsight_api/engine/search/{fusion,reranking,retrieval,graph_retrieval}.py`; `engine/reflect/agent.py::run_reflect_agent`; `config.py::PROVIDER_DEFAULT_MODELS`; `hindsight-docs/docs/developer/rag-vs-hindsight.md`; `hindsight-docs/docs/developer/multilingual.mdx`.
[^hy-memory]: [chat retrieval](hy-memory-chat-retrieval-pipeline.md), [working/coding](hy-memory-working-coding-memory.md), [SDK API/config](hy-memory-sdk-api-and-config.md), [storage](hy-memory-storage-and-reembed.md), [MemHub modes](memhub-memory-modes-and-write-queue.md), [MemHub embedding switch](memhub-embedding-space-switching.md). Raw: `hy_memory/pipelines/reader_base.py::_read_once`; `pipelines/_retrieval/{scoring,rrf,diversity,strength}.py`; `pipelines/_graph/rerank.py`; `client.py::_search_coding`; `hy_memory/config.py::MemoryConfig`; `memhub/apps/core/src/one_memory/local_embedding.py`.
[^mem0]: [retrieval](mem0-retrieval.md), [providers](mem0-providers.md), [source map](mem0-source-map.md). Raw: `mem0/memory/main.py::Memory.search`, `Memory._search_vector_store`, `Memory._compute_entity_boosts`; `mem0/utils/scoring.py::score_and_rank`; `mem0/configs/base.py::MemoryConfig`.
[^tencentdb]: [retrieval/storage](tencentdb-retrieval-storage.md), [proxy](tencentdb-proxy-integrations.md), [knowledge service](tencentdb-knowledge-service.md). Raw: `MemoryCore/src/core/hooks/auto-recall.ts::searchHybrid`; `MemoryCore/src/core/store/mongodb/memory-store.ts::MongoMemoryStore.searchL1Vector`; `MemoryProxy/src/injection/index.ts::buildPipelineBundle`; `MemoryKnowledge/src/engines/wiki/manager.ts::ftsSearch`.
