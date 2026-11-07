---
type: Synthesis
title: Agent memory security and privacy comparison
description: So sánh tư thế bảo mật mặc định, mô hình tenancy/isolation, các lỗ hổng isolation đã quan sát, egress và telemetry, lọc secret, mã hoá và ngữ nghĩa xoá của tám hệ agent-memory, kèm checklist audit.
tags: [agent-memory, survey, comparison, security, privacy, isolation]
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

# Agent memory security and privacy comparison

Trang này thuộc cụm [Agent memory landscape survey](agent-memory-landscape-survey.md). Memory của agent chứa đúng những thứ nhạy cảm nhất: prompt, tool output, đường dẫn, quyết định, đôi khi cả secret. Vì vậy ba câu hỏi cần trả lời trước khi chọn hệ là: **ai đọc được memory của ai**, **text đi ra khỏi máy lúc nào**, và **xoá có thực sự là xoá không**.

Toàn bộ phát hiện dưới đây đến từ **static inspection**, không có pentest hay chạy thử, nên chúng là điểm cần audit chứ không phải lỗ hổng đã được khai thác. Hai hệ tự mô tả mình là single-tenant hoặc workstation (ai-memory, MemHub). Hai hệ có mô hình grant và tenant chi tiết nhất (GBrain, Hindsight qua extension).

## 1. Tư thế mặc định

| Hệ | Bind / exposure mặc định | Auth mặc định | Ghi chú |
|---|---|---|---|
| Mem0 server | Compose: API + Postgres + dashboard | Bearer / API key; có chế độ tắt auth (cho dev) | Compose bắt buộc đặt mật khẩu DB[^mem0] |
| Cognee | Docker / Compose | Bật backend access control mặc định, và auth kế thừa theo đó; muốn tắt auth khi access control vẫn bật thì bị ép bật lại | Muốn single-user thì tắt access control một cách tường minh[^cognee] |
| Hindsight | `HINDSIGHT_API_HOST=0.0.0.0`, port 8888 | **MCP mở mặc định**; Bearer qua `HINDSIGHT_API_MCP_AUTH_TOKEN` hoặc tenant extension (`ApiKeyTenantExtension`, Supabase JWT, static keys) | Mỗi bank cô lập chặt; Oracle cô lập tenant theo schema[^hindsight] |
| Hy SDK server | `127.0.0.1:19527` | **Không có auth**, CORS `*`; chỉ dành cho local/sidecar | Plugin Hermes yêu cầu HTTPS cho URL không phải loopback[^hy-memory] |
| MemHub | API cục bộ | Bearer hoặc cookie UI + kiểm tra origin; broker dùng envelope có chữ ký; endpoint lạ thì fail closed | Bốn quyền độc lập (xem §2)[^hy-memory] |
| TencentDB | Tuỳ script triển khai | Knowledge: **service key rỗng thì tắt bearer gate**, và một số đường read-only luôn bỏ qua gate; bearer gate của Core là tuỳ chọn | Code mặc định và file config mẫu của proxy khác nhau[^tencentdb] |
| ai-memory | `127.0.0.1:49374` | Root bearer được tạo khi `init`; **không có auth thì từ chối phục vụ HTTP ngoài loopback** (trừ cờ `--allow-insecure-no-auth`) | Bản Docker quick-start chưa có auth; có allowlist chống DNS rebinding[^ai-memory] |
| GBrain | Loopback; CORS mặc định chặn | OAuth 2.1 + token đã hash; DCR giới hạn ở `read write`; chủ sở hữu phải duyệt + PKCE; rate limit 30–60 req/60 giây; body tối đa 1 MiB | stdio không cần token, chỉ bị giới hạn bởi config[^gbrain] |
| Headroom | Proxy Python có bind policy; MCP HTTP mặc định loopback | MCP HTTP **không tự thêm auth** | Kiểm tra loopback không phải là ranh giới danh tính giữa các process cục bộ[^headroom] |

## 2. Mô hình tenancy và isolation

