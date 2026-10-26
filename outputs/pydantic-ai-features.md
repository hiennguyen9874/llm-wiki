## Trạng thái wiki

`wiki/` đang **populated** (32 concept, index đầy đủ, log hợp lệ). Câu trả lời dưới đây lấy hoàn toàn từ wiki; **không mở `raw/`** vì không có citation mâu thuẫn cần đối chứng. Mọi claim về API/hành vi đều là evidence class **Reported** (nguồn vendor hoặc bài tour đọc, chưa ai chạy thử trong ingest).

## Bức tranh tổng

Pydantic AI ở trạng thái v2.59.0 (2026-10-20) tổ chức mọi thứ quanh **một primitive duy nhất — capability** — và chia tính năng thành 3 tầng: core `pydantic-ai`, package `pydantic-ai-harness` (0.x), và capability bên thứ ba. Vòng lặp agent (gọi model → chạy tool → nạp kết quả) được coi là đã xong; v2 dồn giá trị vào lớp bao quanh nó ([Pydantic AI v2 release](wiki/pydantic-ai-v2-release.md)).

```python
Agent('anthropic:claude-sonnet-4-6', deps_type=SupportDeps,
      capabilities=[Caching(), hooks, LocalWorkspace('.'), Coder()])
```

### 1. Capability primitive — nền của mọi thứ
Một capability gói **instructions + tools/toolsets + lifecycle hooks + model settings** vào một object gắn qua `capabilities=[...]`, không cần subclass. Hook chạy theo thứ tự cố định ở mỗi stage (`wrap_*` → `before_*` → operation → `after_*` → `wrap_*` exits, `after_*` chạy ngược thứ tự giữa các capability). `defer_loading=True` (bắt buộc có `id`) giữ capability ngoài prompt, chỉ để lại mô tả một dòng trong catalog; `ToolSearch` làm điều tương tự với tool. Pattern lặp lại là "fall up": chạy local trước, dùng native khi provider hỗ trợ ([capability primitive](wiki/pydantic-ai-capability-primitive.md)).

### 2. Bản đồ tính năng theo nhóm

| Nhóm | Tính năng đã biên soạn | Trang |
| --- | --- | --- |
| Điều khiển run | `timeout=` toàn run, `RunContext.deadline`, `request_timeout`, `max_retries`, `UnsupportedSettingWarning`, category lỗi model provider-neutral (`ModelRateLimitError`, `ModelContextWindowExceededError`…), instruction `on_change='append'` (v2.58/2.59) | [run controls](wiki/pydantic-ai-run-controls.md) |
| Trạng thái hội thoại | `Conversation` (v2.55): messages + usage + `conversation_id` + `deferred_tool_requests`, serialize JSON; usage budget tính cho cả thread | [conversation state](wiki/pydantic-ai-conversation-state.md) |
| Phê duyệt của người | `requires_approval=True` → run kết thúc bằng `DeferredToolRequests`, resume bằng `DeferredToolResults`; `HandleDeferredToolCalls`; `ApprovalReviewer` (duyệt hộ) vs `ToolCallJudge` (chặn hộ) | [deferred approvals](wiki/pydantic-ai-deferred-approvals.md) |
| Durable execution | 9 engine (Temporal, DBOS, Prefect, Restate, AWS Lambda, Absurd, pgtask, Kitaru, Airflow) + builder cho backend khác; **một engine mỗi agent** (v2.54 từ chối engine thứ hai); `non_retryable_model_errors` | [durable execution](wiki/pydantic-ai-durable-execution.md) |
| Workspace & sandbox | `ctx.workspace.run(...)` đổi backend không đổi tool code: `LocalWorkspace`, E2B, Sprites, SSH, Bubblewrap, Smol, Daytona, Modal | [workspaces and sandboxes](wiki/pydantic-ai-workspaces-and-sandboxes.md) |
| MCP | `MCP` capability chạy **local mặc định**, `native=True` để provider tự gọi server; `MCPToolset` + Streamable HTTP/SSE; MCP Apps relay sang AG-UI / Vercel AI; agent có thể tự phục vụ như MCP server | [MCP integration](wiki/pydantic-ai-mcp-integration.md) |
| Orchestration | `pydantic-graph` `GraphBuilder`: typed `StepContext`, `edge_from().to(a,b,c)`, `join`, `.map()`; V2 đưa builder API lên top-level; **cố ý không có persistence** | [graph builder](wiki/pydantic-ai-graph-builder.md) |
| Evals | `pydantic-evals`: evaluator deterministic không gọi LLM (`ToolCorrectness`, `TrajectoryMatch`, `ArgumentCorrectness`, `MaxToolCalls`, `MaxModelRequests`) đọc span OTel local; `LLMJudge`/`GEval`; `OnlineEvaluation` chấm nền, phát `gen_ai.evaluation.result` | [Pydantic Evals](wiki/pydantic-evals.md) |
| Observability | OpenTelemetry thuần (backend nào cũng được), instrumentation v5 với `gen_ai.aggregated_usage.*`, cache attributes `pydantic_ai.cache.*` (v2.55), banner nhắc cấu hình backend | [observability](wiki/pydantic-ai-observability.md) |
| Chi phí | `Caching()` / `cache: True` (v2.55) với retention `5m`/`30m`/`1h`, hiệu ứng khác nhau theo provider; cache write đắt hơn input nên mặc định tắt | [prompt caching](wiki/pydantic-ai-prompt-caching.md) |
| Media | `ImageGenerator` gọi trực tiếp + `ImageGeneration` capability (OpenAI GPT Image, Gemini/Vertex, xAI Grok Imagine) → `BinaryImage` (v2.41) | [image generation](wiki/pydantic-ai-image-generation.md) |
| Voice | `agent.realtime()` — speech-to-speech trên OpenAI Realtime, Azure, Gemini Live, xAI Grok Voice (+ElevenLabs ở v2.59); 3 stream audio-in/audio-out/transcript; tool và history dùng lại của agent text | [realtime voice](wiki/pydantic-ai-realtime-voice.md) |
| Harness "batteries" | `Coder`, `Researcher`, `Memory`, `Guardrails`, `Spend Limits`, `Subagents`, `Planning`, `Code Mode` (Monty), `Step Persistence`, `Compaction`, media externalization, approval capabilities | [Harness](wiki/pydantic-ai-harness.md) |
| Đóng gói & hệ sinh thái | Core gầy, provider opt-in (OpenAI/Anthropic/Google mặc định), agent spec file YAML/JSON, capability bên thứ ba (Vstorm ~20 package), agent skills chính thức cho coding agent | [v2 release](wiki/pydantic-ai-v2-release.md), [Vstorm](wiki/vstorm-pydantic-ai-capabilities.md), [coding-agent skills](wiki/pydantic-ai-coding-agent-skills.md) |

