---
type: Synthesis
title: Agent memory data model, write path and lifecycle comparison
description: So sánh đơn vị memory, phân tầng, storage backend, write path, mức phụ thuộc LLM, dedup/reconcile, consolidation, decay và ngữ nghĩa xoá giữa tám hệ agent-memory trong wiki.
tags: [agent-memory, survey, comparison, data-model, write-path, consolidation]
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

# Agent memory data model, write path and lifecycle comparison

Trang này thuộc cụm [Agent memory landscape survey](agent-memory-landscape-survey.md) và đi sâu vào phía *ghi*: memory được lưu dưới dạng nào, ghi vào bằng cách nào, được hợp nhất ra sao, và bị quên hoặc xoá theo cơ chế gì. Có ba trục khác biệt chính. (1) **Đơn vị memory**: một fact rời (Mem0), một node/chunk trong graph (Cognee), một fact/observation có kiểu (Hindsight), một tầng trong hierarchy (Hy, TencentDB), hay một trang Markdown (ai-memory, GBrain). (2) **LLM có nằm trên write path bắt buộc hay không.** (3) **Cập nhật bằng supersession có lịch sử, hay chỉ thêm (additive).** Mọi nhận định đều lấy từ các concept nguồn được dẫn trong footnote. Evidence class mặc định là **Observed**, tức static inspection được giao cho subagent và không chạy code; phần so sánh là **Synthesis**.

## 1. Đơn vị memory và phân tầng

| Hệ | Đơn vị cơ bản | Phân tầng / loại | Quan hệ |
|---|---|---|---|
| Mem0 | Memory record: text và metadata là payload của vector store | Không phân tầng. SQLite giữ history và một buffer giới hạn các message gần nhất | Có entity collection riêng, chỉ dùng để boost điểm. Prompt có yêu cầu `linked_memory_ids` nhưng không được lưu lại[^mem0] |
| Cognee | Document → chunk (đã embed) → graph (entity/relationship) + summary, gom theo dataset | Session cache tách riêng; các "lesson" sau distillation được lưu thành document | Knowledge graph, code graph[^cognee] |
| Hindsight | `memory_units` trong một **bank** | `fact_type`: `world`, `experience`, `observation`; phía trên còn có mental model, knowledge page và directive | `memory_links` gồm bốn loại: entity, temporal, semantic, causal; có hai chiều thời gian (lúc xảy ra và lúc được ghi nhận)[^hindsight] |
| Hy Memory (chat) | Node trong vector store, mỗi node thuộc một tầng | L0 profile · L1 raw · L2 fact · L3 summary · L4 identity (legacy) · L5 knowledge (chưa làm) · L6 schema · L7 intention | Evolution chain; graph projection ở `pro`/`ultra`[^hy-memory] |
| Hy Memory (working/coding) | **Fact** (mỗi session đúng một fact) + **experience** (có thể dùng lại) | Hai tầng, liên kết chéo qua `derived_experience_ids` ↔ `source_fact_ids`; coding có thêm diff chain | Fact chain tối đa 8 thế hệ[^hy-memory] |
| TencentDB | Record L0/L1 trong database + file cho scene/persona | L0 hội thoại · L1 atomic fact · L2 scene block · L3 core/persona; ngoài ra có asset skill, wiki, CodeGraph | Page-link graph trong wiki; CodeGraph có caller/callee[^tencentdb] |
| ai-memory | **Page Markdown** (OKF v0.2) cùng observation và session | `tier`: working/episodic/semantic/procedural; `kind`: rule/decision/gotcha/procedure/fact | `links` với typed edge `causes`/`fixes`/`contradicts`; entity[^ai-memory] |
| GBrain | **Page Markdown** gồm compiled truth, facts fence và timeline | **Facts** (hot: event/preference/commitment/belief/fact/idea) · **takes** (cold: fact/take/bet/hunch, kèm holder và weight) · core memory (`always_load`) | `links` với typed edge (`works_at`, `invested_in`, …); 15 page type trong schema pack mặc định[^gbrain] |
| Headroom | `Memory` mang user/session/agent/turn id, khoảng hiệu lực thời gian và lineage | Theo scope; memory quan trọng ở scope thấp có thể "bubble" thành bản sao ở user scope | Có adapter graph (`sqlite_graph`) nhưng chưa được inspect[^headroom] |

