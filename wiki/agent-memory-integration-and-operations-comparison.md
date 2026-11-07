---
type: Synthesis
title: Agent memory integration and operations comparison
description: So sánh bề mặt interface (SDK, REST, MCP, CLI, UI), cơ chế tích hợp với agent/harness, tính năng riêng cho coding agent, provider LLM/embedding, triển khai, background job, đổi embedding model và observability của tám hệ agent-memory.
tags: [agent-memory, survey, comparison, integration, mcp, operations, deployment]
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

# Agent memory integration and operations comparison

Trang này thuộc cụm [Agent memory landscape survey](agent-memory-landscape-survey.md). Nó so sánh cách mỗi hệ *đi vào* một agent và *được vận hành*. Trục khác biệt lớn nhất là **ai nắm vòng đời ghi**:
- Agent tự gọi tool hoặc SDK: Mem0, Cognee, Hindsight SDK, Hy SDK.
- Hook của harness ghi âm thầm: ai-memory, Hindsight coding-agents, MemHub, GBrain (khi opt-in).
- Proxy đứng giữa agent và LLM: TencentDB, Headroom.
- Import transcript sau khi sự việc xảy ra: MemHub, GBrain, Hindsight coding-agents.

Evidence class mặc định là **Observed** (static inspection). Số lượng harness và integration là con số dự án tự báo cáo (Reported) trừ khi ghi khác.

## 1. Bề mặt interface

| Hệ | SDK | Server / API | MCP | CLI / UI |
|---|---|---|---|---|
| Mem0 | Python, TypeScript (OSS + hosted client) | Server tự host + dashboard (Compose kèm Postgres/pgvector); hosted API v3 | Không ghi nhận trong wiki | CLI Python và Node[^mem0] |
| Cognee | Python | FastAPI | MCP server riêng; `server.py` định nghĩa handler `remember`, `recall`, `code_search`, `forget`, `improve`, `cognify_status` (tên hàm, kiểm tra trong phiên này) | CLI; Compose có profile UI/MCP[^cognee] |
| Hindsight | Python, TypeScript, Go, Rust (sinh tự động) | FastAPI khoảng 120 route `/v1/default/banks/{bank_id}/…`; worker tách riêng | Theo bank: 27 tool (một bank) / 30 tool (nhiều bank) | CLI Rust, `hindsight-admin`, control plane Next.js, daemon `hindsight-embed`[^hindsight] |
| Hy Memory | `HyMemoryClient` (Python) | HTTP stdlib `127.0.0.1:19527` | Thư mục `mcp/` mới để dành chỗ | —[^hy-memory] |
| MemHub | — (dùng SDK) | Node Runtime + Python Core (FastAPI), API cục bộ v1/v2 | Đúng 3 tool: `MemHub_recall`, `MemHub_write`, `MemHub_diagnostic_trace` | Electron desktop, Web, CLI[^hy-memory] |
| TencentDB | TypeScript (top-level v3), Python (top-level v2, v3 tách riêng) | Các service Core / Knowledge / Panel / Proxy; `/v3/tools/list|call` | Tool qua Knowledge | Web Panel[^tencentdb] |
| ai-memory | — | Một binary Rust; `/mcp`, `/hook`, `/api/v1` (opt-in), `/web` (opt-in) | 27 tool `memory_*` | Khoảng 50 subcommand CLI; web UI tiếng Anh và pt-BR[^ai-memory] |
| GBrain | Library entry `src/core/index.ts` | `serve --http` (OAuth 2.1), `/admin` SPA, `/metrics` | stdio/HTTP; surface `verbs` (7) / `starter` (41) / `full` (171 tool gọi từ xa được, trên 194 op) | 129 lệnh chỉ có ở CLI cộng các op[^gbrain] |
| Headroom | `compress()` (Python); SDK TypeScript qua proxy | Proxy Python, proxy Rust riêng | MCP compress/retrieve/stats; memory MCP search/save | `headroom proxy|wrap|install|deploy|learn`[^headroom] |

## 2. Cơ chế tích hợp với agent