| Hệ | Đơn vị cô lập | Cơ chế |
|---|---|---|
| Mem0 | `user_id` / `agent_id` / run trong `filters` | Do caller truyền vào[^mem0] |
| Cognee | Dataset + user | ACL ở backend; tìm kiếm có xác thực qua `authorized_search`[^cognee] |
| Hindsight | **Bank** (thêm tenant schema nếu dùng extension) | Không rò rỉ giữa các bank; muốn cô lập theo user trong cùng bank thì dùng tag/metadata[^hindsight] |
| Hy Memory | `user_id:agent_id`; `source` include/exclude; coding: `workspace_id` + `branch` | Chroma lọc gần đúng; lọc theo branch **giữ cả các dòng `branch IS NULL`**; lọc vector không đẩy xuống DB nên SQLite mới là nguồn quyết định[^hy-memory] |
| MemHub | Cài đặt host + tool grant | **Không có ACL cho từng memory**; tìm xuyên harness được cho phép mặc định[^hy-memory] |
| TencentDB | Các trường danh tính / bucket | `assertIsolation` thay bằng bucket mặc định thay vì throw; SQLite lọc sau khi đã truy vấn[^tencentdb] |
| ai-memory | `(workspace, project)` + grant `read`/`write` với project `restricted` | Một choke point duy nhất là `authorize_project`. **User do proxy xác nhận bỏ qua grant `restricted`**[^ai-memory] |
| GBrain | Brain (DB) + source + grant theo từng credential | 10 scope, `source_grant` (federated/scalar/none), lọc private page, `takes_holders`, `readable_by`, giới hạn surface. Caller cục bộ thấy toàn bộ[^gbrain] |
| Headroom | Project (định tuyến từ request) | Project không xác định thì fallback về store rỗng, không về DB global chung[^headroom] |

## 3. Các điểm isolation và auth cần audit

- **Mem0:** route memory nhận identifier hoặc memory ID do caller cung cấp, **không gắn với principal đã xác thực**; liệt kê entity quét payload dùng chung. Vì vậy có auth chưa có nghĩa là các tenant được tách biệt (Synthesis).[^mem0]
- **TencentDB:**
  - Isolation helper dùng bucket mặc định thay vì báo lỗi.
  - Credential của nguồn knowledge chỉ được base64, không mã hoá.
  - Kiểm tra địa chỉ private chỉ xét chuỗi hostname, không xét địa chỉ DNS đã resolve, nên chưa chặn được SSRF hoàn toàn.
  - Callback của Panel bỏ qua kiểm tra header.
  - Session của Panel lưu trong localStorage.
  - Diagnostic dump có thể chứa nội dung request.[^tencentdb]
- **Cognee:** `prune_system` không kiểm tra quyền; giới hạn thư mục file cục bộ là opt-in; Cypher là rủi ro đã được nhận diện (không route tự động).[^cognee]
- **Hindsight:** MCP mở mặc định; webhook payload rời process (có ký HMAC); host mặc định là `0.0.0.0`.[^hindsight]
- **Hy SDK:** HTTP server không có auth. Plugin OpenClaw tự tạo venv, cài bản mới nhất từ PyPI mỗi lần khởi động nếu không pin version, và SIGKILL process đang giữ port (việc cài cần cờ `--dangerously-force-unsafe-install`).[^hy-memory]
- **ai-memory:** user do proxy xác nhận bỏ qua grant; payload admission webhook không được sanitize; hook spool giữ body *trước khi* strip, nên copy file thô có thể lộ text chưa làm sạch.[^ai-memory]
- **GBrain** tự liệt kê những gì *không* được ràng buộc: ai truy cập trực tiếp được Postgres (container cùng bridge network) là đọc được mọi source; stdio không cần token; token legacy có scope NULL được toàn quyền; private-page có các lối thoát opt-in; RLS không phải ranh giới auth (service role có `BYPASSRLS`).[^gbrain]
- **Headroom:** proxy Rust có mô hình exposure khác proxy Python. Với provider tương thích OpenAI bên thứ ba, nếu không cấu hình upstream thì key có thể bị gửi tới upstream mặc định.[^headroom]

## 4. Egress và telemetry