**Synthesis.** Có ba "trường phái" mô hình hoá:
- *Fact phẳng*: Mem0.
- *Hierarchy theo mức trừu tượng*: Hy, TencentDB, các tầng của Hindsight. Chúng giống nhau ở chỗ raw → atomic fact → tổng hợp → profile/persona/schema.
- *Trang tài liệu*: ai-memory, GBrain. Mỗi trang là một đơn vị người đọc được, có frontmatter.

GBrain là hệ duy nhất tách rõ *ai tin điều gì* (takes có `holder` và `weight`) khỏi *sự thật về một entity* (facts).[^gbrain]

## 2. Storage và source of truth

| Hệ | Source of truth | Backend mặc định | Tuỳ chọn / ghi chú |
|---|---|---|---|
| Mem0 | Payload trong vector store | OpenAI + Qdrant | 24 module vector store, 18 module LLM, 12 module embedding (đếm trong phiên này, không tính `base`/`configs`). Có mặt trong registry không có nghĩa là có đủ tính năng như nhau; server dùng Postgres/pgvector[^mem0] |
| Cognee | Tách store theo vai trò | SQLite (metadata/cache), Ladybug (graph), LanceDB (vector) | Adapter graph: kuzu, ladybug, neo4j, neptune, turso, postgres_demo; vector: lancedb, pgvector, turso (theo danh sách thư mục, chưa kiểm tra parity). Mã hoá file storage không bao gồm graph, vector hay relational store[^cognee] |
| Hindsight | PostgreSQL 15+ có pgvector, hoặc Oracle 23ai | `pg0` embedded (cần extra `embedded-db`) | Vector extension: pgvector, pgvectorscale/pg_diskann, vchord, scann. Text search: native, vchord, pg_textsearch, pgroonga, pg_search. 116 Alembic revision; embedding mặc định 384 chiều; *không* có lớp storage abstraction[^hindsight] |
| Hy Memory | Các store của SDK | Chroma + Kuzu + SQLite cache + SQLite history | Qdrant, FAISS, Neo4j, MySQL. Tên collection có hậu tố `_{dims}` nên các không gian embedding không lẫn vào nhau. Store coding/working là các file SQLite riêng[^hy-memory] |
| MemHub | Data plane của SDK (`governed-v2`) | Kế thừa từ SDK | `one-memory.sqlite3` chỉ chứa grant, queue, receipt và tham chiếu `memory_id`, không chứa memory[^hy-memory] |
| TencentDB | Database cho L0/L1 + file cho conversation/scene/persona/checkpoint | SQLite (FTS5 + bảng vector) | Tencent Cloud VectorDB (hybrid native); MongoDB (dense search là no-op trong snapshot)[^tencentdb] |
| ai-memory | **Wiki Markdown có git** | SQLite derived: WAL, một writer actor (channel 1024), pool 4 reader | 101 migration; FTS5 + chỉ mục bigram cho CJK; vector được scan bằng Rust, không dùng `sqlite-vec`. Không có transaction xuyên giữa file và DB[^ai-memory] |
| GBrain | **Repo Markdown** (với tri thức dạng file) | PGLite (Postgres 17 chạy WASM) | Postgres + pgvector cho brain chia sẻ hoặc lớn. Một số state chỉ có trong DB (raw_data, OAuth token, queue, belief ledger), vì vậy Markdown export không thay được backup DB[^gbrain] |
| Headroom | Store cục bộ dạng plaintext | Memory store + vector + FTS5 | Thư mục adapter có `hnsw`, `sqlite_vector`, `fts5`, `sqlite_graph`. Các component được ghi tuần tự nên có thể lệch index nếu lỗi giữa chừng[^headroom] |

## 3. Write path chi tiết