| Cơ chế | Cách hoạt động | Hệ dùng |
|---|---|---|
| **Library / tool adapter** | Bọc memory thành primitive của framework (`@tool`, `FunctionTool`, `BaseMemory`…) | Hindsight (adapter cho openai-agents, langgraph, llamaindex, google-adk, crewai, pydantic-ai…), Mem0 (16 thư mục integration: claude-code, codex, cursor, openclaw, opencode, vercel-ai-sdk, n8n, zapier, strands…), Cognee SDK[^hindsight][^mem0][^cognee] |
| **MCP + instruction rules** | Đăng ký MCP server và thêm luật "luôn recall/retain" vào file hướng dẫn | Hindsight (`init` cho copilot, openhands, zed…), GBrain (khối *brain-first* được chèn vào `CLAUDE.md`/`AGENTS.md`/`SOUL.md`; mã nguồn trích "1/100 → 92/100 tool-use lift", Reported), ai-memory (Agent Skills), MemHub (skill)[^hindsight][^gbrain][^ai-memory][^hy-memory] |
| **Lifecycle hooks** | `SessionStart`/`UserPromptSubmit` để recall, `Stop`/`SessionEnd` để ghi | ai-memory (9 script cho 10 trigger, POST 0.2 giây, spool offline), Hindsight coding-agents (3–4 hook), MemHub (`failOpenHookCommand`), GBrain (read-context hook; capture hook chỉ khi opt-in)[^ai-memory][^hindsight][^hy-memory][^gbrain] |
| **Import / sync transcript** | Đọc lịch sử hội thoại của host theo cursor | MemHub (`SourceAdapter`, 11 host + 4 định dạng export, polling 60 giây kèm watch), Hindsight coding-agents (import hội thoại + git log + survey), GBrain (`transcripts ingest`, connector chatgpt/claude, source github/google/slack/meetings)[^hy-memory][^hindsight][^gbrain] |
| **Proxy** | Đứng giữa agent và LLM: inject context, ghi lại turn | TencentDB MemoryProxy (không cần plugin cho agent), Headroom proxy/`wrap` (nén)[^tencentdb][^headroom] |
| **Native memory provider** | Plugin memory provider của host | Hy: Hermes `HyMemoryProvider`, OpenClaw plugin (5 tool, auto-recall/capture, tự spawn server Python)[^hy-memory] |

**Độ phủ harness (Reported):**
- ai-memory: khoảng 40 hàng trong support matrix, trên 20 harness có cả hooks + MCP.
- Hindsight: 48 gói integration (README nói "60+").
- MemHub: host bridge cho 10 harness.
- TencentDB: thư mục `agents/` có claude-code, codebuddy, codex, dsh, hermes, openclaw, opencode, workbuddy (kiểm tra trong phiên này).
- GBrain: `gbrain setup` xác minh Claude Code và Codex; OpenClaw/Hermes chưa được hỗ trợ trên đường này.

[^ai-memory][^hindsight][^hy-memory][^tencentdb][^gbrain]

## 3. Tính năng riêng cho coding agent

| Hệ | Tính năng |
|---|---|
| ai-memory | **Handoff claim-once** giữa các session/agent; **managed workstream** (`ai-memory run`: lease 90 giây, ledger, bản chiếu lịch sử native riêng tư khi đổi harness); agent messaging inbox; cross-project profile; `.ai-memory.toml` marker; capture allowlist[^ai-memory] |
| Hindsight | `hindsight-coding-agents`: mỗi repo một bank, seed từ git log, survey headless bằng chính host agent, 5 knowledge page (component map, concepts, conventions, decisions, initiatives), ghi lại transcript khi Stop[^hindsight] |
| Hy Memory | Scene `coding`: fact + experience, cô lập theo workspace/branch, **diff chain** lưu mọi revision của code block; được đánh giá bằng CMB[^hy-memory] |
| Cognee | Code graph qua `enola`; lane `CODING_RULES`, `CODE`[^cognee] |
| TencentDB | CodeGraph: index/sync repo, caller/callee, impact[^tencentdb] |
| GBrain | Chunk AST bằng tree-sitter (TS/JS/Python/Ruby/Go); source `github` (issue, PR, review, CI); plugin variant `gbrain-coding` (21 skill)[^gbrain] |
| Headroom | `headroom learn`: phát hiện vòng lặp lỗi và ghi khuyến nghị vào `CLAUDE.local.md`; nén tool output[^headroom] |
| Mem0 | Plugin cho coding agent dùng chung `agent-plugin-core`[^mem0] |