| Hệ | Gọi mạng mặc định | Egress khi bật thêm |
|---|---|---|
| ai-memory | Chỉ tải model embedding khoảng 87 MB một lần (có pin sha256); **không telemetry** | Embedding/LLM cloud, `capture_assistant` (opt-in hai lần), reranker LLM, admission webhook. Các payload này **không được sanitize**[^ai-memory] |
| GBrain | Keyless thì không cần API model | Embedding, rerank, expansion, `think`/extraction gửi text đi. **Memorable** cần ba công tắc độc lập; có kill switch `GBRAIN_MEMORABLE=0`[^gbrain] |
| Headroom | **Beacon bật mặc định** (gửi tổng hợp cấu trúc và một allowlist config); tắt bằng `HEADROOM_BEACON=off`, `DO_NOT_TRACK=1` hoặc `HEADROOM_OFFLINE=1` | Doc nói beacon không chứa thứ gì suy ra từ body, nhưng code gửi các trường cấu trúc (mâu thuẫn doc/code)[^headroom] |
| MemHub | Script `verify_zero_collection.py` chạy trong CI (Reported); không chụp màn hình, bàn phím hay clipboard | Text gửi tới model bên thứ ba đi qua bước loại credential[^hy-memory] |
| Hy SDK | Gọi LLM/embedding (mặc định là endpoint OpenAI) | Nội dung prompt không được log mặc định[^hy-memory] |
| Hindsight | Gọi LLM khi retain/consolidate (mặc định OpenAI); embedding local | Decision model hosted (Hindsight Inference); webhook[^hindsight] |
| Mem0 | LLM + embedding (mặc định OpenAI); hosted client gọi dịch vụ ngay khi khởi tạo | CLI có thể sao API key vào shell rc hoặc settings của Claude[^mem0] |
| Cognee | Model local tải về lần đầu | Provider LLM khi cognify[^cognee] |
| TencentDB | Không ghi nhận | Telemetry API tuỳ chọn của Panel có trường user key[^tencentdb] |

## 5. Lọc secret và PII

| Hệ | Cơ chế | Giới hạn |
|---|---|---|
| ai-memory | `Sanitizer` và `Sanitized<T>` là ranh giới có kiểu, chạy trước khi ghi FTS và raw segment; redact key, PEM, credential trong URL, chuỗi dạng `*_TOKEN=` | Không áp cho payload egress; spool chứa dữ liệu trước khi lọc[^ai-memory] |
| Hindsight | **Memory defense** (opt-in theo bank): 45 regex (doc) hoặc khoảng 50 detector (code), redact hoặc block, trả 422 | Không áp ngược cho dữ liệu cũ; regex là heuristic[^hindsight] |
| GBrain | Sanitize credential trước khi chunk; exact search che giá trị credential trong index; redact theo pattern khi ingest transcript | Guardrail seam chỉ quan sát và fail-open[^gbrain] |
| MemHub | `sanitize_model_input`; credential lưu trong secure storage của OS | Log ở mức debug ghi đầy đủ prompt; file ZIP "export logs" chứa log thô[^hy-memory] |
| Mem0 | Plugin có redact bằng regex | Không đảm bảo loại hết secret[^mem0] |
| TencentDB | L0 recorder sanitize hội thoại | Chi tiết chưa được inspect[^tencentdb] |
| Cognee, Headroom | Không ghi nhận | Headroom: CCR lưu nội dung gốc của tool[^cognee][^headroom] |

## 6. Mã hoá at-rest và xoá

- **Không mã hoá at-rest theo mặc định:** ai-memory (chỉ dựa vào quyền OS), Headroom (doc xác nhận). Mã hoá file storage của Cognee không bao gồm graph, vector hay relational store.[^ai-memory][^headroom][^cognee]
- **Xoá logical:** purge của ai-memory không phải forensic erasure, dữ liệu còn trong git history và backup. Cognee còn sót fragment LanceDB và không có compaction graph cho người dùng.[^ai-memory][^cognee]
- **Tách expire và purge:** GBrain. `forget` là expire (giữ audit); purge mới xoá text; soft delete giữ 72 giờ; chỉ CLI cục bộ được purge.[^gbrain]
- **MemHub:** gỡ cài đặt vẫn giữ dữ liệu; chỉ `delete-data` (xác nhận hai lần) mới xoá.[^hy-memory]
- **Hindsight:** `restore` xoá schema đích; backup dùng snapshot REPEATABLE READ.[^hindsight]
- **Mem0, TencentDB:** delete qua API; script purge của TencentDB xoá dữ liệu deployment.[^mem0][^tencentdb]