**Mem0 (OSS).** `add` lấy tối đa 10 memory hiện có và 10 message gần nhất của session, rồi gọi LLM **một lần** để trích xuất các fact *additive*. Các fact được embed và ghi vào vector store; nếu insert theo batch thất bại thì có fallback ghi từng record. JSON hỏng được coi như kết quả trích xuất rỗng. `infer=False` ghi thẳng từng message không phải system.[^mem0]

**Cognee.** `remember` điều phối hai bước: `add` (staging) và `cognify`. Khi bật *early indexing*, một pipeline không dùng LLM sẽ chunk và embed trước, sau đó pipeline graph mới chạy trích xuất graph và summary bằng LLM. Hai bước có run record và ranh giới rollback riêng, nên nếu trích xuất lỗi thì chunk vẫn tìm được (Reported). Code graph dựa vào executable `enola` bên ngoài.[^cognee]

**Hindsight.** `retain_batch` chạy theo thứ tự:
1. Kiểm tra bank và embedding, chunk 3000 ký tự.
2. Quyết định có dùng *delta retain* hay không.
3. LLM trích xuất fact. Có các mode `concise`/`verbose`/`custom`/`verbatim`/`chunks`; Batch API là tuỳ chọn.
4. Entity resolution: trigram mặc định, `entity_labels` match chính xác.
5. Lưu, rồi tạo link temporal/semantic (ngưỡng 0.7, top-50)/causal.
6. Kích hoạt consolidation bất đồng bộ.

Có thể đính kèm ảnh và file; khi đó cần VLM.[^hindsight]

**Hy Memory, System 1 (chat).**
1. Ghi `L1_RAW`.
2. Nếu mode khác `lite`: một lời gọi LLM trả về `memory`, `intentions`, `basic_info`.
3. Upsert L0 (bản cũ thành `superseded`), rồi dedup bằng cosine trong batch.
4. **Reconcile** với memory hiện có, khoá tuần tự theo user. Các op là `ADD`, `SUPERSEDE` (khi mâu thuẫn: bản cũ → `SHADOW` và nối vào evolution chain) và `UPDATE` (bản cũ → `SHADOW`, không nối chain).
5. L7 intention bỏ qua reconcile; L1 chuyển thành `SHADOW`.

Từ 2.0.13, khi có lỗi thì write **fail closed** và trả mã lỗi thay vì lưu raw làm fallback.[^hy-memory]

**Hy Memory (working/coding).** Mỗi trace sinh ra một lời gọi LLM, cho ra 0–1 fact và các experience. Experience được reconcile bằng `ADD/UPDATE/DELETE/SKIP`, fact bằng `INSERT/SUPERSEDE`. **Cả hai quyết định phải thành công thì mới ghi gì xuống.** Write chỉ có hiệu lực khi có tool-call trace và mode là `pro`/`ultra`. Diff chain ghi mọi revision code mà không gọi LLM hay embedding.[^hy-memory]

**MemHub.** Mỗi job trong queue là một chunk hội thoại cuối cùng, tương ứng đúng một lần `add()` vào SDK. Job được xếp theo cửa sổ event-time 10 phút, có *first-import barrier*, cửa sổ trích xuất mặc định 90 ngày và tỉ lệ 4 job mới : 1 job tồn. Nếu không có model sinh thì cũng **không có raw để recall**, vì raw chỉ được ghi bên trong `add`.[^hy-memory]

**TencentDB.** `performAutoCapture` ghi L0 có checkpoint và đã sanitize, sau đó scheduler chạy L1 extraction (kèm dedup) → L2 scene → L3 persona, tất cả bất đồng bộ. Seed runtime chỉ chờ L1 rảnh, nên L2/L3 có thể vẫn đang chạy (Reported).[^tencentdb]

**ai-memory.** Hook ghi observation đã sanitize. Khi `SessionEnd`, hệ sinh một trang `sessions/<id>.md` **deterministic** (500 dòng observation, lấy 250 đầu và 250 cuối), không gọi LLM. Consolidation bằng LLM là opt-in (`consolidate_on_session_end=false`), tạo ra 1–5 cập nhật trang kiểu Rule/Decision/Gotcha/Procedure/Fact, với budget 100k token vào / 32k ra và tối đa 3 lần retry. Mỗi lần ghi tạo một phiên bản mới qua supersession và một checkpoint libgit2.[^ai-memory]