## 4. Provider LLM và embedding

| Hệ | LLM | Embedding | Ghi chú |
|---|---|---|---|
| Mem0 | 18 module | 12 module | Factory riêng cho LLM, embedder, vector, reranker; đặt trong optional dependency group[^mem0] |
| Cognee | Cấu hình qua env | Model local hoặc provider | Không có bảng provider trong wiki[^cognee] |
| Hindsight | Khoảng 30 implementation, gồm cả xác thực qua subscription (claude-code, codex, cursor, github-copilot) | 11+ (local, onnx, tei, openai, gemini, cohere…) | Failover/round-robin nhiều LLM; định tuyến LLM theo bank qua extension[^hindsight] |
| Hy Memory | Endpoint tương thích OpenAI | Endpoint tương thích OpenAI | `embed_override` chỉ cho đổi URL/key/header, không cho đổi model hay số chiều[^hy-memory] |
| ai-memory | 10 lựa chọn (anthropic, openai, codex, copilot, cursor, gemini, openai-compat…) | 6 lựa chọn | Fallback chỉ khi lỗi tạm thời; circuit breaker 30 giây; profile riêng cho từng task[^ai-memory] |
| GBrain | Anthropic, DeepSeek, Groq (chỉ chat) | Voyage, OpenAI, Google, Mistral, Ollama, … | Có cost cap và consent cho backfill[^gbrain] |
| TencentDB, Headroom | Không ghi nhận chi tiết | — | —[^tencentdb][^headroom] |

## 5. Triển khai và vận hành

| Hệ | Hình thái | Background work |
|---|---|---|
| Mem0 | Library; server qua Compose (khi khởi động API **cài lại `mem0ai` không pin version**) | —[^mem0] |
| Cognee | Library; Docker API; Compose | Pipeline indexing/cognify; improve registry[^cognee] |
| Hindsight | Docker, Docker + Postgres ngoài, `pip`, Helm, Python embedded, Cloud; API (8888) và worker (8889) scale độc lập | Queue `async_operations` trên Postgres; webhook có retry 6 lần[^hindsight] |
| Hy Memory | Library trong process hoặc sidecar HTTP | Hai event loop (ghi / tìm), workload semaphore, gom batch embedding[^hy-memory] |
| MemHub | Một Runtime cho mỗi máy (LaunchAgent / systemd user); chưa hỗ trợ Windows; bản preview | Durable write queue, live sync, evolve hằng đêm[^hy-memory] |
| TencentDB | `deploy/global-images/start-all.sh` (Core, Hub, Proxy) | Scheduler L1→L3, ingest wiki[^tencentdb] |
| ai-memory | Một binary chạy như service theo user; install script, brew, AUR, RPM, Scoop, Nix, Docker, app macOS | Sweep/decay, auto-improve, dream; writer actor[^ai-memory] |
| GBrain | Bun; PGLite (cá nhân) hoặc Postgres (chia sẻ); thin client qua `remote_mcp` | **Minions** (queue native trên Postgres: lease, supervisor, lane cho job dài, shell job phải bật 2 cổng), autopilot, dream cycle 31 phase[^gbrain] |
| Headroom | `pip` (`headroom-ai`, có Rust extension); proxy; `deploy` cho cài đặt lâu dài | —[^headroom] |

## 6. Đổi embedding model

| Hệ | Cơ chế |
|---|---|
| GBrain | `gbrain config set embedding_model` **bị từ chối**. Chỉ `gbrain migrate embeddings` được đổi, theo thứ tự `--status` → `--dry-run` → backup → `--max-cost-usd` + `--yes`; resumable[^gbrain] |
| Hindsight | `hindsight-admin reembed` đổi tại chỗ; vector lẫn lộn làm giảm chất lượng recall, có guard 503 cho tới khi `--finish`[^hindsight] |
| Hy Memory | `reembed.py`: plan → reembed → verify; **chỉ hỗ trợ Chroma**; graph được dựng lại thành Kuzu DB mới[^hy-memory] |
| MemHub | Danh tính space = model + số chiều. Space khác trên home không rỗng thì trả `409 embedding_switch_required`; re-embed toàn bộ, commit trong một transaction, rollback được; space cũ giữ 14 ngày[^hy-memory] |
| ai-memory | Mỗi vector mang `(provider, model, dim)`; lệch số chiều thì bị từ chối; đổi sang provider cloud sẽ backfill toàn bộ corpus[^ai-memory] |
| Mem0, Cognee, TencentDB, Headroom | Không ghi nhận trong wiki[^mem0][^cognee][^tencentdb][^headroom] |