## 7. Độ tin cậy của nội dung memory

Đây là vấn đề *prompt injection qua memory*. Mức xử lý khác nhau nhiều giữa các hệ:
- **GBrain:** 6 trust tier (`user_confirmed` > … > `external_untrusted`). Mặc định chỉ *flag và gắn nhãn* các ghi trông như chỉ thị, không chặn; quarantine/reject là opt-in. Text của bên thứ ba và transcript được trả về dạng trích dẫn qua MCP.[^gbrain]
- **ai-memory:** body message trong inbox được rào là untrusted kèm `security_notice`. Thứ tự ưu tiên là chỉ dẫn hiện tại > file rules của repo > memory > profile, và "memory không bao giờ tự nó cấp quyền làm gì".[^ai-memory]
- **Hy Hermes provider:** escape `<`/`>` và bọc context trong `<memhub_memory_context>`.[^hy-memory]
- **Hindsight:** directive là luật cứng khi reflect; integration `superagent` chống prompt injection và PII.[^hindsight]
- **Mem0, Cognee, TencentDB, Headroom:** wiki không ghi nhận cơ chế riêng.[^mem0][^cognee][^tencentdb][^headroom]

## Checklist audit trước khi triển khai (Synthesis)

1. Bind address mặc định và chế độ không auth. Hindsight `0.0.0.0` với MCP mở; Hy SDK không auth; Docker quick-start của ai-memory không auth; TencentDB key rỗng.
2. Identifier do caller truyền có được gắn với principal không (Mem0, TencentDB)?
3. Có user hoặc đường nào bỏ qua grant không (ai-memory proxy user, GBrain stdio/DB/token legacy)?
4. Có telemetry hay beacon mặc định không (Headroom)?
5. Payload nào rời máy *không qua sanitize* (webhook, embedding, LLM)?
6. Log và diagnostic có chứa prompt không (MemHub debug, TencentDB dump)?
7. Xoá là logical hay vật lý? Git history và backup có còn dữ liệu không?
8. Memory có được đánh dấu là untrusted khi inject vào prompt không?

## Relationships

- Part of: [Agent memory landscape survey](agent-memory-landscape-survey.md).
- Related: [integration and operations comparison](agent-memory-integration-and-operations-comparison.md), [data model and write comparison](agent-memory-data-model-and-write-comparison.md) (ngữ nghĩa xoá).

