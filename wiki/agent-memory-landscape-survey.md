---
type: Synthesis
title: Agent memory landscape survey
description: Survey so sánh tám hệ agent-memory trong wiki (Mem0, Cognee, Hindsight, Hy-Memory/MemHub, TencentDB Agent Memory, ai-memory, GBrain, Headroom), chia theo hướng thiết kế và đối chiếu storage, write path, retrieval, consolidation, tích hợp, bảo mật và benchmark.
tags: [agent-memory, survey, comparison, rag, synthesis]
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

# Agent memory landscape survey

Wiki hiện có tám hệ agent-memory, mỗi hệ là một snapshot repo đã được compile. Survey này chia chúng thành **sáu hướng thiết kế**:

- **A. Fact memory layer:** memory là các fact rời do LLM trích xuất.
- **B. Knowledge-graph engine:** memory là graph + vector dựng từ nội dung.
- **C. Cognitive/hierarchical learning memory:** phân tầng, consolidation, tự tiến hoá.
- **D. Compiled Markdown brain:** file là source of truth, DB chỉ là index.
- **E. Local-first cross-harness hub:** một memory dùng chung cho nhiều agent qua hook, MCP, proxy hoặc import.
- **F. Context compression:** tối ưu token chứ không lưu trữ.

Một hệ có thể thuộc nhiều hướng. Các hệ đang hội tụ về cùng một khung: hybrid retrieval với RRF `k = 60`, memory phân tầng từ raw đến fact rồi đến belief/profile, cập nhật bằng supersession có lịch sử, và tích hợp qua MCP cộng hook. Khác biệt cốt lõi nằm ở bốn chỗ: LLM có bắt buộc trên write path không, source of truth là Markdown hay DB, mô hình isolation, và ai nắm vòng đời ghi (agent, hook, proxy hay importer). Benchmark đều do vendor tự công bố và không xếp hạng chéo được. Đây là trang hub; chi tiết theo từng chiều nằm ở năm trang chuyên đề trong mục [Các trang chuyên đề](#các-trang-chuyên-đề) (**Synthesis**).

## Các trang chuyên đề

| Chiều so sánh | Trang |
|---|---|
| Đơn vị memory, phân tầng, storage, write path, dedup/reconcile, consolidation, decay, xoá | [Data model, write path and lifecycle](agent-memory-data-model-and-write-comparison.md) |
| Arm, fusion, rerank, budget, temporal/graph, answer synthesis, chế độ suy giảm, embedding mặc định, CJK | [Retrieval comparison](agent-memory-retrieval-comparison.md) |
| SDK/REST/MCP/CLI, cơ chế tích hợp, tính năng cho coding agent, provider, triển khai, đổi embedding, observability | [Integration and operations](agent-memory-integration-and-operations-comparison.md) |
| Tư thế mặc định, tenancy, lỗ hổng isolation, egress/telemetry, lọc secret, xoá, độ tin cậy nội dung | [Security and privacy](agent-memory-security-and-privacy-comparison.md) |
| Bảng benchmark, khác biệt metric, mức tái lập, kết quả âm, mâu thuẫn | [Benchmarks comparison](agent-memory-benchmarks-comparison.md) |

## Phạm vi và phương pháp

- **Đầu vào:** toàn bộ concept `agent-memory` trong [index](index.md). Lần cập nhật này đã đọc phần lớn các trang lõi của từng hệ: overview, write, retrieval, storage, consolidation, security, integration, provider, benchmark. Các trang chưa đọc hoặc chỉ đọc lướt gồm CI/release/contributor (Hindsight, GBrain, Hy), control plane và clients của Hindsight, apps của MemHub, distribution của ai-memory, doc/code discrepancies, và một phần decision models.
- **Raw được mở trong phiên này** chỉ để xác minh: license của 8 repo; version của `mem0ai` (2.2.1) và TencentDB MemoryCore (1.0.2-beta.1); danh sách adapter của Mem0 (vector/LLM/embedding/integrations); enum `SearchType` và adapter storage của Cognee; tên handler MCP của Cognee; adapter memory của Headroom; thư mục `agents/` của TencentDB. Các kết quả này là **Observed**.
- **Evidence class** của các trang nguồn được giữ nguyên: phần lớn là static inspection do subagent thực hiện, benchmark là Reported, không có gì được chạy lại.
- **Loại trừ:** [Memos](memos-overview.md) thuộc domain `note-taking`. Wiki chưa có framework RAG chuyên dụng (LlamaIndex, LangChain, Haystack…), nên "RAG" ở đây là pipeline retrieval *bên trong* các hệ memory; xem [retrieval comparison](agent-memory-retrieval-comparison.md#nhận-xét-rag-so-với-memory-synthesis).

## Bản đồ nhanh

| Hệ | Đơn vị phát triển | Runtime | License | Snapshot | Hướng | Source of truth | Ghi không cần LLM |
|---|---|---|---|---|---|---|---|
| [Mem0](mem0-overview.md) | Mem0 | Python + TypeScript; server; managed platform | Apache-2.0 | `mem0ai` 2.2.1 | A | Vector store | Chỉ `infer=False`[^mem0] |
| [Cognee](cognee-overview.md) | Cognee | Python ≥3.10 | Apache-2.0 | 1.6.6 | B | Graph + vector + relational | Early chunk index[^cognee] |
| [Hindsight](hindsight-overview.md) | Vectorize.io | Python engine; SDK Py/TS/Go/Rust; Next.js UI | MIT | 1.2.0 | C (+E) | PostgreSQL / Oracle | Không[^hindsight] |
| [Hy Memory SDK](hy-memory-overview.md) | Tencent Hunyuan | Python SDK | Apache-2.0 | 2.0.14 | C | Store của SDK (Chroma + Kuzu…) | `lite`[^hy-memory] |
| [MemHub](memhub-product-architecture.md) | Tencent Hunyuan | Node Runtime + Python Core + Electron/Web/CLI | Apache-2.0 | 1.0.6 | E (trên Hy) | Data plane của SDK | `lite`[^hy-memory] |
| [TencentDB Agent Memory](tencentdb-agent-memory-overview.md) | Tencent Cloud | Các service TypeScript; SDK TS/Py | MIT | MemoryCore 1.0.2-beta.1 | C + E (+D cho wiki) | DB (L0/L1) + file | L0[^tencentdb] |
| [ai-memory](ai-memory-overview.md) | Fabio Akita | Một binary Rust | MIT | 3.4.2 (+56 commit) | D + E | **Wiki Markdown có git** | **Mặc định**[^ai-memory] |
| [GBrain](gbrain-overview.md) | Garry Tan | TypeScript / Bun | MIT | 0.60.593.0 | D (+B, E) | **Repo Markdown** (+ state chỉ có trong DB) | Keyless[^gbrain] |
| [Headroom](headroom-overview.md) | Headroom | Python 3.11+ có Rust extension; SDK TS | Apache-2.0 | `headroom-ai` 0.43.1 | F | Store cục bộ dạng plaintext | Có[^headroom] |

### Ma trận hướng × hệ

| Hướng | Mem0 | Cognee | Hindsight | Hy SDK | MemHub | TencentDB | ai-memory | GBrain | Headroom |
|---|---|---|---|---|---|---|---|---|---|
| A. Fact layer | ●●● | | ● | ● | | ● | | ● | |
| B. Knowledge graph | | ●●● | ●● | ●● (`ultra`) | | ● (wiki, CodeGraph) | ● (typed edge) | ●● | |
| C. Cognitive/hierarchical | | ● (improve) | ●●● | ●●● | ●● | ●●● | ● (tier, decay) | ●● (facts→takes, dream) | |
| D. Compiled Markdown | | | ● (page projection) | | | ●● (MemoryKnowledge) | ●●● | ●●● | |
| E. Cross-harness hub | ● (plugin) | ● (MCP) | ●● (48 integration) | ● (plugin) | ●●● | ●●● (proxy) | ●●● | ●● | ● (proxy) |
| F. Context compression | | | | | | | | | ●●● |

●●● = trọng tâm, ●● = mạnh, ● = có (đánh giá **Synthesis** dựa trên các trang chuyên đề).

## Các hướng thiết kế

### A. Fact memory layer

**Ý tưởng:** mỗi lần ghi, LLM trích xuất một vài fact ngắn; retrieval là semantic top-k cộng boost. **Đại diện:** Mem0.
- **Ưu điểm:** đơn giản; nhiều adapter (24 vector store, 18 LLM, 12 embedding); có managed platform và SDK cho hai ngôn ngữ.
- **Nhược điểm:** fact rời, dedup chỉ bằng hash trong top-10; không có consolidation; graph store đã bị gỡ khỏi OSS; benchmark headline là của managed platform.[^mem0]

### B. Knowledge-graph memory engine

**Ý tưởng:** dựng graph entity/relationship và summary từ tài liệu và hội thoại, rồi truy vấn bằng nhiều lane (graph completion, triplet, Cypher, temporal, code). **Đại diện:** Cognee. GBrain có typed graph không cần LLM; Hy `ultra` có schema graph trên Kuzu.
- **Ưu điểm:** trả lời được câu hỏi quan hệ và multi-hop; cùng một engine cho cả memory lẫn tài liệu/code, gần GraphRAG.
- **Nhược điểm:** cognify tốn LLM; nhiều store phải vận hành; xoá chỉ best-effort.[^cognee][^gbrain][^hy-memory]

### C. Cognitive / hierarchical learning memory

**Ý tưởng:** memory phân tầng như nhận thức (raw → fact → summary/observation → schema/persona/mental model). Có tiến trình "học" chạy nền hoặc được gọi tường minh. **Đại diện:** Hindsight, Hy Memory, TencentDB MemoryCore.
- **Ưu điểm:** tự hợp nhất và giảm nhiễu; có profile/persona; Hindsight có agent `reflect` để suy luận.
- **Nhược điểm:** LLM là lõi của write path, nên chi phí và độ trễ khi ghi cao hơn; độ phức tạp vận hành; dễ sinh "sự thật" do model tạo ra nếu reconcile sai (ví dụ subject gate của Hy coding tắt mặc định).[^hindsight][^hy-memory][^tencentdb]

### D. Compiled Markdown brain / wiki

**Ý tưởng:** tri thức được *biên dịch* thành các trang Markdown người đọc và sửa được, có version bằng git; DB chỉ là index dựng lại được. Ý tưởng này kế thừa "LLM Wiki" (ai-memory nêu đích danh Karpathy LLM Wiki). **Đại diện:** ai-memory, GBrain. TencentDB MemoryKnowledge và knowledge page của Hindsight là các biến thể "trang dạng view".
- **Ưu điểm:** minh bạch, grep được, mở được bằng Obsidian, review được qua git; không bị khoá vào vendor; chạy được không cần LLM.
- **Nhược điểm:** đồng bộ file ↔ DB (ai-memory không có transaction xuyên giữa hai bên; GBrain có state chỉ nằm trong DB); khó dùng cho tenancy lớn.[^ai-memory][^gbrain][^tencentdb][^hindsight]

### E. Local-first / cross-harness memory hub

**Ý tưởng:** một memory dùng chung cho nhiều agent hoặc harness. Kênh tích hợp là sản phẩm chính.
- **ai-memory:** hook + MCP, handoff, workstream.
- **MemHub:** import + host bridge, một Runtime mỗi máy.
- **TencentDB:** proxy không cần plugin.
- **Hindsight coding-agents:** mỗi repo một bank.

**Nhược điểm:** bề mặt rủi ro rộng (hook, file cấu hình của harness, proxy thấy toàn bộ traffic); cách hành xử phụ thuộc vào từng harness.[^ai-memory][^hy-memory][^tencentdb][^hindsight]

### F. Context compression

**Đại diện:** Headroom. Nó nén output của tool và message theo loại nội dung, giữ nguyên provider prefix cache, và có CCR để lấy lại bản gốc trong TTL 1800 giây. Phần memory và `learn` chỉ là phụ. Hướng này **bổ trợ** cho A–E: giảm token trong session hiện tại, còn A–E giữ tri thức giữa các session.[^headroom]

## Profile từng hệ

### Mem0
- **Mô hình:** memory record trong vector store; entity collection chỉ để boost; SQLite giữ history.
- **Ghi:** một lời gọi LLM để trích xuất fact additive; dedup bằng hash.
- **Đọc:** semantic + boost BM25/entity; điểm không so sánh được giữa các query.
- **Bề mặt:** SDK Py/TS, hosted client, server tự host + dashboard, CLI, 16 thư mục integration.
- **Rủi ro:** route của server không gắn identifier với principal; server cài lại `mem0ai` không pin version; CLI sao API key vào file cấu hình.
- **Benchmark:** LoCoMo 92.5 / LongMemEval 94.4, nhưng là của managed platform.

Chi tiết: [write](mem0-write-and-storage.md), [retrieval](mem0-retrieval.md), [security](mem0-server-and-security.md).[^mem0]

### Cognee
- **Mô hình:** document → chunk → graph + summary, gom theo dataset; session cache.
- **Ghi:** `add` + `cognify`, có early indexing.
- **Đọc:** `recall` với router regex qua 21 `SearchType`; Cypher không route tự động.
- **Học:** improve registry nhiều stage (session distillation, conflict review…).
- **Storage mặc định:** SQLite + Ladybug + LanceDB.
- **Bảo mật:** access control và auth bật mặc định; `prune_system` không kiểm tra quyền.
- **Benchmark:** BEAM 0.79 @100K (mẫu nhỏ).

Chi tiết: [ingestion](cognee-ingestion-and-code-graphs.md), [retrieval](cognee-retrieval.md).[^cognee]

### Hindsight
- **Mô hình:** bank → fact `world`/`experience` → observation (có proof count) → mental model/knowledge page; bốn loại link.
- **Ghi:** `retain` dùng LLM, entity resolution, link nhân quả, delta retain.
- **Đọc:** 4 arm, RRF, cross-encoder (`hs-rerank-1` mặc định), boost, budget.
- **Suy luận:** `reflect` là agent loop 10 vòng; disposition traits; directive.
- **Tối ưu chi phí:** decision model 0.8B.
- **Storage:** Postgres/pgvector, không có lớp abstraction.
- **Vận hành:** API và worker tách riêng; Helm; Prometheus.
- **Tích hợp:** 48 integration; 27/30 tool MCP.
- **Rủi ro:** host mặc định `0.0.0.0`, MCP mở mặc định.
- **Benchmark:** LongMemEval 94.6%, BEAM 10M 64.1.

Chi tiết: [recall](hindsight-recall-pipeline.md), [reflect](hindsight-reflect-agent.md), [consolidation](hindsight-consolidation-and-mental-models.md).[^hindsight]

### Hy Memory SDK
- **Mô hình chat:** L0–L7. **Working/coding:** fact + experience + diff chain.
- **Mode:** `lite` (raw, không LLM) / `pro` (extract + reconcile) / `ultra` (graph + System 2 `evolve()`).
- **Đọc:** nhiều channel, cộng điểm rồi blend RRF, graph rerank theo `TYPE_PRIOR`, strength decay.
- **Vận hành:** hai event loop; workload semaphore; snapshot/re-embed (chỉ Chroma).
- **Rủi ro:** HTTP server không có auth và CORS `*`; plugin OpenClaw tự cài bản PyPI mới nhất.
- **Benchmark:** CMB (TriLink 43.1% Resolved).

Chi tiết: [chat write](hy-memory-chat-hierarchy-and-write-path.md), [chat retrieval](hy-memory-chat-retrieval-pipeline.md), [coding](hy-memory-working-coding-memory.md).[^hy-memory]

### MemHub
Sản phẩm local-first xây trên Hy SDK.
- **Kiến trúc:** một Runtime cho mỗi máy (LaunchAgent/systemd); durable write queue theo event-time; evolve hằng đêm lúc 03:00 ở `ultra`.
- **Nguồn dữ liệu:** import 11 host + 4 định dạng export, live sync.
- **Tích hợp:** host bridge 10 harness, MCP 3 tool.
- **Embedding:** đổi space có rollback; embedder ONNX tiếng Trung.
- **Quyền:** bốn quyền độc lập nhưng không có ACL theo memory.
- **Giới hạn:** không có model thì không có recall; chưa hỗ trợ Windows; bản preview.

Chi tiết: [architecture](memhub-product-architecture.md), [privacy](memhub-privacy-and-permissions.md).[^hy-memory]

### TencentDB Agent Memory
- **Kiến trúc:** bốn service. Core (L0–L3), Knowledge (wiki ingest bằng LLM, CodeGraph), Panel, Proxy (inject context, ghi turn, không cần plugin).
- **Đọc:** keyword/embedding/hybrid với RRF; L1 chỉ có qua tool, không auto-inject.
- **Tích hợp:** adapter cho claude-code, codex, opencode, openclaw, hermes, codebuddy, workbuddy, dsh.
- **Rủi ro:** `assertIsolation` fallback, key rỗng tắt auth, credential base64, SSRF check chưa đầy đủ.
- **Benchmark:** PersonaMem 48 → 76%.

Chi tiết: [pipeline](tencentdb-memory-pipeline.md), [security](tencentdb-security-deployment.md).[^tencentdb]

### ai-memory
- **Mô hình:** một binary Rust; wiki Markdown có git (OKF v0.2) là truth; SQLite là index derived (writer actor).
- **Mặc định zero-LLM:** hook ghi observation → trang session deterministic.
- **Đọc:** RRF qua 6 stream nhân authority; `as_of`; CJK.
- **Phối hợp agent:** handoff claim-once, workstream (`ai-memory run`), inbox, cross-project profile.
- **Lão hoá:** decay chỉ cho tier episodic; compaction/dedup/dream opt-in; auto-improve tự áp dụng khi có provider.
- **Bảo mật:** loopback, bearer ladder, grant theo project (user do proxy xác nhận bỏ qua); không telemetry.
- **Benchmark:** LongMemEval-S hit@5 0.951, có harness trong repo.

Chi tiết: [architecture](ai-memory-architecture.md), [retrieval](ai-memory-retrieval-pipeline.md), [consolidation](ai-memory-consolidation-and-aging.md).[^ai-memory]

### GBrain
- **Mô hình:** brain (DB) / source (repo); page = compiled truth + facts fence + timeline; facts (hot, bắt buộc provenance) và takes (cold, có holder và weight); 7 verb đã đóng băng.
- **Đọc:** 4 arm, RRF mức page, blend cosine 0.7/0.3, reranker Voyage, mode bundle; `think` có gap analysis.
- **Vận hành:** PGLite hoặc Postgres; Minions queue; dream 31 phase; ingest từ github/google/slack/meetings.
- **Tri thức hành vi:** 75 skill Markdown cùng RESOLVER.
- **Bảo mật:** OAuth 2.1, 10 scope, grant theo credential, 6 trust tier (mặc định chỉ flag); dự án tự liệt kê những gì *không* được ràng buộc.
- **Benchmark:** LongMemEval-S `recall_all@5` 95.53%, nhưng không tái lập được từ repo.

Chi tiết: [data model](gbrain-data-model-and-system-of-record.md), [memory model](gbrain-memory-model.md), [retrieval](gbrain-retrieval-pipeline.md).[^gbrain]

### Headroom
- **Chức năng chính:** nén context theo loại nội dung (JSON, code, log, HTML), CacheAligner, CCR (TTL 1800 giây).
- **Bề mặt:** library, proxy, `wrap`, MCP; proxy Rust riêng.
- **Phụ:** memory phân cấp (vector + FTS5); `learn` ghi bài học vào `CLAUDE.local.md`.
- **Rủi ro:** beacon bật mặc định; không mã hoá at-rest.
- **Benchmark:** tiết kiệm token 21–57% trên 4 kịch bản.

Chi tiết: [compression](headroom-compression.md), [CCR](headroom-cache-and-ccr.md).[^headroom]

## Điểm hội tụ (Synthesis)

1. **Hybrid retrieval + RRF `k = 60`** ở Hindsight, Hy, ai-memory, GBrain và TencentDB (khi không có hybrid native). Rerank bằng cross-encoder rồi cắt theo token budget là chuỗi phổ biến.
2. **Phân tầng memory:** raw → fact → tổng hợp → profile/persona/schema/mental model.
3. **Supersession có lịch sử** thay vì ghi đè.
4. **MCP + hook + chèn instruction** là cách tích hợp chuẩn với coding agent.
5. **Giảm phụ thuộc cloud:** embedder local (ai-memory, Hindsight, MemHub), decision model nhỏ (Hindsight), keyless (GBrain).
6. **Tách *expire* khỏi *purge*** và thừa nhận xoá chỉ là logical.

## Khác biệt cốt lõi (Synthesis)

| Trục | Một phía | Phía kia |
|---|---|---|
| LLM khi ghi | Lớp nâng cấp opt-in (ai-memory, GBrain, Hy `lite`) | Lõi bắt buộc (Hindsight, Mem0 inferred, TencentDB L1, Hy `pro`) |
| Source of truth | Markdown + git (ai-memory, GBrain) | DB (Mem0, Cognee, Hindsight, Hy, TencentDB) |
| Đơn vị xếp hạng | Page (ai-memory, GBrain) | Fact/unit (Mem0, Hindsight, Hy) |
| Ai nắm vòng đời ghi | Agent gọi tool/SDK (Mem0, Cognee, Hy SDK) | Hook/importer/proxy (ai-memory, MemHub, TencentDB, Headroom) |
| Tenancy | Đơn người dùng / workstation (ai-memory, MemHub) | Multi-tenant (Hindsight tenant extension, GBrain grant, Mem0 server) |
| Graph | Graph DB riêng (Cognee, Hy) | Bảng link trong RDBMS (Hindsight, GBrain, ai-memory) / không có (Mem0, Headroom) |
| Học | Sau mỗi lần ghi (Hindsight, Hy S1, TencentDB) | Theo lịch / idle (GBrain dream, ai-memory, MemHub) / tường minh (Hy `evolve()`, Cognee) |

## Gợi ý chọn theo kịch bản (Synthesis)

| Kịch bản | Lựa chọn hợp lý | Vì sao | Cần kiểm tra |
|---|---|---|---|
| App SaaS cần memory cho từng người dùng cuối, muốn có managed option | Mem0 | SDK đơn giản, nhiều adapter, có hosted | Tính năng/benchmark của platform khác OSS; tự làm isolation ở server |
| Memory + tri thức tài liệu/code dạng graph (GraphRAG) | Cognee | Nhiều lane graph, code graph, router | Chi phí `cognify`; ngữ nghĩa xoá; quyền của prune |
| Agent cần "học" và suy luận trên kinh nghiệm; đội vận hành quen Postgres | Hindsight | Observation/mental model, `reflect`, 48 integration, Helm | Đóng MCP và bind lại; chi phí LLM khi retain |
| Cá nhân hoá chat sâu (profile, intention, schema) | Hy Memory SDK | L0–L7, `ultra` + System 2 | Phải tự gọi `evolve()`; cần Kuzu; server không có auth |
| Coding agent làm việc dài, nhiều nhánh, nhiều lần revision | Hy coding (+ diff chain) hoặc Hindsight coding-agents | Fact/experience/diff chain (đánh giá bằng CMB); bank theo repo kèm git seed | Diff chain tắt mặc định; subject gate tắt mặc định |
| Một người dùng nhiều coding agent, muốn local, không cần API key, Markdown đọc được | ai-memory | Zero-LLM, handoff, workstream, hơn 20 harness | Auto-improve tự áp dụng khi bật LLM; Docker không auth |
| Memory chung trên máy cá nhân cho nhiều app AI (kể cả hội thoại cũ) | MemHub | Import + live sync + host bridge | Bản preview; không hỗ trợ Windows; cần model mới có recall |
| "Second brain" cá nhân hoặc công ty: nhiều nguồn (email, lịch, Slack, GitHub), có provenance, tự động hoá ban đêm | GBrain | Facts/takes, connector, dream, skill, OAuth grant | Thay đổi rất nhanh; DB không bị ràng buộc bởi grant |
| Đội agent dùng chung memory qua proxy, gắn với hạ tầng Tencent Cloud | TencentDB Agent Memory | Proxy không cần plugin, skill + wiki + CodeGraph | Audit isolation và auth trước khi expose |
| Giảm token và chi phí của session hiện tại | Headroom, kết hợp với bất kỳ hệ nào ở trên | Nén theo nội dung, CCR | Tắt beacon nếu cần |

## Khoảng trống của wiki

- Chưa có framework RAG chuyên dụng, chưa có các hệ được nhắc tới nhưng chưa ingest (Zep/Graphiti, Letta, LangMem, MemOS, OpenViking; xem [ai-memory comparison claims](ai-memory-comparison-claims.md)).
- Chưa có lần chạy thực nào (benchmark chung, đo độ trễ, pentest).
- Các trang về CI/release/contributor chưa được tổng hợp chéo.

## Coverage và giới hạn

- Survey tổng hợp từ các concept đang ở trạng thái `draft`/`stable`, chủ yếu là static inspection được giao cho subagent. Khi các trang gốc thay đổi, các trang trong cụm này cần cập nhật. `stale_after` lấy theo trang gốc sớm hết hạn nhất.
- Ma trận ●/●●/●●● và các gợi ý chọn là **Synthesis**, phản ánh trọng tâm thiết kế chứ không phải chất lượng đã đo.
- Bảng so sánh do ai-memory tự viết ([comparison claims](ai-memory-comparison-claims.md)) xếp Mem0 vào nhóm "facts" và Cognee vào nhóm "temporal knowledge graph". Phân loại đó khớp với hướng A/B ở đây, nhưng vẫn là quan điểm của một bên.

## Relationships

- Has parts: [data model and write comparison](agent-memory-data-model-and-write-comparison.md), [retrieval comparison](agent-memory-retrieval-comparison.md), [integration and operations comparison](agent-memory-integration-and-operations-comparison.md), [security and privacy comparison](agent-memory-security-and-privacy-comparison.md), [benchmarks comparison](agent-memory-benchmarks-comparison.md).
- Uses: các overview trong [Bản đồ nhanh](#bản-đồ-nhanh), cùng [CMB](cmb-coding-memory-benchmark.md).
- Related: [ai-memory comparison claims](ai-memory-comparison-claims.md) là góc nhìn tự báo cáo của một bên; cụm này đối chiếu trên các nguồn đã compile.

[^ai-memory]: [overview](ai-memory-overview.md), [architecture](ai-memory-architecture.md), [retrieval](ai-memory-retrieval-pipeline.md), [consolidation](ai-memory-consolidation-and-aging.md), [auth/security](ai-memory-auth-and-security.md), [handoffs](ai-memory-handoffs-and-messaging.md), [workstreams](ai-memory-managed-workstreams.md), [evals](ai-memory-evals-and-benchmarks.md), [comparison claims](ai-memory-comparison-claims.md). Raw: `README.md` "Why ai-memory", "Architecture", "Built on the shoulders of"; `Cargo.toml::[workspace.package]`; `crates/ai-memory-store/src/reader.rs::hybrid_search_inner`; `docs/benchmarks/longmemeval-s-3.4.0-release.md` "Results"; `LICENSE` dòng 1 (MIT, kiểm tra trong phiên này).
[^cognee]: [overview](cognee-overview.md), [ingestion](cognee-ingestion-and-code-graphs.md), [retrieval](cognee-retrieval.md), [sessions](cognee-sessions-and-improvement.md), [storage/security](cognee-storage-and-security.md), [benchmarks](cognee-benchmarks.md). Raw: `pyproject.toml::[project]`; `cognee/api/v1/cognify/cognify.py::get_default_tasks`; `cognee/api/v1/recall/query_router.py::_RULES`; `cognee/modules/search/types/SearchType.py::SearchType`; `cognee/modules/data/deletion/prune_system.py::prune_system`; `LICENSE` (Apache-2.0, kiểm tra trong phiên này).
[^gbrain]: [overview](gbrain-overview.md), [data model](gbrain-data-model-and-system-of-record.md), [memory model](gbrain-memory-model.md), [retrieval](gbrain-retrieval-pipeline.md), [knowledge graph](gbrain-knowledge-graph.md), [architecture](gbrain-architecture-and-engines.md), [authorization](gbrain-authorization-and-security.md), [skills](gbrain-skills-and-resolver.md), [evals](gbrain-evals-and-benchmarks.md). Raw: `README.md` intro, "Architecture"; `VERSION`; `src/core/verbs.ts`; `src/core/search/mode.ts::MODE_BUNDLES`; `docs/architecture/system-of-record.md`; `docs/architecture/brains-and-sources.md` "What confines remote callers"; `LICENSE` dòng 1–3.
[^headroom]: [overview](headroom-overview.md), [compression](headroom-compression.md), [cache/CCR](headroom-cache-and-ccr.md), [memory](headroom-memory.md), [learning](headroom-learning.md), [privacy](headroom-privacy-and-security.md), [benchmarks](headroom-benchmarks.md). Raw: `pyproject.toml` `[project]`; `headroom/transforms/content_router.py::ContentRouter`; `headroom/cache/compression_store.py::DEFAULT_CCR_TTL_SECONDS`; `headroom/telemetry/beacon.py::BEACON_DEFAULT_ON`; `README.md` § Proof; `LICENSE` (Apache-2.0, kiểm tra trong phiên này).
[^hindsight]: [overview](hindsight-overview.md), [retain](hindsight-retain-pipeline.md), [recall](hindsight-recall-pipeline.md), [reflect](hindsight-reflect-agent.md), [consolidation](hindsight-consolidation-and-mental-models.md), [decision models](hindsight-decision-models.md), [banks](hindsight-memory-banks.md), [storage](hindsight-storage-and-configuration.md), [API surface](hindsight-api-surface.md), [integrations](hindsight-integrations.md), [coding agents](hindsight-coding-agents.md), [benchmarks](hindsight-benchmarks-and-testing.md). Raw: `README.md` "What is Hindsight?", "Core Concepts"; `hindsight-api-slim/pyproject.toml` (1.2.0, MIT); `hindsight_api/config.py::HindsightConfig`; `hindsight-docs/docs/developer/mcp-server.md`; `hindsight-docs/blog/2026-03-23-agent-memory-benchmark.mdx`.
[^hy-memory]: [overview](hy-memory-overview.md), [chat hierarchy](hy-memory-chat-hierarchy-and-write-path.md), [chat retrieval](hy-memory-chat-retrieval-pipeline.md), [working/coding](hy-memory-working-coding-memory.md), [System 2](hy-memory-system2-evolution.md), [SDK API](hy-memory-sdk-api-and-config.md), [plugins](hy-memory-plugins-openclaw-hermes.md), [MemHub architecture](memhub-product-architecture.md), [MemHub modes](memhub-memory-modes-and-write-queue.md), [MemHub privacy](memhub-privacy-and-permissions.md), [CMB](cmb-coding-memory-benchmark.md). Raw: `README.md::System Architecture`, `::Modes`; `hy_memory/models/memory.py::MemoryLayer`; `hy_memory/client.py::HyMemoryClient`; `hy_memory/server.py`; `memhub/docs/ARCHITECTURE.md`; `docs/papers/CMB_…pdf` Table 2 (tr. 7); `LICENSE` dòng 5 (Apache-2.0, kiểm tra trong phiên này).
[^mem0]: [overview](mem0-overview.md), [write/storage](mem0-write-and-storage.md), [retrieval](mem0-retrieval.md), [providers](mem0-providers.md), [clients](mem0-clients-and-integrations.md), [server/security](mem0-server-and-security.md), [benchmarks](mem0-benchmarks.md). Raw: `mem0/memory/main.py::Memory._add_to_vector_store`, `Memory.search`; `server/main.py::search_memories`; `README.md::New Memory Algorithm (April 2026)`; `pyproject.toml::[project]` `version = "2.2.1"`, `LICENSE` (Apache-2.0) và danh sách `mem0/{vector_stores,llms,embeddings}/`, `integrations/`, tất cả kiểm tra trong phiên này.
[^tencentdb]: [overview](tencentdb-agent-memory-overview.md), [memory pipeline](tencentdb-memory-pipeline.md), [retrieval/storage](tencentdb-retrieval-storage.md), [knowledge service](tencentdb-knowledge-service.md), [proxy](tencentdb-proxy-integrations.md), [security](tencentdb-security-deployment.md). Raw: `README.md` "Technical Implementation", "Benchmark"; `MemoryCore/src/core/store/isolation.ts::assertIsolation`; `MemoryProxy/src/injection/index.ts::buildPipelineBundle`; `MemoryCore/package.json` `version`, `LICENSE` dòng 5 (MIT) và danh sách `agents/`, tất cả kiểm tra trong phiên này.