## 7. Observability

- **Hindsight:** `/metrics` Prometheus, dashboard Grafana, `/health/live|ready`, audit log, trace request LLM.[^hindsight]
- **Hy Memory:** log JSONL, bảng trace `pipeline_logs`, `MemoryInspector`, `MetricsCollector`. Nội dung prompt không được log mặc định. MemHub thêm `DiagnosticEventV1` đã redact.[^hy-memory]
- **ai-memory:** `explain` có thời gian theo từng stream; `status --json` có số liệu theo workload; `doctor`.[^ai-memory]
- **GBrain:** `--timings` báo chi phí USD theo từng lời gọi; `/metrics`; `doctor`; `autopilot --status` trả exit code cho cron; `friction log`.[^gbrain]
- **Headroom:** MCP stats; beacon thống kê (bật mặc định, xem [security](agent-memory-security-and-privacy-comparison.md)).[^headroom]
- **Mem0, Cognee, TencentDB:** wiki không đi sâu.[^mem0][^cognee][^tencentdb]

## Nhận xét (Synthesis)

1. **MCP là mẫu số chung**, nhưng một mình MCP không đủ. GBrain và Hindsight đều chèn thêm luật vào file instruction, vì agent hiếm khi tự gọi một MCP server mà không ai bảo nó.
2. **Hook capture và import transcript** là hai triết lý đối lập. Hook ghi lại *trong lúc* làm việc (ai-memory, Hindsight). Import đọc lại *sau đó* (MemHub, GBrain transcripts). MemHub hỗ trợ cả hai và chống ghi trùng.
3. **Proxy** (TencentDB, Headroom) không cần sửa agent, đổi lại là phải tin một thành phần trung gian nhìn thấy toàn bộ traffic.
4. **Vận hành:** chỉ GBrain (Minions) và Hindsight (`async_operations`) có job queue bền dựa trên Postgres. ai-memory có cách vận hành đơn giản nhất (một binary). MemHub chọn một Runtime cho mỗi máy.

## Relationships

- Part of: [Agent memory landscape survey](agent-memory-landscape-survey.md).
- Related: [security and privacy comparison](agent-memory-security-and-privacy-comparison.md) (rủi ro của hook, proxy, MCP), [data model and write comparison](agent-memory-data-model-and-write-comparison.md).