**GBrain.** Có hai đường vào:
- **Sync** từ git diff. Delete trong git là soft delete, khôi phục được trong 72 giờ. Có van chặn xoá hàng loạt (500 file / 1%).
- **Ingest** từ source kind (github, google, meetings, slack), connector, capture và webhook.

Agent ghi bằng verb `remember`, bắt buộc có `provenance`, và nhận lại trạng thái `inserted|duplicate|superseded`. Auto-link không dùng LLM chỉ chạy trên `put_page` cục bộ được tin cậy. Fact được hấp thụ qua job `facts-absorb`, có giới hạn chi phí ($1/lần chạy, $5/ngày; Reported).[^gbrain]

**Headroom.** `HierarchicalMemory.add` cập nhật memory store, vector index, text index và cache theo tuần tự. Lệnh save qua MCP không thay thế memory cũ tương tự, nên muốn sửa thì phải đi qua update tường minh.[^headroom]

## 4. Mức phụ thuộc LLM khi ghi

| Hệ | Ghi được khi không có LLM | Cần LLM cho |
|---|---|---|
| ai-memory | **Có, đây là mặc định**: trang session deterministic | Consolidation, dream, auto-improve, profile (đều opt-in hoặc chỉ chạy khi có provider)[^ai-memory] |
| GBrain | **Có**: keyless, keyword search, typed link | Enrichment, `think`, extract facts, một số phase của dream cycle[^gbrain] |
| Hy Memory | Có, ở mode `lite` (chỉ raw) | `pro`/`ultra`; MemHub không có model thì không có recall[^hy-memory] |
| Cognee | Một phần: early indexing ở mức chunk | Graph và summary từ `cognify`[^cognee] |
| Mem0 | `infer=False` (raw message) | Trích xuất fact ở chế độ mặc định[^mem0] |
| TencentDB | Ghi L0 | L1–L3[^tencentdb] |
| Hindsight | Không đáng kể (mode `chunks`/`verbatim` vẫn đi qua retain) | Retain, consolidation, reflect. Decision model giảm số lời gọi nhưng không loại bỏ được LLM[^hindsight] |
| Headroom | Có (nén deterministic) | `headroom learn`[^headroom] |

## 5. Dedup, reconcile và cập nhật

| Hệ | Dedup | Cập nhật / mâu thuẫn |
|---|---|---|
| Mem0 | Hash văn bản giống hệt nhau, chỉ so trong top-10 đã lấy và batch hiện tại; không dedup theo ngữ nghĩa | Update/delete là các API riêng[^mem0] |
| Cognee | Novelty check trong session distillation | Stage `conflict review` trong improve registry[^cognee] |
| Hindsight | Entity resolution; observation dedup ở cosine ≥ 0.97 (chỉ Postgres); delta retain giữ lại fact của chunk không đổi | Observation được *refine*, không ghi đè; proof count tăng hoặc giảm[^hindsight] |
| Hy Memory | Cosine trong batch extract; reconcile dùng retrieval kết hợp vector + BM25 | `SUPERSEDE`/`UPDATE` đẩy bản cũ về `SHADOW`. Placeholder L0 không được supersede giá trị thật. Subject gate của coding **tắt mặc định**, nên có thể merge nhầm giữa các subject khác nhau[^hy-memory] |
| TencentDB | `batchDedup` ở L1 | Không có chi tiết trong wiki[^tencentdb] |
| ai-memory | Body/frontmatter giống hệt thì no-op; dedup cụm "cold" bằng DBSCAN (opt-in, cần embedder) | Supersession; cảnh báo cặp có cosine 0.4–0.75; `contradicts` edge; belief strength ∈ [0, 0.95][^ai-memory] |
| GBrain | `remember` trả về `duplicate` nếu đã có | `--replaces` (không gọi model), withdrawal (từ chối nhớ lại claim đã rút), ba cơ chế phát hiện contradiction chỉ *đề xuất*, không tự áp dụng[^gbrain] |
| Headroom | Save không thay memory tương tự | Supersede giữ lịch sử nhưng gỡ bản cũ khỏi index[^headroom] |