[^ai-memory]: [auth/security](ai-memory-auth-and-security.md), [capture/hooks](ai-memory-capture-and-hooks.md), [data handling](ai-memory-data-handling-and-lifecycle-ops.md), [handoffs/messaging](ai-memory-handoffs-and-messaging.md), [project identity](ai-memory-project-identity-and-profile.md). Raw: `SECURITY.md` "Threat model", "Network exposure…"; `docs/users.md` "The four resolution rungs"; `crates/ai-memory-store/src/project_authz.rs::authorize_project`; `docs/admission-webhooks.md`; `crates/ai-memory-core/src/sanitize.rs`; `DATA_HANDLING.md`; `docs/lifecycle-ops.md`; `docs/agent-messaging.md`; `docs/usage.md` "Rules, memory and the profile".
[^cognee]: [storage/security](cognee-storage-and-security.md), [retrieval](cognee-retrieval.md), [interfaces](cognee-interfaces-and-deployment.md). Raw: `cognee/modules/users/methods/get_authenticated_user.py::_resolve_auth_posture`; `cognee/infrastructure/files/utils/local_path_safety.py::get_allowed_local_file_roots`; `cognee/infrastructure/files/encryption/config.py::FileEncryptionConfig`; `cognee/modules/data/deletion/prune_system.py::prune_system`; `cognee/api/v1/forget/forget.py::forget`.
[^gbrain]: [authorization/security](gbrain-authorization-and-security.md), [memory trust/egress](gbrain-memory-trust-and-egress.md), [retrieval](gbrain-retrieval-pipeline.md), [sync/ingestion](gbrain-sync-and-ingestion.md). Raw: `SECURITY.md` "Docker network isolation", "Rate limiting", "Remote MCP Security"; `src/core/scope.ts`; `src/core/grants/model.ts`; `src/mcp/dispatch.ts`; `src/core/search/private-visibility.ts`; `docs/guides/rls-and-you.md`; `src/core/trust/tier.ts`; `docs/memorable-agents.md`; `docs/guardrails.md`.
[^headroom]: [privacy/security](headroom-privacy-and-security.md), [interfaces](headroom-interfaces.md), [memory](headroom-memory.md), [cache/CCR](headroom-cache-and-ccr.md). Raw: `headroom/telemetry/beacon.py::beacon_off_reason`, `BEACON_DEFAULT_ON`; `headroom/telemetry/session.py::_payload_v2`; `docs/content/docs/security-model.mdx` §§ Data at rest; `headroom/ccr/mcp_http.py::create_streamable_http_app`; `headroom/memory/storage_router.py::ProjectResolver.resolve`.
[^hindsight]: [storage/config](hindsight-storage-and-configuration.md), [API surface](hindsight-api-surface.md), [extensions/defense/webhooks](hindsight-extensions-defense-webhooks.md), [banks](hindsight-memory-banks.md), [reflect](hindsight-reflect-agent.md), [integrations](hindsight-integrations.md), [decision models](hindsight-decision-models.md). Raw: `hindsight-api-slim/hindsight_api/config.py::HindsightConfig` (host/port); `hindsight-docs/docs/developer/mcp-server.md` (auth); `hindsight_api/extensions/{tenant,memory_defense}.py`; `hindsight-docs/docs/developer/memory-defense/index.md`; `hindsight-docs/docs/developer/api/webhooks.mdx`; `hindsight-docs/docs/developer/admin-cli.md`.
[^hy-memory]: [SDK API/HTTP server](hy-memory-sdk-api-and-config.md), [plugins](hy-memory-plugins-openclaw-hermes.md), [working/coding isolation](hy-memory-working-coding-memory.md), [runtime/observability](hy-memory-runtime-concurrency-and-observability.md), [MemHub architecture](memhub-product-architecture.md), [MemHub privacy](memhub-privacy-and-permissions.md). Raw: `hy_memory/server.py` module docstring; `plugins/openclaw/src/python-env.ts`; `plugins/hermes/hy_memory/provider.py::_load_broker_configuration`; `coding/store.py::_scope_where`; `memhub/apps/core/src/one_memory/auth.py::local_api_guard`; `memhub/docs/ARCHITECTURE.md` "Permission Boundaries"; `memhub/PRIVACY.md`; `memhub/scripts/verify_zero_collection.py`; `input_sanitization.py::sanitize_model_input`.
[^mem0]: [server/security](mem0-server-and-security.md), [clients/integrations](mem0-clients-and-integrations.md), [retrieval](mem0-retrieval.md), [providers](mem0-providers.md). Raw: `server/auth.py::verify_auth`, `require_admin`; `server/main.py::get_memory`, `search_memories`; `server/routers/entities.py::list_entities`; `cli/python/src/mem0_cli/plugin_sync.py::_update_shell_rc`; `mem0/client/main.py::MemoryClient._validate_api_key`.
[^tencentdb]: [security/deployment](tencentdb-security-deployment.md), [retrieval/storage](tencentdb-retrieval-storage.md), [memory pipeline](tencentdb-memory-pipeline.md). Raw: `MemoryKnowledge/src/middleware/auth.ts::createServiceAuthMiddleware`, `::READONLY_POST_PATHS`; `MemoryCore/src/core/store/isolation.ts::assertIsolation`; `MemoryKnowledge/src/source-auth/credential-codec.ts::encodeSecret`; `MemoryKnowledge/src/source-fetcher/git-fetcher.ts::isPrivateAddress`; `MemoryPanel/src/panel/http/routes/knowledge/callback-routes.ts`; `MemoryProxy/src/pipeline/stages/parse-body.ts::dumpInbound`; `MemoryCore/src/core/conversation/l0-recorder.ts::recordConversation`.