[^ai-memory]: [harness integrations/CLI](ai-memory-harness-integrations-and-cli.md), [capture/hooks](ai-memory-capture-and-hooks.md), [handoffs](ai-memory-handoffs-and-messaging.md), [managed workstreams](ai-memory-managed-workstreams.md), [project identity/profile](ai-memory-project-identity-and-profile.md), [MCP/HTTP surfaces](ai-memory-mcp-tools-and-http-surfaces.md), [providers](ai-memory-llm-and-embedding-providers.md), [distribution](ai-memory-distribution-ci-and-companions.md). Raw: `README.md` "Support matrix", "Quick start"; `hooks/_lib.sh::ai_memory_post_hook`; `crates/ai-memory-mcp/src/server.rs::tool_router`; `crates/ai-memory-cli/src/cli.rs::Command`; `crates/ai-memory-llm/src/factory.rs::ProviderChoice, EmbedderChoice`; `docs/managed-workstreams.md`.
[^cognee]: [interfaces/deployment](cognee-interfaces-and-deployment.md), [ingestion/code graphs](cognee-ingestion-and-code-graphs.md), [retrieval](cognee-retrieval.md). Raw: `cognee/api/client.py::app`; `cognee/cli/_cognee.py::main`; `cognee-mcp/src/server.py` (các handler `remember`, `recall`, `code_search`, `forget`, `improve`, `cognify_status`; kiểm tra trong phiên này); `README.md::Deploy Cognee`.
[^gbrain]: [CLI/MCP surface](gbrain-cli-and-mcp-surface.md), [architecture](gbrain-architecture-and-engines.md), [Minions](gbrain-minions-job-queue.md), [dream cycle](gbrain-dream-cycle-and-autopilot.md), [embeddings](gbrain-embeddings-and-providers.md), [sync/ingestion](gbrain-sync-and-ingestion.md), [recipes/plugins](gbrain-recipes-plugins-and-bootstrap.md), [skills](gbrain-skills-and-resolver.md). Raw: `src/mcp/surface.ts::STARTER_OPS`; `src/cli/command-table.ts`; `src/commands/setup.ts`; `src/core/setup/brain-first.ts`; `src/core/minions/queue.ts`; `docs/embedding-migrations.md`; `src/core/import-file.ts`.
[^headroom]: [interfaces](headroom-interfaces.md), [learning](headroom-learning.md), [overview](headroom-overview.md), [privacy](headroom-privacy-and-security.md). Raw: `pyproject.toml` `[project.scripts]`; `headroom/cli/mcp.py`; `headroom/learn/writer.py::ClaudeCodeWriter`; `sdk/typescript/README.md`.
[^hindsight]: [API surface](hindsight-api-surface.md), [clients/CLI/embed](hindsight-clients-cli-embed.md), [integrations](hindsight-integrations.md), [coding agents](hindsight-coding-agents.md), [providers](hindsight-llm-embedding-providers.md), [deployment/CI](hindsight-deployment-and-ci.md), [extensions/webhooks](hindsight-extensions-defense-webhooks.md), [storage/config](hindsight-storage-and-configuration.md). Raw: `hindsight-api-slim/pyproject.toml` `[project.scripts]`; `hindsight-docs/docs/developer/mcp-server.md`; `hindsight-docs/docs/developer/admin-cli.md`; `hindsight-integrations/README.md`; `hindsight-integrations/coding-agents/README.md`; `config.py::PROVIDER_DEFAULT_MODELS`.
[^hy-memory]: [SDK API/config](hy-memory-sdk-api-and-config.md), [plugins](hy-memory-plugins-openclaw-hermes.md), [runtime/observability](hy-memory-runtime-concurrency-and-observability.md), [storage/reembed](hy-memory-storage-and-reembed.md), [working/coding](hy-memory-working-coding-memory.md), [MemHub architecture](memhub-product-architecture.md), [host bridge](memhub-host-bridge-harness-integration.md), [import adapters](memhub-import-adapters-and-live-sync.md), [embedding switch](memhub-embedding-space-switching.md), [modes/queue](memhub-memory-modes-and-write-queue.md). Raw: `hy_memory/server.py`; `plugins/openclaw/openclaw.plugin.json`; `plugins/hermes/hy_memory/provider.py`; `memhub/packages/host-bridge/src/mcp-toolset.ts`; `memhub/apps/core/src/one_memory/imports/sources/registry.py::build_source_catalog`; `hy_memory/reembed.py`; `memhub/docs/contracts/embedding-switch-v1.md`.
[^mem0]: [clients/integrations](mem0-clients-and-integrations.md), [providers](mem0-providers.md), [server/security](mem0-server-and-security.md). Raw: `mem0/client/main.py::MemoryClient`; `cli/cli-spec.json`; `integrations/agent-plugin-core/README.md`; `server/docker-compose.yaml::services`; `mem0/utils/factory.py`; danh sách `integrations/`, `mem0/{llms,embeddings}/` (kiểm tra trong phiên này).
[^tencentdb]: [proxy/integrations](tencentdb-proxy-integrations.md), [knowledge service](tencentdb-knowledge-service.md), [security/deployment](tencentdb-security-deployment.md), [overview](tencentdb-agent-memory-overview.md). Raw: `MemoryProxy/src/pipeline/runners/openai-chat.ts::runOpenaiChatPipeline`; `MemoryKnowledge/src/routes/tools.ts::createToolsRoutes`; `sdk/memory-core/typescript/src/index.ts`; `sdk/memory-core/python/tencentdb_agent_memory/__init__.py`; `deploy/global-images/start-all.sh`; danh sách `agents/` (kiểm tra trong phiên này).