## 6. Consolidation và tiến hoá

- **Hindsight:** auto-consolidation chạy sau retain/delete/update, batch 50 và LLM batch 8. Có các chiến lược scope `combined`/`per_tag`/…. *Mental model* refresh theo `full`/`delta`, theo cron hoặc sau mỗi lần consolidation; giữ 50 bản lịch sử; delta gate tối đa 200 memory. *Knowledge page* được dựng từ observation và có thể project ra đĩa (`hindsight fs mount`). Decision-model triage được báo cáo giảm khoảng 40% số lời gọi LLM (Reported).[^hindsight]
- **Hy Memory System 2 (`ultra`):**
  - Không bao giờ tự kích hoạt; phải gọi `evolve()`, và lời gọi này đồng bộ, không idempotent.
  - Gom cụm fact bằng DBSCAN, tối đa 128 batch, 24 fact mỗi batch. **Mỗi batch là một lời gọi LLM** trả về mảng operation trên graph (create/update/add_edge/revise_schema/retire_schema…).
  - *Cross-domain sweeper* quy nạp "core schema" khi có ≥ 5 basic schema.
  - MemHub lên lịch evolve hằng đêm lúc 03:00, `EVOLVE_MAX_ROUNDS=20`.[^hy-memory]
- **GBrain dream cycle:** 31 phase có thứ tự cố định. Ví dụ: `consolidate` (facts → takes), `propose_takes`, `grade_takes`, `edge_contradictions`, `claim_conflicts`, `facts_drain`, `skillopt`, `embed`, `purge`. Có khoá Postgres/file, chạy qua `gbrain dream` (cron), `autopilot` hoặc job Minions.[^gbrain]
- **ai-memory:**
  - Consolidation bằng LLM khi kết thúc session (opt-in).
  - *Auto-improve* **bật mặc định khi có LLM provider**: mỗi giờ, tối đa 5 đề xuất mỗi lần chạy, `min_confidence` 0.75, và **tự áp dụng** (`require_approval=false`). Chỉ được sửa trang dưới `_rules/` và `procedures/`.
  - *Dream* (opt-in): chạy khi idle 300 giây, tối đa 8 cụm mỗi lần; trang nguồn bị supersede chứ không bị xoá.[^ai-memory]
- **Cognee:** improve registry chạy các stage theo thứ tự: feedback weighting → lưu session QA (stage fatal duy nhất) → agent trace → context extraction → session distillation → preference → truth subspace → conflict review → global-context index. Các stage còn lại là fail-open.[^cognee]
- **TencentDB:** pipeline L1 → L2 → L3 do scheduler điều khiển.[^tencentdb]
- **Mem0, Headroom:** không có consolidation nền trong wiki. Headroom có `learn` để ghi bài học vào file instruction của agent.[^mem0][^headroom]

## 7. Quên, decay và xoá