### 3. Định vị và điều kiện biên
Mạnh: type safety từ deps → output đã validate, đổi provider bằng một model string, chọn durable engine thay vì bị khoá vào một cái, eval cùng ngôn ngữ với test suite. Yếu/đánh đổi: **chỉ Python**, release rất nhanh (v2.50.0 → v2.59.0 trong chưa đầy một tháng), Harness 0.x có thể breaking ở minor, hệ sinh thái được cho là nhỏ hơn LangChain khoảng 15 lần (con số không nêu phương pháp), Python ≥ 3.11 từ v2.55.0, và chính sách major mới rút còn 3 tháng ([ecosystem positioning](wiki/pydantic-ai-ecosystem-positioning.md)).

## Tổng hợp (Synthesis)

Ba trục phân loại hữu ích khi chọn tính năng: **(a)** cần hỗ trợ sâu của provider hay framework → core; **(b)** chỉ là battery quanh loop → Harness (chấp nhận 0.x); **(c)** do cộng đồng làm → cùng interface. Trục thứ hai là *cái gì sống qua ranh giới process*: `Conversation` sống giữa các run, durable engine sống trong một run, `StepPersistence` lưu checkpoint để resume/fork, và `pydantic-graph` cố ý không lưu gì.

## Giới hạn của câu trả lời này

- Không có gì được cài đặt, chạy, hay kiểm tra source code Pydantic AI trong bất kỳ ingest nào; toàn bộ là **Reported**, trừ vài nhãn UI trong screenshot (**Observed**).
- Danh sách capability core vs Harness là đọc lại từ một bài tour + một bài vendor, **không phải manifest của một version** — hai nguồn lệch nhau (`ContextManagerCapability`/`ConsoleCapability` không xuất hiện ở danh sách sau).
- Trang [image generation](wiki/pydantic-ai-image-generation.md), [realtime voice](wiki/pydantic-ai-realtime-voice.md), [gateway](wiki/pydantic-ai-gateway.md), [coding-agent skills](wiki/pydantic-ai-coding-agent-skills.md) đang `status: draft`; [ecosystem positioning](wiki/pydantic-ai-ecosystem-positioning.md) cũng `draft` vì con số so sánh hệ sinh thái chỉ có một nguồn.
- Không tìm thấy trang nào trong wiki về: retry/fallback model ở mức chi tiết, streaming API, `output_type` union, hay testing utilities — nếu cần, đó là khoảng trống cần nguồn mới, không phải "không tồn tại".

Tôi để kết quả này **transient** (không tạo trang, không ghi log) vì nó chủ yếu là bản đồ hoá các trang đã có, trùng vai với `wiki/index.md`. Nếu bạn muốn, tôi có thể biên soạn nó thành `type: Synthesis` với footnote và locator đầy đủ để tra cứu lại nhanh — hoặc bổ sung trang còn thiếu (streaming/structured output/retry) nếu bạn có nguồn.