| Hệ | Decay / quên | Ngữ nghĩa xoá |
|---|---|---|
| Mem0 | Lọc bản hết hạn *sau* retrieval (riêng `get` xử lý khác) | Delete tường minh[^mem0] |
| Cognee | — | `forget(memory_only=True)` giữ file raw. Xoá là logical, còn sót fragment LanceDB. `prune_system` không kiểm tra quyền. Việc vô hiệu hoá session sau khi xoá là best-effort[^cognee] |
| Hindsight | Recency boost tuyến tính trong 365 ngày (α=0.2) lúc recall; không có decay khi lưu | Delete kích hoạt consolidation; `restore` xoá schema đích[^hindsight] |
| Hy Memory | Strength decay khi đọc: `(1+log(access))·exp(−idle_days/180)`; L7 hết hạn bị hạ thành fact thường | `delete`/`delete_all`; MemHub không bao giờ suy ra việc xoá từ chỗ dữ liệu vắng mặt; `delete-data` cần xác nhận hai lần[^hy-memory] |
| TencentDB | Không có trong wiki | Script purge xoá dữ liệu deployment[^tencentdb] |
| ai-memory | `salience·e^(−λΔt) + σ·ln(1+access)·e^(−μ·days)·breadth`, λ=0.02 (half-life khoảng 35 ngày), **chỉ áp cho tier episodic**; ngưỡng cold 0.20 | Hard delete sau 180 ngày; TTL ưu tiên hơn `pinned`. Purge là logical: `--compact` không phải forensic erasure, dữ liệu còn trong git history[^ai-memory] |
| GBrain | `recall.confidence_weighting` (opt-in) | `forget` = expire, vẫn giữ audit. Withdrawal; purge xoá text. Soft delete 72 giờ; chỉ CLI cục bộ được purge[^gbrain] |
| Headroom | CCR TTL 1800 giây (không phải xoá an toàn) | Supersede gỡ khỏi index[^headroom] |

## Nhận xét (Synthesis)

1. **Supersession có lịch sử** là cơ chế phổ biến nhất: Hy (`SHADOW` và evolution chain), ai-memory (phiên bản + git), GBrain (`superseded_by`, timeline), Hindsight (observation được refine). Mem0 OSS và Headroom thì chỉ thêm hoặc gỡ khỏi index.
2. **LLM trong write path quyết định chi phí và độ trễ khi ghi.** ai-memory và GBrain coi LLM là lớp nâng cấp. Hindsight, Hy `pro` và TencentDB L1 coi LLM là lõi. Hy là hệ duy nhất cho chọn mode `lite/pro/ultra` theo từng client.
3. **Consolidation có ba nhịp:** chạy sau mỗi lần ghi (Hindsight, Hy System 1, TencentDB), chạy theo lịch hoặc idle (GBrain dream, ai-memory auto-improve/dream, MemHub nightly evolve), và gọi tường minh (Hy `evolve()`, Cognee improve).
4. **Không hệ nào được inspect hứa hẹn xoá vật lý.** ai-memory và Cognee nói thẳng điều này; GBrain tách riêng expire và purge.

## Relationships

- Part of: [Agent memory landscape survey](agent-memory-landscape-survey.md).
- Related: [retrieval comparison](agent-memory-retrieval-comparison.md) (cách đọc dữ liệu được ghi ở đây), [security and privacy comparison](agent-memory-security-and-privacy-comparison.md) (xoá, egress).

[^ai-memory]: [architecture](ai-memory-architecture.md), [wiki storage/OKF](ai-memory-wiki-storage-and-okf.md), [capture/hooks](ai-memory-capture-and-hooks.md), [consolidation/aging](ai-memory-consolidation-and-aging.md), [auto-improvement](ai-memory-auto-improvement.md), [data handling](ai-memory-data-handling-and-lifecycle-ops.md). Raw: `crates/ai-memory-store/src/lib.rs::Store::open`, `src/writer.rs`; `crates/ai-memory-core/src/okf.rs::conform_frontmatter`, `src/page.rs::Tier`; `crates/ai-memory-hooks/src/synth.rs::synthesize_session_page`; `crates/ai-memory-store/src/decay.rs::DecayParams::default`; `crates/ai-memory-consolidate/src/{consolidator,sweep,dream,auto_improve}.rs`; `docs/lifecycle-ops.md` "TL;DR - safety matrix".
[^cognee]: [ingestion](cognee-ingestion-and-code-graphs.md), [sessions/improvement](cognee-sessions-and-improvement.md), [storage/security](cognee-storage-and-security.md). Raw: `cognee/api/v1/remember/remember.py::_remember_inner`; `cognee/api/v1/cognify/cognify.py::get_default_tasks`, `::get_indexing_tasks`; `cognee/modules/improve/registry.py::DEFAULT_STAGES`; `cognee/api/v1/forget/forget.py::forget`; `cognee/modules/data/deletion/prune_system.py::prune_system`; danh sách thư mục `cognee/infrastructure/databases/{graph,vector}/` (kiểm tra trong phiên này).
[^gbrain]: [data model](gbrain-data-model-and-system-of-record.md), [memory model](gbrain-memory-model.md), [sync/ingestion](gbrain-sync-and-ingestion.md), [dream cycle](gbrain-dream-cycle-and-autopilot.md), [knowledge graph](gbrain-knowledge-graph.md), [trust](gbrain-memory-trust-and-egress.md). Raw: `src/schema.sql` (`pages`, `links`); `docs/architecture/system-of-record.md` "The three categories"; `src/core/verbs.ts`; `docs/protocol/MEMORY_VERBS_v1.md` (remember, `--replaces`); `src/core/sync-reconcile.ts`; `src/core/cycle.ts::ALL_PHASES`; `docs/guides/facts-drain.md`.
[^headroom]: [memory](headroom-memory.md), [cache/CCR](headroom-cache-and-ccr.md), [learning](headroom-learning.md). Raw: `headroom/memory/core.py::HierarchicalMemory.add`, `supersede`, `_maybe_bubble`; `headroom/memory/mcp_server.py::_TOOLS`; `headroom/cache/compression_store.py::DEFAULT_CCR_TTL_SECONDS`; danh sách `headroom/memory/adapters/` (kiểm tra trong phiên này).
[^hindsight]: [retain](hindsight-retain-pipeline.md), [consolidation/mental models](hindsight-consolidation-and-mental-models.md), [storage/config](hindsight-storage-and-configuration.md), [recall](hindsight-recall-pipeline.md), [API surface](hindsight-api-surface.md). Raw: `hindsight-api-slim/hindsight_api/engine/retain/orchestrator.py::retain_batch`; `engine/retain/link_creation.py`; `engine/consolidation/consolidator.py::run_consolidation_job`; `hindsight-docs/docs/developer/observations.mdx`; `hindsight-docs/docs/developer/storage.md`; `config.py::HindsightConfig`.
[^hy-memory]: [chat hierarchy/write](hy-memory-chat-hierarchy-and-write-path.md), [working/coding](hy-memory-working-coding-memory.md), [diff chain](hy-memory-coding-diff-chain.md), [System 2](hy-memory-system2-evolution.md), [storage/reembed](hy-memory-storage-and-reembed.md), [chat retrieval](hy-memory-chat-retrieval-pipeline.md), [MemHub architecture](memhub-product-architecture.md), [MemHub modes/queue](memhub-memory-modes-and-write-queue.md). Raw: `hy_memory/models/memory.py::MemoryLayer`; `pipelines/writer.py::MemoryWriter.write`; `agent/reconciler.py::ReconcileOp`; `coding/writer.py::CodingWriter.write`; `pipelines/system2_agent.py::run_system2_agent`; `memhub/docs/contracts/memory-event-time-scheduling-v1.md`; `apps/core/src/one_memory/memory_evolution.py`.
[^mem0]: [write/storage](mem0-write-and-storage.md), [retrieval](mem0-retrieval.md), [providers](mem0-providers.md). Raw: `mem0/memory/main.py::Memory.add`, `Memory._add_to_vector_store`; `mem0/memory/storage.py::SQLiteManager.save_messages`; `mem0/configs/prompts.py::ADDITIVE_EXTRACTION_PROMPT`; danh sách `mem0/{vector_stores,llms,embeddings}/` (đếm trong phiên này).
[^tencentdb]: [memory pipeline](tencentdb-memory-pipeline.md), [retrieval/storage](tencentdb-retrieval-storage.md), [knowledge service](tencentdb-knowledge-service.md), [security/deployment](tencentdb-security-deployment.md). Raw: `MemoryCore/src/core/hooks/auto-capture.ts::performAutoCapture`; `MemoryCore/src/core/record/l1-dedup.ts::batchDedup`; `MemoryCore/src/core/seed/seed-runtime.ts::executeSeed`; `MemoryCore/src/core/storage/types.ts::StoragePaths`; `deploy/global-images/stop-all.sh`.
